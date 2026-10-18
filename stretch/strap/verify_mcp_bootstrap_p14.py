#!/usr/bin/env python3
"""verify_mcp_bootstrap_p14.py -- MCP's IPL bootstrap, printed page
14 (programs/mcp_bootstrap_p14.strap), PROSA CWS -- the bootstrap's
last page.  docs/MCP_Mar63_001-249.pdf PDF p.21, header "PAGE NUMBER
14".  AGENTS.md rule 3.

THIRTY-NINE CHAINED CONTROL WORDS, every one checked against the
four-group form the listing prints them in:

    vvvvvv.vv+ fff cccccc rrrrrr

Each fetches one PROSA record of 513 words into X BUFER, 512 words
further along than the one before, and chains to the next by
refilling from $+1.0.  The thirty-eight chained ones are CW(CDSC) --
C28-6129 printed p.14's "Count Disregarding Record, Skip and Chain",
flags 110 -- and the last is CW(CR), "Count Within Record", flags
000, which is what stops the channel.

X BS END, LINE 43, IS WHAT PRINTED p.2's IPL CONTROL WORD COUNTS TO.
p.2's CW(CR) counts X BS END - X IPL BS = 0o621 - 0o41 = 0o560 = 368
words, and until now p.2's transcription SYN'd X BS END from this
page.  Here the assembler places it.

THE COUNT AND THE ADDRESS CHECK EACH OTHER.  The statements write
",513," and the listing prints a count of 001001 octal, which is 513;
the last writes ",512," and prints 001000.  The addresses step
0o1000 words at a time -- 011406, 012406, 013406 -- against operands
written 0, 512., 1024., so the decimal-to-octal conversion is
independently confirmed thirty-nine times.
"""
from listing_oracle import check_rows, finish
from strap_asm import assemble

prog = assemble(open("programs/mcp_bootstrap_p14.strap").read())

SYMBOLS = {
    "XPROSA": "000552.00",
    "XBSEND": "000621.00",
}

