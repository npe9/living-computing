#!/bin/sh
# run_ja_bm6a.sh STAGE -- run IBM's JA BM6A unique-address test
# (../decks/ja_bm6a_unique_adr.strap) on the model, stop it at a point in
# its endless loop, dump core from word 32 (octal 40) to the top, and
# check it with check_ja_bm6a_dump.py.
#
# STAGE (see check_ja_bm6a_dump.py):
#   UPPER  stop at the 1st arrival at 100002.40 (SX,$X3,$R in Part II):
#          Part I has generated and checked the four upper boxes
#          (100000-277777), restored PHA2, and Part II has saved the
#          612 low words; Part II's generation has not begun
#   PASS   stop at the 2nd arrival at 001010.40 (SX,$X3,$R in Part I):
#          one whole pass, both halves, and the next pass's 100-word
#          save
#
# WHY THESE STOP POINTS.  getPC() is the instruction unit's counter and
# runs ahead of execution; ja_bp6a measured that a stop on the
# instruction right after a multi-word T can land while the T is still
# draining, and the dump's first read then returns the T's in-flight
# word (run_ja_bp6a.sh says how it was seen).  Both stops here are the
# THIRD instruction after a T (T, Z, LVI, SX), behind the one the I-box
# prepares during the drain.
#
# WHAT IS STUBBED, AND WHAT IS INFERRED.
#   - THE LOAD.  The deck is "PUNFUL binary ... 13 cards" loaded by IPL
#     (writeup PDF p.1, 3.1).  The printed "PUNFUL," card is commented
#     out (the deck header says why) and gen_tb preloads the assembled
#     image -- the one the listing oracle checks.
#   - THE ENTRY IS AN INFERENCE.  "END,99." (PDF p.11) names word 99
#     (143 octal), where the deck loads nothing; what the 13-card deck
#     put there is not in this document.  The run starts at M06
#     (001000.00), the program's first instruction, under the remark
#     "MEMORY UNIQUENESS TEST M006".  ENTRY=M06 below.
#   - THE SENSE SWITCHES (maintenance bits, word 4) are the model's
#     reset value, 0: no option is on (writeup PDF p.2, 3.2).
#   - THE TYPEWRITER IS NOT WHERE THE MODEL'S CONSOLE IS.  The program
#     types on TYPE, "SYN,19.32" (PDF p.11, printed 23.40), whose
#     channel-address bits 12-18 are 0100111 = channel 39; the model's
#     console is chanConsole = 35 (StretchIO.bsv, a choice, not a
#     source).  Channel 39 is installed with no unit, so every
#     REL(SEOP),TYPE and W(SEOP),TYPE is a Unit Not Ready reject, with
#     interrupts off (the program's first instruction is BD).  So
#     NOTHING THE PROGRAM TYPES REACHES THE MODEL'S PAPER, and the
#     check reads the program's own error message out of core instead
#     (check_ja_bm6a_dump.py says how).
#
# MEASURED, NOT TIMING CLAIMS (2026-11-25, this model): UPPER stops at
# 25,251,350 clocks, PASS at 35,388,608 -- about 35 million clocks a
# pass, so the 100-pass O.K. (writeup PDF p.2, 3.3) would need about
# 3.5 billion and is not run.  The O.K. path (100023.00 onward) is NOT
# exercised.  With one error injected, UPPER stops at 36,807,634: one
# pass through the error routine costs about 11.5 million clocks, nearly
# all of it the "CBR,$X1,$" delay after the (rejected) typeout, count
# (8)606530 = 200,024.  Wall time: UPPER ~3 min,
# PASS ~4 min, after the model is compiled.
set -e
TESTS_DIR="$(cd "$(dirname "$0")" && pwd)"
PYTHONPATH="$TESTS_DIR/../strap:$TESTS_DIR"; export PYTHONPATH

STAGE="$1"
case "$STAGE" in
  UPPER) STOP="$((8#100002 * 2 + 1)),1" ;;
  PASS)  STOP="$((8#1010 * 2 + 1)),2" ;;
  *) echo "usage: $0 UPPER|PASS" >&2; exit 1 ;;
esac

# STEPS: the cap only has to be above the deepest stop point.  The exit
# status is the checker's.
"$TESTS_DIR/run_program.sh" "$TESTS_DIR/../decks/ja_bm6a_unique_adr.strap" "StretchJaBm6a${STAGE}Tb" \
    ENTRY=M06 STOPAT="$STOP" STEPS=60000000 DUMP=32,98272 \
  | python3 "$TESTS_DIR/check_ja_bm6a_dump.py" "$STAGE"
