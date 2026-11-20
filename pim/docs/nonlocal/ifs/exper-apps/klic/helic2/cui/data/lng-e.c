compile goal lng-e.goal
set gp 0
compile p type lng-e.type
compile p rule lng-e.rule
compile p pom lng-e.pom
set p solver system
set p unit all
set p sp
compile d type lng-e.type
compile d rule lng-e.rule
compile d pom lng-e.pom
set d solver system
set d unit all
set d sp
solve p







