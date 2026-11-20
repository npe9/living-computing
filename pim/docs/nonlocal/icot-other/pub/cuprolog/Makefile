RESULTS = sumo.result

############################################################

TMPDIR=/usr/tmp

SHELL = /bin/sh
RM = /bin/rm
MV = /bin/mv
SED = /bin/sed
EMACS = nemacs

.SUFFIXES: .test .result

.test.result:
	@${RM} -f $@
	@DISPLAY='' PWD=`pwd` EMACSLOADPATH=/db/Quixote/v3/SS/lib/emacs \
	${EMACS} -batch  $< -l qxt-all -l qxt-test.el -f qxt-test -kill

all: diff

result:  ${RESULTS}

expected: result
	@for RESULT in ${RESULTS}; do \
		(EXPECTED=`basename $$RESULT .result`.expected; \
		 ${RM} -f $$EXPECTED; \
		 ${MV} $$RESULT $$EXPECTED); \
	done
	@echo 'moving *.result to *.expected'

diff: result
	-@for RESULT in ${RESULTS}; do \
	    (EXPECTED=`basename $$RESULT .result`.expected; \
	     if [ -f $$EXPECTED ]; then \
		 echo "Checking the difference ($$EXPECTED, $$RESULT)..."; \
		 ${SED} -e "s/^\*\*.*$$//" $$RESULT > ${TMPDIR}/$$RESULT; \
		 ${SED} -e "s/^\*\*.*$$//" $$EXPECTED > ${TMPDIR}/$$EXPECTED; \
		 (cd ${TMPDIR}; diff -c $$EXPECTED $$RESULT); \
	     else \
		echo "No such file: $$EXPECTED."; \
		echo "Please run 'make expected'."; \
		exit 1; \
	     fi); \
	done

clean:
	${RM} -f *.result

veryclean:
	${RM} -f *.result *.expected
