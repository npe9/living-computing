OBJS    = c_hutil.o       c_hset.o         c_siflib.o      c_substr.o \
	  c_appstr.o 	      revTrans.o

DBDIR           =       $(SRCDIR)/DB

all             :       $(OBJS)

clean           :
			/bin/rm -f  *.o *.ext *.c *.h *.db

c_hutil.o      	:	c_hutil.kl1
			klic -x$(DBDIR) -c c_hutil.kl1
c_hset.o        	:	c_hset.kl1
			klic -x$(DBDIR) -c c_hset.kl1
c_siflib.o     	:	c_siflib.kl1
			klic -x$(DBDIR) -c c_siflib.kl1
c_substr.o	:	c_substr.kl1
			klic -x$(DBDIR) -c c_substr.kl1
c_appstr.o	:	c_appstr.kl1
			klic -x$(DBDIR) -c c_appstr.kl1
revTrans.o	:	revTrans.kl1
			klic -x$(DBDIR) -c revTrans.kl1

