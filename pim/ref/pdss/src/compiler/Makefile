PDSSCMP	= ../pdsscmp +s
PDSSASM	= ../emulator/pdssasm
PARA	=

COMPILER = blt.sav com.sav comp.sav mrb.sav norm.sav outp.sav reader.sav \
	   reg.sav macarg.sav macro.sav mactbl.sav struct.sav

all: $(PARA)	$(COMPILER)

install:

clean:

reassm:
	for f in `echo $(COMPILER) | sed 's/\.sav//g'`; do $(PDSSASM) $$f; done

.SUFFIXES:	.kl1 .asm .sav
.kl1.sav:
	$(PDSSCMP) $*.kl1
.kl1.asm:
	$(PDSSCMP) -a $*.kl1
.asm.sav:
	$(PDSSASM) $*
