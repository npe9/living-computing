#!/bin/sh
# Fetch the ATT92020 sources listed in MANIFEST.md into this directory and
# check them against SHA256SUMS.  The PDFs stay out of git (.gitignore):
# they are Microprocessor Report articles (c) MicroDesign Resources, and
# the mirror shows no redistribution terms; the repository is public.
#
#   cd hobbit/docs/att92020 && sh fetch.sh     # fetch what is missing, check all
#   sh fetch.sh --check                        # check only
set -eu
cd "$(dirname "$0")"

fetch_pdf() {
    url=$1
    output=$2
    if [ -f "$output" ]; then
        return 0
    fi
    temporary="${output}.part"
    curl --fail --location --proto '=https' --retry 3 --output "$temporary" "$url"
    test "$(head -c 5 "$temporary")" = '%PDF-'
    mv "$temporary" "$output"
}

if [ "${1:-}" != "--check" ]; then
    M=https://www.cecs.uci.edu/~papers/mpr/MPR/ARTICLES
    # L. Gwennap, "AT&T Expands Hobbit Family", MPR 7:14, 25 Oct 1993
    fetch_pdf "$M/071403.pdf" MPR_v7n14_Hobbit_Family_Oct93.pdf
    # "PDAs Begin Shipping in 1993", MPR 8:1, 24 Jan 1994
    fetch_pdf "$M/080104.pdf" MPR_v8n1_PDAs_Begin_Shipping_Jan94.pdf
fi

shasum -a 256 -c SHA256SUMS
