OBJS    = hutil.o       set.o         siflib.o      substring.o \
	  append_string.o 	      revTrans.o

DBDIR           =       $(KLICDIR)/DB

all             :       $(OBJS)

clean           :
			/bin/rm -f  *.o *.ext *.c *.h *.db

hutil.o       	:	hutil.kl1
			klic -x$(DBDIR) -c hutil.kl1
set.o         	:	set.kl1
			klic -x$(DBDIR) -c set.kl1
siflib.o      	:	siflib.kl1
			klic -x$(DBDIR) -c siflib.kl1
substring.o	:	substring.kl1
			klic -x$(DBDIR) -c substring.kl1
append_string.o	:	append_string.kl1
			klic -x$(DBDIR) -c append_string.kl1
revTrans.o	:	revTrans.kl1
			klic -x$(DBDIR) -c revTrans.kl1

