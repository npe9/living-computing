蛋白質立体構造表示システム（C++）

１）プログラム概要

本システムは、タンパク質の立体構造情報をPDB(Protein Data Bank)より読み
込み、三次元グラフィックスで可視化するものである。
このシステムは汎用的３次元グラフィックス表示システム ``3D-View''と、蛋
白質構造表示のために特化した ``Protein-View''の２つからなる。
``3D-View'' は、誰もが簡単に３次元グラフィックスを作成できるように設計
されている。ユーザは ``3D-Talk''というオブジェクト指向の記述言語を記述
して、システムに送るだけで容易に３次元グラフィックスが得られるのである。
記述は、英語の文法を真似ており非常にわかり易いものとなっている。
表示された物体は、マウスによって回転、移動、拡大、縮小、変形等の操作を
することが可能である。また、コントロールパネルを使用することにより、物
体の色や解像度の変更等の細かい作業が可能となる。また、これらの動作は全
て、 ``3D- Talk''を用いても行うことができる。したがってアニメーションを
この言語で記述することも可能である。
``Protein-View'' は、 ``3D-Talk''を機能拡張したProtein-Talkを使用し、
PDB (Protein Data Bank)のデータを読み込み、立体構造を表示することが可
能である。このシステムは、蛋白質の立体構造を見易くするためのリボン表現
や、骨格のみを表示する機能、さらには、化学結合軸を回転して分子動力学シ
ミュレーションをアニメーション表現する機能なども持っている。
今後の蛋白質立体構造デザインや、分子動力学シミュレーションなどの幅広い
分野に利用できるシステムである。

２）プログラムの実行環境

本プログラムは,SGI社製IRIS上で実行することが可能である。基本的には全て
のIRISシリーズでの実行が可能だが、速度的な面でindigo ELAN以上での実行
の方がより望ましい。


３）ファイル名一覧

/proview
atom.c
atom.h
bond.c
bond.h
main.c
method.c
method.h
pdb.c
pdb.h
pdb_io.c
prtalk.c
prtalk.h
matrix/
	d3vector.c     eigenvalue.c   matrix.c
	d3vector.h     eigenvalue.h   matrix.h

/3dview
3dview.c       exit.h         lexical.c      object.c       sphere.c
accept.c       function.c     light.c        object.h       sphere.h
accept.h       function.h     light.h        objecttag.h    symbol.c
boolean.h      gorth.c        location.c     panel.c        symbol.h
box.c          gorth.h        location.h     panel.h        text.c
box.h          group.c        lyyerror.c     parse.tab.c    text.h
color_obj.c    group.h        main.c         parse.tab.h    token.h
color_obj.h    hash.c         make_name.c    parser.c       trackball.c
cylinder.c     hash.h         message.c      parser.h       trackball.h
cylinder.h     header.c       message.h      primitive.c    ui.c
data.c         header.h       messagetag.h   primitive.h    ui.h
data.h         initial.c      node.c         reduce.c       vect.c
event.c        instance.c     node.h         reduce.h       vect.h
event.h        lexbuffer.h    nvect.c        rotation.h


４）インストール概要

INSTALL.j を参照して下さい。


５）プログラムの機能説明と使用説明

DOC.j 、ディレクトリprtalkのドキュメントを参照して下さい


