OBJS    = at.o strMat.o vecMat.o vecMatUtil.o pom.o spsu.o viewDef.o \
	  view_uur.o sp_uur.o suu.o viewTab.o view_uurMan.o justify.o \
	  pomTrans.o

DBDIR		=	$(KLICDIR)/DB

all             :       $(OBJS)

clean           :
			/bin/rm -f  *.o *.ext *.c *.h *.db

at.o 		:	at.kl1
			klic -x$(DBDIR) -c at.kl1
strMat.o 	:	strMat.kl1
			klic -x$(DBDIR) -c strMat.kl1
vecMat.o 	:	vecMat.kl1
			klic -x$(DBDIR) -c vecMat.kl1
vecMatUtil.o	:	vecMatUtil.kl1
			klic -x$(DBDIR) -c vecMatUtil.kl1
pom.o 		:	pom.kl1
			klic -x$(DBDIR) -c pom.kl1
spsu.o    	:	spsu.kl1
			klic -x$(DBDIR) -c spsu.kl1
viewDef.o 	:	viewDef.kl1
			klic -x$(DBDIR) -c viewDef.kl1
view_uur.o 	:	view_uur.kl1
			klic -x$(DBDIR) -c view_uur.kl1
sp_uur.o 	:	sp_uur.kl1
			klic -x$(DBDIR) -c sp_uur.kl1
suu.o 		:	suu.kl1
			klic -x$(DBDIR) -c suu.kl1
viewTab.o 	:	viewTab.kl1
			klic -x$(DBDIR) -c viewTab.kl1
view_uurMan.o	:	view_uurMan.kl1
			klic -x$(DBDIR) -c view_uurMan.kl1
justify.o	:	justify.kl1
			klic -x$(DBDIR) -c justify.kl1
pomTrans.o	:	pomTrans.kl1
			klic -x$(DBDIR) -c pomTrans.kl1



