# The IBM 7612 Disk Synchronizer and its disk storage

A document study, read-only, done to answer one question: **can the
7030's disk subsystem be modelled from the documents in `stretch/docs/`,
and is it the gate on running MCP?**

Both parts have an answer, and the second one is not the answer the
study was commissioned to confirm.

**Headline 1 — the documents are sufficient.** The Reference Manual's
"High-Speed Disk System" chapter, printed pp.157–162, is a complete,
self-contained, implementable specification: capacity, geometry,
addressing, every instruction with its bit positions, every indicator
with its causes, and every timing figure. Six pages. Nothing essential
is missing. The disk is in substantially *better* documentary shape than
the Exchange, which has no CE manual here at all.

**Headline 2 — the disk is not the boot gate.** The premise this study
started from — "MCP IPLs from disk, so no disk, no MCP" — is wrong, and
three independent primary sources say so. The 7030's hardware IPL
mechanism is structurally incapable of booting from a disk, and MCP's
own operating procedure confirms it: a cold start is a **tape** IPL.
What MCP needs the disk for is to *receive* a copy of the system tape
during initialization, and thereafter to serve as its program library.
That is a far weaker and far more bounded requirement than "boot from
disk", and it changes the build order. §5 has the detail.

Every figure below is attributed by printed page. Where I did not read a
page first-hand I say so. Where a document contradicts itself I report
both numbers and do not pick one. Conventions follow
`docs/exchange_and_io.md`: Reference Manual PDF page = printed page + 3,
and the `22-6530-2` scan has no text layer, so every Reference Manual
page cited here was read as a 300 dpi greyscale PNG. The MCP Reference
(`C22-6678-1`) also has no text layer; it was read at 200 dpi, and its
PDF page equals its printed page.

---

## 1. Is the disk on the Exchange? No — and a second source now says so

`docs/exchange_and_io.md` §1.4 asserted this from the Reference Manual
and the Performance Characteristics. Both are confirmed first-hand here,
and a third, independent, *pictorial* source has been added.

Reference Manual **printed p.157**, opening the chapter:

> "The high-speed disk storage system provided with the IBM 7030 is
> composed of the IBM 7612 Disk Synchronizer, which provides the common
> control and data transfer paths for the disk system and the computer,
> and the storage unit, which provides large capacity auxiliary storage
> to supplement internal core storage."

> "Basically, the method of control is the same as that used in the
> exchange. However, the high rate of data transmission between a disk
> storage and internal storage causes some differences in operational and
> program control."

Performance Characteristics Vol.1 **p.A-5** (this PDF *does* have a text
layer, so this is a literal extraction, not a transcription):

> "The disk exchange contains 32 channels (0-31), only one of which can
> be in operation at any given time. It contains enough memory for 1
> control word and 1 data word, and each channel can be attached to one
> disk unit. Disk word rate is 1 extended word/8 µs. No direct chaining
> of the I/O control words is permitted. In addition, the
> copy-control-word operation cannot be performed when reading or
> writing. Otherwise the disk exchange functions in much the same way as
> the exchange."

And the new one. `R23-9702_7503_Card_Rdr_7614_Rdr_Ctl_CE_1961.pdf`
**frontispiece** (PDF p.3, unnumbered; the preface on PDF p.4 calls it
"the frontispiece") is a block diagram of the whole machine. It draws:

```
   7303 Disk  <-->  7612 Disk      <-->  Storage Bus  <-->  7619      <-->  control units
   Storage          Synchronizer         Control            Exchange
```

The disk synchronizer attaches to **Storage Bus Control**, on the
opposite side of the machine from the 7619 Exchange, which attaches to
Storage Bus Control separately. The Exchange's eight drops go to the
7615/7553 punch, 7614/7503 reader, 7623/7152 console, 7616/1403-2
printer and 7613/729 IV tapes. The disk is not among them.

So the picture, the prose and the performance manual agree:

- **Channel addresses 0–31 are the disk synchronizer; 32–63 are the
  Exchange.**

