			DRSインストール・マニュアル
										
1. 概要
										
DRS(Defeasible Reasoning System)の実行環境とインストール方法について説明していま
す。

インストールするにあたり、まず「2. 実行環境」を読んで事前確認を行なって下さい。
その後のインストール手順は「3. インストール方法」に記載されています。

2. 実行環境

以下の環境でインストールや動作することは確認をしました。

(1) ハード
	(a) マシン
		Sun SparcStation 10 
	(b) メモリ
		32MB以上
	(c) ハードディスク
		40MB

(2) ソフト
	(a) OS
		SunOS 4.1.3
	(b) Cコンパイラ 
		gcc-2.6.2
	(c) KLIC (KLICもIFSプログラムである)
		1.7以上
	(d) 日本語環境
		日本語などの2byteキャラクタを使えるDRSをインストールするには以下
		のgccのライブラリかヘッダファイルのどちらかが必要です。

		・ ライブラリ
			libfl.a
		・ ヘッダファイル
			euc.h

3. インストール方法

(0) KLICのインストール
    DRSをインストールする前に必ずKLICがインストールされていなければならない。

(1) Makefileの修正
    drs/srcの下にあるMakefileの環境変数を以下に従って修正してください。

 (a) Flexの修正

	(i) flex Library(libfl.a)が存在する場合は以下のようにしてください。

		Flex = exist

	(ii) flex Library(libfl.a)が存在しない場合は以下のようにしてください。

		Flex = nothing

 (b) LANGの修正
     flex Library(libfl.a)が存在する場合はこの修正は必要ありません。

	(i) ルールや概念名に2byteキャラクタ(日本語など)を使いたい場合は、以下の
	    ようにしてください。

		LANG = japanese

	    この場合は、以下のgccのヘッダファイルがmake実行時に必要になることを
	    注意して下さい。	    

		euc.h

	(ii) ルールや概念名に2byteキャラクタ(日本語など)を使わない場合は、以下
	     のようにしてください。

		LANG = english

(2) makeの実行
    カレント・ディレクトリをdrs/srcにして以下を実行してください。
    プログラムがコンパイルされ、drs/binにDRSの実行ファイルが作成されます。

        make 

(3) 環境変数pathの修正
    DRSは、ルールやゴールを変換する際に変換プログラムを呼び出しています。
    この変換プログラムはmakeが実行されるとdrs/binに作成されます。
    そのため、この変換プログラムの実行ファイルがどこにあるかを.cshrcなどで定義さ
    れている環境変数pathに設定しておかなければいけません。

    例えばこの変換プログラムが~/drs/binにある場合、.cshrcのpathにこのパスを以下
    のように追加します。

	修正前:
		set path=(~/)

	修正後:
		set path=(~/ ~/drs/bin)

4.動作テスト

簡単な動作テストの例を以下に示す。
"+"は上の文字がユーザの入力であることを表す。
また、この実行はカレント・ディレクトリが"drs/data"の時のものである。

! cd drs/data
  +++++++++++
! drs
  +++
DRS>run cntrct.c
    ++++++++++++
ok
DRS>ab
    ++
Goal : canWithdraw(agent=father,objec
0 :  p >:0!:3<:0
Please input number > 0
		      +
ArgJudge : plausible
RuleInfo({RuleName,TopRuleRel}) : {r11,nil}
0  :             r11:canWithdraw(agent=father,objec
1  :              r1:contract(agent=tarou[age=>{19}
2  :               act4:buy(agent=tarou[age=>{19}],imp
3  :               act5:loan(agent=tarou[age=>{19}],ob
4  :               act6:causality(source=buy(agent=tar
5  :    !J (2)    r6:-valid(a_object=contract(agent
6  :               act5:loan(agent=tarou[age=>{19}],ob
7  :               r1:contract(agent=tarou[age=>{19}
8  :                act4:buy(agent=tarou[age=>{19}],imp
9  :                act5:loan(agent=tarou[age=>{19}],ob
10 :                act6:causality(source=buy(agent=tar
11 :    !J (1)     r2:needAllow(agent=father,a_objec
12 :                r1:contract(agent=tarou[age=>{19}
13 :                 act4:buy(agent=tarou[age=>{19}],imp
14 :                 act5:loan(agent=tarou[age=>{19}],ob
15 :                 act6:causality(source=buy(agent=tar
16 :                act0:isFather(a_object=father,basis
17 :               act10:-allow(agent=father,object=loa
18 :               act0:isFather(a_object=father,basis
19 :              act0:isFather(a_object=father,basis
UseCommand:  : [end,show,set]
>end
 +++
ok
DRS>quit
    ++++


