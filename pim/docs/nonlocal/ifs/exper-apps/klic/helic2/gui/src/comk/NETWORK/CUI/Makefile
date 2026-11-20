DBDIR           =       $(KLICDIR)/DB

OBJECTS = 	dnh.o		nh.o		parser2.o \
		ioUtil.o	parser1.o	show.o

all             :       $(OBJECTS)

clean :
	rm -f core *.c *.o *.ext *.h *.db

dnh.o		:	dnh.kl1
		klic -x$(DBDIR) -c dnh.kl1
nh.o 		:	nh.kl1
		klic -x$(DBDIR) -c nh.kl1
parser1.o 	:	parser1.kl1
		klic -x$(DBDIR) -c parser1.kl1
parser2.o 	:	parser2.kl1
		klic -x$(DBDIR) -c parser2.kl1
ioUtil.o 	:	ioUtil.kl1
		klic -x$(DBDIR) -c ioUtil.kl1
show.o 		:	show.kl1
		klic -x$(DBDIR) -c show.kl1


