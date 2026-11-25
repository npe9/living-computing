# KL0 on the PSI: data types, tags, instructions, built-ins

KL0 is the PSI's machine language: Prolog-based, with ESP support. It is executed by firmware.
Each claim is marked **KNOWN** (cited), **MEASURED** (held binaries, with the probe given) or
**UNKNOWN**. "TH" is Nakashima's thesis (PDF page ≈ printed/2 + 4, images in `C/x/thA/`).
Microinstruction formats are out of scope here (another agent owns them).

## 1. Missing primary documents

| Document | What it would give | Held? |
|---|---|---|
| *KL0 Reference Manual* (cited as "to appear as ICOT TR", TR-044 refs [Chikayama 84]) | Authoritative KL0 semantics | **no** |
| JAIST "KL0組込述語説明書" MP7002-1 (KL0 built-in predicate manual) | Built-in names, argument modes, privileged marks, errors | **no** |
| TM-261/353/354 (PSI-II firmware) | Instruction to microcode mapping | titles only |
| PSI-III KL0 instruction list with opcodes | Opcode numbers to mnemonics | **no**: none of the documents read here prints one; see the table below |

**Held, and how far they were read for this spec:**

| Document | Read? | Opcode table? |
|---|---|---|
| TR-265 (PSI-II hardware) | read (§3.2-3.4) | none: format only |
| TM-444 (KL0 on downsized PSI-II, Japanese) | read ch.1-2 | mnemonics only |
| TH App A, C and ch.3 | read | mnemonics and cycles, no codes |
| TR-079 (PSI-I micro-interpreter), TM-104 (KL0 if-then-else), TM-661, TR-714, TR-285, TM-858/862 (PSI-III processor papers) | grepped only: `opcode`, `命令コード`, `instruction code` | one hit in TM-661 (a field label); no table found by grep |

## 2. Machine word and data representation

- **Word (KNOWN, TR-265 §3.2):** a PSI-II word is 40 bits: an 8-bit tag (top 2 bits are GC marks,
  low 6 bits the type) and a 32-bit value. Constants carry their value. Every other type carries a
  32-bit logical address. TR-265 names the types unbound variable, reference, atom, integer,
  float, stack vector, list, heap vector, string. A compound term is a stack vector whose first
  element is the functor (TM-444 §1.4(2)).
- **Address space (KNOWN, TR-265 §3.3):** each process has 4 Gwords. The top 3 bits of an address
  select the area:
  - three stacks per process (local, global, trail);
  - two shared areas (heap and system);
  - three reserved.
  
  The heap holds code, ESP objects and heap vectors. The system area holds the PCBs, the interrupt
  vector and the memory tables.
- **Tag values: MEASURED, new.** Class `pimmcsp##kl0_tag` (in `pimmcsp.ptf`; used by the
  micro-reverse-assembler in `pimmutil`) holds `integer_to_mnemonic/3` and `mnemonic_to_integer/3`.
  Its 49-key hash table has keys 0–34, 36–39 and 48–57; this key set is MEASURED. Its symbol
  table holds 49 mnemonics (plus `?`); the names are MEASURED. **The pairing is INFERENCE**:
  key *i* is read as the *i*-th mnemonic in symbol-table order, which gives:

| Tag | Name | Tag | Name | Tag | Name | Tag | Name |
|---|---|---|---|---|---|---|---|
| 0 | int | 13 | obj | 26 | bflt | 39 | strf |
| 1 | atom | 14 | cdesc | 27 | mod | 48 | save |
| 2 | list | 15 | desc | 28 | cadr | 49 | obcb |
| 3 | strg | 16–22 | svct0..svct6 | 29 | frzn | 50 | excb |
| 4 | gundf | 23 | svct | 30 | sug | 51 | bhcb |
| 5 | lundf | 24 | hvct | 31 | prtc | 52 | evf |
| 6 | ref | 25 | bint | 32 | pmi | 53 | evfi |
| 7 | hook | | | 33 | blt | 54 | bhef |
| 8 | ndref | | | 34 | gmi | 55 | bhefi |
| 9 | ddref | | | 36 | predh | 56 | exef |
| 10 | flt | | | 37 | mdesc | 57 | exefi |
| 11 | loc | | | 38 | frm | | |
| 12 | cod | | | | | | |

Status of this table:

- The pairing rests on symbol order. **Six anchors** agree with it, from `asm/ptfdump.py`'s
  independent cell decoding:
  - tag 0 = integer, 1 = atom;
  - 0x20 = PMI instruction, 0x21 = BLT instruction;
  - 0x24 = predicate header (`predh`, 36);
  - every template body begins with word 0x1b00, i.e. tag 27 = `mod` (module).
  
  The remaining 43 pairings are unverified.
