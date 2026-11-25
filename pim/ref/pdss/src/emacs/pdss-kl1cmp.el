;; Compile KL1 program by sub process for PDSS V2.5  (90.04.04)

;;-----------------------------------------------------------------------------
;; Default options for KL1 compiler.

(defconst pdss-kl1cmp-system-switch 0
  "Switch of system mode.  0->off, 1->on.
If this switch is 1, You can use builtin predicates for system-mode.")

(defconst pdss-kl1cmp-indexing-switch 1
  "Switch of clause indexing mode.  0->off, 1->on.
If this switch is 1, KL1 compiler generate clause indexing code.")

(defconst pdss-kl1cmp-mrbgc-switch 2
  "Switch of MRB-GC mode.  0->off, 1->on (collect), 2->on (collect & reuse).
If this switch is 1 or 2, KL1 compiler generate MRB-GC code.")

;;-----------------------------------------------------------------------------
;; Varables for PDSS KL1 compiler mode.

(defvar pdss-kl1cmp-use-prolog
  "Flag to use KL1/Prolog compiler.")
(setq pdss-kl1cmp-use-prolog (file-exists-p pdss-kl1cmp-compiler))

(defvar pdss-kl1cmp-process nil
  "Process of PDSS KL1 compiler.")
(if pdss-kl1cmp-process
    (progn (delete-process pdss-kl1cmp-process)
	   (setq pdss-kl1cmp-process nil)))

(defvar pdss-kl1cmp-status nil
  "Status of PDSS KL1 compiler.")
(setq pdss-kl1cmp-status nil)

(defvar pdss-kl1cmp-process2 nil
  "One more process of PDSS KL1 compiler.")
(if pdss-kl1cmp-process2
    (progn (delete-process pdss-kl1cmp-process2)
	   (setq pdss-kl1cmp-process2 nil)))

(defvar pdss-kl1cmp-status2 nil
  "Status of PDSS KL1 compiler #2.")
(setq pdss-kl1cmp-status2 nil)

(defvar pdss-kl1cmp-buffer nil
  "Buffer for PDSS KL1 compiler.")
(defvar pdss-kl1cmp-bufstt nil
  "Status of buffer for PDSS KL1 compiler.")
(defvar pdss-kl1cmp-mode nil
  "Compile mode (buffer or region) of PDSS KL1 compiler.")
(defvar pdss-kl1cmp-file nil
  "File Name Compiled by PDSS KL1 compiler.")
(defvar pdss-kl1cmp-buffer-mode-map nil
  "Key map for Buffer of PDSS KL1 compiler.")

;;-----------------------------------------------------------------------------
;; Major mode for the buffer of PDSS KL1 compiler.

(if (null pdss-kl1cmp-buffer-mode-map)
    (let ((map (make-sparse-keymap)))
      (setq pdss-kl1cmp-buffer-mode-map map)
      (define-key map "\C-c\C-k" 'pdss-kl1cmp-clear-buffer)
      (define-key map "\C-c\C-d" 'pdss-kl1cmp-compile-regions)
      (define-key map "\C-c\C-z" 'pdss-kl1cmp-abort-compiler)
      (define-key map "\C-xk"    'pdss-kl1cmp-kill-buffer)))

(defun pdss-kl1cmp-buffer-mode ()
  "Major mode for the buffer of PDSS KL1 compiler.
In this mode, the following commands can be used:
\\{pdss-kl1cmp-buffer-mode-map}"
  (kill-all-local-variables)
  (buffer-flush-undo (current-buffer))
  (setq major-mode 'pdss-kl1cmp-buffer-mode)
  (setq mode-name "PDSS-KL1cmp")
  (use-local-map pdss-kl1cmp-buffer-mode-map))

;;-----------------------------------------------------------------------------
;; Compile region.

(defun pdss-kl1cmp-copy-region-to-buffer ()
  "Copy specified range (mark and point) of text into the KL1cmp buffer."
  (interactive)
  (if (eq pdss-kl1cmp-bufstt 'compile)
      (error "PDSS KL1cmp: Now compiling."))
  (let ((fname  (buffer-file-name))
	(buffer (current-buffer))
	(from   (mark))
	(to     (point))
	s0 s1 s2)
    (if (not (and fname (string-equal (substring fname -4) ".kl1")))
	(error "PDSS KL1cmp: Not KL1 source file."))
    (pdss-kl1cmp-get-buffer-create)
    (setq s0 (pdss-kl1cmp-get-macro-def
	      from to "^[ \t]*:-[ \t]*with_macro[ \n\t]+"))
    (setq s1 (pdss-kl1cmp-get-macro-def
	      from to "^[ \t]*:-[ \t]*implicit[ \n\t]+"))
    (setq s2 (pdss-kl1cmp-get-macro-def
	      from to "^[ \t]*:-[ \t]*local_implicit[ \n\t\\.]+"))
    (switch-to-buffer-other-window pdss-kl1cmp-buffer)
    (if (and pdss-kl1cmp-bufstt
	     (string-equal (substring fname 0 -4) pdss-kl1cmp-fname))
	(if s2 (insert "\n"))
      (erase-buffer)
      (insert ":- module update.\n")	; dummy module name.
      (insert ":- public update/0.\n")	; dummy predicate name.
      (if s0 (insert s0 ".\n"))
      (if s1 (insert s1 ".\n")))
    (if s2 (insert s2 ".\n"))
    (insert "\n")
    (insert-buffer-substring buffer from to)
    (switch-to-buffer-other-window buffer)
    (setq pdss-kl1cmp-fname (substring fname 0 -4))
    (setq pdss-kl1cmp-bufstt 'inserted)))

(defun pdss-kl1cmp-get-macro-def(from to pattern)
  (save-excursion
    (if (> from to)
	(goto-char to)
      (goto-char from))
    (if (re-search-backward pattern 0 t)
	(let ((begin (match-beginning 0)))
	  (goto-char begin)
	  (if (re-search-forward "\\.\\([ \t]*\n\\|[ \t]+[a-z:'%]\\)")
	      (buffer-substring begin (match-beginning 0)))))))

(defun pdss-kl1cmp-clear-buffer ()
  "Clear text in the KL1cmp buffer."
  (interactive)
  (if (eq pdss-kl1cmp-bufstt 'compile)
      (error "PDSS KL1cmp: Now compiling."))
  (let ((buffer (current-buffer)))
    (pdss-kl1cmp-get-buffer-create)
    (if (not (eq buffer pdss-kl1cmp-buffer))
	(switch-to-buffer-other-window pdss-kl1cmp-buffer))
    (erase-buffer)
    (if (not (eq buffer pdss-kl1cmp-buffer))
	(switch-to-buffer-other-window buffer))
    (setq pdss-kl1cmp-bufstt nil)))

(defun pdss-kl1cmp-compile-regions ()
  "Compile regions (text in the KL1cmp buffer), and merge it's object into
current object (.asm) file. This command is used with C-C C-R command."
  (interactive)
  (if (eq pdss-kl1cmp-bufstt 'compile)
      (error "PDSS KL1cmp: Now compiling."))
  (let ((buffer (current-buffer))
	(fname  (buffer-file-name)))
    (if (and (not (eq buffer pdss-kl1cmp-buffer))
	     (not (and fname (string-equal (substring fname -4) ".kl1"))))
	(error "PDSS KL1cmp: Not KL1 file."))
    (if (not (and pdss-kl1cmp-bufstt
		  (or (eq buffer pdss-kl1cmp-buffer)
		      (string-equal (substring fname 0 -4) pdss-kl1cmp-fname))
		  (eq pdss-kl1cmp-bufstt 'inserted)))
	(error "PDSS KL1cmp: There is no text."))
    (setq pdss-kl1cmp-mode 'region)
    (setq pdss-kl1cmp-bufstt 'compile)
    (pdss-kl1cmp-get-buffer-create)
    (if (not (eq buffer pdss-kl1cmp-buffer))
	(switch-to-buffer-other-window pdss-kl1cmp-buffer))
    (write-region (point-min) (point-max)
		  (concat pdss-kl1cmp-fname ".TMP.kl1"))
    (erase-buffer)
    (message "PDSS KL1cmp: Compile region.")
    (pdss-kl1cmp-message-to-window "PDSS KL1cmp: Compile region.")
    (pdss-kl1cmp-compile)))

;;-----------------------------------------------------------------------------
;; Compile buffer.

(defun pdss-kl1cmp-compile-current-buffer ()
  "Compile all text in the buffer."
  (interactive)
  (if (eq pdss-kl1cmp-bufstt 'compile)
      (error "PDSS KL1cmp: Now compiling."))
  (let ((buffer (current-buffer))
	(fname  (buffer-file-name)))
    (if (not (and fname (string-equal (substring fname -4) ".kl1")))
	(error "PDSS KL1cmp: Not KL1 file."))
    (setq pdss-kl1cmp-fname (substring fname 0 -4))
    (setq pdss-kl1cmp-mode nil)
    (setq pdss-kl1cmp-bufstt 'compile)
    (pdss-kl1cmp-get-buffer-create)
    (save-buffer)
    (switch-to-buffer-other-window pdss-kl1cmp-buffer)
    (erase-buffer)
    (message (concat "PDSS KL1cmp: Compile... " fname))
    (pdss-kl1cmp-message-to-window
        (concat "PDSS KL1cmp: Compile... " fname))
    (pdss-kl1cmp-compile)))

;;-----------------------------------------------------------------------------
;; Control compiler process -- Compile phase.

(defun pdss-kl1cmp-compile ()
  (let (status fname (process-connection-type nil))
    (if pdss-kl1cmp-mode
	(setq fname (concat pdss-kl1cmp-fname ".TMP"))
      (setq fname pdss-kl1cmp-fname))
    (if pdss-kl1cmp-use-prolog
	(progn
	  (if (and (eq pdss-kl1cmp-status2 'wait)
		   pdss-kl1cmp-process2
		   (eq (process-status pdss-kl1cmp-process2) 'run))
	      nil
	    (pdss-kl1cmp-get-buffer-create)
	    (if pdss-kl1cmp-process2
		(delete-process pdss-kl1cmp-process2))
	    (setq pdss-kl1cmp-process2
		  (start-process "pdss-kl1cmp2" pdss-kl1cmp-buffer
				 pdss-kl1cmp-compiler))
	    (process-kill-without-query pdss-kl1cmp-process2)
	    (set-process-sentinel pdss-kl1cmp-process2
				  'pdss-kl1cmp-compile-sentinel-p)
	    (set-process-filter pdss-kl1cmp-process2 'pdss-kl1cmp-filter2))
	  (setq pdss-kl1cmp-status2 'compile)
	  (send-string pdss-kl1cmp-process2	;; Compile mode.
		       (nth pdss-kl1cmp-system-switch '("user.\n" "pdss.\n")))
	  (send-string pdss-kl1cmp-process2	;; Clause indexing.
		       (nth pdss-kl1cmp-indexing-switch '("0.\n" "1.\n")))
	  (send-string pdss-kl1cmp-process2	;; MRB-GC mode.
		       (nth pdss-kl1cmp-mrbgc-switch '("1.\n" "2.\n" "3.\n")))
	  (send-string pdss-kl1cmp-process2 (concat "'" fname ".kl1'.\n"))
	  (send-string pdss-kl1cmp-process2 (concat "'" fname ".klb'.\n"))
	  (process-send-eof pdss-kl1cmp-process2))
      (if (and (eq pdss-kl1cmp-status 'wait)
	       pdss-kl1cmp-process
	       (eq (process-status pdss-kl1cmp-process) 'run))
	  nil
	(pdss-kl1cmp-get-buffer-create)
	(if pdss-kl1cmp-process
	    (delete-process pdss-kl1cmp-process))
	(setq pdss-kl1cmp-process
	      (start-process "pdss-kl1cmp" pdss-kl1cmp-buffer
			     pdss-command-name pdss-kl1cmp-startup-file "+t"))
	(process-kill-without-query pdss-kl1cmp-process)
	(set-process-sentinel pdss-kl1cmp-process
			      'pdss-kl1cmp-compile-sentinel-k)
	(set-process-filter pdss-kl1cmp-process 'pdss-kl1cmp-filter))
      (setq pdss-kl1cmp-status 'compile)
      (send-string pdss-kl1cmp-process "no.\n")	;; Assemble Switch.
      (send-string pdss-kl1cmp-process		;; MRB-GC Option
		   (nth pdss-kl1cmp-mrbgc-switch '("1.\n" "2.\n" "3.\n")))
      (send-string pdss-kl1cmp-process (concat "'" fname ".kl1'.\n"))
      (send-string pdss-kl1cmp-process (concat "'" fname ".asm'.\n"))
      (process-send-eof pdss-kl1cmp-process))))

(defun pdss-kl1cmp-compile-sentinel-p (proc reason)
  (let ((process-connection-type nil))
    (set-process-sentinel pdss-kl1cmp-process2 nil)
    (setq reason (substring reason 0 (- (length reason) 1)))
    (if (and (string-equal reason "finished")
	     (pdss-kl1cmp-check-error-message-p))
	(progn
	  (delete-process pdss-kl1cmp-process2)
	  (setq pdss-kl1cmp-process2 nil)
;;	  (setq pdss-kl1cmp-process2
;;		(start-process "pdss-kl1cmp2" pdss-kl1cmp-buffer
;;			       pdss-kl1cmp-compiler))
;;	  (process-kill-without-query pdss-kl1cmp-process2)
;;	  (set-process-sentinel pdss-kl1cmp-process2
;;				'pdss-kl1cmp-compile-sentinel-p)
;;	  (set-process-filter pdss-kl1cmp-process2 'pdss-kl1cmp-filter2)
;;	  (setq pdss-kl1cmp-status2 'wait)
	  (setq pdss-kl1cmp-status2 nil)
	  (setq pdss-kl1cmp-bufstt nil)
	  (pdss-kl1cmp-translate))
      (delete-process pdss-kl1cmp-process2)
      (setq pdss-kl1cmp-process2 nil)
      (setq pdss-kl1cmp-status2 nil)
      (setq pdss-kl1cmp-bufstt nil)
      (beep)
      (message "PDSS KL1cmp: %s." reason))))

(defun pdss-kl1cmp-compile-sentinel-k (proc reason)
  (set-process-sentinel pdss-kl1cmp-process nil)
  (setq reason (substring reason 0 (- (length reason) 1)))
  (if (and (string-equal reason "finished")
	   (pdss-kl1cmp-check-error-message-k))
      (if pdss-kl1cmp-mode
	  (pdss-kl1cmp-merge)
	(pdss-kl1cmp-assemble))
    (delete-process pdss-kl1cmp-process)
    (setq pdss-kl1cmp-process nil)
    (setq pdss-kl1cmp-status nil)
    (setq pdss-kl1cmp-bufstt nil)
    (beep)
    (message "PDSS KL1cmp: %s." reason)))

;;-----------------------------------------------------------------------------
;; Control compiler process -- Translate phase.

(defun pdss-kl1cmp-translate ()
  (pdss-kl1cmp-message-to-window "PDSS KL1cmp: Translate.")
  (let (status fname (process-connection-type nil))
    (if pdss-kl1cmp-mode
	(setq fname (concat pdss-kl1cmp-fname ".TMP"))
      (setq fname pdss-kl1cmp-fname))
    (if (and (eq pdss-kl1cmp-status 'wait)
	     pdss-kl1cmp-process
	     (eq (process-status pdss-kl1cmp-process) 'run))
	nil
      (pdss-kl1cmp-get-buffer-create)
      (if pdss-kl1cmp-process
	  (delete-process pdss-kl1cmp-process))
      (setq pdss-kl1cmp-process
	    (start-process "pdss-kl1cmp" pdss-kl1cmp-buffer
			   pdss-kl1cmp-translator))
      (process-kill-without-query pdss-kl1cmp-process)
      (set-process-sentinel pdss-kl1cmp-process
			    'pdss-kl1cmp-translate-sentinel)
      (set-process-filter pdss-kl1cmp-process 'pdss-kl1cmp-filter))
    (setq pdss-kl1cmp-status 'translate)
    (send-string pdss-kl1cmp-process	;; MRB-GC mode.
      (nth pdss-kl1cmp-mrbgc-switch '("0.\n" "1.\n" "1.\n")))
    (send-string pdss-kl1cmp-process (concat "'" fname ".klb'.\n"))
    (send-string pdss-kl1cmp-process (concat "'" fname ".asm'.\n"))
    (process-send-eof pdss-kl1cmp-process)))


(defun pdss-kl1cmp-translate-sentinel (proc reason)
  (set-process-sentinel pdss-kl1cmp-process nil)
  (setq reason (substring reason 0 (- (length reason) 1)))
  (if (and (string-equal reason "finished")
	   (pdss-kl1cmp-check-error-message-t))
      (pdss-kl1cmp-removeklb)
    (delete-process pdss-kl1cmp-process)
    (setq pdss-kl1cmp-process nil)
    (setq pdss-kl1cmp-status nil)
    (setq pdss-kl1cmp-bufstt nil)
    (beep)
    (message "PDSS KL1cmp: %s." reason)))

;;-----------------------------------------------------------------------------
;; Control compiler process -- Remove *.klb file.

(defun pdss-kl1cmp-removeklb ()
  (pdss-kl1cmp-message-to-window "PDSS KL1cmp: Remove .klb file.")
  (let (status fname (process-connection-type nil))
    (if pdss-kl1cmp-mode
	(setq fname (concat pdss-kl1cmp-fname ".TMP"))
      (setq fname pdss-kl1cmp-fname))
    (pdss-kl1cmp-get-buffer-create)
    (if pdss-kl1cmp-process
	(delete-process pdss-kl1cmp-process))
    (setq pdss-kl1cmp-process
	  (start-process "pdss-kl1cmp" pdss-kl1cmp-buffer
			 "rm" "-f" (concat fname ".klb")))
    (process-kill-without-query pdss-kl1cmp-process)
    (set-process-sentinel pdss-kl1cmp-process
			  'pdss-kl1cmp-removeklb-sentinel)
    (set-process-filter pdss-kl1cmp-process 'pdss-kl1cmp-filter)
    (setq pdss-kl1cmp-status 'removeklb)))

(defun pdss-kl1cmp-removeklb-sentinel (proc reason)
  (set-process-sentinel pdss-kl1cmp-process nil)
  (setq reason (substring reason 0 (- (length reason) 1)))
  (if (string-equal reason "finished")
      (if pdss-kl1cmp-mode
	  (pdss-kl1cmp-merge)
	(pdss-kl1cmp-assemble))
    (delete-process pdss-kl1cmp-process)
    (setq pdss-kl1cmp-process nil)
    (setq pdss-kl1cmp-status nil)
    (setq pdss-kl1cmp-bufstt nil)
    (beep)
    (message "PDSS KL1cmp: %s." reason)))

;;-----------------------------------------------------------------------------
;; Control compiler process -- Merge phase.

(defun pdss-kl1cmp-merge ()
  (pdss-kl1cmp-message-to-window "PDSS KL1cmp: Merge.")
  (let (status fname (process-connection-type nil))
    (setq fname pdss-kl1cmp-fname)
    (pdss-kl1cmp-get-buffer-create)
    (if pdss-kl1cmp-process
	(delete-process pdss-kl1cmp-process))
    (setq pdss-kl1cmp-process
	  (start-process "pdss-kl1cmp" pdss-kl1cmp-buffer
			 pdss-kl1cmp-code-merger
			 (concat fname ".asm") (concat fname ".TMP.asm")))
    (process-kill-without-query pdss-kl1cmp-process)
    (set-process-sentinel pdss-kl1cmp-process
			  'pdss-kl1cmp-merge-sentinel)
    (set-process-filter pdss-kl1cmp-process 'pdss-kl1cmp-filter)
    (setq pdss-kl1cmp-status 'merge)))

(defun pdss-kl1cmp-merge-sentinel (proc reason)
  (set-process-sentinel pdss-kl1cmp-process nil)
  (setq reason (substring reason 0 (- (length reason) 1)))
  (if (string-equal reason "finished")
      (pdss-kl1cmp-removetmp)
    (delete-process pdss-kl1cmp-process)
    (setq pdss-kl1cmp-process nil)
    (setq pdss-kl1cmp-status nil)
    (setq pdss-kl1cmp-bufstt nil)
    (beep)
    (message "PDSS KL1cmp: %s." reason)))

;;-----------------------------------------------------------------------------
;; Control compiler process -- Remove *.TMP.{kl1,asm} file.

(defun pdss-kl1cmp-removetmp ()
  (pdss-kl1cmp-message-to-window "PDSS KL1cmp: Remove temporary file.")
  (let (status fname (process-connection-type nil))
    (setq fname (concat pdss-kl1cmp-fname ".TMP"))
    (pdss-kl1cmp-get-buffer-create)
    (if pdss-kl1cmp-process
	(delete-process pdss-kl1cmp-process))
    (setq pdss-kl1cmp-process
	  (start-process "pdss-kl1cmp" pdss-kl1cmp-buffer
			"rm" "-f" (concat fname ".kl1") (concat fname ".asm")))
    (process-kill-without-query pdss-kl1cmp-process)
    (set-process-sentinel pdss-kl1cmp-process
			  'pdss-kl1cmp-removetmp-sentinel)
    (set-process-filter pdss-kl1cmp-process 'pdss-kl1cmp-filter)
    (setq pdss-kl1cmp-status 'removetmp)))

(defun pdss-kl1cmp-removetmp-sentinel (proc reason)
  (set-process-sentinel pdss-kl1cmp-process nil)
  (setq reason (substring reason 0 (- (length reason) 1)))
  (if (string-equal reason "finished")
      (pdss-kl1cmp-assemble)
    (delete-process pdss-kl1cmp-process)
    (setq pdss-kl1cmp-process nil)
    (setq pdss-kl1cmp-status nil)
    (setq pdss-kl1cmp-bufstt nil)
    (beep)
    (message "PDSS KL1cmp: %s." reason)))

;;-----------------------------------------------------------------------------
;; Control compiler process -- Assembler phase.

(defun pdss-kl1cmp-assemble ()
  (pdss-kl1cmp-message-to-window "PDSS KL1cmp: Assemble.")
  (let (status fname (process-connection-type nil))
    (setq fname pdss-kl1cmp-fname)
    (pdss-kl1cmp-get-buffer-create)
    (if pdss-kl1cmp-process
	(delete-process pdss-kl1cmp-process))
    (setq pdss-kl1cmp-process
	  (start-process "pdss-kl1cmp" pdss-kl1cmp-buffer
			 pdss-kl1cmp-assembler fname))
    (process-kill-without-query pdss-kl1cmp-process)
    (set-process-sentinel pdss-kl1cmp-process
			  'pdss-kl1cmp-assemble-sentinel)
    (set-process-filter pdss-kl1cmp-process 'pdss-kl1cmp-filter)
    (setq pdss-kl1cmp-status 'assemble)))

(defun pdss-kl1cmp-assemble-sentinel (proc reason)
  (let ((process-connection-type nil))
    (set-process-sentinel pdss-kl1cmp-process nil)
    (setq reason (substring reason 0 (- (length reason) 1)))
    (if (and (string-equal reason "finished")
	     (pdss-kl1cmp-check-error-message-a))
	(progn
	  (message "PDSS KL1cmp: Success.")
	  (pdss-kl1cmp-message-to-window "PDSS KL1cmp: Success.")
	  (delete-process pdss-kl1cmp-process)
	  (if pdss-kl1cmp-use-prolog
	      (progn
		(setq pdss-kl1cmp-process nil))
;;		(setq pdss-kl1cmp-process
;;		      (start-process "pdss-kl1cmp" pdss-kl1cmp-buffer
;;				     pdss-kl1cmp-translator))
;;		(process-kill-without-query pdss-kl1cmp-process)
;;		(set-process-sentinel pdss-kl1cmp-process
;;				      'pdss-kl1cmp-translate-sentinel))
	    (setq pdss-kl1cmp-process nil))
;;	    (setq pdss-kl1cmp-process
;;		  (start-process "pdss-kl1cmp" pdss-kl1cmp-buffer
;;			      pdss-command-name pdss-kl1cmp-startup-file "+t"))
;;	    (process-kill-without-query pdss-kl1cmp-process)
;;	    (set-process-sentinel pdss-kl1cmp-process
;;				  'pdss-kl1cmp-compile-sentinel-k))
;;	  (set-process-filter pdss-kl1cmp-process 'pdss-kl1cmp-filter)
;;	  (setq pdss-kl1cmp-status 'wait)
	  (setq pdss-kl1cmp-status nil)
	  (setq pdss-kl1cmp-bufstt nil))
      (delete-process pdss-kl1cmp-process)
      (setq pdss-kl1cmp-process nil)
      (setq pdss-kl1cmp-status nil)
      (setq pdss-kl1cmp-bufstt nil)
      (beep)
      (message "PDSS KL1cmp: %s." reason))))

;;-----------------------------------------------------------------------------
;; Abort Compiler from Keyboard

(defun pdss-kl1cmp-abort-compiler ()
  (interactive)
  (if (and (or (not pdss-kl1cmp-process2) (eq pdss-kl1cmp-status2 'wait))
	   (or (not pdss-kl1cmp-process) (eq pdss-kl1cmp-status 'wait)))
      (error "PDSS KL1cmp: Not running."))
  (message "PDSS KL1cmp: Aborted.")
  (pdss-kl1cmp-message-to-window "PDSS KL1cmp: Aborted.")
  (let ((process-connection-type nil))
    (if (and pdss-kl1cmp-process (not (eq pdss-kl1cmp-status 'wait)))
	(progn
	  (delete-process pdss-kl1cmp-process)
	  (if pdss-kl1cmp-use-prolog
	      (progn
		(setq pdss-kl1cmp-process nil))
;;		(setq pdss-kl1cmp-process
;;		      (start-process "pdss-kl1cmp" pdss-kl1cmp-buffer
;;				     pdss-kl1cmp-translator))
;;		(process-kill-without-query pdss-kl1cmp-process)
;;		(set-process-sentinel pdss-kl1cmp-process
;;				      'pdss-kl1cmp-translate-sentinel))
	    (setq pdss-kl1cmp-process nil))
;;	    (setq pdss-kl1cmp-process
;;		  (start-process "pdss-kl1cmp" pdss-kl1cmp-buffer
;;			      pdss-command-name pdss-kl1cmp-startup-file "+t"))
;;	    (process-kill-without-query pdss-kl1cmp-process)
;;	    (set-process-sentinel pdss-kl1cmp-process
;;				  'pdss-kl1cmp-compile-sentinel-k))
;;	  (set-process-filter pdss-kl1cmp-process 'pdss-kl1cmp-filter)
;;	  (setq pdss-kl1cmp-status 'wait)))
	  (setq pdss-kl1cmp-status nil)))
    (if (and pdss-kl1cmp-process2 (not (eq pdss-kl1cmp-status2 'wait)))
	(progn
	  (delete-process pdss-kl1cmp-process2)
	  (if pdss-kl1cmp-use-prolog
	      (progn
		(setq pdss-kl1cmp-process2 nil)
;;		(setq pdss-kl1cmp-process2
;;		      (start-process "pdss-kl1cmp2" pdss-kl1cmp-buffer
;;				     pdss-kl1cmp-compiler))
;;		(process-kill-without-query pdss-kl1cmp-process2)
;;		(set-process-sentinel pdss-kl1cmp-process2
;;				      'pdss-kl1cmp-compile-sentinel-p)
;;		(set-process-filter pdss-kl1cmp-process2 'pdss-kl1cmp-filter2)
;;		(setq pdss-kl1cmp-status2 'wait))
		(setq pdss-kl1cmp-status2 nil))
	    (setq pdss-kl1cmp-status2 nil))))
    (setq pdss-kl1cmp-bufstt nil)))

;;-----------------------------------------------------------------------------
;; Display to buffer

(defun pdss-kl1cmp-filter (proc string)
  (if (and pdss-kl1cmp-process (not (eq pdss-kl1cmp-status 'wait)))
      (save-excursion
	(let ((cb (current-buffer)))
	  (set-buffer (get-buffer-create "PDSS=COMPILER"))
	  (goto-char (point-max))
	  (insert string)
	  (set-buffer cb)))))

(defun pdss-kl1cmp-filter2 (proc string)
  (if (and pdss-kl1cmp-process2 (not (eq pdss-kl1cmp-status2 'wait)))
      (save-excursion
	(let ((cb (current-buffer)))
	  (set-buffer (get-buffer-create "PDSS=COMPILER"))
	  (goto-char (point-max))
	  (insert string)
	  (set-buffer cb)))))

(defun pdss-kl1cmp-message-to-window (string)
  (save-excursion
    (let ((cb (current-buffer)))
      (set-buffer (get-buffer-create "PDSS=COMPILER"))
      (goto-char (point-max))
      (if (> (current-column) 0) (insert ?\n))
      (insert string)
      (insert ?\n)
      (set-buffer cb))))

(defun pdss-kl1cmp-check-error-message-p ()
  (save-excursion
    (let ((cb (current-buffer))
	  (flag))
      (set-buffer (get-buffer-create "PDSS=COMPILER"))
      (goto-char (point-min))
      (setq case-fold-search nil)
      (setq flag (re-search-forward
"\\*\\*\\*\\*\\|%%%% ERROR\\|%%% ERROR !!\\|%%% Error\\|^\\*\\* \\|\\{ERROR:"
		  nil t))
      (set-buffer cb)
      (not flag))))

(defun pdss-kl1cmp-check-error-message-k ()
  (save-excursion
    (let ((cb (current-buffer))
	  (flag))
      (set-buffer (get-buffer-create "PDSS=COMPILER"))
      (goto-char (point-min))
      (setq case-fold-search nil)
      (setq flag (re-search-forward
     "Error:\\|\\*\\* Syntax Error \\*\\*\\|\\*\\* Ambiguous Expression \\*\\*"
		  nil t))
      (set-buffer cb)
      (not flag))))

(defun pdss-kl1cmp-check-error-message-t ()
  (save-excursion
    (let ((cb (current-buffer))
	  (flag))
      (set-buffer (get-buffer-create "PDSS=COMPILER"))
      (goto-char (point-min))
      (setq case-fold-search nil)
      (setq flag (re-search-forward
	"^ \\*\\* Syntax Error\\|\\*error\\.\\.\\.\\.\\|^\\*\\* \\|\\{ERROR:"
		  nil t))
      (set-buffer cb)
      (not flag))))

(defun pdss-kl1cmp-check-error-message-a ()
  (save-excursion
    (let ((cb (current-buffer))
	  (flag))
      (set-buffer (get-buffer-create "PDSS=COMPILER"))
      (goto-char (point-min))
      (setq case-fold-search nil)
      (setq flag (re-search-forward
		  ">>> Assembler:\\|^Error open\\|^Can not"
		  nil t))
      (set-buffer cb)
      (not flag))))

;;-----------------------------------------------------------------------------
;; Kill compiler buffer.

(defun pdss-kl1cmp-kill-buffer ()
  (interactive)
  (if (yes-or-no-p "Really want to kill this buffer? ")
      (progn
	(if pdss-kl1cmp-process (delete-process pdss-kl1cmp-process))
	(if pdss-kl1cmp-process2 (delete-process pdss-kl1cmp-process2))
	(setq pdss-kl1cmp-process nil)
	(setq pdss-kl1cmp-process2 nil)
	(setq pdss-kl1cmp-status  nil)
	(setq pdss-kl1cmp-status2  nil)
	(setq pdss-kl1cmp-buffer   nil)
	(setq pdss-kl1cmp-bufstt   nil)
	(setq pdss-kl1cmp-mode     nil)
	(setq pdss-kl1cmp-file     nil)
	(kill-buffer (current-buffer)))))

(defun pdss-kl1cmp-get-buffer-create ()
  (if (get-buffer "PDSS=COMPILER")
      (setq pdss-kl1cmp-buffer (get-buffer "PDSS=COMPILER"))
    (setq pdss-kl1cmp-buffer (get-buffer-create "PDSS=COMPILER"))
    (save-excursion
      (let ((cb (current-buffer)))
	(set-buffer pdss-kl1cmp-buffer)
	(pdss-kl1cmp-buffer-mode)
	(set-buffer cb)))))

;;-----------------------------------------------------------------------------
;; Switch compile mode.

(defun pdss-kl1cmp-switch-system-mode (x)
  "Switch compile mode (user or system)."
  (interactive "P")
  (if x (if (and (<= 0 x) (<= x 1)) (setq pdss-kl1cmp-system-switch x))
    (cond
     ((= pdss-kl1cmp-system-switch 0) (setq pdss-kl1cmp-system-switch 1))
     ((= pdss-kl1cmp-system-switch 1) (setq pdss-kl1cmp-system-switch 0))))
  (cond
   ((= pdss-kl1cmp-system-switch 0)
    (message "PDSS KL1cmp: system mode off."))
   ((= pdss-kl1cmp-system-switch 1)
    (message "PDSS KL1cmp: system mode on."))))

(defun pdss-kl1cmp-switch-indexing-mode (x)
  "Switch clause indexing mode."
  (interactive "P")
  (if x (if (and (<= 0 x) (<= x 1)) (setq pdss-kl1cmp-indexing-switch x))
    (cond
     ((= pdss-kl1cmp-indexing-switch 0) (setq pdss-kl1cmp-indexing-switch 1))
     ((= pdss-kl1cmp-indexing-switch 1) (setq pdss-kl1cmp-indexing-switch 0))))
  (cond
   ((= pdss-kl1cmp-indexing-switch 0)
    (message "PDSS KL1cmp: indexing off."))
   ((= pdss-kl1cmp-indexing-switch 1)
    (message "PDSS KL1cmp: indexing on."))))

(defun pdss-kl1cmp-switch-mrbgc-mode (x)
  "Switch MRB-GC mode."
  (interactive "P")
  (if x (if (and (<= 0 x) (<= x 2)) (setq pdss-kl1cmp-mrbgc-switch x))
    (cond
     ((= pdss-kl1cmp-mrbgc-switch 0) (setq pdss-kl1cmp-mrbgc-switch 1))
     ((= pdss-kl1cmp-mrbgc-switch 1) (setq pdss-kl1cmp-mrbgc-switch 2))
     ((= pdss-kl1cmp-mrbgc-switch 2) (setq pdss-kl1cmp-mrbgc-switch 0))))
  (cond
   ((= pdss-kl1cmp-mrbgc-switch 0)
    (message "PDSS KL1cmp: MRB-GC off."))
   ((= pdss-kl1cmp-mrbgc-switch 1)
    (message "PDSS KL1cmp: MRB-GC on (collect)."))
   ((= pdss-kl1cmp-mrbgc-switch 2)
    (message "PDSS KL1cmp: MRB-GC on (collect & reuse)."))))
