#!/usr/bin/env python3
"""check_atlas_data.py -- the fast self-check of the atlas transcription
(tests/perf_char_vol2_atlas.txt).  Registered in run_tests.sh; runs in well
under a second and needs no simulator.  The slow thing -- running the cases
on the model -- is tests/atlas_oracle.py and is NOT registered.

WHAT IT CHECKS

 1. The file parses (atlas_data.load_atlas): every cell is a printed time,
    a stated blank, an indicator mark or a flagged smudge; no page, block or
    row appears twice; printed page = PDF page - 7.

 2. COVERAGE is total and consistent: every PDF page 37-189 has exactly one
    KIND line, and a page is "transcribed" there if and only if it has a
    sheet.

 3. Every uncertain cell ("?") sits on a page whose NOTE explains it.

 4. REDUNDANCY, the part that tests the READING.  The atlas repeats itself,
    and each repetition is a pair of cells the page prints twice:

      invert   VFL: the INVERT SIGN OF INSTRUCTION block against the block
               above it, same row and column
      ibox     VFL: I-BOX OPERAND against EXTERNL OPERAND, same row
      neg      FP: a NEG row against the row above it with the same
               modifiers, same block and column
      ibox     FP: I-BOX OPERAND against EXTERNAL OPERAND
      fwd      FP: a page with forwarding (PDF 73-101) against the page
               31 earlier without it, same instruction, block, row and
               column (EXTERNAL and I-BOX; INTERNAL is blank without)
      vfwd     VFL: a page with forwarding (PDF 143-169) against the page
               27 earlier without it, same instruction, block, row and
               column: EXTERNL OPERAND, EXTERNL WB XOVR, ACCUM. OPERAND
      vfwdib   the same pairing on the I-BOX OPERAND column, kept apart
               because PDF 114 says of it "there should be no difference in
               times between no forwarding vs. forwarding"
      index    VFL forwarding and immediate pages: an INTERNL or IMMED.
               column under NO INDEXING against the same under INDEXING
      immf     VFL immediate (PDF 171-189): IMMED. OPERAND against the same
               instruction's EXTERNL OPERAND with forwarding (an OBSERVED
               relation; the volume does not state one -- see IMM_BASE)
      immn     the same against the page without forwarding
      quotefp  PDF 104's FP subject rows (ST(U) ... LFT(U)) against the
               instruction's no-forwarding sheet; see QUOTED_FP
      noncon   BRANCH: a NONCON column against its CONSEC twin
      quoted   PDF 104's row captions quote the instruction's own figure
               ("5.73 IN A LX ENVIRONMENT"); the index-arithmetic ones are
               compared with PDF 109, a different page printing the same
               number
      rows     IBOX: rows the page prints identically (LV/LC/LR, SV/SC/SR,
               the 18/19/24-bit rows, ...), named in ROW_TWINS below

    A pair is EXACT, NEAR (one unit in the last place, which PDF 39 says
    any figure may be off by) or FAR.  The pairs are NOT required to agree:
    many differ for real (M+ with its sign inverted is a different
    operation).  What is required is that the three counts equal the TALLY
    line recorded on the page when it was transcribed.  At that time the FAR
    pairs were reviewed as grouped lists (--tally prints them) and any that
    broke its page's pattern -- a lone differing cell in a column of equal
    ones -- was re-read on a full-resolution crop; the pages' NOTEs name
    those cells.  A mis-keyed digit moves a count; so does a later
    corruption of the file.

 5. SECOND READING.  PDF 106, 109, 112, 117 and 140 were transcribed once
    before, into tests/perf_char_timing.py, from 300-500 dpi renders.  This
    transcription was made from the images without those tables open.  Every
    cell the two share is compared; a disagreement fails unless it is
    adjudicated in ADJUDICATED below with what the ink shows.

 6. SUM: each page's count and total of numeric cells equals its SUM line.
    This one guards the FILE only -- it reaches every record, including the
    ones no redundancy reaches, but says nothing about the reading.

REACH IS REPORTED, NOT ASSUMED: the last line says how many records no
reading check (4, 5) touches.  A wrong digit in one of those passes
everything here except, after the fact, SUM.

MEASURED INJECTIONS, 2026-11-15.  Each was made to the data file with a
saved copy beside it, the check run, the copy restored and `cmp` clean.
The failure sets are the OBSERVED ones.

 * A record two redundancy rules reach -- PDF 120 (L), first block,
   (BU,32,8) EXTERNL OPERAND 6.00 -> 6.60: three failures and nothing else:
   'ibox' counts (77, 0, 19) against TALLY (78, 0, 18); 'invert' counts
   (133, 2, 1) against (134, 2, 0); PDF 120's SUM.
 * A record the second reading and a cross-page quotation reach -- PDF 109
   LX EXTERNAL DIRECT 5.73 -> 5.13: three failures: PDF 104's 'quoted'
   counts (30, 6, 2) against (32, 6, 0); the second reading names the cell
   ("is 5.13 here and 5.73 in perf_char_timing.py"); PDF 109's SUM.
 * A record NO reading check reaches -- PDF 107 100WD 312.88 -> 312.68: ONE
   failure, PDF 107's SUM, and that only because the SUM line was written
   after the reading.  Had 312.68 been the original mis-reading, nothing
   here would know.  That is what the REACH line counts.

MEASURED INJECTIONS, 2026-11-16, on the floating-point pages (PDF 42-101).
Each was made to a COPY of the file and the check run with --file=; the
original was never written and `cmp` against HEAD was clean after.

 * A record three rules reach -- PDF 88 (*+), NORMALIZED 1., (U) ni_ext
   6.60 -> 6.90: four failures: 'fwd' (127, 0, 1) against (128, 0, 0);
   'ibox' (63, 0, 1) against (64, 0, 0); 'neg' (87, 0, 9) against
   (88, 0, 8); PDF 88's SUM.
 * A record only 'neg' reaches -- PDF 72 (SHF), ADDRESS FIELD NOT
   INDEXED, (U) shift_95 8.70 -> 8.40: two failures: 'neg' (47, 0, 1)
   against (48, 0, 0); PDF 72's SUM.  (The INTERNAL columns and PDF 71
   are reached the same way.  'neg' compares within a column, so a
   misread repeated down a whole column would pass it.)
 * A record only 'quotefp' reaches -- PDF 104 ST(U) quoted 4.82 -> 4.80:
   two failures: 'quotefp' (3, 6, 3) against (2, 6, 4); PDF 104's SUM.

MEASURED INJECTIONS, 2026-11-16, on the VFL forwarding pages (PDF 143-169),
made to a COPY with --file=; the original was `cmp`-clean after.

 * A record 'vfwdib' reaches -- PDF 147 (L), first block, (B,32,1) ni_ibox
   6.60 -> 6.90: four failures: 'ibox' (67, 10, 19) against (68, 10, 18);
   'invert' (212, 11, 1) against (213, 11, 0); 'vfwdib' (95, 0, 1)
   against (96, 0, 0); PDF 147's SUM.
 * A record 'index' reaches -- PDF 143 (+), first block, (BU,32,8) ni_int
   7.36 -> 7.66: three failures: 'index' (67, 20, 1) against (68, 20, 0);
   'invert' (210, 7, 7) against (211, 7, 6); PDF 143's SUM.
 * A record 'vfwd' reaches on an ACCUM. column -- PDF 165 (CV), first
   block, (B,8,1) ni_accum 6.00 -> 6.60: three failures: 'invert' (47, 0,
   1) against (48, 0, 0); 'vfwd' (95, 0, 1) against (96, 0, 0); PDF 165's
   SUM.

MEASURED INJECTIONS, 2026-11-16, on the VFL immediate pages (PDF 171-189),
same method.

 * PDF 171 (+I), first block, (B,32,1) ni_imm 6.76 -> 6.16: four failures:
   'immf' (78, 7, 11) against (79, 7, 10); 'index' (47, 0, 1) against
   (48, 0, 0); 'invert' (45, 2, 1) against (46, 2, 0); PDF 171's SUM.
   'immn' does NOT fail: the pair (PDF 116's 6.60) was already far, and
   stays far -- a far-to-far change is invisible to a count.
 * PDF 188 (CI0011, one block, no invert), (BU,16,4) ix_imm 6.00 -> 6.60:
   four failures: 'immf' (61, 2, 7) against (62, 2, 6); 'immn' (62, 1, 7)
   against (63, 1, 6); 'index' (33, 1, 1) against (34, 1, 0); PDF 188's
   SUM.

    python3 tests/check_atlas_data.py          # the check
    python3 tests/check_atlas_data.py -v       # plus per-column grid census
    python3 tests/check_atlas_data.py --tally  # print TALLY and SUM lines
                                               # for pages that lack them
"""
import os
import sys
from decimal import Decimal

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import atlas_data                                  # noqa: E402
from atlas_data import load_atlas, AtlasError      # noqa: E402

