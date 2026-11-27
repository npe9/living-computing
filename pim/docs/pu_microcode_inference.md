# PSI-III / PIM/m PE microcode: static inference

The static and inference side of reconstructing the PE microcode, to
feed the Python simulator in `ref/pu/` (`docs/pu_microcode_plan.md` is
that agent's plan; this document does not change it). The held
firmware is third-party and stays out of git: the tools read it from
the same place `asm/mekbn.py` does.

Tools (all in `asm/`; every number below is pinned by their `--check`):

| tool | what it does | `--check` time |
|---|---|---|
| `pu_store.py` | a cached loader: syspsi, image 2, sysinit, sysidat, the KL1 control store (image 2 + syspsi 0x6800 and above), decode roots | n/a |
| `pu_cfg.py` | the sequencer rules S1-S13, whole-firmware CFGs, fan-in, loops, multiways, repeats, cross-image evidence | ~1 s |
| `pu_sysinit.py` | sysinit's block map, the three TGT images, the KL1 TGT column check, the mnemonic table, pointer tests | ~1 s |
| `pu_smt.py` | CEGIS field inference over SMT-LIB2 with the z3 binary (a subprocess; nothing installed) | ~30 s |

Labels: DOCUMENTED (a primary source says so), CORROBORATED (two
independent readings agree), INFERRED (our reading, not contradicted),
MEASURED (a count over the held words), EXECUTED (run symbolically),
VERIFIED (a test that would fail if the claim were false), UNKNOWN.
Field names follow Nakashima's thesis Fig. 3-25 as `mekbn.FIELDS`
does. TR-733 fig. 4 is kept as the competing layout (section 6).

## 1. Summary

* **Sequencer.** Two new multiway kinds: 4-bit JMPF 3 is the thesis's
  `case_branch` (rule S8), and a JMPF 1 jump with EM bit 2 set is a
  second multiway (S2b). JMPF 1 with EM = 7fff is a special form, not an
  address (S9). These three account for the "jumps into nowhere" that
  earlier readings counted.
* **CFGs.** About 54% of the non-zero words of both configurations are
  reachable from decode roots by static rules alone: 12591 / 23556 for
  KL1, 14738 / 24414 for KL0. The rest are reached through computed
  transfers and decode start-address variants, which are not yet modelled.
* **The "15 jumps into upper syspsi from image 2" are real shared
  firmware.** syspsi 0x6800-0x7fff stays resident under image 2 and is
  common code: the trap vectors, the illegal-instruction stub 6c21
  (called 244 times from image 2), the page dispatch, and a fixed-
  address interface back down into image 2 at 0x6000-0x6430. After the
  misreadings are removed (14 S9 specials and one date word), image 2
  references 24 distinct upper bases from 333 sites. 23 of the 24 are
  non-zero code in syspsi, and the 24th needs no word of its own.
* **sysinit** is an initialisation image (load 0x5000, 8286 words). It
  holds init microcode, three 64-tag x 8-byte TGT images, exception and
  console text, a 1024-entry mnemonic table, a copy of the decode table
  equal to sysidat, and a little microcode at 0x7000. Column 2 of the
  KL1 TGT (0x5300) is VERIFIED against six image-2 multiway sites.
  No region is a table of addresses into the get_* routines: dispatch
  uses TGT byte offsets, not pointers.
* **SMT.**
  * The CEGIS harness eliminates TR-733 fig. 4 in favour of the thesis
    layout, conditional on the allocator contract.
  * It independently confirms mekbn's memory and stamp rules.
  * It finds that a conditional end tests the condition the previous
    word formed. The timing of conditional jumps is still open.
  * It fixes CNDF 5 = eq and CNDF 7 / EM1 0a = lt, up to one global
    polarity.

## 2. Sequencer (`pu_cfg.py`)

### 2.1 Rules

| rule | meaning | label |
|---|---|---|
| S1 | JMPF 0 / 8: next = a + 1 | VERIFIED (mekbn s.8) |
| S2 | JMPF 1, EM bit 3: jump to (EM & 0x7ff0) \| CNDF | VERIFIED (mekbn s.8) |
| S2b | JMPF 1 jump with EM bit 2: multiway, low target bits ORed in at run time | INFERRED; alignment MEASURED |
| S3 | JMPF 1, EM bits 3, 2 clear: end of instruction (next = decode) | VERIFIED |
| S4 | JMPF 1, EM bit 2 (no bit 3): return | VERIFIED; MSTK DOCUMENTED (thesis p.126) |
| S5 | JMPF 1, EM bit 1: S2-S4 conditional; EM bit 0 the polarity | VERIFIED; polarity EXECUTED (section 6) |
| S6 | JMPF 4: a + signed EM bits 3..0 | VERIFIED |
| S7 | JMPF 5: call absolute; 7 / f: call page-relative; 6 / e / b: page jump; a: page branch | VERIFIED. **Open conflict (U2 sixth session):** rassy's `jmpf/9` names b 'call' (long, 'if cond'), as f, and a / e 'goto' long 'if cond' / 'if not cond'; the twin words `0c0c` (JMPF b) and `0c0f` (JMPF 5, call) to `0c15` support b = conditional call; the polarities a, b 'if cond' and e 'if not cond' are adopted (`pu.CJUMP_TAKEN_ON`; HELD-SOURCE, the arms' relative pool operands resolved to slots `00af`-`00b6`). **Decided (U2 seventh session): b is a page-relative call taken if cond** (`pu.RULES['jmpf_b_call']`, INFERRED, kind HELD-SOURCE): taken at `0c0c` (`get_value`) it calls `0c15`, whose rows return to `0c0d`; the old jump reading stops at `0e72` on an empty micro stack. Census (image 2, words reachable from each target before a return or an end, calls taken as returning): 47 b targets, 38 reach only returns, 9 both, 0 only ends (JMPF 7: 144 / 42 / 4; JMPF 6: 338 / 185 / 510). `mekbn`'s `flow()` still reads b as a page jump (its pins are unchanged); `pu.py` overrides it |
| S8 | 4-bit JMPF 3: `case_branch`, base page \| EM 9..0, low 4 bits from the TGT byte a CNDF 7 set-up word selected | mechanism DOCUMENTED (thesis p.131); alignment MEASURED; one column VERIFIED. U2 seventh session: the whole byte where the base's low bits are free (`0e75`, base `0e60`, column 5's 0..19 on 20 rows; `pu.RULES['case_wide']`), the set-up may stand two words before across a JMPF 1 word (`0802`; `pu.RULES['tdar_holds']`), and every CNDF 7 EM1 `30`-`3f` is rassy's `case_tag_setup mdrN k`, column 7 - k (`pu.CASE_TAG_SETUP`; columns 0, 5, 6, 7 executed) |
| S9 | JMPF 1, EM = 7fff: computed / special form | INFERRED |
| S10 | 4-bit JMPF 2: `case_branch` with a short base, (a + signed EM3) \| TDAR (U2 2026-11-27, sixth session; `ref/pu/README.md` "U2") | INFERRED: kind HELD-SOURCE (rassy `jmpf/9` arm 2 'base' 'case_branch' with `short/3`, as arm 4); 15 of 16 bases 16-aligned (MEASURED); EXECUTED at `2447` |
| S11 | decode roots: KL1 from pimm.MEkbn classes 2/3, KL0 from sysidat classes 0/1 | MEASURED |
| S12 | 32-aligned decode entries are entered at each 4-word row by the tag multiway | INFERRED (thesis p.134; mekbn s.9). U2 sixth session: for ODPF 6 entries the row is match << 2 \| a 2-bit chain code, not a TGT column (`setup.S_OTHER_ROW`, EXECUTED for an operand held directly, row 4 at `3310`); the TGT byte (column 7 - TDPF) goes to TDAR for a later `case_branch` (`setup.S_TDAR`) |
| S13 | words 0..15 are entry vectors (reset, traps), equal in both firmwares | INFERRED |

