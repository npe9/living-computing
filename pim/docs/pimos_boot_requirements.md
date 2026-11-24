# PIMOS boot requirements (roadmap Phase 0 results)

Results of Phase 0 of `pimos_roadmap.md`, filled in as each item is
measured. Reproduce the census with `python3 asm/census.py --model`;
`asm/census.py --check` pins its totals and runs in `run_tests.sh`.

## 0.2 Decoder: every `.sav` decodes (done 2026-11-19)

All 20 `.sav` files in `nonlocal/pimosobj.tar.Z` decode with
`asm/unlsav.py`: **502 modules, 726,053 instructions, 12,344
predicates, no unclassified word.**

*Corrected 2026-11-20.* The figure published on 2026-11-19 was 671,080
instructions and 192 distinct opcodes. It left out the 54,973
atom-form instructions (`write_atom` 31,459, `wait_atom` 12,482,
`get_atom` 6,184, `put_atom` 3,844, `set_atom` 1,004), which the `.sav`
stream serialises differently (`[0x23xx, atom name]`) and the census
skipped. The per-file listing below still shows the old per-file
counts; `asm/census.py` prints the current ones.

```
pimm_bios360E.sav                35 modules   22991 instructions  (2 trailing words)
pimm_debugger360E.sav           116 modules  118344 instructions  (2 trailing words)
pimm_kernel360E.sav              42 modules   49510 instructions  (2 trailing words)
pimm_library360E.sav             96 modules  163798 instructions  (2 trailing words)
pimm_macro360E.sav                6 modules   31162 instructions  (2 trailing words)
pimm_patch_driver360E.sav         1 modules   10071 instructions  (2 trailing words)
pimm_patch_fepsv360E.sav          1 modules    1564 instructions  (2 trailing words)
pimm_patch_hash360E.sav           1 modules     298 instructions  (2 trailing words)
pimm_patch_libvar360E.sav         1 modules    4235 instructions  (2 trailing words)
pimm_patch_lis360E.sav            2 modules    2110 instructions  (2 trailing words)
pimm_patch_macro360E.sav          1 modules   15465 instructions  (2 trailing words)
pimm_patch_mkdir360E.sav          6 modules    9337 instructions  (2 trailing words)
pimm_patch_modu360E.sav           1 modules   10122 instructions  (2 trailing words)
pimm_patch_newpg360E.sav          5 modules    6549 instructions  (2 trailing words)
pimm_patch_scsifep360E.sav        1 modules    1773 instructions  (2 trailing words)
pimm_patch_shutl360E.sav          3 modules    1003 instructions  (2 trailing words)
pimm_patch_tel360E.sav            1 modules    4683 instructions  (2 trailing words)
pimm_server360E.sav              97 modules  101800 instructions  (2 trailing words)
pimm_shell360E.sav               43 modules   35250 instructions  (2 trailing words)
pimm_utility360E.sav             43 modules   81015 instructions  (2 trailing words)
```

The two trailing words of each file have not been interpreted.

**What was wrong.** Three images (`library`, `macro`, `patch_macro`)
failed in their first module. The module's GC area holds floating-point
constants, encoded as a tagged 32-bit object `[0x00TT, V1, V2]`
(`unloader/decoder.kl1` line 322, `decode_atomic(16#"00",TAG,...)`,
`TAG > 0`). The decoder took `0x0030` for an unknown one-word term,
lost sync, read past the `0x1000` end marker and ran into the code
area. Injection: with that case disabled, `census.py --check` exits 1
with the same IndexError. The same case is now handled inside
`hash_on_constant` tables.

**Word tags in a code area.** A three-word item `[0x00TT, V1, V2]`
carries the word's own tag `TT`. Four values occur:

| Tag | Count | Meaning | Source |
|---|---|---|---|
| `0x23` | 661,056 | instruction | `inst_tab.kl1` `Tag = 16#"23"` |
| `0x22` | 10,024 | instruction, second opcode space (extended arithmetic and other built-ins) | `inst_tab.kl1` `Tag = 16#"22"` |
| `0x24` | 12,344 | predicate head: `(Arity<<24) \| offset` | `assembler/assemble.kl1` `make_pred_head`, lines 195-201 |
| `0x30` | 103 | floating-point constant (IEEE single in the value) | by value: `0xbf800000`, `0x3f...`, `0x41...`, `0x42...` |

