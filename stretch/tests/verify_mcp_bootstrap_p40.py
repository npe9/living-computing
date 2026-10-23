#!/usr/bin/env python3
"""verify_mcp_bootstrap_p40.py -- printed page 40: the LIM card's
limit check, the IOD card's field conversion, the REEL card, and the
UNCODE subroutine's two exits (../decks/mcp_bootstrap_p40.strap).
docs/MCP_Mar63_001-249.pdf PDF p.47, header "PAGE NUMBER 40".
AGENTS.md rule 3.

Forty-one printed rows with binary output -- every row on the page --
and eighteen symbol locations.

>>> MCP EXECUTES A SWAP, AND THIS PAGE IS THE PROOF. <<<

Lines 24 and 28 are

    002276.40   000033.00 80   002324.06 E0   SWAPI,3,$11,Y UX SAV
    002302.00   000033.00 80   002324.06 E0   SWAPI,3,$11,Y UX SAV

and bsv/README.md has said since 2026-09-22 that SWAP "is a different
datapath and NOTHING IN THE CORPUS EXECUTES ONE".
decks/transmit_multiword.strap says it too.  BOTH ARE NOW FALSE, and
the instruction is three words from the UNCODE subroutine's normal
exit.

THE ENCODING AGREES WITH THE POCKET CARD AND THE PAGE CONTAINS ITS
OWN CONTROL.  The trailing byte is E0 where a TRANSMIT's is A0 --
sub-op 110 against 010, the one bit X22-6533's TRANSMIT box uses to
tell them apart -- and the right half word's ".06" is J = 0011, an
immediate count of three.  LINE 33 IS "TI,3,Y UX SAV,$11", the same
three words going the other way with A0.  Two rows on one page,
differing in exactly the bit that names the operation.

WHAT IT IS FOR, which is the part that makes it believable: lines
23-29 are the REEL card's handler.  It swaps three index registers
out to Y UX SAV, does its work, and swaps the same three back.  A
two-way interchange is exactly what "save these and restore the old
ones" wants, and it is why a SWAP and not a TRANSMIT is written here.

>>> FIVE MORE PREDICTIONS LAND. <<<

  Y IODC   002266.40   p.38 line 34's "B,Y IODC"      -- line 14
  Y REELC  002276.00   p.38 line 40's "BAEZ,Y REELC"  -- line 23
  Y JCCER  002303.40   p.38 line 35's "BXE,Y JCCER"   -- line 30
  Y UER    002311.00   p.38 lines 8, 36, 38 and 41    -- line 38
  Y UCLLC  002262.00   p.39 line 56's "BXL,Y UCLLC"   -- line 5

THREE OF THE FIVE WERE BIT-18 READINGS -- Y IODC from ".50",
Y JCCER from ".72", Y UCLLC from ".32" -- so the half-word selector
has now been checked on five separate symbols by three separate
pages, each transcribed before the page that defines it.

AND IT USES FOUR EARLIER DEFINITIONS: S ROOF (p.37 line 37) on lines
1 and 3, S MCP (p.37 line 7) on lines 5 and 9, Y USB8C (p.38 line
21) on lines 23 and 30, Y UCBF2 (p.38's prediction) on line 36.

A TRANSMIT'S COUNT REGISTER IS WRITTEN WITHOUT ITS "$", which is
printed p.4 line 28's convention.  Reference Manual printed p.30:
the direct count comes from "the field J, bits 51-54", so the
listing's "$15" there is a four-bit register number and not an
address -- as an address it would be word 0o37 and the assembler
says so.  Line 33's "TI,3,Y UX SAV,$11" KEEPS its "$11", because
there the index register is the transmit's SOURCE ADDRESS and the
count is the immediate 3.  Same page, both readings, and the binary
distinguishes them.
"""
from listing_oracle import check_rows, finish
from strap_asm import assemble

prog = assemble(open("../decks/mcp_bootstrap_p40.strap").read())

SYMBOLS = {
    # The eight this page DEFINES -- five of them predicted earlier.
    "YUCLLC": "002262.00",
    "YUCLLH": "002264.40",
    "YIODC":  "002266.40",
    "YIODTL": "002270.00",
    "YIOCB":  "002272.40",
    "YREELC": "002276.00",
    "YJCCER": "002303.40",
    "YUER":   "002311.00",
    # The ten it uses.
    "SROOF":  "002162.00",
    "SMCP":   "002150.00",
    # S MAXUB shares its half word with p.37's S BAMCP.  Two names
    # for one address is not new -- p.36 line 34 SYNs S LR BU to
    # S BA PP -- and this one is read off line 10's own binary.
    "SMAXUB": "002153.00",
    "YNORR":  "002313.40",
    "YIDX12": "002321.00",
    # A BIT address, not a word one: line 20's VFL left half is a
    # clean twenty-four bits, word 0o2334 and bit 0o64 = 52.
    "YUTOE":  "002334.64",
    "YUSB8C": "002200.00",
    "YUXSAV": "002324.00",
    "YBLWD4": "002364.00",
    "YUCBF2": "002337.00",
}

