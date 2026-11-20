load  type demo-e.t
compile  rule demo-e.rule
compile  pom  demo-e.pom
set   goal provable_guilty(a_object= take_away(agent=person[name=>"mary"],object=handbag[name=>"handbag1"],source=person[name=>"jane"]),goal=crime_of_theft)
set   unit sympo15
solve

