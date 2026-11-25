PDSSCMP	= ../pdsscmp +s
PDSSASM	= ../emulator/pdssasm
PARA	=

RUNTIME	= coddev.sav windev.sav fildev.sav timdev.sav shoen.sav

all: $(PARA)	$(RUNTIME)

install:

clean:

reassm:
	for f in `echo $(RUNTIME) | sed 's/\.sav//g'`; do $(PDSSASM) $$f; done

.SUFFIXES:	.kl1 .asm .sav
.kl1.sav:
	$(PDSSCMP) $*.kl1
.kl1.asm:
	$(PDSSCMP) -a $*.kl1
.asm.sav:
	$(PDSSASM) $*
