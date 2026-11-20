OBJS		=  	appstr.o	revTrans.o	siflib.o \
			hutil.o		setTb.o		substr.o

DB		= 	$(SRC)/DB

all 		:	$(OBJS)

clean		:	
			/bin/rm -f  *.o *.ext *.c *.h *.db

appstr.o	:	appstr.kl1
			klic -x$(DB) -c   appstr.kl1
revTrans.o	:	revTrans.kl1
			klic -x$(DB) -c   revTrans.kl1
siflib.o 	:	siflib.kl1
			klic -x$(DB) -c   siflib.kl1
hutil.o		:	hutil.kl1
			klic -x$(DB) -c   hutil.kl1
setTb.o		:	setTb.kl1
			klic -x$(DB) -c   setTb.kl1
substr.o	:	substr.kl1
			klic -x$(DB) -c   substr.kl1