FIRST_PDF, LAST_PDF = 37, 189

# IBOX rows the page prints with the same figures in every column.
ROW_TWINS = {
    104: [("LC", "LR"), ("SC", "SR"), ("KV", "KC"), ("KV", "V+"),
          ("KV", "V+C"), ("KV", "V+CR"), ("LVI", "V+I"), ("LVI", "KVI"),
          ("LVI", "KCI"), ("V+IC", "V+ICR")],
    109: [("LV", "LC"), ("LV", "LR"), ("SV", "SC"), ("SV", "SR"),
          ("KV", "KC"), ("V+", "KV"), ("R", "RCZ#2"), ("LVNI", "V-I"),
          ("C+I", "C-I"), ("C+I", "KVNI"), ("V-IC", "V-ICR#1")],
    110: [("18BITS", "19BITS"), ("18BITS", "24BITS")],
}

# PDF 104's captions quote "N.NN IN A xx ENVIRONMENT".  For the index
# arithmetic rows that figure is on PDF 109: (row on 104) -> (row, column).
QUOTED_109 = {
    "LX": ("LX", "ext_direct"), "SX": ("SX", "ext_direct"),
    "LV": ("LV", "ext_direct"), "SV": ("SV", "ext_direct"),
    "LC": ("LC", "ext_direct"), "SC": ("SC", "ext_direct"),
    "LR": ("LR", "ext_direct"), "SR": ("SR", "ext_direct"),
    "KV": ("KV", "ext_direct"), "KC": ("KC", "ext_direct"),
    "V+": ("V+", "ext_direct"), "V+C": ("V+C", "ext_direct"),
    "V+CR": ("V+CR#1", "ext_direct"),
    "LVI": ("LV", "immediate"), "V+I": ("V+", "immediate"),
    "V+IC": ("V+C", "immediate"), "V+ICR": ("V+CR#1", "immediate"),
    "KVI": ("KV", "immediate"), "KCI": ("KC", "immediate"),
}

