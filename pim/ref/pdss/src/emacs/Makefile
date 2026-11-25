LIBDIR	= /usr/local/lib/nemacs/lisp
EMACS	= nemacs
FILES	= pdss.elc pdss-manual.elc pdss-kl1cmp.elc kl1-mode.elc

all:	$(FILES)

install:
	cp pdss-init.el  $(LIBDIR)/pdss-init.el

clean:

.SUFFIXES:	.el .elc
.el.elc:
	$(EMACS) -batch -f batch-byte-compile $*.el
