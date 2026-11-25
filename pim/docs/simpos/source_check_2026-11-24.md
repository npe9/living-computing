# Primary-source check, 2026-11-24

The owner's instruction: "Keep checking primary sources." This record
audits what `pim/` has built against the primary sources held:

- the ICOT TRs and TMs;
- the printed SIMPOS listings (`printed/`);
- the held ICOT Free Software and PIMOS archives (`../nonlocal/`) and
  their source;
- the PIMOS manuals;
- the IPSJ papers.

The questions were: what rests on inference where a source settles it,
and what does a source contradict?

**Nothing under `pim/psi/` was edited.** Another agent is changing it.
Every change proposed for `pim/psi/` is in §5, ready to apply.

The docs outside `psi/` were corrected in place:

- `../binary_reverse_engineering.md` §1.4: the shutdown lines, and the
  `getb` rows;
- `../fep_services.md` §2.2: `getb`;
- `../environment_audit.md`: the `fep.py` row;
- `subsystems/window.md`: the `create/4` citations.

## Contents

1. [How the check was done](#how-the-check-was-done)
2. [Counts](#counts)
3. [§1 The stand-ins](#1-the-stand-ins-psistandin)
4. [§2 The KL0 opcode table](#2-the-kl0-opcode-table-psikl0_opcodestsv)
5. [§3 The PIMOS shutdown output](#3-the-pimos-shutdown-output)
6. [§4 FEP protocol claims marked OURS or INFERENCE](#4-fep-protocol-claims-marked-ours-or-inference-in-fep_servicesmd)
7. [§5 Proposed changes to pim/psi/](#5-proposed-changes-to-pimpsi-ready-to-apply-not-applied)
8. [§6 Open after this check](#6-open-after-this-check)
9. [§7 Step 3f's INTERPOLATED and OURS parts, re-checked (2026-11-25)](#7-step-3fs-interpolated-and-ours-parts-re-checked-2026-11-25)
10. [§8 The rest of §7, re-checked in step 3h (2026-11-25)](#8-the-rest-of-7-re-checked-in-step-3h-2026-11-25)

## How the check was done

**The row tables.** Each item has one row in the two companion tables,
which are part of this record:

- `source_check_2026-11-24_standins.tsv` has 140 rows. Rows `SA01`-`SA59`
  and `sb001`-`sb081` give, for each, the file, class, method, current
  label, claim, source checked (with citation and a short quote), the
  verdict, and the proposed change.
- `source_check_2026-11-24_opcodes.tsv` has 126 rows: the 113 table rows,
  the 11 opcodes still missing, and 2 header claims.

§3 and §4 are written out below.

**Where the rows came from.** The rows were built from a script
skeleton of every labelled item in `psi/standin/*.esp`: 225 items, of
which 59 + 60 carry INTERPOLATED, OURS, INFERENCE or UNKNOWN. That
skeleton was then extended:

- process.esp's indented methods, which the skeleton missed;
- one row per header claim of the form "no part of X is printed or
  held";
- one row per PRINTED or HELD-SOURCE file, checked against its listing
  or held file.

**The verdicts.** Four verdicts were used:

- **CONFIRMED**: a primary source states it and agrees.
- **UPGRADED**: a printed or held statement of the item itself exists, so
  the label can move. An interface or result moves to READ; the body
  stays INTERPOLATED unless it is printed.
- **CONTRADICTED**: a primary source, or for an internal inconsistency
  the repository itself, says otherwise.
- **NO SOURCE FOUND**: the searches are listed.

A deviation the file already marks OURS was recorded as CONFIRMED (the
behaviour) with the deviation noted, not as a contradiction. An example
is "wait/1 returns at once: one process, no clock", where the real one
blocks.

**The corpus, and its limits.** The TR/TM PDFs have no text layer:
`pdftotext` gives under 3 kB for all 392. The search corpus was
therefore OCR text:

- 139 documents, 3,242 of the 6,592 held TR/TM pages;
- every page of the 76 SIMPOS/ESP/PSI-related held documents in
  `trtm_table.tsv`, except TM-305 (a Multi-PSI benchmark);
- the IPSJ OCR of `subsystems/notes/ipsj.md`.

An OCR hit was treated as a lead only. Every page that carries a
verdict was read as a page image, except four marked "OCR only" in the
stand-in table.

**The held archives.** These were extracted afresh into empty
directories and read with `python3 -I`:

- `pimos`, `pimosobj`, `pimosman`;
- `ifs/manuals/pimos/*` (the V1.5 manual `man15.ps`, the Japanese V3.0
  manual `man30.j.ps`, and the primers `primer25.tex` and
  `primer15.j.tex`);
- the ESP manuals (`ESPtex`, `ESPtex-j`);
- `kappa2`, and the 63 IFS SIMPOS/CESP/PIMOS application archives
  (2,286 `.esp` files);
- `psdpim`, `vpim`, `pdss` and `klic`.

The PSI packages were read with `psi/fepread/ptfread.py` (read-only).

**Coverage caveats.**

- A NO SOURCE FOUND row means "not found in this corpus", not "does not
  exist".
- The Japanese pages' OCR is poor; where a Japanese document was likely
  to be relevant, its page images were read.
- dvi2ps splits words in the PostScript manuals, so those were read by
  their positioned fragments, not by multi-word grep.

**Who did what.** Three delegated agents produced the row tables. The
lead spot-checked these citations against the held files and the OCR
text (greps, not page images, except TM-444 PDF p31, read as an
image), and they hold:

- CH_CLOCK.ESP:59-62;
- exshow.esp:24-28;
- kwic-esp inEditor1.esp:151;
- TM-161 p18 `with link / get_next / imp / 2`;
- TM-388 PDF p138 "cannot be saved in a slot";
- TR-056 PDF p14 "inherits class 'as_message'";
- TM-444's `get_var_var_list`, `put_unsafe_value` and
  `unify_local_value_t`.

## Counts

| Part | Rows | CONFIRMED | UPGRADED | CONTRADICTED | NO SOURCE FOUND |
|---|---|---|---|---|---|
| §1 stand-ins (labelled methods, header claims, PRINTED/HELD files) | 140 | 88 | 10 | 8 | 34 |
| §2 opcode table rows | 113 | 88 | 13 | 0 | 12 |
| §2 header claims (opcode names / numbers) | 2 | 1 | 0 | 1 | 0 |
| §3 shutdown lines | 9 | 5 | 2 | 1 | 1 |
| §4 FEP claims marked OURS or INFERENCE | 20 | 6 | 1 | 1 | 12 |
| **Total** | **284** | **188** | **26** | **11** | **59** |

The 11 opcodes still missing from the table are in §2. They are
findings, not verdicts.

## §1 The stand-ins (`psi/standin/`)

Full rows: `source_check_2026-11-24_standins.tsv`.

**Checked and found exact:**

- The PRINTED files are exact transcriptions of their page images:
  - `stream`, `channel`, `bounded_channel`, `bounded_post_queue`: token
    diff against `printed/listings` plus the images;
  - `stream` differs only in its 3 marked corrections;
  - `process` (printed parts against `tm0100_p07`-`p10`).
- The HELD-SOURCE files `e_string`, `name` and `pathname` match morphana
  `_simpos/*.esp`. They differ only in the `[CESP, kept]` marks and the 7
  marked pathname restorations. All 34 `HELD-SOURCE: file:N` labels point
  at the right held line.

### CONTRADICTED (8)

| Row | Claim (where) | Source | Verdict and fix (§5) |
|---|---|---|---|
| sb001 | `semaphore.esp` header: "no part of `semaphore` is printed" | TR-056 PDF p13 (folio 11) prints `:p(Semaphore) :- :get(Semaphore,Token).`, `:v(Semaphore) :- :put(Semaphore,token).`, `:init(Semaphore)`, `:init(Semaphore,Count)`. This is a semaphore built on a stream: the 1984 design, with other selectors than TM-100's `p_operation`/`v_operation` | Header wrong. The p/v behaviour (take a token, give one back, Count tokens) agrees with the stand-in |
| sb008 | `list_index.esp` header: entries are the term `{Next, Object, Key}` | TM-388 PDF p138 (folio 126): a stack vector "cannot be saved in a slot. Consequently, a compound term and a list cannot be saved in a slot". TM-161 PDF p18 names `index_entry`, `list_entry` and `with_link` methods. KPPOOL.ESP:35-43 gives the positions 0 next, 1 object, 2 key | The positions are right. The written form is OURS: SIMPOS's entry was a heap vector or an object |
| sb068 | `symbolizer.esp` `string_to_list/3`: works with List bound | TM-115 PDF p98 (folio 93): `string_to_list` "cannot be used with the result already instantiated", fixed by `:string_to_list(#symbolizer,L,String), !, L = List` | The stand-in succeeds where SIMPOS did not. Label it OURS |
| sb074 | `stream.esp` header: waiting_queue, post_queue, inhibit/allow_interrupt, resume/suspend have "no stand-in yet" | the repository: `waiting_queue.esp` and `post_queue.esp` exist; `process.esp` defines them at :81, :92, :94, :248, :283 | Stale header |
| sb081 | `pathname.esp` header: `remove_or_local/6` | held callers spell it `remote_or_local/6`: cil `ms_ist.esp`:251, 1668, 1793; `ds_fep.esp`:912; cal-esp `init.esp`:314 | Typo |
| SA36 | `pmacs_window.esp` header: create/4 "from disc/exshow.esp:23-35" | exshow.esp:24 is create/3 (`:create(#pmacs_window,[title(Buf)\|Init],W)`); its create/4 at :25 is `editor_text_buffer`'s. create/4 of pmacs_window is kwic-esp `src/inEditor1.esp`:151 and mendels `comp_win.esp`:54-62. Count over the IFS sources: about 85 create/3 sends, 3 create/4 | Citation wrong. Also wrong in `subsystems/window.md`, corrected there |
| SA42 | `standard_editor.esp` header: "class pmacs_window is not stood in, so no window is ever made" | the repository: `pmacs_window.esp` exists, and its create/3 sets `Editor!window` | Stale header |
| SA58 | `with_link.esp` header: "what it holds is not printed" | TM-161 PDF p18 (Tables 7, 8, a call-count profile) prints the row `with_link / get_next / imp / 2` (64,056 calls, 3.54%). TM-100 PDF p10: one of "two classes for chaining process instances" | A method name is printed: `get_next/2`, body not printed. That it is SIMPOS's with_link rests on the neighbouring SIMPOS rows |

### UPGRADED (10)

| Row | Item | Source | New label |
|---|---|---|---|
| SA08 | `as_class_with_lock:lock/1` (:unlock as its alternative) | kappa2 `utility/tool/LOADER.ESP`:144-146 (M. Ozawa, 1991-12-17): ":lock has :unlock as its own alternative, so no ! here". At :149-153 the unlock-on-failure clause is commented out as not needed | HELD-SOURCE statement of the behaviour; the code INTERPOLATED |
| SA12 | `message` nature `as_message` | TR-056 PDF p14 (folio 12): "Class 'message' inherits class 'as_message' to include the first two slots" | PRINTED (prose) |
| SA13 | `message` slot `body` | TR-056 PDF p14: "a body (an object to be sent)" | PRINTED (prose); the slot's name `body` OURS |
| SA17 | `as_message` slots `sender`, `receiver` | TR-056 PDF p14: "a sender slot (a channel for reply, if available), a receiver slot (a channel to receive it)" | PRINTED (prose) |
| SA34 | `time` count: "the unit is UNKNOWN" | Held: gog-kl1 `ESP/CH_CLOCK.ESP`:59-62, `:set_count(Obj!time,MS+1000), % 1000 msec interval`. Supporting: PIMOS `server/fep/timer/time_dvc.kl1`:197-209 converts to `msec(C1)` before `fep#on_after`; manual `e-ioctrl.tex`:866 makes the millisecond the default unit; TR-274 PDF p3 gives PSI "a 1-millisecond built-in timer" | MILLISECONDS, HELD-SOURCE |
| sb002 | `semaphore` `nature waiting_queue` | TM-100 PDF p16 (folio 14) prose: "A semaphore which is a component of a bounded post queue inherits a waiting queue"; Fig. 3.9, PDF p17 | READ (prose and figure) |
| sb027 | `hash_index:get_at/3` | TM-161 PDF p14: get_at returns the object under the key, and fails when the search fails | READ (behaviour); body INTERPOLATED |
| sb053 | `list:add_first/2` | TM-161 PDF p12: a SIMPOS pool method that adds its second argument at the head of the list | READ; body INTERPOLATED |
| sb070 | `symbolizer:get_number/3` | ESP manual `ESPtex` `program-e.tex`:6748-6756 (also `program-j.tex`:6489): `:get_number(S,Number,"123")` gives `Number= 123` | READ (interface and the result); body INTERPOLATED |
| sb071 | `symbolizer:get_number_string/3` | `program-e.tex`:6757-6758: `String= "123"` | READ; body INTERPOLATED. `get_number_string/4` (radix, :6761-6762) exists and is not stood in |

### Found in passing (no verdict of their own)

- **kl0's unification compares strings by content.** `psi/kl0.py`,
  `Str.__eq__` does this. TM-388 PDF p79 (folio 67) says `'abc' = 'abc'`
  fails on the PSI; only `equal_string` compares the elements. A
  list_index stand-in keyed by strings happens to give SIMPOS's answer,
  because SIMPOS's list_index used a local `equal_key/2` (TM-161 p18).
  Any other path that relies on two equal strings unifying is off-PSI.
  **Proposed for a kl0 audit (§5, P-k1).**
- **The pool and queue stand-ins keep Prolog lists in slots.** These are
  list, post_queue, waiting_queue and list_index. TM-388 PDF p138
  forbids this on the PSI. Only `list.esp` discloses it.
- **TM-161 PDF p14 prints the arguments key first:**
  `:add_at(Hash,Key,Object)`. TR-056 PDF p8, the ESP manual
  (`program-e.tex`:6523, 6529) and every held caller put the object
  first. TM-161 is taken as the outlier.
- **Selectors held code sends that no stand-in has:**
  - `with_lock` and `as_class_with_lock` `locked/2`;
  - `time` `get_count/2` and `now/2`;
  - `alarm_watch` `on_at/2`;
  - `trace` `notrace/1,2`, and `trace/2` with a process number (cal-esp
    `deb2.12/util.esp`:217-227);
  - `hash_index` `put_at/3`;
  - `symbolizer` `get_number_string/4`.
- **`network_listener_buffer:create/4`'s integers.** They stay UNKNOWN.
  INFERENCE, with sources: the first is a length in elements and the
  second the element width in bits (16 or 32, the ESP string widths,
  TM-388 PDF p29). kappa2 `SRVCMD.ESP`:22 creates `(..,2048,16)`, and
  2048 x 16 bits = 4096 bytes. That is the 4096-byte buffer of kappa2
  `kernel/net/MSGCMD.ESP`:22 and :39.

### NO SOURCE FOUND (34)

These are listed in the table. The searches behind them, by group:

- **Locks, network, timer, trace, window objects.** The OCR corpus and
  the IPSJ OCR were searched for with_lock, lock/unlock/locked,
  common_network, is_installed, listener_buffer, alarm_watch,
  process_clock, set_count/get_count, forced_event, tag_catch, pmacs,
  standard_editor, get_editor/get_window, with_link and waiting_frame,
  with `[_ .-]?` variants, and for リスナ, バッファ, インストール and
  トレース in the Japanese documents. The same terms were searched in all
  IFS `.esp`, `classdefs.tsv`, the ESP and PIMOS manuals, and the class
  lists of the 11 held `.ptf` packages. None defines any of these
  classes.
- **Queues.** The pattern
  `waiting.?queue|post.?queue|waiting.?frame|p_operation|v_operation|semaphore|add_object|remove_object|unhook`
  was searched everywhere. Hits are only in TM-100 and TR-056 (read as
  images) and in unrelated prose.
- **Pool selectors.** The pattern
  `add_first|remove_first|remove_last|get_last|get_contents|get_keys|put_contents|add_after|add_before|stick_tap|list_index|hash_index|get_first|add_last`
  was searched with OCR-tolerant gaps. Read as images: TR-056 PDF pp4-14,
  TM-100 pp8-18, TM-161 pp12-14 and p18, and TM-388's contents. TM-388
  has no "basic classes" chapter; PDF p144 points to a section 6.1 that
  is not in it.
- **The PSI hash function (`hash/2`, blt 6b).** `h[a]sh` was searched in
  every English OCR page, with zero hits in tr0045, tr0075, tr0142,
  tm0001, tr0013 and tr0274. `ハッ ?シュ` was searched in the Japanese
  ones. Read: TR-044 PDF p41 (signature only), TR-005 PDF p5 ("a
  standard hashing function"), TR-056 PDF p9, and TM-444 PDF p12 and p15
  (clause indexing `hash_on_value` by low bits, not `hash/2`).
  `cil_kl0.esp` has the name only. **The real hash function stays lost.**
- **Strings.** `symbolizer|#string|string.{0,3}to.{0,3}list|get_number`
  was searched. A scan of 2,335 held `:append(#string,[...])` lines found
  no element that is not a string.

## §2 The KL0 opcode table (`psi/kl0_opcodes.tsv`)

Full rows: `source_check_2026-11-24_opcodes.tsv`.

**Two primary documents print the KL0 instruction mnemonics.** No held
document prints the opcode NUMBERS. So a primary source confirms an
opcode's meaning by mnemonic or built-in name only, and the link from
number to name always rests on the witness. The two documents (pages
read as images) are:

- **TM-444** (PSI-II KL0 implementation, Jan 1988):
  - PDF p6-16 and p30-31;
  - argument register first in two-operand forms, p15;
  - the try family, p9-10;
  - indexing `hash_on_value`, `jump_on_value`, `jump_on_non_list` and
    `jump_on_non_constant`, p11-13;
  - the cuts, p14;
  - the merged instructions, including `get_var_var_list`, p16;
  - `put_unsafe_value`, `put_local_value` and `unify_local_value_t/_p`,
    p30-31.
- **TR-236** PDF p5 Fig. 1.

Also: TR-044 App. A (PDF p38-41) gives the built-in names and argument
modes, and the held `cil_kl0.esp` gives built-in names and arities.

**Header claims (2 rows).**

- **CONTRADICTED:** "Opcode NAMES are not known (no KL0 instruction table
  is held)" (`asm/ptfdump.py`:33) and "Opcode names are not from a
  document: none is held" (`psi/fepread/README.md`:23). The mnemonics
  are printed (TM-444, TR-236).
- **CONFIRMED:** that no held document gives the NUMBERS (`witness.py`).

**Witnesses re-checked.**

- Every cited cell and byte run is present, with one exception: blt 6e
  cites `devide_value/5 @ad`, but `6e 03 00 00` is at **@ab**.
- Every `file:line` citation matches.
- Five quotes are paraphrases of the held lines: d1 PCAATTR.ESP:217-218;
  60 KFILMP.ESP:871-873; e2 PCMTAPMNG.ESP:233-261; e6
  ITRCHK.ESP:2656-2660; pmi 49 RDOTERM.ESP:1025-1026.
- `witness.py --check` passes (40 witnesses). The measured dd/de claims
  re-run and hold.

**Rows whose witness does not settle the operands.** The mechanical
rule: equal or all-zero operand fields, or a source that does not fix
which operand is which, with no second witness. Where a settling witness
was found, it is in the TSV.

| Rows | What is unsettled |
|---|---|
| e4, c5 | offset 0 |
| c4, c5 | the first byte is not always the arity: c4 = arity in 5,209 of 7,993, arity+1 otherwise; c5 = arity+1 in 204 of 1,713. It reads as the count of saved registers, as TR-236's `try_me_else L,N` |
| c9, c7, cc | R always 0. TM-444 p10: only the first argument is indexed, so compiled code cannot settle R |
| blt e6 | R and offset 0 |
| blt f0 | offset 0 |
| 25, a6 | A = Y (disclosed) |
| 2a | A = 0 |
| 2b | A = T |
| 42, 46 | Y = 0 |
| a0 | A = Y |
| blt 27 | Name = R |
| blt 19 | V = N = 0 |
| dd, de | A = n |
| blt 10 | X = 0 |
| blt 40, 41, 48 | R = A only (disclosed). Held code has R != A 2,028, 924 and 461 times |
| 73, 74, 75 | R = n-1 in all 51,425 held uses, so R is never independent of n |

**Rows with an OURS, UNKNOWN or INFERENCE clause in their meaning:** 60,
c4, 42, 43, a4, a5, de, d3, 24, blt 64, 0b, 1c ("OURS: not witnessed"),
68, 33, 32, 06, 6e, cd00.

**UPGRADED (13).** In each, the row's own witness is the situation the
printed source describes.

- **42/44 and 43/45: the names look swapped**, by TM-444 p31 ex. 8:
  - 42 = `unify_value_p`, 44 = `unify_local_value_p`;
  - 43 = `unify_value_t`, 45 = `unify_local_value_t`.
  - The clause-scoped counts agree: a 44's Y is never made by 40/46, and
    is made by a0 in 3,690 of 6,805; a 45's X is an unwritten head
    argument or its copy in 6,451 of 6,639.
- **a4 = `put_local_value`** (TM-444 p31).
- **a5 = `put_unsafe_value`** (p30).
- **pmi 24 = `get_builtin_variable`** (TR-236 Fig. 1).
- **2b = `get_var_var_list`** (TM-444 p16).
- **blt 45/46/48/49 = `add_constant`/`subtract_constant`/`multiply_constant`/`divide_constant`**
  (`cil_kl0.esp`:82, 264, 173, 117). Row 49 gains R != A witnesses:
  c_grade_ex.esp:26 @40 `49 00 0a 07`, and p_icon.esp:210-211.
- **blt 06:** TR-044 A.2 `stack_vector(?Vector, ^Length)`, an arbitrary
  argument, so a test that fails. That a heap vector fails stays
  INFERENCE.

**Rows CONFIRMED with a wording change:** blt 0b and 1c. Their third
operand is the element Size (`string(?String, ^Length, ^Size)`,
`new_string(~String, Length, Size)`, TR-044 A.2-A.3 PDF p39), not a
"type" (§5, P-k7).

**NO SOURCE FOUND (12)** are listed in the TSV. No source was found, in
TM-444, TR-236, TR-044, `cil_kl0.esp` or the ESP manuals, for:

- the initial element values of `new_string` and `new_heap_vector`;
- the rounding of division;
- whether substring and string_tail share storage;
- the bounds of search_character;
- the third argument of list_to_vector and vector_to_list;
- the split of the e/c try family.

TR-044 refers to "[Chikayama 84]" for the details; it is not held.

**The opcodes still without a row (11).** Readings are from held code
whose source is held, the "would-be witnesses".

| Opcode | Held uses | Reading | Witness |
|---|---|---|---|
| pmi b1 | 342 | `put_vector_1` | HLCAPRSUB.ESP:426-427, make_nest_vector/3 @2ae |
| pmi b5 | 144 | `put_vector_5` | receiver.esp:680-681 @b76 (A = 0 only) |
| pmi b6 | 174 | `put_vector_6` | p_MAIN.esp:444 @3be (A = 0 only) |
| pmi b7 | 67 | `put_vector_n A,_,n` | p_icon.esp:224-228 @6e `b7 00 00 07` |
| pmi ca | 1,025 | jump unless A_R is the next cell's constant (INFERENCE for unbound; R always 0) | FMT_CONV.ESP:20-25 @29; HLCAPRSUB.ESP:425-427 @2a4. No printed source |
| pmi c6 | 169 | long-form switch_on_constant? (measured only) | none with source |
| blt 9a | 14 | `inhibit_interrupt`; blt 9b `allow_interrupt` | TERMCODE.ESP:181-193; `cil_kl0.esp`:149, :85 |
| blt 54 | 418 | `shift_left(X,N,^R)`; also 51 `or`, 55 `shift_right` | BCKBCK.ESP:121-125 @70; KP_TIMER.ESP:43-45; TR-044 A.6 |
| blt f2 | 3,067 | `==`, else = cell+2+u8, as blt f0 (difference UNKNOWN) | CTS.esp:50-52 @48b |
| blt 6f | 75 | `list_to_vector(L,^V,^Tail)` | BCMSETSEQ.ESP:346-348 @4c3 |
| blt 49, R != A | 175 of 585 | as row 49 | above |

Also met without a row: pmi c1, ce, ff, a8; blt 05, 0c, 12, 14, 42, 43,
50, 51, 55, 6b, 72, 73, 92, 9b. Readings that fit the listings, not yet
witnessed: 12 `value`, 72/73 `word`/`set_word`, 92 `system_clock`, 6b
`hash`, 14 `atomic`, 0c `list`.

## §3 The PIMOS shutdown output

The output is checked against the manual, `Eman/e-sysman.tex`:121-144.
The corrections are applied in `binary_reverse_engineering.md` §1.4,
"Against the manual".

| # | Claim (where) | Primary source checked | Verdict |
|---|---|---|---|
| 3.1 | Which PIMOS the manual describes | `Eman/e-v30.tex`:4 and `e-cover1.tex`:5 "(V 3.0)"; the boot log `e-sysman.tex`:106 `V 3.000`; the files dated 17 Mar 1993. Held source: `kernel/init/version.kl1`:15-21, `"3.600"`, `"20-May-93"`; the files dated 1994 | CONFIRMED (a held fact): the manual is V3.0, the source and object are V3.6. No V3.0 source is held |
| 3.2 | The Japanese manual of the same version | `ifs/manuals/pimos/man30.j.ps.Z` prints the same console transcript, `login Server End` and `000954C2` included (positioned fragments read in order) | CONFIRMED: the manual's lines are not a slip of the English translation |
| 3.3 | Prompt `Really(yes/no) ?` (manual) against the source's `Really(yes/no)?` (third branch, `server/user/shutdown_b.kl1`:51) and `Really(yes/no)? ` (:23, :36) | The manual's own source is `\keyin{Really(yes/no) ?}{yes}`. `man15.ps` (V1.5) and `man30.j.ps` typeset the same space. The primers print the source's form, `Really(yes/no)? yes`: `primer25.tex`:460 (PIMOS 3.0 Introductory Manual) and `primer15.j.tex`:524 | **CONTRADICTED** (the manual's spacing, by the primers and the source). The model writes the held source's string: CONFIRMED |
| 3.4 | `Shutdown started` | `kernel/init/init.kl1`:313 | CONFIRMED |
| 3.5 | `login Server End` (manual) against our `User Server End` | Ours is the held source's (`server/login/init/usersvman.kl1`:195, outside any machine switch) and the held object's (`pimm_server360E.sav`, the only `Server End` in `pimosobj`). `login Server End` is in no held archive: `pimos`, `pimosobj`, `psdpim`, `vpim`, `pdss` and `klic` were searched as bytes. Context: the user server runs a job named "Login Server" (`server/user/user_sv.kl1`:29-31) | Ours CONFIRMED against the held source. That the string changed between 3.0 and 3.6: NO SOURCE FOUND, stays INFERENCE (now with the context above) |
| 3.6 | `Statistics in PIMOS:` then two integers | `bios/boot/bios.kl1`:144-147 | CONFIRMED |
| 3.7 | The count: the manual's 0/000954C2h against our 0/790,104 | `e-task.tex`:84 `statistics(High_resoc, Low_resoc)`; `e-shoen.tex`:42 counts 2 per reduction ("1 for goal creation and 1 for termination"); `ref/pimm/pimm.py` `i_shoen_statistics` reports twice the shoen's reductions (it cites `e-shoen.tex`:234). 611,522 = 2 x 305,761; 790,104 = 2 x 395,052 | **UPGRADED**: the unit and the H/L order are sourced, and our count is twice the reductions as the manual defines. The values are counts of different runs, versions and machines, so not comparable. "The model's own count (not traced further)" is withdrawn |
| 3.8 | `PIMOS END********` | `bios.kl1`:167 | CONFIRMED |
| 3.9 | The prefix and the `(  INTo) 00 ...` form "are the console's display" (unsourced) | HELD: the PSI's CSP package `pimmcsp.ptf`, class `csp_halt_messages` (`ptfread.py pimmcsp --strings`): `'DC> '` (`display_console_word/3`), and the format `'(\6s) \s \s'` (`display_console_word/2`: the tag right-aligned in six, then two words). The tag names `"INTo" \| "INTx" \| ...` are in `csp_help_command`. `PE00(00) @ ` is not a literal there | **UPGRADED** (DC> and the integer form); the PE prefix not traced |

## §4 FEP protocol claims marked OURS or INFERENCE in `fep_services.md`

The PIMOS side was checked against `pimos/src` (3.6), the PSI side
against `pimfep.ptf`. Line numbers are of `fep_services.md` after this
check's edit.

| # | Claim (line) | Primary source checked | Verdict |
|---|---|---|---|
| 4.1 | `getb` counted in characters: `fep.py` `getb_unit=2`, OURS "from the run" (`binary_reverse_engineering.md` §1.4; `fep.py` header) | Held PSI side: `pimfep##pimos_file` local `getb/4`. At @259-25a, `a7 00 00 10` then `1c 00 03 00`: `new_string(A0, A3, 16)`, with blt 1c's operand order from its witness `1c 03 01 03`. At @25e it sends `:getb/3` to the SIMPOS file object; at @263 it replies `substring(S, 0, N)`. The instance `getb/4` (@e7-fc) passes its third argument as local A3. That this argument is the wire's Size follows from §6.1's rule (method arity = PIMOS arguments + 3; DevID, command, Size, receiver), its one INFERENCE. PIMOS's commented-out `send_message_getb/7` (`server/fep/file/file_dvcb.kl1`:370-385) sends Size unchanged to a JIS FEP (code 0) and `Size*2` to an EUC FEP | **UPGRADED**: OURS to READ (held object), with the §6.1 inference. Corrected in §2.2 and in the two §1.4 rows. The `fep.py` comment is code: §5 P-f1 |
| 4.2 | 601 makes an object of the class named: INFERENCE (:194) | the same paragraph already says §6.4 read the code and confirms it | CONFIRMED (already superseded in place) |
| 4.3 | 60 on the timer after 304: INFERENCE from `time_sv.kl1`:55 (:309) | `server/fep/fep/time_sv.kl1`:54-56: `TS=[get_date_time(Args)]`, a closed one-element list, so the stream ends after the one request; `fep.py` and the run show the close | CONFIRMED |
| 4.4 | §4 table, "OURS, until the PSI side runs" (:393-420) | by design: these are the stand-in's choices | NO SOURCE FOUND (no PSI-side run is held) |
| 4.5 | U1: the version V and the Host of the 240 answer, OURS (:474, :679) | searched: SIMPOS `version` and `network_node_name` are in no held package (ptf class lists), the corpus and the IFS sources. TM-181 PDF p4's screenshot reads "SIMPOS version 2.19" (an old version, not the PSI that ran pimfep `V0.45`) | NO SOURCE FOUND |
| 4.6 | U5: "903 is dropped" rests on the clause chain `c2`/`d3`, "unwitnessed" (:478, :788) | `psi/kl0_opcodes.tsv` now has rows for both, but c2's witness (kappa `$or$0/1` @812, `c2 00 ff fe`) has no held source clause and targets itself, and d3's (fts `post_cts/2` @27) is a cut; the opcode check found no source for the c-series (NO SOURCE FOUND rows). The try family's meaning is in TM-444 PDF p9-10, by mnemonic only | NO SOURCE FOUND: no witness shows the fall-through; stays INFERENCE (`fep_services.md` reworded to say so) |
| 4.7 | U9: the login task inherits the "login" task's window, INFERENCE (:482) | the request handler was not traced in this check | NO SOURCE FOUND (not re-traced) |
| 4.8 | `refute/3` calls the named method with the vector's elements in order, INFERENCE (:562) | `refute/3` is in no held package; the arities fit all 63 rows (re-run of `fepfacts.py handlers` not repeated). §4.1 adds one more fit (getb's Size lands in A3) | NO SOURCE FOUND (support only) |
| 4.9 | U3: what `remote_or_local/6` returns (the user's home directory, by the names), INFERENCE (:711) | `e-login.tex`:125, :177 (`task:home`, "Home Directory Name String"; `pimos.init` under the home) and `login_p.kl1`:93 (`setenv(task:home,Dir,_)`) say what PIMOS does with it; the SIMPOS method is not held (the held port of `pathname` lacks it, sweep §2.1), and its held callers (cil `ms_ist.esp`:251, 1668) were not read for its result | NO SOURCE FOUND |
| 4.10 | U2: the H and L arithmetic, "unwitnessed built-in opcodes" (:767) | `pimfep##as_pimos_login_requester` uses blt 40, 42 and 48. 40 and 48 have rows; blt 42 has none (§2, "met without a row") | NO SOURCE FOUND (blt 42 still unwitnessed) |
| 4.11 | abort: a failed test goes on to the next clause, INFERENCE (:788) | as 4.6 | NO SOURCE FOUND (as 4.6) |
| 4.12 | what `tag_catch/9` and `abort/3` do, INFERENCE from names (:818) | the SIMPOS `process` class is lost. TM-100 prints no `tag_catch`; it was searched in the corpus, IPSJ and IFS sources | NO SOURCE FOUND |
| 4.13 | the login password, OURS (:893) | `pimosobj/object/pimos.logins` (held) gives the users; the SIMPOS password is the PSI's | CONFIRMED as OURS (no source can give it) |
| 4.14 | "60: one reply; no 903 (§6.6, with its one INFERENCE)" (:896) | as 4.6 | NO SOURCE FOUND (as 4.6) |
| 4.15 | `pimos.syslog` made by the append, OURS (:1007) | `bios/boot/syslog.kl1`:33 opens it for append; `object/INSTALL` does not ship it | CONFIRMED |
| 4.16 | a `shell.com` or `pimos.com` in the home would be OURS (:1012) | `object/INSTALL`:8 puts the objects in `PIMOS.DIR`, not in the home | CONFIRMED |
| 4.17 | how the firmware held LUN 1 open: INFERENCE (:1101) | not in the held source (bios SCSI), the manuals or the corpus (`disconnect`, `reselect`) | NO SOURCE FOUND |
| 4.18 | the idle test, OURS (:1133) | by design | NO SOURCE FOUND |
| 4.19 | login record ID = 1, OURS (:1146) | §6.5: the real requester's ID is "the smallest integer from 0 not in use" (pimfep `pimos_remote_login_socket_table get_key/4`); the first login is 0 | **CONTRADICTED**: the held PSI gives the first login ID 0; the stand-in sends 1. Proposal P-f3 (§5) |
| 4.20 | RN `"pmpsi"` is the SIMPOS user, INFERENCE; RP `""` OURS (:1149-1150) | `pimosobj/object/login.com` `"me" := ["user:pmpsi"]` (held); `primer25.tex` gives the pseudo-Multi-PSI setup with logical directories under `>sys>csp`, but no user | CONFIRMED for the name; the user role NO SOURCE FOUND (counted as CONFIRMED) |

## §5 Proposed changes to `pim/psi/`

Applied on 2026-11-25, each after its own re-check: the status of every
item is in "Status" at the end of this section.

These are listed by file. Each gives the location, the change, and the
citation. P-numbers are for reference.

### `psi/standin/`

- **P-s1. `semaphore.esp`, header lines 2-3.** Replace "no part of
  `semaphore` is printed" with: "no body of TM-100's class `semaphore`
  is printed; TR-056 PDF p13 (folio 11) prints `:p`/`:v`/`:init` bodies
  of a semaphore built on a stream (an earlier design: other selectors,
  no waiting_queue nature), cited, not transcribed."
  - At the `nature waiting_queue` label (line 20): `% READ: TM-100 PDF
    p16 (folio 14) prose and Fig. 3.9 (PDF p17).`
  - At `:create/3`: add "TR-056 PDF p13: an integer semaphore holds 'the
    specified number of tokens', `:init(Semaphore,Count)`".
- **P-s2. `list_index.esp`, header line 14.** It becomes: "one slot
  `first`, holding '$$void' or an entry with Next at 0, Object at 1, Key
  at 2 (KPPOOL.ESP:35-43). OURS: the entry is written as a stack vector
  `{Next, Object, Key}`; on the PSI a stack vector, compound term or
  list cannot be saved in a slot (TM-388 PDF p138, folio 126), so
  SIMPOS's entry was a heap vector or an object (TM-161 PDF p18:
  `index_entry`, `list_entry`, `with_link:get_next/2`)."
  - Line 30: "keys are matched by unification (OURS); SIMPOS used a
    local `equal_key/2` (TM-161 PDF p18); kl0's unification compares
    strings by content, which the PSI's does not (TM-388 PDF p79, folio
    67)."
  - At `add_at`: "TM-161 PDF p14 prints `:add_at(Hash,Key,Object)`, key
    first, against TR-056 PDF p8, `program-e.tex`:6523/6529 and every
    held caller; not followed."
- **P-s3. `hash_index.esp`.**
  - Header: add "TR-056 PDF p9: a hash array of lists with 'a standard
    hash function'; TM-161 PDF p13: data other than stack vectors only
    (the stand-in accepts any term: OURS); `hash/2` can be negative
    (SVHSH_IDX.ESP:83-89 masks with 16#7FFFFFFF)".
  - `get_at/3` label: `% READ: TM-161 PDF p14: returns the object under
    the key, fails on a miss (argument order TR-056 PDF p8,
    program-e.tex:6529). INTERPOLATED: the body.`
  - `create/3`: cite `program-e.tex`:6517 `:create(#hash_index,HT,256)`.
  - Optional: a `put_at/3` (`program-e.tex`:6523; SVHSH_IDX.ESP:28).
- **P-s4. `list.esp`.**
  - `add_first/2` label (line 34): `% READ: TM-161 PDF p12: adds the 2nd
    argument at the head of the list. INTERPOLATED: the body.`
  - Citations only:
    - get_first/2 and count/2: TM-100 Fig. 3.8, PDF p16;
    - clear/1: TM-100 Fig. 3.4, PDF p13;
    - remove/2: the printed comment, TM-100 PDF p9;
    - add/2: TR-056 PDF p6, `as_pool :add(Pool,Object)`.
- **P-s5. `symbolizer.esp`.**
  - `string_to_list/3` label: add "OURS: SIMPOS's string_to_list/3
    could not be called with List already bound (TM-115 PDF p98, folio
    93); the stand-in can."
  - `get_number/3`: `% READ: interface and the result for "123"
    (ESPtex program-e.tex:6748-6756). INTERPOLATED: the body.
    INFERENCE: failure on a non-number.`
  - `get_number_string/3`: `% READ: program-e.tex:6757-6758.
    INTERPOLATED: the body.`
  - Header: cite `program-e.tex`:6748-6762 and TM-115 PDF p98, and note
    that `get_number_string/4` (radix) exists and is not stood in.
- **P-s6. `stream.esp`, header lines 18-21.** Replace "has no stand-in
  yet" with: "is stood in elsewhere: waiting_queue and post_queue
  (INTERPOLATED, waiting_queue.esp, post_queue.esp) and process's
  self/2, inhibit_interrupt/1, allow_interrupt/1, resume/2, suspend/2
  (process.esp)."
- **P-s7. `pathname.esp`, header line 31.** `remove_or_local/6` becomes
  `remote_or_local/6` (cil ms_ist.esp:251).
- **P-s8. `pmacs_window.esp`, header lines 8-11.**
  - Cite create/4 from kwic-esp `src/inEditor1.esp`:151 and mendels
    `comp_win.esp`:54-62 (Opts with `nature([with_superior_input_buffer])`
    and `superior(..)`, third argument `_`).
  - Cite create/3 then `:get_editor` from disc/exshow.esp:24, :28.
  - The label on create/4 changes the same way.
  - Optional: IPSJ 114007 p410 Fig. 3 for the editor as a separate
    object.
- **P-s9. `standard_editor.esp`, header lines 14-19.** It becomes: "In
  SIMPOS the window and its editor are made together (held: exshow.esp:24
  create/3, then :get_editor at :28). The pmacs_window stand-in makes one
  together with its editor and sets this slot; an editor made any other
  way keeps 0, and kl0 refuses the next send to that window." Also apply
  P-s8's citation fix.
- **P-s10. `with_link.esp`, header.** Replace "what it holds is not
  printed" with: "TM-161 PDF p18 prints the profile row `with_link /
  get_next / imp / 2` (get_next/2, body not printed); TM-100 PDF p10:
  one of 'two classes for chaining process instances' into the ready
  queue. The stand-in stays empty." Add no body.
- **P-s11. `waiting_frame.esp`.** Add "the waiting_queue is a
  doubly-linked list of these frames (TM-100 PDF p14, folio 12)".
- **P-s12. `as_class_with_lock.esp`, `:lock/1` label (line 27).**
  - It becomes "HELD-SOURCE statement of the behaviour: LOADER.ESP:144-146
    (M. Ozawa, 1991-12-17), :unlock is :lock's alternative; :149-153 the
    unlock-on-failure clause commented out as not needed. The code is
    INTERPOLATED."
  - Header: note that the class-level `locked/2` (Class, ^Process) is
    sent by kappa2 MOPMANAGER.ESP:55 and is not stood in.
- **P-s13. `with_lock.esp`, header.**
  - Add the held instance-level user: kwic-esp `src/functions.esp`:763-836,
    class fncRightOf, natures `as_resource, with_lock`. It sends
    :lock/1 at :825, :832, :836, :unlock/1 at :796, :locked/1 at :802,
    and :locked/2 at :821 (not stood in).
  - Its waiting-message window around :lock (:827-836) shows that the
    real :lock blocks (TR-524 PDF p4, "lock and unlock primitives"), as
    the disclosed no-wait model says.
  - Add TR-056 PDF p26 (folio 24): "each object has a stream for a lock".
- **P-s14. `message.esp`, `as_message.esp`.**
  - message's `nature as_message` label: `% PRINTED (prose): TR-056 PDF
    p14, folio 12`.
  - The `body` slot: `% PRINTED (prose) TR-056 PDF p14; the slot NAME
    body is OURS`.
  - as_message's `sender, receiver`: `% PRINTED (prose): TR-056 PDF p14,
    folio 12`.
- **P-s15. `time.esp`.**
  - Header lines 13-14 and the label at line 24: "The count is in
    MILLISECONDS: HELD-SOURCE gog-kl1 ESP/CH_CLOCK.ESP:60
    `:set_count(Obj!time,MS+1000), % 1000 msec interval`; PIMOS converts
    to msec before fep#on_after (server/fep/timer/time_dvc.kl1:197-209)."
  - Header: get_count/2 and set_count/2 are also sent by held IFS source
    (CH_CLOCK.ESP:59-60).
- **P-s16. `trace.esp`, header.** Replace "a second arity, UNSPECIFIED"
  with: "trace/2 takes a process number (cal-esp deb2.12/util.esp:217-227,
  'Multi_process_debugger': `:trace(#trace)`, `:trace(#trace,Process_no)`);
  notrace/1,2 exist and are not stood in. TR-087 PDF p11 §5.4: the
  system tracer is a separate ESP process."
- **P-s17. `network_listener_buffer.esp`.** Keep UNKNOWN. Add the
  INFERENCE note of §1, "Found in passing" (length in elements and width
  in bits; SRVCMD.ESP:22 2048 x 16 = MSGCMD.ESP:22's 4096 bytes).
- **P-s18. `post_queue.esp`, `waiting_queue.esp`.**
  - Representation labels: add "a list cannot be saved in a slot on the
    PSI (TM-388 PDF p138): OURS".
  - waiting_queue `unhook/2`: "fails when empty" is OURS (the printed
    put/2 calls unhook only after `:empty` fails).
- **P-s19. `string.esp`.**
  - `append/3`: cite held SIMPOS source `_simpos/pathname.esp`:80, 86
    and `name.esp`:110, 139, 257.
  - `copy/3`: cite `e_string.esp`:67-70 (a fresh, separately mutable
    string).
- **P-s20. `process.esp` `create/3` label.** It becomes: "INFERENCE: four
  area-limit check settings (the same atoms open set_area_limit_execution/6,
  commented 'area limit check free': gog CGS_MAIN.ESP:70, FEP.ESP:21;
  TR-079 PDF p9's four stacks)".

### `psi/kl0_opcodes.tsv`

- **P-k0. Row blt 6e, witness.** `devide_value/5 @ad` becomes `@ab`.
- **P-k1. Rows 42, 43, 44, 45: mnemonics and meanings.** The page is
  verified by the lead (TM-444 PDF p31, printed 30, ex. 8, read as an
  image: `unify_local_value_t A0` on a head argument, `unify_value_p
  Y0` on a Y from `get_variable_p`, `unify local_value_p Y1` on a Y
  from `put_variable_p`); the binding to the numbers rests on the
  agent's clause-scoped counts, not re-run by the lead.
  - 42 `unify_value_p`, 44 `unify_local_value_p`;
  - 43 `unify_value_t`, 45 `unify_local_value_t`;
  - TM-444 PDF p31 ex. 8, with the clause-scoped counts of §2.
  - Separately, for `psi/kl0.py`: a string-unification audit (TM-388 PDF
    p79).
- **P-k2. Rows a4, a5, 24, 2b.**
  - a4 `put_local_value` (TM-444 p31);
  - a5 `put_unsafe_value` (p30);
  - pmi 24 `get_builtin_variable` (TR-236 PDF p5);
  - 2b `get_var_var_list` (TM-444 p16).
  - Each replaces the "UNKNOWN" text.
- **P-k3. Rows blt 45, 46, 48, 49: names.** `add_constant`,
  `subtract_constant`, `multiply_constant`, `divide_constant`
  (`cil_kl0.esp`:82, 264, 173, 117).
  - Row 49: drop "seen only with R = A"; add c_grade_ex.esp:26 @40
    `49 00 0a 07` and p_icon.esp:210-211.
- **P-k4. Row blt 19, operands.** Replace "seen only with V = N" with
  FMT_CONV.ESP:15, sv_to_hv/2 @1b `19 02 04`.
- **P-k5. Rows c4 and c5, operands.**
  - "arity" becomes "n saved argument registers: arity, or arity+1 when
    the A_arity barrier is live" (counts in §2; TR-236 `try_me_else
    L,N`).
  - Add a sourced c5 witness with a non-zero offset.
- **P-k6. Second, settling witnesses.**
  - e6: receiver.esp:1270-1272, $or$54/2 @1e4b;
  - f0: BCMSETSEQ.ESP:344-352 @4c2;
  - 2a: CTS.esp:50-52 @48e;
  - 2b: receiver.esp:1297 @1183 `2b 01 02 03`;
  - a0: KP_TIMER.ESP:41-43 @24;
  - blt 27: KP_TIMER.ESP:38 @20 `27 01 00 02`;
  - dd: c_grade_ex.esp:20-21 @2f `dd 02 09`;
  - e4: HLCAPRSUB.ESP:425-427, make_nest_vector/3 @2a6.
- **P-k7. Rows blt 0b and 1c.**
  - The third operand is the element Size (TR-044 A.2-A.3 PDF p39,
    `string(?String, ^Length, ^Size)`, `new_string(~String, Length,
    Size)`), not "type". The value 8 occurs (TERMCODE.ESP:183).
  - new_string's S is an output argument.
- **P-k8. Rows c9, c7, cc, table cd00, d5, d2, dc.** Cite the TM-444
  mnemonics as INFERENCE bindings: `jump_on_non_list`,
  `jump_on_non_constant`, `jump_on_value`, `hash_on_value`,
  `cut_me_and_fail`, `cut_me_and_proceed` (TR-236), `cut_me`. Note that
  R is unsettled for c9, c7 and cc.
- **P-k9. Rows d1, 60, e2, e6, pmi 49: paraphrased quotes.** Replace them
  with the verbatim lines (files and lines in §2).
- **P-k10. New rows.**
  - b1, b5, b6, b7, ca;
  - c6 as UNKNOWN;
  - blt 9a and 9b;
  - blt 54 (and 51, 55);
  - blt f2, blt 6f;
  - each with the witness in §2's table.
  - Each needs `witness.py` entries and the kl0 tests in the same change.

**Which proposals the lead verified.** P-s7, P-s8, P-s9, P-s15 (the
CH_CLOCK.ESP line), P-s14 (the TR-056 sentence), P-s10 (the TM-161
line), P-s2 (the TM-388 sentence) and P-k1's page were checked by the
lead against the held file or the OCR text; P-f1 to P-f3 are the
lead's own. The rest are agent-reported, with the citation in the row
tables; re-check each line before applying.

### Code and docstrings

These are outside `psi/` in part. Changing them requires the full suite.

- **P-f1. `ref/pimm/fep.py`, header comment.** "the unit of getb's count
  ... longrun_ipl.py gives the kernel 2, the count in characters
  (2026-11-24, from that run)" becomes: "... 2: the count in 16-bit
  characters, READ from pimfep##pimos_file getb/4 (new_string(S, Size,
  16), docs/fep_services.md §2.2); the default 1 is kept for the IPL,
  which works either way."
- **P-f2. `asm/ptfdump.py`:33 and `psi/fepread/README.md`:23.** "Opcode
  NAMES are not known" becomes: "Opcode NUMBERS are not printed in any
  held document; the MNEMONICS are (TM-444 PDF p6-16, 30-31; TR-236 PDF
  p5), so a number is tied to a mnemonic only by a witness."

- **P-f3. `ref/pimm/fep.py`, the login record's ID.** It sends 1; the
  held PSI sends the smallest integer from 0 not in use as a key of the
  replier's socket table (`pimfep##pimos_remote_login_socket_table
  get_key/4`, `fep_services.md` §6.5), so 0 for the first login. Change
  it to 0, or keep 1 and label it a known deviation. Either way the
  tapes and pins that carry it move: the full suite is needed.

### Status (2026-11-25)

Each item was re-checked against its primary source before it was
applied: the page image for a TR/TM citation, the held file and line
for a source citation, the held cells for a witness. APPLIED means
applied as proposed unless the note says otherwise.

| Item | Status | Note |
|---|---|---|
| P-s1 | APPLIED | TR-056 p11 is PDF p13 (image read) |
| P-s2 | APPLIED | TM-388 PDF p79 and TM-161 PDF p18 read as images |
| P-s3 | APPLIED, except `put_at/3` | `put_at/3` NOT APPLIED: optional, and new behaviour, not a label |
| P-s4 | APPLIED | |
| P-s5 | APPLIED | |
| P-s6 | APPLIED | |
| P-s7 | APPLIED with other citations | the audit's cil `ms_ist.esp`:251/1668/1793 and `ds_fep.esp`:912 do not hold `remote_or_local`; cited instead: cal-esp `deb2.12/init.esp`:314, cil `src/ds_fep.esp`:909 (and `ds_bep.esp`:2026) |
| P-s8 | APPLIED, except the IPSJ citation | the optional IPSJ 114007 citation NOT APPLIED: not re-read |
| P-s9 | ALREADY DONE | step 3e (1695727f) |
| P-s10 | APPLIED | |
| P-s11 | APPLIED | |
| P-s12 | APPLIED | |
| P-s13 | APPLIED | |
| P-s14 | APPLIED | |
| P-s15 | APPLIED | time_dvc.kl1 lines are 199-210, not 197-209 |
| P-s16 | APPLIED | |
| P-s17 | APPLIED, corrected | TM-388 PDF p29 lists four element widths (1, 8, 16, 32), not "16 or 32" |
| P-s18 | APPLIED | |
| P-s19 | APPLIED | |
| P-s20 | APPLIED | |
| P-k0 | APPLIED | `@ab` read from the cells |
| P-k1 | APPLIED | counts re-run independently (clause-scoped def-use): 44's Y never from 40/46 (0 of 6,805); 45's X a head argument in 6,451 of 6,639 |
| P-k2 | APPLIED | pmi 24: 5,331 of 5,773 follow a built-in cell |
| P-k3 | APPLIED | handlers renamed; the census refusal text follows the name |
| P-k4 | APPLIED, and executed | kl0 no longer refuses blt 19 V != N; census moves in `psi/README.md` |
| P-k5 | APPLIED, reworded | the rule "arity+1 when the barrier is live" is not exact: of 2,784 arity+1 c4, 2,241 are in predicates keeping a barrier in A_arity and 543 are not; the row gives the counts. c5 witness: h_grade_n.esp:507-512 @368 |
| P-k6 | APPLIED | every cell and source line re-read |
| P-k7 | APPLIED | TR-044 PDF p39 read as an image; TERMCODE.ESP:183's size 8 is a `string/3` call |
| P-k8 | APPLIED | TM-444 PDF p12-14 and TR-236 PDF p5 read as images; cited in the meaning, mnemonics not renamed |
| P-k9 | APPLIED | all five quotes re-read verbatim |
| P-k10 | ALREADY DONE except c6 and blt 6f | b1/b5/b6/b7, ca, 9a/9b, 50/51/54/55, f2 by step 3e; c6 and 6f NOT APPLIED: each needs an implementation and tests, and 6f's third argument is unsettled. c6 APPLIED in step 3g (2026-11-25, with ce, c3, c1, ff, cd03, cd04; §7 and `../../psi/README.md`) |
| P-f1 | NOT APPLIED | `ref/pimm/` is another agent's directory; outside this change |
| P-f2 | APPLIED | also `psi/fepread/ptfread.py`'s docstring, which said the same |
| P-f3 | NOT APPLIED | `ref/pimm/` is another agent's directory; outside this change |
| P-k1 string audit | APPLIED | TM-388 PDF p79, p117-119, p169 and TM-115 PDF p97 read as images: strings unify only by storage. kl0 follows (unify, `==`); string/3 a type test (TR-044 PDF p39); list_index `equal_key/2` compares string keys by contents. Census effect in `psi/README.md` |
| §6 `classes.tsv` | APPLIED (generator) | `asm/simpos_census/espscan.py` `INSTANCE_RESULT`: `time` `now/2` returns an instance (CH_CLOCK.ESP:33-34, 59-60); the scan rerun, every table regenerated; only `time`'s sends move |

## §6 Open after this check

- No V3.0 PIMOS source is held, so `login Server End` stays INFERENCE
  (3.5).
- The `PE00(00) @ ` part of the CSP prefix is not traced in `pimmcsp`
  (3.9).
- The PSI's hash function (blt 6b) has no primary statement anywhere in
  the corpus.
- The opcodes still without a row, and the unrowed blt 42 that U2's
  arithmetic uses (4.10).
- Not given rows: the unlabelled local helpers of INTERPOLATED files
  (about 20 in `hash_index`, `list`, `list_index`), which inherit their
  file's label.
- ~~`required/classes.tsv`'s `time` row lacks get_count/2 and
  set_count/2~~: fixed 2026-11-25 in the generator (Status, §5).
- The primer cited as `primer25.tex` is titled "PIMOS 3.0 Introductory
  Manual" (its `\title`), but points readers to the "PIMOS 2.5 Manual".
- The OCR corpus covers about half the held TR/TM pages. It covers all
  of the SIMPOS-related pages but TM-305.

## §7 Step 3f's INTERPOLATED and OURS parts, re-checked (2026-11-25)

Step 3f (`../../psi/README.md`, the "Step 3f" sections) added kl0's
library and symbolizer models, 17 `pmacs_window` methods and the
census recipes. Each was labelled INTERPOLATED or OURS from cited
pages and lines. Step 3g re-read the citations in the table below
(the rest are listed after it as not re-read):

- TR/TM pages as page images (`pdftoppm`, read by eye). TM-115 was also
  OCRed whole with tesseract, as a lead only.
- Source lines in the held archives.
- Compiled cells in the `ptfread` listings.

Page numbers are PDF pages, with the printed folio where it differs.

| Item (step 3f) | Cited basis | Re-read | Verdict |
|---|---|---|---|
| `library:assign/1` succeeds, binds nothing (INTERPOLATED) | kappa2 `HLCLIB.ESP`:29, `LOADCH.ESP`:64, `LOADER.ESP`:251 | each is the first library send of its clause (`:assign(#library)` before `get_package`/`make_package`, before the hash-index creation, before `check_info`) | CONFIRMED as call sites; what it binds is still NO SOURCE FOUND |
| `library:check_info/3`: "both try `template_file` (then `make_class_object/2`) and `object`" | `LOADER.ESP`:252-256; pimfep `pimos_string_io_invoker` local `get_class_object/3` @5a-80 | LOADER tries `object` first, then `template_file` and `make_class_object`. The pimfep cells try `template_file` first (@60-63, `make_class_object/2` @68), then `object` (@76-79). | CORRECTED: the order differs between the two callers. The model (`object` succeeds for a loaded class, `template_file` fails) answers the same in either order, so no code changes |
| `library:get_class_object/3` (INTERPOLATED name and lookup) | `subsystems/librarian.md` §1.4; HLCLIB.ESP:30-31 | TR-283 PDF p18 (folio 16) Table 4 prints `class library :get_class_object/c2` (image read). HLCLIB.ESP:30-31 `:get_package(Process,Default_Package)` re-read | UPGRADED: the interface (a class method, two arguments) is PRINTED-INTERFACE. The lookup rule stays INTERPOLATED/INFERENCE |
| `symbolizer:enter_atom/3` | TR-283 p18 Table 4; paragraph `p_wshell.esp`:211; `create_string_io/10` @28-2d | Table 4 `:enter_atom/c2` (image). p_wshell.esp:211 `:enter_atom(#symbolizer,Var,C1)`, then `Var` as a key. Cells @28-2d: the pool `#simpos##symbolizer`, `73 02 03 enter_atom/3` | CONFIRMED. The atom's name being the string's text stays OURS |
| `pmacs_window` `set_size/3`, `set_position/3`, `set_title/2` | TM-125 p15-16 | TM-125 PDF p15 (folio 14) §5.3 prints `:set_size(Window, Width, Height)`, `:set_position(Window, X, Y)` and `:set_title(Window, String)` | CONFIRMED |
| `activate/1`, `show/1`, `deactivate/1`, `hide/1` | TM-125 p15-16 | TM-125 PDF p16 (folio 15) §5.4 prints all four | CONFIRMED |
| `get_size/3` | TM-115 p50 | PDF p50 (folio 45) names `:get_size` "provided by the window system", without arguments. PDF p64 (folio 59) prints `:get_size(Instance,^Width,^Height)` | CONFIRMED. PDF p64 is the better citation (it gives the arity) |
| `get_position/3` | TM-115 p63 | PDF p63 (folio 58) and folio 63 (PDF p68) do not print it. It is on PDF p64 (folio 59, "Page 4-26"): `:get_position(Instance,^X,^Y)` | CORRECTED: the citation is PDF p64. PDF p63 opens the parameters_display_menu section (4.14) that the methods belong to, which is likely why `subsystems/notes/tm115.md` and `tm115.tsv` cite p63. Fixed in `standin/pmacs_window.esp`, `subsystems/window.md` §2.1 and the README texts; the generated notes tables (`tm115.tsv` and the coverage outputs built from it) are left as they are (fixed in step 3h: §8) |
| `get_title/2` (USAGE only) | none printed | TM-115 PDF p64 prints `:get_title(Instance,^Title)` among the parameters_display_menu methods that "just call the method of the menu which has the same name" | UPGRADED to PRINTED-INTERFACE, for a menu window (1985) |
| `set_font/2` | TM-112 p16 | TM-112 PDF p16 (folio 12) §3.6 prints `:set_font(Window,Font)` | CONFIRMED |
| `reshape/5`, `set_text_size/3`, `get_text_size/3`, `get_font/2`, `beep/1`, `flash/1` (USAGE only) | held `.ptf` sends | the TM-115 OCR has no hit for any of them | unchanged: USAGE only |
| Model: a setter writes a slot that its getter reads back; initial values 0 and an empty title; the display methods do nothing | OURS | no source can confirm a model | unchanged: OURS |
| Recipes: "the creators' A0 is the stream the device answers on" (INFERENCE) | front end `create_device/4` @42e-447 | @42e-431 `fep_output_stream/2` into Y9; @43c `33 02` builds a 3-vector whose first element is Y9 (`44 09`), with Y10 and Y11 new; `refute/3` @446-447; `add_at/5` @448-452 | CONFIRMED for the front end's three elements |
| the same, per creator | timer `create_timer/9` @19-48 and others | pimos_file `create/9` (called from `read_open/10`, which shifts the message): A0 is the open mode, A1 the output stream, A4 the device id. tcpip `create_socket/9`: A0 to `set_output_stream/2` (@3d-40), A3 to `set_device_id/2` (@49-4c) | CONTRADICTED for pimos_file. Step 3f's recipe put the stream in the open-mode argument. Corrected in step 3g: `DEVICE_CREATORS` now gives each creator's positions |
| the front end's stream is a `simpos##stream` | `fep_scsi_output create/7` @32-3b | `pool[f] = #simpos##stream`, `create/2`, then `set_fep_output_stream/2` | CONFIRMED |
| the string-I/O class names | PIMOS `pass_body.kl1`:68 | `STR = [create(string#"pimos_standard_io_window",Win)]` | CONFIRMED |
| test claim "the timer's device id is unbound" | step 3f test | step 3g gives it REQUEST_ID (16) | SUPERSEDED (test updated in step 3g) |

Also re-read, with less depth:

- `reshape/5` USAGE cal-esp `cal2.12/cpwindow.esp`:85
  (`:reshape(Window!ctree_window, 0,0,Width,Height-NH)`): CONFIRMED.
- `create_pimos_window/3` @19-34: the pool `#pimfep##pimos_window_editor`,
  `create/4` with `{size,70,110}`, a slot write @32. CONFIRMED in shape.
- The executor's after-demon @40-48: a class-slot read (`blt 27`), then
  instance-slot writes (`blt 2f`). CONFIRMED in shape; the slot names
  were not re-derived.
- `manipulator` in place of a coordinate ("the user places the window",
  cited as TM-125 p15 in `standin/pmacs_window.esp`): NOT CONFIRMED.
  Neither TM-125 PDF p15 nor p16 prints the word. It stays USAGE
  (`subsystems/window.md`'s ptf rows) until a page is found.

Not re-read:

- TM-100 Fig. 3.1 (`process:activate/2`), which step 3e's check (§1)
  already read as an image;
- TM-388 pp92-101 (the own-package rule for `get_class_object/3`);
- `fep_services.md` §6.4 (the string-I/O programs' table);
- the rest of `create_string_io/10` beyond @28-2d.

So this re-check is PARTIAL. Step 3h re-read the four items: §8.

## §8 The rest of §7, re-checked in step 3h (2026-11-25)

This section re-reads the four items that §7 left unread. Page images
were made with `pdftoppm` and read by eye. Cells come from the
`ptfread` listings of `pimfep.ptf`. Pool constants were resolved with
kl0's `Code.pool_term`. With these, §7's four items are re-read. One
cross-reference stays unread: §6.1 step 4's `{Id, 5}`.

| Item | Re-read | Verdict |
|---|---|---|
| TM-100 Fig. 3.1 (`process:activate/2`; step 3h also uses it for `children/2`) | TM-100 PDF p7-p10 as images, against `printed/listings/tm0100_p07-p10` | CONFIRMED: the transcriptions match. No page defines `status/3`. |
| TM-388 pp92-101 (the own-package rule kl0's `lib_class_named` uses for `get_class_object/3`) | PDF p92-p101 (folios 80-89, §3.8 "Multi-Class Name Space (Package)") as images | CONFIRMED as a static rule (details below the table) |
| `fep_services.md` §6.4 (the three string-I/O programs) | `create_string_io/10` @15-55, its locals (see the next row), `as_pimos_string_io_device do_io/6` @71-89, the server's, replier's and `simpos_user_device`'s `io/4` and locals | CONFIRMED, except the `{Id, 5}` of §6.1 step 4, which was not re-read (details below the table) |
| `create_string_io/10` beyond @28-2d | @15-55, `get_class_object/3` @5a-86, `create/3` @8b-98, `initiate_string_io_device/7` @9d-bd | CONFIRMED (details below the table) |
| TM-115 `get_position/3` page (§7: CORRECTED, generated tables not fixed) | TM-115 PDF p63 and p64 as images | FIXED (details below the table) |

### TM-388 pp92-101

- PDF p94 (folio 82) prints the lookup: "(1) every class in the self
  package". Then, among the classes of the packages that the
  environment inherits, "only those classes that have been declared as
  external", with the higher inheritance order first.
- PDF p95 (folio 83) has the worked example.
- PDF p93 (folio 81) says linkage is made "when the classes are
  stored", and PDF p98 (folio 86) "statically upon macro expansion".
- No page on pp92-101 describes a run-time lookup.

So "own package first" is PRINTED, but only for names bound when a
class is stored. Applying it to the run-time `get_class_object/3`, with
the sender's package as "own", stays INFERENCE. `psi/kl0.py`'s
docstring now cites these pages; no code changes.

### `fep_services.md` §6.4

- "Name must be a 16-bit string": @1d `blt 0b 08 00 01` (`string/3` on
  A8), then @1e `pmi 27 01 00 10` (the size must be 16).
- The symbolizer and the library: @28 pool `#simpos##symbolizer` with
  `enter_atom/3`, and @2e `#simpos##library` with `assign/1`. The
  `assign/1` is not mentioned in §6.4; it is the call step 3f's
  `library:assign/1` stand-in models (§7 row 1).
- The instance and its process: an instance is made (@39 `create/3` to
  @8b `create/2`), `process/4` @22-23, `activate/2` @44-45.
- The reply: `get/2` on the creation-status stream, compared with
  `normal` (@4b-4c, blt 64). Then `{Y3, 1}` is built (@50-52: `b2`,
  `44 03`, `47 00 00 01`) and sent by `reply_message/2`, which is
  `{Id, 1}`.
- 620, `do_io/6`: by `73 R n` (the receiver is in R) the cells are
  `:io(Self, Command, To_fep, From_fep)` @79-7e and
  `:reply_message(Self, {Id, 1, From_fep})` @82-89. Around the send,
  @78 calls `allow_forced_event/0` (@bf) and @7f calls
  `inhibit_forced_event/0` (@ae).
- From_fep: @80-81 call `check_from_fep_string/1` (@e6-eb). If From_fep
  is unbound (blt e6) it becomes the pool's `string#''` (@e7).
  Otherwise `string/3` must give size 16 (@e9-ea). CONFIRMED.
- Aborts: `io/5` (@36-55) runs `do_io` under `tag_catch/9` with the tag
  `pimos_abort` and the handler `abort_string_io`. `abort_string_io/2`
  (@60-6c) replies `{Id, 6}` (`47 00 00 06`), which agrees with §6.7.
  The `{Id, 5}` for a failed `io/4` is not in these cells: it is §6.1
  step 4's dispatcher, which was not re-read here.
- `pimos_remote_login_server`:
  - `io/4` @8a holds `string#''`.
  - `server_type/2` @768 holds the strings `"local"`, `"lia"` and
    `"tcpip"` (@76a, @76f, @774).
  - `reset/2` holds the atoms `local_login`, `lia` and `tcpip` (@18e,
    @1a4, @1b5).
  - CONFIRMED.
- `pimos_remote_login_replier`: `io/4` @9c and @a7 hold `string#''`.
  `check_status/3` @176 holds `string#'<0000>'`, and @17b and @17e
  hold `string#'<0001>'`: one character, 0 or 1. CONFIRMED.
- `simpos_user_device` `io/4` @33-88 switches on the Command: 0 @3c,
  1 @58, 2 @70.
  - Each case calls `melt/4` (@8d-9d). `melt/4` checks that the
    string's size is 16 and its length is at least 2. Element 0 is
    Name's length, element 1 is Pass's, and the two substrings start
    at 2.
  - Command 0 calls `$or$2/4`: `identify/4`, else `regist/4` (@e0-e7).
    Then it sends `world/2` and calls `$or$3/2` (@ba), which sends
    `default_logical_name/2`. Its pool holds `string#'>'` (@da).
  - Commands 1 and 2 send `identify/4`, then `fullname/2` or
    `nickname/2`.
  - Before- and after-demons toggle forced events (@19, @26).
  - CONFIRMED.

### `create_string_io/10` beyond @28-2d

- The local `get_class_object/3` (@5a-86) has two clauses. The first
  tries `check_info(template_file)`, then `make_class_object/2`, then
  `get_class_object/3`. The second tries `check_info(object)`, then
  `get_class_object/3`. All five pool constants are `#simpos##library`
  (@5e, @64, @69, @74, @7a). This agrees with §7 row 2.
- `create/3` sends `create/2` to the class object.
- `initiate_string_io_device/7` (@9d-bd) sends `set_input_stream/2`,
  `set_output_stream/2`, `set_device_id/2`, `stream/2` and
  `set_creation_status_stream/2`.

Each of the three locals has a last clause that sends `exterminate/1`
(@81-85, @93-97, @b8-bc): if the steps before fail, the object is
killed.

### TM-115 `get_position/3`

- PDF p64 (folio 59, "Page 4-26", §4.14.3) prints `:get_size`,
  `:set_size`, `:set_position` and `:get_position` together.
- PDF p63 (folio 58) prints only the class's description and its
  attributes (§4.14.1-2).

The fix, made through the generators:

- `subsystems/notes/tm115.tsv` rows 37-40 and `tm115.md` lines 89-92
  now cite p64 for all four methods. `get_size` keeps p50 as well.
- `tools/coverage.py` and `tools/window_appendix_gen.py` were re-run.
- `subsystems/window.md` appendix A's three cells (`get_position/3`,
  `get_size/3`, `set_size/3`) were set to the new generated rows.

Two drifts surfaced in the re-run. Both predate step 3h:

- The committed `coverage/out/selectors.md` and `unspec.tsv` were older
  than `notes/fixpoint_fe.tsv` (f1210837, a8880b48). The re-run turns
  seven UNSPECIFIED selectors into CENSUS rows and drops them from
  `unspec.tsv`: `get_character_font/2`, `get_parsing_operator/2`,
  `get_unparsing_operator/2`, `set_max_depth/2`, `set_max_length/2`,
  `set_parsing_operator/2` and `set_unparsing_operator/2`. They are
  committed as generated.
- `window.md` appendix A is not a byte copy of `selectors.md`. After
  the re-run, 12 generated rows are not in it:
  - five that already differed before step 3h (`create/4`, `getl/2`,
    `putt/2` and two `″` rows);
  - the seven new CENSUS rows above, which are still UNSPECIFIED in
    the appendix.

  Only the three citation cells were changed. Bringing the appendix in
  line with the generator is open.
