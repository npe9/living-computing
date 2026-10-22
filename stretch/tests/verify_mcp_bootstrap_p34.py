#!/usr/bin/env python3
"""verify_mcp_bootstrap_p34.py -- MCP INITIALIZATION, printed page 34:
printing the message block at the console, then the mode bits, the
IF trap instructions at word 32, the dummy communication region and
the disk LOCATE loop (../decks/mcp_bootstrap_p34.strap).
docs/MCP_Mar63_001-249.pdf PDF p.41, header "PAGE NUMBER 34".
AGENTS.md rule 3.

Forty-one printed rows with binary output and ten symbol locations
-- every row on the page.

>>> THE FIRST INPUT-OUTPUT INSTRUCTIONS IN THE INITIALIZATION.
Everything since printed p.17 has been table-walking; lines 12 and
39 talk to a device:

    W(SEOP),0.0($15),X MSG W    -> 000000.00 8F 001724.13 00
    LOC(SEOP),0.0($15),0.0      -> 000000.00 8F 000000.17 00

C28-6129 printed p.4's "OP1(OP2), A19(I), A18(I')" -- a primary
operation with a secondary in parentheses, a channel address and a
control-word address.  Both go through the same "SIC,X7 3 / B,X7 1"
IO TEST pair. <<<

>>> A THIRD "(.25)1", ONE COMMIT AFTER THE MODE WAS BUILT.  Line 19
is "CW,X ZEROS,3,X MSG W2(.25)1" -- the same construct as printed
p.8 line 34 and printed p.30 line 27, chain flag on, flag group
printing 100.  This is the first page transcribed after C28-6129
Section II supplied the specification, and it needed it on its
nineteenth line. <<<

>>> THE LISTING WRITES REGISTER FIELDS BOTH WAYS, ON ONE PAGE.
"LC,$1,X 24 A2+.32" (line 5) and "SV,1,S MAXRN" (line 28);
"LV,$15,S Y CO CH" (line 11) and "LX,14,S XCHAN" (line 32).  The
compiled field is the register number either way, which the page's
own binary settles -- so the "$" is the programmer's hand, exactly
as it was for printed p.32's "TI,$10". <<<

NO ASSEMBLER WORK.  The page's unfamiliar spellings were all already
parsed, including line 35's bare trailing point ("C-I,14,32.") and
line 42's bare leading one ("V+I,15,.32").
"""
from listing_oracle import check_rows, finish
from strap_asm import assemble

prog = assemble(open("../decks/mcp_bootstrap_p34.strap").read())

SYMBOLS = {
    "X377A":  "001714.40",
    "X377B":  "001715.00",
    "X377C":  "001717.40",
    "X377D":  "001721.40",
    "XMSGW":  "001724.00",
    "XMSGW2": "001725.00",
    "X378":   "001726.00",
    "XHERE":  "001740.00",
    "XGOON":  "001744.00",
    "X379":   "001745.00",
}

