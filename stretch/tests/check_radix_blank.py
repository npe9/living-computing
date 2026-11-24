#!/usr/bin/env python3
r"""A blank between a radix specifier and its number: "(2) 10".

C22-6578 printed p.21 (PDF 22), Problem 2.9, prints

    TEST    KFI(BU, 2), (2) 10,4        'test if floating-point

and the same page, Problem 2.8 comment (d): "Normally the STRAP
assembler ignores all blanks in instructions and pseudo-instructions."

../decks/repro_radix_blank.strap holds the statement twice, NOB without
the blank and WITHB with it.

THE RULE.  C22-6729 printed p.20 (PDF 20), Chart MAIN Box 5, read in
the ink 2026-11-23: "GETCHA does not give blanks to main flow unless
main flow has turned on the indicator, Gcaz."  Gcaz is turned on only
for an alphabetic DD's datum (printed p.102, MQDALF) and the ID field
(MPUNID), so a blank anywhere else in a statement field is not seen at
all, and "(2) 10" is "(2)10".

CHECKS
  strap2_withb_equals_nob   the host STRAP II (strap/strap2) assembles
                            both, to the same word.
  strap_asm_withb_equals_nob
                            strap_asm assembles WITHB to NOB's word.
                            (Until 2026-11-23 this check PINNED the
                            refusal, "cannot parse expression '(2) 10'".)
  strap_asm_nob_assembles   NOB's word is STRAP II's.
  inner_blanks_strap_asm / inner_blanks_strap2
                            "( 8 ) 17" in a KFI, blanks inside the
                            parentheses too, gives "(8)17"'s word under
                            each assembler.

MEASURED (2026-11-15): 3 of 3 before the fix, with the pin.
MEASURED (2026-11-23, after the fix): 5 of 5.

INJECTION (2026-11-23, tests/inject.py): _TERM_RADIX restored to its
old pattern r'\((\d+)\)(?=[\dA-F.])' (no blank allowed) makes
strap_asm_withb_equals_nob and inner_blanks_strap_asm FAIL; the other
three PASS.  The file was restored from its copy and cmp'd.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'strap'))
sys.path.insert(0, HERE)

from strap_asm import assemble, AssemblerError   # noqa: E402
import gen_tb                                    # noqa: E402

DECK = os.path.join(HERE, '..', 'decks', 'repro_radix_blank.strap')
BLANK = 'KFI(BU, 2), (2) 10,4'


def main():
    src = open(DECK).read()
    assert src.count('\nWITHB   ' + BLANK) == 1, 'the deck no longer holds the printed statement'
    failed = 0

    def check(name, ok, detail=''):
        nonlocal failed
        print('%s %s%s' % ('PASS' if ok else 'FAIL', name, (' -- ' + detail) if detail else ''))
        failed += 0 if ok else 1

    p2 = gen_tb.strap2_program(src)
    nob, withb = p2.words.get(1001), p2.words.get(1002)
    check('strap2_withb_equals_nob', nob is not None and nob == withb,
          'NOB %016x WITHB %016x' % (nob or 0, withb or 0))

    try:
        p1 = assemble(src)
        check('strap_asm_withb_equals_nob',
              p1.words.get(1002) is not None and p1.words.get(1002) == p1.words.get(1001),
              'NOB %016x WITHB %016x' % (p1.words.get(1001) or 0, p1.words.get(1002) or 0))
    except AssemblerError as e:
        check('strap_asm_withb_equals_nob', False, str(e))

    without = '\n'.join(l for l in src.split('\n') if not l.startswith('WITHB'))
    try:
        p1 = assemble(without)
        check('strap_asm_nob_assembles', p1.words.get(1001) == nob,
              'strap_asm %016x' % (p1.words.get(1001) or 0))
    except AssemblerError as e:
        check('strap_asm_nob_assembles', False, str(e))

    inner = ('        SLC, 1000.0\nSTART   BEW, $\n        CNOP\n'
             'A       KFI(BU,8),( 8 ) 17\nB       KFI(BU,8),(8)17\n        END, START\n')
    for name, asm in (('strap_asm', assemble), ('strap2', gen_tb.strap2_program)):
        try:
            p = asm(inner)
            a, b = p.words.get(1001), p.words.get(1002)
            check('inner_blanks_' + name, a is not None and a == b,
                  '( 8 ) 17 %016x  (8)17 %016x' % (a or 0, b or 0))
        except AssemblerError as e:
            check('inner_blanks_' + name, False, str(e))

    if failed:
        print('%d TEST(S) FAILED' % failed)
        return 1
    print('ALL TESTS PASSED')
    return 0


if __name__ == '__main__':
    sys.exit(main())
