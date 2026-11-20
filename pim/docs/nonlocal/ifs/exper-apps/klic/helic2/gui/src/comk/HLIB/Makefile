OBJS	= stio.o stdin.o stdout.o stdinter.o stdio.o \
	  kb.o pool.o getlUtil.o file.o buffer.o hlib.o 

DBDIR		= 	$(KLICDIR)/DB

all 		:	$(OBJS)

clean		:	
			/bin/rm -f  *.o *.ext *.c *.h *.db


stio.o		:	stio.kl1
			klic -x$(DBDIR) -c stio.kl1
stdin.o 	:	stdin.kl1
			klic -x$(DBDIR) -c stdin.kl1
stdout.o 	:	stdout.kl1
			klic -x$(DBDIR) -c stdout.kl1
stdinter.o 	:	stdinter.kl1
			klic -x$(DBDIR) -c stdinter.kl1
stdio.o 	:	stdio.kl1
			klic -x$(DBDIR) -c stdio.kl1
kb.o		:	kb.kl1
			klic -x$(DBDIR) -c kb.kl1
pool.o 		:	pool.kl1
			klic -x$(DBDIR) -c pool.kl1
getlUtil.o 	:	getlUtil.kl1
			klic -x$(DBDIR) -c getlUtil.kl1
file.o 		:	file.kl1
			klic -x$(DBDIR) -c file.kl1
buffer.o 	:	buffer.kl1
			klic -x$(DBDIR) -c buffer.kl1
hlib.o 		:	hlib.kl1
			klic -x$(DBDIR) -c hlib.kl1
