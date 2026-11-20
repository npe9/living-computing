
	   KLIJava: KL1 to Java Compiler based on KLIC 3.002

			    981209-SNAPSHOT

  (C)1993, 1994, 1995 Institute for New Generation Computer Technology
	       (Read COPYRIGHT for detailed information.)

     (C)1996, 1997 Japan Information Processing Development Center
	   (Read COPYRIGHT-JIPDEC for detailed information.)

		  Copyright(C) 1998 Satoshi KURAMOCHI



・概要

KLIC-3.002 のコンパイラを改造して Java のコードを出力するコンパイラを作
成しました。ランタイムライブラリは Java で書き直してあります。

とりあえずコンパイラのセルフコンパイルを目標に実装を進めていますが、まだ
デバッグが終了していません。テストプログラムの中にも実行時エラーになるも
のがいくつか残っています。

・コンパイラのソースとサンプルは、以下の場所に置いてあります。

    compiler/		コンパイラ
    kl1/lang/		ランタイムライブラリ
    test/		テストプログラム

・動作環境

    コンパイラ：        klic-3.002 の動作する環境
    出力プログラム：    JDK 1.1 以上

・現在、動作を確認しているプログラム

  append.kl1, cmac.kl1, fact.kl1, fiblazy.kl1, hanoi.kl1, iotest.kl1,
  kkqueen.kl1, life.kl1, mastermind.kl1, pascal.kl1, pp.kl1, primes.kl1,
  primesp.kl1, prio.kl1, qlay.kl1, qsort.kl1

・まだ実装されていない機能

  - 組込み述語の一部（UNIX インタフェース, タイマ, postmortem など）
  - ジェネリックオブジェクト（I/O など）
  - Javaとのインタフェース（GUI、アプレット）
  - トレーサ
  - 分散処理
  など

・新機能

  - インライン Java :-)

・コンパイル手順

  コンパイラの作成
  % cd compiler
  % make

  ランタイムライブラリの作成
  % cd ../kl1/lang
  % make symlinks
  % make

・テストプログラムを実行するには、以下のようにします。

  % setenv CLASSPATH $CLASSPATH:トップディレクトリ
  % ./compiler/kl1cmp foo.java
  % cp foo.java Module_main.java
  % javac Module_main.java
  % java Module_main

・ベンチマーク結果（参考）

  compiler             KLIC      KLIJava (sec)
  -----------------------------------------------------
  primes(10000)        0.37      15.32        (x 41.40)
  kkqueen(10)          0.33      15.34        (x 46.48)
  life(120,38,38,4,4)  1.22      22.06        (x 18.08)
  mastermind(3,3)      0.77      27.34        (x 35.51)

  MMX-Pentium 266MHz, 64MB, Linux
    KLIJava: JDK 1.1.5, w/o JIT
             -ms32m -mx32m -noasyncgc -noclassgc -noverify
    KLIC: 3.002, gcc -O2

・配布

最新版の公開は、

  http://www.ueda.info.waseda.ac.jp/~satoshi/klijava/

で行なっています。

御意見、御感想などはお気軽に

  satoshi@ueda.info.waseda.ac.jp

までお寄せ下さい。

・参考文献

  [1] 関田 大吾. Inside KLIC Version 1.0, 1998

  [2] jProlog  <http://www.cs.kuleuven.ac.be/~bmd/PrologInJava/>

--
倉持 聡 / Satoshi Kuramochi 
satoshi@ueda.info.waseda.ac.jp
http://www.ueda.info.waseda.ac.jp/~satoshi/index-j.html
