OBJS    =  main.o

DB           =       $(SRC)/DB

all             :	$(OBJS)

clean           :
			/bin/rm -f  *.o *.ext *.c *.h *.db

main.o          :	main.kl1
			klic -x$(DB) -c main.kl1


