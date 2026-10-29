#!/bin/sh
set -eu

output='Manchester_Computer_50_SSEM.html'
temporary="${output}.part"
curl --fail --location --proto '=https' --retry 3 --output "$temporary" \
  'https://www.curation.cs.manchester.ac.uk/computer50/www.computer50.org/index.html?man=true'
test -s "$temporary"
mv "$temporary" "$output"
shasum -a 256 "$output" > SHA256SUMS
