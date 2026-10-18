#!/usr/bin/env python3
"""verify_ibox4_listing.py -- assemble I-Box 4 routine 150's CB, CB+,
CBR and CBR+ test blocks VERBATIM (docs/jb_ax4b_ibox-4.pdf p.155,
LORE1..IBR18, and p.159, LORE3..IBR107) at the listing's own octal
addresses and compare every assembled half-word against the machine
code printed beside each line -- see listing_oracle.py.

Why this matters more than the I-Box 1 check: it is the first external
validation of encodings that until now rested on the pocket card and
the model's own self-consistency --
  - CB / CB+ / CBR / CBR+ (opcodes.py's CB_CODES was sourced from the
    pocket card's legend and never checked against real assembler
    output);
  - LX / SX direct index arithmetic;
  - XW's packed index-word layout. StretchTypes.bsv places count at
    bits 28-45 and refill at 46-63; the listing's own print of
    "XW,IBR9+(8).04,4,-1" -> "11445.04 00 000117.77 FF" has count=4's
    low bit landing at bit 43 and the all-ones refill filling 46-63,
    and "XW,IBRA9+(8).04,3,IBRA10" -> "... 000060.23 88" carries
    IBRA10's own word address 011610 verbatim in bits 46-63. That is
    what ibox4_cb_count_branch.strap's header, written before this
    check existed, said was still unproven about the model's packing.
  - The listing's own syntax forms the assembler had to grow for this:
    "(8)" radix literals in address fields, and a bare "NOP,".

What is and isn't checked: symbols defined INSIDE the transcribed
range (IBR1..IBR18, IBRA1/2, IBR9, IBR96..IBR107, IBRA9..12, HANGS1/2)
are placed by SLC and their rows are genuine address-placement checks.
Symbols defined elsewhere in the 200-page listing (LORE*, CBER*,
IBR28/38/108/113/114/120/121) are given by SYN from the SAME printed
column this test compares against, so rows naming them verify only
the opcode/modifier/half-word bits, not the address -- marked "ext"
below. The two-instruction gaps the listing leaves before each
full-word XW (011441.40, 011621.40) are not printed and not checked.

Run standalone: `./verify_ibox4_listing.py`. Wired into run_tests.sh.
"""

from strap_asm import assemble
from listing_oracle import check_rows, finish