Be precise about which half each source establishes. Performance
Characteristics p.A-5 states the lower half outright ("32 channels
(0-31)"), and Reference Manual p.157 plus the frontispiece corroborate it
structurally. The *upper* half is a different claim, and the Reference
Manual explicitly declines to make it: "the specific assignment of the
addresses is arbitrary and depends upon the specific units in an
installation" (p.111). What settles it is an operating procedure.
`C22-6678-1` **printed p.32**, listing the console binary keys that
select a dump's output device:

> "Key 44 — Printer; Key 45 — **CH 32, UN0** Unlabeled Tape; Key 46 — **CH
> 33, UN0** Unlabeled Tape; Key 47 — **CH 34, UN0** Unlabeled Tape"

Three real Exchange-attached tape units at channels 32, 33 and 34 on a
delivered, MCP-running machine. That is a primary source naming Exchange
channel numbers, and it starts at 32. It also independently vindicates
`bsv/StretchIO.bsv`'s existing choice of 32/33/34 for
reader/printer/tape, which until now rested on nothing.
- The disk synchronizer is a **second, parallel DMA engine** on the
  memory bus, not a channel of the first one.
- It is driven by the *same* I/O instructions — but not all six of them.
  See §3.

---

## 2. Capacity, geometry and addressing

### 2.1 The headline numbers

Reference Manual **printed p.157**:

> "The disk synchronizer has provision for addressing a maximum of 32
> disk storage units. Each disk unit has its own channel address.
> However, only a single data transmission channel is available because
> of the high data transfer rate. Therefore, only one disk at a time may
> be used for reading or writing. Concurrently, however, other disks can
> be accepting and processing instructions for setting the read-write
> heads in position for subsequent data transmission."

> "Each disk storage unit has a capacity of 2,097,152 (2²¹) words. Data
> may be transferred between the disk storage and core storage at an
> instantaneous rate of one full word every eight microseconds."

> "Each disk storage area is subdivided into 4096 (2¹²) addressable
> locations called arcs, consecutively numbered from 0 through 4095. An
> arc contains 512 words of information and is the smallest addressable
> unit in the disk system. Each disk unit contains a total of 512 tracks,
> and each track contains eight arcs."

4096 arcs × 512 words = 2,097,152 words. ✓  512 tracks × 8 arcs = 4096
arcs. ✓ The document is internally consistent on geometry.

> "Full words are transferred between the disk synchronizer and core
> storage. Each word consists of 64 information bits and eight error
> check and correction bits."

Note the asymmetry: **72 bits on the memory side, 78 bits on the platter
side** — the disk's own ECC is a different code from main memory's, and
the synchronizer regenerates between them (p.158, quoted in §2.4).

### 2.2 The physical arrangement

Reference Manual **printed p.157**:

> "Physically, a single disk unit contains 39 disks, coated with a
> magnetic material. These are mounted on a common shaft, and are used
> for data storage. Other disks on the same shaft are used for address
> and arc control, timing and other control purposes. Each information
> disk has two surfaces that are used for data storage. The total of 78
> disk faces is divided into two sets of 39 and each of these sets is
> equipped with 39 read-write heads. The 39 read-write heads are mounted
> on 20 access arms, which are on a common support. The set of heads and
> arms is called an access mechanism. All 39 heads move back and forth
> together during access motion to a track. One set of 39 faces contains
> all the odd-numbered tracks, the other set all even-numbered tracks.
> Thus, two consecutively numbered tracks are never located on the same
> set of disk faces. This arrangement makes it possible to position the
> heads of one access mechanism on the next track during the time the
> previous track is read or written."

This is the single most important structural fact for a faithful timing
model: **there are two access mechanisms per disk unit, one for
even-numbered tracks and one for odd**, and they leapfrog. Sequential
reading across a track boundary therefore costs no seek at all — the
other arm is already there.

And the byte format:

> "Data on the disk storage are handled in bytes of 39 bits each. These
> bytes are read or written in parallel by the set of 39 read-write
> heads common to an access mechanism… each 39 bit byte is composed of 32
> data bits and seven ECC bits… A 64-bit data word is divided into two
> bytes that are recorded on the disk storage in parallel columns 39 bits
> long and positioned in adjacent locations on the set of 39 disk faces."

So one 7030 word = two 39-bit disk bytes, written as two adjacent
39-bit-wide columns across the 39 faces. **One head per face, all 39
transferring in parallel** — this is a fixed-head-per-surface design with
a moving comb, not a serial-bit-stream disk.

### 2.3 The summary table, verbatim

Reference Manual **printed p.158**:

| Quantity | Printed value |
|---|---|
| Faces per disk storage | 78 |
| Tracks per set of 39 disk faces | 256 |
| Arcs per track | 8 |
| Data bits per byte | 32 |
| Bytes per word | 2 |
| Words per arc | 512 |
| Words per track | 4096 |
| Arcs per file | 4096 |
| Words per file | 2,097,512 (2²¹) |
| Maximum track access | 180 ms. |
| Maximum rotational access | 33.3 ms. |
| Data transfer to storage (instantaneous rate) | 8 microseconds/word |

Two printing problems in that table, both reported rather than silently
fixed:

1. **"Words per file 2,097,512 (2²¹)" is a typo.** 2²¹ = 2,097,152, which
   is what p.157 prints twice and what 4096 × 512 gives. The digits 1 and
   5 are transposed. The glyphs are unambiguous at 300 dpi; this is the
   manual's error, not the scan's.
2. **"Maximum track access 180 ms" contradicts p.157's 265 ms.** See
   §4.2. Not resolved.

"Tracks per set of 39 disk faces 256" × 2 sets = 512 tracks, agreeing
with p.157.

### 2.4 How a program addresses a disk location

**Geometrically, in one 12-bit field, and that is the only addressing
there is.** There is no flat word address and no cylinder/head/sector
triple. Reference Manual **printed p.160**, under LOCATE:

> "The right effective address, bit positions 32 through 49, of the
> instruction specifies the arc address. Positions 32-37 must be 0 bits
> while positions 38-49 specify the arc address."

and the programming note on **printed p.161**:

> "The arc address specified in the LOCATE instructions may be considered
> as having two parts:
> 1. Track address: high-order nine bits, bit positions 38 through 46.
> 2. Arc within track address: low-order three bits, bit positions 47
> through 49."

Nine bits of track (0–511) and three bits of arc-within-track (0–7). The
twelve bits together are the flat arc number 0–4095, and the split is
purely an interpretation aid: arc *n* lives on track ⌊n/8⌋ at position
*n* mod 8. Track parity (bit 46, the low bit of the track number) selects
which of the two access mechanisms is used — "Specification of the arc
automatically identifies the access mechanism to be used on that arc"
(p.161).

Within an arc there is **no addressing at all**: an arc is 512 words,
transferred from its start, and "is the smallest addressable unit in the
disk system" (p.157). Sub-arc granularity on *either* end is achieved
only by the control word's count field, and only at the tail:

> "The data read need not be a multiple of the number of words contained
> in an arc." (p.160, READ)

> "The data written need not be a multiple of the number of words
> contained in an arc. In this case, however, the remainder of the last
> arc will be automatically filled with zeros." (p.160, WRITE)

So a read of 100 words from arc 7 reads the first 100 words of arc 7; a
write of 100 words to arc 7 writes 100 words and **zeroes the remaining
412**. Read-modify-write within an arc is not a thing this hardware does.

### 2.5 The arc address register — the disk's implicit cursor

Reference Manual **printed p.161**:

> "Associated with each disk is an arc address register. As successive
> arcs are used, this register is increased by one for each arc. When
> required, the access mechanism will be automatically repositioned to
> the next higher track. Thus the alternating access mechanisms may
> provide continuous data flow."

This is the piece that makes the interface usable. LOCATE sets the
register; READ/WRITE consume arcs from it and advance it; crossing a
track boundary costs nothing because the other arm pre-positioned. A
program streams the whole 2,097,152-word volume with **one** LOCATE and
a sequence of READs.

> "Whenever successive arcs are to be read or written, only the initial
> arc need be specified." (p.161)

The register survives a Release, partially:

> "When a disk unit is released, the arc address register is left at the
> address of the last arc used unless transmission of that arc has been
> completed." (p.161)

---

## 3. The programming interface, completely

### 3.1 Five instructions, not six — and CONTROL is a program check

This is the first place the commissioning brief must be corrected. The
brief said "driven by the same six I/O instructions". The Reference
Manual says five, and names the sixth as an error.

**Printed p.160**, "Operations", transcribed exactly:

| Op | Name | Action | Control word? |
|---|---|---|---|
| `RD` | Read (SEOP) | Data from disk storage to core storage | yes |
| `W` | Write (SEOP) | Data from core storage to disk storage | yes |
| `LOC` | Locate (SEOP) | Set access mechanism to initial arc for later data transmission | no |
| `REL` | Release (SEOP) | Terminate data transmission immediately | no |
| `CCW` | Copy Control Word | Data word address field and word count field of control word to core storage | no |

and immediately after:

> "The CONTROL and CONTROL (SEOP) instructions have no meaning for disk
> storage and will set the EPGK indicator."

Independently, **printed p.159** lists as the first cause of Exchange
Program Check: *"1. A CONTROL has been issued to a disk storage."*

So the answer to "what `CTL` function codes does the disk have" is a
clean, doubly-sourced **none, and issuing one is a program check**. This
is not a gap in the documents; it is the specification. It also means the
whole per-device `CTL` code-table machinery that the tape and printer
need (`exchange_and_io.md` §3.6) is simply absent for the disk — one less
thing to build.

MCP's own list agrees. `C22-6678-1` Appendix B, **printed p.43**, gives
MCP's I/O macros and marks which devices can raise which status for each.
Disk appears under Read, Write, Copy Control Word, Release and **Locate
Arc** — and under no control-function entry anywhere in Appendix B
(pp.43–46, of which p.43 was read first-hand and pp.44–46 contain only
tape, reader, punch, console and printer functions by their contents
listing on printed p.4).

### 3.2 Field positions

Identical across RD, W and CCW (Reference Manual **printed pp.160–161**):

| Field | Bits | Meaning |
|---|---|---|
| Channel address | left effective address, **12–18** | which disk unit (0–31) |
| Core address of control word | right effective address, **32–49** | where the control word lives |

For `LOC`, the right effective address is not a core address but the
**arc address** itself, bits 38–49, with bits 32–37 required zero
(p.160). For `REL` there is no right-hand operand described at all:
"These instructions immediately terminate any data transmission operation
currently in process, at the disk unit specified by the channel address,
bit positions 12 through 18 of the left effective address" (p.161).

### 3.3 The control word — the same word, three quarters ignored

The disk uses the *same* 64-bit control-word layout the Exchange uses
(`exchange_and_io.md` §3.2, Reference Manual Figure 35, printed p.107:
bits 0–17 data word address, 18–24 status, 25–27 chain/multiple/skip
flags, 28–45 count, 46–63 refill). But Reference Manual **printed p.158**
says only two fields survive:

> "No use is made of control word flag bits or refill field and they are
> discarded after checking the control word error correction and check
> bits. Only the data word address field and word count field of the
> control word are retained and used by the disk synchronizer."

Restated for the implementer:

| Field | Disk behaviour |
|---|---|
| Data word address (0–17) | used |
| Status (18–24) | not an input; see below |
| Chain flag (25) | **discarded** — no chaining, ever |
| Multiple flag (26) | **discarded** |
| Skip flag (27) | **discarded** — no skip on the disk |
| Count (28–45) | used |
| Refill (46–63) | **discarded** |

That is a very large simplification against the Exchange. Figure 36's
sixteen-row multiple/chain termination table (`exchange_and_io.md` §3.3)
does not apply to the disk at all: a disk transfer runs until the count
reaches zero, full stop.

The count field's `0 means 2¹⁸` rule (Reference Manual p.123) is stated
for the Exchange and is not restated in the disk chapter. Since the disk
retains the count field unchanged and the field is the same field, the
rule presumably carries — but **the disk chapter does not say so**, so
treat it as unverified for the disk. (Not that it matters much in
practice: 2¹⁸ = 262,144 words is 512 arcs, 64 tracks, and 2.1 seconds of
transfer.)

Note what the disk does *not* have, Reference Manual **printed p.161**:

> "The disk synchronizer does not have control word storage as does the
> exchange. The data word address and word count fields are retained in
> registers in the disk synchronizer and are used to control core storage
> references. Since only one disk unit may transmit at a time, these
> registers are associated with the last channel which was performing a
> data transmission operation."

**One** DWA register and **one** count register for all 32 channels,
because only one channel can transmit. This is what Performance
Characteristics p.A-5 means by "enough memory for 1 control word and 1
data word". It is a wholly different structure from the Exchange's
3-words-per-channel Exchange Storage array.

### 3.4 `LOC` — on a disk it is a seek, not a unit selection

This is the single largest semantic difference between the disk and
everything else on the machine, and the brief was right to single it out.

On the Exchange, `LOCATE`'s right effective address is a **selection
address**: it picks one of up to eight units (e.g. tape drives) sharing a
control unit, and "All READ, WRITE and CONTROL instructions apply to
units last selected by means of a LOCATE instruction" (Reference Manual
p.111).

On the disk, `LOCATE`'s right effective address is an **arc address**,
and the instruction is a seek. Reference Manual **printed p.160–161**:

> "These operations are used to initiate setting of the access mechanism
> to the track which contains the specified arc."

