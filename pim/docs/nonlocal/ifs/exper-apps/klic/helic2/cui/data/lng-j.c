compile goal lng-j.goal
set gp 0
compile p type lng-j.type
compile p rule lng-j.rule
compile p pom lng-j.pom
set p solver system
set p unit all
set p sp
compile d type lng-j.type
compile d rule lng-j.rule
compile d pom lng-j.pom
set d solver system
set d unit all
set d sp
solve p
