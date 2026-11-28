# KL1-B model status: what `PimKL1B` executes, and what it does not

`bsv/PimKL1B.bsv` is the separate KL1-B execution path. It is not the
diagnostic ISA in `PimPU`; the two must not be merged. This page records
the split the repository convention asks for: decode completely,
execute partially, document the rest. Encodings are in
`kl1_encoding.md` (PIMOS assembler table, 263 entries); the model's
word and tags are in `kl1_architecture.md` §2 and `plan.md`.

The status labels are:

- **documented** — the semantics come from a primary-source prose or
  page image cited here.
- **inferred** — the mnemonic and operand packing are unambiguous but
  no prose semantics were found; the inference is named.
- **stand-in** — the model's behaviour is a deliberate approximation of
  a documented instruction whose real mechanism is not modelled yet.

## Implemented

| mnemonic | opcode | model semantics | label | test |
|---|---|---|---|---|
| `set_value` | 0x14 | `R[b] = INT(a)`; TR-246's `set_value Xj, Gi` writes the goal-record argument slot | stand-in | `PimKL1BTb` |
| `set_variable` | 0x13 | `R[b] = UREF(a)`; same goal-slot stand-in | stand-in | `PimKL1BTb` |
| `put_value` | 0x34 | `R[b] = R[a]` | documented (TR-246 p. 7) | `PimKL1BTb` |
| `put_variable` | 0x33 | `R[b] = UREF(a)` | stand-in | `PimKL1BMiscTb` |
| `get_value` | 0xbc | `R[b] = R[a]` | stand-in | `PimKL1BMiscTb` |
| `get_bound_value` | 0xbd | `R[b] = heap[R[a][11:0]]` | stand-in | `PimKL1BTb` |
| `write_value` | 0x25 | `heap[HP] = R[a]; HP++` | documented (TR-246 p. 7) | `PimKL1BTb` |
| `write_variable` | 0x24 | `heap[HP] = UREF(a); HP++` | documented (TR-246 p. 7) | `PimKL1BTb` |
| `write_constant` | 0x20 | `heap[HP] = c40; HP++` | documented (TR-246 p. 7) | `PimKL1BStructTb` |
| `write_integer` | 0x21 | `heap[HP] = INT(c24); HP++` | inferred | `PimKL1BIntTb` |
| `write_nil` | 0x22 | `heap[HP] = NIL; HP++` | documented (TR-246 p. 7) | `PimKL1BNilTb` |
| `put_list` | 0x2e | `R[a] = LIST(HP)` | documented (TR-246 p. 7) | `PimKL1BStructTb` |
| `put_constant` | 0x30 | `R[a] = c40` | documented (TR-246 p. 7) | `PimKL1BStructTb` |
| `put_integer` | 0x31 | `R[a] = INT(c16)` | inferred | `PimKL1BIntTb` |
| `put_nil` | 0x32 | `R[a] = NIL` | documented (TR-246 p. 7) | `PimKL1BNilTb` |
| `put_atom` | 0x40 | `R[a] = ATOM(c8)` — atom ID in operand c; atom table not modelled | model convention / inferred (c-field packing inherited from `set_atom`; PIMOS atom-operand records carry inline atom names, encoder.kl1:310-364) | `PimKL1BPutAtomTb` |
| `put_atom_1..31` | 0x41-0x5f | `R[a] = ATOM(op - 0x40)` — quick forms, atom ID in opcode | inferred (opcode-embedded atom ID attested by inst_tab.kl1's quick-form comment; a-register destination is the put_* analog) | `PimKL1BPutAtomTb` |
| `wait_value` | 0xa4 | halt if `deref(R[a]) != deref(R[b])` | documented (TR-246 p. 5) | `PimKL1BFailTb` |
| `wait_constant` | 0xa0 | halt if `deref(R[a]) != c40` | documented (TR-246 p. 5) | `PimKL1BConstFailTb` |
| `wait_list` | 0xa6 | halt if the deref is not a list | documented (TR-246 p. 5) | `PimKL1BWaitTb` |
| `wait_integer` | 0xa1 | halt if the deref is not INT c16 | inferred (PIMOS r_c16 variant) | `PimKL1BWaitTb` |
| `set_constant` | 0x10 | `args[Gi] = c40` | documented (TR-246 p. 7) | `PimKL1BSetTb` |
| `set_integer` | 0x11 | `args[Gi] = INT(c16)` | documented (TR-246 p. 7) | `PimKL1BSetTb` |
| `set_nil` | 0x12 | `args[Gi] = NIL` | documented (TR-246 p. 7) | `PimKL1BSetTb` |
| `set_atom` | 0x00 | `args[Gi] = ATOM(c8)` — operand c is the atom ID; atom table not modelled | documented (TR-246 p. 7) | `PimKL1BMiscTb`, `PimKL1BSetAtomTb` |
| `set_list` | 0x18 | `args[Gi] = LIST(HP)` | documented (TR-246 p. 7) | `PimKL1BSetTb` |
| `read_constant` | 0xb0 | backtrack-or-halt if `args[argPtr] != c40`, else advance | documented (TR-246 p. 5) | `PimKL1BSetTb` |
| `read_integer` | 0xb1 | backtrack-or-halt if `args[argPtr] != INT c24`, else advance | inferred (PIMOS c24 variant) | `PimKL1BSetTb` |
| `read_nil` | 0xb2 | backtrack-or-halt if `args[argPtr]` is not NIL, else advance | documented (TR-246 p. 5) | `PimKL1BSetTb` |
| `read_atom` | 0xb3 | backtrack-or-halt if `args[argPtr]` is not ATOM, else advance | documented (TR-246 p. 5) | `PimKL1BMiscTb` |
| `read_variable` | 0xb4 | `R[a] = deref(R[a])` | documented (TR-246 p. 5) | `PimKL1BTb` |
| `get_constant` | 0xb8 | compare `deref(R[a])` with c40; bind an unbound REF cell; backtrack-or-halt on mismatch | documented (TR-246 p. 6) | `PimKL1BGetTb` |
| `get_integer` | 0xb9 | backtrack-or-halt unless `deref(R[a])` is INT c16; bind if unbound REF cell | inferred (PIMOS c16 variant) | `PimKL1BGetTb` |
| `get_nil` | 0xba | backtrack-or-halt unless `deref(R[a])` is NIL; bind if unbound REF cell | documented (TR-246 p. 6) | `PimKL1BGetTb` |
| `get_atom` | 0xc0 | backtrack-or-halt unless `deref(R[a])` is ATOM; bind if unbound REF cell | documented (TR-246 p. 6) | `PimKL1BGetTb` |
| `add` | 0xf4 | `R[c] = INT(R[a] + R[b])` | inferred (guard built-in, TR-246 p. 5) | `PimKL1BArithTb` |
| `subtract` | 0xf5 | `R[c] = INT(R[a] - R[b])` | inferred (guard built-in, TR-246 p. 5) | `PimKL1BArithTb` |
| `multiply` | 0xf6 | `R[c] = INT(R[a] * R[b])` | inferred (guard built-in, TR-246 p. 5) | `PimKL1BArithTb` |
| `divide` | 0xf7 | `R[c] = INT(R[a] / R[b])`, halt on zero | inferred (guard built-in, TR-246 p. 5) | `PimKL1BArithTb` |
| `modulo` | 0xf8 | `R[c] = INT(R[a] % R[b])`, halt on zero | inferred (guard built-in, TR-246 p. 5) | `PimKL1BArithTb` |
| `equal` | 0xf2 | backtrack-or-halt unless both INT and equal | inferred (guard built-in, TR-246 p. 5) | `PimKL1BGuardBacktrackTb` |
| `not_equal` | 0xf3 | backtrack-or-halt unless both INT and unequal | inferred (guard built-in, TR-246 p. 5) | `PimKL1BArithTb` |
| `read_variable_without_deref` | 0xa7 | no-op by design: the register already holds the raw value; only read_variable (0xb4) follows a REF | inferred (regass.kl1: read_variable_without_deref = read_variable minus deref) | `PimKL1BNoopTb` |
| `wait` | 0xe0 | halt on unbound UREF; a bound argument advances | inferred (TR-246 p. 5 passive unification; no suspension in this model) | `PimKL1BNoopTb`, `PimKL1BWaitUnboundTb` |
| `collect_value` | 0x1d | no-op GC marker: emitted when a value's last use is detected; this model has no collector | inferred (compiler mrb.kl1) | `PimKL1BNoopTb` |
| `execute` | 0x61 | `narg = a; pc = label(b:c)` | stand-in | `PimKL1BControlTb` |
| `enqueue_goal` | 0x63 | append label to an 8-entry queue | stand-in | `PimKL1BControlTb` |
| `suspend` | 0x69 | append label; jump to it when the queue was empty, else the head | stand-in | `PimKL1BSuspendTb` |
| `proceed` | 0x60 | pop the FIFO head; halt when empty | stand-in | `PimKL1BTb`, `PimKL1BControlTb` |
| `halt` | 0x71 | halt | — | — |
| `jump` | 0x67 | `pc = label` (c16) | inferred (mnemonic and c16_exe packing) | `PimKL1BJumpTb` |
| `try_me_else` | 0x68 | push CP {label,argPtr,narg,HP}, fall through | stand-in | `PimKL1BCpTb` |
| `fail` | 0x73 | pop CP, restore state, jump to label; halt if empty | stand-in | `PimKL1BCpTb` |
| `otherwise` | 0x6a | pop CP (discard the alternative), set arity, jump to label; halt if empty | inferred (instrtbl.kl1 `otherwise(N, Pred/N)`, c8_c16_exe type; 389 occurrences in `pimm_kernel360E.sav`, binary context shows execute/otherwise/try_me_else sequences) | `PimKL1BOtherwiseTb` |
| `switch_on_non_vector` | 0x2b | `switch_on_non_vector R, Ari, Label`, 2-word `r_r_c16_i` (word 1 = op, R, Ari; word 2 = label). Non-vector: jump to the label. Vector: **halt** -- Ari is an output register that receives the vector's arity, and the model has no vector layout to read it from. | partial; inferred (klb_opr.kl1 334-348 for the layout; regass.kl1 361-362 `Out=[X2]` and index.kl1 900-902 `switch_on_constant(Ari, ...)` for Ari; `tagVector` = 0x07 is a model convention) | `PimKL1BSwitchVecTb` |
| `switch_on_constant` | 0x2c | `switch_on_constant R, [K=Label, ...], Else`, `r_c16_c16_16s_sw`: word 0 = op, R, Length; then Length two-word entries (K; else label in bits 31-16, K's label in bits 15-0). Jump to K's label when the deref equals K, to the else label when no entry matches. Model conventions: entries scanned in order, one per `step()`; absolute labels; an unbound value, Length 0, or Length > 4095 halts. | inferred (klb_opr.kl1 470-482 and 504-535 for the layout; optimize.kl1 30-42 and index.kl1 507-509 for match/else; the probe order is not stated in the corpus) | `PimKL1BSwitchConstTb` |

`deref` resolves one REF level: `deref(w) = (w[39:32] == REF) ?
heap[w[11:0]] : w`. A REF whose heap cell is itself a REF does not
chain; the REF-chain test exercises one level only.

## Not implemented: decoded, halts loudly

The module's default case halts on any other opcode, so an unimplemented
instruction never runs silently. The families below are decoded by the
encoding table but not executed, with the blocking reason:

| family | examples | reason |
|---|---|---|
| passive unification reads | `read_eagerly` | needs the suspension machinery |
| atoms and vectors | `put_vector`, `put_structured_constant` | vector layouts and the structured-constant stream are not documented in the corpus |
| extended arithmetic | `add_extended`, `subtract_extended`, `multiply_extended`, `divide_extended` (tag 0x22) | the 64-bit/vector extended forms are not documented in the corpus |
| control beyond the queue | `hash_on_constant` | goal/choice-point machinery partially modelled; `try_me_else`/`fail`/`otherwise`, guard backtracking and `switch_on_constant` are implemented; `switch_on_non_vector` executes its non-vector jump only (the vector path halts, see the table above); `hash_on_constant` (0x2d, `r_c16_c16_16s_ha`) is not implemented -- the assembler emits `{table, {Hashsize, Key_label_list}}` (klb_opr.kl1 483-497) and the hash function that places a key is not in the clauses read. *2026-11-20:* the table as loaded is in `library/kbn/kbn.kl1` (`out_hash_table`, `set_entry_part(...,hash_on_cnst,...)`: index = key AND mask, each slot `{count << 16 | offset}` to a run of `{key, offset}` pairs, offsets `Loc - P1 - 1`), so this is no longer blocked on a source; it is not implemented because the bench model is being replaced (`pimos_roadmap.md`) |
| console and I/O | `get_console`, `put_console` | device shim not built |

`get_structured_constant` and the structure reads halt in the same
default case.

## What this means for PIMOS

*2026-11-25, 2026-11-26:* this page describes the bench model `PimKL1B` only. PIMOS
itself runs on the PIM/m core (`bsv/PimmCore.bsv`, `ref/pimm/pimm.py`),
which is a different path: there the roadmap has reached R9
(`pimos_roadmap.md`): all eight pkl1 samples compiled by PIMOS's own
compiler and run through the Listener in lockstep on both models
(`bsv/README.md`, "R8" and "R8's second half"; 2026-11-26), and R9:
MGTP/G (IFS No.22) by its manual's procedure, 6- and 8-Queens, in
lockstep on both models (`bsv/README.md`, "R9"; 2026-11-26), after
`mark_element` on a list cell was added to both. Floating point, IEEE
single, is on both PIM/m models since 2026-11-26 (`docs/float.md`). The paragraph below is the bench model's
state and is unchanged.

*2026-11-27:* ICOT's own KL1 firmware (`pimm.MEkbn`, the held
microprogram, executed word by word in `ref/pu/pu.py`) now runs a
multi-goal program with its own scheduler: `ref/pu/u3_goals.py` (rung U3,
first step) has a driver clause enqueue two goals of the IPL image's
`append/3` through the held `enqueue_goal` (`4c00`-`4c07`) and the held
`proceed` (`216c`-`2224`) take them, 41 of 41 instructions matched with
`ref/pimm/pimm.py` and 3 scheduler picks compared (2 dispatching, 1
empty) with R16 (ccc) started at 1; started at 0, the other open
reading, it makes 1 pick and stops at `12e3`. The goal queue (R14, the
records, R10, R1b) is written by held words only; R13 and W1f, read at
the picks, are still the declared stand-in, as is the rest of the state
before the first instruction (`ref/pu/README.md`, "U3"). *Second step,
same day:* that state is now written by start's own held boot words
(R1b's refill `3380`, `209f`-`20a8`, `20e7`-`210b`, `202d`-`2030`: 199
words) instead of the stand-in (8 stand-ins before, 0 after); the boot
queues a goal of its own, so the third pick dispatches it (firmware only,
not compared), and R16 = 2 from `20a0`-`20a1` settles ccc as the queue's
length + 1. The PMPF flag `209f` stopped on is found (rassy's
`cond PMPF`, set / reset by the entry vector's `2022` / `2021`); which
entry the held system takes is not, so the harness takes the reset
(OURS) and pins the set as a second run (`ref/pu/README.md`, "U3, second
step"). *Third step, 2026-11-28:* suspend and resume run on the held
firmware. In a second program, `driver([], [], X, X, [], Z)`, the first
`append` goal notes X in its guard (`3a3c`-`3a3f`). It then suspends
through the held `suspend` (`1c08`-`1c81`: the record and X's hook,
matched with `pimm.py`'s suspended record). The second goal binds X in
`get_value` and wakes the first through held code (`4d1a`-`4d1e`: the
GSET entry by priority, a push on R14). The woken goal runs to its end:
22 of 23 instructions matched with 1 declared skip, and 4 picks, 3
compared with `pimm.py` (`ref/pu/README.md`, "U3, third step"). *U3d, first
step, 2026-11-28:* a program compiled by ICOT's own compiler runs on the
held firmware to its answer. PIMOS 3.6's KL1 compiler, run on `pimm.py`,
compiled a producer and two consumers of one stream (`go(L, A, B) :-
c(S, A), c(S, B), g(L, S)`, source OURS). Its code then ran on the
firmware as `go([1], A, B)`: both consumers suspend on S (the second on a
variable already hooked, a chain of goal records through cell 15), the
producer's `get_bound_value` binds S and wakes both, and all three run
to their ends. 64 of 68 instructions matched with 4 declared skips, 5
picks (4 compared), and the answer A = B = [1], read out of the
firmware's memory, is `pimm.py`'s (`ref/pu/README.md`, "U3d, first
step"). *U3d, second step* (2026-11-28): four more compiled programs take
the held paths U3 had not run, each to a pinned stop where no held source
gives the next value. Crr runs out in `execute`: the slow path and the
goal switch `4c11` requeue the goal (compared with `pimm.py`), and the run
stops at cell 33. Crr runs out in `proceed`: the run stops at cell 10. A
suspend on two variables pushes the first onto the suspension stack, takes
the many-variable path to the allocator `3334`, and stops at cell 1a4. An
`@priority` goal stops inside `calculate_priority_from_minimum` (`1d94`,
the carry condition) (`ref/pu/README.md`, "U3d, second step"). This
concerns neither `PimKL1B` nor `PimmCore`. The paragraph below is the
bench model's state.

The model can execute a hand-assembled KL1-B program that builds heap
cells and reads them back, and it can prove the deref path. It has a
flat argument-save area (`set_*`/`read_*`), a goal-label queue
(`execute`/`enqueue_goal`/`proceed`/`suspend`) and the integer guard
built-ins, all as model stand-ins rather than TR-246's record areas.
It cannot yet run a PIMOS module: vector/structure construction
(`put_vector`, `put_structured_constant`) halts because the vector
layouts are not in the corpus, and the choice-point and console paths
are not modelled.  `put_atom*` is now implemented as a register write
with the atom ID, but the atom table itself is still not modelled. The next tranches in
`plan.md` name those gaps.