- Reading the clause bodies would turn the rest from inference into measurement.
- Interpretation (INFERENCE):
  - gundf/lundf: global and local undefined variables.
  - svct0..6: short stack vectors with the length held in the tag (TR-005 says this).
  - hvct: heap vector. bint/bflt: probably 64-bit ("big") numbers.
  - cdesc/desc/mdesc: class, object and method descriptors (TH App A).
  - frzn: frozen term. prtc: protected object.
  - obcb/excb/bhcb: on-backtrack, exception and bind-hook control blocks (TH pp.246–249).
  - `pimmcsp##kl1_tag` and `mpsicspR##kl1_tag` give the KL1 counterpart (not read here).

## 3. Machine instructions

**Format** (KNOWN, TR-265 §3.4, Fig.3): one or more 40-bit words. The first word holds:

- a 2-bit class: 0 = basic Prolog, 1 = built-ins, 2–3 "reserved for future extension, such as
  parallel programming language implementation" (whether PSI-III's KL1 firmware uses them is UNKNOWN here);
- an 8-bit code;
- a 24-bit operand field: three 8-bit, or 8 + 16 (relative branch), or 24 (atom id).

Following words are tagged 40-bit operands.

MEASURED: the `.ptf` cells with tag 0x20 (`pmi`) and 0x21 (`blt`) are class-0 and class-1
instruction words, op/8 + three 8-bit operand bytes (binary_reverse_engineering.md §4.2). This
agrees with the format above.

**Groups** (KNOWN, TR-265 §3.4; TM-444 ch.1; TH ch.3.2.2 Tables 3-2/3-3, App C pp.278–285):

| Group | Instructions |
|---|---|
| get | variable, value, constant, atom, integer, nil, list, vector N |
| put | variable, value, unsafe_value, constant, atom, integer, nil, list, vector N |
| unify | variable, value, constant, atom, integer, list (merged) |
| procedural | call, execute, proceed, allocate, deallocate; merged `execute_with_deallocate`, `proceed_with_deallocate`, `get_var_var_list` |
| indexing | try_me_else, retry_me_else, trust_me, try, retry, trust, switch_on_term, `hash_on_value`, `encode_vector`, `jump_on_non_list`, `jump_on_non_constant`, `execute_and_switch`, `jump_on_value` |
| method | call an ESP method (TR-265) |
| cut | `cut_me`, `cut_allocated_me`, `cut_me_and_fail`, `cut_and_fail`, plus relative and absolute cut |

Mnemonics carry `_t` / `_p` for temporary and permanent operands, and the argument register comes
**first** (`get_value_t Ai, Xj`). Argument registers are A0–A31 (TM-444 §1.4(1)).

**Built-ins** have operands naming any argument register:

- inputs are passed by preceding put instructions;
- outputs are taken by following get instructions;
- no environment or choice point is created (TR-265 §3).

**Registers and stacks** (KNOWN, TH 3.2.2; TM-444 §2–3):

- Registers: P, CP, E, B, G (global top), HR (heap top), TR, S, LVLC (call level), EXTR
  (exception control).
- The environment frame holds E, CP, B, LVLC, Y0..Yn.
- The choice point holds B, TR, G, AP, LVLC, E, CP, A0..An.
- On a cut, PSI-II does "tidy trail": it compacts trail entries that are no longer needed
  (TM-444 §2.4.2).

**Opcode to mnemonic: mostly UNKNOWN.**

- MEASURED: every opcode used by the six packages has a `sysidat` entry: 101 distinct class-0 and
  111 class-1 opcodes, out of 214 and 241 populated entries (binary_reverse_engineering.md §4.2).
- About ten readings are INFERENCE from known-plaintext pairs in the same document's table §4.2:
  `f0` proceed, `dc n` neck cut, `73`/`74` method call / last call, `60–62` local call/execute,
  `5f n` allocate, `6e` deallocate, class-1 `27` slot read.
- No held document prints opcode numbers. Leads:
  - `pimmutil##csp_micro_reverse_assembler_main` (12,859 cells; it references `kl0_tag`);
  - the class `kl0_tag` itself, and any `kl0_instruction`-like table class in `pimmcsp`/`pimmutil`.
  
  These are the most promising held sources for an opcode-name table, but they serve the
  **micro**-reverse-assembler. Check whether they also name KL0 opcodes before relying on them.