The earlier census (`asm/freq.py` before this change) looked up every
such item by opcode regardless of tag, which is where its "unknown
opcodes 0x02-0x07" came from: they were predicate heads of arity 2-7.

**The 1994-only opcodes.** With tags separated, 13 opcode values under
tag `0x23` are absent from the live clauses of the 1992 `inst_tab.kl1`.
All 13 are present there as commented-out clauses, so their names and
operand types are known:

| Opcodes | Mnemonics | Type | `inst_tab.kl1` lines | Uses |
|---|---|---|---|---|
| `0x38`-`0x3e` | `put_vector_0` .. `put_vector_6` | `r_vector` | 65-71 | 34,338 |
| `0xa9`-`0xae` | `wait_vector_1` .. `wait_vector_6` | `r_m` | 157-162 | 9,493 |

The 1992 assembler emits the general `put_vector`/`wait_vector` with a
length field; the 1994 object set uses the per-length quick forms for
lengths up to 6. Whether the quick forms take the operand layout the
commented-out types name is not yet confirmed against the binaries.

**What the object set uses.** 197 distinct (tag, opcode) pairs, the
atom instructions counted once per family whatever register rides in
the opcode byte. Some
opcodes are shared by several built-ins that a sub-function byte tells
apart (`f_r_r`, `f_r_r_r` types); those are not yet broken out.

**Against the bench model.** *(Note 2026-11-23: this is the bench
model only. The reference model and the `Pimm*` core implement 128 on
both, `ref/pimm/README.md`.)* `bsv/PimKL1B.bsv` has an arm for 51 of the
197, covering 533,088 instruction words (73.4%) by static count. The
match is textual, so stand-in arms count. The most used opcodes with no
arm at all:

| Mnemonic | Tag/op | Uses |
|---|---|---|
| `collect_vector` | 23/1f | 26833 |
| `put_vector_2` | 23/3a | 16838 |
| `put_structured_constant` | 23/37 | 11628 |
| `put_vector_3` | 23/3b | 10350 |
| `save` | 23/19 | 9605 |
| `restore` | 23/1a | 7933 |
| `wait_vector_2` | 23/aa | 5768 |
| `write_marked_value` | 23/27 | 5082 |
| `put_vector_4` | 23/3c | 4322 |
| `collect_list` | 23/1e | 4219 |
| `execute_external` | 23/62 | 4030 |
| `put_reused_structure` | 23/2f | 3998 |
| `set_marked_value` | 23/16 | 3445 |
| `put_marked_value` | 23/36 | 3278 |
| `wait_vector_3` | 23/ab | 2360 |
| `enqueue_goal_external` | 23/66 | 2096 |
| `less_than` | 23/f0 | 1937 |
| `b_add` | 22/c0 | 1897 |
| `set_vector_element` | 22/d0 | 1627 |
| `write_marked_variable` | 23/26 | 1407 |
| `string` | 23/e5 | 1350 |
| `put_vector_5` | 23/3d | 1251 |
| `not_less_than` | 23/f1 | 1240 |
| `b_subtract` | 22/c1 | 1062 |
| `wait_vector_4` | 23/ac | 944 |
| `vector_element` | 23/ee | 884 |
| `diff` | 23/f9 | 791 |
| `put_vector` | 23/3f | 766 |
| `set_string_element` | 22/d1 | 735 |
| `put_vector_6` | 23/3e | 705 |
| `vector` | 23/e4 | 655 |
| `put_vector_1` | 23/39 | 544 |
| `display_console` | 23/7f | 451 |
| `new_string` | 22/d4 | 431 |
| `merge` | 22/f0 | 424 |
| `b_string_element` | 22/cd | 404 |
| `and` | 23/ea | 377 |
| `b_vector_element` | 22/cc | 373 |
| `mark_element` | 23/1c | 353 |
| `put_vector_0` | 23/38 | 328 |

