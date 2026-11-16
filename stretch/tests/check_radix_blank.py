#!/usr/bin/env python3
"""A blank between a radix specifier and its number: "(2) 10".

C22-6578 printed p.21 (PDF 22), Problem 2.9, prints

    TEST    KFI(BU, 2), (2) 10,4        'test if floating-point

and the same page, Problem 2.8 comment (d): "Normally the STRAP
assembler ignores all blanks in instructions and pseudo-instructions."

../decks/repro_radix_blank.strap holds the statement twice, NOB without
the blank and WITHB with it.

CHECKS
  strap2_withb_equals_nob   the host STRAP II (strap/strap2) assembles
                            both, to the same word.
  strap_asm_PINNED_refuses_the_blank
                            strap_asm raises AssemblerError on WITHB.
                            THIS PINS A DEFECT (found 2026-11-15, see
                            docs/NEXT.md).  When strap_asm is fixed this
                            check FAILS, on purpose: change it then to
                            "strap_asm assembles WITHB to NOB's word",
                            do not delete it.
  strap_asm_nob_assembles   with WITHB's line removed strap_asm
                            assembles, and NOB's word is STRAP II's.

MEASURED (2026-11-15): 3 of 3.  The blank removed from WITHB in a copy
of the deck: strap_asm_PINNED_refuses_the_blank FAILS (strap_asm then
assembles it) and the other two pass -- the pin is on the blank and
nothing else.  Run with --inject to repeat that.
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
    if '--inject' in sys.argv[1:]:
        src = src.replace('\nWITHB   ' + BLANK, '\nWITHB   KFI(BU, 2), (2)10,4')
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
        assemble(src)
        refused, msg = False, 'strap_asm assembled it'
    except AssemblerError as e:
        refused, msg = "'(2) 10'" in str(e), str(e)
    check('strap_asm_PINNED_refuses_the_blank', refused, msg)

    without = '\n'.join(l for l in src.split('\n') if not l.startswith('WITHB'))
    try:
        p1 = assemble(without)
        check('strap_asm_nob_assembles', p1.words.get(1001) == nob,
              'strap_asm %016x' % (p1.words.get(1001) or 0))
    except AssemblerError as e:
        check('strap_asm_nob_assembles', False, str(e))

    if failed:
        print('%d TEST(S) FAILED' % failed)
        return 1
    print('ALL TESTS PASSED')
    return 0


if __name__ == '__main__':
    sys.exit(main())
