;;
;; Emacs macros for formatting, etc. the SQL files.
;;

(fset 'psql-fk-update
      [?\C-s ?a ?l ?t ?e ?r ?  ?t ?a ?b ?l ?e ?\C-m right ?\C-  ?\C-e left escape ?w ?\C-s ?a ?d ?d ?  ?c ?o ?n ?s ?t ?r ?a ?i ?n ?t ?\C-m right right right ?\C-y ?\C-k ?\C-s ?f ?o ?r ?e ?i ?g ?n ?  ?k ?e ?y ?\C-m right right ?\C-  ?\C-s ?) left escape ?w up end ?_ ?\C-y ?\C-s ?r ?e ?f ?e ?r ?e ?n ?\C-m right right right right ?\C-  ?\C-e ?\; backspace left escape ?w up up end ?_ ?\C-y])

