# PIMOS boot requirements (roadmap Phase 0 results)

Results of Phase 0 of `pimos_roadmap.md`, filled in as each item is
measured. Reproduce the census with `python3 asm/census.py --model`;
`asm/census.py --check` pins its totals and runs in `run_tests.sh`.

## 0.2 Decoder: every `.sav` decodes (done 2026-11-19)

All 20 `.sav` files in `nonlocal/pimosobj.tar.Z` decode with
`asm/unlsav.py`: **502 modules, 671,080 instructions, 12,344
predicates, no unclassified word.**

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

**What the object set uses.** 192 distinct (tag, opcode) pairs. Some
opcodes are shared by several built-ins that a sub-function byte tells
apart (`f_r_r`, `f_r_r_r` types); those are not yet broken out.

**Against the bench model.** `bsv/PimKL1B.bsv` has an arm for 48 of the
192, covering 522,056 instruction words (77.8%) by static count. The
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

1. *A name map.* PIM/m mnemonics (`inst_tab.kl1`, 192 used) against
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

`python3 asm/namemap.py --table` classifies each of the 192 PIM/m
instructions the object set uses against PDSS's table
(`emulator/instr.h`, 350 names; formats from `emulator/instr.c`), by
mnemonic and by number of register operands. `--check` pins the class
sizes and runs in `run_tests.sh`.

| Class | Opcodes | Uses | Share | Meaning |
|---|---|---|---|---|
| same | 69 | 428,329 | 63.8% | same mnemonic, same register count |
| prefix | 46 | 12,920 | 1.9% | same name under PDSS's `g_`/`b_` built-in prefix (`less_than` is `g_less_than`), `floating_point` spelled `float` |
| renamed | 5 | 11,699 | 1.7% | `switch_on_non_{atom,integer,list}` are `jump_on_non_*`; `calculate_priority_from_minimum` is `b_rate`, `..._from_current` is `b_rltv` (read in `blt_system.c`) |
| merged | 1 | 19,249 | 2.9% | `get_bound_value`: PIM/m has it beside `get_value`; PDSS has only `get_value` |
| differs | 4 | 2,495 | 0.4% | a name counterpart with a different register count: `switch_on_non_vector` (two registers; PDSS `jump_on_non_vector` has one), `collect_garbage`, `add_shoen_resource`, `shoen_statistics` |
| split | 17 | 177,202 | 26.4% | one PIM/m instruction where PDSS has one per position or per type |
| absent | 50 | 19,186 | 2.9% | nothing in PDSS's table |

**What this says about a PDSS port: it is a translation layer, not a
renumbering.**

- *The split class is the structural difference.* PIM/m builds and
  reads structures through an implicit position: `write_value`,
  `write_variable`, `read_variable` and their relatives, 26% of all
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

## 0.3, 0.4, 0.5 (built-ins), 0.6, 0.7

Not started: the `.kbn` layout, label address units, the runtime
inventory (built-ins by sub-function, `save`/`restore`), boot I/O,
Bluesim throughput. Also open before decision 3 is taken: whether PDSS
builds and runs its own tests on a modern machine.
