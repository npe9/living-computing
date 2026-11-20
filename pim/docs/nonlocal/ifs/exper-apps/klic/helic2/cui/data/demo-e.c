compile   goal demo-e.goal
load p type demo-e.t
compile p rule demo-e.rule
compile p pom demo-e.pom
load d type demo-e.t
compile d rule demo-e.rule
compile d pom demo-e.pom
set    gp 5
set  p solver system
set  d solver system
set  p unit sympo15
set  d unit sympo15
set  p sp 
set  d sp 

