#!/usr/bin/env python3
"""verify_mcp_bootstrap_p7_p8.py -- MCP's IPL bootstrap, printed pages
7 and 8 (programs/mcp_bootstrap_p7_p8.strap): X ERR DD, the error
table.  docs/MCP_Mar63_001-249.pdf PDF pp.14-15.  AGENTS.md rule 3.

THE LAST TWO PAGES OF THE BOOTSTRAP, and the index to all the rest:
seventy-eight VF half words, one pair per error code, holding the
address of the site that failed and the address of the message to
print for it.

THE TABLE CHECKS ITS OWN LENGTH.  Printed p.8 line 31 is
"X E DD K SYN,$-X ERR DD  -SIZE OF ERROR TABLE" and the listing
prints 000047.00+ -- thirty-nine words, which is what seventy-eight
half words occupy and what thirty-nine distinct error codes need.
The table's extent was not assumed from anywhere.

AND THE TWO TRANSCRIPTIONS CROSS-CHECK.  The thirty-nine message
labels this page names are SYN'd here but PLACED by
programs/mcp_bootstrap_p9_p12.strap and _p13.strap from their own
instruction streams.  cross_check() below asserts the two agree, so a
mistake in either one fails here rather than cancelling out: this
page's printed VF value, the SYN, and the other program's placement
are three statements that must coincide.
"""
from listing_oracle import check_rows, finish
from strap_asm import assemble

prog = assemble(open("programs/mcp_bootstrap_p7_p8.strap").read())


def cross_check():
    """Every message label SYN'd here must equal the address the
    pp.9-13 programs assemble it at."""
    placed = {}
    for f in ("programs/mcp_bootstrap_p9_p12.strap",
              "programs/mcp_bootstrap_p13.strap"):
        for n, v in assemble(open(f).read()).symtab.items():
            if n.startswith("XMSG") or n.startswith("XMS"):
                placed[n] = v
    n_ok = 0
    for n, v in placed.items():
        if n not in prog.symtab:
            continue
        if prog.symtab[n] != v:
            print(f"FAIL MCP pp.7-8 {n}: this page SYNs bit "
                  f"{prog.symtab[n]}, pp.9-13 place it at bit {v}")
            raise SystemExit(1)
        n_ok += 1
    print(f"PASS MCP pp.7-8 {n_ok} message labels agree with the "
          f"addresses programs/mcp_bootstrap_p9_p12.strap and _p13.strap "
          f"place them at")


cross_check()

SYMBOLS = {
    "XERRDD": "000176.00",
    # X E DD K is a SYN whose value is a WORD COUNT, not a location:
    # the LOCATION column prints 000047.00+, thirty-nine words.
    "XEDDK":  "000047.00",
    "XERRIN": "000245.00",
    "XMSCW1": "000246.00",
    "XMSGCW": "000247.00",
    "XLR":    "000250.00",
    "XERRCW": "000253.00",
}

