#!/bin/sh
# run_ja_bb6b.sh STAGE -- run IBM's JA BB6B worst-pattern test
# (../decks/ja_bb6b_worst_pattern.strap) on the model, stop it at a point
# in its endless loop, dump core from word 16 (the index registers) to
# the top, and check it with check_ja_bb6b_dump.py.
#
# STAGE (see check_ja_bb6b_dump.py):
#   CHECK   stop at the 2nd arrival at 001071.40 (BR5's Z,0($X2)): Part
#           I has written and checked the checkerboard and the inverted
#           checkerboard through 100000-277013, BR5 has undone the
#           SWAPIs, and one word, 100000, has been zeroed
#   INJECT  stop at the 2nd arrival at 001157.00 (BR13P's Z,0($X2)):
#           Part I's single-error-injection part, plain and
#           complemented, is done and BR13 has undone its SWAPIs
#   PASS    stop at the 2nd arrival at 001021.00 (PH1): one whole pass,
#           both halves, X14 stepped once
#
# WHY THESE STOP POINTS.  getPC() is the instruction unit's counter and
# runs ahead of execution; ja_bp6a measured that a stop on the
# instruction right after a multi-word T can land while the T is still
# draining.  CHECK and INJECT stop one Z after the LX that follows the
# last SWAPI; PASS stops at PH1, the third instruction after Part II's
# restoring T (T, BB, BD), as run_ja_bm6a.sh does.
#
# PC= makes the testbench print the instruction counter where the run
# ended, so the checker can tell a deliberate stop from the program's
# own failure stop, a hang on one of its four BRGZ,$.
#
# WHAT IS STUBBED, AND WHAT IS INFERRED.
#   - THE LOAD.  The deck is "PUNFUL binary deck consists of 21 cards"
#     loaded by IPL (writeup PDF p.1, 3.1.1).  The printed "PUNFUL,"
#     card is commented out and gen_tb preloads the assembled image --
#     the one the listing oracle checks.
#   - THE ENTRY IS AN INFERENCE.  "END,100." (PDF p.20) names word 100
#     (144 octal), where the deck loads nothing.  The run starts at
#     START1 (001000.00), where the load chain's CW at 777 puts the
#     program and its first instruction (BD,$+0.32).
#   - THE SENSE SWITCHES (word 4) are the model's 0: no option is on.
#   - The maintenance-mode console (error injection and error stop
#     switches, look-ahead disable) does not exist on the model; see
#     the deck header.
#
# MEASURED, NOT TIMING CLAIMS (2026-11-26, this model): CHECK stops at
# 31,776,224 clocks, INJECT at 103,925,782, PASS at 149,241,141.  Wall
# time on a quiet machine: CHECK ~4 min, INJECT ~11 min, PASS ~17 min
# after the model is compiled (PASS took 27 min at a load average of
# 200).  run_tests.sh runs CHECK and PASS.
set -e
TESTS_DIR="$(cd "$(dirname "$0")" && pwd)"
PYTHONPATH="$TESTS_DIR/../strap:$TESTS_DIR"; export PYTHONPATH

STAGE="$1"
case "$STAGE" in
  CHECK)  HW=$((8#1071 * 2 + 1)); N=2; CAP=40000000 ;;
  INJECT) HW=$((8#1157 * 2));     N=2; CAP=120000000 ;;
  PASS)   HW=$((8#1021 * 2));     N=2; CAP=170000000 ;;
  *) echo "usage: $0 CHECK|INJECT|PASS" >&2; exit 1 ;;
esac

# STEPS: the cap only has to be above the stage's stop point, and it is
# what ends a FAILING run: the program's hang on BRGZ,$ does not make
# the model's halted() rise (measured with the injected fault in
# check_ja_bb6b_dump.py's header: the run went to the cap with the PC
# on the BRGZ), so a failure costs the whole cap.  The exit status is
# the checker's.
"$TESTS_DIR/run_program.sh" "$TESTS_DIR/../decks/ja_bb6b_worst_pattern.strap" "StretchJaBb6b${STAGE}Tb" \
    ENTRY=START1 STOPAT="$HW,$N" PC="$HW" STEPS=$CAP DUMP=16,98288 \
  | python3 "$TESTS_DIR/check_ja_bb6b_dump.py" "$STAGE"
