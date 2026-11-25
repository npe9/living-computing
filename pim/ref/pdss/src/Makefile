##########################################################################
#  PDSS (PIMOS Development Support System)  Version 2.52		 #
#  (C) Copyright 1988,1989,1990.					 #
#  Institute for New Generation Computer Technology, Japan.		 #
#  ALL RIGHTS RESERVED.							 #
##########################################################################

BINDIR	= /usr/local/bin

#CFLAGS	= -g -DDEBUG
#CFLAGS	= -g -DDEBUG -J
CFLAGS	= -O
#CFLAGS	= -p

PARA	=


KL1	=	pdss.o option.o emulate.o blt_basic.o blt_float.o\
		blt_shoen.o blt_iodev.o blt_code.o blt_system.o\
		deref.o passive.o unify.o\
		goal.o shoen.o exception.o memory.o atom.o module.o dcode.o\
		float.o string.o\
		gc.o gc_ctrl.o gc_cell.o gc_code.o gc_dead.o mrbgc.o\
		instr.o invassm.o assemble.o saveload.o native.o\
		tracer.o print.o io.o iosub.o timer.o\
		path.o ctype.o
ASM	=	pdssasm.o memory.o atom.o module.o instr.o\
		assemble.o saveload.o float.o ctype.o
INV	=	pdssinv.o memory.o atom.o module.o instr.o\
		invassm.o saveload.o float.o ctype.o
MERGE	=	pdssmerge.o

all:	pdss pdssasm pdssmerge

pdss:	$(PARA)	$(KL1)
	$(CC) $(CFLAGS) -o pdss.x -D"MAKEDATE=\"`date`\"" version.c $(KL1) -lm
	mv -f pdss.x pdss
	rm -f version.o

pdssasm: $(PARA) $(ASM)
	$(CC) $(CFLAGS) -o pdssasm.x -D"MAKEDATE=\"`date`\"" version.c $(ASM) -lm
	mv -f pdssasm.x pdssasm
	rm -f version.o

pdssinv: $(PARA) $(INV)
	$(CC) $(CFLAGS) -o pdssinv.x -D"MAKEDATE=\"`date`\"" version.c $(INV) -lm
	mv -f pdssinv.x pdssinv
	rm -f version.o

pdssmerge: $(PARA) $(MERGE)
	$(CC) -o pdssmerge.x $(MERGE)
	mv -f pdssmerge.x pdssmerge

install:
	cp pdss $(BINDIR)/pdss.x
	strip $(BINDIR)/pdss.x
	mv -f $(BINDIR)/pdss.x $(BINDIR)/pdss

clean:
	rm -f $(KL1) $(ASM) $(INV) $(MERGE)

tags:
	etags *.h `echo $(KL1) | sed 's/\.o/\.c/g'`


#= Dependency ================================================================

pdss.h:		config.h statistics.h atom.h cell.h record.h
	touch pdss.h

pdss.o:		pdss.h io.h instr.h ctype.h
pdssasm.o:	pdss.h memory.h io.h klb.h
pdssinv.o:	pdss.h memory.h io.h klb.h instr.h

option.o:	pdss.h
emulate.o:	pdss.h memory.h io.h klb.h instr.h tracer.h
blt_basic.o:	pdss.h memory.h io.h instr.h
blt_float.o:	pdss.h memory.h io.h instr.h
blt_shoen.o:	pdss.h memory.h io.h instr.h
blt_iodev.o:	pdss.h memory.h io.h instr.h
blt_code.o:	pdss.h memory.h io.h instr.h
blt_system.o:	pdss.h memory.h io.h instr.h tracer.h

deref.o:	pdss.h memory.h
passive.o:	pdss.h
unify.o:	pdss.h memory.h io.h

goal.o:		pdss.h memory.h io.h tracer.h
shoen.o:	pdss.h memory.h io.h
exception.o:	pdss.h memory.h io.h klb.h
memory.o:	pdss.h memory.h io.h
atom.o:		pdss.h memory.h io.h table.c
module.o:	pdss.h memory.h io.h klb.h
dcode.o:	pdss.h

string.o:	pdss.h memory.h io.h ctype.h
float.o:	pdss.h

gc.o:		pdss.h memory.h io.h gc.h
gc_ctrl.o:	pdss.h memory.h io.h gc.h
gc_cell.o:	pdss.h memory.h io.h gc.h
gc_code.o:	pdss.h memory.h io.h klb.h gc.h
gc_dead.o:	pdss.h memory.h io.h klb.h gc.h
mrbgc.o:	pdss.h memory.h io.h klb.h

instr.o:	pdss.h io.h klb.h instr.h table.c
invassm.o:	pdss.h klb.h instr.h
assemble.o:	pdss.h memory.h io.h klb.h instr.h ctype.h table.c
saveload.o:	pdss.h memory.h io.h klb.h instr.h
native.o:	pdss.h memory.h io.h

tracer.o:	pdss.h memory.h io.h klb.h instr.h ctype.h tracer.h
print.o:	pdss.h memory.h io.h klb.h
io.o:		pdss.h memory.h io.h
iosub.o:	pdss.h memory.h io.h ctype.h
timer.o:	pdss.h memory.h io.h

path.o:		pdss.h io.h
ctype.o:	ctype.h
