#!/bin/sh
# run_disk_stall_test.sh -- ../decks/io_disk.strap again, on a disk that
# refuses writes three clocks in four (-D DISK_WRITE_STALL, see
# StretchDiskSource.bsv canWrite).  The SDRAM back end the ULX3S will
# use cannot take a word every clock, so the exchange must wait for
# canWrite() rather than post into a full buffer.  The deck's own checks
# read every written word back off the platter, so a word posted while
# the source refused it is a failed check, not a silent loss.
#
# Its own -bdir/-simdir, because a -D changes what the same .bo means
# (the reason run_mcp_assign_test.sh gives for build-hosttape).
#
# MEASURED 2026-11-07: see the entry in run_tests.sh.
#
# Usage: ./run_disk_stall_test.sh [ModuleName]  (default: StretchIoDiskStallTb)
set -e
TESTS_DIR="$(cd "$(dirname "$0")" && pwd)"
PYTHONPATH="$TESTS_DIR/../strap:$TESTS_DIR"; export PYTHONPATH
BSV_DIR="$TESTS_DIR/../bsv"
MODULE="${1:-StretchIoDiskStallTb}"

export BLUESPECDIR=/opt/homebrew/Cellar/bsc/2026.01/libexec/lib
export PATH=/opt/homebrew/Cellar/bsc/2026.01/bin:$PATH
BSC=/opt/homebrew/Cellar/bsc/2026.01/bin/bsc

cd "$TESTS_DIR"
python3 gen_disk_tb.py "$MODULE" > "$BSV_DIR/$MODULE.bsv"

cd "$BSV_DIR"
mkdir -p build-diskstall simbuild-diskstall
"$BSC" -sim -D DISK_WRITE_STALL -simdir simbuild-diskstall -bdir build-diskstall -info-dir build-diskstall -g "mk$MODULE" -u "$MODULE.bsv" +RTS -K512m -RTS
"$BSC" -sim -D DISK_WRITE_STALL -simdir simbuild-diskstall -bdir build-diskstall -e "mk$MODULE" -o "${MODULE}_sim" +RTS -K512m -RTS
"./${MODULE}_sim" | tee "${TMPDIR:-/tmp}/diskstall.$$.log"
if grep -q "WRITE LOST" "${TMPDIR:-/tmp}/diskstall.$$.log"; then
  echo "FAIL disk_write_lost: a word was written while canWrite was False"
  rm -f "${TMPDIR:-/tmp}/diskstall.$$.log"; exit 1
fi
rm -f "${TMPDIR:-/tmp}/diskstall.$$.log"
