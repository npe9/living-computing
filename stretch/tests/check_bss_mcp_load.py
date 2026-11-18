#!/usr/bin/env python3
"""check_bss_mcp_load.py -- plan R2b: the relocation table the RECONSTRUCTED
BSS processor builds (decks/bss_7030.strap) is fed to MCP's OWN loader and
resume load (printed pp.320-334, IBM's code), which must load the job the
way C28-6379-0 printed p.17 (Example 4's storage map) lays it out.

>>> decks/bss_7030.strap is a RECONSTRUCTION, not IBM's code.  What this test
>>> shows is that the table it builds is one IBM's loader reads and obeys:
>>> every subprogram lands at p.17's printed origin, every common reference
>>> at p.17's printed common origin, every transfer vector holds p.17's entry
>>> addresses, and resume load returns *MAIN*'s entry.  It does not show
>>> that BSS's code is IBM's. <<<

TWO RUNS ON THE MODEL, then a third pair.
  RUN 1, BSS: check_bss_example4's machinery on Example 4's subprograms,
    built here as stubs of p.17's sizes that ALSO (unlike R2a's stubs)
    reference every common they declare and blank common, put a data word
    in each named common, and carry 160 data words in *MAIN* so the input
    runs past one 34-card arc of TWS (53 cards: POLY's run from card 32
    crosses into arc 1, and DERIV and VALUE start there).  BSS must still print p.17's map row for row; its relocation
    table (at the blank common base B) and KSILO words 8-11 are dumped.
  RUN 2, MCP: the LOADER image (pp.99-334, mcp_image), with ONLY these
    words put in from outside:
      * the table words and KSILO+8..+11 exactly as run 1 left them (the
        transfer: C28 p.9, "The BSS processor leaves the relocation table
        in storage"; "Control is passed from the BSS processor to MCP and
        then to the MCP loader");
      * what MCP itself leaves before resume load in a GO job, PLANTED
        (scaffold): KSILO+2 = BSS (p.271 ll.43-50, the GO,FORTRAN rewrite),
        SCORG 0 (p.396 l.47, "SET TOGO (ZERO)"; the image already holds 0),
        KSILO+1.19 = 1 (one of the five TYPE-card bits p.384 ll.19-20 put
        at KSILO+1.18; which TYPE card sets it is NOT established) -- these
        three lines and p.250's, p.271's and p.108's below are cited from
        the transcriptions in decks/, not re-read in the ink; the
        image's REJJOB.60 is 0, as it must be (p.332 l.54 BBZ,REJJOB+.60,
        YSUKFX sends a 1 to "JOB CANNOT BE RUN BECAUSE OF INPUT
        DIFFICULTIES", p.334 l.51; p.250 l.45 BZB1 sets it);
      * the disk, as core images (SCAFFOLD): TWS (type area "))))))))",
        ATWSTA p.291 l.30) at TWSD, every card at disk word 2 + 512 arc +
        15 card (p.332 ll.27-30: V+IC,13,15. / two words at each arc's end
        / LCI,$13,34.0; AREADS's value -13, so the first card is read at
        word 2, spec 5.4 and G6); BSS reads its input from TWSD + 2, so
        its disk address (deck rule C11) is the card's offset from there;
        and one LB type area per library deck (cards contiguous from word
        0, AREAD1), named "LB" + the subprogram's first entry name, six
        characters, blank-padded, in A6 (CHOSEN, spec G7: which type areas
        exist and their names are unprinted);
      * $FETCH, as a stub at word 32 (DMCP, landed p.108 l.5): resume load
        calls it with B,DMCP / ,DFETCH / YRLDTA / YDFRDA / ,YBCBU / ,15.
        (p.332 ll.33-41).  B,DMCP leaves no return address, so the stub
        tells this call from the B,DMCP / ,DRET of p.333 ll.4-5 by SICBU:
        planted with a sentinel, written only by p.333 l.2 (SV,14,SICBU)
        just before $RET.  On $FETCH it looks YRLDTA's 48 bits up (TWS or
        an LB area), copies 15 words from word YDFRDA of that area to YBCBU
        and takes the normal return (YLOAD, p.332 l.42), or, past the end
        of an LB area, the end return (B,YLERR, p.332 l.41).  No IBM word
        is changed.
    The run enters resume load at YRESL1 (p.332 l.2) and from there it is
    IBM's code throughout: YRESL1 -> YARSL (p.333 ll.22-28: the limits from
    KSILO+8 and +9, ARNRM5 with KSILO+9.32) -> ARNRM5 (p.327 ll.5-27: TWS
    or LB, $13 and YRLDTA) -> the read loop (p.332 ll.19-52) -> ALOADR on
    each card (AFPCRD p.324 ll.12-29, ARNRM1-2 p.326 ll.41-47, p.327
    ll.1-4) -> for a library deck the end return (YLERR -> YAERR1, p.334
    ll.7-16) -> ARNRM4 (p.327 ll.28-30) -> YBCENC (p.332 ll.53-56) ->
    p.333 ll.1-5, $RET.
  ORACLE: every subprogram assembled ABSOLUTE at p.17's printed origin, its
    commons at p.17's printed common origins (blank at 213713), loaded by
    the absolute path (strap2.punch.load); each transfer vector the
    skeleton B,entry;NOP with p.17's entry (origin + REL. E. P.); SICBU
    holds *MAIN*'s entry, 000051.0 = 000041 + 000010.0.  Every touched word
    starts as a sentinel, so a bit the load should not write must survive.
    YLJSLT (p.332 l.49, the loader's error word D) must be unchanged.
  RUN 3 + 4, NO LIBRARY (C11): the same subprograms with every call to the
    library removed, so the last relocation-table entry is VALUE, on TWS,
    and is followed there by the FORTRAN branch card.  The deck's card
    count (rule C11) leaves the branch card out; the loader must end the
    job on VALUE's last card through ARNRM4.

C10 and C11, SETTLED (the record is in docs/reading_notes/fortran_bss_plan.md
R2b): C10, the library name, is the 36 bits L p.327 l.24 reads,
LF(BU,36,6) (PDF 78, read in the ink), which C22-6728 p.82 Fig. 39 names
SRDKAD SYN(BU,36,6) "a 36-bit field containing a type-area name" (read in
the ink) -- six 6-bit characters behind ALB's "LB" (p.291 l.29); C28 p.10's
"first 48 bits" is not what this loader reads.  C11: the count leaves the
FORTRAN branch card out (C28 p.10 Fig. 4 "Number of Cards in Subprogram";
p.9 item 9, the branch card signals "end-of-deck to the BSS processor").

THE FETCH COUNT.  The stub logs every card it serves (LOG); the bench
checks that it served each subprogram card once -- 53 on TWS plus 12 in the
LB areas, or 53 without the library -- and so that the loader never read
the FORTRAN branch card behind VALUE (C11).

BRING-UP, 2026-11-17 (each a fault in this file, not in IBM's code or the
deck): TI with an indexed source and LV on YDFRDA both misread the disk
word (LV takes the half word's bit 24, which p.332 l.36's ",0" sets, as
the value's sign: the stub now takes 24 bits with L/ST); a BXL to $+1.32
skipped the LB base; REJJOB.60 first planted 1, which p.332 l.54 sends to
YSUKFX.  Then: ALL CHECKS PASSED -- run 2, 214 bench checks (212 + PC +
cycles), 341,736 cycles; run 4, 202 (200 + 2), 280,355 cycles.  The
library routines were read in disk order, UST*, IOCS*, FISIP*.

MEASURED, each OBSERVED (deck injections scripted, the deck restored from
a saved copy and verified with cmp; run 1 fresh each time; the three deck
injections below were first run on a variant clearing the KSILO half words
whole, then rerun on the committed deck with the same failure sets):
  - C11 CONTROL, the last table entry's count one HIGH (R2B_TAMPER=count+1,
    no-library run): only fetches_53_no_branch_card fails (the loader read
    the branch card and ended there, 282,079 cycles); every loaded word
    passes -- the loader itself cannot tell, so the fetch count is what
    pins C11.  Count one LOW (count-1): only loaded_213542 fails (VALUE's
    last card, its word in A).
  - deck, the disk address one card late (after SCPR1L, +I(BU,18),15): 4
    fail -- loaded_1006, loaded_1447, loaded_1455, and the fetch count (67
    served, not 65); 348,818 cycles.
  - deck, the library name left in A8 (RT3 ST(BU,36) for SF(BU,36,6)): 11
    fail -- YRLDTA names no LB area, the stub stops at NOAREA (PC), 53
    served, SICBU's sentinel stays, and 2451, 2452, 2460, 2461, 2462, 3604,
    5517, 5520 (FISIP*, IOCS*, UST*) stay unloaded.
  - deck, the common origins a half word late (RT5 V+I,$13,3.0 for 2.32):
    the step cap is reached, 52 fail, read mid-run.
  - NOT DISCRIMINATING, measured: the variant deck clearing KSILO+9 and
    +10 as whole half words (bits 24-31 too) and the committed deck (only
    the 24-bit fields) both load correctly in 341,736 cycles:
    YARSL takes KSILO+9.32 with LR (p.333 l.26) and ARNRM5 rewrites it with
    SV (p.327 l.10) before AFPCRD's LV reads it, and ARNRM4 passes only
    KSILO+10's address on (SVA).  The deck is unchanged.
R2B_RUN1, R2B_KEEP, R2B_DUMP and R2B_TAMPER are bring-up and measurement
hooks; the suite sets none of them.
"""
import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "strap"))
sys.path.insert(0, HERE)
import check_bss_example4 as ex4                    # noqa: E402
import mcp_image                                    # noqa: E402
import prosa_dict                                   # noqa: E402
from strap_asm import assemble                      # noqa: E402
from strap2 import compile_cards                    # noqa: E402
from strap2.cards import deck_cards                 # noqa: E402
from strap2.punch import load as abs_load           # noqa: E402
from gen_tb import generate                         # noqa: E402

