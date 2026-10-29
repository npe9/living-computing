#!/bin/sh
set -eu

output='Manchester_Mark_1_documents.html'
temporary="${output}.part"
curl --fail --location --proto '=https' --retry 3 --output "$temporary" \
  'https://curation.cs.manchester.ac.uk/digital60/www.digital60.org/birth/manchestercomputers/mark1/documents/index.html'
test -s "$temporary"
mv "$temporary" "$output"
shasum -a 256 "$output" > SHA256SUMS
