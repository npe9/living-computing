#!/usr/bin/env python3
"""verify_ax5b_16087_listing.py -- jb_ax5b "I-Box 5", routine 1260's
INDICATOR-WALK DRIVER (programs/ax5b_16087_walk.strap) against the
listing's printed machine code, PDF p.45, octal
021376.40-021402.00.

THE BLOCK docs/NEXT.md HAS POINTED AT SINCE 2026-09-21.  Six
half-words: set one indicator bit in word 11, set its mask bit in word
12, enable, and await the interruption -- the deck's own version of
what programs/interrupt_pg0.strap does hand-written from Reference
Manual p.48.  Reached only if no interruption occurs, the final BD
dispatches into the per-indicator error table I60B13 indexed by X6
("FAILED TO INTERRUPT ON IND MK / IN 1 MILLISEC.", then IK, IJ, EK,
TS, ...).

IT NEEDED TRANSMIT IMMEDIATE, WHICH CAME FROM THE POCKET CARD.
X22-6533 pcard-1 gives "TRANSMIT--Strap Format: OP, J, A1(I1),
A2(I2)"; pcard-3's "TRANSMIT OPERATIONS" box gives the word layout.
opcodes.TRANSMIT_CODES carries the diagram; strap_asm.enc_transmit
implements it.  Nothing about TI was read off this listing, per
AGENTS.md rule 4 -- and the card's layout then reproduced both
printed half-words of both TI rows exactly.

A 600 DPI CORRECTION.  The last row is "21402.44 06", not "...00":
the low digit was lost at 200 dpi under an ink smudge.  With 06 it
decomposes cleanly -- bit 18 set so the target is 021402.40, code 001
= BD, literal 000000, index 0110 = $X6 -- and 021402.40 is where the
page prints the label I60B13.

THREE SYMBOLS THIS BLOCK LOCATES, each from its own row's address
field: I60SX1 = 023041.00, I60S1 = 022741.00, I60B13 = 021402.40.
docs/NEXT.md had carried I60S1/I60SX1 as "not located".

PROVEN DISCRIMINATING.  Observed failure sets, transcribed from the
runs -- both TI rows fail together for every encoder fault, because
the block uses the instruction twice:

  enc_transmit's immediate-count bit forced to 0 (TI encoded as T)
      021377.40 -> "024522.00 81 000013.02 20" for "... A0"
      021400.40 -> "024522.00 81 000014.02 20" for "... A0"
  enc_transmit's literal 1000 at bits 24-27 changed to 0000
      021377.40 -> "024522.00 01 000013.02 A0" for "...00 81 ..."
      021400.40 -> "024522.00 01 000014.02 A0" for "...00 81 ..."
  enc_transmit evaluates A2 as a BIT address (shift 0) instead of a
  half-word address (shift 5)
      021377.40 -> "... 000540.02 A0" for "... 000013.02 A0"
      021400.40 -> "... 000600.02 A0" for "... 000014.02 A0"
      octal 540 is 352 = 11 x 32, i.e. the word number scaled by the
      missing shift -- the field is 32x too large, and visibly so.
  enc_branch_or_misc drops the index field
      021402.00  BD -> "021402.44 00" for "021402.44 06"  (1 row)
      This is the row whose low digit a 200 dpi render had lost; the
      injection is what makes the 600 dpi re-read load-bearing.

WHAT THIS FILE CANNOT SEE: the other seven Transmit mnemonics.  Only
TI has a listing row in this project; T/TB/TBI and the four SWAP
forms come from the pocket card alone.  opcodes.TRANSMIT_CODES says
so.
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("programs/ax5b_16087_walk.strap").read())

# Rows marked (ext) name a symbol defined outside the transcribed range
# and given by SYN from this block's own printed address fields, so
# they check the opcode and modifier bits rather than address
# placement.  "BE,$+.32" is self-relative and is a real address check.
ROWS = [
    ('021376.40', '23041.00 80', 'I6087 SIC,I60SX1    (ext) "-TURN ON BIT 20-47."'),
    ('021377.00', '22741.10 00', 'B,I60S1              (ext)'),
    ('021377.40', '24522.00 81 000013.02 A0',
                                 'TI,1,BIT0($X1),$IND   "-SET ONE OF 20-47", full word at an ODD half-word'),
    ('021400.40', '24522.00 81 000014.02 A0',
                                 'I6088 TI,1,BIT0($X1),$MASK   "-SET MASK BIT OF TEST IND BIT"'),
    ('021401.40', '21402.00 00', 'BE,$+.32              "-ENABLE AND AWAIT INTERRUPT"'),
    ('021402.00', '21402.44 06', 'BD,I60B13($X6)       (ext) index $X6; 06 read at 600 dpi'),
]

SYMBOLS = {
    'I6087': '021376.40',
    'I6088': '021400.40',
}

finish(check_rows(prog, ROWS, SYMBOLS, label='1260 walk '))
