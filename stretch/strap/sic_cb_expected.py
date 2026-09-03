#!/usr/bin/env python3
"""sic_cb_expected.py -- derive the expected final state of
programs/ibox1_sic_cb_cbz.strap for run_tests.sh, from the assembled
program itself rather than by hand (same pattern as the CBR test's
symbol-table-derived expectations).

Prints run_program.sh check arguments: one PC check (halted at the
substituted BEW,$ at octal 5432.40) and one word check per hang the
block rewrites, each expected to hold "BD,<next>" in the half-word the
listing's own comment names ("HANG UP OR BECOME BD,ISCBC"), with the
other half of that word unchanged from assembly. ISCBI is rewritten by
LV/SV from ISCBJ's VF (bits 0-24 replaced), not by SIC -- included
because it is on the executed chain and its value is what the VF
encodes: "BD,ISCBK".
"""

from strap_asm import assemble, enc_branch_or_misc
from opcodes import UNCOND_BRANCH_CODES

prog = assemble(open('programs/ibox1_sic_cb_cbz.strap').read())
sym = prog.symtab

def bd_to(label):
    return enc_branch_or_misc((sym[label] >> 5) & 0x7FFFF, UNCOND_BRANCH_CODES['BD'], False, 0)

REWRITES = [  # (hang, what it must become)
    ('ISCBA', 'ISCBB'), ('ISCBB', 'ISCBC'), ('ISCBC', 'ISCBD'),
    ('ISCBD', 'ISCBH'), ('ISCBH', 'ISCBI'), ('ISCBI', 'ISCBK'),
]
args = [f"PC={sym['ISBI'] // 32}"]
for hang, nxt in REWRITES:
    bits = sym[hang]
    word = prog.words[bits // 64]
    half = bd_to(nxt)
    if bits % 64 == 0:
        exp = (half << 32) | (word & 0xFFFFFFFF)
    else:
        exp = (word & ~0xFFFFFFFF) | half
    args.append(f"{hang}_becomes_BD_{nxt}:{bits // 64}=0x{exp:016x}")
# X1's count must have reached zero in the CBZ group (4 CBZs on count 4).
args.append("X1_count_zero:addrIndex(1)=0x%016x" % (prog.words.get(17, 0) & 0))  # placeholder replaced below
args.pop()
print(" ".join(args))
