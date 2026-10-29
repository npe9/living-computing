#!/bin/sh
set -eu

output='6000_Series_Reference_Manual_Jul65.pdf'
temporary="${output}.part"
curl --fail --location --proto '=https' --retry 3 --output "$temporary" \
  'https://bitsavers.trailing-edge.com/pdf/cdc/Tom_Hunter_Scans/6000_Series_Computer_Systems_RefMan_Jul65.pdf'
test "$(head -c 5 "$temporary")" = '%PDF-'
mv "$temporary" "$output"
shasum -a 256 "$output" > SHA256SUMS
