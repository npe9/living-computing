#!/usr/bin/env python3
"""Read a 1st Edition Plan 9 `z` (Hobbit) executable.

Everything here is stated by a file in tools/plan9-1e/:

  struct Exec            sys/include/a.out.h  (8 big-endian words)
  Z_MAGIC = _MAGIC(10)   sys/include/a.out.h  (0x197)
  Sym = value,type,name  sys/include/a.out.h  (4+1+20+3 = 28 bytes)
  UTZERO = UZERO+0x1000  sys/src/9/hobbit/mem.h
  load rule              sys/src/9/port/sysproc.c (file attached at
                         UTZERO, entry in [UTZERO+sizeof(Exec), ...))
  shipped binaries       hobbit/bin/           (3 January 1993)

The text layout, settled from `zl`'s own encoder and from Bell Labs'
startup record (`libc.a` member `main9.z`); see docs/plan9_port.md:

* The text section is a sequence of **32-bit words stored little-endian**.
  `zl/asm.c`'s `SPUT` writes each parcel big-endian into a buffer and
  `cflush` reverses every four-byte group while `swizflag` is set, which
  is the byte reversal that turns them into little-endian words (and is
  applied to the text only -- `datblk` writes data without it).
* Within a word the **high half is the earlier parcel**: the model's own
  format ("even-address parcel in bits 31:16") and the linker's pc
  arithmetic agree.  So the parcels in address order are
  `w >> 16, w & 0xffff` for each little-endian word `w`.
* Reading the file instead as two little-endian 16-bit halves in file
  order swaps every adjacent pair.  That misreading is what produced the
  "two-byte hole" in the earlier notes: the `0x0000` seen after the
  first MOV is the second parcel of that MOV (its 32-bit source field,
  the stack offset of R0), not an instruction.

`TEXT _main(SB), 1, $12` grows one instruction the source does not
contain: `zl/pass.c`'s `follow()` inserts `AENTER` (case ATEXT, "if
autosize > 0") and inserts `ACATCH` after each `ACALL` (case ACALL), so
`_main` really begins

    ENTER R-16
    MOV   R0, _clock        (86dc <hi of _clock> <_clock>)
    MOV   argc+0(FP), R4
    MOV   argv+4(FP), R8
    CALL  main
    CATCH R16               (linker-inserted; the CALL stores the address
                             after itself, i.e. this parcel, as the
                             return address)

which is exactly what all five shipped binaries carry.

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
# struct Exec is 32 bytes and is mapped with the file at UTZERO, so the
# text begins at UTZERO + sizeof(Exec) (sysproc.c's entry check).
TEXTBASE = UTZERO + HEADER.size


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


def _words(exe, off, count):
    """`count` 32-bit words at file offset `off`, little-endian."""
    blob = exe["blob"]
    return [int.from_bytes(blob[off + 4 * k:off + 4 * k + 4], "little")
            for k in range(count)]


def parcel_stream(exe):
    """Parcels in address order from the text section.

    Each little-endian 32-bit word supplies its high half (the even
    address) first, then its low half (the odd address).
    """
    t = exe["text"]
    words = _words(exe, exe["text_off"], t // 4)
    out = []
    for w in words:
        out += [w >> 16, w & 0xffff]
    if t & 3:
        # asmb pads the text end to four bytes; a short tail is a malformed
        # file, and a loud complaint here is better than a silent guess.
        raise SystemExit("%s: text size 0x%x is not a multiple of 4"
                         % (exe["path"], t))
    return out


def parcel_at(exe, addr):
    """The parcel at a byte address, honouring the half of the word."""
    base = addr - TEXTBASE
    if base < 0 or base + 2 > exe["text"]:
        raise SystemExit("parcel address 0x%x outside the text" % addr)
    off = exe["text_off"] + (base & ~3)
    w = int.from_bytes(exe["blob"][off:off + 4], "little")
    return (w & 0xffff) if (base & 3) else (w >> 16)


def instruction_length(p):
    return {0: 1, 1: 1, 2: 3, 3: 5}[p >> 14]


def _sx(value, bits):
    sign = 1 << (bits - 1)
    return (value & (sign - 1)) - (value & sign)


PCREL = {0x01: "CALL", 0x03: "JMP", 0x04: "JMPFN", 0x05: "JMPFY",
         0x06: "JMPTN", 0x07: "JMPTY"}


def decode(parcels, base, start, count):
    """Decode `count` instructions starting at address `start`.

    Instructions follow each other parcel by parcel; `zl` pads only after
    a JMP and after a RETURN (asm.c's TPCTO/TDMON cases, `while(pc & AMOD)`),
    so no unconditional alignment is applied here.
    """
    i = (start - base) // 2
    out = []
    for _ in range(count):
        p = parcels[i]
        ln = instruction_length(p)
        fields = [parcels[i + k] for k in range(1, ln)]
        addr = base + 2 * i
        if ln == 1:
            text = "op%02x" % (p >> 10 & 0x1F)
            if (p >> 10 & 0x1F) in PCREL:
                text = "%s %04x" % (PCREL[p >> 10 & 0x1F],
                                    addr + 2 * _sx(p & 0x3FF, 10))
            out.append((addr, p, text))
        else:
            # The 3- and 5-parcel long CALL/JMP forms share prefix 0x80e?
            # and carry a 32-bit displacement relative to the instruction.
            if (p >> 8) & 0x3F == 0x00 and ln == 3 and (p & 0xF) == 0x1:
                disp = _sx((fields[0] << 16) | fields[1], 32)
                text = "CALL %04x" % (addr + disp)
            elif (p >> 8) & 0x3F == 0x00 and ln == 3 and (p & 0xF) == 0x3:
                disp = _sx((fields[0] << 16) | fields[1], 32)
                text = "JMP %04x" % (addr + disp)
            else:
                text = "op%02x sm%x dm%x" % (p >> 8 & 0x3F,
                                            (p >> 4) & 0xF, p & 0xF)
            out.append((addr, p, text, ["0x%04x" % f for f in fields]))
        i += ln
    return out


def to_model_image(exe):
    """Words for the model's memory, keyed by byte address.

    The model's word is the machine's 32-bit word, so the little-endian
    text word is used as stored.  Data is stored the same way (`nuxiinit`
    reports the target as little-endian: `inuxi = 0 01 0123`), and it
    starts at the program's own `bdata`, not at a fixed offset.
    """
    syms = symbols(exe)
    if "bdata" not in syms:
        raise SystemExit("%s: no `bdata` symbol; the data base is unknown"
                         % exe["path"])
    words = {}
    n = exe["text"] // 4
    for k, w in enumerate(_words(exe, exe["text_off"], n)):
        words[TEXTBASE + 4 * k] = w
    dstart = syms["bdata"][0]
    dn = exe["data"] // 4
    for k, w in enumerate(_words(exe, exe["data_off"], dn)):
        words[dstart + 4 * k] = w
    return words


def check_main(exe, syms, parcels):
    """`_main` must be ENTER + MOV to _clock, as main9.s says.

    The ENTER is not in the source: zl inserts it for TEXT's frame size.
    The MOV's destination field must be the symbol table's `_clock`.
    """
    if "_main" not in syms or "_clock" not in syms:
        return ["symbol table has no `_main`/`_clock`"]
    entry = exe["entry"]
    # The two readers must agree: `parcel_stream` is what the image and the
    # listing use, `parcel_at` reads a single address from the words.  A
    # swapped half-order in either one shows up here first.
    got = [parcels[(entry - TEXTBASE) // 2 + k] for k in range(4)]
    want = [parcel_at(exe, entry + 2 * k) for k in range(4)]
    if got != want:
        return ["parcel_stream and parcel_at disagree at `_main`: %s != %s"
                % (["%04x" % x for x in got], ["%04x" % x for x in want])]
    p0 = parcel_at(exe, entry)
    if (p0 >> 10 & 0x1F) != 0x02 or (p0 & 3) != 0x00:
        return ["`_main` does not begin with ENTER: parcel 0x%04x" % p0]
    off = (p0 >> 2 & 0xFF) - 0x100
    if off * 16 >= 0:
        return ["`_main`'s ENTER is not negative: %d" % (off * 16)]
    p1 = parcel_at(exe, entry + 2)
    if (p1 >> 14) != 2 or (p1 >> 8 & 0x3F) != 0x06:
        return ["`_main`'s second instruction is not a 3-parcel MOV: 0x%04x"
                % p1]
    if (p1 >> 4) & 0xF != 0xD or (p1 & 0xF) != 0xC:
        return ["`_main`'s MOV is not Roffset -> absolute: 0x%04x" % p1]
    if parcel_at(exe, entry + 6) != syms["_clock"][0] & 0xFFFF:
        return ["`_main`'s MOV destination is not _clock: 0x%04x != 0x%04x"
                % (parcel_at(exe, entry + 6), syms["_clock"][0] & 0xFFFF)]
    return []


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("binary")
    ap.add_argument("--image", metavar="PATH",
                    help="write the model image (one 32-bit word per line)")
    ap.add_argument("--entry-bsv", metavar="PATH",
                    help="write a package P9Entry with the entry, text base "
                         "and prefetch-window base")
    ap.add_argument("--decode", type=int, default=8,
                    help="instructions to decode at the entry (default 8)")
    args = ap.parse_args(argv)

    exe = read(args.binary)
    syms = symbols(exe)
    print("%s: magic 0x%x (%s)" % (args.binary, exe["magic"], MAGIC[exe["magic"]]))
    print("  text 0x%x  data 0x%x  bss 0x%x  syms 0x%x  entry 0x%x" %
          (exe["text"], exe["data"], exe["bss"], exe["syms"], exe["entry"]))
    for name in ("main", "_main", "etext", "bdata", "edata", "_clock"):
        if name in syms:
            print("  %-6s 0x%08x (%s)" % (name, syms[name][0], syms[name][1]))
    print("  text base 0x%x (UTZERO + sizeof(Exec))" % TEXTBASE)

    parcels = parcel_stream(exe)
    for item in decode(parcels, TEXTBASE, exe["entry"], args.decode):
        print("  %08x  %04x  %s" % (item[0], item[1],
                                    " ".join(map(str, item[2:]))))

    # Invariants that follow from the header and the symbol table alone.
    problems = []
    if "etext" in syms and syms["etext"][0] != TEXTBASE + exe["text"]:
        problems.append("etext != text base + text size")
    if not TEXTBASE <= exe["entry"] < TEXTBASE + exe["text"]:
        problems.append("entry outside the text")
    if "_main" in syms and syms["_main"][0] != exe["entry"]:
        problems.append("entry != _main")
    if "bdata" in syms and "etext" in syms:
        if syms["bdata"][0] < syms["etext"][0]:
            problems.append("bdata is inside the text")
        if "edata" in syms and syms["edata"][0] < syms["bdata"][0] + exe["data"]:
            problems.append("edata < bdata + data size")
    problems += check_main(exe, syms, parcels)
    if problems:
        print("  CHECK FAILED: " + "; ".join(problems), file=sys.stderr)
        return 1
    print("  check: etext = 0x%04x + text, entry = _main = 0x%04x, "
          "bdata/edata = 0x%04x/0x%04x"
          % (TEXTBASE, exe["entry"], syms["bdata"][0], syms["edata"][0]))
    print("  check: `_main` = ENTER R-16, MOV R0,_clock(0x%04x), "
          "MOV argc,R4, MOV argv,R8, CALL" % syms["_clock"][0])

    if args.entry_bsv:
        # The boot fill is 1 Kbyte (mkHobbitPrefetch: 128 lines x 8 bytes,
        # one way) and there is no on-demand fill, so the window must hold
        # the entry.  Round down to 1 Kbyte: for `cat` that also holds
        # `main` at 0x1020.
        fillbase = exe["entry"] & ~0x3FF
        with open(args.entry_bsv, "w") as f:
            f.write("// Generated by tools/p9exec.py --entry-bsv; do not edit.\n")
            f.write("package P9Entry;\nimport HobbitTypes::*;\n")
            f.write("function Word p9entry(); return 32'h%08x; endfunction\n"
                    % exe["entry"])
            f.write("function Word p9textbase(); return 32'h%08x; endfunction\n"
                    % TEXTBASE)
            f.write("function Word p9fillbase(); return 32'h%08x; endfunction\n"
                    % fillbase)
            f.write("endpackage\n")
        print("  wrote %s: entry 0x%08x, text base 0x%08x, fill base 0x%08x"
              % (args.entry_bsv, exe["entry"], TEXTBASE, fillbase))

    if args.image:
        words = to_model_image(exe)
        lo, hi = 0, max(words)      # the loader maps the image from 0
        with open(args.image, "w") as f:
            for a in range(lo, hi + 1, 4):
                f.write("%08x\n" % words.get(a, 0))
        print("  wrote %s: 0x%x words, 0x%x..0x%x, entry 0x%x" %
              (args.image, (hi - lo) // 4 + 1, lo, hi, exe["entry"]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
