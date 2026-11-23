#!/bin/sh
# Lockstep: PIMOS predicates from the IPL image on the Bluespec PIM/m
# core, the trace compared line for line with the reference model's.
# One driver bench (PimmDriverTb.bsv) executes each test's script
# (ref/pimm/lockstep_*.py, ref/pimm/driver.py).
# Objects go to build_pimm/, never beside the sources: a stale .bo
# there would be picked up by the other benches.
set -eu
cd "$(dirname "$0")"

BSC=${BSC_BIN:-}
if [ -z "$BSC" ]; then
  BSC=$(ls -d /opt/homebrew/Cellar/bsc/*/bin/bsc 2>/dev/null | sort | tail -1)
fi
if [ -z "$BSC" ] || [ ! -x "$BSC" ]; then
  echo "bsc not found; set BSC_BIN to the 2026.01 bsc binary" >&2
  exit 1
fi

BLUESPECDIR=$(cd "$(dirname "$BSC")/../libexec/lib" && pwd)
export BLUESPECDIR
PATH=$(dirname "$BSC"):$PATH
export PATH

python3 ../asm/gen_pimm_bsv.py generated
mkdir -p build_pimm
"$BSC" -sim -p generated:+ -bdir build_pimm -simdir build_pimm -info-dir build_pimm \
  -g mkPimmDriverTb -u PimmDriverTb.bsv > build_pimm/compile.log 2>&1 \
  || { cat build_pimm/compile.log; exit 1; }
"$BSC" -sim -bdir build_pimm -simdir build_pimm -e mkPimmDriverTb \
  -o build_pimm/sim_pimm_driver >> build_pimm/compile.log 2>&1 \
  || { cat build_pimm/compile.log; exit 1; }

# Each test writes its script, the driver executes it, the test
# compares the trace with the reference model's.
for t in jtoa conv get4 ccode asf repl ground rpos dec0 rss dect deca gca modc lmod ext ptab pack newm file file3 pool load mrb atab cons run link unif s32; do
  python3 ../ref/pimm/lockstep_$t.py --script generated/pimm_script.hex
  ./build_pimm/sim_pimm_driver | python3 ../ref/pimm/lockstep_$t.py
done
