# The IBM 7619 Exchange and the 7030 I/O system

A primary-source study of the largest unmodelled subsystem in this
project's Bluespec model. `bsv/StretchIO.bsv` is 342 lines of which 81
are code: three flat device buffers at hardcoded channel addresses
32/33/34, no Exchange, no arbitration, no disk, no device timing. This
document establishes what the real thing is, from the documents in
`docs/`, and what it would cost to model.

**Citation convention.** Reference Manual page numbers are *printed*
pages; `22-6530-2_7030RefMan.pdf` has no text layer, so every page here
was read as a 300 dpi PNG. The offset **PDF page = printed page + 3**
was verified directly (PDF 107 renders printed 104, "IBM 7619
Exchange"); it holds across the whole Exchange and External Units
chapters. Buchholz (`Planning_A_Computer_System.pdf`) has a text layer
and is cited by its own printed page. **The other image-only PDFs do not
share an offset — each was checked on the page.**
`A22-6552-1_physPlan_Feb63.pdf` runs **PDF = printed + 1** (PDF 7 renders
printed 6, PDF 8 renders printed 7).
`C22-6678-1_7030_MCP_Reference_Jun64.pdf` runs **PDF = printed + 0** (PDF
6 renders printed 6, PDF 7 renders printed 7).
`R23-9702_7503_Card_Rdr_7614_Rdr_Ctl_CE_1961.pdf` runs **PDF = printed +
0** (PDF 5 renders printed 5). Performance Characteristics Vol.1 is
cited by its section-page numbering (3-16, A-1, …).

---

## 1. What the Exchange is

### 1.1 The one-paragraph answer

The IBM 7619 Exchange is a **separate, special-purpose, fixed-program
computer** that owns all input-output on the 7030. It is one physical
unit (one frame, Figure 1 of the Reference Manual, printed p.6; "IBM
7619 Exchange" in the physical-planning unit list, A22-6552-1 p.6)
carrying up to 32 logically independent byte-serial channels, numbered
32 through 63, each terminating in exactly one control unit. Its heart
is its own small fast core store — **Exchange Storage (ES)**, 1 µs cycle
— holding, *per channel*, one control word and two data words. A
channel-scanner/multiplexer picks whichever channel has raised a service
request, addresses ES with that channel number, and runs a single 1 µs
cycle that either shifts one 8-bit byte out of (writing) or into
(reading) that channel's data word; every eighth such cycle it instead
runs a control-word-modification cycle that increments the data-word
address, decrements the count, and — when the count hits zero with the
chain flag on — a refill cycle that fetches the next control word from
main core storage. It is the Exchange, not the CPU, that issues the
resulting main-storage references; those are interleaved with the CPU's
through the memory bus control unit. The CPU's entire involvement in an
I/O operation is: compute two effective addresses, hand the Exchange a
channel number, an operation code and a control-word address, and wait
the few microseconds it takes the Exchange to test the unit's stored
status bits and either accept or reject. After that the program runs on
and the Exchange finishes the transfer by itself, reporting completion
by interrupting the program and depositing the channel number in the
channel address register.

### 1.2 The sources, quoted

Function (Buchholz §16.1, printed p.248):

> "The function of the exchange is to direct the information flow
> between input-output or external storage units and internal memory.
> It transfers data between external units and any part of the main
> memory independently of the computer, and so it permits a number of
> external units to function simultaneously with the processing of data
> in the computer. Furthermore, the exchange provides a buffering
> action: for it transfers data on demand, as required by the unit,
> using main memory as buffer storage."

Nature (Buchholz §16.1, printed p.250):

> "In a sense, the exchange is a separate special-purpose, fixed-program
> computer. It receives directions from the main program in the form of
> predigested instructions and control words. In general, the exchange
> performs those functions that remain unchanged from one job to the
> next, and it does such limited jobs more efficiently than the main
> computer could do them."

Mechanism (Buchholz §16.2–16.4, printed pp.250–251):

> "The heart of the exchange is a small, 1-µsec core memory which has
> space for a limited amount of data and control information for each
> channel. In a single 1-µsec cycle, a word can be read from this
> memory, modified, and returned to its location."

> "The exchange starts a 1-µsec memory cycle to pull the data word out
> of the appropriate location and pass it through the shift circuit…
> The leftmost byte is sent to the unit via a multiplexing circuit while
> the remaining bytes are shifted left by 8 bits. The shifted data word
> is returned to the exchange memory, still within the same memory
> cycle."

> "After the eighth such byte cycle, the data word is exhausted and a
> control-word cycle is started. The current data-word address is
> extracted to fetch a new data word while the control word is modified,
> adding 1 to the address and subtracting 1 from the count."

> "The purpose of the multiplexer is to determine which channel has
> requested service, to send the channel number to the exchange memory
> as an address for selecting the appropriate data and control-word
> locations, and to gate the lines of this channel to the common
> data-handling circuits. If more than one channel requests service at
> the same time, the requests are handled in turn during different
> cycles, and no conflict arises."

The Reference Manual's own component list (Figure 34, printed p.104)
names the boxes a Bluespec module would instantiate: **Buffer Register**
and **Addr Regs** (to/from core storage), **Error Checking and
Correction**, **ES Register**, **Exchange Storage (ES)**, **Data Word
Shifting**, **Control Word Modification**, **Storage Drivers**, **ES
Address Control**, and **Channel Scanner and Switch** fanning out to
channels 32, 33, 34, 35 … 63.

### 1.3 How many channels, and is it one unit or several

One unit, expandable in groups of eight (Reference Manual p.104):

> "The exchange provides up to 32 channels for connecting external units
> directly to the system. These units are of the kind that operate
> serially one 8-bit byte at a time, and thus require eight bytes to
> transmit a full storage word of 64 bits. The channels are nine bits
> wide, accommodating an 8-bit byte and a parity bit to check
> transmission over the channel. With units that are presently
> available, a channel can achieve data rates of one byte every 16
> microseconds, but higher rates can be accommodated."

> "The exchange can have several combinations of channels. The minimum
> is eight. This minimum can be augmented by additional channels in
> groups of eight up to 24 additional, or a total of 32 channels."

Channel numbering, and the fact that it is also the arbitration
priority (Reference Manual p.111):

> "The channel addresses correspond to the 32 physical exchange channels
> and are assigned the numbers 32 through 63. Within the range 32
> through 63 the specific assignment of the addresses is arbitrary and
> depends upon the specific units in an installation."

> "The channel address determines the priority a unit receives from the
> exchange in response to its service requests for bytes of data: the
> lower the channel address of a unit, the higher is its priority.
> Consequently, units which cannot interrupt their operation will
> normally have lower channel addresses than those having weights of
> zero. **The same priority applies also to the transmission of words of
> data between the exchange and the core storage.**"

The per-channel ES allocation is stated exactly in Performance
Characteristics Vol.1, Appendix A (p.A-5):

> "The exchange contains up to 32 channels (32-63) for simultaneous I/O
> processing. Through adaptors each channel can be connected to eight
> tape units or with one non-tape I/O unit. Each channel is represented
> by one control word and two data words in the exchange memory. The
> channels communicate with the exchange memory thru a multiplexer."

and the same page gives the Exchange's registers and clock:

> "The exchange unit contains a main memory address register (MMAR) and
> a buffer register to communicate with the MBCU. It also contains an
> interruption address register for the channel which has created an
> interrupt condition, as well as triggers (EOP, UK, EK, EE, and CS) to
> indicate the reason for interrupt… When IAR is busy (Interrupt Wait
> trigger on), other channels cannot use it to cause other
> interrupts."

> "Has its own clocking circuit (1.x µs cycles divided into 10 equal
> pulses) and ECC check-bit generator-comparer. Maximum word rate is 1
> extended word/10 µs for the entire exchange."

(The register list on p.A-9 adds: Exchange storage (EM); EMAR, exchange
memory address register, 7 bits + check; word register communicating
with EM, 76 bits; MMAR 18 + check bits; MBCU buffer register 72 bits;
interrupt address register 7 + check; interrupt triggers for 5
conditions; interrupt wait bit; multiplexer; ECC generator/comparer. A
7-bit EMAR for 32 channels × 3 words = 96 locations is consistent.)

### 1.4 The disk is *not* on the Exchange

This matters for the model, because it is a second, parallel DMA engine.

Reference Manual p.157:

> "The high-speed disk storage system provided with the IBM 7030 is
> composed of the IBM 7612 Disk Synchronizer, which provides the common
> control and data transfer paths for the disk system and the computer,
> and the storage unit… The IBM 7612 Disk Synchronizer serves as the
> major control for the disk system… Basically, the method of control is
> the same as that used in the exchange. However, the high rate of data
> transmission between a disk storage and internal storage causes some
> differences in operational and program control."

> "The disk synchronizer has provision for addressing a maximum of 32
> disk storage units. Each disk unit has its own channel address.
> However, only a single data transmission channel is available because
> of the high data transfer rate… Each disk storage unit has a capacity
> of 2,097,152 (2²¹) words. Data may be transferred between the disk
> storage and core storage at an instantaneous rate of one full word
> every eight microseconds."

Performance Characteristics Vol.1 p.A-5 gives the disk exchange's
channel numbers and its restrictions:

> "The disk exchange contains 32 channels (0-31), only one of which can
> be in operation at any given time. It contains enough memory for 1
> control word and 1 data word, and each channel can be attached to one
> disk unit. Disk word rate is 1 extended word/8 µs. No direct chaining
> of the I/O control words is permitted. In addition, the
> copy-control-word operation cannot be performed when reading or
> writing. Otherwise the disk exchange functions in much the same way as
> the exchange."

So: **channel addresses 0–31 are the disk synchronizer, 32–63 are the
Exchange**, and the same `RD`/`W`/`CTL`/`LOC`/`REL`/`CCW` instructions
address both. The model's choice of 32/33/34 for reader/printer/tape is
therefore in the right range, by accident or by good reading.

---

## 2. What a typical installation has

### 2.1 The definitive sentence

`A22-6552-1_physPlan_Feb63.pdf`, printed p.6, under "System
Components":

> "An average 7030 system will consist of a central processing unit,
> exchange, power distribution unit, six core storage units, three tape
> controls, eight magnetic tape units, card reader, card reader control,
> printer, printer control, card punch, card punch control, console
> control, console, disk synchronizer, and a disk storage."

With model numbers, from the "Unit Description" that follows (pp.6–7):

| Unit | Model | Count in the average system | Notes |
|---|---|---|---|
| Central Processing Unit | IBM 7101 | 1 | |
| Exchange | IBM 7619 | 1 | min. 8 channels, +8 at a time to 32 |
| Core Storage | IBM 7302 | 6 | Model I = 16,384 words; Model II = 8,192 |
| Power Distribution Unit | IBM 7803 | 1 | 60-cycle and 400-cycle |
| Disk Synchronizer | IBM 7612 | 1 | |
| Disk Storage | IBM 353 *(see §2.3)* | 1 | 2,097,152 words |
| Magnetic Tape Unit | IBM 729 IV | 8 | must attach to a 7613 |
| Tape Control | IBM 7613 | 3 | up to eight 729 IV each, one at a time |
| Card Reader | IBM 7503 | 1 | 1000 cpm; must attach to a 7614 |
| Card Reader Control | IBM 7614 | 1 | |
| Card Punch | IBM 7553 | 1 | 250 cpm; must attach to a 7615 |
| Card Punch Control | IBM 7615 | 1 | |
| Printer | IBM 1403-2 | 1 | 600 lpm; must attach to a 7616 |
| Printer Control | IBM 7616 | 1 | |
| Operator's Console | IBM 7152 | 1 | must attach to a 7623 |
| Console Control | IBM 7623 | 1 | |

Three tape controls for eight tape units is deliberate: a 7613 drives up
to eight 729 IVs but "only one may operate at a time" (A22-6552-1 p.7),
so three controls buy three simultaneous tape streams. *(Conjecture, my
arithmetic, not sourced: that fills the basic eight-channel Exchange
almost exactly — 3 tape + 1 reader + 1 punch + 1 printer + 1 console = 7,
with one spare. No document in `docs/` assigns units to specific channel
numbers; the Reference Manual says only that "the specific assignment of
the addresses is arbitrary and depends upon the specific units in an
installation", p.111.)*

Two independent corroborations:

- **Reference Manual Figure 1, "Typical IBM 7030 System", printed p.6.**
  The Exchange is drawn with eight control units hanging off it, feeding
  "Mag Tape Units", a "600 lpm Printer", a "1000 cpm Card Reader", a
  "250 cpm Card Punch", and "Console and Console Printer"; the Disk
  Synchronizer hangs off the Storage Bus Control separately, with "Disk
  Storage 2,097,152 Words 125,000 Words/sec."
- **Performance Characteristics Vol.1, p.A-1**: "The main memory,
  sometimes called extended memory, is composed of six boxes of 16,384
  extended words each (**for the Los Alamos configuration**)." That is a
  real delivered machine, not a brochure, and it agrees on six boxes —
  the same six `StretchMemory.bsv` already models.

### 2.2 What MCP requires (and it needs the disk)

`C22-6678-1_7030_MCP_Reference_Jun64.pdf`, printed p.6, "Minimum I/O and
Core Storage for the 7030":

> "The minimum input-output and storage requirements for the IBM 7030
> Data Processing System under MCP are:
> An IBM 1401 Data Processing System (Tape-Oriented), used for off-line
> operation.
> A minimum of three IBM 7302 Core Storage units.
> An IBM 7612 Disk Synchronizer with at least one disk unit used to
> store system programs and as auxiliary storage for the problem
> program.
> An IBM 7619 Exchange with the minimum eight basic exchange channels is
> used as follows:
> 1. An IBM 7152 Operator's Console is used by the operator to issue and
> receive commands controlling MCP…
> 2. An IBM 7503 Card Reader is used by the system input subroutine to
> read in problem programs and MCP commands while MCP is in either the
> on-line overlapped or bypass mode of operation…
> 3. At least four IBM 729 IV Magnetic Tape Units with one or more tape
> control units…"

The four tapes are named individually: system output tape, alternate
system output tape, system read tape, system write tape. The page then
lists exactly what MCP can survive without:

> "1. The system can operate while the tape-oriented IBM 1401 System is
> temporarily inoperative. 2. The system can operate in the off-line
> overlapped mode without the card reader. 3. The system can operate
> with one output tape while waiting for reloading. 4. The system can
> operate in the bypass mode without the input tapes. 5. The system can
> operate in either overlapped mode with one input tape unit while
> waiting for input prescan and rewind time."

**The disk is not on that list.** MCP stores its own system programs on
the disk and IPLs from it ("Disk IPL", "Disk Initialization" — MCP
Reference contents, pp.32). A conservative reading, and the one this
document recommends: *running MCP requires the 7612 disk synchronizer
and at least one disk unit, the console, the card reader, and four
tapes* — i.e. essentially the whole subsystem, not the minimum subset of
§5. Anyone planning to run MCP on this model should treat the disk as a
first-class deliverable, not an extra.

Note also the 7030's I/O philosophy: the printer and punch are *not* in
MCP's minimum list, because MCP writes a system output tape that a
separate, off-line, tape-oriented IBM 1401 turns into print and cards.
The 1401 is a second computer, out of scope for a 7030 model; a model
that wants visible output without it must drive the 1403-2 on-line,
which MCP supports but does not require.

### 2.3 One unresolved discrepancy: which disk

`A22-6552-1` (Feb 1963) p.6 says "**IBM 7612 Disk Synchronizer and IBM
353 Disk Storage**". The system block diagram at the front of
`R23-9702` (1961) labels the same box "**7303 Disk Storage**". The
Reference Manual's High-Speed Disk System chapter (p.157) gives the
synchronizer's number (7612) but calls the other half only "the storage
unit". Both are primary and both are in this repo. I have not resolved
which designation applies to which machine or date, and I am not
guessing. For modelling purposes the number does not matter — the
*behaviour* (2,097,152 words, 4096 arcs of 512 words, 512 tracks × 8
arcs, 39-bit bytes of 32 data + 7 ECC, one word per 8 µs, ≤265 ms
full-stroke seek, Reference Manual p.157) is unambiguous.

---

## 3. The CPU-side programming interface, completely

### 3.1 Instruction format

All six I/O instructions are full-word, two-half-word instructions
(Reference Manual p.111, with its figure's bit boundaries read off the
300 dpi page):

```
 bit:  0        12      18    24   28   32              49 50 51   55       60   63
      +----------+-------+-----+----+----+----------------+--+-----+---------+----+
      |  (addr)  |CHANNEL|(adr)|1000| I  |    ADDRESS     |  | OP  |  10000  | I  |
      |          |ADDRESS|     |    |    |                |  |     |         |    |
      +----------+-------+-----+----+----+----------------+--+-----+---------+----+
       <------ first half-word ------->   <-------- second half-word -------->
```

- **Channel address**: 7 bits, bit positions 12–18 of the *left*
  effective address. "The channel address is specified by the left
  effective address of all input-output instructions" (p.111). The
  channel address register in the interrupt mechanism "is also seven
  bits long and corresponds to bit positions 12 through 18 when
  addressed" (p.111) — it is word address **5** (p.119).
- **Right effective address**: 18 bits, bit positions 32–49. "Some
  instructions use only part of this field" (p.111).
- **Indexing**: "In the first half-word, index arithmetic extends over
  the full 24 bits of the channel address field of the instruction and
  the whole value field of the index word, including its sign, but only
  bits 12 through 18 of the effective address are used. The rest is
  ignored by the exchange. In the second half-word, index arithmetic
  extends over bits 32 through 50 of the instruction word and the whole
  value field of the index word, including its sign, but only bits 32
  through 49 are used." (p.111)

  *This confirms the derivation already recorded in
  `strap/programs/io_reader_printer.strap`*: the channel number sits
  five bit positions up inside the 24-bit address field, so a literal
  channel 32 is written 32 << 5 = 1024.

What goes in the right effective address, per instruction (p.111):

| Instruction | Right effective address holds |
|---|---|
| `RD` READ | core-storage address of the control word |
| `W` WRITE | core-storage address of the control word |
| `CCW` COPY CONTROL WORD | core-storage address to deposit the control word at |
| `CTL` CONTROL | an 8-bit control code, bits 42–49 (p.120) — *immediate, not an address* |
| `LOC` LOCATE | a 3-bit selection address, bits 47–49 (p.120) |
| `REL` RELEASE | not used; ignored (p.121) |

Each has a SEOP variant: `RD SEOP`, `W SEOP`, `CTL SEOP`, `LOC SEOP`,
`REL SEOP` (p.121).

### 3.2 Control word format — bit by bit

Reference Manual, **Figure 35, printed p.107**, read at 300 dpi. IBM
numbers bit 0 as the most significant bit of the 64-bit word.

| IBM bits | Field | Bluespec `[63:0]` slice |
|---|---|---|
| 0–17 | **Data Word Address** | `w[63:46]` |
| 18 | Status: **Unit Ready** | `w[45]` |
| 19 | Status: **Exchange Program Check** (EPGK) | `w[44]` |
| 20 | Status: **Unit Check** (UK) | `w[43]` |
| 21 | Status: **End Exception** (EE) | `w[42]` |
| 22 | Status: **End of Operation** (EOP) | `w[41]` |
| 23 | Status: **Channel Signal** (CS) | `w[40]` |
| 24 | Status: **Suppress End of Operation** (SEOP) | `w[39]` |
| 25 | Flag: **Chain** | `w[38]` |
| 26 | Flag: **Multiple** | `w[37]` |
| 27 | Flag: **Skip** | `w[36]` |
| 28–45 | **Count** | `w[35:18]` |
| 46–63 | **Refill** address | `w[17:0]` |

**This confirms `bsv/StretchTypes.bsv`'s existing `unpackControlWord` /
`packControlWord` exactly, field for field.** No correction is needed.
Independently it is also confirmed structurally: "The control word
format follows that of an index word: the data word address occupies the
word address portion of an index word value field while the count and
refill fields of control and index words are the same" (p.106), and this
repo's index-word handling is already verified against IBM's own
assembler listings (`verify_ibox1_vpcr_refill_listing.py` and friends).

Three properties of the format the model does **not** currently honour,
all from p.123:

1. **Status bits are inputs, not just outputs.** "Bits 18 to 24 … are
   ignored by the exchange when it obtains a control word from core
   storage; normally bits 18 to 24 will be zeros." A fetched control
   word's status field must be *masked off*, not carried in.
2. **Bit 25 (chain) doubles as the index-flag source.** "Bit 25, the
   chain flag, may set the index-flag indicator in the indicator
   register during indexing operations… Bits 26 and 27 are not used for
   indexing operations, but they are carried along unchanged when
   loading, storing, or refilling index words."
3. **Count 0 means 2¹⁸.** "If the count field in the control word is
   zero initially, it is interpreted as 2¹⁸. The field is not tested for
   zero until the first time the control word is modified; the count at
   that time is 2¹⁸ − 1, and counting will continue. The count field
   cannot specify less than one word." (The model's `IoXfer.remaining`
   is already `Bit#(19)` for exactly this; the header comment cites
   p.107 where the manual puts it on p.123.)

### 3.3 Block termination: Figure 36 in full

Reference Manual **Figure 36, "Multiple and Chain Flag Operations",
printed p.109**. This is the complete, implementable state table for
what happens at a word boundary. Transcribed exactly:

| Multiple | Chain | Count (0=Zero, 1=Not Zero) | End of Block (0=Yes, 1=No) | Action |
|---|---|---|---|---|
| 0 | 0 | 0 | 0 | End operation |
| 0 | 0 | 0 | 1 | Disconnect, then end op. |
| 0 | 0 | 1 | 0 | End operation |
| 0 | 0 | 1 | 1 | Continue |
| 0 | 1 | 0 | 0 | End operation |
| 0 | 1 | 0 | 1 | Chain and continue |
| 0 | 1 | 1 | 0 | End operation |
| 0 | 1 | 1 | 1 | Continue |
| 1 | 0 | 0 | 0 | End operation |
| 1 | 0 | 0 | 1 | Disconnect, then end op. |
| 1 | 0 | 1 | 0 | Restart and continue |
| 1 | 0 | 1 | 1 | Continue |
| 1 | 1 | 0 | 0 | Chain, restart and continue |
| 1 | 1 | 0 | 1 | Disconnect and chain |
| 1 | 1 | 1 | 0 | Restart and continue |
| 1 | 1 | 1 | 1 | Continue |

Supporting rules on the same page:

- "Whenever the end of a block is reached and a new block is started,
  data transfer continues with the next full word in core storage. If a
  block is not an integral number of full words long, on reading, the
  missing bytes of the last word are filled with zeros. On writing, the
  bytes remaining after completion of the block are ignored."
- The multiple+chain, count-exhausted-mid-block case: "When the count
  reaches zero, the exchange sends a disconnect signal to the unit…
  The unit proceeds upon the receipt of the signal to the end of the
  current block without any data transfer and without any control word
  modification. On reading, the remainder, if any, of the current block
  is skipped… Thus, in this mode of operation, it is possible to force a
  gap on tape at the end of any selected control word in a chain."
- "A multiple block operation may, however, be terminated before
  reaching the last block specified by the instruction. If an exchange
  program check, a unit check, or an end exception is caused, the
  operation never proceeds beyond the end of the block in which the
  condition is discovered."

**Skipping** (p.109): "The skip flag, when zero, specifies normal
reading. On writing, the flag is meaningless and is ignored. When the
skip flag is one, no data words are transferred to core storage. The
operation of the unit is still continued, and the system goes through
all the sequences associated with data transfer between the exchange and
the unit. The control word is also appropriately modified… Since the
testing for data word addresses that exceed the available core storage
is performed in the core storage controls, reference to non-existent
core storage locations cannot cause an exchange-program-check indication
when reading with the skip flag on." (The model implements skip on READ
only, correctly.)