- MEASURED 2026-11-24, from known plaintext:
  - 96 opcodes (70 class-0, 22 class-1, 3 atom-cell forms, the `cd00` hash table) were named
    at first; 125 now (77 class-0, 44 class-1, after steps 3c, 3d and 3e). They are in
    `../../../psi/kl0_opcodes.tsv`. Each row's witness pairs the compiled cells with the held
    ESP clause they came from. `../../../psi/kl0.py` executes exactly these rows. 44 rows are
    witnessed independently by `../../../psi/fepread/witness.py`, and both are cited.
  - The table confirms the ten INFERENCE readings above.
  - Facts the table settled:
    - A predicate's cut barrier arrives in register A_arity. `dd A n` / `de A n` cut to it, with
      n the environment size.
    - `d5` is cut-and-fail (`remove(T,T,_,_,_):-!,fail;`).
    - `blt 66 A B` tests A_A < A_B; `blt 67 A B` tests A_A >= A_B.
    - `blt 48`/`49` multiply and divide by an 8-bit immediate.
  - The names are OURS. Their mnemonics follow §3's groups where a group fits.
  - 2026-11-25 (`../source_check_2026-11-24.md` §5): where TM-444 or TR-236 prints a mnemonic
    that the held cells single out, the row now carries it as an INFERENCE binding with its
    count: pmi 42/43 `unify_value_p/t`, 44/45 `unify_local_value_p/t` (TM-444 PDF p31 ex. 8),
    a4 `put_local_value`, a5 `put_unsafe_value`, 24 `get_builtin_variable` (TR-236 PDF p5
    Fig. 1), 2b `get_var_var_list` (TM-444 PDF p16); blt 45/46/48/49 `add_/subtract_/
    multiply_/divide_constant` (held cil `cil_kl0.esp`). The indexing and cut rows cite
    `jump_on_non_list`, `jump_on_non_constant`, `jump_on_value`, `hash_on_value`, `cut_me`,
    `cut_me_and_proceed`, `cut_me_and_fail` in their meaning without renaming. The numbers
    themselves are still printed nowhere.

## 4. Built-in predicates

**KNOWN lists:**

- TR-044 App A pp.34–39 (1984), in categories: type tests, object creation, element and
  substructure access, arithmetic (with `_extended`), bit and string logic, comparison,
  conversion, low-level (memory words, areas, processes, interrupts, registers, clock), debug,
  control, I/O. ESP.md §0 gives the source details.
- TM-388 App D pp.145–147 (1987) adds, among others: `bound`, `method_call`,
  `overridden_method_call`, `predicate_call`, `slot`/`set_slot`, `move_string_element`, the
  `search_character(s)_*` family, `search_string_difference`, `type(?X,^Tag)`, `value`,
  `location*`, `vector_element_location`, `raise`, `on_backtrack`, `exception_hook`, `apply`,
  `code`, `hash`, `protected_*`.
- Witnessed encodings (2026-11-24, `psi/kl0_opcodes.tsv`, known
  plaintext in paragraph): `string(S,^L,^T)` is blt 0b, `new_string(^S,L,T)`
  blt 1c (S out in the first operand, `view_select_menu change/3`),
  `string_element(S,I,^E)` blt 23, `set_string_element(S,I,E)` blt 2b.
- Witnessed encodings, step 3c (2026-11-24, same table; each row's
  witness cites the held cells and the source line):
  - `X + Y` is blt 40 (`40 01 00 01`, h.esp:186, the result over the first operand).
  - `integer(X)` is blt 01, `unbound(X)` blt 10 and `bound(X)` blt 16. Each is a test
    that fails.
  - `stack_vector(V,^N)` is blt 06 (FMT_CONV.ESP:13 `sv_to_hv`).
  - `equal_string(S,T)` is blt 68, and `string_tail(S,P,^T)` is blt 33.
  - `substring(S,P,L,^R)` is blt 32 and `search_character(S,B,E,C,^P)` is blt 5c. These two
    are **two cells long**: the operands past the third are the high bytes of an `integer` cell
    after the instruction. Seen in p_wshell.esp:467 `32 00 03 02` + `integer 0`, and in
    PCPSDSTR.ESP:155 `5c 02 00 01` + `integer 06070000`.
  - INFERENCE: `stack_vector` fails on anything but a stack vector, going by the clause that
    falls through after it.
  - Not witnessed: a backward `search_character`, with B > E, as morphana
    `_simpos/pathname.esp:53` uses it. kl0 refuses it.
- Step 3c said `pmi b0` had **no witness**, from two held predicates. That was wrong: 12 kappa
  predicates use it. Step 3d (2026-11-24, same table) witnesses:
  - `{}` is pmi b0 (`typewin.esp:259` `:refute(PBEDIT,Item,{})` gives `b0 01`;
    `PCAACCA.ESP:93` `set_status(...,{})` gives `b0 03`);
  - a four-element vector `{X,Y,W,H}` is pmi b4 with four unify instructions
    (`p_tgraph.esp:299`);
  - `vector_to_list(V,Tail,^L)` is blt 6e (`dict_io.esp:55`, `6e 00 03 00`; operand roles from
    `BCMSEQUEN.ESP:432`, `6e 03 00 00`). TR-044 App A.8 has the 1984 form
    `vector_to_list(Vector,^List)`. The middle argument is the tail (INFERENCE); only `[]` is run;
  - `set_subvector(V,P,L,S)` is blt 34, two cells long (`p_tgraph.esp:299`; the argument order is
    TR-044 App A.4);
  - add_immediate and subtract_immediate with the result in another register (`bar_v.esp:384`,
    `as_pred.esp:254`), and `put_variable_t A, X` with A != X (`p_tgraph.esp:70-72`).