**The file trailer (2026-11-20).** After the last module each `.sav`
ends in a 32-bit checksum, the XOR of every 16-bit word before it. All
20 files verify (`asm/census.py --check` pins it; summing instead of
XOR-ing failed all 20), so no word of any `.sav` is left unexplained,
and the copies in `nonlocal/` are intact as ICOT wrote them. The "2
trailing words" in the listing above are this checksum.

## 0.1 Firmware search (done 2026-11-19)

Three KL1 executors survive in the ICOT Free Software archive; all
three are now in `nonlocal/` (`MANIFEST.md` §1a has URLs, checksums and
contents). None runs our object set as it stands.

| Package | What it is | Source? | Same dialect as our `.sav`? |
|---|---|---|---|
| `psdpim.tar.Z` | **The Pseudo PIM/m firmware itself** for PSI-III, the system the PIMOS object set targets, with its console system | no: binary firmware (`pimm.MEkbn`, 506,624 bytes; `syspsi`), SIMPOS package files | yes, presumably: it is what executed these files |
| `pdss.tar.Z` | PDSS V2.52.20: a complete KL1-B interpreter in C (28,441 lines) with scheduler, suspension, GC, MRB, shoen, exceptions, built-ins, loader; plus compiler, Micro PIMOS, tests, manual | yes, C | no: different save format (magic `0xA5C3`-`0xA5C9` vs `0x5702`) and different opcode numbering |
| `vpim.tar.Z` | VPIM: the KL1 runtime of every PIM except PIM/m, 185 PSL files, with the distributed runtime (export tables, inter-cluster GC and messages) | yes, PSL, read-only; no translator or build files in the archive | no: a third numbering |

No PSI, Multi-PSI or PIM hardware emulator and no microcode listing was
found (mirror directories, the 100-entry IFS index, English and
Japanese web searches, bitsavers).

**Consequence for Phase 2: the "port" branch, with a caveat.** The
runtime does not have to be reconstructed from prose. PDSS is an
executable description of the same abstract machine by the same
group, used to develop this operating system: the semantics of
suspension, goal scheduling, MRB, shoen and the built-ins can be read
from its C. The caveat is that it is a sibling: every instruction and
built-in has to be mapped by name from the PIM/m table to PDSS's, and
where they differ in operands or behaviour the PIMOS binaries decide.
VPIM is the reference for what PDSS leaves out (multiple PEs).

**Three things this opens up, in order of cost:**

1. *A name map.* PIM/m mnemonics (`inst_tab.kl1`, 197 used) against
   PDSS `instr.h` and VPIM `p_opecode_table.psl.c`: which have a
   same-named counterpart, which do not. Cheap; it sizes the caveat.
2. *PDSS as the lockstep model's starting point* (roadmap decision 3):
   build PDSS on a modern machine, run its own tests, then teach it the
   PIM/m `.sav` format and numbering, or drive a new reference model
   from its sources.
3. *The firmware binary.* `pimm.MEkbn` is the real answer to "what did
   the firmware do", in PSI-III microcode. The PIM/m processing element
   and the PSI-III are close relatives, so its format is worth one look
   (does `syspsi`/`pimm.MEkbn` carry a microinstruction layout our
   sources document?) before it is set aside.

**Applications.** Twenty-odd KL1 applications written for PIMOS are in
the archive (MGTP, GDCC, Kappa-P, PAX, a Go player, LSI routing and
logic simulation, among others); the list is in `MANIFEST.md` §1a.
They are the candidates for rung R9.

## 0.5a Instruction name map against PDSS (done 2026-11-20)

`python3 asm/namemap.py --table` classifies each of the 197 PIM/m
instructions the object set uses against PDSS's table
(`emulator/instr.h`, 350 names; formats from `emulator/instr.c`), by
mnemonic and by number of register operands. `--check` pins the class
sizes and runs in `run_tests.sh`.

