#!/usr/bin/env python3
r"""An integer in parentheses after a datum is a SUBSCRIPT, not an index.

THE RULE, read in the ink 2026-11-23 (and 2026-11-15, docs/NEXT.md):
  C28-6129 printed p.11 (PDF 15), "Address Field": "STRAP bit addresses,
    system symbols and programmer symbols that are defined as bit
    addresses are all legal entries in an index field. ... All of the
    following entries are equivalent in an index subfied of an address:
    4.32 = 4.0 = $4 = 20.0 = 52.0 and all are translated by STRAP to
    mean index register 4.  If an integer is written in the index field,
    the meaning is entirely different.  The integer tells STRAP that the
    symbol in the address field proper has been defined as an array and
    the integer is addressing an element in that array."
  C28-6129 printed p.32 (PDF 36), restriction 3: 'The "I" or "K" fields
    ... must contain at least one STRAP bit address term.'
  C22-6729 printed p.203 (Appendix E): "Dimension or Subscript -- This is
    an integer specified within parentheses after a symbol to refer to an
    item within an array"; "Bit Style Number -- ... Since $3 is
    considered a bit style number and may be written 3.0, a bit style
    datum may also be called an X-datum"; printed p.204: "Since a
    subscript is an example of this, an integer style datum may also be
    called an S-datum."  Appendix C (printed p.198) item 2E codes the
    parenthetical after a symbol as "subscript ('subscript' may be
    index)", so the coded expression does not decide it; VALUE does.

strap_asm took "L,JOE(3)" as index register 3, as strap/strap2 still
does.  What STRAP II assembles for a subscript of a symbol with no dds
(message 74) or of a constant (72, "TRY INDEX"), C22-6729 printed p.177,
is not printed, subscripts of arrays are not implemented in strap_asm,
and printed p.26 reads the (7) of "INFO(7)(.30)1265" as a RADIX, a
third reading.  So strap_asm now REFUSES a parenthetical with no
bit-address term, loud, and assembles every index p.11 names.

CHECKS (strap_asm unless named)
  refuse_*          L,INFO(3) / L,JOE(3) / L,100(3) / L,INFO(JOE) /
                    B,INFO(3) / LX,1,INFO(3) / L,INFO(7)(.30)1265 /
                    KV,2,(3) are refused, the message naming p.11
  p11_index4_*      p.11's five equivalent spellings 4.32, 4.0, $4, 20.0,
                    52.0 all give index 4 (the I field of L,INFO(...))
  sum_index         ($1+1) is index 2 (an integer term beside a bit
                    address term, p.34 item 8: "Integers represent index
                    register number")
  label_index       (INFO), a programmer symbol defined as a bit address,
                    is an index (p.11), INFO's word mod 16
  strap2_PINNED_index3
                    strap2 still makes L,JOE(3) index 3.  THIS PINS A
                    KNOWN DISAGREEMENT (strap2's getfld _paren, CHOSEN);
                    when strap2 is changed, change this check.

MEASURED 2026-11-23 before the fix (the saved strap_asm.py): all 8
refuse_* checks FAIL (each assembled, with index 3, 3, 3, 3, 3, 3, 7, 3);
the other 8 PASS.  After: 16 of 16.

INJECTIONS (2026-11-23, each restored from the saved copy and cmp'd):
  1. _has_bit_address_term answers True for an 'int' token: 7 FAIL, every
     refuse_* but refuse_INFO_JOE (JOE is a symbol, not an int token).
  2. any 'sym' counts, integer-classified or not: exactly refuse_INFO_JOE
     FAILS.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'strap'))
sys.path.insert(0, HERE)

from strap_asm import assemble, AssemblerError   # noqa: E402
import gen_tb                                    # noqa: E402

HEAD = ('        SLC, 1000.0\nS       BEW, $\n        SLC, 1001.0\n'
        'INFO    DD(BU,64),5\nJOE     SYN,3\n        SLC, 1004.0\n')
AT = 1004


def deck(stmt):
    return HEAD + 'T       %s\n        END, S\n' % stmt


def ifield(word):
    """The I field of the instruction's first half word (bits 28-31)."""
    return (word >> 32) & 0xF


def main():
    failed = 0

    def check(name, ok, detail=''):
        nonlocal failed
        print('%s %s%s' % ('PASS' if ok else 'FAIL', name, (' -- ' + detail) if detail else ''))
        failed += 0 if ok else 1

    for name, stmt in [('refuse_INFO_3', 'L,INFO(3)'), ('refuse_JOE_3', 'L,JOE(3)'),
                       ('refuse_const_3', 'L,100(3)'), ('refuse_INFO_JOE', 'L,INFO(JOE)'),
                       ('refuse_branch', 'B,INFO(3)'), ('refuse_LX', 'LX,1,INFO(3)'),
                       ('refuse_p26_radix', 'L,INFO(7)(.30)1265'), ('refuse_null_datum', 'KV,2,(3)')]:
        try:
            w = assemble(deck(stmt)).words.get(AT, 0)
            check(name, False, '%s assembled, I field %d' % (stmt, ifield(w)))
        except AssemblerError as e:
            check(name, 'p.11' in str(e), '%s: %s' % (stmt, str(e)[:70]))

    for tag, ix in [('4p32', '4.32'), ('4p0', '4.0'), ('d4', '$4'), ('20p0', '20.0'), ('52p0', '52.0')]:
        try:
            w = assemble(deck('L,INFO(%s)' % ix)).words.get(AT, 0)
            check('p11_index4_' + tag, ifield(w) == 4, 'L,INFO(%s) I field %d' % (ix, ifield(w)))
        except AssemblerError as e:
            check('p11_index4_' + tag, False, str(e))

    try:
        w = assemble(deck('L,INFO($1+1)')).words.get(AT, 0)
        check('sum_index', ifield(w) == 2, 'I field %d' % ifield(w))
    except AssemblerError as e:
        check('sum_index', False, str(e))
    try:
        w = assemble(deck('L,INFO(INFO)')).words.get(AT, 0)
        check('label_index', ifield(w) == 1001 % 16, 'I field %d' % ifield(w))
    except AssemblerError as e:
        check('label_index', False, str(e))

    try:
        w = gen_tb.strap2_program(deck('L,JOE(3)')).words.get(AT, 0)
        check('strap2_PINNED_index3', ifield(w) == 3, 'strap2 I field %d' % ifield(w))
    except AssemblerError as e:
        check('strap2_PINNED_index3', False, str(e))

    if failed:
        print('%d TEST(S) FAILED' % failed)
        return 1
    print('ALL TESTS PASSED')
    return 0


if __name__ == '__main__':
    sys.exit(main())
