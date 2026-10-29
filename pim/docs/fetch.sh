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

fetch_pdf \
  'https://www.bitsavers.org/pdf/icot/Fifth_Generation_Computer_Systems_1992_Volume_1.pdf' \
  'FGCS92_Volume_1.pdf'
fetch_pdf \
  'https://www.airc.aist.go.jp/aitec-icot/ICOT/Museum/TRTM/TR/TRpdf/tr0324.pdf' \
  'ICOT_TR-324_Parallel_Inference_Machine_Research.pdf'

shasum -a 256 FGCS92_Volume_1.pdf \
  ICOT_TR-324_Parallel_Inference_Machine_Research.pdf > SHA256SUMS
