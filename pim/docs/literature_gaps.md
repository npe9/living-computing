# Literature search for the runtime gaps (PIM/m and the other PIMs)

Compiled 2026-11-20. Question: for each thing this project had to design
by guesswork because the PIM/m firmware is lost (`pimm_semantics.md`
"Runtime state"), what do published sources and public archives say the
machine, or a documented sibling, actually did?

This file has three layers:

1. **Sections 1-9**, one per gap: a short answer, labelled by machine,
   with confidence and what is still unknown. Section 0 lists where the
   sources contradict our invented layouts.
2. **"The other PIMs"**: per-machine subsections and a comparison table.
3. **Appendices A-D**: the detailed extractions (field tables, quotes,
   page and line citations) that sections 1-9 summarise. A claim in
   sections 1-9 that carries no quote of its own is backed there.

## How to read the citations

- **Short keys.** `M92` = Nakashima, Nakajima, Kondo, Takeda, Inamura,
  Onishi, Masuda, "Architecture and Implementation of PIM/m", FGCS'92
  vol. 1 pp. 425-435 (held: `FGCS92_Volume_1.pdf`, PDF p. 458 = printed
  p. 425). `OV92` = Taki, "Parallel Inference Machine PIM", same volume
  pp. 50-72. `H92` = Hirata et al., "Parallel and Distributed
  Implementation of Concurrent Logic Programming Language KL1", same
  volume pp. 436-459 (the VPIM paper). `TR-nnn`/`TM-nnn` = ICOT
  Technical Report / Memorandum,
  `https://www.airc.aist.go.jp/aitec-icot/ICOT/Museum/TRTM/TR/TRpdf/trNNNN.pdf`
  and `.../TM/TMpdf/tmNNNN.pdf` (four digits). `TM-1044` = "VPIM 処理方式
  解説書" ("Inside VPIM", 1991-04-05), which we hold as LaTeX inside
  `nonlocal/vpim.tar.Z` (`vpim/DOCUMENT/TM-1044.j/`); cited by file and
  line. `PARAM` = `psdpim/SYSTEM.DIR/PIMM.PARAM` and `CSP` = the console
  package `psdpim/INSTALL.DIR/pimmcsp.ptf`, both inside the held
  `nonlocal/psdpim.tar.Z`.
- **Who read what.** `M92`, `OV92`, `H92`, the first 900 lines of
  TM-1044 chapter 2, TR-715 sections 3-4 and 5.4.6-5.4.8, and `PARAM`
  were read directly for this file from text. Everything else was
  extracted by four reading passes run in parallel (one per appendix),
  from OCR of the scanned reports with the layout figures re-read from
  page images; each quote in the appendices is flagged as checked
  against the page image or OCR-only. The ICOT TR/TM scans have no text
  layer, so an OCR-only quote can carry digit errors.
- **Machine labels.** "PIM/m" means a source describing PIM/m itself.
  "Pseudo PIM/m" is the PSI-III firmware and console in `psdpim.tar.Z`
  (same firmware family and console program, single CPU). "Multi-PSI/V2"
  is the predecessor. "VPIM" is the runtime of PIM/p, /c, /i, /k and is
  explicitly *not* PIM/m's. "Abstract" is the 1987 abstract machine
  (TR-246, TR-248).
- **Inference** is marked as such. "Not found" lists what was searched.

## Which sibling to trust for PIM/m

The sources rank the siblings for us (all three read directly):

- `OV92` p. 54: "KL1 system on the PIM/m, which was implemented in
  microprogram, was made from conversion of Multi-PSI/V2 microprogram by
  hands or partially in automatic translation."
- `OV92` p. 53: "Only the PIM/m inherited the KL1 implementation method
  directly from the Multi-PSI/V2."
- `OV92` p. 61: "The instruction set is KL1-B itself, which is binary
  compatible with Multi-PSI/V2."
- `M92` p. 425: PIM/m "inherits many architectural features, such as the
  mesh network and KL1 execution mechanism, from Multi-PSI/v2."
- VPIM distribution README (held): VPIM is "the source code for KL1
  language processor of all models of the PIM except PIM/m".

So, in order: PIM/m papers; the Pseudo PIM/m files (same firmware
family); Multi-PSI/V2 reports; then PDSS (written to be "widely
compatible with the KL1 system found on Multi-PSI"); then VPIM and
through it PIM/p, /c, /i, /k; then KLIC. VPIM is nevertheless the only
sibling with a field-level design document, and it names Multi-PSI as
the origin of several of its choices (Appendix B, "Synthesis" item 8),
and its tag names (HOOK, MHOOK, MGHOK, DREF, RHOOK, EUNDF, EHOOK, EMHOK,
SHREC, FPREC, CDESC, COD, MOD) are the ones in the PIM/m tag table. It
is the best guide to *shape*; it is not evidence for PIM/m *bits*. A
checkable example: VPIM's string descriptor puts the element size in
the top three bits and the unused-element count in the next five
(TM-1044 `s2.tex` "ストリング・タイプ"), while the PIM/m image itself has
`pad << 27 | type << 24 | words` (`pimm_semantics.md`, checked against
`pimm_ipl.kbn`). Same idea, different bits.

## 0. Where the sources contradict "Runtime state"

"Runtime state" in `pimm_semantics.md` says of itself that it is this
project's design and not a claim about the machine. These are the points
where a source now says the machine, or its nearest relative, did
something else. Whether any of them changes a
trace the current tests check was not examined.

| Our design | What the sources say | Source and machine | Weight |
|---|---|---|---|
| Heap pointer only; "cells are taken in order and never returned" | Free pools for variable cells, list cells and goal records, with registers for each (`FVP`, `FLP`, `FGP`); MRB reclaims cells into them during dereference and unification; a batch copying collector runs when local memory is exhausted | `M92` pp. 427, 429-430 (PIM/m); TR-715 4.4 (Multi-PSI/V2: size-classed free lists refilled from the heap top); `PARAM` "Copying GC" counters (Pseudo PIM/m) | Direct contradiction, for PIM/m itself |
| One ready list, no priorities | A table of goal stacks, one per physical priority; the top goal of the highest non-empty stack runs | TR-585 sec. 3 (Multi-PSI/V2: "goal stack table"); `PARAM`: "Goal Stack Entry Table "GSET"" with a shift count `16'20 - log2(Entry)`, set to `16'18`, i.e. 256 entries, index = priority >> 24 (Pseudo PIM/m; the arithmetic reading is inference); `M92` p. 427 register `GSP` "Goal stack pointer" (PIM/m) | Direct, expected ("No priorities yet") |
| Goal record `{INT next}{INT status}{INT code}{INT n}` + args | No source gives PIM/m's or Multi-PSI's field order. Abstract machine: `Narg`, arguments, code address, next goal record (TR-246 p. 3). Multi-PSI: "predicate code address, arguments, priority and etc." (TR-715 4.4), with its own `GOAL` tag (the CSP tag list ends "... DREF \| GOAL"). VPIM: six control words `{GOAL arity}{HOOK/MHOOK/EOL next}{COD code}{FPREC foster parent}{INT PE}{VECTn environment record}` then arguments. **No sibling has a status word**: "woken once" is carried by the suspension flag record (below) | TR-246, TR-715, TM-1044 `s2.tex` 544-650 | Shape differs; a priority and a foster-parent (shoen) link are certain to be needed |
| `{HOOK, first suspension record}`; a 2-cell suspension record per (goal, variable) | Two distinct cases with two distinct tags. **Single wait: `HOOK` points at the goal record itself**, goals chained through the goal record's link word; no suspension record. **Multiple wait: `MHOOK` points at a 2-word suspension record `{next}{DREF -> flag record}`, all sharing one 2-word flag record `{goal}{count}`** | TM-1044 type table ("HOOK: ゴールレコードへのポインタ (single-HOOK)", "MHOOK: サスペンドレコードへのポインタ (multiple-HOOK)", "DREF: サスペンドフラグへのポインタ") (VPIM); TR-246 p. 3 gives the same two records for the abstract machine; TR-390 fn. 2 says Multi-PSI has "hook variables, multiple hook variables"; the PIM/m tag table has exactly HOOK, MHOOK, DREF | Contradiction in tag use: our `HOOK` always points at a suspension record. Confidence that PIM/m follows the HOOK/MHOOK/DREF split: high (tag names), bits unknown |
| A goal met on two variables is "woken once" by its status cell | The flag record's goal pointer is cleared (VPIM: set to `EOL`) by whoever resumes first; other suspension records then find it dead | TM-1044 ch. 7 (VPIM); TR-246 "suspension flag record ... goal record and suspension count" | Same effect, different mechanism |
| Binding a hooked variable to another unbound variable wakes its goals | VPIM concatenates the two hook chains (the higher-address cell becomes a `REF` to the lower; its waiters go first). PDSS merges too. Multi-PSI/V2 and PIM/m: not documented | TM-1044 ch. 7 (VPIM) | Every documented sibling merges; ours "costs reductions" and is visible in a trace |
| Wake order: oldest waiter runs first | VPIM: hook chain is LIFO and resumed goals go back on the stack of their own priority; the run order of several resumed goals is not stated. Multi-PSI: resumed goal "would be stored back in the former goal pool" (TR-531 2.3.1); order not stated | TM-1044; TR-531 | Unknown for PIM/m; ours is a choice |
| "Newest goal runs first is the model's choice" | Now established for Multi-PSI/V2: body goals are "pushed onto the top of the current goal stack (thus the scheduling is depth-first), except for the last one goal which is executed tail recursively" | TR-585 sec. 3; also `OV92` p. 65 "depth-first scheduling in a computation node" | Confirms our choice |
| A waiting built-in is a suspended stub goal hooked on the first unbound input | Multi-PSI/V2: "a goal which execute the built-in goal is created and is hooked onto the uninstantiated argument". VPIM differs: a "D-code" goal `add(A,B,C) :- wait(A), wait(B) \| builtin:add(A,B,C).` is pushed *ready* and suspends from its own guard | TR-585 sec. 3 (Multi-PSI/V2); TM-1044 ch. 5 (VPIM) | Ours agrees with the nearest relative. Whether the output gets a fresh variable is not stated anywhere |
| Strings `{CDESC, pad<<27 \| type<<24 \| words}` | Agrees with VPIM in structure (descriptor word typed `CDESC`, then untagged 32-bit groups packed from the top bit) and differs in the descriptor bits, as above | TM-1044 `s2.tex` 334-410 | Ours is checked on the real image; keep ours |
| MRB "inferred" as the low tag bit from the o/x names | The console's help text gives two values outright, "REFo(06) or REFx(07)", and lists the tag mnemonics in o/x pairs. VPIM's figure draws MRB above the type field instead | `CSP` (Pseudo PIM/m / Multi-PSI console; decoded two-byte text, see section 3); TM-1044 `s1.tex` 176-200 | Consistent with ours (`asm/kbn.py` already has 0x06 REFo, 0x07 REFx and takes the low bit as the MRB from the PIMOS source). The console is a second witness to the values; it does not say in words that bit 0 is the MRB. VPIM is different |

## 1. Goal record and the ready queue

**PIM/m itself.** `M92` p. 427 lists the control registers: "CGP
Current goal record pointer. GSP Goal stack pointer. SST Suspension
stack top. HP Heap pointer. SP Structure pointer. FVP Free variable
cell pointer. FLP Free list cell pointer. FGP Free goal record
pointer", with `AP` "Alternate clause pointer". So PIM/m has a current
goal record, a goal stack, a suspension stack and a free goal-record
list. The A stage can add "Current goal pointer, CGP, to get a location
of a goal argument" (`M92` p. 428): goal arguments are addressable in
the record through `CGP`. `M92` p. 432 says context switches happen
"every two to three reductions" in real programs and "take dozens of
cycles". No field layout, record size or priority structure is given.

**Pseudo PIM/m** (`PARAM`, read directly). A fixed "Goal Stack Entry
Table "GSET"" with base and "Shift Count (16'20-log2(Entry))"; the
value is `(gsesh, 16'18)`, so 2^8 = 256 entries. Inference: the entry
is indexed by the top 8 bits of a 32-bit priority. The same file gives
a "Passive Unification Stack" (0x200-0x400) and a "Suspension Stack"
(0x400-0x800) in a fixed area. `CSP` has a "goal record inspector"
(`csp_goal_record_inspector`, `get_goal_record_1`, `get_goal_record_2`)
whose code would give the real field order; it is in SIMPOS
package-template form and was not decompiled.

**Multi-PSI/V2** (best documented relative for behaviour; Appendix A
gap 1).
- "Each processor has a goal stack table which is the root of all
  runnable goals. The table has pointers to goal stacks corresponding to
  physical priorities. The processor picks up the topmost goal of the
  highest non-empty goal stack and executes." (TR-585 sec. 3). A goal
  stack is a linked list of goal records (TR-469 sec. 4).
- On commit: "all the user-defined body goals, except for the
  unification goals and the leftmost user goal in the clause, are pushed
  to the goal stacks according to the priority pragmas attached to the
  goals. Unification goals are executed immediately. The leftmost user
  goal is chosen as the next one to be evaluated unless the goal stack
  of the higher priority has a goal." (TR-715 4.1). `enqueue_goal` for
  the later goals and `execute` for the source-leftmost one, emitted
  last, is how the compiler realises this (TR-248 Fig. 5); that
  reconciliation of "leftmost" with TR-585's "last one" is inference.
- "Goal record can be reclaimed at popping from goal stack into a free
  goal record list." (TR-715 4.4).
- "Control information, such as the priority and the shoen resource, is
  cached on the registers as long as the execution context remains
  unchanged." (TR-715 4.2).
- Every reduction ends with the "slit check" for a GC request and
  message arrival (TR-715 4.1).
- Priorities: a shoen has a range `MinPrio..MaxPrio`; a goal's pragma
  gives a position in it, `priority_in_shoen(n)` or
  `priority_to_current(+-n)` in units of 1/4095 of the range (TR-483
  Fig. 2); physical priority width "about 2^12" (TR-373, scan
  degraded).
- Costs (TR-585 Fig. 1; one `append` iteration = 39 microsteps):
  enqueue + dequeue 0.7 of that, about 27 steps (`OV92` p. 66 states
  "5.4 us (27 micro-instruction steps)").

**VPIM** (field-level; Appendix B gap 1). One ready stack per PE; 4096
physical priorities, "based on Multi-PSI"; a 4-word entry per priority
`{lower link}{INT priority}{HOOK goal chain}{higher link}`, non-empty
entries doubly linked; LIFO within a priority; an idle goal at priority
0. Logical priority is 31 bits and kept in the goal's environment
record; the VPIM source maps it by `>> 19`. Goal record: six control
words then arguments (section 0). `H92` p. 455: "A ready goal is
managed in the ready goal pool which has entries for each priority.
Each entry indicates a linked stack of goal records."

**Abstract machine** (TR-246, held): goal record `Narg`, arguments,
code address, next; ready queue "as a stack rather than a queue".

**Best sibling and carry-over.** Behaviour: Multi-PSI/V2, carried over
with high confidence (converted microprogram, binary-compatible
KL1-B). Table size: Pseudo PIM/m's 256 is a parameter of one
configuration; the real PIM/m value is not known. Field layout: only
VPIM documents one; carry over the *set* of fields (arity, link, code,
shoen/foster-parent, priority), not the order.

**Confidence.** High: per-priority LIFO goal stacks, a free
goal-record list, `execute` continuing with the source-leftmost goal
unless a higher priority is waiting, priority and shoen resource cached
in registers. **Unknown:** PIM/m goal record field order and size,
maximum arity per record, how `GSP`/`CGP` are used by `enqueue_goal`,
`execute`, `proceed` step by step, the number of physical priorities on
the real machine.

## 2. Suspension

**PIM/m itself.** `SST` "Suspension stack top" (`M92` p. 427); the tag
table's HOOK, MHOOK, MGHOK, DREF; `try_me_else` "sets the jump target
for suspension or failure in control register AP" (TR-733 fig. 8
comment, Appendix C 2.7). Nothing on record layouts.

**Abstract machine** (TR-246 p. 3, held): a suspension record `{next
suspension record}{suspension flag record}` and a flag record `{goal
record}{suspension count}`; a suspension stack collects the variables
met unbound in the guards and is cleared on commit.

**Multi-PSI/V2** (Appendix A gap 2).
- "a pointer to the suspended goal is written on the variable cells
  (the goal is said to be hooked onto the variables)" (TR-585 sec. 3).
- "There are several types of unbound variables: hook variables,
  multiple hook variables, etc in the actual KL1 implementation. The
  distinction is mainly for optimizations" (TR-390 sec. 4 fn. 2).
- "If there are two unbound variables which may allow to commit a
  clause, the goal is hooked to both to construct an OR-wait suspension"
  (TR-585 4.2). Costs in `append` iterations: single 1.8, two-way 3.7,
  four-way 6.8, suspended built-in 3.3 (`OV92` p. 66: 70 steps single,
  140 steps two-way).
- Body built-in: "executed in-line, except when one of its input
  arguments is uninstantiated. In this case, a goal which execute the
  built-in goal is created and is hooked onto the uninstantiated
  argument." (TR-585 sec. 3).
- A remote `%read` that finds the variable unbound is itself hooked on
  it (TR-715 5.2.2); so a hook chain can hold reply records as well as
  goals. PIM/m's `RHOOK` tag is presumably this (inference).
- Merger: a "merger hooked variable" cell points at a merger record
  `{pointer to output variable}{number of inputs}`; unifying it with a
  cons instantiates the output at once; with a vector, adds inputs;
  only `merge/2` is built in (TR-466 3.3, figs. 2-3). PIM/m's `MGHOK`
  tag is this.
- Record layouts, chain order, variable-variable unification of hooked
  variables: not in any Multi-PSI report.

**VPIM** (the only field-level account; Appendix B gap 2). Single wait:
variable cell = `HOOK` -> goal record; further goals chained LIFO
through the goal record's second control word. Multiple wait: variable
cell = `MHOOK` -> suspension record `{next}{DREF -> flag}`; flag
`{HOOK -> goal, EOL once resumed}{INT count}`. Unifying two hooked
variables concatenates the chains. A resumed goal keeps its priority
and returns to its PE. Body built-in or `enqueue` with an unbound
input: a D-code goal, with the original instruction's module and offset
kept in the goal's environment record so that an exception can name the
built-in. `H92` p. 440: "almost all goals wait for a single variable
... the operation for the goal suspension is just to link the goal to
the original variable. If multiple uninstantiated variables suspend
goal reduction, however, the goal is linked to the variables through a
special structure for multiple suspension."

**Best sibling and carry-over.** VPIM for layout shape (and it matches
TR-246 and the PIM/m tag names); Multi-PSI/V2 for the built-in rule and
costs. The single/multiple split with HOOK/MHOOK/DREF carries to PIM/m
with high confidence. VPIM's compare-and-swap details do not (PIM/m has
one PE per memory).

**Unknown:** PIM/m record sizes and word order; chain and wake order;
what PIM/m does on variable-variable unification of two hooked
variables; whether a suspended built-in's outputs get fresh variables;
where the "original instruction" information for exceptions lives.

## 3. MRB

**Where the bit is.**
- PIM/m papers: part of the 8-bit tag (`M92` p. 428: "8 bit tag for
  data type representation and incremental/ordinary garbage collection.
  The tag bit for incremental garbage collection is called Multiple
  Reference Bit"); "ALU operation and tag manipulation including
  turning on/off MRB are performed in parallel". No bit number.
- Pseudo PIM/m / Multi-PSI console (`CSP`): the help text reads "you
  can see the dereference result ... through REFo(06) or REFx(07) tag"
  and lists mnemonics "INTo | INTx | ATOMo | ATOMx | LISTo | LISTx |
  REFo | REFx | UNDF | ..." (Appendix C sec. 4). The project's tag table (`asm/kbn.py`, from the PIMOS source) already
  has 0x06 REFo and 0x07 REFx and treats the low bit as the MRB; the
  console is an independent witness to the same two values, from the
  firmware side. Its mnemonic list also has `GOAL` after `DREF`, which
  our table lacks (our table stops at 0x3b DREF; `GOAL` = 0x3c is
  inference from list order). The text is stored two-byte; the string
  "REFo(06) or" was re-found for this file after decoding (a plain byte
  search does not find it).
- Polarity: figures use an open circle for off and a filled one for on
  (`M92` fig. 6). "o" = off = single reference = bit clear, "x" = on =
  bit set is inference from the pair 06/07 and those legends; no source
  says "x means on" in words.
- VPIM: tag = "Reserved Bit 1bit, MRB 1bit, Type 6bits" (TM-1044
  `s2.tex` 107-114), drawn above the type field; white = off = single,
  black = on. Different placement from the PSI-lineage machines.
- PSI-II (KL0) tag: "The top two bits of the tag field are used as mark
  bits for the garbage collection. The lowest six bits represent data
  type" (TR-265, Appendix C 2.5). Whether PIM/m's KL1 tag keeps two GC
  bits above a 5-bit type and the MRB is inference; the PIM/m tag table
  (values 0x00-0x3b) fits six bits including the MRB.

**The rules** (PIM/m, `M92` pp. 429-430, read directly). MRB is "a
one-bit reference counter attached to both pointers and objects";
"turned on (overflowed) if the pointer is duplicated"; "an object
directed by a pointer with MRB off can be reclaimed as a garbage after
the (passive) unification is performed through the pointer"; the
exception: "unbound variables each of which can have two reference
pointers with MRB off, for a producer and a consumer". During
dereference "A member of the chain of reference pointers can be
reclaimed if both its MRB and that of its predecessor are off", and the
pipeline computes "SRP (Single Reference Path): MRBs of all the
pointers on the chain are off" and "COL (Collectable): MRBs of the
first two pointers are off". The full invariants (S1-S2, U1-U3, I1-I4)
and maintenance rules are in TR-248 and transcribed in Appendix A gap 3.

**The instructions.**
- `collect_value`: "Reclaim storage area pointed from A_i if A_i is an
  SRP. ... generated when A_i is unified with a void variable in the
  passive part. When A_i references a structure, not only that structure
  but also its substructures referenced through an SRP are reclaimed
  recursively." (TR-248 sec. 6, abstract machine). `H92` table 6:
  "Collect the structure recursively unless its MRB is marked." VPIM
  limits the depth (Appendix B gap 3).
- `collect_list`: "is located at the beginning of the body code for a
  clause having head unification with a list cell, and reclaims the list
  cell if the path to it is single" (`M92` p. 430, PIM/m).
  `collect_vector Ai,Nv` appears in the 1989 Multi-PSI instruction
  lists (Appendix A 3.7); the PIM/m paper does not name it.
- `put_marked_value`, `set_marked_value`, `write_marked_value` and the
  `_marked_variable` forms: "Instructions with the word 'marked' in
  their names have the same functions as those without it except that
  the MRB of the destination is always set. They are for reference
  duplication." (TR-248 sec. 6). TR-248 fig. 5 compiles `p(X) :- true |
  q([X]), r(X).` with `write_marked_value A1,G1` and `put_marked_value
  A1,A1`: both copies of a duplicated reference are marked.
- `put_reused_structure`: attested for PIM/m in TR-733 fig. 8
  (Mitsubishi Denki Giho 66(6), 1992), `put_reused_structure R1, R2, 2`
  with the comment "入力Listのcell回収が可能なら再利用 / 回収不可なら新しい
  List cellを割付" ("reuse the input list cell if it can be reclaimed;
  otherwise allocate a new list cell"). `M92` p. 430 describes the same
  thing as "reuse_list": "used for passing the list cell directly rather
  than putting and getting it to/from the free cell pool. To these
  instructions, SRP is passed through the MRBs of their operands,
  An/Xn." 1987 form: `reuse_list Ai,Aj` "The same as 'put_list A_i'
  except that if the MRB of A_j is reset, use the list cell A_j points
  to in stead of allocating a new one." (TR-248).
- `set_vector_element`: in place "providing the path to the vector is
  single" (`M92` p. 430). On Multi-PSI/V2 an MRB-on vector is not
  copied whole either: a mutable-array scheme makes the update constant
  time, about 2.5 times slower (TR-466 4.1.1); layout not given.
- Our `set_string_element` copying is therefore not what the machine
  does for a singly referenced string (already noted in
  `pimm_semantics.md`); no source describes strings specifically.

**Best sibling.** The abstract machine papers (TR-248, TR-246) for
instruction meanings, the PIM/m paper for the dereference rule, the
console for the bit. Carry-over to PIM/m: high for meanings, since the
opcode names in our table are the 1989 Multi-PSI names.

**Confidence.** High for the rules and the instruction meanings (PIM/m
paper and the abstract-machine papers agree); high for the tag values
06/07; medium for "x = on" (legend plus list order).

**Unknown:** exactly which cells each `collect_*` returns to which pool
on PIM/m, recursion depth of `collect_value`, whether batch GC resets
MRBs on PIM/m (Multi-PSI's tracing GC recomputes them, TR-469; VPIM's
does not).

## 4. Data layouts

- **Word.** 40 bits, tag in bits 39-32 (TM-1074 fig. 3; `M92`).
- **Vectors.** PIM/m tag table: VECT0..VECT6 and VECT with VDESC. No
  PIM/m or Multi-PSI report draws the layout. VPIM: VECT0 has no body;
  VECT1..VECT8 point at n bare element words; VECT points at element 0
  of a body whose preceding word is `{INT, n}` (TM-1044 `s2.tex`
  441-520). PIM/m differs at least in the short range (0..6) and in
  having a `VDESC` tag; whether `VDESC` is the header word of a long
  vector is inference. TR-390 models a vector as a `VECT` cell holding
  both length and pointer, "without loss of generality", which is not a
  layout claim.
- **Strings.** Ours is checked on the image. VPIM: same structure,
  different descriptor bits; element sizes 1, 8, 16, 32; default 16-bit
  (TM-1044 `s2.tex` 334-410).
- **Lists.** Two-word cons, CAR then CDR in VPIM; "the order ... need
  not be the same on each real machine, but then the KL1 compiler's
  setting must be changed to match" (TM-1044 `s2.tex` 421-423,
  translated). Variables are never stored inline in a structure: "a new
  variable cell is allocated separately, and a pointer to the cell is
  stored in the element" (TR-248 5.2). `M92` p. 432 confirms the cost:
  "variables excluded from list cells".
- **Floats.** VPIM: `FLT` points at two `INT` words holding the IEEE
  double, high half first; PIM/p uses a CDESC word and 64 contiguous
  bits instead (TM-1044 `s2.tex` 304-330). PIM/m: not found (it has an
  FPP chip, `M92` fig. 2; `FLTo/FLTx` tags).
- **Atoms.** VPIM: 8-bit cluster number (0xFF = reserved for the OS)
  over a 24-bit local number, `[]` = 0. `PARAM` has "(atomc, 16'200) %
  Atom Counter (0 ~ 2 ** (24-1))" (Pseudo PIM/m), which fits a 24-bit
  local number.
- **Code modules.** Multi-PSI/V2: "Absolute address pointers in a
  module are gathered at the top region in the module to reduce the
  size of sweeping for maintenance in local GC. The rest (and the
  greater part) of the module contains only atomic data, that is, KL1-B
  instructions (with the relative address operand if any) followed by
  their full word constant operands if any." (TR-715 5.4.8). This is
  what the project already found in the images ("the module's GC
  area"). A code address crosses the network as `<module, offset,
  structure ID>`. VPIM (Appendix B gap 4): 16-word header "based on
  Multi-PSI's", reference table, constant table, entry table, CDESC,
  code; a 6-word predicate header before each predicate. PIM/m's
  `PREDH`, `PMI`, `GMI`, `KLB`, `BLT` tags are not explained in any
  source read; `PREDH` as a predicate header is inference from the
  name.
- **Structure IDs** (code only): a 4-word structure entry record
  `{ID-hash link}{address-hash link}{ID}{address}` with two hash tables
  (TR-715 fig. 9); `PARAM` has both tables ("Structure Hash Table",
  "Structure ID Hash Table", 0x400 entries each).

**Best sibling.** VPIM for anything drawn, Multi-PSI/V2 (TM-662,
section 8a) for the module, the real images for PIM/m bits.
**Confidence.** High for the module shape (TM-662 matches the images);
low for vectors and floats (VPIM only, and PIM/m visibly differs). **Unknown:** long-vector header and `VDESC`, float body, module
header word by word on PIM/m (our image analysis is the authority).

## 5. Shoen, foster parents, resources, exceptions

- **PIM/m.** Only that shoen exist and use WTC (`M92` p. 431). Tags
  SHREC, FPREC; the console also lists `FPRECt` (Appendix C sec. 4).
  `PARAM`: "(wtctu, 16'400) % WTC Throw Unit", "(wtcsu, 16'1000000) %
  WTC Supply Unit", "(rsctu, 16'1000) % Resource Throw Unit", "(rscsu,
  16'10000) % Resource Supply Unit" (Pseudo PIM/m).
- **Multi-PSI/V2.** "The foster parents have the shoen status (running,
  stopped or aborted), the child count (the number of child goals
  created on the PE), and the cached resource information of the shoen."
  (TR-715 5.3.2). "Currently, resource is measured by the number of
  reductions." A shoen is created by `execute(Goal, ControlStream,
  ReportStream, MinPrio, MaxPrio, Mask)`; an exception is reported "if
  the logical AND of the 32 bit exception tag and the 32 bit exception
  mask of the shoen is not zero", else passed outward; "there is no
  failure in a shoen. Any kind of failure is treated as an exception"
  and the handler "is to substitute a new goal for the goal that has
  given rise to the exception" (TR-390 sec. 2). Failure of a reduction
  "is reported on the report stream of the shoen with the goal
  information" (TR-715 4.1). Record layouts: not given.
- **VPIM** (Appendix B gap 5): shoen record 24 words and foster-parent
  record 22 words in the document, field by field; resource = reduction
  count, double word, cached per PE; the exception report is always
  `{shoen#exception, ExpNumber, ExpInfo, NewCode, NewArgv}`; a built-in
  is identified by an ID that "corresponds to the Multi-PSI opcode".
- **PIMOS side** (held manual and TR-764, TR-483): control and report
  stream messages; Appendix A gap 5.

**Best sibling.** VPIM for records, and its exception vector is a
PIMOS-facing contract, so it should hold on PIM/m (inference: PIMOS is
the same source on all machines). **Confidence.** Medium for behaviour (Multi-PSI/V2 prose); low for any
layout. **Unknown:** PIM/m record layouts;
exception numbers (the PIMOS source and PDSS are the places to look).

## 6. Inter-processor machinery

- **PIM/m** (`M92` pp. 430-431, read directly). Export table entries
  "never move"; "A remote reference consists of the pair of identifiers
  for PE and the export table entry". Separate tables by MRB: "it
  registers the pointer into MRB-off export table. Pi also registers the
  remote reference into MRB-off import table"; multiply referenced
  objects go in the "MRB-on export/import table", where "Each entry has
  a slot for WEC value". "both export table and import table are content
  addressable by hashing". Code modules have global identifiers; a
  request for a module returns "the module identifier rather than the
  module itself". Network: 9-bit packet bytes "8-bit data field and a
  mark to indicate the header and trailer", path table with a 2-bit
  direction code, 1 KB read and write buffers that "compose/decompose a
  40-bit word from/into packet bytes" in hardware.
- **Pseudo PIM/m** (`PARAM`): "Black Export Table Size 4 * Entry",
  "Black Import Table Size 5 * Entry", white export and import tables,
  black export and import hash tables, a Read Packet Buffer, an
  "Original Network Path Table", a "Multi-Packet Queue Table".
- **Multi-PSI/V2** (Appendix A gap 6): the entries those sizes refer
  to, from TR-715 fig. 7: black import `{ext. ID}{WEC}{imp. cnt}{-> EX
  cell}{col. link}`, black export `{-> data}{WEC_up}{WEC_low}{col.
  link}`, white import `{ext. ID}`, white export `{-> data}`. Five and
  four words: the Pseudo PIM/m parameters match the Multi-PSI figure
  exactly. WEC: export side 64-bit, import side 32-bit, unit 2^24,
  halved on duplication (TR-390 sec. 7). EXREF vs EXVAL: "The data
  referenced by an EXVAL cell is known to have a concrete value."
  Safe/unsafe references and the 6x6 unification table (TR-390 App. A).
  Packet: header `1,0,destination PE (7 bits)`, a "Message Order" byte,
  body bytes, tail `1,1,source PE` (TR-715 fig. 2). Messages named:
  `%throw_goal`, `%read`, `%answer_value`, `%unify`, `%terminated`,
  `%release`. Sizes: throw of a 3-argument goal 65 bytes, read 14,
  answer_value 24. Copy depth: arguments of a thrown goal are not
  copied below the top level; unification values one level.
- **VPIM** (Appendix B gap 6): external reference ID = 8-bit cluster,
  4 flag bits, 20-bit export offset; white entries carry no WEC; 24
  message kinds with field-by-field formats for a different network.

**Best sibling.** Multi-PSI/V2, confirmed by the Pseudo PIM/m table
sizes. **Confidence.** High for the four table kinds and the black
entry sizes; medium for WEC constants; none for message bytes. **Unknown:** message order codes and body byte formats (no
report gives them); how PIM/m addresses 256 PEs (the 7-bit PE field of
the Multi-PSI packet cannot; inference); EXMRF.

## 7. Memory management and GC

- **PIM/m.** Three free pools with registers (section 0). MRB
  reclamation during dereference in the pipeline. "a PE may exhaust its
  local memory space and invoke a batch-mode garbage collector" which
  moves data (`M92` p. 430); after marking, "the import table is scanned
  to find out unmarked entries and send a message for each". TR-733:
  "空いたメモリ領域は再利用される" ("freed memory areas are reused").
  Cost of the pools: "KL1 append performs 10 memory accesses per one
  reduction in our system, while Prolog append does 6" (`M92` p. 432).
- **Pseudo PIM/m** (`PARAM`, `CSP`): "Copying GC" with requested and
  collected word counters and a GC count; `kl1_heap_limit` parameter;
  "(ihp, 16'E0000000) % Initial Heap Top Pointer"; console strings
  "Copying GC End", "Copying GC Memory Shortage", `kl1_heap_limit_a`,
  `kl1_heap_limit_b`, `synchronized_gc`. Two limits fitting two
  semispaces is inference.
- **Multi-PSI/V2.** Free lists for 13 size classes (1-8, 16, 32, 64,
  128, 256 words); "When records in a free list are exhausted, a
  pre-determined number of new records are created on the heap top and
  linked to the free list"; no coalescing (TR-715 4.4). "The garbage
  collector moves all data cells reachable from the prioritized goal
  stacks and the export tables to a new semi-space. After copying, valid
  entries in the import tables are swept. If unmarked entries are found,
  %release messages are sent" (TR-715 5.4.6). The collector recomputes
  MRBs (TR-469). Messages for a collecting PE are buffered.
- **VPIM** (Appendix B gap 7): 256-word pages, nine power-of-two free
  lists per PE, parallel stop-and-copy per cluster. `H92` pp. 441-442.

**Best sibling.** Multi-PSI/V2. **Confidence.** High that PIM/m has
free pools, MRB reclamation and a moving batch collector (its own
paper); medium that the collector is semispace copying (Pseudo PIM/m
strings, Multi-PSI/V2). **Unknown** for PIM/m: pool cell sizes
(a variable cell is one word and a list cell two by the data layouts;
the goal record size is the open one), the GC trigger, GC tag bits.

## 8. The processing element, firmware and boot

`pim_architecture.md` already covers `M92`. New here (details in
Appendix C):

- **Microinstruction format.** A field-layout figure for the 64-bit
  microinstruction is in Nakajima et al., "並列推論マシンPIMのアーキテクチャ"
  ("Architecture of the parallel inference machine PIM"), Mitsubishi
  Denki Giho 66(6), 1992, pp. 74-78, reissued as TR-733 (fig. 4;
  transcribed in Appendix C 2.3). The same article's fig. 8 is a PIM/m
  KL1-B listing of `append`.
- **Other processor papers found:** TM-862 (= ICCD'90), TM-858, TR-799
  and TM-1159 (chip set), TM-1074 and TR-564 (held, now read), TR-265
  (PSI-II hardware: 53-bit microinstruction, instruction word `001111 |
  class(2) | code(8) | operand(24)`). Register-file sizes, the decode
  RAM, TLB and address split are in Appendix C 2.2-2.6.
- **KL1-B instruction word layout on PIM/m:** not in any source; our
  reading of the images is the only evidence. The PSI-II format above
  has the same 8/8/8/8 shape we observe.
- **The firmware binary: what is new.** `pimos_boot_requirements.md`
  ("The firmware binary") already identifies `psdpim/PMPSI.DIR/
  pimm.MEkbn` as the Pseudo PIM/m microcode, 100,864 forty-bit words,
  and sets it aside because "Reading it needs the PSI-III
  microinstruction format, which we do not have". New here: (a) that
  format's field layout is published (TR-733 fig. 4, above); (b) the
  first 2,285 words of the file carry non-zero tag bytes and look like
  a table, the rest like halves of 64-bit microinstructions, and the
  console has a loader named `load_5byte_wcs` (measurement and
  inference, Appendix C sec. 8); (c) `syspsi` has the shape of a full
  32K x 64-bit control-store image, by name the KL0/SIMPOS firmware;
  (d) the console packages include a microcode reverse assembler
  (`pimmutil##csp_micro_reverse_assembler`) and a goal record
  inspector; (e) `PIMM.PARAM` gives the firmware's memory map and
  parameters (sections 1, 5, 6, 7); (f) the IFS abstract says "the
  language processor is implemented entierly by the microprogram code
  of PSI-III" and that the KL0 and KL1 microprograms are swapped
  dynamically. None of the binaries was decoded. They are for the
  PSI-III host, which has the same PU as PIM/m.
- **Boot.** `psdpim/SYSTEM.DIR/boot.init` gives the sequence: clear,
  init, `impl` (load microcode), `patch`, `ipl`, `start`. The sources
  do not agree on names and start addresses, and the differences matter
  to a model that boots this image:

  | Source | IMPL file | IPL file | Start |
  |---|---|---|---|
  | `boot.init` in `psdpim` (Pseudo PIM/m, 1991) | `/usr/psi/pimos/kl1/pimm.MEkbn` | `pimos:pimm_ipl.kbn` + `pimm_ipl.sym` | `20c` |
  | console help text (`CSP`) | - | - | `2000` (Multi-PSI), `200` (Pseudo MPSI) |
  | PIMOS 3.0 primer, CSP auto-boot panel (Appendix D item 8) | `pmpsi:kl1kp.kbn`, patch `pmpsi:kl1pat.com` | `pimos:pimos.kbn` + `pimos.sym` | `202` |

  *Note 2026-11-23: these start values do not compete with the `.kbn`
  header's `0xE0001E81`. That value is the image's own entry,
  `ipl:boot/0` at cell 7,809 of an image loaded at `0xE0000000`; the
  values in the table are arguments to the CSP's `GO`. `20c` is not an
  offset into the IPL image (cell `0x20c` is inside
  `ipl_file_decoder:check_GC_element/8`). What `20c` addresses is
  open; see `icot_software_survey.md` §7.*
  `$IPL` loads the program "on the boot PE". File kinds: `.mbn` for
  microcode, `.kbn` for 40-bit-word images (both the IPL image and the
  pseudo system's IMPL file), `.com` for patches, `.sym` for symbols.
- **FEP and SCSI.** One PE in eight has a SCSI controller board with a
  670 MB disk and the front-end processor, a MELCOM PSI-II or PSI/UX
  (TR-733). To KL1 the bus is a built-in, `scsi_command(SCSI, Unit, LUN,
  Command, Length, Direction, Data, DataP, ^NewData,
  ^TransferredLength, ^ID, ^Result, ^NewSCSI)` (TR-764). The FEP end is
  in `pimfep.ptf` and `pimscsi.ptf` (SIMPOS packages, not decompiled).
  VPIM's chapter 13 documents the same built-in family for the other
  PIMs.
**Confidence.** High for what is quoted from PIM/m papers; the
firmware-file readings are measurements plus inference.

- **Not found:** a format description of `.kbn`; any heap
  `save`/`restore` description; the size of the KL1 microprogram as a
  stated number; a microassembler for this CPU; an emulator of PSI-II,
  PSI-III or PSI/UX.

## 8a. Three unlisted memoranda read from page images

The TM index page omits 384 memoranda whose PDFs are on the server
(Appendix D 1.5); most are two-page IPSJ national-convention papers.
Three were read directly for this file from page images. URL pattern as
for other TMs.

**TM-662**, Miyazaki, Nakagoshi, Doumae, Inamura, Kimura, Nakajima,
"マルチPSI/V2におけるコード形式について" ("Code representation of
Multi-PSI/V2"), IPSJ 38th National Convention, 1989, 2 pp. Multi-PSI/V2;
bears on gap 4 and agrees with what the project found in the PIM/m
images.
- Fig. 1, the module, top to bottom: "モジュール・サイズ" (module size),
  "GCサイズ" (GC size), "モジュール名" (module name), "GC領域" (GC area),
  "コード領域" (code area); the "構造体定数領域" (structured-constant area)
  is drawn outside the module.
- "モジュールを絶対アドレスポインタを含む領域(GC領域)とそれ以外の領域
  (コード領域)の2つに分けた" ("the module is divided into the area
  containing absolute address pointers (GC area) and the rest (code
  area)"). The GC area holds the predicate descriptors for calls out of
  the module and the absolute pointers to structured constants; the
  code area holds only "命令語、モジュール内相対アドレス、整数・アトムなどの
  アトミック・データ" (instruction words, module-relative addresses, and
  atomic data such as integers and atoms).
- Calls out of a module use "モジュールへのポインタ、述語名アトム、引数個数"
  (pointer to the module, predicate-name atom, arity). The called
  module has, at the head of its code area, a hash table, the
  "述語エントリ表" (predicate entry table), keyed by the encoded
  predicate name and arity. The calling module has a **4-word predicate
  descriptor** per called predicate in its GC area, fig. 2 order:
  "キャッシュフィールド" (cache field: the code address, filled on first
  call, "GC時にはこのフィールドはクリアされる", cleared at GC),
  "モジュールフィールド" (pointer to the called module), "述語名フィールド"
  (predicate-name atom and arity, encoded), "モジュール名フィールド" (the
  called module's name atom, "デバッグ用", for debugging).
- Structured constants: the compiler builds them outside the module and
  puts an absolute pointer in the GC area; the code uses
  `put_structured_constant Ai, Lab`, where `Lab` is "GC領域中の構造体への
  ポインタの格納場所を示す相対ポインタ" (a relative pointer to the place in
  the GC area that holds the pointer to the structure).
- Code is generated on the PSI-II front end by a cross system and
  loaded into one PE, then distributed on demand.

**TM-652**, Kimura, Goto, Nakajima, Chikayama, "KL1抽象命令セットの改良に
ついて" ("Improvement of KL1 Abstract Instruction Set"), same
convention, 2 pp. This is where the two KL1-B dialects part. It
proposes clause indexing with `wait`, `is_XXX`, `test_XXX`,
`wait_XXX`, `jump_on_non_XXX`, `check_XXX`; abolishes the structure
register in favour of `read_element V,I,Ai`, `write_var_element`,
`write_val_element`; and adds `mark_element V,I` ("ベクタVのI番目の要素の
MRBをオンにする", turn on the MRB of element I of vector V). It states
two classes of MRB instruction: "回収用の命令" (collecting instructions,
generated when a clause is selected, for data that may be reclaimable)
and "マーク用の命令" (marking instructions, for data whose reference
count rises in the body). Its example uses `jump_on_non_list`,
`read_element`, `get_list_value`: these are the PDSS/VPIM-side names.
The PIM/m table (`switch_on_non_list`, `read_variable`, `put_marked_
value`, `put_reused_structure`) is the other line. The project's `asm/namemap.py` already maps between the two
namings; this paper dates the split to 1989 and gives its reasons
(that the two lines are these is inference from the instruction lists).

**TM-1213**, Takahashi, Takeda, Murasawa, Komori, Sugino, "PIM/mの
メンテナンス系アーキテクチャとCSP" ("Maintenance Architecture and CSP on
PIM/m"), IPSJ 45th National Convention, Oct 1992, 2 pp. PIM/m itself;
bears on gap 8.
- Fig. 1: a PSI-II holds both the FEP and the CSP; the FEP reaches the
  mesh by SCSI, the CSP by a separate "Maintenance Path". "通常はFEPと
  して用いられるPSI-IIの1台をCSPとして兼用する" (normally one of the
  PSI-IIs used as FEP doubles as the CSP). SCSI is fitted "8PEごとに"
  (every 8 PEs).
- The maintenance bus: CSP master, PEs slaves, "シングルマスタ/マルチ
  スレーブの低速バスであり、8bitのデータアドレス共用線と、幾つかの信号線"
  (a slow single-master, multi-slave bus with 8 shared data/address
  lines and a few signal lines).
- CSP functions: start-up and initialisation including power; fault
  messages and detection of a stopped PE; reconfiguration without a
  failed PE; display and change of PE internal resources; debugging at
  three levels, "KL1、KL1-B命令、マイクロ命令": microinstruction level
  (single step, run, break on a micro address, trace), KL1-B
  instruction level (step, run, conditional break; "マイクロプログラムとの
  連係により実現", realised in cooperation with the microprogram), KL1
  level (spy, trace, inspector).
- Fig. 2 and sec. 4: the CSP can touch only the "CSIFR (Console System
  InterFace Register)" group and three registers, MIR, DR, MDR1; every
  other register is reached by loading a microinstruction into MIR and
  stepping once. PIM/m adds a "Refuge Stack" in each PE to save the
  registers this destroys, so that a write to all PEs is a broadcast
  taking constant time.
- "マルチPSIのCSPが行なっていた各種情報の生成を各PEのマイクロプログラムに
  よる生成に切替える" (generation of various information that the
  Multi-PSI CSP used to do is switched to generation by each PE's
  microprogram); start-up "マルチPSI(64PE版)で約10分" (about 10 minutes
  on the 64-PE Multi-PSI) against "256PEの場合でも3分程度" (about 3
  minutes even with 256 PEs).

Not read, same series, most relevant: TM-850 (PIM/m PE architecture),
TM-1021 and TM-1022 (PIM/m front-end processor: GC method; speed),
TM-767 (batch GC and memory consumption on Multi-PSI/V2; downloaded,
not read), TM-346 (inter-PE address management, Multi-PSI version 2),
TM-768 and TM-551 (structure management; distributed unification),
TM-671 (debugging and maintenance functions on the Multi-PSI, 6 pp.),
TM-261, TM-353, TM-354 (PSI-II firmware), TM-212 (ZEUS, the PSI-II
microprogram simulator), TM-849 (the microcode checker "Microlint").

## 9. Where lost software and documents might be obtained

Summary; the verified URL tables, per-item status and the full list of
queries are in Appendix D.

All of this is from the archive survey (Appendix D), which says for each
URL whether it was opened and read, resolved but not read, or only
cited. Hosts: `AIST` = `https://www.airc.aist.go.jp/aitec-icot/ICOT/`,
`UEDA` = `https://www.uedalab.jp/AITEC_ICOT_ARCHIVES/ICOT/` (same tree;
only UEDA serves directory listings).

**Open now, and new to the project.**
- **384 Technical Memoranda that the TM index page does not list**
  (`Museum/TRTM/TM/TMpdf/tmNNNN.pdf`; titles only in
  `Museum/TRTM/TM/TMidx/tmNNNN.idx`). Mostly two-page IPSJ convention
  papers. On our subject: TM-1213, TM-662, TM-652 (read, section 8a);
  TM-850 (PIM/m PE architecture), TM-1021/1022 (PIM/m front-end
  processor), TM-849 (microcode checker), TM-767, TM-346, TM-768,
  TM-551 (Multi-PSI/V2 GC, address management, structure management,
  distributed unification), TM-261, TM-353, TM-354, TM-212, TM-213
  (PSI-II firmware, microprogram simulator, memory management),
  TM-671 (Multi-PSI debug and maintenance). List in Appendix D 1.5.
- **`ifs/manuals/`**, a directory the IFS index does not link: the
  PIMOS manual v1.5 (English, 177 pp., December 1989, the Multi-PSI-era
  manual with an "Administration" chapter on start-up), the PIMOS 3.0
  manual in Japanese (535 pp., PostScript; this is not the `pimosman.ps.Z` that
  `pimos_roadmap.md` lists as wanted, which was not found), PIMOS primers, a KL1 tutorial
  and textbook, ESP manuals. Also mirrored at CMU's AI Repository,
  `https://www.cs.cmu.edu/afs/cs/project/ai-repository/ai/areas/icot/`
  (a June 1995 copy of the IFS FTP tree).
- **The boot chain in prose**: section 6.1 of the Japanese PIMOS 3.0
  manual (read as page images by the survey; translation theirs). The
  code the CSP loads directly, the `*.kbn` file, is from version 3.0
  only the code that IPLs PIMOS; it then loads the modules listed in
  `pimos.ipl` on the FEP (`>sys>csp>PIMOS.DIR`), one path per line,
  `%` for comments, later files overriding earlier ones (so a patch is
  an appended line): `mpsi_bios.sav` or `ppim_bios.sav`, `debugger`,
  `library`, `utility`, `kernel`, `server`, `shell`, `macro`. Up to
  version 2.5 the `.kbn` was produced by a cross system called CAL;
  from 3.0 the `.sav` files are made by the PIMOS unloader. IPL errors
  shown on the CSP include "Unable to open IPL list file", "Undefined
  Module Found", "CheckSum Error". The English 3.0 primer gives the CSP
  auto-boot panel: CLEAR, INIT, IMPL `.mbn` files, IMPL `.kbn` =
  `pmpsi:kl1kp.kbn`, patch `pmpsi:kl1pat.com`, IPL `pimos:pimos.kbn`,
  symbols `pimos:pimos.sym`, start address 202. The same steps appear in
  `boot.init` in `psdpim`, with different file names and start address
  (table in section 8); `pimos.ipl` and the `.sav` names are the ones
  in our object set. No byte-level format of `.kbn`, `.ipl` or `.sav` is given.
- **Mitsubishi Denki Giho back issues**, whole-issue PDFs at
  `https://www.giho.mitsubishielectric.co.jp/giho/pdf/YYYY/YYMM.pdf`:
  nine articles 1986-1992 on MELCOM PSI, PSI II, Multi-PSI, PSI/UX, the
  PIM/m VLSI and the PIM architecture (list in Appendix D item 5; the
  1992 PIM article is the one read as TR-733).
- **IPSJ repository**: 130 on-topic papers 1984-1996, all open
  (Appendix D item 6 lists them with titles in Japanese and English);
  includes the PIM/m element-processor and PIM/m CSP papers.
- **FGCS'84, '88, '92, '94 proceedings** as per-paper PDFs under
  `Museum/FGCS/`.
- **KLIC 3.014** at `https://www.uedalab.jp/~ueda/software/klic-3.014.tgz`.

**Where the hardware is.** The IPSJ Computer Museum page
(`https://museum.ipsj.or.jp/en/computer/other/0002.html`, read) says
"the PIM/p and PIM/m are preserved at the National Science Museum in
Tokyo". Its page on the JAIST collection lists "PSI (ICOT)" with
related manuals and materials. Five printed 1985 ICOT PSI manuals are
catalogued at the JAIST library (CSP operating manual, KL0 built-in
predicates, three SIMPOS manuals); the survey read catalogue records
only. ICOT's own page says TRs and TMs "can be read at National Diet
Library, Japan and Kawasaki Library established by Kanagawa
Prefecture".

**Not in any archive searched:** PSI or PIM microcode source or
listings; SIMPOS; KL0 or ESP system software for PSI; CSP or FEP
manuals; a microassembler; any emulator, ROM dump or disk image.
bitsavers has only the two FGCS'92 volumes. The negative for forums and
blogs is weak (search engines often ignored exact phrases).

**Cited but not located** (ranked in Appendix D): the "Multi-PSI/V2
Console System (CSP) Operating Manual" (cited by the PIMOS primer for
boot configurations; the document that would describe CLEAR, INIT,
IMPL, IPL and the `.mbn` images); the "(Pseudo) Multi-PSI System
Administration Manual"; the PIMOS 2.5 manual; the PSI/SIMPOS operating
manuals; whatever media and documents accompany the preserved PIM/m.

## The other PIMs

Six machines ran KL1 and PIMOS. They fall into two families, and the
sources say so in print (`OV92` p. 61): "PIM/p, PIM/i and PIM/k have
RISC-like instruction set whereas PIM/m and PIM/c have CISC-like micro
programmable instruction set ... The former processors execute machine
instructions which are at a level still lower than KL1-B. The latter
processors interpret KL1-B code by horizontal micro program." By
runtime, the split is different: Multi-PSI/V2 and PIM/m share one
microprogrammed, register-based KL1-B implementation; PIM/p, /c, /i and
/k all take theirs from VPIM, whose KL1-B is memory-based (`H92`
4.6.3: "goal arguments are basically kept on a goal record ... and each
of them is read onto a register explicitly just before it is
demanded") and is "extended from KL1-B for Multi-PSI".

| Machine | Maker | Processor style | Word / tag | KL1 implementation | Runtime layouts documented | Sources (detail in) |
|---|---|---|---|---|---|---|
| Multi-PSI/V2 | Mitsubishi / ICOT | PSI-II CPU, horizontal microprogram (53-bit microinstruction), 200 ns | 40-bit, 8 tag + 32 data; tag values as on the Pseudo PIM/m console (REFo 06, REFx 07) | KL1-B interpreted by microcode, register-based | Behaviour, costs, export/import entries, packet format, free lists, GC; no record field orders | TR-715, TR-439, TR-585, TR-466, TR-390, TR-469, TR-531, TM-662 (Appendix A, sec. 8a) |
| PIM/m | Mitsubishi | 5-stage pipelined, horizontal microprogram (64-bit), 65 ns | same family as Multi-PSI/V2 | Multi-PSI/V2 microprogram converted; binary-compatible KL1-B | Registers, MRB dereference rule, table kinds; Pseudo PIM/m memory map | FGCS'92 pp. 425-435, TR-733, TM-862, TM-858, TR-799, TM-1213, `psdpim` files (sections 1-8a, Appendix C) |
| PIM/p | Fujitsu | RISC-like with macro-call, 4-stage | 40-bit in 64-bit memory words; MRB bit position not published | KL1-B expanded to native code + macro library; VPIM | Prose only; defers to TM-1044 | TR-577, FGCS'92 pp. 414-424, TR-453, TM-1067, TM-1257, TM-1320, FGCS'94 pp. 80-89; TM-1044 ("detail" sec. 1, Appendix B) |
| PIM/c | Hitachi | horizontal microprogram (104-bit) | 40-bit; bits not published | "KL1B/c" interpreted by microcode generated from VPIM | Behavioural only | TR-672, TR-671, TM-870, FGCS'92 pp. 723-730, TR-863, TM-1260; TM-1044 ("detail" sec. 2, Appendix B) |
| PIM/i | Oki | RISC + LIW, 3-stage | 40-bit: lock, GC, MRB bits, 5-bit type, 32-bit value | KL1-B post-compiled to native code + library; VPIM | None | TR-675, TM-1017, TM-1264, TM-1260; TM-1044 ("detail" sec. 3, Appendix B) |
| PIM/k | Toshiba | Toshiba IP1704 RISC | "32 bit" + "4bits tag" as published | native code; VPIM-based runtime hand-ported | One slide | TR-767, TR-768, TR-769, TM-766, TM-1260; TM-1044 ("detail" sec. 4, Appendix B) |

### Multi-PSI/V2 (Mitsubishi / ICOT, 1988)

64 PEs, each the PSI-II CPU with a network controller, 8 x 8 mesh
(TR-715 sec. 3). Everything published is in Appendix A, organised by
the same gap numbers. It is the machine PIM/m's firmware came from, so
its behaviour carries over to PIM/m unless a PIM/m source says
otherwise; the known differences are hardware ones (pipelined
dereference with the SRP/COL flags, hardware packing of 40-bit words
into packet bytes, 256 PEs, full-duplex channels). Surviving software:
the Pseudo Multi-PSI / Pseudo PIM/m firmware binaries and console
(`psdpim.tar.Z`), PDSS (C source, written to be compatible with
Multi-PSI KL1), and PIMOS. No Multi-PSI microcode source was found.

### PIM/p, PIM/c, PIM/i, PIM/k

For none of the four is a field-level goal
record, suspension record, shoen or foster-parent record, or
export/import entry published; every paper defers to the VPIM manual,
TM-1044, which we hold and which Appendix B extracts. What is published
per machine is the processor and how KL1-B reaches it. Details,
citations, the per-machine "what carries over to PIM/m" paragraphs, a
fuller comparison table and the list of what was not found follow.

**Which sibling documents each gap best, and how far it carries to
PIM/m** (summary of the per-gap paragraphs in sections 1-8):

| Gap | Best documented on | Carries to PIM/m |
|---|---|---|
| 1 ready queue behaviour | Multi-PSI/V2 (TR-585, TR-715) | high: same firmware line |
| 1 goal record fields | VPIM (TM-1044 ch. 2) | the set of fields, not the order |
| 2 suspension structures | VPIM (TM-1044 ch. 7), matching TR-246 and the PIM/m tag names | high for HOOK/MHOOK/DREF roles; bits unknown |
| 2 suspended built-ins | Multi-PSI/V2 (TR-585) | high; VPIM's D-code is the other family's answer |
| 3 MRB rules and instructions | abstract machine (TR-248) + PIM/m paper | high |
| 3 MRB bit | Pseudo PIM/m console; PIM/i (TM-1017) for a published bit layout of another design | console: high; PIM/i: none |
| 4 data layouts | VPIM (TM-1044 ch. 2-3); our own image analysis for PIM/m | structure yes, bits no (strings prove it) |
| 5 shoen records | VPIM (TM-1044 ch. 10); PIM/p measurements (TM-1320) | protocol and PIMOS-facing vectors likely; record layouts no |
| 6 tables and messages | Multi-PSI/V2 (TR-715 fig. 7, TR-390), sizes confirmed by Pseudo PIM/m | high for entries; message bytes unknown |
| 7 GC | Multi-PSI/V2 (TR-469, TR-715); VPIM for a parallel variant | high for scheme; parameters unknown |
| 8 processor | PIM/m's own papers; PSI-II (TR-265) for the instruction word | direct |

## The other PIMs: detail

Scope: the four VPIM-based cluster machines of the FGCS final stage. Multi-PSI/V2 and the VPIM manual TM-1044 are covered elsewhere and only cited here.

### 0. Conventions and one-paragraph result

- **Verification labels.** `IMG` = quote/number read from the rendered page image. `TXT` = born-digital or good text layer (FGCS'92/'94 proceedings), not re-checked on an image. `OCR` = tesseract only; digits may be wrong. `HTML` = copied from fetched HTML. Japanese quotes are transcriptions from the page image by the reader (kanji variants possible) unless the item is labelled OCR (TM-1237 only); translations are ours.
- **Page references.** "pr." = printed page; "PDF" = PDF page with the ICOT cover as page 1. FGCS'92 vol. 2: printed = PDF + 447. TM-1260: PDF = printed + 3.
- **URLs.** `A` = `https://www.airc.aist.go.jp/aitec-icot/ICOT/Museum`. ICOT reports: `A/TRTM/TR/TRpdf/trNNNN.pdf`, `A/TRTM/TM/TMpdf/tmNNNN.pdf` (4-digit, zero-padded).
- `[INFERENCE]` marks anything not stated in a source. Nothing is filled in by guess; gaps are listed in section 8.
- **Supporting transcriptions** (full tables, longer quotes, per-page notes) are in `(scratch)/otherpims_work/frag/` (`pimp_jp.md`, `pimc_pimi.md`, `pimk_general.md`, `web.md`); page renders in the sibling directories `p/`, `p2/`, `jp/`, `ci/`, `kg/`, downloads in `dl/` and `dl2/`.

**Result in brief.** Two families are stated in print (Taki, FGCS'92 p. 61, IMG): "PIM/p, PIM/i and PIM/k have RISC-like instruction set whereas PIM/m and PIM/c have CISC-like micro programmable instruction set (Table 2). The former processors execute machine instructions which are at a level still lower than KL1-B. The latter processors interpret KL1-B code by horizontal micro program." All four machines here take their KL1 runtime from VPIM (PSL), not from Multi-PSI: "Only the PIM/m inherited the KL1 implementation method directly from the Multi-PSI/V2" (Taki p. 54, TXT). PIM/p is well documented at instruction and pipeline level; PIM/i has a published instruction list and formats; PIM/c has its micro-step timing, datapath, word width and firmware-generation method; PIM/k has only its cache hierarchy and the name of its processor chip (IP1704). Tag bit assignment is published for PIM/i only (lock, GC, MRB bits + 5-bit type); for PIM/p only the 1988 word figure and the sizes of the fields. **For none of the four is a field-level goal-record, suspension-record, shoen/foster-parent or export/import-table layout published; every source defers to the VPIM manual (TM-1044).** No firmware image, back-end tool, machine manual or emulator for any of the four was found; what survives is the common VPIM PSL source (the PSL-to-C translator is not in the distributed archive), and PIMOS.

### 1. PIM/p (Fujitsu)

#### 1.1 PIM/p -- English primary sources (TR-577, FGCS'92, TR-514)

Sources used in this block (all opened and read in full):

- **[P1]** A. Goto, T. Shinogi, T. Chikayama, K. Kumon, A. Hattori, "Processor Element Architecture for Parallel Inference Machine: PIM/p", ICOT TR-577, August 1990, 22 numbered pp. + Japanese summary (PDF 30 pp.; printed page = PDF page - 4). Journal version cited by [P2]: J. Information Processing 13(2):174-182, 1990. URL: .../Museum/TRTM/TR/TRpdf/tr0577.pdf
- **[P2]** K. Kumon, A. Asato, S. Arai, T. Shinogi, A. Hattori, K. Hirano, H. Hatazawa, "Architecture and Implementation of PIM/p", Proc. FGCS'92 vol. 1 pp. 414-424 (= ICOT TR-770, April 1992; TR PDF page = TR printed page + 1; FGCS p. 414 = TR printed p. 1).
- **[P3]** A. Hattori, T. Shinogi, K. Kumon, A. Goto, "PIM/p: A Hierarchical Parallel Inference Machine", ICOT TR-514, November 1989 (PDF 7 pp.; printed page = PDF page - 1).

##### (a) Hardware

| Item | Published fact | Quote (verification) | Where |
|---|---|---|---|
| Style | RISC-like tagged pipeline processor with two instruction streams (external = compiled code; internal = routines in an Internal Instruction Memory invoked by tag-conditional "macro-call") | "The instruction processing unit(IPU) executes RISC-like instructions which have been tailored to KL1 execution." (text layer) ; "macro-call instructions which have the advantages of both hard-wired RISC computers and micro-programmable instruction set computers" (text layer) | [P2] p. 415 s.2; p. 414 |
| Why not microcode | KL1-B interpretation by microprogram rejected: dispatch cost large relative to trivially short common paths | "when each KL1-B instruction is interpreted by microprogram, the cost for dispatching to microprogram from a fetched instruction will be relatively large" (OCR-only) | [P1] printed p. 5 (PDF 9) s.3.1 |
| Instruction count | "almost 100 varieties of instructions, more than other RISC processors" (OCR-only) | | [P1] p. 6 (PDF 10) |
| Instruction length | "External instructions are either four or six bytes long, so that the instruction buffer has a hardware aligner." (OCR-only) | | [P1] p. 16 (PDF 20) s.5.3 |
| Instruction forms | Table 1 "Form of Basic Instructions" (image-verified): `ALU-op Rs1,Rs2,Rd` (Rd <- Rs1 op Rs2); `ALU-op Rs1,imm,Rd`; `read sub-op Rd,Ra,ofst` (Rd <- M[Ra+ofst]); `write sub-op Rs,Ra,ofst`; `jump cond Rt,mask8,(imm8,)ofst` (+ delayed jump); `jump_and_link Ra,Rd,retofst,ofst` (Rd <- PC+retofst, PC <- Ra+ofst; + delayed); `skip cond Rt,mask8,(imm8)`. sub-op selects width "8, 16, 32 bits, 32 bits with an 8-bit tag, or 64 bits" (OCR-only). | | [P1] Table 1, p. 7 (PDF 11); p. 6 |
| Tag conditions | Table 2 (image-verified): XOR/Not-XOR: tag(Rt) = imm8; OR/Not-OR: tag(Rt) \| mask8 = all 1; AND/Not-AND: tag(Rt) & mask8 = all 0; XORmask/Not-XORmask: (tag(Rt) & mask8) = imm8. No hardware multi-way tag dispatch: "The PIM/p instruction set has only a two-way tag condition" (image-verified). | | [P1] Table 2, p. 7 (PDF 11) |
| Macro-call | Form `MCall cond, R1, R2/imm8, R3/imm8, i-Addr` (OCR-only, [P1] p. 8). Cost: "the cost to invoke the macro-body is only one additional cycle, while usual jump instructions cost three additional cycles" ([P1] p. 9, OCR-only). Return: per-internal-instruction `eoi` bit. Parameters via "indirect value registers" and "indirect access registers" ([P1] p. 9); [P2] says "three indirect registers" (p. 417). | | [P1] s.3.4, s.5.3, Figs 3-4 (PDF 21-22); [P2] s.2.3, Fig. 5 |
| IIM size | "The IIM can store 8K-step instructions." (image-verified on TR-770 PDF p. 11; the FGCS text layer misreads "SK") | | [P2] p. 423 s.5.3 |
| Pipeline | 4 stages D A T B for external instructions; internal instructions add S (set IIM address) and C (fetch from IIM) in front. [P2] Table 1: D decode; A register read for address / address calculation; T register read / cache tag access; B ALU operation + register write / cache data access / condition test. Results written only at B, bypass from B. Taken external branch: "the target instruction starts four clock after the branch instruction starts"; one-slot delayed branches and conditional skip provided. Internal conditional branches ([P2] Table 2, IMG on TR-770 PDF p. 5): B-stage test "No interlock / 5τ branch penalty", A-stage test "1τ branch penalty / 0/1/2τ interlock" ("1τ=1 clock cycle"); the controller picks dynamically ("dynamic conditional branch test stage change", [Asato et al. 1991]). | (text layer) | [P2] pp. 416-417 s.2.2-2.4, Tables 1-2, Figs 3-5; [P1] Table 5 (PDF 20) |
| Cycle time | Design target 50 ns: "The target of the basic machine cycle is 50 nanoseconds. The LSIs are now being fabricated by CMOS standard cell technology that can include up to 80K gates." (OCR-only) ; "four stage pipeline has a 50 nS clock cycle and can be built on an 80K gate CMOS LSI" ([P3] p. 2, OCR-only). The as-built cycle is not stated in [P2]; it is 80 ns, see 1.2. | | [P1] p. 13 (PDF 17); [P3] p. 2 (PDF 3) |
| Word/tag | "data is represented as 40-bit (8-bit tag + 32-bit data), and the general-purpose register has both a data part and a tag part. The MRB is assigned in one bit of the 8 bit tag." (text layer). Memory: "The memory of PIM/p consists of 64-bit width words. Tagged words are placed in aligned 64-bit width words" (image-verified, TR-770 PDF p. 8). MRB polarity: "MRB-on means the bit is 1" ([P2] p. 418). Type field: "The KL1 language processing system uses 44 kinds of data types; these can be expressed in 6 bits. The tag part, however, is 7-bit width except MRB." (image-verified). Type groups tested with one masked compare: Atomic (atom/integer), Vector (null/short/long), Short Vector (1-8 elements), Undefined. **Which of the 8 bits is the MRB, and the tag code table, are NOT given in [P1]-[P3].** | | [P2] pp. 415, 418, 420 s.5.1 |
| Registers | "32 general-purpose registers, several dedicated registers, indirect value registers, and indirect access registers ... specified by a 6-bit register specifier in most instructions. Each general-purpose register has an 8-bit tag and 32-bit data." (OCR-only). Flags live in the tag part of dedicated registers (condition code register `CCR`, slit-check register) and are tested by tag branches. | | [P1] p. 15 (PDF 19) s.5.2 |
| Address space | "The PIM/p has a 4G-byte global virtual address space on each cluster." (OCR-only) | | [P1] p. 13 (PDF 17) |
| Cache | Two caches per PE (instruction, data), 64 KB each; "The CCU has a block status tag for each 32-byte block, and an address tag for each two blocks, that is, every 64 bytes" (OCR-only; block = four tagged words). "The contents of both cache memories are identical" ([P1] p. 15). | | [P1] p. 15 (PDF 19) s.5.1; [P2] p. 418 |
| Coherence | Copy-back, invalidation-based, "similar to Illinois protocol", plus KL1-specific commands. [P1] Table 4 (image-verified): `read_invalidate`, `read_purge`, `exclusive_read`, `direct_write`, `lock_read`, `write_unlock`, `unlock`. | "PIM/p cache protocol is similar to Illinois protocol." (text layer) | [P1] Table 4, p. 12 (PDF 16); [P2] p. 418 s.3.1 |
| Lock | Lock via cache block state + "lock address register", hardware busy-wait: "If the address hits and its status is exclusive, the address can be locked without using the common bus." (OCR-only). Lock frequency "more than 5% of all memory accesses". | | [P1] p. 13 (PDF 17); [P2] pp. 418-419 s.3.2 |
| Free list / deref | [P1] Table 3 (image-verified, RTL as printed): `Push Rs,Ra,ofst`: M[Ra+ofst] <- Rs, Rs <- Ra; `PushTag Rs,Ra,ofst,imm8`; `Pop Rd,Ra,ofst`: Rd <- Ra, Ra <- M[Ra+ofst]; `PopTag Rd,Ra,ofst,imm8`: Rd <- Ra, tag(Rd) <- imm8, Ra <- M[Ra+ofst]; `ReadOrMRB Rd,Ra,ofst`: Rd <- M[Ra+ofst], mrb(Rd) <- mrb(Ra) \| mrb(old Rd); `Deref Rd,Ra,ofst`: Rd <- Ra, Ra <- M[Ra+ofst], mrb(Ra) <- mrb(Ra) \| mrb(old Ra). "Push links a cell to the free list, and Pop allocates it from the free list, in one machine cycle." (OCR-only). In [P2] the same instructions are named `ReadTagWordMrbOr` and `Deref`. | | [P1] Table 3, p. 10 (PDF 14); [P2] p. 418 s.2.5 |
| Slit check | Asynchronous events (GC request, packet arrival, signals from other PEs) are latched in flag registers and polled once per reduction through one summary flag: "The detection of these events at the end of goal reduction is called slit-checking." (OCR-only) | | [P1] pp. 16, 19 (PDF 21, 23) s.5.4 |
| Cluster | 8 PEs + shared memory on a common bus = cluster; 4 clusters per chassis; max 16 chassis = 64 clusters = 512 PEs; single clock distributed to all PEs. Each PE also has a local memory (not on the bus). | "Eight processing elements form a cluster ... The chassis consists of four clusters. The maximum PIM/p system includes sixteen chassis." (text layer) | [P2] p. 414 s.1, Fig. 1-2 |
| Network | Per-PE Network Interface Unit (co-processor) with 16 KB send and 16 KB receive packet memories; per-cluster two routers (RTR), each connecting four NIUs and up to six RTRs -> two independent 6-dimensional hypercubes; wormhole routing, static (E-cube, [P3]) routing, ~1 KB buffer per output port, sub-cube broadcast. Packet build: header (destination, broadcast mode), body written 1/2/4 bytes at a time by co-processor write instructions, end-of-packet marker. SCSI: four ports per cluster (FEP, disks). | "Each RTR connects four NIUs and up to six other RTRs to build a sixth order hypercube network topology." (text layer) | [P2] p. 419 s.4; [P3] s.4 |

##### (b) KL1 implementation approach (English sources)

- Based on VPIM: "The KL1 language processing system for PIM/p is designed on the basis of the VPIM [Hirata et al. 1992]; it is the common specifications of the KL1 language processing system on the two level hierarchical multi-processor system. Most specifications of VPIM are used for PIM/p with no changes." ([P2] p. 420 s.5, image-verified).
- Native compilation in three passes: "The KL1 compiler for PIM/p consists of three passes - the compiler to the intermediate code, the native machine code generator and the optimizer." ([P2] p. 420, image-verified). The intermediate code is KL1-B: "The KL1-B for PIM is extended from KL1-B for Multi-PSI to exploit the PIM hardware efficiently." ([P2] p. 421 s.5.2.1). Instruction classes: passive unification, active unification, argument/element preparation, incremental GC, goal manipulation; "These specifications are identical with VPIM".
- Template expansion with three rule classes ([P2] p. 421-422 s.5.2.2): (1) in-line, e.g. `load Rgp,Pos,Reg -> ReadTagWordShortOffset Reg,Pos*8+40(Rgp)`; `read Rsp,Pos,Reg -> ReadTagWordMrbOr Reg,Pos*8(Rsp)`; `is_vector Reg,Lab -> JumpNotXorUnderMask Reg,VG,Lab,VGM`; `put_integer` (1 cycle/4 bytes, 2 cycles/8 bytes or 2 cycles/10 bytes depending on the constant); (2) conditional subroutine call, e.g. `reuse_vector Arity,Reg -> MacroCallAnd Reg,MRB,Arity,m_AllocVector`, with per-site "roundabout routines" placed in the compiled code; (3) unconditional subroutine/macro call for "Most KL1-B instructions for active unification and body built-in predicates".
  - Layout facts implied by the templates: argument slots are 8 bytes apart (`Pos*8`), and the goal-record argument area starts at byte offset 40 from the goal pointer register `Rgp` (`Pos*8+40(Rgp)`), i.e. five 8-byte header words precede the arguments **[INFERENCE from the one template; the header fields are not named in [P2]]**.
- Optimizer ([P2] p. 422 s.5.2.3): data-flow analysis done separately on tag part and value part; pipeline reordering to remove address-calculation interlocks and fill delay slots. Example `add(X,1,Y)`: 4 cycles/18 bytes -> 2 cycles/10 bytes.
- Run-time routines in three places ([P2] p. 422-423 s.5.3, Fig. 7, image-verified): (1) macro library in the IIM ("the dereference and unification functions"); (2) local memory ("Functions for the suspend/resume processes for KL1 goals and the copying GC routines"); (3) shared memory ("most of the body built-in predicates, the network control routines and the shoen (meta-function) control routines").
- Motivation number: without macro-call, code grows about 3.5x ([P3] p. 4: "the absence of the macro call instruction increases the code by about 3.5 times", image-verified).

##### (c) Runtime layouts (English sources)

- Only general statements: goals are goal records in a goal pool; suspension/resumption as in the KL1-B abstract machine ([P1] p. 3). Per-PE goal pools: "Each PE has two goal pools, one is local for the PE, the other is public; it is accessible from other PEs. If a PE has many goals in its local pool, it moves some goals into its public pool." ([P2] p. 423 s.6, image-verified).
- String/module layout differs from VPIM ([P2] Fig. 6, image-verified): VPIM string = `STRG` pointer -> header tagged word `CNST | num. of TW` followed by `INT`-tagged 40-bit element words; PIM/p string = `STRG` pointer -> 64-bit header `CNST | - | num. of words` followed by untagged 64-bit words of elements. "A module which holds KL1 compiled code, is also realized under the same scheme."
- MRB rules as executed by hardware: MRB of dereferenced result = OR of pointer MRB and cell MRB ([P2] p. 418; [P1] Table 3).
- GC: MRB incremental collection with free lists; "copying GC routines" in local memory; free lists "recreated after grand garbage collection" ([P2] p. 418).
- NOT in the English sources: goal-record field layout, priority-queue structure, suspension-record/hook layout, shoen/foster-parent records, export/import table formats. (See 1.2 for what TM-1067, TM-1065, TM-1257 and TM-1320 add.)

##### (e) Measured performance (English sources)

- [P2] Table 3 "Speedups for Pentomino" (image-verified): Memory shared system (multi-PE x 1 cluster): 1.00 / 1.96 / 3.86 / 7.50 for 1 / 2 / 4 / 8 PEs; Network connected system (1 PE x multi-cluster): - / 1.93 / 3.80 / 7.28. No absolute times or RPS are given in [P2].
- Design-stage targets: "The target speed of PIM/p PE will be between 200K LIPS to 500K LIPS." ([P2] p. 419); "Our performance goal is 10 to 20 MLIPS per 100 PEs." ([P3] p. 1, OCR-only).
- Simulation ([P3] Tables 2-3, image-verified; cluster of 8 PEs, 64 KB cache): common-bus cycles (x1000) BUP 512 / 643 / 1217 / 654 and 8 Queens 337 / 344 / 356 / 461 for standard / doubled code / quadrupled code / no direct-write; average ratios 1 / 1.14 / 1.72 / 1.32; cluster performance ratio (BUP) 1 / 0.95 / 0.67 / 0.94. [P1] p. 13: optimised cache commands "reduce bus traffic by 40-50% ... Direct write affords 35-45% reduction and other optimizations only 5%" (OCR-only, citing Goto, Matsumoto, Tick ISCA'89).

#### 1.2 PIM/p -- additions from the Japanese reports, the 1988 macro-call paper and the 1994 evaluation

Further sources: **[P4]** Hattori, Shinogi, Kumon, Goto, 「並列推論マシンPIM/pのアーキテクチャ」, TR-453, March 1989 (journal: 情報処理学会論文誌 30(12):1584-1592, 1989, cited-only). **[P5]** Miyazaki, Hatazawa, Hirano, 「並列推論マシンPIM/p用KL1処理系の実装」, TM-1067, July 1991. **[P6]** Hatazawa, Arai, 「並列推論マシンPIM/pにおけるクラスタ内自動負荷分散方式の評価」, TM-1257, April 1993. **[P7]** Takei, Kumagai, Hashimoto, Hatazawa, 「PIM/p上のKL1処理系におけるクラスタ間通信方式および荘園里親処理方式の評価」, TM-1320, February 1995 (PDF = pr. + 1). **[P8]** Shinogi et al., "Macro-call Instruction for the Efficient KL1 Implementation on PIM", TR-389, June 1988 (= FGCS'88 paper; OCR). **[P9]** Imai, 「PIM/pシステム入門」, TM-1237, October 1992 (OCR, not image-verified). **[P10]** Kumon, Hatazawa, "The Evaluation of Parallel Inference Machines", Proc. FGCS'94 pp. 80-89, `A/FGCS94/PS/eval-of-PIM.ps.gz` (TXT; tables IMG). **[G1]** TM-1260 (PIM WG Grand Meeting, 1993). [P4]-[P7] were read from page images.

(a) Hardware additions
- **As-built clock 80 ns** (design 50 ns in 1989-90, "60 nsec" design spec in Taki's 1992 table): 「PIM/pは、1クロック当たり80[nsec]で動作している。」 ("PIM/p operates at 80 ns per clock.") [P7] pr. 19 / PDF 20, IMG. Same in [P10] ("The processor's cycle time is 80ns") and [G1] pr. 171.
- Cache geometry and states ([P4] §3.5, pr. 3 / PDF 4, IMG): 「構成は、それぞれ32Bブロック×2セクタ×256カラム×4セットである。」 (32-byte block x 2 sectors x 256 columns x 4 sets). Six block states: EM (Exclusive Modified), EC (Exclusive Clean), SC (Shared Clean), I (Invalid), EML and ECL (the two exclusive states with lock). Taki's table counts 4 states "not including locking state", 4-way.
- Bus: main memory max 256 MB, 8-byte data width, 50 ns bus cycle target ([P4] §4.1). Router: 11x11 crossbar (6 cluster ports, 4 processor ports, 1 control); link 20 MB/s, packets up to 8 KB ([P4] Table 5; design values). Taki Table 3: 33 MB/s x 2 (design spec).
- 1988 design state ([P8]; PDF p. 10 = pr. 9 IMG, rest OCR): Figure 7 "KL1 tagged data representation" draws the 64-bit memory word as three fields `Tag | free | Data` with bit labels 63, 55, 31, 0, i.e. tag in the top byte, a free 3-byte field (footnote: "the free three bytes in each tagged data will be used as reference count field" under the alternative LRC scheme), data in bits 31-0 -- the only published bit-position figure for a PIM/p word, and it is the 1988 design; "The PIM instruction set can use 16 indirect registers" (later papers: three); "32 general-purpose registers and 6 dedicated registers" (condition code, interrupt request, tag mask) (IMG); external instructions "four, six or eight bytes" (later: four or six). The complete 1988 opcode tables are on TR-389 PDF pp. 17-18 (not transcribed; register specifier 6 bits, imm tag 8, offsets 8/16/24/32).
- Instruction mix measured ([G1] pr. 143-144, 157-158, IMG): tag-condition branches 10-15 %; tag-conditional subroutine (macro) call 2-5 %; read-with-MRB-OR 6-18 %; without the special instructions 「現状のソフトでは、2倍の命令を実行しなければならない」 ("twice as many instructions would have to be executed"). Cycle-time miss attributed to the cache-tag lookup / pipeline interaction.

(b) KL1 implementation additions
- Three-level scheme, stated against Multi-PSI ([P5] §1, pr. 2 / PDF 3, IMG): 「マルチPSIでは、KL1を実行するための抽象機械語KL1-Bを水平型マイクロプログラムによって解釈実行する方式をとっている。…PIM/pでは、両者を合わせた方法を採用している。」 ("Multi-PSI interprets KL1-B by horizontal microprogram ... PIM/p adopts a method combining both."). 「PIM/pではKL1プログラムもKL1-B実行系もRISCふうの命令体系を持ったのPIM/pの機械語に翻訳され、直接実行される。」 ("On PIM/p both the KL1 program and the KL1-B runtime are translated into PIM/p machine language and executed directly.") [P5] §3, pr. 3.
- Template rule: 1-6 machine instructions per KL1-B instruction, at most one macro-call per KL1-B instruction; macro bodies in the IIM, "8Kステップ分の大きさしかない" (only 8K steps), larger routines as main-memory subroutines entered through the IIM ([P5] §4.2.1, IMG). Worked expansions ([P5] §4.2.2, IMG): `is_integer(Src,Lfail) -> jnxim(Src,type#integer,Lfail,mask#type)`; `read_wait(Str,ImmPos,Dst,Lsusp) -> rtwm(Dst,Str,ImmPosB), mcximd(Dst,type#ref,mask#type,m_Deref_Suspend), argset(Str,ImmPosB,Dst), jxim(Dst,type#ref,Lsusp,mask#type)`; `unify(Src1,Src2) -> mc(Src1,Src2,arg#dummy,m_Unify)` with body `$CALL(i_ActiveUnify_Sub(I_RegSource1,I_RegSource2)); $RETURN();`.
- Tool chain ([P5] §5, Fig. 5, IMG): `.kl1 -> compiler proper [common] -> KL1-B (.klb) -> post-compiler [per-machine tables/templates; register allocation] -> .asm -> assembler [per machine] -> .rkp -> linker [common] -> .kbn`. 「KL1コンパイラは、全てKL1で書かれており、テンプレートもKL1で書かれている。」 (the whole compiler, templates included, is written in KL1). The runtime path is `VPIM (PSL) -> PSL compiler -> macro-call library / subroutines in machine code` (Fig. 2).
- Code module in memory ([P5] Fig. 6, IMG): `MOD -> module header (words 0-15; word 15 = "Machine Dependent Info.") | other-module reference table | constant table | entry table | DESC+code-area size | code area`. 「コード領域は機種依存であるが、それ以外の部分は全てタグ付ワードで各PIM共通形式である。」 ("the code area is machine dependent; everything else is tagged words in a format common to all PIMs"). Instructions are packed untagged, 4 or 6 bytes.
- Memory-based KL1-B and two-phase compiling: Hirano and Goto, TM-888, May 1990, pr. 1 IMG: 「引数を必要になるまでメモリ上に置いたままとし、レジスタを全て作業用として利用するメモリベース方式を採用した。」 ("we adopted the memory-based scheme, which leaves arguments in memory until needed and uses all registers as work registers"), in contrast to Multi-PSI's register-based scheme. Hirata et al. (FGCS'92 p. 455, TXT): "The KL1 compiler for PIM has two phases. The first phase compiles a KL1 program into an intermediate instruction code; the instruction set is called KL1-B. The second phase translates the intermediate code into a native code." Their Table 6 lists the PIM KL1-B set (load_wait, read_wait, is_*, test_*, equal, suspend; load, read, put_*, alloc_variable/list/vector, write; mark, collect_value/list/vector, reuse_list/vector; unify_atom/integer, unify_bound_value, unify; collect_goal, alloc_goal, store, get_code, push_goal, push_goal_with_priority, throw_goal, execute, proceed) -- operands must be read from the page image before quoting.
- Object code is not KL1-B and not portable ([P9] §1.3, OCR): 「KL1-B のある命令は、システム固有の領域に格納された KL1 処理系への単純な jump 命令になったり、数命令の組合せになったりします」 ("a KL1-B instruction becomes a simple jump into the KL1 runtime stored in a system area, or a combination of a few instructions"); objects are 「PIM/m とオブジェクトコンパチではない」. Two compilers: a self compiler and a cross compiler `kc.sav` run on (pseudo) PIM/m. PIM/p has no per-KL1-B-instruction trace trap, so debug and non-debug code flavours exist.
- Sizes: VPIM in PSL about 50K steps with comments, about 100K when expanded to virtual-machine instructions; shoen code about 20 % / 40 % respectively (TM-1065 §4.1, IMG).

(c) Runtime layouts -- what is documented
- **Goal queues** ([P6] Fig. 1 and §2, IMG): per PE a table of queues by priority, with the queue of the running priority cached as the "current goal queue"; per PE one "overflow goal queue" in a per-cluster table, readable by all PEs. 「カレントゴールキューに一定数以上のゴールが溜ると、オーバーフローゴールキューに移される」 ("when more than a fixed number of goals accumulate in the current goal queue they are moved to the overflow queue"). [P10] p. 86: local queue "can contain up to two goals"; queues are LIFO ("We should call it a goal stack"). Balancing: **get-G** (an idle PE runs a lowest-priority idle goal that takes a goal from another PE's overflow queue) and **throw-G** (a goal resumed by another PE is thrown back to the PE that suspended it). A goal is a "goal record" (ゴールレコード); no field layout.
- **Inner loop evidence** ([P10] Table 2 and Fig. 3): one `append` reduction = 28 instructions: type-check 6, MRB 6, SHOEN 3, write 2, exclusive 2, deref 2, allocation 2, read 1, slit-check 1, move 1, other 2. The trace shows deref with MRB reclamation to a free list, free-list allocation with empty check, `lock_read`/unlock around the active unification, a per-reduction resource counter and one slit check. [P7] pr. 20 fn. 9 (IMG): 「PIM/p上の1 appendリダクションは、28命令、33クロック、2.64[μsec]である。」 ("One append reduction on PIM/p is 28 instructions, 33 clocks, 2.64 us.")
- **Tag in PSL** (TR-493 §2.1, IMG): `TAG = [GC | MRB | TYPE]`, then `VALUE`; no widths. [P10] p. 81: "Eight bits are used for the tag part ... One of the tag bits is used to represent the MRB status, 46 of the rest 128 types are used in the system." MRB is on the pointer (TM-675 pr. 4, IMG).
- **Shoen / foster-parent** (TM-1065 §3.2, IMG; TR-556): prose only. Shoen record in the creating cluster holds control, resource and foster-parent placement information; foster-parent record per cluster holds state, remaining resource, child count; a root foster-parent exists from start-up; child-shoen links chain shoens under a foster-parent; lock order 「子荘園リンク、里親レコード、子荘園レコード」; per-PE caching of the reduction limit and child count; 「荘園レコードを輸出表に、里親レコードを輸入表に登録することにより実装している」 ("implemented by registering the shoen record in the export table and the foster-parent record in the import table"); every message carries a weighted count WTC; start/stop overtaking handled by the six-state machine of TM-1065 Fig. 3. The 1995 "new system" on PIM/p uses a separate shoen table / foster-parent table and a foster-parent hash table ([P7] §2, §4).
- **Export/import** ([P7] §3, IMG): white export (single-reference; WEC is a 1-bit flag) vs black export (multiple-reference; WEC attached to each message), plus indirect export; so the MRB selects the export form. 28 inter-cluster message types are listed in [P7] Tables 3-4 (`%throw_goal %ready %terminated %start %stop %abort %read %answer_value %release %unify %exception %shutdown %request_wtc %supply_wtc %return_wtc %req_resource %sup_resource %ret_resource %ask_stat %answer_stat %sh_profile %sh_prof_req %synchro_gc %req_BEXID_WEX %req_BEXID_BEX %sup_BEXID %nak_start %nak_stop`). Export levels by type in Table 9 (structures go one level per `%read`). On the wire the tag occupies 4 bytes (atomic datum 8 bytes).
- **GC**: MRB incremental plus copying GC when the heap fills ([P10] p. 82); external-reference IDs are stable across cluster-heap GC (TM-1065).
- **Not published for PIM/p**: the position of the MRB bit and the tag code table; field offsets of goal, suspension, shoen and foster-parent records; the macro-body inventory.

(d) Surviving software, firmware, manuals
- Survives (ICOT Free Software, `A/IFS/`; HEAD-checked, archives not opened): IFS #2 VPIM, "Machine: PIM, Multi-PSI; ... Language: PSL; Source Code: 4.7 MB" with "The tools which translate VPIM into C code for conventional machines" (`vpim.tar.Z`, 1,761,111 bytes); IFS #4 PIMOS source/object/manual; IFS #1 PDSS. HTML.
- Not found anywhere: the PSL-to-PIM/p compiler, the PIM/p post-compiler templates and assembler, `kc.sav`, the IIM macro-body image, the PIM/p instruction-level simulator used in [P5] and [G1], the Fujitsu SSL "PIM/p CSP manual" cited by [P9]. A copy of the VPIM distribution unpacked by a parallel task in the same scratchpad (`vpim/vpim/`: `DOCUMENT`, `README`, `src/{basics,functions,interpreter,primitives,structures}`) was grepped once for machine names: it contains only the common PSL source and TM-1044 TeX, with no per-machine back-end directory; the four machines appear in comments and constants only, e.g. `/* PIM/p 0x7ff, PIM/[ik] 0x3ff */`, `/* PIM/p 0xff (8bytes = 1word), PIM/[ik] 0x7f (4bytes = 1word)*/`, `/* in PIM/p,PIM/k 3 */`, a goal-stack entry size noted as "32 bytes PIM/p" (comments not translated or analysed here; the VPIM draft covers the source). `pimosobj.tar.Z` was not checked.
- Short IPSJ-convention papers on PIM/p exist as TMs that are absent from the TM list page but resolve on the same host (found in a parallel task's crawl index, `dl_tmidx/unlisted_table.md`): TM-530 (PIM/p network, 1988), TM-531 (PE architecture, 1988), TM-779 (branch architecture, 1989), TM-1090 (PIM/p simulator, 1991), TM-1091 (「並列推論マシンPIM/pへのKL1処理系の実装」, 1991), TM-1127 (「PIM/pにおけるパイプライン制御方式」 = Asato et al. 1991). Not read.
- Hardware: "Today, the PIM/p and PIM/m are preserved at the National Science Museum in Tokyo." (IPSJ Computer Museum page, HTML).

(e) Measured performance additions
- Append, single PE, real machine: 305 KRPS (nrev1500), 281 KRPS (nrev5000) at 80 ns ([P10] Table 1, IMG; same numbers on the [G1] slide). 1988 estimate was "over 600K RPS" ([P8]). Absolute times at [P10] Table 3: nrev5000 44452 ms, life 11458, mm 13517, pascal 3546, semi 10832, nqueen(11) 28486, qlay(11) 22144, waltz 9667, zebra 8782, puz15(6) 131905.
- Simulator, 1 PE ([P5] Tables 1-2, IMG): macro-calls are 4.9-16.2 % of expanded instructions, 67-84 % of them taken, 9.5-13.7 body instructions each; instruction share expanded / macro body / subroutine e.g. queen 32/31/37, bup3 31/43/26, cube 55/31/14 %.
- Intra-cluster, 8 PEs vs 1 ([P6] Table 1, IMG): speed-up tsumego 1.44, life 3.77, zebra 5.01, mastermind 7.66; life loses to instruction-count growth 22 % and CPI growth 75 %. Load-distribution cost 17-22 us = 3-4 reductions ([P10] Table 4).
- Inter-cluster ([P7], IMG): message handling is 17-42 % of run time (Table 8); `%read`+`%answer_value`+`%unify`+`%release` exceed 90 % of messages; integer round trip 186.1 us, list 250.8 us (Table 12); shoen/foster-parent creation+deletion 10395 clocks = 832 us (about 315 appends), foster-parent switch 198 clocks = 15.9 us, one shoen message 710 clocks, one inter-cluster goal 7045 clocks = 564 us (Table 19).

**Carry-over to PIM/m.** Carries over as concept and cross-check: the 40-bit word (8-bit tag with MRB + 32-bit data; PIM/m's PU is likewise "a 40-bit pipelined microprocessor", Nakashima et al., FGCS'92 vol. 1 pp. 425-435, TXT), the MRB dereference rule (result MRB = OR along the chain, reclaim MRB-off indirection cells), slit checking at reduction boundaries, white/black export and WEC/WTC, the shoen/foster-parent protocol and its message vocabulary, and PIMOS-level behaviour. The 28-instruction append breakdown is a useful yardstick for what a PIM/m microroutine must do per reduction [INFERENCE that the categories map]. Does not carry over: object code (stated incompatible, [P9]), the memory-based KL1-B (the register-based scheme is the Multi-PSI one, Hirata p. 455-456, and "Only the PIM/m inherited the KL1 implementation method directly from the Multi-PSI/V2", Taki p. 54), goal-queue structure with overflow queues, every lock/cache-command/intra-cluster mechanism ("a processor of the Multi-PSI or PIM/m corresponds to a cluster of the PIM models with the multi-cluster structure", Taki p. 53), tag codes (PIM/p's sparse 7-bit assignment is its own), and the message set as wire format [INFERENCE: PIM/m's inter-PE messages come with the inherited Multi-PSI implementation; no source read here compares the two wire formats]. All statements in this paragraph that concepts "carry over" are [INFERENCE] from shared lineage (MRB, export/import, WEC/WTC and shoen originated on Multi-PSI and were taken into VPIM: TM-1260 pr. 128, 144); none is a published statement about PIM/m.

### 2. PIM/c (Hitachi)

Sources: **[C1]** Nakagawa, Asaie, Tarui, Ido, Sugie et al., 「並列推論マシンPIM/cシステムの開発 ―密結合負荷分散支援とファームウェア―」, TR-672, July 1991 (PDF = pr. + 1; all pages IMG). **[C2]** Nakagawa, Sugie, 「並列推論マシンPIM/cにおける自動負荷分散支援機構」, TR-671, July 1991 (IMG). **[C3]** Nakagawa, Ido, Tarui, Asaie, Sugie, "Hardware Implementation of Dynamic Load Balancing in the Parallel Inference Machine PIM/c", FGCS'92 vol. 2 pp. 723-730 (TXT). **[C4]** Tarui et al., "Evaluation of the Cluster Structure on the PIM/c Parallel Inference Machine", TR-863, January 1994 (OCR; Tables 3.1/3.2 IMG); short version TR-871 (OCR). **[G1]** TM-1260 PIM/c session pr. 83-89. **[T]** Taki, FGCS'92 vol. 1 pp. 50-72, Tables 1-4 (IMG).

(a) Hardware
- **Style: tagged, horizontally microprogrammed; explicitly not RISC.** 「1語が104ビットからなる水平型マイクロ命令を50nsピッチで実行する。これにより分岐コストを0にできる上、レジスタ間操作とメモリアクセスおよび演算操作をオーバラップして処理可能である。」 ("It executes horizontal microinstructions of 104 bits per word at a 50 ns pitch; branch cost becomes zero, and register operations, memory access and arithmetic can be overlapped.") [C1] §2, pr. 2, IMG. 「PIM/cのプロセッサ[10]はタグアーキテクチャを備えた水平型マイクロマシンである。」 [C1] §5, pr. 4. [T] Table 2: "CISC (micro programmable)", 50 nsec design spec, gate arrays, 0.8 um. Clock in March 1993: 66 ns ([G1] pr. 171, IMG).
- **Micro-step costs** ([C1] §5, pr. 4, IMG): two-way branch 1 step; multi-way branch 2; constant access 1; register access 1 (two banks of 8 registers in parallel); register-file access 2; memory access 3; arithmetic 1 (add/sub, shift and increment in parallel).
- **Datapath** ([C1] Fig. 5, IMG): general registers 2 x 8 words, register files 2 x 256 words, two constant adders, ALU, memory address register, read data register, write data register, three buses, a 1-byte constant from the microinstruction. **Control store 32 kW** (「現在のCS容量: 32kw (64k-SRAM 60個片面実装)」 = "current CS capacity 32 kw, sixty 64k SRAMs mounted on one side", [G1] pr. 89, IMG; [C5] Fig. 2 "104bit x 32kw"); each PE and the cluster controller has its own.
- **Word: 8-bit tag + 32-bit data.** 「PIM/cのPEおよびCCは、マシンサイクル50nsで実行される水平マイクロ命令制御のEU[3]を持つ。レジスタ、内部バスを含め8ビットタグ+32ビットデータのタグアーキテクチャを採用している。マイクロ命令長は104ビット幅とすることにより、KL1の高速実行に必要な動的データ型判定とデータ処理の同時実行を狙った。」 ("The PE and CC of PIM/c have a horizontally microprogrammed EU with a 50 ns machine cycle. A tag architecture of 8-bit tag + 32-bit data is adopted, including registers and internal buses. The 104-bit microinstruction aims at doing dynamic type tests and data processing at once.") **[C5]** Goto, Taki, Nakagawa, Sugie, 「並列推論マシンPIM/c ―概要―」, TM-870 (IPSJ 40th convention, 1990; absent from the TM list page but resolves at A/TRTM/TM/TMpdf/tm0870.pdf), pr. 3, IMG. [C5] Fig. 2 (pr. 4, IMG, small print): Eu = sequence control, ALU, "General Purpose Register 40bit x 8w x 2", "Register File 40bit x 256w x 2", "RAM (Micro Program) 104bit x 32kw"; Bu (cache unit) = access control, lock directory, CAA "18bit x 1k column x 2set", BS "45bit x 4W x 1k entry x 2set", x 2 bank; Nu = output buffer and input buffer "45bit x 64w" each. [INFERENCE] 45-bit storage words = 40 data bits + 5 check bits; and 4W x 5 bytes = the 20-byte block of [C3]. Units: EU (CPU), BU (cache), NU (network, CC only), SU (service-processor interface). The tag bit assignment and MRB position are not published.
- **Cache**: store-back snooping, invalidation type, 5 states (lock state not counted), 2-way, 80 KB, 20-byte blocks ([T] Table 4; [C3] Fig. 1 caption "Each cache has a capacity of 80 Kbytes and consists of 20 byte blocks"). State names are not given. [C5] pr. 3 says the cache has cache commands that save bus traffic for KL1 (「バストラヒックを節約するキャッシュコマンドを有する」, citing Goto et al. ISCA'89) and uses the block state to cut locking overhead; the commands are not listed. Intra-cluster signalling: 16 kinds of signal, one-to-one or broadcast, without shared-memory locking ([C5] pr. 4). Lock detail is in TR-732 (not read).
- **Cluster**: 8 PEs + 1 cluster controller (CC) + main memory on a two-way address-interleaved common bus; 32 clusters, 256 PEs in four cabinets; 160 MB per cluster ([C1] Fig. 1; [C4] §2.1; [T] Table 1).
- **Network**: crossbar, reached only through the CC: "The cluster controller has overall responsibility for network communications" ([T] p. 62). Router: 8 ports within a cabinet, 3 ports between cabinets, four cabinets fully connected ([G1] pr. 89, IMG). 40 MB/s design. One-byte-wide interface: "it takes 27 cycles to send this message through the one-byte-wide network interface" ([C3] p. 728, TXT). "normal system firmware is designed so that all operations involved in communication are executed on the CC", with an alternative mode distributing receive operations to the PEs ([C4] §2.1, OCR).
- **Load-balancing hardware** (the machine's speciality): 16 one-bit slit-check registers per PE with broadcast write and test-and-branch in one cycle ("Each PIM/c processor has 16 EFRs", [C3] p. 725) -- response 1 cycle / 2 bus accesses against 9 cycles / 8 accesses by cache polling ([C1] Table 1, IMG); an 8-bit cluster load register in the network, readable in 11 cycles ([C2] Table 2; [C3]). A `Fetch&Or` instruction updates the requester bitmap ([C2] §4.2.2). No hardware free-list or dereference support is described.

(b) KL1 implementation
- **KL1-B interpreted by a microprogram that is machine-generated from VPIM.** 「KL1B命令の仕様はICOTが開発したVPIM[9](Virtual PIM)として供給されている。VPIMは…ロード/ストア命令に換算して33Kstepをこえる大規模なものである。」 ("The KL1B instruction specification is supplied as VPIM ... over 33K steps counted in load/store instructions.") [C1] §4, IMG. Chain ([C1] Figs. 6-7, IMG): VPIM -> PSL expander -> register allocator -> syntax expander -> micro expander (micro templates) -> micro address generation -> micro linker -> micro debugger, with optimisers added at each stage in version 2. 「やってない。泥臭い仕事は全部機械にやらせたかった。その結果処理系が遅くなってしまったが、自動変換でバグが入りにくくPIMOSの立ちあげは早かった。」 ("[Hand optimisation of VPIM?] No. We wanted the machine to do all the dirty work. The system became slow as a result, but automatic conversion let few bugs in and PIMOS came up quickly.") [G1] pr. 83, IMG.
- **Variant "KL1B/c"**: 「この統合により派生したKL1Bのスーパーセットを KL1B/c と呼んでいる。」 ("The superset of KL1B derived by this merging is called KL1B/c.") [C1] §7, pr. 6, IMG; produced by an instruction-merging tool (KL1Bインテグレータ) after the KL1 compiler. No instruction list or encoding is published.
- **Control-store overflow**: VPIM subroutine parts that do not fit are placed in main memory as "RISC命令プログラム"/"p-level" code and interpreted by microprogram: 「CSから溢れたコード→主記憶サブルーチンで実行 20倍おそい!!」 ("code overflowing the CS runs as main-memory subroutines: 20 times slower") [G1] pr. 89, IMG. Address-only branch steps were "just under 30 %" of all steps before branch horizontalisation.
- Status: 16-PE partial prototype with microprogram version 3 in July 1991 ([C1] §8); PIMOS shell and listener up about a week after first boot ([G1]).

(c) Runtime layouts: behavioural statements only -- per-PE load pool ("Each processor has its own load pool", [C3] p. 726); a per-PE ready-goal count word in an exclusive cache block; a requester bitmap and per-PE communication area in shared memory; polling at slit-check points for load request, load dispatch and termination. [P10] p. 86: "In the PIM/c and the PIM/k implementation, each processor has one goal queue which is accessed only by the processor" (the original VPIM scheme). Goal record, priority queue, suspension, MRB, shoen/foster-parent, export/import and GC layouts are not published. [INFERENCE] they are VPIM's, packed into a word format that is itself unpublished.

(d) Surviving: nothing machine-specific found. Existed: microprogram versions 1-3, the generator tool chain, a bus monitor. No simulator was ever built (「シミュレータは工数的に無理だった」 = "a simulator was beyond our man-hours", [G1] pr. 83). Unread short papers that resolve on the host: TM-1000 「並列推論マシンPIM/c；水平型マイクロプログラムの自動生成と最適化」 (IPSJ 42nd convention, 1991).

(e) Performance
- Append: 55 / 56 KRPS (nrev1500 / nrev5000) at 66 ns ([P10] Table 1, IMG) -- the slowest PIM; relative to PIM/p 0.20 on nrev5000 and 0.05-0.12 on the other nine benchmarks ([P10] Table 3). Load-distribution cost 239-275 us = 14-16 reductions ([P10] Table 4).
- Microprogram append path ([C1] Table 2, IMG): 416 micro-steps in version 1; savings dispatch -144, branching -64, coarser KL1B instructions -36, hand optimisation of VPIM -32, register-file access -29, micro-template optimisation -11. [INFERENCE] leaves 100 steps.
- Cluster evaluation ([C4] Table 3.1, IMG; 8 clusters, 64 PEs): routing program 53.4 s with the CC doing all receive work, 22.5 s with receive on the PEs; communication overhead 0.3, receive overhead 0.15; speed-up saturates at about 3 PEs per cluster in the normal mode; common-bus utilisation 5.8 % (OCR). Slit-check registers gave 15 % in an 8-PE model; the load-register shortcut raised 8-cluster speed-up from 3.3 to about 5.5 ([C3], TXT).

**Carry-over to PIM/m.** PIM/c is the only other machine that interprets KL1-B in horizontal microcode, so its published micro-engineering numbers are the closest comparison available: per-step costs of branch / register-file / memory access, the weight of dispatch (144 of 416 steps), and the share of address-only branch steps. They are comparison data, not PIM/m facts [the use suggested here is INFERENCE]: the microprogram descends from VPIM/PSL, not from the Multi-PSI firmware (Taki p. 54; TM-1260 pr. 83-84); the KL1-B dialect is the memory-based PIM set further merged into KL1B/c; the datapath (2x8 registers, 2x256 register files, 104-bit microword) is Hitachi's own. Nothing about layouts or encodings can be carried over, since none is published. For scale, the control stores compare as PIM/c 32 kW (overflowing) against PIM/m 5AD6/8000 hex words used = 71.0 % and Multi-PSI 3D38/4000 = 95.7 % ([G1] pr. 143, IMG).

### 3. PIM/i (Oki)

Sources: **[I1]** Sato, Takeda, Ohara, 「並列推論マシンPIM/iプロセッサの設計」, TR-675, August 1991 (PDF = pr. + 1; all pages IMG); journal version Trans. IPSJ 33(3):278-287, 1992 (cited-only, not found online). **[I2]** Ohara, Takeda, 「並列推論マシンPIM/iのアドレストレースによるメモリシステムの評価」, TM-1264, June 1993 (pr. 1 IMG). **[G1]** TM-1260 PIM/i session pr. 76-82 (IMG). **[T]**, **[P10]** as above. [I3] = TM-1017, introduced under "Word" below.

(a) Hardware
- **Style: RISC fused with LIW, no control store.** 「RISCアーキテクチャをベースにLIWを融合し、分岐処理の影響を少なくするアーキテクチャを提案する。」 ("we propose an architecture that takes RISC as base, fuses LIW into it, and reduces the influence of branching") [I1] abstract, IMG. Up to three of four units per instruction: 「4つの実行ユニット(分岐操作、メモリ操作、演算操作、タグ操作)から最大3つの操作として選び指定する」 [I1] §3.1. (The museum page's table says "RISC", its prose "LIW-type".)
- **Instruction formats** ([I1] Fig. 2, IMG), 40 bits fixed: 3-field `S[39:32] M[31:24] P/T[23:0]`; 2-field `S/T[39:24] P/T[23:0]`; 1-field `S/P[39:0]`. S = branch, M = memory, P = arithmetic, T = tag operation. Branch forms: 8-bit with 6-bit signed relative target; 16-bit with a 5-bit register number or an 8-bit condition; 40-bit with a 30-bit target. [INFERENCE] 5-bit register numbers imply 32 registers; the count is not stated.
- **Instruction list** ([I1] appendix, pr. 9, IMG): branch `return`, `goto`, `jmp`, `gosub`, `jmpsub` with Delay2/Delay3 disciplines and conditions tag_eq, not_tag_eq, fwd_eq ("fwd: tagged full word"), eq, ovf, gt, le, test_tag ...; memory `MemOp` (read, write), `LockOp` (read_lock, write_unlock), `StrResOp` (write, write_unlock, unlock); arithmetic `ValOp` (deposit, merge, extract and dynamic variants), `TagOp` (deposit_tag, merge_tag, extract_tag, merge_tag_imm), `PriOp` (find_first_zero/one and reverse), `AOp`, `LOp`, `AdrOp` (set_adr with pre/post modify), `DbyteImmOp`. Three delay-slot disciplines: normal, delayed, cancelled. No dedicated dereference or free-list instruction; dereference is a one-instruction loop `L: mar=r00, if tag(r00)==REF goto_canceled L. read(r00).` ([I1] Fig. 1(b)).
- **Pipeline**: 「PIM/iの3段パイプラインは、命令フェッチ(F)、実行(E)、レジスタ/メモリ書き込み(W)からなり」 (three stages F, E, W; E includes decode, register read, ALU, address calculation, memory access, branch-target calculation) [I1] §3.2, IMG. No condition codes; 5-port register file; separate instruction and data buses.
- **Cycle time**: target 100 ns in 1.2 um CMOS standard cell, about 170K transistors, 208 pins ([I1] §6, IMG); actual 「100ns → 240ns プロセッサは90~110nsで動くはずなのだが...」 ("100 ns -> 240 ns; the processor ought to run at 90-110 ns, but ..."; [G1] pr. 76, IMG; causes: parity errors, shared-memory delay, single system clock). [P10] text says 160 ns, its Table 1 says 240 ns.
- **Word**: 「PIM/i の 1 語は 40 ビット (タグ 8 ビット、データ 32 ビット) である。」 ("One PIM/i word is 40 bits: tag 8 bits, data 32 bits.") [I2] pr. 1, IMG. **Tag layout** (**[I3]** Kato, Sato, Takeda, Ohara, 「並列推論マシンPIM/iのタグアーキテクチャの評価」, TM-1017, IPSJ 42nd convention, 1991; absent from the TM list page, resolves at A/TRTM/TM/TMpdf/tm1017.pdf; pr. 27-28 IMG): 「1ワード40ビットのデータの中で、8ビットがタグ部、32ビットがバリュー部を構成する(図1)。タグ部の中の下位5ビットはリスト、アトムなどのデータタイプを表すために使用し、残りの3ビットはデータへの参照状態を示すMRBビット、一括GC処理を円滑に行うためのGCビット、共有メモリへの排他アクセスを実現するためのロックビットとして使用している。」 ("Of the 40-bit word, 8 bits form the tag part and 32 the value part. The low 5 bits of the tag express the data type (list, atom ...); the remaining 3 bits are the MRB bit showing the reference state, a GC bit for stop GC, and a lock bit for exclusive access to shared memory.") Its Fig. 2 draws the word as fields of width `1 | 1 | 1 | 5 | 32` labelled, from the left, Lock Bit, Garbage Collection Bit, Multiple Reference Bit, Data Type, Value (order of the three 1-bit labels read from the leader lines at 120 dpi). A processor-internal "tag memory" holds tag groups so a group test is one instruction. The 5-bit type codes are not listed. Measured ([I3] Table 1): instructions containing a tag operation 18.7 % on average; tag operations executed in parallel with another operation 68.6 %; speed gain from tag-conditional branches 6.9 %, from the tag memory 1.0 %.
- **Memory system** ([I2] Table 1, IMG): data cache 32K words, code cache 32K words, local data memory 16K words, local code memory 32K words, shared memory 64M words, shared bus 40-bit data / 38-bit address; cache block 4 words. **Coherence by write-update (broadcast)**, six states built from four flags S/E, O/U (supplier of cache-to-cache transfer), C/D, I ([I2], IMG); [T] Table 4: broadcasting, 6 states, direct-mapped, 160 KB + 160 KB. Retrospective: 2-port memory made the protocol costly ([G1] pr. 81).
- **Cluster**: 8 PEs + cluster interface (CIF, an I/O processor) + shared memory on one bus; 2 clusters / 16 PEs in [T] Table 1, but "PIM/i lacks network connection facilities, consequently an eight processor system is the maximum configuration" ([P10] p. 81). No network or message-handling description is published.

(b) KL1 implementation
- **Native translation by a post-compiler plus a small run-time library**: 「各KL1bの処理単位の小さなものは直接展開し、処理単位の大きなものはランタイム・ライブラリとしてローカルメモリに置き…使用したランタイム・ライブラリのコードサイズは約4KWである。」 ("small KL1b instructions are expanded in line; large ones are placed in local memory as a run-time library ... the run-time library used is about 4 KW") [I1] §5.1, IMG. 「制御記憶やそれに相当する別の世界をもたない / ランタイムルーチンのコードをサブルーチン分岐命令で呼び出す」 ("no control store or equivalent; runtime routines are called with subroutine-branch instructions") [G1] pr. 79, IMG.
- **Two generations**: Oki's own experimental systems IP89 / IP90 (used for the TR-675 simulation), then the VPIM port: 「90.12 VPIM実装開始 / 92.5 VPIM動作 / 92.12 処理系の改良により1.5倍」 ("1990-12 VPIM implementation started / 1992-05 VPIM running / 1992-12 1.5x from improvements to the system"; [G1] pr. 76, IMG). How PSL was translated to PIM/i code is not described.

(c) Runtime layouts: none published. [I2] attributes the implementation to TM-1044 and states MRB incremental GC plus a stop GC; 1 page = 256 words.

(d) Surviving: nothing found. Existed: post-compiler, about 4 KW run-time library, an RTL-level simulator. About twenty 2-page IPSJ-convention papers on PIM/i resolve on the host as TMs missing from the list page and were not read, among them TM-846 (overview), TM-847 (PE architecture; downloaded, 6 pp), TM-922 (translator), TM-923 (simulator), TM-929 / TM-1016 / TM-1093 (memory system, parallel cache), TM-1018 (goal communication), TM-1096 (instruction-set evaluation), TM-1097 (KL1 system evaluation), TM-1098 (「KL1のRISC風PIM/i命令への展開について」, expansion of KL1 into PIM/i instructions; downloaded), TM-1247 (KL1 system improvements, 1993).

(e) Performance: append 65 / 65 KRPS at 240 ns ([P10] Table 1, IMG); 0.12-0.31 of PIM/p ([P10] Table 3). Simulation ([I1] Tables 2-5, IMG): 2.5 machine instructions per KL1b on average (2.2-3.0), 0.11 library calls per KL1b; branch operations 38.0 % of instructions (conditional 21.2, unconditional 5.8, tag branches 11.0); over 90 % of branches within the 6-bit range; 26 % time saved by simultaneous operations; parallelism 1.45 per instruction, 1.26 per cycle ([G1]). Memory system: worst overhead against ideal shared memory 1.31 at 8 PEs ([I2] Table 3, OCR).

**Carry-over to PIM/m.** Nothing structural: native LIW code, shared-memory cluster, update-type cache, VPIM runtime. The 40-bit 8+32 word matches PIM/m's width; its published tag split (lock, GC, MRB, 5-bit type) is PIM/i's own and says nothing about PIM/m's assignment. Useful only as independent KL1-B execution statistics (2.5 native instructions per KL1-B instruction, 38 % branch operations, 11 % tag branches), which bound the dispatch and tag-test work a KL1-B microinterpreter does [INFERENCE]; note they come from the pre-VPIM IP89/IP90 KL1b, not the final system.

### 4. PIM/k (Toshiba)

Sources: **[K1]** Asano, Isobe, Sakai, "The Unique Features of PIM/k: A Parallel Inference Machine with Hierarchical Cache System", TR-767, April 1992 (PDF = pr. + 1). **[K2]** Sakai, Asano, Nakase, Isobe, Muratani, Takewaki, "PIM/k: a Parallel Inference Machine with a Cache Hierarchy", TR-768, April 1992. **[K3]** Sakai, Nakase, Takewaki, Asano, "Applying Inter-Cluster Shared Memory Architecture to a Parallel Inference Machine", TR-769, April 1992 (OCR). **[K4]** Muratani, 「拡張MOESIモデルと並列階層キャッシュ・プロトコル」, TM-1066, July 1991 (abstract only). **[G1]** TM-1260 PIM/k session pr. 146-156 (IMG). No FGCS'92 paper on PIM/k (or PIM/i) exists.

(a) Hardware
- **Processor: the whole published description** is "RISC type 32bits processor; 4bits tag for symbol processing languages; and separated bus for data and instruction." ([K1] pr. 3 / PDF 4, IMG) and "A PE is a RISC-type 32 bit micro-processor with tag architecture" ([K2] pr. 3-4, IMG). Cycle 100 ns, custom LSI, 1.2 um ([T] Table 2); single system clock of 100 ns ([G1]). The chip is named in **[K5]** Asano, 「並列推論マシンPIM/k ～ハードウェア アーキテクチャ～」, TM-766 (IPSJ 38th convention, 1989; missing from the TM list page, resolves on the host), pr. 3, IMG: 「図1のPEはIP1704[1]である。」 ("the PE in Fig. 1 is the IP1704"), ref. [1] = 皆川 他, 「AIチップ(IP1704)のアーキテクチャ」, IPSJ 38th convention, pp. 1538-1539, March 1989 (Toshiba's AI processor chip; not obtained). [K5] also states that slit-check messages are carried on the bus with an addressed destination rather than through shared memory. **No instruction format, pipeline, register set or word layout is published in the PIM/k papers themselves** -- the IP1704 literature is where to look. The "4bits tag" conflicts with [P10]'s generic "Eight bits are used for the tag part" for all PIMs; the sources do not reconcile this, and where the MRB bit sits is not stated.
- **Memory hierarchy** ([K2] pr. 3-4, IMG): 16 PEs as four mini-clusters of four; per PE a private memory (128 KB instruction + 128 KB data) and first-level cache (128 KB instruction, 256 KB data, direct-mapped); per mini-cluster a second-level cache (1 MB instruction, 4 MB data, 4-way); global memory 1 GB. "a second-level cache may be considered as a cluster's shared memory ... the memory-level bus may correspond to the inter-cluster networks of the other PIMs." No inter-cluster network; all memory is globally addressed.
- **Coherence**: write-invalidate, copy-back, Berkeley-derived states INV / UNO / NON / EXC at both levels (second-level EXC = an upper cache holds the valid copy); multi-level inclusion kept by a U-bit replacement rule ([K1] pr. 7-11, OCR). Bus commands, [K1] Table 1 (IMG): RSH read shared; RFO read for ownership; WFI write for invalidation; WWI write without invalidation (copy back to second level); FAI flush and invalidation; FWI flush without invalidation. Full state tables A.1-A.5 are in [K1] PDF pp. 15-16 (rendered, not transcribed). The instruction cache has no hardware coherence, only a flush operation.
- **Lock**: atomic read-write on a block in EXC state, else obtain ownership first ([K1] pr. 11, OCR). Each board also carries a slit-check module, a trace memory, two 16-bit event counters and a diagnostic processor; execution is made repeatable by a single clock and synchronised start.

(b) KL1 implementation
- VPIM-based, **ported by hand**: 「VPIM ベースの処理系を最適化しつつ手動でコーディングした」 ("the VPIM-based system was coded by hand while being optimised"); 「VPIM が PIMOS 対応で大きくふくれた時期には、機能追加についていけなかった。」 ("when VPIM swelled to support PIMOS we could not keep up") [G1] pr. 146, IMG. No optimiser existed. Code runs natively (Taki: "lower than KL1-B"); the compiler back end is not described.
- **PIM/k-specific change: internal and external pointers merged.** The standard system: "They are given different tags, REF and EXREF. ... an external reference requires consulting import and export tables"; PIM/k: "we decided to integrate the internal and external pointers ... the tuned KL1 system is reduced half in code size" ([K2] pr. 9-10, OCR). So PIM/k has no permanent export/import tables; "The stop-and-copy GC creates import and export tables temporarily" ([K2] pr. 11, IMG). MRB incremental GC is unchanged.

(c) Runtime layouts: [K3] gives the common system in English prose ("A goal is represented as a goal record which includes appropriate arguments"; "The export table holds the memory address of all exported data, and the import table holds the pairs of the cluster number and the export table entry number"; a typical reduction consumes five heap words, two with MRB GC). The only PIM/k-specific structure shown is a slide ([G1] pr. 150 / PDF 153, IMG): a system shared fixed area holding a goal-request bitmap (one bit per PE) and a "goal post" per PE, plus HOOK cells; no widths or addresses. Each PE has one private goal queue ([P10] p. 86).

(d) Surviving: nothing found. Unread short papers that resolve on the host: TM-1010 to TM-1012 (PIM/k development: KL1 system debugging tools; preliminary evaluation of the KL1 system; TM-1012 downloaded). Existed: a clock-level simulator, "about 7,500 times slower" than hardware ([K2] pr. 11, IMG); runtime versions V02, V05, V12.

(e) Performance: append 76 / 76 KRPS at 100 ns ([P10] Table 1, IMG); 0.27-0.45 of PIM/p ([P10] Table 3); 「PIM/p の 45 %程度」 ("about 45 % of PIM/p", [G1] pr. 146). April 1992: four PEs "about 3.5 times faster than the single PE's case" on 12-queens; first-level hit ratio about 94 % ([K2] pr. 11, IMG). Load-distribution cost 94-116 us = 9-11 reductions ([P10] Table 4). Cache-to-cache transfer about 40 clocks even for one byte; 12 clusters of 1 PE beat 1 cluster of 12 PEs on pentomino ([G1]).

**Carry-over to PIM/m.** None at the machine level: the published material is almost entirely the two-level cache protocol, which has no counterpart in PIM/m. One point is useful by contrast: PIM/k shows that the export/import machinery (REF/EXREF, tables, WEC) is roughly half the runtime code and exists only because clusters do not share memory -- on PIM/m, with one PE per node and no shared memory between nodes, that machinery cannot be dropped, and it comes with the implementation inherited from Multi-PSI/V2 [INFERENCE from Taki p. 53-54].

### 5. What is common to all four (the VPIM runtime as published)

From Hirata et al., FGCS'92 vol. 1 pp. 436-459 (TXT) unless noted. This is the level at which layouts are documented in the open literature; field offsets are in TM-1044 (other agent).
- Word: "Each data word consists of a value part, a type part and a MRB part ... An MRB part is valid, if the value part is a pointer" (p. 455).
- Goal record and pool: "The goal record consists of arguments and an execution environment which includes the number of arguments and the address of the predicate code. A ready goal is managed in the ready goal pool which has entries for each priority. Each entry indicates a linked stack of goal records. Suspended goals are hooked on the responsible variable." (p. 455). Goal records are reclaimed when dequeued ([P10] p. 82).
- Suspension: single-variable suspension links the goal to the variable; multiple suspension goes "through a special structure for multiple suspension"; done with compare & swap (p. 440).
- Memory primitives assumed of every PE: "lock&read, write&unlock, and unlock" (p. 437). Free lists per PE by size (p. 441).
- Export table = hash table + entries with WEC; import table; parallel stop-and-copy GC per cluster; inter-cluster packets may overtake (pp. 437, 447-449).
- Porting: "VPIM has been translated to lower-level machine languages or microprograms automatically or by hands according to each PIM structure." (Taki p. 54) -- PIM/p: PSL compiler to native code + IIM macros; PIM/c: automatic to microprogram; PIM/k: by hand; PIM/i: not described.

### 6. Comparison table

| Machine | Maker | Processor style | Word / tag format | KL1 implementation | Runtime layouts documented | Main sources |
|---|---|---|---|---|---|---|
| PIM/p | Fujitsu | RISC-like + tag-conditional macro-call into 8K-step internal instruction memory; 4-stage D/A/T/B (+S/C); 80 ns as built (50-60 ns design); 32 registers; 4- or 6-byte instructions | 40-bit (8-bit tag incl. 1 MRB bit + 32-bit data) in aligned 64-bit memory words; 44-46 types in 7 bits; MRB bit position not published | KL1 -> KL1-B (memory-based) -> templates (1-6 native instructions) + macro library (IIM) + subroutines; runtime = VPIM compiled from PSL | Goal queues (priority table, current queue, overflow queue); string/module format; code-module format; message set, export forms, shoen/foster-parent in prose; no field offsets | TR-577, FGCS'92 pp. 414-424, TR-453, TM-1067, TM-1257, TM-1320, FGCS'94 pp. 80-89 |
| PIM/c | Hitachi | Horizontal microprogram, 104-bit microword, 50 ns design / 66 ns; 2x8 registers + 2x256 register files; 32 kW control store | 40-bit (8-bit tag + 32-bit data; TM-870); bit assignment not published | KL1-B superset "KL1B/c" interpreted by microprogram generated automatically from VPIM; overflow code interpreted from main memory | Behavioural only (per-PE load pool, requester bitmap, slit-check flags) | TR-672, TR-671, TM-870, FGCS'92 pp. 723-730, TR-863, TM-1260 |
| PIM/i | Oki | RISC + LIW, 40-bit fixed instructions in 3/2/1-field forms, 3-stage F/E/W, no condition codes; 100 ns design / 240 ns | 40-bit: lock, GC, MRB bits + 5-bit type + 32-bit value (TM-1017) | KL1b -> post-compiler -> native code + about 4 KW run-time library; no control store; VPIM port ran May 1992 | None | TR-675, TM-1017, TM-1264, TM-1260 |
| PIM/k | Toshiba | Toshiba IP1704 chip: RISC "32 bit" with "4bits tag", Harvard buses, 100 ns; nothing else published | "32 bit" + "4bits tag" only | Native code; VPIM-based runtime hand-coded; REF/EXREF merged, no permanent export/import tables | One slide (goal-request bitmap, per-PE goal post) | TR-767, TR-768, TR-769, TM-766, TM-1260 |
| (PIM/m, for reference) | Mitsubishi | Horizontal microprogram, 5-stage, 65 ns, 32 K-word WCS | 40-bit (8-bit tag + 32-bit data) | Register-based KL1-B interpreted by microprogram inherited from Multi-PSI/V2 | (main project) | FGCS'92 pp. 425-435 |

Single-PE append ([P10] Table 1, IMG; KRPS nrev1500 / nrev5000 at the clock used): PIM/m 600 / 411 (65 ns); PIM/p 305 / 281 (80 ns); PIM/k 76 / 76 (100 ns); PIM/i 65 / 65 (240 ns); PIM/c 55 / 56 (66 ns). The TM-1260 slide of March 1993 has the same PIM numbers plus Multi-PSI 125 / 114 (200 ns); its unit is not printed. Taki's Tables 1-4 (configuration, PE, network, cache) are transcribed in table T.1 below; the museum page `A/MACHINE/pim-spec-E.html` carries the same four tables without the Multi-PSI row.

### 7. Filing notes and source conflicts

- **UNIRED II is not a PIM**: "UNIREDII is the high performance inference processor of the parallel inference machine PIE64. It is designed for the committed choice language Fleng" (Shimada, Koike, Tanaka, FGCS'92 vol. 2 p. 715, TXT) -- University of Tokyo, not KL1.
- TR-733 and TM-853, despite general titles, are PIM/m-only (Mitsubishi) and say nothing on the four machines.
- The VPIM manual is cited as "TR-1044" in TM-1257 and "TM-1044" in TM-1320; the TM index lists TM-1044 「VPIM処理方式解説書」, 298 pp.
- PIM/p cycle: 50 ns (1989-90 target), 60 ns (Taki 1992 design spec), 80 ns (measured machines 1993-95).
- PIM/i cycle in [P10]: 160 ns in the text, 240 ns in Table 1 and in TM-1260. PIM/c: 60 ns text, 66 ns table.
- PIM/p indirect registers: 16 (TR-389, 1988) vs three (TM-1067, FGCS'92). Macro-call penalty: "one additional cycle" (TR-577) vs 2 cycles (TR-453).
- PIM/i size: 16 PEs in two clusters (Taki) vs 8 PEs maximum for lack of a network ([P10]).
- TM-1320 Table 5 prints the bestpath messages-per-reduction total as 0.0081, the same as pentomino; the rows above sum to 0.0326 (apparent misprint in the source).

### 8. Not found

| Item | Where looked / exact queries |
|---|---|
| Tag code tables for any of the four; MRB bit position for PIM/p, PIM/c, PIM/k | All documents in section 9 marked read; PIM/p: TR-577, TR-770, TR-453, TM-1067, TR-389 (only "one bit of the 8 bit tag"); PIM/i's bit split is in TM-1017 |
| Field-level goal / suspension / shoen / foster-parent / export-import layouts per machine | Not in any document read; all defer to TM-1044 |
| PIM/c tag bit assignment, microinstruction field layout, cache state names and commands | TR-671, TR-672, TR-863, TR-871, FGCS'92 pp. 723-730, TM-1260 |
| PIM/k instruction set, pipeline, registers | TR-767, TR-768, TR-769, TM-1260 |
| PIM/i network, PSL translation method, register count | TR-675, TM-1264, TM-1260 |
| Sato et al., IPSJ Trans. 33(3) 1992 (journal text; the IPSJ convention papers of the same group do resolve as unlisted ICOT TMs, see section 10) | `"PIM/i" parallel inference machine Oki processor design Sato IPSJ 1992`; `並列推論マシンPIM/iプロセッサの設計 情報処理学会論文誌 佐藤正俊`; `site:ipsj.ixsq.nii.ac.jp 並列推論マシン PIM/i`; `"PIM/i" Oki "LIW" KL1 processor "long instruction word" parallel inference` |
| Oki / Toshiba / Hitachi / Fujitsu house-journal articles | `沖電気研究開発 OR "Oki Technical Review" 並列推論マシン PIM/i`; `東芝レビュー OR "Toshiba Review" 並列推論マシン PIM/k 階層キャッシュ`; `"Hitachi Review" OR "日立評論" 並列推論マシン PIM/c`; `"PIM/p" Fujitsu "Fujitsu Scientific and Technical Journal" parallel inference machine Kumon Asato` |
| PIM/k and PIM/c journal or conference papers beyond ICOT TRs | `"PIM/k" parallel inference machine Toshiba hierarchical cache Sakai Asano`; `並列推論マシン PIM/k 東芝 階層キャッシュ 情報処理学会 酒井 浅野 KL1処理系`; `"PIM/c" parallel inference machine Hitachi Nakagawa Tarui snooping cache lock mechanism`; `並列推論マシン PIM/c 情報処理学会 日立 中川貴之 垂井俊明 スヌープキャッシュ ロック`; `Tarui Nakagawa Ido Asaie Sugie "lock mechanism" snooping cache parallel inference machine journal` (found ICS'92 pp. 53-62 record only) |
| Full text of FGCS'88 macro-call paper, ISCA'89 cache paper, JIP 13(2) | `Shinogi Kumon Hattori Goto "Macro-call instruction for the efficient KL1 implementation on PIM" FGCS 1988` (record only; text = TR-389); `Goto Matsumoto Tick "Design and performance of a coherent cache for parallel logic programming architectures" ISCA 1989` (DOI 10.1109/ISCA.1989.714521, paywalled; text = TR-436, not read); `"Processor element architecture for a parallel inference machine, PIM/p" Journal of Information Processing 13 1990 Goto Shinogi` (not found) |
| Emulators, firmware dumps, machine manuals | `PIM/p OR "PIM/c" OR "PIM/k" OR "PIM/i" KL1 emulator OR simulator surviving firmware VPIM PSL source` (nothing); `IPSJ Computer Museum parallel inference machine PIM/p PIM/c PIM/i PIM/k PIM/m` (only the PIM/p and PIM/m preservation note); no TR/TM title names a firmware listing or hardware manual for PIM/c, /i, /k |
| Museum per-machine technical pages | curl of `A/MACHINE/pim-{p,c,i,k}-E.html` (photo galleries only); `MACHINE/`, `index.html`, `machine-E.html`, `pim-E.html`, `pim-top-E.html` (404/500) |
| Other | `"UNIRED II" high performance inference processor parallel inference machine FGCS 1992` (PIE64, not a PIM); `dblp FGCS 1992 "PIM/k" OR "PIM/c" OR "PIM/i" proceedings Fifth Generation Computer Systems 1992 architecture papers` (no PIM/i or PIM/k paper in the proceedings) |

### 9. Source table

Status: R = opened and read (with the verification level noted); S = resolved, not read; C = cited only.

| Citation | URL / location | Status |
|---|---|---|
| Goto, Shinogi, Chikayama, Kumon, Hattori, TR-577, 1990 | A/TRTM/TR/TRpdf/tr0577.pdf | R (OCR in full; Tables 1-4 IMG) |
| Kumon et al., "Architecture and Implementation of PIM/p", FGCS'92 v.1 pp. 414-424 = TR-770 | A/FGCS/FGCS92en-proc1/92ePIM-1.pdf; tr0770.pdf | R (TXT; pp. 420, 423 IMG) |
| Hattori et al., TR-514, 1989 | tr0514.pdf | R (OCR; Tables 2-3 IMG) |
| Hattori et al., TR-453, 1989 | tr0453.pdf | R (IMG, 130 dpi) |
| Yamamoto et al., TR-493, 1989 | tr0493.pdf | R (IMG) |
| Miyazaki, Hatazawa, Hirano, TM-1067, 1991 | A/TRTM/TM/TMpdf/tm1067.pdf | R (IMG) |
| Yamamoto, Kawai, TM-1065, 1991 | tm1065.pdf | R (IMG) |
| Hatazawa, Arai, TM-1257, 1993 | tm1257.pdf | R (IMG) |
| Takei et al., TM-1320, 1995 | tm1320.pdf | R (IMG; PDF pp. 14-15, 25-27 graphs not read) |
| Shinogi et al., TR-389, 1988 (= FGCS'88) | tr0389.pdf | R (OCR; opcode tables pp. 17-18 not transcribed) |
| Imai, TM-1237, 1992 | tm1237.pdf | R (OCR, Japanese, not image-verified) |
| Hirano, Goto, TM-888, 1990 | tm0888.pdf | R p. 1 (IMG); body not read |
| Kumon, Hatazawa, FGCS'94 pp. 80-89 | A/FGCS94/PS/eval-of-PIM.ps.gz | R (TXT; Tables 1, 3, 4 IMG) |
| Nakagawa et al., TR-672, 1991; Nakagawa, Sugie, TR-671, 1991 | tr0672.pdf, tr0671.pdf | R (IMG) |
| Nakagawa et al., FGCS'92 v.2 pp. 723-730 | FGCS'92 proceedings vol. 2 | R (TXT) |
| Tarui et al., TR-863, 1994; TR-871, 1994 | tr0863.pdf, tr0871.pdf | R (OCR; TR-863 Tables 3.1/3.2 IMG) |
| Sato, Takeda, Ohara, TR-675, 1991 | tr0675.pdf | R (IMG) |
| Ohara, Takeda, TM-1264, 1993 | tm1264.pdf | R (pr. 1 IMG; tables 3, 5 OCR) |
| Asano, Isobe, Sakai, TR-767, 1992 | tr0767.pdf | R (OCR; PDF 3, 4, 10 IMG; appendix tables not transcribed) |
| Sakai et al., TR-768, 1992 | tr0768.pdf | R (OCR; PDF 4, 5, 12 IMG) |
| Sakai et al., TR-769, 1992 | tr0769.pdf | R (OCR) |
| Muratani, TM-1066, 1991 | tm1066.pdf | R abstract only |
| Hirata (ed.), TM-1260, 1993 | tm1260.pdf | R selected sessions (IMG): PIM/i, PIM/c, PIM/k, PIM/p, VPIM, benchmark; rest not read |
| Taki, "Parallel Inference Machine PIM", FGCS'92 v.1 pp. 50-72 (= TR-775) | FGCS'92 vol. 1 | R selected sections (Tables 1-4 IMG) |
| Hirata et al., "Parallel and Distributed Implementation of ... KL1", FGCS'92 v.1 pp. 436-459 | A/FGCS/FGCS92en-proc1/92ePIM-3.pdf | R selectively (TXT) |
| Imai, Hirata, Taki, TR-659, 1991 | tr0659.pdf | R (OCR) |
| Kawai et al., TR-556, 1990; Ichiyoshi, TM-675, 1989 | tr0556.pdf, tm0675.pdf | R (OCR; some pages IMG) |
| Nakashima et al., "Architecture and Implementation of PIM/m", FGCS'92 v.1 pp. 425-435 | FGCS'92 vol. 1 | R (grep only, for the baseline facts) |
| TR-733, TM-853, TM-140 | local | R (OCR); nothing on the four machines |
| ICOT Museum "Outline of 5 modules of PIM"; per-machine photo pages; FGCS'92 demo leaflets doc011-018 | A/MACHINE/pim-spec-E.html; A/MACHINE/pim-{p,c,i,k}-E.html; A/FGCS92Demo/E/ | R (HTML) |
| ICOT TR and TM indexes | A/TRTM/TR/TRlist.html; A/TRTM/TM/TMlist.html | R (filtered for the four machines) |
| ICOT Free Software list, abstracts #1, 2, 3, 4, 72, 74 | A/IFS/list-of-IFS-E.html, A/IFS/abst/ | R (HTML); archives S (HEAD only) |
| IPSJ Computer Museum FGCS page | museum.ipsj.or.jp/en/computer/other/0002.html | R (HTML) |
| TR-436 (Goto, Matsumoto, Tick), TR-656, TR-732 (Tarui et al.), TR-574, TR-575, TR-666, TR-869, TR-247, TR-327; TM-875, TM-930, TM-951, TM-835, TM-717, TM-967, TM-1289, TM-1044 | A/TRTM/... | S |
| Goto, Matsumoto, Tick, ISCA'89 pp. 25-33; Tarui et al., ICS'92 pp. 53-62 | DOI 10.1109/ISCA.1989.714521; dblp conf/ics/TaruiNIAS92 | S (records only) |
| Goto, Taki, Nakagawa, Sugie, 「並列推論マシンPIM/c ―概要―」, TM-870 (IPSJ 40th convention, 1990) | A/TRTM/TM/TMpdf/tm0870.pdf (not on the TM list page) | R (IMG, both pages) |
| Kato, Sato, Takeda, Ohara, 「並列推論マシンPIM/iのタグアーキテクチャの評価」, TM-1017 (IPSJ 42nd convention, 1991) | .../tm1017.pdf (not on the list page) | R (IMG, both pages) |
| Asano, 「並列推論マシンPIM/k ～ハードウェア アーキテクチャ～」, TM-766 (IPSJ 38th convention, 1989) | .../tm0766.pdf (not on the list page) | R (IMG, both pages) |
| TM-847, TM-1098, TM-1012 | .../tm0847.pdf, tm1098.pdf, tm1012.pdf | S (downloaded, not read) |
| Other unlisted convention TMs on the four machines (list in 10b) | A/TRTM/TM/TMpdf/ | S (titles from a crawl index; not fetched) |
| VPIM distribution, unpacked copy from a parallel task | scratchpad `vpim/vpim/` (= IFS #2 `vpim.tar.Z`) | grep for machine names only |
| Goto et al., J. Inf. Process. 13(2):174-182, 1990; Hattori et al., IPSJ Trans. 30(12):1584-1592, 1989; Sato et al., IPSJ Trans. 33(3):278-287, 1992; Tanaka et al. (PIM/c CPU), IPSJ 40th convention 2L-2; 皆川 et al. (IP1704), IPSJ 38th convention; Nakagawa, Goto, Chikayama, 89-ARC-77-3; Hatazawa, IPSJ Trans. 35(10):2069-2077, 1994; "[Sakai et al. 1991]" (Taki's PIM/k citation, unidentified) | - | C |

### 10. Documents worth obtaining or finishing

**10a. Could not be opened (not online, or paywalled).**
1. Tanaka et al., 「並列推論マシンPIM/c ―CPUについて―」, and the companion cache, load-balancing and maintenance papers (Tarui et al., Ido et al., Maeda et al.), IPSJ 40th convention, 1990 -- cited by TM-870 as refs [3]-[6]; the likeliest source of the PIM/c tag assignment and microinstruction fields. Not in the crawl index of unlisted TMs.
2. 皆川 et al., 「AIチップ(IP1704)のアーキテクチャ」, IPSJ 38th convention, pp. 1538-1539, 1989, and any other Toshiba IP1704 literature -- the PIM/k processor's instruction set, registers and tag format.
3. Sato, Takeda, Ohara, Trans. IPSJ 33(3):278-287, 1992 (PIM/i); Goto et al., J. Information Processing 13(2):174-182, 1990 and Hattori et al., IPSJ Trans. 30(12):1584-1592, 1989 (PIM/p); Hatazawa, IPSJ Trans. 35(10):2069-2077, 1994.
4. Goto, Matsumoto, Tick, ISCA'89 (paywalled; the ICOT text TR-436 resolves); Tarui et al., ICS'92 (ICOT text TR-732 resolves).
5. Fujitsu SSL "PIM/p CSP manual" and start-up procedure (1992); ICOT FY1992 hardware results report (平成4年度電算基礎技術開発成果報告書 ハードウェア技術編); the "[Sakai et al. 1991]" PIM/k paper cited by Taki (unidentified).
6. Any firmware image, back-end tool or machine manual for the four machines (none located).

**10b. Resolve on the AIST host, not read** (PDF path `A/TRTM/TM/TMpdf/tmNNNN.pdf` or `.../TR/TRpdf/trNNNN.pdf`).
1. Unlisted IPSJ-convention TMs (2 pp each unless noted). PIM/p: TM-530, TM-531, TM-779, TM-1090, TM-1091, TM-1127. PIM/c: TM-1000. PIM/i: TM-846, TM-847, TM-921, TM-922, TM-923, TM-929, TM-1014, TM-1015, TM-1016, TM-1018, TM-1019, TM-1046, TM-1093, TM-1095, TM-1096, TM-1097, TM-1098, TM-1247, TM-1248. PIM/k: TM-1010, TM-1011, TM-1012. These are the best remaining chance of per-machine detail (PIM/i KL1 expansion and goal communication, PIM/p KL1 implementation and pipeline control, PIM/c microprogram generation, PIM/k KL1 system evaluation).
2. TR-436 (PIM/p cache protocol and lock directory); TR-732, TR-656 (PIM/c cache states and lock); TM-875 (improved KL1-B) ; TR-574, TR-575, TR-666 (PSL environment, intra-cluster execution, export/import evaluation); TM-930 (PIM/k cache simulation); TM-951; TM-835 and TM-717 (1989 workshop, early designs); TR-869 / TM-1289 (PIM/c load balancing with LSI routing).

**10c. Local or downloaded, only partly read.**
1. TR-389 PDF pp. 17-18: the full 1988 PIM/p opcode tables (rendered in `p/t389-17.png`, `t389-18.png`; not transcribed).
2. TM-888 body (memory-based KL1-B instruction changes and measurements); TM-1066 body and TR-767 appendix tables A.1-A.5 (PIM/k protocol state tables).
3. TM-1260 unread sessions: PIM/p slides (pr. 159-164), Imai and Chikayama on VPIM (pr. 132-142), PIM/k slides pr. 153-156, the two panels.
4. TM-847 (6 pp), TM-1098, TM-1012: downloaded to `dl2/`, rendered to `p2/`, not read.
5. TM-1044 and the VPIM source (other agent): the only place field-level layouts are given; its per-machine comments (constants for PIM/p vs PIM/i/k) deserve a targeted pass.

### Tables transcribed from the sources

#### A.1 Taki, FGCS'92 vol. 1 pp. 61-63, Tables 1-4 (IMG)

Table 1 "Global Configuration" (printed p.61, IMG):

| | Topology | Number of Clusters | Total Number of PEs | Memory Size/Cluster |
|---|---|---|---|---|
| PIM/p | hypercube x 2 | 64 | 512 | 256 MB |
| PIM/m | mesh | 256 | 256 | 80 MB |
| PIM/c | crossbar | 32 | 256 | 160 MB |
| PIM/k | -- | 1 (dagger: "four mini-clusters included") | 16 | 1 GB |
| PIM/i | -- | 2 | 16 | 320 MB |
| Multi-PSI/V2 | mesh | 64 | 64 | 80 MB |

Table 2 "Specification of Processing Element" (p.62, IMG):

| | Instruction set | Cycle time | LSI fabrication | Line interval |
|---|---|---|---|---|
| PIM/p | RISC + macro instruction | 60 nsec (dagger) | standard-cell | 0.96 um |
| PIM/m | CISC (micro programmable) | 65 nsec | standard-cell | 0.8 um |
| PIM/c | CISC (micro programmable) | 50 nsec (dagger) | gate-arrays | 0.8 um |
| PIM/k | RISC | 100 nsec | custom | 1.2 um |
| PIM/i | RISC | 100 nsec (dagger) | standard-cell | 1.2 um |
| Multi-PSI/V2 | CISC (micro programmable) | 200 nsec | gate-arrays | 2.0 um |

"(dagger are design specifications. They are under testing with longer cycle time.)" (IMG)

Table 3 "Network" (p.62, IMG):

| | # PEs in a cluster | # NIs in a cluster | Transfer Rate (per channel, full duplex) |
|---|---|---|---|
| PIM/p | 8 | 8 | 33 MB/sec (design spec.) x2 |
| PIM/m | 1 | 1 | 8 MB/sec |
| PIM/c | 8 | 1 | 40 MB/sec (design spec.) |
| PIM/k | 16 | -- | -- |
| PIM/i | 8 | 1 | -- |
| Multi-PSI/V2 | 1 | 1 | 10 MB/sec |

Table 4 "Specification of Cache System" (p.63, IMG):

| | Protocol | # States ("does not include locking state") | Mapping | Instruction cache | Data cache |
|---|---|---|---|---|---|
| PIM/p | invalidation | 4 | 4 way | 64 KB (one cell spanning both) | |
| PIM/m | -- | -- | direct-map | 5 KB | 20 KB |
| PIM/c | invalidation | 5 | 2 way | 80 KB (one cell) | |
| PIM/k | hierarchical invalidation | 4 | (1st) direct-map; (2nd) 4 way | 128 KB; 1 MB | 256 KB; 4 MB |
| PIM/i | broadcasting | 6 | direct-map | 160 KB | 160 KB |
| Multi-PSI/V2 | -- | -- | direct-map | 20 KB (one cell) | |

#### A.2 Kumon and Hatazawa, FGCS'94, Table 1 "Append RPS on various systems" (IMG)

| System | clock (ns) | nrev1500 (RPS x10^3) | nrev5000 (RPS x10^3) | Ratio |
|---|---|---|---|---|
| PIM/m | 65 | 600 | 411 | .69 |
| PIM/p | 80 | 305 | 281 | .92 |
| PIM/c | 66 | 55 | 56 | 1.02 |
| PIM/i | 240 | 65 | 65 | 1.00 |
| PIM/k | 100 | 76 | 76 | 1.00 |
| KLIC (SS10, CPU time) | 28 | 1,151 | 1,173 | 1.01 |
| KLIC/p | 80 | 225 | 238 | 1.06 |
| KLIC/p (10M-word heap) | 80 | 405 | 386 | 0.95 |

#### A.3 PIM/p simulator instruction statistics, TM-1067 Tables 1-2 (IMG; Table 1 = instruction counts at run time, Table 2 = distribution of instructions)

Table 1 「実行時における命令の状況」:

| program | expanded insns executed | macro-call insns (%) | macro-calls actually taken (%) | macro-body insns per macro-call | note |
|---|---|---|---|---|---|
| queen | 1219006 | 8.3 | 81.5 | 11.6 | 8 queens |
| prime | 90734 | 11.1 | 67.2 | 9.5 | primes |
| prime_dd | 42607 | 16.2 | 78.6 | 13.7 | primes |
| bup3 | 1235405 | 11.3 | 70.9 | 12.3 | parsing |
| mastermind | 223403 | 8.0 | 72.5 | 10.5 | game |
| cube | 557358 | 4.9 | 84.0 | 11.3 | constraint satisfaction |

Table 2 「命令の分布」 (share of all executed instructions):

| program | expanded (%) | in macro bodies (%) | in subroutines (%) |
|---|---|---|---|
| queen | 32 | 31 | 37 |
| prime | 27 | 29 | 44 |
| prime_dd | 9 | 21 | 70 |
| bup3 | 31 | 43 | 26 |
| mastermind | 34 | 28 | 38 |
| cube | 55 | 31 | 14 |

#### A.4 PIM/p intra-cluster load balancing, TM-1257 Table 1 (IMG; 8* = resumed goal run on the resuming PE)

| program | PEs | reductions (x1000) | speed-up | suspend rate | get-G rate | throw-G rate |
|---|---|---|---|---|---|---|
| tsumego | 1 | 250 | 1.00 | 0.186 | | |
| | 8 | 906 | 1.44 | 0.200 | 0.003 | 0.033 |
| | 8* | 860 | 2.38 | 0.187 | 0.003 | 0.000 |
| life (4-neighbour variant) | 1 | 360 | 1.00 | 0.572 | | |
| | 8 | 360 | 3.77 | 0.625 | 0.016 | 0.529 |
| | 8* | 360 | 5.44 | 0.588 | 0.064 | 0.000 |
| zebra | 1 | 404 | 1.00 | 0.000 | | |
| | 8 | 404 | 5.01 | 0.003 | 0.091 | 0.003 |
| | 8* | 404 | 4.48 | 0.008 | 0.123 | 0.000 |
| mastermind | 1 | 1737 | 1.00 | 0.000 | | |
| | 8 | 1737 | 7.66 | 0.001 | 0.001 | 0.000 |
| | 8* | 1737 | 7.68 | 0.001 | 0.001 | 0.000 |

#### A.5 PIM/p shoen / foster-parent and inter-cluster costs, TM-1320 Tables 17 and 19 (IMG)

Table 17 (per loop):

| item | program | loops | time [ms] | per-loop [μs] | clocks per loop |
|---|---|---|---|---|---|
| (a) | flat creation of shoen/foster-parent | 65536 | 55314 | 844 | 10550 |
| (b) | flat execution of a goal | 65536 | 815 | 12.4 | 155 |
| (c) | hierarchical creation of shoen/foster-parent | 1024 | 225371 | 2.20x10^5 | 2750000 |
| (d) | foster-parent switch, different foster-parents | 1048576 | 61652 | 58.8 | 735 |
| (e) | same foster-parent | 1048576 | 28438 | 27.1 | 339 |
| (f) | goal execution within a cluster | 1048576 | 13009 | 12.4 | 155 |
| (g) | goal execution across clusters | 262144 | 144776 | 552 | 6900 |
| (h) | across clusters, 1 PA function | 255 | 149 | 586 | 7325 |
| (i) | across clusters, 2 PA functions | 255 | 152 | 596 | 7450 |

Table 19 「荘園/里親に関する基本機能処理時間」:

| basic function | clocks | time [μs] |
|---|---|---|
| shoen/foster-parent creation + deletion | 10395 | 832 |
| one shoen/foster-parent message | 710 | 56.8 |
| foster-parent switch | 198 | 15.9 |
| inter-cluster load distribution (one goal) | 7045 | 564 |

#### A.6 PIM/c microprogram for append, TR-672 Table 2 (IMG; unit micro-steps)

| # | 高速化項目 (speed-up item) | 効果 (effect, μStep) |
|---|---|---|
| 0 | 第1版のステップ数 (steps in version 1) | 416 |
| 1 | ディスパッチの高速化 (dispatch) | -144 |
| 2 | 分岐処理の高速化 (branching) | -64 |
| 3 | KL1B命令の粒度の向上 (coarser KL1B instructions) | -36 |
| 4 | VPIMの人手最適化 (hand optimisation of VPIM) | -32 |
| 5 | レジスタファイルアクセスの削減 (fewer register-file accesses) | -29 |
| 6 | マイクロテンプレートの最適化 (micro-template optimisation) | -11 |

#### A.7 PIM/i simulation, TR-675 Tables 2-3 (IMG). Columns of Table 2: KL1b instructions executed / machine instructions per KL1b / library calls per KL1b. Table 3 rows: conditional branch, unconditional branch, tag branch, all branch operations (% of instructions).

Table 2 1 KL1b当たりの実行命令語数:

| | 実行KL1b数 | KL1b当たりの実行命令数 | KL1b当たりの呼び出し回数 |
|---|---|---|---|
| qk8 | 12.7M | 2.2 | 0.13 |
| qu8 | 26.0M | 3.0 | 0.13 |
| bup | 0.9M | 2.3 | 0.11 |
| han | 2.5M | 2.6 | 0.10 |
| pri | 2.7M | 2.4 | 0.06 |
| 平均 | 9.0M | 2.5 | 0.11 |

(Internal oddity in the source: 12.7M KL1b x 2.2 instructions against 3.2 Mcycles for qk8 in Table 1; transcribed as printed, not resolved.)

Table 3 分岐処理の出現率 (%): 条件分岐 14.0 13.3 14.6 19.5 44.7 (av. 21.2); 無条件分岐 5.9 4.9 6.2 8.1 3.7 (5.8); タグ分岐 15.9 9.7 15.4 4.2 9.8 (11.0); 分岐操作 35.9 28.0 36.2 31.8 58.1 (38.0).


## Could not find

Each line is "not found", not "does not exist". Queries and files
searched are listed in the appendix named.

- PIM/m (or Multi-PSI/V2) goal record field order and size; shoen and
  foster-parent record layouts; suspension record word order (App. A
  "What none of the 18 reports contains").
- Numeric tag values in any paper (the only stated pair is the
  console's REFo 06 / REFx 07); which tag bits the batch collector uses
  on PIM/m (App. A, App. C sec. 4).
- Message order codes and message body byte formats for the PIM/m or
  Multi-PSI network (App. A gap 6).
- What PIM/m does when two hooked variables are unified; the order in
  which several woken goals run (App. A gap 2).
- PIM/m free-pool cell sizes for goal records; the batch GC trigger
  (App. C 1.5).
- The KL1-B instruction word layout for PIM/m in print; the meaning of
  the 54-bit decode-table entry (nano-code); the size of the KL1
  microprogram; a microassembler or microcode listing (App. C 2.10).
- Any description of the `.kbn` format, of heap `save`/`restore`, or of
  the FEP SCSI protocol on the wire (App. C sec. 3; TM-1044 is silent
  too, App. B "Silent across the whole document").
- An emulator, ROM dump or disk image of PSI-II, PSI-III/PSI-UX or any
  PIM; firmware, back-end tools or manuals specific to PIM/p, /c, /i,
  /k (App. D; "The other PIMs" sec. 8).
- Open full text of the ICLP'87, ICLP'89, ICCD'90 and CICC'91 papers
  (their ICOT TR/TM versions are open and were read instead: TR-248,
  TR-439, TM-862, TM-858).

## Principal sources

"Read" = text or page images read for this file (directly or by a
reading pass; the appendix says which quotes were image-checked).
"Held" = already in `pim/docs/` before this search. The complete lists,
including items only cited and URLs that failed, are the source tables
inside each appendix and in "The other PIMs" sec. 9.
`ICOT:` = `https://www.airc.aist.go.jp/aitec-icot/ICOT/Museum/TRTM/`.

| Source | Where | Status | Gaps |
|---|---|---|---|
| Nakashima et al., "Architecture and Implementation of PIM/m", FGCS'92 vol. 1 pp. 425-435 (= TR-742) | held `FGCS92_Volume_1.pdf`; bitsavers `pdf/icot/` | read | 1, 2, 3, 6, 7, 8 |
| Taki, "Parallel Inference Machine PIM", FGCS'92 vol. 1 pp. 50-72 | held | read | all; sibling ranking |
| Hirata et al., "Parallel and Distributed Implementation of Concurrent Logic Programming Language KL1", FGCS'92 vol. 1 pp. 436-459 | held | read | 1-7 (VPIM) |
| Kumon et al., "Architecture and Implementation of PIM/p", FGCS'92 vol. 1 pp. 414-424 (= TR-770) | held | read | other PIMs |
| Nakagawa et al., "Hardware Implementation of Dynamic Load Balancing in the Parallel Inference Machine PIM/c", FGCS'92 vol. 2 pp. 723-730 | held `FGCS92_Volume_2.pdf` | read | other PIMs |
| "VPIM 処理方式解説書" (Inside VPIM), ICOT TM-1044, 1991-04-05, ICOT First Research Laboratory ed. | held, LaTeX in `nonlocal/vpim.tar.Z` `vpim/DOCUMENT/TM-1044.j/` | read (App. B) | 1-7 (VPIM) |
| `psdpim.tar.Z` (ICOT Free Software no. 3, Pseudo PIM/m): `SYSTEM.DIR/PIMM.PARAM`, `boot.init`, `INSTALL.DIR/*.ptf` strings, `PMPSI.DIR/*` | held `nonlocal/psdpim.tar.Z`; abstract `.../Museum/IFS/abst/003.html` | parameter file and boot script read; packages only as strings; images only measured | 1, 3, 5, 6, 7, 8 |
| Kimura & Chikayama, "An Abstract KL1 Machine and Its Instruction Set", TR-246 (SLP'87) | held `nonlocal/tr0246.pdf` | read earlier (`kl1_architecture.md`) | 1, 2 |
| Chikayama & Kimura, "Multiple Reference Management in Flat GHC", TR-248, Mar 1987 (ICLP'87 pp. 276-293) | `ICOT:TR/TRpdf/tr0248.pdf` | read (App. A) | 3 |
| Nakajima, "Distributed Implementation of KL1 on the Multi-PSI", TR-715, Nov 1991 (chapter in Kacsuk & Wise eds., *Implementations of Distributed Prolog*, Wiley 1992) | `ICOT:TR/TRpdf/tr0715.pdf` | read | 1-8 (Multi-PSI/V2) |
| Nakajima, Inamura, Ichiyoshi, Rokusawa, Chikayama, "Distributed Implementation of KL1 on the Multi-PSI/V2", TR-439, Dec 1988 (ICLP'89 pp. 436-451) | `ICOT:TR/TRpdf/tr0439.pdf` | read | 1, 2, 5, 6 |
| Onishi, Matsumoto, Nakajima, Taki, "Evaluation of the KL1 Language System on the Multi-PSI", TR-585 | `ICOT:TR/TRpdf/tr0585.pdf` | read | 1, 2 |
| Inamura, Ichiyoshi, Rokusawa, Nakajima, "Optimization Techniques Using the MRB and Their Evaluation on the Multi-PSI/V2", TR-466 (NACLP'89 pp. 907-921) | `ICOT:TR/TRpdf/tr0466.pdf` | read | 2 (merger), 3, 6 |
| Ichiyoshi, Rokusawa, Nakajima, Inamura, "A New External Reference Management and Distributed Unification for KL1", TR-390 (FGCS'88 pp. 904-913) | `ICOT:TR/TRpdf/tr0390.pdf` | read | 5, 6 |
| Rokusawa, Ichiyoshi, Chikayama, Nakashima, "An Efficient Termination Detection and Abortion Algorithm for Distributed Processing Systems", TR-341 (ICPP'88); Rokusawa & Ichiyoshi, TR-737 | `ICOT:TR/TRpdf/tr0341.pdf`, `tr0737.pdf` | read | 5 |
| Nakajima & Ichiyoshi, "Evaluation of Inter-processor Communication in the KL1 Implementation on the Multi-PSI", TR-531 (ICPP'90); Japanese twin TR-563 | `ICOT:TR/TRpdf/tr0531.pdf`, `tr0563.pdf` | read | 6 |
| Miyauchi, Kawada, Nakajima, "Tracing Garbage Collection for KL1 on the Multi-PSI/V2 System", TR-469 | `ICOT:TR/TRpdf/tr0469.pdf` | read | 7 |
| Inamura & Onishi, "A Detection Algorithm of Perpetual Suspension in KL1", TR-530 (ICLP'90) | `ICOT:TR/TRpdf/tr0530.pdf` | read | 2, 7 |
| Miyazaki et al., "並列論理型言語KL1の実現方式と並列OSの記述" (Implementation of the parallel logic language KL1 and the description of a parallel OS), TR-373, 1988 | `ICOT:TR/TRpdf/tr0373.pdf` | read from page images | 1, 2, 5 |
| Kimura et al., "並列論理型言語KL1の多重参照管理によるガーベジ・コレクション" (GC by multiple reference management for KL1), TR-498; Miyauchi et al., TR-321 | `ICOT:TR/TRpdf/tr0498.pdf`, `tr0321.pdf` | read from page images | 3 |
| Chikayama, Satoh, Miyazaki, "Overview of the Parallel Inference Machine Operating System (PIMOS)", TR-483; Yashiro et al., "Resource Management Mechanism of PIMOS", TR-764 | `ICOT:TR/TRpdf/tr0483.pdf`, `tr0764.pdf` | read | 1 (priority), 5, 8 (SCSI) |
| Sato et al., "KL1 Execution Model for PIM Cluster with Shared Memory", TR-250 (ICLP'87) | `ICOT:TR/TRpdf/tr0250.pdf` | read | 2 (early PIM, not Multi-PSI) |
| Nakajima, Masuda, Nakashima, Kondo, Takeda, Murasawa, Komori, "並列推論マシンPIMのアーキテクチャ" (Architecture of the parallel inference machine PIM), Mitsubishi Denki Giho 66(6) 1992 pp. 74-78 = TR-733 | `ICOT:TR/TRpdf/tr0733.pdf`; `https://www.giho.mitsubishielectric.co.jp/giho/pdf/1992/9206.pdf` | read from page images | 3, 7, 8 |
| Nakashima, Takeda, Nakajima, Andou, Furutani, "A Pipelined Microprocessor for Logic Programming Languages", TM-862 (ICCD'90 pp. 355-359) | `ICOT:TM/TMpdf/tm0862.pdf` | read (OCR) | 8 |
| Andou et al., "A 40-bit Microprocessor for Logic Programming Language", TM-858; Japanese twin TM-857 | `ICOT:TM/TMpdf/tm0858.pdf`, `tm0857.pdf` | read, tables from images | 8 |
| Machida et al., "A VLSI Chip Set for a Large Scale Parallel Inference Machine: PIM/m", TR-799 and TM-1159; Furutani et al., TM-1074; Nakashima et al., TR-564 | held `nonlocal/tr/`, `nonlocal/tm/` | read | 8 |
| Nakashima & Nakajima, "Hardware Architecture of the Sequential Inference Machine: PSI-II", TR-265 (SLP'87) | `ICOT:TR/TRpdf/tr0265.pdf` | read | 8 (predecessor) |
| TR-870, TM-1295, TR-907 (Nakashima, copying GC algorithms), TR-354 (Nakajima, Piling GC) | `ICOT:` | read; generic, not about the PIM/m heap. The PDFs served as TR-870 and TM-1295 carry each other's index titles | 7 (negative) |
| PIM/p: TR-577, TR-514, TR-453, TR-493, TM-1067, TM-1257, TM-1320, TM-1065; Shinogi et al. TR-389 (held); Kumon & Hatazawa FGCS'94 | `ICOT:`; FGCS'94 under `.../Museum/FGCS/` | read ("The other PIMs") | other PIMs |
| PIM/c: TR-672, TR-671, TR-863, TM-870. PIM/i: TR-675, TM-1017, TM-1264. PIM/k: TR-767, TR-768, TR-769, TM-766. General: TR-556, TM-1260 (PIM WG Grand Meeting report, 210 pp.) | `ICOT:` | read or skimmed as stated in "The other PIMs" sec. 9 | other PIMs |
| Miyazaki et al., "マルチPSI/V2におけるコード形式について" (Code representation of Multi-PSI/V2), TM-662, IPSJ 38th Nat. Conv. 1989 | `ICOT:TM/TMpdf/tm0662.pdf` | read from page images (sec. 8a) | 4 |
| Kimura, Goto, Nakajima, Chikayama, "KL1抽象命令セットの改良について" (Improvement of KL1 Abstract Instruction Set), TM-652, 1989 | `ICOT:TM/TMpdf/tm0652.pdf` | read from page images (sec. 8a) | 3, dialects |
| Takahashi, Takeda, Murasawa, Komori, Sugino, "PIM/mのメンテナンス系アーキテクチャとCSP" (Maintenance Architecture and CSP on PIM/m), TM-1213, IPSJ 45th Nat. Conv. 1992 | `ICOT:TM/TMpdf/tm1213.pdf` | read from page images (sec. 8a) | 8 |
| TM-767 (Miyauchi et al., batch GC and memory consumption on Multi-PSI/V2, 1989) | `ICOT:TM/TMpdf/tm0767.pdf` | downloaded, not read | 7 |
| TM-444 (Nakajima, KL0 implementation on PSI-II, 1988); TM-696 (Masuda et al., Multi-PSI basic configuration, 1989); TM-750 | `ICOT:TM/TMpdf/` | single passages read (OCR), Appendix C sec. 8 | 8 |
| TM-850, TM-1021, TM-1022, TM-849, TM-346, TM-768, TM-551, TM-671, TM-261, TM-353, TM-354, TM-212, TM-213 (unlisted memoranda on PIM/m, Multi-PSI/V2 and PSI-II firmware) | `ICOT:TM/TMpdf/`; titles in `ICOT:TM/TMidx/tmNNNN.idx` | resolved, not read (titles read) | 1-8 |
| PIMOS manual v1.5 (English, Dec 1989, 177 pp.) and PIMOS 3.0 manual (Japanese, 535 pp.); PIMOS primers | `https://www.cs.cmu.edu/afs/cs/project/ai-repository/ai/areas/icot/manuals/pimos/man.tgz`; `UEDA/ifs/manuals/pimos/` | opened; sec. 6.1 of the 3.0 manual and the primer's boot panel read (Appendix D item 8), the rest not | 8, 9 |
| IFS abstract no. 3 (Pseudo PIM/m) | `https://www.airc.aist.go.jp/aitec-icot/ICOT/Museum/IFS/abst/003.html` | read | 8 |
| "Document for FGCS'92 Demonstrations", p. 14 | `https://www.airc.aist.go.jp/aitec-icot/ICOT/Museum/FGCS92Demo/E/doc014.html` | read through a text extractor | 7 |
| IPSJ Computer Museum, FGCS page | `https://museum.ipsj.or.jp/en/computer/other/0002.html` | read | 9 |
| Mitsubishi Denki Giho 1986-1992, nine articles on MELCOM PSI, PSI II, Multi-PSI, PSI/UX, PIM/m | `https://www.giho.mitsubishielectric.co.jp/giho/pdf/YYYY/YYMM.pdf` (list in Appendix D item 5) | three issues opened; the PSI/UX hardware article and the 1992 PIM article read | 8 |
| IPSJ repository, 130 papers 1984-1996 | list in Appendix D item 6 | 40 downloaded, 20 read by the survey | all |
| ICOT TR and TM index pages | `ICOT:TR/TRlist.html`, `ICOT:TM/TMlist.html` | read | 9 |

Not opened, cited by the above (the proceedings versions of reports we
did read): ICLP'87 pp. 276-293 and 257-275; ICLP'89 pp. 436-451;
NACLP'89 pp. 907-921; ICCD'90 pp. 355-359; CICC'91 pp. 15.3.1-15.3.4
(Machida et al., "A 1.5 MLIPS 40-bit AI Processor"); the Wiley book.

## Most worth obtaining or doing next

1. **Decode what we already hold in `psdpim.tar.Z`.** `pimm.MEkbn` (the
   IMPL microcode-load file; by measurement a tagged table followed by
   what looks like halves of 64-bit microinstructions), the console's
   micro reverse assembler in `pimmutil.ptf`, its goal record inspector
   in `pimmcsp.ptf`, and the FEP SCSI code in `pimfep.ptf` /
   `pimscsi.ptf`. With the 64-bit field figure of TR-733 this is the one
   route to the real goal record, suspension and GC code. It needs the
   SIMPOS package-template format understood first.
2. **The rest of TM-1044 as a design reference** for the multi-PE work
   (messages, shoen protocol), keeping in mind it is the other family.
3. **The unlisted two-page TMs** on the AIST host (IPSJ national
   convention papers; the 106 on hardware and KL1 are tabulated in
   Appendix E): several are on Multi-PSI and PIM/m
   firmware topics and were not read.
4. **TM-444** (Nakajima, KL0 implementation on PSI-II, 1988) and
   **TM-696** (Multi-PSI basic configuration) in full; only single
   passages were read.
5. **TM-1260**, the 1993 PIM working group report (210 pages of
   slides), in full for PIM/m slides; it was only skimmed for the other
   machines.
6. **Download and read what section 9 lists as open**: the Japanese
   PIMOS 3.0 manual and the v1.5 manual from `ifs/manuals/`, and the
   Mitsubishi Denki Giho PSI II and PSI/UX articles.
7. **Ask for what exists only on paper or in a museum** (Appendix D,
   "Ranked: most worth obtaining"): the Multi-PSI/V2 Console System
   (CSP) Operating Manual; whatever media and documents accompany the
   PIM/m preserved at the National Museum of Nature and Science; the
   JAIST PSI machine and its manuals; the ICCD'90 and CICC'91 papers
   and the Wiley chapter through a library.



Note on paths: `(scratch)/...` in the appendices names working files of the reading passes (page renders, OCR text). They were temporary and are not in the repository; every quote is tied to a document and page so it can be re-checked from the source.

## Appendix A. Multi-PSI/V2: extraction from the ICOT reports

Status: draft. Purpose: closest documented relative of the lost PIM/m KL1 microcode.

Conventions
- Citation form: `TR-NNN, section, printed p. X (PDF p. Y)`.
- `[img]` = quote/number checked against the rendered page image. `[ocr]` = taken from tesseract text only (wording reliable, digits less so).
- `[INFERENCE]` = my reading, not a statement in the source.
- Every fact is labelled with the system it describes when that is not the Multi-PSI/V2 microcoded implementation (e.g. "general MRB scheme", "PIMOS level", "early shared-memory PIM").
- Printed-page offsets (checked on page images): TR-715, 439, 466, 469, 531, 585, 341, 737, 530, 764, 250, 563, 498, 321: printed = PDF - 1. TR-248, TR-390, TR-483: printed = PDF - 3. TR-373: printed = PDF - 2.
- Provenance: the eight core English reports (715, 439, 390, 466, 248, 469, 531, 585) were read in full by me; the six peripheral English reports and the four Japanese reports were read by two sub-readers (the Japanese ones entirely from page images) and merged here; in those subsections the [img]/[ocr] flags are theirs. I spot-checked four of their claims against page images and all held: TR-373 PDF p. 13 (priority width 2^12, superscript degraded), TR-483 PDF p. 13 (n/4095 and Fig. 2), TR-483 PDF p. 31 (pseudo Multi-PSI, two microcode sets, fn. 24), TR-530 PDF p. 10 (GOAL tag, the two counters).

### 0. Bibliography

URL pattern: `https://www.airc.aist.go.jp/aitec-icot/ICOT/Museum/TRTM/TR/TRpdf/trNNNN.pdf`

| TR | Authors | Title | Date | PDF pp. | Published version (as stated in the report or in later reports' reference lists) |
|---|---|---|---|---|---|
| TR-715 | K. Nakajima (Mitsubishi) | Distributed Implementation of KL1 on the Multi-PSI | Nov 1991 | 25 | Book chapter; footnote p. 1: "extended version of the paper titled 'Distributed Implementation of KL1 on the Multi-PSI/V2' in Proceedings of International Conference on Logic Programming, 1989"; section 7 derived from Nakajima & Ichiyoshi, ICPP 1990 Vol. I (= TR-531). The book is not named in the report. |
| TR-439 | K. Nakajima, Y. Inamura, N. Ichiyoshi, K. Rokusawa, T. Chikayama | Distributed Implementation of KL1 on the Multi-PSI/V2 | Dec 1988 | 13 | Proc. 6th ICLP, 1989 (per TR-466 ref. [6], TR-715 [Nakj89a]) |
| TR-466 | Y. Inamura, N. Ichiyoshi, K. Rokusawa, K. Nakajima | Optimization Techniques Using the MRB and Their Evaluation on the Multi-PSI/V2 | Apr 1989 | 11 | NACLP'89 (per task brief; cover does not say) |
| TR-248 | T. Chikayama, Y. Kimura | Multiple Reference Management in Flat GHC | Mar 1987 | 18 | Proc. 4th ICLP, 1987, pp. 276-293 (page range from TR-469 ref. [2]) |
| TR-390 | N. Ichiyoshi, K. Rokusawa (cover); FGCS'88 version adds K. Nakajima, Y. Inamura | A New External Reference Management and Distributed Unification for KL1 | Jun 1988 | 27 | Proc. FGCS'88, pp. 904-913 (per TR-469 ref. [5]) |
| TR-341 | K. Rokusawa, N. Ichiyoshi, T. Chikayama, H. Nakashima | An Efficient Termination Detection and Abortion Algorithm for Distributed Processing Systems | Feb 1988 | 9 | Proc. ICPP 1988, Vol. I, pp. 18-22 (per TR-737 ref. [1]) |
| TR-737 | K. Rokusawa (Oki), N. Ichiyoshi | A Scheme [cover: "Sheme"] for State Change in a Distributed Environment Using Weighted Throw Counting | Feb 1992 | 8 | none named |
| TR-585 | S. Onishi, Y. Matsumoto, K. Nakajima, K. Taki | Evaluation of the KL1 Language System on the Multi-PSI | Aug 1990 | 11 | not stated |
| TR-531 | K. Nakajima, N. Ichiyoshi | Evaluation of Inter-processor Communication in the KL1 Implementation on the Multi-PSI | Feb 1990 | 21 | Proc. ICPP 1990, Vol. I, pp. 613- (per TR-715 footnote) |
| TR-469 | N. Miyauchi, Y. Kawada (Mitsubishi / SET Corp.), K. Nakajima | Tracing Garbage Collection for KL1 on the Multi-PSI/V2 System | Mar 1989 | 21 | not stated |
| TR-530 | Y. Inamura, S. Onishi | A Detection Algorithm of Perpetual Suspension in KL1 | Feb 1990 | 17 | Proc. 7th ICLP, June 1990 (per TR-715 [Inam90a]) |
| TR-764 | H. Yashiro, T. Fujise, T. Chikayama, M. Matsuo, A. Hori (Mitsubishi), K. Wada | Resource Management Mechanism of PIMOS | Apr 1992 | 16 | none named; PIMOS 3.2 |
| TR-483 | T. Chikayama, H. Satoh (Mitsubishi), T. Miyazaki (Oki) | Overview of the Parallel Inference Machine Operating System (PIMOS) | Jun 1989 | 33 (printed = PDF - 3) | none named; FGCS'88 paper of the same title, pp. 230-251, is cited by the other reports |
| TR-250 | M. Sato, H. Shimizu, A. Matsumoto, K. Rokusawa, A. Goto | KL1 Execution Model for PIM Cluster with Shared Memory | Apr 1987 | 19 | NOT Multi-PSI: early shared-memory PIM design |
| TR-373 | 宮崎敏彦, 内田俊一 (T. Miyazaki, S. Uchida; only two authors on the cover) | 並列論理型言語KL1の実現方式と並列OSの記述 ("Implementation method of the parallel logic language KL1 and description of a parallel OS") | May 1988 | 45 (printed = PDF - 2) | none named; survey of the Multi-PSI design "under study" |
| TR-498 | 木村康則, 近山隆 (Y. Kimura, T. Chikayama) | 並列論理型言語KL1の多重参照管理によるガーベジコレクション | Aug 1989 | 31 | none named; measured on PDSS (C emulator) |
| TR-563 | 中島克人, 稲村雄, 市吉伸行 (K. Nakajima, Y. Inamura, N. Ichiyoshi) | 疎結合並列マシンMulti-PSI上でのKL1分散処理系におけるプロセッサ間通信の評価 | May 1990 | 9 | none named; Japanese counterpart of TR-531 |
| TR-321 | 木村康則, 西田健次, 宮内信仁, 近山隆 | KL1の多重参照ビットによるGC方式について ("Realtime GC by Multiple Reference Bit in KL1") | Nov 1987 | 9 | Data Flow Workshop 1987, pp. 215-222 (per TR-469 ref. [7]); C emulator, PIM-motivated |

Differences between the 1988 and 1991 accounts are reported separately below and never merged.

---

### Gap 1. Goal record and the ready queue

#### 1.1 Goal record
- Fields named, no sizes or offsets: "Goal contexts are maintained in a goal record, which contains the predicate code address, arguments, priority and etc." TR-715, 4.4, printed p. 7 (PDF p. 8) [ocr].
- "Goals are represented by goal records whose fields are argument slots, pointer to code, and so on." TR-585, 3, printed p. 2 (PDF p. 3) [ocr].
- What a `%throw_goal` must carry gives a lower bound on the record's contents: "The goal information in the goal record such as predicate code, goal arguments and execution priority are encoded into %throw_goal message." TR-715, 5.2.1, printed p. 9 (PDF p. 10) [ocr]. TR-390 adds the owning shoen: throw message encodes "the code of the predicate of the goal, the arguments of the goal, the shoen to which the goal belongs plus other bookkeeping information" TR-390, 3.2, printed p. 5 (PDF p. 8) [ocr].
- Goal "colour" (normal / traced / spying, with spied predicate name+arity inherited by children) is per-goal state, so it must live in or beside the record: TR-715, 6.1, printed p. 17 (PDF p. 18) [ocr]. [INFERENCE] that it is a goal-record field.
- Goal record size in words, field order, link field position: **not found in these reports** (English core set). See 1.6 for the Japanese TR-373 and for TR-250's early-PIM record.

#### 1.2 Free goal-record list
- "Goal record can be reclaimed at popping from goal stack into a free goal record list." TR-715, 4.4, printed p. 7 (PDF p. 8) [ocr].
- General free lists are by size class (1..8, 16, 32, 64, 128, 256 words; see Gap 7). Whether goal records use one of those classes or a dedicated list: the sentence above says a dedicated "free goal record list"; its record size is not given.
- General MRB scheme (TR-248): body-goal arguments are written straight into a goal record "in the goal queue designated by G_i" with `set_*` instructions ("goal stacking"): TR-248, 6.4, printed p. 11 (PDF p. 14) [ocr].

#### 1.3 Prioritized goal stack
- One per PE, not global: "each PE may have each prioritized goal stack, at the sacrifice of scheduling strictness" TR-715, 4.3, printed p. 7 (PDF p. 8) [ocr]; same in TR-439, 3.3, printed p. 5 (PDF p. 6) [ocr].
- Structure: "Each processor has a goal stack table which is the root of all runnable goals. The table has pointers to goal stacks corresponding to physical priorities. The processor picks up the topmost goal of the highest non-empty goal stack and executes." TR-585, 3, printed pp. 2-3 (PDF pp. 3-4) [img for the second and third sentences].
- The goal stack is a linked list of goal records, not a contiguous stack: "active goals are chained to a list, called goal stack" TR-469, 4, printed p. 10 (PDF p. 11) [ocr].
- TR-531 calls the same thing "goal pools": "Reduced KL1 body goals are stored in the current priority goal pool, or other priority pools if priority pragmas are specified. KL1 execution is done by choosing a goal from the highest priority pool." TR-531, 2.3.1, printed p. 5 (PDF p. 6) [ocr].
- Number of physical priority levels: **not found in the English core reports** (see 1.6).
- Logical vs physical priority: TR-585 uses the term "physical priorities" for the table index (above). The language-level rule is: "The shoen has a priority range and each goal inside it can have an individual priority within this range. The priority is specified by a priority pragma with a relative value in the allowed range." TR-715, 2.2(3), printed p. 3 (PDF p. 4) [ocr]. The shoen is created with the range: `execute(Goal, ControlStream, ReportStream, MinPrio, MaxPrio, Mask)` TR-715, 5.3.1, printed p. 10 (PDF p. 11) [img]. TR-390 (1988) gives a different argument order and arity: `execute(Min,Max,Mask,Code,Argv,Control,Report)` = execute/7, "Min and Max are minimum and maximum possible priorities allowed in the shoen" TR-390, 2, printed p. 3 (PDF p. 6) [ocr]. The normalisation arithmetic is not in the core reports; see 1.6 (TR-483 priority pragma).
- Priority is cached in a register: "Control information, such as the priority and the shoen resource, is cached on the registers as long as the execution context remains unchanged." TR-715, 4.2, printed p. 7 (PDF p. 8) [ocr].

#### 1.4 Reduction cycle; which body goal runs next
- 1988 wording: "If one of the clauses commits, all the body goals except for the leftmost one in the source code are pushed to the goal stack. The leftmost goal is chosen as the next one to evaluate. When a clause without body goals commits, another goal is popped from the goal stack." TR-439, 3.1, printed p. 4 (PDF p. 5) [ocr].
- 1991 wording (adds the priority check and the unification exception): "all the user-defined body goals, except for the unification goals and the leftmost user goal in the clause, are pushed to the goal stacks according to the priority pragmas attached to the goals. Unification goals are executed immediately. The leftmost user goal is chosen as the next one to be evaluated unless the goal stack of the higher priority has a goal." TR-715, 4.1, printed p. 6 (PDF p. 7) [ocr].
- 1990 wording says the LAST goal is the one run by tail recursion, and that push is onto the current-priority stack: "Goal records are allocated for the user-defined body goals and pushed onto the top of the current goal stack (thus the scheduling is depth-first), except for the last one goal which is executed tail recursively." TR-585, 3, printed p. 3 (PDF p. 4) [img].
  - [INFERENCE] The two statements ("leftmost in the source" vs "last one") are reconciled by the compiler's code order: in TR-248 Fig. 5 the clause `p(X) :- true | q([X]), r(X).` compiles to `enqueue_goal r/1 ... execute q/1`, and `p :- true | q(X), r(X), s(X).` compiles to `enqueue_goal s/1; ...; enqueue_goal r/1; ...; execute q/1` (TR-248, Fig. 5, printed p. 12 (PDF p. 15) [img]). So the source-leftmost goal is emitted LAST as `execute`; the others are enqueued right-to-left, so that after a LIFO push the source order is q, r, s. "Last" in TR-585 is the last in object-code order.
- With a `@priority` pragma: "the goal is pushed onto the goal stack corresponding to the specified priority, not the previous one." TR-585, 3, printed p. 3 (PDF p. 4) [img].
- Guard clauses are tried sequentially: "guard unification is performed one by one for efficiency reason." TR-715, 4.1, printed p. 6 (PDF p. 7) [ocr].
- After suspension, failure, or a clause with no user body goal: "the next goal is picked up from the highest priority goal stack for execution." TR-585, 3, printed p. 3 (PDF p. 4) [img].
- Failure: "If no clause commits and there is no suspended clause, a failure is reported on the report stream of the shoen with the goal information." TR-715, 4.1, printed p. 6 (PDF p. 7) [ocr].
- Slit check, once per reduction: "Every reduction cycle, request for (non-incremental) GC and message arrivals from the network are checked, and processed if necessary. This timing, called the slit check, is most suitable for switching the process because the PE is free from goal contexts." TR-715, 4.1, printed p. 6 (PDF p. 7) [ocr]; identical in TR-439, 3.1, printed pp. 4-5 [ocr].
- Argument registers: "The arguments for the unification are fetched on the registers every reduction cycle." TR-715, 4.2, printed pp. 6-7 [ocr].

#### 1.5 KL1-B instructions and costs
- `enqueue_goal p/n`, `execute p/n`, `set_* X, G_i` (write into the goal record being built), `put_* X, A_i` (argument registers for the goal run next): TR-248 Table 2 and Fig. 5, printed pp. 11-12 (PDF pp. 14-15) [img for Fig. 5]. This is the general FGHC abstract machine of 1987; the reports do not say the Multi-PSI/V2 opcode set is identical. `proceed` is not named anywhere in the English core reports.
- Costs (TR-585, Fig. 1, printed p. 5 (PDF p. 6) [img]; unit = 1 append-LI = one iteration of the first `append` clause = 39 microinstruction steps, about 8 microseconds, 128 KRPS):
  - (e-1) goal stack enqueue + dequeue: 0.7 append-LI. [INFERENCE] about 27 steps, about 5.5 microseconds.
  - (g-1) guard unification success on atomic: 0.05; (g-2) success on list: 0.3.
  - (s-1) suspension (hook + re-enqueue + dequeue), single: 1.8; (s-2) 2-way multiple wait: 3.7; (s-3) 4-way multiple wait: 6.8; (s-4) built-in: 3.3.
  - (b-1) body unification, bind value to var: 0.2; (b-2) var-var make ref: 0.3; (b-3) atomic-atomic match: 0.1; (b-4) list-list match: 1.25 ("not optimized in the current implementation").
- "The cost of one reduction (iteration) of the first clause is 39 steps of the micro instructions in the best case (no suspension, and so on), and the speed turns out 128 KRPS ... assuming no cache miss." TR-585, 4.1, printed p. 3 (PDF p. 4) [img].
- Tail-recursion gain: "the gain of TRO in append is (0.7/1.7) x 100 = 40 %." TR-585, 4.2, printed p. 4 (PDF p. 5) [ocr].
- Other speed figures: 150 K reductions/sec for append (TR-439, 5, printed p. 10 (PDF p. 11) [ocr], Dec 1988); Append 110 / 128 / 146 KRPS for no reuse / frame reuse / element reuse (TR-466, Table 1, printed p. 7 (PDF p. 8) [img]); Pentomino 39.3 KRPS and Bestpath 23.4 KRPS on 1 PE (TR-531 Table 2 [img]).

#### 1.6 From the peripheral and Japanese reports
Flags here are the sub-readers' (page images unless marked); I spot-checked the 2^12 line on the TR-373 page image.
- Priority width (Multi-PSI design "under development", May 1988): "現在開発中のマルチPSIではこの優先度の幅を2^12程度用意しており" = "the Multi-PSI under development provides a priority width of about 2^12". TR-373, 2.3.1, printed p. 11 (PDF p. 13) [img; the superscript is degraded in the scan, "12" is the probable reading and agrees with the 4095 denominator below]. This is the only statement of the number of priority levels in the whole set.
- Priority pragma arithmetic (KL1/PIMOS level; TR-483, 2.4.2 and Fig. 2, printed pp. 9-10 (PDF pp. 12-13) [img]): two forms, `@priority_in_shoen(n)` and `@priority_to_current(+-n)`. "The ratios are given by an integer n, where n/4095 is the actual value of the ratio" (OCR reads 1/4095; image n/4095). Fig. 2 bars: in_shoen spans shoen-min..shoen-max split n : 4095-n; to_current(neg.) spans shoen-min..current split 4095-n : n; to_current(pos.) spans current..shoen-max split n : 4095-n. [INFERENCE] p = smin + (smax-smin)*n/4095; p = cur + (smax-cur)*n/4095 for n >= 0; p = cur - (cur-smin)*|n|/4095 for n < 0; rounding not stated. Examples: `q(X,Y)@priority_in_shoen(4095)` = highest in the shoen; `r(Y,Z)@priority_to_current(-16)`.
- TR-373 names the same two methods 所属荘園内割合指定 and 所属荘園内自己相対指定 (2.3.1, printed p. 10 (PDF p. 12) [img]).
- Defaults: "When no priority pragma is given, the priority of the parent goal is used as the default value. When a new shoen is created, its top level goal will have the maximum priority allowed in the shoen." Range is fixed: "once a shoen is created, its priority range cannot be changed afterwards." TR-483, 2.4.2 and fn. 11 [img].
- Logical vs physical: "Different implementations may have different physical priority ranges. Relative priority specification can be free from such implementation dependency." TR-483, printed p. 10 [img]. No mapping table is given anywhere.
- Within one priority: "simple depth-first scheduling is known to yield the best results usually"; priority is only a hint, but "a goal with the highest priority should be reduced at least by one step within a finite time period". TR-483, 2.4.1-2.4.3 [img/ocr].
- `alternatively` clause separator: later clauses tried "not only when the first clause fails but also when it suspends" TR-483, 2.4.4, printed p. 11 (PDF p. 14) [ocr].
- Goal record on Multi-PSI has its own tag and lives in the GC'd heap: "We introduced a new tag GOAL which only appears in goal records and enables us to distinguish goal records from other data objects during the sweeping." TR-530, 4.2, printed p. 9 (PDF p. 10) [img]. Contents: "the goal's context such as arguments of the goal and a code pointer" (3.1 [ocr]). The ready structure is "the ready goal stack, a stack of goal records ready for execution" [ocr].
- Each goal points to its shoen record: "各ゴールは、自身が所属している荘園の荘園レコードへのポインタを持ち" TR-373, 3.4, printed pp. 18-19 (PDF pp. 20-21) [img] (design level).
- A goal counter exists (for termination detection), "incremented or decremented on the creation or the termination of a goal". TR-530, 4.1 fn. 2 [img].
- PDSS (C emulator, not microcode): goal record = argument slots + code + "slots for other control information" (TR-498, 5.1, printed p. 14 [img]).
- Body-goal order evidence from the 1987 emulator paper: `p :- true | q([X|Y],Y), r(X,[Y|X]).` compiles to `create_goal r/2; set_list A1,G1; ...; enqueue_goal r/2; put_list A1; ...; execute q/2` (TR-321, Fig. 6, printed p. 6 (PDF p. 7) [img]) - leftmost goal run in place, the other queued; note the 1987 set has `create_goal` before the `set_*` and `enqueue_goal` after them.
- EARLY-PIM (TR-250, shared-memory cluster design, April 1987; NOT Multi-PSI): Table 1 goal record fields = "Status of a goal; Link to goal records; Arguments list; Pointer to code; Pointer to metacall record" (printed p. 4 (PDF p. 5) [img]). KL1-B codes named there: wait, suspend, get, set, enqueue, p-enqueue, execute, proceed; `execute` reuses the parent's goal record for the goal run next and `proceed` decrements the metacall's children counter (2.2 [ocr]). Its "high/low priority queues" are for load distribution only.

---

### Gap 2. Suspension

#### 2.1 Hooking
- Non-busy wait, hook on the variable cell itself: "a pointer to the suspended goal is written on the variable cells (the goal is said to be hooked onto the variables). When one of the variables becomes instantiated, the goal can be put back to the goal stack for scheduling." TR-585, 3, printed p. 3 (PDF p. 4) [img].
- Which variables: 1988 "the goal is hooked to the causal variable of the suspension" (singular), TR-439, 3.1, printed p. 4 [ocr]; 1991 "the goal is hooked on the variable(s) that caused the suspension", TR-715, 4.1, printed p. 6 [ocr].
- Single vs multiple wait: "If there are two unbound variables which may allow to commit a clause, the goal is hooked to both to construct an OR-wait suspension (s-2)." TR-585, 4.2, printed p. 4 (PDF p. 5) [ocr]. Costs 1.8 / 3.7 / 6.8 append-LI for 1 / 2 / 4 variables (above) [img].
- There are distinct tagged variable kinds: "There are several types of unbound variables: hook variables, multiple hook variables, etc in the actual KL1 implementation. The distinction is mainly for optimizations" TR-390, 4, footnote 2, printed p. 5 (PDF p. 8) [ocr]. Exported unbound variables also have their own tag: "UNDEF and EUNDEF denote non-exported and exported unbound variables. (They are distinguished by the tag in the KL1 implementation.)" TR-390, App. A, printed p. 23 (PDF p. 26) [img].
- GC confirms the object kinds: "various data types ... such as suspended goals and variables which hook them, special data for a constant time merger, pointers to data in other processors, and instruction codes." TR-469, 4, printed p. 10 (PDF p. 11) [ocr].
- Suspension-record / flag-record layouts, hook chain order, what happens when two hooked variables are unified, order of resumption: **not found in the English core reports**. See 2.5.
- Where resumed goals go: back on the goal stack of their own priority: the goal "would be stored back in the former goal pool when the variable is instantiated" TR-531, 2.3.1, printed p. 5 (PDF p. 6) [ocr]; Fig. 3 of TR-715 / Fig. 1 of TR-439 label the arc from "Suspended goals" to "Prioritized goal stack" as "Resumption" [ocr].
- No hardware help: "The suspension costs are not small because the PE does not have any special hardware for manipulating goal records." TR-585, 7, printed p. 10 (PDF p. 11) [ocr].

#### 2.2 Body built-ins and body unification with unbound input
- "a body unification is done in-line. The body built-in predicate goal is also executed in-line, except when one of its input arguments is uninstantiated. In this case, a goal which execute the built-in goal is created and is hooked onto the uninstantiated argument." TR-585, 3, printed p. 3 (PDF p. 4) [img]. Cost (s-4) = 3.3 append-LI [img].
- Body unification never suspends locally: variable-variable makes a REF (b-2). Remote cases go through `%unify` (Gap 6).

#### 2.3 Remote reads suspend too
- A `%read` arriving for a still-unbound exported variable is itself hooked: "the reply is suspended by hooking the received %read message on the variable." TR-715, 5.2.2, printed p. 9 (PDF p. 10) [ocr]. [INFERENCE] so a variable's hook chain can hold reply records as well as goal records.
- The requesting side: the EX cell is replaced by a cell on which the goal hooks: Return "is also an external pointer pointing to the cell which substitutes the former external pointer and will be instantiated by the value returned by %answer_value message. The suspended goal is hooked on the cell until it is instantiated." TR-715, 5.2.2 [ocr]. The EX cell remembers that a read was sent: "the first read attempt is remembered by X' and the second attempt only waits for the return of the value" TR-390, 4.1, printed p. 7 (PDF p. 10) [ocr].
- A goal thrown to a PE that lacks its code module "is hooked on a newly created variable which will receive the module." TR-715, 5.4.8, printed p. 17 (PDF p. 18) [ocr].

#### 2.4 Merger built-in (TR-466, 3.3, printed pp. 3-5 (PDF pp. 4-6))
- Two special objects: "merger hooked variable: MHV" and "merger record: MR". "The MHV points to the MR and the MR points to a variable cell which corresponds to the output variable of the merger process. The MR also contains an integer value which indicates the number of input streams to itself. This value is used to detect the termination of a merger process" [ocr text; structure checked on Fig. 2 image].
- Fig. 2 [img]: MHV cell -> MR (two words drawn: word 0 = pointer to Merger Output cell, tagged VAR; word 1 = N). Several MHVs point to the same MR.
- Fig. 3 [img], unifying an MHV with cons cell [X|Y]: (a) before: MHV -> MR(ptr, N) -> VAR output. (b) after: a New Cons cell is allocated whose CAR = X and whose CDR -> a new VAR cell ("New Merger Output"); the old output cell becomes LIST -> New Cons cell; the MR's pointer is redirected to the new VAR; a "New MHV" (pointing to the same MR) is unified with Y, the tail of the input. N is unchanged.
- "A unification between an MHV and list data causes the instantiation of the output variable with new list data immediately, thus eliminating the overheads associated with suspension" [ocr].
- MRB optimisation: "When the input cons cell is single-referenced, it can be reused as the new output cons cell." [ocr]. Measured: built-in merger 4x faster than the KL1-defined merger; MRB-off input twice as fast as MRB-on (TR-466, 4.2, printed p. 7 (PDF p. 8) [img]).
- Adding inputs: "When a vector is unified to an MHV, as many input streams (MHVs) as the arity of the vector are added to the merger process and each element of the vector is unified to each new input stream." Only `merge/2` exists as a built-in: "only 'merge/2' is prepared as a built-in predicate, and merger processes which have multiple input streams are realized only by the unification between an MHV and a vector" TR-466, 3.3, printed p. 5 (PDF p. 6) [ocr].
- Fig. 4 logical definition [ocr]: `merge([],Out) :- Out=[]`; unifying an input with `[]` drops one input (N decrements; when the last input closes the output is closed with `[]`) [INFERENCE from "This value is used to detect the termination" plus Fig. 4]; `merge({},Out) :- Out=[]`, `merge({X},Out) :- merge(X,Out)`, `merge({X,Y},Out) :- merge(X,Y,Out)`.

#### 2.5 From the peripheral and Japanese reports
- Multi-PSI design, 1988: a per-variable suspension stack. On suspension the goal is "原因となった変数に付加されている中断スタックにプッシュされる" (pushed on the suspension stack attached to the causing variable); on binding "中断スタック中のゴールは全てゴール・スタックに移され" (all goals in the suspension stack are moved to the goal stack). TR-373, 3.2, printed p. 15 (PDF p. 17) [img]. Fig. 3 shows the unbound cell pointing to a chain of goals. Resumption order is not stated.
- A remote `%read` waiting on an unbound variable is represented as "返信用の特殊なゴール" (a special reply goal) pushed on that variable's suspension stack: TR-373, 3.3.1, printed p. 16 (PDF p. 18) [img]. This supports the [INFERENCE] in 2.3 (a goal-like reply record on the same chain), but TR-373 is a 1988 design survey, not a description of the V2 microcode.
- Multi-PSI (1990): "a goal record ... is hooked to the variable(s)"; several goal records may hang on one variable ("the goal records hooked to the variable are resumed"); resumed records "are pushed to the ready goal stack". TR-530, 3.1, printed p. 6 (PDF p. 7) [ocr]. TR-530 Fig. 4 [img] draws cells tagged HOOK pointing directly at the goal record whose argument cells are REF back to the HOOK cell; it is a schematic and shows no suspension records.
- PDSS: "サスペンションレコード" (suspension records) are allocated for suspended goals (TR-498, 5.1 [img]); no layout.
- EARLY-PIM (TR-250, not Multi-PSI) is the only place a multiple-wait layout is drawn: Table 1 suspension record = "Link to a next suspension record; Link to a goal record; Link to an OR-waiting flag"; Fig. 4 (printed p. 13 (PDF p. 14) [img]): variable cell [hook | ptr] -> suspension record of two cells ([hook|next] or [undef] at end of chain; [ref | -> OR waiting flag]); the OR waiting flag is one cell holding "goal ID" (pointer to the goal record) or NULL: "NULL shows that the other variable has already been instantiated." Resume: for each suspension record on the chain, if the flag holds a goal ID write NULL and enqueue the goal; if NULL do nothing. [INFERENCE] The Multi-PSI "multiple hook variable" + 3.7/6.8 append-LI multi-wait costs are consistent with the same flag-indirection idea, but no Multi-PSI report shows it.
- Built-in suspension rules at language level: `apply(Code, ArgVector)` suspends until both are instantiated; `set_vector_element` until its first two arguments are (TR-483, 2.6.2, 2.7.1 [img]).
- Merger at language level: `merge(In, Out)`; `merge({}, O) :- O = [].`, `merge({I}, O) :- merge(I, O).`, `merge({I1,I2}, O) :- merge(I1, I2, O).`; "the actual implementation is of course quite different. It is highly optimized using the MRB information." TR-483, 2.7.2, printed p. 15 (PDF p. 18) [img].
- Unifying two hooked variables; single-wait record layout on Multi-PSI: **not found in these reports**.

---

### Gap 3. MRB

#### 3.1 Where the bit lives
- General scheme: "One additional bit in pointers is used"; "All the memory words and all the argument/temporary registers have one extra bit called MRB" TR-248, 2 and 5.1, printed pp. 2, 8 (PDF pp. 5, 11) [ocr]. The S (structure pointer) register "also has its own MRB field" (ibid.).
- Multi-PSI/V2: "The MRB is one-bit information attached to every reference pointer." TR-466, 2, printed p. 2 (PDF p. 3) [ocr]. Word is "40-bit (8-bit for tag, 32-bit for data)" TR-715, 3.1; TR-585, 2.1 [img]. Which of the 8 tag bits is the MRB, and its polarity in the tag encoding: **not found in the English core reports** (see 3.7). Logical polarity: off (reset, white circle) = guaranteed single reference; on (set, black circle) = possibly multiple. "if the MRB of the pointer is off, the pointer is guaranteed to be the sole pointer to the data" TR-466, 2 [ocr].
- The copying GC uses, in each old-space object, "the GC bits and MRB of the object in old area" to encode four visit states (TR-469, 3.3, printed p. 10 (PDF p. 11) [ocr]) - so there is at least one GC bit per word besides the MRB: "Generally one bit of a memory cell is used as a GC bit" TR-469, 3.2, printed p. 6 (PDF p. 7) [ocr].

#### 3.2 Invariants (general scheme, TR-248 section 2, printed pp. 2-3 (PDF pp. 5-6) [ocr]; restated for Multi-PSI/V2 in TR-469 Figs. 1-2)
- Structures: S1 "There exists only one reference path to the structure which is an SRP." S2 "All the reference paths to the structure are MRP's."
- Uninstantiated variable cells (the exception): U1 "There exist exactly two SRP's to the cell." U2 "There exists only one SRP to the cell. All the other paths, if any, are MRP's." U3 "All the reference paths are MRP's."
- Instantiated variable cells (MRB of the pointer to the cell combined with MRB of the datum stored in the cell): I1 cell datum MRB reset, one SRP; I2 datum MRB reset, all paths MRP; I3 datum MRB set, exactly one SRP plus any MRPs; I4 datum MRB set, all MRP.
- Multi-PSI/V2 statement of the exception: "As for variables, one can have up to two pointers with the MRB off. Typically, a variable is shared by a producer process and a consumer process, and is instantiated to a concrete data via one of the pointers, and the variable cell together with the data will be reclaimed when the data is read via the other pointer." TR-466, 2, printed p. 2 (PDF p. 3) [ocr].

#### 3.3 Maintenance rules (TR-248 section 4, printed pp. 5-8 (PDF pp. 8-11) [ocr])
- New structure built as a body-goal argument: pointer MRB reset (S1).
- New variable: MRB set by the number of body occurrences: in `p :- true | q(X,Y), r(Y,Z), s(Z,Z).` "the MRB of the pointers to X and Y should be reset (U1) and that to Z should be set (U3)" - two occurrences -> both off; three or more -> on; one occurrence X (void-like) off.
- Dereference: result MRB reset only in case I1 (path SRP and cell datum MRB reset); in I2/I3/I4 "the MRB of the result should be set". In case I1 the variable cell just passed through is consumed.
- Instantiation (binding, including var-var): "MRB of the data stored in the variable cell can be reset if and only if the reference to the variable cell is an SRP and the MRB of the data to be stored there is reset. In all other cases, the MRB of the stored data should be set."
- Duplication (head variable occurring twice or more in the body): "MRB of the duplicated pointers should be set".
- Structure element retrieval: if the path to the structure is MRP, "the MRB of the retrieved value should be set regardless of the MRB stored in the structure"; if SRP, "the MRB of the structure elements can be simply copied as the MRB of the retrieved result."
- Unit of atomicity: "all the required conditions on MRB are maintained correctly before and after each reduction, but not necessarily during a goal reduction." TR-248, 5.1 [ocr].
- No variables inside structures: "structure elements should not be used directly as variable cells ... a new variable cell is allocated separately, and a pointer to the cell is stored in the element" TR-248, 5.2, printed p. 9 (PDF p. 12) [ocr].
- Import interaction (Multi-PSI/V2): "If an imported pointer is copied, the MRB of both pointers, the original and its copy, are turned on so that the import table entry is not released when one of the pointers becomes garbage." TR-715, 5.4.5 footnote 2, printed p. 15 (PDF p. 16) [ocr].
- Tracing GC re-derives the MRB (Gap 7).

#### 3.4 MRB instructions (general FGHC abstract machine, TR-248 section 6, Tables 1-2, printed pp. 9-12 (PDF pp. 12-15); Fig. 5 [img], rest [ocr])
- Passive (guard) unification: `wait_value Xi,Aj`, `wait_reused_value Xi,Aj`, `wait_variable Xi,Aj`, `wait_constant C,Ai`, `wait_list Ai`, `read_value Xi`, `read_reused_value Xi`, `read_variable Xi`, `read_constant C`. In general unification "pointers to a structure in A_j or in a structure element used in the unification are pushed to the garbage stack if they are an SRP. Ones without the word reused also push such pointers in X_i; ones with the word will not."
- Garbage stack: garbage found in the guard is deferred; the stack "is emptied each time a goal reduction is initiated and each time a candidate clause fails or suspends. Its contents are reclaimed by an explicit instruction at the top of the body part." TR-248, 5.3 [ocr].
- `collect_stack`: "Reclaim storage area pointed from the garbage stack."
- `collect_list Ai`: "Reclaim the list structure pointed from A_i if A_i is an SRP. This instruction is generated when A_i is unified with a list structure in the passive part." (one cons cell, not recursive)
- `collect_value Ai`: "Reclaim storage area pointed from A_i if A_i is an SRP. ... generated when A_i is unified with a void variable in the passive part. When A_i references a structure, not only that structure but also its substructures referenced through an SRP are reclaimed recursively."
- `collect_vector`: not in TR-248 ("Extending them to treat general structures is straightforward"). Not named in the English core reports.
- Argument preparation: `put_variable`, `put_constant`, `put_marked_variable`, `put_list`, `put_value`, `put_marked_value`; `set_variable`, `set_constant`, `set_marked_variable`, `set_list`, `set_value`, `set_marked_value`; `write_variable`, `write_marked_variable`, `write_value`, `write_marked_value`, `write_constant`. "Instructions with the word 'marked' in their names have the same functions as those without it except that the MRB of the destination is always set. They are for reference duplication."
- Active unification: `get_value Xi,Aj` general; "During the unification, structures or variable cells known to have become inaccessible from the program are reclaimed."
- `reuse_list Ai,Aj`: "The same as 'put_list A_i' except that if the MRB of A_j is reset, use the list cell A_j points to in stead of allocating a new one." [img]
- `replace_cdr Ai,Aj,Ak`: "The same as the instruction sequence 'reuse_list A_i, A_j; write_value A_k', except that, if A_j can be reused, the car part is directly reused without rewriting." [img]
- Compilation examples (Fig. 5 [img]):
  - `p(X,X,Y,Y) :- true | q(X).` -> `wait_reused_value A1,A2; wait_value A3,A4; collect_stack; execute q/1`
  - `p([X|Y]) :- true | q(X,Y).` -> `wait_list A1; read_variable X3; read_variable A2; collect_list A1; put_value X3,A1; execute q/2`
  - `p(X) :- true | q([X]), r(X).` -> `enqueue_goal r/1; set_list G1; write_marked_value A1,G1; write_constant []; put_marked_value A1,A1; execute q/1` (as printed: the listing attaches `set_list G1 / write_marked_value` under `enqueue_goal r/1`; transcribed literally)
  - `p :- true | q(X), r(X), s(X).` -> `enqueue_goal s/1; set_marked_variable A1,G1; enqueue_goal r/1; set_marked_value A1,G1; put_marked_value A1,A1; execute q/1`
  - append before/after `replace_cdr` (Fig. 6, printed p. 13 (PDF p. 16) [ocr]): before: `wait_list A1; read_variable X4; read_variable X5; collect_list A1; put_list X6; write_value X4; write_variable X7; get_value X6,A3; put_value X5,A1; put_value X7,A3; execute append/3`; after: `wait_list A1; read_variable X4; read_variable X5; replace_cdr A1,X6,X4; write_variable X7; get_value X6,A3; put_value X5,A1; put_value X7,A3; execute append/3`.
- Multi-PSI/V2 naming for the same ideas: "structure frame reuse" (reuse the cons cell) and "structure element reuse" (reuse cons cell AND an unchanged element): TR-466, 3.1, printed p. 2 (PDF p. 3) [ocr]. `put_reused_structure`, `mark`, `set_vector_element`: these names do not occur in the English core reports.

#### 3.5 Destructive vector update
- "On updating an off-MRB array, destructive assignment can be performed. ... in the case of a single-referenced array, the original array can be reused as a new one by modifying the element destructively." TR-715, 4.4, printed p. 8 (PDF p. 9) [ocr].
- MRB-on case is NOT a full copy on Multi-PSI/V2: "As the mutable array scheme [3] was introduced to deal with the bad case in updating vector, the modification cost of one element is constant even if the vector's MRB is on. However ... the modification cost of a vector with MRB on is about 2.5 times as much as that of a vector with MRB off." TR-466, 4.1.1, printed p. 6 (PDF p. 7) [ocr]. ([3] = Eriksson & Rayner, "Incorporating mutable arrays into logic programming", ICLP 1984.) [INFERENCE] i.e. a multi-version (inverted-chain) array representation exists for multiply referenced vectors; its layout is not given.

#### 3.6 What is reclaimed, and how much
- "When a pointer with the MRB off is consumed - i.e. the referenced data is read and the pointer is no longer needed, or the pointer is simply discarded -, the memory area occupied by the data can be reclaimed" TR-466, 2 [ocr].
- Consumption points (general scheme): dereference with store-back, structure unification in the guard, unification with a void, elements of reclaimed structures: TR-248, 3.1, printed p. 4 (PDF p. 7) [ocr].
- "The memory cell for the collected object is chained to a free list for the reclamation." TR-469, 2, printed p. 3 (PDF p. 4) [ocr].
- Rates: "40 to 90 percent of garbage data is incrementally reclaimed" (TR-466, 2 [ocr]); "more than 60% of the garbage cells are collected" (TR-715, 4.4 [img]).
- Export side: when a `%release` zeroes an export entry, "the exported object cell itself may also be reclaimed when the export table entry is known to be the single reference to the cell by the MRB mechanism." TR-715, 5.4.3, printed p. 14 (PDF p. 15) [ocr].
- Early deadlock detection through MRB: "If an MRB-off pointer that points to an unbound variable with suspended goals hooked on it is found to be discarded at the commitment of a clause, the suspended goals are known to become perpetually suspended." TR-715, 6.2, printed pp. 17-18 (PDF pp. 18-19) [ocr].
- Free-list organisation: Gap 7.

#### 3.7 From the peripheral and Japanese reports
TR-498 (Aug 1989) and TR-321 (Nov 1987) describe MRB on the C emulators (PDSS), motivated by PIM; neither says which instruction set the Multi-PSI/V2 microcode implements.
- Bit location: "MRBのフィールドを各KL1データセルに設けなければならない。これにはタグフィールドの1ビットを充てることとした" = one bit of the tag field (TR-321, 3.1, printed pp. 4-5 [img]). "一語はMRBを含めたタグ部1バイト,データ部4バイトから構成される" = word is a 1-byte tag part including the MRB plus 4 data bytes (TR-498, 6.2 fn. 7, printed p. 20 (PDF p. 21) [img]; stated for PDSS). TR-483, 2.7.1: "kept in pointers using one bit tag" [img]. Which bit, and its numeric polarity: **not found in any report**.
- "定数の場合は,定数自体もMRBを持ち,未定義変数はMRBを持たない" = a constant carries an MRB itself; an unbound variable cell has none (TR-498, 3.2, printed p. 7 [img]).
- Dereference: result MRB = logical OR of the MRBs of the indirect pointers on the chain (TR-498, 3.3, printed p. 10 [img]); an indirect cell in state I1 is reclaimed during dereference.
- Instantiation table (TR-498 Table 1 = TR-321 Table 1, printed p. 11 (PDF p. 12) [img]); entries give the state of the instantiated cell; * = structure-structure, element-wise:

| X \ Y | S1 | S2 | U1 | U2 white | U2 black | U3 |
|---|---|---|---|---|---|---|
| S1 | * | * | I1 | I1 | I3 | I4 |
| S2 | * | * | I3 | I4 | I3 | I4 |
| U1 | I1 | I3 | I1 | I2 | I3 | I2 |
| U2 white | I1 | I4 | I2 | I2 | I4 | I4 |
| U2 black | I3 | I3 | I3 | I4 | I3 | I3 |
| U3 | I4 | I4 | I2 | I4 | I3 | I4 |

- 1989 instruction set (TR-498 Table 2 and 5.3, printed pp. 15-17 (PDF pp. 16-18) [img]): `put_marked_value Xi,Aj`; `set_marked_value Xi,Gj`; `write_marked_car_value L,Xi`; `write_marked_cdr_value L,Xi`; `write_marked_element_value V,I,Xi`; `put_marked_variable Xi,Aj`; `set_marked_variable Xi,Gj`; `write_marked_car_variable L,Xi`; `write_marked_cdr_variable L,Xi`; `write_marked_element_variable V,I,Xi`; `mark_element V,I`. The value forms copy the datum and "両者のMRBを黒くする" (blacken both copies); the variable forms allocate a new unbound cell and point both places at it with black MRB; `mark_element` blackens element I of V (needed for `vector_element(V,I,E)` in a guard).
- `collect_list Ai`: if white, put the cons cell on the free list. `collect_vector Ai,Nv`: same for a vector, length Nv is an operand. `collect_value Ai`: "MRBが白である限り再帰的に回収し,各々の長さに応じたフリーリストに繋ぐ" (recursively while white, each onto the free list for its length).
- `put_reused_list Ai,Aj`: if Ai's cell is white move the pointer to Aj with white MRB (bypassing the free list), else allocate; `put_reused_vector Ai,Aj,Nv` likewise. (= `reuse_list` of TR-248.) No `put_reused_structure` under that name.
- `set_vector_element(Vold,I,C,Vnew)`: "VoldのMRBが白ならば, Voldを再利用し" (white: update in place); black: allocate and copy (TR-498, 4.4, printed p. 13 [img]). Five-argument KL1-level form `set_vector_element(OldV, N, OldE, NewE, NewV)` in TR-483, 2.7.1 [ocr].
- TR-498 compile example (Fig. 7 [img], as printed) for `p([X|Y], X, Z) :- true | Z = [X|ZZ], q(X, ZZ).`: `wait_list A1; read_car A1,X3; read_cdr A1,X4; wait_value X3,A2; collect_value A2; collect_value X4; put_reused_list A1,X5; write_marked_car_value A1,X3; write_cdr_variable A1,A2; get_list_value X5,A3; put_value X3,A1; execute q/1`.
- 1987 instruction set (TR-321, 3.2 [img]): `wait_reused_value`, `read_reused_value`, `mark Xi`, `set_marked_variable`, `put_marked_variable`, `write_marked_variable`, `collect_list`, `collect_value`, `collect_stack` + garbage stack. The 1989 set drops `mark`, `collect_stack` and the garbage stack and adds explicit `read_car`/`read_cdr`, `collect_vector`, `put_reused_*`.
- Reclamation timing: "概念的には,コミットメントオペレータの位置に" (conceptually at the commit operator) (TR-498, 4.5).
- Measured overhead (PDSS): MRB code 1.05x static / 1.07x executed instructions (TR-498 Table 4); heap use ratio 0.11-1.17 (Table 5).

---

### Gap 4. Data layouts

- Word: 40 bits = 8-bit tag + 32-bit data (TR-715, 3.1; TR-531, 2.1.1; TR-585, 2.1 [img]).
- Cell kinds named in the reports (tag names, no numeric tag values): `ATOM`, `VECT`, `REF`, `UNDEF`, `EXREF`, `EXVAL` (TR-390, 4, printed p. 5 (PDF p. 8) [ocr]); `EUNDEF` (exported unbound, distinct tag; TR-390 App. A [img]); `LIST`, `VAR` (TR-466 Fig. 3 [img]); `STRUCT`/`STR`, `UNDF` (TR-469 Figs. 5-6 [img]); hook variable, multiple hook variable (TR-390 footnote 2); MHV, MR (TR-466); EX cell with white/black mark (TR-715 Fig. 7 [img]).
- Vector (TR-390's model, stated as an assumption "without loss of generality", not as the exact Multi-PSI layout): "VECT (vector of terms represented by a cell whose tag is VECT and whose value field consists of a subfield containing the length (n) of the vector and another subfield pointing to a consecutive sequence of n cells)" TR-390, 4, printed p. 5 (PDF p. 8) [ocr]. [INFERENCE] length-in-pointer, no header word in the body.
- List: two-word cons cell (CAR, CDR) pointed to by a `LIST`-tagged word (TR-466 Fig. 3 [img]). Variables are never inline in a cons cell (TR-248, 5.2).
- Unbound variable: a separate one-word cell (`UNDEF`/`UNDF`/`VAR`); binding overwrites it with a value or a `REF`.
- Strings: named as a structured type ("structured data such as vector or string", TR-715, 5.2.1 [ocr]); layout **not found**.
- Floats: **not found in these reports**.
- Atoms: one-word atomic cell, "encoded directly" in messages (TR-715, 5.2.1); atom table / name representation **not found**.
- Code module (TR-715, 5.4.8, printed pp. 16-17 (PDF pp. 17-18) [img for p. 16]):
  - "A module is the unit of compilation and is also used as the unit of code distribution to PEs."
  - "The predicate calls within a module are represented by relative pointers. ... Only the inter-module predicate calls use absolute address pointers which require address maintenance in data transfer."
  - "Absolute address pointers in a module are gathered at the top region in the module to reduce the size of sweeping for maintenance in local GC. The rest (and the greater part) of the module contains only atomic data, that is, KL1-B instructions (with the relative address operand if any) followed by their full word constant operands if any."
  - A code address on the wire is "a tuple of <module, offset, structure ID>, where module is an external reference to the code module in the exporting PE, and offset is the code location in the module." On arrival: "structure ID is used to check whether the same module exists or not. If it does, the code address is calculated with offset. If it does not, a %read message is sent to the exporting PE." (printed p. 17 [ocr]).
  - Modules live in the heap and are moved by GC ("when the module is moved in a local GC"); "Initially, the Code data are storaged in the processor whose number is zero." TR-469, 5, printed p. 12 (PDF p. 13) [ocr].
- Structure IDs (TR-715, 5.4.7 and Fig. 9, printed pp. 15-16 (PDF pp. 16-17) [img]):
  - "It is a global ID attached to an instantiated structure." Used only for code: "Currently, we manage the structure ID for only program code objects." TR-439, 4.2, printed p. 9 (PDF p. 10) [ocr]; "The global structure management mechanism is used for the program code" TR-715 [img].
  - Structure entry record, 4 words as drawn in Fig. 9: `col.link` (*1 hashed-ID collision link), `col.link` (*2 hashed-address collision link), `strct.ID`, `strct.adr` (-> the structure). Two hash tables index the same records: "Structure ID hash table" by hash(ID) and "Structure address hash table" by hash(adr). [img]
  - ID format and how IDs are generated: **not found**. Garbage IDs are never collected: "needs a kind of global GC scheme, and is not implemented yet."

#### 4.x From the peripheral and Japanese reports
- Functors are vectors: "Usual functor structures such as \"f(X)\" are also represented using the vector structures such as \"{f, X}\"" TR-483, fn. 14 (PDF p. 17) [img].
- Module object: "A module data structure consists of two parts: GC part where pointers to other data are stored and non-GC part where only atomic data, mainly executable KL1-B code, are stored. All accesses to data outside of a module is made via pointers stored in the GC part." TR-483, 2.6.1, printed pp. 13-14 (PDF pp. 16-17) [ocr/img]. Types `module` and `code` (a public predicate entry). The GC part may hold unbound variables (a call into a not-yet-loaded module suspends). Matches TR-715's "absolute pointers gathered at the top region".
- Atoms: "In the KL1 language level, atoms do not have any association with their name strings"; names are kept by a PIMOS atom-name database process. TR-483, 4-4.1, printed p. 19 (PDF p. 22) [ocr]. So the microcode needs no atom table.
- Strings: "updatable character strings" (TR-483, 3.5 [ocr]); structures = list, vector, string (TR-498 fn. 4). Type names seen in figures: REF, UNDF/UNDEF, LIST, VECT, INT, ATOM, HOOK, GOAL.
- Cons cell = 2 words, variable = 1 word (TR-498 fn. 1; TR-321 Table 3 arithmetic `LIST*2 + VARIABLE`) [img].
- Unbound variable in a vector slot is a separate UNDEF cell reached by a white REF (TR-498 Fig. 6 [img]).
- Tag table, numeric tag values, float format, string layout: **not found in any of the 18 reports**.

---

### Gap 5. Shoen, foster parents, WTC

#### 5.1 From the Multi-PSI implementation papers
- Shoen creation: `execute/6` in TR-715 (1991) [img]: `execute(Goal, ControlStream, ReportStream, MinPrio, MaxPrio, Mask)`; `execute/7` in TR-390 (1988) [ocr]: `execute(Min,Max,Mask,Code,Argv,Control,Report)`.
- Mask: "Mask is a bit-map to specify which exceptions should be reported." (TR-715 [img]); "reported to the report stream if the logical AND of the 32 bit exception tag and the 32 bit exception mask of the shoen is not zero" - otherwise delegated outward (TR-390, 2, printed p. 3 (PDF p. 6) [ocr]).
- "there is no failure in a shoen. Any kind of failure is treated as an exception." and "the monitoring process is to substitute a new goal for the goal that has given rise to the exception." TR-390, 2 [ocr].
- Resource: "Currently, resource is measured by the number of reductions." TR-715, 2.2(2), printed p. 3 (PDF p. 4) [ocr]. Upper limit set by a control message; "Resource shortage is notified on the report stream, and additional amount of resource can be selectively given."
- "A child shoen is treated as one of the goals in the parent shoen." TR-715, 5.3.1 [img].
- Foster parent: one per (shoen, PE) pair on every PE other than the shoen's that holds goals of the shoen. Fields: "The foster parents have the shoen status (running, stopped or aborted), the child count (the number of child goals created on the PE), and the cached resource information of the shoen." TR-715, 5.3.2, printed p. 10 (PDF p. 11) [img]. (TR-439 has "running, stopped, aborted, etc." [ocr].) Plus a WTC value (5.3.3).
- Registers: the shoen resource (reduction budget) of the current goal's shoen is "cached on the registers as long as the execution context remains unchanged" TR-715, 4.2 [ocr].
- Termination: a foster parent whose child count reaches zero sends `%terminated(Shoen)` carrying all its WTC. Invariant: WTC_shoen = sum(WTC_fosterparent) + sum(WTC_message), where messages are "%throw_goal, %unify or %terminated message in transit". "%throw_goal and %unify messages are always attached with some amount of WTC, and the foster parents accumulate their WTCs when receiving the messages. Foster parents can split it when they throw child goals or issue %unify messages." TR-715, 5.3.3, printed pp. 11-12 (PDF pp. 12-13) [ocr]. (TR-439, 1988, says split only "when they throw child goals" [ocr].)
- Trace/spy exceptions and the Shoen Profiler ("counts the number of reductions of each predicates in the shoen", controlled via the control stream): TR-715, 6.1 and 6.3 [ocr].
- Shoen record field list/sizes: **not found in the English core reports**.

#### 5.2 From the peripheral and Japanese reports (WTC algorithm, PIMOS level)
Shoen interface (KL1/PIMOS level; TR-483 June 1989 unless noted; [img] by the sub-reader):
- Control stream messages: `start` ("After its creation, the execution of the shoen is suspended until this message is first received"), `stop`, `abort`, `add_resource(Amount)`, `statistics`. Report stream: `started`, `stopped`, `aborted`, `terminated`, `exception(Info, Goal, NewGoal)`, `resource_low`, `resource_added`, `statistics_started`, `statistics(Status)`. TR-483, 2.2.2-2.2.3, 2.3.2, 2.5.4, printed pp. 5-13 (PDF pp. 8-16).
- Goal / NewGoal are each a code pointer + argument vector (TR-483 fn. 2, 7, 8; TR-530, 2.2). The failed goal "is replaced by a new goal. That goal waits for the instantiation of NewGoal ... and, after its instantiation, executes it" - it stays in the shoen, so the shoen cannot terminate meanwhile.
- Tag match: "Two tags match when their bit-wise conjunction yields non-zero"; reported "to the innermost shoen whose tag matches" (2.3.2). Tag = "one word bit pattern".
- `raise(Info, Data, Tag)` in TR-483 (1989) vs `raise(Tag, Data, Info)` in TR-764 (PIMOS 3.2, 1992); report `exception(Kind, EventInfo, ^NewCode, ^NewArgV)` in TR-764. Creation in TR-764: `execute(Code, Argv, MinPrio, MaxPrio, ExcepMask, Control, ^Report)` (1.1, printed p. 2 (PDF p. 3) [img]) - same seven arguments as TR-390's 1988 form in a different order; TR-715's execute/6 folds Code+Argv into Goal. TR-373 (1988) shows `execute(Goal, Control, Report, Tag)`.
- Resource: "In stead of measuring the CPU time, the current implementation counts the number of reductions as its estimate. The current implementation does not count the memory consumption." TR-483, 2.5.1 [img]. Protocol: the shoen "only reports the resource_low status to the meta-level when the allowed amount of resource has almost been consumed up. If the resource consumption actually reaches the limit, then the execution is suspended until the limit is raised" [ocr]. Thresholds, grant sizes, and how the budget is divided among foster parents: **not found**.
- Shoen record (design level): holds "その荘園の現在の実行状態を表すフラグ" (a flag for the current execution state), checked whenever a goal is scheduled (run / suspend / abandon); the foster parent is "荘園レコードのキャッシュ" (a cache of the shoen record) on each PE; goals point to their foster parent, foster parents point to the shoen by external reference; goal and child-shoen counts are kept per foster parent. TR-373, 3.4 and Fig. 5, printed pp. 18-20, 42 [img].
- Perpetual suspension is reported per maximal goal as `exception(Info,Goal,NewGoal)` to the goal's shoen (TR-530, 2.2).

WTC (TR-341, Feb 1988; an algorithm paper written before the Multi-PSI/V2 implementation: "The algorithm will be applied to parallel implementation of KL1 ... on the Multi-PSI"; vocabulary: process pool / controlling process / subpool = shoen / shoen record / foster parent [INFERENCE]):
- Invariant: "The weight of a process in transit and that of a subpool are positive integers, while the weight of the controlling process is a negative integer" and "The sum of the weights is zero." (5.1, printed p. 3 (PDF p. 4) [ocr]). TR-373 states the same sign convention for shoen/foster parent/messages.
- Messages (italic words in the paper, no `%`): thrown process (weighted); `ready` (PE -> controller when a subpool is created; unweighted under FIFO; controller memorises the PE); `terminated` (weighted); `abort` (weighted); `return` (weighted; reply to abort/supply when no subpool exists); `request`; `supply` (weighted). (5.2-5.3, printed pp. 4-7 [img].)
- Abort: "(1) Sending an abort message to each PE memorized; (2) Sending an abort message to the sender PE of a ready message received after operation (1)"; PE: "(3a) Forcing the subpool with the specified PID to terminate, and sending back a terminated message which carries the sum of the weight of the terminated subpool and the abort message; (3b) If there is no subpool ... sending back a return message".
- Exhaustion: at subpool weight one, throwing is suspended and `request` is sent; controller replies `supply`.
- Weights: "Assign a fixed weight (say 2^10) to a thrown process if the weight of the subpool is more than twice of that; otherwise assign half of the weight of the subpool." "A supply message carries a very large weight (say 2^20)." (5.4, printed p. 7 (PDF p. 8) [img at 300 dpi]). These are "say" examples, not attested Multi-PSI constants. Initial weight: not stated.
- Non-FIFO variant: weighted `ready` and `request`, per-PE counters at the controller (section 6).
- "no more than one subpool can exist in one PE at a time" per PID (section 6 [img]).

State change (TR-737, Feb 1992; fn. 1 attests only that WTC "has been employed" on Multi-PSI, not this protocol):
- For stop / restart / priority change / abort. Controller keeps a "changed weight" (initialised to its own negative weight) and an "ack counter" (= number of PEs), increments a generation ("three generation numbers are enough ... 0 -> 1 -> 2 -> 0") and broadcasts `change(PID, new state, generation)`. Each PE always answers `ackChange`; if it has a subpool in the old state it changes it and sends `changed` with a copy of the subpool weight; if none it memorises PID+state ("empty subpool"). A thrown process carries weight, generation and state; a PE reconciles a mismatched arrival by generation and sends `changed`.
- Two kinds of `terminated`: with the old generation the weight is added "to both its weight and the changed weight"; with the same generation "to only its weight". Complete when changed weight and ack counter are both zero. After termination the controller broadcasts `forget`; PEs answer `ackForget`. (5.2-5.3, printed pp. 4-6 (PDF pp. 5-7) [img].)
- Variant 5.4: a weighted `change` makes `ackChange` unnecessary. Which variant was implemented: not stated.

EARLY-PIM (TR-250): "metacall record" (pre-shoen) = Status; Link to brother; Link to parent; Counter of children goals; Pointer to a result variable (Table 1 [img]).

---

### Gap 6. Inter-PE

#### 6.1 Packet format (TR-715, Fig. 2, printed p. 5 (PDF p. 6) [img])
- The channel carries 9-bit units (bits 8..0). Bit 8 = 1 marks header and tail, 0 marks body bytes.
  - Header: bit 8 = 1, bit 7 = 0, bits 6..0 = "Destination PE Number".
  - 2nd unit: bit 8 = 0, bits 7..0 = "Message Order" (the message type code).
  - Body: bit 8 = 0, 8 data bits each; "variable length (depending on Message Order)".
  - Tail: bit 8 = 1, bit 7 = 1, bits 6..0 = "(Source PE Number)".
  - "Only [bold-boxed] part is examined by the Network Controller" [img at 220 dpi]: the bold box visibly encloses bit 7 of the tail and the header row (flag bits and Destination PE Number); the exact extent of the box on the bit-8 column is [INFERENCE]. The Message Order and Source PE Number are not boxed. [INFERENCE] 7-bit PE number is enough for 64 PEs; the same format cannot address PIM/m's 256 PEs unchanged.
- "Each channel consists of 11 bits, 9 bits for data, one for a parity and one for a busy acknowledge signal of the opposite direction." 5 Mbytes/s, 200 ns cycle; 48-byte Output Buffer per output channel; 4-Kbyte Write Buffer and Read Buffer for the PE port. TR-715, 3.2, printed p. 4 (PDF p. 5) [img for 48-byte, 4-Kbyte, 5 Mbytes/s; 11/9 bits ocr]. TR-585, 2.1 [img] says "two 8-bit channels of opposite directions" per mesh edge (8 data bits + the header/tail flag bit = the 9 of TR-715 [INFERENCE]).
- Routing: wormhole, "prioritized coordinate ordering" (x first, then y), via a software-defined "path table". Channel between two PEs is FIFO: TR-390, 3.1, printed p. 5 (PDF p. 8) [ocr] - the WEC zero-access trick depends on it.
- Microcode layer: "arranging a 32-bit data in the PE to/from four byte serial data in the Write/Read Buffer" (TR-715, 3.3 [img]); tagged words are cut into bytes ("putting a byte-serial message in the Write Buffer cutting from tagged words", TR-715, 7.1 [ocr]). The wire encoding is variable-length by data type (TR-563: the "KL1 Encoder/decoder" encodes each argument in "variable-length bytes" according to its type); per-type sizes are not given, and the measured lengths (14, 24, 65 bytes) do not fit a fixed 5-bytes-per-word scheme.
- Receive path: interrupt when the tail is in the Read Buffer; microroutine "moves the complete message to a large memory area, called the Read Packet Buffer"; "The messages in the Read Packet Buffer are decoded at a slit of reductions." Send path blocks: "if the routine cannot find enough room to store the whole message in the Write Buffer, it will wait" (TR-715, 3.3 [img]). The copy is skipped when the Read Buffer has room (TR-715, 7.1 footnote 4 [ocr]).

#### 6.2 Message types
Complete list is not given anywhere in the English core reports ("Typical Inter-PE Messages", "(part)"). What is named:

| Message | Arguments | Source |
|---|---|---|
| `%throw_goal(PE,Code,Args,Priority,etc.)` (also written `%throw`) | "Move the goal to specified PE"; Code = <module EXREF, offset, structure ID>; atoms inline, structures and unbound variables as external pointers (level-0); carries WTC and the shoen | TR-715 Table 1 [img]; 5.2.1; 5.3.3; TR-390 3.2 |
| `%read(Ext,Return)` | "Request to reply the value of an external pointer"; Return = a (simpler, single-use) external reference to the requesting cell | TR-715 Table 1 [img]; TR-390 4.4 writes `%read(access(X),ReturnAddress)` |
| `%answer_value(Val,Return)` | "Respond to a %read message"; Val encoded 1 level deep; or only a structure ID if the datum has one | TR-715 Table 1 [img]; TR-390 writes `%answer_value(ReturnAddress, value(V))` (argument order differs) |
| `%unify(Ext,Val)` | "Request to unify with an external pointer and an argument"; carries WTC | TR-715 Table 1 [img]; TR-390 `%unify(access(X),pass(Y))` |
| `%terminated(Shoen)` | "Report a local shoen termination in a PE"; carries the foster parent's WTC | TR-715 Table 1 [img] |
| `%release(WEC)` | "Return WEC value of an external pointer" | TR-715 Table 1 [img] |
| `%request_WEC`, `%supply_WEC` | WEC supply protocol when an import entry's WEC is 1 and must be split (alternative to indirect export) | TR-390, 5.3, printed p. 14 (PDF p. 17) [ocr] - described as one of "two ways"; the paper prefers indirect exportation + zero access on a FIFO network, so these may not exist in the Multi-PSI/V2 microcode [INFERENCE] |
| "etc." | 7.3 % of messages on 64-PE Pentomino, 2.9 % on Bestpath are neither read/answer_value/release/unify/throw | TR-531 Table 2 [img] |

- Predecessor names on Multi-PSI/V1: "%read and %answer_value messages correspond to the %read_value and %return_value messages in [Ichiyoshi87]" TR-390 footnote 4 [ocr].
- Measured lengths and costs (TR-715 Fig. 10 = TR-531 Fig. 3, printed p. 19 (PDF p. 20) [img]; steps x 200 ns, excluding cache misses):

| Operation | Bytes | Steps | Time |
|---|---|---|---|
| Send `%throw_goal` of p(atom,EXREF,EXREF) | 65 | 419 | 85 us |
| Receive same (incl. Copy_to_RPKB, store to goal stack; code already present) | 65 | 637 | 130 us |
| Send `%read`(EXREF) | 14 | 117 | 25 us |
| Receive `%read` | 14 | 175 | 35 us |
| Send `%answer_value`([atom\|EXREF]) | 24 | 208 | 42 us |
| Receive `%answer_value` | 24 | 397 | 80 us |

  `%unify` costs "almost same as those of %answer_value". In append-LI (TR-585 Fig. 2 [img]): %throw 10.7 send / 16.3 receive / 1.67 network; %read 3.0 / 4.5 / 0.36; %answer_value 5.3 / 10.2 / 0.62.
- Average message length 20-21 bytes (Pentomino), 27 bytes (Bestpath); frequency mix in TR-531 Table 2, printed p. 14 (PDF p. 15) [img]: Pentomino 64 PEs: read 30,736 (32.4 %), answer_value 30,581 (32.3 %), release 13,641 (14.4 %), unify 11,129 (11.7 %), throw 1,768 (1.9 %), etc. 6,895 (7.3 %), total 94,750.
- Per-field byte layout of any message body: **not found in the English core reports**.

#### 6.3 External reference ID, export/import tables
- ID = <pe, entry>: "pe is a PE number and entry is the entry position of the export table. The global ID is called the external ID." TR-715, 5.4.2, printed pp. 12-13 [img p. 13]. Bit widths of the two fields: not given.
- Export and import table entries "are never moved in local garbage collection" TR-466, 3.2, printed p. 2 (PDF p. 3) [ocr]; the export entry's pointer to the data is updated by GC.
- All local references to one external object go through one EX cell: "The external reference cell and the import table entry point to each other." TR-390, 4.1, printed p. 6 (PDF p. 9) [ocr]. They are separate because on `%answer_value` "the EX cell identified by ReturnAddress is overwritten by the value, and the import table entry corresponding to the EX cell can be freed." TR-390, 4.4, printed p. 10 (PDF p. 13) [ocr].
- Entry layouts, TR-715 Fig. 7, printed p. 13 (PDF p. 14) [img], fields top to bottom:
  - **Black import table entry** (5 words): `ext. ID` | `WEC` | `imp. cnt` | pointer back to the EX cell | `col.link` (import-hash collision chain; the import hash table points at the entry). The EX cell (black mark) points to the entry.
  - **Black export table entry** (4 words): pointer to exported data | `WEC_up` | `WEC_low` | `col.link` (export-hash collision chain).
  - **White import table entry** (1 word): `ext. ID`. EX cell (white mark) points to it; no back pointer, no WEC, no count, no hash link.
  - **White export table entry** (1 word): pointer to exported data.
- WEC widths: "The WEC of an export table entry is represented by a 64 bit unsigned integer, while the WEC of any external reference (import table entry and encoded reference) is represented by a 32 bit unsigned integer." TR-390, 7, printed p. 19 (PDF p. 22) [img] - matches `WEC_up`/`WEC_low` = two 32-bit halves [INFERENCE].
- Import count: "The number of imports, the import count, is also counted." TR-715, 5.4.3 [ocr]; a `%release` is sent when "the import count reaches zero by incremental GC by using the MRB mechanism". [INFERENCE] `imp. cnt` counts local MRB-tracked references/import events to the EX cell, so the MRB collector can free the black entry.
- Two EX cell types: "An external reference cell is either an EXREF cell or an EXVAL cell. The data referenced by an EXVAL cell is known to have a concrete value." TR-390, 4.1, printed p. 7 (PDF p. 10) [ocr].
- Import-entry flags (TR-390, 1988): a **zero flag** ("The import table entry has a zero flag for this purpose. When the zero flag is ON, the external reference must not be transferred but must be indirectly exported.", 5.3, printed pp. 14-15 [ocr]) and an **unsafeness flag** (6.1). Not drawn in TR-715 Fig. 7.

#### 6.4 WEC values and operations (TR-390)
- `WEC_UNIT (= 2^24)`. "The WEC to assign in encoding by location is always WEC_UNIT. At reference duplication, the WEC of the import table is divided in half. It follows that an external reference which is encoded by location can be duplicated at least 24 times until the WEC becomes 1." TR-390, 7, printed p. 19 (PDF p. 22) [img].
- Import overflow: "When the WEC of an import table entry overflows, WEC_UNIT (= 2^24) is left and the excess is returned to the export table entry by a %release message." [img]
- Access encoding: "The WEC to assign in encoding to access is 1 when the WEC of the export table entry is greater than 1, and 0 otherwise (zero encoding)." TR-390, 7 [ocr] ("export table entry" as printed; the context of 5.3 is the import entry's WEC [INFERENCE: probable slip in the paper]).
- Export, by location: add w to the export entry's WEC (initialise to w if new), attach w. Export, by reference (re-export of an EX cell): subtract w from the import entry's WEC, attach w. Import, non-self: add w to the import entry (initialise if new). Import, self (pointer comes home): subtract w from the export entry; free it at zero. TR-390, 5.2, printed pp. 12-13 (PDF pp. 15-16) [ocr].
- Transitions: duplication (split), discard (`%release` with all WEC; EX cell + import entry freed), transfer (last internal reference exported: all WEC travels with the message, entry freed; "can be detected if the implementation supports the MRB mechanism").
- Exhaustion (WEC = 1): either `%request_WEC`/`%supply_WEC`, or **indirect exportation** (export the EX cell itself by location through this PE's export table, lengthening the chain); for access use **zero encoding** (WEC 0, legal only on a FIFO network), and set the zero flag.
- `%release` triggers (TR-715, 5.4.3 [ocr]): (1) value returned by `%answer_value`; (2) import count reaches zero through MRB; (3) entry found unmarked after a local GC.
- White entries = "an import table for the pointers whose WEC and import count equals one, and its entries are released immediately when the imported pointers are collected by the MRB GC. Their white export entries are also released only when the %release message is received." TR-715, 5.4.5, printed p. 15 (PDF p. 16) [ocr]. No hash tables for white. Chosen by the MRB of the exported pointer: MRB-off variable -> white; MRB-on -> black; atom -> inline (TR-466, 4.3.1, printed pp. 7-8 [ocr]).
- White vs black cost: black export about 3x white per argument above the constant throw overhead; one cons-cell transfer by read/answer_value: 240 us white, 300 us black (TR-466 Table 2, printed p. 9 (PDF p. 10) [img]); goal throw is roughly 330 us at arity 1 rising to about 600 (atomic) / 700 (MRB-off) / 930 (MRB-on) us at arity 16 (read off TR-466 Fig. 7 [img], approximate).

#### 6.5 Re-export, hash tables
- "The export hash table associates the exported object addresses with their external IDs, and the import hash table associates the imported external IDs and the import table entry." TR-715, 5.4.4, printed p. 14 (PDF p. 15) [ocr]. Purpose: a second export of the same cell reuses the entry, so only one `%read` is ever sent and only one copy is fetched.

#### 6.6 Copy levels and distributed unification
- "the 0-level copying is done for the arguments of thrown goals and the 1-level copying for those of unifications (for the Val of %answer_value and %unify)". TR-715, 5.4.1, printed p. 12 (PDF p. 13) [ocr]. Lists: "only one cons cell is transferred at one time and the CDR of the cons cell is represented by an external reference if it is pointed to another cons cell" TR-466, 4.3.2 [ocr].
- `%read` on an EX cell at the exporter is forwarded: "If it is an EX cell, a %read message is passed to the PE it references." TR-390, 4.4 [ocr].
- Safe/unsafe: "An external reference E is unsafe, iff (1) processor(from(E)) < processor(to(E)), or (2) to(E) is an unsafe external reference." Implemented with an unsafeness flag: set on encode-by-location if the term is an unsafe EX cell; inherited on encode-by-reference. "The binding order rule: An exported unbound variable cannot be bound to an unsafe EXREF cell." TR-390, 6.1, printed pp. 16-17 (PDF pp. 19-20) [ocr]. TR-715's summary: "The binding order is determined with the two exporting PE numbers." (5.2.3).
- Unification table (TR-390 App. A, printed p. 23 (PDF p. 26) [img]); rows = X, columns = Y; `%u(X,Y)` = send `%unify(access(X),pass(Y))` to the PE X references:

| X \ Y | UNDEF | EUNDEF | sEXREF | uEXREF | EXVAL | concrete |
|---|---|---|---|---|---|---|
| UNDEF | X := ref(Y) | X := ref(Y) | X := Y | X := Y | X := Y | X := Y |
| EUNDEF | Y := ref(X) | X := ref(Y) | X := Y | %u(Y,X) | X := Y | X := Y |
| sEXREF | Y := X | Y := X | %u(X,Y) | %u(X,Y) | %u(X,Y) | %u(X,Y) |
| uEXREF | Y := X | %u(X,Y) | %u(X,Y) | %u(X,Y) | %u(X,Y) | %u(X,Y) |
| EXVAL | Y := X | Y := X | %u(X,Y) | %u(X,Y) | %u(X,Y) | %u(X,Y) |
| concrete | Y := X | Y := X | %u(Y,X) | %u(Y,X) | %u(Y,X) | X=Y |

#### 6.7 Global structure management: see Gap 4 (structure IDs). `%read` of a structure with an ID returns "only the ID"; the reader looks it up in its structure ID hash table and, if absent, "a %read message is sent again to copy it" (TR-715, 5.4.7 [ocr]).

#### 6.8 From the peripheral and Japanese reports
- TR-563 (Japanese counterpart of TR-531, May 1990, authors Nakajima, Inamura, Ichiyoshi) [img]: Table 1 prints the five messages as `throw_goal`, `read`, `answer_value`, `unify`, `release`; Fig. 3 gives the same step counts as TR-715 Fig. 10 (419/637, 117/175, 208/397) - the same figures from the same measurement, in the Japanese write-up. Two microcode layers named "Basic message handler" (header/tail, 32-bit <-> byte serial; KL1-independent) and "KL1 Encoder/decoder" ("variable-length bytes" per argument data type, code address, export/import table registration). Node pass-through delay 5 cycles. Calendar clock precision 1/16 ms. Sender busy-waits when the Write Buffer is full while still draining arrivals into the Read Packet Buffer. [INFERENCE by the sub-reader] in Bestpath `release` count = `throw` count at every size.
- TR-373 (1988 design) [img]: exref = PE number + offset into the export table (輸出表); no import table mentioned; a large structure reply first sends only a pointer; loop-avoidance rule stated as smaller PE number -> larger (the pre-TR-390 direction).
- The front-end processor speaks the same inter-PE protocol: "the front-end and the host communicate to each other using the same protocols used in the communication between two processors of the host" TR-483, 3.3, printed pp. 17-18 [img].
- TR-341/737 messages (ready, abort, return, request, supply, change, changed, ackChange, forget, ackForget) are candidates for the unnamed "etc." class of TR-531 Table 2 [INFERENCE]; no report gives the `%` names or codes of the shoen-control messages.
- Message order codes, per-field byte formats, external-ID bit split: **not found in any of the 18 reports**.

---

### Gap 7. Memory management and GC

- Heap-based, no stacks. Allocation normally from size-classed free lists refilled from the heap top: "When records in a free list are exhausted, a pre-determined number of new records are created on the heap top and linked to the free list." TR-715, 4.4, printed p. 8 (PDF p. 9) [img]. The batch size is not given.
- Size classes: "In the current implementation, the sizes are from 1 to 8, 16, 32, 64, 128 and 256. A record over 256 words is allocated on the heap top." TR-715 footnote 1, printed p. 8 (PDF p. 9) [img]; same in TR-439 footnote [ocr]. = 13 free lists: 1, 2, 3, 4, 5, 6, 7, 8, 16, 32, 64, 128, 256 words [INFERENCE on the count].
- No coalescing: "fragmentation among the free lists is resolved only by local (non-incremental) GC, because, free list handling operation is too frequent to employ fragment reconstruction techniques such as the buddy system" [img].
- Semispaces: "data cells are allocated to a half of the heap area, the active heap, until it is used up and the tracing garbage collector are invoked. The tracing garbage collector only traces active data from marking roots, and copies them to another half" TR-469, 3.2, printed pp. 5-6 (PDF pp. 6-7) [ocr]. Measured configuration: "4 processors with 12 Mword of heap memory. (Physical memory = 16 Mword)" (printed p. 16 [ocr]); Table 1 "Heap [Mword]" column 6.13 (1), 3.07 (1/2), 4.60 (3/4) [img]; that 6.13 is one semispace of the 12 Mword heap is [INFERENCE].
- Trigger: "When a new data is created and the corresponding free list is empty, the list is extended by consuming the heap area. If the size of the extended list is too small because of the short of the available heap area, the garbage collector is invoked." TR-469, 4, printed pp. 10-12 (PDF pp. 11-13) [ocr]. The request is honoured at the slit check (Gap 1). The user can also invoke GC (TR-715, 6.2).
- Roots: "the roots of the marking are the arguments of the goals in the goal stack" and "Each entry of the export table ... is one of the root of the marking." TR-469, 4 [ocr]. TR-715: "moves all data cells reachable from the prioritized goal stacks and the export tables to a new semi-space. After copying, valid entries in the import tables are swept. If unmarked entries are found, %release messages are sent" (5.4.6, printed p. 15 [ocr]). [INFERENCE] suspended goals are not roots: they are reached only through the variables they hook on, which is what makes perpetual-suspension detection possible (TR-715, 6.2: "the suspended goals which are not reachable from active goals are perpetually suspended. These goals are copied to the new semi-space and examined further").
- Algorithm specifics (TR-469, 3.3, printed pp. 6-10 (PDF pp. 7-12)):
  - Dereferences while copying, eliminating REF chains: "Almost of reference pointer cells can be collected by dereference of tracing garbage collection." Pointers to atomic cells are replaced by the atom itself. [ocr]
  - Recomputes MRB: first visit copies object and pointer with MRB off "regardless of the MRB of the pointers in the reference chain"; the forwarding word left in old space points to the FIRST POINTER in new space (not to the copied object), so that a second visit can turn that first pointer's MRB on. [ocr; Figs. 4-5 img]
  - Fig. 5 [img] structures: old object states "unmarked" / "visited once" (forwarding, white) / "visited more once" (forwarding, black); result: one referrer -> STR with MRB off; two or more -> all STR pointers MRB on.
  - Fig. 6 [img] unbound variables: one or two referrers -> both REF pointers MRB off; on the third visit the first pointer is turned on and the third is on, the second stays off (so 3 referrers end as on, off, on). "the first and second pointers are copied as off-MRB pointers, and the MRB of the first pointer is turned on when the third pointer is copied." Four states "unmarked, marked once, twice and more than twice" are encoded with "the GC bits and MRB of the object in old area". [ocr]
- Cost: GC overhead 1-2 % at full heap, up to about 4 % at half heap (TR-469 Table 1, printed p. 18 (PDF p. 19) [img]); e.g. Pentomino PE0: heap 6.13 Mword, run 502 s, 3 GCs, 9.56 s, 0.386 Mword active, 1.90 %.
- Messages during GC: "Messages sent to the garbage collecting PE are buffered in the reserved memory area by the PE." TR-715, 5.4.6 footnote 3, printed p. 15 (PDF p. 16) [ocr]. Other PEs waiting for a reply simply wait.
- Not implemented: generation GC ("worth while investigating but not implemented yet", TR-715, 5.4.6), global GC, collection of structure IDs, cross-PE cycles (TR-390, 8).
- Three collectors in total: "an incremental intra-PE garbage collector by Multiple Reference Bit (MRB), a tracing intra-PE garbage collector, and an incremental inter-PE garbage collector" TR-469, 1, printed p. 2 (PDF p. 3) [ocr].

#### 7.x From the peripheral and Japanese reports
- Perpetual-suspension detection inside the copying GC (TR-530, section 4, printed pp. 8-13 (PDF pp. 9-14) [img]; implemented on Multi-PSI): roots are "the executable goals"; `copied_goal_counter` is incremented per goal copied; "perpetual suspension occurred if the copied_goal_counter is smaller than the goal_counter". Then **sweep-and-copy**: sweep the old semispace for GOAL-tagged records (the tag is cleared in old space when a goal is copied); copy each found goal G and everything reachable from it; register G in the "maximal goal candidate table" ("realized as a list of goal records in the old semi-space"). Then **mark-and-sift**: taking candidates latest first, mark from the goal's arguments using "one special bit in each memory cell" (the GC bit), delete any earlier candidate reached; the survivors are the maximal goals reported. New-space layout (Fig. 5): normal GC copy | G1 | data of G1 | G2 | data of G2 | ... | Gn | data of Gn.
- Limits: no global GC, so inter-PE perpetual suspension is undetected; MRB-based incremental detection was "now ... implementing" in Feb 1990 (TR-530, 5.2, 6 [ocr]) and is described as present in TR-715 (Nov 1991).
- TR-563: "PE内部の局所GCとしてマルチPSIではMRB方式と一括GCを併用している" (MRB plus batch GC as the PE-local GC) [img].
- PDSS batch GC also re-whitens single references (TR-498, 5.4), and free lists are "per size" (5.1); TR-321 has separate free lists for variable cells and structures. Memory is not charged to shoens (TR-483, 2.5.3).

---

### Gap 8. PE hardware and microcode

- PE = PSI-II CPU: "It is a 40-bit (8-bit for tag, 32-bit for data) CISC processor controlled by the horizontal microinstruction." Cycle 200 ns; up to 16 Mwords local memory; 4-Kword direct-map cache. TR-715, 3.1, printed p. 3 (PDF p. 4) [ocr].
- Microinstruction width: "controlled by horizontal micro-instruction (53 bits)" TR-585, 2.1, printed p. 2 (PDF p. 3) [img] (OCR reads "33"; the image reads 53).
- Same CPU hardware as PSI-II, different microprogram: "the same CPU hardware of the personal sequential inference (PSI) machine [Nakashima 87] (the microprogram is different)" TR-585, 1, printed p. 1 (PDF p. 2) [ocr].
- Microcode capabilities used: "tag insertion, two-way or multi-way branching on a tag, specially prepared counter and flag operation, ALU operation and memory access operation" in parallel. TR-715, 4.2 [ocr].
- KL1-B size: 1988 "some tens of instructions for built-in predicates" (TR-439, 3.2 [ocr]); 1991 "approximately one hundred instructions for predefined predicates" (TR-715, 4.2 [ocr]). All "directly interpreted by the microcode".
- Registers: argument registers A_i / temporaries X_i, structure pointer S with its own MRB (TR-248, general machine); priority and shoen resource cached in registers (TR-715, 4.2). Register numbers/names of the real microcode: **not found in the English core reports**.
- Microprogram size in words/steps: **not found in the English core reports**.
- Step counts: 39 steps per append reduction (TR-585, 4.1); message steps in 6.2 above. "obtained by microprogram traces" (TR-531, 3.1.1 [ocr]).
- Measurement hardware: "Each PE of the Multi-PSI has a built-in hardware for counting the number of steps executed at specified micro addresses. The PEs also have a calendar clock, all of which are simultaneously initialized when the system starts up." TR-531, 3.2.3, printed p. 13 (PDF p. 14) [ocr].
- Slit check: Gap 1.4.
- Trace/spy: goals are "colored with normal or traced. The reduction of a 'traced' goal results in a trace exception with the information of all its subgoals to be forked. ... the user can specify which subgoals are to be traced next." Spy: "The user can fork a goal with spying color with a spied predicate information (the name and arity of the predicate to be spied). This information is inherited to the child goals. If a subgoal for calling the spied predicate is created, a spy exception is raised reporting the parent goal information." TR-715, 6.1, printed p. 17 (PDF p. 18) [ocr].
- Profiling: Shoen Profiler (per-predicate reduction counts, via control stream) and Processor Profiler ("records the time stamps of idling and local GCs, counts each inter-PE message frequency and the total time spent for message handling, records the user-defined events with time stamps"; started/stopped by a predefined predicate). TR-715, 6.3, printed p. 18 (PDF p. 19) [ocr].
- Deadlock detection at GC and by MRB: TR-715, 6.2 (and TR-530).
- Multi-PSI/V1: "The Multi-PSI/V1 (up to 6 PEs) used the first version of the PSI as PEs" TR-439, 1, printed p. 2 (PDF p. 3) [ocr]; its KL1 had no inter-PE GC (TR-390, 8).
- PIM/m: "The Multi-PSI now has its successor, called PIM/m. The maximum configuration of the PIM/m is 256-PE (16x16 mesh). The PE of the PIM/m is more than twice faster and four times smaller ... the network of the PIM/m was designed to have roughly the same performance as that of the Multi-PSI, while a hardware support for message composing/decomposing is added to the processor. The KL1 implementation described here has been ported to the PIM/m" TR-715, 8, printed p. 22 (PDF p. 23) [ocr].
- PIM (shared-memory clusters): external reference scheme is meant to carry over ("The PIM's clusters correspond to processors in the above model", TR-390, 3.1); "The PIM may not support FIFO communication" (ibid.).
- Pseudo-Multi-PSI on PSI-II: **not mentioned in the English core reports**. TR-469 mentions "the sequential KL1 emulator" (5, printed p. 13 [ocr]) without detail.

#### 8.x From the peripheral and Japanese reports
- **Pseudo Multi-PSI** (TR-483, 7.3, printed p. 28 (PDF p. 31) [img]): "The Pseudo Multi-PSI is an implementation of the KL1 language on single-processor PSI-II machines." "implemented on the PSI-II by storing two distinct set of microcodes in the microprogram storage: One required for KL1 and the other for KL0"; fn. 24: "In the actual implementation, two versions of the microcodes are overlayed due to lack of storage capacity." "One processor of the Multi-PSI is emulated by one process on the pseudo version. Pseudo processors are switched when given number of reductions are completed. The scheduler can specify arbitrary scheduling, including random ones." "the pseudo Multi-PSI attains almost the same performance as the Multi-PSI system consisting of only one processor." Port order: PDSS -> Pseudo Multi-PSI -> real Multi-PSI. "Symbolic tracing feature of the PDSS was also made available on the pseudo and real Multi-PSI."
- [INFERENCE] the KL1 microcode did not fit in PSI-II writable control store together with the KL0 (ESP/SIMPOS) microcode - the only size hint for the KL1 microprogram in the set.
- PDSS = KL1 in C on UNIX, same KL1-B abstract machine and "basically the same compiler" (TR-483, 7.1-7.2); word 1-byte tag + 4-byte data (TR-498).
- KL1-B is common to all ICOT parallel machines: "ICOTで開発中の幾つかの並列マシンは全てこのKL1-Bを中間言語あるいは機械語として用いている" TR-373, section 1, printed pp. 2-3 [img].
- TR-563: PE "identical to the PSI-II CPU", about 130 KRPS append; per-PE microaddress step counters.
- PIMOS 3.2 I/O built-in (PIM era): `scsi_command(SCSI, Unit, LUN, Command, Length, Direction, Data, DataP, ^NewData, ^TransferredLength, ^ID, ^Result, ^NewSCSI)`, 13 arguments (TR-764, 3.4, printed p. 13 (PDF p. 14) [img]). PIMOS "was first developed in 1988" on Multi-PSI and "Later ... ported to several models of parallel inference machines" (TR-764, section 1).
- PIM/p is named as the MRB-hardware target in TR-498 section 7. PIM/m is named only in TR-715 section 8.
- Register list, microprogram word count, numeric tag values: **not found in any of the 18 reports**.

---

### 9. Where the accounts differ (not merged above)

Most rows are differences of wording or of level of detail between papers, not evidence that the implementation changed; the first row is the one real conflict.

| Topic | Statements | Comment |
|---|---|---|
| Which body goal runs next | TR-439 (1988) and TR-715 (1991): "the leftmost" goal; TR-585 (1990): "except for the last one goal which is executed tail recursively" | Real conflict in the prose. [INFERENCE] reconciled by object-code order: TR-248 Fig. 5 and TR-321 Fig. 6 both emit `enqueue_goal` for later goals and `execute` (last instruction) for the source-leftmost goal. Not confirmed by any statement about the V2 compiler. |
| Shoen creation primitive | TR-390 (1988): `execute(Min,Max,Mask,Code,Argv,Control,Report)`; TR-764 (1992): `execute(Code, Argv, MinPrio, MaxPrio, ExcepMask, Control, ^Report)`; TR-715 (1991): `execute(Goal, ControlStream, ReportStream, MinPrio, MaxPrio, Mask)`; TR-483: `execute(Goal, Control, Report)` "plus more"; TR-373: `execute(Goal, Control, Report, Tag)` | Seven arguments at both ends of the period, in different orders; TR-715 folds Code+Argv into Goal. Argument order of the real built-in is therefore uncertain. |
| `raise` / `exception` | TR-483: `raise(Info, Data, Tag)`, `exception(Info, Goal, NewGoal)`; TR-764: `raise(Tag, Data, Info)`, `exception(Kind, EventInfo, ^NewCode, ^NewArgV)` | Unexplained in the reports. |
| Body goals pushed | TR-439: "all the body goals except for the leftmost one"; TR-715/585: only user-defined goals; unification and built-ins run in line | Level of detail. |
| Suspension | TR-439: "the causal variable"; TR-715: "variable(s)"; but TR-390 (1988) already names "multiple hook variables" | Wording; multi-wait existed in 1988. |
| WTC | TR-439: WTC attached to thrown goals and unify messages, split "when they throw child goals"; TR-715: split on throw or %unify | Wording. |
| Loop-avoidance direction | TR-373 and Multi-PSI/V1: bind only from smaller PE number to larger; TR-390: reversed, plus the safe/unsafe flag | TR-390 says the reversal is deliberate. |
| Built-in instruction count | TR-439: "some tens"; TR-715: "approximately one hundred" | Growth of the built-in set. |
| MRB instruction set | TR-248/TR-321 (1987): `mark`, `collect_stack`, garbage stack, `reuse_list`, `replace_cdr`; TR-498 (1989): `*_marked_*`, `mark_element`, `collect_vector`, `put_reused_list/vector`, no garbage stack | Both are emulator-era; which the V2 microcode has is not stated. |
| Append speed | 150 KRPS (TR-439), 128 KRPS / 39 steps (TR-585), about 130 (TR-563), 110/128/146 by reuse level (TR-466) | Different compilations. |
| Deadlock detection, trace/spy, profilers | absent in 1988 papers; TR-530 (1990) and TR-715 section 6 | Added later. |

### 9a. What none of the 18 reports contains
- Which tag bit is the MRB and its numeric polarity; any numeric tag value or tag table.
- Goal record, shoen record, foster-parent record and suspension record sizes and field offsets for Multi-PSI.
- Message order codes and per-field byte formats; external-ID bit split; the `%` names of the shoen-control / WTC messages.
- KL1 microcode register assignments; microprogram size; opcode encodings of KL1-B.
- Float and string layouts; atom representation below "one-word atomic cell".
- Initial WTC weight; resource-budget split between shoen and foster parents; free-list refill batch size.

Fuller transcriptions that were condensed here (TR-737 figures, TR-250 tables and figures, TR-563 Table 2, TR-498/TR-321 measurements) are in `(scratch)/mpsi_work/partA.md` and `(scratch)/mpsi_work/partB.md`.

### 10. Open web copies (searched last)
Searched with generic bibliographic terms only (2026-11-20). No open full text of either conference paper was found; the ICOT TR scans remain the only open copies.
- "Multiple Reference Management in Flat GHC", Chikayama & Kimura, Proc. 4th ICLP (MIT Press, 1987), pp. 276-293 (one later Springer reference list prints 276-283). Bibliographic record only: https://bibtex.github.io/ICLP-1987-ChikayamaK87.html . Open text = TR-248: https://www.airc.aist.go.jp/aitec-icot/ICOT/Museum/TRTM/TR/TRpdf/tr0248.pdf
- "Distributed Implementation of KL1 on the Multi-PSI/V2", Nakajima, Inamura, Ichiyoshi, Rokusawa, Chikayama, Proc. 6th ICLP, 1989, pp. 436-451. Record only (no full text): https://cir.nii.ac.jp/crid/1570572699088496256 . Open text = TR-439 (and the extended TR-715): https://www.airc.aist.go.jp/aitec-icot/ICOT/Museum/TRTM/TR/TRpdf/tr0439.pdf
- Journal version of TR-390: Ichiyoshi, Rokusawa, Nakajima, Inamura, New Generation Computing (1990), https://link.springer.com/article/10.1007/BF03037484 (publisher page; paywall status not checked).
- The search-result URLs above were returned by the search engine; I did not fetch them individually. The TR URLs follow the pattern the scans were downloaded from.

## Appendix B. VPIM: extraction from TM-1044 "Inside VPIM"

Draft. Organised by gap number; inside each gap, one block per chapter group. Citations are `file:line` in the original LaTeX files (line numbers identical in `vpim/vpim/DOCUMENT/TM-1044.j/*.tex`; file names here carry the `TM-1044.j_` prefix of the converted copies). Japanese quotes are verbatim from a single source line. "(inference)" marks the extractor's reading; "(from VPIM source ..., not TM-1044)" marks facts taken from the PSL source; "not in TM-1044 (sN)" means chapter N is silent -- another chapter's block under the same gap may answer it; the list of items silent across the WHOLE document is at the end of the Synthesis. Quote delimiters differ per block (「...」, backticks, or straight quotes, with the citation before or after); 225 Japanese quotes were machine-checked to occur on a source line covered by a citation on the same Markdown line; the only quoted strings not so checked are the document titles, one figure label (RHOOKへのポインタ) and the README.j sentence. The 24 "(from VPIM source ...)" citations were checked for file existence and identifier presence; the MRB polarity and priority-shift constants were re-read by hand. Source was consulted beyond `src/structures/` (also `functions/`, `interpreter/`, `primitives/`), each use labelled. Length exceeds the 400-700 line target because the per-chapter field tables were kept whole; the pressure model, goal-post protocol and Multi-PSI lineage are each told in more than one block.

### Bibliographic data and the virtual machine (ch. 1, ch. 2 tail)


##### Bibliographic data
- Title: VPIM 処理方式解説書 (ICOT Technical Memorandum TM-1044; English name "Inside VPIM" per `vpim/DOCUMENT/README`). `TM-1044.j_top.tex:17` 「{\LARGE VPIM 処理方式解説書}」.
- Date: 5 April 1991. `TM-1044.j_top.tex:19` 「{\Large 1991年 4月 5日}」; same date signs the preface, `TM-1044.j_hajimeni.tex:67`.
- Issuer / editor: ICOT, First Research Laboratory. `TM-1044.j_top.tex:21-23` 「{\Large 第一研究室~編}」. Copyright 1991 ICOT (`top.tex:26`).
- Version described: VPIM version 1.0, released February 1991 as the first version with everything needed to run PIMOS. `TM-1044.j_hajimeni.tex:13` 「VPIM バージョン1.0 をリリースすることができた。」 Development began summer 1988 (`hajimeni.tex:3`). The text is the handout of the 28 Feb - 2 Mar 1991 Yugawara source-reading camp, re-edited (`hajimeni.tex:15-19`).
- Scope statement: describes KL1-B *interpretation*, not compilation. `TM-1044.j_hajimeni.tex:28` 「KL1-B 命令の解釈実行に重点を置いて説明する。」 (focus is on interpretive execution of KL1-B instructions).
- Contact: vpim@icot.or.jp (`hajimeni.tex:59`).
- Chapter order (`top.tex:40-57`) and authors (each chapter's 執筆担当者 line):

| ch | file | subject | author(s) | cite |
|---|---|---|---|---|
| 1 | s1 | overall structure, virtual hardware | 今井 (Imai) | s1.tex:10 |
| 2 | s2 | data structures | 畑澤 (Hatazawa) | s2.tex:95 |
| 3 | s3 | code module, KL1-B instructions | 平野 (Hirano) | s3.tex:27 |
| 4 | s4 | memory management, MRB | 今井 | s4.tex:10 |
| 5 | s5 | D-code | 畑澤 | s5.tex:11 |
| 6 | s6 | goal scheduling | 今井 | s6.tex:10 |
| 7 | s7 | unification, merge | 今井 | s7.tex:10 |
| 8 | s8 | slit check | 堂前 (Domae) | s8.tex:10 |
| 9 | s9 (+s9-msg-kl1data, s9-network, s9-message) | inter-cluster | 仲瀬, 高木 (Nakase, Takagi) | s9.tex:9 |
| 10 | s10 | shoen / foster parent | 川合, 山本 (Kawai, Yamamoto) | s10.tex:11 |
| 11 | s11 | stop-and-copy GC | 今井 | s11.tex:10 |
| 12 | s12 | debug support | 今井 (12.x perpetual-suspension part from 稲村 Inamura; trace/spy parts from 平野) | s12.tex:12-14 |
| 13 | s13-1, s13-3 | SCSI | 武井, 堂前 (Takei, Domae) | s13-1.tex:12 |
| App. | s13-a | SCSI appendix | 武井 | s13-a.tex:3 |

- Companion PSL documents in the same directory (`vpim/DOCUMENT/README`): 1j "PSL Macro Definition Specification", 2j "Syntax of PSL Language", 3j "Outline of PSL", 4j "Minor Changes to PSL", 5j "並列推論マシンPIMにおける抽象機械語KL1-Bの実装 --高級機械語を実装するための道具立--" by 山本礼己 (Reki Yamamoto), 今井明 (Akira Imai), 中川貴之 (Takayuki Nakagawa), 川合英夫 (Hideo Kawai), ICOT, undated (`5j.tex:2-18`), 6j "List of Basic Macros".
- Lines of ch. 2 inside the already-read range 92-900 that are garbled in `vpimdoc/` and should be re-read from `vd2/`: `TM-1044.j_s2.tex:525`, `:721`, `:794`.
- Source-text note: the distributed files are ISO-2022-JP. The copy in `scratchpad/vpimdoc/` has mojibake on roughly 1-20 lines per chapter (JIS spans decoded as ASCII). All quotes and line numbers below are from a clean re-decode in `scratchpad/vd2/` (identical line numbering to the originals in `vpim/vpim/DOCUMENT/TM-1044.j/`).

##### Chapter 1: the virtual machine (context for every gap)
- VPIM is the abstract machine common to the shared-memory PIM sub-modules; it is then converted to each real machine's instructions. `TM-1044.j_s1.tex:30` 「それを実際のハードウェアが持つ命令に変換することとした。そのため、」 (it was decided to convert it into the instructions the actual hardware has).
- Memory management and priority control are done at VPIM level, not by PIMOS (`s1.tex:38-40`).
- Reduction cycle: pop a goal from the ready goal stack; test candidate clauses' passive parts, pushing each suspension-cause variable on a stack and trying the next clause; if none commits and some suspended, hook the goal on the variables; on commit, body goals get goal records and are pushed to the ready goal stack; a body unification on a variable with waiters pushes them to the ready goal stack (`s1.tex:77-99`). Key quote `s1.tex:86` 「中断原因になった変数をスタックに積み、次の候補節を試みる。」 (push the variable that caused suspension on a stack and try the next candidate clause).
- All data (variables, lists, goal records, code modules) live in the heap (`s1.tex:101-103`).
- Topology: clusters joined by a network; each cluster about 8 PEs on a shared bus/memory. Cluster number 8 bits (0-255), PE-in-cluster number 3 bits (0-7) (`s1.tex:140-164`). `s1.tex:158` 「\item クラスタ番号 (8ビット: 0 $\sim$ 255)」.
- With one PE per cluster the inter-cluster processing is "like Multi-PSI" loosely-coupled processing (`s1.tex:152-154`).
- Address space: one 32-bit shared space per cluster; no per-PE local memory assumed (`s1.tex:168-172`).
- Tagged word figure: bits 39..32 tag (MRB 1 bit + Type 6 bits), bits 31..0 value (`s1.tex:176-200`); reads/writes of one tagged word are atomic (`s1.tex:184-185`).
- Registers (`s1.tex:211-239`): argument registers (tagged words; at least 5 = the largest built-in arity. `s1.tex:216` 「\item 個数としては、5個(もっとも多く引数を持つ組込述語の引数個数)以上の適当数持つものとする。」); work registers (unlimited in the VM); constant registers (null = reads all-zero, void = write-only, PE-number, cluster-number, both set at initialisation); special registers PC, CCR, SCR (slit check register).
- KL1-B instructions take registers or immediate constants as operands; no limit on instruction count/arity in the VM except register-operand count <= number of argument registers (`s1.tex:279-304`).
- Shared-memory primitives (table `s1.tex:316-346`): `read_invalidate`, `read_purge`, `exclusive_read`, `direct_write` (cache optimisations), `lock_read`, `write_unlock`, `unlock`. Only the last three are semantically required: `s1.tex:350` 「全て最適化のための操作であり、これらの操作を持たないPIMにおいては」 (all [the others] are optimisations; on a PIM lacking them [use plain read/write]).
- Hardware lock: never more than one location locked at once, and only register-level work inside the lock, i.e. a compare-and-swap primitive (`s1.tex:353-357`). Linked shared structures (shoen/foster-parent records, export/import tables) use "soft locks" built from it (`s1.tex:359-368`).
- Slit check: events are detected at reduction boundaries; SCR is a set of "10 to 12 or so" cause flags: network receive, interrupt from another PE in the cluster, trap raised during a KL1-B instruction (`s1.tex:372-392`). `s1.tex:386` 「SCRは一種の割り込み要因フラグの集合(10ないし12個程度)であり、」.
- Network model: complete graph joining PEs of the *same PE number* in every cluster; word-at-a-time send/receive of tagged words; unbounded buffering, no message length limit; each link FIFO, but because there are several links between two clusters, message overtaking between clusters is possible and is handled explicitly (`s1.tex:394-414`).

##### Chapter 2 recap (lines 92-900, already read by the caller) and tail (900-1087)
- Recap with section line numbers: basic unit `s2.tex:100`; type table `s2.tex:140`; atom `:248`, integer `:282`, float `:304`, string `:334`, list `:416`, vector `:441` (null `:448`, short `:467`, long `:495`); goal record `:544`; environment records: plain `:654` (VECT2), with original code `:706` (VECT4), with caller code `:759` (VECT6), spy `:818` (VECT8), trace `:878` (VECT3).
- Trace environment record (`s2.tex:900-908`): pointer type VECT3; words = {INT Logical Priority; INT Goal Attribute; any-type Trace ID}. Trace ID is the user datum given to `apply_tracing`, emitted as an argument of the trace exception message (`s2.tex:914-920`).
- Nine environment-record kinds (`s2.tex:928-941`):

| code | pointer tag | debug information carried |
|---|---|---|
| B | VECT2 | none |
| BO | VECT4 | original code |
| B-C | VECT6 | caller code |
| BOC | VECT6 | original + caller code |
| B--S | VECT8 | spy |
| BO-S | VECT8 | original + spy |
| B-CS | VECT8 | caller + spy |
| BOCS | VECT8 | original + caller + spy |
| BT | VECT3 | trace |

- Transition tables (`s2.tex:957-1085`; legend `:949-954`: → reuse parent's record, 新 make a new record, × raise trace/spy exception instead of creating the goal, △ impossible):
  - `enqueue`/`execute` instructions (`:962-986`): unchanged attributes → share the parent's environment record; priority or other attribute changed → new record of the same kind; **instruction suspends → new record with O added (B→BO, B-C→BOC, B--S→BO-S, B-CS→BOCS) and a D-code goal is created**. `s2.tex:984` 「\multicolumn{7}{c}{{\tt enqueue}, {\tt execute}系の命令がサスペンドする場合には{\tt enqueue}系の}」 (when an enqueue/execute-type instruction suspends, [a D-code goal that runs the] enqueue-type [built-in is created]).
  - enqueue-type built-ins running from a D-code goal (`:995-1018`): start state always has O; the new goal gets a new record with O removed.
  - `apply` → plain B (new record unless already B / B--S); `apply_tracing` → BT; `apply_spying` → B--S; `create_shoen` family → B; from a spy state apply_tracing/apply_spying/create_shoen raise the exception; from BT everything raises (`:1027-1052`).
  - Suspending built-in → D-code, adds O (B→BO etc.); calling a built-in that is defined in KL1 (an enqueue) adds C (B→B-C, B--S→B-CS) (`:1061-1078`).
  - A built-in called from D-code never suspends, because its input arguments were waited on in the guard of the D-code; and in trace mode built-in suspension does not occur (`s2.tex:1080-1082`). `s2.tex:1081` 「\multicolumn{5}{c}{入力引数をガードでwaitしているのでサスペンドは発生しない。}」.


### Synthesis: short answers per gap, and cross-chapter reconciliations

Everything here is a pointer into the detailed sections below; the citations and quotes are there. "(source)" = taken from the VPIM PSL source, not from TM-1044.

1. **Ready goals.** One ready goal stack PER PE: 4096 (2^12) physical priorities, one 4-word entry each {lower-entry link; INT physical priority; HOOK goal chain; higher-entry link}, only non-empty entries doubly linked, LIFO within a priority, idle goal at priority 0 (s6). Logical priority is 2^31 per goal; the conversion formula is NOT in TM-1044 (source: `>> 19`). `execute` does not touch the stack unless the slit-check flag is set; `proceed` pops; both count a reduction first (s3). Goal records come from the general power-of-two free lists (1..256 words, per PE); 16/32-word short/long goal records are (source); GC allocates goal records at 2^(n+1), minimum 16 words (s11).
2. **Suspension.** Single wait: variable cell = HOOK -> goal record, goals chained LIFO through the goal record's second control word. Multiple wait: variable cell = MHOOK -> 2-word suspension record {next link; DREF -> flag}; one shared 2-word suspension flag {HOOK -> goal (EOL once resumed); INT count}. All by compare-and-swap, no lock bits; a failed CAS re-enqueues the goal. Unifying two hooked variables concatenates the chains (higher-address cell becomes REF to the lower; its waiters go first). Resume sends each goal back to the PE that created it (goal post + SCR bit 6), keeping its priority; explicit ordering is not stated. A body built-in or enqueue with an unbound input becomes an ORDINARY goal of a per-built-in D-code predicate (`add(A,B,C) :- wait(A), wait(B) | builtin:add(A,B,C).`) pushed on the ready stack; it suspends from its guard like any user goal; its environment record gains the "original code" part (B -> BO, s2 tail).
3. **MRB.** One bit in the 8-bit tag (`TM-1044.j_s2.tex:110-114` lists Reserved 1 bit, MRB 1 bit, Type 6 bits in that order; no bit number is given; the s1 figure draws MRB to the left of Type), carried by the referencing pointer; OFF = white = single reference, ON = black = possibly multiple (s4); numeric 0/1 only from (source). KL1-B/s MRB instructions are exactly `mark`, `collect_value`, `collect_list`, `collect_vector`, and the eight `reuse_*`; there is no put_marked_value / write_marked_value / put_reused_structure in TM-1044. Reading through a black pointer blackens what is read. VPIM collects the surface only (list CDR to depth 3). GC never whitens (Multi-PSI's MRB maintenance deliberately dropped).
4. **Layouts.** Code module = 16-word header (common to all machines, based on Multi-PSI's) + other-module reference table (4-word module / predicate descriptors) + constant table (black pointers; bodies outside the module) + entry table (hash + 3-word name entries) + CDESC + code area (machine dependent). Predicate definition header = 6 words ending in a VECT0 marker; COD points just past it. Merger record = 8 words, input cells typed MGHOK.
5. **Shoen / foster parent.** Shoen record 24 words, foster-parent record 22 words (document) -- the source records are larger. Resource = reduction count, double-word, cached per PE. Exception report is always `{shoen#exception, ExpNumber, ExpInfo, NewCode, NewArgv}`; ExpInfo per kind; built-ins are identified by KlbID ("corresponds to the Multi-PSI opcode") + module/offset pairs from the environment record.
6. **Inter-cluster.** External reference ID = 8-bit cluster | 4 flag bits | 20-bit export-entry offset; white (single-reference) entries carry no WEC word; black WEC = 2^24 per export, 2 words on the export side, 1 on the import side; one structure level per message; "24 message kinds".
7. **Memory / GC.** Three areas: system shared fixed (0..0x100000), processor-local fixed (0x100000..0x200000, 8 equal parts), heap (two semispaces). 256-word pages, nine power-of-two free lists per PE, no splitting or coalescing. GC = per-cluster parallel stop-and-copy with five synchronisation points, triggered only by page shortage through the slit check.
8. **Carry-over.** TM-1044 never mentions PIM/m. The distribution README states VPIM is common to "all models of the PIM except PIM/m". PSL reserved a `#PIMM_define` directive (1j) but its expansion was "not yet studied" and the shipped source never uses it. Multi-PSI is cited as the origin of: 4096 priority levels, the code-module format, MRB incremental GC, WTC, list-cell streams, `apply_tracing` / `apply_spying` (identical specification), perpetual-suspension detection, and the KlbID = opcode numbering. Stated as fixed from outside VPIM: 32-bit integers (PIMOS, s2:286), CAR/CDR order (must match the KL1 compiler setting, s2:421-423), module header / reference table / constant table / entry table common to all machines (s3:53, 141), body built-in output unification after the built-in (compiler contract, s10:1012), exception tag bits 15-8 belong to PIMOS (s10). (inference, not stated as requirements: that the exception vector shape, the KlbID numbering and the `builtin` module name are equally binding on PIM/m because PIMOS and the compiler consume them.)

#### Reconciliations between chapters
- **Two different tracers.** The MRB of the goal record's FPREC word is the switch of the *limited tracer* (限定トレーサ, the CSP-level one): `TM-1044.j_s2.tex:622` 「即ち、MRB白が限定トレーサOFFを、MRB黒が限定トレーサON を意味するものとする。」 (MRB white = limited tracer OFF, black = ON). The KL1-level *soft trace* and *spy* of ch. 12 are instead selected by the environment-record pointer type (VECT3 / VECT8) and never use that bit. 限定トレーサ occurs only at `TM-1044.j_s2.tex:612-622` and the footnote `TM-1044.j_s2.tex:882` (grep of every chapter); its mechanism is not described anywhere in TM-1044.
- **Goal record first word.** Goal record word 0 is GOAL with MRB white; merger record word 0 is GOAL with MRB black; the old-space sweep for perpetual suspension relies on this (s12, s7; s2:598 「理のために{\sf GOAL}型(MRBは必ず白)とする。」 is cited as `TM-1044.j_s2.tex:598`).
- **Goal-record operand bias.** `store`/`load` POS operands are biased by +5 (s3), which matches 6 control words only if the goal pointer addresses the second control word; that addressing is confirmed only by (source).
- **Record sizes.** Shoen 24 / foster parent 22 words in the document versus 64(38 valid) / 32(28 valid) in the source. (inference: the document's figures predate the stop/start bit table and WTC fields.)
- **Which PE a resumed goal returns to.** Three wordings. `TM-1044.j_s7.tex:759` 「リジュームによる再スケジュールは、そのゴールを作成したPE」 (the PE that CREATED the goal). `TM-1044.j_s6.tex:814` 「ときは、そのゴールをサスペンドさせた PE に投げて、サスペンドさせたPEで」 (the PE that SUSPENDED it). `TM-1044.j_s2.tex:627` 「る。この情報は一旦サスペンドしたゴールがリジュームした時に、そのゴール」 -- the goal record's processor-ID word holds "the PE the goal belongs to", is written at suspend time or earlier, and is read at resume to return the goal "to its original PE" (`TM-1044.j_s2.tex:624-628`). (inference: the mechanism is the processor-ID word; "created" and "suspended" coincide unless the goal migrated between creation and suspension, and s2's "written at suspend time" favours the suspending PE.) Item 2 above says "created" after s7; treat it as unresolved between these.
- **Where a COD pointer points.** s3: `TM-1044.j_s3.tex:913` 「お、述語ポインタ({\sf COD}\index{COD@{\sf COD}}タイプ)は常に機械語命令」 -- always the first instruction, i.e. just after the 6-word header whose word 3 is the offset to the module head and word 5 the VECT0 marker. s11: `TM-1044.j_s11.tex:921` 「プの場合は、述語定義の先頭を指しているが、この直前にモジュー」 -- "points at the head of the predicate definition, and just before it is the offset from the module's first word". The two do not agree on what immediately precedes the COD target (marker vs offset). Unresolved by TM-1044; ch. 3 is the layout chapter.
- **Shoen ID.** `TM-1044.j_s10.tex:473` 「荘園IDは、荘園を格納した黒輸出表エントリのオフセット値の上位3ビットにクラ」 (the black-export-entry offset with the cluster number joined at its upper 3 bits) versus ch. 9's external reference ID with an 8-bit cluster field and 4 flag bits above a 20-bit offset, while `TM-1044.j_s10.tex:956` 「という形になっていて、荘園を識別する荘園IDも外部参照IDを用いている。」 says the shoen ID IS an external reference ID. The "3 bits" wording is unexplained (inference: a leftover from an 8-PE or earlier layout, or a typo).
- **ReplyHook (RHOOK) record.** Text, figure and source disagree on the order of its 3 words; unresolved by TM-1044.
- **Message count.** "24 kinds" is stated; 21 are named (24 if white/black variants of three messages count separately -- inference).
- **Idle goal on real machines.** A commented-out sentence in s5 saying the idle goal is VPIM-only is retracted in the same comment. (inference: the idle goal is therefore real-machine behaviour too; the printed document says only "currently in VPIM".)
- **Document gaps.** All state-transition diagrams of ch. 10 are blank placeholders in the LaTeX source; numeric constants for resource units, WTC amounts, message codes, exception numbers and report codes are absent from the document and given below only from (source).


#### Silent across the whole document (checked against every chapter block)
- Logical-to-physical priority formula (only "rounding" is described); numeric MRB bit value and bit number; short/long goal-record sizes; suspend-stack and unify-stack sizes; explicit order in which several resumed goals run.
- Opcodes / KlbID numbers of individual built-ins; numeric message kind codes; numeric exception numbers and report-stream codes; report-stream formats other than the exception vector; resource, cache and WTC constants; GC threshold.
- Hash functions and table sizes (entry table, export/import, structure table); wire encoding of floats; maximum packet size.
- Step-by-step locking when building a multiple-wait structure; the pop path when the current priority level empties.
- IPL / boot image / how the bootstrap is loaded; save/restore of a running system; FEP-side protocol; disk layout; the limited tracer (CSP) mechanism; anything specific to PIM/m.
- Answered in another block than the one that says "not in (sN)": MRB bit position (s2:110-114, s1 figure); body built-in suspension (ch. 5 block of GAP 2); which instructions host the slit check (`execute`, `proceed`, `suspend`, `fail`, `check_heap`: ch. 3 block of GAP 1/2); perpetual-suspension report format (ch. 10 block of GAP 5); message formats (ch. 9 block of GAP 6); GC algorithm (ch. 11 block of GAP 7).

### GAP 1: Ready goal stack and priority

#### From ch. 4 (memory, MRB), ch. 5 (D-code), ch. 6 (scheduling)

##### Ready goal stack: structure
- One ready goal stack PER PE; goals linked LIFO per priority. `TM-1044.j_s6.tex:29-38` 「に応じて図\ref{readygoalstack}のような(リンクによるLIFOの)」 = "according to [priority], in a (linked, LIFO) [ready goal stack] as in the figure". Per-PE: `TM-1044.j_s6.tex:593` 「クラスタ内の各PE は、個別にレディゴールスタックを持っているので、」 = "each PE in the cluster has its own ready goal stack".
- "Executable" = "not obviously suspended"; a suspended goal hangs on its variable cell and is not in the ready link (footnote, `TM-1044.j_s6.tex:30-33`).
- Two priorities. Physical: 4096 (2^12) levels actually distinguished at run time, `TM-1044.j_s6.tex:44-46` 「4096 ($2^{12}$) 段階」 = "4096 (2^12) levels". Logical: what the KL1 user sees, 2^31 resolution per goal, `TM-1044.j_s6.tex:47-51` 「KL1ユーザに見えるプライオリティであり、各ゴール毎に $2^{31}$」 = "the priority visible to the KL1 user, 2^31 per goal".
- Logical is converted to physical when the goal is put on the stack; low logical priorities round to the same physical level, so logical order may not be honoured. `TM-1044.j_s6.tex:53-57` 「(丸め誤差により)同一物理プライオリティに変換されるため、」 = "because (by rounding error) they convert to the same physical priority".
- Mapping FORMULA: not in TM-1044 (s6). (from VPIM source structures/str_pr_goal_stack.psl.c:312-319, not TM-1044): `_LOGICAL_PRIO_BITS 31`, `_PHYSICAL_PRIO_BITS 12`, `_SHIFT_VALUE_LOGICAL_TO_PHYSICAL_PRIO 19`; `s_ConvertLogicalToPhysicalPriority` = shift right 19, i.e. physical = logical >> 19. Also (same file :201-209, not TM-1044) `_MAX_PHY_PRIO 0xfff`, `_MIN_PHY_PRIO 0`, `_IDLE_GOAL_PRIO 0`, `_MAX_LOGICAL_PRIO 0x7fffffff`, `_MIN_LOGICAL_PRIO 0x00100000` (excludes idle), `_REPORT_GOAL_PRIO 0x7fe00000`, `_INPUT_GOAL_PRIO 0x7fffffff`, same-physical mask `0x0007ffff`.
- Entries live in the fixed area (processor-local fixed area item 3, `TM-1044.j_s4.tex:135-140`, which holds only the HEAD of each link); one 4-word entry per physical priority, contiguous. `TM-1044.j_s6.tex:59-61` 「4ワードで構成される1エントリが、物理プライオリティ種類数連続している」 = "one entry of 4 words, repeated contiguously for the number of physical priorities". => 4096 x 4 = 16384 words (inference; source comment str_pr_goal_stack.psl.c:200 gives `_SIZE_OF_PHY_GOAL_STACK 0x4000`, not TM-1044).

Entry layout (text `TM-1044.j_s6.tex:63-69`, legend `TM-1044.j_s6.tex:166-169`; NOTE this figure draws word 0 at the BOTTOM of each entry, priority 4095 at top, 0 at bottom):

| # | tag | value / meaning |
|---|-----|-----------------|
| 0 | (not shown; REF in source, not TM-1044) | pointer to the (valid) LOWER entry; drawn as a bullet = end at priority 0 (`:114`) |
| 1 | INT | physical priority value, 0..4095 (`:100,104,107,110,113`) |
| 2 | HOOK | pointer to first (executable) goal record of this priority; "?" drawn where the entry is unused (`:99,102,105,106,109,112`) |
| 3 | (not shown) | pointer to the (valid) HIGHER entry; bullet at the top entry (`:98`) |

- Offsets confirmed (from VPIM source structures/str_pr_goal_stack.psl.c:79-85, not TM-1044): `_SIZE_OF_STACK_ENTRY 4` ("PIM/c, PIM/i"; "32 bytes PIM/p"), `_LOWER_ENTRY_OFST_STE 0`, `_PHY_PRIO_OFST_STE 1`, `_GR_PTR_OFST_STE 2`, `_HIGHER_ENTRY_OFST_STE 3`.
- Only VALID (non-empty) entries are doubly linked; reason: `TM-1044.j_s6.tex:70-71` 「プライオリティが変化した時に実行すべきゴールの検索を高速化するためである。」 = "to speed up finding the goal to run when the priority changes". In the figure 4094 is empty and skipped: 4095 <-> 4093 (`:126-149`).
- Idle goal is always linked at physical priority 0 (`TM-1044.j_s6.tex:122-123`, `:294-298`).
- Goals within a priority are chained through the goal record (second control word HOOK/EOL, already known); figure shows 2-3 records chained per entry (`:115-121`).

##### Permanent registers (`TM-1044.j_s6.tex:213-240`)
- `D_CurrentGoalStackPtr`: cached head of the goal link of the entry whose physical priority equals the running goal's (the starred HOOK word of the current entry is really held here, `:92-95` 「実際には★は\\」). Push at equal priority = rewrite this register only; pop likewise as long as it is not EOL. `:223` 「値が {\sf EOL}でない限り、取り出し操作も、このレジスタの書き換え」 = "unless its value is EOL, the take-out operation too is a rewrite of this register".
- `D_CurrentStackEntryPtr`: pointer to the stack entry of the running goal's physical priority. `:226` 「現在実行中のゴールの物理プライオリティのスタックへのポインタを保持している。」
- `D_MaxPriority`: highest physical priority now in the stack; value part = priority, TYPE (tag) part = valid/invalid. Invalid when equal to the running priority; valid only between pushing a higher-priority goal and the update of `D_CurrentStackEntryPtr` (a "high priority goal arose" software interrupt = slit-check cause is always pending then). `:230` 「タイプ部に、このレジスタの値部が valid か invalid かの意味を持たせている。」
- Other names (from VPIM source structures/str_pr_goal_stack.psl.c:215-227, not TM-1044): `D_GoalStackBase`, `D_GoalStackLimit` (in memory), `D_WorkStackEntryPtr`, `D_WorkIdlePriority`.

##### When goals are pushed / popped
- Push (`TM-1044.j_s6.tex:180-198`): enqueue-family instruction creates a goal; resume of a suspended goal (variable instantiated; foster parent made runnable by `%start` / `%supply_resource`); `%throw_goal` arrives; goal received by intra-cluster load balancing; D-code goal split off; execute-family instruction detects a slit-check event and parks the goal it was about to run.
- Pop (`TM-1044.j_s6.tex:200-209`): `proceed` (running goal ended with no child); after slit-check processing, the goal parked by execute; throwing a goal on a load-balance request. So `execute` itself does not touch the stack unless a slit-check event is pending (inference from the two lists).
- Order: LIFO within a priority (`:36`); FIFO is nowhere mentioned in s6.

##### Push algorithm, P_push vs P_cur vs P_max (`TM-1044.j_s6.tex:242-287`)
- (1.a) P_push = P_cur: push onto `D_CurrentGoalStackPtr` (`:250-251`).
- (1.b) entry P_push already has goals: push onto that entry (`:252-253`).
- (1.c) P_push < P_cur, entry unused: search toward HIGHER priority for a non-empty entry, get the upper and lower neighbours, link both ways, push (`:254-258`).
- (2.a) P_max invalid, P_push > P_cur: entry must be unused; link it with the P_cur entry; P_max := P_push (valid); raise slit-check cause; push (`:260-267`). `:265` 「→ $P_{max} := P_{push}$  として (validにして)」
- (3.a) P_max valid, P_push > P_max > P_cur: link with the P_max entry, P_max := P_push, push (`:271-274`).
- (3.b) P_max > P_push > P_cur, entry unused: search toward LOWER priority for a non-empty entry, link, [push] (`:275-278`).
- (3.c) P_max = P_push > P_cur: cannot occur (`:279-281`).
- Priority CHANGE (switch to the higher goal): update of `D_CurrentGoalStackPtr`, `D_CurrentStackEntryPtr` and invalidation of `D_MaxPriority` are done in the slit check, `:285-287` 「{\tt D\_MaxPriority}の無効化は、スリットチェックで行なう。」 = "invalidation of D_MaxPriority is done in the slit check".
- Pop path when `D_CurrentGoalStackPtr` is EOL (drop to next lower valid entry): not described in TM-1044 (s6); the lower-entry link exists for it (inference).
- What enqueue_with_priority / execute / proceed do instruction-by-instruction: not in TM-1044 (s4-s6) beyond the lists above (refers to KL1-B chapter).

##### Intra-cluster distribution: request / throw (`TM-1044.j_s6.tex:289-353`)
- Automatic, by the runtime, not by user pragma (`:20-22`).
- Idle goal runs special built-in `kblt_idle` (`:299-302`; in the D-code it is the guard built-in `idle`, s5:180): (1) set own bit in the goal-request BITMAP in the fixed area and set the "goal request bit" in every other PE's slit-check register (SCR); (2) poll own SCR "goal received bit" (really: wait for any event, footnote `:318-319`). `TM-1044.j_s6.tex:311` 「\item 固定領域に用意したゴール要求の有無を示したビットマップの」
- Bitmap is 8 bits PE0..PE7 in the system shared fixed area, plus one GOAL POST per PE; SCR has "要求" and "受信" bits (figures `:356-430`, `:435-507`, `:512-587`).
- Sender, at its slit check: (1) read the bitmap into a register and clear the other PEs' request bits; (2) take ONE goal, the HIGHEST priority one, from its own ready stack, link it to the requester's goal post, set the requester's "goal received bit". `TM-1044.j_s6.tex:331` 「プライオリティの一番高いゴールを一つ取りだし、」 = "take out one goal of the highest priority". Repeat (2) for every PE whose bitmap bit was set; if it runs out of goals, it issues a goal request on behalf of the unserved PEs (`:336-341`).
- Receiver: takes ALL goals from its goal post (may be several) and links each at its physical priority (`:345-353`).
- (from VPIM source structures/str_pr_goal_stack.psl.c:683, not TM-1044) `_ENOUGH_GOALS 3` with `s_IfNotEnoughGoal`.

##### High-priority goal request: "pressure model" (`TM-1044.j_s6.tex:591-651`)
- Variables: P (pressure), UpLimit, LowLimit, Δt (timer interrupt), CLMax (cluster max priority), PEMax (priority this PE is running). Every Δt: `P(new) = P(old) + (CLMax - PEMax)` (`:618`).
- P > UpLimit: PE issues a goal request (same mechanism as idle) and resets P. P < LowLimit: PE sets CLMax := its PEMax and resets P (`:607-613`, example 300/100/200 `:623-636`).
- Known problems: received goal may be lower priority than the one being run; CLMax is currently set to the priority of each goal sent on request, which risks lowering it unduly (`:641-650`).

##### Child count / fork count (`TM-1044.j_s6.tex:653-816`)
- Foster-parent record holds the child count (goals + child shoens); each PE caches a FORK COUNTER for one foster parent at a time; total = Σ fork counts + child count (`:660-673`); written back (added in) when the PE switches foster parent or goes idle (`:676-679`).
- When throwing a goal: if (fork counter > 0) AND (thrown goal belongs to the currently running foster parent), first add the fork count into the child count and clear the counter, then throw (`:797-803`). Guarantee: child count 0 implies no goals (`:805-808`).
- A goal resumed by active unification is thrown back to the PE that suspended it and runs there. `:814` 「ときは、そのゴールをサスペンドさせた PE に投げて、サスペンドさせたPEで」 = "it is thrown to the PE that suspended the goal, and [run] on the suspending PE".

##### Goal record free lists and sizes
- TM-1044 (s4) has no goal-record-specific list: goal records are heap data (`TM-1044.j_s4.tex:225`) drawn from the nine power-of-two per-PE free lists (GAP 7). Sizes not in TM-1044 (s4-s6).
- (from VPIM source structures/str_goal_record.psl.c:117-126,189-212, not TM-1044): `_SIZE_OF_SHORT_GR 16`, `_SIZE_OF_LONG_GR 32`, `_SIZE_OF_CTRL_INFO_GR 6`; free-list registers `D_Free_Short_GR_PtrReg`, `D_Free_Long_GR_PtrReg`; allocated with tag HOOK via `b_AllocN`, returned via `b_ReclaimN`. So 10 or 26 argument slots (inference).

#### From ch. 3 (code module, KL1-B/s) and 5j

- Registers named in TM-1044.j_s3.tex: general registers (汎用レジスタ, numbered operands), SSP (suspend-stack pointer, TM-1044.j_s3.tex:1329), CGP (current goal record pointer, TM-1044.j_s3.tex:1854, 1892), a dedicated register holding the committed clause ID for the tracer (commit, TM-1044.j_s3.tex:1343-1345), Program Counter (TM-1044.j_s3.tex:946), work memory slots for spilled registers (save/restore POS, TM-1044.j_s3.tex:1555-1567). Number of argument registers: not in TM-1044 (s3) (register operand field 8 bit (inference); from VPIM source structures/str_klb_reg.psl.c:49-50 `_MAX_ARG_REG 64`, `_MAX_ARG_REG_OF_KLB 32`, not TM-1044). 5j.tex:219-224, 601-608: special registers CCR, PESR (per-PE private), SCR slit-check register (per PE but shared so other PEs can signal).
- Convention (sequence is inference from the individual specs): caller builds a goal record (alloc_goal ARITY → Rgoal; store Reg,Rgoal,POS), obtains Rcode by a get_code-family instruction, then enqueue; callee reads args with load/load_wait from the goal record (Rgoal,POS 0-origin) (TM-1044.j_s3.tex:1376-1383, 1536-1543, 1787-1809).
- alloc_goal(ARITY,Rgoal): allocate a goal record able to hold ARITY args (TM-1044.j_s3.tex:1787-1788). set_caller_code_info(Rgoal): adds caller code info to the goal's environment record, pointing at the NEXT instruction (normally an enqueue); used when calling builtins defined in KL1 (TM-1044.j_s3.tex:1797-1801).
- enqueue(Rgoal,Rcode,ARITY): no pragma; write control info to run Rcode's predicate into the goal record, enqueue on the goal stack (TM-1044.j_s3.tex:1805-1809).
- enqueue_with_priority(Rgoal,Rcode,Rpriority,ARITY): `上の論理プライオリティ(整数)で指定されるゴールスタックにエンキューする。}` (TM-1044.j_s3.tex:1817) = "enqueue on the goal stack designated by the logical priority (integer) in Rpriority". Logical→physical mapping: not in TM-1044 (s3).
- enqueue_to_cluster: enqueue to goal stack of cluster number in Rcluster, i.e. `%throw`; enqueue_resident_to_cluster: add cluster-resident attribute then same; enqueue_emigrant_to_cluster: clear cluster-resident attribute then same as enqueue (TM-1044.j_s3.tex:1825-1833). enqueue_to_processor / resident / emigrant: same with processor number and processor-resident attribute; text also says `%throw` (TM-1044.j_s3.tex:1840-1848).
- execute(Rcode,ARITY)/execute_self(Lpred,ARITY): finish current goal, continue with predicate using the goal record pointed by CGP: 1 count reductions; 2 test slit-check flag; 2a clear → run CGP goal at once; 2b set → enqueue it like `enqueue`, do slit-check processing, then dequeue one goal (maybe a different one) and run it (TM-1044.j_s3.tex:1854-1868).
- proceed(): 1 count reduction; 2 slit check if flag set; 3 dequeue one goal from goal stack and run (TM-1044.j_s3.tex:1872-1881).
- check_heap(Pages): if free heap pages < Pages, stop the predicate, put it back on the goal stack, raise the stop-GC request flag, do slit-check, then dequeue and run a goal (TM-1044.j_s3.tex:1335-1339).
- fail(Lpred,ARITY): report Reduction Fail exception for CGP goal; slit check; dequeue next (TM-1044.j_s3.tex:1934-1944).
- Goal stack structure, free lists, sizes: not in TM-1044 (s3).

#### From ch. 7 (unification, suspend, merger) and ch. 8 (slit check)

- Resume = re-schedule by SENDING the goal to the PE that created it: "リジュームによる再スケジュールは、そのゴールを作成したPE" (TM-1044.j_s7.tex:759-760) = "re-scheduling by resume is done [by sending the goal to] the PE that created the goal". Reasons: goal args/code likely in that PE's cache; child count is cached per PE (s7:761-766). Declared provisional: "などの理由によるが、今後評価/検討の余地がある。" (TM-1044.j_s7.tex:767) = "...but there is room for future evaluation/study".
- Transport = "1 to 1" PE signal. Per-receiving-PE **goal post** in the communication area of the system shared fixed area; senders PUSH goal records on it, so several goals arrive in one event: "受信PE毎に用意したゴールポストにゴールレコードをプッシュすることに" (TM-1044.j_s8.tex:165-165) = "by pushing the goal record onto the goal post provided per receiving PE". 1-to-1 is used for exactly 3 things: reply to auto load-balance request, reply to high-priority-goal request, resume (s8:158-159).
- Receiver (SCR bit 6, goal receive): locks goal post, reads the goal-record link, resets the SCR bit and writes EOL to the post inside the lock, unlocks (s8:392-397); then "受信したゴール(複数の可能性あり)は自PEのそれぞれのプライオリティに対応した" (TM-1044.j_s8.tex:398-398) + "レディゴールスタックに入れる。" (TM-1044.j_s8.tex:399-399) = "received goals (possibly several) are put into the ready goal stack of this PE corresponding to each one's priority". So ready goal stacks are per PE and per priority; a resumed goal keeps its own priority (inference from s8:398-399). No priority boost on resume is mentioned: not in TM-1044 (s7/s8).
- Order of resumed goals: not stated explicitly in TM-1044 (s7/s8). Derivable (inference): hook chain is LIFO (newest suspender at head, s7:150-151, 202-205), it is walked from the variable cell, each goal is pushed on the creating PE's goal post (a stack, s8:162-166), then entered into per-priority ready stacks (also stacks).
- Failed single-suspend CAS: goal's next-link := EOL and the goal is Enqueued (locally) (s7:209). HOOK-HOOK merge fallback also enqueues to the ready goal stack (s7:585).
- D-code goals (list_unifier, vect_unifier, unify_retry, merger retry) go in "通常のユーザゴールと同じレディゴールスタック" (TM-1044.j_s7.tex:433-433) = "the same ready goal stack as ordinary user goals" and are scheduled like user goals (s7:432-436, 497-498).
- Higher-priority goal forked (SCR bit 8): "要因をリセットし、カレントゴールをレディゴールスタックに戻しカレントスタック" (TM-1044.j_s8.tex:424-424) = "reset the cause, return the current goal to the ready goal stack and [update] the current stack entry pointer and current goal stack pointer" (s8:419-425). Names: カレントスタックエントリポインタ, カレントゴールスタックポインタ.
- Priority "pressure model" (s8:241-284), run on timer event. Requirements: no frequent interrupts/polling; middle priorities must not sink under the top one; NO cluster-wide shared global stack (s8:246-250). Variables (s8:257-261): `D_Max_Priority` (reg: highest priority in own ready goal stack), `CL_Max_Priority` (shared memory: believed highest in cluster), `D_Pressure` (reg), `_PRIO_LOW_LIMIT` (negative int), `_PRIO_HIGH_LIMIT` (positive int). Update: `D_Pressure <- D_Pressure + (CL_Max_Priority - D_Max_Priority)` (s8:267). `D_Pressure < _PRIO_LOW_LIMIT` => `CL_Max_Priority := D_Max_Priority` (s8:270-275); `D_Pressure > _PRIO_HIGH_LIMIT` => issue goal-distribution request to other PEs and reset pressure (s8:236-238, 277-279). The first PE noticing the request throws its highest throwable goal, no guarantee it is higher than the requester's (s8:281-284).
- Throwable-goal conditions (s8:376-380): "アイドルゴールの他に3個(可変)以上のゴールがある" (TM-1044.j_s8.tex:378-378) = "there are 3 (tunable) or more goals besides the idle goal"; goal attribute is not processor-resident (s8:379). Auto load-balance request is issued when a PE becomes idle (s8:365). An "idle goal" exists in the stack (s8:378).
- Logical->physical priority mapping, number of levels, goal free lists: not in TM-1044 (s7/s8).

#### From ch. 10 (shoen / foster parent)

- Initial goal priority: TM-1044.j_s10.tex:217 q:`のゴールのプライオリティは、引数で与えられた最高プライオリティとなる。` = "its priority is the maximum priority given as argument".
- Min/max priority are stored in shoen words 11/12 and FP words 16/17 (above). Formula mapping logical -> physical priority, constants: not in TM-1044 (s10). (from VPIM source structures/str_pr_goal_stack.psl.c:205-206, not TM-1044: _MAX_LOGICAL_PRIO 0x7fffffff, _MIN_LOGICAL_PRIO 0x00100000 "excluding idle".)
- Goals come from the "ready goal stack" (TM-1044.j_s10.tex:1162); a non-runnable goal is chained to its FP and the next one is scheduled (TM-1044.j_s10.tex:1181-1182).

### GAP 2: Suspension, resume, D-code

#### From ch. 7 (unification, suspend, merger) and ch. 8 (slit check)

##### Single suspend (HOOK)
- Variable cell UNDF -> `HOOK` pointer to the suspended goal record, whose next-link slot = `EOL` (fig s7:154-168). If goals already wait: PUSH at head: "また、同じ変数を待つゴールが既にあった場合は、そのリンクにプッシュする" (TM-1044.j_s7.tex:150-150) = "if a goal already waits on the same variable, push onto that link" (fig s7:173-195: var HOOK -> new goal [next=HOOK] -> old goal [next=EOL]).
- Procedure (s7:199-210), lock-free, CAS only: Step 1: if cause variable is UNDF, goal next-link := EOL; if it is a pointer (HOOK, MHOOK etc.), goal next-link := that pointer. Step 2: Compare&Swap(ptr = pointer to the variable, "old = 前に読んだ未定義変数の内容," (TM-1044.j_s7.tex:207-207) = "old = contents of the variable read before", new = pointer to goal record). Step 3: success = done; failure = goal next-link := EOL and Enqueue (i.e. retry the reduction; no loop).
- Instructions: `suspend_single` when the cause variable is identifiable; `suspend` or `otherwise` when not (s7:141-143). No cause variable at all => Reduction Failure exception (s7:137-139).

##### Multiple suspend (MHOOK / DREF)
- Two kinds of 2-word records: "2ワードのレコードが割り付けられるが、サスペンドリンクを保持している方を" (TM-1044.j_s7.tex:232-232) = "2-word records are allocated; the one holding the suspend link is [the suspension record]", the one holding the pointer to the goal record is the suspension flag (s7:231-236). One suspension record per cause variable, one shared flag (fig s7:239-287).

Suspension record (サスペンドレコード), fig s7:244-259; word order from VPIM source structures/str_suspend_record.psl.c:106-109 (`_SIZE_OF_SR 2`, `_NEXT_PTR_OFST_SR 0`, `_PTR_TO_FLAG_OFST_SR 1`), not TM-1044:

| # | tag | value / meaning |
|---|-----|-----------------|
| 0 | EOL / HOOK / MHOOK (next-link) | next element of this variable's hook chain (goal record or suspension record) |
| 1 | DREF | pointer to the suspension flag |

Suspension flag (サスペンドフラグ), fig s7:273-278; order from VPIM source structures/str_suspend_record.psl.c:112-115 (`_SIZE_OF_SF 2`, `_GR_PTR_OFST_SF 0`, `_REF_CNT_OFST_SF 1`), not TM-1044:

| # | tag | value / meaning |
|---|-----|-----------------|
| 0 | HOOK (EOL after resume) | pointer to the multiply-suspended goal record |
| 1 | INT | n = number of cause variables (= reference count from suspension records) |

- Variable cell holds `MHOOK` -> suspension record (fig s7:244-258). The goal record reached from the flag always has next-link EOL: "サスペンドフラグから指されるゴールレコードの" (TM-1044.j_s7.tex:306-307) = "the next-link of the goal record pointed to from the suspension flag [is always EOL]".
- Mixed chains: the TAG of each next-link says what the next element is: HOOK => goal record, MHOOK => suspension record (s7:204-205, 772-774). Reply-hook records (inter-cluster) are also chained through their next-link slot (s7:770-772). (From VPIM source structures/str_suspend_record.psl.c:80-99, not TM-1044: MHOOK is the only pointer to a suspension record; DREF = "not dereferenced by the dereferencing global GC".)
- Cause variables are collected by `load_wait` / `read_wait` onto the **suspend stack** (サスペンドスタック), in the processor-local part of the system fixed area, holding pointers to the variables (s7:291-295). `suspend`/`otherwise` checks it: "をチェックし、(重複を除いた) 変数が 2つ以上ある時、多重サスペンド構造を作る。" (TM-1044.j_s7.tex:298-298) = "...and when there are 2 or more variables (duplicates removed), builds the multiple-suspend structure". Stack size: not in TM-1044 (s7).
- Step-by-step locking for building the multiple-suspend structure (CAS per variable, what if one CAS fails): not in TM-1044 (s7).
- EHOOK, EMHOK = HOOK-type cells possibly exported; appear only as variable cells (1-word cells), never inside hook links (s7:303-305).
- MRB on HOOK-type cells (permanent-suspension detection): white = "白いパスでフックした" (TM-1044.j_s7.tex:312-312) = "hooked via a white path", black = hooked via a black path (s7:308-314).

##### Passive (guard) unification
- Never binds; no mutual exclusion needed except for Bind-Hook in suspend: "る処理だけであり、値を書き換えるという処理がないため、排他制御は不要であ" (TM-1044.j_s7.tex:48-48) = "only reads/checks, no value is rewritten, so no exclusion is needed" (s7:44-51).
- Sequences: atomic: deref+bound check (`load_wait`,`read_wait`) -> type (`is_XXX`) -> value (`test_XXX`,`hash_on_XXX`,`jump_on_XXX`) (s7:56-60). Structure: `load_wait`/`read_wait` -> `is_list`/`is_vector` -> `test_arity` (s7:69-73). Var-var: `load_wait` arg1, `load_wait` arg2, `equal` (s7:82-86); compiler emits `klb_equal` both for explicit guard `X=Y` and repeated head variables (s7:106-113).
- `equal` on two structures recurses using the **unify stack** (ユニファイスタック, processor-local fixed area); on overflow it jumps to the instruction's suspend label: "サスペンドラベルに飛ぶことになる。" (TM-1044.j_s7.tex:94-94) (s7:90-94).
- Two identical UNBOUND variables do NOT succeed, they suspend: "が具体化されない限り成功しないことにしている。これは、クラスタ間データが" (TM-1044.j_s7.tex:97-97) = "[even if identical] it does not succeed unless they are instantiated; this is because inter-cluster data..." (s7:96-103; example p(X,X,1) called as p(X,X,2) suspends, not fails).
- Guard built-in with output shared with a head arg: compiled as output to a temp then `Temp = Z` passive unify (s7:115-123).

##### Active (body) unification
- All exclusion is Compare&Swap: "この排他アクセスによるユニフィケーションはVPIMでは全て、" (TM-1044.j_s7.tex:329-330) = "this exclusive-access unification is in VPIM entirely [realised by Compare & Swap]". No per-cell lock bits appear in s7.
- Instructions: `unify_atom`, `unify_integer` (one side atomic, s7:340-342); structure side: Write Mode assumed, structure built first then unified: "Modeであるため、ロック期間が短く単純な前者を選択する。" (TM-1044.j_s7.tex:374-375); sequence `alloc_list`, `put_atom`, `write`, `write`, `unify_bound_value` (s7:379-385); fully-ground structure = structure constant unified with `unify` (s7:390-395); everything else `unify` (s7:401).

| X \ Y | action | cite |
|---|---|---|
| atomic / atomic | compare type+value; unequal => Unification Failure exception | s7:407-408 |
| struct / struct | same pointer => success; else enqueue D-code goal `list_unifier([X1\|X2],[Y1\|Y2]) :- X1=Y1, X2=Y2` or `vect_unifier(N,V1,V2)` (uses `set_vector_element`, counts N down) in the ordinary ready goal stack; strings compared element-wise inline, no D-code | s7:412-436, 456-459 |
| white-path VOID / value | VOID cell reclaimed without binding; collect-value operation applied to the value | s7:465-477 |
| UNDF / value | CAS bind; on CAS failure enqueue D-code goal `unify_retry(X,Y) :- true \| X=Y` (X = ptr to variable, Y = value) | s7:481-498 |
| HOOK-type / value | CAS as UNDF; on success resume the hooked goals | s7:502-505 |
| white VOID / other unbound | VOID reclaimed; other side: white VOID => reclaim; white UNDF or HOOK => CAS-rewritten to VOID; REF-white -> HOOK-white = permanent suspension detected | s7:511-523 |
| UNDF / UNDF | CAS the HIGHER-address cell into REF to the lower; equal pointers => nothing; CAS fail => D-code retry | s7:527-542 |
| UNDF / HOOK-type | CAS UNDF cell into REF to the HOOK cell; CAS fail => D-code retry | s7:546-550 |
| HOOK / HOOK | both white paths => permanent suspension; else list merge below | s7:554-591 |

- Ordering rule: "『アドレスの大きい方のセルから小さい方のセルへ向けてリンクを張る』" (TM-1044.j_s7.tex:531-531) = "link from the cell with the larger address toward the cell with the smaller address" (loop avoidance between PEs).
- CAS-failure policy everywhere: "Dコードゴールを生成してユニファイ再実行を試みる。" (TM-1044.j_s7.tex:540-540) = "create a D-code goal and retry the unify"; D-code is defined in section \ref{subsec-d-code-goal} (not in s7; s7:430-431).
- **HOOK-HOOK = hook-list MERGE (concatenation)**, Ptr1 > Ptr2, Obj1/Obj2 = the HOOK words read (s7:563-591, figs 593-748): (2) CAS cell@Ptr1: HOOK -> REF to cell@Ptr2 (fail => D-code retry). (3) now Obj1's chain is private: "指されているリンクはこのPE だけがたどれることに注意する。" (TM-1044.j_s7.tex:573-573). (4) walk Obj1's chain to its last element (goal record or suspension record) and write Obj2 into its next-link: "『次リンク部』にObj2の値を書き込む" (TM-1044.j_s7.tex:577-577). (5) CAS cell@Ptr2: Obj2 -> Obj1; success => done (result: cell2 -> chain1 -> chain2, i.e. higher-address variable's waiters FIRST). Failure => rewrite that tail next-link to EOL, deref from Ptr2; if now bound, enqueue (resume) Obj1's goals itself: "ペンドゴールをレディゴールスタックにエンキュー(リジューム)する。" (TM-1044.j_s7.tex:585-585) (Obj2's goals are resumed by the binding PE, s7:586-587); if still unbound, go back to (4) with the new Obj2.
- Body built-in / enqueue with unbound input suspending via a D-code goal: not in TM-1044 (s7/s8) beyond the D-code forward reference (s7:430-431).

##### Resume
- Walk the chain via next-link slots of goal records, suspension records and reply-hook records; HOOK link => single resume, MHOOK link => multiple resume (s7:769-774).
- Single: goal next-link := EOL, re-schedule the goal (s7:778-779).
- Multiple (s7:783-804, fig 807-856): resumed when ANY one cause variable is bound: "一つでも変数が具体化されると、他のサスペンド要因の変数が具体化されて" (TM-1044.j_s7.tex:784-784). Steps: reclaim the suspension record; look at flag word 0: HOOK => CAS it to EOL and re-schedule the goal; EOL => already resumed via another variable, do nothing; then decrement the flag count, reclaim the flag at 0: "サスペンドフラグの参照カウントを減じる。この時結果が 0 になれ" (TM-1044.j_s7.tex:802-802). The suspension records still hanging on the other (unbound) variables stay until those are bound (fig s7:818-828) (inference from figure).

#### From ch. 4 (memory, MRB), ch. 5 (D-code), ch. 6 (scheduling)

##### What D-code is (`TM-1044.j_s5.tex:19-42`)
- KL1 programs preloaded into the system code area at VPIM start; a goal created for the runtime's own convenience that uses such code is a "D-code goal". `:19` 「Dコードは、VPIMの起動時にあらかじめシステムコード領域にロードされる」 = "D-code is loaded beforehand into the system code area when VPIM starts".
- Purpose: reuse the ordinary ready goal stack for scheduling; no runtime stack-depth concern; slower, so only for rare events (`:34-42`).
- All D-codes are PUBLIC predicates of one module, the D-code module (also called the `builtin` module, footnote `:239`), referenced from KL1 as `builtin:Pred(...)` or `module#builtin` (`:237-246`). Built-ins defined in KL1 are also public predicates there, registered with the KL1 compiler (`:248-253`).

##### List of D-codes named in s5
| D-code | clause | cite |
|---|---|---|
| per body built-in, e.g. `add/3` | `add(A,B,C) :- wait(A), wait(B) | builtin:add(A,B,C).` | `:60-64` |
| per enqueue-family instr. | `enqueue_with_priority(A,B,C) :- wait(B), wait(C) | builtin:enqueue_with_priority(A,B,C).` (A = goal pointer, NOT waited) | `:93-103` |
| `dcode_unify_retry/2` | `:- true | X = Y.` (after failed Compare & Swap; X = unbound-var pointer, Y = value) | `:116-125` |
| `dcode_list_unifier/2` | `([X1|X2],[Y1|Y2]) :- true | X1=Y1, X2=Y2.` | `:142-145` |
| `dcode_vect_unifier/3` | `(0,V1,V2) :- true|true.` ; `(N,V1,V2) :- N>0 | subtract(N,1,N1), set_vector_element(V1,N1,Elm1,_,NV1), set_vector_element(V2,N1,Elm2,_,NV2), Elm1=Elm2, dcode_vect_unifier(N1,NV1,NV2).` | `:146-155` |
| `dcode_idle_goal/0` | `:- idle | builtin:pims_shut_down.` `alternatively.` `:- true | dcode_idle_goal.` | `:172-177` |
| `dcode_apply/2` | `(Code,Argv) :- true | builtin:apply(Code,Argv).` (on `%throw_goal` receipt) | `:197-204` |
| `dcode_read_module/3` | `(Mod,Ofst,Code) :- wait(Mod) | builtin:module_offset_to_code(Mod,Ofst,Code).` | `:206-215` |
| `dcode_enqueue_cluster_with_spy_mode/5` | `(Cluster,Code,Argv,SpiedCodeV,SpyId) :- integer(Cluster), wait(Code) | builtin:apply_spying(Code,Argv,SpiedCodeV,SpyId)@cluster(Cluster).` | `:217-230` |

##### Body built-in with an unbound input (`TM-1044.j_s5.tex:54-82`)
- Trigger: an input argument is unbound OR an external reference. `:54` 「ボディ部の組込述語を実行する際に、入力となる引数が未定義または外部参照の」 = "when executing a body built-in, if an input argument is undefined or an external reference".
- The built-in is abandoned and a D-code goal made; output arguments get fresh unbound variables, which are also passed to the D-code goal and unified with the result there. `:56` 「この場合、出力引数には未定義変数が渡される。」 = "in this case undefined variables are passed for the output arguments".
- Each body built-in has its own D-code whose guard `wait`s every argument that must be instantiated (`:60-68`).
- Steps: (1) D-code goal created and PUSHED ON THE READY GOAL STACK (not hooked directly); (2) when popped its guard runs: all waited args bound -> body built-in executes; otherwise the goal suspends like any user goal, is resumed by the normal resume path, and runs the built-in after commit (`:70-82`). `:72` 「\item Dコードゴールが生成され、レディゴールスタックに格納される。」
- Record contents: not in TM-1044 (s5). It is an ordinary goal whose code is the preloaded KL1 predicate (`:21-24`) and whose arguments are the built-in's arguments, i.e. standard goal record, COD word -> the D-code predicate in the D-code module, args in arg slots (inference). Priority / foster parent of the D-code goal: not in TM-1044 (s5).
- enqueue family: same mechanism when the code or a pragma value (priority etc.) is unbound (`:88-95`); goal pointers are HOOK-family typed, normally treated as pointers to unbound variables, so `wait` on them would never succeed; enqueue built-ins exist only as D-code (footnote `:104-108`).
- Also: `new_vector` / `new_string` failing for lack of heap set a slit-check cause and enqueue a D-code goal to redo the built-in (`TM-1044.j_s4.tex:294-297`).

##### Idle goal (`TM-1044.j_s5.tex:166-191`)
- Pushed at lowest priority at VPIM start; guard built-in `idle` issues the goal request then loops watching the slit-check register: flag raised -> FAIL -> clause 2 (re-`execute` itself, slit check done before the execute; the idle goal is enqueued before the slit check); user-program termination detected -> commit -> `pims_shut_down` (`:179-191`).

#### From ch. 3 (code module, KL1-B/s) and 5j

- Suspension stack exists (サスペンションスタック / サスペンドスタック), pointer register SSP; reset_ssp is emitted at predicate head only when the predicate may suspend and single-wait optimisation failed: `\DOC{サスペンドスタックポインタ(SSPレジスタ)を初期化する。この命令はサ` (TM-1044.j_s3.tex:1329-1331). Stack size/layout: not in TM-1044 (s3).
- load_wait/read_wait/read_ind_wait: read into Reg, dereference, write back; if unbound variable or external reference, push it (precisely the REF) on the suspension stack and branch to Lsusp (TM-1044.j_s3.tex:1376-1383). read_cst_wait: same, only for external reference (TM-1044.j_s3.tex:1392-1396). *_single variants: identical but do NOT push (single-wait optimisation) (TM-1044.j_s3.tex:1407-1410).
- get_module_wait / get_code_wait: push the variable/external ref through which the module will be bound, branch Lsusp (TM-1044.j_s3.tex:1462-1468, 1495-1499).
- equal(Reg1,Reg2,Lsusp,Lfail): recursive compare; unbound element → push it, branch Lsusp; nesting too deep → also Lsusp (nothing pushed (inference)), so `suspend` finds the stack empty and reports Reduction Fail (TM-1044.j_s3.tex:1646-1655).
- suspend(Lpred,ARITY): 1a stack holds only unbound vars/external refs → write control info (predicate Lpred, ARITY args) into goal record at CGP and hook it on the variables; 1b stack contains something already bound → re-execute: branch to Lpred; 1c stack empty → `トすることができなかったことを意味するので、リダクションフェイルの例外` (TM-1044.j_s3.tex:1901) = "[goal] could not commit, so report reduction-fail exception"; then 2 slit check, 3 dequeue next goal (TM-1044.j_s3.tex:1886-1907).
- suspend_single(Reg,Lpred,ARITY): tests only Reg: unbound/external → hook goal; bound → branch Lpred; then slit check, dequeue (TM-1044.j_s3.tex:1912-1930).
- otherwise(Lpred,ARITY): `サスペンションスタックの状態を調べ、そこが空ならば次命令の処理に進むが、` (TM-1044.j_s3.tex:1949) = "inspect suspension stack; if empty go on to next instruction", else do the same suspend processing as `suspend` (TM-1044.j_s3.tex:1948-1951).
- alternatively(): if external references are on the suspension stack, `それに対する Eager Read を行う。}` (TM-1044.j_s3.tex:1957) = "perform Eager Read on them"; no branch.
- Guard builtins [2xx]: all args in registers, optional fail label; input type checks are done by separate preceding instructions, not inside (TM-1044.j_s3.tex:1978-1984). Body builtins [3xx]: `ボディ組込述語の場合には、ガードと違い、入力引数のデレファレンスや型検` (TM-1044.j_s3.tex:1999) = "unlike guard, a body builtin must do all dereferencing/type-checking of inputs inside the instruction". What it does on an unbound input: not in TM-1044 (s3).
- D-code in TM-1044.j_s3.tex: builtin-predicate module = "Dコードモジュール" (TM-1044.j_s3.tex:1480, 1517). get_code (body, no Lsusp) when the target module is unbound/unimported creates a D-code goal: `を求めるためのDコードを生成する。このDコードは、\\` (TM-1044.j_s3.tex:1506) running builtin predicate_to_code(Module, PredName, PredArity, Code), and Reg is set to the variable that D-code will bind (TM-1044.j_s3.tex:1503-1510). Record contents: not in TM-1044 (s3).
- HOOK/MHOOK record layouts, merge of hooked variables, resume order: not in TM-1044 (s3).

#### From ch. 9 (inter-cluster)

- Guard-side (passive) wait on an external cell: suspend the goal ON the external cell and send %read to the exporter. Quote TM-1044.j_s9.tex:1280-1280 「実行中のゴールを外部参照セルにサスペンドさせて、」 "the running goal is suspended on the external-reference cell" (:1279-1289). Example `consume(X)@cluster(2)` (:1294-1312).
- Case 1, cell single-ref and single wait (TM-1044.j_s9.tex:1324-1336): (1) register a pointer to the cell in the WHITE export table -> "reply-destination ID"; (2) take ID+WEC from the import record and reclaim the record; (3) hook the goal on the cell, cell type := HOOK; (4) send %read.
- Case 2, cell multiple-ref or multiple wait (TM-1044.j_s9.tex:1372-1408): import record cannot be reclaimed; (1) soft-lock cell (EXLOCK); (2) reply ID via white export table; (3) allocate 2-word ReadHook record = import-record pointer + hooked goal; (4) take ID and HALF the record's WEC, keep record; (5) cell := RDHOK -> ReadHook, unlock; (6) send %read.
- Case 3, %read already sent: lock, hook goal on the existing ReadHook record, unlock (TM-1044.j_s9.tex:1445-1453). No second %read.
- %read receipt (TM-1044.j_s9.tex:1459-1543): instantiated datum (atom, int, list, vector, module, code) -> %answer_value (level 1). Variable -> allocate ReplyHook record (variable pointer, reply-destination cell pointer; previous hooked goals go to the goal link) and overwrite the variable with type RHOOK exclusively. External cell -> same ReplyHook, suspended on that external cell, and a %read is forwarded if none was sent yet.
- %answer_value receipt (TM-1044.j_s9.tex:1552-1563): reply ID -> requesting cell; import data; write it into the cell and resume goals hooked on the cell or its ReadHook; reclaim the ReadHook's import record if any and return ID+WEC by %release.
- Body-side (active) unification with an external cell does not suspend the goal; it sends %unify (see GAP 6). Layout of the suspension record itself, resume order: not in TM-1044 (s9).

#### From ch. 11 (GC), ch. 12 (debug), ch. 13 (SCSI)

##### Perpetual suspension found at stop-and-copy GC
- Two detection methods, "as in Multi-PSI": at the stop GC (reporting only the maximal goals) and at once by MRB (TM-1044.j_s12.tex:49-56).
- Detection: suspended goals are not reachable from runnable goals, only runnable goals are roots, so goal counts before and after GC are compared: `括GC前後でゴール数を比較することで永久中断の発生が検出出来る` "by comparing the goal count before and after the GC, the occurrence of perpetual suspension can be detected" (TM-1044.j_s12.tex:283-287). Counters per foster parent: child count (goal_counter, already present for termination detection, so no run-time overhead) and child count during GC (copied_goal_counter) (TM-1044.j_s12.tex:288-296).
- Finding them: the old space is swept. The tag GOAL appears only in the first slot of goal records and merger records: goal record = GOAL white, merger record = GOAL black (TM-1044.j_s12.tex:302-308). `{\sf GOAL}$\circ$が、マージャレコードの場合、先頭スロットに` "GOAL-white [for a goal record]; for a merger record the first slot holds [GOAL-black]" (TM-1044.j_s12.tex:306-308). Copied goals no longer carry GOAL there because the forwarding address overwrote it (TM-1044.j_s11.tex:846-848).
- Sweep-and-copy: while goal_counter > copied_goal_counter: sweep old space; each goal record G found is copied to new space, registered in the maximal-goal candidate table, copied_goal_counter incremented, and everything reachable from G copied (TM-1044.j_s12.tex:346-360). So a perpetually suspended goal and its arguments SURVIVE the GC, because they are reported to the shoen with argument information (TM-1044.j_s12.tex:310-314). The candidate table is the unify stack area in VPIM (a list of old-space goal records on Multi-PSI) (TM-1044.j_s12.tex:367-369). Done by 1 PE (TM-1044.j_s12.tex:318-328).
- Mark-and-sift: for candidates G_j, trace the data from G_j's arguments; any other candidate G_i reached is deleted from the table; visited goal records are marked with type VISIT; old space is used as the trace stack; marks are removed at the end (TM-1044.j_s12.tex:427-479). Only the remaining "maximal" goals are reported (TM-1044.j_s12.tex:484-493). Known bug: a cyclic structure such as X=[X] loops and overflows the stack (TM-1044.j_s12.tex:441-445).
- Maximal goal = member of an equivalence class of perpetually suspended goals not reachable from any other class (TM-1044.j_s12.tex:233-264).

##### Immediate detection by MRB
- The MRB of the object-side HOOK word is given a meaning: on suspension, if the path to the unbound variable was white, HOOK-white is written, if black, HOOK-black: `その未定義変数へのパスが白かった場合 {\sf HOOK}$\circ$, 黒かった場合` "if the path to that unbound variable was white, HOOK-white; if black ..." (TM-1044.j_s12.tex:511-515).
- 6 detected patterns (4 for mergers, REF-white -> MGHOK, where 2 and 4 cannot occur) (TM-1044.j_s12.tex:517-534): (1) `collect_value` on REF-white -> HOOK-white; (2) suspension through a white path on REF-white -> HOOK-white; (3) active unify of two REF-white -> HOOK-white; (4) suspension through a white path on REF-white -> VOID; (5) active unify of REF-white -> HOOK-white with REF-white -> VOID; (6) `%release` received for REF-white -> EHOOK-white. In 2 and 3 two goals are found at once and an exception is raised to the shoen of each (TM-1044.j_s12.tex:536-538).

##### Trace
- Tracer switch as the MRB of the goal record's FPREC word: not in TM-1044 (s12). s12 states the mode test differently: a dequeued goal is in trace mode when its pointer to the environment record has type VECT3: `すなわち、環境レコードへのポインタが{\sf VECT3}であった場合` "i.e. when the pointer to the environment record was VECT3" (TM-1044.j_s12.tex:723-728). Then the trace ID is written into `D_CurrentTraceId`; that register holding type EOL means "not tracing" (EOL cannot be set by a KL1 user) (TM-1044.j_s12.tex:725-728; TM-1044.j_s12.tex:790-790).
- Entry built-in, same specification as the Multi-PSI system: `apply_tracing(Code, Argv, TraceID)` (TM-1044.j_s12.tex:664-675). Checks: already in trace mode -> the built-in itself is reported as a trace exception; in spy mode -> reported unconditionally as a spy exception; Code unbound -> suspend, not code -> Illegal Input; Argv unbound -> suspend, not a vector -> Illegal Input, wrong length -> Arity Mismatch. Otherwise a subgoal is enqueued in trace mode with TraceID attached to its environment record (TM-1044.j_s12.tex:677-698).
- Execution in trace mode: only the reduction is done; subgoals (including unifications and built-ins) are collected in a list and reported, nothing is enqueued or executed (TM-1044.j_s12.tex:701-708). Registers: TSGL (Top of Sub Goal List; source name `D_TraceSubGoalListTop`) and CID (Clause ID) (TM-1044.j_s12.tex:711-721). Unresolved inconsistency in the source: footnote 719 names CID as `D_CurrentTraceId`, yet 725-726 and footnote 790 use `D_CurrentTraceId` for the trace ID / mode flag. The trace-ID reading is the one the code has: `s_GetTraceIdEnvRecord(D_CurrentEnvRecPtr,D_CurrentTraceId)` (from VPIM source interpreter/klb_control.psl.c:923, not TM-1044). On commit in trace mode: TSGL := [] and CID := the clause ID that is an argument of the commit instruction (TM-1044.j_s12.tex:731-733). Each body operation does TSGL := [info | TSGL] (TM-1044.j_s12.tex:735-739). On proceed (and after an execute-type instruction) the trace exception is reported (TM-1044.j_s12.tex:767-784).
- Cost: every body unification / built-in / enqueue must test the mode; without hardware support like Multi-PSI's per-KL1-B-instruction interrupt, the compiler should generate two code variants (traceable-slow, untraceable-fast) (TM-1044.j_s12.tex:787-799).

##### Spy
- Spy flags stored in code: not in TM-1044 (s12). Spy mode = environment-record pointer of type VECT8: `すなわち環境レコードへのポインタが{\sf VECT8}になっていた場合には、` "i.e. when the pointer to the environment record is VECT8" (TM-1044.j_s12.tex:877-880); flag register `D_CurrentSpyId` (EOL = not spying, otherwise the spy ID) (TM-1044.j_s12.tex:870-875).
- `apply_spying(Code, Argv, SpiedPredVector, SpyID)`, same specification as Multi-PSI (TM-1044.j_s12.tex:805-817). SpiedPredVector = {ModName1,PredName1,PredArity1, ModName2,...}; length must be a multiple of 3; elements atoms or integers; an integer in a module/predicate position or an atom in the arity position is a wildcard; an unbound element is Illegal Input, not a suspension (TM-1044.j_s12.tex:832-857).
- In spy mode each subgoal about to be enqueued is tested against the vector: if spied it is reported instead of enqueued; if not it is enqueued in spy mode (inherits the same vector) (TM-1044.j_s12.tex:861-865; TM-1044.j_s12.tex:933-936). Across clusters the D-code goal `dcode_enqueue_cluster_with_spy_mode(Cluster,Code,Argv,SpiedCodeV,SpyId)` re-issues `builtin:apply_spying(...)@cluster(Cluster)` (TM-1044.j_s12.tex:937-945).

### GAP 3: MRB

#### From ch. 4 (memory, MRB), ch. 5 (D-code), ch. 6 (scheduling)

- Bit POSITION within the tag: not in TM-1044 (s4) (s4:51 only: 40-bit word = 8-bit tag + 32-bit value).
- The MRB is carried by the REFERENCE POINTER, 1 bit. `TM-1044.j_s4.tex:347` 「MRB方式とは、参照ポインタにMRBと呼ばれる1ビットの多重参照情報を持たせ、」 = "the MRB scheme gives each reference pointer one bit of multiple-reference information called the MRB".
- Polarity: OFF = white (○) = guaranteed SINGLE reference. `TM-1044.j_s4.tex:348` 「MRBがOFF(MRB$\circ$と表記し、「白い」\index{MRB!がしろい@〜が白い}と読む)」 = "MRB OFF (written MRB○, read 'white')"; `:349` 「ならばデータへの単一参照であることを保証し、」. ON = black (●) = possibly multiple: `TM-1044.j_s4.tex:361` 「MRBがON(MRB$\bullet$と表記し、「黒い」\index{MRB!がくろい@〜が黒い}と読む)」.
- Numeric value: not in TM-1044 (s4). (from VPIM source structures/str_variable_type.psl.c:272-273, not TM-1044) `_MRB_ON = _MRB_1`, `_MRB_OFF = _MRB_0`; (primitives/prim.psl.c:1253-1254, not TM-1044) `_MRB_0 0`, `_MRB_1 1`. So bit 1 = black, 0 = white.
- Reclamation: when a reference known white is consumed, the referenced area is reclaimed ("MRB-GC"); unbound variables are treated a little differently (`:350-354`). Once black, never reclaimed by MRB even if references vanish -> garbage accumulates -> stop (copying) GC also implemented (`:360-366`).
- MRB also used for destructive vector-element update, stream-merge optimisation, export/import optimisation (`:356-358`).

Rules stated in s4 (there is NO rules table in s4; this list is the whole content of `TM-1044.j_s4.tex:368-465`):

| situation | rule | cite |
|---|---|---|
| new variable in body, 2 occurrences (`q(X), r(X,[Car|Cdr])`) | pointers to the cell are ○ | `:378-381` |
| new variable, 3+ occurrences | pointers to the cell are ●; pointers to a new structure with one path are ○ | `:383-387` |
| reference count increases (`p(X) :- true | q(X), r(X).`) | `mark` instruction turns X's MRB ON at commit, the marked value is distributed to both | `:390-395` |
| reference count decreases (`p(X) :- true | true.`) | `collect_value`: if X's MRB is OFF the data can be reclaimed recursively while white; VPIM reclaims the SURFACE only; exception: list CDR followed to depth 3 | `:399-410` |
| head destructuring (`p([X|Y])`, `p({X,Y,Z})`) | `collect_list` / `collect_vector`: reclaim the surface cell/vector if the pointer to it is OFF | `:412-423` |
| dereference | a REF cell reached through an OFF pointer can be reclaimed during deref | `:426-431`, fig `:436-452` |
| path colour | all REF pointers ○ = "white reference path"; any one ● = "black reference path" | `:458-465` |

- Key quotes: `TM-1044.j_s4.tex:395` 「命令により $X$ のMRB を ON にしたものを、$q/1$, $r/1$ に分配する。」; `:406` 「ただしVPIMでは、その表層のみの回収に留めている」 = "but VPIM limits itself to reclaiming the surface only"; `:410` 「例外として、リストのCDR部についてのみ、深さが3までは回収を行う。」 = "as an exception, only for the CDR of a list, reclamation goes to depth 3".
- Reading an element ORs the pointer's MRB into the value read (from VPIM source structures/str_mrb_ope.psl.c:74-99 `s_ReadWithMRBor`, not TM-1044; "PIM/p MRBorRead").
- put_marked_value, write_marked_value, reuse / put_reused_structure: not in TM-1044 (s4) (only `mark`, `collect_value`, `collect_list`, `collect_vector` are named; see the KL1-B chapter).

#### From ch. 3 (code module, KL1-B/s) and 5j

- Polarity/bit position: not in TM-1044 (s3); s3 only uses 白/黒. Tag fields per PSL paper: type, MRB, GC fields (`及びGCフィールドから成る。` 5j.tex:211).
- mark(Reg)[068]: `\DOC{レジスタ{\bf Reg}のMRBを黒くする。}` (TM-1044.j_s3.tex:1667) = "blacken the MRB of register Reg" (register only, no memory access (inference)).
- read / read_wait / read_ind(_wait) on a structure: if Rstruct's MRB is black, blacken MRB of BOTH the element and Reg: `{\bf Reg}のMRBを黒くする必要がある。この後、もし読み込んだデータが未定` (TM-1044.j_s3.tex:1380; rule at 1379-1380 and 1430-1431). load/load_wait (goal args): no MRB rule stated. *_wait variants also dereference and WRITE BACK (デレファレンスと書き戻し, TM-1044.j_s3.tex:1378).
- collect_list(Reg)[070] / collect_vector(ARITY,Reg)[071]: `\DOC{レジスタ{\bf Reg}のMRBが白であれば、それが指すリスト、または、` (TM-1044.j_s3.tex:1673) = "if Reg's MRB is white, reclaim the list / ARITY-element vector it points to" (black: nothing (inference)).
- collect_value(Reg)[073]: if MRB white and Reg points to a structure, float, string etc., reclaim it; `の再帰的な回収は行なっていない。}` (TM-1044.j_s3.tex:1680) = "[VPIM] does not reclaim structure elements recursively" (TM-1044.j_s3.tex:1678-1680).
- reuse_list(Reg)[080] / reuse_vector(ARITY,Reg)[082]: white → reuse as same type/size, i.e. do nothing (VPIM: short vectors only); `もしない。MRBが黒であれば、新たにリスト、または、要素数{\bf ARITY}個の` (TM-1044.j_s3.tex:1688) = "…does nothing. If MRB black, allocate a new list / ARITY-element vector" and set Reg (TM-1044.j_s3.tex:1686-1689).
- reuse_for_list[081] / reuse_for_vector[083]: white → reuse as a DIFFERENT type/size by re-tagging (`グの付け変えを行なう。MRBが黒であれば、新たにリスト、または、要素数` TM-1044.j_s3.tex:1697); black → allocate new, set Reg (TM-1044.j_s3.tex:1695-1698).
- reuse_*_with_elements[084-087]: white → same as plain reuse; black → allocate new AND copy from the old structure the elements that would have been reused in place; FLAGS = 8 bits, bit=1 copy that element, 0 no copy; `コピーする前に要素のMRBを黒くする必要がある。}` (TM-1044.j_s3.tex:1713) = "the element's MRB must be blackened before copying" (TM-1044.j_s3.tex:1706-1713). Which bit ↔ which element: not in TM-1044 (s3).
- alloc_list/alloc_vector: pointer placed in Reg with MRB white: `そこへのポインタ(MRBは白)をレジスタ{\bf Reg}に書き込む。}` (TM-1044.j_s3.tex:1743); alloc_variable/alloc_void: REF pointer, MRB white (TM-1044.j_s3.tex:1748-1749).
- collect_goal(ARITY,Rgoal)[0C1]: reclaims the goal record unconditionally (no MRB test) (TM-1044.j_s3.tex:1792-1793).
- Static MRB rules in code modules: constant-table pointers all black (TM-1044.j_s3.tex:560); module-descriptor pointer black (TM-1044.j_s3.tex:381); header slots holding REF/pointer black, atomic any (TM-1044.j_s3.tex:205-206, 213-214).
- write/store/write_ind, move, put_atom/put_integer, unify*: no MRB behaviour stated (TM-1044.j_s3.tex:1536-1548, 1357, 1727, 1763-1775).

#### From ch. 7 (unification, suspend, merger) and ch. 8 (slit check)

- Structure constants are created black: "MRB が黒として用意される。" (TM-1044.j_s7.tex:397-397) = "prepared with MRB black" (may be called repeatedly, s7:396).
- VOID = variable that had reference count 1 at allocation (type `VOID`) (s7:465-466). Path MRB decides: REF-white -> VOID = true single-reference void; REF-black -> VOID may be multiply referenced, like REF-black -> UNDF (s7:467-472). White VOID vs value: "具体化すること無く回収して処理を終わる。" (TM-1044.j_s7.tex:474-474) = "reclaimed without instantiation"; the value side loses a reference => same operation as collect-value (s7:476-477, 515-516). NOTE s7:475 literally says white VOID is "equivalent in processing to black-path UNDF" (text as printed; s7:471 suggests black VOID was meant) (inference).
- Permanent-suspension detection by MRB: REF-white -> HOOK-white unified with white VOID, or two REF-white -> HOOK-white (s7:521-523, 554-555); white VOID with white MGHOK (s7:1144-1146); white MGHOK with white HOOK (s7:1157-1158); two white MGHOK (s7:1288-1289).
- Merger reuse on white paths: white MHV cell reused as the new MHV cell; white input list cell reused for output (s7:1021-1024); white MGHOK reused instead of allocating (s7:1168-1170, 1376-1377).
- MRB bit position / polarity, MRB KL1-B instructions: not in TM-1044 (s7/s8).

### GAP 4: Data layouts: code module, descriptors, constants, merger

#### From ch. 3 (code module, KL1-B/s) and 5j

##### Code module overall (TM-1044.j_s3.tex:31-57, fig. 79-129)
- Heap structure, usable from PIMOS/KL1 too; spec based on Multi-PSI's. `おけるコードモジュールの仕様はMulti-PSIのものをベースとして以下の条件` (TM-1044.j_s3.tex:35) = "the VPIM code-module spec is based on Multi-PSI's, subject to the following conditions": separate machine-dependent/common parts; info used by PIMOS code-module library in common part; inter-module reference paths gathered in one place (demand loading) (TM-1044.j_s3.tex:37-44).
- 5 parts in address order: module header, other-module reference table, constant table, entry table, code area. Only code area is machine dependent; the rest all tagged words, common to all machines: `種依存になるが、それ以外の部分は全機種に共通の仕様とし、全てタグ付ワー` (TM-1044.j_s3.tex:53). A `CDESC` word (value = Code Area Size) sits just before the code area so stop-the-world GC skips the code area (TM-1044.j_s3.tex:54-56, 121). Pointer to a code module has type `COD` (TM-1044.j_s3.tex:56-57) [sic; the header figure labels word 0 with "MOD→" (TM-1044.j_s3.tex:79) and module constants are `MOD` pointers (TM-1044.j_s3.tex:377, 1452); `COD` = predicate pointer to first instruction (TM-1044.j_s3.tex:913-914)].

##### Module header: 16 tagged words, fixed, all machines (fig. TM-1044.j_s3.tex:79-94; text TM-1044.j_s3.tex:140-244)
`付ワード16個(固定長)から成っている。ここは全機種共通とする。` (TM-1044.j_s3.tex:141) = "consists of 16 tagged words (fixed length); common to all machines."

| # | tag | value / meaning |
|---|---|---|
| 0 (MOD→) | INT | Module Size: whole module incl. itself, in tagged words (converted even if code area is untagged). No REF indirection; MRB any (TM-1044.j_s3.tex:143-147) |
| 1 | INT | GC Maintenance Area Size = header+ext.ref table+const table+entry table, tagged words. NOT read by GC (CDESC controls that); used when VPIM/KL1 copies a module (TM-1044.j_s3.tex:149-157) |
| 2 | ATOM/INT | Package Name: atom, or integer default; spec not fixed, "for now write integer 0" (TM-1044.j_s3.tex:159-166) |
| 3 | ATOM | Module Name (TM-1044.j_s3.tex:168-170) |
| 4 | INT | Number of External Module Reference = count of descriptors (module + predicate descriptors, not words) (TM-1044.j_s3.tex:172-176) |
| 5 | INT | Number of Constants = tagged words in constant table (TM-1044.j_s3.tex:178-181) |
| 6 | INT | Number of Entries (public predicates) (TM-1044.j_s3.tex:183-186) |
| 7 | INT | Start Position of Entry Table: tagged-word offset from module head = KL1 "module element number" as in builtin module_element (TM-1044.j_s3.tex:188-193) |
| 8 | INT | Hash Mask for Entry Table, always 2^n-1, chosen by compiler/assembler (TM-1044.j_s3.tex:195-199) |
| 9 | INT | Compile Information: unused, always integer 0; planned vector; for PIMOS, not read by VPIM; REF allowed, pointer MRB must be black (TM-1044.j_s3.tex:201-206) |
| 10 | INT | Compile Date/Time: Y/M/D/h/m/s in 6+4+5+5+6+6=32 bit, year origin 1990 (1990-2053); not read by VPIM (TM-1044.j_s3.tex:208-214) |
| 11 | INT/ATOM | Version (KL1Comp) |
| 12 | INT/ATOM | Version (PostComp) |
| 13 | INT | Version (Assembler) |
| 14 | INT/ATOM | Version (for User), from `:- version(Int).`; unused slots hold atom `[]`; not read by VPIM; REF allowed, then MRB black (TM-1044.j_s3.tex:216-233) |
| 15 | ??? | Machine Dependent Information; integer 0 if unused; e.g. PIM/p (untagged code area) keeps a vector locating atoms/macro-call addresses for the unloader; not read by VPIM (TM-1044.j_s3.tex:235-244) |

##### Other-module reference table (fig. TM-1044.j_s3.tex:257-306; text TM-1044.j_s3.tex:316-326)
Elements are module descriptors or predicate descriptors (4 tagged words each). Maintained on export to another cluster, stop GC, relink; code-area instructions never need patching (TM-1044.j_s3.tex:318-322). VPIM must type-check on reference and raise an exception if wrong (OS/compiler/linker bugs) (TM-1044.j_s3.tex:324-326).

Module descriptor (モジュール記述子), fig. TM-1044.j_s3.tex:287-294, text TM-1044.j_s3.tex:340-400:
| # | tag | value / meaning |
|---|---|---|
| 0 | MOD (or ATOM) | Pointer to Module. Assembler emits REF→UNDEF (unbound variable); linker binds it to a MOD pointer; reader must dereference, check, suspend if unbound; MRB black (TM-1044.j_s3.tex:374-381). On export copied as REF→EXVAL (EXREF if unlinked); importer fetches the module on first read, goal suspends meanwhile (TM-1044.j_s3.tex:385-393). Demand loading: bound to atom `[]` → exception to PIMOS on first reference (TM-1044.j_s3.tex:396-400) |
| 1 | ATOM | `[]`: discriminates from predicate descriptor, whose word 1 is always INT (TM-1044.j_s3.tex:342-343, 437-438) |
| 2 | ATOM/INT | Package Name (integer 0 = default) (TM-1044.j_s3.tex:345-349) |
| 3 | ATOM | Module Name (TM-1044.j_s3.tex:351-353) |

Predicate descriptor (述語記述子), fig. TM-1044.j_s3.tex:268-275, text TM-1044.j_s3.tex:430-477:
| # | tag | value / meaning |
|---|---|---|
| 0 | COD (or ATOM / INT) | Pointer to Predicate. Assembler/linker write atom `[]`; on first reference VPIM finds the module via word 1, searches its entry table, writes back a COD pointer; MRB any (TM-1044.j_s3.tex:451-460). On export rewritten to INT = predicate offset from module head (machine-dependent unit); importer recomputes COD on first reference (TM-1044.j_s3.tex:464-472). If module unbound/unimported the referencing goal suspends (TM-1044.j_s3.tex:474-477) |
| 1 | INT | Module Information = self-relative address (tagged words) of the module descriptor (TM-1044.j_s3.tex:433-438) |
| 2 | ATOM | Predicate Name (TM-1044.j_s3.tex:440-442) |
| 3 | INT | Predicate Arity (TM-1044.j_s3.tex:444-446) |

##### Constant table / structured constants (TM-1044.j_s3.tex:555-563, fig. 490-545)
One tagged word per structured constant (list, vector, string with no variables) = the POINTER only (e.g. `VECT3`→body, `LIST`→cells); the BODY lives on the heap OUTSIDE the code module. `モジュールの外のヒープ上に展開しておく。ポインタのMRBは全て黒くしてお` (TM-1044.j_s3.tex:560) = "bodies are expanded on the heap outside the module; all pointer MRBs must be black." Code refers to a constant by relative address (base/unit machine dependent), so GC need not patch code (TM-1044.j_s3.tex:561-563).

##### Entry table (fig. TM-1044.j_s3.tex:598-634; text TM-1044.j_s3.tex:649-674)
Hash table (size 2^n; per bucket: | INT Start Position | INT Collision Number |; start position = tagged-word offset from module head) then name table, one 3-word element per public predicate: | ATOM Predicate Name | INT Predicate Arity | INT Predicate Offset (machine-dependent offset from module head, same as in exception messages / builtin module_offset_to_code) |. Same-hash candidates contiguous; empty bucket points at any entry (search is repeat-until: one failing compare, then "predicate not found") (TM-1044.j_s3.tex:663-674). Hash function itself beyond "2^n-1 mask" on name/arity: not in TM-1044 (s3).

##### Code area, VPIM (PIM/s) form (fig. TM-1044.j_s3.tex:682-697; text TM-1044.j_s3.tex:710-727)
All tagged words in VPIM. | INT Table Area Size (tagged words of branch-table area) | multiway-branch tables #0.. | predicate definitions #0.. |.
- Hash branch table (hash_on_integer/hash_on_atom) fig. TM-1044.j_s3.tex:736-777, text 789-821: header | INT Hash Mask (2^n-1, non-zero) | INT Number of Entry (MSB 0=hash_on_integer, 1=hash_on_atom; used by loader/unloader) |; hash table | INT Start Position | INT Collision Number | (machine-dependent self-relative); value table per entry | INT RelAddr to Instruction | ATOM/INT key |. KL1-B instruction's Ltable points after the header (fig. 743).
- Index branch table (jump_on_integer) fig. TM-1044.j_s3.tex:829-841, text 853-872: header | INT 0x00000000 | INT Number of Entry (=Nh-Nl; bias=Nl) |, then INT RelAddr #0..; holes filled with address of next instruction.
- Predicate definition (述語定義) fig. TM-1044.j_s3.tex:881-892, text 905-947 (the "predicate header"):

| # | tag | value / meaning |
|---|---|---|
| 0 | ATOM | Predicate Name |
| 1 | INT | Predicate Arity |
| 2 | INT | Soft Info (compiler-set, for debugger; VPIM does not read) |
| 3 | INT | RelAddr to Module Head (machine-dependent self-relative; used at exception to find module from predicate address) |
| 4 | INT | Code Size (tagged words of following instructions) |
| 5 | VECT0 | Marker: pattern that never occurs in instructions; used to find header from PC at exception. `別できるように{\sf VECT0$\circ$}\index{VECT0@{\sf VECT0}}を使用する。` (TM-1044.j_s3.tex:945) (the ∘ presumably = MRB white (inference)) |
| 6.. | INT (ATOM for atom operands) | machine instructions; COD pointer always points here (TM-1044.j_s3.tex:910-914) |

##### Instruction encoding (TM-1044.j_s3.tex:956-970, format macros TM-1044.j_s3.tex:987-1316)
- Spec is "KL1-B/s", machine language of PIM/s: `る。ここで説明するKL1-Bの仕様はPIM/sの機械語としてのもので、KL1-B/sと` (TM-1044.j_s3.tex:957). Names are the compiler's; VPIM source names may differ: `る名前であり、VPIMのソースコード上では別の名前になっているものがあるの` (TM-1044.j_s3.tex:962). Operand spelling: ALL CAPS = immediate, R+lowercase = register number, L+lowercase = label (relative address); opcodes in hex (TM-1044.j_s3.tex:964-969).
- Each instruction = 1-4 tagged words, tag INT (ATOM for an atom-immediate word). From the picture proportions (value box 120 = fields 60+30+30) a word value is opcode 16 bit + two 8-bit operands (inference; widths are not stated in text). Opcodes are 3 hex digits. Field kinds (inference from macro names TM-1044.j_s3.tex:1288-1316): b = 8-bit (register / POS / ARITY / FLAGS), s = 16-bit (label, Pages, CID, MASK, SIZE), w = full 32-bit INT word (INTEGER, ID, BIAS), a = full ATOM word.
- Layouts, `|` separates fields, `/` separates words: o `OP|-|-`; oR `OP|R|-`; oRR,oBR,oRB,oRF `OP|b|b`; oRRR,oRBR,oRRB,oBRF `OP|b|b / b|-|-|-`; oRRRB `OP|b|b / b|b|-|-`; oS,oL `OP|s`; oLR,oLB `OP|L / b|-|-|-`; oRL `OP|R|- / L|-|-`; oRRL,oBRL `OP|b|b / L|-|-`; oRLB `OP|R|- / L|B|-`; oRRRL,oRBRL `OP|b|b / b|L|-`; oLRL `OP|L / R|L|-`; oRRLL `OP|b|b / L|L`; oRML `OP|R|- / MASK|L`; oIR `OP|-|- / INT32 / R|-|-|-`; oAR same with ATOM word; oIRL,oARL `OP|-|- / imm word / R|L|-`; oRSBL `OP|R|- / SIZE|-|- / BIAS32 / L|-|-`.
- Goal-record operands are stored pre-biased: `… ここでは {\bf POS'} := {\bf POS}$+$5 である。` (TM-1044.j_s3.tex:1374, 1403, 1426, 1534) = "here POS' := POS+5". store and write are the SAME machine instruction (020): `令は{\bf POS}の値を調整することにより共通化することができ、VPIMでは同` (TM-1044.j_s3.tex:1540). Bias 5 is consistent with the 6 control words: the goal pointer addresses the 2nd control word (next-goal pointer, offset 0), the GOAL/arity word is at offset -1 and arg 0 at +5 (from VPIM source structures/str_goal_record.psl.c:126-134 `_SIZE_OF_CTRL_INFO_GR 6`, `_ARITY_OFST_GR -1`, `_NEXT_PTR_OFST_GR 0`, `_ARG0_OFST_GR 5`, not TM-1044).

##### Instruction inventory (name(operands)[opcode hex]; line of \KLB heading)
- 実行準備 (TM-1044.j_s3.tex:1326-1345): reset_ssp()[000] 1326, check_heap(Pages)[001] 1333, commit(ClauseID)[002] 1341
- レジスタ移動 (1355): move(Rsource,Rdestination)[042]
- 読み込み+具体化検査, guard only (1371-1410): load_wait(Rgoal,POS,Reg,Lsusp)[013] 1371, read_wait(Rstruct,POS,Reg,Lsusp)[010] 1372, read_ind_wait(Rstruct,Rpos,Reg,Lsusp)[019] 1385, read_cst_wait(Lconst,Reg,Lsusp)[016] 1390, load_wait_single[014] 1398, read_wait_single[011] 1399, read_ind_wait_single[01A] 1400, read_cst_wait_single[017] 1401
- 読み込み, basically body only (1423-1444): load(Rgoal,POS,Reg)[015], read(Rstruct,POS,Reg)[012], read_ind(Rstruct,Rpos,Reg)[01B] 1434, read_cst(Lconst,Reg)[018] 1439
- モジュール/コード定数 (1460-1519): get_module_wait(Lmodule,Reg,Lsusp)[031], get_module(Lmodule,Reg)[030] 1470, get_module_self(Reg)[033], get_module_builtin(Reg)[032] 1478, get_code_wait(Lcode,Reg,Lsusp)[035] 1483, get_code(Lcode,Reg)[034] 1501, get_code_self(Lpred,Reg)[037] 1512, get_code_builtin(ID,Reg)[036] 1513
- 書き出し (1531-1548): store(Reg,Rgoal,POS)[020], write(Reg,Rstruct,POS)[020], write_ind(Reg,Rstruct,Rpos)[021] 1545
- 作業用メモリ (1559-1567): save(Reg,POS)[040], restore(POS,Reg)[041]
- 型検査 (1580-1588): is_atom[050], is_integer[051], is_floating_point[052], is_list[053], is_vector[054], is_string[055] -- all (Reg,Lfail) (figure caption says "050〜054", TM-1044.j_s3.tex:1586, though is_string is 055)
- 値検査 (1601-1634): test_atom(ATOM,Reg,Lfail)[056], test_integer(INTEGER,Reg,Lfail)[057], test_arity(ARITY,Reg,Lfail)[058], hash_on_atom(Reg,MASK,Ltable)[059], hash_on_integer(Reg,MASK,Ltable)[05A] 1614, jump_on_integer(Reg,SIZE,BIAS,Ltable)[05B] 1623
- 任意データ比較 (1644): equal(Reg1,Reg2,Lsusp,Lfail)[060]
- MRB操作/実時間GC (1665-1713): mark(Reg)[068], collect_list(Reg)[070], collect_vector(ARITY,Reg)[071], collect_value(Reg)[073] 1676, reuse_list(Reg)[080], reuse_vector(ARITY,Reg)[082], reuse_for_list(Reg)[081], reuse_for_vector(ARITY,Reg)[083], reuse_list_with_elements(Reg,FLAGS)[084], reuse_vector_with_elements(ARITY,Reg,FLAGS)[086], reuse_for_list_with_elements(Reg,FLAGS)[085], reuse_for_vector_with_elements(ARITY,Reg,FLAGS)[087]
- 定数書き込み (1723): put_atom(ATOM,Reg)[090], put_integer(INTEGER,Reg)[091]
- 割り付け (1738-1749): alloc_list(Reg)[0A0], alloc_vector(ARITY,Reg)[0A1], alloc_variable(Reg)[0A2], alloc_void(Reg)[0A3]
- アクティブユニフィケーション (1759-1775): unify_atom(ATOM,Reg)[0B0], unify_integer(INTEGER,Reg)[0B1], unify_bound_value(Rbound,Reg)[0B2], unify(Reg1,Reg2)[0B3]
- 実行制御 (1785-1961): alloc_goal(ARITY,Rgoal)[0C0], collect_goal(ARITY,Rgoal)[0C1], set_caller_code_info(Rgoal)[0C3], enqueue(Rgoal,Rcode,ARITY)[0C4], enqueue_with_priority(Rgoal,Rcode,Rpriority,ARITY)[0C5], enqueue_to_cluster(Rgoal,Rcode,Rcluster,ARITY)[0C6], enqueue_to_processor(..,Rprocessor,ARITY)[0C7], enqueue_resident_to_cluster[0C8], enqueue_resident_to_processor[0C9], enqueue_emigrant_to_cluster(Rgoal,Rcode,ARITY)[0CA], enqueue_emigrant_to_processor(Rgoal,Rcode,ARITY)[0CB], execute(Rcode,ARITY)[0D0], execute_self(Lpred,ARITY)[0D1], proceed()[0D2], suspend(Lpred,ARITY)[0D3], suspend_single(Reg,Lpred,ARITY)[0D4], fail(Lpred,ARITY)[0D5], otherwise(Lpred,ARITY)[0D6], alternatively()[0D7], jump(Label)[0D8]
- ガード組込 (1972-1984): builtin_name(Rarg1,Rarg2,…[,Label])[2xx]; ボディ組込 (1995-2000): b_builtin_name(Rarg1,…)[3xx]. Individual builtin opcodes: not in TM-1044 (s3). Opcode 0C2 is unassigned in s3; no instruction named put_marked_value, write_marked_value, put_reused_structure, put_value/get_value, wait_* is specified in TM-1044 (s3) -- the MRB family is exactly mark/collect_*/reuse_*.

#### From ch. 7 (unification, suspend, merger) and ch. 8 (slit check)

##### Merger record (マージャレコード), 8 words (text s7:899-927, fig s7:959-973; offsets 0-7 confirmed in VPIM source structures/str_merger_record.psl.c:73-84, not TM-1044)

| # | tag | value / meaning |
|---|-----|-----------------|
| 0 | GOAL with MRB black (GOAL●) | number of input streams = reference count of the record: "マージャレコード自体の参照カウンタになっている。" (TM-1044.j_s7.tex:904-904) |
| 1 | REF (normally) | pointer to the output variable cell (s7:905-906) |
| 2 | FPREC | foster-parent record of the merger: exception handling, and test whether the merger may reduce (s7:907-908) |
| 3 | MOD | pointer to module (s7:909) |
| 4 | INT | offset in module, pointing at the KL1-B code compiled from `merge/3`; for permanent-suspension / bad-input reports via the shoen report stream (s7:910-914) |
| 5 | INT | processor ID = PE that created the merger (s7:915-916) |
| 6 | INT | priority at creation; only for the substitute goal on exception and the retry goal of a failed output unify: "通常実行時には守られない。" (TM-1044.j_s7.tex:921-921) = "not honoured in normal execution" (s7:917-921) |
| 7 | INT | attribute; only for the substitute goal's priority on exception (s7:922-924) |

- Size: "の8ワードによって構成される。ただし、これ以降の説明では、" (TM-1044.j_s7.tex:926-926) = "consists of 8 words".
- MHV (Merger Hooked Variable) cell = 1 variable cell per input stream holding `MGHOK` -> merger record (s7:928-932, fig 942-958). "MHV セルを白パスで指しているのは、たかだか1本である。" (TM-1044.j_s7.tex:987-987) = "at most one white path points to an MHV cell" (merger's own reference is hidden).
- Goal: n-input merge at constant order independent of n (s7:889-894). Stream = list cells, "(Multi-PSIでも同様である)。" (TM-1044.j_s7.tex:866-866) = "(same on Multi-PSI)".

##### Algorithm = unification of an MHV cell with ...

| other side | action | cite |
|---|---|---|
| NIL (stream closed) | 1 bind MHV to NIL (fail => D-code retry); 2 count -1; 3 "参照カウントが0になったら、出力とNIL をユニファイする" (TM-1044.j_s7.tex:999-999) = "when count reaches 0 unify output with NIL" | s7:993-1000 |
| list [Car\|Cdr] (one message) | 1 alloc a new list cell and a new variable cell; 2 copy Car, new Cdr := REF to the new variable; 3 bind MHV to the input list (fail => D-code retry); 4 alloc new MHV cell, unify with input Cdr; 5 merger output := pointer to new variable; 6 unify OLD output with the new list cell (fail => D-code retry running inside the merger's foster parent). White MHV: step 3 skipped, cell reused as new MHV; white input list: reused for output | s7:1007-1024, figs 1027-1107 |
| vector {I1..Ik} (add streams; `merge/2` semantics, `merge({},Out)` => Out=[]) | 1 alloc k new MHV cells, count += "(要素数-1)増やす" (TM-1044.j_s7.tex:1130-1130) = "(element count - 1)"; 2 bind input MHV to the vector; 3 unify each new MHV with each element | s7:1114-1133 |
| UNDF, VOID | link UNDF cell -> MHV cell; white VOID + white MHV => merger permanent suspension | s7:1141-1149 |
| HOOK-type | 1 CAS MGHOK cell -> REF to HOOK cell (fail => D-code retry; skip if MGHOK path white); 2 alloc (or reuse if white) a new MHV cell; 3 create a D-code goal unifying new MHV with the HOOK variable and PUSH it on the HOOK chain | s7:1163-1173, figs 1176-1278 |
| MGHOK (two mergers) | compare addresses, link larger -> smaller: "アドレスを比較し、大きい方から小さい方に向けてパスを張る。" (TM-1044.j_s7.tex:1291-1291) (no link if either path white); result cell becomes HOOK with TWO hooked unify goals (NewY=Y, NewX=Y), NewX/NewY = fresh MGHOK cells for each merger | s7:1285-1295, fig 1299-1363 |

- The merger itself does no reduction, so foster-parent state is not checked for var/var cases (s7:1148-1149, 1160-1161). When the foster parent is not executable: no output, no stream add/delete, but the MHV cell must still be bound if other paths reference it (s7:1368-1373). Stopped: alloc new MHV (reuse if MRB white), make a goal unifying with it, push it on the foster parent's stopped-goal link (s7:1375-1380). Aborted: "再開されることがないので、出力を行なわない。" (TM-1044.j_s7.tex:1382-1382).
- Vector-merger as a distinct record type, code module / predicate header layouts: not in TM-1044 (s7/s8).

### GAP 5: Shoen and foster-parent records, resources, exceptions

#### From ch. 10 (shoen / foster parent)

##### Concepts (TM-1044.j_s10.tex:13-197)
- Shoen = unit of failure localisation, execution control and resource management; every goal belongs to one shoen, children inherit; shoens nest (TM-1044.j_s10.tex:21-33).
- Control goes through a KL1 "shoen module" (not part of the language: TM-1044.j_s10.tex:62 q:`\footnote{KL1の言語仕様として定めている訳ではない。}` = "not laid down as KL1 language spec"). The control stream is a KL1 program translating each command into a built-in (TM-1044.j_s10.tex:68-70, fig TM-1044.j_s10.tex:79-97).
- Control built-ins take the shoen and a NewShoen output variable bound to the shoen pointer when the built-in finishes; this serialises control (TM-1044.j_s10.tex:72-75).
- Resource unit: TM-1044.j_s10.tex:123 q:`現在はCPU時間の代用としてリダクション数のみを資源として用いている` = "at present only the reduction count is used as resource, in place of CPU time".
- Foster-parent (里親): per-cluster proxy for the shoen; has no control/report stream; exceptions are reported via the shoen's report stream; child shoens hang off the foster-parent by a doubly-linked list (TM-1044.j_s10.tex:154-162). A foster-parent is also placed in the shoen's own cluster and ALL shoen<->foster-parent traffic is inter-cluster messages (network handler decides whether it really goes on the wire) (TM-1044.j_s10.tex:164-168). Created dynamically when a goal arrives in a cluster with no foster-parent for it; disappears when it has no goals/child shoens (TM-1044.j_s10.tex:173-174).
- Both records are heap structures (TM-1044.j_s10.tex:219-221), "on shared memory" (TM-1044.j_s10.tex:426).

##### Shoen record -- 24 words (fig TM-1044.j_s10.tex:438-463, text TM-1044.j_s10.tex:470-554)
TM-1044.j_s10.tex:432 q:`荘園レコードは24ワードからなる構造体` = "the shoen record is a 24-word structure". Tags are NOT given per word in TM-1044; only TM-1044.j_s10.tex:448 q:`第9ワード & CDESC（以下のワードのタグは{\sf DNTC}) \\ \hline` = "word 9: CDESC (words below have tag DNTC)".

| # | tag | value / meaning |
|---|---|---|
| 0 | not given | software-lock flag for the whole shoen record (TM-1044.j_s10.tex:470-471) |
| 1 | not given | shoen ID = offset of the black-export-table entry holding the shoen, with the cluster number concatenated into its upper 3 bits (TM-1044.j_s10.tex:472-474; q TM-1044.j_s10.tex:473 `荘園IDは、荘園を格納した黒輸出表エントリのオフセット値の上位3ビットにクラ`) |
| 2 | not given | pointer to parent foster-parent record (direct parent, always same cluster) (TM-1044.j_s10.tex:475-476) |
| 3 | not given | sibling shoen pointer, right link (siblings under the same parent FP, doubly linked) (TM-1044.j_s10.tex:477-479) |
| 4 | not given | sibling shoen pointer, left link (TM-1044.j_s10.tex:480-482) |
| 5 | not given | foster-parent table: 32-bit bitmap, bit n on = cluster n has a foster-parent; a vector of as many words as the cluster count needs (TM-1044.j_s10.tex:483-486) |
| 6 | not given | resource-requesting FP table: same bitmap form, bit on = that cluster's FP is requesting resource (TM-1044.j_s10.tex:487-490) |
| 7 | not given | report-stream variable (data returned on the report stream is bound to it) (TM-1044.j_s10.tex:491-492) |
| 8 | not given | Ready/Terminated message counter: counts `%ready`/`%terminated` from FPs; exists for message overtaking (TM-1044.j_s10.tex:493-496) |
| 9 | CDESC | marks that tags of following words are meaningless; used by the GC routine (TM-1044.j_s10.tex:497-499) |
| 10 | DNTC | shoen status: two 8-bit parts (TM-1044.j_s10.tex:500-534): (1) transition status, 6 values: started, stopped_by_control, stopped_by_parent, stopped_by_both, aborted, terminated; (2) state flags, 3, not exclusive: resource_report_disallowed (do not report low resource), no_more_external_event (control stream closed), resource_request_fp_existance_flag (some FP is requesting resource) |
| 11 | DNTC | shoen minimum priority: lowest priority a goal in this shoen may take (TM-1044.j_s10.tex:536-537) |
| 12 | DNTC | shoen maximum priority (TM-1044.j_s10.tex:538-539) |
| 13 | DNTC | exception mask pattern: decides whether an exception passed up from an FP is accepted by this shoen (TM-1044.j_s10.tex:540-542) |
| 14 | DNTC | number of unanswered statistics requests (statistics queries waiting to run) (TM-1044.j_s10.tex:543-544) |
| 15 | DNTC | number of child FPs that have not yet answered the statistics query (TM-1044.j_s10.tex:545-546) |
| 16-17 | DNTC | resource consumed by this shoen and its descendants (upper, lower) (TM-1044.j_s10.tex:547-548) |
| 18-19 | DNTC | consumed resource most recently reported to parent FP or report stream (upper, lower) (TM-1044.j_s10.tex:549-550) |
| 20-21 | DNTC | resource on hand: amount that may be consumed for the time being (upper, lower) (TM-1044.j_s10.tex:551-552) |
| 22-23 | DNTC | remaining amount up to the shoen's resource limit (upper, lower) (TM-1044.j_s10.tex:553-554) |

Not in the 24-word figure but introduced later: a stop/start bit table (one bit per cluster) and the WTC value itself (see below) -- TM-1044 (s10) does not say which word holds them (inference: figure is older than TM-1044.j_s10.tex:1639-1647; the VPIM source record is `_SIZE_OF_SH_REC 64`, `_VALID_SIZE_OF_SH_REC 38`, from VPIM source structures/str_shoen_record.psl.c:80-81, not TM-1044).
Status encodings (from VPIM source structures/str_shoen_rec_ope.psl.c:35-51, not TM-1044): _STARTED 0, _STOPPED_BY_CTRL 1, _STOPPED_BY_PARENT 2, _STOPPED_BY_BOTH 3, _ABORTED 4, _TERMINATED 5 under mask 0xff; flags 0x100 rsc_rep_disallowed, 0x200 no_more_external_event, 0x400 rsc_req_fp_existance.

##### Foster-parent record -- 22 words (fig TM-1044.j_s10.tex:564-587, text TM-1044.j_s10.tex:593-661)
TM-1044.j_s10.tex:558 q:`里親レコードは22ワードからなる構造体で各ワードには図\ref{FPrecord_format}に` = "the foster-parent record is a 22-word structure".

| # | tag | value / meaning |
|---|---|---|
| 0 | not given | pointer to the black-import-table entry in which this FP record is registered (TM-1044.j_s10.tex:593-595) |
| 1 | not given | child shoen pointer, right link of the child-shoen doubly-linked list (TM-1044.j_s10.tex:597-599) |
| 2 | not given | child shoen pointer, left link (TM-1044.j_s10.tex:601-603) |
| 3 | not given | link root for stopped goals (TM-1044.j_s10.tex:605) |
| 4 | not given | link root for messages that cannot be sent for lack of WTC (TM-1044.j_s10.tex:606) |
| 5 | not given | software-lock flag for the FP record (TM-1044.j_s10.tex:607) |
| 6 | not given | software-lock flag for the child-shoen link (TM-1044.j_s10.tex:608) |
| 7 | CDESC | following words have tag DNTC (TM-1044.j_s10.tex:572, 609) |
| 8 | DNTC | FP status (TM-1044.j_s10.tex:610-631): (1) logical status, mutually exclusive, 6: reserved, started, stopped, aborted, terminate, aborted-terminate; (2) physical status, independent, 4: resource_exhausted, WTC_requested, resource_requested, child_resource_requested |
| 9-10 | DNTC | FP resource on hand (upper, lower): may be consumed for now (TM-1044.j_s10.tex:632-635) |
| 11-12 | DNTC | consumed resource most recently reported to the shoen in answer to a statistics query (upper, lower) (TM-1044.j_s10.tex:637-640) |
| 13 | DNTC | child count = goals belonging to FP + child shoens of FP; used for termination (TM-1044.j_s10.tex:642-644) |
| 14 | DNTC | child count for detecting perpetually suspended goals at GC (TM-1044.j_s10.tex:646) |
| 15 | DNTC | number of child shoens that have not yet answered the statistics query (TM-1044.j_s10.tex:647) |
| 16 | DNTC | FP minimum priority (TM-1044.j_s10.tex:648) |
| 17 | DNTC | FP maximum priority (TM-1044.j_s10.tex:649) |
| 18 | DNTC | start/stop counter: counts `%start`/`%stop` from the shoen so overtaking still comes out right (TM-1044.j_s10.tex:650-653) |
| 19-20 | DNTC | child-shoen reported consumed resource (upper, lower): sum of statistics answers (TM-1044.j_s10.tex:655-658) |
| 21 | DNTC | consumed-resource collection event count (TM-1044.j_s10.tex:660; no further explanation) |

The FP's own WTC is not a field of this record in the figure; "formally, an FP record is an exported shoen record": shoen record is registered in the EXPORT table, FP record in the IMPORT table, shoen ID = external-reference ID (TM-1044.j_s10.tex:948-956) (inference: WTC lives in the black import/export entries as their WEC). The shoen record never moves to another cluster (TM-1044.j_s10.tex:962). Source FP record is 32 physical / 28 logical words, CDESC size 18 (from VPIM source structures/str_fp_record.psl.c:250-252, not TM-1044). FP codes (from VPIM source structures/str_fp_rec_ope.psl.c:34-50, not TM-1044): _FP_STARTED 0, _FP_RESERVED 1, _FP_STOPPED 2, _FP_ABORTED 3, _FP_TERMINATE 4, _FP_ABORTED_TERMINATE 5; flags 0x100 rsc_exhausted, 0x10000 WTC_req, 0x20000 rsc_req, 0x1000000 child_rsc_req.

##### Related records / lists
- Child-shoen link: ring of shoen records, doubly linked through shoen words 3/4, rooted at FP words 1/2 (TM-1044.j_s10.tex:1112-1113); "no child shoen" = link pointer is EOL (TM-1044.j_s10.tex:1847).
- Stopped / resource-starved goals are chained on the FP record (FP word 3) and re-enqueued on `%start` / `%supply_resource` (TM-1044.j_s10.tex:820-822, 788-790, 1181-1184).
- Message suspend record: one per message kind, the message body is copied in, linked on the FP's WTC-shortage queue (FP word 4) (TM-1044.j_s10.tex:1484-1486). Layout not in TM-1044 (s10).
- Exception record, resource-cache record: not in TM-1044 (s10) as records; cache is "per-PE registers" (below).
- Locks: busy-wait soft lock macros over a hardware lock instruction (TM-1044.j_s10.tex:976-988). Orders: shoen -> export table; import table -> FP; child-shoen link -> FP -> child shoen (TM-1044.j_s10.tex:1001, 1040, 1110). A new FP is published with transition state `_FP_RESERVED`; finders busy-wait until `_FP_STARTED` (TM-1044.j_s10.tex:1055 q:`里親の遷移状態を \verb+_FP_RESERVED+ とする。`; TM-1044.j_s10.tex:1063-1067).

##### States and transitions (TM-1044.j_s10.tex:308-420, 799-929)
- The state-transition figures (captions TM-1044.j_s10.tex:367, 389, 413), the hierarchy / shoen-FP / WTC / resource-flow figures (TM-1044.j_s10.tex:51, 194, 266, 750) and the stop/start-bit state diagram with its legend (TM-1044.j_s10.tex:1707-1709, 1777-1779, empty \vspace{18cm}) are blank placeholders in the LaTeX: diagrams not recoverable from s10, only the prose rules below exist.
- Shoen: started; stopped (stopped_by_control / stopped_by_parent / stopped_by_both); aborted (from abort until termination); terminated (TM-1044.j_s10.tex:313-329). FP: started, stopped, aborted, terminated (TM-1044.j_s10.tex:331-341). More internal states exist (footnote TM-1044.j_s10.tex:310-311). Goals may run only in started; aborted/terminated never return (TM-1044.j_s10.tex:417-420). Runnable = shoen not stopped AND remaining resource > 0 (TM-1044.j_s10.tex:1164 q:`(荘園が止められていなくて、かつ資源残量 $>0$)で`).
- start (start_shoen): clear stopped_by_control; by_control->started, by_both->by_parent; any other state is an implementation error because the shoen module forbids start on started / stop on stopped (TM-1044.j_s10.tex:806-816). On becoming started send `%start` to every known FP (TM-1044.j_s10.tex:817-818). FP: state := started, goals chained while stopped go back to the goal queue, clear stopped_by_parent in all child shoens (by_parent->started, by_both->by_control), which in turn send `%start` to their FPs (TM-1044.j_s10.tex:820-829).
- stop (stop_shoen): add stopped_by_control; started->by_control, by_parent->by_both; on becoming by_control send `%stop` to all known FPs (TM-1044.j_s10.tex:831-841). FP: state := stopped, then interrupt every PE in the cluster; taken at the reduction boundary (slit check); TM-1044.j_s10.tex:847 q:`していた場合には、スケジュールされたゴールは里親につながれ実行されない。` = "the scheduled goal is chained to the FP and not executed". Child shoens get stopped_by_parent and send `%stop` on (TM-1044.j_s10.tex:843-857).
- abort: shoen := aborted, `%abort` to all known FPs. FP := aborted, PEs interrupted, at slit check TM-1044.j_s10.tex:867 q:`変化していた場合には、スケジュールされたゴールは実行されずに捨てられる。` = "scheduled goals are discarded unexecuted". No child shoens: after every PE has checked and written its cached resource back, FP sends `%terminated` carrying its final consumed resource. With child shoens: all are set aborted and send `%abort`; FP sends `%terminated` only when all child shoens have terminated (TM-1044.j_s10.tex:859-878).
- stop/abort reach a PE's current goal stream only at the slit check (so not mid-reduction: inference), where the PE acts as if a goal of a different FP had been scheduled (TM-1044.j_s10.tex:1218-1224).
- Start/stop overtaking: FP counts logically-wrong `%start`/`%stop` and changes state only when a correct message arrives with count 0 (TM-1044.j_s10.tex:1379-1383; worked example TM-1044.j_s10.tex:1344-1403). Multi-PSI simply discarded such messages (TM-1044.j_s10.tex:1340-1342).
- "Next-generation FP" problem (old `%stop` hits a new FP in the same cluster, TM-1044.j_s10.tex:1549-1613): fixed with a per-cluster stop/start bit table in the shoen (ON = an FP there will stop in finite time, OFF = will start) plus `%NAKstop`/`%NAKstart` (TM-1044.j_s10.tex:1629-1652). Rules: started->stopped: send `%stop` to known-FP clusters whose bit is OFF, set ON; stopped->started: `%start` to bit-ON clusters, set OFF (TM-1044.j_s10.tex:1659-1669). New FP recognised (`%ready`): shoen stopped & bit OFF -> send `%stop`, set ON; stopped & ON -> nothing; started & OFF -> nothing; started & ON -> send `%start`, set OFF (TM-1044.j_s10.tex:1672-1683). `%NAKstop`: bit ON -> OFF, and if shoen stopped and an FP is known there, resend `%stop` and set ON; bit OFF -> send `%stop` (TM-1044.j_s10.tex:1688-1693). `%NAKstart`: bit ON -> send `%start`; bit OFF -> ON, and if shoen started and FP known, send `%start`, set OFF (TM-1044.j_s10.tex:1694-1699).

##### Resource accounting (TM-1044.j_s10.tex:113-149, 664-797, 1139-1199)
- Reduction cycle per PE: execute goal; count consumed resource; child-count maintenance; slit check; schedule next goal incl. FP state check (TM-1044.j_s10.tex:670-677). No runnable goal -> idle goal (TM-1044.j_s10.tex:708-709).
- The consumer is the FP: each reduction is subtracted from the FP's resource, via a cache: TM-1044.j_s10.tex:690 q:`大きくなるため、里親の資源の一部をPEごとのレジスタにキャッシュしてい` = "part of the FP's resource is cached in per-PE registers". Before running a goal a fixed amount ("cache unit") is taken from its FP; consecutive goals of the same FP decrement the cache; when it runs out, refill from the FP; if the FP has none the goal is chained to the FP record as a suspended goal and the next goal is scheduled (TM-1044.j_s10.tex:1177-1184). FP record fields are maintained only when the current goal's FP changes (TM-1044.j_s10.tex:1145 q:`具体的にはカレントゴールの里親が切り替わるときにのみ、`): write the cache back to the old FP, fetch from the new one and check its runnable state (TM-1044.j_s10.tex:1185-1188).
- FP remaining resource below "a fixed value" -> `%request_resource` to the shoen (TM-1044.j_s10.tex:716-719). Requests flow FP -> shoen -> parent FP -> parent shoen; supply flows the other way except at termination (TM-1044.j_s10.tex:721-727).
- Shoen keeps (a) limit remainder = what it may still obtain from its parent FP, decremented on each grant; (b) on-hand resource, a temporary store that FP requests are served from and returned resource goes into (TM-1044.j_s10.tex:761-770). On `%request_resource` (TM-1044.j_s10.tex:772-786): on-hand sufficient -> `%supply_resource`, in a fixed unit (TM-1044.j_s10.tex:779 q:`る資源の単位は ResourceSupplyUnitと呼ばれる一定の値である。`); limit left but nothing on hand -> take from parent FP (which sends `%request_resource` to the parent shoen if empty); no limit left -> resource_low on the report stream (actually reported somewhat before the limit is reached: footnote TM-1044.j_s10.tex:766-767).
- FP on `%supply_resource`: if nothing else blocks it, all goals chained for lack of resource go to the goal queue; unsatisfied child shoens are given resource and they send `%supply_resource` to their unsatisfied FPs (TM-1044.j_s10.tex:788-793).
- add_resource raises the LIMIT remainder only, not the on-hand amount (TM-1044.j_s10.tex:880-886). Unused resource goes back to shoen / parent FP at termination; at shoen termination the surplus (limit minus consumed) is reported on the report stream (TM-1044.j_s10.tex:795-797).
- Statistics (ask_statistics / built-in shoen_statistics): shoen sends `%ask_statistics` to all known FPs, reports the total on the report stream when all have answered; further requests are only counted meanwhile (TM-1044.j_s10.tex:891-905). FP: all PEs of the cluster synchronise and write caches back (after child shoens were queried), answer with `%answer_statistics` (TM-1044.j_s10.tex:907-923). Guarantees: monotone non-decreasing; exact only for a terminated shoen (TM-1044.j_s10.tex:144-149). Cluster-wide synchronisation is needed only for GC and this survey, mutually excluded by a flag; a clash postpones to the next sync point (TM-1044.j_s10.tex:1236-1251, 1274-1276).
- Numbers: TM-1044 (s10) gives NO numeric value for ResourceSupplyUnit, cache unit, request threshold or resource_low threshold. (from VPIM source functions/f_fp_main.psl.c:1966-1969, not TM-1044: _RSC_SUPPLY_UNIT 0x01000000, _RSC_CACHE_UNIT 0x2000, _RSC_THROW_GOAL_UNIT 0x10000, _RSC_ENOUGH_TO_CACHE_UNIT 0x8000.) Resource quantities are double-word (upper/lower) everywhere.

##### Goal counting / termination (TM-1044.j_s10.tex:225-302, 1190-1199, 1817-1849)
- Child count: TM-1044.j_s10.tex:231 q:`チャイルドカウントはその里親に属するゴールの総数と子荘園の総数との` = "the child count is the sum of the goals belonging to the FP and its child shoens". Up on receipt of a thrown goal and on creating a goal or child shoen, down on goal/child-shoen end; at 0 the FP terminates and sends `%terminated` (TM-1044.j_s10.tex:232-236). After abort it generally does not reach 0 (TM-1044.j_s10.tex:238-241).
- Per-PE cache: PE child count := 0 before running; +1 per goal enqueued, -1 when the goal ends; written back and cleared when the FP changes (TM-1044.j_s10.tex:1193-1199).
- Other "work" also counted in the child count: child shoens, deferred statistics sync, handling of a message from the shoen (count +1 for the duration), statistics request-to-answer; non-goal work additionally has one dedicated counter so that after abort only goals remain to be drained (TM-1044.j_s10.tex:1830-1848, 1864-1867). The executing goal holds a reference on its FP, so reading single FP fields needs no lock (TM-1044.j_s10.tex:1082-1085). An aborted FP with only goals left is removed from the import table but the record is kept until every goal has been scheduled (TM-1044.j_s10.tex:1076-1078).
- WTC (Weighted Throw Count): TM-1044.j_s10.tex:273 q:`WTCは、一つの荘園とその里親との間でトータルが0になる値で、里親の生成時に` = "WTC sums to 0 over a shoen and its FPs"; a fixed amount is given to an FP at creation and subtracted from the shoen (TM-1044.j_s10.tex:273-274). Sender subtracts the WTC it attaches, receiver adds (TM-1044.j_s10.tex:276-277). A terminating FP returns all its WTC; a message arriving where no FP exists is sent back to the shoen (TM-1044.j_s10.tex:278-279). Shoen terminates when its WTC returns to 0 (TM-1044.j_s10.tex:288-294). TM-1044.j_s10.tex:286 q:`ないことを保証するために、全てのクラスタ間メッセージにWTCが付加されている。` = "WTC is attached to all inter-cluster messages" (VPIM-specific, against overtaking). The shoen issues WTC freely until counter overflow; an FP must ask (TM-1044.j_s10.tex:1447-1449). Shoen record reclamation needs BOTH all WTC back AND `b_remove_shoen` (TM-1044.j_s10.tex:1024-1026). No WTC numbers in TM-1044 (s10). (from VPIM source functions/f_shoen_control.psl.c:45 _INIT_SHOEN_WTC 0x01000000; structures/str_trade_init.psl.c:409-411 _SHOEN_WTC_UNIT 1, _SUPPLY_WTC_UNIT 0x01000000; not TM-1044.)

##### Exceptions (TM-1044.j_s10.tex:1877-2277)
- The raising goal's FP is known (also for perpetual-suspension goals found in GC, via the FP pointer in the goal record: footnote TM-1044.j_s10.tex:1883-1884). TM-1044.j_s10.tex:1885 q:`このため、例外発生時の情報(コード、引数など)は適当な形のベクタにまとめられて里` = "the information (code, args...) is packed in a vector and sent as a message from the FP to the shoen", with the exception's tag (TM-1044.j_s10.tex:1885-1887).
- Shoen tests the tag against its mask: not masked -> reported on this shoen's report stream; masked -> passed through the parent FP to the ancestor shoen (TM-1044.j_s10.tex:1890-1897). Mask = bitmap given at shoen creation (TM-1044.j_s10.tex:1899).
- Replacement goal: the implementation adds two fresh variables for code and argument vector; the user binds them to run a substitute goal; TM-1044.j_s10.tex:1908 q:`せたゴールは実行が終了したものとして捨てられる。` = "the raising goal is discarded as if finished" (TM-1044.j_s10.tex:1901-1908).
- Tag word 32 bits (fig TM-1044.j_s10.tex:1927-1936): bits 31-16 language-defined (KL1), bits 15-8 PIMOS, bits 7-0 user. Language-defined bit positions (table TM-1044.j_s10.tex:1955-1972): illegal_input 16; range_overflow 17; out_of_bounds 18; integer_overflow 19; integer_zero_division 20; invalid_floating_point_operation 21; arity_mismatch 22; undefined_module 23; undefined_predicate 23; illegal_merger_input 24; reduction_failure 25; unification_failure 26; perpetual_suspension 27; merger_perpetual_suspension 28; trace 29; spy 29; (reserved) 30; etc 31. `raise` takes the tag as an argument, so no fixed bit (TM-1044.j_s10.tex:1977-1978).
- Report-stream exception message, always a 5-element vector (TM-1044.j_s10.tex:1987 q:`{\bf \{shoen\#exception, ExpNumber, ExpInfo, NewCode, NewArgv\}}`): shoen#exception = number marking an exception message; ExpNumber = kind number; ExpInfo = per-kind vector; NewCode/NewArgv = variables to be bound "on the PIMOS side" to the substitute predicate's code and argument vector (TM-1044.j_s10.tex:1989-1993). Numeric values of shoen#exception / ExpNumber: not in TM-1044 (s10) ((from VPIM source structures/str_shoen_rec_ope.psl.c:80, not TM-1044: _EXCEPTION_REP 100)).
- ExpInfo common elements, in this order (TM-1044.j_s10.tex:2001-2075):
  - ClsAndProc: one word, bits 31-16 cluster number, bits 15-0 processor number within cluster (fig TM-1044.j_s10.tex:2016-2022).
  - Predicate, 4 forms (TM-1044.j_s10.tex:2035-2050): `Code` (raised in a KL1-defined predicate); `{Code, CallerMod, CallerOffs}` (in a KL1-defined built-in); `{KlbID, OriginMod, OriginOffs}` (in a firmware-defined built-in); `{KlbID, OriginMod, OriginOffs, CallerMod, CallerOffs}` (firmware built-in called from a KL1-defined built-in). KlbID = KL1B-instruction-ID of the KL1-B instruction for the built-in (TM-1044.j_s10.tex:2054 q:`対応するKL1-B命令に付与されている番号KL1B-instruction-IDを使用する。こ`). OriginMod/OriginOffs = module pointer + offset from module head of the start of the machine-instruction sequence of that built-in (TM-1044.j_s10.tex:2056-2061). CallerMod/CallerOffs = same pair for the enqueue-family KL1-B instruction in the user module that called the KL1-defined built-in (TM-1044.j_s10.tex:2062-2068).
  - ArgVect: vector of ALL arguments of the raising predicate (TM-1044.j_s10.tex:2069-2071).
  - ArgPos: position of the offending argument, TM-1044.j_s10.tex:2074 q:`具体的には、0オリジンの番号で指定することにする。` = "0-origin".
- ExpInfo per kind: Illegal Input `{ClsAndProc, Predicate, ArgVect, ArgPos}` (body built-in, wrong input type; TM-1044.j_s10.tex:2079-2082). Range Overflow same 4 (value out of range, other than an element index; TM-1044.j_s10.tex:2087-2091). Out of Bounds same 4 (element index; TM-1044.j_s10.tex:2096-2100). Integer Overflow `{ClsAndProc, Predicate, ArgVect}` (TM-1044.j_s10.tex:2105-2108). Integer Zero Division same 3 (TM-1044.j_s10.tex:2113-2116). Arity Mismatch same 3 (apply-family and create_shoen-family; TM-1044.j_s10.tex:2121-2125). Illegal Merger Input `{ClsAndProc, Predicate, Input, Merger}`, Predicate in KlbID form with KlbID = merge (TM-1044.j_s10.tex:2130-2138; commented-out remark "not yet implemented" TM-1044.j_s10.tex:2131). Reduction Failure `{ClsAndProc, Predicate, ArgVect}` (TM-1044.j_s10.tex:2142-2145). Unification Failure `{ClsAndProc, DataX, DataY}` = the two data being unified -- no predicate, no ArgVect (TM-1044.j_s10.tex:2150-2156). Raised `{ClsAndProc, Info, Data}` = the raise built-in's arguments (TM-1044.j_s10.tex:2160-2166). Perpetual Suspension `{ClsAndProc, Type, Predicate, ArgVect}` or `+ Collector` (Type = detection-kind number; Collector, Predicate-format, = predicate that tried to collect the HOOK variable, only when found by real-time GC; TM-1044.j_s10.tex:2170-2180). Merger Perpetual Suspension `{ClsAndProc, Type, Predicate, Inputs}` / `+ Collector` (TM-1044.j_s10.tex:2184-2199). Trace `{ClsAndProc, ListOfTraceID, SubGoalInfoList, ClauseInfo}`; ListOfTraceID = length-1 list of the TraceID given as 3rd arg of apply_tracing; ClauseInfo = compile-time clause ID of the committed clause (TM-1044.j_s10.tex:2203-2214). SubGoalInfo forms (TM-1044.j_s10.tex:2221-2243): `{KlbID, DataX, DataY}` unification; `{KlbID, ArgVect}` firmware built-in; `{KlbID, Code, ArgVect}` call; `{KlbID, Code, ArgVect, Priority}` (enqueue_with_priority, logical priority); `{KlbID, Code, ArgVect, Cluster}` (enqueue_to_cluster / enqueue_resident_to_cluster); `{KlbID, Code, ArgVect, Processor}` (enqueue_to_processor / enqueue_resident_to_processor) (TM-1044.j_s10.tex:2253-2260). Spy `{ClsAndProc, SpyID, SubGoalInfo, Module, Offset}`, SpyID = 3rd arg of apply_spying, Module/Offset = position of the calling enqueue-family instruction (TM-1044.j_s10.tex:2264-2277).
- No ExpInfo subsection for invalid_floating_point_operation, undefined_module/predicate, etc: not in TM-1044 (s10).

##### Report stream / control stream
- Control-stream commands shown: start, stop, abort, add_resource(Res) (fig TM-1044.j_s10.tex:81-92, "..." continues), plus ask_statistics (TM-1044.j_s10.tex:891-893). State flags imply a "close" and a resource-report allow/disallow command (TM-1044.j_s10.tex:525-530) (inference).
- Report-stream contents named in TM-1044.j_s10.tex: resource_low (TM-1044.j_s10.tex:766, 784), surplus resource at termination (TM-1044.j_s10.tex:796-797), total consumed resource for ask_statistics (TM-1044.j_s10.tex:902-903), exception vector (TM-1044.j_s10.tex:1987). Formats of started/terminated/aborted/resource_low etc.: not in TM-1044 (s10). (from VPIM source structures/str_shoen_rec_ope.psl.c:64-80, not TM-1044: report codes started 1, stopped 2, aborted 3, rsc_added 4, stat_started 5, rsc_rep_allowed 6, terminated 7, rsc_low 8, stat 9, return_rsc 0xa, exception 100.)

##### Shoen built-ins named in s10
- `create_shoen/5` (TM-1044.j_s10.tex:202); shoen and its FP are created in the executing cluster; initial goal built from the code + argument vector and enqueued as the FP's first goal (TM-1044.j_s10.tex:214-216). Commented-out argument list (TM-1044.j_s10.tex:204-212): Code, Argv, MinPrio, MaxPrio, MinNode, MaxNode (node range for throwing goals), ExcepMask, Report, Shoen -- 9 names against arity 5 (unresolved in s10). Internal name `b_create_shoen` (TM-1044.j_s10.tex:1008); Shoen output is instantiated only after the built-in body runs (TM-1044.j_s10.tex:1010-1014).
- `start_shoen(Shoen,NewShoen)`, `stop_shoen(Shoen,NewShoen)`, `abort_shoen(Shoen,NewShoen)`, `add_shoen_resource(Shoen,Res,NewShoen)` (TM-1044.j_s10.tex:81-92); `shoen_statistics` (TM-1044.j_s10.tex:893); `b_remove_shoen` (TM-1044.j_s10.tex:1025); `raise` (TM-1044.j_s10.tex:1977, args Info, Data TM-1044.j_s10.tex:2163-2165); `apply_tracing` (3rd arg TraceID, TM-1044.j_s10.tex:2210-2211); `apply_spying` (3rd arg SpyID, TM-1044.j_s10.tex:2271).

#### From ch. 7 (unification, suspend, merger) and ch. 8 (slit check)

- Slit-check events touching foster parents: FP status check (bit 4: an FP became stopped/aborted; if current goal's FP not executable, write cached resources back to the FP and reschedule the goal, s8:350-356); FP statistics gathering (bit 3 + slot type `_FP_IN_EVT_ABORTED` / `_FP_IN_EVT_ASK_STAT` / `_FP_IN_EVT_ANS_STAT`, slot value = pointer to target FP; cached resource written back; ASK/ANS busy-wait until the total is fixed; ABORT no wait/no signal, s8:320-345); deferred gathering (bit 9, internal event stack, s8:430-440); resource cache exhausted (bit 11: per-PE cached resource hit 0 and the FP also had 0; reschedule current goal, s8:465-470). Resources are cached per PE and written back on demand.

#### From ch. 9 (inter-cluster)

Shoen <-> foster-parent messages; every one carries `DNTC kind; DNTC shoen ID (the shoen's external reference ID); DNTC WTC` then the extra fields below, then EOM. Resource is always 2 words (upper, lower) (TM-1044.j_s9-message.tex:582-582).
| message | direction / purpose | extra fields after shoen ID, WTC | cite |
|---|---|---|---|
| %start | shoen -> FP, (re)start | — | TM-1044.j_s9-message.tex:382-404 |
| %stop | shoen -> FP, stop | — | TM-1044.j_s9-message.tex:412-434 |
| %abort | shoen -> FP, abandon | — | TM-1044.j_s9-message.tex:442-464 |
| %supply_resource | shoen -> FP, supply requested resource | — (figure has no resource-amount word) | TM-1044.j_s9-message.tex:472-495 |
| %ask_statistics | shoen -> FP | — | TM-1044.j_s9-message.tex:503-526 |
| %supply_wtc | shoen -> FP | WTC word = WTC supplied | TM-1044.j_s9-message.tex:534-557 |
| %terminated | FP -> shoen, all work done | order: shoen ID; sender cluster no.; WTC; returned resource upper, lower; consumed resource upper, lower | TM-1044.j_s9-message.tex:565-603 |
| %ready | FP -> shoen, new FP created and ready | sender cluster no. | TM-1044.j_s9-message.tex:611-637 |
| %request_wtc | FP -> shoen | sender cluster no. | TM-1044.j_s9-message.tex:645-671 |
| %return_wtc | FP -> shoen | sender cluster no. | TM-1044.j_s9-message.tex:679-704 |
| %request_resource | FP -> shoen | sender cluster no. | TM-1044.j_s9-message.tex:712-738 |
| %answer_statistics | FP -> shoen | resource upper, lower (statistics = consumed resource only, for now); sender cluster no. | TM-1044.j_s9-message.tex:746-779 |
| %return_resource | FP -> shoen | resource upper, lower; sender cluster no. | TM-1044.j_s9-message.tex:787-819 |
| %exception | to shoen, exception during goal execution | exception number; pointer to exception-info vector; pointer to new code (run instead); new argument vector | TM-1044.j_s9-message.tex:827-862 |
- Shoen ID on the wire = external reference ID of the shoen, tag `INT○/●` in %throw_goal (TM-1044.j_s9-message.tex:28-29, :59-59). WTC semantics, shoen/FP record fields: not in TM-1044 (s9).
- A foster parent is created on demand at receipt of %throw_goal / %unify and announced by %ready (TM-1044.j_s9.tex:1132-1134, :1725-1727).

#### From ch. 11 (GC), ch. 12 (debug), ch. 13 (SCSI)

- Perpetual-suspension report format: not in TM-1044 (s12); both detections refer to the shoen-exception section (TM-1044.j_s12.tex:491-493; TM-1044.j_s12.tex:536-538). Stated here: the goal is reported to its shoen together with its argument information (TM-1044.j_s12.tex:310-312).
- Trace exception, sent to the shoen's report stream on proceed (TM-1044.j_s12.tex:776-784): `を荘園のレポートストリームに報告する。` "is reported to the shoen's report stream" (TM-1044.j_s12.tex:784-784).
 Tuple: {message number "exception", exception number "trace exception", {cluster number and processor number, list of trace IDs, subgoal list, clause ID}, predicate code to execute instead, argument vector of that predicate}.
- Subgoal-info shapes; the leading number is always the KL1B-instruction-ID (TM-1044.j_s12.tex:741-773): active unification {id, {DataX, DataY}}; built-in other than enqueue-type {id, argument vector}; enqueue-type {id, code, argv} or with a 4th element = logical priority / cluster number / processor number; execute-type {id, code, argv}.
- Spy exception (TM-1044.j_s12.tex:882-890): {message number "exception", exception number "spy exception", {cluster number and processor number, spy ID, subgoal info}, code to execute instead, argv to execute instead}. Subgoal info: enqueue-type and execute-type as above; apply: {id of apply, vector of apply's arguments}; `apply_tracing`, `apply_spying`, `create_shoen`, `create_profiling_shoen` are ALWAYS reported as {id, argument vector} (TM-1044.j_s12.tex:893-930).
- Numeric message / exception codes: not in TM-1044 (s12). Receiver: the PIMOS debugger ("listener"), which re-issues `apply_tracing/3` on branches to keep tracing and `apply/2` on the others (TM-1044.j_s12.tex:69-73).
- Built-in argument exceptions named in these files: Illegal Input, Arity Mismatch (TM-1044.j_s12.tex:684-689), Range Overflow (TM-1044.j_s13-3.tex:72-75).

### GAP 6: Inter-cluster: tables, WEC, messages

#### From ch. 9 (inter-cluster)

Notation in figures: `\wordbox{x}{y}{TAG}{value}` = one word (tag, value), higher y = earlier word (TM-1044.j_s9-fig-macro.tex:26-38); `\shoryakubox` = elided words (:42-53). Tag suffix `$\circ$` (○) = MRB white/off, `$\bullet$` (●) = MRB black/on (inference: convention defined outside s9); `DNTC` = tag don't-care. Authors: 仲瀬, 高木 (TM-1044.j_s9.tex:9-9).

##### Terms and the external-reference path
- Export = making local data referable from another cluster; import = the converse; the cross-cluster reference is an "external reference" (TM-1044.j_s9.tex:15-26).
- Export table = set of ONE-word export table entries in the cluster's system fixed area. TM-1044.j_s9.tex:33-34 「クラスタ内のシステム固定領域に割り付けられる。」 "allocated in the cluster's system fixed area".
- Path: external-reference cell (1 word, importer) -> import record (holds the external reference ID) -> [network] -> export table entry (exporter) -> data (TM-1044.j_s9.tex:43-57, fig :60-112).

##### External reference ID (外部参照ID), 1 word (fig TM-1044.j_s9.tex:134-174)
| # | field | meaning |
|---|---|---|
| tag | WEXREF○ / WEXVAL○ / BEXREF○ / BEXVAL○ / INT○ | W=white (single ref), B=black (multiple ref); REF = exported datum was unbound, VAL = instantiated; INT○ when stored inside an import record (TM-1044.j_s9.tex:119-120, :193-197, :209-209, :308-311, :326-326) |
| value hi | cluster number, 8 bit | exporting cluster (TM-1044.j_s9.tex:163-164) |
| value | control flags, 4 bit | Safe/Unsafe, structure (構造体) flag, Unify flag, 1 reserved; drawn left to right in that order (TM-1044.j_s9.tex:121-130, :146-161) |
| value lo | export table entry offset, 20 bit | offset from top of export table area (TM-1044.j_s9.tex:36-40, :169-170) |
- TM-1044.j_s9.tex:130-130 「3ビットを使用しており、残りの1ビットは予備としている。」 "3 bits used, the remaining 1 bit is spare".
- Bit numbers (from VPIM source structures/str_trade_misc.psl.c:1008-1013, not TM-1044): cluster = bits 31-24, Safe/Unsafe = bit 23 (0x00800000), structure = bit 22, Unify = bit 21, bit 20 spare (debug), offset = bits 19-0.

##### White (single-reference) export/import
- White export table entry = the export table entry itself, 1 word = pointer to the exported datum (fig shows `LIST○` -> cons, `REF○` -> EUNDF cell). TM-1044.j_s9.tex:181-185, fig :220-271.
- White import record = 1 word = the external ref ID retagged INT○; white import table is in the system fixed area to ease batch GC; the external-reference cell (1 word) points at the record and carries the SAME tag as the ID in the message (WEXREF / WEXVAL). TM-1044.j_s9.tex:200-213. Quote TM-1044.j_s9.tex:211-211 「外部参照セルのタグは、メッセージ中の外部参照IDのタグと同一のものにする。」 "the cell's tag is made identical to the tag of the ID in the message".
- No hashing for white tables (direct offset). (inference from TM-1044.j_s9.tex:181-213: hashing is described only for black.)

##### Black (multiple-reference) export/import
- Black export = export table entry (1 word, pointer to black export record) + black export record; same-address data share one record ("re-export" 再輸出); records are also entered in a hash table keyed by the datum's ADDRESS. TM-1044.j_s9.tex:277-300. Quote TM-1044.j_s9.tex:296-296 「黒輸出表は、そのアドレスをキーとしたハッシュ表にも登録する。」 "the black export table is also registered in a hash table keyed by that address". Hash function and table sizes: not in TM-1044 (s9).

Black export record (fig TM-1044.j_s9.tex:377-385; text :298-299; WEC is 2 words per :721-721, so 4 words):
| # | tag | value / meaning |
|---|---|---|
| 0 | (pointer tag; EOL = "release reserved") | pointer to exported datum (TM-1044.j_s9.tex:1787-1787) |
| 1-2 | — | WEC, two words, negative, range 0 .. -2^64 |
| 3 | — | hash-collision chain |
(order confirmed by VPIM source structures/str_exp_table_rec.psl.c:529-534, not TM-1044: DATA 0, WEC1 1, WEC2 2, CHAIN 3)

Black import record, 4 words (text TM-1044.j_s9.tex:323-325, fig :401-415):
| # | tag | value / meaning |
|---|---|---|
| 0 | INT○ | imported black external ref ID (NULL-like value = release reserved, :1861-1861) |
| 1 | — | WEC, one word, positive, 0 .. 2^32 |
| 2 | MRB = re-import flag (white = first import, black = re-imported) | pointer to the external-reference cell |
| 3 | — | hash-collision chain |
- Quote TM-1044.j_s9.tex:327-327 「また、外部参照セルを指すポインタのMRBを1度目の輸入では白とし、」 "the MRB of the pointer to the external-reference cell is white on the first import" (black on re-import, :328-331).
- Black import records are hashed by the black external ref ID; a re-import allocates NO new cell and reuses the existing cell pointer (TM-1044.j_s9.tex:333-344).

##### Single vs multiple reference: which bit decides
- White/black = single- vs multiple-reference datum (TM-1044.j_s9.tex:178-185, :275-282), i.e. the MRB of the exported pointer (inference); on the wire it is the TAG (WEX* vs BEX*), not a flag bit.
- Estimating paths to an external-reference cell (table TM-1044.j_s9-msg-kl1data.tex:341-356): white cell + MRB off = single; white cell + MRB on = multiple; black cell + MRB off + re-import flag off = single; black + MRB off + re-import on = multiple; black + MRB on = multiple; ReadHook cell = always multiple.
- Safe/Unsafe is a different thing (unification-loop prevention): flag OFF = Safe, ON = Unsafe. Quote TM-1044.j_s9.tex:797-797 「と呼び、OFFの時をSafe属性、ONの時をUnsafe属性とする。」. A cell is Safe when the exporting cluster number < own cluster number, else Unsafe (TM-1044.j_s9.tex:799-805); when an Unsafe cell is indirectly exported the ID's Safe/Unsafe flag is set ON, and flag ON overrides a Safe number comparison (TM-1044.j_s9.tex:869-874).

##### WEC (Weighted Export Count)
- Sum over export entry + import records + in-flight messages = 0; negative in the export table, positive in messages and import records (TM-1044.j_s9.tex:439-444). Quote TM-1044.j_s9.tex:443-443 「WECは、輸出表内では負の値になり、メッセージ内と輸入レコード内では正の値になる」.
- Reclaimed import record returns its WEC to the export table; export side adds; at 0 the export entry and export record are reclaimed and reclamation of the datum is attempted (TM-1044.j_s9.tex:446-451). Worked example -100 / 100 -> 50+50 -> returns (figs :458-711).
- Black: each export adds 2^24. Quote TM-1044.j_s9.tex:719-719 「黒外部参照IDには1回輸出される毎に\(2^{24}\)のWECが付けられる。」 "2^24 of WEC is attached per export of a black ID".
- Black import record overflow: above 2^32, keep 2^24 in the record and return the rest to the export record (TM-1044.j_s9.tex:724-725). Export-record WEC assumed never to overflow; more than 2 words would be needed for larger systems (:727-728).
- Splitting rule: single-ref cell -> "release export" (解放輸出): take ID and ALL WEC, reclaim import record and cell; possibly-multiple-ref cell -> "split export" (分割輸出): take ID and HALF the record's WEC, keep record and cell (TM-1044.j_s9-msg-kl1data.tex:331-337). Quote TM-1044.j_s9-msg-kl1data.tex:336-336 「この方式では、輸入レコードから外部参照IDと輸入レコード内のWECの半分を獲得し、」.
- White: no WEC word. ID Unify flag off = WEC 2, on = WEC 1; white export entry MRB white = WEC -2, black = WEC -1 (table TM-1044.j_s9.tex:744-750). Quote TM-1044.j_s9.tex:736-736 「白輸出表エントリではデータへのポインタのMRBをWECの代わりとして用いる。」.
- WEC exhausted (import record WEC = 1, cannot split; TM-1044.j_s9.tex:1966-1970):
  - Indirect export (間接輸出): leave the WEC, export a pointer to the external-reference cell itself (i.e. through the local export table, fig :2016-2050; inference); used when lengthening a reference (args of %throw_goal, arg 2 of %unify). White import records always use it when split is needed, WEC=1 and 2 not distinguished (TM-1044.j_s9.tex:2004-2011).
  - WEC supply (WEC補給): %request_BEXID to the exporter, answered by %supply_BEXID; used when following the reference (target of %read, arg 1 of %unify); message sending for that cell is suspended meanwhile (TM-1044.j_s9.tex:2055-2064).
  - %request_BEXID send (TM-1044.j_s9.tex:2071-2087): (1) allocate (or reuse) a ReadHook record behind the cell and hook the goal (%read case) or the unify D-code (%unify case); (2) allocate one white export entry as reply destination; (3) take ID+WEC out of the import record and reclaim the record; (4) ReadHook's import-record pointer := NULL, with the ID's Safe/Unsafe bit stored as its MRB; (5) send ID, WEC, reply ID.
  - Receipt of %request_BEXID (TM-1044.j_s9.tex:2141-2147): find datum from ID, re-export it as multiple-reference to get a black ID + WEC, send %supply_BEXID(reply ID, black ID, WEC).
  - Receipt of %supply_BEXID (TM-1044.j_s9.tex:2203-2215): get requesting cell from reply ID; import the black ID+WEC giving a new cell; if the requesting cell is already instantiated (an %answer_value overtook) do nothing; if its type is RDHOK write the new cell pointer into it; resume the goals on the ReadHook record.
- Immediate GC: reclaim request on a single-ref external cell -> take ID+WEC from import record, send %release; multiple-ref -> nothing. After batch GC both import tables are scanned and unused records are released by %release (TM-1044.j_s9.tex:1731-1738).

##### Cell types used (all named in the text)
- External-reference cells: WEXREF, WEXVAL, BEXREF, BEXVAL (pointer to import record); RDHOK (pointer to ReadHook record, TM-1044.j_s9.tex:1383-1383); EXLOCK = soft-locked external cell (:1386-1387, :1810-1811); HOOK on a single-ref single-wait cell after %read (:1333-1333).
- Exported variables: UNDF->EUNDF, HOOK->EHOOK, MHOOK->EMHOK when exported (TM-1044.j_s9-msg-kl1data.tex:279-280); RHOOK = variable with a ReplyHook record (TM-1044.j_s9.tex:1494-1495; listed with exported variables at TM-1044.j_s9-msg-kl1data.tex:292-293).
- SLOCK = soft-locked white export entry, black export/import hash entry or record (TM-1044.j_s9.tex:1750-1750, :1754-1756, :1820-1822). "EXVAL"/"EXREF" without W/B prefix: not in TM-1044 (s9).

##### ReadHook record (RDHOK), 2 words (TM-1044.j_s9.tex:1374-1383, fig :1422-1424)
| # | tag | value / meaning |
|---|---|---|
| 0 | same type the external cell had (WEX*/BEX*) | pointer to import record (NULL while a %request_BEXID is outstanding, MRB then = saved Safe/Unsafe bit, :2083-2084) |
| 1 | HOOK etc. | pointer to hooked goal(s) |
- Quote TM-1044.j_s9.tex:1383-1383 「ReadHookレコードを指す外部参照セルのタイプは{\sf RDHOK}とする。」 "the external cell pointing to a ReadHook record has type RDHOK".

##### ReplyHook record (RHOOK), 3 words (TM-1044.j_s9.tex:1478-1480, fig :1506-1511)
| # | tag | value / meaning |
|---|---|---|
| 0 | — | goal link (goals previously hooked on the variable) |
| 1 | — | pointer to the hooked variable ("RHOOKへのポインタ") |
| 2 | — | pointer to reply destination = an external cell (WEXREF) -> white import record holding the reply ID |
- Three-way disagreement on word order: text (TM-1044.j_s9.tex:1479-1480) lists variable pointer, goal link, reply destination; the figure (above) goal link, variable, reply; (VPIM source structures/str_trade_misc.psl.c:315-319, not TM-1044) goals 0, reply/return address 1, hooked variable 2. Figure order not authoritative; the source offsets are the only concrete ones. Unresolved by TM-1044.
- Quote TM-1044.j_s9.tex:1478-1478 「ReplyHookレコードは3ワードのセルからなるデータ構造で、」; variable is overwritten exclusively with type RHOOK -> record (:1494-1495).

##### Structure ID and structure table (構造体管理)
- For large data (code modules) so that one cluster never holds two copies. Structure ID = 1 word, tag INT○, value top 8 bits cluster number, low 24 bits serial within cluster (TM-1044.j_s9.tex:882-898). Quote TM-1044.j_s9.tex:897-897 「構造体IDは1ワードデータで、タグは{\sf INT}$\circ$、値部の上位8ビットに」.
- Structure record = 4 words: structure ID, pointer to data, hash link keyed by ID, hash link keyed by address; two hash tables (TM-1044.j_s9.tex:927-934). Fig :970-991 draws (top to bottom) ID hash link, address hash link, structure ID, pointer — same as VPIM source structures/str_struct_rec.psl.c:136-141 (not TM-1044): 0 ID chain, 1 addr chain, 2 ID, 3 addr.
- Import with structure ID (TM-1044.j_s9.tex:904-920): look up ID; if present take local pointer and RETURN the ext ref ID to the exporter; else import the ID, register (structure ID -> external cell); later replace by the body pointer. Exporter sets the ID's structure flag ON.

##### Export levels and wire encoding of each KL1 type
- Two levels only: level 0 = pointer only (ext ref ID), level 1 = the body with each ELEMENT exported level 0. Quote TM-1044.j_s9-msg-kl1data.tex:13-13 「VPIMでは前者を{\dg\bf レベル0輸出}、」 (:11-19). So exactly one level of structure travels per message.
- Black IDs are always followed by a (DNTC, WEC) word; white IDs are a single word.

| datum | level 0 | level 1 | cite |
|---|---|---|---|
| INT, ATOM, VECT0 (null vector) | — (always level 1, never registered) | 1 word as is: `INT○ int` / `ATOM○ atom number` / `VECT0○ null` | TM-1044.j_s9-msg-kl1data.tex:33-51 |
| list | `WEXVAL○ id` or `BEXVAL○ id; DNTC WEC` | `LIST○ null`; car (level 0); cdr (level 0); cons freed if pointer single-ref | TM-1044.j_s9-msg-kl1data.tex:60-86 |
| short vector | as list | `VECT1○..VECT8○ null`; elements 0..last (level 0); body freed if single-ref | TM-1044.j_s9-msg-kl1data.tex:101-128 |
| long vector | as list | `VECT○ null`; `INT○ length`; elements (level 0) | TM-1044.j_s9-msg-kl1data.tex:137-165 |
| string | as list | `STRG○ null`; `CDESC○ string length`; whole string body contiguous | TM-1044.j_s9-msg-kl1data.tex:174-198 |
| module | `MOD● structure-ID`; `BEXVAL○ id` (structure flag ON); `DNTC WEC` | `MOD○ null`; module body, each element level 0 | TM-1044.j_s9-msg-kl1data.tex:206-230 |
| code | no level distinction: `COD● module structure-ID`; `BEXVAL○ module ext-ref ID` (structure flag ON); `DNTC module WEC`; `DNTC offset in module` | | TM-1044.j_s9-msg-kl1data.tex:238-265 |
| variable (UNDF/HOOK/MHOOK) | no level distinction: cell becomes EUNDF/EHOOK/EMHOK, registered; `WEXREF○ id` or `BEXREF○ id; DNTC WEC` | | TM-1044.j_s9-msg-kl1data.tex:276-282, :303-312 |
| exported variable (EUNDF/EHOOK/EMHOK/RHOOK) | same wire form, type unchanged | | TM-1044.j_s9-msg-kl1data.tex:292-298 |
| external-ref cell | normally the ID it points to is sent (release export or split export; else indirect export) | | TM-1044.j_s9-msg-kl1data.tex:324-337, :358-360 |
| float | not in TM-1044 (s9) | | |
- Import (TM-1044.j_s9.tex:1025-1108): atomic written in place; IDs registered in white/black import table + cell; list -> allocate 1 cons; vector -> length from leading tag; string -> size from leading descriptor; module level 0 / code -> structure-table lookup, if known return ID (+WEC) to exporter, else import and for code allocate a variable and push D-code goal `dcode_read_module(Mod,Ofst,Code) :- wait(Mod) | module_offset_to_code(Mod,Ofst,Code).` (:1101-1105).

##### Messages: "24 kinds" (TM-1044.j_s9-message.tex:11-11 「現在 VPIM で用意したメッセージは全部で24種類である。以下では、これらの」); 21 named sections, 24 if the white/black variants of %read, %release, %request_BEXID are counted separately (inference). Every logical packet = kind symbol word, data, End of Message word (TM-1044.j_s9-network.tex:19-20). Numeric kind codes: not in TM-1044 (s9).

| message | fields in order (tag value) | cite |
|---|---|---|
| %throw_goal | `DNTC THROW_GOAL`; `INT○/● shoen ID`; `DNTC WTC`; `DNTC shoen priority lower`; `DNTC shoen priority upper`; `DNTC resource`; `DNTC goal priority`; `COD● module structure-ID`; `BEXVAL○ module ext-ref ID`; `DNTC WEC`; `DNTC offset in module`; `DNTC arg count`; arg1..argn (each level 0); EOM | TM-1044.j_s9-message.tex:25-75 |
| %unify | `DNTC UNIFY`; `DNTC shoen ID`; `DNTC WTC`; `DNTC current priority`; arg1 (external ref ID [+WEC]); arg2 (level 1); EOM | TM-1044.j_s9-message.tex:89-116 |
| %read (white) | `DNTC READ`; `WEXREF/VAL○ ID to read`; `WEXREF○ reply ID`; EOM | TM-1044.j_s9-message.tex:132-151 |
| %read (black) | `DNTC READ`; `BEXREF/VAL○ ID to read`; `DNTC WEC`; `WEXREF○ reply ID`; EOM | TM-1044.j_s9-message.tex:160-182 |
| %answer_value | `DNTC ANSWER_VALUE`; `WEXREF/VAL○ reply ID`; reply data (level 1); EOM | TM-1044.j_s9-message.tex:194-212 |
| %release (white) | `DNTC RELEASE`; `WEXREF/VAL○ ID`; EOM | TM-1044.j_s9-message.tex:229-245 |
| %release (black) | `DNTC RELEASE`; ID (text: type BEXREF/BEXVAL; figure prints `WEXREF/VAL○`, apparent typo); `DNTC WEC returned`; EOM | TM-1044.j_s9-message.tex:254-273 |
| %request_BEXID (white->black conversion) | `DNTC REQUEST_BEXID`; `WEXREF/VAL○ data ID`; `WEXREF○ reply ID`; EOM | TM-1044.j_s9-message.tex:291-309 |
| %request_BEXID (black, WEC short) | `DNTC REQUEST_BEXID`; `BEXREF/VAL○ data ID`; `DNTC remaining WEC`; `WEXREF○ reply ID`; EOM | TM-1044.j_s9-message.tex:319-340 |
| %supply_BEXID | `DNTC SUPPLY_BEXID`; reply ID (figure tag `BEXREF/VAL○`, though requests carry a `WEXREF○` reply ID); `BEXREF○ supplied black ID`; `DNTC WEC`; EOM | TM-1044.j_s9-message.tex:353-374 |
(shoen/foster-parent messages: see GAP 5.)

##### Processing on send/receipt (data-reference messages)
- %throw_goal send: code pointer + each arg level 0, plus shoen ID, WTC, resource, foster-parent max/min priority, goal priority, because the receiver may have to create a foster parent (TM-1044.j_s9.tex:1121-1128). Receipt: shoen ID -> foster parent; if none, create one from the priority info + shoen ID and send %ready to the shoen; import code pointer and args, build goal record, push on goal stack — actually the D-code goal `dcode_apply(Code, Argv) :- true | apply(Code, Argv).` because the code pointer may not be available yet (TM-1044.j_s9.tex:1132-1144); if the module is absent, D-code read_module runs first (:1162-1164). Example `test(X) :- true | dist(X)@cluster(2).` (:1150-1150).
- %read / %answer_value: see GAP 2.
- %unify send: arg1 = the external cell that caused it: single-ref -> reclaim cell + import record, send ID + all WEC; multiple-ref -> ID + half WEC; arg2 exported level 1; shoen ID, WTC, priority included (TM-1044.j_s9.tex:1610-1631). Cases: instantiated datum vs ext cell -> %unify with datum as arg2 (:1660-1662); never-exported variable vs ext cell -> just bind variable -> ext cell, hooked goals go to the goal stack (:1666-1668); exported variable vs ext cell: if cell is WEXVAL/BEXVAL/RDHOK->*VAL bind locally; if WEXREF/BEXREF/RDHOK->*REF then Unsafe -> send %unify with the variable as arg2, Safe -> bind locally (:1672-1693); ext cell vs ext cell -> %unify to one exporter with the other as arg2, WEC supply if short, unification suspended until supplied (:1697-1702).
- %unify receipt: import both args; easy pair (one variable, one instantiated) unified on the spot; if the shoen's foster parent exists keep the WTC here, else return WTC to the shoen; otherwise push D-code goal `dcode_unify(Arg1,Arg2) :- true | Arg1 = Arg2.` under that foster parent, creating one (and sending %ready) if absent (TM-1044.j_s9.tex:1706-1727).
- %release receipt: add returned WEC; at 0 reclaim export entry/record (TM-1044.j_s9.tex:449-451); black record is first "release reserved" (data pointer type := EOL), then unhooked from the hash chain under the hash-entry lock (:1777-1802).

- Locking (structures shared by all PEs of a cluster, TM-1044.j_s9.tex:1742-1743): white export entry: soft lock (type SLOCK) for the MRB white->black (WEC -2 -> -1) change (:1747-1750). Black export: SLOCK on hash entry and on record; export = lock hash entry, search chain, found -> lock record, change WEC, unlock; not found -> allocate, set WEC + pointer, insert (:1758-1775). External cell: EXLOCK (:1810-1811). White import record: no lock needed while the cell is locked (:1815-1816). Black import: SLOCK on hash entry and record, same pattern, updates WEC and re-import flag (:1824-1847); release-reserve by setting the ID to a NULL-like value (:1861-1861). Structure table: one lock flag for the whole table (:1962-1962).

##### Cluster numbering and network layer
- Cluster number = 8 bits in external ref ID and structure ID (TM-1044.j_s9.tex:163-164, :897-898); number ORDER defines Safe/Unsafe (:799-805). Processor (PE) numbering within a cluster, number of clusters: not in TM-1044 (s9).
- Unit = packet; message built in heap as a logical packet using a worst-case length ESTIMATE (exact size too costly), then control words added -> physical packet written to the network buffer; multi-packet decided at that point from the real length (TM-1044.j_s9-network.tex:10-24, :70-90). Quote TM-1044.j_s9-network.tex:101-101 「ただし、VPIMでは、基本的に1データ1ワードである。」 "in VPIM basically one datum = one word".
- Single physical packet (fig TM-1044.j_s9-network.tex:129-134): `DNTC sender cluster no.`; `DNTC receiver cluster no.`; `INT○ packet length` (words, sender cluster no. through End Of Message); message body; End Of Message.
- Multi physical packet (fig :135-143): `DNTC sender`; `DNTC receiver`; `INT● packet length`; `DNTC packet ID`; `DNTC total packets`; `DNTC packet number`; body; End Of Message. The "tag part" of the length word distinguishes: INT○ single, INT● multi (:110-111), i.e. its MRB (inference). Packet ID separates interleaved multi-packet messages of the same kind (:112-116).
- Receive: at slit check on the event "packet arrived"; ALL packets in the network buffer are processed in one receive pass; single packet -> build logical packet in memory -> message dispatcher (TM-1044.j_s9-network.tex:150-162).
- Multi-packet record (fig TM-1044.j_s9-network.tex:180-187): `INT○ packet ID`; `INT○ sender cluster no.`; `INT○ total packets`; `INT○ received packets`; `VECT○ next-record link`; `STRG○ pointer to logical packet 1` .. `STRG○ pointer to logical packet n` (one slot per packet; a logical packet is treated as a STRG). Complete when received = total; packets are then concatenated, passed to the dispatcher, record reclaimed (:198-229).
- Buffer capacity / maximum packet size: not in TM-1044 (s9-network).

#### From ch. 10 (shoen / foster parent)

Field-by-field formats: not in TM-1044 (s10); only names, direction, payload hints:
- shoen -> FP: `%start`, `%stop`, `%abort` (TM-1044.j_s10.tex:818, 841, 861), `%supply_resource` (TM-1044.j_s10.tex:778), `%ask_statistics` (TM-1044.j_s10.tex:899), `%supply_WTC` (TM-1044.j_s10.tex:1520).
- FP -> shoen: `%ready` (new FP created by an arriving goal, TM-1044.j_s10.tex:1585-1586), `%terminated` (carries final consumed resource, TM-1044.j_s10.tex:872-873; and all the FP's WTC, TM-1044.j_s10.tex:278), `%request_resource` (TM-1044.j_s10.tex:719), `%return_resource`, `%answer_statistics` (carries FP consumed resource, TM-1044.j_s10.tex:918), `%request_WTC` (TM-1044.j_s10.tex:1486), exception message (TM-1044.j_s10.tex:1885-1887).
- Cluster with no FP -> shoen: `%NAKstart`/`%NAKstop`, formerly one undifferentiated `%return_WTC` (TM-1044.j_s10.tex:1649-1652 q TM-1044.j_s10.tex:1652:`{\tt \%return\_WTC} メッセージとしていた。`).
- WTC-carrying, FP-to-FP, already in Multi-PSI: `%throw_goal`, `%unify` (may create a goal at the receiver) (TM-1044.j_s10.tex:1496-1501). Newly WTC-carrying for PIM, FP -> shoen: `%ready`, `%request_resource`, `%return_resource`, `%answer_statistics`, `%request_WTC`, `%terminated` (TM-1044.j_s10.tex:1503-1512).
- WTC shortage: check is made on what remains after reserving WTC for one `%terminated` and one `%request_WTC`, so those two are never held back (TM-1044.j_s10.tex:1488-1491; q TM-1044.j_s10.tex:1488 `WTC は、{\tt \%terminated}メッセージの分と{\tt \%request\_WTC} メッセージの分を確保したあとの、`). Held messages are retried on receipt of ANY WTC-carrying message, not only `%supply_WTC` (TM-1044.j_s10.tex:1520-1521); a held `%unify` is re-run as the unify D-code because the variable may have become bound (TM-1044.j_s10.tex:1523-1525). An aborted FP with held `%return_resource`/`%answer_statistics` waits for `%supply_WTC` instead of terminating (TM-1044.j_s10.tex:1529-1536).
- Shoen word 8 counts `%ready`/`%terminated` from FPs against overtaking (TM-1044.j_s10.tex:493-496). (from VPIM source structures/str_int_cl_packet.psl.c:70-106, not TM-1044: message numbers throw_goal 0, ready 1, terminated 2, start 3, stop 4, abort 5, read 6, answer_value 7, release 8, unify 9, exception 10, request_WTC 14, supply_WTC 15, return_WTC 16, request_resource 17, supply_resource 18, return_resource 19, ask_statistics 20, answer_statistics 21, nak_start 28, nak_stop 29.)

#### From ch. 7 (unification, suspend, merger) and ch. 8 (slit check)

- Guard: data whose body is in another cluster is treated as unbound (suspends) (footnote s7:43). Compile-time structure constants may live in another cluster, hence `unify` is emitted (footnote s7:393-394). Reply-hook records share the hook chain (s7:770-772). Packet arrival = SCR bit 0 => packet receive processing (s8:218-224).

### GAP 7: Memory map, heap, free lists, GC (and slit check)

#### From ch. 4 (memory, MRB), ch. 5 (D-code), ch. 6 (scheduling)

##### Assumptions (`TM-1044.j_s4.tex:29-58`)
- All memory is shared, no physical local memory; all PEs of a cluster share one address space; no address translation (physical = logical); memory contiguous from address 0; word addressing, 1 word = 40 bits (8 tag + 32 value); addresses 00000000..FFFFFFFF, max 4G words. `:51` 「1ワードは40ビット(タグ部8ビット,値部32ビット)からなっている。」

##### Memory map (figure `TM-1044.j_s4.tex:62-91`, address labels `:86-89`; low address at top)
| range (hex, words) | area | cite |
|---|---|---|
| 00000000 - 00100000 | system SHARED fixed area | `:85,87,89` |
| 00100000 - 00200000 | processor-LOCAL fixed area (split in 8 equal parts, one per PE; no locking) | `:83,88`, `:112-114` |
| 00200000 - end of physical memory | heap area, two halves (A) then (B) | `:76-79` |
| above, up to FFFFFFFF | (unused; logical space beyond installed memory) | `:74,86` |
- Three areas; only the heap is GC'd. `:24-25` 「ヒープ領域だけである。」 Fixed-area boundaries are set at system design time, never changed at run time (`:99-102`). 8 parts: `:113` 「全体の領域を8等分して使う。」 (=> 0x20000 words per PE, inference).
- Processor-local fixed area holds (`:116-155`): (1) memory-allocated pseudo-registers, and the `save`/`restore` area used when the KL1 compiler runs out of argument registers; (2) suspend stack (pointers to the unbound cells that prevented commit); (3) ready-goal-stack entries; (4) unify stack (passive unification of structures); (5) internal event stack (signals deferred when another PE holds the barrier).
- System shared fixed area holds (`:159-209`): (1) system configuration (PEs per cluster, clusters); (2) memory management (global heap top, last address of the heap half in use); (3) intra-cluster communication (flags, goal posts); (4) system code area (D-code module loaded at init; on real machines also runtime routines called from micro-instructions); (5) inter-cluster area: export table entries, black export (address) hash table, white import table, black import (ID) hash table, structure address hash table, structure ID hash table. There is NO separate shared vs local HEAP: one heap, per-PE free lists.

##### Heap (`TM-1044.j_s4.tex:211-266`)
- Contiguous; copying stop GC, so split in two halves used alternately (`:217-219`). Holds KL1 data, goal records, user code, PIMOS code (`:224-228`).
- Logical page = 256 words, hardware-independent. `:254` 「とは独立であり、256ワードとしている。」 Pages are the unit handed to PEs.
- Each PE keeps a reserve of "allocated pages" (割当ページ) as a free list of pages, big enough to finish one goal reduction (`:255-258`, `:270-277`).
- Free list of some size empty -> extend the heap by 1 page (global heap top) and carve the whole page into cells of that size (`:280-281`, `:326-328`). If no page can be got: set a slit-check cause, take 1 page from the reserve, continue the reduction (`:259-261`, `:282-285`).
- GC trigger: at a reduction boundary, when reserve-page shortage is detected, stop GC starts. `:262-263` 「一括GCを起動する。」; cause is reported to all PEs at the next reduction boundary (`:285`).
- Data >= 1 page: only from body built-ins `new_vector`, `new_string`; heap extended in page units, no free-list management; on failure set slit-check cause and enqueue a D-code goal (`:289-297`).

##### Free lists (`TM-1044.j_s4.tex:299-336`)
- Per PE, per size (`:233-237`). Terminator = EOL type; link tag = FLC (Free List Cell), chosen only for debugging; unused part of a cell not initialised (`:307-309`).
- Nine sizes, powers of two. `:314` 「丸めている。即ち、1, 2, 4, 8, 16, 32, 64, 128, 256 の9種類である」 = "rounded: nine kinds, 1, 2, 4, 8, 16, 32, 64, 128, 256". A request takes the next size up (3 words -> the 4-word list, `:315-318`).
- Free-list tops are registers; on real PIMs short of registers the less-used ones (all but 1, 2, 16 words, footnote) may sit in the processor-local fixed area (`:320-324`).
- Explicitly NOT done: splitting a larger cell; coalescing neighbours (buddy system) (`:330-336`).
- Allocation routine names: not in TM-1044 (s4). GC algorithm detail: not in s4 (ref. to chapter `sec-stop-gc`).

#### From ch. 11 (GC), ch. 12 (debug), ch. 13 (SCSI)

##### Scope, trigger, semispaces
- "一括GC" = per-cluster, all PEs of the cluster stop in sync, each PE does GC work independently, all finish in sync and resume (TM-1044.j_s11.tex:54-61). `\item クラスタ内の全てのPEが同期して通常実行を停止し` "all PEs in the cluster synchronously stop normal execution" (TM-1044.j_s11.tex:57-57). Clusters GC independently because cross-cluster data goes through the export table (TM-1044.j_s11.tex:46-52).
- Trigger: only "memory shortage", detected as an internal event: `\item メモリ不足によるGC要求の検出 (内部イベント処理として行う)` "detection of a GC request due to memory shortage (done as internal-event processing)" (TM-1044.j_s11.tex:600-600); also "when memory is used up" (TM-1044.j_s11.tex:40-44). No threshold number: not in TM-1044 (s11).
- Semispace copying (Baker): `コピー方式では、ヒープ領域を二等分し、通常実行時にはそ` "the heap is split in two equal halves, normal execution uses only one" (TM-1044.j_s11.tex:124-126). S = scan pointer, B = "bottom" (formerly called heap top) (TM-1044.j_s11.tex:134-137); sequential algorithm fig. (TM-1044.j_s11.tex:156-182); ends when S = B (TM-1044.j_s11.tex:148-148). Chosen because only live cells are touched = low bus traffic on a shared-memory multiprocessor (TM-1044.j_s11.tex:128-131).
- Multi-PSI's "MRB maintenance" (restoring white MRBs during GC) is NOT implemented: `は、メモリアクセスを増大させることになるので、実装しないことにした。` "it increases memory accesses, so we decided not to implement it" (TM-1044.j_s11.tex:92-94). MRB is instead used to skip forwarding marks for single-reference cells (TM-1044.j_s11.tex:82-89).

##### Parallel copying, units, locking
- GC roots are distributed per PE; each PE copies from its own roots (TM-1044.j_s11.tex:96-100). Shared pointer GlobalB (how far new space is used) is advanced only in units of HEU (Heap Extension Unit, "page"): `ver1.0では 256語である。})。` "256 words in VPIM ver1.0" (TM-1044.j_s11.tex:360-366). The GlobalB update is the one atomic operation in checkB/copy (TM-1044.j_s11.tex:285-286; TM-1044.j_s11.tex:337-339).
- Pages are per size class; structures are allocated rounded up to a power of two; each PE keeps one (S_k, B_k) pair per size k (TM-1044.j_s11.tex:368-374). scan-all loops sizes i = HEU, HEU/2, ..., 1 while S_i < B_i (TM-1044.j_s11.tex:230-241).
- Objects with Arity >= HEU: space of exactly Arity is taken from GlobalB at copy time and the copied area is put straight into the shared pool (TM-1044.j_s11.tex:333-350; TM-1044.j_s11.tex:570-573).
- Load balancing: one cluster-wide shared pool of unscanned areas; busy PEs add, idle PEs take (TM-1044.j_s11.tex:113-118; TM-1044.j_s11.tex:243-250). When B crosses into a new page and S and B are 2 or more pages apart, the page S was in goes to the pool (TM-1044.j_s11.tex:379-389). LDU (Load Distribution Unit): `\footnote{VPIM ver1.0 では、32語である。}を導入している。こ` "32 words in VPIM ver1.0" (TM-1044.j_s11.tex:402-411); checkS hands LDU-sized unscanned runs to the pool when S reaches an LDU boundary, cases same-LDU / same-HEU / different-HEU (TM-1044.j_s11.tex:293-315; TM-1044.j_s11.tex:475-484).
- Termination: all PEs idle (for all j,k: S_k^j = B_k^j) and shared pool empty (TM-1044.j_s11.tex:391-397; TM-1044.j_s11.tex:252-253).
- Locking: marking of the old-space cell (writing the forwarding address) must be exclusive (TM-1044.j_s11.tex:197-199); for goal records and black import records the exclusion is unnecessary but currently done to share the routine (TM-1044.j_s11.tex:829-832; TM-1044.j_s11.tex:901-904). Software locks (SLOCK, EXLOCK) must all be released before entering GC (TM-1044.j_s11.tex:978-980).

##### Flow and PE synchronisation (fig. TM-1044.j_s11.tex:599-627)
| step | action | who |
|---|---|---|
| 1 | detect GC request (memory shortage, internal event) | - |
| 2 | sync (dag 1): switch to GC phase; barrier = PE counter in memory | all |
| 3 | pre-processing (heap flip etc.) | 1 PE (the last PE to enter the GC phase) |
| 4 | sync (dag 2): start GC; plain broadcast signal | all |
| 5a | copy roots: (i) goals pointed to from the ready goal stack, (ii) goals in the intra-cluster goal communication post, (iii) goals pointed to from the export table (table area split per PE), (iv) all foster parents reachable from the import table | all |
| 5b | main copying loop | all |
| 6 | sync (dag 3): end of copy; polling of an idle bitmap at a fixed address in the system fixed area (not a slit check) | all |
| 7a | scan black import table, detect perpetual suspension, Sweep-and-Copy | 1 PE |
| 7b | turn the remainders of pages into free lists | all |
| 7c | rehash structure table | 1 PE |
| 7d | sync (dag 4): the point at which old space may be destroyed (structure-table maintenance finished) | |
| 7e/7f/7g | Mark-and-Sift / white import table maintenance / black export table rehash | 1 PE each |
| 8 | sync (dag 5): end of GC; same barrier as (dag 1) | all |
- `メモリ中のPE数カウンタ(バリア)を用いてGCフェーズへの切り替えの同期を実現する。` "the switch to the GC phase is synchronised with a PE-count counter in memory (a barrier)" (TM-1044.j_s11.tex:584-585). 7a, 7c and 7e, 7f, 7g can run concurrently on different PEs (TM-1044.j_s11.tex:595-596). Sync descriptions: (TM-1044.j_s11.tex:584-593).
- SCSI: SPC interrupts are normally masked and seen at slit checks, but are ENABLED during GC so the PE answers select/reselect (TM-1044.j_s13-1.tex:1041-1044); results are parked on the post-processing queue until after GC (TM-1044.j_s13-3.tex:876-893).

##### Per-type treatment while scanning new space
- Atomic, nothing done: EOL, ATOM, INT, VOID, UNDF, EUNDF, GOAL, VECT0, HLINK (TM-1044.j_s11.tex:637-652).
- Guaranteed single reference -> copied to a page of its size class WITHOUT writing a forwarding address: by type alone MHOOK, EMHOK, RHOOK, RDHOK; by type + white MRB: LIST, VECT1..VECT8, VECT, STRG (TM-1044.j_s11.tex:654-687). `ドレス(新領域のポインタ)を書き込むことなく、そのサイズに応じ` "without writing the destination address, [copied] according to its size" (TM-1044.j_s11.tex:656-660). The refcount-is-1 optimisation for MGHOK (merger input count) and DREF (number of still-unbound variables of a multiple wait) is not done (TM-1044.j_s11.tex:660-665).
- Single reference but marked anyway (to know afterwards whether it was copied, not against double copying): BEXREF, BEXVAL, HOOK, EHOOK (TM-1044.j_s11.tex:689-698).
- Possibly multiply referenced -> forwarding address written into old space, then copied: by type alone (MRB not ORed) DREF, SHREC, FPREC, MGHOK; type + black MRB with MRB ORed: LIST, VECT1..VECT8, VECT; type + black MRB without OR: STRG (TM-1044.j_s11.tex:700-745).
- MRB after GC: because the copy is breadth-first, the elements of a black-referenced list/vector are written to new space with their MRB set black (TM-1044.j_s11.tex:706-722); `$\bullet$にして)書き込むことでこれを回避する` "this is avoided by writing them [with MRB] made black" (TM-1044.j_s11.tex:716-717). White pointers stay white; no MRB is ever turned back to white (inference from TM-1044.j_s11.tex:92-94).
- REF: dereferenced during scan. Bound target: no allocation, the value is written at the scan pointer and the word is re-scanned. Unbound target: 1 word allocated, the variable's contents copied (scanned later), and a forwarding address IS written in old space even for REF-white (TM-1044.j_s11.tex:795-815).
- Goal record (reached via HOOK / EHOOK): forwarding address written (for perpetual-suspension detection), at the word holding the GOAL tag. `\item [コピーサイズ] 引数個数 (アリティ) + 制御用語数 (6語)` "copy size = arity + 6 control words" (TM-1044.j_s11.tex:835-835). Allocation size: if 2^(n-1) < copy size <= 2^n then 2^(n+1), minimum 16 words, "to prepare for reuse after GC": `$ 2^{n-1} < $ (コピーサイズ) $\leq 2^{n}$の時、$2^{n+1}$。ただし、最低 16 ワード。` (TM-1044.j_s11.tex:836-839). Each copy increments the "child count during GC" slot of its foster parent (old-space record) (TM-1044.j_s11.tex:841-848). If the foster parent is Aborted or Aborted-Terminated, arguments and code are not copied: `アリティを 0 とし、コードへのポインタを EOL にする。` "arity is set to 0 and the code pointer to EOL" (TM-1044.j_s11.tex:850-854).
- Merger record (via MGHOK): forwarding + copy; also counted in the foster parent's GC child count; if the foster parent is Aborted(/Terminated) the scanned word is rewritten to EUNDF instead of copying (no EMGHOK type exists) (TM-1044.j_s11.tex:856-879).
- WEXREF / WEXVAL: point to white import table entries in the system fixed (non-GC) area; value kept, entry only marked (TM-1044.j_s11.tex:881-890). BEXREF / BEXVAL: black import record is in the heap; forwarding written and copied (TM-1044.j_s11.tex:892-904).
- Code module (COD, MOD): the forwarding address is always written at the module's first word. MOD points there; COD points at a predicate definition: `プの場合は、述語定義の先頭を指しているが、この直前にモジュー` "in the [COD] case it points at the head of the predicate definition, but just before it the modu[le ...]" (TM-1044.j_s11.tex:921-921); that preceding word holds the offset from the module's first word, from which the module head is computed and the forwarding address written there (TM-1044.j_s11.tex:919-924). So the whole module is copied as one object (inference).
- Shoen record (SHREC): multiply referenced (sibling links) -> forwarding + copy; increments the GC child count of the parent shoen's foster parent, except when the record is already unlinked from the child-shoen chain (between reporting terminated and `remove_shoen`) (TM-1044.j_s11.tex:926-945).
- Foster-parent record (FPREC): forwarding + copy; all foster-parent records are copied before the main GC; in the new copy the "child count during GC" slot is set to 0 instead of copied (TM-1044.j_s11.tex:947-954).
- Skipper CDESC: object tag guaranteeing that the following words are atomic (strings, machine-code area of a code module, and padding inserted by GC when allocation size > copy size). The scanner advances by (low 24 bits of the value, unsigned) + 1 (TM-1044.j_s11.tex:956-970).
- Never met while scanning: FLC (free-list cells are never touched), SLOCK / EXLOCK, MARKED, VISIT, DNTC (always behind a CDESC) (TM-1044.j_s11.tex:972-991).
- Forwarding marker tag = MARKED (inference from the two statements following; s11 never says it in one sentence): `旧領域にのみ現れるタイプであるため。` "[MARKED] is a type that appears only in old space" (TM-1044.j_s11.tex:981-983); the type table lists MARKED as "used at GC" (TM-1044.j_s2.tex:159-159). The bit value of MARKED: not in TM-1044 (s11).

##### Inter-cluster tables and post-processing
- Export table entries are roots: every entry whose type is not FLC has its data (including black export records) copied; the hash link word of a black export record has type HLINK (atomic for the scanner) so unneeded records are not dragged in (TM-1044.j_s11.tex:998-1013).
- White import table (contiguous, fixed area): scanning a WEXREF/WEXVAL changes the entry's type INT -> MARKED (value kept). Afterwards the table is scanned: MARKED -> back to INT; INT -> send `%release` and return the entry to the free list; FLC -> nothing (TM-1044.j_s11.tex:1024-1041).
- Black import table: after GC every black import record is walked from the black import hash table (fixed area); for unmarked (uncopied) ones `%release` is sent, and the hash chains are rebuilt in new space (TM-1044.j_s11.tex:1043-1052).
- Black export hash table (keyed by the address of the exported datum): cleared, entries strung into one chain, then re-hashed with the new addresses (TM-1044.j_s11.tex:1054-1065).
- Structure table (address hash + ID hash; records live in the heap): records whose structure is still referenced are copied, both tables cleared and rebuilt; the count is "at most 3 digits" (TM-1044.j_s11.tex:1067-1094).
- Additional roots required by SCSI: the starred words of command and transfer records (foster parent, goal environment, the three KL1 output variables, pointer to Data) and the abnormal-connection list (TM-1044.j_s13-3.tex:620-621; TM-1044.j_s13-3.tex:776-777; TM-1044.j_s13-3.tex:894-900).
- Memory map / heap sizes / free-list layout: not in TM-1044 (s11); s11 refers to the heap-area section (TM-1044.j_s11.tex:368-370).

#### From ch. 7 (unification, suspend, merger) and ch. 8 (slit check)

- GC trigger and delivery: (a) a PE detects heap shortage in a reduction => own SCR bit 10 (`_PAGE_ALLOC_FAIL_EVENT`) (s8:445-448). (b) at next slit check it inspects the 1-to-all message slot: free => set `_GC_REQUEST`, set barrier := number of PEs, signal all PEs (bit 3), reset cause; already `_GC_REQUEST` => reset, do nothing; other message => leave bit set, retry at next slit check (s8:450-459). (c) every PE at bit 3 with slot type `_GC_REQUEST`: lock barrier, reset cause, decrement, write back, unlock (s8:308-312). (d) the PE that brings it to 0 re-signals all: "とるために、もう一度全PEにシグナルを送りGC処理を開始する。" (TM-1044.j_s8.tex:314-314) = "to synchronise GC start, signals all PEs once more and starts GC"; others: "最後でなかった時はGC開始のシグナルが送られてくるのをビジーウェイトする。" (TM-1044.j_s8.tex:315-315) = "busy-wait for the GC-start signal". GC is 一括GC (stop-all, all PEs synchronised) (s8:183, 306).
- Processor-local fixed areas hold unify stack (s7:90-92) and suspend stack (s7:293); system shared fixed area holds the communication area (goal posts, request bitmap, barrier, 1-to-all message slot) (s8:162-166, 175-178, 183-191). Memory map, heap layout, GC algorithm: not in TM-1044 (s7/s8).

##### Slit check (s8)
- Definition/timing: events are handled ONLY between reductions, in software, instead of hardware interrupts: "リダクション間でのみ行なうイベント処理機構である。" (TM-1044.j_s8.tex:23-23) = "an event mechanism performed only between reductions" (s8:18-25). The hosting KL1-B instruction (proceed/execute/...) is not in TM-1044 (s8). D-code structure unify gets one slit check per element: "一要素をユニファイする毎に、スリットチェックが入るので、レスポンスが良" (TM-1044.j_s7.tex:446-446).
- Per-PE **SCR** (slit check register), one bit per event, and **SCF** (slit check flag) = OR of SCR for a fast test (s8:27-35). "現在VPIMでは13個のイベントに対し" (TM-1044.j_s8.tex:36-36) = "currently in VPIM, for 13 events" 12 bits (0-11) are used (s8:36-38); bits 12-31 reserved (s8:57).
- Primitives (s8:63-69): `p_IfSCFON()`, `p_GetSCR(DestReg)`, `p_SetSCRBitImmPosition(ImmSignalPosition,PENumberReg)`, `p_ResetSCRBitImmPosition(..)`, `p_SetSCRBitImmPositionAll(ImmSignalPosition)`, `p_ResetSCRBitImmPositionAll(..)`, `p_PutSCRBit(SignalValueReg,SignalPositionReg,PENumberReg)` (unused).

| bit | event ID (s8:45-56) | class | cause / handling | cite |
|---|---|---|---|---|
| 0 | `_NW_MSG_PACKET_ARV_EVENT` | external | inter-cluster packet arrived; reset, receive | s8:218-224 |
| 1 | `_TIMER_INT_EVENT` | external | per-reduction counter exceeded a set value; pressure update | s8:229-238 |
| 2 | `_SPC_INT_EVENT` | external | SCSI protocol controller interrupt (Selected, Reselected, Disconnected, ResetCondition); cause read from SPC INTS register; bit 2 auto-clears when all INTS bits are 0; per-cause handler | s8:289-300 |
| 3 | `_ALL_SYNCHRONIZE_EVENT` | PE signal (1-to-all) | TWO events, told apart by the 1-to-all message slot type: GC request (`_GC_REQUEST`) / FP statistics gathering (`_FP_IN_EVT_*`) | s8:305-345 |
| 4 | `_FP_STATUS_CHECK_EVENT` | PE signal | FP became stopped/aborted | s8:350-356 |
| 5 | `_GOAL_REQ_EVENT` | PE signal (1-to-any) | load-balance or high-priority goal request; lock request bitmap, reset bit 5 on ALL PEs, clear bitmap, unlock; answer every requester in the bitmap; re-issue request if out of goals | s8:361-380 |
| 6 | `_THROW_GOAL_EVENT` | PE signal (1-to-1) | goals arrived in own goal post (thrown or resumed) | s8:385-399 |
| 7 | `_SERIAL_EXEC_EVENT` | PE signal (1-to-1) | reproducible debug mode: neighbour PE finished 1 reduction; do 1 reduction, signal neighbour, busy-wait | s8:404-412 |
| 8 | `_HIGH_PRIO_GOAL_EVENT` | software | previous reduction forked a higher-priority goal | s8:418-425 |
| 9 | `_FP_STAT_GATHER_EVENT` | software | deferred FP statistics (barrier busy); pop internal event stack | s8:430-440 |
| 10 | `_PAGE_ALLOC_FAIL_EVENT` | software | heap shortage detected in previous reduction | s8:445-459 |
| 11 | `_RESOURCE_CACHE_EXHAUST_EVENT` | software | resource cache and FP resource both 0 | s8:465-470 |

- Processing ORDER (fig s8:78-136, arrow 処理順序 downward): external [packet arrival, SPC, timer] -> PE signals [sync events (GC request, FP stats gathering), FP status check, goal distribution request, goal receive, serial execution] -> software [high-priority goal, memory shortage, deferred FP stats, resource cache miss]. Differs from bit order (SPC before timer; bit 10 before bit 9). Fig notes: underlined = assigned an SCR bit (s8:134); bold (SPC, GC request) = "太字はスリットチェックの要因となるイベント" (TM-1044.j_s8.tex:136-136).
- Barrier (1-to-all): sender sets barrier := number of PEs in the cluster and signals all; each receiver decrements; 0 = all noticed; then a sync signal to all (s8:183-194). 1-to-any: bitmap by PE number in the communication area, any one PE answers (s8:171-178). Software interrupt colliding with a busy barrier: push the event on the per-PE internal event stack and interrupt oneself (s8:199-207).

### GAP 8: Boot, SCSI, real-machine notes, PIM/m and Multi-PSI mentions, footnotes

#### From front matter, ch. 1, ch. 2 tail, PSL documents

##### From the front matter, ch. 1, ch. 2 and the PSL documents (1j-6j)
- VPIM exists to be translated to real machines: besides VPIM itself the team built "(5) a method of converting VPIM written in PSL into real-machine code" (`TM-1044.j_hajimeni.tex:10` 「(5) PSLで書いたVPIMを実機機械語へ変換する方式の開発」), and checked the specification on a Sequent Symmetry (`hajimeni.tex:8`).
- **PIM/m is named as a PSL target.** `1j.tex:33-34` 「{\bf PIM/m}に固有な定義」 (definitions specific to PIM/m), under the directive `#PIMM_define`, alongside `#SYMMETRY_define`, `#PIMP_define`, `#PIMC_define`, `#PIMI_define`, `#PIMK_define` (`1j.tex:22-36`). But the per-machine directives were reserved words only: `1j.tex:297` 「現状では、予約語とされているものの展開方法等の詳細は未検討である。」 (at present the expansion method etc. of these reserved words has not been studied). A case-insensitive grep of the whole shipped tree for `pim/m`, `pimm`, `pim-m` finds, apart from 1j, only the distribution README: `vpim/vpim/README:5-6` "...processor of all models of the PIM except PIM/m" (README.j line 5: 「PIM の各モデル (PIM/m を除く) に共通する」 -- quoted from the README, not from TM-1044); the source hits are substrings of unrelated identifiers. TM-1044 itself never mentions PIM/m (all chapters: 0 hits); every Multi-PSI mention is listed per chapter below.
- 5j on lineage: Multi-PSI/V2 was the prototype for PIM; both execute KL1-B on every PE (`5j.tex:97-102`). For Multi-PSI/V2 the KL1-B execution scheme was first designed in C and then rewritten as Multi-PSI/V2 firmware, which was hard to convert directly (`5j.tex:109-112`); `5j.tex:110` 「それをMulti-PSI/V2のファームウェアに書き直していが、」. PSL was created to stay close to the firmware-level architecture of the real PIMs (`5j.tex:114-117`). How PIM/m's firmware was produced: not stated anywhere in the corpus.
- 3j/4j: `PIM/s` is the word-addressed simulator on which VPIM is checked (`3j.tex:27`); a PSL macro change was made because on real machines guaranteeing the destination tag cost too much (`4j.tex:36-38`).
- Footnotes and real-machine remarks, ch. 1:
  - `s1.tex:25-28` (fn): "Virtual PIM" is a historical name; it means the abstract machine interpreting KL1-B.
  - `s1.tex:172`: a real PIM with local memory may use it. 「PIMの実機が局所メモリを持つ場合は、適宜利用することにする。」
  - `s1.tex:178-179` (fn): on a machine with an 8-bit tag one bit is unused and free for measurement etc.
  - `s1.tex:222-223`: work registers are limited on real machines and are allocated when converting to real-machine code.
  - `s1.tex:281`: the primitive operations "correspond to the micro-instruction operations of a real PIM". 「実機PIMのマイクロ命令操作に相当する以下のような基本操作の列として定義できる。」
  - `s1.tex:349-351`: cache-control memory operations are optional per machine.
- Footnotes, ch. 2 (which layouts are VPIM-only and which are fixed from outside):

| cite | item | VPIM-only or required | quote |
|---|---|---|---|
| s2.tex:266-267 | atom number bit width / field allocation | free per real machine | 「各実機処理系において必ずしもVPIMと同じにする必要はない。}」 |
| s2.tex:286-287 | integers are exactly 32 bits | **required by PIMOS** (exception-tag allocation assumes 32 bits) | 「\footnote{整数は、必ず32ビットであることがPIMOS側から要請される。」 |
| s2.tex:314-317 | float storage (two INT words, IEEE 754 double) | free; PIM/p uses a contiguous 64-bit area after the CDESC word | 「PIM/pでは、CDESCワードに続く64ビットの連続領域を使用して」 |
| s2.tex:407-411 | string element storage | free, but `change_element_size/3` assumes elements are packed from the high-order bit; PIM/p packs elements without tags | 「各要素を上位ビット側から詰めることを前提としているので注意すること。」 |
| s2.tex:421-423 | CAR/CDR order in memory | free, **but the KL1 compiler settings must be changed to match** | 「ただし、その場合にはKL1コンパイラ等の設定を合わせて変更する必要がある。}」 |
| s2.tex:501-503 | vector pointer points at element 0 for both short and long vectors | VPIM design note (uniform element access) | - |
| s2.tex:754-756, 812-815 | "position of a built-in" in original/caller-code info | on PIM/p, which translates KL1-B to low-level machine instruction sequences, it is the start of that sequence; the compiler emits an extra KL1-B instruction before `enqueue` when caller info is needed | 「PIM/pのようにKL1-Bを複数の低レベル機械語命令列に変換してから実行する場」 |
| s2.tex:882-883 | "soft trace" vs CSP "limited trace" | terminology | - |

#### From ch. 3 (code module, KL1-B/s) and 5j

##### Footnotes (s3 has 3 \footnote; 5j.tex has none, only \thanks at 5j.tex:10, 20 = author e-mail / ICOT address)
- TM-1044.j_s3.tex:160-161: packages -- see PIMOS manual (ver. 2.5) §8.2 module management.
- TM-1044.j_s3.tex:399-400: demand-loading procedure needs coordination with PIMOS, not yet decided.
- TM-1044.j_s3.tex:1490-1492: predicate not found in entry table: current VPIM has no handling yet; plan = fail in guard, exception in body.

##### Real machine / other machines / VPIM-specific vs common
- TM-1044.j_s3.tex:35 code-module spec based on Multi-PSI's. TM-1044.j_s3.tex:39-41 machine-dependent vs common split is for porting to each maker's PIM and PIMOS machine independence.
- TM-1044.j_s3.tex:53, 141: header, ext-ref table, constant table, entry table = common to ALL machines; code area machine dependent (TM-1044.j_s3.tex:52-53, 710-712) though "basic structure must be the same on every machine" (TM-1044.j_s3.tex:711).
- TM-1044.j_s3.tex:238-241: PIM/p code area is untagged; word 15 holds relocation-like info for the unloader. TM-1044.j_s3.tex:145-146: sizes converted to tagged words on untagged-code machines.
- TM-1044.j_s3.tex:466, 562, 665-666, 809, 815, 868, 931: offsets/relative addresses inside code are in machine-dependent units.
- TM-1044.j_s3.tex:700, 712-713, 909, 956-958: code-area format and instruction set described are VPIM (PIM/s) = "KL1-B/s"; code area fully tagged only in VPIM. TM-1044.j_s3.tex:962: compiler names differ from VPIM source names.
- TM-1044.j_s3.tex:1540: store/write merged into one instruction "in VPIM". TM-1044.j_s3.tex:1679-1680: VPIM does no recursive collect. TM-1044.j_s3.tex:1686-1687, 1695-1696: reuse of vectors is short-vector only "in VPIM". TM-1044.j_s3.tex:944-945: Marker = VECT0 "in VPIM".
- Planned/unfinished: package slot spec unsettled, write 0 (TM-1044.j_s3.tex:165-166); Compile Information unused (TM-1044.j_s3.tex:202-203); version check at load "planned" (TM-1044.j_s3.tex:220-221); demand loading to be added to get_module/get_code group in future (将来, TM-1044.j_s3.tex:1455-1458); entry-table miss unhandled (TM-1044.j_s3.tex:1491).
- PIMOS/compiler dependencies: module is manipulated from PIMOS/KL1 level too (TM-1044.j_s3.tex:33-34); bad table data from OS/compiler/linker bugs must raise exceptions (TM-1044.j_s3.tex:324-326); PIMOS code manager reads header slots 9-15, VPIM does not (TM-1044.j_s3.tex:203-204, 212, 230, 242); hash mask and table sizes chosen by compiler/assembler (TM-1044.j_s3.tex:197, 659-660); compiler picks 2-way vs multiway branch (TM-1044.j_s3.tex:1597-1598); module_element / module_offset_to_code builtins expose element numbers/offsets to KL1 (TM-1044.j_s3.tex:191, 667).
- `これをコンパイルするとPIM実機のファームウェアプログラムとなることを狙っている。` (5j.tex:63) = "VPIM, compiled, is intended to become the firmware of the real PIM"; 5j.tex:148-158 PSL is macro-expansion (no value-returning subroutines) because stack-based subroutine calls are hard on the real machines; 5j.tex:524-526, 689-691 real-machine code generator still under development (only C generator done); 5j.tex:557-558 real-hardware parts are not in VPIM. 5j.tex:115 PSL chosen for affinity with real-PIM firmware-level architecture; 5j.tex:517-518 three aims = spec, real-machine firmware source, simulator source; 5j.tex:535 evaluate on simulator before the real machine; 5j.tex:53 PIM "currently under development"; 5j.tex:70-71 at present only PART of the spec is compiled and running as simulator; 5j.tex:685 VPIM currently being debugged on the simulator; 5j.tex:630 PSL environment on UNIX; 5j.tex:570 PIM/s needs KL1 cross compiler, assembler, linker.
- 5j.tex:97-102 Multi-PSI/V2 is PIM's prototype (loosely coupled, no shared memory; PIM = shared-memory clusters joined by a network); `Multi-PSI/V2ではKL1-B実行方式をはじめC言語で設計し、` (5j.tex:109) = "for Multi-PSI/V2 the KL1-B execution scheme was first designed in C" then rewritten as firmware by hand (5j.tex:109-112). 5j.tex:699 thanks to Multi-PSI and PIMOS groups. 5j.tex:678-682: PSL conceived spring 1988, coding from 1989, 50K steps incl. comments. PIM/m is never mentioned in either file; boot/SCSI/save-restore: not in TM-1044 (s3) nor 5j.

#### From ch. 4 (memory, MRB), ch. 5 (D-code), ch. 6 (scheduling)

##### Footnotes (all)
- `TM-1044.j_s4.tex:323` candidates for memory-resident free-list tops: sizes other than 1, 2, 16 words.
- `TM-1044.j_s4.tex:407-409` why surface-only collection: unbounded depth would thrash the cache on deeply nested structures.
- `TM-1044.j_s5.tex:104-108` goal pointers are HOOK-family typed; never instantiated by `wait`; enqueue built-ins are used only as D-code.
- `TM-1044.j_s5.tex:239` D-code module is also called the `builtin` module.
- `TM-1044.j_s6.tex:30-33` "executable" = not obviously suspended.
- `TM-1044.j_s6.tex:46` 4096 physical levels: 「\footnote{Multi-PSIと同様。}。」 = "same as Multi-PSI".
- `TM-1044.j_s6.tex:50` 「\footnote{Multi-PSIでは $2^{32}$であるが、符号なし演算のコストが高いマシンへの移植を考慮し、$2^{31}$とした。}、」 = "Multi-PSI has 2^32; 2^31 chosen for portability to machines where unsigned arithmetic is costly".
- `TM-1044.j_s6.tex:318-319` the idle PE really waits for any event (e.g. inter-cluster message arrival).

##### Real machine / PIM / Multi-PSI / VPIM-specific statements
- `TM-1044.j_s4.tex:180-181` 「さらに実機においては、マイクロ命令(内部命令)から」: on real machines the system code area also holds runtime routines called from micro-instructions.
- `TM-1044.j_s4.tex:321` 「レジスタに置く。ただし、PIM実機で物理レジスタ個数の制限などの」: real PIMs may keep some free-list tops in memory.
- `TM-1044.j_s4.tex:120-125` pseudo-registers in memory for lack of physical registers; `save`/`restore` driven by the KL1 compiler.
- `TM-1044.j_s4.tex:313` power-of-two rounding is stated as a VPIM choice 「VPIMでは」; `:254` page size 256 "independent of hardware"; `:406` surface-only collection is a VPIM choice; `:365` VPIM implements stop GC as well.
- `TM-1044.j_s4.tex:227` PIMOS code lives in the heap (so it is moved by GC).
- `TM-1044.j_s5.tex:166` 「現在VPIMでは、各PEにおいて実行すべきゴールがなくなった場合には、」 = "currently in VPIM" the idle goal is used.
- `TM-1044.j_s5.tex:193-195` COMMENTED-OUT source lines (not in the printed document): 「% なお、idleゴールを使った処理はVPIM(PIM/s)のみに必要なものであり、」 "idle-goal processing is needed only in VPIM (PIM/s), not on the real machines", followed by 「% 各実機においては必要ない。--> 嘘です(今井よりf-hatazaへ)」 = "that is false (Imai to f-hataza)" and an apology. I.e. the claim was retracted: real machines use the idle goal too. Also names VPIM as "PIM/s".
- `TM-1044.j_s5.tex:252` KL1-defined built-ins are made usable by registration with the KL1 compiler.
- `TM-1044.j_s6.tex:647` CLMax lowering is the "current" (現在は) policy, a known weak point.
- (from VPIM source structures/str_pr_goal_stack.psl.c:79-80, not TM-1044) stack entry "4 /* PIM/c, PIM/i */", "32 bytes PIM/p".
- No mention of PIM/m, PIM/p, PIM/c, PIM/i, PIM/k, PSI (other than Multi-PSI above), 将来, 未実装, 暫定 in s4-s6. No boot/SCSI/save-restore content in s4-s6 beyond "D-code module loaded at init" (s4:178, s5:19) and idle goal pushed at start (s5:168).

#### From ch. 7 (unification, suspend, merger) and ch. 8 (slit check)

Footnotes (all):
- s7:43 data whose body is in another cluster is also treated as unbound (guard).
- s7:305 EHOOK/EMHOK appear only inside 1-word cells.
- s7:393-394 structure constants may be placed in another cluster, so the `unify` instruction is emitted.
- s7:486-487 the unify_retry D-code simplification is "rather, to improve the readability of VPIM written in PSL" -- i.e. a VPIM implementation choice.
- s7:771 reply-hook record: see the inter-cluster chapter.
- s8:192-193 the sync signal is sent either by the PE that decremented the barrier last, or by the requester polling the barrier.
- s8:222-223 "reset the cause" = clear own PE's SCR bit for the event.
- s8:231 the per-reduction counter: "実機では省略できる。" (TM-1044.j_s8.tex:231-231) = "can be omitted on a real machine" (a real timer interrupt replaces it; inference).
- s8:457-458 pending non-GC message may make GC requests keep missing: "でメモリ消費が伴う場合、GC要求が空振りを続ける可能性がある。今後の課題。" (TM-1044.j_s8.tex:458-458) = "future work".

Mentions:
- 実機: only s8:231 (above). Multi-PSI: only s7:866 (streams are list cells there too). PSI (alone), PIM/m, PIM/p/c/i/k, PIMOS: no occurrence in s7 or s8 (every "PIM" hit is "VPIM").
- VPIM-specific statements: all exclusion by Compare&Swap "in VPIM" (s7:329-330); structure unify via D-code KL1 goals instead of a stack is a design choice with listed pros/cons (slow; failure cannot name the failing element) (s7:438-454); unify_retry for PSL readability (s7:486-487); resume-to-creating-PE is provisional (s7:767); "currently" 13 events / 12 SCR bits (s8:36-38); `p_PutSCRBit` unused (s8:69); software reduction counter as timer (s8:230-231); throw threshold "3 (tunable)" (s8:378); SCSI SPC interrupt handled through the slit check (s8:289-300).
- Compiler-determined (not runtime choices): guard `=` and repeated head variables both compile to `klb_equal` (s7:111-113); guard built-in output shared with a head arg compiled via a temp (s7:117-123); Write-Mode-first body structure unification sequence (s7:374-388); structure constants built at compile time, MRB black (s7:390-397).
- KL1 language rule: the guard cannot instantiate an unbound variable (s7:38-43).
- 将来 / 未実装 / 暫定: no occurrence. 今後: s7:767, s8:458.

#### From ch. 9 (inter-cluster)

- Footnotes (all in the chapter): TM-1044.j_s9.tex:435-435 "Weighted Export Count方式" (expansion of WEC). TM-1044.j_s9-network.tex:79-81, :159-161, :225-227 (same text three times): if heap is short when building / receiving / reassembling a packet, the message-processing state must be saved in the system fixed area and a GC requested — still under study. Quote TM-1044.j_s9-network.tex:81-81 「現在この部分は検討中である。}、」.
- 実機, PIM/m, PIM/p/c/i/k, Multi-PSI / マルチPSI, PSI, PIMOS, コンパイラ: no occurrence in any of the five files (grep). No comparison with Multi-PSI is made in this chapter.
- "VPIM" statements: level-0 / level-1 are VPIM's names (TM-1044.j_s9-msg-kl1data.tex:13-19); VPIM communicates in packets with multi-packet support (TM-1044.j_s9-network.tex:10-15); one datum = one word in VPIM (TM-1044.j_s9-network.tex:101-101); "currently" 24 message kinds prepared in VPIM (TM-1044.j_s9-message.tex:11-11); "currently" statistics = consumed resource amount (TM-1044.j_s9-message.tex:760-760 「現在、統計情報は消費資源量になっている」).
- Stated limits/assumptions: black export WEC (2 words) assumed not to overflow, more words needed as cluster count / memory grow (TM-1044.j_s9.tex:727-728); external-cell export has many exceptional variants "described later" but not in these files (TM-1044.j_s9-msg-kl1data.tex:358-360).
- Document inconsistencies (not resolved by the text): black %release figure tag WEXREF/VAL vs text BEXREF/BEXVAL (TM-1044.j_s9-message.tex:258-258 vs :269-269); %supply_BEXID reply-ID tag BEXREF/VAL vs WEXREF in the requests (:369-369 vs :306-306, :337-337); caption "%terminate" for %terminated (:603-603).
- 未実装, 暫定, 将来: no occurrence.

#### From ch. 10 (shoen / foster parent)

Footnotes (all in s10):
- TM-1044.j_s10.tex:62 shoen-module predicates are not part of the KL1 language spec.
- TM-1044.j_s10.tex:297-298 strictly there are timings where an FP cannot terminate even at child count 0 (explained later).
- TM-1044.j_s10.tex:310-311 more internal states exist, not described.
- TM-1044.j_s10.tex:766-767 resource_low is actually reported when the limit remainder gets fairly small.
- TM-1044.j_s10.tex:826-827 (re-used via \footnotemark at TM-1044.j_s10.tex:838, 854) any other state is an implementation error.
- TM-1044.j_s10.tex:870 goals of an FP are never run after abort.
- TM-1044.j_s10.tex:1068-1071 q TM-1044.j_s10.tex:1068:`\footnote{PIMでは、ここらへんの排他制御が大変複雑になっている。荘園里` = "in PIM the exclusion here is very complicated"; borrowing the real export/import tables for shoen/FP "was the cause of defeat"; registering FPs in a dedicated FP table would simplify things.
- TM-1044.j_s10.tex:1883-1884 exceptions not tied to execution (perpetual suspension found in GC) still find the FP from the goal record.

Real machine / Multi-PSI / PIM mentions (no 実機, no PIM/m, no PIM/c/i/k, no 未実装/暫定/将来 in s10):
- TM-1044.j_s10.tex:1299-1305 Multi-PSI attaches WTC to network messages; no overtaking there and the shoen always outlives the FP, so FP->shoen messages needed no WTC (q TM-1044.j_s10.tex:1303 `しかし、Multi-PSIではネットワークメッセージの追い越しがなく、里親が存在`). TM-1044.j_s10.tex:1306-1308, 1312 PIM has overtaking, so WTC also on FP->shoen messages.
- TM-1044.j_s10.tex:1340-1342 Multi-PSI discards logically-wrong start/stop; VPIM counts them (TM-1044.j_s10.tex:812-813).
- TM-1044.j_s10.tex:1437 WTC hold/resend is an extension from the Multi-PSI implementation to VPIM. TM-1044.j_s10.tex:1439-1445 q TM-1044.j_s10.tex:1445:`このため荘園里親間のすべてのメッセージにWTCをつけることにした。` = "so WTC is attached to all shoen<->FP messages".
- TM-1044.j_s10.tex:1456 q:`Multi-PSIでは、1クラスタ -- 1PEであるが、PIMは1クラスタ -- 複数PEで、` = "Multi-PSI: 1 cluster = 1 PE; PIM: 1 cluster = many PEs". TM-1044.j_s10.tex:1459 only explicit model mention: PIM/p's double hypercube as a network with non-unique routes.
- TM-1044.j_s10.tex:2055 and TM-1044.j_s10.tex:2247 KlbID q TM-1044.j_s10.tex:2055:`の番号はマルチPSIにおけるオペコードに相当するものである。` = "this number corresponds to the opcode on the Multi-PSI".
- TM-1044.j_s10.tex:1236 inside a PIM cluster several PEs run independently.
VPIM-specific vs required:
- VPIM choices: FP also in the shoen's own cluster, so even a 1-cluster system needs the inter-cluster machinery (TM-1044.j_s10.tex:960-962); per-PE caching of resource and child count because several PEs run goals of one FP (TM-1044.j_s10.tex:1165-1171); counters for start/stop overtaking (TM-1044.j_s10.tex:812-816, 1542-1546); "current stage" solution, may be revisited (TM-1044.j_s10.tex:1421-1422); design principle "do not slow ordinary reduction; shoen creation/control overhead is acceptable" (TM-1044.j_s10.tex:944-946).
- Compiler contract: output unification of a body built-in is done after the built-in executes (TM-1044.j_s10.tex:1012 q:`ケーションは、組込述語実行後に行なうことを、コンパイラがコード生成の約`).
- PIMOS-facing: exception tag bits 15-8 are PIMOS-defined (TM-1044.j_s10.tex:1912, 1935); NewCode/NewArgv are bound on the PIMOS side (TM-1044.j_s10.tex:1993); the shoen module forbids start-on-started / stop-on-stopped (TM-1044.j_s10.tex:813-815); ClauseInfo is a clause ID attached at compile time (TM-1044.j_s10.tex:2213).
- "At present": resource = reduction count only (TM-1044.j_s10.tex:123); only one trace cause, apply_tracing (TM-1044.j_s10.tex:2210).

#### From ch. 11 (GC), ch. 12 (debug), ch. 13 (SCSI)

##### Start-up, FEP, disk
- SCSI is the way disks and the FEP are reached: `本章では、ディスクやFEP(フロントエンドプロセッサ)を操作するためのSCSI` "this chapter [describes] the SCSI used to operate disks and the FEP (front-end processor)" (TM-1044.j_s13-1.tex:14-16). Tutorial figure: PIM, disk unit and FEP on one SCSI bus (TM-1044.j_s13-a.tex:13-55). PIM acts as both initiator and target (TM-1044.j_s13-a.tex:109-114).
- Boot statement: `PIM実機上でPIMOSを立ち上げる際、` "when PIMOS is started on a real PIM," the SCSI device-driver process is created first and SCSI built-ins are called only inside it; the driver is created by `PIMOS のブートストラップルーチンあるいはPIMOS自身である。` "the PIMOS bootstrap routine or PIMOS itself"; it is connected by streams (open / close / read / write commands) to the PIMOS loader written in KL1 and to user processes; it is resident on one PE of one cluster, the CPU that has the SCSI bus interface (TM-1044.j_s13-3.tex:12-23).
- `scsi_init` hands the sequencing variables and SCSI system parameters from the KL1 system to PIMOS and is normally called once at PIMOS start-up (TM-1044.j_s13-3.tex:408-413).
- IPL, boot image format, how the bootstrap routine itself is loaded, save/restore, FEP-side protocol, disk layout: not in TM-1044 (s13). PIM/m, PIM/c, PIM/i, PIM/k: no mention in s11, s12, s13-*.

##### KL1 SCSI built-ins (TM-1044.j_s13-3.tex:55-64)
- `scsi_command(SCSI,ArgVect,^NewData,^TransferredLength,^ID,^Result_I,^NewSCSI)`, ArgVect = {Unit,LUN_I,Command,Length,Direction,Data,DataPos}: one initiator session (until the command completes) (TM-1044.j_s13-3.tex:365-372).
- `scsi_transfer(SCSI,ArgVect,^NewData,^TransferredLength,^Result_T,^NewSCSI)`, ArgVect = {Unit,LUN_T,Kind,Length,Continue,Data,DataPos}: as target, one transfer with no bus-free phase inside (TM-1044.j_s13-3.tex:374-380).
- `scsi_abort(SCSI,ID,^NewSCSI)` cancels a buffered command; `scsi_reset(SCSI,Unit,LUN_T,^NewSCSI)` lifts the "transfers keep being cancelled" state of a unit/LUN after a failed target transfer; `scsi_init(^SCSI,^ReportInterruptionVect,^Info)` (TM-1044.j_s13-3.tex:390-413).
- They only RESERVE bus I/O; end of the KL1-B instruction = reservation done; order per (unit, LUN) is guaranteed, time is not (TM-1044.j_s13-3.tex:382-389). The SCSI argument only serialises calls; its value is an integer encoding cluster number (bits 31-16), processor number (15-8), own unit number (7-0) (TM-1044.j_s13-3.tex:189-210; TM-1044.j_s13-3.tex:360-363).
- Argument checks: unbound -> suspend, wrong type -> Illegal Input, out of range -> Range Overflow. Command = byte string of length 5, 9 or 11 (CDB without control byte); Continue 0/1; Direction 0..2 (3 = bidirectional unsupported); Kind in {0 data out, 2 data in, 4 command, 6 status, 7 message in}; Length 0..16K for `scsi_command`, 0..4K for `scsi_transfer`, 1 if Kind = 6; LUN 0..2047 (LUN_T may be []); Unit 0..7; DataPos 0..length of Data (TM-1044.j_s13-3.tex:67-156; TM-1044.j_s13-3.tex:640-643).
- Outputs: ^ID at reservation; ^Info = {command-record buffer size, transfer-record buffer size, extended-message flag 0/1, unused}; ^ReportInterruptionVect = 3-element vector {Unit,Msg,Next} unified when PIM is selected as a target; ^Result_I = error detail (16 bit, 31-16) | completion state (8 bit, 15-8) | status byte (7-0); ^Result_T = 0 normal / message byte string on attention / [] cancelled / error-detail integer (TM-1044.j_s13-3.tex:158-241; TM-1044.j_s13-3.tex:303-325).
- Result_I bits: 25 Unexpected Phase, 24 Unexpected Message, 23 Bus Released, 22 Transfer Interrupted, 21 Parity Error In Output Data, 20 Parity Error In Input Data, 19 Hardware Error, 18 Error In Selection, 17 Time Out, 16 Reset Condition Detected; 12 Error End, 11 Status Not Received, 10 Command Complete Not Received, 9 Canceled After Execution, 8 Canceled Before Execution (TM-1044.j_s13-3.tex:252-296). Result_T bits: 6 Invalid CDB Length, 5/4 parity out/in, 3 Hardware Error, 2 Error In Reselection, 1 Time Out, 0 Reset Condition Detected (TM-1044.j_s13-3.tex:327-346).
- Unresolved inconsistency in the source: the command record's completion state starts as 2#"00011000" "Bit 4 = Command Complete not received, Bit 3 = status not received" (TM-1044.j_s13-3.tex:488-492), whereas the Result_I table puts those at field bits 2 and 3 (bits 10 and 11) and Error End at field bit 4 (TM-1044.j_s13-3.tex:285-291).

##### Records (all in the system fixed area, free list per SCSI-connected PE)
Command record, fig. (TM-1044.j_s13-3.tex:521-623); pointer-side tag ATOM marks it; the pointer value is the reservation ID; max 16 at once (TM-1044.j_s13-3.tex:430-438). `*` = must be a GC marking root.

| word | content |
|---|---|
| 0 / 1 | next record / previous record |
| 2* / 3* | foster parent / goal execution environment (environment-record pointer, used to create the unify goals for outputs) |
| 4 | cancel flag (initially 0) |
| 5 / 6 | target unit number / logical unit number |
| 7 | command length (6, 10 or 12 = string length + 1) |
| 8 / 9 / 10 / 11 | transfer length / direction / start element in the data string / transferred-byte counter |
| 12* / 13* / 14* | KL1 output variables NewData / TransferredLength / Result |
| 15 | element position in the data buffer (updated on Save Data Pointer) |
| 16* | pointer to the Data argument (copied first if direction is DATA IN and Data's MRB is black) |
| 17 / 18 / 19 | status byte buffer (0) / error detail code (0) / completion state |
| 20 | next expected phase (for reconnect) |
| 21-25 | command body: descriptor 1 word + 4 words = 16 bytes (string body form, since VPIM has no byte-access instruction) |
| 26-4122 | transfer data buffer: descriptor 1 word + 4K words = 16 KByte |

- Transfer record, fig. (TM-1044.j_s13-3.tex:688-779); tag INT; max 64: words 0-3 as above; 4 initiator-side unit number; 5 target-side LUN; 6 kind; 7 length; 8 disconnect-after-transfer (Continue); 9 counter; 10 start element; 11*-13* NewData / TransferredLength / Result; 14 buffer position; 15* Data pointer (copied if DATA OUT and MRB black); 16 message length; 17 completion status; 18-22 message buffer (1 + 4 words = 16 bytes); 23-1047 data buffer (1 + 1K words = 4 KByte) (TM-1044.j_s13-3.tex:628-675).
- Selection record, fig. (TM-1044.j_s13-3.tex:830-853); tag FLT; max 64: 0 next; 1 selecting unit number; 2 message length; 3-7 message buffer. Used as message buffer on select and to remember a select that arrived during GC (TM-1044.j_s13-3.tex:784-818).
- Queues: reservation queue, bus-right queue, executing list (disconnected commands), post-processing queue (events during GC), abnormal-connection list (4-word heap cells, GC root) (TM-1044.j_s13-3.tex:859-901).
- Bus control: initiator and target automata, one PSL subroutine per state returning the next state (TM-1044.j_s13-1.tex:41-53); initiator path arbitration -> selection -> command -> data -> status -> Command Complete, with disconnect/reconnect state saved in the command record (TM-1044.j_s13-1.tex:68-80); no error recovery, errors end the sequence and are returned to KL1 (TM-1044.j_s13-1.tex:55-59). Controller: `SCSI プロトコルコントローラ MB87033B` "SCSI protocol controller MB87033B" (TM-1044.j_s13-1.tex:999-1001); Select and Transfer commands, 8 interrupt flags (TM-1044.j_s13-1.tex:1013-1039). Reselect interrupts are noticed at the slit check of goal reduction, by interrupt during GC, or when starting a (re)selection (TM-1044.j_s13-1.tex:621-626). Target select is delivered to KL1 by unifying the {Unit, Mesg, Next} vector, which resumes the hooked goal (TM-1044.j_s13-3.tex:35-43).
- "Not supported at present": commands without option messages (no message-out after selection) (TM-1044.j_s13-1.tex:455-457; TM-1044.j_s13-1.tex:916-917); only 6/10/12-byte commands (TM-1044.j_s13-3.tex:73-75).

##### Real machines, Multi-PSI, VPIM-only vs required
- `PIM実機処理系の抽象仕様であるVPIMとして定めたものである。` "[the record formats] are defined as VPIM, the abstract specification of the real-PIM implementations"; record counts and element formats should be optimised per PIM (TM-1044.j_s13-3.tex:423-426).
- `で使用する定数は実機処理系毎に変わり得る。` "the constants used [in range checks] may differ for each real-machine implementation" (TM-1044.j_s13-3.tex:47-49); ^Info returns the real-machine-dependent limits (TM-1044.j_s13-3.tex:165-173).
- PIM/p: `\footnote{PIM/p のように、{\tt p\_Read} と` "on a machine like PIM/p, where p_Read and s_ReadWithMRBor cost the same, this test [MRB OR while copying] has no overhead" (TM-1044.j_s11.tex:718-720).
- Multi-PSI: MRB incremental GC was implemented and proven there (TM-1044.j_s11.tex:33-34); its MRB maintenance at GC is dropped in VPIM (TM-1044.j_s11.tex:92-94); perpetual-suspension detection follows Multi-PSI (TM-1044.j_s12.tex:49-50), whose sequential pruning is why VPIM also uses 1 PE (TM-1044.j_s12.tex:318-321); candidate table differs (TM-1044.j_s12.tex:367-369); Multi-PSI has a dedicated GC bit for the Mark-and-sift visited mark (TM-1044.j_s12.tex:445-445); `VPIMではMulti-PSI用処理系と全く同じ仕様の組込述語` "VPIM provides a built-in with exactly the same specification as the Multi-PSI system" for both `apply_tracing` and `apply_spying` (TM-1044.j_s12.tex:665-665; TM-1044.j_s12.tex:805-806); Multi-PSI has a per-KL1-B-instruction interrupt facility in hardware (TM-1044.j_s12.tex:792-793).
- Required by PIMOS / compiler: the PIMOS listener uses the trace report and re-issues the built-ins (so the formats are PIMOS-visible: inference) (TM-1044.j_s12.tex:69-73); the compiler "should" emit traceable and untraceable code variants (TM-1044.j_s12.tex:793-799); the SCSI built-in interface is what the PIMOS device driver calls (TM-1044.j_s13-3.tex:12-23). VPIM-specific numbers: HEU 256, LDU 32, 16 / 64 / 64 records, 16K / 4K buffers. PSI (plain): no mention.
- Version notes: before VPIM 0.5 the GC ran without the LDU mechanism (TM-1044.j_s11.tex:399-401); the numbers are for "VPIM ver1.0".

##### Footnotes (every \footnote in the five files)
- s11: 29 most communication is 1 goal to 1 goal; 136 "Bottom" after Baker instead of "heap top"; 365 HEU = 256 words (ver1.0); 375 PE index j omitted in the figures; 381 the next page is probably another PE's; 400 VPIM before 0.5 ran with just this; 405 LDU = 32 words; 662 the counts behind MGHOK (merger inputs) and DREF (unbound variables left); 691 the mark is not against double copying; 713 because traversal is breadth-first; 718 PIM/p p_Read vs s_ReadWithMRBor; 809 no "skip retry if atomic" optimisation; 829 exclusion not needed for goal-record forwarding but done; 876 no EMGHOK type so EUNDF is used; 901 same for black import records; 913 as many entry points as predicates; 943 window between reporting terminated and `remove_shoen`; 1087 the ID rehash is strictly unnecessary, about 3-digit count.
- s12: 12 authorship (Inamura for the stop-GC detection section, Hirano for trace and spy, re-edited by Imai); 441 cyclic-structure bug, planned fix = top bit on vectors/lists, Multi-PSI uses a GC bit; 480 Sweep-and-Copy runs while another PE maintains the structure table, then sync, then Mark-and-sift; 715 TSGL = `D_TraceSubGoalListTop`; 719 CID = `D_CurrentTraceId`; 790 the mode test is "is `D_CurrentTraceId` EOL"; 871 `D_CurrentSpyId`, EOL = not spying; 880 the spy ID is set at the same time.
- s13-1: 56 results are reported to KL1 by binding KL1 variables; 694 the bus-free interrupt is normally limited to "connected as initiator" and is widened after a lost arbitration. s13-3: 40 (commented out in the source) "precisely, a D-code goal that does the unification is enqueued". s13-a: none.

## Appendix C. PIM/m processor, microcode, GC and boot

Scope: gaps 7 (memory management / GC), 8 (processing element, microcode, boot/IPL/FEP) and the
MRB note for gap 3. Compiled 2026-11-20 from the OCR'd ICOT reports, page images, four further
ICOT reports and three Mitsubishi Denki Giho issues fetched during this pass, and one ICOT Free
Software archive.

Conventions
- "PDF p.N" is the page of the PDF file; "printed p.N" is the number printed on the page.
- Verification label on every quote: **[IMG]** = read by me on the rendered page image;
  **[OCR]** = OCR text only, not checked against the image; **[TEXT]** = machine-readable file
  (HTML or a text/binary file inside an archive), decoded as described.
- **[INFERENCE]** marks anything that is my deduction and not a statement in a source.
- **[ADDS]** / **[CONTRADICTS]** are relative to the FGCS'92 PIM/m paper (pp. 425-435) baseline.
- ICOT report URLs: `https://www.airc.aist.go.jp/aitec-icot/ICOT/Museum/TRTM/TR/TRpdf/trNNNN.pdf`
  and `.../TM/TMpdf/tmNNNN.pdf` (abbreviated below as ICOT-TR/NNNN, ICOT-TM/NNNN).

### 0. Headline findings

1. **Firmware images for the PSI-III (same PU/CU chips) survive; that they contain the KL1
   microprogram is likely but unconfirmed (see 2.9 and section 8).** ICOT Free Software item 3, "KL1 Pseudo
   Parallel System for PSI-III" (`psdpim.tar.Z`, 1,354,121 bytes, still served, HTTP 200), is
   the "Pseudo PIM/m". Its README says directory `PMPSI.DIR` holds "KL0 and KL1 firmware" for
   the PSI-III (= PSI/UX), the workstation that uses the same PU/CU chips as PIM/m. It contains
   binary images only (no microassembler source), plus the console (CSP) software as SIMPOS
   package-template files, a boot script, and a parameter file giving the memory map. See 2.9
   and 3. I downloaded and inspected it; I did not reverse-engineer the images.
2. **Microinstruction format found**: a 64-bit field layout figure (図4) in the Mitsubishi
   Denki Giho article reissued as ICOT TR-733. See 2.3.
3. **MRB position**: the console software's own help text names tag values `REFo(06)` and
   `REFx(07)`, and lists tag mnemonics in o/x pairs. MRB is therefore the least significant
   tag bit in the Multi-PSI / pseudo-PIM/m KL1 tag encoding. See 4.
4. **Boot sequence found** as a script: CLEAR, INIT, IMPL (microcode load), PATCH, IPL
   (`pimm_ipl.kbn` + `.sym`), START at an address. See 3.
5. **Gap 7 is still thin for the real PIM/m.** Nothing read gives the FVP/FLP/FGP cell sizes
   or the GC trigger for PIM/m itself. What exists is Multi-PSI/V2 (TR-469) and the pseudo
   PIM/m parameter file and console strings ("Copying GC"). See 1.
6. **One index swap on the ICOT site**: the PDFs served as TR-870 and TM-1295 carry each
   other's titles (see 1.4). Neither describes the PIM/m or PSI heap.

### 1. Gap 7: PIM/m memory management and garbage collection

#### 1.1 What the PIM/m hardware papers say (almost nothing)
- TR-799, TM-1159, TM-862, TM-858, TR-564, TM-1074, TR-733 and TM-1109 contain no statement
  about heap layout, free-list pools, cell sizes, a batch GC, or GC tag bits for PIM/m. The
  only GC content is the MRB incremental collection support in the S stage (already known):
  Nakashima et al., TM-862 (1990), printed p.8 / PDF p.10: "In order to support this
  incremental garbage collection, the S stage passes the following information to the E
  stage. SRP (Single Reference Path): MRBs of all the pointers and terminal are of[f]. COL
  (Collectable): MRBs of the first two pointers are off." **[OCR]** (ICOT-TM/0862)
- Japanese parallel text: Nakashima, Takeda, Nakajima, "PIM/m 要素プロセッサのアーキテクチャ",
  TR-564 (May 1990), PDF p.5: "SRP(Single Reference Path) ... COL(Collectable): 最初の2つの
  ポインタのMRBがオフ" ("MRB of the first two pointers is off") **[OCR]**. Same content, no
  additions.
- TR-733 (below, 2.3) adds one sentence on reuse of freed memory, PDF p.5 / journal p.77(685):
  "空いたメモリ領域は再利用される" ("freed memory areas are reused") and that memory
  management is done "言語機能の一部としてマイクロプログラムによって" ("as part of the language
  function, by the microprogram") **[IMG]**. No sizes.
- The KL1-B listing in TR-733 図8 (PDF p.6 / journal p.78(686)) shows the reuse instruction
  `put_reused_structure R1, R2, 2` with the comment "入力Listのcell回収が可能なら再利用 /
  回収不可なら新しいList cellを割付" ("reuse the input list cell if it can be reclaimed;
  otherwise allocate a new list cell") **[IMG]**. **[ADDS]** an instruction name and operand
  shape for MRB-based cell reuse on PIM/m.

#### 1.2 Pseudo PIM/m parameter file and console strings (same firmware family, PSI-III host)
Source: `psdpim/SYSTEM.DIR/PIMM.PARAM` inside `psdpim.tar.Z` (ICOT Free Software no. 3), file
header "icpsi517::>sys>csp>SYSTEM.DIR>MPSI.PARAM Modified at 07-Aug-91 ... *** FOR PSEUDO
MULTI-PSI ***" **[TEXT]**; the file is two-byte JIS X 0208 without escapes, decoded by me.
These are parameters of the pseudo (single-CPU) system, so transfer to the real PIM/m is
**[INFERENCE]** unless stated.
- A copying GC exists and keeps three counters: section "%%% Copying GC %%%" with
  "(rqwd, 16'0), % Requested Words to GC", "(clwd, 16'0), % Collected Words by GC",
  "(gccnt, 16'0), % GC Count" **[TEXT]**.
- Heap limit is a parameter: "(kl1_heap_limit , 16'800)", with commented alternatives
  16'1000 and 16'1800 **[TEXT]**. Unit not stated; **[INFERENCE]** pages of 1 Kword (0x800
  pages = 2 Mwords), because the logical address has a 10-bit offset (2.6).
- Initial heap pointer: "(ihp , 16'E0000000), % Initial Heap Top Pointer" **[TEXT]**.
  **[INFERENCE]** top three bits 111 = area 7 with the 3/19/10 address split (2.6).
- Fixed tables live in "Area 5" (written `10 : address`): Multi-Packet Queue Table 0x180,
  Passive Unification Stack 0x200-0x400, Suspension Stack 0x400-0x800, Original Network Path
  Table 0x1000, Micro Trace Log Area 0x2000, Read Packet Buffer 0x3000-0xAFFF (0x8000
  entries), Structure Hash Table 0xB000 (0x400), Structure ID Hash Table 0xB400 (0x400), Goal
  Stack Entry Table "GSET" 0xB800 (0x100 entries), Black Export Hash Table 0xBC00 (0x800),
  Black Export Table 0xC400 ("Size 4 * Entry", 0x1200), Black Import Hash Table 0x10C00,
  Black Import Table 0x11400 ("Size 5 * Entry"), White Export Table 0x13C00 (0x1000), White
  Import Table 0x14C00 (0x1000), SCSI record base 0x15C00 **[TEXT]**. **[ADDS]** concrete
  table names and record sizes (4 words per black export entry, 5 per black import entry).
- Resource and WTC units: "(wtctu, 16'400) % WTC Throw Unit", "(wtcsu, 16'1000000) % WTC
  Supply Unit", "(rsctu, 16'1000) % Resource Throw Unit", "(rscsu, 16'10000) % Resource
  Supply Unit", "(atomc, 16'200) % Atom Counter (0 ~ 2 ** (24-1))" **[TEXT]**.
- Console message strings in `INSTALL.DIR/pimmcsp.ptf` (strings extracted, not the code):
  "Copying GC End : \x words collected", "Copying GC Memory Shortage : \x words",
  identifiers `copying_gc_end`, `copying_gc_short`, `synchronized_gc_start`,
  `synchronized_gc`, `set_kl1_heap_limit`, `kl1_heap_limit_a`, `kl1_heap_limit_b`,
  `csp_goal_record_inspector`, `get_goal_record_1`, `get_goal_record_2`,
  `free_kl1_value_cell_for_input` **[TEXT]**. **[INFERENCE]** two heap limits a/b fit a
  two-semispace copying collector; "synchronized GC" fits all PEs collecting together.
- Free-pool names FVP/FLP/FGP do not occur in any string of the archive (searched).

#### 1.3 Multi-PSI/V2 (predecessor firmware; label: NOT PIM/m)
Miyauchi et al., "Tracing Garbage Collection for KL1 on the Multi-PSI/V2 System", TR-469
(June 1989) (ICOT-TR/0469). Skim only, another agent covers it.
- Copying, half the heap active: "data cells are allocated to a half of the heap area, the
  active heap, until it is used up and the tracing garbage collector are invoked." printed
  pp.5-6 / PDF pp.6-7 **[OCR]**.
- GC bit: "Generally one bit of a memory cell is used as a GC bit to indicate whether it has
  been already copied or not." PDF p.7 **[OCR]**; "To identify the four different states,
  unmarked, marked once, twice and more than twice, the GC bits and MRB of the object in old
  area are used." PDF p.10 **[OCR]**.
- Free lists by size: "There are several free lists according to the size of cells. When a
  new data is created and the corresponding free list is empty, the list is extended by
  consuming the heap area." printed p.10 / PDF p.11 **[OCR]**.
- Heap size in the measurement: "4 processors with 12 Mword of heap memory. (Physical memory
  => 16 Mword)" PDF p.14 **[OCR]**.
- **[INFERENCE]** PIM/m "inherits Multi-PSI's architecture and firmware" (FGCS'92 demo
  document, search snippet only, not opened), so the same scheme (size-classed free lists
  refilled from the heap, copying GC when the active half is used up) is the most likely
  PIM/m design; no PIM/m source read here confirms it.

#### 1.4 GC algorithm reports that turned out not to describe PIM/m or PSI
- **Index mismatch.** The ICOT index lists TR-870 as "データ構造の一部を指すポインタを許容する
  コピー型ゴミ集め方式" and TM-1295 as "スタック領域が不要な深さ優先順コピー型ゴミ集め方式".
  The served PDFs are the other way round: `tr0870.pdf` cover and p.2 read "スタック領域が
  不要な深さ優先順コピー型ゴミ集め方式 ... Depth-First Copying Garbage Collection without Extra
  Stack Space, Hiroshi Nakashima (Kyoto University), Takashi Chikayama (ICOT)"; `tm1295.pdf`
  reads "データ構造の一部を指すポインタを許容するコピー型ゴミ集め方式 ... Copying Garbage
  Collection with Substructure Pointers, Hiroshi Nakashima (Kyoto University)" (both April
  1994) **[IMG]**. TR-907 (Feb 1995) is a later version of the depth-first paper.
- Depth-first paper (file `tr0870.pdf`), printed p.9 / PDF p.11: "プログラムはC言語によって
  作成し,主記憶容量16MB,キャッシュ容量64KBのSparcStation1で実行した" ("the program was
  written in C and run on a SparcStation 1 with 16 MB main memory and 64 KB cache") **[IMG]**.
  It is a generic algorithm study; no PIM/m, PSI, KL1 or ESP heap, header or descriptor
  layout. Abstract (English, PDF p.2): "the proposed methods don't require that a data
  object itself indicates whether it is a pointer" **[OCR]**.
- Substructure-pointer paper (file `tm1295.pdf`): generic; mentions logic-language
  variable-reference pointers only as an example ("論理型言語の処理系の変数参照ポインタのよう
  に,もともと透明ポインタを持つような場合には,ポインタ型の追加は不要である", PDF p.2
  **[OCR]**: "where transparent pointers already exist, as with variable reference pointers
  in logic language implementations, no extra pointer type is needed"). No machine named.
- K. Nakajima, "Piling GC - Efficient Garbage Collection for AI Languages", TR-354 (March
  1988) (ICOT-TR/0354): a proposal, not an implementation report. "Piling GC will be
  implemented and evaluated on the Flat GHC system on the Parallel Inference Machine [4]
  which is being developed at ICOT." PDF p.13 **[OCR]**. Trigger in the proposal: "Objects
  are created in the work area until the pages for the area is exhausted. When the work area
  becomes full, only the active objects are copied to the piling area." PDF p.5 **[OCR]**.
  Whether it was ever used on Multi-PSI or PIM/m: not found.

#### 1.5 Gap 7 not found
- FVP / FLP / FGP record sizes (words per variable cell, list cell, goal record) for PIM/m.
- PIM/m batch GC trigger condition and whether all PEs collect together.
- PIM/m GC tag bits (which of the 8 tag bits, if any, are reserved for the collector).

### 2. Gap 8: processing element

#### 2.1 Chip set, cycle time, WCS
- Machida et al., "A VLSI Chip Set for a Large Scale Parallel Inference Machine: PIM/m",
  TR-799 (Aug 1992), printed p.2 / PDF p.3: "it is a 5-stage 40-bit pipelined microprocessor
  under the control of a microprogram stored in a 32K-word WCS" **[OCR]**.
- **WCS address is 15 bits, data 64 bits.** Masuda, Tanabe, Ikeda, Fukazawa, Iwayama,
  Nakashima, "三菱AIワークステーション《MELCOM PSI/UXシリーズ》のハードウェアシステム",
  三菱電機技報 Vol.65 No.6 (1991) pp.602-607, 図3 "推論部のハードウェア構成", p.84(604) /
  issue PDF p.90: signals "WCS_ADR<14:0>", "WCS_DATA<63:0>", box "WCS 32K×64ビット"; also
  "IC_DATA<39:0>", "DC_ADDR<31:0>", "DC_DATA<39:0>", "MM_ADDR<31:0>", "MM_DATA<46:0>", "DCM
  4K×40ビット", "TRCM", "FPP", "IOC", "XAD<31:0>", "XINTR", "EDCD<31:0>", "EADR<31:0>"
  **[IMG]**. (URL: https://www.giho.mitsubishielectric.co.jp/giho/pdf/1991/9106.pdf)
  **[ADDS]** signal names and widths. MM_DATA 47 bits = 40 data + 7 ECC **[INFERENCE]**,
  consistent with TR-564 PDF p.6 "7ビットECC" **[OCR]**.
- **[CONTRADICTS, within sources]** WCS size. Ando, Machida, Nakashima, Nakaya, "A 40-bit
  Microprocessor for Logic Programming Language", TM-858 (Feb 1990), PDF p.1: "under the
  control of microprogram stored in 64-bit by 64-Kword writable control store" **[IMG]**.
  Every other source says 32K. The same paper's Table 1 gives "Microprogram address stack
  16bit x 32word" **[IMG]**. **[INFERENCE]** the PU's microprogram address is 16 bits (64K
  addressable) and the boards populate 32K (15 address lines in the PSI/UX figure).
- **Cycle time: three different numbers.**
  - 60 ns: TR-564 PDF p.3 "要素プロセッサのマシン・サイクルは60nsである" ("the machine
    cycle of the element processor is 60 ns") **[OCR]**; TR-799 Table 3 "PU 60nsec" **[OCR]**.
  - 65 ns: Furutani et al. (cover) / TM-1074 "並列推論マシン(PIM/m)用VLSI" (July 1991),
    表1, printed p.24 / PDF p.25: "動作サイクル 65nsec" **[IMG]**; TR-733 表1 "サイクル時間
    65ns" **[IMG]**; Giho 65(6) 表2 "クロック 65ns (15.4MHz)" **[OCR of the journal's own
    text layer]**.
  - 16.7 MHz typical / 15.4 MHz worst case: TM-1159 (Feb 1992) PDF p.3: "has correctly
    executed the KL1 at 15.4 MHz under worst case condition" **[OCR]**; TR-799 printed p.9:
    "at 16.7 MHz under typical condition" **[OCR]**. 1/15.4 MHz = 64.9 ns, so 65 ns is the
    worst-case system cycle and 60 ns the typical one **[INFERENCE]**.
  - Chip-level: TR-799 Table 5 "Chip cycle time 30nsec / 33nsec / 28nsec" for PU/CU/NU
    **[OCR]** (the last digit group is garbled as "?8nsec" in TR-799 and reads "28" in
    TM-1159's table OCR).
- Device table, TM-1074 表1 **[IMG]**: PU 0.8 um, 384K transistors (RAM 270K, PLA 4K, logic
  110K), 16.3x13.6 mm, 2.5 W; CU 1.0 um, 610K (RAM 542K, PLA 3K, logic 65K), 14.5x14.8 mm,
  2.3 W; NU 1.0 um, 329K (RAM 261K, logic 68K), 14.2x14.0 mm, 2.2 W; package 361 PGA.
  TR-799 Table 5 adds scan path stages 409/420/268 and pad counts 352/347/325 **[OCR]**.
- Board: TR-733 PDF p.3 / journal p.75(683): PE = one processor board + one memory board;
  "メモリボードは4MビットDRAMを使用することによって80Mバイトの容量を実現" (80 MB = 16
  Mwords) **[IMG]**; TR-799 printed p.10: "32.5-cm x 31.0-cm PIM/m processing element board"
  **[OCR]**.

#### 2.2 On-chip memories and register files (PU)
TM-858 Table 1 "Device Features", PDF p.2 **[IMG]**:

| Item | Value |
|---|---|
| Data width | 40bit |
| ALU | 32bit |
| Operation decode table | 54bit x 512word |
| Register file | 40bit x 32word x 2 |
| Work register | 40bit x 32word |
| Tag dispatch table | 8bit x 512word |
| Microprogram address stack | 16bit x 32word |
| Transistor count | 384K |
| Chip size | 16.3 x 13.6 mm |
| Package | 361 pin PGA |
| Clock | 16.7MHz |

- Text, PDF p.1 **[IMG for the first clause, OCR for the rest]**: "an instruction provided by
  an instruction cache in the CU is decoded with a 54-bit by 512-word operation decode table
  (OPT)"; "The A-stage has copies of a 40-bit by 32-word register file (RF) and a few special
  registers for FGHC execution in the E-stage"; "Main resources are a 32-bit ALU, a 40-bit by
  32-word register file (RF), a 40-bit by 32-word work register (WR), an 8-bit by 512-word
  tag dispatch table (TGT) and a 16-bit by 32-word microprogram address stack (MSTK)."
- **[ADDS]** sizes: OPT 512 entries of 54 bits (so the decode index is 9 bits; **[INFERENCE]**
  8-bit opcode plus one mode/class bit, or a 9-bit opcode field; no source says which), TGT
  512 x 8 (**[INFERENCE]** 8 dispatch blocks of 64 tag values, or 2 blocks of 256), MSTK depth
  32, ARF = copy of RF (TR-799 printed p.3: "ARF is a copy of a register file(RF) of the
  E-stage" **[OCR]**).
- TM-858 Figure 2 block labels **[IMG]**: D-stage: IR, OPT. A-stage: OPR, IR, RF, a
  three-register stack "PC / ER(?) / CPR", Address Calculator. R-stage: OPR, IR, MAR.
  S-stage: OPR, IR, MAR, MDR. E-stage phase 1: DR, a stack "PC / SR / GR / LC / IR", RF, WR;
  phase 2: MDR, MAR, REG, ALU; control: TGT, Condition Generator, Branch Address Generator,
  MIR; pins "Microinstruction", "WCS Address", "Instruction Cache Data", "Data Cache
  Address", "Data Cache Data". The middle label of the A-stage stack is not legible (reads
  "ER" or "FR").
- Giho 65(6) 図6 "PU(Processing Unit)の構成", p.86(606) **[IMG]**: "RF 32w | WR 32w | sp.
  Reg." feeding phase 2 "XR/YR | MAR1/2 | MDR1/2", "uProgram Control", pin "WCS". Same
  drawing as TR-564 図2.
- Console register names for the real machine are listed in the pseudo-PIM/m console package
  strings (`pimmcsp.ptf`) **[TEXT]**, apparently one name per CSP-visible register:
  `memory_data_register`, `micro_instruction_register`, `micro_program_counter_set`,
  `work_register`, `memory_address_register`, `temporary_register`, `global_top_pointer`,
  `structure_pointer`, `instruction_register`, `rf_address_register`,
  `rf_validity_flag__register`, `alu_flag_and_condition_code`, `switch_flag`,
  `reference_tag_register`, `tag_dispatch_address_register`, `jump_register`,
  `micro_stack_address_register`, `micro_stack_data_register`, `byte_position_register`,
  `interrupt_mask_register`, `pipeline_control_register`, `instruction_register_in_dec`,
  `reference_tag_register_in_adr`, `area_base_register_in_adr`, `micro_program_counter`,
  `machine_status_register`, `machine_control_register`, `interrupt_status_register`,
  `register_file`, `tag_dispatch_table`, `micro_stack`, `console_interface_register`,
  `d_cache_process_id_register`, `i_cache_process_id_register`, `cache_unit_status_register`,
  `syndrome_register`, then the network registers (2.8). **[ADDS]**; **[INFERENCE]** these
  are PU/CU/NU registers because they include pipeline, D/I-cache and TLB items that PSI-II
  (non-pipelined, single cache) does not have. The companion `mpsicspR.ptf` carries the
  older PSI-II/Multi-PSI list (`instruction_fetch_register`, `instruction_buffer_register`,
  `loop_counter`, `dispatch_memory`, `writable_control_store`, `page_map_memory` ...).

#### 2.3 Microinstruction format (64 bits)
Source: K. Nakajima, Masuda, H. Nakashima, Kondo, Takeda, Murasawa, Komori, "並列推論マシン
PIMのアーキテクチャ", 三菱電機技報 Vol.66 No.6 (1992) pp.74-78 (682-686), reissued as ICOT
TR-733 (Jan 1992) (ICOT-TR/0733; journal issue
https://www.giho.mitsubishielectric.co.jp/giho/pdf/1992/9206.pdf, downloaded, not re-read).
図4 "要素プロセッサのマイクロ命令フォーマット", journal p.76(684) / TR PDF p.4 **[IMG]**.

Text, same page **[IMG]**: "E:機械命令の主な処理を64ビット幅のマイクロプログラムで実行する。
マイクロ命令は32K語の高速のマイクロ制御メモリに格納され,毎サイクル読み出されて実行される。
... 条件分岐,内部レジスタ間データ転送,レジスタ間演算,キャッシュアクセス,条件フラグ設定,
内部カウンタ操作などが1命令で同時に行える。特に,タグ値などの判定から分岐完了までが2サイ
クルで行える"
("E: the main processing of a machine instruction is executed by a 64-bit-wide microprogram.
Microinstructions are stored in a fast 32K-word micro control memory and read and executed
every cycle. ... Conditional branch, data transfer between internal registers,
register-to-register arithmetic, cache access, condition flag setting and internal counter
operation can all be done at once in one instruction. In particular, from the test of a tag
value to completion of the branch takes two cycles.")

Field legend as printed **[IMG]** (name<width> : meaning):

| Field | Width | Printed meaning | Translation |
|---|---|---|---|
| CCF | 5 | キャッシュ/メモリ制御 | cache / memory control |
| DSTF | 5 | 引数/制御レジスタ セット指定 | argument/control register: set (write) select |
| SC1F | 5 | 引数/制御レジスタ 選択指定(1) | argument/control register: read select 1 |
| SC2F | 5 | 引数/制御レジスタ 選択指定(2) | argument/control register: read select 2 |
| SD1F | 3 | 内部ワークレジスタ セット指定(1) | internal work register: set select 1 |
| SD2F | 2 | 内部ワークレジスタ セット指定(2) | internal work register: set select 2 |
| AS1F | 3 | ALU左入力レジスタ指定 | ALU left input register |
| AS2F | 2 | ALU右入力レジスタ指定 | ALU right input register |
| ADF | 3 | ALU出力レジスタ指定 | ALU output register |
| ALF | 3 | ALUオペレーション制御 | ALU operation |
| JMPF | 3 | 分岐オペレーション制御 | branch operation |
| CNDF | 4 | 分岐条件制御 | branch condition |
| EM1 | 6 | 即値/オペレーション修飾子(1) | immediate / operation modifier 1 |
| EM2 | 6 | 即値/オペレーション修飾子(2) | immediate / operation modifier 2 |
| EM3 | 4 | 即値/オペレーション修飾子(3) | immediate / operation modifier 3 |
| * | 計5 | 条件フラグ設定,カウンタ操作 | condition flag setting, counter operation (5 bits in total) |

Widths sum to 59 + 5 = 64. The figure prints only the byte-boundary numbers (63, 56 55, 48
47, 40 39, 32 / 31, 24 23, 16 15, 8 7, 0). Bit positions below are measured from the drawn
box widths, so they are **[INFERENCE from figure geometry]**; they are self-consistent (each
row sums to 32, and every printed boundary lands where the widths put it):

| Bits | Field | Bits | Field |
|---|---|---|---|
| 63 | * | 31-29 | ADF |
| 62-58 | CCF | 28-26 | ALF |
| 57 | * | 25-23 | JMPF |
| 56-52 | DSTF | 22-19 | CNDF |
| 51-47 | SC1F | 18 | * |
| 46-42 | SC2F | 17-16 | * (2 bits) |
| 41-39 | SD1F | 15-10 | EM1 |
| 38-37 | SD2F | 9-4 | EM2 |
| 36-34 | AS1F | 3-0 | EM3 |
| 33-32 | AS2F | | |

Reading against the datapath **[INFERENCE]**: DSTF/SC1F/SC2F are 5 bits = 32 entries, matching
RF 32w / WR 32w / special registers (phase 1); SD1F/SD2F/AS1F/AS2F/ADF select among the six
phase-2 registers (XR, YR, MAR1/2, MDR1/2); EM1..EM3 (16 bits) can hold a tag immediate
(8 bits), a dispatch-table block number, or a branch offset.

Related, already known but worth pinning: tag test costs two cycles in the E stage. TM-862
printed p.7 / PDF p.9: "Those operations requires two machine cycles. The first cycle makes
the jump condition or offset, and the second generates the jump address and fetches the
microinstruction." **[OCR]**

Comparison row: TR-733 表1 **[IMG]** gives "マイクロ命令: 64ビット水平型" for PIM/m and
"53ビット水平型" for Multi-PSI (PSI-II); pipeline "5段" vs "なし"; cache "データ4K語×1,
命令1K語×1" vs "データ,命令共通4K語×1"; network "10ビット/チャネル, 3.84Mバイト/秒・ch" vs
"5Mバイト/秒・ch"; LSI "CMOSセルベース0.8/1.0um 3種" vs "CMOSゲートアレー8K/20Kゲート9種".

#### 2.4 Pipeline, nano-code, decode
- Nano-code and RAM decoder: TR-564 PDF p.3 **[OCR]**: the D-stage table holds the
  microprogram start address plus control for address calculation and operand set-up for the
  downstream stages; TM-1074 printed p.5 / PDF p.6 **[IMG]**: "DステージにはデコードのためのRAM
  テーブルがあり,マイクロプログラムの実行開始アドレスや下流のステージを制御するためのナノ
  コードが格納されている。デコーダをRAMで構成したことは,複数言語のサポートや,マイクロ
  プログラム開発に多大な効果をもたらしている。" ("The D stage has a RAM table for
  instruction decode, holding the microprogram start address and the nano-code that controls
  the downstream stages. Building the decoder from RAM has greatly helped support of several
  languages and microprogram development.") TR-799 printed p.3 names the languages: "makes it
  possible to execute several languages such as ESP, KL1, and Lisp" **[OCR]**.
- **[ADDS]** D-stage decides operand kinds: TR-733 journal p.75(683) **[IMG]**: "D:命令
  キャッシュから読み出された機械語命令のデコードを行う。すなわち,機械語命令コードからオペ
  ランドのタイプ(レジスタ,即値,メモリアクセス)やオペランドに対する処理を決定する。"
  ("D: decodes the machine instruction read from the instruction cache; that is, from the
  instruction code it determines the operand types (register, immediate, memory access) and
  the processing of the operands.")
- **[ADDS]** branch prediction and refetch: same page **[IMG]**: "A:メモリアクセスオペランドの
  アドレス計算を行う。次命令若しくは分岐先命令のフェッチも行う。なお,分岐予測が失敗した場合
  や予測が不可能な場合には,Eステージの指示によって再フェッチが行われる。" ("A: computes
  memory operand addresses and fetches the next or branch-target instruction. When branch
  prediction fails or prediction is impossible, a refetch is done on the E stage's order.")
- **[ADDS]** S stage reads the first microinstruction: same page **[IMG]**: "S:Eステージでの
  マイクロ命令の読出し,オペランドのセットアップ,及びデレファレンス機能がある。" ("S: reads
  the microinstruction for the E stage, sets up operands, and dereferences.")
- **[ADDS]** last microinstruction of a routine: TM-1074 printed p.6 / PDF p.7 **[IMG]**:
  "マイクロプログラムルーチンの最後のマイクロ命令では,フェーズ1はSステージによって制御され,
  オペランドのセットアップのために使用される。" ("In the last microinstruction of a
  microprogram routine, phase 1 is controlled by the S stage and used for operand set-up.")
- A-stage special address registers by language, TM-862 printed p.6 / PDF p.8 **[OCR]**:
  "In the KL1 execution, the special address registers contain the address of the
  alternative, and the base of a frame representing a goal, the execution of which is
  postponed. In the ESP execution, they contain the address of continuation, and the base of
  environment." TR-564 PDF p.4 names the KL0 ones "(E)" and "continuation (CP)" **[OCR]**.
- Pipeline break cost, TM-862 printed p.6 **[OCR]**: "the break is mainly caused by
  backtracking ... backtracking takes many cycles which are enough to re-fill all the
  stages".
- Step counts for append (recursive clause), TM-862 printed p.11 / PDF p.13 **[IMG]**:
  PSI-II "36 cycles for KL1, and 15 cycles for ESP"; two-phase "37 ... 23"; two-stage
  "29 ... 19"; PU "20 cycles for KL1, and 13 cycles in ESP". **[CONTRADICTS, within
  sources]** TR-799 Table 3 gives "PU 60nsec 11steps" for the ESP append and an overall
  factor 3.51 (1.55 x 1.67 x 1.36) **[OCR]**; TM-1159 says "a factor of 3.78" **[OCR]**.
  The measured chip evidently needed 11 steps where the 1990 simulation said 13.
- Performance: TM-862 Table 1 **[IMG]** "PIM/m(PU) 833/1282" KLIPS (KL1/ESP, simulated),
  "PSI-II 179/430"; TM-1074 表2 **[IMG]** "PIM/m 0.60 / 1.40 MLIPS (KL1/KL0), Multi-PSI/v2
  0.14, PSI-II 0.43"; TR-733 **[IMG]** "530K LIPS" for KL1 append; TR-799 Table 4 **[OCR]**
  append 1,000 elements 1.63 msec (PIM/m) vs 7.80 msec (Multi-PSI/v2).

#### 2.5 Word format and tag
- TM-1074 図3 "データの内部表現", printed p.15 / PDF p.16 **[IMG]**: bit labels "39 tag 32 |
  31 value 0"; examples (a) integer 1990, (b) list -> cell at 1990/1991, (c) reference 1991.
  Text printed p.4 / PDF p.5 **[IMG]**: "1ワードの幅は40ビットであり,その内の8ビットがタグ
  として用いられている" ("a word is 40 bits wide, of which 8 bits are used as the tag").
  **[ADDS]** the tag is the top byte, bits 39-32.
- No PIM/m paper gives the internal layout of the 8 tag bits. Predecessor (PSI-II, KL0):
  Nakashima & Nakajima, "Hardware Architecture of the Sequential Inference Machine: PSI-II",
  TR-265 (June 1987) (ICOT-TR/0265), printed p.4 / PDF p.5: "Data is represented by a 40-bit
  word separated into 8-bit tag field and 32-bit value field, as shown in Figure 1. The top
  two bits of the tag field are used as mark bits for the garbage collection. The lowest six
  bits represent data type" **[OCR; Figure 1 labels "GC | type | value" IMG]**.
  **[INFERENCE]** PIM/m KL1 keeps a 2-bit GC field + 6-bit type field: the pseudo-PIM/m tag
  list (section 4) has about 60 mnemonics, which fits 6 bits, and TM-858's 512-entry tag
  dispatch table fits 8 blocks x 64 types (PSI-II: 2K entries = 32 blocks x 64, TR-265
  printed p.9 **[OCR]**).
- MRB in the tag: see section 4.

#### 2.6 Memory system: caches, TLB, logical address
- Logical address, TR-564 図5, PDF p.6 **[IMG]**: fields "area (3) | page number (19) |
  offset (10)". Text PDF p.6 **[OCR]**: stacks are assigned to different areas; the data TLB
  entry address is the XOR of the area field (bit-reversed) / process id with the low page
  number bits, to stop stacks in different areas fighting for entries. PSI-II has the same
  split: TR-265 Figure 2 **[IMG]** "31-29 area number | 28-0 inner area address"; TR-265
  printed p.6 **[OCR]**: 19-bit page field, 10-bit offset, 26-bit physical address, eight
  Page Map Base Registers.
- Instruction cache, TM-1074 printed pp.7-8 / PDF pp.8-9 **[IMG]**: "4w/blockのダイレクト
  マッピング方式の1Kwのデータメモリと256wのタグメモリならびに2セット,64エントリのセット
  アソシアティブ方式のTLB" ("1 Kw data memory, direct mapped, 4 words per block, 256-word
  tag memory, and a 2-set, 64-entry set-associative TLB"); hit ratio 94.4%; TLB 99.83%.
- Data cache, same pages **[IMG]**: "4w/blockのダイレクトマッピング方式の1Kwのタグメモリと,
  2セット,64エントリのセットアソシアティブ方式のTLB ... データメモリはチップサイズの関係
  からチップ外部に置かれている" (1 Kw tag memory = 4 Kw of data in 4-word blocks, data array
  off chip); hit ratios 99.2% (cache) and 99.88% (TLB).
- **[CONTRADICTS, within sources; reconciliation is my inference]** TLB: "2セット,64エントリ" (TR-564, TM-1074) vs
  "32entry 2-way" (TR-799 / TM-1159 Table "Cache Features" **[OCR]**). Both describe 64
  entries in total = 32 sets x 2 ways **[INFERENCE]**.
- TR-799 Table 1 **[OCR]**: instruction cache "Physical, Direct map, 5KBytes, Tag entry 256,
  TLB 32entry 2-way, LRU"; data cache "Physical, Direct map, 20KBytes (off chip), Tag entry
  1024, TLB 32entry 2-way, LRU"; rows "Parity", "SECDED", "Coherency write back", "DRAM
  refresh". 5 KB = 1 Kw x 40 bit; 20 KB = 4 Kw x 40 bit.
- Instruction-cache PC copy, TM-1074 printed p.8 **[IMG]**: the PU / instruction-cache
  interface is a shared address/data bus, so the cache block holds a copy of the PU program
  counter, auto-incremented on fetch; "PUチップが分岐処理を行う際には正しいプログラムカウンタ
  の値をセットする必要がある" ("when the PU branches it must set the correct program counter
  value"). TR-564 PDF p.6 **[OCR]** adds that about 20% of instructions pay this and that
  the net slowdown is about 1.5% (digits OCR-only).
- **[CONTRADICTS, within sources]** Trail buffer size: "Trail Bufferという32エントリのスタック"
  (TM-1074 printed p.9 / PDF p.10 **[IMG]**; TR-564 PDF p.6 **[OCR]**) vs "16-word x 32-bit
  RAM" and "can hold up to 16 addresses" (TR-799 printed p.6-7, TM-1159 **[OCR]**). The
  1990-91 Japanese design papers say 32, the 1992 chip papers say 16; the fabricated chip
  value is presumably 16 **[INFERENCE]**. Function, TM-1074 printed p.9 **[IMG]**: addresses
  are pushed automatically on variable-binding writes, and on backtrack "アドレスのポップ
  アップとアドレスのリセットのための書き込みがCUチップ内部で行われる" (pop and reset writes
  happen inside the CU). This is a KL0/ESP feature; KL1 does not backtrack.
- ECC, TM-1074 printed p.9 **[IMG]**: single-bit correct / double-bit detect check bits on
  every main-memory word, generated and checked in the CU memory interface, which also
  generates DRAM timing.
- PSI-II area use under ESP (context only): Nakashima & Takeda, "PSI-IIのメモリ・アーキテクチャ
  評価", TM-859 (Feb 1990) (ICOT-TM/0859), PDF p.3 **[OCR]**: areas 0-3 shared between
  processes, 4-7 per process; area 1 code and heap, area 5 global stack, area 6 local stack,
  area 7 trail stack. The KL1 area assignment on PIM/m: not found (but see `ihp =
  16'E0000000` and "Area 5 allocation" in 1.2).

#### 2.7 Machine instruction format
- PIM/m KL1-B instruction word layout (opcode / operand fields): **not found** in any source
  read. Evidence available:
  - TR-733 図8 **[IMG]** shows the instruction mnemonics and operand shapes as compiled for
    PIM/m: `try_me_else app/s`; `switch_on_non_list R1, app/n`; `read_variable R4`;
    `read_variable R5`; `put_reused_structure R1, R2, 2`; `write_value R4`; `write_variable
    R4`; `get_bound_value R3, R1`; `put_value R1, R5`; `put_value R3, R4`; `execute app/3`;
    `wait_nil R1`; `get_value R2, R3`; `proceed`; `suspend app/3`. Comment on the first line:
    "中断または失敗時の飛先を制御レジスタAPにセット" ("sets the jump target for suspension or
    failure in control register AP").
  - OPT has 512 entries (2.2), so at most 9 bits index the decoder.
  - Predecessor format (PSI-II, KL0), TR-265 Figure 3, printed p.5 / PDF p.6 **[IMG]**:
    bits 39-34 = "001111" (the tag of an instruction word), 33-32 = "class", 31-24 = "inst.
    code", 23-0 = "operand", with operand shapes 8/8/8, 8/16, or 24 bits; text **[OCR]**:
    "The 2-bit classification field divides the instruction set into four classes ... The
    third and fourth are reserved for future extension, such as parallel programming language
    implementation. The 8-bit instruction code field can represent up to 256 instructions for
    each class". **[INFERENCE]** PIM/m keeps this shape (the E-stage byte field extractor,
    the "byte_position_register" in 2.2, and the 512 = 2 x 256 OPT entries all fit a class
    bit plus an 8-bit code), but this is unconfirmed.
- ESP/KL0 vs KL1 mode: TR-564 PDF p.3 **[OCR]**: the FEP CPU is almost exactly the PIM/m
  element processor, so the element processor needs a flexible structure supporting both
  KL1 and KL0. IFS abstract no. 3 **[TEXT]**
  (https://www.airc.aist.go.jp/aitec-icot/ICOT/Museum/IFS/abst/003.html): "Since KL0
  execution and KL1 execution have to coexist on a single CPU, each microprogram for
  executing KL0 and KL1 programs must be dynamically swapped properly. To execute KL1
  programs efficiently, the language processor is implemented entierly by the microprogram
  code of PSI-III." **[ADDS]**: on the workstation the two microprograms do not fit the WCS
  together and are swapped. Whether the RAM decode table is also reloaded on the swap: not
  stated (**[INFERENCE]** it must be, since OPT entries hold microprogram entry addresses).

#### 2.8 Network unit, interrupts, FPP, SCSI bus
- NU blocks, TR-799 printed p.8 / PDF p.9 **[OCR]**: "It consists of a network control unit,
  a trace memory, a system timer, a maintenance control unit, and an external bus control
  unit. ... The external bus control unit has a function which arbitrates among the NU chip,
  FPP, and SCSI." **[ADDS]** trace memory, system timer and maintenance control unit sit in
  the NU chip.
- Path table, same page **[OCR]**: "The index of the PT is the coordinate of the destination
  point which is represented by a 1024 x 2 bit map."
- **[ADDS]** Packet byte format, TR-733 図6 "メッセージパケットのフォーマット", journal
  p.77(685) / PDF p.5 **[IMG]**: 9-bit bytes, bits 8..0. Header byte: bit8 = 1, bit7 = 0,
  bits 6-0 "(制御情報)" (control information). Then bytes with bit8 = 0: "あて先PE番号"
  (destination PE number), "メッセージ種別" (message type), "可変長(メッセージ種別による。)"
  (variable length, by message type), "発信元PE番号" (source PE number). Tail byte: bit8 = 1,
  bit7 = 1, rest "(未使用)" (unused). Note: "□の部分のみがネットワーク制御回路で解釈され,
  他はCPU部のファームウェアで処理される" ("only the boxed parts [header, destination PE
  number, tail] are interpreted by the network control circuit; the rest is processed by
  the CPU firmware"). Text journal p.76(684) **[IMG]**: "データ線の上位の2ビットにより,
  メッセージパケットの先頭バイト(以下'ヘッダ'という。)と最後尾バイト(以下'テール'という。)
  が判別される" ("the top two data bits distinguish the first byte, the header, and the
  last byte, the tail"); channel = "9本のデータ線,1本のbusy線(逆方向)" (9 data lines, 1 busy
  line in the reverse direction), 3.84 Mbyte/s; "wormhole" routing, channel held until the
  tail passes. **[CONTRADICTS, within sources]** TR-799 Table 2 says "10 bits (9 bits; data,
  1 bit; parity)" **[OCR]**, i.e. the tenth line is parity, not busy.
- Message interrupt timing ("slit"): TR-799 printed p.8 **[OCR]**: "The interrupt signal of
  informing a message arrival invokes a micro routine to decode it just before starting the
  next reduction." TR-733 journal p.76(684) **[IMG]**: after the tail is taken into the read
  buffer the NWC "CPUに割込みを上げ,メッセージの解釈を要求する。CPUではKL1プログラムの処理の
  適当な区切りでこの割込みを処理する" ("raises an interrupt to the CPU and requests
  interpretation of the message; the CPU handles it at a suitable break in KL1 processing").
  Sending: "CPUのメッセージ送信はNWCのライトバッファに一つの完全なメッセージを書き込み終わる
  ことにより,自動的に開始される" ("transmission starts automatically once one complete
  message has been written to the NWC write buffer").
- Read Packet Buffer overflow path, TR-799 printed p.9 **[OCR]**: "If it is below the fixed
  value, the micro routine moves the messages, instead of decoding, from the RB to a large
  memory area, called Read Packet Buffer." The pseudo system's parameter file places it at
  area 5, 0x3000-0xAFFF (1.2).
- A slit-check paper exists but is about another machine: Nakagawa et al., "プロセッサ間
  ソフトウェア割り込み処理を高速化するスリットチェック機構", TM-750 (July 1989); the first
  author also wrote the PIM/c reports TR-671/672, so this is PIM/c (Hitachi) **[INFERENCE
  from authorship]**. Downloaded and OCR'd, not read.
- FPP: PSI/UX table, Giho 65(6) 表1 p.82(602) **[journal text layer]**: "浮動小数点プロセッサ
  MC 68882" for the inference unit. Text p.85(605): "(3) FPP (Floating point processor) 単
  精度/倍精度の浮動小数点演算及び関数演算を高速に行うためのもので,浮動小数点演算専用LSI
  を中心に構成されている" ("for fast single/double floating point arithmetic and functions,
  built around a dedicated floating-point LSI") **[journal text layer]**. **[INFERENCE]** the
  PIM/m PE's FPP is the same MC68882 arrangement; no PIM/m source names the part.
- Network registers visible to the console (`pimmcsp.ptf` strings **[TEXT]**):
  `write_buffer_write_address_register`, `write_buffer_read_address_register`,
  `read_buffer_write_address_register`, `read_buffer_read_address_register`,
  `last_send_packet_register`, `last_receive_packet_register`,
  `path_table_address_register`, `network_interrupt_register`,
  `network_interrupt_mask_register`, `network_condition_register`,
  `network_error_channel_register`, `network_io_channel_register`,
  `network_channel_select_register`, `output_buffer_write_address_register`,
  `output_buffer_read_address_register`, `output_register`, `scsi_spc_register`.

#### 2.9 Microprogram structure and size
- No paper gives the size of the KL1 microprogram in words or steps.
- Measured on the distributed images (ICOT Free Software no. 3, `psdpim/PMPSI.DIR/`), all
  **[TEXT]** = my own byte-level inspection; interpretation is **[INFERENCE]**:
  - `syspsi` (262,400 bytes): 256-byte header then exactly 32,768 records of 8 bytes. Header
    32-bit little-endian words 0x0, 0x8000, 0x3; at offset 0x40 the EBCDIC string
    "50.17 11-06'92". 24,414 of the 32,768 records are non-zero (74.5%). This has the shape
    of a full 32K x 64-bit WCS image; by its name and install location
    (`/usr/psi/simpos/csp`) it is the PSI-III system (KL0/SIMPOS) firmware.
  - `sysinit` (66,544 bytes): header words 0x5000, 0x205E, 0x5000; 8,286 records of 8 bytes.
  - `sysidat` (8,576 bytes): header words 0x6800, 0x410, 0x5000; 1,040 records of 8 bytes.
  - `pimm.MEkbn` (506,624 bytes): header words 0x4200, 0x18A00 (= 100,864). The body is 1,978
    blocks of 256 bytes, each 51 five-byte words plus one zero pad byte; exactly 100,864
    words are used and the 14 left over are zero. The fifth byte of each word takes only 40
    distinct values and is zero in 99% of words, i.e. it behaves like a tag byte. So the
    file is an image of 100,864 40-bit words with load address 0x4200. `boot.init` names
    this file in the IMPL step and the README calls the directory "KL0 and KL1 firmware", so
    it should contain the KL1 microprogram (and probably the decode and dispatch tables),
    packed in a form I did not decode. 100,864 x 40 bits = 63,040 64-bit words, close to two
    32K WCS loads; whether that is meaningful is unknown.
  - Console identifiers `load_5byte_wcs`, `load_2byte_wcs`, `load_5byte_mem`, `load_wcs`,
    `save_wcs`, `read_wcs`, `write_wcs`, `cir_to_wcs`, `wcs_reverse_assemble`,
    `pimmutil##csp_micro_reverse_assembler`, and the user command "Micro Field Modifier"
    (`pimmutil##firm_utility`, `mfm`) show that the loader understands a 5-byte WCS file
    form and that a microcode disassembler ships inside `pimmutil.ptf` (477,374 bytes).
    That disassembler is the best available route to mnemonics for the 64-bit fields.
  - WCS addresses are entered as "<WCS Address> ::= <4 digits>" (hex), and a stop code lives
    at "[CIA0 (WCS 3FF8)]".
- Microprogram development: only "RAM decoder makes it easy to develop the microprogram"
  (TM-862 printed p.4 **[OCR]**). Microassembler for PU: not found. (ICOT TR-021, "汎用型
  マイクロプログラム・アセンブラ", Takagi, Aug 1983, is the PSI-I era general microassembler;
  listed in the index, not opened.)

#### 2.10 Gap 8 not found
- KL1-B instruction word layout for PIM/m (bit fields).
- Meaning of the 54 OPT bits (entry address width vs nano-code fields) and of the code values
  in any microinstruction field.
- Size of the KL1 microprogram as a stated number.
- Interrupt priority structure; the papers give only the message-arrival interrupt.

### 3. Boot, IPL, console processor, FEP link, `.kbn`, save/restore

#### 3.1 The boot script (pseudo PIM/m; same console program as Multi-PSI)
`psdpim/SYSTEM.DIR/boot.init`, complete, decoded **[TEXT]**:

```
% me:boot.init, Modified at 17-May-91 16:08:35
[
power_on_boot(on),
auto_power_off(on),
clear(on,"(Don't care on Pseudo)"),
init(on,"(Don't care on Pseudo)","(Don't care on Pseudo)"),
impl(on,"(Don't care on Pseudo)","/usr/psi/pimos/kl1/pimm.MEkbn"),
patch(on,"pmpsi:pimm_patch.com"),
ipl(on,"pimos:pimm_ipl.kbn","pimos:pimm_ipl.sym"),
start(pimos,"20c"),
silent(off)].
```

The console panel strings give the file kind for each step **[TEXT]** (`pimmcsp.ptf`):
"CLEAR FILE (.mbn)", "INIT FILE (.mbn)", "IMPL FILE (.mbn)", "IMPL FILE (.kbn)", "PATCH FILE
(.com)", "IPL FILE (.kbn)", "SYMBOL FILE (.sym)", "START ADDRESS", "Silent Mode"; a default
name "sys:clear.mbn" also appears. So on the real machine: `.mbn` = micro binary (CLEAR, INIT
and IMPL microprograms), `.kbn` = KL1-B binary (the IPL image; the pseudo system's second
IMPL file is also loaded as a 40-bit image), `.com` = micro patch command file, `.sym` =
symbol file for the IPL image. Expansion of the letters "mbn"/"kbn" is **[INFERENCE]**.

Console help text **[TEXT]**, sequence and commands:
- Order listed under the boot help: "$CLear ... (Multi-PSI only) / $INITialize ... (Multi-PSI
  only) / (Setting system parameters) ... (Multi-PSI only) / (Loading Path Table data) ...
  (Multi-PSI only) / $IMPL / ($comm <MicroPatchFile>) / $IPL / $GO/PIMos <Start Address> ...
  <Start Address> = 2000 (Multi-PSI) ... = 200 (Pseudo MPSI)".
- "Usage: $IMPl  loads the micro code on PEs."
- "Usage: $INItialize  initializes the status/environment for cold start ($GO 2000 etc.) on
  PEs."
- "Usage: $IPL  loads a program specifed in "me:boot" or "$PANel" on the boot PE, which is
  determined by the configuration file 'MPSI.CONFIG.'"
- "$[<PE Number>@]LOad <File Name>  loads mocro code from a file on the (currently activated)
  PEs. The file's name should be <File Name> with ".mbn" extension." and "LOad/KL1 ... loads
  KL1 program from a file ... with ".kbn" extension." and "LOad/KL0 loads KL0 program".
- "$[<PE Number>@]GO <Micro Start Address> ... (Multi-PSI) / GO <KL1 Start Address> ...
  (Pseudo MPSI) ... starts the CPU from the current Micro(Multi-PSI) or KL1-B(Pseudo MPSI)
  address"; "GO/PIMos ... starts CPU and throws a boot goal to the boot PE."; "GO/ERfree ...
  starts CPU with Error Free."
- "$NETInitialize ... (Multi-PSI only) initializes the network of the PEs for the Multi-PSI.
  It also reloads the Network Path Talbe Data on both the NWC (Network Controller) and the
  memory calculating from the files named "sys:MPSI.PARAM" and "sys:MPSI.CONFIG"."
- Guard string: "Abnormal start : IPL is not done yet !!! continue (y/n) ?"
- Other IPL names in strings: "kl1:pimos.kbn", "kl1:pimos.sym", "pmpsi:kl1kp.kbn",
  identifiers `ipl_version`, `firm_version`, `ipl_offset`, `check_ipl_offset`,
  `is_ipl_class_object`.
- Parameter file **[TEXT]**: "(bmadr, 16'2E6), % Boot Module Address"; "(stadr, 16'204), %
  Start Address (Firmware debug use only)".
- Configuration file `PIMM.CONFIG` **[TEXT]**: "% Released at 21-Nov-91 by ICOT 1st lab. Firm
  Gr."; `unit([[0]]).` and `pes([[@,@,@,@], ... ])` an 8-row by 4-column map with one `*`
  entry (row 4, column 1); commented alternatives have 2, 4 and 8 `*` entries.
  **[INFERENCE]** 8 x 4 is one 32-PE cabinet; `*` marks PEs present/simulated, `@` absent.

**[INFERENCE]** For the real PIM/m the sequence is therefore: FEP console (CSP program on a
PSI-II or PSI/UX under SIMPOS) clears and initialises each PE, sets parameters from a
`.PARAM` file, loads the path tables, loads the microcode (IMPL) into each PE's WCS, applies
micro patches, loads the `.kbn` IPL image into the boot PE's memory, then starts the PEs
and throws a boot goal to the boot PE. The pseudo system skips CLEAR/INIT and starts at
KL1-B address 0x20C ("20c") rather than micro address 0x2000.

#### 3.2 Console processor (CSP) and maintenance path
- CSP for Multi-PSI: Fujise et al., "並列論理型言語KL1によるオペレーティングシステムPIMOSの
  実現について", TM-1203 (Aug 1992), PDF p.7 **[OCR]**: "動作確認のためのツール
  は,Multi-PSIのハード的サポートを行なうCSP(コンソール・プロセッサ)のもつ機能である"
  ("the tool for checking operation was a function of the CSP (console processor), which
  provides hardware-level support for the Multi-PSI"). 
- Multi-PSI maintenance bus (predecessor; NOT PIM/m): Masuda, Nakagawa, Iwayama, Takeda,
  Nakashima, Taki, "(財)新世代コンピュータ技術開発機構向けマルチPSIシステム", 三菱電機技報
  Vol.62 No.12 (1988) pp.1100-1105 (issue-internal pp.90-95)
  (https://www.giho.mitsubishielectric.co.jp/giho/pdf/1988/8812.pdf), p.91(1101) / issue
  PDF p.97 **[journal text layer]**: "フロントエンドプロセッサは,一つのシステムに最大4台まで
  接続することができ,その内の一つはシステムの立上げ,保守,マイクロプログラムのデバッグなどの
  メンテナンス機能を持っている。... フロントエンドプロセッサの一つ(マスタ)とすべての要素
  プロセッサ ... はメンテナンスパスというバスにより接続されている。... フロントエンドプロセッサ
  はメンテナンスパスを介して要素プロセッサの起動/停止,内部資源の読出し/書込みを行うことが
  できる。" ("Up to four front-end processors can be connected; one of them has the
  maintenance functions: system start-up, maintenance, microprogram debugging. ... One FEP,
  the master, and all element processors are connected by a bus called the maintenance
  path. ... Through it the FEP can start/stop the element processors and read/write their
  internal resources.") And p.94(1104) / PDF p.100: "フロントエンドプロセッサから各PEの内部
  資源(レジスタ,バッファなど)の読出し/書込み,各PEへのブートストラップ,イニシャライズ,
  異常検出などが行える" ("from the FEP: read/write of each PE's internal resources
  (registers, buffers), bootstrap of each PE, initialisation, fault detection").
- **[INFERENCE]** PIM/m keeps a maintenance path: the NU chip has a "maintenance control
  unit" (TR-799), and the console register list includes `maintenunce_path_power_register`,
  `console_interface_register`, `debug_command_register`, `command_base_register`,
  `data_buffer_base_address_register`, `bloadcast_mode_flag`, `power_fail_flag_clear`
  **[TEXT]**. How the maintenance path is carried physically on PIM/m (separate bus vs
  SCSI): not found.
- Console abilities seen in strings **[TEXT]**: micro address break ("CSP Micro Program
  Break", "Breaked WCS Address"), micro step, micro trace memory display and log save
  ("dumps the executed micro code log"), register compare breaks, KL1 instruction step,
  heap meter, goal record inspector, limited trace, FEP network monitor. Hardware error
  messages name parity-checked items: "IR (Instruction Register) Parity Error", "Tag-1 Bus
  Parity Error", "Tag-2 Bus Parity Error", "Micro-Instruction Register Parity Error", "Tag
  Bus Parity Error", "Memory 1 bit Error".

#### 3.3 FEP and SCSI
- TM-862 printed p.1 / PDF p.3 **[OCR]**: "Up to 32 SCSI ports are available to connect disks
  and front end processors (FEP)." TR-564 PDF p.3 **[OCR]**: four SCSI ports per cabinet.
- TR-733 journal p.75(683) **[IMG]**: "8PEごとに一つのPEには入出力用SCSIバスの制御ボードを
  通して670Mバイトの内蔵磁気ディスクやフロントエンドプロセッサ(FEP)などが接続される。FEP
  には"MELCOM PSI-II"若しくは"MELCOM PSI/UX"が用いられる。" ("One PE in every eight has, via
  an I/O SCSI bus control board, a 670 MB internal disk and the front-end processor(s). The
  FEP is a MELCOM PSI-II or MELCOM PSI/UX.") 図2 **[IMG]** labels "SCSIバス制御ボード",
  "DISK (670Mバイト)", "Front-end Processor (PSI-II, PSI/UX)", "8PEごとに一つ". **[ADDS]**
  the SCSI controller is a separate board on 1 PE in 8, and PSI-II can also be the FEP.
- SCSI as seen by KL1/PIMOS: Yashiro et al., "Resource Management Mechanism of PIMOS",
  TR-764 (April 1992), PDF p.14 **[OCR]**: "Each operation to the SCSI bus is
  provided as a built-in predicate by the KL1 ... scsi_command(SCSI, Unit, LUN, Command,
  Length, Direction, Data, DataP, ^NewData, ^TransferredLength, ^ID, ^Result, ^NewSCSI)".
  (Another agent's area; cited only to show where the FEP protocol sits.)
- FEP-side software names in `pimfep.ptf` / `pimscsi.ptf` strings **[TEXT]**:
  `pimos_scsi_front_end`, `pimos_scsi_fep_control`, `scsi_stream`, `pseudo_scsi_fep`,
  `scsi_port_0` .. `scsi_port_3`, `set_scsi_id`, `scsi_init_list`, `pimos_login_requester`,
  `packet32`, `scsi_device_bus_management`, `scsi_device_interrupt_management`,
  "*** SCSI HMCB log ***", error strings "SCSI error (receive command)", "SCSI error (send
  data)", "BootError(\d)!". These packages are the FEP end of the PIM/m-to-FEP SCSI
  protocol (and its pseudo version); the code is in SIMPOS package-template form and was
  not decompiled.
- PSI/UX internal link (not the PIM/m link): Giho 65(6) pp.83-84 (603-604) **[journal text
  layer]**: the inference unit and the MC68030 UNIX unit talk through a 128 KB interface
  memory on a VME interface board: write control information and data to a fixed region,
  interrupt the other side, the other side reads it; a software "交信用論理チャネル" (logical
  communication channel) protocol runs on top. "推論部からみれば,汎用部は入出力制御装置として
  機能する" ("seen from the inference unit, the general-purpose unit acts as its I/O
  controller").

#### 3.4 Save / restore of the heap
- Not found in any paper. Only identifiers in console strings: `remote_node_save_file`,
  `save_wcs`, `save_micro_log`, `tag_save` (a KL0 tag mnemonic), "save data pointer" (a SCSI
  message name) **[TEXT]**. None of these is evidence of a heap save/restore facility.

### 4. Gap 3 note: MRB position and polarity

- Papers: MRB is "a part of the tag" (TM-862 printed p.8 **[OCR]**); figure legend "○:
  MRB=off  ●: MRB=on" (TM-862 Figure 4 PDF p.11 **[OCR]**; TR-564 図3 **[OCR]**); TR-564 PDF
  p.4 **[OCR]**: "タグの比較やMRBのオン/オフなど,タグ操作のための機能がどちらのフェーズにも
  用意されている" ("functions for tag manipulation, such as tag comparison and turning MRB
  on/off, are provided in both phases"). No paper gives a bit position.
- Console help text in `pimmcsp.ptf` **[TEXT]**: "'++' specifies the dereference. That is,
  you can see the dereference result trainling from the specifed <Register> through
  REFo(06) or REFx(07) tag." Tag mnemonic grammar, in this order: "INTo | INTx | ATOMo |
  ATOMx | LISTo | LISTx | REFo | REFx | UNDF | HOKo | HOOKx | MHOOK | VDESC | STRGo | STRGx |
  VECT0o | VECT0x | ... | VECT6o | VECT6x | VECTo | VECTx | PMI | BLT | GMI | KLB | PREDH |
  CDESC | COD | MOD | MGHOK | EXMRF | EUNDFo | EUNDFx | EHOOKo | EHOOKx | EMHOKo | EMHOKx |
  FLTo | FLTx | EXREFo | EXREFx | EXVALo | EXVALx | RHOOKo | RHOOKx | SHREC | FPREC |
  FPRECt | DREF | GOAL". Values are entered as "<tag> ::= <tag_mnemonic> | <digit> |
  <digit><digit>" (hex).
- Stated fact: REFo = 0x06, REFx = 0x07. **[INFERENCE]** (a) the o/x pair differs only in
  the least significant bit, so MRB is tag bit 0 (word bit 32); (b) "o" = MRB off = 0 and
  "x" = MRB on = 1, matching the ○/● legend; (c) if the list is in numeric order from zero
  then INTo=00, INTx=01, ATOMo=02, ATOMx=03, LISTo=04, LISTx=05, REFo=06, REFx=07, which is
  consistent with the one documented pair but otherwise unverified. This encoding is for the
  Multi-PSI / pseudo-PIM/m KL1 firmware of 1989-91; that the real PIM/m firmware uses the
  same values is **[INFERENCE]** (same console program, same firmware group).
- Related identifiers: `exref_mrb`, `exval_mrb`, `integer_mrb`, `atom_mrb`, `vector0_mrb` ..
  `vector6_mrb`, `vector_mrb`, `string_mrb` **[TEXT]**. The KL0 tag set is listed separately
  (`tag_int`, `tag_atom`, `tag_list`, `tag_strg`, `tag_gundf`, `tag_lundf`, `tag_ref`,
  `tag_hook`, ... `tag_cadr`, `tag_frzn`, `tag_save`, ...), confirming two tag encodings on
  one CPU.

### 5. Web search: found and not found

Found (beyond the ICOT report archive)
- Mitsubishi Denki Giho back issues are online as whole-issue PDFs with a (poor) text layer:
  1988 Vol.62 No.12, 1991 Vol.65 No.6, 1992 Vol.66 No.6 (URLs in the table). Opened and read.
- ICOT Free Software abstract no. 3 and archive `psdpim.tar.Z` (opened, downloaded,
  inspected); abstract no. 4 (PIMOS) opened.
- DBLP record confirming the ICCD'90 citation (Nakashima, Takeda, Nakajima, Andou, Furutani,
  ICCD 1990: 355-359), https://dblp1.uni-trier.de/rec/conf/iccd/NakashimaTNAF90.html: search
  result only, not opened.
- IEICE author-page snippet for the cache chip paper ("610 k transistors including 80 kbits
  memory cells ... 1.0 um CMOS ... Trail Buffer"): search snippet only, not opened; adds
  nothing to TR-799.

Not found (exact queries tried)
- Full text of the ICCD'90 paper: `"A Pipelined Microprocessor for Logic Programming
  Languages" Nakashima ICCD 1990` (only the DBLP record; TM-862 is the summary in hand).
- CICC'91 paper: `"1.5 MLIPS 40-bit AI processor" Machida CICC 1991` (no relevant hit;
  the Japanese version TM-1109 was downloaded and its first four pages read via OCR; it
  repeats TM-1074).
- PSI/UX microprogram details: `"PSI/UX" OR "PSI-UX" MELCOM AIワークステーション マイクロ
  プログラム 推論部 三菱電機技報` (led to the Giho PDFs; no microprogram size or format
  beyond what is reported above).
- PIM/m GC and free lists: `"PIM/m" KL1 microprogram "garbage collection" free list goal
  record "Mitsubishi" inference machine firmware`; `PIM/m 並列推論マシン KL1 処理系 マイクロ
  プログラム ごみ集め 情報処理学会 中島 浩 近藤 誠一` (no relevant paper).
- `.kbn` format: `ICOT PIMOS ".kbn" KL1-B binary file IPL PIM/m boot front-end processor`
  (nothing; the format evidence is from the archive, 2.9 and 3.1).
- Pseudo PIM/m: `"PSI-III" OR "PSI/UX" inference machine microprogram "KL1" "pseudo" "PIM/m"
  emulator workstation ICOT` (found the IFS abstract).
- `"An Intelligent Cache Memory Chip Suitable for Logical Inference" IEICE Transactions
  Electronics 1991 Yasuda` (snippets only).
- A background web-search agent could not be started (agent limit), so the web pass is these
  eight queries only. Not searched: IPSJ digital library, CiNii, J-STAGE, IEEE Xplore
  abstract pages, IPSJ computer museum pages, bitsavers.

### 6. Source table

| Citation | URL | Status |
|---|---|---|
| Machida et al., A VLSI Chip Set for a Large Scale Parallel Inference Machine: PIM/m, ICOT TR-799, Aug 1992 | ICOT-TR/0799 (local PDF) | opened and read (OCR, all 24 pp; figures/tables not re-read on image) |
| Machida et al., same title, ICOT TM-1159, Feb 1992 (CICC'92 30.1) | ICOT-TM/1159 (local PDF) | opened and read (OCR) |
| Nakashima et al., A Pipelined Microprocessor for Logic Programming Languages, ICOT TM-862, Feb 1990 | ICOT-TM/0862 | opened and read (OCR; PDF pp.13-14 on image) |
| Ando et al., A 40-bit Microprocessor for Logic Programming Language, ICOT TM-858 (cover TM-0857.0858), Feb 1990 | ICOT-TM/0858 | opened and read (image: Table 1, Figure 2, intro) |
| Ando et al., 論理型言語処理マイクロプロセッサ, ICOT TM-857 | ICOT-TM/0857 | OCR skimmed; same content as TM-858 |
| Nakashima, Takeda, Nakajima, PIM/m 要素プロセッサのアーキテクチャ, ICOT TR-564, May 1990 | ICOT-TR/0564 (local PDF) | opened and read (OCR; 図2, 図4, 図5 on image) |
| Furutani et al., 並列推論マシン(PIM/m)用VLSI, ICOT TM-1074, July 1991 | ICOT-TM/1074 (local PDF) | opened; read on image printed pp.2, 4-6, 8-9, 15, 24; rest not read (OCR unusable) |
| Machida et al., 1.5MLIPS AIプロセッサの開発, ICOT TM-1109, Sept 1991 | ICOT-TM/1109 | downloaded; pp.2-4 read (OCR) |
| K. Nakajima et al., 並列推論マシンPIMのアーキテクチャ, ICOT TR-733, Jan 1992 = 三菱電機技報 66(6) 1992 pp.74-78 | ICOT-TR/0733; https://www.giho.mitsubishielectric.co.jp/giho/pdf/1992/9206.pdf | opened and read on image (TR PDF pp.3-6); journal PDF downloaded only |
| Masuda et al., 《MELCOM PSI/UXシリーズ》のハードウェアシステム, 三菱電機技報 65(6) 1991 pp.602-607 | https://www.giho.mitsubishielectric.co.jp/giho/pdf/1991/9106.pdf | opened and read (text layer pp.82-85; image p.84 図3, p.86) |
| Yuasa, Ueda, Matsumoto, 《MELCOM PSI/UXシリーズ》の概要と特長, 三菱電機技報 65(6) 1991 pp.594-601 | same PDF | resolved, not read |
| Masuda et al., ICOT向けマルチPSIシステム, 三菱電機技報 62(12) 1988 pp.1100-1105 | https://www.giho.mitsubishielectric.co.jp/giho/pdf/1988/8812.pdf | opened and read (text layer, pp.91, 92, 94, 95) |
| Nakashima & Nakajima, Hardware Architecture of the Sequential Inference Machine: PSI-II, ICOT TR-265, June 1987 (SLP'87 pp.104-113) | ICOT-TR/0265 | downloaded; read OCR PDF pp.5-6, 8-10; Figures 1-3 on image |
| Nakashima & Takeda, PSI-IIのメモリ・アーキテクチャ評価, ICOT TM-859, Feb 1990 | ICOT-TM/0859 | downloaded; abstract and pp.3-4 skimmed (OCR) |
| Miyauchi et al., Tracing Garbage Collection for KL1 on the Multi-PSI/V2 System, ICOT TR-469, June 1989 | ICOT-TR/0469 | skimmed (OCR, keyword passages) |
| K. Nakajima, Piling GC, ICOT TR-354, March 1988 | ICOT-TR/0354 | skimmed (OCR: abstract, sections 2-3 lines, conclusion) |
| Nakashima & Chikayama, スタック領域が不要な深さ優先順コピー型ゴミ集め方式 (served as tr0870.pdf), April 1994 | ICOT-TR/0870 | cover, p.2, p.11 on image; rest skimmed |
| Nakashima (& Chikayama on cover), データ構造の一部を指すポインタを許容するコピー型ゴミ集め方式 (served as tm1295.pdf), April 1994 | ICOT-TM/1295 | cover, p.2 on image; OCR grep |
| Nakashima & Chikayama, Depth-First Copying GC without Extra Stack Space, ICOT TR-907, Feb 1995 | ICOT-TR/0907 | abstract read (OCR); body not read |
| Fujise et al., PIMOSの実現について, ICOT TM-1203, Aug 1992 | ICOT-TM/1203 | one passage (OCR) |
| Yashiro et al., Resource Management Mechanism of PIMOS, ICOT TR-764, April 1992 | ICOT-TR/0764 | one passage (OCR) |
| ICOT Free Software no. 3, KL1 Pseudo Parallel System for PSI-III (abstract) | https://www.airc.aist.go.jp/aitec-icot/ICOT/Museum/IFS/abst/003.html | opened and read |
| `psdpim.tar.Z` (Pseudo PIM/m), sha256 f9e2f0874ce2b2856f94618c08574b6d06123ebd0378b757cf750df417c99c81 | https://www.airc.aist.go.jp/aitec-icot/ICOT/ifs/symbolic-proc/pim-psi/psdpim.tar.Z | downloaded; README, INSTALL, 5 text files decoded and read; binaries measured; `.ptf` strings extracted |
| ICOT Free Software no. 4, PIMOS (abstract) | https://www.airc.aist.go.jp/aitec-icot/ICOT/Museum/IFS/abst/004.html | opened and read |
| FGCS'92 demo documents pp.11-12 | https://www.airc.aist.go.jp/aitec-icot/ICOT/Museum/FGCS92Demo/E/doc011.html, doc012.html | opened and read (nothing hardware-specific) |
| Nakagawa et al., スリットチェック機構, ICOT TM-750, July 1989 | ICOT-TM/0750 | downloaded and OCR'd, not read |
| Masuda et al., マルチPSIの基本構成と今後の展開, ICOT TM-696, June 1989 | ICOT-TM/0696 | downloaded and OCR'd, not read |
| K. Nakajima, 小型化PSIにおける論理型言語KL0の処理系実装方式, ICOT TM-444, Jan 1988 (36 pp) | ICOT-TM/0444 | downloaded and OCR'd, not read |
| Nakashima et al., Architecture and Implementation of PIM/m, ICOT TR-742, March 1992 | ICOT-TR/0742 | downloaded, not read (baseline already known) |
| Nakashima et al., ICCD 1990 pp.355-359 | DBLP record above | cited only |
| Machida et al., A 1.5 MLIPS 40-bit AI Processor, CICC 1991 pp.15.3.1-15.3.4 | none found | cited only |
| Yasuda et al., An Intelligent Cache Memory Chip Suitable for Logical Inference, IEICE Trans. Electron. E74(11) 1991 pp.3796-3802 | global.ieice.org author pages (snippet) | cited only |

Working files of this pass (scratchpad, disposable):
`(scratch)/hw_work/`
with `dl/` (ICOT PDFs), `giho/` (journal issues), `psdpim/` (archive and extraction), `dec/`
(decoded text files and `.ptf` string lists), `ocr/`, `img/` (page renders), `bin/` (the
three small analysis scripts).

### 7. Documents worth obtaining or reading next

1. **`psdpim.tar.Z` contents, properly decoded** (highest value): unpack `pimm.MEkbn` into
   40-bit words and find the microcode, OPT and TGT images; decompile or at least dump
   `pimmutil.ptf` (micro reverse assembler, Micro Field Modifier) and `pimmcsp.ptf`
   (`csp_micro_loader`, `csp_ipl`, tag macro tables `kl1_tag_macro` / `kl0_tag_macro` with
   numeric values, register address tables). The licence file `COPYRIGHT` is in the archive
   and was not reviewed.
2. The rest of the ICOT Free Software tree under `.../ICOT/ifs/symbolic-proc/pim-psi/`
   (`pimos.tar.Z`, `pimosobj.tar.Z`, manuals): the object archive may hold `pimm_ipl.kbn`
   and `.sym` files named by `boot.init`.
3. ICOT TM-444 (KL0 implementation on the small PSI = PSI-II firmware design, 36 pp),
   TM-696, TM-750: downloaded and OCR'd here but unread.
4. 三菱電機技報 65(6) 1991 pp.594-601 (PSI/UX overview; has a firmware section according to
   its introduction: "ハードウェア,ファームウェアの面から紹介する") and 62(12) 1988 pp.61-66
   "LSI化高性能AIワークステーション MELCOM PSI II" (in the already downloaded 8812.pdf,
   unread).
5. ICCD'90 full paper (5 pp) and CICC'91 paper (4 pp): IEEE Xplore; not openly available.
6. Yasuda et al., IEICE Trans. E74-C(11) 1991: CU chip details (trail buffer size would be
   settled here).
7. Nakashima & Takeda, IPSJ SIG ARC 90-ARC-80-8 pp.57-64 (1990) = TM-859 (in hand).
8. ICOT TR-021 (general microprogram assembler, 1983) and TR-079 (PSI micro interpreter,
   1984) for the PSI-family microassembler notation.
9. Any PIM/m firmware manual or CSP manual (the console help text implies a "$HElp" corpus
   and a "sys:MPSI.PARAM" maker tool); none located.

### 8. Corrections and additions from a final checking pass (these override the text above)

- **WCS size contradiction settled (2.1).** The Japanese twin of TM-858, Ando, Machida,
  Nakashima, Nakaya, "論理型言語処理マイクロプロセッサ", TM-857 (Feb 1990), PDF p.2 (printed
  p.1, the page after the cover): "PUは,32KwのWCSに格納されたマイクロプログラムの制御により
  動作するマイクロプロセッサである" ("the PU is a microprocessor operating under the control
  of a microprogram stored in a 32 Kw WCS") **[IMG]**. So "64-Kword" in the English TM-858 is
  the outlier, most likely an error; the 16-bit MSTK width remains the only hint of a larger
  address space. Page numbers quoted for TM-858 as "PDF p.1 / p.2" in 2.1-2.2 are the text
  pages after the cover, i.e. PDF pp.2-3 of the served file **[not rechecked]**.
- **"Area 5" versus `10 :` (1.2).** The parameter file comments say "Area 5 allocation" while
  the values are written `(10 : 16'...)`. The meaning of "10" is unexplained; I did not
  resolve it (it is not 5 in hex, octal or decimal).
- **`pimm.MEkbn` discriminator (2.9, headline 1)**, one further script run, **[TEXT]**
  measurement: the image is 100,864 five-byte words. Byte 0 of each word takes all 256
  values; byte 4 is zero in 99,930 words. Of the 934 words with non-zero byte 4, 932 lie in
  the first 2,285 words and 2 near word 47,528. The first words alternate
  `80 12 01 4a 00` / `25 04 12 78 08`. Compare PSI-II, where every instruction word carries
  the fixed tag 001111 in its top six bits (TR-265 Figure 3): no such constant tag appears.
  **[INFERENCE]** The bulk of the file is therefore not tagged 40-bit KL1-B code in the
  PSI-II sense; it is compatible with 32-bit halves of 64-bit microinstructions (console
  loader name `load_5byte_wcs`) preceded by a ~2.3 Kword tagged table. This supports, but
  does not prove, that the file holds the KL1 microprogram. Not disassembled.
- **Bridge from Multi-PSI firmware to PIM/m (1.3).** "Document for FGCS'92 Demonstrations
  Documents P.14", https://www.airc.aist.go.jp/aitec-icot/ICOT/Museum/FGCS92Demo/E/doc014.html:
  under "PIM/m": "Inherits Multi-PSI's architecture and firmware" **[TEXT; page fetched
  through a text-extraction tool, wording not seen by me in raw HTML]**. This one bullet is
  the whole basis for carrying TR-469's free-list and copying-GC description over to PIM/m.
- **Slit-check (2.8).** Nakagawa et al., TM-750 (July 1989), PDF p.2-3 **[OCR, poor]**: the
  target machine is named in the text as "PIM-FIRM" (OCR also "PIM-PIRM"), a shared-memory
  machine whose slit-check is treated "as a extension of a coherent cache scheme" (English
  abstract). PIM/m has no shared memory or coherent cache, so this paper does not describe
  PIM/m. Slit-check on PIM/m: not found; the nearest statements are the "just before
  starting the next reduction" interrupt handling in 2.8.
- **PSI-II firmware scope (2.9).** K. Nakajima, "小型化PSIにおける論理型言語KL0の処理系実装
  方式", TM-444 (Jan 1988), conclusion (OCR line 1362; PDF page not noted) **[OCR]**:
  "PSI-IIのファームウェアは16KwのWCS容量を利用し,ESP/SIMPOSマシンとしての非常に多くの機能を
  サポートしている ... マークコンパクション方式のGC ..." ("the PSI-II firmware uses the 16 Kw
  WCS capacity and supports a great many functions as an ESP/SIMPOS machine ... a
  mark-compaction GC ..."). So the KL0 system's GC is mark-compact (hence two GC mark bits
  in the PSI-II tag), in firmware. Only this passage was read; the body (KL0 instruction
  implementation on PSI-II) remains unread.
- **Multi-PSI boot and maintenance path (3.2).** Masuda et al., "マルチPSIの基本構成と今後の
  展開", TM-696 (June 1989), PDF pp.4-6 **[OCR]**: "CSPはPIMOSの立上げ時点に,イニシャル
  プログラムのローディングや,接続ネットワークのルーティングのためのパステーブルの設定の
  ほか,要素プロセッサの診断や監視を行う。FEPはPIMOSの立上げが終わると,本体上のPIMOSと一本
  のストリームによる通信路により結合され" ("at PIMOS start-up the CSP loads the initial
  program and sets the path tables for network routing, and also diagnoses and monitors the
  element processors. When start-up is finished the FEP is joined to PIMOS on the main
  machine by a single stream"); the maintenance path interface sits on the network
  controller board, and the bus is "1本の非同期バスでいもづる式に接続 ... フロントエンド・
  プロセッサがマスタでPEがスレーブ" ("one asynchronous bus, daisy-chained; FEP master, PEs
  slaves"). Multi-PSI, not PIM/m.
- **PSI/UX overview article (section 7 item 4).** Grep of the journal text layer for
  ファームウェア / マイクロプログラム in pp.594-601 found only the one introductory sentence;
  the microprogram statements are all in the hardware article already cited ("実行制御用の
  メモリ(WCS)に専用マイクロ命令でプログラム(マイクロプログラム)しており"). Status: grepped,
  nothing further.
- Source-table status changes: TM-857 page image read; TM-750, TM-444, TM-696 passages
  above read (OCR), remainder unread; FGCS'92 demo doc014 opened.
- Length: this draft exceeds the requested 300-600 lines because of hard wrapping.

## Appendix D. Archives, mirrors and holdings

Draft, researched 2026-11-20. Status vocabulary used in every table:

- **opened-and-read** -- the bytes were fetched and the content was read (how is stated).
- **resolved-not-read** -- HTTP 200/206 with the stated size/type; content not read.
- **cited-only** -- named by another document; no copy located.
- **dead** -- HTTP error (code given).

Hosts: `UEDA` = `https://www.uedalab.jp/AITEC_ICOT_ARCHIVES/ICOT/`,
`AIST` = `https://www.airc.aist.go.jp/aitec-icot/ICOT/`. Both carry the same tree (the
2005 AITEC/ICOT archive DVD). Every path given below as "both mirrors" was checked with a
ranged GET on both hosts (HTTP 206 on each). UEDA serves Apache directory listings; AIST
does not (directory URLs return 404/500 there, files return 200).

Headline findings (details in the sections):

1. **384 Technical Memoranda exist as PDFs but are not in `TMlist.html`.** `TMpdf/` holds
   1,305 PDFs; `TMlist.html` lists 935 numbers. The unlisted ones are mostly ICOT's
   collected IPSJ national-convention papers in Japanese, including PSI-II firmware,
   Multi-PSI/V2 code format, the KL1-B revision, PIM/m PE architecture, the PIM/m
   front-end processor, and "PIM/m maintenance architecture and CSP". Titles come from
   the per-report `TMidx/tmNNNN.idx` records. See 1.5.
2. **`ifs/manuals/` is a directory the IFS index pages do not link to**: PIMOS manual
   v1.5 (English, 177 pp PostScript), PIMOS manual v3.0 (Japanese PostScript), PIMOS
   primers 1.5 (J) and 3.0 (E, LaTeX source), the KL1 tutorial and KL1 textbook, and the
   ESP manuals. The English PIMOS 3.0 primer documents the CSP auto-boot panel, the
   `.kbn` / `.mbn` / `.sym` / `.com` boot files and names five manuals that were not
   located anywhere. See 1.2 and item 8.
3. **No PSI firmware, SIMPOS, ESP system, KL0, CSP, FEP or microprogram-assembler
   software is in the archive.** The only firmware is the already-held `psdpim.tar.Z`.
   The `simpos/` directories hold ESP *applications* only. CESP was never part of IFS.
4. **FGCS'84, '88, '92 and '94 proceedings are on the mirrors as per-paper PDFs**, plus
   Japanese-language conference records, demonstration descriptions and symposium slides.
5. **A second, independent mirror of the IFS FTP tree** (June 1995 snapshot, re-packed
   `.tgz`) is at the CMU AI Repository, including `manuals/` and the PIMOS packages. See item 3.
6. **The Japanese PIMOS 3.0 manual has an IPL chapter (6.1)** describing the `.kbn` ->
   `pimos.ipl` -> `*.sav` boot chain, the CAL cross system used up to 2.5, and the IPL
   error messages. Operational prose, not a byte-level format. See item 8, supplement A.
7. **Five printed 1985 ICOT PSI manuals** (CSP operating manual, KL0 built-in predicates,
   three SIMPOS manuals) are catalogued in exactly one library, at JAIST -- the same
   institution whose collection page says a PSI and "related manuals" are preserved. The
   IPSJ museum page says PIM/p and PIM/m are preserved at the National Science Museum.
   See items 4 and 8 (supplement B).
8. **Mitsubishi Denki Giho is fully online**: nine articles on MELCOM PSI, PSI II, the
   Multi-PSI system, PSI/UX, the PIM/m VLSI and PIM architecture, 1986-1992. See item 5.
9. **130 on-topic Japanese papers are open in the IPSJ repository** (1984-1996), with the
   PIM/m element-processor and PIM/m CSP papers read in full; convention volumes 34-36
   and 43 are missing there but partly present as unlisted ICOT TMs. See item 6.
10. **KLIC continued to 3.014**; no PSI/PIM emulator, ROM or microcode dump, SIMPOS
   image, CSP/FEP manual or `.kbn` format specification was found anywhere. See items 7, 8.

---

### Item 1 -- Directory structure of the ICOT archive mirrors

Method: recursive crawl of the UEDA autoindex (listings only, no binaries), 23,910 files
recorded with size and date over 1,224 directories (the eight directories whose names contain `&` (three under `Museum/FGCS/`, five under `Museum/SYMPO/`) were not walked by the crawler; their index pages were fetched by hand); index pages fetched with curl and decoded per page
(iso-2022-jp / EUC-JP / Shift_JIS). Five `R&D...` directories contain `&` in the name and
must be requested with `%26`.

#### 1.1 Top level (UEDA listing, opened-and-read)

| Path | What it is |
|---|---|
| `HomePage.html`, `HomePage-J.html` | archive top pages |
| `changelog-E.html`, `changelog-J.html` | maintenance log of the UEDA copy (see 1.8) |
| `Free-Software/` | "IFS still under development" link page (external links, c. 2004) |
| `ifs/` | the ICOT Free Software FTP tree (`ftp.icot.or.jp:/ifs`) |
| `pub/` | other FTP material: `klic/v3.0/`, `contest/` (KLIC programming contests 1996-98), `cuprolog/`, `m-qxt/`, `ftp/` (empty) |
| `Museum/` | the "FGCS Museum" / "FGCS Digital Archive" |
| `GENE/`, `IMAGES/`, `PICS/` | genome-application pages, images, OHP pictures |

`Museum/` subdirectories: `CONTEST FGCS-OHP FGCS FGCS92Demo FGCS94 FGCS94W FUNDING
FinalEval FinalReport HISTORY ICOT ICRA IExchange IFS IFSN InvitedResearcher JOURNAL
LECTURE MACHINE MITIrr Minutes NEWS PERSONS SOFTWARE SYMPO TODAY TRTM VIDEO`.

File counts by area: `Museum/Minutes` 7,764; `Museum/TRTM` 6,649; `Museum/FUNDING` 2,268;
`Museum/FGCS92Demo` 1,148; `Museum/FGCS` 970; `ifs/exper-apps` 869; `Museum/SOFTWARE` 866;
`Museum/FinalEval` 420; `ifs/contract-research` 347; `ifs/symbolic-proc` 69;
`ifs/manuals` 12.

#### 1.2 `ifs/` -- everything related to PSI, SIMPOS, ESP, KL0, PIMOS, KL1 tools

`ifs/README` (17 KB, opened-and-read, plain text) is the authoritative list of the 100
IFS items and their directories. The complete set of relevant files:

| Item | Path under `ifs/` (both mirrors) | Size, date | Status | What it contains | Why it matters |
|---|---|---|---|---|---|
| PIMOS manual v1.5, English | `manuals/pimos/man15.ps.Z` | 322K, 1992-09-16 | opened-and-read (uncompressed, PostScript "PIMOS Manual", 177 pages; text extracted with Ghostscript) | Full PIMOS 1.5 reference: KL1 language, builtins, shoen, devices; section 7.4 "Unloader", appendix "Howto create a string I/O device on FEP" | An English PIMOS reference manual older than the held `pimosman` |
| PIMOS manual v3.0, Japanese | `manuals/pimos/man30.j.ps.Z` | 1.6M, 1992-09-16 | resolved-not-read (uncompresses to valid PostScript, `%%Title: top.dvi`, contains an embedded `rmon.ps` picture) | PIMOS 3.0 manual in Japanese | Intermediate edition between 1.5 and the 1994 `pimosman` |
| PIMOS primer 1.5, Japanese | `manuals/pimos/primer15.j.tex.Z` | 42K | resolved-not-read (LaTeX source, JIS) | "PIMOS速修マニュアル" source (= TM-883) | Boot procedure on Multi-PSI |
| PIMOS 3.0 Introductory Manual, English | `manuals/pimos/primer25.tex.Z` | 36K | **opened-and-read** (LaTeX, 2,480 lines; title `PIMOS 3.0 Introductory Manual`, author "PIMOS Development Group") | Chapters: setting up PIMOS on PSI-II, boot-strap/login/shutdown, CSP, running KL1 | Documents the CSP boot panel and the boot file types -- see item 8 |
| KL1 tutorial | `manuals/kl1/kl1-tut.ps.Z` (120K, 42 pp), `kl1-tut.j.ps.Z` (263K), `kl1-tut.dvi.Z` (58K) | 1992-09-16 | resolved-not-read (valid PostScript, 42 pages) | KL1 tutorial, English and Japanese | Language reference |
| KL1 textbook | `manuals/kl1/kl1-text.tar.Z` | 197K | opened-and-read (tar listing: `kl1-text/introductory/*.tex` ...) | "KL1 Programming: Introduction / Beginning / Intermediate" LaTeX source (Japanese file names `hajimeni`, `kiso`) | The KL1 course cited by the PIMOS primer |
| ESP manuals | `manuals/esp/ESPps.tar.Z` (362K), `ESPps-j.tar.Z` (585K), `ESPtex.tar.Z` (167K), `ESPtex-j.tar.Z` (179K) | 1992-08-04 | opened-and-read for `ESPtex.tar.Z` (tar listing: `overview-e.tex`, `program-e.tex`, ...); others resolved-not-read | ESP language guide, English and Japanese, PostScript and TeX | ESP is the language of SIMPOS, of the CSP and of `psdpim`'s ESP half |
| PIMOS manual, PostScript | `symbolic-proc/pim-psi/pimosman.ps.Z` | 846K, 1994-03-29 | opened-and-read (valid PostScript, `%%Title: e-top.dvi`, 504 pages) | Typeset form of the held `pimosman.tar.Z` | Same content as held item, ready to print; note it for page citations |
| PIMOS, PIMOS object, PIMOS manual, Pseudo-PIM | `symbolic-proc/pim-psi/{pimos,pimosobj,pimosman,psdpim}.tar.Z` | 1994 | already held | -- | -- |
| PDSS, VPIM, pkl1, A'UM | `symbolic-proc/unix/{pdss,vpim,pkl1}.tar.Z`, `aum-1.2c.tar.Z`, `aum-pat-1.2b.Z` | 1992-93 | held except A'UM (resolved-not-read) | -- | -- |
| KLIC 1.500, 2.000, 2.001, 2.002 | `symbolic-proc/klic-system/klic-old/klic-{1.500,2.000,2.001}.tgz`, `klic-system/klic-2.002.tgz`; same again under `symbolic-proc/unix/klic/` | 741K-929K, 1995 | resolved-not-read | Older KLIC releases | 2.002 is held; 1.500 is the last "version 1" |
| KLIC 3.001 | `symbolic-proc/KLIC-New/klic-3.001.tgz` (also `symbolic-proc/unix/KLIC-New/`, and as `klic-system/klic.tgz`) | 812K, 1997-07-04 | resolved-not-read (206 on both mirrors) | KLIC version 3 (distributed-memory parallel KLIC) | Later than the held 2.002 |
| KLIC 3.002 | `../pub/klic/v3.0/klic-3.002.tgz` (= `klic.tgz` = `klic3.002.tgz`) | 817K, 1997-09-18 | resolved-not-read (206 on both mirrors) | Latest KLIC on these mirrors | Later than the held 2.002 |
| KL1 tutorial for KLIC | `symbolic-proc/klic-system/tutorial/{tutorial.tex,tutorial.dvi,KL1TUT.info}` | 94K-147K, 1995 | resolved-not-read | KL1 tutorial as Texinfo | -- |
| PIMOS-hosted KL1 tools | `symbolic-proc/pimos/{exreps,kl1graph,strtgysh,aya,ldlib}.tar.Z` | 120K-420K | resolved-not-read | ExReps, KL1 visualiser, strategy shell, AYA, load-distribution library | KL1 source that exercises PIMOS |
| Distributed Pool | `symbolic-proc/klic-apps/d-pool/{dpool_klic,dpool_pimos}.tgz` | 165K, 221K | resolved-not-read | D-Pool for KLIC and for PIMOS | -- |
| ESP applications on SIMPOS | `kbms-clp/simpos/{kappa2,kappa2d1,kappa2d2,kappa2d3,chal,cal-esp,knov}.tar.Z`; `solver-prover/simpos/{papyrus,euod,fuzclust}.tar.Z`; `natural-lang/simpos/{cil.tar.gz,disc,icotext,kwic-esp,kwic-esp-002,sum,txtstrct,utter}.tar.Z`; `exper-apps/simpos/gog-esp.tar.Z` | 74K-9.5M, 1992-94 | resolved-not-read | Application source in ESP for PSI/SIMPOS (Kappa-II is 25 MB in four archives) | The only surviving large bodies of ESP code; no SIMPOS itself |
| Common-ESP applications | `kbms-clp/cesp/cal-cesp.tar.Z`; `natural-lang/cesp/{kwic-cesp,linguist,morphana,sdiv}.tar.Z` | 79K-1.2M | resolved-not-read | CESP application source | CESP itself is not here (see quote) |
| General information | `INFO.tar.Z` | 21K | opened-and-read (contains `COPYRIGHT`, `cesp`, `character.e`, `klic`, `pdss`, `.j` versions) | Licence, character-code note, ESP-to-CESP guide, KLIC notes | States where CESP came from |
| IFS newsletters | `newsletter/E01.920701` ... `E09.950331`, `J01` ... `J09` | 5K-21K | resolved-not-read | IFS release notes 1992-95 | Release history of PIMOS / psdpim |
| AITEC contract research | `contract-research/{95,96,97,98}/DH*/` and `*_report/` | 347 files | index README opened-and-read | FY1995-98 funded work, e.g. DH7-1 "KLICの実行時システムの改良・拡張" (improvement of the KLIC runtime), DH7-5 KL1 goal-scheduling optimisation | KLIC-era, not PIM firmware |

Exact passages (from files fetched and read):

- `ifs/README`, directory section: "`pim-psi/ OS on PSI or PIM.` / `psdpim [03] Pseudo PIM (PIM emulator on PSI)` / `pimos [04] PIMOS (KL1 language system and OS)`". Nothing else is in `pim-psi/`.
- `INFO.tar.Z`, file `cesp`: "CESP is not part of the ICOT Free Software, instead being available from MITSUBISHI ELECTRIC COMPUTER SYSTEMS(TOKYO) CORP. (MTC)." and "CESP Ver.3.3 assumes the following environment. Computer : SUN4 (SPARC)". It was written "with the aid of" AI Language Research Institute, Ltd. (AIR), which "extended ESP, and developed CESP".
- `Museum/IFS/abst/003.html` (Pseudo PIM): "Machine: PSI-III / Environment: SIMPOS / Language: ESP, microprogram / Source Code: 2.5 MB / Documents: None" and "the language processor is implemented entierly by the microprogram code of PSI-III" [sic].
- `Museum/IFS/abst/002.html` (VPIM): "a common identical KL1 language processor on all PIM models (except for PIM/m)" and "To run VPIM on conventional machines and actually execute KL1 programs, a user-interface portion of PIMOS, FEP etc. are needed. However, the current distribution does not include such programs."
- `Museum/IFS/abst/004.html` (PIMOS): "Machine: PIM, Multi-PSI / Environment: SIMPOS / Language: KL1 / Source Code: 5.5 MB".

**Not found in `ifs/` or `pub/`** (filename search of all 23,910 crawled paths for
`psi`, `simpos`, `esp`, `kl0`, `csp`, `fep`, `kbn`, `firm`, `micro`, `cesp`): no SIMPOS
system, no ESP compiler/runtime, no KL0 firmware, no PSI-II or PSI-III microcode other
than `psdpim`, no microprogram assembler, no CSP, no FEP software, no `pimfep`, no `kbn`
tools, no PSI-UX, no Multi-PSI or PIM/m firmware.

#### 1.3 `Museum/IFS/` and related index pages

| Page (under `Museum/`, both mirrors) | Status | Content |
|---|---|---|
| `IFS/lang-E.html`, `lang-J.html` | opened-and-read | IFS grouped by language. The "ESP" group is item 3 (Pseudo PIM) plus 17 ESP applications; "PSL" is VPIM only |
| `IFS/field-E.html`, `field-J.html` | opened-and-read | IFS grouped by field; "Symbolic Processing" = items 1-8, 72-74, 78, 85, 86 |
| `IFS/abst/001.html` ... `100.html` (+ `-J`) | 002, 003, 004 opened-and-read | One abstract page per IFS item |
| `IFS/INFO/{character,cesp,klic}-{E,J}.html` | `klic-E` opened-and-read | HTML forms of the `INFO.tar.Z` notes |
| `IFS/pointers-E.html`, `IFS-column-E.html`, `about-IFS-E.html`, `access-E.html`, `list-of-IFS-E.html` | opened-and-read (pointers, column) | Navigation; no extra software |
| `IFSN/newsletter01`...`09` (E and J) | resolved-not-read | HTML IFS newsletters |
| `../Free-Software/Free-Software-E.html` | opened-and-read | External links: `http://www.klic.org/software/klic/index.en.html`, Waseda `klint`/`Kima`, Toyohashi "KLIC/TH" goal-scheduling KLIC, Tsukuba `Klitcl`/`Javaklic` (liveness of those external URLs: see item 7) |

#### 1.4 `Museum/MACHINE/` -- machine pages

All opened-and-read. These are photo galleries with at most a paragraph of text; none
mentions surviving hardware, firmware or documentation.

| Page | Content |
|---|---|
| `MACHINE/psi-I-E.html`, `-J` | 3 photos (PSI-I, inside, monitor screen) |
| `MACHINE/psi-II-E.html`, `-J` | 7 photos: "PSI-II (by Mitsubishi)", "PSI-II (by Oki)", "A processor board of PSI II", four chip photos |
| `MACHINE/multi-PSI.html` | "Under Construction"; Japanese text: purpose was to build "KL1の処理系（ファームウェア）、並列OS" on a real machine; PSI-II CPUs, 64 connected, four per cabinet |
| `MACHINE/pim-m-E.html`, `-J` | 9 photos: cabinet, back, inside, "processor board", "memory board", "network board" of PIM/m (`pim-m/pim-m-3.jpg`, `-31.jpg`, `-32.jpg`) |
| `MACHINE/pim-p-*.html`, `pim-c-*`, `pim-i-*`, `pim-k-*` | photo pages per model |
| `MACHINE/pim-spec-E.html`, `-J`, `pim-spec.html` | Comparison table of the five PIMs. "PIM/m targets the parallel software development machine and rigid compatibility with the Multi-PSI. Maximum 256 PEs can be connected with two dimensional mesh network. The PE of PIM/m has CISC-like micro programmable instruction set." |
| `MACHINE/chi-I-*.html`, `chi-II-*`, `delta-*` | CHI and Delta photo pages |

There is **no PSI-III or PSI-UX page**.

#### 1.5 `Museum/TRTM/` -- Technical Reports and Memoranda: what the lists hide

`TRTM/trtm-E.html` (opened-and-read) says: "ICOT published more than 900 Technical
Reports (TR) and more than 1300 Technical Memorandum (TM)" and "TRs and TMs can be read
at National Diet Library, Japan and Kawasaki Library established by Kanagawa Prefecture."

Comparison of the crawled directory against the list pages:

| Series | Numbers in list page | PDFs in `*pdf/` | `.idx` records in `*idx/` | PDF exists but number absent from list | No PDF at all |
|---|---|---|---|---|---|
| TR | 908 (`TRlist.html`) | 900 | 911 | 3: TR-618, 621, 622 | 11: TR-69, 111, 133, 221, 276, 277, 305, 340, 348, 542, 834 |
| TM | 935 (`TMlist.html`) | 1,305 | 1,322 | **384** | 17: TM-72, 81, 127, 376, 542, 543, 544, 688, 723, 901, 902, 917, 1168, 1185, 1280, 1281, 1283 |

TM numbers with a PDF but no line in `TMlist.html`: 14-23 184 187-188 191-193 195-197
199-200 202 204-207 210-213 218-219 221-223 228 230 232 251-252 257 259-261 263-266
268-272 277-279 282-283 285-286 313-321 324-329 332-350 353-363 365 369 371-375 378-380
382-383 385 387 394-396 429 432-436 438 440-443 446-448 450 452 454-455 457-462 466
481-482 485-486 492 499 517-519 521-523 526-527 529-541 545-562 564-565 569 571-572 578
582-585 589-590 592-593 607 614 619 623 625-627 637-638 642-643 645 647-648 650-653 660
662 665-666 668 670-671 686-687 695 702 705 708-711 713-714 735 738 740-741 744 748 752
758 766-770 772-780 789-790 794 798 832 834 836-838 840 842-852 870 872-873 876 896
904-916 918-926 929 1000 1004 1006 1009-1023 1025 1027 1029 1036 1039 1046-1047 1051
1059-1061 1077 1081-1084 1086-1098 1102-1105 1107-1108 1121-1122 1127 1154-1156
1213-1215 1217 1220 1222-1224 1228 1245 1247-1248.

Their titles are only in `Museum/TRTM/TM/TMidx/tmNNNN.idx` (Shift_JIS text: number, date,
title, authors, affiliations, section-to-page map). All 387 unlisted records were
downloaded and read. They are almost all two-page papers from the IPSJ national
conventions (27th, 33rd-46th), JSPP and similar, collected by ICOT. PDF URL pattern:
`.../Museum/TRTM/TM/TMpdf/tmNNNN.pdf`.

The ones that bear most directly on PSI-II / Multi-PSI / PIM/m firmware. "PDF checked"
means the PDF was downloaded from both mirrors and begins `%PDF-`; TM-1213 page 1 was
rendered and read.

| TM | Date | Title (as in the `.idx`) | English translation | Authors (as in `.idx`) | PDF checked |
|---|---|---|---|---|---|
| TM-1213 | 1992.10 | 情報処理学会 第45回全国大会論文集; PIM/mのメンテナンス系アーキテクチャとCSP | IPSJ 45th Nat. Conv.: Maintenance architecture and CSP on PIM/m | K.Takahashi, Y.Takeda, Y.Murasawa, R.Komori, E.Sugino | yes, 2 pp, page 1 read |
| TM-1021 | 1991.02 | 第42回情報処理学会全国大会発表論文集II; PIM/mフロントエンド・プロセッサ; GC方式とその評価 | 42nd: PIM/m front-end processor -- GC method and its evaluation | H.Tateno, Y.Kawada, K.Takahashi, M.Ikeda | yes, 2 pp |
| TM-1022 | 1991.02 | 同; PIM/mフロントエンド・プロセッサの速度性能評価 | 42nd: Speed evaluation of the PIM/m front-end processor | M.Saeki, H.Nakashima, H.Tateno, M.Ikeda, ... | yes, 2 pp |
| TM-850 | 1989.12 | 情報処理学会 第40回全国大会論文集; PIM/m要素プロセッサのアーキテクチャ | 40th: Architecture of the PIM/m processing element | H.Nakajima, Y.Takeda, K.Nakajima | yes, 2 pp |
| TM-849 | 1989.12 | 同; マイクロコード・チェッカ「マイクロリント」の開発 | 40th: Development of the microcode checker "Microlint" | S.Miyauchi, N.Ichiyoshi | yes, 2 pp |
| TM-662 | 1989.06 | 情報処理学会 第38回全国大会; マルチPSI/V2におけるコード形式について | 38th: On the code format in Multi-PSI/V2 (scan's own English title: "Code representation of Multi-PSI/V2") | Y.Miyazaki, Y.Nakagoshi, Y.Doumae, Y.Inamura, Y.Kimura, K.Nakajima (Fujitsu Social Science Laboratory, ICOT) | yes, 2 pp, page 1 read: KL1 module layout (module size, GC size, module name, GC area, code area, structure-constant area); says code is produced by a cross system on the PSI-II front-end processor and downloaded to the Multi-PSI |
| TM-652 | 1989.06 | 同; KL1抽象命令セットの改良について | 38th: On the improvement of the KL1 abstract instruction set | Y.Kimura, A.Goto, K.Nakajima, T.Chikayama | yes, 2 pp |
| TM-671 | 1989.06 | JSPP'89; マルチPSIにおけるデバッグ機能・メンテナンス機能 | JSPP'89: Debugging and maintenance functions on the Multi-PSI | E.Sugino, S.Furuichi, Y.Inamura, K.Taki | yes, 6 pp |
| TM-767 | 1989.07 | 第38回; Multi-PSI/V2における一括GC及びメモリ消費特性の評価 | 38th: Evaluation of batch GC and memory consumption on Multi-PSI/V2 | N.Miyauchi, Y.Kawata, K.Nakajima | resolved (listed in crawl) |
| TM-768 | 1989.07 | 第39回; 分散環境における構造体管理 | 39th: Structure management in a distributed environment | K.Rokusawa, T.Chikayama, H.Nakashima, K.Taki... | resolved (listed in crawl) |
| TM-551 | 1988.09 | 第37回; 分散環境におけるユニフィケーションの実現 | 37th: Realising unification in a distributed environment | K.Rokusawa, N.Ichiyoshi, T.Chikayama, H.Nakashima... | resolved (listed in crawl) |
| TM-443 | 1988.01 | 学会発表論文(PSI PIM)第4研究室; 並列処理における重みつき参照カウントを用いた実時間GC | Real-time GC using weighted reference counts in parallel processing | N.Ichiyoshi, K.Rokusawa, T.Chikayama, K.Nakajima... | resolved (listed in crawl) |
| TM-452 | 1988.01 | 同; 並列処理におけるPE間に渡るゴールの重みつき参照カウントを用いた管理方式 | Managing goals that span PEs using weighted reference counts | K.Rokusawa, N.Ichiyoshi, K.Taki, K.Yoshida... | resolved (listed in crawl) |
| TM-346 | 1987.07 | 第35回 4-1; マルチPSI第2版のPE間アドレス管理方法 | 35th: Inter-PE address management in Multi-PSI version 2 | K.Rokusawa, N.Ichiyoshi, T.Miyazaki, T.Chikayama... | yes, 2 pp |
| TM-359 | 1987.07 | 第35回 4-2; マルチPSI第2版のハードウェア構成 | 35th: Hardware configuration of Multi-PSI version 2 | Y.Takeda, H.Nakajima, K.Masuda, K.Taki | yes, 2 pp |
| TM-334, 336, 337 | 1987.07 | 第35回 4-1; MRBによる多重参照管理方式 (3 papers) | 35th: Multiple-reference management by MRB | Miyauchi / Chikayama, Kimura / Nishida et al. | resolved (listed in crawl) |
| TM-263 | 1987.02 | 第34回-4; 並列推論マシンPIM(2) KL1の抽象命令仕様とコンパイラ | 34th: PIM (2) -- KL1 abstract instruction specification and compiler | Y.Kimura, T.Chikayama, K.Kumon, H.Nakajima | yes, 2 pp |
| TM-268 | 1987.02 | 第34回-5; PSI-IIのシステム・アーキテクチャ (the `.idx` record mistypes it as "PIM-II"; the scan reads PSI-II) | 34th: System architecture of PSI-II (scan's own English title: "System Architecture of PSI-II") | Y.Inamura, K.Nakajima, H.Nakashima, T.Tanabe, T.Fukasawa, O.Nose, T.Ehara, Y.Hakeda (ICOT, Mitsubishi Electric, Oki) | yes, 2 pp, page 1 read: block diagram with CPU, WCS, console processor, I/O bus |
| TM-261 | 1987.02 | 第34回-3; PSI-IIシステムのファームウェア | 34th: Firmware of the PSI-II system | M.Ikeda, H.Tateno, A.Yamamoto, H.Yoshida, K.... | yes, 2 pp |
| TM-210 | 1986.08 | 第33回-6; マルチPSI要素プロセッサPSI-IIのアーキテクチャ | 33rd: Architecture of PSI-II, the Multi-PSI element processor | K.Nakajima, K.Taki, O.Nakajima, ... | yes, 2 pp |
| TM-211 | 1986.08 | 同; ...PSI-IIの最適化手法 | 33rd: Optimisation techniques of PSI-II | H.Nakajima, T.Chikayama, K.Nakajima | yes, 2 pp |
| TM-212 | 1986.08 | 同; ...PSI-IIのマイクロ・プログラム・シミュレータZEUS | 33rd: ZEUS, the microprogram simulator for PSI-II | M.Terayama, H.Yoshida, K.Nakajima | yes, 2 pp |
| TM-213 | 1986.08 | 同; ...PSI-IIのメモリ管理とプロセス管理 | 33rd: Memory and process management of PSI-II | H.Yoshida, M.Ikeda, H.Nakajima, M.Yokota, ... | yes, 2 pp |
| TM-353 | 1987.07 | 第35回 4-2; PSI-IIにおけるESPサポート用ファームウェア | 35th: Firmware for ESP support on PSI-II | M.Ikeda, M.Murasawa, H.Yoshida, T.Chikayama | yes, 2 pp |
| TM-354 | 1987.07 | 同; PSI-IIにおけるKL0実行順序系組み込み述語の実現方式 | 35th: Implementing KL0 control built-ins on PSI-II | H.Nakajima, H.Tateno, Y.Kimura | yes, 2 pp |
| TM-355-358 | 1987.07 | 同; PSI-IIのコンパイラ / 性能評価(1)(2)(3) (機械語命令評価, マイクロ命令動的評価) | 35th: PSI-II compiler; performance evaluation 1-3 (machine instructions, dynamic micro-instruction evaluation) | Kondo / K.Nakajima / Inamura / Yoshida et al. | resolved (listed in crawl) |
| TM-572 | 1988.09 | 第37回-2; PSI-IIの性能評価 | 37th: Performance evaluation of PSI-II | H.Tateno, S.Kondo, H.Nakajima, M.Ikeda... | resolved (listed in crawl) |
| TM-232 | 1986.10 | 第33回-9; 汎用アセンブラのPSI上への移植 | 33rd: Porting the general-purpose assembler to PSI | H.Tateno, S.Takagi | resolved (listed in crawl) |
| TM-348, 363, 432, 532, 564, 565, 775 | 1987-89 | 並列論理型OS-PIMOS (1)(2), PIMOSのタスク管理方式, 設計方針, シェル, 例外処理方式, 評価 | PIMOS: resource management, KL1 development system, task management, design policy, shell, exception handling, evaluation | Sato, Koshimura, Chikayama, Fujise, Matsuo, Miyazaki ... | resolved (listed in crawl) |
| TM-1047, 1092, 1013, 920 | 1990-91 | WTCを用いた分散プロセス制御方式 / 大域GCにおけるWTC方式を用いたマーキング終了検出 / メッセージの追い越しがある分散環境における... | Distributed process control using WTC; marking-termination detection for global GC using WTC; execution stop/restart and low-cost external reference management when messages overtake | Rokusawa, Ichiyoshi, Nakajima, Inamura, Nakase, Kawai, Imai | resolved (listed in crawl) |

A further ~75 unlisted TMs cover the other PIMs: PIM/i (TM-846, 847, 921-923, 929,
1014-1019, 1046, 1093, 1095-1098, 1247, 1248 -- including "KL1のRISC風PIM/i命令への展開"
and "PIM/iにおけるゴール通信方式の評価"), PIM/p (TM-526, 530, 531, 779, 1090, 1091, 1127 --
"PIM/pへのKL1処理系の実装", "PIM/pにおけるパイプライン制御方式"), PIM/c (TM-870, 1000 --
"水平型マイクロプログラムの自動生成と最適化"), PIM/k (TM-766, 1010-1012), the PIM
common KL1 system (TM-911, 912, 918), early PIM (TM-199, 200, 202, 230, 264-266, 272,
332, 333), MRB/LRC GC (TM-527, 539, 770, 798), and PSI-I (TM-18, 22). The machine-made
table of all 106 hardware/KL1 rows is in the scratchpad at `dl_tmidx/unlisted_table.md`
and the full 387-row title list at `dl_tmidx/unlisted_titles.tsv`.

Listed TR/TM titles that concern firmware, manuals or specifications (from the list
pages; the project holds the lists, so only the ones easy to overlook): TR-021
"汎用型マイクロプログラム・アセンブラ" (general-purpose microprogram assembler, Takagi,
83.08, 37 pp); TR-079 "逐次型推論マシンψのマイクロインタプリタ" (micro-interpreter of PSI,
Yamamoto et al., 84.09); TM-290 "PIMOS第一版概念仕様書" (PIMOS first-edition conceptual
specification, 64 pp); TM-305 "マルチPSIのベンチマーク方式" (81 pp); TM-684
"スイッチング・ユニット・チップ仕様書" (switching-unit chip specification, Tanaka et al., 77 pp);
TM-786 "オンラインSIMPOS照会書 操作説明書"; TM-857 "論理型言語処理マイクロプロセッサ"
(Ando et al., 90.02, 2 pp); TM-883/884 PIMOS primer 1.5 (J/E); TM-720 and TM-945 PDSS
manuals.

#### 1.6 `Museum/FGCS/` -- conference proceedings as per-paper PDFs

`Museum/FGCS/FGCS.html` (opened-and-read) is the index. Directories (file counts from
the crawl):

| Directory | Content (page count as stated on the index) | Files |
|---|---|---|
| `FGCS84en-rpt/`, `FGCS84jp-rpt/` | FGCS'84 conference report, English (92 pp) / Japanese 会議録 (199 pp) | 16 / 31 |
| `R&D84en-rpt/`, `R&D84jp-rpt/` | "Report on ICOT's R&D in the Initial Stage" (91 pp) / Japanese (65 pp) | index opened |
| `FGCS84en-proc/` | FGCS'84 Proceedings (706 pp) | 76 |
| `FGCS84en-prs/`, `FGCS84jp-opn/` | press proceedings (88 pp), opening | 9 / 9 |
| `FGCS88en-rpt/`, `FGCS88jp-rpt/` | FGCS'88 conference report (128 pp) / Japanese 会議録 (261 pp, `88jR001`-`88jR116.pdf`) | 16 / 140 |
| `R&D88en-rpt/` | "Report on ICOT's R&D in the Intermediate Stage" (117 pp), `88e001`-`88e007.pdf` | index opened |
| `FGCS88en-proc1/`, `proc2/`, `proc3/` | **FGCS'88 Proceedings vols 1-3** (325 + 496 + 491 pp) | 35 / 60 / 59 |
| `FGCS88jp-demo/` | FGCS'88 demonstration descriptions, Japanese (144 pp) | 33 |
| `FGCS92en-rpt/`, `FGCS92jp-rpt/` | FGCS'92 conference report / Japanese 会議録 (262 pp) | 17 / 127 |
| `FGCS92jp-out/` | 第五世代コンピュータの研究開発成果 (R&D results of the FGCS project, Japanese, 180 pp) | 13 |
| `FGCS92en-proc1/`, `proc2/` | FGCS'92 Proceedings (per-paper mirror of the held bitsavers volumes) | 47 / 94 |
| `FGCS92jp-demo/` (+ HTML at `Museum/FGCS92Demo/{E,J}/`) | FGCS'92 demonstration descriptions (121 pp) | 30 |
| `FGCS94en-prg/`, `FGCS94en-proc/`, `FGCS94en-material/` | FGCS'94 program, Proceedings (160 pp), presentation materials (176 pp) | 10 / 18 / 16 |
| `FGCS94en-work1/` ... `work5/`, `FGCS94jp-work6/` | FGCS'94 workshops (1 = Parallel Logic Programming, 175 pp; 6 = Parallel and Distributed LSI-CAD) | 18 / 15 / 27 / 16 / 14 / 23 |
| `Museum/FGCS94/PS/` | FGCS'94 papers as PostScript: `eval-of-PIM.ps.gz`, `klic.ps.gz`, `parallel-basic-soft.ps.gz`, `distributed.ps.gz`, `general-report.ps.gz`, ... (15 files) | 15 |

**FGCS'88 hardware / KL1-implementation papers**, file name under
`Museum/FGCS/FGCS88en-procN/` (index pages opened-and-read; `88eIRT-2`, `88ePARA2-2`,
`88ePIM-4` resolved on both mirrors, others resolved in the crawl listing):

| File | Vol, page | Paper |
|---|---|---|
| `proc1/88eR&D-2.pdf` (2.8M; URL needs `%26`) | 1, p.16 | Uchida, Taki, Nakajima, Goto, Chikayama: Research and Development of the Parallel Inference System in the Intermediate Stage of the FGCS Project |
| `proc1/88eIRT-2.pdf` (3.2M) | 1, p.208 | Goto, Sato, Nakajima, Taki, Matsumoto: Overview of the Parallel Inference Machine Architecture (PIM) |
| `proc1/88eIRT-3.pdf` (3.4M) | 1, p.230 | Chikayama, Sato, Miyazaki: Overview of the Parallel Inference Machine Operating System (PIMOS) |
| `proc1/88eTPCS-6.pdf` | 1, p.165 | Ueda: Theory and Practice of Concurrent Systems -- The Role of Kernel Language in the FGCS Project |
| `proc2/88ePAT1-4.pdf` | 2, p.582 | Ueda, Furukawa: Transformation Rules for GHC Programs |
| `proc2/88eCOM-2.pdf` | 2, p.638 | Yoshida, Chikayama: A'UM -- A Stream-Based Concurrent Object-Oriented Language |
| `proc2/88ePPL-4.pdf` | 2, p.774 | Tanaka: Meta-Interpreters and Reflective Operations in GHC |
| `proc3/88ePARA2-2.pdf` (1.5M) | 3, p.904 | Ichiyoshi, Rokusawa, Nakajima, Inamura: A New External Reference Management and Distributed Unification for KL1 |
| `proc3/88ePIM-1.pdf` (1.3M) | 3, p.953 | Shinogi, Kumon, Hattori, Goto, Kimura, Chikayama: Macro-Call Instruction for the Efficient KL1 Implementation on PIM |
| `proc3/88ePIM-3.pdf` | 3, p.970 | Koike, Tanaka: Multi-Context Processing and Data Balancing Mechanism of the Parallel Inference Machine PIE64 |
| `proc3/88ePIM-4.pdf` (1.2M) | 3, p.978 | Takeda, Nakashima, Masuda, Chikayama, Taki: A Load Balancing Mechanism for Large Scale Multiprocessor Systems and Its Implementation |
| `proc3/88eSPM-1.pdf` | 3, p.987 | Sugie, Yoneyama, Ido, Tarui: Load-Dispatching Strategy on Parallel Inference Machines |
| `proc3/88eSPM-2.pdf` | 3, p.994 | Tick: Compile-Time Granularity Analysis for Parallel Logic Programming Languages |
| `proc3/88eIMPL-1.pdf` ... `88eIMPL-4.pdf` | 3, pp.1031-1059 | Flat GHC on the Connection Machine (Nilsson, Tanaka); KL1 in Condition Graphs on a Connection Machine (Barklund et al.); A Parallel Implementation of GHC (Glauert, Papadopoulos); LogDf (Biswas, Tseng) |
| `proc3/88eITIM-1.pdf`, `88eITIM-2.pdf` | 3, pp.922, 931 | A Light-Weight Prolog Garbage Collector (Touati, Hama); Wide Instruction Word Architecture ... BSL (Ebcioglu, Kumar) |
| `proc3/88eINV-1.pdf` | 3, p.943 | Warren, Haridi: Data Diffusion Machine |

**FGCS'94 papers** under `Museum/FGCS/FGCS94en-proc/` (index opened-and-read; `94eEPIM`
resolved on both mirrors): `94ePBSOFT.pdf` Chikayama "Parallel Basic Software" (p.10);
`94ePIKL1.pdf` Fujise, Chikayama, Rokusawa, Nakase "KLIC: A Portable Implementation of
KL1" (p.66); **`94eEPIM.pdf` Kumon, Hatazawa "The Evaluation of Parallel Inference
Machines" (p.80)**; `94eDPII.pdf` Sato, Yamauchi, Chikayama "Distributed Pool and its
Implementation" (p.90); `94eFOLWON.pdf` Uchida general report. Workshop 1
(`FGCS94en-work1/`): `94eLANG2.pdf` "An Efficient Implementation of Reflection in KL1";
`94eDIST1.pdf` "Design and Implementation of a Handy Distributed KLIC System";
`94eDIST2.pdf` Rokusawa et al. "Reference Loops Management in a Distributed KLIC
Implementation"; `94eGARB2.pdf` Ichiyoshi, Morita, Chikayama "A Shared-Memory Parallel
Extension of KLIC and its Garbage Collection".

**FGCS'84 PSI papers** under `Museum/FGCS/FGCS84en-proc/` (index opened-and-read;
`84eANGC2-2` resolved on both mirrors): `84eR&D-4.pdf` Uchida, Yokoi "Sequential
Inference Machine: SIM -- Progress Report" (p.58); `84eR&D-5.pdf` "SIM -- Its Programming
and Operating System" (p.70); `84eLPLM1-4.pdf` Chikayama "Unique Features of ESP"
(p.292); `84eANGC2-1.pdf` Taki, Yokota, Yamamoto, Nishikawa, Uchida et al. "Hardware
Design and Implementation of the Personal Sequential Inference Machine (PSI)" (p.398);
**`84eANGC2-2.pdf` Yokota, Yamamoto, Taki, Nishikawa, Uchida "A Microprogrammed
Interpreter for the Personal Sequential Inference Machine" (p.410)**.

**Japanese-language items worth opening** (index pages opened-and-read, PDFs resolved):
`FGCS88jp-demo/88jDEMO01.pdf` -- demonstration 1, "並列ソフトウェア開発システム" (Multi-PSI
hardware, the KL1 distributed implementation, PIMOS, "PSI-II上の並列ソフトウェア開発環境：
PIMOS-S", the Multi-PSI utilisation monitor); `FGCS92jp-out/92jOUT1.pdf` Taki
"並列推論マシンPIM" (p.41) and `92jOUT2.pdf` Chikayama "オペレーティングシステムPIMOSと
核言語KL1" (p.64); `FGCS92jp-out/92jTOTAL3.pdf` Uchida "並列推論マシンと基本ソフトウェア総論".

#### 1.7 Other document series in `Museum/`

| Series | Path | Status | What is there |
|---|---|---|---|
| ICOT Journal | `JOURNAL/journal-index-E.html`, `icot-jrnl01.html` ... `42.html` (+ `-J` to no.37) | opened-and-read (index, no.20) | **Tables of contents only** for all 42 issues (1983-1995); no article scans. `HISTORY/PDF/` has 16 PDFs of page ranges (`006-017.pdf` ... `170-184.pdf`, 1.0-2.3 MB) excerpted for the Japanese history pages `HISTORY/83-J.html` ... `94-2-J.html` |
| Symposium slides | `SYMPO/symposium.html`, `SYMPO/R&D86jp-sld/`, `R&D88jp-sld/`, `R&D89jp-sld/`, `R&D90jp-sld/`, `R&D93jp-ref/` | opened-and-read (all five index pages, via `%26`) | Japanese slide sets of the 4th/6th/7th/8th/10th FGCS symposia. Relevant: `86jSLD10.pdf` "KL1言語系（KL1-b）", `86jSLD16.pdf` PIM mid-term plan, `86jSLD17.pdf` Taki "並列ソフトウェア開発用マシン マルチPSIシステム", `88jSLD07.pdf` Goto "PIMのKL1並列処理系用GC方式", `88jSLD08.pdf` "PIMOSとユーザプログラムの間の通信方式", **`89jSLD06.pdf` Nakajima K. "マルチPSI上へのKL1分散処理系の実装"** (Implementation of the distributed KL1 system on the Multi-PSI), `90jSLD06.pdf` Imai "PIM用のKL1処理系とその開発支援環境", `90jSLD07.pdf` Shinogi "並列推論マシンPIM/pのアーキテクチャ" |
| Steering-committee papers | `Minutes/HomePage.html`, `Minutes/S56-1/` ... `H4-3/` | index opened-and-read | 7,764 files: materials of the 推進委員会 (project promotion committee) for every meeting from June 1981 to March 1993 -- plans, budgets, progress reports written for non-specialists |
| Final evaluation workshop | `FinalEval/` (`PDF/` 23 files, `GIF/tm1216/`) | resolved-not-read | "Proceedings of the FGCS Project Evaluation Workshop" (title from `museum-E.html`; the image directory is named `tm1216`) |
| Final report (follow-on project) | `FinalReport/final.html`, `node1`-`node53.html`, `appendix/` | resolved-not-read | LaTeX2HTML report |
| Slides of results | `FGCS-OHP/FGCS-OHP-latest-E.htm` | resolved-not-read | OHP set for the project and follow-on project |
| ICOT TODAY | `TODAY/icot-today01`-`13.html` | resolved-not-read | Japanese newsletter, HTML |
| AITEC News | `NEWS/newsletter01`-`16` (E/J) | resolved-not-read | AITEC newsletters 1995-98 |
| IFS Newsletter | `IFSN/`, `ifs/newsletter/` | resolved-not-read | 9 issues, 1992-95 |
| MITI Research Review | `MITIrr/HomePage.html`, `MITIrr/PDF/section1-5.pdf` | opened-and-read (index) | 中村・渋谷, "日本の技術政策 -- 第五世代コンピュータの研究開発を通じて", MITI Research Review No.5, May 1995, pp.108-133 |
| Videos | `VIDEO/PSI/MPlayer/{icot,melco,psi,esp,prolog,simpos,closing}.wmv` (2.5-5.5 MB), `VIDEO/FGCS91-J/`, `VIDEO/ICOT94Dec/`, `VIDEO/MrBengo/` | index opened-and-read; `psi.wmv` resolved on both mirrors | "PROLOG AI ワークステーション PSI" video in seven parts, incl. "三菱電機とPSI" (3:30), "This is PSI" hardware (2:19), "PSIのソフトウェアSIMPOS" (2:46) |
| International agreements, funding, contest | `ICRA/`, `IExchange/`, `FUNDING/`, `CONTEST/`, `InvitedResearcher/` | resolved-not-read | MoUs, AITEC funding programme, KLIC contests |
| AITEC half of the archive | `https://www.uedalab.jp/AITEC_ICOT_ARCHIVES/AITEC/` (`Report/H7-reports` ... `H14-reports`, `Ronbun/`, `Seminar/`) | listing opened-and-read | AITEC survey reports FY1995-2002; not searched further |

**No "manual" directory exists other than `ifs/manuals/`.** No annual-report series was
found. The document series present are: TR, TM, ICOT Journal (contents only), ICOT TODAY,
IFS Newsletter, AITEC News, the conference/symposium sets and the committee papers.

#### 1.8 Who maintains the mirror

`changelog-E.html` (opened-and-read) states: "The DVD content was copied to this site in
2016-2018. The work below was done from 18 to 30 September 2026 ... at the request of the
site maintainer." The archive's own top page credits the 2005 DVD to JIPDEC ("copyright
2005 JIPDEC"). The mirror is therefore actively maintained. Its site root (`https://www.uedalab.jp/`,
opened-and-read) is titled "Ueda Lab. Homepage"; the archive's own `Free-Software` page
lists "Prof. Ueda Waseda University" as the maintainer of the KL1 tools `klint` and
`Kima`. Whether the laboratory holds ICOT material that was not on the DVD was not
established; it is the obvious party to ask.

#### Queries / fetches tried for item 1

No search engine was needed; everything is from direct fetches: `UEDA` and `AIST` roots;
`ICOT/`, `ICOT/ifs/`, `ICOT/pub/`, `ICOT/Museum/` recursive listings; `ifs/README`;
`Museum/museum-E.html`, `library.html`, `old_library.html`; `Museum/IFS/{lang,field,
pointers,IFS-column}-E.html`, `abst/00{2,3,4}.html`, `INFO/klic-E.html`;
`Museum/MACHINE/*.html`; `Museum/TRTM/trtm-E.html`, `TR/TRlist.html`, `TM/TMlist.html`,
387 `TM/TMidx/tmNNNN.idx`; `Museum/FGCS/FGCS.html` and the index page of each
proceedings directory; `Museum/JOURNAL/journal-index-E.html`; `Museum/SYMPO/*`;
`Museum/Minutes/HomePage.html`; `Museum/MITIrr/HomePage.html`;
`Museum/VIDEO/PSI/HomePage.html`; `changelog-E.html`; `Free-Software/Free-Software-E.html`;
`AITEC/` listing.

---

### Item 2 -- bitsavers

| Item | URL | Status | What it contains | Why it matters |
|---|---|---|---|---|
| `pdf/icot/` | `https://bitsavers.org/pdf/icot/` | opened-and-read (listing) | Exactly two files: `Fifth_Generation_Computer_Systems_1992_Volume_1.pdf` (39M) and `..._Volume_2.pdf` (64M), dated 2015-09-16 | Already held. Nothing else |
| `pdf/mitsubishi/` | `https://bitsavers.org/pdf/mitsubishi/` | opened-and-read (listing + index) | `disk/`, `floppy/`, `monitor/`, and `Mitsubishi_VLSI_MOS_Memory_RAM_ROM_and_Memory_Cards_Jan91.pdf`. 85 index entries: floppy/disk drive manuals, Diamondscan monitors, one memory data book | No MELCOM, no PSI. The 1991 memory data book could matter only for identifying RAM parts on PIM/m boards |
| `bits/ICOT/` | `https://bitsavers.org/bits/ICOT/` | dead (404) | -- | No ICOT software on bitsavers |
| `pdf/icot_corp/` | index line `icot_corp/ICOT_ICOBUS_757-14_ROM_dumps.zip` | resolved-not-read (index entry only) | An unrelated US company named ICOT Corp | False positive; ignore |
| Whole-site index, PDFs | `https://bitsavers.org/pdf/IndexByDate.txt` | opened-and-read (93,705 lines, grepped) | Searched for ` icot/`, `fifth.?gen`, `FGCS`, `melcom`, `inference`, `logic.?prog`, `simpos`, `kl1`, `multi-?psi`, `_PSI[_-]` | Only the two FGCS'92 volumes match. Every `PSI` hit is DEC VAX PSI, Honeywell PSI or HP PSI |
| Whole-site index, software | `https://bitsavers.org/bits/IndexByDate.txt` | opened-and-read (70,865 lines, grepped) | Searched for `icot`, `melcom`, `mitsubishi`, `simpos`, `prolog`, `fifth` | Nothing relevant (matches are "Apricot", Tektronix 4404 Prolog, PDP-8 music files) |
| Vendor directories | `pdf/fujitsu/`, `pdf/hitachi/`, `pdf/toshiba/`, `pdf/nec/` (no `pdf/oki/`) | opened-and-read (index) | Fujitsu: brochures, disk, floppy, tape, mainframe, and the journal below. Hitachi: disk, HITAC 303, a paper-tape reader. Toshiba: CD/DVD/floppy drives, T-250 | No PIM/p, PIM/c, PIM/k material |
| FUJITSU Scientific & Technical Journal | `https://bitsavers.org/pdf/fujitsu/Fujitsu_Scientific_and_Technical_Journal/` -- 17 issues: V24 N1-4 (1988), V25 N4 (1989-12), V26 N1-4 (1990-91), V27 N1, N2, N4 (1991), V28 N1-3 (1992), V29 N1-2 (1993) | **opened-and-read**: all 17 downloaded (24-97 MB each), text-extracted with `pdftotext`, grepped for "parallel inference", "KL1", "PIM/p", "Fifth Generation", "ICOT" | One relevant article: **V29 N2 (June 1993), "ParaGraph: A Graphical Tuning Tool for Multiprocessor Systems", Seiichi Aikawa, Mayumi Kamiko, Takashi Chikayama** (manuscript received November 30, 1992) -- about load-distribution profiling on PIM under PIMOS. V26 N1 (1990-04) has references to ICOT work in one article's bibliography; V24 N3 only a passing phrase | No PIM/p hardware article in the issues bitsavers holds. Missing issues (V25 N1-3, V27 N3, V28 N4, V29 N3-4) were not checked here -- see item 5 |
| `magazines/` | `https://bitsavers.org/magazines/` | opened-and-read (listing) | US trade magazines only | No Japanese vendor journals |

Not found on bitsavers: anything on PSI, PSI-II, PSI-III, PSI-UX, MELCOM PSI, Multi-PSI,
any PIM, SIMPOS, ESP, KL0, KL1, PIMOS.

Fetches tried: the six URLs above plus `https://bitsavers.org/pdf/` and
`https://bitsavers.org/bits/` top listings.

---

> Items 3-8 below were researched by three delegated search agents working to the same rules; their sections are reproduced as written, with their own status vocabulary (stated at the head of each). The parent agent re-checked a sample of their key URLs and quotes directly: the two IPSJ museum sentences and the two JAIST sentences (grep in raw bytes, 1 match each); five Mitsubishi Denki Giho PDFs (HTTP 206, application/pdf); the CMU ICOT directory, `manuals/pimos/man.tgz` and `pimosman.pgz`; the uedalab software page and `klic-3.014.tgz`; the GitHub KLIC mirror; the KLIC manual page; three archive.org metadata records (`logicprogramming01lusk` and `peogrammingoffut0000kfuc` restricted, `primetimefreewar0000unse` not restricted); four IPSJ PDFs. One discrepancy is noted in the consolidated list (Wayback KLIC 3.003). Where an agent wrote "the caller" it means this project.

#### Method note of the agent for items 3, 7, 8

Run date 2026-11-20. All fetches used curl with User-Agent "Mozilla/5.0" (archive.org / Wayback CDX / GitHub / Open Library / HN APIs, CMU, AIST, uedalab) or the WebSearch tool. WebFetch was not used at all, so nothing here passed through a summarising model except WebSearch result summaries, which are used only as pointers (every URL taken from them was then fetched with curl, or is marked "cited-only").
Status vocabulary: **opened-and-read** (content fetched with curl and read as text), **metadata-read** (archive.org `/metadata/ID` JSON read; the book itself NOT opened), **resolved-not-read** (HTTP status + type/bytes only), **cdx-row-only** (only a Wayback CDX index row seen; capture not fetched), **cited-only**, **dead**.
Quotes in section (b) of each item were confirmed with `grep -F` against the raw downloaded bytes unless explicitly marked otherwise.
**Quotation marks:** byte-verified passages appear ONLY in the (b) sections. Double quotes elsewhere (table cells) enclose names of books, sections, menu items or file names taken from catalogue metadata, directory listings, or my de-kerned reading of PostScript text; they are labels, not verified verbatim passages.
Downloads are in the sibling `dl_agentA/` directory (subdirs `ia/`, `cdx/`, `gh/`, `web/`, `cmu/`).

**Headline finding (affects Items 3, 7, 8): the CMU Artificial Intelligence Repository still serves a June-1995 snapshot of `ftp.icot.or.jp:/ifs/` (re-packed as .tgz), including a `manuals/` tree (PIMOS manual PostScript V1.5 English + V3.0 Japanese, PIMOS 3.0 primer, KL1 textbook, "Introduction to KL1", ESP manuals), `symbolic/pim_psi/pimosman.pgz` (= gzip of `pimosman.ps`, PIMOS Manual V3.0, 504 pages), IFS newsletters, and KLIC 1.000-1.410.** Whether these `manuals/` packages are also in the uedalab/AIST IFS mirror was not checked by me (the caller is crawling those).

### Item 3 — archive.org / Wayback / other mirrors

#### (a) Table

| item | exact URL | status (+evidence) | what it contains | why it matters |
|---|---|---|---|---|
| FGCS'88 proceedings (3 vols) on archive.org | (none) | **absent** as a scanned book: 6 title/creator queries returned no FGCS 1988 item; Open Library lists 6 works, all `ebook_access: no_ebook`, `ia: None` | — | Not borrowable or viewable at archive.org |
| FGCS'88 proceedings, per-paper PDFs on the AIST ICOT mirror | https://www.airc.aist.go.jp/aitec-icot/ICOT/Museum/FGCS/FGCS88en-proc3/88ePIM-4.pdf ; index https://www.airc.aist.go.jp/aitec-icot/ICOT/Museum/FGCS/FGCS88en-proc3/FGCS88en-proc3.html | resolved-not-read (HEAD 200, application/pdf, 1,232,615 bytes; index HEAD 200 text/html) | FGCS'88 vol.3 paper PDF (file name suggests a PIM paper) | The proceedings exist free as per-paper PDFs in the ICOT archive (caller's crawl covers this); Wayback did NOT capture them on the old host (rows 404/410 only) |
| FGCS'84 proceedings on archive.org | (none) | **absent**: Open Library 3 works, all `no_ebook` | — | — |
| FGCS'84 proceedings PDFs, Wayback copy of old ICOT host | https://web.archive.org/web/20040717014328id_/http://www.icot.or.jp/ARCHIVE/Museum/FGCS/FGCS84en-proc/84eANGC1-1.pdf | resolved-not-read (HEAD 200 application/pdf 1,205,958 bytes); CDX shows 58 PDF rows with status 200 under `ARCHIVE/Museum/FGCS/FGCS84en-proc/` | FGCS'84 English proceedings, per paper | Independent mirror of the AIST copy (live AIST file HEAD 200, same 1,205,958 bytes) |
| FGCS 1981 conference proceedings (Moto-oka ed., North-Holland 1982) | https://archive.org/details/fifthgenerationc0000inte | metadata-read: `access-restricted-item: true`, collections `internetarchivebooks, inlibrary, printdisabled` | Full scan, 20.5 MB PDF (private) | **Borrowable** (controlled lending), not full view |
| "Introduction of the Fifth Generation Computer Systems 1981" | https://archive.org/details/TNM_Introduction_of_the_Fifth_Generation_Computer_20180309_0160 | metadata-read: no access restriction, collection `tednelsonjunkmail`, PDF 1,116,977 bytes | Short 1981 brochure-type document | **Full view** |
| ICLP'87 (4th Int. Conf., Lassez ed., MIT Press 1987) | https://archive.org/details/LogicProgr_00_Lass and https://archive.org/details/logicprogramming0000unse_b9u9 | metadata-read both: `access-restricted-item: true`; collections `mitpress, americana, inlibrary, printdisabled` / `internetarchivebooks, inlibrary, printdisabled`; metadata date 1987; both carry ISBN 0262121255 (so two scans of the same set; volume split not stated in metadata) | Proceedings scan | **Borrowable** |
| ICLP'88 (5th Int. Conf. and Symp., Kowalski & Bowen) | https://archive.org/details/LogicProgr_00_Kowa | metadata-read: restricted, `mitpress, inlibrary, printdisabled`, date 1988 | Proceedings scan | Borrowable (not asked for, listed for completeness) |
| ICLP'89 (6th Int. Conf., Lisbon; Levi & Martelli) | (none) | **absent**: `title:(logic programming sixth international conference)` 0 hits; creator Levi/Martelli 0 hits; Open Library work OL19127550W "Logic programming" 1989 MIT Press `no_ebook` | — | Not on archive.org |
| ICLP'90 (7th Int. Conf.) | https://archive.org/details/logicprogramming0000unse_h6h8 | metadata-read: restricted, `inlibrary, printdisabled`, date 1990, ISBN 0262730901 | Proceedings scan | Borrowable |
| NACLP'89 vol. 1 (Lusk & Overbeek) | https://archive.org/details/logicprogramming01lusk | metadata-read: restricted; `mitpress, americana, inlibrary, printdisabled`; `volume: Volume 1`; date 1989 | Scan, 152 MB PDF (private) | **Borrowable** |
| NACLP'89 vol. 2 | https://archive.org/details/logicprogramming02lusk | metadata-read: restricted; same collections; `volume: Volume 2` | Scan, 101 MB PDF (private) | **Borrowable** |
| NACLP'90 (Debray & Hermenegildo) | https://archive.org/details/logicprogramming00debr | metadata-read: restricted, `mitpress, inlibrary, printdisabled` | Scan | Borrowable |
| "Implementations of Distributed Prolog" (Kacsuk & Wise, Wiley 1992) | (none) | **absent**: title query 0 hits; `creator:(Kacsuk)` finds only a different book; Open Library OL19499398W `no_ebook` | — | Chapter "Distributed Implementation of KL1 on the Multi-PSI" is not obtainable here |
| (related) Kacsuk, "Execution models of Prolog for parallel computers" 1990 | https://archive.org/details/executionmodelso0000kacs | metadata-read: restricted, `inlibrary, printdisabled` | Different book by same author | Borrowable; only tangential |
| "Programming of Future Generation Computers" (Fuchi & Nivat, 1988), vol. I | (none) | **absent** on archive.org; Open Library OL4619001W `no_ebook` | — | — |
| "Programming of Future Generation Computers II" (Fuchi & Kott, 1988) | https://archive.org/details/peogrammingoffut0000kfuc | metadata-read: title mis-spelt "Peogramming Of Future Generation Computers II"; creator "K. Fuchi and L. Kott"; `access-restricted-item: true`; collections `internetarchivebooks, universityofarizonalib, printdisabled, inlibrary`; PDF 21.8 MB (private) | Full scan of vol. II | **Borrowable**. Findable only via the mis-spelt title |
| PIMOS manuals on archive.org | (none) | **absent**: `title:(PIMOS) OR subject:(PIMOS)` 0 hits; bare `PIMOS` 2 irrelevant hits | — | See CMU rows below for manuals |
| Logic Programming '86 / '87 (Tokyo conf., Springer LNCS) | https://archive.org/details/logicprogramming0000unse_q8s7 ; https://archive.org/details/logicprogramming0000unse_p9d3 | metadata-read: both restricted, `internetarchivebooks, printdisabled` only (no `inlibrary`) | Japanese LP conference proceedings (ICOT-era papers) | **Print-disabled only** |
| IFIP TC10 "Fifth generation computer architectures" 1986 | https://archive.org/details/fifthgenerationc0000ifip | metadata-read: restricted, `inlibrary, printdisabled` | Proceedings | Borrowable |
| Moto-oka, "The fifth generation computer: the Japanese challenge" 1985 | https://archive.org/details/fifthgenerationc0000moto | metadata-read: restricted, `inlibrary, printdisabled` | Book | Borrowable |
| "New generation computer systems" proceedings 1989; "New generation computing: recent research" 1990; "World yearbook of new generation computing R&D" 1988 | https://archive.org/details/newgenerationcom0000inte ; https://archive.org/details/newgenerationcom0000ciyu ; https://archive.org/details/worldyearbookofn0000unse | first: search row only (collections `inlibrary, printdisabled`); other two metadata-read: restricted | Background books | Borrowable |
| New Generation Computing (journal) | https://archive.org/details/pub_new-generation-computing | metadata-read: an empty periodical *collection* record (ISSN 0288-3635, Springer); queries `collection:"pub_new-generation-computing"` and `identifier:sim_new-generation-computing*` both returned 0 items | Placeholder only | No issues are actually scanned there |
| ICOT Journal on archive.org | (none) | **absent**: `title:("ICOT Journal") OR ...` 0 hits | — | Wayback has only HTML index pages `/ICOT/Publication/Journal/icot-jrnl24..31(-J).html` (cdx-row-only, 200, <1 KB each) |
| ONR Far East Scientific Bulletin vol. 9 no. 4 (1984) | https://archive.org/details/DTIC_ADA151274 | metadata-read: unrestricted, PDF 9.4 MB; surfaced by full-text `ICOT` query; not opened | US Navy report issue mentioning ICOT | Full view; relevance unverified |
| Xerox PARC tape "Parallel Logic Programming" (1986), 2 reels | https://archive.org/details/xerox-parc-tapes-v-345-1 ; https://archive.org/details/xerox-parc-tapes-v-345-2 | search row only (mediatype movies, collection `xerox-parc`) | Video of a 1986 talk; speaker not checked | Possibly relevant; unverified |
| Shapiro (ed.) "Concurrent Prolog: collected papers" vols 1-2; Tick "Parallel logic programming" 1991 | https://archive.org/details/concurrentprolog01shap ; https://archive.org/details/concurrentprolog02shap ; https://archive.org/details/parallellogicpro00tick | metadata-read (first two): restricted, `mitpress, inlibrary`; third search row only | Background on FGHC/KL1-family implementation | Borrowable |
| **CMU AI Repository: mirror of `ftp.icot.or.jp:/ifs/` (June 1995 file dates)** | https://www.cs.cmu.edu/afs/cs/project/ai-repository/ai/areas/icot/ (description page https://www.cs.cmu.edu/afs/cs.cmu.edu/Web/Groups/AI/util/areas/icot/0.html ; index https://www.cs.cmu.edu/afs/cs/project/ai-repository/ai/areas/icot/index.txt) | **opened-and-read** (curl; directory listing 4,168 bytes, index.txt 6,299 bytes, 0.html 3,964 bytes) | Top level: `apps/ kbms_clp/ manuals/ newsltr/ nlp/ reasonng/ symbolic/ info.tgz index.txt readme.txt readme_j.txt cesp.txt`. index.txt lists IFS catalogue numbers [01]-[84] | **Another mirror of everything the caller holds, plus manuals (Item 8).** Files are re-packed `.tgz` (not the original `.tar.Z`), each with a `.ltv` (tar listing) |
| CMU mirror: `symbolic/pim_psi/` | https://www.cs.cmu.edu/afs/cs/project/ai-repository/ai/areas/icot/symbolic/pim_psi/ | opened-and-read (listing); `.ltv` listings of pimos, pimosman, pimosobj, psdpim downloaded and read | `pimos.tgz` 1.4M, `pimosman.tgz` 347K, `pimosman.pgz` 637K, `pimosobj.tgz` 1.7M, `psdpim.tgz` 950K. Listings show e.g. `psdpim/INSTALL.DIR/pimfep.ptf` (266,512), `pimmcsp.ptf` (1,496,186), `mpsicspR.ptf`, `pimscsi.ptf`, `psdpim/PMPSI.DIR/pimm.MEkbn` (506,624), `object/pimm_ipl.kbn` (92,160), `object/pimos.ipl`, `object/pimm_*360E.sav` | Mirror of held pimos / pimosman / pimosobj / psdpim (tar dates Mar-May 1994). Byte-identity with the caller's `.tar.Z` not checked |
| CMU mirror: `symbolic/unix/` | https://www.cs.cmu.edu/afs/cs/project/ai-repository/ai/areas/icot/symbolic/unix/ | opened-and-read (listing) | `pdss.tgz` 1.4M, `pkl1.tgz` 70K, `vpim.tgz` 913K, `aum/`, `klic/` | Mirror of held pdss / pkl1 / vpim |
| CMU mirror: `symbolic/pimos/` | https://www.cs.cmu.edu/afs/cs/project/ai-repository/ai/areas/icot/symbolic/pimos/ | opened-and-read (listing) | `aya.tgz`, `exreps.tgz`, `kl1graph.tgz`, `ldlib.tgz`, `strtgysh.tgz` | KL1 programs that ran on PIMOS (test material) |
| CMU mirror: IFS newsletters | https://www.cs.cmu.edu/afs/cs/project/ai-repository/ai/areas/icot/newsltr/ (`e01_07.tgz` 19K, `j01_08.tgz` 24K) | listing + `e01_07.ltv` opened-and-read; tgz not downloaded | English newsletters E01 (1992-07-01) to E07 (1994-01-14); Japanese 01-08 | Release notes / change history of IFS packages |
| archive.org WARC of the whole CMU AI Repository (2019-10-20) | https://archive.org/details/warc_www_cs_cmu_edu-afs-cs-project-ai-repository-ai_20191020 | metadata-read: unrestricted, collection `warczone`; one WARC of 5,206,619,566 bytes + CDX 4.4 MB; not downloaded | Full crawl of the CMU AI Repository | **A third-party archival copy of the CMU ICOT mirror** (in case CMU goes away). Not verified that the icot/ subtree is inside (CDX not downloaded) |
| "Prime time freeware for AI: issue 1-1" (book that shipped with 2 CD-ROMs, 1994) | https://archive.org/details/primetimefreewar0000unse ; PDF https://archive.org/download/primetimefreewar0000unse/primetimefreewar0000unse.pdf | metadata-read: `access-restricted-item` absent, collection `internetarchivebooks` only, PDF 10,023,653 bytes not marked private; PDF URL resolved (HTTP 206 application/pdf for a ranged GET) | The printed book/index of the CD-ROM set; CMU pages say the ICOT directory was on this CD-ROM | **Full view book.** The CD-ROM images themselves were NOT found on archive.org |
| Wayback: `www.icot.or.jp` (old ICOT/AITEC host) | CDX `url=icot.or.jp&matchType=domain` | cdx-row-only: 20,000 rows returned (limit hit; rows are alphabetical and stop inside `/FTS/Ronbun/`; the `offset=20000` page failed with a Wayback error). Supplementary filtered queries succeeded | Top dirs by row count: `ARCHIVE/Museum` 5,683; `cgi-bin/readgif.sh?TRHOME=` 3,562; `FTS/REPORTS` 2,436; `AITEC/FGCS` 1,381; `AITEC/COLUMN` 993; `cgi-bin/downloadgif.sh?T=` 526 (525 with status 200; these are the TR/TM scan tar downloads); `AITEC/IFS` 244 | See next rows for what is and is not there |
| Wayback: IFS software tarballs under icot.or.jp | — | **Not found in CDX rows**: the filter `urlkey:.*\.(z|tgz|gz|ps|lzh|zip|tar|dvi)$` returned 548 rows = 526 `downloadgif.sh` TR/TM tars + 10 KLIC-contest `.tar.gz` + 10 `.ps` + `mgtp.ps.gz` (404) + `https://edition.icot.or.jp/sitemap.xml.gz` (2026 capture, status 301, unrelated). No `ifs/...*.tar.Z` and no `symbolic-proc/pim-psi` path in any row. A local keyword scan (psi, simpos, esp/cesp, kl0, firm, fep, pim, manual, micro) of ALL retrieved row files (icot.or.jp first 20,000 rows, `/ICOT/*`, `*/ifs*`, jipdec, ftp host), excluding TR/TM gif scripts, KLIC column pages and funding pages, finds only: machine-museum pages and photos (`/ARCHIVE/Museum/MACHINE/{pim-c,pim-i,pim-k,pim-m,pim-p,psi-I,psi-II}...`, `psi-II/chip-1..4.jpg`), PIM photos (`PIM-m.jpeg`, `PIM-p.jpeg`, `PIMinAnnex.jpeg`, `PIMwithMan.jpeg`, `HISTORY/activePIM.jpg`, `PIMintheroom.jpg`), CESP info pages (`IFS/INFO/cesp`, `cesp.j`, `cesp-E.html`, `cesp-J.html`), `FinalReport/appendix/pim.html`, `VIDEO/PSI/` (one row, 200), `VIDEO/ICOT94Dec/MPlayer/second-pim.wmv` (404) and `second-pim.wmx` (200), `94eEPIM.pdf` (200), `88ePIM-4.pdf` (status '-'), `eval-of-PIM.ps` (200). No SIMPOS, KL0, firmware, FEP or manual file names at all | — | The IFS distribution was FTP-only; Wayback did not capture it. `/ifs/` rows that exist are 404s (`/ifs/`, `/ifs/k`, `/ifs/kb`, `/ifs/kbm`, `/ifs/kbms`, all captured 2025-12-02 status 404; `http://ftp.icot.or.jp/ifs/contract-research/98/DH10-03/` 2013 status 404; `/ifs` 1999 status 404) |
| Wayback: IFS catalogue / abstract HTML pages | e.g. `http://www.icot.or.jp/AITEC/IFS/list/catalogue-E.html` (19980224050133, 200, 1,676 B), `.../catalogue-rest-E.html` (200, 2,986 B), `.../using-IFS-E.html`, `/AITEC/3/IFS/INFO/{cesp,cesp.j,klic,klic.j,pdss,pdss.j,character.e,character.j,COPYRIGHT.j.txt}` (1997-07, all 200), `/ARCHIVE/Museum/IFS/INFO/{cesp-E,character-E,klic-E}.html` (2002-12, 200), `/ICOT/IFS/usingIFS.html` (1997, 200), `/ICOT/IFS/IFS-News/...` (21 rows) | cdx-row-only | Catalogue, usage instructions, CESP conversion guide, newsletters. IFS abstract pages numbered 1-100 have at least one status-200 capture | Descriptions only, no payloads |
| Wayback: FGCS'94 PostScript papers on old host | `http://www.icot.or.jp/ICOT/Outline/FGCS-Proc/PS/{distributed,eval-of-PIM,general-report,general-report-J,helic2,helios,knowledge-base,knowledge-info,parallel-basic-soft,quixote}.ps` (all captured 1997-07-05/06, status 200, 69,876-177,680 bytes compressed length) | cdx-row-only | 10 PostScript files (that these are FGCS'94 papers is my inference from the directory name `FGCS-Proc` and matching names under `Museum/FGCS94/`), e.g. `eval-of-PIM.ps` (117,392), `parallel-basic-soft.ps` (89,743), `distributed.ps` (110,443) | Original PostScript (text-searchable) forms of FGCS'94 overview papers, including a PIM evaluation paper. Captures not fetched |
| Wayback: KLIC programming-contest sources | `http://www.icot.or.jp/AITEC/ACTIVITY/PROGRAM/FREE/GIJUTU/kl1httpd.tar.gz` (19970705075539, 200, 31,590), `.../FREE/KASAKU/qtickl.tar.gz` (39,360), `.../FREE/SAIYUUSHUU/krbs100c.tar.gz` (16,993), `.../FREE/YUUSHUU/submit2.tar.gz` (37,978), plus 6 small `PARALLEL/` and `SEQUENCE/` tarballs and 8 `.kl1` files (`multi_set.kl1`, `encode.kl1`, `naomalp1.kl1`) | cdx-row-only (all status 200) | KL1 programs from a KLIC programming contest (year 1996 is an inference from an unrelated CDX row `ftp.icot.or.jp/pub/contest/1996/SRC/...`; `kl1httpd` being an HTTP daemon is inferred from the name) | Extra real-world KL1 test programs; captures not fetched |
| Wayback: "Inside KLIC" and KLIC language/system HTML docs on old host | `http://www.icot.or.jp/AITEC/COLUMN/KLIC/{lang,inside,system}/...` (268 / 154 / 111 rows; `inside/index.html` 19990202160730 status 200 5,023 B; many `nodeNNN.html` are 200, many others 404) | cdx-row-only | HTML renderings of KLIC documentation ("inside" = implementation internals) | Partial capture (numerous nodes 404) |
| Wayback: `ftp.icot.or.jp` | CDX `url=ftp.icot.or.jp*` | cdx-row-only: 1,180 rows, all `http://ftp.icot.or.jp:80/...` web pages (885 `ARCHIVE/Museum/Minutes`, 52 `FinalReport`, 34 `SOFTWARE`, FTS reports, seminar PDFs). The `ftp://` scheme query returned the same 1,180 http rows | No FTP payloads | Nothing software-related |
| Wayback: JIPDEC-hosted copy of the ICOT archive | CDX `url=jipdec.or.jp/archives/icot*` | cdx-row-only: 356 rows, incl. `ARCHIVE/Museum/MACHINE/` (62 rows: `pim-m-E.html` 20140226131452 200 949 B, `pim-p-E.html`, `pim-c-E.html`, `pim-i-E.html`, `pim-k-E.html`, `pim-spec-E.html` 2,484 B, `psi-I-E.html`, `psi-II-E.html`, `chi-I/II-E.html`, `delta-E.html`, and photo GIF/JPGs incl. `psi-II/small-psi-II-processor-board.gif`, `small-chip-1..4.gif`). Live URL `https://www.jipdec.or.jp/archives/icot/ARCHIVE/Museum/MACHINE/pim-m-E.html` is **dead (404)** | Machine museum pages + photos | Third historical host of the same archive; photos of PIM/m and PSI-II boards (also on the live mirrors, presumably) |
| Wayback: `klic.org` | see Item 7 | — | — | — |

#### (b) Exact quotes (grep -F confirmed in raw bytes)
- CMU `areas/icot/0.html`: "Note that most of the programs are written for the PSI machines," / "and very few have been ported to Unix-based emulators." (the sentence spans a line break in the file; second half grep-confirmed, first half read in the same file) and "Prime Time Freeware for AI, Issue 1-1".
- CMU `index.txt`: "psdpim	[03] Pseudo PIM (PIM emulator on PSI)" and "manuals/	Manuals and textbooks of the languages and OS" (tabs as in the file).
- CMU `rep_info/cdrom.html` (https://www.cs.cmu.edu/afs/cs.cmu.edu/project/ai-repository/ai/html/rep_info/cdrom.html, opened-and-read): "two ISO-9660 CD-ROMs bound into a 224-page book".

#### (c) Queries tried (verbatim)
Archive.org advancedsearch (`https://archive.org/advancedsearch.php?q=<Q>&fl[]=identifier&fl[]=title&fl[]=collection&fl[]=year&fl[]=mediatype&rows=50..100&output=json`):
- `title:("Fifth Generation Computer Systems")` -> numFound 8
- `title:("fifth generation computer")` -> numFound 11
- `title:("Logic Programming") AND title:(proceedings) AND title:(international conference)` -> numFound 19
- `title:("Implementations of Distributed Prolog")` -> numFound 0
- `title:("Logic Programming") AND title:("North American")` -> numFound 3
- `title:("Programming of Future Generation Computers")` -> numFound 0
- `PIMOS` -> numFound 2 (both irrelevant CIA reading-room full-text hits)
- `ICOT` -> numFound 75 (only 60 rows fetched; noise-dominated; redone field-restricted below)
- `title:(fifth generation computer systems) AND year:[1984 TO 1989]` -> HTTP 200, numFound 4
- `title:(fifth generation) AND mediatype:(texts OR software) AND year:[1980 TO 1995]` -> HTTP 200, numFound 34
- `title:(logic programming) AND year:[1987 TO 1990] AND mediatype:texts` -> HTTP 200, numFound 76
- `title:(distributed prolog)` -> HTTP 200, numFound 2
- `creator:(Kacsuk)` -> HTTP 200, numFound 4
- `title:(future generation computers)` -> HTTP 200, numFound 1
- `creator:(Fuchi)` -> HTTP 200, numFound 8
- `(title:(ICOT) OR subject:(ICOT) OR creator:(ICOT)) AND mediatype:(texts OR software)` -> HTTP 200, numFound 14
- `title:(PIMOS) OR subject:(PIMOS)` -> HTTP 200, numFound 0
- `title:("parallel inference machine") OR subject:("parallel inference machine")` -> HTTP 200, numFound 0
- `title:(KL1) OR subject:(KL1)` -> HTTP 200, numFound 22
- `title:(SIMPOS) OR subject:(SIMPOS)` -> HTTP 200, numFound 1
- `title:("Multi-PSI") OR subject:("Multi-PSI")` -> HTTP 200, numFound 0
- `title:("PSI machine") OR subject:("PSI machine") OR title:("personal sequential inference")` -> HTTP 200, numFound 0
- `title:("New Generation Computing")` -> HTTP 200, numFound 7
- `creator:("Institute for New Generation Computer Technology") OR publisher:("Institute for New Generation Computer Technology") OR title:("Institute for New Generation Computer Technology")` -> HTTP 200, numFound 0
- `title:("ICOT Journal") OR title:("新世代コンピュータ") OR title:("第五世代コンピュータ")` -> HTTP 200, numFound 0
- `title:(KLIC) AND mediatype:(texts OR software)` -> HTTP 200, numFound 61
- `title:("ESP language") OR title:("extended self-contained prolog") OR subject:("ESP (Computer program language)")` -> HTTP 200, numFound 1
- `title:(guarded horn clauses) OR title:(concurrent prolog) OR title:(parlog)` -> HTTP 200, numFound 10
- `title:(logic programming sixth international conference)` -> HTTP 200, numFound 0
- `title:(logic programming) AND creator:(Levi OR Martelli)` -> HTTP 200, numFound 0
- `title:(fifth generation computer systems 1984) OR title:(fifth generation computer systems 1988)` -> HTTP 200, numFound 2
- `title:(international conference fifth generation computer systems) AND mediatype:texts` -> HTTP 200, numFound 1
- `collection:(pub_new-generation-computing)` -> HTTP 200, numFound 0
- `title:(Programming of future generation computers) OR title:(Peogramming)` -> HTTP 200, numFound 1
- `title:(distributed prolog) OR creator:(Wise, Michael J)` -> HTTP 200, numFound 35
- `title:(ICOT) AND mediatype:software` -> HTTP 200, numFound 0
- `title:(fifth generation) AND mediatype:software` -> HTTP 200, numFound 3
- `subject:("Fifth generation computers") AND mediatype:texts` -> HTTP 200, numFound 9
- `title:(parallel logic programming) OR title:(parallel inference)` -> HTTP 200, numFound 25
- `creator:(Ueda, Kazunori) OR creator:(Chikayama) OR creator:(Taki, Kazuo)` -> HTTP 200, numFound 13
- `title:(fifth generation) AND (title:(Japan) OR title:(Japanese)) AND mediatype:texts` -> HTTP 200, numFound 4
- `title:(prolog) AND title:(machine) AND mediatype:texts` -> HTTP 200, numFound 2
- `collection:"pub_new-generation-computing"` -> HTTP 200, numFound 0
- `identifier:sim_new-generation-computing*` -> HTTP 200, numFound 0
- `title:("new generation computer systems")` -> HTTP 200, numFound 1
- (archive.org advancedsearch) `title:("Prime Time Freeware")` -> HTTP 200, numFound 2
- (archive.org advancedsearch) `title:(freeware for AI) OR title:("AI Repository") OR title:("CMU Artificial Intelligence Repository")` -> HTTP 200, numFound 5
- (archive.org advancedsearch) `title:(PTF AI) OR title:("Prime Time") AND mediatype:software` -> HTTP 200, numFound 38

Open Library (`https://openlibrary.org/search.json?q=<Q>&fields=key,title,first_publish_year,ia,ebook_access,publisher&limit=20`):
- `title:"Fifth generation computer systems" 1988` -> numFound 6 (all no_ebook)
- `title:"Fifth generation computer systems" 1984` -> numFound 3 (all no_ebook)
- `title:"Implementations of distributed Prolog"` -> numFound 1 (no_ebook)
- `title:"Programming of future generation computers"` -> numFound 3 (all no_ebook)
- `title:"Logic programming" "sixth international conference"` -> numFound 1 (no_ebook)
- `ICOT "Institute for New Generation Computer Technology"` -> numFound 1 (no_ebook)

Wayback CDX (`https://web.archive.org/cdx/search/cdx?<params>`):
- `url=icot.or.jp&matchType=domain&collapse=urlkey&fl=original,timestamp,statuscode,mimetype,length&limit=20000` -> HTTP 200, 20000 rows
- `url=klic.org&matchType=domain&collapse=urlkey&fl=original,timestamp,statuscode,mimetype,length&limit=20000` -> HTTP 200, 1928 rows
- `url=jipdec.or.jp/archives/icot*&collapse=urlkey&fl=original,timestamp,statuscode,mimetype,length&limit=20000` -> HTTP 200, 356 rows
- `url=www.jipdec.or.jp/icot*&collapse=urlkey&fl=original,timestamp,statuscode,mimetype,length&limit=20000` -> HTTP 503, 14 rows
- `url=ftp.icot.or.jp*&collapse=urlkey&fl=original,timestamp,statuscode,mimetype,length&limit=20000` -> HTTP 200, 1180 rows
- `url=icot.or.jp&matchType=domain&collapse=urlkey&fl=original,timestamp,statuscode,mimetype,length&limit=20000&offset=20000` -> HTTP 503, 14 rows
  - NOTE: the two rows above logged as 'HTTP 200/503, 14 rows' for jipdec.or.jp/icot* and offset=20000 were Wayback 'Temporarily Offline' HTML error bodies, not data; retried below.
- `url=icot.or.jp&matchType=domain&collapse=urlkey&fl=original,timestamp,statuscode,mimetype,length&filter=urlkey:.*/ifs.*&limit=5000` -> HTTP 200, 1108 rows
- `url=icot.or.jp&matchType=domain&collapse=urlkey&fl=original,timestamp,statuscode,mimetype,length&filter=urlkey:.*%5C.(z%7Ctgz%7Cgz%7Cps%7Clzh%7Czip%7Ctar%7Cdvi)$&limit=5000` -> HTTP 200, 548 rows
- `url=icot.or.jp&matchType=domain&collapse=urlkey&fl=original,timestamp,statuscode,mimetype,length&filter=!urlkey:.*/(archive/museum%7Ccgi-bin%7Cfts%7Caitec)/.*&limit=5000` -> HTTP 504, 7 rows
- `url=www.icot.or.jp/ICOT/*&collapse=urlkey&fl=original,timestamp,statuscode,mimetype,length&limit=8000` -> HTTP 200, 835 rows
- `url=ftp://ftp.icot.or.jp/*&collapse=urlkey&fl=original,timestamp,statuscode,mimetype,length&limit=3000` -> HTTP 200, 1180 rows
- (CDX) `url=ueda.info.waseda.ac.jp/software*&matchType=prefix&collapse=urlkey&fl=original,timestamp,statuscode,mimetype,length&limit=300` -> HTTP 200, 0 rows
- (CDX) `url=ueda.info.waseda.ac.jp&matchType=domain&collapse=urlkey&fl=original,timestamp,statuscode,mimetype,length&filter=urlkey:.*klic.*&limit=500` -> HTTP 503, 14 rows (ERROR BODY)
- (CDX retry) same ueda.info.waseda.ac.jp klic filter query -> HTTP 000, 14 rows
- (CDX, not in raw log) `url=klic.org/files*&matchType=prefix&fl=original,timestamp,statuscode,mimetype,length,digest&limit=200` -> HTTP 200, 0 bytes (empty; the klic.org domain query already had the rows)
- (CDX, not in raw log) `url=www.klic.org/software/klic/*&collapse=urlkey&fl=original,timestamp,statuscode,mimetype,length&limit=1500` -> HTTP 200, 75,301 bytes
- (CDX, not in raw log) `url=icot.or.jp&matchType=domain&collapse=urlkey&fl=original,timestamp,statuscode,mimetype,length&filter=urlkey:.*(psi%7Csimpos%7Ckl0%7Cfep%7Cfirm%7Cmanual%7Cpim).*&limit=3000` -> HTTP 504 (error body)

WebSearch:
- `"pimosobj.tar.Z" OR "psdpim.tar.Z" OR "pimosman.tar.Z" OR "vpim.tar.Z"` -> CMU listings only (engine reported treating OR as plain keywords)
- `"Prime Time Freeware for AI" CD-ROM iso image download` -> CMU cdrom.html; no ISO

#### (d) Not found
- Not found: FGCS'88 or FGCS'84 proceedings as an archive.org book scan (they exist only as per-paper PDFs in the ICOT archive mirrors).
- Not found: ICLP'89 proceedings on archive.org.
- Not found: "Implementations of Distributed Prolog" (Kacsuk & Wise) on archive.org.
- Not found: "Programming of Future Generation Computers" volume I on archive.org (vol. II is there, borrowable, under a mis-spelt title).
- Not found: any PIMOS manual, ICOT Journal, or scanned New Generation Computing issue on archive.org.
- Not found: any archive.org item (texts or software) with title/subject SIMPOS, Multi-PSI, "parallel inference machine", "PSI machine", KL1 (22 hits, all unrelated), ESP language (1 unrelated hit), KLIC (61 hits, all Kodak batteries / radio / unrelated), or ICOT software.
- Not found: any Wayback capture of IFS tarballs or other software/firmware payloads, or a `symbolic-proc/pim-psi` path, on icot.or.jp, ftp.icot.or.jp or jipdec.or.jp. The rows DO contain the names cesp (info pages), PIM-*/pim-* and psi-* (museum pages, photos, one video directory); they contain no SIMPOS / KL0 / firmware / FEP / manual names. Caveat: a server-side keyword-filtered CDX query over the whole domain (to cover rows beyond the 20,000-row cut) failed with HTTP 504, so paths alphabetically after `/FTS/Ronbun/` are covered only by the `/ICOT/*` and `*/ifs*` queries.
- Not found: ISO images of the "Prime Time Freeware for AI" CD-ROMs.
- Not checked: textfiles.com / cd.textfiles.com (no query run there); rows of icot.or.jp alphabetically after `/FTS/Ronbun/` other than `/ICOT/*` (835 rows, retrieved separately) and `*/ifs*` (1,108 rows) — the paged CDX request failed (Wayback 503/504).

---

#### Method note of the agent for items 4, 5

Research date: 2026-11-20. All fetches used `curl -A "Mozilla/5.0"`; nothing was executed from downloads.

Status vocabulary:
- **opened-and-read** = body fetched and read (method stated).
- **resolved-not-read** = HTTP 200 with content-type/bytes, body not read.
- **cited-only** = seen only in a search result or in another document's reference list.
- **dead** = HTTP error code given.

Quote vocabulary:
- **[raw]** = string confirmed by `grep` on the raw downloaded bytes (HTML, UTF-8 unless stated).
- **[pdf-text]** = string confirmed in the PDF's own text layer via `pdftotext`. For the scanned journals this layer is OCR.
- **[image]** = read by me from a 100-dpi rendering of the PDF page (`pdftoppm`). The OCR layer is garbled there, so these are NOT byte-verified; treat as my transcription.

---

### Item 4 — Museum holdings

#### 4(a) Table

| item | exact URL | status (+evidence) | what it contains | why it matters |
|---|---|---|---|---|
| IPSJ Computer Museum, FGCS project page (JA) | https://museum.ipsj.or.jp/computer/other/0002.html | opened-and-read (200, text/html, 12379 B; tags stripped, read in full; quote grepped) | One-paragraph history of the project, then a sentence saying PIM/p and PIM/m are preserved at the National Museum of Nature and Science | The only page found that names a holder of PIM/m hardware |
| same, EN | https://museum.ipsj.or.jp/en/computer/other/0002.html | opened-and-read (200, 11862 B; quote grepped) | English version of the same text | Same claim in English ("National Science Museum in Tokyo") |
| IPSJ Computer Museum, MELCOM PSI page (JA) | https://museum.ipsj.or.jp/computer/other/0009.html | opened-and-read (200, 12932 B) | Technical description of PSI and PSI II (40-bit word, 8-bit tag, 200 ns cycle, SIMPOS, ESP, KL0 by microprogram) | Says nothing about any surviving machine or holder |
| same, EN | https://museum.ipsj.or.jp/en/computer/other/0009.html | opened-and-read (200, 11778 B) | English version | Same: no preservation statement |
| IPSJ "other computers" index (JA) | https://museum.ipsj.or.jp/computer/other/index.html | opened-and-read (200; all links listed) | 21 entries; only three relevant: 0002 (FGCS), 0009 (MELCOM PSI), 0016 (Univ. of Tokyo PIE) | Shows there are NO separate IPSJ pages for PSI-II, PSI-III, Multi-PSI, or any individual PIM model |
| IPSJ model-name index (JA) | https://museum.ipsj.or.jp/computer/list.html | opened-and-read (200, 871644 B; keyword-scanned) | Whole-site machine index | Only hits: "MELCOM PSI", "PrologマシンPEK", "並列推論エンジンPIE", the FGCS entry (plus unrelated "ML803PSII/ML905PSII") |
| IPSJ PIE page (JA) | https://museum.ipsj.or.jp/computer/other/0016.html | opened-and-read (200, 11537 B; quote grepped) | Univ. of Tokyo Parallel Inference Engine | Not an ICOT machine, but a second inference machine stated to be at the same museum (one cabinet) |
| IPSJ Information Processing Technology Heritage list, index + year pages 2008-2019, 2023-2025, both indexes (by device, by maker) | https://museum.ipsj.or.jp/heritage/index.html , .../heritage/2008.html ... 2019.html (2011 is .../heritage/2011/2011.html), 2023.html, 2024.html, 2025.html, sakuin-kiki.html, sakuin-sezosha.html | opened-and-read (all 200; keyword-scanned; sakuin-kiki has 145 links and does contain e.g. "MELCOM 1101", so the scan works) | Certified heritage items | **No PSI / PIM / ICOT / 推論 / 第五世代 entry** in the heritage list |
| heritage year pages 2020, 2021, 2022, 2026 | https://museum.ipsj.or.jp/heritage/2020.html (and 2021, 2022, 2026) | dead (404 each) | — | Those years are not linked from the index either; the two sakuin indexes cover the list |
| IPSJ satellite museum: JAIST collection (JA) | https://museum.ipsj.or.jp/satellite/hokurikusentandai.html | opened-and-read (200, 10895 B; quotes grepped) | JAIST Collection of Symbolic Processing Computers (ELIS LISP machines etc.) | **Names "PSI (ICOT)" as a preserved artifact, and says related manuals and materials are also preserved** |
| same, EN | https://museum.ipsj.or.jp/en/satellite/JAIST.html | opened-and-read (200, 10396 B; quotes grepped) | English version | Same |
| JA path guessed from EN | https://museum.ipsj.or.jp/satellite/JAIST.html | dead (404) | — | JA page is at hokurikusentandai.html |
| IPSJ satellite museum pages, the other 12 (KCG Kyoto, Fujitsu DNA館, Hitachi Omika, NTT, Tohoku Univ., TUS, Kyoto Sangyo Univ., ISM, Kobe Univ. RIEB, 計算科学振興財団 FOCUS, 科学技術継承財団, TUAT) | https://museum.ipsj.or.jp/satellite/{kyoto_kcg,DNA,o-mika,NTT_gijyutu,tohokudai,MathSci_Experience_Center,kyoto-sangyo-univ,ism,focus,focus2,gijyutsu,noukoudai}.html | opened-and-read (all 200; keyword-scanned only) | Satellite museum descriptions | No PSI/PIM/ICOT/推論 mention on any of them |
| KCG Computer Museum (Kyoto) own site | https://www.kcg.ac.jp/museum/computer/ + 36 linked category pages | opened-and-read (200; keyword-scanned only) | Collection lists by maker | No PSI / 推論 / MELCOM / ICOT / 三菱 hit (control: the same pages contain 富士通/FACOM/TOSBAC 283 times) |
| IPSJ "when the explanations were written" page | https://museum.ipsj.or.jp/computer/j8ro9c00000000qe.html | opened-and-read (200, 1698 B — title only, no body text) | Empty stub | The "現在" (today) in the PIM sentence therefore cannot be dated |
| "Fifth Generation Museum" link given by IPSJ | http://www.jipdec.or.jp/archives/icot/ARCHIVE/HomePage-J.html and .../HomePage-E.html | dead (404 both, after https upgrade) | — | The link IPSJ gives is broken |
| ICOT archive mirror at AIST (surfaced in search) | https://www.airc.aist.go.jp/aitec-icot/ICOT/Museum/MACHINE/pim-spec-E.html | resolved-not-read (200, text/html, 8098 B) | "Outline of 5 modules of PIM" per search title | Live mirror of the ICOT museum material |
| ICOT archive mirror at Waseda (search result) | https://www.ueda.info.waseda.ac.jp/AITEC_ICOT_ARCHIVES/ICOT/Museum/FGCS92Demo/E/doc011.html | cited-only | — | Second mirror |
| Kahaku industrial-technology database | https://sts.kahaku.go.jp/sts/result.php?word=… | opened-and-read (200; 15 keyword queries, results parsed) | Survey records of artifacts held by companies/institutions | **No record for PSI, PIM (ICOT), 推論マシン, 第五世代, ICOT, Prolog, 論理型, AIワークステーション** (see not-found) |
| Kahaku integrated search | https://sts.kahaku.go.jp/integrated_search/?word=…&mode=and | opened-and-read (200; 5 queries) | Combined search | 推論 → 1 unrelated hit; 第五世代 → 0; 推論マシン → 0; ICOT → 1 hit that is a substring match on "apricot" (BIOS ROMs, 三菱電機インフォメーションテクノロジー, 鎌倉市) |
| Kahaku HITNET | https://sts.kahaku.go.jp/hitnet/index.php | resolved-not-read (200, 5024 B) | Museum-network search front page | Not queried |
| Kahaku systematization-survey index | https://sts.kahaku.go.jp/research/taikei/index.html and I.html … X.html | opened-and-read (200; all ten category pages keyword-scanned) | List of survey reports with PDF links | No report title/abstract mentions 推論 / 第五世代 / 第5世代 |
| Kahaku survey report, Yamada 2001 (1st/2nd-generation computers) | https://sts.kahaku.go.jp/albums/abm.php?d=3277&f=abm00011040.pdf&n=003.pdf | opened-and-read (200, application/pdf, 4275884 B, `%PDF-`; pdftotext + grep) | Computer development history and preservation status | No hit for 推論/第五世代/ICOT/PSI/PIM |
| Kahaku survey report, Yamada 2002 (3rd/3.5-gen and supercomputers) | https://sts.kahaku.go.jp/albums/abm.php?d=3277&f=abm00011039.pdf&n=006.pdf | opened-and-read (200, application/pdf, 4976745 B, `%PDF-`; pdftotext + grep) | same series | No hit |
| Old URLs for those two reports (as returned by search engines) | https://sts.kahaku.go.jp/diversity/document/system/pdf/003.pdf and .../006.pdf | dead as PDFs (200 but text/html, 29346 B = the report-list page; soft redirect) | — | Search-engine links are stale; use the abm.php URLs above |
| Computer History Museum catalog | https://www.computerhistory.org/collections/catalog/search-catalog/… | **search could not be executed** (pages return 200 but every keyword URL form returned `"criteria":[]` and the default unfiltered listing) | — | No conclusion about CHM holdings can be drawn from this run |

#### 4(b) Exact quotes

1. IPSJ FGCS page, JA **[raw]**: 「現在，PIM/pおよびPIM/mは国立科学博物館で保存されている．また，下記のWebで「第五世代博物館」が公開されている．」
   Translation: "At present, PIM/p and PIM/m are preserved at the National Museum of Nature and Science. In addition, the 'Fifth Generation Museum' is published on the Web below."
2. IPSJ FGCS page, EN **[raw]**: "Today, the PIM/p and PIM/m are preserved at the National Science Museum in Tokyo."
   - Caveats: single source; undated; says "preserved", not "exhibited"; does not say Ueno vs. Tsukuba storage, nor how many cabinets, nor whether documentation came with them.
3. IPSJ JAIST page, JA **[raw]**: 「さらにICOTのPSIなども保存されている」 / 「その他：CELIS，TAO/SILENT，PSI（ICOT），お茶の水5号」 / 「これらのほかに関連するマニュアルや資料などが保存されている」
   Translation: "…and in addition ICOT's PSI etc. are also preserved" / "Others: CELIS, TAO/SILENT, PSI (ICOT), Ochanomizu No.5" / "Besides these, related manuals and materials are also preserved."
   Location on the page: 〒923-1292 石川県能美市旭台1-1 北陸先端科学技術大学院大学 情報科学系研究棟1F.
4. IPSJ JAIST page, EN **[raw]**: "It also includes ICOT PSI and other symbolic processing computers." / "Others: CELIS, TAO/SILENT, PSI (ICOT), Ochanomizu No.5"
   - Caveat: the page does not say which PSI model (PSI, PSI-II, PSI-III), nor whether the "related manuals" include PSI manuals (the sentence follows a list dominated by ELIS items).
5. IPSJ PIE page, JA **[raw]**: 「1筐体が国立科学博物館に保存されている」 — "One cabinet is preserved at the National Museum of Nature and Science." (Univ. of Tokyo PIE, not an ICOT machine.)
6. IPSJ MELCOM PSI page, JA **[raw]**: 「を1986年に三菱電機が製品化したAIワークステーションである」 / 「1987年には，性能が3倍以上でデスクサイドにおけるPSI IIを発表した」 — "…an AI workstation that Mitsubishi Electric commercialised in 1986" / "In 1987 the desk-side PSI II, with more than three times the performance, was announced." No holdings statement on this page.

#### 4(c) Queries tried (verbatim)

WebSearch:
- `IPSJ コンピュータ博物館 PSI 逐次型推論マシン 第五世代コンピュータ`
- `国立科学博物館 並列推論マシン PIM/m PIM/p 保存 展示 第五世代コンピュータ`
- `産業技術史資料データベース 推論マシン PSI 三菱電機 sts.kahaku.go.jp`
- `Computer History Museum catalog ICOT "Fifth Generation" PSI machine artifact`
- (allowed_domains computerhistory.org) `ICOT "Fifth Generation Computer Systems" catalog`
- (allowed_domains computerhistory.org) `"Institute for New Generation Computer Technology" catalog`
- `PSI-II OR "Multi-PSI" OR "PIM/m" 推論マシン 実機 保存 展示 大学 博物館 ICOT`
- `"PIM/m" OR "PIM/p" parallel inference machine preserved museum "National Museum of Nature and Science" Tsukuba storage`

Site-internal searches (direct GET):
- Kahaku DB `https://sts.kahaku.go.jp/sts/result.php?word=<w>` with w = `推論` (1 hit, a 1991 flatbed scanner with fuzzy inference) | `PSI` (2 hits, aircraft landing-gear struts) | `第五世代` (0) | `PIM` (2 hits: IBM PS/55 note; "PIM" 1993 at 富士電機デバイステクノロジー 松本事業所, a power-semiconductor module — unrelated, record read) | `ICOT` (0) | `推論マシン` (0) | `新世代コンピュータ` (0) | `Prolog` (0) | `人工知能` (5, robots etc.) | `並列` (46; first page read, none relevant) | `MELCOM` (16; first page read: MELCOM 81/83/84/88/80/1101 only) | `ワークステーション` (51; first page read, none relevant) | `論理型` (0) | `AIワークステーション` (0) | `Lisp` (1: パーソナルLISPマシン ELM-1 at AIST Tsukuba)
- Kahaku integrated search `https://sts.kahaku.go.jp/integrated_search/?word=<w>&mode=and` with w = `推論` | `第五世代` | `推論マシン` | `ICOT` | `三菱電機`
- CHM catalog URL forms tried, all ignoring the keyword: `/collections/search/?s=ICOT` ; `/collections/catalog/search-catalog/search/ICOT` ; `.../search/keyword:ICOT` ; `.../search/q:ICOT` ; `/collections/catalog/search-catalog?s=ICOT` ; `.../search/s:ICOT` ; `.../search/keyword:icot` ; `.../search/keyword:ICOT/` ; `.../search/keyword:fifth%20generation` ; `.../search/collection:physical-objects/keyword:prolog`. (Filter URLs such as `.../search/collection:physical-objects` do work, so the keyword is applied client-side through an API I could not identify in the JS bundle.)
- Keyword scan applied to every IPSJ / KCG / Kahaku page fetched: `PSI|PIM|推論|第五世代|ICOT|第5世代|Prolog|Fifth Generation|Inference|KL1|論理型|新世代`

#### 4(d) Not found

- Not found: any IPSJ Computer Museum page for PSI-II (as its own page), PSI-III, PSI-UX, Multi-PSI, or for PIM/p, PIM/m, PIM/c, PIM/i, PIM/k individually. Only the FGCS page (0002) and the MELCOM PSI page (0009) exist.
- Not found: any PSI / PIM / FGCS entry in the IPSJ 情報処理技術遺産 (Information Processing Technology Heritage) list, 2008-2025.
- Not found: any statement, anywhere, of a surviving PIM/c, PIM/i, PIM/k, Multi-PSI, PSI-II, PSI-III or PSI-UX machine.
- Not found: any National Museum of Nature and Science page of its own confirming the PIM/p and PIM/m holding; the Kahaku industrial-technology database has no record for them (that database lists surveyed items mostly held by companies, so absence there does not contradict IPSJ).
- Not found: any surviving-documentation statement for PIM/m (manuals, microcode listings, firmware media) at any museum.
- Not found: Mitsubishi, Fujitsu or Oki corporate-collection page listing a PSI or PIM. (Fujitsu DNA館 satellite page has no mention; no Mitsubishi or Oki corporate museum page was located.)
- Not determined: Computer History Museum holdings (search could not be run; the two domain-restricted web searches returned only a 1983 "Fifth Generation Computer Systems" bulletin in the Stoyan LISP finding aid and the software-preservation Prolog page — both cited-only).

---

### Item 5 — Vendor technical journals

#### 5(a) Table

| item | exact URL | status (+evidence) | what it contains | why it matters |
|---|---|---|---|---|
| **Mitsubishi Denki Giho — official archive index** | https://www.mitsubishielectric.co.jp/giho/ | opened-and-read (200, 147433 B; links listed) | Back-number section with decade pages 1920s–2020s, plus "バックナンバー詳細目次（1925～1959年）" PDF | **Public full-issue PDF archive exists, back to January 1925** (earliest link .../giho/pdf/1925/2501.pdf, HEAD 200 application/pdf 3610412 B) |
| decade pages | https://www.mitsubishielectric.co.jp/giho/1980s/ and .../1920s/ | opened-and-read (200, 357522 B and 211005 B; PDF hrefs extracted) | 1980s page links 120 issue PDFs; 1920s page links e.g. .../pdf/1929/2912.pdf | URL pattern is `https://www.giho.mitsubishielectric.co.jp/giho/pdf/YYYY/YYMM.pdf` |
| every issue Jan 1984 – Dec 1994 | https://www.giho.mitsubishielectric.co.jp/giho/pdf/{1984..1994}/{YY}{01..12}.pdf | resolved-not-read (HEAD: all 132 return 200 application/pdf, 4.4–50.8 MB each) | Whole-issue scans with an OCR text layer | Complete run for the PSI/PIM period is online |
| Vol.60 No.9 (1986-09), 知識情報処理特集 | https://www.giho.mitsubishielectric.co.jp/giho/pdf/1986/8609.pdf | opened-and-read (GET 200, `%PDF-`, 6823168 B, 77 pp.; article first page read as image; text layer grepped) | 「三菱AIワークステーション《MELCOM PSI》」 pp.598–602 (hardware, firmware, software overview); the vol.60 annual index (OCR) also lists, in the same special issue, 「第5世代コンピュータプロジェクトの狙い」 at p.593, and the issue's OCR footers show an ESP-language article ("Extended Self Contained Prolog") around pp.603–605 — neither was image-checked | Vendor description of the first PSI |
| Vol.61 No.7 (1987-07), ワークステーション特集 | https://www.giho.mitsubishielectric.co.jp/giho/pdf/1987/8707.pdf | opened-and-read (GET 200, `%PDF-`, 7061596 B; text layer only) | 「知識処理におけるAIワークステーションの活用」 p.527– (uses of MELCOM PSI) | Application-level, not hardware |
| Vol.62 No.2 (1988-02) | https://www.giho.mitsubishielectric.co.jp/giho/pdf/1988/8802.pdf | opened-and-read (GET 200, `%PDF-`, 6337691 B; first page read as image; text layer grepped) | 「LSI化高性能AIワークステーション《MELCOM PSI II》」 pp.163–168; covers hardware, firmware and compiler; states the microprogram lives in a 16K-word WCS (image) and, per the OCR text layer of p.167, that KL0 is compiled to WAM-based machine instructions | **Vendor's own firmware/WCS description of PSI II; the article says PSI II was productised using the element-processor results of the Multi-PSI Ver 2 work** |
| Vol.62 No.12 (1988-12) | https://www.giho.mitsubishielectric.co.jp/giho/pdf/1988/8812.pdf | opened-and-read (GET 200, `%PDF-`, 7197063 B, 111 pp.; first page read as image; text layer grepped) | 「(財)新世代コンピュータ技術開発機構向け マルチPSIシステム」 pp.1100–1105; hardware spec table (boards, gate arrays, network), maintenance path and diagnostics | **Multi-PSI hardware as built by the vendor** |
| Vol.63 No.7 (1989-07) | https://www.giho.mitsubishielectric.co.jp/giho/pdf/1989/8907.pdf | opened-and-read (GET 200, `%PDF-`, 5639713 B; first page read as image) | 「AIワークステーション《MELCOM PSI II》」 pp.549–553 (new 430 KLIPS model, speed-up techniques, tools) | Later PSI II model |
| Vol.65 No.6 (1991-06) | https://www.giho.mitsubishielectric.co.jp/giho/pdf/1991/9106.pdf | opened-and-read (GET 200, `%PDF-`, 7340014 B; two first pages read as image) | 「三菱AIワークステーション《MELCOM PSI/UXシリーズ》の概要と特長」 pp.594–601 and 「…のハードウェアシステム」 pp.602–607 (inference VLSI + MC68030 general part; models 350/400, type numbers B2150/B2151) | PSI/UX is presented as the successor to MELCOM PSI II; hardware and firmware. The name "PSI-III" does not appear in what I read |
| Vol.65 No.11 (1991-11) | https://www.giho.mitsubishielectric.co.jp/giho/pdf/1991/9111.pdf | opened-and-read (GET 200, `%PDF-`, 6974649 B; first page read as image; text layer grepped) | 「並列推論マシン(PIM/m)用VLSI」 pp.1158–1162; PU/CU/NU chips, 5-stage pipeline, 32K-word WCS holding the microprogram | **Direct vendor article on the PIM/m processor element and where its microprogram lived** |
| Vol.66 No.6 (1992-06) | https://www.giho.mitsubishielectric.co.jp/giho/pdf/1992/9206.pdf | opened-and-read (GET 200, `%PDF-`, 5036948 B, 89 pp.; first page read as image; text layer grepped) | 「並列推論マシンPIMのアーキテクチャ」 pp.682–686; PIM/m architecture and the KL1 implementation | **Direct vendor article on PIM/m architecture** |
| December (annual-index) issues 1984–1994 | .../pdf/1984/8412.pdf, 1985/8512.pdf, 1986/8612.pdf, 1987/8712.pdf, 1988/8812.pdf, 1989/8912.pdf, 1990/9012.pdf, 1991/9112.pdf, 1992/9212.pdf, 1993/9312.pdf, 1994/9412.pdf | opened-and-read (GET 200, all `%PDF-`, 5.7–12.1 MB; OCR text of the 総目次 grepped) | Each carries that volume's 総目次 (annual index) | Used to find the articles above; no relevant entry seen for vols 58 (1984), 59 (1985), 67 (1993), 68 (1994) |
| Mitsubishi Electric ADVANCE (English journal), 1987 workstation article | — | cited-only (appears in the reference list of the 1991-06 PSI/UX article, text layer) | — | Possible English-language counterpart; not located |
| **Hitachi Hyoron — archive** | https://www.hitachihyoron.com/jp/index_year.html | opened-and-read (200, 25993 B; year links 1950–present listed) | Year index | **Public archive exists, 1950s onward**; `/jp/archive/index.html` and `/jp/search_by/year.html` are meta-refresh stubs to it |
| Hitachi per-issue index pages 1984–1994 | https://www.hitachihyoron.com/jp/archive/{1980s,1990s}/YYYY/{01..12}.html | opened-and-read (132 pages, all fetched, Shift_JIS decoded, about 1948 PDF links in total, link titles grepped) | Article titles with per-article PDFs | **No PIM/c article; no ICOT/FGCS hardware article at all** (see not-found) |
| Hitachi sample PDF | https://www.hitachihyoron.com/jp/pdf/1987/03/1987_03_02.pdf | resolved-not-read (GET 200, application/pdf, 4594343 B, `%PDF-`) | 「知識処理言語"VOS3/HI-UX PROLOG"の高速化方式とプログラミング環境」 | Proves 1980s article PDFs open; not PIM-related |
| **Fujitsu — official FSTJ archive** | https://www.fujitsu.com/global/about/resources/publications/fstj/archives/ | dead for this purpose (301 → https://global.fujitsu/en-global/about, which answers 429 "Vercel Security Checkpoint" to curl) | — | Old archive URL no longer leads to an archive; a search summary says the official online archive only ever covered 1997 onward (not verified by me) |
| Fujitsu 雑誌FUJITSU official back numbers | https://www.fujitsu.com/jp/about/resources/publications/magazine/backnumber/ | dead for this purpose (redirects to https://global.fujitsu/ja-JP/about/activities, 429 checkpoint) | — | Could not establish whether any 1984–1994 Japanese-journal archive exists |
| **FSTJ scans on bitsavers** | https://bitsavers.org/pdf/fujitsu/Fujitsu_Scientific_and_Technical_Journal/ | opened-and-read (200, directory listing; 17 PDFs) | V24 N1–4 (1988), V25 N4 (1989-12), V26 N1–4 (1990–91), V27 N1, N2, N4 (1991), V28 N1–3 (1992), V29 N1–2 (1993) | Third-party partial run for the period; 1984–87, most of 1989, V27 N3, V28 N4 and 1994 are absent |
| the 17 bitsavers PDFs | https://bitsavers.org/pdf/fujitsu/Fujitsu_Scientific_and_Technical_Journal/Fujitsu_Scientific_and_Technical_Journal_V{24_N01_198803 … 29_N02_199306}.pdf | opened-and-read (all GET 200, `%PDF-`, 24.0–96.6 MB; pdftotext, grepped) | Full issues with OCR | Two FGCS-related articles, neither on PIM/p hardware (below) |
| FSTJ Vol.29 No.2 (Summer 1993) | .../Fujitsu_Scientific_and_Technical_Journal_V29_N02_199306.pdf | opened-and-read (34639306 B; contents + article opening read from text layer) | "ParaGraph: A Graphical Tuning Tool for Multiprocessor Systems" (Aikawa, Kamiko, Chikayama), starts p.119; a KL1/PIMOS load-visualisation tool for PIM, done under ICOT contract | Software tool for the PIMs; not a PIM/p hardware article |
| FSTJ Vol.26 No.1 (April 1990) | .../Fujitsu_Scientific_and_Technical_Journal_V26_N01_199004.pdf | opened-and-read (51876210 B; text layer) | "Overview of an Experimental Reflective Programming System: ExReps" (Tanaka, Ohta, Matono), starts p.86; GHC-based, FGCS-funded; cites the PSI-II hardware paper | Language research only |
| FSTJ partial mirror list, Univ. of Arizona | https://www2.cs.arizona.edu/projects/japan/fujitsu.html | cited-only (search result) | Said to list vols 29–33 | Not opened |
| **Toshiba Review — archive** | https://www.global.toshiba/jp/technology/corporate/review/backnumber.html | opened-and-read (200, 91667 B; year links extracted) | Back numbers 1995–2026 only | **No online archive for 1984–1994** |
| Toshiba pre-1995 year pages | https://www.global.toshiba/jp/technology/corporate/review/1994.html (also 1993, 1990) | dead (404 each) | — | Confirms the 1995 floor |
| **Oki Technical Review — archive** | https://www.oki.com/global/ja/technologies/otr/archives/ | opened-and-read (200, 260071 B, EUC-JP; issue links extracted) | Issues from 1995 (No.166) onward | **No online archive for 1984–1994** (the period when the journal was 沖電気研究開発) |
| Oki guessed back-number URL | https://www.oki.com/jp/otr/backnumber.html | dead (404) | — | — |

#### 5(b) Mitsubishi Denki Giho articles found (volume / issue / pages / title / authors)

Volume, issue and page numbers are from the running footers on the article pages (read in the page images for the first page of each article; end pages from the footers in the text layer). Titles and author names are **[image]** unless marked.

| Vol. No. (date) | pages | title (original) | English translation | authors | PDF opens? |
|---|---|---|---|---|---|
| 60(9), 1986-09 | 598–602 | 三菱AIワークステーション《MELCOM PSI》 | Mitsubishi AI Workstation "MELCOM PSI" | 鷹取東朋・益田嘉直・川上孝仁・池田守宏・中島 浩 | yes, 6823168 B |
| 61(7), 1987-07 | 527– (end not checked) | 知識処理におけるAIワークステーションの活用 (OCR of annual index only, not image-checked) | Using AI workstations in knowledge processing | 秋田興一郎・太細孝・荻野敬迪・丸山冬樹 (OCR) | yes, 7061596 B |
| 62(2), 1988-02 | 163–168 | LSI化高性能AIワークステーション《MELCOM PSI II》 | LSI-based high-performance AI workstation "MELCOM PSI II" | 京 敬人・田辺隆司・立野裕和・中島 浩・近藤誠一 | yes, 6337691 B |
| 62(12), 1988-12 | 1100–1105 | (財)新世代コンピュータ技術開発機構向け マルチPSIシステム | The Multi-PSI System for the Institute for New Generation Computer Technology | 益田嘉直・中川智明・岩山洋明・武田保孝・中島 浩・瀧 和男 | yes, 7197063 B |
| 63(7), 1989-07 | 549–553 | AIワークステーション《MELCOM PSI II》 | AI Workstation "MELCOM PSI II" | 池田守宏・梁田和彦・吉永俊郎 | yes, 5639713 B |
| 65(6), 1991-06 | 594–601 | 三菱AIワークステーション《MELCOM PSI/UXシリーズ》の概要と特長 | Overview and features of the Mitsubishi AI Workstation "MELCOM PSI/UX Series" | 湯浅維央・上田尚純・松本 明 | yes, 7340014 B |
| 65(6), 1991-06 | 602–607 | 三菱AIワークステーション《MELCOM PSI/UXシリーズ》のハードウェアシステム | Hardware system of the Mitsubishi AI Workstation "MELCOM PSI/UX Series" | 益田嘉直・田辺隆司・池田守宏・深沢 雄・岩山洋明・中島 浩 | yes (same PDF) |
| 65(11), 1991-11 | 1158–1162 | 並列推論マシン(PIM/m)用VLSI | VLSI for the Parallel Inference Machine (PIM/m) | 古谷清広・安田憲一・町田浩久・安藤秀樹・武田保孝・中島 浩 | yes, 6974649 B |
| 66(6), 1992-06 | 682–686 | 並列推論マシンPIMのアーキテクチャ | Architecture of the Parallel Inference Machine PIM | 中島克人・益田嘉直・中島 浩・近藤誠一・武田保孝・村澤 靖・小森隆三 | yes, 5036948 B |

Byte-confirmed title strings **[pdf-text]** (contents page, p.2 of each PDF): 「並列推論マシン(PIM/m)用 VLSI」 (9111.pdf); 「並列推論マシン PIM のアーキテクチャ」 (9206.pdf); 「マルチPS1システム」 (8812.pdf — note the OCR writes "PS1" for "PSI"; search these PDFs for `PS1` as well as `PSI`).

Passages bearing on the lost firmware, **[image]** (my transcription from the page image; the OCR layer does not reproduce them exactly, so these are NOT byte-verified quotations. Byte-present tokens on those pages: `32K` and `WCS` on 9111.pdf p.112, where the OCR reads "WCS (wntable co0廿olst0羚ge)"; `16K語の容` and `WCS` on 8802.pdf p.67):
- 1991-11, p.1158: 「PUチップは，5ステージのパイプラインを持ったマイクロプロセッサであり，32KワードのWCS (Writable Control Storage) に格納されたマイクロプログラムによって論理型言語を実行する。」 — "The PU chip is a microprocessor with a 5-stage pipeline, and executes the logic language by a microprogram stored in a 32K-word WCS (Writable Control Storage)."
- 1991-11, p.1158: 「PIM/mの要素プロセッサで実行されるプログラムは，KL1と呼ばれる並列論理型言語である。一方，FEPでは逐次処理型の論理型言語であるKL0やESPが実行される。」 — "Programs run on the PIM/m processor elements are in the parallel logic language KL1; the FEP runs the sequential logic languages KL0 and ESP."
- 1988-02, p.163: 「これらの機能は，16K語の容量を持つWCS (Writable Control Store) に格納されたマイクロプログラムにより，効率的に実行される。」 — "These functions are executed efficiently by a microprogram stored in a WCS (Writable Control Store) of 16K-word capacity." (PSI II)
- 1988-12, p.1100 (text): 「このシステムの要素プロセッサ1台分は，PSIのCPUをLSI化により改良小型化したCPU部，80Mバイトメモリ及び接続ネットワーク制御部から成り」 — "One element processor of this system consists of a CPU part that is the PSI CPU improved and miniaturised by LSI, 80 MB of memory, and a connection-network control part."
- 1988-12, p.1100 (spec table): CPU 「プリント基板3枚（改良小型化PSIのCPU部）／8Kゲート CMOS G.A. 8種9石」; 接続ネットワーク制御部 「プリント基板1枚／20Kゲート CMOS G.A. 1種2石」; 主記憶 「プリント基板4枚（最大80Mバイト）」; 「最大64台」 — Multi-PSI: CPU on 3 boards (the improved, miniaturised PSI CPU), 8K-gate CMOS gate arrays, 8 types / 9 chips; network controller 1 board, 20K-gate gate array; main memory 4 boards (max 80 MB); up to 64 processors.
- 1992-06, p.682: 「PIM/mの最大構成は256PEである。」 and figure caption 「PIM/mの筐体外観(32PE内蔵)（最大構成は8筐体256PE）」 — "The maximum PIM/m configuration is 256 PE" / "PIM/m cabinet (32 PE inside); maximum configuration 8 cabinets, 256 PE."

#### 5(c) Queries tried (verbatim)

WebSearch:
- `三菱電機技報 バックナンバー 1986 PSI 逐次型推論マシン AIワークステーション MELCOM PSI`
- `FUJITSU Scientific & Technical Journal 1992 "PIM/p" parallel inference machine article back issues archive`
- `東芝レビュー バックナンバー 1990年 1992年 アーカイブ PDF 並列推論マシン PIM/k`
- `沖電気研究開発 並列推論マシン PIM/i OR 逐次型推論マシン PSI 沖テクニカルレビュー バックナンバー 1980年代`
- `"Fujitsu Scientific & Technical Journal" archives back issues 1980s 1990s PDF online where`
- `雑誌FUJITSU バックナンバー 1990年 1992年 並列推論マシン PIM/p 富士通`

WebFetch (one call; returned only a redirect notice, nothing quoted from it): `https://www.fujitsu.com/global/about/resources/publications/fstj/archives/` with prompt "List the earliest volume/year of FUJITSU Scientific & Technical Journal back issues available on this page, and the URL pattern of the per-issue pages. If this is a bot checkpoint or error page, say so."

Direct index greps:
- Mitsubishi: HEAD sweep of `https://www.giho.mitsubishielectric.co.jp/giho/pdf/YYYY/YYMM.pdf`, 1984–1994 × 01–12.
- Mitsubishi: OCR text of the eleven December (annual-index) issues grepped for `推論|PSI|PIM|第五世代|第5世代|論理型|Prolog|KL1|AIワークステーション|ＰＳＩ|知識情報`, then again within the index region for `PS[1I]|P51|推論|ワークステーシ|第5世代|第五世代|人工知能|Prolog|論理型|知識` and `AI|A1|A17|人工知能|エキスパート|知識`.
- Hitachi: all 132 per-issue pages 1984–1994, article-link titles grepped (cp932) for `推論|PSI|PIM|第五世代|第5世代|第５世代|論理型|Prolog|PROLOG|KL1|ＰＩＭ|ＰＳＩ|新世代|並列.{0,6}マシン|知識処理マシン|AIワークステーション|人工知能|ICOT`.
- Fujitsu: text of the 17 bitsavers issues grepped (case-insensitive) for `parallel inference|PIM/p|fifth generation|KL1|ICOT|Prolog|inference machine`.

#### 5(d) Not found

- Not found (Mitsubishi): any article on PSI/PIM in the annual indexes of vol.58 (1984), 59 (1985), 67 (1993), 68 (1994). Positive control: the index regions of those four issues do contain ordinary words (システム 31/44/76/634 lines, 計算機 or コンピュータ 1/14/17/24 lines), so the index OCR is not blank. Limits of this check: it rests on OCR of the annual indexes, and the OCR is poor (e.g. "AI ワークステーション" comes out as "A17ークステーション", "PSI" as "PS1"); the eleven January "技術の進歩" review issues and the non-December issues other than those listed were not opened. A relevant short item could have been missed.
- Not found (Mitsubishi): a separate article titled with "逐次型推論マシン", "論理型言語処理マイクロプロセッサ" or "PSI-III". The name "PSI-III" was not found in any article read; the 1991-06 articles describe MELCOM PSI/UX as the successor to MELCOM PSI II.
- Not found (Hitachi): any Hitachi Hyoron article 1984–1994 on PIM/c, on ICOT, or on the Fifth Generation project hardware. Titles that matched the keywords were all unrelated: 「知識処理のための推論ソフトウェア」 (1985-12), 「知識処理言語"VOS3/HI-UX PROLOG"の高速化方式とプログラミング環境」 and 「ES/KERNELでの知識表現方法と高速推論方式」 (1987-03), 「PROLOGを用いたリスク管理エキスパートシステム」 (1988-11), two fuzzy-inference articles (1989-08, 1989-11), and two "新世代" product articles (1992-09, 1993-04).
- Not found (Fujitsu): any FSTJ article on PIM/p hardware in the 17 issues available on bitsavers (1988–1993, incomplete run). Not checked: FSTJ 1984–87, 1989 N1–3, V27 N3, V28 N4, 1994 (no copy located); 雑誌FUJITSU (no archive located).
- Not found (Toshiba): no online Toshiba Review archive before 1995, so PIM/k coverage could not be checked at all.
- Not found (Oki): no online Oki review archive before 1995 (No.166), so PIM/i and Oki-PSI coverage could not be checked at all.

---

##### Items 4-5: exists or is cited but could not be opened


- Computer History Museum online catalog keyword search (computerhistory.org/collections/catalog/search-catalog): site is up, but a keyword query could not be executed without a browser; holdings for ICOT / PSI / Fifth Generation remain unchecked.
- http://www.jipdec.or.jp/archives/icot/ARCHIVE/HomePage-J.html and HomePage-E.html — the "Fifth Generation Museum" link printed on the IPSJ page: 404.
- https://sts.kahaku.go.jp/diversity/document/system/pdf/003.pdf and 006.pdf — stale; now serve the report-list HTML. (The reports themselves were opened at the abm.php URLs.)
- https://sts.kahaku.go.jp/hitnet/index.php — resolves (200) but was not queried.
- Fujitsu official journal archives (FSTJ and 雑誌FUJITSU): old URLs redirect to a generic page behind a bot checkpoint (429); existence of any 1984–1994 archive not established.
- https://www2.cs.arizona.edu/projects/japan/fujitsu.html — search result only, not opened.
- Toshiba Review 1984–1994 and Oki 沖電気研究開発 1984–1994: journals exist in print, but no online back issues were found; not opened.
- Mitsubishi Electric ADVANCE (English-language journal), a 1987 AI-workstation article cited in the 1991-06 PSI/UX article: not located.
- IPSJ "解説文の作成時期" page (https://museum.ipsj.or.jp/computer/j8ro9c00000000qe.html): opens but is an empty stub, so the date of the "PIM/p and PIM/m are preserved" sentence is unknown.
- Search results never opened: https://www.tus.ac.jp/info/setubi/museum/db/museum-yama/si/mainframe.html ; https://sts.kahaku.go.jp/material/2024pdf/leg_technography2024.pdf ; https://jipdec.or.jp/archives/publications/J0005062 ; https://ithistory.org/node/22506 ; https://atmarkit.itmedia.co.jp/news/200903/02/museum.html .

---

### Item 6
Scope: Japanese-language papers on PIM/m, Multi-PSI/V2, PSI-II/III, PIM/i/k/c/p, KL1/KL1-B, VPIM, PIMOS in the IPSJ digital library, CiNii Research, J-STAGE, IEICE.

**How to read the status column (applies to every row)**

- All bibliographic data in the IPSJ tables (Japanese title, English title, authors, venue, pages, date, PDF URL) is copied by script from the raw JSON returned by the IPSJ repository search API (`https://ipsj.ixsq.nii.ac.jp/api/records/?q=...&size=100&page=N`, WEKO3, HTTP 200 `application/json`), not from a summarising model and not from memory. English titles are the repository's own (typos such as "Processer", "Evalutation" are theirs); they are not my translations. Where a record has no English title this is stated.
- Landing URLs `https://ipsj.ixsq.nii.ac.jp/records/<id>` are constructed from the record id; each was then fetched with a plain GET and the HTTP code and byte count are shown beside it. The HTML was not read (status for landing pages: resolved-not-read); the metadata comes from the JSON API.
- The **why it matters** column states its own basis: text after an opened-and-read status comes from the page images I read; "(from repository abstract, paper not read)" paraphrases the Japanese abstract in the API record; "(from title only, unverified)" is no more than a reading of the title.
- **opened-and-read** = full GET of the PDF (HTTP 200, `%PDF` magic, byte count), saved, and the stated page images were actually read (the PDFs are image-only scans: `pdftotext` returns no text for every one, so reading means looking at the rendered page).
- **resolved-not-read (full GET ...)** = full GET, `%PDF` magic, byte count, page count from `pdfinfo`, file kept; content not read.
- **resolved-not-read: range GET** = GET with `Range: bytes=0-1023` returned HTTP 206, the first four bytes are `%PDF`, and `Content-Range` gives the total size. This shows a real PDF is served without login; the whole file was not downloaded and nothing was read.
- The repository redirects PDF GETs to an object store with a short-lived signed URL; use the `ipsj.ixsq.nii.ac.jp/record/<id>/files/<name>.pdf` URL given here, not the redirect target.

**Result in one paragraph.** The IPSJ repository holds 130 on-topic records from 1984-1996 after filtering; 130 of them were confirmed to serve a real PDF without login (39 fully downloaded, the rest by range GET), 0 could not be confirmed, 0 not yet checked. Every one of these records carries `accessrole=open_date` in its file metadata (a few unrelated, recent records in the raw hits carry `open_login`). Convention volumes 34, 35, 36 (1987 - spring 1988) and 43 (autumn 1991) returned no hits for any topic or author query in either the IPSJ API or CiNii, while 33, 37-42 and 44+ returned many. A CiNii query restricted to the venue name gave 24 records for 1987 (citation stubs, none from the IPSJ repository) against 1127 for 1988 and 1139 for 1991; the first 200 of 1988 are all volume 37 and the first 200 of 1991 all volume 42. So volumes 34 and 35 are observed to be essentially absent from CiNii; for 36 and 43 the evidence is only the absence of hits. Convention papers from 1987 to spring 1988 and from autumn 1991 could therefore not be retrieved.

#### Notes on the named targets
- IPSJ Trans. vol 33 no 3 (1992) pp 278-287 "並列推論マシンPIM/iプロセッサの設計" is by **佐藤正俊 (Sato Masatoshi)**, 武田浩一, 大原輝彦 (Oki), as printed on the paper's first page. The repository lists both 佐藤正俊 and 佐藤正樹 on PIM/i convention records with the same co-authors; whether those are two people or a metadata variant was not checked. Search under both spellings.
- 91-ARC-89-27 is "シミュレータによるVPIM処理系の評価 - データの輸出入処理に関して -" by 高木常好 (ICOT) and 仲瀬明彦 (Toshiba), 1991-07-19, pp 201-208; the page header reads "計算機アーキテクチャ 89-27". 91-ARC-89-28, next to it, is the PIM/p KL1 implementation paper.
- The slit-check paper is 89-ARC-77-3 (1989-07-13), by 中川貴之, 後藤厚宏, 近山隆 (ICOT). Its abstract is about inter-processor communication on tightly coupled multiprocessors; PIM/m is not named on the page I read.
- Author-name search needs a space between family and given name (`中島 克人`); the unspaced form returns almost nothing, and `creator=`/`title=` parameters return a non-JSON error page.

#### A1. Flagged: the most implementation-relevant papers (all openly downloadable; rows repeated in the topical tables are omitted there)

| paper (JP title / EN title as given in the repository record) | authors | bibliographic data | landing URL | PDF URL | status (+evidence) | why it matters |
|---|---|---|---|---|---|---|
| PIM/m要素プロセッサのアーキテクチャ / Architecture of PIM/m Processor Element | 中島浩, 武田保孝, 中島克人 | 全国大会講演論文集,  第40回,  ハードウェア, p. 1183-1184,  1990-03-14 | https://ipsj.ixsq.nii.ac.jp/records/118810 (GET HTTP 200, 62993 bytes; HTML not read) | https://ipsj.ixsq.nii.ac.jp/record/118810/files/KJ00001338430.pdf | **opened-and-read**: full GET HTTP 200, %PDF magic, 168190 bytes, 2 pp, image-only scan; read page image pp.1-2 (whole paper). Open: yes. File `ipsj_118810_KJ00001338430.pdf` | **PIM/m element processor**: microprogrammed CISC that directly emulates KL1-B (and KL0/ESP for the FEP role); three VLSI chips PU/CU/NCU; 5-stage pipeline D/A/R/S/E with RAM decode table and "nano-code"; WCS 32Kw x 64b; I-cache 1Kw, D-cache 4Kw, 2x32-entry TLBs, trail buffer (TRB); S stage does tag dispatch (modifies microprogram entry address), dereference and MRB test; 60 ns cycle vs 200 ns Multi-PSI/V2 and 155 ns PSI-II; append = 20/13 microsteps (KL1/KL0), 833/1282 KLIPS vs 36/15 steps, 139/430 KLIPS on Multi-PSI/V2(PSI-II). |
| PIM/mのメンテナンス系アーキテクチャとCSP / Maintenance Architecture and CSP on PIM/m | 高橋勝己, 武田保孝, 村沢靖, 小森隆三, 杉野栄二 | 全国大会講演論文集,  第45回,  ハードウェア, p. 167-168,  1992-09-28 | https://ipsj.ixsq.nii.ac.jp/records/122850 (GET HTTP 200, 70025 bytes; HTML not read) | https://ipsj.ixsq.nii.ac.jp/record/122850/files/KJ00001344570.pdf | **opened-and-read**: full GET HTTP 200, %PDF magic, 197980 bytes, 2 pp, image-only scan; read page image pp.1-2 (whole paper). Open: yes. File `ipsj_122850_KJ00001344570.pdf` | **PIM/m maintenance architecture and CSP**: 32 PE (8x4) per cabinet up to 8 cabinets / 256 PE (16x16); FEP = PSI-II over SCSI, one SCSI per 8 PE; CSP reaches every PE over an 8-bit single-master maintenance bus; CSP-visible registers are CSIFR plus MIR, DR, MDR1 (everything else is reached by loading a microinstruction into MIR and single-stepping); per-PE **Refuge Stack** saves the registers clobbered by that procedure so CSP can broadcast to all PEs at once; three execution levels named (KL1, KL1-B instruction, microinstruction) each with step/break/trace; boot about 3 min for 256 PE vs about 10 min on the 64-PE Multi-PSI. Cites a JSPP'90 version of the element-processor paper and a JSPP'89 paper on Multi-PSI debug/maintenance functions. |
| マルチPSI要素プロセッサPSI-IIのアーキテクチャ / Architecture of Multi-PSI Element Processor (PSI-II) | 中島克人, 瀧和男, 中島浩, 京敬人, 江原輝文, 山本明, 横田実 | 全国大会講演論文集,  第33回,  アーキテクチャおよびハードウェア, p. 149-150,  1986-10-01 | https://ipsj.ixsq.nii.ac.jp/records/113880 (GET HTTP 200, 75334 bytes; HTML not read) | https://ipsj.ixsq.nii.ac.jp/record/113880/files/KJ00001330686.pdf | **opened-and-read**: full GET HTTP 200, %PDF magic, 173256 bytes, 2 pp, image-only scan; read page image pp.1-2 (whole paper). Open: yes. File `ipsj_113880_KJ00001330686.pdf` | **PSI-II architecture (1986)**: C-MOS gate arrays (8000 gates), CPU on 3 boards, 200 ns cycle like PSI; word = 8-bit tag (2 GC bits + 6-bit data type) + 32-bit data; 64-word two-port register file; MAR/IAR with auto-increment, IFR/IBR/IR 3-stage instruction registers; counters LC, GR, SR; **microinstruction shortened from 64 to 53 bits, 16K-word WCS**, 1K trace memory, dispatch memory widened from 12 to 32 patterns; 10-bit opcode (1024 instructions) reserved so a KL1 instruction set can coexist with the Prolog one; eop-time interrupt test, firmware-raised events; plan: KL0 firmware by March 1987, Multi-PSI hardware and KL1 firmware by end of 1987. |
| マルチPSI/V2におけるコード形式について / Code representation of Multi-PSI/V2 | 宮崎芳枝, 中越靖行, 堂前慶之, 稲村雄, 木村康則, 中島克人 | 全国大会講演論文集,  第38回,  ソフトウェア, p. 1007-1008,  1989-03-15 | https://ipsj.ixsq.nii.ac.jp/records/116581 (GET HTTP 200, 72868 bytes; HTML not read) | https://ipsj.ixsq.nii.ac.jp/record/116581/files/KJ00001333324.pdf | **opened-and-read**: full GET HTTP 200, %PDF magic, 142667 bytes, 2 pp, image-only scan; read page image pp.1-2 (whole paper). Open: yes. File `ipsj_116581_KJ00001333324.pdf` | **Multi-PSI/V2 code/module format**: module = KL1 data object with module size, GC size, module name, GC area (absolute pointers: external-call predicate descriptors, structured-constant pointers) and code area (instructions, module-relative addresses, atomic data); 4-word external predicate descriptor (cache field, module field, predicate-name field, module-name field); predicate entry hash table at head of code area; `put_structured_constant Ai, Lab`. |
| マイクロコード・チェッカ「マイクロリント」の開発 / Micro Lint for Checking Micro Program Code | 宮内信仁, 市吉伸行 | 全国大会講演論文集,  第40回,  ソフトウェア工学, p. 1005-1006,  1990-03-14 | https://ipsj.ixsq.nii.ac.jp/records/118717 (GET HTTP 200, 59797 bytes; HTML not read) | https://ipsj.ixsq.nii.ac.jp/record/118717/files/KJ00001338334.pdf | **opened-and-read**: full GET HTTP 200, %PDF magic, 176023 bytes, 2 pp, image-only scan; read page image p.1 of 2. Open: yes. File `ipsj_118717_KJ00001338334.pdf` | **Multi-PSI/V2 microcode practice**: says the KL1 system is written in microcode, the 16Kword WCS of the PSI-II CPU is tight, shows the microprogram source syntax (one step = comma-separated field operations ending in a period, e.g. `mar := reg, read(mar, mdr), if (zero) goto jump_label.`), and describes a static register-usage checker for microroutines. |
| KL1抽象命令セットの改良について / Improvement of KL1 Abstract Instruction Set | 木村康則, 後藤厚宏, 中島克人, 近山隆 | 全国大会講演論文集,  第38回,  ソフトウェア, p. 1003-1004,  1989-03-15 | https://ipsj.ixsq.nii.ac.jp/records/116579 (GET HTTP 200, 65925 bytes; HTML not read) | https://ipsj.ixsq.nii.ac.jp/record/116579/files/KJ00001333322.pdf | **opened-and-read**: full GET HTTP 200, %PDF magic, 179214 bytes, 2 pp, image-only scan; read page image p.1 of 2. Open: yes. File `ipsj_116579_KJ00001333322.pdf` | **KL1 abstract instruction set (KL1-B) revision**: clause-indexing instructions (wait, is_XXX, test_XXX, wait_XXX, jump_on_non_XXX, check_XXX), suspension branch vs try_me_else failure branch, abolition of the structure (S) register, new MRB-management and MRB-GC instructions; shows compiled append. |
| 並列論理型言語KL1の抽象機械語の改良 / Optimal Design of the Abstract KL1 Instruction Set | 平野喜芳, 後藤厚宏 | 情報処理学会研究報告計算機アーキテクチャ（ARC）,  1990,  27(1989-ARC-081), p. 1-8,  1990-03-23 | https://ipsj.ixsq.nii.ac.jp/records/24664 (GET HTTP 200, 62576 bytes; HTML not read) | https://ipsj.ixsq.nii.ac.jp/record/24664/files/IPSJ-ARC89081003.pdf | **opened-and-read**: full GET HTTP 200, %PDF magic, 1089696 bytes, 8 pp, image-only scan; read page image p.1 (title, abstract). Open: yes. File `ipsj_24664_IPSJ-ARC89081003.pdf` | New KL1-B for PIM: memory-based goal execution (arguments stay in the goal record until needed), registers all working, cheaper context switch. |
| 分散環境におけるユニフィケーションの実現 / A Distributed Implementation of Unification | 六沢一昭, 市吉伸行, 近山隆, 中島浩 | 全国大会講演論文集,  第37回,  プログラミング言語とその処理系, p. 689-690,  1988-09-12 | https://ipsj.ixsq.nii.ac.jp/records/115342 (GET HTTP 200, 66358 bytes; HTML not read) | https://ipsj.ixsq.nii.ac.jp/record/115342/files/KJ00003117883.pdf | **opened-and-read**: full GET HTTP 200, %PDF magic, 165109 bytes, 2 pp, image-only scan; read page image p.1 of 2. Open: yes. File `ipsj_115342_KJ00003117883.pdf` | **Distributed unification** for the Multi-PSI v2 KL1 system: external reference pointers (EXREF), indirect export, %unify messages carrying exref()/value() terms, loop avoidance and termination guarantee. |
| 分散環境における構造体管理 / Structure Management for Distributed Processing Systems | 六沢一昭, 近山隆, 中島浩, 瀧和男, 市吉伸行, 中島克人, 稲村雄 | 全国大会講演論文集,  第39回,  ソフトウェア, p. 1277-1278,  1989-10-16 | https://ipsj.ixsq.nii.ac.jp/records/117689 (GET HTTP 200, 75826 bytes; HTML not read) | https://ipsj.ixsq.nii.ac.jp/record/117689/files/KJ00001335962.pdf | **opened-and-read**: full GET HTTP 200, %PDF magic, 162726 bytes, 2 pp, image-only scan; read page image p.1 of 2. Open: yes. File `ipsj_117689_KJ00001335962.pdf` | **Structure management across PEs** on the Multi-PSI/V2 KL1 system: external reference pointers, read requests ("import"), unique ids so the same structure imported twice or via loops is recognised, avoiding duplicate allocation and transfer. |
| Multi-PSI/V2における一括GC及びメモリ消費特性の評価 / Evaluation of GC and Memory Consumption on the Multi-PSI/V2 | 宮内信仁, 川田易治, 中島克人 | 全国大会講演論文集,  第39回,  ソフトウェア, p. 1285-1286,  1989-10-16 | https://ipsj.ixsq.nii.ac.jp/records/117693 (GET HTTP 200, 62525 bytes; HTML not read) | https://ipsj.ixsq.nii.ac.jp/record/117693/files/KJ00001335966.pdf | **opened-and-read**: full GET HTTP 200, %PDF magic, 154568 bytes, 2 pp, image-only scan; read page image p.1 of 2. Open: yes. File `ipsj_117693_KJ00001335966.pdf` | Multi-PSI/V2 memory management: MRB incremental GC inside a PE, copying (two-semispace) stop GC when free lists run out, WEC weighted reference counting for inter-PE garbage; MRB-based optimisations of the copying GC. |
| プロセッサ間ソフトウェア割り込み処理を高速化するスリットチェック機構 / Slit - Check Features to Speed Up Interprocessor Software Interruption Handling | 中川貴之, 後藤厚宏, 近山隆 | 情報処理学会研究報告計算機アーキテクチャ（ARC）,  1989,  60(1989-ARC-077), p. 17-24,  1989-07-13 | https://ipsj.ixsq.nii.ac.jp/records/24712 (GET HTTP 200, 66787 bytes; HTML not read) | https://ipsj.ixsq.nii.ac.jp/record/24712/files/IPSJ-ARC89077003.pdf | **opened-and-read**: full GET HTTP 200, %PDF magic, 1045081 bytes, 8 pp, image-only scan; read page image p.1 (title, abstract). Open: yes. File `ipsj_24712_IPSJ-ARC89077003.pdf` | **Slit check** (スリットチェック) defined: a software interrupt polled at coarse grain; proposes hardware support (extension of coherent cache) to speed inter-processor software interrupts on tightly coupled multiprocessors; used for automatic load balancing and priority control. ICOT (Nakagawa, Goto, Chikayama). This is ARC 77-3, 1989-07-13. |
| シミュレータによるVPIM処理系の評価　－データの輸出入処理に関して－ / Evaluation of VPIM : A Distributed KL1 Implementation -Focusing on Inter - cluster Operations- | 高木常好, 仲瀬明彦 | 情報処理学会研究報告計算機アーキテクチャ（ARC）,  1991,  64(1991-ARC-089), p. 201-208,  1991-07-19 | https://ipsj.ixsq.nii.ac.jp/records/24531 (GET HTTP 200, 62806 bytes; HTML not read) | https://ipsj.ixsq.nii.ac.jp/record/24531/files/IPSJ-ARC91089027.pdf | **opened-and-read**: full GET HTTP 200, %PDF magic, 1122627 bytes, 8 pp, image-only scan; read page image p.1 (title, abstract). Open: yes. File `ipsj_24531_IPSJ-ARC91089027.pdf` | **The named target 91-ARC-89-27**: VPIM (distributed KL1 implementation for PIM) evaluated on a simulator for inter-cluster export/import processing; incremental reclamation cut export/import table area to 1/10; unification optimisation removed up to 50% of unify messages. |
| 並列推論マシンにおけるKL1の実行制御方式　－分散・ゴール管理の課題と対策－ / Distributed KL1 Goal Management for the Parallel Inference Machine | 川合英夫, 仲瀬明彦, 今井明, 後藤厚宏, 六沢一昭 | 情報処理学会研究報告計算機アーキテクチャ（ARC）,  1990,  29(1990-ARC-082), p. 1-8,  1990-04-20 | https://ipsj.ixsq.nii.ac.jp/records/24656 (GET HTTP 200, 72562 bytes; HTML not read) | https://ipsj.ixsq.nii.ac.jp/record/24656/files/IPSJ-ARC90082002.pdf | **opened-and-read**: full GET HTTP 200, %PDF magic, 1356549 bytes, 8 pp, image-only scan; read page image p.1 (title, abstract). Open: yes. File `ipsj_24656_IPSJ-ARC90082002.pdf` | Distributing the meta-control (goal management) functions of KL1 for PIM: shared-memory cluster level and message-overtaking network level. |
| KL1における永久中断ゴールの検出と報告 / Detection and Report of Perpetual Suspension in KL1 | 大西諭, 稲村雄 | 情報処理学会研究報告計算機アーキテクチャ（ARC）,  1990,  29(1990-ARC-082), p. 1-8,  1990-04-20 | https://ipsj.ixsq.nii.ac.jp/records/24655 (GET HTTP 200, 62757 bytes; HTML not read) | https://ipsj.ixsq.nii.ac.jp/record/24655/files/IPSJ-ARC90082001.pdf | **opened-and-read**: full GET HTTP 200, %PDF magic, 1098953 bytes, 8 pp, image-only scan; read page image pp.1-2 of 8. Open: yes. File `ipsj_24655_IPSJ-ARC90082001.pdf` | **Perpetual suspension** detection at stop-GC time, implemented on the Multi-PSI: finds perpetually suspended goals, reports only the maximal goals of their causality graph, and raises it as an exception through the shoen report stream. |
| 並列論理言語型KL1の多重参照管理によるガーベジコレクション / Incremental Garbage Collection by Multiple Reference Management of Data Objects in KL1 | 木村康則, 近山隆 | 情報処理学会論文誌,  31,  2, p. 316-328,  1990-02-15,ISSN,1882-7764 | https://ipsj.ixsq.nii.ac.jp/records/15095 (GET HTTP 200, 63040 bytes; HTML not read) | https://ipsj.ixsq.nii.ac.jp/record/15095/files/IPSJ-JNL3102016.pdf | resolved-not-read (full GET HTTP 200, %PDF magic, 1037146 bytes, 13 pp, image-only scan; saved, content not read). Open: yes. File `ipsj_15095_IPSJ-JNL3102016.pdf` | (from repository abstract, paper not read) MRB journal paper: a one-bit reference-count flag kept in the pointer, maintained by compiler and runtime, so cells are reclaimed as soon as the single reference is consumed; evaluation included. |
| PIM/mフロントエンド・プロセッサの速度性能評価 / performance Evaluation of PIM/m fornt End Processor | 佐伯稔, 中島浩, 立野裕和, 池田守宏, 田嶋隆二 | 全国大会講演論文集,  第42回,  ハードウェア, p. 25-26,  1991-02-25 | https://ipsj.ixsq.nii.ac.jp/records/120642 (GET HTTP 200, 69204 bytes; HTML not read) | https://ipsj.ixsq.nii.ac.jp/record/120642/files/KJ00001341482.pdf | **opened-and-read**: full GET HTTP 200, %PDF magic, 171764 bytes, 2 pp, image-only scan; read page image p.1 of 2. Open: yes. File `ipsj_120642_KJ00001341482.pdf` | PIM/m front-end processor = PSI-III, built from the same PU/CU VLSI chips; horizontal microprogram executing WAM-based machine code; tag architecture, 5-stage pipeline with auto-dereference, trail buffer; benchmark table vs PSI-II (machine cycle PSI-III 65 ns, PSI-II 155 ns). |
| 並列推論マシンPIMにおけるメタ機能「荘園」の実装 / Implementation of meta functions "Shoen" for PIM | 山本礼己, 川合英夫 | 情報処理学会研究報告システムソフトウェアとオペレーティング・システム（OS）,  1991,  63(1991-OS-051), p. 81-88,  1991-07-18 | https://ipsj.ixsq.nii.ac.jp/records/26377 (GET HTTP 200, 63072 bytes; HTML not read) | https://ipsj.ixsq.nii.ac.jp/record/26377/files/IPSJ-OS91051011.pdf | **opened-and-read**: full GET HTTP 200, %PDF magic, 1232499 bytes, 8 pp, image-only scan; read page image pp.1-2 of 8. Open: yes. File `ipsj_26377_IPSJ-OS91051011.pdf` | **Shoen (荘園)** = the meta-level facility by which KL1 programs control execution of KL1 programs (used inside PIMOS; built-in `shoen:exec` is shown); already implemented on the loosely coupled Multi-PSI, being re-designed for PIM (shared-memory clusters joined by a network): lock contention, overtaking of shoen operations inside a cluster, message overtaking between clusters; cost measured on the PIM simulator. |
| 並列論理型言語KL1分散処理系の外部参照管理方式の評価 / Evaluation of Remote Reference Management in a Distributed KL1 Implementation | 六沢一昭, 市吉伸行 | 情報処理学会研究報告プログラミング（PRO）,  1996,  82(1996-PRO-008), p. 13-18,  1996-08-28 | https://ipsj.ixsq.nii.ac.jp/records/30293 (GET HTTP 200, 61209 bytes; HTML not read) | https://ipsj.ixsq.nii.ac.jp/record/30293/files/IPSJ-PRO96008003.pdf | **opened-and-read**: full GET HTTP 200, %PDF magic, 453203 bytes, 6 pp, image-only scan; read page image p.1 (title, abstract). Open: yes. File `ipsj_30293_IPSJ-PRO96008003.pdf` | Evaluation of the external (remote) reference management of the distributed KL1 implementation on a real parallel machine: export-table entry counts, inter-processor garbage loops. |

#### A2. PIM/m (Mitsubishi) hardware, FEP, CSP

| paper (JP title / EN title as given in the repository record) | authors | bibliographic data | landing URL | PDF URL | status (+evidence) | why it matters |
|---|---|---|---|---|---|---|
| PIM/mフロントエンド・プロセッサ : GC方式とその評価 / Garbage Collector of PIM/m Fornt-end Processor | 立野裕和, 川田易治, 高橋勝己, 池田守宏 | 全国大会講演論文集,  第42回,  ハードウェア, p. 27-28,  1991-02-25 | https://ipsj.ixsq.nii.ac.jp/records/120643 (GET HTTP 200, 65908 bytes; HTML not read) | https://ipsj.ixsq.nii.ac.jp/record/120643/files/KJ00001341483.pdf | resolved-not-read (full GET HTTP 200, %PDF magic, 172640 bytes, 2 pp, image-only scan; saved, content not read). Open: yes. File `ipsj_120643_KJ00001341483.pdf` | (from repository abstract, paper not read) GC scheme and its evaluation for PSI-III, the name used here for the PIM/m front-end processor (a workstation running ESP with the PIM/m element processor as CPU). |
| Iterative ? Deepening A*アルゴリズムのスタック分割動的負荷分散方式による並列化と並列推論マシン　PIM/m上の性能評価 / An Implementation of Parallel Iterative - Deepening A* using Stack - splitting Dynamic Load Balancer and Its Evaluation on the Parallel Inference Machine PIM/m | 和田正寛, 市吉伸行, 六沢一昭 | 情報処理学会研究報告プログラミング（PRO）,  1992,  67(1992-PRO-008), p. 195-202,  1992-08-20 | https://ipsj.ixsq.nii.ac.jp/records/30652 (GET HTTP 200, 65964 bytes; HTML not read) | https://ipsj.ixsq.nii.ac.jp/record/30652/files/IPSJ-PRO92008025.pdf | resolved-not-read: range GET HTTP 206, %PDF magic, Content-Range bytes 0-1023/1255062. Open: yes | (from title only, unverified) relevance is the topic of this table: PIM/m (Mitsubishi) hardware, FEP, CSP |

#### A3. Multi-PSI (v1, /V2): hardware, network, KL1 system

| paper (JP title / EN title as given in the repository record) | authors | bibliographic data | landing URL | PDF URL | status (+evidence) | why it matters |
|---|---|---|---|---|---|---|
| マルチPSIシステムとその接続方式 / MultiPSI system and its network | 木村康則, 瀧和男, 内田俊一 | 全国大会講演論文集,  第33回,  アーキテクチャおよびハードウェア, p. 145-146,  1986-10-01 | https://ipsj.ixsq.nii.ac.jp/records/113878 (GET HTTP 200, 64271 bytes; HTML not read) | https://ipsj.ixsq.nii.ac.jp/record/113878/files/KJ00001330684.pdf | resolved-not-read: range GET HTTP 206, %PDF magic, Content-Range bytes 0-1023/164417. Open: yes | (from title only, unverified) relevance is the topic of this table: Multi-PSI (v1, /V2): hardware, network, KL1 system |
| マルチPSIのネットワーク・ハードウェア構成 / Network Hardware of Multi-PSI system | 益田嘉直, 瀧和男, 木村康則 | 全国大会講演論文集,  第33回,  アーキテクチャおよびハードウェア, p. 147-148,  1986-10-01 | https://ipsj.ixsq.nii.ac.jp/records/113879 (GET HTTP 200, 63216 bytes; HTML not read) | https://ipsj.ixsq.nii.ac.jp/record/113879/files/KJ00001330685.pdf | resolved-not-read: range GET HTTP 206, %PDF magic, Content-Range bytes 0-1023/175722. Open: yes | (from title only, unverified) relevance is the topic of this table: Multi-PSI (v1, /V2): hardware, network, KL1 system |
| マルチPSI重要素プロセッサPSI-IIの最適化手法 / Optimization Method in Multi-PSI Element Processor (PSI-II) | 中島浩, 近山隆, 中島克人 | 全国大会講演論文集,  第33回,  アーキテクチャおよびハードウェア, p. 151-152,  1986-10-01 | https://ipsj.ixsq.nii.ac.jp/records/113881 (GET HTTP 200, 63063 bytes; HTML not read) | https://ipsj.ixsq.nii.ac.jp/record/113881/files/KJ00001330687.pdf | resolved-not-read: range GET HTTP 206, %PDF magic, Content-Range bytes 0-1023/192268. Open: yes | (from title only, unverified) PSI-II optimisation techniques. |
| マルチPSI要素プロセッサPSI-IIのメモリ管理とプロセス管理 / Memory and Process Management for Multi-PSI Element Processor (PSI-II) | 吉田裕之, 池田守宏, 中島浩, 横田実, 中島克人 | 全国大会講演論文集,  第33回,  アーキテクチャおよびハードウェア, p. 153-154,  1986-10-01 | https://ipsj.ixsq.nii.ac.jp/records/113882 (GET HTTP 200, 69269 bytes; HTML not read) | https://ipsj.ixsq.nii.ac.jp/record/113882/files/KJ00001330688.pdf | resolved-not-read (full GET HTTP 200, %PDF magic, 168829 bytes, 2 pp, image-only scan; saved, content not read). Open: yes. File `ipsj_113882_KJ00001330688.pdf` | (from repository abstract, paper not read) PSI-II: multiple logical address spaces, process management and memory management. |
| マルチPSI要素プロセッサPSI-IIのマイクロ・プログラム・シミュレータZEUS / ZEUS microprogram simulator for Multi-PSI Element Processor (PSI-II) | 守山貢, 吉田裕之, 中島克人 | 全国大会講演論文集,  第33回,  アーキテクチャおよびハードウェア, p. 155-156,  1986-10-01 | https://ipsj.ixsq.nii.ac.jp/records/113883 (GET HTTP 200, 63358 bytes; HTML not read) | https://ipsj.ixsq.nii.ac.jp/record/113883/files/KJ00001330689.pdf | resolved-not-read (full GET HTTP 200, %PDF magic, 174218 bytes, 2 pp, image-only scan; saved, content not read). Open: yes. File `ipsj_113883_KJ00001330689.pdf` | (from repository abstract, paper not read) ZEUS, a software simulator of PSI-II microinstruction execution used to develop and verify PSI-II firmware before hardware. |
| マルチPSIにおける接続ネットワークの構成とその評価 / Network hardware and its evaluation of the Multi - PSI system | 益田嘉直, 岩山洋明, 石塚裕一, 末原義人, 瀧和男, 杉野栄二 | 情報処理学会研究報告計算機アーキテクチャ（ARC）,  1987,  45(1987-ARC-066), p. 1-8,  1987-07-10 | https://ipsj.ixsq.nii.ac.jp/records/24868 (GET HTTP 200, 75774 bytes; HTML not read) | https://ipsj.ixsq.nii.ac.jp/record/24868/files/IPSJ-ARC87066008.pdf | resolved-not-read: range GET HTTP 206, %PDF magic, Content-Range bytes 0-1023/1241760. Open: yes | (from title only, unverified) Multi-PSI network, ARC version. |
| マルチPSIにおける接続ネットワークの試作と評価 / Network Hardware and Evaluation of the Multi - PSI System | 益田嘉直, 石塚裕一, 岩山洋明, 瀧和男, 杉野栄二 | 情報処理学会論文誌,  29,  10, p. 995-1003,  1988-10-15,ISSN,1882-7764 | https://ipsj.ixsq.nii.ac.jp/records/15329 (GET HTTP 200, 72070 bytes; HTML not read) | https://ipsj.ixsq.nii.ac.jp/record/15329/files/IPSJ-JNL2910010.pdf | resolved-not-read (full GET HTTP 200, %PDF magic, 733546 bytes, 9 pp, image-only scan; saved, content not read). Open: yes. File `ipsj_15329_IPSJ-JNL2910010.pdf` | (from title only, unverified) Multi-PSI (v1) interconnection network hardware and evaluation, journal paper. |
| マルチPSIにおける実験的負荷分散メカニズム / A LOAD BALANCING MECHANISM FOR THE Multi - PSI SYSTEM | 武田保孝, 岩山洋明, 中島浩, 益田嘉直, 近山隆, 瀧和男 | 情報処理学会研究報告計算機アーキテクチャ（ARC）,  1988,  79(1988-ARC-073), p. 93-100,  1988-10-31 | https://ipsj.ixsq.nii.ac.jp/records/24765 (GET HTTP 200, 75694 bytes; HTML not read) | https://ipsj.ixsq.nii.ac.jp/record/24765/files/IPSJ-ARC88073013.pdf | resolved-not-read: range GET HTTP 206, %PDF magic, Content-Range bytes 0-1023/1250700. Open: yes | (from title only, unverified) Experimental load-distribution mechanism on Multi-PSI. |

#### A4. PIM/p (Fujitsu)

| paper (JP title / EN title as given in the repository record) | authors | bibliographic data | landing URL | PDF URL | status (+evidence) | why it matters |
|---|---|---|---|---|---|---|
| 並列推論マシンPIM/pの概要 / The Overview of Parallel Inference Machine PIM/p | 後藤厚宏, 篠木剛, 久門耕一, 服部彰 | 全国大会講演論文集,  第37回,  アーキテクチャおよびハードウェア, p. 135-136,  1988-09-12 | https://ipsj.ixsq.nii.ac.jp/records/115058 (GET HTTP 200, 66397 bytes; HTML not read) | https://ipsj.ixsq.nii.ac.jp/record/115058/files/KJ00003117592.pdf | resolved-not-read: range GET HTTP 206, %PDF magic, Content-Range bytes 0-1023/206784. Open: yes | (from title only, unverified) relevance is the topic of this table: PIM/p (Fujitsu) |
| 並列推論マシンPIM/pの要素プロセッサのアーキテクチャ / The Architecture of a Processor Element of PIM/p | 篠木剛, 松本明, 近山隆, 後藤厚宏, 服部彰 | 全国大会講演論文集,  第37回,  アーキテクチャおよびハードウェア, p. 137-138,  1988-09-12 | https://ipsj.ixsq.nii.ac.jp/records/115059 (GET HTTP 200, 69243 bytes; HTML not read) | https://ipsj.ixsq.nii.ac.jp/record/115059/files/KJ00003117593.pdf | resolved-not-read: range GET HTTP 206, %PDF magic, Content-Range bytes 0-1023/198883. Open: yes | (from title only, unverified) relevance is the topic of this table: PIM/p (Fujitsu) |
| 並列推論マシンPIM/pのネットワーク / The Network of Parallel Inference Machine PIM/p | 久門耕一, 服部彰, 後藤厚宏 | 全国大会講演論文集,  第37回,  アーキテクチャおよびハードウェア, p. 139-140,  1988-09-12 | https://ipsj.ixsq.nii.ac.jp/records/115060 (GET HTTP 200, 62903 bytes; HTML not read) | https://ipsj.ixsq.nii.ac.jp/record/115060/files/KJ00003117594.pdf | resolved-not-read: range GET HTTP 206, %PDF magic, Content-Range bytes 0-1023/172699. Open: yes | (from title only, unverified) relevance is the topic of this table: PIM/p (Fujitsu) |
| 並列推論マシンPIM/pの要素プロセッサにおける分岐機能の高速化のためのアーキテクチャ / The Architecture on Branch of a Processor Element of PIM/p | 篠木剛, 久門耕一, 安里彰, 服部彰, 近山隆, 後藤厚宏 | 全国大会講演論文集,  第39回,  ハードウェア, p. 1774-1775,  1989-10-16 | https://ipsj.ixsq.nii.ac.jp/records/117942 (GET HTTP 200, 72523 bytes; HTML not read) | https://ipsj.ixsq.nii.ac.jp/record/117942/files/KJ00003118278.pdf | resolved-not-read: range GET HTTP 206, %PDF magic, Content-Range bytes 0-1023/189678. Open: yes | (from title only, unverified) relevance is the topic of this table: PIM/p (Fujitsu) |
| 並列推論マシンPIM/pのアーキテクチャ / The Architecture of Parallel Inference Machine PIM/p | 服部彰, 篠木剛, 久門耕一, 後藤厚宏 | 情報処理学会論文誌,  30,  12, p. 1584-1592,  1989-12-15,ISSN,1882-7764 | https://ipsj.ixsq.nii.ac.jp/records/15121 (GET HTTP 200, 69099 bytes; HTML not read) | https://ipsj.ixsq.nii.ac.jp/record/15121/files/IPSJ-JNL3012008.pdf | resolved-not-read (full GET HTTP 200, %PDF magic, 729235 bytes, 9 pp, image-only scan; saved, content not read). Open: yes. File `ipsj_15121_IPSJ-JNL3012008.pdf` | (from title only, unverified) PIM/p architecture, journal paper. |
| Processer Element Architecture for a Parallel Inference Machine  PIM/p / Processer Element Architecture for a Parallel Inference Machine, PIM/p | Atshiro, Goto, Tsuyoshi, Shinogi, Takashi, Chikayama, Kouichi, Kumon, Akira, Hattoti, Atshiro, Goto, Tsuyoshi, Shinogi, Takashi, Chikayama, Kouichi, Kumon, Akira, Hattoti | Journal of Information Processing ,  13,  2, p. 174-182,  1990-08-25,ISSN,1882-6652 | https://ipsj.ixsq.nii.ac.jp/records/59752 (GET HTTP 200, 69118 bytes; HTML not read) | https://ipsj.ixsq.nii.ac.jp/record/59752/files/IPSJ-JIP1302009.pdf | resolved-not-read: range GET HTTP 206, %PDF magic, Content-Range bytes 0-1023/1894536. Open: yes | (from title only, unverified) relevance is the topic of this table: PIM/p (Fujitsu) |
| 並列推論マシンPIM/p用KL1処理系の実装 / Implementation of KL1 Processing System for Parallel Inference Machine PIM/p | 宮崎芳枝, 畑澤宏善, 平野喜芳 | 情報処理学会研究報告計算機アーキテクチャ（ARC）,  1991,  64(1991-ARC-089), p. 209-216,  1991-07-19 | https://ipsj.ixsq.nii.ac.jp/records/24532 (GET HTTP 200, 66246 bytes; HTML not read) | https://ipsj.ixsq.nii.ac.jp/record/24532/files/IPSJ-ARC91089028.pdf | **opened-and-read**: full GET HTTP 200, %PDF magic, 1091542 bytes, 8 pp, image-only scan; read page image p.1 (title, abstract). Open: yes. File `ipsj_24532_IPSJ-ARC91089028.pdf` | KL1 system for PIM/p built from the common abstract spec (KL1-B) in three levels: inline machine instructions, macro-call subroutines, macro-body subroutines; includes compiler and simulator evaluation. ARC 89-28 (same meeting as the VPIM paper). |

#### A5. PIM/c (Hitachi)

| paper (JP title / EN title as given in the repository record) | authors | bibliographic data | landing URL | PDF URL | status (+evidence) | why it matters |
|---|---|---|---|---|---|---|
| 並列推論マシンPIM/c : 概要 / Parallel Inference Machine PIM/c : Global Structure | 後藤厚宏, 瀧和男, 中川貴之, 杉江衛 | 全国大会講演論文集,  第40回,  ハードウェア, p. 1177-1178,  1990-03-14 | https://ipsj.ixsq.nii.ac.jp/records/118805 (GET HTTP 200, 66437 bytes; HTML not read) | https://ipsj.ixsq.nii.ac.jp/record/118805/files/KJ00001338425.pdf | resolved-not-read: range GET HTTP 206, %PDF magic, Content-Range bytes 0-1023/173038. Open: yes | (from title only, unverified) relevance is the topic of this table: PIM/c (Hitachi) |
| 並列推論マシンPIM/c : CPUについて / Parallel Inference Machine PIM/c : CPU | 田中誠, 堀尾公正, 中川貴之, 杉江衛 | 全国大会講演論文集,  第40回,  ハードウェア, p. 1179,  1990-03-14 | https://ipsj.ixsq.nii.ac.jp/records/118806 (GET HTTP 200, 65704 bytes; HTML not read) | https://ipsj.ixsq.nii.ac.jp/record/118806/files/KJ00001338426.pdf | resolved-not-read: range GET HTTP 206, %PDF magic, Content-Range bytes 0-1023/75178. Open: yes | (from title only, unverified) relevance is the topic of this table: PIM/c (Hitachi) |
| 並列推論マシンPIM/c : キャッシュ・メモリについて / Parallel Inference Machine PIM/c : Snooping Cache Organization | 垂井俊明, 井門徳安, 前田浩光, 中川高之, 杉江衛 | 全国大会講演論文集,  第40回,  ハードウェア, p. 1180,  1990-03-14 | https://ipsj.ixsq.nii.ac.jp/records/118807 (GET HTTP 200, 69102 bytes; HTML not read) | https://ipsj.ixsq.nii.ac.jp/record/118807/files/KJ00001338427.pdf | resolved-not-read: range GET HTTP 206, %PDF magic, Content-Range bytes 0-1023/88054. Open: yes | (from title only, unverified) relevance is the topic of this table: PIM/c (Hitachi) |
| 並列推論マシンPIM/c : 負荷分散支援機構 / Parallel Inference Machine PIW/c : Mechanism to support dynamic load balancing | 井門徳安, 前田浩光, 垂井俊明, 中川貴之, 杉江衛 | 全国大会講演論文集,  第40回,  ハードウェア, p. 1181,  1990-03-14 | https://ipsj.ixsq.nii.ac.jp/records/118808 (GET HTTP 200, 69123 bytes; HTML not read) | https://ipsj.ixsq.nii.ac.jp/record/118808/files/KJ00001338428.pdf | resolved-not-read: range GET HTTP 206, %PDF magic, Content-Range bytes 0-1023/88546. Open: yes | (from title only, unverified) relevance is the topic of this table: PIM/c (Hitachi) |
| 並列推論マシンPIM/c : メンテナンス・デバッグ機構について / Parallel Inference Machine PIM/c : Maintenance & Debug Sub-system | 前田浩光, 井門徳安, 垂井俊明, 中川貴之, 杉江衛 | 全国大会講演論文集,  第40回,  ハードウェア, p. 1182,  1990-03-14 | https://ipsj.ixsq.nii.ac.jp/records/118809 (GET HTTP 200, 69230 bytes; HTML not read) | https://ipsj.ixsq.nii.ac.jp/record/118809/files/KJ00001338429.pdf | resolved-not-read: range GET HTTP 206, %PDF magic, Content-Range bytes 0-1023/70948. Open: yes | (from title only, unverified) relevance is the topic of this table: PIM/c (Hitachi) |
| 並列推論マシンPIM/c : PIM/cのファームウエアの開発 / Parallel Inference Machine PIM/c : Development of PIM/c Firmware | 中川貴之, 朝家真知子, 早木茂, 今西祐之, 杉江衛 | 全国大会講演論文集,  第42回,  ハードウェア, p. 39,  1991-02-25 | https://ipsj.ixsq.nii.ac.jp/records/120649 (GET HTTP 200, 69463 bytes; HTML not read) | https://ipsj.ixsq.nii.ac.jp/record/120649/files/KJ00001341489.pdf | **opened-and-read**: full GET HTTP 200, %PDF magic, 81581 bytes, 1 pp, image-only scan; read page image whole paper (1 page). Open: yes. File `ipsj_120649_KJ00001341489.pdf` | PIM/c firmware: KL1-B spec is >33K steps in load/store terms and is written as VPIM; microprogram v1 generated automatically from VPIM, v2 semi-automatically; 104-bit horizontal microinstruction; append microstep counts (416 -> after optimisation); 200 KLIPS target. |
| 並列推論マシンPIM/c : 水平型マイクロプログラムの自動生成と最適化 / Parallel inference Machine PIM/c : Automatic Horizontal Microprogram Generation and Optimization | 早木茂, 森務, 橋田亨, 今西祐之, 中川貴之, 杉江衛 | 全国大会講演論文集,  第42回,  ハードウェア, p. 40,  1991-02-25 | https://ipsj.ixsq.nii.ac.jp/records/120650 (GET HTTP 200, 72617 bytes; HTML not read) | https://ipsj.ixsq.nii.ac.jp/record/120650/files/KJ00001341490.pdf | resolved-not-read (full GET HTTP 200, %PDF magic, 68928 bytes, 1 pp, image-only scan; saved, content not read). Open: yes. File `ipsj_120650_KJ00001341490.pdf` | (from title only, unverified) PIM/c: automatic generation and optimisation of horizontal microprograms. |
| 並列推論マシンPIM/c : 分岐コストを0にするためのマイクロアドレスの自動生成 / Parallel Inference Machine PIM/c : Automatic Generation of Micro Instruction Address to Make Brunch Cost to Zero | 今西祐之, 佐久間良, 小島丈一, 早木茂, 中川貴之, 杉江衛 | 全国大会講演論文集,  第42回,  ハードウェア, p. 41,  1991-02-25 | https://ipsj.ixsq.nii.ac.jp/records/120651 (GET HTTP 200, 72632 bytes; HTML not read) | https://ipsj.ixsq.nii.ac.jp/record/120651/files/KJ00001341491.pdf | resolved-not-read (full GET HTTP 200, %PDF magic, 85809 bytes, 1 pp, image-only scan; saved, content not read). Open: yes. File `ipsj_120651_KJ00001341491.pdf` | (from title only, unverified) PIM/c: automatic microaddress assignment to make branch cost zero. |

#### A6. PIM/i (Oki)

| paper (JP title / EN title as given in the repository record) | authors | bibliographic data | landing URL | PDF URL | status (+evidence) | why it matters |
|---|---|---|---|---|---|---|
| 並列推論マシンPIM/iの概要 / The Overview of Parallel Inference Machine PIM/i | 大原輝彦, 武田浩一, 佐藤正樹 | 全国大会講演論文集,  第40回,  ハードウェア, p. 1185-1186,  1990-03-14 | https://ipsj.ixsq.nii.ac.jp/records/118811 (GET HTTP 200, 62735 bytes; HTML not read) | https://ipsj.ixsq.nii.ac.jp/record/118811/files/KJ00001338431.pdf | resolved-not-read: range GET HTTP 206, %PDF magic, Content-Range bytes 0-1023/161152. Open: yes | (from title only, unverified) relevance is the topic of this table: PIM/i (Oki) |
| 並列推論マシンPIM/iの要素プロセッサのアーキテクチャ / The Architecture of a Processing Element of PIM/i | 武田浩一, 大原輝彦, 佐藤正樹 | 全国大会講演論文集,  第40回,  ハードウェア, p. 1187-1188,  1990-03-14 | https://ipsj.ixsq.nii.ac.jp/records/118812 (GET HTTP 200, 62749 bytes; HTML not read) | https://ipsj.ixsq.nii.ac.jp/record/118812/files/KJ00001338432.pdf | resolved-not-read: range GET HTTP 206, %PDF magic, Content-Range bytes 0-1023/152435. Open: yes | (from title only, unverified) relevance is the topic of this table: PIM/i (Oki) |
| 並列推論マシンPIM/iの処理系の概要 / Overview of the (KL1) language system of PIM/i (my translation; record has no English title) | 久野英治, 佐藤正俊 | 全国大会講演論文集,  第41回,  ソフトウェア, p. 58-59,  1990-09-04 | https://ipsj.ixsq.nii.ac.jp/records/119474 (GET HTTP 200, 55221 bytes; HTML not read) | https://ipsj.ixsq.nii.ac.jp/record/119474/files/KJ00003118570.pdf | resolved-not-read: range GET HTTP 206, %PDF magic, Content-Range bytes 0-1023/150539. Open: yes | (from title only, unverified) relevance is the topic of this table: PIM/i (Oki) |
| 並列推論マシンPIM/iの開発支援環境 : シミュレーター / Development support environment for PIM/i: the simulator (my translation; record has no English title) | 吉田裕一, 佐藤正俊, 大原輝彦 | 全国大会講演論文集,  第41回,  ソフトウェア工学, p. 369-370,  1990-09-04 | https://ipsj.ixsq.nii.ac.jp/records/119630 (GET HTTP 200, 57407 bytes; HTML not read) | https://ipsj.ixsq.nii.ac.jp/record/119630/files/KJ00003118726.pdf | resolved-not-read: range GET HTTP 206, %PDF magic, Content-Range bytes 0-1023/148175. Open: yes | (from title only, unverified) relevance is the topic of this table: PIM/i (Oki) |
| 並列推論マシンPIM/iの開発支援環境 : 翻訳系 / (no English title in record) | 佐藤正俊, 久野英治 | 全国大会講演論文集,  第41回,  ソフトウェア工学, p. 371-372,  1990-09-04 | https://ipsj.ixsq.nii.ac.jp/records/119631 (GET HTTP 200, 55324 bytes; HTML not read) | https://ipsj.ixsq.nii.ac.jp/record/119631/files/KJ00003118727.pdf | resolved-not-read: range GET HTTP 206, %PDF magic, Content-Range bytes 0-1023/156902. Open: yes | (from title only, unverified) relevance is the topic of this table: PIM/i (Oki) |
| 並列推論マシンPIM/iのメモリシステムの概要 / Overview of the memory system of PIM/i (my translation; record has no English title) | 武田浩一, 佐藤正樹, 大原輝彦 | 全国大会講演論文集,  第41回,  ハードウェア, p. 161-162,  1990-09-04 | https://ipsj.ixsq.nii.ac.jp/records/119759 (GET HTTP 200, 56575 bytes; HTML not read) | https://ipsj.ixsq.nii.ac.jp/record/119759/files/KJ00001336694.pdf | resolved-not-read: range GET HTTP 206, %PDF magic, Content-Range bytes 0-1023/161718. Open: yes | (from title only, unverified) relevance is the topic of this table: PIM/i (Oki) |
| 並列推論マシンPIM/iのファイングレインパラレリズム / Fine-grain parallelism in the parallel inference machine PIM/i (my translation; record has no English title) | 加藤研児, 佐藤正俊, 武田浩一, 大原輝彦 | 全国大会講演論文集,  第41回,  ハードウェア, p. 169-170,  1990-09-04 | https://ipsj.ixsq.nii.ac.jp/records/119763 (GET HTTP 200, 59096 bytes; HTML not read) | https://ipsj.ixsq.nii.ac.jp/record/119763/files/KJ00001336698.pdf | resolved-not-read: range GET HTTP 206, %PDF magic, Content-Range bytes 0-1023/152165. Open: yes | (from title only, unverified) relevance is the topic of this table: PIM/i (Oki) |
| 並列推論マシンPIM/iにおけるゴール通信方式の評価 / Evaluation of Goal Communication on Parallel Inference Machine PIM/i | 久野英治, 佐藤正俊 | 全国大会講演論文集,  第42回,  ソフトウェア, p. 145-146,  1991-02-25 | https://ipsj.ixsq.nii.ac.jp/records/120518 (GET HTTP 200, 60762 bytes; HTML not read) | https://ipsj.ixsq.nii.ac.jp/record/120518/files/KJ00001340857.pdf | resolved-not-read: range GET HTTP 206, %PDF magic, Content-Range bytes 0-1023/191874. Open: yes | (from title only, unverified) relevance is the topic of this table: PIM/i (Oki) |
| 並列推論マシンPIM/iにおける実行履歴の利用 / The usage of profile in parallel machine PIM/i | 吉田裕一, 佐藤正俊 | 全国大会講演論文集,  第42回,  ソフトウェア工学, p. 234,  1991-02-25 | https://ipsj.ixsq.nii.ac.jp/records/120563 (GET HTTP 200, 59912 bytes; HTML not read) | https://ipsj.ixsq.nii.ac.jp/record/120563/files/KJ00001340902.pdf | resolved-not-read: range GET HTTP 206, %PDF magic, Content-Range bytes 0-1023/80440. Open: yes | (from title only, unverified) relevance is the topic of this table: PIM/i (Oki) |
| 並列推論マシンPIM/iの要素プロセッサのアーキテクチャ評価 / Measurements of Instruction Set Usage of the Processing Element of Parallel Inference Machine PIM/i | 武田浩一, 佐藤正俊, 大原輝彦 | 全国大会講演論文集,  第42回,  ハードウェア, p. 31-32,  1991-02-25 | https://ipsj.ixsq.nii.ac.jp/records/120645 (GET HTTP 200, 63766 bytes; HTML not read) | https://ipsj.ixsq.nii.ac.jp/record/120645/files/KJ00001341485.pdf | resolved-not-read: range GET HTTP 206, %PDF magic, Content-Range bytes 0-1023/168346. Open: yes | (from title only, unverified) relevance is the topic of this table: PIM/i (Oki) |
| 並列推論マシンPIM/iのタグアーキテクチャの評価 / Evalution of Tagged Architecture on Parallel Inference Machine PIM/i | 加藤研児, 佐藤正俊, 武田浩一, 大原輝彦 | 全国大会講演論文集,  第42回,  ハードウェア, p. 33-34,  1991-02-25 | https://ipsj.ixsq.nii.ac.jp/records/120646 (GET HTTP 200, 66642 bytes; HTML not read) | https://ipsj.ixsq.nii.ac.jp/record/120646/files/KJ00001341486.pdf | resolved-not-read: range GET HTTP 206, %PDF magic, Content-Range bytes 0-1023/160858. Open: yes | (from title only, unverified) relevance is the topic of this table: PIM/i (Oki) |
| 並列推論マシンPIM/iのメモリシステムの評価 : 並列キャッシュ / Evaluation of the Parallel Inference Machine PIM/i Memori System : Parallel Cache | 大原輝彦, 武田浩一, 佐藤正樹 | 全国大会講演論文集,  第42回,  ハードウェア, p. 35-36,  1991-02-25 | https://ipsj.ixsq.nii.ac.jp/records/120647 (GET HTTP 200, 63347 bytes; HTML not read) | https://ipsj.ixsq.nii.ac.jp/record/120647/files/KJ00001341487.pdf | resolved-not-read: range GET HTTP 206, %PDF magic, Content-Range bytes 0-1023/161000. Open: yes | (from title only, unverified) relevance is the topic of this table: PIM/i (Oki) |
| 並列推論マシンPIM/iにおける分岐特性 / Branch Behavior in Parallel Inference Machi PIM/i | 佐藤正俊, 武田浩一, 大原輝彦 | 全国大会講演論文集,  第42回,  ハードウェア, p. 37-38,  1991-02-25 | https://ipsj.ixsq.nii.ac.jp/records/120648 (GET HTTP 200, 64068 bytes; HTML not read) | https://ipsj.ixsq.nii.ac.jp/record/120648/files/KJ00001341488.pdf | resolved-not-read: range GET HTTP 206, %PDF magic, Content-Range bytes 0-1023/166738. Open: yes | (from title only, unverified) relevance is the topic of this table: PIM/i (Oki) |
| 並列推論マシンPIM/iプロセッサの設計 / Design of the Parallel Inference Machine PIM/i Processor | 佐藤正俊, 武田浩一, 大原輝彦 | 情報処理学会論文誌,  33,  3, p. 278-287,  1992-03-15,ISSN,1882-7764 | https://ipsj.ixsq.nii.ac.jp/records/14717 (GET HTTP 200, 65579 bytes; HTML not read) | https://ipsj.ixsq.nii.ac.jp/record/14717/files/IPSJ-JNL3303004.pdf | **opened-and-read**: full GET HTTP 200, %PDF magic, 803701 bytes, 10 pp, image-only scan; read page image p.1 of 10. Open: yes. File `ipsj_14717_IPSJ-JNL3303004.pdf` | **The named target IPSJ Trans. 33(3) 278-287**. Authors as printed: 佐藤正俊, 武田浩一, 大原輝彦 (Oki; English byline Masatoshi Sato, Koichi Takeda, Teruhiko Oohara). RISC + LIW (long instruction word) design for KL1. |
| 並列推論マシンPIM/iにおけるKL1言語処理系の改良 / Improvements to the KL1 language system on PIM/i (my translation; record has no English title) | 加藤研児, 久野英治, 六沢一昭, 武田浩一, 大原輝彦 | 全国大会講演論文集,  第46回,  ソフトウェア, p. 49-50,  1993-03-01 | https://ipsj.ixsq.nii.ac.jp/records/123659 (GET HTTP 200, 59792 bytes; HTML not read) | https://ipsj.ixsq.nii.ac.jp/record/123659/files/KJ00001337501.pdf | resolved-not-read: range GET HTTP 206, %PDF magic, Content-Range bytes 0-1023/171115. Open: yes | (from title only, unverified) relevance is the topic of this table: PIM/i (Oki) |
| 並列推論マシンPIM/iのアドレストレースによるメモリシステムの評価 / Evaluation of System on Parallel Inference Machine PIM/i Using Address Tracing | 大原輝彦, 武田浩一 | 全国大会講演論文集,  第46回,  ハードウェア, p. 95-96,  1993-03-01 | https://ipsj.ixsq.nii.ac.jp/records/123855 (GET HTTP 200, 60282 bytes; HTML not read) | https://ipsj.ixsq.nii.ac.jp/record/123855/files/KJ00001337702.pdf | resolved-not-read: range GET HTTP 206, %PDF magic, Content-Range bytes 0-1023/183133. Open: yes | (from title only, unverified) relevance is the topic of this table: PIM/i (Oki) |
| 並列推論マシンPIM/iのバスの動特性の解析 / Analysis of Dynamic Characteristics or the Shared Bus on the Parallel Inference Machine PIM/i | 武田浩一, 大原輝彦 | 全国大会講演論文集,  第46回,  ハードウェア, p. 97-98,  1993-03-01 | https://ipsj.ixsq.nii.ac.jp/records/123856 (GET HTTP 200, 60796 bytes; HTML not read) | https://ipsj.ixsq.nii.ac.jp/record/123856/files/KJ00001337703.pdf | resolved-not-read: range GET HTTP 206, %PDF magic, Content-Range bytes 0-1023/183620. Open: yes | (from title only, unverified) relevance is the topic of this table: PIM/i (Oki) |

#### A7. PIM/k (Toshiba)

| paper (JP title / EN title as given in the repository record) | authors | bibliographic data | landing URL | PDF URL | status (+evidence) | why it matters |
|---|---|---|---|---|---|---|
| 並列推論マシンPIM/k : ハードウェア アーキテクチャ / Parallel Inference Machine PIM/k : Hardware Architecture | 浅野滋博 | 全国大会講演論文集,  第39回,  ハードウェア, p. 1772-1773,  1989-10-16 | https://ipsj.ixsq.nii.ac.jp/records/117941 (GET HTTP 200, 56700 bytes; HTML not read) | https://ipsj.ixsq.nii.ac.jp/record/117941/files/KJ00003118277.pdf | resolved-not-read: range GET HTTP 206, %PDF magic, Content-Range bytes 0-1023/157537. Open: yes | (from title only, unverified) relevance is the topic of this table: PIM/k (Toshiba) |
| 並列階層キャッシュメモリの性能評価 / Simulation study of a two-level coherent cache architecture | 村谷博文, 浅野滋博, 酒井浩 | 全国大会講演論文集,  第40回,  ハードウェア, p. 1213-1214,  1990-03-14 | https://ipsj.ixsq.nii.ac.jp/records/118825 (GET HTTP 200, 63425 bytes; HTML not read) | https://ipsj.ixsq.nii.ac.jp/record/118825/files/KJ00001338445.pdf | resolved-not-read: range GET HTTP 206, %PDF magic, Content-Range bytes 0-1023/158989. Open: yes | (from repository abstract, paper not read) Simulator study of two-level coherent cache; the model is PIM/k (per abstract, title does not name it). |
| 並列階層キャッシュの性能とキャッシュ・ミスの分類 / (no English title in record) | 村谷博文 | 全国大会講演論文集,  第41回,  ハードウェア, p. 105-106,  1990-09-04 | https://ipsj.ixsq.nii.ac.jp/records/119677 (GET HTTP 200, 53955 bytes; HTML not read) | https://ipsj.ixsq.nii.ac.jp/record/119677/files/KJ00001336612.pdf | resolved-not-read: range GET HTTP 206, %PDF magic, Content-Range bytes 0-1023/154693. Open: yes | (from repository abstract, paper not read) PIM/k hierarchical parallel cache: cache-miss classification by simulation (PIM/k named in abstract). |
| 並列推論マシンPIM/kの開発(1) : KL1処理系のデバッグ手法とツール / Development of Parallel Inference Machine PIM/k(1) : Debugging Technique of KL1 System | 沖健治, 丹野尚, 酒井浩, 仲瀬明彦, 武脇敏晃 | 全国大会講演論文集,  第42回,  ソフトウェア, p. 13-14,  1991-02-25 | https://ipsj.ixsq.nii.ac.jp/records/120452 (GET HTTP 200, 69358 bytes; HTML not read) | https://ipsj.ixsq.nii.ac.jp/record/120452/files/KJ00001340790.pdf | resolved-not-read: range GET HTTP 206, %PDF magic, Content-Range bytes 0-1023/177942. Open: yes | (from title only, unverified) relevance is the topic of this table: PIM/k (Toshiba) |
| 並列推論マシンPIM/kの開発(2) : KL1処理系の予備評価 / Development of Parallel Inference Machine PIM/k(2) : Debugging Technique of KL1 System | 丹野尚, 沖健治, 酒井浩, 仲瀬明彦, 武脇敏晃 | 全国大会講演論文集,  第42回,  ソフトウェア, p. 15-16,  1991-02-25 | https://ipsj.ixsq.nii.ac.jp/records/120453 (GET HTTP 200, 69307 bytes; HTML not read) | https://ipsj.ixsq.nii.ac.jp/record/120453/files/KJ00001340791.pdf | resolved-not-read: range GET HTTP 206, %PDF magic, Content-Range bytes 0-1023/199173. Open: yes | (from title only, unverified) relevance is the topic of this table: PIM/k (Toshiba) |
| 拡張MOESIモデルと並列階層キャッシュ・プロトコル / An entended MOESI model and parallel hierarchical cache protocols | 村谷博文 | 情報処理学会研究報告計算機アーキテクチャ（ARC）,  1991,  64(1991-ARC-089), p. 169-176,  1991-07-19 | https://ipsj.ixsq.nii.ac.jp/records/24527 (GET HTTP 200, 59288 bytes; HTML not read) | https://ipsj.ixsq.nii.ac.jp/record/24527/files/IPSJ-ARC91089023.pdf | resolved-not-read: range GET HTTP 206, %PDF magic, Content-Range bytes 0-1023/1195063. Open: yes | (from repository abstract, paper not read) PIM/k cache-consistency protocol (hierarchical extension of the Berkeley protocol), extended MOESI model, proposed fix (PIM/k named in abstract). |

#### A8. PSI / PSI-II / PSI-III / PSI/UX hardware and firmware

| paper (JP title / EN title as given in the repository record) | authors | bibliographic data | landing URL | PDF URL | status (+evidence) | why it matters |
|---|---|---|---|---|---|---|
| 遂次型推論マシンPSIのオペレーティング・システム / Operating system of the sequential inference machine PSI (my translation; record has no English title) | 服部隆, 黒川利明, 坂井公, 辻順一郎, 近山隆, 高木茂行, 横井俊夫 | 情報処理学会研究報告システムソフトウェアとオペレーティング・システム（OS）,  1984,  11(1984-OS-023), p. 1-10,  1984-06-08 | https://ipsj.ixsq.nii.ac.jp/records/26580 (GET HTTP 200, 61995 bytes; HTML not read) | https://ipsj.ixsq.nii.ac.jp/record/26580/files/IPSJ-OS84023001.pdf | resolved-not-read: range GET HTTP 206, %PDF magic, Content-Range bytes 0-1023/1226838. Open: yes | (from title only, unverified) relevance is the topic of this table: PSI / PSI-II / PSI-III / PSI/UX hardware and firmware |
| 逐次型推論マシン&Psi;のマイクロインタプリタ / Micro-interpreter of the sequential inference machine PSI (my translation; record has no English title) | 山本明, 横田実, 西川宏, 瀧和男, 内田俊一 | 情報処理学会研究報告プログラミング（PRO）,  1984,  41(1984-PRO-029), p. 45-52,  1984-10-11 | https://ipsj.ixsq.nii.ac.jp/records/31384 (GET HTTP 200, 58120 bytes; HTML not read) | https://ipsj.ixsq.nii.ac.jp/record/31384/files/IPSJ-PRO84029007.pdf | resolved-not-read (full GET HTTP 200, %PDF magic, 1308779 bytes, 8 pp, image-only scan; saved, content not read). Open: yes. File `ipsj_31384_IPSJ-PRO84029007.pdf` | (from title only, unverified) Micro-interpreter (firmware) of the original PSI. |
| PSIのガーベッジコレクタ / Garbage Collector on PSI | 西川宏, 池田守宏 | 情報処理学会論文誌,  27,  11, p. 1137-1145,  1986-11-15,ISSN,1882-7764 | https://ipsj.ixsq.nii.ac.jp/records/15599 (GET HTTP 200, 61832 bytes; HTML not read) | https://ipsj.ixsq.nii.ac.jp/record/15599/files/IPSJ-JNL2711012.pdf | resolved-not-read: range GET HTTP 206, %PDF magic, Content-Range bytes 0-1023/675720. Open: yes | (from title only, unverified) Garbage collector of PSI (firmware level). |
| PSIへのコンパイラ向きProlog命令の試験実装と評価 / An Experimental Implementation of a Compiler Target Prolog Instruction Set for the PSI Machine and Its Evaluation | 中島浩, 中島克人, 瀧和男 | 情報処理学会論文誌,  28,  10, p. 1091-1095,  1987-10-15,ISSN,1882-7764 | https://ipsj.ixsq.nii.ac.jp/records/15461 (GET HTTP 200, 64557 bytes; HTML not read) | https://ipsj.ixsq.nii.ac.jp/record/15461/files/IPSJ-JNL2810011.pdf | resolved-not-read: range GET HTTP 206, %PDF magic, Content-Range bytes 0-1023/413017. Open: yes | (from repository abstract, paper not read) A Warren-style compiler-oriented instruction set trial-implemented on the microprogrammed PSI: 1.74-3.36x the original, 114.5 KLIPS. |
| パーソナル逐次型推論マシンPSIの評価　－実行速度とハードウェア各部の性能について－ / Evaluation of the Personal Sequential Inference Machine PSI -Execution Speed and Performance Analysis of the Hardware Components- | 中島浩, 瀧和男, 中島克人, 三石彰純 | 情報処理学会論文誌,  28,  12, p. 1298-1305,  1987-12-15,ISSN,1882-7764 | https://ipsj.ixsq.nii.ac.jp/records/15436 (GET HTTP 200, 69740 bytes; HTML not read) | https://ipsj.ixsq.nii.ac.jp/record/15436/files/IPSJ-JNL2812009.pdf | resolved-not-read: range GET HTTP 206, %PDF magic, Content-Range bytes 0-1023/708659. Open: yes | (from title only, unverified) Evaluation of the original PSI: execution speed and hardware components. |
| PSI-IIの性能評価 : If_Then_Else,Neck_Cut / Performance Evaluation of PSI-II -- If then else &Neck cut optimizeation -- | 立野裕和, 近藤誠一, 中島浩, 池田守宏, 中島克人 | 全国大会講演論文集,  第37回,  プログラミング言語とその処理系, p. 619-620,  1988-09-12 | https://ipsj.ixsq.nii.ac.jp/records/115306 (GET HTTP 200, 68976 bytes; HTML not read) | https://ipsj.ixsq.nii.ac.jp/record/115306/files/KJ00003117847.pdf | resolved-not-read: range GET HTTP 206, %PDF magic, Content-Range bytes 0-1023/177118. Open: yes | (from title only, unverified) relevance is the topic of this table: PSI / PSI-II / PSI-III / PSI/UX hardware and firmware |
| PSI - IIの機械命令セット評価 / Evaluation of instruction set of the PSI - II | 立野裕和, 近藤誠一, 中島浩, 中島克人 | 情報処理学会研究報告計算機アーキテクチャ（ARC）,  1989,  9(1988-ARC-074), p. 1-8,  1989-01-26 | https://ipsj.ixsq.nii.ac.jp/records/24746 (GET HTTP 200, 69178 bytes; HTML not read) | https://ipsj.ixsq.nii.ac.jp/record/24746/files/IPSJ-ARC88074003.pdf | resolved-not-read (full GET HTTP 200, %PDF magic, 1366935 bytes, 8 pp, image-only scan; saved, content not read). Open: yes. File `ipsj_24746_IPSJ-ARC88074003.pdf` | (from title only, unverified) PSI-II machine instruction set evaluation. |
| PSI - IIのメモリ・アーキテクチャ評価 / Evaluation of the PSI - II Memory Architecture | 中島浩, 武田保孝 | 情報処理学会研究報告計算機アーキテクチャ（ARC）,  1990,  7(1989-ARC-080), p. 57-64,  1990-01-25 | https://ipsj.ixsq.nii.ac.jp/records/24677 (GET HTTP 200, 63129 bytes; HTML not read) | https://ipsj.ixsq.nii.ac.jp/record/24677/files/IPSJ-ARC89080008.pdf | resolved-not-read (full GET HTTP 200, %PDF magic, 1026888 bytes, 8 pp, image-only scan; saved, content not read). Open: yes. File `ipsj_24677_IPSJ-ARC89080008.pdf` | (from title only, unverified) PSI-II memory architecture evaluation (cache, address translation); cited by the PIM/m element-processor paper as its design input. |
| 論理型言語指向の推論マシン：4. 逐次型推論マシンのアーキテクチャ / Architecture of Sequential Inference Machines | 金田悠紀夫, 松田秀雄 | 情報処理,  32,  4,  1991-04-15 | https://ipsj.ixsq.nii.ac.jp/records/4701 (GET HTTP 200, 59343 bytes; HTML not read) | https://ipsj.ixsq.nii.ac.jp/record/4701/files/IPSJ-MGN320414.pdf | resolved-not-read: range GET HTTP 206, %PDF magic, Content-Range bytes 0-1023/800081. Open: yes | (from title only, unverified) IPSJ magazine tutorial: sequential inference machine architecture (PSI family among others). |
| AIワークステーションPSI/UXのアーキテクチャ / Architecture of AI Workstation PSI/UX | 益田嘉直, 松本明, 池田守宏 | 情報処理学会研究報告計算機アーキテクチャ（ARC）,  1991,  100(1991-ARC-091), p. 53-60,  1991-11-21 | https://ipsj.ixsq.nii.ac.jp/records/24478 (GET HTTP 200, 66153 bytes; HTML not read) | https://ipsj.ixsq.nii.ac.jp/record/24478/files/IPSJ-ARC91091007.pdf | resolved-not-read: range GET HTTP 206, %PDF magic, Content-Range bytes 0-1023/1015803. Open: yes | (from repository abstract, paper not read) PSI/UX, successor of PSI-II: uses the inference VLSI developed as the PIM/m element processor as its CPU; 1.4 MLIPS. |

#### A9. VPIM, KL1-B abstract machine, distributed KL1 mechanisms (unification, external references, goal control)

| paper (JP title / EN title as given in the repository record) | authors | bibliographic data | landing URL | PDF URL | status (+evidence) | why it matters |
|---|---|---|---|---|---|---|
| 並列推論マシンPIM : 中期PIMの処理方式について / Parallel Inference Machine:PIM : On Execution Mechanism of the Intermediate Stage PIM | 佐藤正俊, 清水肇, 近山隆 | 全国大会講演論文集,  第33回,  アーキテクチャおよびハードウェア, p. 95-96,  1986-10-01 | https://ipsj.ixsq.nii.ac.jp/records/113855 (GET HTTP 200, 63876 bytes; HTML not read) | https://ipsj.ixsq.nii.ac.jp/record/113855/files/KJ00001330661.pdf | resolved-not-read: range GET HTTP 206, %PDF magic, Content-Range bytes 0-1023/258914. Open: yes | (from title only, unverified) relevance is the topic of this table: VPIM, KL1-B abstract machine, distributed KL1 mechanisms (unification, external references, goal control) |
| 核言語KL1分散処理系 : ソフトウェアシミュレータによる評価 / Distributed Imprementation of the KL1 : Evaluation with the Software Simulator | 鳥居悟, 大原有理, 小野越夫 | 全国大会講演論文集,  第33回,  プログラミング言語およびソフトウェア工学, p. 449-450,  1986-10-01 | https://ipsj.ixsq.nii.ac.jp/records/114027 (GET HTTP 200, 63877 bytes; HTML not read) | https://ipsj.ixsq.nii.ac.jp/record/114027/files/KJ00001330833.pdf | resolved-not-read: range GET HTTP 206, %PDF magic, Content-Range bytes 0-1023/145718. Open: yes | (from title only, unverified) relevance is the topic of this table: VPIM, KL1-B abstract machine, distributed KL1 mechanisms (unification, external references, goal control) |
| 制限付きGHCの逐次型処理系 / A Sequential Implementation of GHC subset | 佐藤健 | 全国大会講演論文集,  第33回,  プログラミング言語およびソフトウェア工学, p. 453-454,  1986-10-01 | https://ipsj.ixsq.nii.ac.jp/records/114029 (GET HTTP 200, 56265 bytes; HTML not read) | https://ipsj.ixsq.nii.ac.jp/record/114029/files/KJ00001330835.pdf | resolved-not-read: range GET HTTP 206, %PDF magic, Content-Range bytes 0-1023/146840. Open: yes | (from title only, unverified) relevance is the topic of this table: VPIM, KL1-B abstract machine, distributed KL1 mechanisms (unification, external references, goal control) |
| PIMOSの例外処理方式 / Exception Handling in PIMOS | 越村三幸, 佐藤裕幸, 近山隆, 藤瀬哲朗, 松尾正浩 | 全国大会講演論文集,  第37回,  オペレーティングシステム, p. 249-250,  1988-09-12 | https://ipsj.ixsq.nii.ac.jp/records/115117 (GET HTTP 200, 70258 bytes; HTML not read) | https://ipsj.ixsq.nii.ac.jp/record/115117/files/KJ00003117651.pdf | resolved-not-read: range GET HTTP 206, %PDF magic, Content-Range bytes 0-1023/190476. Open: yes | (from title only, unverified) relevance is the topic of this table: VPIM, KL1-B abstract machine, distributed KL1 mechanisms (unification, external references, goal control) |
| KL1クローズインデキシング方式の評価 / Performance evaluation of KL1 clause indexing. | 西崎慎一郎, 平野喜芳, 武井則雄, 森田京子, 木村康則 | 全国大会講演論文集,  第38回,  ソフトウェア, p. 1005-1006,  1989-03-15 | https://ipsj.ixsq.nii.ac.jp/records/116580 (GET HTTP 200, 69520 bytes; HTML not read) | https://ipsj.ixsq.nii.ac.jp/record/116580/files/KJ00001333323.pdf | resolved-not-read: range GET HTTP 206, %PDF magic, Content-Range bytes 0-1023/161302. Open: yes | (from title only, unverified) relevance is the topic of this table: VPIM, KL1-B abstract machine, distributed KL1 mechanisms (unification, external references, goal control) |
| 密結合マルチプロセッサ上のKL1並列処理系の評価 / Evaluation of KL1 on a shared memory multiprocessor | 細井聡, 小沢年弘, 服部彰 | 全国大会講演論文集,  第38回,  ソフトウェア, p. 1009-1010,  1989-03-15 | https://ipsj.ixsq.nii.ac.jp/records/116582 (GET HTTP 200, 65833 bytes; HTML not read) | https://ipsj.ixsq.nii.ac.jp/record/116582/files/KJ00001333325.pdf | resolved-not-read: range GET HTTP 206, %PDF magic, Content-Range bytes 0-1023/149939. Open: yes | (from title only, unverified) relevance is the topic of this table: VPIM, KL1-B abstract machine, distributed KL1 mechanisms (unification, external references, goal control) |
| 汎用計算機上のKL1処理系　－PDSS－ / The implementation of the KL1 system on the UNIX : PDSS | 平野喜芳, 中越靖行, 西崎慎一郎, 宮崎芳枝, 宮崎敏彦, 近山隆 | 情報処理学会研究報告プログラミング（PRO）,  1989,  50(1989-PRO-021), p. 1-8,  1989-06-13 | https://ipsj.ixsq.nii.ac.jp/records/30973 (GET HTTP 200, 74143 bytes; HTML not read) | https://ipsj.ixsq.nii.ac.jp/record/30973/files/IPSJ-PRO89021001.pdf | resolved-not-read: range GET HTTP 206, %PDF magic, Content-Range bytes 0-1023/1371530. Open: yes | (from title only, unverified) PDSS: KL1 system on general-purpose machines. |
| VPIM及びその開発言語PSLについて / Virtual Parallel Inference Machine and PIM Specification descriptive Language | 中越靖行, 宮崎芳枝, 堂前慶之, 山本礼己, 今井明 | 全国大会講演論文集,  第39回,  ハードウェア, p. 1776-1777,  1989-10-16 | https://ipsj.ixsq.nii.ac.jp/records/117943 (GET HTTP 200, 70008 bytes; HTML not read) | https://ipsj.ixsq.nii.ac.jp/record/117943/files/KJ00003118279.pdf | resolved-not-read (full GET HTTP 200, %PDF magic, 208382 bytes, 2 pp, image-only scan; saved, content not read). Open: yes. File `ipsj_117943_KJ00003118279.pdf` | (from title only, unverified) VPIM and its implementation language PSL. |
| KL1並列処理系の評価－メモリ消費特性とゴミ集め－ / Evaluation of the Parallel KL1 System - Memory Consumption Characteristics and Garbage Collection | 佐藤正俊, 後藤厚宏 | 情報処理学会論文誌,  30,  12, p. 1620-1627,  1989-12-15,ISSN,1882-7764 | https://ipsj.ixsq.nii.ac.jp/records/15125 (GET HTTP 200, 61982 bytes; HTML not read) | https://ipsj.ixsq.nii.ac.jp/record/15125/files/IPSJ-JNL3012012.pdf | resolved-not-read (full GET HTTP 200, %PDF magic, 666432 bytes, 8 pp, image-only scan; saved, content not read). Open: yes. File `ipsj_15125_IPSJ-JNL3012012.pdf` | (from title only, unverified) KL1 parallel system evaluation: memory consumption and GC. |
| 並列マシンにおける言語処理系の開発環境と実装手法　－PIMのKL1言語処理系を例に－ / Developing Environments and Imprementation Techniques for Parallel Language Processor -For example : KL1 Processor in PIM- | 高木常好, 山本礼己, 今井明, 仲瀬明彦, 平野喜芳, 中越靖行 | 情報処理学会研究報告計算機アーキテクチャ（ARC）,  1990,  60(1990-ARC-083), p. 133-138,  1990-07-18 | https://ipsj.ixsq.nii.ac.jp/records/24621 (GET HTTP 200, 76177 bytes; HTML not read) | https://ipsj.ixsq.nii.ac.jp/record/24621/files/IPSJ-ARC90083023.pdf | resolved-not-read (full GET HTTP 200, %PDF magic, 1019758 bytes, 6 pp, image-only scan; saved, content not read). Open: yes. File `ipsj_24621_IPSJ-ARC90083023.pdf` | (from repository abstract, paper not read) PSL, a language designed to describe the PIM KL1 language system, with utilities, an implementation simulator and a compiler to the real machines. |
| メッセージの追い越しがある分散環境における低コストな外部参照管理 / Low-cost external reference management in a distributed environment with message overtaking (my translation; record has no English title) | 六沢一昭, 仲瀬明彦, 川合英夫, 今井明 | 全国大会講演論文集,  第41回,  ソフトウェア, p. 20-21,  1990-09-04 | https://ipsj.ixsq.nii.ac.jp/records/119455 (GET HTTP 200, 58803 bytes; HTML not read) | https://ipsj.ixsq.nii.ac.jp/record/119455/files/KJ00003118551.pdf | resolved-not-read: range GET HTTP 206, %PDF magic, Content-Range bytes 0-1023/170657. Open: yes | (from repository abstract, paper not read) External reference management for the distributed implementation: says weighted reference counting is the known method but costly; exports single-reference data with a plain external address; treats %read/%unify being overtaken by %release. |
| 共有メモリマルチプロセッサにおける効率的なKL1ストリームマージ処理方式 / An efficient KL1 stream-merge scheme on shared-memory multiprocessors (my translation; record has no English title) | 今井明, 稲村雄, 後藤厚宏 | 全国大会講演論文集,  第41回,  ソフトウェア, p. 34-35,  1990-09-04 | https://ipsj.ixsq.nii.ac.jp/records/119462 (GET HTTP 200, 57084 bytes; HTML not read) | https://ipsj.ixsq.nii.ac.jp/record/119462/files/KJ00003118558.pdf | resolved-not-read: range GET HTTP 206, %PDF magic, Content-Range bytes 0-1023/172719. Open: yes | (from title only, unverified) relevance is the topic of this table: VPIM, KL1-B abstract machine, distributed KL1 mechanisms (unification, external references, goal control) |
| 共有メモリ結合マルチプロセッサ上でのKL1処理系のユニフィケーション / Unification in the KL1 system on shared-memory multiprocessors (my translation; record has no English title) |  | 全国大会講演論文集,  第41回,  ソフトウェア, p. 36-37,  1990-09-04 | https://ipsj.ixsq.nii.ac.jp/records/119463 (GET HTTP 200, 50671 bytes; HTML not read) | https://ipsj.ixsq.nii.ac.jp/record/119463/files/KJ00003118559.pdf | resolved-not-read: range GET HTTP 206, %PDF magic, Content-Range bytes 0-1023/174113. Open: yes | (from title only, unverified) relevance is the topic of this table: VPIM, KL1-B abstract machine, distributed KL1 mechanisms (unification, external references, goal control) |
| メッセージの追い越しがある分散環境におけるプロセスの実行停止/再開方式 / An Execution Control for Distributed Processing Systems with Non-FIFO Communication | 六沢一昭, 山本礼己, 川合英夫, 今井明, 仲瀬明彦 | 全国大会講演論文集,  第42回,  ソフトウェア, p. 13-14,  1991-02-25 | https://ipsj.ixsq.nii.ac.jp/records/120346 (GET HTTP 200, 69878 bytes; HTML not read) | https://ipsj.ixsq.nii.ac.jp/record/120346/files/KJ00001341366.pdf | resolved-not-read: range GET HTTP 206, %PDF magic, Content-Range bytes 0-1023/184834. Open: yes | (from title only, unverified) Stopping/resuming distributed processes (shoen control) under message overtaking. |
| クラスタ間メモリ共有型アーキテクチャにおけるKL1処理系の考察 / KL1 System on the Intercluster Shared Memory | 酒井浩, 仲瀬明彦, 武脇敏晃 | 全国大会講演論文集,  第42回,  ハードウェア, p. 29-30,  1991-02-25 | https://ipsj.ixsq.nii.ac.jp/records/120644 (GET HTTP 200, 63880 bytes; HTML not read) | https://ipsj.ixsq.nii.ac.jp/record/120644/files/KJ00001341484.pdf | resolved-not-read: range GET HTTP 206, %PDF magic, Content-Range bytes 0-1023/171669. Open: yes | (from title only, unverified) relevance is the topic of this table: VPIM, KL1-B abstract machine, distributed KL1 mechanisms (unification, external references, goal control) |
| 並列論理型言語KL1のクローズインデキシング方式 / Clause Indexing Scheme for Parallel Logic Programming Language KL1 | 木村康則, 近山隆 | 情報処理学会論文誌,  32,  3, p. 281-295,  1991-03-15,ISSN,1882-7764 | https://ipsj.ixsq.nii.ac.jp/records/14878 (GET HTTP 200, 63411 bytes; HTML not read) | https://ipsj.ixsq.nii.ac.jp/record/14878/files/IPSJ-JNL3203001.pdf | resolved-not-read (full GET HTTP 200, %PDF magic, 1199806 bytes, 15 pp, image-only scan; saved, content not read). Open: yes. File `ipsj_14878_IPSJ-JNL3203001.pdf` | (from title only, unverified) KL1 clause indexing, journal paper. |
| 論理型言語指向の推論マシン：3. 論理型言語の並列処理方式 / Parallel Implementation Schemes of Logic Programming Languagws | 市吉伸行 | 情報処理,  32,  4,  1991-04-15 | https://ipsj.ixsq.nii.ac.jp/records/4700 (GET HTTP 200, 56087 bytes; HTML not read) | https://ipsj.ixsq.nii.ac.jp/record/4700/files/IPSJ-MGN320413.pdf | resolved-not-read: range GET HTTP 206, %PDF magic, Content-Range bytes 0-1023/1655764. Open: yes | (from title only, unverified) IPSJ magazine tutorial: parallel execution of logic languages (KL1 on Multi-PSI/PIM). |
| ブロードキャストとWTC方式を用いた分散プロセス制御方式 / A Scheme for State Change in a Distributed Environment Using Broadcast and Weighted Throw Counting | 六沢一昭, 市吉伸行 | 情報処理学会論文誌,  33,  3, p. 320-329,  1992-03-15,ISSN,1882-7764 | https://ipsj.ixsq.nii.ac.jp/records/14721 (GET HTTP 200, 62586 bytes; HTML not read) | https://ipsj.ixsq.nii.ac.jp/record/14721/files/IPSJ-JNL3303008.pdf | resolved-not-read: range GET HTTP 206, %PDF magic, Content-Range bytes 0-1023/851889. Open: yes | (from repository abstract, paper not read) Forced termination, stop/resume and state change of process groups by broadcast, with completion confirmed by WTC (Weighted Throw Counting, spelled out in the abstract). |
| PortableなKL1処理系の構想 / Plan for a portable implementation of KL1 | 関田大吾, 近山隆 | 情報処理学会研究報告プログラミング（PRO）,  1992,  67(1992-PRO-008), p. 123-130,  1992-08-20 | https://ipsj.ixsq.nii.ac.jp/records/30643 (GET HTTP 200, 61566 bytes; HTML not read) | https://ipsj.ixsq.nii.ac.jp/record/30643/files/IPSJ-PRO92008016.pdf | resolved-not-read: range GET HTTP 206, %PDF magic, Content-Range bytes 0-1023/1149272. Open: yes | (from title only, unverified) relevance is the topic of this table: VPIM, KL1-B abstract machine, distributed KL1 mechanisms (unification, external references, goal control) |
| 分散環境におけるデッドロックのWTC方式を用いた検出方式 / Distributed Deadlock Detection Using Weighted Throw Counting | 六沢一昭, 近山隆, 市吉伸行 | 全国大会講演論文集,  第47回,  ソフトウェア, p. 25-26,  1993-09-27 | https://ipsj.ixsq.nii.ac.jp/records/124525 (GET HTTP 200, 62908 bytes; HTML not read) | https://ipsj.ixsq.nii.ac.jp/record/124525/files/KJ00001339220.pdf | resolved-not-read: range GET HTTP 206, %PDF magic, Content-Range bytes 0-1023/161756. Open: yes | (from repository abstract, paper not read) Deadlock detection in an asynchronous distributed environment using the WTC termination-detection scheme. |
| ごみ集めの基礎と最近の動向：6. 分散ごみ集め / Distributed Garbage Collection | 市吉伸行 | 情報処理,  35,  11,  1994-11-15 | https://ipsj.ixsq.nii.ac.jp/records/4003 (GET HTTP 200, 55964 bytes; HTML not read) | https://ipsj.ixsq.nii.ac.jp/record/4003/files/IPSJ-MGN351110.pdf | resolved-not-read: range GET HTTP 206, %PDF magic, Content-Range bytes 0-1023/685604. Open: yes | (from title only, unverified) Survey of distributed garbage collection by Ichiyoshi (covers weighted reference counting schemes). |

#### A10. Garbage collection / MRB / LRC

| paper (JP title / EN title as given in the repository record) | authors | bibliographic data | landing URL | PDF URL | status (+evidence) | why it matters |
|---|---|---|---|---|---|---|
| LRCによる多重参照管理方式 / Multiple Reference Management by LRC | 後藤厚宏, 近山隆 | 全国大会講演論文集,  第37回,  プログラミング言語とその処理系, p. 691-692,  1988-09-12 | https://ipsj.ixsq.nii.ac.jp/records/115343 (GET HTTP 200, 61658 bytes; HTML not read) | https://ipsj.ixsq.nii.ac.jp/record/115343/files/KJ00003117884.pdf | resolved-not-read: range GET HTTP 206, %PDF magic, Content-Range bytes 0-1023/185082. Open: yes | (from title only, unverified) LRC multiple-reference management scheme (an MRB alternative). |
| LRCのためのオブジェクト・コード / Object Code for LRC | 関田大吾, 木村康則 | 全国大会講演論文集,  第37回,  プログラミング言語とその処理系, p. 693-694,  1988-09-12 | https://ipsj.ixsq.nii.ac.jp/records/115344 (GET HTTP 200, 59767 bytes; HTML not read) | https://ipsj.ixsq.nii.ac.jp/record/115344/files/KJ00003117885.pdf | resolved-not-read: range GET HTTP 206, %PDF magic, Content-Range bytes 0-1023/168345. Open: yes | (from title only, unverified) Object code for LRC. |
| LRCによるインクリメンタルGCの評価 / Evaluation of the Incremental GC by LRC | 宮内信仁, 中川貴之 | 全国大会講演論文集,  第37回,  プログラミング言語とその処理系, p. 695-696,  1988-09-12 | https://ipsj.ixsq.nii.ac.jp/records/115345 (GET HTTP 200, 59388 bytes; HTML not read) | https://ipsj.ixsq.nii.ac.jp/record/115345/files/KJ00003117886.pdf | resolved-not-read: range GET HTTP 206, %PDF magic, Content-Range bytes 0-1023/159212. Open: yes | (from title only, unverified) Evaluation of incremental GC by LRC. |
| 並列論理型言語KL1の多重参照管理によるガーベジコレクション / Incremental Grabage Collection by Multiple Reference Management of Data Objects in KL1 | 木村康則, 近山隆, 武井則雄 | 情報処理学会研究報告プログラミング（PRO）,  1989,  84(1989-PRO-022), p. 1-10,  1989-10-05 | https://ipsj.ixsq.nii.ac.jp/records/30949 (GET HTTP 200, 66221 bytes; HTML not read) | https://ipsj.ixsq.nii.ac.jp/record/30949/files/IPSJ-PRO89022001.pdf | resolved-not-read (full GET HTTP 200, %PDF magic, 1613171 bytes, 10 pp, image-only scan; saved, content not read). Open: yes. File `ipsj_30949_IPSJ-PRO89022001.pdf` | (from title only, unverified) MRB (multiple reference bit) incremental GC, SIG-PRO version of the journal paper. |
| 共有メモリ結合マルチプロッセサにおけるKL1向きガーベジコレクション : MRBを用いた最適化と並列実行 / Garbage Collection for KL1 on Shared Memory Multi-Processor : Optimization by MRB and Parallel Execution | 今井明, 川合英夫, 中川貴之, 中島克人, 後藤厚宏 | 全国大会講演論文集,  第39回,  ソフトウェア, p. 1281-1282,  1989-10-16 | https://ipsj.ixsq.nii.ac.jp/records/117691 (GET HTTP 200, 70657 bytes; HTML not read) | https://ipsj.ixsq.nii.ac.jp/record/117691/files/KJ00001335964.pdf | resolved-not-read: range GET HTTP 206, %PDF magic, Content-Range bytes 0-1023/181132. Open: yes | (from title only, unverified) KL1 GC on shared-memory multiprocessors: MRB optimisation and parallel execution. |
| MRB-GCの評価 : アクティブセル量とヒープ消費 / Evaluation of MRB-GC : Active Cells and Heap Consumption | 武井則雄, 平野喜芳, 西崎慎一郎, 森田京子, 木村康則, 近山隆 | 全国大会講演論文集,  第39回,  ソフトウェア, p. 1287-1288,  1989-10-16 | https://ipsj.ixsq.nii.ac.jp/records/117694 (GET HTTP 200, 72955 bytes; HTML not read) | https://ipsj.ixsq.nii.ac.jp/record/117694/files/KJ00001335967.pdf | resolved-not-read: range GET HTTP 206, %PDF magic, Content-Range bytes 0-1023/193236. Open: yes | (from title only, unverified) MRB-GC evaluation: active cells and heap consumption. |
| 共有メモリ結合マルチプロセッサにおけるKL1向き並列実行GC方式の評価 / Evaluation of a Parallel GC scheme for KL1 on Shared Memory Multi - Processor | 今井明, 宮崎芳枝, 中島克人, 後藤厚宏 | 情報処理学会研究報告計算機アーキテクチャ（ARC）,  1989,  99(1989-ARC-079), p. 49-56,  1989-11-20 | https://ipsj.ixsq.nii.ac.jp/records/24693 (GET HTTP 200, 69311 bytes; HTML not read) | https://ipsj.ixsq.nii.ac.jp/record/24693/files/IPSJ-ARC89079007.pdf | resolved-not-read (full GET HTTP 200, %PDF magic, 1062373 bytes, 8 pp, image-only scan; saved, content not read). Open: yes. File `ipsj_24693_IPSJ-ARC89079007.pdf` | (from title only, unverified) Parallel GC for KL1 on shared-memory clusters (ARC version of the journal paper). |
| 共有メモリマルチプロセッサにおけるガーベジコレクションの並列実行と評価 / Parallel Garbage Collection on a Shared Memory MultiProcessor and Its Evaluation | 今井明, エヴァンティック, 中島克人, 後藤厚宏 | 情報処理学会論文誌,  33,  3, p. 298-306,  1992-03-15,ISSN,1882-7764 | https://ipsj.ixsq.nii.ac.jp/records/14719 (GET HTTP 200, 68374 bytes; HTML not read) | https://ipsj.ixsq.nii.ac.jp/record/14719/files/IPSJ-JNL3303006.pdf | resolved-not-read (full GET HTTP 200, %PDF magic, 734689 bytes, 9 pp, image-only scan; saved, content not read). Open: yes. File `ipsj_14719_IPSJ-JNL3303006.pdf` | (from title only, unverified) Parallel GC on shared-memory multiprocessor (PIM cluster), journal paper. |

#### A11. PIMOS

| paper (JP title / EN title as given in the repository record) | authors | bibliographic data | landing URL | PDF URL | status (+evidence) | why it matters |
|---|---|---|---|---|---|---|
| PIMOSの設計方針 / Design Principle of the PIMOS | 佐藤裕幸, 越村三幸, 近山隆, 藤瀬哲朗, 松尾正浩, 和田久美子 | 全国大会講演論文集,  第37回,  オペレーティングシステム, p. 247-248,  1988-09-12 | https://ipsj.ixsq.nii.ac.jp/records/115116 (GET HTTP 200, 72998 bytes; HTML not read) | https://ipsj.ixsq.nii.ac.jp/record/115116/files/KJ00003117650.pdf | resolved-not-read: range GET HTTP 206, %PDF magic, Content-Range bytes 0-1023/239730. Open: yes | (from title only, unverified) relevance is the topic of this table: PIMOS |
| PIMOSの階層的資源管理 / Hierarchical Resource Management on PIMOS | 藤瀬哲朗, 佐藤裕幸, 近山隆 | 全国大会講演論文集,  第37回,  オペレーティングシステム, p. 251-252,  1988-09-12 | https://ipsj.ixsq.nii.ac.jp/records/115118 (GET HTTP 200, 63286 bytes; HTML not read) | https://ipsj.ixsq.nii.ac.jp/record/115118/files/KJ00003117652.pdf | resolved-not-read: range GET HTTP 206, %PDF magic, Content-Range bytes 0-1023/190714. Open: yes | (from title only, unverified) relevance is the topic of this table: PIMOS |
| PIMOS上でのシェルの実現 : 共有資源管理 / 'SHELL', Implemantation on PIMOS | 松尾正浩, 藤瀬哲朗, 佐藤裕幸, 近山隆 | 全国大会講演論文集,  第37回,  オペレーティングシステム, p. 253-254,  1988-09-12 | https://ipsj.ixsq.nii.ac.jp/records/115119 (GET HTTP 200, 66129 bytes; HTML not read) | https://ipsj.ixsq.nii.ac.jp/record/115119/files/KJ00003117653.pdf | resolved-not-read: range GET HTTP 206, %PDF magic, Content-Range bytes 0-1023/201216. Open: yes | (from title only, unverified) relevance is the topic of this table: PIMOS |
| PIMOSのトレーサ / Tracer on PIMOS | 中尾浩一, 近山隆, 中島克人, 大西諭 | 全国大会講演論文集,  第39回,  ソフトウェア, p. 1135-1136,  1989-10-16 | https://ipsj.ixsq.nii.ac.jp/records/117618 (GET HTTP 200, 65859 bytes; HTML not read) | https://ipsj.ixsq.nii.ac.jp/record/117618/files/KJ00001335891.pdf | resolved-not-read: range GET HTTP 206, %PDF magic, Content-Range bytes 0-1023/172402. Open: yes | (from title only, unverified) relevance is the topic of this table: PIMOS |
| PIMOSの評価 / Evaluation of the PIMOS | 佐藤裕幸, 星田昌紀, 近山隆, 藤瀬哲朗 | 全国大会講演論文集,  第39回,  ソフトウェア, p. 1189-1190,  1989-10-16 | https://ipsj.ixsq.nii.ac.jp/records/117645 (GET HTTP 200, 66565 bytes; HTML not read) | https://ipsj.ixsq.nii.ac.jp/record/117645/files/KJ00001335918.pdf | resolved-not-read: range GET HTTP 206, %PDF magic, Content-Range bytes 0-1023/207296. Open: yes | (from title only, unverified) relevance is the topic of this table: PIMOS |
| PIMOSのセルフ・コンパイラ / Implementing KL1 self compiler on PIMOS | 佐藤令子, 掘敦史, 関田大吾, 近山隆 | 全国大会講演論文集,  第39回,  ソフトウェア, p. 1330-1331,  1989-10-16 | https://ipsj.ixsq.nii.ac.jp/records/117716 (GET HTTP 200, 66727 bytes; HTML not read) | https://ipsj.ixsq.nii.ac.jp/record/117716/files/KJ00001335989.pdf | resolved-not-read: range GET HTTP 206, %PDF magic, Content-Range bytes 0-1023/151697. Open: yes | (from title only, unverified) relevance is the topic of this table: PIMOS |
| PIMOSの資源管理方式 / Resource Management of PIMOS | 佐藤裕幸, 越村三幸, 近山隆, 藤瀬哲朗, 松尾正浩, 和田久美子 | 情報処理学会論文誌,  30,  12, p. 1646-1655,  1989-12-15,ISSN,1882-7764 | https://ipsj.ixsq.nii.ac.jp/records/15128 (GET HTTP 200, 75208 bytes; HTML not read) | https://ipsj.ixsq.nii.ac.jp/record/15128/files/IPSJ-JNL3012015.pdf | resolved-not-read (full GET HTTP 200, %PDF magic, 986050 bytes, 10 pp, image-only scan; saved, content not read). Open: yes. File `ipsj_15128_IPSJ-JNL3012015.pdf` | (from title only, unverified) PIMOS resource management, journal paper. |
| 並列論理型言語KL1によるオペレーティングシステムPIMOSの実現について / Implementation of PIMOS in a Concurrent Logic Programming Language KL1 | 藤瀬哲朗, 屋代寛, 近山隆 | 情報処理学会研究報告システムソフトウェアとオペレーティング・システム（OS）,  1992,  65(1992-OS-056), p. 49-56,  1992-08-20 | https://ipsj.ixsq.nii.ac.jp/records/26332 (GET HTTP 200, 66181 bytes; HTML not read) | https://ipsj.ixsq.nii.ac.jp/record/26332/files/IPSJ-OS92056007.pdf | resolved-not-read: range GET HTTP 206, %PDF magic, Content-Range bytes 0-1023/1203822. Open: yes | (from title only, unverified) PIMOS implemented in KL1. |

#### A12. PIM general, load balancing, other

| paper (JP title / EN title as given in the repository record) | authors | bibliographic data | landing URL | PDF URL | status (+evidence) | why it matters |
|---|---|---|---|---|---|---|
| 並列推論マシン / Parallel inference machines (my translation; record has no English title) | 田中英彦 | 情報処理学会研究報告計算機アーキテクチャ（ARC）,  1984,  78(1984-ARC-057), p. 1-8,  1985-03-28 | https://ipsj.ixsq.nii.ac.jp/records/24981 (GET HTTP 200, 53195 bytes; HTML not read) | https://ipsj.ixsq.nii.ac.jp/record/24981/files/IPSJ-ARC84057003.pdf | resolved-not-read: range GET HTTP 206, %PDF magic, Content-Range bytes 0-1023/1362367. Open: yes | (from title only, unverified) relevance is the topic of this table: PIM general, load balancing, other |
| 並列推論マシンPIM : 中期構想 / Parallel Inference Machine:PIM : Intermediate Stage Plan | 後藤厚宏, 杉江衛, 服部彰, 伊藤徳義, 内田俊一 | 全国大会講演論文集,  第33回,  アーキテクチャおよびハードウェア, p. 91-92,  1986-10-01 | https://ipsj.ixsq.nii.ac.jp/records/113853 (GET HTTP 200, 69280 bytes; HTML not read) | https://ipsj.ixsq.nii.ac.jp/record/113853/files/KJ00001330659.pdf | resolved-not-read: range GET HTTP 206, %PDF magic, Content-Range bytes 0-1023/205850. Open: yes | (from title only, unverified) relevance is the topic of this table: PIM general, load balancing, other |
| 並列推論マシンPIM : 中期PIMのハードウェア構成について / Parallel Inference Machine:PIM : On Hardware Configuration of the Intermediate Stage PIM | 松本明, 六沢一昭, 後藤厚宏 | 全国大会講演論文集,  第33回,  アーキテクチャおよびハードウェア, p. 93-94,  1986-10-01 | https://ipsj.ixsq.nii.ac.jp/records/113854 (GET HTTP 200, 63954 bytes; HTML not read) | https://ipsj.ixsq.nii.ac.jp/record/113854/files/KJ00001330660.pdf | resolved-not-read: range GET HTTP 206, %PDF magic, Content-Range bytes 0-1023/180217. Open: yes | (from title only, unverified) relevance is the topic of this table: PIM general, load balancing, other |
| 並列推論マシンPIM : ストリームの効率的実現方式 / Parallel Inference Machine:PIM : an Efficient Stream Implementation | 久野英治, 伊藤徳義, 佐藤正俊 | 全国大会講演論文集,  第33回,  アーキテクチャおよびハードウェア, p. 97-98,  1986-10-01 | https://ipsj.ixsq.nii.ac.jp/records/113856 (GET HTTP 200, 62758 bytes; HTML not read) | https://ipsj.ixsq.nii.ac.jp/record/113856/files/KJ00001330662.pdf | resolved-not-read: range GET HTTP 206, %PDF magic, Content-Range bytes 0-1023/196981. Open: yes | (from title only, unverified) relevance is the topic of this table: PIM general, load balancing, other |
| 並列推論マシンPIM: リダクション方式の評価 / PIM Evaluation of Reduction-Based Parallel Inference Machine | 杉江衛, 米山貢, 岩崎正明, 菅谷正弘, 清水肇, 松本明 | 全国大会講演論文集,  第33回,  アーキテクチャおよびハードウェア, p. 99-100,  1986-10-01 | https://ipsj.ixsq.nii.ac.jp/records/113857 (GET HTTP 200, 72164 bytes; HTML not read) | https://ipsj.ixsq.nii.ac.jp/record/113857/files/KJ00001330663.pdf | resolved-not-read: range GET HTTP 206, %PDF magic, Content-Range bytes 0-1023/149673. Open: yes | (from title only, unverified) relevance is the topic of this table: PIM general, load balancing, other |
| Efficient Stream Processing in GHC and Its Evaluation on a Parallel Inference Machine / Efficient Stream Processing in GHC and Its Evaluation on a Parallel Inference Machine | Noriyoshi, Ito, Eiji, Kuno, Teruhiko, Oohara, Noriyoshi, Ito, Eiji, Kuno, Teruhiko, Oohara | Journal of Information Processing ,  10,  4, p. 237-244,  1988-03-10,ISSN,1882-6652 | https://ipsj.ixsq.nii.ac.jp/records/59818 (GET HTTP 200, 65801 bytes; HTML not read) | https://ipsj.ixsq.nii.ac.jp/record/59818/files/IPSJ-JIP1004004.pdf | resolved-not-read: range GET HTTP 206, %PDF magic, Content-Range bytes 0-1023/1003335. Open: yes | (from title only, unverified) relevance is the topic of this table: PIM general, load balancing, other |
| 並列推論マシンに於ける負荷分散方式の評価 / An Evaluation of the Load Balancing Mechanism for a Parallel Inference Machine | 山内宗, 田中英彦 | 情報処理学会研究報告計算機アーキテクチャ（ARC）,  1988,  45(1988-ARC-071), p. 125-132,  1988-07-07 | https://ipsj.ixsq.nii.ac.jp/records/24790 (GET HTTP 200, 62230 bytes; HTML not read) | https://ipsj.ixsq.nii.ac.jp/record/24790/files/IPSJ-ARC88071017.pdf | resolved-not-read: range GET HTTP 206, %PDF magic, Content-Range bytes 0-1023/966381. Open: yes | (from title only, unverified) relevance is the topic of this table: PIM general, load balancing, other |
| KL1のデバッグサポート機能 / Debugging support tools for KLl. | 平野喜芳, 中越靖行, 宮崎芳枝, 西崎慎一郎, 木村康則 | 全国大会講演論文集,  第37回,  ソフトウェア工学, p. 744-745,  1988-09-12 | https://ipsj.ixsq.nii.ac.jp/records/115371 (GET HTTP 200, 69530 bytes; HTML not read) | https://ipsj.ixsq.nii.ac.jp/record/115371/files/KJ00001331354.pdf | resolved-not-read: range GET HTTP 206, %PDF magic, Content-Range bytes 0-1023/220105. Open: yes | (from title only, unverified) relevance is the topic of this table: PIM general, load balancing, other |
| PIMにおける負荷分散方式 : 動的負荷分散方式のプロセッサ数依存性の評価 / Load-Dispatching Strategy in PIMs | 井門徳安, 杉江衛, 垂井俊明 | 全国大会講演論文集,  第38回,  ハードウェア, p. 1560,  1989-03-15 | https://ipsj.ixsq.nii.ac.jp/records/116862 (GET HTTP 200, 62908 bytes; HTML not read) | https://ipsj.ixsq.nii.ac.jp/record/116862/files/KJ00003118019.pdf | resolved-not-read: range GET HTTP 206, %PDF magic, Content-Range bytes 0-1023/87002. Open: yes | (from title only, unverified) relevance is the topic of this table: PIM general, load balancing, other |
| 並列論理型言語によるOSの記述 / An Operating System Written in a Concurrent Logic Programming Language | 越村三幸, 近山隆, 佐藤裕幸, 藤瀬哲朗, 松尾正浩, 和田久美子 | 情報処理学会研究報告プログラミング（PRO）,  1989,  42(1989-PRO-029), p. 11-19,  1989-05-18 | https://ipsj.ixsq.nii.ac.jp/records/30981 (GET HTTP 200, 73473 bytes; HTML not read) | https://ipsj.ixsq.nii.ac.jp/record/30981/files/IPSJ-PRO89029002.pdf | resolved-not-read: range GET HTTP 206, %PDF magic, Content-Range bytes 0-1023/1563909. Open: yes | (from title only, unverified) relevance is the topic of this table: PIM general, load balancing, other |
| 疎結合並列計算機上でのOR並列問題に適した動的負荷分散方式とその評価 / An Efficient Dynamic Load Balancing Scheme for OR - Parallel Problems on Loosely - Coupled Multiprocessor and its Evaluation | 古市昌一, 瀧和男, 市吉伸行 | 情報処理学会研究報告計算機アーキテクチャ（ARC）,  1989,  99(1989-ARC-079), p. 73-81,  1989-11-20 | https://ipsj.ixsq.nii.ac.jp/records/24696 (GET HTTP 200, 67039 bytes; HTML not read) | https://ipsj.ixsq.nii.ac.jp/record/24696/files/IPSJ-ARC89079010.pdf | resolved-not-read: range GET HTTP 206, %PDF magic, Content-Range bytes 0-1023/1513388. Open: yes | (from repository abstract, paper not read) Dynamic load balancing for OR-parallel search on a loosely coupled machine (Multi-PSI named in abstract). |
| 論理型言語指向の推論マシン：5. 並列型推論マシンのアーキテクチャ / Parallel Inference Machine Architectures | 後藤厚宏 | 情報処理,  32,  4,  1991-04-15 | https://ipsj.ixsq.nii.ac.jp/records/4702 (GET HTTP 200, 56088 bytes; HTML not read) | https://ipsj.ixsq.nii.ac.jp/record/4702/files/IPSJ-MGN320415.pdf | resolved-not-read: range GET HTTP 206, %PDF magic, Content-Range bytes 0-1023/1077202. Open: yes | (from title only, unverified) IPSJ magazine tutorial: parallel inference machine architecture. |
| 並列論理型言語KL1のデバッグ環境 / Debugging Facilities for KL1 | 中尾浩一, 和田久美子, 清原良三, 近山隆 | 情報処理学会研究報告プログラミング（PRO）,  1992,  67(1992-PRO-008), p. 131-138,  1992-08-20 | https://ipsj.ixsq.nii.ac.jp/records/30644 (GET HTTP 200, 68003 bytes; HTML not read) | https://ipsj.ixsq.nii.ac.jp/record/30644/files/IPSJ-PRO92008017.pdf | resolved-not-read: range GET HTTP 206, %PDF magic, Content-Range bytes 0-1023/1134981. Open: yes | (from title only, unverified) relevance is the topic of this table: PIM general, load balancing, other |
| KL1負荷分散ライブラリの試作 / Development of An Experimental Load Distribution Library for KL1 | 市吉伸行 | 全国大会講演論文集,  第46回,  ソフトウェア, p. 41-42,  1993-03-01 | https://ipsj.ixsq.nii.ac.jp/records/123655 (GET HTTP 200, 56691 bytes; HTML not read) | https://ipsj.ixsq.nii.ac.jp/record/123655/files/KJ00001337497.pdf | resolved-not-read: range GET HTTP 206, %PDF magic, Content-Range bytes 0-1023/169643. Open: yes | (from title only, unverified) relevance is the topic of this table: PIM general, load balancing, other |
| 疎結合型マルチプロセッサ上の拡散型動的負荷分散方式　－LLS ? G方式－ / A Diffusional Load Balancing Scheme on Loosely Coupled Multi -Processors- LLS -G- | 佐藤令子, 佐藤裕幸, 中島克人, 田中千代治 | 情報処理学会論文誌,  35,  4, p. 571-580,  1994-04-15,ISSN,1882-7764 | https://ipsj.ixsq.nii.ac.jp/records/14257 (GET HTTP 200, 69321 bytes; HTML not read) | https://ipsj.ixsq.nii.ac.jp/record/14257/files/IPSJ-JNL3504009.pdf | resolved-not-read: range GET HTTP 206, %PDF magic, Content-Range bytes 0-1023/1056454. Open: yes | (from repository abstract, paper not read) LLS-G diffusion-type dynamic load balancing for loosely coupled multiprocessors (abstract mentions PIM). |
| 共有メモリ並列マシン上の細粒度自動負荷分散方式の評価 / Evaluation of Fine - Grain Automatic Load Balancing Method on the Shared Memory Parallel Machine | 畑澤宏善 | 情報処理学会論文誌,  35,  10, p. 2069-2077,  1994-10-15,ISSN,1882-7764 | https://ipsj.ixsq.nii.ac.jp/records/14111 (GET HTTP 200, 59355 bytes; HTML not read) | https://ipsj.ixsq.nii.ac.jp/record/14111/files/IPSJ-JNL3510013.pdf | resolved-not-read: range GET HTTP 206, %PDF magic, Content-Range bytes 0-1023/852091. Open: yes | (from repository abstract, paper not read) Fine-grain automatic load balancing inside an 8-PE cluster, evaluated with the KL1 system on PIM/p. |
| 並列推論マシンPIMの単体プロセッサの評価 / Evaluation of an Elementaly Processor of Prarllel Inference Machine | 久門耕一 | 情報処理学会研究報告計算機アーキテクチャ（ARC）,  1995,  60(1995-ARC-112), p. 65-72,  1995-06-23 | https://ipsj.ixsq.nii.ac.jp/records/24141 (GET HTTP 200, 59670 bytes; HTML not read) | https://ipsj.ixsq.nii.ac.jp/record/24141/files/IPSJ-ARC95112009.pdf | resolved-not-read: range GET HTTP 206, %PDF magic, Content-Range bytes 0-1023/667079. Open: yes | (from title only, unverified) relevance is the topic of this table: PIM general, load balancing, other |

#### B. J-STAGE (survey-level articles; all five PDFs fetched by full GET)

| paper (JP title / EN translation) | authors | bibliographic data | landing URL | PDF URL | status (+evidence) | why it matters |
|---|---|---|---|---|---|---|
| 並列推論マシンPIM / The Parallel Inference Machine (PIM) (English title printed on the paper) | 市吉伸行, 後藤厚宏, 近山隆 | 人工知能 (J. JSAI) 4(3), 265-271, 1989 | https://www.jstage.jst.go.jp/article/jjsai/4/3/4_265/_article/-char/ja/ | https://www.jstage.jst.go.jp/article/jjsai/4/3/4_265/_pdf | **opened-and-read** (first page only): GET HTTP 200 `application/pdf`, %PDF magic, 651263 bytes, 7 pp; has a text layer; title, authors, ICOT affiliation and keywords confirmed with `pdftotext`. Open: yes. File `jstage_jjsai_4_3_265.pdf` | ICOT overview of PIM by three of the KL1 implementers; keywords include metaprogramming, network-connected multiprocessor, parallel implementation |
| 逐次型Prologマシン / Sequential Prolog machines (my translation) | 横田実 | 人工知能 2(4), 441-449, 1987 | https://www.jstage.jst.go.jp/article/jjsai/2/4/2_441/_article/-char/ja/ | https://www.jstage.jst.go.jp/article/jjsai/2/4/2_441/_pdf | resolved-not-read: GET HTTP 200 `application/pdf`, %PDF magic, 648084 bytes (not kept). Open: yes | Survey; matched the full-text query マルチPSI |
| 並列推論マシン / Parallel inference machines (my translation) | 内田俊一 | 人工知能 2(4), 450-458, 1987 | https://www.jstage.jst.go.jp/article/jjsai/2/4/2_450/_article/-char/ja/ | https://www.jstage.jst.go.jp/article/jjsai/2/4/2_450/_pdf | resolved-not-read: GET HTTP 200, %PDF magic, 612381 bytes (not kept). Open: yes | ICOT survey of PIM plans at the Multi-PSI stage |
| 推論マシン / Inference machines (my translation) | 横田実, 内田俊一 | 計測と制御 25(4), 355-361, 1986 | https://www.jstage.jst.go.jp/article/sicejl1962/25/4/25_4_355/_article/-char/ja/ | https://www.jstage.jst.go.jp/article/sicejl1962/25/4/25_4_355/_pdf | resolved-not-read: GET HTTP 200, %PDF magic, 955479 bytes (not kept). Open: yes | Survey of PSI-era inference machines |
| 並列推論マシン上のLSI-CADプログラム / LSI-CAD programs on parallel inference machines (my translation) | 瀧和男 | 人工知能 8(2), 159-165, 1993 | https://www.jstage.jst.go.jp/article/jjsai/8/2/8_159/_article/-char/ja/ | https://www.jstage.jst.go.jp/article/jjsai/8/2/8_159/_pdf | resolved-not-read: GET HTTP 200, %PDF magic, 547219 bytes (not kept). Open: yes | Application-level; low priority |

J-STAGE holds no IPSJ or IEICE Transactions for this period; nothing on firmware internals was found there.

#### C. Exists or is cited, but could not be opened (bibliographic records only)

Source for every row: CiNii Research OpenSearch JSON (`https://cir.nii.ac.jp/opensearch/articles?q=...&format=json`). The CiNii record pages themselves were not opened; the records carry no full-text link. Status for all rows: **cited-only**. English renderings of titles here are my translations.

| paper | authors (as in CiNii) | bibliographic data | CiNii record | why it matters |
|---|---|---|---|---|
| 並列推論マシン(PIM/m)用VLSI / VLSI for the parallel inference machine PIM/m | 古谷 清広 (first author) | 三菱電機技報 65(11), pp 1158-1162, 1991 | https://cir.nii.ac.jp/crid/1520854805941911424 | Mitsubishi house-journal article on the PIM/m VLSI (from title only) |
| 並列推論マシンPIMのアーキテクチャ / Architecture of the parallel inference machine PIM | 中島 克人 (first author) | 三菱電機技報 66(6), pp 682-686, 1992 | https://cir.nii.ac.jp/crid/1523669555466075136 | Mitsubishi house-journal article on PIM architecture (from title only) |
| (財)新世代コンピュータ技術開発機構向けマルチPSIシステム / The Multi-PSI system for ICOT | 益田 嘉直 (first author) | 三菱電機技報 62(12), pp 1100-1105, 1988 | https://cir.nii.ac.jp/crid/1523106604524439552 | Mitsubishi house-journal article on the Multi-PSI system delivered to ICOT (from title only; version not stated in the record) |
| 三菱AIワークステーション《MELCOM PSI/UXシリーズ》のハードウェアシステム / Hardware of the MELCOM PSI/UX AI workstation | 益田 嘉直 (first author) | 三菱電機技報 65(6), pp 602-607, 1991 | https://cir.nii.ac.jp/crid/1520573330965152896 | PSI/UX hardware (from title only) |
| マルチPSI(プサイ)(並列推論マシン)システムの開発を見る / A look at the development of the Multi-PSI system | 益田 嘉直, 内田 俊一 | エレクトロニクス 34(4), pp 61-64, 1989 | https://cir.nii.ac.jp/crid/1520291855512132736 | Trade-magazine article |
| 並列論理型言語KL1の実現方式と並列OSの記術 / Implementation of KL1 and description of a parallel OS | 宮崎 敏彦 | 電子情報通信学会論文誌 D, 71(8), pp 1423-1432, 1988 | https://cir.nii.ac.jp/crid/1520853832424936192 | IEICE Transactions paper on KL1 implementation (from title only) |
| マルチPSIにおける並列処理とその評価 -- 小粒度高並列オブジェクトモデルに基づくパラダイムについて / Parallel processing on the Multi-PSI and its evaluation | 滝 和男, 市吉 伸行 | 電子情報通信学会論文誌 D-I, 75(8), pp 723-739, 1992 | https://cir.nii.ac.jp/crid/1520009410307993216 | Long evaluation paper; an English translation exists in Systems and Computers in Japan 25 (1994) 17-36, doi 10.1002/scj.4690250102 (CiNii record 1870587968348300032, not opened) |
| 並列推論マシンPIM/cにおける自動負荷分散支援機構 / Automatic load-balancing support mechanism in PIM/c | 中川貴之 | 信学技報 CPSY91-9, 1991 | https://cir.nii.ac.jp/crid/1571980076614278912 | PIM/c load-balancing support mechanism (from title only) |
| 並列推論マシンPIMにおける抽象機械語KL1-Bの実装 - 高級機械語を実装するための道具立 - / Implementing the abstract machine language KL1-B on PIM | 山本 (first author) | 信学技報, 1989 (no number in the record). The PIM/c firmware paper I read cites the same title as 並列処理に関する指宿ミニシンポジウム, 1989 | https://cir.nii.ac.jp/crid/1571980074519825152 | Title says it is about implementing KL1-B on PIM; cited as reference [4] (VPIM) by the PIM/c firmware paper I read; not found online |
| 並列推論マシンPIM/pにおけるクラスタ内自動負荷分散方式の評価 / Evaluation of intra-cluster automatic load balancing on PIM/p | 畑澤宏善 | 並列処理シンポジウム JSPP'93 論文集, pp 355-362 | https://cir.nii.ac.jp/crid/1572824500576906112 | PIM/p evaluation |
| LSI配線プログラムを用いた並列推論マシンPIM/cの負荷分散方式の評価 / Evaluation of PIM/c load balancing using an LSI routing program | 朝家真知子 | JSPP'94 論文集, pp 279-286 | https://cir.nii.ac.jp/crid/1570009749132985856 | PIM/c evaluation |
| 共有メモリ構成クラスタ向きKL1処理方式 / A KL1 execution scheme for shared-memory clusters | 佐藤 正俊, 清水 肇, 松本 明 | 日本ソフトウェア科学会大会論文集 3, pp 117-120, 1986 | https://cir.nii.ac.jp/crid/1520009408026248960 | Early KL1 cluster execution scheme |
| 並列論理型言語KL1 ; 並列推論マシンの組み立て ; 並列推論マシンのOS -- PIMOS / The parallel logic language KL1 ; Building a parallel inference machine ; PIMOS, the OS of the parallel inference machine | 市吉 伸行 / 後藤 厚宏 / 近山 隆 | 数理科学 27(7), pp 11-17 / 18-24 / 26-33, 1989 | https://cir.nii.ac.jp/crid/1522543655354754048 , https://cir.nii.ac.jp/crid/1521417755428727040 , https://cir.nii.ac.jp/crid/1521417755593500544 | Magazine tutorials by the implementers |
| 第五世代コンピュータの並列処理 / Parallel processing in the fifth generation computer | 瀧和男 | bit 別冊, 1993 | https://cir.nii.ac.jp/crid/1571135649491176320 | bit special issue (from the CiNii record only) |
| PIM/m要素プロセッサのアーキテクチャ / Architecture of the PIM/m element processor ("Technical Report", 1990) | 中島 | CiNii citation stub with no venue | https://cir.nii.ac.jp/crid/1570854176706779648 | Same title as the convention paper in table A1; what report this is was not established |
| Evaluation of Inter-processor Communication in the KL1 Implementation on the Multi-PSI | NAKAJIMA K. | ICOT Technical Report TR-531, 1990 | https://cir.nii.ac.jp/crid/1572824499335263360 | English ICOT TR, listed for cross-reference |
| PIM/m要素プロセッサのアーキテクチャ / Architecture of the PIM/m element processor (JSPP version) | 中島, 武田, 中島 | JSPP'90 (並列処理シンポジウム 1990); cited as reference [2] of the PIM/m CSP paper I read | (no record found; citation read on the page image of IPSJ record 122850) | A symposium-length version of the 2-page convention paper; not found online |
| マルチPSIにおけるデバッグ機能・メンテナンス機能 / Debug and maintenance functions of the Multi-PSI | 杉野, 古市, 稲村, 瀧 | JSPP'89; cited as reference [4] of the PIM/m CSP paper I read | (no record found; citation read on the page image of IPSJ record 122850) | Multi-PSI CSP/debug functions including microinstruction-level debugging; not found online |
| PSI-IIのメモリ・アーキテクチャ評価 (as cited) | 中島 浩 | 情報処理学会計算機アーキテクチャ研究会資料, 1990; reference [3] of the PIM/m element-processor paper | this is IPSJ record 24677 in table A8 (open) | Listed only to tie the citation to the open record |

J-STAGE landing pages in table B were fetched with a plain GET (codes in the query log section below); HTML not read.

IEICE itself: `search.ieice.org` and `ken.ieice.org` answered every scripted GET with HTTP 405 and a "Human Verification" page, so IEICE Transactions and 信学技報 (CPSY) could not be searched or opened. I did not try to get past the check.

#### Not found

- Not found: any paper whose subject is the **PIM/m microprogram / KL1 firmware itself** (title searches for PIM/m with マイクロプログラム, ファームウェア, KL1 処理系). The closest are the element-processor paper (A1), the CSP/maintenance paper, and the two FEP papers.
- Not found: a **PIM/m network** paper and a **PIM/m garbage-collection** paper (other than the FEP/PSI-III GC paper).
- Not found: a paper titled with **WEC / 重み付きエクスポートカウント / Weighted Export Counting** (`重み付きエクスポートカウント` 0 hits in IPSJ; `WEC` 26 hits, none related; CiNii `WEC 並列推論` 0, `Weighted Export Counting` 1 unrelated). WEC is named in the body of the Multi-PSI/V2 stop-GC paper (A1, read: "WEC方式と呼ばれる重み付き参照カウンタ"). The 1990 convention paper 119455 says in its abstract that weighted reference counting is the known method.
- Not found: a paper titled with **輸入表** (0 hits); **輸出表** gives only the 1996 SWoPP paper.
- Not found: a dedicated **PSI-III** hardware paper. "PSI-III" is the name the two 1991 convention papers give the PIM/m front-end processor; the PSI/UX paper (91-ARC-91) says in its abstract that PSI/UX uses the PIM/m inference VLSI as CPU.
- Not found: Japanese papers on the **Multi-PSI/V2 KL1 firmware** from convention volumes 34-36 (1987-88) and 43 (1991): those volumes return nothing at all.
- Not found: **スリットチェック** in CiNii (0) or J-STAGE (no result); found once in IPSJ (A1).
- Not found: anything by author **竹田泰治** (`竹田泰治` 0 hits; `竹田 泰治` 1 hit, an unrelated 2004 paper by other people). A guess, not verified: the intended person may be **武田保孝** (Mitsubishi), who is printed as co-author on the PIM/m element-processor and PIM/m CSP papers and listed on the PSI-II memory-architecture and Multi-PSI load-distribution records.
- Not found: additional papers for **益田嘉直** beyond the five listed (Multi-PSI network x3, load distribution, PSI/UX); for **稲村雄**, **平野喜芳**, **中川貴之**, **六沢一昭**, **市吉伸行** all on-topic hits are in the tables.
- Not found: IPSJ-hosted papers on **PIM/k** beyond three convention papers titled PIM/k (1989, 1991) and three hierarchical-cache papers that name PIM/k only in the abstract; on **PIM/c** beyond eight one- or two-page convention papers (1990, 1991).
- Not reachable: **IEICE** (bot wall, HTTP 405).

#### Downloaded files (40, all in the download directory, untrusted, none executed)

Directory: `<scratchpad>/dl_agentC`

- `ipsj_113880_KJ00001330686.pdf` (173256 bytes)
- `ipsj_113882_KJ00001330688.pdf` (168829 bytes)
- `ipsj_113883_KJ00001330689.pdf` (174218 bytes)
- `ipsj_115342_KJ00003117883.pdf` (165109 bytes)
- `ipsj_116579_KJ00001333322.pdf` (179214 bytes)
- `ipsj_116581_KJ00001333324.pdf` (142667 bytes)
- `ipsj_117689_KJ00001335962.pdf` (162726 bytes)
- `ipsj_117693_KJ00001335966.pdf` (154568 bytes)
- `ipsj_117943_KJ00003118279.pdf` (208382 bytes)
- `ipsj_118717_KJ00001338334.pdf` (176023 bytes)
- `ipsj_118810_KJ00001338430.pdf` (168190 bytes)
- `ipsj_120642_KJ00001341482.pdf` (171764 bytes)
- `ipsj_120643_KJ00001341483.pdf` (172640 bytes)
- `ipsj_120649_KJ00001341489.pdf` (81581 bytes)
- `ipsj_120650_KJ00001341490.pdf` (68928 bytes)
- `ipsj_120651_KJ00001341491.pdf` (85809 bytes)
- `ipsj_122850_KJ00001344570.pdf` (197980 bytes)
- `ipsj_14717_IPSJ-JNL3303004.pdf` (803701 bytes)
- `ipsj_14719_IPSJ-JNL3303006.pdf` (734689 bytes)
- `ipsj_14878_IPSJ-JNL3203001.pdf` (1199806 bytes)
- `ipsj_15095_IPSJ-JNL3102016.pdf` (1037146 bytes)
- `ipsj_15121_IPSJ-JNL3012008.pdf` (729235 bytes)
- `ipsj_15125_IPSJ-JNL3012012.pdf` (666432 bytes)
- `ipsj_15128_IPSJ-JNL3012015.pdf` (986050 bytes)
- `ipsj_15329_IPSJ-JNL2910010.pdf` (733546 bytes)
- `ipsj_24531_IPSJ-ARC91089027.pdf` (1122627 bytes)
- `ipsj_24532_IPSJ-ARC91089028.pdf` (1091542 bytes)
- `ipsj_24621_IPSJ-ARC90083023.pdf` (1019758 bytes)
- `ipsj_24655_IPSJ-ARC90082001.pdf` (1098953 bytes)
- `ipsj_24656_IPSJ-ARC90082002.pdf` (1356549 bytes)
- `ipsj_24664_IPSJ-ARC89081003.pdf` (1089696 bytes)
- `ipsj_24677_IPSJ-ARC89080008.pdf` (1026888 bytes)
- `ipsj_24693_IPSJ-ARC89079007.pdf` (1062373 bytes)
- `ipsj_24712_IPSJ-ARC89077003.pdf` (1045081 bytes)
- `ipsj_24746_IPSJ-ARC88074003.pdf` (1366935 bytes)
- `ipsj_26377_IPSJ-OS91051011.pdf` (1232499 bytes)
- `ipsj_30293_IPSJ-PRO96008003.pdf` (453203 bytes)
- `ipsj_30949_IPSJ-PRO89022001.pdf` (1613171 bytes)
- `ipsj_31384_IPSJ-PRO84029007.pdf` (1308779 bytes)
- `jstage_jjsai_4_3_265.pdf` (651263 bytes)

Working files (scripts, harvested JSON, logs) are in the sibling scratch directory `<scratchpad>/workC`; they are not deliverables.

#### Queries tried (verbatim)

Format: service, query string, request URL, outcome. IPSJ URLs were paged (`page=1..4`).

```
CiNii	マルチPSI	https://cir.nii.ac.jp/opensearch/articles?q=%E3%83%9E%E3%83%AB%E3%83%81PSI&format=json&count=200&until=1997	HTTP 200 total=28 returned=28
CiNii	PIM/m	https://cir.nii.ac.jp/opensearch/articles?q=PIM/m&format=json&count=200&until=1997	HTTP 200 total=28 returned=28
CiNii	並列推論マシン	https://cir.nii.ac.jp/opensearch/articles?q=%E4%B8%A6%E5%88%97%E6%8E%A8%E8%AB%96%E3%83%9E%E3%82%B7%E3%83%B3&format=json&count=200&until=1997	HTTP 200 total=143 returned=143
CiNii	KL1 処理系	https://cir.nii.ac.jp/opensearch/articles?q=KL1%20%E5%87%A6%E7%90%86%E7%B3%BB&format=json&count=200&until=1997	HTTP 200 total=48 returned=48
CiNii	PIMOS	https://cir.nii.ac.jp/opensearch/articles?q=PIMOS&format=json&count=200&until=1997	HTTP 200 total=40 returned=40
CiNii	VPIM	https://cir.nii.ac.jp/opensearch/articles?q=VPIM&format=json&count=200&until=1997	HTTP 200 total=5 returned=5
CiNii	スリットチェック	https://cir.nii.ac.jp/opensearch/articles?q=%E3%82%B9%E3%83%AA%E3%83%83%E3%83%88%E3%83%81%E3%82%A7%E3%83%83%E3%82%AF&format=json&count=200&until=1997	HTTP 200 total=0 returned=0
CiNii	多重参照ビット	https://cir.nii.ac.jp/opensearch/articles?q=%E5%A4%9A%E9%87%8D%E5%8F%82%E7%85%A7%E3%83%93%E3%83%83%E3%83%88&format=json&count=200&until=1997	HTTP 200 total=1 returned=1
CiNii	逐次型推論マシン	https://cir.nii.ac.jp/opensearch/articles?q=%E9%80%90%E6%AC%A1%E5%9E%8B%E6%8E%A8%E8%AB%96%E3%83%9E%E3%82%B7%E3%83%B3&format=json&count=200&until=1997	HTTP 200 total=44 returned=44
CiNii	PSI-II	https://cir.nii.ac.jp/opensearch/articles?q=PSI-II&format=json&count=200&until=1997	HTTP 200 total=24 returned=24
J-STAGE	マルチPSI	https://api.jstage.jst.go.jp/searchapi/do?service=3&text=%E3%83%9E%E3%83%AB%E3%83%81PSI&pubyearto=1997&count=200	HTTP 200 total=12 returned=12
J-STAGE	PIM/m	https://api.jstage.jst.go.jp/searchapi/do?service=3&text=PIM/m&pubyearto=1997&count=200	HTTP 200 total=1049 returned=200
J-STAGE	並列推論マシン	https://api.jstage.jst.go.jp/searchapi/do?service=3&text=%E4%B8%A6%E5%88%97%E6%8E%A8%E8%AB%96%E3%83%9E%E3%82%B7%E3%83%B3&pubyearto=1997&count=200	HTTP 200 total=54 returned=54
J-STAGE	KL1	https://api.jstage.jst.go.jp/searchapi/do?service=3&text=KL1&pubyearto=1997&count=200	HTTP 200 total=2154238 returned=200
J-STAGE	PIMOS	https://api.jstage.jst.go.jp/searchapi/do?service=3&text=PIMOS&pubyearto=1997&count=200	HTTP 200 total=14 returned=14
J-STAGE	VPIM	https://api.jstage.jst.go.jp/searchapi/do?service=3&text=VPIM&pubyearto=1997&count=200	HTTP 200 total=6 returned=6
J-STAGE	スリットチェック	https://api.jstage.jst.go.jp/searchapi/do?service=3&text=%E3%82%B9%E3%83%AA%E3%83%83%E3%83%88%E3%83%81%E3%82%A7%E3%83%83%E3%82%AF&pubyearto=1997&count=200	HTTP 200 total= returned=1
J-STAGE	逐次型推論マシン	https://api.jstage.jst.go.jp/searchapi/do?service=3&text=%E9%80%90%E6%AC%A1%E5%9E%8B%E6%8E%A8%E8%AB%96%E3%83%9E%E3%82%B7%E3%83%B3&pubyearto=1997&count=200	HTTP 200 total=15 returned=15
J-STAGE	PSI-II	https://api.jstage.jst.go.jp/searchapi/do?service=3&text=PSI-II&pubyearto=1997&count=200	HTTP 200 total=52518 returned=200
J-STAGE	Multi-PSI	https://api.jstage.jst.go.jp/searchapi/do?service=3&text=Multi-PSI&pubyearto=1997&count=200	HTTP 200 total=2385 returned=200
J-STAGE	マルチPSI	https://api.jstage.jst.go.jp/searchapi/do?service=3&article=%E3%83%9E%E3%83%AB%E3%83%81PSI&pubyearto=1997&count=200	HTTP 200 total=1 returned=1
J-STAGE	PIM	https://api.jstage.jst.go.jp/searchapi/do?service=3&article=PIM&pubyearto=1997&count=200	HTTP 200 total=3 returned=3
J-STAGE	並列推論マシン	https://api.jstage.jst.go.jp/searchapi/do?service=3&article=%E4%B8%A6%E5%88%97%E6%8E%A8%E8%AB%96%E3%83%9E%E3%82%B7%E3%83%B3&pubyearto=1997&count=200	HTTP 200 total=4 returned=4
J-STAGE	KL1	https://api.jstage.jst.go.jp/searchapi/do?service=3&article=KL1&pubyearto=1997&count=200	HTTP 200 total=219957 returned=200
J-STAGE	PIMOS	https://api.jstage.jst.go.jp/searchapi/do?service=3&article=PIMOS&pubyearto=1997&count=200	HTTP 200 total= returned=1
J-STAGE	推論マシン	https://api.jstage.jst.go.jp/searchapi/do?service=3&article=%E6%8E%A8%E8%AB%96%E3%83%9E%E3%82%B7%E3%83%B3&pubyearto=1997&count=200	HTTP 200 total=5 returned=5
J-STAGE	PSI	https://api.jstage.jst.go.jp/searchapi/do?service=3&article=PSI&pubyearto=1997&count=200	HTTP 200 total=107 returned=107
J-STAGE	並列論理型言語	https://api.jstage.jst.go.jp/searchapi/do?service=3&article=%E4%B8%A6%E5%88%97%E8%AB%96%E7%90%86%E5%9E%8B%E8%A8%80%E8%AA%9E&pubyearto=1997&count=200	HTTP 200 total=1 returned=1
J-STAGE	第五世代コンピュータ	https://api.jstage.jst.go.jp/searchapi/do?service=3&article=%E7%AC%AC%E4%BA%94%E4%B8%96%E4%BB%A3%E3%82%B3%E3%83%B3%E3%83%94%E3%83%A5%E3%83%BC%E3%82%BF&pubyearto=1997&count=200	HTTP 200 total=16 returned=16
J-STAGE	GHC	https://api.jstage.jst.go.jp/searchapi/do?service=3&article=GHC&pubyearto=1997&count=200	HTTP 200 total=2 returned=2
CiNii	Multi-PSI	https://cir.nii.ac.jp/opensearch/articles?q=Multi-PSI&format=json&count=200&until=1997	HTTP 200 total=42 returned=42
CiNii	KL1	https://cir.nii.ac.jp/opensearch/articles?q=KL1&format=json&count=200&until=1997	HTTP 200 total=364 returned=200
CiNii	KL1-B	https://cir.nii.ac.jp/opensearch/articles?q=KL1-B&format=json&count=200&until=1997	HTTP 200 total=13 returned=13
CiNii	PIM/p	https://cir.nii.ac.jp/opensearch/articles?q=PIM/p&format=json&count=200&until=1997	HTTP 200 total=12 returned=12
CiNii	PIM/c	https://cir.nii.ac.jp/opensearch/articles?q=PIM/c&format=json&count=200&until=1997	HTTP 200 total=11 returned=11
CiNii	PIM/i	https://cir.nii.ac.jp/opensearch/articles?q=PIM/i&format=json&count=200&until=1997	HTTP 200 total=21 returned=21
CiNii	PIM/k	https://cir.nii.ac.jp/opensearch/articles?q=PIM/k&format=json&count=200&until=1997	HTTP 200 total=5 returned=5
CiNii	MRB ガーベジコレクション	https://cir.nii.ac.jp/opensearch/articles?q=MRB%20%E3%82%AC%E3%83%BC%E3%83%99%E3%82%B8%E3%82%B3%E3%83%AC%E3%82%AF%E3%82%B7%E3%83%A7%E3%83%B3&format=json&count=200&until=1997	HTTP 200 total=3 returned=3
CiNii	輸出表	https://cir.nii.ac.jp/opensearch/articles?q=%E8%BC%B8%E5%87%BA%E8%A1%A8&format=json&count=200&until=1997	HTTP 200 total=1 returned=1
CiNii	WEC 並列推論	https://cir.nii.ac.jp/opensearch/articles?q=WEC%20%E4%B8%A6%E5%88%97%E6%8E%A8%E8%AB%96&format=json&count=200&until=1997	HTTP 200 total=0 returned=0
CiNii	分散ユニフィケーション	https://cir.nii.ac.jp/opensearch/articles?q=%E5%88%86%E6%95%A3%E3%83%A6%E3%83%8B%E3%83%95%E3%82%A3%E3%82%B1%E3%83%BC%E3%82%B7%E3%83%A7%E3%83%B3&format=json&count=200&until=1997	HTTP 200 total=1 returned=1
CiNii	PSI-III	https://cir.nii.ac.jp/opensearch/articles?q=PSI-III&format=json&count=200&until=1997	HTTP 200 total=2 returned=2
CiNii	推論マシン ファームウェア	https://cir.nii.ac.jp/opensearch/articles?q=%E6%8E%A8%E8%AB%96%E3%83%9E%E3%82%B7%E3%83%B3%20%E3%83%95%E3%82%A1%E3%83%BC%E3%83%A0%E3%82%A6%E3%82%A7%E3%82%A2&format=json&count=200&until=1997	HTTP 200 total=5 returned=5
CiNii	推論マシン マイクロプログラム	https://cir.nii.ac.jp/opensearch/articles?q=%E6%8E%A8%E8%AB%96%E3%83%9E%E3%82%B7%E3%83%B3%20%E3%83%9E%E3%82%A4%E3%82%AF%E3%83%AD%E3%83%97%E3%83%AD%E3%82%B0%E3%83%A9%E3%83%A0&format=json&count=200&until=1997	HTTP 200 total=4 returned=4
CiNii	並列推論マシン用オペレーティングシステム	https://cir.nii.ac.jp/opensearch/articles?q=%E4%B8%A6%E5%88%97%E6%8E%A8%E8%AB%96%E3%83%9E%E3%82%B7%E3%83%B3%E7%94%A8%E3%82%AA%E3%83%9A%E3%83%AC%E3%83%BC%E3%83%86%E3%82%A3%E3%83%B3%E3%82%B0%E3%82%B7%E3%82%B9%E3%83%86%E3%83%A0&format=json&count=200&until=1997	HTTP 200 total=0 returned=0
CiNii	中島克人	https://cir.nii.ac.jp/opensearch/articles?q=%E4%B8%AD%E5%B3%B6%E5%85%8B%E4%BA%BA&format=json&count=200&until=1997	HTTP 200 total=36 returned=36
CiNii	稲村雄	https://cir.nii.ac.jp/opensearch/articles?q=%E7%A8%B2%E6%9D%91%E9%9B%84&format=json&count=200&until=1997	HTTP 200 total=13 returned=13
CiNii	市吉伸行	https://cir.nii.ac.jp/opensearch/articles?q=%E5%B8%82%E5%90%89%E4%BC%B8%E8%A1%8C&format=json&count=200&until=1997	HTTP 200 total=19 returned=19
CiNii	六沢一昭	https://cir.nii.ac.jp/opensearch/articles?q=%E5%85%AD%E6%B2%A2%E4%B8%80%E6%98%AD&format=json&count=200&until=1997	HTTP 200 total=18 returned=18
CiNii	瀧和男	https://cir.nii.ac.jp/opensearch/articles?q=%E7%80%A7%E5%92%8C%E7%94%B7&format=json&count=200&until=1997	HTTP 200 total=65 returned=65
CiNii	近山隆	https://cir.nii.ac.jp/opensearch/articles?q=%E8%BF%91%E5%B1%B1%E9%9A%86&format=json&count=200&until=1997	HTTP 200 total=72 returned=72
CiNii	後藤厚宏	https://cir.nii.ac.jp/opensearch/articles?q=%E5%BE%8C%E8%97%A4%E5%8E%9A%E5%AE%8F&format=json&count=200&until=1997	HTTP 200 total=26 returned=26
CiNii	益田嘉直	https://cir.nii.ac.jp/opensearch/articles?q=%E7%9B%8A%E7%94%B0%E5%98%89%E7%9B%B4&format=json&count=200&until=1997	HTTP 200 total=6 returned=6
CiNii	木村康則	https://cir.nii.ac.jp/opensearch/articles?q=%E6%9C%A8%E6%9D%91%E5%BA%B7%E5%89%87&format=json&count=200&until=1997	HTTP 200 total=34 returned=34
CiNii	平野喜芳	https://cir.nii.ac.jp/opensearch/articles?q=%E5%B9%B3%E9%87%8E%E5%96%9C%E8%8A%B3&format=json&count=200&until=1997	HTTP 200 total=4 returned=4
CiNii	久門耕一	https://cir.nii.ac.jp/opensearch/articles?q=%E4%B9%85%E9%96%80%E8%80%95%E4%B8%80&format=json&count=200&until=1997	HTTP 200 total=6 returned=6
CiNii	今井章	https://cir.nii.ac.jp/opensearch/articles?q=%E4%BB%8A%E4%BA%95%E7%AB%A0&format=json&count=200&until=1997	HTTP 200 total=181 returned=181
IPSJ	マルチPSI	https://ipsj.ixsq.nii.ac.jp/api/records/?q=%E3%83%9E%E3%83%AB%E3%83%81PSI&size=100&page=1	HTTP 200 total=26 page=1 returned=26
IPSJ	Multi-PSI	https://ipsj.ixsq.nii.ac.jp/api/records/?q=Multi-PSI&size=100&page=1	HTTP 200 total=79 page=1 returned=79
IPSJ	PIM/m	https://ipsj.ixsq.nii.ac.jp/api/records/?q=PIM/m&size=100&page=1	HTTP 200 total=165 page=1 returned=100
IPSJ	PIM/m	https://ipsj.ixsq.nii.ac.jp/api/records/?q=PIM/m&size=100&page=2	HTTP 200 total=165 page=2 returned=65
IPSJ	PIM/p	https://ipsj.ixsq.nii.ac.jp/api/records/?q=PIM/p&size=100&page=1	HTTP 200 total=165 page=1 returned=100
IPSJ	PIM/p	https://ipsj.ixsq.nii.ac.jp/api/records/?q=PIM/p&size=100&page=2	HTTP 200 total=165 page=2 returned=65
IPSJ	PIM/c	https://ipsj.ixsq.nii.ac.jp/api/records/?q=PIM/c&size=100&page=1	HTTP 200 total=165 page=1 returned=100
IPSJ	PIM/c	https://ipsj.ixsq.nii.ac.jp/api/records/?q=PIM/c&size=100&page=2	HTTP 200 total=165 page=2 returned=65
IPSJ	PIM/i	https://ipsj.ixsq.nii.ac.jp/api/records/?q=PIM/i&size=100&page=1	HTTP 200 total=165 page=1 returned=100
IPSJ	PIM/i	https://ipsj.ixsq.nii.ac.jp/api/records/?q=PIM/i&size=100&page=2	HTTP 200 total=165 page=2 returned=65
IPSJ	PIM/k	https://ipsj.ixsq.nii.ac.jp/api/records/?q=PIM/k&size=100&page=1	HTTP 200 total=162 page=1 returned=100
IPSJ	PIM/k	https://ipsj.ixsq.nii.ac.jp/api/records/?q=PIM/k&size=100&page=2	HTTP 200 total=162 page=2 returned=62
IPSJ	並列推論マシン	https://ipsj.ixsq.nii.ac.jp/api/records/?q=%E4%B8%A6%E5%88%97%E6%8E%A8%E8%AB%96%E3%83%9E%E3%82%B7%E3%83%B3&size=100&page=1	HTTP 200 total=142 page=1 returned=100
IPSJ	並列推論マシン	https://ipsj.ixsq.nii.ac.jp/api/records/?q=%E4%B8%A6%E5%88%97%E6%8E%A8%E8%AB%96%E3%83%9E%E3%82%B7%E3%83%B3&size=100&page=2	HTTP 200 total=142 page=2 returned=42
IPSJ	KL1	https://ipsj.ixsq.nii.ac.jp/api/records/?q=KL1&size=100&page=1	HTTP 200 total=128 page=1 returned=100
IPSJ	KL1	https://ipsj.ixsq.nii.ac.jp/api/records/?q=KL1&size=100&page=2	HTTP 200 total=128 page=2 returned=28
IPSJ	KL1-B	https://ipsj.ixsq.nii.ac.jp/api/records/?q=KL1-B&size=100&page=1	HTTP 200 total=128 page=1 returned=100
IPSJ	KL1-B	https://ipsj.ixsq.nii.ac.jp/api/records/?q=KL1-B&size=100&page=2	HTTP 200 total=128 page=2 returned=28
IPSJ	PIMOS	https://ipsj.ixsq.nii.ac.jp/api/records/?q=PIMOS&size=100&page=1	HTTP 200 total=25 page=1 returned=25
IPSJ	VPIM	https://ipsj.ixsq.nii.ac.jp/api/records/?q=VPIM&size=100&page=1	HTTP 200 total=4 page=1 returned=4
IPSJ	スリットチェック	https://ipsj.ixsq.nii.ac.jp/api/records/?q=%E3%82%B9%E3%83%AA%E3%83%83%E3%83%88%E3%83%81%E3%82%A7%E3%83%83%E3%82%AF&size=100&page=1	HTTP 200 total=1 page=1 returned=1
IPSJ	MRB	https://ipsj.ixsq.nii.ac.jp/api/records/?q=MRB&size=100&page=1	HTTP 200 total=10 page=1 returned=10
IPSJ	多重参照ビット	https://ipsj.ixsq.nii.ac.jp/api/records/?q=%E5%A4%9A%E9%87%8D%E5%8F%82%E7%85%A7%E3%83%93%E3%83%83%E3%83%88&size=100&page=1	HTTP 200 total=2 page=1 returned=2
IPSJ	輸出表	https://ipsj.ixsq.nii.ac.jp/api/records/?q=%E8%BC%B8%E5%87%BA%E8%A1%A8&size=100&page=1	HTTP 200 total=1 page=1 returned=1
IPSJ	重み付きエクスポートカウント	https://ipsj.ixsq.nii.ac.jp/api/records/?q=%E9%87%8D%E3%81%BF%E4%BB%98%E3%81%8D%E3%82%A8%E3%82%AF%E3%82%B9%E3%83%9D%E3%83%BC%E3%83%88%E3%82%AB%E3%82%A6%E3%83%B3%E3%83%88&size=100&page=1	HTTP 200 total=0 page=1 returned=0
IPSJ	分散ユニフィケーション	https://ipsj.ixsq.nii.ac.jp/api/records/?q=%E5%88%86%E6%95%A3%E3%83%A6%E3%83%8B%E3%83%95%E3%82%A3%E3%82%B1%E3%83%BC%E3%82%B7%E3%83%A7%E3%83%B3&size=100&page=1	HTTP 200 total=1 page=1 returned=1
IPSJ	逐次型推論マシン	https://ipsj.ixsq.nii.ac.jp/api/records/?q=%E9%80%90%E6%AC%A1%E5%9E%8B%E6%8E%A8%E8%AB%96%E3%83%9E%E3%82%B7%E3%83%B3&size=100&page=1	HTTP 200 total=52 page=1 returned=52
IPSJ	PSI-II	https://ipsj.ixsq.nii.ac.jp/api/records/?q=PSI-II&size=100&page=1	HTTP 200 total=362 page=1 returned=100
IPSJ	PSI-II	https://ipsj.ixsq.nii.ac.jp/api/records/?q=PSI-II&size=100&page=2	HTTP 200 total=362 page=2 returned=100
IPSJ	PSI-II	https://ipsj.ixsq.nii.ac.jp/api/records/?q=PSI-II&size=100&page=3	HTTP 200 total=362 page=3 returned=100
IPSJ	PSI-II	https://ipsj.ixsq.nii.ac.jp/api/records/?q=PSI-II&size=100&page=4	HTTP 200 total=362 page=4 returned=62
IPSJ	PSI-III	https://ipsj.ixsq.nii.ac.jp/api/records/?q=PSI-III&size=100&page=1	HTTP 200 total=4 page=1 returned=4
IPSJ	PSI ファームウェア	https://ipsj.ixsq.nii.ac.jp/api/records/?q=PSI%20%E3%83%95%E3%82%A1%E3%83%BC%E3%83%A0%E3%82%A6%E3%82%A7%E3%82%A2&size=100&page=1	HTTP 200 total=4 page=1 returned=4
IPSJ	推論マシン マイクロプログラム	https://ipsj.ixsq.nii.ac.jp/api/records/?q=%E6%8E%A8%E8%AB%96%E3%83%9E%E3%82%B7%E3%83%B3%20%E3%83%9E%E3%82%A4%E3%82%AF%E3%83%AD%E3%83%97%E3%83%AD%E3%82%B0%E3%83%A9%E3%83%A0&size=100&page=1	HTTP 200 total=4 page=1 returned=4
CiNii	マルチPSI/V2	https://cir.nii.ac.jp/opensearch/articles?q=%E3%83%9E%E3%83%AB%E3%83%81PSI/V2&format=json&count=200&until=1997	HTTP 200 total=1 returned=1
CiNii	PIM/m 要素プロセッサ	https://cir.nii.ac.jp/opensearch/articles?q=PIM/m%20%E8%A6%81%E7%B4%A0%E3%83%97%E3%83%AD%E3%82%BB%E3%83%83%E3%82%B5&format=json&count=200&until=1997	HTTP 200 total=5 returned=5
CiNii	KL1 抽象命令	https://cir.nii.ac.jp/opensearch/articles?q=KL1%20%E6%8A%BD%E8%B1%A1%E5%91%BD%E4%BB%A4&format=json&count=200&until=1997	HTTP 200 total=2 returned=2
CiNii	KL1 ガーベジコレクション	https://cir.nii.ac.jp/opensearch/articles?q=KL1%20%E3%82%AC%E3%83%BC%E3%83%99%E3%82%B8%E3%82%B3%E3%83%AC%E3%82%AF%E3%82%B7%E3%83%A7%E3%83%B3&format=json&count=200&until=1997	HTTP 200 total=7 returned=7
CiNii	荘園 KL1	https://cir.nii.ac.jp/opensearch/articles?q=%E8%8D%98%E5%9C%92%20KL1&format=json&count=200&until=1997	HTTP 200 total=1 returned=1
CiNii	スリットチェック機構	https://cir.nii.ac.jp/opensearch/articles?q=%E3%82%B9%E3%83%AA%E3%83%83%E3%83%88%E3%83%81%E3%82%A7%E3%83%83%E3%82%AF%E6%A9%9F%E6%A7%8B&format=json&count=200&until=1997	HTTP 200 total=0 returned=0
CiNii	PSI-II 命令セット	https://cir.nii.ac.jp/opensearch/articles?q=PSI-II%20%E5%91%BD%E4%BB%A4%E3%82%BB%E3%83%83%E3%83%88&format=json&count=200&until=1997	HTTP 200 total=0 returned=0
CiNii	PSI ファームウェア	https://cir.nii.ac.jp/opensearch/articles?q=PSI%20%E3%83%95%E3%82%A1%E3%83%BC%E3%83%A0%E3%82%A6%E3%82%A7%E3%82%A2&format=json&count=200&until=1997	HTTP 200 total=5 returned=5
CiNii	WEC 外部参照	https://cir.nii.ac.jp/opensearch/articles?q=WEC%20%E5%A4%96%E9%83%A8%E5%8F%82%E7%85%A7&format=json&count=200&until=1997	HTTP 200 total=0 returned=0
CiNii	Weighted Export Counting	https://cir.nii.ac.jp/opensearch/articles?q=Weighted%20Export%20Counting&format=json&count=200&until=1997	HTTP 200 total=1 returned=1
CiNii	中川貴之	https://cir.nii.ac.jp/opensearch/articles?q=%E4%B8%AD%E5%B7%9D%E8%B2%B4%E4%B9%8B&format=json&count=200&until=1997	HTTP 200 total=12 returned=12
CiNii	佐藤正樹	https://cir.nii.ac.jp/opensearch/articles?q=%E4%BD%90%E8%97%A4%E6%AD%A3%E6%A8%B9&format=json&count=200&until=1997	HTTP 200 total=154 returned=154
CiNii	平田圭二 KL1	https://cir.nii.ac.jp/opensearch/articles?q=%E5%B9%B3%E7%94%B0%E5%9C%AD%E4%BA%8C%20KL1&format=json&count=200&until=1997	HTTP 200 total=0 returned=0
CiNii	武田保孝	https://cir.nii.ac.jp/opensearch/articles?q=%E6%AD%A6%E7%94%B0%E4%BF%9D%E5%AD%9D&format=json&count=200&until=1997	HTTP 200 total=4 returned=4
IPSJ	中島克人	https://ipsj.ixsq.nii.ac.jp/api/records/?q=%E4%B8%AD%E5%B3%B6%E5%85%8B%E4%BA%BA&size=100&page=1	HTTP 200 total=5 page=1 returned=5
IPSJ	稲村雄	https://ipsj.ixsq.nii.ac.jp/api/records/?q=%E7%A8%B2%E6%9D%91%E9%9B%84&size=100&page=1	HTTP 200 total=1 page=1 returned=1
IPSJ	市吉伸行	https://ipsj.ixsq.nii.ac.jp/api/records/?q=%E5%B8%82%E5%90%89%E4%BC%B8%E8%A1%8C&size=100&page=1	HTTP 200 total=0 page=1 returned=0
IPSJ	六沢一昭	https://ipsj.ixsq.nii.ac.jp/api/records/?q=%E5%85%AD%E6%B2%A2%E4%B8%80%E6%98%AD&size=100&page=1	HTTP 200 total=1 page=1 returned=1
IPSJ	瀧和男	https://ipsj.ixsq.nii.ac.jp/api/records/?q=%E7%80%A7%E5%92%8C%E7%94%B7&size=100&page=1	HTTP 200 total=6 page=1 returned=6
IPSJ	近山隆	https://ipsj.ixsq.nii.ac.jp/api/records/?q=%E8%BF%91%E5%B1%B1%E9%9A%86&size=100&page=1	HTTP 200 total=7 page=1 returned=7
IPSJ	後藤厚宏	https://ipsj.ixsq.nii.ac.jp/api/records/?q=%E5%BE%8C%E8%97%A4%E5%8E%9A%E5%AE%8F&size=100&page=1	HTTP 200 total=17 page=1 returned=17
IPSJ	中川貴之	https://ipsj.ixsq.nii.ac.jp/api/records/?q=%E4%B8%AD%E5%B7%9D%E8%B2%B4%E4%B9%8B&size=100&page=1	HTTP 200 total=1 page=1 returned=1
IPSJ	益田嘉直	https://ipsj.ixsq.nii.ac.jp/api/records/?q=%E7%9B%8A%E7%94%B0%E5%98%89%E7%9B%B4&size=100&page=1	HTTP 200 total=0 page=1 returned=0
IPSJ	竹田泰治	https://ipsj.ixsq.nii.ac.jp/api/records/?q=%E7%AB%B9%E7%94%B0%E6%B3%B0%E6%B2%BB&size=100&page=1	HTTP 200 total=0 page=1 returned=0
IPSJ	佐藤正樹	https://ipsj.ixsq.nii.ac.jp/api/records/?q=%E4%BD%90%E8%97%A4%E6%AD%A3%E6%A8%B9&size=100&page=1	HTTP 200 total=3 page=1 returned=3
IPSJ	木村康則	https://ipsj.ixsq.nii.ac.jp/api/records/?q=%E6%9C%A8%E6%9D%91%E5%BA%B7%E5%89%87&size=100&page=1	HTTP 200 total=4 page=1 returned=4
IPSJ	平野喜芳	https://ipsj.ixsq.nii.ac.jp/api/records/?q=%E5%B9%B3%E9%87%8E%E5%96%9C%E8%8A%B3&size=100&page=1	HTTP 200 total=0 page=1 returned=0
IPSJ	久門耕一	https://ipsj.ixsq.nii.ac.jp/api/records/?q=%E4%B9%85%E9%96%80%E8%80%95%E4%B8%80&size=100&page=1	HTTP 200 total=2 page=1 returned=2
IPSJ	今井章	https://ipsj.ixsq.nii.ac.jp/api/records/?q=%E4%BB%8A%E4%BA%95%E7%AB%A0&size=100&page=1	HTTP 200 total=0 page=1 returned=0
IPSJ	平田圭二	https://ipsj.ixsq.nii.ac.jp/api/records/?q=%E5%B9%B3%E7%94%B0%E5%9C%AD%E4%BA%8C&size=100&page=1	HTTP 200 total=24 page=1 returned=24
IPSJ	マルチPSI/V2	https://ipsj.ixsq.nii.ac.jp/api/records/?q=%E3%83%9E%E3%83%AB%E3%83%81PSI/V2&size=100&page=1	HTTP 200 total=5 page=1 returned=5
IPSJ	KL1 処理系	https://ipsj.ixsq.nii.ac.jp/api/records/?q=KL1%20%E5%87%A6%E7%90%86%E7%B3%BB&size=100&page=1	HTTP 200 total=57 page=1 returned=57
IPSJ	PIMOS オペレーティングシステム	https://ipsj.ixsq.nii.ac.jp/api/records/?q=PIMOS%20%E3%82%AA%E3%83%9A%E3%83%AC%E3%83%BC%E3%83%86%E3%82%A3%E3%83%B3%E3%82%B0%E3%82%B7%E3%82%B9%E3%83%86%E3%83%A0&size=100&page=1	HTTP 200 total=11 page=1 returned=11
IPSJ	91-ARC-89	https://ipsj.ixsq.nii.ac.jp/api/records/?q=91-ARC-89&size=100&page=1	HTTP 200 total=4697 page=1 returned=100
IPSJ	91-ARC-89	https://ipsj.ixsq.nii.ac.jp/api/records/?q=91-ARC-89&size=100&page=2	HTTP 200 total=4697 page=2 returned=100
IPSJ	91-ARC-89	https://ipsj.ixsq.nii.ac.jp/api/records/?q=91-ARC-89&size=100&page=3	HTTP 200 total=4697 page=3 returned=100
IPSJ	91-ARC-89	https://ipsj.ixsq.nii.ac.jp/api/records/?q=91-ARC-89&size=100&page=4	HTTP 200 total=4697 page=4 returned=100
IPSJ	仮想並列推論マシン	https://ipsj.ixsq.nii.ac.jp/api/records/?q=%E4%BB%AE%E6%83%B3%E4%B8%A6%E5%88%97%E6%8E%A8%E8%AB%96%E3%83%9E%E3%82%B7%E3%83%B3&size=100&page=1	HTTP 200 total=0 page=1 returned=0
IPSJ	PIM ガーベジコレクション	https://ipsj.ixsq.nii.ac.jp/api/records/?q=PIM%20%E3%82%AC%E3%83%BC%E3%83%99%E3%82%B8%E3%82%B3%E3%83%AC%E3%82%AF%E3%82%B7%E3%83%A7%E3%83%B3&size=100&page=1	HTTP 200 total=6 page=1 returned=6
IPSJ	ゴール 中断 KL1	https://ipsj.ixsq.nii.ac.jp/api/records/?q=%E3%82%B4%E3%83%BC%E3%83%AB%20%E4%B8%AD%E6%96%AD%20KL1&size=100&page=1	HTTP 200 total=1 page=1 returned=1
IPSJ	輸入表	https://ipsj.ixsq.nii.ac.jp/api/records/?q=%E8%BC%B8%E5%85%A5%E8%A1%A8&size=100&page=1	HTTP 200 total=0 page=1 returned=0
IPSJ	プロセッサ間通信 KL1	https://ipsj.ixsq.nii.ac.jp/api/records/?q=%E3%83%97%E3%83%AD%E3%82%BB%E3%83%83%E3%82%B5%E9%96%93%E9%80%9A%E4%BF%A1%20KL1&size=100&page=1	HTTP 200 total=1 page=1 returned=1
IPSJ	WEC	https://ipsj.ixsq.nii.ac.jp/api/records/?q=WEC&size=100&page=1	HTTP 200 total=26 page=1 returned=26
IPSJ	CSP PSI	https://ipsj.ixsq.nii.ac.jp/api/records/?q=CSP%20PSI&size=100&page=1	HTTP 200 total=2 page=1 returned=2
IPSJ	FEP PSI	https://ipsj.ixsq.nii.ac.jp/api/records/?q=FEP%20PSI&size=100&page=1	HTTP 200 total=1 page=1 returned=1
IPSJ	推論マシン VLSI	https://ipsj.ixsq.nii.ac.jp/api/records/?q=%E6%8E%A8%E8%AB%96%E3%83%9E%E3%82%B7%E3%83%B3%20VLSI&size=100&page=1	HTTP 200 total=3 page=1 returned=3
IPSJ	PSI ファームウェア 評価	https://ipsj.ixsq.nii.ac.jp/api/records/?q=PSI%20%E3%83%95%E3%82%A1%E3%83%BC%E3%83%A0%E3%82%A6%E3%82%A7%E3%82%A2%20%E8%A9%95%E4%BE%A1&size=100&page=1	HTTP 200 total=0 page=1 returned=0
IPSJ	中島 克人	https://ipsj.ixsq.nii.ac.jp/api/records/?q=%E4%B8%AD%E5%B3%B6%20%E5%85%8B%E4%BA%BA&size=100&page=1	HTTP 200 total=116 page=1 returned=100
IPSJ	中島 克人	https://ipsj.ixsq.nii.ac.jp/api/records/?q=%E4%B8%AD%E5%B3%B6%20%E5%85%8B%E4%BA%BA&size=100&page=2	HTTP 200 total=116 page=2 returned=16
IPSJ	稲村 雄	https://ipsj.ixsq.nii.ac.jp/api/records/?q=%E7%A8%B2%E6%9D%91%20%E9%9B%84&size=100&page=1	HTTP 200 total=23 page=1 returned=23
IPSJ	市吉 伸行	https://ipsj.ixsq.nii.ac.jp/api/records/?q=%E5%B8%82%E5%90%89%20%E4%BC%B8%E8%A1%8C&size=100&page=1	HTTP 200 total=18 page=1 returned=18
IPSJ	六沢 一昭	https://ipsj.ixsq.nii.ac.jp/api/records/?q=%E5%85%AD%E6%B2%A2%20%E4%B8%80%E6%98%AD&size=100&page=1	HTTP 200 total=35 page=1 returned=35
IPSJ	瀧 和男	https://ipsj.ixsq.nii.ac.jp/api/records/?q=%E7%80%A7%20%E5%92%8C%E7%94%B7&size=100&page=1	HTTP 200 total=69 page=1 returned=69
IPSJ	近山 隆	https://ipsj.ixsq.nii.ac.jp/api/records/?q=%E8%BF%91%E5%B1%B1%20%E9%9A%86&size=100&page=1	HTTP 200 total=210 page=1 returned=100
IPSJ	近山 隆	https://ipsj.ixsq.nii.ac.jp/api/records/?q=%E8%BF%91%E5%B1%B1%20%E9%9A%86&size=100&page=2	HTTP 200 total=210 page=2 returned=100
IPSJ	近山 隆	https://ipsj.ixsq.nii.ac.jp/api/records/?q=%E8%BF%91%E5%B1%B1%20%E9%9A%86&size=100&page=3	HTTP 200 total=210 page=3 returned=10
IPSJ	後藤 厚宏	https://ipsj.ixsq.nii.ac.jp/api/records/?q=%E5%BE%8C%E8%97%A4%20%E5%8E%9A%E5%AE%8F&size=100&page=1	HTTP 200 total=93 page=1 returned=93
IPSJ	中川 貴之	https://ipsj.ixsq.nii.ac.jp/api/records/?q=%E4%B8%AD%E5%B7%9D%20%E8%B2%B4%E4%B9%8B&size=100&page=1	HTTP 200 total=12 page=1 returned=12
IPSJ	益田 嘉直	https://ipsj.ixsq.nii.ac.jp/api/records/?q=%E7%9B%8A%E7%94%B0%20%E5%98%89%E7%9B%B4&size=100&page=1	HTTP 200 total=5 page=1 returned=5
IPSJ	竹田 泰治	https://ipsj.ixsq.nii.ac.jp/api/records/?q=%E7%AB%B9%E7%94%B0%20%E6%B3%B0%E6%B2%BB&size=100&page=1	HTTP 200 total=1 page=1 returned=1
IPSJ	佐藤 正樹	https://ipsj.ixsq.nii.ac.jp/api/records/?q=%E4%BD%90%E8%97%A4%20%E6%AD%A3%E6%A8%B9&size=100&page=1	HTTP 200 total=54 page=1 returned=54
IPSJ	木村 康則	https://ipsj.ixsq.nii.ac.jp/api/records/?q=%E6%9C%A8%E6%9D%91%20%E5%BA%B7%E5%89%87&size=100&page=1	HTTP 200 total=55 page=1 returned=55
IPSJ	平野 喜芳	https://ipsj.ixsq.nii.ac.jp/api/records/?q=%E5%B9%B3%E9%87%8E%20%E5%96%9C%E8%8A%B3&size=100&page=1	HTTP 200 total=7 page=1 returned=7
IPSJ	久門 耕一	https://ipsj.ixsq.nii.ac.jp/api/records/?q=%E4%B9%85%E9%96%80%20%E8%80%95%E4%B8%80&size=100&page=1	HTTP 200 total=50 page=1 returned=50
IPSJ	今井 明	https://ipsj.ixsq.nii.ac.jp/api/records/?q=%E4%BB%8A%E4%BA%95%20%E6%98%8E&size=100&page=1	HTTP 200 total=241 page=1 returned=100
IPSJ	今井 明	https://ipsj.ixsq.nii.ac.jp/api/records/?q=%E4%BB%8A%E4%BA%95%20%E6%98%8E&size=100&page=2	HTTP 200 total=241 page=2 returned=100
IPSJ	今井 明	https://ipsj.ixsq.nii.ac.jp/api/records/?q=%E4%BB%8A%E4%BA%95%20%E6%98%8E&size=100&page=3	HTTP 200 total=241 page=3 returned=41
IPSJ	今井 章	https://ipsj.ixsq.nii.ac.jp/api/records/?q=%E4%BB%8A%E4%BA%95%20%E7%AB%A0&size=100&page=1	HTTP 200 total=45 page=1 returned=45
IPSJ	平田 圭二	https://ipsj.ixsq.nii.ac.jp/api/records/?q=%E5%B9%B3%E7%94%B0%20%E5%9C%AD%E4%BA%8C&size=100&page=1	HTTP 200 total=319 page=1 returned=100
IPSJ	平田 圭二	https://ipsj.ixsq.nii.ac.jp/api/records/?q=%E5%B9%B3%E7%94%B0%20%E5%9C%AD%E4%BA%8C&size=100&page=2	HTTP 200 total=319 page=2 returned=100
IPSJ	平田 圭二	https://ipsj.ixsq.nii.ac.jp/api/records/?q=%E5%B9%B3%E7%94%B0%20%E5%9C%AD%E4%BA%8C&size=100&page=3	HTTP 200 total=319 page=3 returned=100
IPSJ	平田 圭二	https://ipsj.ixsq.nii.ac.jp/api/records/?q=%E5%B9%B3%E7%94%B0%20%E5%9C%AD%E4%BA%8C&size=100&page=4	HTTP 200 total=319 page=4 returned=19
IPSJ	中島 浩	https://ipsj.ixsq.nii.ac.jp/api/records/?q=%E4%B8%AD%E5%B3%B6%20%E6%B5%A9&size=100&page=1	HTTP 200 total=376 page=1 returned=100
IPSJ	中島 浩	https://ipsj.ixsq.nii.ac.jp/api/records/?q=%E4%B8%AD%E5%B3%B6%20%E6%B5%A9&size=100&page=2	HTTP 200 total=376 page=2 returned=100
IPSJ	中島 浩	https://ipsj.ixsq.nii.ac.jp/api/records/?q=%E4%B8%AD%E5%B3%B6%20%E6%B5%A9&size=100&page=3	HTTP 200 total=376 page=3 returned=100
IPSJ	中島 浩	https://ipsj.ixsq.nii.ac.jp/api/records/?q=%E4%B8%AD%E5%B3%B6%20%E6%B5%A9&size=100&page=4	HTTP 200 total=376 page=4 returned=76
IPSJ	武田 保孝	https://ipsj.ixsq.nii.ac.jp/api/records/?q=%E6%AD%A6%E7%94%B0%20%E4%BF%9D%E5%AD%9D&size=100&page=1	HTTP 200 total=6 page=1 returned=6
IPSJ	宮内 信仁	https://ipsj.ixsq.nii.ac.jp/api/records/?q=%E5%AE%AE%E5%86%85%20%E4%BF%A1%E4%BB%81&size=100&page=1	HTTP 200 total=18 page=1 returned=18
IPSJ	川合 英夫	https://ipsj.ixsq.nii.ac.jp/api/records/?q=%E5%B7%9D%E5%90%88%20%E8%8B%B1%E5%A4%AB&size=100&page=1	HTTP 200 total=8 page=1 returned=8
IPSJ	仲瀬 明彦	https://ipsj.ixsq.nii.ac.jp/api/records/?q=%E4%BB%B2%E7%80%AC%20%E6%98%8E%E5%BD%A6&size=100&page=1	HTTP 200 total=29 page=1 returned=29
IPSJ	荘園 KL1	https://ipsj.ixsq.nii.ac.jp/api/records/?q=%E8%8D%98%E5%9C%92%20KL1&size=100&page=1	HTTP 200 total=2 page=1 returned=2
IPSJ	外部参照 KL1	https://ipsj.ixsq.nii.ac.jp/api/records/?q=%E5%A4%96%E9%83%A8%E5%8F%82%E7%85%A7%20KL1&size=100&page=1	HTTP 200 total=2 page=1 returned=2
IPSJ	PSI/UX	https://ipsj.ixsq.nii.ac.jp/api/records/?q=PSI/UX&size=100&page=1	HTTP 200 total=3 page=1 returned=3
IPSJ	マルチPSI ファームウェア	https://ipsj.ixsq.nii.ac.jp/api/records/?q=%E3%83%9E%E3%83%AB%E3%83%81PSI%20%E3%83%95%E3%82%A1%E3%83%BC%E3%83%A0%E3%82%A6%E3%82%A7%E3%82%A2&size=100&page=1	HTTP 200 total=3 page=1 returned=3
IEICE	(homepage)	https://search.ieice.org/	HTTP 405 "Human Verification" page (2372 bytes) - bot wall, not searchable by script
IEICE	category D 1992	https://search.ieice.org/bin/index.php?category=D&lang=J&year=1992&abst=	HTTP 405 "Human Verification"
IEICE	並列推論マシン	https://search.ieice.org/bin/search.php?lang=J&keyword=%E4%B8%A6%E5%88%97%E6%8E%A8%E8%AB%96%E3%83%9E%E3%82%B7%E3%83%B3	HTTP 405 "Human Verification"
IEICE	並列推論マシン	https://www.ieice.org/ken/search/index.php?search_mode=form&title=%E4%B8%A6%E5%88%97%E6%8E%A8%E8%AB%96%E3%83%9E%E3%82%B7%E3%83%B3&lang=jpn	HTTP 202, 0 bytes
IEICE	並列推論マシン	https://ken.ieice.org/ken/search/index.php?search_mode=form&title=%E4%B8%A6%E5%88%97%E6%8E%A8%E8%AB%96%E3%83%9E%E3%82%B7%E3%83%B3	HTTP 405 "Human Verification"
IPSJ	q=中島 克人	https://ipsj.ixsq.nii.ac.jp/api/records/?q=%E4%B8%AD%E5%B3%B6%20%E5%85%8B%E4%BA%BA&size=3	probe
IPSJ	creator=中島, 克人	https://ipsj.ixsq.nii.ac.jp/api/records/?creator=%E4%B8%AD%E5%B3%B6%2C%20%E5%85%8B%E4%BA%BA&size=3	probe
IPSJ	creator=中島 克人	https://ipsj.ixsq.nii.ac.jp/api/records/?creator=%E4%B8%AD%E5%B3%B6%20%E5%85%8B%E4%BA%BA&size=3	probe
IPSJ	search_type=0&q="中島, 克人"	https://ipsj.ixsq.nii.ac.jp/api/records/?search_type=0&q=%22%E4%B8%AD%E5%B3%B6%2C%20%E5%85%8B%E4%BA%BA%22&size=3	probe
IPSJ	title=マルチPSI	https://ipsj.ixsq.nii.ac.jp/api/records/?title=%E3%83%9E%E3%83%AB%E3%83%81PSI&size=3	probe
IPSJ	creator=六沢, 一昭	https://ipsj.ixsq.nii.ac.jp/api/records/?creator=%E5%85%AD%E6%B2%A2%2C%20%E4%B8%80%E6%98%AD&size=3	probe
IPSJ	q=中島 克人&search_type=2	https://ipsj.ixsq.nii.ac.jp/api/records/?q=%E4%B8%AD%E5%B3%B6%20%E5%85%8B%E4%BA%BA&search_type=2&size=3	probe
J-STAGE	pdf GET	https://www.jstage.jst.go.jp/article/jjsai/4/3/4_265/_pdf
J-STAGE	pdf GET	https://www.jstage.jst.go.jp/article/jjsai/2/4/2_441/_pdf
J-STAGE	pdf GET	https://www.jstage.jst.go.jp/article/jjsai/2/4/2_450/_pdf
J-STAGE	pdf GET	https://www.jstage.jst.go.jp/article/sicejl1962/25/4/25_4_355/_pdf
J-STAGE	pdf GET	https://www.jstage.jst.go.jp/article/jjsai/8/2/8_159/_pdf
IPSJ	マルチPSI (API discovery probe)	https://ipsj.ixsq.nii.ac.jp/api/records/?q=%E3%83%9E%E3%83%AB%E3%83%81PSI&size=5	HTTP 200 application/json 171109 bytes, total=26
IPSJ	マルチPSI (API discovery probe, no trailing slash)	https://ipsj.ixsq.nii.ac.jp/api/records?q=%E3%83%9E%E3%83%AB%E3%83%81PSI&size=5	HTTP 308 redirect to /api/records/
CiNii	マルチPSI (probe)	https://cir.nii.ac.jp/opensearch/articles?q=%E3%83%9E%E3%83%AB%E3%83%81PSI&format=json&count=5	HTTP 200 application/json
J-STAGE	マルチPSI (probe)	https://api.jstage.jst.go.jp/searchapi/do?service=3&text=%E3%83%9E%E3%83%AB%E3%83%81PSI&count=5	HTTP 200 application/xml
IPSJ	全国大会講演論文集 第35回	https://ipsj.ixsq.nii.ac.jp/api/records/?q=%E5%85%A8%E5%9B%BD%E5%A4%A7%E4%BC%9A%E8%AC%9B%E6%BC%94%E8%AB%96%E6%96%87%E9%9B%86%20%E7%AC%AC35%E5%9B%9E&size=5	HTTP 200, total=3, none from the 35th convention
IPSJ	(index tree probe)	https://ipsj.ixsq.nii.ac.jp/api/tree	HTTP 200, body "[]"
IPSJ	(index tree probe)	https://ipsj.ixsq.nii.ac.jp/api/tree/index/7945	HTTP 403
IPSJ	(index tree probe)	https://ipsj.ixsq.nii.ac.jp/api/index/	HTTP 500
IPSJ	(landing page check)	https://ipsj.ixsq.nii.ac.jp/records/122850	HTTP 200 text/html 70015 bytes
IPSJ	(single-record API, used for 38 ids)	https://ipsj.ixsq.nii.ac.jp/api/records/<id>	HTTP 200 application/json
NOTE	J-STAGE lines marked "text=" are full-text searches (very noisy: KL1 -> 2154238, PSI-II -> 52518); lines marked "article=" are title searches.
NOTE	CiNii queries all carried &until=1997; IPSJ author queries in unspaced form (queries2) are kept for completeness although they proved ineffective.
CiNii	publicationTitle=全国大会講演論文集 from=1987 until=1987	https://cir.nii.ac.jp/opensearch/articles?publicationTitle=%E5%85%A8%E5%9B%BD%E5%A4%A7%E4%BC%9A%E8%AC%9B%E6%BC%94%E8%AB%96%E6%96%87%E9%9B%86&from=1987&until=1987&format=json&count=200	see result note
CiNii	publicationTitle=全国大会講演論文集 from=1988 until=1988	https://cir.nii.ac.jp/opensearch/articles?publicationTitle=%E5%85%A8%E5%9B%BD%E5%A4%A7%E4%BC%9A%E8%AC%9B%E6%BC%94%E8%AB%96%E6%96%87%E9%9B%86&from=1988&until=1988&format=json&count=200	see result note
CiNii	publicationTitle=全国大会講演論文集 from=1991 until=1991	https://cir.nii.ac.jp/opensearch/articles?publicationTitle=%E5%85%A8%E5%9B%BD%E5%A4%A7%E4%BC%9A%E8%AC%9B%E6%BC%94%E8%AB%96%E6%96%87%E9%9B%86&from=1991&until=1991&format=json&count=200	see result note
IPSJ	マルチPSI (record-structure probe)	https://ipsj.ixsq.nii.ac.jp/api/records/?q=%E3%83%9E%E3%83%AB%E3%83%81PSI&size=2	HTTP 200, total=26
IPSJ	VPIM (timing probe)	https://ipsj.ixsq.nii.ac.jp/api/records/?q=VPIM&size=100&page=1	HTTP 200, 32851 bytes, 3.5 s
IPSJ	KL1 (page-size probe)	https://ipsj.ixsq.nii.ac.jp/api/records/?q=KL1&size=100&page=1	HTTP 200, total=128, returned=100
IPSJ	(index tree probe)	https://ipsj.ixsq.nii.ac.jp/api/tree/index/8030	HTTP 403
IPSJ	(PDF verification)	GET with Range: bytes=0-1023 on the PDF URL of each of 144 candidate records	all HTTP 206 with %PDF magic
CiNii	venue probe results	(see the three publicationTitle lines above)	1987 total=24; 1988 total=1127 (first 200: 第37回 only); 1991 total=1139 (first 200: 第42回 only)
LANDING	GET of 135 landing pages (https://ipsj.ixsq.nii.ac.jp/records/<id> for every table row, plus 5 J-STAGE article pages)	result codes: {'200': 135}
LANDING	https://www.jstage.jst.go.jp/article/jjsai/4/3/4_265/_article/-char/ja/	HTTP 200 text/html;charset=utf-8 72434 bytes
LANDING	https://www.jstage.jst.go.jp/article/jjsai/2/4/2_441/_article/-char/ja/	HTTP 200 text/html;charset=utf-8 69801 bytes
LANDING	https://www.jstage.jst.go.jp/article/jjsai/2/4/2_450/_article/-char/ja/	HTTP 200 text/html;charset=utf-8 69878 bytes
LANDING	https://www.jstage.jst.go.jp/article/sicejl1962/25/4/25_4_355/_article/-char/ja/	HTTP 200 text/html;charset=utf-8 72049 bytes
LANDING	https://www.jstage.jst.go.jp/article/jjsai/8/2/8_159/_article/-char/ja/	HTTP 200 text/html;charset=utf-8 70138 bytes
```

#### Item 6 supplement -- the same convention papers inside the ICOT archive (parent agent's own check)

The IPSJ repository has no hits for national-convention volumes 34-36 (1987 to spring
1988) and 43 (autumn 1991) (see the paragraph above). **ICOT's own unlisted Technical
Memoranda fill part of that gap**: the `TMidx` records in section 1.5 show 34th- and
35th-convention papers (TM-259 to TM-286 and TM-313 to TM-396, e.g. TM-261 "PSI-IIシステムの
ファームウェア", TM-263 "KL1の抽象命令仕様とコンパイラ", TM-346 "マルチPSI第2版のPE間アドレス
管理方法", TM-353 "PSI-IIにおけるESPサポート用ファームウェア", TM-359 "マルチPSI第2版の
ハードウェア構成") and 43rd-convention papers (TM-1087 to TM-1098 and TM-1127, e.g. TM-1091
"並列推論マシンPIM/pへのKL1処理系の実装", TM-1092 "大域GCにおけるWTC方式を用いたマーキング
終了検出", TM-1127 "PIM/pにおけるパイプライン制御方式"). They are open PDFs at
`.../Museum/TRTM/TM/TMpdf/tmNNNN.pdf` on both mirrors (nineteen of them downloaded and
checked for `%PDF-`; three first pages read). Several papers are therefore available
twice (IPSJ record and ICOT TM): PIM/m PE architecture = IPSJ record 118810 = TM-850;
PIM/m maintenance architecture and CSP = record 122850 = TM-1213; Multi-PSI/V2 code
format = record 116581 = TM-662; KL1 abstract instruction set = record 116579 = TM-652;
Microlint = record 118717 = TM-849.

The JSPP'89 paper "マルチPSIにおけるデバッグ機能・メンテナンス機能" (Sugino, Furuichi, Inamura,
Taki), which the Item 6 agent lists as "cited, not found online", **is TM-671** in the
ICOT archive (TMidx record: "並列処理シンポジュームJSPP'89での発表論文", same title and authors; 6 pages by `pdfinfo`; `%PDF-` from both mirrors; not read).

Spot checks by the parent agent of the Item 6 agent's results: the IPSJ search API
answered with JSON; the PDF URLs of records 118810, 122850, 113880 and 116581 each
returned HTTP 206 with `%PDF` magic on a ranged GET.

**Correction to table C above:** the four 三菱電機技報 rows (62(12), 65(6), 65(11), 66(6)) are listed there as cited-only because CiNii carries no full-text link. They are in fact openly downloadable from the publisher's archive -- see Item 5 for the PDF URLs (five issue PDFs checked by the parent agent, HTTP 206 `application/pdf`).

---

### Item 7 — later KLIC, surviving KL1 implementations, CESP, emulators, forum threads

#### (a) Table

| item | exact URL | status (+evidence) | what it contains | why it matters |
|---|---|---|---|---|
| **KLIC 3.014** (current, Ueda lab) | https://www.uedalab.jp/~ueda/software/klic-3.014.tgz (linked from https://www.uedalab.jp/software.html) | software.html opened-and-read (curl, 5,910 bytes, UTF-8); tarball resolved-not-read (HEAD 200, application/x-gzip, 26,403,272 bytes) | Page text (tags stripped) lists KLIC version 3.014, previous version KLIC-3.005, a socket/shared-library extension of KLIC-3.003, a KLIC Emacs mode, a GHC system on SWI-Prolog, `klint` v2.2 and `kima` v2.2; page footer "Last update: August 3, 2023" (grep-confirmed in raw bytes) | **Newest KL1 implementation; later than the held klic-2.002.** Sequential + distributed-memory parallel |
| GHC system on SWI-Prolog; klint | https://www.uedalab.jp/~ueda/software/ghcsystem-swi.tgz ; `/~ueda/software/klint-v22.tgz` | first: resolved-not-read (HEAD 200, 195,188 bytes); second: link seen in page, not probed | A GHC interpreter/compiler on SWI-Prolog; static analyser for KL1 | A second, independent executable semantics for GHC/KL1 programs |
| Ueda lab old host | https://www.ueda.info.waseda.ac.jp/ | **dead from here**: curl "Could not resolve host" (HTTP 000) on 3 attempts; uedalab.jp is the working host | — | Old links (incl. those in search results and softwarepreservation.org) need rewriting to uedalab.jp |
| KLIC GitHub mirror (3.01, 3.011, 3.013, 3.014 + extras) | https://github.com/GunterMueller/KLIC | opened-and-read: repo API JSON + contents API + raw README.md (3,270 bytes). Not a GitHub fork (`fork: false`), created 2019-07-10, pushed 2023-10-27. Top level: `SOURCES/`, `klic/`, `klic-3.01/`, `klic-3.011/`, `klic-3.013/`, `klic-3.014/`. `SOURCES/` holds `klic-3.01.tgz` (3,297,560), `klic-3.011.tgz` (3,288,831), `klic-3.013.tgz` (26,433,009), `klic-3.014.tgz` (26,403,272 — same size as the uedalab file), `klic-3.005-extio-shared.tar.gz` (1,062,916), `ghcsystem-swi.tgz` (195,188), `klint-v22.tgz` (44,805). `raw.githubusercontent.com/.../SOURCES/klic-3.014.tgz` HEAD 200 | Unpacked trees and original tarballs of the Waseda maintenance releases | **Second mirror of KLIC 3.x, incl. intermediate versions and 3.005-extio** |
| **KLIC 3.003** (last ICOT/JIPDEC/KLIC Association release, 1999) | https://web.archive.org/web/20031006015341id_/http://www.klic.org/files/v3.0/klic-3.003.tgz | resolved-not-read: HEAD 200, content-type application/x-tar, content-length 1,044,732, `x-archive-orig-last-modified: Mon, 29 Mar 1999 11:34:55 GMT`. CDX row: 20031006015341 status 200 length 1,044,502 | The official 3.003 tarball | **Retrievable from Wayback.** Not downloaded |
| KLIC 2.002 on klic.org (Wayback) | `http://www.klic.org:80/files/v2.0/klic-2.002.tgz` capture 20030829012854 | cdx-row-only (status 200, length 951,392) | Same version the caller holds | Another mirror of a held file |
| klic.org home page (Wayback) | https://web.archive.org/web/20031209125449id_/http://www.klic.org/software/klic/index.en.html | opened-and-read (curl, 6,264 bytes) | States 3.003 is the latest; primary site klic.org, secondary `ftp://pwd.chroot.org/pub/klic/v3.0/klic-3.003.tgz`; three implementations (sequential, distributed-memory, shared-memory); links `tutorial/KL1TUT.info`, `tutorial/tutorial.tex` | Establishes the 2.002 -> 3.003 lineage and that shared-memory KLIC stayed at 2.002 |
| klic.org today | https://www.klic.org/ | opened-and-read: 114-byte HTML that redirects to `/lander` (parked domain). CDX shows unrelated WordPress content from 2025 | — | **Domain is lost; only Wayback is useful.** CDX: 1,928 rows; 864 under `software/klic/` (`lang` 392, `inside` 274, `system` 157, `tutorial` 9) |
| KLIC tutorial sources on klic.org (Wayback) | https://web.archive.org/web/20100119023023id_/http://www.klic.org/software/klic/tutorial/tutorial.tex ; `.../tutorial/KL1TUT.info` (20001207200900, 200, 28,343) | first resolved-not-read (HEAD 200 text/x-tex 94,189 bytes); second cdx-row-only | KL1 tutorial (TeX and Info) | See Item 8 |
| "Inside KLIC" archive on klic.org | `http://www.klic.org:80/files/contrib/tutorial/inside.tgz` (20030720120007, status 403), `inside.zip` (20060616091543, status 404) | cdx-row-only — **captures are error pages** | — | Not retrievable as an archive; HTML version partially captured (274 rows under `software/klic/inside/`) |
| KLIC 1.000 - 1.410 (1994-95) | https://www.cs.cmu.edu/afs/cs/project/ai-repository/ai/areas/icot/symbolic/unix/klic/ | opened-and-read (listing + first lines of `0.lst`): `klic1000.tgz`, `klic1100.tgz`, `klic1210.tgz`, `klic1410.tgz` with `.ltv` listings; 0.lst shows `klic-1.000/{compiler,documents/manual,include,runtime,test}` | Early KLIC releases (1.000 and 1.100 confirmed by directory names in `0.lst`; 1.210 and 1.410 inferred from file names only) | Closest in time to PIMOS/KL1-B practice; earlier than held 2.002 |
| Debian package `klic` 3.003 | https://snapshot.debian.org/archive/debian/20050312T000000Z/pool/main/k/klic/ ; https://sources.debian.org/data/main/k/klic/3.003-2/runtime | first opened-and-read (curl, 11,971 bytes; lists `klic_3.003-1.1_{alpha,arm,hppa,hurd-i386,i386,ia64,m68k,mips,mipsel,...}.deb`); second resolved-not-read (HTTP 200, but sources.debian.org served me an anti-bot challenge page on another URL, so body not trusted) | Debian packages of KLIC 3.003-1.1 (2005 snapshot); the listing also has `klic_3.003.orig.tar.gz`, `klic_3.003-1.1.diff.gz`, `klic_3.003-1.1.dsc`. HEAD of `.../klic_3.003.orig.tar.gz` returned 200, content-length 1,044,878 (content-type reported as text/html; not downloaded). A search result also names a 3.003-2 source path | **Distro mirror of the 3.003 source** |
| FreeBSD / pkgsrc / Repology | https://repology.org/api/v1/project/klic ; https://www.freshports.org/lang/klic/ ; https://cgit.freebsd.org/ports/plain/lang/klic/Makefile ; https://pkgsrc.se/lang/klic ; https://pkgsrc.se/search.php?so=klic | Repology API opened-and-read: body `[]` (2 bytes) = no current package anywhere; freshports `lang/klic` **404**; cgit `lang/klic/Makefile` **404**; pkgsrc.se `lang/klic` **404**; pkgsrc.se search page 200 with no klic package link | — | No FreeBSD/NetBSD port found at the paths tried. Further URLs tried: `https://cgit.freebsd.org/ports/log/lang/klic` (HTTP 200 page but with no commit rows that I could see), `https://cgit.freebsd.org/ports/tree/lang/klic?h=release/4.11.0` (404), `http://distcache.freebsd.org/ports-distfiles/klic-3.003.tgz` (404), `http://ftp.netbsd.org/pub/pkgsrc/distfiles/klic-3.003.tgz` (404). The category `lang/` is my guess; freshports search endpoint returned 403 to curl, so absence is not proven |
| KLIC User's Manual (HTML, for 3.002) | https://dbane.tilde.institute/klic.html | opened-and-read (curl, 569,686 bytes) | Full texinfo-to-HTML KLIC manual: title "KLIC User's Manual", March 1995, revised June 1997, authors Chikayama / Fujise / Sekita | See Item 8 |
| Rosetta Code KLIC page | https://rosettacode.org/wiki/KLIC | resolved-not-read (HTTP 200, 42,960 bytes; not read) | — | — |
| Other KL1 repos on GitHub | https://github.com/suharahiromichi/kl1 | search row only (description "GHC/KL1 Program", pushed 2017-06-20) | Sample GHC/KL1 programs (not an implementation) | Minor |
| GitHub repos titled "ICOT PIMOS operating system" and "ICOT MGTP Theorem Prover" | (two hits in results of queries `pimos` and `ICOT prolog`) | search rows only; not opened | Appear to be re-uploads of already-held IFS packages (2024) | Not fetched; not counted as findings |
| Common ESP (CESP) | https://www.cs.cmu.edu/afs/cs/project/ai-repository/ai/areas/icot/cesp.txt ; `info.tgz` (contains `cesp`, `cesp.j`, 5,000 / 7,222 bytes) ; https://www.airc.aist.go.jp/aitec-icot/ICOT/Museum/IFS/INFO/cesp-E.html | cesp.txt opened-and-read (637 bytes); info.tgz downloaded (13,040 bytes, sha256 9e4a9abac3a038a0432a9cfe02b3f21949fb3ed7e9684600a7d05a70b259944a) and its member list read; AIST page cited-only (title as given by the search result: A GUIDE TO CONVERTING ESP PROGRAMS TO CESP PROGRAMS) | Statement that CESP is NOT part of IFS and was distributed by AI Language Research Institute (AIR), c/o Mitsubishi Electric Ofuna; contact `cesp-request@air.co.jp` | **CESP sources/binaries: not found anywhere.** Only the conversion guide and the contact address survive |
| IFS #3 "KL1 Pseudo Parallel System for PSI-III" abstract | https://www.airc.aist.go.jp/aitec-icot/ICOT/Museum/IFS/abst/003.html | opened-and-read (curl, 2,671 bytes) | Machine PSI-III, environment SIMPOS, language "ESP, microprogram", source 2.5 MB; says the KL1 processor is implemented by PSI-III microprogram code | This is the already-held psdpim package; it is the only published PSI-family microprogram artefact I found referenced |
| PSI / PIM emulators, microcode or ROM dumps, SIMPOS disk images | — | **Not found** (GitHub API: `psi machine prolog emulator` 0, `icot fifth generation` 0, `fifth generation computer ICOT` 0, `PDSS KL1` 0, `SIMPOS` 571 all unrelated in first page, `Multi-PSI` 91 all private-set-intersection crypto; 3 web searches) | — | — |
| Forum / mailing-list / blog threads on surviving PSI hardware | — | **Not found** (web searches naming cctalk/classiccmp/vcfed returned no thread; 2 Japanese-language searches returned none) | — | — |
| Hacker News | https://news.ycombinator.com/item?id=40995274 (Algolia objectID of the comment) | HN Algolia API JSON read: query `"KL1" "ICOT"` gave 1 hit, a comment (2024-07-18) in "Ask HN: What's Prolog like in 2024?" that mentions the FGCS project; story query gave 0 hits | General mention only | No hardware/software leads |
| IPSJ Computer Museum: MELCOM PSI | https://museum.ipsj.or.jp/en/computer/other/0009.html | opened-and-read (curl, 11,778 bytes) | Catalogue description of the commercial PSI (Mitsubishi, 1986); 40-bit words (32-bit data + 8-bit tag), KL0 as machine language | Descriptive entry; **the page text I read does not say where a physical unit is held** |
| ithistory.org MELCOM PSI entry; CHM documents | https://ithistory.org/node/22506 ; https://archive.computerhistory.org/resources/access/text/2022/11/102785625-05-01-acc.pdf | cited-only (appeared in search results; not fetched) | Unknown | Unverified |
| softwarepreservation.org Prolog archive | https://www.softwarepreservation.org/projects/prolog/ ; https://www.softwarepreservation.org/projects/prolog/lisbon/lpw83/p53-Nishikawa.pdf | first opened-and-read (curl, 304,558 bytes; grep for ICOT/KLIC/PSI); second cited-only | Mentions ICOT's KLIC in narrative text and cites FGCS'84 PDFs as hosted at ueda.info.waseda.ac.jp; no ICOT software section found by keyword grep | No new ICOT software there; the Nishikawa PDF (LP Workshop '83 paper, probably on PSI) not opened |

#### (b) Exact quotes (grep -F confirmed in raw bytes)
- GitHub mirror README.md: "KL1 to C compiler system: KLIC (version 3.011)"; "klic-3.003 (official version previously released from ICOT and JIPDEC)"; "the KLIC User's Manual (klic.pdf, klicj.pdf) in the \"documents\"".
- Wayback klic.org index.en.html: "Version 3.003 is the latest and"; "ftp://pwd.chroot.org/pub/klic/v3.0/klic-3.003.tgz"; "still has fatal bugs" (said of the shared-memory parallel implementation in 3.003).
- CMU cesp.txt: "CESP is not part of the ICOT Free Software, instead being".
- IPSJ museum page: "the PSI hardware directly executed KL0".
- AIST IFS abstract 003 (raw line 18, whitespace is a tab + spaces in the file): `Language:    ESP, microprogram`.
- NOT quoted because HTML tags intervene in the raw bytes: the uedalab software page's KLIC line (plain-text rendering reads: KLIC: Portable implementation of KL1 (version 3.014) (Kazunori Ueda)).

#### (c) Queries tried (verbatim)
GitHub repository search API (`https://api.github.com/search/repositories?q=<Q>`, unauthenticated):
- `klic kl1` -> HTTP 200, total_count 1
- `kl1 in:name,description` -> HTTP 200, total_count 336
- `guarded horn clauses` -> HTTP 200, total_count 0
- `fghc` -> HTTP 200, total_count 38
- `pimos` -> HTTP 200, total_count 68
- `icot fifth generation` -> HTTP 200, total_count 0
- `KL1 parallel logic` -> HTTP 200, total_count 0
- `psi machine prolog emulator` -> HTTP 200, total_count 0
- `klic in:name language:C` -> HTTP 200, total_count 8
- `kl1 compiler concurrent logic` -> HTTP 200, total_count 0
- `flat GHC concurrent logic language` -> HTTP 200, total_count 0
- `KLIC concurrent logic programming` -> HTTP 200, total_count 0
- `ICOT prolog` -> HTTP 200, total_count 1
- `fifth generation computer ICOT` -> HTTP 200, total_count 0
- `SIMPOS` -> HTTP 200, total_count 571
- `PDSS KL1` -> HTTP 200, total_count 0
- `Multi-PSI` -> HTTP 200, total_count 91

Hacker News Algolia API (`https://hn.algolia.com/api/v1/search?query=<Q>`):
- `ICOT "fifth generation" PSI KL1` (tags=story) -> nbHits 0
- `"KL1" "ICOT"` -> nbHits 1

Repology API: `https://repology.org/api/v1/project/klic` -> `[]`

WebSearch (annotations: 'simplified' = the tool reported dropping OR operators / phrases):
- `KLIC KL1 to C compiler version 3.014 download Waseda Ueda` -> GitHub KLIC mirror, IFS abstracts, dbane manual
- `PSI machine ICOT "SIMPOS" emulator OR "ROM dump" OR "disk image" Prolog machine preservation` -> nothing relevant
- `PSI-II OR PSI-UX 逐次型推論マシン 実機 現存 OR 保存 OR 動態保存 SIMPOS` -> IPSJ museum page etc.; nothing on surviving machines
- `cctalk OR vcfed "ICOT" "PSI" Prolog machine Mitsubishi "MELCOM PSI" surviving OR collector OR museum` -> no forum threads (simplified: OR and site terms dropped)
- `"Common ESP" OR "CESP" ICOT AIR source code download "Extended Self-contained Prolog" unix` -> CMU AI Repository, AIST cesp-E.html, FOLDOC
- `第五世代コンピュータ PSI マシン 実機 展示 OR 所蔵 OR ジャンク OR 入手 "PSI-II" OR "PSI-III" OR "PSI/UX" 三菱 沖 ブログ` -> no blog on surviving units
- `"Multi-PSI" OR "PIM/m" OR "PSI-II" ICOT emulator github OR simulator "KL1-B" OR "KL0" microcode` -> IFS abstract pages only
- `classiccmp cctalk "fifth generation" ICOT "PSI" OR "PIM" Prolog machine anyone have` -> no threads
- `KLIC "klic-3.003" OR "klic-3.005" OR "klic-3.01" FreeBSD ports OR pkgsrc OR Debian package distfiles` -> Debian 3.003-2 path only
- `ICOT PSI Prolog machine fifth generation` with allowed_domains [classiccmp.org, vcfed.org, forum.vcfed.org] -> no result from those domains (returned arXiv/USPTO items despite the domain restriction)

CDX for klic.org / ueda.info.waseda.ac.jp: see Item 3 list.

#### (d) Not found
- Not found: any PSI-I/II/III, PSI-UX, Multi-PSI or PIM emulator, microcode listing, ROM dump or SIMPOS disk image published anywhere searched.
- Not found: Common ESP (CESP) sources or binaries.
- Not found: any retrocomputing forum, mailing-list or blog thread about a surviving PSI or PIM machine, in English or Japanese.
- Not found: a FreeBSD port or pkgsrc package of KLIC (Debian packaged 3.003).
- Not found: Wayback captures of `ueda.info.waseda.ac.jp` software pages (prefix query returned 0 rows; the domain-wide filtered query failed twice with Wayback errors, so this is inconclusive).
- Not attempted: Twitter/X mirrors; direct queries of the cctalk/classiccmp pipermail archives or the vcfed forum search (only general web search, plus one search restricted with allowed_domains to classiccmp.org / vcfed.org / forum.vcfed.org, which returned no result from those domains).
- Caveat on web search: several WebSearch runs reported that the engine ignored OR operators / exact phrases (see annotations in the per-item query lists), so the forum and blog negatives are weak.

---

### Item 8 — PIMOS / KL1 manuals in PS/TeX form; .kbn / IPL / save-restore / FEP documentation

#### (a) Table

| item | exact URL | status (+evidence) | what it contains | why it matters |
|---|---|---|---|---|
| **`pimosman.ps`** (as `pimosman.pgz`) | https://www.cs.cmu.edu/afs/cs/project/ai-repository/ai/areas/icot/symbolic/pim_psi/pimosman.pgz | **opened-and-read**: downloaded 652,037 bytes, sha256 39c2def4a5bc53a2ee67ce7608f5057347c6279e77e6cc5526b0ab0cc2f1b7b1; `file` says gzip data, was "pimosman.ps", modified 1994-07-08; decompressed 3,177,447 bytes; DSC header `%%Title: e-top.dvi`; 504 `%%Page:` markers. Text strings extracted with a regex (NOT rendered) | PIMOS Manual (V 3.0), Operation Volume, ICOT PIMOS Developing Group, November 1991 (English). Term counts are LOWER BOUNDS (dvi2ps splits words at kerns; counted on extracted strings, then recounted with all whitespace removed): FEP 117, CSP 29, IPL 22, PIM/m 21, Multi-PSI 35, unload 38, pimfep 11 (e.g. `pimfep##pimos_remote_login_requester`, `pimfep_version(#pimfep##pimos_scsi_front_end,^Version,^Date,^Comment)`), `.sav` 3, boot 5; `kbn` 0 and upper-case `SCSI` 0 even with whitespace removed. It refers the reader to a Multi-PSI/V2 Console System Operation Manual (Version 3) for the CPU-side console (de-kerned reading) | **The rendered PostScript of the PIMOS 3.0 manual** (the held pimosman.tar.Z is the TeX source `Eman/e-*.tex`, incl. `e-v30.tex`, `e-protocol.tex`, `e-sysman.tex`, per the `.ltv` listing). Whether it covers both volumes was not determined |
| **PIMOS manuals, older + Japanese** (`man.tgz`) | https://www.cs.cmu.edu/afs/cs/project/ai-repository/ai/areas/icot/manuals/pimos/man.tgz | **opened-and-read**: downloaded 1,506,074 bytes, sha256 5472702fd890121ad9e623d2d3cfac7e30e0319b4d63e9ff1c36dab946ed6386; contains `man/man15.ps` (1,228,977 bytes, 177 pages) and `man/man30.j.ps` (10,124,296 bytes, 535 pages) | `man15.ps`: PIMOS Manual (V 1.5), ICOT PIMOS Developing Group, December 1989, English — the **Multi-PSI-era** manual: chapters on KL1 language spec and built-ins, unloader/loader, a chapter 12 "Administration" with start-up/boot procedure, an appendix "How to create a string I/O device on FEP"; it refers the reader to a separate "Multi-PSI Console System Operation Manual" for CSP operation (lower-bound counts with whitespace removed: FEP 49, CSP 23, boot/Boot 20, IPL 1, kbn 0, SCSI 0, pimfep 0; chapter 12 Administration has 12.1 Booting and Shutdown, 12.1.1 Booting procedure, 12.2 How to Set Up Booting Procedure). `man30.j.ps`: Japanese manual, presumably V3.0 from the file name (Japanese text is in a font encoding I did not decode; ASCII fragments counted on whitespace-stripped strings, lower bounds: FEP 126, IPL 50, CSP 46, PIM/m 22, `.sav` 14, pimfep 11, kbn 2, SCSI 1). **It has an IPL chapter**: table-of-contents fragments read `6.1 IPL...`, `6.1.2 IPL ...`, `6.1.4 IPL ...`, `6.1.5 CSP ...`; both `kbn` hits are the pattern `*.kbn` next to `IPL`/`CAL`/`PIMOS`; other ASCII fragments include `pimos.ipl`, `>sys>csp>PIMOS.DIR>mpsi_bios.sav`, `>sys>csp>PIMOS.DIR>ppim_bios.sav`, and a console transcript `DC> Link Modules...`, `DC> PIMOS booting...`, `DC> V3.000...`, `DC> SCSI UNITS FOUND`; appendix headings mention FEP | **An earlier edition (V1.5) than the held V3.0 TeX, plus the Japanese V3.0 rendering.** V1.5 documents the Multi-PSI/FEP/CSP environment directly; the Japanese V3.0 file is the only manual found that mentions `*.kbn` and shows the IPL/boot console sequence — needs a Japanese reader after rendering |
| **PIMOS primer** (`primer.tgz`) | https://www.cs.cmu.edu/afs/cs/project/ai-repository/ai/areas/icot/manuals/pimos/primer.tgz | **opened-and-read**: 57,462 bytes, sha256 dd9b4669a02188d656052da6c37387ba59ee22ca73de8aab37d290df8c51e9cf; `primer/primer25.tex` (86,498) and `primer/primer15.j.tex` (101,260) | `primer25.tex`: "PIMOS 3.0 Introductory Manual" (English LaTeX). Chapters: Preparing To Run PIMOS (user registration to SIMPOS, SYSTEM MENU entries "Pseudo Multi-PSI", "REMOTE CSP", "PIMOS LOGIN", directory logical names `>sys>csp>SYSTEM.DIR`, `>sys>csp>PMPSI.DIR`, `>sys>csp>PIMOS.DIR`, config file `pimos:pimos.conf`, `pimos:pimos.logins`, `pimos:pimos.groups`), "Booting Up, Logging Into, and Shutting Down PIMOS" incl. section "Booting CSP on (Pseudo) Multi-PSI" | **Best found description of the FEP/CSP-side boot procedure and file layout** (matches `psdpim/SYSTEM.DIR`, `PMPSI.DIR` in the held psdpim package) |
| **"Introduction to KL1"** (`kl1_tut.tgz`) | https://www.cs.cmu.edu/afs/cs/project/ai-repository/ai/areas/icot/manuals/kl1/kl1_tut.tgz | **opened-and-read**: 368,067 bytes, sha256 98031a104eb5e21d9b141bba4af65e018d528aed58b4553c2dc494effc548923; `kl1-tut.ps` (419,548), `kl1-tut.j.ps` (1,034,119), `kl1-tut.dvi` (128,036) | "Introduction to KL1", Takashi Chikayama, ICOT (English PS + DVI, Japanese PS); first extracted strings confirm title/author | The KL1 tutorial asked for |
| **KL1 textbook** (`kl1_text.tgz`) | https://www.cs.cmu.edu/afs/cs/project/ai-repository/ai/areas/icot/manuals/kl1/kl1_text.tgz | downloaded (124,969 bytes, sha256 5ee32d0b8f43bee75b7395338cbcf6f49fc948f2d2664993c57811e470f115ef); member list read, contents not read | LaTeX sources dated June-July 1989: `kl1-text/introductory/` (kiso, types, unification, process, pdss, exercises, answers), `kl1-text/beginner/` (control.tex 84 KB, selection, types, examples), `kl1-text/chuukyu/` (chu-1.0 ... chu-5.0), `whole.tex`. File names (hajimeni, kiso, chuukyu) suggest Japanese text | 1989 three-level KL1 course text (Multi-PSI/PDSS era) |
| ESP manuals | https://www.cs.cmu.edu/afs/cs/project/ai-repository/ai/areas/icot/manuals/esp/ (`espps.tgz` 265K, `espps_j.tgz` 448K, `esptex.tgz` 107K, `esptex_j.tgz` 112K) | `espps.tgz` (271,649 bytes, sha256 162eb8d4...) and `esptex.tgz` (110,046 bytes, sha256 c9d14ea3...) downloaded, member lists read; `_j` variants listed only | `overview-e.ps` (304,075), `program-e.ps` (964,003), and `.tex` sources, dated 1992-08-04; Japanese `overview-j`, `program-j` | ESP language overview + programming manual (the language of SIMPOS and of the CSP/FEP software) |
| KLIC User's Manual | https://dbane.tilde.institute/klic.html (HTML, for 3.002); `klic.pdf` / `klicj.pdf` inside the KLIC 3.01x distributions (per README) | first opened-and-read; PDFs cited-only (named in README, not opened) | KL1 language + built-ins + generic objects as implemented in KLIC | Later, portable description of KL1 built-ins |
| KLIC tutorial | https://web.archive.org/web/20100119023023id_/http://www.klic.org/software/klic/tutorial/tutorial.tex | resolved-not-read (HEAD 200, text/x-tex, 94,189 bytes) | KL1 tutorial TeX source from klic.org | Likely the Info/TeX form of the same Chikayama tutorial (not verified) |
| `.kbn` object / IPL format | no document found. Pointers only: CMU `symbolic/pim_psi/pimos.ltv` (opened-and-read) lists source modules `pimos/src/library/kbn/{kbn.kl1 (20,016), kbnatom.kl1, kbnfile.kl1, kbnheap.kl1, kbnlink.kl1}`, `pimos/src/library/{loader,unloader,assembler}/`, `pimos/src/bios/boot/` (incl. `fep.kl1`), and `0.lst` gives `pimos/protocol` (39,447 bytes) | listing read; these files are inside the already-held pimos package | KL1 source of the kbn writer/linker and the unloader/loader | **The only description of `.kbn` located is this source code.** The English manuals (pimosman.ps V3.0, man15.ps V1.5) contain `kbn` 0 times even with kerning whitespace removed; the Japanese `man30.j.ps` contains `*.kbn` twice, in its IPL chapter (surrounding Japanese not decoded) |
| save / restore (`.sav`) | PIMOS manual V1.5 and V3.0 (above), sections "Unloader" / "Loader" | read as extracted strings | Describes `unload(ModuleAtomList, FileName)` and the loader shell program at user level; V3.0 names `sav` as the default extension of an unloaded file | User-level description only; no byte-level format found |
| SCSI FEP boot protocol / "pimfep" / CSP manual | no document found. Pointers: `pimos/src/bios/fep_module/scsi_fep.kl1` (23,662), `pimos/src/bios/scsi/`, `pimos/src/server/{fep,scsi}/` in pimos.ltv; `psdpim/INSTALL.DIR/pimfep.ptf`, `pimscsi.ptf`, `pimmcsp.ptf`, `mpsicspR.ptf` in psdpim.ltv; TeX file `Eman/e-protocol.tex` (35,680) in pimosman.ltv | listings read (packages already held) | — | The "Multi-PSI Console System Operation Manual" named in the V1.5 manual is the document that would cover CSP/FEP operation; **it was not found** |

#### (b) Exact quotes
grep -F confirmed in raw bytes:
- `primer25.tex`: `\title{PIMOS 3.0\\ Introductory Manual}`; "of the file with the following pathname on FEP with FEP number 0." (preceded in the file by "When PIMOS starts up, PIMOS is initiated according to the contents", and followed by `pimos:pimos.conf`).
- dbane KLIC manual: "This manual corresponds to KLIC version 3.002".

NOT byte-exact (PostScript from dvi2ps stores text in kerned fragments, e.g. raw `PIMOS Man ual \(V 3.0\)`; the following are my de-kerned readings of extracted strings and must be re-checked by rendering the file):
- pimosman.ps opening: PIMOS Manual (V 3.0) | Volume Operation | ICOT PIMOS Developing Group, November 1991 ... "This manual details the use of the Operating System PIMOS, Version 3.0, which is for parallel inference machines" ... the manual "has been divided into two volumes, the Operation Volume and the Programming Volume".
- man15.ps opening: PIMOS Manual (V 1.5), ICOT PIMOS Developping Group, December 1989.
- man15.ps, administration chapter: for environment setting up and CSP operation, refer to the Multi-PSI Console System Operation Manual (whitespace-stripped raw text contains `refertothe"Multi-PSIConsoleSystemOperationManual"`).
- pimosman.ps: for the CPU of the Multi-PSI, PIM/M, refer to the Multi-PSI/V2 Console System Operation Manual (Version 3) (whitespace-stripped raw text contains `Multi-PSI/V2ConsoleSystemOperationManual\(Version3\)`).
- kl1-tut.ps opening: Introduction to KL1, Takashi Chikayama, ICOT.

#### (c) Queries tried (verbatim)
WebSearch:
- `"PIMOS" manual KL1 "Multi-PSI" FEP "front end processor" boot SCSI "PSI-III"` -> nothing relevant (simplified by the engine to PIMOS KL1 Multi-PSI manual)
- `"PIMOS" "KL1" manual "Multi-PSI" OR "PIM/m" "front end processor" OR "FEP" console "CSP"` -> nothing relevant
- `"Introduction to KL1" OR "KL1 programming" tutorial ICOT Chikayama PIMOS manual pdf` -> nothing relevant (simplified: OR dropped)
- `"Multi-PSI Console System" OR "Multi-PSI CSP" OR "pimfep" OR "mpsicsp" operation manual` -> nothing relevant (engine said exact-match operators were not applied)
- `"pimfep"` -> nothing relevant (unrelated R/Python packages)
- `"Multi-PSI/V2 Console System Operation Manual"` -> nothing relevant
- `"Common ESP" OR "CESP" ICOT AIR source code download "Extended Self-contained Prolog" unix` -> surfaced the CMU mirror

Direct directory walks (curl) of `https://www.cs.cmu.edu/afs/cs/project/ai-repository/ai/areas/icot/` : `manuals/`, `manuals/esp/`, `manuals/kl1/`, `manuals/pimos/`, `symbolic/`, `symbolic/pim_psi/`, `symbolic/unix/`, `symbolic/unix/klic/`, `symbolic/pimos/`, `newsltr/`, `apps/`, `kbms_clp/`, `nlp/`, `reasonng/`.

#### (d) Not found
- Not found: any document specifying the `.kbn` object format, the `.ipl` file, or the `.sav` unloaded-module format at byte level. Nearest: the IPL chapter (chapter 6 by its table of contents) of the Japanese PIMOS 3.0 manual `man30.j.ps`, which names `*.kbn`, `pimos.ipl` and `*_bios.sav` files; whether it describes formats or only procedure is undetermined.
- Not found: the Multi-PSI Console System Operation Manual (so named in V1.5; V3.0 calls it Multi-PSI/V2 Console System Operation Manual (Version 3)); exact-phrase web search for the V3 title returned nothing relevant. Nor any CSP / FEP / "pimfep" / SCSI front-end boot-protocol document.
- Not found: a PIMOS manual later than V3.0 (the `Eman/` TeX is dated 1993-03-17 in the tar listing but its cover file is `e-v30.tex`; a 3.x point release manual was not identified).
- Not found: any PIM/m, PIM/p or PSI hardware/firmware manual.
- Not done: rendering the PostScript files (untrusted PostScript was not executed), so page-level citations are not available; the caller should render `pimosman.ps`, `man15.ps`, `man30.j.ps` in a sandbox.

#### Item 8 supplement A -- what the PIMOS primers and the Japanese 3.0 manual say about CSP, IPL and `.kbn` (parent agent, files from the ICOT mirror)

Read from `UEDA/ifs/manuals/pimos/primer25.tex.Z` (LaTeX source, grep and direct reading)
and from `UEDA/ifs/manuals/pimos/man30.j.ps.Z` (rendered with Ghostscript `-dSAFER`;
pages printed "203" and "204", chapter 6 "システムの管理", were read as page images; the
strings `*.kbn`, `pimos.ipl`, `pimos:pimos.ipl`, `>sys>csp>PIMOS.DIR>mpsi_bios.sav` and
`>sys>csp>PIMOS.DIR>ppim_bios.sav` were also confirmed in the raw PostScript bytes).

`primer25.tex` ("PIMOS 3.0 Introductory Manual"), exact strings:

- SIMPOS system-menu entries are bound to ESP entry points: `{"Pseudo Multi-PSI",  mpsicsp##pseudo_csp_main_program}`, `{"REMOTE CSP",         mpsicsp##remote_csp}`, `{"PIMOS LOGIN",       mpsicsp##pimos_remote_login}`; logical directories `"psys"  := [">sys>csp>SYSTEM.DIR"]`, `"pmpsi" := [">sys>csp>PMPSI.DIR"]`, `"pimos" := [">sys>csp>PIMOS.DIR"]`.
- "When PIMOS starts up, PIMOS is initiated according to the contents of the file with the following pathname on FEP with FEP number 0." -- the file is `pimos:pimos.conf`; users and groups come from `pimos:pimos.logins` and `pimos:pimos.groups`.
- CSP start-up transcript: "Initiating all PEs from configuration file MPSI.CONFIG ... PE auto power on... All PEs power ready. / PEs initiation completed" and "The \$ that appears is the CSP prompt symbol."
- The CSP "Auto-Boot switch definitions" panel has the switches CLEAR, INIT, IMPL, Patch, IPL, START, and "Boot file name definitions" with typed files: `CLEAR FILE (.mbn)`, `INIT FILE (.mbn)`, `IMPL FILE (.mbn)`, `IMPL FILE (.kbn)` = `pmpsi:kl1kp.kbn`, `PATCH FILE (.com)` = `pmpsi:kl1pat.com`, `IPL FILE (.kbn)` = `pimos:pimos.kbn`, `SYMBOL FILE (.sym)` = `pimos:pimos.sym`, `START ADDRESS` = `202`. On the pseudo machine the three `.mbn` entries are "(Don't care on Pseudo)".
- "To bootstrap PIMOS from CSP, type the ``boot'' command into the ``CSP Command Window''. If you are using a real Multi-PSI machine, all nodes will automatically turn on."
- After boot the CSP window shows `DC> TCPIP LOGIN STARTED **********` / `DC> (INTo) 00 00000000`; login asks "Enter FEP node name", with the example of a Multi-PSI "connected with icpsi383 (which is also PSI-II machine) as FEP".
- Its bibliography names six documents: "(Pseudo) Multi-PSI System Administration Manual"; "Multi-PSI/V2 Console System (CSP) Operating Manual" (the primer points to its "Chapters 4 and 6" for other boot configurations); "PIMOS 2.5 Manual"; "KL1 Programming: Introduction, Beginning Level, and Intermediate Level"; "Basic System Administration Manual for PSI/SIMPOS Systems"; "Basic PSI/SIMPOS Operating Manual (1),(2)". Of these only the KL1 text was possibly located: `ifs/manuals/kl1/kl1-text.tar.Z` has sub-directories `introductory/`, `beginner/` and `chuukyu/` (intermediate), which matches the cited title's three levels; the title page was not compared.

So the file-type vocabulary is: `.mbn` = images for the CLEAR / INIT / IMPL steps (not
used on the pseudo machine; by position these are the microprogram-level loads, but the
primer does not expand the abbreviation), `.kbn` = KL1-level images for IMPL (`kl1kp.kbn`)
and IPL (`pimos.kbn`), `.com` = patch command file, `.sym` = symbol file.

`man30.j.ps` (PIMOS 3.0 manual, Japanese), section 6.1 "IPL の設定", my translation from
the page images (not byte-verifiable: the Japanese text is in font-encoded fragments):

- 6.1.1: the PIMOS IPL method changed greatly from version 2.5. The code loaded directly from the CSP (the file named `*.kbn`) is now only the code that IPLs PIMOS; that IPL code then loads all the modules that make up PIMOS. Formerly the file loaded at IPL (`*.kbn`) was produced by the cross system CAL; from version 3.0 the files loaded at IPL are produced by the PIMOS unloader, so user programs can also be loaded at IPL time.
- 6.1.2: the files to load are listed in `pimos.ipl` under `>sys>csp>PIMOS.DIR` on the FEP, one full path per line; a line beginning with `%` is a comment; if a module occurs in several files the one loaded last wins, so a patch is applied by appending a line. The printed example lists `mpsi_bios.sav` (and, commented out, `ppim_bios.sav`), `debugger.sav`, `library.sav`, `utility.sav`, `kernel.sav`, `server.sav`, `shell.sav`, `macro.sav`, then `patch0.sav` and a user `demo.sav`.
- 6.1.3: files made with `unload:package/2` cannot be loaded at IPL; use `unload:go/2` or the compiler's unload command. No undefined-predicate check is made at IPL.
- 6.1.4: IPL error messages shown on the CSP: "Unable to open IPL list file", "cannot open file FileName", "Undefined Module Found ModuleName", "CheckSum Error" (with the note that unload files must be transferred by FTP in binary mode).
- 6.1.5: how to produce the symbol file needed for CSP limited trace / spy on IPL-loaded modules.

This is the only prose description of the `.kbn` / `.ipl` / `.sav` boot chain found. It is
operational, not a byte-level format; the format itself is in the held PIMOS source
(`src/library/kbn/`, loader/unloader) as the Item 8 table says.

#### Item 8 supplement B -- printed PSI manuals located in library catalogues (parent agent)

Queried: National Diet Library Search OpenSearch API (`https://ndlsearch.ndl.go.jp/api/opensearch?any=<q>&cnt=N`)
and CiNii Books OpenSearch (`https://cir.nii.ac.jp/opensearch/books?q=<q>&format=json`),
then the CiNii Books holdings page of each record (`https://ci.nii.ac.jp/ncid/<NCID>`,
opened-and-read: HTML fetched, decoded, holdings block read).

| Item (as catalogued) | English | Record | Holding library shown | Status |
|---|---|---|---|---|
| コンソール・プロセッサ(CSP)操作説明書 : 逐次型推論マシンPSI説明書. 新世代コンピュータ技術開発機構, 1985.4. 1冊, 30cm. Note: "MP7003-1" | Console Processor (CSP) Operating Manual: Sequential Inference Machine PSI manual. ICOT, April 1985 | `https://ci.nii.ac.jp/ncid/BN13167682` (CRID 1971149384740275614) | "大学図書館所蔵 件 / 全 1 件" -- 北陸先端科学技術大学院大学 附属図書館 (JAIST Library), call number C42.4/K/1:2950404 | catalogue record opened-and-read; the book itself cited-only |
| KLO組込述語説明書 : 逐次型推論マシンPSI説明書 [sic: "KLO" for KL0]. ICOT, 1985 | KL0 Built-in Predicates Manual: PSI manual | `https://ci.nii.ac.jp/ncid/BN13167310` | JAIST Library, 1 of 1 | same |
| SIMPOS操作説明書. ICOT, 1985 | SIMPOS Operating Manual | `https://ci.nii.ac.jp/ncid/BN13167514` | JAIST Library, 1 of 1 | same |
| SIMPOS使用説明書. ICOT, 1985 | SIMPOS User's Manual | `https://ci.nii.ac.jp/ncid/BN13167194` | JAIST Library, 1 of 1 | same |
| SIMPOS(1.5版)機能追加・変更点の説明資料. ICOT, 1985 | SIMPOS (version 1.5): explanation of added functions and changes | `https://ci.nii.ac.jp/ncid/BN13167467` | JAIST Library, 1 of 1 | same |

These are PSI-I-era (1985) manuals, not PSI-II/III or Multi-PSI ones; the CSP manual is
for the PSI console processor, not the "Multi-PSI/V2 Console System (CSP) Operating
Manual". They are nevertheless the only ICOT machine manuals found in any catalogue, and
they sit at the same institution whose collection page (Item 4) says a "PSI (ICOT)" and
"related manuals and materials" are preserved, and where one author of the PIM/m CSP
paper (TM-1213) gave his affiliation in 1992.

Other catalogue records seen (CiNii Books, publisher = 新世代コンピュータ技術開発機構, 20
records in all): "ICOT無償公開ソフトウェア総覧" (IFS catalogue, 1993); "ICOTジャーナル"
(serial, 1983-); "ICOT technical memorandum : ICOT研究速報" and "ICOT technical report :
ICOT研究論文" (serials); "電子計算機基礎技術開発成果概要報告書" (1983, 1986);
"第五世代コンピュータの研究開発成果" (1992). NDL Search also returns a doctoral thesis record
"並列論理型言語KL1の処理系に関する研究" (木村康則; `https://ndlsearch.ndl.go.jp/books/R100000002-I000000274054`,
record seen in API output only) and "LPC'91チュートリアル" (ICOT, 1991).

Queries tried (NDL `any=`): `SIMPOS`, `PIMOS`, `マルチPSI`, `MELCOM PSI` (HTTP 429 twice), `PSI-II`,
`逐次型推論マシン`, `並列推論マシン`, `ESP 説明書 PSI` (0), `KL1 プログラミング`, `PSI-UX` (3),
`PIM/m`, `新世代コンピュータ技術開発機構 マニュアル` (1), `新世代コンピュータ技術開発機構 説明書` (4),
`木村康則 KL1 処理系` (HTTP 429). CiNii Books `q=`: `逐次型推論マシンPSI説明書` (2),
`新世代コンピュータ技術開発機構 説明書` (4), `... マニュアル` (0), `... 仕様書` (0), `逐次型推論マシン` (2),
`並列推論マシン` (0), `SIMPOS` (7), `PIMOS` (1), `MELCOM PSI` (0), `PSI 三菱電機 説明書` (0),
`マルチPSI` (0), `KL1` (7), `ESP 新世代コンピュータ技術開発機構` (0), `PSI-II` (0), `PSI/UX` (0),
`KL0` (1), `ICOT manual` (0), `Multi-PSI` (0), `推論マシン 説明書` (2), `PSI説明書` (2),
`ESP 説明書` (0), `PSI 操作説明書` (1), `PSI ハードウェア` (0), `KL1 説明書` (0),
`PIMOS マニュアル` (0), `並列推論マシン 説明書` (0), `ESP reference manual` (1, unrelated),
`SIMPOS manual` (0); `publisher=新世代コンピュータ技術開発機構` (20); and the same keywords
restricted to the JAIST library (`fano=FA014009`, 1983-1995): `説明書` (6), `マニュアル` (158),
`PSI` (2), `推論マシン` (2), `MELCOM` (0), `ESP` (0), `三菱電機` (1), `沖電気` (0).

Not found in either catalogue: any Multi-PSI, PSI-II, PSI-III/PSI-UX, PIM or PIMOS
manual; any Mitsubishi-published MELCOM PSI manual; the "Multi-PSI/V2 Console System
(CSP) Operating Manual".

##### Items 3, 7, 8: exists or is cited but could not be opened

- `https://www.ueda.info.waseda.ac.jp/...` (all URLs on this host, incl. `/AITEC_ICOT_ARCHIVES/ICOT/Museum/IFS/abst/003.html`, `004.html`, `FGCS92Demo/E/doc018.html`): DNS did not resolve from here; same paths work under `www.uedalab.jp` / the AIST mirror.
- `https://www.uedalab.jp/~kaneki/klic/klic_top.html` (KLIC-3.005 page): HTTP 401.
- `http://www.logos.ic.i.u-tokyo.ac.jp/klic/software/klic/index.ja.html` ("original homepage of KLIC" link on the uedalab page): HTTP 404.
- `ftp://pwd.chroot.org/pub/klic/v3.0/klic-3.003.tgz` (secondary KLIC site named on the 2003 klic.org page): not probed.
- `http://www.klic.org/files/contrib/tutorial/inside.tgz`: only a Wayback capture with status 403 exists.
- `https://www.jipdec.or.jp/archives/icot/ARCHIVE/Museum/MACHINE/pim-m-E.html`: live 404 (Wayback 2014 capture exists per CDX, not fetched).
- Wayback captures listed as "cdx-row-only" above (FGCS'94 `.ps` files, KLIC contest tarballs, IFS catalogue pages, KLIC "inside" HTML): index rows seen, captures not fetched.
- FGCS'88 vol.1-3 PDFs on the old `www.icot.or.jp` host: CDX rows show only 404 / 410 / "-" statuses for the few PDFs crawled (`88eREL-2.pdf`, `88eITIM-2.pdf`, `88ePIM-4.pdf`, `88ePPS-3.pdf`); the files are live on the AIST mirror.
- archive.org WARC `warc_www_cs_cmu_edu-afs-cs-project-ai-repository-ai_20191020` (5.2 GB): metadata only.
- Borrow-only archive.org books (need an archive.org account to borrow; not opened): `fifthgenerationc0000inte`, `LogicProgr_00_Lass`, `logicprogramming0000unse_b9u9`, `logicprogramming01lusk`, `logicprogramming02lusk`, `peogrammingoffut0000kfuc`, `logicprogramming0000unse_h6h8`, `LogicProgr_00_Kowa`, `fifthgenerationc0000ifip`.
- "Multi-PSI Console System Operation Manual" (cited inside PIMOS Manual V1.5): no copy located.
- Common ESP (CESP) from AI Language Research Institute: cited by ICOT's `cesp` info file; no copy located.
- "Implementations of Distributed Prolog" (Wiley 1992), ICLP'89 proceedings, "Programming of Future Generation Computers" vol. I: catalogue records only (Open Library, `no_ebook`).
- `https://ithistory.org/node/22506`, `https://archive.computerhistory.org/resources/access/text/2022/11/102785625-05-01-acc.pdf`, `https://www.softwarepreservation.org/projects/prolog/lisbon/lpw83/p53-Nishikawa.pdf`, `https://rosettacode.org/wiki/KLIC`: surfaced by search, not read.
- sources.debian.org (`/api/src/klic/` returned an anti-bot challenge page); freshports search (HTTP 403).

---

### Consolidated: exists or is cited, but was not opened

(The per-item lists above are kept; this is the union, shortest form.)

- Manuals cited by the PIMOS primers/manuals, no copy located anywhere: "Multi-PSI/V2 Console System (CSP) Operating Manual" (primer25.tex; cited as "Multi-PSI Console System Operation Manual" in the PIMOS 1.5 manual and as "Multi-PSI/V2 Console System Operation Manual (Version 3)" in the PIMOS 3.0 manual `pimosman.ps`, per the Item 8 agent's raw-text matches); "(Pseudo) Multi-PSI System Administration Manual"; "PIMOS 2.5 Manual"; "Basic System Administration Manual for PSI/SIMPOS Systems"; "Basic PSI/SIMPOS Operating Manual (1),(2)".
- Printed 1985 ICOT manuals catalogued at the JAIST Library (catalogue records read, books not seen): CSP operating manual for PSI ("MP7003-1"), KL0 built-in predicates manual, SIMPOS operating manual, SIMPOS user's manual, SIMPOS 1.5 changes.
- Hardware said to be preserved (statements read, objects and any accompanying documentation not verified): PIM/p and PIM/m at the National Museum of Nature and Science; a "PSI (ICOT)" plus "related manuals and materials" in the JAIST symbolic-processing collection.
- ICOT TR/TM with no PDF on the mirrors: TR-69, 111, 133, 221, 276, 277, 305, 340, 348, 542, 834; TM-72, 81, 127, 376, 542, 543, 544, 688, 723, 901, 902, 917, 1168, 1185, 1280, 1281, 1283. Per the archive's own page, TRs and TMs "can be read at National Diet Library, Japan and Kawasaki Library established by Kanagawa Prefecture".
- ICOT Journal nos. 1-42: only tables of contents online; the serial is catalogued in CiNii Books.
- Common ESP (CESP) 3.3 for SUN4, sold by Mitsubishi Electric Computer Systems (Tokyo) Corp.: no copy located.
- Books with catalogue records only: "Implementations of Distributed Prolog" (Wiley 1992); ICLP'89 proceedings; "Programming of Future Generation Computers" vol. I. Borrow-only on archive.org: FGCS 1981, ICLP'87, NACLP'89 vols 1-2, "Programming of Future Generation Computers II".
- Vendor journals with no online back issues for 1984-1994: Toshiba Review, Oki 沖電気研究開発, FUJITSU (Japanese) and the FSTJ issues missing from bitsavers.
- IEICE Transactions / 信学技報 papers (CiNii records only), incl. "並列推論マシンPIMにおける抽象機械語KL1-Bの実装" (1989) and 宮崎 "並列論理型言語KL1の実現方式と並列OSの記術" (IEICE Trans. D 71(8), 1988); JSPP'90 version of the PIM/m element-processor paper.
- Computer History Museum catalogue: could not be searched by script; holdings unknown.
- Wayback captures seen only as CDX rows; KLIC 3.003 from the klic.org capture (the Item 7 agent got HEAD 200; the parent agent's later GET was answered with a 302 between two capture timestamps and no bytes -- the Item 7 agent also reports a Debian snapshot copy `klic_3.003.orig.tar.gz`, which the parent agent did not re-check; the GitHub mirror holds 3.01-3.014, not 3.003).
- "Prime Time Freeware for AI 1-1" CD-ROM images (book scan exists, discs not found); 5.2 GB WARC of the CMU AI Repository on archive.org (metadata only).

### Ranked: most worth obtaining

Only things that exist or are cited but that this survey could not open. (Things that
were opened and are simply new to the project -- the 384 unlisted TMs, `ifs/manuals/`,
the Mitsubishi Denki Giho articles, the 130 open IPSJ papers, KLIC 3.x -- are free to
download now and are listed in items 1, 5, 6, 7, 8.)

1. **"Multi-PSI/V2 Console System (CSP) Operating Manual"** (publisher not stated in the citations; cited by the PIMOS 3.0 primer, which points to its chapters 4 and 6 for boot configurations, by the PIMOS 1.5 manual as "Multi-PSI Console System Operation Manual", and by the PIMOS 3.0 manual as "... (Version 3)"). It is the document that would describe the CLEAR / INIT / IMPL / IPL steps and the `.mbn` microprogram images. No copy or catalogue record found. Ask: JAIST (collection and library), the maintainer of the uedalab mirror, Mitsubishi Electric.
2. **Whatever accompanies the preserved PIM/m (and PIM/p) at the National Museum of Nature and Science**: the IPSJ page states the machines are preserved there; whether the WCS load media, FEP (PSI-III/PSI-UX) disks, or maintenance documents came with them is unknown. Sourced: the PIM/m control store is a 32K-word writable control store (IPSJ record 118810; Giho 65(11)). Inference, not verified: a writable control store has to be loaded from somewhere at power-on, so the microprogram image may have been kept on the front-end processor's disk rather than in ROM.
3. **The JAIST holdings**: the "PSI (ICOT)" machine and "related manuals and materials" (IPSJ satellite-museum page), and the five 1985 manuals in the JAIST Library (CSP operating manual "MP7003-1", KL0 built-ins, SIMPOS operating and user manuals, SIMPOS 1.5 changes). Even though PSI-I-era, the KL0 and CSP manuals document the lineage that PSI-II, Multi-PSI and PIM/m firmware continued; whether the machine's disk survives or holds SIMPOS is not known (speculation).
4. **"(Pseudo) Multi-PSI System Administration Manual"** and **"PIMOS 2.5 Manual"** (cited by the primer). The 2.5-era IPL used a CAL-built `.kbn`; the 2.5 manual should describe it.
5. **"Basic PSI/SIMPOS Operating Manual (1),(2)"** and **"Basic System Administration Manual for PSI/SIMPOS Systems"** -- the operating documentation for the environment `psdpim` needs: the IFS abstract page for package #3 (`Museum/IFS/abst/003.html`, read by the Item 7 agent) gives machine PSI-III, environment SIMPOS, language "ESP, microprogram".
6. **SIMPOS itself / a PSI-II or PSI-III (PSI/UX) system disk** -- not in any archive searched. The held `psdpim` is described by its IFS abstract as running under SIMPOS on PSI-III. Note that its tar listing (CMU `.ltv`, read) contains `psdpim/PMPSI.DIR/pimm.MEkbn` (506,624 bytes) and `INSTALL.DIR/{pimmcsp,pimmutil,pimscsi,mpsicspR,pimfep}.ptf`; what `pimm.MEkbn` is (KL1-level image or microprogram) was not determined in this survey and is worth examining in the held copy. Leads only: JAIST's machine; Mitsubishi.
7. **IEICE-side papers** behind the bot wall: "並列推論マシンPIMにおける抽象機械語KL1-Bの実装 -- 高級機械語を実装するための道具立" (1989) and 宮崎敏彦, IEICE Trans. D 71(8) 1423-1432 (1988); plus the JSPP'90 PIM/m element-processor paper. Obtainable through a library.
8. **"Implementations of Distributed Prolog"** (Kacsuk & Wise, Wiley 1992), chapter on the Multi-PSI -- no scan anywhere; note ICOT TR-715 "Distributed Implementation of KL1 on the Multi-PSI" (K.Nakajima, 91.11, 25 pp; `TRpdf/tr0715.pdf` is present in the crawl) carries the same title and author as the chapter; whether the texts match was not compared.
9. **TR/TM numbers with no PDF** (list above), readable at the National Diet Library or the Kanagawa prefectural library in Kawasaki; titles of most are in the list pages and should be checked for relevance before a trip.
10. **ICOT Journal full issues** (42 numbers; contents online, text not) and **Toshiba / Oki / Fujitsu house-journal articles** on PIM/k, PIM/i, PIM/p for 1984-94 (print only).
11. **Common ESP 3.3** (Mitsubishi Electric Computer Systems) -- a working ESP implementation outside SIMPOS; whether the `.ptf` files in `psdpim` are ESP that it could load was not determined.

---

### Appendix -- verbatim query logs of the delegated searches

#### Items 3, 7, 8


#### archive.org advancedsearch (https://archive.org/advancedsearch.php?q=<Q>&fl[]=identifier,title,collection,year,mediatype&rows=60&output=json)
- `title:("Fifth Generation Computer Systems")` -> numFound 8
- `title:("fifth generation computer")` -> numFound 11
- `title:("Logic Programming") AND title:(proceedings) AND title:(international conference)` -> numFound 19
- `title:("Implementations of Distributed Prolog")` -> numFound 0
- `title:("Logic Programming") AND title:("North American")` -> numFound 3
- `title:("Programming of Future Generation Computers")` -> numFound 0
- `PIMOS` -> numFound 2 (both irrelevant CIA reading-room full-text hits)
- `ICOT` -> numFound 75 (only 60 rows fetched; noise-dominated; redone field-restricted below)
- `title:(fifth generation computer systems) AND year:[1984 TO 1989]` -> HTTP 200, numFound 4
- `title:(fifth generation) AND mediatype:(texts OR software) AND year:[1980 TO 1995]` -> HTTP 200, numFound 34
- `title:(logic programming) AND year:[1987 TO 1990] AND mediatype:texts` -> HTTP 200, numFound 76
- `title:(distributed prolog)` -> HTTP 200, numFound 2
- `creator:(Kacsuk)` -> HTTP 200, numFound 4
- `title:(future generation computers)` -> HTTP 200, numFound 1
- `creator:(Fuchi)` -> HTTP 200, numFound 8
- `(title:(ICOT) OR subject:(ICOT) OR creator:(ICOT)) AND mediatype:(texts OR software)` -> HTTP 200, numFound 14
- `title:(PIMOS) OR subject:(PIMOS)` -> HTTP 200, numFound 0
- `title:("parallel inference machine") OR subject:("parallel inference machine")` -> HTTP 200, numFound 0
- `title:(KL1) OR subject:(KL1)` -> HTTP 200, numFound 22
- `title:(SIMPOS) OR subject:(SIMPOS)` -> HTTP 200, numFound 1
- `title:("Multi-PSI") OR subject:("Multi-PSI")` -> HTTP 200, numFound 0
- `title:("PSI machine") OR subject:("PSI machine") OR title:("personal sequential inference")` -> HTTP 200, numFound 0
- `title:("New Generation Computing")` -> HTTP 200, numFound 7
- `creator:("Institute for New Generation Computer Technology") OR publisher:("Institute for New Generation Computer Technology") OR title:("Institute for New Generation Computer Technology")` -> HTTP 200, numFound 0
- `title:("ICOT Journal") OR title:("新世代コンピュータ") OR title:("第五世代コンピュータ")` -> HTTP 200, numFound 0
- `title:(KLIC) AND mediatype:(texts OR software)` -> HTTP 200, numFound 61
- `title:("ESP language") OR title:("extended self-contained prolog") OR subject:("ESP (Computer program language)")` -> HTTP 200, numFound 1
- `title:(guarded horn clauses) OR title:(concurrent prolog) OR title:(parlog)` -> HTTP 200, numFound 10
- `title:(logic programming sixth international conference)` -> HTTP 200, numFound 0
- `title:(logic programming) AND creator:(Levi OR Martelli)` -> HTTP 200, numFound 0
- `title:(fifth generation computer systems 1984) OR title:(fifth generation computer systems 1988)` -> HTTP 200, numFound 2
- `title:(international conference fifth generation computer systems) AND mediatype:texts` -> HTTP 200, numFound 1
- `collection:(pub_new-generation-computing)` -> HTTP 200, numFound 0
- `title:(Programming of future generation computers) OR title:(Peogramming)` -> HTTP 200, numFound 1
- `title:(distributed prolog) OR creator:(Wise, Michael J)` -> HTTP 200, numFound 35
- `title:(ICOT) AND mediatype:software` -> HTTP 200, numFound 0
- `title:(fifth generation) AND mediatype:software` -> HTTP 200, numFound 3
- `subject:("Fifth generation computers") AND mediatype:texts` -> HTTP 200, numFound 9
- `title:(parallel logic programming) OR title:(parallel inference)` -> HTTP 200, numFound 25
- `creator:(Ueda, Kazunori) OR creator:(Chikayama) OR creator:(Taki, Kazuo)` -> HTTP 200, numFound 13
- `title:(fifth generation) AND (title:(Japan) OR title:(Japanese)) AND mediatype:texts` -> HTTP 200, numFound 4
- `title:(prolog) AND title:(machine) AND mediatype:texts` -> HTTP 200, numFound 2
- `collection:"pub_new-generation-computing"` -> HTTP 200, numFound 0
- `identifier:sim_new-generation-computing*` -> HTTP 200, numFound 0
- `title:("new generation computer systems")` -> HTTP 200, numFound 1
#### Open Library search.json (https://openlibrary.org/search.json?q=<Q>&fields=key,title,first_publish_year,ia,ebook_access,publisher&limit=20)
- `title:"Fifth generation computer systems" 1988`
- `title:"Fifth generation computer systems" 1984`
- `title:"Implementations of distributed Prolog"`
- `title:"Programming of future generation computers"`
- `title:"Logic programming" "sixth international conference"`
- `ICOT "Institute for New Generation Computer Technology"`
#### Wayback CDX (https://web.archive.org/cdx/search/cdx?<params>)
- `url=icot.or.jp&matchType=domain&collapse=urlkey&fl=original,timestamp,statuscode,mimetype,length&limit=20000` -> HTTP 200, 20000 rows
- `url=klic.org&matchType=domain&collapse=urlkey&fl=original,timestamp,statuscode,mimetype,length&limit=20000` -> HTTP 200, 1928 rows
- `url=jipdec.or.jp/archives/icot*&collapse=urlkey&fl=original,timestamp,statuscode,mimetype,length&limit=20000` -> HTTP 200, 356 rows
- `url=www.jipdec.or.jp/icot*&collapse=urlkey&fl=original,timestamp,statuscode,mimetype,length&limit=20000` -> HTTP 503, 14 rows
- `url=ftp.icot.or.jp*&collapse=urlkey&fl=original,timestamp,statuscode,mimetype,length&limit=20000` -> HTTP 200, 1180 rows
- `url=icot.or.jp&matchType=domain&collapse=urlkey&fl=original,timestamp,statuscode,mimetype,length&limit=20000&offset=20000` -> HTTP 503, 14 rows
  - NOTE: the two rows above logged as 'HTTP 200/503, 14 rows' for jipdec.or.jp/icot* and offset=20000 were Wayback 'Temporarily Offline' HTML error bodies, not data; retried below.
- `url=icot.or.jp&matchType=domain&collapse=urlkey&fl=original,timestamp,statuscode,mimetype,length&filter=urlkey:.*/ifs.*&limit=5000` -> HTTP 200, 1108 rows
- `url=icot.or.jp&matchType=domain&collapse=urlkey&fl=original,timestamp,statuscode,mimetype,length&filter=urlkey:.*%5C.(z%7Ctgz%7Cgz%7Cps%7Clzh%7Czip%7Ctar%7Cdvi)$&limit=5000` -> HTTP 200, 548 rows
- `url=icot.or.jp&matchType=domain&collapse=urlkey&fl=original,timestamp,statuscode,mimetype,length&filter=!urlkey:.*/(archive/museum%7Ccgi-bin%7Cfts%7Caitec)/.*&limit=5000` -> HTTP 504, 7 rows
- `url=www.icot.or.jp/ICOT/*&collapse=urlkey&fl=original,timestamp,statuscode,mimetype,length&limit=8000` -> HTTP 200, 835 rows
- `url=ftp://ftp.icot.or.jp/*&collapse=urlkey&fl=original,timestamp,statuscode,mimetype,length&limit=3000` -> HTTP 200, 1180 rows
#### GitHub repository search API (https://api.github.com/search/repositories?q=<Q>&per_page=30), unauthenticated
- `klic kl1` -> HTTP 200, total_count 1
- `kl1 in:name,description` -> HTTP 200, total_count 336
- `guarded horn clauses` -> HTTP 200, total_count 0
- `fghc` -> HTTP 200, total_count 38
- `pimos` -> HTTP 200, total_count 68
- `icot fifth generation` -> HTTP 200, total_count 0
- `KL1 parallel logic` -> HTTP 200, total_count 0
- `psi machine prolog emulator` -> HTTP 200, total_count 0
- `klic in:name language:C` -> HTTP 200, total_count 8
#### WebSearch tool (general web search), verbatim queries
- `KLIC KL1 to C compiler version 3.014 download Waseda Ueda` -> hits: GitHub KLIC mirror, AIST IFS abst 078/001, uedalab IFS abst 003, rosettacode KLIC, dbane.tilde.institute/klic.html
- `PSI machine ICOT "SIMPOS" emulator OR "ROM dump" OR "disk image" Prolog machine preservation` -> nothing relevant
- `"PIMOS" manual KL1 "Multi-PSI" FEP "front end processor" boot SCSI "PSI-III"` -> nothing relevant (unrelated instrument manuals)
- `PSI-II OR PSI-UX 逐次型推論マシン 実機 現存 OR 保存 OR 動態保存 SIMPOS` -> IPSJ museum MELCOM PSI page, softwarepreservation.org p53-Nishikawa.pdf, IPSJ repository records; nothing on surviving machines
#### Hacker News Algolia API (https://hn.algolia.com/api/v1/search?query=<Q>)
- `ICOT "fifth generation" PSI KL1` (tags=story)
- `"KL1" "ICOT"` (stories+comments)
- `"PIMOS" "KL1" manual "Multi-PSI" OR "PIM/m" "front end processor" OR "FEP" console "CSP"` -> nothing relevant
- `"Introduction to KL1" OR "KL1 programming" tutorial ICOT Chikayama PIMOS manual pdf` -> nothing relevant (PLC manuals)
- `cctalk OR vcfed "ICOT" "PSI" Prolog machine Mitsubishi "MELCOM PSI" surviving OR collector OR museum` -> IPSJ museum, ithistory.org/node/22506, CHM text 102785625, softwarepreservation prolog; no forum threads
- `"Common ESP" OR "CESP" ICOT AIR source code download "Extended Self-contained Prolog" unix` -> CMU AI Repository areas/icot (incl. manuals/esp), AIST IFS INFO/cesp-E.html, FOLDOC
- (archive.org advancedsearch) `title:("Prime Time Freeware")` -> HTTP 200, numFound 2
- (archive.org advancedsearch) `title:(freeware for AI) OR title:("AI Repository") OR title:("CMU Artificial Intelligence Repository")` -> HTTP 200, numFound 5
- (archive.org advancedsearch) `title:(PTF AI) OR title:("Prime Time") AND mediatype:software` -> HTTP 200, numFound 38
- (CDX) `url=ueda.info.waseda.ac.jp/software*&matchType=prefix&collapse=urlkey&fl=original,timestamp,statuscode,mimetype,length&limit=300` -> HTTP 200, 0 rows
- (CDX) `url=ueda.info.waseda.ac.jp&matchType=domain&collapse=urlkey&fl=original,timestamp,statuscode,mimetype,length&filter=urlkey:.*klic.*&limit=500` -> HTTP 503, 14 rows (ERROR BODY)
- (CDX retry) same ueda.info.waseda.ac.jp klic filter query -> HTTP 000, 14 rows
- (WebSearch) `"pimosobj.tar.Z" OR "psdpim.tar.Z" OR "pimosman.tar.Z" OR "vpim.tar.Z"` -> CMU AI Repository areas/icot listings (tgz re-packs), uedalab IFS abst 004; no other .tar.Z mirror
- (WebSearch) `第五世代コンピュータ PSI マシン 実機 展示 OR 所蔵 OR ジャンク OR 入手 "PSI-II" OR "PSI-III" OR "PSI/UX" 三菱 沖 ブログ` -> IPSJ museum, ithistory.org, kahaku PDF (unrelated), FGCS92Demo doc018; no blog on surviving units
- (WebSearch) `"Multi-PSI" OR "PIM/m" OR "PSI-II" ICOT emulator github OR simulator "KL1-B" OR "KL0" microcode` -> only IFS abstract pages; no emulator
- (GitHub repo search) `kl1 compiler concurrent logic` -> HTTP 200, total_count 0
- (GitHub repo search) `flat GHC concurrent logic language` -> HTTP 200, total_count 0
- (GitHub repo search) `KLIC concurrent logic programming` -> HTTP 200, total_count 0
- (GitHub repo search) `ICOT prolog` -> HTTP 200, total_count 1
- (GitHub repo search) `fifth generation computer ICOT` -> HTTP 200, total_count 0
- (GitHub repo search) `SIMPOS` -> HTTP 200, total_count 571
- (GitHub repo search) `PDSS KL1` -> HTTP 200, total_count 0
- (GitHub repo search) `Multi-PSI` -> HTTP 200, total_count 91
- (WebSearch) `classiccmp cctalk "fifth generation" ICOT "PSI" OR "PIM" Prolog machine anyone have` -> no mailing-list/forum threads
- (WebSearch) `"Multi-PSI Console System" OR "Multi-PSI CSP" OR "pimfep" OR "mpsicsp" operation manual` -> nothing relevant
- (WebSearch) `"Prime Time Freeware for AI" CD-ROM iso image download` -> CMU cdrom.html info page; no ISO
- (WebSearch) `KLIC "klic-3.003" OR "klic-3.005" OR "klic-3.01" FreeBSD ports OR pkgsrc OR Debian package distfiles` -> sources.debian.org klic 3.003-2 path; nothing for FreeBSD/pkgsrc
- (WebSearch) `"pimfep"` -> nothing relevant
- (WebSearch) `"Multi-PSI/V2 Console System Operation Manual"` -> nothing relevant
- (WebSearch, allowed_domains classiccmp.org, vcfed.org, forum.vcfed.org) `ICOT PSI Prolog machine fifth generation` -> no result from those domains
- (CDX) `url=klic.org/files*&matchType=prefix&fl=original,timestamp,statuscode,mimetype,length,digest&limit=200` -> HTTP 200, 0 bytes
- (CDX) `url=www.klic.org/software/klic/*&collapse=urlkey&fl=original,timestamp,statuscode,mimetype,length&limit=1500` -> HTTP 200, 75301 bytes
- (CDX) `url=icot.or.jp&matchType=domain&collapse=urlkey&fl=original,timestamp,statuscode,mimetype,length&filter=urlkey:.*(psi%7Csimpos%7Ckl0%7Cfep%7Cfirm%7Cmanual%7Cpim).*&limit=3000` -> HTTP 504 (error body)
- NOTE: Open Library numFound for the six queries above: 6, 3, 1, 3, 1, 1. HN Algolia nbHits: 0 and 1.

(Query logs for items 4-5 and for item 6 are inside those sections; fetches for items 1-2 are listed at the end of each.)

## Appendix E. Unlisted Technical Memoranda on hardware and KL1

PDFs present on the server but absent from `TMlist.html`; titles from the `TMidx/tmNNNN.idx` records (Appendix D 1.5). Columns: number, date, title as in the index record, authors, path under `Museum/TRTM/TM/`. Only TM-652, TM-662 and TM-1213 (section 8a) and the few named in "The other PIMs" were read.

| TM | Date | Title | Authors | PDF |
|---|---|---|---|---|
| TM-199 | 1986.08 | 情報処理学会　第33回全国大会論文集-4;並列推論マシンPIM | H.Hisano,N.Ito,M.Sato | TMpdf/tm0199.pdf |
| TM-200 | 1986.08 | 情報処理学会　第33回全国大会論文集-4;並列推論マシンPIM;中期構想 | A.Goto,M.Sugie,A.Hattori,N.Ito,S.Uchida | TMpdf/tm0200.pdf |
| TM-202 | 1986.08 | 情報処理学会　第33回全国大会論文集-4;並列推論マシンPIM;リダクション方式の評価 | M.Sugie,M.Yoneyama,M.Iwasaki,M.Sugaya,H.Shimizu,A.Matsumoto | TMpdf/tm0202.pdf |
| TM-204 | 1986.10 | 情報処理学会　第33回全国大会論文集-5;核言語KL1分散処理系;ソフトウェアシミュレータによる評価 | S.Torii,Y.Ohhara,E.Ono | TMpdf/tm0204.pdf |
| TM-210 | 1986.08 | 情報処理学会　第33回全国大会論文集-6;マルチPSI要素プロセッサPSI-IIのアーキテクチャ | K.Nakajima,K.Taki,O.Nakajima,T.Kyou,T.Ehara,A.Yamamoto,M.Yokota | TMpdf/tm0210.pdf |
| TM-211 | 1986.08 | 情報処理学会　第33回全国大会論文集-6;マルチPSI要素プロセッサPSI-IIの最適化手法 | H.Nakajima,T.Chikayama,K.Nakajima | TMpdf/tm0211.pdf |
| TM-212 | 1986.08 | 情報処理学会　第33回全国大会論文集-6;マルチPSI要素プロセッサPSI-IIのマイクロ・プログラム・シミュレータZEUS | M.Terayama,H.Yoshida,K.Nakajima | TMpdf/tm0212.pdf |
| TM-213 | 1986.08 | 情報処理学会　第33回全国大会論文集-6;マルチPSI要素プロセッサPSI-IIのメモリ管理とプロセス管理 | H.Yoshida,M.Ikeda,H.Nakajima,M.Yokota,K.Nakajima | TMpdf/tm0213.pdf |
| TM-230 | 1986.08 | 情報処理学会　第33回全国大会論文集-4;並列推論マシンPIM;中期PIMの処理方式 | M.Sata,H.Shimizu,T.Chikayama | TMpdf/tm0230.pdf |
| TM-232 | 1986.10 | 情報処理学会　第33回全国大会論文集-9;汎用アセンブラのPSI上への移植 | H.Tateno,S.Takagi | TMpdf/tm0232.pdf |
| TM-259 | 1987.02 | 情報処理学会　第34回全国大会論文集-3;マルチPSIにおける処理系動特性の評価 | E.Sugino,M.Furuichi,K.Inoue,T.Miyazaki,K.Taki | TMpdf/tm0259.pdf |
| TM-260 | 1987.02 | 情報処理学会　第34回全国大会論文集-3;マルチPSIにおける接続ネットワークの評価 | K.Masuda,H.Iwayama,Y.Ishizuka,Y.Suehara,K.Taki | TMpdf/tm0260.pdf |
| TM-261 | 1987.02 | 情報処理学会　第34回全国大会論文集-3;PSI-IIシステムのファームウェア | M.Ikeda,H.Tateno,A.yamamoto,H.yoshida,K.nakajima,Y.kimura,Y.Inamura | TMpdf/tm0261.pdf |
| TM-263 | 1987.02 | 情報処理学会　第34回全国大会論文集-4;並列推論マシンPIM(2)KL1の抽象命令仕様とコンパイラ | Y.Kimura,T.Chikayama,K.Kumon,H.nakajima | TMpdf/tm0263.pdf |
| TM-264 | 1987.02 | 情報処理学会　第34回全国大会論文集-4;並列推論マシンPIM(3)クラスタ内処理のメモリアクセス特性 | T.Nakagawa,A.Matsumoto,M.Sato,H.Shimizu,A.Goto | TMpdf/tm0264.pdf |
| TM-265 | 1987.02 | 情報処理学会　第34回全国大会論文集-4;並列推論マシンPIM(4)クラスタ内実験処理系 | M.Sato,H.Shimizu | TMpdf/tm0265.pdf |
| TM-266 | 1987.02 | 情報処理学会　第34回全国大会論文集-4;並列推論マシンPIM(5)並列キャッシュとロック機構 | A.Matusmoto,T.Nakagawa,A.Goto | TMpdf/tm0266.pdf |
| TM-268 | 1987.02 | 情報処理学会　第34回全国大会論文集-5;PIM-IIのシステム・アーキテクチャ | Y.Inamura,K.Nakajima,H.Nakajima,T.Tanabe,T.Fukasawa,O.Nose,T.Ehara,Y.Haneda | TMpdf/tm0268.pdf |
| TM-272 | 1987.02 | 情報処理学会　第34回全国大会論文集-5;並列推論マシンPIM;共有メモリ構造クラスタにおけるユニフィケーション | H.Shimizu,M.Sato | TMpdf/tm0272.pdf |
| TM-321 | 1987.07 | 情報処理学会 第35回全国大会論文集1;核言語KL1分散実行方式;ソフトウェアシュミレータによる評価 | Y.Ohhara,S.Torii,E.Ono,Y.Kanda | TMpdf/tm0321.pdf |
| TM-332 | 1987.07 | 情報処理学会 第35回全国大会論文集4-1;PIMの並列キャッシュ;共有バスの一構成法 | A.Matsumoto,T.Nakagawa,A.Goto | TMpdf/tm0332.pdf |
| TM-333 | 1987.07 | 情報処理学会 第35回全国大会論文集4-1;KL1の並列処理;密結合マルチプロセッサでの並列処理系での評価 | M.Sato,H.Shimizu,A.Goto | TMpdf/tm0333.pdf |
| TM-334 | 1987.07 | 情報処理学会 第35回全国大会論文集4-1;MRBによる多重参照管理方式;KL1処理系における一括型GCの特性評価 | N.Miyauchi,Y.Kimura,T.Chikayama,K.Kumon | TMpdf/tm0334.pdf |
| TM-336 | 1987.07 | 情報処理学会 第35回全国大会論文集4-1;ポインタタグ(MRB)による多重参照管理方式 | T.Chikayama,Y.Kimura | TMpdf/tm0336.pdf |
| TM-337 | 1987.07 | 情報処理学会 第35回全国大会論文集4-1;MRBによる多重参照管理方式 | K.Nishida,A.Matsumoto,Y.Kimura,A.Goto | TMpdf/tm0337.pdf |
| TM-346 | 1987.07 | 情報処理学会 第35回全国大会論文集4-1マルチPSI第2版のPE間アドレス管理方法 | K.Rokusawa,N.Ichiyoshi,T.Miyazaki,T.Chikayama,K.Taki | TMpdf/tm0346.pdf |
| TM-348 | 1987.07 | 情報処理学会 第35回全国大会論文集4-1並列論理型OS-PIMOS(2) 開発支援KL1処理系 | T.Miyazaki,Y.Kimura | TMpdf/tm0348.pdf |
| TM-353 | 1987.07 | 情報処理学会 第35回全国大会論文集4-2PS1-IIにおけるESPサポート用ファームウェア | M.Ikeda,M.Murasawa,H.Yoshida,T.Chikayama | TMpdf/tm0353.pdf |
| TM-354 | 1987.07 | 情報処理学会 第35回全国大会論文集4-2PS1-IIにおけるKL0実行順序系組み込み述語の実現方式 | H.Nakajima,H.Tateno,Y.Kimura | TMpdf/tm0354.pdf |
| TM-355 | 1987.07 | 情報処理学会 第35回全国大会論文集4-2PSI-IIのコンパイラ | S.Kondo,T.Sato,T.Chikayama | TMpdf/tm0355.pdf |
| TM-356 | 1987.07 | 情報処理学会 第35回全国大会論文集4-2PSI-IIの性能評価(1) | K.Nakajima,Y.Inamura,H.Nakajima,S.Kondo,H.Yoshida | TMpdf/tm0356.pdf |
| TM-357 | 1987.07 | 情報処理学会 第35回全国大会論文集4-2PSI-IIの性能評価(2);機械語命令評価 | Y.Inamura,S.Kondo,K.Nakajima | TMpdf/tm0357.pdf |
| TM-358 | 1987.07 | 情報処理学会 第35回全国大会論文集4-2PSI-IIの性能評価(3)マイクロ命令動的評価 | H.Yoshida,H.Nakajima,K.Nakajima | TMpdf/tm0358.pdf |
| TM-359 | 1987.07 | 情報処理学会 第35回全国大会論文集4-2;マルチPSI第2版のハードウェア構成 | Y.Takeda,H.Nakajima,K.Masuda,K.Taki | TMpdf/tm0359.pdf |
| TM-363 | 1987.07 | 情報処理学会 第35回全国大会論文集4-2並列論理型OS-PIMOS(1);資源管理方法 | H.Sato,M.Koshimura,T.Chikayama,K.Taki | TMpdf/tm0363.pdf |
| TM-396 | 1987.07 | 情報処理学会 第35回全国大会論文集4-2;KL1の並列処理;実用規模KL1プログラムの動特性評価 | S.Hosoi,M.Kishimoto,K.Kumon,A.Hattori | TMpdf/tm0396.pdf |
| TM-432 | 1988.03 | 学会発表論文(PSI PIM)第4研究室 PIMOSのタスク管理方式;タスク終了時の資源解放 | M.Matsuo,T.Fujise,H.Sato,T.Chikayama | TMpdf/tm0432.pdf |
| TM-438 | 1988.01 | 学会発表論文(PSI PIM)第4研究室 KL1コンパイラにおけるコード生成の最適化 | Y.Kimura,D.Sekita,T.Chikayama | TMpdf/tm0438.pdf |
| TM-443 | 1988.01 | 学会発表論文(PSI PIM)第4研究室 並列処理における重みつき参照カウントを用いた実時間GC | N.Ichioshi,K.Rokusawa,T.Chikayama,K.Nakajima,T.Miyazaki,E.Sugino | TMpdf/tm0443.pdf |
| TM-452 | 1988.01 | 学会発表論文（PSI PIM）第4研究室 並列処理におけるPE間に渡るゴールの重みつき参照カウントを用いた管理方式 | K.Rokusawa,N.Ichiyoshi,K.Taki,K.Yoshida,Y.Inamura,H.Nakajima | TMpdf/tm0452.pdf |
| TM-454 | 1988.01 | 学会発表論文（PSI PIM）第4研究室 KL1による簡易OS-MicroPIMOS | Y.Nakagoshi,K.Hirano,Y.Miyazaki,S.Nishizaki,T.Miyazaki | TMpdf/tm0454.pdf |
| TM-455 | 1988.01 | 学会発表論文（PSI PIM）第4研究室 汎用計算機上のKL1処理系におけるメモリ管理とデッドロックの検出 | K.Hirano,Y.Nakagoshi,Y.Miyazaki,S.Nishizaki,T.Miyazaki | TMpdf/tm0455.pdf |
| TM-521 | 1988.09 | 情報処理学会第37回全国大会論文集-2;(推論マシン関係)PSI/SIMPOSのネットワーク環境;TELNET機能(TCP/IP) | K.Amanuma,Y.Azuma,M.Hoshi,J.Tsuchikawa | TMpdf/tm0521.pdf |
| TM-522 | 1988.09 | 情報処理学会第37回全国大会論文集-2;(推論マシン関係)PSI/SIMPOSのネットワーク環境;リモートオブジェクト機構を用いた運用管理の試作 | K.Mori,K.Yoshida,H.Fukui,K.Ishihara | TMpdf/tm0522.pdf |
| TM-526 | 1988.09 | 情報処理学会第37回全国大会論文集-2;(推論マシン関係)並列推論マシンPIM/sの概要 | A.Goto,T.Shinogi,K.Kumon,A.Hattori | TMpdf/tm0526.pdf |
| TM-527 | 1988.09 | 情報処理学会第37回全国大会論文集-2;(推論マシン関係)LRCによる多重参照管理方式 | A.Goto,T.Chikayama | TMpdf/tm0527.pdf |
| TM-530 | 1988.09 | 情報処理学会第37回全国大会論文集-2;(推論マシン関係)PIM/pのネットワーク | K.Kumon,A.Hattori,A.Goto | TMpdf/tm0530.pdf |
| TM-531 | 1988.09 | 情報処理学会第37回全国大会論文集-2;(推論マシン関係)並列推論マシンPIM/pの要素プロセッサのアーキテクチャ | T.Shinogi,A.Matsumoto,T.Chikayama,A.Goto,A.Hattori | TMpdf/tm0531.pdf |
| TM-532 | 1988.09 | 情報処理学会第37回全国大会論文集-2;(推論マシン関係)PIMOSの設計方針 | H.Sato,M.Koshimura,T.Chikayama,T.Fujise,M.Matsuo,K.Wada | TMpdf/tm0532.pdf |
| TM-539 | 1988.09 | 情報処理学会第37回全国大会論文集-2;(推論マシン関係)LRCによるインクリメンタルGCの評価 | N.Miyauchi,T.Nakagawa | TMpdf/tm0539.pdf |
| TM-551 | 1988.09 | 情報処理学会第37回全国大会論文集-2;(推論マシン関係)分散環境におけるユニフィケーションの実現 | K.Rokusawa,N.Ichiyoshi,T.Chikayama,H.Nakajima | TMpdf/tm0551.pdf |
| TM-564 | 1988.09 | 情報処理学会第37回全国大会論文集-2;(推論マシン関係)PIMOS上でのシェルの実現;共有資源管理 | M.Matsuo,T.Fujise,H.Sato,T.Chikayama | TMpdf/tm0564.pdf |
| TM-565 | 1988.09 | 情報処理学会第37回全国大会論文集-2;(推論マシン関係)PIMOSの例外処理方式 | M.Koshimura,M.Matsuo,T.Fujise,H.Sato,T.Chikayama | TMpdf/tm0565.pdf |
| TM-572 | 1988.09 | 情報処理学会第37回全国大会論文集-2;(推論マシン関係)PSI-IIの性能評価 | H.Tateno,S.Kondo,H.Nakajima,M.Ikeda,K.Nakajima | TMpdf/tm0572.pdf |
| TM-652 | 1989.06 | 情報処理学会 第38回全国大会論文集III;KLI抽象命令セットの改良について | Y.Kimura,A.Goto,K.Nakajima,T.Chikayama | TMpdf/tm0652.pdf |
| TM-653 | 1989.06 | 情報処理学会 第38回全国大会論文集III;KL1クローズインデキシング方式の評価 | S.Nishizaki,K.Hirano,N.Takei,K.Morita,Y.Kimura | TMpdf/tm0653.pdf |
| TM-662 | 1989.06 | 情報処理学会 第38回全国大会論文集III;マルチPSI/V2におけるコード形式について | Y.Miyazaki,Y.Nakagoshi,Y.Douzen,Y.Inamura,Y.Kimura,K.Nakajima | TMpdf/tm0662.pdf |
| TM-671 | 1989.06 | 並列処理シンポジュームJSPP'89での発表論文;マルチPSIにおけるデバッグ機能・メンテナンス機能 | E.Sugino,S.Furuichi,Y.Inamura,K.Taki | TMpdf/tm0671.pdf |
| TM-687 | 1989.06 | 情報処理学会 第38回全国大会論文集III;密結合マルチプロセッサ上のKL1並列処理系の評価 | S.Hosoi,T.Ozawa,M.Feldman,A.Hattori | TMpdf/tm0687.pdf |
| TM-766 | 1989.07 | 第38回情報処理学会 全国大会論文集（4研関連）並列推論マシンPIM/k;ハードウェアアーキテクチャ | S.Asano | TMpdf/tm0766.pdf |
| TM-767 | 1989.07 | 第38回情報処理学会 全国大会論文集（4研関連）Multi-PSI/V2における一括GC及びメモリ消費特性の評価 | N.Miyauchi,Y.Kawata,K.Nakajima | TMpdf/tm0767.pdf |
| TM-768 | 1989.07 | 第39回情報処理学 会全国大会論文集（4研関連）分散環境における構造体管理 | K.Rokusawa,T.Chikayama,H.Nakashima,K.Taki,N.Ichiyoshi,K.Nakajima,Y.Inamura | TMpdf/tm0768.pdf |
| TM-770 | 1989.07 | 第38回情報処理学会 全国大会論文集（4研関連）MRB-GCの評価;アクティブセル量とヒープ消費 | N.Takei,K.Hirano,S.Nisizaki,K.Morita,Y.Kimura,T.Chikayama | TMpdf/tm0770.pdf |
| TM-775 | 1989.07 | 第38回情報処理学会 全国大会論文集（4研関連）PIMOSの評価 | H.Sato,M.Hoshida,T.Chikayama,T.Fujise | TMpdf/tm0775.pdf |
| TM-779 | 1989.07 | 第38回情報処理学会 全国大会論文集（4研関連）並列推論マシンPIM/pの要素プロセッサにおける分岐機能の高速化のためのアーキテクチャ | T.Shinogi,K.Kumon,A.Asato,A.Hattori,T.Chikayama,A.Goto | TMpdf/tm0779.pdf |
| TM-798 | 1989.07 | 第38回情報処理学会 全国大会論文集（4研関連）共有メモリ結合マルチプロセッサにおけるKL1向きガーベジコレクション;MRBを用いた最適化と並列実行 | A.Imai,H.Kawai,T.Nakagawa,K.Nakajima,A.Goto | TMpdf/tm0798.pdf |
| TM-846 | 1989.12 | 情報処理学会 第40回全国大会論文集;並列推論マシンPIM/iの概要 | T.Oohara,K.Takeda,M.Sato | TMpdf/tm0846.pdf |
| TM-847 | 1989.12 | 情報処理学会 第40回全国大会論文集;並列推論マシンPIM/iの要素プロセッサのアーキテクチャ | K.Takeda,T.Oohara,M.Sato | TMpdf/tm0847.pdf |
| TM-849 | 1989.12 | 情報処理学会 第40回全国大会論文集;マイクロコード・チェッカ「マイクロリント」の開発 | S.Miyauchi,N.Ichiyoshi | TMpdf/tm0849.pdf |
| TM-850 | 1989.12 | 情報処理学会 第40回全国大会論文集;PIM/m要素プロセッサのアーキテクチャ | H.Nakajima,Y.Takeda,K.Nakajima | TMpdf/tm0850.pdf |
| TM-870 | 1990.03 | 情報処理学会 第40回全国大会論文集;並列推論マシンPIM/c概要 | A.Goto,K.Taki,T.Nakagawa,M.Sugie | TMpdf/tm0870.pdf |
| TM-911 | 1990.08 | 情報処理学会 第41回全国大会論文集;並列推論マシンPIMの処理系の概要 | E.Kuno,M.Sato | TMpdf/tm0911.pdf |
| TM-912 | 1990.08 | 情報処理学会 第41回全国大会論文集;共有メモリ結合マルチプロセッサ上でのKL1処理系ユニフィケーション | Y.Doumae,A.Imai,A.Goto | TMpdf/tm0912.pdf |
| TM-918 | 1990.08 | 情報処理学会 第41回全国大会論文集;共有メモリマルチプロセッサにおける効率的なKL1ストリーママージ処理方式 | A.Imai,Y.Inamura,A.Goto | TMpdf/tm0918.pdf |
| TM-920 | 1990.08 | 情報処理学会 第41回全国大会論文集;メッセージの追い越しがある分散環境における低コストな外部参照管理 | K.Rokusawa,A.Nakase,H.Kawai,A.Imai | TMpdf/tm0920.pdf |
| TM-921 | 1990.08 | 情報処理学会 第41回全国大会論文集;並列推論マシンPIM/iのファイングレインパラレリズム | K.Kato,M.Sato,K.Y.Takeda,T.Oohara | TMpdf/tm0921.pdf |
| TM-922 | 1990.08 | 情報処理学会 第41回全国大会論文集;並列推論マシンPIM/iの開発支援環境;翻訳系 | M.Sato,E.Kuno | TMpdf/tm0922.pdf |
| TM-923 | 1990.08 | 情報処理学会 第41回全国大会論文集;並列推論マシンPIM/iの開発支援環境;シミュレータ | Y.Yoshida,M.Sato,T.Oohara | TMpdf/tm0923.pdf |
| TM-929 | 1990.08 | 情報処理学会 第41回全国大会論文集;並列推論マシンPIM/iのメモリシステムの概要 | K.Takeda,M.Sato,T.Oohara | TMpdf/tm0929.pdf |
| TM-1000 | 1991.02 | 第42回情報処理学会 全国大会発表論文集II;並列推論マシンPIM/c;水平型マイクロプログラムの自動生成と最適化 | S.Hayaki,T.Mori,T.Kitta,H.Imanishi,T.Nakagawa,M.Sugie | TMpdf/tm1000.pdf |
| TM-1010 | 1991.02 | 第42回情報処理学会 全国大会発表論文集II;クラスタ間メモリ共有型アーキテクチャにおけるKL1処理系の考察 | H.Sakai,A.Nakase,T.Takewaki | TMpdf/tm1010.pdf |
| TM-1011 | 1990.02 | 第42回情報処理学会 全国大会発表論文集II;並列推論マシンPIM/kの開発(1)KL1処理系のデバッグ手法とツール | K.Oki,H.Tanno,H.Sakai,A.Nakase,T.Takewaki | TMpdf/tm1011.pdf |
| TM-1012 | 1991.02 | 第42回情報処理学 会全国大会発表論文II;並列推論マシンPIM/kの開発(2)KL1処理系の予備評価 | H.Tanno,K.Oki,H.Sakai,A.Nakase,T.Takewaki | TMpdf/tm1012.pdf |
| TM-1013 | 1991.02 | 第42回情報処理学会 全国大会発表論文集II;メッセージの追い越しがある分散環境におけるプロセスの実行停止/再開方式 | K.Rokusawa,R.Yamamoto,H.Kawai,A.Imai,A.Nakase | TMpdf/tm1013.pdf |
| TM-1014 | 1991.02 | 第42回情報処理学会 全国大会発表論文集II;並列推論マシンPIM/iにおける実行履歴の利用 | Y.Yoshida,M.Sato | TMpdf/tm1014.pdf |
| TM-1015 | 1991.02 | 第42回情報処理学会 全国大会発表論文集II;並列推論マシンPIM/iの要素プロセッサのアーキテクチャ評価 | K.Takeda,M.Sato,T.Oohara | TMpdf/tm1015.pdf |
| TM-1016 | 1991.02 | 第42回情報処理学会 全国大会発表論文集II;並列推論マシンPIM/iのメモリシステムの評価;並列キャッシュ | T.Oohara,K.Takeda,M.Sato | TMpdf/tm1016.pdf |
| TM-1017 | 1991.02 | 第42回情報処理学会 全国大会発表論文集II;並列推論マシンPIM/iのタグアーキテクチャの評価 | K.Kato,M.Sato,K.Takeda,T.Oohara | TMpdf/tm1017.pdf |
| TM-1018 | 1991.02 | 第42回情報処理学会 全国大会発表論文集II;並列推論マシンPIM/iにおけるゴール通信方式の評価 | E.Kuno,M.Sato | TMpdf/tm1018.pdf |
| TM-1019 | 1991.02 | 第42回情報処理学会 全国大会発表論文集II;並列推論マシンPIM/iにおける分岐特性 | M.Sato,K.Takeda,T.Oohara | TMpdf/tm1019.pdf |
| TM-1021 | 1991.02 | 第42回情報処理学会 全国大会発表論文集II;PIM/mフロントエンド・プロセッサ;GC方式とその評価 | H.Tateno,Y.Kawada,K.Takahashi,M.Ikeda | TMpdf/tm1021.pdf |
| TM-1022 | 1991.02 | 第42回情報処理学 会全国大会発表論文集II;PIM/mフロントエンド・プロセッサの速度性能評価 | M.Saeki,H.Nakashima,H.Tateno,M.Ikeda,R.Tajima | TMpdf/tm1022.pdf |
| TM-1046 | 1991.05 | 並列処理シンポジウム91発表論文集;並列推論マシンPIM/iの命令レベル並列性の評価 | T.Oohara,K.Takeda,M.Sato | TMpdf/tm1046.pdf |
| TM-1047 | 1991.05 | 並列処理シンポジウム91発表論文;集WTCを用いた分散プロセス制御方式 | K.Rokusawa,N.Ichiyoshi | TMpdf/tm1047.pdf |
| TM-1090 | 1991.08 | 第43回 情報処理学会 全国大会論文集;並列推論マシンPIM/pのシュミレータ | T.Mitsuyu,S.Arai,N.Takei | TMpdf/tm1090.pdf |
| TM-1091 | 1991.08 | 第43回 情報処理学会 全国大会論文集;並列推論マシンPIM/pへのKL1処理系の実装 | H.Hatazawa,Y.Nakagoshi,Y.Miyazaki,K.Hirano | TMpdf/tm1091.pdf |
| TM-1092 | 1991.08 | 第43回 情報処理学会 全国大会論文集;大域GCにおけるWTC方式を用いたマーキング終了検出 | K.Rokusawa,K.Nakajima,N.Ichiyoshi,Y.Inamura | TMpdf/tm1092.pdf |
| TM-1093 | 1991.08 | 第43回 情報処理学会 全国大会論文集;並列推論マシンPIM/iの並列キャッシュ機構の評価 | T.Oohara,K.Takeda,M.Sato | TMpdf/tm1093.pdf |
| TM-1095 | 1991.08 | 第43回 情報処理学会 全国大会論文集;並列推論マシンPIM/iにおけるバスの振る舞い | Y.Yoshida,M.Sato,E.Kuno | TMpdf/tm1095.pdf |
| TM-1096 | 1991.08 | 第43回 情報処理学会 全国大会論文集;並列推論マシンPIM/iの命令セットの評価 | K.Kato,M.Sato | TMpdf/tm1096.pdf |
| TM-1097 | 1991.08 | 第43回 情報処理学会 全国大会論文集;並列推論マシンPIM/i向きKL1言語処理系の評価 | E.Kuno,M.Sato,Y.Yoshida | TMpdf/tm1097.pdf |
| TM-1098 | 1991.08 | 第43回 情報処理学会 全国大会論文集;KL1のRISC風PIM/i命令への展開について | M.Sato,K.Takeda,K.Kato | TMpdf/tm1098.pdf |
| TM-1127 | 1991.10 | 情報処理学会v第43回全国大会論文集;PIM/pにおけるパイプライン制御方式 | A.Asato,M.Kimura,T.Shinogi,A.Hattori | TMpdf/tm1127.pdf |
| TM-1213 | 1992.10 | 情報処理学会 第45回全国大会論文集;PIM/mのメンテナンス系アーキテクチャとCSP | K.Takahashi,Y.Takeda,Y.Murasawa,R.Komori,E.Sugino | TMpdf/tm1213.pdf |
| TM-1247 | 1993.03 | 情報処理学会 第46回全国大会論文集;並列推論マシンPIM/iにおけるKL1言語処理系の改良 | K.Kato,E.Kuno,K.Rokusawa,K.Takeda,T.Oohara | TMpdf/tm1247.pdf |
| TM-1248 | 1993.03 | 情報処理学会 第46回全国大会論文集;並列推論マシンPIM/iのバスの動特性の解析 | K.Takeda,T.Oohara | TMpdf/tm1248.pdf |
