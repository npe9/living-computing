OBJS    	=  	netIo.o	 netRpar.o  netSnh.o \
			netRnh.o netShArg.o netShPom.o netShGl.o netSpar.o

DB           	=       $(SRC)/DB

all             :	$(OBJS)

clean           :
			/bin/rm -f  *.o *.ext *.c *.h *.db

netIo.o	        :	netIo.kl1
			klic -x$(DB) -c netIo.kl1
netRpar.o	:	netRpar.kl1
			klic -x$(DB) -c netRpar.kl1
netSnh.o        :	netSnh.kl1
			klic -x$(DB) -c netSnh.kl1
netRnh.o	:	netRnh.kl1
			klic -x$(DB) -c netRnh.kl1
netShArg.o	:	netShArg.kl1
			klic -x$(DB) -c netShArg.kl1
netShPom.o	:	netShPom.kl1
			klic -x$(DB) -c netShPom.kl1
netShGl.o	:	netShGl.kl1
			klic -x$(DB) -c netShGl.kl1
netSpar.o       :	netSpar.kl1
			klic -x$(DB) -c netSpar.kl1


