#!/usr/bin/env python3
"""mktape.py -- assemble a STRAP program and write it as an IPL tape
image, in the layout the IBM 7030's initial-program-load hardware
expects.

THE LAYOUT IS SETTLED BY TWO PRIMARY SOURCES, both read first-hand and
recorded in docs/NEXT.md 5i and 5h.

1. THERE IS NO PREAMBLE.  docs/ka_ul1_load_and_tape_write_util.pdf
   ("LOAD AND TAPE WRITE UTILITY, KA UL1, 13 Oct 1961") writes an IPL
   tape with ONE `W` against one control word: no tape mark, no label,
   no header record.  A bootable 7030 tape is just its words.

2. THE FIRST WORD ON THE TAPE IS A CONTROL WORD.  Reference Manual
   printed p.126 (PDF 129): on the first channel signal after INITIAL
   PROGRAM LOAD, the exchange plants a FIXED control word --

       Data word address = 4 · Chain flag = 1 · Multiple flag = 0
       Skip flag = 0 · Count = 1 · Refill address = 4

   -- and reads with it.  "The first word read from the unit is stored
   in the special core storage location referred to by means of
   address 4.  Since the fixed control word is then exhausted, its
   refill address causes the next control word to be fetched from
   location 4.  Location 4 at this time should contain another control
   word specifying the address at which the word immediately following
   should be stored, and the number of words to be read from the unit.
   Reading then proceeds normally."

   So word 0 of the image is a control word that lands in location 4
   and immediately becomes the active one.  Words 1..count follow it
   into memory at that control word's data word address.

   Then: "the computer ... fetches and executes the instruction in the
   location specified by the data word address field of the control
   word in core storage location 4.  The address of this instruction,
   however, is not placed in the instruction counter," and "the first
   instruction of a program loaded by means of the initial program
   loading technique must be BRANCH DISABLED."

MCP'S OWN BOOTSTRAP IS EXACTLY THIS SHAPE, which is the corroboration
that the reading is right.  MCP_Mar63_001-249.pdf printed p.2:

    15*  000040.00                            SLC,(8)40.0
    17*  000040.00  000041.00+ 000 000560 000001
                                              CW(CR),X IPL BS,X BS END-X IPL BS,1
    24*  000041.00  000043.44 00    X IPL BS  BD,X BEGIN   -DISABLE AND START IPL

i.e. a control word addressing 000041.00 with count 0o560 = 368 and
refill 1, followed immediately by a BD.  `--refill` defaults to 1 for
that reason: MCP's bootstrap finds which channel IPL'd it by scanning
for the refill bit ("ONE IN REFILL FIELD IDENTIFIES IPLCW").

THE FILE FORMAT is a flat sequence of big-endian 64-bit words, which
is what bsv/sd_reference/host_tape.c reads and what an SD card image
will hold.  Byte 0 of each record is IBM bits 0-7, the leftmost byte.

Usage:
    mktape.py PROGRAM.strap OUT.tape [--start LABEL] [--refill N]

`--start` names the label the loaded program begins at; it defaults to
the lowest word address the assembly emits.  The control word's data
word address is that label, and the count is the number of words from
there to the end of the image.
"""
import argparse
import struct
import sys

from strap_asm import assemble, AssemblerError


# THE STANDARD TAPE MARK.  Reference Manual printed p.132's IBM 729 IV
# control-code table: "117 Write Tape Mark (writes the standard tape
# mark 0001111)" and "077 Space File (forward past a tape mark; EE and
# EOP given)".  A mark is a one-character record holding 0001111; this
# model has no records, so it is a word with that character in byte 0 --
# IBM bits 0-7, the leftmost -- and nothing after it.  The same constant
# is bsv/StretchTypes.bsv's tapeMarkWord, which says at length why a
# sentinel rather than a side table.
TAPE_MARK = 0x0F00000000000000