### 3.4 Chaining timing

Reference Manual pp.124–125, the parts an implementation has to get
right:

- "When chaining is specified, the exchange obtains the new control word
  immediately before referring to the first core storage location
  specified by the new control word. On reading, the new control word is
  fetched when the data transfer specified by the preceding control word
  has been completed and the exchange has already assembled the first
  data word to be sent to the area defined by the new control word. This
  timing does not depend upon the original word count of the control
  word nor on the state of its multiple flag."
- "On single block writing, chaining normally takes place when the count
  in the control word is stepped from 2 to 1. When a control word on
  chained writing originally has a word count of one, the next control
  word is obtained one word time (the time required to write one word)
  after fetching the control word with the count of one. If the first
  control word of a WRITE has a word count of one, and the chain flag is
  on, the next control word is fetched immediately after fetching the
  data word for the first control word."
- "An exception to the above rules for chained writing occurs when the
  current control word has both the multiple and the chain flags on. In
  this case the new control word starts a new operation as far as the
  unit is concerned, and chaining takes place only after the exchange
  buffer has been cleared and the preceding block has been terminated."

### 3.5 The two-word write buffer and the terminal control-word values

Reference Manual p.124. This is the "+2 quirk" the model deliberately
does not reproduce; here is the complete rule, which is actually a
*three*-way distinction:

> "In order to insure continuous data transmission, each exchange
> channel provides a buffer for storing two data words for the current
> operation."

| Operation terminated | Data word address | Count |
|---|---|---|
| READ | `Aₙ` | `Cᵢ − N` |
| WRITE | `Aₙ + 2` | `Cᵢ − N` |

> "`Aₙ` = address of next data word to be handled by an external unit =
> 1 + address of last word read or written = `Aᵢ + N`; `Aᵢ` = initial
> data word address; `N` = number of words transmitted between the
> exchange and the unit; `Cᵢ` = initial count."

And, separately, during an in-flight `CCW`: "During writing, the control
word always gives an address which is two words ahead of the data word
just being written" (p.122) — but when the write has *completed*, "the
count is zero and the data word address refers to a location that is
**three** words ahead of the one from which the last word was fetched"
(p.124). Both numbers appear; they describe different instants
(mid-operation copy vs. normal completion). A cycle-accurate model with
a real two-word buffer gets all three for free; the current model, which
moves one word per cycle with no lookahead, correctly declines to fake
any of them.

Also: "The sum of the current values of the data word address and count
fields is always equal to the sum of the original values of these
fields" (p.124, for READ) — a cheap, strong invariant to assert in a
testbench.

### 3.6 `CTL` function codes — the bounded negative, then the real tables

There is **no universal `CTL` code list, by design.** Buchholz is
explicit (printed p.183):

> "Thus CONTROL has only a single meaning in the computer. The
> specialized functions are defined separately for each external unit
> and form part of its design specifications. They may range from an
> elaborate set of control functions for some high-performance units to
> none at all for rather primitive devices. The input-output channels
> remain general in function and need not be altered as new devices are
> attached or as the mix of units is changed."

