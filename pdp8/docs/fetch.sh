#!/bin/sh
set -eu

output='1966_PDP8_UsersHandbook.pdf'
temporary="${output}.part"
curl --fail --location --proto '=https' --retry 3 --output "$temporary" \
  'https://bitsavers.trailing-edge.com/pdf/dec/pdp8/handbooks/1966_PDP8_UsersHandbook.pdf'
test "$(head -c 5 "$temporary")" = '%PDF-'
mv "$temporary" "$output"
shasum -a 256 "$output" > SHA256SUMS
