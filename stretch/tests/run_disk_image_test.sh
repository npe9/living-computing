#!/bin/sh
# run_disk_image_test.sh -- THE SIMULATED 353 HAS AN IMAGE FILE
# (docs/disk_subsystem.md §9c; bsv/host_tape.c host_disk_*).
#
#   STRETCH_DISK=path       load the image the first time the disk is used;
#                           a short file is zero-filled to 2^21 words
#   STRETCH_DISK_SAVE=path  write the whole unit when the testbench
#                           finishes (gen_tb.py's finish rule)
#
# Format: 2^21 words, 8 bytes each, big-endian (the tape's), word i =
# arc*512 + word at byte 8*i: exactly 16,777,216 bytes.
#
# FIVE PARTS, every one in a host build (-D HOST_TAPE, mkDiskSourceFile);
# run_disk_test.sh's build is mkDiskSourceSmall, which has no file.
#
#   1. SAVE.  MCP's P1 IPL (run_mcp_p1deck_test.sh, all its own checks)
#      with STRETCH_DISK_SAVE set.  The file is exactly one 353 long, and
#      the 33 arcs the run wrote (arcs 0-32, measured) hold the IPL tape's
#      words at the offsets check_disk_image.py pins; every other arc is
#      zero.
#   2. LOAD.  decks/io_disk_image.strap, which only READS, run on that
#      saved image: it finds the saved words in arcs 0 and 32 and zeros in
#      arcs 33 and 4095.
#   3. ZERO-FILL.  The same deck on a short image whose last word is
#      partial (check_disk_image.py short): the missing bytes and every
#      word past the end read zero.  Loading it and saving again gives the
#      short file zero-padded to one 353.
#   4. CONTROL.  The same deck with neither variable set, from an empty
#      directory: every word reads zero, host_disk prints nothing, and no
#      file appears.
#
# INJECTIONS, measured 2026-11-24 (bsv/host_tape.c, each reverted by its
# exact inverse patch, git diff clean after):
#   - host_disk_save's loop bound DISK_WORDS - 512 (the last arc dropped):
#     MEASURED_SAVE
#   - the load's memset of a short read removed (no zero-fill):
#     MEASURED_LOAD
set -e
TESTS_DIR="$(cd "$(dirname "$0")" && pwd)"
BSV_DIR="$TESTS_DIR/../bsv"
PYTHONPATH="$TESTS_DIR/../strap:$TESTS_DIR"; export PYTHONPATH
export BLUESPECDIR=/opt/homebrew/Cellar/bsc/2026.01/libexec/lib
export PATH=/opt/homebrew/Cellar/bsc/2026.01/bin:$PATH
BSC=/opt/homebrew/Cellar/bsc/2026.01/bin/bsc
MODULE="${1:-StretchDiskImageTb}"
unset STRETCH_DISK STRETCH_DISK_SAVE
W=$(mktemp -d "${TMPDIR:-/tmp}/disk_image.XXXXXX")
trap 'rm -rf "$W"' EXIT
status=0
CHK="python3 $TESTS_DIR/check_disk_image.py"

# ---- 1. SAVE: MCP's P1 IPL --------------------------------------------
# run_mcp_p1deck_test.sh regenerates this tree's P1 tape at TAPE.
TAPE="$BSV_DIR/build-hosttape/mcp.p1deck.tape"
STRETCH_DISK_SAVE="$W/p1.disk" "$TESTS_DIR/run_mcp_p1deck_test.sh" \
  > "$W/p1.log" 2>&1 || { cat "$W/p1.log"; echo "FAIL disk_image_p1_run"; exit 1; }
grep -q "^host_disk: saved $W/p1.disk, 2097152 words$" "$W/p1.log" \
  || { echo "FAIL disk_image_saved_line: no 'host_disk: saved' line"; status=1; }
$CHK size "$W/p1.disk" || status=1
$CHK ipl "$W/p1.disk" "$TAPE" || status=1

# ---- the read-only deck, built once ------------------------------------
cd "$TESTS_DIR"
python3 gen_disk_image_tb.py "$MODULE" > "$BSV_DIR/$MODULE.bsv"
cd "$BSV_DIR"
mkdir -p build-hosttape simbuild-hosttape
"$BSC" -sim -D HOST_TAPE -simdir simbuild-hosttape -bdir build-hosttape \
       -info-dir build-hosttape -g "mk$MODULE" -u "$MODULE.bsv" \
       +RTS -K512m -RTS > "$W/bsc.log" 2>&1 || { cat "$W/bsc.log"; exit 1; }
"$BSC" -sim -D HOST_TAPE -simdir simbuild-hosttape -bdir build-hosttape \
       -e "mk$MODULE" -o "${MODULE}_sim" host_tape.c +RTS -K512m -RTS \
       > "$W/bsc.log" 2>&1 || { cat "$W/bsc.log"; exit 1; }
SIM="$BSV_DIR/${MODULE}_sim"

# ---- 2. LOAD the saved image --------------------------------------------
STRETCH_DISK="$W/p1.disk" "$SIM" > "$W/load.log" 2>&1 || status=1
grep -q "^host_disk: loaded $W/p1.disk, 16777216 bytes; 0 words zero-filled$" \
  "$W/load.log" || { echo "FAIL disk_image_loaded_line"; status=1; }
$CHK dump "$W/load.log" "$W/p1.disk" || status=1

# ---- 3. ZERO-FILL: a short image, then load-and-save --------------------
$CHK short "$W/short.disk"
STRETCH_DISK="$W/short.disk" STRETCH_DISK_SAVE="$W/resave.disk" "$SIM" \
  > "$W/short.log" 2>&1 || status=1
$CHK dump "$W/short.log" "$W/short.disk" || status=1
python3 - "$W/short.disk" "$W/resave.disk" <<'EOF' || status=1
import sys
a = open(sys.argv[1], "rb").read(); b = open(sys.argv[2], "rb").read()
want = a + bytes((1 << 21) * 8 - len(a))
if b == want:
    print(f"PASS disk_image_resave: the short image saved back as itself "
          f"plus {len(want) - len(a)} zero bytes")
else:
    print(f"FAIL disk_image_resave: {len(b)} bytes, differs from the short "
          f"image zero-padded to {len(want)}")
    sys.exit(1)
EOF

# ---- 4. CONTROL: neither variable, from an empty directory -------------
mkdir "$W/empty"
(cd "$W/empty" && "$SIM") > "$W/none.log" 2>&1 || status=1
$CHK dump "$W/none.log" || status=1
if grep -q "^host_disk:" "$W/none.log"; then
  echo "FAIL disk_image_control_quiet: host_disk printed with no variable set"
  status=1
fi
if [ -n "$(ls -A "$W/empty")" ]; then
  echo "FAIL disk_image_control_no_file: $(ls -A "$W/empty")"; status=1
else
  echo "PASS disk_image_control: no image, all zeros, nothing printed, no file"
fi
exit $status
