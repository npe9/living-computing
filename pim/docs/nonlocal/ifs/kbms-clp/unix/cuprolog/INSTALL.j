	(C)1992 Institute for New Generation Computer Technology
	(詳しくは COPYRIGHT を参照して下さい)

ICOT フリーソフトウェア
"Constraint Logic Programming Lanuguage	cu-Prolog"
インストールガイド

1. How to install cu-Prolog.
cu-Prologの実行コードを得るには、src/*.cの全てのファイルをコンパイル、
リンクする。
例えばUNIXの場合は上記のファイルを一つのディレクトリに置き、
 	 cc -o cuprolog *.c [CR]
または添付のmakefileを用いて、
	 make [CR]
とする。
オプティマイズおよびデバッグ用のコンパイルについては src/makefile を参
照のこと。

2. cu-Prologのカスタマイズ法
使用する機種、コンパイラによっては、コンパイル前にinclude.h中の最初の
#define文を書き換える必要がある。

2.1 CPU時間の表示
cu-PrologはCPU時間の計測にシステム依存のライブラリを使用している。
(1) システムに times() ライブラリがある場合
	(times() とはUNIX 4.2/3 BSD のライブラリで プロセスのCPU時間を
	1/60秒単位で返す.)
 	 #define CPUTIME	60
(2) システムの times() ライブラリが1/N秒 単位で時間計測を行なう場合
	 #define CPUTIME	N
(3) Sun-4の場合には clock() ライブラリを用いる。以下のように、CPUTIME
のかわりにSUN4を定義してください。
	 #define SUN4	1
(4) それ以外には、CPUタイムは表示されません。
 	 #define CPUTIME	0

2.2 ヒープサイズ
cu-Prologには以下のデータ領域がある。
システムヒープ:	プログラム節、新述語定義等。
	大きさはSHEAP_SIZE (デフォルトは20000)
ユーザヒープ:	Prolog反駁時の一時的な構造等。 
	大きさはHEAP_SIZE  (デフォルトは600000)
制約ヒープ:	制約・PSTの一時的な構造等。
	大きさはCHEAP_SIZE  (デフォルトは25000)
環境スタック:	Prolog反駁時の環境。
	大きさはESP_SIZE  (デフォルトは500000)
ユーザスタック:	Prolog反駁時のポインタのつけかえ等。
	大きさはUSTACK_SIZE  (デフォルトは10000)
文字列ヒープ: 文字列の格納領域。
	大きさはNAME_SIZE   (デフォルトは50000)

cu-Prolog実行中に、これらヒープ、スタックのオーバーフローが頻繁に起こ
るようならば、起動時の引数で変更することができる。

2.2 組み込み述語の追加
cu-Prolog を拡張して新たに組み込み述語を追加するには
doc/newpred_e.doc (英語)
doc/newpred_j.doc (日本語)
を参照のこと
----------------------------------

以上
(より詳しくは ./doc/cu3man.tex を参照のこと)
