#!/bin/sh
# The FEP emulator (PimmFepEmu.bsv) against ref/pimm/fep.py, in Bluesim.
#
# Builds mkPimmFepEmuTb (the emulator over a card image file, through
# PimmSdBlockFile's BDPI) and mkPimmFepEmuSpiTb / mkPimmFepEmuSpiSdscTb
# (the same emulator over the SPI-mode SD reader PimmSdBlock.bsv, the
# module the board synthesizes, and a card model, PimmSdCardModel.bsv,
# block- and byte-addressed); then bsv/fepemu_check.py replays
# every tape in ref/pimm/fep_tapes/ (the commands ref_scsi.py's parts gave
# fep.py, the "direct" and "direct kernel" sequences, and the "kernel"
# tape of PIMOS's start) into each, and compares each answer
# with fep.py's, byte for byte.  Everything is written to
# bsv/build_fepemu/ (FEPEMU_BUILD to override); nothing outside it.
# Use BSC_BIN to pin a compiler, as in run_sdram_tb.sh.
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

B=${FEPEMU_BUILD:-build_fepemu}
mkdir -p "$B"
FLAGS="-steps-warn-interval 4000000 -bdir $B -simdir $B -info-dir $B"

build() {   # top, source, simulator
  "$BSC" -sim -u -g "$1" $FLAGS "$2" > "$B/$1.bsc.log" 2>&1 || { cat "$B/$1.bsc.log"; exit 1; }
  (cd "$B" && "$BSC" -sim -e "$1" -bdir . -simdir . -o "$3" \
     ../PimmSdBlockFile.c ../PimmFepEmuTb.c > "$1.link.log" 2>&1) || { cat "$B/$1.link.log"; exit 1; }
}

echo "== bsc: mkPimmFepEmuTb (the emulator over the image file)"
build mkPimmFepEmuTb PimmFepEmuTb.bsv sim_fepemu
SIMS="$B/sim_fepemu"
echo "== bsc: mkPimmFepEmuSpiTb, mkPimmFepEmuSpiSdscTb (the emulator over the SPI reader"
echo "   PimmSdBlock.bsv and a card model: block-addressed v2, byte-addressed v1)"
build mkPimmFepEmuSpiTb PimmFepEmuSpiTb.bsv sim_fepemu_spi
build mkPimmFepEmuSpiSdscTb PimmFepEmuSpiTb.bsv sim_fepemu_spi_sdsc
SIMS="$SIMS $B/sim_fepemu_spi $B/sim_fepemu_spi_sdsc"

echo "== the direct tapes are what record_fep.py makes now (the kernel tape needs"
echo "   a saved machine: record_fep.py --kernel PKL --type shutdown --type yes --check,"
echo "   by hand)"
python3 ../ref/pimm/record_fep.py --check --part direct
python3 ../ref/pimm/record_fep.py --check --part direct_kernel

status=0
for sim in $SIMS; do
  echo "== $sim"
  python3 fepemu_check.py "$sim" || status=1
done
if [ $status -ne 0 ]; then
  echo "run_fepemu: FAIL"
  exit 1
fi
echo "run_fepemu: PASS"
