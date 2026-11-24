# PSI microinstruction formats and the held control stores (2026-11-23)

Working notes of a delegated reading of Nakashima's 1991 thesis
(`nonlocal/lit/theses/`, figures read from page images) and its test
against the held PSI-III stores in `psdpim.tar.Z`, kept as written. The
scripts it used are in `asm/psi_microword/` (run as `python3 -I
asm/psi_microword/X.py docs/nonlocal/psdpim.tar.Z`). Summary:
`psi_acquisition.md` section 11. Not yet applied: `asm/mekbn.py`'s
FIELDS still follow TR-733 fig. 4.

# Nakashima 1991 thesis: PSI microinstruction formats, and a test against the held PSI-III stores

Source: `pim/docs/nonlocal/lit/theses/kurenai_2433_168749_nakashima_D_Nakashima_Hiroshi.pdf`
(156 PDF pages, two printed pages per scan). **Page map (checked): PDF page n = printed pages
2n-8 (left) and 2n-7 (right).** All readings below are from page images rendered with `pdftoppm`
(200 dpi halves; Figs. 3-11, 3-22, 3-25 re-cropped at 400-600 dpi; Fig. 3-19's width row read
at 200 dpi only, cross-checked against the text: CCF 4, DSTF 7, ALF 2 and the 53-bit total are
stated in prose), read by eye. Images: `img/`.
Labels: [READ] = printed in the thesis; [DERIVED] = computed from what is printed;
[MEASURED] = a number from a script in `bin/`; [INFERENCE] = my reading.

## 0. Conventions about bit positions

None of the three figures prints bit numbers; each prints field widths above the boxes,
left to right. Positions below assume left = MSB (bit 63 / 62 / 52) [DERIVED]. Support: PSI-I
text p.77 says TYPF fixes "the interpretation of the lower 20 bits" (下位20ビット), and the
variable part is drawn on the right; for PSI-III the store test (section 4) supports it.

## 1. PSI-I microinstruction, Fig. 3-11, printed p.74 (PDF 41 left), section 3.1.7 [READ]

Text p.74: 63 bits = a 43-bit basic part of 13 fields + a 20-bit variable part whose
interpretation TYPF selects (types 1-3). Evaluated on BUP and Window [Nakashima 87b].

Basic part (43 bits):

| Field | Width | Bits [DERIVED] | Meaning (text pp.74-78) |
|---|---|---|---|
| DBGF | 2 | 62-61 | debug/evaluation: set breakpoint or increment evaluation counters GEVC1/2 |
| DRF | 1 | 60 | select data register pDR / cDR |
| LARF | 1 | 59 | select address register pLAR / cLAR |
| LAIF | 1 | 58 | increment selected address register or not |
| MDF | 3 | 57-55 | modifies DSTF: 0-5 DSTF is a WF address generator, 6-7 individual registers; some values also write WF and one of pLAR/cLAR/pDR/cDR at once, or decrement JR |
| DSTF | 7 | 54-48 | register written from DST-Bus |
| SC1F | 8 | 47-40 | register driven onto S1-Bus |
| SMF | 2 | 39-38 | mask: extract low 16, 8 or 5 bits after rotate (S2 path) |
| SC2F | 6 | 37-32 | register driven onto S2-Bus; constant source when TYPF=1 or type 3 with SI2F=1 |
| CCF | 4 | 31-28 | memory operation (with DRF/LARF); includes rare ops e.g. cache purge |
| BYRF | 2 | 27-26 | byte count of the S2 rotate |
| FF1F | 4 | 25-22 | MSTR control: set ALU flags all at once, sign/zero only, or set/reset SW0-3 |
| TYPF | 2 | 21-20 | 0 or 1 = type 1, 2 = type 2, 3 = type 3 |

Variable part (20 bits, 19-0):

