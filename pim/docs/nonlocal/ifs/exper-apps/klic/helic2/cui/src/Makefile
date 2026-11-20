# Language
LANG            =       japanese
#LANG           =       english

# Flex
Flex            =       exist
#Flex           =       nothing

TOPDIR 		= 	..

SRCDIR		= 	$(TOPDIR)/src
BINDIR          =       $(TOPDIR)/bin

DB		= 	$(SRCDIR)/DB
HLIBDIR		= 	$(SRCDIR)/HLIB
UTILDIR	 	= 	$(SRCDIR)/UTIL
POMDIR		= 	$(SRCDIR)/POM

TRANSDIR	= 	$(SRCDIR)/TRANS
MTRANSDIR	= 	$(SRCDIR)/TRANS/MAIN

TYPEDIR   	=  	$(SRCDIR)/TYPE
RBRDIR		=  	$(SRCDIR)/RBR
NETCUIDIR	=       $(SRCDIR)/NETWORK/CUI

DEBATEDIR	=       $(SRCDIR)/DEBATE
DBTUTILDIR	=       $(SRCDIR)/DEBATE/DBT/UTIL
USERDIR		=       $(SRCDIR)/DEBATE/DBT/USER
SYSTEMDIR	=       $(SRCDIR)/DEBATE/DBT/SYSTEM
DBTMAINDIR	=       $(SRCDIR)/DEBATE/DBT/MAIN
GUIDIR		=       $(SRCDIR)/DEBATE/GUI/MAIN
SLVDIR		=       $(SRCDIR)/DEBATE/GUI/SOLVE

MAINDIR         =       $(SRCDIR)/MAIN/GUI


#all 		:	compile link link-trans
all 		:	compile link 

clean		:	
			cd $(HLIBDIR);	$(MAKE) clean 
			cd $(UTILDIR);	$(MAKE) clean 
			cd $(POMDIR);	$(MAKE) clean 
			cd $(TRANSDIR); $(MAKE) LANG="$(LANG)"\
    					        Flex="$(Flex)" clean 
			cd $(TYPEDIR);	$(MAKE) clean 
			cd $(RBRDIR);	$(MAKE) clean 
			cd $(NETCUIDIR);$(MAKE) clean 
			cd $(DEBATEDIR);$(MAKE) clean 
			cd $(MAINDIR);	$(MAKE) clean 
			cd $(DB);   	/bin/rm -f  *.*
			cd $(SRCDIR);   /bin/rm -f  *.h
			cd $(BINDIR);   /bin/rm -f  *

compile 	:	trans hlib util pom type rbr netcui debate main 

hlib		:
			cd $(HLIBDIR);	$(MAKE) SRCDIR="../$(SRCDIR)" 
util		:
			cd $(UTILDIR);	$(MAKE) SRCDIR="../$(SRCDIR)"
pom		:
			cd $(POMDIR);	$(MAKE) SRCDIR="../$(SRCDIR)"
trans		:
			cd $(TRANSDIR);	$(MAKE) LANG="$(LANG)"\
					        Flex="$(Flex)"\
						SRCDIR="../$(SRCDIR)"
type		:
			cd $(TYPEDIR);	$(MAKE) SRCDIR="../$(SRCDIR)"
rbr		:
			cd $(RBRDIR);	$(MAKE) SRCDIR="../$(SRCDIR)"
netcui		:
			cd $(NETCUIDIR);$(MAKE) SRCDIR="../../$(SRCDIR)"
debate		:
			cd $(DEBATEDIR);$(MAKE) SRCDIR="../$(SRCDIR)"
main		:
			cd $(MAINDIR);	$(MAKE) SRCDIR="../../$(SRCDIR)"

link		:	
			klic -x $(DB)  \
			     -o $(BINDIR)/cui   $(HLIBDIR)/*.o          \
						$(UTILDIR)/*.o    	\
						$(POMDIR)/*.o     	\
						$(TYPEDIR)/*.o   	\
						$(RBRDIR)/*.o     	\
						$(NETCUIDIR)/*.o     	\
						$(DBTUTILDIR)/*.o    	\
						$(USERDIR)/*.o    	\
						$(SYSTEMDIR)/*.o    	\
						$(DBTMAINDIR)/*.o    	\
						$(GUIDIR)/*.o           \
						$(SLVDIR)/*.o           \
						$(MAINDIR)/*.o

link-trans	:	
			klic -x $(DB)  \
			     -o $(BINDIR)/ctrans $(HLIBDIR)/*.o          \
						$(UTILDIR)/*.o    	\
						$(POMDIR)/*.o     	\
						$(TYPEDIR)/*.o   	\
						$(MTRANSDIR)/*.o





