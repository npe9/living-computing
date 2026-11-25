#!/bin/sh
# run_ja_bp6a.sh STAGE -- run IBM's JA BP6A memory-pattern test
# (../decks/ja_bp6a_memory_patterns.strap) on the model, stop it at a
# point in its endless loop, dump core from word 32 (octal 40) to the
# top, and check every word with check_ja_bp6a_dump.py -- the stand-in
# for the CE's oscilloscope, since the test itself compares nothing.
#
# STAGE (see check_ja_bp6a_dump.py):
#   B<k>  k = 1..5  stop at the (k+1)th arrival at MPAT1  (001003.00)
#   A<k>  k = 1..5  stop at the (k+1)th arrival at MPAT2  (100002.40)
#   LOOP            stop at the 8th arrival at MPAT1: one whole loop
#                   done, and the next pass's first pattern (zeros)
#
# WHY THESE STOP POINTS AND NOT THE OBVIOUS ONES.  getPC() is the
# instruction unit's counter, and it runs ahead of execution: the probe
# that stopped at the first arrival at 001005.00 (the BB after the
# ripple) stopped after 612 clocks, with the 65,535-word T barely
# started -- rl_xmit drains a multi-word T while nothing new is armed,
# but the instruction after it has already been prepared.  To arrive at
# MPAT1 or MPAT2 AGAIN, the BB, V+I and CB behind the T must be
# prepared, which cannot happen until the drain is over; so the
# (k+1)th arrival sees pattern k complete, with TI k+1 not yet done.
# Straight-line arrivals are NOT safe, and it was measured: a first
# version stopped LOOP at the 2nd arrival at MPATA1, which the I-box
# prepares while the 50-word save "T,$X2,MPATB,MPST1" is still
# draining.  The stop came 16 clocks after the T began, and the dump's
# FIRST read (word 32 = 000040) returned 0200066102004000501020, which
# is word 100001 -- the read rl_xmit had in flight.  A stop mid-drain
# hands the harness's read the transmit's response.  (Stopping at
# 001001.00, before the T, word 32 read the right ones-ECC word.)  So
# every stop here is behind a CB, and LOOP is the 8th arrival at MPAT1.
#
# WHAT IS STUBBED.  The deck is "PUNFUL Binary, 7 cards" loaded by IPL
# from the card reader (writeup PDF p.1).  The model's IPL is NOT used:
# the deck's printed PUNFUL card is commented out (its header says why)
# and gen_tb preloads the assembled image -- the one the listing oracle
# checks -- and starts at END's MPATA.  Sense switches (word 4 bits 35-37) are
# whatever the model's word 4 holds at reset, 0: no BB is taken.
# Nothing else: the program does no I/O.
set -e
TESTS_DIR="$(cd "$(dirname "$0")" && pwd)"
PYTHONPATH="$TESTS_DIR/../strap:$TESTS_DIR"; export PYTHONPATH

STAGE="$1"
case "$STAGE" in
  B[1-5]) STOP="$((8#1003 * 2)),$(( ${STAGE#B} + 1 ))" ;;
  A[1-5]) STOP="$((8#100002 * 2 + 1)),$(( ${STAGE#A} + 1 ))" ;;
  LOOP)   STOP="$((8#1003 * 2)),8" ;;
  *) echo "usage: $0 B1..B5|A1..A5|LOOP" >&2; exit 1 ;;
esac


# STEPS: one full loop is ~590,000 word moves; the cap only has to be
# above the deepest stop point.  The exit status is the checker's.
"$TESTS_DIR/run_program.sh" "$TESTS_DIR/../decks/ja_bp6a_memory_patterns.strap" "StretchJaBp6a${STAGE}Tb" \
    STOPAT="$STOP" STEPS=40000000 DUMP=32,98272 \
  | python3 "$TESTS_DIR/check_ja_bp6a_dump.py" "$STAGE"
