TOP 		= 	..

KLICDIR 	= 	$(TOP)/comk
DB		= 	$(KLICDIR)/DB
SRCDIR		= 	$(KLICDIR)
BINDIR          =       ../$(TOP)/bin

HLIBDIR		= 	$(SRCDIR)/HLIB
UTILDIR	 	= 	$(SRCDIR)/UTIL
POMDIR		= 	$(SRCDIR)/POM


TRANSDIR        =       $(SRCDIR)/TRANS
MTRANSDIR       =       $(SRCDIR)/TRANS/MAIN

TYPEDIR   	=  	$(SRCDIR)/TYPE
RBRDIR		=  	$(SRCDIR)/RBR
NETGUIDIR	=       $(SRCDIR)/NETWORK/GUI
NETCUIDIR	=       $(SRCDIR)/NETWORK/CUI
DEBATEDIR	=       $(SRCDIR)/DEBATE
DBTUTILDIR	=       $(SRCDIR)/DEBATE/DBT/UTIL
USERDIR		=       $(SRCDIR)/DEBATE/DBT/USER
SYSTEMDIR	=       $(SRCDIR)/DEBATE/DBT/SYSTEM
DBTMAINDIR	=       $(SRCDIR)/DEBATE/DBT/MAIN
SLVDIR		=       $(SRCDIR)/DEBATE/DBT/SOLVE
GUIDIR		=       $(SRCDIR)/DEBATE/GUI
MAINDIR         =       $(SRCDIR)/MAIN/GUI

LANG            =       $(LANG)

Flex            =       $(Flex)

MAKE		= /bin/make

all 		:	compile link-gtrans link-guidbt 

clean		:	
			cd $(HLIBDIR);	$(MAKE) clean 
			cd $(UTILDIR);	$(MAKE) clean 
			cd $(POMDIR);	$(MAKE) clean 
			cd $(TRANSDIR);	$(MAKE) LANG="$(LANG)" \
						Flex="$(Flex)" \
						clean
			cd $(TYPEDIR);	$(MAKE) clean 
			cd $(RBRDIR);	$(MAKE) clean 
			cd $(NETGUIDIR);$(MAKE) clean 
			cd $(NETCUIDIR);$(MAKE) clean 
			cd $(DEBATEDIR);KLICDIR="../$(KLICDIR)" \
					$(MAKE) clean 
			cd $(MAINDIR);	$(MAKE) clean 
			cd $(DB);   	/bin/rm -f  *.*
			cd $(KLICDIR);  /bin/rm -f  *.h

compile 	:	trans hlib util pom type rbr netgui netcui debate main

hlib		:
			cd $(HLIBDIR);	$(MAKE) KLICDIR="../$(KLICDIR)" 
util		:
			cd $(UTILDIR);	$(MAKE) KLICDIR="../$(KLICDIR)"
pom		:
			cd $(POMDIR);	$(MAKE) KLICDIR="../$(KLICDIR)"
trans		:
			cd $(TRANSDIR);	$(MAKE) SRCCDIR="../$(KLICDIR)" \
					LANG="$(LANG)" \
					Flex="$(Flex)"
type		:
			cd $(TYPEDIR);	$(MAKE) KLICDIR="../$(KLICDIR)"
rbr		:
			cd $(RBRDIR);	$(MAKE) KLICDIR="../$(KLICDIR)"
netgui		:
			cd $(NETGUIDIR);$(MAKE) KLICDIR="../../$(KLICDIR)"
netcui		:
			cd $(NETCUIDIR);$(MAKE) KLICDIR="../../$(KLICDIR)"
debate		:
			cd $(DEBATEDIR);$(MAKE) KLICDIR="../$(KLICDIR)"
main		:
			cd $(MAINDIR);	$(MAKE) KLICDIR="../../$(KLICDIR)"


link-guidbt	:	
			klic -x $(DB)  \
			     -o $(BINDIR)/guidbt $(HLIBDIR)/*.o    	\
						$(UTILDIR)/*.o    	\
						$(POMDIR)/*.o     	\
						$(TYPEDIR)/*.o   	\
						$(RBRDIR)/*.o     	\
						$(NETGUIDIR)/*.o     	\
						$(DBTUTILDIR)/*.o    	\
						$(USERDIR)/*.o    	\
						$(SYSTEMDIR)/*.o    	\
						$(SLVDIR)/*.o    	\
						$(DBTMAINDIR)/*.o    	\
						$(GUIDIR)/*.o           \
						$(MAINDIR)/*.o

link-gtrans      :
			klic 	-x $(DB)  \
				-o $(BINDIR)/gtrans $(HLIBDIR)/*.o \
		                   $(UTILDIR)/*.o          \
                		   $(POMDIR)/*.o           \
		                   $(TYPEDIR)/*.o          \
		                   $(MTRANSDIR)/*.o

