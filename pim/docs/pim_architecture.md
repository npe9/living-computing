# PIM/m processing-element architecture

Source note for the PIM/m reproduction. Citations are **printed page
numbers**, not PDF indices. This note covers only PIM/m; the other PIM
models are mentioned only where they are a trap for the model.

| Key | Document | Printed pages used |
|---|---|---|
| `M92` | H. Nakashima, K. Nakajima, S. Kondo, Y. Takeda, Y. Inamura, S. Onishi, K. Masuda, "Architecture and Implementation of PIM/m", FGCS '92 proceedings vol. 1 | 425–435 |
| `OV92` | K. Taki, "Parallel Inference Machine PIM", FGCS '92 proceedings vol. 1 | 53–54, 61–63 |
| `TR659` | A. Imai, K. Hirata, K. Taki, "PIM Architecture and Implementations", ICOT TR-659, June 1991 | 1–9 |
| `TR324` | A. Goto, "Parallel Inference Machine Research in FGCS Project", ICOT TR-324, Nov. 1987 | 1–3, 8–11 |
| `PIMp92` | A. Goto et al., "Architecture and Implementation of PIM/p", FGCS '92 proceedings vol. 1 | 417 |

`M92` has an OCR text layer (PDF page 458 is printed page 425). `TR659`
and `TR324` are scanned images with no text layer; their content below was
read from page images. `OV92` also has an OCR text layer.

## 1. System and PE structure

A PIM/m system has up to 256 PEs in a 16 × 16 mesh (`M92` p. 425). A
cabinet holds 32 PEs in an 8 × 4 sub-mesh; adjacent cabinets are connected
into the larger mesh, so systems from 32 to 256 PEs can be built (`M92`
p. 426). A cabinet also holds four 670 MB disks, giving a 256-PE system
more than 20 GB (`M92` p. 426). The front-end processor is a PSI/UX AI workstation whose CPU
kernel is the same as the PIM/m PE (`M92` p. 426).

Each PE has three custom VLSI chips and a separate local-memory board (`M92`
p. 426, Figure 2):

| Unit | Documented content | Citation |
|---|---|---|
| PU (Processing Unit) | 40-bit pipelined microprocessor, five-stage pipeline, microprogram control, 384 K transistors, 0.8 µm | `M92` p. 426, Figure 2 |
| CU (Cache Unit) | 1 K-word (5 KB) instruction cache, 4 K-word (20 KB) data cache, 610 K transistors, 1 µm | `M92` p. 426, Figure 2 |
| NU (Network Control Unit) | 5 × 5 crossbar, read buffer 1 KB, write buffer 1 KB, 324 K transistors, 1 µm | `M92` p. 426, Figure 2 |
| Local memory | 16 M-word (80 MB), 40-bit words, 4 M-bit DRAMs | `M92` p. 426, Figure 2 |

The machine cycle is 65 ns, improved from 200 ns on Multi-PSI/v2 (`M92`
p. 426; `OV92` p. 62; `TR659` p. 6).

*Note 2026-11-23: other sources print 60 ns for PIM/m. TR-564 PDF p. 3
(printed p. 2) says the PE's machine cycle is 60 ns, read from the page
image. FGCS'92 Vol. 1 p. 45, Fig. 7 ("PIM model M") says "Machine cycle:
60ns". TR-799 Table 3 says "PU 60nsec" (OCR, `literature_gaps.md`
App. C 2.1). The same volume's p. 43 Table 2, "Target cycle time",
prints 50 nsec in the PIM/m column. TM-1159 gives 15.4 MHz worst case
and TR-799 16.7 MHz typical (App. C 2.1, OCR), so 65 ns is probably the
worst-case clock and 60 ns the typical one (INFERENCE). 65 ns stays the
figure here: it is the one the PIM/m paper itself gives. A timing claim
should cite which figure it uses. `gap_analysis.md` §D's "60 ns" is the
other figure, not an error.*

