DBDIR           =       $(SRCDIR)/DB


OBJECTS = 	n_dnh.o		n_nh.o		n_par2.o \
		n_ioUtil.o	n_par1.o	n_shArg.o \
		n_shGl.o n_shPom.o

all             :       $(OBJECTS)

clean :
	rm -f core *.c *.o *.ext *.h *.db

n_dnh.o		:	n_dnh.kl1
			klic -x$(DBDIR) -c n_dnh.kl1
n_nh.o 		:	n_nh.kl1
			klic -x$(DBDIR) -c n_nh.kl1
n_par1.o 	:	n_par1.kl1
			klic -x$(DBDIR) -c n_par1.kl1
n_par2.o 	:	n_par2.kl1
			klic -x$(DBDIR) -c n_par2.kl1
n_ioUtil.o 	:	n_ioUtil.kl1
			klic -x$(DBDIR) -c n_ioUtil.kl1
n_shArg.o 	:	n_shArg.kl1
			klic -x$(DBDIR) -c n_shArg.kl1
n_shGl.o 	:	n_shGl.kl1
			klic -x$(DBDIR) -c n_shGl.kl1
n_shPom.o 	:	n_shPom.kl1
			klic -x$(DBDIR) -c n_shPom.kl1


