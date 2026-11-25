/*************************************************************************
*  PDSS (PIMOS Development Support System)  Version 2.52		 *
*  (C) Copyright 1988,1989,1990,1992.					 *
*  Institute for New Generation Computer Technology (ICOT), Japan.	 *
*  Read "../COPYRIGHT" for detailed information.			 *
**************************************************************************

  このファイルに指定された名前のマクロを定義すると、統計情報を集計する為の
プローブを処理系に挿入する事ができます。プローブには、秒単位、リダクション
単位、KL1B命令単位で情報を収集するものがあります。通常は各マクロに情報収集
の為に実行すべき処理(関数呼び出し等)を定義します。なお、情報収集の為に関数
を定義した場合には Makefile を変更して、その関数をリンクする必要があります。

(1) STATISTICS_START
    処理系が実行を始めた時に実行すべき処理。

(2) STATISTICS_END
    処理系が実行を終了した時に実行すべき処理。

(3) STATISTICS_SECOND
    1秒ごとに実行する処理。アラームクロックによる割り込みを利用しています。

(4) STATISTICS_REDUCTION
    1リダクションごとに実行する処理。

(5) STATISTICS_INSTRUCTION
    KL1Bの1命令ごとに実行する処理。

*************************************************************************/

/**
以下はサンプルで、一定時間(10秒)ごとに一括GCを起動して、ヒープの使用状況を
調べるものです。
**
EXTERN int __count;
#define STATISTICS_START  __count=0
#define STATISTICS_SECOND if(++__count==10){ SetHeapGcFlag(); __count=0; }
**/