### 2.2 The multiways

S8 is 4-bit JMPF 3, not JMPF 3 with bit 26 ignored: code 0xb is not
aligned.

* Target alignment. In image 2, 156 of 199 targets are 16-aligned. In
  syspsi it is 248 of 294. Other kinds land aligned at the chance rate
  of 1/16: 169 / 2259 and 268 / 4304.
* The set-up word. 108 of the JMPF 3 words in each firmware follow a
  CNDF 7, JMPF 0 word, whose EM1 holds the `case_tag_setup` parameter.

S2b is a JMPF 1 jump with EM bit 2 set.

* Alignment. With EM & 7 = 4, the targets are aligned in 245 of 254
  syspsi words and 34 of 37 image-2 words. EM & 7 = 5 aligns to 8.
* Examples: 4477 → 44c0, 1c3e → 1c40, and the page dispatch at
  6f02 / 6f04 / 6f06 → 6000 / 6400 / 6800.

### 2.3 Not addresses

* The S9 specials. Their apparent targets, 7ff0-7ffb, are 12
  DBGF-only filler words (`8000000000000000`). There are 49 S9 words in
  syspsi; 14 of image 2's were among the cross-image candidates.
* The date word. Image 2's word at 67ff, `000000022e111993`, is data
  (a date), not a jump to 6802.