The NU switches four adjacent-PE channel pairs plus the CPU pair. A packet
byte is 9 bits: 8 data bits plus a mark bit for header/trailer. Routing uses
a RAM path table indexed by destination PE number; each entry holds a 2-bit
direction code (straight, left, right, arrived). The read buffer holds a
whole packet and raises an interrupt when the packet tail arrives. The NU
transmits one packet byte per four machine cycles, independent of physical
distance, using FIFO output buffers and back-pressure rather than
per-byte acknowledgements (`M92` p. 427, Figures 3–4).

## 2. The five stages D/A/R/S/E

`M92` p. 428 defines exactly five stages: Decode, Address Calculation, Read
Data, Setup, Execution.

| Stage | Documented function | Citation |
|---|---|---|
| **D** (Decode) | Uses a RAM table for instruction decode. Each table entry contains the start address of the microprogram routine for the instruction and the **nano-code** that controls the following stages. The RAM decoder is intended to make microprogram development easy. | `M92` p. 428 |
| **A** (Address Calculation) | Calculates the operand address by adding two of: the instruction's operand field, PC, an An/Xn named by the operand field, and CGP (to locate a goal argument). Also controls instruction fetch, including conditional and unconditional branches. | `M92` p. 428 |
| **R** (Read Data) | Fetches an operand from the data cache using the calculated address, if necessary. | `M92` p. 428 |
| **S** (Setup) | Selects three operands from: the instruction's operand field; the operand fetched by R and its address; an An/Xn named by the operand field; a WR control register; SP. Transfers them to E according to the nano-code. S is an extra stage, beyond a conventional R stage, for pipelined data typing and dereference. It also precomputes tag-jump information (see §4). | `M92` pp. 428–429 |
| **E** (Execution) | Has two pipelined phases controlled by microinstructions. Phase 1 contains An/Xn, WR and special registers including PC and SP; it is shared by S and E for operand setup. Phase 2 contains two temporary registers (XR/YR), two memory address registers (MAR1/2) and two memory data registers (MDR1/2). Two of those registers feed the ALU, and the result is written into registers in the first and/or second phase. ALU operation and tag manipulation, including turning MRB on/off, run in parallel. | `M92` p. 428 |

The stage names and five-stage count are corroborated by `OV92` p. 62
("microprogram controlled processor with five-stage pipelining").

## 3. Words, tags and MRB

The PU is a 40-bit microprocessor (`M92` p. 426). Each register is 40 bits
wide, **including an 8-bit tag** for data type (`M92` p. 427). Local memory
is 16 M words of 40 bits (`M92` p. 426, Figure 2). The sources do not print
a bit diagram for the word. A 32-bit data payload follows arithmetically
from 40 − 8; the 8-bit-tag/32-bit-data split is stated explicitly for the
Multi-PSI PE (`TR659` p. 3), not separately for PIM/m, so treat the 32-bit
payload as inferred rather than quoted.

Named tag categories in the text and figures include reference pointer,
unbound variable, atom, list cell and structure (`M92` pp. 429–430,
Figures 6–7). Code modules are a kind of data object with a global
identifier, but the paper does not say they use a distinct tag value
(`M92` p. 432). **No numeric tag assignments or tag subfield layout are
stated** (`M92` pp. 427–429).

The tag bit used by incremental garbage collection is the **Multiple
Reference Bit (MRB)** (`M92` p. 428). `M92` p. 429 defines it as a one-bit
reference counter attached to both pointers and objects:

- a pointer's MRB is turned on when the pointer is duplicated;
- an object pointed to only by MRB-off pointers can be reclaimed after the
  (passive) unification that consumes it;
- an unbound variable may have two MRB-off pointers, one for its producer
  and one for its consumer;
- if an unbound variable is unified through an MRB-on pointer, the resulting
  data has an MRB-off pointer but cannot be reclaimed by unification through
  that pointer; the object-side MRB records whether other pointers exist.

For pipelined dereference the PU maintains two derived signals (`M92`
p. 430):

| Signal | Definition |
|---|---|
| SRP (Single Reference Path) | MRBs of **all** pointers on the reference chain are off. |
| COL (Collectable) | MRBs of the **first two** pointers are off. |

