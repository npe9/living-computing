BINDIR = /usr/local/bin

quick:
	cd emulator	; make all
	sh -c "test ! -d compiler_pl || (cd compiler_pl ; make all)"
	sh -c "test ! -d emacs       || (cd emacs       ; make all)"

reassm:
	cd emulator	; make all
	sh -c "test ! -d compiler_pl || (cd compiler_pl ; make all)"
	cd runtime	; make reassm
	cd mpimos	; make reassm
	cd compiler	; make reassm
	sh -c "test ! -d debug_utl   || (cd debug_utl   ; make reassm)"
	sh -c "test ! -d pimos_utl   || (cd pimos_utl   ; make reassm)"
	sh -c "test ! -d emacs       || (cd emacs       ; make all)"

all:
	cd emulator	; make all
	sh -c "test ! -d compiler_pl || (cd compiler_pl ; make all)"
	cd runtime	; make all
	cd mpimos	; make all
	cd compiler	; make all
	sh -c "test ! -d debug_utl   || (cd debug_utl   ; make all)"
	sh -c "test ! -d pimos_utl   || (cd pimos_utl   ; make all)"
	sh -c "test ! -d emacs       || (cd emacs       ; make all)"

install:
	cd emulator	; make install
	sh -c "test ! -d emacs       || (cd emacs       ; make install)"
	cp pdsscmp $(BINDIR)/pdsscmp.x
	mv -f $(BINDIR)/pdsscmp.x $(BINDIR)/pdsscmp

clean:
	cd emulator	; make clean
	sh -c "test ! -d compiler_pl || (cd compiler_pl ; make clean)"
	cd runtime	; make clean
	cd mpimos	; make clean
	cd compiler	; make clean
	sh -c "test ! -d debug_utl   || (cd debug_utl   ; make clean)"
	sh -c "test ! -d pimos_utl   || (cd pimos_utl   ; make clean)"
	sh -c "test ! -d emacs       || (cd emacs       ; make clean)"
