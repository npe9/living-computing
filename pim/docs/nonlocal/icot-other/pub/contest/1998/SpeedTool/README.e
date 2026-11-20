KLIC PROGRAMMING CONTEST '98
SPEED CATEGORY Subject:Skeleton Contest

 
Program for displaying solutions (ver.1)
					Aug. 25 1998 
					by  Eiji Sugino <sugino@iwate-pu.ac.jp>

This program displays solutions which are find by participants'
program in the Speed Category of KLIC Programming Contest '98. Please
remark that using this program for the contest judgement is not
guaranteed. Further more, when you submit your program, please DO NOT
include this program.


1. Structure of the directory:

	% ls
	Makefile	README.j	make.sh*	test.dat
	README.e	main.kl1	sample/
		
   (0) README.e is this file. README.j is its Japanese version,
   (1) directory 'sample' provides a dummy program for Skeleton Contest,
   (2) main.kl1 is for displaying solutions,
   (3) 'Makefile' is a sample file to compile your program,
   (4) 'test.dat' is a sample data for testing,
   (5) 'make.sh' is a Bourne-shell program to execute your program.

2. How to place your program:

   (1) Make a directory (with ANY name, for example 'sample' here.)

	% mkdir sample
	% cd sample

   (2) Put your program at the directory 'sample'.
       All of files with extensions 'kl1' will be compiled later.

	% cp ~myself/*.kl1  .

   (3) Put a 'Makefile' at the directory 'sample'.
       Please copy Makefile mentioned 1-(3) in the above, 
       or make a link to it.


	% ln -s ../Makefile Makefile
	% ls 
	Makefile@	skeleton.kl1

	% cd ..

3. How to compile:

	% ./make.sh sample

	The name of the directory in which your program is placed
	should be specified. The executable program is created as 'skel'.

4. How to execute:

	%./sample/skel  [Time] Size FileName

	Time surrounded by '[' and ']' is optional.

	(1) 'Time' is the timeout limit in second. Program will 
	    be terminated at the designate timeout limit.
	(2) 'Size' is a size of a square board.  (1 =< Size =< 20)
	(3) 'FileName' is the file name of test data.
	    A sample 'test.dat' has:

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

* This program checks the correctness of solutions produced by your program.
  If the solution is wrong, the followings messages will be displayed:

  Illegal number of arguments
  Illegal size of the board

  Error! Illegal word usage :  using words which are not given in the problem.
  Error! Illegal word or position :
                               designating wrong position for placing words.
  Error! Illegal connection :  detecting wrong connection of words
  Error! There is a isolated word: 
                               detecting no connection
