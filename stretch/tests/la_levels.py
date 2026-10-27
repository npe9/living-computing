#!/usr/bin/env python3
"""Perf. Char. Table A-2 as data: how many look-ahead levels each
instruction occupies.

Transcribed in docs/spec_lookahead.md section 1.7 from rendered PDF
pages 69, 70 and 71, and mapped onto this project's mnemonics in
section 5.  Nothing here is a new reading of the page; the citations
are the section numbers.

WHY IT IS DATA AND NOT A BSV FUNCTION YET: bsv/StretchCore.bsv loads
ONE level per instruction, and Table A-2 says that is the FP case only.
Before changing the ring, this answers how much the change is worth --
statically, over MCP's own transcribed code, with no model run, so the
answer cannot be an artifact of instrumenting the model.
"""
import sys, os, re, glob, collections

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "strap"))
import opcodes as O

NOT_GIVEN = None   # the page does not list this mnemonic

# --- sheet 3, E-box: floating point -------------------------------------
FP = {}
for m in ("+", "L", "LWF", "+MG", "D+", "DL", "DLWF", "D+MG",
          "K", "KMG", "KMGR", "KR", "*", "/", "R/", "F+", "E+"):
    FP[m] = 1                      # op + opnd
FP["E+I"] = 1
FP["SHF"] = 1                      # op + count
for m in ("ST", "SLO", "SRD", "SRT"):
    FP[m] = 1                      # store
for m in ("M+", "M+MG"):
    FP[m] = 2                      # op + opnd / store
FP["*+"] = 2                       # op + opnd / C($FT)
for m in ("LFT", "D/"):
    FP[m] = 2
FP["D*"] = NOT_GIVEN               # sheet 3 lists D+, DL, DLWF, D+MG -- not D*

# --- sheet 3, E-box: VFL integer ---------------------------------------
VFL = {}
for m in ("+", "L", "LWF", "+MG", "K", "KR", "KE", "KF", "KFE", "KFR", "LCV"):
    VFL[m] = 2                     # op / opnd
VFL["*"] = 2                       # binary
for m in ("CV", "DCV"):
    VFL[m] = 2                     # op / INT
for m in ("ST", "SRD", "M+MG", "M+1", "M+"):
    VFL[m] = 3                     # op / opnd / store
VFL["*+"] = 3                      # op / opnd / C($FT)
for m in ("LFT", "LTRS", "LTRCV"):
    VFL[m] = 3
VFL["/"] = NOT_GIVEN               # only "/(dec)" is listed, never binary /

# --- sheet 1, I-box ----------------------------------------------------
DIX = {}
for m in ("LX", "LV", "LC", "LR", "V+", "V+C", "V+CR", "LVE"):
    DIX[m] = 1                     # IX Rec.
for m in ("KV", "KC"):
    DIX[m] = 1                     # NOOP
for m in ("SX", "SV", "SC", "SR", "SVA"):
    DIX[m] = 1                     # store, LAAR needed
DIX["RNX"] = 3                     # test, store, NOOP

IMM = {m: 1 for m in O.IMM_INDEX_CODES}        # all IX Rec. or NOOP

MISC = {"EX": 1, "RCZ": 1, "Z": 1, "R": 1, "EXIC": NOT_GIVEN}  # EXIC is "N stores"

CB = {m: 1 for m in O.CB_CODES}                # IX Rec.

UNCOND = {"B": 2, "BR": 2, "BE": 2, "NOP": 2, "BD": 2, "BEW": 3}

BB = {m: 4 for m in O.BB_CODES}                # OP / opnd / store / B Rec.

XMIT = {m: NOT_GIVEN for m in O.TRANSMIT_CODES}  # 2 + N, and 2 + 2N for SWAP

