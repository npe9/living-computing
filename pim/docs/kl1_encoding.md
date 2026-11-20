# KL1-B instruction encodings from the PIMOS assembler

Source note for the PIM/m reproduction. This document transcribes the
instruction encoding table and operand packing rules from the PIMOS
source archive, which is a primary source: ICOT's own assembler for the
KL1-B virtual machine that PIMOS runs. It closes the "no KL1-B encoding
table" gap recorded in `kl1_architecture.md` §8 and `plan.md` Stage 6.

## Provenance

| Artifact | Location | Contents |
|---|---|---|
| `pimos.tar.Z` | `docs/nonlocal/pimos.tar.Z` (2,932,865 bytes) | PIMOS source, 706 files, (C)1992 ICOT |
| `inst_tab.kl1` | `pimos/src/library/assembler/inst_tab.kl1` | 263 instruction encodings: mnemonic, 16-bit tag, 8-bit opcode, operand type |
| `klb_opr.kl1` | `pimos/src/library/assembler/klb_opr.kl1` | operand packing rules (`p/7` and `p/11` clauses) |
| `assemble.kl1` | `pimos/src/library/assembler/assemble.kl1` | module layout, predicate heads, code area |

All three files carry the header `(C)1992 Institute for New Generation
Computer Technology`. The archive is the same one cited in
`docs/README.md` as the PIMOS source (`nonlocal/pimos.tar.Z`).

The assembler is a KL1 program (`kl1_self_assembler`), so its table is
executable evidence rather than a prose transcription: the encodings
below are what ICOT's assembler actually emitted.

## Instruction format

The assembler's internal representation is a tagged word: an 8-bit tag
and a 32-bit data word (`Word = 1`), or a second 32-bit word for wide
operands (`Word = 2`). The tag value `16#"23"` marks the core KL1-B set
and `16#"22"` the extended set; both fit in 8 bits. This matches
TR-389 p. 9's 40-bit KL1 data (8-bit tag, 32-bit value) rather than a
16-bit prefix.

| Field | Bits | Meaning |
|---|---|---|
| Tag | 8 bits | `16#"23"` for the core KL1-B set, `16#"22"` for the extended set |
| Opcode | data word bits 31–24 | the one-byte operation code from the table |
| Operand | data word bits 23–0 | up to three 8-bit fields, or a 16/24-bit constant |

The assembler's `{Tag, Op}` pair is its internal list representation; the
byte serialization to the loader is not shown in these clauses and is
not claimed here.

The packing rules in `klb_opr.kl1` are literal:

- `p(no, ...)`: `Op := Opcode<<24`, one word, no operand.
- `p(c8, ...)`: opcode in bits 31–24, 8-bit value in bits 23–16.
- `p(c16, ...)`: opcode in bits 31–24, 16-bit constant in bits 15–0.
- `p(c24, ...)`: opcode in bits 31–24, 24-bit constant in bits 23–0.
- `p(r, ...)`: opcode in bits 31–24, register in bits 23–16.
- `p(r_r, ...)`: opcode 31–24, reg1 23–16, reg2 15–8.
- `p(r_r_r, ...)`: opcode 31–24, reg1 23–16, reg2 15–8, reg3 7–0.
- `p(c40, ...)`: two words; the second word holds the 40-bit constant.
- `p(c8_c16, ...)`: opcode 31–24, 8-bit field 23–16, 16-bit constant 15–0.
- `p(c8_r, ...)`: opcode 31–24, 8-bit field 23–16, register 15–8.
- `p(r_c16, ...)`: opcode 31–24, register 23–16, 16-bit constant 15–0.
- `p(r_c40, ...)`: two words; register and 40-bit constant.
- `p(r_vector, ...)`: opcode 31–24, register 23–16, vector length in the low bits; length > 6 uses a second word.