SRP and COL are passed to E and combined with the data-typing result to form
the microprogram entry address, so the E stage can decide whether reclamation
is possible (`M92` p. 430). SRP is also passed through the MRBs of An/Xn
operands of `collect_list` and `reuse_list` (`M92` p. 430).

The position of MRB within the 8-bit tag is **not stated** in `M92`. The
PIM/p paper says MRB is assigned to one of its eight tag bits (`PIMp92`
p. 417), but that is a different machine and is not evidence for the PIM/m
bit position.

## 4. Tag checking and the documented two-cycle cost

`M92` p. 428 lists three E-stage microprogram operations for tag checking:

| Operation | Documented comparison |
|---|---|
| Two-way conditional jump | Compares the tag of a register with an immediate value or with the tag of another register. |
| Three-way jump | Compares the tag of MDR1 or MDR2 with an immediate value and with the reference tag. |
| Multi-way jump | Looks up a RAM table of jump offsets, indexed by the tag of MDR1 or MDR2. |

The paper then states the timing explicitly:

> "These operations requires two machine cycles. The first cycle makes the
> jump condition or offset, and the second generates the jump address and
> fetches the microinstruction." (`M92` p. 428)

The S stage precomputes information used by the first microinstruction
(`M92` pp. 428–429):

1. modify the microprogram entry address by comparing the R-fetched
   operand's tag with an immediate value;
2. set up the offset of a multi-way jump by looking up the RAM table with
   the R-fetched operand's tag;
3. set up the two-way jump condition by comparing the tag of an operand
   transferred to E with an immediate value.

The first two require the special S stage between R and E (`M92` p. 429).
The sources do **not** state whether every tag test costs two cycles or only
the jump operations above; the quoted two-cycle cost is attached to the
E-stage tag-check jump operations. They also do not state whether the
S-stage multi-way table and the E-stage multi-way table are one physical
RAM.

Dereference is tag-driven (`M92` p. 429): when dereference from An/Xn is
ordered, R fetches the operand only if An/Xn contains a reference pointer;
when dereference is from memory, R always fetches the operand. In both cases
S examines the fetched data's tag and repeatedly reads memory until a
non-reference value is obtained. The MRB state of each reference pointer on
the path is examined as part of this walk.

## 5. WCS, decode table, tag-jump table and microinstruction format

| Structure | Documented | Not stated |
|---|---|---|
| WCS | 32 K-word writable control store; Figure 2 labels it 32Kw × 64b (`M92` p. 426). The KL1 system on PIM/m is implemented in microprogram and was converted from the Multi-PSI/v2 microprogram (`OV92` p. 54). | Microinstruction field layout, opcode fields, control-field assignment. |
| Decode table | RAM table in D; one entry per instruction; entry holds the microprogram routine's start address and the nano-code controlling the following stages (`M92` p. 428). | Table size, index width, entry width, nano-code width and encoding. |
| Tag-jump table | RAM table containing jump offsets, indexed by the tag of MDR1 or MDR2 in E (`M92` p. 428); the same lookup is described for S using the R-fetched operand's tag (`M92` p. 429). | Table size, index width, offset width/encoding, base to which an offset is added, and whether S and E use the same physical table. |
| Microinstruction | 64-bit WCS word (`M92` p. 426, Figure 2); "horizontal micro program" (`OV92` p. 62; `TR659` p. 6). | The 64-bit field layout is not printed anywhere in these sources. |

No PIM/m microprogramming manual or microinstruction listing was found in
the acquired corpus; the only assembler in the repository is the model's own
`asm/pimasm.py`. The absence is recorded in `docs/README.md`. Consequently
the decode-table and microinstruction contents above are the mechanism, not
an encoding.