# PDF 104's floating-point subject rows quote their own time ("ST(U) (4.82
# IN A ST(U) ENVIRONMENT)").  The figure is compared with the instruction's
# own FP sheet without forwarding, NORMALIZED 1. block, (U) row, EXTERNAL
# OPERAND with no indexing.  PDF 102 puts every instruction of the test on
# the same external operand; that it is unindexed is an ASSUMPTION (the
# ix_ext figure is the same as ni_ext on all six sheets except DL, 1.41
# against 1.40).  That it is the no-forwarding sheet is supported by the
# ink: L(U) 1.34 and DL(U) 1.41 fit PDF 64/66 (1.33, 1.40), not the
# forwarding PDF 95/97 (2.41).  The quoted figures sit within 0.02 of the sheets: the
# environment run is a different measurement, so this rule's far pairs
# are expected and its counts are what is checked.
QUOTED_FP = {
    "ST(U)": (48, "ST"), "SLO(U)": (49, "SLO"), "SRD(U)": (50, "SRD"),
    "L(U)": (64, "L"), "DL(U)": (66, "DL"), "LFT(U)": (68, "LFT"),
}

# FP pages with forwarding (PDF 73-101) repeat, page for page, the pages
# without it (PDF 42-70): same instruction, same blocks and rows.  Where
# forwarding cannot help (ST, the shifts, *, /, ...) the two print the same
# figure; elsewhere they differ for real.  The pair is made on the EXTERNAL
# and I-BOX columns, the only ones both print.
FWD_OFFSET = 31

