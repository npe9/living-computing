# Language
LANG            =       japanese
#LANG           =       english

# Flex
Flex            =       exist
#Flex           =       nothing


TOP 		= 	..
SRC		= 	$(TOP)/src
BIN          	=       $(TOP)/bin

DB		= 	$(SRC)/DB

CUI		= 	$(SRC)/CUI/MAIN
NET		= 	$(SRC)/CUI/NETWORK
SLV		= 	$(SRC)/CUI/SOLVE
HLIB		= 	$(SRC)/HLIB
MAIN         	=       $(SRC)/MAIN
POM		= 	$(SRC)/POM
RBR		=  	$(SRC)/RBR
TYPE   		=  	$(SRC)/TYPE
UTIL	 	= 	$(SRC)/UTIL
TRANS	 	= 	$(SRC)/TRANS

all 		:	compile link

clean		:
			cd $(CUI);	$(MAKE) clean 
			cd $(NET);	$(MAKE) clean 
			cd $(SLV);	$(MAKE) clean 
			cd $(HLIB);	$(MAKE) clean 
			cd $(MAIN);	$(MAKE) clean 
			cd $(POM);	$(MAKE) clean 
			cd $(RBR);	$(MAKE) clean 
			cd $(TYPE);	$(MAKE) clean 
			cd $(UTIL);	$(MAKE) clean 
			cd $(TRANS);	$(MAKE) clean 
			cd $(DB);   	/bin/rm -f  *.*
			cd $(SRC);      /bin/rm -f  *.h
			cd $(BIN);      /bin/rm -f  *

compile 	:	cui net slv hlib main pom rbr type util trans

cui		:
			cd $(CUI);	$(MAKE) SRC="../../$(SRC)" 
net		:
			cd $(NET);	$(MAKE) SRC="../../$(SRC)" 
slv		:
			cd $(SLV);	$(MAKE) SRC="../../$(SRC)" 
hlib		:
			cd $(HLIB);	$(MAKE) SRC="../$(SRC)" 
main		:
			cd $(MAIN);	$(MAKE) SRC="../$(SRC)"
pom		:
			cd $(POM);	$(MAKE) SRC="../$(SRC)"
rbr		:
			cd $(RBR);	$(MAKE) SRC="../$(SRC)"
type		:
			cd $(TYPE);	$(MAKE) SRC="../$(SRC)"
util		:
			cd $(UTIL);	$(MAKE) SRC="../$(SRC)"
trans		:
			cd $(TRANS);	$(MAKE) LANG="$(LANG)"\
						Flex="$(Flex)" \
						BIN="../$(BIN)"

link		:	
			klic -x $(DB)  				\
			     -o $(BIN)/drs     			\
						$(CUI)/*.o	\
						$(NET)/*.o	\
						$(SLV)/*.o	\
						$(HLIB)/*.o    	\
						$(MAIN)/*.o	\
						$(POM)/*.o     	\
						$(RBR)/*.o     	\
						$(TYPE)/*.o   	\
						$(UTIL)/*.o    	\