*Corrected 2026-11-23: the row "Microinstruction" was true of the
sources this note read (`M92`, `OV92`, `TR659`). The field layout IS
printed elsewhere: TR-733 (Mitsubishi Denki Giho 66(6), 1992) fig. 4,
"要素プロセッサのマイクロ命令フォーマット", journal p. 76(684), TR PDF
p. 4, read from the page image. It shows bits 63..0 as CCF<5>, DSTF<5>,
SC1F<5>, SC2F<5>, SD1F<3>, SD2F<2>, AS1F<3>, AS2F<2>, ADF<3>, ALF<3>,
JMPF<3>, CNDF<4>, EM1<6>, EM2<6>, EM3<4> and five one-bit strobes
(`*`). The transcription and legend are in `literature_gaps.md`
App. C 2.3. The same page's text says one microinstruction is read
every cycle from a 32 K-word control memory, and that a tag test
through to the completed branch takes two cycles. The field
assignments within each field (the values) are still not printed;
`pseudo_pimm_microcode.md` reads them from the Pseudo PIM/m binary.*

The instruction set is KL1-B: the PU executes "WAM-like instructions for
KL1, named KL1-B" (`M92` p. 427). `OV92` p. 62 adds that the PIM/m
instruction set is KL1-B itself and is binary compatible with Multi-PSI/v2;
`TR659` p. 6 calls the PIM/m instruction set CISC and says it interprets
KL1-B code by horizontal microprogram. The **KL1-B instruction encoding is
not given** in `M92` or `OV92`; `M92` points to Kimura and Chikayama 1987 for
the instruction-set definition. The PIM/m machine-instruction word layout is
therefore not stated here.

## 6. Registers, memory and caches

The PU register set is listed on `M92` p. 427. An/Xn are implemented as one
register file; the other file, WR, holds the control registers except PC and
SP, which are hardware counters. Every register is 40 bits including the
8-bit tag.

| Register | Documented role (`M92` p. 427) |
|---|---|
| An/Xn | Argument and temporary registers |
| PC | Program counter |
| AP | Alternate clause pointer |
| CGP | Current goal record pointer |
| GSP | Goal stack pointer |
| SST | Suspension stack top |
| HP | Heap pointer |
| SP | Structure pointer |
| FVP | Free variable cell pointer |
| FLP | Free list cell pointer |
| FGP | Free goal record pointer |
| XR/YR | E-stage temporary registers (`M92` p. 428) |
| MAR1/2 | E-stage memory address registers (`M92` p. 428) |
| MDR1/2 | E-stage memory data registers (`M92` p. 428) |

Figure 5 on p. 428 labels the An/Xn file as **32w**, the WR file as **32w**,
and SP as a separate register. The sources do not state how the 32 An/Xn
entries are divided between An and Xn (`M92` p. 428, Figure 5).

Memory and cache facts:

- Local memory: 16 M words × 40 bits = 80 MB, built from 4 M-bit DRAMs
  (`M92` p. 426, Figure 2).
- Instruction cache: 1 K word × 40 bits = 5 KB (`M92` p. 426, Figure 2).
- Data cache: 4 K word × 40 bits = 20 KB (`M92` p. 426, Figure 2).
- Both caches are **direct-mapped**; PIM/m has no cache-coherence protocol
  (`TR659` p. 7, Table 4; `OV92` p. 63, Table 4).
- The R stage reads operands from the data cache (`M92` p. 428).
- Cache miss is a major performance degradation factor; the paper says the
  cache size and physical-memory access time of PIM/m are not greatly
  evolved from Multi-PSI/v2 (`M92` p. 433).
- The PIM/m cache write policy is **not stated** in these sources. `OV92`
  p. 63 says all PIMs have write-back coherent protocols, but its own
  PIM/m row has no coherence protocol; do not infer a PIM/m write policy
  from that sentence.

## 7. Pipeline and instruction latencies

The documented latencies are sparse:

| Item | Documented | Citation |
|---|---|---|
| Machine cycle | 65 ns | `M92` p. 426; `OV92` p. 62; `TR659` p. 6 |
| Pipeline | Five stages, D/A/R/S/E | `M92` p. 428; `OV92` p. 62 |
| Tag-check jump | Two machine cycles: first forms condition/offset, second forms the jump address and fetches the microinstruction | `M92` p. 428 |
| Major E-stage operations | Speedup only 1.5 versus Multi-PSI/v2, because PIM/m takes two 65 ns cycles where Multi-PSI/v2 took one 200 ns cycle | `M92` p. 432 |
| Context switch | Instructions take "dozens of cycles" in the E stage and make the pipeline stagnant | `M92` p. 432 |
| Network packet byte | One packet byte per four machine cycles | `M92` p. 427 |

