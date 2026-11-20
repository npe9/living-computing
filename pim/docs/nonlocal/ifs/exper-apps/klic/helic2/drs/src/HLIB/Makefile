OBJS	= pool.o stio.o stdin.o stdout.o stdinter.o stdio.o \
	  kb.o getlUtil.o file.o buffer.o hlib.o 

DB		= 	$(SRC)/DB

all 		:	$(OBJS)

clean		:	
			/bin/rm -f  *.o *.ext *.c *.h *.db

stio.o		:	stio.kl1
			klic -x$(DB) -c stio.kl1
stdin.o 	:	stdin.kl1
			klic -x$(DB) -c stdin.kl1
stdout.o 	:	stdout.kl1
			klic -x$(DB) -c stdout.kl1
stdinter.o 	:	stdinter.kl1
			klic -x$(DB) -c stdinter.kl1
stdio.o 	:	stdio.kl1
			klic -x$(DB) -c stdio.kl1
kb.o		:	kb.kl1
			klic -x$(DB) -c kb.kl1
pool.o 		:	pool.kl1
			klic -x$(DB) -c pool.kl1
getlUtil.o 	:	getlUtil.kl1
			klic -x$(DB) -c getlUtil.kl1
file.o 		:	file.kl1
			klic -x$(DB) -c file.kl1
buffer.o 	:	buffer.kl1
			klic -x$(DB) -c buffer.kl1
hlib.o 		:	hlib.kl1
			klic -x$(DB) -c hlib.kl1
