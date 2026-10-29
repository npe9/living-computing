#!/bin/sh
set -eu

output='Colossus_Tunny_overview.html'
temporary="${output}.part"
curl --fail --location --proto '=https' --retry 3 --output "$temporary" \
  'https://rutherfordjournal.org/article030109.html'
test -s "$temporary"
mv "$temporary" "$output"
shasum -a 256 "$output" > SHA256SUMS
