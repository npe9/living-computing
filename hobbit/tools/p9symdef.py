#!/usr/bin/env python3
"""Where every byte of a 1e `__.SYMDEF` comes from (A3).

`rl` (sys/src/cmd/rl.c `writerl`) writes NNAME = 20 bytes of each
symbol's name, and the name is libmach's `Sym.name`, copied whole by
`objlookup()` (`memmove(s->name, name, NNAME)`) out of readar()'s local
`Prog p` (sys/src/libmach/obj.c), whose `id[]` `_readz()`
(sys/src/libmach/zobj.c) fills only up to the name's NUL.  So past the
NUL a table entry holds either

  * a byte an earlier name of the same member wrote into `p.id` in the
    same readar() call ("in-call": a property of the archive), or
  * a byte that was on the stack when readar() was entered ("pre"):
    a property of the machine and the `rl` binary that made the table.

`readrl()` below replays readrl()/readar()/objlookup()/objupdate()/
_readz() (transcribed from those files; libmach is not vendored -- the
release tarball's sys/src/libmach, sha256 in docs/plan9_port.md) over an
archive with `p.id` tracked byte by byte, and says which is which.

The pre bytes of the shipped tables are predicted exactly by the frames
of **/mips/bin/rl** (the release's MIPS binary, read instruction by
instruction; docs/plan9_syscalls.md):

  readrl's SP = S.  readar: `SUB $36` -> p at 12(SP) = S-24; Prog's
  kind, type and sym are one byte each (_readz's `sb` at 0/1/2(p)), so
  id[] = S-21.. .  objtype, called just before it from the same SP:
  `SUB $28`; its outgoing-argument words 8(SP) = S-20 and 12(SP) = S-16
  hold Bseek's last two arguments, -8 and 1, big-endian; buf[8] at
  16(SP) = S-12; `i`, spilled at 24(SP) = S-4 before each indirect
  `obj[i].is` call, big-endian, 3 for a .z member.

  so, at readar's entry:  id[1..4] = ff ff ff f8   (-MAXIS)
                          id[5..8] = 00 00 00 01   (Bseek's type)
                          id[9..16] = the member's first 8 bytes (buf)
                          id[17..19] = 00 00 00    (i's high bytes)

The Hobbit's own rl lays out buf at id[9..16] too (zc's frames happen to
match), but it is little-endian and passes no arguments in a word there,
so on the model id[17] is i's low byte (3) and id[7..8] whatever the
previous member's names left: the 212 bytes `p9kbuild archeck` finds.
"""

import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

NNAME = 20                  # a.out.h
RLENTSIZE = 4 + NNAME + 4   # rl.c
SAR_HDR = 60                # ar.h
NNAMES = 50                 # obj.c
# z.out.h enum as: ANAME, ATEXT, AGLOBL; the D_ address types
AGLOBL, ANAME, ATEXT = 46, 67, 85
D_BRANCH, D_REG, D_EXTERN, D_STATIC, D_AUTO, D_PARAM, D_CONST, D_FCONST, \
    D_SCONST, D_ADDR = range(2, 12)
D_INDIR = 32
TYPE2CHAR = {D_EXTERN: "U", D_STATIC: "b", D_AUTO: "a", D_PARAM: "p"}

#: /mips/bin/rl: the stack under readar()'s p.id[j] when readar is
#: entered, for j in 1..19 (module doc); None where the MIPS frames say
#: nothing (id[0]).
MIPS_PRE = [None] + list(b"\xff\xff\xff\xf8\x00\x00\x00\x01") + [None] * 8 \
    + [0, 0, 0]


class Bio:
    """The archive as Bgetc sees it: the whole file, -1 only at EOF."""

    def __init__(self, data):
        self.data = data
        self.off = 0

    def getc(self):
        if self.off >= len(self.data):
            self.off += 1
            return -1
        c = self.data[self.off]
        self.off += 1
        return c


class Lib:
    """obj.c's statics: sym[], names[], local/global, plus the provenance
    of each id byte ("pre" or an int)."""

    def __init__(self):
        self.sym = []
        self.names = [0] * NNAMES


