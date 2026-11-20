=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
%									%
%	Quixote を用いた代謝反応知識ベース				%
%									%
%		1995.3 							%
%									%
%	(C)1995 Institute for New Generation Computer Technology	%
%	配布、その他はCOPYRIGHTファイルを参照して下さい。		%
=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

【概要】細胞内の反応関係や活性化関係を視覚化してユーザに提示する
	知識ベースシステム

【構成】知識ベース部………………細胞内信号伝達経路情報
	インタフェース部…………経路の表示と質問応答
	外部ＤＢ検索部……………PIRのアクセス支援

【特徴】

１．知識ベース部

Quixote の演繹オブジェクト指向データベース言語の特徴により、生体内に
起こる素過程を、オブジェクト指向の枠組を用いて体系的に知識ベースに表
現でき、またその全体像は素過程の追加や詳細化に応じて随時に演繹機能を
使って構成できるようになっている。研究の発展に伴う知識追加や詳細化に
容易に対応して知識ベースを最新化できる。

２．インタフェース部

反応関係／活性化関係などの表示を行なうグラフィックユーザインタフェー
ス。ユーザは、複数の詳細度で関係をみることができる。経路の検索は発端
となる信号をキーとし、質問言語はQuixote を用いる。

３．外部ＤＢ検索部

PIR やProSite など公共データベースの参照をするためのインタフェース。
参照ファイルを独自に持ち、そこでまず検索する。なかった項目については、
PIRのフラットファイルを圧縮した状態のままキーワードサーチし、結果を
暫定的ファイルに出力する。そこからユーザは適当と思う場所を参照ファイルに
編集して登録し、次回以後の利用に備える。

【実行環境】

Machine     : UNIXワークステーション(IRIS,Sparc10で動作確認済)
Environment : UNIX, X Window(Motif)
Language    : C, C++, yacc/lex
Source Code : 190KB

【ファイル】

Bio-Reaction KB (pathway/)
	motifhead.c	motifhead.h 
	TextWidget.c	TextWidget.h 
	callbacks.c
	newclass.c	newclass.h 
	bind.c		bind.h
	io.c 
	allow.c 
	questionBox.c
	wprintf.c 
	qxoteParse.c	qxoteParse.l	qxoteParse.y 
	main.c 
	Makefile

micro-Quixote Version 8 (pathway/mq-008/)

BUGS            COPYRIGHT.j     INSTALL         src/
COPYRIGHT       GNU/            README

GNU:
COPYING         MANIFEST        obstack.c       parse_t.c       quixote.el
COPYING.LIB     alloca.c        obstack.h       parse_t.h

src:
ChangeLog       cs-dot.c        ext.c           obstack.c@      subrel.c
MANIFEST        cs-ext.c        extern.h        obstack.h@      subsump.c
Makefile-dist   cs-sub.c        internal.c      option.c        syntax.ref
alloca.c@       cs.c            internal.h      parse.y         syntax.ref.j
api.c           dot.c           lex.c           parse_t.c@      tree.c
api_example.c   emit.c          lookup.c        parse_t.h@      tree.h
atom.c          emit.h          mq.1            print.c         unify.c
attr.c          error.c         mq.c            quixote.el@     version.c
commands.c      exec.c          mq.h            rule.c

【使用方法】

１．インストールと起動

	INSTALL.j を参照して下さい。

２．検索

	DOC.j を参照して下さい。

３．知識の作成や追加

	DOC.j を参照して下さい。