Reported performance anchors, not timing rules: 615 KLIPS on `append` for a
single processor, sustained single-processor performance about twice
Multi-PSI/v2, and 5–10 times Multi-PSI/v2 for the whole system (`M92`
p. 425). KL1 `append` performs 10 memory accesses per reduction, against 6
essential accesses for Prolog `append` (`M92` p. 432).

No per-stage latency, cache-hit latency, memory-access latency, load-use
interlock, or branch penalty is given for PIM/m (`M92` pp. 428–433). The
paper's performance discussion is qualitative on cache miss and pipeline
stagnation (`M92` pp. 432–433). Do not fill these gaps from Multi-PSI/v2
(200 ns) or from PIM/p.

## 8. Microprogramming and instruction execution

- KL1 programs are compiled to WAM-like KL1-B machine instructions and
  executed by a microprogrammed PU (`M92` pp. 426–427).
- The microprogram lives in a writable 32 K-word control store (`M92`
  p. 426). The PIM/m KL1 system was converted from the Multi-PSI/v2
  microprogram by hand or partly automatically (`OV92` p. 54).
- Instruction decode is a RAM table lookup that yields the microprogram
  start address plus nano-code for the following stages; the paper presents
  this as an aid to microprogram development (`M92` p. 428).
- The E stage is controlled by microinstructions and has two pipelined
  phases; ALU operation and MRB/tag manipulation are parallel (`M92`
  p. 428).
- The S stage exists specifically to precompute tag and dereference
  information for the E stage, including the multi-way jump offset and the
  two-way jump condition (`M92` pp. 428–429).
- The sources do not give a microinstruction listing, a micro-op table, a
  KL1-B opcode table, or per-instruction microprogram lengths (`M92`
  pp. 426–430). Those remain unknown.

## 9. Do not conflate PIM/p

PIM/p is a different PE. It has RISC-like external instructions plus an
internal instruction memory, macro-call instructions, and a four-stage
D/A/T/B pipeline with extra S and C stages for internal instructions
(`PIMp92` p. 417; `OV92` p. 62). PIM/m's pipeline is D/A/R/S/E, and its
WCS/decoder model is the one described above. PIM/p's branch penalties,
macro-call mechanism and S/C pre-decode behaviour must not be imported into
the PIM/m model (`PIMp92` p. 417; `TR659` p. 6).

## 10. Model implications

The current model is in `bsv/PimTypes.bsv`, `bsv/PimStages.bsv`,
`bsv/PimE.bsv`, `bsv/PimPU.bsv` and `asm/pimasm.py`. The comments there
already label most invented fields as `MODEL`. The following separates what
the sources confirm from what they contradict.

### Model-defined routing, packet format and arbitration

`M92` p. 427 documents the mechanism: a 9-bit packet byte (8 data bits
plus a mark bit), a RAM path table indexed by destination PE whose entry
is a 2-bit direction code (straight, left, right, arrived), a 5 × 5
crossbar, and one byte per four machine cycles. It prints no encoding or
frame format. The Bluespec model therefore defines the following, all
labelled `MODEL` in `bsv/PimNU.bsv`, `bsv/PimNURouted.bsv` and
`bsv/PimMesh.bsv`:

- **Port numbering.** 0 = North, 1 = East, 2 = South, 3 = West,
  4 = CPU. The source says "four adjacent-PE channel pairs plus the CPU
  pair" and shows a 5 × 5 crossbar but does not number the ports.
- **Direction code.** An absolute output-port selector, 0 = North,
  1 = East, 2 = South, 3 = West. "Arrived" is not a table code: a
  packet whose destination PE equals the NU's own PE is sent to the CPU
  port (4) instead.
- **Route table.** `Vector#(256, Direction)`, indexed by destination PE
  (0..255). The mesh builder fills it with deterministic XY routing: if
  `destX > x` then East, if `destX < x` then West, else if `destY > y`
  then South, if `destY < y` then North. The own-PE entry is a
  don't-care because the own-PE comparison wins.
