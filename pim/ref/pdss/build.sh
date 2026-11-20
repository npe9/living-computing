#!/bin/sh
# Build PDSS V2.52.20 (docs/nonlocal/pdss.tar.Z) with the port in this
# directory, and reassemble its KL1 libraries.  Output: build/emulator/pdss.
# See README.md.  Exit 77 = this machine cannot run the port (skip).
set -e
HERE=$(cd "$(dirname "$0")" && pwd)
TAR="$HERE/../../docs/nonlocal/pdss.tar.Z"
B="$HERE/build"

case "$(uname -s)/$(uname -m)" in
  Darwin/*)
    arch -x86_64 /usr/bin/true 2>/dev/null || { echo "pdss: SKIP (no x86_64 execution: Rosetta not installed)"; exit 77; }
    ARCH="-arch x86_64"
    LINK="-Wl,-pagezero_size,0x10000 -Wl,-no_pie -Wl,-image_base,0x100000"
    LOW=1 ;;
  Linux/x86_64|Linux/i?86)
    # UNTESTED: a 32-bit build needs none of the low-memory shim.
    ARCH="-m32"; LINK=""; LOW=0 ;;
  *) echo "pdss: SKIP (no build recipe for $(uname -s)/$(uname -m))"; exit 77 ;;
esac

# PDSS_INJECT="shell command" runs in build/emulator after patching and
# before compiling: the fault-injection hook (it forces a rebuild; run
# once more with PDSS_REBUILD=1 afterwards to restore).
if [ -n "$PDSS_INJECT" ] || [ -n "$PDSS_REBUILD" ] || [ ! -x "$B/emulator/pdss" ] || [ "$HERE/port.diff" -nt "$B/emulator/pdss" ] \
   || [ "$HERE/port_low.c" -nt "$B/emulator/pdss" ]; then
  mkdir -p "$B"
  gzip -dc "$TAR" | (cd "$B" && tar xf -)
  (cd "$B" && patch -s -p1 < "$HERE/port.diff")
  cp "$HERE/port_low.c" "$B/emulator/"
  cd "$B/emulator"
  [ -z "$PDSS_INJECT" ] || sh -c "$PDSS_INJECT"
  CF="$ARCH -O1 -std=gnu89 -w -Wno-error=implicit-function-declaration -Wno-error=implicit-int -Wno-error=int-conversion -Wno-error=incompatible-pointer-types -Wno-error=return-type -fcommon"
  KL1="pdss option emulate blt_basic blt_float blt_shoen blt_iodev blt_code blt_system deref passive unify goal shoen exception memory atom module dcode float string gc gc_ctrl gc_cell gc_code gc_dead mrbgc instr invassm assemble saveload native tracer print io iosub timer path ctype"
  ASM="pdssasm memory atom module instr assemble saveload float ctype"
  if [ $LOW = 1 ]; then
    CF="$CF -Dmalloc=pdss_malloc -Dfree=pdss_free -Drealloc=pdss_realloc -Dcalloc=pdss_calloc -Dmain=pdss_main"
    cc $ARCH -O1 -c port_low.c -o port_low.o; SHIM=port_low.o
  else
    cc $ARCH -O1 -DPDSS_NO_LOW -c port_low.c -o port_low.o; SHIM=port_low.o
  fi
  for f in $KL1 pdssasm; do cc $CF -c $f.c -o $f.o; done
  objs() { for f in "$@"; do printf '%s.o ' $f; done; }
  cc $ARCH $LINK -w -std=gnu89 -D'MAKEDATE="living-computing port"' -o pdss version.c $(objs $KL1) $SHIM -lm 2>&1 | grep -v 'no_pie is deprecated' || true
  cc $ARCH $LINK -w -std=gnu89 -D'MAKEDATE="living-computing port"' -o pdssasm version.c $(objs $ASM) $SHIM -lm 2>&1 | grep -v 'no_pie is deprecated' || true
  # The shipped .sav files were assembled on a big-endian SPARC;
  # reassemble every library from its .asm (the tape's "make reassm").
  for d in runtime mpimos compiler; do
    (cd "$B/$d" && for f in *.asm; do
       ../emulator/pdssasm ${f%.asm} </dev/null | grep -q ' OK' || { echo "pdss: pdssasm failed on $d/$f"; exit 1; }
     done)
  done
fi
echo "pdss: built $B/emulator/pdss"
