#!/bin/sh
# Fetch public PARC/CHM Alto disk images (Bitsavers trailing-edge mirror).
set -e
DEST="${1:-disks}"
mkdir -p "$DEST"
BASE="http://bitsavers.trailing-edge.com/bits/Xerox/Alto/disk_images/chm"
for z in diags.zip bcpl.zip games.zip; do
  echo "fetching $z"
  curl -fsSL -o "/tmp/$z" "$BASE/$z"
  unzip -o "/tmp/$z" -d "$DEST"
done
echo "images in $DEST"
ls -l "$DEST"
