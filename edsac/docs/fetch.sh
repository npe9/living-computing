#!/bin/sh
set -eu

output='EDSAC_Tutorial_Guide.pdf'
temporary="${output}.part"
curl --fail --location --proto '=https' --retry 3 --output "$temporary" \
  'https://www.dcs.warwick.ac.uk/~edsac/Software/EdsacTG.pdf'
test "$(head -c 5 "$temporary")" = '%PDF-'
mv "$temporary" "$output"
shasum -a 256 "$output" > SHA256SUMS
