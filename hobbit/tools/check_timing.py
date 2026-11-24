#!/usr/bin/env python3
"""Validate docs/timing.csv against Chapter 4 (and Table 2-4) of the ATT92010
Programmer's Reference Manual (January 1993) and against Table 3-1's
mnemonic census.

Usage:  python3 hobbit/tools/check_timing.py [CSV]

The census is Table 3-1 (printed pp. 3-1 to 3-2): 46 mnemonic entries that
expand to 60 assembled spellings (each [3] entry adds NAME3; the one
JMP(F/N)(Y/N) entry is four spellings).  The same expansion is used by
tools/check_optab.py and docs/isa_inventory.md.  "Covered exactly once" is
enforced at the spelling level: every spelling must appear in exactly one
row's `covers` cell, so every one of the 46 entries is covered, duplicate
rows are rejected, and deleting a row leaves a spelling uncovered.

Checks, all of which must pass:

  1. the CSV parses with the expected header;
  2. row ids are unique;
  3. every row carries a `source` of the form "p. 4-N Table 4-M" and the
     page is the page on which that table is printed (p. 4-2 names the
     tables 4-1 to 4-9; the printed captions read 4-32 to 4-40 -- both
     spellings are accepted and mapped to the same table);
  4. each table has exactly the number of printed lines it prints;
  5. (kind, group) matches the table;
  6. min/max are integers with min <= max for the two-valued tables
     (4-32, 4-33); every other timing cell is a cycle expression built
     from integers, + * ( ) and the p. 4-2 symbols A D Q N E, plus the
     printed-but-undefined S (Table 4-34, "8·S");
  7. every @reference in a note resolves to a row id, and every
     "delays are possible" sentence named in DELAY_CITING_ROWS cites at
     least one delay row;
  8. Table 3-1 coverage: 46/46 entries, 60/60 spellings, each spelling
     exactly once.

  9. Table 2-4 (PRM §2.6, printed p. 2-9, the MMU's address-translation
     penalties) is a table too: 13 printed rows, kind `translation`,
     cited "p. 2-9 Table 2-4", and its cells may use only A (p. 2-9
     defines no other symbol).

Observed injected-defect runs (2026-11-24, after Table 2-4 was added;
baseline exit 0).  Defects A and B are the 2026-11-19 ones, re-run:

  python3 tools/check_timing.py            -> exit 0
      timing.csv: 100 rows
        70 instruction/table rows, 17 delay rows, 13 translation rows, 30 note references
      Table 3-1 coverage: 46/46 entries, 60/60 spellings
        4-32 38, 4-33 8, 4-34 10, 4-35 7, 4-36 7, 4-37 6, 4-38 6,
        4-39 2, 4-40 3, 2-4 13
      OK

  defect A -- deleted the row t432_add (Table 4-32, ADD):
      defect_a.csv: 99 rows
      Table 3-1 coverage: 45/46 entries, 59/60 spellings
      FAIL: Table 4-32 (p. 4-3) has 37 rows, printed lines: 38
      FAIL: UNCOVERED spelling ADD (entry ADD[3])
      2 violation(s)                                       exit 1

  defect B -- blanked the source of row t439_dt1:
      FAIL: t439_dt1: missing source (need "p. 4-N Table 4-M" or "p. 2-9 Table 2-4")
      FAIL: Table 4-39 (p. 4-7) has 1 rows, printed lines: 2
      2 violation(s)                                       exit 1

  defect C -- t24_read_nonpaged's cell A + 3 changed to D + 3:
      FAIL: t24_read_nonpaged: symbol 'D' in Table 2-4, which defines only A (p. 2-9)
      1 violation(s)                                       exit 1

  defect D -- t24_text_tlb_hit cited "p. 2-8 Table 2-4":
      FAIL: t24_text_tlb_hit: malformed source 'p. 2-8 Table 2-4'
      FAIL: Table 2-4 (p. 2-9) has 12 rows, printed lines: 13
      2 violation(s)                                       exit 1
"""
import csv
import re
import sys
from pathlib import Path

