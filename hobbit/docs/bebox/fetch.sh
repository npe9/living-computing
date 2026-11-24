#!/bin/sh
# Fetch the surviving Hobbit BeBox software and documentation listed in
# MANIFEST.md into hobbit/build/bebox/ (gitignored) and check it against
# SHA256SUMS.  None of it is in git: it is Be Inc.'s proprietary software
# and a document marked "CONFIDENTIAL : Be Labs, Inc.", and its source
# shows no redistribution terms (the repository is public).
#
# Each archive gets its own directory; the contents are untrusted data:
# never run a binary from them on the host, and read them with `python3 -I`
# (tools/befs1.py).
#
#   sh hobbit/docs/bebox/fetch.sh            # fetch what is missing, check all
#   sh hobbit/docs/bebox/fetch.sh --check    # check only
set -eu
here=$(cd "$(dirname "$0")" && pwd)
dest=$(cd "$here/../.." && pwd)/build/bebox
mkdir -p "$dest"
cd "$dest"

B='https://fsck.technology/software/Be/BeOS%20Install%20Media/BeOS%20Hobbit%20Prototype%20Release'

get() {  # url output
    if [ -f "$2" ]; then
        return 0
    fi
    mkdir -p "$(dirname "$2")"
    curl --fail --silent --show-error --location --proto '=https' --retry 3 \
        --output "$2.part" "$1"
    mv "$2.part" "$2"
}

if [ "${1:-}" != "--check" ]; then
    for f in 1of7 2of7 3of7 4of7 5of7 6of7 7of7 installer update; do
        get "$B/Floppy%20Images/$f.img" "floppy-$f/$f.img"
    done
    for f in Hobbit-9308000044 hobbit-9308000058 hobbit-930800009; do
        get "$B/Hard%20Drive%20Image/$f.img" "hdd-$f/$f.img"
    done
    for f in be3 pixels; do
        get "$B/Hard%20Drive%20Image/FS%20Dump/$f.tgz" "fsdump-$f/$f.tgz"
    done
    # The September 1993 hardware documentation drafts, page scans.
    D="$B/Documentation%20%28Loose%20Files%29"
    awk '$2 ~ /^docscans\// {print $2}' "$here/SHA256SUMS" | while read -r p; do
        get "$D/${p#docscans/}" "$p"
    done
    # The NCR 53C94/95/96 data sheet (Feb 1990), which tools/beboot.py's
    # 53C94 model cites by page; bitsavers, no redistribution terms.
    get "https://bitsavers.trailing-edge.com/components/ncr_symbios/scsi/53C94/NCR_53C94_53C95_53C96_Data_Sheet_Feb90.pdf" \
        datasheets/NCR_53C94_53C95_53C96_Data_Sheet_Feb90.pdf
fi

shasum -a 256 -c "$here/SHA256SUMS" | grep -v ': OK$' || true
shasum -a 256 -c --status "$here/SHA256SUMS" && echo "bebox: $(wc -l < "$here/SHA256SUMS" | tr -d ' ') files OK"