The `c8_c16_exe`, `r_c16_i`, `r_r_c16_i`, `c16_exe`, `r_c16_c8_exe`,
`c8_c16_ext`, `r_c16_c8_ext`, `r_c16_scnst`, `label`,
`r_c16_c16_16s_sw` and `r_c16_c16_16s_ha` types add address or label
resolution on top of the same field layout; they are defined in
`klb_opr.kl1` lines 310–500.
Two of them are longer than one word. `r_r_c16_i` is two words: opcode
31–24, reg1 23–16, reg2 15–8 in the first and the label alone in the
second (`klb_opr.kl1` lines 334–348). `r_c16_c16_16s_sw` is
`2*Length + 1` words: opcode 31–24, register 23–16, entry count in the
low bits, then per entry the constant and a data word with the else
label in bits 31–16 and the entry's label in bits 15–0 (lines 470–482,
504–535).

### Length reconciliation

TR-389 p. 11 states instruction lengths of four, six, or eight bytes.
The assembler's clauses emit tagged words: a tag plus one 32-bit data
word for `Word = 1`, and a second 32-bit word for `Word = 2`. If each
word is a 40-bit tagged word (TR-389 p. 9), one instruction is five or
ten bytes, which does not match the printed four/six/eight counts. The
assembler's byte serialization to the loader is not shown in the clauses
read here, so the mapping from these tagged words to TR-389's byte
lengths is unresolved. The discrepancy is recorded rather than smoothed
over. A future check should compare an assembled module's byte stream
against a printed listing, if one survives.

## The table

Every entry below is a literal `t(...)` clause from `inst_tab.kl1`.
`Tag` is the 16-bit tag word; `Op` is the one-byte opcode; `Type` is the
operand type that selects a `p(...)` clause in `klb_opr.kl1`.