ROWS = [
    ("000552.00", "011406.00+ 110 001001 000553",
     "line 4  CW(CDSC),0 +X BUFER,513,$+1.0  -FETCH ONE PROSA RECORD"),
    ("000553.00", "012406.00+ 110 001001 000554",
     "line 5  CW(CDSC),512. +X BUFER,513,$+1.0  -FETCH ONE PROSA RECORD"),
    ("000554.00", "013406.00+ 110 001001 000555",
     "line 6  CW(CDSC),1024. +X BUFER,513,$+1.0  -FETCH ONE PROSA RECORD"),
    ("000555.00", "014406.00+ 110 001001 000556",
     "line 7  CW(CDSC),1536. +X BUFER,513,$+1.0  -FETCH ONE PROSA RECORD"),
    ("000556.00", "015406.00+ 110 001001 000557",
     "line 8  CW(CDSC),2048. +X BUFER,513,$+1.0  -FETCH ONE PROSA RECORD"),
    ("000557.00", "016406.00+ 110 001001 000560",
     "line 9  CW(CDSC),2560. +X BUFER,513,$+1.0  -FETCH ONE PROSA RECORD"),
    ("000560.00", "017406.00+ 110 001001 000561",
     "line 10  CW(CDSC),3072. +X BUFER,513,$+1.0  -FETCH ONE PROSA RECORD"),
    ("000561.00", "020406.00+ 110 001001 000562",
     "line 11  CW(CDSC),3584. +X BUFER,513,$+1.0  -FETCH ONE PROSA RECORD"),
    ("000562.00", "021406.00+ 110 001001 000563",
     "line 12  CW(CDSC),4096. +X BUFER,513,$+1.0  -FETCH ONE PROSA RECORD"),
    ("000563.00", "022406.00+ 110 001001 000564",
     "line 13  CW(CDSC),4608. +X BUFER,513,$+1.0  -FETCH ONE PROSA RECORD"),
    ("000564.00", "023406.00+ 110 001001 000565",
     "line 14  CW(CDSC),5120. +X BUFER,513,$+1.0  -FETCH ONE PROSA RECORD"),
    ("000565.00", "024406.00+ 110 001001 000566",
     "line 15  CW(CDSC),5632. +X BUFER,513,$+1.0  -FETCH ONE PROSA RECORD"),
    ("000566.00", "025406.00+ 110 001001 000567",
     "line 16  CW(CDSC),6144. +X BUFER,513,$+1.0  -FETCH ONE PROSA RECORD"),
    ("000567.00", "026406.00+ 110 001001 000570",
     "line 17  CW(CDSC),6656. +X BUFER,513,$+1.0  -FETCH ONE PROSA RECORD"),
    ("000570.00", "027406.00+ 110 001001 000571",
     "line 18  CW(CDSC),7168. +X BUFER,513,$+1.0  -FETCH ONE PROSA RECORD"),
    ("000571.00", "030406.00+ 110 001001 000572",
     "line 19  CW(CDSC),7680. +X BUFER,513,$+1.0  -FETCH ONE PROSA RECORD"),
    ("000572.00", "031406.00+ 110 001001 000573",
     "line 20  CW(CDSC),8192. +X BUFER,513,$+1.0  -FETCH ONE PROSA RECORD"),
    ("000573.00", "032406.00+ 110 001001 000574",
     "line 21  CW(CDSC),8704. +X BUFER,513,$+1.0  -FETCH ONE PROSA RECORD"),
    ("000574.00", "033406.00+ 110 001001 000575",
     "line 22  CW(CDSC),9216. +X BUFER,513,$+1.0  -FETCH ONE PROSA REXORD"),
    ("000575.00", "034406.00+ 110 001001 000576",
     "line 23  CW(CDSC),9728. +X BUFER,513,$+1.0  -FETCH ONE PROSA RECORD"),
    ("000576.00", "035406.00+ 110 001001 000577",
     "line 24  CW(CDSC),10240.+X BUFER,513,$+1.0  -FETCH ONE PROSA RECORD"),
    ("000577.00", "036406.00+ 110 001001 000600",
     "line 25  CW(CDSC),10752.+X BUFER,513,$+1.0  -FETCH ONE PROSA RECORD"),
    ("000600.00", "037406.00+ 110 001001 000601",
     "line 26  CW(CDSC),11264.+X BUFER,513,$+1.0  -FETCH ONE PROSA RECORD"),
    ("000601.00", "040406.00+ 110 001001 000602",
     "line 27  CW(CDSC),11776.+X BUFER,513,$+1.0  -FETCH ONE PROSA RECORD"),
    ("000602.00", "041406.00+ 110 001001 000603",
     "line 28  CW(CDSC),12288.+X BUFER,513,$+1.0  -FETCH ONE PROSA RECORD"),
    ("000603.00", "042406.00+ 110 001001 000604",
     "line 29  CW(CDSC),12800.+X BUFER,513,$+1.0  -FETCH ONE PROSA RECORD"),
    ("000604.00", "043406.00+ 110 001001 000605",
     "line 30  CW(CDSC),13312.+X BUFER,513,$+1.0  -FETCH ONE PROSA RECORD"),
    ("000605.00", "044406.00+ 110 001001 000606",
     "line 31  CW(CDSC),13824.+X BUFER,513,$+1.0  -FETCH ONE PROSA RECORD"),
    ("000606.00", "045406.00+ 110 001001 000607",
     "line 32  CW(CDSC),14336.+X BUFER,513,$+1.0  -FETCH ONE PROSA RECORD"),
    ("000607.00", "046406.00+ 110 001001 000610",
     "line 33  CW(CDSC),14848.+X BUFER,513,$+1.0  -FETCH ONE PROSA RECORD"),
    ("000610.00", "047406.00+ 110 001001 000611",
     "line 34  CW(CDSC),15360.+X BUFER,513,$+1.0  -FETCH ONE PROSA RECORD"),
    ("000611.00", "050406.00+ 110 001001 000612",
     "line 35  CW(CDSC),15872.+X BUFER,513,$+1.0  -FETCH ONE PROSA RECORD"),
    ("000612.00", "051406.00+ 110 001001 000613",
     "line 36  CW(CDSC),16384.+X BUFER,513,$+1.0  -FETCH ONE PROSA RECORD"),
    ("000613.00", "052406.00+ 110 001001 000614",
     "line 37  CW(CDSC),16896.+X BUFER,513,$+1.0  -FETCH ONE PROSA RECORD"),
    ("000614.00", "053406.00+ 110 001001 000615",
     "line 38  CW(CDSC),17408.+X BUFER,513,$+1.0  -FETCH ONE PROSA RECORD"),
    ("000615.00", "054406.00+ 110 001001 000616",
     "line 39  CW(CDSC),17920.+X BUFER,513,$+1.0  -FETCH ONE PROSA RECORD"),
    ("000616.00", "055406.00+ 110 001001 000617",
     "line 40  CW(CDSC),18432.+X BUFER,513,$+1.0  -FETCH ONE PROSA RECORD"),
    ("000617.00", "056406.00+ 110 001001 000620",
     "line 41  CW(CDSC),18944.+X BUFER,513,$+1.0  -FETCH ONE PROSA RECORD"),
    ("000620.00", "057406.00+ 000 001000 000621",
     "line 42  CW(CR),19456.+X BUFER,512,$+1.0  -FETCH ONE PROSA RECORD AND STO"),
]

finish(check_rows(prog, ROWS, SYMBOLS, label="MCP p.14 "))
