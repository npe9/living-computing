#!/bin/sh
# Build the 1e CPU-server kernel 9pccpu inside the guest with 1e's own
# mk/8c/8l from the release's sys/src/9/pc (config pccpu, a qemu1e
# addition: the release's `pc` with cpuserver = 1 and `boot cpu`), and
# make the CPU server's boot floppy from it.  docs/qemu_1e_server.md
# section 5.  Needs build.sh (or overlay.sh) to have put
# overlay/sys/src/9/pc/pccpu into build/qemu/fs.img.
#
#   tools/qemu1e/cpukernel.sh
#
# fs.img is attached with snapshot=on: the build's objects are thrown
# away and fs.img stays as built.  The second disk is scratch: a swap
# partition (the build needs one: mkcpu.rc) and `out`, where the guest
# copies the kernel raw; it is cut out by its a.out header.
#
# Produces, under build/qemu-cpu/:
#   9pccpu        the kernel as 8l wrote it
#   9pccpu.q      patched for QEMU (patch_kernel.py: the same three patches)
#   9pccpu.qs     the same, stripped (to fit the floppy)
#   fd-cpu.img    the distribution floppy with 9pccpu.qs as its 9DOS
#   run-mk/       the build's screen log; mk's output stays in the
#                 (discarded) kfs snapshot, its tail is on the screen log
set -e
here=$(cd "$(dirname "$0")" && pwd)
hob=$(cd "$here/../.." && pwd)
Q=$hob/build/qemu
C=$hob/build/qemu-cpu
S=$Q/src/plan9-1e
mkdir -p "$C/run-mk"

python3 "$here/mkdisk.py" "$C/out.img" --parts swap:48,out:2
python3 -u "$here/qemu1e.py" --workdir "$C/run-mk" --fd "$Q/fd.img" \
	--extra="-drive file=$Q/fs.img,if=ide,format=raw,index=0,snapshot=on" \
	--hd2 "$C/out.img" --log "$C/run-mk/mkcpu.log" "$here/cpukernel.script"

# the a.out header (sys/include/a.out.h): eight big-endian longs, magic
# text data bss syms entry spsz pcsz; the file is the header, text,
# data, then syms, spsz and pcsz bytes of tables
python3 - "$C/out.img" "$C/9pccpu" <<'EOF'
import struct, sys
b = open(sys.argv[1], 'rb').read()[48 * 1024 * 1024:]     # partition out
magic, text, data, bss, syms, entry, spsz, pcsz = struct.unpack('>8I', b[:32])
if magic != 0x1eb:     # I_MAGIC = _MAGIC(11) = (4*11)*11+7 (a.out.h)
    sys.exit('no 386 a.out at the start of the disk: magic %#x' % magic)
n = 32 + text + data + syms + spsz + pcsz
open(sys.argv[2], 'wb').write(b[:n])
print('%s: %d bytes (text %d data %d bss %d syms %d spsz %d pcsz %d, entry %#x)'
      % (sys.argv[2], n, text, data, bss, syms, spsz, pcsz, entry))
EOF
python3 "$here/patch_kernel.py" "$C/9pccpu" "$C/9pccpu.q"
python3 "$here/patch_kernel.py" --strip "$C/9pccpu" "$C/9pccpu.qs"
python3 "$here/mkfloppy.py" "$S/sys/lib/pcdisk" "$S/sys/lib/pc/b.com" "$C/fd-cpu.img" "$C/9pccpu.qs"
