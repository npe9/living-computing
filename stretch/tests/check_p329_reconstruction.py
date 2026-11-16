#!/usr/bin/env python3
"""check_p329_reconstruction.py -- the RECONSTRUCTED printed p.329 fits the
hole the scan leaves, and every reference the landed pages make into it.

decks/mcp_p329_reconstruction.strap is NOT IBM's code (its header says what
is cited and what chosen).  What can be checked without the page is that it
sits exactly where the landed pages say p.329 was, and that the landed pages'
own binaries still assemble to what they printed with it in place:

  span_written            the 34 words 235112-235153 are all written, and
  span_only               the reconstruction writes no word outside them;
  label_<NAME>            each label a landed page branches to lands where
                          that page's printed binary puts it (AOIGN3 p.328
                          l.49, AOIGN1 l.46, AOCTH1 l.29, APCRD2 l.13;
                          AOCTL6 p.327 l.48; APCARD p.320 l.33; APCRD4 p.330
                          ll.5, 10);
  full_word_at_APCRD4     APCRD4+1. (p.330 l.37, ADCRD1's return) is an
                          instruction boundary: APCRD4 holds a full word;
  landed_words_unchanged  every word of pp.99-334 outside the span is the
                          same with the reconstruction as without it (the
                          merge also refuses a stand-in that disagrees);
  names_<NAME>            the page names the eight landed labels no landed
                          card names (AOCT4A, AOCTH2, APCRD5, ADCRD1, ADCRD2,
                          AERR6, AERR7, APT168 -- check_never_used_symbols.py's
                          ABSENT list, whose reason is "p.329 is missing").
  falls_into_p330         the word before 235154.00 is an unconditional B
                          (p.330 l.1 has no label: only a branch to
                          APCRD4+3.32 may reach it).

MEASURED INJECTIONS (2026-11-16), each on a copy of the deck passed in
P329_DECK (the committed deck is not touched):
  - one half-word statement dropped from AOCTL6's region (BZXVZ,AOCT4A):
    the merge refuses before any check runs, and the run exits 1 with the
    one line "FAIL APCARD: printed p.320 SYNs bit 5150208, printed p.329
    RECONSTRUCTED places it at bit 5150176" (strap/mcp_image.py's
    stand-in check: p.320's APCARD SYN disagrees by a half word).
  - V+,$1,APT168 changed to V+,$1,AOPT24: FAIL names_APT168 only.
  - APCRD4's BBZ,ADCRDI,ADCRD1 replaced by two half-word NOPs (placement
    kept): FAIL full_word_at_APCRD4 and names_ADCRD1 (its only use).
Control (the deck as committed): ALL CHECKS PASSED.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "strap"))
import mcp_image                                            # noqa: E402

fails = 0


def check(name, got, want):
    global fails
    ok = got == want
    fails += not ok
    print(("PASS " if ok else "FAIL ") + name + ("" if ok else f": got {got!r}, want {want!r}"))


LO, HI = 0o235112, 0o235154          # words; p.329 is LO .. HI-1
CITED = {"AOIGN3": 0o235113 * 64, "AOIGN1": 0o235114 * 64 + 32,
         "AOCTH1": 0o235116 * 64, "AOCTL6": 0o235122 * 64 + 32,
         "APCARD": 0o235130 * 64, "APCRD2": 0o235135 * 64,
         "APCRD4": 0o235150 * 64 + 32}
NAMED = ("AOCT4A", "AOCTH2", "APCRD5", "ADCRD1", "ADCRD2", "AERR6", "AERR7", "APT168")


def main():
    deck = os.environ.get("P329_DECK", mcp_image.P329_RECONSTRUCTION)
    pages = mcp_image.pages(99, 334, p329=True)
    pages = [(deck if lab.endswith("RECONSTRUCTED") else p, lab) for p, lab in pages]
    try:
        with_, _s, _d, _e = mcp_image.build(False, pages, end_at="SDISP")
    except Exception as ex:                       # noqa: BLE001
        check("merge_accepts_the_reconstruction", str(ex), "")
        print(f"{fails} FAILED")
        return 1
    without, _s, _d, _e = mcp_image.build(False, mcp_image.pages(99, 334), end_at="SDISP")
    span = set(range(LO, HI))
    check("span_written", sorted(span - set(with_.written_words)), [])
    extra = (set(with_.written_words) - set(without.written_words)) - span
    check("span_only", sorted(extra), [])
    for n, v in CITED.items():
        check("label_" + n, with_.symtab.get(n), v)
    # APCRD4+1. (p.330 l.37 prints 235151.50): ADCRD1 returns a full word
    # past APCRD4, so APCRD4's instruction must be a full word -- bits
    # 24-27 = 1000 (Reference Manual Figure 6, p.18) in the half word at
    # 235150.40, i.e. word bits 56-59.
    w = with_.words.get(0o235150, 0)
    check("full_word_at_APCRD4", (w >> 4) & 0xF, 0b1000)
    diff = [w for w in set(without.written_words) if w not in span
            and with_.words.get(w) != without.words.get(w)]
    check("landed_words_unchanged", sorted(diff), [])
    src = open(deck).read()
    body = src.split("SLC, (8)235112.0", 1)[1]
    code = [ln.split("!")[0] for ln in body.splitlines() if not ln.startswith("!")]
    for n in NAMED:
        check("names_" + n, any(re.search(r"\b%s\b" % n, c.split(None, 1)[-1] if c[:1] != " " else c)
                                for c in code if c.strip()), True)
    # The last statement before 235154.00 is an unconditional branch.
    stmts = [c for c in code if c.strip()]
    last = stmts[-1].split()
    op = last[-1] if len(last) == 1 else last[1] if not stmts[-1].startswith(" ") else last[0]
    check("falls_into_p330", op.split(",")[0], "B")
    print("ALL CHECKS PASSED" if not fails else f"{fails} FAILED")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
