KLICON 98 エントリーコース『ライツアウト』動作確認プログラム 第 1版
===================================================================

Sep 24, 1998
by ROKUSAWA Kazuaki <rokusawa@klic.org>

[実行の仕方]

1. 作成した課題プログラムをこのディレクトリ (Kakunin) に
game.kl1 という名前で置いてください.  

2. コンパイルします.  
% klic check.kl1 game.kl1<CR>

3. プログラムを実行します.  
% a.out < test_data.dat<CR>

[実行結果]

動作が正常の場合は correct と (だけ) 表示されます.  
動作が異常の場合は, 以下の 3つが表示されます.  
o 異常動作が起きた時のボードの状態
o 入力 -- click(Row,Col) あるいは redraw
o 異常な出力 -- [set(Row,Col),reset(),...]

[ファイルリスト]

README.j -- このファイル (README の日本語版)
README.e -- README の英語版
check.kl1 -- 動作確認プログラム
game.kl1 -- 作成した課題プログラム (動作確認対象プログラム)
test_data.dat -- 動作確認に使用するデータ
test.kl1 -- 簡易実行プログラム (下記参照)


=========================================================

!! 簡易実行プログラム !!

[実行の仕方]

1. コンパイルします.  
% klic test.kl1 game.kl1<CR>

2. プログラムを実行します.  
% a.out<CR>

[実行例]

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