# --- sheet 3's I/O row -------------------------------------------------
# "I/O | no | op / LAOP | no | no | no | no" plus the sheet's own note,
# "LA communicates with exchange directly".
IO = {m: 2 for m in O.IO_OP}
# GONG and SPFL are CTL with a function code, not separate instructions:
# strap_asm.py line 258, '"SPFL(SEOP),0.0($15)" is "CTL(SEOP),0.0($15),
# <Space File>"'.  Same levels as the CTL they assemble to.
import strap_asm as _sa
for _m in _sa.IO_FUNCTION_OPS:
    IO[_m] = 2

# --- the sign modifier is not a different instruction ------------------
# opcodes.py line 55: '"-" is "+" with the invert-sign modifier'.  So a
# subtract occupies whatever its add occupies, in both unit tables.
for _t in (VFL, FP):
    for _plus, _minus in (("+", "-"), ("+MG", "-MG")):
        if _plus in _t:
            _t[_minus] = _t[_plus]

# --- VFL IMMEDIATES: the page is silent, and the one data point does not
# --- transfer ----------------------------------------------------------
# Sheet 3 lists no immediate VFL row.  The tempting inference is that an
# immediate needs no operand FETCH so it cannot need an operand LEVEL,
# i.e. base - 1.  THE ONE IMMEDIATE THE PAGE DOES GIVE ARGUES THE OTHER
# WAY: FP E+- is 1 level and FP E+-I is also 1.  But FP's single level is
# "op + opnd" TOGETHER, so there was never a separate level to remove,
# and the argument cannot be carried to VFL, whose op and opnd are two
# levels.  So these are NOT GIVEN, not guessed.
_VFL_IMM_STEMS = set(VFL) | {"LF", "SF"}
VFL_IMM = {}
for _m in ("KFI", "LFI", "LI", "/I", "*I", "+I", "-I", "KI", "KRI",
           "STI", "SRDI", "CVI", "LCVI"):
    if _m[:-1] in _VFL_IMM_STEMS:
        VFL_IMM[_m] = NOT_GIVEN

# Branch on indicator: 1 level for an INDEX condition, 4 for any other.
# The index conditions are sheet 2's own list.
INDEX_CONDITIONS = {"XF", "XCZ", "XVLZ", "XVZ", "XVGZ", "XL", "XE", "XH"}

TABLES = [("fp", FP), ("vfl", VFL), ("dix", DIX), ("imm", IMM),
          ("misc", MISC), ("cb", CB), ("uncond", UNCOND), ("bb", BB),
          ("xmit", XMIT), ("io", IO), ("vflimm", VFL_IMM)]

# --- sheet 3's connective rows -----------------------------------------
# "C, CT" sit in the 2-level op/opnd row and "CM" in the 3-level
# op/opnd/store row.  A connective mnemonic is one of the three suffixes
# followed by the four connective bits -- CM0000, CT0011 -- and
# strap_asm.CONNECTIVE_ALIASES adds two more spellings of the same
# instructions: LF is C0011 and SF is CM0101 (strap_asm.py:1232-1233).
CONN_LEVELS = {"C": 2, "CT": 2, "CM": 3}
_CONN_RE = re.compile(r"^(CM|CT|C)([01]{4})$")

# --- sheet 2's branch-on-indicator split -------------------------------
# An INDEX condition takes one noop level; any other indicator takes four
# (OP / INT / INT.stores / B Rec.).  The mnemonic is B or BZ, then an
# indicator name from opcodes.INDICATOR_BITS, then an optional trailing Z
# meaning "and clear".
_BIND_RE = re.compile(r"^B(Z?)([A-Z0-9]+?)(Z?)$")


def _connective(mnemonic):
    import strap_asm
    if mnemonic in strap_asm.CONNECTIVE_ALIASES:
        return CONN_LEVELS[strap_asm.CONNECTIVE_ALIASES[mnemonic][0]]
    m = _CONN_RE.match(mnemonic)
    return CONN_LEVELS[m.group(1)] if m else None


