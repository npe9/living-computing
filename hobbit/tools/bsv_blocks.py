#!/usr/bin/env python3
"""bsv_blocks.py -- declaration-level structure for Bluespec SystemVerilog.

`ast_edit` and ast-grep cannot parse `.bsv` (no tree-sitter grammar), so the
editor has no structural view of a Bluespec file.  This is the equivalent
that is honest about what it is: a *tokeniser* plus brace/keyword matching,
which knows the file's blocks and their exact byte ranges and nothing about
the language's semantics.  Every edit it proposes is printed with its ranges
and is only written with `--apply`; `bsc` remains the judge.

Blocks it recognises (each with its own terminator unless noted):

    package … endpackage            interface … endinterface
    module … endmodule              function … endfunction
    rule … endrule                  method … endmethod
    typedef struct/enum/union … }   instance … endinstance

    other braced forms: begin … end, case … endcase, for … end

Commands

    list FILE                   one line per block, outermost first
    show FILE NAME              the block's text, with its leading comments
    enclosing FILE LINE         the innermost block containing LINE
    check FILE…                 balance and nesting errors, per file
    rename FILE --in BLOCK OLD NEW [--apply]
                                word-boundary rename inside BLOCK only,
                                skipping comments and string literals
    move FILE --block BLOCK --to FILE2 --module MODULE [--apply]
                                cut BLOCK (with the comments directly above
                                it) and insert it before MODULE's endmodule

Why this shape: the codemods this repository actually performs are
move-a-rule, delete-a-rule, rename-a-signal-within-a-block, and ask "which
module owns this rule".  All four need block boundaries and word
boundaries, neither of which needs a full grammar; a half-grammar would be
*worse* than this because it would silently mis-parse and rewrite.

Exit status: 0 on success (and for a clean `check`), 1 on a structural
error, 2 on a usage error.
"""

import argparse
import sys

# keyword -> its terminator; None means "the block ends with a brace"
KEYWORD_BLOCKS = {
    "package": "endpackage",
    "interface": "endinterface",
    "module": "endmodule",
    "function": "endfunction",
    "rule": "endrule",
    "method": "endmethod",
    "instance": "endinstance",
    "begin": "end",
    "case": "endcase",
}
# Names whose closing brace is `}`, opened by `typedef struct {`
BRACED_TYPEDEF = ("struct", "enum", "union")


class Block:
    __slots__ = ("kind", "name", "start_line", "end_line", "start", "end",
                 "children", "parent", "closed", "depth")

    def __init__(self, kind, name, start, start_line):
        self.kind = kind
        self.name = name
        self.start = start
        self.start_line = start_line
        self.end = None
        self.end_line = None
        self.closed = False
        self.depth = 0
        self.children = []
        self.parent = None

    def label(self):
        return f"{self.kind} {self.name}".strip()


def strip_mask(text):
    """A copy of `text` with comments and string literals blanked to spaces.

    Offsets are preserved, so matches found in the mask index straight into
    the original text.  Newlines are kept so line numbers stay right.
    """
    out = list(text)
    i, n = 0, len(text)
    while i < n:
        c = text[i]
        if c == "/" and i + 1 < n and text[i + 1] == "/":
            while i < n and text[i] != "\n":
                out[i] = " "
                i += 1
        elif c == "/" and i + 1 < n and text[i + 1] == "*":
            out[i] = out[i + 1] = " "
            i += 2
            while i < n and not (text[i] == "*" and i + 1 < n and text[i + 1] == "/"):
                if text[i] != "\n":
                    out[i] = " "
                i += 1
            if i < n:
                out[i] = out[i + 1] = " "
                i += 2
        elif c == '"':
            out[i] = " "
            i += 1
            while i < n and text[i] != '"':
                if text[i] == "\\" and i + 1 < n:
                    out[i] = " "
                    i += 1
                if text[i] != "\n":
                    out[i] = " "
                i += 1
            if i < n:
                out[i] = " "
                i += 1
        else:
            i += 1
    return "".join(out)


