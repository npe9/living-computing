#!/bin/sh
set -eu

output='A24-1403-5_1401_Reference_Apr62.pdf'
temporary="${output}.part"
curl --fail --location --proto '=https' --retry 3 --output "$temporary" \
  'https://bitsavers.trailing-edge.com/pdf/ibm/1401/A24-1403-5_1401_Reference_Apr62.pdf'
test "$(head -c 5 "$temporary")" = '%PDF-'
mv "$temporary" "$output"
shasum -a 256 "$output" > SHA256SUMS
