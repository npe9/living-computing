	(C)1992 Institute for New Generation Computer Technology
	(詳しくは COPYRIGHT を参照して下さい)

ICOT フリーソフトウェア
"Constraint Logic Programming Lanuguage	cu-Prolog"

1. はじめに
制約論理型言語cu-Prologは、自然言語処理の単一化文法の特徴である宣言的
な文法記述の実装を目的とした、記号的・組合せ的な制約を解くのに適した言
語である。ここでいう制約とは、変数共有や変数束縛などによる依存関係をい
う。cu-Prologは、従来のCLPの多くが代数方程式・不等式による制約を扱うの
に対して、自然言語処理並びにAI全般への応用に適するプログラム言語である
といえる。

cu-PrologはICOTのPSG-WGにて、JPSG(Japanese Phrase Structre Grammar:日
本語句構造文法)のパーザを実現する目的で考案された。JPSGでは、情報を素
性(ラベル)とその値の対の不定個の並びによる素性構造により格納し、それら
をノードとする句構造によって自然言語の構造を表現する。JPSGのような制約
ベースの単一化文法では、自然言語の文法はすべて制約で宣言的に記述される。
JPSGにおける制約とは、二分木の各ノードにおける素性値の記号的・組合せ的
関係である。

cu-PrologはPrologのユーザ定義述語による項を制約として扱うことができる
ので、JPSGなどの自然言語処理における制約を自然に記述し、そのまま制約と
して実行することが可能である。cu-Prologの制約解消系は、論理プログラム
のunfold/fold変換を基本操作とし、変数共有や束縛などによるヒューリスティッ
クスを加えたところに特徴がある。

cu-Prolog第三版では、制約ベースの単一化文法の記述により適したものとす
るため、データ構造として部分項(Partially Specified Term)をとり入れた。
これにより、素性構造をそのまま扱うことができる。さらに、制約解消系も部
分項の導入とともに自然に拡張を行ない、単一化文法で重要となる選言的素性
構造に対しても対応できるようになった。選言的素性構造の単一化は本来計算
量の大きな問題であり、より実際的なアルゴリズムが研究されている。
cu-Prolog第三版では、それがヒューリスティックスも含めて制約変換という
共通した枠組で解決されている。

2. 実行環境
UNIX 4.2/3BSD上のC言語により実装されている。

3. ファイル構成
INSTALL		README		doc/	
INSTALL.j	README.j	src/	/sample	

doc/
cu3eman.bbl	cu3man.bbl	cup3.index	cup3e.xref
cu3eman.tex	cu3man.tex	cup3.xref

src/
defsysp.c	main.c		print.c		syspred1.c	unify.c
funclist.h	mainsub.c	read.c		syspred2.c	varset.h
globalv.h	makefile	refute.c	tr_split.c
include.h	modular.c	sysp.h		tr_sub.c
jpsgsub.c	new.c		syspdef.h	trans.c

sample/
eisele.p	jpsg.p		jpsg2.p		kasper.p	memap.p

4. インストールに関するコメント
詳しくは INSTSALL.j または doc/cu3eman.texを参照のこと.
全てのCプログラムをコンパイルするだけである。

5. 他機種への移植
cu-Prologは機種依存のライブラリをほとんど使っていないので、他機種ヘの
移植は比較的容易である。
中京大学の白井英俊助教授により、Macintosh版および、80386/486MS-DOSマシ
ン版(DOSエクステンダ DJ's GPP使用)がある。

これらは、
	FTP host name: 	csli.stanford.edu
	Directory:	pub/MacCup. 
or
	ftp.icot.or.jp
	pub/cuprolog
より入手可能である。

6. 参考文献
Hiroshi Tsuda, Hasida Koiti and Sirai Hidetosi,
JPSG Parser on Constraint Logic Programming,
In Proceedings of 4th ACL European Chapter, pp 95--102, 1989.

Hiroshi Tsuda, Hasida Koiti and Sirai Hidetosi,
cu-Prolog and its application to a JPSG parser,
In K.Furukawa,H.Tanaka,and T.Fujisaki(eds.), Logic Programming'89,
pp.134--143, Springer-Verlag, LNAI-485.

Hiroshi Tsuda,
cu-Prolog for Constraint-Based Grammar, proceedings of FGCS'92, 1992.

Hiroshi Tsuda, Hasida Koiti and Sirai Hidetosi,
cu-PrologIII system (cu-Prolog第三版処理系仕様書).
Technical Report ICOT-TM1160, 1992. (In Japanese)

橋田浩一, 白井英俊,
条件付単一化.
コンピュータソフトウェア, vol3 number4, pp.28--38, 1986.(In Japanese)

津田宏, 橋田浩一, 白井英俊,
制約充足としての構文解析 --- 制約論理型言語cu-Prologの応用.
日本ソフトウェア科学会第6回大会論文集, pp.257--260, 1989.(In Japanese)

津田宏,
cu-Prologによる選言的素性構造.
日本ソフトウェア科学会第8回大会論文集, pp.505--508, 1991.(In Japanese)


7.パッチ情報
Oct5-1992: main.c (set global vars)	:thanks to Mr.Horikawa
	   syspred1.c (reaad_pred bug)	:thanks to Dr.Fontanini
	   cu3eman.tex	(delete lingmacros.sty) :thanks to Mr.Utsumi
Oct29-1992: main.c (reset termset log) :thanks to Dr.Sivand Lakmazaheri
Jan10-1996: update jpsg.p : thanks to John Fry


8. Q&A
Q: How to run cu-Prolog on Linux:
A: Add the following lines in the end of src/include.h

#undef is_readable
#undef is_writable
#define is_readable(FP) (!((FP)->_flags & _IO_NO_READS))
#define is_writable(FP) (!((FP)->_flags & _IO_NO_WRITES))

(by Yukihiro Oda  in fj.os.linux, fj.lang.prolog, 16 Dec 1995)
