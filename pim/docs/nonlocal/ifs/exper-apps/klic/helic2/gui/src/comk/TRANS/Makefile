CDIR		= 	C
MDIR		= 	MAIN
DBDIR           =       $(SRCDIR)/DB

all             :
		       cd  $(CDIR); $(MAKE) LANG="$(LANG)"\
					    Flex="$(Flex)"
		       cd  $(MDIR); $(MAKE) SRCDIR="../../$(SRCDIR)"

clean           :
			cd $(CDIR); $(MAKE) clean
			cd $(MDIR); $(MAKE) clean