- **Packet format.** The first byte is the header: mark bit 8 = 1,
  bits [7:0] = destination PE. Payload bytes have mark bit 8 = 0. The
  last byte is the tail: mark bit 8 = 1, bits [7:0] = the last payload
  byte. Per input port, a marked byte while idle is a header (it sets
  the stored destination and enters the packet); a marked byte while
  in-packet is the tail. The header is routed by its own destination,
  the tail by the stored destination, and `packetTail()` pulses when a
  tail is delivered to the CPU port (4).
- **Arbitration.** When several input ports target one output port the
  lowest input-port index wins (fixed priority). A header locks its
  output port to its input until that packet's tail moves into the port,
  so byte-level arbitration cannot split a packet across two packets'
  bytes on one output link. Releasing the lock when the header is
  dequeued is wrong: on a mesh link the next packet's header then
  interleaves with the first packet's tail and the destination NU
  misclassifies it as a tail. `M92` p. 427 gives the
  one-byte-per-four-cycles rate but no arbitration order and no lock.

Everything above is a model choice, not a documented PIM/m encoding.

### Confirmed

1. **40-bit word, 8-bit tag.** `PimTypes` uses `Word = Bit#(40)` and
   `Tag = Bit#(8)`, matching `M92` p. 427 and the 40-bit local memory on
   p. 426. The header comment cites p. 426 for tag width; the tag-width
   sentence is on p. 427. Fix the citation, not the type.
2. **Five stages and their broad roles.** The D/A/R/S/E split in
   `PimStages` and `PimE` matches `M92` p. 428: decode-table lookup, address
   calculation, data-cache read, operand setup/tag precompute, execution.
3. **32 K × 64-bit WCS.** `PimPU` allocates 32 K WCS entries and a 15-bit
   micro-PC; `PimTypes` uses a 64-bit microinstruction. This matches
   `M92` p. 426, Figure 2.
4. **Register set and file sizes.** `PimE` has a 32-entry An/Xn space
   (16 A + 16 X), an 8-entry WR control block (AP, CGP, GSP, SST, HP, FVP,
   FLP, FGP), separate SP and PC, and XR/YR/MAR1/2/MDR1/2. This is
   consistent with `M92` p. 427 and Figure 5 on p. 428. The 16/16 A/X split
   is model-defined: Figure 5 shows one 32-word An/Xn file, not a split.
5. **MRB semantics.** The model's one-bit MRB and its SRP/COL calculation
   match `M92` pp. 428–430: MRB is a tag bit; SRP requires all chain
   pointers MRB-off; COL requires the first two MRB-off; dereference walks
   until a non-reference value.
6. **Two-cycle tag jumps.** `PimE`'s two-phase tag-jump handling (form the
   condition/offset, then update the micro-PC and fetch) matches `M92`
   p. 428.
7. **Documented memory/cache values.** 16 M × 40-bit local memory, 1 K-word
   instruction cache and 4 K-word data cache, direct-mapped, no coherence,
   are stated in `M92` p. 426, `TR659` p. 7 and `OV92` p. 63. The model
   implements only a 64 K-word memory, a deliberate simulation scaling, and
   no caches; see item 6 under contradictions.
8. **65 ns cycle.** `M92` p. 426 and `OV92` p. 62 state it (other
   sources say 60 ns, and one table gives a 50 ns target; see the note
   in §1). The model
   currently does not attach time to steps; that is acceptable only if it
   does not claim cycle accuracy.

### Contradicted or incomplete — change these

1. **The tag-jump table drops MRB.** `PimE` indexes `jumpTable` with
   `zeroExtend(tagType(wordTag(av)))`, a 7-bit type, and `condTagEq`/
   `condTagNe` compare `tagType` with `instr.imm[6:0]`. `M92` p. 428 says
   the multi-way jump is looked up by **the tag** of MDR1/MDR2, and two-way
   jumps compare **tags**. Since MRB is a tag bit (`M92` p. 428), the model
   silently discards it. Either index and compare the full 8-bit `Tag`, or
   add an explicit, documented mask policy (e.g. compare type only for
   type tests, full tag where MRB matters). Do not leave the choice
   implicit. **Resolved (2026-11-19):** the multi-way jump indexes the
   full 8-bit `Tag`; `condTagEq`/`condTagNe` compare the 7-bit type
   because the assembler's `jmp_tag` immediate is a tag type; and
   `condTagRef`/`condTagNotRef` are type tests. The policy is stated in
   `PimE.bsv` as well.