| Class | Opcodes | Uses | Share | Meaning |
|---|---|---|---|---|
| same | 73 | 451,843 | 62.2% | same mnemonic, same register count |
| prefix | 46 | 12,920 | 1.8% | same name under PDSS's `g_`/`b_` built-in prefix (`less_than` is `g_less_than`), `floating_point` spelled `float` |
| renamed | 5 | 11,699 | 1.6% | `switch_on_non_{atom,integer,list}` are `jump_on_non_*`; `calculate_priority_from_minimum` is `b_rate`, `..._from_current` is `b_rltv` (read in `blt_system.c`) |
| merged | 1 | 19,249 | 2.7% | `get_bound_value`: PIM/m has it beside `get_value`; PDSS has only `get_value` |
| differs | 4 | 2,495 | 0.3% | a name counterpart with a different register count: `switch_on_non_vector` (two registers; PDSS `jump_on_non_vector` has one), `collect_garbage`, `add_shoen_resource`, `shoen_statistics` |
| split | 18 | 208,661 | 28.7% | one PIM/m instruction where PDSS has one per position or per type |
| absent | 50 | 19,186 | 2.6% | nothing in PDSS's table |

**What this says about a PDSS port: it is a translation layer, not a
renumbering.**

- *The split class is the structural difference.* PIM/m builds and
  reads structures through an implicit position: `write_value`,
  `write_variable`, `write_atom`, `read_variable` and their relatives, 29% of all
  instruction uses, with `put_vector_N`/`wait_vector_N` setting the
  position up. PDSS names the cell in the instruction:
  `write_car_value`, `write_cdr_value`, `write_element_value`,
  `read_car`, `read_cdr`, `read_element`. The same holds for constants
  (PIM/m `put_constant`, `switch_on_constant`, `hash_on_constant`
  against PDSS's per-type `put_atom`/`put_integer`, `branch_on_atom`/
  `branch_on_integer`). The semantics exist in PDSS; the instructions
  do not, so a reference model needs PIM/m's structure-pointer state
  that PDSS never had.
- *`save` and `restore`* (17,538 uses) are absent from PDSS and present
  by name in VPIM's table. What they save is not yet read from either
  source; it belongs to 0.5.
- *The rest of "absent"* is machine- or era-specific and small: extended
  (bignum) arithmetic, extended floating point, SCSI, profiling,
  `enqueue_goal_to_processor`, `export_entry`, `apply_tracing`,
  `apply_spying`, timers, heap alerts. `module` (83 uses) matches a
  PDSS name that is an assembler directive, not an instruction, and is
  counted absent.
- *False friends.* PIM/m `vector` (two registers) and `string` (three)
  are guard built-ins; PDSS's `vector` and `string` are the
  one-register wait-and-check instructions. The register count sends
  them to `g_vector`/`g_string`. Name alone would have paired them
  wrongly, which is why "same" here means a candidate, not a result.
- *VPIM* shares only 12 mnemonics with the used set. Its table is at a
  lower level (`READ_WAIT`, `WRITE_IND`, `GET_CODE`): it is a reference
  for runtime mechanisms, not for instructions.

**Limits.** By name and register count only: operand order,
non-register operands and behaviour are unchecked. An opcode shared by
several mnemonics through a sub-function field is classified by its
first. The pinned check catches a changed table or decoder, not a wrong
pairing of equal count (observed: removing the `b_rate` row from `RENAMED` moved
renamed 5 to 4 and absent 50 to 51 and failed the check).

## 0.3 The IPL image `pimm_ipl.kbn` (done 2026-11-20)

The format is in the source: `src/library/kbn/kbnfile.kl1` writes the
file, `kbn.kl1` lays out modules, `kbnheap.kl1` names the tags.
`python3 asm/kbn.py` decodes it; `--check` pins the result and runs in
`run_tests.sh`. Every one of the 18,300 cells is placed.

**File.** A 256-byte header, then 256-byte blocks of 51 five-byte
cells and one pad byte. The header is 128 16-bit words, little-endian
on disk, each field a 32-bit value as low word then high word. A cell
is the 32-bit value low byte first, then the 8-bit tag.

| Header words | Field | Value in `pimm_ipl.kbn` |
|---|---|---|
| 0-1 | LoadAddress | `0xE0000000` (the default in `kbn.kl1`) |
| 2-3 | CodeSize, in cells | 18,300 |
| 4-5 | StartAddress | `0xE0001E81` (cell 7,809) |
| 6-7 | ModuleAddress | `0xE0001E25` (cell 7,717) |
| 126-127 | Version | `0x01973460` (meaning not yet read) |

