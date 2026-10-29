#!/bin/sh
set -eu

output='24-6661-2_704_Manual_1955.pdf'
temporary="${output}.part"
curl --fail --location --proto '=https' --retry 3 --output "$temporary" \
  'https://bitsavers.trailing-edge.com/pdf/ibm/704/24-6661-2_704_Manual_1955.pdf'
test "$(head -c 5 "$temporary")" = '%PDF-'
mv "$temporary" "$output"
shasum -a 256 "$output" > SHA256SUMS
