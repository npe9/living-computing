#!/usr/bin/env python3
"""gen_loader_deck_tb.py -- MCP's own loader loads a deck STRAP II punched.

The JOB CONTROL BINARY LOADER (printed pp.320-334, transcribed, p.329 lost
from the scan) is IBM's code for reading the binary cards STRAP II punches.
This runs it, on the model, on a deck strap/strap2 punched, and checks that
core holds what STRAP II assembled.  It is the first IBM check of the card
format the punch writes: column 1's class, the sequence number in column 3,
the check sum in column 4 (ACHSM, printed p.322 l.48 - p.323 l.13), the
origin/flow/branch layout, and a zero after loading (a DRZ after data).
NOT EXERCISED: a DR, and a skip or zero before loading.

THE IMAGE: the LOADER overlay as check_mcp_body_image builds it, resident
pp.99-319 and pp.320-334, by strap/mcp_image.py.

THE DRIVER (scaffolding, assembled by strap_asm): for each card, fifteen
TI,1 into YBCBU (the model transmits one word per instruction), then the
calling sequence resume load itself uses, printed p.332 lines 42-52:

    LVI,15,A ; B,ALOADR
    A  VF,YBCBU        FWA
       ,L              lower limit; bit .25 = new job (p.333 line 25)
       ,U              upper limit
       B,ERR           error return
       VF,0            D: sequence number and error code
       B,DONE          branch return
       VF,0            A: the branch address
    (normal return: the next card)

L and U are plain half-word addresses, as at YRLLL (p.332 lines 46-47);
ALOADR reads 18 bits of each (p.320 lines 15-18).  The new-job bit, .25 of
L, is tested BZBZ,.57($15) (p.320 line 11) and cleared by that test, so the
driver sets it once, before the first card, with CM1111(BU,1) as ALOADR sets
its own indicators (p.320 line 14).  ERR loops on itself, so an error
return runs out the step cap and the PC check fails.

THE CHECKS.  Every word the deck touches starts as a sentinel, 5555...;
each must then hold STRAP II's bits where the deck wrote, zero where a DRZ
filled, and the sentinel elsewhere (the half word after GO's B,GO: the
loader stores a partial word and leaves the rest).  The END card's address
must come back in VF,A (SV,$1,3.($15), p.321 line 21).  Each card's D must
be untouched: the loader writes it only on the error return, so a failure
names IBM's code (docs/bss_loader_spec.md 8.1).

FIRST RUN, 2026-11-11: 54 checks pass, PC at DONE, 30,232 cycles.

MEASURED INJECTIONS, in strap/strap2/punch.py, each restored by copy and
cmp:
  - check sum without the end-around fold (s & 0xFFF): every check fails
    (48), PC at ERR; card 1's D = 0x00104000, sequence 1, code 1, CHECK
    SUM ERROR.
  - sequence numbers from 0: the same 48 fail; card 1's D = 0x00008000,
    sequence 0, code 2, SEQUENCE ERROR.
  - flow-card data one column late (FLOW_DATA + 12): exactly the 26 words
    the two flow cards carry fail (loaded_120013 .. loaded_120044), the
    check sum agreeing with the shifted data; nothing else (re-measured on
    the final generator, the six no_error checks passing).
  - (control, during bring-up) the driver's L punched as DD(BU,32): the
    new-job bit missed bit .25, the bounds stayed zero, and card 1 took
    code 5, TRIED TO LOAD OUTSIDE LIMITS.

MODE "rel" (argv[2]): the same driver on a PUNREL deck (REL_BODY), with
ORIGIN,(8)120000.0, so MCP's loader relocates every word by 120000 octal.
Its expected image is the same body assembled absolute at SLC,(8)120000.0:
a relocatable deck loaded at X must equal the program assembled at X.  The
body has a B,START and an XW,A,3,START (left and right relocation), an
LVI,$3,5 (none), DRs and a DRZ.  No branch-address check: under PUNREL END
punches no branch card (CHOSEN, strap/strap2/punch.py).
FIRST RUN, 2026-11-11: 44 checks pass, PC at DONE, 40,231 cycles.
MEASURED INJECTIONS, restored by copy and cmp:
  - relocation codes one half-word late (reloc.get(h-1)): 8 fail
    (loaded_120014-17, 120020-22, 120026).
  - every relocated field coded left ("1000"): 1 fails, loaded_120020,
    the XW (its right half not relocated, its left half doubled).
  - the card's bit count including the codes: 18 fail (120014-120035).
  - data card data from column 9, not 11: 35 fail, all data words plus
    zeroed_120041/42, loaded_120043, no_error_card_4 and the PC.
  - no relocation recorded (pass2): 18 fail, exactly the instruction words
    120014-120035.

MODE "fortran" (argv[2]): the FORTRAN program, common definition and
FORTRAN branch cards STRAP II punches for FORTRAN_SOURCE, each fed as the
first card of a new job.  Outside BSS, MCP's loader must return each with
code 4, ILLEGAL NON-BSS FUNCTION: ATBL (printed p.331) sends all three
classes to AFPCRD, which finds no BSS at KSILO+2 (p.324 lines 12-15).  The
error return goes on to the next card; a normal return fails the PC check.
FIRST RUN, 2026-11-11: 3 checks pass, PC at DONE, 3,303 cycles.
MEASURED, in strap/strap2/punch.py, restored by copy and cmp:
  - the program card's column 1 as 5,6,7: code4_fprog fails, D holding
    sequence 0 and code 3, ILLEGAL TYPE OF CARD; the other two pass.
  - LIMIT, measured: the common card punched with the branch card's class
    (5,6,7,8,9) passes -- outside BSS the loader does not tell the three
    apart.  check_strap2_punch.py R10-R12 pin each class.

MODE "bss" (argv[2]): a FORTRAN subprogram STRAP II punched -- program
card, common definition card, relocatable instruction and data cards,
three named commons and blank common, FORTRAN branch card -- loaded as a
BSS job, with the BSS processor's table RECONSTRUCTED by the driver (see
BSS_SOURCE's comment).  Core must equal what the same program assembled
absolute, the program at 120000 and each common at its table origin, loads
through the absolute path (strap2.punch.load).
FIRST RUN, 2026-11-12: 10 checks pass, PC at DONE, 31,707 cycles; the run
before that, comparing with the image's written mask, failed only the half
word the punch rounds over before XW (zeros on the card, the oracle's
sentinel), which is why the oracle is the absolute deck's load.
MEASURED, restored by copy and cmp:
  - i one bit wider (punch.py): 5 fail, the instruction words 120000-120004
    (every relocation after the first named-common code is misread).
  - blank common's code without its 1 0 tail: 1 fails, loaded_120002 (XW).
  - data card loading base always 0: 6 fail, the commons' data landing on
    the program (120000-01) and the four common words left sentinel.
  - CONTROL, in the reconstructed table only: the named commons' origins
    rotated -- 7 fail, every reference to and word of a named common.  So
    the loader reads the planted table, as pp.324-326 were read.

ITS OWN BUILD DIRECTORIES (build-loader, simbuild-loader): built in the
shared bsv/build without -show-schedule, it left mkStretchCore up to date
with no .sched, and the smoke test's schedule check then failed.

THE IMAGE IS LOADED FROM A FILE (gen_tb's fast_load): the LOADER image as
an inline case made bsc's code generation run nineteen hours without
finishing (2026-11-10); from a RegFile it compiles in about a minute.

"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
STRETCH = os.environ.get("STRETCH", os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(STRETCH, "strap"))
sys.path.insert(0, os.path.join(STRETCH, "tests"))

import mcp_image                                   # noqa: E402
from strap_asm import assemble                     # noqa: E402
from strap2 import compile_cards                   # noqa: E402
from gen_tb import generate                        # noqa: E402

DRIVER_AT = 0o100000        # words: free in the LOADER image (nothing below 215000)
LOW, HIGH = 0o110000, 0o130000

# The deck under test, in STRAP II.  Absolute, at 120000: forty full words
# (more than one origin card's 23 half-words, so flow cards follow), a DRZ
# (zeros the loader must write), more data, and an END with a branch address.
SOURCE = [
    "        SLC,(8)120000.0",
] + [f"        DD(BU,64),(8){(0o1010101010101010 * (k + 1)) & 0o1777777777777777777777:o}"
     for k in range(40)] + [
    "        DRZ(BU,64),3",
    "Z1      DD(BU,64),(8)7777777700000000",
    "GO      B,GO",
    "        END,GO",
]


# THE RELOCATABLE DECK (mode rel).  The same body is assembled twice: in
# PUNREL mode with an ORIGIN card for 120000, punched, and loaded by MCP's
# loader; and absolute at 120000, which is what core must then hold.
REL_BODY = [
] + ["%-8sDD(BU,64),(8)%o" % ("A" if k == 0 else "", 0o1111111111111111 * (k + 1) & ((1 << 63) - 1))
     for k in range(12)] + [
    "START   L,A",
    "        ST,TAB+2.0",
    "        B,NEXT",
    "NEXT    LVI,$2,TAB",
    "        LVI,$3,5",
    "PTR     SYN,TAB+1.0",
    "        LVI,$4,PTR",
    "X       XW,A,3,START",
    "        L(BU,24),TAB.24",
] + ["        B,START"] * 24 + [
    "TAB     DR(BU,64),3",
    "Z       DRZ(BU,64),2",
    "C       DD(BU,64),(8)4444",
    "        END,START",
]
REL_SOURCE = ["        PUNREL", "        ORIGIN,(8)120000.0"] + REL_BODY
REL_ABSOLUTE = ["        SLC,(8)120000.0"] + REL_BODY

# THE FORTRAN CARDS (mode fortran): the FORTRAN program, common definition
# and FORTRAN branch cards, in p.184's order.  Outside a BSS job each must take
# AFPCRD (ATBL, printed p.331) and the error return with code 4, ILLEGAL
# NON-BSS FUNCTION (printed p.324 lines 12-15: KSILO+2 does not hold BSS).
FORTRAN_SOURCE = [
    "        PUNFPC,LAST,0",
    "KRUM    ENTER,START",
    "        PUNCDC",
    "BLOCK1  COMBLOCK,100",
    "        PUNREL",
    "START   B,START",
    "LAST    SYN,$",
    "        FEND",
]

# THE BSS DECK (mode bss): a FORTRAN subprogram with three named commons and
# blank common, loaded as a BSS job.  RECONSTRUCTION, scaffolding for the
# lost BSS processor (C28-6379 pp.7-14; nothing of it in the listing): the
# driver plants what the loader reads from it (bss_loader_spec.md 5.4, from
# printed pp.324-326 as read) -- KSILO+2 holding BSS (ABSSID's 18 bits, p.324
# lines 13-15), KSILO+9's value field the blank common origin (p.325 line 23),
# KSILO+9.32 the relocation table's address (p.324 line 17), and the table:
# word 0 bits 28-45 the card count, bit 63 0 (not library); word 1's value
# field the program origin (line 18); word 2 bits 0-18 the number of named
# commons (line 20); the half-word at 2.0 + k.32 named common k's origin
# (p.325 lines 25-31, p.326 lines 18-25).  CHOSEN: the card count is larger
# than the deck, so the subprogram-end path (ARNRM2, p.326 l.44 on, near the
# lost p.329) is not run.
BSS_BODY = [
    "START   L,X2",
    "        LVI,$2,Y",
    "        XW,X3,2,Z",
    "        L,A",
    "        B,START",
    "A       DD(BU,64),(8)7070",
    "LAST    SYN,$",
]
BSS_COMMONS = [("", 0o121300, ["Z       DR(BU,64),2", "CL      SYN,$"]),
               ("BL1", 0o121000, ["Y       DD(BU,64),(8)1111"]),
               ("BL2", 0o121100, ["X2      DD(BU,64),(8)2222", "        DD(BU,64),(8)2223"]),
               ("BL3", 0o121200, ["X3      DD(BU,64),(8)3333"])]
BSS_SOURCE = (["        PUNFPC,LAST,CL", "KRUM    ENTER,START", "        PUNCDC",
               "BL1     COMBLOCK,1", "BL2     COMBLOCK,2", "BL3     COMBLOCK,1",
               "        PUNREL"] + BSS_BODY
              + sum([["        SLCRCOM,%s" % n] + body for n, _a, body in BSS_COMMONS], [])
              + ["        FEND"])
# The program at 120000 and each common at its origin, assembled absolute:
# what core must hold after the load.
BSS_ABSOLUTE = (["        SLC,(8)120000.0"] + BSS_BODY
                + sum([["        SLC,(8)%o.0" % at] + body for _n, at, body in BSS_COMMONS], [])
                + ["        END,START"])
BSS_TABLE = 0o107000


def card(name, stmt):
    return " " + name.ljust(8) + stmt


def compile_lines(lines):
    cards = []
    for ln in lines:
        parts = ln.split(None, 1) if not ln.startswith("        ") else ["", ln.strip()]
        name, stmt = (parts[0], parts[1]) if len(parts) == 2 else ("", parts[0])
        cards.append(card(name, stmt))
    return compile_cards(cards)


def deck():
    return compile_lines(SOURCE)


def card_words(cols):
    bits = 0
    for c in cols:
        bits = (bits << 12) | (c & 0o7777)
    return [(bits >> (64 * (14 - i))) & ((1 << 64) - 1) for i in range(15)]


def main():
    module = sys.argv[1]
    mode = sys.argv[2] if len(sys.argv) > 2 else ""
    if mode not in ("", "rel", "fortran", "bss"):
        raise SystemExit("mode: none, rel, fortran or bss, not %r" % mode)
    pages = [(mcp_image.DECK("mcp_bootstrap_p%d.strap" % n), "printed p.%d" % n)
             for n in range(99, 335)
             if n not in mcp_image.NO_DECK_PAGES | mcp_image.MISSING_PAGES]
    image, _src, _d, _e = mcp_image.build(False, pages, end_at="SDISP")
    S = image.symtab

    if mode == "fortran":
        p2 = compile_lines(FORTRAN_SOURCE)
        if p2.punch.unwritten or p2.msg.items:
            raise SystemExit("the punch: %s %s" % (p2.punch.unwritten, p2.msg.items))
        fc = [c for c in p2.punch.cards if c.kind in ("fprog", "comdef", "fbranch")]
        # Each the first card of its own job: sequence 1.
        imgs = [p2.punch._encode(c, 1, 0o1234) for c in fc]
        kinds = [c.kind for c in fc]
        expect = None
    elif mode == "bss":
        p2 = compile_lines(BSS_SOURCE)
        if p2.punch.unwritten:
            raise SystemExit("the punch did not write the deck: %s" % p2.punch.unwritten)
        imgs = p2.punch.deck_images(clock=0o1234)
        kinds = [how if how == "text" else c.kind for how, c in p2.punch.deck()]
        expect = compile_lines(BSS_ABSOLUTE)
    elif mode == "rel":
        p2 = compile_lines(REL_SOURCE)
        if p2.punch.unwritten:
            raise SystemExit("the punch did not write the deck: %s" % p2.punch.unwritten)
        if p2.msg.items:
            raise SystemExit("messages: %s" % p2.msg.items)
        # The whole deck: TYPE and LIM (B cards, a normal return, printed
        # p.320 line 27), the O card, the binary cards.
        imgs = p2.punch.deck_images(clock=0o1234)
        kinds = [how if how == "text" else c.kind for how, c in p2.punch.deck()]
        expect = compile_lines(REL_ABSOLUTE)
    else:
        p2 = deck()
        if p2.punch.unwritten:
            raise SystemExit("the punch did not write the deck: %s" % p2.punch.unwritten)
        imgs = p2.punch.images(clock=0o1234)
        kinds = [c.kind for c in p2.punch.cards]
        expect = p2

    drv = ["        SLC,(8)%o.0" % DRIVER_AT,
           "ALOADR  SYN,(8)%o.%02o" % (S["ALOADR"] // 64, S["ALOADR"] % 64),
           "YBCBU   SYN,(8)%o.%02o" % (S["YBCBU"] // 64, S["YBCBU"] % 64),
           "LOWLIM  SYN,(8)%o.0" % LOW,
           "HIGHLIM SYN,(8)%o.0" % HIGH,
           # The new-job bit, .25 of L: tested BZBZ,.57($15) (p.320
           # line 11), set the way ALOADR sets its own (p.320 line 14).
           "START   CM1111(BU,1),A0+.57"]
    for k in range(len(imgs)):
        if mode == "fortran" and k:
            drv.append("        CM1111(BU,1),A%d+.57" % k)     # a new job each card
        for w in range(15):
            drv.append("        TI,1,C%d+%d.0,YBCBU+%d.0" % (k, w, w))
        drv += ["        LVI,$15,A%d" % k,
                "        B,ALOADR",
                "A%d      VF,YBCBU" % k,
                "        ,LOWLIM",
                "        ,HIGHLIM",
                "        B,E%d" % k if mode == "fortran" else "        B,ERR",
                "D%d      VF,0" % k,
                "        B,DONE",
                "BA%d     VF,0" % k]
        if mode == "fortran":
            drv.append("        B,ERR")         # a normal return is wrong here
            drv.append("E%d      NOP" % k)       # the error return: next card
    drv += ["        B,DONE", "ERR     B,ERR", "DONE    B,DONE"]
    for k, cols in enumerate(imgs):
        drv.append("        CNOP")
        for w, v in enumerate(card_words(cols)):
            drv.append(("C%d" % k if w == 0 else "").ljust(8) + "DD(BU,64),(8)%o" % v)
    drv.append("        END,START")
    d = assemble("\n".join(drv) + "\n")

    words = dict(image.words)
    for w, v in d.words.items():
        if w in words:
            raise SystemExit("driver overlaps the image at %o" % w)
        words[w] = v
    image.words = words
    image.end_pc = d.end_pc
    if mode == "bss":
        ks = S["KSILO"] // 64
        words[ks + 2] = image.words[S["ABSSID"] // 64]
        words[ks + 9] = ((0o121300 * 64) << 40) | ((BSS_TABLE * 64) << 8)
        t = {0: 0o7777 << (63 - 45),                   # the card count
             1: (0o120000 * 64) << 40,                 # the program origin
             2: (3 << 45)}                             # three named commons
        for k, (_n, at, _b) in enumerate(BSS_COMMONS[1:], 1):
            w, half = divmod(2 * 2 + k, 2)
            t[w] = t.get(w, 0) | ((at * 64) << (40 - 32 * half))
        for w, v in t.items():
            if BSS_TABLE + w in words:
                raise SystemExit("the table overlaps the image")
            words[BSS_TABLE + w] = v

    # Every word the deck touches starts as SENTINEL, so a bit the deck
    # does not punch must come through the load unchanged.  Without it
    # those bits are Bluesim's power-on pattern, which says nothing.
    SENTINEL = 0x5555555555555555
    checks = []
    if mode == "fortran":
        # D: bits 0-11 the sequence, 13-17 the code (6728-0 p.80), a VF.
        for k in range(len(imgs)):
            dk = d.symtab["D%d" % k]
            sh = 64 - dk % 64 - 32
            want = (d.words[dk // 64] & ~(0xffffffff << sh)) | (((1 << 20) | (4 << 14)) << sh)
            checks.append(("code4_%s" % kinds[k], str(dk // 64), want))
        sys.stderr.write("cards: %s\n" % kinds)
        print(generate(module, image, checks, pc_check=d.symtab["DONE"] // 32,
                       cycle_bound=20000000, step_cap=2000000,
                       fast_load=os.path.join(os.path.abspath(STRETCH), "bsv", "build-loader",
                                              module + ".hex")))
        return
    im = expect.image
    if mode == "bss":
        # What the absolute assembly's own deck loads (punch.load, the
        # absolute path that mode "" runs on IBM's loader): the punch puts a
        # half-word rounded over before a full-word instruction on the card as
        # zeros, which the image's written mask leaves out.
        from strap2.punch import load as abs_load
        mem, _b = abs_load(expect.punch.cards)
        im = type("Loaded", (), {})()
        im._written, im._fill, im.words = {}, {}, {}
        for b, bit in mem.items():
            w, k = divmod(b, 64)
            im._written[w] = im._written.get(w, 0) | (1 << (63 - k))
            im.words[w] = im.words.get(w, 0) | (bit << (63 - k))
    touched = sorted(set(w for w, m in im._written.items() if m)
                     | set(w for w, m in im._fill.items() if m))
    full = (1 << 64) - 1
    for w in touched:
        if w in words:
            raise SystemExit("the deck overlaps the image at %o" % w)
        words[w] = SENTINEL
        wr = im._written.get(w, 0)
        fl = im._fill.get(w, 0) & ~wr
        exp = (im.words.get(w, 0) & wr) | (SENTINEL & ~(wr | fl) & full)
        kind = "loaded" if wr == full else "zeroed" if fl == full else "partial"
        checks.append(("%s_%o" % (kind, w), str(w), exp))
    if mode not in ("rel", "bss"):
        last = len(imgs) - 1
        ba = d.symtab["BA%d" % last]
        # VF,A is the half word at BA: "VF,A half-word branch address" (6728-0
        # p.80).  The loader returns the END card's address through the
        # calling sequence: SV,$1,3.($15), printed p.321 line 21 (p.323 for
        # the branch card), a 24-bit value field three words past A, i.e. BA.
        addr = p2.punch.cards[-1].address
        sh = 64 - ba % 64 - 24
        want = (d.words[ba // 64] & ~(0xffffff << sh)) | (addr << sh)
        checks.append(("branch_address_returned", str(ba // 64), want))
    sys.stderr.write("cards: %s\n" % kinds)
    sys.stderr.write("checks: %d\n" % len(checks))
    # D, the error word (bits 0-11 the card's sequence, 13-17 the code,
    # 6728-0 p.80), is written only on the error return, so each card's D
    # must still hold the driver's VF,0.  On a failure this names IBM's
    # error code (docs/bss_loader_spec.md 8.1).
    for k in range(len(imgs)):
        dk = d.symtab["D%d" % k]
        checks.append(("no_error_card_%d" % (k + 1), str(dk // 64), d.words[dk // 64]))
    print(generate(module, image, checks,
                   pc_check=d.symtab["DONE"] // 32,
                   cycle_bound=20000000, step_cap=2000000,
                   fast_load=os.path.join(os.path.abspath(STRETCH), "bsv", "build-loader",
                                          module + ".hex")))


if __name__ == "__main__":
    main()
