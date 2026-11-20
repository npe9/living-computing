	「遺伝的アルゴリズムを用いたアライメントシステム」

1. はじめに
  本プログラムは、マルチプルアライメントの問題を組合せ最適化問題と捉え、
遺伝的アルゴリズムの手法を応用した並列システムである。本システムは、遺
伝的アルゴリズムをマルチ個体群の方式で並列計算機上に実装したものであり、
実用規模のアライメント問題でも、準最適な解を比較的高速に求めることがで
きる。本システムは、単純なマルチ山登り並列より、早期に収束に至り、かつ、
最良優先探索並列のような局所最適解に陥ることが少ない。また、ときどき良
いスコアの解の部分アライメントを繋ぎ合わせる操作（クロスオーバー）で、
改善の効率を向上させている。

2. 概要
  我々は、効率の良い探索を実現するマルチ個体群方式の遺伝的アルゴリズムを
  開発し、タンパク質配列の解析問題に応用した。分子生物分野の代表的な
  配列解析問題であるマルチプルアライメントは、最近、並列反復改善法で
  効果的に解決できることが示された。そこで使われた並列探索手法は、最良
  優先探索とマルチ山登り探索であったが、各々は問題点を持っていた。
  最良優先探索は、スコアの良い解の近傍を集中的に探索するので改善速度が
  速いが、比較的悪い局所解に陥ることも多い。一方、マルチ山登り探索は、
  広い範囲を分散的に探索するので比較的良い解へ至り易いが、解の改善に
  時間がかかる。マルチプルアライメントの問題は、すでに定評のある評価尺度が
  確立されており、組合せ最適化問題として解決可能である。しかし現時点では、
  あらゆる観点からの生物学的評価が数値化されているわけではないので、
  生物学者は、いくつかの準最適解を比較のうえ、そこから生物学的知見を導き
  出す。そこでマルチプルアライメントのシステムには、良質の準最適解を高速に
  生成する機能が必要とされている。我々は、並列反復改善法の解法を遺伝的
  アルゴリズムの枠組にあてはめ、効率的な探索を行うマルチ個体群方式を考案した。
  その結果、最良優先探索のように速い改善を行いながら、マルチ山登り探索の
  ように良い準最適解を得られるアライメントシステムを構築できた。

3.プログラム実行環境
  このソフトウェアは、２つのバージョンが存在する。
  ひとつはPIM版で、PIM/mでの実行が可能である。
  もうひとつは。KLIC版で、分散KLIC上での実行が可能であり、
  Sparc Center上での実行を確認している。

  また、マルチ個体群の方式の実行の様子をリアルタイムに
  見ることのできる可視化ツール"gavtool"も同時に公開するが、
  これはSUN OS, OpenWare/Motifの環境で使用できる。

4.文献
   ICOT TR 849:（英語）
   Parallel Iterative Aligner with Genetic Algorithm
   Masato Ishikawa, Tomoyuki Toya, Yasushi Totoki, Akihiko Konagaya.

   ICOT TR 855:（英語）
   Parallel Iterative Aligner with Genetic Algorithm
   Masato Ishikawa, Tomoyuki Toya, Yasushi Totoki, Akihiko Konagaya.

   ICOT TR 900:（日本語）
   並列反復改善法によるタンパク質の配列解析
   石川 幹人、十時 泰、戸谷 智之、星田 昌紀、広沢 誠

   現在、情報処理学会に論文（日本語）を執筆中。（1996年公開見込み）
   タイトルは、
   「マルチ個体群の並列遺伝的アルゴリズムを用いたタンパク質の配列解析」
   戸谷 智之、石川 幹人

