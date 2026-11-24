#!/bin/sh
# Fetch the DSP3210 documents listed in MANIFEST.md into this directory and
# check them against SHA256SUMS.  The PDFs stay out of git (.gitignore): no
# redistribution terms are shown for them.
#
#   cd hobbit/docs/dsp3210 && sh fetch.sh     # fetch what is missing, check all
#   sh fetch.sh --check                       # check only
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
    # github.com/Wrangler491/AA3000-DSP, pinned to commit bfaf151 (2024-08-23)
    B=https://raw.githubusercontent.com/Wrangler491/AA3000-DSP/bfaf15154222735eb156f13b0f6ea440225e459d
    # WE DSP3210 Digital Signal Processor Information Manual, September 1991,
    # split by the uploader into four page ranges of the 288-page scan
    for r in 1-46 47-134 135-226 227-288; do
        fetch_pdf "$B/DSP3210_Information_Manual-$r.pdf" "DSP3210_Information_Manual-$r.pdf"
    done
    # AT&T "DSP3210 Digital Signal Processor: The Multimedia Solution" data sheet
    fetch_pdf "$B/AT%26T%20DSP3210%20DSP%20The%20Multimedia%20Solution.pdf" \
      ATT_DSP3210_DSP_The_Multimedia_Solution.pdf
fi

shasum -a 256 -c SHA256SUMS
