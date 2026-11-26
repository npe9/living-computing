#!/bin/sh
# The window hardware on the ULX3S (docs/simpos/window_hardware_plan.md
# H3): bsc -verilog mkWinUlx3s (WinUlx3s.bsv), yosys synth_ecp5 (top
# ulx3s_win_top, WinUlx3sTop.v), nextpnr-ecp5 --85k CABGA381 -6 on
# ulx3s_win.lpf for each seed in SEEDS (default "1 2 3"), ecppack.  The
# pattern of run_fepemu_fpga.sh.  ALL OURS.
#
#   1. the self-test's load files in the build directory: test_11's font
#      (psi/winfb.py fonthex, from the held archive), the `mode0` case's
#      drawing stream and scan configuration (psi/winscan.py stream,
#      config);
#   2. the video PLL: ecppll -n win_pll -i 25 -o 370 --clkout1 74 (mode 0,
#      plan §5.2);
#   3. bsc -verilog, yosys, then per seed nextpnr and ecppack;
#   4. THE CHECKS, per seed (the script fails if any fails; nextpnr runs
#      with --timing-allow-fail only so that every figure is reported):
#        - each clock's Fmax PASSes its constraint (the 25 MHz system
#          clock, the 74 MHz pixel clock, the 370 MHz shift clock);
#        - DP16KD = WIN_DP16KD (default 156, yosys's mapping MEASURED
#          2026-11-25: the frame's 80 banks of 1,024 x 16, the save areas'
#          65,536 x 16, the font's 4,096 x 16, the index's 8,869 x 8, the
#          self-test's 512 x 104 stream and 160 x 32 configuration), so a
#          frame that is no longer banked by hand, or a RAM mapped to
#          logic, fails;
#        - THE SERIALIZER'S LOAD PHASE: nextpnr 0.6 times each PLL output
#          as its own clock and only REPORTS a pclk -> sclk path ("Max
#          delay <pclk> -> <sclk>"); it has no multicycle or max-delay
#          constraint for it.  So this script is the constraint: the
#          reported pclk -> sclk delay must be at most WIN_XDOM_NS
#          (default 2.70 ns, one shift period at 370 MHz).  The word is
#          sampled two or three shift clocks after the pixel edge that
#          launches it (WinScanOut.bsv mkWinTmdsSer), so its budget is two
#          periods (5.40 ns) less the CLKOP/CLKOS skew; one period is
#          checked, leaving the other for that skew.  The check is the
#          script's, not the tool's.
#        - the serializer's 8 load flags and 3 sample enables are 11
#          separate flops in the netlist (a yosys `keep`, set after
#          `proc`; without it opt_merge folds equal flops into one, which
#          undoes the replication: 4 of 11 were seen before the select
#          was fixed, MEASURED 2026-11-25).
#      Any other cross-domain path reported (sys -> pclk: the scan
#      command FIFO, the resets) goes through a synchronizer and is
#      printed, not checked.
#
# IT DOES NOT TOUCH THE BOARD: no openFPGALoader, no serial port, no
# device file.  Loading the bitstream is the owner's step (plan §5.4,
# bsv/README.md "The SIMPOS window framebuffer").
# WINFPGA_BUILD overrides the build directory (deleted and remade); it
# must stay gitignored (build-*/): the bitstream holds the held font.
set -eu
cd "$(dirname "$0")"

BUILD=${WINFPGA_BUILD:-build-winfpga}
SEEDS=${SEEDS:-"1 2 3"}
XDOM_NS=${WIN_XDOM_NS:-2.70}
WANT_DP16KD=${WIN_DP16KD:-156}
die() { echo "run_win_fpga: $*" >&2; exit 1; }

