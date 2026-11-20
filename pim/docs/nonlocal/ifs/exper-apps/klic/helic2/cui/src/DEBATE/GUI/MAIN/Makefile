OBJS	 	= 	c_cgs.o c_load.o c_send.o c_start.o c_sort.o \
			c_check.o c_cui.o c_prtcl.o c_set.o c_util.o \
			c_runCP.o c_run.o c_dn.o c_trans.o c_cmp.o \
			c_mf.o c_trc.o c_slv.o c_ab.o c_help.o

DBDIR		= 	$(SRCDIR)/DB

all 		:	$(OBJS)

clean		:	
			/bin/rm -f  *.o *.ext *.c *.h *.db

c_cgs.o  	:	c_cgs.kl1
			klic -x$(DBDIR) -c c_cgs.kl1
c_load.o  	:	c_load.kl1
			klic -x$(DBDIR) -c c_load.kl1
c_send.o  	:	c_send.kl1
			klic -x$(DBDIR) -c c_send.kl1
c_start.o  	:	c_start.kl1
			klic -x$(DBDIR) -c c_start.kl1
c_check.o  	:	c_check.kl1
			klic -x$(DBDIR) -c c_check.kl1
c_cui.o  	:	c_cui.kl1
			klic -x$(DBDIR) -c c_cui.kl1
c_prtcl.o  	:	c_prtcl.kl1
			klic -x$(DBDIR) -c c_prtcl.kl1
c_set.o  	:	c_set.kl1
			klic -x$(DBDIR) -c c_set.kl1
c_util.o 	:	c_util.kl1
			klic -x$(DBDIR) -c c_util.kl1
c_runCP.o 	:	c_runCP.kl1
			klic -x$(DBDIR) -c c_runCP.kl1
c_run.o		:	c_run.kl1
			klic -x$(DBDIR) -c c_run.kl1
c_sort.o	:	c_sort.kl1
			klic -x$(DBDIR) -c c_sort.kl1
c_dn.o		:	c_dn.kl1
			klic -x$(DBDIR) -c c_dn.kl1
c_trans.o	:	c_trans.kl1
			klic -x$(DBDIR) -c c_trans.kl1
c_cmp.o		:	c_cmp.kl1
			klic -x$(DBDIR) -c c_cmp.kl1
c_mf.o		:	c_mf.kl1
			klic -x$(DBDIR) -c c_mf.kl1
c_trc.o		:	c_trc.kl1
			klic -x$(DBDIR) -c c_trc.kl1
c_slv.o		:	c_slv.kl1
			klic -x$(DBDIR) -c c_slv.kl1
c_ab.o		:	c_ab.kl1
			klic -x$(DBDIR) -c c_ab.kl1
c_help.o	:	c_help.kl1
			klic -x$(DBDIR) -c c_help.kl1