# VFL pages with forwarding (PDF 143-169) repeat, page for page, the VFL
# pages without it (PDF 116-142): same instruction, blocks and rows.  PDF
# 114 (printed 107), of the no-forwarding run: "For I-box operands, the
# locations were $X0, $X1, $X2, $X3, $X0, etc.  Here there should be no
# difference in times between no forwarding vs. forwarding, and this was
# indeed the case."  So the I-BOX OPERAND pair is its own rule, 'vfwdib',
# the one the volume itself predicts equal; 'vfwd' pairs the other columns
# both pages print (EXTERNL OPERAND, EXTERNL WB XOVR, ACCUM. OPERAND),
# where forwarding may help.  The INTERNL columns are printed only with
# forwarding.
VFL_FWD_OFFSET = 27

# The immediate pages (PDF 171-189) print one figure per group, IMMED.
# OPERAND.  PDF 114: "The 24 bit address of the instruction contained the
# equivalent of the standard operand (444...4)16.  There is, of course, no
# case of forwarding with immediate operands."  The volume does NOT say how
# these figures relate to the memory-operand pages, so the immediate column
# is paired with the same instruction's EXTERNL OPERAND column on BOTH
# runs: 'immf' against the forwarding page, 'immn' against the no-forwarding
# page.  Both are counted, neither is required to agree, and neither fits
# throughout: on +I the forwarding page fits better (PDF 171 (B,8,1) 4.96 =
# PDF 143's, not PDF 116's 4.80); over all 19 pages 'immn' has more exact
# pairs (929 of 1,600 against 731), and on the compares KI..KFEI neither fits
# (the immediate figure is lower, e.g. 3.61 against 4.20).
IMM_BASE = {
    "+I": "+", "+MGI": "+MG", "LI": "L", "LWFI": "LWF", "LFTI": "LFT",
    "LTRSI": "LTRS", "KI": "K", "KRI": "KR", "KEI": "KE", "KFI": "KF",
    "KFRI": "KFR", "KFEI": "KFE", "*I": "*", "/I": "/", "*I+": "*+",
    "LCVI": "LCV", "LTRCVI": "LTRCV", "CI0011": "C0011",
    "CTI0111": "CT0111",
}

# On the forwarding and immediate pages the INTERNL and IMMED. columns are
# printed under both NO INDEXING and INDEXING; 'index' pairs ni_X with ix_X
# for those columns (PDF 113: the indexing columns index by a register
# containing zero).  The older columns are not paired this way, so the
# TALLY lines of PDF 116-142 are unchanged.
INDEX_PAIRED = ("int", "int_wbx", "imm")


def vfl_page(by_pdf, instr, forwarding, addressing="direct"):
    """The VFL sheet timing instr under the given conditions, or None."""
    for p in (by_pdf or {}).values():
        if p.cls == "VFL" and instr in p.instrs and p.records and \
                p.records[0].cond.get("forwarding") == forwarding and \
                p.records[0].cond.get("addressing") == addressing:
            return p
    return None


