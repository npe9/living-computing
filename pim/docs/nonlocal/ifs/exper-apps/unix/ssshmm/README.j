=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
%									%
%	隠れマルコフモデルの逐次状態分割法による蛋白質配列の分類	%
%									%
%		1995.3 							%
%									%
%	(C)1995 Institute for New Generation Computer Technology	%
%	配布、その他はCOPYRIGHTファイルを参照して下さい。		%
=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

【概要】隠れマルコフモデルのネットワーク構造を逐次状態分割法を用いて
	自動生成し、タンパク質のアミノ酸配列による分類を試みる。

【構成】ＨＭＭ学習部………………データとＨＭネットからＨＭＭを学習
	ＨＭネット生成部…………状態分割によりＨＭネットを成長させる
	ユーザインタフェース部…ＨＭネット、ＨＭＭをユーザに表示

【特徴】

１．ＨＭＭ学習部

学習には Viterbi法を用いている。アミノ酸配列のデータの形式は
マルチプルアライメントツールと共通にしてある。
学習の終了の判定は、出力分布の変化の総量が一定値を下回った時としている。

２．ＨＭネット生成部

ネットの成長に、逐次状態分割法を用いている。
終了判定は、分割するべき状態を通るタンパク質が１本となった時としている。

３．ユーザインタフェース部

ＨＭネットの形状の表示の最適化を自動的に行なっている。
アミノ酸配列に特化した出力分布表示を持つ。アミノ酸の表示色は
マルチプルアライメントツールと共通にしてある。

【実行環境】

Machine     : UNIXワークステーション(Sparc10で動作確認済)
Environment : UNIX, X Window(Motif)
Language    : C
Source Code : 100 kbytes

【ファイル】

DHMM.res	Ｘウィンドウ用リソースファイル
Makefile	make 記述ファイル

defs.h          各種設定値(#define)
struct.h	共通データ構造体定義
e_struct.h      上記 extern 版

getsample.c	データ入力
gethmn.c        初期隠れマルコフネットの入力
inithmn.c	隠れマルコフモデルの初期化
watchhmn.c	隠れマルコフネットの諸元調査

disc_viterbi.c  データのViterbi学習
nodesplit.c	状態分割

hmmdisplay.c    隠れマルコフネットの表示
outputdisplay.c	出力分布表示

init.c          全体の初期設定（メイン部）
logcal.c        対数計算用ツール
mklogtbl.c	対数テーブル作成

lp1tbl.c        対数テーブル（自動作成）
lm1tbl.c        対数テーブル（自動作成）

hmnbackbone.c   隠れマルコフネットの初期値の生成支援

hmnet/		隠れマルコフネットの例
hmn.big		hmn.new		hmn.old		hmn.zen

samples/	サンプルの例
sample.real     sample2         sample3         sample4         sampleAA

【使用方法】

(1) setenv XENVIRONMENT DHMM.res

(2) ./DHMM

【実装方法】

(1) Makefile 内の SRC にソースファイルのディレクトリを設定する。

(2) make で本体が実装される。

(3) make HmnALC で隠れマルコフネットの初期値の生成支援ツールが実装される。

なお、

(4) make clean で本体に関連する部分の *.o と実行形式が消去される。

(5) make allclean で全ての *.o 、実行形式、自動生成された対数テーブルが
    消去される。
