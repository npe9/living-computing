OBJS	=  	ty_att.o ty_blt.o ty_info.o ty_init.o ty_lat.o \
	        ty_osif.o ty_tatt.o ty_tcmp.o ty_texp.o ty_tlat.o \
        	ty_tload.o ty_top.o ty_tread.o ty_tsav.o ty_util.o \
	        var_env.o

DBDIR		= 	$(SRCDIR)/DB

all 		:	$(OBJS)

clean		:	
			/bin/rm -f  *.o *.ext *.c *.h *.db

ty_att.o  	:	ty_att.kl1
			klic -x$(DBDIR) -c ty_att.kl1
ty_blt.o   	:	ty_blt.kl1
			klic -x$(DBDIR) -c ty_blt.kl1
ty_info.o   	:	ty_info.kl1
			klic -x$(DBDIR) -c ty_info.kl1
ty_init.o   	:	ty_init.kl1
			klic -x$(DBDIR) -c ty_init.kl1
ty_lat.o   	:	ty_lat.kl1
			klic -x$(DBDIR) -c ty_lat.kl1
ty_osif.o   	:	ty_osif.kl1
			klic -x$(DBDIR) -c ty_osif.kl1
ty_tatt.o   	:	ty_tatt.kl1
			klic -x$(DBDIR) -c ty_tatt.kl1
ty_tcmp.o   	:	ty_tcmp.kl1
			klic -x$(DBDIR) -c ty_tcmp.kl1
ty_texp.o   	:	ty_texp.kl1
			klic -x$(DBDIR) -c ty_texp.kl1
ty_tlat.o   	:	ty_tlat.kl1
			klic -x$(DBDIR) -c ty_tlat.kl1
ty_tload.o   	:	ty_tload.kl1
			klic -x$(DBDIR) -c ty_tload.kl1
ty_top.o   	:	ty_top.kl1
			klic -x$(DBDIR) -c ty_top.kl1
ty_tread.o   	:	ty_tread.kl1
			klic -x$(DBDIR) -c ty_tread.kl1
ty_tsav.o   	:	ty_tsav.kl1
			klic -x$(DBDIR) -c ty_tsav.kl1
ty_util.o   	:	ty_util.kl1
			klic -x$(DBDIR) -c ty_util.kl1
var_env.o  	:	var_env.kl1
			klic -x$(DBDIR) -c var_env.kl1