# (pdf, instr, block, row, col): (this file, perf_char_timing.py, verdict)
ADJUDICATED = {}


def classify(a, b):
    d = abs(Decimal(a) - Decimal(b))
    return "exact" if d == 0 else ("near" if d == Decimal("0.01") else "far")


def twin_pairs(page, by_pdf=None):
    """Yield (rule, record_a, record_b) for every printed-twice pair."""
    if page.pdf == 104 and by_pdf and 109 in by_pdf:
        tgt = {(r.row, r.col): r for r in by_pdf[109].records}
        for r in page.records:
            if r.col == "quoted" and r.row in QUOTED_109:
                t = tgt.get(QUOTED_109[r.row])
                if t is not None and t.kind == "time":
                    yield "quoted", r, t
    if page.pdf == 104 and by_pdf:
        for r in page.records:
            if r.col == "quoted" and r.row in QUOTED_FP:
                pdf, ins = QUOTED_FP[r.row]
                for t in (by_pdf[pdf].records if pdf in by_pdf else ()):
                    if (t.instr, t.block, t.row, t.col, t.kind) == (
                            ins, "NORMALIZED 1.", "(U)", "ni_ext", "time"):
                        yield "quotefp", r, t
    idx = {(r.instr, r.block, r.row, r.col): r for r in page.records
           if r.kind == "time"}
    if page.cls == "VFL":
        for (ins, blk, row, col), r in idx.items():
            if blk == "-":
                t = idx.get((ins, "INVERT SIGN OF INSTRUCTION", row, col))
                if t:
                    yield "invert", r, t
            if col.endswith("_ext"):
                t = idx.get((ins, blk, row, col[:-3] + "ibox"))
                if t:
                    yield "ibox", r, t
            if col.startswith("ni_") and col[3:] in INDEX_PAIRED:
                t = idx.get((ins, blk, row, "ix_" + col[3:]))
                if t:
                    yield "index", r, t
        cond = page.records[0].cond if page.records else {}
        if cond.get("forwarding") == "yes" and \
                cond.get("addressing") == "direct" and by_pdf:
            base = by_pdf.get(page.pdf - VFL_FWD_OFFSET)
            if base is not None and base.cls == "VFL" and base.records and \
                    base.records[0].cond.get("forwarding") == "no" and \
                    base.instrs == page.instrs:
                bidx = {(r.instr, r.block, r.row, r.col): r
                        for r in base.records if r.kind == "time"}
                for key, r in idx.items():
                    t = bidx.get(key)
                    if t is not None:
                        yield ("vfwdib" if key[3].endswith("_ibox")
                               else "vfwd"), r, t
        if cond.get("addressing") == "immediate" and by_pdf:
            for rule, fwd in (("immf", "yes"), ("immn", "no")):
                for ins in dict.fromkeys(page.instrs):
                    base = vfl_page(by_pdf, IMM_BASE.get(ins), fwd)
                    if base is None:
                        continue
                    bidx = {(r.instr, r.block, r.row, r.col): r
                            for r in base.records if r.kind == "time"}
                    for (i2, blk, row, col), r in idx.items():
                        if i2 == ins and col.endswith("_imm"):
                            t = bidx.get((IMM_BASE[ins], blk, row,
                                          col[:-3] + "ext"))
                            if t is not None:
                                yield rule, r, t
    elif page.cls == "FP":
        base = by_pdf.get(page.pdf - FWD_OFFSET) if by_pdf else None
        if base is not None and base.cls == "FP" and page.records and \
                base.records and \
                page.records[0].cond.get("forwarding") == "yes" and \
                base.records[0].cond.get("forwarding") == "no":
            bidx = {(r.instr, r.block, r.row, r.col): r for r in base.records
                    if r.kind == "time"}
            for key, r in idx.items():
                t = bidx.get(key)
                if t is not None and (r.cond.get("ah_indicator") ==
                                      t.cond.get("ah_indicator")):
                    yield "fwd", r, t
        for (ins, blk, row, col), r in idx.items():
            if not row.startswith("NEG "):
                t = idx.get((ins, blk, "NEG " + row, col))
                if t:
                    yield "neg", r, t
            if col.endswith("_ext"):
                t = idx.get((ins, blk, row, col[:-3] + "ibox"))
                if t:
                    yield "ibox", r, t
    elif page.cls == "BRANCH":
        for (ins, blk, row, col), r in idx.items():
            if col.endswith("_consec"):
                t = idx.get((ins, blk, row, col[:-6] + "noncon"))
                if t:
                    yield "noncon", r, t
    if page.pdf in ROW_TWINS:
        for a, b in ROW_TWINS[page.pdf]:
            for (ins, blk, row, col), r in idx.items():
                if row == a:
                    for (ins2, blk2, row2, col2), t in idx.items():
                        if row2 == b and col2 == col and blk2 == blk:
                            yield "rows", r, t


