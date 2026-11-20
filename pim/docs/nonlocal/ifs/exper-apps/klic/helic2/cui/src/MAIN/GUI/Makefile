OBJS    =  cuiMain.o

DBDIR           =       $(SRCDIR)/DB

all             :	$(OBJS)

clean           :
			/bin/rm -f  *.o *.ext *.c *.h *.db

cuiMain.o       :	cuiMain.kl1
			klic -x$(DBDIR) -c cuiMain.kl1


