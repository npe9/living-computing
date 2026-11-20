# The Pseudo PIM/m microprogram: layout of `pimm.MEkbn`

Continues `pseudo_pimm_firmware.md` section 3 ("Not read"). Looked at
2026-11-20, time-boxed. Everything describes the Pseudo PIM/m (PIM/m KL1
firmware on a PSI-III), not a PIM/m processing element.

`asm/mekbn.py` reads the file; `asm/mekbn.py --check` pins every number
marked MEASURED below and is in `run_tests.sh`. Statements are
labelled MEASURED (a number from the tool), or INFERENCE.

Sections 7-13 are a second pass the same day (control flow, the
immediate, bit 62, two operand selects, the allocator; then what
that does and does not give for goal records and suspension). They
correct four statements of the first pass, each marked *Corrected* where
it stands. Section 13 says what was not known after that pass.

Sections 14-20 are a third pass (the memory datapath: read and write
strobes, the two address and two data registers, timing; then the
multiple-suspension record and the goal record). They correct the
second pass in five places, listed in section 14. **Recovered: the memory datapath (read, write and step strobes, two
address and two data registers, timing); the multiple-suspension
record's four fields and which tags they carry, with their order
(prev, next, goal, rival) resting on one addressing rule that is
supported but not verified; that a `HOOK` pointer addresses the first
cell of a goal record taken from the register `1b` list, and what
`suspend` writes in its cells 12-14 on one path. Inference only: 16
cells, cell 15 as the link, `R14` as the head of the ready list. Not
recovered: arity, priority, the use of the Goal Stack Entry Table.**

## Answer in brief

- The microinstruction at address `A` of the KL1 microprogram is file
  words `0xba00 + 2*A` (low 32 bits) and `0xba00 + 2*A + 1` (high 32
  bits), both with tag byte 0. `A` runs `0..0x67ff`. (File words are the
  40-bit words `psdpim.words()` returns, counted from 0.)
- A decode entry's start address is in its second word, in one of two
  forms selected by that word's tag byte:
  - tag `& 0x18 == 0`: address = value bits 14..0;
  - tag `& 0x18 != 0`: address = `(decode index >> 7) << 11` | value
    bits 9..0, and value bits 15..10 are a 6-bit immediate (a tag:
    `ATOMo` for `wait_atom`, `VECT3o` for `wait_vector_3`, `COD` for
    `code`).

  The decode index is `class * 256 + opcode`, so the KL1 pages are
  `0x2800` (GMI opcodes `80`-`ff`), `0x3000` (KLB `00`-`7f`) and
  `0x3800` (KLB `80`-`ff`).
- `mekbn.py --entries` prints the start address of every KL1
  instruction; `--dis ADDR N` prints microinstructions.

## 1. File layout (MEASURED)

| File words | Content |
|---|---|
| `00000`-`007ff` | decode table, 1,024 two-word entries |
| `00800`-`008ec` | descriptor 1 |
| `00900`-`0b8ff` | image 1: `0x5800` microinstructions |
| `0b900`-`0b9a9` | descriptor 2 |
| `0ba00`-`189ff` | image 2: `0x6800` microinstructions |

The gaps between are zero. The last two words of image 2 (address
`67ff`) are `2e111993:00 00000002:00`, which reads like a date and is
not explained.

**Pointers are file word + `0x4200`**, the header's load address:

| Word | Value | Is |
|---|---|---|
| `0801` | `00004a03:1c` | pointer to word `0803` |
| `0802` | `0000fb00:0b` | pointer to word `b900` (descriptor 2) |
| `0803` | `00004b00:00` | pointer to word `0900` (image 1) |
| `0804` | `58000000:00` | image 1 length in the high half |
| `b900` | `0000fc00:00` | pointer to word `ba00` (image 2) |
| `b901` | `68000000:00` | image 2 length in the high half |

Every decode entry of classes 0 and 1 that is not all zero (455 of 512;
57 are all zero) has `4a01` in the high half of its first word, and
every non-empty one of classes 2 and 3 has `4a02`:
the addresses of words `0801` and `0802`. So the decode entry itself
names its image: classes 0/1 (PMI, BLT) use image 1 and classes 2/3
(GMI, KLB) use image 2. The words called "nano-code that starts
`4a01`/`4a02`" in the earlier note are this link plus 16 bits of
nano-code.

**`sysidat` is the class 0/1 half of the decode table**, packed eight
bytes to an entry: the second word's value (4 bytes) and tag, a zero
byte, and the first word's low 16 bits. It has no link half. Of its
first 512 records 496 equal this file's entries; the 16 that differ are
indices `1a0`-`1af`, and its 16 records past the 1,024th are exactly
this file's entries `1a0`-`1af`. Records 512-1023 are zero. So classes
0 and 1 are the PSI-III system's own decode table (with the alternate
`1a0`-`1af`), independently of the `4a01` link, and the high half of a
first word is a link, not nano-code.

**The runs of 16-bit pairs are lists of decode indices**, read high
half first, each ending in a word with tag `0a` that holds one index.
They are not page maps or permutations.

- Descriptor 2's list (words `b902`-`b9a7`, 331 items, 324 distinct) is
  exactly the set of non-empty decode entries of classes 2 and 3. It is
  in order of start address: 0 descents in 330 steps under the rule in
  section 3, 22 descents if the low 15 bits are taken as the address
  throughout.
- Descriptor 1's list (words `0805`-`08ea`, 459 items, 443 distinct,
  values `000`-`1ff`) is in start-address order for image 1 with 7
  descents under the same rule (61 without it). It omits 12 of the 455
  entries that are not all zero (`050`, `05a`-`05d`, `0fc`,
  `17c`-`17f`, `1bf`, `1c6`) and lists `1a0`-`1af` twice each, the
  sixteen indices that have two versions in `sysidat`.

After each list come two words, `00004a02:00 00000000:01` after list 1
and `00004a01:00 00000000:01` after list 2. Not explained.

Code starts on 16-microinstruction boundaries: of the 67 places in
image 2 where code follows eight or more zero microinstructions, 66 are
at a multiple of 16, 58 of 32, 24 of 1,024 (image 1: 76 of 76, 63, 19).
This is the "zero gaps end on boundaries" observation in address terms;
the earlier "256-word" figure was a file-word artefact.

## 2. Word pairing and the two images (MEASURED)

- `PMPSI.DIR/syspsi` is flat: a 256-byte header and 32,768 eight-byte
  records. Read little-endian, record `A` is the microinstruction at
  WCS address `A`.
- **Image 1 equals `syspsi` addresses `0..0x57ff` exactly**: all 22,528
  microinstructions agree, 17,496 of them non-zero. This fixes the
  pairing (two consecutive file words), the order (low half first) and
  that the tag bytes are zero (0 non-zero tags in either image).
- Image 2 is a different program: 18,343 non-zero microinstructions, 15
  equal to image 1 at the same address (twelve in `0000`-`000f`, and
  `3d84`, `4281`, `483b`).

INFERENCE: image 1 is the PSI-III's own (KL0/ESP) firmware and image 2
the KL1 firmware; the file carries both because the README calls the
directory "KL0 and KL1 firmware". Why only the first `0x5800` words of
`syspsi` are repeated is not known.

INFERENCE, weak: the KL1 program runs with `syspsi`'s upper control
store in place. 238 absolute branches in image 2 (section 4) go to 15
distinct addresses at or above `0x6800` (`6c06`-`6c23`, `7214`, `7303`,
`7358`, `7476`, `75b6`, `7de6`, `7de7`), outside image 2; all 15 are
non-zero in `syspsi`. That region of `syspsi` is about 85% non-zero, so
15 hits is roughly a one-in-ten chance result.

## 3. Decode entries (MEASURED, with the anchors)

The rule in "Answer in brief" was found from the order of descriptor
2's list. Of all one-bit predicates over the 80 bits of an entry and
all ORs and ANDs of two, exactly two bring the list to 0 descents: tag
bit 3 or bit 4 (`0x18`), and tag bit 3 or bit 5 (`0x28`). The rule was
then checked against things it was not fitted to:

1. **Every start lands on code.** All 331 list items, and all 216
   distinct KL1 entries, start on a non-zero microinstruction. (Image 2
   is 69% non-zero. This check does not discriminate the page: a page
   shift of 10 instead of 11 also lands 331 of 331. The list order
   does: 12 descents.)
2. **The 6-bit immediate is the tag the instruction's name predicts**,
   against `asm/kbn.py`'s `TAGS` (from the PIMOS inspector's source),
   for 28 entries, of which 22 are informative (six predict `INTo`,
   which is zero). The list was assembled after seeing `--entries`, so
   the weight is on the ones that cannot be chance: the
   `wait_vector_0`..`_6` sequence, `COD`/`MOD`, and item 3. The 28: `atom` `ATOMo`, `integer` `INTo`, `list` `LISTo`,
   `code` `COD` (`26`), `module` `MOD` (`27`), `wait_atom` and
   `wait_nil` `ATOMo`, `wait_list` `LISTo`, `wait_vector_0`..`_6`
   `VECT0o`..`VECT6o`, `wait_vector` `VECTo`, `set_atom`, `put_atom`,
   `write_atom` `ATOMo`, `switch_on_non_integer/atom/list`
   `INTo`/`ATOMo`/`LISTo`, `collect_list` `LISTo`, `collect_vector`
   `VECTo`, and `integer`, `wait_integer`, `switch_on_non_integer` and
   the three `set/put/write_integer` forms `INTo`.
   `wait_list` and `wait_vector_1`..`_6` share the routine at `39e0`
   and differ only in the immediate.
