#!/usr/bin/env python3
"""A minimal MIPS R3000 disassembler for a 1st Edition /mips/bin a.out
(V_MAGIC 0x407, text at 0x1020): prints the named functions, enough to
read stack-frame layouts.  It backs tools/p9symdef.py's MIPS_PRE (A3):
the release's /mips/bin/rl (not vendored; from plan9-1e.tar.bz2,
`tar -xjf plan9-1e.tar.bz2 plan9-1e/mips/bin/rl`, sha256 in
docs/plan9_syscalls.md) is what wrote the shipped __.SYMDEF tables.

    python3 tools/p9mipsdis.py DIR/plan9-1e/mips/bin/rl objtype readar
    python3 tools/p9mipsdis.py DIR/plan9-1e/mips/bin/rl -s     # symbols

vl may fill a JAL's delay slot with the callee's first instruction and
jump to callee+4 (readrl's call of objtype does), so `jal X+4` followed by `addi SP,SP,-N` is a call
of X.  Only the opcodes rl's code needs are named; others print raw."""
import struct
import sys

R = ["r0", "r1", "r2", "r3", "r4", "r5", "r6", "r7", "r8", "r9", "r10",
     "r11", "r12", "r13", "r14", "r15", "r16", "r17", "r18", "r19", "r20",
     "r21", "r22", "r23", "r24", "r25", "r26", "r27", "r28", "SP", "r30",
     "LINK"]
I_OPS = {8: "addi", 9: "addiu", 10: "slti", 11: "sltiu", 12: "andi",
         13: "ori", 14: "xori", 15: "lui", 32: "lb", 33: "lh", 35: "lw",
         36: "lbu", 37: "lhu", 40: "sb", 41: "sh", 43: "sw", 4: "beq",
         5: "bne", 6: "blez", 7: "bgtz", 49: "lwc1", 57: "swc1"}
SPECIAL = {0: "sll", 2: "srl", 3: "sra", 4: "sllv", 8: "jr", 9: "jalr",
           32: "add", 33: "addu", 34: "sub", 35: "subu", 36: "and",
           37: "or", 38: "xor", 39: "nor", 42: "slt", 43: "sltu",
           24: "mult", 25: "multu", 26: "div", 27: "divu", 16: "mfhi",
           18: "mflo", 12: "syscall"}

path = sys.argv[1]
b = open(path, "rb").read()
magic, text, data, bss, syms, entry, _s, _l = struct.unpack(">8I", b[:32])
base = 0x1020
symoff = 32 + text + data
sy = {}
names = []
for i in range(symoff, symoff + syms - 27, 28):
    v, t, nm, _p = struct.unpack(">IB20s3s", b[i:i + 28])
    names.append((v, chr(t & 0x7f), nm.split(b"\0")[0].decode("latin-1")))
fun = sorted((v, n) for v, t, n in names if t in "Tt")


def word(a):
    o = 32 + a - base
    return struct.unpack(">I", b[o:o + 4])[0]


def dis(a):
    w = word(a)
    op = w >> 26
    rs, rt, rd = (w >> 21) & 31, (w >> 16) & 31, (w >> 11) & 31
    imm = w & 0xFFFF
    simm = imm - 0x10000 if imm & 0x8000 else imm
    if w == 0:
        return "nop"
    if op == 0:
        f = w & 63
        nm = SPECIAL.get(f, "special%d" % f)
        if f in (0, 2, 3):
            return "%s %s,%s,%d" % (nm, R[rd], R[rt], (w >> 6) & 31)
        return "%s %s,%s,%s" % (nm, R[rd], R[rs], R[rt])
    if op in (2, 3):
        t = ((a + 4) & 0xF0000000) | ((w & 0x3FFFFFF) << 2)
        n = [nn for v, nn in fun if v == t]
        return "%s %x %s" % ("j" if op == 2 else "jal", t, n)
    if op in I_OPS:
        nm = I_OPS[op]
        if op in (32, 33, 35, 36, 37, 40, 41, 43, 49, 57):
            return "%s %s,%d(%s)" % (nm, R[rt], simm, R[rs])
        if op in (4, 5, 6, 7):
            return "%s %s,%s,%x" % (nm, R[rs], R[rt], a + 4 + 4 * simm)
        return "%s %s,%s,%d" % (nm, R[rt], R[rs], simm)
    if op == 1:
        return "regimm %s rt=%d %x" % (R[rs], rt, a + 4 + 4 * simm)
    return "op%d %08x" % (op, w)


if len(sys.argv) > 2 and sys.argv[2] == "-s":
    for v, n in fun:
        print("%x %s" % (v, n))
    sys.exit()
for want in sys.argv[2:]:
    for k, (v, n) in enumerate(fun):
        if n == want:
            end = fun[k + 1][0] if k + 1 < len(fun) else base + text
            print("%s:" % n)
            for a in range(v, end, 4):
                print("  %x  %08x  %s" % (a, word(a), dis(a)))
