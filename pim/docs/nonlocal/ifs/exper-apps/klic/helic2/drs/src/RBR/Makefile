OBJS	=  	chkarg.o rlmNLUD.o rbrUnify.o cbrUnify.o cntNLU.o \
		ppNLU.o cbrSolve.o drNLU.o rbrNLUD.o rulchk.o \
		chgpri.o evlans.o sltNLU.o rtop.o \
		trc.o trcPr.o calcDan.o cbrPUnif.o

DB		= 	$(SRC)/DB

all 		:	$(OBJS)

clean		:	
			/bin/rm -f  *.o *.ext *.c *.h *.db

chkarg.o 	:	chkarg.kl1
			klic -x$(DB) -c   chkarg.kl1
rlmNLUD.o 	:	rlmNLUD.kl1
			klic -x$(DB) -c   rlmNLUD.kl1
rbrUnify.o 	:	rbrUnify.kl1
			klic -x$(DB) -c   rbrUnify.kl1
cbrUnify.o 	:	cbrUnify.kl1
			klic -x$(DB) -c   cbrUnify.kl1
cntNLU.o 	:	cntNLU.kl1
			klic -x$(DB) -c   cntNLU.kl1
ppNLU.o 	:	ppNLU.kl1
			klic -x$(DB) -c   ppNLU.kl1
cbrSolve.o 	:	cbrSolve.kl1
			klic -x$(DB) -c   cbrSolve.kl1
drNLU.o 	:	drNLU.kl1
			klic -x$(DB) -c   drNLU.kl1
#rbrNLU.o 	:	rbrNLU.kl1
#			klic -x$(DB) -c   rbrNLU.kl1
rbrNLUD.o 	:	rbrNLUD.kl1
			klic -x$(DB) -c   rbrNLUD.kl1
rulchk.o 	:	rulchk.kl1
			klic -x$(DB) -c   rulchk.kl1
chgpri.o 	:	chgpri.kl1
			klic -x$(DB) -c   chgpri.kl1
evlans.o 	:	evlans.kl1
			klic -x$(DB) -c   evlans.kl1
sltNLU.o 	:	sltNLU.kl1
			klic -x$(DB) -c   sltNLU.kl1
rtop.o		:	rtop.kl1
			klic -x$(DB) -c   rtop.kl1
trc.o 		:	trc.kl1
			klic -x$(DB) -c   trc.kl1
trcPr.o		:	trcPr.kl1
			klic -x$(DB) -c   trcPr.kl1
calcDan.o	:	calcDan.kl1
			klic -x$(DB) -c   calcDan.kl1
cbrPUnif.o	:	cbrPUnif.kl1
			klic -x$(DB) -c   cbrPUnif.kl1
