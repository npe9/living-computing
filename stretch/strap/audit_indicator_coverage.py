#!/usr/bin/env python3
"""audit_indicator_coverage.py -- which indicators does the model write
that no program ever looks at?

WHY THIS EXISTS.  A model that set all five index result indicators
UNCONDITIONALLY TO 1 passed 300+ suite sections, because every check in
every program branched IF THE INDICATOR WAS ON and nothing asked whether
one was correctly OFF.  That hole was found by attacking a green suite,
not by adding coverage.  This script looks for the same shape of hole
across every indicator at once, statically and in a second.

WHAT IT DOES NOT TELL YOU.  It is a REFERENCE audit, not a discrimination
audit: it answers "does any program mention this indicator", never "would
any program notice if it were wrong".  An indicator can be referenced by
twenty programs and still be pinned by none of them -- XF was, until
ibox1_bind.strap.  Treat a hit as "look closer", not as "covered".

THE AUDIT NEEDED THREE CORRECTIONS, which is the useful part of its
history, because each one was a mechanism I did not know programs used:

  1. Branch-on-indicator mnemonics are not the only way to test one.
     ZM came back "never tested" and the plan doc said F214D6 was its
     first test anywhere -- it uses BRANCH ON BIT against word 11
     (BZB, 11.33, $+2.0), the indicator register as ordinary storage.
  2. Indicators are also named by SYMBOL.  NM came back "never tested"
     and F219 turns noisy mode on with BB1, $NM, $+1.0 -- $<IND>
     resolves to word 11, that bit (strap_asm.py, symbol lookup).
  3. Comments mention indicator names constantly, so they have to be
     stripped or half the tape's prose counts as coverage.

Each correction shrank the gap list; the first version's 29 "gaps" were
mostly my own blind spots.  An audit that has not been audited is a
claim, not a measurement.
"""
import re, glob, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from opcodes import INDICATOR_BITS

ROOT     = os.path.dirname(HERE)
PROGRAMS = os.path.join(HERE, 'programs', '*.strap')
BSV      = os.path.join(ROOT, 'bsv', '*.bsv')

BY_BIT = {v: k for k, v in INDICATOR_BITS.items()}
_NAMES = '|'.join(sorted(INDICATOR_BITS, key=len, reverse=True))

RE_MNEM = re.compile(r'\bB(Z?)(' + _NAMES + r')(Z?)\s*,')      # B[Z]<IND>[Z],
RE_SYM  = re.compile(r'\$(' + _NAMES + r')\b')                 # $<IND>
RE_BIT  = re.compile(r'(?:\b11|\$IND)\s*[.+]\s*\.?(\d+)')      # 11.<bit>, $IND+.<bit>
RE_WRITE = r'setBit\([^,]+,\s*ind_%s\s*,'                      # a real model WRITE


def referenced_by_programs():
    """{indicator: {files}} -- every indicator any program names."""
    out = {}
    for f in sorted(glob.glob(PROGRAMS)):
        src = re.sub(r'!.*', '', open(f).read())               # strip comments
        for m in RE_MNEM.finditer(src): out.setdefault(m.group(2), set()).add(f)
        for m in RE_SYM.finditer(src):  out.setdefault(m.group(1), set()).add(f)
        for m in RE_BIT.finditer(src):
            n = BY_BIT.get(int(m.group(1)))
            if n: out.setdefault(n, set()).add(f)
    return out


def written_by_model():
    """{indicator: {files}} -- indicators the model actually assigns.
    StretchTypes.bsv is excluded: defining a name is not writing it."""
    out = {}
    for f in sorted(glob.glob(BSV)):
        if 'Types' in f: continue
        s = open(f).read()
        for n in INDICATOR_BITS:
            if re.search(RE_WRITE % n, s): out.setdefault(n, set()).add(f)
    return out


def value_checked():
    """Indicators compared as part of a whole expected word by a testbench
    generator, e.g. gen_io_tb.py's UNRJ check."""
    out = set()
    for f in glob.glob(os.path.join(HERE, '*.py')):
        out |= set(re.findall(r'_ind\("([A-Z0-9]+)"\)', open(f).read()))
    return out


# The gap as it stands, so this runs as a RATCHET in the suite: a new
# indicator write that no program looks at fails here rather than landing
# silently.  Shrink this set when one gets pinned; grow it only with a
# reason written down.
#
# Currently EMPTY: every indicator the model writes is named by at least
# one program.  OP and AD were the last two and are pinned by
# programs/op_ad_indicators.strap.  Note what that does and does not
# mean -- see the "reference, not discrimination" caveat above.
KNOWN_GAP = set()


def main():
    refd, written, valc = referenced_by_programs(), written_by_model(), value_checked()
    seen = set(refd) | valc
    gap = sorted(set(written) - seen)

    print(f"indicators written by the model : {len(written)}")
    print(f"named by at least one program   : {len(refd)}")
    print(f"value-checked by a generator    : {len(valc - set(refd))} more")
    print()
    if not gap:
        print("No indicator is written by the model and ignored by every program.")
    else:
        print(f"WRITTEN BY THE MODEL, NAMED BY NO PROGRAM ({len(gap)}):")
        for n in gap:
            where = ', '.join(sorted(os.path.basename(f) for f in written[n]))
            print(f"  {n:6} bit {INDICATOR_BITS[n]:>3}   written in {where}")
    print()
    print("Reference, not discrimination: a named indicator may still be")
    print("pinned by nothing.  See this file's header.")

    new_gap  = sorted(set(gap) - KNOWN_GAP)
    now_kept = sorted(KNOWN_GAP - set(gap))
    if new_gap:
        print(f"\nFAIL: newly untested indicator write(s): {', '.join(new_gap)}")
        print("Either pin them with a program or add them to KNOWN_GAP with a reason.")
        return 1
    if now_kept:
        print(f"\nFAIL: {', '.join(now_kept)} is now covered -- remove it from KNOWN_GAP.")
        return 1
    if KNOWN_GAP:
        print(f"\nPASS: gap is exactly the {len(KNOWN_GAP)} known and documented "
              f"({', '.join(sorted(KNOWN_GAP))}).")
    else:
        print(f"\nPASS: every indicator the model writes ({len(written)}) is named "
              f"by at least one program.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
