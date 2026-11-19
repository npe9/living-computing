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
| `put_variable` | 0x33 | `R[b] = UREF(a)` | stand-in | — |
| `get_value` | 0xbc | `R[b] = R[a]` | stand-in | — |
| `get_bound_value` | 0xbd | `R[b] = heap[R[a][11:0]]` | stand-in | `PimKL1BTb` |
| `write_value` | 0x25 | `heap[HP] = R[a]; HP++` | documented (TR-246 p. 7) | `PimKL1BTb` |
| `write_variable` | 0x24 | `heap[HP] = UREF(a); HP++` | documented (TR-246 p. 7) | `PimKL1BTb` |
| `write_constant` | 0x20 | `heap[HP] = c40; HP++` | documented (TR-246 p. 7) | `PimKL1BStructTb` |
| `write_integer` | 0x21 | `heap[HP] = INT(c24); HP++` | inferred | `PimKL1BIntTb` |
| `put_list` | 0x2e | `R[a] = LIST(HP)` | documented (TR-246 p. 7) | `PimKL1BStructTb` |
| `put_constant` | 0x30 | `R[a] = c40` | documented (TR-246 p. 7) | `PimKL1BStructTb` |
| `put_integer` | 0x31 | `R[a] = INT(c16)` | inferred | `PimKL1BIntTb` |
| `wait_value` | 0xa4 | halt if `deref(R[a]) != deref(R[b])` | documented (TR-246 p. 5) | `PimKL1BFailTb` |
| `wait_constant` | 0xa0 | halt if `deref(R[a]) != c40` | documented (TR-246 p. 5) | `PimKL1BConstFailTb` |
| `wait_list` | 0xa6 | halt if the deref is not a list | documented (TR-246 p. 5) | `PimKL1BWaitTb` |
| `wait_integer` | 0xa1 | halt if the deref is not INT c16 | inferred (PIMOS r_c16 variant) | `PimKL1BWaitTb` |
| `set_constant` | 0x10 | `args[Gi] = c40` | documented (TR-246 p. 7) | `PimKL1BSetTb` |
| `set_integer` | 0x11 | `args[Gi] = INT(c16)` | documented (TR-246 p. 7) | `PimKL1BSetTb` |
| `set_nil` | 0x12 | `args[Gi] = NIL` | documented (TR-246 p. 7) | `PimKL1BSetTb` |
| `set_atom` | 0x00 | `args[Gi] = ATOM` | documented (TR-246 p. 7) | — |
| `set_list` | 0x18 | `args[Gi] = LIST(HP)` | documented (TR-246 p. 7) | `PimKL1BSetTb` |
| `read_constant` | 0xb0 | halt if `args[argPtr] != c40`, advance | documented (TR-246 p. 5) | `PimKL1BSetTb` |
| `read_integer` | 0xb1 | halt if `args[argPtr] != INT c24`, advance | inferred (PIMOS c24 variant) | `PimKL1BSetTb` |
| `read_nil` | 0xb2 | halt if `args[argPtr]` is not NIL, advance | documented (TR-246 p. 5) | `PimKL1BSetTb` |
| `read_atom` | 0xb3 | halt if `args[argPtr]` is not ATOM, advance | documented (TR-246 p. 5) | — |
| `read_variable` | 0xb4 | `R[a] = deref(R[a])` | documented (TR-246 p. 5) | `PimKL1BTb` |
| `execute` | 0x61 | `narg = a; pc = label(b:c)` | stand-in | — |
| `enqueue_goal` | 0x63 | append label to an 8-entry queue | stand-in | — |
| `suspend` | 0x69 | append label to the same queue | stand-in | — |
| `proceed` | 0x60 | pop the queue; halt when empty | stand-in | `PimKL1BTb` |
| `halt` | 0x71 | halt | — | — |

`deref` resolves one REF level: `deref(w) = (w[39:32] == REF) ?
heap[w[11:0]] : w`. A REF whose heap cell is itself a REF does not
chain; the REF-chain test exercises one level only.

## Not implemented: decoded, halts loudly

The module's default case halts on any other opcode, so an unimplemented
instruction never runs silently. The families below are decoded by the
encoding table but not executed, with the blocking reason:

| family | examples | reason |
|---|---|---|
| goal-record argument setup | `set_structured_constant`, `set_atom` | `set_structured_constant` needs the constant stream; `set_atom` writes a placeholder atom because the atom table is not modelled |
| passive unification reads | `read_eagerly` | needs the suspension machinery |
| active unification | `get_constant`, `get_variable`, `get_list`, `get_vector`, `get_structured_constant`, `unify_*` | needs argument registers and structure construction |
| atoms and vectors | `put_atom*`, `put_vector`, `put_structured_constant`, `get_atom`, `get_vector` | atom-table and vector layouts are not documented in the corpus; the atom packing clause (`atom`) is an indirect table reference |
| arithmetic and comparison | `add`, `subtract`, `multiply`, `divide`, `modulo`, `equal`, `not_equal`, `integer`; extended `add_extended` and friends | named as guard built-ins in TR-246 p. 5; operand and result conventions not yet extracted |
| control beyond the queue | `switch_*`, `jump`, `try_me_else`, `otherwise`, `fail` | goal/choice-point machinery not modelled |
| console and I/O | `get_console`, `put_console` | device shim not built |

`get_constant` (the one c40 instruction that needs the argument area
in memory rather than the register-file model) halts in the same
default case.

## What this means for PIMOS

The model can execute a hand-assembled KL1-B program that builds heap
cells and reads them back, and it can prove the deref path. It cannot
yet run a PIMOS module: no argument registers, no goal records, no
atom/vector/structure construction, no arithmetic. The next tranches in
`plan.md` name those gaps.