> "Specification of the arc automatically identifies the access mechanism
> to be used on that arc. These instructions cause the proper access
> mechanism of the pair attached to each disk storage to be positioned at
> the track containing the specified arc. Concurrently, the other access
> mechanism is positioned on the track immediately following the
> specified track. When both access mechanisms have been positioned, an
> EOP indication is given. The starting arc within the track is retained
> within the disk unit."

Three consequences, all of them load-bearing for a model:

1. **One LOCATE moves both arms.** The addressed one to the target track,
   the other to target+1. EOP comes only when *both* are in position.
2. **LOCATE is the disk's only concurrency.** "A LOCATE or LOCATE SEOP
   may be given to any disk attached to the data synchronizer at any time
   if the disk specified is not busy with data transmission or a prior
   LOCATE" (p.161). This is the one thing 32 disks can do simultaneously,
   and it is explicitly why they can: p.157's "Concurrently, however,
   other disks can be accepting and processing instructions for setting
   the read-write heads in position".
3. **LOCATE is what makes the disk random-access.** "Because of these
   instructions, the disk units are randomly addressable by arc" (p.161).

There is **no selection address on the disk** — "Each disk unit has its
own channel address" (p.157), one unit per channel. So the Exchange's
whole channel → selection-address → unit hierarchy, and its per-unit
status attribution rules (Reference Manual p.113), do not exist here.
The model's current one-device-per-channel shape is, for the disk, exactly
right.

Note also, p.161, that the disk's `LOCATE` breaks one Exchange rule:

> "If the disk unit is not ready, the disk system will not accept the
> instruction. Instead, the unit-not-ready-reject indicator is turned on.
> **In this respect these operations are different from the exchange.**"

(On the Exchange, LOCATE is the escape hatch that is *not* subject to the
reject interlocks — Reference Manual p.112. On the disk it is subject to
UNRJ like everything else.)

### 3.5 `REL` — forced termination, with a zero-fill side effect

Reference Manual **printed p.161**:

> "When a disk unit is released, the arc address register is left at the
> address of the last arc used unless transmission of that arc has been
> completed. If the disk unit was writing, the remainder of the arc, in
> which the RELEASE operation was accepted, will have zeros recorded. A
> LOCATE operation will proceed to its normal end and the arc address
> register will be set as specified."

> "RELEASE SEOP differs from RELEASE in that the EOP indication will be
> suppressed when the operation is completed normally. This instruction
> resets all status indications during its execution."

Indicators for REL: **UNRJ and EOP only** (p.161). Not EKJ, not CBJ, not
EPGK, not UK. REL is the one instruction you can always issue.

Note the asymmetry: REL aborts a transfer but **cannot abort a LOCATE** —
the seek runs to completion and the arc register ends up where the LOCATE
said. That is implementable but easy to get wrong.

### 3.6 `CCW` — readable only when idle, and it returns no EOP

Reference Manual **printed p.161**:

> "Since the execution of a COPY CONTROL WORD instruction uses the
> transmission channel of the disk synchronizer, the instruction is not
> executed when a disk storage is reading or writing, and the
> channel-busy indicator will be turned on."

> "The normal completion of this instruction will not give an EOP
> indication, since when this instruction is used with the disk system it
> must be completed before the computer proceeds with the next
> instruction."

So `CCW` on the disk is **synchronous** — the CPU stalls, there is no
interrupt, and there is no EOP. The contents placed in core are "the data
word address and word count fields… placed in a full-word format,
corresponding to their location in a control word" (p.161) — i.e. a
control word with bits 18–27 and 46–63 presumably zero or undefined; the
manual does not say what those bits contain, which is a real gap (§7.3).

Indicators for CCW: **EKJ, CBJ, UNRJ, AD** (p.161). Notably *not* EPGK,
not UK, not EOP.

### 3.7 SEOP

Uniform and dull, which is good news. For RD, W, LOC and REL, "SEOP
differs… in that the EOP indication will be suppressed when the operation
is completed normally. Otherwise they are the same" (pp.160–161). `CCW`
has no SEOP variant on the disk (there is no EOP to suppress).

One exception, **printed p.159**: EOP "will be set for all instructions
except COPY CONTROL WORD and those instructions specifying SEOP. In this
latter case, however, **the suppression is ignored if a unit-check is
also turned on and the operation is completed**."

### 3.8 The indicators, with every documented cause

Reference Manual **printed pp.158–159**. Seven indicators; the per-op
applicability is from pp.160–161.

| Indicator | RD/W | LOC | REL | CCW |
|---|:-:|:-:|:-:|:-:|
| `EKJ` Exchange Check Reject | ✓ | ✓ | | ✓ |
| `CBJ` Channel Busy Reject | ✓ | ✓ | | ✓ |
| `UNRJ` Unit Not Ready Reject | ✓ | ✓ | ✓ | ✓ |
| `EPGK` Exchange Program Check | ✓ | ✓ | | |
| `UK` Unit Check | ✓ | ✓ | | |
| `EOP` End of Operation | ✓ | ✓ | ✓ | |
| `AD` Address Invalid | ✓ | | | ✓ |

**`AD` — Address Invalid** (p.158):

> "The purpose of this indicator, when on in conjunction with
> input-output instructions, signals that the right effective address of
> a READ, WRITE, or COPY CONTROL WORD instruction is 0 through 31. When an
> error is found which turns on this indicator, the processing of the
> instruction is terminated in the CPU."

Core addresses 0–31 are the 7030's register addresses; pointing a control
word at one is an addressing error caught in the CPU, before the disk
sees the instruction. Independently corroborated by EPGK cause 2 below,
which calls 0–31 "locations to which [the DS] does not have access".

**`EKJ` — Exchange Check Reject** (pp.158–159). Three documented causes:

1. "Parity errors in the information contained in…" *(the sentence
   continues onto p.159's left column, which opens at cause 2; the tail
   of cause 1 is in the p.158 right column and reads "…the information
   contained in" with the continuation on p.159 beginning "2.". The
   object of cause 1 is therefore cut between columns and I did not
   recover it. Treat cause 1 as "a parity error in the instruction
   information sent to the disk system", by analogy with the Exchange's
   identically-worded EKJ at p.112, flagged as inference.)*
2. "Specification of disk storage or channel addresses that are not
   available to the programmer. This includes uninstalled channels or
   channels that are not operative because no disk storage has been
   provided for them. When a disk storage is temporarily physically
   disconnected from the disk synchronizer, the channel will be in a
   not-ready status and the disk synchronizer will not set the
   exchange-check-reject indicator."
3. "An attempt is made to locate to or process data to or from a disk arc
   with an arc address greater than 4095."

**`UNRJ`** (p.159): "turned on when an instruction is given to a disk
storage that is not ready to be operated. This is usually caused when a
disk storage is temporarily disconnected from its channel."

**`CBJ`** (p.159) — and this one is *richer* on the disk than on the
Exchange, because of the one-transfer-at-a-time rule:

> "Because of the restrictions on addressing and simultaneous operation
> of disk storage, this indicator can be turned on by a number of
> conditions that do not exist in the exchange. The conditions which can
> be responsible for channel-busy-reject in the disk synchronizer are:
> 1. A READ, WRITE or LOCATE instruction is addressed to a disk which is
> executing a previous instruction, or is waiting to make a program
> interruption.
> 2. A READ or WRITE instruction is addressed to a disk storage at a time
> when **some other** disk storage is engaged in a reading or writing
> operation.
> 3. A COPY CONTROL WORD instruction is issued at a time when a disk unit
> is engaged in reading or writing."

Cause 2 is the global interlock. It is the thing a model will get wrong
if it treats the 32 channels as independent.

**`EPGK` — Exchange Program Check** (p.159). Three causes:

1. "A CONTROL has been issued to a disk storage."
2. "The DS attempts to transfer a word to or from a core storage location
   to which it does not have access (locations 0 through 31 or in
   locations above the maximum address available in core storage). In the
   case of a WRITE instruction to the disk unit with a data word address
   too high, the DS writes zeros in the arc specified in the locate
   register. The EPGK indicator is delayed until the write zeros operation
   is completed."
3. "A nonexistent disk address is encountered by attempting to read or
   write beyond arc 4095."

With the timing caveat that matters for interrupt modelling:

> "Programming errors indicated above are detected after the instruction
> is sent to the disk system. The EPGK indicator is set soon after the
> instruction has been accepted by the disk synchronizer. However, by the
> time an interruption can be made, the computer has proceeded with its
> instruction sequence. The specified disk storage will not perform the
> instruction."

> "The EPGK indicator is set, by invalid address detection, when an
> attempt is made to transfer a word to or from the location specified by
> the invalid address. The operation proceeds normally until the invalid
> address is detected."

Note the distinction between EKJ cause 3 (an arc address > 4095 given to
a LOCATE or at instruction setup — a *reject*, nothing happens) and EPGK
cause 3 (running *off the end* past arc 4095 during a transfer — a
*program check*, and the part before the end did happen). Two different
indicators for two different moments.

