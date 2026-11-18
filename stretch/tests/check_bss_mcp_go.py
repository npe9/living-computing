#!/usr/bin/env python3
"""check_bss_mcp_go.py -- plan R2b, the job half: a GO,FORTRAN job run the
way MCP ran it, as far as IBM's code is landed.  MCP's OWN job control
reads `B TYPE,GO,FORTRAN`, turns it into a compile-and-go job whose chain
is BSS, fetches the processor-control area PCBSS and lays the chain into
KSILO (stage 1).  MCP's OWN chain step, YC4INT, and resume load then load
the reconstructed BSS processor (decks/bss_7030.strap with R2a's Example 4
input) from its disk type area "BSS" through MCP's loader, and BSS is
entered at the entry the loader leaves in SICBU (stage 3).  BSS runs under
those limits and prints C28-6379 p.17's storage map THROUGH MCP's $SPR,
whose IF trap, tentacle table and print program CSTART are IBM's code
(stage 4), and leaves by $EOJ into MCP's own YC4NO (stage 5), from where
MCP's $EOJ program, fetched back from disk by YMPFCH, runs job control to
TASIGN (stage 6).

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
  SICBU = 200000.  140 cards since the deck's $SPR/$EOJ code (137 before),
  142 $MCP calls.  SCAFFOLD/RECONSTRUCTION:
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
STAGE 4: the deck with SPRSW = 1 (its PRINT goes to PRSPR, one 17-word
  $SPR line a call: byte 0 single space, LINE in bytes 1-120, blanks to
  135; C22-6678-1 p.20).  The stub enters BSS (SCAFFOLD for MCP's $RET to
  the PP) with SL = 0, the interruption address at the stub's table ITAB,
  the boundaries IPL's XBOUND sets (p.33 ll.51-52, PDF 40: only 32.0
  protected),
  MCP's mask SLRMCP+9.0 (the IF bit) and BE.  So each B,$MCP / ,$SPR is
  suppressed and traps IF (RefMan printed p.32, from the OCR) into ITAB+21 (SIC,STIC /
  BD,STUBIF, MCP's own p.111 ll.1-3 shape, PDF 118).  STUBIF, SCAFFOLD for SIFAE
  (p.117): ll.5-6 and 9-10 as printed (save the low registers in STLR,
  $2 = STIC, $3 = the op), then NOT ll.20-28 (MCP bounds and mask; l.28's
  STLR -> SLRBU would overwrite SLRBU's planted PP limits with this bench's
  32-33 bounds) but the same copy into its own PPSAV, and B,MIF6+.32.
  From there IBM's code runs: p.117 ll.36-48 (the tentacle SCSPRT from
  MIFTTT+3.32, user bit = SL = 0, SL set to MCP), p.118 ll.1-24 (linkage
  FWA, normal return, $OP and the two parameters into SCSPRT+2.32..3.32),
  MTC1-MTC3A (ll.26-40, enabled entry), and the print program p.203 ll.21-56
  CSTART: ACHK checks FWA and FWA+17N against SPPLB/SPPUB (SLRBU), and
  CTRANS moves 16 full words and 5 bytes of each line into buffer X,
  LF(BU,64,8) -> SF(BU,48,6): 133 six-bit characters a line, each A8 byte
  without its two high bits.  CSTART's ARET (p.201 ll.51-54) $RET traps IF
  again; STUBIF's IRET (SCAFFOLD for MCP's return routine) sets SL = 0,
  restores registers 8-31 from PPSAV and BE's to the normal return p.118
  l.6 left in SCSPRT+1.32.  ENTER begins with a BD: MCP's stage 3 may
  leave the system enabled.  MEASURED (R2G_TAMPER=nobd, the BD a NOP):
  BSS is never entered (ENTRYX unwritten), no ITAB entry is taken, and
  38 checks fail; the cause is NOT isolated.  (The first run, before ITAB
  was word-aligned, went into YBCBU with OP.)
  Checks: 12 $SPR traps and 12 $RET traps, no other op or interrupt; OUTB
  unwritten; the tentacle's linkage, return, FWA and user bit; after the
  12th line (CNUM = 12, p.209 l.49; C22-6728-1 PDF 170: "Each physical
  printer record contains twelve full lines") CBTA = 1, CWA refilled to
  buffer Y (CY+.6, count 12), CBWA = 0, so no $W was issued: the record
  waits for the next $SPR (CAOS3A) or the output EOJ (CEOJ; pp.202-204,
  from the transcriptions), which are not run; the $W path was not
  examined beyond them.  Buffer X decoded 6 bits a character: byte 0 '-' on every line,
  bytes 121-132 blank, and every p.17 row, header and '**' as
  check_bss_example4 judges OUTB; the 43-word table and KSILO 8-11 too.
  The call's ,$SPR and ,1. half words equal MCP's own p.203 ll.13, 15
  (000103.40 80, 000001.00 80).
STAGE 5: BSS's normal end, B,$MCP / ,$EOJ (C22-6678-1 p.22), traps the
  same way; STUBIF takes MCP's path for 65.0 (and 68.0) through MIF6+.32:
  the tentacle YJC4TT (MIFTTT+1.0, N = 1, enabled entry) and p.274's
  YC4NO: LVE,$14 (65.0), YLLSAV.25 = 0 (not spurious), SMAXRN count 0 so
  no PP I/O wait, KVI,$14,DABEOJ not equal -> YC4B3 (l.51 LX,$1,YXWEJM /
  B,YMPFCH).  YEOJS stays 0.
STAGE 6, $EOJ past YC4B3 (2026-11-18).  YMPFCH, "SPECIAL PACKAGE TO PULL
  MCP PROGRAMS FROM THE DISK" (p.269 ll.13-36, PDF 20, read in the ink),
  takes YXWEJM (l.40, XW,YEOJTA,YPPMEM: name $EOJ, FWA 020000), saves the
  name in YMPSAV, sets YFHBR to YEOJTA's BE,YPPMEM and calls B,DMCP /
  ,DFETCH with the name 22$EOJ, RELFWA 0, FWA 020000, N 0, M (C22-6678-1
  p.21).  B,DMCP traps IF as the PP's calls do; STUBIF serves $FETCH
  (DFETCH SYN,66.32, p.105 l.36), SCAFFOLD for MCP's disk fetch: it checks
  the name and FWA, copies the type area "22$EOJ" -- planted at 260000 as
  the core image of the landed pp.381-439, 020000-023233, unwritten words 0
  (CHOSEN) -- sets M = 1692, restores registers 8-31 from STLR and returns
  enabled to the normal return.  The fetch is needed: word 020000 was 0 at
  the call (resume load's PP clear, "PP memory is cleared from location
  41.(8) TO SBAPP", C22-6728-1 p.86, PDF 86, read in the ink).  Then IBM's code: p.381 (PDF 131) l.11
  $14 = 65.0, not SJC4; ll.13-14 SIT+20..47 <- FWIT (MARKER: SIT+20..47
  planted with the sentinel, which the image otherwise assembles equal to
  FWIT); l.17 SCORG = 1 -> YC4INT; p.396 ll.32-35 the pointer 2 > count 1
  -> YLASTC: SCORG = 0, KSILO+7.25 (the reject flag, C22-6728 p.197) 0,
  KSILO+1.19 = 1, YDFCS <- '))))))))' (p.397 l.19); p.397 (PDF 147) ll.1-9:
  KSILO+2 is BSS, SYSMOD = 00 (overlap): $15 = WJ4PFF, YTSP set, TJUNAS
  (p.434, PDF 184): TMAXRF's count 0 -> TJEND, SPROGS 0 -> YC4BZ (pp.436-
  437, transcriptions) -> WJ4PFF (p.388, PDF 138): SCNFCG 1 as assembled,
  so BZBZ clears it, CM1111(BU,1),WJCW marks a configuration change, and
  LVI,$15,WJCW / B,TASIGN, where the bench stops (p.398 l.31).  Stages 3-6:
  1,677,355 cycles.
  WHAT BLOCKS TASIGN, MEASURED (the stop removed, R2G_PCLOG=1): TA9 (p.406
  l.35) walks the channel status table at SXCHAN, which IPL builds; here it
  is p.103 l.28's assembled XW,0 (base 0, count 0) in the image (not read
  at the halt).  OBSERVED in the PC trace: TASIGN -> TA9 -> TCM9, TA9A,
  T9M, TB9, TA9D, TA9E loops -> TA9F -> MCP's own T N BD,$ at 021725.00,
  "MACH CONF CH. ASSIGN BIT ON - MULTI" (p.410 l.52, PDF 160).  INFERRED,
  not observed: the scan walked a table based at 0, so the halt is an
  artifact of the missing table.  Without a configuration change TASIGN walks JC1's PP
  reference table TSAV instead, not built either (stage 2).
  Left as the image assembles them (SCAFFOLD): SCNFCG 1, SYSMOD 00, TMAXRF
  0, SPROGS 0; KSILO+7 is 0 (p.395 l.46 zeroes it; the reconstructed BSS
  does not set 7.0-7.17, "Number of arcs occupied by compiled program",
  C22-6728 p.197).
STAGE 0 (no bench): p.20's five carriage-control characters (Restore 1,
  Single -, Double J, Triple K, Quadruple L, with their "Binary
  Representation") are strap2/a8.py's A8 codes; and A6 (the six bits the
  print program keeps) tells every A8 character apart.  The A8 48-set
  codes are all below 0o100, so the six bits are the code itself: '1' =
  000001, '-' = 100000, 'J' = 100001 are BCD's B-A-8-4-2-1 rows.  What the
  1401 does with the tape is not read here (the 1401 peripheral output
  program is not landed).

PAGES READ IN THE INK for this test (MCP listing printed page / PDF page;
MCP_Mar63_250-445 unless noted).  For stages 4-5, 2026-11-18: MCP_Mar63_
001-249 p.33/PDF 40 (ll.35-53, X377's $IA, LWF(U),XBOUND / ST(BU),$UB,64),
p.111/PDF 118 (ll.1-8, SIT+21's SIC,STIC / BD,SIFAE), p.116/PDF 123 (ll.12-
31, STLR, SLRBU, SPPUB/SPPLB, SLRMCP, l.28 INDMK,$IF), p.121/PDF 128 (ll.1-
13, MIFTTT: 65.0 YJC4TT, 67.32 SCSPRT, 68.0 YJC4TT), p.117/PDF 124 (ll.1-48, SIFAE, SIFAD, MIF6), p.118/PDF 125 (ll.1-50,
the tentacle setup, MTC1-MTC4A), p.201/PDF 208 (ll.1-11 SCSPRT, ll.44-56 ARET, ARET1), p.203/PDF
210 (ll.1-56: ACHK, ACHERR, $SPR's ,$SPR / ,1., CSTART..CAOS3B),
p.209/PDF 216 (ll.42-56: CNUM SYN,12., CWX, CWY, CWA, CWT, CWW, CX), p.210/
PDF 217 (ll.1-28 and 39-54: CY, CXR7, ASERR, the record control characters, "X=(133*6*CNUM+5)/64",
CBTA, CFILL, CBWA, APPERR, CATUB); MCP_Mar63_250-445 p.274/PDF 25 (ll.21-
52, YEOJS, YC4NO..YC4B3); C22-6678-1 p.20 (the $SPR line and its control
table) and p.22 ($EOJ).  Earlier: p.250/PDF 1 (l.45 RTONRJ, ll.29-33 MCP's
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

INJECTIONS (MEASURED, observed failure sets; R2G_TAMPER, no file edited;
all re-run 2026-11-18 on the stage-6 bench (stop at TASIGN), control run
all pass.  judge6 has 12 checks; two pass under EVERY injection below and
are consistency checks, not discriminating: "word 020000 was 0 at the
fetch" (PREW is never written when no fetch comes) and "KSILO's link
pointer still 1" (stage 3 leaves it 1).  "the ten stage-6 checks" below
are the other ten):
  nofetch -- STUBIF's $FETCH copies nothing (its ST a NOP): 7 fail: the
    $EOJ program in core, SIT+20..47, SCORG, YDFCS, YTSP, SCNFCG/WJCW, the
    stop at TASIGN; YMPSAV, YFHBR, M and word 020000 = 0 pass (YMPFCH ran).
  eojl17 -- p.381 l.17 BB,SCORG,YC4INT as BZB (on the disk copy too): 6
    fail: l.18 on runs, and its B,DMCP / ,SKOM traps as an unserved op
    (BADOPX = 79.32): "no other op", SCORG, YDFCS, YTSP, SCNFCG/WJCW, the
    stop; SIT+20..47 and the fetch checks pass.
  yxwejm -- p.269 l.40 XW,YEOJTA,YPPMEM as XW,YDBTA,YPPMEM: the fetch asks
    for $DUMP and the stub stops at BADF2: 10 fail: YMPSAV ($DUMP), YFHBR
    (YDBBEG), M, the program in core, SIT, SCORG, YDFCS, YTSP, SCNFCG/WJCW,
    the stop; stage 5's checks pass.
  nocc -- PRSPR stores LINE at byte 0 (no control byte): 18 fail: byte 0,
    header 2, all 10 subprogram rows, all 5 common rows, rows 6-10/'**'.
    Header 1 passes (its words survive a one-column shift).  Stages 5-6
    pass.
  fwa -- the call's FWA outside the PP limits (220000): ACHK -> ACHERR
    (SPRIME primes the error print and $ABEOJ, p.203 ll.11-18); 8 $SPR and 7
    $RET traps, BSS never finishes: 40 fail (ERRC, OUTN, the trap counts,
    FWA, CBTA, CWA, every buffer-line check, four stage-5 checks, all ten
    stage-6 checks); the
    table and KSILO 8-11 (written before the map), the linkage, return
    and user bit, CBWA, P and YEOJS pass.
  lci15 -- p.203 l.36 LCI,$9,16 as 15 (15 full words a line): 19 fail:
    byte 0, bytes 121-132, header 2, every row; header 1 passes.  Stages
    5-6 pass.
  bs8 -- p.203 l.39 SF(BU,48,6) as SF(BU,48,8): 20 fail: every buffer-line
    check (byte 0, padding, both headers, all rows).  Stages 5-6 pass.
  nobd -- ENTER's BD a NOP: 48 fail (see STAGE 4): the entry and every
    stage-4 check but five (OUTB unwritten, the call's half words, the user
    bit, CBWA, P); stage 5's trap count, linkage, fetch and $14 (YLLSAV,
    SMAXRN and YEOJS pass); all ten stage-6 checks.
  abeoj -- BSS leaves by $ABEOJ (68.0): MCP takes p.274 ll.46-48 (YEOJS =
    1, B,DMCP / BE,DDUMP), whose $DUMP (64.0) the stub does not serve: 14
    fail: the "no other op" check (BADOPX = 64.0), stage 5's fetch, $14
    and YEOJS, all ten stage-6 checks.
  R2G_TAMPER=abssid -- ABSSID (p.291 l.8) spelled BSX: exactly the eight
    1a checks fail (PC area name, M, KSILO count, KSILO+1, KSILO+2,
    YCIDBT, $13, the stop at YC4B5); 1b and 1c pass; stages 3-4 are
    skipped.
  R2G_TAMPER=order -- type-area cards 41 and 42 swapped: the loader reads
    41 cards and stops (p.322 l.42, sequence error); the fetch count, last
    address, call count, SICBU and entry checks fail, and so does every
    stage-4, -5 and -6 check but eight (OUTB unwritten, the call's half
    words, CBWA, P, SMAXRN, YEOJS, and stage 6's two consistency checks):
    54 in all; YRLDTA's check passes.
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
from strap2.a8 import A8, A6                        # noqa: E402

# The six-bit code the print program stores (p.203 l.39 SF(BU,48,6) of
# LF(BU,64,8) bytes): each A8 byte without its two high bits.
A6INV = {}
for _c, _v in A6.items():
    A6INV.setdefault(_v, _c)

BSV = os.path.join(HERE, "..", "bsv")
BSC_DIR = "/opt/homebrew/Cellar/bsc/2026.01"
DRIVER_AT = 0o100000
SENT = 0x5555555555555555
# R2G_PCLOG (diagnosis only): the PC through $EOJ and job control
PC_LOG = [(0o20000 * 2, 0o24000 * 2), (0o231000 * 2, 0o231777 * 2 + 1)]
PC_LOG2 = PC_LOG + [(0o234424 * 2, 0o235264 * 2), (0o235267 * 2, 0o235500 * 2)]
# R2G_PCLOG=3 (diagnosis only): the stage-3 stub, the IF analyzer and the
# print program
PC_LOG3 = [(0o250000 * 2, 0o252000 * 2), (0o215470 * 2, 0o215572 * 2),
           (0o222104 * 2, 0o222400 * 2)]
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
              pc_log={"1": PC_LOG, "2": PC_LOG2, "3": PC_LOG3}.get(os.environ.get("R2G_PCLOG", "")))
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
    elif t in IMAGE_TAMPERS:  # one statement of IBM's code reassembled
        a, nbits, stmt = IMAGE_TAMPERS[t]
        p = assemble("        SLC,(8)%o.%02o\n        %s\n" % (a // 64, a % 64, stmt))
        e0 = S["YPPMEM"] // 64
        for b in range(a, a + nbits):
            w, m = b // 64, 1 << (63 - b % 64)
            words[w] = (words[w] & ~m) | (p.words.get(w, 0) & m)
            # a word of the $EOJ program is changed on its disk copy too,
            # which is what YMPFCH's $FETCH brings back (stage 6)
            if e0 <= w < 0o40000 and EOJ_AT + w - e0 in words:
                c = EOJ_AT + w - e0
                words[c] = (words[c] & ~m) | (p.words.get(w, 0) & m)
    elif t and t not in ("order", "nocc", "fwa", "abeoj", "nobd", "nofetch"):
        raise SystemExit("R2G_TAMPER: abssid, order, nocc, fwa, abeoj or %s, not %r"
                         % (", ".join(IMAGE_TAMPERS), t))


# R2G_TAMPER (measurement only), the print program as p.203 (PDF 210, read
# in the ink) prints it: l.36 LCI,$9,16 at 222242.00 with 15 full words a
# line; l.39's six-bit store SF(BU,48,6)(V+I),.48($8) at 222244.40 with
# eight-bit bytes.
IMAGE_TAMPERS = {"lci15": (0o222242 * 64, 32, "LCI,$9,15"),
                 "bs8": (0o222244 * 64 + 32, 64, "SF(BU,48,8)(V+I),.48($8)"),
                 # p.381 l.17 (PDF 131) at 020004.00: BB,SCORG,YC4INT as BZB
                 "eojl17": (0o20004 * 64, 64, "BZB,(8)215001.03,(8)21017.40"),
                 # p.269 l.40 YXWEJM XW,YEOJTA,YPPMEM as XW,YDBTA,YPPMEM: the
                 # fetch asks for $DUMP's area (YDBTA, p.269 l.49)
                 "yxwejm": (0o231162 * 64, 64, "XW,(8)231167.0,(8)20000.")}


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
EOJ_AT = 0o260000            # the type area "22$EOJ" on disk, a core image (SCAFFOLD)
EOJ_NAME = "22$EOJ  "        # p.269 ll.24, 52-54: YFDO's "22" and YEOJTA's "$EOJ  "
TWS_NAME = "))))))))"        # p.397 l.19 YTWSTA, the compiled program's type area
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
    # The print through $SPR: the deck's switch, as a test sets TWSA.
    sw = "SPRSW   DD(BU,64), 0\n"
    assert src.count(sw) == 1
    src = src.replace(sw, "SPRSW   DD(BU,64), (16)8000000000000000\n")
    if os.environ.get("R2G_TAMPER") == "nocc":     # measurement only: the
        old = "        ST(BU,64), .8($9)\n"        # control byte left out,
        assert src.count(old) == 1                 # LINE at byte 0
        src = src.replace(old, "        ST(BU,64), 0($9)\n")
    elif os.environ.get("R2G_TAMPER") == "fwa":    # FWA outside the limits
        old = "        , SPRL\n"
        assert src.count(old) == 1
        src = src.replace(old, "        , (8)220000.0\n")
    elif os.environ.get("R2G_TAMPER") == "abeoj":  # BSS leaves by $ABEOJ
        old = "        , $EOJ\n"
        assert src.count(old) == 1
        src = src.replace(old, "        , $ABEOJ\n")
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
    # The $EOJ program's type area (SCAFFOLD): the core image of the landed
    # pp.381-439 from YPPMEM (020000) to END (023233), the words the image
    # leaves unwritten as 0 (CHOSEN).  YMPFCH's $FETCH copies it to its FWA.
    e0 = S["YPPMEM"] // 64
    e1 = max(w for w in words if e0 <= w < 0o40000) + 1
    for i in range(e1 - e0):
        plant[EOJ_AT + i] = words.get(e0 + i, 0)
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
    # MARKER: SIT+20..47 (MCP's own interruption table; this bench's $IA is
    # the stub's ITAB, so nothing else reads them) hold the sentinel, so
    # p.381 ll.13-14's restore from FWIT is seen (the image assembles them
    # equal).
    for k in range(20, 48):
        plant[at("SIT", k)] = SENT
    for w2, v in plant.items():
        words[w2] = v
    sy = lambda nm, extra=0, al=None: sym(S, nm, extra, al)   # noqa: E731
    drv = ["        SLC,32.0",
           "        B,SDMCP",
           "        SLC,(8)%o.0" % DRV2_AT,
           sy("YC4INT"), sy("YRESL1"), sy("YLOAD"), sy("YLOAD", -32, "RYLOAD"),
           sy("YRLDTA"), sy("YDFRDA"), sy("YBCBU"), sy("SICBU"),
           sy("MR4"), sy("MPQR"),
           sy("STIC"), sy("STLR"), sy("SL"), sy("MIF6"), sy("SCSPRT"),
           sy("SLRMCP"), sy("MCR"),
           sy("YPPMEM"), sy("YFHFWA"), sy("YFHFWA", 2 * 64 + 32, "RDFET"),
           "YFHTAW  SYN,(8)%o.0" % (S["YFHTA"] // 64),
           "START   B,YC4INT",
           # After ENTER every $MCP call traps IF (ITAB) -- the PP's, and
           # from stage 6 MCP's own B,DMCP / ,DFETCH (STUBIF's IFETCH); one
           # that reaches 32.0 is not expected: stop.
           "SDMCP   BB,RUNF,LATE",
           "        LX,$1,NCALL",
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
            # ... with the PP's state (SCAFFOLD, CHOSEN): level bit SL = 0 (PP;
            # p.117 l.39 copies it to the user bit, p.203 l.28 checks the
            # parameters only for PP), the interruption address at this
            # stub's table (ITAB), word 32.0 the only protected address
            # (the boundaries MCP's IPL sets, p.33 ll.51-52: XBOUND VF,33.0 /
            # VF,32.0, upper 33, lower 32, control bit 0), MCP's mask
            # (SLRMCP+9.0: the image's word, the IF bit; p.116 l.28 INDMK,$IF),
            # and entered enabled, so B,$MCP is suppressed and traps IF
            # (RefMan printed p.32, from the OCR).
            "ENTER   BD,$+.32" if os.environ.get("R2G_TAMPER") != "nobd" else "ENTER   NOP",
            "        CM0000(BU,1),SL",
            "        LVI,$1,ITAB",
            "        SV,$1,$IA",
            "        LWF(U),BNDW",
            "        ST(BU),$UB,64",
            "        LWF(U),SLRMCP+9.0",
            "        ST(U),$MASK",
            "        CM1111(BU,1),RUNF",
            "        LV,$1,SICBU",
            "        SX,$1,ENTRYX",
            "        BE,0($1)",
            # THE IF TRAP (ITAB+21: SIC,STIC / BD,STUBIF, as MCP's own
            # p.111 ll.1-3 with SIFAE).  SCAFFOLD for SIFAE (p.117 ll.5-29),
            # IBM's instructions where they are used: ll.5-6 save the low
            # registers in STLR, ll.9-10 the op.  $SPR from PP: ll.20-28 are
            # NOT run (MCP's bounds and mask, and l.28's STLR -> SLRBU, which
            # would overwrite SLRBU's planted PP limits with this bench's
            # 32-33 boundaries); the PP's registers go to PPSAV instead, and
            # MCP's own code takes over at MIF6+.32 (p.117 l.36): the tentacle
            # table (p.117 ll.36-48, p.118 ll.1-24), MTC1-MTC3A (ll.26-40)
            # and the print program CSTART (pp.203-204), enabled.
            "STUBIF  TI,14,3.0,STLR",
            "        TI,15,17.0,STLR+14.0",
            "        LV,2,STIC",
            "        LVE,3,0.0($2)",
            "        KVI,3,67.32",
            "        BXE,ISPR",
            "        KVI,3,65.0",
            "        BXE,IEOJ",
            "        KVI,3,68.0",
            "        BXE,IEOJ",
            "        KVI,3,33.0",
            "        BXE,IRET",
            "        KVI,3,66.32",
            "        BXE,IFETCH",
            "        SX,$3,BADOPX",
            "BADOP   B,BADOP",
            "IEOJ    L(BU,18),NEOJ",
            "        +I(BU,18),1",
            "        ST(BU,18),NEOJ",
            "        B,IPP",
            "ISPR    L(BU,18),NSPR",
            "        +I(BU,18),1",
            "        ST(BU,18),NSPR",
            "IPP     LCI,15,30",
            "        T,15,STLR,PPSAV",
            "        B,MIF6+.32",
            # $RET from CSTART's ARET (p.201 ll.53-54): SCAFFOLD for MCP's
            # return routine.  Back to the PP at the normal return p.118 l.6
            # left in SCSPRT+1.32, the PP's registers 8-31 restored, SL = 0,
            # enabled.
            "IRET    L(BU,18),NRET",
            "        +I(BU,18),1",
            "        ST(BU,18),NRET",
            "        CM0000(BU,1),SL",
            "        LV,$1,SCSPRT+1.32",
            "        SVA,$1,RETB",
            "        TI,24,PPSAV+5.0,8.0",
            "RETB    BE,0",
            # $FETCH (DFETCH SYN,66.32, p.105 l.36) from MCP's own code
            # after the PP has run: B,DMCP traps IF as the PP's calls do.
            # SCAFFOLD for MCP's DFETCH.  The first must be YMPFCH's fetch of
            # the $EOJ program (p.269 ll.22-29, from YC4B3, p.274 ll.51-52):
            # name, RELFWA, FWA, N, M (C22-6678-1 p.21); N = 0, so the whole
            # area is read and M is its word count; registers 8-31 restored
            # from STLR, back enabled to the normal return.  A second $FETCH
            # is served by no stub: the run stops at TWSF.
            "IFETCH  L(BU,18),NFET",
            "        +I(BU,18),1",
            "        ST(BU,18),NFET",
            "        KI(BU,18),1",
            "        BZAE,FET2",
            "        L(BU,64),STIC",
            "        ST(BU,64),FSTC1",
            "        L(BU,64),STLR+27.0",
            "        ST(BU,64),FX14",
            "        L(BU,64),YPPMEM",
            "        ST(BU,64),PREW",
            "        L(BU,48),YFHTAW",
            "        KF(BU,48),EOJNM",
            "        BZAE,BADF2",
            "        LV,$2,YFHFWA",
            "        KV,$2,PPMW",
            "        BXE,$+1.0",
            "        B,BADF2",
            "        LVI,$1,(8)%o.0" % EOJ_AT,
            "MFL     L(BU,64),0($1)",
            "        ST(BU,64),0($2)" if os.environ.get("R2G_TAMPER") != "nofetch"
            else "        NOP",
            "        V+I,$1,1.0",
            "        V+I,$2,1.0",
            "        KV,$1,EOJE",
            "        BXL,MFL",
            "        LI(BU,18),%d" % (e1 - e0),
            "        ST(BU,18),YFHFWA+1.0",
            "        TI,24,STLR+5.0,8.0",
            "        BE,RDFET",
            "FET2    L(BU,64),STIC",
            "        ST(BU,64),FSTC2",
            "TWSF    B,TWSF",
            "BADF2   B,BADF2",
            "LATE    B,LATE",
            "BADI    B,BADI",
            "        CNOP",
            "NCALL   XW,0",
            "SAV1    XW,0",
            "SAV2    XW,0",
            "TMPV    XW,0",
            "LASTF   XW,0",
            "ENTRYX  XW,0",
            "LENA    XW,%d.0" % len(area),
            "PPMW    XW,YPPMEM",
            "EOJE    XW,(8)%o.0" % (EOJ_AT + e1 - e0),
            "EOJNM   DD(BU,64),(16)%016X" % (a6(EOJ_NAME) << 16),
            "NFET    DRZ(BU,64),1",
            "FSTC1   DRZ(BU,64),1",
            "FSTC2   DRZ(BU,64),1",
            "FX14    DRZ(BU,64),1",
            "PREW    DRZ(BU,64),1",
            "FNAM1   DRZ(BU,64),1",
            "LOGP    XW,LOG",
            "SICW    DD(BU,64),(16)%016X" % SICS,
            "BSSNM   DD(BU,64),(16)%016X" % (a6(BSS_PROC) << 16),
            "QSNAP   DRZ(BU,64),8",
            "RUNF    DRZ(BU,64),1",
            "NSPR    DRZ(BU,64),1",
            "NRET    DRZ(BU,64),1",
            "NEOJ    DRZ(BU,64),1",
            "BADOPX  DRZ(BU,64),1",
            "BADIC   DRZ(BU,64),64",
            "BNDW    VF,33.0",
            "        VF,32.0",
            "        CNOP",
            "PPSAV   DRZ(BU,64),30",
            "LOG     DRZ(BU,64),200",
            "ITAB    SYN,$"]
    for k in range(64):     # the interruption table: IF to STUBIF, else BADI
        drv += ["        SIC,STIC" if k == 21 else "        SIC,BADIC+%d.0" % k,
                "        BD,STUBIF" if k == 21 else "        BD,BADI"]
    drv += ["        END,START"]
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
    # The stop: YC4B3 (p.274 l.51), where MCP's $EOJ (entered at YC4NO
    # through the tentacle YJC4TT) goes on to the chain's next link by
    # YMPFCH.  A deck that halts instead (BEW,$) stops on core.halted().
    halt = S["TASIGN"] // 32
    reads += [("x13", 29), ("sreads", at("SREADS")), ("yrltt2", at("YRLTT", 2)),
              ("ydfrda", at("YDFRDA"))]
    reads += [(nm.lower(), d.symtab[nm] // 64) for nm in ("NSPR", "NRET", "BADOPX", "NEOJ")]
    reads += [("x14", 16 + 14), ("yeojs", at("YEOJS")), ("yllsav", at("YLLSAV")),
              ("smaxrn", at("SMAXRN"))]
    reads += [("jc4t%d" % i, at("YJC4TT", i)) for i in range(3)]
    # Stage 6: $EOJ past YC4B3 (the stub's record and IBM's words)
    reads += [(nm.lower(), d.symtab[nm] // 64)
              for nm in ("NFET", "FSTC1", "FSTC2", "FX14", "PREW")]
    reads += [(nm.lower(), at(nm)) for nm in
              ("YMPSAV", "YFHBR", "XNFOST", "CBUFF", "CFOT", "SCORG", "YDFCS", "SSYRFT",
               "SDKMCP", "YTSP", "TMAXRF", "WJCW", "SLRBU", "SBAPP", "YEDLL", "SPROGS",
               "SCNFCG", "JHBIT", "YPPMEM")]
    reads += [("yfhm", at("YFHFWA", 1)), ("yi4ta", at("YI4TA")), ("yi4ta1", at("YI4TA", 1)),
              ("x15", 31), ("x1", 17)]
    reads += [("sit%d" % k, at("SIT", k)) for k in range(20, 48)]
    reads += [("fwit%d" % k, at("FWIT", k)) for k in range(28)]
    reads += [("badic%d" % k, d.symtab["BADIC"] // 64 + k) for k in range(64)]
    reads += [("tent%d" % i, at("SCSPRT", i)) for i in range(4)]
    reads += [("cwa", at("CWA")), ("cbta", at("CBTA")), ("cbwa", at("CBWA")),
              ("sl", at("SL"))]
    # the dump: the deck (200000-214777) and the output program's print
    # buffers CX and CY (p.209 l.56 - p.210 l.3), up to 223177
    res = run_bench(tmp, "StretchBssGoLoadTb", [prog], reads, stop_hw=halt,
                    step_cap=8000000, cycle_bound=60000000,
                    mem_dump=(0o200000, 0o23200))
    return res, p2, imgs, exp, d, sym2


# C22-6678-1 printed p.20 (PDF 20, read in the ink): $SPR's carriage control,
# "Binary Representation" and "8-Bit BCD Code".
P20_CONTROL = [("Restore", "00000001", "1"), ("Single Space", "00100000", "-"),
               ("Double Space", "00100001", "J"), ("Triple Space", "00100010", "K"),
               ("Quadruple Space", "00100011", "L")]


def judge0():
    """The character code, against p.20, before any bench runs."""
    check("0: p.20's five control characters are A8 as strap2/a8.py has it",
          [(f, oct(A8[c])) for f, _b, c in P20_CONTROL],
          [(f, oct(int(b, 2))) for f, b, _c in P20_CONTROL])
    # p.20: "The 132 bytes which follow, must be 8-bit BCD (A8)"; the print
    # program keeps six bits of each (p.203 l.39).  So a character survives
    # only if no two A8 characters share their low six bits.
    s48 = [c for c, v in A8.items() if c != ";"]
    clash = sorted({c for c in s48 for e in s48 if c < e and A6[c] == A6[e]})
    check("0: A6 (A8 without its two high bits) tells every A8 character apart", clash, [])


def main():
    judge0()
    with tempfile.TemporaryDirectory() as tmp:
        res, S, d = stage1(tmp)
        st = judge1(res, S, d)
        if st is None or fails:
            print("SKIP stages 3-4: they start from stage 1's KSILO")
        else:
            judge34(*stage34(tmp, st["GO,FORTRAN"]))
    print("ALL CHECKS PASSED" if not fails else f"{fails} FAILED")
    return 1 if fails else 0


def judge6(g, S):
    """Stage 6: $EOJ past YC4B3, IBM's code from YMPFCH to TASIGN."""
    eoj = a6(EOJ_NAME)
    n_eoj = max(w for w in image().words if S["YPPMEM"] // 64 <= w < 0o40000) + 1 \
        - S["YPPMEM"] // 64
    check("6: YMPFCH saved the name $EOJ in YMPSAV (p.269 ll.15-17, YEOJTA p.269 l.54)",
          field(g["ympsav"], 0, 36), eoj & ((1 << 36) - 1))
    check("6: YFHBR's address = YPPMEM, the area's entry (p.269 ll.18-19, l.53 BE,YPPMEM)",
          field(g["yfhbr"], 0, 19), S["YPPMEM"] // 32)
    check("6: word 020000 was 0 at the fetch: resume load's PP clear (p.332 ll.13-17) had"
          " wiped the $EOJ program", g["prew"], 0)
    check("6: M = %d, the whole area (N = 0, C22-6678-1 p.21)" % n_eoj,
          field(g["yfhm"], 32, 18), n_eoj)
    check("6: the $EOJ program is in core again (word 020000, p.381 l.11)",
          g["yppmem"], image().words[S["YPPMEM"] // 64])
    check("6: SIT+20..47 restored from FWIT (p.381 ll.13-14)",
          [g["sit%d" % k] for k in range(20, 48)], [g["fwit%d" % k] for k in range(28)])
    check("6: SCORG = 0, the GO phase (p.381 l.17 BB,SCORG,YC4INT; p.396 l.47 YLASTC)",
          field(g["scorg"], S["SCORG"] % 64, 1), 0)
    check("6: KSILO's link pointer still 1, so YC4INT took YLASTC (p.396 ll.32-35)",
          field(g["ks0"], 32, 18), 1)
    check("6: YDFCS = '))))))))', the compiled program's type area (p.396 ll.50-51,"
          " p.397 l.19)", field(g["ydfcs"], 0, 48), a6(TWS_NAME))
    check("6: YTSP set: a BSS chain, overlap mode (p.397 ll.1-8; SYSMOD = 00)",
          field(g["ytsp"], S["YTSP"] % 64, 1), 1)
    check("6: SCNFCG cleared and WJCW's flag set: a configuration change (p.388 ll.28-29)",
          (field(g["scnfcg"], S["SCNFCG"] % 64, 1),
           field(g["wjcw"], 0, 1)), (0, 1))
    check("6: stopped at TASIGN (p.398 l.31) with $15 = WJCW (p.388 ll.30-31), the I-O"
          " assignment the job's tables are not built for",
          (g["_stopped"], field(g["x15"], 0, 24)), (S["TASIGN"] // 32, S["WJCW"]))


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
    # Stage 4: the processor's own run, its map through $SPR into MCP's
    # print buffer, judged as check_bss_example4 judges OUTB.
    def text(at, nwords):
        return "".join(ex4.A8INV.get((mem.get(at + i, 0) >> (56 - 8 * k)) & 255, "?")
                       for i in range(nwords) for k in range(8))

    def bits(bit0, n):
        """n bits from absolute bit address bit0 of the dump."""
        v = 0
        for b in range(bit0, bit0 + n):
            w = mem.get(b // 64)
            v = (v << 1) | ((w >> (63 - b % 64)) & 1 if w is not None else 0)
        return v

    def six(bit0, nchars):
        return "".join(A6INV.get(bits(bit0 + 6 * c, 6), "?") for c in range(nchars))
    check("4: BSS's ERRC = 0 at its halt (map printed, tables and KSILO set)",
          field(g["errc"], 0, 8), 0)
    check("4: PRINT counted 12 lines (OUTN)", field(g["outn"], 0, 18), 12)
    check("4: 12 IF traps of $SPR, 12 of $RET; no other op, no other interrupt",
          (field(g["nspr"], 0, 18), field(g["nret"], 0, 18), g["badopx"],
           [k for k in range(64) if g["badic%d" % k]]),
          (12, 12, 0, []))
    check("4: OUTB not written (the print went to $SPR)",
          "SUBPROGRAMS" in text(sym2("OUTB") // 64, 15), False)
    spl = sym2("SPRC")
    # The call as assembled, against MCP's own $SPR call printed p.203
    # ll.13-15 (PDF 210, read in the ink): ,$SPR 000103.40 80; ,1. 000001.00 80.
    def half(hw):
        w = p2.image.words[hw // 2]
        return "%08x" % ((w >> 32) & 0xFFFFFFFF if hw % 2 == 0 else w & 0xFFFFFFFF)
    check("4: the call's ,$SPR and ,1. half words as p.203 ll.13, 15 print them",
          (half(spl // 32 + 1), half(spl // 32 + 3)), ("0010e080", "00004080"))
    check("4: tentacle SCSPRT+2.0 = the linkage FWA, the B,$MCP (p.118 l.1)",
          field(g["tent2"], 0, 19), spl // 32)
    check("4: tentacle SCSPRT+1.32 = the normal return, past ,N (p.118 ll.3-6)",
          field(g["tent1"], 32, 19), spl // 32 + 4)
    check("4: tentacle SCSPRT+3.0 = FWA SPRL (p.118 ll.12-13, p.203 l.23)",
          field(g["tent3"], 0, 18), sym2("SPRL") // 64)
    check("4: tentacle user bit SCSPRT.4 = 0, PP (p.117 l.44): ACHK ran (p.203 l.28)",
          field(g["tent0"], 4, 1), 0)
    cx, cy = S["CX"], S["CY"]
    check("4: CBTA = 1: buffer X full after 12 lines, CNUM (p.203 ll.43-47; p.209 l.49)",
          field(g["cbta"], S["CBTA"] % 64, 1), 1)
    check("4: CWA refilled to buffer Y: CY+.6, count 12 (p.203 ll.48, 50; p.209 l.55)",
          (field(g["cwa"], 0, 24), field(g["cwa"], 28, 18)), (cy + 6, 12))
    check("4: CBWA = 0: no write buffer in use, so no $W (p.203 l.52)",
          field(g["cbwa"], S["CBWA"] % 64, 1), 0)
    check("4: buffer X's record control character P untouched (p.209 l.56)",
          bits(cx, 6), A6["P"])
    lines = [six(cx + 6 + 798 * i, 133) for i in range(12)]
    check("4: every line's byte 0 is the single-space control '-' (C22-6678-1 p.20)",
          [ln[0] for ln in lines], ["-"] * 12)
    check("4: bytes 121-132 of every line blank (PRSPR's SPRL)",
          [ln[121:] for ln in lines], [" " * 12] * 12)
    lines = [ln[1:121] for ln in lines]
    check("4: header 1 holds **SUBPROGRAMS** and **COMMONS**",
          lines[0].split(), ["**SUBPROGRAMS**", "**COMMONS**"])
    check("4: header 2: NAME ORIGIN REL. E. P. SIZE LIB. SEG. NO. NAME ORIGIN AMOUNT SEG. NO.",
          " ".join(lines[1].split()),
          "NAME ORIGIN REL. E. P. SIZE LIB. SEG. NO. NAME ORIGIN AMOUNT SEG. NO.")
    subs, coms, seps = ex4.map_rows(lines)
    for k, want in enumerate(ex4.MAP_SUB):
        check(f"4: p.17 subprogram row {k + 1}: {' '.join(want)}",
              subs[k] if k < len(subs) else None, want)
    for k, want in enumerate(ex4.MAP_COM):
        check(f"4: p.17 common row {k + 1}: {' '.join(w for w in want if w)}",
              coms[k] if k < len(coms) else None, want)
    check("4: rows 6-10 have no common; '**' on all ten data rows",
          (coms[5:], seps), ([("", "", "")] * 5, ["**"] * 10))
    for k, ln in enumerate(lines):
        print("INFO buffer X line %2d: %s" % (k + 1, ln.rstrip()))
    # Stage 5: BSS leaves by $EOJ (C22-6678-1 p.22), MCP's own $EOJ code.
    eojc = sym2("EOJC")
    check("5: one IF trap of $EOJ (65.0), from EOJC", field(g["neoj"], 0, 18), 1)
    check("5: tentacle YJC4TT+2.0 = the linkage, EOJC's B,$MCP (p.118 l.1)",
          field(g["jc4t2"], 0, 19), eojc // 32)
    check("5: YLLSAV.25 = 0, so the $EOJ is not 'spurious' (p.274 l.26)",
          field(g["yllsav"], 25, 1), 0)
    # SMAXRN is VF,0 at 215005.32 (p.103 l.36); bits 28-63 hold any count
    # field LC,1,SMAXRN can read (bits 0-27 hold the word's first half).
    check("5: SMAXRN's count 0, so LC,1,SMAXRN / BXCZ skip the PP I/O wait (p.274"
          " ll.29-30)", field(g["smaxrn"], 28, 36), 0)
    check("5: past YC4B3 (p.274 ll.25-30, 44-45, 51-52: YC4NO, not $ABEOJ) into YMPFCH:"
          " one $FETCH from MCP, its linkage YFDO's B,DMCP (p.269 ll.22-23)",
          (field(g["nfet"], 0, 18), field(g["fstc1"], 0, 24)), (1, S["YFDO"] + 32))
    check("5: $14 = $EOJ's op 65.0 at the fetch (p.274 l.25 LVE,$14,YJC4TT+2.32)",
          field(g["fx14"], 0, 24), 65 * 64)
    check("5: YEOJS still 0: a normal end (p.274 l.46 sets it only past l.45)",
          field(g["yeojs"], S["YEOJS"] % 64, 1), 0)
    judge6(g, S)
    b0, b1 = exp["table_span"]
    bad = [f"{a:o}" for a in range(b0, b1) if mem.get(a, 0) != exp["table"].get(a, 0)]
    check(f"4: the relocation table, {b1 - b0} words at {b0:o}", bad, [])
    ks = S["KSILO"] // 64
    for a, v in sorted(exp["ksilo"].items()):
        check(f"4: KSILO+{a - ks} = {v:016x}", g.get("ks%d" % (a - ks)), v)


if __name__ == "__main__":
    sys.exit(main())
