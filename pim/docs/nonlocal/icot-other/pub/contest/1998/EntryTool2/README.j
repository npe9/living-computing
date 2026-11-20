* X Window System で Lights Out を遊ぶプログラム

uudecode して, tar で解凍して下さい。klicon-YYMMDD というディレクトリ
の下に, main.kl1, klic-with-x.kl1, Makefile, README ができます。
(その他, NxN-buttons.kl1, ChangeLog, README.kl1-x とできますが
プログラムの実行には関係しません。)

klicon-YYMMDD のディレクトリ以下に, lo.kl1 というファイル名で課題のプ
ログラムをおいて下さい。

Makefile の INCLUDE_FLAGS, LINK_FLAGS を環境にあわせて適当に変更した後,

	% make

で, lo というプログラムが生成されます。

	% ./lo

で実行できます。
-- 
g新部 裕  <gniib@klic.org>

===========================================================================
以下の環境で動作確認しました。

AITEC:
SunOS 4.1.3
	INCLUDE_FLAGS=
	LINK_FLAGS= -lXaw -lXt -lXmu -lX11 -lXext

MRI:
Solaris 2.5.1
	INCLUDE_FLAGS= -I/usr/openwin/include
	LINK_FLAGS= -lXaw -lXt -lXmu -lX11 -lXext

AKeBoNo 3.9 (GNU C libarary 2.0.94, Linux 2.0.105)
	INCLUDE_FLAGS=-I/usr/X11R6/include
	LINK_FLAGS=-L/usr/X11R6/lib -lXaw -lXt -lXmu -lX11 -lSM -lICE -lXext
===========================================================================
# $Id: README,v 1.2 1998/09/24 10:56:40 gniibe Exp $
