#!/usr/bin/env python3
"""check_strap2_mnemonics.py -- IBM's printed STRAP II operation set against
the host's table of operations (strap/strap2/optable.py), both ways.

THE WITNESSES, each transcribed in the ink 2026-11-15 into tests/:
  c28_6129_appendix_a_ops.txt   C28-6129 App. A pp.44-45, the alphabetic list
                                of operations, with its footnote suffixes
  c28_6129_appendix_c_ops.txt   C28-6129 App. C pp.47-53, every modified form
                                written out
  c28_6129_n28_1081_ops.txt     N28-1081 (Apr 1963): revised App. B and the
                                additions to App. C
  c22_6729_appendix_b_ops.txt   C22-6729 App. B pp.195-196: THE PROGRAM'S OWN
                                list of what it accepts beyond the Reference
                                Manual
  c22_6531_appendix_a_ops.txt   STRAP-1's list (C22-6531 pp.57-58): only a
                                cross-check of the C28-6129 transcription

WHY THIS MATTERS FOR STEP 4a.  The guide (p.22, Boxes 17-22) looks an op up
in "the ordered table of primary operations" by BOPSER; only the branch-on-
indicator family is outside it (MIBA).  MBSPEC (p.93) only swaps keypunch-
confusable characters, so every spelling STRAP II accepts is its own entry.
The 7030 table is generated from the host; this check says which of the
host's names IBM printed, and which printed names the host lacks.

THE BUCKETS.  Every printed name is accepted by the host (in a fitting
context: a VFL mode for a V row, an FP mode for an F row, a secondary on CW
or RD for a secondary) or is in exactly one REFUSED bucket below.  Every name
the host accepts (from a candidate list: the printed names, the host's own
code tables, and its suffix grammar) is printed or is in exactly one EXTRA
bucket.  A name that moves fails the check.  So does a bucket entry that
is no longer true.

MEASURED 2026-11-15: the corpus's 509 lookups (op, mode, secondaries) use
365 names.  Outside the branch-on-indicator family every one is printed,
except the blank null op (C28-6129 p.6) and CBRZ+ CBRZ- CBRZH
(LISTING_WITNESSED).  Five HOST_ORDER spellings were used by two decks
until 2026-11-15: fp_arith_f216b.strap now writes its listing's "*A+",
"*N+", "*NA+" (jb_af1c PDF p.149, read again in the ink: an earlier note
had dropped the trailing "+"), and add_family_signs.strap the printed
written-minus VFL forms "-MG" and "M-MG" (and "-", "M-" for the FP-only
"+N", "M+N"), every word unchanged.

INJECTIONS, re-measured 2026-11-15 after the host took IBM's spellings
(control: nothing fails, before and after; each reverted from a saved
copy and checked with cmp):
  a p.44 row dropped (F KMGR)        -> 1: the C28-6129 vs C22-6531 check
  a footnote misread (V KR 4 -> -)   -> 1: the same
  optable.py drops PRNOR             -> 2: "every printed name the host
                                        refuses is bucketed ['PRNNOR', ...]"
                                        (N28-1081's spelling of it) and the
                                        guide's App. B check
  strap_asm's IBM_SPELLING loses     -> 2: the same two checks, ['NOPRINT']
    NOPRINT
  an App. C row dropped (FP KMGRNA)  -> 1: the row count check
A dropped row that another witness also prints (KMGR is in App. C) is caught
only by the row checks, which is why they are there.

Run: PYTHONDONTWRITEBYTECODE=1 python3 check_strap2_mnemonics.py
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "strap"))
import opcodes as O                 # noqa: E402
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


def host_names():
    """The names the host accepts, out of a candidate list."""
    cand = set(printed)
    for d in (T.PSEUDO, T.FIXED_DATA, O.UNCOND_BRANCH_CODES, O.MISC_CODES,
              O.DIR_INDEX_CODES, O.IMM_INDEX_CODES, O.CB_CODES,
              O.TRANSMIT_CODES, O.BB_CODES, O.IO_OP, A.IO_FUNCTION_OPS,
              A.IO_BASE_OPS, O.VFL_INT_CODES, O.VFL_INT_WRITTEN_MINUS,
              O.FP_CODES, A.CONNECTIVE_ALIASES):
        cand |= set(d)
    with open(os.path.join(HERE, "..", "strap", "strap_asm.py")) as f:
        cand |= set(re.findall(r'"([A-Z+\-*/][A-Z0-9+\-*/]{0,7})"', f.read()))
    for k in list(O.VFL_INT_CODES) + list(O.VFL_INT_WRITTEN_MINUS) + list(O.FP_CODES):
        for s in ("I", "N", "A", "NA", "NI", "MG"):
            cand.add(k + s)
    out = set()
    for c in cand:
        if not c or len(c) > 8 or A.classify_branch_indicator(c) is not None:
            continue
        if look(c) or look(c, "BU") or look(c, "N"):
            out.add(c)
    return out

# ------------------------------------------------------------------ buckets
# Printed, and the host refuses it.


REFUSED = {
    # (Until 2026-11-15 three more buckets were here -- ORDER, the same
    # operation in IBM's spelling where the host wrote another, *A+ CBZR SU
    # SPFLSEOP ...; PSEUDO_SPELLING, NOPRINT PUNSYN PRNNOR; and SIGN_GAP,
    # -A M-MG -MGI M-MGI.  strap_asm's IBM_SPELLING and its sign rules now
    # take them; tests/check_ibm_spellings.py assembles each both ways.)
    # N28-1081 p.12's FP "double negatives".  "-" is already "+" with the
    # one invert-sign bit set (jb_af1c), and no page read says whether STRAP
    # cancels a second N or keeps one: no bits until a listing prints one.
    # -NMG D-NMG M-NMG likewise: -MG is +MG with the invert bit (the host's
    # VFL -MG and +MGN have one skeleton).
    "DOUBLE_NEGATIVE": {"-N", "-NA", "D-N", "D-NA", "E-N", "E-NA", "F-N",
                        "F-NA", "M-N", "M-NA", "-NMG", "D-NMG", "M-NMG"},
    # Printed on N28-1081 p.12 and read as printed, meaning not settled:
    # "LNFI, LWFNI" under Load with Flag Bits (LWFI?), "M+N1, M-N1" under
    # Add One to Memory, and VFL "+MGA" under Add to Magnitude (VFL has no
    # absolute-sign modifier; FP +MGA is accepted).
    "UNREAD": {"LNFI", "M+N1", "M-N1", "+MGA"},
    # No machine code in any witness yet (docs/mcp_tape_manufacture.md's
    # two-witness rule): the I-O function family, and N28-1081's "New
    # Instruction" Store/Load Multiply Register.  Lead for STM: MCP printed
    # p.360's dump table AFLTBL holds "STM" in op-code order.
    "CODE_UNKNOWN": {"BS", "BSFL", "ECC", "ERG", "EVEN", "HD", "KLN", "LD",
                     "NOECC", "ODD", "ODDECC", "ODDNEC", "RLF", "RLN",
                     "RWDUNL", "SP", "TILF", "WEF", "CRDRUN", "CRDRUNSEOP",
                     "BSSEOP", "BSFLSEOP", "ECCSEOP", "ERGSEOP", "EVENSEOP",
                     "HDSEOP", "LDSEOP", "ODDSEOP", "RLFSEOP", "RLNSEOP",
                     "SPSEOP", "WEFSEOP",
                     "STM", "STMA", "STMN", "STMNA", "LMR", "LMRA", "LMRI",
                     "LMRN", "LMRNA", "LMRNI"},
}

# The host accepts it, and no witness prints it.
EXTRA = {
    # The host's order for a form IBM prints in another (ORDER above).
    "HOST_ORDER": {"*+A", "*+N", "*+NA", "*+I", "+MGN", "+MGNA", "D+MGN",
                   "D+MGNA", "M+MGN", "M+MGNA", "E+IA", "E+IN", "E+INA",
                   "SRTN", "SRTNA", "*+NI"},
    # A suffix on a printed name that IBM's lists do print elsewhere: the CB
    # suffixes on CBRZ (p.51 "CBRZ or CBZR"; MCP printed p.360 line 26 prints
    # CBRZH, CBRZ+, CBRZ-).
    "LISTING_WITNESSED": {"CBRZ+", "CBRZ-", "CBRZH"},
    # An immediate form no list allows: CV, DCV (footnote 5: N only), ST and
    # SRD (footnote 5), VFL M+ and M+1 (STRAP II p.44 prints VFL M+ with no
    # footnote; STRAP-1's p.57 gave it 3).
    # VFL N and NI where no list prints them: + and M+ (footnote 3 and
    # none), +MG and M+MG with an N, M+1 (N28-1081 prints "M+N1, M-N1",
    # UNREAD above, not M+1N).
    "OVER_ACCEPTED": {"CVI", "DCVI", "STI", "SRDI", "M+I", "M+1I",
                      "CVNI", "DCVNI", "STNI", "SRDNI", "+NI", "M+NI",
                      "+MGNI", "M+MGNI", "M+1N", "M+1NI"},
}

# ------------------------------------------------------------------- checks

fails = []


def check(ok, what):
    print(("PASS " if ok else "FAIL ") + what)
    if not ok:
        fails.append(what)


# 1. The transcription: STRAP II's list is STRAP-1's with the noted changes.
one = [(t, m, f) for t, m, f, n in ROWS_1]
two = [(t, m, f) for t, m, f, n in ROWS_A]
patched = [(t, m.replace("C+1", "C+I").replace("C-1", "C-I"),
            "-" if (t, m) == ("V", "M+") else f) for t, m, f in one]
check(len(two) == 160 and two == patched,
      "C28-6129 pp.44-45 is C22-6531 pp.57-58 but for C+I, C-I and VFL M+'s footnote")
check(len(ROWS_C) == 254 and len(ROWS_N) == 169 and len(ROWS_G) == 93,
      "the witnesses have 254, 169 and 93 rows")

# 2. Every bucket is disjoint and every bucketed name is printed / not.
allref = [n for s in REFUSED.values() for n in s]
allext = [n for s in EXTRA.values() for n in s]
check(len(allref) == len(set(allref)) and len(allext) == len(set(allext)),
      "no name is in two buckets")
check(all(n in printed for n in allref),
      "every REFUSED name is printed")
check(not any(n in printed for n in allext),
      "no EXTRA name is printed")

# 3. Printed -> host.
refused = {n for n, s in printed.items()
           if not all(accepted(n, k) for k in kinds_of(s))}
unclassified = sorted(refused - set(allref))
stale = sorted(set(allref) - refused)
check(not unclassified, "every printed name the host refuses is bucketed %s" % unclassified)
check(not stale, "every REFUSED name is still refused %s" % stale)

# 4. Host -> printed.
host = host_names()
extra = host - set(printed)
unclassified = sorted(extra - set(allext))
stale = sorted(set(allext) - extra)
check(not unclassified, "every unprinted host name is bucketed %s" % unclassified)
check(not stale, "every EXTRA name is still accepted %s" % stale)

# 5. The guide's own App. B is all accepted bar its buckets: the program's
#    table of operations holds these, so the 7030 table must.
guide = {m for g, m, n in ROWS_G if g != "SECONDARY"}
gmiss = sorted(n for n in guide if n in refused)
check(set(gmiss) <= REFUSED["CODE_UNKNOWN"],
      "the guide's App. B misses only names with no known code (%d)" % len(gmiss))

print()
print("printed %d, host %d, agree %d; refused %d, extra %d" % (
    len(printed), len(host), len(printed) - len(refused), len(refused), len(extra)))
for b, s in REFUSED.items():
    print("  refused %-16s %3d" % (b, len(s)))
for b, s in EXTRA.items():
    print("  extra   %-16s %3d" % (b, len(s)))
if fails:
    print("\n%d FAILED" % len(fails))
    sys.exit(1)
print("\nALL MNEMONIC CHECKS PASSED")