3. **The code at the `put_vector_N` entries carries `VECTNo`.**
   `put_vector_3`..`_6` start at `3201`, `3203`, `3205`, `3207`; each
   is two microinstructions, a call to `3331`/`3334`/`3337`/`333a` and
   then a page-relative branch to `3209` whose immediate is `16`, `18`,
   `1a`, `1c`. `put_vector_0`..`_2` (`31f8`, `31f9`, `31fd`) carry
   `10`, `12`, `14`.
4. **The same rule orders descriptor 1's list** for image 1: 61
   descents fall to 7, 457 of 459 land on code.

Observed fault injections into `--check`, each FAILed and restored:
selector mask `0x08` instead of `0x18` (6 descents, 3 starts on zero
words, `collect_list` loses its tag); page shift 10 (12 descents);
immediate taken one bit low (24 entry tags wrong); the two halves of a
microinstruction swapped (image 1 no longer equals `syspsi`, all seven
`put_vector` tags lost); images taken one microinstruction late
(`put_vector_0`..`_2` tags lost, page-relative targets fall on zero
words).

Not established about the entries:

- The rest of the second word (value bits 31..16, tag bits other than
  `0x18`) and the 16 nano-code bits of the first word. Tag bits `0x10`
  and `0x20` occur together in classes 2/3, so the selector may be
  `0x08 | 0x10`, `0x08 | 0x20` or all three; `0x18` is what also fits
  class 0/1 best (7 descents against 9).
- Whether a zero immediate means `INTo` or "no immediate" (`less_than`
  .. `modulo`, `wait`, `wait_constant` have zero).
- INFERENCE: the second word is shaped like the low half of a
  microinstruction (immediate/address in bits 15..0), consistent with
  TM-1074's remark that the last microinstruction's phase 1 is driven
  by the decode stage.
- Descriptor 2's list repeats index `376` (`register_tag_and_value`)
  eight times, unexplained. Descriptor 1's 7 remaining descents and 12
  omissions are unexplained.

Entry points of interest for the runtime (from `--entries`):
`otherwise` `1c00`, `suspend` `1c08`, `read_eagerly` `1ce2`,
`try_me_else` `216a`, `proceed` `216c`, `enqueue_goal` `4c00`,
`enqueue_goal_with_priority` `4c5c`, `execute` `4cc0`, `create_shoen`
`1694`, `merge` `3e54`, `collect_garbage` `02d5`, `start` `2028`.

## 4. Microinstruction fields

MEASURED:

- Bits 25..23 select the branch kind and bits 15..0 are its operand.
  These are TR-733 fig. 4's `JMPF` and `EM1`-`EM3` at the positions
  `literature_gaps.md` Appendix C 2.3 measured from the figure, so that
  part of the hypothesis holds.
- `JMPF` = 5: bits 15..0 are an absolute address. In `syspsi` 1,455 of
  1,455 targets are non-zero. In image 2, 1,889 of 2,127 are non-zero
  inside the image and the other 238 are the out-of-image targets of
  section 2.
- `JMPF` = 2, 3, 6, 7: bits 9..0 are an address in the current
  1,024-word page and bits 15..10 a 6-bit immediate. Page-relative
  targets non-zero in image 2: 525 of 532, 246 of 246, 1,497 of 1,497,
  231 of 231 (taken as absolute, 1,862 of 2,506 land: 74%, against a 69%
  baseline).
- Bit 15 and bits 18..16 are sparse (bit 16 set in 2-3% of words), and
  bits 14..0 are each set in 20-30%, as a 15-bit address field with
  modifier bits above it would be.

INFERENCE or not checked:

- `JMPF` = 1 often carries a 15-bit absolute address (2,063 of 4,918
  within 256 of the instruction's own address in image 2) but was not
  separated from its other uses. `JMPF` = 0 and 4 not characterised.
  Which kind calls and which returns is not established (`JMPF` 5 looks
  like the call: `put_vector_N` uses it for a shared routine and then
  continues).
  *Corrected in section 8:* the `JMPF` 1 address is not bits 14..0. It
  is EM bits 14..4 with bits 22..19 as the low four bits; all eight
  kinds are characterised there.
- What the 6-bit immediate is in general. It is a tag in every anchor
  above, but its distribution over all page-relative branches (value 0:
  552, `10`: 326, `01`: 182) says it is also used for other constants.
- The meaning of `CNDF` (bits 22..19) values. *Corrected in section 8:*
  with `JMPF` 1 these four bits are not a condition at all.
- All other field boundaries `--dis` prints (`CCF`, `DST`, `SC1`, ...)
  are the figure's and untested.

## 5. Tried and failed, or misleading

- **Low 15 bits as the address for every entry.** 22 descents in
  descriptor 2's list; `wait_vector`, `processor_profile`, `log_event`,
  `collect_vector`, `put_reused_structure` fall outside the image;
  `less_than`, `wait`, `wait_value`, `divide_extended` fall on zero
  words. "204 of 216 land on code" under this reading looked like
  support and was not: the baseline is 69% and several hits are
  accidents (`set_atom` is `3188`, not `0988`; `wait_atom` is `3960`,
  not `0960`; `less_than`..`modulo` are `3a48`..`3a88`, not
  `0248`..`0288`).
- **Searching for a branch field by "value near own address" with 8- to
  12-bit windows.** Dominated by noise; every window scored alike. The
  15-bit window at bit 0 conditioned on bits 25..23 is what separated.
- **Reading the 16-bit runs as a permutation or page map.** They are
  index lists (section 1).
- **`sysinit` and `sysidat` as microcode.** No non-zero record of
  either equals `syspsi` or either image at the same offset from their
  header addresses (`0x5000`, `0x6800`). `sysidat` turned out to be a
  decode table (section 1); `sysinit` (8,286 records, header `0x5000`)
  is not identified.
- **Console text.** The reverse assembler's strings give register and
  tag names and "Input WCS Base (default #6800)" but no field table;
  the Micro Field Modifier's grammar (`[N]`, `[N,M]`) does not state a
  width or numbering. One by-product: its tag list ends `SHREC FPREC
  FPRECt DREF GOAL res3d res3e res3f`, so INFERENCE: `GOAL` is tag
  `3c`. 13 page-relative branches in image 2 carry immediate `3c`; they
  were not read.

## 6. Open, in order of use

1. Read the suspension code from `suspend` (`1c08`) and the enqueue
   code from `4c00` with `--dis`. This needs the meanings of `JMPF`
   0/1/4 and `CNDF` first: take the 32-entry dispatch tables at
   `3800`-`38bf` (the six `get_*` entries start 32 apart there, which
   looks like one row per tag pair; INFERENCE, not read) as the worked
   example. `--tag HOOKo` (39 sites,
   11 in page `2c00`), `--tag MHOOK` (46, 17 in page `2c00`) and `--tag
   DREF` (14, 10 in page `2c00`) point at page `2c00` as the
   suspension/resumption code; that is a count, not a reading.
   *Corrected in sections 9 and 11:* the tables are eight rows of four
   words, not 32 entries; and `--tag` then listed page-relative
   branches only, which missed every word that writes a tag. With
   those included the `MHOOK` writes are in `1d24`-`1d75` (reached from
   `suspend`) and `2d46`-`2ef8`.
2. The register-select fields: test the figure's `DSTF`/`SC1F`/`SC2F`
   positions against the register-operand families (`set_atom`,
   `put_atom` take the register from the opcode's low bits).
   *Done in section 10, with a negative result for the test as posed:*
   the operand's register number is not in the microinstruction.
3. The other 16 bits of each decode word.
4. (Done: `asm/mekbn.py --check` is in `run_tests.sh`.)

## 7. Second pass: what was done, and the labels

Time-boxed, 2026-11-20. Labels: MEASURED (a number `mekbn.py` prints
and `--check` pins), DERIVED (follows from a verified rule applied to
the listed addresses), INFERENCE. A rule is called verified only where
it predicted something in code it was not fitted on; the fit and the
prediction are named each time. Three approaches to the field meanings
were used: (a) minimal pairs, the XOR of two routines whose semantics
differ in one known way; (b) statistics over the control-flow graph of
the whole image; (c) the same rule applied to `syspsi`, an independent
program in the same format (the PSI-III's own firmware, section 2).

`mekbn.py` now has `flow(a, x)`, the rules of section 8; `--dis` prints
them (`end`, `return`, `jump`, `call`, `branch`, a trailing `?` for
"conditional"); `--tag NAME` also lists words that carry the immediate
with bits 17..16 non-zero (`stamp`); `--alloc` lists the allocator
entry words of section 10 and what reaches them.

## 8. Control flow (MEASURED and verified)

| `JMPF` | Meaning |
|---|---|
| 0 | fall through |
| 1, EM bit 3 set | jump to `(EM & 0x7ff0) \| bits 22..19` |
| 1, EM bit 3 clear | end: EM bit 2 clear ends the machine instruction, EM bit 2 set returns from a microsubroutine |
| 1, EM bit 1 set | the jump, end or return is conditional; the next word is the other arm |
| 2 | page-relative conditional branch |
| 3, 6 | page-relative jump; conditional when bits 22..19 are non-zero |
| 4 | jump to own address + EM bits 3..0, signed; conditional when bits 22..19 are non-zero |
| 5 | call, absolute |
| 7 | call, page-relative |

**`JMPF` 1 does not use bits 22..19 as a condition.** With `JMPF` 0 the
field is zero in 6,063 of 8,180 words; with `JMPF` 1 its sixteen values
are evenly spread (133 to 282 words each, 2,131 zero of 4,918). That is
what address bits look like, and it was the clue.

- Fit: `set_list` (`3186`), `set_marked_variable` (`3190`),
  `put_vector_1`/`_2` (`31fc`, `3200`), which jump to `3378` and
  `337d` after taking a cell.
- Prediction 1: 2,830 `JMPF` 1 words in image 2 have EM bit 3 set;
  2,721 targets are inside the image and **2,710 land on a non-zero
  word (99.6%, baseline 69%), on 1,430 distinct addresses**. In
  `syspsi`: 3,918 of 3,973 (98.6%, baseline 74.5%), 1,899 distinct.
  Landing alone does not discriminate the low four bits (code is
  dense: dropping them lands 2,711); prediction 2 does.
- Prediction 2: the size-dispatch tables of section 10. Ten words at
  `31ac`-`31c6` (the general `put_vector`) are `JMPF` 1 jumps whose
  targets, under this rule, are exactly the allocator entry words
  numbered 3, 4, 5, 6, 13, 12, 11, 10, 7, 8, the first four being the
  same addresses `put_vector_3`..`_6` reach by `JMPF` 5. With the low
  bits dropped, two of the ten are allocator entries (both the same
  one).
- Prediction 3: no word may jump to itself unconditionally. Under the
  rule none does; with the low bits dropped 25 words in image 2 and 23
  in `syspsi` do.

**Conditional or not** was read off what follows each word. A word is
an "explicit target" if some branch names it or a decode entry starts
there (20% of non-zero words). After a word that always transfers, the
next word is zero or an explicit target; after one that can fall
through, it rarely is:

| Kind (image 2) | words | next word zero or an explicit target |
|---|---|---|
| `JMPF` 0 | 8,180 | 7% |
| `JMPF` 1, EM bits 2..0 = 0, 4 (bit 3 clear) | 603, 864 | 65%, 61% |
| `JMPF` 1, EM bits 2..0 = 2, 3, 6, 7 (bit 3 clear) | 602 | 5-13% |
| `JMPF` 1 jump, EM bits 2..0 = 0 | 1,859 | 57% |
| `JMPF` 1 jump, EM bits 2..0 = 2, 3 | 811 | 9-11% |
| `JMPF` 2 | 532 | 14-18% |
| `JMPF` 3 | 246 | 54-70% |
| `JMPF` 4 | 611 | 31-49% |
| `JMPF` 5 | 2,127 | 9% |
| `JMPF` 6 | 1,497 | 36-43% |
| `JMPF` 7 | 231 | 4-14% |

`syspsi` gives the same split kind for kind (66%, 73%; 6-12%; 62%;
14-15%; 6-16%; 45-66%; 24-48%; 9-16%; 34-43%; 8-11%). The unconditional
kinds do not reach 100% because the explicit-target set is incomplete
(the dispatch tables of section 9 are reached through the decode stage,
not by a branch word). These percentages are scratch output, not
pinned; what is pinned is the next test, which depends on them.

**Call and return.** Fit: `put_vector_3`..`_6` (`3201`-`3208`) use
`JMPF` 5 and continue at the next word, and the subroutine at `12e0`
ends in `JMP=1 EM=4`. Prediction: reading on from each call target to
the first word that cannot fall through, a subroutine must show a
return and a machine instruction's entry must show an end.

| Read on from | return | end |
|---|---|---|
| targets of `JMPF` 5 and 7, image 2 | 222 | 10 |
| targets of `JMPF` 5 and 7, `syspsi` | 250 | 13 |
| KL1 decode entries, image 2 | 0 | 96 |
| decode entries of classes 0/1, `syspsi` | 0 | 122 |

(The rest reach a jump first.) This one test stands on four rules at
once: EM bit 2 is "return", EM bit 1 is "conditional", `JMPF` 5 and 7
are the calls and 3 and 6 are not. `3378`/`3379` against `3376`/`3377`
shows `JMPF` 7 beside `JMPF` 6 in the same routine: the first pair is
"jump to `3365`", the second "call `3365`, then end".

**`JMPF` 3, 4 and 6 are conditional when bits 22..19 are non-zero.**
The successor table cannot show this (it gives 31-54% for those words,
between the two groups). What shows it: 23 words in image 2 jump to
their own address (17 `JMPF` 6, 6 `JMPF` 4; `1c30`, `1c35`, `3367`,
`336e`, `3374` among them) and every one has bits 22..19 non-zero (6,
`b` or 2). A loop has to be able to leave. Fitted on image 2;
`syspsi` has 37 such words and again none with the field zero. What
each value tests is not known; value 6 with bit 18 set is the
counted-loop case (`1c30`). The first version of this section called
3, 4 and 6 unconditional outright; with the correction the call/return
table above changed from 181/9, 198/6, 74 and 101 to the numbers
shown, and no entry moved to the wrong column.

**`JMPF` 4.** Fit: `3383`, `3385`, `3389` (EM bits 3..0 = 7, 5, 1) all
reach `338a`, the address the `JMPF` 6 at `3387` names. Prediction: the
word at `338c` has `e`, which is `338a` only if the field is signed;
over the image the 193 words with the top bit set land 193 times
signed and 175 unsigned (`syspsi`: 277 of 277 against 251).

INFERENCE, not verified:

- EM bit 0 of a `JMPF` 1 word. `1c3e` and `1c54` (EM bits 3..0 = `d`)
  jump to a 16-aligned address where a run of single-word jumps
  stands, one per size (section 10): a multi-way dispatch that ORs an
  index into the low address bits. Fitted on those two; the other two
  size tables found by their content, `31c0` and `4e40`, are each
  entered only by such a word (`31b1`, `3210`; `4e39`), which is three
  predictions met. What supplies the index is not known, and the other
  66 words with EM bits 2..0 = 5 were not examined (`--dis` prints
  `bit0` for them).
- What a `JMPF` 2 branch or a conditional `JMPF` 1 tests. TM-862 says
  the condition is formed one cycle before the branch; in the dumps a
  word with `JMPF` 0 and non-zero bits 22..19 usually precedes one
  (`3184` before `3185`, `31fa` before `31fb`). So bits 22..19 of a
  `JMPF` 0 word probably select the condition the next word uses. No
  condition code was identified.
- Why there are two page-relative jumps (3 and 6), and whether a
  `JMPF` 5 word with bits 22..19 non-zero (31 words) is a conditional
  call.

## 9. The immediate, and the rows of a dispatch table

**EM bits 15..10 are a 6-bit immediate in any word**, not only in a
page-relative branch; bits 9..4 and 3..0 are separate (TR-733's
`EM1`/`EM2`/`EM3` split holds).

- Fit: the allocator words at `3331`, `3334`, `3337`, `333a` carry 3,
  4, 5, 6 in bits 15..10 (EM = `0da0`, `11a0`, `15a0`, `19a0`), and
  `put_vector_3`..`_6` call exactly those. So here the immediate is a
  number, not a tag.
- Prediction: `set_nil` (`3189`), `set_list` (`3183`), `set_variable`
  (`318b`), which must write an `ATOM`, a `LIST` and an unbound cell,
  carry `02`, `04` and `08` (`UNDF`) there, with bits 17..16 = 2. MEASURED
  by `--dis`; not separately pinned.
- With bits 17..16 = 1 or 2 and `JMPF` 0 the immediate's values over
  the image are tag-like (most common: `INTo`, `ATOMo`, `REFo`, `HOOKo`,
  `COD`, `VDESC`, and `3c` twelve times under bits 17..16 = 1).
  INFERENCE: bits 17..16 non-zero means "use the immediate as a tag";
  what distinguishes 1, 2 and 3 is not known. `write_nil` (`3193`,
  EM = `8020`, bits 17..16 = 3) has its `02` in bits 9..4, so the rule
  is not simply "bits 15..10".

**A `get_*` or `wait_*` entry is a table of eight rows of four words.**
The six `get_*` entries are 32 apart for that reason. DERIVED from
`3800`-`381f`, `3820`, `3840`:

- Rows 0 and 1 are the same two words except the immediate: `ATOMo`
  and `ATOMx` for `get_atom` and `get_nil`, `INTo` and `INTx` for
  `get_integer` (fitted on `get_atom`; `get_integer` and `get_nil`
  predicted). Their second word has bit 62 (section 10) and
  ends the instruction. INFERENCE: rows 0 and 1 are "unbound, not
  multiply referenced" and "unbound, multiply referenced", and bind.
- Rows 2 and 3 of `get_atom` call `0cf1` and then write and end; row
  4 jumps to `0cd0`; rows 5-7 call `0cd4`, `0cda`, `0cdc` and then jump
  to `0c00`.
  INFERENCE: these are the hooked-variable and bound cases. Which row
  is which tag comes from the tag dispatch table (TM-858's TGT), which
  was not found in this file and is not in the microinstructions.

## 10. Bit 62, two operand selects, the allocator

**Bit 62 (the top bit of the figure's `CCF`) is a memory operation
that every `set_*`/`write_*` has and register arithmetic never has. It
is not shown to be "write".** *Corrected in section 15:* it is the
write strobe; bit 61 is the read strobe; the "reads" below that carry
bit 62 push a freed cell on a free list.

- Fit (minimal pairs): `set_integer`, `set_value`, `set_atom` are the
  one word `4000000000800000`; `write_integer`, `write_atom`,
  `write_value` are `4000000000848000`; `put_integer`, `put_value` are
  `0490000200800000`. The `*_constant` endings at `31cc` (put), `3181`
  (set), `3192` (write) differ only in bit 62.
- Prediction met: in the guard comparisons and arithmetic
  (`3a48`-`3a8f`), the type checks (`3abe`-`3acf`), the guard shifts
  and logic (`3af0`-`3b27`) and the body arithmetic (`2928`-`29b7`) it
  is set in **0 of 219** non-zero words; over the image it is set in
  2,177 of 18,343 (12%), so about 26 were expected by chance. All
  eleven `set_*`/`write_*` routines checked have it on their straight
  line; none of `put_integer`, `put_atom`, `put_nil`, `put_value`,
  `put_constant` does.
- **Prediction failed for "write":** routines that should only read
  memory have it too. `vector_element` (`5011`-`5057`) has it in 17 of
  67 words, the shared tails of `read_atom`/`read_integer`/
  `read_constant` (`3438`-`3459`) in 18 of 38; `3442`, which differs
  from `put_value`'s word only in bit 62, bit 18 and EM bit 15, looks
  like "take the element at the structure pointer into a register and
  advance". Against that, `read_variable` (`34a0`-`34bf`) has it in 0
  of 29 and `string_element`/`b_string_element` in 0 of 10. So the bit
  is either a memory access of a kind both writes and some reads use
  (through the structure pointer, or a second access port), or those
  routines write for a reason not understood (MRB marking). Counted in
  scratch, not pinned.
- Not known: the other four bits of `CCF`, where the address and the
  data come from, how a plain read is requested.

**The register operand of a machine instruction is not in the
microinstruction** (negative result for agenda item 2 of section 6).
`put_integer` (`31cd`) and `put_value` (`31da`) are the same word
although one moves a constant and the other a register; `set_value`,
`set_integer` and `set_atom` are the same word. The operands are
prepared before the E stage (the decode entries differ:
`7c0901cd:08` against `000031da:06`), as TM-1074 describes. So the
one-word routines say nothing about `SC1F`/`SC2F` and the argument
offset of `set_value` is not in the microcode at all.

What they do give: **`DSTF` and `SC1F` are register selects at the
figure's positions, and values 8 and 9 mean "the register named by the
instruction", through two different operand fields.**

- Fit: `put_integer` (`31cd`) and `put_atom` (`31ce`) differ in one
  bit, bit 52: `DST` = 9 and 8. `put_atom` takes its register from the
  opcode's low bits, `put_integer` from the `x` byte.
- Prediction: `wait_atom` (`3960`) and `wait_integer` (`39a0`) differ
  the same way. They do: `SC1` = 8 against 9 in the first word, `DST` =
  8 against 9 in the second, and nothing else in those fields.
- The pin holds the values; the injections (section 12) show it is
  sensitive to the field positions, but two positions one bit apart
  are not excluded by it alone. The single-bit differences are the
  evidence for the positions.

DERIVED from the same routines, each seen in three or more places but
not tested by prediction: `DST` = 2 is the structure pointer
(`put_vector_0`..`_2` `31fb`/`31ff`, `put_list` `31d2`, and `3209`
where all of `put_vector_3`..`_6` end); `DST` = 4 with `EM` = `10` is
"go to the alternative clause" (`3967`, `39a7`, `391a`, the failing
arms of `wait_*`).

**The allocator.** `--alloc` lists seventeen words of the form
`0402af40 0000xxa0` whose immediate N is 3-8 and 10-13
(`3331`, `3334`, `3337`, `333a`, `333d`, `3340`, `3354`/`3356`, `3359`,
`335b`, `335d`, and a second family `3382`-`338d` for 3-8).

- Fit: `put_vector_3`..`_6` call the words with N = 3..6.
- Prediction: the general `put_vector`'s table (`31ac`-`31c6`, section
  8) continues the series: its words go to N = 3, 4, 5, 6 and then 13,
  12, 11, 10, `334d`, 7, 8. MEASURED and pinned.
- DERIVED for N = 3..6: "the word with immediate N begins the
  allocation of N cells". One and two cells do not use these words:
  `put_vector_1` and `set_variable` use register `19` (routines
  `3320`/`3325`), `put_vector_2` and `set_list` use register `1a`
  (`332a`/`332c`). A third table (`4e41`-`4e46`, entered from `4e39`,
  routine not traced) has, in order, `3326`, `332d`, then N = 3, 4, 5,
  6, which fits "position = cells" for 1 to 6.
- **N is not shown to be a cell count above 8.** There is no N = 9
  word; in its place in the tables stands a routine with register `1b`
  and three entries, `3349`, `334b`, `334d`, that differ only in the
  immediate they carry: `HOOKo`, `FPREC`, `VDESC`. INFERENCE: N is a
  free-list number, equal to the size for 1-8, and 9-13 are larger
  classes. The sibling Multi-PSI/V2 is published as having free lists
  for 1..8, 16, 32, 64, 128, 256 words (`literature_gaps.md` Appendix
  A, gap 7), which is thirteen lists; if this firmware is the same,
  register `1b` is the 16-word list, and a 14-field foster-parent
  record (the `FPREC` entry) fits it. No size was read from the code.
- INFERENCE: `19`, `1a`, `1b` hold the heads of those free lists. **This conflicts with
  `wait`** (`38c0`, `38c1`), which reads `SC1` = `19` and writes `DST`
  = `19` with bit 62 when its operand is unbound, where no
  allocation is expected. Either `19` is not a free-list head or a
  5-bit select means different registers in different words. Not
  resolved; it is the reason no register is named beyond the ones
  above. *Resolved in section 15:* `38c0`-`38c1` is a push on the
  one-cell free list (the shape of `collect_value`), not the unbound
  case.

## 11. Goal records, suspension, the ready structure: what the code shows

None of the three layouts was recovered. What follows is the part that
stands on sections 8-10, and then what is only suggestive.
*Superseded in part by sections 17 and 18* (third pass): the
multiple-suspension record's four cells and the goal record's size,
pointer and trailer are read there.

MEASURED (from `SYSTEM.DIR/PIMM.PARAM`, the firmware's parameter
file; the three `gse` lines are pinned as `gset_param`):

- The Goal Stack Entry Table has a base and a **shift count**:
  `gseb = 10:B800`, `gsesh = 16'18`, commented "Goal Stack Entry Table
  "GSET" Shift Count (`16'20 - log2(Entry)`)", `16'100` entries. So an
  entry is found by shifting a 32-bit value right until log2(entries)
  bits remain, 256 entries in this file. INFERENCE: the value is the
  goal's priority, so the table is indexed by the top eight bits of a
  32-bit priority, one goal stack entry per value. (The address
  differs from the parameter editor's default `005800` in
  `pseudo_pimm_firmware.md`.) The file's own first line calls itself
  `MPSI.PARAM` "FOR PSEUDO MULTI-PSI"; what that says about the file's
  origin was not followed up.
- Suspension Stack `sspb = 10:400`, limit `10:800`; Passive
  Unification Stack `10:200`-`10:400`.

DERIVED (control flow of section 8, allocator entries of section 10):

- **The first thing `suspend` does is take a record from the register
  `1b` allocator through its `HOOKo` entry.** `1c08` calls `1c1d`,
  which jumps to `3349`. `3349` has nineteen callers,
  among them `proceed` (`2175`, `218a`), `enqueue_goal_with_priority`
  (`4c62`), `start` (`202d`) and `1088`, after `consume_resource`'s
  entry. The sibling entries are `334b` (`FPREC`, no caller found by
  a branch word) and `334d` (`VDESC`, from the tables at `31c4` and
  `1e3c`).
- **Later, a subroutine of `suspend` allocates by size through two
  tables.** `1c3a` calls `1c3e`, a jump into `1c40`-`1c44`, whose
  targets are `332c` (register `1a`) and the allocator words N = 3, 4,
  5, 6. `1c4b` calls `1c53`/`1c54`, a jump into `1c58`-`1c5f`: `1c5b`-
  `1c5e` go to N = 10, `334c` (register `1b`), N = 8, N = 7, and
  `1c58`-`1c5a`, `1c5f` to `6c22`, outside the image (in `syspsi`'s
  upper control store). The second table is reached only on the path
  that first calls the N = 3 allocator (`1c47`), chosen by the branch
  at `1c39`, which carries the immediate `10`. Pinned as
  `suspend_size_table`. The order of the large entries differs from
  `put_vector`'s table (there N = 10, `334d`, 7, 8), not understood.
- **The multiple-waiter code allocates from the N = 4 word.** `1d3a`,
  called from `1d21` and `1d2b` and nowhere else, is `call 3334`; the
  next five words carry the immediates `HOOKo` (`1d3c`) and `DREF`
  (`1d3d`, with bit 62), and `1d40` jumps with `MHOOK` into a
  fifteen-word table (`1d50`-`1d5e`) whose words carry `MHOOK`,
  `EMHOKo`, `EMHOKx`, `HOOKx`, `RHOOKo`. The code is reached from
  `suspend` by the jump at `1c65`, which carries `DREF`. All 29 words
  in the image that carry `MHOOK` with bits 17..16 non-zero are in
  `1d24`-`1d75` and `2d46`-`2ef8`.
- `1c0a` carries `HOOKo` with bits 17..16 = 2; `enqueue_goal` carries
  `HOOKo` the same way at `4c05`, `4c06`, `4c13`.
- `3c`, the tag after `DREF` (inferred `GOAL`), is carried with bits
  17..16 non-zero by 21 words, among them `4c24` (after
  `enqueue_goal_external`), `2c82`, `19ec`-`19fc`.

INFERENCE (each needs the datapath fields to become a reading):

- **A goal record is one record of the register `1b` class, and a
  pointer to it is tagged `HOOK`.** For: `suspend`, `proceed` and the
  enqueue code all go through the `HOOKo` entry `3349`; `enqueue_goal`
  stamps `HOOKo`. That would make "a `HOOK` cell points at the goal
  record itself" true here, as published for Multi-PSI/V2, and the
  record a fixed size (16 words if the free lists are the sibling's).
  Against, or at least unexplained: `suspend`'s later size tables. If
  their index were the arity, the first would say "arity + 2 cells for
  arity 0-4", a variable-size record with a two-cell header. The two
  readings exclude each other for the goal record itself; the size
  tables may belong to something else `suspend` builds (what was not
  read). The index was not traced to its source.
- **The multiple-suspension record has four cells**, one written with
  `HOOKo` and one with `DREF`. Four is the number of items in the
  console's inspector (`prev`, `next`, `goal`, `rival`,
  `pseudo_pimm_firmware.md` section 2), which makes those items fields
  rather than navigation commands; `HOOK` for "goal" and `DREF` for
  the shared record a goal's suspensions have in common would be the
  VPIM arrangement (`literature_gaps.md` Appendix B, "Multiple
  suspend"), and that shared record is how a goal on several variables
  would be woken once. Which cell gets which, and that the `DREF`
  target is such a record, were not read.
- `1c30` and `1c35` jump to themselves with bit 18 (a counter
  operation in the figure) and bit 62: counted copy loops, presumably
  the argument registers into the new record.

Not found: the order of the goal record's fields, where the code
address, the priority and the shoen pointer sit, push and pop order on
a goal stack, how the Goal Stack Entry Table's entries are used, how a
single waiter's `HOOK` chain is linked, anything in `proceed` (`216c`)
beyond its control flow.

## 12. Fault injections into the new checks (observed)

Each was made by setting the named constant of `mekbn.py` and running
`check()`; each FAILed as listed and PASSes with the constant restored.

| Injection | Observed failures |
|---|---|
| `J1_LOW='x18'` (bit 18 in place of bits 22..19) | 1,430 distinct targets fall to 788 (`syspsi` 1,899 to 1,013; landings 2,711 and 3,861); 25 and 23 unconditional self-jumps appear; `suspend_size_table` right in 1 of 9 places, `put_vector_size_table` in 1 of 11, `third_size_table` in 0 of 6 |
| `J1_HIGH=0x7fe0` | landings 2,598 and 3,838; 3 and 6 unconditional self-jumps; the three tables right in 3 of 9, 2 of 11, 2 of 6 |
| `J1_HIGH=0x7ff7, J1_LOW='x18'` (low bits from EM bits 2..0 and bit 18) | landings 2,686 and 3,836; 24 and 25 unconditional self-jumps; tables right in 0, 1, 0 places |
| `J4_SIGNED=False` | backward `JMPF` 4 lands 175 of 193 (`syspsi` 251 of 277) |
| `J1_RETURN=1` | after a call: 5 returns, 227 ends (`syspsi` 2, 261); one decode entry "returns" |
| `J1_COND=1` | after a call 268/9 (`syspsi` 298/7); entry ends 94 and 128 |
| `CALLS=(5,6), GOTOS=(3,7)` | after a call 345 returns, 132 ends (`syspsi` 327, 187); entry ends 109 and 132 |
| `GOTO_COND=False` | all 23 and 37 self-jumps unconditional; after a call 181/9 and 198/6; entry ends 74 and 101 |
| `MEM_BIT=61` | 2 of 219 register-only words; ten of eleven `set_*`/`write_*` lose it |
| `MEM_BIT=58` | 68 of 219; six lose it, four `put_*` gain it |
| `EM1_SHIFT=9` | allocator numbers double (6, 8, ...); `put_vector_alloc` and all three tables wrong |
| `DST` at 55..51 | `operand_selects` items 3 and 5 |
| `SC1` at 52..48 | `operand_selects` item 4 |
| `gsesh` expected as `16'16` | `gset_param` `[1, 0, 1]` |

One injection did not fail and was replaced: widening the allocator
pattern's mask changes nothing, because the size is read from the same
bits either way.

## 13. Not checked, and the next step

Not checked:

- Every datapath field except the two select values, and what bit 62
  is beyond "a memory operation":
  `SC2F`, `SD1F`/`SD2F`, `AS1F`/`AS2F`, `ADF`, `ALF`, the low four bits
  of `CCF`, bits 63, 57 and 18. In the dumps `SD1` is non-zero exactly
  when `SC1` is and `SD2` when `SC2` is, as "where the register read
  goes" would be; untested.
- The condition codes, EM bit 0 of `JMPF` 1, EM bits 9..4 as an
  operation modifier.
- The tag dispatch table (which row of a `get_*` table is which tag).
  It is not in `pimm.MEkbn`'s microinstructions; `sysinit` (8,286
  records, unidentified, section 5) is the first place to look.
- The successor percentages of section 8 are not pinned.
- `proceed`, `execute`, `try_me_else`, `enqueue_goal` were dumped and
  not read; page `2c00` was not dumped. The routine `334e`-`3353` and
  the refill code at `3360`-`337f` were dumped looking for a record
  size and show none that could be read without the datapath.
- The work stopped on the time-box. The three approaches of section 7
  were all still producing results; none is exhausted.

*Done in sections 14-18; the current next step is in section 20.*
Most useful next step (as it stood): settle the memory datapath on the two smallest
routines that read and write through a known pointer, the one-cell
allocator (`3320`-`3324`: take the head of a free list, replace it by
the cell's link) and `write_variable`/`set_variable` (`318b`, `3195`:
write `UNDF`, make a `REFo` to it). Their semantics fix which of
`SC1`/`SD1`/`AS1`/`AS2`/`AD` carry the address, the data read and the
data written, and the `19` conflict of section 10 has to come out of
the same reading. With that, `1d3a`-`1d40` (five words) gives the
multiple-suspension record's field order directly, and `1c08`-`1c3d`
the suspended goal record's header.

## 14. Third pass: the memory datapath (what was done, and the labels)

Time-boxed, 2026-11-20, third pass. Goal: which fields read and write
memory, where the address and the data come from; then the
multiple-suspension record, the suspended goal record, and as much of
the goal record as the evidence carries. Labels as in section 7, plus
VERIFIED: a rule fitted on named routines that then predicted something
specific in code it was not fitted on (both named each time). A layout
is given only where it is DERIVED from VERIFIED rules; where a step
rests on something weaker it says so.

`mekbn.py --check` pins every number below (`img2_mem`, `syspsi_mem`,
`fill_after_alloc`, `records`, `enqueue_trailer`). `--rtl ADDR N`
prints the register transfers and memory accesses of each word under
these rules; `--records` prints the record writes of sections 17-18.

Seven predictions were written down before the routines were dumped
(scratch file, not in the repository). Their outcomes are in section
15; one was right for the wrong reason and one failed in `syspsi`.

**Corrections to the second pass** (each also marked where it stands):

- Section 10, "bit 62 is not shown to be write": **bit 62 is the write
  strobe.** The reads are bit 61, which the second pass did not look
  at. The "reading" routines that carry bit 62 push a cell on a free
  list (section 15).
- Section 10, the register `19` conflict: **resolved.** `wait`'s first
  row (`38c0`-`38c1`) has the shape of `collect_value`: it frees a
  cell. `19`, `1a`, `1b` are free-list heads.
- Section 4 and `FIELDS`: **bits 36..34 are not an ALU input.** They
  name the work register the ALU result goes to (section 16). The name
  `AS1` is kept in the tool so that the earlier dumps still read.
- Section 11, "the multiple-waiter code allocates from the N = 4 word
  ... which cell gets which ... were not read": read in section 17.
- Section 11, "a goal record is one record of the register `1b` class
  ... (16 words if the free lists are the sibling's)": which cells the
  code writes is now read (section 18); the size is still inference.

## 15. The strobes: bit 61 reads, bit 62 writes, bit 60 steps the address

The figure's five-bit `CCF` is five separate bits.

| Bit | Meaning | Status |
|---|---|---|
| 62 | write memory | VERIFIED |
| 61 | read memory | VERIFIED |
| 60 | add one to the address register after the access | VERIFIED |
| 59, 58 | in a strobe word: which MDR, which MAR (section 16). In a word without a strobe: "MDR2 is used", "MDR1 is used" | see section 16 |

**Read (bit 61).** Fit: the free-list pops of `put_vector_1`
(`31f9`-`31fa`), `put_list` (`31d0`-`31d1`) and the one-cell allocator
(`3320`-`3322`): the word with the bit is followed by a word that moves
`AS2` = 2 into the head register. Prediction: over the whole image the
word after a read uses `AS2` = 2. It does in **854 of 1,386** (62%;
`AS2` = 2 is in 25% of all words), and in `syspsi` in 907 of 1,867 (49%
against 24%). `read_variable`'s first word (`34a0`), which the second
pass counted as having no memory bit, has bit 61 and loads the
structure pointer (register 2) into an address register.

**Write (bit 62).** Fit: the `set_*`/`write_*` words of the second
pass. Predictions written before the dump, and what was found:

| Routine | Predicted | Found |
|---|---|---|
| `collect_value` `3000` | a write, and the head register takes the cell's address | `3001`: write, `DST` = `19` from `AS2` = 3 (the address); the word before loads the old `19` as data. Met |
| `mark_element` `30a9` | at least one write | `30aa` reads, `30ab` writes. Met |
| `wait` `38c0`-`38c1` | one write, no read ("pushes the variable on the suspension stack") | one write, no read, **but it is `collect_value`'s shape** (old `19` as data, `19` takes the address): it frees the cell the operand was reached through. Count met, reason wrong |
| `new_vector` `1e7a` | a write in a loop | no loop; `1e84`-`1e88` call the 3-cell allocator and then write three times. Half met; it gave the next test |

The test that carries the rule: **after a call of the N-cell allocator
(section 10's words for N = 3..6), the writes on the fall-through path
fill exactly cells 0..N-1 of the new record.** `mekbn.fill_after_alloc`
follows each of the 77 call sites with the rules of section 16 and
keeps those where it can name the address of a write:

| Call | N | Cells written, in order |
|---|---|---|
| `30f3` | 6 | 0, 1, 2, 3, 4, 5 |
| `312b` | 6 | 0, 1, 2, 3, 4, 5 |
| `311d` | 5 | 0, 1, 2, 3, 4 |
| `1b4a` | 3 | 0, 1, 2 |
| `1d3a` | 4 | 2, 0, 1 (cell 3 is written elsewhere, section 17) |
| `1f99` | 4 | 0, then the path leaves what the tracer models |

None of the four complete ones was looked at before the rule was
fixed; `1d3a` is the routine the pass was after. All four load the
address register straight from the register that holds the new record
(`SD1` = 6 or 7), so they test the strobes and the stepping, **not**
the base-plus-constant addressing that `1d3a` uses (section 16). The other 71 sites
compute the address in ways the tracer does not model, so this is 4 of
4 where it could be checked, not 4 of 77.

**Step (bit 60).** Fit: `1e86`-`1e88` (write, write, write with the
bit on the first two). Predictions: the table above (N strobes and N-1
steps give N distinct cells); and a word that jumps to itself and
accesses memory must move its address. All 23 self-jumping words of
image 2 have a strobe; 19 have bit 60, and the other four (`208b`,
`3e59`, `4d17`, `6368`) reload the address register from a register the
same word updates. In `syspsi` 36 of 37 have a strobe and all 36 have
bit 60 (bit 60 is in 51% of its strobe words).

**The strobes together.** Predicted: bits 61 and 62 are rarely set
together. Image 2: 40 words, where chance gives 287. **`syspsi`: 512
words, where chance gives 367: the prediction failed there.** They are
`CCF` values `19`, `1d`, `1f` (132, 130, 181 words) spread over twenty
pages. Not explained; a read-modify-write or a KL0-only operation
(the trail) are guesses. Nothing below depends on it, but it means the
five bits are not fully independent.

**What the second pass's failed prediction was.** `3454`-`3455`, one of
the `read_*` tails it counted as "a read that has bit 62", is
`[..] <- MDR; R19 <- XR; [MAR1] <- MDR1`: the head of the one-cell
free list takes a new value in a word that writes. That is the push of
`collect_value` again. INFERENCE: reading an element through a
singly-referenced pointer frees the cell it was reached through (MRB
reclamation), and that is why reading routines write. `vector_element`
(17 words with the bit) was not re-read.

**`19`, `1a`, `1b` are free-list heads** (DERIVED; closes the conflict
in section 10). A pop is "read at the head, head := the data"
(`31f9`-`31fa`, `3349`-`334e`); a push is "data := old head, write at
the cell, head := the cell's address" (`3000`-`3001`, `38c0`-`38c1`,
`3454`-`3455`, and `proceed`'s first two words, section 18). The link
in a free cell is stamped `VECT0x` (`3000`, `216c`).

## 16. Registers, ports and timing

**The phase-2 registers, as `SD1` and bits 36..34 number them:**

| Number | Register | Evidence |
|---|---|---|
| 1 | XR | below, "one word later" |
| 4 | MDR1 | the enable rule |
| 5 | MDR2 | the enable rule |
| 6 | MAR1 | the port rule |
| 7 | MAR2 | the port rule |

`SD2` = 1 loads a second operand register, called YR here; `SD2` = 2
and 3 obey the enable rule as MDR1 and MDR2 do. The names are TR-564's
(XR/YR, MAR1/2, MDR1/2); which physical register is which is not the
claim, only that there are two data and two address registers and that
the numbers pair up as shown.

**The enable rule (MEASURED, both images).** In a word without a
strobe, bit 58 is set whenever MDR1 is named and bit 59 whenever MDR2
is:

| Use | Image 2: bit missing | `syspsi` |
|---|---|---|
| `SD1` = 4, bit 58 | 0 of 833 | 8 of 1,053 |
| bits 36..34 = 4, bit 58 | 0 of 918 | 12 of 1,142 |
| `SD2` = 2, bit 58 | 0 of 355 | 10 of 607 |
| `SD1` = 5, bit 59 | 0 of 327 | 0 of 466 |
| bits 36..34 = 5, bit 59 | 1 of 483 | 15 of 967 |
| `SD2` = 3, bit 59 | 0 of 300 | 0 of 390 |
| `AS2` = 2, neither bit | 3 of 3,541 | 43 of 4,505 |

So `AS2` = 2 is "the MDR", and which one is said by bits 59..58. This
is what makes registers 4 and 5 a pair and what the two low `CCF` bits
are for outside memory accesses. (The converse does not hold: 518 of
the 6,251 strobe-free words with a low bit set name neither register
in any field examined.)

**Bits 36..34 are the ALU's destination** (VERIFIED). Fit: `set_nil`
(`3189`: bits 36..34 = 4 with a tag immediate, then a write of that
constant) and `add` (`3a68`: bits 36..34 = 1, and the next word passes
XR to the destination register). Prediction: a word with 6 there is
followed by a strobe on MAR1, with 7 by a strobe on MAR2 (next
paragraph). Bits 31..29, the figure's "ALU output", then say what the
ALU passes. 4 = XR is VERIFIED ("one word later", below). **5 = XR +
YR is not VERIFIED**: it was fitted on `1d3a` itself and no routine
with an independently known layout was found that uses it (looked for:
a `VDESC` pointer made as "descriptor + 3", a vector size read at
"+ 1"; neither is formed this way). What supports it: the constants
are never above 15 in 133 uses; a constant of 13, 14 or 15 is never
followed by a stepping access (0 of 27 uses), as an offset near the
end of a 16-cell record would not be; the same field lands at +2 on
two paths of section 17; and three routines carry 12 just before
they write the `COD` cell (section 18), two of them by other address
forms. 1 = YR is DERIVED from two words. The other values, and 4
together with `AS2`, are not understood.

**The port rule: in a strobe word bit 58 selects MAR2, else MAR1**
(VERIFIED). Fit: `3320`-`3321` (`SD1` = 6, then a read with bit 58
clear). Prediction, word before the strobe against bit 58 of the
strobe word:

| Word before | Image 2: bit 58 clear / set | `syspsi` |
|---|---|---|
| loads 6 through `SD1` | 188 / 10 | 244 / 33 |
| loads 7 through `SD1` | 26 / 67 | 48 / 125 |
| ALU destination 6 | 946 / 32 | 441 / 41 |
| ALU destination 7 | 23 / 117 | 52 / 255 |

**For a read, bit 59 selects the MDR the data arrive in** (VERIFIED).
Fit: four pops (`31f9`, `31d4` without the bit, `3349`, `332b` with
it). Prediction: the next word, if it has no strobe and uses `AS2` = 2
with exactly one low bit, names that MDR: 320 and 136 right against 22
and 15 wrong in image 2, 238 and 140 against 28 and 8 in `syspsi`.
This is why the one-cell allocator can load `UNDF` into MDR1 in the
word that reads the link (`3321`): the link goes to MDR2.

**For a write, the data register when bit 59 is set is NOT settled.**
With the bit clear the data are MDR1's: where the word before loaded
exactly one of the two, it was MDR1 in 397 of 419 (image 2) and 147 of
168 (`syspsi`). With the bit set the same count gives MDR2 in 50 of
100 and 75 of 222. Six writes whose data are known from semantics
(`31d7`, `38c1`, `3001` with the bit, `318f`, `3322`, `318c` without)
fit "bit 59 = MDR2", and `enqueue_goal`'s `4c05`-`4c06` do not seem to.
`--rtl` prints such a write with a question mark. Scratch counts for
this paragraph, not pinned.

**One word later** (VERIFIED). A register loaded in one word is seen by
the next word, not by its own. Fit: `1d20`-`1d21` and `3a68`-`3a69`.
Prediction: a word that names no ALU input and passes XR follows a
word with `SD1` = 1: 420 of 487 (`SD1` = 1 is in 13% of words), in
`syspsi` 245 of 341.

**A write stores the MDR as it stood before its own word** (VERIFIED,
on less than the others). Fit: `set_variable` (`318b`-`318f`: `UNDF`
is made in the first word, the reference is loaded into MDR1 in the
second, which writes, and the third writes again; the cell gets `UNDF`
and the argument the reference only on this timing). Predictions: a
word that loads MDR1 through `SD1` is followed by a write in 393 of
628 (17% of words have a write), `syspsi` 258 of 721; and `new_vector`
`1e86`-`1e88`, which loads `{INTo, size}` once and writes three times,
then writes that value **twice, after one other cell**, which is the
descriptor `kbnheap.kl1` lays out (`{VDESC, ..}`, `{INT, n}`,
`{INT, n}`; `pimm_semantics.md`). With the data taken from the same
word it would be three integers. A count that does tell the two
timings apart: in a run of two or more consecutive writes of MDR1, a
load of MDR1 in the *last* word is useless on this timing and
necessary on the other. Image 2 has 181 such runs; MDR1 is loaded in
196 of the 357 words before the last (55%) and in 17 of the 181 last
words (9%). `syspsi`: 62 runs, 54 of 124 (44%) against 4 of 62 (6%).
(`1e86`-`1e88` is also the fit for bit 60, so it is not an independent
prediction for both.)

**Bits 17..16** (VERIFIED for 1). 1 stamps the tag immediate (EM bits
15..10) on what `SD1` loads: 396 of the 397 words with the value have
an `SD1` load (30% of all words do), 460 of 461 in `syspsi`. 2 stamps
it on the ALU result (DERIVED: `put_nil`, `set_nil`, `1d40`). 3 not
understood.

**Bit 57 makes `DST`, `SC1` and `SC2` name a second register file**
(VERIFIED as a qualifier, INFERENCE as to which file). It is set in
6,318 words of image 2 and 6,148 of `syspsi` and never in a word
without a register select; never with `SC1` = 8..`b` (the operand
selects of section 10); with it `DST` is `10`-`1f` in 3,266 of 3,373
words. Written `W1c` against `R1c` below. INFERENCE: it is TM-858's
40-bit by 32-word work register file. Fit: the allocators leave their
result in `W1c` and the callers read `W1c`.

**`SC2` = 8 and 9 are the immediates EM1 and EM2** (VERIFIED). Fit:
the refill entries of the one- and two-cell lists (`3376`-`337e`:
`SC2` = 8 with EM1 = 1 beside register `19`, EM1 = 2 beside `1a`).
Prediction: a word cannot use the same EM bits twice, so `SC2` = 8
excludes `JMPF` 5 and `SC2` = 9 excludes `JMPF` 3, 5, 6, 7:

| | Image 2 | Expected by chance | `syspsi` |
|---|---|---|---|
| `SC2` = 8 with `JMPF` 5 | 0 of 718 | 83 | 0 of 1,339 |
| `SC2` = 9 with `JMPF` 3, 5, 6, 7 | 0 of 211 | 47 | 0 of 426 |
| `SC2` = `b` with any `JMPF` | 0 of 704 | 390 | 0 of 747 |

What the table leaves out, so that the record shows it: `SC2` = 8 or 9
occurs with `JMPF` 1 in 33 words of image 2 and 69 of `syspsi`, and
**every one is an end or a return, none a jump** (58% of `JMPF` 1
words are jumps, which carry address bits in EM); and `SC2` = 9 occurs
with `JMPF` 2 in 3 words of image 2 (`0105`, `0107`, `2401`; about 6
expected, so `JMPF` 2 is not excluded, and those three words use EM
bits 9..4 both as the immediate 1 and in the target).

`SC2` = `b` is therefore a wider immediate (its layout was not read);
`a`, `c`, `d`, `e` look like immediates of other shapes and were not
read either.

**Base plus constant.** "XR := a register, YR := an immediate" and then
"MAR1 := XR + YR" occurs 133 times in image 2. **The constant is never
above 15**, though the field holds 63. That is the size of the largest
fixed record (section 18).

## 17. The multiple-suspension record (DERIVED)

Rules used: sections 15 and 16. Two of them are not VERIFIED, and the
table depends on them as follows:

- **Which tagged value is written, in what sequence, and that "next"
  is the cell after "prev"** stand on VERIFIED rules (strobes, stepping,
  MDR1 through `SD1`, the stamp, the write timing).
- **The cell numbers 0, 2 and 3** stand on "5 = XR + YR", which is
  fitted on this routine and supported, not VERIFIED (section 16). If
  that rule is wrong, what is recovered is the set of four fields and
  the adjacency of two of them, not the order.
- The write at `1d61` stands on "bit 59 = MDR2" for a write, which is
  not settled.

`mekbn.py --records` prints the writes; `--rtl 1d20 90` the code.

Context (DERIVED from `1c60`-`1c65` and `1d20`-`1d39`): the code is a
loop over the variables the goal is waiting on. For each it has the
variable cell's address in `W16`, the cell's present content in `W14`,
and `{HOOKo, goal record}` in `W11` (copied from `W15`, section 18).
`1d3a` allocates four cells; `W17` becomes `{MHOOK, record}`.

| Cell | Written at | Content | Console name (INFERENCE) |
|---|---|---|---|
| 0 | `1d3e` | `{DREF, address of the variable cell}` | prev |
| 1 | `1d60` (`1d64` for the third group) | `{ATOMo, R06}` (rows `1d50`-`1d52`), `{HOOKx, W14}` (rows `1d53`-`1d55`, by `1d62`), `{MHOOK, W14}` (rows `1d56`-`1d58`, by `1d63`), `{RHOOKo, W14}` (rows `1d59`-`1d5a`, by `1d65`) | next |
| 2 | `1d3d` | `{HOOKo, goal record}` | goal |
| 3 | `1d2f`, `1d39` | `{MHOOK, the next record made for the same goal}`; `1d39` closes the ring by writing the first record (`W12`) into the last one's cell 3 | rival |

Then `1d61` writes the variable cell itself (`W16`): `{tag, record}`
with the tag the row chose (`MHOOK`, `EMHOKo` or `EMHOKx`). This is the
write whose data register rests on the unsettled rule; the other
candidate, MDR1, holds the value just written to cell 1, which makes
no sense in a variable cell.

So, DERIVED under the caveat above: **the record is four cells in the
order the console's inspector lists them, prev / next / goal / rival**
(the names are the console's, matched by position and by what the
cells hold; that match is INFERENCE, the cell contents are not). The
agreement of the derived order with the console's order was not used
to choose the rule, and is the best single piece of support the
"XR + YR" reading has. The record sits in a
doubly-linked chain of the waiters on one variable, headed by the
variable cell (cells 0 and 1), points at its goal with a `HOOK`
pointer (cell 2), and is on a ring of all the records made for the
same goal (cell 3). The ring is how a goal woken through one variable
can be taken off the others: that use is INFERENCE, the code that
walks it (`2d46`-`2ef8`) was not read.

On the `1d63` path (the variable already held `{MHOOK, a record}`)
`1d64` also sets MAR1 from that old content and `1d60` then writes
`{MHOOK, new record}` there. The address is formed by an ALU
combination the tracer does not model (YR, holding 0, with the MDR), so
INFERENCE: it is cell 0 of the old record, whose "prev" becomes the new
record, as a doubly-linked insertion at the head needs.

A second path, `1d71`-`1d77`, adds a goal to a record that exists: it
writes `{HOOKo, goal}` at `W17` + 2 again, which is the independent
agreement on "cell 2 is the goal".

Not read: which tag of the variable's old content selects which row
(the rows are entered through `1d3f`-`1d40`, a dispatch on a tag whose
mechanism is not understood; INFERENCE that the tag is `W14`'s); what
`R06` holds (`{ATOMo, R06}` is written where a nil would stand, here
and in section 18, so INFERENCE: zero); cell 1's content on the
`1d63` path beyond the tag; `1d66`-`1d6a` and `1d6b`-`1d70`, the rows
for `EXMRF` and for a plain `HOOKo` content.

## 18. The goal record, and what `suspend`, `enqueue_goal` and `proceed` do with it

**A goal record comes from the register `1b` free list, a `HOOK`
pointer addresses its first cell, and it is written through cell 15**
(DERIVED; the cell numbers again rest on "5 = XR + YR", section 16).
That it is exactly 16 cells is INFERENCE: nothing was seen written
past +15 of a `HOOK` record, but the bound is not general, because
`create_shoen` (`1702`-`1715`) writes cells 8 to 23 of another kind of
record.

- `suspend` (`1c08`) calls `1c1d`, which pops the `1b` list through
  the `HOOKo` entry (`3349`); `1c09` puts the result in `R10` and
  takes the old `R10` as an address; `1c0a` makes `W15` :=
  `{HOOKo, old R10}`. So `R10` holds a goal record kept ready, the
  suspended goal goes into that one, and a fresh one replaces it.
  This is TM-862's "base of a frame representing a goal, the execution
  of which is postponed" (`literature_gaps.md` Appendix C 2.4).
- `1c31`-`1c32` set the address to `W15` + 12, and four writes follow
  (`1c0d`-`1c10`, three stepping): cells 12, 13, 14, 15. The same "+12,
  then four writes" is in the routine that makes a goal for a built-in
  that has to wait (`3d6a`, called from `new_vector`, `1e69`): `3d6f`
  sets MAR1 in a word that carries the immediate 12 (in a form the
  tracer does not model) and `3d70`-`3d73` are four writes, three
  stepping; `1d73` writes at +15 of such a record.
- The words `1c30` and `1c35` (section 11) are `MDR1 := R0c; write,
  step`: the copy of the argument registers into the record, starting
  at the address loaded at `1c09`, the record's first cell.

The table is for one path only: `1c2c` returning through `1c32` (the
other returns, `1c3d` and `1c52`, leave the address elsewhere and were
not followed) and `1c0d`, `1c0e`, `1c0f` each falling through (each
has a conditional exit: to `1c21`, `1c18`, `1c12`).

| Cell | `suspend` writes (`1c0d`-`1c10`), on that path | Label |
|---|---|---|
| 0.. | the argument registers, by the counted loop | DERIVED for "from cell 0"; which argument is first, and how many fit, not read |
| 12 | `{COD, the instruction's operand}`, made at `1c08` | DERIVED. INFERENCE: the operand is the label, so this is the predicate's code address |
| 13 | `R12` | DERIVED; what `R12` holds is not known |
| 14 | `R13` | DERIVED. `1c12` stamps `FPREC` on `R13`, so INFERENCE: the goal's parent (foster-parent record) |
| 15 | a value made at `1c0f` that the tracer cannot name | not recovered |

`enqueue_goal` (`4c00`) agrees where it can be read, and uses the
other port:

- `4c03` stamps `COD` and sets MAR2 in a word that carries the
  immediate 12 (again in a form the tracer does not model); `4c04`-
  `4c07` are four writes through MAR2, three stepping (pinned as
  `enqueue_trailer`). The registers loaded for them, in order, are
  `{COD, W10}`, `R12`, `R13`, `R14`: the same trailer.
- `4c05`: `R10 := {HOOKo, XR}` with XR loaded from `R1b` the word
  before, and `4c04`: `R1b := the MDR`. A fresh record replaces `R10`
  again.
- `4c06`: `R14 := {HOOKo, f(old R10)}`, the record just filled (f is
  an ALU operation, `AL` = 1, that was not identified), and the last
  value loaded for the trailer is the old `R14`.

INFERENCE, not DERIVED: **cell 15 is the link, and `R14` is the head
of a list of goal records linked through cell 15, newest first.** It
rests on three steps that are each weaker than the rules of section
16: MAR2 is set at `4c03` in a form the tracer does not model, so
"these four writes are cells 12-15" is by the immediate 12 and the
agreement with `suspend`; the data are paired to the cells by the
order of the loads, and two of the four writes (`4c05`, `4c06`) have
bit 59 clear after an MDR2 load, against the reading of bit 59 that
fits elsewhere; and `R14`'s new value passes through an unidentified
ALU operation. If it holds, the newest goal of a priority runs first,
which is what the reference model does by choice
(`pimm_semantics.md`); this pass does not establish it.

`proceed` (`216c`): the first two words are a push on the `1b` list
(data `{VECT0x, old R1b}`, a write, `R1b` := the address) and `216e`
is `R10 := f(R14)` with the same unidentified `AL` = 1. DERIVED for
those transfers; INFERENCE: it frees the
record of the goal that has finished and takes the head of the `R14`
list as the next one. The rest of `proceed` (the branches at `216e`,
`216f`, the calls of `3349` at `2175` and `218a`) was not read.

**Not recovered:** where the arity and the priority are (candidates:
`R12`, and whatever cell 15 gets in `suspend`); the extension that
`suspend`'s size tables allocate (`1c3a`-`1c5f`, with `VECTo` and
`VDESC` stamps at `1c48`, `1c4d`: INFERENCE, a vector for arguments
that do not fit); **how the Goal Stack Entry Table is used** (no word
that forms an address from `B800` or shifts by `18` was looked for);
whether `R14` is one stack or the current priority's.

## 19. Fault injections into the third-pass checks (observed)

Each was made on a scratch copy of `mekbn.py` by setting the named
constant and running `measure()` against `PINNED`; each FAILed as
listed.

| Injection | Observed failures |
|---|---|
| `RD_BIT=60` | read followed by an MDR use 206 of 755 (`syspsi` 475 of 1,556); enable rule broken in up to 176 words; `read_port` (22, 21, 2, 1); `new_vector_descriptor` loses its second integer |
| `MEM_BIT=61` | the second pass's `register_only_writes` and `writers_missing_bit`; MDR1 load followed by a write 26 of 628; every `fill_after_alloc` site and every record lost |
| `INC_BIT=63` | no loop steps (0 of 23, 0 of 36); the fill sites write cell 0 N times; the suspension record's cell 1 and the trailer's cells 13-15 collapse |
| bits 58 and 59 swapped | enable rule broken in 657 of 833 and five more rows; `read_port` (317, 105, 18, 53); `alu_dst_port` (732, 246, 71, 69); `1d61` loses its address |
| `WRB_BIT=56` | 5 words with `SC1` = 8..`b`; no fill site found; every record names `R` registers |
| `MDR1=5, MDR2=4` | enable rule broken in four rows; MDR1 load followed by a write 77 of 196; every record's data unknown or exchanged |
| `MAR1=7, MAR2=6` | both port tables reversed; `base_plus_constant` (3, 52); every address unknown |
| `WRITE_SAME_WORD=True` | **records only**: cell 2 of the suspension record gets `DREF`, the trailer shifts by one, the descriptor becomes three integers. No statistic changes: the constant only steers the tracer. The count that argues the timing is `write_runs` (section 16), which does not depend on the constant |
| `SC2_EM1=9, SC2_EM2=8` | exclusions 182 of 718 and 368 of 1,339; largest constant 59; the suspension record's cells become 0, 10, 11 |
| `SRC_SUM=1, SRC_YR=5` | one base-plus-constant left (with constant 49); `1d3a` and all `+constant` addresses lost |
| `XR=2` | XR pass 0 of 487 and 0 of 341; addresses lost |
| `SRC_XR=3` | XR pass 0 of 0; `{MHOOK, record}` values lost |
| `AS2_MDR=3, AS2_MAR=2` | read followed by an MDR use 49 of 1,386; `AS2` with neither low bit 450 of 820 |

## 20. Dead ends, not checked, and the next step

Dead ends and things that misled:

- **Bits 59..58 as one two-bit code.** Tabulating the four values
  against neighbouring loads gave nothing clean, because the bits mean
  one thing in a strobe word and another outside it. Splitting on
  "has a strobe" is what separated them.
- **Reading bits 31..29 as the ALU's destination** (the figure's
  label). The first tracer treated "= 5" as "into MAR1"; the strobe
  that follows depends on bits 36..34 instead (946 against 32).
- **Lift tables of "field value in one word, field value in the
  next"** across `SD1`, bits 36..34, 31..29 and `AS2`. Suggestive at
  best (lifts of 2-5); the 0%/100% tables above came only after
  conditioning on the strobe.
- **A size sweep of `new_vector`** (N writes for size N). The routine
  is not laid out one case per size.
- **Bit 59 as the data select of a write.** Section 16: fits image 2
  weakly, fails in `syspsi`.
- The prediction "a `wait` on an unbound variable pushes on the
  suspension stack with one write" matched the count and was wrong
  about what the write is.

Not checked:

- `x18` (bit 18). `write_*` differ from `set_*` by bit 18 and EM1 =
  `20`, which must be "advance the structure pointer", and the counted
  loops carry bit 18 with EM1 = `10`: one field, at least two uses.
- Every value of bits 31..29 except 1, 4, 5; `AS2` = 1; `SD1` = 2, 3;
  bits 17..16 = 3; bit 63 (57 words); the condition codes; the
  dispatch that enters the tables at `1d50` and `3440`.
- The `syspsi` words with both strobes.
- `vector_element`, page `2c00`-`2eff` (resumption), `execute`,
  `try_me_else`, the rest of `proceed` and `enqueue_goal`, the
  allocators for three cells and more (`3331`-`3347`: they keep their
  heads in memory, through `R05`, and were only partly followed).
- The tracer (`mekbn.Walk`) models the constructs named in section 16
  and nothing else; an address or value it cannot name is printed `?`,
  and it follows only the path it is given.

State: the goal of this pass is met for the memory datapath; met for
the multiple-suspension record's fields and tags, with the cell order
conditional on the unverified "XR + YR" rule; met in part for the goal
record (pointer, cells 12-14 on one path of `suspend`); inference only
for its size, link and the ready list; not met for arity, priority and
the Goal Stack Entry Table. The approaches are not exhausted.

Most useful next step: first verify "5 = XR + YR" on held-out code
with a layout known from elsewhere, since two record layouts hang on
it (candidates: the list cell's cdr at +1 in `merge` `3e54` or the
`get_list` rows, the string descriptor, the 14 fields of the
foster-parent record against `create_shoen`'s run at `1702`). Then
read `proceed` from `216e` and page `2c00` with
`--rtl`, after settling two small things it will trip on: what a
bit-59 write stores (take the 100 image-2 words with an unambiguous
load before them and look at the 50 that disagree), and bit 18 with
its EM1 codes (minimal pair: `set_value` `3187` against `write_value`
`31c9`, and the loop at `1c30`). `proceed` must read the next goal's
priority and code from the record, which names `R12` and cell 15, and
it is the place the Goal Stack Entry Table has to appear if this
firmware uses it per priority.