| TYPF | Fields (width) | Notes |
|---|---|---|
| 00/01 (type 1) | ALF 3, CNDF 8, RAF 9 | arithmetic ALU ops; CNDF = branch kind and condition; RAF = self-relative branch address |
| 10 (type 2) | ALF 3, BIRF 3, AAF 14 | logical ALU ops; BIRF = bit count added to BYRF rotate; AAF = absolute branch address |
| 11 (type 3) | ALF 3, BIRF 3, EALF 1, SI2F 1, FF2F 1, BJF 1, BCF 3, TEF 1, TVF 6 | EALF: ALF does both arith/logic; SI2F: SC2F is a constant; FF2F: changes FF1F to act on SW4-7; BJF: indirect branch to JR; BCF: I/O bus control; TEF: TVF (6-bit tag immediate) driven to DST-Bus tag |

MSTR (p.76): 10-bit ALU flags, 8 switch flags SW0-7, 14-bit flag "for use as machine-level
condition code". Measured use (p.77): type 1 ~65%, type 2 ~10%, type 3 ~7%, type-independent ~18%.

## 2. PSI-II microinstruction, Fig. 3-19, printed p.113 (PDF 60 right), section 3.2.7 [READ]

Text p.113: 53 bits, 10 fewer than PSI-I; emit fields EM1, EM2, EM3 hold immediates, branch
addresses and codes for rare functions (Table 3-5).

| Field | Width | Bits [DERIVED] | Meaning (pp.113-118) |
|---|---|---|---|
| DBGF | 1 | 52 | as PSI-I, breakpoint or GEVC increment, chosen by a control flag (2 bits -> 1) |
| CCF | 4 | 51-48 | memory access op, address/data register select, address increment (PSI-I 7 bits -> 4) |
| TYPF | 3 | 47-45 | selects type 1 (frequent) / type 2 (rare) codes of CCF, DSTF, SC1F, SC2F, ALF; also, with EM1 as code/immediate: MSTR control, LC/G/S counters, tag immediate to DST-Bus. Combinations listed: (1) ALU status load (no EM1); (2) status load + counter + tag immediate (restricted); (3) status load + tag immediate (any); (4) switch flags + counter |
| DSTF | 7 | 44-38 | DST-Bus destination; mostly RF direct area; simultaneous writes MDR+MAR, IFR+MAR, LC+MDR, G+MAR, S+MAR; type 2 also does I/O bus control (PSI-I 10 bits -> 7) |
| SC1F | 6 | 37-32 | S1-Bus source; half the codes address the RF direct area; constants from emit fields |
| ALF | 2 | 31-30 | add/sub and AND directly; 16 other type-1 ops (OR, shifts, mul/div support) chosen by EM2; type 2 passes the Am29332 7-bit opcode directly in EM2+EM3. Shift count from EM1 or LC; PSI-I BIRF abolished |
| SC2F | 6 | 29-24 | S2-Bus source; RF direct area 32w (PSI-I 16w); indirect area; constants from emit fields, concatenated, byte-rotated; byte shift/mask of IR etc. |
| JMPF | 3 | 23-21 | branch kind; conditional eop, subroutine call/return possible |
| CNDF | 7 | 20-14 | branch condition; tag-immediate compare (equal / not equal, masked upper-bit compare); tag 0-15 directly in CNDF, others via EM1; compound conditions (same_tag && zero, carry+zero, sign XOR overflow); MSTR 32 -> 24 bits; unconditional branches use CNDF for absolute address generation instead of EM2 |
| EM1 | 6 | 13-8 | emit field |
| EM2 | 4 | 7-4 | emit field |
| EM3 | 4 | 3-0 | emit field |

Branch address (p.117): EM3 alone self-relative; EM2:EM3 self-relative; EM1:EM2:EM3 absolute.
eop/return selected by EM3.

**Conflict, not resolved:** p.116 says SC1F is "1 bit shorter than PSI-I"; PSI-I's SC1F is 8
bits (Fig. 3-11), Fig. 3-19 prints 6. Widths as printed sum to 53, matching the text.

Table 3-5 (p.114), emit-field use (O = uses that field; (O) printed in parentheses):