BSV = os.path.join(HERE, "..", "bsv")
BSC_DIR = "/opt/homebrew/Cellar/bsc/2026.01"
DRIVER_AT = 0o100000
TWSD = 0o140000             # disk word 0 of TWS, as a core image (SCAFFOLD)
LIBD = 0o150000             # the LB areas (SCAFFOLD)
SENT = 0x5555555555555555   # every word the load touches starts so
SICS = 0x3333333333333333   # SICBU's sentinel: still there means $FETCH
FILLER = 160                # data words in *MAIN*: the input crosses an arc
fails = 0


def check(label, got, want):
    global fails
    ok = got == want
    fails += not ok
    print(f"{'PASS' if ok else 'FAIL'} {label}" + ("" if ok else f": got {got!r}, want {want!r}"))


# ---- the stubs ------------------------------------------------------------
# Example 4's subprograms (check_bss_example4.SUBS/LIB, sizes from p.17)
# with what the loader must relocate: a reference to each named common
# (K<k>, a data word at a per-subprogram offset into it) and to blank
# common (BC, reserved only: loading into blank common is inhibited, C28
# p.4), and *MAIN*'s FILLER data words.
INDEX = {s[0][0][0]: j for j, s in enumerate(ex4.SUBS)}


def offset(name, j, size):
    return min(j, size - 1)


