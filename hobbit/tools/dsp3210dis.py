#!/usr/bin/env python3
"""Disassemble AT&T WE DSP3210 code (the Hobbit BeBox's three DSPs).

Written from the *WE DSP3210 Digital Signal Processor Information Manual*,
AT&T Microelectronics, September 1991 (docs/dsp3210/MANIFEST.md; "p." is
the printed page, the scan's PDF page is given where it helps):

  - Table 10-1, Instruction Encodings, pp. 10-1..10-2 (PDF 229-230):
    the formats, selected by bits 31-21;
  - Table 10-2, CA field encodings, pp. 10-3..10-4 (PDF 231-232): W
    (size), F (ALU function), T (direction), the 5-bit CAU register code,
    R (I/O register), C (condition);
  - Table 10-3, DA field encodings, p. 10-5 (PDF 233): G, M, N, S/F and
    the 7-bit X/Y/Z operand (p:4 pointer, i:3 increment);
  - the per-instruction formats and encoded examples of section 4.6,
    pp. 4-20..4-84 (PDF 68-132), which settle what the tables leave open:
    nop is 0x80000000 (if (false) goto r0, p. 4-62); return (rM) is goto
    rM with C = true (p. 4-65); ireturn is goto pcsh (p. 4-58); rS2 codes
    10110/10111 in format 6a/6b mean the constant -1/+1 (INCR/DECR,
    p. 4-55); waiti is spc = (long) r0 (Table 4-6, p. 4-6).

Words are big-endian (the Be modules are COFF files whose headers and
code are big-endian; DSP3210 bus byte order is set by the B/LN pin).  The
pc read by an instruction is its own address + 8 (macros.h AddressPR,
"pc + LAB - (.+8)"), so pc-relative targets are shown as addr + 8 + N.

The Be modules under /system/vcos/ are COFF-like files: a 20-byte file
header (a 16-bit word that differs per file -- not a fixed magic, perhaps
a checksum -- then nscns, time, symptr, nsyms, opthdr = 1, flags =
0x0200; in stripped modules the symptr field holds 0x382b and nsyms a
small count, so the symbol table is used only when it fits in the file),
the 1-byte optional header (zero), then 40-byte section
headers (name[8], paddr, vaddr, size, scnptr, relptr, lnnoptr, nreloc:2,
nlnno:2, flags), standard 18-byte symbols and a string table.  Each VCOS
section starts with an 0x20-byte section header of its own (macros.h
NewSection) and the module with a 0x38-byte module header (NewModule).

The files are untrusted data: run this with `python3 -I`.

  python3 -I tools/dsp3210dis.py MODULE                # all code sections
  python3 -I tools/dsp3210dis.py MODULE --headers
  python3 -I tools/dsp3210dis.py --word 0x80000000     # one word
"""
import struct
import sys

# 5-bit CAU register code, Table 10-2 p. 10-3.  -1/+1 are the "-n"/"+n"
# codes: constants in ALU forms, post-decrement/increment as rI.
CAU = (["r0"] + ["r%d" % i for i in range(1, 15)] + ["pc", "?16"]
       + ["r%d" % i for i in range(15, 20)] + ["-1", "+1"]
       + ["r20", "r21", "r22", "?27", "?28", "?29", "pcsh", "?31"])
CAU_VALID = {i for i, n in enumerate(CAU) if not n.startswith("?")}

# I/O registers, CA - R field, Table 10-2 p. 10-3.
IOR = {0b00000: "ps", 0b01000: "emr", 0b01010: "spc", 0b01100: "pcw",
       0b01110: "dauc", 0b01111: "ctr"}

# Conditions, C field, p. 10-4.
COND = ["false", "true", "pl", "mi", "ne", "eq", "vc", "vs", "cc", "cs",
        "ge", "lt", "gt", "le", "hi", "ls", "auc", "aus", "age", "alt",
        "ane", "aeq", "avc", "avs", "agt", "ale"] + [None] * 6 + [
        "ibe", "ibf", "obf", "obe", None, None, None, None,
        "syc", "sys", "fbc", "fbs", "ir0c", "ir0s", "ir1c", "ir1s"] + [None] * 16