| Mnemonic | Tag | Op | Operand type |
|---|---|---|---|
| `set_atom` | `16#"23"` | `16#"00"` | `atom` |
| `set_constant` | `16#"23"` | `16#"10"` | `c8_c40` |
| `set_integer` | `16#"23"` | `16#"11"` | `c8_c16` |
| `set_nil` | `16#"23"` | `16#"12"` | `c8` |
| `set_variable` | `16#"23"` | `16#"13"` | `c8_r` |
| `set_value` | `16#"23"` | `16#"14"` | `c8_r` |
| `set_marked_variable` | `16#"23"` | `16#"15"` | `c8_r` |
| `set_marked_value` | `16#"23"` | `16#"16"` | `c8_r` |
| `set_list` | `16#"23"` | `16#"18"` | `c8` |
| `save` | `16#"23"` | `16#"19"` | `r_c16` |
| `restore` | `16#"23"` | `16#"1a"` | `r_c16` |
| `clause_info` | `16#"23"` | `16#"1b"` | `c24` |
| `mark_element` | `16#"23"` | `16#"1c"` | `r_r` |
| `collect_value` | `16#"23"` | `16#"1d"` | `r` |
| `collect_list` | `16#"23"` | `16#"1e"` | `r` |
| `collect_vector` | `16#"23"` | `16#"1f"` | `r_c16` |
| `write_constant` | `16#"23"` | `16#"20"` | `c40` |
| `write_integer` | `16#"23"` | `16#"21"` | `c24` |
| `write_nil` | `16#"23"` | `16#"22"` | `no` |
| `write_atom` | `16#"23"` | `16#"23"` | `atom_no_length` |
| `write_variable` | `16#"23"` | `16#"24"` | `r` |
| `write_value` | `16#"23"` | `16#"25"` | `r` |
| `write_marked_variable` | `16#"23"` | `16#"26"` | `r` |
| `write_marked_value` | `16#"23"` | `16#"27"` | `r` |
| `switch_on_non_integer` | `16#"23"` | `16#"28"` | `r_c16_i` |
| `switch_on_non_atom` | `16#"23"` | `16#"29"` | `r_c16_i` |
| `switch_on_non_list` | `16#"23"` | `16#"2a"` | `r_c16_i` |
| `switch_on_non_vector` | `16#"23"` | `16#"2b"` | `r_r_c16_i` |
| `switch_on_constant` | `16#"23"` | `16#"2c"` | `r_c16_c16_16s_sw` |
| `hash_on_constant` | `16#"23"` | `16#"2d"` | `r_c16_c16_16s_ha` |
| `put_list` | `16#"23"` | `16#"2e"` | `r` |
| `put_reused_structure` | `16#"23"` | `16#"2f"` | `r_r_c8` |
| `put_constant` | `16#"23"` | `16#"30"` | `r_c40` |
| `put_integer` | `16#"23"` | `16#"31"` | `r_c16` |
| `put_nil` | `16#"23"` | `16#"32"` | `r` |
| `put_variable` | `16#"23"` | `16#"33"` | `r_r` |
| `put_value` | `16#"23"` | `16#"34"` | `r_r` |
| `put_marked_variable` | `16#"23"` | `16#"35"` | `r_r` |
| `put_marked_value` | `16#"23"` | `16#"36"` | `r_r` |
| `put_structured_constant` | `16#"23"` | `16#"37"` | `r_c16_scnst` |
| `put_vector` | `16#"23"` | `16#"3f"` | `r_vector` |
| `put_atom` | `16#"23"` | `16#"40"` | `atom` |
| `proceed` | `16#"23"` | `16#"60"` | `no` |
| `execute` | `16#"23"` | `16#"61"` | `c8_c16_exe` |
| `execute_external` | `16#"23"` | `16#"62"` | `c8_c16_ext` |
| `enqueue_goal` | `16#"23"` | `16#"63"` | `c8_c16_exe` |
| `enqueue_goal_with_priority` | `16#"23"` | `16#"64"` | `r_c16_c8_exe` |
| `enqueue_goal_to_processor` | `16#"23"` | `16#"65"` | `r_c16_c8_exe` |
| `enqueue_goal_external` | `16#"23"` | `16#"66"` | `c8_c16_ext` |
| `jump` | `16#"23"` | `16#"67"` | `c16_exe` |
| `try_me_else` | `16#"23"` | `16#"68"` | `c16_exe` |
| `suspend` | `16#"23"` | `16#"69"` | `c8_c16_exe` |
| `otherwise` | `16#"23"` | `16#"6a"` | `c8_c16_exe` |
| `read_eagerly` | `16#"23"` | `16#"6b"` | `no` |
| `extended_floating_point_equal` | `16#"23"` | `16#"6e"` | `f_r_r(0)` |
| `extended_floating_point_not_equal` | `16#"23"` | `16#"6e"` | `f_r_r(1)` |
| `extended_floating_point_less_than` | `16#"23"` | `16#"6e"` | `f_r_r(2)` |
| `extended_floating_point_not_less_than` | `16#"23"` | `16#"6e"` | `f_r_r(3)` |
| `extended_floating_point_to_integer` | `16#"23"` | `16#"6e"` | `f_r_r(4)` |
| `integer_to_extended_floating_point` | `16#"23"` | `16#"6e"` | `f_r_r(5)` |
| `extended_floating_point_to_floating_point` | `16#"23"` | `16#"6e"` | `f_r_r(6)` |
| `floating_point_to_extended_floating_point` | `16#"23"` | `16#"6e"` | `f_r_r(7)` |
| `extended_floating_point` | `16#"23"` | `16#"6e"` | `f_r_r(8)` |
| `extended_floating_point_add` | `16#"23"` | `16#"6f"` | `f_r_r_r(0)` |
| `extended_floating_point_subtract` | `16#"23"` | `16#"6f"` | `f_r_r_r(1)` |
| `extended_floating_point_multiply` | `16#"23"` | `16#"6f"` | `f_r_r_r(2)` |
| `extended_floating_point_divide` | `16#"23"` | `16#"6f"` | `f_r_r_r(3)` |
| `nop` | `16#"23"` | `16#"70"` | `no` |
| `halt` | `16#"23"` | `16#"71"` | `r` |
| `fail` | `16#"23"` | `16#"73"` | `no` |
| `set_gevc_increment_bits` | `16#"23"` | `16#"74"` | `r_r` |
| `reset_gevc_increment_bits` | `16#"23"` | `16#"75"` | `r_r` |
| `export_entry` | `16#"23"` | `16#"76"` | `f_r_r_r(0)` |
| `import_entry` | `16#"23"` | `16#"76"` | `f_r_r_r(1)` |
| `structure_entry` | `16#"23"` | `16#"76"` | `f_r_r_r(2)` |
| `free_list_top_address` | `16#"23"` | `16#"76"` | `f_r_r(3)` |
| `tag_and_value` | `16#"23"` | `16#"76"` | `f_r_r_r(4)` |
| `word` | `16#"23"` | `16#"76"` | `f_r_r_r(5)` |
| `set_word` | `16#"23"` | `16#"76"` | `f_r_r_r(6)` |
| `register_tag_and_value` | `16#"23"` | `16#"76"` | `f_r_r_r(7)` |
| `collect_garbage` | `16#"23"` | `16#"77"` | `no` |
| `system_timer` | `16#"23"` | `16#"78"` | `r_r` |
| `execute_first_predicate` | `16#"23"` | `16#"79"` | `no` |
| `increment_resource_by_one` | `16#"23"` | `16#"7a"` | `no` |
| `start` | `16#"23"` | `16#"7b"` | `no` |
| `get_console` | `16#"23"` | `16#"7c"` | `r` |
| `put_console` | `16#"23"` | `16#"7d"` | `r` |
| `read_console` | `16#"23"` | `16#"7e"` | `r` |
| `display_console` | `16#"23"` | `16#"7f"` | `r` |
| `wait_atom` | `16#"23"` | `16#"80"` | `atom` |
| `wait_constant` | `16#"23"` | `16#"a0"` | `r_c40` |
| `wait_integer` | `16#"23"` | `16#"a1"` | `r_c16` |
| `wait_nil` | `16#"23"` | `16#"a2"` | `r` |
| `wait_value` | `16#"23"` | `16#"a4"` | `r_r` |
| `wait_different_value` | `16#"23"` | `16#"a5"` | `r_r` |
| `wait_list` | `16#"23"` | `16#"a6"` | `r` |
| `read_variable_without_deref` | `16#"23"` | `16#"a7"` | `r` |
| `wait_vector_0` | `16#"23"` | `16#"a8"` | `r_m` |
| `wait_vector` | `16#"23"` | `16#"af"` | `r_vector` |
| `read_constant` | `16#"23"` | `16#"b0"` | `c40` |
| `read_integer` | `16#"23"` | `16#"b1"` | `c24` |
| `read_nil` | `16#"23"` | `16#"b2"` | `no` |
| `read_atom` | `16#"23"` | `16#"b3"` | `atom_no_length` |
| `read_variable` | `16#"23"` | `16#"b4"` | `r` |
| `bignum_less_than` | `16#"23"` | `16#"b6"` | `r_r` |
| `bignum_not_less_than` | `16#"23"` | `16#"b7"` | `r_r` |
| `get_constant` | `16#"23"` | `16#"b8"` | `r_c40` |
| `get_integer` | `16#"23"` | `16#"b9"` | `r_c16` |
| `get_nil` | `16#"23"` | `16#"ba"` | `r` |
| `get_value` | `16#"23"` | `16#"bc"` | `r_r` |
| `get_bound_value` | `16#"23"` | `16#"bd"` | `r_r` |
| `get_atom` | `16#"23"` | `16#"c0"` | `atom` |
| `wait` | `16#"23"` | `16#"e0"` | `r` |
| `atom` | `16#"23"` | `16#"e1"` | `r` |
| `integer` | `16#"23"` | `16#"e2"` | `r` |
| `list` | `16#"23"` | `16#"e3"` | `r` |
| `vector` | `16#"23"` | `16#"e4"` | `r_r` |
| `string` | `16#"23"` | `16#"e5"` | `r_r_r` |
| `floating_point` | `16#"23"` | `16#"e6"` | `r` |
| `shift_left` | `16#"23"` | `16#"e8"` | `r_r_r` |
| `shift_right` | `16#"23"` | `16#"e9"` | `r_r_r` |
| `and` | `16#"23"` | `16#"ea"` | `r_r_r` |
| `or` | `16#"23"` | `16#"eb"` | `r_r_r` |
| `exclusive_or` | `16#"23"` | `16#"ec"` | `r_r_r` |
| `complement` | `16#"23"` | `16#"ed"` | `r_r` |
| `vector_element` | `16#"23"` | `16#"ee"` | `r_r_r` |
| `string_element` | `16#"23"` | `16#"ef"` | `r_r_r` |
| `less_than` | `16#"23"` | `16#"f0"` | `r_r` |
| `not_less_than` | `16#"23"` | `16#"f1"` | `r_r` |
| `equal` | `16#"23"` | `16#"f2"` | `r_r` |
| `not_equal` | `16#"23"` | `16#"f3"` | `r_r` |
| `add` | `16#"23"` | `16#"f4"` | `r_r_r` |
| `subtract` | `16#"23"` | `16#"f5"` | `r_r_r` |
| `multiply` | `16#"23"` | `16#"f6"` | `r_r_r` |
| `divide` | `16#"23"` | `16#"f7"` | `r_r_r` |
| `modulo` | `16#"23"` | `16#"f8"` | `r_r_r` |
| `diff` | `16#"23"` | `16#"f9"` | `r_r` |
| `code` | `16#"23"` | `16#"fa"` | `r4` |
| `module` | `16#"23"` | `16#"fb"` | `r_r` |
| `floating_point_equal` | `16#"23"` | `16#"fc"` | `f_r_r(0)` |
| `floating_point_not_equal` | `16#"23"` | `16#"fc"` | `f_r_r(1)` |
| `floating_point_less_than` | `16#"23"` | `16#"fc"` | `f_r_r(2)` |
| `floating_point_not_less_than` | `16#"23"` | `16#"fc"` | `f_r_r(3)` |
| `floating_point_to_integer` | `16#"23"` | `16#"fc"` | `f_r_r(4)` |
| `integer_to_floating_point` | `16#"23"` | `16#"fc"` | `f_r_r(5)` |
| `floating_point_add` | `16#"23"` | `16#"fd"` | `f_r_r_r(0)` |
| `floating_point_subtract` | `16#"23"` | `16#"fd"` | `f_r_r_r(1)` |
| `floating_point_multiply` | `16#"23"` | `16#"fd"` | `f_r_r_r(2)` |
| `floating_point_divide` | `16#"23"` | `16#"fd"` | `f_r_r_r(3)` |
| `string_less_than` | `16#"23"` | `16#"fe"` | `r_r` |
| `string_not_less_than` | `16#"23"` | `16#"ff"` | `r_r` |
| `scsi_where` | `16#"22"` | `16#"a0"` | `r` |
| `scsi_bus_reset` | `16#"22"` | `16#"a1"` | `r` |
| `string_operation` | `16#"22"` | `16#"b0"` | `r4` |
| `search_characters` | `16#"22"` | `16#"b1"` | `r7` |
| `log_event` | `16#"22"` | `16#"A2"` | `r` |
| `add_extended` | `16#"22"` | `16#"b2"` | `r4` |
| `subtract_extended` | `16#"22"` | `16#"b3"` | `r4` |
| `multiply_extended` | `16#"22"` | `16#"b4"` | `r4` |
| `divide_extended` | `16#"22"` | `16#"b5"` | `r5` |
| `add_bignum` | `16#"22"` | `16#"b6"` | `r_r_r` |
| `subtract_bignum` | `16#"22"` | `16#"b7"` | `r4` |
| `multiply_bignum_word` | `16#"22"` | `16#"b8"` | `r_r_r` |
| `supply_atom_number` | `16#"22"` | `16#"b9"` | `r_r_r` |
| `binary_to_extended_floating_point` | `16#"22"` | `16#"bc"` | `r4` |
| `extended_floating_point_to_binary` | `16#"22"` | `16#"bd"` | `r4` |
| `b_extended_floating_point_to_integer` | `16#"22"` | `16#"be"` | `f_r_r(0)` |
| `b_integer_to_extended_floating_point` | `16#"22"` | `16#"be"` | `f_r_r(1)` |
| `b_extended_floating_point_to_floating_point` | `16#"22"` | `16#"be"` | `f_r_r(2)` |
| `b_floating_point_to_extended_floating_point` | `16#"22"` | `16#"be"` | `f_r_r(3)` |
| `extended_floating_point_sinh` | `16#"22"` | `16#"be"` | `f_r_r(16#"22")` |
| `extended_floating_point_sqrt` | `16#"22"` | `16#"be"` | `f_r_r(16#"24")` |
| `extended_floating_point_lognp1` | `16#"22"` | `16#"be"` | `f_r_r(16#"26")` |
| `extended_floating_point_etoxm1` | `16#"22"` | `16#"be"` | `f_r_r(16#"28")` |
| `extended_floating_point_tanh` | `16#"22"` | `16#"be"` | `f_r_r(16#"29")` |
| `extended_floating_point_atan` | `16#"22"` | `16#"be"` | `f_r_r(16#"2a")` |
| `extended_floating_point_asin` | `16#"22"` | `16#"be"` | `f_r_r(16#"2c")` |
| `extended_floating_point_atanh` | `16#"22"` | `16#"be"` | `f_r_r(16#"2d")` |
| `extended_floating_point_sin` | `16#"22"` | `16#"be"` | `f_r_r(16#"2e")` |
| `extended_floating_point_tan` | `16#"22"` | `16#"be"` | `f_r_r(16#"2f")` |
| `extended_floating_point_etox` | `16#"22"` | `16#"be"` | `f_r_r(16#"30")` |
| `extended_floating_point_twotox` | `16#"22"` | `16#"be"` | `f_r_r(16#"31")` |
| `extended_floating_point_tentox` | `16#"22"` | `16#"be"` | `f_r_r(16#"32")` |
| `extended_floating_point_logn` | `16#"22"` | `16#"be"` | `f_r_r(16#"34")` |
| `extended_floating_point_log10` | `16#"22"` | `16#"be"` | `f_r_r(16#"35")` |
| `extended_floating_point_log2` | `16#"22"` | `16#"be"` | `f_r_r(16#"36")` |
| `extended_floating_point_abs` | `16#"22"` | `16#"be"` | `f_r_r(16#"38")` |
| `extended_floating_point_cosh` | `16#"22"` | `16#"be"` | `f_r_r(16#"39")` |
| `extended_floating_point_neg` | `16#"22"` | `16#"be"` | `f_r_r(16#"3a")` |
| `extended_floating_point_acos` | `16#"22"` | `16#"be"` | `f_r_r(16#"3c")` |
| `extended_floating_point_cos` | `16#"22"` | `16#"be"` | `f_r_r(16#"3d")` |
| `b_extended_floating_point_add` | `16#"22"` | `16#"bf"` | `f_r_r_r(0)` |
| `b_extended_floating_point_subtract` | `16#"22"` | `16#"bf"` | `f_r_r_r(1)` |
| `b_extended_floating_point_multiply` | `16#"22"` | `16#"bf"` | `f_r_r_r(2)` |
| `b_extended_floating_point_divide` | `16#"22"` | `16#"bf"` | `f_r_r_r(3)` |
| `b_add` | `16#"22"` | `16#"c0"` | `r_r_r` |
| `b_subtract` | `16#"22"` | `16#"c1"` | `r_r_r` |
| `b_multiply` | `16#"22"` | `16#"c2"` | `r_r_r` |
| `b_divide` | `16#"22"` | `16#"c3"` | `r_r_r` |
| `b_modulo` | `16#"22"` | `16#"c4"` | `r_r_r` |
| `b_shift_left` | `16#"22"` | `16#"c5"` | `r_r_r` |
| `b_shift_right` | `16#"22"` | `16#"c6"` | `r_r_r` |
| `b_and` | `16#"22"` | `16#"c7"` | `r_r_r` |
| `b_or` | `16#"22"` | `16#"c8"` | `r_r_r` |
| `b_exclusive_or` | `16#"22"` | `16#"c9"` | `r_r_r` |
| `b_vector` | `16#"22"` | `16#"ca"` | `r_r_r` |
| `b_string` | `16#"22"` | `16#"cb"` | `r4` |
| `b_vector_element` | `16#"22"` | `16#"cc"` | `r4` |
| `b_string_element` | `16#"22"` | `16#"cd"` | `r4` |
| `b_floating_point_to_integer` | `16#"22"` | `16#"ce"` | `f_r_r(0)` |
| `b_integer_to_floating_point` | `16#"22"` | `16#"ce"` | `f_r_r(1)` |
| `b_floating_point_add` | `16#"22"` | `16#"cf"` | `f_r_r_r(0)` |
| `b_floating_point_subtract` | `16#"22"` | `16#"cf"` | `f_r_r_r(1)` |
| `b_floating_point_multiply` | `16#"22"` | `16#"cf"` | `f_r_r_r(2)` |
| `b_floating_point_divide` | `16#"22"` | `16#"cf"` | `f_r_r_r(3)` |
| `set_vector_element` | `16#"22"` | `16#"d0"` | `r5` |
| `set_string_element` | `16#"22"` | `16#"d1"` | `r4` |
| `new_atom` | `16#"22"` | `16#"d2"` | `r` |
| `new_vector` | `16#"22"` | `16#"d3"` | `r_r` |
| `new_string` | `16#"22"` | `16#"d4"` | `r_r_r` |
| `new_instruction` | `16#"22"` | `16#"d5"` | `r_r_r` |
| `new_module` | `16#"22"` | `16#"d6"` | `r_r` |
| `copy_string_elements` | `16#"22"` | `16#"d7"` | `r7` |
| `move_string_elements` | `16#"22"` | `16#"d8"` | `r5` |
| `search_character` | `16#"22"` | `16#"d9"` | `r6` |
| `change_element_size` | `16#"22"` | `16#"da"` | `r_r_r` |
| `scsi_command` | `16#"22"` | `16#"db"` | `r7` |
| `scsi_transfer` | `16#"22"` | `16#"dc"` | `r6` |
| `scsi_abort` | `16#"22"` | `16#"dd"` | `r_r_r` |
| `scsi_reset` | `16#"22"` | `16#"de"` | `r4` |
| `scsi_init` | `16#"22"` | `16#"df"` | `r_r_r` |
| `create_shoen` | `16#"22"` | `16#"e0"` | `r7` |
| `start_shoen` | `16#"22"` | `16#"e1"` | `r_r` |
| `stop_shoen` | `16#"22"` | `16#"e2"` | `r_r` |
| `abort_shoen` | `16#"22"` | `16#"e3"` | `r_r` |
| `remove_shoen` | `16#"22"` | `16#"e4"` | `r` |
| `add_shoen_resource` | `16#"22"` | `16#"e5"` | `r4` |
| `shoen_statistics` | `16#"22"` | `16#"e6"` | `r_r` |
| `allow_shoen_resource_report` | `16#"22"` | `16#"e7"` | `r_r` |
| `consume_resource` | `16#"22"` | `16#"e8"` | `r` |
| `current_priority` | `16#"22"` | `16#"ea"` | `r_r_r` |
| `current_processor` | `16#"22"` | `16#"eb"` | `r_r_r` |
| `calculate_priority_from_current` | `16#"22"` | `16#"ec"` | `r_r` |
| `calculate_priority_from_minimum` | `16#"22"` | `16#"ed"` | `r_r` |
| `current_node` | `16#"22"` | `16#"ee"` | `r_r` |
| `unbound` | `16#"22"` | `16#"ef"` | `r_r` |
| `merge` | `16#"22"` | `16#"f0"` | `r_r` |
| `apply` | `16#"22"` | `16#"f1"` | `r_r` |
| `raise` | `16#"22"` | `16#"f2"` | `r_r_r` |
| `predicate_to_code` | `16#"22"` | `16#"f3"` | `r4` |
| `code_to_predicate` | `16#"22"` | `16#"f4"` | `r5` |
| `module_offset_to_code` | `16#"22"` | `16#"f5"` | `r_r_r` |
| `hash` | `16#"22"` | `16#"f6"` | `r_r_r` |
| `module_element` | `16#"22"` | `16#"f7"` | `r_r_r` |
| `apply_tracing` | `16#"22"` | `16#"f8"` | `r_r_r` |
| `apply_spying` | `16#"22"` | `16#"f9"` | `r4` |
| `create_profiling_shoen` | `16#"22"` | `16#"fa"` | `r7` |
| `shoen_profile` | `16#"22"` | `16#"fb"` | `r_r` |
| `set_heap_alert` | `16#"22"` | `16#"fd"` | `r_r` |
| `get_heap_size` | `16#"22"` | `16#"fe"` | `r_r` |
| `set_timer` | `16#"22"` | `16#"ff"` | `r_r` |
| `processor_profile` | `16#"22"` | `16#"fc"` | `r_r` |
| `modname_to_module` | `16#"22"` | `16#"ff"` | `r_r` |

