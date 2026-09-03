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

if __name__ == "__main__":
    finish(check_rows(assemble(SOURCE), ROWS, SYMBOLS))