# W field (size), p. 10-3: load names; stores use byte/hbyte/short/long.
W_LOAD = {0: "byte", 1: "char", 2: "ushort", 3: "short", 4: "hbyte", 7: "long"}
W_STORE = {0: "byte", 1: "byte", 2: "short", 3: "short", 4: "hbyte", 7: "long"}

# F field (ALU / barrel-shifter function), p. 10-3.
F_OP = {0: "+", 1: "<<", 2: "N-", 3: "#", 4: "-", 6: "&~", 7: "cmp", 8: "^",
        9: ">>>", 10: "|", 11: "<<<", 12: ">>", 13: "$>>", 14: "&", 15: "btst"}

# DA G field (special functions), p. 10-5.
G_FN = {0: "ic", 1: "oc", 2: "float16", 3: "int16", 4: "round", 5: "ifalt",
        6: "ifaeq", 7: "ifagt", 8: "float32", 9: "int32", 12: "ieee",
        13: "dsp", 14: "seed"}

DA_M = ["a0", "a1", "a2", "a3", "0.0", "1.0", None, None]
DA_I = ["", "++r15", "++r16", "++r17", "++r18", "++r19", "--", "++"]


def sx16(n):
    return n - 0x10000 if n & 0x8000 else n


def creg(code):
    return CAU[code]


def da_operand(f):
    """A 7-bit X/Y/Z field: p (bits 6-3) pointer r1-r14, i (2-0) the post
    modification; p = 0 selects a0-a3 (i 0-3) or, for Z, no write (i 7)."""
    p, i = f >> 3, f & 7
    if p == 0:
        return ("a%d" % i) if i < 4 else (None if i == 7 else "?acc%d" % i)
    if p == 15:
        return "?p15"
    return "*r%d%s" % (p, DA_I[i])


class Insn:
    __slots__ = ("text", "valid", "kind", "target")

    def __init__(self, text, valid=True, kind="", target=None):
        self.text, self.valid, self.kind, self.target = text, valid, kind, target


def bad(word):
    return Insn(".long 0x%08x  /* reserved encoding */" % word, False)


def _target(rb, n, addr):
    """rB + N; for rB = pc the target is addr + 8 + N."""
    if rb == 15 and addr is not None:
        return "0x%x" % ((addr + 8 + n) & 0xFFFFFFFF), (addr + 8 + n) & 0xFFFFFFFF
    if rb == 0:
        return "0x%x" % (n & 0xFFFFFFFF), n & 0xFFFFFFFF
    base = creg(rb)
    if n == 0:
        return base, None
    return "%s%+d" % (base, n), None


