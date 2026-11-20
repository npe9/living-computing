UTILDIR         =       DBT/UTIL
USERDIR         =       DBT/USER
SYSTEMDIR       =       DBT/SYSTEM
MAINDIR         =       DBT/MAIN
GUIDIR		= 	GUI/MAIN
SLVDIR		= 	GUI/SOLVE

all             :	compile

clean		:
			cd $(UTILDIR);  	$(MAKE) clean
			cd $(USERDIR);  	$(MAKE) clean
			cd $(SYSTEMDIR);  	$(MAKE) clean
			cd $(MAINDIR);  	$(MAKE) clean
			cd $(GUIDIR);  		$(MAKE) clean
			cd $(SLVDIR);  		$(MAKE) clean

compile         :       util user system main gui slv

util            :
			cd $(UTILDIR);  $(MAKE) SRCDIR="../../$(SRCDIR)"
user            :
			cd $(USERDIR);  $(MAKE) SRCDIR="../../$(SRCDIR)"
system          :
			cd $(SYSTEMDIR); $(MAKE) SRCDIR="../../$(SRCDIR)"
main            :
			cd $(MAINDIR); $(MAKE) SRCDIR="../../$(SRCDIR)"
gui            :
			cd $(GUIDIR); $(MAKE) SRCDIR="../../$(SRCDIR)"
slv            :
			cd $(SLVDIR); $(MAKE) SRCDIR="../../$(SRCDIR)"

