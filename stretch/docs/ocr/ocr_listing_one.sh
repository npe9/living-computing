#!/bin/bash
# MCP listing page: crop to the content columns, 600 dpi, uniform block.
# $1 pdf  $2 tmpdir  $3 page
pdftoppm -f "$3" -l "$3" -r 600 -png -gray -x 1700 -y 500 -W 7600 -H 6200 "$1" "$2/p$3" 2>/dev/null
f=$(ls "$2"/p"$3"-*.png 2>/dev/null | head -1)
[ -n "$f" ] && tesseract "$f" "$2/t$3" --psm 6 \
   -c tessedit_char_whitelist='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ.,()+-*/$ =&%#@' 2>/dev/null
rm -f "$f"
