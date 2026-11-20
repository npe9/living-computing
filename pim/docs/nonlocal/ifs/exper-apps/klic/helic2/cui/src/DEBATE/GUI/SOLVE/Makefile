OBJS	= 	sl_caU.o	sl_isU.o	sl_shAL.o	sl_svU.o \
		sl_AU.o		sl_cs.o		sl_sense.o	sl_shD.o \
		sl_ael.o	sl_ial.o	sl_shA.o	sl_shell.o \
		sl_nShA.o	sl_nh.o		sl_nio.o	sl_npar.o \
		sl_shHlp.o


DB           	=       $(SRCDIR)/DB

all             :	$(OBJS)

clean           :
			/bin/rm -f  *.o *.ext *.c *.h *.db

sl_caU.o	:	sl_caU.kl1
			klic -x$(DB) -c sl_caU.kl1
sl_isU.o	:	sl_isU.kl1
			klic -x$(DB) -c sl_isU.kl1
sl_shAL.o	:	sl_shAL.kl1
			klic -x$(DB) -c sl_shAL.kl1
sl_svU.o	:	sl_svU.kl1
			klic -x$(DB) -c sl_svU.kl1
sl_AU.o		:	sl_AU.kl1
			klic -x$(DB) -c sl_AU.kl1
sl_cs.o		:	sl_cs.kl1
			klic -x$(DB) -c sl_cs.kl1
sl_sense.o	:	sl_sense.kl1
			klic -x$(DB) -c sl_sense.kl1
sl_shD.o	:	sl_shD.kl1
			klic -x$(DB) -c sl_shD.kl1
sl_ael.o	:	sl_ael.kl1
			klic -x$(DB) -c sl_ael.kl1
sl_ial.o	:	sl_ial.kl1
			klic -x$(DB) -c sl_ial.kl1
sl_shA.o	:	sl_shA.kl1
			klic -x$(DB) -c sl_shA.kl1
sl_shell.o	:	sl_shell.kl1
			klic -x$(DB) -c sl_shell.kl1
sl_nShA.o	:	sl_nShA.kl1
			klic -x$(DB) -c sl_nShA.kl1
sl_nh.o		:	sl_nh.kl1
			klic -x$(DB) -c sl_nh.kl1
sl_nio.o	:	sl_nio.kl1
			klic -x$(DB) -c sl_nio.kl1
sl_npar.o	:	sl_npar.kl1
			klic -x$(DB) -c sl_npar.kl1
sl_shHlp.o	:	sl_shHlp.kl1
			klic -x$(DB) -c sl_shHlp.kl1

