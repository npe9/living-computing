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
lead spot-checked these citations against the sources, and they hold:

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
| §4 FEP claims marked OURS or INFERENCE | 20 | 7 | 4 | 0 | 9 |
| **Total** | **284** | **189** | **29** | **10** | **56** |

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
- **blt 0b and 1c:** the third operand is the element Size
  (`string(?String, ^Length, ^Size)`, `new_string(~String, Length,
  Size)`, TR-044 A.2-A.3 PDF p39), not a "type". This was counted with
  the row changes; see §5.

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
| 4.6 | U5: "903 is dropped" rests on the clause chain `c2`/`d3`, "unwitnessed" (:478, :788) | `psi/kl0_opcodes.tsv` now has KNOWN-PLAINTEXT rows for both: c2 `retry_me_else` (kappa `$or$0/1` @812) and d3 `cut_env_d3` (fts `post_cts/2` @27). The try family is in TM-444 PDF p9-10 | **UPGRADED**: the inference is discharged by the witnessed rows. `fep_services.md` U5 and §6.6 should drop "unwitnessed" (done) |
| 4.7 | U9: the login task inherits the "login" task's window, INFERENCE (:482) | the request handler was not traced in this check | NO SOURCE FOUND (not re-traced) |
| 4.8 | `refute/3` calls the named method with the vector's elements in order, INFERENCE (:562) | `refute/3` is in no held package; the arities fit all 63 rows (re-run of `fepfacts.py handlers` not repeated). §4.1 adds one more fit (getb's Size lands in A3) | NO SOURCE FOUND (support only) |
| 4.9 | U3: what `remote_or_local/6` returns (the user's home directory, by the names), INFERENCE (:711) | `e-login.tex`:125, :177 (`task:home`, "Home Directory Name String"; `pimos.init` under the home) and `login_p.kl1`:93 (`setenv(task:home,Dir,_)`) say what PIMOS does with it; the SIMPOS method is not held (the held port of `pathname` lacks it, sweep §2.1), and its held callers (cil `ms_ist.esp`:251, 1668) were not read for its result | NO SOURCE FOUND |
| 4.10 | U2: the H and L arithmetic, "unwitnessed built-in opcodes" (:767) | `pimfep##as_pimos_login_requester` uses blt 40, 42 and 48. 40 and 48 have rows; blt 42 has none (§2, "met without a row") | NO SOURCE FOUND (blt 42 still unwitnessed) |
| 4.11 | abort: a failed test goes on to the next clause, INFERENCE (:788) | as 4.6: c2/d3 are witnessed | **UPGRADED** (same as 4.6) |
| 4.12 | what `tag_catch/9` and `abort/3` do, INFERENCE from names (:815) | the SIMPOS `process` class is lost. TM-100 prints no `tag_catch`; it was searched in the corpus, IPSJ and IFS sources | NO SOURCE FOUND |
| 4.13 | the login password, OURS (:890) | `pimosobj/object/pimos.logins` (held) gives the users; the SIMPOS password is the PSI's | CONFIRMED as OURS (no source can give it) |
| 4.14 | "60: one reply; no 903 (§6.6, with its one INFERENCE)" (:893) | as 4.6 | **UPGRADED** (same as 4.6) |
| 4.15 | `pimos.syslog` made by the append, OURS (:1004) | `bios/boot/syslog.kl1`:33 opens it for append; `object/INSTALL` does not ship it | CONFIRMED |
| 4.16 | a `shell.com` or `pimos.com` in the home would be OURS (:1009) | `object/INSTALL`:8 puts the objects in `PIMOS.DIR`, not in the home | CONFIRMED |
| 4.17 | how the firmware held LUN 1 open: INFERENCE (:1098) | not in the held source (bios SCSI), the manuals or the corpus (`disconnect`, `reselect`) | NO SOURCE FOUND |
| 4.18 | the idle test, OURS (:1130) | by design | NO SOURCE FOUND |
| 4.19 | login record ID = 1, OURS (:1143) | §6.5: the real requester's ID is "the smallest integer from 0 not in use" (pimfep `pimos_remote_login_socket_table get_key/4`); the first login is 0 | **CONFIRMED that it is a deviation**: the PSI would send 0 for the first login. Noted, not changed (the run's tapes depend on it) |
| 4.20 | RN `"pmpsi"` is the SIMPOS user, INFERENCE; RP `""` OURS (:1146-1147) | `pimosobj/object/login.com` `"me" := ["user:pmpsi"]` (held); `primer25.tex` gives the pseudo-Multi-PSI setup with logical directories under `>sys>csp`, but no user | CONFIRMED for the name; the user role NO SOURCE FOUND (counted as CONFIRMED) |

## §5 Proposed changes to `pim/psi/` (ready to apply; NOT applied)

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
- **P-k1. Rows 42, 43, 44, 45: mnemonics and meanings.**
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

## §6 Open after this check

- No V3.0 PIMOS source is held, so `login Server End` stays INFERENCE
  (3.5).
- The `PE00(00) @ ` part of the CSP prefix is not traced in `pimmcsp`
  (3.9).
- The PSI's hash function (blt 6b) has no primary statement anywhere in
  the corpus.
- The opcodes still without a row, and the unrowed blt 42 that U2's
  arithmetic uses (4.10).
- The OCR corpus covers about half the held TR/TM pages. It covers all
  of the SIMPOS-related pages but TM-305.
