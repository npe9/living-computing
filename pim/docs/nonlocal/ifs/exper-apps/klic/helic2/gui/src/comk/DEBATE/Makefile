SRCDIR		= 	$(KLICDIR)

UTILDIR         =       $(SRCDIR)/DEBATE/DBT/UTIL
USERDIR         =       $(SRCDIR)/DEBATE/DBT/USER
SYSTEMDIR       =       $(SRCDIR)/DEBATE/DBT/SYSTEM
MAINDIR         =       $(SRCDIR)/DEBATE/DBT/MAIN
SLVDIR		= 	$(SRCDIR)/DEBATE/DBT/SOLVE
GUIDIR		= 	$(SRCDIR)/DEBATE/GUI



all             :	compile

clean		:
			cd $(UTILDIR);  	$(MAKE) clean
			cd $(USERDIR);  	$(MAKE) clean
			cd $(SYSTEMDIR);  	$(MAKE) clean
			cd $(MAINDIR);  	$(MAKE) clean
			cd $(SLVDIR);  		$(MAKE) clean
			cd $(GUIDIR);  		$(MAKE) clean

compile         :       slv util user system main gui 

slv		:
			cd $(SLVDIR);  $(MAKE) KLICDIR="../../$(KLICDIR)"
util            :
			cd $(UTILDIR);  $(MAKE) KLICDIR="../../$(KLICDIR)"
user            :
			cd $(USERDIR);  $(MAKE) KLICDIR="../../$(KLICDIR)"
system          :
			cd $(SYSTEMDIR); $(MAKE) KLICDIR="../../$(KLICDIR)"
main            :
			cd $(MAINDIR); $(MAKE) KLICDIR="../../$(KLICDIR)"
gui            :
			cd $(GUIDIR); $(MAKE) KLICDIR="../$(KLICDIR)"