5. image file
   PIM/mで実行した時のgavtoolの画面イメージ。

   ALIGNGA/image/crossover0/*.gif : (crossover rate = 0%) execution
   ALIGNGA/image/crossover10/*.gif : (crossover rate = 10%) execution
   
   align??.gif   : アライメント表示 window 
   distrib??.gif : 個体分布 window
   info??.gif	 : 個体情報 window
   fitness.gif	 : 適応度グラフ window
   (?? の数字は世代数に対応します。)


6. installについて
  PIM版については、PIM/mにアクセス可能なファイルシステム(SIMPOS、
  あるいは、telnetでPIMにアクセスする場合、UNIX）上にFTPすれば良い。
  KLIC版については、compileコマンドを実行すれば良い。
  gavtoolについても同じ名称のディレクトリ構造でファイルをセーブし、
  gavtoolでmakeコマンドを起動すればよい。
  なお、詳しくはINSTALLファイルを参照のこと。

7.ファイル名一覧
7.File Lists

ALIGNGA/
-rw-r--r--  1 toya         5248 Jan 10 18:10 COPYRIGHT
-rw-r--r--  1 toya         3794 Jan 10 18:10 COPYRIGHT.j
-rw-r--r--  1 toya         4434 Mar 23 17:03 INSTALL
-rw-r--r--  1 toya         4795 Mar 23 17:03 INSTALL.j
-rw-r--r--  1 toya        16824 Mar 24 15:18 README
-rw-r--r--  1 toya        17232 Mar 24 15:19 README.j
drwxr-xr-x  4 toya          512 Mar 24 14:41 image/
drwxr-xr-x  4 toya          512 Mar 23 17:30 software/

  image/
  drwxr-xr-x  2 toya          512 Mar 24 14:44 crossover0/
  drwxr-xr-x  2 toya          512 Mar 24 14:45 crossover10/

    crossover0/
    -rw-rw-rw-  1 toya        72292 Mar 24 14:44 align34.gif
    -rw-rw-rw-  1 toya         7958 Mar 24 14:44 distrib01.gif
    -rw-rw-rw-  1 toya         8311 Mar 24 14:44 distrib10.gif
    -rw-rw-rw-  1 toya         7349 Mar 24 14:44 distrib20.gif
    -rw-rw-rw-  1 toya         7407 Mar 24 14:44 distrib30.gif
    -rw-rw-rw-  1 toya        13512 Mar 24 14:44 fitness.gif
    -rw-rw-rw-  1 toya         7673 Mar 24 14:44 info10.gif

    crossover10/
    -rw-rw-rw-  1 toya        74257 Mar 24 14:45 align64.gif
    -rw-rw-rw-  1 toya         8033 Mar 24 14:45 distrib01.gif
    -rw-rw-rw-  1 toya         7367 Mar 24 14:45 distrib10.gif
    -rw-rw-rw-  1 toya         7252 Mar 24 14:45 distrib20.gif
    -rw-rw-rw-  1 toya         7382 Mar 24 14:45 distrib30.gif
    -rw-rw-rw-  1 toya         7569 Mar 24 14:45 distrib40.gif
    -rw-rw-rw-  1 toya         7241 Mar 24 14:45 distrib50.gif
    -rw-rw-rw-  1 toya         7359 Mar 24 14:45 distrib60.gif
    -rw-rw-rw-  1 toya        17208 Mar 24 14:45 fitness.gif
    -rw-rw-rw-  1 toya         9734 Mar 24 14:45 info10.gif

  software/
  drwxr-xr-x  4 toya          512 Mar 23 17:30 gav/
  drwxr-xr-x  4 toya          512 Mar 23 17:30 gavtool/

    gav/
    drwxr-xr-x  2 toya         1024 Mar 23 17:30 KLIC/
    drwxr-xr-x  2 toya         1024 Mar 23 17:30 PIM/

      KLIC/
      -rw-r--r--  1 toya         1132 Mar 23 15:31 2dp_new_klic.h
      -rw-r--r--  1 toya         3703 Mar 23 15:40 align_string.c
      -rw-r-----  1 toya         2887 Mar 23 15:20 ch_og.kl1
      -rw-r-----  1 toya         1834 Mar 23 15:20 check_msg.kl1
      -rwxr-x--x  1 toya          464 Mar 23 15:52 compile*
      -rw-r-----  1 toya         2021 Mar 23 15:20 converter.kl1
      -rw-r-----  1 toya        19370 Mar 23 15:20 cost_b.c
      -rw-r-----  1 toya        14986 Mar 23 15:20 cost_s.c
      -rw-r-----  1 toya         1430 Mar 23 15:20 cp.kl1
      -rw-r-----  1 toya         4285 Mar 23 15:20 crossover.kl1
      -rw-r-----  1 toya         4090 Mar 23 15:20 datalist.kl1
      -rw-r-----  1 toya        25723 Mar 23 15:20 dayhoff.kl1
      -rw-r-----  1 toya        25187 Mar 23 15:20 dist_b.c
      -rw-r-----  1 toya        15806 Mar 23 15:20 dist_s.c
      -rw-r-----  1 toya         1948 Mar 23 15:20 dp_1seq.kl1
      -rw-r-----  1 toya          919 Mar 23 15:20 dummy.kl1
      -rw-r-----  1 toya         6978 Mar 23 15:20 energy.kl1
      -rw-r-----  1 toya         3681 Mar 23 15:20 gav.kl1
      -rw-r-----  1 toya         9212 Mar 23 15:20 gdp_c.c
      -rw-r-----  1 toya         7405 Mar 23 15:20 generateD_b.c
      -rw-r-----  1 toya         7407 Mar 23 15:20 generateD_s.c
      -rw-r-----  1 toya         5860 Mar 23 15:20 gunkan.kl1
      -rw-r-----  1 toya         7781 Mar 23 15:20 gunnai.kl1
      -rw-r-----  1 toya         2051 Mar 23 15:20 heni.kl1
      -rw-r-----  1 toya         5724 Mar 23 15:43 keep_m_b.c
      -rw-r-----  1 toya         1189 Mar 23 15:43 keep_m_s.c
      -rw-r-----  1 toya         2231 Mar 23 15:20 kl1-pt2.kl1
      -rw-r-----  1 toya         3029 Mar 23 15:20 main.kl1
      -rw-r-----  1 toya         2876 Mar 23 15:20 make_prof.c
      -rw-r-----  1 toya         4445 Mar 23 15:20 master.kl1
      -rw-r-----  1 toya         2699 Mar 23 15:20 matrix_amino.c
      -rw-r-----  1 toya        10488 Mar 23 15:20 minimum_b.c
      -rw-r-----  1 toya         2576 Mar 23 15:20 minimum_s.c
      -rw-r-----  1 toya         5553 Mar 23 15:20 slave.kl1
      -rw-r-----  1 toya         1963 Mar 23 15:20 socket.kl1
      -rw-r-----  1 toya         3531 Mar 23 15:20 sort.kl1
      -rw-r-----  1 toya         1939 Mar 23 15:20 stringdata.kl1
      -rw-r-----  1 toya         2414 Mar 23 15:20 to_gav.kl1
      -rw-r-----  1 toya         3122 Mar 23 15:20 to_slave.kl1
      -rw-r-----  1 toya         8078 Mar 23 15:20 tool.kl1
      -rw-r-----  1 toya          810 Mar 23 15:49 top-2_c.kl1

      PIM/
      -rw-r--r--  1 toya        48174 Feb  2 11:14 DP_aligned.kl1
      -rw-r--r--  1 toya         7282 Feb  2 11:14 VGA.kl1
      -rw-r--r--  1 toya         7280 Feb  2 11:15 VGB.kl1
      -rw-r--r--  1 toya         6669 Feb  2 11:15 VP4.kl1
      -rw-r--r--  1 toya         4589 Feb  2 11:15 VPF.kl1
      -rw-r--r--  1 toya         2884 Feb  2 11:15 ch_og.kl1
      -rw-r--r--  1 toya         1792 Feb  2 11:16 check_msg.kl1
      -rw-r--r--  1 toya          679 Jan 10 18:12 compile.com
      -rw-r--r--  1 toya         1659 Feb  2 11:16 cp.kl1
      -rw-r--r--  1 toya         4118 Feb  2 11:16 crossover.kl1
      -rw-r--r--  1 toya         3379 Feb  2 11:16 datalist.kl1
      -rw-r--r--  1 toya        25588 Feb  2 11:17 dayhoff.kl1
      -rw-r--r--  1 toya        12904 Jan 10 18:12 dayhoff.unload
      -rw-r--r--  1 toya         2295 Jan 10 18:12 demo.com
      -rw-r--r--  1 toya         2803 Feb  2 11:17 dp_1seq.kl1
      -rw-r--r--  1 toya         7545 Feb  2 11:18 energy.kl1
      -rw-r--r--  1 toya         6713 Feb  2 11:18 gav.kl1
      -rw-r--r--  1 toya       112542 Jan 10 18:12 gav.unload
      -rw-r--r--  1 toya         3252 Feb  2 11:18 gav_rec.kl1
      -rw-r--r--  1 toya         6227 Feb  2 11:18 gunkan.kl1
      -rw-r--r--  1 toya         7908 Feb  2 11:19 gunnai.kl1
      -rw-r--r--  1 toya         1788 Feb  2 11:19 heni.kl1
      -rw-r--r--  1 toya         5297 Feb  2 11:19 master.kl1
      -rw-r--r--  1 toya         5117 Feb  2 11:19 master_rec.kl1
      -rw-r--r--  1 toya         1175 Feb  2 11:19 outgap.kl1
      -rw-r--r--  1 toya          291 Jan 10 18:12 relink.com
      -rw-r--r--  1 toya         4042 Feb  2 11:20 rm_ag.kl1
      -rw-r--r--  1 toya         5376 Feb  2 11:20 slave.kl1
      -rw-r--r--  1 toya         1997 Feb  2 11:21 socket.kl1
      -rw-r--r--  1 toya         2056 Feb  2 11:21 stringdata.kl1
      -rw-r--r--  1 toya         2427 Feb  2 11:22 to_gav.kl1
      -rw-r--r--  1 toya         3239 Feb  2 11:22 to_slave.kl1
      -rw-r--r--  1 toya         8010 Feb  2 11:22 tool.kl1
      -rw-r--r--  1 toya          595 Jan 10 18:12 unload.com

    gavtool/
    -rw-r--r--  1 toya          116 Mar 22 16:59 Makefile
    drwxr-xr-x  2 toya          512 Mar 23 17:33 gadmks/
    drwxr-xr-x  2 toya         2560 Mar 23 17:34 gavtool/

      gadmks/
      -rw-r--r--  1 toya         1889 Mar 23 17:33 Makefile
      -rw-r--r--  1 toya          683 Mar 23 17:33 gadmks_def.c
      -rw-r--r--  1 toya          707 Mar 23 17:33 gadmks_def.h
      -rw-r--r--  1 toya         1267 Mar 23 17:33 gadmks_error.c
      -rw-r--r--  1 toya         1154 Mar 23 17:33 gadmks_main.c
      -rw-r--r--  1 toya         6900 Mar 23 17:33 gadmks_socket.c
      -rw-r--r--  1 toya         1532 Mar 23 17:33 gavt_ifdef.h

      gavtool/
      -rw-r--r--  1 toya        12467 Mar 23 17:34 Makefile
      -rw-r--r--  1 toya       852137 Mar 23 17:34 cross0.gatd
      -rw-r--r--  1 toya      1626742 Mar 23 17:34 cross10.gatd
      -rwxr-xr-x  1 toya        24576 Mar 23 17:34 gadmks*
      -rw-r--r--  1 toya        12116 Mar 23 17:34 gavt_debug.c
      -rw-r--r--  1 toya         6449 Mar 23 17:34 gavt_def.c
      -rw-r--r--  1 toya         7548 Mar 23 17:34 gavt_def.h
      -rw-r--r--  1 toya         1284 Mar 23 17:34 gavt_error.c
      -rw-r--r--  1 toya         1532 Mar 23 17:34 gavt_ifdef.h
      -rw-r--r--  1 toya         1318 Mar 23 17:34 gavt_main.c
      -rw-r--r--  1 toya         2670 Mar 23 17:34 gavt_utility.c
      -rw-r--r--  1 toya         1206 Mar 23 17:34 gavt_warning.c
      -rw-r--r--  1 toya        14436 Mar 23 17:34 gavtd_file.c
      -rw-r--r--  1 toya        20571 Mar 23 17:34 gavtd_gadatainf.c
      -rw-r--r--  1 toya        27035 Mar 23 17:34 gavtd_memory.c
      -rw-r--r--  1 toya         4771 Mar 23 17:34 gavtd_realtime.c
      -rw-r--r--  1 toya        13707 Mar 23 17:34 gavtg_adwbarchart.c
      -rw-r--r--  1 toya         2050 Mar 23 17:34 gavtg_adwcolor.c
      -rw-r--r--  1 toya        29515 Mar 23 17:34 gavtg_adwcostparam.c
      -rw-r--r--  1 toya        17565 Mar 23 17:34 gavtg_adwda.c
      -rw-r--r--  1 toya         3413 Mar 23 17:34 gavtg_adwdebug.c
      -rw-r--r--  1 toya         6111 Mar 23 17:34 gavtg_adwdef.c
      -rw-r--r--  1 toya         6498 Mar 23 17:34 gavtg_adwdef.h
      -rw-r--r--  1 toya         4212 Mar 23 17:34 gavtg_adwdialog.c
      -rw-r--r--  1 toya         4063 Mar 23 17:34 gavtg_adwdpmgr.c
      -rw-r--r--  1 toya         3293 Mar 23 17:34 gavtg_adwevent.c
      -rw-r--r--  1 toya          980 Mar 23 17:34 gavtg_adwfile.c
      -rw-r--r--  1 toya         3026 Mar 23 17:34 gavtg_adwfont.c
      -rw-r--r--  1 toya         4763 Mar 23 17:34 gavtg_adwgc.c
      -rw-r--r--  1 toya        10826 Mar 23 17:34 gavtg_adwidentity.c
      -rw-r--r--  1 toya         5693 Mar 23 17:34 gavtg_adwmain.c
      -rw-r--r--  1 toya         4493 Mar 23 17:34 gavtg_adwmenu.c
      -rw-r--r--  1 toya         1035 Mar 23 17:34 gavtg_adwtest.c
      -rw-r--r--  1 toya          844 Mar 23 17:34 gavtg_adwview.c
      -rw-r--r--  1 toya         4156 Mar 23 17:34 gavtg_buildmenu.c
      -rw-r--r--  1 toya         1323 Mar 23 17:34 gavtg_color.c
      -rw-r--r--  1 toya         1594 Mar 23 17:34 gavtg_debug.c
      -rw-r--r--  1 toya         1804 Mar 23 17:34 gavtg_def.c
      -rw-r--r--  1 toya         2085 Mar 23 17:34 gavtg_def.h
      -rw-r--r--  1 toya        28375 Mar 23 17:34 gavtg_fgwda.c
      -rw-r--r--  1 toya        21751 Mar 23 17:34 gavtg_fgwdctrl.c
      -rw-r--r--  1 toya         3533 Mar 23 17:34 gavtg_fgwdebug.c
      -rw-r--r--  1 toya         3192 Mar 23 17:34 gavtg_fgwdef.c
      -rw-r--r--  1 toya         9708 Mar 23 17:34 gavtg_fgwdef.h
      -rw-r--r--  1 toya         4238 Mar 23 17:34 gavtg_fgwdialog.c
      -rw-r--r--  1 toya        39989 Mar 23 17:34 gavtg_fgwdparam.c
      -rw-r--r--  1 toya         6191 Mar 23 17:34 gavtg_fgwevent.c
      -rw-r--r--  1 toya         9250 Mar 23 17:34 gavtg_fgwexpshr.c
      -rw-r--r--  1 toya         4521 Mar 23 17:34 gavtg_fgwfile.c
      -rw-r--r--  1 toya         2075 Mar 23 17:34 gavtg_fgwfont.c
      -rw-r--r--  1 toya         4519 Mar 23 17:34 gavtg_fgwgc.c
      -rw-r--r--  1 toya         4454 Mar 23 17:34 gavtg_fgwmain.c
      -rw-r--r--  1 toya        12311 Mar 23 17:34 gavtg_fgwmenu.c
      -rw-r--r--  1 toya         3055 Mar 23 17:34 gavtg_fgwpickgen.c
      -rw-r--r--  1 toya         4518 Mar 23 17:34 gavtg_fgwsignal.c
      -rw-r--r--  1 toya         3599 Mar 23 17:34 gavtg_fgwsim.c
      -rw-r--r--  1 toya         1467 Mar 23 17:34 gavtg_fgwtest.c
      -rw-r--r--  1 toya         2341 Mar 23 17:34 gavtg_fgwview.c
      -rw-r--r--  1 toya         3463 Mar 23 17:34 gavtg_font.c
      -rw-r--r--  1 toya        10987 Mar 23 17:34 gavtg_idgwbreadth.c
      -rw-r--r--  1 toya        10530 Mar 23 17:34 gavtg_idgwda.c
      -rw-r--r--  1 toya         2705 Mar 23 17:34 gavtg_idgwdebug.c
      -rw-r--r--  1 toya         2242 Mar 23 17:34 gavtg_idgwdef.c
      -rw-r--r--  1 toya         6672 Mar 23 17:34 gavtg_idgwdef.h
      -rw-r--r--  1 toya         4254 Mar 23 17:34 gavtg_idgwdialog.c
      -rw-r--r--  1 toya         4535 Mar 23 17:34 gavtg_idgwdpmgr.c
      -rw-r--r--  1 toya         4138 Mar 23 17:34 gavtg_idgwevent.c
      -rw-r--r--  1 toya         1144 Mar 23 17:34 gavtg_idgwfile.c
      -rw-r--r--  1 toya         2098 Mar 23 17:34 gavtg_idgwfont.c
      -rw-r--r--  1 toya         3061 Mar 23 17:34 gavtg_idgwgc.c
      -rw-r--r--  1 toya         5319 Mar 23 17:34 gavtg_idgwmain.c
      -rw-r--r--  1 toya         3912 Mar 23 17:34 gavtg_idgwmenu.c
      -rw-r--r--  1 toya         6039 Mar 23 17:34 gavtg_idgwpickgf.c
      -rw-r--r--  1 toya          864 Mar 23 17:34 gavtg_idgwtest.c
      -rw-r--r--  1 toya          852 Mar 23 17:34 gavtg_idgwview.c
      -rw-r--r--  1 toya         1439 Mar 23 17:34 gavtg_iidwdef.c
      -rw-r--r--  1 toya         2262 Mar 23 17:34 gavtg_iidwdef.h
      -rw-r--r--  1 toya         4248 Mar 23 17:34 gavtg_iidwdialog.c
      -rw-r--r--  1 toya          961 Mar 23 17:34 gavtg_iidwfile.c
      -rw-r--r--  1 toya         1338 Mar 23 17:34 gavtg_iidwfont.c
      -rw-r--r--  1 toya         4809 Mar 23 17:34 gavtg_iidwmain.c
      -rw-r--r--  1 toya         3167 Mar 23 17:34 gavtg_iidwmenu.c
      -rw-r--r--  1 toya         6936 Mar 23 17:34 gavtg_iidwst.c
      -rw-r--r--  1 toya         1099 Mar 23 17:34 gavtg_iidwtest.c
      -rw-r--r--  1 toya         3334 Mar 23 17:34 gavtg_main.c
      -rw-r--r--  1 toya         1030 Mar 23 17:34 gavtg_warp.c
      -rwxr-xr-x  1 toya      1564672 Mar 23 17:34 gavtool*
      -rw-r--r--  1 toya          504 Mar 23 17:34 gavtool.res

