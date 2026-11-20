OBJS	= h_stio.o h_stdin.o h_stdout.o h_stdint.o h_stdio.o \
	  h_kb.o h_pool.o h_getl.o h_file.o h_buffer.o h_hlib.o 

DBDIR		= 	$(SRCDIR)/DB

all 		:	$(OBJS)

clean		:	
			/bin/rm -f  *.o *.ext *.c *.h *.db


h_stio.o	:	h_stio.kl1
			klic -x$(DBDIR) -c h_stio.kl1
h_stdin.o 	:	h_stdin.kl1
			klic -x$(DBDIR) -c h_stdin.kl1
h_stdout.o 	:	h_stdout.kl1
			klic -x$(DBDIR) -c h_stdout.kl1
h_stdint.o 	:	h_stdint.kl1
			klic -x$(DBDIR) -c h_stdint.kl1
h_stdio.o 	:	h_stdio.kl1
			klic -x$(DBDIR) -c h_stdio.kl1
h_kb.o		:	h_kb.kl1
			klic -x$(DBDIR) -c h_kb.kl1
h_pool.o 	:	h_pool.kl1
			klic -x$(DBDIR) -c h_pool.kl1
h_getl.o 	:	h_getl.kl1
			klic -x$(DBDIR) -c h_getl.kl1
h_file.o 	:	h_file.kl1
			klic -x$(DBDIR) -c h_file.kl1
h_buffer.o 	:	h_buffer.kl1
			klic -x$(DBDIR) -c h_buffer.kl1
h_hlib.o 	:	h_hlib.kl1
			klic -x$(DBDIR) -c h_hlib.kl1
