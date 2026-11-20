load    type demo-j.t
compile rule demo-j.rule
compile pom demo-j.pom
set     goal 立件する(a_object= 持ち去る(agent=人間[name=>"甲"],object=ハンドバッグ[name=>"ハンドバッグ1"],source=人間[name=>"乙"]),goal=窃盗罪)
set     unit sympo15
solve