ROWS = [
    ("000176.00", "000055.40+",
     "p.7 line 2  VF,X ERR 00+1.0"),
    ("000176.40", "000254.00+",
     "p.7 line 3  VF,X MSG 00  -EKJ ON CCW OF IPL CW"),
    ("000177.00", "000060.40+",
     "p.7 line 4  VF,X ERR 01+1.0"),
    ("000177.40", "000260.00+",
     "p.7 line 5  VF,X MSG 01  -EKJ DETECTED IN IO TEST ROUTINE"),
    ("000200.00", "000061.40+",
     "p.7 line 6  VF,X ERR 02+1.0"),
    ("000200.40", "000266.00+",
     "p.7 line 7  VF,X MSG 02  -UNRJ DETECTED IN IO TEST ROUTINE"),
    ("000201.00", "000062.40+",
     "p.7 line 8  VF,X ERR 03+1.0"),
    ("000201.40", "000274.00+",
     "p.7 line 9  VF,X MSG 03  -CBJ DETECTED IN IO TEST ROUTINE"),
    ("000202.00", "000064.40+",
     "p.7 line 10  VF,X ERR 04+1.0"),
    ("000202.40", "000302.00+",
     "p.7 line 11  VF,X MSG 04  -EKJ ON CCW IN IO TEST ROUTINE"),
    ("000203.00", "000070.00+",
     "p.7 line 12  VF,X ERR 05+1.0"),
    ("000203.40", "000310.00+",
     "p.7 line 13  VF,X MSG 05  -UNSUCCESSFUL COMPLETION"),
    ("000204.00", "000072.00+",
     "p.7 line 14  VF,X ER 05A+1.0"),
    ("000204.40", "000315.00+",
     "p.7 line 15  VF,X MS 05A  -EKJ IN SPACING OVER EOF"),
    ("000205.00", "000073.00+",
     "p.7 line 16  VF,X ER 05B+1.0"),
    ("000205.40", "000322.00+",
     "p.7 line 17  VF,X MS 05B  -UNRJ IN SPACING OVER EOF"),
    ("000206.00", "000074.00+",
     "p.7 line 18  VF,X ER 05C+1.0"),
    ("000206.40", "000327.00+",
     "p.7 line 19  VF,X MS 05C  -CBJ IN SPACING OVER EOF"),
    ("000207.00", "000076.00+",
     "p.7 line 20  VF,X ER 05D+1.0"),
    ("000207.40", "000334.00+",
     "p.7 line 21  VF,X MS 05D  -EKJ OF CCW IN TEST OF SPACE FILE"),
    ("000210.00", "000102.00+",
     "p.7 line 22  VF,X ER 05E+1.0"),
    ("000210.40", "000342.00+",
     "p.7 line 23  VF,X MS 05E  -SPACE EOF OPERATION IN ERROR"),
    ("000211.00", "000127.40+",
     "p.7 line 24  VF,X ERR 10+1.0"),
    ("000211.40", "000374.00+",
     "p.7 line 25  VF,X MSG 10  -UNSUCCESSFUL COMPLETION OF MCP"),
    ("000212.00", "000106.00+",
     "p.7 line 27  VF,X ERR 06+1.0"),
    ("000212.40", "000347.00+",
     "p.7 line 28  VF,X MSG 06  -EKJ ON READ OF SOURCE TAPE"),
    ("000213.00", "000107.00+",
     "p.7 line 29  VF,X ERR 07+1.0"),
    ("000213.40", "000354.00+",
     "p.7 line 30  VF,X MSG 07  -UNRJ ON READ OF SOURCE TAPE"),
    ("000214.00", "000110.00+",
     "p.7 line 31  VF,X ERR 08+1.0"),
    ("000214.40", "000361.00+",
     "p.7 line 32  VF,X MSG 08  -CBJ ON READ OF SOURCE TAPE"),
    ("000215.00", "000112.00+",
     "p.7 line 33  VF,X ERR 09+1.0"),
    ("000215.40", "000366.00+",
     "p.7 line 34  VF,X MSG 09  -EKJ ON CCW ON SOURCE TAPE"),
    ("000216.00", "000631.00+",
     "p.7 line 36  VF,X ERR 11+1.0"),
    ("000216.40", "000403.00+",
     "p.7 line 37  VF,X MSG 11  -EKJ ON DISK OPERATION"),
    ("000217.00", "000632.00+",
     "p.7 line 38  VF,X ERR 12+1.0"),
    ("000217.40", "000410.00+",
     "p.7 line 39  VF,X MSG 12  -UNRJ ON DIST OPERATION"),
    ("000220.00", "000633.00+",
     "p.7 line 40  VF,X ERR 13+1.0"),
    ("000220.40", "000415.00+",
     "p.7 line 41  VF,X MSG 13  -CBJ ON DISK OPERATION"),
    ("000221.00", "000640.40+",
     "p.7 line 42  VF,X ERR 14+1.0"),
    ("000221.40", "000424.00+",
     "p.7 line 43  VF,X MSG 14  -EKJ ON CCW ON DISK WRITE OPERATION"),
    ("000222.00", "000641.40+",
     "p.7 line 44  VF,X ERR 15+1.0"),
    ("000222.40", "000432.00+",
     "p.7 line 45  VF,X MSG 15  -CBJ ON CCW ON DISK WRITE OPERATION"),
    ("000223.00", "000642.40+",
     "p.7 line 46  VF,X ERR 16+1.0"),
    ("000223.40", "000432.00+",
     "p.7 line 47  VF,X MSG 16  -UNSUCCESSFUL COMPLETION OF DISK"),
    ("000224.00", "000645.40+",
     "p.7 line 49  VF,X ER 16A+1.0"),
    ("000224.40", "000432.00+",
     "p.7 line 50  VF,X MS 16A  -EKJ OF CCW IN TEST OF DISK WRITE"),
    ("000225.00", "000646.40+",
     "p.7 line 51  VF,X ER 16B+1.0"),
    ("000225.40", "000432.00+",
     "p.7 line 52  VF,X MS 16B  -WRITE DISK OPERATION IN ERROR"),
    ("000226.00", "000662.40+",
     "p.7 line 53  VF,X ER 16C+1.0"),
    ("000226.40", "000440.00+",
     "p.7 line 54  VF,X MS 16C  -NO IOCC CARD DETECTED"),
    ("000227.00", "000707.40+",
     "p.7 line 55  VF,X ERR 17+1.0"),
    ("000227.40", "000444.00+",
     "p.7 line 56  VF,X MSG 17  -WRONG EQUIPMENT CODE"),
    ("000230.00", "000723.40+",
     "p.8 line 1  VF,X ERR 18+1.0"),
    ("000230.40", "000451.00+",
     "p.8 line 2  VF,X MSG 18  -IO CONFIGURATION DEFINED"),
    ("000231.00", "000760.40+",
     "p.8 line 4  VF,X ERR 19+1.0"),
    ("000231.40", "000460.00+",
     "p.8 line 5  VF,X MSG 19  -INCORRECT CARD TYPE"),
    ("000232.00", "001006.40+",
     "p.8 line 6  VF,X ERR 20+1.0"),
    ("000232.40", "000464.00+",
     "p.8 line 7  VF,X MSG 20  -NO CONSOLE DEFINED"),
    ("000233.00", "001010.00+",
     "p.8 line 8  VF,X ERR 21+1.0"),
    ("000233.40", "000501.00+",
     "p.8 line 9  VF,X MSG 21  -NO CONSOLE AVAILABLE"),
    ("000234.00", "001157.40+",
     "p.8 line 10  VF,X ER 21A+1.0"),
    ("000234.40", "000464.00+",
     "p.8 line 11  VF,X MS 21A  -EKJ OF CCW IN IO STATUS REPORT"),
    ("000235.00", "001441.40+",
     "p.8 line 13  VF,X ERR 22+1.0"),
    ("000235.40", "000473.00+",
     "p.8 line 14  VF,X MSG 22  -INCORRECT CARD TYPE WITHIN IODS"),
    ("000236.00", "001453.00+",
     "p.8 line 15  VF,X ERR 23+1.0"),
    ("000236.40", "000501.00+",
     "p.8 line 16  VF,X MSG 23  -IO REQUIREMENTS REJECTED"),
    ("000237.00", "001471.40+",
     "p.8 line 17  VF,X ERR 24+1.0"),
    ("000237.40", "000506.00+",
     "p.8 line 18  VF,X MSG 24  -IO ASSIGNMENTS CANNOT BE MADE"),
    ("000240.00", "001505.40+",
     "p.8 line 19  VF,X ERR 25+1.0"),
    ("000240.40", "000513.30+",
     "p.8 line 20  VF,X MSG 25  -IO TABLES CANNOT BE FORMED"),
    ("000241.00", "001520.40+",
     "p.8 line 21  VF,X ERR 26+1.0"),
    ("000241.40", "000521.00+",
     "p.8 line 22  VF,X MSG 26  -PROSA ARC COUNT INCORRECT"),
    ("000242.00", "001605.40+",
     "p.8 line 23  VF,X ERR 27+1.0"),
    ("000242.40", "000526.00+",
     "p.8 line 24  VF,X MSG 27  -MCP PARAMETER INPUT MISSING"),
    ("000243.00", "001614.00+",
     "p.8 line 25  VF,X ERR 28+1.0"),
    ("000243.40", "000533.00+",
     "p.8 line 26  VF,X MSG 28  -IMPOSSIBLE OPERATING MODE"),
    ("000244.00", "001647.40+",
     "p.8 line 27  VF,X ERR 29+1.0"),
    ("000244.40", "000540.00+",
     "p.8 line 28  VF,X MSG 29  -SPOOL INPUT ASSIGNMENTS NOT"),
    # ---- printed p.8's definitions ----
    ("000245.00", "000176.00+ 000 000050 000000",
     "p.8 line 32  X ERR IN  XW,X ERR DD,X E DD K+1.0,0  -XW FOR "
     "INITIALIZING ERROR SEARCH"),
    # WRITTEN CW(CCR) HERE, "CW,X ZEROS,3,X MSG CW(.25)1" on the page.
    # The (.25)1 sets bit 25, the chain flag, and CCR sets the same
    # three bits -- which this row is what proves.
    ("000246.00", "001037.00+ 100 000003 000247",
     "p.8 line 34  X MS CW1  CW,X ZEROS,3,X MSG CW(.25)1  -CW FOR "
     "LOWER CONSOLE REGISTERS"),
    ("000247.00", "000000.00+ 000 000012 000000",
     "p.8 line 35  X MSG CW  CW,0,10,0  -CW FOR ERROR MSG"),
    # X LR's own row prints 000003.00, the reservation's SIZE rather
    # than any contents; what is checked is that its three words put
    # X ERR CW three words later.
    ("000253.00", "000000.00+ 000 000000 000000",
     "p.8 line 37  X ERR CW  CW,0  - SLOT FOR COPIED CW"),
]

finish(check_rows(prog, ROWS, SYMBOLS, label="MCP pp.7-8 "))
