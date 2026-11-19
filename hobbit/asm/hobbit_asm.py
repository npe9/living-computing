#!/usr/bin/env python3
"""Parcel-level assembler and disassembler for the AT&T 92010 Hobbit.

The encodings implemented here are transcribed from the ATT92010
Programmer's Reference Manual (January 1993), printed pages cited in the
code, and cross-checked against Plan 9's 1st Edition Hobbit linker
(tools/plan9-1e/sys/src/cmd/zl/asm.c and optab.c).  The README next to
this file records the supported syntax and the deliberate gaps.

Image format (shared repository contract): one 32-bit word per line,
eight hex digits, increasing address from 0.  The parcel at an even
address is bits 31:16 of its word; the parcel at an odd address is bits
15:0.  Program entry is address 0.
"""

from __future__ import annotations

import argparse
import ast
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

# ---------------------------------------------------------------------------
# Instruction set tables
# ---------------------------------------------------------------------------

# Table 1-17, printed p. 1-22: niladic subcode[9:0] (parcel = 0x0b00 |
# subcode).  Six of the ten entries have an encoding printed again on the
# instruction page cited here.
NILADICS: Dict[str, Tuple[int, str]] = {
    "CPU":    (0x000, "PRM p. 3-14"),
    "KRET":   (0x001, "PRM p. 3-30"),
    "NOP":    (0x002, "PRM p. 3-35"),
    "FLUSHI": (0x003, "PRM p. 3-24"),
    "FLUSHP": (0x004, "PRM p. 3-25"),
    "CRET":   (0x005, "PRM p. 3-15"),
    "FLUSHD": (0x006, "PRM p. 3-22"),
    "TESTV":  (0x008, "PRM p. 3-46"),
    "TESTC":  (0x009, "PRM p. 3-44"),
    "CLRE":   (0x00A, "PRM p. 3-12"),
}

# Table 1-19, printed p. 1-24: monadic subcode[3:0].  The three-parcel
# monadic first parcel is 0x8000 | subcode | smode << 4; its operand is a
# 32-bit field in parcels 2-3 (PRM p. 1-23).
MONADICS: Dict[str, Tuple[int, str]] = {
    "KCALL":    (0x0, "PRM p. 3-29"),
    "CALL":     (0x1, "PRM p. 3-9"),
    "RETURN":   (0x2, "PRM p. 3-40"),
    "JMP":      (0x3, "PRM p. 3-28"),
    "JMPFN":    (0x4, "PRM p. 3-28"),
    "JMPFY":    (0x5, "PRM p. 3-28"),
    "JMPTN":    (0x6, "PRM p. 3-28"),
    "JMPTY":    (0x7, "PRM p. 3-28"),
    "CATCH":    (0x8, "PRM p. 3-11"),
    "ENTER":    (0x9, "PRM p. 3-21"),
    "LDRAA":    (0xA, "PRM p. 3-31"),
    "FLUSHPTE": (0xB, "PRM p. 3-27"),
    "FLUSHPBE": (0xC, "PRM p. 3-26"),
    "FLUSHDCE": (0xD, "PRM p. 3-23"),
    "POPN":     (0xF, "PRM p. 3-38"),
}

# Tables 1-18 (printed p. 1-23) and 1-20 (printed p. 1-25).  Both tables
# have the same opcode[5:3] x opcode[2:0] grid; the only differing cell is
# row 000 column 000 (monadic versus unimp).  These are the 35 grid
# mnemonics.
DYADICS: Dict[str, Tuple[int, str]] = {
    "ORI":  (0x01, "PRM p. 3-36"),
    "ANDI": (0x02, "PRM p. 3-8"),
    "ADDI": (0x03, "PRM p. 3-6"),
    "MOVA": (0x04, "PRM p. 3-33"),
    "UREM": (0x05, "PRM p. 3-49"),
    "MOV":  (0x06, "PRM p. 3-32"),
    "DQM":  (0x07, "PRM p. 3-18"),
    "TADD": (0x0C, "PRM p. 3-42"),
    "TSUB": (0x0D, "PRM p. 3-47"),
    "CMPGT": (0x1D, "PRM p. 3-13"),
    "CMPHI": (0x1E, "PRM p. 3-13"),
    "CMPEQ": (0x1F, "PRM p. 3-13"),
    "SUB":  (0x20, "PRM p. 3-43"),
    "OR":   (0x21, "PRM p. 3-36"),
    "AND":  (0x22, "PRM p. 3-7"),
    "ADD":  (0x23, "PRM p. 3-5"),
    "XOR":  (0x24, "PRM p. 3-51"),
    "REM":  (0x25, "PRM p. 3-39"),
    "MUL":  (0x26, "PRM p. 3-34"),
    "DIV":  (0x27, "PRM p. 3-17"),
    "SHR":  (0x2C, "PRM p. 3-41"),
    "USHR": (0x2D, "PRM p. 3-50"),
    "SHL":  (0x2E, "PRM p. 3-41"),
    "UDIV": (0x2F, "PRM p. 3-48"),
    "SUB3": (0x30, "PRM p. 3-43"),
    "OR3":  (0x31, "PRM p. 3-37"),
    "AND3": (0x32, "PRM p. 3-8"),
    "ADD3": (0x33, "PRM p. 3-5"),
    "XOR3": (0x34, "PRM p. 3-51"),
    "REM3": (0x35, "PRM p. 3-39"),
    "MUL3": (0x36, "PRM p. 3-34"),
    "DIV3": (0x37, "PRM p. 3-17"),
    "SHR3": (0x3C, "PRM p. 3-41"),
    "USHR3": (0x3D, "PRM p. 3-50"),
    "SHL3": (0x3E, "PRM p. 3-41"),
}

# Table 3-1, printed pp. 3-1 and 3-2: 46 entries, 60 spellings.
TABLE31 = """ADD ADD3 ADDI AND AND3 ANDI CALL CATCH CLRE CMPEQ CMPGT CMPHI
CPU CRET DIV DIV3 DQM ENTER FLUSHD FLUSHDCE FLUSHI FLUSHP FLUSHPBE
FLUSHPTE JMP JMPTY JMPTN JMPFY JMPFN KCALL KRET LDRAA MOV MOVA MUL MUL3
NOP OR OR3 ORI POPN RETURN REM REM3 SHL SHL3 SHR SHR3 SUB SUB3 TADD TESTC
TESTV TSUB UDIV UREM USHR USHR3 XOR XOR3""".split()

# Plan 9 keeps the floating-point names from the CRISP architecture.  The
# 92010 PRM marks those opcode cells "unimp*" (Tables 1-18/1-20) and gives
# no 92010 encoding; we refuse rather than invent one.
FLOATING_POINT = {
    "FADD", "FADD3", "FCLASS", "FCMPEQ", "FCMPEQN", "FCMPGE", "FCMPGT",
    "FCMPN", "FDIV", "FDIV3", "FLOGB", "FMOV", "FMUL", "FMUL3", "FNEXT",
    "FREM", "FSCALB", "FSQRT", "FSUB", "FSUB3",
}

