OBJS	= 	cgs.o load.o send.o startDebate.o startSolve.o sort.o \
		check.o gui.o proPool.o set.o util.o runComParser.o run.o

DBDIR		= 	$(KLICDIR)/DB

all 		:	$(OBJS)

clean		:	
			/bin/rm -f  *.o *.ext *.c *.h *.db

cgs.o  		:	cgs.kl1
			klic -x$(DBDIR) -c cgs.kl1
load.o  	:	load.kl1
			klic -x$(DBDIR) -c load.kl1
send.o  	:	send.kl1
			klic -x$(DBDIR) -c send.kl1
startDebate.o  	:	startDebate.kl1
			klic -x$(DBDIR) -c startDebate.kl1
startSolve.o  	:	startSolve.kl1
			klic -x$(DBDIR) -c startSolve.kl1
check.o  	:	check.kl1
			klic -x$(DBDIR) -c check.kl1
gui.o  		:	gui.kl1
			klic -x$(DBDIR) -c gui.kl1
proPool.o  	:	proPool.kl1
			klic -x$(DBDIR) -c proPool.kl1
set.o  		:	set.kl1
			klic -x$(DBDIR) -c set.kl1
util.o 		:	util.kl1
			klic -x$(DBDIR) -c util.kl1
runComParser.o 	:	runComParser.kl1
			klic -x$(DBDIR) -c runComParser.kl1
run.o		:	run.kl1
			klic -x$(DBDIR) -c run.kl1
sort.o		:	sort.kl1
			klic -x$(DBDIR) -c sort.kl1