## 3. CFG headline numbers

| | KL1 (image 2 + syspsi upper) | KL0 (syspsi) |
|---|---|---|
| non-zero words | 23556 | 24414 |
| roots (decode + rows + vectors) | 353 | 528 |
| reachable | 12591 | 14738 |
| unreachable words / runs | 10965 / 869 | 9676 / 907 |
| SCCs / largest / self-loops | 221 / 99 / 25 | 321 / 285 / 72 |
| upper (0x6800+) words reached | 1762 | 2962 |
| addresses with fan-in >= 10 | 127 | 124 |
| largest dead runs | 540a/358, 7487/303, 7893/228, 72dd/218 | 3cce/301, 59a0/247, 78ab/204, 2cd9/178 |
| top fan-in | 6c21 244, 0d87 66, 082b 53, 3331 52, 0d88 46, 4678 42 | 682c 155, 08c3 145, 6c05 64, 6c04 50, 6800 42, 5405 41 |

KL1 word kinds: seq 10779, jump 5902, call 3077, return 1606, end 829,
branch 711, case1 386, case 200, special 49, open 16, data 1.

Repeated 4-word sequences:

* image 2: 304 distinct, 760 occurrences (top 0886 x17, 0cc4 x17);
* syspsi: 514 distinct, 1356 occurrences;
* 100 sequences occur in both.

They are candidates for shared macro expansions: tag checks and the
allocator call-and-fill pattern.

The unreachable 46%. Static rules cannot reach it: it is entered by S9
computed transfers and by decode start-address modification (ODPF
variants). A heuristic that also roots every word in a decode entry's
32-word block whose predecessor cannot fall through would raise reach
to 13784 (KL1) and 16678 (KL0). That heuristic is NOT adopted: it
would hide the question rather than answer it. The simulator should
treat a transfer into these regions as expected, not as an error.

## 4. Cross-image verdict: real shared firmware

Image 2 reaches into syspsi 0x6800-0x7fff because that half of the
control store stays loaded under the KL1 program. Evidence (`pu_cfg.py
--cross`, all pinned):

1. **The references are code.** Image 2 references 24 distinct upper
   bases from 333 sites. 23 are non-zero words in syspsi. The one zero,
   7299, is a case1 base and needs no word of its own. 11 of the 24
   are also used by syspsi's own KL0 code, which references 94 upper
   targets from 638 sites.
2. **A vector table.** syspsi 6c00-6c25 is a table: each entry reads
   [MAR2++] and calls group handler 6c30 + 2k, which calls 6c7d with
   immediate k. Image 2 calls 6c21 244 times, in 185 "call 6c21"
   stubs, 66 of them standing alone: the trap for illegal or
   unimplemented instructions. Row e of the 1d50 table also goes to 6c21.
3. **Entry vectors.** Words 0x0000-0x000f are equal in both firmwares
   and call 6c08 / 6c0b / 7476.
4. **A fixed interface downward.** Upper syspsi jumps back into
   0x6000-0x6430: 11 targets from 81 sites. Five of these targets
   (6400, 6402, 6410, 6420, 6430) are zero in syspsi but non-zero in
   image 2, and 6400 / 6410 are clean routine starts there. The
   language firmware supplies these addresses.
5. **The page dispatch.** 6f02 / 6f04 / 6f06 → 6000 / 6400 / 6800.
6. **Misreadings removed.** These were the 14 S9 words (EM = 7fff) and
   the date word at 67ff. Neither is a jump.

Label: CORROBORATED, by points 1-5, which are independent. For the
simulator, the KL1 control store is `image 2 ++ syspsi[0x6800:]`
(`pu_store.Stores.kl1_wcs`).

## 5. sysinit (`pu_sysinit.py`)

Header (load 0x5000, count 8286, entry 0x5000). sysidat's header is
(0x6800, 1040, 0x5000).

