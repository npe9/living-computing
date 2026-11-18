#!/usr/bin/env python3
"""check_bss_mcp_go.py -- plan R2b, the job half: a GO,FORTRAN job run the
way MCP ran it, as far as IBM's code is landed.  MCP's OWN job control
reads `B TYPE,GO,FORTRAN`, turns it into a compile-and-go job whose chain
is BSS, fetches the processor-control area PCBSS and lays the chain into
KSILO (stage 1).  MCP's OWN chain step, YC4INT, and resume load then load
the reconstructed BSS processor (decks/bss_7030.strap with R2a's Example 4
input) from its disk type area "BSS" through MCP's loader, and BSS is
entered at the entry the loader leaves in SICBU (stage 3).  BSS runs under
those limits and prints C28-6379 p.17's storage map (stage 4).

STAGE 1, three TYPE cards on one compiled bench (a fast_load image swap):
  1a  `B TYPE,GO,FORTRAN`: $SCR (stub) -> UNCODE (pp.270-273) -> YTOPGO ->
      YBSSGO, p.271 ll.43-50, rewrites field 3 FORTRAN -> BSS and goes to
      YTOPCG (count 01011) -> YNORR -> p.384 ll.19-22 (KSILO+1.18-22 =
      01011, SCORG = 1) -> YCOJB1 (p.395 ll.44-56) builds "PC"+field 3 and
      calls $FETCH for PCBSS -> p.396 ll.1-28 break the PC card into KSILO
      (count 1, KSILO+1.0 = 4096-SSYRFT, KSILO+2 = BSS), set YCIDBT and
      $13, and go to YC4B5 (p.384 l.24), where the bench stops.  61,347
      cycles.  This settles R2b's open item: KSILO+1.19 = 1 is set by a
      COMPILGO-class TYPE (YTOPCG's 01011), which GO,FORTRAN becomes.
  1b  control `B TYPE,GO`: count 00100, SCORG 0, no PC fetch, KSILO untouched.
  1c  control `B TYPE,COMPILGO,FORTRAN`: no rewrite, the fetch asks for
      PCFORTRA, which this disk does not hold.
STAGE 2 (NOT RUN, PLANTED): YC4B5 -> the PC area's LIM/IOD cards through
  YRDFSO -> DECODE, TASIGN, TMOVE -> WJC4G1.  The PC area's LIM and IOD
  cards are not printed anywhere we hold, and Assign/Move need the PP
  reference tables JC1 builds.  Planted instead (SCAFFOLD): SLRBU as YL1
  (p.384 ll.36-44) leaves it for a CHOSEN `LIM,200000,214777` (the deck
  assembles at 200000; MCP's resume load clears PP memory from 41 for
  SBAPP's count, capped at YMAX = 30000, so the clear stays below the
  deck), and KSILO+8..11 as check_bss_example4 plants them.
STAGE 3: entered at YC4INT (p.396 l.30) with stage 1a's KSILO, SCORG and
  YCIDBT words copied in.  YC4INT steps the chain, YDFCS <- KSILO+2 (BSS),
  $13 <- YDKCRS, WJC4G (p.386 ll.8-31) sets YLLSAV from SLRBU, SREADS
  <- $13, primes $RESLD and gives $RET.  The stub (SCAFFOLD for MCP's
  dispatcher: unprime -> YRLTT -> YRESLD p.291 ll.45-51 -> YMPFCH) enters
  YRESL1 (p.332 l.2): SCORG = 1 -> YRESL2, YRLDTA <- YDFCS, the PP clear
  (ll.13-17), then per card YRDISK (ll.27-41) -> $FETCH (stub, reads the
  type-area image at 240000 by YDFRDA) -> YLOAD -> ALOADR (pp.320-331) ->
  ... -> the branch card -> YBCENC (p.332 l.53) -> p.333 -> $RET with
  SICBU = 200000.  137 cards, 139 $MCP calls.  SCAFFOLD/RECONSTRUCTION:
  - YEOJS is left 0, as the image has it.  p.396 l.30 BBZ,YEOJS,YCREJ
    branches on a 1, p.274 ll.44-46 set it only for $ABEOJ (KVI,$14,DABEOJ
    / BZXE,YC4B3 / CM1111,YEOJS), and C22-6728-1 p.65 (PDF 65, in the ink):
    "terminate compilation immediately if an abnormal EOJ is given (YEOJS
    = 1)".  MEASURED: planted 1, the run went YCREJ -> WJC4Q -> TMOVE.
  - YRLTT+2.50 planted 0.  The tentacle's two parameter words (p.291 l.49,
    DR(BU),(2), no value) are left by the dispatcher; C22-6728-1 p.86 (PDF
    86, read in the ink): pseudo-op 74.32 "forces resume load to use $SCR
    as a source of cards"; "the op code is checked for 74.32, or
    unconditional $SCR"; p.332 ll.10-11 zero $13 for it.  WJC4G primed $RESLD
    (66.00), so it is 0 (RECONSTRUCTION of the dispatcher's setting).
    MEASURED: left as unwritten memory (bit 50 = 1), the loader read
    through $SCR, and the error path's spool print (YPR -> YPRSPL, p.270)
    then called $MCP; the stub stops on a repeated disk address since.
  - The type area is contiguous 15-word records: YDKCRS (p.397 l.17,
    XW,-15.,0,0,7) has count 0, so p.332 l.28's end-of-arc step never
    fires for it (MEASURED: the 137th read is at 240000 + 15*136).
  - $RET to the loaded program: the stub branches to SICBU (SCAFFOLD).
  - The stub serves calls by state: the first is WJC4G's $RET; while SICBU
    holds its sentinel (only p.333 l.2 writes it) a call is a $FETCH of the
    area YRLDTA names; after, it is $RET (p.333 ll.4-5).
STAGE 4: BSS, entered by the stub at SICBU, runs to its BEW,$ halt with
  ERRC 0 and prints the p.17 map: all 10 subprogram rows, 5 common rows,
  the 43-word relocation table and KSILO+8..11 match check_bss_example4's
  expectations.  1,459,437 cycles for stages 3-4.

NOT DONE -- the map is still printed into the deck's SCAFFOLD print buffer
(OUTB), not through MCP's printer path.  $SPR (C22-6678-1 p.20, read in
the ink: B,$MCP / ,$SPR / ,FWA / ,N; 17-word lines, byte 0 carriage
control) hands lines to the output program (p.201: tentacle SCSPRT ->
CSTART), which buffers them to a tape "for processing on the IBM 1401";
NOT ATTEMPTED here: changing the deck's PRINT to call $SPR (gated so
check_bss_example4 stays as it is) is the next step; running the output
program's CSTART behind it is unexamined.

PAGES READ IN THE INK for this test (MCP listing printed page / PDF page;
MCP_Mar63_250-445 unless noted): p.250/PDF 1 (l.45 RTONRJ, ll.29-33 MCP's
own $SPR call), p.271/PDF 22 (ll.1-50, ll.43-50 YBSSGO), p.384/PDF 134,
p.386/PDF 136, p.274/PDF 25 (ll.44-46: KVI,$14,DABEOJ / BZXE,YC4B3 /
CM1111,YEOJS -- YEOJS is set for $ABEOJ only), p.333/PDF 83 (ll.1-5, and
l.26 LR,$2,KSILO+9.32), p.395/PDF 145 (ll.44-56 YCOJB1), p.396/PDF 146
(ll.1-56), p.397/PDF 147 (l.17 YDKCRS XW,-15.,0,0,7, binary 000017.00-
111 000000 000000: count 0, where YPPDKS/YPPBSD on ll.16 and 18 have 34);
p.201/PDF 208 and p.108/PDF 115 (MCP_Mar63_001-249; p.108 l.5 `D MCP
SYN,32.0` = 000040.00+); C22-6678-1 p.7 (definition card layout) and p.20
($SPR); C22-6728-1 pp.65, 86.  Lines not in this list that the run passes
through (UNCODE pp.270, 272-273, ALOADR pp.320-331, p.332) are landed,
!CHECKed deck pages read from their transcriptions here.

THE SEPARATOR.  MCP's SCA6/SBRK8 break on the 0-3-8 punch (iocd's
IOD_SUBFIELD_SEPARATOR), not Appendix F's 4-8 comma.  MEASURED: with the
4-8 comma UNCODE's compare (p.270 l.49) fails and the job goes YJOCER ->
YTCERR -> YPR -> YPRSPL.

INJECTIONS (MEASURED, observed failure sets):
  R2G_TAMPER=abssid -- ABSSID (p.291 l.8) spelled BSX: exactly the eight
    1a checks fail (PC area name, M, KSILO count, KSILO+1, KSILO+2,
    YCIDBT, $13, the stop at YC4B5); 1b and 1c pass; stages 3-4 are
    skipped.
  R2G_TAMPER=order -- type-area cards 41 and 42 swapped: the loader reads
    41 cards and stops (p.322 l.42, sequence error); the fetch count, last
    address, call count, SICBU and entry checks fail and all 22 stage-4
    checks fail (27 in all); YRLDTA's check passes.
  Controls: 1b and 1c above.

Run with PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=../strap:. from tests/.
R2G_PCLOG=1|2 (a PC log through job control / the loader) and R2G_KEEP
(keep the bench output): diagnosis only.
"""
import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "strap"))
sys.path.insert(0, HERE)
import cards                                        # noqa: E402
import iocd                                         # noqa: E402
import mcp_image                                    # noqa: E402
import prosa_dict                                   # noqa: E402
from strap_asm import assemble                      # noqa: E402
from gen_tb import generate                         # noqa: E402

