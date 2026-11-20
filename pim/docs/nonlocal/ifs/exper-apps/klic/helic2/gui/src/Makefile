COMC		= 	comc
GUI		= 	gui
COMK		= 	comk

# Language
LANG            =       japanese
#LANG            =       english

# Flex
Flex            =       exist
#Flex           =       nothing


all             :
		       cd  $(COMC); $(MAKE) 
		       cd  $(GUI); $(MAKE)
		       cd  $(COMK); $(MAKE) LANG="$(LANG)" \
				    Flex="$(Flex)" \
				    MAKE="$(MAKE)" \
				    all 

dbt             :
		       cd  $(COMK); $(MAKE) LANG="$(LANG)" \
				    Flex="$(Flex)" \
				    MAKE="$(MAKE)" \
				    all 

clean           :
			cd $(COMC); $(MAKE) clean
			cd $(GUI); $(MAKE) clean
			cd $(COMK); $(MAKE) LANG="$(LANG)" \
				    Flex="$(Flex)" \
				    MAKE="$(MAKE)" \
				    clean
			cd ../bin; /bin/rm -f guidbt libcomc.a gtrans gtransrg
####test

TEST            =       comk/TRANS

test            :      
			cd  $(TEST); $(MAKE) LANG="$(LANG)" \
				    Flex="$(Flex)" \
				    MAKE="$(MAKE)" \
				    all 