CSV = Path(__file__).resolve().parent.parent / "docs" / "timing.csv"

HEADER = ["id", "kind", "group", "op", "variant", "min", "max", "time",
          "covers", "source", "note"]

# Table 3-1, printed pp. 3-1 to 3-2: 46 entries, 60 spellings.
TABLE31 = [
    ("ADD[3]", ["ADD", "ADD3"]),
    ("ADDI", ["ADDI"]),
    ("AND[3]", ["AND", "AND3"]),
    ("ANDI", ["ANDI"]),
    ("CALL", ["CALL"]),
    ("CATCH", ["CATCH"]),
    ("CLRE", ["CLRE"]),
    ("CMPEQ", ["CMPEQ"]),
    ("CMPGT", ["CMPGT"]),
    ("CMPHI", ["CMPHI"]),
    ("CPU", ["CPU"]),
    ("CRET", ["CRET"]),
    ("DIV[3]", ["DIV", "DIV3"]),
    ("DQM", ["DQM"]),
    ("ENTER", ["ENTER"]),
    ("FLUSHD", ["FLUSHD"]),
    ("FLUSHDCE", ["FLUSHDCE"]),
    ("FLUSHI", ["FLUSHI"]),
    ("FLUSHP", ["FLUSHP"]),
    ("FLUSHPBE", ["FLUSHPBE"]),
    ("FLUSHPTE", ["FLUSHPTE"]),
    ("JMP", ["JMP"]),
    ("JMP(F/N)(Y/N)", ["JMPFY", "JMPFN", "JMPTY", "JMPTN"]),
    ("KCALL", ["KCALL"]),
    ("KRET", ["KRET"]),
    ("LDRAA", ["LDRAA"]),
    ("MOV", ["MOV"]),
    ("MOVA", ["MOVA"]),
    ("MUL[3]", ["MUL", "MUL3"]),
    ("NOP", ["NOP"]),
    ("OR[3]", ["OR", "OR3"]),
    ("ORI", ["ORI"]),
    ("POPN", ["POPN"]),
    ("RETURN", ["RETURN"]),
    ("REM[3]", ["REM", "REM3"]),
    ("SHL[3]", ["SHL", "SHL3"]),
    ("SHR[3]", ["SHR", "SHR3"]),
    ("SUB[3]", ["SUB", "SUB3"]),
    ("TADD", ["TADD"]),
    ("TESTC", ["TESTC"]),
    ("TESTV", ["TESTV"]),
    ("TSUB", ["TSUB"]),
    ("UDIV", ["UDIV"]),
    ("UREM", ["UREM"]),
    ("USHR[3]", ["USHR", "USHR3"]),
    ("XOR[3]", ["XOR", "XOR3"]),
]
SPELLINGS = [s for _, group in TABLE31 for s in group]

# Printed caption -> (printed page, rows printed, kind, group).  p. 4-2's
# body text calls the same tables 4-1 to 4-9; the printed captions are
# 4-32 to 4-40 (offset 31).  See docs/timing_tables.md.
TABLES = {
    "4-32": ("4-3", 38, "instruction", "Simple"),
    "4-33": ("4-4", 8, "instruction", "Multi-Cycle Arithmetic"),
    "4-34": ("4-4", 10, "dqm", "DQM"),
    "4-35": ("4-5", 7, "condjump", "Conditional Jump"),
    "4-36": ("4-5", 7, "misc", "Miscellaneous"),
    "4-37": ("4-6", 6, "delay", "Fetch and Empty Pipeline"),
    "4-38": ("4-6", 6, "delay", "Operand Access"),
    "4-39": ("4-7", 2, "delay", "Data Type"),
    "4-40": ("4-7", 3, "delay", "Miscellaneous"),
    # PRM §2.6, printed p. 2-9: Table 2-4, Address Translation Performance
    # (13 printed rows, read from the page image; no text layer is
    # trusted).  Its cells use only A, "the I/O delay for a single word
    # access" (p. 2-9).
    "2-4": ("2-9", 13, "translation", "Address Translation Performance"),
}
# Symbols each table outside Chapter 4 may use: p. 2-9 defines only A.
TABLE_SYMBOLS = {"2-4": {"A"}}

# p. 4-2 defines IC PDU A D Q M N SC E EU.  A, D, Q, N and E are used in
# cycle expressions; S is not defined and appears only in Table 4-34's
# "8·S" row, recorded verbatim (see timing_tables.md, errata).
SYMBOLS = {"A", "D", "Q", "N", "E", "S"}

# Notes that must cite at least one delay row: the sentences on pp. 4-3 to
# 4-5 that say which delay tables may apply to a group.
DELAY_CITING_ROWS = {
    "t433_div", "t433_mul", "t434_const_sc_dw", "t435_correct_folded",
    "t436_catch",
}

SOURCE_RE = re.compile(
    r"^p\. ((?:4-[1-7])|(?:2-9)) Table (4-(?:3[2-9]|40|[1-9])|2-4)$")
ID_RE = re.compile(r"^[a-z0-9_]+$")
REF_RE = re.compile(r"@([a-z0-9_]+)")
EXPR_RE = re.compile(r"^[0-9A-Za-z+*()\u00b7 ]+$")


def normalise_table(cited):
    """Map a cited table to its printed caption: Chapter 4's body names
    4-1 .. 4-9 become 4-32 .. 4-40; Table 2-4 is itself."""
    chapter, n = cited.split("-")
    if chapter == "4" and int(n) <= 9:
        return f"4-{int(n) + 31}"
    return cited


def parse_expr(cell):
    """Validate a cycle expression; return an error string or None.

    The manual writes products both with a centred dot and by
    juxtaposition ("2·D", "2D").  Repetition is preserved verbatim, so
    this only checks the alphabet and parenthesis balance; it does not
    evaluate.
    """
    if not cell:
        return "empty time"
    if not EXPR_RE.match(cell):
        return f"illegal characters in {cell!r}"
    depth = 0
    for ch in cell:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth < 0:
                return f"unbalanced parentheses in {cell!r}"
    if depth:
        return f"unbalanced parentheses in {cell!r}"
    for word in re.findall(r"[A-Za-z]+", cell):
        if word not in SYMBOLS:
            return f"undefined symbol {word!r} in {cell!r}"
    return None


def load(path):
    with path.open(newline="", encoding="utf-8") as fh:
        return list(csv.reader(fh))


def main(argv):
    path = Path(argv[1]) if len(argv) > 1 else CSV
    try:
        rows = load(path)
    except OSError as exc:
        print(f"{path}: {exc}")
        return 1

    errors = []
    if not rows or rows[0] != HEADER:
        print(f"{path}: header is not {','.join(HEADER)}")
        return 1

    body = rows[1:]
    print(f"{path.name}: {len(body)} rows")

    ids = {}
    per_table = {t: 0 for t in TABLES}
    covers = {}
    delays = set()
    translations = set()

    for lineno, row in enumerate(body, start=2):
        if len(row) != len(HEADER):
            errors.append(f"line {lineno}: {len(row)} fields, expected "
                          f"{len(HEADER)}")
            continue
        rec = dict(zip(HEADER, row))
        rid = rec["id"]

        if not ID_RE.match(rid):
            errors.append(f"line {lineno}: bad id {rid!r}")
        if rid in ids:
            errors.append(f"line {lineno}: duplicate id {rid}")
        ids[rid] = rec

        # 3. source cite and page
        m = SOURCE_RE.match(rec["source"])
        if not rec["source"]:
            errors.append(f"{rid}: missing source (need "
                          f"\"p. 4-N Table 4-M\" or \"p. 2-9 Table 2-4\")")
        elif not m:
            errors.append(f"{rid}: malformed source {rec['source']!r}")
        else:
            table = normalise_table(m.group(2))
            if table not in TABLES:
                errors.append(f"{rid}: unknown table {table}")
            else:
                page, _, kind, group = TABLES[table]
                per_table[table] += 1
                if m.group(1) != page:
                    errors.append(f"{rid}: Table {table} is printed on "
                                  f"p. {page}, cited p. {m.group(1)}")
                if rec["kind"] != kind:
                    errors.append(f"{rid}: kind {rec['kind']!r}, Table "
                                  f"{table} is {kind!r}")
                if rec["group"] != group:
                    errors.append(f"{rid}: group {rec['group']!r}, Table "
                                  f"{table} is {group!r}")

        # 6. timing cells
        if rec["kind"] == "delay":
            delays.add(rid)
        if rec["kind"] == "translation":
            translations.add(rid)
            allowed = TABLE_SYMBOLS["2-4"]
            for word in re.findall(r"[A-Za-z]+", rec["time"]):
                if word not in allowed:
                    errors.append(f"{rid}: symbol {word!r} in Table 2-4, "
                                  f"which defines only A (p. 2-9)")
        if rec["kind"] == "instruction" and rec["group"] in (
                "Simple", "Multi-Cycle Arithmetic"):
            try:
                lo, hi = int(rec["min"]), int(rec["max"])
            except ValueError:
                errors.append(f"{rid}: min/max must be integers")
            else:
                if lo > hi:
                    errors.append(f"{rid}: min {lo} > max {hi}")
                if rec["time"]:
                    errors.append(f"{rid}: has both min/max and time")
        else:
            if rec["min"] or rec["max"]:
                errors.append(f"{rid}: min/max only for Tables 4-32 and 4-33")
            bad = parse_expr(rec["time"])
            if bad:
                errors.append(f"{rid}: {bad}")

        # 8. coverage tokens
        for token in filter(None, (t.strip()
                                   for t in rec["covers"].split(";"))):
            if token not in SPELLINGS:
                errors.append(f"{rid}: covers unknown mnemonic {token!r}")
            covers.setdefault(token, []).append(rid)

    # 4. printed line counts
    for table, (page, printed, _, _) in TABLES.items():
        got = per_table[table]
        if got != printed:
            errors.append(f"Table {table} (p. {page}) has {got} rows, "
                          f"printed lines: {printed}")

    # 7. note references
    refs = 0
    for rid, rec in ids.items():
        for target in REF_RE.findall(rec["note"]):
            refs += 1
            if target not in ids:
                errors.append(f"{rid}: note references missing row @{target}")
        if rid in DELAY_CITING_ROWS and not any(
                t in delays for t in REF_RE.findall(rec["note"])):
            errors.append(f"{rid}: note must cite a delay row with @id")

    # 8. Table 3-1 census
    entries_ok = spellings_ok = 0
    for entry, spellings in TABLE31:
        entry_ok = True
        for s in spellings:
            owners = covers.get(s, [])
            if not owners:
                errors.append(f"UNCOVERED spelling {s} (entry {entry})")
                entry_ok = False
            elif len(owners) > 1:
                errors.append(f"DUPLICATE coverage of {s}: {', '.join(owners)}")
                entry_ok = False
            else:
                spellings_ok += 1
        if entry_ok:
            entries_ok += 1

    print(f"  {len(body) - len(delays) - len(translations)} "
          f"instruction/table rows, {len(delays)} delay rows, "
          f"{len(translations)} translation rows, {refs} note references")
    print(f"Table 3-1 coverage: {entries_ok}/{len(TABLE31)} entries, "
          f"{spellings_ok}/{len(SPELLINGS)} spellings")
    print("  " + ", ".join(f"{t} {per_table[t]}" for t in TABLES))

    for err in errors:
        print(f"FAIL: {err}")
    if errors:
        print(f"{len(errors)} violation(s)")
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