def decode(word, addr=None):
    """Decode one 32-bit instruction word (Table 10-1)."""
    top3 = word >> 29
    # 8a-8c: 101 / 110 / 111, Ne (28-21) : N (15-0) = 24-bit M.
    if top3 >= 5:
        m = (((word >> 21) & 0xFF) << 16) | (word & 0xFFFF)
        r = (word >> 16) & 31
        if r not in CAU_VALID:
            return bad(word)
        if top3 == 5:                                   # 8a goto rB+M
            if r == 0:
                return Insn("goto 0x%06x" % m, kind="goto", target=m)
            return Insn("goto %s+0x%06x" % (creg(r), m), kind="goto")
        if top3 == 6:                                   # 8b rD = M
            return Insn("%s = (ushort24) 0x%06x" % (creg(r), m), kind="set24")
        return Insn("call 0x%06x (%s)" % (m, creg(r)), kind="call", target=m)
    if top3 in (1, 2, 3):
        return decode_da(word)
    # top3 is 000 or 100: E (bit 31) is the size for CA forms.
    e = word >> 31
    op = (word >> 25) & 0x3F       # bits 30-25
    sz = "" if e else "(short) "
    if op >> 2 == 0:               # 0a/0b/1a/1b: bits 30-27 = 0000
        if not e:
            return bad(word)       # 0a/1a reserved
        c = (word >> 21) & 63      # 0b/1b conditional branch
        rb = (word >> 16) & 31
        n = sx16(word & 0xFFFF)
        if COND[c] is None or rb not in CAU_VALID:
            return bad(word)
        if word == 0x80000000:
            return Insn("nop", kind="nop")
        tgt, ta = _target(rb, n, addr)
        if c == 1:
            if rb == 30 and n == 0:
                return Insn("ireturn", kind="ireturn")
            if rb != 15 and rb != 0 and n == 0:
                return Insn("return (%s)" % creg(rb), kind="return")
            return Insn("goto %s" % tgt, kind="goto", target=ta)
        return Insn("if (%s) goto %s" % (COND[c], tgt), kind="branch", target=ta)
    if op >> 1 == 2:               # 2a/2b reserved: bits 30-26 = 00010
        return bad(word)
    if op >> 1 == 3:               # 3a loop counter, 3b/3c do
        if not e:
            rm = (word >> 21) & 31
            rb = (word >> 16) & 31
            if rm not in CAU_VALID or rb not in CAU_VALID:
                return bad(word)
            tgt, ta = _target(rb, sx16(word & 0xFFFF), addr)
            return Insn("if (%s-- >= 0) goto %s" % (creg(rm), tgt),
                        kind="loop", target=ta)
        b = (word >> 24) & 1       # B: dolock (p. 4-31)
        mm = (word >> 23) & 1      # M: doblock (p. 4-31)
        k = (word >> 11) & 0x7F
        if b and mm:
            return bad(word)
        name = "dolock" if b else ("doblock" if mm else "do")
        if (word >> 25) & 1:       # 3c: count in rM
            rm = word & 31
            if rm not in CAU_VALID:
                return bad(word)
            cnt = creg(rm)
        else:
            cnt = str(word & 0x7FF)
        if mm:
            return Insn("%s %s  /* K=%d */" % (name, cnt, k), kind="do")
        return Insn("%s %d, %s" % (name, k, cnt), kind="do")
    if op >> 1 == 4:               # 4a call rB+N (rM); 4b shift-and-or
        r1_ = (word >> 21) & 31
        r2_ = (word >> 16) & 31
        n = word & 0xFFFF
        if r1_ not in CAU_VALID or r2_ not in CAU_VALID:
            return bad(word)
        if not e:
            tgt, ta = _target(r2_, sx16(n), addr)
            return Insn("call %s (%s)" % (tgt, creg(r1_)), kind="call", target=ta)
        return Insn("%s = %s <<| 0x%04x" % (creg(r1_), creg(r2_), n), kind="alu")
    if op >> 1 == 5:               # 5a/5b rD = rS3 + N
        rd = (word >> 21) & 31
        rs = (word >> 16) & 31
        n = sx16(word & 0xFFFF)
        if rd not in CAU_VALID or rs not in CAU_VALID:
            return bad(word)
        if rs == 0:
            return Insn("%s = %s%d" % (creg(rd), sz, n), kind="set")
        if rs == 15 and addr is not None:
            return Insn("%s = %spc%+d  /* 0x%x */" % (creg(rd), sz, n,
                        (addr + 8 + n) & 0xFFFFFFFF), kind="alu")
        return Insn("%s = %s%s%+d" % (creg(rd), sz, creg(rs), n), kind="alu")
    if op == 0b001100:             # 6a/6b register ALU, conditional
        f = (word >> 21) & 15
        rd = (word >> 16) & 31
        rs1 = (word >> 11) & 31
        c = (word >> 5) & 63
        rs2 = word & 31
        if (f not in F_OP or COND[c] is None or rd not in CAU_VALID
                or rs1 not in CAU_VALID or rs2 not in CAU_VALID):
            return bad(word)
        pre = "" if c == 1 else "if (%s) " % COND[c]
        a, b = creg(rs1), creg(rs2)
        fn = F_OP[f]
        if fn == "+" and rs2 in (22, 23):
            expr = "%s %s 1" % (a, "-" if rs2 == 22 else "+")
        elif fn == "+" and rs1 == 0:
            expr = b
        elif rs2 in (22, 23) and fn in ("<<", ">>", "$>>"):
            expr = "%s %s 1" % (a, fn)
        elif fn == "-" and rs1 == 0:
            expr = "-%s" % b
        elif fn == "cmp":
            return Insn("%s%s%s - %s" % (pre, sz, a, b), kind="alu")
        elif fn == "btst":
            return Insn("%s%s%s & %s" % (pre, sz, a, b), kind="alu")
        elif fn == "N-":
            expr = "%s -r %s" % (a, b)
        elif fn in (">>>", "<<<"):
            expr = "%s %s 1" % (a, fn)
        else:
            expr = "%s %s %s" % (a, fn, b)
        return Insn("%s%s = %s%s" % (pre, creg(rd), sz, expr), kind="alu")
    if op == 0b001101:             # 6c/6d immediate ALU: rD = rD F N
        f = (word >> 21) & 15
        rd = (word >> 16) & 31
        n = word & 0xFFFF
        if f not in F_OP or rd not in CAU_VALID:
            return bad(word)
        d = creg(rd)
        fn = F_OP[f]
        if fn == "N-":
            return Insn("%s = %s%d - %s" % (d, sz, sx16(n), d), kind="alu")
        if fn == "cmp":
            return Insn("%s%s - %d" % (sz, d, sx16(n)), kind="alu")
        if fn == "btst":
            return Insn("%s%s & 0x%04x" % (sz, d, n), kind="alu")
        if fn in ("&", "|", "^", "&~"):
            return Insn("%s = %s%s %s 0x%04x" % (d, sz, d, fn, n), kind="alu")
        return Insn("%s = %s%s %s %d" % (d, sz, d, fn, sx16(n)), kind="alu")
    if op in (0b001110, 0b001111):  # 7a-7d moves
        t = (word >> 24) & 1
        w = (word >> 21) & 7
        rh = (word >> 16) & 31
        if not e:                  # 7a: memory direct *L
            if op != 0b001110 or rh not in CAU_VALID or w not in W_LOAD:
                return bad(word)
            mem = "*0x%04x" % (word & 0xFFFF)
            if t:
                return Insn("%s = (%s) %s" % (mem, W_STORE[w], creg(rh)), kind="store")
            return Insn("%s = (%s) %s" % (creg(rh), W_LOAD[w], mem), kind="load")
        if op == 0b001110 and (word >> 10) & 1:   # 7b: rH <-> iorH
            io = word & 31
            if io not in IOR or rh not in CAU_VALID:
                return bad(word)
            if t:
                if rh == 0 and io == 0b01010:
                    return Insn({7: "waiti", 3: "bkpt", 2: "bkpt", 0: "sftrst",
                                 1: "sftrst"}.get(w, "spc = r0"), kind="special")
                return Insn("%s = (%s) %s" % (IOR[io], W_STORE.get(w, "?"), creg(rh)),
                            kind="ioset")
            return Insn("%s = (%s) %s" % (creg(rh), W_LOAD.get(w, "?"), IOR[io]),
                        kind="ioget")
        if (word >> 10) & 1:
            return bad(word)
        rp = (word >> 11) & 31
        ri = word & 31
        if rp not in CAU_VALID or ri not in CAU_VALID or w not in W_LOAD:
            return bad(word)
        if ri == 0:
            mem = "*%s" % creg(rp)
        elif ri == 22:
            mem = "*%s--" % creg(rp)
        elif ri == 23:
            mem = "*%s++" % creg(rp)
        else:
            mem = "*%s++%s" % (creg(rp), creg(ri))
        if op == 0b001110:         # 7c: rH <-> memory via rP
            if t:
                return Insn("%s = (%s) %s" % (mem, W_STORE[w], creg(rh)), kind="store")
            return Insn("%s = (%s) %s" % (creg(rh), W_LOAD[w], mem), kind="load")
        if rh not in IOR:          # 7d: iorH <-> memory
            return bad(word)
        if t:
            return Insn("%s = (%s) %s" % (mem, W_STORE[w], IOR[rh]), kind="store")
        return Insn("%s = (%s) %s" % (IOR[rh], W_LOAD[w], mem), kind="ioset")
    return bad(word)