The Reference Manual agrees operationally: a code the unit does not
recognise is an **Exchange Program Check** raised *by the unit*, not by
the Exchange — "The eight low-order bits of the right effective address
of a CONTROL instruction contain a code that is not defined for the
unit" is cause (2) of EPGK (p.113).

What *is* enumerable is the per-device tables. Complete, for the devices
of §2:

**Standard functions, common to most external units** (Reference Manual
p.130):

| Octal | Function |
|---|---|
| 016 | Reserved Light Off |
| 017 | Reserved Light On |
| 057 | ECC Mode — subsequent data read/written with ECC bits attached |
| 116 | Check Light On — can only be turned off by the unit's start key |
| 157 | No-ECC Mode |

**IBM 729 IV magnetic tape** (Reference Manual p.132; the tape
*redefines* 016, 057 and 157):

| Octal | Function |
|---|---|
| 016 | Remove End of Tape Condition (tape-indicator-on light off) |
| 036 | High Density Mode (556 bpi; power-on default) |
| 037 | Low Density Mode (200 bpi) |
| 056 | Erase Long Gap (next WRS/WTM lays an 8½-inch blank gap) |
| 057 | ECC Mode and Odd Parity |
| 076 | Space Block (forward one block; EE+EOP if the block is a tape mark) |
| 077 | Space File (forward past a tape mark; EE and EOP given) |
| 117 | Write Tape Mark (writes the standard tape mark 0001111) |
| 136 | Rewind (EOP given **at initiation**; CS when load point reached) |
| 137 | Rewind and Unload (no channel signal on completion) |
| 156 | No-ECC Mode and Even Parity |
| 157 | No-ECC Mode and Odd Parity (power-on default) |
| 176 | Backspace Block |
| 177 | Backspace File |

(The model implements 136/137 and 176 only. Every other code decodes to
Operation Code Invalid — a documented, deliberate gap.)

**IBM 7503 card reader** (Reference Manual p.139): the five standard
codes only — 016, 017, 057, 116, 157. No reader-specific functions
exist.

**IBM 1403-2 printer** (Reference Manual p.145): "Standard control
functions initiated by a CONTROL instruction and executed by the printer
are: 016 Reserved Light Off, 017 Reserved Light On, 116 Check Light On."
Three codes, no ECC-mode codes. The printer section runs pp.145–148 and
p.146 was also read: it is entirely carriage control, with no further
`CTL` codes, so three is very likely the complete list — but the manual
says "standard control functions", not "only", and pp.147–148 were not
read, so treat "three" as near-certain rather than established.

Carriage motion is *not* a `CTL` function: "Operation of the carriage is
under the control of a special control code, called CARRIAGE CONTROL
FIELD. The carriage control field consists of one or more 8-bit bytes
and specifies the number of lines over which the carriage must skip
before reaching the line on which the information immediately following
is to be printed. **Every line to be printed must be preceded by a
carriage control field.**" (p.145) That is in-band, in the written data,
not in a `CTL`.

**Carriage control field codes** — Reference Manual Figure 44, printed
p.146. One 8-bit byte; a skip byte is always the last byte of the field,
and "the printer interprets the following information as data to be
printed":

| Decimal | Meaning |
|---|---|
| 0 | Skip 0 lines (single space) |
| 1 | Skip 1 line (double space) |
| 2 | Skip 2 lines (triple space) |
| … | … |
| 223 | Skip 223 lines |
| 224 | Select No Report |
| 225–232 | Select Report 1 / 2 / 1 or 2 / 3 / … / Report 4 |
| 239 | Select Reports 1, 2, 3 or 4 |
| 240 | Suppress Post-Spacing |
| 241 | Skip To Restore |
| 242–253 | Not used; ignored by the printer (same effect as no-op) |
| 254 | End — "causes the subsequent bytes to be ignored and terminates the current block of the operation… suppresses all printing" |
| 255 | No Operation — "may be used as a filler preceding another carriage control byte" |

Codes 224 and up "except for the SKIP TO RESTORE code, cause the
following byte to be interpreted as another carriage control byte",
and 224–239 "suppress post-spacing if printing is suppressed".

**IBM 7152 Operator's Console** (Reference Manual printed p.150, read
at 300 dpi; the console's section runs printed pp.149–156). Four
codes, and that is the whole CONTROL-instruction table:

| Octal | Function |
|---|---|
| 016 | Reserved Light Off |
| 017 | Reserved Light On |
| 116 | Check Light On — "These functions are standard" |
| 177 | **Sound Gong.** "This function causes a clearly audible gong to sound a single stroke." |

**The console redefines nothing; it OMITS two of the five standard
codes.** 057 and 157, the ECC-mode pair, do not appear in its table at
all — unlike the 729 IV, which takes 016, 057 and 157 and gives them
tape meanings. And 177 collides across devices with the tape's 177
Backspace File: same octal, different unit, which is the whole point
of a per-device table.

This is the second independent source for STRAP's `GONG` mnemonic
(X22-6533 page 4 lists it under INPUT-OUTPUT; C28-6129 Appendix B
calls it "Sound Gong"), and it agrees with MCP printed p.5 line 45,
which prints `000177` in the control-code field of a `GONG(SEOP)`.

Two details about SOUND GONG that a timing model needs, both printed
p.151: the end-of-operation indication "is given immediately upon the
initiation of the operation, even though the striking of the gong
takes place some time later", and back-to-back SOUND GONGs ring "at
its maximum rate of approximately once per second". A thirty-third
pluggable-exit output jack (printed p.152) "furnishes a momentary
current whenever the gong is sounded".

*Not transcribed:* the card punch's table (printed p.142). The MCP Reference's Appendix B (printed
pp.43–46) independently lists the I/O operations MCP itself issues, and
is a useful cross-check: Read, Write, Copy Control Word, Release, Locate
Arc, Feed Card, Tape Indicator Off, Erase Long Gap, Space Record,
Backspace Record, Space File, Backspace File, Write Tape Mark, Rewind,
Rewind and Unload, Reserve Light Off, Reserve Light On, Check Light On,
**Sound Gong**, High Density, Low Density, Even Parity No ECC, Odd
Parity No ECC, Error Checking and Correction, No Error Checking and
Correction. Note "Feed Card" and "Sound Gong" — codes for the reader/punch
and console that the Reference Manual pages I read do not name, and
"Locate Arc" for the disk.

### 3.7 `LOC` — what LOCATE actually does

Reference Manual p.111:

> "The selection address selects one unit among a set of units
> accommodated by a channel address. The selection addresses are
> assigned to a set of units independently of other such sets, usually
> as 0, 1, 2, 3, etc., and are specified by means of the right effective
> address of a LOCATE instruction. **All READ, WRITE and CONTROL
> instructions apply to units last selected by means of a LOCATE
> instruction.**"

p.120 places the field: three bits, bit positions 47–49 — eight units
per control unit, matching the 7613's eight tape drives.

Three consequences the model would have to absorb:

1. LOCATE makes the channel **stateful across instructions** in a way
   the model's one-device-per-channel shape currently avoids: each
   channel needs a "currently selected unit" register, and every
   subsequent RD/W/CTL has to route through it.
2. Status-bit attribution becomes per-unit: "If two or more units are
   accommodated by a single channel address… the status bits can be
   turned on only by that unit that has been last selected by means of a
   LOCATE. (The channel signal is an exception; it can be turned on by
   any unit.)" (p.113)
3. IPL only works from selection address 0: "a program can be loaded by
   the initial loading technique only from a unit having the selection
   address 0" (p.126), and a power-on/IPL reset forces "the control unit
   is reset to select the unit with the selection address 0" (p.125).

LOCATE is also not subject to UNRJ, and is the escape hatch for a busy
channel: "Certain operations, such as rewinding tape, may be completed
by the unit after disconnecting from the exchange. New instructions for
channels performing such operations can be accepted, provided another
unit is selected by means of a LOCATE instruction. In these cases CBJ is
not turned on." (p.112)

### 3.8 How a channel reports completion and error — the indicators

Two disjoint groups, and the distinction is load-bearing (Reference
Manual pp.112–113).

**Reject indicators** — the instruction was *never accepted*; the unit
is not started, the control word is not fetched, and the channel's
control-word location in exchange storage is not altered. Listed in
order of decreasing interruption priority:

| Ind. | Name | Cause |
|---|---|---|
| `EKJ` | Exchange Check Reject | "an error is detected by the exchange in the course of testing and setting up the present instruction" — equipment malfunction, parity error in the instruction word sent to the exchange, errors during the unit's status test; **or** "specification of channel addresses that are not available to the programmer. An unavailable channel is one that is not installed in the particular system… The test applies only to the 7-bit channel address portion of the left effective address, bit positions 12 through 18. The remaining bits of the field are ignored." |
| `UNRJ` | Unit Not Ready Reject | "an instruction is given to a channel that is not ready to be operated. The unit-ready status bit in the control word is zero. This happens when the unit accommodated by the channel is in the not-ready status **or no unit is attached to the channel**." |
| `CBJ` | Channel Busy Reject | "an instruction is addressed to a channel that is still busy performing a previous instruction or which is waiting to make a program interruption." |

