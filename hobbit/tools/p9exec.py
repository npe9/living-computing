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
    python3 tools/p9exec.py hobbit/tools/plan9-1e/hobbit/s9term

A kernel image (`zl -H1`, the 80-byte COFF-style header of zl/asm.c's
case 1) is recognised by its first word and read by `read_kernel`; the
user-binary checks (`_main`, UTZERO) do not apply to it.  See
docs/s9term.md.
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
    with open(path, "rb") as handle:
        data = handle.read()
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


# ---------------------------------------------------------------------------
# Kernel images: `zl -H1` ("boot", zl/obj.c), as the kernel mkfile links
# them (sys/src/9/hobbit/mkfile: `-l -R4 -H1 -T0x80004000 -E0x80004000`).
#
# zl/obj.c case 1 sets HEADR = 20+60 = 80 bytes; zl/asm.c `asmb` case 1
# writes twenty big-endian words (`lput` = two big-endian `SPUT`s, with
# `swizflag` already cleared), a MIPS-style COFF file header and optional
# header:
#
#   0  0x161<<16           magic 0x161 and 0 sections
#   1  0                   time and date
#   2  HEADR+text+data     (the file offset of the symbol table)
#   3  symsize             nsyms: bytes of 28-byte Sym records
#   4  0x38<<16 | 7        optional-header size and flags
#   5  407<<16 | 0437      magic (decimal 407 = 0x197) and version 0x11f
#   6  text  7 data  8 bss
#   9  entry               entryvalue(): -E, here a number
#  10  INITTEXT            text base       11 INITDAT  data base
#  12  INITDAT+data        bss base        13 ~0       "gp reg mask"
#  14  lcsize              pc/line table   15-17 0
#  18  ~0                  "gp value ??"   19 0        "complete mystery"
#
# then the text at offset 80 (little-endian words, as in a user binary:
# `cflush` swizzles while `swizflag` is set), the data at 80+text, the
# symbols (`asmsym`, big-endian `lput` values) and the pc/line table
# (`asmlc`).  There is no rounding between sections (asmb's case 1/2
# seeks to HEADR+textsize, HEADR+textsize+datsize).
# ---------------------------------------------------------------------------

KHEADER = struct.Struct(">20I")
KMAGIC = 0x161 << 16
KOPT = (0x38 << 16) | 7
KAOUT = (407 << 16) | 0o437


def is_kernel(path):
    with open(path, "rb") as handle:
        head = handle.read(4)
    return len(head) == 4 and int.from_bytes(head, "big") == KMAGIC


def read_kernel(path):
    """The -H1 header and section offsets; raises SystemExit if not -H1."""
    with open(path, "rb") as handle:
        blob = handle.read()
    if len(blob) < KHEADER.size:
        raise SystemExit("%s: shorter than a -H1 header" % path)
    w = KHEADER.unpack_from(blob)
    if w[0] != KMAGIC:
        raise SystemExit("%s: word 0 is 0x%08x, not -H1's 0x%08x"
                         % (path, w[0], KMAGIC))
    k = {"path": path, "blob": blob, "words": w,
         "symptr": w[2], "syms": w[3], "text": w[6], "data": w[7],
         "bss": w[8], "entry": w[9], "textbase": w[10], "database": w[11],
         "bssbase": w[12], "lcsize": w[14]}
    k["text_off"] = KHEADER.size
    k["data_off"] = k["text_off"] + k["text"]
    k["sym_off"] = k["data_off"] + k["data"]
    k["lc_off"] = k["sym_off"] + k["syms"]
    return k


def kernel_symbols(k):
    """The symbol table as a list, in file order: (value, type, name)."""
    blob = k["blob"][k["sym_off"]:k["sym_off"] + k["syms"]]
    out = []
    for i in range(0, len(blob) - SYM.size + 1, SYM.size):
        value, typ, name, _pad = SYM.unpack_from(blob, i)
        out.append((value, chr(typ), name.split(b"\0")[0].decode("latin-1")))
    return out


