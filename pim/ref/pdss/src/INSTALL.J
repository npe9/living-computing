                                                                1992年5月25日
                                                               ICOT 第1研究室
                    PDSS (V2.52.20) インストールの手引き
                   --------------------------------------

  PDSSとは "PIMOS Development Support System" の略であり、その名のとおりPIMOS
の開発環境として作成された(マルチプロセッサでない)汎用計算機上で動作するKL1シ
ステムです。 PDSSはコンパイラ、バイトコードインタープリタ、および、MicroPIMOS
(コマンドインタープリタと入出力ライブラリ等)から構成されている。また、2つの 
Emacs Lisp ライブラリ、KL1-mode と PDSS-mode も提供している。KL1-mode はKL1の
ソースコードを編集するためのメジャーモードであり、PDSS-mode は Emacs の複数の
バッファを通してPDSSを使用するためのメジャーモードです。ICOTでは、PDSSをSUN-3,
SUN-4および Sequent Symmetry 上で使用しており、BSD 4.2, 4.3 UNIX を使用したシ
ステムには簡単にインストールできるようになっている。


 1. PDSSのテープの内容
-----------------------

  PDSSのテープには以下のようなファイルが含まれている。これらの全てを読み込む
ためには8MB、メイクするためには約13MBのファイルスペースが必要です。

 ---------------------------------------------------------------------------
     名前                       内    容                             サイズ
 ---------------------------------------------------------------------------
   Makefile     Makefile                                                  2
   pdsscmp*     KL1ソースをコンパイルするためのシェルスクリプト           6
   emulator/    KL1-Bバイトコードインタープリタ = KL1抽象機械           970
   runtime/     KL1で記述したランタイムライブラリ                       147
   mpimos/      Micro PIMOS = コマンドインタープリタと入出力ライブラリ 1582
   compiler/    KL1で記述したKL1コンパイラ                             1424
   macro/       KL1マクロの定義ファイル                                  13
 + debug_utl/   KL1ソースをテストするツールプログラム                   303
 + pimos_utl/   PIMOSグループが作成したライブラリプログラム             773
 + compiler_pl/ SICStus Prolog で記述したKL1コンパイラ                  368
 + emacs/       Emacs Lisp ライブラリ (KL1-mode と PDSS-mode)            88
 + test/        KL1テストプログラム                                     551
 + sample/      KL1サンプルプログラム                                   133
 ---------------------------------------------------------------------------
 ↑この ``+'' 印はオプションのモジュールを意味する。                    KB


 2. テープからのリストア方法
-----------------------------

  PDSSのテープはtarフォーマットで書き込まれているので、リストアするためには
以下のようなコマンドを実行すればよい。この結果、現在のカレントディレクトリに
全てのファイルが読み込まれる。

        % tar xf /dev/rst0
                 ^^^^^^^^^ これはテープドライブのデバイス名。この名前は機種
                           とメディアに依存するので適当なものを指定する必要
                           がある。もし分からない場合には、インストール先の
                           マシンのマニュアルを調べて下さい。

  テープからのリストアが完了したら、必ず以下の手続きを行なって下さい。もし
SICStus Prolog を持っていない場合には、"compiler_pl" ディレクトリをrenameする
かremoveして下さい。もし GNU Emacs を持っていない場合には、"emacs"ディレクト
リをrenameするかremoveして下さい。その他、オプションモジュールの中で必要のな
いものがあれば、それをrenameするかremoveして下さい。


 3. Makefile と configuration-file の編集
------------------------------------------

  メイクを行なう前に、以下のようなマシン依存やサイト依存の部分を含んだファイ