| range | content | label |
|---|---|---|
| 5000-523f | init microcode: 39 calls, 38 internal, 1 to upper syspsi; 1 DBGF word | MEASURED |
| 5240-527f | ffff control words | MEASURED |
| 5280, 52c0, 5300 | three TGT images, 64 tags x 8 bytes | INFERRED; 5300 VERIFIED (below) |
| 5700-57bf, 6080-617f | message text, `ERROR_..._(system)`, 8 big-endian bytes per word | MEASURED |
| 5b80-5fbf | mnemonic table: a header, then 1024 entries; name i at 0x5b81 + i | CORROBORATED |
| 5fc0-603f | console text | MEASURED |
| 6800-6c0f | decode table, equal to sysidat in all 1040 words | MEASURED |
| 7000-705d | microcode | MEASURED |

* **The KL1 TGT (5300).** The thesis gives the TGT as 512 entries and
  `case_tag_setup k` as k = 0..7: 64 tags x 8 columns.
  * Column 3 over VECT0o..VECTo gives 6, 8, ..., 20.
  * Rows 0x20-0x23 (the PMI / BLT / GMI / KLB tags) are identical.
  * Column 2 classes: 0 UNDF, 1 EUNDFo, 2 EUNDFx, 3 HOOKo/x, 4 EHOOKo,
    5 EHOOKx, 6 MHOOK, 7 EMHOKo, 8 EMHOKx, 9 RHOOKo, 10 RHOOKx,
    11 EXREF / EXVAL, 12 EXMRF, 13 MGHOK, 14 every other tag (46).
  * VERIFIED at the image-2 multiway sites whose set-up has EM1 = 0x3a.
    At 1d40 → 1d50 the stamps follow the export attribute, and row e
    calls 6c21. Rows at 0221, 0263, 1d40, 2d3f, 2ed7 and 3c61 group the
    classes consistently, and 5300 column 2 is the best-fitting table
    at 5 of the 6 sites.
* **Open.**
  * The column chosen by the other EM1 values. The hypothesis "column =
    EM1 & 7" was tested and is not significant against a random-column
    null.
  * Which of 5280 / 52c0 is KL0's table. The o/x-pair test does not
    discriminate: 126 / 101 / 129 of 168.
* **The mnemonic table.** It matches 124 of 153 KL0 opcode names and
  179 of 205 KL1 names, by a subsequence test on the first three
  characters. A further 51 / 63 match with the index shifted by ±1
  (KL0), and 57 / 55 (KL1).
* **Pointer test.** Only the decode copy is enriched for KL0 start
  addresses: 227 hits against 5.5 expected. No block is enriched for
  KL1 get_* starts. **sysinit is not a table of routine addresses.**

## 5a. ESP (KL0) against KL1: the Rosetta comparison

The KL0 entry points come from sysidat, and their names from the
sysinit mnemonic table (section 5) and `psi/kl0_opcodes.tsv`.

| KL0 (syspsi) | KL1 (image 2) | comparison | label |
|---|---|---|---|
| ADD 0x140 at 1120 | add at 3a68 | `0c05830667382523` against `0c0583066738266c`: the same word apart from the jump target. The end words 1121 and 3a69 are identical (`00b0000080820003`) | MEASURED |
| SUB 0x141 at 1130 | subtract at 3a70 | the same first word apart from the target. KL0's end word 1131 has no TGIF = 2 INTo stamp | MEASURED |
| EQ 0x162 at 1000 | equal at 3a58 | both form CNDF 5 on MDR1 - MDR2 (AS1F 4, AS2F 3, ALF 1), then a conditional end with EM bits 1..0 = 2 | MEASURED; meaning EXECUTED (6.3) |
| LESST 0x166 at 1028, noLESST 0x167 at 1038 | less_than 3a48, not_less_than 3a50 | both use CNDF 7 with EM1 = 0x0a; polarity in EM bit 0 (1029 = 2 / 1039 = 3, as 3a49 / 3a51) | MEASURED |

* **Hardware.** What is shared is datapath and sequencer:
  * the ALU encoding (ALF 0 / 1, AS1F 4 / AS2F 3 = MDR1 / MDR2);
  * the condition codes (CNDF 5; CNDF 7 with EM1 selecting a rare
    condition);
  * the conditional-end encoding.

  The KL0 add, subtract and equal contracts hold under the same
  selectors as the KL1 ones (section 6), so these fields carry the
  same meaning in both firmwares. This is EXECUTED for the fields
  those words use.
* **Language convention.** What differs:
  * the result tag: KL0 SUB leaves the tag as the ALU passes it, and
    KL1 stamps INTo;
  * the entry layout: KL0 entries from sysidat classes 0/1, KL1 from
    pimm.MEkbn classes 2/3;
  * the free-list registers R19/1a/1b, used by KL1's allocators.
