	big-Quixoteのインストール及びテスト
---------------------------------------------------------------

参照するマニュアル:

「Quixote導入マニュアル」 		doc/INSTALL_J.tex 
「Quixoteシステム利用マニュアル」	doc/QXTMAN_J.tex


======================================================================
1. Quixote システムの入手と展開
======================================================================
	ftp を binary (image) mode にして、必要なシステム(例えば、
	qxtall.tgz) を入手し、zcat, uncompress, tar などを使って
	展開する。

----------- qxtall.tgz の展開 -----------------
% zcat qxtall.tgz | tar xvf -
-----------------------------------------------

	詳しくは、「Quixote導入マニュアル」3. を参照して下さい。
	
======================================================================
2. Quixoteのコンパイル
======================================================================
	入手したシステムを展開したディレクトリを QXTDIR とすると、
	QXTDIR/server-dist と QXTDIR/client で \verb|make| コマンドを
	実行する。必要があれば、Makefile を変更すること。
	サーバのコンパイルで以下の warning が出るが、問題はない。
		Redundant clause
		Clause deleted: sie_non_delayed/4$0/4
		Redundant clause
		Clause deleted: sie_delayed_solution_lists/4$0/5
	また、サーバのコンパイルには、40分ほど掛かる。
	詳しくは、「Quixote導入マニュアル」4. を参照して下さい。


======================================================================
3. Emacsインタフェースの設定
======================================================================
	以下のように、.cshrc と .emacs を変更する。
	詳しくは、「Quixoteシステム利用マニュアル」2.2を参照のこと。

.cshrc の変更
-----------add to .cshrc -----------------
# Quixote
setenv QXTDIR xxxxx
------------------------------------------
xxxxは、QuixoteのIFSファイルを展開したディレクトリ名を入れる。


.emacsの変更
-----------add to .emacs -----------------
;; Quixote
(setq load-path (cons (concat (expand-file-name
       (substitute-in-file-name "$QXTDIR")) "/client") load-path))
(autoload 'qxt-start
	  "qxt-all" "Start Quixote session to SERVER."
	  t nil)
(setq auto-mode-alist
      (cons '("\\.qxt$" . qxt-mode) auto-mode-alist))
(autoload 'qxt-mode
	  "qxt-mode" "Major mode for Quixote, DOODKRL."
	  t nil)
(setq qxt-inferior-qxt-program "yyyyyy")
------------------------------------------
yyyyy には、<1>で作成した Quixoteサーバのプログラム名をフルパスで (例
えば /usr/local/bin/quixote) 入れる。


======================================================================
4. Emacsインタフェースから Q&A
======================================================================

	詳しくは、example/cider_demoJ.qxt を参照のこと。

--------------- プログラム --------------------------
&program;;
&submodule;;
    usa >- west;;
    uk >- west;;
&rule;;
japan::{cider/[source=soda_pop];;
	drink[name=X]/[trade=no_tax] <= X/[alcohol=non]};;
west::cider/[source=apple, process=ferment];;
uk::cider/[alcohol=yes];;
usa::cider/[alcohol=non];;
&end.


-------------------質問------------------------------
[q1] 
?-japan:drink[name=cider]/[trade=X].

[q2] 
?-japan:drink[name=cider]/[trade=X];;&program;;&rule;;japan::cider/[alcohol=non];;&end.

--------------------------手順-----------------------
(1) <Qmacsの立ちあげ>
    Emacsを立ちあげて
	M-x qxt-start
    とすると、Quixoteサーバが立ち上がり、 *Quixote* ウィンドウができ、
	Quixote server on nil
  	server>
    が表示される。

(2) <データベースの作成>
    上の &program から、&end. の後までをリージョン指定して
	M-x qxt-create-database
    とする。データベース名を聞いてくるので適当な名前(例えば cider)を
    入力する。データベース構築に成功すると、*Quixote* ウィンドウには次の
    ように出力される。
	Quixote server on nil
  	server> ** created : 1.1
	database>


(3) <質問>
    質問の ?-で始まる一行をリージョン指定して M-x qxt-queryとする。

    [q1] の予想される答えは次のようになる。
	database> ** 1 answer exists **
	** Answer 1 **
	 IF japan:cider.alcohol == non THEN
    	X == no_tax
	database>

    [q2] の予想される答えは次のようである。
	database> ** 1 answer exists **
	** Answer 1 **
    	X == no_tax
	database>

(4) <Qmacsの終了>
    M-x qxt-quit を入力する。
    Really Quit? (yes or no) に対しては yes を入力。
-----------------------------------------------------

    ( qxt-quit を実行した時、カーソルが *Quixote* ウインドウに
      戻らないというバグがある。詳しくは、BUGS.j を参照のこと。)