def _readz(bio, p):
    """zobj.c _readz: fill p (a dict); False at EOF."""
    as_ = bio.getc()
    if as_ < 0:
        return False
    p["kind"] = None
    if as_ == ANAME:
        p["kind"] = "name"
        p["type"] = TYPE2CHAR.get(bio.getc(), "?")
        p["sym"] = bio.getc()
        c = bio.getc()
        i = 0
        while i < NNAME and c > 0:
            p["id"][i] = c
            c = bio.getc()
            i += 1
        if i < NNAME:
            p["id"][i] = c & 0xFF       # char p->id[i] = c (0, or -1)
        return True
    if as_ == ATEXT:
        p["kind"] = "text"
    elif as_ == AGLOBL:
        p["kind"] = "data"
    for _ in range(4):                  # lineno
        bio.getc()
    t, s = _addr(bio, p)
    if t not in (D_STATIC, D_EXTERN):
        p["kind"] = None
    p["sym"] = s
    t, _s = _addr(bio, p)
    if t != D_CONST:
        p["kind"] = None
    return True


def _addr(bio, p):
    t = bio.getc()
    bio.getc()                          # width
    s = bio.getc()
    name = t & ~D_INDIR
    if name in (D_CONST, D_BRANCH, D_ADDR, D_REG, D_EXTERN, D_STATIC):
        for _ in range(4):
            bio.getc()
    elif name in (D_AUTO, D_PARAM):
        off = bio.getc() | bio.getc() << 8 | bio.getc() << 16 | \
            bio.getc() << 24
        if off & 0x80000000:
            off -= 1 << 32
        off = abs(off)
        if s:
            p["offsets"].append((s, off))
    elif name == D_SCONST:
        for _ in range(bio.getc()):
            bio.getc()
    elif name == D_FCONST:
        for _ in range(8):
            bio.getc()
    # a char: Bgetc's 0..255 (or -1) truncated
    return t, s if s < 128 else s - 256


def _name(toks):
    out = bytearray()
    for b in toks:
        if not isinstance(b, int) or b == 0:
            break
        out.append(b)
    return bytes(out[:NNAME])


def _objlookup(lib, ident, toks, typ, local, glob):
    """obj.c objlookup; `toks` is p.id with provenance."""
    sym, names = lib.sym, lib.names
    name = _name(toks)
    if sym:
        s = sym[names[ident]]
        i = local if typ in "ap" else glob
        if names[ident] >= i and _name(s["id"]) == name:
            s["type"] = typ
            return
        for j in range(i, len(sym)):
            s = sym[j]
            if _name(s["id"]) != name:
                continue
            if (s["type"] in "TDU" and typ == "U") or \
                    (s["type"] in "tdb" and typ == "b") or \
                    (s["type"] in "ap" and typ in "ap"):
                names[ident] = j
                return
    names[ident] = len(sym)
    sym.append({"id": list(toks), "type": typ,
                "value": 0x7fffffff if typ in "ap" else 0})


def _readar(lib, bio, end, member):
    """obj.c readar: `while(_readz(bp, &p) && BOFFSET(bp) < end)
    processprog(&p)`; p.id starts as the stack ("pre", j)."""
    p = {"id": [("pre", j) for j in range(NNAME)], "offsets": []}
    local = glob = len(lib.sym)
    while _readz(bio, p) and bio.off < end:
        for s, off in p["offsets"]:     # zobj.c addr(): _offset()
            ss = lib.sym[lib.names[s]]
            if _name(ss["id"]) and ss["type"] in "ap" and ss["value"] > off:
                ss["value"] = off
        p["offsets"] = []
        if p["kind"] is None:
            continue
        if not 0 <= p["sym"] < NNAMES:
            raise SystemExit("p9symdef: %s: symbol index %d" % (member,
                                                                 p["sym"]))
        if p["kind"] == "name":
            _objlookup(lib, p["sym"], p["id"], p["type"], local, glob)
        else:
            s = lib.sym[lib.names[p["sym"]]]
            ty = "T" if p["kind"] == "text" else "D"
            if _name(s["id"]):
                if s["type"] == "U":
                    s["type"] = ty
                elif s["type"] in ("b", ty.lower()):
                    s["type"] = ty.lower()