**`UK` — Unit Check** (p.159), in two classes:

> "1. Those errors which cause immediate termination of the instruction
> and immediate interruption. These errors are developed by malfunctioning
> of the disk storage and the disk synchronizer.
> 2. Those errors which permit the operation to be completed. These errors
> include uncorrectable data and addressing parity errors. This class of
> errors will set the UK and EOP indicator bits."

**`EOP`** (p.159): "When this indicator is turned on and no other check
interruption occurs, it indicates that the instruction has been completed
successfully."

**Status timing**, p.159, which a model must honour:

> "Status information can occur prior to, during or subsequent to data
> transmission. Certain checks that occur while data transmission is in
> progress are held up in the disk synchronizer or disk storage until the
> end-of-operation is signalled. Other checks can cause immediate
> termination of the instruction being executed."

> "Each channel will retain the status bits associated with termination of
> the last instruction executed or attempted by the channel or disk
> synchronizer until the priority sequencing controls permit it to
> interrupt in the central processing unit."

**There is no Channel Signal (CS) on the disk.** CS does not appear in any
of the five instructions' indicator lists on pp.160–161, and p.159's "Keys
and Lights" says "A disk file switch turns the 60-cycle power on and off…
The disk units do not require operator access, and can be installed
outside of the operating area." No Signal key, no Start key, no operator
panel. This is not a small detail — see §5.1.

**There is no End Exception (EE) on the disk** either; it appears in no
indicator list on pp.160–161. The disk never runs out of material.

### 3.9 Automatic Access Elimination

Reference Manual **printed p.162**, the chapter's last page. This is a
latency optimisation with an observable side effect, and it is worth
understanding precisely because *for data placement it is transparent*
and therefore need not be modelled for functional correctness.

> "This feature of the disk system provides an automatic method for
> minimizing rotational access time when full tracks of information are
> to be read or written. On the average the effective access time is
> reduced by a factor of eight."

The synchronizer tests three conditions on **each** read or write:

> "1. The arc address at the disk file must have the three low-order bit
> positions equal to zero. That is, the arc address must specify arc 0 of
> this track.
> 2. The twelve low-order bits of the data word address field of the
> control word must be zero. Thus the data read or written will be stored
> or obtained from core storage locations starting with address 4096 or a
> multiple of 4096.
> 3. The word count field of the control word must be 4096. Therefore,
> only one track of information can be transferred with automatic access
> elimination."

and then:

> "If these three conditions are satisfied, the disk begins transmission
> operations at the start of the next arc it senses. The data word address
> is automatically adjusted to correspond to this arc's data address.
> Transmission continues from this point until transmission associated
> with arc 7 of this track has been completed. The data word address is
> then automatically adjusted to the initial data word address and
> transmission continues with arc 0 until the starting point is reached,
> i.e., 4096 words have been transmitted."

> "When successive tracks are to be read or written an automatic
> adjustment of the arc address is made to its next track and transmission
> continues. At the completion of data transmission the arc address
> register will be left at arc zero (0) of the next sequential track if
> the operation was terminated at sector 8."

> "The data word address register contains the core storage location of
> the last word read, which depends on the sector in which the read
> operation started."

**For the model this means:** the resulting core image is *identical* to a
plain in-order transfer, because the DWA is re-adjusted per arc so each
arc lands at its own fixed offset. A model that always starts at arc 0
with zero rotational latency produces bit-for-bit the same memory
contents. AAE is therefore **not needed for functional correctness** —
only for timing, and for one observable: the **DWA register left behind
and readable by `CCW`** depends on where the rotation happened to be, and
is therefore genuinely nondeterministic on real hardware. A program that
reads it back after an AAE transfer is reading a physical accident.

The condition-3 wording "the word count field must be 4096" is worth a
caution: 4096 is a legal literal count, distinct from the count-zero
convention, so this needs no special-casing.

---

## 4. Timing

### 4.1 Transfer rate — one number, unambiguous, three sources

