#!/bin/sh
set -eu

output='UNIVAC1_Operating_Manual_1954.pdf'
temporary="${output}.part"
curl --fail --location --proto '=https' --retry 3 --output "$temporary" \
  'https://bitsavers.trailing-edge.com/pdf/univac/univac1/UNIVAC1_Operating_Manual_1954.pdf'
test "$(head -c 5 "$temporary")" = '%PDF-'
mv "$temporary" "$output"
shasum -a 256 "$output" > SHA256SUMS
