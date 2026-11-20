3. 知識の作成と追加

   細胞内信号伝達経路情報はmicro-Quixoteを用いて記述する。
 インターフェース部から「物質Aが細胞に到着すると何がおこるか」という
 queryを受けとると、micro-Quixoteは物質Aから細胞内にシグナルが伝えられ
 る経路を生成し、answerとして返す。
 インターフェース部はこのanswerを解析してシグナル伝達経路を視覚的に画
 面表示する（micro-Quixoteの文法、操作方法についてはmicro-Quixoteのマ
 ニュアルを参照すること）。


3.1.プログラム

 Quixoteプログラムはオブジェクトセクションとルールセクションから構成さ
 れる。
 この細胞内反応知識ベースでは、オブジェクトセクションには化学反応に関
 係する物質間の関係や、反応場所（組織、細胞など）の関係を記述し、ルー
 ルセクションには細胞内の化学反応（ファクト）と一連の化学反応をpathway
 に導くルールなどを記述している。

3.1.1.オブジェクトセクション

  生体内の化学物質をその種類に従って、階層関係を記述する。
  また、反応の場である細胞と、属している器官の関係も記述する。
  以下の例では、"INF-gamma"はinterferonの一種であり、
  interferon は interleukinとともにcytokineに含まれることを示している。

    cytokine >= {interleukin,interferon};;
    interferon >= "INF-gamma";;

3.1.2.ルールセクション

    生体内の化学反応をファクトとして記述し、それらのファクトから一連の
  pathwayを導くルールを記述する。

3.1.2.1.pathwayを導くルール

    pathwayを導くルールは以下のようになっている。

  (1) 2つの反応をつなぐ。

     state[now=Now,next=Next]
         <= Now/[result=Next];;

     このルールにより、nextの値はオブジェクトNowの属性resultの値になる。
   例えば、Nowが

     activate[name=kinase]

   であり、ファクト

     activate[name=kinase]/
            [result=phsophorylate[name="MAP"]];;

   が存在している時、Nextは

     phsophorylate[name="MAP"]

   となる。
   このようにして2つのファクトをpathwayとしてつなぐことができる。

  (2) 反応をリストにおさめる。

     path[stage=X,next=Y,path=P]
         <= state[now=X,next =Y1],
            path[stage=Y1,next=Y,path=P2]
         ||{P==state[now=X,next=P2]};; 

     先のstate[now=X,next =Y1]により、Xという反応から次々に集められ
   たresultの値は、上記のルールによりPに再帰的にリストにおさめられて、
   一連のpathwayが生成される。
     ただし、このルールのみではpathwayの終点がわからないため、A→Dとい
   うpathを求めるqueryがあった場合にA→B、A→B→C、A→B→C→D とAを始
   点とするpathが全てanswerとして返されてしまう。これを避けるために、
   pathwayの最後の反応には、ファクトの記述で属性 resultの値に「end」と
   いう値を明示しておく。

     infiltrate[name=eosinophil]/[result=end];;

   こうしておくと、次のルールにより属性nextの値が end になった時にリス
   トが閉じられる。

     path[stage=X,next=Y,path=P]
	 <= state[now=X,next =Y1]
        ||   {Y1==end,Y==X,P==X};;

   以上のようにして、一連の化学反応のpathwayをリストの形で求めることが
   できる。

