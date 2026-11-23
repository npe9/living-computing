#!/usr/bin/env python3
"""Compare a linked 1e Hobbit kernel image with the shipped `s9term`.

    python3 tools/p9kcmp.py 9term [--ref tools/plan9-1e/hobbit/s9term]

`s9term` was linked on 1992-11-07 from sources older than the ones the
release ships (docs/s9term.md, "Not the shipped sources"), so a kernel
linked from the vendored tree cannot be byte-identical to it.  This tool
separates what MUST agree -- what the format, the mkfile's link line, the
`term` configuration and the generated files fix -- from what may differ
because the sources drifted, and prints the second kind as a diff with
the reason.  It exits non-zero only when a MUST item disagrees.

MUST agree (each line prints `same` or `DIFFERENT`):

  format     both images pass `p9exec.check_kernel` (asm.c case 1 header,
             file size, section bases, etext/bdata/edata/end, every
             symbol inside its section)
  header     the header words asm.c writes as constants (0, 1, 4, 5,
             13, 15-19), the text base and the entry (-T, -E)
  entry      the entry is `_startup` and its first four instructions
             (raml.s: FLUSHP; FLUSHI; the CPU escape and its MOV $..., %CONFIG) decode the same
  objects    the first two objects in text order are raml.s and term.c
             (the link line's first two files)
  libraries  objects come in link-line order: raml.z, term.z, libram.a,
             -lgnot, -lg, -lc (each object is assigned to the first
             archive, from the current one on, that has a member of its
             name)
  kerndate   `kerndate` (mkdevc; -DKERNDATE= on term.c's compile)
  conffile   the string `conffile` points at
  devchar    its characters.  Their width is reported, not compared:
             s9term stores one byte per character, the vendored mkdevc's
             `Rune *devchar=L"..."` compiled by the shipped zc two
             (docs/s9term.md)
  devtab     every function pointer of devtab[] resolved to its name
  streams    the `MOV $xinfo, R4` operands of streaminit, by name
  initcode   initcode[]'s bytes (60: init.h, made on the model)

REPORTED (may differ; why is printed):

  sections   text, data, bss, symbol table and pc/line sizes
  symbols    counts by type
  members    each archive's members in load order, as a diff
  functions  per object, functions only in one image
  bootcode   bootlen and the embedded boot program's Exec header

Objects are recovered from the symbol table's `z` (include history)
records: zl emits a file's history before the first function of each
object, as indices into the `f` file-name components (name[0] = 0, then
big-endian 16-bit indices, ended by 0).  Data-only objects
(bootterm.root.c, defont0.c) carry no history and are not listed.
"""

import argparse
import difflib
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import p9exec  # noqa: E402

REL = HERE / "plan9-1e"
S9TERM = REL / "hobbit" / "s9term"
LIB = REL / "hobbit" / "lib"
FIXED_WORDS = (0, 1, 4, 5, 13, 15, 16, 17, 18, 19)


