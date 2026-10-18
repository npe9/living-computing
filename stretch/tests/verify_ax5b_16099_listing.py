#!/usr/bin/env python3
"""verify_ax5b_16099_listing.py -- jb_ax5b "I-Box 5", routine 1260's
TEST 7 upper-boundary data loop (../decks/ax5b_16099_ub_data.strap)
against the listing's printed machine code, PDF p.65, octal
022215.00-022224.40.

THIS IS THE DRIVER docs/NEXT.md ASKED FOR.  Item 1 warned that
"pp.66-79 were GUESSED to hold the positive boundary-interrupt cases"
and said to FIND THE DRIVER BEFORE TRANSCRIBING.  Found 2026-09-23 by
scanning pp.46-86 for BOUND/MONITOR and reading the hits:

    p.65   "TEST 7 CHKS BOUNDARY CONTROL." / "CHK UPPER BOUNDARY
           DATA."   <- this block, the driver at I6099/I60100
    p.67   "CHK LOWER BOUNDARY DATA." and "CHK BOUNDARY CONTROL BIT."
    p.71   "FETCH FROM X-1 TO CHK UB COMP." and "FROM X-3 TO CHK LB
           COMP."   <- the COMPARISON tests, which are the positive
           address-monitoring cases the plan was actually after

So pp.65-70 test whether the REGISTERS HOLD THEIR BITS and p.71 tests
whether the comparison FIRES.  The guess was wrong in range and in
kind.

THE BLOCK is eighteen iterations -- the upper boundary is word 3 bits
0-17, exactly eighteen bits.  Each writes BIT<n> into $UB, waits four
NOPs, reads back, compares with KV, and on mismatch branches into the
per-bit error table I60B17 indexed by $X3, which steps by 1.32
because each entry is three half-words.

PROVEN DISCRIMINATING (encoding).  Observed failure sets:

  IMM_INDEX_CODES["LCI"] 0b0010 -> 0b0011 (LCI encoded as LRI)
      022215.40                                        (1 row)
  DIR_INDEX_CODES["KV"] 0b01001 -> 0b01011
      022222.40                                        (1 row)
  INDICATOR_BITS["XE"] 53 -> 54
      022223.00  BXE                                   (1 row)

AND THE RUN CATCHES A BOUNDARY FAULT AND NAMES THE BIT.  Measured:
injecting StretchStorage.bsv's boundary write as
"boundaryReg <= (v & ~(64'b1 << 46))" -- dropping IBM bit 17 -- halts
the program at 022263.00, the table's eighteenth entry, "UPPER
BOUNDARY DATA FAILURE, BIT 17".  Clean it halts at PASS (022225.00).
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("../decks/ax5b_16099_ub_data.strap").read())

ROWS = [
    ('022215.00', '0.03 01',     'I6099 LVI,$X1,0.0    "-TEST 7 CHKS BOUNDARY CONTROL."'),
    ('022215.40', '22.03 02',    'LCI,$X1,18            "-CHK UPPER BOUNDARY DATA." -- 18 bits'),
    ('022216.00', '0.07 01',     'LVI,$X3,0.0           the error-table index'),
    ('022216.40', '14.22 00',    'I60100 Z,$MASK       word 12'),
    ('022217.00', '24522.04 31', 'LV,$X2,BIT0($X1)      (ext) the word with only bit X1 set'),
    ('022217.40', '3.05 30',     'SV,$X2,$UB            word 3, the upper boundary'),
    ('022220.00', '0.30 00',     'NOP'),
    ('022220.40', '0.30 00',     'NOP'),
    ('022221.00', '0.30 00',     'NOP'),
    ('022221.40', '0.30 00',     'NOP                   four, the deck\'s own spacing'),
    ('022222.00', '3.04 30',     'LV,$X2,$UB            read it back'),
    ('022222.40', '24522.04 91', 'KV,$X2,BIT0($X1)      (ext) compare'),
    ('022223.00', '22224.32 C2', 'BXE,$+1.0             equal -> skip the error branch'),
    ('022223.40', '22231.50 03', 'B,I60B17($X3)        (ext) "-DATA ERROR."'),
    ('022224.00', '1.47 05',     'I60101 V+I,$X3,1.32  next entry: three half-words'),
    ('022224.40', '22216.43 48', 'CB+,$X1,I60100       count and loop'),
]

SYMBOLS = {'I6099': '022215.00', 'I60100': '022216.40', 'I60101': '022224.00'}

finish(check_rows(prog, ROWS, SYMBOLS, label='1260 T7 '))