3.1.2.2. 化学反応の表現

     A→B→C→D→Eの一連のpathwayは次のような化学反応の記述の羅列によっ
   て表す。

       A/[result=B];;
       B/[result=C];;
       C/[result=D];;
       D/[result=E];;

   pathwayに属する反応の全てが解明されているとは限らないので、この場合
   のresultに入る現象は'/'の左側の部分の反応の直接の結果である必要はな
   く、pathwayでその反応より下流にある現象が入る。
   現在わかっている反応を羅列していけば、1に述べたルールによって自動的
   にpathwayが導かれる。
   そして、後にB→Cの詳細が判明しB→B'→Cであることがわかったような場
   合には、

       B/[result=B'];;
       B'/[result=C];;
       C/[result=D];;

   のように修正することができる。

  (1)基本形
 
     化学反応は基本的には以下のような形で表す。

       化学反応名[name=化学反応の対象となっている物質名]/
                 [result=反応の結果];;

   反応の結果には、「物質が生成される」「ある遺伝子に結合する」などの
   現象がはいる。結果の部分も上の基本形のヘッドの部分（'/'の左側の部分）
   と同様の表現で表す。
   例えば、kinaseがactivate（活性化）されたという現象は以下のように表す。

      activate[name=kinase];;

   そして、活性kinaseが"MAP kinase"をphosphorylateすることは、次のよう
   に記述する。

      activate[name=kinase]/[result=phosphorylate[name="MAP kinase"]];;

   この、phosphorylate （リン酸化）されたMAPが物質Aをactivateする場合、
   表現は以下のようになる。

     phosphorylate[name="MAP"]/[result=activate[name="A"]];;

   この時、属性resultの値が次に起こる反応を表すファクトのヘッドと同じ
   になるようにする。こうすることにより、3.1.2.1.で述べたルールによっ
   て化学反応のpathwayを導くことができる。

  (2)反応の制約

     生体内の反応は、反応が起きた場所や時期によって結果が異なることが
   多い。反応場所などの条件でパスの流れを変えられるようにするには、上
   記の基本形のヘッドにplace、timeなどの条件を加える。
   例えば、反応がヒトの細胞でのみ起こることを表したい場合は、場所を示
   す属性placeに制約をつける。

       inactivate[name="Rb",place=human_cell];;

   こう書くことにより、placeの値にplantなどが入っている場合にはヒトの
   細胞内反応のpathwayは導かれなくなる。

  (3)ある条件のもとで起こるファクトの表現

     ある反応が、特定の条件が成立している場合にのみ起こる現象は、ルー
   ルのbody部に条件となるオブジェクトを列挙することによって表現する。
   そして、body部に書いたオブジェクトを別にファクトとして記述しておく。

      differentiate[name="B cell"]/
           [result=receive[name="IL4,IL5,IL6",place="B cell"]]
           <= arrive[name="IL4"],
              arrive[name="IL5"],
              arrive[name="IL6"];;

      arrive[name="IL4"];;
      arrive[name="IL5"];;
      arrive[name="IL6"];;

   上記は、「"IL4"、"IL5"、"IL6"の3種類の物質を受けとった時に"B cell"
   は分化する」ということを表している。


  (4)遺伝子の制御エレメント部分

     遺伝子の制御エレメントと、そのエレメントにより発現されるタンパク
   質については、次のように表現する。

       gene[name=制御エレメント名 , coded = 発現されるタンパク質];;

   [例]
       gene[name="SRE",coded="c-fos"];;
       gene[name="TRE",coded="G1cyclin"];;

   遺伝子の制御エレメントに分子が結合した結果、タンパク質が発現される
   現象は次のように表している。

      bind_element[name=X]/
           [result=express[name=Y]]
           <=gene[name=X,coded=Y];;

   例えば、"SRE"に制御タンパクが結合した場合のqueryとanswerはこのよう
   になる。

      ?- bind_element[name="SRE",place=human]/[result=X].
      yes.
      X = express[name="c-fos",place=human]

  (5)pathway記述の具体例
 
     「すい臓β細胞がグルコースを受け取り、インシュリンを分泌する」と
   いう現象を記述してみる。

   a.オブジェクトセクションにすい臓β細胞について記述する。
     グルコースを受け取ってインシュリンを分泌する細胞はすい臓のβ細胞
   なので、β細胞をinsulin_secretory_cellよりも下位にあることを記述し
   ておく。

       insulin_secretory_cell >= {beta_cell};;

   b.反応を記述する。

      receive[name="glucose",place=P]
         /[result=activate[name="GLUT2",place=P,
                           long_name="glucose transporter 2"]]
         |{P =< insulin_secretory_cell};;

     インシュリンを分泌するのはすい臓のβ細胞だけなので、反応の起こる
   場所placeに制約をかけておく。この制約により、他の種類の細胞にグルコー
   スが来た時と反応が区別されるようになる。
     次に、"GLUT2"がacitivateされた結果を書く。

     activate[name="GLUT2",place=P,long_name="glucose transporter 2"]
         /[result = intake[name= "glucose",place=P]]
         |{P =< insulin_secretory_cell};;

   以上のようにして、化学反応を記述していく。pathwayの最後のインシュリ
   ンを分泌するという現象では、pathwayの終りを示すフラグを立てておく。

       secrete[name="insulin",place=P]/
	      [result= end ];;

   以上の記述により以下のようなquery&answerをmicro-Quixoteで行なうこと
   ができるようになる。

   [実行例]

  ?- arrive[name="glucose",place=beta_dell]/[path= Path,result=Result].
  ?- yes.
  Path = state[now=receive[name=glucose,place=beta_cell],
             next=state[now=activate[name="GLUT2",long_name="glucosetransporter 2",
                                     place=beta_cell],
             next=state[now=intake[name=glucose,place=beta_cell],
             next=state[now=phosphorylate[name=glucose,enzyme=glucokinase,
                                          place=beta_cell],
             next=state[now=produce[name="G6P",long_name="glucose-6-phosphate",
                                    place=beta_cell],
             next=state[now=activate[name="TCA cycle",input="G6P",place=beta_cell],
             next=state[now=produce[name="ATP",long_name="adenosine 5'-triphosphate",
                                    place=beta_cell],
             next=state[now=suppress[name="K ATP channel",
                                     long_name="ATP dependant K+ channel",
                                     place=beta_cell],
             next=state[now=depolarize[name="VDCC",
                                       long_name="voltage dependant Ca++ channel",
                                       place=beta_cell],
             next=state[now=increase[name="Ca++",place=beta_cell],
             next=secrete[name=insulin,place=beta_cell]]]]]]]]]]], 
  Result = secrete[name=insulin,place=beta_cell]

   β細胞のようなインシュリン分泌細胞でのみこの反応が起こるので、以下
   のように、placeにinsulin_secretory_cellではないオブジェクトを入れて
   queryを出した場合はanswerにpathwayは返ってこない。

    ?- arrive[name="glucose",place=epidermis]/[path= Path,result=X].
    no.

3.1.2.3. pathwayが分岐する場合

     今まではpathwayが一直線の場合だったが、実際の反応では反応に関わる
   物質が複数あって途中で分岐する場合が多い。ここではそのような反応を
   どう表現するかを述べる。
     ある反応Aの結果pathwayが分岐する場合、まず分岐した結果それぞれに
   ついてのpathwayを作り、各pathwayの始点をAにつなげることによって、
   pathwayの分岐を表現している。

  (1) 分岐した各pathwayについて、一連の反応を記述する。

  (2) 分岐した各pathwayの始点を元の反応につなげる。

     これは、分岐元の反応pを次のように表現することによって行なう。

       p/[result=q[names=list[element1=A,element2=B]]];;

   A , Bにそれぞれ分岐する反応の主体となる物質名をいれる。q[name=A]と
   q[name=B]それぞれを始点とする、一連の反応は(1)で先に記述しておく。

  (3) q[names=list[element1=A,element2=B]]をヘッドとするオブジェクトを
      書く。

     このオブジェクトのresultの値は、

       list[path1=Path1,result1=R1,path2=Path2,result2=R2]]

   となる。listの属性path1とpath2の値には分岐した後の各pathwayが入り、
   result1、result2の値には各pathwayの終点が入る。

    q[names = list[element1=A,element2=B]]/
         [result=list[path1=Path1,result1=R1,
                      path2=Path2,result2=R2]]
         <= path[stage=q[name=A],
                 next=R1,path=Path1],
            path[stage=q[name=B],
                 next=R2,path=Path2];;

  (4) list[path1=P1,result1=R1,path2=P2,result2=R2]をヘッドとするオブ
     ジェクトを書く。

     result1とresult2の値について制限項をつけることによって、resultの
   値が決まる。

     list[path1=P1,result1=R1,path2=P2,result2=R2]/
         [result = ResultOfList]
         | {R1==ResultOfPath1,
            R2==ResultOfPath2};;

   以上のようにして、一つの反応pから分岐した複数のpathwayを再び一つに
   まとめることができる。

  (5)具体例

     adenovirus （ガンウイルスの一種）が細胞に感染し、"EIA"と"EIB"という
   2種類のタンパク質を生産し、各々が細胞内の物質に結合した結果発ガンす
   るという現象を例にとって説明する。

   (a) 分岐する部分を書く

     arrive[name="adenovirus"]/
           [result=synthesize[names =
            list[element1="EIA",element2="EIB"]]];;

     これは、"adenovirus"が到着した結果、"EIA"と"EIB"の2種類の物質が生
   成されることを表している。

   (b) 分岐後の各pathwayを書く

      produce[name="EIA"]とproduce[name="EIB"]それぞれを始点とする反応
    のファクトを記述しておく。

       produce[name="EIA"]/
           [result=bind[name="EIA",to="Rb"]];;
                ・
                ・
       produce[name="EIB"]/
           [result=bind[name="EIB",to="p53"]];;
                ・
                ・

   (c) 分岐したpathwayを一つにまとめる

     (a)のlist[element1="EIA",element2="EIB"]をヘッドとするオブジェク
   トを書く。Aを始点とするpathwayの終点result1、Bを始点とするpathwayの
   終点result2の値について制限項をつけることによって、resultの値が決ま
   る。

    list[path1=P1,result1=R1,path2=P2,result2=R2]/
        [result=results[result=inactivate[name = "Rb and p53",
                                          place=human_cell]]]
       |{R1==inactivate[name="Rb",place=P],
         R2==inactivate[name="p53",place=P]};;

   このように記述していくことにより、一つの反応Aから分岐した複数の
   pathwayを再び一つにまとめることができる。
  「アデノウイルスが感染すると発ガンする」という一連の反応は以下のよう
  なqueryで求められる。

  [実行例]

   ?- infect[name="adenovirus"]/[result=Result,path=Path].
   yes.
   Result = cancer_growth, 
   Path = state[now=arrive[name=adenovirus,place=human_cell],
                next=state[now=synthesize[place=human_cell,
                                names=list[element1="EIA",element2="EIB"]],
                next=state[now=list[
                  path1=state[now=produce[name="EIA",place=human_cell],
                              next=state[now=bind[name="EIA",to="Rb",place=human_cell],
                              next=inactivate[name="Rb",place=human_cell]]],
                  result1=inactivate[name="Rb",place=human_cell],
                  path2=state[now=produce[name="EIB",place=human_cell],
                              next=state[now=bind[name="EIB",to=p53,place=human_cell],
                              next=inactivate[name=p53,place=human_cell]]],
                  result2=inactivate[name=p53,place=human_cell]],
                next=state[now=results[result=inactivate[name="Rb and p53",
                                                         place=human_cell]],
                next=state[now=inactivate[name="Rb and p53",place=human_cell],
                next=state[now=activate[name="s-gene",status=uncontrolled,
                                        place=human_cell],
                next=cancer_growth]]]]]]