## Quick / inline-atom forms

The assembler table contains explicit quick forms where the atom or
vector-length operand is encoded in the opcode byte itself.  These
reduce code size when the inline operand fits.  In the PIMOS source
they are shown as comments or `%`-commented-out clauses in
`inst_tab.kl1`; the assembler emits them in practice and they are
visible in the kernel `.sav` files.

| Family | Opcode range | Mnemonic pattern | Type |
|---|---|---|---|
| `set_atom` register forms | `0x01`–`0x0f` | `set_atom_1` … `set_atom_15` | `atom` (argument = opcode; the atom is the low 24 bits) |
| `put_atom` register forms | `0x41`–`0x5f` | `put_atom_1` … `put_atom_31` | `atom` (register = opcode – 0x40; the atom is the low 24 bits) |
| `get_atom` register forms | `0xc1`–`0xdf` | `get_atom_1` … `get_atom_31` | `atom` (register = opcode – 0xc0; the atom is the low 24 bits). Corrected 2026-11-20: this table said the opcode's low bits were the atom ID. In the IPL image `c300000c` is `get_atom r3, normal`, and it runs that way against its source (`ref/pimm/lockstep_ccode.py`); the same reading of the set/put/wait forms is by analogy, not yet run |
| `wait_atom` register forms | `0x81`–`0x9f` | `wait_atom_1` … `wait_atom_31` | `atom` (register = opcode – 0x80; the atom is the low 24 bits) |
| `put_vector` short forms | `0x38`–`0x3e` | `put_vector_0` … `put_vector_6` | `r_vector` |
| `wait_vector` short forms | `0xa9`–`0xae` | `wait_vector_1` … `wait_vector_6` | `r_m` |

(The `put_vector` / `wait_vector` families have a dedicated generic
opcode — `0x3f` for `put_vector`, `0xaf` for `wait_vector` — for
lengths that do not fit the inline range.)

## Opcode conflicts and gaps

- `0x19` is claimed by both `save` (`r_c16`) and the commented-out
  `set_reused_structure` (`c8_r`).  In current PIMOS `inst_tab.kl1`
  `save` is active and `set_reused_structure` is commented out.
- `0x17` (`set_vector`) and `0xa3`, `0xa7` (older gaps) are unused.
- `0xbe` and `0xbf` are unused in the core set (`0x23`).
- `0xbb` is unused in the core set.