# Encodings exist in the PRM but the hardware takes the unimplemented
# instruction sequence.  Refused unless --allow-unimplemented is given.
UNIMPLEMENTED_HARDWARE = {
    "FLUSHD": "PRM p. 3-22: the 92010 has no data cache; FLUSHD raises the "
              "unimplemented-instruction sequence",
    "FLUSHDCE": "PRM p. 3-23: the 92010 has no data cache; FLUSHDCE raises "
                "the unimplemented-instruction sequence",
}

# ---------------------------------------------------------------------------
# Table 1-15 (printed p. 1-22) one-parcel forms.
#
# Classes: C/N = 5-bit immediate (C 0..15, N -16..-1), S = 5-bit
# word-aligned stack offset, I = 5-bit word-aligned indirect stack offset,
# X/W = 5-bit word-aligned immediate (X is 16..28, W is 32..124).  Source
# fields in bits 9:5 and destination in bits 4:0.  S, I, X and W fields
# are divided by four (PRM p. 1-21: five-bit offset values are multiplied
# by four).  The table's caption spells S "5-bit word-aligned immediate";
# the instruction pages (e.g. MOV p. 3-32 "stk5") and Plan 9's codc2[]
# establish that it is the stack-offset class.
ONE_PARCEL: Dict[str, Dict[Tuple[str, str], int]] = {
    "ADD":   {("C", "S"): 0x14, ("N", "S"): 0x14, ("S", "S"): 0x16},
    "ADD3":  {("C", "S"): 0x15, ("N", "S"): 0x15, ("S", "S"): 0x17,
              ("X", "S"): 0x0D, ("W", "S"): 0x0D},
    "AND":   {("S", "S"): 0x0F},
    "AND3":  {("C", "S"): 0x0E, ("N", "S"): 0x0E},
    "CMPEQ": {("C", "S"): 0x10, ("N", "S"): 0x10, ("S", "S"): 0x13},
    "CMPGT": {("C", "S"): 0x12, ("N", "S"): 0x12, ("S", "S"): 0x11},
    "MOV":   {("S", "S"): 0x18, ("I", "S"): 0x19, ("S", "I"): 0x1A,
              ("I", "I"): 0x1B, ("C", "S"): 0x1C, ("N", "S"): 0x1C,
              ("X", "S"): 0x0A, ("W", "S"): 0x0A},
    "MOVA":  {("S", "S"): 0x1D},
}
SHIFT_ONE_PARCEL = {"SHL3": 0x1E, "SHR3": 0x1F}

# Table 1-16, printed p. 1-22: stack one-parcel subcode[1:0].  Parcel is
# 0x0800 | offset8 << 2 | subcode.
STACK_ONE_PARCEL = {"ENTER": 0, "CATCH": 1, "RETURN": 2, "POPN": 3}

# Table 1-21, printed p. 1-25: general smode/dmode values.  Table 1-22,
# printed p. 1-26, restricts CPU-prefixed instructions to the word modes
# (0xc, 0xd, 0xe, 0xf) plus register mode 0x7.
GENERAL_MODE = {
    ("abs", "B"): 0x0, ("abs", "UB"): 0x1, ("abs", "H"): 0x2,
    ("abs", "UH"): 0x3, ("abs", "W"): 0xC,
    ("stack", "B"): 0x4, ("stack", "UB"): 0x5, ("stack", "H"): 0x6,
    ("stack", "UH"): 0x7, ("stack", "W"): 0xD,
    ("indirect", "B"): 0x8, ("indirect", "UB"): 0x9,
    ("indirect", "H"): 0xA, ("indirect", "UH"): 0xB,
    ("indirect", "W"): 0xE,
    ("imm", "B"): 0xF, ("imm", "UB"): 0xF, ("imm", "H"): 0xF,
    ("imm", "UH"): 0xF, ("imm", "W"): 0xF,
     ("register", "B"): 0x7, ("register", "UB"): 0x7,
     ("register", "H"): 0x7, ("register", "UH"): 0x7,
     ("register", "W"): 0x7,
}
MODE_WIDTH = {0: "B", 1: "UB", 2: "H", 3: "UH", 4: "B", 5: "UB",
              6: "H", 7: "UH", 8: "B", 9: "UB", 10: "H", 11: "UH",
              12: "W", 13: "W", 14: "W", 15: "W"}

# Table 1-24, printed p. 1-26.
REGISTERS = {
    "MSP": 0x1, "ISP": 0x2, "SP": 0x3, "CONFIG": 0x4, "PSW": 0x5,
    "SHAD": 0x6, "VB": 0x7, "STB": 0x8, "FAULT": 0x9, "ID": 0xA,
    "TIMER1": 0xB, "TIMER2": 0xC,
}
REGISTER_NAMES = {v: k for k, v in REGISTERS.items()}

WIDTH_ALIASES = {"B": "B", "UB": "UB", "H": "H", "UH": "UH",
                  "W": "W", "L": "W"}  # PRM p. 3-3 writes R8:L
CONTROL_JUMPS = {"JMP", "JMPFN", "JMPFY", "JMPTN", "JMPTY"}
PCREL_CONTROL = CONTROL_JUMPS | {"CALL"}
FLOW_CONTROL = CONTROL_JUMPS | {"CALL", "LDRAA"}
FLOW32 = {"JMP", "CALL", "LDRAA"}
ABS32 = {"JMPFN", "JMPFY", "JMPTN", "JMPTY"}
STK32_ONLY = {"RETURN", "POPN"}
WORD32 = {"KCALL", "CATCH", "ENTER", "FLUSHPTE", "FLUSHPBE", "FLUSHDCE"}


# ---------------------------------------------------------------------------
# Errors and expression evaluation
# ---------------------------------------------------------------------------

class AsmError(Exception):
    def __init__(self, line: int, message: str):
        self.line = line
        self.message = message
        super().__init__(message)


class UnknownSymbol(Exception):
    def __init__(self, name: str):
        self.name = name
        super().__init__(name)


def eval_expression(text: str, symbols: Dict[str, int]) -> int:
    """Evaluate an integer expression containing labels and integer ops."""
    try:
        node = ast.parse(text, mode="eval")
    except SyntaxError as exc:
        raise ValueError(f"bad expression {text!r}: {exc.msg}") from None

    def walk(n):
        if isinstance(n, ast.Expression):
            return walk(n.body)
        if isinstance(n, ast.Constant):
            if isinstance(n.value, bool) or not isinstance(n.value, int):
                raise ValueError("only integer constants are allowed")
            return n.value
        if isinstance(n, ast.Name):
            if n.id not in symbols:
                raise UnknownSymbol(n.id)
            return symbols[n.id]
        if isinstance(n, ast.UnaryOp):
            v = walk(n.operand)
            if isinstance(n.op, ast.UAdd):
                return v
            if isinstance(n.op, ast.USub):
                return -v
            if isinstance(n.op, ast.Invert):
                return ~v
            raise ValueError("unsupported unary operator")
        if isinstance(n, ast.BinOp):
            a, b = walk(n.left), walk(n.right)
            if isinstance(n.op, ast.Add):
                return a + b
            if isinstance(n.op, ast.Sub):
                return a - b
            if isinstance(n.op, ast.Mult):
                return a * b
            if isinstance(n.op, ast.FloorDiv):
                if b == 0:
                    raise ValueError("division by zero")
                return a // b
            if isinstance(n.op, ast.Mod):
                if b == 0:
                    raise ValueError("division by zero")
                return a % b
            if isinstance(n.op, ast.LShift):
                return a << b
            if isinstance(n.op, ast.RShift):
                return a >> b
            if isinstance(n.op, ast.BitOr):
                return a | b
            if isinstance(n.op, ast.BitAnd):
                return a & b
            if isinstance(n.op, ast.BitXor):
                return a ^ b
            raise ValueError("unsupported binary operator")
        raise ValueError("unsupported expression")

    return walk(node)


