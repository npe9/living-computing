#!/bin/sh
# Extract the pristine PDSS V2.52.20 emulator sources from
# docs/nonlocal/pdss.tar.Z into DIR (default: a fresh temporary
# directory, whose name is printed), and check them against
# pristine.sha256.  src/ began as exactly this extraction (emulator/ was at src/ itself until
# the commit that moved it to src/emulator/) (git history:
# the commit "pim/ref/pdss: pristine import"); every later change to
# src/ is a commit on top of it.  To see the whole modernisation as one
# diff:
#
#   ./pristine.sh /tmp/pdss-orig && diff -ru /tmp/pdss-orig/emulator src/emulator
#
# --update rewrites pristine.sha256 (only ever needed if the import
# itself changes, which it should not).
set -e
HERE=$(cd "$(dirname "$0")" && pwd)
TAR="$HERE/../../docs/nonlocal/pdss.tar.Z"
DIR=${1:-$(mktemp -d)}
[ "$1" = --update ] && DIR=$(mktemp -d)
mkdir -p "$DIR"
gzip -dc "$TAR" | (cd "$DIR" && tar xf - COPYRIGHT emulator)
SHA="shasum -a 256"; command -v shasum >/dev/null 2>&1 || SHA=sha256sum
if [ "$1" = --update ]; then
  (cd "$DIR" && $SHA COPYRIGHT emulator/*) > "$HERE/pristine.sha256"
  echo "pristine: wrote pristine.sha256"; exit 0
fi
(cd "$DIR" && $SHA -c "$HERE/pristine.sha256" >/dev/null) \
  || { echo "pristine: FAIL (extraction does not match pristine.sha256)"; exit 1; }
echo "pristine: $DIR (matches pristine.sha256)"
