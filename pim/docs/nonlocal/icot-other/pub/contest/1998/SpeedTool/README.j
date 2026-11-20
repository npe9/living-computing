平成１０年度 KLIC プログラミング・コンテスト スピード部門課題

	「スケルトンコンテスト」
 
結果表示用 プログラム 第1版
					Aug. 25 1998 
					by  Eiji Sugino <sugino@iwate-pu.ac.jp>

このプログラムは、平成10年度KLICプログラミング・コンテスト スピード部門課題
「スケルトンコンテスト」参加者に対して、各自が作成したプログラムの動作確認に
利用してもらうために作成した。 
  なお、このプログラムは、実際に、本プログラムコンテストの選考に用いられる
保証は無い。 また、プログラムコンテストへの応募の際には、本プログラムを
添付しないこと。

１ ディレクトリ構造

   このセットのディレクトリ構造は、次のようになっている

	% ls
	Makefile	README.j	make.sh*	test.dat
	README.e	main.kl1	sample/
		
   (0) README.j は本ファイル、README.e は英語版である。
   (1) ディレクトリ sample は、ダミープログラムが入っている。 
   (2) main.kl1 は、表示用プログラムである。
   (3) Makefileは、参加者のプログラムをmakeするためのサンプルである。
   (4) test.dat は、テスト用のデータである。
   (5) make.sh によって、指定ディレクトリにあるプログラムをMakeする。

２ 評価対象プログラムの置き方

	ここでは ダミーを例にして、プログラムの置き方を説明する。

   (1) ディレクトリを作る。 
	ディレクトリ名は、何でもかまわない。ここでは sample とする。

	% mkdir sample
	% cd sample

   (2) (1)で作ったディレクトリにユーザプログラムを置く。
	ここに置かれた *.kl1 の形のすべてのファイルがコンパイルされる。

	% cp ~myself/*.kl1  .

   (3) (1)で作ったディレクトリにMakefileを置く。
	１の(3)で用意した Makefile をコピーするかリンクを張ればよい。

	% ln -s ../Makefile Makefile
	% ls 
	Makefile@	skeleton.kl1

	% cd ..

３ 評価プログラムのコンパイル方法

	コマンド make.sh に、ディレクトリを指定して実行する。

	% ./make.sh sample

４ 評価プログラムの実行方法

	コマンド は、上で指定したディレクトリの下に skel という名前で
	作られる。 
	このコマンドに引数を与えて実行する。

	./sample/skel  [Time] Size FileName

	[ ]でくくられた Time は省略可能である。

	(1) Time は、タイムアウト時間である。 
	    指定した時間になると強制終了する。省略した場合は、強制終了しない。
	(2) Size は、盤面のサイズである。 1～20の範囲で指定する。
	(3) FileName は、データファイル名である。
	    サンプルとして用意した test.dat には、以下のように与えられている。

		 [	word(fifth, "FIFTH", 5),
			word(gener, "GENERATION", 17),
			word(klic,  "KLIC", 13),
			word(speed, "SPEED", 4),
			word(cont,  "CONTEST", 9),
			word(prob,  "PROBLEM", 4),
			word(solut, "SOLUTION", 15),
			word(yours, "YOURS", 3),
			word(winner,"WINNER",21),
			word(or,    "OR", 1),
			word(loser, "LOSER", 2) 
		].

※ 本プログラムでは、対象プログラムから与えられた結果を吟味して、
   正しいかチェックしている。
   もし誤った解であれば、次のようなメッセージを出力する。

  Illegal number of arguments        	コマンドの引数個数が間違っている。
  Illegal size of the board 		盤面のサイズ指定に誤りがある。

  Error! Illegal word usage : ...	
	問題として与えていない単語を使ったか、2度以上使用している。
  Error! Illegal word or position : ...
	盤面に置けないような位置に単語を置いている。
  Error! Illegal connection : ...
	単語を置くと、誤った単語の接続ができる。
  Error! There is a isolated word: ...
	孤立する単語がある。