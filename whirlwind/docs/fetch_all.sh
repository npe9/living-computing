#!/bin/sh
set -eu

fetch_pdf() {
    url=$1
    output=$2
    temporary="${output}.part"
    curl --fail --location --proto '=https' --retry 3 --output "$temporary" "$url"
    test "$(head -c 5 "$temporary")" = '%PDF-'
    mv "$temporary" "$output"
}

sed -n 's/^| `\([^`]*\.pdf\)` | \[[^]]*\](\(https:[^)]*\)) |.*$/\1	\2/p' README.md |
while IFS='	' read -r output url; do
    fetch_pdf "$url" "$output"
done

shasum -a 256 ./*.pdf > SHA256SUMS
