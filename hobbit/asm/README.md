# Hobbit parcel assembler and disassembler

`hobbit_asm.py` assembles the ATT92010 Hobbit instruction set at parcel
level and disassembles the repository's image format.  It is Python 3
standard library only.  No encoding is invented: every form below is
transcribed from a printed page of the *ATT92010 Hobbit Microprocessor
Programmer's Reference Manual* (January 1993), with Plan 9's 1st Edition
linker as a second, code-level oracle.

## Command line

```
python3 hobbit/asm/hobbit_asm.py [-o IMAGE] [--list FILE]
                                 [--allow-unimplemented] INPUT
python3 hobbit/asm/hobbit_asm.py --disasm IMAGE [--list FILE]
```

* Without `-o`, the image is written to `INPUT` with its suffix replaced
  by `.hex` (`prog.s` -> `prog.hex`).
* `--list FILE` writes a listing with the byte address, all 16-bit
  parcels of each instruction, and the source text.
* `--disasm IMAGE` writes canonical assembly to standard output.  It
  cannot be combined with `-o`.
* Errors are reported as `file:line: error: ...` and exit nonzero.
* `--allow-unimplemented` is described under "Deliberate gaps".

## Image format

One 32-bit word per line, eight uppercase/lowercase hex digits, words in
increasing address order from address 0.  The parcel at an even address
is bits 31:16 of its word; the parcel at an odd address is bits 15:0.
Program entry is address 0.  A program with an odd number of parcels is
padded with one `NOP` (0x2C02, PRM p. 3-35) to complete the final 32-bit
word; the listing marks this line `; padding to a whole 32-bit image
word`.  Without that pad the low half of the last word would be an
imaginary parcel.

The disassembler decodes exactly the parcels present in the file.  A
padded file therefore shows the pad `NOP`; a reassembled disassembly
reproduces the same words.

## Source syntax

Comments run from `;` or `#` to end of line.  A label is
`name:` (letter or underscore first) on its own line or before an
instruction.  Labels resolve to byte addresses, and expressions may use
labels, integer literals, parentheses, and `+ - * / % << >> | & ^ ~`.
There is no data directive and no relocation: the input is a complete
absolute program.

### Mnemonics

All 46 entries and 60 spellings of Table 3-1 (printed pp. 3-1 to 3-2)
are accepted: the 35 dyadic grid names of Tables 1-18/1-20, the
monadics of Table 1-19, the niladics of Table 1-17, and the four
conditional jumps `JMPFN`, `JMPFY`, `JMPTN`, `JMPTY`.  The trailing-`3`
forms are written `ADD3`, `AND3`, `DIV3`, `MUL3`, `OR3`, `REM3`,
`SHL3`, `SHR3`, `SUB3`, `USHR3`, `XOR3`, exactly as the encoding tables
print them.  The manual's format notation `ADD[3]` is a description of
the optional accumulator form, not a second spelling; write `ADD3`.

