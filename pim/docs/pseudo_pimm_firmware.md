# The Pseudo PIM/m firmware archive: what has been read out of it

`docs/nonlocal/psdpim.tar.Z` is the Pseudo PIM/m: the PIM/m KL1
firmware and its console system for a PSI-III workstation (ICOT Free
Software, files dated 1991-94). Everything below describes that
system. PIM/m's processing element has the same processor as PSI-III
by the published papers (`literature_gaps.md` section 8), and this is
the firmware the PIMOS object files were run on, but none of it is a
measurement of a PIM/m.

`asm/psdpim.py` reads the archive; `asm/psdpim.py --check` (in
`run_tests.sh`) pins every count in this note. Looked at 2026-11-20,
time-boxed; the "Not read" list at the end is what stopped.

## 1. `pimm.MEkbn` begins with the instruction decode table

`PMPSI.DIR/pimm.MEkbn` is in the IPL image's container (`asm/kbn.py`):
100,864 five-byte words, value then tag byte; its header says load
address `0x4200`. Its first 2,048 words are 1,024 two-word entries
indexed by

    (low two bits of the instruction cell's tag) * 256 + opcode byte

so the four classes are PMI (tag `20`), BLT (`21`), GMI (`22`) and KLB
(`23`). An entry of `00002000:00 00000000:00` is "no such
instruction". This is the D-stage decode RAM the hardware papers
describe ("a RAM table for instruction decode, holding the microprogram
start address and the nano-code", TM-1074), found in the file; which
bits are the start address and which the nano-code is not worked out.

The reading is checked in both directions against
`docs/kl1_encoding.md`, which was built from the PIMOS assembler's
source and knows nothing of this file:

| | KLB (class 3) | GMI (class 2) |
|---|---|---|
| opcodes named in `kl1_encoding.md` | 125 | 80 |
| of those, with no entry | 1: `wait_different_value` (`a5`) | 1: `scsi_transfer` (`dc`) |
| opcodes neither named nor in a register/size family, with an entry | 0 | 0 |
| empty entries | 11 | 177 |

- The register families share one entry each, as they must if the
  register is an operand: `set_atom` `00`-`0f`, `put_atom` `40`-`5f`,
  `wait_atom` `80`-`9f`, `get_atom` `c0`-`df`. This is a second witness
  for the correction made to `kl1_encoding.md` on 2026-11-20 (the low
  opcode bits are the register, not an atom number).
- The size families have an entry per size: `put_vector_0`..`6`
  (`38`-`3e`), `wait_vector_0`..`6` (`a8`-`ae`).
- All 13,156 KLB and GMI instruction cells of `pimm_ipl.kbn` have an
  entry.
- All 726,053 instructions of the `.sav` object set (`asm/census.py`)
  have an entry, except one: `scsi_transfer`, used once.
- **Two instructions the assembler knows are not in this firmware:**
  `wait_different_value`, which no PIMOS object uses, and
  `scsi_transfer`, which the IPL image does not use and the object set
  uses once. So this firmware build is not quite the one that object
  set needs, or that one call was never reached. The ten KLB opcode values with no name (`17 6c 6d 72 a3
  b5 bb be bf e7`) have no entry either: they are unassigned, not
  undocumented instructions.
- Classes 0 and 1 (PMI, BLT) are populated (class 0: 32 entries of one
  filler pair, 42 all zero; class 1: 15 all zero) and have not been matched
  to anything: `kl1_encoding.md` has no table for those tags.

Observed fault injections into the reader, each FAILed and restored:
KLB read as class 1 (every unassigned opcode gains an entry, the atom
families stop sharing); entries taken one word late; the table taken
one opcode late (nine named instructions lose their entry); the
image's class taken from the wrong tag bit (most of the image's
instructions have no entry).

## 2. The console's record inspectors name the record fields

The console packages (`INSTALL.DIR/*.ptf`) are compiled ESP, not read
here, but their text is two-byte JIS and extracts cleanly
(`asm/psdpim.py --text INSTALL.DIR/pimmcsp.ptf`). The Shoen Tree
inspector prints each record as a numbered menu, so the menu is the
record's field order. Whether a number is a word offset or only a menu
position is not established; the `(Low)`/`(High)` pairs suggest words.

**Foster-parent record** (`FPREC`), 14 fields: 0 Shoen ID, 1 Status,
2 Stop Goals, 3 Child, 4 Left Link, 5 Right Link, 6 Resource Left,
7 (unlabelled), 8 Shoen Statistics, 9 Max Priority, A Min Priority,
B Suspend Messages, C-D Last Resource (low, high).

**Shoen record** (`SHREC`), 24 fields: 0 Shoen ID, 1 Status, 2-3 Bit
Table 0/1, 4 Foster Parent (an `FPREC` pointer), 5 Left Brother,
6 Right Brother, 7 Result Report, 8-9 Resource Request 0/1,
A (unlabelled), B Resource Left, C (unlabelled), D Statistics Hook,
E Statistics Counter, F Exception Mask, 10 Max Priority, 11 Min
Priority (printed "Mix"), 12-13 Resource Limit, 14-15 Resource
Consumed, 16-17 Last Consumed.

**Multiple suspension record**: its inspector's menu has four
unnumbered items, `prev >`, `next >`, `goal >`, `rival >`. Unlike the
two menus above they carry no field numbers, so they may be the
record's fields or only the inspector's ways of moving (to the
previous and next record, to the goal, to the goal's other records).
Whether they are fields is not established. The single-waiter case has its own inspector ("Suspension Stack", "SST")
and no field names in the text.

**Import/export tables.** Black import entry: Exref ID, Weight, Import
Count, Exref Cell, Hash Link. Black export entry: Exported Data,
Weight, one unlabelled, Hash Link. White import: Exref ID. White
export: Exported Data. (`PIMM.PARAM` gives 5 and 4 words for the black
entries, which fits.)

**Tags.** The console's tag grammar lists the same names in the same
order as `debugger/inspector/tagtbl.kl1` and ends `... "DREF" |
"GOAL"`: one tag past the 59 we have, for goal records. Its value is
not printed.

**Fixed memory areas** (the parameter editor's defaults): `000200`
Passive Unification Stack, `000400` Suspension Stack, `005000`
Structure Hash Table, `005800` Goal Stack Entry Table, `005C00`/`006000`
Black Export Hash Table / Table, `007800`/`007C00` Black Import Hash
Table / Table, `009800` White Export Table, `00A000` White Import
Table, `00A800` SCSI Records, with console, trace and network areas
between (`asm/psdpim.py --text INSTALL.DIR/pimmutil.ptf`).

**The goal record's fields are not in the text.** The goal inspector
shows a goal as `Module : Predicate / Arity` with its arguments
(`get_goal_arity`, `get_goal_args`, `get_goal_record_1`/`_2`); the
layout is in the compiled code.

## 3. Not read

*Superseded in part the same day: `pseudo_pimm_microcode.md` and
`asm/mekbn.py` locate the microprogram in the file and the address in
a decode entry. The first two items below are answered there; the
guess about address bits in the second was partly wrong.*

- The microprogram itself. After the decode table the file is not a
  flat array: words 2,049-2,284 and the words before 47,529 are runs of
  16-bit pairs (values up to `3ff`, nearly a permutation) ending in a
  three-word trailer, and the zero gaps end on 256-word boundaries.
  The segment structure, the pairing of words into 64-bit
  microinstructions and their order are not worked out, so the
  published field layout (TR-733 fig. 4) has not been tried on it.
- Which bits of a decode entry are the microprogram address. The
  second word's low bits behave like one (`less_than` .. `modulo` step
  by 8 from `0248`; `put_vector_3`, `_4`, `_5`, `_6` are `3201`, `3203`,
  `3205`, `3207`), which is suggestive and unchecked.
- `syspsi`, `sysinit`, `sysidat`, the fonts, and the compiled code of
  the `.ptf` packages (the microcode reverse assembler's mnemonic table
  would be the prize; `set_mnemonic_file` says it loads one from a file
  that is not in the archive).

## 4. What this changes

- Nothing in the models. The record layouts are for the shoen
  machinery (roadmap R6-R7), which is not started; they replace "not
  found" in `literature_gaps.md` for the Pseudo PIM/m.
- The suspension design question (`pimm_semantics.md`, "Runtime
  state") is not settled by the menu items above; the microprogram
  would settle it.
- `wait_different_value` needs no model (nothing uses it);
  `scsi_transfer` is used once in the object set and is not in this
  firmware.
