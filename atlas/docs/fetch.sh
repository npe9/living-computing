#!/bin/sh
set -eu

output='Atlas_Provisional_Programming_Manual_catalog.html'
temporary="${output}.part"
curl --fail --location --proto '=https' --retry 3 --output "$temporary" \
  'https://www.computinghistory.org.uk/det/15674/Ferranti-Atlas-Provisional-Programming-Manual/'
test -s "$temporary"
mv "$temporary" "$output"
shasum -a 256 "$output" > SHA256SUMS
