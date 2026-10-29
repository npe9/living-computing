#!/bin/sh
set -eu

output='Whirlwind_I_Description_Apr1955.pdf'
temporary="${output}.part"
curl --fail --location --proto '=https' --retry 3 --output "$temporary" \
  'https://bitsavers.trailing-edge.com/pdf/mit/whirlwind/Whirlwind_I_descr_Apr1955.pdf'
test "$(head -c 5 "$temporary")" = '%PDF-'
mv "$temporary" "$output"
shasum -a 256 "$output" > SHA256SUMS