def body(entries, size, blank, commons, calls):
    j = INDEX.get(entries[0][0], 9)
    src = []
    at0 = [k for k, (_n, w) in enumerate(entries) if w == 0]
    src.append("%-8sXW,0,%d" % ("E%d" % at0[0] if at0 else "", len(calls)))
    src += ["        DD(BU,64),(16)%016X" % ex4.a8_word(c) for c in calls]
    pos = 1 + len(calls)
    for k, (_n, w) in enumerate(entries):
        if w == 0:
            continue
        assert w >= pos
        if w > pos:
            src.append("        DR(BU,64),%d" % (w - pos))
        src += ["E%d      B,E%d" % (k, k), "        NOP"]
        pos = w + 1
    if size is None:            # RANDM: its extent is 7 words, a DD at word 6
        return src + ["        DR(BU,64),5", "        DD(BU,64),0", "LAST    SYN,$"]
    src += ["        XW,K%d" % k for k in range(len(commons))]
    pos += len(commons)
    if blank:
        src.append("        XW,BC+%d.0" % (j % blank))
        pos += 1
    if entries[0][0] == "*MAIN*":
        src += ["        DD(BU,64),(8)%o" % (0o1234500000000 + n) for n in range(FILLER)]
        pos += FILLER
    assert size >= pos, (entries, size, pos)
    if size > pos:
        src.append("        DR(BU,64),%d" % (size - pos))
    return src + ["LAST    SYN,$"]


