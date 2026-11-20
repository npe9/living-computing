	                CUI インストール・マニュアル
                                                                		
1. 概要
                                                                
CUI(Character-based User Interface)の実行環境とインストール方法に関して説明して
います。インストールするにあたり、まず「2. 実行環境」を読んで事前確認を行なって
下さい。その後のインストール手順は「3. インストール方法」に記載されています。

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
        (c) KLIC(KLICもIFSプログラムである)
                1.7以上
        (d) 日本語環境
                日本語などの2byteキャラクタを使えるCUIをインストールするには以下
		のgccのライブラリかヘッダファイルのどちらかが必要です。

                ・ ライブラリ
                        libfl.a
                ・ ヘッダファイル
                        euc.h

3. インストール方法

(0) KLICのインストール
    CUIをインストールする前に必ずKLICがインストールされていなければならない。

(1) Makefileの修正
    cui/srcの下にあるMakefileの環境変数を以下に従って修正してください。
   

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

        (ii) ルールや概念名に2byteキャラクタ(日本語など)を使わない場合は、以下の
	     ようにしてください。

                LANG = english

(2) makeの実行
    カレント・ディレクトリをcui/srcにして以下を実行してください。
    プログラムがコンパイルされ、cui/binにCUIやトランスレータの実行ファイルが作成
    されます。


        make 

(3) 環境変数pathの修正
    CUIやトランスレータでは、ルールやゴールを変換する際に変換プログラムを呼び出
    しています。

    この変換プログラムはmakeが実行されるとcui/binに作成されます。

    そのため、この変換プログラムの実行ファイルがどこにあるかを.cshrcなどで定義さ
    れている環境変数pathに設定しておかなければいけません。

    例えばこの変換プログラムが~/cui/binにある場合、.cshrcのpathにこのパスを以下
    のように追加します。

        修正前:
                set path=(~/)

        修正後:
                set path=(~/ ~/cui/bin)

4.動作テスト

簡単な動作テストの例を以下に示す。

"+"は上の文字がユーザの入力であることを表す。

また、この実行はカレント・ディレクトリが"cui/data"の時のものである。

!cd cui/data
 +++++++++++
!cui
 +++
HELIC-II>run cntrct.c
	 ++++++++++++

<<<<<省略>>>>>

ok
HELIC-II>start
	 +++++
History : start

<<<<<省略>>>>>

Status : defendant finish p0
Status : defendant finished p0
ok
HELIC-II>quit
         ++++