# ---------------------------------------------------------------------------
# Source parsing
# ---------------------------------------------------------------------------

@dataclass
class Operand:
    kind: str                  # imm, abs, abs_indirect, stack, indirect,
                               # register, label
    expr: Optional[str] = None
    width: str = "W"
    reg: Optional[str] = None
    text: str = ""


@dataclass
class Instr:
    mnemonic: str
    operands: List[Operand]
    force: Optional[int]
    line: int
    text: str
    cpu_prefix: bool = False   # implied CPU escape for a %register operand
    size: Optional[int] = None  # bytes, set by layout


@dataclass
class Item:
    labels: List[str]
    instr: Optional[Instr]


LABEL_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_.$]*):\s*(.*)$")
FORCE_RE = re.compile(r"^\.([135])\s+(.*)$")


def strip_comment(line: str) -> str:
    cut = len(line)
    for ch in (";", "#"):
        p = line.find(ch)
        if p >= 0:
            cut = min(cut, p)
    return line[:cut].rstrip()


def split_operands(text: str) -> List[str]:
    parts = []
    depth = 0
    start = 0
    for i, ch in enumerate(text):
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth < 0:
                raise ValueError("unbalanced ')'")
        elif ch == "," and depth == 0:
            parts.append(text[start:i].strip())
            start = i + 1
    if depth != 0:
        raise ValueError("unbalanced '('")
    parts.append(text[start:].strip())
    if any(p == "" for p in parts):
        raise ValueError("empty operand")
    return parts


def parse_operand(text: str, line: int) -> Operand:
    raw = text.strip()
    width = "W"
    if ":" in raw:
        head, tail = raw.rsplit(":", 1)
        tail = tail.strip()
        if tail.upper() in WIDTH_ALIASES:
            raw, width = head.strip(), WIDTH_ALIASES[tail.upper()]
        else:
            raise AsmError(line, f"unknown width suffix :{tail}")
    if not raw:
        raise AsmError(line, "missing operand")

    if raw.startswith("%"):
        name = raw[1:].strip().upper()
        if name not in REGISTERS:
            holder = ", ".join(f"%{n}" for n in REGISTER_NAMES.values())
            raise AsmError(line, f"unknown register %{name}; known: {holder}")
        return Operand("register", width=width, reg=name, text=text)
    if raw.startswith("**$"):
        return Operand("abs_indirect", expr=raw[3:].strip(), width=width,
                       text=text)
    if raw.startswith("*$"):
        return Operand("abs", expr=raw[2:].strip(), width=width, text=text)
    if raw.startswith("$"):
        return Operand("imm", expr=raw[1:].strip(), width=width, text=text)
    if re.match(r"^\*[Rr](?=[-+0-9(])", raw):
        return Operand("indirect", expr=raw[2:].strip(), width=width,
                       text=text)
    if re.match(r"^[Rr](?=[-+0-9(])", raw):
        return Operand("stack", expr=raw[1:].strip(), width=width, text=text)
    if re.match(r"^[-+0-9(]", raw):
        return Operand("label", expr=raw, width=width, text=text)
    if re.match(r"^[A-Za-z_][A-Za-z0-9_.$]*$", raw):
        return Operand("label", expr=raw, width=width, text=text)
    raise AsmError(line, f"cannot parse operand {text!r}")


def parse_source(text: str, filename: str):
    items: List[Item] = []
    previous_was_cpu = False
    seen_labels = set()
    lines = text.splitlines()
    for lineno, original in enumerate(lines, 1):
        line = strip_comment(original).strip()
        if not line:
            continue
        labels: List[str] = []
        rest = line
        while True:
            m = LABEL_RE.match(rest)
            if not m:
                break
            label = m.group(1)
            if label in seen_labels:
                raise AsmError(lineno, f"duplicate label {label}")
            seen_labels.add(label)
            labels.append(label)
            rest = m.group(2).strip()
            if not rest:
                break
        instr = None
        if rest:
            force = None
            fm = FORCE_RE.match(rest)
            if fm:
                force = int(fm.group(1))
                rest = fm.group(2).strip()
            bits = rest.split(None, 1)
            mnemonic = bits[0].upper()
            operand_text = bits[1].strip() if len(bits) > 1 else ""
            try:
                operands = (split_operands(operand_text)
                            if operand_text else [])
            except ValueError as exc:
                raise AsmError(lineno, str(exc)) from None
            parsed = [parse_operand(op, lineno) for op in operands]
            has_reg = any(op.kind == "register" for op in parsed)
            instr = Instr(mnemonic=mnemonic, operands=parsed, force=force,
                          line=lineno, text=original.strip())
            instr.cpu_prefix = has_reg and not previous_was_cpu
            previous_was_cpu = (mnemonic == "CPU")
        items.append(Item(labels=labels, instr=instr))
    return items


# ---------------------------------------------------------------------------
# Encoding helpers
# ---------------------------------------------------------------------------

def _check_mnemonic(instr: Instr):
    name = instr.mnemonic
    if name in NILADICS or name in MONADICS or name in DYADICS:
        return
    if name in SHIFT_ONE_PARCEL:
        return
    if name in FLOATING_POINT:
        raise AsmError(
            instr.line,
            f"{name} has no ATT92010 encoding: PRM Tables 1-18/1-20 "
            f"(printed pp. 1-23, 1-25) mark the cell unimp* and the 92010 "
            f"traps; Plan 9's optab.c keeps the CRISP floating-point name")
    raise AsmError(instr.line, f"unknown mnemonic {name}")


def _arity(instr: Instr, expected: int):
    if len(instr.operands) != expected:
        raise AsmError(
            instr.line,
            f"{instr.mnemonic} takes {expected} operand"
            f"{'s' if expected != 1 else ''}, got {len(instr.operands)}")


def _value(op: Operand, symbols: Dict[str, int], line: int) -> int:
    if op.expr is None:
        raise AsmError(line, "operand has no value")
    try:
        return eval_expression(op.expr, symbols)
    except UnknownSymbol as exc:
        raise AsmError(line, f"undefined symbol {exc.name}") from None
    except ValueError as exc:
        raise AsmError(line, str(exc)) from None


def _try_value(op: Optional[Operand], symbols: Dict[str, int]) -> Optional[int]:
    if op is None or op.expr is None:
        return None
    try:
        return eval_expression(op.expr, symbols)
    except (UnknownSymbol, ValueError):
        return None


