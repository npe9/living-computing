#!/usr/bin/env python3
"""verify_ax5b_16086_listing.py -- jb_ax5b "I-Box 5", routine 1260's DS
block (programs/ax5b_16086_ds.strap) against the listing's own printed
machine code, PDF pp.43-44, octal 021365.00-021376.00.

WHY THIS ONE MATTERS.  Storage protection and the interruption
mechanism were both implemented from the Reference Manual and tested
only by hand-written programs -- the weaker of this project's two
standards, stated as such in storage_protection.strap's and
interrupt_pg0.strap's own headers.  This is IBM's deck testing the
same hardware, and its error message names the rule outright:

    "SV TO 1.0 FAILS TO SET DS WHEN ENABLED."

word 1 (one of p.31's permanently protected locations), the DS
indicator, and the enable gating -- the three things this model's
protViolates predicate implements.  The block also polls DS only AFTER
"I6086A BD,$+.32" disables the system, which is the "a program cannot
poll DS while enabled" trap in docs/NEXT.md, confirmed by a programmer
who had the machine.

WHAT IT CHECKS.  Nineteen half-words, field for field.  Four of them
are encodings no listing had checked before:

  * BDS   "21375.51 C2"  branch on indicator DS (19)
  * BADZ  "21376.10 46"  branch on indicator AD (16) and zero it
  * SVA   "2.13 D0"      store value address into $IA (word 2)
  * DD(BU,32,8) "00000003740"  a 32-bit datum printed as 11 octal
    digits -- the row that taught listing_oracle.py that shape

A NOTE ON WHAT THE I6088 ROW DOES AND DOES NOT PROVE.  I6088 is a
SYN of 021400.40, an INPUT to this check, so the row passing is not
evidence for that address -- it was chosen to make the row match.
The evidence for .40 is elsewhere and is two-fold: p.45's address
column read first-hand at 600 dpi prints 021400.40 beside the row
labelled I6088 (a 200 dpi render of the same rows gave 021400.00,
which is what made the page look a half-word short), and the printed
"21400.50 00" here has bit 18 -- the top bit of that octal pair --
set.  What this row DOES add is that the assembler puts bit 18 where
the listing puts it, which injection 3 below witnesses by removing
it.  With .40 settled, p.45 is self-consistent: its two TI
instructions are full words at ODD half-words (021377.40, 021400.40),
legal per Reference Manual p.39, and the "BE,$+.32 -ENABLE AND AWAIT
INTERRUPT" after them sits at 021401.40 branching to its printed
021402.00.

PROVEN DISCRIMINATING.  Four injections, each naming its own rows --
observed failure sets, not predicted ones:

  INDICATOR_BITS["DS"] 19 -> 18
      021373.40  BDS  "21375.51 42" for "...C2"     (1 row)
  classify_branch_indicator's trailing-Z clear bit 1 -> 0
      021375.40  BADZ "21376.10 42" for "...46"     (1 row)
  enc_branch_or_misc drops bit 18 of the target (addr19 & ~1)
      021372.00  BE,I6086A -> "21372.00 00"        (2 rows: exactly
      021376.00  B,I6088   -> "21400.10 00"         the two targets
                                                     at odd half-words)
  dds_length_bits ignores the declared length (always 64)
      20 of the 22 checks fail.  The only two that survive are the
      symbol I6086 and the row at 021365.00 -- everything at or
      after the DD moves, because the DD's SIZE is what aligns the
      rest of the block

A WARNING PAID FOR HERE.  Reverting an injection with `cp` can leave a
STALE __pycache__: CPython compares the source's mtime at
one-second granularity, so a restore inside the same second as the
injected import is not noticed and the injected bytecode is reused.
The first run of injection 2 above reported BDS failing as well, which
was the previous injection's opcodes.pyc, not this one's edit.  Always
`rm -rf __pycache__` between an injection and its revert.
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("programs/ax5b_16086_ds.strap").read())

# Rows marked (ext) name a symbol defined outside the transcribed range
# and given by SYN from the same print, so they check the opcode and
# modifier bits rather than address placement.  Rows naming I6086,
# I6086A or I6086B are real address checks: those labels are defined
# INSIDE the range.
ROWS = [
    ('021365.00', '1.11 30',      'I6086 SV,$X4,1.00   store into protected word 1'),
    ('021365.40', '00000003740',  'DD(BU,32,8),(8)3740  "ILLEGAL OP, FP 31."'),
    ('021366.00', '1.51 30',      'SV,$X4,1.32          "TURN ON $AD ON"'),
    ('021366.40', '21365.10 10',  'LX,$X4,I6086        this block\'s own first half-word'),
    ('021367.00', '21300.11 10',  'SX,$X4,I6085B+15.0  (ext) table word 15, OP'),
    ('021367.40', '23061.10 10',  'LX,$X4,I60K16       (ext)'),
    ('021370.00', '21301.11 10',  'SX,$X4,I6085B+16.0  (ext) table word 16, AD'),
    ('021370.40', '2.10 30',      'LV,$X4,$IA           save the interruption address'),
    ('021371.00', '21261.13 01',  'LVI,$X5,I6085B      (ext)'),
    ('021371.40', '2.13 D0',      'SVA,$X5,$IA          point $IA at the NOP table'),
    ('021372.00', '21372.40 00',  'BE,I6086A           enable'),
    ('021372.40', '21373.04 00',  'I6086A BD,$+.32     disable, so DS can be read'),
    ('021373.00', '2.11 D0',      'SVA,$X4,$IA          restore the saved address'),
    ('021373.40', '21375.51 C2',  'BDS,I6086B          DS set -> pass'),
    ('021374.00', '1310.00 80',   'SIC,SEN              (ext)'),
    ('021374.40', '1304.10 00',   'B,SERS               (ext) "SV TO 1.0 FAILS TO SET"'),
    ('021375.00', '21734.10 00',  'B,I6093             (ext) "DS WHEN ENABLED."'),
    ('021375.40', '21376.10 46',  'I6086B BADZ,$+.32   clear AD on the way out'),
    ('021376.00', '21400.50 00',  'B,I6088             (ext) bit 18 set: I6088 is at .40'),
]

SYMBOLS = {
    'I6086':  '021365.00',
    'I6086A': '021372.40',
    'I6086B': '021375.40',
}

finish(check_rows(prog, ROWS, SYMBOLS, label='1260 DS '))