*(Note 2026-11-23: StartAddress is the image's entry, `ipl:boot/0`. It
is not the `20c` that `boot.init` passes to the CSP's `start`: cell
`0x20c` lies inside `ipl_file_decoder:check_GC_element/8`. What `20c`
addresses is open, `icot_software_survey.md` §7.)*

92,160 bytes = 1 header block + 359 blocks of 51 cells = 18,309 cells,
the last 9 zero.

**Layout.** 20 modules, 17,010 cells, each followed by its structured
constants (1,270 cells in all: strings, vectors, lists), then a
20-entry module table at the very end.

- A module is `{module, self+1}`, `{cdesc, 0x06<<24 | Length}`,
  `{integer, GCSize}`, the GC area, the entry (predicate hash) table,
  then code (`kbn.kl1` `encode_module`). Lengths run from 43 to 1,857
  cells.
- ModuleAddress is the `cdesc` cell of the module at cell 7,716;
  StartAddress is an instruction 92 cells into it, directly after a
  predicate head (`kbnlink.kl1`: StartAddress = module address + the
  code offset of the start predicate).
- 13,156 instruction cells (12,651 tag `0x23`, 505 tag `0x22`), 349
  predicate heads; 143 distinct opcodes, none unnamed. The bench model
  has some arm for 47 of them, 10,466 instruction cells by static
  count.

**Tags, from `kbnheap.kl1` `tag/2`.** These are the machine's own data
tags, which the bench model has so far invented:

| Tag | Type | | Tag | Type |
|---|---|---|---|---|
| `0x00` | integer | | `0x10`,`13`,`15`,`17`,`19`,`1B`,`1D` | vector of 0..6 elements |
| `0x02` | atom | | `0x1F` | vector, 7 or more (through a `vdesc`) |
| `0x05` | list | | `0x25` | `cdesc` (code/string descriptor) |
| `0x0D` | `vdesc` | | `0x27` | module |
| `0x0F` | string | | `0x30` / `0x3F` | float / extended float |

**The full tag table is in the source too** (found 2026-11-20):
`debugger/inspector/tagtbl.kl1` names 59 tags, and `asm/kbn.py` carries
it whole. The ones the runtime turns on:

| Tag | Name | | Tag | Name |
|---|---|---|---|---|
| `00`/`01` | INT | | `20`, `21`, `22`, `23` | PMI, BLT, GMI, KLB (instruction words) |
| `02`/`03` | ATOM | | `24`, `25`, `26`, `27` | PREDH, CDESC, COD, MOD |
| `04`/`05` | LIST | | `28` | MGHOK |
| `06`/`07` | REF | | `29` | EXMRF |
| `08` | UNDF (unbound) | | `2A`-`2F` | EUNDF, EHOOK, EMHOK |
| `0A`/`0B` | HOOK (suspended goals wait here) | | `30`/`31` | FLT |
| `0C` | MHOOK | | `32`-`35` | EXREF, EXVAL (other processors) |
| `0D` | VDESC | | `36`/`37` | RHOOK |
| `0E`/`0F` | STRG | | `38`, `39`, `3A` | SHREC, FPREC, FPRECt |
| `10`-`1F` | VECT0..VECT6, VECT | | `3B` | DREF |

Paired tags differ in the low bit and are printed with an `o` or `x`
suffix (`INTo`/`INTx`). The source does not say what the bit means; the
MRB (multiple-reference) bit is the obvious reading and is ours. Every
pointer the image builder writes has it set.

`bsv/PimKL1B.bsv` uses `0x02` for integer, `0x06` for atom, `0x07` for
vector and `0x01` for an unbound variable; only its list tag agrees.

**The `06` and `07` cells are references.** The 20 cells at the end of
the image are REFo, one per module, each pointing at a module's MOD
cell; the 51 `07` cells inside modules' GC areas are REFx pointing at
those. So an external module reference is a two-step reference chain
through one cell per module, where the 1992 `kbn.kl1` writes a direct
`{module, address}` cell. (Before the tag table was found these were
described here as a "module table" under names of our own.)