def word_at(mask, pos):
    end = pos
    while end < len(mask) and (mask[end].isalnum() or mask[end] in "_'"):
        end += 1
    return mask[pos:end]


def block_name(mask, text, kw_start, kw):
    """The block's name: the first identifier after the keyword, where the
    printed language puts one.  `rule step` -> step, `module mkCore#(...)`
    -> mkCore, `typedef struct {` -> the typedef's name (which follows the
    closing brace, so it is taken from the line)."""
    i = kw_start + len(kw)
    while i < len(mask) and mask[i] in " \t":
        i += 1
    if i < len(mask) and mask[i] == "(":      # rule (guard)
        return ""
    # `function Bool isZero(...)` and `method Word get()` put the name
    # immediately before the parameter list; `module mkTop(...)` and
    # `interface Top;` put it first.
    if kw in ("function", "method"):
        lp = mask.find("(", i)
        semi = mask.find(";", i)
        if lp > 0 and (semi < 0 or lp < semi):
            j = lp - 1
            while j >= i and mask[j] in " \t":
                j -= 1
            k = j
            while k >= i and (mask[k].isalnum() or mask[k] in "_'"):
                k -= 1
            return mask[k + 1:j + 1]
    return word_at(mask, i)


def line_of(text, pos):
    return text.count("\n", 0, pos) + 1


def parse_blocks(text):
    """Every block, outermost first, each with its parent."""
    mask = strip_mask(text)
    root = Block("file", "", 0, 1)
    stack = [root]
    depth = 0
    i, n = 0, len(mask)
    while i < n:
        ch = mask[i]
        if ch in " \t\r\n":
            i += 1
            continue
        if ch == "{":
            # Braces appear in expressions too (`{30'd0, lane}`), so the
            # depth is tracked and a struct closes only at its own level.
            depth += 1
            if stack[-1].kind in ("struct", "enum", "union") and stack[-1].depth == depth - 1:
                pass
            i += 1
            continue
        if ch == "}":
            depth -= 1
            b = stack[-1]
            if b.kind in ("struct", "enum", "union") and depth == b.depth:
                b.end = i + 1
                b.end_line = line_of(text, i)
                b.closed = True
                stack.pop()
            i += 1
            continue
        if ch.isalpha() or ch == "_":
            w = word_at(mask, i)
            term = KEYWORD_BLOCKS.get(w)
            if w == "interface":
                # A module's `interface Server s;` is a declaration, not a
                # block: it ends at `;`, and there is no `endinterface`.
                # `interface Name;` opens a block; `interface Type name;`
                # (two identifiers before the semicolon) is a declaration
                # inside a module, with no `endinterface`.
                semi = mask.find(";", i)
                endi = mask.find("endinterface", i)
                if 0 <= semi and (endi < 0 or semi < endi):
                    head = mask[i + len("interface"):semi]
                    if len(head.split()) >= 2:
                        term = None
            if w == "function":
                # `function T f(args) = expr;` is complete at the semicolon;
                # the block form ends with `endfunction`.  Tell them apart by
                # the same line: a one-liner has an `=` before its `;` and no
                # newline in between.  A block's first `;` is a declaration
                # *inside* the body, which is on later lines.
                semi = mask.find(";", i)
                if semi > 0:
                    head = mask[i:semi]
                    depth, eq = 0, False
                    for k, c in enumerate(head):
                        if c == "(":
                            depth += 1
                        elif c == ")":
                            depth -= 1
                        elif c == "=" and depth == 0:
                            prev = head[k - 1] if k else ""
                            nxt = head[k + 1] if k + 1 < len(head) else ""
                            if prev not in "=!<>" and nxt != "=":
                                eq = True
                    if eq:
                        term = None
            if w == "method":
                # An interface declares `method T name(...);` -- no body, no
                # `endmethod`.  A module defines `method ... endmethod`.
                # Decide by whichever comes first after the keyword.
                semi = mask.find(";", i)
                endm = mask.find("endmethod", i)
                if 0 <= semi and (endm < 0 or semi < endm):
                    term = None
            if term is not None:
                b = Block(w, block_name(mask, text, i, w), i, line_of(text, i))
                b.parent = stack[-1]
                stack[-1].children.append(b)
                stack.append(b)
            elif w == "typedef":
                j = i + len(w)
                rest = mask[j:j + 80]
                lb = rest.find("{")
                ls = rest.find(";")
                if not (0 <= lb and (ls < 0 or lb < ls)):
                    lb = -1
                for kind in (BRACED_TYPEDEF if lb >= 0 else ()):
                    if kind in rest[:lb]:
                        b = Block(kind, "", i, line_of(text, i))
                        b.depth = depth
                        b.parent = stack[-1]
                        stack[-1].children.append(b)
                        stack.append(b)
                        break
            elif w == "end" and stack[-1].kind == "begin":
                b = stack.pop()
                b.end = i + len(w)
                b.end_line = line_of(text, i)
                b.closed = True
            elif term is None and w.startswith("end") and stack[-1].kind == w[3:]:
                b = stack.pop()
                b.end = i + len(w)
                b.end_line = line_of(text, i)
                b.closed = True
            i += len(w)
            continue
        i += 1
    for b in walk(root):
        if b.end is None and b.kind != "file":
            b.end = n
            b.end_line = line_of(text, n)
    return root, mask