def _one_parcel_class(op: Operand, value: int, is_source: bool) -> Optional[str]:
    """Class letter of a Table 1-15 one-parcel operand."""
    if op.width != "W":
        return None
    if op.kind == "imm":
        if is_source:
            if -16 <= value <= -1:
                return "N"
            if 0 <= value <= 15:
                return "C"
            if 16 <= value <= 28 and value % 4 == 0:
                return "X"
            if 16 <= value <= 31:
                return "U"
            if 32 <= value <= 124 and value % 4 == 0:
                return "W"
            return None
        return None
    if op.kind == "stack" and 0 <= value <= 124 and value % 4 == 0:
        return "S"
    if op.kind == "indirect" and 0 <= value <= 124 and value % 4 == 0:
        return "I"
    return None


def _field5(cls: str, value: int) -> int:
    if cls in ("S", "I", "X", "W"):
        return (value >> 2) & 0x1F
    return value & 0x1F


def one_parcel_encoding(instr: Instr, symbols: Dict[str, int]
                        ) -> Optional[List[int]]:
    """Return the Table 1-15 1-parcel encoding, or None if not eligible."""
    name = instr.mnemonic
    if name in ("KCALL",):
        if len(instr.operands) != 1:
            return None
        op = instr.operands[0]
        v = _try_value(op, symbols)
        if op.kind == "imm" and v is not None and 0 <= v <= 4092 and v % 4 == 0:
            return [((v >> 2) & 0x3FF)]
        return None
    if name in PCREL_CONTROL:
        if len(instr.operands) != 1:
            return None
        op = instr.operands[0]
        if op.kind != "label":
            return None
        v = _try_value(op, symbols)
        if v is None:
            return None
        offset = v - _pc_of(instr)
        if offset < -1024 or offset > 1022 or (offset & 1):
            return None
        return [((MONADICS[name][0] << 10) | ((offset >> 1) & 0x3FF))]
    if name in STACK_ONE_PARCEL:
        if len(instr.operands) != 1:
            return None
        op = instr.operands[0]
        if op.kind != "stack":
            return None
        v = _try_value(op, symbols)
        if v is None:
            return None
        if name == "ENTER":
            if not (-4096 <= v <= -16) or v % 16:
                return None
        else:
            if not (0 <= v <= 4080) or v % 16:
                return None
        return [0x0800 | (((v >> 4) & 0xFF) << 2) | STACK_ONE_PARCEL[name]]
    if name in SHIFT_ONE_PARCEL:
        if len(instr.operands) != 2:
            return None
        src, dst = instr.operands
        sv = _try_value(src, symbols)
        dv = _try_value(dst, symbols)
        if (src.kind != "imm" or src.width != "W" or sv is None
                or not 0 <= sv <= 31):
            return None
        if (dst.kind != "stack" or dst.width != "W" or dv is None
                or not 0 <= dv <= 124 or dv % 4):
            return None
        return [(SHIFT_ONE_PARCEL[name] << 10) | ((sv & 0x1F) << 5)
                | ((dv >> 2) & 0x1F)]
    if name not in ONE_PARCEL:
        return None
    if len(instr.operands) != 2:
        return None
    src, dst = instr.operands
    sv = _try_value(src, symbols)
    dv = _try_value(dst, symbols)
    if sv is None or dv is None:
        return None
    sc = _one_parcel_class(src, sv, True)
    dc = _one_parcel_class(dst, dv, False)
    if sc is None or dc is None:
        return None
    opcode = ONE_PARCEL[name].get((sc, dc))
    if opcode is None:
        # ADD3/MOV also accept a source in the X/W class, but ADD3's
        # Table 1-15 cell is named .WS and Plan 9's decod lists xs/ws;
        # the mapping above already contains both.
        return None
    return [(opcode << 10) | (_field5(sc, sv) << 5) | _field5(dc, dv)]


# The layout pass needs the address of the instruction for PC-relative
# sizing.  It is attached temporarily to the Instr object.
def _pc_of(instr: Instr) -> int:
    return getattr(instr, "_pc", 0)


def _set_pc(instr: Instr, pc: int):
    instr._pc = pc


def _mode_and_value(op: Operand, symbols: Dict[str, int], line: int,
                    cpu: bool) -> Tuple[int, int]:
    if op.kind == "register":
        return 0x7, REGISTERS[op.reg]
    if cpu and op.width != "W":
        raise AsmError(
            line,
            "CPU-prefixed instructions accept only word-sized memory/immediate "
            "modes and register mode (PRM Table 1-22, printed p. 1-26)")
    try:
        mode = GENERAL_MODE[(op.kind, op.width)]
    except KeyError:
        raise AsmError(line, f"{op.kind} operand cannot use width :{op.width}")
    return mode, _value(op, symbols, line)


def _fit16(op: Operand, value: int) -> bool:
    if op.kind in ("imm", "stack", "indirect"):
        return -0x8000 <= value <= 0x7FFF
    if op.kind == "abs":
        return 0 <= value <= 0xFFFF
    if op.kind == "register":
        return 0 <= value <= 0xF
    return False


def _fit32(value: int) -> bool:
    return -(1 << 31) <= value <= 0xFFFFFFFF


def message_for_unimplemented(instr: Instr) -> str:
    return UNIMPLEMENTED_HARDWARE[instr.mnemonic]


def _encode_monadic(name: str, instr: Instr, symbols: Dict[str, int],
                    size: int) -> List[int]:
    _arity(instr, 1)
    op = instr.operands[0]
    subcode = MONADICS[name][0]
    if name in FLOW_CONTROL:
        if op.kind == "label":
            if name in ABS32:
                mode = 0xE
            elif name in FLOW32:
                mode = 0xE
            else:
                mode = 0xE
            target = _value(op, symbols, instr.line)
            value = target - _pc_of(instr)
        elif op.kind == "abs":
            if name in ABS32:
                mode = 0xF
            elif name in FLOW32:
                mode = 0xF
            else:
                raise AsmError(instr.line, f"{name} does not take an absolute "
                                           f"operand")
            value = _value(op, symbols, instr.line)
        elif op.kind == "abs_indirect":
            if name in ABS32:
                raise AsmError(instr.line, f"{name} cannot use indirect "
                                           f"addressing (PRM p. 3-28)")
            mode = 0xC
            value = _value(op, symbols, instr.line)
        elif op.kind == "indirect":
            if name in ABS32:
                raise AsmError(instr.line, f"{name} cannot use indirect "
                                           f"addressing (PRM p. 3-28)")
            mode = 0xD
            value = _value(op, symbols, instr.line)
        else:
            raise AsmError(instr.line, f"{name} needs a label, *$addr, "
                                       f"**$addr or *Roffset operand")
        if mode == 0xE:
            if not -(1 << 31) <= value <= 0x7FFFFFFF:
                raise AsmError(instr.line,
                               "PC-relative offset does not fit 32 bits")
        elif not _fit32(value):
            raise AsmError(instr.line, "address or offset does not fit 32 bits")
    elif name in STACK_ONE_PARCEL:
        # A bare number is parsed as a label, not as a stack offset.  For
        # these four instructions say what the operand should be instead
        # of complaining about an addressing-mode width.  ENTER and CATCH
        # also have word32 forms ($imm, *$addr, *Roff); RETURN and POPN
        # are stack-offset only (PRM pp. 3-11, 3-21, 3-40, 3-38).
        allowed = (("stack",) if name in STK32_ONLY
                   else ("stack", "imm", "abs", "indirect"))
        if op.kind not in allowed:
            examples = {"ENTER": "R-16", "CATCH": "R32",
                        "RETURN": "R16", "POPN": "R16"}
            pages = {"ENTER": "3-21", "CATCH": "3-11",
                     "RETURN": "3-40", "POPN": "3-38"}
            raise AsmError(
                instr.line,
                f"{name} expects a stack offset "
                f"({name} {examples[name]}; PRM p. {pages[name]})")
        mode, value = _mode_and_value(op, symbols, instr.line, False)
        if name == "ENTER" and op.kind == "stack" and value >= 0:
            raise AsmError(instr.line, "ENTER stack offset must be negative; "
                                       "ENTER R0 and positive offsets are illegal "
                                       "(PRM p. 3-21)")
        if name in STK32_ONLY and value < 0:
            raise AsmError(instr.line, f"{name} stack offset must be "
                                       f"non-negative (PRM p. 3-40)")
        if mode not in (0xC, 0xD, 0xE, 0xF):
            raise AsmError(instr.line, f"{name} needs a word32 addressing mode "
                                       f"(PRM Table 3-2, p. 3-4)")
        if not _fit32(value):
            raise AsmError(instr.line, "address or offset does not fit 32 bits")
    else:
        mode, value = _mode_and_value(op, symbols, instr.line, False)
        if op.kind == "register":
            raise AsmError(instr.line, f"{name} cannot take a register operand "
                                       f"without CPU")
        if mode not in (0xC, 0xD, 0xE, 0xF):
            raise AsmError(instr.line, f"{name} needs a word32 addressing mode "
                                       f"(PRM Table 3-2, p. 3-4)")
        if not _fit32(value):
            raise AsmError(instr.line, "address or offset does not fit 32 bits")
    if size != 6:
        raise AsmError(instr.line, f"{name} has no {size}-byte form")
    return [0x8000 | (mode << 4) | subcode,
            (value >> 16) & 0xFFFF, value & 0xFFFF]


