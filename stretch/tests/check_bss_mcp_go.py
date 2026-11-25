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
MCP's $EOJ program, fetched back from disk by YMPFCH, runs job control, in
the bypass mode IPL leaves, through YL1 to YPPID4's $FETCH of the compiled
program '))))))))' (stage 6).  That fetch is MCP's own DISK FETCH, from TWS
holding the cards BSS read; job control finds no IOD card and primes resume
load, which, as the BSS postprocessor, loads the compiled program from TWS
and the library and gives $RET with SICBU = *MAIN*'s entry (stage 7).
MCP's own return path (SIFAE -> CRETN -> MDRET -> CRETBU) enters *MAIN*;
its SCAFFOLD body gives $EOJ, and MCP's own end of job runs to the output
EOJ's $W, which K NO GO holds until the operator readies the OUTPT unit
(OPERATOR ACTION, below); MCP then writes the job's listing to that reel
and job control reaches ZJOBC1, the wait for the next job card (stage 7,
the end).  On a bench of its own the operator then loads a second job's
cards and readies the reader, and MCP's own job control reads the JOB
card, types the job's name and time, reads the TYPE card through UNCODE
and asks for more cards (stage 8).
Every stage runs on THE POST-IPL CORE IMAGE (below): all 98,304 words a
real IPL leaves, not the assembled listing.

M-a, EVERY $FETCH IS MCP'S OWN DISK FETCH (2026-11-24; docs/fidelity_plan.md
M-a).  The stub's $FETCH (LFETCH/SFETCH/IFETCH over core images of type
areas at 240000, 260000, 264000 and a TWS image) is DELETED.  Every
B,DMCP / ,DFETCH (DFETCH SYN,66.32, MCP_Mar63_001-249 p.105 l.36) traps
IF into SIT+21 (SIC,STIC / BD; p.111) and goes to MCP's SIFAE at l.7
(SIFAE+2.0), through MIFTTT 66.32 to the tentacle X TENTB and DISK FETCH
as landed (MCP_Mar63_250-445 pp.311-318, transcribed and !CHECKed against
the listing with the rest of MCP, NEXT.md "pp.298-328 LANDED"): the index
read once (p.311 l.13 CSCNOP, p.317 ll.23-45 CNDXF), the dictionary search
(p.312 CRODE), the reads (p.317 ll.14-32, waiting at BB,ADSKRD,$), and its
returns -- normal through XRETN ,SDRET (p.314 l.24), error through CURD
(p.315 l.21), end through CHKPAR, SIZE - RELFWA <= 0 (p.315 ll.28-39).
DISK FETCH's own $MCP calls (the disk READs; NDFT, 9 in stage 7) are
counted, not logged.  The disk is THE ONE THE POST-IPL RUN'S IPL WROTE:
post_ipl() saves it with the core image (STRETCH_DISK_SAVE, host_tape.c;
same cache key, a pkl without its disk is a miss) and every bench loads a
copy (STRETCH_DISK), so DISK FETCH's in-core index (read by IPL's run)
matches the disk.  WHAT IS FETCHED, and from where:
  - 22LOADER (stage 3; stage 7 again) and 22$EOJ (stages 6 and 7): the
    default PROSA's overlay areas, which IPL writes (P1 arcs 0-32).
  - PCBSS (1a; N = 0, the whole area, M = 15) and PCFORTRA (1c: not in the
    dictionary, so DISK FETCH's error return, p.396 l.1's B,YTCERR, and
    MCP's error path: YTCERR -> YBRLOG -> YC4B, which clears SCORG and
    idles in KFRONT to the 400,000-cycle cap; 1c's SCORG check is now read
    at the fetch, snap8).
  - BSS (stage 3, 140 cards, RELFWA 15k) and the library LBUST*, LBIOCS*,
    LBFISIP* (stage 7: 2, 7 and 3 cards, then one fetch at RELFWA = the
    area's size, DISK FETCH's end return, YLERR): ON THE MASTER TAPE, so
    IPL writes them (strap/prosa_dict.py's opt-in PROSA_EXTRA, written by
    prosa_extra_spec() into the post-IPL cache).  RECONSTRUCTION: no
    listing of BSS, the PC areas or the library exists; C22-6728 printed
    p.96 puts the system's type areas on the master tape after the first
    four, and UPDATE-30 is what put them there.  Not IPL's code: the
    tape's content.
  - '))))))))', TWS (stage 6's YPPID4 fetch, then the loader's 33 cards in
    stage 7).  Nothing IPL runs writes it: the BSS chain's last link
    leaves it (C22-6728-1 printed p.209), and the reconstructed BSS does
    not.  Its dictionary entry is PROSA_EXTRA's "beyond" entry at the first
    track past PROSA, the arc S SYRFT names (printed p.28 ll.24-27, ceil8 of
    the PROSA arcs: arc 40 for this tape, IPL's arcs reaching 37; p.103
    l.40 "VARIABLE POINTER FOR PP DISK ASSIGN"; p.396 l.20, TWS = 4096 - S
    SYRFT arcs), RECONSTRUCTION/CHOSEN; its words (tws_words) are written
    into the bench's copy of the disk, SCAFFOLD for BSS's own write.  DISK
    FETCH's own routine for it, p.317 l.22 X TRCTC "DITTO COMPILED
    PROGRAM", is BEW,$ in the listing.
  The disk dictionary as IPL wrote it (measured, disk_dir()): LBSIN at disk
  word 16723 (45), LBUST* 16768 (30), LBFISIP* 16798 (45), LBIOCS* 16843
  (105), PCBSS 16948 (15), BSS 16963 (2100), )))))))) 20480 (512, arc 40),
  22$EOJ 15031 (1692), 22LOADER 12948 (1057).  In arcs (512 words):
  22LOADER 25-27, 22$EOJ 29-32, the LB areas 32-33, PCBSS 33, BSS 33-37
  (IPL's last written arc), TWS 40.
  An in-run tamper of BSS, TWS or 22$EOJ patches the bench's disk copy
  (the program's `disk`); the IPL stays the control's.
THE STUBS THAT REMAIN on this path (each still SCAFFOLD unless named):
  - stage 1's $SCR (68.32): the TYPE card copied to YBCBU (M-b);
  - SIT+21's BD (and FWIT+1's, by SIT+20..47's copy) to STUBIF, which
    now only observes and routes: it logs every 66.32 call (FLOG) and
    sends it to SIFAE+2.0; it plays MCP's dispatcher for the $RET before
    BSS (ENTER: $RET to the BSS processor, SCAFFOLD for MCP's $RET to the
    PP), counts the $RET traps after the load (IRET -> MRET), and stops the
    first run at the second post-BSS fetch (HALT2, STOPC 8);
  - ITAB and STUB1 while the reconstructed BSS runs (stage 4: SIFAE's PP
    half and IRETP for $SPR/$RET, IEOJ for its $EOJ);
  - stage 2's plants (SLRBU and SBAPP as YL1 leaves them for the CHOSEN
    LIM, KSILO+8..11);
  - SIT+20..47's MARKER;
  - *MAIN*'s one-word body (MAIN_BODY);
  - the reader's 32-word image (stage 8, FIXTURE);
  - the TWS words on the disk and their dictionary entry (above);
  - the BSS/PCBSS/LB areas on the tape (above, RECONSTRUCTION).
  check_bss_mcp_load.py keeps its own $FETCH stub (not this milestone).
MOVED PINS (header numbers and INFO lines; no check pins cycles): every
  fetch is now real disk I/O (a LOCATE and READs per call, and channel-0
  EOP reports, which the stage 7/8 report checks now leave out,
  _dreports).  1a 61,347 -> 93,405 cycles; 1b 30,596; stages 3-6
  1,773,207 -> 2,442,409 (143 fetches: 22LOADER, 140 BSS cards, 22$EOJ,
  TWS); stage 7 ZJOBC1 2,559,405 -> 3,195,867 (193 fetches); stage 8
  the spooler's wait (half-word 152237) 2,683,602 -> 3,321,754 (36 traps after
  the entry, as before).  Stage 8's step cap 3.2M -> 4.5M (R2G_STEPS8): its reader CS
  comes at step 3,195,836, past the old cap.  Step and cycle numbers in
  the stage texts below are the stub's, before M-a.

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
  (p.384 ll.36-44) leaves it for a CHOSEN `LIM,200000,214513` (the deck
  assembles at 200000; MCP's resume load clears PP memory from 41 for
  SBAPP's count, capped at YMAX = 30000, so the clear stays below the
  deck), and KSILO+8..11 as check_bss_example4 plants them.  The upper
  limit was 214777 until 2026-11-18; it is now just below 214514, where the
  post-IPL image has SBAMCP, "the base address of the I-O location table"
  for MCP (C22-6728-1 p.274, PDF 274, read in the ink), with IPL's unit
  tables and channel status table at 214515-214777 (SXCHAN 214724.00).
  The deck, its tables and BSS's upper limit (KSILO+8, 213766) lie below.
  MEASURED (R2G_TAMPER=lim, the old 214777): no check fails, so the move
  rests on the document, not on a failure.
