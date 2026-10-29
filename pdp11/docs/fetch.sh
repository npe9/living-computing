#!/bin/sh
set -eu

output='PDP-11_Handbook_Second_Edition_1970.pdf'
temporary="${output}.part"
curl --fail --location --proto '=https' --retry 3 --output "$temporary" \
  'https://bitsavers.trailing-edge.com/pdf/dec/pdp11/1120/PDP-11_Handbook_Second_Edition_1970.pdf'
test "$(head -c 5 "$temporary")" = '%PDF-'
mv "$temporary" "$output"
shasum -a 256 "$output" > SHA256SUMS
