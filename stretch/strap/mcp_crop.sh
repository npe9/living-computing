#!/bin/sh
# mcp_crop.sh -- render one column band of an MCP listing page at a
# resolution high enough to read it.  docs/boot_plan.md M3 has twelve
# more pages to go and the geometry was worked out twice by hand
# before this existed.
#
# Usage:  ./mcp_crop.sh PRINTED_PAGE COLUMN BAND [DPI]
#   COLUMN : code | stmt | loc
#   BAND   : 1 | 2 | 3   (top / middle / bottom third of the rows)
#   DPI    : default 900 for `code`, 600 otherwise -- see below
#
# WHY 900 dpi FOR THE CODE COLUMN.  docs/listing_typography.md 11:
# the trailing hex byte of a half-word was read as 80 at 200 dpi AND
# at 600 dpi when the page prints B0.  B and 8 are the only pair in
# 0-9A-F that differ mainly in one vertical stroke, and that stroke
# is the first thing a worn drum printer loses.  The octal columns do
# not need it -- they have no letters.
#
# PDF PAGE != PRINTED PAGE and the offset is NOT constant: volume 1
# duplicates pp.1-2 and carries three blanks.  For the bootstrap
# (printed pp.2-14) the offset is +7, which is applied below; ALWAYS
# confirm against the rendered page's own "PAGE NUMBER" header.

set -e
PRINTED="$1"; COL="${2:-code}"; BAND="${3:-1}"
PDF=../docs/MCP_Mar63_001-249.pdf
PAGE=$((PRINTED + 7))

# COLUMN BANDS, EXPRESSED AT 600 dpi AND SCALED BELOW.  Calibrated
# against the crops that actually worked while transcribing printed
# p.2: code at x=2850 w=1900 and stmt at x=5000 w=2800, both at 600
# dpi.  Writing 900-dpi numbers here and then scaling them as if they
# were 600-dpi is how the first version of this script landed on the
# statement column when asked for the code column.
case "$COL" in
  loc)  X=400;  W=1900 ;;   # LINE + LOCATION
  code) X=2800; W=2000 ;;   # BINARY OUTPUT
  stmt) X=4950; W=2900 ;;   # NAME + STATEMENT + comment
  *) echo "COLUMN must be loc|code|stmt" >&2; exit 1 ;;
esac
case "$COL" in code) DEF=900 ;; *) DEF=600 ;; esac
DPI="${4:-$DEF}"

# The rows occupy roughly y=1250..5600 at 600 dpi; scale to the
# requested resolution and take a third of them.
SCALE=$((DPI * 100 / 600))
Y0=$(( (1200 + (BAND - 1) * 1400) * SCALE / 100 ))
H=$(( 1550 * SCALE / 100 ))
X=$(( X * SCALE / 100 )); W=$(( W * SCALE / 100 ))

OUT="/tmp/mcp_p${PRINTED}_${COL}_${BAND}"
pdftoppm -f "$PAGE" -l "$PAGE" -r "$DPI" -png -x "$X" -y "$Y0" -W "$W" -H "$H" "$PDF" "$OUT"
ls -la "${OUT}"*.png
echo "printed p.$PRINTED = PDF p.$PAGE, column=$COL band=$BAND dpi=$DPI"
echo "CONFIRM the page's own 'PAGE NUMBER' header matches $PRINTED."
