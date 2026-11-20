OBJS	= 	main.o shell.o

DBDIR		= 	$(KLICDIR)/DB

all 		:	$(OBJS)

clean		:	
			/bin/rm -f  *.o *.ext *.c *.h *.db

main.o 		:	main.kl1
			klic -x$(DBDIR) -c main.kl1
shell.o		:	shell.kl1
			klic -x$(DBDIR) -c shell.kl1