def pack_control_word(data_addr, count, refill, chain=0):
    """Figure 35's layout, the same field order as
    StretchTypes.bsv's packControlWord and gen_tape_tb.py's pack_cw.
    unitReady is 1; every status bit is 0, which p.123 says the
    exchange ignores on a control word fetched from core anyway."""
    v = (data_addr & 0x3FFFF) << 46
    v |= 1 << 45                      # unitReady
    v |= (chain & 1) << 38
    v |= (count & 0x3FFFF) << 18
    v |= (refill & 0x3FFFF)
    return v


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("program")
    ap.add_argument("out")
    ap.add_argument("--start", default=None,
                    help="label the loaded program starts at "
                         "(default: lowest emitted word address)")
    ap.add_argument("--refill", type=int, default=1,
                    help="refill field of the IPL control word "
                         "(default 1, as MCP's own bootstrap uses)")
    ap.add_argument("--tape-mark", action="store_true",
                    help="write a TAPE MARK after the image, as MCP's "
                         "bootstrap expects (printed p.3 spaces over one "
                         "before reading anything else)")
    ap.add_argument("--cw-in-image", action="store_true",
                    help="the program's FIRST WORD already is the IPL "
                         "control word; write the image verbatim and "
                         "synthesise nothing")
    args = ap.parse_args()

    with open(args.program) as f:
        src = f.read()
    try:
        prog = assemble(src)
    except AssemblerError as e:
        print(f"error: {e}", file=sys.stderr)
        sys.exit(1)

    if not prog.words:
        print("error: the program emits no words", file=sys.stderr)
        sys.exit(1)

    lo = min(prog.words)
    hi = max(prog.words)
    if args.start is not None:
        if args.start not in prog.symtab:
            print(f"error: no such label {args.start}", file=sys.stderr)
            sys.exit(1)
        bits = prog.symtab[args.start]
        if bits % 64:
            print(f"error: {args.start} is not word-aligned", file=sys.stderr)
            sys.exit(1)
        start = bits // 64
    else:
        start = lo

    # The image is contiguous from `start`: a tape is read sequentially
    # into consecutive words, so a gap in the assembly becomes a zero
    # word rather than a skipped address.
    if args.cw_in_image:
        # A HISTORICAL PROGRAM BRINGS ITS OWN CONTROL WORD, and it is
        # not the same word this file would synthesise.  MCP's printed
        # p.2 line 17 assembles
        #
        #     000040.00   000041.00+ 000 000560 000001
        #
        # and the printed value's IBM bit 18 -- inside the "000041.00"
        # group -- is ZERO, i.e. the UNIT READY status bit is clear,
        # where pack_control_word below sets it.  RefMan printed p.123
        # says the exchange ignores a fetched control word's status
        # bits, so the two behave alike; but the tape should carry the
        # word the assembler produced, not a reconstruction of it.
        # With --cw-in-image the image is written out verbatim from
        # its own first word, which IS the control word.
        if args.start is not None:
            print("error: --cw-in-image and --start are exclusive",
                  file=sys.stderr)
            sys.exit(1)
        body = [prog.words.get(a, 0) for a in range(lo, hi + 1)]
        # THE COLLISION IS DETECTED, NOT ASSUMED.  A tape mark is a
        # reserved word value, so a program word equal to it would be
        # read as a mark.  Refusing here means the day an image
        # collides, this says so -- rather than the tape quietly
        # growing a mark in the middle of a program.
        for i, w in enumerate(body):
            if w == TAPE_MARK:
                print(f"error: word {lo + i} (0o{lo + i:o}) of the image "
                      f"equals the tape mark 0x{TAPE_MARK:016X}; this "
                      f"format cannot represent it as data", file=sys.stderr)
                sys.exit(1)
        if args.tape_mark:
            body.append(TAPE_MARK)
        with open(args.out, "wb") as f:
            for w in body:
                f.write(struct.pack(">Q", w & 0xFFFFFFFFFFFFFFFF))
        print(f"{args.out}: {len(body)} words ({8 * len(body)} bytes)")
        if args.tape_mark:
            print(f"  word {len(body) - 1}  TAPE MARK "
                  f"0x{TAPE_MARK:016X}")
        print(f"  word 0   the program's OWN control word, from "
              f"{lo} (0o{lo:o})")
        print(f"  words 1+ program image {lo + 1}..{hi} "
              f"(0o{lo + 1:o}..0o{hi:o})")
        return

    count = hi - start + 1
    body = [prog.words.get(a, 0) for a in range(start, hi + 1)]
    cw = pack_control_word(start, count, args.refill)

    with open(args.out, "wb") as f:
        for w in [cw] + body:
            f.write(struct.pack(">Q", w & 0xFFFFFFFFFFFFFFFF))

    print(f"{args.out}: {1 + len(body)} words "
          f"({8 * (1 + len(body))} bytes)")
    print(f"  word 0   control word  dataAddr={start} (0o{start:o}) "
          f"count={count} (0o{count:o}) refill={args.refill}")
    print(f"  words 1+ program image {start}..{hi} "
          f"(0o{start:o}..0o{hi:o})")
    if lo < start:
        print(f"  NOTE: the assembly emits words from {lo} (0o{lo:o}), "
              f"below --start; those are NOT on the tape")


if __name__ == "__main__":
    main()
