#!/bin/sh
# Boot the shipped 1e kernel, s9term, on the Hobbit SoC in Verilator -- the
# gated core, the memory adapter, the SDRAM controller and an SDRAM model,
# the host link -- and compare every retirement record with the reference
# boot's, as bsv/run_p9kern.sh does for the bare core (fpga/README.md,
# "Verification").
#
#   fpga/sim/run_soc.sh RECORDS [WORKDIR]
#
# RECORDS: how many records of the reference boot to record and compare
# (125203 reaches `main`).  WORKDIR defaults to fpga/build/socsim.
# SOC_KEEP_SIM=1 reuses the simulator already built there.
# SOC_LOAD=1 loads RAM and the ROM block through the UART pins with
# tools/p9link.py's stream (B frames, then G) instead of the back door, so
# the host link's load path and the adapter's aux port are exercised too.
#
# Result, 2026-11-24: `run_soc.sh 2893000` prints "MATCH: 2893000 records
# agree in every field but cyc (2865913 also agree in cyc)" and "SOC
# console: 74 bytes, identical", at 10.58 system clocks per core clock.
#
# Discriminating: with the page-entry probe dropped (bsv/HobbitMmu.bsv,
# walkProbeFn: `v[1] = tagged Valid pteAddr(ste0, r.va);` made
# `v[1] = tagged Invalid;`), so the adapter no longer fetches the PTE a
# paged walk reads, the run OBSERVED: "P9KERN FAIL: device write 00000000
# to ffffefa4 after record 2849644" and "FAIL at record 2849643: pc, insn,
# sp_before, sp_after, msp_before, msp_after, we, addr, data, mask differ
# (last function reached before it: gotolabel)" -- the first record after
# the store to ffffefb0, a paged address; rc=1.  Reverted by the reverse
# patch; the file compared identical to its pre-injection copy.
#
# SOC_LOAD=1 run_soc.sh 2893000, 2026-11-24: "SOC load: 768 replies, 0
# frames unsent", then the same MATCH and console (10.17 system clocks
# per core clock).  Discriminating: with hostlink.v's B address step
# `mem_addr + 4` made `mem_addr + 8`, OBSERVED: "P9KERN FAIL: device write
# 00000000 to fffffff4 after record 3" and "FAIL at record 3: insn, we,
# addr, mask differ (last function reached before it: _startup)" (the
# core fetched insn 00000000 at 80004004); rc=1.  Reverted by the reverse
# patch; identical to the pre-injection copy.
#
# The core's arrays read on the system clock (fpga/README.md, "The core's
# arrays on the system clock"): the run is built from sysram_filter.py's
# netlist, and the HOBBIT_SIM checks (SYSRAM STALE, PROBE STALE, WINDOW
# DUPLICATE, EDGE STALE) fail it.  With the area milestones of
# docs/fpga_area.md, 2026-11-24: the same MATCH, all 2,893,027 HRI lines
# byte-identical to the run before them, 9,920,333 core clocks.
# Discriminating, each in a scratch copy of the tree, run_soc.sh 300000,
# OBSERVED: hobbit_sysregfile.v's read register clocked on CLK instead of
# SYSCLK, "SYSRAM STALE TOP.soc_sim_top.soc.cpu.core_c_pf_way0 at system
# clock 5106: a 2/1/0/1/0", 0 records, rc=1; hobbit_soc_mem.v's S_CHECK
# counting every probe a hit, "PROBE STALE at core clock 0: probe 21
# 00000000 not in the window", rc=1; S_CHECK treating a hit as a miss
# when wptr is 3, "WINDOW DUPLICATE at 0: entries 2 and 3 both hold
# 80000000", 2245 records, rc=1.
#
# Byte enables and device reads (fpga/README.md, "Byte enables and device
# reads"), 2026-11-24: run_soc.sh 2893000 gave the same MATCH and HRI lines
# byte-identical, with "181 of 181 recorded reads replayed, 0 repeated, 0
# unrecorded" (16,316 unrecorded before: 16,314 merge reads of LCD
# registers and 2 speculative SONIC reads), 181 forwarded reads (was
# 16,497), and 9,920,614 core clocks (was 9,920,333: the declined
# speculative reads wait for the instructions ahead).  Discriminating,
# OBSERVED: the adapter's write enables forced to 4'hF, "P9KERN FAIL:
# device write 00000000 to b0003000 after record 2474518 has byte enables
# f; the recording's mask is 3", rc=1; EU_S1's speculation flag forced
# False (HobbitCore fetchOperand `!drained` made `False`), "2 unrecorded"
# and "run_soc.sh: the SoC read a device register the reference boot did
# not read", rc=1.  Each in a scratch copy, the tree itself untouched.
set -eu
here=$(cd "$(dirname "$0")" && pwd)
fpga=$(dirname "$here")
hobbit=$(dirname "$fpga")
n=${1:?usage: run_soc.sh RECORDS [WORKDIR]}
work=${2:-$fpga/build/socsim}
mkdir -p "$work/rec" "$work/obj"
work=$(cd "$work" && pwd)