def commons_src(entries, blank, commons, where=None):
    """The common sections: SLCRCOM (relocatable) or SLC at p.17's origins."""
    j = INDEX.get(entries[0][0], 9)
    src = []
    for k, (c, w) in enumerate(commons):
        src.append("        SLCRCOM,%s" % c if where is None else "        SLC,(8)%o.0" % where[c])
        off = offset(c, j, w)
        if off:
            src.append("        DR(BU,64),%d" % off)
        src.append("K%d      DD(BU,64),(8)%o" % (k, 0o7700000000 + 0o100 * j + k))
    if blank:
        src.append("        SLCRCOM," if where is None else "        SLC,(8)%o.0" % where[""])
        src.append("BC      DR(BU,64),%d" % blank)
    return src


def stub_source(entries, size, blank, commons, calls):
    src = ["        PUNFPC,%s,%d" % ("(8)777777" if size is None else "LAST", blank)]
    src += ["%-8sENTER,E%d" % (n, k) for k, (n, _w) in enumerate(entries)]
    if commons:
        src.append("        PUNCDC")
        src += ["%-8sCOMBLOCK,%d" % (c, w) for c, w in commons]
    src.append("        PUNREL")
    return src + body(entries, size, blank, commons, calls) \
        + commons_src(entries, blank, commons) + ["        END"]


MAP_ORG = {r[0]: int(r[1], 8) for r in ex4.MAP_SUB}
MAP_EP = {r[0]: (int(r[1], 8) + int(r[2].split(".")[0], 8)) * 2 + (r[2].endswith(".4"))
          for r in ex4.MAP_SUB}               # half-word addresses, from p.17
MAP_CORG = {r[0]: int(r[1], 8) for r in ex4.MAP_COM}


def absolute_source(s):
    entries = s[0]
    name = entries[0][0]
    return (["        SLC,(8)%o.0" % MAP_ORG[name]] + body(*s)
            + commons_src(entries, s[2], s[3], MAP_CORG) + ["        END"])


def no_library(subs):
    lib = {e for s in ex4.LIB.values() for e, _w in s[0]}
    return [(e, z, b, c, [x for x in calls if x not in lib]) for e, z, b, c, calls in subs]


# ---- run 1: BSS -----------------------------------------------------------
def run_bss(tmp, tag, subs):
    ex4.stub_source = stub_source           # R2b's stubs, R2a's machinery
    src, exp = ex4.build(subs=subs, lib=ex4.LIB)
    got, out = ex4.run(src, tmp, "R2b" + tag)
    return got, exp, out


# ---- run 2: MCP's loader --------------------------------------------------
def a6name(name):
    return prosa_dict.a6(name.ljust(8)[:8])


