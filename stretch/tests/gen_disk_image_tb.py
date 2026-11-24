#!/usr/bin/env python3
"""gen_disk_image_tb.py -- driver for ../decks/io_disk_image.strap.

The deck only READS the disk (see its header).  It checks nothing
itself: its 20 destination words are dumped as MEMDUMP lines, and
tests/check_disk_image.py compares them with the image file the run
loaded.  One testbench serves all three runs in
tests/run_disk_image_test.sh (P1's saved image, a short image, no
image), because what differs between them is the host file, not the
model.

Usage: gen_disk_image_tb.py ModuleName > ../bsv/ModuleName.bsv
"""
import sys

from strap_asm import assemble, AssemblerError
from gen_tb import generate
from gen_disk_tb import pack_cw, word_addr

PROGRAM = "../decks/io_disk_image.strap"

# (label, arc, words) in the deck's order; the DESTs are contiguous.
READS = [("DEST0", 0, 8), ("DEST1", 23, 8), ("DEST2", 24, 2),
         ("DEST3", 4095, 2)]


def main():
    if len(sys.argv) != 2:
        print(f"usage: {sys.argv[0]} ModuleName", file=sys.stderr)
        sys.exit(1)
    with open(PROGRAM) as f:
        src = f.read()
    try:
        prog = assemble(src)
    except AssemblerError as e:
        print(f"error: {e}", file=sys.stderr)
        sys.exit(1)
    first = word_addr(prog, READS[0][0])
    off = 0
    for n, (label, _arc, count) in enumerate(READS):
        dest = word_addr(prog, label)
        assert dest == first + off, f"{label} is not contiguous"
        prog.words[word_addr(prog, f"CTLW{n}")] = pack_cw(dataAddr=dest,
                                                          count=count)
        off += count
    print(generate(sys.argv[1], prog, [], step_cap=20000,
                   mem_dump=(first, off)))


if __name__ == "__main__":
    main()
