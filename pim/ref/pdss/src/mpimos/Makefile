PDSSCMP = ../pdsscmp +s
PDSSASM = ../emulator/pdssasm
PARA	=

MPIMOS	=	boot.sav op.sav optbl.sav \
		parser.sav unparser.sav shell.sav macro_ex.sav \
		task_monitor.sav utl.sav code_man.sav module_pool.sav \
		window.sav window_man.sav window_drv.sav \
		file.sav file_man.sav file_drv.sav \
		dir.sav dir_drv.sav timer_man.sav \
		dummy_window.sav dummy_file.sav dummy_dir.sav \
		builtin.sav cmd_basic.sav cmd_code.sav cmd_debug.sav \
		cmd_dir.sav cmd_env.sav cmd_utl.sav pool_mli.sav \
		mpimos_iodev.sav mpimos_windev.sav \
		mpimos_fildev.sav mpimos_timdev.sav

all: $(PARA)	$(MPIMOS)

install:

clean:

reassm:
	for f in `echo $(MPIMOS) | sed 's/\.sav//g'`; do $(PDSSASM) $$f; done

.SUFFIXES:	.kl1 .asm .sav
.kl1.sav:
	$(PDSSCMP) $*.kl1
.kl1.asm:
	$(PDSSCMP) -a $*.kl1
.asm.sav:
	$(PDSSASM) $*
