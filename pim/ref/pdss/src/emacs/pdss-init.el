;; GNU Emacs initiation file for PDSS V2.5  (89.09.13)
;; Copy this file to emacs/lisp directory (see Makefile),
;; and insert following command into user's .emacs file.
;;	(load "pdss-init")

;;-----------------------------------------------------------------------------
;; Path Names.

(defconst pdss-directory-name
  "/usr/local/src/pdss/"
  "Directory path name of PDSS.")

(defconst pdss-emacs-directory-name
  "/usr/local/src/pdss/emacs/"
  "Directory path name of PDSS.")

(defconst pdss-command-name
  (concat pdss-directory-name "emulator/pdss")
  "Command path name of PDSS emulator.")

(defconst pdss-kl1cmp-compiler
  (concat pdss-directory-name "compiler_pl/kl1cmp")
  "Command path name of KL1/Prolog compiler.")

(defconst pdss-kl1cmp-startup-file
  (concat pdss-directory-name "emulator/KL1CMP")
  "Path name of startup file for KL1/KL1 compiler.")

(defconst pdss-kl1cmp-translator
  (concat pdss-directory-name "compiler_pl/pdsstrans")
  "Command path name of KLB->ASM translator.")

(defconst pdss-kl1cmp-code-merger
  (concat pdss-directory-name "emulator/pdssmerge")
  "Command path name of ASM code merger.")

(defconst pdss-kl1cmp-assembler
  (concat pdss-directory-name "emulator/pdssasm")
  "Command path name of PDSS assembler.")

(defconst pdss-manual-file-name
  (concat pdss-directory-name "doc.j/pdss.tex")
  "Path name of PDSS manual file.")

;;-----------------------------------------------------------------------------
;; Auto Loading.

(autoload 'pdss
	  (concat pdss-emacs-directory-name "pdss")
	  "Run PDSS emulator." t)
(autoload 'kl1-mode
	  (concat pdss-emacs-directory-name "kl1-mode")
	  "Mode for editing KL1 code." t)
(autoload 'pdss-manual-builtin-predicate
	  (concat pdss-emacs-directory-name "pdss-manual")
	  "Looking for builtin predicate manual." t)
(autoload 'pdss-manual-mpimos-command
	  (concat pdss-emacs-directory-name "pdss-manual")
	  "Looking for Micro PIMOS command manual." t)

(setq auto-mode-alist
      (cons '("\\.kl1$" . kl1-mode) auto-mode-alist))