def _branch_on_indicator(mnemonic):
    """Levels for a B<ind>/BZ<ind> mnemonic, or None if the name does not
    resolve to an indicator.  Longest match wins so XVGZ beats XV."""
    m = _BIND_RE.match(mnemonic)
    if not m:
        return None
    body = m.group(2) + m.group(3)
    for cand in sorted(O.INDICATOR_BITS, key=len, reverse=True):
        if body == cand or (body == cand + "Z"):
            return 1 if cand in INDEX_CONDITIONS else 4
    return None


def vfl_levels(base, crosses=False, progressive=False):
    """Sheet 3's note: a VFL operand crossing a full-word boundary
    DOUBLES the opnd and store levels, and progressive indexing adds
    one IX level.  An op level is never doubled, so of a base of n the
    doubled part is n - 1."""
    if base is NOT_GIVEN:
        return NOT_GIVEN
    return base + ((base - 1) if crosses else 0) + (1 if progressive else 0)


def lookup(mnemonic):
    """(kind, levels) for a bare mnemonic.

    kind is a table name, "conn", "bind", "not-given" when Table A-2
    lists no count for an instruction the assembler accepts, or None when
    this module simply failed to recognise the mnemonic.  THE TWO ARE
    KEPT APART deliberately: "the page is silent" is a fact about the
    source and "I did not match it" is a fact about this file."""
    for name, t in TABLES:
        if mnemonic in t:
            return ("not-given" if t[mnemonic] is NOT_GIVEN else name), t[mnemonic]
    n = _connective(mnemonic)
    if n is not None:
        return "conn", n
    n = _branch_on_indicator(mnemonic)
    if n is not None:
        return "bind", n
    return None, None


# ---------------------------------------------------------------------------
# The statement scanner, for a census over the transcribed decks
# ---------------------------------------------------------------------------
PSEUDO = {"DD", "DR", "DRZ", "VF", "CF", "RF", "XW", "CW", "END", "SYN",
          "SLC", "CNOP", "DDI", "EXT", "SIC", "TAIL", "UNTAIL",
          "PRNS"}


def opcode_of(line):
    """The bare mnemonic on one STRAP source line, or None.

    A label starts in column 1, so an indented line's first token is the
    operation.  Modifiers in parentheses and the operand comma are
    stripped; "SIC" is a prefix to the NEXT statement and carries no
    level of its own here.
    """
    line = line.split("!", 1)[0].rstrip()
    if not line.strip():
        return None
    toks = line.split()
    op = toks[0] if line[0] in " \t" else (toks[1] if len(toks) > 1 else None)
    if op is None:
        return None
    if op.startswith(","):
        return None            # an operand continuation line, not an opcode
    op = op.split("(", 1)[0].rstrip(",")
    return op or None


def census(paths):
    """(levels, unmatched, not-given, total) as Counters plus an int."""
    levels, unmatched, total = collections.Counter(), collections.Counter(), 0
    notgiven = collections.Counter()
    for p in paths:
        with open(p) as f:
            for line in f:
                op = opcode_of(line)
                if op is None or op in PSEUDO:
                    continue
                total += 1
                kind, n = lookup(op)
                if kind == "not-given":
                    notgiven[op] += 1
                elif n is None:
                    unmatched[op] += 1
                else:
                    levels[n] += 1
    return levels, unmatched, notgiven, total


