#!/bin/sh
# Extract the PDSS V2.52.20 distribution, docs/nonlocal/pdss.tar.Z
# (SHA-256 3da79c34abf3bcd5f30d0b178b869ee25b4cc544de82713552721da94888c13c),
# into DIR (default: a fresh temporary directory, whose name is printed)
# and check the files imported into src/ against pristine.sha256.
#
# src/ is that distribution, imported unedited, minus its build products
# (the 68 *.sav save files, which pdssasm rebuilds from the *.asm, and the
# 2 *.dvi files, which TeX builds from the *.tex): pristine.excluded
# lists them.  The import is two commits, "pristine import of the PDSS
# V2.52.20 emulator sources" (emulator/ and COPYRIGHT, then at src/
# itself; moved to src/emulator/ by a pure rename) and "the rest of the
# distribution, pristine"; every later change to src/ is a commit on top.
# To see the whole modernisation as one diff:
#
#   ./pristine.sh /tmp/pdss-orig && diff -ru /tmp/pdss-orig src
#
# --update rewrites pristine.sha256 and pristine.excluded (only ever
# needed if the import itself changes, which it should not).
set -e
HERE=$(cd "$(dirname "$0")" && pwd)
TAR="$HERE/../../docs/nonlocal/pdss.tar.Z"
DIR=${1:-$(mktemp -d)}
[ "$1" = --update ] && DIR=$(mktemp -d)
mkdir -p "$DIR"
gzip -dc "$TAR" | (cd "$DIR" && tar xf -)
SHA="shasum -a 256"; command -v shasum >/dev/null 2>&1 || SHA=sha256sum
if [ "$1" = --update ]; then
  (cd "$DIR" && find . -type f \( -name '*.sav' -o -name '*.dvi' \) | sed 's#^\./##' | LC_ALL=C sort) \
    > "$HERE/pristine.excluded"
  (cd "$DIR" && find . -type f ! -name '*.sav' ! -name '*.dvi' | sed 's#^\./##' | LC_ALL=C sort \
    | while read f; do $SHA "$f"; done) > "$HERE/pristine.sha256"
  echo "pristine: wrote pristine.sha256 ($(wc -l < "$HERE/pristine.sha256") files)," \
       "pristine.excluded ($(wc -l < "$HERE/pristine.excluded") files)"
  exit 0
fi
(cd "$DIR" && $SHA -c "$HERE/pristine.sha256" >/dev/null) \
  || { echo "pristine: FAIL (extraction does not match pristine.sha256)"; exit 1; }
echo "pristine: $DIR (matches pristine.sha256)"