ルを編集する必要がある。

  ・Makefile
    変数BINDIRの値を自分のサイトに適したものに変更する。これは、"make install"
    を行なった時のターゲットとして使われる。

  ・emulator/Makefile
    変数BINDIRの値を自分のサイトに適したものに変更する。これは、"make install"
    を行なった時のターゲットとして使われる。
    変数CFLAGSの値を必要であれば適当なものに変更する。

  ・emulator/config.h
    ファイル内のコメントに従って各定義を変更する必要がある。パス名の定義以外は
    変えなくても大丈夫です。

  ・compiler_pl/libdir.pl  (もしPrologで書かれたクロスコンパイラを使うなら)
    パス名を自分のサイトに適したものに変更する。

  ・emacs/Makefile  (もし Emacs Lisp ライブラリを使うなら)
    変数LIBDIRの値を自分のサイトに適したものに変更する。これは、"make install"
    を行なった時のターゲットとして使われる。
    変数EMACSの値を自分のサイトに適したものに変更する。これは、Emacs Lisp ライ
    ブラリをコンパイルするために使われる。

  ・emacs/pdss-init.el  (もし Emacs Lisp ライブラリを使うなら)
    変数 pdss-directory-name の値を自分のサイトに適したものに変更する。これは
    PDSSのトップレベルのディレクトリのパス名にする。

  ・pdsscmp
    最初の5行で定義しているパス名を変更する。


 4. メイク
-----------

  メイクは、もし KLB_PACKED_CODE と KLB_4BYTE_RED_ADDR の値を変更していない場
合には、以下のコマンドをPDSSのトップレベルのディレクトリで実行して下さい。

        % make

  もしこれらの値を変更した場合には、以下のコマンドを実行して下さい。この場合
には、全てのKL1-Bコードのファイルを再アセンブルします。

        % make reassm

  上記のメイクが成功した場合には、以下のコマンドによりPDSSを公共ディレクトリに
コピーし、一般のユーザーから使えるようにします。

        % make install

  最後に(もし必要であれば)作業用に作ったファイルを削除します。

        % make clean

  付録-I にICOTでメイクを行った時のログがあるので、それを参考にして下さい。
その時の環境は SUN SparcStation-2 (SunOS 4.1.1) です。


 5. Emacs ライブラリ
---------------------

  PDSSは2つの Emacs Lisp ライブラリ、KL1-mode と PDSS-mode を提供している。
KL1-mode はKL1のソースコードを編集するためのメジャーモードであり、PDSS-mode 
はEmacsの複数のバッファを通してPDSSを使用するためのメジャーモードです。これら
のライブラリを使いたい場合には、ユーザーのホームディレクトリにある ".emacs" 
ファイルに以下のコマンドを挿入して下さい。また、全ユーザーが使えるようにする
場合には同じものを "site-init.el" ファイルに挿入して下さい。

        (load "pdss-init")

  なお、ICOT で使用している GNU-Emacs は "GNU Emacs 18.55.28" をベースにした
"Nemacs version 3.3.2" です。 他の版を使っている場合には、変更が必要かも知れ
ません。


 6. BSD UNIX 以外に移植する場合
--------------------------------

  PDSSは BSD UNIX 上で動作することを目的に書かれているので、System-V等のUNIX 
に移植する場合には多くの変更を必要とします。少なくとも以下の部分に変更が必要
になります。

  ・emulator/pdss.c
    signal(), sigblock(), sigsetmask() および kill() がシグナルハンドラで使わ
    れている。
    getrusage() が CPU Time を調べる為に使われている。

  ・emulator/io.c
    signal(), sigblock(), sigmask() および sigsetmask()  がシグナルハンドラで
    使われている。
    ioctl() および fcntl() がI/Oデバイスの制御で使われている。

  ・emulator/blt_system.c
    getrusage() が CPU Time を調べる為に使われている。

  ・emulator/blt_iodev.c
    opendir(), readdir() および closedir() がディレクトリのリスティングのため
    に使われている。
    unlink() がファイルの削除のために使われている。
    re_comp() および re_exec() が正規表現の処理の為に使われている。

  ・emulator/timer.c
    signal(), sigblock(), sigmask() および sigsetmask()  がシグナルハンドラ
    で使われている。
    alarm() がタイマー割り込みのために使われている。
    time() が現在時刻を取り出すために使われている。

 付録-I  ICOTで行なったメイクのログ
------------------------------------

  以下は ICOT の SUN SS-2 (SunOS 4.1.1) 上でメイクを行った時のログです。

