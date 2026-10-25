#!/bin/bash
pdf="$1"; out="$2"; jobs="${3:-4}"
here="$(cd "$(dirname "$0")" && pwd)"
base=$(basename "$pdf" .pdf)
tmp=$(mktemp -d "$here/L.XXXXXX")
n=$(pdfinfo "$pdf" | awk '/^Pages/{print $2}')
seq 1 "$n" | xargs -P "$jobs" -I@ "$here/ocr_listing_one.sh" "$pdf" "$tmp" @
: > "$out"
for i in $(seq 1 "$n"); do
  printf '\n===== %s PDF page %d =====\n' "$base" "$i" >> "$out"
  [ -f "$tmp/t$i.txt" ] && cat "$tmp/t$i.txt" >> "$out"
done
rm -rf "$tmp"
printf '%-34s %4d pages %9d bytes\n' "$base" "$n" "$(wc -c < "$out")"
