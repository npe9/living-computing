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
THE SUBPROGRAM END, 2026-11-12: the exact card count runs ARNRM2; 13
checks pass, 36,707 cycles: the vector over the A8 name at 120001, the
branch address from KSILO+10 through the branch return (the last card's
normal return goes to ERR).  MEASURED, in the reconstructed table:
  - count one high: vector_120001, branch_address_from_KSILO10 and the PC
    fail (the last card returns normally).
  - count one low: branch_address_from_KSILO10 fails alone (the card
    before ends the job; the FORTRAN branch card carries no data).
  - the vector put at word 5: vector_120001 reads Bluesim's 0xAAAA... from
    word 4, so the loader takes table + 3.0 + n.32 with n = 3 as word 4.
  - vector length 0: vector_120001 fails, the A8 name left in place.

MODE "bss2" (argv[2]): R1 of docs/reading_notes/fortran_bss_plan.md.  The
same subprogram, then a SECOND one (SUB2_SOURCE): table 1's refill, SRNXAD,
points at a second reconstructed table, so the first subprogram's last card
runs ARNRM2 -> ARNRM5 with a next table (printed p.327 ll.1-22): KSILO+9.32
takes table 2's address, YRLDTA takes ATWSTA ("))))))))", a subprogram on
TWS), $13 takes AREADS plus table 2's disk address, and the loader returns
NORMALLY.  The driver then feeds the second subprogram's binary cards as
resume load would read them.  It has four named commons (i 3 bits wide,
not 2), BL2 shared with the first at index 1 (index 2 there), its own
origin, a two-word vector at table + 5.0, and refill 0, so its last card
ends the job through ARNRM4's branch return.  ORACLE: core equals both
subprograms assembled absolute (each common at its table origin, the two
vectors over the A8 names); YRLDTA equals ATWSTA's 48 bits; $13 equals
AREADS with value -13.0 + 557.0 and count 35 - (557 mod 512) // 15 = 32,
p.327 ll.12-19 as read (the arc bits cleared by LFI(BU,9) before the /I
by 15.: 557 is arc 1, word 45, so a missed clear would give count -2).
PAGES READ IN THE INK for R1, 2026-11-16: p.291 ll.6-31 (ABSSID, ARCDCT,
ALB, ATWSTA), p.324 ll.10-29, p.326 ll.37-45, p.327 ll.1-28, p.332
ll.27-42, p.334 ll.1-19 (PDF = printed - 249 to p.328, - 250 after).
FIRST RUN, 2026-11-16: 29 checks pass, PC at DONE, 76,369 cycles ($13
first measured with disk address 5: value -8.0, count 35, as read); with
BL2 moved to index 1 (the run committed), 76,366 cycles.
MEASURED INJECTIONS (BL2 at index 1), each restored by copy and cmp:
  - wrong SRNXAD chain (table 1's refill SUB2_TABLE + 1, here): the step
    cap is reached and 17 checks fail -- every word of the second
    subprogram and its commons BL4/BL5/BL6 (121400-121600, 122000-122011,
    left sentinel), branch_address_from_KSILO10, read_source_13 and the
    PC; the first subprogram's 13 words and YRLDTA pass.
  - wrong named-common index width (strap/strap2/punch.py, w =
    (ncommon - 1).bit_length() or 1: the same 2 bits for three commons,
    2 not 3 for four): 6 fail, exactly the second subprogram's
    instruction words 122003-122010; the first subprogram passes.
MODE "bsslib": the same, but table 2 is a LIBRARY entry: word 0 bit 63 is
1 and bits 0-35 a 36-bit name (CHOSEN, "SINE  " in A6: how an A8 name
becomes 36 bits is spec G7, unprinted).  ARNRM3 (p.327 ll.23-27) must put
"LB" (ALB, p.291 l.29) and those 36 bits in YRLDTA and AREAD1 in $13.
YRLDTA = "LBSINE  " (LF(BU,12,6) and LF(BU,36,6) are connectives at byte
size 6, so each character becomes an eight-bit byte, Reference Manual p.75
as quoted in bsv/StretchVFL.bsv; SF(BU,48,6) packs the eight bytes back).
HOW A LIBRARY ROUTINE ENDS.  Its card count is set to 0 ("LIBRARY ROUTINE
CARD CT.=0", p.324 l.28) and ARNRM1 decrements before it tests (p.326
ll.41-44), so no card ends it: the first run (2026-11-16, B,NRET after
the last card) measured the count wrapping, the FORTRAN branch card
returning normally and the vector left untransmitted.  The end comes from
resume load: DFETCH's second return is B,YLERR (p.332 ll.40-41, "NOP
-FORGET ERROR RETURN." before it), and YLERR, "CASE WHERE BRANCH CARD IS
MISSING" (p.334 ll.2-3), on a BSS job whose current table is a library
one takes YAERR1, "-FETCH END RETURN ON A BSS JOB": LI(BU,18),1. "-LIBRARY
ROUTINE WAS READ" / ST(BU,18),ARCDCT / B,ARNORM (p.334 ll.12-16).  So the
driver, after the last library card, plays DFETCH reaching the end of the
LB area: LVI,$15,AEND / B,YLERR (CHOSEN: that the area's end gives this
return; DFETCH's end-of-area behaviour was not re-read for this).  ARNRM1
then counts 1 to 0, ARNRM2 sends the two-word vector and ARNRM4 ends the
job through AEND's branch return.  RUN, 2026-11-16: every check passes
(29 printed before the end-return's D check, 30 with it), PC at DONE,
76,579 cycles: both vectors sent, KSILO+10's address returned.
MEASURED, restored by copy and cmp:
  - p.334 l.14 as LI(BU,18),2. (decks/mcp_bootstrap_p334.strap): 4 fail,
    vector_122001, vector_122002 (the A8 names left), branch_address_
    from_KSILO10 and the PC (ARNRM1 counts 2 to 1 and returns normally).
  - CONTROL: a card count planted in table 2's word 0 (bits 43-45)
    changes nothing -- all pass, 76,579 cycles -- as p.324 l.24 predicts
    (the library bit sends the count to 0 before it is read).
NOT BUILT: C, P and D cards.  R0.3 is not done: printed p.329 is missing
(mcp_image.MISSING_PAGES) and not reconstructed, and P, D and every C card
with fewer than four half-words or a hex digit go through it
(bss_loader_spec.md 7.2).  One C form avoids it (an origin and four
half-words of digits 0-9, spec 7.2); it is not in this test.

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
# (p.325 lines 25-31, p.326 lines 18-25).  The card count is the deck's
# binary cards from the program card on, so the last, the FORTRAN branch
# card, takes the count to zero and runs ARNRM2 (printed p.326 l.46 - p.327
# l.30): word 1 is an index word whose count is the transfer vector's length
# and refill the next table (0: none); the vector, at table + 3.0 + n.32 (n
# named commons; the transmit takes the word), goes to origin + 1.0; the
# branch address is KSILO+10's value field, returned through the branch
# return.  The body begins as a FORTRAN subprogram does (p.184): the vector's
# length, then its A8 name, which the transmitted vector overwrites.
BSS_TV = 0o0123456701234567012345
BSS_BODY = [
    "        DD(BU,64),1",
    "        (A*)DD(BU,64,8),INPUT   *",
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

# THE SECOND SUBPROGRAM (modes bss2 and bsslib).  RECONSTRUCTION, the same
# scaffolding as above: the driver plants the lost BSS processor's second
# relocation table, and the first table's word 1 refill (SRNXAD) points at
# it.  ARNRM2-ARNRM5 (printed p.326 l.46 - p.327 l.27, as read) then: store
# the refill as KSILO+9.32, the next table's address; if that table's word 0
# bit 63 is 1 (a library routine) set resume load's type area YRLDTA from ALB
# ("LB", p.291 l.29) and word 0's first 36 bits, and $13 from AREAD1; if 0
# (a subprogram BSS left on TWS) set YRLDTA from ATWSTA ("))))))))", p.291
# l.30) and $13 from AREADS plus a disk address taken from word 0's first 18
# bits; and return NORMALLY, so resume load reads the next card from there.
# The driver plays resume load: it feeds the second subprogram's binary
# cards (CHOSEN: only its binary cards, as punched, sequence from 1; how BSS
# writes a subprogram to TWS is spec G6, unprinted).  Every field of table 2
# differs from table 1: origin, card count, four named commons not three (so
# the relocation's i field is 3 bits wide, not 2: p.324 ll.20-23), common
# origins (BL2 shared, at index 1 not 2), vector length 2 not 1, and the
# vector's place (table + 3.0 + 4.32 = word 5, not word 4).
SUB2_ORIGIN = 0o122000
SUB2_TABLE = 0o107100
# CHOSEN: table 2's word 0 bits 0-17 (TWS case), a word address on the disk
# area resume load reads: arc 1 (512 words), word 45 = 3 cards of 15 into it.
# p.327 ll.12-19, as read: $13 = AREADS (p.331 l.40, XW,-13.,35,,7) with
# its value plus this, and its count less (this mod 512) // 15 (LFI(BU,9)
# clears the arc bits before /I by 15.), the cards already past in the arc.
SUB2_DISK = 512 + 45
# CHOSEN: the library entry's 36-bit name.  How an A8 entry name reduces to
# 36 bits is UNSPECIFIED (spec G7); the driver plants six A6 characters.
SUB2_LIBNAME = "SINE  "
SUB2_TV = [0o0765432107654321076543, 0o0111122223333444455556]
SUB2_BODY = [
    "        DD(BU,64),2",
    "        (A*)DD(BU,64,8),SIN     *",
    "        (A*)DD(BU,64,8),COS     *",
    "START   L,W4",
    "        LVI,$3,W6",
    "        XW,W2,4,W5",
    "        XW,BZ2,5,START",
    "        L,B2",
    "        B,START",
    "B2      DD(BU,64),(8)6060",
    "LAST    SYN,$",
]
SUB2_COMMONS = [("", 0o121300, ["BZ2     DR(BU,64),1", "CL      SYN,$"]),
                ("BL2", 0o121100, ["W2      DR(BU,64),1"]),
                ("BL4", 0o121400, ["W4      DD(BU,64),(8)4444"]),
                ("BL5", 0o121500, ["W5      DD(BU,64),(8)5555", "        DD(BU,64),(8)5556"]),
                ("BL6", 0o121600, ["W6      DD(BU,64),(8)6666"])]
SUB2_SIZES = {"BL4": 1, "BL2": 2, "BL5": 2, "BL6": 1}


def bss_source(entry, body, commons, sizes):
    return (["        PUNFPC,LAST,CL", "%-8sENTER,START" % entry, "        PUNCDC"]
            + ["%-8sCOMBLOCK,%d" % (n, sizes[n]) for n, _a, _b in commons if n]
            + ["        PUNREL"] + body
            + sum([["        SLCRCOM,%s" % n] + b for n, _a, b in commons], [])
            + ["        FEND"])


def bss_absolute(origin, body, commons):
    return (["        SLC,(8)%o.0" % origin] + body
            + sum([["        SLC,(8)%o.0" % at] + b for _n, at, b in commons], [])
            + ["        END,START"])


SUB2_SOURCE = bss_source("SINE", SUB2_BODY, SUB2_COMMONS, SUB2_SIZES)
SUB2_ABSOLUTE = bss_absolute(SUB2_ORIGIN, SUB2_BODY, SUB2_COMMONS)


def bss_table(ncards, origin, tv, refill, commons):
    """The reconstructed relocation table: {word offset: value}."""
    n = len(commons) - 1
    t = {0: ncards << (63 - 45),                       # word 0 bits 28-45: card count
         1: ((origin * 64) << 40) | (len(tv) << 18) | refill,   # origin; vector length; SRNXAD
         2: n << 45}                                   # word 2 bits 0-18: named commons
    for k, (_n, at, _b) in enumerate(commons[1:], 1):
        w, half = divmod(2 * 2 + k, 2)
        t[w] = t.get(w, 0) | ((at * 64) << (40 - 32 * half))
    v0 = (3 * 64 + n * 32) // 64                       # the transmit takes the word
    for j, v in enumerate(tv):
        assert v0 + j not in t
        t[v0 + j] = v
    return t


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


def pcname(module):
    """Mode pcname (plan R0.5): printed p.395 ll.47-49, the $EOJ's naming of
    the processor-control type area, run on the model as printed:
    L(BU,48),YUCBF2+2.0 / LFI(BU,12),YCCIN,48 / ST(BU,48),YDFCTA,12, with
    YCCIN the printed DDI's value (p.396 l.29, +00004763) and the third
    field FORTRAN (YFORTR, p.274 l.13) or BSS (ABSSID, p.291 l.8, as
    p.271 ll.46-50 put it there for a GO job).  YDFCTA must then hold
    "PCFORTRA" / "PCBSS   " (prosa_dict.pc_area) in bits 0-47, its other 16
    bits untouched.
    FIRST RUN, 2026-11-16: 2 checks pass, 110 cycles.  MEASURED, restored by
    copy and cmp: LFI written (BU,12,6), byte size 6 where p.395 l.48's
    printed binary has 000 (8): both fail, bits 0-7 0x73 not 0x9F (the
    connective spreads P and C into eight-bit bytes, so the name is
    shifted)."""
    import prosa_dict
    SENT = 0x5555555555555555
    src = ["        SLC,(8)%o.0" % DRIVER_AT,
           "YCCIN   SYN(BU,12,6),(8)4763",
           "START   L(BU,48),F1+2.0",
           "        LFI(BU,12),YCCIN,48",
           "        ST(BU,48),T1,12",
           "        L(BU,48),F2+2.0",
           "        LFI(BU,12),YCCIN,48",
           "        ST(BU,48),T2,12",
           "DONE    B,DONE",
           "        CNOP",
           "T1      DD(BU,64),(8)%o" % SENT,
           "T2      DD(BU,64),(8)%o" % SENT,
           "F1      DR(BU,64),2",
           "        CNOP",
           "        (AX)DD(BU,48,6),FORTRAN X",
           "        CNOP",
           "F2      DR(BU,64),2",
           "        (A*)DD(BU,48,6),BSS     *",
           "        END,START"]
    d = assemble("\n".join(src) + "\n")
    checks = []
    for lab, f3 in (("T1", "FORTRAN "), ("T2", "BSS     ")):
        want = (prosa_dict.a6(prosa_dict.pc_area(f3)) << 16) | (SENT & 0xFFFF)
        checks.append(("pc_area_%s" % f3.strip(), str(d.symtab[lab] // 64), want))
    print(generate(module, d, checks, pc_check=d.symtab["DONE"] // 32,
                   cycle_bound=100000, step_cap=10000,
                   fast_load=os.path.join(os.path.abspath(STRETCH), "bsv", "build-loader",
                                          module + ".hex")))


def main():
    module = sys.argv[1]
    mode = sys.argv[2] if len(sys.argv) > 2 else ""
    if mode not in ("", "rel", "fortran", "bss", "bss2", "bsslib", "pcname"):
        raise SystemExit("mode: none, rel, fortran, bss, bss2, bsslib or pcname, not %r" % mode)
    if mode == "pcname":
        return pcname(module)
    two = mode in ("bss2", "bsslib")
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
    elif mode.startswith("bss"):
        p2 = compile_lines(BSS_SOURCE)
        if p2.punch.unwritten:
            raise SystemExit("the punch did not write the deck: %s" % p2.punch.unwritten)
        imgs = p2.punch.deck_images(clock=0o1234)
        kinds = [how if how == "text" else c.kind for how, c in p2.punch.deck()]
        expect = compile_lines(BSS_ABSOLUTE)
        boundary = None
        if two:
            # The first subprogram's last card returns normally into the
            # second's cards: the binary cards alone, as resume load would
            # read them from TWS or the library (CHOSEN, see SUB2_ABSOLUTE).
            q2 = compile_lines(SUB2_SOURCE)
            if q2.punch.unwritten or q2.msg.items:
                raise SystemExit("the punch, subprogram 2: %s %s" % (q2.punch.unwritten, q2.msg.items))
            boundary = len(imgs) - 1
            for how, c in q2.punch.deck():
                if how == "binary":
                    imgs.append(q2.punch._encode(c, c.seq, 0o1234))
                    kinds.append(c.kind)
            expect2 = compile_lines(SUB2_ABSOLUTE)
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
           "YLERR   SYN,(8)%o.%02o" % (S["YLERR"] // 64, S["YLERR"] % 64),
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
                "        B,ERR" if two and k == boundary else "        B,DONE",
                "BA%d     VF,0" % k]
        if mode in ("bss", "bss2") and k == len(imgs) - 1:
            drv.append("        B,ERR")         # the last card must branch-return
        if mode == "bsslib" and k == len(imgs) - 1:
            # The count of a library routine is 0 and never ends it
            # (p.324 l.28); resume load's DFETCH reaches the end of the LB
            # area and takes its second return, B,YLERR (p.332 ll.40-41),
            # whose YAERR1 "-FETCH END RETURN ON A BSS JOB" sets the count
            # to 1, "-LIBRARY ROUTINE WAS READ", and goes to ARNORM (p.334
            # ll.12-16).  The driver plays DFETCH's end return, with $15 at
            # a calling sequence as resume load's YLOADA would be.
            drv += ["        LVI,$15,AEND",
                    "        B,YLERR",
                    "AEND    VF,YBCBU",
                    "        ,LOWLIM",
                    "        ,HIGHLIM",
                    "        B,ERR",
                    "DEND    VF,0",
                    "        B,DONE",
                    "BAEND   VF,0",
                    "        B,ERR"]
        if two and k == boundary:
            # SRNXAD nonzero: ARNRM2's normal return (p.327 l.22 or l.27).
            # Keep the read source resume load would use.
            drv.append("        SX,$13,SAV13")
        if mode == "fortran":
            drv.append("        B,ERR")         # a normal return is wrong here
            drv.append("E%d      NOP" % k)       # the error return: next card
    drv += ["        B,DONE", "ERR     B,ERR", "DONE    B,DONE"]
    if two:
        drv += ["SAV13   XW,0"]
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
    if mode.startswith("bss"):
        ks = S["KSILO"] // 64
        words[ks + 2] = image.words[S["ABSSID"] // 64]
        words[ks + 9] = ((0o121300 * 64) << 40) | ((BSS_TABLE * 64) << 8)
        ncards = sum(1 for how, _c in p2.punch.deck() if how == "binary")
        # table 1: count, origin 120000, vector length 1, refill table 2 or 0
        tables = [(BSS_TABLE, bss_table(ncards, 0o120000, [BSS_TV],
                                        SUB2_TABLE if two else 0, BSS_COMMONS))]
        if two:
            n2 = sum(1 for how, _c in q2.punch.deck() if how == "binary")
            t2 = bss_table(n2, SUB2_ORIGIN, SUB2_TV, 0, SUB2_COMMONS)
            if mode == "bss2":
                t2[0] |= SUB2_DISK << 46                 # bits 0-17: the disk address
            else:
                import prosa_dict
                t2[0] = ((prosa_dict.a6("XX" + SUB2_LIBNAME) & ((1 << 36) - 1)) << 28) | 1
            tables.append((SUB2_TABLE, t2))
        bss_start = expect.val.symbol_value(expect.st.search("START"))[0]
        words[ks + 10] = bss_start << 40
        for at, t in tables:
            for w, v in t.items():
                if at + w in words:
                    raise SystemExit("the table overlaps the image")
                words[at + w] = v

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
    if mode.startswith("bss"):
        # What the absolute assembly's own deck loads (punch.load, the
        # absolute path that mode "" runs on IBM's loader): the punch puts a
        # half-word rounded over before a full-word instruction on the card as
        # zeros, which the image's written mask leaves out.
        from strap2.punch import load as abs_load
        mem, _b = abs_load(expect.punch.cards)
        if two:
            mem2, _b = abs_load(expect2.punch.cards)
            for b, bit in mem2.items():
                if b in mem:
                    raise SystemExit("the two subprograms overlap at bit %o" % b)
                mem[b] = bit
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
        if mode.startswith("bss") and w == 0o120001:
            exp, kind = BSS_TV, "vector"     # ARNRM2 transmits the vector over the A8 name
        if two and SUB2_ORIGIN + 1 <= w <= SUB2_ORIGIN + len(SUB2_TV):
            exp, kind = SUB2_TV[w - SUB2_ORIGIN - 1], "vector"
        checks.append(("%s_%o" % (kind, w), str(w), exp))
    if mode.startswith("bss"):
        ba = d.symtab["BAEND" if mode == "bsslib" else "BA%d" % (len(imgs) - 1)]
        sh = 64 - ba % 64 - 24
        want = (d.words[ba // 64] & ~(0xffffff << sh)) | (bss_start << sh)
        checks.append(("branch_address_from_KSILO10", str(ba // 64), want))
    if two:
        # What ARNRM2-ARNRM5 leave for resume load: YRLDTA's type area
        # (p.327 ll.20-21 or 23-25) and the read source in $13 (ll.13-19 or
        # 26), kept by the driver at SAV13 just after the normal return.
        import prosa_dict
        yr = S["YRLDTA"] // 64
        words[yr] = SENTINEL
        if mode == "bss2":
            at = S["ATWSTA"]
            w0, off = divmod(at, 64)
            pair = (image.words.get(w0, 0) << 64) | image.words.get(w0 + 1, 0)
            name48 = (pair >> (128 - off - 48)) & ((1 << 48) - 1)
        else:
            name48 = prosa_dict.a6("LB" + SUB2_LIBNAME)
        checks.append(("YRLDTA_type_area", str(yr), (name48 << 16) | (SENTINEL & 0xFFFF)))
        sys.stderr.write("YRLDTA expected %s\n" % oct(name48))
        sv = d.symtab["SAV13"] // 64
        def xw(nm):
            return image.words[S[nm] // 64]
        if mode == "bss2":
            # AREADS with value -13.0 + SUB2_DISK.0 (sign and magnitude, bit
            # 24 the sign) and count 35 - (SUB2_DISK mod 512) // 15.
            base = xw("AREADS")
            v = -((base >> 46) & 0o777777) if (base >> 39) & 1 else (base >> 46) & 0o777777
            assert (base >> 40) & 0o77 == 0
            v += SUB2_DISK
            cnt = ((base >> 18) & 0o777777) - (SUB2_DISK % 512) // 15
            want13 = (base & ~(0x1FFFFFF << 39) & ~(0o777777 << 18)) \
                | ((abs(v) * 64) << 40) | ((1 if v < 0 else 0) << 39) | (cnt << 18)
        else:
            want13 = xw("AREAD1")          # p.327 l.26, LX,$13,AREAD1
        checks.append(("read_source_13", str(sv), want13))
    if mode not in ("rel", "bss", "bss2", "bsslib"):
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
    if mode == "bsslib":
        dk = d.symtab["DEND"]
        checks.append(("no_error_fetch_end", str(dk // 64), d.words[dk // 64]))
    print(generate(module, image, checks,
                   pc_check=d.symtab["DONE"] // 32,
                   cycle_bound=20000000, step_cap=2000000,
                   fast_load=os.path.join(os.path.abspath(STRETCH), "bsv", "build-loader",
                                          module + ".hex")))


if __name__ == "__main__":
    main()
