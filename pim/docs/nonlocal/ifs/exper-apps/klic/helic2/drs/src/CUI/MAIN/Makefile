OBJS    	=  	cui.o cuiCs.o cuiPrtcl.o cuiSend.o cuiTrans.o \
			cuiCheck.o cuiDn.o cuiRun.o cuiSet.o cuiUtil.o \
			cuiCmp.o cuiLoad.o cuiRunP.o cuiSlv.o rpm.o    \
			cuiMf.o cuiAb.o cuiTrc.o cuiHelp.o


DB           	=       $(SRC)/DB

all             :	$(OBJS)

clean           :
			/bin/rm -f  *.o *.ext *.c *.h *.db

cui.o           :	cui.kl1
			klic -x$(DB) -c cui.kl1
cuiCs.o         :	cuiCs.kl1
			klic -x$(DB) -c cuiCs.kl1
cuiPrtcl.o      :	cuiPrtcl.kl1
			klic -x$(DB) -c cuiPrtcl.kl1
cuiSend.o       :	cuiSend.kl1
			klic -x$(DB) -c cuiSend.kl1
cuiTrans.o      :	cuiTrans.kl1
			klic -x$(DB) -c cuiTrans.kl1
cuiCheck.o      :	cuiCheck.kl1
			klic -x$(DB) -c cuiCheck.kl1
cuiDn.o        :	cuiDn.kl1
			klic -x$(DB) -c cuiDn.kl1
cuiRun.o        :	cuiRun.kl1
			klic -x$(DB) -c cuiRun.kl1
cuiSet.o        :	cuiSet.kl1
			klic -x$(DB) -c cuiSet.kl1
cuiUtil.o       :	cuiUtil.kl1
			klic -x$(DB) -c cuiUtil.kl1
cuiCmp.o        :	cuiCmp.kl1
			klic -x$(DB) -c cuiCmp.kl1
cuiLoad.o       :	cuiLoad.kl1
			klic -x$(DB) -c cuiLoad.kl1
cuiRunP.o       :	cuiRunP.kl1
			klic -x$(DB) -c cuiRunP.kl1
cuiSlv.o        :	cuiSlv.kl1
			klic -x$(DB) -c cuiSlv.kl1
rpm.o          	:	rpm.kl1
			klic -x$(DB) -c rpm.kl1
cuiMf.o		:	cuiMf.kl1
			klic -x$(DB) -c cuiMf.kl1
cuiAb.o		:	cuiAb.kl1
			klic -x$(DB) -c cuiAb.kl1
cuiTrc.o	:	cuiTrc.kl1
			klic -x$(DB) -c cuiTrc.kl1
cuiHelp.o	:	cuiHelp.kl1
			klic -x$(DB) -c cuiHelp.kl1