**In-memory atom instructions.** In the image an atom instruction is
one cell: opcode byte (the base plus a register for `set_atom`,
`put_atom`, `wait_atom`, `get_atom`), then a 24-bit atom number
(`kbn.kl1` `encode_code_1`). `pimm_ipl.sym` is the atom-number-to-name
table (two-byte JIS text, 487 lines).

**Observed injections on `asm/kbn.py --check`:** 50 cells per block
instead of 51 gave 1 module instead of 20 and 11,449 structural
violations; reading the header big-endian raised an error before any
result. Both restored; PASS.

This replaces the description in `pimos_binaries.md`, which read the
header's four fields as heap cells.

## 0.4 Address units (done 2026-11-20)

One address is one 40-bit cell, and one instruction word is one cell.
A module is a contiguous run of cells; the entry table and the
`hash_on_constant` tables hold offsets in cells relative to the cell
that holds them (`kbn.kl1` `set_entry_part`: `Loc - P1`, and
`Loc - P1 - 1` for hash tables, both limited to 16 signed bits). The
header's addresses are cell addresses.

A label in an instruction is 16 signed bits, `target - (here + 2)` in
cells: of the 492 `try_me_else` instructions in the IPL image, 475
point, read that way, at another `try_me_else`, a `suspend` or an
`otherwise`, which is what the next clause starts with (`asm/kbn.py
--check` pins both numbers; with `here + 1` or `here` instead, fewer
than half do). The other 17 are not yet looked at. The `.sav` stream's 16-bit word positions are not addresses: several
stream words make one cell.

## 0.7 Bluesim throughput (measured 2026-11-20)

The bench model, stepping a three-instruction loop (`put_integer`,
`put_integer`, `jump`): 30,000,000 steps in 2.08 s of CPU, about
**14 million steps per second** on the development machine. The bench
is not in the tree (the model's `step()` is driven by one rule; the
loop touches no memory beyond 4,096-word register files).

What it means: simulation speed does not shape the plan. A model with
megaword memories, a scheduler and a cycle-level pipeline will be
slower, perhaps by one or two orders of magnitude, and a boot of
10^8-10^9 instructions would still be minutes to hours, not weeks. The
number of instructions PIMOS executes to reach its prompt is itself
unmeasured.

## 0.5 Runtime inventory (done 2026-11-20)

`python3 asm/inventory.py --list` groups every instruction by the part
of the runtime it needs, for the whole object set and for the IPL
image, with the shared opcodes broken out by sub-function (bits 23-16
of the word; `klb_opr.kl1` `p({f_r_r,F},...)`). `--check` pins the
table and runs in `run_tests.sh`. The grouping is by mnemonic and is
ours: it sizes the work, it does not define semantics.

| Group | Object set: mnemonics | uses | IPL image: mnemonics | uses |
|---|---|---|---|---|
| unification/structure | 56 | 504,586 | 51 | 8,143 |
| goal control | 14 | 117,634 | 9 | 2,197 |
| heap/gc/profile (`collect_*`, `mark_element`, ...) | 8 | 57,556 | 4 | 911 |
| indexing | 6 | 20,821 | 6 | 429 |
| guard type/compare | 8 | 9,923 | 7 | 547 |
| string/vector built-ins | 18 | 7,222 | 13 | 287 |
| integer arithmetic | 21 | 5,176 | 18 | 397 |
| code/module/atom objects | 13 | 1,228 | 11 | 51 |
| device | 14 | 563 | 5 | 137 |
| float | 16 | 485 | 2 | 8 |
| bignum/extended integer | 9 | 322 | 0 | 0 |
| shoen/priority/processor | 19 | 278 | 17 | 48 |
| extended float | 43 | 259 | 1 | 1 |
| **total** | **245** | **726,053** | **144** | **13,156** |

245 mnemonics, not 197, because the nine shared opcodes are 57 distinct
sub-functions in use. All but one are float or extended-float
operations (631 uses in all); the other is `tag_and_value` (23/76
sub-function 4, 87 uses), which the earlier tables listed under its
opcode's first name, `export_entry`.

**What this says.**

