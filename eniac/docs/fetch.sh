#!/bin/sh
set -eu

output='ENIAC_Operating_Manual_Jun46.pdf'
temporary="${output}.part"
curl --fail --location --proto '=https' --retry 3 --output "$temporary" \
  'https://bitsavers.trailing-edge.com/pdf/univOfPennsylvania/eniac/ENIAC_Operating_Manual_Jun46.pdf'
test "$(head -c 5 "$temporary")" = '%PDF-'
mv "$temporary" "$output"
shasum -a 256 "$output" > SHA256SUMS
