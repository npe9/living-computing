#!/usr/bin/env python3
"""verify_ibox1_vmi_listing.py -- IBOX-1 routine IBP-IBP14
(../decks/ibox1_vmi.strap) against ja_ax1a pp.35-36.

Chosen by measurement: V-I as a DIRECT IMMEDIATE OPCODE was one of the
five index operations still shown unreachable.  Not to be confused with
the "V-I" that is a progressive modifier on a VFL instruction, which
ibox4_prog_ix_v already reaches through a different path entirely.

The block manufactures its own branch chain out of the value field and
ends by storing the whole index word with SX, so IBPA1's refill of -1
lands in the half-word the listing annotates "-ALL ONES".
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("../decks/ibox1_vmi.strap").read())

CODE_ROWS = [
    ('004551.00', '4563.02 10', 'IBP LX, $X1, IBPA1   set up XW'),
    ('004551.40', '0.43 0D', 'IBP1 V-I, $X1, 0.32   subtract from value +.32'),
    ('004552.00', '4562.43 30', 'SV, $X1, IBP13   store new value'),
    ('004552.40', '2.03 0D', 'IBP2 V-I, $X1, 2.0   subtract from value +2.0'),
    ('004553.00', '4562.03 30', 'SV, $X1, IBP12   store new value'),
    ('004553.40', '777776.03 0D', 'IBP3 V-I, $X1, (8)777776.0'),
    ('004554.00', '777777.03 05', 'V+I, $X1, (8)777777.0'),
    ('004554.40', '4560.03 30', 'SV, $X1, IBP8   store new value'),
    ('004555.00', '2.43 0D', 'IBP4 V-I, $X1, 2.32   subtract from value 2.32'),
    ('004555.40', '4561.03 10', 'SX, $X1, IBP10   store index'),
    ('004556.00', '4562.50 00', 'IBP4A B, IBP13   branch to test IBP13'),
    ('004556.40', '4564.10 00', 'IBP5 B, IBP14   go to next routine'),
    ('004557.00', '4557.10 00', 'IBP6 B, $   hang up'),
    ('004557.40', '4557.50 00', 'IBP7 B, $   hang up'),
    ('004560.00', '4560.10 00', 'IBP8 B, $   becomes BD, IBP10'),
    ('004560.40', '4560.50 00', 'IBP9 B, $   hang up'),
    ('004561.00', '4561.10 00', 'IBP10 B, $   becomes BD, IBP5'),
    ('004561.40', '4561.50 00', 'IBP11 B, $   becomes all ones'),
    ('004562.00', '4562.10 00', 'IBP12 B, $   becomes BD, IBP8'),
    ('004562.40', '4562.50 00', 'IBP13 B, $   becomes BD, IBP12'),
    ('004563.00', '4562.44 00 777777.77 FF', 'IBPA1 XW, IBP13+(8).04, (8)37777, -1'),
]

if __name__ == "__main__":
    finish(check_rows(prog, CODE_ROWS, label="code"))