BSV = os.path.join(HERE, "..", "bsv")
BSC_DIR = "/opt/homebrew/Cellar/bsc/2026.01"
DRIVER_AT = 0o100000
SENT = 0x5555555555555555
# R2G_PCLOG (diagnosis only): the PC through $EOJ and job control
PC_LOG = [(0o20000 * 2, 0o24000 * 2), (0o231000 * 2, 0o231777 * 2 + 1)]
PC_LOG2 = PC_LOG + [(0o234424 * 2, 0o235264 * 2), (0o235267 * 2, 0o235500 * 2)]
fails = 0


def check(label, got, want):
    global fails
    ok = got == want
    fails += not ok
    print(f"{'PASS' if ok else 'FAIL'} {label}" + ("" if ok else f": got {got!r}, want {want!r}"))


def field(word, first, length):
    """Bits first..first+length-1 of a 64-bit word, bit 0 the leftmost."""
    if word is None:
        return None
    return (word >> (64 - first - length)) & ((1 << length) - 1)


def a6(name):
    return prosa_dict.a6(name.ljust(8)[:8])


_IMAGE = None


def image():
    """The resident MCP and the LOADER (printed pp.99-334) with the $EOJ
    overlay (pp.381-439, PUNID 22$EOJ, low core 020031 on).  SCOMD and
    $DUMP (pp.335-380) share the LOADER's addresses and are left out."""
    global _IMAGE
    if _IMAGE is None:
        pg = mcp_image.pages(99, 334) + mcp_image.pages(381, 439)
        _IMAGE = mcp_image.build(False, pg, end_at="SDISP")[0]
    return _IMAGE


