#!/usr/bin/env python3
r"""A name written with blanks, with something after it: "K REPET.32".

THE RULE.  C22-6729 printed p.20 (PDF 20), Chart MAIN Box 5, read in the
ink 2026-11-23: "GETCHA does not give blanks to main flow unless main
flow has turned on the indicator, Gcaz."  The guide turns Gcaz on for an
alphabetic DD's datum (printed pp.26, 102) and the ID field (p.27),
never for an address field, so the field scanner never sees a blank in
one: "K REPET.32" is "KREPET.32", "S T LR + 0.57" is "STLR+0.57".

strap_asm closed a blanked name up only when it was the WHOLE field
(_BLANKED_SYMBOL); with anything after it, "CB,2,K REPET.32" was
refused, "undefined symbol 'K'" (docs/NEXT.md, "A BLANKED NAME BREAKS
THE MOMENT ANYTHING FOLLOWS IT"), and the MCP decks wrote the names
closed up.  Since 2026-11-23 tokenize_expr reads a name on across blanks
(_symbol_across_blanks), and the decks carry the printed spellings.

CHECKS
  Six PRINTED ROWS, each a mini deck at the row's own location with the
  symbols SYNned to their printed addresses, checked by
  strap/listing_oracle.py against the machine code the MCP listing
  prints (the decks' own !CHECK rows):
    p138_l25   CM0000(BU,1), S CNS SG+1.0($1),0     000001.57 81 001000.00 F0
    p169_l11   BZB, S T LR + 0.57, C CHEKT          215230.71 80 220406.34 00
    p177_l11   SVA,2,K IOD RN-.32                   220706.05 D0
    p177_l13   SWAPI,2,$2,S TLR+15.                 000022.00 80 215247.04 E0
    p187_l11   L(BU,6),K WS.19                      221367.23 80 006000.20 50
    p188_l30   CB,2,K REPET.32                      221376.44 48
  Three behaviours with no printed row:
    inherit_dds   "L,K WS.19" with no dds of its own takes K WS's (BU,6),
                  as "L,KWS.19" does (C22-6531 printed p.11: an
                  expression takes its final symbol's dds) -- the
                  silent length-0 failure p.164 once had
    forward       a blanked name defined AFTER its use ("B,FWD Q+1.0")
    two_names     "B, A B" with A and B defined and AB not is REFUSED
                  (undefined AB); it was summed, A+B, silently.

MEASURED 2026-11-23 before the fix (the saved strap_asm.py):
  every printed row FAILS (each refused, "undefined symbol"),
  inherit_dds and forward FAIL (refused), two_names FAILS (assembled
  A+B).  After: 9 of 9.

INJECTION (2026-11-23): _symbol_across_blanks made to stop at the first
blank ("while True:" -> "while False:") -- all 9 FAIL, the same set and
messages as before the fix; verify_mcp_page.py refuses all 14 decks that
now carry the printed spellings (pp.138, 164, 166, 169, 171, 177, 178,
186, 187, 188, 189, 190, 195, 335), each with "undefined symbol" at the
restored line.  The file was restored from its saved copy and cmp'd.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'strap'))

from strap_asm import assemble, AssemblerError   # noqa: E402
import listing_oracle                            # noqa: E402

# (name, location, SYNs, printed statement, printed code)
PRINTED = [
    ('p138_l25', '217074.00', ['SCNSSG  SYN(BU,1), 0.47'],
     'CM0000(BU,1), S CNS SG+1.0($1),0', '000001.57 81 001000.00 F0'),
    ('p169_l11', '220403.00', ['STLR    SYN, (8)215230.0', 'CCHEKT  SYN, (8)220406.0'],
     'BZB, S T LR + 0.57, C CHEKT', '215230.71 80 220406.34 00'),
    ('p177_l11', '220703.40', ['KIODRN  SYN, (8)220706.40'],
     'SVA,2,K IOD RN-.32', '220706.05 D0'),
    ('p177_l13', '220704.40', ['STLR    SYN, (8)215230.0'],
     'SWAPI,2,$2,S TLR+15.', '000022.00 80 215247.04 E0'),
    ('p187_l11', '221353.40', ['KWS     SYN, (8)221367.0'],
     'L(BU,6),K WS.19', '221367.23 80 006000.20 50'),
    ('p188_l30', '221404.00', ['KREPET  SYN, (8)221376.0'],
     'CB,2,K REPET.32', '221376.44 48'),
]


def deck(loc, syns, stmt, after=()):
    return ''.join('%s\n' % s for s in syns) + \
        '        SLC, (8)%s\nT       %s\n' % (loc, stmt) + \
        ''.join('%s\n' % s for s in after) + '        END, T\n'


def word(src, at_bits):
    return listing_oracle.word_at(assemble(src), at_bits)


def main():
    failed = 0

    def check(name, ok, detail=''):
        nonlocal failed
        print('%s %s%s' % ('PASS' if ok else 'FAIL', name, (' -- ' + detail) if detail else ''))
        failed += 0 if ok else 1

    for name, loc, syns, stmt, printed in PRINTED:
        try:
            prog = assemble(deck(loc, syns, stmt))
            want = listing_oracle.norm(printed)
            got = listing_oracle.render(prog, loc, want)
            check(name, got == want, '%s: assembled %r, listing %r' % (stmt, got, want))
        except AssemblerError as e:
            check(name, False, '%s: %s' % (stmt, e))

    at = listing_oracle.loc_bits('1000.00')
    syn = ['KWS     SYN(BU,6), 11.0']
    try:
        a = word(deck('1000.00', syn, 'L,K WS.19'), at)
        b = word(deck('1000.00', syn, 'L,KWS.19'), at)
        c = word(deck('1000.00', syn, 'L(BU,6),KWS.19'), at)
        check('inherit_dds', a == b == c, 'L,K WS.19 %016x  L,KWS.19 %016x  L(BU,6),KWS.19 %016x'
              % (a, b, c))
    except AssemblerError as e:
        check('inherit_dds', False, str(e))

    try:
        a = word(deck('1000.00', [], 'B,FWD Q+1.0', after=['FWDQ    SYN, 12.0']), at)
        b = word(deck('1000.00', [], 'B,FWDQ+1.0', after=['FWDQ    SYN, 12.0']), at)
        check('forward', a == b, 'B,FWD Q+1.0 %016x  B,FWDQ+1.0 %016x' % (a, b))
    except AssemblerError as e:
        check('forward', False, str(e))

    try:
        a = word(deck('1000.00', ['A       SYN, 3.0', 'B       SYN, 5.0'], 'B, A B'), at)
        check('two_names', False, '"B, A B" assembled to %016x' % a)
    except AssemblerError as e:
        check('two_names', "'AB'" in str(e), str(e))

    if failed:
        print('%d TEST(S) FAILED' % failed)
        return 1
    print('ALL TESTS PASSED')
    return 0


if __name__ == '__main__':
    sys.exit(main())