def decode_da(word):
    """DA formats 1-5 (Table 10-1 p. 10-2, Table 10-3 p. 10-5, 4.6)."""
    n = "a%d" % ((word >> 21) & 3)
    x = da_operand((word >> 14) & 0x7F)
    y = da_operand((word >> 7) & 0x7F)
    z = da_operand(word & 0x7F)
    if (word >> 27) == 0b01111:                    # format 5: special function
        g = (word >> 23) & 15
        if g not in G_FN or (word >> 14) & 0x7F or y is None:
            return bad(word)
        if "?" in y or (z is not None and ("?" in z or z.startswith("a"))):
            return bad(word)
        out = "" if z is None else "%s = " % z
        return Insn("%s%s = %s(%s)" % (out, n, G_FN[g], y), kind="da")
    fmt = word >> 29
    m = (word >> 26) & 7
    if (word >> 25) & 1:
        return bad(word)
    neg = "-" if (word >> 24) & 1 else ""
    s = "-" if (word >> 23) & 1 else "+"
    if x is None or y is None or "?" in x or "?" in y or (z and "?" in z):
        return bad(word)
    zout = "" if z is None or z.startswith("a") else "%s = " % z
    if z is not None and z.startswith("a"):
        return bad(word)            # Z is a memory operand or "no write"
    if fmt == 1 and m == 6:        # format 4: FADD-TAP
        if z is None:
            return bad(word)
        return Insn("%s = %s(%s = %s) %s %s" % (n, neg, z, y, s, x), kind="da")
    am = DA_M[m]
    if am is None:
        return bad(word)
    if fmt == 1:                   # format 1: aN = [-]Y {+,-} aM*X
        if m == 4:
            return Insn("%s%s = %s%s" % (zout, n, neg, y), kind="da")
        if m == 5:
            return Insn("%s%s = %s%s %s %s" % (zout, n, neg, y, s, x), kind="da")
        return Insn("%s%s = %s%s %s %s * %s" % (zout, n, neg, y, s, am, x), kind="da")
    if fmt == 2:                   # format 2: aN = [-]aM {+,-} (Z=Y)*X
        if z is None:
            return bad(word)
        if m == 4:
            return Insn("%s = %s(%s = %s) * %s" % (n, "-" if s == "-" else "", z, y, x),
                        kind="da")
        return Insn("%s = %s%s %s (%s = %s) * %s" % (n, neg, am, s, z, y, x), kind="da")
    # format 3: [Z=] aN = [-]aM {+,-} Y*X
    if m == 4:
        return Insn("%s%s = %s%s * %s" % (zout, n, "-" if s == "-" else "", y, x), kind="da")
    return Insn("%s%s = %s%s %s %s * %s" % (zout, n, neg, am, s, y, x), kind="da")


