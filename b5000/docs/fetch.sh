#!/bin/sh
set -eu

output='B5000_Descriptor_Definition_1961.pdf'
temporary="${output}.part"
curl --fail --location --proto '=https' --retry 3 --output "$temporary" \
  'https://bitsavers.trailing-edge.com/pdf/burroughs/LargeSystems/B5000_5500_5700/5000-20002-P_The_Descriptor_-_A_Definition_of_the_B_5000_Information_Processing_System_196102.pdf'
test "$(head -c 5 "$temporary")" = '%PDF-'
mv "$temporary" "$output"
shasum -a 256 "$output" > SHA256SUMS