def build_mcp(subs, lib_used, bss_mem, exp, tamper=None):
    pages = mcp_image.pages(99, 334)
    image, _s, _d, _e = mcp_image.build(False, pages, end_at="SDISP")
    S = image.symtab
    words = dict(image.words)

    def at(nm):
        return S[nm] // 64
    # The disk: TWS, then the LB areas (SCAFFOLD).
    decks = [ex4.punch(stub_source(*s)) for s in subs]
    tws = [c for d in decks for c in d] + ex4.punch(["        PUNREL", "        FEND"])
    plant = {}
    for k, cols in enumerate(tws):
        for i, v in enumerate(ex4.card_words(cols)):
            plant[TWSD + 2 + ex4.tws_offset(k) + i] = v
    areas, a = [], LIBD
    for name in lib_used:
        d = ex4.punch(stub_source(*ex4.LIB[name]))
        ws = [v for cols in d for v in ex4.card_words(cols)]
        for i, v in enumerate(ws):
            plant[a + i] = v
        areas.append(("LB" + name.ljust(6)[:6], a, len(ws)))
        a += len(ws) + 16
    # What BSS left: the table and KSILO 8-11, as run 1 dumped them.
    b0, b1 = exp["table_span"]
    ks = at("KSILO")
    for w in list(range(b0, b1)) + [ks + 8, ks + 9, ks + 10, ks + 11]:
        plant[w] = bss_mem[w]
    if tamper:
        tamper(plant, exp)
    # What MCP leaves for a GO job (PLANTED, see the header).
    plant[ks + 2] = words[at("ABSSID")]
    plant[ks + 1] = words.get(ks + 1, 0) | (1 << (63 - 19))
    assert not (words.get(at("REJJOB"), 0) >> (63 - 60)) & 1   # no input difficulties
    plant[at("SICBU")] = SICS
    # The $FETCH stub and the start (SCAFFOLD, assembled by strap_asm).
    def sym(nm, extra=0):
        v = S[nm] + extra
        return "%-8sSYN,(8)%o.%02o" % (nm if not extra else "R" + nm, v // 64, v % 64)
    drv = ["        SLC,32.0",
           "        B,SDMCP",
           "        SLC,(8)%o.0" % DRIVER_AT,
           sym("YRESL1"), sym("YLOAD"), sym("YLOAD", -32), sym("YRLDTA"),
           sym("YDFRDA"), sym("YBCBU"), sym("SICBU"),
           "START   B,YRESL1",
           "SDMCP   L(BU,64),SICBU",       # SICBU untouched: the $FETCH call
           "        K(BU,64),SICW",
           "        BAE,SFETCH",
           "DONE    B,DONE",               # $RET (p.333 ll.4-5): the job is loaded
           "SFETCH  SX,$1,SAV1",
           "        L(BU,48),YRLDTA",
           "        KF(BU,48),TWSNM",
           "        BAE,FTWS"]
    for i, (_n, _a, _l) in enumerate(areas):
        drv += ["        KF(BU,48),NM%d" % i, "        BAE,FL%d" % i]
    drv += ["NOAREA  B,NOAREA",
            "FTWS    L(BU,24),YDFRDA",
            "        ST(BU,24),TMPV",
            "        LV,$1,TMPV",
            "        V+I,$1,(8)%o.0" % TWSD,
            "        B,FCOPY"]
    for i, (_n, a0, ln) in enumerate(areas):
        drv += ["FL%d     L(BU,24),YDFRDA" % i,
                "        ST(BU,24),TMPV",
                "        LV,$1,TMPV",
                "        KV,$1,LEN%d" % i,
                "        BXL,FLA%d" % i,
                "        B,FEND",
                "FLA%d    V+I,$1,(8)%o.0" % (i, a0),
                "        B,FCOPY"]
    drv += ["FCOPY   SX,$1,LASTF",              # a log of the words read (diagnosis)
            "        SX,$2,SAV2",
            "        LX,$2,LOGP",
            "        SX,$1,0($2)",
            "        V+I,$2,1.0",
            "        SX,$2,LOGP",
            "        LX,$2,SAV2"]
    for k in range(15):
        drv += ["        L(BU,64),%d.0($1)" % k, "        ST(BU,64),YBCBU+%d.0" % k]
    drv += ["        LX,$1,SAV1",
            "        B,YLOAD",
            "FEND    LX,$1,SAV1",
            "        B,RYLOAD",              # the end return, B,YLERR (p.332 l.41)
            "        CNOP",
            "SAV1    XW,0",
            "SAV2    XW,0",
            "TMPV    XW,0",               # YDFRDA's 24-bit address field: LV on the
                                          # half word itself would read its bit 24
                                          # (p.332 l.36 prints 000000.00 80) as a sign
            "LOGP    XW,LOG",
            "LASTF   XW,0",
            "SICW    DD(BU,64),(16)%016X" % SICS,
            "TWSNM   DD(BU,64),(16)%016X" % (a6name("))))))))") << 16)]
    for i, (n, _a, ln) in enumerate(areas):
        drv += ["NM%d     DD(BU,64),(16)%016X" % (i, a6name(n) << 16),
                "LEN%d    XW,%d.0" % (i, ln)]
    drv += ["LOG     DRZ(BU,64),200", "        END,START"]
    d = assemble("\n".join(drv) + "\n")
    for w, v in d.words.items():
        if w in words:
            raise SystemExit("the stub overlaps the image at %o" % w)
        words[w] = v
    # The oracle: p.17's layout, assembled absolute and loaded.
    mem = {}
    for s in subs + [ex4.LIB[n] for n in lib_used]:
        p2 = compile_cards(deck_cards("\n".join(absolute_source(s)) + "\n"))
        assert not p2.msg.items and not p2.punch.unwritten, (p2.msg.items[:3], p2.punch.unwritten)
        m, _b = abs_load(p2.punch.cards)
        for bit, v in m.items():
            assert bit not in mem, "the oracle overlaps at %o" % (bit // 64)
            mem[bit] = v
    wr, val = {}, {}
    for bit, v in mem.items():
        w, k = divmod(bit, 64)
        wr[w] = wr.get(w, 0) | (1 << (63 - k))
        val[w] = val.get(w, 0) | (v << (63 - k))
    skel = ex4.tvskel()
    vec = {}
    for s in subs + [ex4.LIB[n] for n in lib_used]:
        o = MAP_ORG[s[0][0][0]]
        for i, c in enumerate(s[4]):
            vec[o + 1 + i] = (skel & ~(((1 << 19) - 1) << 45)) | (MAP_EP[c] << 45)
    checks = []
    full = (1 << 64) - 1
    for w in sorted(wr):
        if w in words or w in plant:
            raise SystemExit("the load area overlaps at %o" % w)
        words[w] = SENT
        want = (val[w] & wr[w]) | (SENT & ~wr[w] & full)
        kind = "loaded"
        if w in vec:
            want, kind = vec.pop(w), "vector"
        checks.append(("%s_%o" % (kind, w), str(w), want))
    assert not vec, vec
    for w, v in plant.items():
        if w in words and w not in (ks + 1, ks + 2, ks + 8, ks + 9, ks + 10, ks + 11,
                                    at("REJJOB"), at("SICBU")):
            raise SystemExit("a plant overlaps the image at %o" % w)
        words[w] = v
    image.words = words
    image.end_pc = d.end_pc
    sic = (SICS & ~(0xFFFFFF << 40)) | ((MAP_EP["*MAIN*"] << 5) << 40)
    checks.append(("SICBU_holds_MAIN_entry_51.0", str(at("SICBU")), sic))
    # The cards $FETCH served: every subprogram card on TWS and in the LB
    # areas, once each, and NOT the FORTRAN branch card after VALUE (C11).
    nread = len(tws) - 1 + sum(ln // 15 for _n, _a, ln in areas)
    lp = d.symtab["LOGP"] // 64
    checks.append(("fetches_%d_no_branch_card" % nread, str(lp),
                   (d.words[lp] & ~(0xFFFFFF << 40)) | ((d.symtab["LOG"] // 64 + nread) << 46)))
    yl = at("YLJSLT")
    checks.append(("no_loader_error_YLJSLT", str(yl), words[yl]))
    return image, checks, d


def run_mcp(tmp, module, image, checks, d):
    hexf = os.path.join(tmp, module + ".hex")
    src = generate(module, image, checks, pc_check=d.symtab["DONE"] // 32,
                   cycle_bound=20000000, step_cap=4000000, fast_load=hexf,
                   mem_dump=(tuple(int(x, 8) for x in os.environ["R2B_DUMP"].split(","))
                             if os.environ.get("R2B_DUMP") else None))
    bsv = os.path.join(BSV, module + ".bsv")
    with open(bsv, "w") as fh:
        fh.write(src)
    env = dict(os.environ, BLUESPECDIR=BSC_DIR + "/libexec/lib",
               PATH=BSC_DIR + "/bin:" + os.environ.get("PATH", ""))
    for sub in ("build-loader", "simbuild-loader"):
        os.makedirs(os.path.join(BSV, sub), exist_ok=True)
    out = ""
    try:
        for args in (["-sim", "-simdir", "simbuild-loader", "-bdir", "build-loader",
                      "-info-dir", "build-loader", "-g", "mk" + module, "-u", module + ".bsv"],
                     ["-sim", "-simdir", "simbuild-loader", "-bdir", "build-loader",
                      "-e", "mk" + module, "-o", module + "_sim"]):
            r = subprocess.run([BSC_DIR + "/bin/bsc"] + args + ["+RTS", "-K512m", "-RTS"],
                               cwd=BSV, env=env, capture_output=True, text=True)
            if r.returncode:
                return None, r.stdout + r.stderr
        r = subprocess.run(["./" + module + "_sim"], cwd=BSV, env=env, capture_output=True, text=True)
        out = r.stdout + r.stderr
        if os.environ.get("R2B_KEEP"):
            with open(os.environ["R2B_KEEP"] + "." + module, "w") as fh:
                fh.write(out)
    finally:
        for name in os.listdir(BSV):        # by exact name, never a glob
            if name in (module + ".bsv", module + "_sim", module + "_sim.so"):
                os.remove(os.path.join(BSV, name))
    return out, None


def report(out, nchecks, label):
    """Fold the bench's PASS/FAIL lines into one check each, by kind."""
    if out is None:
        check(label + ": the bench built and ran", False, True)
        return
    lines = out.splitlines()
    bad = [ln for ln in lines if ln.startswith("FAIL")]
    npass = sum(1 for ln in lines if ln.startswith("PASS"))
    for ln in bad[:40]:
        print("   ", ln)
    m = re.search(r"cycles = (\d+)", out)
    print(f"INFO {label}: {npass} bench checks pass, {len(bad)} fail"
          + (f", {m.group(1)} cycles" if m else ""))
    check(label, (len(bad), npass >= nchecks + 1), (0, True))


def _count(delta):
    """A measurement only (R2B_TAMPER): the LAST table entry's card count,
    word 0 bits 28-45, moved by delta, after BSS built it."""
    def t(plant, exp):
        b0, b1 = exp["table_span"]
        at, last = b0, None
        while True:
            last = at
            nxt = plant[at + 1] & 0o777777
            if not nxt:
                break
            at = nxt
        w = plant[last]
        n = (w >> 18) & 0o777777
        plant[last] = (w & ~(0o777777 << 18)) | ((n + delta) << 18)
    return t


TAMPER = {"count+1": _count(1), "count-1": _count(-1)}


def main(only=None):
    with tempfile.TemporaryDirectory() as tmp:
        runs = [("", ex4.SUBS, ["FISIP*", "IOCS*", "UST*"]),
                ("NoLib", no_library(ex4.SUBS), [])]
        for tag, subs, lib_used in runs:
            if only is not None and tag != only:
                continue
            cache = os.environ.get("R2B_RUN1")      # bring-up only: reuse run 1
            if cache and os.path.exists(cache + tag):
                import pickle
                got, exp, out = pickle.load(open(cache + tag, "rb"))
            else:
                got, exp, out = run_bss(tmp, tag, subs)
                if cache and got is not None:
                    import pickle
                    pickle.dump((got, exp, out), open(cache + tag, "wb"))
            if got is None:
                check(f"run 1{tag}: BSS ran to its halt", out[-1500:], "")
                continue
            check(f"run 1{tag}: BSS ERRC 0", got["errc"], 0)
            subs_rows, coms, _s = ex4.map_rows(got["lines"])
            if tag == "":
                check("run 1: BSS still prints p.17's ten subprogram rows",
                      subs_rows[:10], [tuple(r) for r in ex4.MAP_SUB])
                check("run 1: ... and its five common rows", coms[:5], [tuple(r) for r in ex4.MAP_COM])
            else:
                check("run 3: the six input subprograms at p.17's origins",
                      [r[:2] for r in subs_rows[:6]], [r[:2] for r in ex4.MAP_SUB[:6]])
                check("run 3: the commons at p.17's origins", coms[:5],
                      [tuple(r) for r in ex4.MAP_COM])
            ncards = len([c for s in subs for c in ex4.punch(stub_source(*s))])
            print(f"INFO run 1{tag}: {ncards} subprogram cards on TWS; steps {got['steps']}")
            image, checks, d = build_mcp(subs, lib_used, got["mem"], exp,
                                         tamper=TAMPER.get(os.environ.get("R2B_TAMPER")))
            out, err = run_mcp(tmp, "StretchBssMcpLoad%sTb" % tag, image, checks, d)
            if err:
                print(err[-3000:])
            report(out, len(checks), f"run {'2' if not tag else '4'}: MCP's loader loads the job as p.17 lays it out"
                   f" ({len(checks)} checks)")
    print("ALL CHECKS PASSED" if not fails else f"{fails} FAILED")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else None))
