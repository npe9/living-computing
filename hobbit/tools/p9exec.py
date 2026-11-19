#!/usr/bin/env python3
"""Read a 1st Edition Plan 9 `z` (Hobbit) executable.

Everything here is stated by a file in tools/plan9-1e/:

  struct Exec            sys/include/a.out.h  (8 big-endian words)
  Z_MAGIC = _MAGIC(10)   sys/include/a.out.h  (0x197)
  Sym = value,type,name  sys/include/a.out.h  (4+1+20+3 = 28 bytes)
  UTZERO = UZERO+0x1000  sys/src/9/hobbit/mem.h
  shipped binaries       hobbit/bin/           (3 January 1993)

Two facts about the text were established from the shipped `echo` and
are checked here rather than assumed:

**The text layout is not settled yet, and this tool does not pretend
otherwise.** Two candidate layouts are tested instead:

  A  code at file offset 32, parcels little-endian 16-bit halves
  B  code at file offset 64, parcels little-endian 16-bit halves

Under A, `_main` (0x2ad0) begins with parcel 0x86dc: a 3-parcel MOV
(opcode 0x06, the AMOV genop in zl/optab.c) whose destination field is
0x4008, the symbol-table address of `_clock` -- exactly main9.s's first
instruction, `MOV R0, _clock(SB)`.  Under A, `main` (0x1020) begins with
an invalid 0xffff parcel.  Under B it is the other way round.  The
etext arithmetic (0x3278 = 0x1020 + 0x2258) says the text is based at
0x1020, which neither layout alone explains.  The linker's own decoder
(`libmach/z.c`) and the kernel's exec path are the arbiters; until one
of them is read, this is a lead, not a rule.

The model's image format is big-endian parcels (even parcel in bits
31:16), so the conversion here is the inverse of the file's order.

    python3 tools/p9exec.py hobbit/tools/plan9-1e/hobbit/bin/echo
    python3 tools/p9exec.py --image echo.hex <binary>
"""

import argparse
import struct
import sys

MAGIC = {0x197: "z (Hobbit)"}
HEADER = struct.Struct(">8I")
SYM = struct.Struct(">IB20s3s")
UTZERO = 0x1000


def read(path):
    data = open(path, "rb").read()
    if len(data) < HEADER.size:
        raise SystemExit("%s: shorter than an Exec header" % path)
    magic, text, data_sz, bss, syms, entry, spsz, pcsz = HEADER.unpack_from(data)
    if magic not in MAGIC:
        raise SystemExit("%s: magic 0x%x is not Z_MAGIC" % (path, magic))
    text_off = HEADER.size
    data_off = text_off + text
    sym_off = data_off + data_sz
    return {
        "path": path,
        "blob": data,
        "magic": magic,
        "text": text,
        "data": data_sz,
        "bss": bss,
        "syms": syms,
        "entry": entry,
        "text_off": text_off,
        "data_off": data_off,
        "sym_off": sym_off,
    }


def symbols(exe):
    blob = exe["blob"][exe["sym_off"]:exe["sym_off"] + exe["syms"]]
    out = {}
    for i in range(0, len(blob) - SYM.size + 1, SYM.size):
        value, typ, name, _pad = SYM.unpack_from(blob, i)
        out[name.split(b"\0")[0].decode("latin-1")] = (value, chr(typ))
    return out


def parcel_stream(exe):
    """Parcels as stored in the text section, in address order.

    The file holds each parcel low byte first; this returns the value of
    each parcel as the machine sees it (16-bit little-endian halves).
    """
    t = exe["blob"][exe["text_off"]:exe["text_off"] + exe["text"]]
    return [t[i] | (t[i + 1] << 8) for i in range(0, len(t) - 1, 2)]


def instruction_length(p):
    return {0: 1, 1: 1, 2: 3, 3: 5}[p >> 14]


def decode(parcels, base, start, count):
    """Decode `count` instructions, honouring the 4-byte padding."""
    i = (start - base) // 2
    out = []
    for _ in range(count):
        p = parcels[i]
        ln = instruction_length(p)
        fields = [parcels[i + k] for k in range(1, ln)]
        if ln == 1:
            out.append((base + 2 * i, p, "op%02x" % (p >> 10 & 0x1F)))
        else:
            out.append((base + 2 * i, p,
                        "op%02x" % ((p >> 8) & 0x3F),
                        "sm%x" % ((p >> 4) & 0xF), "dm%x" % (p & 0xF),
                        ["0x%04x" % f for f in fields]))
        i += ln
        if i & 1:
            i += 1
    return out


