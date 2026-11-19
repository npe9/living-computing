#!/usr/bin/env python3
"""Generate docs/isa.md from pimasm.py.

The machine and microinstruction encodings are the model's own; the 1992
sources do not publish the bit assignments, and KL1-B's encoding is not
in the corpus.  This script is the single generator for the ISA table;
``--check`` fails if the committed document drifts from the assembler.

Usage:
    python3 asm/gen_isa_table.py            # write docs/isa.md
    python3 asm/gen_isa_table.py --check    # verify docs/isa.md
"""

from __future__ import annotations

import argparse
import difflib
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import pimasm  # noqa: E402

DOC = HERE.parent / "docs" / "isa.md"

# Operand forms and one-line semantics.  The assembler's _encode_line
# owns the operand grammar; this table documents it and --check verifies
# every mnemonic is covered.
FORMS = {
    "nop": ("", "do nothing"),
    "halt": ("", "halt the PE"),
    "put_imm": ("rd, imm", "rd <- zero-extended 17-bit immediate"),
    "put_reg": ("rd, rs", "rd <- rs"),
    "get_arg": ("rd, rs", "rd <- rs (argument fetch in the model)"),
    "add": ("rd, rs, rt", "rd <- rs + rt"),
    "sub": ("rd, rs, rt", "rd <- rs - rt"),
    "move": ("rd, rs", "rd <- rs"),
    "load": ("rd, [rs+imm]", "rd <- memory[rs + imm]"),
    "store": ("rd, [rs+imm]", "memory[rs + imm] <- rd"),
    "deref": ("rd, rs", "rd <- dereference(rs)"),
    "set_mrb": ("rd", "rd.tag.MRB <- 1"),
    "clr_mrb": ("rd", "rd.tag.MRB <- 0"),
    "jmp": ("rt", "branch to rt"),
    "jmp_tag": ("rs, tag, rt", "branch to rt if rs.tag == tag"),
}

# Display name, bit range, width, meaning.  The layout probes below tie
# each range to the packer in pimasm.py.
INSTR_FIELDS = [
    ("op", 39, 32, "machine opcode"),
    ("rd", 31, 27, "destination register"),
    ("rs", 26, 22, "first source register"),
    ("rt", 21, 17, "second source register or branch target"),
    ("imm", 16, 0, "immediate, offset, or tag"),
]

# Display name, packer parameter name, bit range, width, meaning.
DECODE_FIELDS = [
    ("uBase", "u_base", 19, 5, "microprogram base"),
    ("valid", "valid", 4, 4, "decode entry valid"),
    ("needsEA", "needs_ea", 3, 3, "instruction needs an effective address"),
    ("isLoad", "is_load", 2, 2, "load"),
    ("isStore", "is_store", 1, 1, "store"),
    ("deref", "deref", 0, 0, "dereference"),
]

MICRO_FIELDS = [
    ("next", 63, 49, "next micro-PC"),
    ("imm", 48, 33, "micro immediate"),
    ("alu", 32, 29, "ALU operation"),
    ("srcA", 28, 23, "A source selector"),
    ("srcB", 22, 17, "B source selector"),
    ("dst", 16, 11, "destination selector"),
    ("mem", 10, 9, "memory operation"),
    ("cond", 8, 6, "branch condition"),
    ("deref", 5, 5, "dereference"),
    ("halt", 4, 4, "halt"),
    ("mrb_set", 3, 3, "set MRB"),
    ("mrb_clr", 2, 2, "clear MRB"),
    ("last", 1, 1, "last microinstruction"),
    ("branch", 0, 0, "branch"),
]


def _names(prefix: str) -> dict[int, str]:
    out: dict[int, str] = {}
    for name, value in vars(pimasm).items():
        if name.startswith(prefix) and isinstance(value, int):
            out[value] = name
    return out


def _op_names() -> dict[int, str]:
    return {value: name for name, value in pimasm.OPCODES.items()}


def _bits(hi: int, lo: int) -> str:
    return f"{hi}:{lo}" if hi != lo else str(hi)


def _mask(hi: int, lo: int) -> int:
    return ((1 << (hi - lo + 1)) - 1) << lo


def _micro_probe(**kwargs: int) -> "pimasm.Micro":
    base = dict(
        next=0, imm=0, alu=0, srcA=0, srcB=0, dst=0, mem=0, cond=0,
        deref=False, halt=False, mrb_set=False, mrb_clr=False,
        last=False, branch=False,
    )
    base.update(kwargs)
    return pimasm.Micro(**base)


