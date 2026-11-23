#!/bin/sh
# Reproduce the QEMU 1e file server's disks from the release tarball.
# See docs/qemu_1e_server.md.  Everything goes under hobbit/build/qemu/
# (gitignored).
#
#   tools/qemu1e/build.sh [/path/to/plan9-1e.tar.bz2] [fs-size-MB]
#
# Produces
#   build/qemu/src/plan9-1e/      the release, extracted
#   build/qemu/9dos.q, 9pc.q      shipped kernels, patched for QEMU (patch_kernel.py)
#   build/qemu/fd.img             the distribution floppy, bootable without DOS,
#                                 9dos.q as its 9DOS, plus /kfsinit, /serve, /n/kfs
#                                 and tools/qemu1e/ndb.local appended to /lib/ndb/local
#   build/qemu/fd-term.img        the same floppy with 9pc.qs (9pc, patched, stripped) as 9DOS
#   build/qemu/release.arch       the whole release as a mkfs archive
#   build/qemu/arch.img           that archive as a raw IDE disk
#   build/qemu/fs.img             the kfs disk, reamed and filled by 1e in QEMU
set -e
here=$(cd "$(dirname "$0")" && pwd)
hob=$(cd "$here/../.." && pwd)
Q=$hob/build/qemu
TAR=${1:-/tmp/p9/plan9-1e.tar.bz2}
FSMB=${2:-1024}
SHA=8718e279aa35b10a9391f330976d31c177bad00de40e7f0f67232ffa54fb7d77

mkdir -p "$Q/src" "$Q/run"
echo "$SHA  $TAR" | shasum -a 256 -c -
S=$Q/src/plan9-1e
[ -d "$S/386" ] || tar -xjf "$TAR" -C "$Q/src"

python3 "$here/patch_kernel.py" "$S/sys/lib/pc/9dos" "$Q/9dos.q"
python3 "$here/patch_kernel.py" "$S/386/9pc" "$Q/9pc.q"
python3 "$here/mkfloppy.py" "$S/sys/lib/pcdisk" "$S/sys/lib/pc/b.com" "$Q/fd.img" "$Q/9dos.q"
mmd -i "$Q/fd.img" ::/N/KFS
mcopy -i "$Q/fd.img" "$here/kfsinit.rc" ::/KFSINIT
mcopy -i "$Q/fd.img" "$here/serve.rc" ::/SERVE
mtype -i "$Q/fd.img" ::/LIB/NDB/LOCAL > "$Q/ndb.local"
cat "$here/ndb.local" >> "$Q/ndb.local"
mcopy -o -i "$Q/fd.img" "$Q/ndb.local" ::/LIB/NDB/LOCAL

# a second floppy: the shipped 9pc (a terminal kernel), patched, stripped
python3 "$here/patch_kernel.py" --strip "$S/386/9pc" "$Q/9pc.qs"
python3 "$here/mkfloppy.py" "$S/sys/lib/pcdisk" "$S/sys/lib/pc/b.com" "$Q/fd-term.img" "$Q/9pc.qs"

# /adm first: kfsinit's first pass reads only it
python3 "$here/mkarchive.py" "$S" "$Q/release.arch" --overlay "$here/overlay" \
	adm $(cd "$S" && ls | grep -v '^adm$')
python3 "$here/mkdisk.py" "$Q/arch.img" --data "$Q/release.arch"
python3 "$here/mkdisk.py" "$Q/fs.img" --fs "$FSMB"

cd "$Q"
python3 -u "$here/qemu1e.py" --workdir run --fd fd.img --hd fs.img --hd2 arch.img \
	--log run/provision.log "$here/provision.script"