`R4` is the stack slot the manual calls the integer accumulator
(PRM p. 1-7: "the word in memory above the word addressed by the
current stack pointer"); it is an ordinary stack offset in the operand
syntax.  The `3` instruction forms select it implicitly as destination.

### Operands

Operand suffixes are the Table 1-21 widths (printed p. 1-25): `:B`
(signed byte), `:UB` (unsigned byte), `:H` (signed half-word), `:UH`
(unsigned half-word), and `:W` (word, the default).  `:L` is accepted
as the same word width because the manual's pipeline example writes
`MOV R4:B, R8:L` (PRM p. 3-3); its own suffix list (printed p. 1-28)
uses `:W`.  Section 1.7 prints that list but omits `:H`; Table 1-21 has
mode codes 0x2/0x6/0xA for it, and the mode is implemented.

| syntax | mode (Table 1-21, p. 1-25) | meaning |
|---|---|---|
| `$expr[:w]` | 0xF | immediate; width is not encoded |
| `*$expr[:w]` | 0x0/1/2/3/0xC | absolute (the `*` is the manual's spelling) |
| `Rexpr[:w]` | 0x4/5/6/7/0xD | stack offset, signed |
| `*Rexpr[:w]` | 0x8/9/A/B/0xE | stack-offset indirect, signed |
| `%NAME` | 0x7 with CPU | internal register |

The CPU-modified modes (Table 1-22, printed p. 1-26) are register 0x7
plus only the word modes 0xC-0xF.  A non-word memory or immediate
operand alongside a `%register` is an error.  At most one register may
be *read* per instruction (PRM p. 1-27).  `MOV %SP,%SHAD` is legal: it
reads SP and writes SHAD, and it is the manual's own sequence after a
PSW change (PRM p. 1-15).  Other dyadics read their destination too, so
two register operands on `ADD`, `AND`, and the like are refused.
Registers are the printed names
of Table 1-24 (printed p. 1-26): `%MSP`, `%ISP`, `%SP`, `%CONFIG`,
`%PSW`, `%SHAD`, `%VB`, `%STB`, `%FAULT`, `%ID`, `%TIMER1`, `%TIMER2`.
Register 0 and codes 0xD-0xF have no name and are refused.

`%NAME` emits the `CPU` prefix automatically, so the manual's printed
examples work verbatim:

```
MOV $new,%SHAD
ADD $16,%SHAD
```

An explicit `CPU` line is also accepted.  The following instruction uses
the explicit prefix; no second `CPU` is emitted.  (The manual calls
`CPU` a prefix and says the PC covers four or six parcels after it,
PRM p. 3-14.)

### Control transfers

For `CALL`, `JMP`, the four conditional jumps, and `LDRAA`, Table 1-23
(printed p. 1-26) gives four ways to name the target:

| syntax | mode | Table 1-23 meaning |
|---|---|---|
| `label` or a bare absolute number | 0xE | program-counter relative |
| `*$expr` | 0xF | absolute |
| `**$expr` | 0xC | absolute indirect |
| `*Rexpr` | 0xD | stack-offset indirect |

The assembler computes the PC-relative offset from the instruction's own
address (PRM p. 1-27: the offset is added to "the address of the
instruction").  The one-parcel forms of `CALL` and the jumps use the
signed 10-bit offset multiplied by two (PRM p. 1-21); the assembler
chooses them when the offset is even and in -1024..1022.  A bare number
is a target address, not an offset.  Conditional jumps cannot use the
indirect modes (PRM p. 3-28), and are refused if given one.

`KCALL` is not in Table 1-23.  Its one-parcel form is a 10-bit immediate
multiplied by four (PRM p. 3-29: `KCALL $imm10`); its three-parcel form
uses the word32 modes `$imm`, `*$addr`, `Roff`, `*Roff` (PRM Table 3-2,
p. 3-4).

The one-parcel stack forms of `ENTER`, `CATCH`, `RETURN`, and `POPN`
use an 8-bit field multiplied by 16 (Table 1-16, p. 1-22; instruction
pages pp. 3-11, 3-21, 3-38, 3-40).  `ENTER`'s field is one-filled and
must be in -4096..-16; the other three are zero-extended and must be in
0..4080.  All four must be multiples of 16.  Other offsets fall back to
the three-parcel form automatically.

### Parcel-count selection and forcing

Without a directive the assembler chooses the shortest form that can
represent the operands:

1. one parcel when Table 1-15/1-16/1-17 has a matching form;
2. three parcels when every source/destination fits a 16-bit field
   (PRM p. 1-23: the fields are sign extended for immediate and offset
   modes);
3. five parcels otherwise (PRM pp. 1-24 to 1-25).

`.1`, `.3`, and `.5` before a mnemonic force that parcel count.  They
are an assembler extension, not PRM syntax, and exist so the
disassembler can reproduce a non-minimal encoding bit-exactly.  For
example `.3 CALL 0x002e` is the three-parcel `CALL` even though the
target is in one-parcel range.  A forced count that the instruction
does not have is an error.

## Deliberate gaps (fail loud)

The following are refused explicitly; no fallback or plausible guess is
emitted.

* **Cells the manual marks `unimp*`.**  Tables 1-15 (p. 1-22),
  1-18 (p. 1-23), and 1-20 (p. 1-25) mark cells whose unimplemented
  instruction sequence is performed.  They have no mnemonic here and
  no invented encoding.
* **Floating point.**  `FADD`, `FMUL`, `FSQRT`, and the other Plan 9
  floating-point names have no ATT92010 encoding: the 92010 PRM marks
  those opcode cells `unimp*` and traps.  They are refused even with
  `--allow-unimplemented`; Plan 9's `optab.c` keeps the CRISP names,
  but that is not a 92010 encoding.
* **`FLUSHD` and `FLUSHDCE`.**  The PRM prints encodings (pp. 3-22 and
  3-23) but says the part has no data cache and takes the
  unimplemented-instruction sequence.  By default the assembler refuses
  them with that page and reason.  `--allow-unimplemented` encodes the
  printed pattern and marks the listing `[unimplemented]`.
* **Data directives, relocations, macros, and section control** are not
  implemented.  The assembler emits instructions only.
* **Numeric or unknown register names** (`%3`, `%FOO`) are refused;
  only Table 1-24 names are accepted.
* **More than one register read**, a register without a word-sized
  companion mode, or a register in a form whose page forbids it is
  refused.  A `MOV` with one source register and one destination
  register is allowed because the destination is written, not read.
* **Immediate width on a 3/5-parcel instruction is not encodable.**
  Table 1-21 has a single immediate code 0xF; `$1:B` and `$1` produce
  the same parcel stream.  The suffix is accepted for source
  readability, but disassembly cannot recover it and prints `$1`.
* **`MOVA` restrictions**: an immediate or register source, a register
  destination, or a non-word source mode is refused (PRM p. 3-33).
* **`DQM` modes**: the source must be a word mode (0xC-0xF) and the
  destination one of the documented double/quad modes
  0x0/0x4/0x8/0xC/0xD/0xE; other combinations are refused (PRM p. 3-18).
* **`ENTER` stack offsets** must be negative; `ENTER R0` and positive
  stack offsets are refused (PRM p. 3-21).  `RETURN` and `POPN` stack
  offsets must be non-negative (PRM pp. 3-40, 3-38).
* **Conditional jumps with indirect modes** are refused (PRM p. 3-28).
* **Odd-byte PC-relative targets** for one-parcel `CALL`/`JMP` cannot be
  represented; they use the three-parcel form.

## Disassembler

Known forms are printed in a syntax that the assembler accepts.  Every
three- and five-parcel instruction is prefixed `.3` or `.5` so a
round-trip preserves its exact length.  PC-relative control transfers
are printed as bare target addresses.  A `CPU` prefix is printed as its
own line, followed by the instruction with `%NAME` operands.

Anything not decodable is printed with the literal word
`unimplemented`, the raw parcels, and the table/page or mode that
rejected it, for example

```
unimplemented 0x2000 ; one-parcel opcode 0x08 (Table 1-15, p. 1-22)
```

It never substitutes a mnemonic that happens to share the opcode.  A
niladic subcode in the `1xxxxxx` rows of Table 1-17 (printed p. 1-22)
is the documented trap through `VB+8` and prints `trapt`.  Truncated
three- or five-parcel instructions are errors, not partial guesses.

## Which PRM tables this implements

| table | printed page | use here |
|---|---|---|
| Table 1-15 | 1-22 | one-parcel monadic/dyadic opcodes and 5-bit source/destination fields |
| Table 1-16 | 1-22 | one-parcel stack subcodes |
| Table 1-17 | 1-22 | one-parcel niladic subcodes and traps |
| Table 1-18 | 1-23 | three-parcel opcode[5:0] grid |
| Table 1-19 | 1-24 | three-parcel monadic subcodes |
| Table 1-20 | 1-25 | five-parcel opcode[5:0] grid |
| Table 1-21 | 1-25 | general addressing-mode codes |
| Table 1-22 | 1-26 | CPU-modified addressing-mode codes |
| Table 1-23 | 1-26 | CALL/JMP/LDRAA addressing-mode codes |
| Table 1-24 | 1-26 | internal register codes |
| Table 3-1 | 3-1 to 3-2 | mnemonic inventory (46 entries, 60 spellings) |
| Table 3-2 | 3-4 | `gen16`/`gen32`/`word32`/`flow32`/`abs32`/`stk8`/`stk32` operand classes |

The format prose is PRM section 1.6.1 (p. 1-21: five-bit offsets
multiplied by four; 10-bit PC offsets multiplied by two), 1.6.2
(p. 1-23: three-parcel source and destination 16-bit fields), 1.6.3
(pp. 1-24 to 1-25: five-parcel hi/lo layout), and 1.7 (pp. 1-27 to
1-28: addressing modes and suffixes).  The instruction pages cited in
`hobbit_asm.py` supply each mnemonic's opcode, subcode, and operand
class; the per-instruction encoding blocks are the primary source for
the examples in the tests.

The Plan 9 cross-check is `tools/plan9-1e/sys/src/cmd/zl/optab.c`
(`genop` bytes) and `zl/asm.c` (`0x8000 | genop << 8` for three parcels,
`0xc000 | genop << 8` for five, and the one-parcel `decod` strings).  It
is used only to corroborate the PRM's opcode[5:0] field; it is not
AT&T's assembler and its mnemonic spellings are not treated as syntax.

## Cross-check against the hand-derived golden images

Every image in `tests/golden/` was written by hand from the PRM without
using this assembler.  Each one disassembles here, re-encodes, and
disassembles to the **same instruction stream**, which is an independent
confirmation of the field layout (the project's canonical form is chosen
on re-encoding, so the bytes can differ where the tables admit two
encodings of the same operation).

That duality is real and worth knowing: `MOV $8,R16` exists both as the
`wai5`/`stk5` one-parcel form `0x2844` (source field 8/4 = 2, p. 1-22:
one-parcel fields are scaled by four) and as the `imm5`/`stk5` form
`0x7104` (source field 8, unscaled).  Both are legal; only the tables
say which classes each opcode accepts, not that one spelling is unique.
`006.hex` contains `FLUSHD`, which is refused by default (the part
traps, p. 3-22) and assembles only with `--allow-unimplemented`.

## Tests

```
python3 hobbit/tests/test_hobbit_asm.py
```

Runs with `unittest` from any directory and exits 0 on success.  The
tests transcribe Tables 1-15 to 1-24 and compare all 35 grid mnemonics
in both three- and five-parcel form, check 31 hand-computed parcel
sequences with page citations, round-trip a mixed program through the
CLI, exercise malformed/truncated diagnostics, and compare every
assembled opcode field with `optab.c`.  The test header records the
observed failures when the one-parcel source/destination fields were
deliberately swapped.