class Image:
    def __init__(self, path):
        self.path = str(path)
        self.k = p9exec.read_kernel(self.path)
        self.syms = p9exec.kernel_symbols(self.k)
        self.problems = p9exec.check_kernel(self.k, self.syms)
        self.byname = {}
        for v, t, n in self.syms:
            self.byname.setdefault(n, []).append((v, t))
        self.textnames = {}
        for v, t, n in self.syms:
            if t in "Tt":
                self.textnames.setdefault(v, n)

    def sym(self, name, types="DdBbTt"):
        hits = [v for v, t in self.byname.get(name, []) if t in types]
        if len(hits) != 1:
            raise KeyError("%s: %d symbols named %s" % (self.path, len(hits),
                                                        name))
        return hits[0]

    def at(self, va, n):
        k = self.k
        if not k["database"] <= va < k["database"] + k["data"]:
            raise KeyError("0x%08x is not in the data" % va)
        o = k["data_off"] + va - k["database"]
        return k["blob"][o:o + n]

    def word(self, va):
        return int.from_bytes(self.at(va, 4), "little")

    def cstr(self, va):
        out = b""
        while True:
            c = self.at(va + len(out), 1)
            if c in (b"", b"\0"):
                return out
            out += c

    def objects(self):
        """[[path, first function, its address, [function names],
        [their addresses]]] in symbol table order (zl's text order)."""
        fname, out, hist = {}, [], []
        blob = self.k["blob"][self.k["sym_off"]:
                              self.k["sym_off"] + self.k["syms"]]
        recs = [p9exec.SYM.unpack_from(blob, i)
                for i in range(0, len(blob) - p9exec.SYM.size + 1,
                               p9exec.SYM.size)]
        for v, t, name, _pad in recs:
            if chr(t) == "f":
                fname[v] = name.split(b"\0")[0].decode("latin-1")
        for v, t, name, _pad in recs:
            t = chr(t)
            if t == "z":
                idx = [int.from_bytes(name[j:j + 2], "big")
                       for j in range(1, 19, 2)]
                hist.append(idx[:idx.index(0)] if 0 in idx else idx)
            elif t in "Tt":
                n = name.split(b"\0")[0].decode("latin-1")
                if hist:
                    path = "/".join(fname.get(i, "?%d" % i) for i in hist[0])
                    out.append([path, n, v, [], []])
                    hist = []
                if out:
                    out[-1][3].append(n)
                    out[-1][4].append(v)
        return out


def members(path):
    import build_zl_inferno
    return [m for m in build_zl_inferno.read_members(str(path))
            if m != "__.SYMDEF"]


def kernel_member_names():
    import p9kbuild
    return [o + ".z" for o in p9kbuild.kernel_objects("term")]


def assign(objs, archives):
    """Give each object (after raml.s and term.c) the first archive, from
    the current one on, that has a member named after it."""
    out, cur = [], 0
    for path, *_rest in objs:
        base = path.rsplit("/", 1)[-1]
        member = base.rsplit(".", 1)[0] + ".z"
        if base in ("raml.s", "term.c"):
            out.append(base)
            continue
        for i in range(cur, len(archives)):
            if member in archives[i][1]:
                cur = i
                out.append(archives[i][0])
                break
        else:
            out.append("?")
    return out


