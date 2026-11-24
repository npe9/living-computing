#!/bin/sh
# Make the two boot floppies from the extracted release (build.sh runs
# this; run it alone after changing serve.rc, kfsinit.rc or ndb.local --
# the kfs on fs.img is not touched).
set -e
here=$(cd "$(dirname "$0")" && pwd)
Q=$(cd "$here/../.." && pwd)/build/qemu
S=$Q/src/plan9-1e

python3 "$here/patch_kernel.py" "$S/sys/lib/pc/9dos" "$Q/9dos.q"
python3 "$here/patch_kernel.py" "$S/386/9pc" "$Q/9pc.q"
python3 "$here/mkfloppy.py" "$S/sys/lib/pcdisk" "$S/sys/lib/pc/b.com" "$Q/fd.img" "$Q/9dos.q"
mmd -i "$Q/fd.img" ::/N/KFS
mcopy -i "$Q/fd.img" "$here/kfsinit.rc" ::/KFSINIT
mcopy -i "$Q/fd.img" "$here/serve.rc" ::/SERVE
mtype -i "$S/sys/lib/pcdisk" ::/LIB/NDB/LOCAL > "$Q/ndb.local"
cat "$here/ndb.local" >> "$Q/ndb.local"
mcopy -o -i "$Q/fd.img" "$Q/ndb.local" ::/LIB/NDB/LOCAL

# a second floppy: the shipped 9pc (a terminal kernel), patched, stripped
python3 "$here/patch_kernel.py" --strip "$S/386/9pc" "$Q/9pc.qs"
python3 "$here/mkfloppy.py" "$S/sys/lib/pcdisk" "$S/sys/lib/pc/b.com" "$Q/fd-term.img" "$Q/9pc.qs"