# ---------------------------------------------------------------- COFF

class CoffError(Exception):
    pass


class Coff:

    def __init__(self, path):
        with open(path, "rb") as f:
            self.blob = d = f.read()
        if len(d) < 20:
            raise CoffError("%s: too short" % path)
        # 0x6601 (0x0166 read little-endian) marks a little-endian file.
        self.e = e = "<" if d[:2] == b"\x66\x01" else ">"
        (self.magic, nscns, self.time, symptr, nsyms, opthdr,
         self.flags) = struct.unpack(e + "HHIIIHH", d[:20])
        if not 0 < nscns < 256 or opthdr > 64 or 20 + opthdr + 40 * nscns > len(d):
            raise CoffError("%s: not a VCOS module (nscns %d, opthdr %d)"
                            % (path, nscns, opthdr))
        self.sections = []
        off = 20 + opthdr
        for _ in range(nscns):
            name = d[off:off + 8].split(b"\0", 1)[0].decode("latin-1")
            (paddr, vaddr, size, scnptr, relptr, lnptr, nrel, nln,
             flags) = struct.unpack(e + "IIIIIIHHI", d[off + 8:off + 40])
            self.sections.append(dict(name=name, paddr=paddr, size=size,
                                      scnptr=scnptr, relptr=relptr,
                                      nreloc=nrel, flags=flags))
            off += 40
        self.symbols = []
        if symptr + 18 * nsyms > len(d):
            nsyms = 0              # no symbol table: the field holds 0x382b
        strtab = symptr + 18 * nsyms
        i = 0
        while i < nsyms:
            e = d[symptr + 18 * i: symptr + 18 * i + 18]
            if e[:4] == b"\0\0\0\0":
                so = struct.unpack(self.e + "I", e[4:8])[0]
                name = d[strtab + so:].split(b"\0", 1)[0].decode("latin-1")
            else:
                name = e[:8].split(b"\0", 1)[0].decode("latin-1")
            value, scn, typ, sclass, naux = struct.unpack(self.e + "IhHBB", e[8:18])
            self.symbols.append((name, value, scn, sclass))
            i += 1 + naux

    def data(self, sec):
        return self.blob[sec["scnptr"]:sec["scnptr"] + sec["size"]]

    def labels(self, secno):
        out = {}
        for name, value, scn, sclass in self.symbols:
            if scn == secno and sclass in (2, 3, 6) and not name.startswith("."):
                out.setdefault(value, name)
        return out