- Step 3e (2026-11-24, same table) witnesses pmi ca, a first-clause guard: `ca 00 00 n` and a
  constant cell; if A0 is bound and not the constant, jump to cell + 3 + n (the second clause),
  else fall through (`h.esp:189` `draw_string(nil,...):-!;`, `c_grade_ex.esp:125`
  `set_pattern(256,_,_,_):-!;`). The unbound case is INFERENCE from the source. All 1,025 held
  uses have R = 0 (MEASURED). It also witnesses blt f2 as `==` in a test-and-branch, read as blt f0
  (`g_window.esp:15`, `( Display == color,!, ... ; true )`: `f2 02 03 00`). The difference from f0
  is UNKNOWN.
- Step 3e also witnesses, each on held kappa or paragraph code beside its source
  (`psi/README.md`, "the interrupt brackets, the vector puts, the bit operations"):
  - `inhibit_interrupt` / `allow_interrupt` are blt 9a / 9b, no operands (`TERMCODE.ESP:181-193`).
    They are no-ops in the interpreter (OURS: no interrupts are modelled);
  - vectors of one, five and six elements are pmi b1, b5, b6; `b7 A 0 n` puts an n-element vector
    (`HLCAPRSUB.ESP:427`, `receiver.esp:680`, `p_MAIN.esp:444`, `p_icon.esp:229`). MEASURED: every
    held use is followed by exactly that many element cells;
  - `and`, `or`, `shift_left` and `shift_right` (TR-044 A.6) are blt 50, 51, 54 and 55, written
    `X, Y, ^R` (`TERMCODE.ESP:85, 188`, `CONVERTER.ESP:41-45`, `KP_TIMER.ESP:43-45`). The 32-bit
    word's sign and overflow are not printed, so negative operands and results of 2**31 or more
    are refused;
  - blt 40 and 49 take the result in another register (`p_wwin.esp:420`, `c_grade_ex.esp:26`).
- OVW (lines 2662–2704) states that categories (7) system control and (8) language-processing
  support are **not described** in the user manuals.

**MEASURED:** 241 populated class-1 entries in `sysidat`, of which 111 distinct opcodes are used in
the held packages.

**Gap:**

- The names in the two lists were not counted, because the OCR is too noisy for a reliable count.
  The mapping name ↔ class-1 opcode is **UNKNOWN** for all but slot access (`27`).
- The privileged marks (`*`, `**`) in TR-044 App A were lost in OCR. The page images (TR-044
  pdf 38–43) must be read to recover them.
- The argument modes for the 1987 additions come only from TM-388 App D, with modes `+ - ? ^`.
- MP7002-1 would close all three gaps.

**Exceptions** (KNOWN, TH App A pp.246–249):

- A failing built-in calls `exception_handler(Pred,Type,ErrArg,ArgsVector,Addr)`.
- There are 32 system exception types: built-in, user (`raise`), trace and interrupt.
- The handler table sits at the bottom of the global stack, and `exception_hook` saves the old
  value on the trail.
- The exception type numbers are **UNKNOWN**.

## 5. ESP support in KL0

KNOWN (TH App A pp.241–245):

- An object is a pointer to an object descriptor, followed by its slots.
- The descriptor holds the method-table base and mask and the slot-table base and mask.
- The method key is `n·2^24 + a + n` and the slot key is the atom number; collisions use direct
  chaining.
- The lookup from object to code is done in microcode.
- Methods are cut through `load_choice_point`/`method_cut`.

MEASURED: method calls in `.ptf` carry a selector name/arity atom, not a key; the key is presumably
built at load time or by microcode.

**UNKNOWN:** the descriptor word layout, the hash function width, and how class objects differ
from instances in memory.

## 6. What is enough to build a KL0 engine, and what is not

| Need | Status |
|---|---|
| WAM semantics, stack frames, choice points, cut, indexing | Enough: TH App C, TM-444 |
| Tag set | Names MEASURED; pairing INFERENCE with 6 anchors (§2) |
| Instruction field format | KNOWN |
| Opcode ↔ mnemonic | 109 rows MEASURED from known plaintext (`../../../psi/kl0_opcodes.tsv`, 2026-11-24; 100 before step 3c's nine), of 101 class-0 and 111 class-1 opcodes used. The rest are refused by `psi/kl0.py`; its census ranks them by use |
| Built-in opcode ↔ name and modes | Largely UNKNOWN |
| Object-descriptor layout and loader behaviour | UNKNOWN beyond TH App A |