> "The reject indicators have a mask bit that is permanently set to one.
> Consequently, if the program interruption system is enabled, any of
> the three reject indicators will always interrupt the program. This
> interruption occurs before the computer has proceeded to the next
> instruction."

> "If more than one condition exists that could reject an input-output
> instruction, only the reject having the higher priority is given. As
> an example, if an instruction is given to a channel which is not ready
> and is busy or waiting to make an interruption, only the UNRJ
> indicator is set up."

**Status indicators** — the instruction *was* accepted and has now
terminated. Also listed in decreasing interruption priority:

| Ind. | Name | Meaning |
|---|---|---|
| `EPGK` | Exchange Program Check | "turned on when an operation concerning an external unit is terminated prematurely by a programming error" — (1) an instruction the unit is not designed to perform, "such as a READ given to a printer"; (2) an undefined CONTROL code; (3) an instruction the unit cannot perform in its present condition, "e.g., a backspace CONTROL given to a tape unit with the tape at the load point"; (4) the exchange attempts to touch a core location it has no access to — "locations 0 through 31, or locations having addresses above the maximum available address in a particular installation". |
| `UK` | Unit Check | an uncorrectable data error at the unit. |
| `EE` | End Exception | the unit ran out of material / hit a tape mark / end-of-tape etc. |
| `EOP` | End Of Operation | the operation finished. |
| `CS` | Channel Signal | the unit rang its bell — operator pressed start/signal, or a secondary operation (rewind) completed. |

> "The input-output status indicators are permanent and their mask bits
> are permanently set to one." (p.113)

> "At the time of such an interruption, the channel address of the
> external unit is entered into the channel address register." (p.113)

And the ordering rule the model's header note already quotes correctly:
status is recorded in the control word *first*, and promoted to the
indicator register only when the interruption conditions are met.

**Two general (non-I/O-specific) indicators also fire on I/O
instructions** (Reference Manual p.111):

| Ind. | Name | On I/O |
|---|---|---|
| `EK` | Exchange Control Check | "the exchange has failed to function properly in a manner that cannot be identified with any particular channel. It usually signals the discovery of major control and addressing errors such as inserting a byte of data into another channel's control word. **The turning on of EK does not terminate the performance of the current input-output operations**, if any, in the exchange." |
| `AD` | Address Invalid | "turned on if the right effective address of a READ, WRITE or COPY CONTROL WORD is 0 through 31 or exceeds the largest address of main storage. When an error causing the AD indication is found, the processing of the instruction is terminated. The unit is never started and the contents of the channel's control word location in the exchange storage are not altered." |

A programming note on the same page is worth recording because it
contradicts a natural assumption: "**The data-store and data-fetch
indicators are never turned on by an input-output operation. Address
monitoring is not effective on input-output operations**, and data can
be read into and written from the protected core storage area as defined
by the upper and lower boundary registers… The exchange, however, cannot
transfer data to or from locations 0 through 31."

`CA`, the Channel Address register, is not an indicator: it is **word
address 5**, 7 bits at bit positions 12–18 (pp.111, 119).

The repo's `bsv/StretchTypes.bsv` already carries all eight numbers
(`ind_EK` = 3, `ind_EKJ` = 6, `ind_UNRJ` = 7, `ind_CBJ` = 8,
`ind_EPGK` = 9, `ind_UK` = 10, `ind_EE` = 11, `ind_EOP` = 12,
`ind_CS` = 13), sourced from C22-6531 Appendix A and cross-checked
against the jb_ax5b listing's 48-entry error tables. **Their relative
order 6,7,8 and 9,10,11,12,13 is exactly the two
"decreasing-interruption-priority" lists above** — an independent
confirmation of both the numbering and the priority rule that no one in
this project appears to have noticed yet.

### 3.9 Per-instruction response summary — Figure 40

Reference Manual **Figure 40, "Exchange Instruction Response", printed
p.123**, transcribed exactly:

| | Read / Write / Control | Locate | Release | Copy Control Word |
|---|---|---|---|---|
| **Reject indicators available:** | | | | |
| Exchange Check Reject | Yes | Yes | Yes | Yes |
| Unit Not Ready Reject | Yes | No | No | No |
| Channel Busy Reject | Yes | Yes | No | No |
| **Computer waits until end of operation** | No | No | No | **Yes** |
| **Status indicators available at the end of operation:** | | | | |
| Exchange Program Check | Yes | Yes | No | No |
| Unit Check | Yes | Yes | No | No |
| End Exception | Yes | No | No | No |
| End of Operation | Yes | Yes | Yes\* | No |

> "\* The End Of Operation is never turned on in a RELEASE SEOP
> instruction."
> "\*\* A Channel Signal indication can be caused by the program only
> upon the completion of tape rewinding (initiated by a CONTROL
> instruction)." — Channel Signal is otherwise "available at any time
> except when channel is in operation."

`CCW` is the only I/O instruction the CPU *blocks* on. "The COPY CONTROL
WORD is completed before the computer proceeds to the next instruction,
and no EOP indication is given" (p.122). It is also the only one that
can never set a status bit: "Since COPY CONTROL WORD by definition does
not affect the contents of the control word of the addressed channel, it
cannot cause any status bits or status indicators to be turned on. As a
result, all errors that preclude the completion of the COPY CONTROL WORD
are signalled by turning on the EKJ indicator" (p.122).

There is one genuinely nasty `CCW` restriction a model would have to
reproduce or document (p.122):

> "If a control word is to be interpreted as an instruction after it is
> brought from the exchange by COPY CONTROL WORD, it cannot be located in
> either of the two core storage words that are fetched by the
> instruction fetching mechanism immediately following the fetching of
> the COPY CONTROL WORD… The mechanism cannot… detect changes in these
> words caused by the exchange."

### 3.10 `REL` — forced termination

Reference Manual p.121. "The RELEASE instruction is accepted regardless
of the status of the unit-ready bit… The pertinent status bits in the
control word are reset to zero, and the EOP indication is immediately
turned on… The RELEASE instruction is not subject to channel busy
reject." `REL SEOP` "never causes any interruptions. It performs all the
functions of RELEASE except that it does not cause an EOP indication.
Thus, RELEASE SEOP can be used to turn off EPGK, UK, EE, CS as well as
any previously set EOP bits in the control word."

Buchholz's framing (printed p.253): "Occasionally it may be desirable to
force an input-output operation to come to a halt; for example, a
programming error may give rise to an endless control-word chain."

### 3.11 SEOP semantics

Reference Manual p.121:

> "At the time an SEOP instruction is given, the SEOP bit in the control
> word is set to one. As the result of this, the EOP bit in the control
> word (and therefore in the indicator register) is not turned on unless
> it is accompanied by unit check or end exception."

> "When an exceptional condition is discovered, as indicated by the
> presence of EPGK, UK or EE status bits, the interruption of the program
> is not suppressed. In this case, the status bit indicating the
> exceptional condition, as well as the EOP bit if the operation has been
> completed, are turned on, and program interruption is permitted."

> "Receipt of a channel signal during the execution of an SEOP
> instruction does not cause the EOP bit to be turned on. When the
> operation is completed, the CS indicator is set, but this does not have
> any effect on the turning on of the indicators pertaining to the SEOP
> operation."

### 3.12 Initial Program Loading — the whole sequence

This is how a deck gets into the machine with no program in memory, and
it is fully specified. Reference Manual pp.125–126.

Depressing the INITIAL PROGRAM LOAD key:

> "1. The execution of any program by the computer is terminated. 2. The
> interruption system is temporarily disabled. 3. All input-output
> operations on the exchange are terminated. 4. All control words in the
> exchange are reset to zero. 5. The exchange is set to interpret the
> next channel signal in a special way. 6. All input-output units are
> reset to 'initial power-on' status."

Then, on the first channel signal from any unit accommodated by the
exchange:

> "1. The exchange automatically stores in the control word location for
> the channel responsible for the channel signal a fixed control word
> with the following contents:
> Data word address = 4; Chain flag = 1; Multiple flag = 0; Skip flag =
> 0; Count = 1; Refill address = 4.
> 2. The exchange initiates a READ for the indicated channel, using the
> fixed control word.
> 3. The first word read from the unit is stored in the special core
> storage location referred to by means of address 4. Since the fixed
> control word is then exhausted, its refill address causes the next
> control word to be fetched from location 4. Location 4 at this time
> should contain another control word specifying the address at which
> the word immediately following should be stored, and the number of
> words to be read from the unit. Reading then proceeds normally.
> 4. If and when the READ operation is completed… the exchange sends an
> initial start signal to the computer…
> 5. The computer, upon receipt of the initial-start signal, fetches and
> executes the instruction in the location specified by the data word
> address field of the control word in core storage location 4. The
> address of this instruction, however, is not placed in the instruction
> counter."

> "As the result, the first instruction of a program loaded by means of
> the initial program loading technique must be BRANCH DISABLED."

