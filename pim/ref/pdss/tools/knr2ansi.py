#!/usr/bin/env python3
"""Rewrite K&R function definitions in PDSS's C sources as ANSI ones.

    knr2ansi.py FILE.c ...      rewrite in place, print a report
    knr2ansi.py --protos FILE.c ...   also print prototypes (stdout)

A one-time, mechanical step of the modernisation (the commit that
applies it contains nothing else).  It recognises, at file scope,

    [storage] [type] name(a, b, c)
        type1 a, *b;
        register type2 c;
    {

and writes ``[storage] type name(type1 a, type1 *b, register type2 c)``
(``int`` where the return type or a parameter's type was implicit,
``(void)`` for an empty list).  Definitions it cannot parse safely
(a preprocessor line among the parameter declarations, for example)
are left untouched and listed, for a hand edit.

With --protos it prints one prototype per definition: ``extern`` ones
for proto.h and ``static`` ones per file, in definition order.
"""
import re
import sys

IDENT = r"[A-Za-z_]\w*"
HEAD = re.compile(r"^(?P<pre>[A-Za-z_][\w \t\*]*?[\s\*])?(?P<name>" + IDENT +
                  r")\((?P<params>[\w\s,]*)\)\s*(?P<cmt>/\*.*\*/)?\s*$")
KEYWORDS = {"if", "while", "for", "switch", "return", "sizeof", "else", "do"}


def strip_comments(s):
    return re.sub(r"/\*.*?\*/", " ", s, flags=re.S)


def split_top(s, sep):
    out, depth, cur = [], 0, ""
    for ch in s:
        if ch in "([":
            depth += 1
        elif ch in ")]":
            depth -= 1
        if ch == sep and depth == 0:
            out.append(cur)
            cur = ""
        else:
            cur += ch
    out.append(cur)
    return out


def declarator_name(d):
    # the identifier of a declarator: `*p`, `a[3]`, `(*f)()`, `**pp`
    m = re.search(r"\(\s*\*+\s*(" + IDENT + r")\s*\)", d)
    if m:
        return m.group(1)
    ids = re.findall(IDENT, d)
    return ids[0] if ids else None


def parse_decls(text):
    """'type a, *b; type2 c;' -> {name: 'type *b'}; None if unparsable."""
    out = {}
    for decl in text.split(";"):
        decl = " ".join(decl.split())
        if not decl:
            continue
        parts = split_top(decl, ",")
        first = parts[0].strip()
        # split `base declarator` in the first part
        m = re.match(r"^(?P<base>.*?)(?P<d>(?:\(|\*)+.*|" + IDENT + r"(?:\s*\[.*\])?)$",
                     first)
        if not m:
            return None
        base, d0 = m.group("base").strip(), m.group("d").strip()
        if not base:
            base = "int"
        if re.fullmatch(r"register", base):
            base = "register int"
        decls = [d0] + [p.strip() for p in parts[1:]]
        for d in decls:
            n = declarator_name(d)
            if n is None:
                return None
            out[n] = base + (" " if not d.startswith("*") else " ") + d
    return out


def convert(path, want_protos):
    src = open(path, encoding="latin-1").read()
    lines = src.split("\n")
    out, protos, skipped = [], [], []
    depth = 0
    i = 0
    in_comment = False
    while i < len(lines):
        line = lines[i]
        m = HEAD.match(line) if depth == 0 and not in_comment else None
        if m and m.group("name") not in KEYWORDS and \
                not (m.group("pre") or "").strip().startswith(("extern", "typedef", "return")):
            # collect parameter declarations up to the opening brace
            j = i + 1
            body = []
            ok = True
            while j < len(lines) and not lines[j].lstrip().startswith("{"):
                if lines[j].lstrip().startswith("#"):
                    ok = False
                    break
                body.append(lines[j])
                j += 1
            if j >= len(lines):
                ok = False
            params = [p.strip() for p in m.group("params").split(",") if p.strip()]
            if any(not re.fullmatch(IDENT, p) or p == "void" for p in params):
                out.append(line)     # already a prototype-style definition
                i += 1
                continue
            decltext = strip_comments("\n".join(body))
            if ok and decltext.strip() and not decltext.strip().endswith(";"):
                ok = False
            decls = parse_decls(decltext) if ok else None
            if ok and decls is not None and set(decls) <= set(params):
                pre = (m.group("pre") or "")
                pre_s = " ".join(pre.split())
                storage = ""
                if pre_s.startswith("static"):
                    storage, pre_s = "static ", pre_s[len("static"):].strip()
                rtype = pre_s if pre_s else "int"
                star = "" if rtype.endswith("*") else " "
                plist = ", ".join(decls.get(p, "int " + p) for p in params) or "void"
                # keep per-parameter comments from the K&R block
                cmts = re.findall(r"/\*.*?\*/", "\n".join(body), flags=re.S)
                head = "%s%s%s%s(%s)" % (storage, rtype, star, m.group("name"), plist)
                if m.group("cmt"):
                    head += " " + m.group("cmt")
                out.append(head)
                for c in cmts:
                    out.append("    " + c)
                protos.append((storage.strip(), "%s%s%s%s(%s);" % (
                    storage, rtype, star, m.group("name"), plist)))
                i = j
                continue
            elif body or not ok:
                skipped.append("%s:%d: %s" % (path, i + 1, line.strip()))
        # track brace depth and comments (good enough for this code base)
        k = 0
        s = line
        while k < len(s):
            if in_comment:
                e = s.find("*/", k)
                if e < 0:
                    break
                in_comment = False
                k = e + 2
                continue
            c = s[k]
            if s.startswith("/*", k):
                in_comment = True
                k += 2
                continue
            if c in "\"'":
                q = c
                k += 1
                while k < len(s) and s[k] != q:
                    if s[k] == "\\":
                        k += 1
                    k += 1
            elif c == "{":
                depth += 1
            elif c == "}":
                depth -= 1
            k += 1
        out.append(line)
        i += 1
    open(path, "w", encoding="latin-1").write("\n".join(out))
    return protos, skipped


def main():
    want = "--protos" in sys.argv
    files = [a for a in sys.argv[1:] if not a.startswith("--")]
    for f in files:
        protos, skipped = convert(f, want)
        for s in skipped:
            print("SKIPPED " + s, file=sys.stderr)
        if want:
            for st, p in protos:
                print("%s\t%s\t%s" % (f, st or "extern", p))


if __name__ == "__main__":
    main()