# p.155, from LORE1 (011430.00) through IBR18's second NOP (011456.40).
# The listing prints parentheses as % and =; restored here.
SOURCE_P155 = """
LORE    SYN, (8)11772.0        ! ext: printed operand of LORE1's LX
IBR28   SYN, (8)11471.0        ! ext
IBR38   SYN, (8)11504.0        ! ext
CBERA   SYN, (8)12016.0        ! ext: the CBERA*/CBERB* error routines
CBERA1  SYN, (8)12017.40       ! ext
CBERA2  SYN, (8)12021.0        ! ext
CBERA3  SYN, (8)12022.40       ! ext
CBERA4  SYN, (8)12024.0        ! ext
CBERA5  SYN, (8)12025.40       ! ext
CBERA6  SYN, (8)12027.0        ! ext
CBERA7  SYN, (8)12030.40       ! ext
CBERB   SYN, (8)12032.0        ! ext
CBERB1  SYN, (8)12033.40       ! ext
CBERB2  SYN, (8)12035.0        ! ext
CBERB3  SYN, (8)12036.40       ! ext
CBERB4  SYN, (8)12040.0        ! ext
CBERB5  SYN, (8)12041.40       ! ext
CBERB6  SYN, (8)12043.0        ! ext
        SLC, (8)11430.0
LORE1   LX,$X1,LORE
        SX,$X1,IBR8
        SX,$X1,IBR18
        SX,$X1,IBR28
        SX,$X1,IBR38
IBR     LX,$X1,IBRA1           ! -SET UP XW
IBR1    CB,$X1,IBR2            ! -COUNT TO 3 + BRANCH
        BD,CBERA               ! -ERROR OCCURED
IBR2    CB,$X1,IBR3            ! -COUNT TO 2 + BRANCH
        BD,CBERA1
        BD,CBERA2
IBR3    CB,$X1,IBR4            ! -COUNT TO 1 + BRANCH
        BD,CBERA3
        BD,CBERA4
        BD,CBERA5
IBR4    CB,$X1,IBR7            ! -COUNT TO ZERO NO BRANCH
IBR5    SX,$X1,IBR8            ! -STORE FOR VALUE TEST
IBR6    B,IBR8
IBR7    BD,CBERA6              ! -ERROR OCCURED
IBRA1   XW,IBR9+(8).04,4,-1
IBR8    NOP,0.
        NOP,0.                 ! -BECOMES(BD,IBR9),14-0+18-1S
        NOP,
        BD,CBERA7              ! -ERROR OCCURED
IBR9    VF,(8)777777.70        ! -21 ONES OR NOP,-1
        VF,(8)777777.70        ! -21 ONES OR NOP,-1
IBR10   LX,$X1,IBRA2           ! -SET UP XW
IBR11   CB+,$X1,IBR12          ! -COUNT TO 3 + BRANCH
        BD,CBERB
IBR12   CB+,$X1,IBR13          ! -COUNT TO 2 + BRANCH
        BD,CBERB1
        BD,CBERB2
IBR13   CB+,$X1,IBR14          ! -COUNT TO 1 + BRANCH
        BD,CBERB3
        BD,CBERB4
        BD,CBERB5
IBR14   CB+,$X1,IBR17          ! -COUNT TO ZERO NO BRANCH
IBR15   SX,$X1,IBR18           ! -STORE FOR VALUE TEST
IBR16   B,IBR18
IBR17   BD,CBERB6              ! -ERROR OCCURED
IBRA2   XW,IBR16+(8).04,4,-1
IBR18   NOP,0.
        NOP,0.                 ! -BECOMES BD,IBR19 +14-0+18-1S
        END, LORE1
"""

ROWS_P155 = [
    ("011430.00", "11772.02 10", "LORE1 LX,$X1,LORE (ext)"),
    ("011430.40", "11443.03 10", "      SX,$X1,IBR8"),
    ("011431.00", "11456.03 10", "      SX,$X1,IBR18"),
    ("011431.40", "11471.03 10", "      SX,$X1,IBR28 (ext)"),
    ("011432.00", "11504.03 10", "      SX,$X1,IBR38 (ext)"),
    ("011432.40", "11442.02 10", "IBR   LX,$X1,IBRA1"),
    ("011433.00", "11434.02 48", "IBR1  CB,$X1,IBR2"),
    ("011433.40", "12016.04 00", "      BD,CBERA (ext)"),
    ("011434.00", "11435.42 48", "IBR2  CB,$X1,IBR3"),
    ("011434.40", "12017.44 00", "      BD,CBERA1 (ext)"),
    ("011435.00", "12021.04 00", "      BD,CBERA2 (ext)"),
    ("011435.40", "11437.42 48", "IBR3  CB,$X1,IBR4"),
    ("011436.00", "12022.44 00", "      BD,CBERA3 (ext)"),
    ("011436.40", "12024.04 00", "      BD,CBERA4 (ext)"),
    ("011437.00", "12025.44 00", "      BD,CBERA5 (ext)"),
    ("011437.40", "11441.02 48", "IBR4  CB,$X1,IBR7"),
    ("011440.00", "11443.03 10", "IBR5  SX,$X1,IBR8"),
    ("011440.40", "11443.10 00", "IBR6  B,IBR8"),
    ("011441.00", "12027.04 00", "IBR7  BD,CBERA6 (ext)"),
    ("011442.00", "11445.04 00 000117.77 FF", "IBRA1 XW,IBR9+(8).04,4,-1"),
    ("011443.00", "0.30 00",     "IBR8  NOP,0."),
    ("011443.40", "0.30 00",     "      NOP,0."),
    ("011444.00", "0.30 00",     "      NOP,"),
    ("011444.40", "12030.44 00", "      BD,CBERA7 (ext)"),
    ("011445.00", "777777.70+",  "IBR9  VF,(8)777777.70"),
    ("011445.40", "777777.70+",  "      VF,(8)777777.70"),
    ("011446.00", "11455.02 10", "IBR10 LX,$X1,IBRA2"),
    ("011446.40", "11447.43 48", "IBR11 CB+,$X1,IBR12"),
    ("011447.00", "12032.04 00", "      BD,CBERB (ext)"),
    ("011447.40", "11451.03 48", "IBR12 CB+,$X1,IBR13"),
    ("011450.00", "12033.44 00", "      BD,CBERB1 (ext)"),
    ("011450.40", "12035.04 00", "      BD,CBERB2 (ext)"),
    ("011451.00", "11453.03 48", "IBR13 CB+,$X1,IBR14"),
    ("011451.40", "12036.44 00", "      BD,CBERB3 (ext)"),
    ("011452.00", "12040.04 00", "      BD,CBERB4 (ext)"),
    ("011452.40", "12041.44 00", "      BD,CBERB5 (ext)"),
    ("011453.00", "11454.43 48", "IBR14 CB+,$X1,IBR17"),
    ("011453.40", "11456.03 10", "IBR15 SX,$X1,IBR18"),
    ("011454.00", "11456.10 00", "IBR16 B,IBR18"),
    ("011454.40", "12043.04 00", "IBR17 BD,CBERB6 (ext)"),
    ("011455.00", "11454.04 00 000117.77 FF", "IBRA2 XW,IBR16+(8).04,4,-1"),
    ("011456.00", "0.30 00",     "IBR18 NOP,0."),
    ("011456.40", "0.30 00",     "      NOP,0."),
]

