OBJS    	=  	LArgUtil.o	cs.o		sense.o	showArgL.o \
			ael.o		ial.o		shell.o	showDisp.o \
			caUtil.o	isUtil.o	showArg.o	\
			svUtil.o 	showHelp.o


DB           	=       $(SRC)/DB

all             :	$(OBJS)

clean           :
			/bin/rm -f  *.o *.ext *.c *.h *.db

LArgUtil.o	:	LArgUtil.kl1
			klic -x$(DB) -c LArgUtil.kl1
cs.o		:	cs.kl1
			klic -x$(DB) -c cs.kl1
sense.o		:	sense.kl1
			klic -x$(DB) -c sense.kl1
showArgL.o 	:	showArgL.kl1
			klic -x$(DB) -c showArgL.kl1
ael.o		:	ael.kl1
			klic -x$(DB) -c ael.kl1
ial.o		:	ial.kl1
			klic -x$(DB) -c ial.kl1
shell.o		:	shell.kl1
			klic -x$(DB) -c shell.kl1
showDisp.o 	:	showDisp.kl1
			klic -x$(DB) -c showDisp.kl1
caUtil.o	:	caUtil.kl1
			klic -x$(DB) -c caUtil.kl1
isUtil.o	:	isUtil.kl1
			klic -x$(DB) -c isUtil.kl1
showArg.o	:	showArg.kl1
			klic -x$(DB) -c showArg.kl1
svUtil.o	:	svUtil.kl1
			klic -x$(DB) -c svUtil.kl1
showHelp.o	:	showHelp.kl1
			klic -x$(DB) -c showHelp.kl1
        