% 
% cd /usr/local/src/pdss
% ls -F
LOG		compiler/	doc.j/		mpimos/		sample/
Makefile	compiler_pl/	emacs/		pdsscmp*	test/
README		debug_utl/	emulator/	pimos_utl/
README.J	doc.e/		macro/		runtime/
% make
cd emulator	; make all
cc -O  -target sun4 -c  pdss.c
cc -O  -target sun4 -c  option.c
cc -O  -target sun4 -c  emulate.c
cc -O  -target sun4 -c  blt_basic.c
cc -O  -target sun4 -c  blt_float.c
cc -O  -target sun4 -c  blt_shoen.c
cc -O  -target sun4 -c  blt_iodev.c
cc -O  -target sun4 -c  blt_code.c
cc -O  -target sun4 -c  blt_system.c
cc -O  -target sun4 -c  deref.c
cc -O  -target sun4 -c  passive.c
cc -O  -target sun4 -c  unify.c
cc -O  -target sun4 -c  goal.c
cc -O  -target sun4 -c  shoen.c
cc -O  -target sun4 -c  exception.c
cc -O  -target sun4 -c  memory.c
cc -O  -target sun4 -c  atom.c
cc -O  -target sun4 -c  module.c
cc -O  -target sun4 -c  dcode.c
cc -O  -target sun4 -c  float.c
cc -O  -target sun4 -c  string.c
cc -O  -target sun4 -c  gc.c
cc -O  -target sun4 -c  gc_ctrl.c
cc -O  -target sun4 -c  gc_cell.c
cc -O  -target sun4 -c  gc_code.c
cc -O  -target sun4 -c  gc_dead.c
cc -O  -target sun4 -c  mrbgc.c
cc -O  -target sun4 -c  instr.c
cc -O  -target sun4 -c  invassm.c
cc -O  -target sun4 -c  assemble.c
cc -O  -target sun4 -c  saveload.c
Routine _write_predicate too big:                   ## スワップ領域不足が発生。
use lower optimization level or increase swap space ## (ICOTのSUNはそんなに巨大
getpage: Not enough memory                          ##  なスワップを持ってない)
compiler(iropt) error:	getpage: out of memory 
*** Error code 1
make: Fatal error: Command failed for target `saveload.o'
Current working directory /usr/local/src/pdss/emulator
*** Error code 1
make: Fatal error: Command failed for target `quick'
% cd emulator                                       ## 手動で再コンパイル。
% cc -target sun4 -c  saveload.c
% cd ..
% make                                              ## 再びmakeを行なう。
cd emulator	; make all
cc -O  -target sun4 -c  native.c
cc -O  -target sun4 -c  tracer.c
cc -O  -target sun4 -c  print.c
cc -O  -target sun4 -c  io.c
cc -O  -target sun4 -c  iosub.c
cc -O  -target sun4 -c  timer.c
cc -O  -target sun4 -c  path.c
cc -O  -target sun4 -c  ctype.c
cc -O -o pdss.x -D"MAKEDATE=\"`date`\"" version.c pdss.o option.o emulate.o blt
_basic.o blt_float.o blt_shoen.o blt_iodev.o blt_code.o blt_system.o deref.o pa
ssive.o unify.o goal.o shoen.o exception.o memory.o atom.o module.o dcode.o flo
at.o string.o gc.o gc_ctrl.o gc_cell.o gc_code.o gc_dead.o mrbgc.o instr.o inva
ssm.o assemble.o saveload.o native.o tracer.o print.o io.o iosub.o timer.o path
.o ctype.o -lm
mv -f pdss.x pdss
rm -f version.o
cc -O  -target sun4 -c  pdssasm.c
cc -O -o pdssasm.x -D"MAKEDATE=\"`date`\"" version.c pdssasm.o memory.
o atom.o module.o instr.o assemble.o saveload.o float.o ctype.o -lm
mv -f pdssasm.x pdssasm
rm -f version.o
cc -O  -target sun4 -c  pdssmerge.c
cc -O -o pdssmerge.x pdssmerge.o
mv -f pdssmerge.x pdssmerge
sh -c "test ! -d compiler_pl || (cd compiler_pl ; make all)"
echo "compile('pdss_sys.pl'), make_kl1cmp_for_pdss." | sicstus
SICStus 0.7 #9: Sat May 23 12:33:04 JST 1992
{compiling /usr/local/src/pdss/compiler_pl/pdss_sys.pl...}
{/usr/local/src/pdss/compiler_pl/pdss_sys.pl compiled, 280 msec 3392 bytes}
{compiling /usr/local/src/pdss/compiler_pl/top2.pl...}
{Warning: [Index,Old,Opt] - singleton variables in tsscomp/2 in lines 121-127}

     ... Many many messages ...