* **Not done.** The planned per-field distribution comparison between
  syspsi below 0x6800 and image 2 (to separate hardware fields from
  convention fields statistically) was not done. Neither was a check of
  the KL0 LESST path, which calls 1046 and returns from 1048 / 1049
  before the conditional end at 1029.

## 6. SMT field inference (`pu_smt.py`)

### 6.1 Method

Each unknown field value is a selector over a finite set of meanings:

* the work-register codes of SD1F / ADF (none, XR, YR, MDR1, MDR2,
  MAR1, MAR2) and of AS1F / AS2F (zero, or one of the six);
* ALF: add, sub, pass1, pass2;
* conditions per CNDF value, and per EM1 value when CNDF is 7: lt, le,
  eq, ne, gt, ge, never, always;
* the CCF bit roles: which of bits 58-62 is the read strobe, the write
  strobe, the increment, and the MAR / MDR / write-data select;
* the TGIF bit roles: stamp the SD1 load, stamp the ALU result, or
  nothing;
* four timing choices:
  * vis: does phase 2 see this word's phase-1 loads?
  * wtime: does a write store the MDR as it was before phase 1, or after?
  * ctime: does a transfer test the condition its own word forms, or
    the previous word's?
  * endpol: which value of EM bit 0 makes a conditional end end?
* the layout: thesis or TR-733.

Under TR-733 every ALU field value gets a selector of its own (`tr_*`),
so TR-733 is never forced into the thesis numbering.

The held routines are executed symbolically over SMT integers with
the contracts below. Memory is a set of symbolic cells plus a default.
The data range is ±2^20, so overflow never happens.

* **Synthesis.** Find selectors that satisfy every contract on the
  pool of concrete counterexamples.
* **Verification.** With those selectors fixed, look for symbolic data
  that breaks any contract; one z3 process runs one push/pop per
  contract.
* **Loop.** Add any counterexample to the pool and repeat.

For each value of each selector, the value survives if its CEGIS run
is SAT. For an eliminated value, `--table` also runs every contract
alone, to name the contracts that kill it on their own.

| contract | path | spec | label |
|---|---|---|---|
| alloc_1cell | img2 3320-3323 | R19 = p, mem[p].v = q ⇒ R19 = q, W1c = {REFo, p}, mem[p].tag = UNDF | INFERRED (mekbn s.17) |
| set_variable | img2 318b, 318c, 318f | R19 = MAR2 = h, MAR1 = s, mem[h].v = q ⇒ R19 = q, mem[h].tag = UNDF, mem[s] = {REFo, h}, opda = {REFo, h} | INFERRED (WAM; entry name) |
| write_variable | img2 3195, 3196, 3199 | the same, s from R02, operand 9 | INFERRED |
| add / subtract, KL1 and KL0 | 3a68-69, 3a70-71, 1120-21, 1130-31 | MDR1 = {INT, a}, MDR2 = {INT, b} ⇒ opdb = {INT, a ± b} (KL0 SUB: no tag claim); the first word's conditional jump is not taken, and the second word's conditional end ends | DOCUMENTED instruction; the operand placement INFERRED |
| less_than, not_less_than, equal, not_equal (KL1); equal (KL0) | 3a48-49, 3a50-51, 3a58-59, 3a60-61, 1000-01 | succeeds iff the relation holds, where success = the first word does not jump and the second word's conditional end ends | DOCUMENTED; the exits (R04 := R11, end) read as failure INFERRED |

### 6.2 Results

All 12 contracts are jointly satisfiable: 3 heap, 4 arithmetic and 5
comparisons. KL0 LESST / noLESST are not included, because their path
goes through a call (section 5a). Surviving meanings, with the
contracts that kill each other value on their own (`--table`):

