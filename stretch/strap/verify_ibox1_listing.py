#!/usr/bin/env python3
"""verify_ibox1_listing.py -- assemble I-Box 1's WEN2/WEN/VEN routines
VERBATIM (docs/ja_ax1a_ibox-1.pdf p.51, plus their WEN6/WEN7 constants
from p.59) at the listing's own octal addresses, via SLC, and compare
every assembled half-word bit-for-bit against the machine code the
1961 listing prints beside each source line -- IBM's own STRAP output
as the oracle (see listing_oracle.py for the print format and the
reasoning). This was the first such check in the project and the first
real use of SLC; every symbol here is defined inside the transcribed
range, so every row is a genuine address-placement check.

Run standalone: `./verify_ibox1_listing.py`. Wired into run_tests.sh.
"""

from strap_asm import assemble
from listing_oracle import check_rows, finish

SOURCE = """
        SLC, (8)5454.0
WEN2    L(BU,64,8), WEN7       ! -LOAD ONES
        BRGZZ, $+1.0
        BD, $
        SLC, (8)5456.0
WEN     L(BU,64,8), WEN6       ! -LOAD ZEROS
        BRZZ, $+1.0
        BD, $
        SLC, (8)5460.0
VEN     L(BU,64,8), WEN7
        BRGZZ, $+1.0
        BD, $
        SLC, (8)6102.0
WEN6    DD(BU,64,8), 0
WEN7    DD(BU,64,8), 18446744073709551615
        END, WEN2
"""

ROWS = [
    ("005454.00", "6103.00 80 000000.20 50", "WEN2  L%BU,64,8=,WEN7"),
    ("005455.00", "5456.35 46",              "      BRGZZ,$+1.0"),
    ("005455.40", "5455.44 00",              "      BD,$"),
    ("005456.00", "6102.00 80 000000.20 50", "WEN   L%BU,64,8=,WEN6"),
    ("005457.00", "5460.34 C6",              "      BRZZ,$+1.0"),
    ("005457.40", "5457.44 00",              "      BD,$"),
    ("005460.00", "6103.00 80 000000.20 50", "VEN   L%BU,64,8=,WEN7"),
    ("005461.00", "5462.35 46",              "      BRGZZ,$+1.0"),
    ("005461.40", "5461.44 00",              "      BD,$"),
]

SYMBOLS = {"WEN2": "005454.00", "WEN": "005456.00", "VEN": "005460.00",
           "WEN6": "006102.00", "WEN7": "006103.00"}

# p.50: the SIC-CB / SIC-CBZ test groups, ISCB (005412.00) through the
# NOP-valued VF after ISCBK (005432.00) -- the same text as
# programs/ibox1_sic_cb_cbz.strap minus its substituted terminal BEW.
# Checks SIC's own half-word (address, 1000, I), the embedded CB/CBZ
# half-words that complete each SIC word, LCI's count-in-bits-0-17
# packing (the row that caught the immediate-index bug, see
# strap/README.md "Gotchas" 16), LV/SV, and VF,ISCBK+.04.
SOURCE_SIC = open(__file__.replace("verify_ibox1_listing.py",
                                    "programs/ibox1_sic_cb_cbz.strap")).read()

ROWS_SIC = [
    ("005412.00", "4.03 02",     "ISCB   LCI,$X1,4"),
    ("005412.40", "0.30 00",     "       NOP,0.0"),
    ("005413.00", "5430.40 80",  "ISCB1  SIC,ISCBA"),
    ("005413.40", "5414.42 48",  "       CB,$X1,ISCB2"),
    ("005414.00", "5414.04 00",  "ISCBB  BD,$"),
    ("005414.40", "5414.00 80",  "ISCB2  SIC,ISCBB"),
    ("005415.00", "5416.02 48",  "       CB,$X1,ISCB3"),
    ("005415.40", "5415.44 00",  "ISCBC  BD,$"),
    ("005416.00", "5415.40 80",  "ISCB3  SIC,ISCBC"),
    ("005416.40", "5417.42 48",  "       CB,$X1,ISCB4"),
    ("005417.00", "5417.04 00",  "ISCBD  BD,$"),
    ("005417.40", "5417.00 80",  "ISCB4  SIC,ISCBD"),
    ("005420.00", "5421.02 4A",  "       CBZ,$X1,ISCB5"),
    ("005420.40", "5420.44 00",  "ISCBH  BD,$"),
    ("005421.00", "4.03 02",     "ISCB5  LCI,$X1,4"),
    ("005421.40", "5422.40 80",  "ISCB6  SIC,ISCBE"),
    ("005422.00", "5422.42 4A",  "       CBZ,$X1,$+.32"),
    ("005422.40", "5423.04 00",  "ISCBE  BD,$+.32"),
    ("005423.00", "5424.00 80",  "ISCB7  SIC,ISCBF"),
    ("005423.40", "5424.02 4A",  "       CBZ,$X1,$+.32"),
    ("005424.00", "5424.44 00",  "ISCBF  BD,$+.32"),
    ("005424.40", "5425.40 80",  "ISCB8  SIC,ISCBG"),
    ("005425.00", "5425.42 4A",  "       CBZ,$X1,$+.32"),
    ("005425.40", "5426.04 00",  "ISCBG  BD,$+.32"),
    ("005426.00", "5420.40 80",  "ISCB9  SIC,ISCBH"),
    ("005426.40", "5427.42 4A",  "       CBZ,$X1,$+1.0"),
    ("005427.00", "5427.04 00",  "ISCBI  BD,$"),
    ("005427.40", "5431.02 30",  "       LV,$X1,ISCBJ"),
    ("005430.00", "5427.03 30",  "       SV,$X1,ISCBI"),
    ("005430.40", "5430.44 00",  "ISCBA  BD,$"),
    ("005431.00", "5431.44+",    "ISCBJ  VF,ISCBK+.04"),
    ("005431.40", "777777.70+",  "ISCBK  VF,(8)777777.70"),
    ("005432.00", "777777.70+",  "       VF,(8)777777.70"),
]

SYMBOLS_SIC = {"ISCB": "005412.00", "ISCB1": "005413.00", "ISCBB": "005414.00",
               "ISCB2": "005414.40", "ISCBC": "005415.40", "ISCB3": "005416.00",
               "ISCBD": "005417.00", "ISCB4": "005417.40", "ISCBH": "005420.40",
               "ISCB5": "005421.00", "ISCB6": "005421.40", "ISCBE": "005422.40",
               "ISCB7": "005423.00", "ISCBF": "005424.00", "ISCB8": "005424.40",
               "ISCBG": "005425.40", "ISCB9": "005426.00", "ISCBI": "005427.00",
               "ISCBA": "005430.40", "ISCBJ": "005431.00", "ISCBK": "005431.40"}

if __name__ == "__main__":
    fails = check_rows(assemble(SOURCE), ROWS, SYMBOLS, label="p51 ")
    fails += check_rows(assemble(SOURCE_SIC), ROWS_SIC, SYMBOLS_SIC, label="p50 ")
    finish(fails)
