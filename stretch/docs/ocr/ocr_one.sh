#!/bin/bash
# $1 pdf  $2 tmpdir  $3 page  $4 dpi  $5 psm
pdftoppm -f "$3" -l "$3" -r "${4:-300}" -png -gray "$1" "$2/p$3" 2>/dev/null
f=$(ls "$2"/p"$3"-*.png 2>/dev/null | head -1)
[ -n "$f" ] && tesseract "$f" "$2/t$3" --psm "${5:-3}" 2>/dev/null
rm -f "$f"
