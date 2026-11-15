#!/usr/bin/env python3
"""Step 4a-ii: every operation-table entry from one primary entry and a rule.

STRAP II's table of primary operations has ONE entry per mnemonic (C22-6729
printed p.22, read in the ink: for an ambiguous op "There is one entry (not
two entries)"), and the table of secondary operations (Fig. 24 p.192) one
per secondary.  So the 7030 op
tables can hold the host's entries only if every (op, mode, secondary)
entry the host makes is its primary entry transformed by a rule that
depends on the mode, the secondary, and nothing about the op but its kind.
This check says the rule exists, writes it down (RULE below, which the
table generator uses), and holds the host to it over the whole printed set:
every name in C28-6129 Apps. A and C, N28-1081 and the guide's App. B that
the host accepts, under every mode and every secondary.

THE RULE.  The primary entry is lookup(op, "BU") for a VFL or connective
op, lookup(op, "N") for a floating-point op, lookup(op) for anything else.
  VFL, connective  the mode's two bits replace the primary's: unsigned
                   0x1000 (BU, DU, and no mode), decimal 0x400 (D, DU);
                   a connective's skeleton ignores the mode (those bits
                   are its connective code: strap_asm.enc_connective);
                   a progressive secondary's code replaces field P
                   (Reference Manual printed p.21)
  floating point   U sets bit 0x200000000000 (unnormalized); NO mode takes
                   the op's default, normalized except the E and E+I
                   families, unnormalized (C22-6729 p.140 Box 5, rule 4) --
                   the one place an op's NAME enters the rule
  I-O              SEOP: 0x800 (the SEOP form of the op)
  CW               CR 0, SCR 0x1000000000, CD 0x2000000000, SCD
                   0x3000000000, CCR 0x4000000000, SCCR 0x5000000000, CDSC
                   0x6000000000, SCDSC 0x7000000000 (strap_asm.CW_SECONDARY)
Length, alignment, kind and fills are the primary's, always.  Any other
secondary has no entry (C22-6729 printed p.22: "+ (BU, 3) (SEOP) and CW
(V + I) -- are illegal"), nor has more than one.

MEASURED 2026-11-15: 5,547 entries (vfl 1801, conn 2155, fp 408, io 210,
data 98, instr 539, pseudo 336) all follow the rule.  Before the secondary
family rule (check_secondary_ops.py) the host made entries for B(CCR),
RD(V+I), +(V+I)(N) and the like, and the rule could not have held.

MEASURED INJECTIONS, in strap2/optable.py (each on a copy, reverted by
cmp; control passes before and after):
    SHF joins the E-family no-mode default    FAIL the rule (SHF, 6 entries)
    a no-mode VFL op defaults to B, not BU    FAIL the rule (201 entries)
    the secondary family guard not called     FAIL the rule ("an entry for
                                              an illegal secondary")
"""
import os
import sys
import io
import contextlib

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "strap"))
sys.path.insert(0, HERE)
import strap_asm as A                       # noqa: E402
from strap2 import optable as T             # noqa: E402
with contextlib.redirect_stdout(io.StringIO()):
    try:
        import check_strap2_mnemonics as CM  # noqa: E402  (the printed set)
    except SystemExit:
        pass

MODE_MASK = {None: 0x1000, "BU": 0x1000, "B": 0, "DU": 0x1400, "D": 0x400}   # unsigned 0x1000, decimal 0x400
P_MASK = 0xE0000000
P_SHIFT = 29
U_BIT = 0x200000000000
CW_MASK = {k: (4 * c + 2 * m + s) << 36 for k, (c, m, s) in A.CW_SECONDARY.items()}
E_FAMILY = ("E+", "E+I")


def fp_family(op):
    sm = A.strip_fp_sign(A.ibm_spelling(op, [])[0])
    return sm[0] if sm else op


def rule(kind, op, primary_sk, mode, secs):
    """The entry's skeleton, or None where no entry may exist (a secondary
    outside the op's family: C22-6729 printed p.22)."""
    sk = primary_sk
    if len(secs) > 1:
        return None
    sec = secs[0] if secs else None
    if kind in ("vfl", "conn"):
        if kind == "vfl":
            sk = (sk & ~0x1400) | MODE_MASK[mode]
        if sec is not None:
            if sec not in A.PROGRESSIVE_SECONDARY_OP:
                return None
            sk = (sk & ~P_MASK) | (A.PROGRESSIVE_SECONDARY_OP[sec] << P_SHIFT)
        return sk
    if kind == "fp":
        if sec is not None:
            return None
        if mode == "U" or (mode is None and fp_family(op) in E_FAMILY):
            sk |= U_BIT
        return sk
    if kind == "io":
        if sec is None:
            return sk
        if sec == "SEOP" and not op.upper().endswith("SEOP") and op.upper() != "CCW":
            return sk | 0x800
        return None
    if sec is None:
        return sk
    if op.upper() == "CW" and sec in CW_MASK:
        return sk | CW_MASK[sec]
    return None


def look(op, mode=None, secs=()):
    try:
        return T.lookup(op, mode, secs)
    except Exception:
        return None


MODES = [None, "N", "U", "B", "BU", "D", "DU"]
SECS = [()] + [(s,) for s in A.PROGRESSIVE_SECONDARY_OP] + [("SEOP",)] + \
       [(s,) for s in A.CW_SECONDARY]

n = 0
bad = []
kinds = {}
for name in sorted(CM.printed):
    for m in MODES:
        for s in SECS:
            e = look(name, m, s)
            if e is None:
                continue
            if e.kind in ("vfl", "conn"):
                p = look(name, "BU")
            elif e.kind == "fp":
                p = look(name, "N")
            else:
                p = look(name)
            n += 1
            kinds[e.kind] = kinds.get(e.kind, 0) + 1
            if p is None or p.kind != e.kind:
                bad.append((name, m, s, "no primary"))
                continue
            want = rule(e.kind, name, p.skeleton, m, s)
            if want is None:
                bad.append((name, m, s, "an entry for an illegal secondary"))
                continue
            same = (e.length, e.align, tuple(e.fills)) == (p.length, p.align, tuple(p.fills))
            if e.skeleton != want or not same:
                bad.append((name, m, s, hex(e.skeleton), hex(want), same))

failures = []


def check(what, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + what + ("" if ok else ": " + detail))
    if not ok:
        failures.append(what)


print(f"entries tested: {n} {dict(sorted(kinds.items()))}")
check("every entry is its primary under the rule", not bad, str(bad[:12]) + f" ... {len(bad)}")
check("the walk is not empty (every kind present)",
      all(kinds.get(k, 0) > 0 for k in ("vfl", "conn", "fp", "io", "data", "instr", "pseudo")),
      str(kinds))
if failures:
    print(f"*** {len(failures)} CHECK(S) FAILED ***")
    sys.exit(1)
print("ALL CHECKS PASSED")