def _encode_dyadic(name: str, instr: Instr, symbols: Dict[str, int],
                   size: int, cpu: bool) -> List[int]:
    _arity(instr, 2)
    src, dst = instr.operands
    register_count = sum(1 for o in instr.operands if o.kind == "register")
    # PRM p. 1-27 permits at most one register *read*.  MOV writes its
    # destination, so the manual's own MOV %SP,%SHAD (PRM p. 1-15) is a
    # read of SP plus a write of SHAD.  Other dyadics read their
    # destination as well, so two register operands would be two reads.
    if cpu and register_count > 1 and name != "MOV":
        raise AsmError(instr.line, "at most one register may be read per "
                                   "instruction (PRM p. 1-27)")
    smode, sval = _mode_and_value(src, symbols, instr.line, cpu)
    dmode, dval = _mode_and_value(dst, symbols, instr.line, cpu)
    if cpu:
        for op, mode in ((src, smode), (dst, dmode)):
            if mode not in (0x7, 0xC, 0xD, 0xE, 0xF):
                raise AsmError(
                    instr.line,
                    "CPU-prefixed instructions accept only mode 0x7 and the "
                    "word modes 0xc-0xf (PRM Table 1-22, printed p. 1-26)")
    if name == "DQM":
        # PRM p. 3-18: source is a word mode (0xc-0xf; mode 0xf is the
        # replicated constant); destination size is selected by special
        # modes 0x0/0x4/0x8 (double-word) or 0xc/0xd/0xe (quad-word).
        if smode not in (0xC, 0xD, 0xE, 0xF):
            raise AsmError(instr.line, "DQM source must use a word addressing "
                                       "mode (PRM p. 3-18)")
        if dmode not in (0x0, 0x4, 0x8, 0xC, 0xD, 0xE):
            raise AsmError(instr.line, "DQM destination must be a double- or "
                                       "quad-word mode 0x0/0x4/0x8/0xc/0xd/0xe "
                                       "(PRM p. 3-18)")
    if name == "MOVA":
        if src.kind == "imm":
            raise AsmError(instr.line, "MOVA does not accept an immediate "
                                       "source (PRM p. 3-33)")
        if src.kind == "register" or dst.kind == "register":
            raise AsmError(instr.line, "MOVA does not accept register operands "
                                       "(PRM p. 3-33)")
        if smode not in (0xC, 0xD, 0xE):
            raise AsmError(instr.line, "MOVA source must use a word addressing "
                                       "mode (PRM p. 3-33)")
    opcode = DYADICS[name][0]
    if size == 6:
        if not _fit16(src, sval) or not _fit16(dst, dval):
            raise AsmError(instr.line, "operand does not fit the 16-bit fields "
                                       "of the three-parcel form (PRM p. 1-23)")
        return [0x8000 | (opcode << 8) | (smode << 4) | dmode,
                sval & 0xFFFF, dval & 0xFFFF]
    if size == 10:
        if not _fit32(sval) or not _fit32(dval):
            raise AsmError(instr.line, "operand does not fit a 32-bit field")
        return [0xC000 | (opcode << 8) | (smode << 4) | dmode,
                (sval >> 16) & 0xFFFF, sval & 0xFFFF,
                (dval >> 16) & 0xFFFF, dval & 0xFFFF]
    raise AsmError(instr.line, f"{name} has no {size}-byte form")


def encode_instruction(instr: Instr, symbols: Dict[str, int]) -> List[int]:
    _check_mnemonic(instr)
    name = instr.mnemonic
    size = instr.size

    if name in UNIMPLEMENTED_HARDWARE and not getattr(instr, "_allow_unimp", False):
        raise AsmError(instr.line, message_for_unimplemented(instr))

    if name in NILADICS:
        _arity(instr, 0)
        if size != 2:
            raise AsmError(instr.line, f"{name} is a one-parcel niladic; "
                                       f"it has no {size}-byte form")
        return [(0x0B << 10) | NILADICS[name][0]]

    if name in STACK_ONE_PARCEL:
        one = one_parcel_encoding(instr, symbols)
        if size == 2:
            if one is None:
                raise AsmError(instr.line, f"{name} stack offset is not "
                                           f"encodable in the one-parcel form")
            return one
        # Fall through to the three-parcel monadic stack form.
        return _encode_monadic(name, instr, symbols, size)

    if name in MONADICS:
        one = one_parcel_encoding(instr, symbols) if name in (
            PCREL_CONTROL | {"KCALL"}) else None
        if size == 2:
            if one is None:
                raise AsmError(instr.line, f"{name} is not encodable in one "
                                           f"parcel with these operands")
            return one
        return _encode_monadic(name, instr, symbols, size)

    if name in SHIFT_ONE_PARCEL or name in DYADICS:
        one = one_parcel_encoding(instr, symbols)
        if size == 2:
            if one is None:
                raise AsmError(instr.line, f"{name} is not encodable in one "
                                           f"parcel with these operands "
                                           f"(PRM Table 1-15, p. 1-22)")
            return one
        body_size = size - (2 if instr.cpu_prefix else 0)
        return _encode_dyadic(name, instr, symbols, body_size,
                              cpu=instr.cpu_prefix or _prev_cpu(instr))

    raise AsmError(instr.line, f"unknown mnemonic {name}")


