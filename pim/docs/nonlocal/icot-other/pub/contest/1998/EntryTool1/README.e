KLIC PROGRAMMING CONTEST '98 ENTRY CATEGORY
Lights Out Checking Execution Program (ver. 1) 

Sep 24, 1998
by ROKUSAWA Kazuaki <rokusawa@klic.org>

[how to execute]

1. Copy your program to this directory (Kakunin) with the name "game.kl1."

2. compile
% klic check.kl1 game.kl1<CR>

3. execute
% a.out < test_data.dat<CR>

[execution results]

If your program is correct, this program displays only "correct".  
If incorrect, the followings are displayed.  
o status of BOARD on which illegal set/reset outputs are generated.  
o click/redraw input which causes illegal outputs.  
o illegal set/reset outputs.  

[list of files]

README.e -- this file (README in English)
README.j -- README in Japanese
check.kl1 -- checking execution program
game.kl1 -- your program to be checked
test_data.dat -- data used for checking
test.kl1 -- handy execution program (see below)

===============================================================

!! handy execution program !!

[How to execute]

1. compile
% klic test.kl1 game.kl1<CR>

2. execute
% a.out<CR>

[example of execution results]

% klic test.kl1 game.kl1
% a.out
"input: click(Row,Col).|redraw.|[]."
"o -- ON, x -- OFF"
ooooo
ooooo
ooooo
ooooo
ooooo
click(0,0).
[reset(0,0),reset(1,0),reset(0,1)]
xxooo
xoooo
ooooo
ooooo
ooooo
click(4,4).
[reset(4,4),reset(3,4),reset(4,3)]
xxooo
xoooo
ooooo
oooox
oooxx
redraw.
[reset(0,0),reset(0,1),reset(1,0),reset(3,4),reset(4,3),reset(4,4)]
click(1,2).
[reset(1,2),reset(0,2),reset(2,2),reset(1,1),reset(1,3)]
xxxoo
xxxxo
ooxoo
oooox
oooxx
[].
% 
