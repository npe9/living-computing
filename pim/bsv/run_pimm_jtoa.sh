#!/bin/sh
# Lockstep: jis_to_ascii:convert_element/2 from the IPL image on the
# Bluespec PIM/m core, its trace compared line for line with the
# reference model's (ref/pimm/lockstep_jtoa.py).
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
  -g mkPimmJtoaTb -u PimmJtoaTb.bsv > build_pimm/compile.log 2>&1 \
  || { cat build_pimm/compile.log; exit 1; }
"$BSC" -sim -bdir build_pimm -simdir build_pimm -e mkPimmJtoaTb \
  -o build_pimm/sim_pimm_jtoa >> build_pimm/compile.log 2>&1 \
  || { cat build_pimm/compile.log; exit 1; }
./build_pimm/sim_pimm_jtoa | python3 ../ref/pimm/lockstep_jtoa.py
