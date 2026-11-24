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
# keyfs's mount point (serve.rc, authinit.rc): auth/* look keys up on
# /mnt/keys; the floppy's /mnt has no keys directory
mmd -i "$Q/fd.img" ::/MNT/KEYS
mcopy -i "$Q/fd.img" "$here/kfsinit.rc" ::/KFSINIT
mcopy -i "$Q/fd.img" "$here/serve.rc" ::/SERVE
mcopy -i "$Q/fd.img" "$here/mkcpu.rc" ::/MKCPU
mtype -i "$S/sys/lib/pcdisk" ::/LIB/NDB/LOCAL > "$Q/ndb.local"
cat "$here/ndb.local" >> "$Q/ndb.local"
mcopy -o -i "$Q/fd.img" "$Q/ndb.local" ::/LIB/NDB/LOCAL
# the kfs's own /lib/ndb/local plus the same additions: il17008 binds it
# over the served /lib/ndb/local, so that the machines whose root is the
# kfs (terminals, cpu9) know fs9, cpu9 and $auth; the kfs keeps the
# release's file (and tcp564, the host probe's service, serves it)
cat "$S/lib/ndb/local" "$here/ndb.local" > "$Q/ndb.served"
mcopy -o -i "$Q/fd.img" "$Q/ndb.served" ::/LIB/NDB/SERVED
mcopy -o -i "$Q/fd.img" "$here/authinit.rc" ::/AUTHINIT

# a second floppy: the shipped 9pc (a terminal kernel), patched, stripped
python3 "$here/patch_kernel.py" --strip "$S/386/9pc" "$Q/9pc.qs"
python3 "$here/mkfloppy.py" "$S/sys/lib/pcdisk" "$S/sys/lib/pc/b.com" "$Q/fd-term.img" "$Q/9pc.qs"

