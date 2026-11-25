# PDSS V2.52.20, modernised (living-computing).  Plain POSIX make.
#
#   make                      # pdss and pdssasm, with $(CC)
#   make CC=gcc-15            # any C11 compiler
#   make O=../build-x         # objects and binaries in another directory
#
# The original Makefile is in git history (the pristine import).

CC	= cc
OPT	= -O2
WARN	=
CFLAGS	= $(OPT) $(WARN)
LDFLAGS	=
LIBS	= -lm
O	= .
MAKEDATE = living-computing modern build
# Extra objects (the transitional low-memory shim, see ../README.md).
SHIM	=

KL1	= pdss option emulate blt_basic blt_float blt_shoen blt_iodev \
	  blt_code blt_system deref passive unify goal shoen exception \
	  memory atom module dcode float string gc gc_ctrl gc_cell gc_code \
	  gc_dead mrbgc instr invassm assemble saveload native tracer print \
	  io iosub timer path ctype arena sysdep
ASM	= pdssasm memory atom module instr assemble saveload float ctype arena sysdep

all: $(O)/pdss $(O)/pdssasm

$(O)/pdss: objs
	$(CC) $(CFLAGS) $(LDFLAGS) -o $@ -D'MAKEDATE="$(MAKEDATE)"' version.c \
	  `for f in $(KL1); do printf '$(O)/%s.o ' $$f; done` $(SHIM) $(LIBS)

$(O)/pdssasm: objs
	$(CC) $(CFLAGS) $(LDFLAGS) -o $@ -D'MAKEDATE="$(MAKEDATE)"' version.c \
	  `for f in $(ASM); do printf '$(O)/%s.o ' $$f; done` $(SHIM) $(LIBS)

objs:
	@mkdir -p $(O)
	@for f in $(KL1) pdssasm; do \
	  if [ ! -f $(O)/$$f.o ] || [ $$f.c -nt $(O)/$$f.o ] || \
	     [ -n "`find . -name '*.h' -newer $(O)/$$f.o`" ]; then \
	    echo "$(CC) $(CFLAGS) -c $$f.c"; \
	    $(CC) $(CFLAGS) -c $$f.c -o $(O)/$$f.o || exit 1; \
	  fi; \
	done

clean:
	rm -f $(O)/*.o $(O)/pdss $(O)/pdssasm

.PHONY: all objs clean
