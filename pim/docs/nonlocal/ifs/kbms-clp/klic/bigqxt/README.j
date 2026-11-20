
		ICOT Free Software

		知識表現言語 : Quixote

	       (KLIC 版,  "big-Quixote")		

					March, 1995
------------------------------------------------------

1. はじめに
 Quixote は演繹オブジェクト指向データベース(Deductive Object-Oriented
Database:DOOD)と、包摂関係に基づいた制約論理プログラミング(CLP)の
ハイブリッド言語として設計されている。Quixote の新しい機能は、
オブジェクト識別性と属性継承といったオブジェクト指向の概念と、
大きな知識ベースを分類するモジュールの概念を結びつけていることで
ある。さらに加えて、その論理的推論システムは仮説推論とアブダクション
による推論を行なうことができるように拡張してある。そのような特徴は、
法的推論、生物データベース、自然言語理解といった応用において重要な
役割を果たしている。

IFS (ICOT Free Software)には二種類の Quixote ( "big-Quixote" と
"micro-Quixote" )が登録されている。"big-Quixote" は KLIC (KL1)
を用いて開発され、クライアント・サーバ形式で実装されている。
"micro-Quixote" は Quixote の主要機能のみを C を用いて開発した
小さなシステムである。

このファイルは、"big-Quixote" のためのものである。


2. 必要とする環境
オペレーティングシステムとしては通常の UNIX で動作することを念頭において
作成している。

SunOS 4.1.3 の環境では、"big-Quixote" システムは Disk を 10MB 程度消費する。
コンパイルを行なうためには 30MB 程度の Disk が必要である。"big-Quixote"
システムのインストールには root の権限は必要ない。

"big-Quixote" システムの導入と実行に必須であるライブラリ/システムを以下に示す。
・ BSD ソケットライブラリ
・ KLIC システム
   KLIC は ICOT の IFS より入手可能である。
・ Perl
   Perl は prep.ai.mit.edu のディレクトリ ``/pub/gnu''  から入手できる。
・ GNU Emacs 系統の Editor (GNU Emacs, Mule など)
   GNU Emacs は prep.ai.mit.edu のディレクトリ ``/pub/gnu''  から
   Mule は etlport.etl.go.jp のディレクトリ ``/pub/mule''  から
   入手できる。


3. ファイル:
(展開前の状態)
$QXTDIR/
	BUGS			バグについて (英語)
	BUGS.j			      〃     (日本語)
	COPYRIGHT		IFS copyright (英語)
	COPYRIGHT.j		      〃      (日本語)
	README			README ファイル (英語)
	README.j		      〃	(日本語)
	INSTALL			インストールについて (英語)
	INSTALL.j		      〃	     (日本語)
	qxtall.tgz	全ての Quixote 関係プログラム
			(=> BUGS*, COPYRIGHT*, INSTALL*, README*,
			    client/, doc/, example/, server-dist/)
	qxtserver.tgz	Quixote サーバ プログラム
			(=> server-dist/)
	qxtclient.tgz	Quixote クライアント プログラム
			(=> client/)
	qxtdoc.tgz	ドキュメント
			(=> doc/, example/)

	(server-org.tgz	Quixote オリジナル サーバ
				プログラム ; OPTIONAL) 

始めて、Quixote システムを入手する場合は、qxtall.tgz を持っていくとよい。
サーバーのみ、クライアントのみ、ドキュメントのみ入手する場合は、
それぞれ、qxtserver.tgz、qxtclient.tgz、qxtdoc.tgz を持っていくこと。


"qxtserver.tgz", "qxtclient.tgz", "qxtdoc.tgz" を展開すると
それぞれ以下のようになる。
"qxtall.tgz" を展開すると以下の全てが得られる。
-----
$QXTDIR/
	server-dist/		Quixote サーバ ソース
		QC-cs/		制約解消系
		QC-sd/		解記述マネージャ
		QD-dp/		ディスパッチャー
		QD-lm/		束マネージャ
		QD-pc/		プログラム変換
		QD-qd2/		Quixote データ マネージャ
		QD-rt/		ルール変換
		QD-spm/		スパイ マネージャ
		QD-um/		更新マネージャ
		QE-ip/		処理系
		QS-pm/		永続マネージャ
		QF-pm2/		      〃
		QS-henkan/	項変換
		QS-kl1IF/	KL1 I/F
		QS-server/	Quixote サーバ
		QZ-tools/	misc. tools
-----
$QXTDIR/
	client/			Quixote クライアント ソース (Emacs I/F)
				*.el(c)
-----
$QXTDIR/
	doc/			Tex 形式のドキュメント
	example/		例題
		QMI/		Mosaic を用いた Quixote ユーザ I/F (サンプル)
-----

"server-original.tgz" は、Quixote サーバのオリジナル版で、
$QXTDIR/server に展開される。$QXTDIR/server-dist のファイルで
読み難いものは、$QXTDIR/server のファイルを参照すること。

4. インストール
インストールについては、以下のファイルを参照のこと。
	INSTALL(.J)
	doc/INSTALL_E.tex, INSTALL_J.tex 
	doc/QXTMAN_E.tex, QXTMAN_J.tex 

