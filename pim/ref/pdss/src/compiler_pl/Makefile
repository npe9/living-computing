PROLOG	= sicstus

CMDCMP	= "compile('pdss_sys.pl'), make_kl1cmp_for_pdss."
CMP	= top2.pl read.pl write2.pl norm3.pl comp2.pl mrb4.pl reg.pl \
	  index2.pl macro2.pl convert.pl code_opt2.pl aux2.pl \
	  pdss_blt.pl pdss_sys.pl libdir.pl
CMDTRN	= "compile(['pdsstrans.pl']), go."
TRN	= pdsstrans.pl


all:	kl1cmp pdsstrans

kl1cmp:	$(CMP)
	-echo $(CMDCMP) | $(PROLOG)
	chmod +x kl1cmp

pdsstrans: $(TRN)
	-echo $(CMDTRN) | $(PROLOG)
	chmod +x pdsstrans

install:

clean:
