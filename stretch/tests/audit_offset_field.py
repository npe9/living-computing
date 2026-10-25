#!/usr/bin/env python3
"""audit_offset_field.py -- decode the VFL offset out of the PRINTED
BINARY OUTPUT column of every transcribed MCP page and compare it
with the offset the deck's STRAP statement writes.

THE RULE UNDER TEST, from docs/NEXT.md:

    the VFL offset is a SEVEN-BIT FIELD AT BITS 12-18 of the second
    printed group, negatives in two's complement

and the reason it is worth a tool is that bits 12-18 STRADDLE the
printed group's dot.  A group prints as WWWWWW.BB FF -- eighteen bits
of word address in octal, six of bit address in octal, eight flag
bits in hex -- so bits 12-17 are the last two octal digits of WWWWWW
and bit 18 is the top bit of BB.  Read the WWWWWW column alone and
every offset looks HALVED, with the odd bit hiding next door.  That
appearance is what this rule explains, and a person transcribing a
row by eye needs it.

>>> THIS IS AN AUDIT, NOT A SUITE TEST, AND THE DIFFERENCE MATTERS. <<<
listing_oracle.check_rows already compares each assembled word with
its printed column bit-for-bit, so an assembler that placed the
offset anywhere else would fail there first.  Asserting the decode
too would measure the assembler against itself and could never fail.
What this produces is evidence for the READING RULE.  Run it when
that rule is questioned, or after transcribing a page with unusual
offsets.  It takes no arguments and writes nothing.

FORMAT 7 ONLY.  Bits 12-18 of a BRANCH, TRANSMIT or I/O word are not
an offset.  Sweeping those rows too turns 331 clean agreements into
236 meaningless disagreements, every one a different instruction
format.  The mnemonic filter is what keeps the number honest.

THE STATEMENT COMES FROM THE DECK, NOT THE VERIFIER'S LABEL.  Labels
are often abbreviated -- "ST(BU,7)" where the deck says
"ST(BU,7), 0.57(LXSU), 46" -- so the verifier's row gives the LINE
NUMBER and the deck's "! line NN" comment gives the statement.  A
first version read the labels instead and reported twenty rows it
could not parse; all twenty were abbreviations or expressions and
all twenty agreed once resolved by hand.

>>> AND THE OFFSET IS THE LAST OF TWO OPERANDS, NOT THE LAST NUMBER
ON THE LINE. <<<  STRAP format 7 is "OP(dds), ADDRESS, OFFSET".  With
only ONE operand there is no offset and STRAP defaults it to zero --
so "KFI(BU,4), 9" has offset 0 and that 9 is the IMMEDIATE OPERAND.
A second version took the trailing number and reported four such rows
as FAILURES of the rule.  They were failures of the parser.  Counting
operands is the whole fix, and it is why this script splits on
top-level commas rather than running a regex at the end of the line.

RESULT ON 2026-10-25: 299 rows reached, 297 parsed and ALL AGREEING,
0 disagreements, and 2 offsets written as expressions and checked by
hand -- "18+9" = 27 on printed p.16, and "64+QKSIZ" = 70 on printed
p.45 where p.45 line 24 declares "QKSIZ SYN, 6".

The 299 is lower than the 331 VFL/connective rows the pages hold
because a row is only reached when its deck line carries a
"! line NN" comment to match the verifier's row against.  That is a
limit of the matching, not of the rule.
"""
import glob
import os
import re
import sys

HERE = os.environ.get("STRETCH_TESTS",
                      os.path.dirname(os.path.abspath(__file__)))
DECKS = os.path.join(HERE, "..", "decks")

# Format 7 (VFL) and the connectives; "$" prefixes an indirect form.
VFL = re.compile(
    r'^\$?(?:L|LF|LFI|LWF|ST|SF|SRD|K|KF|KFE|KFI|KFR|KR|KE|M\+1|M\+MG|M\+'
    r'|\+MG|\+|-|\*|/|CV|LCV|LTRCV|DCV|LFT|LTRS'
    r'|C[01]{4}|CM[01]{4}|CT[01]{4})\s*\(')

ROW = re.compile(r'\("(\d{6}\.\d\d)",\s*\n?\s*"([^"]*)",\s*\n?\s*"line\s+(\d+)')


def second_group(printed):
    """The second printed group as 32 bits: WWWWWW.BB FF, octal/octal/hex."""
    tok = printed.split()
    if len(tok) != 4 or "." not in tok[2]:
        return None
    word, bit = tok[2].split(".")
    try:
        return (int(word, 8) << 14) | (int(bit, 8) << 8) | int(tok[3], 16)
    except ValueError:
        return None


