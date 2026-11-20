OBJS	= 	u_ial.o u_pool.o \
		u_cancel.o u_claim2.o u_fin2.o u_notic1.o u_pass.o \
		u_claim1.o u_fin1.o u_main.o u_notic2.o u_start.o \
		u_shell.o u_shell1.o u_shell2.o u_shell3.o  \
		u_shell4.o u_shell5.o

DBDIR		=	$(SRCDIR)/DB

all 		:	$(OBJS)

clean		:	
			/bin/rm -f  *.o *.ext *.c *.h *.db

u_ial.o		:	u_ial.kl1
			klic -x$(DBDIR) -c u_ial.kl1
u_pool.o 	:	u_pool.kl1
			klic -x$(DBDIR) -c u_pool.kl1
u_cancel.o 	:	u_cancel.kl1
			klic -x$(DBDIR) -c u_cancel.kl1
u_claim2.o 	:	u_claim2.kl1
			klic -x$(DBDIR) -c u_claim2.kl1
u_fin2.o	:	u_fin2.kl1
			klic -x$(DBDIR) -c u_fin2.kl1
u_notic1.o	:	u_notic1.kl1
			klic -x$(DBDIR) -c u_notic1.kl1
u_pass.o	:	u_pass.kl1
			klic -x$(DBDIR) -c u_pass.kl1
u_claim1.o 	:	u_claim1.kl1
			klic -x$(DBDIR) -c u_claim1.kl1
u_fin1.o	:	u_fin1.kl1
			klic -x$(DBDIR) -c u_fin1.kl1
u_main.o 	:	u_main.kl1
			klic -x$(DBDIR) -c u_main.kl1
u_notic2.o	:	u_notic2.kl1
			klic -x$(DBDIR) -c u_notic2.kl1
u_start.o	:	u_start.kl1
			klic -x$(DBDIR) -c u_start.kl1
u_shell.o	:	u_shell.kl1
			klic -x$(DBDIR) -c u_shell.kl1
u_shell1.o	:	u_shell1.kl1
			klic -x$(DBDIR) -c u_shell1.kl1
u_shell2.o	:	u_shell2.kl1
			klic -x$(DBDIR) -c u_shell2.kl1
u_shell3.o	:	u_shell3.kl1
			klic -x$(DBDIR) -c u_shell3.kl1
u_shell4.o	:	u_shell4.kl1
			klic -x$(DBDIR) -c u_shell4.kl1
u_shell5.o	:	u_shell5.kl1
			klic -x$(DBDIR) -c u_shell5.kl1
