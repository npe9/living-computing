#!/bin/sh
# Reproduce the QEMU 1e file server's disks from the release tarball.
# See docs/qemu_1e_server.md.  Everything goes under hobbit/build/qemu/
# (gitignored).
#
#   tools/qemu1e/build.sh [/path/to/plan9-1e.tar.bz2] [fs-size-MB]
#
# The tarball: the argument, else $P9TAR, else hobbit/build/dist/ (the
# durable copy), else /tmp/p9/ (where it first was; /tmp gets cleaned).
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
#   build/qemu/fs.img             the kfs disk, reamed and filled by 1e in QEMU,
#                                 with /adm/keys and glenda (authinit.py)
#   build/qemu-cpu/fd-cpu.img     the CPU server floppy (cpukernel.sh)
set -e
here=$(cd "$(dirname "$0")" && pwd)
hob=$(cd "$here/../.." && pwd)
Q=$hob/build/qemu
TAR=${1:-$P9TAR}
if [ -z "$TAR" ]; then
	TAR=$hob/build/dist/plan9-1e.tar.bz2
	[ -f "$TAR" ] || TAR=/tmp/p9/plan9-1e.tar.bz2
fi
FSMB=${2:-1024}
SHA=8718e279aa35b10a9391f330976d31c177bad00de40e7f0f67232ffa54fb7d77

mkdir -p "$Q/src" "$Q/run"
echo "$SHA  $TAR" | shasum -a 256 -c -
S=$Q/src/plan9-1e
[ -d "$S/386" ] || tar -xjf "$TAR" -C "$Q/src"

sh "$here/floppies.sh"
(cd "$Q" && shasum -a 256 -c "$here/SHA256SUMS")

# from the tarball, not the extraction: the release has names that
# differ only in case, which a case-insensitive host folds together.
# /adm first: kfsinit's first pass reads only it.
python3 "$here/mkarchive.py" "$TAR" "$Q/release.arch" --overlay "$here/overlay" \
	--list "$Q/release.list" adm
python3 "$here/mkdisk.py" "$Q/arch.img" --data "$Q/release.arch"
python3 "$here/mkdisk.py" "$Q/fs.img" --fs "$FSMB"

cd "$Q"
python3 -u "$here/qemu1e.py" --workdir run --fd fd.img --hd fs.img --hd2 arch.img \
	--log run/provision.log "$here/provision.script"

# section 5: the auth database and glenda (writes fs.img), then the
# CPU-server kernel built in the guest (build/qemu-cpu/fd-cpu.img)
python3 -u "$here/authinit.py"
sh "$here/cpukernel.sh"