- *The IPL is not a small subset.* 144 mnemonics, including 17 of the
  19 shoen/priority/processor instructions and 11 of the 13
  code/module object ones (`new_module`, `new_instruction`,
  `predicate_to_code`: it builds modules from the `.sav` stream).
  Rung R2 "the IPL runs" already needs goals, suspension, shoen, MRB
  collection and the module objects. There is no boot stage that runs
  on the bench model's level of machine.
- *The long tail is cheap to defer.* Extended float, bignum and float
  are 68 mnemonics and 1,066 uses in the whole set, 3 mnemonics and 9
  uses in the IPL. They can fail loudly until something calls them.
- *`save`/`restore`* (17,538 uses) do not occur in the IPL at all, nor
  does `read_variable_without_deref` (20,625) or `jump`. What `save`
  and `restore` do is still unread.

## 0.6 Boot I/O at the instruction level (done 2026-11-20; protocol open)

The device instructions, with uses in the object set and in the IPL:

| Instruction | Set | IPL | |
|---|---|---|---|
| `display_console` | 451 | 61 | diagnostic output; every BIOS error path ends in one |
| `put_console` | 72 | 71 | |
| `read_console` | 16 | 0 | |
| `scsi_init`, `scsi_command` | 2, 2 | 1, 1 | the whole SCSI path goes through these two (`bios/scsi/scsi_blt.kl1`: `scsi_init/3`, `scsi_command/7`) |
| `scsi_where`, `scsi_transfer`, `scsi_abort`, `scsi_reset`, `scsi_bus_reset` | 7 | 0 | |
| `system_timer`, `set_timer` | 12 | 0 | |
| `log_event` | 1 | 0 | |
| `halt` | 1 | 3 | |

So the IPL needs a console sink and one SCSI command primitive, and
nothing else from outside the machine. `pimos_binaries.md` ("The SCSI
device PIMOS expects") has what the BIOS source says about the
device.

*Open:* which SCSI commands the IPL issues, in what order, and what the
other end must answer. The IPL's source (modules `ipl`, `ipl_module`,
`ipl_file_decoder`, named in `pimm_ipl.sym`) is not in `pimos.tar.Z`;
its decoder shares predicate names with `library/unloader/decoder.kl1`.
The answer has to come from disassembling the image, which needs the
atom table joined to the code. That is Phase 1 work (the loader), not
Phase 0.

## The IPL by name (2026-11-20)

`python3 asm/kbndis.py` joins the image with its atom table
(`pimm_ipl.sym`, 486 atoms) and disassembles by module and predicate.
`--check` pins the 20 module names, that all 349 predicate heads are
named, that the start address is `ipl:boot/0`, four predicates with
their arities and lengths, and a digest of every predicate's name,
arity and length; it runs in `run_tests.sh`. Observed injection:
reading the arity from bits 23-16 of the head changed the digest and
failed the check. (The check as first committed in 63ecc47e did not
pin arities, and that injection passed it; the commit message there
says otherwise and is wrong.)

A predicate in the image is `{atom, name}`, `{integer, 0}`,
`{predicate head, arity << 24 | offset in module}`,
`{integer, length << 16}`, then the code. All 349 heads check against
their own offset.

| Module (all in package `pimos`) | Cells | Predicates | KL1 source in `pimos.tar.Z` |
|---|---|---|---|
| `ipl` (start: `boot/0`) | 1,440 | 34 | none |
| `top` | 865 | 23 | none |
| `ipl_file_decoder` | 1,857 | 41 | none (shares predicate names with `library/unloader/decoder.kl1`) |
| `ipl_loader`, `ipl_module`, `ipl_pool`, `ipl_link_table`, `ipl_scsi` | 4,479 | 111 | none |
| `scsi_fep_file`, `scsi_fep_module`, `scsi_fep_general`, `scsi_fep_util` | 3,177 | 66 | none under these names (`bios/fep_module/scsi_fep.kl1` is module `scsi_fep`) |
| `exception_table` | 1,701 | 14 | `kernel/builtin/excpt_tbl.kl1` |
| `shoen` | 1,343 | 22 | `kernel/builtin/shoen.kl1` |
| `scsi_common` | 731 | 13 | `bios/scsi/scsi_common.kl1` |
| `builtin_utility` | 349 | 8 | `kernel/builtin/string.kl1` |
| `scsi_processor` | 340 | 3 | `bios/scsi/scsi_processor.kl1` |
| `scsi` | 328 | 9 | `bios/scsi/scsi_handler.kl1` |
| `jis_to_ascii` | 317 | 3 | `bios/boot/jtoa.kl1` |
| `scsi_builtin` | 43 | 2 | `bios/scsi/scsi_blt.kl1` |

