「遺伝的アルゴリズムを用いたアライメントシステム」

1.実行環境
  [PIM version]
  Machine: PIM/m 256PEs
  SIMPOS : III Version 8.2
  PIMOS : 

  [KLICversion}
  Machine: Sparc Center (20PE)
  KLIC: Version 1.7

  [gavtool]
   Machine: Sparc
   SunOS: Release 4.1.3-JLE1.1.3 OS/AS=V4.13 (AB1405)
   System Memory: 16M
   DISK Memory: 10M
   Toolkit: OpenWare/Motif version2

2. インストールの仕方
  [PIM version]
   ディレクトリ kl1の下のファイルをPIM/mにアクセスするファイルシステム
   上にFTPする。
   telnetを介してPIMにアクセスする場合はUNIX file systemで構いません。
   （ただし、実行形式の*.unloadはbinary modeで、
   *.kl1や*.comはascii modeで転送して下さい。）


  PIMOSにloginした後、listenerで、
 	load("gav.unload").
  を実行することでプログラムがロードされます。
  listenerでtake "compile.com".を実行することでcompileを
  やり直すことができる。
   
   [KLIC version]
   distributed KLIC systemをインストールしたマシンに、
   software/gav/KLICの下のファイルを全てFTPして下さい。
   そして、main.kl1を以下のように書きなおして下さい。  

   もし、gavtoolを起動するマシンのinternet addressがA.B.C.Dなら、

       旧： {{192,156,144,116},10000},              % SocketAddress
       ->
       新： {{A,B,C,D},10000},              % SocketAddress

   書き直した後、"compile" commandを入力して下さい。

   [gavtool]
   FTPなどでディレクトリgavの下を同じ構造でファイルをセーブする。
   gavのすぐ下でmakeを実行するとgavtool, gadmksでそれぞれのmakeが
   行なわれ、gavtool, gadmksが作られる。
   gadmksをディレクトリgavtoolにcpする。

3. 実行の仕方
   [PIM version]
  実行例がdemo.comにあります。
  環境変数XENVIRONMENTにgav/gavtool/gavtool.resを設定した後、
  gav/gavtool/gavtoolを起動し、できたウィンドウで、
  "simulation","start"をクリックする。
   (シェルに表示されるport No.が10000であることを確認下さい。)
  それから、PIMのlistener上でgoalを実行させる。

  なお、実行ゴールのシンタクスは以下の通り。
  gav:ga(
	SeqList,	% Sequence List [List of string data]
	NameList,	% Name of Sequence's List [List of string data]
	GrpVectList,	% List of GrpVet, [List of Vector]
			% GrpVect = {Population,SelectionRate} [Vector of int]
	CrossoverRate,	% crossover percentage [integer]
	OneCycleTime,	% Time of one cycle (sec) [integer]
	DPCutRatio,	% Cut percentage in Dynamic Programming [integer]
	GapParam,	% GapCost Parameter  {A,B,C} (cost=A+B*K)
			% [vector of int]  
	ExecTime,	% Execution Time (sec) [integer]
	RandomSeed,	% Seed of Random Numbers [integer]
	Address,	% Internet address and port No. for gavtool [vector]
			% default port No. = 10000
			% 192.26.9.203 => {{192,26,9,203},10000}
	Output ).	% Output.

   [KLIC version]
  環境変数XENVIRONMENTにgav/gavtool/gavtool.resを設定した後、
  gav/gavtool/gavtoolを起動し、できたウィンドウで、
  "simulation","start"をクリックする。
   (シェルに表示されるport No.が10000であることを確認下さい。)
  その後、コマンド"gav"をシェルから入力下さい。
  もし、データやパラメータを変更する場合は、main.kl1を
  書き直して、compileを再び行なって下さい。
  main.kl1に書かれているgoal syntaxはKL1版と同じです。

4. gavtoolの簡単な機能紹介

[Fitness Graph window]
    KL1プログラムの実行データをリアルタイム表示する時は、
    "simulation"&"start"をクリックして、待機状態にする
    また、実際の実行データガディレクトリgavtoolの下に、
    "cross0.gatd"と"cross10.gatd"があるので、これを"file"&"open"をクリック
    してできたウィンドウから指定して表示することができる。

    このウィンドウには、
    各個体群ごとのFitnessスコアの平均値の履歴（実線）と 最大、最小値の
    履歴（点線）が表示される。
    "options"の"dislpay group"をクリックすることで描く線を選択できる。
    また、マウスの左ボタンで範囲指定することで拡大、中ボタンの範囲指定で
    縮小表示が可能。("options"の"expand ..."で方向を指定できる。）
    グラフ上、マウス右クリックでその世代での個体分布グラフが見られる。

[Individual Distribution graph window]
    棒グラフをマウス右クリックすることでそれに含まれる個体の情報を
    見ることができる。
   （個体のID、スコア、最後にグループを移動した世代、最後に交配した世代）
    また、グループのアルファベットを右クリックすることでそのグループでの
    最大スコアのアライメントを表示する。