That is a complete, testable specification — a bootstrap that needs
*no* instructions in memory, exactly what is wanted for "load a deck and
run". It also explains the Reference Manual's otherwise odd reservation
of word address 4 and the "loading is initiated by a channel signal"
shape of the whole I/O system.

### 3.13 The channel interface itself — the Bluespec interface, already drawn

`R23-9702_7503_Card_Rdr_7614_Rdr_Ctl_CE_1961.pdf`, **Figure 4.5-1
"Communication Lines", printed p.28**, draws every wire between the 7619
Exchange and a 7614 Card Reader Control. Because the interface is
deliberately uniform across all units (Buchholz §12.9, printed p.190:
"Input-output units, regardless of type, must be connected to their
exchange channels in the same manner, electrically and mechanically"),
**this figure is the generic channel interface** and is almost literally
a Bluespec `interface` declaration.

Exchange → control unit:

| Line | Meaning (R23-9702 p.27, p.29) |
|---|---|
| `Write (8)` | "Eight write lines are used to send information to the reader control during a control operation… These lines feed an eight-bit byte to the line register." |
| `Write Parity` | odd parity accompanying the 8 bits |
| `Byte Response` | "Used to inform the reader control that the exchange has recognized and honored a service request… during a read operation, indicates that a byte of data has been accepted by the exchange and the successive byte may be transmitted." |
| `Read Instruction` | "Initiates a read operation if the card reader is in a ready status and is not busy." |
| `Write Instruction` | signalled even where the unit cannot write (then → EPGK + EOM) |
| `Control Instruction` | "Starts a control operation to perform some desired function at the card reader." |
| `Locate Instruction` | signalled even where the unit cannot locate (then → EPGK + EOM) |
| `Disconnect` | "Is initiated at the exchange when the end-of-message (EOM) trigger is turned on at the reader control. The disconnect line resets triggers in the reader control… The disconnect line may be activated from the exchange before the EOM trigger is turned on… defined as an early disconnect. This early disconnect blocks further data transfer from the reader control to the exchange." |
| `−36 Volt` | power / CE test panel |

Control unit → Exchange:

| Line | Meaning |
|---|---|
| `Read (8)` | "Eight lines transmit the data bytes to the exchange during a read operation." |
| `Read Parity` | "Odd-parity checking is employed by all I-O devices for data transmission." |
| `Unit Check` | "indicates that an uncorrectable data error has occurred… The Unit check status bit is set in the control word in the exchange at the end of the current block of data." |
| `Ready` | "the card reader is loaded with cards and is in a status to accept a read or control instruction" |
| `Channel Signal` | "active when the reader is initially placed in a ready status or when the signal key is depressed" |
| `End Exception` | "active when the card reader stacker is full or when the reader runs out of cards… the end exception indication is not given until the data of the last card have been transmitted" |
| `Exch Prog Check` | "activated when a write or locate instruction is programmed to the card reader, or when the control code during a control operation is invalid" |
| `Ecc` | "active when the reader control is in ECC mode" |
| `Eom` (End of Message) | "the current operation (read or control) is terminated and… the reader control is to be disconnected from the exchange channel. Any unusual condition which turns on the cancel trigger… will also initiate the end-of-message. The exchange responds with a disconnect signal." |
| `Ser Req` (Service Request) | "Indicates to the exchange that a byte of data is on line ready to be accepted during a data transfer (read) operation. During a control operation, this line signifies that the reader control is ready to accept control information." |
| `Cancel` | "an unusual condition is recognized at the card reader or control unit such as card feed failure or circuit failure" |
| `Block Channel` | "Carries a −36v back to the exchange to block the channel… while the CE test panel is in use." |

This matches Buchholz's count exactly (printed p.190): "The interface
contains eighteen data lines (eight information-bit lines and a parity-bit
line in each direction), a timing line, and several more lines
corresponding to the instructions and indications referred to earlier."

**This is the single most valuable artefact in this study for
implementation purposes**: it means the Exchange and each device can be
built as separate Bluespec modules against a fixed, documented,
primary-sourced interface, and tested against each other independently
of the CPU.

---

## 4. Memory-cycle stealing, and what a second requester costs

### 4.1 Who arbitrates, and in what order

Two levels of priority, from two different documents, and they compose.

**Level 1, inside the Exchange** (Reference Manual p.111, quoted in full
in §1.3): lower channel address = higher priority, *both* for byte
service and for "the transmission of words of data between the exchange
and the core storage". Fixed, not rotating. The manual's rule for
assigning channel numbers makes the ordering meaningful: "the unit
having the highest byte and word weights has the lowest channel address
of the system, with the weights decreasing in the order of ascending
channel addresses" (p.105), and a violation costs you safety margin:
"If this sequence is violated, a unit's byte and word weights have to be
set equal to those of the unit having the largest weights at a higher
channel address" (p.106).

**Level 2, at the memory bus control unit** (Buchholz §14.3, printed
pp.205–206):

> "The memory bus unit monitors the requests for storing in or fetching
> from memory and sets up a priority scheme. **Since input-output units
> cannot hold up their requests, the exchange and disk synchronizer will
> get highest priority, followed by the CPU. In the CPU the operand-fetch
> mechanism, the look-ahead unit, has priority over the instruction-fetch
> mechanism. Altogether the memory bus unit receives requests from and
> assigns priority to eight different channels.**"

> "Since access to a memory unit can be independently initiated from
> several sources, a busy condition can exist. Here again, the memory bus
> tests for the busy conditions and delays the requesting unit until the
> desired memory unit is ready."

Buchholz §12.8 (printed p.188) gives the general rule and the reason:

> "Its use is time-shared automatically among the computer and the
> input-output channels by allocating memory cycles to each device when
> needed. **If more than one device demands attention, each is served in
> turn, with the highest priority assigned to the channel with the
> fastest input-output unit.**"

So: **fixed priority, not rotating.** Exchange and disk synchronizer
above the CPU; within the CPU, look-ahead above instruction fetch; within
the Exchange, lowest channel number first. `StretchMemory.bsv`'s header
already quotes the Buchholz passage and explicitly defers the scheme —
"the arbiter's eight-channel priority scheme becomes real when the
look-ahead and the exchange are separate requesters (plan stages 3 and
later)".

### 4.2 How often, in machine cycles

The time base `StretchMemory.bsv` already uses: 1 clock = 0.3 µs
(Performance Characteristics Vol.1 p.3-2), memory unit busy 7 clocks
(2.1 µs), read data at 5 clocks (~1.6 µs).

Three independent statements of the Exchange's main-memory demand, and
they agree:

1. Reference Manual p.105: "The communications between the exchange and
   core storage limit the maximum instantaneous information transmission
   rate of the exchange to **100,000 words per second**."
2. Reference Manual p.7: "The exchange as a whole can reach a peak rate
   of 100,000 words or 6,400,000 bits per second."
3. Performance Characteristics Vol.1 p.A-5: "Maximum word rate is **1
   extended word/10 µs for the entire exchange**."

100,000 words/s = one word per 10 µs = **one main-storage reference
every 33⅓ machine cycles, for the entire Exchange, across all 32
channels**. And Reference Manual p.119 confirms this is the *unit* of
Exchange↔storage work, not just an average: "each of the latter
functions occupies a 10-microsecond cycle" (referring to chaining and
to transmitting data words to or from core storage).

The disk synchronizer: one word per 8 µs = **one reference every 26⅔
machine cycles**, and only one disk at a time ever.

Worst case, both at full tilt: 1/33.3 + 1/26.7 ≈ **6.7 % of machine
cycles carry an I/O memory request.** Against six interleaved memory
units each capable of a request every 7 cycles, that is a 7-cycle
occupancy on one unit every 33 cycles from the Exchange — about 21 % of
one unit's capacity if every reference landed on the same unit, and
~3.5 % of the whole six-unit array's capacity since consecutive data
words step through consecutive interleaved units by construction.

IBM's own prediction (Performance Characteristics Vol.1 pp.3-16/3-17):

> "In actual computations, with the instructions occupying the two lower
> memory boxes and data occupying the four upper memory boxes, **memory
> conflict is not expected to be an important factor, even if the I/O
> units are in full operation. Delays due to repeated demands of the same
> memory box are expected to be quite infrequent.**"

### 4.3 Byte-level demand, and the weight system

Below the word level, the Exchange's own ES runs a 1 µs cycle per byte
per channel, and that load never touches main memory at all. It is
nonetheless the thing that limits how many channels can run at once, and
the manual gives the programmer an arithmetic for it (Reference Manual
p.105):

- **Byte weight**: fixed per unit type, "indicates the relative amount
  of exchange capacity which is necessary to service the unit. It depends
  upon the shortest interval in which the exchange may have to respond to
  the unit's byte request." Buffered units (card readers, punches,
  consoles, printers) have byte weight **zero** — they can be stalled
  without data loss. Non-buffered units (tape) have non-zero weights, and
  stalling one loses data and raises Unit Check.
- **Word weight** = **2560 / (T − 11)**, where T is the unit's minimum
  instantaneous word period in µs/word. "When a unit is engaged in chained
  reading or writing, its word weight has to be doubled."
