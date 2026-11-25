PDSSCMP	= ../pdsscmp
PDSSASM	= ../emulator/pdssasm
PARA	=

PUTIL	= comparator.sav hasher.sav sorter.sav merger.sav\
	  keyed_bag.sav keyed_sorted_bag.sav multiply_keyed_bag.sav\
          pool.sav queue.sav stack.sav quick_sort.sav pimos_utility_error.sav

all: $(PARA)	$(PUTIL)

install:

clean:

reassm:
	for f in `echo $(PUTIL) | sed 's/\.sav//g'`; do $(PDSSASM) $$f; done

.SUFFIXES:	.kl1 .asm .sav
.kl1.sav:
	$(PDSSCMP) $*.kl1
.kl1.asm:
	$(PDSSCMP) -a $*.kl1
.asm.sav:
	$(PDSSASM) $*
