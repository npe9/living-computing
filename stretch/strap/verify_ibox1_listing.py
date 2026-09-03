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

# pp.50-51: the SIC-B,ZIND and SIC-B,IND groups (ISBI at 005432.40
# through the second VF after ISBIK at 005453.40), from the span
# transcription programs/ibox1_p50_p51_span.strap. SIC with Branch on
# Indicator embedded; the indicator numbers (XF=38, XCZ=48, XVZ=50,
# XVGZ=51, XVLZ=49) are visible in bits 19-24 of each branch. The
# BZXVLZ row's printed code reads as either "5443.20 C0" or
# "5443.30 C0" on the scan; .30 is the only reading consistent with
# XVLZ (49 = 110001) and is what is checked.
SOURCE_SPAN = open(__file__.replace("verify_ibox1_listing.py",
                                     "programs/ibox1_p50_p51_span.strap")).read()

ROWS_SICB = [
    ("005432.40", "5442.02 10",  "ISBI   LX,$X1,ISBXW"),
    ("005433.00", "0.30 00",     "       NOP"),
    ("005433.40", "5452.00 80",  "ISBI1  SIC,ISBIA"),
    ("005434.00", "5435.23 40",  "       BZXF,ISBI2"),
    ("005434.40", "5434.44 00",  "ISBIB  BD,$"),
    ("005435.00", "5434.40 80",  "ISBI2  SIC,ISBIB"),
    ("005435.40", "5436.70 40",  "       BZXCZ,ISBI3"),
    ("005436.00", "5436.04 00",  "ISBIC  BD,$"),
    ("005436.40", "5436.00 80",  "ISBI3  SIC,ISBIC"),
    ("005437.00", "5440.31 C0",  "       BZXVGZ,ISBI4"),
    ("005437.40", "5437.44 00",  "ISBID  BD,$"),
    ("005440.00", "5437.40 80",  "ISBI4  SIC,ISBID"),
    ("005440.40", "5443.30 C0",  "       BZXVLZ,ISBI5 (scan: .20 or .30)"),
    ("005441.00", "5441.04 00",  "ISBIH  BD,$"),
    ("005442.00", "0.00 00 000040.00 00", "ISBXW  XW,0,2,0"),
    ("005443.00", "5444.00 80",  "ISBI5  SIC,ISBIE"),
    ("005443.40", "5444.23 42",  "       BXF,$+.32"),
    ("005444.00", "5444.44 00",  "ISBIE  BD,$+.32"),
    ("005444.40", "5445.40 80",  "ISBI6  SIC,ISBIF"),
    ("005445.00", "5445.70 42",  "       BXCZ,$+.32"),
    ("005445.40", "5446.04 00",  "ISBIF  BD,$+.32"),
    ("005446.00", "5447.00 80",  "ISBI7  SIC,ISBIG"),
    ("005446.40", "5447.31 C2",  "       BXVGZ,$+.32"),
    ("005447.00", "5447.44 00",  "ISBIG  BD,$+.32"),
    ("005447.40", "5441.00 80",  "ISBI8  SIC,ISBIH"),
    ("005450.00", "5451.31 42",  "       BXVZ,$+1.0"),
    ("005450.40", "5450.44 00",  "ISBII  BD,$"),
    ("005451.00", "5452.42 30",  "       LV,$X1,ISBIJ"),
    ("005451.40", "5450.43 30",  "       SV,$X1,ISBII"),
    ("005452.00", "5452.04 00",  "ISBIA  BD,$"),
    ("005452.40", "5453.04+",    "ISBIJ  VF,ISBIK+.04"),
    ("005453.00", "777777.70+",  "ISBIK  VF,(8)777777.70"),
    ("005453.40", "777777.70+",  "       VF,(8)777777.70"),
]

SYMBOLS_SICB = {"ISBI": "005432.40", "ISBI1": "005433.40", "ISBIB": "005434.40",
                "ISBI2": "005435.00", "ISBIC": "005436.00", "ISBI3": "005436.40",
                "ISBID": "005437.40", "ISBI4": "005440.00", "ISBIH": "005441.00",
                "ISBXW": "005442.00", "ISBI5": "005443.00", "ISBIE": "005444.00",
                "ISBI6": "005444.40", "ISBIF": "005445.40", "ISBI7": "005446.00",
                "ISBIG": "005447.00", "ISBI8": "005447.40", "ISBII": "005450.40",
                "ISBIA": "005452.00", "ISBIJ": "005452.40", "ISBIK": "005453.00",
                "WEN2": "005454.00", "WEN": "005456.00", "VEN": "005460.00",
                "IBY": "005462.00"}

if __name__ == "__main__":
    fails = check_rows(assemble(SOURCE), ROWS, SYMBOLS, label="p51 ")
    fails += check_rows(assemble(SOURCE_SIC), ROWS_SIC, SYMBOLS_SIC, label="p50 ")
    prog_span = assemble(SOURCE_SPAN)
    fails += check_rows(prog_span, ROWS_SICB, SYMBOLS_SICB, label="span ")
    fails += check_rows(prog_span, ROWS, {}, label="span-WEN ")
    finish(fails)
