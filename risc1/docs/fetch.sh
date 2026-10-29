#!/bin/sh
set -eu

output='CSD-82-106_RISC-I.pdf'
temporary="${output}.part"
curl --fail --location --proto '=https' --retry 3 --output "$temporary" \
  'https://www2.eecs.berkeley.edu/Pubs/TechRpts/1982/Archive/CSD-82-106.pdf'
test "$(head -c 5 "$temporary")" = '%PDF-'
mv "$temporary" "$output"
shasum -a 256 "$output" > SHA256SUMS
