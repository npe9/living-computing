#!/usr/bin/env python3
"""Statement drafts confirmed by assembly (tools/statement_confirm.py).

CHECKS

  table_fresh          docs/vision/listing_statements.tsv is what the
                       reading produces now
  hex_vs_deck          every asm-confirmed statement on a landed page whose
                       deck prints a hex byte assembles to THAT byte: the
                       octal fields were matched by construction, the hex
                       byte (opcode bits the octal does not show) was not
  floor_confirmed      the share of eligible landed lines confirmed, and
  floor_text           the share of those whose text is the deck's, are
                       what was measured (2026-11-04, leave-one-page-out:
                       1,466 of 3,520 = 41.6%; 92.6% text-equal; hex 1,432
                       of 1,432) -- so a broken assembler or repair cannot
                       pass by confirming less

MEASURED INJECTIONS (python3 check_statement_confirm.py --inject):

    control, nothing changed                          PASS
    deck hex byte of the first confirmed row changed  FAIL hex_vs_deck
    one row of listing_statements.tsv edited          FAIL table_fresh
"""
import os
import re
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import statement_confirm as SC      # noqa: E402

CONFIRMED_FLOOR, TEXT_FLOOR = 0.38, 0.90


def main(root=ROOT):
    fails = 0

    def ok(cond, name, text):
        nonlocal fails
        print(("PASS " if cond else "FAIL ") + name + " = " + text)
        fails += not cond

    path = os.path.join(root, "docs", "vision", "listing_statements.tsv")
    fresh = SC.table(SC.reading(root), root) == open(path).read()
    ok(fresh, "table_fresh", "listing_statements.tsv" +
       ("" if fresh else " -- STALE: run python3 tools/statement_confirm.py"))
    c = SC.score(root, quiet=True)
    for b in c.get("bad", [])[:10]:
        print(f"FAIL hex_vs_deck: p.{b[0]} line {b[1]} {b[2]}: assembled hex {b[3]}, deck prints {b[4]}")
    ok(c["hex"] and c["hex_ok"] == c["hex"], "hex_vs_deck",
       f"{c['hex_ok']} of {c['hex']} confirmed statements assemble to the deck's hex byte")
    e = max(1, c["eligible"])
    ok(c["confirmed"] / e >= CONFIRMED_FLOOR, "floor_confirmed",
       f"{c['confirmed']} of {c['eligible']} eligible landed lines ({100 * c['confirmed'] / e:.1f}%, "
       f"floor {100 * CONFIRMED_FLOOR:.0f}%)")
    t = c["text"] / max(1, c["confirmed"])
    ok(t >= TEXT_FLOOR, "floor_text",
       f"{c['text']} of {c['confirmed']} confirmed equal the deck's text ({100 * t:.1f}%, "
       f"floor {100 * TEXT_FLOOR:.0f}%)")
    print("ALL TESTS PASSED" if not fails else f"{fails} CHECK(S) FAILED")
    return fails


def inject():
    def scratch():
        td = tempfile.mkdtemp(prefix="stmt-inject-")
        shutil.copytree(os.path.join(ROOT, "decks"), os.path.join(td, "decks"))
        os.symlink(os.path.join(ROOT, "tests"), os.path.join(td, "tests"))
        shutil.copytree(os.path.join(ROOT, "docs", "vision"), os.path.join(td, "docs", "vision"))
        return td
    res = []
    td = scratch()
    res.append(("control", main(td)))
    shutil.rmtree(td)

    # the first confirmed row whose deck !CHECK prints a hex byte: change it
    td = scratch()
    target = None
    for ln in open(os.path.join(td, "docs", "vision", "listing_statements.tsv")).read().splitlines()[1:]:
        vol, pdf, printed, line, st, stmt, a = ln.split("\t")
        if st != "asm-confirmed" or vol != "1" or not printed:
            continue
        deck = os.path.join(td, "decks", "mcp_bootstrap_p%s.strap" % printed)
        if not os.path.exists(deck):
            continue
        h1, hx = a.split()[:2]
        bad = "%02X" % (int(hx, 16) ^ 0x01)
        s = open(deck).read()
        t = re.sub(r"^(!CHECK\s+[0-7.]+\s*\|\s*" + re.escape(h1) + r"\s+)" + hx + r"(\b[^\n]*\|\s*line\s+%s\b)" % line,
                   r"\g<1>" + bad + r"\g<2>", s, count=1, flags=re.M)
        if t != s:
            target = (printed, line, hx, bad, deck, t)
            break
    assert target, "hex injection found no row to change"
    printed, line, hx, bad, deck, t = target
    open(deck, "w").write(t)
    print(f"-- injected: p.{printed} line {line} deck hex {hx} -> {bad}")
    res.append((f"deck hex p.{printed} line {line}", main(td)))
    shutil.rmtree(td)

    td = scratch()
    f = os.path.join(td, "docs", "vision", "listing_statements.tsv")
    s = open(f).read().split("\n")
    s[100] += "x"
    open(f, "w").write("\n".join(s))
    print("-- injected: listing_statements.tsv row 100 edited")
    res.append(("table row", main(td)))
    shutil.rmtree(td)
    print("INJECTIONS: " + ", ".join(f"{n} -> {'FAIL' if r else 'PASS'}" for n, r in res))


if __name__ == "__main__":
    if sys.argv[1:] == ["--inject"]:
        inject()
    else:
        sys.exit(main())