The "source" column is by `:- module` name only; whether the 1994
object was compiled from the 1992 text as it stands is unchecked.

**What this gives.**

- *Source paired with object code*, for eight modules. That is the
  material for settling operand order and behaviour instruction by
  instruction, which the name map could not.
- *A first real predicate for rung R2:* `jis_to_ascii:convert/2` and
  its helpers. Three predicates, 317 cells, known source
  (`bios/boot/jtoa.kl1`), integer guards and arithmetic, one loop, two
  string built-ins, no I/O and no shoen. In order of difficulty:
  `convert_element/2` is a leaf (guards and arithmetic);
  `convert_loop/4` needs goals (`enqueue_goal`, `execute`) and, as its
  code reads, a body built-in (`set_string_element`) applied to a
  variable that `convert_element` has not bound yet, which means
  built-in suspension and wake-on-bind (unconfirmed against the
  source); `convert/2` adds `new_string`.
- *The image is closed.* All 92 `execute_external` and
  `enqueue_goal_external` instructions resolve, by module and
  predicate key, to a predicate present in the image (pinned). The
  operand is a location, `target - (here + 2)`, of a four-cell entry:
  `{integer}`, `{REFx to the module}`, `{atom, arity << 24 | atom
  number + arity}`, `{atom, module name}`.
- *Where the SCSI exchange is.* The image's only `scsi_init` and
  `scsi_command` are in module `scsi` (`command_executer/2` issues the
  command); what is sent comes down through `ipl_scsi` and the
  `scsi_fep_*` modules, which talk to the front-end processor as a
  SCSI device. Reading that exchange out is now a matter of
  disassembly, and is not done.

## The firmware binary (one look, 2026-11-20)

`psdpim`'s `PMPSI.DIR/pimm.MEkbn` (506,624 bytes) is in the same
container as the IPL image: a 256-byte header and 51 five-byte words
per block. Its header says load address `0x4200`, 100,864 words, start
0. The words are not tagged KL1 cells (99% have a zero in the tag
byte's place): they are the Pseudo PIM/m's microcode, 40 bits a word.
Reading it needs the PSI-III microinstruction format, which we do not
have. Set aside; recorded so that it is not looked at twice.

*Looked at again the same day, after the literature search found the
format in print: the file begins with the instruction decode table,
which agrees with our opcode map entry for entry, and the console
packages name the shoen, foster-parent and suspension record fields.
The microprogram proper is still unread. See
`pseudo_pimm_firmware.md`.*

## PDSS runs (2026-11-20)

`ref/pdss/` builds PDSS V2.52.20 from `nonlocal/pdss.tar.Z` on the
development machine and `ref/pdss/test.sh` (in `run_tests.sh`) runs a
KL1 program on it end to end: PDSS's own KL1 compiler, running on the
port, compiles N-queens; the result prints 2, 4 and 92 solutions for 4,
6 and 8 queens, and again through four garbage collections with a
small heap.

The port is a 683-line patch and a shim, not a 64-bit rewrite: PDSS
keeps pointers in `int`, so it is built x86_64 with code, heap and
stack all placed below 2 GB (macOS on Apple Silicon therefore needs
Rosetta; the Linux `-m32` recipe is written but untested). The one real
64-bit bug was `long` used as a 32-bit code word in `klb.h`. Details,
what is unverified (PDSS's own `test/` directory has not been run), and
the observed fault injections are in `ref/pdss/README.md`.

**Roadmap decision 3 can now be taken on evidence:** an executable
KL1-B runtime by the PIMOS group exists to read and experiment
against. It is a sibling dialect (§0.5a) and cannot load the PIMOS
images.