def stream_infos(img):
    lo = img.sym("streaminit", "T")
    parcels = p9exec.parcel_stream(img.k)
    i = (lo - img.k["textbase"]) // 2
    data = {}
    for v, t, n in img.syms:
        if t in "DdBb":
            data.setdefault(v, n)
    hi = min(v for v in img.textnames if v > lo)    # the next function
    seen = []
    for j in range(i, (hi - img.k["textbase"]) // 2 - 2):
        if parcels[j] == 0xC6FD:        # MOV $imm32, R4 (docs/s9term.md)
            seen.append(data.get((parcels[j + 1] << 16) | parcels[j + 2],
                                 "?"))
    return seen


def chars(raw):
    """A NUL-ended device-character string as (text, bytes per character):
    one byte each (s9term), or 16-bit little-endian runes (`Rune *devchar
    = L"..."` through the shipped zc, u.h: Rune is ushort)."""
    if len(raw) >= 4 and raw[1] == 0 and raw[3] == 0:
        out = b""
        for i in range(0, len(raw) - 1, 2):
            r = raw[i] | raw[i + 1] << 8
            if r == 0:
                break
            if r > 0xFF:
                raise ValueError("rune 0x%04x" % r)
            out += bytes([r])
        return out.decode("latin-1"), 2
    return raw.split(b"\0")[0].decode("latin-1"), 1


def devchar(img):
    p = img.word(img.sym("devchar"))
    k = img.k
    return chars(img.at(p, min(256, k["database"] + k["data"] - p)))


def devtab(img, n):
    base = img.sym("devtab")
    return [img.textnames.get(img.word(base + 4 * i), "?") for i in range(n)]


def entry_insns(img, count=4):
    parcels = p9exec.parcel_stream(img.k)
    items = p9exec.decode(parcels, img.k["textbase"], img.k["entry"], count)
    return ["%04x %s" % (it[1], " ".join(map(str, it[2:]))) for it in items]


def object_sizes(img, objs):
    """[(path, text bytes)]: each function runs to the next text symbol's
    address (etext for the last), and an object is its functions."""
    addrs = sorted({v for v, t, _n in img.syms if t in "Tt"})
    nxt = dict(zip(addrs, addrs[1:] + [img.k["textbase"] + img.k["text"]]))
    return [(o[0], sum(nxt[v] - v for v in set(o[4]))) for o in objs]


def runs(seq):
    r = []
    for s in seq:
        if not r or r[-1] != s:
            r.append(s)
    return r


ERRORS = (KeyError, IndexError, ValueError, StopIteration)


def compare(mine, ref, out=sys.stdout):
    must = []

    def check(what, get, detail):
        """get(img) -> value; detail(value_mine, value_ref) -> text."""
        try:
            a, b = get(mine), get(ref)
        except ERRORS as e:
            must.append((what, False))
            out.write("  %-10s %-9s unreadable: %s\n" % (what, "DIFFERENT",
                                                         e))
            return
        same = a == b
        must.append((what, same))
        try:
            text = detail(a, b)
        except ERRORS:
            text = ""
        if not same:
            text = (text + "; " if text else "") + "this %r, s9term %r" % (
                a, b)
            if len(text) > 400:
                text = text[:400] + "..."
        out.write("  %-10s %-9s %s\n" % (what, "same" if same else
                                          "DIFFERENT", text))

    out.write("p9kcmp: %s vs %s\n" % (mine.path, ref.path))
    out.write("MUST agree:\n")
    check("format", lambda i: i.problems,
          lambda a, b: "p9exec.check_kernel: " + ("; ".join(a + b)
                                                  or "both pass"))
    check("header", lambda i: [i.k["words"][w] for w in FIXED_WORDS]
          + [i.k["entry"], i.k["textbase"]],
          lambda a, b: "fixed words; entry 0x%08x, text base 0x%08x"
          % tuple(a[-2:]))
    check("entry", lambda i: ([n for v, t, n in i.syms
                               if v == i.k["entry"] and t in "Tt"],
                              entry_insns(i)),
          lambda a, b: "%s: %s" % (",".join(a[0]), "; ".join(a[1])))
    mo, ro = mine.objects(), ref.objects()
    objs = {id(mine): mo, id(ref): ro}
    check("objects", lambda i: [o[0] for o in objs[id(i)][:2]],
          lambda a, b: " then ".join(a))
    archives = [("libram.a", set(kernel_member_names())),
                ("-lgnot", set(members(LIB / "libgnot.a"))),
                ("-lg", set(members(LIB / "libg.a"))),
                ("-lc", set(members(LIB / "libc.a")))]
    ma, ra = assign(mo, archives), assign(ro, archives)
    origin = {id(mine): ma, id(ref): ra}
    check("libraries", lambda i: runs(origin[id(i)]),
          lambda a, b: " ".join(a))
    check("kerndate", lambda i: i.word(i.sym("kerndate")),
          lambda a, b: "%d" % a)
    check("conffile", lambda i: i.cstr(i.word(i.sym("conffile"))),
          lambda a, b: repr(a.decode("latin-1")))
    widths = {}

    def dc(i):
        text, widths[id(i)] = devchar(i)
        return text
    check("devchar", dc, lambda a, b: "%r (%d byte(s) per character; "
          "s9term %d)" % (a, widths.get(id(mine)), widths.get(id(ref))))
    ndev = {}
    try:
        ndev["n"] = 13 * len(devchar(ref)[0])
    except ERRORS:
        ndev["n"] = 0
    check("devtab", lambda i: devtab(i, ndev["n"]),
          lambda a, b: "%d entries of 13 functions, by name" % (len(a) // 13))
    check("streams", stream_infos, lambda a, b: " ".join(a))
    check("initcode", lambda i: i.at(i.sym("initcode"), 60),
          lambda a, b: "60 bytes")

    out.write("REPORTED (may differ: the sources drifted, docs/s9term.md):\n")
    try:
        report(mine, ref, mo, ro, ma, ra, out)
    except ERRORS as e:
        out.write("  (report stopped: %s)\n" % e)
    bad = [w for w, s in must if not s]
    out.write("p9kcmp: %s\n" % ("every MUST item agrees" if not bad else
                                "MUST items differ: " + ", ".join(bad)))
    return 0 if not bad else 1


def report(mine, ref, mo, ro, ma, ra, out):
    rows = [("text", "text"), ("data", "data"), ("bss", "bss"),
            ("symbols", "syms"), ("pc/line", "lcsize")]
    for label, key in rows:
        a, b = mine.k[key], ref.k[key]
        out.write("  %-10s %8d  s9term %8d  %+d\n" % (label, a, b, a - b))
    out.write("  %-10s %8d  s9term %8d  %+d\n" % (
        "file", len(mine.k["blob"]), len(ref.k["blob"]),
        len(mine.k["blob"]) - len(ref.k["blob"])))

    def bytype(img):
        c = {}
        for _v, t, _n in img.syms:
            c[t] = c.get(t, 0) + 1
        return c
    mc, rc = bytype(mine), bytype(ref)
    out.write("  symbols by type (this/s9term): " + "  ".join(
        "%s %d/%d" % (t, mc.get(t, 0), rc.get(t, 0))
        for t in sorted(set(mc) | set(rc))) + "\n")
    out.write("  objects with text: %d (s9term %d)\n" % (len(mo), len(ro)))
    for arch in ("libram.a", "-lgnot", "-lg", "-lc", "?"):
        a = [o[0].rsplit("/", 1)[-1] for o, x in zip(mo, ma) if x == arch]
        b = [o[0].rsplit("/", 1)[-1] for o, x in zip(ro, ra) if x == arch]
        if a == b:
            if a:
                out.write("  members %-9s same %d, same order\n"
                          % (arch, len(a)))
            continue
        out.write("  members %-9s %d (s9term %d):" % (arch, len(a), len(b)))
        for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(
                None, b, a, autojunk=False).get_opcodes():
            if tag != "equal":
                out.write(" [%s s9term:%s this:%s]" % (
                    tag, ",".join(b[i1:i2]) or "-",
                    ",".join(a[j1:j2]) or "-"))
        out.write("\n")
    # text by object: where the text-size difference comes from
    ms, rs = dict(object_sizes(mine, mo)), dict(object_sizes(ref, ro))
    deltas = []
    for path in [o[0] for o in mo] + [o[0] for o in ro if o[0] not in ms]:
        d = ms.get(path, 0) - rs.get(path, 0)
        if d:
            deltas.append((path, ms.get(path), rs.get(path), d))
    out.write("  text by object: %d objects differ in size, sum %+d "
              "(text %+d)\n" % (len(deltas), sum(d[3] for d in deltas),
                                 mine.k["text"] - ref.k["text"]))
    rf = {o[0]: set(o[3]) for o in ro}
    mf = {o[0]: set(o[3]) for o in mo}
    for path, a, b, d in deltas:
        extra = ""
        if path in rf and path in mf:
            om, orf = sorted(mf[path] - rf[path]), sorted(rf[path] - mf[path])
            if om or orf:
                extra = "  functions: this only %s; s9term only %s" % (
                    ",".join(om) or "-", ",".join(orf) or "-")
        out.write("    %-28s %7s %7s %+6d%s\n" % (
            path, a if a is not None else "-", b if b is not None else "-",
            d, extra))
    for img, label in ((mine, "this"), (ref, "s9term")):
        n = img.word(img.sym("bootlen"))
        h = [int.from_bytes(img.at(img.sym("bootcode") + 4 * i, 4), "big")
             for i in range(8)]
        out.write("  bootcode %-7s bootlen %d; Exec magic %#x text %#x "
                  "data %#x bss %#x syms %d entry %#x\n"
                  % (label, n, h[0], h[1], h[2], h[3], h[4], h[5]))


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("image")
    ap.add_argument("--ref", default=str(S9TERM))
    a = ap.parse_args(argv)
    return compare(Image(a.image), Image(a.ref))


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
