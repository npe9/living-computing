PDSSCMP	= ../pdsscmp
PDSSASM	= ../emulator/pdssasm
PARA	=

DUTIL	= mpimos_xref.sav mpimos_xref_table.sav \
	  mpimos_pretty_printer.sav mpimos_varchk.sav

all: $(PARA)	$(DUTIL)

install:

clean:

reassm:
	for f in `echo $(DUTIL) | sed 's/\.sav//g'`; do $(PDSSASM) $$f; done

.SUFFIXES:	.kl1 .asm .sav
.kl1.sav:
	$(PDSSCMP) $*.kl1
.kl1.asm:
	$(PDSSCMP) -a $*.kl1
.asm.sav:
	$(PDSSASM) $*
