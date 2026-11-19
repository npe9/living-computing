#!/bin/sh
set -eu

fetch_pdf() {
    url=$1
    output=$2
    temporary="${output}.part"
    curl --fail --location --proto '=https' --retry 3 --output "$temporary" "$url"
    test "$(head -c 5 "$temporary")" = '%PDF-'
    mv "$temporary" "$output"
}

fetch_pdf 'https://bitsavers.trailing-edge.com/components/att/hobbit/ATT92010_Hobbit_Programmers_Reference_Jan93.pdf' \
  'ATT92010_Hobbit_Programmers_Reference_Jan93.pdf'
fetch_pdf 'https://bitsavers.trailing-edge.com/components/att/hobbit/ATT92010_Hobbit_Microprocessor_Data_Sheet_Dec92.pdf' \
  'ATT92010_Hobbit_Microprocessor_Data_Sheet_Dec92.pdf'
fetch_pdf 'https://bitsavers.trailing-edge.com/components/att/hobbit/ATT2100_Microprocessor_Hardware_Specification_Mar91.pdf' \
  'ATT2100_Microprocessor_Hardware_Specification_Mar91.pdf'
fetch_pdf 'https://www.ardent-tool.com/CPU/docs/MPR/19920212/060201.pdf' \
  'MicroprocessorReport_v6n2_Hobbit_Feb92.pdf'
shasum -a 256 ./*.pdf > SHA256SUMS