| selector | survives | eliminated, and by |
|---|---|---|
| **layout** | **thesis** | tr733: only jointly; a minimal killing set is {alloc_1cell, write_variable} |
| vis | same, next | (undecided) |
| **wtime** | **old** | new: only jointly; it survives if alloc_1cell is dropped |
| **ctime** | **prev** | same: only jointly, and no single contract's removal saves it |
| endpol | both | coupled with the conditions, see 6.3 |
| rd | 59, 61 | 58 alloc; 60, 62 alloc, set_variable, write_variable |
| **wr** | **62** | 58 set_variable; 59, 61 set/write_variable; 60 all three |
| inc | none, 60 | 58, 59, 61 set_variable; 62 jointly |
| **marsel** | **58** | none, 59, 60 by set_variable (and write_variable) |
| **mdrsel** | **59** | none, 58, 60 jointly |
| wdsel | none, 59, 60 | 58 jointly |
| **tg1** (TGIF = 1) | **stamps the SD1 load** | none: alloc / set / write; ALU: set / write |
| **tg2** (TGIF = 2) | **stamps the ALU result** | none: alloc / set / write; S1: alloc / set |
| dstsrc | ALU | S1: seven contracts on their own |
| sd1_4 / sd1_6 | MDR1 / MAR1 | every other meaning, set / write_variable and alloc |
| sd1_1, sd1_5 | open (sd1_5 is not MAR1) | |
| th_adf_4 | MDR1 | jointly |
| th_adf_0 | none, XR, YR, MDR2, MAR2 | MDR1, MAR1: jointly |
| th_adf_1, th_adf_7 | open | |
| th_as1_4 / 5 / 6 | MDR1 / MDR2 / MAR1 | jointly |
| th_as1_1 | not zero | |
| th_as2_0 / th_as2_3 | zero / MDR2 | jointly |
| **th_alf_0 / th_alf_1** | **add / sub** | jointly |
| **cond_5** | **eq, ne** | lt, gt, never jointly; le, ge by equal / not_equal |
| **cond_7_0a** | **lt, ge** | eq by not_less_than; the rest jointly |
| cond_7_09 | never, always (coupled with endpol) | |
| cond_0, cond_b | open | |
| **cond_7_29** (side contract) | **mrb_on, mrb_off**; under endpol 'b0=0 ends if cond' **mrb_on** | every value relation, never and always by `reuse_kl1` alone |
| **ctime** (side contract `execute_fast`, CNDF 3 = lt) | **prev** | same by `execute_fast` alone |
| **cond_3** (side contract, ctime same) | **never** | every relation and always |
| **cond_7_19** (side contract, ctime prev) | **never** | every relation and always |

*Added 2026-11-27 (U2, fourth session):* the condition domain of
CNDF 7 EM1 `29` alone (`TAG_CONDS`) also offers `mrb_on` / `mrb_off`,
the MRB (tag bit 0) of the ALU result's tag (for a word that only
passes its AS1 input, that input's tag). The contract `reuse_kl1`
(`31ec`-`31ed`, `put_reused_structure`'s other row, MDR1 = LISTo or
LISTx): the second word ends (the cell reused in place) iff the MRB is
off (TR-466 4.2: a single-referenced input cons cell is reused). It is
decided on its own (`side_contracts`, `SIDE_PINNED`), not in the joint
set: offered to every condition or added to the joint set, it made
`--check` take 67-80 s instead of 17 s. Both rows are pinned by
`--check`. Injection (in-process): the contract flipped (ends iff the
MRB is ON) gives 1 FAIL, the fixed-polarity row (`['mrb_off']`).

