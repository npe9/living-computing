"""printed_ops.py -- IBM's printed STRAP II operation set, read from the
transcriptions in tests/ (each read in the ink 2026-11-15; their headers say
from where).  Imported by check_strap2_mnemonics.py, which compares it with
the host's table both ways, and by the 7030 op-table generator and its check,
whose membership it is (optab_names).

  c28_6129_appendix_a_ops.txt   C28-6129 App. A pp.44-45 with its footnotes
  c28_6129_appendix_c_ops.txt   C28-6129 App. C pp.47-53, the modified forms
  c28_6129_n28_1081_ops.txt     N28-1081 (Apr 1963): App. B and App. C additions
  c22_6729_appendix_b_ops.txt   C22-6729 App. B pp.195-196, the program's own list
  c22_6531_appendix_a_ops.txt   STRAP-1's list, a cross-check only
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "strap"))
import strap_asm as A               # noqa: E402
from strap2 import optable as T     # noqa: E402

# ---------------------------------------------------------------- witnesses


def rows(name):
    with open(os.path.join(HERE, name)) as f:
        return [l.split("\t") for l in f.read().splitlines()
                if l and not l.startswith("#")]


def four(x):
    return [x.replace("####", format(v, "04b")) for v in range(16)] if "####" in x else [x]


# Appendix A footnotes (p.45): the suffixes each one licenses.
SUFFIX = {"3": ["I"], "4": ["I", "N", "NI"], "5": ["N"], "6": ["A"],
          "7": ["N", "A", "NA"], "8": ["+", "-", "H"]}
VFLISH = ("V", "VFL", "ADDVFL", "CONN")
FPISH = ("F", "FP", "ADDFP")

printed = {}        # name -> set of "source:group"


def add(name, src):
    for n in four(name):
        printed.setdefault(n, set()).add(src)


ROWS_A = rows("c28_6129_appendix_a_ops.txt")
ROWS_C = rows("c28_6129_appendix_c_ops.txt")
ROWS_N = rows("c28_6129_n28_1081_ops.txt")
ROWS_G = rows("c22_6729_appendix_b_ops.txt")
ROWS_1 = rows("c22_6531_appendix_a_ops.txt")

for t, m, f, n in ROWS_A:
    if f == "10":                       # C, CM, CT: a family, not an op
        add(m + "####", "A:" + t)
        add(m + "####I", "A:" + t)
        continue
    add(m, "A:" + t)
    for s in SUFFIX.get(f, []):
        add(m + s, "A" + f + ":" + t)
for sec, m, imm, page in ROWS_C:
    add(m, "C:" + sec)
    if imm == "I":
        add(m + "I", "CI:" + sec)
for g, m, n in ROWS_N:
    # "CRDRUN (SEOP)" and "REW (SEOP)": the op, written with SEOP allowed.
    if m.endswith(" (SEOP)"):
        b = m[:-len(" (SEOP)")]
        add(b, "N:" + g)
        add(b + "SEOP", "N:" + g)
        continue
    add(m, "N:" + g)
for g, m, n in ROWS_G:
    add(m, "G:" + g)


def kinds_of(srcs):
    """The types a name is printed as: V (VFL or connective), F (floating
    point), S (secondary), or - (anything else).  A name printed both ways
    (L, +, *, ...) must be accepted both ways."""
    out = set()
    for s in srcs:
        g = s.split(":")[1]
        out.add("V" if g in VFLISH else "F" if g in FPISH else
                "S" if g == "SECONDARY" else "-")
    return out


def look(op, mode=None, sec=()):
    try:
        return T.lookup(op, mode, sec)
    except Exception:
        return None


def accepted(name, kind):
    if name == "SEOP":
        return look("RD", None, ("SEOP",)) is not None
    if kind == "S":
        return any(look(p, None, (name,)) for p in ("CW", "RD", "W"))
    if kind == "V":
        e = look(name, "BU")
        return e is not None and e.kind in ("vfl", "conn")
    if kind == "F":
        e = look(name, "N")
        return e is not None and e.kind == "fp"
    return look(name) is not None



# Spelled in a listing, not in a list: MCP printed p.360 prints CBRZH,
# CBRZ+ and CBRZ- (App. C p.51 prints only CBRZ and CBZR).
LISTING_WITNESSED = {"CBRZ+", "CBRZ-", "CBRZH"}


def optab_names():
    """The 7030 table of primary operations' membership: every printed name
    (other than a secondary) the host accepts, and the listing-witnessed
    ones, without the branch-on-indicator family (C22-6729 p.22: MIBA
    supplies it, "not in the op table").  No host-order spelling (*+A, +MGN)
    and no form no list prints is in it.  And the null op, eight blanks:
    C22-6729 printed p.21, Box 8, read in the ink 2026-11-15: "since the
    buffer was blanked out in the initialization, Bopx is already set up
    for the look-up of the null op in the primary op table" (Chart AA
    p.14, Box 8 to Box 17)."""
    out = set()
    for n, s in printed.items():
        if kinds_of(s) - {"S"} and A.classify_branch_indicator(n) is None and look(n):
            out.add(n)
    return out | LISTING_WITNESSED | {""}