BSC=${BSC_BIN:-$(ls -d /opt/homebrew/Cellar/bsc/*/bin/bsc 2>/dev/null | sort | tail -1)}
BLUESPECDIR=$(cd "$(dirname "$BSC")/../libexec/lib" && pwd)
export BLUESPECDIR

PYTHONDONTWRITEBYTECODE=1 python3 "$hobbit/tools/p9coreboot.py" record \
    "$work/rec" --max-steps "$n"

if [ "${SOC_KEEP_SIM:-0}" != 1 ] || [ ! -x "$work/obj/Vsoc_sim_top" ]; then
  mkdir -p "$work/bsc"
  "$BSC" +RTS -K512M -RTS -verilog -g mkHobbitSocCpu -u \
      -vdir "$work/bsc" -bdir "$work/bsc" -info-dir "$work/bsc" \
      -p "$hobbit/bsv:$BLUESPECDIR/Libraries" "$hobbit/bsv/HobbitSocCpu.bsv" \
      > "$work/bsc.log" 2>&1 || { tail -30 "$work/bsc.log"; exit 1; }
  # The core's arrays read on the system clock, as on the board.
  python3 "$fpga/sysram_filter.py" "$work/bsc/mkHobbitSocCpu.v" \
      "$work/bsc/mkHobbitSocCpu.sys.v"
  ${CC:-cc} -O2 -c "$hobbit/bsv/p9kern.c" -o "$work/p9kern.o"
  rm -f "$work/obj/Vsoc_sim_top"
  verilator --cc --exe --build -j "${VL_JOBS:-4}" -O3 \
      --x-assign fast --x-initial fast --no-timing \
      -Wno-fatal -Wno-lint -Wno-style -Wno-STMTDLY -Wno-MULTIDRIVEN \
      -DHOBBIT_SIM ${SOC_SETTLE:+-DHOBBIT_SOC_SETTLE=$SOC_SETTLE} \
      --top-module soc_sim_top -y "$BLUESPECDIR/Verilog" -Mdir "$work/obj" \
      -CFLAGS "-O2" \
      "$work/bsc/mkHobbitSocCpu.sys.v" "$fpga/rtl/hobbit_sysregfile.v" \
      "$fpga/rtl/uart8n1.v" "$fpga/rtl/hostlink.v" \
      "$fpga/rtl/sdram_word.v" "$fpga/rtl/hobbit_soc_mem.v" "$fpga/rtl/hobbit_soc.v" \
      "$here/sdram_model.v" "$here/soc_sim_top.v" "$here/soc_main.cpp" \
      "$work/p9kern.o" > "$work/verilator.log" 2>&1 || { tail -30 "$work/verilator.log"; exit 1; }
fi

loadfile=""
if [ "${SOC_LOAD:-0}" = 1 ]; then
  PYTHONDONTWRITEBYTECODE=1 python3 "$hobbit/tools/p9link.py" emit \
      "$work/load.bin" --sparse
  loadfile="$work/load.bin"
fi

simstatus=0
(cd "$work" && SOC_LOAD="$loadfile" P9KREC="$work/rec/boot.rec" P9KCONSOLE="$work/console" \
    SOC_ROM="$hobbit/tools/p9kbuild/fpi.rom" SOC_IOLOG="$work/io.log" \
    ./obj/Vsoc_sim_top > "$work/core.log" 2>&1) || simstatus=$?
grep '^SOC\|^P9KERN\|STALE\|DUPLICATE' "$work/core.log" || true
# The arrays' and the probes' freshness checks (HOBBIT_SIM in
# rtl/hobbit_sysregfile.v and rtl/hobbit_soc_mem.v) stop the run.
stale=0
if grep -q 'STALE\|DUPLICATE' "$work/core.log"; then
  echo "run_soc.sh: a core edge came before the core's logic had settled" >&2
  stale=1
fi

fail=0
python3 "$hobbit/tools/p9coreboot.py" compare "$work/rec/ref.hri" \
    "$work/core.log" --functions "$work/rec/functions" || fail=1
touch "$work/console"
if cmp -s "$work/console" "$work/rec/console"; then
  echo "SOC console: $(wc -c < "$work/console" | tr -d ' ') bytes, identical to the reference boot's"
else
  echo "run_soc.sh: the console differs from the reference boot's" >&2
  fail=1
fi
# A device register read is a side effect (a FIFO pops, a status bit
# clears), so the SoC reads a device exactly when the reference boot does:
# never twice for one record, never on a path the core then squashes
# (fpga/README.md "Byte enables and device reads").
if ! grep -q '^P9KERN devices: .* 0 repeated, 0 unrecorded' "$work/core.log"; then
  echo "run_soc.sh: the SoC read a device register the reference boot did not read" >&2
  fail=1
fi
[ "$simstatus" = 0 ] || { echo "run_soc.sh: the simulator stopped with status $simstatus" >&2; fail=1; }
[ "$stale" = 0 ] || fail=1
exit $fail