def _check(packer, kw: dict, hi: int, lo: int, label: str) -> None:
    word = packer(**kw)
    mask = _mask(hi, lo)
    if word & ~mask:
        raise SystemExit(
            f"layout check failed: {label} sets bits outside {hi}:{lo}")
    value = (word >> lo) & ((1 << (hi - lo + 1)) - 1)
    if value != 1:
        raise SystemExit(
            f"layout check failed: {label} value {value} != 1")


def verify() -> None:
    missing = set(pimasm.OPCODES) - set(FORMS)
    extra = set(FORMS) - set(pimasm.OPCODES)
    if missing or extra:
        raise SystemExit(
            f"FORMS coverage: missing={sorted(missing)} extra={sorted(extra)}")

    instr_base = {"op": 0, "rd": 0, "rs": 0, "rt": 0, "imm": 0}
    for name, hi, lo, _ in INSTR_FIELDS:
        probe = dict(instr_base)
        probe[name] = 1
        _check(pimasm.pack_instr, probe, hi, lo, f"instr.{name}")
    decode_base = {"u_base": 0, "valid": 0, "needs_ea": 0, "is_load": 0,
                   "is_store": 0, "deref": 0}
    for display, param, hi, lo, _ in DECODE_FIELDS:
        probe = dict(decode_base)
        probe[param] = 1
        _check(lambda **k: pimasm.pack_decode(**k), probe, hi, lo,
               f"decode.{display}")
    for name, hi, lo, _ in MICRO_FIELDS:
        _check(lambda **k: pimasm.pack_micro(_micro_probe(**k)),
               {name: 1}, hi, lo, f"micro.{name}")


def _table(header: list[str], rows: list[list[str]]) -> list[str]:
    out = ["| " + " | ".join(header) + " |",
           "|" + "|".join("---" for _ in header) + "|"]
    for row in rows:
        out.append("| " + " | ".join(row) + " |")
    return out


def _flags(micro: "pimasm.Micro") -> str:
    set_flags = [
        name for name in ("deref", "halt", "mrb_set", "mrb_clr", "last",
                          "branch")
        if getattr(micro, name)
    ]
    return ", ".join(f"`{name}`" for name in set_flags) or "—"