def tallies(page, by_pdf=None):
    out, reached, far = {}, set(), []
    for rule, a, b in twin_pairs(page, by_pdf):
        c = classify(a.text, b.text)
        e = out.setdefault(rule, {"exact": 0, "near": 0, "far": 0})
        e[c] += 1
        reached.add(id(a))
        reached.add(id(b))
        if c == "far":
            far.append((rule, a, b))
    return ({k: (v["exact"], v["near"], v["far"]) for k, v in out.items()},
            reached, far)


def page_sum(page):
    t = [r.us for r in page.records if r.kind == "time"]
    return len(t), sum(t, Decimal(0))


def second_reading(pages):
    """Compare with the earlier transcriptions in perf_char_timing.py.
    Returns (n_compared, disagreements, reached ids, presence mismatches)."""
    import perf_char_timing as P
    by_pdf = {p.pdf: p for p in pages}
    n, bad, reached, presence = 0, [], set(), []

    def cmp(pdf, instr, block, row, cols, values):
        nonlocal n
        page = by_pdf.get(pdf)
        if page is None:
            return
        for col, v in zip(cols, values):
            r = None
            for x in page.records:
                if (x.block, x.row, x.col) == (block, row, col) and \
                        (instr is None or x.instr == instr):
                    r = x
                    break
            if v is None and r is None:
                continue
            if v is None or r is None or r.kind != "time":
                presence.append((pdf, block, row, col, v,
                                 r.text if r else None))
                continue
            n += 1
            reached.add(id(r))
            if Decimal(r.text) != Decimal("%.2f" % v):
                key = (pdf, r.instr, block, row, col)
                if key not in ADJUDICATED:
                    bad.append((key, r.text, "%.2f" % v))

    for row, vals in P.V2_TRANSMIT.items():
        cmp(106, None, "-", "%dWD" % row, P.V2_TRANSMIT_COLUMNS, vals)
    names = {"V+CR_unsuccessful": "V+CR#1", "V+CR_successful": "V+CR#2",
             "V-ICR_unsuccessful": "V-ICR#1", "V-ICR_successful": "V-ICR#2",
             "RCZ_a": "RCZ#1", "RCZ_b": "RCZ#2"}
    for row, vals in P.V2_IBOX.items():
        cmp(109, None, "-", names.get(row, row), P.V2_IBOX_COLUMNS, vals)
    for row, vals in P.V2_BRANCH.items():
        blk = {"BXL BZXL": "BIND / I-BOX IND",
               "BAL BZAL": "ARITH RESULT IND"}.get(row, "-")
        cmp(112, None, blk, row, P.V2_BRANCH_COLUMNS, vals)
    for table, blk in ((P.V2_VFL_MPLUS, "-"),
                       (P.V2_VFL_MPLUS_INVERT_SIGN,
                        "INVERT SIGN OF INSTRUCTION")):
        for (mode, fl, bs), vals in table.items():
            cmp(117, "M+", blk, "(%s,%d,%d)" % (mode, fl, bs),
                P.V2_VFL_COLUMNS, vals)
    for (mode, fl, bs), vals in P.V2_VFL_C0011.items():
        cmp(140, None, "-", "(%s,%d,%d)" % (mode, fl, bs),
            P.V2_VFL_COLUMNS, vals)
    return n, bad, reached, presence


