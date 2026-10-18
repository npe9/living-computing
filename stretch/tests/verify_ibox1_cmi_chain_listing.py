#!/usr/bin/env python3
"""verify_ibox1_cmi_chain_listing.py -- IBOX-1 routine IBP66-IBP77
(../decks/ibox1_cmi_chain.strap) against ja_ax1a pp.38-39 (code) and
p.59 (the scratch cells).

Chosen by measurement: C-I was one of the five index operations still
shown unreachable after ibox1_cpi_chain closed C+I and SC.

Like its C+I sibling the block checks itself without a SERS: each step
stores the COUNT, reads it back as a VALUE, adds COM04, and stores the
result over a branch-to-self.  All four sums were derived from the
constants before the first run and land on the chain the listing's
comments name: IBP71 -> IBP76 -> IBP73 -> IBP74 -> IBP72 -> IBP77.
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("../decks/ibox1_cmi_chain.strap").read())

CODE_ROWS = [
    ('004677.00', '4723.03 02', 'IBP66 LCI, $X1, IBP77   set up count'),
    ('004677.40', '0.30 00', 'CNOP'),
    ('004700.00', '1.03 08', 'IBP67 C-I, $X1, 1.0   C-1.0'),
    ('004700.40', '6105.03 50', 'SC, $X1, ISTOY'),
    ('004701.00', '6105.02 30', 'LV, $X1, ISTOY'),
    ('004701.40', '6106.02 B0', 'V+, $X1, COM04'),
    ('004702.00', '4715.03 30', 'SV, $X1, IBP71   store for test'),
    ('004702.40', '0.30 00', 'NOP, 0.0'),
    ('004703.00', '3.03 08', 'IBP68 C-I, $X1, 3.0   C-3.0'),
    ('004703.40', '6105.03 50', 'SC, $X1, ISTOY'),
    ('004704.00', '6105.02 30', 'LV, $X1, ISTOY'),
    ('004704.40', '6106.02 B0', 'V+, $X1, COM04'),
    ('004705.00', '4722.03 30', 'SV, $X1, IBP76   store for test'),
    ('004705.40', '0.30 00', 'NOP, 0.0'),
    ('004706.00', '777777.03 08', 'IBP69 C-I, $X1, (8)777777.0   C+1.0'),
    ('004706.40', '6105.03 50', 'SC, $X1, ISTOY'),
    ('004707.00', '6105.02 30', 'LV, $X1, ISTOY'),
    ('004707.40', '6106.02 B0', 'V+, $X1, COM04'),
    ('004710.00', '4717.03 30', 'SV, $X1, IBP73   store for test'),
    ('004710.40', '0.30 00', 'NOP, 0.0'),
    ('004711.00', '2.03 08', 'IBP70 C-I, $X1, 2.0   C-2.0'),
    ('004711.40', '6105.03 50', 'SC, $X1, ISTOY'),
    ('004712.00', '6105.02 30', 'LV, $X1, ISTOY'),
    ('004712.40', '6106.02 B0', 'V+, $X1, COM04'),
    ('004713.00', '4720.03 30', 'SV, $X1, IBP74   store for test'),
    ('004713.40', '0.30 00', 'NOP, 0.0'),
    ('004714.00', '6104.02 10', 'LX, $X1, ISTOZ'),
    ('004714.40', '0.30 00', 'CNOP'),
    ('004715.00', '0.10 00', 'IBP71 B, 0.0'),
    ('004715.40', '4715.44 00', 'BD, $'),
    ('004716.00', '777777.70 00', 'IBP72 NOP, -1'),
    ('004716.40', '4723.04 00', 'BD, IBP77'),
    ('004717.00', '0.10 00', 'IBP73 B, 0.0'),
    ('004717.40', '4717.44 00', 'BD, $'),
    ('004720.00', '0.10 00', 'IBP74 B, 0.0'),
    ('004720.40', '4720.44 00', 'BD, $'),
    ('004721.00', '4721.10 00', 'IBP75 B, $'),
    ('004721.40', '4721.44 00', 'BD, $'),
    ('004722.00', '0.10 00', 'IBP76 B, 0.0'),
    ('004722.40', '4722.44 00', 'BD, $'),
]

if __name__ == "__main__":
    finish(check_rows(prog, CODE_ROWS, label="code"))