*Added 2026-11-27 (U2, fifth session):* the side contract
`execute_fast` (`4cc0`-`4cc1`, `execute`'s first two words): with no
asynchronous event pending, `4cc1` (a conditional JMPF b to `4cc5`,
taken when the COND it tests holds) is not taken, whatever the
registers hold. It is decided with the datapath values already decided
held fixed (`EXEC_DECIDED`: thesis layout, AS1F 4 MDR1, AS2F 0 zero,
ALF 1 sub, SD1F 1 XR, SD2F 1 YR, ADF 0 none, AS2F 1 YR, AS1F 2 YR);
left free, ADF 0 = MDR1 lets `4cc1` compare R0d with itself and
`same` survives. Results (pinned): with CNDF 3 a relation on the ALU
result (lt), only **ctime prev** survives; under `same`, CNDF 3 must be
`never`; under `prev`, CNDF 7 EM1 `19` (the condition `4cc0` forms)
must be `never` for every register content, i.e. it does not depend on
the ALU result, as a hardware flag (slit_check, `ref/pu/pu.py`
`FLAG_CONDS`) that is clear. This is the first test of the timing of a
conditional JUMP (section 6.3 item 3 had it for ends only); it rests
on the INFERRED contract and on CNDF 3 being a data condition (rassy's
short table: carry, zero, sign, same_tag, equal, lc_one). Injections
(private copy, `--check`): `th_adf_0` left free gives 2 FAIL (ctime
['same', 'prev'], cond_3 ['lt', 'ne', 'gt', 'never']); the contract
flipped (4cc1 taken) gives 2 FAIL (cond_3 and cond_7_19 ['always']).

The table was computed before the arithmetic contracts gained their
end clause. Adding the clause can only remove meanings. After the
change, the cond_7_09 row was re-run, as were layout, wtime, ctime,
vis, rd, inc, wdsel, endpol, cond_5 and cond_7_0a, and every pinned
row; all are unchanged except cond_7_09. Bold rows are pinned by
`pu_smt.py --check` (about 30 s). The full
table is `--table`, about 9 minutes. The leave-one-out and minimal-set
runs were done by a scratch script.

### 6.3 What it decides

1. **TR-733 fig. 4 is eliminated; the thesis layout survives.**
   EXECUTED, but conditional on the INFERRED allocator contract.
   * No single contract kills TR-733, and it survives if alloc_1cell
     is dropped. {alloc_1cell, write_variable} is a minimal set that
     kills it.
   * This agrees with `psi_microword.md` section 7, which measured
     bit 26 as part of JMPF.
2. **The third-pass memory rules of `mekbn.py`.** EXECUTED, and
   independent of how mekbn found them:
   * write strobe bit 62;
   * MAR select bit 58;
   * read-data MDR select bit 59;
   * TGIF 1 stamps what SD1 loads, TGIF 2 stamps the ALU result;
   * a write stores the MDR as it stood before its word (mekbn's
     WRITE_SAME_WORD = False);
   * SD1F 4 MDR1 and 6 MAR1; AS1F 4 MDR1, 5 MDR2, 6 MAR1; AS2F 0 zero
     and 3 MDR2; ADF 4 MDR1;
   * ALF 0 add, 1 sub.

   The read strobe is 61 or 59. mekbn says 61; these contracts cannot
   separate it from 59, because every read in them also has bit 59 set.
3. **A conditional END tests the previous word's condition (ctime =
   prev).** NEW, EXECUTED for ends only.
   * A conditional end (JMPF 1 with EM bit 1) tests the condition the
     PREVIOUS word formed from its own ALU result, under that word's
     CNDF (and EM1 when CNDF is 7). The comparing word's own
     conditional jump (3a48 JMPF e) does NOT test that word's
     comparison.
   * This is forced by the shared first word: less_than and
     not_less_than begin with identical words, which differ only in
     the jump target. If the jump tested its own word's comparison,
     the two instructions would fail on the same inputs. The argument
     holds equally with the exits read the other way round.
   * **Scope.** No contract tests a conditional jump, branch or return
     positively: every jump on the paths is asserted not taken, and
     under "prev" that holds because the word before is assumed to ask
     for nothing. One selector covers ends and jumps alike, and the
     model lets every word form a condition. **The timing of
     conditional jumps, branches and returns is UNKNOWN.** The KL0
     LESST path is the place to test it: it calls 1046, compares and
     returns conditionally in one word at 1048, then 1049 returns, and
     1029 ends conditionally.
4. **Condition codes, up to one global polarity.** EXECUTED.
   * CNDF 5 is eq (or ne), and CNDF 7 with EM1 = 0x0a is lt (or ge).
   * The pair (condition, end polarity) is fixed; the polarity alone
     is not. Either "EM bit 0 = 0 ends if the condition holds" with
     eq / lt, or the opposite with ne / ge.
   * The second pu_smt injection in section 8 fixes endpol and gets
     the single answers eq and lt.
   * INFERRED choice: CNDF 5 = eq, CNDF 7 / EM1 0a = lt, and EM bit 0
     = 0 ends if the condition holds. The other reading would need the
     firmware to use "ne" and "ge" as its primitive tests.
5. **CNDF 7 with EM1 = 09 (add / subtract) is the overflow test.**
   EXECUTED up to the same polarity.
   * The end word (3a69 / 1121 / 1131, EM bits 1..0 = 3) must end for
     every in-range result. Falling through instead reaches 3a6a
     (`opdb <- MAR1`), which restores opdb: the overflow exit.
   * cond_7_09 survives as never or always, coupled with endpol. Under
     the polarity chosen in item 4 it is "never" on in-range data, i.e.
     overflow. That is INFERRED, since no contract has overflowing data.
6. **Undecided by these contracts:** vis; the read strobe 59 vs 61;
   inc; wdsel; SD1F 1 and 5; ADF 1 and 7; CNDF b; the timing of
   conditional jumps. More contracts are the way
   forward: the sized allocators 3331-333a, and the get_* routines
   entered by the TGT multiway.

## 7. What the simulator agent should adopt

