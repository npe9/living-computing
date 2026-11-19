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
| `wait_value` | 0xa4 | halt if `deref(R[a]) != deref(R[b])` | documented (TR-246 p. 5) | `PimKL1BFailTb` |
| `wait_constant` | 0xa0 | halt if `deref(R[a]) != c40` | documented (TR-246 p. 5) | `PimKL1BConstFailTb` |
| `wait_list` | 0xa6 | halt if the deref is not a list | documented (TR-246 p. 5) | `PimKL1BWaitTb` |
| `wait_integer` | 0xa1 | halt if the deref is not INT c16 | inferred (PIMOS r_c16 variant) | `PimKL1BWaitTb` |
| `set_constant` | 0x10 | `args[Gi] = c40` | documented (TR-246 p. 7) | `PimKL1BSetTb` |
| `set_integer` | 0x11 | `args[Gi] = INT(c16)` | documented (TR-246 p. 7) | `PimKL1BSetTb` |
| `set_nil` | 0x12 | `args[Gi] = NIL` | documented (TR-246 p. 7) | `PimKL1BSetTb` |
| `set_atom` | 0x00 | `args[Gi] = ATOM` (placeholder value; atom table not modelled) | documented (TR-246 p. 7) | `PimKL1BMiscTb` |
| `set_list` | 0x18 | `args[Gi] = LIST(HP)` | documented (TR-246 p. 7) | `PimKL1BSetTb` |
| `read_constant` | 0xb0 | halt if `args[argPtr] != c40`, advance | documented (TR-246 p. 5) | `PimKL1BSetTb` |
| `read_integer` | 0xb1 | halt if `args[argPtr] != INT c24`, advance | inferred (PIMOS c24 variant) | `PimKL1BSetTb` |
| `read_nil` | 0xb2 | halt if `args[argPtr]` is not NIL, advance | documented (TR-246 p. 5) | `PimKL1BSetTb` |
| `read_atom` | 0xb3 | halt if `args[argPtr]` is not ATOM, advance | documented (TR-246 p. 5) | `PimKL1BMiscTb` |
| `read_variable` | 0xb4 | `R[a] = deref(R[a])` | documented (TR-246 p. 5) | `PimKL1BTb` |
| `get_constant` | 0xb8 | compare `deref(R[a])` with c40; bind an unbound REF cell | documented (TR-246 p. 6) | `PimKL1BGetTb` |
| `get_integer` | 0xb9 | halt unless `deref(R[a])` is INT c16 | inferred (PIMOS c16 variant) | `PimKL1BGetTb` |
| `get_nil` | 0xba | halt unless `deref(R[a])` is NIL | documented (TR-246 p. 6) | `PimKL1BGetTb` |
| `get_atom` | 0xc0 | halt unless `deref(R[a])` is ATOM | documented (TR-246 p. 6) | `PimKL1BGetTb` |
| `add` | 0xf4 | `R[c] = INT(R[a] + R[b])` | inferred (guard built-in, TR-246 p. 5) | `PimKL1BArithTb` |
| `subtract` | 0xf5 | `R[c] = INT(R[a] - R[b])` | inferred (guard built-in, TR-246 p. 5) | `PimKL1BArithTb` |
| `multiply` | 0xf6 | `R[c] = INT(R[a] * R[b])` | inferred (guard built-in, TR-246 p. 5) | `PimKL1BArithTb` |
| `divide` | 0xf7 | `R[c] = INT(R[a] / R[b])`, halt on zero | inferred (guard built-in, TR-246 p. 5) | `PimKL1BArithTb` |
| `modulo` | 0xf8 | `R[c] = INT(R[a] % R[b])`, halt on zero | inferred (guard built-in, TR-246 p. 5) | `PimKL1BArithTb` |
| `equal` | 0xf2 | halt unless both INT and equal | inferred (guard built-in, TR-246 p. 5) | `PimKL1BArithTb` |
| `not_equal` | 0xf3 | halt unless both INT and unequal | inferred (guard built-in, TR-246 p. 5) | `PimKL1BArithTb` |
| `execute` | 0x61 | `narg = a; pc = label(b:c)` | stand-in | `PimKL1BControlTb` |
| `enqueue_goal` | 0x63 | append label to an 8-entry queue | stand-in | `PimKL1BControlTb` |
| `suspend` | 0x69 | append label; jump to it when the queue was empty, else the head | stand-in | `PimKL1BSuspendTb` |
| `proceed` | 0x60 | pop the FIFO head; halt when empty | stand-in | `PimKL1BTb`, `PimKL1BControlTb` |
| `halt` | 0x71 | halt | — | — |
| `jump` | 0x67 | `pc = label` (c16) | inferred (mnemonic and c16_exe packing) | `PimKL1BJumpTb` |

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
| atoms and vectors | `put_atom*`, `put_vector`, `put_structured_constant` | atom-table and vector layouts are not documented in the corpus; the atom packing clause (`atom`) is an indirect table reference |
| extended arithmetic | `add_extended`, `subtract_extended`, `multiply_extended`, `divide_extended` (tag 0x22) | the 64-bit/vector extended forms are not documented in the corpus |
| control beyond the queue | `try_me_else`, `otherwise`, `fail`, `switch_on_non_vector`, `switch_on_constant` | goal/choice-point machinery not modelled; the three one-word `switch_on_non_*` type tests are in |
| console and I/O | `get_console`, `put_console` | device shim not built |

`get_structured_constant` and the structure reads halt in the same
default case.

## What this means for PIMOS

The model can execute a hand-assembled KL1-B program that builds heap
cells and reads them back, and it can prove the deref path. It has a
flat argument-save area (`set_*`/`read_*`), a goal-label queue
(`execute`/`enqueue_goal`/`proceed`/`suspend`) and the integer guard
built-ins, all as model stand-ins rather than TR-246's record areas.
It cannot yet run a PIMOS module: atom/vector/structure construction
(`put_atom*`, `put_vector`, `put_structured_constant`) halts because the
atom table and vector layouts are not in the corpus, and the
choice-point and console paths are not modelled. The next tranches in
`plan.md` name those gaps.