def render() -> str:
    ops = _op_names()
    alu = _names("ALU_")
    mem = _names("MEM_")
    cond = _names("COND_")
    rsel = _names("RSEL_")
    tags = sorted(pimasm.TAG_NAMES.items(), key=lambda kv: kv[1])

    lines: list[str] = []
    lines.append("# PIM/m model ISA")
    lines.append("")
    lines.append("Generated from `asm/pimasm.py` by `asm/gen_isa_table.py`.")
    lines.append("The encodings are the model's own, not historical PIM/m")
    lines.append("encodings. The 1992 sources give the 40-bit word, the 8-bit")
    lines.append("tag, the 32K x 64-bit WCS and the five-stage pipeline, but")
    lines.append("not the bit assignments. KL1-B's encoding is not in the")
    lines.append("corpus; see [Gaps](#gaps).")
    lines.append("")

    lines.append("## Word format (40 bits)")
    lines.append("")
    lines.extend(_table(
        ["field", "bits", "width", "meaning"],
        [[f"`{name}`", _bits(hi, lo), str(hi - lo + 1), meaning]
         for name, hi, lo, meaning in INSTR_FIELDS],
    ))
    lines.append("")

    lines.append("## Machine opcodes")
    lines.append("")
    rows = []
    for op in sorted(ops):
        mnem = ops[op]
        operands, semantics = FORMS[mnem]
        rows.append([f"`{mnem}`", f"`0x{op:02x}`", operands or "—",
                     semantics])
    lines.extend(_table(["mnemonic", "opcode", "operands", "semantics"], rows))
    lines.append("")

    lines.append("## Tags")
    lines.append("")
    lines.extend(_table(
        ["tag", "value"],
        [[f"`{name}`", str(value)] for name, value in tags],
    ))
    lines.append("")

    lines.append("## ALU operations")
    lines.append("")
    lines.extend(_table(
        ["operation", "value"],
        [[f"`{name}`", str(value)] for value, name in sorted(alu.items())],
    ))
    lines.append("")

    lines.append("## Memory operations")
    lines.append("")
    lines.extend(_table(
        ["operation", "value"],
        [[f"`{name}`", str(value)] for value, name in sorted(mem.items())],
    ))
    lines.append("")

    lines.append("## Conditions")
    lines.append("")
    lines.extend(_table(
        ["condition", "value"],
        [[f"`{name}`", str(value)] for value, name in sorted(cond.items())],
    ))
    lines.append("")

    lines.append("## Register selectors")
    lines.append("")
    lines.extend(_table(
        ["selector", "value"],
        [[f"`{name}`", str(value)] for value, name in sorted(rsel.items())],
    ))
    lines.append("")
    lines.append("The register file is 32 entries: `a0`-`a15` are 0-15 and")
    lines.append("`x0`-`x15` are 16-31.")
    lines.append("")

    lines.append("## Decode entry (20 bits)")
    lines.append("")
    lines.extend(_table(
        ["field", "bits", "width", "meaning"],
        [[f"`{display}`", _bits(hi, lo), str(hi - lo + 1), meaning]
         for display, _param, hi, lo, meaning in DECODE_FIELDS],
    ))
    lines.append("")
    lines.append("Decode flags per opcode; an opcode without an explicit")
    lines.append("entry has all flags clear.")
    lines.append("")
    default = dict(needs_ea=False, is_load=False, is_store=False, deref=False)
    rows = []
    for op in sorted(pimasm.MICRO_ROUTINES):
        flags = pimasm.DECODE_FLAGS.get(op, default)
        rows.append([
            f"`{ops[op]}`",
            "yes" if flags["needs_ea"] else "no",
            "yes" if flags["is_load"] else "no",
            "yes" if flags["is_store"] else "no",
            "yes" if flags["deref"] else "no",
        ])
    lines.extend(_table(
        ["opcode", "needs_ea", "is_load", "is_store", "deref"], rows))
    lines.append("")

    lines.append("## Microinstruction (64 bits)")
    lines.append("")
    lines.extend(_table(
        ["field", "bits", "width", "meaning"],
        [[f"`{name}`", _bits(hi, lo), str(hi - lo + 1), meaning]
         for name, hi, lo, meaning in MICRO_FIELDS],
    ))
    lines.append("")

    lines.append("## Micro routines")
    lines.append("")
    rows = []
    for op in sorted(pimasm.MICRO_ROUTINES):
        micro = pimasm.MICRO_ROUTINES[op]
        rows.append([
            f"`{ops[op]}`",
            f"`0x{micro.next:04x}`",
            f"`0x{micro.imm:04x}`",
            f"`{alu.get(micro.alu, micro.alu)}`",
            f"`{rsel.get(micro.srcA, micro.srcA)}`",
            f"`{rsel.get(micro.srcB, micro.srcB)}`",
            f"`{rsel.get(micro.dst, micro.dst)}`",
            f"`{mem.get(micro.mem, micro.mem)}`",
            f"`{cond.get(micro.cond, micro.cond)}`",
            _flags(micro),
        ])
    lines.extend(_table(
        ["opcode", "next", "imm", "alu", "srcA", "srcB", "dst", "mem",
         "cond", "flags"], rows))
    lines.append("")

    lines.append("## Images")
    lines.append("")
    lines.append("`pimasm.py --out-dir <dir>` writes the assembled image:")
    lines.append("")
    lines.append("- `program.hex`: 64K words of 40 bits.")
    lines.append("- `wcs.hex`: 32K microinstructions of 64 bits.")
    lines.append("- `decode.hex`: 256 decode entries of 20 bits.")
    lines.append("- `jump.hex`: 256 tag-indexed microprogram offsets of 15 bits.")
    lines.append("- `program.lst`: listing with PC, machine word and source.")
    lines.append("")

    lines.append("## Gaps")
    lines.append("")
    lines.append("- **KL1-B encoding.** The model ISA is a diagnostic stand-in.")
    lines.append("  The sources name KL1-B and binary compatibility with")
    lines.append("  Multi-PSI but do not publish the instruction layout,")
    lines.append("  opcode table or register-field widths. Do not call these")
    lines.append("  images PIM/m machine code. See")
    lines.append("  `docs/pim_architecture.md` \"Not stated\" and `plan.md`")
    lines.append("  WP1.2.")
    lines.append("- **Tag layout.** The 8-bit tag's internal field layout and")
    lines.append("  the MRB bit position are not stated in the sources.")
    lines.append("- **Microinstruction layout.** The 64-bit field layout and")
    lines.append("  the nano-code and decode-table widths are model-defined.")
    lines.append("- **Jump table.** The multi-way jump base and the")
    lines.append("  jump-table encoding are unconfirmed.")
    lines.append("")
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args(argv)
    verify()
    text = render()
    if args.check:
        if not DOC.exists():
            print(f"missing {DOC}", file=sys.stderr)
            return 1
        old = DOC.read_text()
        if old != text:
            print(f"{DOC} is stale; run python3 asm/gen_isa_table.py",
                  file=sys.stderr)
            sys.stderr.writelines(difflib.unified_diff(
                old.splitlines(True), text.splitlines(True),
                "docs/isa.md", "generated"))
            return 1
        print(f"{DOC}: up to date")
        return 0
    DOC.write_text(text)
    print(f"wrote {DOC}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
