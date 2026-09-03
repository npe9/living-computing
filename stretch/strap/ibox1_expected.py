#!/usr/bin/env python3
"""ibox1_expected.py -- derive the expected final state of a verbatim
I-Box 1 transcription for run_tests.sh, from the assembled program
itself rather than by hand (same pattern as the CBR test's symbol-
table-derived expectations).

Usage: ibox1_expected.py PROGRAM.strap END_LABEL SPEC [SPEC ...]

Prints run_program.sh check arguments: a PC check (halted at
END_LABEL, the transcription's substituted terminal BEW,$) and one
full-word check per SPEC, each a word the deck rewrites at run time:

  HANG:NEXT          a "BD,$" hang rewritten into "BD,NEXT" -- by a SIC
                     storing the instruction counter into it, or by the
                     LV/SV patch that sets up a chain's last hop; the
                     other half of the word is unchanged from assembly.
                     The pairs are the listing's own "HANG UP OR BECOME
                     BD,..." comments, transcribed.
  LABEL=XW:V,C,R     a word overwritten by SX,$X1,LABEL with X1's whole
                     index word at that point: value V (any address
                     expression, e.g. IBR107+(8).04), count C, refill R
                     (a label; stored as a word address), packed exactly
                     as strap_asm.py packs an XW literal. The deck's
                     "SX FOR VALUE TEST" stores: V is the value the
                     comments say the count-and-branch variant should
                     have produced (e.g. two CBR+ from IBR106+.04 give
                     IBR107+.04), so this is where the H/+/- units are
                     checked.
  LABEL=COPY:OTHER   a word overwritten with the assembled contents of
                     OTHER -- the deck's "SX + TEST FOR REFILL" stores,
                     where X1 has just been refilled from OTHER's XW.
import sys
from strap_asm import assemble, enc_branch_or_misc, eval_expr
from opcodes import UNCOND_BRANCH_CODES

prog = assemble(open(sys.argv[1]).read())
sym = prog.symtab

def bd_to(label):
    return enc_branch_or_misc((sym[label] >> 5) & 0x7FFFF, UNCOND_BRANCH_CODES['BD'], False, 0)

def pack_xw(vexpr, cexpr, rexpr):
    """Mirror emit_statement's XW packing (value sign-magnitude, count
    18 bits, refill = bit address >> 6, flag 0)."""
    val = eval_expr(vexpr, sym, 0)
    sign = 1 if val < 0 else 0
    mag = abs(val) & 0xFFFFFF
    count = eval_expr(cexpr, sym, 0) & 0x3FFFF
    refill = (eval_expr(rexpr, sym, 0) >> 6) & 0x3FFFF
    return (mag << 40) | (sign << 39) | (count << 18) | refill

args = [f"PC={sym[sys.argv[2]] // 32}"]
for spec in sys.argv[3:]:
    if '=XW:' in spec:
        label, rest = spec.split('=XW:')
        v, c, r = rest.split(',')
        args.append(f"{label}_SX_value_test:{sym[label] // 64}=0x{pack_xw(v, c, r):016x}")
    elif '=COPY:' in spec:
        label, other = spec.split('=COPY:')
        args.append(f"{label}_SX_refill_test:{sym[label] // 64}=0x{prog.words[sym[other] // 64]:016x}")
    else:
        hang, nxt = spec.split(':')
        bits = sym[hang]
        word = prog.words[bits // 64]
        half = bd_to(nxt)
        exp = (half << 32) | (word & 0xFFFFFFFF) if bits % 64 == 0 else (word & ~0xFFFFFFFF) | half
        args.append(f"{hang}_becomes_BD_{nxt}:{bits // 64}=0x{exp:016x}")
print(" ".join(args))