SYMBOLS_P155 = {
    "LORE1": "011430.00", "IBR": "011432.40", "IBR1": "011433.00",
    "IBR2": "011434.00", "IBR3": "011435.40", "IBR4": "011437.40",
    "IBR5": "011440.00", "IBR6": "011440.40", "IBR7": "011441.00",
    "IBRA1": "011442.00", "IBR8": "011443.00", "IBR9": "011445.00",
    "IBR10": "011446.00", "IBR11": "011446.40", "IBR12": "011447.40",
    "IBR13": "011451.00", "IBR14": "011453.00", "IBR15": "011453.40",
    "IBR16": "011454.00", "IBR17": "011454.40", "IBRA2": "011455.00",
    "IBR18": "011456.00",
}

# p.159, from LORE3 (011573.00) through the BD after IBR107 (011627.40).
SOURCE_P159 = """
LOREE   SYN, (8)11777.0        ! ext (all SYNs here: printed operands)
LOREF   SYN, (8)12000.0
LOREG   SYN, (8)12001.0
LOREH   SYN, (8)12002.0
LOREI   SYN, (8)12003.0
LOREJ   SYN, (8)12004.0
LOREK   SYN, (8)12005.0
IBR108  SYN, (8)11630.0
IBR113  SYN, (8)11640.0
IBR114  SYN, (8)11642.0
IBR120  SYN, (8)11654.0
IBR121  SYN, (8)11656.0
CBERJ   SYN, (8)12142.0
CBERJ1  SYN, (8)12143.40
CBERJ2  SYN, (8)12145.0
CBERJ3  SYN, (8)12146.0
CBERJ4  SYN, (8)12150.0
CBERK   SYN, (8)12151.40
CBERK1  SYN, (8)12153.0
CBERK2  SYN, (8)12154.40
CBERK3  SYN, (8)12156.0
CBERK4  SYN, (8)12157.40
CBERK5  SYN, (8)12161.0
CBERK6  SYN, (8)12162.40
        SLC, (8)11573.0
LORE3   LX,$X1,LOREE
        SX,$X1,IBR100
        LX,$X1,LOREF
        SX,$X1,IBR106
        LX,$X1,LOREG
        SX,$X1,IBR107
        LX,$X1,LOREH
        SX,$X1,IBR113
        LX,$X1,LOREI
        SX,$X1,IBR114
        LX,$X1,LOREJ
        SX,$X1,IBR120
        LX,$X1,LOREK
        SX,$X1,IBR121
IBR96   LX,$X1,IBRA9           ! -SET UP XW
IBR97   CBR,$X1,IBR98          ! -COUNT 3 TO 2,BR,NO REFILL
        BD,CBERJ               ! -ERROR OCCURED
IBR98   CBR,$X1,IBR99          ! -COUNT 2 TO 1,BR,NO REFILL
        BD,CBERJ1
        BD,CBERJ2
IBR99   CBR,$X1,HANGS1         ! -COUNT 1 TO 0,NO BR, REFILL
        SX,$X1,IBR100          ! -STORE NEW XW
        B,IBR100               ! -BRANCH TO NEW INST.
        NOP,0.0
IBRA9   XW,IBRA9+(8).04,3,IBRA10        ! -ORIGIANL XW
IBRA10  XW,IBR101+(8).04,(8)37777,-1    ! -REFILL XW
IBR100  NOP,
        BD,CBERJ3              ! -ERROR OCCURED
HANGS1  NOP,
        BD,CBERJ4              ! -ERROR OCCURED
IBR101  VF,(8)777777.70        ! -NOP,-.32
        VF,(8)777777.70        ! -NOP,-.32
IBR102  LX,$X1,IBRA11          ! -SET UP XW
IBR103  CBR+,$X1,IBR104        ! -COUNT 3 TO 2,1 TO VAL,+ BRANCH
        BD,CBERK
IBR104  CBR+,$X1,IBR105        ! -COUNT 2 TO 1,1 TO VAL,+BRANCH
        BD,CBERK1
        BD,CBERK2
IBR105  SX,$X1,IBR106          ! -SX TO TEST VALUE
        CBR+,$X1,HANGS2        ! -COUNT TO 0,NO V,NO B,REFILL
        SX,$X1,IBR107          ! -SX + TEST FOR REFILL
        B,IBR106               ! -BRANCH TO VALUE TEST
        NOP,0.0
IBRA11  XW,IBR106+(8).04,3,IBRA12       ! -ORIGINAL XW
IBRA12  XW,IBR108+(8).04,(8)37777,-1
IBR106  NOP,
        BD,CBERK3              ! -ERROR OCCURED
HANGS2  NOP,
        BD,CBERK4              ! -ERROR OCCURED
IBR107  NOP,
        BD,CBERK5              ! -ERROR OCCURED
        NOP,
        BD,CBERK6              ! -ERROR OCCURED
        END, LORE3
"""