def sym(S, nm, extra=0, alias=None):
    v = S[nm] + extra
    return "%-8sSYN,(8)%o.%02o" % (alias or nm, v // 64, v % 64)


def run_bench(tmp, module, progs, reads, stop_hw, step_cap, cycle_bound=40000000,
              mem_dump=None):
    """Build ONE bench and run it on each of `progs` in turn.  The image is
    read at simulation start from a hex file (gen_tb's fast_load, a
    mkRegFileLoad), so programs that load the same set of words differ only
    in that file: it is rewritten and the same simulator rerun.  `reads` are
    (label, word) pairs: the bench prints each word (its expected value is a
    dummy 0) and the values are judged here, field by field.  Returns a list
    of ({label: value}, output), or (None, error) for a build failure."""
    checks = [(lab, str(w), 0) for lab, w in reads]
    hexf = os.path.join(tmp, module + ".hex")
    kw = dict(step_cap=step_cap, cycle_bound=cycle_bound, stop_at_pc=stop_hw,
              fast_load=hexf, mem_dump=mem_dump,
              pc_log={"1": PC_LOG, "2": PC_LOG2}.get(os.environ.get("R2G_PCLOG", "")))
    src = generate(module, progs[0], checks, **kw)
    with open(os.path.join(BSV, module + ".bsv"), "w") as fh:
        fh.write(src)
    env = dict(os.environ, BLUESPECDIR=BSC_DIR + "/libexec/lib",
               PATH=BSC_DIR + "/bin:" + os.environ.get("PATH", ""))
    for sub in ("build-loader", "simbuild-loader"):
        os.makedirs(os.path.join(BSV, sub), exist_ok=True)
    results = []
    try:
        for args in (["-sim", "-simdir", "simbuild-loader", "-bdir", "build-loader",
                      "-info-dir", "build-loader", "-g", "mk" + module, "-u", module + ".bsv"],
                     ["-sim", "-simdir", "simbuild-loader", "-bdir", "build-loader",
                      "-e", "mk" + module, "-o", module + "_sim"]):
            r = subprocess.run([BSC_DIR + "/bin/bsc"] + args + ["+RTS", "-K512m", "-RTS"],
                               cwd=BSV, env=env, capture_output=True, text=True)
            if r.returncode:
                return [(None, r.stdout + r.stderr)]
        for k, prog in enumerate(progs):
            if k:
                assert sorted(prog.words) == sorted(progs[0].words), "a different word set"
                assert generate(module, prog, checks, **kw) == src
            r = subprocess.run(["./" + module + "_sim"], cwd=BSV, env=env,
                               capture_output=True, text=True)
            out = r.stdout + r.stderr
            if os.environ.get("R2G_KEEP"):
                with open("%s.%s.%d" % (os.environ["R2G_KEEP"], module, k), "w") as fh:
                    fh.write(out)
            got = {}
            for lab, _w in reads:
                m = re.search(r"^(?:PASS|FAIL) %s = (\d+) " % re.escape(lab), out, re.M)
                got[lab] = int(m.group(1)) if m else None
            m = re.search(r"STOPPED DELIBERATELY at half-word (\d+) after (\d+) steps", out)
            got["_stopped"] = int(m.group(1)) if m else None
            m = re.search(r"cycles = (\d+)", out)
            got["_cycles"] = int(m.group(1)) if m else None
            got["_mem"] = {int(a): int(v, 16) for a, v in re.findall(r"MEMDUMP (\d+) ([0-9a-f]+)", out)}
            results.append((got, out))
    finally:
        for name in os.listdir(BSV):        # by exact name, never a glob
            if name in (module + ".bsv", module + "_sim", module + "_sim.so"):
                os.remove(os.path.join(BSV, name))
    return results


# ---- stage 1: the TYPE card to the PC area's chain in KSILO ---------------
# The TYPE card, as C22-6678-1 printed p.7 (PDF 7, read in the ink) lays a
# definition card out: B in column 1, name in 2-9, the statement from column
# 10, its subfields separated by commas.
def type_card(statement):
    # The separator is punched 0-3-8, the punch MCP's own SCA6 and SBRK8
    # break on -- measured on the model in strap/iocd.py, where Appendix F's
    # 4-8 comma leaves the field unbroken.  MEASURED HERE TOO, 2026-11-17:
    # with 4-8, YUCBF2 field 1 read "TYPE", 4-8's code, "GO", the compare
    # with YTYPMK (p.270 l.49) failed, and UNCODE took YUER (p.273 l.22).
    return "B        " + statement.replace(",", iocd.IOD_SUBFIELD_SEPARATOR)


# The PC area's first card: RECONSTRUCTION.  p.396 ll.4-12 convert 80
# columns and break from column 2 (YUCBF1+.6, CF,71.), so the names start in
# column 2; what column 1 holds is unprinted (CHOSEN blank).  Only the name's
# first three characters are fixed, BSS (p.332 ll.4-5 KF(BU,18),ABSSID;
# p.397 l.1 KFI,YBSSID): the BSS processor's type-area name "BSS" is CHOSEN.
PC_NAME = "PCBSS   "
PC_CARD = " BSS"
BSS_PROC = "BSS     "


def stage1_prog(card_text, pc_cards):
    """The image, the TYPE card in the $SCR stub, the PC area in $FETCH's."""
    im = image()
    S = im.symtab
    words = dict(im.words)
    card = cards.card_words(card_text)
    npc = 15 * len(pc_cards)
    drv = ["        SLC,32.0",
           "        B,SDMCP",
           "        SLC,(8)%o.0" % DRIVER_AT,
           sym(S, "YTCSR"), sym(S, "YBCBU"), sym(S, "SJCTWS"), sym(S, "YCIODC"),
           sym(S, "YTCINF"), sym(S, "YDFCTA"),
           "KSILO1  SYN,(8)%o.0" % (S["KSILO"] // 64 + 1),
           "YDFCW   SYN,(8)%o.0" % (S["YDFCTA"] // 64),
           "SCORGW  SYN,(8)%o.0" % (S["SCORG"] // 64),
           # the $SCR stub's normal return: past ,YBCBU / ,1.0 / ,0 / B,YC4B
           # (p.384 ll.8-11; C22-6678-1 p.20's $SCR: FWA, N, M, end, normal)
           sym(S, "YTCSR", 3 * 64, "RSCR"),
           # $FETCH's normal return: past YCIODC (M), B,YTCERR (error, p.396
           # l.1) and NOP (end, l.2) -- p.396 l.3
           sym(S, "YCIODC", 64 + 32, "RFETCH"),
           "START   B,YTCSR",
           # B,DMCP leaves no return address (MCP finds the caller through
           # the IF trap, boot_plan.md); the stub serves the calls this
           # path makes, IN ORDER, and anything more is BADC.
           "SDMCP   LX,$1,NCALL",
           # SNAP: words copied at each call (diagnosis and checks)
           "        SX,$2,SNAPX2",
           "        LX,$2,SNAPP",
           "        L(BU,64),YTCINF",
           "        ST(BU,64),0($2)",
           "        L(BU,64),YDFCW",
           "        ST(BU,64),1.0($2)",
           "        L(BU,64),YDFCW+1.0",
           "        ST(BU,64),2.0($2)",
           "        L(BU,64),SCORGW",
           "        ST(BU,64),3.0($2)",
           "        L(BU,64),KSILO1",
           "        ST(BU,64),4.0($2)",
           "        V+I,$2,5.0",
           "        SX,$2,SNAPP",
           "        LX,$2,SNAPX2",
           "        V+I,$1,.32",
           "        SX,$1,NCALL",
           "        B,CTAB-.32($1)",
           "CTAB    B,SCR",
           "        B,FETCH",
           "        B,BADC",
           "        B,BADC",
           "BADC    B,BADC"]
    drv.append("SCR     NOP")
    for k in range(15):
        drv += ["        L(BU,64),CARD+%d.0" % k, "        ST(BU,64),YBCBU+%d.0" % k]
    drv += ["        B,RSCR",
            # The disk holds ONE PC area: a fetch of any other name stops
            # at BADF (and so does a call from anywhere but p.395 l.50,
            # whose YDFCTA is then not that name).
            "FETCH   L(BU,48),YDFCTA",
            "        KF(BU,48),PCNM",
            "        BZAE,BADF",
            "        L(BU,24),SJCTWS",          # FWA: LVE,,SJCTWS (p.395 l.54)
            "        ST(BU,24),TMPV",
            "        LV,$2,TMPV"]
    for k in range(npc):
        drv += ["        L(BU,64),PC+%d.0" % k, "        ST(BU,64),%d.0($2)" % k]
    # N = 0 (p.395 l.55): "fetch will read in all of the specified
    # type-area", and M "will then contain the number of full words that
    # were actually transmitted" (C22-6678-1 p.21, docs/mcp_macros.md)
    drv += ["        LI(BU,18),%d" % npc,
            "        ST(BU,18),YCIODC",
            "        B,RFETCH",
            "        CNOP",
            "BADF    B,BADF",
            "        CNOP",
            "PCNM    DD(BU,64),(16)%016X" % (a6(PC_NAME) << 16),
            "NCALL   XW,0",
            "TMPV    XW,0",
            "SNAPX2  XW,0",
            "SNAPP   XW,SNAP",
            "SNAP    DRZ(BU,64),20",
            "PCNAME  DR(BU,64),1"]
    drv += [("CARD" if i == 0 else "").ljust(8) + "DD(BU,64),(16)%016X" % v
            for i, v in enumerate(card)]
    pcw = [v for t in pc_cards for v in cards.card_words(t)]
    drv += [("PC" if i == 0 else "").ljust(8) + "DD(BU,64),(16)%016X" % v
            for i, v in enumerate(pcw or [0])]
    drv.append("        END,START")
    d = assemble("\n".join(drv) + "\n")
    for w, v in d.words.items():
        if w in words:
            raise SystemExit("the stub overlaps the image at %o" % w)
        words[w] = v
    ks = S["KSILO"] // 64
    for w in (ks, ks + 1, ks + 2, ks + 7):     # KSILO is DR(BU,64) (p.171)
        assert not words.get(w), "KSILO+%d holds a word in the image" % (w - ks)
        words[w] = SENT
    im2 = type(im).__new__(type(im))
    im2.__dict__.update(im.__dict__)
    im2.words = words
    im2.end_pc = d.end_pc
    return im2, d


# The cases, on one bench: the GO,FORTRAN job, then the controls.
CASES = [("GO,FORTRAN", "TYPE,GO,FORTRAN"),
         ("GO alone", "TYPE,GO"),
         ("COMPILGO,FORTRAN", "TYPE,COMPILGO,FORTRAN")]


def tamper_image(words, S):
    """R2G_TAMPER, measurement only: an injected fault in IBM's words."""
    t = os.environ.get("R2G_TAMPER")
    if t == "abssid":       # ABSSID (p.291 l.8) spelled BSX: the GO,FORTRAN
        w = S["ABSSID"] // 64        # rewrite still runs, the name changes
        words[w] = (prosa_dict.a6("BSX     ") << 16) | (words[w] & 0xFFFF)
    elif t and t != "order":
        raise SystemExit("R2G_TAMPER: abssid or order, not %r" % t)


def stage1(tmp):
    im = image()
    S = im.symtab
    at = lambda nm, extra=0: (S[nm] // 64) + extra    # noqa: E731
    progs = []
    for _lab, statement in CASES:
        prog, d = stage1_prog(type_card(statement), [PC_CARD])
        tamper_image(prog.words, S)
        progs.append(prog)
    reads = [("ksilo0", at("KSILO")), ("ksilo1", at("KSILO", 1)), ("ksilo2", at("KSILO", 2)),
             ("ksilo7", at("KSILO", 7)), ("ytcinf", at("YTCINF")),
             ("scorg", at("SCORG")), ("ycidbt", at("YCIDBT")), ("ycd773", at("YDFCTA")),
             ("ycd774", at("YDFCTA", 1)), ("yciodc", at("YCIODC")), ("x13", 16 + 13),
             ("ncall", d.symtab["NCALL"] // 64), ("ssyrft", S["SSYRFT"] // 64),
             ("sjctws", S["SJCTWS"] // 64), ("yeojs", S["YEOJS"] // 64)]
    reads += [("snap%d" % i, d.symtab["SNAP"] // 64 + i) for i in range(10)]
    res = run_bench(tmp, "StretchBssGoTypeTb", progs, reads,
                    stop_hw=S["YC4B5"] // 32, step_cap=400000)
    return res, S, d


def judge1(res, S, d):
    """The checks of stage 1, from the words each case's bench printed."""
    if res[0][0] is None:
        check("stage 1: the bench built", res[0][1][-2000:], "")
        return None
    hw = lambda nm: S[nm] // 32                          # noqa: E731
    name = lambda g: (field(g["ycd773"], 32, 32) << 16) | field(g["ycd774"], 0, 16)  # noqa: E731
    ncall = lambda g: field(g["ncall"], 0, 24) // 32     # noqa: E731
    out = {}
    for (lab, statement), (g, o) in zip(CASES, res):
        out[lab] = g
        print(f"INFO stage 1, {statement}: stopped at {g['_stopped']}, {g['_cycles']} cycles,"
              f" {ncall(g)} $MCP call(s)")
        info = field(g["ytcinf"], 28, 18)               # UNCODE's $12 count (p.273 l.30)
        if lab == "GO,FORTRAN":
            check("1a: UNCODE's normal return, count 01011 (YTOPCG, p.272 l.4)", info, 0b01011)
            check("1a: KSILO+1.18-22 = 01011 (p.384 ll.19-20), so KSILO+1.19 = 1",
                  field(g["ksilo1"], 18, 5), 0b01011)
            check("1a: SCORG = 1 (p.384 l.21 CM1010 at offset 2: a compile-and-go job)",
                  field(g["scorg"], 3, 1), 1)
            check("1a: the PC area fetched is PCBSS (p.395 ll.47-49 on p.271's rewrite)",
                  name(g), a6("PCBSS   "))
            check("1a: two $MCP calls, $SCR then $FETCH", ncall(g), 2)
            check("1a: KSILO+7 zeroed (p.395 l.46)", g["ksilo7"], 0)
            check("1a: M = 15, one card's words (the stub's)", field(g["yciodc"], 0, 18), 15)
            check("1a: KSILO.0-17 = 1, one compiler (p.396 ll.16-18)", field(g["ksilo0"], 0, 18), 1)
            check("1a: KSILO+1.0-17 = 4096 - SSYRFT (p.396 ll.19-21)",
                  field(g["ksilo1"], 0, 18), (4096 - field(g["ssyrft"], 32, 18)) % (1 << 18))
            check("1a: KSILO+2.0-47 = the PC card's name BSS (p.396 l.22)",
                  field(g["ksilo2"], 0, 48), a6(BSS_PROC))
            check("1a: YCIDBT set (p.396 l.23)", field(g["ycidbt"], 48, 1), 1)
            src = field(g["sjctws"], 0, 24) + 15 * 64
            check("1a: $13 = the PC area past its first card, count M, bit 25 (ll.24-27)",
                  (field(g["x13"], 0, 24), field(g["x13"], 28, 18), field(g["x13"], 25, 1)),
                  (src, 15, 1))
            check("1a: stopped at YC4B5 (p.396 l.28 -> p.384 l.24)", g["_stopped"], hw("YC4B5"))
        elif lab == "GO alone":
            check("1b control: count 00100 (YTOPGO, p.271 l.24; YBSSGO l.45 to YNORR)",
                  info, 0b00100)
            check("1b control: KSILO+1.18-22 = 00100, KSILO+1.19 = 0", field(g["ksilo1"], 18, 5),
                  0b00100)
            check("1b control: SCORG = 0", field(g["scorg"], 3, 1), 0)
            check("1b control: no PC area fetched, one $MCP call", (name(g), ncall(g)),
                  (field(S_IMG_WORDS(S, "YDFCTA", 0), 32, 32) << 16
                   | field(S_IMG_WORDS(S, "YDFCTA", 1), 0, 16), 1))
            check("1b control: KSILO untouched", (g["ksilo0"], g["ksilo2"]), (SENT, SENT))
            check("1b control: stopped at YC4B5 (p.384 ll.22-24)", g["_stopped"], hw("YC4B5"))
        else:
            check("1c control: count 01011 (YTOPCG via p.271 l.31)", info, 0b01011)
            check("1c control: SCORG = 1", field(g["scorg"], 3, 1), 1)
            check("1c control: the fetch asks for PCFORTRA (no BSS rewrite)", name(g),
                  a6("PCFORTRA"))
            check("1c control: ... which the disk does not hold: never at YC4B5",
                  g["_stopped"], None)
    return out


def S_IMG_WORDS(S, nm, k):
    return image().words.get(S[nm] // 64 + k, 0)


# ---- stages 3 and 4: the BSS processor loaded by MCP from its type area,
# entered, run ----------------------------------------------------------------
AREA_AT = 0o240000           # the type area "BSS     " on disk, a core image (SCAFFOLD)
DRV2_AT = 0o250000           # the stub, above PP memory and MCP (installed: 0-277777)
SICS = 0x3333333333333333    # SICBU's sentinel (written only by p.333 l.2)
LIM_A, LIM_B = 0o200000, 0o214777    # the processor's limits: CHOSEN (see header)


def bss_deck():
    """The RECONSTRUCTED BSS processor (decks/bss_7030.strap) with R2a's
    Example 4 input, punched by the host STRAP II as an absolute binary
    deck.  The KSILO+8..11 lines check_bss_example4 appends are taken out:
    a deck loaded under limits cannot reach KSILO; they are planted."""
    import check_bss_example4 as ex4
    import strap_asm
    from strap2 import compile_cards
    from strap2.cards import deck_cards
    src, exp = ex4.build()
    lines = src.splitlines()
    k = lines.index("        SLC, (8)%o.0" % (ex4.KSILO + 8))
    ks = lines[k + 1:k + 5]
    assert all(x.startswith("        DD(BU,64), (16)") for x in ks)
    kwords = [int(x.split("(16)")[1], 16) for x in ks]
    src = "\n".join(lines[:k] + lines[k + 5:]) + "\n"
    p2 = compile_cards(deck_cards(src), strap_asm.DEFAULT_ORIGIN_BITS)
    assert not p2.msg.items and not p2.punch.unwritten
    return p2, p2.punch.images(clock=0o1234), kwords, exp


def stage34_prog(state, deck_imgs, kwords):
    """The image as stage 1 left KSILO and SCORG, the gap PLANTED, the type
    area BSS on the disk image, and the stub."""
    import check_bss_example4 as ex4
    im = image()
    S = im.symtab
    words = dict(im.words)
    at = lambda nm, extra=0: (S[nm] // 64) + extra    # noqa: E731
    if os.environ.get("R2G_TAMPER") == "order":   # measurement only:
        deck_imgs = list(deck_imgs)                # cards 40 and 41 swapped
        deck_imgs[40], deck_imgs[41] = deck_imgs[41], deck_imgs[40]
    area = [v for cols in deck_imgs for v in ex4.card_words(cols)]
    assert AREA_AT + len(area) < DRV2_AT
    plant = {AREA_AT + i: v for i, v in enumerate(area)}
    # What stage 1 left (run 1a's words, copied).
    for lab, w in (("ksilo0", at("KSILO")), ("ksilo1", at("KSILO", 1)),
                   ("ksilo2", at("KSILO", 2)), ("ksilo7", at("KSILO", 7)),
                   ("scorg", at("SCORG")), ("ycidbt", at("YCIDBT"))):
        plant[w] = state[lab]
    # THE GAP, PLANTED (SCAFFOLD): p.384 YC4B5 .. p.386 WJC4G1 is not run.
    # YEOJS is left as the image has it, 0: p.396 l.30 BBZ takes the branch
    # to YCREJ on a 1 (and zeroes it), and p.274 ll.44-46 set it only for
    # $ABEOJ (C22-6728-1 PDF 65: "terminate compilation immediately if an
    # abnormal EOJ is given (YEOJS = 1)").  MEASURED: planted 1, the run
    # went YCREJ -> WJC4Q -> TMOVE (p.386 l.44, p.423) and never loaded BSS.
    assert not (words.get(at("YEOJS"), 0) >> (63 - S["YEOJS"] % 64)) & 1
    # SLRBU and SBAPP as p.384 ll.36-44 (YL1) leave them for a LIM card
    # LIM,A,B: SV A at SLRBU+.32, SC B at SLRBU, SBAPP's count B capped at
    # YMAX (ll.41-44).
    w = at("SLRBU")
    v = words.get(w, 0) & ~((0o777777 << 46) | (0o777777 << 14))
    plant[w] = v | (LIM_B << 46) | (LIM_A << 14)
    w = at("SBAPP")
    plant[w] = (words.get(w, 0) & ~(0o777777 << 46)) | (min(LIM_B, S["YMAX"] // 64) << 46)
    # KSILO+8..11 as check_bss_example4 plants them for BSS (U, sentinels).
    for i, v in enumerate(kwords):
        plant[at("KSILO", 8 + i)] = v
    # YRLTT+2.50: the tentacle's parameter words (p.291 l.49 DR(BU),(2), no
    # value) say which pseudo-op entered resume load; 74.32 "forces resume
    # load to use $SCR as a source of cards" (C22-6728-1 PDF 86), and p.332
    # ll.10-11 zero $13 for it.  WJC4G primed $RESLD (66.00), so MCP's
    # dispatcher (not run) would leave it 0.  SCAFFOLD; MEASURED: left as
    # unwritten memory (bit 50 = 1), the loader read through $SCR.
    w = at("YRLTT", 2)
    plant[w] = words.get(w, 0) & ~(1 << (63 - 50))
    plant[at("SICBU")] = SICS
    for w2, v in plant.items():
        words[w2] = v
    sy = lambda nm, extra=0, al=None: sym(S, nm, extra, al)   # noqa: E731
    drv = ["        SLC,32.0",
           "        B,SDMCP",
           "        SLC,(8)%o.0" % DRV2_AT,
           sy("YC4INT"), sy("YRESL1"), sy("YLOAD"), sy("YLOAD", -32, "RYLOAD"),
           sy("YRLDTA"), sy("YDFRDA"), sy("YBCBU"), sy("SICBU"),
           sy("MR4"), sy("MPQR"),
           "START   B,YC4INT",
           "SDMCP   LX,$1,NCALL",
           "        V+I,$1,.32",
           "        SX,$1,NCALL",
           "        KVI,$1,.32",
           "        BXE,DISP",
           "        L(BU,64),SICBU",
           "        K(BU,64),SICW",
           "        BAE,SFETCH",
           "        B,ENTER",
           # MCP's dispatcher (SCAFFOLD): WJC4G primed $RESLD (p.386 ll.23-25)
           # and gave $RET (ll.30-31); MCP unprimes it -- YRLTT (p.291 l.45),
           # YRESLD (l.50), YMPFCH fetches the LOADER -- whose entry runs
           # p.332 l.2.  The prime control and queue are copied for the check.
           "DISP    L(BU,64),MR4",
           "        ST(BU,64),QSNAP",
           "        L(BU,64),MPQR",
           "        ST(BU,64),QSNAP+1.0"]
    for k in range(6):
        drv += ["        L(BU,64),(8)215646.0+%d.0" % k, "        ST(BU,64),QSNAP+%d.0" % (k + 2)]
    drv += ["        B,YRESL1",
            "SFETCH  SX,$1,SAV1",
            "        L(BU,48),YRLDTA",
            "        KF(BU,48),BSSNM",
            "        BZAE,NOAREA",
            "        L(BU,24),YDFRDA",
            "        ST(BU,24),TMPV",
            "        LV,$1,TMPV",
            "        KV,$1,LENA",
            "        BXL,$+1.0",
            "        B,FEND",
            "        V+I,$1,(8)%o.0" % AREA_AT,
            # a repeated address is not a loader read (an error path's
            # $MCP call, e.g. YPRSPL's spool print): stop there
            "        KV,$1,LASTF",
            "        BXE,BADF",
            "        SX,$1,LASTF",
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
            "        B,RYLOAD",
            "NOAREA  B,NOAREA",
            "BADF    B,BADF",
            # $RET after the load (p.333 ll.4-5): MCP enters the program at
            # SICBU (SCAFFOLD for MCP's $RET to a loaded processor).
            "ENTER   LV,$1,SICBU",
            "        SX,$1,ENTRYX",
            "        B,0($1)",
            "        CNOP",
            "NCALL   XW,0",
            "SAV1    XW,0",
            "SAV2    XW,0",
            "TMPV    XW,0",
            "LASTF   XW,0",
            "ENTRYX  XW,0",
            "LENA    XW,%d.0" % len(area),
            "LOGP    XW,LOG",
            "SICW    DD(BU,64),(16)%016X" % SICS,
            "BSSNM   DD(BU,64),(16)%016X" % (a6(BSS_PROC) << 16),
            "QSNAP   DRZ(BU,64),8",
            "LOG     DRZ(BU,64),200",
            "        END,START"]
    d = assemble("\n".join(drv) + "\n")
    for w2, v in d.words.items():
        if w2 in words:
            raise SystemExit("the stub overlaps at %o" % w2)
        words[w2] = v
    im2 = type(im).__new__(type(im))
    im2.__dict__.update(im.__dict__)
    im2.words = words
    im2.end_pc = d.end_pc
    return im2, d, len(area)


def stage34(tmp, state):
    p2, imgs, kwords, exp = bss_deck()
    sym2 = lambda n: p2.val.symbol_value(p2.st.search(n))[0]   # noqa: E731
    prog, d, nwords = stage34_prog(state, imgs, kwords)
    tamper_image(prog.words, image().symtab)
    S = image().symtab
    at = lambda nm, extra=0: (S[nm] // 64) + extra    # noqa: E731
    reads = [("sicbu", at("SICBU")), ("entryx", d.symtab["ENTRYX"] // 64),
             ("logp", d.symtab["LOGP"] // 64), ("ncall", d.symtab["NCALL"] // 64),
             ("lastf", d.symtab["LASTF"] // 64),
             ("ydfcs", at("YDFCS")), ("yrldta", at("YRLDTA")), ("yljslt", at("YLJSLT")),
             ("errc", sym2("ERRC") // 64), ("outn", sym2("OUTN") // 64)]
    reads += [("q%d" % i, d.symtab["QSNAP"] // 64 + i) for i in range(8)]
    reads += [("ks%d" % i, at("KSILO", i)) for i in range(12)]
    halt = None                          # the deck's BEW,$ halt (core.halted())
    reads += [("x13", 29), ("sreads", at("SREADS")), ("yrltt2", at("YRLTT", 2)),
              ("ydfrda", at("YDFRDA"))]
    res = run_bench(tmp, "StretchBssGoLoadTb", [prog], reads, stop_hw=halt,
                    step_cap=8000000, cycle_bound=60000000,
                    mem_dump=(0o200000, 0o14000))
    return res, p2, imgs, exp, d, sym2


def main():
    with tempfile.TemporaryDirectory() as tmp:
        res, S, d = stage1(tmp)
        st = judge1(res, S, d)
        if st is None or fails:
            print("SKIP stages 3-4: they start from stage 1's KSILO")
        else:
            judge34(*stage34(tmp, st["GO,FORTRAN"]))
    print("ALL CHECKS PASSED" if not fails else f"{fails} FAILED")
    return 1 if fails else 0


def judge34(res, p2, imgs, exp, d, sym2):
    import check_bss_example4 as ex4
    g, out = res[0]
    if g is None:
        check("stage 3: the bench ran", out[-2000:], "")
        return
    mem = g.get("_mem", {})
    S = image().symtab
    print(f"INFO stage 3/4: {g.get('_cycles')} cycles")
    # Stage 3: MCP's resume load.
    log0 = d.symtab["LOG"] // 64
    nread = field(g["logp"], 0, 18) - log0
    check(f"3: the loader read all {len(imgs)} cards of the type area, one $FETCH each",
          nread, len(imgs))
    check("3: ... the last at the area's last card (15-word records, no gap: YDKCRS count 0)",
          field(g["lastf"], 0, 18), AREA_AT + 15 * (len(imgs) - 1))
    check("3: $MCP calls: $RET (WJC4G), the fetches, $RET (p.333 l.5)",
          field(g["ncall"], 0, 19), 1 + len(imgs) + 1)
    check("3: YRLDTA = YDFCS = the area named BSS (p.332 l.8, p.396 l.40)",
          field(g["yrldta"], 0, 48), a6(BSS_PROC))
    check("3: SICBU = the deck's branch-card entry, BSS at 200000 (p.333 l.2)",
          field(g["sicbu"], 0, 24), sym2("BSS") // 64 << 6)
    check("3: ... entered there", field(g["entryx"], 0, 24), sym2("BSS") // 64 << 6)
    # Stage 4: the processor's own run, judged as check_bss_example4 judges it.
    def text(at, nwords):
        return "".join(ex4.A8INV.get((mem.get(at + i, 0) >> (56 - 8 * k)) & 255, "?")
                       for i in range(nwords) for k in range(8))
    check("4: BSS's ERRC = 0 at its halt (map printed, tables and KSILO set)",
          field(g["errc"], 0, 8), 0)
    n = field(g["outn"], 0, 18)
    lines = [text(sym2("OUTB") // 64 + 15 * i, 15) for i in range(n or 0)]
    check("4: 12 lines in OUTB", len(lines), 12)
    subs, coms, seps = ex4.map_rows(lines)
    for k, want in enumerate(ex4.MAP_SUB):
        check(f"4: p.17 subprogram row {k + 1}: {' '.join(want)}",
              subs[k] if k < len(subs) else None, want)
    for k, want in enumerate(ex4.MAP_COM):
        check(f"4: p.17 common row {k + 1}: {' '.join(w for w in want if w)}",
              coms[k] if k < len(coms) else None, want)
    b0, b1 = exp["table_span"]
    bad = [f"{a:o}" for a in range(b0, b1) if mem.get(a, 0) != exp["table"].get(a, 0)]
    check(f"4: the relocation table, {b1 - b0} words at {b0:o}", bad, [])
    ks = S["KSILO"] // 64
    for a, v in sorted(exp["ksilo"].items()):
        check(f"4: KSILO+{a - ks} = {v:016x}", g.get("ks%d" % (a - ks)), v)


if __name__ == "__main__":
    sys.exit(main())