3.1.2.4. query用のルール

     3.1.2.1.で述べた、pathwayを導くルールをそのまま以下のようにquery
   に使用すればpathwayを求めることができる。

    ?- path[stage=receive[name="NMDA",long_name="N-methyl-D-aspartate",
			       place=hippocampus],next=N,path=Path].

   この queryを出すと、stageから以降の反応がPathに、Nに最終結果が返っ
   てくる。
     しかし、上記のように反応にlong_name、placeなど属性が多く記述され
   ているqueryでは、単純なタイプミスなどでanswerを得られなくなることが
   ある。
   そこで、「物質Aが細胞Bに到着した」のような、一連のpathwayの始点とな
   るような現象をヘッドとするpathwayを求めるルールをquery用にあらかじ
   め作っておく。

   [例]
     arrive[name=antigen,place=P]/[path=Path,result=R]
	  | {P =< "APC"} 
	  <= path[stage=receive[name=antigen,place=P],
		  next=R,
		  path=Path];;

   このルールによって、APCにantigenが来た時に起こるpathwayはPathに、最
   終結果はRに返ってくる。

   データベースには「%for query」のようなコメントをつけてこのようなquery
   用のルールを用意しておく。
   実際のqueryでは以下のようになる。

  [実行例]
  ?- arrive[name=antigen,place="APC"]/[path=Path,result=Result].
  yes.
  Result = "allergic reaction", 
  Path = state[now=receive[name=antigen,place="APC"],
               next=state[now=activate[name="helper T-cell"],
               next=state[now=secrete[name="IL3,IL4,IL5,IL10",place="helper T-cell"],
               next=state[now=accept[names=list[element1="IL4,IL5",element2="IL5"]],
               next=state[now=list[
                 path1=state[now=receive[name="IL4,IL5",place="B-cell"],
                             next=state[now=secrete[name="IgE",
                                                    long_name="immunogloblin E",
                                                    place="B-cell"],
                             next=state[now=arrive[name="IgE",
                                                   long_name="immunogloblin E",
                                                   place="mast cell"],
                             next=state[now=bind[name="IgE",
                                                 to="IgE specific Fc receptor",
                                                 place="mast cell"],
                             next=state[now=compound[name=cell_surface_receptor,
                                                     with=antigen,place="mast cell"],
                             next=state[now=bind[name=antigen,to=cell_surface_receptor,
                                                 place="mast cell"],
                             next=state[now=cross_link[name=antigen,place="mast cell"],
                             next=state[now=exocytosis[name="mast cell"],
                             next=secrete[name=histamine,place="mast cell"]]]]]]]]],
                 result1=secrete[name=histamine,place="mast cell"],
                 path2=state[now=receive[name="IL5",place=eosinophil],
                             next=state[now=release[name=mediator,place=eosinophil],
                             next=infiltrate[name=eosinophil]]],
                 result2=infiltrate[name=eosinophil]],
               next=state[now=results[result="allergic reaction"],
               next="allergic reaction"]]]]]]


   この他に、pathwayの始点と終点を指定してpathwayを導くルールもある。

    pathToEnd[stage=X,next=Y,path=P]
	<= &true || {X==Y,P==Y};;

    pathToEnd[stage=X,next=Y,path=P]
	<= state[now=X,next =Y1],
	   pathToEnd[stage=Y1,next=Y,path=P2]
	   || {P==state[now=X,next=P2]};;

   このルールを用いて、以下のようなqueryを出すことができる。

     ?- pathToEnd[stage= differentiate[name="lymphoid stem cell"],
	          next= differentiate[name="T-cell"],path=Path].

   これは、 "lymphoid stem cell"から "T-cell"に分化するまでのpathwayを
   求めるqueryである。

