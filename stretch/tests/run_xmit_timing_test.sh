#!/bin/sh
# Build and run mkXmitTimingTb: a TRANSMIT's time by destination (Perf.
# Char. Vol. 1 Table 9, printed p.3-14, PDF 32; Vol. 2 PDF 106-107) and the
# transmit loop's pacer (bsv/StretchXmitTiming.bsv; fidelity_plan.md A7,
# 2026-11-27).  The pattern and the private build directories are
# run_laparts_test.sh's.
set -e
TESTS_DIR="$(cd "$(dirname "$0")" && pwd)"
BSV_DIR="$TESTS_DIR/../bsv"
export BLUESPECDIR=/opt/homebrew/Cellar/bsc/2026.01/libexec/lib
export PATH=/opt/homebrew/Cellar/bsc/2026.01/bin:$PATH
BSC=/opt/homebrew/Cellar/bsc/2026.01/bin/bsc
cd "$BSV_DIR"
mkdir -p build-xmittiming simbuild-xmittiming
"$BSC" -sim -simdir simbuild-xmittiming -bdir build-xmittiming -info-dir build-xmittiming \
       -g mkXmitTimingTb -u StretchXmitTiming.bsv +RTS -K512m -RTS
"$BSC" -sim -simdir simbuild-xmittiming -bdir build-xmittiming -e mkXmitTimingTb \
       -o xmittiming_sim +RTS -K512m -RTS
./xmittiming_sim