1. **Control store.** For KL1, `image 2 ++ syspsi[0x6800:]`
   (`pu_store.Stores.kl1_wcs`). Upper syspsi is shared, resident code,
   not an image-2 bug (section 4).
2. **Sequencer.** Rules S1-S8 as in section 2.1:
   * S8: 4-bit JMPF 3 is `case_branch`, whose low 4 bits come from the
     TGT byte of the last CNDF 7 set-up word;
   * S2b: a JMPF 1 jump with EM bit 2 is a multiway;
   * fail loud on S9 (EM = 7fff) and S10 (JMPF 2): their meaning is open.
3. **TGT.** Load sysinit 5280 / 52c0 / 5300 as three 64 x 8 tables;
   use 5300 for KL1. Column 2 is VERIFIED for set-up EM1 = 0x3a. Make
   every other EM1 → column choice a loud UNKNOWN until it is pinned.
   (Adopted by the simulator, U2 seventh session: EM1 `30`-`3f` are
   rassy's `case_tag_setup mdr1/mdr2 k`, column 7 - k of the named
   MDR's tag, `ref/pu/pu.py` `CASE_TAG_SETUP`; 3a = mdr1 5 is the
   VERIFIED column 2.)
4. **Trap stub.** 6c21 is the illegal / unimplemented instruction
   trap: 244 image-2 call sites. Implement it as a trap.
5. **Datapath.** The thesis layout, with mekbn's third-pass rules
   (section 6.3, items 1-2), now SMT-checked. Bit 62 is the write
   strobe, 58 selects MAR2, 59 selects MDR2 on a read. A write stores
   the old MDR. TGIF 1 stamps the SD1 load and 2 the ALU result. ALF 0
   is add and 1 is sub.
6. **Condition timing.** A conditional END tests the condition the
   PREVIOUS word formed. For conditional jumps, branches and returns
   the timing is UNKNOWN (6.3 item 3), so make it a switch. The
   condition is selected by that word's CNDF
   (with EM1 when CNDF is 7). Take CNDF 5 = eq and CNDF 7 / EM1 0a =
   lt, with "EM bit 0 = 0: end if the condition holds" (INFERRED
   polarity, section 6.3 item 4).
7. **Reachability.** About 46% of words are not statically reachable.
   Expect computed entries there; do not treat them as dead code.

## 8. Discriminating injections (observed)

Each was made on a private copy, by `inject.py` in the session
scratchpad. That script copies the file into a fresh directory, changes
the one line, runs `--check` there, and deletes the copy, so the tree
was never edited. The counts below are the observed lines beginning
`FAIL `, not predicted ones; the summary line is not counted. Every
line of every run was read, with no output cap:

| injection | observed |
|---|---|
| `pu_cfg.J1_CASE_BIT = 0` (S2b off) | 17 FAIL: kl1/kl0 reachable, kinds.case1 None, jump, dangling, sccs, unreachable, largest_dead, upper_reached |
| `pu_cfg.CASE_JMPF = 6` (multiway on the wrong code) | 17 FAIL: kinds.case 1405 / 1628, reachable, sccs, unreachable, upper_reached, case_img2 (1091, 77, 7, ...) |
| `pu_sysinit.KL1_COL_FOR_3A = 3` | 21 FAIL: col2_classes.0-13 (14), col2_other, column2 at all six sites (0221, 0263, 1d40, 2d3f, 2ed7, 3c61) |
| `pu_sysinit.TGT_STRIDE = 4` | 24 FAIL: the same 21, plus vect_column, ox_same.52c0, ox_same.5300 |
| `pu_smt` add_kl1 contract expects a - b | 13 FAIL: satisfiable False, every one of the 12 pinned selectors [] |
| `pu_smt` endpol domain cut to its first meaning | 2 FAIL: cond_5 ['eq'], cond_7_0a ['lt'] (the coupling of section 6.3, item 4) |
| `pu_smt` reuse_kl1 contract flipped (ends iff the MRB is on; 2026-11-27, in-process) | 1 FAIL: cond_7_29 over reuse_kl1 with endpol 'b0=0 ends if cond' ['mrb_off'] |
| `pu_smt` EXEC_DECIDED without th_adf_0 (2026-11-27, private copy) | 2 FAIL: ctime over execute_fast ['same', 'prev'], cond_3 ['lt', 'ne', 'gt', 'never'] |
| `pu_smt` execute_fast contract flipped (4cc1 taken; 2026-11-27, private copy) | 2 FAIL: cond_3 and cond_7_19 over execute_fast ['always'] |
