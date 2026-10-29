#!/bin/sh
set -eu

base='https://bitsavers.org/pdf/symbolics/3600_series'

fetch_pdf() {
    remote=$1
    output=$2
    temporary="${output}.part"
    curl --fail --location --proto '=https' --retry 3 \
      --output "$temporary" "$base/$remote"
    test "$(head -c 5 "$temporary")" = '%PDF-'
    mv "$temporary" "$output"
}

fetch_pdf '3600_TechnicalSummary_Feb83.pdf' \
  '3600_TechnicalSummary_Feb83.pdf'
fetch_pdf '990075_Lisp_Machine_Summary_3600_Edition_Aug83.pdf' \
  'Lisp_Machine_Summary_3600_Aug83.pdf'
fetch_pdf '3600_Microcode_Dec83.pdf' '3600_Microcode_Dec83.pdf'
fetch_pdf '3600_Block_Diagram_1985.pdf' '3600_Block_Diagram_1985.pdf'
fetch_pdf 'Symbolics_3600_Series_Basic_Field_Maint_Jul86.pdf' \
  '3600_Series_Basic_Field_Maint_Jul86.pdf'
fetch_pdf 'Lisp_Machine_Hardware_Memos.pdf' \
  'Lisp_Machine_Hardware_Memos.pdf'

shasum -a 256 ./*.pdf > SHA256SUMS