def main():
    fails = 0

    def check(label, got, want):
        nonlocal fails
        if got == want:
            print(f"PASS {label} = {got}")
        else:
            print(f"FAIL {label} = {got}, expected {want}")
            fails += 1

    # 1. BUCHHOLZ'S WORST CASE, derived two ways.  PDF 271 says a VFL ADD
    #    TO MEMORY with progressive indexing "may require six successive
    #    levels"; sheet 3's base of 3 plus its own doubling-and-+1 note
    #    gives 3 + 2 + 1.  Neither number was taken from the other.
    check("buchholz_worst_case_is_six",
          vfl_levels(VFL["M+"], crosses=True, progressive=True), 6)
    check("vfl_add_to_memory_base", VFL["M+"], 3)
    check("vfl_plain_add_base", VFL["+"], 2)
    check("fp_plain_add_base", FP["+"], 1)
    # the op level is never doubled, so a 2-level VFL op crossing a word
    # boundary takes 3, not 4
    check("crossing_doubles_only_the_operand_levels",
          vfl_levels(VFL["+"], crosses=True), 3)
    check("progressive_indexing_adds_exactly_one",
          vfl_levels(VFL["+"], progressive=True), 3)

    # 2. COVERAGE: every mnemonic the assembler knows must be mapped or
    #    explicitly marked NOT_GIVEN.  A census that silently skips what
    #    it cannot match is the failure mode this project has a memory
    #    note about, so the gap is an assertion, not a shrug.
    for fam, table in (("VFL_INT_CODES", VFL), ("FP_CODES", FP),
                       ("DIR_INDEX_CODES", DIX), ("IMM_INDEX_CODES", IMM),
                       ("MISC_CODES", MISC), ("CB_CODES", CB),
                       ("UNCOND_BRANCH_CODES", UNCOND), ("BB_CODES", BB),
                       ("TRANSMIT_CODES", XMIT), ("IO_OP", IO)):
        missing = sorted(set(getattr(O, fam)) - set(table))
        check(f"coverage_{fam}", missing, [])

    # 3. THE GAPS, named so they cannot be forgotten.  Each is a mnemonic
    #    the assembler accepts and Table A-2 does not list.
    check("not_given_is_exactly_these",
          sorted(m for _, t in TABLES for m, v in t.items() if v is NOT_GIVEN),
          sorted(["D*", "/", "EXIC"] + list(O.TRANSMIT_CODES)
                 + list(VFL_IMM)))

    decks = sorted(glob.glob(os.path.join(HERE, "..", "decks",
                                          "mcp_bootstrap_p*.strap")))
    check("mcp_decks_found", len(decks) > 50, True)
    levels, unmatched, notgiven, total = census(decks)
    print(f"\n--- MCP level-occupancy census: {total} statements in "
          f"{len(decks)} decks ---")
    mapped = sum(levels.values())
    for n in sorted(levels):
        print(f"  {n} level(s): {levels[n]:5d}")
    print(f"  page silent: {sum(notgiven.values()):5d} "
          f"({len(notgiven)} distinct) -- Table A-2 gives no count")
    print(f"  unmatched : {sum(unmatched.values()):5d} "
          f"({len(unmatched)} distinct)")
    if mapped:
        weighted = sum(n * c for n, c in levels.items())
        print(f"  mapped statements {mapped}, levels {weighted}, "
              f"mean {weighted / mapped:.2f} levels per instruction")
        print(f"  >>> the model loads ONE level each, so it is short by "
              f"{weighted - mapped} levels over these decks <<<")
    print("  most common unmatched: "
          + ", ".join(f"{m}x{c}" for m, c in unmatched.most_common(12)))

    # >>> AND THE CENSUS IS AN ASSERTION, NOT A REPORT. <<<  A mnemonic
    # this file cannot place is a hole in the mapping, and a census that
    # silently skips what it cannot match is the exact failure
    # docs/NEXT.md and the session memory both record -- a SYN census
    # once counted "SYN(" and so could not match the bare SYN cards it
    # was hunting.  So: a new instruction in a deck fails HERE.
    check("census_leaves_nothing_unmatched", sum(unmatched.values()), 0)
    # The page-silent set is allowed but FIXED: if it grows, a deck has
    # started using an instruction Table A-2 does not cost, and that is
    # a thing to know before M2 relies on the table.
    check("page_silent_mnemonics_in_mcp",
          sorted(notgiven),
          ["/I", "KFI", "LFI", "LI", "SWAPI", "T", "TB", "TI"])

    if fails:
        print(f"\n{fails} TEST(S) FAILED")
        return 1
    print("\nALL TESTS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
