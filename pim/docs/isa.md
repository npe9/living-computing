# PIM/m model ISA

Generated from `asm/pimasm.py` by `asm/gen_isa_table.py`.
The encodings are the model's own, not historical PIM/m
encodings. The 1992 sources give the 40-bit word, the 8-bit
tag, the 32K x 64-bit WCS and the five-stage pipeline, but
not the bit assignments. KL1-B's encoding is in the corpus
(the PIMOS assembler's `inst_tab.kl1`, transcribed in
[`kl1_encoding.md`](kl1_encoding.md)) but is not implemented
in the model; see [Gaps](#gaps).

## Word format (40 bits)

| field | bits | width | meaning |
|---|---|---|---|
| `op` | 39:32 | 8 | machine opcode |
| `rd` | 31:27 | 5 | destination register |
| `rs` | 26:22 | 5 | first source register |
| `rt` | 21:17 | 5 | second source register or branch target |
| `imm` | 16:0 | 17 | immediate, offset, or tag |

## Machine opcodes

| mnemonic | opcode | operands | semantics |
|---|---|---|---|
| `nop` | `0x00` | — | do nothing |
| `halt` | `0x01` | — | halt the PE |
| `put_imm` | `0x02` | rd, imm | rd <- zero-extended 17-bit immediate |
| `put_reg` | `0x03` | rd, rs | rd <- rs |
| `get_arg` | `0x04` | rd, rs | rd <- rs (argument fetch in the model) |
| `add` | `0x05` | rd, rs, rt | rd <- rs + rt |
| `sub` | `0x06` | rd, rs, rt | rd <- rs - rt |
| `move` | `0x07` | rd, rs | rd <- rs |
| `load` | `0x08` | rd, [rs+imm] | rd <- memory[rs + imm] |
| `store` | `0x09` | rd, [rs+imm] | memory[rs + imm] <- rd |
| `deref` | `0x0a` | rd, rs | rd <- dereference(rs) |
| `set_mrb` | `0x0b` | rd | rd.tag.MRB <- 1 |
| `clr_mrb` | `0x0c` | rd | rd.tag.MRB <- 0 |
| `jmp` | `0x0d` | rt | branch to rt |
| `jmp_tag` | `0x0e` | rs, tag, rt | branch to rt if rs.tag == tag |

## Tags

| tag | value |
|---|---|
| `int` | 0 |
| `atom` | 1 |
| `ref` | 2 |
| `var` | 3 |
| `list` | 4 |
| `struct` | 5 |
| `code` | 6 |
| `float` | 7 |

## ALU operations

| operation | value |
|---|---|
| `ALU_ADD` | 0 |
| `ALU_SUB` | 1 |
| `ALU_AND` | 2 |
| `ALU_OR` | 3 |
| `ALU_XOR` | 4 |
| `ALU_MOV` | 5 |
| `ALU_SHL` | 6 |
| `ALU_SHR` | 7 |
| `ALU_EQ` | 8 |
| `ALU_NE` | 9 |
| `ALU_TAG_SET` | 10 |
| `ALU_TAG_CLR` | 11 |
| `ALU_NEG` | 12 |

## Memory operations

| operation | value |
|---|---|
| `MEM_NONE` | 0 |
| `MEM_READ` | 1 |
| `MEM_WRITE` | 2 |

## Conditions

| condition | value |
|---|---|
| `COND_ALWAYS` | 0 |
| `COND_NEVER` | 1 |
| `COND_TAG_EQ` | 2 |
| `COND_TAG_NE` | 3 |
| `COND_TAG_REF` | 4 |
| `COND_TAG_NOTREF` | 5 |
| `COND_MULTIWAY` | 6 |
| `COND_ZERO` | 7 |

## Register selectors

| selector | value |
|---|---|
| `RSEL_IMM` | 48 |
| `RSEL_RS` | 49 |
| `RSEL_RT` | 50 |
| `RSEL_RD` | 51 |
| `RSEL_FETCH` | 52 |
| `RSEL_DEREF` | 53 |
| `RSEL_NONE` | 63 |

The register file is 32 entries: `a0`-`a15` are 0-15 and
`x0`-`x15` are 16-31.

## Decode entry (20 bits)

| field | bits | width | meaning |
|---|---|---|---|
| `uBase` | 19:5 | 15 | microprogram base |
| `valid` | 4 | 1 | decode entry valid |
| `needsEA` | 3 | 1 | instruction needs an effective address |
| `isLoad` | 2 | 1 | load |
| `isStore` | 1 | 1 | store |
| `deref` | 0 | 1 | dereference |

Decode flags per opcode; an opcode without an explicit
entry has all flags clear.

| opcode | needs_ea | is_load | is_store | deref |
|---|---|---|---|---|
| `nop` | no | no | no | no |
| `halt` | no | no | no | no |
| `put_imm` | no | no | no | no |
| `put_reg` | no | no | no | no |
| `get_arg` | no | no | no | no |
| `add` | no | no | no | no |
| `sub` | no | no | no | no |
| `move` | no | no | no | no |
| `load` | yes | yes | no | no |
| `store` | yes | no | yes | no |
| `deref` | no | no | no | yes |
| `set_mrb` | no | no | no | no |
| `clr_mrb` | no | no | no | no |
| `jmp` | no | no | no | no |
| `jmp_tag` | no | no | no | no |

## Microinstruction (64 bits)

| field | bits | width | meaning |
|---|---|---|---|
| `next` | 63:49 | 15 | next micro-PC |
| `imm` | 48:33 | 16 | micro immediate |
| `alu` | 32:29 | 4 | ALU operation |
| `srcA` | 28:23 | 6 | A source selector |
| `srcB` | 22:17 | 6 | B source selector |
| `dst` | 16:11 | 6 | destination selector |
| `mem` | 10:9 | 2 | memory operation |
| `cond` | 8:6 | 3 | branch condition |
| `deref` | 5 | 1 | dereference |
| `halt` | 4 | 1 | halt |
| `mrb_set` | 3 | 1 | set MRB |
| `mrb_clr` | 2 | 1 | clear MRB |
| `last` | 1 | 1 | last microinstruction |
| `branch` | 0 | 1 | branch |

## Micro routines

| opcode | next | imm | alu | srcA | srcB | dst | mem | cond | flags |
|---|---|---|---|---|---|---|---|---|---|
| `nop` | `0x0000` | `0x0000` | `ALU_MOV` | `RSEL_NONE` | `RSEL_NONE` | `RSEL_NONE` | `MEM_NONE` | `COND_ALWAYS` | `last` |
| `halt` | `0x0000` | `0x0000` | `ALU_MOV` | `RSEL_NONE` | `RSEL_NONE` | `RSEL_NONE` | `MEM_NONE` | `COND_ALWAYS` | `halt`, `last` |
| `put_imm` | `0x0000` | `0x0000` | `ALU_MOV` | `RSEL_IMM` | `RSEL_NONE` | `RSEL_RD` | `MEM_NONE` | `COND_ALWAYS` | `last` |
| `put_reg` | `0x0000` | `0x0000` | `ALU_MOV` | `RSEL_RS` | `RSEL_NONE` | `RSEL_RD` | `MEM_NONE` | `COND_ALWAYS` | `last` |
| `get_arg` | `0x0000` | `0x0000` | `ALU_MOV` | `RSEL_RS` | `RSEL_NONE` | `RSEL_RD` | `MEM_NONE` | `COND_ALWAYS` | `last` |
| `add` | `0x0000` | `0x0000` | `ALU_ADD` | `RSEL_RS` | `RSEL_RT` | `RSEL_RD` | `MEM_NONE` | `COND_ALWAYS` | `last` |
| `sub` | `0x0000` | `0x0000` | `ALU_SUB` | `RSEL_RS` | `RSEL_RT` | `RSEL_RD` | `MEM_NONE` | `COND_ALWAYS` | `last` |
| `move` | `0x0000` | `0x0000` | `ALU_MOV` | `RSEL_RS` | `RSEL_NONE` | `RSEL_RD` | `MEM_NONE` | `COND_ALWAYS` | `last` |
| `load` | `0x0000` | `0x0000` | `ALU_MOV` | `RSEL_FETCH` | `RSEL_NONE` | `RSEL_RD` | `MEM_READ` | `COND_ALWAYS` | `last` |
| `store` | `0x0000` | `0x0000` | `ALU_MOV` | `RSEL_RD` | `RSEL_NONE` | `RSEL_NONE` | `MEM_WRITE` | `COND_ALWAYS` | `last` |
| `deref` | `0x0000` | `0x0000` | `ALU_MOV` | `RSEL_DEREF` | `RSEL_NONE` | `RSEL_RD` | `MEM_NONE` | `COND_ALWAYS` | `deref`, `last` |
| `set_mrb` | `0x0000` | `0x0000` | `ALU_TAG_SET` | `RSEL_RS` | `RSEL_NONE` | `RSEL_RD` | `MEM_NONE` | `COND_ALWAYS` | `last` |
| `clr_mrb` | `0x0000` | `0x0000` | `ALU_TAG_CLR` | `RSEL_RS` | `RSEL_NONE` | `RSEL_RD` | `MEM_NONE` | `COND_ALWAYS` | `last` |
| `jmp` | `0x0000` | `0x0000` | `ALU_MOV` | `RSEL_NONE` | `RSEL_NONE` | `RSEL_NONE` | `MEM_NONE` | `COND_ALWAYS` | `last`, `branch` |
| `jmp_tag` | `0x0000` | `0x0000` | `ALU_MOV` | `RSEL_RS` | `RSEL_NONE` | `RSEL_NONE` | `MEM_NONE` | `COND_TAG_EQ` | `last`, `branch` |

## Images

`pimasm.py --out-dir <dir>` writes the assembled image:

- `program.hex`: 64K words of 40 bits.
- `wcs.hex`: 32K microinstructions of 64 bits.
- `decode.hex`: 256 decode entries of 20 bits.
- `jump.hex`: 256 tag-indexed microprogram offsets of 15 bits.
- `program.lst`: listing with PC, machine word and source.

## Gaps

- **KL1-B encoding.** The model ISA is a diagnostic stand-in.
  The full KL1-B instruction set and encoding table is
  available (PIMOS-derived and documented in
  `kl1_encoding.md`), but it is not implemented in the
  model. Do not call these images PIM/m machine code until
  the full ISA is implemented. See
  `docs/pim_architecture.md` "Not stated" and `plan.md`
  WP1.2.
- **Tag layout.** The 8-bit tag's internal field layout and
  the MRB bit position are not stated in the sources.
- **Microinstruction layout.** The 64-bit field layout and
  the nano-code and decode-table widths are model-defined.
- **Jump table.** The multi-way jump base and the
  jump-table encoding are unconfirmed.
