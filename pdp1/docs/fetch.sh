#!/bin/sh
set -eu

output='F15B_PDP1_Handbook_1961.pdf'
temporary="${output}.part"
curl --fail --location --proto '=https' --retry 3 --output "$temporary" \
  'https://bitsavers.trailing-edge.com/pdf/dec/pdp1/F15B_PDP1_Handbook_1961.pdf'
test "$(head -c 5 "$temporary")" = '%PDF-'
mv "$temporary" "$output"
shasum -a 256 "$output" > SHA256SUMS
