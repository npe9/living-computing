#!/usr/bin/env python3
"""check_prosa_dict.py -- the RECONSTRUCTED PROSA dictionary and index
(strap/prosa_dict.py), decoded back out of the record prosa.py puts on
the tape, field by field, against C22-6728 printed p.164 and the code
that reads them.

The decoder below is written from the printed figure, NOT from
prosa_dict.py's packers, so a packing error cannot cancel itself out:

  dictionary word 1   TYPE 0-11, AREA 12-47   (A6 code)
  dictionary word 2   ARC 0-11, WORD 12-20, SIZE 28-45
  index word          TYPE 0-11, ARC 32-43, WORD 44-52, TYPE NO. 56-63

(IBM bit 0 is the most significant bit.)

WHAT EACH CHECK ESTABLISHES
  names_assemble_identically  every dictionary name equals what
        strap_asm assembles from "(AX)DD(BU,48,6),<name>X", the route
        that builds MCP's own request (printed p.269 lines 24 and 48).
  first_four_in_tape_order    entries 0-3 are 11A11DIC, 11B11IND,
        11C11IPL, 11D11MCP (C22-6728 printed p.96), so the bootstrap's
        X BUFER+1/+3/+5/+7 (printed p.4) are their word 2s.
  index_from_second_entry     the second entry's ARC/WORD is an arc
        boundary, where printed p.317 line 41 reads the index from.
  index_is_forty_words        its SIZE is 40 (printed p.317 line 47,
        "CW,CINDEX,40,0"), and the words after the last type are zero
        (printed p.316 X SQ SCH compares all forty; printed p.312 C RODE
        stops on a zero WORD).
  index_points_at_its_type    each index entry's ARC/WORD lands on a
        dictionary entry of that TYPE, the entry before it is another
        type, and TYPE NO. counts that type's entries.
  areas_tile_the_record       every area's ARC/WORD/SIZE are
        contiguous from word 0, without overlap or gap.
  scomd_is_the_overlay        the 22SCOMD area is the printed pp.361-380
        image from Y MPBUF: its first word equals the assembled word at
        234424, and it is 613 words (to VDUB at 235570).
  loader_gap_is_page_329      exactly 34 words of 22LOADER carry the
        gap tag, the words of the missing printed p.329.

INJECTIONS, MEASURED 2026-11-07, each by editing strap/prosa_dict.py
and reverting from a saved copy checked with cmp.  Observed:
  index WORD field one bit too far left (word << 12)
        FAIL index_points_at_its_type = ['22'], and nothing else
  index tail filled with GAP_TAG instead of zeros
        FAIL index_is_forty_words = (40, False), and nothing else
  names coded in the IQS (89) set instead of the A (48) set
        FAIL names_assemble_identically (five of the eight names),
        first_four_in_tape_order, scomd_is_the_overlay ("no 22SCOMD
        entry") and loader_gap_is_page_329 ("no 22LOADER entry")
  the p.329 gap filled with zeros instead of GAP_TAG
        FAIL loader_gap_is_page_329 = 0, and nothing else
  NOT DISCRIMINATING, and recorded so: shifting the index's ARC field
  (arc << 21) passes, because every dictionary entry is on arc 0 and
  a shifted zero is zero.  The P1 boot (run_mcp_p1deck_test.sh) is
  what proves the tables are read correctly end to end.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "strap"))
import charsets                                            # noqa: E402
import prosa                                               # noqa: E402
import prosa_dict                                          # noqa: E402
import strap_asm                                           # noqa: E402


def field(w, a, b):
    """IBM bits a..b inclusive of a 64-bit word."""
    return (w >> (63 - b)) & ((1 << (b - a + 1)) - 1)


def a6_text(v, n):
    rev = {c: ch for ch, c in charsets.A.items()}
    return "".join(rev.get((v >> (6 * (n - 1 - k))) & 0o77, "?") for k in range(n))


def main():
    fails = 0

    def check(name, got, want):
        nonlocal fails
        ok = got == want
        fails += not ok
        print(f"{'PASS' if ok else 'FAIL'} {name} = {got}"
              f"{'' if ok else f' expected {want}'}")

    rec = prosa.record()
    entries = []
    k = 0
    while rec[k] != 0:
        w1, w2 = rec[k], rec[k + 1]
        entries.append(dict(name=a6_text(field(w1, 0, 47), 8),
                            arc=field(w2, 0, 11), word=field(w2, 12, 20),
                            size=field(w2, 28, 45), raw1=w1))
        k += 2
    names = [e["name"] for e in entries]
    print("dictionary:", names)

    bad = []
    for e in entries:
        try:
            p = strap_asm.assemble("        SLC, (8)100.0\nA       (AX)DD(BU,48,6),"
                                   + e["name"] + "X\n        END, A\n")
            ok = p.words[0o100] == e["raw1"]
        except strap_asm.AssemblerError:
            ok = False              # the name decodes to no A-set text
        if not ok:
            bad.append(e["name"])
    check("names_assemble_identically", bad, [])

    check("first_four_in_tape_order", names[:4],
          ["11A11DIC", "11B11IND", "11C11IPL", "11D11MCP"])

    ind = entries[1]
    check("index_from_second_entry", (ind["word"], ind["arc"] * 512 + ind["word"]),
          (0, 512))
    at = ind["arc"] * 512
    index = rec[at:at + 40]
    n_types = len({n[:2] for n in names})
    check("index_is_forty_words", (ind["size"], index[n_types:] == [0] * (40 - n_types)),
          (40, True))

    probs = []
    for w in index[:n_types]:
        t = a6_text(field(w, 0, 11), 2)
        pos = (field(w, 32, 43) * 512 + field(w, 44, 52)) // 2
        cnt = field(w, 56, 63)
        if pos >= len(names) or names[pos][:2] != t \
                or (pos and names[pos - 1][:2] == t) \
                or cnt != sum(n[:2] == t for n in names):
            probs.append(t)
    check("index_points_at_its_type", probs, [])

    at, gaps = 0, []
    for e in sorted(entries, key=lambda e: e["arc"] * 512 + e["word"]):
        start = e["arc"] * 512 + e["word"]
        if start != at:
            gaps.append((e["name"], start, at))
        at = start + e["size"]
    check("areas_tile_the_record", gaps, [])

    sc = next((e for e in entries if e["name"] == "22SCOMD "), None)
    if sc is None:
        check("scomd_is_the_overlay", "no 22SCOMD entry", (613, True, True))
    else:
        start = sc["arc"] * 512 + sc["word"]
        img, _ = prosa_dict.overlay_image(361, 380, prosa_dict.YMPBUF)
        check("scomd_is_the_overlay",
              (sc["size"], rec[start] == img[0] != 0,
               rec[start:start + sc["size"]] == img),
              (613, True, True))

    lo = next((e for e in entries if e["name"] == "22LOADER"), None)
    if lo is None:
        check("loader_gap_is_page_329", "no 22LOADER entry", 34)
    else:
        start = lo["arc"] * 512 + lo["word"]
        tagged = sum((w >> 48) == 0x6A6A for w in rec[start:start + lo["size"]])
        check("loader_gap_is_page_329", tagged, 34)

    print("\n%s" % ("ALL TESTS PASSED" if not fails else f"{fails} TEST(S) FAILED"))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
