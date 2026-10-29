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

fetch_pdf 'https://www.transputer.net/fbooks/tarch/tarch.pdf' \
  'Transputer_Architecture_Reference_Manual_Jul87.pdf'
fetch_pdf 'https://transputer.net/ibooks/72-trn-203-01/tdata2nd.pdf' \
  'Transputer_Databook_2nd_Ed_1989.pdf'
fetch_pdf \
  'https://bitsavers.org/pdf/inmos/transputer/Inmos_IMS_T800_Transputer_preliminary_datasheet_Apr87.pdf' \
  'IMS_T800_Preliminary_Datasheet_Apr87.pdf'

shasum -a 256 ./*.pdf > SHA256SUMS