STAGE 3: entered at YC4INT (p.396 l.30) with stage 1a's KSILO, SCORG and
  YCIDBT words copied in.  YC4INT steps the chain, YDFCS <- KSILO+2 (BSS),
  $13 <- YDKCRS, WJC4G (p.386 ll.8-31) sets YLLSAV from SLRBU, SREADS
  <- $13, primes $RESLD and gives $RET (p.386 l.31, BE,DMCP / ,SDRET).
  That call reaches the stub at 32.0 (no trap: stage 3 runs before ENTER
  sets ITAB and the boundaries); DISP (SCAFFOLD for the IF trap only)
  stores STIC = 020217.40, the ,SDRET, as SIT+21's SIC would, and BD's
  to SIFAE (p.117 l.5) -- disabled, as the trap's BD leaves it (p.111
  l.3; MEASURED: entered enabled, the run hangs at p.117 l.8).  Since
  2026-11-19 MCP's own dispatcher runs from there (SIFAE -> KFRONT ->
  CRETN -> MDRET -> MUP1 -> p.142 ll.1-15, the unprime, -> MTC1 -> YRLTT
  -> YRESLD, l.50; see stage 7), and from YRESLD it is IBM's code: LX,$1,YXWRLD / B,YMPFCH (ll.50-51); YMPFCH
  (p.269) finds YMPSAV holding $EOJ (the post-IPL image: JC4 was in core),
  saves LOADER and fetches 22LOADER into YMPBUF -- the overlay area holds
  22SCOMD after IPL -- through MCP's DISK FETCH from the disk IPL wrote
  (M-a; before 2026-11-24 the stub's LFETCH over a core image of the
  landed pp.320-334 at 264000); YFHBR's BE,YRESL1 (p.269
  l.56) enters YRESL1 (p.332 l.2): SCORG = 1 -> YRESL2, YRLDTA <- YDFCS, the PP clear
  (ll.13-17), then per card YRDISK (ll.27-41) -> $FETCH (DISK FETCH, the
  area BSS on the disk, RELFWA 15k; before M-a a stub over a core image
  at 240000) -> YLOAD -> ALOADR (pp.320-331) ->
  ... -> the branch card -> YBCENC (p.332 l.53) -> p.333 -> $RET with
  SICBU = 200000.  140 cards since the deck's $SPR/$EOJ code (137 before),
  143 $MCP calls (142 before YMPFCH's fetch was run).  SCAFFOLD/RECONSTRUCTION:
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
    (66.00), so it is 0 (RECONSTRUCTION of the dispatcher's setting;
    since 2026-11-19 the dispatcher's own p.142 ll.11-13 copy the
    parameters from the prime queue, and the image's 0 is IPL's).
    MEASURED: left as unwritten memory (bit 50 = 1), the loader read
    through $SCR, and the error path's spool print (YPR -> YPRSPL, p.270)
    then called $MCP; the stub stops on a repeated disk address since.
    SINCE THE POST-IPL IMAGE NOTHING IS PLANTED: IPL leaves YRLTT+2 = 0.
  - The type area is contiguous 15-word records: YDKCRS (p.397 l.17,
    XW,-15.,0,0,7) has count 0, so p.332 l.28's end-of-arc step never
    fires for it (MEASURED: the 137th read is at 240000 + 15*136).
  - $RET to the loaded BSS processor: the stub's ENTER branches to SICBU
    (SCAFFOLD: stage 4 runs BSS under ITAB and 32/33 bounds, because the
    reconstructed BSS writes KSILO in MCP's area).
  - Before M-a the stub served calls by state: the first was WJC4G's $RET;
    while SICBU held its sentinel (only p.333 l.2 writes it) a call was a
    $FETCH of the area YRLDTA names; after, $RET (p.333 ll.4-5).  Since
    M-a every $FETCH goes to DISK FETCH, and the stub plays only the $RET
    from the LOADER's range (ENTER) and WJC4G's (to SIFAE, after QSNAP).
    Stage 3's fetches are checked as one list: 22LOADER, then BSS at
    RELFWA 15k for k = 0..139 (the three old fetch checks, merged).
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
  p.21).  B,DMCP traps IF as the PP's calls do; since M-a STUBIF sends the
  $FETCH (DFETCH SYN,66.32, p.105 l.36) to SIFAE+2.0, and MCP's DISK
  FETCH reads the 22$EOJ area IPL wrote (1692 words) to 020000 and
  returns to the normal return.  (Before M-a STUBIF copied a core image
  of it planted at 260000, SCAFFOLD.)  The fetch is needed: word 020000 was 0 at
  the call (resume load's PP clear, "PP memory is cleared from location
  41.(8) TO SBAPP", C22-6728-1 p.86, PDF 86, read in the ink).  Then IBM's code: p.381 (PDF 131) l.11
  $14 = 65.0, not SJC4; ll.13-14 SIT+20..47 <- FWIT (MARKER: SIT+20..47
  planted with the sentinel, which the image otherwise assembles equal to
  FWIT); l.17 SCORG = 1 -> YC4INT; p.396 ll.32-35 the pointer 2 > count 1
  -> YLASTC: SCORG = 0, KSILO+7.25 (the reject flag, C22-6728 p.197) 0,
  KSILO+1.19 = 1, YDFCS <- '))))))))' (p.397 l.19); p.397 (PDF 147) ll.1-9:
  KSILO+2 is BSS; l.3 $14 <- KSILO+8 ("TAKE P.P. LIMITS FROM KSILO"), l.4
  $13 <- YPPBSD, l.5 $15 = YL1, and l.6 BB,SYSMOD,TJUNAS "-IF BYPASS" is
  taken: SYSMOD = 10 (below), so ll.7-8 (WJ4PFF, YTSP) are skipped.  TJUNAS
  (p.434, PDF 184): TMAXRF's count 0 -> TJEND, SPROGS 0 -> YC4BZ (pp.436-
  437, transcriptions) -> $15 = YL1 (p.384 ll.36-49): YEDLL and SLRBU from
  KSILO+8 (the limits BSS left), SMARK, SBAPP; SCORG 0 and SYSMOD.0 = 1, so
  not WJCV-1.0 but ll.50-54: YIODSO -> YRDFSO (p.387 l.4; $13's flag is on,
  so YICDTM) -> SCORG 0 -> YPPID4 (ll.22-27): YI4TA <- YDFCS
  '))))))))', $13 = YPPBSD (XW,-13.,34,0,7) + 15., so RELFWA 2.0, the
  first card past the arc's two header words ("SO JC WILL LOOK AT FIRST
  CARD OF AN ARC", p.397 l.18), and B,DMCP / ,DFETCH (ll.29-30), which
  traps IF.  The bench's FIRST run halts there (the stub's HALT2 word,
  STOPC 8), and stages 3-6 are judged on it: 1,773,207 cycles (2026-11-19;
  1,776,198 before stage 3 went through MCP's dispatcher).  The SECOND
  run of the same bench goes on (stage 7).
STAGE 7, THE GO PHASE PAST THE FETCH (2026-11-18, the second run; the
dispatcher, *MAIN* and the end of job 2026-11-19).
  WHAT TWS HOLDS.  C22-6728-1 printed p.209 (PDF 209, read in the ink):
  "MCP assumes that the compiled problem program is left in card form and
  may be loaded from the first arc up to and including the number of arcs
  occupied in TWS"; the last link must "leave the binary output on the
  disk" for a Compile and Go run.  For the BSS chain the last link is BSS,
  and its input is the subprogram decks on TWS (C22-6728-1 p.86, PDF 86:
  resume load is "the last phase of the Fortran BSS Loader").  So the
  type area '))))))))' is served (SCAFFOLD for TWS on the disk: since M-a
  its words are planted in the bench's disk copy and DISK FETCH reads
  them; before, the stub's $FETCH over core images) as the very cards the
  reconstructed BSS read as its input (tws_cards, checked equal to the
  deck's TWS words): Example 4's six subprogram decks and the FORTRAN
  branch card, in the loader's arc geometry -- arc n's two header words at
  512n (CHOSEN 0: spec G6), card k at 2 + check_bss_example4.tws_offset(k)
  (34 cards of 15 words an arc; p.332 ll.27-30, p.397 l.18).  CHOSEN: no
  LIM or IOD card ahead of the program (none is printed for this job).
  The library decks are LB areas, "LB" + the first entry name (CHOSEN,
  spec G7), as check_bss_mcp_load has them.
  THE RUN, IBM's code (before M-a, 2026-11-24, all but the fetches;
  before 2026-11-19, all but the dispatcher too):
  - p.385 (PDF 135, read in the ink) ll.1-5: the card (*MAIN*'s first
    binary card) is not the pattern l.4 tests, so YIO (l.6) sends it to
    UNCODE (l.8), whose error return (l.13) is YIDCER.
  - p.392 (PDF 142, read in the ink 2026-11-18) ll.27-31 YIDCER -> YBCERR
    ll.37-51: column 1 is not the T punch (l.38) nor B (l.42); $10 is
    YICEM (l.44); ll.46-47 the IOD count below SLRBU; l.50 KCI,$12,1.0 "IS
    NUMBER OF IODS ZERO" -> l.51 BXE,WJC4G1.  (PC trace, R2G_PCLOG=4.)
  - p.386 (PDF 136, read in the ink) l.7 WJC4G1 BB,SCORG,YC4INT: SCORG 0,
    so WJC4G (ll.8-31): limits from SLRBU, SREADS, $RESLD primed (ll.23-
    25), SJ1FUL 0 so no SJC1 (l.26), BE,DMCP / ,SDRET (ll.30-31): MCP's
    $RET, STIC at 020217.40.
  - MCP'S OWN DISPATCHER (2026-11-19; it was the stub MRET).  The $RET
    traps IF (ITAB+21: SIC,STIC / BD,STUBIF) and STUBIF hands it, as any
    MCP-level $RET, to SIFAE at l.7 (p.117, PDF 124): l.19 KVI,3,64.0 /
    BXL,KFRONT -> KFRONT (p.177) -> KPLUG1 (p.178 l.33, BR,-32.0($3):
    33.0 is B,CRETN) -> CRETN (p.140) -> MDRET (p.141, PDF 148, read in
    the ink) -> MUP1 (l.41): MPRMQK holds WJC4G's prime, so ll.43-50 and
    p.142 (PDF 149, read in the ink) ll.1-15 take $RESLD off the prime
    queue, put its parameters in the tentacle YRLTT and B,MTC1 -> YRESLD.
    YMPFCH fetches 22LOADER again (YMPSAV held $EOJ); YRESL1 with SCORG 0, KSILO+1.19 = 1 and KSILO+2 = BSS is the
    BSS postprocessor (C22-6728-1 p.86): limits from KSILO, MRNRM5, and
    the loader reads all 33 subprogram cards on TWS once, in order, never
    the branch card, then the three library decks the calls bring in
    (UST*, IOCS*, FISIP*: 3, 8 and 4 fetches -- 2, 7 and 3 cards, each
    deck then one fetch at RELFWA = its area's size, DISK FETCH's end
    return, YLERR), and p.333 ll.4-5 give $RET with SICBU = 000051.0,
    *MAIN*'s entry on p.17's map.  That $RET goes the same way to MDRET;
    the prime queue is empty now, so MUP1 -> MPP1 (p.142 l.18) -> JMPP1
    (l.56) -> CRETBU (ll.41-51): SL = 0 (l.42, "CHANGE TO PP LEVEL"),
    registers 3-31 from SLRBU (l.50 T,15,SLRBU,3.0: the boundaries are the
    PP limits YL1 put there) and BE to SICBU (l.51).  Control reaches
    000051.0.
  - The load is judged against p.17's map: at each subprogram's printed
    origin its first word XW,0,<calls>, every transfer-vector word the
    skeleton B,entry;NOP with the callee's printed entry, and each entry's
    B,E;NOP (load_oracle, 32 words).
  - No other trap: 12 $SPR, 12 PP $RET, 1 $EOJ, no bad op, no interrupt;
    YLJSLT unchanged.
  - THE PROGRAM IS LOST; ITS BODY IS SCAFFOLD.  No 7030 FORTRAN object
    deck or library code is held (archival_inventory.md; fortran_bss_plan
    section 2.4), and Example 4's subprograms are stubs of p.17's sizes.
    *MAIN*'s one-word entry, B,E0 / NOP in check_bss_example4 (a branch to
    itself), is here B,$MCP / ,$EOJ (MAIN_BODY, CHOSEN): C22-6751 p.23 makes
    a main-program RETURN a "good stop" that returns to MCP, C22-6678-1
    p.22 gives $EOJ.  The map, the TWS-equals-input assert and
    check_bss_example4's own run are unchanged (a 6th SUBS field).  The
    word loads absolute: B,32.0 / ,65.0 at 000051 (load_oracle).
  - THE PROGRAM'S $EOJ.  B,32.0 traps IF: 32 lies outside the PP's limits
    (41-10577, control bit 1, from SLRBU).  ITAB+21's SIC,STIC stores into
    MCP's area, protected for the PP -- which the model refused until
    2026-11-19 (decks/sic_bd_protected_store.strap; MEASURED before the
    fix: STIC kept resume load's ,SDRET, DS came on, SIFAE analyzed that
    $RET again and CRETPP led to the BADI stop).  From the program's entry
    on, STUBIF sends every trap but $FETCH to SIFAE (l.7); SIFAE's PP half
    ll.20-28 now runs as printed (MCP's bounds and mask, STLR -> SLRBU).
    Then IBM's code: MIF6 -> YJC4TT -> YC4NO -> YC4B3 -> YMPFCH, whose
    $FETCH of 22$EOJ is DISK FETCH's (the 51st fetch) -> p.381 (PDF 131):
    SCORG 0, so ll.19-21 B,DMCP / ,SKOM ,1.32 "EJSCAN" (input commands:
    MIFTTT 79.32 VVSKM, p.121 l.45), the spooler's VSSKOM gives $RET from
    224147.40; ll.25-27 ,SLOG2 (81.0, MIFTTT l.48: UNDEF), JUNDEF's $RET
    from 233147.40; l.37 ,SSPEOJ (77.32: SAEOJT, "OUTPUT EOJ", p.121
    l.41); the print program's output subroutine CAOS3A then gives B,$MCP
    / ,$W at 222265.40 (p.204 ll.8-9, PDF 211, read in the ink), the write
    of the record buffer X holds.
  - K NO GO (PC log, R2G_PCLOG=5, 2026-11-19; pp.177 and 179-180 read in
    the ink, PDF 184, 186): the $W enters KFRONT (p.177 l.5), through
    KIODRN, and l.21 BB,SL,KMCP; KMCP (p.179 ll.4-7) -> KSOAR (p.177
    l.27).  l.37 (BZB,SMULTI,KUNA) falls through; l.41 BZRZ,KNOGO ("LOOP
    IF MOUNT OR REW BIT ON", after l.40 L(BU,2),SMOUNT($11)) is taken.
    KNOGO (p.179 l.13) runs ll.13-29 and l.29 BZAH,KCHOPN ("BRANCH IF
    TIME NOT ELAPSED") is taken: KCHOPN, p.180 l.2 (221041.00, half-word
    148546), at 2,524,928 cycles.  (Earlier text named l.30's
    BB1,SRMIND; see below.)
  - THE UNIT IS REAL, NOT A BENCH ARTIFACT.  The $W's IOD parameter AMR
    (224032, p.204 l.10) is 11: CT11, channel 34 unit 0, UST entry
    214772 ($11), unit area 214676 ($12).  IPL sets its MOUNT (.51) and
    initial-mount (.53) bits (printed p.79 ll.3-4, TP4) and types "MOUNT -
    REEL NUMBER OUTPT ON CHANNEL 34 UNIT 0" (docs/boot_plan.md): MCP is
    waiting for the operator to mount the output reel.  WHY KCHOPN:
    l.30's BB1 (assembled ...221041.34 0E, "SET SWTCH") sets SRMIND
    whenever it runs, and a probe of that shape confirms the model writes
    the bit without branching.  Under nooper, uat1 at KCHOPN is still
    0000400000000000, with bit 63 clear.  So l.30 did not complete, and
    the branch is l.29's BZAH ("TIME NOT ELAPSED").  R2G_STOP=148512 fires
    8 cycles before KCHOPN: that is the instruction counter ahead of the
    branch resolving (inferred).  SRMTC and $TC were not read.
  - OPERATOR ACTION (the default; R2G_TAMPER=nooper restores the old stop
    at KCHOPN).  The operator mounts a blank reel and readies the unit.
    The bench mounts REEL_WORDS (2^18, CHOSEN) zero words as the tape
    (-D HOST_TAPE, host_tape.c), and the first time the PC reaches KCHOPN
    gives channel 34 the channel signal: Reference Manual printed p.116
    (PDF 119, read in the ink), CS "comes on ... whenever the unit changes
    from not-ready to ready status", "a means of communication from the
    operator".  gen_tb.py OPSIG -> StretchIO.operatorReadyTape (unit 0
    turns ready, and CS); nothing in MCP's tables is touched.  Since
    2026-11-19 the tape control's units are selected (UNIT SELECT, below):
    the bench starts with no tape unit ready (TAPEREADY 0; IPL asked for a
    reel on units 0 and 1) and the operator readies unit 0 only.  NOT
    MODELLED: the units' data (one reel serves every unit).
  - Then IBM's code: the CS report (00001) -> KSTORE (p.122) -> KSIGNL
    (p.124 l.53) -> KHUNT/KSTAB (p.125) -> p.126 l.5 BZBZ,SMOUNT($11),
    ZRCPFC clears MOUNT.  The $W, retried from KSUPP, goes through, and
    MCP prepares the new reel: seven operations on channel 34, each
    reported EOP alone (00010): density (p.155 l.5), label read (p.183
    l.25), backspace (p.155 l.18), label write (p.155 l.45), tape mark
    (p.156 l.14), the $W's record (EWR311, p.154 l.18), and the output
    EOJ's tape mark (p.164 l.33).  Two model gaps were found on this path
    and fixed with their own decks: the state-setting CONTROL codes
    (decks/io_tape_control_modes.strap) and WRITE TAPE MARK
    (decks/io_tape_mark.strap).
  - THE REEL (host_tape.c's STRETCH_TAPE_TRACE): from the load point a
    one-word label, a mark, one 150-word record and a mark.  The record is
    buffer X (p.209 l.56): control character P and 12 lines, which are
    p.17's map, every subprogram and common row.
  - WHERE IT STOPS: ZJOBC1 (020416.40, half-word 16925, p.391 l.37), job
    control's wait for the next job card, at 2,559,405 cycles (2,561,915
    before unit select), with 16 traps after the entry and nothing typed
    on the console.
  - Traps after the entry are logged (PTRL: STIC, word 3, SCOMRG; 64
    entries since 2026-11-19, 32 before): the first *MAIN*'s ,$EOJ at
    51.40 with SL 0 and word 3 = SLRBU; then 231147.40, 20007.40,
    224147.40, 20013.00, 233147.40, 20021.00, 222266.00, and eight at MCP
    level after the $W is held (AFTER_W, pinned, judge7_units).
  - UNIT SELECT, A MODEL DEFECT FOUND BY NAMING THE TRAPS (2026-11-19).
    Before, NINE traps followed the held $W; the first, from 222572.40, is
    p.209 l.44 (PDF 216, read in the ink) ,$RET of ATPBCS (ll.41-44),
    entered from AXITB+4 (l.28 B,ATPBCS).  AXITB is CT21's I/O table of
    exits (IOD 12, AXITB, CH34, UN1: tests/mcp_iod_deck_p1.tsv), and word
    4 is its SIGNAL INTERRUPT INSTRUCTION, taken "when CS (.13) is on
    alone" (C22-6678-1 printed pp.15-16, PDF 15-16).  So one operator
    action on unit 0 ran unit 1's signal fix-up too: the model had no
    unit select and every unit read ready, so the receptor's walk of the
    channel's MOUNT units (p.125 KHUNT ll.5-7, KSTAB ll.41-56, PDF 132:
    LOCATE the unit, CCW its control word) found unit 1 ready, and p.126
    (PDF 133) l.2 "BZB,KRECEP.18,KHEX -IF UNIT IS NOT READY, SKIP" did not
    skip it; l.5 cleared CT21's MOUNT (MEASURED: UST 214773 = 4671c020
    81801400 in the post-IPL image, MOUNT .51 and initial mount .53 on;
    81800000 at the old stop).  The Reference Manual settles the unit:
    printed p.120 (PDF 123, read in the ink), LOCATE "is used to select
    one of several devices accommodated by a single channel address
    ... The selection address is three bits long and appears in bit
    positions 47 through 49"; printed p.107 (PDF 110, read in the ink),
    control word bit 18, Unit Ready, "When the bit is off, the unit is in
    the not-ready status".  Fixed in StretchIO/StretchExecute (LOCATE
    selects the unit; CCW's bit 18 is the selected unit's) with
    decks/io_tape_unit_ready.strap.  MEASURED after (R2G_PCLOG=8): KHUNT
    reaches KSTAB twice, unit 1 first, and p.126 l.2 sends unit 1 to KHEX;
    unit 0 goes on through ll.3-12 to RMCPCS.  CT21's MOUNT and initial
    mount stay on.
  - THE EIGHT TRAPS AFTER THE HELD $W, NAMED (pages read in the ink; the
    path confirmed by R2G_PCLOG=8).  Each is an IF trap (Reference Manual
    printed p.45, PDF 48, indicator 21: a branch to the protected area
    while enabled) of a B,$MCP or B,DMCP (DMCP SYN,32.0, p.108 l.5);
    STIC is the call's ,op half-word.  SIFAE (p.117 l.19) sends ops below
    64.0 to KFRONT (p.177), the rest through MIFTTT (p.121).
      222574.40  p.209 l.48 ,DRET (DRET SYN,33.0, $RET): RATPCS (ll.45-48,
                 PDF 216), entered from AXITA+4 (l.13 B,RATPCS), CT11's
                 SIGNAL fix-up.  The first CS on CT11 is consumed: l.46
                 SVA,14,AXITA+4.0 points the entry at ATPACS and ATARI is
                 not set.
      222266.00  p.204 l.9 ,$W (PDF 211) again: the $W KSUPP had
                 suppressed, re-executed now that MOUNT is off.
      222320.40  p.204 l.47 ,$RET at CRET: the $W's END OF OPERATION.
                 AXITA+5, the NORMAL INTERRUPT word (p.209 ll.15-17: LV,
                 14,AOP / TI,2,AXITA,0($14) / B,5.($14)), copies the
                 interrupt words to CEXN, the table AOP names (p.204 ll.6-
                 7, l.41 "TABLE OF EXITS FOR PRINT BUFFER"), and enters
                 CEXN+5 = CEOPN (l.49 "MAKE TAPE AVAILABLE", l.50, l.51
                 BZB,CBTA,CRET), whose CRET gives $RET.  (PC log:
                 222546.00, 222547.40, 222321.00-222323.00, 222320.00.)
      222311.00  p.204 l.36 ,$WEF: CEOJ4 (l.31 BB,CATUB,$ "WAIT IF TAPE
                 IS BUSY") waited out that EOP; ll.32-36 set AOP = CEXEF
                 and write the end of file (the tape mark, p.164 l.33).
      222320.40  p.204 l.47 again: the $WEF's EOP.  AXITA+5 -> CEXEF+5 =
                 CEOPEF (p.206 l.17 CM0000,CATUB "RELEASE TAPE", l.18
                 B,CRET).  (PC log: 222376.00, 222377.00.)
      222146.40  p.201 l.54 ,$RET at ARET1 (PDF 208): p.204 l.39 B,ARET
                 "GO TO RESTORE AND EXIT", ARET (p.201 l.51) -> ARET1, the
                 output EOJ (p.381 l.37 ,SSPEOJ) returning to $EOJ.
      020031.40  p.382 l.1 ,SSCR4 (PDF 132, binary 000117.00 = 79.0) after
                 p.381 l.56 RNOREJ B,$MCP (PDF 131): MIFTTT 79.0 VF,VVSCR
                 "1ST CARD REQUEST" (p.121 l.44, PDF 128), on the page that
                 "READ[S] THE JOB CARD" (p.381 ll.39-43).
      224451.00  p.222 l.31 ,DRET at VRTN (PDF 229; ll.27-31 VSCRA): the
                 spooler returns with no card.  Job control resumes at
                 p.382 l.3 B,WSYSCA+.32 (PDF 132) -> p.391 (PDF 141) ll.29-
                 31, BZB,SJ1FUL,ZJOBC1 -> ZJOBC1.  (PC log: 020032.40,
                 020412.00-020413.00, 020416.40.)
    None of the eight is a model defect.
  - THE UPPER LIMIT, SETTLED (2026-11-19): KSILO+8.28.  C22-6728-1 printed
    p.88 says "upper limit of PP 8.32 (BU,18)", but C22-6728 (-0) printed
    p.197 (PDF 197, read in the ink) prints "PP UPPER LIMIT 8.28", and
    p.397 l.3 LX,$14,KSILO+8 / p.384 l.39 SC take it from the index count
    field, bits 28-45.  BSS now writes 213766 there (decks/bss_7030.strap,
    check_bss_example4), so SLRBU's upper boundary is 213766.
  TASIGN is not on this path (no IOD card).
STAGE 8, A SECOND JOB CARD (2026-11-19).  Its own bench,
  StretchBssGoJob2Tb: stage 7's program, a fresh blank reel, the reader
  image JOB2_CARDS (`JOB,SECOND` and `TYPE,GO`, CHOSEN; 15 words a card,
  so the two fill 30 of the model's 32 reader words).  OPERATOR ACTIONS:
  unit 0 of channel 34 readied at KCHOPN as in stage 7, then, at job
  control's first arrival at ZJOBC1, the deck is loaded and the reader
  (channel 32, "READER IS INPUT SOURCE ON CHANNEL 32" at IPL) readied: a
  CS (printed p.116).  The CS comes at step 2,559,374.  Then MCP's own
  job path, every trap named in the ink (JOB2_TRAPS; MCP printed page,
  PDF = printed+7 in volume 1, printed-250 in volume 2):
    p.215 l.40 ,DCCW (the spooler takes the reader's CS); p.216 l.51
    ,DRD (the READ); p.222 l.31 ,DRET at VRTN; p.226 l.42 ,DCCW at VEE
    (the READ's end exception); DRET; p.391 l.42 ,SDRET (ZJOBC1's $RET;
    JC4, primed, runs again); p.382 l.1 ,SSCR4 (the 1ST CARD REQUEST
    again); DRET (the JOB card in hand); p.201 l.54 ARET1 (the card on
    the spool listing); p.382 l.34 ,67.0 ($SPU with the JOB card, l.36);
    ARET1; l.38 ,DTIME; l.41 ,DCOMM, typing "SECOND     00:00:01"; ARET1;
    p.383 l.4 ,SLOG4 (logger 4, the beginning of the job); JUNDEF's $RET
    (MIFTTT 80.32 UNDEF, p.121 l.47); p.384 l.7 ,DSCR (YTCSR, GET 1
    CARD: the TYPE card); DRET; p.387 l.9 ,DSCR (YRDFSO's next card);
    p.216 l.24 ,DCOMM: "SERVICE THE CARD READER".
  The TYPE card goes through IBM's UNCODE normally: KSILO+1.18-22 =
  00100, TYPE,GO's count, as stage 1b.  The reader reports 00001 (the CS)
  and 00110 (EE with EOP): the model's 32-word reader image runs out
  (FIXTURE: a real empty hopper is simply not ready).
  WHERE IT STOPS: the spooler's wait for the reader, p.224 ll.16-17
  (PDF 231) B,DMCP / ,DRIO: the bench halts on the step that executes the
  B at 224526.00, the IF pending and the PC at the ,DRIO (half-word
  152237), at 2,683,602 cycles, 36 traps after the entry.  (Run to its
  step cap the DRIO trap is logged as the 37th, MEASURED.)
  INJECTIONS (R2G_ONLY8=1, so only the stage-8 bench runs; MEASURED):
    control -- all 6 stage-8 checks pass.
    job2nocs -- the reader is never readied (no second OPERATOR ACTION):
      all 6 fail.  Job control keeps cycling SDRET / SSCR4 / DRET at
      ZJOBC1 (64 traps logged), nothing is typed, KSILO+1.18-22 keeps
      stage 7's 01011, and the run hits the step cap.
    job2nojob -- the first card punched JOX,SECOND: 4 fail (the console
      text, the trap list, KSILO+1.18-22 = 01011, the stop); the two
      operator and reader-report checks pass.  The reader is read, but
      no JOB card is found, nothing is typed, and job control cycles to
      the step cap.
THE POST-IPL CORE IMAGE (2026-11-18, later).  post_ipl() runs
  StretchMcpStartTb (tests/run_mcp_start_test.sh's bench: IPL from tape
  with p.1's IOD deck, CLOCK and BYPASS, JC4 polling at ZJOBC1, p.391
  l.37) with gen_mcp_boot_tb.py's MCP_START_MEM_DUMP=1 and dumps all
  98,304 words at its stop; the dump is cached in bsv/build-hosttape/
  postipl/, keyed by the bench source, the tape and every model source.
  MEASURED cold (cache moved aside, 2026-11-18): the dump is rebuilt to the
  same key (the run is deterministic), and the whole test takes 116 s.
  Every stage starts from it (words 0-31, the registers, left to each
  bench).  Against the assembled image (MEASURED, 1,225 words differ):
  - the overlay area 234424-236523 holds 22SCOMD, the command package
    (563 of its 1088 assembled words equal; the rest its buffers), not
    the LOADER: stage 3 now runs YMPFCH's fetch of 22LOADER (above);
  - YMPSAV holds $EOJ, which is why that fetch is needed;
  - SXCHAN = 214724.00 count 36, SMCP = SBAMCP = 214514.00 (assembled 0,
    215000.00, 215000.00): IPL's channel and I/O location tables;
  - SCOMRG = 2c86000000000000, SYSMOD 10 (below);
  1,028 of the 1,225 differing words are in the overlay area; the other
  197 resident words (those above among them) are run state and IPL-set
  pointers, not classified further.
  Re-checked against it, each SCAFFOLD the bench planted: SYSMOD 10 is
  the image's own (nothing planted; set_sysmod asserts it); YRLTT+2 is 0
  (nothing planted); KSILO+0..11 are 0 (stage 1 writes 0-2 and 7 and the
  bench plants 8-11 as before); SLRBU is 0 (the stage-2 gap's plant
  stays); SIT+20..47 equal FWIT (the MARKER stays); SICBU holds 1800 (the
  sentinel stays); SXCHAN and the CST are now IBM's (the overlap path
  below).  Stub and disk images go only where the dump holds 0 (asserted).
  MEASURED (R2G_TAMPER=assembled, the assembled image with the old YRLTT
  plant): only the check on SXCHAN/SMCP/SBAMCP fails; this job's path
  reads none of the other words that differ.
SYSMOD = 10 IS REAL (2026-11-18).  The image assembles SCOMRG as
  a800000000000000 (p.103 ll.10-27): SYSMOD 00, overlap.  A whole-core dump
  of StretchMcpStartTb at its stop (IPL from tape with p.1's IOD deck, the
  CLOCK and BYPASS commands IPL primes, JC4 polling at ZJOBC1) reads SCOMRG
  2c86000000000000: SCNFCG 1, SL 1, SM 1, SYSMOD 10, SPPBT1 1, SPPBT2 1.
  p.376 l.37 (PDF 126, read in the ink) ZBA1X CM0000(BU,1),SYSMOD+.1 "SET
  BYPASS FROM IPL MODE", l.38 CM1111(BU,2),SPPBT1 "SET SWITCHES FOR BYPASS
  FIRST".  So a machine started the way this model's IPL starts it is in
  bypass mode, and p.397 l.6 (PDF 147, in the ink: "BB,SYSMOD,TJUNAS -IF
  BYPASS", binary 215001.10 80) sends the GO phase to YL1.  The value is
  planted from that run (POST_IPL_SYSMOD; since the post-IPL image it is
  the image's own word, and only R2G_TAMPER=assembled plants it), in stage 1's image too (its
  SCOMRG word, with SCORG, is what stages 3-6 copy); stage 1's three runs
  take the same cycles as with 00 (61,465 / 30,032 / 30,998) and pass
  the same checks.  gen_mcp_boot_tb.py pins the
  SCOMRG word at the start bench's stop, so a change there shows.  Only
  SYSMOD is taken: SCNFCG is 1 in both; SL, SM and the SPPBT bits are left
  as this bench has them (no path here reads the SPPBT bits; pp.377-378,
  the command package, do).
THE OVERLAP PATH (R2G_TAMPER=overlap, SYSMOD 00 as assembled), as before:
  $15 = WJ4PFF, YTSP set, TJUNAS -> WJ4PFF (p.388): SCNFCG 1, so BZBZ
  clears it, CM1111(BU,1),WJCW, and B,TASIGN, where that run stops (p.398
  l.31).  With the stop moved to T N (R2G_STOP=18346): TASIGN -> TA9 (p.406
  l.35, "BEGINNING OF CHAN STAT TABLE") -> ... -> MCP's own T N BD,$ at
  021725.00, "MACH CONF CH. ASSIGN BIT ON - MULTI" (p.410 l.52, PDF 160,
  read in the ink), 2,341,326 steps.  OBSERVED at that halt: the SXCHAN
  word is 0 (p.103 l.28's assembled XW,0: base 0, count 0), so TA9's index
  TIXF walked from location 0.  IPL's SXCHAN, from the same start-bench
  dump: 214724.00 with count 36, over tables IPL built at 214515-214777
  (unit tables, the CST); SMCP and SBAMCP are 214514.00, not the assembled
  215000.00, and about 1,200 other words from 214764 up differ from the
  image, not classified (run state, and words such as JPICK and B1RA whose
  addresses look like pointers into the moved area).  NOT GRAFTED: the
  tables cannot safely be taken alone while the words that may point into
  them are unclassified; and this bench's CHOSEN limits LIM,200000,214777
  overlap them (IPL's MCP base, SMCP, is 214514).  [All of the above was
  observed on the assembled image, before 2026-11-18 (later).]
  ON THE POST-IPL IMAGE (2026-11-18, later; R2G_TAMPER=overlap now plants
  SYSMOD 00 into the IPL dump, nothing else changed): the run takes the same
  path and reaches TASIGN, where the bench's stop_at_pc (TASIGN, half-word
  17640) ends it -- a bench stop, not a halt -- after 1,775,302 cycles,
  NFET 1, now with IBM's SXCHAN = 214724.00 count 36 and SMCP = SBAMCP =
  214514.00 in core and the PP limits below them.  TA9 on those tables is
  NOT run by this test.  One diagnosis run, R2G_TAMPER=overlap
  R2G_STOP=18346 R2G_ONLY6=1 (2026-11-18), is NOT a clean measurement and
  is recorded only as observed: stage 4's linkage/tentacle checks fail as
  well (7 FAIL, the map itself prints right), so the moved stop disturbs
  more than stage 6; stage 6 passes TASIGN (SCNFCG 0, WJ4PFF cleared it)
  and ends not at T N but at the stub's unserved-op stop (STOPC 4, STIC
  22226600).  Not diagnosed.  TA9 on IBM's tables is still open.
  TMAXRF (215005.32, its count) and SPROGS (215021-215022) are 0 in the
  image AND in the post-IPL dump, so they match a real IPL (at JC4's idle
  poll, before any job; not measured after one).  Left as the image
  assembles them (SCAFFOLD): SXCHAN 0 and the CST; KSILO+7 is 0 (p.395 l.46 zeroes it; the reconstructed BSS
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

INJECTIONS (MEASURED, observed failure sets; R2G_TAMPER, no file edited).
M-a (2026-11-24): THE INJECTIONS BELOW THIS ONE'S OWN WERE MEASURED BEFORE
M-a, with the stub's $FETCH, and were NOT re-run.  nofetch and dispbypass
are RETIRED (the stub they changed is deleted).  M-a's own, in-bench
(R2G_MEASURE=ksilo9,diskksilo9,coreksilo9, one compiled bench, judged on
88 checks; the control 113 PASS in the same run, where stage 8 does not run;
its six passed under R2G_ONLY8=1):
  diskksilo9 -- ONE FETCHED AREA CORRUPTED ON THE DISK ONLY: p.397 l.3
    LX,$14,KSILO+8 reassembled as KSILO+9 in the 22$EOJ type area of the
    bench's disk copy; core untouched.  PREDICTED: ksilo9's set; coreksilo9
    nothing.  OBSERVED: 10 fail -- stage 6's YL1 limits; stage 7's "no
    fetch of anything else but 22$EOJ" and "one fetch past the end of
    each library deck ... no other past an area's end" (one root: FLOG
    logged, from YFDO's call site, a fetch whose name word is
    ?0202536424444720 where 22$EOJ was expected; an unknown name counts as
    past its end; the cause is NOT isolated, and it is not shown that MCP
    asked for that name), the first trap, the $EOJ path, the seven
    operations, the reel's layout, the stop (none: the 12M step cap),
    judge7_units' trap list, and "YLJSLT unchanged".  Not predicted: the
    library-end check (the same root as "no other fetch"), the 7u trap
    list and YLJSLT; the rest were.  So the 22$EOJ the run executes is the disk's, as DISK FETCH
    read it.
  coreksilo9 -- the same statement in core only, the disk untouched: 0
    fail (88 PASS).  Resume load's PP clear and the fetch replace the core
    copy, so a core-only change cannot reach the run any more.
  ksilo9 -- core and disk: the same 10 as diskksilo9.
UNIT SELECT (2026-11-19, later; before M-a, which merged stage 3's
three fetch checks into one, so 119 now): the control passed 121 PASS lines
(the 113 below, judge7_units' two, and stage 8's six); stage 7 stops at
ZJOBC1 at 2,559,405 cycles, stage 8 at 224526.40 at 2,683,602.
  allready (own build) -- every tape unit ready from the start and the
    operator's CS readying none in particular, the model before unit
    select: 2 fail, both judge7_units': CT21's MOUNT and initial mount
    (got 0, 0) and the trap list (the extra ATPBCS $RET from 222572.40
    first).  Stage 7 still reaches ZJOBC1, at 2,561,915 cycles.
  nooper -- re-measured: 7 fail, the same seven as below.
  vtape -- re-measured: 7 fail, the six below plus judge7_units' trap
    list (the REPLACE TAPE path takes other traps); ZJOBC1 at 2,579,016.
  Stage 8's own (job2nocs, job2nojob): see STAGE 8.
The in-bench and other own-build injections below were measured before
unit select (every unit ready); they were not re-run, and judge7_units'
two checks are not in their counts.
Re-run 2026-11-19 with stage 7's operator end (SIT, the channel signal,
the reel, the stop at ZJOBC1): the control run passes all checks, 113
PASS lines.  The in-bench tampers ran as extra program pairs on the one
compiled bench (R2G_MEASURE=cretsl,twsxw,ybc51,vic13,ksilo9,lim,eojl17,
yxwejm,abeoj,nocc,lci15,bs8,fwa,order,itab; each pair's lines are
prefixed "MEASURE <t>", judged on 88 checks), the others each as its own
R2G_TAMPER build.  Judge7 has 21 checks in the default run (22 under
nooper): "stage 7's twenty" means all but "YLJSLT unchanged", and "the
operator eight" means its last eight: the OPERATOR ACTION and its
reports, MOUNT cleared, the seven EOP operations, nothing typed, the
reel's layout, the record's form, its rows, and the stop at ZJOBC1.
Some checks pass under every injection, so they are consistency checks,
not discriminating ones:
- judge6: "word 020000 was 0 at the fetch" (PREW is never written when no
  fetch comes) and "KSILO's link pointer still 1" (stage 3 leaves it 1).
- judge6, under every injection except overlap: "YTSP still 0" and
  "SCNFCG 1, WJCW 0", which are the image's values when p.397 is not
  reached.
- judge7: "YLJSLT unchanged" (before M-a; it fails under M-a's ksilo9).
"The stage-6 eleven" means judge6's other eleven checks.
THE OPERATOR PATH'S OWN INJECTIONS (2026-11-19):
  nooper (own build) -- no channel signal, the old stop at KCHOPN: 7 fail,
    the operator eight but "nothing typed".  The run stops at KCHOPN
    (148546), and the old check "the run stops at KCHOPN, the eighth trap
    the last", judged under nooper only, passes.  So the operator's
    action is what moves the run on.
  vtape (own build) -- the signal is given but no reel is mounted, so the
    tape is the model's 16-word register image: 6 fail.  The failures are
    MOUNT (on again at the stop), the seven operations, nothing typed, and
    the reel's layout, record and rows.  THE RUN STILL REACHES ZJOBC1, at
    2,581,677 cycles.  The record writes run off the 16-word tape (EE,
    reports 00110), MCP takes it as the end of the reel, and types
    "REPLACE TAPE ON CHANNEL 34 UNIT 0 WITH REEL NO. OUTPT JOB **MCP**".
    So the stop alone is no evidence that the listing was written; the
    reel checks are.
  itab (in-bench) -- $IA left at the stub's ITAB from ENTER on (the old
    bench, every entry but IF a stop): 7 fail.  The CS is reported (00001)
    but taken by ITAB's entry 13 (BADI, STOPC 3), so MCP never clears
    MOUNT.  The failures are the operator eight but OPERATOR and "nothing
    typed", plus "no other interrupt" (indicator 13).
  The model's own (bsv/ edits, each reverted by the exact patch and
    checked by hash; the decks' own results are in their headers):
    nosig -- StretchIO.operatorSignal sets nothing: 7 fail, the operator
      eight but "nothing typed".  No report, MOUNT stays on, nothing is
      written, and the run hits the step cap.
    no036 -- tape CONTROL 036 program-checked again: 6 fail.  The failures
      are the seven operations, nothing typed, the reel's layout, record
      and rows, and the stop.  The density CONTROL at KDENOP is reported
      EPGK + EOP (10010), and MCP types six garbage words.
    nowtm -- WRITE TAPE MARK (117) program-checked again: 6 fail, the same
      six.  The label is written (one word), and the mark after it is
      reported 10010.
THE EARLIER INJECTIONS, re-measured on the operator path:
  cretsl -- p.142 (PDF 149) l.42 CRETBU's CM0000(BU,1),SL ("CHANGE TO PP
    LEVEL") as CM1111, so *MAIN* runs at MCP level: 11 fail, all stage 7:
    the first trap (51.40, but SL 1), the $EOJ path, no 22$EOJ fetch, and
    the operator eight.  K NO GO is never reached (no operator action),
    and MCP types five words.  Everything up to CRETBU passes.
  dispbypass (own build) -- stage 3's DISP goes straight to YRESLD (the old
    SCAFFOLD), so WJC4G's $RESLD prime stays on MCP's queue: 3 fail,
    stage 7's end returns (4), first trap and $EOJ path.  Resume load runs
    a second time (55 fetches).  The run still reaches K NO GO, writes the
    reel and stops at ZJOBC1.
  twsxw -- on the disk only, *MAIN*'s card holding its first word is
    punched from XW,0,5 instead of XW,0,6: 1 fails, the load check (word
    41).  Every fetch, count, return, trap and the reel pass.  So the
    program is loaded from TWS's words, not from the deck BSS read.
  ybc51 -- p.392 l.51 BXE,WJC4G1 made a NOP, so the no-IOD branch is not
    taken: 17 fail, stage 7's twenty but the first fetch, "nothing typed"
    and "no other trap".  Stage 7 stops at no stub (None).
  vic13 -- p.387 l.23 V+IC,$13,15. as 13.: 2 fail, stage 6's RELFWA
    (got 0) and stage 7's first fetch (RELFWA 0).  Everything after it
    passes, the reel too: the loader re-reads card 0.
  ksilo9 -- (re-measured under M-a: 10, see above) p.397 l.3
    LX,$14,KSILO+8. as KSILO+9.: 7 fail.  The failures
    are YL1's limits and, in stage 7, "no other fetch", the first trap,
    the $EOJ path, the seven operations, the reel's layout and the stop.
    Under KSILO+9's limits CRETBU's BE to 000051.0 traps at once.  MCP
    handles that trap through to K NO GO, the label and the record (six
    operations, 152 words), but not the output EOJ's mark.  It stops at
    the stub's BADF (STOPC 1).
  lim -- the old CHOSEN LIM,200000,214777: 0 fail (see STAGE 2).
  eojl17 -- p.381 l.17 BB,SCORG,YC4INT as BZB (on the disk copy too):
    26 fail.  l.18 runs on, and its B,DMCP / ,SKOM traps as an unserved
    op (STOPC 4).  The failures are stage 4's "no other op", six of stage
    6's, and stage 7's twenty but "nothing typed".
  yxwejm -- p.269 l.40 XW,YEOJTA,YPPMEM as XW,YDBTA,YPPMEM: the fetch asks
    for $DUMP, and the stub stops at BADF2 (STOPC 1).  29 fail: the
    stage-6 eleven, and stage 7's twenty but "nothing typed" and "no
    other trap".  Stage 5's checks pass.
  abeoj -- BSS leaves by $ABEOJ (68.0): MCP takes p.274 ll.46-48 (YEOJS =
    1, B,DMCP / BE,DDUMP), and the stub does not serve its $DUMP (64.0).
    34 fail: "no other op" (stage 4), stage 5's fetch, $14 and YEOJS, the
    stage-6 eleven, and stage 7's twenty but "nothing typed".
  nocc -- PRSPR stores LINE at byte 0 (no control byte): 20 fail.  The
    failures are byte 0, header 2, all 10 subprogram rows, all 5 common
    rows, rows 6-10/'**', and the reel's record and rows (the same lines,
    written to tape).  Header 1 passes in stage 4, because its words
    survive a one-column shift.
  lci15 -- p.203 l.36 LCI,$9,16 as 15 (15 full words a line): 21 fail:
    byte 0, bytes 121-132, header 2, every row, and the reel's record and
    rows.  Header 1 passes.
  bs8 -- p.203 l.39 SF(BU,48,6) as SF(BU,48,8): 22 fail: every
    buffer-line check (byte 0, padding, both headers, all rows) and the
    reel's record and rows.
  fwa -- the call's FWA outside the PP limits (220000): ACHK -> ACHERR
    (SPRIME primes the error print and $ABEOJ, p.203 ll.11-18).  There are
    8 $SPR and 7 $RET traps, and BSS never finishes.  61 fail: ERRC, OUTN,
    the trap counts, FWA, CBTA, CWA, every buffer-line check, four stage-5
    checks, the stage-6 eleven, and stage 7's twenty.
  order -- type-area cards 41 and 42 swapped: 73 fail.  The loader reads
    41 cards and stops (p.322 l.42, sequence error).  The failures are the
    fetch count, last address, call count, SICBU and entry checks, and
    every stage-4, -5, -6 and -7 check but fifteen (in stage 7, all but
    YLJSLT and "nothing typed").  YRLDTA's check passes.
  overlap (own build) -- SYSMOD at the assembled 00, on the post-IPL
    image: 24 fail.  Six are stage 6's: YTSP (1), SCNFCG/WJCW (0, 1),
    YL1's limits, YI4TA, RELFWA, and the stop.  The run stops at TASIGN,
    half-word 17640, NFET 1, as it did on the assembled image.  The rest
    are stage 7's twenty but "nothing typed" and "no other trap", since
    nothing runs past TASIGN.
  assembled (own build) -- the assembled image, with the old YRLTT plant
    and SYSMOD planted: 8 fail.  They are the SXCHAN/SMCP/SBAMCP check
    (0, 0, 215000.00) and six of stage 7's: the $EOJ path, the seven
    operations, the reel's layout, record and rows, and the stop.  On the
    assembled image the program's $EOJ, the 22$EOJ fetch and ,SKOM go as
    on the post-IPL one, but the next trap is from 224237.00, not VSSKOM's
    $RET at 224147.40.  The CS is reported and nothing more is written:
    the run hits the step cap.  The load check fails too (word 42).  So
    the spooler's path reads words IPL sets.
  nofetch (own build) -- STUBIF's $FETCH copies nothing (its ST a NOP):
    26 fail: eight of the stage-6 eleven (the $EOJ program in core,
    SIT+20..47, SCORG, YDFCS, YL1's limits, YI4TA, RELFWA, the stop) and
    stage 7's twenty but "nothing typed" and "no other trap".  Stage 4's
    "no other interrupt" now passes: with $IA = SIT the AD on entering
    020000 is MCP's to take.  The run hits the step cap.
  nobd (own build) -- ENTER's BD a NOP: 71 fail (see STAGE 4).  The
    failures are SICBU and the entry (stage 3), 34 stage-4 checks, stage
    5's four, the stage-6 eleven, and stage 7's twenty.
  abssid (own build) -- ABSSID (p.291 l.8) spelled BSX: exactly the eight
    1a checks fail (PC area name, M, KSILO count, KSILO+1, KSILO+2,
    YCIDBT, $13, the stop at YC4B5).  1b and 1c pass, and stages 3-7 are
    skipped.
  Controls: the unmodified pair (113 PASS) and 1b and 1c above.

Run with PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=../strap:. from tests/.
R2G_MEASURE=t1,t2,... runs the listed in-bench tampers beside the control
(INJECTIONS).  R2G_PCLOG=1|2|3|4|5|6|7 (a PC log through job control / the
loader / the stage-3 stub / stage 6 on / resident MCP and low core / all /
the channel-signal receptor, the tape write and K NO GO),
R2G_PCLOG=8 (after the $W: exit tables, the unit walk, job control), =9 (job
control's overlay and the spooler),
R2G_STEPS (stage 7's step cap, 12M), R2G_ONLY6 (the first run alone),
R2G_ONLY8 (stage 8's bench alone), R2G_NOJOB2 (skip stage 8), R2G_STEPS8
(stage 8's step cap, 4.5M), R2G_STOP8 (stage 8's stop, a half-word),
R2G_KEEP (keep the bench output) and R2G_STOP (stage 3's stop, a half-word
address; 18346 is T N): diagnosis only.
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
A8INV = {}
for _c, _v in A8.items():
    A8INV.setdefault(_v, _c)


def a8_text(w):
    """A word as eight A8 bytes, '.' for a byte that is no A8 character."""
    return "".join(A8INV.get((w >> (56 - 8 * k)) & 0xFF, ".") for k in range(8))

BSV = os.path.join(HERE, "..", "bsv")
BSC_DIR = "/opt/homebrew/Cellar/bsc/2026.01"
# The blank OUTPT reel the operator mounts (stage 7): CHOSEN size, 2^18
# words, far more than the job writes and far less than a reel holds.
REEL_WORDS = 1 << 18
DRIVER_AT = 0o100000
SENT = 0x5555555555555555
# R2G_PCLOG (diagnosis only): the PC through $EOJ and job control
PC_LOG = [(0o20000 * 2, 0o24000 * 2), (0o231000 * 2, 0o231777 * 2 + 1)]
PC_LOG2 = PC_LOG + [(0o234424 * 2, 0o235264 * 2), (0o235267 * 2, 0o235500 * 2)]
# R2G_PCLOG=3 (diagnosis only): the stage-3 stub, the IF analyzer and the
# print program
PC_LOG3 = [(0o250000 * 2, 0o252000 * 2), (0o215470 * 2, 0o215572 * 2),
           (0o222104 * 2, 0o222400 * 2)]
# R2G_PCLOG=4 (diagnosis only): stage 6 on, the $EOJ program, the stub and
# the LOADER
PC_LOG4 = [(0o20000 * 2, 0o24000 * 2), (0o250000 * 2, 0o252000 * 2)]
# R2G_PCLOG=5 (diagnosis only): the resident MCP and low core
PC_LOG5 = [(0o215000 * 2, 0o223000 * 2), (0, 0o1000 * 2)]
PC_LOG6 = [(0, 0o300000 * 2)]     # R2G_PCLOG=6: everywhere (with R2G_STEPS)
# R2G_PCLOG=7 (diagnosis only): the receptor (pp.122-128), K NO GO's pages
# (pp.177-180) and low core
PC_LOG7 = [(0o215700 * 2, 0o216400 * 2), (0o217500 * 2, 0o221400 * 2), (0, 0o100 * 2)]
# R2G_PCLOG=8 (diagnosis only): after the $W -- the print program's exit
# tables and fix-ups (pp.204-206, 209), the receptor's unit walk (pp.125-126)
# and job control from p.381 l.44 to ZJOBC1 and on (pp.381-382, 391)
PC_LOG8 = [(0o222256 * 2, 0o222400 * 2), (0o222541 * 2, 0o222575 * 2),
           (0o216056 * 2, 0o216140 * 2), (0o20021 * 2, 0o20060 * 2),
           (0o20372 * 2, 0o20432 * 2), (0o222144 * 2, 0o222147 * 2)]
# R2G_PCLOG=9 (diagnosis only): job control's overlay and the spooler
PC_LOG9 = [(0o20000 * 2, 0o24000 * 2), (0o224000 * 2, 0o226000 * 2)]
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


_POST_IPL = None
POST_IPL_MODULE = "StretchPostIplMcpStartTb"


def post_ipl():
    """THE POST-IPL CORE IMAGE: all 98,304 installed words of
    StretchMcpStartTb at its stop (tests/run_mcp_start_test.sh's bench:
    IPL from tape with p.1's IOD deck, the CLOCK and BYPASS commands, JC4
    polling for a job card at ZJOBC1, p.391 l.37), dumped by gen_tb's
    mem_dump (gen_mcp_boot_tb.py, MCP_START_MEM_DUMP=1).  It is run once
    per change of its inputs and cached under bsv/build-hosttape/postipl/,
    keyed by the bench source, the tape and every model source, so a model
    change re-runs it.  Returns {word: value}, every word."""
    global _POST_IPL, POST_IPL_DISK
    if _POST_IPL is not None:
        return _POST_IPL
    import hashlib
    import json
    import pickle
    cache = os.path.join(BSV, "build-hosttape", "postipl")
    os.makedirs(cache, exist_ok=True)
    tape = os.path.join(cache, "postipl.tape")      # this bench's own tape
    # THE SYSTEM TAPE CARRIES THIS JOB'S TYPE AREAS (M-a, 2026-11-24):
    # PROSA_EXTRA (strap/prosa_dict.py), see prosa_extra_spec().
    spec = os.path.join(cache, "prosa_extra.json")
    spec_text = json.dumps(prosa_extra_spec(), sort_keys=True)
    with open(spec + ".tmp", "w") as fh:
        fh.write(spec_text)
    os.replace(spec + ".tmp", spec)
    env = dict(os.environ, PROSA_IOD_DECK="P1", STRETCH_TAPE=tape, MCP_START_MEM_DUMP="1",
               PROSA_EXTRA=spec,
               PYTHONPATH=os.path.join(HERE, "..", "strap") + ":" + HERE,
               BLUESPECDIR=BSC_DIR + "/libexec/lib",
               PATH=BSC_DIR + "/bin:" + os.environ.get("PATH", ""))
    env.pop("STRETCH_DISK", None)
    env.pop("STRETCH_DISK_SAVE", None)
    r = subprocess.run([sys.executable, os.path.join(HERE, "gen_mcp_boot_tb.py"),
                        POST_IPL_MODULE], env=env, capture_output=True, text=True, cwd=HERE)
    if r.returncode:
        raise SystemExit("post-IPL bench: gen_mcp_boot_tb failed\n" + r.stderr[-2000:])
    src = r.stdout
    h = hashlib.sha256(src.encode())
    h.update(open(tape, "rb").read())
    h.update(spec_text.encode())
    for name in sorted(os.listdir(BSV)):
        if name.endswith(".bsv") or name in ("host_tape.c",):
            if name.endswith("Tb.bsv"):          # generated benches
                continue
            h.update(name.encode())
            h.update(open(os.path.join(BSV, name), "rb").read())
    key = os.path.join(cache, h.hexdigest()[:24] + ".pkl")
    # The disk the same run leaves (STRETCH_DISK_SAVE, docs/disk_subsystem.md
    # 9c): what IPL wrote, and the in-core DISK FETCH state (its index,
    # p.317 ll.33-44, read once) matches it.  A cached core image without
    # its disk is a miss.
    disk = key[:-4] + ".disk"
    env["STRETCH_DISK_SAVE"] = disk + ".tmp"
    if os.path.exists(key) and os.path.exists(disk):
        with open(key, "rb") as fh:
            _POST_IPL = pickle.load(fh)
        POST_IPL_DISK = disk
        return _POST_IPL
    bsv = os.path.join(BSV, POST_IPL_MODULE + ".bsv")
    with open(bsv, "w") as fh:
        fh.write(src)
    os.makedirs(os.path.join(BSV, "build-hosttape"), exist_ok=True)
    os.makedirs(os.path.join(BSV, "simbuild-hosttape"), exist_ok=True)
    try:
        for args in (["-g", "mk" + POST_IPL_MODULE, "-u", POST_IPL_MODULE + ".bsv"],
                     ["-e", "mk" + POST_IPL_MODULE, "-o", POST_IPL_MODULE + "_sim",
                      "host_tape.c"]):
            r = subprocess.run([BSC_DIR + "/bin/bsc", "-sim", "-D", "HOST_TAPE",
                                "-simdir", "simbuild-hosttape", "-bdir", "build-hosttape",
                                "-info-dir", "build-hosttape"] + args +
                               ["+RTS", "-K512m", "-RTS"],
                               cwd=BSV, env=env, capture_output=True, text=True)
            if r.returncode:
                raise SystemExit("post-IPL bench: bsc failed\n" + (r.stdout + r.stderr)[-3000:])
        r = subprocess.run(["./" + POST_IPL_MODULE + "_sim"], cwd=BSV, env=env,
                           capture_output=True, text=True)
        out = r.stdout + r.stderr
    finally:
        for name in os.listdir(BSV):        # by exact name, never a glob
            if name in (POST_IPL_MODULE + ".bsv", POST_IPL_MODULE + "_sim",
                        POST_IPL_MODULE + "_sim.so"):
                os.remove(os.path.join(BSV, name))
    if not re.search(r"STOPPED DELIBERATELY at half-word 16925 ", out) or \
            re.search(r"^FAIL", out, re.M):
        raise SystemExit("post-IPL bench: did not reach ZJOBC1 cleanly\n" + out[-3000:])
    mem = {int(a): int(v, 16) for a, v in re.findall(r"MEMDUMP (\d+) ([0-9a-f]+)", out)}
    if len(mem) != 98304:
        raise SystemExit("post-IPL bench: %d words dumped" % len(mem))
    if os.path.getsize(disk + ".tmp") != 8 << 21:
        raise SystemExit("post-IPL bench: the saved disk is not one 353 unit")
    os.replace(disk + ".tmp", disk)
    with open(key + ".tmp", "wb") as fh:
        pickle.dump(mem, fh)
    os.replace(key + ".tmp", key)
    _POST_IPL = mem
    POST_IPL_DISK = disk
    return mem


POST_IPL_DISK = None


# The 22LOADER type area (p.320 l.10 SLC,YMPBUF: 234424.00 on) is not in
# core after IPL: the overlay area holds 22SCOMD, the command package the
# CLOCK and BYPASS commands ran in (MEASURED: 563 of SCOMD's 1088 assembled
# words there are equal; the rest are its buffers and run state).  Resume
# load "immediately enters YMPFCH to get itself into memory from disk"
# (C22-6728-1 p.86, PDF 86, read in the ink): stage 3 now runs that
# YMPFCH (p.291 ll.50-51, p.269), and the stub serves its $FETCH.
LOADER_AT = 0o234424


def base_words():
    """The words a job stage starts from: the post-IPL core image, words
    0-31 (the registers, which each bench sets itself) left out.  R2G_TAMPER=assembled (measurement
    only): the assembled image instead, as the bench ran before."""
    im = image()
    if os.environ.get("R2G_TAMPER") == "assembled":
        return dict(im.words)
    return {w: v for w, v in post_ipl().items() if w >= 32}


def sym(S, nm, extra=0, alias=None):
    v = S[nm] + extra
    return "%-8sSYN,(8)%o.%02o" % (alias or nm, v // 64, v % 64)


def run_bench(tmp, module, progs, reads, stop_hw, step_cap, cycle_bound=40000000,
              mem_dump=None, operator_signal=None, reel=None, tape_ready=None,
              reader_image=None):
    """Build ONE bench and run it on each of `progs` in turn.  The image is
    read at simulation start from a hex file (gen_tb's fast_load, a
    mkRegFileLoad), so programs that load the same set of words differ only
    in that file: it is rewritten and the same simulator rerun.  `reads` are
    (label, word) pairs: the bench prints each word (its expected value is a
    dummy 0) and the values are judged here, field by field.  Returns a list
    of ({label: value}, output), or (None, error) for a build failure.
    `reel`: a host file mounted as the tape (-D HOST_TAPE, host_tape.c,
    STRETCH_TAPE), with its own build directories; None keeps the model's
    16-word register tape."""
    checks = [(lab, str(w), 0) for lab, w in reads]
    hexf = os.path.join(tmp, module + ".hex")
    kw = dict(step_cap=step_cap, cycle_bound=cycle_bound, stop_at_pc=stop_hw,
              fast_load=hexf, mem_dump=mem_dump, operator_signal=operator_signal,
              tape_ready=tape_ready, reader_image=reader_image,
              pc_log={"1": PC_LOG, "2": PC_LOG2, "3": PC_LOG3, "4": PC_LOG4, "5": PC_LOG5, "6": PC_LOG6, "7": PC_LOG7, "8": PC_LOG8, "9": PC_LOG9}.get(os.environ.get("R2G_PCLOG", "")))
    src = generate(module, progs[0], checks, **kw)
    with open(os.path.join(BSV, module + ".bsv"), "w") as fh:
        fh.write(src)
    env = dict(os.environ, BLUESPECDIR=BSC_DIR + "/libexec/lib",
               PATH=BSC_DIR + "/bin:" + os.environ.get("PATH", ""))
    bd, sd, dflag, link = "build-loader", "simbuild-loader", [], []
    # A program with a `disk` attribute ({disk word: value}) runs on its own
    # copy of the post-IPL disk with those words changed (write_disk): the
    # 353 is host_tape.c's (-D HOST_TAPE, STRETCH_DISK; docs/disk_subsystem.md
    # 9c), so such a bench is a host-tape build with or without a reel.
    disked = any(getattr(p, "disk", None) is not None for p in progs)
    env.pop("STRETCH_DISK", None)
    env.pop("STRETCH_DISK_SAVE", None)
    if reel or disked:
        bd, sd, dflag, link = "build-loader-reel", "simbuild-loader-reel", ["-D", "HOST_TAPE"], \
            ["host_tape.c"]
    if reel:
        env["STRETCH_TAPE"], env["STRETCH_TAPE_TRACE"] = reel, "1"
    elif disked:
        env.pop("STRETCH_TAPE", None)       # no reel: the tape has no media
    for sub in (bd, sd):
        os.makedirs(os.path.join(BSV, sub), exist_ok=True)
    results = []
    try:
        for args in (["-sim"] + dflag + ["-simdir", sd, "-bdir", bd,
                      "-info-dir", bd, "-g", "mk" + module, "-u", module + ".bsv"],
                     ["-sim"] + dflag + ["-simdir", sd, "-bdir", bd,
                      "-e", "mk" + module, "-o", module + "_sim"] + link):
            r = subprocess.run([BSC_DIR + "/bin/bsc"] + args + ["+RTS", "-K512m", "-RTS"],
                               cwd=BSV, env=env, capture_output=True, text=True)
            if r.returncode:
                return [(None, r.stdout + r.stderr)]
        for k, prog in enumerate(progs):
            if k:
                assert sorted(prog.words) == sorted(progs[0].words), "a different word set"
                assert generate(module, prog, checks, **kw) == src
            if getattr(prog, "disk", None) is not None:
                env["STRETCH_DISK"] = os.path.join(tmp, "%s.%d.disk" % (module, k))
                write_disk(env["STRETCH_DISK"], prog.disk)
            r = subprocess.run(["./" + module + "_sim"], cwd=BSV, env=env,
                               capture_output=True, text=True)
            if env.get("STRETCH_DISK"):
                os.remove(env.pop("STRETCH_DISK"))
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
            # the reel, as written (host_tape.c's STRETCH_TAPE_TRACE), in order
            got["_tape"] = [(int(a), int(v, 16))
                            for a, v in re.findall(r"^TAPE_WRITE (\d+) ([0-9a-f]+)", out, re.M)]
            got["_oper"] = len(re.findall(r"^OPERATOR ACTION:", out, re.M))
            got["_operat"] = [(int(c), int(h), int(st)) for c, h, st in re.findall(
                r"^OPERATOR ACTION: channel signal on channel (\d+).* at half-word (\d+),"
                r" step (\d+)", out, re.M)]
            reps = re.findall(r"I/O status report, channel (\d+), "
                              r"EPGK UK EE EOP CS = ([01]{5})", out)
            # channel 0 is the 353 disk (M-a, 2026-11-24): DISK FETCH's own
            # reads end in EOP reports there; the checks are about the
            # tape/reader channels, so the disk's are counted apart
            got["_reports"] = [r for r in reps if r[0] != "0"]
            got["_dreports"] = len(reps) - len(got["_reports"])
            got["_typed"] = re.findall(r"^CONSOLE_TYPED ([0-9a-f]{16})", out, re.M)
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


def set_sysmod(words, S):
    """SCOMRG's SYSMOD as IPL leaves it (POST_IPL_SYSMOD), in stage 1 and in
    stages 3-6 alike; R2G_TAMPER=overlap keeps the assembled 00."""
    w, b = S["SYSMOD"] // 64, S["SYSMOD"] % 64
    t = os.environ.get("R2G_TAMPER")
    if t not in ("overlap", "assembled"):
        # From the post-IPL image the word is IPL's own: nothing to plant.
        assert (words[w] >> (62 - b)) & 3 == POST_IPL_SYSMOD, "%016x" % words[w]
        return
    sm = 0 if t == "overlap" else POST_IPL_SYSMOD
    words[w] = (words.get(w, 0) & ~(3 << (62 - b))) | (sm << (62 - b))


def stage1_prog(card_text):
    """The image, the TYPE card in the $SCR stub; the PC area on the disk,
    fetched by MCP's own DISK FETCH (M-a, 2026-11-24)."""
    im = image()
    S = im.symtab
    words = base_words()
    card = cards.card_words(card_text)
    drv = ["        SLC,32.0",
           "        B,SDMCP",
           "        SLC,(8)%o.0" % DRIVER_AT,
           sym(S, "YTCSR"), sym(S, "YBCBU"), sym(S, "YTCINF"), sym(S, "YDFCTA"),
           sym(S, "STIC"), sym(S, "STLR"), sym(S, "SIFAE"), sym(S, "SIT"),
           sym(S, "SLRMCP"),
           "KSILO1  SYN,(8)%o.0" % (S["KSILO"] // 64 + 1),
           "YDFCW   SYN,(8)%o.0" % (S["YDFCTA"] // 64),
           "SCORGW  SYN,(8)%o.0" % (S["SCORG"] // 64),
           # the $SCR stub's normal return: past ,YBCBU / ,1.0 / ,0 / B,YC4B
           # (p.384 ll.8-11; C22-6678-1 p.20's $SCR: FWA, N, M, end, normal)
           sym(S, "YTCSR", 3 * 64, "RSCR"),
           # JC4 as MCP runs it after IPL: SIT (IPL's word 2), the boundaries
           # IPL's XBOUND sets (p.33 ll.51-52: only 32.0 protected), MCP's
           # mask (SLRMCP+9.0) and enabled, so B,DMCP traps IF (RefMan
           # printed p.45, indicator 21) into SIT+21, as at ZJOBC1.
           "START   LVI,$1,SIT",
           "        SV,$1,$IA",
           "        LWF(U),BNDW",
           "        ST(BU),$UB,64",
           "        LWF(U),SLRMCP+9.0",
           "        ST(U),$MASK",
           "        BE,YTCSR",
           "SDMCP   B,SDMCP",
           # THE IF HOOK (SIT+21's BD, SCAFFOLD): SIFAE's ll.5-6 and 9-10 as
           # printed, then the $SCR stub (M-b) for 68.32 (DSCR, p.105 l.40),
           # and MCP's own SIFAE at l.7 for everything else -- $FETCH
           # (66.32) included, which MCP's DISK FETCH serves from the disk.
           # NCALL counts the two ($SCR and $FETCH), SNAP keeps words at each.
           "STUBIF  TI,14,3.0,STLR",
           "        TI,15,17.0,STLR+14.0",
           "        LV,2,STIC",
           "        LVE,3,0.0($2)",
           "        KVI,3,68.32",
           "        BXE,SNAPC",
           "        KVI,3,66.32",
           "        BXE,SNAPC",
           "        B,SIFAE+2.0",
           "SNAPC   LX,$1,NCALL",
           "        LX,$4,SNAPP",
           "        L(BU,64),YTCINF",
           "        ST(BU,64),0($4)",
           "        L(BU,64),YDFCW",
           "        ST(BU,64),1.0($4)",
           "        L(BU,64),YDFCW+1.0",
           "        ST(BU,64),2.0($4)",
           "        L(BU,64),SCORGW",
           "        ST(BU,64),3.0($4)",
           "        L(BU,64),KSILO1",
           "        ST(BU,64),4.0($4)",
           "        V+I,$4,5.0",
           "        SX,$4,SNAPP",
           "        V+I,$1,.32",
           "        SX,$1,NCALL",
           "        KVI,3,66.32",
           "        BXE,SIFAE+2.0",
           # $SCR: the first gives the TYPE card; a second is not on this
           # path (an error print's), and stops (SCR2, the step cap).
           "        KVI,$1,.32",
           "        BXE,SCR",
           "SCR2    B,SCR2"]
    drv.append("SCR     NOP")
    for k in range(15):
        drv += ["        L(BU,64),CARD+%d.0" % k, "        ST(BU,64),YBCBU+%d.0" % k]
    drv += ["        TI,14,STLR,3.0",
            "        TI,15,STLR+14.0,17.0",
            "        BE,RSCR",
            "        CNOP",
            "NCALL   XW,0",
            "SNAPP   XW,SNAP",
            "SNAP    DRZ(BU,64),20",
            "BNDW    VF,33.0",
            "        VF,32.0",
            "        CNOP"]
    drv += [("CARD" if i == 0 else "").ljust(8) + "DD(BU,64),(16)%016X" % v
            for i, v in enumerate(card)]
    drv.append("        END,START")
    d = assemble("\n".join(drv) + "\n")
    for w, v in d.words.items():
        if w in im.words:
            raise SystemExit("the stub overlaps the image at %o" % w)
        if w >= 33 and os.environ.get("R2G_TAMPER") != "assembled":
            assert not post_ipl().get(w), "the stub over IPL's word %o" % w
        words[w] = v
    # SIT+21's BD to the hook (MCP's own is BD,SIFAE, p.111 ll.1-3)
    w = S["SIT"] // 64 + 21
    assert words[w] == im.words[w], "%016x" % words[w]
    words[w] = assemble("        SLC,(8)%o.0\n        SIC,(8)%o.%02o\n        BD,(8)%o.%02o\n"
                        % (w, S["STIC"] // 64, S["STIC"] % 64, d.symtab["STUBIF"] // 64,
                           d.symtab["STUBIF"] % 64)).words[w]
    ks = S["KSILO"] // 64
    for w in (ks, ks + 1, ks + 2, ks + 7):     # KSILO is DR(BU,64) (p.171)
        assert not im.words.get(w), "KSILO+%d holds a word in the image" % (w - ks)
        words[w] = SENT
    set_sysmod(words, S)
    im2 = type(im).__new__(type(im))
    im2.__dict__.update(im.__dict__)
    im2.words = words
    im2.end_pc = d.end_pc
    return im2, d


# The cases, on one bench: the GO,FORTRAN job, then the controls.
CASES = [("GO,FORTRAN", "TYPE,GO,FORTRAN"),
         ("GO alone", "TYPE,GO"),
         ("COMPILGO,FORTRAN", "TYPE,COMPILGO,FORTRAN")]


def tamper_image(words, S, disk=None):
    """R2G_TAMPER, measurement only: an injected fault in IBM's words.
    `disk` ({disk word: value}, the program's disk patches): a word of the
    $EOJ program is changed on its type area 22$EOJ too."""
    t = os.environ.get("R2G_TAMPER")
    if t == "abssid":       # ABSSID (p.291 l.8) spelled BSX: the GO,FORTRAN
        w = S["ABSSID"] // 64        # rewrite still runs, the name changes
        words[w] = (prosa_dict.a6("BSX     ") << 16) | (words[w] & 0xFFFF)
    elif t in IMAGE_TAMPERS or t in ("diskksilo9", "coreksilo9"):
        # one statement of IBM's code reassembled; diskksilo9 / coreksilo9
        # (M-a's discriminating pair): ksilo9 on the 22$EOJ type area on
        # the DISK only / in CORE only
        a, nbits, stmt = IMAGE_TAMPERS[t if t in IMAGE_TAMPERS else "ksilo9"]
        p = assemble("        SLC,(8)%o.%02o\n        %s\n" % (a // 64, a % 64, stmt))
        e0 = S["YPPMEM"] // 64
        for b in range(a, a + nbits):
            w, m = b // 64, 1 << (63 - b % 64)
            if t != "diskksilo9":
                words[w] = (words[w] & ~m) | (p.words.get(w, 0) & m)
            # a word of the $EOJ program is changed on its disk copy too,
            # which is what YMPFCH's $FETCH brings back (stage 6)
            if disk is not None and e0 <= w < 0o40000 and t != "coreksilo9":
                d0, dn = disk_area(EOJ_NAME)
                if w - e0 < dn:
                    c = d0 + w - e0
                    v = disk.get(c, disk_base_word(c))
                    disk[c] = (v & ~m) | (p.words.get(w, 0) & m)
    elif t and t not in ("order", "nocc", "fwa", "abeoj", "nobd", "overlap",
                         "assembled", "lim", "twsxw", "itab", "nooper",
                         "vtape", "allready", "job2nocs", "job2nojob"):
        raise SystemExit("R2G_TAMPER: abssid, order, nocc, fwa, abeoj, nobd,"
                         " overlap, itab, nooper, vtape, allready, job2nocs, job2nojob or %s, not %r"
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
                 "yxwejm": (0o231162 * 64, 64, "XW,(8)231167.0,(8)20000."),
                 # p.397 l.3 (PDF 147) at 021045.40: LX,$14,KSILO+8. as
                 # KSILO+9. (printed binary 220461.34 10: KSILO+8 = 220461)
                 "ksilo9": (0o21045 * 64 + 32, 32, "LX,$14,(8)220462.0"),
                 # p.387 l.23 at 020246.40: V+IC,$13,15. as V+IC,$13,13.
                 "vic13": (0o20246 * 64 + 32, 32, "V+IC,$13,13."),
                 # p.392 l.51 (PDF 142) at 020470.40: BXE,WJC4G1 ("IS NUMBER OF
                 # IODS ZERO") as NOP, so YBCERR goes on to l.52 B,YC4C9
                 "ybc51": (0o20470 * 64 + 32, 32, "NOP"),
                 # p.142 (PDF 149) l.42 at 217300.00, CRETBU's CM0000(BU,1),SL
                 # ("CHANGE TO PP LEVEL") as CM1111: the program runs at MCP level
                 "cretsl": (0o217300 * 64, 64, "CM1111(BU,1),(8)215001.04")}


def stage1(tmp):
    im = image()
    S = im.symtab
    at = lambda nm, extra=0: (S[nm] // 64) + extra    # noqa: E731
    progs = []
    for _lab, statement in CASES:
        prog, d = stage1_prog(type_card(statement))
        prog.disk = {}          # the post-IPL disk as IPL left it
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
            check("1a: M = 15, the PC area's one card: DISK FETCH read the whole area"
                  " (N = 0, C22-6678-1 p.21)", field(g["yciodc"], 0, 18), 15)
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
            check("1c control: SCORG = 1 at the $FETCH (snapped at the call; MCP's error path"
                  " clears it later, below)", field(g["snap8"], 3, 1), 1)
            check("1c control: the fetch asks for PCFORTRA (no BSS rewrite)", name(g),
                  a6("PCFORTRA"))
            check("1c control: ... which the disk does not hold: never at YC4B5",
                  g["_stopped"], None)
    return out


def S_IMG_WORDS(S, nm, k):
    return image().words.get(S[nm] // 64 + k, 0)


# ---- stages 3 and 4: the BSS processor loaded by MCP from its type area,
# entered, run ----------------------------------------------------------------
DRV2_AT = 0o250000           # the stub, above PP memory and MCP (installed: 0-277777)
EOJ_NAME = "22$EOJ  "        # p.269 ll.24, 52-54: YFDO's "22" and YEOJTA's "$EOJ  "
TWS_NAME = "))))))))"        # p.397 l.19 YTWSTA, the compiled program's type area
FLOG_N = 260                 # $FETCH calls the stub's log holds (4 words each)
WJC4G_RET = 0o20217 * 64 + 32   # p.386 l.31 ,SDRET (PDF 136), WJC4G's $RET
SICS = 0x3333333333333333    # SICBU's sentinel (written only by p.333 l.2)
LIM_A, LIM_B = 0o200000, 0o214513    # the processor's limits: CHOSEN (see header)
# SCOMRG's SYSMOD (p.103 l.18, bits 8-9) as IBM's IPL and the BYPASS command
# leave it: 10.  MEASURED on StretchMcpStartTb (tests/run_mcp_start_test.sh),
# which pins the whole SCOMRG word at ZJOBC1 (gen_mcp_boot_tb.py).
POST_IPL_SYSMOD = 0b10


def bss_deck():
    """The RECONSTRUCTED BSS processor (decks/bss_7030.strap) with R2a's
    Example 4 input, punched by the host STRAP II as an absolute binary
    deck.  The KSILO+8..11 lines check_bss_example4 appends are taken out:
    a deck loaded under limits cannot reach KSILO; they are planted."""
    import check_bss_example4 as ex4
    import strap_asm
    from strap2 import compile_cards
    from strap2.cards import deck_cards
    src, exp = ex4.build(go_subs())
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


def tws_cards():
    """The cards on TWS as the deck reads them (check_bss_example4.build's
    input: each Example 4 subprogram punched, then the FORTRAN branch
    card), each as its 15 words.  Checked against the words the deck's
    source assembles after `TWS SYN, $`, so it is the deck's own input."""
    import check_bss_example4 as ex4
    decks = [ex4.punch(ex4.stub_source(*s)) for s in go_subs()]
    fb = ex4.punch(["        PUNREL", "        FEND"])
    cards_ = [ex4.card_words(c) for d in decks for c in d] + \
        [ex4.card_words(c) for c in fb]
    src, _exp = ex4.build(go_subs())
    lines = src.splitlines()
    k = lines.index("TWS     SYN, $")
    words = []
    for k2, cw in enumerate(cards_):
        while len(words) < ex4.tws_offset(k2):
            words.append(0)
        words += cw
    got = [int(x.split("(16)")[1], 16) for x in lines[k + 1:k + 1 + len(words)]]
    assert got == words, "TWS: not the deck's own input"
    return cards_


def lib_areas():
    """The library: one type area per library deck, "LB" + its first entry
    name, six characters, cards contiguous from word 0 (AREAD1) -- as
    check_bss_mcp_load plants them (RECONSTRUCTION; the naming CHOSEN, spec
    G7; the library's code is lost, these are Example 4's stubs)."""
    import check_bss_example4 as ex4
    out = []
    for nm in ex4.LIB:
        ws = [v for cols in ex4.punch(ex4.stub_source(*ex4.LIB[nm]))
              for v in ex4.card_words(cols)]
        out.append(("LB" + nm.ljust(6)[:6], ws))
    return out


def tws_words(tws=None):
    """The compiled program's type area '))))))))' as BSS would leave it on
    TWS: the cards BSS read as its input (tws_cards), in the loader's arc
    geometry -- arc n's two header words at 512n, card k at 2 +
    ex4.tws_offset(k) (34 cards of 15 words an arc; p.332 ll.27-30, p.397
    l.18).  Header words 0 (CHOSEN: spec G6, unprinted).  {relative word:
    value}, and the area's length."""
    import check_bss_example4 as ex4
    tws = tws_cards() if tws is None else tws
    out = {}
    for k, cw in enumerate(tws):
        for i, v in enumerate(cw):
            out[2 + ex4.tws_offset(k) + i] = v
    return out, 2 + ex4.tws_offset(len(tws) - 1) + 15


def bss_area(deck_imgs):
    import check_bss_example4 as ex4
    return [v for cols in deck_imgs for v in ex4.card_words(cols)]


def prosa_extra_spec():
    """THE TYPE AREAS THIS JOB FETCHES THAT THE DEFAULT PROSA DOES NOT HOLD
    (M-a, 2026-11-24), for strap/prosa_dict.py's PROSA_EXTRA:
      * on the master tape, so that IPL writes them to the disk and MCP's
        DISK FETCH finds them in the dictionary: "BSS     ", the
        reconstructed BSS processor punched as an absolute deck
        (RECONSTRUCTION: decks/bss_7030.strap); "PCBSS   ", the PC area
        (RECONSTRUCTION, one card, PC_CARD); the LB areas (lib_areas).
        These are system type areas: C22-6728 printed p.96 puts the type
        areas on the master tape after the first four, and UPDATE-30, not
        IPL, puts them there (C22-6728-1 printed p.96).  No listing of any
        of them exists.
      * "))))))))", TWS, as a dictionary entry only, at S SYRFT's track
        past PROSA ("beyond"); its words are written into the disk image
        by this test (disk_patches), SCAFFOLD for the BSS chain's own
        write of TWS, which the reconstructed BSS does not do.
    The control's words, whatever R2G_TAMPER says: a tamper of these areas
    is a patch of the bench's disk copy, so one IPL serves every run."""
    def build():
        _p2, imgs, _kw, _exp = bss_deck()
        areas = [(BSS_PROC, bss_area(imgs)),
                 (PC_NAME, list(cards.card_words(PC_CARD)))] + lib_areas()
        return {"areas": [[n, ["%016x" % v for v in ws]] for n, ws in areas],
                "beyond": [[TWS_NAME, tws_words()[1]]]}
    return with_tamper(None, build)


_DISK_DIR = None


def disk_dir():
    """The saved post-IPL disk's dictionary (arc 0; C22-6728 printed p.164,
    as strap/prosa_dict.py builds it): {48-bit A6 name: (first disk word,
    size)}.  disk_area(name) looks one up."""
    global _DISK_DIR
    if _DISK_DIR is None:
        post_ipl()
        with open(POST_IPL_DISK, "rb") as fh:
            arc0 = fh.read(8 * 512)
        ws = [int.from_bytes(arc0[8 * i:8 * i + 8], "big") for i in range(512)]
        out = {}
        for k in range(0, 512, 2):
            if not ws[k]:
                break
            arc, word, size = ws[k + 1] >> 52, (ws[k + 1] >> 43) & 511, (ws[k + 1] >> 18) & 0x3FFFF
            out[ws[k] >> 16] = (arc * 512 + word, size)
        _DISK_DIR = out
    return _DISK_DIR


def disk_area(name):
    return disk_dir()[a6(name)]


def disk_base_word(i):
    with open(POST_IPL_DISK, "rb") as fh:
        fh.seek(8 * i)
        return int.from_bytes(fh.read(8), "big")


def write_disk(path, patches):
    """A copy of the post-IPL disk with `patches` ({disk word: value})."""
    import shutil
    post_ipl()
    shutil.copyfile(POST_IPL_DISK, path)
    with open(path, "r+b") as fh:
        for i, v in sorted(patches.items()):
            fh.seek(8 * i)
            fh.write(v.to_bytes(8, "big"))


def stage34_prog(state, deck_imgs, kwords):
    """The image as stage 1 left KSILO and SCORG, the gap PLANTED, the type
    area BSS on the disk image, and the stub."""
    import check_bss_example4 as ex4
    im = image()
    S = im.symtab
    words = base_words()
    at = lambda nm, extra=0: (S[nm] // 64) + extra    # noqa: E731
    if os.environ.get("R2G_TAMPER") == "order":   # measurement only:
        deck_imgs = list(deck_imgs)                # cards 40 and 41 swapped
        deck_imgs[40], deck_imgs[41] = deck_imgs[41], deck_imgs[40]
    area = bss_area(deck_imgs)
    # THE DISK (M-a, 2026-11-24).  Every $FETCH is MCP's own DISK FETCH
    # (pp.311-318) against the disk the post-IPL run's IPL wrote (saved by
    # that run, STRETCH_DISK_SAVE): 22LOADER and 22$EOJ as the default
    # PROSA has them, and BSS, PCBSS and the LB areas from this job's
    # PROSA_EXTRA (prosa_extra_spec).  This program's copy of that disk
    # differs from it only by `dpatch`: TWS (SCAFFOLD, below) and the
    # measurement tampers, which change words of a type area on the disk
    # where they used to change the stub's core image.
    dpatch, plant = {}, {}
    b0, bn = disk_area(BSS_PROC)
    assert bn == len(area), (bn, len(area))
    base_area = bss_area(with_tamper(None, bss_deck)[1])
    for i, v in enumerate(area):
        if v != base_area[i]:
            dpatch[b0 + i] = v
    e0 = S["YPPMEM"] // 64
    e1 = max(w for w in im.words if e0 <= w < 0o40000) + 1
    nldr = max(w for w in im.words if w >= LOADER_AT) + 1 - LOADER_AT
    # The compiled program's type area '))))))))' (SCAFFOLD for TWS on the
    # disk: the BSS chain would write it, the reconstructed BSS does not):
    # tws_words(), at the dictionary's entry past PROSA (prosa_extra_spec).
    tws = tws_cards()
    if os.environ.get("R2G_TAMPER") == "twsxw":       # measurement only:
        # on the disk only, *MAIN*'s card that carries its first word
        # punched from XW,0,5 for XW,0,6
        src = ex4.stub_source(*go_subs()[0])
        k = src.index("        XW,0,6")
        alt = [ex4.card_words(c) for c in ex4.punch(src[:k] + ["        XW,0,5"] + src[k + 1:])]
        tws = list(tws)
        diff = [i for i, cw in enumerate(alt) if cw != tws[i]]
        assert len(diff) == 1, diff
        tws[diff[0]] = alt[diff[0]]
    tw, tws_len = tws_words(tws)
    t0, tn = disk_area(TWS_NAME)
    assert tn == tws_len, (tn, tws_len)
    for i, v in tw.items():
        dpatch[t0 + i] = v
    areas = [(EOJ_NAME,) + disk_area(EOJ_NAME), ("22LOADER",) + disk_area("22LOADER"),
             (TWS_NAME, t0, tn), (BSS_PROC, b0, bn), (PC_NAME,) + disk_area(PC_NAME)]
    for nm, _ws in lib_areas():
        areas.append((nm,) + disk_area(nm))
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
    # R2G_TAMPER=lim (measurement only): the old limits, LIM,200000,214777.
    lim_b = 0o214777 if os.environ.get("R2G_TAMPER") == "lim" else LIM_B
    w = at("SLRBU")
    v = words.get(w, 0) & ~((0o777777 << 46) | (0o777777 << 14))
    plant[w] = v | (lim_b << 46) | (LIM_A << 14)
    w = at("SBAPP")
    plant[w] = (words.get(w, 0) & ~(0o777777 << 46)) | (min(lim_b, S["YMAX"] // 64) << 46)
    # KSILO+8..11 as check_bss_example4 plants them for BSS (U, sentinels).
    for i, v in enumerate(kwords):
        plant[at("KSILO", 8 + i)] = v
    # YRLTT+2.50: the tentacle's parameter words (p.291 l.49 DR(BU),(2), no
    # value) say which pseudo-op entered resume load; 74.32 "forces resume
    # load to use $SCR as a source of cards" (C22-6728-1 PDF 86), and p.332
    # ll.10-11 zero $13 for it.  WJC4G primed $RESLD (66.00), so MCP's
    # dispatcher (not run) would leave it 0.  MEASURED (2026-11-17, on the
    # assembled image): left as unwritten memory (bit 50 = 1), the loader
    # read through $SCR.  SINCE 2026-11-18 IT IS IPL'S: the post-IPL image
    # holds YRLTT+2 = 0, so nothing is planted (the assembled image, under
    # R2G_TAMPER=assembled, still gets the old SCAFFOLD).
    w = at("YRLTT", 2)
    if os.environ.get("R2G_TAMPER") == "assembled":
        plant[w] = words.get(w, 0) & ~(1 << (63 - 50))
    else:
        assert words[w] == 0, "YRLTT+2 post-IPL: %016x" % words[w]
    plant[at("SICBU")] = SICS
    # MARKER: SIT+20 and SIT+22..47 hold the sentinel, so p.381 ll.13-14's
    # restore from FWIT is seen (IPL leaves them equal).  SIT is this
    # bench's $IA from the start (IPL's word 2, below), but those entries
    # are for indicators 20 and 22-47, which MCP's mask (word 12, IF and
    # the always-enabled 0-19) never lets interrupt before the restore.
    # SIT+21, the IF entry, is the $FETCH hook (below), not a marker.
    for k in [20] + list(range(22, 48)):
        plant[at("SIT", k)] = SENT
    # SYSMOD AS IBM'S IPL LEAVES IT (REAL, measured; see the header's STAGE
    # 6): 10, bypass.  It shares SCORG's word, SCOMRG, which is copied from
    # stage 1 above, where set_sysmod planted it.
    assert at("SYSMOD") == at("SCORG") and at("SYSMOD") in plant
    sb = 62 - S["SYSMOD"] % 64
    assert (plant[at("SYSMOD")] >> sb) & 3 == \
        (0 if os.environ.get("R2G_TAMPER") == "overlap" else POST_IPL_SYSMOD)
    for w2, v in plant.items():
        words[w2] = v
    sy = lambda nm, extra=0, al=None: sym(S, nm, extra, al)   # noqa: E731
    # DISK FETCH's own code (pp.311-318, X TENTB 233667 to CWRD 234242):
    # a trap from there is one of its calls (,DLOCS ,DRD ,DRET ,SDRET).
    dft_lo, dft_hi = S["XTENTB"] // 64, S["CWRD"] // 64 + 1
    drv = ["        SLC,32.0",
           "        B,SDMCP",
           "        SLC,(8)%o.0" % DRV2_AT,
           sy("YC4INT"), sy("SICBU"), sy("MR4"), sy("MPQR"),
           sy("STIC"), sy("STLR"), sy("SL"), sy("MIF6"), sy("SCSPRT"),
           sy("SLRMCP"), sy("MCR"), sy("SIFAE"), sy("SIT"), sy("YPPMEM"),
           # $IA = SIT, MCP's own interruption table, as IPL leaves word 2
           # (the post-IPL image: 215023.00, p.110; X377, MCP_Mar63_001-249
           # p.33).  Only stage 4, the reconstructed BSS processor, runs
           # under the stub's ITAB (ENTER to IEOJ).
           # SINCE M-a (2026-11-24) STAGE 3 RUNS AS MCP RUNS AFTER IPL: the
           # boundaries IPL's XBOUND sets (p.33 ll.51-52, PDF 40: only 32.0
           # protected), MCP's mask (SLRMCP+9.0, the IF bit; p.116 l.28) and
           # enabled, so every B,DMCP traps IF into SIT+21 (RefMan printed
           # p.45, indicator 21) as at JC4's own ZJOBC1, and DISK FETCH's
           # waits on the disk's end of operation (p.317 l.32 BB,ADSKRD,$)
           # are ended by MCP's own I/O interrupt path.  Before, the bench
           # ran disabled and unbounded, and B,DMCP reached a stub at 32.0.
           "START   LVI,$1,SIT",
           "        SV,$1,$IA",
           "        LWF(U),BNDW",
           "        ST(BU),$UB,64",
           "        LWF(U),SLRMCP+9.0",
           "        ST(U),$MASK",
           "        BE,YC4INT",
           # 32.0 is protected from the start: a branch there traps.  One
           # that is executed is not expected: stop (STOPC 2).
           "SDMCP   B,LATE",
           # $RET to the BSS processor, after resume load put it in core
           # (p.333 ll.4-5): MCP enters the program at SICBU (SCAFFOLD for
           # MCP's $RET to a loaded processor: M-b).
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
           # THE IF TRAP: SIT+21 and ITAB+21 are SIC,STIC / BD,STUBIF (MCP's
           # own SIT+21 is SIC,STIC / BD,SIFAE, p.111 ll.1-3).  STUBIF runs
           # SIFAE's ll.5-6 and 9-10 as printed (the low registers to STLR,
           # $2 = STIC, $3 = the op) and then hands the trap to MCP's own
           # SIFAE at l.7 (SIFAE+2.0) -- every trap, $FETCH included, but
           # the stub's $RET to the BSS processor (ENTER) and the BSS
           # processor's own calls while it runs (STUB1, SCAFFOLD for SIFAE's
           # PP half and the return routine: M-b).
           "STUBIF  TI,14,3.0,STLR",
           "        TI,15,17.0,STLR+14.0",
           "        LV,2,STIC",
           "        LVE,3,0.0($2)",
           # Every $FETCH (DFETCH SYN,66.32, p.105 l.36) is LOGGED, never
           # served: its STIC and calling sequence (C22-6678-1 p.21: name,
           # RELFWA, FWA, N, M) go to FLOG, and MCP's own DISK FETCH
           # (pp.311-318, the tentacle X TENTB, MIFTTT 66.32) does it.
           "        KVI,3,66.32",
           "        BXE,FLOGR",
           "FDISP   BZB,RUNF,PRE",
           "        BB,BSSEND,POST",
           "        B,STUB1",
           # Stage 3, before the BSS processor is entered: $RET from WJC4G
           # (p.386 l.31) goes to MCP's own dispatcher, which unprimes
           # $RESLD through the tentacle YRLTT to YRESLD (p.142 ll.1-15;
           # DISP, which planted STIC and BD'd to SIFAE, is gone with the
           # real trap); resume load's $RET with SICBU written (p.333 l.2,
           # from the LOADER) is the stub's ENTER.  The prime control and
           # queue are copied at WJC4G's $RET for the check.
           "PRE     KVI,3,33.0",
           "        BXE,PRET",
           "        B,SIFAE+2.0",
           "PRET    KVI,2,(8)%o.%02o" % (WJC4G_RET // 64, WJC4G_RET % 64),
           "        BXE,QSN",
           "        KVI,2,(8)%o.0" % LOADER_AT,
           "        BXL,SIFAE+2.0",
           "        KVI,2,(8)237000.0",
           "        BXH,SIFAE+2.0",
           "        L(BU,64),SICBU",
           "        K(BU,64),SICW",
           "        BZAE,ENTER",
           "        B,SIFAE+2.0",
           "QSN     L(BU,64),MR4",
           "        ST(BU,64),QSNAP",
           "        L(BU,64),MPQR",
           "        ST(BU,64),QSNAP+1.0"]
    for k in range(6):
        drv += ["        L(BU,64),(8)215646.0+%d.0" % k, "        ST(BU,64),QSNAP+%d.0" % (k + 2)]
    drv += ["        B,SIFAE+2.0",
            # A $FETCH: logged (4 words: STIC, then 64 bits from the
            # calling sequence's .32, 1.32 and 2.32 -- name; RELFWA, FWA;
            # N, M), and after the BSS processor's end counted (NFET): the
            # first such is YMPFCH's of 22$EOJ (FSTC1, $14 and word 020000
            # kept); at the second, YPPID4's of '))))))))', the first run
            # stops (HALT2, STOPC 8), and stages 3-6 are judged on it.
            "FLOGR   LX,$4,FLOGP",
            "        KVI,$4,FLOGE",
            "        BXE,FLOGX",
            "        L(BU,64),STIC",
            "        ST(BU,64),0($4)",
            "        L(BU,64),.32($2)",
            "        ST(BU,64),1.0($4)",
            "        L(BU,64),1.32($2)",
            "        ST(BU,64),2.0($4)",
            "        L(BU,64),2.32($2)",
            "        ST(BU,64),3.0($4)",
            "        V+I,$4,4.0",
            "        SX,$4,FLOGP",
            "FLOGX   BZB,BSSEND,FDISP",
            "        L(BU,18),NFET",
            "        +I(BU,18),1",
            "        ST(BU,18),NFET",
            "        KI(BU,18),1",
            "        BZAE,FLG2",
            "        L(BU,64),STIC",
            "        ST(BU,64),FSTC1",
            "        L(BU,64),STLR+27.0",
            "        ST(BU,64),FX14",
            "        L(BU,64),YPPMEM",
            "        ST(BU,64),PREW",
            "        B,FDISP",
            "FLG2    KI(BU,18),2",
            "        BZAE,FDISP",
            "        L(BU,64),STIC",
            "        ST(BU,64),FSTC2",
            "        BB,HALT2,STOP8",
            "        B,FDISP",
            # After the BSS processor's $EOJ: MCP's own.  Its $RETs from JC4
            # ($EOJ program, 020000-023777) or the LOADER (234424-236777)
            # are counted (MRET); once the compiled program is entered
            # (NMRET = 2) each trap but DISK FETCH's own calls is logged.
            "POST    LV,$4,NMRET",
            "        KVI,$4,2.0",
            "        BXL,POST1",
            "        KVI,2,(8)%o.0" % dft_lo,
            "        BXL,PTR0",
            "        KVI,2,(8)%o.0" % dft_hi,
            "        BXL,PDFT",
            "PTR0    LX,$4,PTRP",
            "        KVI,$4,PTRL+192.0",
            "        BXE,SIFAE+2.0",
            "        L(BU,64),STIC",
            "        ST(BU,64),0($4)",
            "        L(BU,64),3.0",              # the boundaries at the trap
            "        ST(BU,64),1.0($4)",
            "        L(BU,64),(8)%o.0" % (S["SL"] // 64),   # SCOMRG: SL
            "        ST(BU,64),2.0($4)",
            "        V+I,$4,3.0",
            "        SX,$4,PTRP",
            "        B,SIFAE+2.0",
            "PDFT    L(BU,18),NDFT",
            "        +I(BU,18),1",
            "        ST(BU,18),NDFT",
            "        B,SIFAE+2.0",
            "POST1   KVI,3,33.0",
            "        BXE,IRET",
            "        B,SIFAE+2.0",
            # While the BSS processor runs (ENTER to its $EOJ): the stub's.
            "STUB1   KVI,3,67.32",
            "        BXE,ISPR",
            "        KVI,3,65.0",
            "        BXE,IEOJ",
            "        KVI,3,68.0",
            "        BXE,IEOJ",
            "        KVI,3,33.0",
            "        BXE,IRET",
            "        SX,$3,BADOPX",
            "        B,BADOP",
            "IEOJ    L(BU,18),NEOJ",
            "        +I(BU,18),1",
            "        ST(BU,18),NEOJ",
            "        CM1111(BU,1),BSSEND",
            # the BSS processor's end: MCP's own table again (SIT)
            "        LVI,$1,SIT" if os.environ.get("R2G_TAMPER") != "itab" else "        NOP",
            "        SV,$1,$IA" if os.environ.get("R2G_TAMPER") != "itab" else "        NOP",
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
            # A $RET from MCP's own JC4 ($EOJ program, 020000-023777) or
            # LOADER (234424-236777) is not the print program's: MRET.
            # After the BSS processor's end any other $RET is MCP's own.
            "IRET    LV,$1,STIC",
            "        KVI,$1,(8)20000.0",
            "        BXL,IRET0",
            "        KVI,$1,(8)24000.0",
            "        BXL,MRET",
            "        KVI,$1,(8)%o.0" % LOADER_AT,
            "        BXL,IRET0",
            "        KVI,$1,(8)237000.0",
            "        BXL,MRET",
            "IRET0   BB,BSSEND,SIFAE+2.0",
            "IRETP   L(BU,18),NRET",
            "        +I(BU,18),1",
            "        ST(BU,18),NRET",
            "        CM0000(BU,1),SL",
            "        LV,$1,SCSPRT+1.32",
            "        SVA,$1,RETB",
            "        TI,24,PPSAV+5.0,8.0",
            "RETB    BE,0",
            # MCP's $RET from JC4 or the LOADER, served by MCP's own
            # SIFAE from l.7 (p.117) -> KFRONT -> CRETN -> MDRET (p.141).
            # The first is WJC4G's in the GO phase (p.386 ll.23-31: $RESLD
            # primed, then $RET), unprimed to YRESLD (p.142 ll.1-15); the
            # second is resume load's (p.333 ll.4-5), which CRETBU (p.142
            # ll.41-51) turns into the entry of the program at SICBU.  The
            # stub only counts them and records STIC and SICBU.
            "MRET    L(BU,18),NMRET",
            "        +I(BU,18),1",
            "        ST(BU,18),NMRET",
            "        LX,$3,MRETP",
            "        L(BU,64),STIC",
            "        ST(BU,64),0($3)",
            "        V+I,$3,1.0",
            "        SX,$3,MRETP",
            "        L(BU,64),SICBU",
            "        ST(BU,64),SICB2",
            "        B,SIFAE+2.0",
            # Every stop of the stub comes here, its reason in STOPC
            # (bench's stop address): 2 LATE, 3 BADI, 4 BADOP, 8 HALT2.
            "LATE    LI(BU,18),2",
            "        B,STOPS",
            "BADI    LI(BU,18),3",
            "        B,STOPS",
            "BADOP   LI(BU,18),4",
            "        B,STOPS",
            "STOP8   LI(BU,18),8",
            "STOPS   ST(BU,18),STOPC",
            "        NOP",
            "        NOP",
            "        NOP",
            "        NOP",
            "SSTOP   B,SSTOP",
            "        CNOP",
            "NMRET   DRZ(BU,64),1",
            "SICB2   DRZ(BU,64),1",
            "MRETP   XW,MRETL",
            "PTRP    XW,PTRL",
            "PTRL    DRZ(BU,64),192",
            "MRETL   DRZ(BU,64),4",
            "HALT2   DRZ(BU,64),1",
            "STOPC   DRZ(BU,64),1",
            "FLOGP   XW,FLOG",
            "ENTRYX  XW,0",
            "NFET    DRZ(BU,64),1",
            "NDFT    DRZ(BU,64),1",
            "FSTC1   DRZ(BU,64),1",
            "FSTC2   DRZ(BU,64),1",
            "FX14    DRZ(BU,64),1",
            "PREW    DRZ(BU,64),1",
            "SICW    DD(BU,64),(16)%016X" % SICS,
            "QSNAP   DRZ(BU,64),8",
            "RUNF    DRZ(BU,64),1",
            "BSSEND  DRZ(BU,64),1",
            "NSPR    DRZ(BU,64),1",
            "NRET    DRZ(BU,64),1",
            "NEOJ    DRZ(BU,64),1",
            "BADOPX  DRZ(BU,64),1",
            "BADIC   DRZ(BU,64),64",
            "BNDW    VF,33.0",
            "        VF,32.0",
            "        CNOP",
            "PPSAV   DRZ(BU,64),30",
            "FLOG    DRZ(BU,64),%d" % (4 * FLOG_N),
            "FLOGE   SYN,$",
            "ITAB    SYN,$"]
    for k in range(64):     # the interruption table: IF to STUBIF, else BADI
        drv += ["        SIC,STIC" if k == 21 else "        SIC,BADIC+%d.0" % k,
                "        BD,STUBIF" if k == 21 else "        BD,BADI"]
    drv += ["        END,START"]
    d = assemble("\n".join(drv) + "\n")
    for w2, v in d.words.items():
        if w2 in im.words or w2 in plant:
            raise SystemExit("the stub overlaps at %o" % w2)
        words[w2] = v
    # THE IF HOOK (SCAFFOLD): SIT+21, MCP's IF entry, is SIC,STIC /
    # BD,SIFAE (p.111 ll.1-3); here its BD goes to STUBIF instead, which
    # logs each $FETCH and hands every trap to SIFAE but the stub's
    # $RET to the BSS processor and that processor's own calls (M-b).
    # FWIT+1, the copy p.381 ll.13-14 restore SIT+21 from, carries the same
    # hook.  Every other SIT entry is IPL's.  SINCE M-a (2026-11-24) IT
    # SERVES NO $FETCH: MCP's own DISK FETCH (pp.311-318) reads the disk.
    hook = d.words[d.symtab["ITAB"] // 64 + 21]
    for nm, k in (("SIT", 21), ("FWIT", 1)):
        w2 = at(nm, k)
        assert words[w2] == im.words[at("SIT", 21)], "%s+%d: %016x" % (nm, k, words[w2])
        words[w2] = hook
    if os.environ.get("R2G_TAMPER") != "assembled":
        # the stub and the disk images go where IPL left nothing
        pi = post_ipl()
        used = [w2 for w2 in d.words if w2 >= 33]
        bad = ["%o" % w2 for w2 in used if pi.get(w2, 0)]
        assert not bad, "stub/disk words over IPL's: %s" % bad[:10]
    im2 = type(im).__new__(type(im))
    im2.__dict__.update(im.__dict__)
    im2.words = words
    im2.end_pc = d.end_pc
    d.areas = areas
    im2.disk = dpatch
    return im2, d, len(area)


def with_tamper(t, fn, *a):
    """fn(*a) with R2G_TAMPER = t (None: unset), the variable restored."""
    old = os.environ.get("R2G_TAMPER")
    if t:
        os.environ["R2G_TAMPER"] = t
    else:
        os.environ.pop("R2G_TAMPER", None)
    try:
        return fn(*a)
    finally:
        if old is None:
            os.environ.pop("R2G_TAMPER", None)
        else:
            os.environ["R2G_TAMPER"] = old


def stage34_progs(state):
    p2, imgs, kwords, exp = bss_deck()
    prog, d, nwords = stage34_prog(state, imgs, kwords)
    tamper_image(prog.words, image().symtab, prog.disk)
    # Two runs on one bench: the first halts at the second $FETCH (HALT2,
    # STOPC 8), where stages 3-6 are judged; the second goes on (stage 7).
    progA = type(prog).__new__(type(prog))
    progA.__dict__.update(prog.__dict__)
    progA.words = dict(prog.words)
    progA.words[d.symtab["HALT2"] // 64] = 1 << 63
    return progA, prog, p2, imgs, exp, d


def stage34(tmp, state, measure=()):
    """Build the stage 3-7 bench and run it.  `measure` (R2G_MEASURE): more
    R2G_TAMPER names whose programs share the bench (same word set), run
    after the control's two; their results follow in the list."""
    progA, prog, p2, imgs, exp, d = stage34_progs(state)
    sym2 = lambda n: p2.val.symbol_value(p2.st.search(n))[0]   # noqa: E731
    extra = [with_tamper(t, stage34_progs, state) for t in measure]
    S = image().symtab
    at = lambda nm, extra=0: (S[nm] // 64) + extra    # noqa: E731
    reads = [("sicbu", at("SICBU")), ("entryx", d.symtab["ENTRYX"] // 64),
             ("ydfcs", at("YDFCS")), ("yrldta", at("YRLDTA")), ("yljslt", at("YLJSLT")),
             ("errc", sym2("ERRC") // 64), ("outn", sym2("OUTN") // 64)]
    reads += [("q%d" % i, d.symtab["QSNAP"] // 64 + i) for i in range(8)]
    reads += [("ks%d" % i, at("KSILO", i)) for i in range(12)]
    # The stop: YC4B3 (p.274 l.51), where MCP's $EOJ (entered at YC4NO
    # through the tentacle YJC4TT) goes on to the chain's next link by
    # YMPFCH.  A deck that halts instead (BEW,$) stops on core.halted().
    # Stage 6 stops where the stub stops a second $FETCH (TWSF): in bypass
    # mode, YPPID4's fetch of the compiled program '))))))))' (p.387 l.29).
    # On the overlap path (R2G_TAMPER=overlap) it stops at TASIGN as before.
    halt = S["TASIGN"] // 32 if os.environ.get("R2G_TAMPER") == "overlap" \
        else (d.symtab["SSTOP"] // 32, S["KCHOPN"] // 32)
    # OPERATOR ACTION (the default since 2026-11-19).  IPL typed "MOUNT -
    # REEL NUMBER OUTPT ON CHANNEL 34 UNIT 0" and set the unit's MOUNT bit
    # (printed p.79 ll.3-4); K NO GO holds the $W until the unit signals.
    # The operator mounts a blank reel and readies the unit: the bench mounts
    # REEL_WORDS zero words as the tape (tmp/outpt.tape) and, the first time the
    # $W reaches KCHOPN, gives channel 34 the channel signal (Reference
    # Manual printed p.116, PDF 119: CS "whenever the unit changes from
    # not-ready to ready status").  Nothing in MCP's tables is touched.  The
    # run then stops where job control waits for the next job card, ZJOBC1.
    # R2G_TAMPER=nooper: no operator (the old stop at KCHOPN); =vtape: the
    # operator signals but no reel is mounted (the 16-word register tape).
    # THE TWO UNITS (2026-11-19).  IPL asked for a reel on channel 34 unit 0
    # AND unit 1 (CT11, CT21) and set both MOUNT bits.  The operator mounts
    # ONE reel, on unit 0, and readies that unit: no tape unit is ready at
    # the start (tape_ready 0, StretchIO.setTapeUnitsReady) and the action
    # at KCHOPN readies unit 0 (operatorReadyTape: ready, and CS).  So when
    # MCP's receptor walks the channel's units (p.125 KHUNT/KSTAB, LOCATE
    # then CCW), p.126 l.2 "IF UNIT IS NOT READY, SKIP" passes over unit 1
    # (Reference Manual printed p.120 LOCATE, p.107 bit 18).
    # R2G_TAMPER=allready: the model before unit select (every unit ready,
    # the CS alone), which cleared BOTH MOUNT bits.
    oper, reel = (S["KCHOPN"] // 32, 34, 0), os.path.join(tmp, "outpt.tape")
    tape_ready = 0
    if os.environ.get("R2G_TAMPER") == "allready":
        oper, tape_ready = (S["KCHOPN"] // 32, 34), None
    if os.environ.get("R2G_TAMPER") != "overlap":
        halt = (d.symtab["SSTOP"] // 32, S["ZJOBC1"] // 32)
    if os.environ.get("R2G_TAMPER") == "nooper":
        oper, halt = None, (d.symtab["SSTOP"] // 32, S["KCHOPN"] // 32)
    if os.environ.get("R2G_TAMPER") == "vtape":
        reel = None
    if reel:
        os.makedirs(os.path.dirname(reel), exist_ok=True)
        with open(reel, "wb") as fh:
            fh.write(bytes(8 * REEL_WORDS))
    if os.environ.get("R2G_STOP"):     # diagnosis only: a half-word address
        halt = int(os.environ["R2G_STOP"], 0)
    # the output unit K NO GO judges (IOD 11 = CT11, channel 34 unit 0, in
    # IPL's tables): $10-$12 at the stop, AMR (the print program's IOD
    # parameter, p.204 l.10), the unit area table's words 0-1 and the
    # unit status table entry (decoded in judge7)
    reads += [("x10", 26), ("x11", 27), ("x12", 28), ("amr", 0o224032),
              ("uat0", 0o214676), ("uat1", 0o214677), ("ust0", 0o214772),
              ("ust1", 0o214773)]
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
    reads += [("stic", at("STIC"))]
    reads += [(nm.lower(), d.symtab[nm] // 64) for nm in ("STOPC", "NDFT", "FLOGP")]
    reads += [("cwa", at("CWA")), ("cbta", at("CBTA")), ("cbwa", at("CBWA")),
              ("sl", at("SL"))]
    # the dump: the deck (200000-214777) and the output program's print
    # buffers CX and CY (p.209 l.56 - p.210 l.3), up to 223177
    reads += [(nm.lower(), d.symtab[nm] // 64) for nm in ("NMRET", "SICB2")]
    reads += [("sxchan", at("SXCHAN")), ("smcp", at("SMCP")), ("sbamcp", at("SBAMCP"))]
    reads += [("ld_%o" % w, w) for w in sorted(load_oracle())]
    reads += [("mretl%d" % k, d.symtab["MRETL"] // 64 + k) for k in range(4)]
    reads += [("ptrp", d.symtab["PTRP"] // 64)]
    reads += [("ptrl%d" % k, d.symtab["PTRL"] // 64 + k) for k in range(192)]
    reads += [("flog%d" % k, d.symtab["FLOG"] // 64 + k) for k in range(4 * FLOG_N)]
    reads += [("lw%d" % k, k) for k in range(16)]     # words 0-15 at the stop
    progs = [progA] if os.environ.get("R2G_ONLY6") else [progA, prog]
    for x in extra:
        progs += [x[0], x[1]]
    # R2G_ONLY8 (measurement only): stage 8's bench alone
    res = [] if os.environ.get("R2G_ONLY8") else run_bench(tmp, "StretchBssGoLoadTb", progs, reads, stop_hw=halt,
                    step_cap=int(os.environ.get("R2G_STEPS", 12000000)), cycle_bound=60000000,
                    mem_dump=(0o200000, 0o23200), operator_signal=oper, reel=reel,
                    tape_ready=tape_ready)
    global JOB2
    JOB2 = None
    if not measure and not os.environ.get("R2G_ONLY6") and not os.environ.get("R2G_NOJOB2") \
            and os.environ.get("R2G_TAMPER", "") in ("", "job2nocs", "job2nojob"):
        JOB2 = stage8(tmp, prog, reads, S, d)
    for r in res + (JOB2 or []):
        if r[0] is not None:
            r[0]["_twsf"] = d.symtab["SSTOP"] // 32
            r[0]["_flog"] = d.symtab["FLOG"] // 64
            r[0]["_ptrl"] = d.symtab["PTRL"] // 64
            r[0]["_areas"] = d.areas
    if measure:
        return res, p2, imgs, exp, d, sym2, extra
    return res, p2, imgs, exp, d, sym2


# ---- stage 8: the next job card at ZJOBC1 ----------------------------------
# C22-6678-1 printed p.7 (PDF 7, read in the ink): "One JOB card and one TYPE
# card must be at the beginning of every problem program in that order";
# the JOB card is "B JOB, any identification", JOB in columns 10-13.  The
# second job is CHOSEN: a JOB card and a TYPE,GO card, the two cards the
# model's 32-word reader holds (15 words a card).
JOB2_CARDS = [type_card("JOB,SECOND"), type_card("TYPE,GO")]
# Where stage 8 stops: the spooler's B,DMCP / ,DRIO at p.224 ll.16-17 (PDF
# 231), 224526.00, its wait for reader I/O after "SERVICE THE CARD READER".
JOB2_STOP = 0o224526 * 2
# Stage 8's traps after the stage-7 ones (STIC; every page named here is
# read in the ink, 2026-11-19).
JOB2_TRAPS = [
    (0o224172 * 64 + 32, "p.215 l.40 ,DCCW: the spooler takes the reader's CS"),
    (0o224237 * 64, "p.216 l.51 ,DRD: the spooler READs the reader"),
    (0o224451 * 64, "p.222 l.31 ,DRET at VRTN"),
    (0o224634 * 64, "p.226 l.42 ,DCCW at VEE: the READ's end exception"),
    (0o224451 * 64, "p.222 l.31 ,DRET at VRTN"),
    (0o20421 * 64, "p.391 l.42 ,SDRET: ZJOBC1's $RET; JC4, primed, runs again"),
    (0o20031 * 64 + 32, "p.382 l.1 ,SSCR4: the 1ST CARD REQUEST again"),
    (0o224451 * 64, "p.222 l.31 ,DRET: the JOB card in hand"),
    (0o222146 * 64 + 32, "p.201 l.54 ,$RET at ARET1: the JOB card on the spool listing"),
    (0o20054 * 64 + 32, "p.382 l.34 ,67.0: to $SPU with the JOB card (l.36)"),
    (0o222146 * 64 + 32, "p.201 l.54 ,$RET at ARET1"),
    (0o20056 * 64 + 32, "p.382 l.38 ,DTIME"),
    (0o20060 * 64, "p.382 l.41 ,DCOMM: the job's name and time to the operator"),
    (0o222146 * 64 + 32, "p.201 l.54 ,$RET at ARET1"),
    (0o20074 * 64, "p.383 l.4 ,SLOG4: logger 4, the beginning of the job"),
    (0o233147 * 64 + 32, "JUNDEF's $RET (MIFTTT 80.32 UNDEF, p.121 l.47)"),
    (0o20076 * 64, "p.384 l.7 ,DSCR: YTCSR, GET 1 CARD -- the TYPE card"),
    (0o224451 * 64, "p.222 l.31 ,DRET: the TYPE card in hand"),
    (0o20235 * 64 + 32, "p.387 l.9 ,DSCR: YRDFSO reads the next card"),
    (0o224217 * 64 + 32, "p.216 l.24 ,DCOMM: SERVICE THE CARD READER")]
# The next trap would be p.224 l.17's ,DRIO (STIC 224526.40), but the bench
# stops on the step that executes l.16's B,DMCP: the branch is suppressed,
# the IF is pending and the PC reads the ,DRIO half-word (224526.40) -- so
# that trap is not yet logged.  (A run to the step cap logs it as the 21st,
# measured 2026-11-19, 37 traps after the entry.)
JOB2 = None


def stage8(tmp, prog, reads, S, d):
    """Stage 7's program on a bench whose reader holds JOB2_CARDS: the
    operator readies the tape at KCHOPN as in stage 7, then, when job
    control first waits at ZJOBC1, loads the deck and readies the reader
    (channel 32, the system input reader IPL named: "READER IS INPUT SOURCE
    ON CHANNEL 32"): a CS (Reference Manual printed p.116)."""
    reel = os.path.join(tmp, "outpt2.tape")
    with open(reel, "wb") as fh:
        fh.write(bytes(8 * REEL_WORDS))
    oper = [(S["KCHOPN"] // 32, 34, 0), (S["ZJOBC1"] // 32, 32)]
    if os.environ.get("R2G_TAMPER") == "job2nocs":
        oper = oper[:1]
    deck = JOB2_CARDS
    if os.environ.get("R2G_TAMPER") == "job2nojob":
        deck = [type_card("JOX,SECOND")] + deck[1:]
    words = [w for c in deck for w in cards.card_words(c)]
    halt = int(os.environ.get("R2G_STOP8", 0)) or (d.symtab["SSTOP"] // 32, JOB2_STOP)
    return run_bench(tmp, "StretchBssGoJob2Tb", [prog], reads, stop_hw=halt,
                     step_cap=int(os.environ.get("R2G_STEPS8", 4500000)),
                     cycle_bound=60000000, mem_dump=(0o200000, 0o23200),
                     operator_signal=oper, reel=reel, tape_ready=0, reader_image=words)


def judge8(res, S):
    """Stage 8: how far the second job gets."""
    g, out = res[0]
    if g is None:
        check("8: the job-2 bench ran", out[-2000:], "")
        return
    nt = (field(g["ptrp"], 0, 24) // 64 - g["_ptrl"]) // 3
    traps = [(field(g["ptrl%d" % (3 * k)], 0, 24), g["ptrl%d" % (3 * k + 1)])
             for k in range(min(nt, 64))]
    print("INFO stage 8: stopped at %s, STOPC %s, STIC %o, %s cycles, %d traps after the"
          " entry" % (g["_stopped"], field(g["stopc"], 0, 18), field(g["stic"], 0, 24),
                      g["_cycles"], nt))
    for k, (a, b) in enumerate(traps):
        print("INFO   8 trap %2d: STIC %o.%02o" % (k, a // 64, a % 64))
    print("INFO stage 8: operator %s; reports %s; %d disk (channel 0) reports" % (
        g["_operat"], " ".join("%s:%s" % r for r in g["_reports"]), g["_dreports"]))
    for k, w in enumerate(g["_typed"]):
        print("INFO   8 typed %2d: %s %r" % (k, w, a8_text(int(w, 16))))
    print("INFO stage 8: %d tape words written" % len(g["_tape"]))
    for nm in ("ust0", "ust1"):
        print("INFO   8 %s at the stop: %016x" % (nm, g[nm] or 0))
    import check_console_text
    text = " ".join(check_console_text.console_text(out).split())
    print("INFO stage 8: console %r" % text)
    ops = g["_operat"]
    check("8: OPERATOR ACTIONS: tape unit 0 readied at KCHOPN, then the deck loaded and the"
          " reader readied (channel 32, CS) at job control's first arrival at ZJOBC1",
          [(c, h) for c, h, _st in ops], [(34, S["KCHOPN"] // 32), (32, S["ZJOBC1"] // 32)])
    check("8: the reader's reports: its CS, then the READ's end -- EE with EOP, the model's"
          " reader running out of its 32-word image (FIXTURE: a real empty hopper is not"
          " ready)", [r for r in g["_reports"] if r[0] == "32"], [("32", "00001"), ("32", "00110")])
    check("8: the job is announced as C22-6678-1 p.7 says (the JOB card's first eight"
          " characters typed), and then the spooler asks for cards (p.216 l.24)", text,
          "SECOND 00:00:01 SERVICE THE CARD READER")
    check("8: the traps from the reader's CS on, each named (pp.215-226, 382-391, 201)",
          [a for a, _b in traps[16:]], [a for a, _n in JOB2_TRAPS])
    check("8: the TYPE card went through IBM's UNCODE normally (p.384 ll.12-20, not l.18's"
          " error return): KSILO+1.18-22 = 00100, TYPE,GO's count (as stage 1b)",
          field(g["ks1"], 18, 5), 0b00100)
    check("8: and the run stops at the spooler's wait: p.224 l.16's B,DMCP (224526.00)"
          " executed, its IF pending, the PC at l.17's ,DRIO (224526.40)",
          g["_stopped"], JOB2_STOP + 1)


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
            ms = [t for t in os.environ.get("R2G_MEASURE", "").split(",") if t]
            res34 = stage34(tmp, st["GO,FORTRAN"], ms)
            if not os.environ.get("R2G_ONLY8"):
                judge34(*res34[:6])
            if len(res34[0]) > 1:
                judge7(res34[0][1][0], res34[0][0][0], image().symtab, res34[3])
            if JOB2:
                judge8(JOB2, image().symtab)
            if ms:
                measure_report(res34, ms)
    print("ALL CHECKS PASSED" if not fails else f"{fails} FAILED")
    return 1 if fails else 0


def measure_report(res34, ms):
    """R2G_MEASURE (measurement only): judge each tamper's two runs from the
    shared bench, under its R2G_TAMPER, and print its FAIL lines."""
    import contextlib
    import io
    global fails
    res, extra = res34[0], res34[6]
    keep = fails
    for k, t in enumerate(ms):
        progA, prog, p2, imgs, exp, d = extra[k]
        sym2 = lambda n, p2=p2: p2.val.symbol_value(p2.st.search(n))[0]   # noqa: E731
        rr = res[2 + 2 * k: 4 + 2 * k]
        buf = io.StringIO()
        fails = 0
        with contextlib.redirect_stdout(buf):
            def go():
                judge34([rr[0]], p2, imgs, exp, d, sym2)
                if rr[1][0] is not None:
                    judge7(rr[1][0], rr[0][0], image().symtab, exp)
            with_tamper(t, go)
        lines = buf.getvalue().splitlines()
        bad = [ln for ln in lines if ln.startswith("FAIL")]
        print("MEASURE %s: %d FAIL, %d PASS" % (t, len(bad),
                                               sum(ln.startswith("PASS") for ln in lines)))
        for ln in bad:
            print("MEASURE %s   %s" % (t, ln[:250]))
        for ln in lines:
            if ln.startswith("INFO stage 6") or ln.startswith("INFO stage 7"):
                print("MEASURE %s   %s" % (t, ln))
    fails = keep


def judge6(g, S):
    """Stage 6: $EOJ past YC4B3, IBM's code from YMPFCH to TASIGN."""
    print("INFO stage 6: stopped at %s, STOPC %s, NFET %s, STIC %o"
          % (g["_stopped"], field(g["stopc"], 0, 18), field(g["nfet"], 0, 18),
             field(g["stic"], 0, 24)))
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
    ks8 = g["ks8"]
    check("6: YTSP still 0: bypass mode, p.397 l.6 BB,SYSMOD,TJUNAS ('-IF BYPASS') skips"
          " ll.7-8", field(g["ytsp"], S["YTSP"] % 64, 1), 0)
    check("6: SCNFCG still 1 and WJCW's flag 0: WJ4PFF (p.388 l.28) is not on the bypass"
          " path", (field(g["scnfcg"], S["SCNFCG"] % 64, 1), field(g["wjcw"], 0, 1)), (1, 0))
    check("6: YL1 (p.384 ll.36-39) took the PP limits from KSILO+8 (p.397 l.3): YEDLL,"
          " SLRBU+.32 = its value, SLRBU.0-17 = its count (the model's SC"
          " stores a count in the half word's bits 0-17)",
          (field(g["yedll"], 0, 24), field(g["slrbu"], 32, 24), field(g["slrbu"], 0, 18)),
          (field(ks8, 0, 24), field(ks8, 0, 24), field(ks8, 28, 18)))
    check("6: YPPID4 (p.387 ll.22-27) asks for '))))))))' (TI,1,YDFCS,YI4TA)",
          field(g["yi4ta"], 0, 48), a6(TWS_NAME))
    check("6: ... RELFWA 2.0, past the arc's two header words: YPPBSD -13. + 15. (p.397"
          " l.18; p.387 l.23 V+IC, l.27 SV,13,YI4TA+1.)", field(g["yi4ta1"], 0, 24), 2 * 64)
    check("6: on IPL's words: SXCHAN 214724.00 with count 36, SMCP and SBAMCP 214514.00"
          " (the assembled image: 0, 215000.00, 215000.00; p.103)",
          (field(g["sxchan"], 0, 24), field(g["sxchan"], 28, 18), field(g["smcp"], 0, 24),
           field(g["sbamcp"], 0, 24)), (0o214724 * 64, 36, 0o214514 * 64, 0o214514 * 64))
    check("6: the first run halted at the second $FETCH (HALT2), from YPPID4's B,DMCP /"
          " ,DFETCH (p.387 ll.29-30)",
          (g["_stopped"], field(g["stopc"], 0, 18), field(g["nfet"], 0, 18),
           field(g["fstc2"], 0, 24)),
          (g["_twsf"], 8, 2, S["YI4TA"] - 32))


def lib_used():
    """The library decks Example 4's calls bring in, in the order
    check_bss_example4.expect fetches them."""
    import check_bss_example4 as ex4
    known = {e for sb in ex4.SUBS for e, _w in sb[0]}
    queue, used = [c for sb in ex4.SUBS for c in sb[4]], []
    while queue:
        c = queue.pop(0)
        if c in known:
            continue
        nm = next(n for n, sb in ex4.LIB.items() if c in [e for e, _w in sb[0]])
        used.append(nm)
        known |= {e for e, _w in ex4.LIB[nm][0]}
        queue += ex4.LIB[nm][4]
    return used


# THE COMPILED PROGRAM IS LOST.  No 7030 FORTRAN object deck, and no code
# of the FORTRAN library (FISIP*, IOCS*, SPTXT*, UST*), is held
# (docs/archival_inventory.md; fortran_bss_plan.md section 2.4): Example 4's
# subprograms are stubs of p.17's sizes (check_bss_example4).  *MAIN*'s
# entry, B,E0 / NOP there (a branch to itself), is here B,$MCP / ,$EOJ
# (SCAFFOLD, CHOSEN): C22-6751 p.23 makes a main-program RETURN a "good
# stop" that returns to MCP, and $EOJ is MCP's normal end (C22-6678-1
# p.22).  What the compiler really emitted there (after the call to the
# initializing routine it inserts first, p.23) is not printed.  The
# map is unchanged: the body is one word, as B,E0 / NOP was.
MAIN_BODY = {0: ["B,$MCP", ",$EOJ"]}


def go_subs():
    import check_bss_example4 as ex4
    return [ex4.SUBS[0] + (MAIN_BODY,)] + list(ex4.SUBS[1:])


def main_entry():
    """*MAIN*'s entry, a half-word address, from p.17's map (000051.0)."""
    import check_bss_example4 as ex4
    r = next(r for r in ex4.MAP_SUB if r[0] == "*MAIN*")
    return (int(r[1], 8) + int(r[2].split(".")[0], 8)) * 2 + r[2].endswith(".4")


def load_oracle():
    """What the GO phase's load must leave, from p.17's map (C28-6379 p.17,
    check_bss_example4.MAP_SUB): for each subprogram and each library deck
    the calls bring in, at its printed origin, the stub's first word
    XW,0,<calls>; its transfer vector, each word the skeleton B,entry;NOP
    with the callee's printed entry (as check_bss_mcp_load's oracle); and at
    each entry past word 0 its B,E;NOP, the branch relocated to itself."""
    import check_bss_example4 as ex4
    org = {r[0]: int(r[1], 8) for r in ex4.MAP_SUB}
    ep = {r[0]: (int(r[1], 8) + int(r[2].split(".")[0], 8)) * 2 + r[2].endswith(".4")
          for r in ex4.MAP_SUB}
    skel = ex4.tvskel()
    want = {}
    for sb in list(go_subs()) + [ex4.LIB[n] for n in lib_used()]:
        entries, _size, _blank, _commons, calls = sb[:5]
        body = sb[5] if len(sb) > 5 else {}
        o = org[entries[0][0]]
        want[o] = assemble("        SLC,(8)%o.0\n        XW,0,%d\n" % (o, len(calls))).words[o]
        for i, c in enumerate(calls):
            want[o + 1 + i] = (skel & ~(((1 << 19) - 1) << 45)) | (ep[c] << 45)
        for _n, w in entries:
            if w and body:
                # the SCAFFOLD body, absolute: B,$MCP / ,$EOJ = B,32.0 / ,65.0
                # (C22-6678-1 p.22; $MCP = 32.0, p.108 l.5; $EOJ = 65.0)
                want[o + w] = assemble("        SLC,(8)%o.0\n        B,32.0\n        ,65.0\n"
                                       % (o + w)).words[o + w]
            elif w:
                want[o + w] = assemble("        SLC,(8)%o.0\n        B,(8)%o.0\n        NOP\n"
                                       % (o + w, o + w)).words[o + w]
    return want


def fetch_log(g):
    """The stub's FLOG: every $FETCH, in order, as (STIC, name, RELFWA, FWA,
    N) from its calling sequence (C22-6678-1 p.21), the name decoded
    against the disk's dictionary ('?' + octal for a name it lacks)."""
    names = {a6(nm): nm for nm, _a, _n in g["_areas"]}
    n = (field(g["flogp"], 0, 24) // 64 - g["_flog"]) // 4
    out = []
    for k in range(n):
        w = [g.get("flog%d" % (4 * k + i)) for i in range(4)]
        if None in w:
            break
        nm = field(w[1], 0, 48)
        out.append((field(w[0], 0, 24), names.get(nm, "?%016o" % nm), field(w[2], 0, 24),
                    field(w[2], 32, 24), field(w[3], 0, 24)))
    return out


def judge7(g, g6, S, exp):
    """Stage 7: the GO phase past the fetch of '))))))))' (the second run)."""
    import check_bss_example4 as ex4
    if g is None:
        check("7: the second run ran", g6, None)
        return
    full = fetch_log(g)
    first_eoj = [k for k, e in enumerate(full) if e[1] == EOJ_NAME][0]
    log = [(f, r, nm) for f, nm, r, _fwa, _n in full[first_eoj + 1:]]
    sizes = {nm: n for nm, _a, n in g["_areas"]}
    print("INFO stage 7: stopped at %s, STOPC %s, %d fetches in all, %d past the $EOJ"
          " program's, %d calls from DISK FETCH's own code after the entry, %s cycles"
          % (g["_stopped"], field(g["stopc"], 0, 18), len(full), len(log),
             field(g["ndft"], 0, 18), g["_cycles"]))
    for k, (f, r, nm) in enumerate(log):
        print("INFO   fetch %2d: %-8s RELFWA %6o.%02o from ,DFETCH at %o.%02o"
              % (k, nm, r // 64, r % 64, f // 64, f % 64))
    mr = [field(g["mretl%d" % k], 0, 24) for k in range(4)]
    check("7: the fetch of '))))))))' at RELFWA 2.0 from YPPID4 (p.387 ll.29-30) is served"
          " first", log[:1], [(S["YI4TA"] - 32, 128, TWS_NAME)])
    # p.385 ll.1-13 send the card (the first binary card of *MAIN*) to
    # UNCODE, whose error return goes YIDCER -> YBCERR (p.392 ll.27-31,
    # 37-51): no IOD card was read, so WJC4G1 (p.386 l.7; SCORG 0) ->
    # WJC4G primes $RESLD (ll.23-25) and gives $RET at l.31 (020217.40).
    check("7: the next MCP call is WJC4G's $RET, ,SDRET at 020217.40 (p.386 l.31): no IOD"
          " card, so YBCERR took WJC4G1 (p.392 l.51)", mr[0], 0o20217 * 64 + 32)
    check("7: then YRESLD -> YMPFCH (p.291 ll.50-51) fetched 22LOADER, RELFWA 0",
          [(r, nm) for _f, r, nm in log[1:2]], [(0, "22LOADER")])
    sub_cards = sum(len(ex4.punch(ex4.stub_source(*sb))) for sb in go_subs())
    want_tws = [(2 + ex4.tws_offset(k)) * 64 for k in range(sub_cards)]
    got_tws = [r for _f, r, nm in log[2:] if nm == TWS_NAME]
    check("7: resume load as the BSS postprocessor (C22-6728-1 p.86) read every subprogram"
          " card on TWS once, in order, and not the branch card (%d cards)" % sub_cards,
          got_tws, want_tws)
    used = lib_used()
    got_lb = []
    for _f, r, nm in log[2:]:
        if nm.startswith("LB") and nm not in got_lb:
            got_lb.append(nm)
    check("7: ... and the library decks the calls bring in, from their LB areas: %s"
          % ", ".join(used), sorted(got_lb), sorted("LB" + n.ljust(6)[:6] for n in used))
    # The end of a library deck: the loader asks for the card past the
    # area's last (RELFWA = its size; a library entry's count is 0, p.324
    # l.28), DISK FETCH takes the end return (p.315 ll.28-39, SIZE-BETA not
    # above 0), and YLERR (p.332 l.41) ends the routine.
    ends = [nm for _f, r, nm in log if nm.startswith("LB") and r == 64 * sizes.get(nm, -1)]
    check("7: one fetch past the end of each library deck's area, the end return (DISK"
          " FETCH p.315 ll.28-39; YLERR, p.332 l.41), and no other past an area's end",
          (sorted(ends), [(nm, r) for _f, r, nm in log if r >= 64 * sizes.get(nm, 0)
                          and not nm.startswith("LB")]),
          (sorted("LB" + n.ljust(6)[:6] for n in used), []))
    other = [(f, nm) for f, _r, nm in log[2:] if nm != TWS_NAME and not nm.startswith("LB")]
    check("7: no fetch of anything else but, after the program's $EOJ, 22$EOJ once, from"
          " YMPFCH's YFDO (p.269 ll.22-23)", other, [(S["YFDO"] + 32, EOJ_NAME)])
    main = field(exp["ksilo"][ex4.KSILO + 10], 0, 19)
    check("7: resume load's $RET (p.333 ll.4-5, in the LOADER) with SICBU = *MAIN*'s entry"
          " %o.%02o (KSILO+10, p.17's map); two MCP $RETs in all" % (main // 2, main % 2 * 32),
          (field(g["nmret"], 0, 18), LOADER_AT * 64 <= mr[1] < 0o237000 * 64,
           field(g["sicb2"], 0, 24)), (2, True, main * 32))
    # MCP's own $RET path (SIFAE p.117 l.19 -> KFRONT p.177 -> KPLUG1 p.178
    # -> CRETN p.140 -> MDRET p.141 -> MUP1 -> MPP1 p.142 -> CRETBU ll.41-51)
    # restores the PP's registers from SLRBU (l.50 T,15,SLRBU,3.0) and
    # BE's to SICBU: the run arrives at *MAIN*'s entry with SL = 0 (l.42)
    # and the boundary register = SLRBU's word (the PP limits YL1 set).
    # The traps after the program is entered (STUBIF's PTRL: STIC, word 3,
    # SCOMRG at each), all served by MCP's own SIFAE but $FETCH.
    nt = (field(g["ptrp"], 0, 24) // 64 - g["_ptrl"]) // 3
    traps = [(field(g["ptrl%d" % (3 * k)], 0, 24), g["ptrl%d" % (3 * k + 1)],
              field(g["ptrl%d" % (3 * k + 2)], S["SL"] % 64, 1))
             for k in range(min(nt, 64))]
    for k, (a, b, sl) in enumerate(traps):
        print("INFO   trap %d after the entry: STIC %o.%02o, word 3 %016x, SL %d"
              % (k, a // 64, a % 64, b or 0, sl))
    check("7: the first trap after CRETBU (p.142 ll.41-51) is *MAIN*'s ,$EOJ at %o.%02o (its"
          " SCAFFOLD body ran from the entry %o.%02o): SL = 0, word 3 (the boundaries) = SLRBU,"
          " the PP limits" % (main // 2, main % 2 * 32 + 32, main // 2, main % 2 * 32),
          traps[:1], [(main * 32 + 32, g["slrbu"], 0)])
    # Then MCP's $EOJ, all IBM's code but the $FETCH: SIFAE's PP half
    # (p.117 ll.21-28) -> MIF6 -> YJC4TT -> YC4NO -> YC4B3 -> YMPFCH's
    # $FETCH of 22$EOJ (YFDO, p.269) -> p.381 (PDF 131) ll.11-17, SCORG 0, so
    # l.20-21 B,DMCP / ,SKOM (input commands, MIFTTT 79.32 VVSKM, p.121
    # l.45), whose spooler gives $RET at VSSKOM+3.40 (224147.40); ll.26-27
    # ,SLOG2 (81.0, MIFTTT p.121 l.48: UNDEF), whose JUNDEF gives $RET
    # (233147.40); l.37 ,SSPEOJ (77.32, SAEOJT, "OUTPUT EOJ", p.121 l.41),
    # and the print program's output EOJ reaches p.204 (PDF 211) ll.8-9
    # B,$MCP / ,$W at 222265.40, the record's write.
    want = [0o51 * 64 + 32, S["YFDO"] + 32, 0o20007 * 64 + 32, 0o224147 * 64 + 32,
            0o20013 * 64, 0o233147 * 64 + 32, 0o20021 * 64, 0o222266 * 64]
    check("7: then MCP's own $EOJ path: YMPFCH's $FETCH, p.381's ,SKOM, VSSKOM's $RET, ,SLOG2,"
          " JUNDEF's $RET, ,SSPEOJ, and p.204 l.9's ,$W", [a for a, _b, _s in traps[:8]], want)
    # The $W is taken by KFRONT (p.177) -> KIODRN -> KMCP (p.179 l.4) ->
    # KNOGO (p.179 ll.13-25) -> KCHOPN, where the bench stops.  MEASURED
    # without the stop (2026-11-19): KCHOPN -> KSUPP suppresses the $W and
    # it traps again from 222266.00, again and again, to the step cap.
    print("INFO stage 7: %d operator action(s); reports %s; %d disk (channel 0) reports;"
          " %d words typed; %d tape words written"
          % (g["_oper"], " ".join("%s:%s" % r for r in g["_reports"]), g["_dreports"],
             len(g["_typed"]), len(g["_tape"])))
    for k, (a, v) in enumerate(g["_tape"]):
        print("INFO   tape write %2d: position %5d  %016x  %r" % (k, a, v, a8_text(v)))
    for k, (a, b, sl) in enumerate(traps[10:], 10):
        print("INFO   trap %d after the entry: STIC %o.%02o, word 3 %016x, SL %d"
              % (k, a // 64, a % 64, b or 0, sl))
    for nm in ("ust0", "ust1", "uat0", "uat1"):
        print("INFO   %s at the stop: %016x" % (nm, g[nm] or 0))
    if os.environ.get("R2G_TAMPER") == "nooper":
        check("7: ... and the $W goes to K NO GO (p.179 ll.13-25): the run stops at KCHOPN, the"
              " eighth trap the last", (g["_stopped"], nt), (S["KCHOPN"] // 32, 8))
    judge7_operator(g, S, traps, nt)
    judge7_units(g, S, traps)
    check("7: no other trap: still 12 $SPR, 12 PP $RET, 1 $EOJ; no bad op, no other"
          " interrupt", (field(g["nspr"], 0, 18), field(g["nret"], 0, 18),
                         field(g["neoj"], 0, 18), g["badopx"],
                         [k for k in range(64) if g["badic%d" % k]]), (12, 12, 1, 0, []))
    check("7: the loader's error word YLJSLT unchanged (p.332 l.49)", g["yljslt"],
          g6["yljslt"])
    want = load_oracle()
    bad = ["%o" % w for w in sorted(want) if g.get("ld_%o" % w) != want[w]]
    check("7: the program as loaded: each subprogram's first word, transfer vector and"
          " entries at p.17's origins (%d words)" % len(want), bad, [])


# THE TRAPS AFTER THE $W, NAMED (2026-11-19; every page read in the ink).
# Each is an IF trap of a B,$MCP / B,DMCP (STIC = the call's ,op half-word).
AFTER_W = [
    (0o222574 * 64 + 32, "p.209 l.48 ,DRET: RATPCS, CT11's SIGNAL fix-up (AXITA+4)"),
    (0o222266 * 64, "p.204 l.9 ,$W again, past K NO GO"),
    (0o222320 * 64 + 32, "p.204 l.47 ,$RET at CRET: the $W's EOP (AXITA+5 -> CEOPN)"),
    (0o222311 * 64, "p.204 l.36 ,$WEF: the output EOJ's end of file"),
    (0o222320 * 64 + 32, "p.204 l.47 again: the $WEF's EOP (AXITA+5 -> CEOPEF, p.206 l.18)"),
    (0o222146 * 64 + 32, "p.201 l.54 ,$RET at ARET1: output EOJ returns to $EOJ"),
    (0o20031 * 64 + 32, "p.382 l.1 ,SSCR4 (79.0): job control's 1ST CARD REQUEST"),
    (0o224451 * 64, "p.222 l.31 ,DRET at VRTN: the spooler returns, no card")]


def judge7_units(g, S, traps):
    """Stage 7: unit select.  The operator readied channel 34 UNIT 0 only."""
    if os.environ.get("R2G_TAMPER") in ("nooper",):
        return
    # CT21 (IOD 12, channel 34 unit 1) has UST entry 214773; IPL set its MOUNT
    # (.51) and initial-mount (.53) bits (printed p.79 ll.3-4), as CT11's.
    # p.126 l.2 (PDF 133) "BZB,KRECEP.18,KHEX -IF UNIT IS NOT READY, SKIP"
    # passes over it, so the receptor leaves both on.
    check("7u: CT21's MOUNT and initial-mount bits still on (UST 214773 .51, .53): its unit,"
          " channel 34 unit 1, was never readied, so p.126 l.2 skipped it",
          (field(g["ust1"], 51, 1), field(g["ust1"], 53, 1)), (1, 1))
    check("7u: after the $W held at K NO GO, eight traps, each named (p.209 l.48, p.204"
          " ll.9, 47, 36, 47, p.201 l.54, p.382 l.1, p.222 l.31); no signal fix-up for CT21"
          " (ATPBCS's ,$RET from 222572.40, p.209 l.44)",
          [a for a, _b, _s in traps[8:]], [a for a, _n in AFTER_W])


def judge7_operator(g, S, traps, nt):
    """Stage 7 past K NO GO: the operator readies channel 34 (OPERATOR ACTION)."""
    check("7: OPERATOR ACTION: one channel signal on channel 34, at KCHOPN (Reference Manual"
          " printed p.116: the unit made ready), then the reports MCP takes",
          (g["_oper"], g["_reports"][:1]), (1, [("34", "00001")]))
    # MCP's channel-signal receptor (KSTORE p.122 -> KSIGNL p.124 l.53 ->
    # KHUNT/KSTAB p.125 -> p.126 l.5 BZBZ,SMOUNT($11),ZRCPFC) clears the
    # unit's MOUNT bit (.51 of its UST entry, p.179's S MOUNT).
    check("7: ... and MCP's receptor cleared CT11's MOUNT bit (UST 214772 .51, p.126 l.5)",
          field(g["ust0"], 51, 1), 0)
    check("7: then seven operations on the blank OUTPT reel, each ending with EOP alone:"
          " no EPGK, no EE (density p.155 l.5, label read p.183 l.25, backspace p.155"
          " l.18, label write p.155 l.45, tape mark p.156 l.14, the $W's record p.154"
          " l.18, the output EOJ's tape mark p.164 l.33)",
          g["_reports"][1:], [("34", "00010")] * 7)
    check("7: nothing typed on the console (no mount reminder, no REPLACE TAPE)",
          g["_typed"], [])
    # THE REEL AS WRITTEN (host_tape.c's trace, in order).  p.155 l.45 writes
    # the label from E LAB CW (one word here), p.156 l.14 a tape mark after
    # it; the $W (p.154 l.18) writes the record buffer X holds (p.209 l.56:
    # CX, the control character then 12 lines of 133), and the output EOJ's
    # p.164 l.33 CTL 117 ends the file with a mark.
    import check_bss_example4 as ex4
    tape = g["_tape"]
    mark = 0x0F00000000000000
    check("7: the reel, written in order from the load point: a one-word label, a tape mark,"
          " a 150-word record, a tape mark",
          ([a for a, _v in tape], [k for k, (_a, v) in enumerate(tape) if v == mark]),
          (list(range(153)), [1, 152]))
    bits = "".join(format(v, "064b") for _a, v in tape[2:152])
    chars = "".join(A6INV.get(int(bits[i:i + 6], 2), "~") for i in range(0, len(bits) - 5, 6))
    lines = [chars[1 + 133 * i:1 + 133 * (i + 1)] for i in range(12)]
    check("7: the record is the listing: control character P (p.209 l.56), 12 single-spaced"
          " lines (C22-6678-1 p.20), headers **SUBPROGRAMS** **COMMONS**",
          (chars[:1], [ln[:1] for ln in lines], lines[0][1:121].split()),
          ("P", ["-"] * 12, ["**SUBPROGRAMS**", "**COMMONS**"]))
    subs, coms, _seps = ex4.map_rows([ln[1:121] for ln in lines])
    check("7: ... and its rows are p.17's map, every subprogram and common row",
          (subs[:len(ex4.MAP_SUB)], coms[:len(ex4.MAP_COM)]),
          (list(ex4.MAP_SUB), list(ex4.MAP_COM)))
    for k, ln in enumerate(lines):
        print("INFO reel line %2d: %s" % (k + 1, ln.rstrip()))
    check("7: and the run reaches job control's wait for the next job card, ZJOBC1 (p.391"
          " l.37, 020416.40)", g["_stopped"], S["ZJOBC1"] // 32)


def judge34(res, p2, imgs, exp, d, sym2):
    import check_bss_example4 as ex4
    g, out = res[0]
    if g is None:
        check("stage 3: the bench ran", out[-2000:], "")
        return
    mem = g.get("_mem", {})
    S = image().symtab
    print(f"INFO stage 3/4: {g.get('_cycles')} cycles")
    # Stage 3: MCP's resume load, every $FETCH MCP's own DISK FETCH.
    log = fetch_log(g)
    nb = [k for k, e in enumerate(log) if e[1] == BSS_PROC]
    pre = log[:nb[-1] + 1] if nb else log
    for k, (f, nm, r, fwa, n) in enumerate(pre[:3] + pre[-2:]):
        print("INFO stage 3 fetch: %-8s RELFWA %o.%02o FWA %o.%02o N %o.%02o from %o.%02o"
              % (nm, r // 64, r % 64, fwa // 64, fwa % 64, n // 64, n % 64, f // 64, f % 64))
    check("3: the fetches before the BSS processor ran: YMPFCH's of 22LOADER (p.269"
          " ll.22-29, RELFWA 0), then the type area BSS card by card from RELFWA 0 in"
          " 15-word steps (p.332 ll.27-41; YDKCRS count 0, no end-of-arc step), all %d"
          " cards once, the last the branch card" % len(imgs),
          [(nm, r) for _f, nm, r, _fwa, _n in pre],
          [("22LOADER", 0)] + [(BSS_PROC, 64 * 15 * k) for k in range(len(imgs))])
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
          " the first $FETCH from MCP, its linkage YFDO's B,DMCP (p.269 ll.22-23)",
          field(g["fstc1"], 0, 24), S["YFDO"] + 32)
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