def _prev_cpu(instr: Instr) -> bool:
    return bool(getattr(instr, "_cpu_ctx", False))


# ---------------------------------------------------------------------------
# Layout and assembly
# ---------------------------------------------------------------------------

def _choose_size(instr: Instr, pc: int, symbols: Dict[str, int]) -> int:
    _set_pc(instr, pc)
    name = instr.mnemonic
    base = 2 if instr.cpu_prefix else 0

    if instr.force:
        forced = instr.force * 2
        if name in NILADICS and forced != 2:
            raise AsmError(instr.line, f"{name} has no {forced}-byte form")
        if name in STACK_ONE_PARCEL and forced not in (2, 6):
            raise AsmError(instr.line, f"{name} has no {forced}-byte form")
        if forced == 10 and name not in SHIFT_ONE_PARCEL and name not in DYADICS:
            raise AsmError(instr.line, f"{name} has no five-parcel form")
        return base + forced

    if name in NILADICS:
        return base + 2

    if name in STACK_ONE_PARCEL:
        if one_parcel_encoding(instr, symbols) is not None:
            return base + 2
        return base + 6

    if name in PCREL_CONTROL:
        if one_parcel_encoding(instr, symbols) is not None:
            return base + 2
        return base + 6

    if name == "KCALL":
        if one_parcel_encoding(instr, symbols) is not None:
            return base + 2
        return base + 6

    if name in MONADICS:
        return base + 6

    # Dyadic.
    if one_parcel_encoding(instr, symbols) is not None:
        return base + 2
    # Default to the wide form when a symbol is still unresolved; the
    # layout loop shrinks it once labels have addresses.
    ok16 = True
    for op in instr.operands:
        v = REGISTERS[op.reg] if op.kind == "register" else _try_value(op, symbols)
        if v is None or not _fit16(op, v):
            ok16 = False
            break
    return base + (6 if ok16 else 10)


def layout(items: List[Item]) -> Tuple[Dict[str, int], int]:
    symbols: Dict[str, int] = {}
    previous: Optional[Tuple[Tuple[Tuple[str, int], ...],
                            Tuple[int, ...]]] = None
    for _ in range(40):
        new_symbols: Dict[str, int] = {}
        sizes: List[int] = []
        addr = 0
        for item in items:
            for label in item.labels:
                if label in new_symbols:
                    raise AsmError(0, f"duplicate label {label}")
                new_symbols[label] = addr
            if item.instr is None:
                continue
            pc = addr
            # An explicit CPU line emits its parcel before the next
            # instruction.  A %register instruction with no explicit CPU
            # gets an implied prefix, included in its own size.
            size = _choose_size(item.instr, pc, symbols)
            item.instr.size = size
            sizes.append(size)
            addr += size
        state = (tuple(sorted(new_symbols.items())), tuple(sizes))
        if state == previous:
            return new_symbols, addr
        previous = state
        symbols = new_symbols
    raise AsmError(0, "assembly did not converge (phase error)")


def pad_parcels(parcels: List[int]) -> Tuple[List[int], bool]:
    if len(parcels) % 2:
        return parcels + [(0x0B << 10) | NILADICS["NOP"][0]], True
    return parcels, False


def parcels_to_words(parcels: List[int]) -> List[int]:
    words = []
    for i in range(0, len(parcels), 2):
        hi = parcels[i] & 0xFFFF
        lo = parcels[i + 1] & 0xFFFF if i + 1 < len(parcels) else 0
        words.append((hi << 16) | lo)
    return words


def words_to_parcels(words: Sequence[int]) -> List[int]:
    parcels = []
    for w in words:
        parcels.append((w >> 16) & 0xFFFF)
        parcels.append(w & 0xFFFF)
    return parcels


def write_image(path: Path, parcels: List[int]):
    words = parcels_to_words(parcels)
    with path.open("w", encoding="ascii") as f:
        for w in words:
            f.write(f"{w:08X}\n")


def read_image(path: Path) -> Tuple[List[int], List[int]]:
    words: List[int] = []
    word_lines: List[int] = []
    for lineno, line in enumerate(path.read_text(encoding="ascii").splitlines(), 1):
        s = line.strip()
        if not s:
            continue
        if not re.fullmatch(r"[0-9A-Fa-f]{8}", s):
            raise AsmError(lineno, "image word must be exactly 8 hex digits")
        words.append(int(s, 16))
        word_lines.append(lineno)
    return words, word_lines


def listing_from_assembly(text: str, filename: str,
                          allow_unimplemented: bool = False) -> Tuple[str,
                                                                   List[int],
                                                                   List[int]]:
    items = parse_source(text, filename)
    for item in items:
        if item.instr is None:
            continue
        _check_mnemonic(item.instr)
        if item.instr.mnemonic in UNIMPLEMENTED_HARDWARE:
            if not allow_unimplemented:
                raise AsmError(item.instr.line,
                               message_for_unimplemented(item.instr))
            item.instr._allow_unimp = True
    symbols, total = layout(items)
    prev_cpu = False
    for item in items:
        if item.instr is None:
            continue
        item.instr._cpu_ctx = prev_cpu
        if item.instr.cpu_prefix:
            item.instr._cpu_ctx = True
        prev_cpu = item.instr.mnemonic == "CPU"

    out: List[str] = ["; hobbit_asm listing"]
    parcels_all: List[int] = []
    addresses: List[int] = []
    for item in items:
        for label in item.labels:
            out.append(f"          {label}:")
        if item.instr is None:
            continue
        instr = item.instr
        addr = len(parcels_all) * 2
        addresses.append(addr)
        _set_pc(instr, addr)
        encoded = encode_instruction(instr, symbols)
        body_size = instr.size - (2 if instr.cpu_prefix else 0)
        if len(encoded) * 2 != body_size:
            raise AsmError(instr.line,
                           f"internal phase error: {instr.mnemonic} sized "
                           f"{instr.size} bytes but encoded to "
                           f"{len(encoded) * 2 + (2 if instr.cpu_prefix else 0)}")
        if instr.cpu_prefix:
            encoded = [(0x0B << 10)] + encoded
        parcels_all.extend(encoded)
        mark = ""
        if instr.mnemonic in UNIMPLEMENTED_HARDWARE and \
                getattr(instr, "_allow_unimp", False):
            mark = "  [unimplemented]"
        ptext = " ".join(f"{p:04X}" for p in encoded)
        out.append(f"{addr:06X}: {ptext:<26} {instr.text}{mark}")
    if len(parcels_all) % 2:
        pad_addr = len(parcels_all) * 2
        pad = (0x0B << 10) | NILADICS["NOP"][0]
        out.append(f"{pad_addr:06X}: {pad:04X}                "
                   f"NOP ; padding to a whole 32-bit image word")
    return "\n".join(out) + "\n", parcels_all, addresses


# ---------------------------------------------------------------------------
# Disassembler
# ---------------------------------------------------------------------------

def _sx(value: int, bits: int) -> int:
    sign = 1 << (bits - 1)
    return (value & ((1 << bits) - 1)) - (sign << 1) if value & sign else value


def _reg_name(code: int) -> Optional[str]:
    if code == 0x0 or 0xD <= code <= 0xF:
        return None
    return REGISTER_NAMES.get(code)


