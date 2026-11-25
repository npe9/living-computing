;;-----------------------------------------------------------------------------
;;   kl1-mode: Major mode for editing KL1 source for PDSS V2.5	(90.04.25)
;;-----------------------------------------------------------------------------


(defun kl1-mode ()
  "								    [90.02.13]
	  ＫＬ１のソースコードを編集するためのメジャーモード
	 ====================================================


このモードでは標準のコマンド以外に次のようなコマンドを使用できる。


クローズ操作コマンド
--------------------
    ESC a	カーソルをクローズの先頭に移動する。(繰り返し回数の指定可)
    ESC e	カーソルをクローズの最後に移動する。(繰り返し回数の指定可)
    ESC k	カーソルのあるクローズを削除する。(繰り返し回数の指定可)
    ESC ?       カーソルのあるクローズのモジュール名,述語名,アリティを調べる。
                また、それを mod:pred/arity の形で kill-ring にセーブする。

字下げ操作コマンド
------------------
    TAB		カーソルのある行の字下げを行う。この時の字下げ幅はKL1の構文を
		調べて(注1)決められる。この時、以下の定数(注2)を参照する。
		    kl1-head-indent-level   : ヘッド部の字下げ幅
		    kl1-guard-indent-level  : ガードゴールの字下げ幅
		    kl1-body-indent-level   : ボディゴールの字下げ幅
		また、述語引数や構造体の途中で改行している場合には、その構造を
		開始した左括弧 ( { [ の位置を元に字下げ位置を決める。
    LFD		カーソルのある位置に改行を挿入後、TAB と同様な字下げを行う。
    ESC X indent-region
		カーソルとマークの間の各行に対して TAB と同様な字下げを行う。

コメント操作コマンド
--------------------
    ESC ;	カーソルのある行にコメントが無ければ、KL1の構文上適当な位置に
		(注1) コメントを作り、その中にカーソルを移動する。既にコメント
		が有れば、コメントの位置を適当な桁位置に移動し、カーソルをコメ
		ント本文の最初の文字に移動する。
    C-X ;	カーソルのある桁位置をコメント開始位置として登録する。この位置
		はKL1コードの右側に書かれるコメントの開始位置として使われる。
		初期値は定数 kl1-comment-column (注2)の値がセットされる。

マニュアル検索コマンド
----------------------
    C-C C-F	PDSSのマニュアルを検索し、指定された組込述語の説明を専用のバッ
		ファに表示する。

コンパイルコマンド
------------------
    C-C C-C	編集中のバッファにあるKL1ソースコード全体をファイルにセーブし、
		コンパイルする。コンパイラはEMACSの子プロセスとして並列に実行
		され、コンパイル中のメッセージ等は専用のバッファに出力される。
    C-C C-R	KL1コードの部分コンパイルのために指定されたリージョンを別のバッ
		ファにコピーする。この後 C-C C-D コマンドで実際のコンパイルを
		行う。なお、このコマンドを複数回使う事により複数の「部分」を指
		定する事ができる。
    C-C C-K	部分コンパイルのために選択したものを棄てる。
    C-C C-D	KL1コードの部分コンパイルを行う。
    C-C C-Z	コンパイラをアボートする。
    ESC X pdss-kl1cmp-switch-system-mode
		コンパイルモード(一般用またはシステム用)の切り替えを行う。一般
		用のモードではシステム専用の組込述語を使う事ができない。デフォ
		ルトでは一般ユーザー用モード。
    ESC X pdss-kl1cmp-switch-indexing-mode
		クローズインデキシング機能を使う/使わないの切り替えを行う。デ
		フォルトではクローズインデキシング機能を使う。
    ESC X pdss-kl1cmp-switch-mrbgc-mode
		MRB-GCの為の回収命令を生成する/しないの切り替えを行う。デフォ
		ルトでは回収命令を生成する。


 注1: この kl1-mode ではKL1の全ての構文をサポートしている訳ではないので、以下
      のような構文を使っている場合には字下げ機能等が正しく働かない。
	・ 条件分岐のマクロを使っている場合。
	・ コミットメントバー `|' が無いクローズがある場合。
	・ :- や --> を含んでいるが引用符で囲まれていないアトムがある場合。
	・ ストリング等の中に改行コード含まれている場合。
	・ /* ... */ のコメントを使っている場合。

 注2: これらの定数は各ユーザーが .emacs ファイルの中で以下のような形で定義する
      事によりカスタマイズ可能になっている。
	    (setq kl1-mode-hook 'my-kl1-mode-init)
	    (defun my-kl1-mode-init ()
	      (setq kl1-head-indent-level  0)  ; ヘッド部の字下げ幅
	      (setq kl1-guard-indent-level 2)  ; ガードゴールの字下げ幅
	      (setq kl1-body-indent-level  4)) ; ボディゴールの字下げ幅"
  (interactive)
  (kill-all-local-variables)
  (setq major-mode 'kl1-mode)
  (setq mode-name "KL1")
  (use-local-map kl1-mode-map)
  (set-syntax-table kl1-syntax-table)
  (setq paragraph-start "^$\\|\f")
  (setq paragraph-separate "^$\\|\f")
  (make-local-variable 'kl1-head-indent-level)
  (make-local-variable 'kl1-guard-indent-level)
  (make-local-variable 'kl1-body-indent-level)
  (make-local-variable 'indent-line-function)
  (setq indent-line-function 'kl1-indent-line)
  (make-local-variable 'comment-column)
  (setq comment-column kl1-comment-column)
  (make-local-variable 'comment-start)
  (setq comment-start "%")
  (make-local-variable 'comment-end)
  (setq comment-end "")
  (make-local-variable 'comment-multi-line)
  (setq comment-multi-line nil)
  (make-local-variable 'comment-start-skip)
  (setq comment-start-skip "%+ *")
  (make-local-variable 'comment-indent-hook)
  (setq comment-indent-hook 'kl1-get-comment-column)
  ;; 標準のコメントの字下げには機能上不完全な部分があり文字列内にコメント開始
  ;; 文字 % があると正しく字下げされない。kl1-mode ではコメントの字下げを自分
  ;; で定義した関数で行う。
  (make-local-variable 'require-final-newline)
  (setq require-final-newline t)
  (run-hooks 'kl1-mode-hook))


(defvar kl1-mode-map nil)
(if (null kl1-mode-map)
    (let ((map (make-sparse-keymap)))
      ;; クローズ操作コマンド。
      (define-key map "\M-a"	 'kl1-backward-clause)
      (define-key map "\M-e"     'kl1-forward-clause)
      (define-key map "\M-k"	 'kl1-kill-clause)
      (define-key map "\M-?"	 'kl1-what-clause)
      ;; 字下げ操作コマンド。
      (define-key map "\t"	 'kl1-indent-line)
      (define-key map "\M-;"	 'kl1-indent-comment)
      ;; その他の編集コマンド。
      (define-key map "\177"	 'backward-delete-char-untabify)
      ;; マニュアル検索コマンド。→ pdss-manual.el を参照。
      (define-key map "\C-c\C-f" 'pdss-manual-builtin-predicate)
      ;; コンパイル用コマンド。→ pdss-kl1cmp.el を参照。
      (define-key map "\C-c\C-c" 'pdss-kl1cmp-compile-current-buffer)
      (define-key map "\C-c\C-r" 'pdss-kl1cmp-copy-region-to-buffer)
      (define-key map "\C-c\C-k" 'pdss-kl1cmp-clear-buffer)
      (define-key map "\C-c\C-d" 'pdss-kl1cmp-compile-regions)
      (define-key map "\C-c\C-z" 'pdss-kl1cmp-abort-compiler)
      (setq kl1-mode-map map)))


(autoload 'pdss-manual-builtin-predicate
  (concat pdss-emacs-directory-name "pdss-manual")
  "組込述語のマニュアルを検索する。" t)
(autoload 'pdss-kl1cmp-compile-current-buffer
  (concat pdss-emacs-directory-name "pdss-kl1cmp")
  "編集中のバッファにあるKL1ソースコード全体をコンパイルする。" t)
(autoload 'pdss-kl1cmp-copy-region-to-buffer
  (concat pdss-emacs-directory-name "pdss-kl1cmp")
  "部分コンパイルのために指定されたリージョンを別のバッファにコピーする。" t)
(autoload 'pdss-kl1cmp-switch-system-mode
  (concat pdss-emacs-directory-name "pdss-kl1cmp")
  "コンパイルモード(一般用/システム用)の切り替えを行う。" t)
(autoload 'pdss-kl1cmp-switch-indexing-mode
  (concat pdss-emacs-directory-name "pdss-kl1cmp")
  "クローズインデキシング機能を使う/使わないの切り替えを行う。" t)
(autoload 'pdss-kl1cmp-switch-mrbgc-mode
  (concat pdss-emacs-directory-name "pdss-kl1cmp")
  "MRB-GCの為の回収命令を生成する/しないの切り替えを行う。" t)


(defvar kl1-syntax-table nil)
(if (null kl1-syntax-table)
    (let ((table (make-syntax-table)))
      (setq kl1-syntax-table table)
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


;; kl1-mode で参照している定数の宣言。
;; これらの定数はソースコードのスタイルを指定する。
;; 各定数の数値はユーザーが .emacs ファイルの中で変更する事ができる。
(defconst kl1-head-indent-level   0  "*ヘッド部の字下げ幅。")
(defconst kl1-guard-indent-level  4  "*ガードゴールの字下げ幅。")
(defconst kl1-body-indent-level   8  "*ボディゴールの字下げ幅。")
(defconst kl1-comment-column     40  "コードの右に書くコメントの桁位置。")


;;-----------------------------------------------------------------------------


(defun kl1-backward-clause (&optional n)
  "この関数は現在 point があるクローズの先頭に point を移動する。もし、引数が
指定された場合には指定された個数だけ前のクローズに移動する。(引数が負ならば
kl1-forward-clause と同様な移動を行う。)"
  (interactive "p")
  (or n (setq n 1))
  (if (< n 0)
      (kl1-forward-clause (- 0 n))
    (while (>= (setq n (1- n)) 0)
      (while (and (not (bobp))
		  (kl1-is-point-out-of-clause))
	(skip-chars-backward "\0- ")
	(while (kl1-is-point-in-comment)
	  (search-backward "%" nil 'move)))
      (while (not (kl1-is-point-out-of-clause))
	(backward-char)
	(skip-chars-backward "^\0- ")
	(while (kl1-is-point-in-comment)
	  (search-backward "%" nil 'move))))))


(defun kl1-forward-clause (&optional n)
  "この関数は現在 point があるクローズの最後に point を移動する。もし、引数が
指定された場合には指定された個数だけ後のクローズに移動する。(引数が負ならば
kl1-backward-clause と同様な移動を行う。)"
  (interactive "p")
  (or n (setq n 1))
  (if (< n 0)
      (kl1-backward-clause (- 0 n))
    (while (>= (setq n (1- n)) 0)
      (while (and (not (eobp))
		  (kl1-is-point-out-of-clause))
	(cond
	 ((looking-at "[\0- ]")
	  (skip-chars-forward "\0- "))
	 ((looking-at "%")
	  (end-of-line)
	  (skip-chars-forward "\0- "))
	 (t
	  (forward-char))))
      (while (and (< (point) (point-max))
		  (not (kl1-is-point-out-of-clause)))
	(cond
	 ((looking-at "[\0- ]")
	  (forward-char))
	 ((looking-at "%")
	  (end-of-line)
	  (skip-chars-forward "\0- "))
	 (t
	  (skip-chars-forward "^\0- ")))))))


(defun kl1-kill-clause (&optional n)
  "この関数は現在 point があるクローズを削除する。もし、引数が指定された場合
には指定された個数だけ後ろ向きにクローズを削除する。(引数が負ならば前向きに
削除する。)"
  (interactive "p")
  (or n (setq n 1))
  (save-excursion
    (let ((p0 (point)) p1 p2)
      (cond
       ((> n 0)
	(kl1-forward-clause)
	(kl1-backward-clause)
	(setq p1 (point))
	(kl1-forward-clause n)
      	(setq p2 (point))
	(if (and (<= p1 p0) (< p0 p2)) (kill-region p1 p2)))
       ((< n 0)
	(kl1-backward-clause)
	(kl1-forward-clause)
	(setq p2 (point))
	(kl1-backward-clause (- 0 n))
      	(setq p1 (point))
	(if (and (<= p1 p0) (< p0 p2)) (kill-region p1 p2)))))))


(defun kl1-what-clause ()
  "この関数は現在 point があるクローズのモジュール名, 述語名, アリティを調べ、
それをミニバッファに表示する。同時に、これを mod:pred/arity の形式で kill-
ring にセーブする。ctrl-Y で取り出すことができる。"
  (interactive)
  (save-excursion
    (let ((p0 (point)) p1 p2 msg
	  (module nil) pred arity (a0 nil) (a1 nil) (a2 nil))
      (message "This predicate is ...")
      (kl1-forward-clause)
      (setq p2 (point))
      (kl1-backward-clause)
      (setq p1 (point))
      (if (or (> p1 p0) (>= p0 p2))
	  (error "Point is not on KL1 clause !!"))
      (if (looking-at ":-")
	  (error "Point is on directive clause !!"))
      (skip-chars-forward "^a-zA-Z0-9_'")
      (setq p0 (point))
      (if (= (char-after (point)) ?')
	  (while (= (char-after (point)) ?')
	    (forward-char)
	    (skip-chars-forward "^'")
	    (forward-char))
	(skip-chars-forward "a-zA-Z0-9_"))
      (setq pred (buffer-substring p0 (point)))
      (message "This predicate is ... %s" pred)
      (setq arity (if (= (char-after (point)) ?\() (kl1-count-argument) 0))
      (message "This predicate is ... %s/%d" pred arity)
      (setq a0 (looking-at "[\0- ]*-->"))
      (if a0
	  (progn
	    (message "This predicate is ... %s/%d+" pred arity)
	    (while (and (null a2) (search-backward "local_implicit" nil t))
	      (if (and (not (kl1-is-point-in-string))
		       (eq (kl1-where-is-point) 'directive))
		  (setq a2 (kl1-count-implicit-argument))))
	    (goto-char (point-min))
	    (while (and (null a1) (re-search-forward "[^_]implicit" nil t))
	      (if (and (not (kl1-is-point-in-string))
		       (eq (kl1-where-is-point) 'directive))
		  (setq a1 (kl1-count-implicit-argument))))))
      (if a1 (setq arity (+ arity a1)))
      (if a2 (setq arity (+ arity a2)))
      (message "This predicate is ... %s/%d" pred arity)
      (goto-char (point-min))
      (while (and (null module) (search-forward "module" nil t))
	(if (and (not (kl1-is-point-in-string))
		 (eq (kl1-where-is-point) 'directive))
	    (progn
	      (skip-chars-forward "^a-zA-Z0-9_'")
	      (setq p0 (point))
	      (if (= (char-after (point)) ?')
		  (while (= (char-after (point)) ?')
		    (forward-char)
		    (skip-chars-forward "^'")
		    (forward-char))
		(skip-chars-forward "a-zA-Z0-9_"))
	      (setq module (buffer-substring p0 (point))))))
      (if (null module)
	  (error "Module name is not found !!"))
      (setq msg (concat module ":" pred "/" arity))
      (setq kill-ring (cons msg kill-ring))
      (setq kill-ring-yank-pointer kill-ring)
      (message "%s" msg))))

(defun kl1-count-argument ()
  (let ((count 1) (level 0) ch)
    (forward-char)
    (while (and (not (eobp)) (>= level 0))
      (skip-chars-forward "^,(){}[]'\"")
      (setq ch (char-after (point)))
      (cond
       ((= ch ?,)  (if (= level 0) (setq count (1+ count))))
       ((= ch ?\() (setq level (1+ level)))
       ((= ch ?\)) (setq level (1- level)))
       ((= ch ?\{) (setq level (1+ level)))
       ((= ch ?\}) (setq level (1- level)))
       ((= ch ?\[) (setq level (1+ level)))
       ((= ch ?\]) (setq level (1- level)))
       ((= ch ?\') (forward-char) (skip-chars-forward "^'"))
       ((= ch ?\") (forward-char) (skip-chars-forward "^\"")))
      (forward-char))
    count))

(defun kl1-count-implicit-argument ()
  (save-excursion
    (let ((count 0) (f t) ch)
      (while (and (not (eobp)) f)
	(skip-chars-forward "^:.'\"%")
	(setq ch (char-after (point)))
	(cond
	 ((= ch ?:)
	  (cond
	   ((looking-at ":[\0- ]*shared[,.%\0- ]") (setq count (1+ count)))
	   ((looking-at ":[\0- ]*stream[,.%\0- ]") (setq count (1+ count)))
	   ((looking-at ":[\0- ]*oldnew[,.%\0- ]") (setq count (+ count 2)))))
	 ((= ch ?.)  (setq f nil))
	 ((= ch ?\') (forward-char) (skip-chars-forward "^'"))
	 ((= ch ?\") (forward-char) (skip-chars-forward "^\""))
	 ((= ch ?%) (end-of-line)))
	(forward-char))
      count)))


(defun kl1-is-point-out-of-clause ()
  "この関数は point がクローズの外部(正確には、前のクローズの終わりの \". \"
の次の文字から point のあるクローズの最初の文字まで)にあるかを調べる。そして、
もしクロース外にある場合には t を、そうでない場合には nil を返す。"
  (save-excursion
    (let ((cp (point)))
      (skip-chars-backward "\0- ")
      (while (kl1-is-point-in-comment)
	(search-backward "%" nil 'move)
	(skip-chars-backward "\0- "))
      (or (= (point) (point-min))
	  (if (= (point) (1+ (point-min)))
	      (and (< (point) cp)
		   (string-match "\\.[\0- %]"
				 (buffer-substring (- (point) 1)
						   (+ (point) 1)))
		   t)
	    (and (< (point) cp)
		 (string-match "[^#$&*+--/:-@\\\\^`~]\\.[\0- %]"
			       (buffer-substring (- (point) 2)
						 (+ (point) 1)))
		 t))))))