BSC=${BSC_BIN:-}
if [ -z "$BSC" ]; then
  BSC=$(ls -d /opt/homebrew/Cellar/bsc/*/bin/bsc 2>/dev/null | sort | tail -1)
fi
[ -n "$BSC" ] && [ -x "$BSC" ] || die "bsc not found; set BSC_BIN"
BLUESPECDIR=$(cd "$(dirname "$BSC")/../libexec/lib" && pwd)
export BLUESPECDIR
PATH=$(dirname "$BSC"):$PATH
export PATH
for tool in python3 yosys nextpnr-ecp5 ecppack ecppll; do
  command -v "$tool" >/dev/null 2>&1 || die "required tool not found: $tool"
done

rm -rf "$BUILD"
mkdir -p "$BUILD/bsc" "$BUILD/verilog"
echo "== build dir: bsv/$BUILD"
echo "   $(yosys -V)"
echo "   $(nextpnr-ecp5 --version 2>&1 | head -1)"
echo "   $(ecppack --help 2>&1 | grep -i 'version' | head -1)"

echo "== the self-test's load files (font, the mode0 test card, its configuration)"
python3 -I ../psi/winfb.py fonthex "$BUILD/win_font.hex"
python3 -I ../psi/winscan.py stream mode0 > "$BUILD/win_stream.hex"
python3 -I ../psi/winscan.py config mode0 > "$BUILD/win_scan.hex"
echo "   $(grep -c . "$BUILD/win_stream.hex") stream records, $(grep -c . "$BUILD/win_scan.hex") configuration words"

echo "== ecppll: the mode 0 video PLL"
ecppll -n win_pll -i 25 -o 370 --clkout1 74 -f "$BUILD/win_pll.v" > "$BUILD/ecppll.log" 2>&1 || { cat "$BUILD/ecppll.log"; die "ecppll failed"; }
grep -E "frequency|VCO" "$BUILD/ecppll.log" | sed 's/^/   /'

echo "== bsc: mkWinUlx3s -> Verilog"
"$BSC" -verilog -u -g mkWinUlx3s -steps-warn-interval 4000000 \
  -bdir "$BUILD/bsc" -vdir "$BUILD/verilog" -info-dir "$BUILD/bsc" WinUlx3s.bsv \
  > "$BUILD/bsc.log" 2>&1 || { cat "$BUILD/bsc.log"; die "bsc (verilog) failed"; }

# synth_ecp5's own script, run in its labelled parts, with the `coarse`
# part spelled out WITHOUT `share` (yosys 0.51's list, `yosys -h
# synth_ecp5`): share merged the box's multipliers of exclusive rules
# (accept's y x 80, the line's address, the glyph index's row x 94) into
# one, with its input muxes, and the system clock's critical path ran
# from accept's command through it to the index RAM's write enables
# (22.89 MHz, MEASURED 2026-11-25).  The cursor planes (8 x 16 x 32) are
# kept in LUT RAM (ram_style distributed): since the H3 follow-up their
# address is registered (WinScanOut.bsv mkWinCursor's two-clock lookup),
# and yosys then put them in a 157th DP16KD (MEASURED 2026-11-26).
echo "== yosys: synth_ecp5 (without share)"
V="$BLUESPECDIR/Verilog"
# run from the build directory, where $readmemh finds the load files
(cd "$BUILD" && yosys -l yosys.log -p "
  read_verilog -D BSV_NO_INITIAL_BLOCKS verilog/mkWinUlx3s.v
  read_verilog $(pwd)/../WinUlx3sTop.v win_pll.v
  read_verilog -defer -D BSV_NO_INITIAL_BLOCKS $V/BRAM1Load.v
  read_verilog -D BSV_NO_INITIAL_BLOCKS $V/BRAM1.v $V/BRAM2.v $V/FIFO2.v $V/SizedFIFO.v $V/SyncFIFO.v $V/SyncResetA.v $V/RegFile.v
  hierarchy -top ulx3s_win_top
  proc
  select -set ldff w:ser_ld_* w:ser_sm_* %u %ci1:+\$dff[Q] t:\$dff %i
  select -list @ldff
  setattr -set keep 1 @ldff
  synth_ecp5 -top ulx3s_win_top -run begin:coarse
  proc; flatten; tribuf -logic; deminout; opt_expr; opt_clean; check
  opt -nodffe -nosdff; fsm; opt; wreduce; peepopt; opt_clean
  techmap -map +/cmp2lut.v -D LUT_WIDTH=4; opt_expr; opt_clean
  techmap -map +/mul2dsp.v -map +/ecp5/dsp_map.v -D DSP_A_MAXWIDTH=18 -D DSP_B_MAXWIDTH=18 -D DSP_A_MINWIDTH=2 -D DSP_B_MINWIDTH=2 -D DSP_NAME=\$__MUL18X18
  chtype -set \$mul t:\$__soft_mul
  alumacc; opt; memory -nomap; opt_clean
  setattr -set ram_style \"distributed\" ulx3s_win_top/*cursor_planes*
  synth_ecp5 -top ulx3s_win_top -run map_ram: -json top.json
" > yosys.console 2>&1) || { tail -30 "$BUILD/yosys.console" >&2; die "yosys failed"; }
grep -E "^ +(LUT4|TRELLIS_FF|CCU2C|DP16KD|ODDRX1F|EHXPLLL|TRELLIS_DPR16X4|PFUMX|L6MUX21) " "$BUILD/yosys.log" | tail -8 | sed 's/^/   yosys: /' || true
# the serializer's replicated flags (8 load, 3 sample) must survive as
# separate flops: yosys merges equal flops unless they are kept
nrep=$(python3 -I -c 'import json, re, sys
c = json.load(open(sys.argv[1]))["modules"]["ulx3s_win_top"]["cells"]
print(sum(1 for n in c if re.fullmatch(r"win\.ser_(ld|sm)_\d+_TRELLIS_FF_Q", n)))' "$BUILD/top.json")
echo "   serializer flags kept: $nrep of 11"
[ "$nrep" -eq 11 ] || die "the serializer's replicated load/sample flags were merged ($nrep of 11)"

fail=0
for seed in $SEEDS; do
  S="$BUILD/s$seed"
  mkdir -p "$S"
  echo "== nextpnr-ecp5: seed $seed"
  nextpnr-ecp5 --85k --package CABGA381 --speed 6 \
    --json "$BUILD/top.json" --lpf ulx3s_win.lpf --textcfg "$S/top.config" \
    --log "$S/nextpnr.log" --report "$S/report.json" --seed "$seed" --timing-allow-fail \
    > "$S/nextpnr.console" 2>&1 || { tail -30 "$S/nextpnr.console" >&2; die "nextpnr failed (seed $seed)"; }
  ecppack --compress --input "$S/top.config" --bit "$S/ulx3s_win.bit" \
    > "$S/ecppack.console" 2>&1 || die "ecppack failed (seed $seed)"
  [ -s "$S/ulx3s_win.bit" ] || die "no bitstream (seed $seed)"
  if ! python3 -I ../tools/win_fpga_check.py "$S/nextpnr.log" "$XDOM_NS" "$WANT_DP16KD" seed "$seed"; then
    fail=1
  fi
done

# the bitstream the owner is told to load exists only if every seed passed
[ $fail -eq 0 ] || die "FAIL (a check above failed; no bsv/$BUILD/ulx3s_win.bit)"
cp "$BUILD/s$(echo $SEEDS | awk '{print $1}')/ulx3s_win.bit" "$BUILD/ulx3s_win.bit"
echo "   bitstream: bsv/$BUILD/ulx3s_win.bit (seed $(echo $SEEDS | awk '{print $1}'); not loaded: the board is the owner's step)"
echo "run_win_fpga: PASS (all seeds: every clock meets its constraint, DP16KD = $WANT_DP16KD, pclk -> sclk <= $XDOM_NS ns)"