def walk(block):
    yield block
    for c in block.children:
        yield from walk(c)


def find(root, name):
    hits = [b for b in walk(root) if b.kind != "file" and
            (b.label() == name or b.name == name or b.label().endswith(" " + name))]
    return hits


def block_span(text, b):
    """A block's text including the comment lines directly above it."""
    start = b.start
    line_start = text.rfind("\n", 0, start) + 1
    while True:
        prev_end = line_start - 1
        if prev_end <= 0:
            break
        prev_start = text.rfind("\n", 0, prev_end) + 1
        line = text[prev_start:prev_end].strip()
        if line.startswith("//"):
            line_start = prev_start
        else:
            break
    return line_start, b.end


def cmd_list(a):
    text = open(a.file, encoding="utf-8").read()
    root, _ = parse_blocks(text)
    for b in walk(root):
        if b is root:
            continue
        depth = 0
        p = b.parent
        while p is not None and p is not root:
            depth += 1
            p = p.parent
        print(f"{b.start_line:6d}-{b.end_line:6d}  {'  ' * depth}{b.label()}")
    return 0


def cmd_show(a):
    text = open(a.file, encoding="utf-8").read()
    root, _ = parse_blocks(text)
    hits = find(root, a.name)
    if not hits:
        print(f"bsv_blocks: no block named {a.name!r}", file=sys.stderr)
        return 2
    b = hits[0]
    s, e = block_span(text, b)
    sys.stdout.write(text[s:e])
    sys.stdout.write("\n")
    return 0


def cmd_enclosing(a):
    text = open(a.file, encoding="utf-8").read()
    root, _ = parse_blocks(text)
    best = None
    for b in walk(root):
        if b is root:
            continue
        if b.start_line <= a.line <= b.end_line:
            if best is None or (b.end_line - b.start_line) <= (best.end_line - best.start_line):
                best = b
    if best is None:
        print("(no block)")
    else:
        print(best.label(), f"lines {best.start_line}-{best.end_line}")
    return 0


def cmd_check(a):
    bad = 0
    for path in a.files:
        text = open(path, encoding="utf-8").read()
        root, _ = parse_blocks(text)
        open_blocks = [b for b in walk(root) if b.kind != "file" and not b.closed]
        for b in open_blocks:
            print(f"{path}:{b.start_line}: unclosed {b.label()}")
            bad += 1
        # a block must not start before its parent and end after it
        for b in walk(root):
            p = b.parent
            while p is not None and p.kind != "file":
                if b.start < p.start or (b.end or 0) > (p.end or 0):
                    print(f"{path}:{b.start_line}: {b.label()} escapes {p.label()}")
                    bad += 1
                p = p.parent
    return 1 if bad else 0


