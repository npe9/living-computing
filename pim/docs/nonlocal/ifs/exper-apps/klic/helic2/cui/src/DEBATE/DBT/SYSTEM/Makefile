OBJS	=       s_caPool.o s_cancel.o s_claim1.o s_claim2.o s_fin1.o s_fin2.o \
		s_ial.o s_icPool.o s_isPool.o s_main.o s_notic1.o s_notic2.o  \
		s_pass.o s_pool.o s_shell.o s_start.o

DBDIR		=	$(SRCDIR)/DB

all 		:	$(OBJS)

clean		:	
			/bin/rm -f  *.o *.ext *.c *.h *.db

s_caPool.o 	:	s_caPool.kl1
			klic -x$(DBDIR) -c s_caPool.kl1
s_cancel.o 	:	s_cancel.kl1
			klic -x$(DBDIR) -c s_cancel.kl1
s_claim1.o 	:	s_claim1.kl1
			klic -x$(DBDIR) -c s_claim1.kl1
s_claim2.o 	:	s_claim2.kl1
			klic -x$(DBDIR) -c s_claim2.kl1
s_fin1.o 	:	s_fin1.kl1
			klic -x$(DBDIR) -c s_fin1.kl1
s_fin2.o	:	s_fin2.kl1
			klic -x$(DBDIR) -c s_fin2.kl1
s_ial.o 	:	s_ial.kl1
			klic -x$(DBDIR) -c s_ial.kl1
s_icPool.o 	:	s_icPool.kl1
			klic -x$(DBDIR) -c s_icPool.kl1
s_isPool.o 	:	s_isPool.kl1
			klic -x$(DBDIR) -c s_isPool.kl1
s_main.o 	:	s_main.kl1
			klic -x$(DBDIR) -c s_main.kl1
s_notic1.o 	:	s_notic1.kl1
			klic -x$(DBDIR) -c s_notic1.kl1
s_notic2.o  	:	s_notic2.kl1
			klic -x$(DBDIR) -c s_notic2.kl1
s_pass.o 	:	s_pass.kl1
			klic -x$(DBDIR) -c s_pass.kl1
s_pool.o 	:	s_pool.kl1
			klic -x$(DBDIR) -c s_pool.kl1
s_shell.o 	:	s_shell.kl1
			klic -x$(DBDIR) -c s_shell.kl1
s_start.o	:	s_start.kl1
			klic -x$(DBDIR) -c s_start.kl1




