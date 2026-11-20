OBJS	=       caPool.o cancel.o claim1.o claim2.o finish1.o finish2.o \
		ial.o icaPool.o issuePool.o main.o notice1.o notice2.o  \
		pass.o pool.o shell.o start.o

DBDIR		= 	$(KLICDIR)/DB

all 		:	$(OBJS)

clean		:	
			/bin/rm -f  *.o *.ext *.c *.h *.db

caPool.o 	:	caPool.kl1
			klic -x$(DBDIR) -c caPool.kl1
cancel.o 	:	cancel.kl1
			klic -x$(DBDIR) -c cancel.kl1
claim1.o 	:	claim1.kl1
			klic -x$(DBDIR) -c claim1.kl1
claim2.o 	:	claim2.kl1
			klic -x$(DBDIR) -c claim2.kl1
finish1.o 	:	finish1.kl1
			klic -x$(DBDIR) -c finish1.kl1
finish2.o	:	finish2.kl1
			klic -x$(DBDIR) -c finish2.kl1
ial.o 		:	ial.kl1
			klic -x$(DBDIR) -c ial.kl1
icaPool.o 	:	icaPool.kl1
			klic -x$(DBDIR) -c icaPool.kl1
issuePool.o 	:	issuePool.kl1
			klic -x$(DBDIR) -c issuePool.kl1
main.o 		:	main.kl1
			klic -x$(DBDIR) -c main.kl1
notice1.o 	:	notice1.kl1
			klic -x$(DBDIR) -c notice1.kl1
notice2.o  	:	notice2.kl1
			klic -x$(DBDIR) -c notice2.kl1
pass.o 		:	pass.kl1
			klic -x$(DBDIR) -c pass.kl1
pool.o 		:	pool.kl1
			klic -x$(DBDIR) -c pool.kl1
shell.o 	:	shell.kl1
			klic -x$(DBDIR) -c shell.kl1
start.o		:	start.kl1
			klic -x$(DBDIR) -c start.kl1




