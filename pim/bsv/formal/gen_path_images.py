#!/usr/bin/env python3
"""gen_path_images.py -- images for the formal path properties.

`gen_verilog.sh` writes the smoke images (program/wcs/decode/jump.hex)
with the assembler.  This script writes the extra image sets used by the
multi-way tag-jump, decode-error and fault harnesses:

    multiway_*      multi-way tag jump indexed by the full 8-bit tag
    decode_error_*  undefined opcode: the documented loud error
    fault_*         microinstruction writing an unwritable register

The encodings come from asm/pimasm.py so there is one definition.  The
script writes only the ranges the capped RegFileLoad instances read; the
caps are set in gen_verilog.sh.

Run from bsv/formal/ (gen_verilog.sh does):

    python3 gen_path_images.py formal_images
"""

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "asm"))
import pimasm  # noqa: E402


def write_hex(path, values, width, n):
    """Write exactly n hex values, zero-padding/truncating to n."""
    if len(values) > n:
        values = values[:n]
    else:
        values = list(values) + [0] * (n - len(values))
    mask = (1 << (4 * width)) - 1
    with open(path, "w") as f:
        for v in values:
            f.write(f"{v & mask:0{width}x}\n")


def standard_decode():
    dec = [0] * 256
    for op in pimasm.MICRO_ROUTINES:
        flags = pimasm.DECODE_FLAGS.get(
            op, dict(needs_ea=False, is_load=False, is_store=False, deref=False)
        )
        dec[op] = pimasm.pack_decode(
            op, True, flags["needs_ea"], flags["is_load"],
            flags["is_store"], flags["deref"]
        )
    return dec


def standard_wcs(overrides=None):
    wcs = [0] * (1 << 15)
    for op, mi in pimasm.MICRO_ROUTINES.items():
        wcs[op] = pimasm.pack_micro(mi)
    for addr, mi in (overrides or {}).items():
        wcs[addr] = pimasm.pack_micro(mi)
    return wcs


def main(argv):
    out = Path(argv[1]) if len(argv) > 1 else HERE / "formal_images"
    out.mkdir(parents=True, exist_ok=True)
    M = pimasm.Micro

    # ---------------------------------------------------------------
    # Multi-way tag jump.  The E-stage microcode at uBase 0x0e is a
    # condMultiway jump; the table offset is added to the micro-PC
    # (0x0e), so the four targets are 0x3e/0x4e/0x5e/0x6e.  The entries
    # for 0x00 and 0x7f are decoys that a type-only (7-bit) index would
    # select for tags 0x01 and 0xff (MRB set).
    # ---------------------------------------------------------------
    multiway_src = """
start:
    put_imm a3, 100
    put_imm a4, 0x17f
    put_imm a5, 0x100
    put_imm a6, 0x101
    put_imm a7, 0x1ff
    load    a0, [a3+0]
    jmp_tag a0, int, a6
    load    a2, [a3+1]
    jmp_tag a2, int, a7
    halt
"""
    multiway_prog = pimasm.assemble(multiway_src)
    multiway_prog.words[100] = 0x010000002A   # tag 0x01: type int, MRB set
    multiway_prog.words[101] = 0xFF0000002A   # tag 0xff: type 0x7f, MRB set

    multiway_jump = [0] * 256
    multiway_jump[0x00] = 0x40   # decoy target 0x4e, a1 = a5 = 0x100
    multiway_jump[0x01] = 0x30   # target 0x3e, a1 = a6 = 0x101
    multiway_jump[0x7F] = 0x60   # decoy target 0x6e, a2 = a4 = 0x17f
    multiway_jump[0xFF] = 0x50   # target 0x5e, a2 = a7 = 0x1ff

    multiway_wcs = standard_wcs({
        0x0E: M(srcA=pimasm.RSEL_RS, cond=pimasm.COND_MULTIWAY, last=False),
        0x3E: M(dst=1, srcA=pimasm.RSEL_RT, alu=pimasm.ALU_MOV, last=True),
        0x4E: M(dst=1, srcA=5, alu=pimasm.ALU_MOV, last=True),
        0x5E: M(dst=2, srcA=pimasm.RSEL_RT, alu=pimasm.ALU_MOV, last=True),
        0x6E: M(dst=2, srcA=4, alu=pimasm.ALU_MOV, last=True),
    })

    write_hex(out / "multiway_program.hex", multiway_prog.words, 10, 128)
    write_hex(out / "multiway_wcs.hex", multiway_wcs, 16, 128)
    write_hex(out / "multiway_decode.hex", standard_decode(), 5, 16)
    write_hex(out / "multiway_jump.hex", multiway_jump, 4, 256)

    # ---------------------------------------------------------------
    # Decode error.  Word 0 is an undefined opcode (0x0f); the decode
    # table entry is zero (valid=0).  Word 1 is halt, which must never
    # be reached: the model must raise error instead.
    # ---------------------------------------------------------------
    decode_error_prog = pimasm.Program()
    decode_error_prog.words[0] = pimasm.pack_instr(0x0F)
    decode_error_prog.words[1] = pimasm.pack_instr(pimasm.OP_HALT)

    write_hex(out / "decode_error_program.hex", decode_error_prog.words, 10, 128)
    write_hex(out / "decode_error_wcs.hex", standard_wcs(), 16, 16)
    write_hex(out / "decode_error_decode.hex", standard_decode(), 5, 16)
    write_hex(out / "decode_error_jump.hex", [0] * 256, 4, 16)

    # ---------------------------------------------------------------
    # Fault path.  The jmp microcode (uBase 0x0d) is replaced by one
    # whose destination is rselPc (41), which PimRegFile::write marks
    # badW; the top-level fault rule must turn that into error.
    # ---------------------------------------------------------------
    fault_prog = pimasm.Program()
    fault_prog.words[0] = pimasm.pack_instr(pimasm.OP_JMP, rt=6)
    fault_prog.words[1] = pimasm.pack_instr(pimasm.OP_HALT)

    fault_wcs = standard_wcs({
        0x0D: M(dst=41, srcA=pimasm.RSEL_IMM, alu=pimasm.ALU_MOV, last=True),
    })

    write_hex(out / "fault_program.hex", fault_prog.words, 10, 128)
    write_hex(out / "fault_wcs.hex", fault_wcs, 16, 16)
    write_hex(out / "fault_decode.hex", standard_decode(), 5, 16)
    write_hex(out / "fault_jump.hex", [0] * 256, 4, 16)


if __name__ == "__main__":
    main(sys.argv)