def check_kernel(k, syms, data_base=None, entry=None):
    """What asmb's case 1 and pass.c's xdefine()s make true of any -H1 file.
    `data_base` / `entry`: the link's -D and -E when it gave them (9rom:
    -D0xC0604000 -E0x0, sys/src/9/hobbit/mkfile), checked instead of
    "the data follows the text" and "the entry is in the text"."""
    w = k["words"]
    p = []
    fixed = {1: 0, 4: KOPT, 5: KAOUT, 13: 0xFFFFFFFF, 15: 0, 16: 0, 17: 0,
             18: 0xFFFFFFFF, 19: 0}
    for i, v in sorted(fixed.items()):
        if w[i] != v:
            p.append("header word %d is 0x%08x, asm.c writes 0x%08x"
                     % (i, w[i], v))
    if w[2] != KHEADER.size + k["text"] + k["data"]:
        p.append("word 2 (0x%x) != HEADR + text + data" % w[2])
    want = k["lc_off"] + k["lcsize"]
    if len(k["blob"]) != want:
        p.append("file is %d bytes; 80 + text + data + syms + lcsize = %d"
                 % (len(k["blob"]), want))
    if k["syms"] % SYM.size:
        p.append("symbol table size 0x%x is not a multiple of %d"
                 % (k["syms"], SYM.size))
    if k["text"] % 4:
        p.append("text size 0x%x is not a multiple of 4" % k["text"])
    if k["bssbase"] != k["database"] + k["data"]:
        p.append("bss base != data base + data")
    # -R4 and no -D: INITDAT = rnd(INITTEXT + textsize, INITRND).
    gap = k["database"] - (k["textbase"] + k["text"])
    if data_base is not None:
        if k["database"] != data_base:
            p.append("data base 0x%x is not -D 0x%x"
                     % (k["database"], data_base))
    elif not 0 <= gap < 4096 or k["database"] % 4:
        p.append("data base 0x%x does not follow the text (gap %d)"
                 % (k["database"], gap))
    if entry is not None:
        if k["entry"] != entry:
            p.append("entry 0x%x is not -E 0x%x" % (k["entry"], entry))
    elif not k["textbase"] <= k["entry"] < k["textbase"] + k["text"]:
        p.append("entry 0x%x outside the text" % k["entry"])
    if not syms:
        return p
    named = {}
    for v, t, n in syms:
        named.setdefault((n, t), v)
    expect = [(("etext", "T"), k["textbase"] + k["text"]),
              (("bdata", "B"), k["database"]),
              (("edata", "B"), k["database"] + k["data"]),
              (("end", "B"), k["bssbase"] + k["bss"])]
    for key, v in expect:
        if key not in named:
            p.append("no `%s` symbol" % key[0])
        elif named[key] != v:
            p.append("`%s` is 0x%08x, the header says 0x%08x"
                     % (key[0], named[key], v))
    lo_t, hi_t = k["textbase"], k["textbase"] + k["text"]
    lo_d, hi_d = k["database"], k["bssbase"] + k["bss"]
    for v, t, n in syms:
        if t in "TtLl" and not lo_t <= v <= hi_t:
            p.append("text symbol %s 0x%08x outside the text" % (n, v))
        if t in "DdBb" and not lo_d <= v <= hi_d:
            p.append("data symbol %s 0x%08x outside data+bss" % (n, v))
    return p


def kernel_main(path, ndecode):
    k = read_kernel(path)
    syms = kernel_symbols(k)
    print("%s: -H1 kernel image (zl asm.c case 1), %d bytes" %
          (path, len(k["blob"])))
    print("  text 0x%x  data 0x%x  bss 0x%x  syms 0x%x (%d entries)  "
          "lcsize 0x%x" % (k["text"], k["data"], k["bss"], k["syms"],
                           k["syms"] // SYM.size, k["lcsize"]))
    print("  entry 0x%08x  text 0x%08x  data 0x%08x  bss 0x%08x  end 0x%08x"
          % (k["entry"], k["textbase"], k["database"], k["bssbase"],
             k["bssbase"] + k["bss"]))
    print("  file offsets: text 0x%x  data 0x%x  syms 0x%x  pc/line 0x%x"
          % (k["text_off"], k["data_off"], k["sym_off"], k["lc_off"]))
    print("  %s" % ("stripped" if not syms else "not stripped"))
    at = [n for v, t, n in syms if v == k["entry"] and t in "TtLl"]
    if at:
        print("  entry is %s" % ", ".join(at))
    if ndecode:
        parcels = parcel_stream(k)
        for item in decode(parcels, k["textbase"], k["entry"], ndecode):
            print("  %08x  %04x  %s" % (item[0], item[1],
                                        " ".join(map(str, item[2:]))))
    problems = check_kernel(k, syms)
    if problems:
        print("  CHECK FAILED: " + "; ".join(problems), file=sys.stderr)
        return 1
    print("  check: header words, file size, section bases, etext/bdata/"
          "edata/end and every symbol's section agree")
    return 0


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("binary")
    ap.add_argument("--kernel", action="store_true",
                    help="require a -H1 kernel image (detected anyway)")
    ap.add_argument("--image", metavar="PATH",
                    help="write the model image (one 32-bit word per line)")
    ap.add_argument("--entry-bsv", metavar="PATH",
                    help="write a package P9Entry with the entry, text base "
                         "and prefetch-window base")
    ap.add_argument("--decode", type=int, default=8,
                    help="instructions to decode at the entry (default 8)")
    args = ap.parse_args(argv)

    if args.kernel or is_kernel(args.binary):
        if args.image or args.entry_bsv:
            raise SystemExit("--image/--entry-bsv are for user binaries")
        return kernel_main(args.binary, args.decode)

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
