#!/usr/bin/env python3
"""verify_dcp_compool.py -- the STRETCH MAINTENANCE COMPOOL
(../decks/dcp_compool.strap) against the addresses the listing itself
prints, ka_ua1_diagnostic_ctl_pgm.pdf PDF pp.129-130.

WHY THIS IS NOT A rule-3 CHECK, AND WHAT IT IS INSTEAD.  AGENTS.md
rule 3 compares assembled machine code against the listing's printed
machine code.  A SYN emits no code, so there is nothing to compare.
What this page does print, on every row, is the RESOLVED ADDRESS -- so
the oracle here is the assembler's symbol table against that column.
Weaker than rule 3, and stated as such, but not nothing: it tests the
offsets, the decimal-offset/octal-address convention, and the reading
of the operator glyph.

TWELVE OF THE 65 ROWS ARE CIRCULAR AND ARE REPORTED SEPARATELY.  The
base symbols (ECTL1-4, EQAV1-7, EDCP1, ACA) are defined elsewhere in
the DCP, not on these pages; their values in the .strap are
back-computed from the printed addresses of the rows that use them.
So any row with no offset of its own is true by construction.  The
rows WITH an offset are the real check.
"""
import sys
from strap_asm import assemble, AssemblerError

PROGRAM = "../decks/dcp_compool.strap"

# (symbol, printed address as the listing shows it, has_own_offset)
PRINTED = [
    ("EBAUTO", "4006.00", False), ("EBMAIN", "4006.01", True),
    ("EBSURV", "4006.02", True),  ("EBDCP",  "4006.03", True),
    ("EBMCON", "4006.04", True),  ("EBBLNK", "4006.56", True),
    ("EMACH",  "4007.00", False), ("ETAPCM", "4007.14", True),
    ("ETAPDM", "4007.23", True),  ("ETAPCS", "4007.34", True),
    ("ETAPDS", "4007.43", True),  ("ETAPCO", "4007.54", True),
    ("ETAPDO", "4007.63", True),  ("EB16CH", "4007.75", True),
    ("MNTCTL", "4007.76", True),
    ("EBDRSP", "4010.21", True),  ("EDPLOC", "4010.40", True),
    ("EBAEC",  "4011.01", True),  ("EBHARV", "4011.02", True),
    ("EBK1",   "4011.03", True),  ("EBK2",   "4011.04", True),
    ("EBK3",   "4011.05", True),
]
for grp, word in [("EQRDR", "4012"), ("EQPUN", "4013"), ("EQTYP", "4014"),
                  ("EQPTR", "4015"), ("EQDIS", "4016"), ("EQTAP", "4017")]:
    for k, (bits, off) in enumerate([("00", False), ("20", True),
                                     ("40", True), ("60", True)]):
        PRINTED.append((f"{grp}{k+1}", f"{word}.{bits}", off))
PRINTED += [("EQTAP5", "4020.00", False), ("EQTAP6", "4020.20", True),
            ("ETAP7",  "4020.40", True),  ("EQTAP8", "4020.60", True),
            ("EQMEM",  "4025.00", True)]
# p.130: ACA is the base; the rest are word offsets from it.  THE
# ADDRESS COLUMN HERE WAS READ, NOT INFERRED -- an earlier draft of
# this file computed these from ACA and the offsets and wrote them as
# though the listing printed them, which is asserting an unread value.
# Rendered at 600 dpi the column is "0.00& 1.00& ... 7.00& 10.00&
# 11.00& 12.00& 13.00& 14.00& 15.00&": OCTAL, running 7 -> 10 with no
# 8 or 9, which independently confirms the decimal-offset/octal-address
# convention on a second page.  The listing prints them unpadded; the
# zero-padding below is this file's formatting, not the listing's.
PRINTED += [("ACA", "0000.00", False)]
for k, sym in enumerate(["ACB", "ACC", "ACD", "ACE", "ACF", "ACG", "ACH",
                         "ADA", "ADB", "ADC", "ADD", "AIDNTA", "AIDNTB"], start=1):
    PRINTED.append((sym, f"{oct(k)[2:].zfill(4)}.00", True))


def main():
    with open(PROGRAM) as f:
        src = f.read()
    try:
        prog = assemble(src)
    except AssemblerError as e:
        print(f"error: {e}", file=sys.stderr)
        sys.exit(1)

    failed = real = circular = 0
    for sym, printed, has_off in PRINTED:
        if sym not in prog.symtab:
            print(f"FAIL {sym:8} not defined by the transcription")
            failed += 1
            continue
        bits = prog.symtab[sym]
        word, bit = divmod(bits, 64)
        got = f"{oct(word)[2:].zfill(4)}.{oct(bit)[2:].zfill(2)}"
        kind = "check " if has_off else "CIRCULAR"
        if got != printed:
            print(f"FAIL {sym:8} assembled {got}, listing {printed}")
            failed += 1
        else:
            print(f"PASS {sym:8} {got}  ({kind}: listing prints {printed})")
            if has_off:
                real += 1
            else:
                circular += 1

    print()
    print(f"{len(PRINTED)} symbols: {real} genuine address checks, "
          f"{circular} circular by construction (base-derived), {failed} failed")
    if failed:
        print(f"{failed} TEST(S) FAILED")
        sys.exit(1)
    print("ALL TESTS PASSED")


if __name__ == "__main__":
    main()
