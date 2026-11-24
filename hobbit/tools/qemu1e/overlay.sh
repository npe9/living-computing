#!/bin/sh
# Refresh tools/qemu1e/overlay (the qemu1e service files) in an existing
# build/qemu/fs.img, with 1e's mkext, without re-running build.sh.
set -e
here=$(cd "$(dirname "$0")" && pwd)
Q=${QEMU1E_Q:-$(cd "$here/../.." && pwd)/build/qemu}
python3 "$here/mkarchive.py" "$here/overlay" "$Q/overlay.arch" rc
python3 "$here/mkdisk.py" "$Q/overlay.img" --data "$Q/overlay.arch"
cd "$Q"
python3 -u "$here/qemu1e.py" --workdir run --fd fd.img --hd fs.img --hd2 overlay.img \
	--log run/overlay.log "$here/overlay.script"
