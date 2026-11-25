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
  ${CC:-cc} -O2 -c "$hobbit/bsv/p9kern.c" -o "$work/p9kern.o"
  rm -f "$work/obj/Vsoc_sim_top"
  verilator --cc --exe --build -j "${VL_JOBS:-4}" -O3 \
      --x-assign fast --x-initial fast --no-timing \
      -Wno-fatal -Wno-lint -Wno-style -Wno-STMTDLY -Wno-MULTIDRIVEN \
      -DHOBBIT_SIM \
      --top-module soc_sim_top -y "$BLUESPECDIR/Verilog" -Mdir "$work/obj" \
      -CFLAGS "-O2" \
      "$work/bsc/mkHobbitSocCpu.v" "$fpga/rtl/uart8n1.v" "$fpga/rtl/hostlink.v" \
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
grep '^SOC\|^P9KERN' "$work/core.log" || true

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
[ "$simstatus" = 0 ] || { echo "run_soc.sh: the simulator stopped with status $simstatus" >&2; fail=1; }
exit $fail