{compiling /usr/local/src/pdss/compiler_pl/libdir.pl...}
{/usr/local/src/pdss/compiler_pl/libdir.pl compiled, 29 msec 324 bytes}
{ SICStus state saved into /usr/local/src/pdss/compiler_pl/kl1cmp }
**** KL1/B Compiler Ver.0.96(890922) ****
****       for PDSS Ver.2.52(890922) ****

Compiler Mode : 
%%% ERROR !! end_of_file was read

{ End of SICStus execution, user time 63.550 }
chmod +x kl1cmp
echo "compile(['pdsstrans.pl']), go." | sicstus
SICStus 0.7 #9: Sat May 23 12:33:04 JST 1992
{compiling /usr/local/src/pdss/compiler_pl/pdsstrans.pl...}
{Warning: [Lab0] - singleton variables in tbl/2 in lines 153-153}

     ... Many many messages ...

{/usr/local/src/pdss/compiler_pl/pdsstrans.pl compiled, 6600 msec 70352 bytes}
{ SICStus state saved into /usr/local/src/pdss/compiler_pl/pdsstrans }
Debug mode  : 
** end_of_file was read

{ End of SICStus execution, user time 6.620 }
chmod +x pdsstrans
sh -c "test ! -d emacs       || (cd emacs       ; make all)"
nemacs -batch -f batch-byte-compile pdss.el
Compiling /usr/local/src/pdss/pdss.el...
>>Error occurred processing pdss.el: File error (("Opening input file" "no such
 file or directory" "/usr/local/src/pdss/pdss.el"))
Done                                                ## 良く分からないけど、
*** Error code 1                                    ## "cd emacs" が効かない！
make: Fatal error: Command failed for target `pdss.elc'
Current working directory /usr/local/src/pdss/emacs
*** Error code 1
make: Fatal error: Command failed for target `quick'
%
% (cd emacs       ; make all)                       ## 手動でこうすると...
nemacs -batch -f batch-byte-compile pdss.el
Compiling /usr/local/src/pdss/emacs/pdss.el...
Compiling /usr/local/src/pdss/emacs/pdss.el (pdss)...

     ... Many many messages ...

Compiling /usr/local/src/pdss/emacs/kl1-mode.el (kl1-tabify)...
Wrote /usr/local/src/pdss/emacs/kl1-mode.elc
Done
%                                                   ## これでmakeは完了。
%                                                   ## 簡単なテストを行なう。
% cd emulator
% ./pdss
***** PDSS-KL1 V2.52.20 (Mon May 25 21:40:30 JST 1992) *****
....................................................

*******************************************
**** Micro PIMOS (version 2.5) ************
*******************************************
World is /usr/local/src/pdss/emulator
Total heap size is 200000 words
Total code size is 272496 bytes
*******************************************

| ?- compile(sample).
"sample" : Compiling ... primes/0,primes/2,gen/3,sift/2,filter/3,display/1,END.

[primes/0]
successdone
Loading ... done
Module name : sample
Saving ... done

yes.
| ?- stat(sample:primes).
[2,3,5,7,11,13,17,19,23,29,31,37,...]
Total of 5880 reductions in 170 msec.

yes.
| ?- halt.

% 

 付録-II  "emulator/config.h" ファイルのサンプル
-------------------------------------------------

/*************************************************************************
PDSSの為のディレクトリ/ファイル環境の指定。
>> PDSS_LIBDIR: PDSSが立ち上がる時に、ランタイムライブラリを探しにいくディ
      レクトリのパス名。通常はPDSSのトップレベルのディレクトリと同じ。
>> PDSS_SUPDIR: 立ち上げ用ファイル STARTUP が置いてあるディレクトリのパス名。
      STARTUP ファイルには、立ち上げ時に読み込むべき KL1 モジュールのファ
      イル名と、最初のゴール名が記述してある。
>> PDSS_OBJECT_FILE: エミュレータ本体のパス名。Native Code Module を動的に
      リンクする時に使われる。 (しかし、現在 Native Code Generator は
      サポートされていない。)
Configuration of the directory/file environment for PDSS.
>> PDSS_LIBDIR: A path name of the directory which PDSS search for runtime
      libraries at initial startup time. Normally, this is equal to the
      PDSS toplevel directory.
>> PDSS_SUPDIR: A path name of the directory which contains STARTUP file.
      STARTUP file describes path names (relative path from PDSS_LIBDIR)
      of the runtime library which are read at initial startup time, and
      initial goal name.
>> PDSS_OBJECT_FILE: A path name of the PDSS byte-code interpreter executable
      object. It is uesd by dynamic native code module linker.
      (But, native code generator is not supported yet.)
*************************************************************************/
#define PDSS_LIBDIR      "/usr/local/src/pdss"
#define PDSS_SUPDIR      "/usr/local/src/pdss/emulator"
#define PDSS_OBJECT_FILE "/usr/local/src/pdss/emulator/pdss"

/*************************************************************************
PDSS のコードの形式に関する指定。
>> KLB_PACKED_CODE: これが YES の場合には、KL1-B のコードは詰め込まれた
      状態で保持される。この場合、整数等の複数バイトのデータもワードの境界
      に合わせずに詰めて書き込まれる。)  マシンの CPU が RISC タイプの場合
      には、これを NO にしておく必要がある。
>> KLB_4BYTE_REL_ADDR: これが YES の場合には、KL1-B のコードにおける相対
      アドレスは 4byte で表現される。そうでなければ 2byte で表現される。
Configuration for KL1-B code format.
>> KLB_PACKED_CODE: If this switch's value is `YES', KL1-B instruction
      code (byte-code) is filled in continuously. In this case, multiple
      byte data (e.g. integer) is written not in word alignment. If your
      machine uses RISC type CPU, you must define this switch `NO'.
>> KLB_4BYTE_REL_ADDR: If this switch's value is `YES', PDSS use 4 byte
      relative address instead of 2 byte one.
*************************************************************************/
#define KLB_PACKED_CODE    NO
#define KLB_4BYTE_REL_ADDR YES

/*************************************************************************
PDSS が使用するメモリのデフォルトの大きさの指定。
>> HEAP_SIZE: ヒープ領域の大きさ。単位はタグ付きワード(8 バイト)。
      PDSS ではコピー方式の GC を行うので、ここでは全ヒープ領域の半分の
      大きさを指定する。
>> CODE_SIZE: コード領域の大きさ。単位はバイト。ここで指定するのはコード全体
      の大きさである。PDSS は立ち上げ時に、ランタイムライブラリを読み込む
      ために先頭から使用し、その残りを半分に分けてユーザー用として使用する。
Configuration for the default memory size.
>> HEAP_SIZE: Size of head area. This specifies the number of tagged-words
      (8 byte) in the HALF of heap area, since PDSS use copying GC.
>> CODE_AREA: Size of code area. This specifies the number of bytes in the
      whole code area. PDSS loads runtime libraries into top of the code
      area at initial startup time, then PDSS divide code area into 2
      parts and use divided one for user codes.
*************************************************************************/
#define HEAP_SIZE  200000
#define CODE_SIZE 1000000

/*************************************************************************
MRB-GC に関する設定。
>> MRBGC_SWITCH: これが YES の場合に MRB による実時間 GC を行う。
>> MRBGC_COLLECT_VALUE_DEPTH: Collect Value 命令で回収する構造体の深さ。
>> MRBGC_DEREF_TYPE: デレフ時の回収のタイプ。
       0 --> 参照パスで一旦 MRB=ON になった先の回収を行わない。
       1 --> 参照パスで一旦 MRB=ON になった先の回収も行う。
>> MRBGC_FREE_LIST_TYPE: メモリ再利用の為のフリーリストの種類。
       0 --> 1W,2W,3W, ... ,7W,8W,16W,32W の10種類を用意する。
       1 --> 1W,2W,4W,8W,16W,32W,64W,128W の8種類を用意する。
>> MRBGC_STATISTICS: MRB-GCに関する統計情報の集計。
       0 --> 集計は行わない。
       1 --> フリーリストの使用状況の集計を行う。
       2 --> 1 + 命令ごとの回収状況の集計も行う。
Configuration for MRB-GC.
>> MRBGC_SWITCH: If this switch's value is `YES', PDSS collect garbage
      incrementally by the MRB scheme in real time.
>> MRBGC_COLLECT_VALUE_DEPTH: The maximum depth of the nested data structure
      which collected by collect_value instruction.
>> MRBGC_DEREF_TYPE: The switch of garbage collection in dereference routine.
      0 -> If MRB-ON pointer is found in reference path, PDSS don't try
           to collect garbage in the forward path of this pointer.
      1 -> In spite of MRB-ON pointer is found in reference path, PDSS
           try to collect garbage in the forward path of this pointer.
>> MRBGC_FREE_LIST_TYPE: The variation of free lists.
      0 -> Use 10 kinds (1W,2W,3W,...,7W,8W,16W and 32W) of free lists.
      1 -> Use 8 kinds (1W,2W,4W,8W,16W,32W,64W and 128W) of free lists.
>> MRBGC_STATISTICS: The switch of statistics of MRB-GC.
      0 -> PDSS don't collect statistics information of MRB-GC.
      1 -> PDSS collect statistics information about free list only.
      2 -> PDSS collect statistics information about free list and
           incremental garbage collecting instructions.
*************************************************************************/
#define MRBGC_SWITCH              YES
#define MRBGC_COLLECT_VALUE_DEPTH 100
#define MRBGC_DEREF_TYPE            1
#define MRBGC_FREE_LIST_TYPE        0
#define MRBGC_STATISTICS            0

/*************************************************************************
MRB を利用したデッドロック(無限待ち)の eager detection に関する設定。
>> EAGER_DEADLOCK_DETECTION:
      これが YES の場合には eager detection を行なう。
Configuration for eager detection of deadlock (perpetual suspension).
>> EAGER_DEADLOCK_DETECTION:
      If this switch's value is `YES', PDSS deetect deadlock eagerly.
*************************************************************************/
#define EAGER_DEADLOCK_DETECTION YES

/*************************************************************************
Ready Goal Pool に関する設定。
>> TWO_WAY_READY_GOAL_POOL: これが YES の場合には、先頭と最後の2つの入口を
      持った Ready Goal Pool を使用する。即ち、スタックとキューの両方に
      使えるので、この時には、ゴールのスケジューリングを Breadth First
      に変更する事もできる。NO の場合には、スタック方式のみになる。
Configuration for ready goal pool.
>> TWO_WAY_READY_GOAL_POOL: If this switch's value is `YES', PDSS use ready
      goal pool with two entry point: top and last. In this case, ready
      goal pool can be used as stack or queue, and user can select depth
      first or breadth first scheduling. If it's value is `NO', reday goal
      pool is stack and scheduling is depth first only.
*************************************************************************/
#define TWO_WAY_READY_GOAL_POOL YES

/*************************************************************************
コピーGC 時に異常事態になった時の処理に関する設定。
>> GC_SWAP_GOALS_WHEN_PANIC: これが YES の場合には、コピー GC でヒープ領域
      があまり回収できなかった時に、ゴール・スタックの highest プライオリティ
      の中のゴールの順番を入れ替える。これにより、実行順序が変わるので
      ヒープが回収できるようになる可能性がある。
>> GC_ABORT_TASK_WHEN_PANIC: これが YES の場合には、コピー GC でヒープ領域
      がほとんど回収できなかった(GC直後なのにGC要求フラグが立っている)時に、
      ユーザーのタスクをアボートする。これにより、PDSS全体が異常終了する
      のを防ぐ。
Configuration for emergency measures of copying GC.
>> GC_SWAP_GOALS_WHEN_PANIC: If this switch's value is `YES', PDSS swap
      goals in ready goal pool when copying GC get only small gain.
      By this goal swapping, the sequence of goal execution is changed and
      some data on heap may be consumed and collected.
>> GC_ABORT_TASK_WHEN_PANIC: If this switch's value is `YES', PDSS abort
      user task when copying GC get little gain. By this abortion, many
      heap uesd by user task are released and whole PDSS may not abort.
*************************************************************************/
#define GC_SWAP_GOALS_WHEN_PANIC YES
#define GC_ABORT_TASK_WHEN_PANIC YES

/*************************************************************************
アトムテーブルに関する設定。
>> MAX_ATOMS: PDSS で使用できるアトムの数。
Configuration for atom table.
>> MAX_ATOMS: Maximum number of atoms.
*************************************************************************/
#define MAX_ATOMS 20000

/*************************************************************************
整数演算に関する設定。
>> IGNORE_INTEGER_OVERFLOW: この値が YES ならば、組込述語における整数演算
      のオーバーフローを無視する。
>> IGNORE_INTEGER_OVERFLOW: If this value is `YES', PDSS ignores integer
      overflow in builtin predicates.
*************************************************************************/
#define IGNORE_INTEGER_OVERFLOW NO

/*************************************************************************
パッシブユニフィケーションに関する設定。
>> PASSIVE_UNIFY_DEPTH: この値は Passive Unification (wait_value, diff)
      で構造体同士を比較する深さを指定する。この深さまで調べても成功が確定
      しない場合には失敗と見做す。
Configuration for passive unification.
>> PASSIVE_UNIFY_DEPTH: This is the maximum depth of the nested structures
      which compare in passive unification (wait_value, diff). If PDSS
      can't confirm the result of unification while PDSS compare until
      this depth, PDSS regards the unification as failure.
*************************************************************************/
#define PASSIVE_UNIFY_DEPTH 100

/*************************************************************************
コンソール出力に関する設定。
>> PRINT_LENGTH, PRINT_DEPTH: コンソールへのターム出力における、長さと深さ
      の制限の初期値。これを越える部分は "..." で出力する。 
Configuration for console outputs.
>> PRINT_LENGTH, PRINT_DEPTH: These are initial maximum length and depth
      of structure which can be displayed in the console. PDSS print the
      part over this limitation link "...".
*************************************************************************/
#define PRINT_LENGTH 12
#define PRINT_DEPTH  6

/*************************************************************************
パーザーに関する設定。
>> MAX_PRINTABLE_STRING_ATOM_LENGTH: ウィンドウ/ファイル等に出力可能な文字
      列/アトムの長さの最大長。文字列 --> アトム の変換もこの制限を受ける。
Configuration for parser.
>> MAX_PRINTABLE_STRING_ATOM_LENGTH: The maximum length of atom/string
      which can be displayed into window/file.  This limitation is also
      used for atom-string conversion.
*************************************************************************/
#define MAX_PRINTABLE_STRING_ATOM_LENGTH 10000

/*************************************************************************
組込述語のサスペンドに関する設定。
>> COUNT_DCODE_REDUCTION: この値が `YES' ならば、組込述語がサスペンドし、
      ゴール(D-Code)がエンキューされた時に、そのゴールの分のリダクション数
      を普通のゴールと同様に数える。
Configuration for builtin predicate suspension.
>> COUNT_DCODE_REDUCTION: If this switch's value is `YES', PDSS count
      reductions by D-code goals which are generated by builtin predicate
      suspension.
*************************************************************************/
#define COUNT_DCODE_REDUCTION NO

/*************************************************************************
インストラクショントレースに関する設定。
>> INSTRUCTION_TRACE: これが YES の場合には、KL1-B のインストラクション
      単位のトレースが可能となる。
>> INSTRUCTION_COUNT: これが YES の場合には、KL1-B の命令種類ごとの実行
      回数の集計を行う。
>> INSTRUCTION_BRANCH_COUNT: これと INSTRUCTION_COUNT が両方とも YES の
      場合には、KL1-B の命令種類ごとに分岐回数の集計を行う。
Configuration for instruction trace.
>> INSTRUCTION_TRACE: If this switch's value is `YES', PDSS can trace
      KL1-B instructions.
>> INSTRUCTION_COUNT: If this switch's value is `YES', PDSS counts the
      number of times each KL1-B instuction is executed.
>> INSTRUCTION_BRANCH_COUNT: If both this switch's value and
      INSTRUCTION_COUNT's value are `YES', PDSS counts the number of
      branches in each KL1-B instuction.
*************************************************************************/
#define INSTRUCTION_TRACE        NO
#define INSTRUCTION_COUNT        NO
#define INSTRUCTION_BRANCH_COUNT NO