def rewrite_span(text, start, end, old, new):
    """Word-boundary replacement of `old` by `new` in text[start:end],
    skipping comments and string literals."""
    seg = text[start:end]
    mask = strip_mask(seg)
    out, i = [], 0
    hits = 0
    while True:
        j = mask.find(old, i)
        if j < 0:
            out.append(seg[i:])
            break
        before_ok = j == 0 or not (mask[j - 1].isalnum() or mask[j - 1] == "_")
        after_ok = (j + len(old) >= len(mask) or
                    not (mask[j + len(old)].isalnum() or mask[j + len(old)] == "_"))
        out.append(seg[i:j])
        if before_ok and after_ok:
            out.append(new)
            hits += 1
        else:
            out.append(seg[j:j + len(old)])
        i = j + len(old)
    return "".join(out), hits


def cmd_rename(a):
    text = open(a.file, encoding="utf-8").read()
    root, _ = parse_blocks(text)
    hits = find(root, a.in_block)
    if not hits:
        print(f"bsv_blocks: no block named {a.in_block!r}", file=sys.stderr)
        return 2
    b = hits[0]
    s, e = block_span(text, b)
    new_seg, count = rewrite_span(text, s, e, a.old, a.new)
    print(f"{b.label()}: {count} occurrence(s) of {a.old!r} -> {a.new!r} "
          f"in lines {line_of(text, s)}-{b.end_line}")
    if count and a.apply:
        open(a.file, "w", encoding="utf-8").write(text[:s] + new_seg + text[e:])
        print("applied")
    elif count:
        sys.stdout.write(new_seg)
    return 0


def cmd_move(a):
    src_text = open(a.file, encoding="utf-8").read()
    root, _ = parse_blocks(src_text)
    hits = find(root, a.block)
    if not hits:
        print(f"bsv_blocks: no block named {a.block!r}", file=sys.stderr)
        return 2
    b = hits[0]
    s, e = block_span(src_text, b)
    chunk = src_text[s:e].rstrip("\n") + "\n"
    dst_text = open(a.to, encoding="utf-8").read()
    droot, _ = parse_blocks(dst_text)
    mods = [m for m in find(droot, a.module) if m.kind == "module"]
    if not mods:
        print(f"bsv_blocks: no module named {a.module!r} in {a.to}", file=sys.stderr)
        return 2
    m = mods[0]
    end_kw = dst_text.rfind("endmodule", m.start, m.end)
    print(f"move lines {line_of(src_text, s)}-{b.end_line} of {a.file} "
          f"to {a.to} before line {line_of(dst_text, end_kw)} (module {a.module})")
    if not a.apply:
        sys.stdout.write(chunk)
        return 0
    new_src = src_text[:s] + src_text[e:]
    new_dst = dst_text[:end_kw] + chunk + "\n" + dst_text[end_kw:]
    open(a.file, "w", encoding="utf-8").write(new_src)
    open(a.to, "w", encoding="utf-8").write(new_dst)
    print("applied")
    return 0


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("list"); p.add_argument("file"); p.set_defaults(fn=cmd_list)
    p = sub.add_parser("show"); p.add_argument("file"); p.add_argument("name"); p.set_defaults(fn=cmd_show)
    p = sub.add_parser("enclosing"); p.add_argument("file"); p.add_argument("line", type=int); p.set_defaults(fn=cmd_enclosing)
    p = sub.add_parser("check"); p.add_argument("files", nargs="+"); p.set_defaults(fn=cmd_check)
    p = sub.add_parser("rename")
    p.add_argument("file"); p.add_argument("--in", dest="in_block", required=True)
    p.add_argument("old"); p.add_argument("new"); p.add_argument("--apply", action="store_true")
    p.set_defaults(fn=cmd_rename)
    p = sub.add_parser("move")
    p.add_argument("file"); p.add_argument("--block", required=True)
    p.add_argument("--to", required=True); p.add_argument("--module", required=True)
    p.add_argument("--apply", action="store_true")
    p.set_defaults(fn=cmd_move)

    a = ap.parse_args(argv)
    return a.fn(a)


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except BrokenPipeError:       # `| head`: the reader is gone, that is fine
        try:
            sys.stdout.close()
        except BrokenPipeError:
            pass
        sys.exit(0)
