1.データ形式

データ形式は、次のようになっています。

[要素,その要素の数,要素,その要素の数,要素,その要素の数,...]

ただし、要素は、昇順にソートされています。

例えば、[7,1,2,7,7]というリストの場合、7が3個、1が1個、2が2個あるので、
これを昇順にソートして、[1,1,2,1,7,3]という形となります。

2.encode/2

encode/2では、クイックソートのアルゴリズムを用いて、入力されたリストを
ソートすると同時に、それぞれの要素の数をカウントしています。

 encode([]   ,Out) :- Out = [].
 encode([H|T],Out) :- terminal(T,H,1,Out,[]).

terminal/5という述語で、クイックソートの軸要素を選択していますが、これ
には、左からみて最初に得られた2つの異なる値の大きいほうをとるという方
法を用いています(3,4番目の節)。ここで、異なる値が得られるまでリストを
サーチするのと並行して、同じ要素の数をカウントしています(2番目の節)。
異なる要素が無ければ、その要素と、要素の数を結果として出力します(1番目
の節)。

 terminal([]   ,H0,N,Xs ,Ys) :- Xs=[H0,N|Ys].
 terminal([H|T],H0,N,Xs, Ys) :- H =:= H0 |
     terminal(T,H0,~(N+1),Xs,Ys).
 terminal([H|T],H0,N,Xs0,Ys) :- H  >  H0 |
     node(T,H ,L,R), terminal(L,H0,N,Xs0,Xs1), terminal(R,H,1,Xs1,Ys).
 terminal([H|T],H0,N,Xs0,Ys) :- H  <  H0 |
     node(T,H0,L,R), terminal(L,H,1,Xs0,Xs1), terminal(R,H0,N,Xs1,Ys).

その後、node/4を用いて、軸要素未満の要素の集合と、軸要素以上の要素の集
合とに分割します。この時、軸の選び方から、それぞれの集合が空となること
が無いため、その場合の判定を行う必要がありません。

 node([]   ,V,L,R) :-          L = [], R = [].
 node([H|T],V,L,R) :- H >= V | R = [H|NR], node(T,V,L,NR).
 node([H|T],V,L,R) :- H <  V | L = [H|NL], node(T,V,NL,R).

3.decode/2

decode/2は、各要素を、その要素の数だけ生成することで行っています。逐次
で行うことを考えて、decode/4という1つの述語で全ての処理を行っています。

 decode([]     ,L) :- L = [].
 decode([H,N|T],L) :- decode(N,H,T,L).

 decode(N,H,T      ,L) :- N > 0 | L = [H|L1], decode(~(N-1),H,T,L1).
 decode(0,_,[]     ,L) :- L = [].
 decode(0,_,[H,N|T],L) :- decode(N,H,T,L).

4.union/3

union/3は、マージをすることで実現しています。片方のリストにしか現れな
い要素は、そのまま結果に流します(1～4番目の節)。また、同じ要素が現れた
場合、その要素数を加えて結果とします(5番目の節)。また、ガード部分の形
を同じにすることで、KLICからCへのコンパイルが効率よくなされるようにし
ています。

 union([],M1,M) :- M1 = M.
 union(M0,[],M) :- M0 = M.
 union(M0,M1,M) :- M0 = [H0,_ |_ ], M1 = [H1,N1|T1], H0  >  H1 |
     M = [H1,N1	    |MN], union(M0,T1,MN).
 union(M0,M1,M) :- M0 = [H0,N0|T0], M1 = [H1,_ |_ ], H0  <  H1 |
     M = [H0,N0	    |MN], union(T0,M1,MN).
 union(M0,M1,M) :- M0 = [H0,N0|T0], M1 = [H1,N1|T1], H0 =:= H1 |
     M = [H0,~(N0+N1)|MN], union(T0,T1,MN).

5.intersection/3

intersection/3では、2つのリストを順に見ていって、片方のリストにしか現
れない要素は無視し(1～4番目の節)、2つのリストに同じ要素がある場合に、
その要素と、要素数の小さい方を返す(5,6番目の節)ことで行っています。
union/3と同様に、ガード部の形を同じにして効率を上げています。

 intersection([],_ ,M) :- M = [].
 intersection(_ ,[],M) :- M = [].
 intersection(M0,M1,M) :- M0=[H0,_ |_ ], M1=[H1,_ |T1], H0  >  H1 |
		     intersection(M0,T1,M ).
 intersection(M0,M1,M) :- M0=[H0,_ |T0], M1=[H1,_ |_ ], H0  <  H1 |
		     intersection(T0,M1,M ).
 intersection(M0,M1,M) :- M0=[H0,N0|T0], M1=[H1,N1|T1], H0 =:= H1, N0 >= N1 |
     M = [H0,N1|MN], intersection(T0,T1,MN).
 intersection(M0,M1,M) :- M0=[H0,N0|T0], M1=[H1,N1|T1], H0 =:= H1, N0 =< N1 |
     M = [H0,N0|MN], intersection(T0,T1,MN).

6.difference/3

difference/3は、intersection/3と同様に行います。1つ目のリストにのみ現
れる要素はそのまま返し(2,4番目の節)、2つ目のリストにのみ現れる要素は無
視します(1,3番目の節)。また、同じ要素があった場合、その差を求めて、要
素が1個以上残るならば、それを結果として返します(5,6番目の節)。ここでも
union/3と同様、ガード部の形を同じにして効率を上げています。

 difference([],_ ,M) :- M = [].
 difference(M0,[],M) :- M = M0.
 difference(M0,M1,M) :- M0=[H0,_ |_ ], M1=[H1,_ |T1], H0  >  H1 |
			   difference(M0,T1,M ).
 difference(M0,M1,M) :- M0=[H0,N0|T0], M1=[H1,_ |_ ], H0  <  H1 |
     M = [H0,N0      |MN], difference(T0,M1,MN).
 difference(M0,M1,M) :- M0=[H0,N0|T0], M1=[H1,N1|T1], H0 =:= H1, N0 >  N1 |
     M = [H0,~(N0-N1)|MN], difference(T0,T1,MN).
 difference(M0,M1,M) :- M0=[H0,N0|T0], M1=[H1,N1|T1], H0 =:= H1, N0 =< N1 |
			   difference(T0,T1,M ).

7.contraction/2

contraction/2では、リスト中の全ての「要素数」の項目を1にする処理を行っ
ています。

 contraction([]     ,M) :- M = [].
 contraction([H,_|T],M) :- M = [H,1|MN], contraction(T,MN).

8.choose/3

choose/3で取り出す要素は、最初の要素とします。また、その要素を除いた残
りのマルチ集合としては、最初の要素の数を1つ減らした集合になります。た
だし、要素数が0の要素があってはいけないので、最初の要素の数が1個だった
場合は、その要素自体を無くします。

 choose([H,1|T],E,S) :-         E = H, S = T.
 choose([H,N|T],E,S) :- N > 1 | E = H, S = [H,~(N-1)|T].