- Either count reaching **256** is the maximum safe load.

The manual's own worked example (Figure-less table, p.106) is the best
single picture of a loaded machine:

| Type of unit | No. operating | Chaining? | Byte wt | Word wt | Byte count | Word count |
|---|---|---|---|---|---|---|
| 729 high dens. | 2 | no | 32 | 17 | 64 | 34 |
| 729 low dens. | 1 | yes | 9 | 6 | 9 | 12 |
| Card reader | 2 | no | 0 | 5 | 0 | 10 |
| Card punch | 1 | yes | 0 | 5 | 0 | 10 |
| Console | 1 | no | 0 | 3 | 0 | 3 |
| | | | | **Total** | **73** | **69** |

> "Both the byte and word weight counts are well below the maximum
> limits, and hence there is no danger of exceeding exchange capacity."

The formula checks out against the device chapter: a 729 IV at 556 bpi
has an "avg. word period" of 170 µs (Reference Manual p.130), and
2560/(170−11) = 16.1 → 17. At 200 bpi, T = 474 µs and 2560/(474−11) =
5.5 → 6. Both match the table. This is a closed-form device model: give a
simulated device its T and the weights follow.

Overrun behaviour is specified too (p.105): "Whenever the exchange
capacity to communicate with core storage is exceeded and a data word or
a control word is not transferred, a unit-check indication for that
channel is given." For zero-byte-weight units the consequence is merely
a stall: "their operation is interrupted. This interruption, however, is
not associated with any loss of information. As soon as the excess load
is removed and the exchange has time to spare, the mechanism of the unit
is automatically restarted and the original reading or writing operation
is continued. The interruption does not have any effect on the completion
of the operation, and no indication is given to the computer to this
effect."

### 4.4 What this costs `StretchMemory.bsv`

The file today: six `mkMemoryUnit`s with per-unit `busy`/`readDue`
counters, `unitOf`/`indexOf` interleave maps, a `RetTag` return-address
scheme with 7 tags (0 = operand channel, 1–2 = 1Y/2Y, 3–6 = look-ahead
levels), and **one requester**. The header says the eight-channel
priority scheme is deferred until the Exchange and look-ahead become
separate requesters.

Adding the Exchange is **a small, bounded change to that file**, and
that is the good news:

1. **Two more return tags.** Buchholz's "eight different channels" is
   already almost covered by `NumTags = 7`; the Exchange and the disk
   synchronizer are tags 7 and 8, taking `RetTag` to `Bit#(4)` and
   `NumTags` to 9. (The exact 8-way breakdown Buchholz counted is not
   stated anywhere I could find; §7 records this as an open question.
   What *is* stated is the ordering, which is what matters.)
2. **A real arbiter in front of the units.** Today's single requester
   needs no arbitration logic at all. The replacement is a fixed-priority
   select over the request wires in the documented order:
   `disk > exchange > look-ahead > instruction-fetch`, with the existing
   per-unit `free()` check as the second-level gate. That is one
   combinational priority encoder plus a register per requester to hold a
   waiting request, not a redesign — perhaps 60–100 lines.
3. **A throttle, not a flood.** The Exchange must not be able to request
   on every cycle: it is allowed one reference per 10 µs ≈ 33 clocks
   (disk: one per 8 µs ≈ 27 clocks). A small down-counter per DMA engine
   makes the stolen-cycle *pattern* correct, not just its average, which
   is the whole point under a cycle-accuracy goal.
4. **No change to the interleave map, the BRAM backing, or the timing
   constants.** An Exchange reference is an ordinary 2.1 µs unit cycle on
   whichever of the six units `unitOf(addr)` picks.

The observable effect on the CPU is exactly what Buchholz describes as
"the slight delays that may occur when the exchange requires a memory
cycle at the same time as the computer" (p.248) and the Reference Manual
as "the slight delay involved in the actual core storage references"
(p.104): a CPU request that collides with an in-flight Exchange access
on the same unit waits up to 7 clocks. Because the Exchange references
are periodic at ~33 clocks and the units are 6-way interleaved, the
resulting interference pattern is *deterministic and reproducible* given
the Exchange's start time and the address stream — which is precisely
what a cycle-accurate model needs. **The sources are sufficient to
reproduce the interference pattern, not merely its average**, provided
one accepts the 10 µs/8 µs reference periods as the rate and fixed
priority as the rule. What the sources do *not* give is the sub-cycle
phase relationship between the Exchange's own 1.x µs clock and the CPU's
0.3 µs clock (§7).

### 4.5 One project or two?

**The Exchange can be built and verified separately from the CPU**, and
should be. The evidence:

- Its interface to the units is a fixed, fully documented signal list
  (§3.13) that does not vary by device type.
- Its interface to the CPU is three values in and a small status out:
  channel address, operation, right effective address → accept/reject;
  then later an interrupt with a channel number and five status bits.
  Reference Manual p.104: "The only computer time involved is that needed
  to start and interlock the operations."
- Its interface to memory is a single word-address request port.
- Its internal state (ES: one control word + two data words per channel)
  and its arithmetic (control-word modification, byte shift, Figure 36)
  are entirely self-contained.
- It even has its own clock (Performance Characteristics p.A-5).

So the recommended shape is **two landings, one of them small**:

- **Landing A (large, independent):** `StretchExchange.bsv` plus one or
  more device modules, driven by a standalone testbench against a *stub*
  memory port. Verifiable on its own: Figure 36's 16 rows, the p.124
  terminal control-word arithmetic, the reject/status split of Figure 40,
  the IPL sequence of pp.125–126. None of this needs the CPU.
- **Landing B (small, coupled):** make the Exchange a second MBCU
  requester in `StretchMemory.bsv` (§4.4, items 1–3) and wire the
  accept/reject handshake and the interrupt into `StretchExecute.bsv` /
  `StretchCore.bsv`.

The cycle-accuracy goal is what forces Landing B to exist at all; without
it the Exchange would be a pure functional add-on. But B is genuinely
small, and A does not have to wait for it.

---

## 5. The minimum useful subset

### 5.1 What it is

**One card-reader channel, one printer channel, the console, and IPL.**
Concretely:

1. **An Exchange module** with ES modelled as a real per-channel array
   (control word + 2 data words × N channels), the channel-scanner
   priority rule, control-word modification every 8 bytes, and the
   Figure 36 termination table — but with only a handful of channels
   instantiated.
2. **Three devices behind the Figure 4.5-1 interface**: 7503 reader +
   7614 control (1000 cpm; a card is a 960-bit block = 15 words;
   `CTL` codes 016/017/057/116/157), 1403-2 printer + 7616 control
   (600 lpm; a line is ≤17 words preceded by a carriage control field;
   `CTL` codes 016/017/116), 7152 console + 7623 control (first three
   words of a READ come from the switches, the rest from the keyboard;
   first three words of a WRITE drive the lights and digital display,
   the rest print).
3. **IPL** (Reference Manual pp.125–126), which is what makes it a
   machine you can *use* rather than one you preload: press the key,
   press start on the reader, the fixed control word at address 4 reads
   one word, refills from 4, and the deck loads itself.
4. **Indicator and channel-address-register propagation** — the gap
   `StretchIO.bsv`'s own header calls out under "NOT PROPAGATED". Without
   it, `BI` (Branch on Indicator) and the `SIC`-based wait loops that
   every historical 7030 program uses cannot work, and `CCW` remains the
   only way to see status.
5. **The Exchange as a second memory requester** (§4.4) — needed for
   cycle accuracy, not for function.

### 5.2 What it leaves out, deliberately

- **The disk and the 7612 disk synchronizer.** Separate DMA engine,
  separate channel number range (0–31), arcs/tracks/access arms, 265 ms
  seeks, 39-bit bytes. This is its own project. **And it is what MCP
  needs** (§2.2) — so the minimum subset is explicitly *not* enough to
  run MCP.
- **Magnetic tape beyond what exists.** The 729 IV's full `CTL` table,
  tape marks, files, variable block lengths, density and parity modes,
  and the 7613's eight-drive multiplexing via `LOC`.
- **`LOC` and multi-unit channels** entirely (§3.7).
- **The card punch** (7553/7615).
- **Real byte-level timing.** A card reader at 1000 cpm and a printer at
  600 lpm (100 ms per line, of which only 8.5 ms is data transmission —
  Reference Manual Figure 45, p.149) are so slow relative to a 0.3 µs
  machine cycle that modelling them at word granularity loses nothing a
  program can observe. Tape and disk are different.
- **Error injection**: parity, ECC, unit check, the ECC/no-ECC modes.
- **Off-line operation** (Buchholz Figure 12.4, printed p.190: a reader
  and a tape unit wired to each other with no computer in between).

### 5.3 Does `io_reader_printer.strap` already exercise it?

**Partly, and it is a better starting point than its size suggests —
but it is not a test of an Exchange.**

