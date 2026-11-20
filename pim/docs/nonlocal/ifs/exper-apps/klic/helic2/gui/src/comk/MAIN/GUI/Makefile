OBJS    =  main.o

DBDIR           =       $(KLICDIR)/DB

all             :	$(OBJS)

clean           :
			/bin/rm -f  *.o *.ext *.c *.h *.db

main.o          :	main.kl1
			klic -x$(DBDIR) -c main.kl1


