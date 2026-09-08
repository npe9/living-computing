#!/usr/bin/env python3
"""verify_fp_arith_f214d_listing.py -- F214 "MULTIPLY TEST ROUTINE",
sub-block F214D "INDICATOR TESTS" (programs/fp_arith_f214d.strap)
against jb_af1c pp.139-141.  This completes F214.

D1 has no leading "B,$+.32" where D2-D6 do, so it spans thirteen and a
half words from 017762.40 and the rest are fourteen each -- putting
their bases at 020000, 020016, 020034, 020052 and 020070 and the exit
at 020106.00, all of which fall out of the transcription.

D6 inverts the order: five BZBs for the exponent indicators and then
"BB,11.33 -TEST ZM IND ON" last, where D1-D5 test their own indicator
first.

TRANSCRIPTION NOTE: the page prints some BZB branch-target fields as
".24" where others in the same block print ".34" -- D2's BZB,11.28
reads "020006.34 00" while D3's, D4's and D6's read "...24 00".  Every
one is the same "$+2." branch, so the field cannot legitimately
differ; read as OCR damage and taken as .34 throughout, which both the
assembler and the majority of the printed rows give.
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("programs/fp_arith_f214d.strap").read())

CONST_ROWS = [
    ("022041.00", "0200177777777777777760", "FPK28"),
    ("022057.00", "0001460000000000000000", "FPK42"),
    ("022115.00", "0001500000000000000000", "FPK74"),
    ("022145.00", "0003700000000000000000", "FK3"),
    ("022170.00", "0400177777777777777760", "FK22"),
    ("022205.00", "1777400000000000000000", "FK35"),
    ("022211.00", "0777625252525252525240", "FK39"),
    ("022235.00", "1000024713560247135620", "FK59"),
    ("022240.00", "0777424713560247135620", "FK62"),
    ("022241.00", "0777500000000000000000", "FK63"),
    ("022244.00", "0001476743126765431260", "FK66"),
    ("022274.00", "0000000000000000000002", "FK91"),
]

SIC   = "1310.00 80"
BSERS = "1304.10 00"
Z     = "13.22 00"
A = {"FPK28":"22041","FPK42":"22057","FPK74":"22115","FK3":"22145","FK22":"22170",
     "FK35":"22205","FK39":"22211","FK59":"22235","FK62":"22240","FK63":"22241",
     "FK66":"22244","FK91":"22274"}
ALL = [28, 29, 30, 31, 32, 33]

# (name, base half-word address as (word, off), accumulator, mode, operand, ON bit)
SUB = [("D1", (0o17762, 32), "FK59",  ".41 A0", "FK35",  28),
       ("D2", (0o20000,  0), "FK62",  ".41 A0", "FK63",  29),
       ("D3", (0o20016,  0), "FK22",  ".41 A0", "FPK74", 30),
       ("D4", (0o20034,  0), "FPK28", ".41 A0", "FPK42", 31),
       ("D5", (0o20052,  0), "FK39",  ".41 A0", "FK3",   32),
       ("D6", (0o20070,  0), "FK66",  ".01 A0", "FK91",  33)]

def hw(w, off):
    return f"{w:06o}.{'40' if off else '00'}"

CODE_ROWS = []
for name, (w0, off0), acc, mode, mem, on in SUB:
    if off0 == 0:                      # D2-D6 open with a fall-through branch
        CODE_ROWS.append((hw(w0, 0), f"{w0:05o}.50 00", f"{name} B, $+.32"))
        base = (w0, 32)
    else:
        base = (w0, off0)
    w, o = base
    CODE_ROWS += [
        (hw(w, o),      A[acc] + ".40 60", f"{name} L(U), {acc}"),
        (hw(w + 1, 0),  Z,                 f"{name} Z, $IND"),
        (hw(w + 1, 32), A[mem] + mode,     f"{name} *{'(N)' if mode.startswith('.01') else '(U)'}, {mem}"),
    ]
    b = w + 2                          # first full-word branch test
    if name != "D6":
        CODE_ROWS += [
            (hw(b, 0), f"13.{on:o} 80 {b+2:06o}.34 02", f"{name} BB, 11.{on}, $+2.0"),
            (hw(b+1, 0), SIC, f"{name} SIC"), (hw(b+1, 32), BSERS, f"{name} B, SERS"),
        ]
        b += 2
        for off in ALL:
            if off == on: continue
            CODE_ROWS += [
                (hw(b, 0), f"13.{off:o} 80 {b+2:06o}.34 00", f"{name} BZB, 11.{off}, $+2.0"),
                (hw(b+1, 0), SIC, f"{name} SIC"), (hw(b+1, 32), BSERS, f"{name} B, SERS"),
            ]
            b += 2
    else:                              # D6 puts its ON test last
        for off in ALL:
            if off == on: continue
            CODE_ROWS += [
                (hw(b, 0), f"13.{off:o} 80 {b+2:06o}.34 00", f"{name} BZB, 11.{off}, $+2.0"),
                (hw(b+1, 0), SIC, f"{name} SIC"), (hw(b+1, 32), BSERS, f"{name} B, SERS"),
            ]
            b += 2
        CODE_ROWS += [
            (hw(b, 0), f"13.{on:o} 80 {b+2:06o}.34 02", f"{name} BB, 11.{on}, $+2.0  test ZM ind ON"),
            (hw(b+1, 0), SIC, f"{name} SIC"), (hw(b+1, 32), BSERS, f"{name} B, SERS"),
        ]

if __name__ == "__main__":
    fails = check_rows(prog, CONST_ROWS, label="constants")
    fails += check_rows(prog, CODE_ROWS, label="code")
    finish(fails)
