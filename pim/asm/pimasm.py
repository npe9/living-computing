#!/usr/bin/env python3
"""pimasm.py -- table-driven assembler for the PIM/m PE model.

The machine-instruction and microinstruction encodings are the model's
own, not historical PIM/m encodings.  The 1992 sources acquired in
docs/ give the 40-bit word, the 8-bit tag, the 32K x 64-bit WCS and the
five-stage pipeline, but not the bit assignments; see
docs/architecture.md "Evidence status".  This file is the single place
those model encodings are defined, and bsv/PimTypes.bsv mirrors it.

Usage:
    python3 pimasm.py --out-dir ../bsv/generated
    python3 pimasm.py --selftest
"""

from __future__ import annotations

import argparse
import random
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

# ---------------------------------------------------------------------
# Encodings (mirror of bsv/PimTypes.bsv)
# ---------------------------------------------------------------------

# Machine opcodes.
OP_NOP = 0x00
OP_HALT = 0x01
OP_PUT_IMM = 0x02
OP_PUT_REG = 0x03
OP_GET_ARG = 0x04
OP_ADD = 0x05
OP_SUB = 0x06
OP_MOVE = 0x07
OP_LOAD = 0x08
OP_STORE = 0x09
OP_DEREF = 0x0A
OP_SET_MRB = 0x0B
OP_CLR_MRB = 0x0C
OP_JMP = 0x0D
OP_JMP_TAG = 0x0E

OPCODES = {
    "nop": OP_NOP,
    "halt": OP_HALT,
    "put_imm": OP_PUT_IMM,
    "put_reg": OP_PUT_REG,
    "get_arg": OP_GET_ARG,
    "add": OP_ADD,
    "sub": OP_SUB,
    "move": OP_MOVE,
    "load": OP_LOAD,
    "store": OP_STORE,
    "deref": OP_DEREF,
    "set_mrb": OP_SET_MRB,
    "clr_mrb": OP_CLR_MRB,
    "jmp": OP_JMP,
    "jmp_tag": OP_JMP_TAG,
}

# Tag types.
TAG_INT = 0
TAG_ATOM = 1
TAG_REF = 2
TAG_VAR = 3
TAG_LIST = 4
TAG_STRUCT = 5
TAG_CODE = 6
TAG_FLOAT = 7

TAG_NAMES = {
    "int": TAG_INT,
    "atom": TAG_ATOM,
    "ref": TAG_REF,
    "var": TAG_VAR,
    "list": TAG_LIST,
    "struct": TAG_STRUCT,
    "code": TAG_CODE,
    "float": TAG_FLOAT,
}

# ALU operations.
ALU_ADD = 0
ALU_SUB = 1
ALU_AND = 2
ALU_OR = 3
ALU_XOR = 4
ALU_MOV = 5
ALU_SHL = 6
ALU_SHR = 7
ALU_EQ = 8
ALU_NE = 9
ALU_TAG_SET = 10
ALU_TAG_CLR = 11
ALU_NEG = 12

# Memory operations.
MEM_NONE = 0
MEM_READ = 1
MEM_WRITE = 2

# Conditions.
COND_ALWAYS = 0
COND_NEVER = 1
COND_TAG_EQ = 2
COND_TAG_NE = 3
COND_TAG_REF = 4
COND_TAG_NOTREF = 5
COND_MULTIWAY = 6
COND_ZERO = 7

# Register selectors used by microcode.
RSEL_IMM = 48
RSEL_RS = 49
RSEL_RT = 50
RSEL_RD = 51
RSEL_FETCH = 52
RSEL_DEREF = 53
RSEL_NONE = 63

REG_NAMES = {f"a{i}": i for i in range(16)}
REG_NAMES.update({f"x{i}": 16 + i for i in range(16)})


def pack_instr(op: int, rd: int = 0, rs: int = 0, rt: int = 0, imm: int = 0) -> int:
    if not (0 <= op < 256 and 0 <= rd < 32 and 0 <= rs < 32 and 0 <= rt < 32):
        raise ValueError("instruction field out of range")
    if not (0 <= imm < (1 << 17)):
        raise ValueError("instruction immediate out of range")
    return (op << 32) | (rd << 27) | (rs << 22) | (rt << 17) | imm


