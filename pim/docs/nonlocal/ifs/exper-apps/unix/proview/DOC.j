蛋白質立体構造表示システム

　概略

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


１、３次元グラフィックス表示システム

１、１、機能

　(1) 3D-Talkを翻訳して、グラフィックオブジェクトを表示する。3D-Talkの
      詳細は別途リファレンスマニュアルを参照して下さい。

　(2) マウスによる回転、移動、拡大・縮小が可能である。      

　(3) コントロールパネルでの、詳細な調整が可能である。


１、２、モジュール　3dview

(1) トップ・ソース・ファイル名
　main.c

(2) ロード・ファイル名
　3dview

(3) 参照モジュール
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


１、３、実行例

DOC.pia を参照して下さい。



２、蛋白質立体構造表示システム

２、１、機能

  　(1) PDB(Protein Data Bank)より、立体構造情報を読み込み、3D-Talkを
        生成する。この時、3D-Talkは標準出力に出力される。

  　(2) 3D-Talkを拡張したProtein-Talkを使用することにより、蛋白質の構
        造表示に特化した機能を実現できる。


２、２、モジュール　proview

(1) ソース・ファイル名
　proview/main.c

(2) ロード・ファイル名
　proview

(3) 参照モジュール
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


２、３、実行例

DOC.tpia を参照して下さい。