ROWS = [
    ("002260.00", "002162.31 90", "line 1   KC,$12,S ROOF"),
    ("002260.40", "002311.33 42", "line 2   BXH,Y UER"),
    ("002261.00", "002162.26 30", "line 3   LV,$11,S ROOF"),
    ("002261.40", "002264.50 00", "line 4   B,Y UCLLH"),
    ("002262.00", "002150.31 90", "line 5   Y UCLLC  KC,$12,S MCP"),
    ("002262.40", "002311.33 42", "line 6   BXH,Y UER"),
    ("002263.00", "000041.31 04", "line 7   KVI,$12,33.0"),
    ("002263.40", "002311.32 42", "line 8   BXL,Y UER"),
    ("002264.00", "002150.26 30", "line 9   LV,$11,S MCP"),
    ("002264.40", "002153.27 30", "line 10  Y UCLLH  SV,$11,S MAXUB"),
    ("002265.00", "000034.31 90", "line 11  KC,$12,$12  -IS LOWER GREATER"),
    ("002265.40", "002311.33 40", "line 12  BZXH,Y UER  -THAN UPPER LIMIT"),
    ("002266.00", "002313.50 00", "line 13  B,Y NORR  -LIMITS OK"),
    ("002266.40", "002321.30 10",
     "line 14  Y IODC  LX,$12,Y IDX12  -CONVERT I-O REFERENCE"),
    # (2)001010 IS THE SAME BCD ZERO printed p.39 line 45 loads and
    # printed p.24 line 13 writes.  Three pages, one nibble.
    ("002267.00", "120000.00 80  406000.20 50",
     "line 15  LI(BU,6),(2)001010  -NUMBER AND ABSOLUTE EXIT"),
    ("002270.00", "000000.06 8C  106000.15 70",
     "line 16  Y IODTL  CT0110(V+I)(BU,6),.6($12)"),
    ("002271.00", "002272.74 C4", "line 17  BZRZZ,Y IOCB"),
    ("002271.40", "777777.72 8C  006000.00 F0", "line 18  CM0000(BU,6),-.6($12)"),
    ("002272.40", "002270.30 4C", "line 19  Y IOCB  CBR,$12,Y IODTL"),
    ("002273.00", "002334.64 80  074600.06 70", "line 20  LF(BU,60,6),Y UTOE"),
    # TWO SFs IN A ROW, one with a three-operand form.  Both carry
    # the CM0101 connective function this project derived from
    # printed p.39 line 52.
    ("002274.00", "000034.64 80  014330.12 F0",
     "line 21  SF(BU,12,3),$12+.52,48  -PUT IN $12"),
    ("002275.00", "000034.00 80  022300.12 F0", "line 22  SF(BU,18,3),$12"),
    ("002276.00", "002200.30 50",
     "line 23  Y REELC  LC,$12,Y USB8C  -LOAD COUNT WITH = OF FIELDS"),
    # >>> THE SWAP. <<<  Trailing E0, where line 33's TRANSMIT of the
    # same three words is A0.
    ("002276.40", "000033.00 80  002324.06 E0", "line 24  SWAPI,3,$11,Y UX SAV"),
    ("002277.40", "000002.37 BE", "line 25  LVE,$15,2.0($14)"),
    ("002300.00", "002364.00 80  000000.02 AF", "line 26  TI,1,Y BLWD4,0.0($15)"),
    ("002301.00", "000000.00 8F  000001.16 AF", "line 27  TI,7,0.0($15),1.0($15)"),
    ("002302.00", "000033.00 80  002324.06 E0", "line 28  SWAPI,3,$11,Y UX SAV"),
    ("002303.00", "002313.50 00", "line 29  B,Y NORR  -IN BREAKDOWN, AND RETURN"),
    ("002303.40", "002200.36 50", "line 30  Y JCCER  LC,$15,Y USB8C"),
    ("002304.00", "000001.32 9E", "line 31  KV,$13,1.0($14)"),
    ("002304.40", "002311.32 C0", "line 32  BZXE,Y UER"),
    # THE MATCHED PAIR: the same three words as line 24, with A0.
    ("002305.00", "002324.00 80  000033.06 A0", "line 33  TI,3,Y UX SAV,$11"),
    ("002306.00", "000002.37 BE", "line 34  LVE,$15,2.0($14)"),
    ("002306.40", "000000.00 8F  000000.00 F0", "line 35  CM0000(BU),0($15)"),
    # A DIRECT-COUNT TRANSMIT whose count register is written without
    # its "$", printed p.4 line 28's convention.
    ("002307.40", "002337.00 80  000000.36 2F", "line 36  T,$15,Y UCBF2,0.0($15)"),
    ("002310.40", "000002.50 0E", "line 37  B,2.32($14)"),
    ("002311.00", "002324.00 80  000033.06 A0", "line 38  Y UER  TI,3,Y UX SAV,$11"),
    ("002312.00", "000002.37 BE", "line 39  LVE,$15,2.0($14)"),
    ("002312.40", "000000.22 0F", "line 40  Z,0.0($15)"),
    ("002313.00", "000002.50 0E", "line 41  B,2.32($14)"),
]

fails = check_rows(prog, ROWS, SYMBOLS, label="MCP p.40 ")
finish(fails)