def load_coverage(path=atlas_data.ATLAS):
    """KIND lines live in the atlas file as comments the loader skips:
       #KIND <tab> first-last <tab> status <tab> kind <tab> what"""
    cov = {}
    errs = []
    with open(path) as f:
        for lineno, line in enumerate(f, 1):
            if not line.startswith("#KIND\t"):
                continue
            parts = line.rstrip("\n").split("\t")
            if len(parts) < 5:
                errs.append("line %d: #KIND needs range, status, kind, what" % lineno)
                continue
            a, _, b = parts[1].partition("-")
            for pdf in range(int(a), int(b or a) + 1):
                if pdf in cov:
                    errs.append("line %d: PDF %d has two #KIND lines" % (lineno, pdf))
                cov[pdf] = (parts[2], parts[3], parts[4])
    return cov, errs


def main(argv):
    verbose = "-v" in argv
    want_tally = "--tally" in argv
    path = atlas_data.ATLAS
    for a in argv:
        if a.startswith("--file="):
            path = a[7:]
    fails = []
    try:
        pages = load_atlas(path)
    except AtlasError as e:
        print("FAIL atlas does not parse: %s" % e)
        return 1
    recs = [r for p in pages for r in p.records]
    times = [r for r in recs if r.kind == "time"]

    # 1. page numbers
    for p in pages:
        if p.printed != p.pdf - 7:
            fails.append("PDF %d: printed %d is not PDF - 7" % (p.pdf, p.printed))

    # 2. coverage
    cov, errs = load_coverage(path)
    fails += errs
    for pdf in range(FIRST_PDF, LAST_PDF + 1):
        if pdf not in cov:
            fails.append("PDF %d has no #KIND line" % pdf)
    have = {p.pdf for p in pages}
    for pdf, (status, kind, what) in sorted(cov.items()):
        if status not in ("transcribed", "other", "remaining"):
            fails.append("PDF %d: unknown status %r" % (pdf, status))
        if (status == "transcribed") != (pdf in have):
            fails.append("PDF %d: #KIND says %s but %s" % (
                pdf, status, "a sheet exists" if pdf in have else "there is no sheet"))

    # 3. uncertain cells
    unc = [r for r in recs if r.uncertain or r.kind == "illegible"]
    for p in pages:
        if any(r.uncertain or r.kind == "illegible" for r in p.records) \
                and not p.notes:
            fails.append("PDF %d has an uncertain cell and no NOTE" % p.pdf)

    # 4. redundancy
    by_pdf = {p.pdf: p for p in pages}
    reached = set()
    tot = {}
    far_all = []
    for p in pages:
        got, rch, far = tallies(p, by_pdf)
        reached |= rch
        far_all += far
        for rule, t in got.items():
            e = tot.setdefault(rule, [0, 0, 0])
            for i in range(3):
                e[i] += t[i]
        if want_tally:
            if got != p.tallies or p.sum != page_sum(p):
                print("PDF %d:" % p.pdf)
                for rule, t in sorted(got.items()):
                    print("TALLY\t%s\t%d\t%d\t%d" % ((rule,) + t))
                print("SUM\t%d\t%s" % page_sum(p))
                grp = {}
                for rule, a, b in far:
                    grp.setdefault((rule, a.col, a.text, b.text), []).append(
                        ("i:" if a.block != "-" and rule != "invert" else "") + a.row)
                for (rule, col, x, y), rows in sorted(grp.items()):
                    print("   far %-7s %-11s %6s vs %-6s x%d  %s" % (
                        rule, col, x, y, len(rows), " ".join(rows[:6])))
            continue
        if got != p.tallies:
            for rule in sorted(set(got) | set(p.tallies)):
                if got.get(rule) != p.tallies.get(rule):
                    fails.append("PDF %d: redundancy rule %r counts exact/near/"
                                 "far %s, the page's TALLY says %s" % (
                                     p.pdf, rule, got.get(rule),
                                     p.tallies.get(rule)))
        # 6. sum
        if p.sum is None:
            fails.append("PDF %d has no SUM line" % p.pdf)
        elif p.sum != page_sum(p):
            fails.append("PDF %d: %d numeric cells totalling %s, the SUM line "
                         "says %d totalling %s" % ((p.pdf,) + page_sum(p) + p.sum))
    if want_tally:
        return 0

    # 5. second reading
    n2, bad2, rch2, presence = second_reading(pages)
    reached |= rch2
    for key, mine, theirs in bad2:
        fails.append("second reading: PDF %d %s [%s] %s %s is %s here and %s "
                     "in perf_char_timing.py, not adjudicated" % (
                         key + (mine, theirs)))
    for pr in presence:
        fails.append("second reading: PDF %d [%s] %s %s: perf_char_timing.py "
                     "has %s, this file has %s" % pr)

    # report
    whole = sum(1 for r in times if r.whole_cycles)
    print("atlas: %d pages transcribed, %d records (%d times, %d indicator "
          "marks, %d illegible), %d cells stated blank" % (
              len(pages), len(recs), len(times),
              sum(1 for r in recs if r.kind == "mark"),
              sum(1 for r in recs if r.kind == "illegible"),
              sum(p.blank for p in pages)))
    st = {}
    for pdf, (status, kind, what) in cov.items():
        st[status] = st.get(status, 0) + 1
    print("coverage of PDF %d-%d: %s" % (FIRST_PDF, LAST_PDF, ", ".join(
        "%d %s" % (v, k) for k, v in sorted(st.items()))))
    print("times on the 0.3 us grid: %d of %d (%.0f%%)" % (
        whole, len(times), 100.0 * whole / max(1, len(times))))
    for rule, (e, n, f) in sorted(tot.items()):
        print("redundancy %-7s %5d pairs: %5d exact, %4d within the last "
              "digit, %4d differ" % (rule, e + n + f, e, n, f))
    print("second reading against perf_char_timing.py: %d cells compared, "
          "%d disagree, %d adjudicated" % (n2, len(bad2), len(ADJUDICATED)))
    print("uncertain or illegible cells: %d" % len(unc))
    for r in unc:
        print("   PDF %d %s [%s] %s %s = %s" % (
            r.pdf, r.instr, r.block, r.row, r.col, r.text))
    unreached = [r for r in times if id(r) not in reached]
    print("REACH: %d of %d times are touched by a reading check; %d are NOT "
          "(only the file-integrity SUM covers those)" % (
              len(times) - len(unreached), len(times), len(unreached)))
    if verbose:
        print("\nper page and column: how many times are whole clocks")
        for p in pages:
            cols = {}
            for r in p.records:
                if r.kind == "time":
                    c = cols.setdefault(r.col, [0, 0])
                    c[0] += r.whole_cycles
                    c[1] += 1
            print("  PDF %3d %-8s %s" % (p.pdf, ",".join(dict.fromkeys(
                p.instrs))[:8] or p.cls, "  ".join(
                    "%s %d/%d" % (k, a, b) for k, (a, b) in cols.items())))
        by = {}
        for r in unreached:
            by[r.pdf] = by.get(r.pdf, 0) + 1
        print("\nunreached times by page: " + ", ".join(
            "PDF %d: %d" % kv for kv in sorted(by.items())))
    if fails:
        for f in fails:
            print("FAIL " + f)
        print("%d FAILURE(S)" % len(fails))
        return 1
    print("PASS atlas data self-check")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
