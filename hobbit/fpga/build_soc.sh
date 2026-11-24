#!/bin/sh
# Build the Hobbit SoC bitstream for the ULX3S (fpga/README.md, "The SoC"):
# bsc (bsv/HobbitSocCpu.bsv -> mkHobbitSocCpu.v, socdev/HobbitSocDevs.bsv
# -> mkHobbitSocDevs.v) -> yosys synth_ecp5 -> nextpnr-ecp5 -> ecppack.
# Products in build/soc (gitignored).
#
#   ./build_soc.sh [SEED]        the SoC with the privileged core
#   ./build_soc.sh stub [SEED]   the periphery only: rtl/cpu_stub.v stands
#                                in for the core (build/soc-stub), to place
#                                and time the adapter, SDRAM controller,
#                                host link and devices while the core does
#                                not fit
#
# SOC_RTL=N chooses the RTL devices (hobbit_soc's DEV_RTL, the bits of
# fpga/socdev/HobbitSocDevs.bsv; default 0, every device forwarded).
#
# Nothing here touches the board.
set -eu
cd "$(dirname "$0")"
FPGA=$(pwd)
STUB=0
if [ "${1:-}" = stub ]; then STUB=1; shift; fi
SEED=${1:-1}
RTL=$((${SOC_RTL:-0}))
B=build/soc
[ $STUB = 1 ] && B=build/soc-stub
mkdir -p "$B"

BSC=${BSC_BIN:-$(ls -d /opt/homebrew/Cellar/bsc/*/bin/bsc 2>/dev/null | sort | tail -1)}
if [ -z "$BSC" ] || [ ! -x "$BSC" ]; then
  echo "build_soc.sh: bsc not found; set BSC_BIN" >&2
  exit 1
fi
BLUESPECDIR=$(cd "$(dirname "$BSC")/../libexec/lib" && pwd)
export BLUESPECDIR

# The bsc library cells a netlist instantiates (build.sh does the same).
# RegFileLoad is read with -defer: its file name is a parameter
# (fpga/dev/rtc.md).
libreads() {
  for m in $(sed -n 's/^  \([A-Z][A-Za-z0-9_]*\)[ #(].*/\1/p' "$@" | sort -u); do
    if [ -f "$BLUESPECDIR/Verilog/$m.v" ]; then
      if [ "$m" = RegFileLoad ]; then
        printf ' read_verilog -defer %s;' "$BLUESPECDIR/Verilog/$m.v"
      else
        printf ' read_verilog %s;' "$BLUESPECDIR/Verilog/$m.v"
      fi
    fi
  done
}

# Its own -bdir: bsc's .bo files record no flags, and the regression
# suite compiles the same packages in bsv/.
if [ $STUB = 1 ]; then
  CPUREADS="read_verilog $FPGA/rtl/cpu_stub.v;"
  CPUV=""
else
  "$BSC" +RTS -K512M -RTS -verilog -g mkHobbitSocCpu -u \
    -vdir "$B" -bdir "$B" -info-dir "$B" \
    -p "../bsv:$BLUESPECDIR/Libraries" ../bsv/HobbitSocCpu.bsv > "$B/bsc.log" 2>&1 \
    || { tail -30 "$B/bsc.log"; exit 1; }
  if grep -q 'G0021' "$B/bsc.log"; then
    echo "build_soc.sh: bsc reports a rule that can never fire:" >&2
    grep -A2 G0021 "$B/bsc.log" >&2
    exit 1
  fi
  CPUREADS="read_verilog $FPGA/$B/mkHobbitSocCpu.v;"
  CPUV="$B/mkHobbitSocCpu.v"
fi

"$BSC" +RTS -K512M -RTS -verilog -g mkHobbitSocDevs -u \
  -vdir "$B" -bdir "$B" -info-dir "$B" \
  -p "socdev:dev:dev/quart:dev/intc:$BLUESPECDIR/Libraries" \
  socdev/HobbitSocDevs.bsv > "$B/bsc_devs.log" 2>&1 \
  || { tail -30 "$B/bsc_devs.log"; exit 1; }
DEVV=""
for v in "$B"/mk*.v; do
  case "$v" in */mkHobbitSocCpu.v) ;; *) DEVV="$DEVV read_verilog $FPGA/$v;" ;; esac
done
LIBREADS=$(libreads $CPUV "$B"/mk*.v)

# yosys runs in $B: the RTC's NVRAM and the IIC's EEPROM images are read
# from the working directory.
cp dev/rtc_nvram.hex dev/iic_eeprom.hex "$B/"
(cd "$B" && yosys -p "$CPUREADS $DEVV $LIBREADS \
          read_verilog $FPGA/rtl/uart8n1.v $FPGA/rtl/hostlink.v $FPGA/rtl/sdram_word.v \
                       $FPGA/rtl/hobbit_soc_mem.v $FPGA/rtl/hobbit_soc.v \
                       $FPGA/rtl/ulx3s_hobbit_top.v; \
          chparam -set DEV_RTL $RTL ulx3s_hobbit_top; \
          synth_ecp5 -top ulx3s_hobbit_top -json top.json" \
      -l yosys.log > /dev/null)

nextpnr-ecp5 --85k --package CABGA381 --speed 6 \
  --json "$B/top.json" --lpf ulx3s_soc.lpf \
  --textcfg "$B/top.config" \
  --freq 25 --timing-allow-fail --seed "$SEED" \
  --log "$B/nextpnr.log" > /dev/null 2>&1 || {
  echo "build_soc.sh: nextpnr failed; its utilisation and error:" >&2
  grep -E 'Total LUT4s|TRELLIS_COMB|TRELLIS_FF|DP16KD|MULT18X18D|ERROR' "$B/nextpnr.log" | head -12 >&2
  exit 1
}

ecppack --compress "$B/top.config" "$B/hobbit_soc.bit"

echo "=== yosys (DEV_RTL $RTL) ============================================="
sed -n '/=== ulx3s_hobbit_top ===/,/^$/p;/Number of cells:/,/^$/p' "$B/yosys.log" | tail -30
echo "=== nextpnr ========================================================"
grep -E 'TRELLIS_COMB|TRELLIS_FF|DP16KD|MULT18X18D|TRELLIS_RAMW|DCCA|TRELLIS_IO' "$B/nextpnr.log" | tail -8
grep 'Max frequency for' "$B/nextpnr.log" | tail -4
ls -l "$B/hobbit_soc.bit"
