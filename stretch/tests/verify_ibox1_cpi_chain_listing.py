#!/usr/bin/env python3
"""verify_ibox1_cpi_chain_listing.py -- IBOX-1 routine IBP54-IBP65
(../decks/ibox1_cpi_chain.strap) against ja_ax1a p.38 (code) and p.59
(the scratch cells).

Chosen by measurement: C+I and SC were two of the seven index
operations still shown unreachable after IBOX-4 closed KC and SR.

The block checks itself without a SERS.  Each step stores the COUNT,
reads it back as a VALUE, adds COM04, and stores the result over a
branch-to-self.  All four sums were derived from the constants before
the first run and land on the chain the listing's comments name:
IBP59 -> IBP61 -> IBP62 -> IBP64 -> IBP63 -> IBP65.
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("../decks/ibox1_cpi_chain.strap").read())

CODE_ROWS = [
    ('004653.00', '4667.03 02', 'IBP54 LCI, $X1, IBP58+2.32   set up count'),
    ('004653.40', '3.03 00', 'IBP55 C+I, $X1, 3.0   C+3.0'),
    ('004654.00', '6105.03 50', 'SC, $X1, ISTOY'),
    ('004654.40', '6105.02 30', 'LV, $X1, ISTOY'),
    ('004655.00', '6106.02 B0', 'V+, $X1, COM04'),
    ('004655.40', '4670.03 30', 'SV, $X1, IBP59   store for test'),
    ('004656.00', '0.30 00', 'NOP, 0.0'),
    ('004656.40', '1.03 00', 'IBP56 C+I, $X1, 1.0   C+1.0'),
    ('004657.00', '6105.03 50', 'SC, $X1, ISTOY'),
    ('004657.40', '6105.02 30', 'LV, $X1, ISTOY'),
    ('004660.00', '6106.02 B0', 'V+, $X1, COM04'),
    ('004660.40', '4672.03 30', 'SV, $X1, IBP61   store for test'),
    ('004661.00', '0.30 00', 'NOP, 0.0'),
    ('004661.40', '2.03 00', 'IBP57 C+I, $X1, 2.0   C+2.0'),
    ('004662.00', '6105.03 50', 'SC, $X1, ISTOY'),
    ('004662.40', '6105.02 30', 'LV, $X1, ISTOY'),
    ('004663.00', '6106.02 B0', 'V+, $X1, COM04'),
    ('004663.40', '4673.03 30', 'SV, $X1, IBP62   store for test'),
    ('004664.00', '0.30 00', 'NOP, 0.0'),
    ('004664.40', '777777.03 00', 'IBP58 C+I, $X1, (8)777777.0   C-1.0'),
    ('004665.00', '6105.03 50', 'SC, $X1, ISTOY'),
    ('004665.40', '6105.02 30', 'LV, $X1, ISTOY'),
    ('004666.00', '6106.02 B0', 'V+, $X1, COM04'),
    ('004666.40', '4675.03 30', 'SV, $X1, IBP64   store for test'),
    ('004667.00', '0.30 00', 'NOP, 0.0'),
    ('004667.40', '0.30 00', 'NOP'),
    ('004670.00', '0.10 00', 'IBP59 B, 0.0'),
    ('004670.40', '4670.44 00', 'BD, $'),
    ('004671.00', '4671.04 00', 'IBP60 BD, $'),
    ('004671.40', '4671.44 00', 'BD, $'),
    ('004672.00', '4672.10 00', 'IBP61 B, $'),
    ('004672.40', '4672.44 00', 'BD, $'),
    ('004673.00', '4673.10 00', 'IBP62 B, $'),
    ('004673.40', '4673.44 00', 'BD, $'),
    ('004674.00', '777777.70 00', 'IBP63 NOP, -1'),
    ('004674.40', '4676.04 00', 'BD, IBP65'),
    ('004675.00', '4675.10 00', 'IBP64 B, $'),
    ('004675.40', '4675.44 00', 'BD, $'),
]

if __name__ == "__main__":
    finish(check_rows(prog, CODE_ROWS, label="code"))