ROWS = [
    # ---- print the contents of X MSG BK ----
    ("001713.40", "001473.42 50",
     "line 5   LC,$1,X 24 A2+.32  -DROP OUT BIAS  (X24A2 is printed p.27)"),
    ("001714.00", "000021.03 50", "line 6   SC,$1,$1"),
    ("001714.40", "002000.35 01",
     "line 7   X37 7A  LVI,$14,XMSGBK  -GET BASE OF MSG BLOCK"),
    ("001715.00", "000000.00 8E 000000.07 70",
     "line 8   X37 7B  CT0011(BU,64),0.0($14)  -TEST IF MSG TO BE PRINTED"),
    ("001716.00", "001721.74 C2", "line 9   BRZ,X37 7D"),
    ("001716.40", "001725.35 D0", "line 10  SVA,$14,X MSG W2  -NO * FIX CW"),
    ("001717.00", "002156.36 30", "line 11  LV,$15,S Y CO CH  -GET CONSOLE CHANNEL"),
    ("001717.40", "000000.00 8F 001724.13 00",
     "line 12  X 37 7C  W(SEOP),0.0($15),X MSG W  -WRITE ONE MSG"),
    ("001720.40", "000066.40 80", "line 13  SIC,X7 3"),
    ("001721.00", "000057.50 00", "line 14  B,X7 1  -IO TEST"),
    ("001721.40", "000012.35 05",
     "line 15  X37 7 D  V+I,$14,10.0  -ADVANCE TO NEXT MSG"),
    ("001722.00", "000021.34 90", "line 16  KV,$14,$1"),
    ("001722.40", "001715.32 42", "line 17  BXL,X377B  -IF PRINTED LAST MSG"),
    ("001723.00", "001726.10 00", "line 18  B,X37 8"),
    ("001724.00", "001037.00+ 100 000003 001725",
     "line 19  X MSG W  CW,X ZEROS,3,X MSG W2(.25)1"),
    ("001725.00", "000000.00+ 000 000012 000000",
     "line 20  X MSG W2  CW,0.0,10,0  -TYPE ONE MSG"),
    # ---- mode bits, trap instructions, dummy communication region ----
    ("001726.00", "000000.35 01",
     "line 21  X37 8  LVI,$14,0.0  -GET BASE OF MCP COMMUNICATION REGION"),
    ("001726.40", "002151.10 80 002000.36 F0",
     "line 22  CM1111(BU,2),S COM RG+.8  -SET MODE BITS TO IPL CODE"),
    ("001727.40", "000040.22 00", "line 23  Z,32.0  -CLEAR WORD 32.0"),
    ("001730.00", "002161.00 30",
     "line 24  LV,$0,S IF DMP  -GET IF TRAP INSTRUCTION FROM COM RG."),
    ("001730.40", "000040.01 30",
     "line 25  SV,$0,32.0  -INSERT FIRST TRAP INSTRUCTION"),
    ("001731.00", "000040.41 30",
     "line 26  SV,$0,32.32  -INSERT DUPLICATE OF IF TRAP INSTR"),
    ("001731.40", "000000.03 01", "line 27  LVI,$1,0.0"),
    ("001732.00", "002155.43 30", "line 28  SV,1,S MAXRN  -CLEAR S MAXRN"),
    ("001732.40", "002150.74 50",
     "line 29  LC,$14,S COMSZ  -GET SIZE OF MCP COMMUNIZIATION REGION"),
    ("001733.00", "002150.00 80 000000.34 2E",
     "line 30  T,$14,S MCP,0.0($14)  -MOVE DUMMY COMMUNICATION REGION TO MCP"),
    ("001734.00", "000014.25 80 001000.36 F0",
     "line 31  CM1111(BU,1),$MASK+.21  -SET IF MASK BIT ON"),
    # ---- force LOCATE to zero on every disk unit in the CST ----
    ("001735.00", "002152.34 10", "line 32  LX,14,S XCHAN  -GET BASE OF CST"),
    ("001735.40", "000000.44 8E 001000.36 F0",
     "line 33  CM1111(BU,1),.36($14)  -FORCE LOCATE TO ZERO ON DISK"),
    ("001736.40", "000040.35 05", "line 34  V+I,14,32.0"),
    ("001737.00", "000040.35 08", "line 35  C-I,14,32."),
    ("001737.40", "000020.37 01", "line 36  LVI,15,16.0"),
    ("001740.00", "000000.31 8E 001744.34 02",
     "line 37  X HERE  BB,.25($14),X GOON"),
    ("001741.00", "000000.64 8E 001744.34 00", "line 38  BZB,.52($14),X GOON"),
    ("001742.00", "000000.00 8F 000000.17 00", "line 39  LOC(SEOP),0.0($15),0.0"),
    ("001743.00", "000066.40 80", "line 40  SIC,X7 3"),
    ("001743.40", "000057.50 00", "line 41  B,X7 1  -IO TEST"),
    ("001744.00", "000000.77 05", "line 42  X GOON  V+I,15,.32"),
    ("001744.40", "001740.35 48", "line 43  CB+,14,X HERE"),
    ("001745.00", "000040.00 00", "line 44  X37 9  BE,32.0"),
    ("001745.40", "000041.00 80",
     "line 45  ,D RET  (null operation field, C28-6129 printed p.6)"),
]

finish(check_rows(prog, ROWS, SYMBOLS, label="MCP p.34 "))
