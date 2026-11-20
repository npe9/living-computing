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
it stands. Section 13 says what is still not known: **the goal record
layout was not recovered.**

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
is not shown to be "write".**

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
  above.

## 11. Goal records, suspension, the ready structure: what the code shows

None of the three layouts was recovered. What follows is the part that
stands on sections 8-10, and then what is only suggestive.

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

Most useful next step: settle the memory datapath on the two smallest
routines that read and write through a known pointer, the one-cell
allocator (`3320`-`3324`: take the head of a free list, replace it by
the cell's link) and `write_variable`/`set_variable` (`318b`, `3195`:
write `UNDF`, make a `REFo` to it). Their semantics fix which of
`SC1`/`SD1`/`AS1`/`AS2`/`AD` carry the address, the data read and the
data written, and the `19` conflict of section 10 has to come out of
the same reading. With that, `1d3a`-`1d40` (five words) gives the
multiple-suspension record's field order directly, and `1c08`-`1c3d`
the suspended goal record's header.
