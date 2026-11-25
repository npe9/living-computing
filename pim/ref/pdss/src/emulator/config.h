/*************************************************************************
*  PDSS (PIMOS Development Support System)  Version 2.52		 *
*  (C) Copyright 1988,1989,1990,1992.					 *
*  Institute for New Generation Computer Technology (ICOT), Japan.	 *
*  Read "../COPYRIGHT" for detailed information.			 *
*************************************************************************/


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
#define PDSS_LIBDIR      ".."   /* PORT: run from emulator/ */
#define PDSS_SUPDIR      "."
#define PDSS_OBJECT_FILE "./pdss"


/*************************************************************************
PDSS のコードの形式に関する指定。
>> KLB_PACKED_CODE: これが YES の場合には、KL1-B のコードは詰め込まれた
      状態で保持される。この場合、整数等の複数バイトのデータもワードの境界
      に合わせずに詰めて書き込まれる。)  マシンの CPU が RISC タイプの場合
      には、これを NO にしておく必要がある。
>> KLB_4BYTE_REL_ADDR: これが YES の場合には、KL1-B のコードにおける相対
      アドレスは 4byte で表現される。そうでなければ 2byte で表現される。
Configuration for instruction trace.
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
#define MRBGC_SWITCH		  YES
#define MRBGC_COLLECT_VALUE_DEPTH 100
#define MRBGC_DEREF_TYPE	    1
#define MRBGC_FREE_LIST_TYPE	    0
#define MRBGC_STATISTICS	    0


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