def disassemble(coff, out=sys.stdout):
    """Every non-__ModH section: the 0x20-byte VCOS section header, then words."""
    stats = {"words": 0, "reserved": 0}
    for idx, sec in enumerate(coff.sections, 1):
        if sec["name"] == "__ModH" or not sec["size"]:
            continue
        data = coff.data(sec)
        labels = coff.labels(idx)
        out.write("\n; section %s  paddr 0x%x size 0x%x\n"
                  % (sec["name"], sec["paddr"], sec["size"]))
        hdr = struct.unpack(coff.e + "8I", data[:32]) if len(data) >= 32 else ()
        if hdr:
            out.write("; VCOS section header: type 0x%x\n" % hdr[1])
        if hdr and hdr[1] != 0x100:
            continue                 # not sPROG: data
        for off in range(32, len(data) - 3, 4):
            a = sec["paddr"] + off
            if a in labels:
                out.write("%s:\n" % labels[a])
            w = struct.unpack(coff.e + "I", data[off:off + 4])[0]
            ins = decode(w, a)
            stats["words"] += 1
            stats["reserved"] += not ins.valid
            out.write("  %06x  %08x  %s\n" % (a, w, ins.text))
    return stats


def main(argv):
    if len(argv) >= 2 and argv[0] == "--word":
        for s in argv[1:]:
            print(decode(int(s, 0), 0).text)
        return 0
    if not argv:
        print(__doc__)
        return 2
    coff = Coff(argv[0])
    if "--headers" in argv:
        print("magic 0x%04x time %d" % (coff.magic, coff.time))
        for s in coff.sections:
            print("%-10s paddr 0x%05x size 0x%05x scnptr 0x%05x nreloc %d flags 0x%x"
                  % (s["name"], s["paddr"], s["size"], s["scnptr"], s["nreloc"],
                     s["flags"]))
        for name, value, scn, sclass in coff.symbols:
            print("  sym %-20s 0x%06x scn %d class %d" % (name, value, scn, sclass))
        return 0
    st = disassemble(coff)
    print("\n; %d words, %d reserved encodings" % (st["words"], st["reserved"]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