def unpack_instr(word: int) -> dict:
    return {
        "op": (word >> 32) & 0xFF,
        "rd": (word >> 27) & 0x1F,
        "rs": (word >> 22) & 0x1F,
        "rt": (word >> 17) & 0x1F,
        "imm": word & 0x1FFFF,
    }


def pack_decode(u_base: int, valid: bool, needs_ea: bool, is_load: bool,
                is_store: bool, deref: bool) -> int:
    return ((u_base & 0x7FFF) << 5 | (int(valid) << 4) | (int(needs_ea) << 3)
            | (int(is_load) << 2) | (int(is_store) << 1) | int(deref))


def unpack_decode(value: int) -> dict:
    return {
        "uBase": (value >> 5) & 0x7FFF,
        "valid": bool((value >> 4) & 1),
        "needsEA": bool((value >> 3) & 1),
        "isLoad": bool((value >> 2) & 1),
        "isStore": bool((value >> 1) & 1),
        "deref": bool(value & 1),
    }


@dataclass
class Micro:
    next: int = 0
    imm: int = 0
    alu: int = ALU_MOV
    srcA: int = RSEL_NONE
    srcB: int = RSEL_NONE
    dst: int = RSEL_NONE
    mem: int = MEM_NONE
    cond: int = COND_ALWAYS
    deref: bool = False
    halt: bool = False
    mrb_set: bool = False
    mrb_clr: bool = False
    last: bool = False
    branch: bool = False


def pack_micro(m: Micro) -> int:
    if not (0 <= m.next < (1 << 15)):
        raise ValueError("micro next out of range")
    if not (0 <= m.imm < (1 << 16)):
        raise ValueError("micro immediate out of range")
    return (
        (m.next << 49)
        | (m.imm << 33)
        | ((m.alu & 0xF) << 29)
        | ((m.srcA & 0x3F) << 23)
        | ((m.srcB & 0x3F) << 17)
        | ((m.dst & 0x3F) << 11)
        | ((m.mem & 0x3) << 9)
        | ((m.cond & 0x7) << 6)
        | (int(m.deref) << 5)
        | (int(m.halt) << 4)
        | (int(m.mrb_set) << 3)
        | (int(m.mrb_clr) << 2)
        | (int(m.last) << 1)
        | int(m.branch)
    )


def unpack_micro(value: int) -> Micro:
    return Micro(
        next=(value >> 49) & 0x7FFF,
        imm=(value >> 33) & 0xFFFF,
        alu=(value >> 29) & 0xF,
        srcA=(value >> 23) & 0x3F,
        srcB=(value >> 17) & 0x3F,
        dst=(value >> 11) & 0x3F,
        mem=(value >> 9) & 0x3,
        cond=(value >> 6) & 0x7,
        deref=bool((value >> 5) & 1),
        halt=bool((value >> 4) & 1),
        mrb_set=bool((value >> 3) & 1),
        mrb_clr=bool((value >> 2) & 1),
        last=bool((value >> 1) & 1),
        branch=bool(value & 1),
    )


# Microprogram per opcode.  uBase == opcode; each routine is one
# microinstruction in this model.
MICRO_ROUTINES: dict[int, Micro] = {
    OP_NOP: Micro(last=True),
    OP_HALT: Micro(halt=True, last=True),
    OP_PUT_IMM: Micro(dst=RSEL_RD, srcA=RSEL_IMM, alu=ALU_MOV, last=True),
    OP_PUT_REG: Micro(dst=RSEL_RD, srcA=RSEL_RS, alu=ALU_MOV, last=True),
    OP_GET_ARG: Micro(dst=RSEL_RD, srcA=RSEL_RS, alu=ALU_MOV, last=True),
    OP_ADD: Micro(dst=RSEL_RD, srcA=RSEL_RS, srcB=RSEL_RT, alu=ALU_ADD, last=True),
    OP_SUB: Micro(dst=RSEL_RD, srcA=RSEL_RS, srcB=RSEL_RT, alu=ALU_SUB, last=True),
    OP_MOVE: Micro(dst=RSEL_RD, srcA=RSEL_RS, alu=ALU_MOV, last=True),
    OP_LOAD: Micro(dst=RSEL_RD, srcA=RSEL_FETCH, alu=ALU_MOV,
                   mem=MEM_READ, last=True),
    OP_STORE: Micro(srcA=RSEL_RD, mem=MEM_WRITE, last=True),
    OP_DEREF: Micro(dst=RSEL_RD, srcA=RSEL_DEREF, alu=ALU_MOV,
                    deref=True, last=True),
    OP_SET_MRB: Micro(dst=RSEL_RD, srcA=RSEL_RS, alu=ALU_TAG_SET, last=True),
    OP_CLR_MRB: Micro(dst=RSEL_RD, srcA=RSEL_RS, alu=ALU_TAG_CLR, last=True),
    OP_JMP: Micro(cond=COND_ALWAYS, branch=True, last=True),
    OP_JMP_TAG: Micro(srcA=RSEL_RS, cond=COND_TAG_EQ, branch=True, last=True),
}

