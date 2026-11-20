OBJS	= agent.o	dbt.o		idt.o

DBDIR		= 	$(KLICDIR)/DB

all 		:	$(OBJS)

clean		:	
			/bin/rm -f  *.o *.ext *.c *.h *.db

agent.o		:	agent.kl1
			klic -x$(DBDIR) -c agent.kl1
dbt.o		:	dbt.kl1
			klic -x$(DBDIR) -c dbt.kl1
idt.o		:	idt.kl1
			klic -x$(DBDIR) -c idt.kl1