(defun kl1-is-point-in-string ()
  "この関数は point が引用符(ストリングに使う \" またはアトムに使う ' )に囲ま
れた範囲内にあるかを調べる。そして、もし囲まれた範囲内にある場合には t を、
範囲外の場合には nil を返す。また、コメント内にある場合には必ず nil を返す。"
  (save-excursion
    (let ((cpoint (point)) mstr)
      (beginning-of-line)
      (catch 'comment-check-loop
	(while (re-search-forward "[\"'%]" cpoint 'move)
	  (setq mstr (buffer-substring (match-beginning 0) (match-end 0)))
	  (if (string-equal mstr "%")
	      (throw 'comment-check-loop nil))
	  (or (search-forward mstr cpoint 'move)
	      (throw 'comment-check-loop t)))
	nil))))


(defun kl1-is-point-in-comment ()
  "この関数は point が % で始まるコメント内にあるかを調べる。そして、もしコメ
ント内にある場合には t を、コメント外の場合には nil を返す。"
  (save-excursion
    (let ((cpoint (point)) mstr)
      (beginning-of-line)
      (catch 'string-check-loop
	(while (re-search-forward "[\"'%]" cpoint 'move)
	  (setq mstr (buffer-substring (match-beginning 0) (match-end 0)))
	  (if (string-equal mstr "%")
	      (throw 'string-check-loop t))
	  (or (search-forward mstr cpoint 'move)
	      (throw 'string-check-loop nil)))
	nil))))


(defun kl1-where-is-point ()
  "この関数は point がKL1のソースプログラムのどの部分にあるかを調べる。そして、
位置により以下のような値(アトム)を返す。
	ヘッド部 : head		文字列中等 : string
	ガード部 : guard	コメント中 : comment
	ボディ部 : body		指示部	   : directive"
  (save-excursion
    (if (kl1-is-point-in-comment) 'comment
      (if (kl1-is-point-in-string) 'string
	(let ((flag nil) (stack nil) mstr)
	  (catch 'syntax-check-loop
	    (while (re-search-backward
		    "[^#$&*+--/:-@\\\\^`~]\\.[\0- ]\\|[][(){}|'\"]\\|:-\\|-->"
		    nil 'move)
	      (setq mstr (buffer-substring (match-beginning 0) (match-end 0)))
	      (if (kl1-is-point-in-comment)
		  (search-backward "%" nil 'move)
		(cond
		 ((string-match "^[]})]$" mstr)
		  (setq stack (cons flag stack))
		  (setq flag nil))
		 ((string-match "^[[{(]$" mstr)
		  (setq flag (if stack (car stack)))
		  (setq stack (if stack (cdr stack))))
		 ((string-equal mstr "'")
		  (if (kl1-is-point-in-string)
		      (search-backward "'" nil 'move)))
		 ((string-equal mstr "\"")
		  (if (kl1-is-point-in-string)
		      (search-backward "\"" nil 'move)))
		 ((string-equal mstr "|")
		  (or flag (setq flag 'body)))
		 ((string-equal mstr ":-")
		  (or flag
		      (setq flag (if (kl1-is-point-out-of-clause)
				     'directive 'guard))))
		 ((string-equal mstr "-->")
		  (or flag (setq flag 'guard)))
		 (t
		  (throw 'syntax-check-loop (or flag 'head))))))
	    (or flag 'head)))))))


(defun kl1-get-indent-column ()
  "この関数は point のある行を字下げする場合に、何桁目まで字下げすれば良いか
を計算する。この時、以下の定数を参照し字下げ位置を計算する。
        kl1-head-indent-level  : ヘッド部の字下げ幅
        kl1-guard-indent-level : ガードゴールの字下げ幅
        kl1-body-indent-level  : ボディゴールの字下げ幅
また、述語引数や構造体の途中で改行している場合には、左括弧 ( { [ の位置を
元に字下げ位置を計算する。"
  (save-excursion
    (beginning-of-line)
    (let ((level nil) (stack nil) mstr)
      (catch 'syntax-check-loop
	(while (re-search-backward
		"[^#$&*+--/:-@\\\\^`~]\\.[\0- ]\\|[][(){}|'\"]\\|:-\\|-->"
		nil 'move)
	  (setq mstr (buffer-substring (match-beginning 0) (match-end 0)))
	  (if (kl1-is-point-in-comment)
	      (search-backward "%" nil 'move)
	    (cond
	     ((string-match "^[]})]$" mstr)
	      (setq stack (cons level stack))
	      (setq level nil))
	     ((string-match "^[[{(]$" mstr)
	      (if (null stack)
		  (progn
		    (forward-char)
		    (if (not (looking-at "[ \t]+$\\|[ \t]+%"))
			(skip-chars-forward " \t"))
		    (throw 'syntax-check-loop (current-column))))
	      (setq level (car stack))
	      (setq stack (cdr stack)))
	     ((string-equal mstr "'")
	      (if (kl1-is-point-in-string)
		  (search-backward "'" nil 'move)))
	     ((string-equal mstr "\"")
	      (if (kl1-is-point-in-string)
		  (search-backward "\"" nil 'move)))
	     ((string-equal mstr "|")
	      (or level (setq level kl1-body-indent-level)))
	     ((string-equal mstr ":-")
	      (or level
		  (setq level (if (kl1-is-point-out-of-clause)
				  (progn (forward-word 1)
					 (skip-chars-forward "A-Za-z_")
					 (skip-chars-forward " \t")
					 (current-column))
				kl1-guard-indent-level))))
	     ((string-equal mstr "-->")
	      (or level (setq level kl1-guard-indent-level)))
	     (t
	      (throw 'syntax-check-loop
		     (or level kl1-head-indent-level))))))
	(or level kl1-head-indent-level)))))


(defun kl1-indent-line ()
  "この関数は point のある行の字下げを行う。字下げの幅は関数 kl1-get-indent-
column により計算された値を用いる。また、KL1コードの左側にコメントがある
場合にはその位置も関数 kl1-get-comment-column により計算された位置に移動
する。"
  (interactive)
  (let ((indent (kl1-get-indent-column)) start)
    (save-excursion
      (beginning-of-line)
      (setq start (point))
      (skip-chars-forward " \t")
      (delete-region start (point))
      (indent-to-column indent))
    (if (> indent (current-column))
	(move-to-column indent))
    (save-excursion
      (end-of-line)
      (if (kl1-is-point-in-comment)
	  (kl1-indent-comment)))))


(defun kl1-get-comment-column ()
  "この関数は point のある行に関してコメントの開始位置を計算する。もしその行
が空行またはコメントだけの行であれば、その上の行を調べ、そこにコメントがあれ
ば、開始位置をその位置に合わせ、なければ、開始位置を関数 kl1-get-indent-
column で計算された位置(通常のKL1コードの字下げ位置)と同じとする。また、
もしその行に一般のKL1コードがある場合には変数 comment-column で指定された
桁位置(初期値は定数 kl1-comment-column で与えられ、コマンド M-X set-comment-
column により変更可能。)とその行のKL1コードの右端の桁位置+1との大きい方と
する。"
  (save-excursion
    (beginning-of-line)
    (if (looking-at "[ \t]*$\\|[ \t]*%")
	(if (not (bobp))
	    (progn (backward-char)
		   (if (kl1-is-point-in-comment)
		       (progn (while (kl1-is-point-in-comment)
				(search-backward "%" nil 'move))
			      (current-column))
		     (forward-char)
		     (kl1-get-indent-column)))
	  (kl1-get-indent-column))
      (end-of-line)
      (while (kl1-is-point-in-comment)
	(search-backward "%" nil 'move))
      (skip-chars-backward " \t")
      (max (1+ (current-column))
	   comment-column))))


(defun kl1-indent-comment ()
  "この関数は point のある行に関してコメント付けの処理を行う。もしその行にコメ
ントがなかった場合には、関数 kl1-get-comment-column により計算された位置に
コメントを作り、その中に point を移動する。また、もしその行に既にコメントが
ある場合には、そのコメントの位置を同じ関数で計算された位置に移動し、その中
のコメント本文の始まりに point を移動する。"
  (interactive)
  (end-of-line)
  (if (kl1-is-point-in-comment)
      (while (kl1-is-point-in-comment)
	(search-backward "%" nil 'move))
    (insert "% ")
    (backward-char 2))
  (let ((indent (kl1-get-comment-column)) end)
    (setq end (point))
    (skip-chars-backward " \t")
    (delete-region (point) end)
    (indent-to-column indent)
    (skip-chars-forward "%")
    (skip-chars-forward " \t")))


(defun kl1-encomment (start end)
  "この関数は指定されたリージョン内の各行をコメントにする。"
  (interactive "r")
  (save-excursion
    (save-restriction
      (goto-char end)
      (if (bolp) (setq end (1- end)))
      (narrow-to-region start end)
      (kl1-untabify (point-min) (point-max))
      (goto-char (point-min))
      (replace-regexp "^" "% ")
      (kl1-tabify (point-min) (point-max)))))


(defun kl1-decomment (start end)
  "この関数は指定されたリージョン内の各コメント行(kl1-emcomment された行)を
元に戻す。"
  (interactive "r")
  (save-excursion
    (save-restriction
      (goto-char end)
      (if (bolp) (setq end (1- end)))
      (narrow-to-region start end)
      (kl1-untabify (point-min) (point-max))
      (goto-char (point-min))
      (replace-regexp "^% ?\\(.*\\)$" "\\1")
      (kl1-tabify (point-min) (point-max)))))


(defun kl1-untabify (start end)
  "この関数は字下げの桁位置を変えずに、指定されたリージョン内の TAB を複数のス
ペースに展開する。"
  (interactive "r")
  (untabify start end))


(defun kl1-tabify (start end)
  "この関数は字下げの桁位置を変えずに、指定されたリージョン内の複数のスペース
をできるだけ TAB に変換する。ただし、KL1のストリングやアトムの中は変換しない。"
  (interactive "r")
  (save-excursion
    (save-restriction
      (goto-char end)
      (while (kl1-is-point-in-string)
	(re-search-backward "['\"]" nil 'move))
      (setq end (point))
      (goto-char start)
      (while (kl1-is-point-in-string)
	(re-search-forward "['\"]" nil 'move))
      (setq start (point))
      (if (< start end)
	  (progn
	    (narrow-to-region start end)
	    (while (re-search-forward " +[ \t]\\|[\"']" nil t)
	      (let* ((cp (match-beginning 0))
		     (ch (char-after cp)))
		(cond
		 ((= ch ? )
		  (let ((column (current-column))
			(indent-tabs-mode t))
		    (delete-region cp (point))
		    (indent-to column)))
		 ((= ch ?\")
		  (re-search-forward "[\\\"]" nil t)
		  (while (= (char-after (match-beginning 0)) ?\\)
		    (forward-char)
		    (re-search-forward "[\\\"]" nil t)))
		 ((= ch ?\')
		  (re-search-forward "[\\']" nil t)
		  (while (= (char-after (match-beginning 0)) ?\\)
		    (forward-char)
		    (re-search-forward "[\\']" nil t)))))))))))