def to_model_image(exe):
    """Big-endian-parcel words, one per line, as `asm/hobbit_asm.py` reads."""
    parcels = parcel_stream(exe)
    if len(parcels) & 1:
        parcels.append(0)
    seen = []          # (address, parcels) in execution order from the entry
    i = (exe["entry"] - (UTZERO + 0x20)) // 2
    words = {}
    # The whole text section maps: address = UTZERO + 0x20 + 2*i.
    for k in range(0, len(parcels), 2):
        address = UTZERO + 0x20 + 2 * k
        words[address] = (parcels[k] << 16) | parcels[k + 1]
    # Data follows the text in the same image, at its own base.
    dstart = UTZERO + 0x3000
    blob = exe["blob"][exe["data_off"]:exe["data_off"] + exe["data"]]
    for k in range(0, len(blob) - 3, 4):
        words[dstart + k] = int.from_bytes(blob[k:k + 4], "big")
    return words, i


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("binary")
    ap.add_argument("--image", metavar="PATH",
                    help="write the model image (one 32-bit word per line)")
    ap.add_argument("--entry-bsv", metavar="PATH",
                    help="write a package P9Entry with the entry and text base")
    ap.add_argument("--decode", type=int, default=6,
                    help="instructions to decode at the entry (default 6)")
    args = ap.parse_args(argv)

    exe = read(args.binary)
    syms = symbols(exe)
    print("%s: magic 0x%x (%s)" % (args.binary, exe["magic"], MAGIC[exe["magic"]]))
    print("  text 0x%x  data 0x%x  bss 0x%x  syms 0x%x  entry 0x%x" %
          (exe["text"], exe["data"], exe["bss"], exe["syms"], exe["entry"]))
    for name in ("main", "_main", "etext", "bdata", "edata"):
        if name in syms:
            print("  %-6s 0x%08x (%s)" % (name, syms[name][0], syms[name][1]))
    base = syms.get("main", (UTZERO + 0x20, "T"))[0]
    print("  text base 0x%x (from symbol `main`)" % base)

    parcels = parcel_stream(exe)
    for addr, p, *rest in decode(parcels, base, exe["entry"], args.decode):
        print("  %08x  %04x  %s" % (addr, p, " ".join(map(str, rest))))

    # The layout settled from `cat` against main9p.s (see the docstring):
    # text at 0x1020 (file offset 32 under the kernel's mapping), parcels
    # little-endian 16-bit halves, instructions aligned to 4 bytes.
    code = exe["blob"][exe["text_off"]:exe["text_off"] + exe["text"]]
    parcels = [code[i] | (code[i + 1] << 8)
               for i in range(0, len(code) - 1, 2)]
    if "_main" in syms:
        first = decode(parcels, base, syms["_main"][0], 1)[0]
        p0 = first[1]
        fields = first[5] if len(first) > 5 else []
        clock = syms.get("_clock")
        ok = ((p0 >> 8) & 0x3F == 0x06 and len(fields) == 2 and
              (clock is None or fields[1] == "0x%04x" % clock[0]))
        if not ok:
            print("  CHECK FAILED: `_main` does not begin with MOV ...,_clock",
                  file=sys.stderr)
            return 1
        print("  check: `_main` begins with MOV ...,0x%04x (_clock), "
              "as main9.s/main9p.s say" % clock[0])

    # Invariants that follow from the header and the symbol table alone.
    problems = []
    if "main" in syms and "etext" in syms:
        if syms["etext"][0] != syms["main"][0] + exe["text"]:
            problems.append("etext != main + text size")
    if "_main" in syms and syms["_main"][0] != exe["entry"]:
        problems.append("entry != _main")
    if "bdata" in syms and "etext" in syms:
        if syms["bdata"][0] < syms["etext"][0]:
            problems.append("bdata is inside the text")
        if "edata" in syms and syms["edata"][0] != syms["bdata"][0] + exe["data"]:
            problems.append("edata != bdata + data size")
    if problems:
        print("  CHECK FAILED: " + "; ".join(problems), file=sys.stderr)
        return 1
    print("  check: etext = main + text, entry = _main, "
          "bdata/edata = 0x%04x/0x%04x" % (syms["bdata"][0], syms["edata"][0]))

    if args.entry_bsv:
        with open(args.entry_bsv, "w") as f:
            f.write("// Generated by tools/p9exec.py --entry-bsv; do not edit.\n")
            f.write("package P9Entry;\nimport HobbitTypes::*;\n")
            f.write("function Word p9entry(); return 32'h%08x; endfunction\n"
                    % exe["entry"])
            f.write("function Word p9textbase(); return 32'h%08x; endfunction\n"
                    % base)
            f.write("endpackage\n")
        print("  wrote %s: entry 0x%08x, text base 0x%08x"
              % (args.entry_bsv, exe["entry"], base))

    if args.image:
        words, entry_parcel = to_model_image(exe)
        lo, hi = 0, max(words)      # the loader maps the image from 0
        with open(args.image, "w") as f:
            for a in range(lo, hi + 1, 4):
                f.write("%08x\n" % words.get(a, 0))
        print("  wrote %s: 0x%x words, 0x%x..0x%x, entry parcel index 0x%x" %
              (args.image, (hi - lo) // 4 + 1, lo, hi, entry_parcel))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
