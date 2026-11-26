#!/bin/sh
# The pim checks that run in about a minute: the ten generated-doc checks
# and the PSI tests.  Run from anywhere; prints one line per failing check
# and a final verdict line.  Output of each check goes to $QC_LOG
# (default: a mktemp file, printed at the end on failure).
#
#   tools/quick_checks.sh            # doc checks + PSI tests
#   QC_WIN=1 tools/quick_checks.sh   # also bsv/run_win_tb.sh (~2 min)
#
# Exit 0 when everything passes, 1 otherwise.  The full regression suite is
# ./run_tests.sh (with tools/suite_verdict.py on its log); this is not it.
set -u
cd "$(dirname "$0")/.."
LOG=${QC_LOG:-$(mktemp -t pim_quick_checks)}
: > "$LOG"
BSC_PIN=/opt/homebrew/Cellar/bsc/2026.01/bin
[ -d "$BSC_PIN" ] && PATH=$BSC_PIN:$PATH && export PATH
fail=0
n=0
run() {
    n=$((n + 1))
    echo "### $*" >> "$LOG"
    if ! "$@" >> "$LOG" 2>&1; then
        echo "FAIL $*"
        fail=$((fail + 1))
    fi
}
for c in gen_isa_table census namemap kbn kbndis inventory bltdir pimm_stubs \
         psdpim mekbn; do
    run python3 "asm/$c.py" --check
done
run python3 ref/pu/check_pu.py
run python3 asm/fep_services/savpreds.py --check
run python3 asm/ptfdump.py --check
run python3 psi/fepread/check.py
for t in psi/test_*.py; do
    run python3 "$t"
done
if [ "${QC_WIN:-0}" = 1 ]; then
    run bsv/run_win_tb.sh
fi
if [ $fail = 0 ]; then
    echo "quick_checks: PASS ($n checks)"
    [ -z "${QC_LOG:-}" ] && rm -f "$LOG"
    exit 0
fi
echo "quick_checks: FAIL ($fail of $n; log $LOG)"
exit 1
