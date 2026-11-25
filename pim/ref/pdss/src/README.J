ＵＮＩＸ上のＫＬ１プログラミング環境 --- ＰＤＳＳ

ＰＤＳＳは PIMOS Development Support System の略で、その名前が示す通り、
PIMOSを開発するために使用したKL1システムです。PDSSは通常のBSD系のUNIX
マシン上で動作し、Multi-PSI上のKL1システムとは、実装方式や実行速度の違
いをのぞいては、かなりの部分でコンパチビリティが確保されています。さら
に、PDSSでは GNU Emacs ライブラリを用意しており、KL1ソースプログラムの
編集の支援や複数のemacsバッファを通して会話的にPDSSを使うことができる
ようになっています。従って、PDSSは一般のKL1プログラムを開発するために
も使い易く、有用になっています。

構成:
 - KL1-B(バイトコード)のインタープリタ。Cで記述。
 - KL1からKL1-Bへのコンパイラ。 KL1とSICStus Prologで記述したもの2種。
 - ランタイムサポートルーチン(コマンドインタープリタやI/O)。 KL1で記述。
 - GNU Emacs のライブラリ --- KL1ソースプログラムを編集するときに使用す
   る KL1-mode と、複数のEmacsバッファを使いながらPDSSを会話的に実行す
   るための PDSS-mode がある.

インストール環境:
 - PDSSはUNIXシステム(BSD系)の上で動作します。
   ICOTでは、SUN-3, SUN-4 および Sequent Symmetry 上で使用しています。
 - PDSSの全体をインストールするためには、
   約20MBのディスクスペースが必要です。
 - KL1コンパイラのうち一方は SICStus Prolog で記述されています。
   これはオプショナルな部分ですが、この版のほうが良いコードが生成されます。
 - PDSSは GNU Emacs とともに使用するべきです。とても使い易くなります。

(C) Copyright 1988--1992 Institute for New Generation Computer Technology.
    著作権に関する詳細は "COPYRIGHT" ファイルを参照して下さい。