What it already covers, against the right pages: `RD`, `W`, `CCW`, `REL`,
`W(SEOP)`, `REL(SEOP)`; the reject-vs-status split (channel 0 with no
device → `UNRJ`; `RD` to the printer → `EPGK`), which is exactly the
Figure 40 / pp.112–113 distinction; the SKIP flag on READ with sentinel
data that must survive; the control-word update arithmetic of p.124; and
the channel-address field at bits 12–18 reached through an index
register, which is the p.111 indexing rule. That is a real, discriminating
deck and the derivations in its header are correct.

What it does **not** exercise, and cannot without the work above:

- Any chaining or multiple-block operation — it never sets `chain` or
  `multiple`, so none of Figure 36's 16 rows past the two trivial ones
  is touched.
- Any count-exhaustion-versus-end-of-block distinction; there is no block
  concept in the model at all.
- Any indicator or channel-address-register propagation: every status
  check goes through `CCW`, by the model's own admission.
- Any concurrency. The model's transfer is synchronous: `StretchCore`'s
  `ioPending` FSM stalls the CPU for the whole transfer. The single
  defining property of the Exchange — that the program runs on while the
  transfer proceeds — is absent.
- Any arbitration, memory-cycle stealing, or device timing.
- IPL.

So: as a **regression oracle for the instruction-level semantics** it
survives the rewrite and should be kept and extended. As evidence that
the I/O system works, it covers the CPU-side instruction decode and the
control-word arithmetic, and nothing else.

---

## 6. Sizing

These are engineering estimates, **flagged as conjecture**: they are my
judgement from the documented behaviour and from the shape of the
existing modules, not measurements. Line counts are *code* lines in the
style of this repo (which runs roughly 1:3 code:comment).

### 6.1 Full subsystem

| Piece | Est. code lines | Basis |
|---|---|---|
| Exchange core: ES array, EMAR/scanner, byte shifter, control-word modification, refill | 400–600 | Figure 34's nine boxes; Figure 36's 16 rows; the p.124 arithmetic |
| Per-channel FSM: accept/reject, status accumulation, disconnect/EOM handshake, interrupt presentation + IAR busy interlock | 250–400 | §3.8, §3.13, Perf. Char. p.A-5 |
| Generic channel interface + adaptor plumbing | 80–150 | Figure 4.5-1 |
| 7503 + 7614 card reader | 150–250 | Ref. Man. pp.138–141; R23-9702 in CE detail |
| 1403-2 + 7616 printer (incl. carriage control field) | 150–250 | Ref. Man. pp.145–148 |
| 7152 + 7623 console | 200–350 | Ref. Man. pp.149–156; switches/keyboard/lights/display/printer are five sub-devices |
| 729 IV + 7613 tape control, full `CTL` table, tape marks, `LOC` for 8 drives | 400–600 | Ref. Man. pp.130–137 |
| 7553 + 7615 card punch | 150–250 | Ref. Man. pp.142–144 |
| 7612 disk synchronizer + disk storage (arcs, seek, 39-bit bytes, no chaining, no CCW-during-transfer) | 400–700 | Ref. Man. pp.157–162 |
| MBCU second/third requester + fixed-priority arbiter + DMA rate throttles | 60–120 | §4.4 |
| Indicator/CA-register propagation into the interrupt system | 100–200 | §3.8; depends on the interrupt system landing first |
| IPL sequence | 60–120 | Ref. Man. pp.125–126 |
| **Total** | **≈ 2,400–4,000** | |

Plus testbenches, generators and STRAP decks, which in this repo
historically run comparable to the model code.

The hard dependency nobody can estimate around: **the interrupt system**.
"All input-output operations are interlocked with the central program
interruption system" (Reference Manual p.111), and the Exchange's whole
completion path is an interrupt. The model's `StretchIO.bsv` header
already identifies this: propagation "needs the interrupt-enable state
this implementation doesn't model". If the interrupt system is not
already landing, it is a prerequisite, not a part of this estimate.

### 6.2 Minimum useful subset

| Piece | Est. code lines |
|---|---|
| Exchange core, reduced (no chaining initially, ES for 4 channels) | 250–400 |
| Per-channel FSM + accept/reject + status | 200–300 |
| Channel interface | 80–150 |
| 7503 + 7614 reader | 150–250 |
| 1403-2 + 7616 printer | 150–250 |
| 7152 + 7623 console | 200–350 |
| IPL | 60–120 |
| MBCU second requester + throttle | 60–120 |
| **Total** | **≈ 1,150–1,950** |

Against the 81 code lines in `StretchIO.bsv` today, the minimum subset is
roughly a 15–25× expansion of the I/O model. It is not a weekend, and it
is not months either — it is the same order as one of this project's
larger single milestones, with the important property that most of it can
be verified without the CPU (§4.5).

---

## 7. What the documents in `docs/` do **not** answer

Stated as bounded negatives. Each is something I looked for and could not
find in the sources available here, not something I declined to look up.

1. **The eight MBCU requester channels are never enumerated.** Buchholz
   says "the memory bus unit receives requests from and assigns priority
   to eight different channels" (p.205) and gives the *ordering*
   (exchange + disk synchronizer, then CPU; within the CPU, look-ahead
   over instruction fetch) but never lists the eight. Blosk's TR00.722
   p.19 (quoted in `StretchMemory.bsv`'s header) says the return address
   is three bits — consistent with eight — and names some of them for the
   I-unit, but the full mapping is not in any document I read. The model's
   existing 7-tag scheme is a reasonable reconstruction; the 8th is
   presumably the Exchange and the 9th the disk, which would need 4 bits,
   so either Blosk's three bits are per-unit rather than system-wide or
   the exchange/disk share a tag. **Unresolved.**

2. **The phase relationship between the Exchange's clock and the CPU's.**
   The Exchange "has its own clocking circuit (1.x µs cycles divided into
   10 equal pulses)" (Perf. Char. p.A-5 — the digit after "1." is
   illegible in the scan; from context and from the 1 µs ES cycle quoted
   by Buchholz it is most likely 1.0, but I am not asserting it) and the
   CPU runs on 0.3 µs cycles from a master oscillator. Buchholz p.204
   says "All the units of the computer are loosely coupled together, each
   one controlled by its own clock system, which in turn is synchronized
   by a master oscillator", but no document here gives the ratio or the
   synchronisation discipline. A cycle-accurate model must *choose* one.

3. **Exchange instruction acceptance latency.** "It usually must wait a
   few microseconds until the exchange has interrogated the status of the
   addressed unit" (Ref. Man. p.112) and "the computer may have to wait
   some microseconds" (p.104). No number. The Performance Characteristics
   volumes do not contain an I/O timing table at all — Vol.1 is CPU
   instruction timing plus Appendix A, and **Vol.2 is a set of benchmark
   program listings (GERB2, MXM16, PRIMC…) with no device data whatever**.
   Anyone needing a figure must either guess or find a document not in
   this repo.

4. **The 7619's internal cycle-by-cycle sequencing.** There is no 7619 CE
   manual in `docs/`. `R23-9702` documents the *card reader and its
   control unit* in CE detail (including the full interface, §3.13) but
   the Exchange side is a black box in it. The register list at Perf.
   Char. p.A-9 is the deepest internal view available here. A truly
   cycle-accurate Exchange would be reconstructed from its external
   timing contract (10 µs word cycles, 1 µs ES cycles, byte-weight
   arithmetic), not from logic diagrams.

5. **Which disk storage model number is correct** (§2.3): `A22-6552-1`
   says IBM 353, `R23-9702`'s system diagram says 7303. Not resolved.

6. **Card punch and operator's console `CTL` code tables** were not
   transcribed in this pass. They exist at Reference Manual pp.142–144
   and pp.149–156 respectively and should be straightforward; I ran out
   of budget, not sources. The printer's table (p.145) *was* read and
   p.146 confirms no continuation, but pp.147–148 were not read, so the
   claim "the printer has exactly three `CTL` codes" is near-certain
   rather than established (§3.6). The MCP Reference Appendix B (pp.43–46) names
   two codes — **Feed Card** and **Sound Gong** — that I did not find on
   the Reference Manual pages I read, so those tables may contain
   functions beyond the five standard codes.

7. **Byte weights for most devices.** The weight-count example (p.106)
   gives byte weights for the 729 at both densities (32 and 9) and
   confirms zero for reader/punch/console; the card reader's word weight
   of 5 is stated at p.138. I did not find a table of byte and word
   weights for every unit. The word weight is recoverable from the
   formula 2560/(T − 11) given each unit's minimum word period, which the
   device sections do give; the byte weight is not derivable and would
   have to be read off a table I did not locate.

8. **What happens on simultaneous main-memory requests from the Exchange
   and the disk synchronizer.** Buchholz lists them together as jointly
   highest priority (p.205) without ordering them against each other.
   Conjecture, flagged as such: the disk, being faster and unable to
   stall, almost certainly wins; but no document here says so.

9. **Whether anything in this repo's historical decks exercises
   chaining.** The diagnostic listings (`ka_ua1`, the `ja_`/`jb_` I-Box
   programs) use `%SEOP` and the channel primitives, per
   `docs/archival_inventory.md`, but I did not audit them for `chain`/
   `multiple` flag usage. If one of them does, it would be a far stronger
   oracle for Figure 36 than any purpose-written deck.