def offset_field(group):
    """Bits 12-18, IBM numbering within the group (bit 0 is leftmost)."""
    return (group >> (31 - 18)) & 0x7F


def deck_statements(page):
    """{line number: statement} for one transcribed page."""
    path = os.path.join(DECKS, f"mcp_bootstrap_p{page}.strap")
    out = {}
    if not os.path.exists(path):
        return out
    for raw in open(path):
        if raw.lstrip().startswith("!"):
            continue
        code, sep, comment = raw.partition("!")
        m = re.match(r'\s*line\s+(\d+)\b', comment) if sep else None
        if m and code.strip():
            out[m.group(1)] = code.strip()
    return out


def operands(stmt):
    """The comma-separated operand fields after "MNEMONIC(dds)".

    Splits on TOP-LEVEL commas only, so "(BU,8,8)" and "0.0(LXSU)"
    stay whole.  Returns None if the statement has no operand list.
    """
    # the mnemonic, then ANY number of parenthesised groups: a data
    # description "(BU,8,8)" and/or a progressive suffix "(V+I)", in
    # either order -- printed p.22 writes "L(BU,8)(V+I)" and printed
    # p.17 writes "L(V+I)(BU,48)".
    m = re.match(r'\s*\$?[A-Za-z0-9+\-*/]+\s*(?:\([^)]*\)\s*)*,?', stmt)
    if not m:
        return None
    rest, depth, cur, out = stmt[m.end():], 0, "", []
    for ch in rest:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        if ch == "," and depth == 0:
            out.append(cur.strip())
            cur = ""
        else:
            cur += ch
    if cur.strip():
        out.append(cur.strip())
    return [o for o in out if o]


def expected_offset(stmt):
    """The offset the statement writes, or None if it cannot be read here.

    STRAP format 7 is "OP(dds), ADDRESS, OFFSET" and the offset is the
    LAST field when there are two.  With ONE field there is no offset
    and STRAP defaults it to zero -- which is why "KFI(BU,4), 9" is
    offset 0 and not offset 9: that 9 is the IMMEDIATE OPERAND.  A
    first version of this script read the last number on the line and
    reported four such rows as failures.
    """
    ops = operands(stmt)
    if ops is None:
        return None
    if len(ops) <= 1:
        return 0
    last = ops[-1]
    if re.fullmatch(r'-?\d+', last):
        return int(last) % 128
    # a bit-address literal: "0.0" is WORD.BIT, and an offset written
    # that way is words*64 + bits.  printed pp.55-58 write "0.0" for a
    # zero offset rather than leaving it off.
    m = re.fullmatch(r'(\d+)\.(\d+)', last)
    if m:
        return (int(m.group(1)) * 64 + int(m.group(2))) % 128
    return None          # an expression: "18+9", "64+QKSIZ"


def main():
    agree = differ = 0
    unparsed = []
    for path in sorted(glob.glob(os.path.join(HERE, "verify_mcp_bootstrap_p*.py"))):
        txt = open(path).read()
        if "ROWS = [" not in txt:
            continue
        page = os.path.basename(path).split("_p")[-1][:-3]
        stmts = deck_statements(page)
        for addr, printed, line in ROW.findall(txt[txt.index("ROWS = ["):]):
            if "+" in printed:              # CW rows print in another format
                continue
            group = second_group(printed)
            if group is None:
                continue
            stmt = stmts.get(line)
            if stmt is None:
                continue
            # a leading label is separated from the statement by two spaces
            body = re.sub(r'^[A-Z0-9][A-Z0-9 ]*?\s\s+', '', stmt)
            if not VFL.match(body):
                continue
            got = offset_field(group)
            want = expected_offset(body)
            if want is None:
                unparsed.append((page, addr, got, body))
            elif got == want:
                agree += 1
            else:
                differ += 1
                print(f"DIFFER p{page:>3} {addr} column {got:3d}, "
                      f"statement {want:3d}: {body}")

    total = agree + differ + len(unparsed)
    print(f"VFL/connective rows : {total}")
    print(f"  agree             : {agree}")
    print(f"  DIFFER            : {differ}")
    print(f"  offset written as an expression (resolve by hand): {len(unparsed)}")
    for page, addr, got, stmt in unparsed:
        print(f"      p{page:>3} {addr}  column says {got:3d}   {stmt}")
    return 1 if differ else 0


if __name__ == "__main__":
    sys.exit(main())
