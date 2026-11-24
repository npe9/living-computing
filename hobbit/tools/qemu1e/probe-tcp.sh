#!/bin/sh
# Boot the QEMU 1e file server (after build.sh) on slirp networking and
# check it from the host with p9probe.py over tcp!...!564.  -snapshot:
# the run leaves fs.img as built.
set -e
here=$(cd "$(dirname "$0")" && pwd)
Q=$(cd "$here/../.." && pwd)/build/qemu
P9PORT=${P9PORT:-5640}
export P9PORT
cd "$Q"
python3 -u "$here/qemu1e.py" --workdir run-probe --fd fd.img --hd fs.img --hd2 arch.img --extra=-snapshot \
	--net "-netdev user,id=n0,net=10.0.2.0/24,hostfwd=tcp:127.0.0.1:$P9PORT-10.0.2.15:564 -device ne2k_isa,iobase=0x300,irq=9,netdev=n0" \
	--log run-probe/probe.log "$here/probe-tcp.script"
