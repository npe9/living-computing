#!/usr/bin/env python3
"""verify_ibox1_ensu_listing.py -- I-Box 1's ENSU interrupt-and-boundary
setup block (../decks/ibox1_ensu.strap) against ja_ax1a PDF p.56,
octal 005731.00-005736.40.

WHY THIS ONE MATTERS.  The address boundary registers were implemented
from Reference Manual p.31 and tested only by hand-written programs --
the weaker of this project's two standards.  This block is IBM's own
assembler printing a boundary word, so it checks the field placement
with no dependence on the model or on my reading of the manual:

  * bits 0-17  of the word  = octal 777777 = 262143  -> UPPER boundary
  * bits 32-49 of the word  = octal 40     = 32      -> LOWER boundary
  * bits 56-63 of the word  = hex 40 = 0100 0000     -> BIT 57 SET,
    the boundary control bit, which p.31 says means "a signal is
    obtained for a comparand OUTSIDE the specified area"

and the deck's own comment on the line above reads "-32.0-262143.",
i.e. protect everything outside words 32..262142.  A housekeeping
routine guarding its own working area, which is the natural use of
that polarity and an independent second witness for it.

It also settles the spelling of the mask register: "SX,$X1,$MASK"
prints as "14.03 10", and octal 14 is decimal word 12.
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("../decks/ibox1_ensu.strap").read())

# Rows marked (ext) name a symbol defined outside the transcribed range
# and given by SYN from the same print, so they check the opcode and
# modifier bits rather than address placement.  BOUND is defined INSIDE
# the range, so the two rows naming it are real address checks.
ROWS = [
    ('005731.00', '5731.44 00',   'BD,$+.32          disable first'),
    ('005731.40', '6054.03 01',   'LVI,$X1,INT1      (ext)'),
    ('005732.00', '2.03 30',      'SV,$X1,$IA        word 2, interruption address'),
    ('005732.40', '6102.02 10',   'LX,$X1,WEN6       (ext)'),
    ('005733.00', '14.03 10',     'SX,$X1,$MASK      octal 14 = word 12'),
    ('005733.40', '5735.02 10',   'LX,$X1,BOUND      address of BOUND'),
    ('005734.00', '3.03 10',      'SX,$X1,3.0        word 3, the boundaries'),
    ('005734.40', '5736.10 00',   'B,BOUND+1.0       step over the datum'),
    ('005735.00', '777777.00 00 000040.00 40',
                                  'BOUND XW          upper 262143, lower 32, ctl 1'),
    ('005736.00', '5736.40 00',   'BE,$+.32          enable again'),
    ('005736.40', '0.30 00',      'CNOP              the alignment NOP'),
]

SYMBOLS = {
    'ENSU':  '005731.00',
    'BOUND': '005735.00',
}

finish(check_rows(prog, ROWS, SYMBOLS, label='ENSU '))