def _format_general_operand(mode: int, value: int, bits: int,
                            control: bool = False) -> Optional[str]:
    """One disassembled operand for a general smode/dmode."""
    if control:
        if mode == 0xC:
            return f"**${value:#x}"
        if mode == 0xD:
            return f"*R{_sx(value, bits)}"
        if mode == 0xE:
            return "label"  # caller substitutes the computed target
        if mode == 0xF:
            return f"*${value:#x}"
        return None
    width = MODE_WIDTH.get(mode)
    if width is None:
        return None
    suffix = "" if width == "W" else f":{width}"
    if mode in (0x0, 0x1, 0x2, 0x3, 0xC):
        return f"*${value:#x}{suffix}"
    if mode in (0x4, 0x5, 0x6, 0x7, 0xD):
        return f"R{_sx(value, bits)}{suffix}"
    if mode in (0x8, 0x9, 0xA, 0xB, 0xE):
        return f"*R{_sx(value, bits)}{suffix}"
    if mode == 0xF:
        return f"${_sx(value, bits)}"
    return None


def _decode_niladic(parcel: int) -> str:
    sub = parcel & 0x3FF
    for name, (code, _) in NILADICS.items():
        if code == sub:
            return name
    if sub >= 0x200:
        return f"trapt {parcel:#06x} ; niladic trap through VB+8 (Table 1-17, p. 1-22)"
    return f"unimplemented {parcel:#06x} ; niladic subcode {sub:#x} (Table 1-17, p. 1-22)"


def _decode_stack(parcel: int) -> str:
    sub = parcel & 0x3
    field = (parcel >> 2) & 0xFF
    names = {0: "ENTER", 1: "CATCH", 2: "RETURN", 3: "POPN"}
    name = names[sub]
    if name == "ENTER":
        # PRM p. 3-21: the 8-bit field is left padded with ones and
        # multiplied by 16, so field 0 is -4096, not 0.
        off = (field - 256) * 16
    else:
        off = field * 16
    return f"{name} R{off}"


def _decode_one_parcel(parcel: int, pc: int) -> str:
    opcode = (parcel >> 10) & 0x1F
    src = (parcel >> 5) & 0x1F
    dst = parcel & 0x1F
    if opcode == 0x0B:
        return _decode_niladic(parcel)
    if opcode == 0x02:
        return _decode_stack(parcel)
    if opcode == 0x00:
        return f"KCALL ${(parcel & 0x3FF) << 2:#x}"
    pcrel_names = {0x01: "CALL", 0x03: "JMP", 0x04: "JMPFN", 0x05: "JMPFY",
                   0x06: "JMPTN", 0x07: "JMPTY"}
    if opcode in pcrel_names:
        off = _sx(parcel & 0x3FF, 10) * 2
        return f"{pcrel_names[opcode]} {pc + off:#06x}"
    if opcode in (0x0E, 0x10, 0x12, 0x14, 0x15, 0x1C):
        names = {0x0E: "AND3", 0x10: "CMPEQ", 0x12: "CMPGT", 0x14: "ADD",
                 0x15: "ADD3", 0x1C: "MOV"}
        return f"{names[opcode]} ${_sx(src, 5)},R{dst * 4}"
    if opcode in (0x0A, 0x0D):
        names = {0x0A: "MOV", 0x0D: "ADD3"}
        return f"{names[opcode]} ${src * 4},R{dst * 4}"
    if opcode in (0x1E, 0x1F):
        names = {0x1E: "SHL3", 0x1F: "SHR3"}
        return f"{names[opcode]} ${src},R{dst * 4}"
    stack_stack = {0x0F: "AND", 0x11: "CMPGT", 0x13: "CMPEQ", 0x16: "ADD",
                   0x17: "ADD3", 0x18: "MOV", 0x1D: "MOVA"}
    if opcode in stack_stack:
        return f"{stack_stack[opcode]} R{src * 4},R{dst * 4}"
    if opcode == 0x19:
        return f"MOV *R{src * 4},R{dst * 4}"
    if opcode == 0x1A:
        return f"MOV R{src * 4},*R{dst * 4}"
    if opcode == 0x1B:
        return f"MOV *R{src * 4},*R{dst * 4}"
    return (f"unimplemented {parcel:#06x} ; one-parcel opcode "
            f"{opcode:#04x} (Table 1-15, p. 1-22)")


def _decode_monadic(parcel: int, operand: int, pc: int, cpu: bool) -> str:
    sub = parcel & 0xF
    mode = (parcel >> 4) & 0xF
    name = None
    for n, (code, _) in MONADICS.items():
        if code == sub:
            name = n
            break
    if name is None:
        return (f"unimplemented {parcel:#06x} {operand >> 16:#06x} "
                f"{operand & 0xffff:#06x} ; monadic subcode {sub:#x} "
                f"(Table 1-19, p. 1-24)")
    if name in FLOW_CONTROL:
        if mode == 0xE:
            target = pc + _sx(operand, 32)
            return f"{name} {target:#06x}"
        text = _format_general_operand(mode, operand, 32, control=True)
        if text is None:
            return (f"unimplemented {parcel:#06x} {operand >> 16:#06x} "
                    f"{operand & 0xffff:#06x} ; {name} mode {mode:#x} "
                    f"(Table 1-23, p. 1-26)")
        return f"{name} {text}"
    if name in STK32_ONLY and mode != 0xD:
        return (f"unimplemented {parcel:#06x} {operand >> 16:#06x} "
                f"{operand & 0xffff:#06x} ; {name} requires stack offset "
                f"mode 0xd (PRM p. 3-40/3-38)")
    if name not in STK32_ONLY and mode not in (0xC, 0xD, 0xE, 0xF):
        return (f"unimplemented {parcel:#06x} {operand >> 16:#06x} "
                f"{operand & 0xffff:#06x} ; {name} requires a word32 mode "
                f"0xc-0xf (PRM Table 3-2, p. 3-4)")
    text = _format_general_operand(mode, operand, 32)
    if text is None:
        return (f"unimplemented {parcel:#06x} {operand >> 16:#06x} "
                f"{operand & 0xffff:#06x} ; {name} mode {mode:#x}")
    return f"{name} {text}"


def _decode_dyadic(parcel: int, src: int, dst: int, pc: int,
                   cpu: bool) -> str:
    opcode = (parcel >> 8) & 0x3F
    smode = (parcel >> 4) & 0xF
    dmode = parcel & 0xF
    name = None
    for n, (code, _) in DYADICS.items():
        if code == opcode:
            name = n
            break
    if name is None:
        return (f"unimplemented {parcel:#06x} {src:#06x} {dst:#06x} ; "
                f"opcode {opcode:#04x} (Table 1-18/1-20)")

    def operand(mode: int, value: int):
        if cpu and mode == 0x7:
            # PRM p. 3-14: the low four bits select the register and the
            # high bits are ignored but should be zero.  A non-zero high
            # field is not reproduced bit-exactly, so do not pretend it is.
            if value & ~0xF:
                return None
            reg = _reg_name(value)
            return f"%{reg}" if reg else None
        if cpu and mode not in (0xC, 0xD, 0xE, 0xF):
            return None
        if not cpu and mode == 0x7:
            return None
        return _format_general_operand(mode, value, 16)

    s = operand(smode, src)
    d = operand(dmode, dst)
    if s is None or d is None:
        return (f"unimplemented {parcel:#06x} {src:#06x} {dst:#06x} ; "
                f"{name} modes {smode:#x}/{dmode:#x}"
                f"{' (CPU prefix required for mode 7)' if 7 in (smode, dmode) else ''}")
    return f"{name} {s},{d}"


