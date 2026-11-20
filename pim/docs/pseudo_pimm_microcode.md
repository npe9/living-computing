# The Pseudo PIM/m microprogram: layout of `pimm.MEkbn`

Continues `pseudo_pimm_firmware.md` section 3 ("Not read"). Looked at
2026-11-20, time-boxed. Everything describes the Pseudo PIM/m (PIM/m KL1
firmware on a PSI-III), not a PIM/m processing element.

`asm/mekbn.py` reads the file; `asm/mekbn.py --check` pins every number
marked MEASURED below and is in `run_tests.sh`. Statements are
labelled MEASURED (a number from the tool), or INFERENCE.

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
- What the 6-bit immediate is in general. It is a tag in every anchor
  above, but its distribution over all page-relative branches (value 0:
  552, `10`: 326, `01`: 182) says it is also used for other constants.
- The meaning of `CNDF` (bits 22..19) values.
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
2. The register-select fields: test the figure's `DSTF`/`SC1F`/`SC2F`
   positions against the register-operand families (`set_atom`,
   `put_atom` take the register from the opcode's low bits).
3. The other 16 bits of each decode word.
4. Add `asm/mekbn.py --check` to `run_tests.sh`.
