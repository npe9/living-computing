OBJS    = p_at.o	p_spsu.o	p_suu.o	p_vwDef.o	p_vwUurM.o \
	  p_just.o	p_spuur.o	p_vecM.o	p_vwTab.o \
	  p_pom.o	p_strM.o	p_vecMU.o	p_vwUur.o p_trans.o


DBDIR		=	$(SRCDIR)/DB

all             :       $(OBJS)

clean           :
			/bin/rm -f  *.o *.ext *.c *.h *.db

p_at.o	 	:	p_at.kl1
			klic -x$(DBDIR) -c p_at.kl1
p_spsu.o	:	p_spsu.kl1
			klic -x$(DBDIR) -c p_spsu.kl1
p_suu.o		:	p_suu.kl1
			klic -x$(DBDIR) -c p_suu.kl1
p_vwDef.o 	:	p_vwDef.kl1
			klic -x$(DBDIR) -c p_vwDef.kl1
p_vwUurM.o 	:	p_vwUurM.kl1
			klic -x$(DBDIR) -c p_vwUurM.kl1
p_just.o 	:	p_just.kl1
			klic -x$(DBDIR) -c p_just.kl1
p_spuur.o 	:	p_spuur.kl1
			klic -x$(DBDIR) -c p_spuur.kl1
p_vecM.o 	:	p_vecM.kl1
			klic -x$(DBDIR) -c p_vecM.kl1
p_vwTab.o 	:	p_vwTab.kl1
			klic -x$(DBDIR) -c p_vwTab.kl1
p_pom.o	 	:	p_pom.kl1
			klic -x$(DBDIR) -c p_pom.kl1
p_strM.o 	:	p_strM.kl1
			klic -x$(DBDIR) -c p_strM.kl1
p_vecMU.o 	:	p_vecMU.kl1
			klic -x$(DBDIR) -c p_vecMU.kl1
p_vwUur.o 	:	p_vwUur.kl1
			klic -x$(DBDIR) -c p_vwUur.kl1
p_trans.o 	:	p_trans.kl1
			klic -x$(DBDIR) -c p_trans.kl1