def disassemble_parcels(parcels: Sequence[int],
                        line_at=None) -> List[str]:
    """Disassemble exactly this parcel sequence.

    line_at(parcel_index) may supply a source line for truncation errors;
    it exists so --disasm can report file:line for a truncated image.
    """
    out: List[str] = []
    i = 0
    cpu = False

    def where(index: int) -> int:
        return line_at(index) if line_at else 0

    while i < len(parcels):
        pc = i * 2
        p = parcels[i]
        top = p >> 14
        cpu_here = cpu
        cpu = False
        if not (p & 0x8000):
            text = _decode_one_parcel(p, pc)
            if p == ((0x0B << 10) | NILADICS["CPU"][0]):
                cpu = True
            out.append(text)
            i += 1
        elif top == 2:
            if i + 2 >= len(parcels):
                raise AsmError(where(i),
                               f"truncated three-parcel instruction at "
                               f"address {pc:#x}")
            operand = (parcels[i + 1] << 16) | parcels[i + 2]
            if ((p >> 8) & 0x3F) == 0:
                text = _decode_monadic(p, operand, pc, cpu_here)
            else:
                text = _decode_dyadic(p, parcels[i + 1], parcels[i + 2],
                                      pc, cpu_here)
            out.append(".3 " + text)
            i += 3
        elif top == 3:
            if i + 4 >= len(parcels):
                raise AsmError(where(i),
                               f"truncated five-parcel instruction at "
                               f"address {pc:#x}")
            src = (parcels[i + 1] << 16) | parcels[i + 2]
            dst = (parcels[i + 3] << 16) | parcels[i + 4]
            text = _decode_dyadic_wide(p, src, dst, pc, cpu_here)
            out.append(".5 " + text)
            i += 5
        else:
            # top == 1 cannot occur here: bit 15 == 0 is the one-parcel
            # case above, so an 01 prefix is a one-parcel opcode, not an
            # illegal length.
            raise AsmError(0, f"internal disassembly error at {pc:#x}")
    return out


def disassemble_words(words: Sequence[int],
                      word_lines: Optional[Sequence[int]] = None) -> List[str]:
    parcels = words_to_parcels(words)

    def line_at(parcel_index: int) -> int:
        if not word_lines:
            return 0
        return word_lines[min(parcel_index // 2, len(word_lines) - 1)]

    return disassemble_parcels(parcels, line_at)


def _decode_dyadic_wide(parcel: int, src: int, dst: int, pc: int,
                        cpu: bool) -> str:
    opcode = (parcel >> 8) & 0x3F
    smode = (parcel >> 4) & 0xF
    dmode = parcel & 0xF
    name = None
    for n, (code, _) in DYADICS.items():
        if code == opcode:
            name = n
            break
    if name is None:
        return (f"unimplemented {parcel:#06x} {src:#06x} {dst:#06x} ; "
                f"opcode {opcode:#04x} (Table 1-18/1-20)")

    def operand(mode: int, value: int):
        if cpu and mode == 0x7:
            if value & ~0xF:
                return None
            reg = _reg_name(value)
            return f"%{reg}" if reg else None
        if cpu and mode not in (0xC, 0xD, 0xE, 0xF):
            return None
        if not cpu and mode == 0x7:
            return None
        return _format_general_operand(mode, value, 32)

    s = operand(smode, src)
    d = operand(dmode, dst)
    if s is None or d is None:
        return (f"unimplemented {parcel:#06x} {src:#06x} {dst:#06x} ; "
                f"{name} modes {smode:#x}/{dmode:#x}"
                f"{' (CPU prefix required for mode 7)' if 7 in (smode, dmode) else ''}")
    return f"{name} {s},{d}"


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="ATT92010 Hobbit parcel assembler/disassembler")
    p.add_argument("input", nargs="?", help="assembly source (or ignored with --disasm)")
    p.add_argument("-o", "--output", help="image output path (default: INPUT.hex)")
    p.add_argument("--list", metavar="FILE", help="write an address/parcel listing")
    p.add_argument("--disasm", metavar="IMAGE",
                   help="disassemble IMAGE to standard output")
    p.add_argument("--allow-unimplemented", action="store_true",
                   help="encode PRM-defined instructions the 92010 traps on "
                        "(FLUSHD, FLUSHDCE) and mark the listing")
    return p


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_arg_parser().parse_args(argv)

    if args.disasm:
        if args.output:
            print("hobbit_asm: error: -o cannot be used with --disasm; "
                  "disassembly goes to standard output", file=sys.stderr)
            return 1
        path = Path(args.disasm)
        try:
            words, word_lines = read_image(path)
            text = disassemble_words(words, word_lines)
        except AsmError as exc:
            where = f"{path}:{exc.line}" if exc.line else str(path)
            print(f"{where}: error: {exc.message}", file=sys.stderr)
            return 1
        except (OSError, UnicodeDecodeError) as exc:
            print(f"{path}: error: {exc}", file=sys.stderr)
            return 1
        print("\n".join(text))
        if args.list:
            try:
                lines = []
                all_parcels = words_to_parcels(words)
                parcel_index = 0
                for line in text:
                    # The length is in the parcel prefix, even for an
                    # unimplemented encoding: bit 15 clear is one parcel,
                    # 10 is three, 11 is five.
                    p0 = all_parcels[parcel_index]
                    if not (p0 & 0x8000):
                        n = 1
                    elif (p0 >> 14) == 2:
                        n = 3
                    else:
                        n = 5
                    parcels = all_parcels[parcel_index:parcel_index + n]
                    ptext = " ".join(f"{p:04X}" for p in parcels)
                    lines.append(f"{parcel_index * 2:06X}: {ptext:<24} {line}")
                    parcel_index += n
                Path(args.list).write_text("\n".join(lines) + "\n",
                                           encoding="ascii")
            except OSError as exc:
                print(f"{args.list}: error: {exc}", file=sys.stderr)
                return 1
        return 0

    if not args.input:
        print("hobbit_asm: error: INPUT is required unless --disasm is used",
              file=sys.stderr)
        return 1
    src_path = Path(args.input)
    try:
        source = src_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        print(f"{src_path}: error: {exc}", file=sys.stderr)
        return 1
    try:
        listing, parcels, addresses = listing_from_assembly(
            source, str(src_path), args.allow_unimplemented)
    except AsmError as exc:
        where = f"{src_path}:{exc.line}" if exc.line else str(src_path)
        print(f"{where}: error: {exc.message}", file=sys.stderr)
        return 1
    parcels, _padded = pad_parcels(parcels)
    out_path = Path(args.output) if args.output else src_path.with_suffix(".hex")
    try:
        write_image(out_path, parcels)
        if args.list:
            Path(args.list).write_text(listing, encoding="ascii")
    except OSError as exc:
        print(f"{out_path}: error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
