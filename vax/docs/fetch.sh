#!/bin/sh
set -eu

output='VAX_Architecture_Handbook_Vol1_1977.pdf'
temporary="${output}.part"
curl --fail --location --proto '=https' --retry 3 --output "$temporary" \
  'https://bitsavers.trailing-edge.com/pdf/dec/vax/handbook/VAX_Architecture_Handbook_Vol1_1977.pdf'
test "$(head -c 5 "$temporary")" = '%PDF-'
mv "$temporary" "$output"
shasum -a 256 "$output" > SHA256SUMS