| Function | Variant | EM1 | EM2 | EM3 |
|---|---|---|---|---|
| S1-Bus constant | 4 bit | | | O |
| | 4 bit | | O | |
| | 6 bit | O | | |
| S2-Bus constant | 4 bit | | | O |
| | 4 bit | | O | |
| | 6 bit | O | | |
| | 8 bit with shift | | O | O |
| | 14 bit with shift | O | O | O |
| ALU op | special op. | (O) | O | |
| | hyper-special op. | (O) | O | O |
| Branch | eop, return | | | O |
| | short relative | | | O |
| | long relative | | O | O |
| | unconditional absolute | O | | O |
| | conditional absolute | O | O | O |
| Tag immediate compare | long tag | O | | |
| Tag immediate generate | long tag | O | | |
| | short with counter op. | O | | |
| Flag control | general | O | | |
| | special | O | O | |

## 3. PSI-III microinstruction, Fig. 3-25, printed p.143 (PDF 75 right), section 3.3.6 [READ]

Text p.143: E stage split into two phases, so 64 bits (53 + 11); emit-field idea pushed further.

| Field | Width | Bits [DERIVED] | Meaning (pp.143-144) |
|---|---|---|---|
| DBGF | 1 | 63 | as PSI-II: breakpoint / GEVC increment |
| CCF | 5 | 62-58 | memory op, address/data register select, address increment; more register combinations and trail-buffer ops (4.2.2) made it 5 bits |
| WRBF | 1 | 57 | one of the 5 WR address bits, shared by DSTF/SC1F/SC2F |
| DSTF | 5 | 56-52 | phase-1 register write; a code makes EM1 the address; sequencing/pipeline registers addressed via EM1 |
| SC1F | 5 | 51-47 | S1-Bus read (phase 1); a code makes EM1 the address |
| SC2F | 5 | 46-42 | S2-Bus read; a code makes EM2 the address; IR field extraction with bit count/position in EM2 |
| SD1F | 3 | 41-39 | destination of the phase1->phase2 transfer via S1-Bus; codes include writing the same value to MAR1+MDR1 and MAR2+MDR2 |
| SD2F | 2 | 38-37 | same, via S2-Bus |
| ADF | 3 | 36-34 | DST-Bus -> phase-2 register write; includes MAR1+MDR1 at once, so with DSTF three registers get one value |
| AS1F | 3 | 33-31 | AS1-Bus read |
| AS2F | 2 | 30-29 | AS2-Bus read; AS1F modifies AS2F's meaning for constants etc. **Printed label is "AS1F" [sic]**; "AS2F" is from the heading of item (5), p.144 |
| ALF | 2 | 28-27 | add/sub only; everything else (field extraction, MRB on/off, ...) in EM2 |
| JMPF | 4 | 26-23 | branch kind; takes part of condition generation from CNDF |
| CNDF | 4 | 22-19 | branch condition; rare conditions selected by EM1 (JMPF+CNDF 2 bits fewer than PSI-II) |
| MCF | 1 | 18 | counter/flag control (PSI-II's TYPF function) |
| TGIF | 2 | 17-16 | tag-immediate generation (PSI-II's TYPF function); EM2 can also be the DST-Bus tag immediate |
| EM1 | 6 | 15-10 | emit |
| EM2 | 6 | 9-4 | emit |
| EM3 | 4 | 3-0 | emit |

Widths as printed: 1 5 1 5 5 5 3 2 3 3 2 2 4 4 1 2 6 6 4 = 64. No code values are listed for any
PSI-III field (the text gives functions only).

### 3a. Nanocode (decode table entry), Fig. 3-22, printed p.127 (PDF 67 right) [READ]

| Field | Width | Bits [DERIVED, right-aligned 50] | Meaning (pp.125-129) |
|---|---|---|---|
| ACF | 3 | 49-47 | A-stage address calculation (sources RF, E, CP, PC) |
| ASF | 1 | 46 | shift generated address right 2 bits (byte access) |
| DFF | 2 | 45-44 | R-stage fetch kind: (1) plain fetch, (2) dereference rooted in RF (no fetch unless ref), (3) dereference rooted in memory |
| LKF | 4 | 43-40 | interlock on RF entries / E / CP for instructions that update them |
| IFF | 2 | 39-38 | branch or not (A stage fetches the branch target) |
| LNF | 2 | 37-36 | instruction length 1w/2w |
| ODPF | 3 | 35-33 | how the microprogram start address is generated (MAF, upper bits from EMO2, low bits modified by conditions: tag test, unify read/write mode, shallow-backtrack mode) |
| OS1F | 3 | 32-30 | operand set-up source 1 |
| OS1F [sic, = OS2F] | 3 | 29-27 | printed "OS1F" twice; text p.128 names OS1F, OS2F |
| ODSF | 2 | 26-25 | which register the set-up goes to (MAR1/2, MDR1/2) |
| MDF | 2 | 24-23 | turns execution-mode flags (read/write mode etc.) on/off |
| TDPF | 3 | 22-20 | set-up of the E-stage tag multiway branch |
| EMO1 | 4 | 19-16 | emit |
| EMO2 | 6 | 15-10 | emit; tag immediate attached to the set-up (via "OTF", a field named in the text but not in the figure); upper bits of start address |
| MAF | 10 | 9-0 | microprogram start address (with the opcode) |

Sum 50. The decode table holds 512 entries for 1024 opcode kinds (KL0 0-511, KL1 512-1023): it is
a cache with a KL0/KL1 flag per entry; a mismatch raises a special interrupt in E whose
microprogram replaces the entry, flushes and refetches; used for pseudo-PIM (KL0 and KL1 on one
PSI-III) (p.125).

### 3b. Other PSI-III facts in section 3.3 [READ]

- Pipeline (pp.121, 125): D decode, A address calculation, R memory operand fetch (Read Data),
  S data-type test / set-up, E execute. A, R, S driven by nanocode; E by microprogram. E has
  phase 1 (RF etc. -> MAR/MDR) and phase 2 (ops on MAR/MDR), concurrent; phase 1 shared with S.
- Machine cycle 60 ns (p.123). 1.5 MLIPS, 2-3.5x PSI-II (p.122); Fig. 3-24 append: PSI-III 833
  (KL1) / 1515 (KL0) KLIPS vs PSI-II 179 / 430. PSI-II critical path quoted as 155 ns (p.139).
- Hardware (p.123, Fig. 3-20): main memory up to 64 Mw, 32-bit physical address; TLB replaces
  address translation, 64 entries each for I and D, 2-way set associative; I-cache 1 Kw, D-cache
  4 Kw, both direct mapped; 16-word trail buffer. All on chip CU (~610K transistors, 1 um CMOS)
  except the D-cache data array. PU: whole 5-stage pipeline, ~380K transistors, 0.8 um CMOS
  (p.124). **WCS: off-chip fast SRAM, 64 bit x 32 Kw (p.124).** FPP does mul/div (p.130);
  I/O bus and timer moved outside PU (p.130). One board.
- Registers (Fig. 3-21, p.126): RF 32w (argument registers A_i, addressed by r0-r2/r3),
  WR 32w (control/scratch), G, S, LC, PC, DR, IR; phase 2: XR/YR, MAR1/2, MDR1/2;
  sequence controller: ALF (ALU flags), SW, TGT (512, tag dispatch table), TDAR, MSTK (32,
  microprogram stack), JR. MAR1/MAR2 reach only AS1-Bus; XR, YR, MDR1/2 reach AS1 and AS2;
  AS2-Bus has a constant output (p.130).
- Branching (p.130, 131-132): condition selected into flag COND one step, branch on COND the
  next; ALU results can go straight to COND. No branch prediction, delay slots or multiple
  streams; the fetch side is fixed per instruction and a miss flushes. Tag multiway branch:
  `case_tag_setup` indexes TGT by MDR1/2 tag into TDAR, then `case_branch` ORs TDAR with a base.
  A 3-way dereference branch writes a 2-bit code (ref / equals immediate / other) into TDAR bits
  3-2; a 4-way version also tests MRB for KL1 (p.133).
- S stage tag mechanisms (p.134): (1) tag-vs-immediate compare of any operand into COND;
  (2) multiway-branch set-up by memory operand tag; (3) start-address change by tag compare.
  Table 3-6 (p.136) get_list steps PSI-III / PSI-II: list 1/1; ref->list 1/4; ref->undef (no
  trail) 2/5; ref->undef (trail) 3/7. Flag MODE_A (read/write unify mode) (pp.128, 137).
- Dereference in S stage (p.137-138): repeats fetch until tag is not ref; 2 cycles per pointer;
  reports SRP (all MRB in chain off) and COL (first two pointers' MRB off) to E (Fig. 3-23).
- TLB (p.141): 3-bit process ID per entry; microprogram keeps an 8-process pid map (LRU);
  D-TLB index EA(4:2)=page#(4:2) XOR area#, EA(1:0)=page#(1:0) (heap) or page#(1:0) XOR
  pid(1:0) (stacks). TLB miss handled by a microprogram-level trap: next micro-address pushed
  on MSTK automatically, logical address, R/W, write data, MDR1/2 destination saved.
- Harvard cache benefit estimate ~20% (p.142).
- **Tag and word format of the PSI-III: NOT FOUND in the thesis.** Searched: section 3.3
  (pp.119-145, all read), PSI-II 3.2.5 (pp.105-106, read: S1/S2/DST buses all carry tags; tag
  input to the ALU abolished; MDR tag and GC bit transfer kept; no widths), and the OCR layer of
  the whole thesis (de-spaced grep for tag/bit-width phrases: nothing). 3.3.4.1 says the E-stage
  tag architecture is "almost the same as PSI-II", plus a tag immediate on S1-Bus and MRB on/off
  in parallel with the ALU. The only word width printed is "40-bit word <-> 8-bit byte"
  conversion for PIM/m packets (p.148). EM1 and EMO2 being 6 bits is consistent with 6-bit tag
  immediates (INFERENCE; the project's KL1 tags run 00..3c).

### 3c. Section 3.4, parallel inference machines, pp.145-150 [READ]

- Multi-PSI/v1: 6 PSI-I, KL1 in software. Multi-PSI/v2: up to 64 PSI-II CPUs, KL1 in
  microcode, PIMOS. PIM/m: PSI-III CPU as element processor, up to 256 PE, large disks (p.145).
- Both: 2-D mesh, message passing; each PE has 16 Mw local memory; FEP is a PSI-II/PSI-III;
  FEP link: Multi-PSI/v2 via the network, **PIM/m via SCSI**; PIM/m has a 600 MB disk per 8 PEs
  on SCSI; cabinet holds 8 PEs (Multi-PSI/v2) / 32 PEs (PIM/m); 1-4 FEPs; PSI-II/III also serve as
  debugging bench via pseudo Multi-PSI / pseudo PIM (KL0 and KL1 together), with pseudo-parallel
  simulation of several PEs (p.146). Fig. 3-26 8x8=64 PE; Fig. 3-27 16x16=256 PE, 4x8=32 PE per
  cabinet (p.147).
- Network (pp.148-149, Figs. 3-28, 3-29): channel = 8 data + mark bit (packet head/tail) +
  parity = 10 bits, full duplex; output buffers 48 B (Multi-PSI/v2) / 64 B (PIM/m); CPU-side
  WB/RB buffers 4 KB each (v2) -> 1 KB (PIM/m), RB interrupts the CPU; PIM/m adds 40-bit word <->
  8-bit byte conversion; routing table PT (RAM) + 5x5 crossbar, 5-port PT read (4-port on v2);
  PT 16K entries (v2) / 1K (PIM/m); v2 router: two 20K-gate CMOS gate arrays on one board, PE = 8
  boards; PIM/m: all in 1 um CMOS VLSI on the CPU board, PE = 2 boards, 4x the PEs in the same
  volume.

## 4. The control-store test [MEASURED; scripts in bin/, outputs *_out.txt]

Files (in memory from `docs/nonlocal/psdpim.tar.Z`, never extracted or executed):

| File | Size | Header (first 12 bytes, LE u32) | Shape |
|---|---|---|---|
| `syspsi` | 262,400 | 0, 0x8000, 3 | 256 + 32,768 x 8 B LE words |
| `sysinit` | 66,544 | 0x5000, 0x205e (8,286), 0x5000 | 256 + 8,286 x 8 B |
| `sysidat` | 8,576 | 0x6800, 0x410 (1,040), 0x5000 | 256 + 1,040 x 8 B |
| `pimm.MEkbn` | 506,624 | .kbn container (5-byte words) | images 1, 2 as in `asm/mekbn.py` |

Reproduced: `pimm.MEkbn` image 1 = `syspsi` 0..0x57ff on all 17,496 non-zero words.

### 4.1 Field value distributions under Fig. 3-25 (non-zero words) [MEASURED, test_layout.py]

| Field | syspsi (24,414) | KL1 image 2 (18,343) |
|---|---|---|
| DBGF (63) set | 86 (0.35%) | 57 (0.31%) |
| WRBF (57) set | 25% | 34% |
| SD1F 2 / 3 | 68 / 57 | 41 / 38 |
| ADF (36-34) = 3 | 61 (0.25%) | 71 |
| AS1F (33-31) | all 8 values used (3 = 7%) | same |
| JMPF (26-23) | 16 values; 0:10461 1:6113 5:1387 6:1628 a:1203 e:826 ... | 16 values |
| MCF (18) set | 7.1% | 6.3% |
| TGIF (17-16) non-zero | 8.8% | 8.1% |

### 4.2 Where the thesis and TR-733 fig. 4 disagree (bits 36..23)

TR-733 fig. 4 (PIM/m, 1992; `literature_gaps.md` App. C 2.3; used by `asm/mekbn.py`). Its
legend PRINTS the widths ALF 3, JMPF 3 and the order AS1F, AS2F, ADF; only the bit positions
were measured from box geometry. So the two documents conflict as printed, not merely by
measurement: TR-733 AS1F 36-34, AS2F 33-32, ADF 31-29, ALF 28-26 (3), JMPF 25-23 (3). Thesis: ADF 36-34, AS1F 33-31, AS2F 30-29, ALF 28-27 (2), JMPF 26-23 (4). All other fields
coincide (CCF 62-58, 57, DSTF, SC1F, SC2F, SD1F, SD2F, CNDF 22-19, 18, 17-16, EM1/EM2/EM3 6/6/4).

Tests (both stores agree):

1. **Bit 26 belongs to the jump field.** MI(bit 26; bits 25-23) = 0.231 (syspsi) / 0.159 (img2);
   MI(bit 26; bits 28-27) = 0.012 / 0.013. 3-bit "JMPF 2" has bit 26 set in 1,203 of 1,229
   (syspsi) and 516 of 532 (img2); "JMPF 5" in 68 of 1,455; "JMPF 1" in 68 of 6,181.
2. **Characterisation, NOT discriminating** (`targets.py`; baseline occupancy 74.5% syspsi,
   68.9% img2): absolute EM15..0 lands 100% for 4-bit JMPF 5, 9, d (syspsi 1387/68/68; img2
   2046 [89% in range]/124/81); page-relative EM9..0 lands 99.9-100% for 3, 6, 7, a, b, e, f.
   The pairs 1/9, 3/b, 5/d, 6/e, 7/f keep the same addressing mode with bit 26 either way; only
   2 (26 words, 77%) vs a (1,203, 99.9%) splits. The evidence for bit 26 is test 1 and test 5.
5. **ALF is 2 bits (28-27) with EM2 as the operation code** (`extra.py`): with ALF = 0 or 1,
   EM2 takes all 64 values; with ALF = 2, EM2 takes 13 (syspsi) / 14 (img2) values, mostly 0-7;
   with ALF = 3, 16 / 17 values, mostly 8-14 (syspsi top: 12:850, 14:573, 8:381, 9:175, 10:149).
   That matches p.144 ("all operations other than add/sub are given by EM2") and `rassy`'s
   16-entry ALU table (0-7 arithmetic variants, 8 and, 9 or, 10 pass_as2, 11 xor, 12-15
   shifts). Under TR-733's 3-bit ALF, bit 26 would cut across these groups.
3. **ADF at 36-34 and AS1F at 33-31 in `rassy`'s SD1F/ADF numbering (0, 1 xr, 2 yr, 4 mdr1,
   5 mdr2, 6 mar1, 7 mar2).** ADF value 3 occurs in 0.25% of words (rassy lists no 3 for adf);
   SD1F 2/3 rare (rassy lists neither). In the word after a read strobe (bit 61, `disc3.py`),
   AS1F = mdr1 rises from 14% to 45% (syspsi) / 17% to 60% (img2) when bit 59 = 0 and AS1F = mdr2
   rises to 30% / 41% when bit 59 = 1 (bit 59 is the project's MDR2-select bit). Bit 31, which
   TR-733 puts in ADF, is exactly the mdr1/mdr2 discriminator. Bits 30-29 do not move after reads.
   The project's own fit (`mekbn.py` third pass) had already found that bits 36..34 "behave as
   the ALU's destination in SD1's numbering" and that bits 31..29 = 4/1/5 mean pass XR / YR /
   the sum: under the thesis these are AS1F=xr, AS2F=yr, and both (xr+yr).
4. **Byte order / alignment nulls** (`nulls.py`): as held (LE, 256-byte header) bit 63 = 0.35%,
   JMPF 5 lands 100%, MI 0.231. Big-endian: 31% / 77% / 0.066. Halves swapped: 31% / 75% / 0.002.
   Offset 257 or 260: 30% / 69-75% / 0.11, 0.002.

Verdict: **syspsi and the KL1 image are 64-bit little-endian words that parse under Fig. 3-25
better than under TR-733's measured geometry**. Fields fixed by the thesis that the project had
not placed: DBGF = bit 63 (99.6% zero), JMPF is 4 bits (26-23), ALF is 2 bits (28-27), the
ADF/AS1F/AS2F order. MCF = bit 18 and TGIF = 17-16 agree with the project's "x18" and
"17..16 stamp the tag immediate"; `rassy` (the firmware's own reverse assembler) has
predicates `mcf` and `tgif`, names that are in the thesis and not in TR-733's legend.
Strength: strong for bit 26, ALF 2 bits and bits 36-29 (two microprograms for the same machine,
largely different code: only 3,104 of 18,343 non-zero img2 words occur anywhere in syspsi and
15 at the same address; a predicted, discriminating cue; nulls); moderate for MCF/TGIF/DBGF
(consistent, not discriminating); none for CCF's internal coding (the thesis says it is a code,
the project reads strobe bits 62/61/60/59/58; not tested here). JMPF 25-23, EM and bit 57 were
already fitted by the project from TR-733, so agreement there is not new evidence.

Caution: TR-733 describes PIM/m (1992), the thesis PSI-III (1991), and they print different
widths, so either the PIM/m PE word differs from the PSI-III's or one document is wrong. The
held files are PSI-III microcode (and run on the PIM/m PU per TM-862); the store fits the thesis.

### 4.3 sysinit [MEASURED, sysinit_regions.py]

Not an overlay of `syspsi` (0 of 5,851 non-zero words equal `syspsi[0x5000+a]`; 206 occur
anywhere in syspsi). Only 0x5000-0x51ff looks like microcode under Fig. 3-25: DBGF set in 1 of
512, JMPF 5 targets land 100% inside sysinit (36 words), page-relative targets 97-100%. Large
parts are ASCII text stored in 32-bit little-endian groups ("udoM" = "Modu", "****" banners;
0x5c00-0x5fff all text) and data with DBGF set in 15-35% of words (0x5800-0x59ff, 0x6200-0x6fff):
not microcode. 0x6800-0x6c0f is exactly `sysidat` (4.4). INFERENCE: a small initialisation
microprogram at 0x5000 plus its messages, tables and a copy of the decode table; its relation to
syspsi 0x5000 (different contents) is open.

### 4.4 sysidat [MEASURED, idat.py, extra.py]

**`sysidat` is identical, word for word, to `sysinit` 0x6800-0x6c0f** (1,040 of 1,040; its
header load address is 0x6800). So `sysinit` contains the decode table.

Not a microword store: bits 63-61, 56 and 47-40 are zero in every one of 471 non-zero entries.
Start address, with the form selected by bits 36-35 (the 64-bit counterpart of `mekbn.py`'s
`tag & 0x18` rule for the KL1 table): bits 36-35 = 0 -> low 15 bits absolute, 210 of 210 land
on non-zero syspsi words; bits 36-35 != 0 -> ((index >> 7) << 11) | low 10 bits, 105/105,
142/142, 14/14 land. **471 of 471** (baseline 74.5%). That is Fig. 3-22 / p.129's rule: MAF (10
bits) + opcode, upper bits optionally from EMO2 (6 bits, = bits 15-10, the project's "6-bit
immediate"), the form chosen by a start-address-generation field (ODPF). Right-aligned, Fig. 3-22
would put ODPF at 35-33, one bit off bits 36-35, and the used bits (60-57, 55-48, 39-0 = 52,
with gaps) do not match a packed 50-bit word; the exact packing is open.

## 5. Appendix A, ESP/KL0, printed pp.237-263 (PDF 122-135) [READ, skimmed]

A language description, **not an instruction set and not a built-in list**:
A.1 object-oriented features: A.1.1 basic language (class, slots, methods, local predicates;
`Obj!slot` macros expand to KL0 built-ins `get_slot`/`set_slot`) p.237; A.1.2 inheritance,
before/after demons p.239; A.1.3 implementation of objects/classes, Fig. A-1 (object
descriptor, method table and slot table as hash tables, method-table base/mask) pp.240-241;
A.1.4 heap (ESP slot store; `heap vector`) p.245.
A.2 execution-order control: A.2.1 exceptions (`exception_handler(Pred,Type,ErrArg,Args,Addr)`,
`exception_hook/2`, register EXTR, exception control blocks on the global stack) p.246;
A.2.2 remote cut (`mark`, `remote_cut`, Fig. A-4) p.250; A.2.3 On-Backtrack
(`on_backtrack/1`, `set_slot_with_undo`) p.257; A.2.4 Bind Hook (`bind_hook/2`) p.260.
Appendix B (p.264) is KL1 (spec and implementation, MRB); Appendix C (pp.278-285) is a WAM
instruction list (get/put/unify/control/indexing) with PSI-II execution cycle counts (per
section 3.2.2's text as seen only in the OCR layer; Appendix C itself not opened); Appendix D (p.286) a WAM execution example.

## 6. Files

- `bin/stores.py` reader (in-memory tar, .kbn container, raw 64-bit words)
- `bin/test_layout.py` field histograms under Fig. 3-25; `layout_out.txt`
- `bin/disc.py`, `bin/disc2.py`, `bin/disc3.py` thesis vs TR-733 discriminators; `disc*_out.txt`
- `bin/targets.py` jump landing per 4-bit JMPF; `targets_out.txt`
- `bin/nulls.py` byte order / offset nulls; `nulls_out.txt`
- `bin/sysinit_regions.py`; `sysinit_out.txt`; `bin/idat.py` (sysidat)
- `img/` page renders and figure crops (f311a/b, f319, f325_0/1, f322b)
Run any of them as `python3 -I bin/X.py /Users/npe/src/living-computing/pim/docs/nonlocal/psdpim.tar.Z`.
