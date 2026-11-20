OBJS    = tranMain.o

DBDIR           =       $(SRCDIR)/DB

all             :       $(OBJS)

clean           :
			/bin/rm -f  *.o *.ext *.c *.h *.db

tranMain.o       :	tranMain.kl1
			klic -x$(DBDIR) -c tranMain.kl1