2. **The decode table has no nano-code.** `DecodeEntry` contains a
   microprogram base plus `valid/needsEA/isLoad/isStore/deref`. `M92`
   p. 428 says an entry contains the routine start address **and the
   nano-code to control the following stages**. The current entry is a
   fixed-flag simplification, not the documented decoder. Add a nano-code
   field (its width is model-defined because the source gives none) or
   explicitly label the flags as the model's entire nano-code subset.
   **Model status:** labelled — the flags are the model's entire
   nano-code subset; no field is added.
3. **E is not modelled as two pipelined phases.** `PimE` executes one
   microinstruction per cycle and writes its destination once. `M92`
   p. 428 describes two pipelined E phases: phase 1 holds An/Xn, WR, PC and
   SP; phase 2 holds XR/YR, MAR1/2 and MDR1/2; two of those feed the ALU,
   and ALU plus MRB/tag manipulation run in parallel. Either split E into
   phase 1/phase 2 or state that the model collapses them and therefore
   cannot claim PIM/m's E-stage timing. **Model status:** labelled — the
   model collapses the two phases into one microinstruction per cycle and
   therefore cannot claim PIM/m's E-stage timing.
4. **No memory-dereference provenance in S.** `PimPU` calls
   `sstage.start(r2s.rsVal)` for every dereference, and the model's current
   `deref` instruction is register-only (`pimasm.py` sets `needs_ea=False`).
   `M92` p. 429 documents two cases: dereference from An/Xn, where R fetches
   only if An/Xn contains a reference pointer, and dereference from memory,
   where R **always fetches** the operand and S examines the fetched data.
   Add a provenance bit and pass `r2s.fetched` for a memory dereference and
   `r2s.rsVal` for a register dereference before adding memory-deref
   instructions; otherwise S would walk from the address word rather than
   the memory operand. **Model status:** labelled — no memory-deref
   instruction exists; the provenance bit must be added before one is.
5. **The ISA is model-defined, not KL1-B.** `PimTypes`/`pimasm.py` define
   an 8-bit opcode, 5-bit register fields, a 17-bit immediate and their own
   opcode table. The sources say the PIM/m instruction set is KL1-B, binary
   compatible with Multi-PSI/v2 (`M92` p. 427; `OV92` p. 62). No KL1-B
   encoding table is given by `M92` or `OV92`, but the PIMOS assembler's
   table is now available (`docs/kl1_encoding.md`). Keep calling the
   current images a model-defined diagnostic ISA; do not call them PIM/m
   machine code or claim binary compatibility until the PIMOS-derived
   KL1-B encoding is implemented in the model.
   **Model status:** labelled — the model ISA is a diagnostic stand-in;
   the PIMOS-derived KL1-B encoding is documented but not implemented, so
   no binary-compatibility claim is made.
6. **No instruction or data caches in the model.** The model uses one flat
   `RegFile` for memory (`PimPU`) and therefore cannot exhibit the documented
   1 K/4 K-word direct-mapped caches or the cache-miss penalty (`M92`
   p. 426; p. 433). If the model is meant to be cycle-accounted, add
   parameterized I/D caches or explicitly exclude cache timing from every
   claim. **Model status:** labelled — no caches; cache timing is excluded
   from every claim.
7. **Front-end stall is a model choice, not documented timing.** `PimPU`
   holds D/A/R while E has any microprogram active, and while S walks a
   dereference chain. `M92` p. 428 documents a five-stage pipeline and an S
   stage that precomputes for E, but publishes no per-instruction stall or
   branch penalty. Keep the conservative interlock if it makes the model
   simple, but label it as a model choice and do not report its cycle counts
   as PIM/m's. **Model status:** labelled — the interlock is a model choice;
   its cycle counts are not PIM/m's.
