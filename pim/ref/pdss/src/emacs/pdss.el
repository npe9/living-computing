;; Run PDSS V2.5 - Multi Window Version  (90.04.25)
;; for Nemacs version 2.1 & 3.0.
;; Setting fileio-code & process-code to use EUC code.

;;-----------------------------------------------------------------------------
;; Variables for PDSS.

(defvar pdss-process nil
  "a PDSS process.")

(defvar pdss-dispatch-table 
  (vector 'pdss-read-tag
	  'pdss-insert-to-current-buffer
	  'pdss-read-buffer-name)
  "a dispatch table for filter function.")

(defvar pdss-output-switch 0
  "switch for pdss-dispatch-table:
      0 : next character is TAG.
      1 : output to buffer.
      2 : read buffer name.")

(defvar pdss-current-output-buffer nil
  "current output buffer.")
(defvar pdss-console-buffer nil
  "PDSS console buffer.")
;; for debugging.
;; (defvar pdss-logging-buffer nil
;;   "PDSS logging buffer for debugging.")

(defvar pdss-new-buffer-id nil 
  "new buffer id was saved in this variable.")
(defvar pdss-new-buffer-name ""
  "new buffer name was saved in this variable.")

(defvar pdss-buffer-list nil
  "association list for pdss buffer.")
(defvar pdss-buffer-tail nil
  "tail of association list for pdss buffer.")
(defvar pdss-buffer-count 0
  "number of buffers in pdss-buffer-list.")

;;-----------------------------------------------------------------------------
;; Run PDSS.

(defun pdss (&optional option-sw)
  "Run PDSS, with I/O through multiple buffers."
  (interactive "P")
;; for debugging.
;; (setq pdss-logging-buffer (get-buffer-create "PDSS-LOGGING"))
  (let (status (process-connection-type nil))
    (if pdss-process
	(setq status (process-status pdss-process)))
    (if (memq status '(run stop))
	nil
      (setq pdss-console-buffer (generate-new-buffer "PDSS-CONSOLE"))
      (setq pdss-buffer-list (list (cons 0 pdss-console-buffer)))
      (setq pdss-buffer-tail pdss-buffer-list)
      (setq pdss-buffer-count 1)
      (set-buffer pdss-console-buffer)
      (pdss-mode 0)
      (if (not (fboundp 'change-process-code))	; Use EUC code for kanji.
	  (setq kanji-fileio-code 0)		; for NEmacs 2.1
	(make-local-variable 'default-kanji-process-code)
	(setq default-kanji-process-code 3))	; for NEmacs 3.0
      (setq case-fold-search nil)
      (setq case-replace nil)
      (if pdss-process (delete-process pdss-process))
      (if option-sw
	  (let (option)
	    (setq option (read-string "PDSS Option ?: " ""))
	    (setq pdss-process
		  (start-process "pdss" nil ; pdss-console-buffer
				 pdss-command-name "-2" option)))
	(setq pdss-process
	      (start-process "pdss" nil ; pdss-console-buffer
			     pdss-command-name "-2")))
      (setq pdss-output-switch 0)
      (set-process-sentinel pdss-process 'pdss-sentinel)
      (set-process-filter pdss-process 'pdss-filter)))
  (setq pdss-current-output-buffer pdss-console-buffer)
  (pop-to-buffer pdss-console-buffer))

;;-----------------------------------------------------------------------------
;; PDSS mode definition.

(defun pdss-mode (id)
  "Major mode for interacting with PDSS.
In this mode, the following commands can be used:
\\{pdss-map}"
  (interactive)
  (kill-all-local-variables)
  (setq major-mode 'pdss-mode)
  (setq mode-name "PDSS")
  (use-local-map pdss-map)
  (set-syntax-table kl1-mode-syntax-table)
  (goto-char (point-max))
  (make-local-variable 'pdss-buffer-id)
  (setq pdss-buffer-id id)
  (make-local-variable 'pdss-last-input)
  (setq pdss-last-input "")
  (make-local-variable 'pdss-output-start)
  (setq pdss-output-start (move-marker (make-marker) (point)))
  (make-local-variable 'pdss-output-end)
  (setq pdss-output-end (move-marker (make-marker) (point)))
  (run-hooks 'pdss-mode-hook))

(defvar pdss-map nil)
(if (null pdss-map)
    (let ((map (make-sparse-keymap)))
      (setq pdss-map map)
      (define-key map "\C-c\C-f" 'pdss-manual-builtin-predicate)
      (define-key map "\C-cf"    'pdss-manual-mpimos-command)
      (define-key map "\C-c\C-b" 'pdss-buffer-menu)
      (define-key map "\C-m"     'pdss-send-input)
      (define-key map "\C-c\C-y" 'pdss-copy-last-input)
      (define-key map "\C-ck"    'pdss-buffer-erase)
      (define-key map "\C-c\C-k" 'pdss-all-buffer-erase)
      (define-key map "\C-c\C-[" 'pdss)
      (define-key map "\C-c\C-z" 'pdss-send-interrupt)
      (define-key map "\C-c\C-t" 'pdss-send-statistics)
      (define-key map "\C-c\C-d" 'pdss-send-end-of-file)
      (define-key map "\C-c\C-c" 'pdss-send-trace-on)
      (define-key map "\C-c@"    'pdss-send-terminate)
      (define-key map "\C-c!"    'pdss-send-gc-on)
      (define-key map "\e."      'pdss-dabbrev-expand)
      (define-key map "\C-cm"    'pdss-insert-predicate-id)
      (define-key map "\C-xk"    'pdss-warning-kill-buffer)))

(global-set-key "\C-c\C-p" 'pdss-switch-next-buffer) ; switch to pdss buffer
(global-set-key "\C-cp"    'pdss-popup-next-buffer)  ; pop to pdss buffer

(autoload 'pdss-manual-builtin-predicate
	  (concat pdss-emacs-directory-name "pdss-manual")
	  "Looking for builtin predicate manual." t)
(autoload 'pdss-manual-mpimos-command
	  (concat pdss-emacs-directory-name "pdss-manual")
	  "Looking for Micro PIMOS command manual." t)

(defvar kl1-mode-syntax-table nil)
(if (null kl1-mode-syntax-table)
    (let ((table (make-syntax-table)))
      (setq kl1-mode-syntax-table table)
      (modify-syntax-entry ?\n ">"    table) ;; end comment
      (modify-syntax-entry ?!  "."    table)
      (modify-syntax-entry ?\" "\""   table) ;; string
      (modify-syntax-entry ?#  "."    table)
      (modify-syntax-entry ?$  "."    table)
      (modify-syntax-entry ?%  "<"    table) ;; comment
      (modify-syntax-entry ?&  "."    table)
      (modify-syntax-entry ?\' "\""   table) ;; string
      (modify-syntax-entry ?\( "()"   table) ;; open
      (modify-syntax-entry ?\) ")("   table) ;; close
      (modify-syntax-entry ?*  ". 23" table)
      (modify-syntax-entry ?+  "."    table)
      (modify-syntax-entry ?,  "."    table)
      (modify-syntax-entry ?-  "."    table)
      (modify-syntax-entry ?.  "."    table)
      (modify-syntax-entry ?/  ". 14" table)
      (modify-syntax-entry ?:  "."    table)
      (modify-syntax-entry ?;  "."    table)
      (modify-syntax-entry ?<  "."    table)
      (modify-syntax-entry ?=  "."    table)
      (modify-syntax-entry ?>  "."    table)
      (modify-syntax-entry ??  "."    table)
      (modify-syntax-entry ?@  "."    table)
      (modify-syntax-entry ?[  "(]"   table) ;; open
      (modify-syntax-entry ?\\ "."    table)
      (modify-syntax-entry ?]  ")["   table) ;; close
      (modify-syntax-entry ?^  "."    table)
      (modify-syntax-entry ?_  "_"    table)
      (modify-syntax-entry ?`  "."    table)
      (modify-syntax-entry ?\{ "(}"   table) ;; open
      (modify-syntax-entry ?\| "."    table)
      (modify-syntax-entry ?\} "){"   table) ;; close
      (modify-syntax-entry ?~  "."    table)))

;;-----------------------------------------------------------------------------
;; Keyboard to PDSS process. (called by CR)

(defun pdss-send-input ()
  (interactive)
  (end-of-line)
  (let ((start (make-marker))
	(end (make-marker)))
    (if (eobp)
	(progn
	  (beginning-of-line)
	  (if (> (point) (marker-position pdss-output-end))
	      (move-marker start (point))
	    (move-marker start (marker-position pdss-output-end)))
	  (goto-char (point-max))
	  (insert ?\n)
	  (move-marker end (point)))
      (beginning-of-line)
      (re-search-forward "^[^-%]*[-%] *" nil t)
      (let ((copy (buffer-substring
		   (point) (progn (forward-line 1) (point)))))
	(goto-char (point-max))
	(move-marker start (point))
	(insert copy)
	(move-marker end (point))))
    (send-string pdss-process (char-to-string (+ ?A pdss-buffer-id)))
    (send-region pdss-process start end)
    (interrupt-process pdss-process)
    (setq pdss-last-input (buffer-substring start end)))
  (move-marker pdss-output-start (point))
  (move-marker pdss-output-end (point)))

;;-----------------------------------------------------------------------------
;; Other commands for PDSS process.

(defun pdss-copy-last-input ()
  (interactive)
  (insert pdss-last-input)
  (delete-char -1))

(defun pdss-buffer-erase ()
  (interactive)
  (erase-buffer)
  (move-marker pdss-output-start (point))
  (move-marker pdss-output-end (point)))

(defun pdss-all-buffer-erase ()
  (interactive)
  (let ((bl pdss-buffer-list)
	(cb (current-buffer)))
    (while bl
      (set-buffer (cdr (car bl)))
      (erase-buffer)
      (move-marker pdss-output-start (point))
      (move-marker pdss-output-end (point))
      (setq bl (cdr bl)))
    (set-buffer cb)))

(defun pdss-send-interrupt ()
  (interactive)
  (pdss-cancel-input)
  (send-string pdss-process (char-to-string (+ ?a pdss-buffer-id)))
  (send-string pdss-process "1\n")
  (interrupt-process pdss-process))

(defun pdss-send-statistics ()
  (interactive)
  (pdss-cancel-input)
  (send-string pdss-process (char-to-string (+ ?a pdss-buffer-id)))
  (send-string pdss-process "2\n")
  (interrupt-process pdss-process))

(defun pdss-send-end-of-file ()
  (interactive)
  (pdss-cancel-input)
  (send-string pdss-process (char-to-string (+ ?a pdss-buffer-id)))
  (send-string pdss-process "9\n")
  (interrupt-process pdss-process))

(defun pdss-send-trace-on ()
  (interactive)
  (send-string pdss-process "?\n")
  (interrupt-process pdss-process))

(defun pdss-send-gc-on ()
  (interactive)
  (send-string pdss-process "!\n")
  (interrupt-process pdss-process))

(defun pdss-send-terminate ()
  (interactive)
  (kill-process pdss-process))
;;  (interrupt-process pdss-process))

(defun pdss-cancel-input ()
  (goto-char (point-max))
  (let ((end (point)))
    (goto-char (marker-position pdss-output-end))
    (delete-char (- end (point)))))

;;-----------------------------------------------------------------------------
;; PDSS process to emacs buffers.

(defun pdss-sentinel (proc reason)
  (setq reason (substring reason 0 (- (length reason) 1)))
  (if (or (string= reason "finished")
	  (string= reason "interrupt"))
      (message "PDSS is Terminated.")
    (ding)
    (message "PDSS is Aborted. (%s)." reason))
  (setq pdss-process nil)
  (setq pdss-buffer-list nil)
  (setq pdss-buffer-tail nil)
  (setq pdss-buffer-count 0)
  (let ((cb (current-buffer)))
    (pdss-special-function-set-mode-name "PDSS: Aborted")
    (set-buffer cb)))

(defun pdss-filter (proc string)
  (funcall (aref pdss-dispatch-table pdss-output-switch) string)
  (set-buffer (window-buffer (selected-window))))

;; subroutine function.
;;
;;       |<-- 3 -->|<--- 4 --->|
;;       +---------+-----------+
;; TAG:  | Command | buffer ID |
;;       +---------+-----------+
;; Command
;;      2  \040: write string to buffer
;;      3  \060: create new buffer
;;      4  \100: kill buffer
;;      5  \120: show buffer
;;      6  \140: hide buffer
(defun pdss-read-tag (string)
  (if (string= string "")
      nil
    (let ((cc (string-to-char string))
	  (bf nil)
	  (c nil))
      (setq bf (assoc (logand cc 15) pdss-buffer-list))
      (setq c (logand cc 112))
      (cond
       ((eq c 32)			;write string to buffer
	(if bf
	    (progn
	      (setq pdss-current-output-buffer (cdr bf))
	      (setq pdss-output-switch 1)
	      (pdss-insert-to-current-buffer (substring string 1 nil)))
	  (setq pdss-current-output-buffer nil)	;error: buffer isn't exist
	  (setq pdss-output-switch 1)
	  (pdss-insert-to-current-buffer (substring string 1 nil))))
       ((eq c 48)			;create new buffer
	(progn
	  (setq pdss-new-buffer-id (logand cc 15))
	  (setq pdss-new-buffer-name "")
	  (setq pdss-output-switch 2)	;set to the buffer-name read mode
	  (pdss-read-buffer-name (substring string 1 nil))))
       ((eq c 64)			;kill buffer
	(if (null bf)
	    nil				;error: buffer isn't exist
	  (pdss-kill-buffer (cdr bf) (car bf))
	  (setq pdss-output-switch 0)
	  (pdss-read-tag (substring string 1 nil))))
       ((eq c 80)			;show buffer
	(if (null bf)
	    nil				;error: buffer isn't exist
	  (pdss-show-buffer (cdr bf))
	  (setq pdss-output-switch 0)
	  (pdss-read-tag (substring string 1 nil))))
       ((eq c 96)			;hide
	(if (null bf)
	    nil				;error: buffer isn't exist
	  (pdss-hide-buffer (cdr bf))
	  (setq pdss-output-switch 0)
	  (pdss-read-tag (substring string 1 nil))))
       ((eq c 112)			;special
	(pdss-special-function (logand cc 15))
	(setq pdss-output-switch 0)
	(pdss-read-tag (substring string 1 nil)))))))

;;-----------------------------------------------------------------------------
;; Create new buffer for PDSS.

(defun pdss-read-buffer-name (string)
  (let ((p1 (string-match "\01" string 0)))
    (if p1
	(let ((name (concat pdss-new-buffer-name (substring string 0 p1))))
	  (pdss-create-buffer name pdss-new-buffer-id)
	  (setq pdss-output-switch 0)
	  (pdss-read-tag (substring string (+ p1 1) nil)))
      (setq pdss-new-buffer-name (concat pdss-new-buffer-name string)))))

(defun pdss-create-buffer (name new-id)
  (let* ((new-buffer (generate-new-buffer (concat "PDSS-" name)))
	 (cb (current-buffer)))
    (setq pdss-buffer-list (cons (cons new-id new-buffer) 
				 pdss-buffer-list))
    (setq pdss-buffer-count (+ 1 pdss-buffer-count))
    (set-buffer new-buffer)
    (pdss-mode new-id)
    (if (not (fboundp 'change-process-code))	; Use EUC code for kanji.
	(setq kanji-fileio-code 0)		; for NEmacs 2.1
      (make-local-variable 'default-kanji-process-code)
      (setq default-kanji-process-code 3))	; for NEmacs 3.0
    (setq case-fold-search nil)
    (setq case-replace nil)
    (set-buffer cb)
    new-buffer))

;;-----------------------------------------------------------------------------
;; Output (Insert) text to buffers.

(defun pdss-insert-to-current-buffer (string)
  (let ((p1 0))
    (if (setq p1 (string-match "[\001\007\014]" string 0))
	(let ((string1 (substring string 0 p1))
	      (command (string-to-char (substring string p1 (+ p1 1))))
	      (string2 (substring string (+ p1 1) nil)))
	  (cond
	   ((eq command 1)	; end of insert, next is TAG
	    (if (not (string= "" string1)) (pdss-insert string1))
	    (setq pdss-output-switch 0)
	    (pdss-read-tag string2))
	   ((eq command 7)	; beep
	    (pdss-insert string1)
	    (beep)
	    (pdss-insert-to-current-buffer string2))
	   ((eq command 12)	; clear buffer
	    (pdss-buffer-erase)
	    (pdss-insert-to-current-buffer string2))))
      (pdss-insert string))))

(defun pdss-insert (string)
  (if pdss-current-output-buffer
      (if (eq pdss-current-output-buffer (current-buffer))
	  (let ((pp (point))
		(ip (marker-position pdss-output-end)))
	    (goto-char ip)
	    (insert string)
	    (move-marker pdss-output-end (point))
	    (if (< pp ip)
		(goto-char pp)
	      (goto-char (+ pp (- (point) ip)))))
	(let ((cb (current-buffer)))
	  (set-buffer pdss-current-output-buffer)
	  (let ((pp (point))
		(ip (marker-position pdss-output-end)))
	    (goto-char ip)
	    (insert string)
	    (move-marker pdss-output-end (point))
	    (if (< pp ip)
		(goto-char pp)
	      (goto-char (+ pp (- (point) ip)))
	      (if (get-buffer-window pdss-current-output-buffer)
		  (set-window-point
		   (get-buffer-window pdss-current-output-buffer)
		   (point)))))
	  (set-buffer cb)))))

;;-----------------------------------------------------------------------------
;; Other commands to buffers.

(defun pdss-kill-all-buffers ()
  (interactive)
  (if (> pdss-buffer-count 0)
      (let ((bf nil))
	(while (setq bf (cdr (car pdss-buffer-list)))
	  (setq pdss-buffer-list (cdr pdss-buffer-list))
	  (kill-buffer bf))))
  (setq pdss-buffer-list nil)
  (setq pdss-buffer-tail nil)
  (setq pdss-buffer-count 0))

(defun pdss-kill-buffer (buffer id)
  (kill-buffer buffer)
  (if pdss-buffer-list
      (let ((l pdss-buffer-list)
	    (n (cdr pdss-buffer-list)))
	(if (eq (car (car l)) id)
	    (setq pdss-buffer-list n)
	  (while (not (eq (car (car n)) id))
	    (setq n (cdr (setq l n))))
	  (if (eq n pdss-buffer-tail)
	      (setq pdss-buffer-tail l))
	  (rplacd l (cdr n)))
	(setq pdss-buffer-count (- 1 pdss-buffer-count)))))

(defun pdss-show-buffer (buffer)
  (if (null (get-buffer-window buffer))
      (pop-to-buffer buffer)))

(defun pdss-hide-buffer (buffer)
  (if (get-buffer-window buffer)
      (replace-buffer-in-windows buffer)))

(defun pdss-special-function (code)
  (let ((cb (current-buffer)))
    (cond
     ((eq code 0)
      (pdss-special-function-set-mode-name "PDSS: Running"))
     ((eq code 1)
      (pdss-special-function-set-mode-name "PDSS:  Idling"))
     ((eq code 2)
      (pdss-special-function-set-mode-name "PDSS: RD-Cons")))
    (set-buffer cb)))

(defun pdss-special-function-set-mode-name (name)
  (let ((list pdss-buffer-list))
    (while list
      (set-buffer (cdr (car list)))
      (setq mode-name name)
      (setq list (cdr list)))))

;;-----------------------------------------------------------------------------
;; Keyboard commands to buffers.

(defun pdss-insert-predicate-id ()
  (interactive)
  (let (s)
    (if (not (setq s (pdss-get-module-predicate)))
	(message "no match")
      (insert s))))

(defun pdss-get-module-predicate ()
  (let (str cp)
    (save-excursion
      (beginning-of-line)
      (if (not (re-search-forward
   "\\(Call\\|CALL\\|SUSP\\|Susp\\|RESU\\|SWAP\\|FAIL\\)\.\.: \\[\.\.\.\.\\]"))
	  nil
	(setq cp (point))
	(if (not (re-search-forward "(\\|\\."))
	    nil
	  (buffer-substring cp (- (match-end 0) 1)))))))

(defun pdss-buffer-menu ()
  (interactive)
  (list-buffers)
  (set-buffer "*Buffer List*")
  (toggle-read-only)
  (next-line 2)
  (delete-non-matching-lines "PDSS-")
  (toggle-read-only))

(defun pdss-switch-next-buffer ()
  (interactive)
  (if pdss-buffer-list
      (let ((l pdss-buffer-list)
	    (n (cdr pdss-buffer-list)))
	(if (get-buffer-window (cdr (car l)))
	    (while n
	      (if (get-buffer-window (cdr (car n)))
		  (setq n (cdr (setq l n)))
		(switch-to-buffer (cdr (car n)))
		(if (eq n pdss-buffer-tail)
		    nil
		  (rplacd l (cdr n))
		  (rplacd pdss-buffer-tail n)
		  (rplacd n nil)
		  (setq pdss-buffer-tail n))
		(setq n nil)))
	  (switch-to-buffer (cdr (car l)))
	  (if (eq l pdss-buffer-tail)
	      nil
	    (setq pdss-buffer-list (cdr l))
	    (rplacd pdss-buffer-tail l)
	    (rplacd l nil)
	    (setq pdss-buffer-tail l))))))

(defun pdss-popup-next-buffer ()
  (interactive)
  (if pdss-buffer-list
      (let ((l pdss-buffer-list)
	    (n (cdr pdss-buffer-list)))
	(if (get-buffer-window (cdr (car l)))
	    (while n
	      (if (get-buffer-window (cdr (car n)))
		  (setq n (cdr (setq l n)))
		(pop-to-buffer (cdr (car n)))
		(if (eq n pdss-buffer-tail)
		    nil
		  (rplacd l (cdr n))
		  (rplacd pdss-buffer-tail n)
		  (rplacd n nil)
		  (setq pdss-buffer-tail n))
		(setq n nil)))
	  (pop-to-buffer (cdr (car l)))
	  (if (eq l pdss-buffer-tail)
	      nil
	    (setq pdss-buffer-list (cdr l))
	    (rplacd pdss-buffer-tail l)
	    (rplacd l nil)
	    (setq pdss-buffer-tail l))))))

(defun pdss-warning-kill-buffer ()
  (interactive)
  (if (null pdss-process)
      (if (yes-or-no-p "Kill this buffer? ")
	  (pdss-kill-buffer-2 (current-buffer)))
    (ding)
    (if (eq (current-buffer) pdss-console-buffer)
	(error "Cannot kill PDSS-CONSOLE buffer"))
    (if (yes-or-no-p "PDSS System still running. Kill this buffer? ")
	(pdss-kill-buffer-2 (current-buffer)))))
		    
(defun pdss-kill-buffer-2 (buffer)
  (if pdss-buffer-list
      (let ((l pdss-buffer-list)
	    (n (cdr pdss-buffer-list)))
	(if (eq (cdr (car l)) buffer)
	    (setq pdss-buffer-list n)
	  (while (not (eq (cdr (car n)) buffer))
	    (setq n (cdr (setq l n))))
	  (if (eq n pdss-buffer-tail)
	      (setq pdss-buffer-tail l))
	  (rplacd l (cdr n)))
	(setq pdss-buffer-count (- 1 pdss-buffer-count))))
  (kill-buffer buffer)
  (if (eq pdss-current-output-buffer buffer)
      (setq pdss-current-output-buffer nil)))

(defun pdss-read-y (mess)		; if "y" then return t else return nil
  (message mess)
  (let ((c (read-char)))
    (while (not (or (eq c ?n) (eq c ?y)))
      (message "Answer (y or n). %s" mess)
      (setq c (read-char)))
    (if (eq c ?y) t nil)))

;;-----------------------------------------------------------------------------
;; Dynamic abbreviation package for PDSS.
;; based on
; ;; Dynamic abbreviation package for GNU Emacs.
; ;; Copyright (C) 1985, 1986 Free Software Foundation, Inc.
;
; ;; This file is part of GNU Emacs.
;
; ;; GNU Emacs is distributed in the hope that it will be useful,
; ;; but WITHOUT ANY WARRANTY.  No author or distributor
; ;; accepts responsibility to anyone for the consequences of using it
; ;; or for whether it serves any particular purpose or works at all,
; ;; unless he says so in writing.  Refer to the GNU Emacs General Public
; ;; License for full details.
;
; ;; Everyone is granted permission to copy, modify and redistribute
; ;; GNU Emacs, but only under the conditions described in the
; ;; GNU Emacs General Public License.   A copy of this license is
; ;; supposed to have been given to you along with GNU Emacs so you
; ;; can know your rights and responsibilities.  It should be in a
; ;; file named COPYING.  Among other things, the copyright notice
; ;; and this notice must be preserved on all copies.
;
;
; ; DABBREVS - "Dynamic abbreviations" hack, originally written by Don Morrison
; ; for Twenex Emacs.  Converted to mlisp by Russ Fish.  Supports the table
; ; feature to avoid hitting the same expansion on re-expand, and the search
; ; size limit variable.  Bugs fixed from the Twenex version are flagged by
; ; comments starting with ;; ; .
; ; 
; ; converted to elisp by Spencer Thomas.
; ; Thoroughly cleaned up by Richard Stallman.
; ;  
; ; If anyone feels like hacking at it, Bob Keller (Keller@Utah-20) first
; ; suggested the beast, and has some good ideas for its improvement, but
; ; doesn?tknow TECO (the lucky devil...).  One thing that should definitely
; ; be done is adding the ability to search some other buffer(s) if you can?t
; ; find the expansion you want in the current one.

(defvar pdss-dabbrevs-limit nil
  "*Limits region searched by dabbrevs-expand to that many chars away (local)")
(make-variable-buffer-local 'pdss-dabbrevs-limit)

(defvar pdss-last-dabbrevs-abbreviation ""
  "Last string we tried to expand.  Buffer-local.")
(make-variable-buffer-local 'pdss-last-dabbrevs-abbreviation)

(defvar pdss-last-dabbrevs-abbrev-location nil
  "Location last abbreviation began (local).")
(make-variable-buffer-local 'pdss-last-dabbrevs-abbrev-location)

(defvar pdss-last-dabbrevs-expansion nil
    "Last expansion of an abbreviation. (local)")
(make-variable-buffer-local 'pdss-last-dabbrevs-expansion)

(defvar pdss-last-dabbrevs-expansion-location nil
  "Location the last expansion was found. (local)")
(make-variable-buffer-local 'pdss-last-dabbrevs-expansion-location)

(defvar pdss-shell-prompt         "?-"    "")
(defvar pdss-shell-prompt-pattern "\?- *" "")

(defun pdss-dabbrev-expand (arg)
  "Expand previous shell commands \"dynamically\".
Expands to the most recent, preceding word for which this is a prefix.
If no suitable preceding word is found, words following point are considered.

A positive prefix argument, N, says to take the Nth backward DISTINCT
possibility.

If the cursor has not moved from the end of the previous expansion and
no argument is given, replace the previously-made expansion
with the next possible expansion not yet tried."
  (interactive "*P")
  (let (abbrev expansion old which loc n pattern)
    ;; abbrev -- the abbrev to expand
    ;; expansion -- the expansion found (eventually) or nil until then
    ;; old -- the text currently in the buffer
    ;;    (the abbrev, or the previously-made expansion)
    ;; loc -- place where expansion is found
    ;;    (to start search there for next expansion if requested later)
    (save-excursion
      (if (and (null arg)
	       (eq last-command this-command)
	       pdss-last-dabbrevs-abbrev-location)
	  (progn
	    (setq abbrev pdss-last-dabbrevs-abbreviation)
	    (setq old pdss-last-dabbrevs-expansion)
	    (setq which 1))
	(setq which (if (null arg) 1 (prefix-numeric-value arg)))
	(setq loc (point))
	(forward-word -1)
	(setq pdss-last-dabbrevs-abbrev-location (point)) ; Original location.
	(setq abbrev (buffer-substring (point) loc))
	(setq old abbrev)
	(setq pdss-last-dabbrevs-expansion-location nil)
	(setq last-dabbrev-table nil))  	; Clear table of things seen.
      (setq pattern (concat pdss-shell-prompt-pattern
		     "\\b" (regexp-quote abbrev)))

      ;; Try looking backward unless inhibited.
      (if (>= which 0)
	  (progn 
	    (setq n (max 1 which))
	    (if pdss-last-dabbrevs-expansion-location
		(goto-char pdss-last-dabbrevs-expansion-location))
	    (while (and (> n 0)
			(setq expansion (pdss-dabbrevs-search pattern)))
	      (setq loc (point-marker))
	      (setq last-dabbrev-table (cons expansion last-dabbrev-table))
	      (setq n (1- n)))
	    (or expansion (setq pdss-last-dabbrevs-expansion-location nil)))))

    (if (not expansion)
	(let ((first (string= abbrev old)))
	  (setq pdss-last-dabbrevs-abbrev-location nil)
	  (if (not first)
	      (progn (undo-boundary)
		     (delete-backward-char (length old))
		     (insert abbrev)))
	  (error (if first
		     "No dynamic expansion for \"%s\" found."
		     "No further dynamic expansions for \"%s\" found.")
		 abbrev))
      ;; Success: stick it in and return.
      (undo-boundary)
      (search-backward old)
      (replace-match expansion t 'literal)
      ;; Save state for re-expand.
      (setq pdss-last-dabbrevs-abbreviation abbrev)
      (setq pdss-last-dabbrevs-expansion expansion)
      (setq pdss-last-dabbrevs-expansion-location loc))))

;; Search function used by dabbrevs library.  
;; First arg is string to find as prefix of word.  Second arg is
;; t for reverse search, nil for forward.  Variable pdss-dabbrevs-limit
;; controls the maximum search region size.

;; Table of expansions already seen is examined in buffer last-dabbrev-table,
;; so that only distinct possibilities are found by dabbrevs-re-expand.
;; Note that to prevent finding the abbrev itself it must have been
;; entered in the table.

;; Value is the expansion, or nil if not found.  After a successful
;; search, point is left right after the expansion found.

(defun pdss-dabbrevs-search (pattern)
  (let (missing result cmd-start-point line-end-point)
    (save-restriction 	    ; Uses restriction for limited searches.
      (if pdss-dabbrevs-limit
	  (narrow-to-region pdss-last-dabbrevs-abbrev-location
			    (+ (point)
			       (* pdss-dabbrevs-limit -1))))
      ;; Keep looking for a distinct expansion.
      (setq result nil)
      (setq missing nil)
      (while  (and (not result) (not missing))
	; Look for it, leave loop if search fails.
	(setq missing (not (re-search-backward pattern nil t)))
	(if (not missing)
	    (progn
	      (setq cmd-start-point 
		    (+ (match-beginning 0) (length pdss-shell-prompt)))
	      (save-excursion
		(goto-char cmd-start-point)
		(end-of-line)
		(setq line-end-point (point)))
	      (setq result (buffer-substring cmd-start-point
					     line-end-point))
	      (if (string= " " (substring result 0 1))
		  (setq result (substring result 1 (length result))))
	      (let* ((test last-dabbrev-table))
		(while (and test (not (string= (car test) result)))
		  (setq test (cdr test)))
		(if test (setq result nil))))))	; if already in table, ignore
      result)))
