#!/bin/sh
# mcp_page.sh -- everything needed to START transcribing one MCP page,
# in one command.
#
#   strap/mcp_page.sh 86
#
# Renders the page's full width from LINE 1 (not line 6 -- see the
# warning in docs/transcription_workflow.md), runs the OCR
# cross-check on the LOCATION column, and prints the checklist of what
# is left.  Four commands became one; the reading is still done by eye,
# because tesseract on a 1963 drum-printer scan is a SECOND opinion and
# not a source.
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
P="$1"
[ -n "$P" ] || { echo "usage: $0 PRINTED_PAGE" >&2; exit 1; }
PDF="$HERE/../docs/MCP_Mar63_001-249.pdf"
OUT="${MCP_PAGE_OUT:-$HERE/../../out}"
mkdir -p "$OUT"
PDFPAGE=$((P + 7))

# The whole row, from line 1: LOCATION, BINARY OUTPUT, NAME, STATEMENT
# and the comment.  y=480 at 400 dpi is line 1.
pdftoppm -f "$PDFPAGE" -l "$PDFPAGE" -r 400 -png \
         -x 900 -y 480 -W 4300 -H 4100 "$PDF" "$OUT/p${P}_full"
# Halves, because the full page at a readable scale is two screens.
magick "$OUT/p${P}_full"*.png -crop 100%x50% +repage "$OUT/p${P}_half_%d.png"
magick "$OUT/p${P}_half_0.png" -resize 1450x "$OUT/p${P}_top.png"
magick "$OUT/p${P}_half_1.png" -resize 1450x "$OUT/p${P}_bot.png"

echo "printed p.$P = PDF p.$PDFPAGE"
echo "  CONFIRM the page's own 'PAGE NUMBER' header reads $P."
echo "  top:    $OUT/p${P}_top.png"
echo "  bottom: $OUT/p${P}_bot.png"
echo
echo "--- OCR cross-check of the LOCATION column (a SECOND reading) ---"
python3 "$HERE/mcp_ocr.py" "$P" 2>/dev/null || echo "  (ocr unavailable)"
echo
echo "--- then ---"
echo "  1. read both halves; diff the locations against the OCR above"
echo "  2. write decks/mcp_bootstrap_p${P}.strap, including its"
echo "     !SYM / !CHECK block (tests/verify_mcp_page.py reads it)"
echo "  3. strap/mcp_image.py: widen MCP_IPL_PAGES' range; add the page"
echo "     to NO_DECK_PAGES if it compiles nothing"
echo "  4. cd tests && python3 verify_mcp_page.py $P"
echo "  5. ./run_mcp_boot.sh StretchMcpBootTb   then   ./run_tests.sh"
