OBJS		= 	d_agent.o d_dbt.o d_idt.o

DBDIR		=	$(SRCDIR)/DB

all 		:	$(OBJS)

clean		:	
			/bin/rm -f  *.o *.ext *.c *.h *.db

d_agent.o	:	d_agent.kl1
			klic -x$(DBDIR) -c d_agent.kl1
d_dbt.o		:	d_dbt.kl1
			klic -x$(DBDIR) -c d_dbt.kl1
d_idt.o		:	d_idt.kl1
			klic -x$(DBDIR) -c d_idt.kl1


