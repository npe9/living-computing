#!/bin/bash
pdf="$1"; out="$2"; jobs="${3:-3}"; dpi="${4:-300}"; psm="${5:-3}"
here="$(cd "$(dirname "$0")" && pwd)"
base=$(basename "$pdf" .pdf)
tmp=$(mktemp -d "$here/w.XXXXXX")
n=$(pdfinfo "$pdf" | awk '/^Pages/{print $2}')
seq 1 "$n" | xargs -P "$jobs" -I@ "$here/ocr_one.sh" "$pdf" "$tmp" @ "$dpi" "$psm"
: > "$out"
for i in $(seq 1 "$n"); do
  printf '\n===== %s PDF page %d =====\n' "$base" "$i" >> "$out"
  [ -f "$tmp/t$i.txt" ] && cat "$tmp/t$i.txt" >> "$out"
done
rm -rf "$tmp"
printf '%-50s %7d pages %9d bytes\n' "$base" "$n" "$(wc -c < "$out")"