ROWS_P159 = [
    ("011573.00", "11777.02 10", "LORE3 LX,$X1,LOREE (ext)"),
    ("011573.40", "11611.03 10", "      SX,$X1,IBR100"),
    ("011574.00", "12000.02 10", "      LX,$X1,LOREF (ext)"),
    ("011574.40", "11624.03 10", "      SX,$X1,IBR106"),
    ("011575.00", "12001.02 10", "      LX,$X1,LOREG (ext)"),
    ("011575.40", "11626.03 10", "      SX,$X1,IBR107"),
    ("011576.00", "12002.02 10", "      LX,$X1,LOREH (ext)"),
    ("011576.40", "11640.03 10", "      SX,$X1,IBR113 (ext)"),
    ("011577.00", "12003.02 10", "      LX,$X1,LOREI (ext)"),
    ("011577.40", "11642.03 10", "      SX,$X1,IBR114 (ext)"),
    ("011600.00", "12004.02 10", "      LX,$X1,LOREJ (ext)"),
    ("011600.40", "11654.03 10", "      SX,$X1,IBR120 (ext)"),
    ("011601.00", "12005.02 10", "      LX,$X1,LOREK (ext)"),
    ("011601.40", "11656.03 10", "      SX,$X1,IBR121 (ext)"),
    ("011602.00", "11607.02 10", "IBR96 LX,$X1,IBRA9"),
    ("011602.40", "11603.42 4C", "IBR97 CBR,$X1,IBR98"),
    ("011603.00", "12142.04 00", "      BD,CBERJ (ext)"),
    ("011603.40", "11605.02 4C", "IBR98 CBR,$X1,IBR99"),
    ("011604.00", "12143.44 00", "      BD,CBERJ1 (ext)"),
    ("011604.40", "12145.04 00", "      BD,CBERJ2 (ext)"),
    ("011605.00", "11612.02 4C", "IBR99 CBR,$X1,HANGS1"),
    ("011605.40", "11611.03 10", "      SX,$X1,IBR100"),
    ("011606.00", "11611.10 00", "      B,IBR100"),
    ("011606.40", "0.30 00",     "      NOP,0.0"),
    ("011607.00", "11607.04 00 000060.23 88", "IBRA9  XW,IBRA9+(8).04,3,IBRA10"),
    ("011610.00", "11613.04 00 777777.77 FF", "IBRA10 XW,IBR101+(8).04,(8)37777,-1"),
    ("011611.00", "0.30 00",     "IBR100 NOP,"),
    ("011611.40", "12146.04 00", "       BD,CBERJ3 (ext)"),
    ("011612.00", "0.30 00",     "HANGS1 NOP,"),
    ("011612.40", "12150.04 00", "       BD,CBERJ4 (ext)"),
    ("011613.00", "777777.70+",  "IBR101 VF,(8)777777.70"),
    ("011613.40", "777777.70+",  "       VF,(8)777777.70"),
    ("011614.00", "11622.02 10", "IBR102 LX,$X1,IBRA11"),
    ("011614.40", "11615.43 4C", "IBR103 CBR+,$X1,IBR104"),
    ("011615.00", "12151.44 00", "       BD,CBERK (ext)"),
    ("011615.40", "11617.03 4C", "IBR104 CBR+,$X1,IBR105"),
    ("011616.00", "12153.04 00", "       BD,CBERK1 (ext)"),
    ("011616.40", "12154.44 00", "       BD,CBERK2 (ext)"),
    ("011617.00", "11624.03 10", "IBR105 SX,$X1,IBR106"),
    ("011617.40", "11625.03 4C", "       CBR+,$X1,HANGS2"),
    ("011620.00", "11626.03 10", "       SX,$X1,IBR107"),
    ("011620.40", "11624.10 00", "       B,IBR106"),
    ("011621.00", "0.30 00",     "       NOP,0.0"),
    ("011622.00", "11624.04 00 000060.23 93", "IBRA11 XW,IBR106+(8).04,3,IBRA12"),
    ("011623.00", "11630.04 00 777777.77 FF", "IBRA12 XW,IBR108+(8).04,(8)37777,-1"),
    ("011624.00", "0.30 00",     "IBR106 NOP,"),
    ("011624.40", "12156.04 00", "       BD,CBERK3 (ext)"),
    ("011625.00", "0.30 00",     "HANGS2 NOP,"),
    ("011625.40", "12157.44 00", "       BD,CBERK4 (ext)"),
    ("011626.00", "0.30 00",     "IBR107 NOP,"),
    ("011626.40", "12161.04 00", "       BD,CBERK5 (ext)"),
    ("011627.00", "0.30 00",     "       NOP,"),
    ("011627.40", "12162.44 00", "       BD,CBERK6 (ext)"),
]

SYMBOLS_P159 = {
    "LORE3": "011573.00", "IBR96": "011602.00", "IBR97": "011602.40",
    "IBR98": "011603.40", "IBR99": "011605.00", "IBRA9": "011607.00",
    "IBRA10": "011610.00", "IBR100": "011611.00", "HANGS1": "011612.00",
    "IBR101": "011613.00", "IBR102": "011614.00", "IBR103": "011614.40",
    "IBR104": "011615.40", "IBR105": "011617.00", "IBRA11": "011622.00",
    "IBRA12": "011623.00", "IBR106": "011624.00", "HANGS2": "011625.00",
    "IBR107": "011626.00",
}

if __name__ == "__main__":
    fails = check_rows(assemble(SOURCE_P155), ROWS_P155, SYMBOLS_P155, label="p155 ")
    fails += check_rows(assemble(SOURCE_P159), ROWS_P159, SYMBOLS_P159, label="p159 ")
    finish(fails)
