並列反復改善法によるマルチプルアライメントプログラム（KL1,C）

1) プログラムの実行環境

Machine     : UNIXワークステーション(IRIS,Sparc10で動作確認済)
Environment : UNIX, X Window(Motif)
Language    : C, C++, yacc/lex
Source Code : 190KB


2) インストール方法

1. gunzip で圧縮を解く。

2. tar xvf pathway.tarを実行。以下のようなファイルが展開される。

motifhead.c motifhead.h TextWidget.c TextWidget.h callbacks.c
newclass.c newclass.h bind.c bind.h io.c allow.c questionBox.c
wprintf.c qxoteParse.c qxoteParse.l qxoteParse.y main.c Makefile
mq-008/

3. microQuixoteをINSTALLする。詳しくはmicroQuixoteのREADMEを参照して下
さい。

4. pathwayというディレクトリ内でmakeを実行。


3) プログラムの使用説明

別途README.jを参照してください。
