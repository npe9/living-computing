#!/usr/bin/env python3
"""MCP's own IOD deck, printed p.1, against strap/iocd.py and the body.

Printed p.1 (MCP_Mar63_001-249.pdf PDF p.8, read at 300 dpi) lists the
cards ahead of the assembly: lines 1-16 are MCP's IOD and REEL cards,
line 17 is "SEM,114,116,118,119,120".  It prints no binary column; the
oracle is the right-hand field, columns 63-72 as STRAP II punched them
on the output cards (C22-6678-1 printed p.9: "STRAP II converts the
IODNAME to an absolute number and punches this four-digit octal number"
in 63-66, and "punches the six-digit octal equivalent of the evaluated
symbol" in 67-72).  tests/mcp_iod_deck_p1.tsv is the transcription.

CHECKS
  rows_transcribed            17 lines
  ref_numbers_count_iods      an IOD card's 63-66 is its ordinal among
                              the IOD cards, in octal; a REEL card
                              carries the IOD's number before it
  exits_are_body_symbols      67-72 is the word address the resident
                              body (printed pp.99-319) assembles the
                              exit symbol to; "0"/"C" exits punch 0
  statement_ends_at_column_62 the longest statement (line 3) is 53
                              characters, columns 10-62, and abuts 63
  iocd_punches_as_printed     strap/iocd.iod_card_text reproduces the
                              statement and columns 63-72 of every IOD
                              card whose type C22-6678-1 lists (the
                              0-3-8 separator iocd writes as "'" is the
                              listing's ",")

OPEN: iocd builds no REEL card, and the NOT USED / RESERVED FOR
UNASSIGN cards are not IOD types C22-6678-1 lists ("PULL THIS CARD
BEFORE UPDATING").  The p.1 order of SEM is unexplained.

MEASURED INJECTIONS (python3 check_iod_deck_p1.py --inject):
    control                          PASS
    iocd punches the ref in decimal  FAIL iocd_punches_as_printed
                                     (refs 8-12 read 0008.., not 0010..)
    iocd punches the exit in decimal FAIL iocd_punches_as_printed
    a row dropped                    FAIL rows_transcribed,
                                     ref_numbers_count_iods
"""
import csv
import os
import sys
import types

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "strap"))
import iocd                 # noqa: E402
import mcp_image            # noqa: E402

TSV = os.path.join(HERE, "mcp_iod_deck_p1.tsv")


def rows():
    with open(TSV) as f:
        return list(csv.DictReader(f, delimiter="\t"))


def body_symtab():
    skip = mcp_image.NO_DECK_PAGES | mcp_image.MISSING_PAGES
    pages = [(mcp_image.DECK("mcp_bootstrap_p%d.strap" % n), "printed p.%d" % n)
             for n in range(99, 320) if n not in skip]
    return mcp_image.build(False, pages, end_at="SDISP")[0].symtab


def main(mod=iocd, rs=None, symtab=None):
    rs = rows() if rs is None else rs
    symtab = body_symtab() if symtab is None else symtab
    fails = 0

    def check(name, bad, n):
        nonlocal fails
        for b in bad:
            print("     " + b)
        fails += bool(bad)
        print(f"{'FAIL' if bad else 'PASS'} {name} = {n - len(bad)} of {n}")

    check("rows_transcribed", [] if len(rs) == 17 else [f"{len(rs)} rows, 17 printed"], 1)

    bad, n, ordinal, last = [], 0, 0, None
    for r in rs:
        st = r["statement"]
        if st.startswith("IOD,"):
            ordinal += 1
            last = "%04o" % ordinal
            want = last
        elif st.startswith("REEL,"):
            want = last
        else:
            continue
        n += 1
        if r["cols63_72"][:4] != want:
            bad.append(f"line {r['line']}: 63-66 {r['cols63_72'][:4]}, ordinal gives {want}")
    check("ref_numbers_count_iods", bad, n)

    bad, n = [], 0
    for r in rs:
        f = r["statement"].split(",")
        if f[0] != "IOD":
            continue
        n += 1
        ex = f[2]
        want = "000000" if ex in ("0", "C") else (
            "%06o" % (symtab[ex] // 64) if ex in symtab else f"no symbol {ex}")
        if r["cols63_72"][4:] != want:
            bad.append(f"line {r['line']}: 67-72 {r['cols63_72'][4:]}, body gives {want}")
    check("exits_are_body_symbols", bad, n)

    longest = max(rs, key=lambda r: len(r["statement"]))
    check("statement_ends_at_column_62",
          [] if len(longest["statement"]) == 62 - 10 + 1 else
          [f"line {longest['line']} is {len(longest['statement'])} characters"], 1)

    bad, n = [], 0
    for r in rs:
        f = r["statement"].split(",")
        if f[0] != "IOD" or f[1] not in mod.IOD_TYPES:
            continue
        n += 1
        text = mod.iod_card_text(r["name"], f[1], f[2], tuple(f[3:]),
                                 ref_number=int(r["cols63_72"][:4], 8),
                                 absolute_exit=symtab[f[2]] // 64)
        got_st = text[9:62].rstrip().replace(mod.IOD_SUBFIELD_SEPARATOR, ",")
        got_cols = text[62:72]
        if got_st != r["statement"] or got_cols != r["cols63_72"]:
            bad.append(f"line {r['line']}: iocd {got_st!r} {got_cols}, "
                       f"printed {r['statement']!r} {r['cols63_72']}")
    check("iocd_punches_as_printed", bad, n)

    print("ALL TESTS PASSED" if not fails else f"{fails} TEST(S) FAILED")
    return fails


def patched(old, new):
    src = open(iocd.__file__).read()
    assert src.count(old) == 1, old
    m = types.ModuleType("iocd_injected")
    m.__file__ = iocd.__file__
    exec(compile(src.replace(old, new), iocd.__file__, "exec"), m.__dict__)
    return m


if __name__ == "__main__":
    if sys.argv[1:] == ["--inject"]:
        st = body_symtab()
        res = [("control", main(symtab=st))]
        print("-- injected: iocd punches the ref in decimal")
        res.append(("refdec", main(patched('ref = "%04o" % ref_number',
                                           'ref = "%04d" % ref_number'), symtab=st)))
        print("-- injected: iocd punches the exit in decimal")
        res.append(("exitdec", main(patched('ex = "%06o" % absolute_exit',
                                            'ex = "%06d" % absolute_exit'), symtab=st)))
        print("-- injected: a row dropped")
        res.append(("drop", main(rs=[r for r in rows() if r["line"] != "6"], symtab=st)))
        print("INJECTIONS: " + ", ".join(f"{n} -> {'FAIL' if r else 'PASS'}" for n, r in res))
    else:
        sys.exit(main())