DECODE_FLAGS = {
    OP_LOAD: dict(needs_ea=True, is_load=True, is_store=False, deref=False),
    OP_STORE: dict(needs_ea=True, is_load=False, is_store=True, deref=False),
    OP_DEREF: dict(needs_ea=False, is_load=False, is_store=False, deref=True),
}


# ---------------------------------------------------------------------
# Assembler
# ---------------------------------------------------------------------

@dataclass
class Program:
    words: list[int] = field(default_factory=lambda: [0] * (1 << 16))
    labels: dict[str, int] = field(default_factory=dict)
    listing: list[tuple[int, int, str]] = field(default_factory=list)


class AsmError(Exception):
    pass


def _reg(name: str) -> int:
    key = name.strip().lower()
    if key not in REG_NAMES:
        raise AsmError(f"unknown register {name!r}")
    return REG_NAMES[key]


def _imm(text: str, labels: dict[str, int] | None) -> int:
    text = text.strip()
    if labels is not None and text in labels:
        return labels[text]
    if text.startswith("-"):
        return int(text, 0) & 0x1FFFF
    if re.fullmatch(r"0x[0-9a-fA-F]+", text):
        return int(text, 16)
    if re.fullmatch(r"\d+", text):
        return int(text, 10)
    raise AsmError(f"bad immediate {text!r}")


def _parse_mem(text: str) -> tuple[str, int]:
    m = re.fullmatch(r"\[\s*([A-Za-z][A-Za-z0-9]*)\s*(?:\+\s*(.+))?\s*\]", text)
    if not m:
        raise AsmError(f"bad memory operand {text!r}")
    return m.group(1), (m.group(2) if m.group(2) is not None else "0")


def _encode_line(mnem: str, ops: list[str], labels: dict[str, int] | None) -> int:
    op = OPCODES[mnem]
    if mnem == "nop" or mnem == "halt":
        return pack_instr(op)
    if mnem == "put_imm":
        if len(ops) != 2:
            raise AsmError("put_imm needs rd, imm")
        return pack_instr(op, rd=_reg(ops[0]), imm=_imm(ops[1], labels))
    if mnem in ("put_reg", "get_arg", "move"):
        if len(ops) != 2:
            raise AsmError(f"{mnem} needs rd, rs")
        return pack_instr(op, rd=_reg(ops[0]), rs=_reg(ops[1]))
    if mnem in ("add", "sub"):
        if len(ops) != 3:
            raise AsmError(f"{mnem} needs rd, rs, rt")
        return pack_instr(op, rd=_reg(ops[0]), rs=_reg(ops[1]), rt=_reg(ops[2]))
    if mnem == "load":
        if len(ops) != 2:
            raise AsmError("load needs rd, [rs+imm]")
        base, off = _parse_mem(ops[1])
        return pack_instr(op, rd=_reg(ops[0]), rs=_reg(base), imm=_imm(off, labels))
    if mnem == "store":
        if len(ops) != 2:
            raise AsmError("store needs rd, [rs+imm]")
        base, off = _parse_mem(ops[1])
        return pack_instr(op, rd=_reg(ops[0]), rs=_reg(base), imm=_imm(off, labels))
    if mnem == "deref":
        if len(ops) != 2:
            raise AsmError("deref needs rd, rs")
        return pack_instr(op, rd=_reg(ops[0]), rs=_reg(ops[1]))
    if mnem in ("set_mrb", "clr_mrb"):
        if len(ops) != 1:
            raise AsmError(f"{mnem} needs rd")
        r = _reg(ops[0])
        return pack_instr(op, rd=r, rs=r)
    if mnem == "jmp":
        if len(ops) != 1:
            raise AsmError("jmp needs rt")
        return pack_instr(op, rt=_reg(ops[0]))
    if mnem == "jmp_tag":
        if len(ops) != 3:
            raise AsmError("jmp_tag needs rs, tag, rt")
        tag = ops[1].strip().lower()
        if tag not in TAG_NAMES:
            raise AsmError(f"unknown tag {ops[1]!r}")
        return pack_instr(op, rs=_reg(ops[0]), rt=_reg(ops[2]),
                          imm=TAG_NAMES[tag])
    raise AsmError(f"unsupported mnemonic {mnem!r}")