3.1.2.5.知識の追加

   (1) 記述済みのpathwayの一部を変更する場合

       A→B→C→D→E

     というpathwayがすでに記述されていて、その中の B→C という反応がさ
   らに詳しく B→B'→C という反応であるということを新たに追加したい場合は、

      B/[result=C];;

   という記述を

      B/[result=B'];;
      B'/[result=C];;

   と書き換える。

   (2) 記述済みのpathwayと一部を共有する場合

     細胞内のシグナル伝達は、レセプター−リガンドの組合せは異なってい
   ても、細胞内部での経路は共通である場合が多い。新たに追加するpathway
   が、すでに知識ベースに登録されているpathwayと共通の部分がある場合は、
   共通部分を利用できるように書く。

     既に書かれているpathway  A→B→C→D→E→F
     新たに追加したいpathway  P→Q→C→D→E→R

   このような場合は、

      P/[result=Q];;
      Q/[result=C];;
      E/[result=R];;

   というように共通部分（C→D→E）への入口と出口の部分の反応を書く。た
   だし、P→Q→C→D→E→F あるいは A→B→C→D→E→R といったpathwayの
   “混線”を避けるために、反応場所等で制約をかけるようにする。

  [例]
     アドレナリン（adrenalin）と甲状腺刺激ホルモン（TSH）は両方とも細
   胞膜のGs proteinを介して細胞内に作用する。Gs proteinの活性化からPKA
   の増加までのpathwayは同じなので、アドレナリン受容後の細胞内反応が既
   に記述されている場合は、甲状腺刺激ホルモン→Gs Proteinまでの反応と、
   PKA→甲状腺ホルモン分泌の反応を書けばいい。

    %アドレナリンを受容した"skeltal muscle cell"の反応

    receive[name="adrenalin",place=P]/
         [result=activate[name="G protein(Gs)",place=P]]
        |{P=="skeltal muscle cell"};;

    %甲状腺ホルモンを受容した"thyroid gland"の反応

    receive[name="TSH",long_name="thyroid stimulating hormone",place="thyroid gland"]/
         [result=bind[name="TSH",to = "TSH receptor",place="thyroid gland"]];;
    bind[name="TSH",to = "TSH receptor",place="thyroid gland"]/
         [result=activate[name="G protein(Gs)",place="thyroid gland"]];;

    % Gs protein活性化 〜 PKA活性化までの反応

    activate[name="G protein(Gs)",place=P]/
         [result = activate[name="adenylyl cyclase",place=P]];;
    activate[name="adenylyl cyclase",place=P]/
         [result=produce[name="cAMP",long_name="cyclic AMP",place=P]];;
    produce[name="cAMP",long_name="cyclic AMP",place=P]/
         [result=increase[name="cAMP",place=P]];;
    increase[name="cAMP",place=P]/
         [result=activate[name="PKA",long_name="cAMP-dependent protein kinase A",
                          place=P]];;

    %PKA活性化以後は属性placeの値（"skeltal muscle cell"か"thyroid gland"か）に
    %従って反応が分かれる。

    %PKA活性化以後のアドレナリンを受容した"skeltal muscle cell"の反応

    activate[name="PKA",long_name="cAMP-dependent protein kinase A",place=P]/
         [result= phosphorylate[name="phosphorylase kinase,glycogen synthase",place=P]]
        | {P=="skeltal muscle cell"}
        <= phosphorylate[name="phosphorylase kinase",place=P],
           phosphorylate[name="glycogen synthase",place=P];;
    phosphorylate[name="phosphorylase kinase,glycogen synthase",place=P]/
         [result=increase[name=glucose,location="inside cell",place=P]]
        |{P == "skeltal muscle cell"};;

    %PKA活性化以後の甲状腺ホルモンを受容した"thyroid gland"の反応

    activate[name="PKA",long_name="cAMP-dependent protein kinase A",place=P]/
         [result= produce[name="thyroid hormon",place=P]]
        | {P=="thyroid gland"};;
    produce[name="thyroid hormon",place=P]/
         [result=secrete[name="thyroid hormon",place=P]]
        | {P=="thyroid gland"};;


3.1.2.6 記述に用いている単語

  記述に用いている単語と化学反応との対応は以下の通り。


name                       反応の主体となる物質の名前。略語で表しても
                           よい。
long_name                  nameの一般的な表記。name="DNA"ならば
                           long_name="deoxyribonucleic acid"。
to                         反応bindでnameが結合する物質。
from                       反応unbindでnameが離れる物質。
with                       反応compoundでnameが結合して化合物を一緒に
                           生成する物質。
place                      反応がおきている場所。主として細胞／組織の
                           種類がはいる。
location                   反応translocateの結果nameが細胞内で移動した
                           場所。
enzyme                     反応に関連している酵素。
time                       反応が起きた時期。
status                     反応が起きた時の、細胞／レセプターの状態。


begin                      一連の反応が始まる。ある反応が複数の時期に
                           分けられるような場合、特定の時期に入る。
[例]
    begin[name="G2-period",place=P]/
	 [result=activate[name="Cdc25 phosphatase",place=P]];;

duplicate                  DNA、RNAを複製する。
[例]
    duplicate[name="DNA",long_name="deoxyribonucleic acid",place=P]/
	 [result=phosphorylate[name="Cdc2 kinase",place=P]];;

receive                    細胞が外部から物質／シグナルを受け取る。
[例]
    receive[name="insulin",place=P]
	/[result=activate[name="IRTK",long_name="insulin receptor tyrosine kinase",
			 place=P]]
	|{P =< insulin_target_cell};;

arrive                     組織／細胞／細胞内器官に物質／シグナルが到
                           着する。
[例]
    arrive[name="SV40",place=P]/
	 [result=produce[name="T-antigen",place=P]];;

activate                   細胞／生体内物質が活性化する。
[例]
    activate[name="S6 kinase2",place=P]
	/[result=activate[name="PP1",long_name="protein phosphatase 1",place=P]];;

inactivate                 細胞／生体内物質が不活性化する。
[例]
    inactivate[name="glycogen synthase",place=P]/
	 [result=suppress[name="glycogen synthesis",place=P]]
	|{P == "skeltal muscle cell"};;

phosphorylate              生体内物質がリン酸化される。
[例]
    phosphorylate[name= "phosphorylase kinase",place=P]/
	 [result=phosphorylate[name="glycogen phosphorylase",place=P]]
	| {P=="skeltal muscle cell"};;

bind_element               遺伝子の制御エレメントに分子が結合する。
[例]
    bind_element[name="TRE",place=P];;

express                    遺伝子が発現する。
[例]
    express[name="late response gene",place=hippocampus]/
	 [result=increase[name="LTP",
			 long_name="long-term potentiation",
			 place=hippocampus]];;

produce                    生体内物質が生成される。
[例]
    produce[name="AP-1",place=P]/
	 [result=bind_element[name="TRE",long_name="TPA response element",place=P]];;

intake                     ある物質が細胞内に取り込まれる。
[例]
    intake[name="glucose",place = P]
	/[result=phosphorylate[name = "glucose",enzyme = "glucokinase",place = P]]
	|{P =<insulin_secretory_cell};;

suppress                   反応／特定の物質の活性が抑制される。
[例]
    suppress[name="K ATP channel",long_name="ATP dependant K+ channel",place=P]
	/[result=depolarize[name="VDCC",
			    long_name="voltage dependant Ca++ channel",place=P]]
	|{P =<insulin_secretory_cell};;

depolarize                 細胞膜のチャンネルが脱分極する。
[例]
    depolarize[name="VDCC",long_name="voltage dependant Ca++ channel",place=P]
	/[result=increase[name="Ca++",place=P]];;

secrete                    ある物質が分泌細胞／器官から分泌される。
[例]
    secrete[name = "INF-gamma",long_name="gamma interferon",place="TH1 cell"]/
	 [result = suppress[name=produce[name="IgE",
					 long_name="immunogloblin E"],
			    place="B-cell"]];;

increase                   生体内物質が増加する。
[例]
    increase[name="Ca++",place=P]
	/[result=secrete[name="insulin",place=P]]
	|{P =<insulin_secretory_cell};;

decrease                   生体内物質が減少する。
[例]
    decrease[name="cGMP",long_name="cyclic GMP",place="rod"]/
	 [result=unbind[name="cGMP",long_name="cyclic GMP",
			from="cGMP-gated cation channel",
			place="rod"]];;

translocate                物質の細胞内での位置が変わる（染色体異常で
                           いう“転座”とは別）。
[例]
    translocate[name="GLUT4",location = "cell membrane",place=P]
	/[result=intake[name="glucose",location = "inside cell",place=P]];;

unbind                     物質の結合が切れる。結合していた先はfromで
                           示した物質。
[例]
    unbind[name="E2F",from="Rb",place=P]/
	 [result=activate[name="s-gene",status=uncontrolled,place=P]];;

bind                       物質が他の物質に結合する。結合先はtoで示し
                           た物質。
[例]
    bind[name="Ca++",to=calmodulin,place=P]/
	 [result=activate[name="Ca++/calmodulin",place=P]];;

hydrolyze                  物質が加水分解される。
[例]
    hydrolyze[name="cGMP",long_name="cyclic GMP",place="rod"]/
	 [result=decrease[name="cGMP",long_name="cyclic GMP",place="rod"]];;

infect                     ウイルスが細胞に感染する。
[例]
    infect[name=X]/[result=R,path=Path]
	<=infect[name=X,place=human_cell]/[result=R,path=Path];;


form                       物質が結合、二量化などで生成される。
[例]
    form[name="DHT-AR",time=T]/[result=activate[name="DHT-AR",time=T]];;

compound                   物質がwithで示した物質と結合して化合物を生
                           成する。
[例]
    compound[name="c-fos",with="c-jun",place=P]/
	 [result=produce[name="AP-1",place=P]];;

become                     分化の結果ある状態になる。
[例]
    become[name=female];;

release                    細胞が物質を細胞外に放出する。% secreteとの違いは？
infiltrate                 浸潤をおこす。
[例]
    release[name= mediator , place = eosinophil]/
	 [result = infiltrate[name=eosinophil]];;

cross_link                 細胞表面の複数のレセプターにリガンドが結合
                           する。
[例]
    cross_link[name="antigen",place="mast cell"]/
	 [result=exocytosis[name="mast cell"]];;

develope                   発生・分化の過程である器官が発達する。
[例]
    develope[name="Mullerian duct",time=T]/[result=become[name=female]]|
	{T =< fetus};;

involute                   発生・分化の過程である器官が退縮する。
[例]
    involute[name="Wolffian duct",time=T,status=ar_receptor_broken]/
	 [result=become[name=female]]|
	{T =< fetus};;

differentiate              細胞・器官が分化する。
[例]
    differentiate[name="B cell"]/
	 [result=differentiate[name="plasma cell"]]

pathwayの分岐を示すため、以下の3語は後に必ず
[resutl=list[elemnt1=E1,element2=E2]]が来る

synthesize                 2種類の物質が生成される。
[例]
    synthesize[names = list[element1="EIA",element2="EIB"],place=P]/
	 [result=list[path1=Path1,result1=R1,
		      path2=Path2,result2=R2]];;

energize                   2種類の物質が活性化される。
[例]
    energize[names =list[element1="Grb2/Ash",element2="small G protein"],place=P]
	/[result=list[path1=Path1,result1=R1,
		     path2=Path2,result2=R2]];;

accept                     2種類の物質を受け取る。
[例]
    accept[names=list[element1="IL4,IL5",
		       element2="IL5"]]/
	 [result = list[path1=Path1,result1=R1,
		      path2=Path2,result2=R2]]


3.2. 参考

 ・ micro-Quixoteが出力するanswerの構文

  <answer_list>   ::= <answer>
                    | <answer> ',' <answer_list>
                    | <answer> '\n' <answer_list>
  <answer>        ::= <upper-string> '=' <o-term>
  <o-term>        ::= <lower-string>
                    | <b-term>'[' <attr-list> ']'
                    | <string>
  <attr-list>     ::= <attribute>
                    | <attribute>','<attribute-list>
  <attribute>     ::= <a-label> '=' <o-term>
  <a-label>       ::= now | next | stage | name | names | element1 
                    | element2 | to | with | result | path | path1 
                    | path2 | place | input | location | enzyme |time |status 
                    | long_name | from
  <b-term>        ::= state | begin | duplicate | receive 
                    | activate | increase | phosphorylate | bind_element
                    | express | produce | results | intake | suppress
                    | depolarize | secrete | decrease | list | translocate
                    | inactivate | unbind | hydrolyze | infect | bind | form
                    | compound | become   | release | infiltrate 
                    | cross_link | exocytosis | synthesize | energize
                    | develope | involute | differentiate

  上記の内、<b-term>は主としてシグナル伝達経路上の化学反応を表し、
  <a-label>は化学反応の主体となる物質名（nameで指す）や伝達経路上の前
  後関係（now,next）などを表す。インターフェース部は<a-label>と
  <b-term>から各々に対応したウィジェットを自動的に生成し、画面上に配置
  するので、answerとして出力される部分に上記の<a-label><b-term>以外の
  アトムが含まれないようにする。


