#!/usr/bin/env python3
"""A numeric DD in use mode D or DU: one decimal digit a byte.

THE RULE.  C28-6129 printed p.15 (PDF 19), read in the ink 2026-11-23:
"When use mode D is specified, a character-by-character type of
conversion is called for, wherein each decimal digit in the numeric
entry is converted to the four bit binary coded decimal form.  If the
byte size specified in the dds is greater than 4, high order zeros are
added. ... If use mode DU is specified, the conversion process is the
same.  However, no sign byte is compiled", and the page PRINTS one
compiled field:

    DD(DU, 12, 4),12        000000010010

Printed p.30 (PDF 34), "Decimal Signed VFL": the radix entry mode is the
radix the number is written in (example b, "(2)DD(D, 20),
111010001101S7 ... Binary-to-decimal conversion"), E multiplies by
powers of ten, and an omitted FL or BS is 64 or 4; example c, "DD(D, ,
8), 432E3 ... Four binary zeros are inserted in the zone positions of
each byte".  Minus is S10 in a 4-bit sign byte (printed p.29, PDF 33).
strap_asm assembled all of these as a binary integer until 2026-11-23
(docs/NEXT.md, "strap_asm ASSEMBLES A DECIMAL-MODE DD AS A BINARY
INTEGER", found transcribing C22-6578 Problem 2.8).

CHECKS, each row under strap_asm and under the host STRAP II
(strap/strap2), against the value worked from the rule:
  p15_printed            DD(DU,12,4),12      the page's printed bits
  repro_DU8 .. repro_DS4 decks/repro_dd_decimal_mode.strap's four rows
  p30_a_D / p30_a_DU      p.30's examples a without S, and (8) 77241
  p30_b_radix2           p.30 example b without its S7
  p30_c_zone             p.30 example c, byte size 8
  bu_control             DD(BU,16,8),12, binary, unchanged
and two refusals under strap_asm (both host STRAP II refuses, 45):
  refuse_bs3             a byte size under 4 ("truncation occurs", p.15,
                         by a rule the page does not print)
  refuse_overflow        more digits than the field holds

MEASURED 2026-11-23, after the fix: 22 of 22 (12 strap_asm, 10 strap2).

INJECTIONS (2026-11-23, each applied to strap_asm.py, run, and the file
restored from its saved copy and cmp'd):
  1. The D/DU branch in emit_statement bypassed (every DD through
     parse_dd_literal, as before the fix): the 9 strap_asm value rows
     other than bu_control and both refusals FAIL (000C for 12, 04D2 for
     1234, FF85 for -123: binary integers); 11 PASS, every strap2 row and
     strap_asm_bu_control among them.
  2. The sign byte's 0b1000 made 0b0001 (tests/inject.py): exactly
     strap_asm_repro_DS4 and strap_asm_p30_a_D FAIL.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'strap'))
sys.path.insert(0, HERE)

from strap_asm import assemble, AssemblerError   # noqa: E402
import gen_tb                                    # noqa: E402

# (name, statement, bits, the value right-justified in those bits)
ROWS = [
    ('p15_printed', 'DD(DU, 12, 4),12', 12, 0b000000010010),
    ('repro_DU8', 'DD(DU,16,8), 12', 16, 0x0102),
    ('repro_DU4', 'DD(DU,16,4), 1234', 16, 0x1234),
    ('repro_DUE', 'DD(DU,48,8), 000125', 48, 0x000000010205),
    ('repro_DS4', 'DD(D,16,4), -123', 16, 0x1238),
    ('p30_a_D', 'DD(D), -9534812', 64, 0x95348128),
    ('p30_a_DU', 'DD(DU), (8) 77241', 64, 0x32417),
    ('p30_b_radix2', '(2)DD(D, 20), 111010001101', 20, 0x37250),
    ('p30_c_zone', 'DD(D, , 8), 432E3', 64, 0x0004030200000000),
    ('bu_control', 'DD(BU,16,8), 12', 16, 0x000C),
]
REFUSE = [('refuse_bs3', 'DD(D,16,3), 12'), ('refuse_overflow', 'DD(DU,8,4), 123')]


def deck(stmt):
    return ('        SLC, 1000.0\nS       BEW, $\n        SLC, 1001.0\n'
            '        %s\n        END, S\n' % stmt)


def main():
    failed = 0

    def check(name, ok, detail=''):
        nonlocal failed
        print('%s %s%s' % ('PASS' if ok else 'FAIL', name, (' -- ' + detail) if detail else ''))
        failed += 0 if ok else 1

    for asm_name, asm in (('strap_asm', assemble), ('strap2', gen_tb.strap2_program)):
        for name, stmt, bits, want in ROWS:
            want_word = want << (64 - bits)
            try:
                got = asm(deck(stmt)).words.get(1001, 0)
                check('%s_%s' % (asm_name, name), got == want_word,
                      '%s: got %016x want %016x' % (stmt, got, want_word))
            except AssemblerError as e:
                check('%s_%s' % (asm_name, name), False, '%s: %s' % (stmt, e))
        if asm_name == 'strap_asm':
            for name, stmt in REFUSE:
                try:
                    got = asm(deck(stmt)).words.get(1001, 0)
                    check('%s_%s' % (asm_name, name), False,
                          '%s assembled to %016x' % (stmt, got))
                except AssemblerError as e:
                    check('%s_%s' % (asm_name, name), True, str(e)[:90])

    if failed:
        print('%d TEST(S) FAILED' % failed)
        return 1
    print('ALL TESTS PASSED')
    return 0


if __name__ == '__main__':
    sys.exit(main())