def readrl(data):
    """rl.c readrl over an archive's bytes.  Returns the table rl would
    write, [(name, id tokens, member, member's first 8 bytes)] for the
    'T' and 'D' symbols in order; a token is an int or ("pre", j)."""
    bio = Bio(data)
    lib = Lib()
    owner = []
    offset = 8                          # SARMAG
    while True:
        if offset & 1:
            offset += 1
        hdr = data[offset:offset + SAR_HDR]
        if len(hdr) < SAR_HDR:
            break
        name = hdr[0:16].decode("latin-1").split(" ")[0]
        size = int(hdr[48:58].decode().strip())
        size += size & 1
        start = offset + SAR_HDR
        if name != "__.SYMDEF":
            n0 = len(lib.sym)
            bio.off = start
            _readar(lib, bio, start + size, name)
            owner += [(name, data[start:start + 8])] * (len(lib.sym) - n0)
        offset = start + size
    return [(_name(s["id"]), s["id"]) + owner[k]
            for k, s in enumerate(lib.sym) if s["type"] in "TD"]


def symdef_body(data):
    """The shipped __.SYMDEF member's bytes (it is first)."""
    hdr = data[8:8 + SAR_HDR]
    if not hdr.startswith(b"__.SYMDEF"):
        raise SystemExit("p9symdef: no __.SYMDEF first")
    size = int(hdr[48:58].decode().strip())
    return data[8 + SAR_HDR:8 + SAR_HDR + size]


def explain(data, table=None):
    """Account for every byte past a name's NUL in `table` (a __.SYMDEF
    body; default the archive's own).  Returns a dict of counts and the
    list of bytes nothing explains."""
    entries = readrl(data)
    body = symdef_body(data) if table is None else table
    if len(body) != RLENTSIZE * len(entries):
        raise SystemExit("p9symdef: %d table entries, readrl makes %d"
                         % (len(body) // RLENTSIZE, len(entries)))
    c = {"entries": len(entries), "in_call": 0, "in_call_same": 0,
         "pre": 0, "pre_mips": 0, "pre_unknown": 0}
    odd = []
    for k, (name, toks, member, head) in enumerate(entries):
        got = body[RLENTSIZE * k + 4:RLENTSIZE * k + 4 + NNAME]
        if got.split(b"\0")[0] != name:
            raise SystemExit("p9symdef: entry %d is %r, readrl says %r"
                             % (k, got, name))
        mips = list(MIPS_PRE)
        mips[9:17] = head
        for j in range(len(name) + 1, NNAME):
            t = toks[j]
            if isinstance(t, int):
                c["in_call"] += 1
                if t == got[j]:
                    c["in_call_same"] += 1
                else:
                    odd.append((name, member, j, "in-call %02x" % t, got[j]))
            else:
                c["pre"] += 1
                if mips[j] is None:
                    c["pre_unknown"] += 1
                elif mips[j] == got[j]:
                    c["pre_mips"] += 1
                else:
                    odd.append((name, member, j, "MIPS %02x" % mips[j],
                                got[j]))
    return c, odd


def main(argv):
    import argparse
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("archive", nargs="+")
    ap.add_argument("--table", help="explain this archive's __.SYMDEF "
                    "instead (one archive; e.g. p9kbuild archeck's new.a)")
    a = ap.parse_args(argv)
    bad = 0
    for path in a.archive:
        data = pathlib.Path(path).read_bytes()
        table = (symdef_body(pathlib.Path(a.table).read_bytes())
                 if a.table else None)
        c, odd = explain(data, table)
        print("%s: %d entries; past the NULs %d in-call bytes (%d as "
              "replayed), %d pre (%d as /mips/bin/rl's frames predict, %d "
              "not predicted)" % (path, c["entries"], c["in_call"],
                                  c["in_call_same"], c["pre"],
                                  c["pre_mips"], c["pre_unknown"]))
        for o in odd:
            print("  %s (%s) id[%d]: %s, table %02x" % (
                o[0].decode("latin-1"), o[1], o[2], o[3], o[4]))
        bad += len(odd)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