8. **Multi-way jump base is unconfirmed.** `PimE` computes
   `eUPC + jumpTable[tag]`, i.e. an offset from the current micro-PC.
   `M92` pp. 428–429 says the table contains jump offsets and that S "sets
   up the offset", but does not state the base. This is a model assumption.
   Consider a jump table of absolute micro-PCs or an explicit base field;
   either way record the choice as unconfirmed. **Model status:** labelled —
   the offset-from-current-micro-PC base is a model assumption; no
   multi-way instruction exists to exercise it.
9. **Local memory is scaled.** `PimPU` uses 16-bit addresses and 64 K words,
   while `M92` p. 426 documents 16 M words. This is acceptable for Bluesim,
   but address-width behaviour (wrap, aliasing, page effects) must never be
   presented as architectural. **Model status:** labelled — 16-bit
   addresses and 64 K words; address-width behaviour is not architectural.

### Not stated — keep these out of "confirmed architecture"

- The 8-bit tag's internal field layout and the numeric values of the tag
  types (`M92` pp. 427–429 give names and comparisons, not bit assignments).
- The position of MRB within the tag (`M92` p. 428 only says it is a tag
  bit; the PIM/p statement on p. 417 is not PIM/m evidence).
- The 32-bit data-field width as a PIM/m statement; it is inferred from
  40 − 8 and from the Multi-PSI 8/32 split (`TR659` p. 3), not quoted for
  PIM/m.
- The KL1-B instruction layout, opcode values, and register-field widths
  (`M92` p. 427 names KL1-B but does not encode it).
- The 64-bit microinstruction field layout, nano-code width, decode-table
  size/index, jump-table size and offset encoding (`M92` pp. 426–429).
  *(Corrected 2026-11-23: the field layout is printed in TR-733 fig. 4;
  see the note after the §5 table. The rest of this item stands.)*
- Cache-hit latency, memory latency, branch penalty, load-use interlock,
  write policy and per-stage latencies (`M92` pp. 428–433).
- Whether every tag test or only tag-check jumps cost two cycles (`M92`
  p. 428 attaches the two-cycle statement to the three jump operations).
- Whether the S-stage and E-stage multi-way tables are the same physical
  RAM (`M92` pp. 428–429).
- The division of the 32-word An/Xn file into An and Xn (`M92` p. 428,
  Figure 5 shows one file labelled 32w).

### Cross-check: TR-324 is not a PIM/m source

`TR324` is a 1987 research overview. It describes KL1-B as the virtual
machine interface and says MRB is maintained in each KL1-B instruction
(`TR324` p. 9), but its architecture sections describe the planned PIM-1
hierarchical machine with shared-memory clusters (`TR324` pp. 10–11), not
PIM/m's 16 × 16 PE mesh (`M92` p. 425). It was used only for the KL1-B
lineage and for that negative check; it provides no PIM/m PE details.

## Sources read

- `docs/FGCS92_Volume_1.pdf`: `M92` printed pp. 425–435 (OCR text layer;
  page images of pp. 426–430 checked for figures, register list and stage
  wording). PDF page = printed page + 33. Also `OV92` printed pp. 53–54 and
  61–63 (PDF pp. 82–83 and 90–92), and `PIMp92` p. 417 (Table 1 and
  pipeline text).
- `docs/nonlocal/tr0659.pdf`: cover plus printed pp. 1–9 (PDF pp. 1–10),
  read as page images.
- `docs/ICOT_TR-324_Parallel_Inference_Machine_Research.pdf`: cover plus
  printed pp. 1–3 and 8–11 (PDF pp. 1–4 and 9–12), read as page images.
- `docs/nonlocal/tr0460.pdf`: cover plus printed pp. 1–6 (PDF pp. 1–7),
  read as page images. This 1989 report describes PIM/p (40-bit tagged PE,
  64-bit data path, IIM, cluster/hypercube network); it was checked for
  PIM/m PE content and contains none, so it is not cited above.