**8 µs per 64-bit word**, from Reference Manual p.157 ("an instantaneous
rate of one full word every eight microseconds"), p.158's summary table
("Data transfer to storage (instantaneous rate) 8 microseconds/word"),
and Performance Characteristics p.A-5 ("Disk word rate is 1 extended
word/8 µs"). Reference Manual Figure 1 (printed p.6) also labels the disk
"2,097,152 Words 125,000 Words/sec", and 1/8 µs = 125,000 words/s exactly.

In machine cycles: the 7030 CPU cycle is 0.3 µs, so **one memory
reference every 26⅔ cycles** per `exchange_and_io.md` §4.2 — a very low
duty cycle on the memory bus, but an *unstallable* one. Note that the
disk is the fastest single requester on the bus (the whole Exchange
manages only one word per 10 µs, Performance Characteristics p.A-5) and
is the one that cannot be held up.

*Derived, flagged as my arithmetic, not the manual's:* 512 words/arc ×
8 µs = 4.096 ms of data per arc, against a revolution of 33.3 ms / 8 arcs
= 4.16 ms per arc slot. The data occupies 98.4% of the arc slot, leaving
~1.6% (about 64 µs) of inter-arc gap. So 8 µs/word is very nearly the
sustained rate within a track, not merely an instantaneous peak. Also
derived: 33.3 ms per revolution = **1800 rpm**.

### 4.2 Seek — piecewise, three points, and one unresolved conflict

The documents give **no formula and no distribution**. They give three
specific numbers, and they contradict themselves on the largest.

Reference Manual **printed p.157**:

> "Positioning of the arms under program control requires a maximum of 265
> milliseconds (ms.) when the arms are moved from the outermost to the
> innermost track."

Reference Manual **printed p.158**, continuing the same sentence from the
previous page:

> "Moving sequentially from one track to the next track, however, requires
> 51 ms. provided the tracks are in the same group of 16. Moving
> sequentially from the last track in one 16 group to the first track of
> the next 16 group, requires 117 ms."

| Motion | Time | Source |
|---|---|---|
| Within a group of 16 tracks, one track | 51 ms | p.158 |
| Last track of a 16-group → first of the next | 117 ms | p.158 |
| Outermost → innermost (full stroke) | **265 ms** | p.157 |
| "Maximum track access" | **180 ms** | p.158 summary table |

**265 ms and 180 ms cannot both be the maximum.** They are two pages
apart in the same manual, in the same chapter, on the same quantity. I
have not resolved this and I am not guessing. Nothing in the chapter
reconciles them, and no other document in `docs/` gives a disk seek time
at all (Performance Characteristics Vol.1 mentions the disk only at p.A-5
and in the test-program list; Vol.2 is benchmark listings with no device
data — `exchange_and_io.md` §7.3 established that).

Two readings are *available* and neither is supported: that 265 ms is
worst-case over all possible arm motions while 180 ms is a specification
limit for a single access command; or that one of the two is a revision
artefact between the manual's printings. A cycle-accurate model must
choose, and should say which it chose and why, in a comment.

The "group of 16" structure is itself significant and unexplained. The
arms evidently detent into 32 groups of 16 tracks (512/16), with a large
penalty — 117 ms versus 51 ms, a 2.3× step — for crossing a group
boundary. No document here explains the mechanism. For a model, the
honest three-case function is:

```
seek(from_track, to_track):
    if from_track == to_track:                      0
    elif |Δ| == 1 and same group of 16:            51 ms
    elif adjacent 16-groups, sequential:          117 ms
    else:                        unspecified, ≤ 265 (or 180) ms
```

and the last line is the one the documents do not fill in. Any
interpolation across it is invention.

Remember §2.2: **sequential forward reading pays no seek at all**, because
the other arm pre-positions. The 51 ms figure applies to a *programmed*
LOCATE to the adjacent track, not to streaming.

### 4.3 Rotational latency — and the second conflict, which arithmetic settles

Reference Manual **printed p.158**:

> "After the access mechanism is first positioned, a rotational delay may
> be expected when a reading or writing operation is started. This may
> take a maximum of 34 ms. although an average of 17 ms. may be expected.
> If certain conditions of addressing and data block length are met, the
> rotational delay is reduced to a maximum of 4.2 ms. and an average of
> 2.1 ms. This feature is called 'automatic access elimination.'"

against the same page's table: "Maximum rotational access 33.3 ms."

Here arithmetic discriminates, and I flag the reasoning as mine:

- 33.3 / 8 = 4.16, matching the printed AAE maximum of 4.2 ms.
- 33.3 / 2 = 16.65, matching the printed average of 17 ms.
- 4.16 / 2 = 2.08, matching the printed AAE average of 2.1 ms.
- 34 / 8 = 4.25 and 34 / 2 = 17, which also round acceptably.

**33.3 ms is the self-consistent value**; 34 ms reads as prose rounding of
the same quantity. 33.3 ms also gives the clean 1800 rpm. I would model
33.3 ms and note the 34 ms text. This is a far softer conflict than the
seek one — the two numbers are 2% apart and describe the same thing — and
unlike the 265/180 conflict it does not need to be left open.

Summary of the latency model the documents support:

| Phase | Max | Average | Source |
|---|---|---|---|
| Seek, one track in group | 51 ms | — | p.158 |
| Seek, crossing 16-group | 117 ms | — | p.158 |
| Seek, full stroke | 265 ms / 180 ms (conflict) | — | pp.157, 158 |
| Rotational, normal | 33.3 ms (text: 34) | 17 ms | p.158 |
| Rotational, with AAE | 4.2 ms | 2.1 ms | p.158 |
| Transfer | 8 µs/word | — | pp.157, 158, A-5 |

**Are these distributions or fixed numbers?** Mixed, and the brief was
right to ask. The seek figures are *fixed* numbers for specific motions
with the full-stroke case unspecified in between. The rotational figures
are explicitly a *distribution* — the manual gives both a maximum and an
average and nothing else, which is exactly what you get from a uniform
distribution over one revolution. A model wanting determinism should use
the average and say so; a model wanting realism should sample uniformly
on [0, 33.3 ms) (or [0, 4.16 ms) under AAE) and will then have a
reproducibility problem, because the AAE case leaves an
observable-by-`CCW` DWA that depends on the sample (§3.9).

---

## 5. What MCP actually does with the disk

### 5.1 MCP does **not** IPL from the disk — three sources

This is the most important finding in the study, and it inverts the
premise the study was commissioned on.

**First: the hardware IPL mechanism is exchange-only, by construction.**
Reference Manual **printed p.126**, read first-hand:

> "The first channel signal indication received after the depression of
> the INITIAL PROGRAM LOAD key **from a unit accommodated by the
> exchange** initiates the following sequence of events:
> 1. The exchange automatically stores in the control word location for
> the channel responsible for the channel signal a fixed control word with
> the following contents:
> Data word address = 4; Chain flag = 1; Multiple flag = 0; Skip flag = 0;
> Count = 1; Refill address = 4.
> 2. The exchange initiates a READ for the indicated channel, using the
> fixed control word.
> 3. The first word read from the unit is stored in the special core
> storage location referred to by means of address 4. Since the fixed
> control word is then exhausted, its refill address causes the next
> control word to be fetched from location 4…"

Every single element of that sequence is something the disk cannot do:

| IPL step requires | Disk reality | Source |
|---|---|---|
| a **channel signal** from the unit | the disk has no CS indicator and no Signal key *(weakest of the four — see below)* | pp.159–161 |
| a **unit accommodated by the exchange** | the disk is on Storage Bus Control, not the Exchange | p.157; R23-9702 frontispiece |
| storing a fixed CW in **the channel's control word location** | "The disk synchronizer does not have control word storage as does the exchange" | p.161 |
| **Chain flag = 1** | "No use is made of control word flag bits… they are discarded" | p.158 |
| **Refill address = 4** to fetch the second CW | "No use is made of… refill field" | p.158 |

Four blockers, and the conclusion does not rest on all four. **The first
is the weakest and the argument does not need it:** MCP Reference p.43
prints "`CS  $LOC completed`" for the disk's Locate Arc, which I believe
is a misprint for EOP but have not resolved (§5.3). Set that row aside
entirely and the remaining three each independently kill the IPL path:

- p.126 requires the signalling unit to be **"accommodated by the
  exchange"**, and the disk is on Storage Bus Control (§1);
- p.126 step 1 stores the fixed control word **"in the control word
  location for the channel"**, and p.161 says flatly that the disk
  synchronizer has no control word storage;
- p.126's fixed control word has **chain flag = 1 and refill address =
  4**, and the entire bootstrap turns on the refill fetching the second
  control word from location 4 — both fields that p.158 says the disk
  "discards after checking the control word error correction and check
  bits".

Any one of those three ends it. The disk chapter (pp.157–162, read in
full) never mentions initial program loading at all.

**Second: MCP's own cold-start procedure is a tape IPL.** `C22-6678-1`
**printed p.29**, "Initializing the System":

> "At the time of initialization, the minimum machine configuration is
> assumed to be available. Basically, the initialization program reads the
> MCP portion of the master system tape into core storage and **writes a
> copy of the entire tape on the disk in the PROSA area**."

The accompanying figure draws it: *Master System Tape* → *Initialization
Program* → *MCP in Core Storage* and → *Entire System on Disk Storage*.
Arrows point **into** the disk. The procedure:

> "Input: The current MCP master system tape is file protected and mounted
> on any tape unit dialed to zero. Density for this unit is set to HIGH
> and the unit is made READY."
> "Procedure: … 3. Press IPL key. 4. **Press Signal key on the adapter
> unit for the channel on which the master system tape is mounted.**"

"Mounted on any tape unit dialed to zero" satisfies Reference Manual
p.126's "only from a unit having the selection address 0"; pressing the
Signal key on the tape adapter is exactly the channel signal p.126 waits
for. This is the Exchange IPL, from tape, exactly as specified.

**Third: "Disk IPL" is a card deck, and is a shortcut, not the primary
path.** `C22-6678-1` **printed p.32**:

> "The Disk IPL program can be used to reinitialize the system quickly,
> and eliminate the need for the master system tape **once there has been
> a successful IPL**."
> "Procedure: 1. Press the IPL key. 2. Set up the IPL options as explained
> in 'Initializing the System.' **3. Put the binary deck of the Disk IPL
> program in the card reader.** … 4. Ready the card reader."

So "Disk IPL" is: hardware-IPL a card deck from the 7503 card reader; the
deck then reads the system back out of the disk's PROSA area. The disk is
the *source of the system image*, never the source of the first
instruction. And the same page's note settles the terminology:

> "Note: In this section, the initials IPL represent the entire initial
> program loading procedure. A successful IPL involves placing MCP in core
> storage and writing a copy of the entire master system tape on the disk
> in the PROSA area."

Its failure path is explicit, twice:

> "This means that the disk is contaminated, so the program halts and the
> system must be rewritten on the disk by a **tape IPL**."
> "If any error interrupts occur, or the disk dictionary is incorrect,
> message 2 is given and the program halts. The system must be
> reinitialized by a **tape IPL**."

Tape IPL is the ground truth; Disk IPL is a fast path that falls back to
it.

**Conclusion.** MCP's minimum configuration *does* require the disk
(`C22-6678-1` printed p.6, verified first-hand: "An IBM 7612 Disk
Synchronizer with at least one disk unit used to store system programs
and as auxiliary storage for the problem program", and the disk is not on
the same page's list of five things the system can survive without). But
it requires it as a **writable store that initialization fills and the
running system reads back**, not as a boot device. The brief's framing —
"no disk, no MCP" — is right in the end but for a different reason, and
the different reason makes the first milestone much smaller.

### 5.2 What MCP keeps on the disk: PROSA, a program library

`C22-6678-1` **printed p.6**, in the overview:

> "The system I/O includes input, output, **disk fetching of prestored
> routines**, and console typewriter facilities."

`C22-6678-1` **printed p.40**, "Updating the System":

> "A program called UPDATE 30 is available to facilitate the incorporation
> of changes into the current system **located in the PROSA area of the
> disk**."

and the same page's figure: *Disk / PROSA* → *UPDATE 30 Program* ← *
Changes*, producing a *New Master System Tape* and a *PROSA Listing*. The
same page lists the type-areas the MCP deck is divided into, which are
what PROSA holds:

> "5. HED card MCP Bootstrap Type Area … 7. HED card IPL Type Area …
> 9. HED card Restart Type Area … 11. HED card MCP Mainleg Type Area …
> 13. HED card MCP Loader Type Area … 15. HED card MCP Dump Type Area …
> 17. HED card MCP System Commands Type Area … 19. HED card MCP Job
> Control Type Area"

So PROSA is a **named-segment program library**: MCP's own overlays
(mainleg, loader, dump, system commands, job control, restart) live there
and are fetched on demand. There is a "disk dictionary" (p.32) mapping
names to locations, and type-areas are addressed by name — including one
whose name is literally `))))))).` (p.32), used to carry the system
checksum.

### 5.3 What MCP offers *programs*: an arc allocator, not a filesystem

`C22-6678-1` **printed p.9**, the IOD card:

> "DISK OR TRACK IOD CARD: … where: type is either DISK or TRACK; number
> is a decimal integer indicating: a. Number of arcs if type is DISK, or
> b. Number of tracks if type is TRACK. **MCP reserves the requested
> multiple of eight arcs, the first reserved arc being the first arc of a
> track.** This permits the programmer to perform an autoaccess
> elimination operation, but his control word must meet the requirements
> of the 7030 as stated in the Automatic Access Elimination section of the
> Reference Manual, IBM 7030 Data Processing System, Form A22-6530-2."

A program declares "I want N arcs" or "I want N tracks" on a punched
card; MCP reserves a run and gives it a logical name (IODNAME). Arc
numbers the program uses are **relative to its allocation** and
bounds-checked in software — `C22-6678-1` **printed p.43**:

> `EPGK (Disk) Operation would exceed requested arcs` *(under Read and
> under Write)*
> `EPGK (Disk) The arc number, ARC.(J), exceeds the number requested for
> IODNAME(I).` *(under Locate Arc)*

So MCP's disk abstraction is: **a contiguous, track-aligned extent of
arcs per logical unit, with relative addressing and a software bounds
check**. That is an allocator, not a filesystem — no directories for user
data, no record structure, no free-space management visible to the
program. (MCP's *own* PROSA has a dictionary and named type-areas, so MCP
runs something filesystem-shaped for itself and exposes an extent
allocator to problem programs.)

The MCP macro set, `C22-6678-1` printed p.43, maps one-for-one onto the
hardware: `MRD`/`MRDS` → `$RD`/`$RDS`, `MW`/`MWS` → `$W`/`$WS`, `MCCW` →
`$CCW`, `MREL`/`MRELS` → `$REL`/`$RELS`, `MLOC`/`MLOCS` → `$LOC`/`$LOCS`.
Five operations, the same five as the hardware, and no control function.

One printed anomaly worth recording: under **Locate Arc**, p.43 lists
"`CS  $LOC completed`" where every other operation on the page lists EOP
(`EOP $RD completed`, `EOP $W completed`, `EOP $REL completed`). The
Reference Manual's LOCATE indicator list (p.161) contains EOP and does
*not* contain CS, and p.161 says explicitly "When both access mechanisms
have been positioned, an EOP indication is given". I believe the MCP
manual has a misprint, but both are primary and I am not overwriting one
with the other. Flagged, unresolved.

### 5.4 **The minimum disk behaviour MCP needs to boot** — versus a faithful model

This is the distinction the brief asked for, and §5.1 makes it a useful
one.

#### To IPL MCP at all (tape IPL, the cold start)

The hardware IPL itself needs **nothing from the disk** — it is an
Exchange card/tape read (Reference Manual pp.125–126) and the disk is not
involved. What the *initialization program* then does is write the entire
master system tape into PROSA (`C22-6678-1` p.29). So the disk behaviour
needed to get through initialization is:

| # | Behaviour | Source |
|---|---|---|
| 1 | A 2,097,152-word backing store per unit, zero-initialised | p.157 |
| 2 | `LOC` setting a 12-bit arc address from right EA bits 38–49, with 32–37 required zero; EOP on completion | p.160 |
| 3 | `W` streaming `count` words from core at DWA into successive arcs from the arc register, incrementing it | pp.160–161 |
| 4 | Zero-fill of the tail of the last arc on a short write | p.160 |
| 5 | `RD`, the mirror of 3 | p.160 |
| 6 | `EOP` on normal completion; `SEOP` suppressing it | pp.159–161 |
| 7 | `UNRJ` when no disk is attached to the addressed channel | p.159 |
| 8 | The control word read as DWA + count **only** — flags and refill discarded | p.158 |

Eight items. Notably absent from the list, and *genuinely not needed to
boot*:

- **`CTL`** — not merely unneeded, but required to raise EPGK. One line.
- **Chaining, multiple, skip, refill** — all discarded by the hardware.
- **Automatic access elimination** — a pure timing feature whose data
  placement is identical to the naive path (§3.9).
- **Any timing at all.** Seek and rotational latency are invisible to a
  functionally-correct program; MCP polls or takes an interrupt on EOP.
- **The two-access-mechanism structure.** Its only functional consequence
  is that sequential reads don't seek, which a zero-latency model gets
  for free.
- **`CCW`** — MCP has an `MCCW` macro, but nothing in the initialization
  path (pp.29–32) uses it, and on the disk `CCW` is forbidden during
  transfer anyway. Low risk to defer, but see the caveat below.
- **The 39-bit byte format, the 7-bit ECC, the 78 faces.** Entirely
  internal; nothing observable depends on them in a model that does not
  inject errors.
- **The 32-channel multiplexing.** MCP's minimum configuration is *one*
  disk unit (p.6). One channel suffices.
- **`UK`, `EKJ`, `EPGK`** beyond the CONTROL case — error paths a healthy
  model never enters.

That is a **remarkably small** minimum: a flat 2²¹-word array, an arc
cursor, a sequential read and a sequential write, and EOP. Perhaps
80–150 lines in this repo's style. The disk is not the hard part of
running MCP; the Exchange, the interrupt system, the tape unit and the
console are.

Three caveats on that claim, stated so nobody is surprised:

1. **It is derived from the manuals, not from MCP's source.** The MCP
   listing (`MCP_Mar63_001-249.pdf` + `MCP_Mar63_250-445.pdf`, 451 pages,
   no text layer) is in `docs/` and is the authority on what MCP's disk
   routines actually issue. Reading it was out of budget here. If MCP's
   disk driver issues a `CCW` to recover a position, or depends on AAE
   behaviour, item 6 or the AAE exclusion moves into the minimum. **The
   decisive check is a grep of that listing for `$LOC`/`$CCW`/`$RD`
   against the disk IOD**, and it has not been done.
2. **EOP must reach the CPU**, which means the interrupt system — the same
   hard prerequisite `exchange_and_io.md` §6.1 identified for the
   Exchange. The disk adds nothing to that problem, but it does not
   escape it.
3. **"To boot" presupposes the tape unit and the Exchange work.** The real
   gate on MCP is the tape IPL path, not the disk.

#### CAVEAT 1 IS NOW DISCHARGED, AND IT CHANGES THE MINIMUM

*Added 2026-10-18.* Caveat 1 below says the minimum "is derived from
the manuals, not from MCP's source", and names the decisive check: a
look at what MCP's disk routines actually issue. **That check has now
been done for the initialization path**, because MCP printed pp.15–16
have been transcribed bit-exactly (`decks/mcp_bootstrap_p15.strap`,
`decks/mcp_bootstrap_p16.strap`). What they issue is:

| MCP row | statement | comment on the row |
|---|---|---|
| p.15 line 26 | `LOC(SEOP),0.0,0.0` | `-POSITION TO ARC ZERO` |
| p.16 line 13 | `W(SEOP),0.0,X PRO WR` | `-WRITE PROSA` |
| p.16 line 22 | `CCW,0.0,X IPL BS+1.0` | `-ATTEMPT TO GET CW` |

**`CCW` MOVES INTO THE MINIMUM, and not as an afterthought — it is
MCP's completion poll.** §3.6 reads, from printed p.161, that `CCW`
"is not executed when a disk storage is reading or writing, and the
channel-busy indicator will be turned on". MCP uses exactly that:

```
  line 21   LC,$7,0.0            -DONE * SET UP FOR TEST OF WRITE
  line 22   X11 CCW  CCW,0.0,X IPL BS+1.0    -ATTEMPT TO GET CW
  line 23-24  SIC,X ERR AD / BEKJZ,X ERROR   -IF EKJ
  line 25-26  SIC,X ERR AD / CBZ,$7,X ERROR  -IF WRITE NOT SUCCESSFUL
  line 27   BCBJZ,X11 CCW                    -IF WRITE DONE
```

The `BCBJZ` retries the `CCW` for as long as channel-busy keeps coming
back, and `CBZ,$7` bounds the retries. **A `CCW` that refuses with CBJ
is how MCP learns the write is still running, and a `CCW` that
succeeds is how it learns the write finished** — and line 28 then takes
the arc count out of it. The same shape appears one block earlier for
the LOCATE: lines 13–20 reissue the `W` while CBJ is on, which is MCP
waiting for p.15's seek.

Two consequences for the model:

1. **Implement `CCW` with the disk's own refusal rule.** It is item 9
   of what was an eight-item list. Returning a control word built from
   the live data-word-address and count fields is not optional
   decoration; the arc count MCP accumulates into the communication
   region comes from it.
2. **A zero-latency disk is still correct, and it is worth saying why.**
   If `W` completes within its own instruction, CBJ is never on, every
   `BCBJZ` falls through on the first try and the loops run once. The
   retry structure is tolerant of a disk that is infinitely fast; what
   it is NOT tolerant of is a `CCW` that fails for some other reason,
   or one that returns a count MCP cannot use.

What the check did **not** find, and the exclusions that therefore
still stand: no `CTL` on the disk path, no chaining, no `REL`, no
dependence on automatic access elimination, no second disk unit. The
`UNRJ` and `EKJ` tests are present on every one of those three rows,
so those two indicators must exist and must be *off* on a healthy
model — which they are by construction.

The caveat's own wording is kept below unchanged, because it names the
check that was right to ask for.

#### To run MCP well

Add: `CCW`, the full indicator set with its documented causes, the global
one-transfer-at-a-time interlock and `CBJ` cause 2 (needed the moment a
second disk unit exists), the arc-boundary and end-of-volume checks
(EKJ cause 3, EPGK cause 3), and the per-arc zero-fill-on-RELEASE
behaviour.

#### To be a faithful 353/7303

Add: the three-point seek model with the 16-group structure, the
rotational distribution, automatic access elimination including the
nondeterministic residual DWA, the dual access mechanism with
pre-positioning, 8 µs/word pacing against the memory bus as the
highest-priority unstallable requester, the EPGK-delayed-until-write-zeros
behaviour, and the status-held-until-EOP rule.

---

## 6. Is there a deck oracle? No — and that is now a firm negative

Short answer: **no disk diagnostic deck exists in `stretch/docs/`**, two
IBM disk test programs are known by name to have existed, and neither
listing is here. The disk, like the Exchange, would be built to a
manual-only standard.

The evidence, in increasing strength:

**The repo's deck inventory has none.** `docs/archival_inventory.md`'s
listing table (lines 1463–1477) covers the I-Box diagnostics (`ja_ax1a`,
`jb_ax2a`–`jb_ax5b`), floating point (`jb_af1c`), three memory tests
(`ja_bb6b`, `ja_bm6a`, `ja_bp6a`), the exchange/box test (`ka_ex1`,
`ka_ex1b`), SSIP (`ja_ua1`), the Diagnostic Control Program (`ka_ua1`),
the maintenance tape builder (`ja_uc1a`) and the loader utility
(`ka_ul1`). No disk test.

**The August 1961 acceptance schedule has none.**
`7030_SystemTestPrograms_Aug61.pdf` §2 "Program List" (PDF p.6, the
section is unpaginated) lists sixteen programs in full:

> JA AX1 (I-Box), JA UA1 (SSIP-Utility Routines), JB AX2/AX3/AX4/AX5
> (I-Box), JB AF1C (Floating Point Circuitry), JB AV1C (Variable Field
> Length Cktry), KA BT1 (Mem Timer), KA AT1 (Raw Speed 1), JB AC1 (I-Box,
> I-Checker), JA BM6A (Memory Addressing), JA BB6B (Memory Worst Pattern),
> JA CE2 (Tape 7 (All Channels)), JA EE3 (BX/TAPE), JA NE6 (Punch)

Nothing for the disk. (The schedule's own introduction, PDF p.5, says the
sequence "is recommended although not mandatory" and is a guide for
"acceptance tests", so this is a *selected* schedule, not a catalogue of
everything that existed.)

**But IBM did write disk tests, and we know their names.** Performance
Characteristics Vol.1 **p.5-5** (text layer, literal extraction) lists the
system test programs by area:

> "• High-Speed Exchange - This program utilizes the disk file in an
> elementary fashion to test the disk synchronizer.
> • Disk - Tests the disk and includes worst patterns and timing tests.
> • I/O Scan - Tests the circuitry associated with the exchange scan and
> the disk scan."

and **p.5-8** describes the SEVA system-evaluation program's disk
component:

> "• Disk Routine - This routine is similar to the tape routines in that
> it will exercise all possible disk operations."
> "• I/O Initiator - This routine operates with the initiator routine to
> start from one to eight tape routines and **one disk routine**…"
> "When available, the disk and eight tapes will be running simultaneously
> with the central processor unit routine."

So three disk-exercising programs are named in a primary source — a
synchronizer test, a worst-pattern-and-timing disk test, and a SEVA
routine exercising "all possible disk operations" — and **none of their
listings is in this repository**. That third one in particular, had we got
it, would be exactly the oracle wanted: an IBM-written exerciser of every
disk operation, with IBM's own assembler output to check the
transcription against (`AGENTS.md` rule 3).

This is a bounded negative of the most actionable kind: the artefact
exists in the historical record and is simply not here. It is worth adding
to `archival_inventory.md`'s wanted list under the names **"Disk"**,
**"High-Speed Exchange"** and **SEVA**. Until one surfaces, the disk is in
the same position as the Exchange: built to the manual, verified by
purpose-written STRAP, with the manual's own tables (the pp.157–162
indicator causes, the three AAE conditions, the LOC field split) as the
checklist.

---

## 7. The 353-vs-7303 verdict

**Verdict: only the nameplate differs. The behaviour is single-sourced
and therefore cannot be in conflict.** Both labels are confirmed
first-hand here; neither carries any behavioural claim.

| Source | Printed location | What it says | Geometry given? |
|---|---|---|---|
| `A22-6552-1_physPlan_Feb63` | printed p.6 (PDF 7) | "**IBM 7612 Disk Synchronizer and IBM 353 Disk Storage.** The disk synchronizer connects disk storage units to the system. The disk storage supplies vast additional word storage capacity." | **No** |
| `R23-9702` (1961) | frontispiece, PDF p.3 | block labelled "**7303 Disk Storage**", wired to "7612 Disk Synchronizer" | **No** |
| `22-6530-2` Ref. Man. | pp.157–162 | "the IBM 7612 Disk Synchronizer… and **the storage unit**" — the other half is never given a model number anywhere in the chapter | **Yes, all of it** |

The structure of the evidence settles the question asked:

- The **nameplate** is multiply-sourced and inconsistent: 353 (Feb 1963),
  7303 (1961), unnamed (Reference Manual).
- The **behaviour** is singly-sourced: Reference Manual pp.157–162 is the
  only place in `docs/` that gives any capacity, geometry, timing or
  interface for the thing. A single source cannot contradict itself across
  model numbers.
- No document here attaches a *different* capacity or geometry to a
  different number. Everything that quotes a capacity quotes 2,097,152
  words: Reference Manual p.157 (twice), p.158's table, and Figure 1 on
  printed p.6 ("Disk Storage 2,097,152 Words 125,000 Words/sec").

So: **the difference is a nameplate, not a behaviour, and for modelling
purposes it does not matter.** Model the Reference Manual's device and
call it whatever the model's comments prefer — 7612 + "disk storage" is
the Reference Manual's own usage and the safest.

What remains genuinely unresolved is *why* two numbers exist. Three
hypotheses are available and none is supported by anything in `docs/`:
that 7303 was a pre-announcement designation superseded by 353 (the dates
fit — 7303 in 1961, 353 in Feb 1963 — but "fits the dates" is not
evidence); that they are two different storage units both attachable to a
7612; or that one of the two documents is simply in error. Settling it
needs a document this repository does not have — an IBM sales manual, a
field-engineering parts catalogue or a 7612/353 CE manual. The
`exchange_and_io.md` §7.5 open question stands, with the important
amendment that **it is now known to be a question about labels only, and
therefore not a blocker**.

(`exchange_and_io.md` §2.3 mentioned "a third source disagreeing again".
I could not locate a third disagreeing designation in this pass; what I
found was the Reference Manual declining to name the unit at all, which is
a silence, not a third name. Reported as a correction.)

---

## 8. Sizing

Engineering estimates, **flagged as conjecture** — my judgement from the
documented behaviour and the shape of `bsv/StretchIO.bsv` (342 lines
total, roughly 1:3 code:comment in this repo's style), not measurements.
"Code lines" below means code, not comment.

### 8.1 A faithful 7612 + disk storage

| Piece | Est. code lines | Basis |
|---|---|---|
| Arc/track geometry, arc address register, auto-increment, auto-reposition, dual access mechanism | 60–100 | pp.157, 161 |
| `LOC` (field split, both arms, EOP on both-positioned, not-ready rejection) | 60–100 | pp.160–161 |
| `RD`/`W` transfer FSM (DWA+count only, per-arc stepping, short-write zero fill, end-of-volume check) | 100–160 | pp.158, 160 |
| `REL` (abort transfer, zero-fill remainder, leave arc register, don't abort LOCATE) | 40–70 | p.161 |
| `CCW` (synchronous, idle-only, DWA+count in control-word format, no EOP) | 30–60 | p.161 |
| `CTL` → EPGK | 5–10 | pp.159–160 |
| Indicator logic: 7 indicators × their documented causes, hold-until-EOP vs immediate, per-channel status retention | 90–150 | pp.158–159 |
| Global one-transfer interlock + `CBJ` causes 1–3 across 32 channels | 50–90 | p.159, A-5 |
| Automatic Access Elimination (3 conditions, wrap at arc 7, DWA readjust, residual register) | 60–110 | p.162 |
| Timing model (piecewise seek, rotational sampling, 8 µs/word pacing) | 60–110 | pp.157–158 |
| MBCU requester + unstallable-priority hookup | 40–80 | `exchange_and_io.md` §4 |
| **Total** | **≈ 600–1,040** | |

That is **above** `exchange_and_io.md` §6.1's 400–700 estimate, and
deliberately so. That estimate was made without the chapter in hand. The
pieces it would not have anticipated are the indicator table (seven
indicators with ~15 distinct documented causes), the dual access
mechanism, AAE, and the global interlock — the chapter is denser than
"no chaining, no CCW during transfer" suggests. I would revise the figure
to **600–1,000 code lines** for a faithful model, which with this repo's
comment ratio is on the order of 2,000–4,000 lines of file.

### 8.2 The boot-MCP minimum (§5.4)

| Piece | Est. code lines |
|---|---|
| Backing store + arc register + auto-increment | 25–40 |
| `LOC` (field split, set register, EOP) | 20–35 |
| `RD`/`W` sequential + zero-fill tail | 35–60 |
| EOP/SEOP + UNRJ | 15–25 |
| `CTL` → EPGK | 5–10 |
| **Total** | **≈ 100–170** |

Two orders of magnitude smaller than the Exchange minimum
(`exchange_and_io.md` §6.2: 1,150–1,950). **The disk is the cheap part.**

### 8.3 Dependencies — including one that is not lines of code

1. **The interrupt system.** EOP must reach the CPU. Same hard
   prerequisite as the Exchange; the disk does not escape it and does not
   add to it.
2. **`StretchMemory.bsv` as a multi-requester bus.** The disk is a second
   DMA engine at one reference per 26⅔ machine cycles, unstallable, at (or
   near) top priority. `exchange_and_io.md` §4.4 estimates 60–120 lines
   for the arbiter shared with the Exchange; the disk's marginal cost on
   top of that is small. Who wins between the Exchange and the disk is
   genuinely unspecified (`exchange_and_io.md` §7.8) — the disk, being
   unable to stall, almost certainly does, but no document here says so.
3. **The backing store itself, which is not registers.** 2,097,152 words ×
   72 bits = **≈ 18 MiB per disk unit**. That is not a Bluespec `Vector`
   and it is not on-chip BRAM on most parts — a Bluesim model wants a
   file-backed or malloc-backed store behind a BDPI/import-BVI shim, and
   an FPGA build wants external DRAM. This is a *structural* dependency,
   not a line count, and it is the one that interacts with
   `docs/fpga_feasibility.md`. For comparison, the whole of main memory is
   six units × 16,384 words × 72 bits ≈ 864 KiB, which this project
   already models as registers. The disk is 21× the entire core store.
   Note that `bsv/StretchIO.bsv`'s existing device model already faced a
   smaller version of this problem and solved it by pre-loading fixed-size
   `Vector`s from the testbench, explicitly because "bsc's `$fopen`/
   `$fgetc` are Actions" — that solution does not scale to 2²¹ words and a
   different mechanism will be needed.
4. **A sparse representation is viable and worth considering.** MCP's
   PROSA is a few hundred KB at most; a problem program's IOD allocation
   is as many arcs as it asks for. A hash-map-of-arcs model, with
   unwritten arcs reading as zero, would cover every realistic workload at
   a tiny fraction of 18 MiB and is semantically exact (the manual
   specifies zero-fill on short writes, so "unwritten reads as zero" is
   consistent with the documented behaviour of a freshly-written volume —
   though note the manual does *not* specify what a never-written arc
   reads as, see §9.5).

---

## 9. What the documents do **not** answer

Bounded negatives. Each is something I looked for in `stretch/docs/` and
could not find, not something I declined to look up.

1. **Which is the true maximum seek, 265 ms or 180 ms** (§4.2). Reference
   Manual p.157 and p.158 contradict each other on the same quantity, five
   paragraphs apart. No third source gives a disk seek time. A
   cycle-accurate model must choose and document the choice.

2. **The seek time for any motion other than the three given.** 51 ms
   (one track within a group of 16), 117 ms (crossing a 16-group
   boundary), and full stroke. Nothing in between, no formula, no
   settling-time model, and no explanation of what a "group of 16" is
   physically. Interpolation is invention.

3. **What `CCW` puts in the bits that are not DWA and count.** p.161 says
   the two retained fields are "placed in a full-word format,
   corresponding to their location in a control word". It does not say
   whether bits 18–27 (status, flags) and 46–63 (refill) come back zero,
   come back as whatever the synchronizer last saw, or are undefined. A
   program that compares a whole returned word against an expected value
   would discriminate; none is available (§6).

4. **Whether the Exchange's "count 0 means 2¹⁸" rule applies to the
   disk.** Reference Manual p.123 states it for the Exchange. The disk
   chapter retains the same count field but never restates the rule
   (§3.3).

5. **What a never-written arc reads as.** The manual specifies zero-fill
   of the *tail* of a partially-written arc (p.160) and of the arc in
   which a RELEASE landed during a write (p.161), and zeros written on an
   EPGK-causing over-high DWA (p.159). It says nothing about the power-on
   or factory state of the medium. A model must choose (zero is the
   obvious choice) and say so.

6. **The disk synchronizer's internal cycle-level sequencing.** There is
   no 7612 CE manual, and no 353 or 7303 CE manual, in `docs/`. The
   deepest internal view available is p.158's "Data Paths" paragraph —
   three registers, "one in a full-word register, the second in two
   half-word byte registers" — plus Performance Characteristics p.A-5's
   "enough memory for 1 control word and 1 data word". A gate-accurate
   7612 cannot be built from what is here; a *behaviourally* accurate one
   can.

7. **The arbitration order between the Exchange and the disk synchronizer
   at the memory bus.** Buchholz (`Planning_A_Computer_System.pdf` p.205)
   lists them together as jointly highest priority without ordering them
   against each other. Inherited unresolved from `exchange_and_io.md`
   §7.8; nothing in the disk chapter settles it.

8. **How long the disk synchronizer takes to *accept* an instruction.**
   The Exchange's equivalent is "a few microseconds" with no number
   (Reference Manual p.112). The disk chapter gives no acceptance latency
   at all — it says only that EPGK "is set soon after the instruction has
   been accepted" (p.159). No number anywhere.

9. **Whether MCP's disk driver uses `CCW` or depends on AAE.** §5.4's
   minimum-to-boot list excludes both, derived from the manuals. The MCP
   source listing (`MCP_Mar63_001-249.pdf` + `MCP_Mar63_250-445.pdf`,
   451 pages, no text layer) is in `docs/` and would settle it, and
   reading it is the single highest-value follow-up this study leaves
   behind. Until then item 6 of §5.4's exclusion list is an inference, not
   a finding.

10. **Why two model numbers exist** (§7). Resolved to the extent that
    matters — nameplate only, no behavioural difference — but the
    historical question is open and needs a document not in this
    repository.

11. **The tail of EKJ cause 1** (§3.8), lost in the p.158/p.159 column
    break. Recoverable by re-reading the bottom of p.158's right column
    with more care than I gave it; I inferred it from the Exchange's
    parallel wording at p.112 and flagged the inference.

12. **The three IBM disk test program listings** — "Disk", "High-Speed
    Exchange", and the SEVA Disk Routine — named in Performance
    Characteristics Vol.1 pp.5-5 and 5-8 and absent from `docs/` (§6).
    This is the only *missing artefact* in the study, as against missing
    *information*: the disk can be modelled without them, but it cannot be
    verified the way the I-Box was.

---

## 10. Summary for the build plan

- **The disk can be modelled from what is here.** pp.157–162 is a complete
  specification. No document is missing that blocks the work.
- **The disk is not the gate on MCP.** The gate is the tape IPL path: the
  Exchange, the 7613/729 IV, and the interrupt system. MCP cold-starts
  from tape and writes its system onto the disk; it never boots from it.
- **The boot-MCP minimum is ~100–170 code lines** — a 2²¹-word store, an
  arc cursor, sequential read/write with tail zero-fill, EOP, UNRJ, and
  `CTL`→EPGK. Build it early; it is cheap and it unblocks nothing else by
  being deferred. **Plus `CCW`**: §5.4's new subsection discharges
  caveat 1 against MCP's own transcribed source, and `CCW` turns out to
  be MCP's write-completion poll, not a convenience.
- **A faithful model is ~600–1,000 code lines**, above
  `exchange_and_io.md`'s 400–700, with the indicator table, the dual
  access mechanism, AAE and the global interlock accounting for the
  difference.
- **The real structural dependency is 18 MiB of backing store**, not logic.
  Plan for a file-backed or sparse representation; it interacts with
  `fpga_feasibility.md`.
- **No deck will verify it.** Build to the manual, with pp.157–162's own
  tables as the checklist, and write the STRAP exerciser the way the
  Exchange will have to be exercised.
- **The 353/7303 question is closed for engineering purposes** and open
  only as history.
