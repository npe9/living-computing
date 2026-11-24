#!/bin/sh
# The FEP emulator on the ULX3S: its self-test in Bluesim, then the
# bitstream (yosys, nextpnr-ecp5, ecppack), the pattern of
# run_fpga_build.sh.  ALL OURS.
#
#   1. a card image of the held system (tools/mkfepcard.py --held) in the
#      build directory;
#   2. Bluesim: mkPimmFepUlx3sTb, the board's self-test over the SPI
#      reader and a card model on that image: it must print PASS;
#   3. bsc -verilog mkPimmFepUlx3s; yosys synth_ecp5 (top ulx3s_fep_top,
#      PimmFepTop.v); nextpnr-ecp5 --85k CABGA381 with ulx3s_fep.lpf;
#      ecppack.  Reports LUTs, flip-flops, BRAM and Fmax.
#
# IT DOES NOT TOUCH A BOARD OR A CARD: no openFPGALoader, no serial port,
# no device file.  Programming the board and writing a card are the
# owner's steps (bsv/README.md "The FEP emulator on the ULX3S").
# FEPFPGA_BUILD overrides the build directory (deleted and remade).
set -eu
cd "$(dirname "$0")"

BUILD=${FEPFPGA_BUILD:-fpga_build_fepemu}
die() { echo "run_fepemu_fpga: $*" >&2; exit 1; }

BSC=${BSC_BIN:-}
if [ -z "$BSC" ]; then
  BSC=$(ls -d /opt/homebrew/Cellar/bsc/*/bin/bsc 2>/dev/null | sort | tail -1)
fi
[ -n "$BSC" ] && [ -x "$BSC" ] || die "bsc not found; set BSC_BIN"
BLUESPECDIR=$(cd "$(dirname "$BSC")/../libexec/lib" && pwd)
export BLUESPECDIR
PATH=$(dirname "$BSC"):$PATH
export PATH
for tool in python3 yosys nextpnr-ecp5 ecppack; do
  command -v "$tool" >/dev/null 2>&1 || die "required tool not found: $tool"
done

rm -rf "$BUILD"
mkdir -p "$BUILD/bsc" "$BUILD/verilog" "$BUILD/sim"
echo "== build dir: bsv/$BUILD"

echo "== card image: tools/mkfepcard.py --held"
python3 ../tools/mkfepcard.py "$BUILD/held.img" --held
python3 ../tools/mkfepcard.py --list "$BUILD/held.img" | head -4

echo "== Bluesim: mkPimmFepUlx3sTb (the self-test over the SPI reader and a card model)"
"$BSC" -sim -u -g mkPimmFepUlx3sTb -steps-warn-interval 4000000 \
  -bdir "$BUILD/sim" -simdir "$BUILD/sim" -info-dir "$BUILD/sim" PimmFepUlx3sTb.bsv \
  > "$BUILD/sim/bsc.log" 2>&1 || { cat "$BUILD/sim/bsc.log"; die "bsc (sim) failed"; }
(cd "$BUILD/sim" && "$BSC" -sim -e mkPimmFepUlx3sTb -bdir . -simdir . -o sim_selftest \
  ../../PimmSdBlockFile.c > link.log 2>&1) || { cat "$BUILD/sim/link.log"; die "link failed"; }
PIMM_SD_IMAGE="$BUILD/held.img" "$BUILD/sim/sim_selftest" | tee "$BUILD/sim/selftest.out"
grep -q "^fepselftest: PASS" "$BUILD/sim/selftest.out" || die "the self-test does not pass in Bluesim"

echo "== bsc: mkPimmFepUlx3s -> Verilog"
"$BSC" -verilog -u -g mkPimmFepUlx3s -steps-warn-interval 4000000 \
  -bdir "$BUILD/bsc" -vdir "$BUILD/verilog" -info-dir "$BUILD/bsc" PimmFepUlx3s.bsv \
  > "$BUILD/bsc.log" 2>&1 || { cat "$BUILD/bsc.log"; die "bsc (verilog) failed"; }

echo "== yosys: synth_ecp5"
V="$BLUESPECDIR/Verilog"
yosys -l "$BUILD/yosys.log" -p "
  read_verilog $BUILD/verilog/mkPimmFepUlx3s.v $BUILD/verilog/mkPimmFepEmu.v PimmFepTop.v
  read_verilog $V/FIFO2.v $V/FIFO20.v $V/FIFO1.v $V/SizedFIFO.v $V/BRAM1.v
  hierarchy -top ulx3s_fep_top
  synth_ecp5 -top ulx3s_fep_top -json $BUILD/top.json
" > "$BUILD/yosys.console" 2>&1 || { tail -30 "$BUILD/yosys.console" >&2; die "yosys failed"; }

echo "== nextpnr-ecp5: place and route"
nextpnr-ecp5 --85k --package CABGA381 --speed 6 \
  --json "$BUILD/top.json" --lpf ulx3s_fep.lpf --textcfg "$BUILD/top.config" \
  --log "$BUILD/nextpnr.log" --seed 1 --timing-allow-fail \
  > "$BUILD/nextpnr.console" 2>&1 || { tail -30 "$BUILD/nextpnr.console" >&2; die "nextpnr failed"; }

echo "== ecppack: bitstream"
ecppack --compress --input "$BUILD/top.config" --bit "$BUILD/ulx3s_fep.bit" \
  > "$BUILD/ecppack.console" 2>&1 || die "ecppack failed"
[ -s "$BUILD/ulx3s_fep.bit" ] || die "no bitstream"

echo
echo "== FEP emulator FPGA build result"
grep -E "Total LUT4s|logic LUTs|carry LUTs|RAM LUTs|DP16KD:|TRELLIS_IO:" "$BUILD/nextpnr.log" | head -6 || true
grep -E "^ +(LUT4|TRELLIS_FF|CCU2C|DP16KD) " "$BUILD/yosys.log" | tail -4 | sed 's/^/   yosys: /' || true
grep "Max frequency for clock" "$BUILD/nextpnr.log" | tail -1
echo "   bitstream: bsv/$BUILD/ulx3s_fep.bit (not loaded: the board is the owner's step)"
echo "run_fepemu_fpga: PASS (self-test PASS in Bluesim; flow completed)"
