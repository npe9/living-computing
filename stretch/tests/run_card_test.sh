#!/bin/sh
# run_card_test.sh -- punch an ASCII deck and read it on the machine.
# See gen_card_reader_tb.py; the deck is text, the machine sees
# punches, and ../decks/card_reader.strap knows nothing about either.
set -e
TESTS_DIR="$(cd "$(dirname "$0")" && pwd)"
# The assembler lives in ../strap now; the verifiers and
# generators import it by module name.
PYTHONPATH="$TESTS_DIR/../strap:$TESTS_DIR"; export PYTHONPATH
BSV_DIR="$TESTS_DIR/../bsv"
MODULE="${1:-StretchCardTb}"
export BLUESPECDIR=/opt/homebrew/Cellar/bsc/2026.01/libexec/lib
export PATH=/opt/homebrew/Cellar/bsc/2026.01/bin:$PATH
BSC=/opt/homebrew/Cellar/bsc/2026.01/bin/bsc
cd "$TESTS_DIR"
python3 gen_card_reader_tb.py "$MODULE" > "$BSV_DIR/$MODULE.bsv"
cd "$BSV_DIR"
mkdir -p build simbuild
"$BSC" -sim -simdir simbuild -bdir build -info-dir build -show-schedule \
       -g "mk$MODULE" -u "$MODULE.bsv" +RTS -K512m -RTS
"$BSC" -sim -simdir simbuild -bdir build -e "mk$MODULE" -o "${MODULE}_sim" \
       +RTS -K512m -RTS
"./${MODULE}_sim"