def assemble(text: str) -> Program:
    lines: list[tuple[str | None, str, str]] = []
    labels: dict[str, int] = {}
    pc = 0
    for raw in text.splitlines():
        line = raw.split(";", 1)[0].split("#", 1)[0].strip()
        if not line:
            continue
        label = None
        while ":" in line:
            head, rest = line.split(":", 1)
            if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", head.strip()):
                break
            label = head.strip()
            if label in labels:
                raise AsmError(f"duplicate label {label!r}")
            labels[label] = pc
            line = rest.strip()
        if not line:
            lines.append((label, "", raw))
            continue
        parts = line.replace(",", " ").split()
        lines.append((label, line, raw))
        pc += 1

    prog = Program(labels=labels)
    pc = 0
    for label, line, raw in lines:
        if not line:
            prog.listing.append((pc, 0, raw.rstrip()))
            continue
        # Keep bracketed memory operands intact: re-split the original
        # mnemonic/operand text rather than the comma-flattened form.
        m = re.match(r"([A-Za-z_][A-Za-z0-9_]*)\s*(.*)$", line)
        assert m
        mnem = m.group(1).lower()
        rest = m.group(2).strip()
        if mnem not in OPCODES:
            raise AsmError(f"unknown mnemonic {mnem!r} on line {raw!r}")
        ops = _split_ops(rest)
        word = _encode_line(mnem, ops, labels)
        prog.words[pc] = word
        prog.listing.append((pc, word, raw.rstrip()))
        pc += 1
    return prog


def _split_ops(text: str) -> list[str]:
    if not text:
        return []
    out: list[str] = []
    depth = 0
    cur = ""
    for ch in text:
        if ch == "[":
            depth += 1
        elif ch == "]":
            depth -= 1
        if ch == "," and depth == 0:
            out.append(cur.strip())
            cur = ""
        else:
            cur += ch
    if cur.strip():
        out.append(cur.strip())
    return out


def build_smoke_program() -> Program:
    src = """
start:
    put_imm a0, 10
    put_imm a1, 32
    put_imm a3, 100
    put_imm a6, done
    add     a2, a0, a1
    store   a2, [a3+0]
    load    a4, [a3+0]
    set_mrb a4
    deref   a5, a4
    jmp_tag a5, ref, a6
    jmp     a6
    put_imm a7, 99
done:
    halt
"""
    return assemble(src)


# ---------------------------------------------------------------------
# Image writer
# ---------------------------------------------------------------------

def write_images(prog: Program, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)

    # program.hex: 64K words of 40 bits.
    with open(out_dir / "program.hex", "w") as f:
        for w in prog.words:
            f.write(f"{w & ((1 << 40) - 1):010x}\n")

    # wcs.hex: 32K microinstructions, 64 bits each.
    wcs = [0] * (1 << 15)
    for op, mi in MICRO_ROUTINES.items():
        wcs[op] = pack_micro(mi)
    with open(out_dir / "wcs.hex", "w") as f:
        for w in wcs:
            f.write(f"{w:016x}\n")

    # decode.hex: 256 entries, 20 bits each.
    dec = [0] * 256
    for op in MICRO_ROUTINES:
        flags = DECODE_FLAGS.get(op, dict(needs_ea=False, is_load=False,
                                          is_store=False, deref=False))
        dec[op] = pack_decode(op, True, flags["needs_ea"], flags["is_load"],
                              flags["is_store"], flags["deref"])
    with open(out_dir / "decode.hex", "w") as f:
        for w in dec:
            f.write(f"{w:05x}\n")

    # jump.hex: 256 tag-indexed microprogram offsets, 15 bits each.
    with open(out_dir / "jump.hex", "w") as f:
        for _ in range(256):
            f.write(f"{0:04x}\n")

    with open(out_dir / "program.lst", "w") as f:
        for pc, word, raw in prog.listing:
            if word:
                f.write(f"{pc:04x}  {word:010x}  {raw}\n")
            else:
                f.write(f"            {raw}\n")
        f.write("\nlabels:\n")
        for name, addr in sorted(prog.labels.items(), key=lambda kv: kv[1]):
            f.write(f"  {name} = {addr}\n")


