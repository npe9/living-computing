#!/usr/bin/env python3
"""Rewrite accesses to record fields that became PREFs (record.h, cell.h).

    prefwrap.py FILE ...     rewrite in place, print a count per file

A one-time, mechanical step of the 64-bit-clean change.  For the record
fields that hold a PREF instead of a pointer (code, pcode, parent,
suspended, other, left_son, right_son, left_brother, right_brother,
input; `next` is shared with pointer-valued fields of other structs and
is done by hand):

    E->f = RHS      becomes  E->f = Ref(RHS)      (0 for NULL / 0, and
                                                   unchanged when RHS is
                                                   itself such a field)
    E->f (a read)   becomes  View(E->f)           (CodeOf, PrecOf, ...)

`&E->f` and increments are left alone, for the compiler to report.
Comments and string literals are skipped.  The compiler, run with
conversion errors on, checks the result.
"""
import re
import sys

VIEW = {"code": "CodeOf", "pcode": "CodeOf", "parent": "PrecOf",
        "left_son": "PrecOf", "right_son": "PrecOf", "left_brother": "PrecOf",
        "right_brother": "PrecOf", "suspended": "GrecOf", "other": "SrecOf",
        "input": "CellOf"}
FIELD = re.compile(r"(->|\.)(" + "|".join(VIEW) + r")\b")
MARK = "\x01"


def code_mask(s):
    """True for characters that are code (not comment / string / char)."""
    m = [True] * len(s)
    i, n = 0, len(s)
    while i < n:
        if s.startswith("/*", i):
            j = s.find("*/", i + 2)
            j = n if j < 0 else j + 2
            for k in range(i, j):
                m[k] = False
            i = j
        elif s[i] in "\"'":
            q, j = s[i], i + 1
            while j < n and s[j] != q:
                j += 2 if s[j] == "\\" else 1
            for k in range(i, min(j + 1, n)):
                m[k] = False
            i = j + 1
        else:
            i += 1
    return m


def expr_start(s, i):
    """Start of the postfix expression whose member access begins at i."""
    j = i
    while True:
        k = j
        while k > 0 and s[k - 1] in " \t":
            k -= 1
        if k > 0 and s[k - 1] in ")]":
            close, opn = s[k - 1], "(" if s[k - 1] == ")" else "["
            d, k = 0, k - 1
            while k >= 0:
                if s[k] == close:
                    d += 1
                elif s[k] == opn:
                    d -= 1
                    if d == 0:
                        break
                k -= 1
            j = k
            # a call or subscript: include the name before it
            while j > 0 and (s[j - 1].isalnum() or s[j - 1] == "_"):
                j -= 1
        elif k > 0 and (s[k - 1].isalnum() or s[k - 1] == "_"):
            j = k
            while j > 0 and (s[j - 1].isalnum() or s[j - 1] == "_"):
                j -= 1
        else:
            return j
        if s[j - 2:j] == "->":
            j -= 2
        elif j > 0 and s[j - 1] == "." and not (j > 1 and s[j - 2].isdigit()):
            j -= 1
        else:
            return j


def rhs_end(s, i):
    d, n = 0, len(s)
    while i < n:
        c = s[i]
        if c in "([{":
            d += 1
        elif c in ")]}":
            if d == 0:
                return i
            d -= 1
        elif c in ";," and d == 0:
            return i
        elif c == "?" and d == 0:
            pass
        i += 1
    return i


def pass_assign(s):
    mask = code_mask(s)
    out, last, n = [], 0, 0
    for m in FIELD.finditer(s):
        if not mask[m.start()] or m.start() < last:
            continue
        k = m.end()
        while k < len(s) and s[k] in " \t":
            k += 1
        if not (s[k:k + 1] == "=" and s[k + 1:k + 2] != "="):
            continue
        a = k + 1
        e = rhs_end(s, a)
        rhs = s[a:e]
        r = rhs.strip()
        # mark the LHS field so that the read pass skips it
        out.append(s[last:m.start()] + m.group(1) + MARK + m.group(2) + s[m.end():a])
        if r.startswith("Ref(") or r.startswith("pdss_ref("):
            new = rhs
        elif r in ("NULL", "0", "(OBJ *)NULL", "(PARENT_RECORD *)NULL"):
            new = " 0"
        elif re.fullmatch(r"[\w\[\]().>-]*(->|\.)(" + "|".join(VIEW) + r")", r):
            new = FIELD.sub(lambda q: q.group(1) + MARK + q.group(2), rhs)
        else:
            lead = rhs[:len(rhs) - len(rhs.lstrip())]
            trail = rhs[len(rhs.rstrip()):]
            new = lead + "Ref(" + r + ")" + trail
        out.append(new)
        last = e
        n += 1
    out.append(s[last:])
    return "".join(out), n


def pass_read(s):
    n = 0
    while True:
        mask = code_mask(s)
        found = None
        for m in FIELD.finditer(s):
            if mask[m.start()] and s[m.start() + len(m.group(1))] != MARK:
                found = m
                break
        if not found:
            return s, n
        m = found
        a = expr_start(s, m.start())
        k = m.end()
        while k < len(s) and s[k] in " \t":
            k += 1
        pre = s[:a].rstrip()
        inview = any(pre.endswith(v + "(") for v in set(VIEW.values()) | {"Ref", "pdss_ref"})
        if inview or s[k:k + 2] in ("++", "--") or pre.endswith("&") and not pre.endswith("&&"):
            s = s[:m.start()] + m.group(1) + MARK + s[m.start() + len(m.group(1)):]
            continue
        # a read that is only compared or tested needs no view, but one is harmless
        view = VIEW[m.group(2)]
        acc = s[a:m.start()] + m.group(1) + MARK + m.group(2)
        s = s[:a] + view + "(" + acc + ")" + s[m.end():]
        n += 1


def main():
    for f in sys.argv[1:]:
        s = open(f, encoding="latin-1").read()
        s, na = pass_assign(s)
        s, nr = pass_read(s)
        s = s.replace(MARK, "")
        open(f, "w", encoding="latin-1").write(s)
        if na or nr:
            print("%s: %d assignments, %d reads" % (f, na, nr))


if __name__ == "__main__":
    main()
