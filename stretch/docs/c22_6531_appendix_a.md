# C22-6531 Appendix A — the normative mnemonic list

`docs/C22-6531_7030xasm-sim_1960.pdf`, *7030 Symbolic Assembly
Program / Simulator* (1960). **PDF page = printed page + 1.**

| printed | PDF | content |
|---|---|---|
| 57 | 58 | ALPHABETIC LIST OF OPERATIONS, both columns (`+` … `SRD`) |
| 58 | 59 | the list's tail (`SRT` … `Z`) and the twelve FOOTNOTES |

This appendix is the only place in the corpus that gives, for **every
STRAP-1 mnemonic**, a TYPE letter and a FOOTNOTE number. It is
therefore a normative cross-check for `strap/opcodes.py` — the one
`strap/README.md`'s "Next steps" item 2 asks for, and the reason this
note exists. It was read to settle `LFI` on MCP printed p.18; the
rest has not been transcribed, and transcribing it is cheap now that
the offset is written down.

## The footnotes, read at 400 dpi

Verbatim, in full, because four of them are the whole mnemonic
grammar this assembler implements:

1. This mnemonic is a system symbol. It must be prefixed by the
   character "$" whenever used.
2. This mnemonic is both an indicator mnemonic and a system symbol…
   may also be used directly to express a Branch on Indicator
   instruction by being substituted for the letter "I" in any of the
   following four formats: **BI**, **BIZ**, **BZI**, **BZIZ**. "The
   mnemonics BI, BIZ, BZI, BZIZ are not in themselves legal operation
   codes. Any of the integers 0 through 63 may also be substituted
   for I if it is desired to designate an indicator numerically."
3. **"This operation code may be suffixed by the letter 'I' to invoke
   immediate addressing."**
4. This VFL operation code may have the following suffixes:
   **I** Immediate, **N** Negative, **NI** Negative Immediate.
5. …suffixed by the letter "N" to invoke the negative sign modifier.
6. This floating point operation code may be suffixed by the letter
   "A" to invoke the absolute sign modifier.
7. This floating point operation code may have the following
   suffixes: **N** Negative, **A** Absolute, **NA** Negative Absolute.
8. Count and Branch operation may have the following suffixes:
   **+** Add one to value, **-** Subtract one from value,
   **H** Add half to value.
9. This operation code may be used to indicate either an immediate
   indexing operation or the secondary operation of any VFL
   instruction.
10. **"This operation mnemonic specifies, potentially, 16 connect
    instructions. Four binary digits are written directly after the
    operation code to select a particular one of the 16 instructions.
    This operation code is also subject to Footnote 3."**
11. This code may be used as a secondary operation with I-O select
    orders that are subject to end-of-operation interrupts.
12. These mnemonics are mathematical constants.

## What it settled, and what it corrected

**`LFI` is legal.** Footnote 10 is the one `C`, `CM` and `CT` carry,
and it ends by making them subject to footnote 3's `I` suffix. `LF`
is the connective `C0011` (`strap_asm.py`'s `CONNECTIVE_ALIASES`,
recovered from MCP printed p.5 line 12), so `LFI` is `LF` with
immediate addressing — which is what MCP printed p.18 line 34 is, and
the assembler now accepts it.

**`SF` IS in the manual.** `strap_asm.py` used to say "SF (Store
Field) is deliberately absent"; printed p.57 lists `V  SF  Store
Field` directly under `V  LF  Load Field`. What the table does not
give is either one's connective *number*, so SF is still absent from
this assembler for the original reason — the number would be a guess
— but the claim about the manual was wrong and has been corrected in
place.

**THE TABLE IS INCOMPLETE ABOUT `LF`, AND THAT IS WORTH KNOWING
BEFORE ANYONE USES IT AS AN ORACLE.** `LF`'s and `SF`'s footnote
columns are BLANK, where `C`, `CM` and `CT` all carry 10 — and the
table gives no hint that `LF` is a connective at all, listing it as a
plain type-V operation. So a blank in the footnote column is not
evidence that a suffix is illegal; it may simply be a row the
compiler of the table did not finish. Any future exhaustive check of
`opcodes.py` against this appendix has to treat *disagreements about
footnotes* as questions, not as findings.

## Other rows worth having noticed

- `I RNX  Rename` — the operation `audit_opcode_coverage.py` lists as
  a known gap has a name and a type here.
- `E SEOP  Suppress End of Operation`, footnote 11: a **secondary**
  operation on I-O select orders. That is the `(SEOP)` modifier the
  MCP pages write on `RD`, `W`, `CTL` and `LOC`.
- `V LFT  Load Factor` **and** `F LFT  Load Factor` — the same
  mnemonic in both the VFL and floating-point tables, which is why
  `classify_vfl_or_fp` has to disambiguate by data description.