# ---------------------------------------------------------------------
# Self-tests
# ---------------------------------------------------------------------

def selftest() -> int:
    rng = random.Random(0x7030)
    fails = 0

    def check(name: str, got, want) -> None:
        nonlocal fails
        if got != want:
            print(f"FAIL {name}: got {got!r}, want {want!r}")
            fails += 1

    for _ in range(2000):
        op = rng.randrange(256)
        rd, rs, rt = (rng.randrange(32) for _ in range(3))
        imm = rng.randrange(1 << 17)
        w = pack_instr(op, rd, rs, rt, imm)
        check("instr", unpack_instr(w),
              dict(op=op, rd=rd, rs=rs, rt=rt, imm=imm))

    for _ in range(2000):
        m = Micro(
            next=rng.randrange(1 << 15), imm=rng.randrange(1 << 16),
            alu=rng.randrange(16), srcA=rng.randrange(64),
            srcB=rng.randrange(64), dst=rng.randrange(64),
            mem=rng.randrange(4), cond=rng.randrange(8),
            deref=bool(rng.randrange(2)), halt=bool(rng.randrange(2)),
            mrb_set=bool(rng.randrange(2)), mrb_clr=bool(rng.randrange(2)),
            last=bool(rng.randrange(2)), branch=bool(rng.randrange(2)))
        check("micro", unpack_micro(pack_micro(m)), m)

    prog = build_smoke_program()
    check("label start", prog.labels["start"], 0)
    check("label done", prog.labels["done"], 12)
    expected = [
        ("put_imm", dict(op=OP_PUT_IMM, rd=0, imm=10)),
        ("put_imm", dict(op=OP_PUT_IMM, rd=1, imm=32)),
        ("put_imm", dict(op=OP_PUT_IMM, rd=3, imm=100)),
        ("put_imm", dict(op=OP_PUT_IMM, rd=6, imm=12)),
        ("add", dict(op=OP_ADD, rd=2, rs=0, rt=1)),
        ("store", dict(op=OP_STORE, rd=2, rs=3, imm=0)),
        ("load", dict(op=OP_LOAD, rd=4, rs=3, imm=0)),
        ("set_mrb", dict(op=OP_SET_MRB, rd=4, rs=4)),
        ("deref", dict(op=OP_DEREF, rd=5, rs=4)),
        ("jmp_tag", dict(op=OP_JMP_TAG, rs=5, rt=6, imm=TAG_REF)),
        ("jmp", dict(op=OP_JMP, rt=6)),
        ("put_imm", dict(op=OP_PUT_IMM, rd=7, imm=99)),
        ("halt", dict(op=OP_HALT)),
    ]
    for pc, (mnem, fields) in enumerate(expected):
        got = unpack_instr(prog.words[pc])
        for k, v in fields.items():
            check(f"word {pc} {mnem} {k}", got[k], v)

    check("decode load",
          unpack_decode(pack_decode(OP_LOAD, True, True, True, False, False)),
          dict(uBase=OP_LOAD, valid=True, needsEA=True, isLoad=True,
               isStore=False, deref=False))
    check("decode deref",
          unpack_decode(pack_decode(OP_DEREF, True, False, False, False, True)),
          dict(uBase=OP_DEREF, valid=True, needsEA=False, isLoad=False,
               isStore=False, deref=True))
    check("micro halt", unpack_micro(pack_micro(MICRO_ROUTINES[OP_HALT])).halt, True)
    check("micro jmp branch",
          unpack_micro(pack_micro(MICRO_ROUTINES[OP_JMP])).branch, True)

    if fails == 0:
        print("pimasm selftest: PASS")
    else:
        print(f"pimasm selftest: {fails} FAIL")
    return 1 if fails else 0


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", type=Path, default=Path("../bsv/generated"))
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest:
        return selftest()
    prog = build_smoke_program()
    write_images(prog, args.out_dir)
    print(f"wrote images to {args.out_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
