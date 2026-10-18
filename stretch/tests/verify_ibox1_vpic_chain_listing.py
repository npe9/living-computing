#!/usr/bin/env python3
"""verify_ibox1_vpic_chain_listing.py -- IBOX-1 routine IBM-IBM60
(../decks/ibox1_vpic_chain.strap) against ja_ax1a pp.33-34.

V+IC, the LAST of the eight modeled index operations a coverage screen
found in zero suite programs.  The only TWO-PHASE block in the suite:
six V+IC tests store their values over one chain of branch-to-self
half-words and their counts into plain data words, and a second phase
reads those counts back, adds a 0.4 constant, and stores the sums over
a second chain.
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("../decks/ibox1_vpic_chain.strap").read())

CODE_ROWS = [
    ('004423.00', '777777.30 00', 'IBM NOP, -1.0   start V+IC test'),
    ('004423.40', '4507.02 10', 'IBM1 LX, $X1, IBM58   set up, V is N, C is P'),
    ('004424.00', '1.03 06', 'IBM2 V+IC, $X1, 1.0   N+1, P-1'),
    ('004424.40', '4447.43 30', 'SV, $X1, IBM9'),
    ('004425.00', '6105.03 50', 'SC, $X1, ISTOY'),
    ('004425.40', '6105.02 30', 'LV, $X1, ISTOY'),
    ('004426.00', '6106.02 B0', 'V+, $X1, COM04'),
    ('004426.40', '4461.43 30', 'SV, $X1, IBM29'),
    ('004427.00', '4447.42 30', 'LV, $X1, IBM9'),
    ('004427.40', '2.03 06', 'IBM3 V+IC, $X1, 2.0   N+3, P-2'),
    ('004430.00', '4450.43 30', 'SV, $X1, IBM11'),
    ('004430.40', '6105.03 50', 'SC, $X1, ISTOY'),
    ('004431.00', '6105.02 30', 'LV, $X1, ISTOY'),
    ('004431.40', '4462.03 30', 'SV, $X1, IBM30'),
    ('004432.00', '4450.42 30', 'LV, $X1, IBM11'),
    ('004432.40', '3.03 06', 'IBM4 V+IC, $X1, 3.0   N+6, P-3'),
    ('004433.00', '4452.43 30', 'SV, $X1, IBM15'),
    ('004433.40', '6105.03 50', 'SC, $X1, ISTOY'),
    ('004434.00', '6105.02 30', 'LV, $X1, ISTOY'),
    ('004434.40', '4462.43 30', 'SV, $X1, IBM31'),
    ('004435.00', '4452.42 30', 'LV, $X1, IBM15'),
    ('004435.40', '777777.03 06', 'IBM5 V+IC, $X1, 262143.0   N+5, P-4'),
    ('004436.00', '4455.43 30', 'SV, $X1, IBM21'),
    ('004436.40', '6105.03 50', 'SC, $X1, ISTOY'),
    ('004437.00', '6105.02 30', 'LV, $X1, ISTOY'),
    ('004437.40', '4463.03 30', 'SV, $X1, IBM32'),
    ('004440.00', '4455.42 30', 'LV, $X1, IBM21'),
    ('004440.40', '4.03 06', 'IBM6 V+IC, $X1, 4.0   N+9, P-5'),
    ('004441.00', '4454.43 30', 'SV, $X1, IBM19'),
    ('004441.40', '6105.03 50', 'SC, $X1, ISTOY'),
    ('004442.00', '6105.02 30', 'LV, $X1, ISTOY'),
    ('004442.40', '4463.43 30', 'SV, $X1, IBM33'),
    ('004443.00', '4454.42 30', 'LV, $X1, IBM19'),
    ('004443.40', '777776.03 06', 'IBM7 V+IC, $X1, 262142.0   N+7, P-6'),
    ('004444.00', '4460.43 30', 'SV, $X1, IBM27'),
    ('004444.40', '6105.03 50', 'SC, $X1, ISTOY'),
    ('004445.00', '6105.02 30', 'LV, $X1, ISTOY'),
    ('004445.40', '6106.02 B0', 'V+, $X1, COM04'),
    ('004446.00', '4464.03 30', 'SV, $X1, IBM34'),
    ('004446.40', '4460.42 30', 'LV, $X1, IBM27'),
    ('004447.00', '0.30 00', 'IBM8 NOP, 0.0   prove add to value'),
    ('004447.40', '4447.40 00', 'IBM9 BE, $   becomes BD, IBM11, from IBM2A'),
    ('004450.00', '4450.04 00', 'IBM10 BD, $'),
    ('004450.40', '4450.40 00', 'IBM11 BE, $   becomes BD, IBM15, from IBM3A'),
    ('004451.00', '4451.04 00', 'IBM12 BD, $'),
    ('004451.40', '4451.44 00', 'IBM13 BD, $'),
    ('004452.00', '4452.04 00', 'IBM14 BD, $'),
    ('004452.40', '4452.40 00', 'IBM15 BE, $   becomes BD, IBM21, from IBM4A'),
    ('004453.00', '4453.04 00', 'IBM16 BD, $'),
    ('004453.40', '4453.44 00', 'IBM17 BD, $'),
    ('004454.00', '4454.04 00', 'IBM18 BD, $'),
    ('004454.40', '4454.40 00', 'IBM19 BE, $   becomes BD, IBM27, from IBM6A'),
    ('004455.00', '4455.04 00', 'IBM20 BD, $'),
    ('004455.40', '4455.40 00', 'IBM21 BE, $   becomes BD, IBM19, from IBM5A'),
    ('004456.00', '4456.04 00', 'IBM22 BD, $'),
    ('004456.40', '4464.44 00', 'IBM23 BD, IBM35   to prove counting opn'),
    ('004457.00', '4457.04 00', 'IBM24 BD, $'),
    ('004457.40', '4457.44 00', 'IBM25 BD, $'),
    ('004460.00', '4460.04 00', 'IBM26 BD, $'),
    ('004460.40', '4460.40 00', 'IBM27 BE, $   becomes BD, IBM23, from IBM7'),
    ('004461.00', '4461.04 00', 'IBM28 BD, $'),
    ('004461.40', '0.00 00', 'IBM29 BE, 0   count field storage, P-1'),
    ('004462.00', '0.00 00', 'IBM30 BE, 0   P-2'),
    ('004462.40', '0.00 00', 'IBM31 BE, 0   P-3'),
    ('004463.00', '0.00 00', 'IBM32 BE, 0   P-4'),
    ('004463.40', '0.00 00', 'IBM33 BE, 0   P-5'),
    ('004464.00', '0.00 00', 'IBM34 BE, 0   P-6'),
    ('004464.40', '4510.02 10', 'IBM35 LX, $X1, IBM59   V has .4 to give BD opn code'),
    ('004465.00', '4461.42 B0', 'V+, $X1, IBM29'),
    ('004465.40', '4504.03 30', 'SV, $X1, IBM53   P-1 with BD opn code'),
    ('004466.00', '4510.02 10', 'IBM36 LX, $X1, IBM59'),
    ('004466.40', '4462.02 B0', 'V+, $X1, IBM30   P-2 with BD op code'),
    ('004467.00', '4503.03 30', 'SV, $X1, IBM51'),
    ('004467.40', '4510.02 10', 'IBM37 LX, $X1, IBM59'),
    ('004470.00', '4462.42 B0', 'V+, $X1, IBM31   P-3 with BD op code'),
    ('004470.40', '4502.03 30', 'SV, $X1, IBM49'),
    ('004471.00', '4510.02 10', 'IBM38 LX, $X1, IBM59'),
    ('004471.40', '4463.02 B0', 'V+, $X1, IBM32   P-4 with BD op code'),
    ('004472.00', '4501.03 30', 'SV, $X1, IBM47'),
    ('004472.40', '4510.02 10', 'IBM39 LX, $X1, IBM59'),
    ('004473.00', '4463.42 B0', 'V+, $X1, IBM33   P-5 with BD op code'),
    ('004473.40', '4500.03 30', 'SV, $X1, IBM45'),
    ('004474.00', '4510.02 10', 'IBM40 LX, $X1, IBM59'),
    ('004474.40', '4464.02 B0', 'V+, $X1, IBM34   P-6 with BD op code'),
    ('004475.00', '4477.03 30', 'SV, $X1, IBM43'),
    ('004475.40', '0.30 00', 'CNOP'),
    ('004476.00', '4477.04 00', 'IBM41 BD, IBM43'),
    ('004476.40', '4476.44 00', 'IBM42 BD, $'),
    ('004477.00', '4477.00 00', 'IBM43 BE, $   becomes BD, IBM45 from IBM40/7B'),
    ('004477.40', '4477.44 00', 'IBM44 BD, $'),
    ('004500.00', '4500.00 00', 'IBM45 BE, $   becomes BD, IBM47 from IBM39/6B'),
    ('004500.40', '4500.44 00', 'IBM46 BD, $'),
    ('004501.00', '4501.00 00', 'IBM47 BE, $   becomes BD, IBM49 from IBM38/5B'),
    ('004501.40', '4501.44 00', 'IBM48 BD, $'),
    ('004502.00', '4502.00 00', 'IBM49 BE, $   becomes BD, IBM51 from IBM37/4B'),
    ('004502.40', '4502.44 00', 'IBM50 BD, $'),
    ('004503.00', '4503.00 00', 'IBM51 BE, $   becomes BD, IBM53 from IBM36/3B'),
    ('004503.40', '4503.44 00', 'IBM52 BD, $'),
    ('004504.00', '4504.00 00', 'IBM53 BE, $   becomes BD, IBM55 from IBM35/2B'),
    ('004504.40', '4504.44 00', 'IBM54 BD, $'),
    ('004505.00', '4511.04 00', 'IBM55 BD, IBM60   to next test'),
    ('004505.40', '777777.30 00', 'IBM56 NOP, -1.0'),
    ('004506.00', '777777.30 00', 'IBM57 NOP, -1.0'),
    ('004510.00', '0.04 00 000000.00 00', 'IBM59 XW, 0.4, 0, 0   to convert C to BD, C'),
    ('004511.00', '777777.70 00', 'IBM60 NOP, -1'),
]

DATA_ROWS = [
    ('004507.00', '4447.44 00 112140.00 00', 'IBM58 XW, IBM9+(8)0.04, (8)4506, 0'),
]

if __name__ == "__main__":
    fails = check_rows(prog, CODE_ROWS, label="code")
    fails += check_rows(prog, DATA_ROWS, label="data")
    finish(fails)
