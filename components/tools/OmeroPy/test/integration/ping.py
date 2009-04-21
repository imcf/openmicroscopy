#!/usr/bin/env python

"""
   Integration test testing distributed processing via
   ServiceFactoryI.acquireProcessor().

   Copyright 2008 Glencoe Software, Inc. All rights reserved.
   Use is subject to license terms supplied in LICENSE.txt

"""

import test.integration.library as lib
import omero, tempfile, unittest, os, sys
import omero_api_IScript_ice
from omero.rtypes import *

PINGFILE = """
#!/usr/bin/env python

import sys
from pprint import pprint
pprint(sys.path)

import os, uuid
from omero_ext import pysys
import omero, omero.scripts as s
from omero.rtypes import *

#
# Unique name so that IScript does not reject us
# based on duplicate file names.
#
uuid = str(uuid.uuid4())
print "I am the script named %s" % uuid

#
# Creation
#
client = s.client(uuid, "simple ping script", s.Long("a").inout(), s.String("b").inout())
client.createSession()
print "Session", client.getSession()

#
# Echo'ing input to output
#
keys = client.getInputKeys()
print "Keys found:"
print keys
for key in keys:
    client.setOutput(key, client.getInput(key))

#
# Env
#
print "This was my environment:"
for k,v in os.environ.items():
    print "%s => %s" %(k,v)

#
# Must use pysys because of a naming clash with
# with the omero.sys package.
#
pysys.stderr.write("Oh, and this is stderr.");

"""

PUBLIC = omero.model.PermissionsI()
PUBLIC.setGroupRead(True)
PUBLIC.setWorldRead(True)

class TestPing(lib.ITest):

    def testUploadAndPing(self):
        pingfile = tempfile.NamedTemporaryFile(mode='w+t')
        try:
            pingfile.write(PINGFILE)
            pingfile.flush()
            file = self.root.upload(pingfile.name, type="text/x-python", permissions = PUBLIC)
            j = omero.model.ScriptJobI()
            j.linkOriginalFile(file)

            p = self.client.sf.acquireProcessor(j, 100)
            jp = p.params()
            self.assert_(jp, "Non-zero params")

            input = rmap({})
            input.val["a"] = rint(1)
            input.val["b"] = rstring("c")
            process = p.execute(input)
            rc = process.wait()
            if rc:
                self.assert_(rc == 0, "Non-zero return code")
            output = p.getResults(process)
            self.assert_( 1 == output.val["a"].val )
        finally:
            pingfile.close()

    def _getProcessor(self):
        scripts = self.root.getSession().getScriptService()
        id = scripts.uploadScript(PINGFILE)
        j = omero.model.ScriptJobI()
        j.linkOriginalFile(omero.model.OriginalFileI(rlong(id),False))
        p = self.client.sf.acquireProcessor(j, 100)
        return p

    def testPingViaISCript(self):
        p = self._getProcessor()
        input = rmap({})
        input.val["a"] = rint(2)
        input.val["b"] = rstring("d")
        process = p.execute(input)
        process.wait()
        output = p.getResults(process)
        self.assert_( 2 == output.val["a"].val )

    def testPingParametersViaISCript(self):
        p = self._getProcessor()
        params = p.params()
        self.assert_( params )
        self.assert_( params.inputs["a"] )
        self.assert_( params.inputs["b"] )
        self.assert_( params.outputs["a"] )
        self.assert_( params.outputs["b"] )

    def _checkstd(self, output, which):
        rfile = output.val[which]
        ofile = rfile.val
        self.assert_( ofile )

        tmpfile = tempfile.NamedTemporaryFile(mode='w+t')
        try:
            self.client.download(ofile, tmpfile.name)
            self.assert_( os.path.getsize(tmpfile.name) )
        finally:
            tmpfile.close()

    def testPingStdout(self):
        p = self._getProcessor()
        params = p.params()
        self.assert_( params.stdoutFormat )

        process = p.execute(rmap({}))
        process.wait()
        output = p.getResults(process)

        self._checkstd(output, "stdout")
        self._checkstd(output, "stderr")        

if __name__ == '__main__':
    unittest.main()
