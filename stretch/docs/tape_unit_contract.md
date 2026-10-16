# The tape unit contract for an MCP tape IPL

What a modelled IBM 729 IV tape unit (plus its tape control / adapter)
must do for MCP to get through IPL and initialization. Written as a
spec to implement against `bsv/StretchIO.bsv`, not as an essay.

**Why this document exists.** `docs/NEXT.md` §5h established from
`C22-6678-1` printed p.29 that MCP boots from the *master system tape*
and writes the disk as a side effect, so a tape unit is on the MCP
critical path. `bsv/StretchIO.bsv` already has a tape stand-in on
channel 34 (16-word `Vector`, persistent `tapePos`, CONTROL 136/137 and
176). This says which of its choices survive contact with MCP.

**Citation offsets.** Reference Manual `22-6530-2` is printed + 3
(printed p.133 = PDF p.136). `C22-6678-1` is printed + 0.
`ka_ul1_load_and_tape_write_util.pdf` and
`ja_uc1a_maintenance_tape.pdf` are 2-up scans with no text layer; their
PDF page is given explicitly each time. Everything below was read as a
page image at 300 dpi (RefMan, MCP Ref) or 200 dpi (the two utility
write-ups), with the KA UL1 machine-code columns re-read at 600 dpi.

**Three documents opened here for the first time** (see §4 for the full
verdict on each):

* `docs/ka_ul1_load_and_tape_write_util.pdf` — "LOAD AND TAPE WRITE
  UTILITY, KA UL1, October 13, 1961". **It is the program that writes
  an IPL tape**, and its STRAP listing is included. It is the single
  most useful document found for this task.
* `docs/ja_uc1a_maintenance_tape.pdf` — "MAINTENANCE TAPE, MNT TP 1,
  File No. JA UC 1A". A 32-program multi-record tape with its own tape
  IPL procedure and loader flowchart. Independent corroboration of the
  IPL path.
* `docs/C28-6379-0_MCP_Loader.pdf` — "Loader and BSS Processor". **Not
  the boot path**: it is MCP's *resume load program* + the FORTRAN
  Binary and Symbolic Subroutine processor, i.e. how a problem
  program's binary deck is loaded *after* MCP is running. Nothing about
  IPL or on-tape system format.

---

## §1. The contract — required behaviours

Each item is something an implementation must do, with the page that
requires it. Items marked **[IPL]** are needed to get the first
instruction executed; **[INIT]** are needed for the initialization
program that runs afterwards; **[DRV]** are needed by MCP's general
tape driver but not provably by initialization.

### 1.1 Unit and addressing

1. **[IPL]** A tape unit is reached through a *tape control* on an
   exchange channel, not directly. "Each exchange channel can
   accommodate one tape control and as many as eight tape units may be
   attached to the tape control. Only one of the units attached to a
   channel, however, can be operated at a time." (RefMan printed p.130
   = PDF p.133.)
2. **[IPL]** The unit's selection address comes from a physical rotary
   **Address Selection Switch** on the drive: "ten positions marked
   with the numbers 0 through 9, out of which the positions 0 through 7
   represent assignable addresses. Positions 8 and 9 are invalid and a
   unit that has one of these addresses cannot be selected." (RefMan
   printed p.131 = PDF p.134.) This is `C22-6678-1` p.29's "dialed to
   zero".
3. **[DRV]** `LOCATE` selects the unit: only the three low-order bits
   of the right effective address, bits 47–49, are decoded by the
   control (RefMan printed p.133 = PDF p.136). All subsequent
   READ/WRITE/CONTROL apply to the last-located unit (printed p.111).
4. **[IPL]** At IPL the selection is forced: "the tape control is reset
   to select the tape unit having selection address 0" (RefMan printed
   p.134 = PDF p.137), and "a program can be loaded by the initial
   loading technique only from a unit having the selection address 0"
   (printed p.126).

### 1.2 The IPL sequence as the tape sees it

5. **[IPL]** Pressing INITIAL PROGRAM LOAD resets the tape subsystem to
   a known state that the model must reproduce, because the first read
   depends on it: *tape control* → **odd parity, no-ECC**; *all tape
   units* → **high density**; *tape control* → **select unit 0**.
   (RefMan printed p.134 = PDF p.137, first paragraph.) Separately
   printed p.130 (= PDF p.133): "When the initial-program-load key is
   depressed, or the power in the unit is turned on, the unit is reset
   to the no-ECC mode of operation, and the reserved and check lights
   are off."
6. **[IPL]** The boot is started by a **channel signal**, and the
   channel that raises it is the channel that boots: the exchange
   "stores in the control word location for *the channel responsible
   for the channel signal* a fixed control word" (RefMan printed p.126,
   transcribed in full in `docs/exchange_and_io.md` §3.12). The model
   therefore needs a per-channel channel-signal input that is
   *externally triggerable*, not just a status bit.
7. **[IPL]** **A 729 IV has no Signal key.** "The channel-signal
   indication on tape units is caused whenever the unit changes from
   not-ready status to ready status. This change can be the result of
   either a depression of the start key or the completion of a REWIND
   control operation. **There is no signal key on the tape units to
   generate a channel-signal indication.**" (RefMan printed p.136 =
   PDF p.139.) `C22-6678-1` p.29 step 4 therefore means a Signal key on
   the **adapter unit** (the tape control), not on the drive — and
   `ja_uc1a` PDF p.2 (printed p.2), loading procedure step 3, gives the
   drive-side alternative in so many words: "Cause a Channel Signal to
   emanate from Tape Unit 0 of the channel used. (**Make Tape Unit Not
   Ready then Ready.**)". Both routes must be modellable; the
   generic standard-unit Signal key is described at RefMan printed
   p.129 = PDF p.132.
8. **[IPL]** A channel signal may come from *any* unit on the control:
   "a channel-signal indication may be given by any of the units
   regardless of whether or not the unit is currently selected by a
   locate instruction. No distinction is made between channel-signal
   indications coming from different tape units attached to the same
   control unit." (RefMan printed p.136 = PDF p.139.) So the channel
   signal identifies a *channel*, and the thing that picks the drive is
   rule 4, not the signal.
9. **[IPL]** The exchange then issues **one READ** against the fixed
   control word `data word address = 4, chain = 1, multiple = 0,
   skip = 0, count = 1, refill address = 4` (RefMan printed p.126). The
   tape unit sees an ordinary single-block READ. The first word lands
   at core location 4; the count is then exhausted and the chain flag
   makes the exchange refill the control word *from location 4* and
   keep reading **the same block**. That is Figure 36's
   `multiple 0 / chain 1 / count zero / not end of block` row, whose
   action is literally "**Chain and continue**" (RefMan printed p.109,
   full 16-row table transcribed at `docs/exchange_and_io.md` §3.3);
   the adjacent row with `end of block = yes` is "End operation", which
   is what terminates the IPL read at the first gap. The number of
   words read is
   therefore `1 + (count field of the control word that the tape itself
   supplied as its first word)`, and is a property of the tape, not of
   the hardware.
10. **[IPL]** When the READ completes the exchange sends an
    initial-start signal; the CPU executes the instruction at the data
    word address of the control word now in location 4, without setting
    the instruction counter, so **the first instruction must be BRANCH
    DISABLED** (RefMan printed p.126).
11. **[IPL]** Consequence for the model: **chain + refill must actually
    work.** This is the one hard blocker. An IPL with the chain flag
    ignored reads exactly one word and stops.

### 1.3 Block and record structure

12. **[IPL]** A tape is a sequence of variable-length **blocks**
    separated by a blank gap "approximately ¾ inch long… reading in the
    single-block mode transfers the information located between two
    consecutive gaps. When the end of the last block of an operation is
    reached, the tape control causes an end-of-operation indication."
    (RefMan printed p.133 = PDF p.136.) **There is no length field and
    no count on tape**: the reader knows a record ended because the
    signal stops. Block length is therefore a property of the stored
    image, not of the control word.
13. **[IPL]** The tape is a *bit stream*, not an array of words. In
    no-ECC mode "64 bits constitute a word. On writing, only the 64
    data bits are recorded, and they form 10⅔ six-bit bytes on tape."
    (RefMan printed p.134 = PDF p.137.) The tape control "contains a
    'byte converter' that converts four successive 6-bit bytes on
    reading into three successive 8-bit bytes for entry into the
    exchange… **Incomplete 6-bit bytes at the end of a word are filled
    with the first bits of the next word so that no gaps are left on
    tape.** Conversely, successive 6-bit bytes on tape appear in
    consecutive 6-bit groups in storage without gaps, and may straddle
    storage word boundaries." (RefMan printed p.130 = PDF p.133.)
    Words are **not** 6-bit-aligned on tape; the mapping is
    `bit i of the block → frame i/6, bit i mod 6`.
14. **[DRV]** In ECC mode a word is 72 bits = exactly 12 six-bit bytes,
    **ECC bits first** (RefMan printed p.134 = PDF p.137). Not needed
    for IPL: rule 5 resets the control to no-ECC.
15. **[IPL]** Ragged ends are defined and observable: "If, during
    writing, the number of bits in the words to be written as one block
    is not divisible by six, the remaining four or two information bits
    are combined with two or four zeros… On subsequent reading these
    zeros are treated as information bits. Similarly, during reading,
    if the number of information bits in the tape block is not
    divisible by 8, the remaining 6, 4, or 2 bits are combined with
    zeros to form the last 8-bit byte to be sent to the exchange. Thus,
    **it is possible to read an extra word of all zeros.**" (RefMan
    printed p.131 = PDF p.134.)
16. **[DRV]** Seven tracks, `CBA 8421`, C = parity. "When these bits are
    stored, bit B is in the lowest-numbered, or leftmost, bit position.
    Successive bytes are stored in the order in which they are read."
    (RefMan printed p.131 = PDF p.134.)

### 1.4 Tape marks and files

17. **[DRV]** "A tape mark consists of a block containing the **single
    byte 0001111** and the associated longitudinal parity check bits.
    It is preceded and followed by the regular ¾ inch inter-record gap.
    The tape mark is written on tape by means of a WRITE TAPE MARK
    control instruction and is used to indicate the end of a series of
    blocks (sometimes called a file)." (RefMan printed p.135 = PDF
    p.138.)
18. **[DRV]** Detection is **structural, not by value**: "the byte
    0001111 may occur in ordinary data being read, where it is not
    interpreted as a tape mark. The distinction between a tape mark and
    a data block is that **the tape mark is a single-byte block. Data
    blocks must contain more than one byte.**" (same page.) A model
    that stores records as byte strings gets this for free: a tape mark
    is a one-byte record whose byte is `0b0001111`.
19. **[DRV]** Indications on crossing a tape mark (RefMan printed p.135
    = PDF p.138): reading, spacing or backspacing over one causes an
    **end-exception**. On reading, "no information is transferred to
    core storage and the operation is always immediately terminated…
    Since no data are sent to the exchange, **the control word in the
    exchange is not modified**." Single-record mode → **EE and EOP**
    both set; multiple-record mode → **EE only**. Spacing or
    backspacing → EE **always** accompanied by EOP.
20. **[DRV]** Density gates tape-mark recognition: "a tape mark cannot
    be recognized unless it is read or spaced over in the correct
    density" (RefMan printed p.133 = PDF p.136), and reading in high
    density over low-density data stops the tape after one byte with
    **no error indication at all**.

### 1.5 Density

21. **[IPL]** Two densities, **556 bpi (high)** and **200 bpi (low)**
    (RefMan printed p.130 = PDF p.133, p.132 = PDF p.135 codes 036/037).
    Density changes the **recording density and hence the bit rate**;
    it does not change the encoding, the 7-track frame, the parity
    scheme or the tape-mark byte. Rates: 62,550 6-bit bytes/sec and
    170 µs per 64-bit word at 556 bpi; 22,500 and 474 µs at 200 bpi
    (RefMan printed p.130 = PDF p.133). Exchange load weights 32/17 and
    9/6 (printed p.131 = PDF p.134).
22. **[IPL]** Density lives **in the drive**, parity/ECC mode lives **in
    the control**: "The mode specifying even or odd parity and ECC or
    no-ECC type of operation is set up in the tape control and applies
    to all the tape units accommodated by that control… The mode
    specifying high or low density, on the other hand, is set up in the
    tape unit itself." (RefMan printed p.133 = PDF p.136.) Two distinct
    pieces of state, scoped differently. High density is the power-on
    and IPL default, which is why `C22-6678-1` p.29 says "Density for
    this unit is set to HIGH" — the master system tape is readable with
    no CONTROL issued first.
23. **[DRV]** Density may only be changed at load point: MCP's own
    `$HD` / `$LD` list "EPGK (Tape) Tape is not at load point"
    (`C22-6678-1` printed pp.45–46).

### 1.6 CONTROL function codes

24. The complete 729 IV table is RefMan printed p.132 = PDF p.135,
    re-read for this document and matching `docs/exchange_and_io.md`
    §3.6 exactly. Columns: whether MCP's own documented operation list
    (`C22-6678-1` Appendix B, printed pp.43–46) has a macro for it, and
    whether *initialization* is established to need it.

    | Octal | Function | MCP macro (App. B) | Needed by IPL/init? |
    |---|---|---|---|
    | 016 | Remove End of Tape Condition | `MTIF`/`$TIF` | no evidence |
    | 036 | High Density Mode (556 bpi) | `MHD`/`$HD` | **no** — IPL resets to high (rule 5) |
    | 037 | Low Density Mode (200 bpi) | `MLD`/`$LD` | no |
    | 056 | Erase Long Gap | `MERG`/`$ERG` | no evidence |
    | 057 | ECC Mode and Odd Parity | `MECC`/`$ECC` | **no** — IPL resets to no-ECC |
    | 076 | Space Block | `MSP`/`$SP` | **plausible** (see §3.2) |
    | 077 | Space File | `MSPFL`/`$SPFL` | **plausible** |
    | 117 | Write Tape Mark | `MWEF`/`$WEF` | **no** for a file-protected input tape (rule 35) |
    | 136 | Rewind | `MREW`/`$REW` | **yes** (see rule 25) |
    | 137 | Rewind and Unload | `MUNLD`/`$UNLD` | **established for KA UL1**, plausible for MCP |
    | 156 | No-ECC Mode and Even Parity | `MEVEN`/`$EVEN` | no |
    | 157 | No-ECC Mode and Odd Parity | `MNOECC`/`$NOECC` | **no** — IPL resets to this |
    | 176 | Backspace Block | `MBSP`/`$BSP` | **plausible** |
    | 177 | Backspace File | `MBSFL`/`$BSFL` | **plausible** |

    Standard codes 016/017/057/116/157 (RefMan printed p.130 = PDF
    p.133) are *redefined* by the tape for 016/057/157; 017 (Reserved
    Light On) and 116 (Check Light On) survive and appear in Appendix B
    as `$RLN` and `$KLN`.
25. **[DRV]** REWIND's EOP is anomalous and already half-modelled: "the
    end-of-operation indication is given as soon as the operation is
    initiated at the unit. Subsequently, while rewinding takes place,
    the unit is not ready. When the operation is completed, the unit
    automatically becomes ready and sends a channel-signal indication."
    (RefMan printed p.132 = PDF p.135.) MCP's Appendix B records the
    completion the same way: `$REW` reports **CS**, "`$REW` completed
    and new tape at load point" (`C22-6678-1` printed p.45). REWIND AND
    UNLOAD (137) is identical "except that the unit does not
    automatically become ready… **No channel signal is given upon
    completion**" — but MCP's `$UNLD` *does* list CS, a conflict
    recorded in §4.2.
26. **[DRV]** Space/backspace semantics (RefMan printed p.132 = PDF
    p.135): 076 forward one block to the next gap, EOP on completion,
    EE+EOP if the block was a tape mark. 077 forward past a tape mark,
    stopping in the gap *after* it, EE+EOP. 176 as 076 backward. 177 as
    077 backward, stopping in the gap *immediately preceding* the tape
    mark, "so that the next READ operation will read this tape mark".
27. **[IPL]** Backspace at load point is an error: "The tape cannot be
    moved by any means under program control beyond the load point. Any
    backspace instructions given with the tape in this position are
    terminated with an exchange-program-check indication." (RefMan
    printed p.136 = PDF p.139.) `StretchIO.bsv` already implements
    exactly this.
28. **[DRV]** Backspacing after a WRITE erases forward ~½ inch first
    (RefMan printed p.133 = PDF p.136). No programmer-visible effect;
    listed so an implementer does not look for one.

### 1.7 Indicators and error paths — the anti-hang list

A driver that polls will hang if any of these is missing.

29. **[IPL]** **Unit Ready / UNRJ.** An instruction to a channel whose
    unit-ready status bit is zero is *rejected* (`UNRJ`), the control
    word is not fetched and the unit is not started (RefMan printed
    p.112). Condition: unit not ready, or no unit attached. The master
    system tape is "mounted on any tape unit dialed to zero… and the
    unit is made READY" (`C22-6678-1` p.29), so for IPL the condition is
    just "ready = 1 after the operator readies it".
30. **[IPL]** **End of Operation (EOP).** Set at the end of the last
    block of an operation (RefMan printed p.133 = PDF p.136) and "upon
    the completion of every instruction unless the instruction is of
    the SEOP type" (printed p.132 = PDF p.135).
31. **[IPL]** **The SEOP status bit, control-word bit 24, is the thing a
    real driver polls.** "At the time an SEOP instruction is given, the
    SEOP bit in the control word is set to one. As the result of this,
    the EOP bit in the control word (and therefore in the indicator
    register) is not turned on unless it is accompanied by unit check or
    end exception." (RefMan printed p.121 = PDF p.124.) KA UL1's tape
    writer polls exactly this bit — see §3.4. **The hardware must
    therefore clear the SEOP bit when the operation ends**, and the
    branch sense is checked, not assumed: KA UL1's loop instruction is
    `BB` (Branch on Bit, i.e. branch *when the bit is one*), and IBM's
    own printed modifier byte for it is hex `02` = bit 62 (the "value
    that takes the branch") set, bits 60–61 (the "set the bit
    afterward" field) zero — against hex `0E` on the same listing page
    for `BB1` and hex `00` for `BZB`, exactly as `strap/opcodes.py`'s
    `BB_CODES` has them from pocket card X22-6533. So the loop spins
    **while bit 24 is 1** and falls through when it clears. *Flagged as
    an inference only in this narrow sense:* the manual states the set
    and not the clear; the clear is established from the deck. Its REL
    SEOP note ("the SEOP bit is **temporarily** set in the control
    word", same page) points the same way.
32. **[DRV]** **End Exception (EE).** Conditions, each a separate
    trigger: (a) tape mark crossed on read/space/backspace (rule 19);
    (b) end-of-tape reflective strip sensed **during writing** —
    "the tape-indicator-on light is turned on and the operation is
    terminated with an end-exception indication upon the completion of
    the current block. If this is also the last block to be written…
    end-of-operation accompanies end-exception; otherwise
    end-of-operation is absent" (RefMan printed p.136 = PDF p.139);
    (c) while the tape-indicator light is on, *every* WRITE is
    terminated by EE after one block; (d) a LOCATE selecting a unit
    whose tape indicator is on and which is in write status is
    terminated by EE and EOP (RefMan printed p.132 = PDF p.135).
    Note (e), a bounded negative: **the end-of-tape strip is ignored
    during reading and spacing** — "the program must rely upon tape
    marks to indicate the extent of the useful recorded information."
33. **[DRV]** **Unit Check (UK).** Conditions: uncorrectable data error
    (rule 34); the tape pulled off the reel by writing past end-of-tape
    or by reading/spacing beyond recorded data, after which "the unit
    becomes not ready. Operator intervention is subsequently required"
    (RefMan printed p.136 = PDF p.139); RESET key pressed mid-operation
    (printed p.131 = PDF p.134); more than one unit selected and ready
    on a READ (printed p.133 = PDF p.136).
34. **[DRV]** **Parity.** Two independent checks. *Vertical*: one C-track
    bit per 6-bit byte, odd parity normally. *Longitudinal*: one extra
    7-bit byte automatically recorded at the end of every block, even
    count parity per track. The complete error table, RefMan printed
    p.135 = PDF p.138, verbatim: during **writing**, longitudinal error
    → *ignored*, vertical error → **UK and EOP**; during **reading** in
    no-ECC mode, both → **UK and EOP**; in ECC mode, longitudinal →
    *ignored*, vertical → ignored if only one per word, **UK and EOP**
    if more than one per word. "The setting of the mode of parity
    checking is irrelevant when spacing or backspacing tape. All data
    errors in these operations are ignored."
35. **[DRV]** **Exchange Program Check (EPGK), tape-specific causes.**
    Backspace at load point (rule 27); WRITE or WRITE TAPE MARK to a
    reel without a file-protect ring — "are not executed and cause an
    EPGK indication. A tape unit in protected status, however, can
    execute READ instructions and all control instructions except WRITE
    TAPE MARK" (RefMan printed p.136 = PDF p.139); an all-zeros first
    byte of a tape record in even-parity mode — "the tape unit will not
    write a record but generates an exchange program check" (printed
    p.134 = PDF p.137); an undefined CONTROL code (printed p.113).
    **This matters for MCP**: the master system tape "is file
    protected" (`C22-6678-1` p.29), so any WRITE the model lets through
    to it is wrong, and MCP's own `$W` lists "EPGK (Tape) Write on file
    protected tape" (printed p.43).
36. **[IPL]** **Channel Signal (CS).** Raised on not-ready → ready
    (rules 7, 8) and on completion of a REWIND (rule 25). RefMan Figure
    40 note, printed p.123 = PDF p.126: "A Channel Signal indication can
    be caused **by the program** only upon the completion of tape
    rewinding (initiated by a CONTROL instruction)." CS is "available at
    any time except when channel is in operation" (same figure).
37. **[IPL]** **The polling primitive is COPY CONTROL WORD, and it does
    not block.** "The COPY CONTROL WORD instruction is accepted
    regardless of the status of the unit and can be executed while an
    operation is in progress at the addressed channel without
    disturbing the operation. Consequently, it is not subject to UNRJ
    and CBJ. The computer program may thus monitor the progress of an
    input-output operation." (RefMan printed p.122 = PDF p.125.) "The
    status bits, bits 18 through 24, reflect the current status of the
    input-output unit last selected." Figure 40's "computer waits until
    end of operation: Yes" for CCW refers to the CCW *instruction*
    completing, not the channel's operation — p.122 settles it.
38. **[DRV]** Status-bit attribution is per-unit once more than one unit
    exists: "the status bits can be turned on only by that unit that has
    been last selected by means of a LOCATE. (The channel signal is an
    exception; it can be turned on by any unit.)" (RefMan printed
    p.113.)

---

## §2. What changes in `bsv/StretchIO.bsv`

### 2.1 What survives

| Existing choice | Verdict |
|---|---|
| Tape on its own channel number (34) | **Survives.** `C22-6678-1` p.32's dump table names CH 32/33/34 on a real MCP machine, and p.29's unit is "dialed to zero". One unit at selection address 0 on its own channel is exactly the IPL configuration (rule 4). |
| Persistent `tapePos` as a concept | **Survives.** Its representation does not (§2.2 item 2). |
| REWIND 136/137 → position 0 | **Survives** as the position effect. The *indication* does not: 136 must give EOP at initiation and CS at completion (rule 25). |
| BACKSPACE BLOCK 176 → position − 1, EPGK at load point | **Survives, and is right.** Rules 26–27. |
| Not distinguishing 136 from 137 | **Survives for IPL**, breaks for KA UL1-style use, which relies on UNLOAD leaving the reel unmounted (§3.4 item 5). Cheap to add a one-bit `unloaded` state. |
| Synchronous whole-block transfer | **Survives.** Nothing in the IPL or initialization path requires CPU/IO overlap; the real drivers poll (rule 37). |
| Reject vs. status-bit split (UNRJ for an uninstalled channel, EPGK for a wrong-op) | **Survives**, and is exactly right for tape (rules 29, 35). |
| `W`'s "+2" quirk deliberately not reproduced | **Survives** for IPL; note that a driver doing `CCW` after a `W` and arithmetic on the count will see a 2-word discrepancy versus a real machine. |

### 2.2 What must change

Line counts are rough and are anchored on `docs/exchange_and_io.md`
§6.2's own estimates ("729 IV + 7613 tape control, full CTL table, tape
marks, LOC for 8 drives: 400–600 lines"; "IPL sequence: 60–120"), not
invented fresh.

1. **The backing store stops being a flat word `Vector`.** `typedef 16
   TapeWords` + `Vector#(TapeWords, Reg#(Word64))` cannot express
   variable-length records, tape marks, or ragged word ends (rules
   12, 13, 15, 18). Replace with a byte image plus a record table:
   `Vector#(TapeBytes, Reg#(Bit#(8)))` and `Vector#(TapeRecs,
   Reg#(RecDesc))` where `RecDesc = { start, length }` and a tape mark
   is a `length == 1` record holding `0b0001111`. ~50–70 lines
   (types, storage, accessors, testbench load/inspect methods).
   *This one change is what unlocks items 3 and 4 below* — every
   CONTROL code the current file declines to implement declines for
   want of it.
2. **`tapePos` becomes a pair.** `TapePos` → `{ recIdx, byteOff }`, plus
   an `atLoadPoint` predicate (`recIdx == 0 && byteOff == 0`) that rule
   27's EPGK already wants and that rule 23's density check will want.
   ~15–25 lines, plus matching edits in `StretchExecute.bsv`'s `IoOp`
   case and `StretchCore.bsv`'s `ioPending` FSM where `devIdx` is
   seeded and written back.
3. **The remaining CONTROL codes.** 076, 077, 117, 176 (re-expressed on
   records), 177, 016, 036, 037, 056, 057, 156, 157, with the EE/EOP
   rules of 19 and 26. ~70–100 lines, almost all of it a case arm per
   code plus three shared helpers (space-one-record,
   space-to-tape-mark forward, space-to-tape-mark backward).
4. **Tape-mark EE/EOP on READ**, including "no data transferred, control
   word not modified" and the single-vs-multiple-record EE/EOP split
   (rule 19). ~25–40 lines, mostly in the `StretchCore` FSM.
5. **Chain and refill in the transfer FSM. This is the IPL blocker and
   should be done first.** The file's own header says chain and multiple
   "are captured in the control word… but the transfer FSM in
   StretchCore ignores them". The IPL fixed control word is
   `chain = 1, count = 1, refill = 4` (rule 9); with chain ignored the
   bootstrap reads one word and stops. Figure 36's 16 rows are already
   transcribed in `docs/exchange_and_io.md` §3.3. ~60–100 lines in
   `StretchCore.bsv`, not in `StretchIO.bsv`.
6. **The IPL mechanism itself**: an IPL input to the module, the
   reset-everything step, the "interpret the next channel signal
   specially" latch, synthesis of the fixed control word into the
   signalling channel's control-word slot, and the initial-start handoff
   to the CPU (rules 5, 6, 9, 10). ~60–120 lines split between
   `StretchIO.bsv` and `StretchCore.bsv`.
7. **An externally-triggerable channel signal per channel**, with the
   two tape sources — not-ready→ready, and REWIND completion (rules 7,
   8, 25). The current `unitReady` is "fixed at 1 (installed)… there is
   no not-ready/busy state to model"; IPL needs the *transition*, not
   the level. ~20–30 lines.
8. **The SEOP status bit must be set at issue and cleared at
   completion** (rule 31). `ControlWord.seop` exists in the struct and
   is never written by `StretchIO`. Without this, KA UL1's polling loop
   — and by §3.4's evidence the idiom every real 7030 tape driver uses —
   spins forever. ~10–20 lines.
9. **Indicator propagation.** The header's "NOT PROPAGATED" note
   (ind_EPGK, ind_UK, ind_EE, ind_EOP, ind_CS, and the Channel Address
   register at word address 5) has to close before `BRANCH ON
   INDICATOR` can drive a tape driver. ~30–50 lines in
   `StretchExecute.bsv`.
10. **`LOCATE` and an 8-unit control.** Needed only if §3.6's open
    question resolves against the simplification. A per-channel
    `selectedUnit` register, eight tape images, LOCATE's bits 47–49
    decode, the non-existent-address → channel-not-ready rule, and
    per-unit status attribution (rules 3, 38; RefMan printed p.133 =
    PDF p.136). ~80–120 lines **plus 8× the storage**, which on a
    ULX3S is the real cost.

Order to do them in: 5, 8, 6, 7 (IPL works), then 1, 2 (records exist),
then 3, 4 (the CTL table falls out), then 9, then 10 if needed.

---

## §3. The six questions, answered

### 3.1 The IPL sequence end to end — what the tape sees

The tape unit sees **nothing until a human readies it**, then **one
ordinary single-block READ**, and nothing else. There is no special tape
mode, no boot record format enforced in hardware, and no handshake
beyond the standard channel interface.

In order: operator mounts a file-protected reel on a unit dialled to 0,
density HIGH (`C22-6678-1` p.29, Input). Operator presses IPL (step 3),
which per RefMan printed p.125–126 terminates programs, disables
interrupts, terminates all exchange operations, zeroes all exchange
control words, arms the "next channel signal is special" latch, and
resets all I/O units to initial power-on status — which for tape means
rule 5's odd-parity / no-ECC / high-density / unit-0 reset. Operator then
causes a channel signal on the chosen channel (step 4). The exchange
plants `addr 4 / chain 1 / multiple 0 / skip 0 / count 1 / refill 4` in
that channel's control-word slot and starts a READ. The tape control
begins streaming the first block byte-at-a-time; the byte converter
turns 4 six-bit frames into 3 eight-bit bytes; the first 64 bits become
the word stored at location 4, the count exhausts, the chain flag causes
a refill *from location 4*, and reading continues inside the same block
under the control word the tape itself just supplied. At the gap the
operation ends; the exchange raises initial-start; the CPU executes the
instruction at the new control word's data word address, which must be
BRANCH DISABLED.

**What a Signal key is, in Exchange terms.** It is a physical key whose
only function is to assert the `Channel Signal` line of the channel
interface (R23-9702 printed p.28, as transcribed in
`docs/exchange_and_io.md` §3.13: "active when the reader is initially
placed in a ready status or when the signal key is depressed";
generically, RefMan printed p.129 = PDF p.132: "Depression of the signal
key when the unit is ready generates a channel-signal indication which
is sent to the computer to interrupt the program as soon as conditions
permit"). During IPL that one line does two jobs at once: it *starts*
the load, and it *names the channel to load from*, because the exchange
plants the fixed control word "in the control word location for the
channel responsible for the channel signal". No channel number is
entered anywhere. **A 729 IV drive does not have this key** (rule 7),
which is why `C22-6678-1` says "on the adapter unit".

**How many words/bytes.** Exactly one word (rule 9) under the fixed
control word, then however many the tape's own first word asks for.
`ja_uc1a` (PDF p.2 = printed p.1 §1.1, and PDF p.3 = printed p.3 §4.1)
gives a real figure for one such tape: its control routine "occupies
locations 64–192" — 129 words — and "the lower portion 100 - 777"
octal is "reserved for the Tape Loader".

### 3.2 Tape marks and file structure

Rules 17–20 and 26 are the whole mechanism: a tape mark is a one-byte
block holding `0001111`, written only by CONTROL 117, detected by being
a one-byte block, and reported as **EE** (plus EOP except in
multiple-record mode).

**Is the master system tape multi-file?** `C22-6678-1` p.29 calls it the
"master system tape" and says the initialization program reads "the MCP
portion" of it and copies "the entire tape" to disk — the word *portion*
implies structure, and `$DATE OF IPL TAPE` (p.30) implies a label record
that must be found and read. But I could not establish the file layout
from `C22-6678-1`: pp.29–30 never use the words "file", "tape mark" or
"record" about the system tape, and Appendix B's tape-mark operations
are a driver inventory, not an initialization trace.

What *is* established, from an independent 7030 system tape, is that
this class of tape is navigated **by reading, not by tape marks**.
`ja_uc1a` PDF p.3 (printed p.3, §4.1 and the CONTROL RECORD flowchart):
"Each Maintenance Switch from 0 to 31 corresponds to one program on the
Maintenance Tape. **Forward movement of tape causes that record to be
loaded into memory. Backward movement is by Backspace or Rewind.** The
control routine interrogates the maintenance switches, searches the tape
for the corresponding sequence number and gives control to the main
program." The flowchart's loop is: read a control record → is this ID
selected? → are any selections above the current tape position? → if
not, **"Backspace To First Selection"**. Space File never appears. *My
inference, flagged:* an MCP initialization program finding "the MCP
portion" most likely does the same — read the label, read forward,
backspace if it overshot — which puts 076/176 ahead of 077/177 in
priority, but I could not confirm it for MCP specifically.

### 3.3 Record/block structure and density

Covered by rules 12–16 and 21–23. In one paragraph: records are
**variable length**, delimited by ¾-inch gaps, with no length field; the
reader learns the record ended when the data stops and the gap arrives;
a 64-bit word is 10⅔ six-bit frames in no-ECC mode and exactly 12 in ECC
mode, and words are **not frame-aligned**, so the honest model of a
block is a bit string, with the word boundary imposed by the exchange's
count and the tape control's byte converter (4 six-bit ↔ 3 eight-bit).
Density changes the **bit rate only** — 556 vs 200 bpi, 62,550 vs 22,500
6-bit bytes/sec — not the encoding; but because a tape must be read at
the density it was written, density is a correctness property, not a
performance knob, and in the wrong direction (high reading low) the tape
silently stops after one byte with **no error indication**. "Dialed to
zero" (`C22-6678-1` p.29) is the drive's Address Selection Switch (rule
2) and has nothing to do with density; "Density… set to HIGH" is
redundant with the IPL reset (rule 5) and is belt-and-braces by the
operator.

### 3.4 The CONTROL codes a real driver uses — and the strongest evidence in this document

Rule 24's table is the enumeration. The distinction the task asks for —
"the manual documents it" vs. "MCP uses it" — now has a third, better
column, because `ka_ul1` contains a **real 7030 tape driver in STRAP
with IBM's own machine code printed beside it**.

`ka_ul1_load_and_tape_write_util.pdf` **PDF p.17**, section header
`@@@TAPE WRITE` (read at 200 dpi; the machine-code columns below were
re-read at 600 dpi on a crop). The whole I/O portion, transcribed:

```
LOC%SEOP□,0%$X1□,0%$X2□   @LOC TAPE.          0.00 81 000000.17
CCW,0%$X1□,LDRCCW                             0.00 81 000164.21
BB,LDRCCW&.24,$-1.0                         164.30 80 000565.74

W%SEOP□,0%$X1□,END        @WRITE IPL TAPE.    0.00 81 000576.13
CCW,0%$X1□,LDRCCW                             0.00 81 000164.21
BB,LDRCCW&.24,$-1.0                         164.30 80 000570.74

UNLOAD%SEOP□,0%$X1□       @UNLOAD TAPE.       0.00 81 000137.15
CCW,0%$X1□,LDRCCW                             0.00 81 000164.21
BB,LDRCCW&.24,$-1.0                         164.30 80 000573.74

B,B5                      @START PROGRAM.   343.10 00
END   XW,0,0,0                                0.00 00 000000.00
```

Five things fall out, all of them primary-source:

1. **The entire IPL tape is written by ONE `W`.** Not a chain of
   records, not a tape mark, not a label — one WRITE against one control
   word built at `END` by the immediately preceding block
   (`ST%BU□,END  @TAPE WRITE CW.`, with the count computed from
   `MIC − LIC`). `WRITE TAPE MARK` is therefore *not* needed to make a
   bootable tape. (That **a single block is all IPL can ever read** is
   established from the other side and more cleanly: the fixed control
   word has `multiple = 0`, so by Figure 36 the operation ends at the
   first end-of-block. I did not decode the multiple flag of the
   control word KA UL1 builds at `END`.) The same preceding block
   stores two words it labels
   `@IPL CW.` and `@IPL BD.`; *my inference, flagged* — those are the
   control word destined for core location 4 and the BRANCH DISABLED
   that rule 10 requires, i.e. the first two words of the block.
2. **It uses `LOCATE` — unconditionally, even for drive 0.** The
   preceding block builds `$X1` from the channel (switches 12–17) and
   `$X2` from the drive (switches 21–23), per PDF p.2 (printed p.2):
   "Switches 12-17 are used for the channel selection and 21-23 are used
   for drive selection. If channel 32 (40₈) and drive 0 are to be used,
   these bits may all be set to zero." The `LOC` is issued with no test
   for drive 0.
3. **The CONTROL function code really is a raw literal in the right
   effective address.** `UNLOAD` assembles to right address
   **`000137`** — octal 137, REWIND AND UNLOAD — confirming
   `strap_asm.py`'s choice not to apply the `>>6` word-address
   conversion to `CTL`'s second field, against IBM's own assembler
   output. (`LOC`'s right address is `000000` = drive 0; `W`'s is
   `000576` = the control word at `END`; `CCW`'s is `000164` = `LDRCCW`.)
4. **Every operation is the SEOP form**, and completion is detected by
   `CCW` + `BB` on **bit 24**, the SEOP status bit (rule 31). This is
   the real 7030 tape-driver idiom, and it is exactly the loop that
   `StretchIO.bsv`'s own header anticipated ("COPY CONTROL WORD is how a
   program observes EOP/EE/etc. here") — except that the bit it polls is
   one the model never writes.
5. **REWIND AND UNLOAD is load-bearing, not decorative.** PDF p.2: "At
   the completion of writing the IPL tape, the tape write routine will
   unload the tape so that it cannot be destroyed by the program. As
   soon as the EOP is received from the unload instruction, the tape
   write routine will branch to the location loaded from the branch
   control card." So `StretchIO.bsv`'s collapsing of 136 and 137 into
   one behaviour is a real, if small, gap.

For MCP specifically, the bound is: Appendix B (printed pp.43–46)
documents a macro for **every** code in rule 24's table, so MCP's driver
layer implements all of them; but Appendix B is an inventory of what
MCP *offers*, and for *initialization* I could establish only rules 5
and 29's implicit requirements plus rule 25's REWIND. Everything else in
the "plausible" column is plausible and unproven.

### 3.5 Indicators and error paths

Rules 29–38. The minimum set for a non-hanging driver is **Unit Ready**
(or the first instruction is rejected and never starts), **EOP**,
**the SEOP status bit** (§3.4 item 4 — without it the real polling idiom
spins forever, and this is the one most likely to be overlooked because
it is a *status* bit named after an *instruction* modifier), **EE** (the
only way a read of a tape mark or an overrun terminates), **UK** and
**EPGK** (the two error exits a retry loop branches on), and **CS** (the
only completion report for REWIND, rule 25). `EKJ` and `CBJ` are exchange
rejects, not tape conditions, and are listed with their conditions in
`docs/exchange_and_io.md` §3.8.

### 3.6 Unit addressing — does one-unit-per-channel break MCP?

**Answer: it survives IPL exactly, and I could not establish that it
survives initialization. The evidence leans against it.**

*It survives IPL, and not by luck.* IPL forces selection address 0 twice
over (rule 4), the IPL reset points the control at unit 0 before any
instruction runs (rule 5), and the channel signal identifies a channel
rather than a unit (rule 8). A model with exactly one tape unit, at
selection address 0, on its own channel, is **isomorphic to the post-IPL
state of a real tape control**. `C22-6678-1` p.29's "dialed to zero" and
`ja_uc1a`'s "Tape Unit 0, any channel (input)" both describe that state.
Nothing in the IPL path can tell the difference.

*Three pieces of evidence that it does not survive what comes next*, in
increasing strength:

1. `C22-6678-1` p.29 procedure step 6: "**Mount the system tapes** as
   directed by the mounting messages issued by the initialization
   program. (If key 28 is on, the IPL mounting messages are
   suppressed.)" Plural, and after the IPL read.
2. `C22-6678-1` p.30, I/O Assignment Messages, verbatim:
   `$MCPIPL*MOUNT-REEL NUMBER 'reel' CHANNEL XX UNIT Y`. **The
   initialization program's own message names a unit number.** A program
   that prints `UNIT Y` and then reads that reel must have issued a
   LOCATE for Y, by RefMan printed p.111's rule that all READ/WRITE/
   CONTROL apply to the last-located unit.
3. `C22-6678-1` p.29, I/O Status Report, numeric switch columns: "7 and
   8 — Channel number of the device. 15 and 16 — **Tape unit number.**
   If the device is not a tape unit, these two columns are not used. If
   an entire tape channel is unavailable, put 08 in columns 15 and 16."
   MCP's device identity is the pair (channel, unit), and 08 is reserved
   as the "whole channel" escape precisely because 0–7 are real units.

*And one piece that complicates it.* MCP's documented I/O operation list
(`C22-6678-1` Appendix B, printed pp.43–46, all four pages read)
contains **no LOCATE-a-unit operation at all**. The one `MLOC`/`$LOC`
entry is **Locate Arc**, a disk operation whose own error list says
"EPGK (Tape, Console, Reader, Punch, or Printer) Invalid operation"
(printed p.43). Every MCP tape operation takes a symbolic `IODNAME(I)`
instead. So unit selection in MCP is *below* the documented interface —
inside the IOD tables and the channel scheduler — which is exactly where
I cannot see it without reading the MCP source listing.

**What this means for the model.** Build the IPL path on the existing
one-unit-per-channel shape; it is correct there, and the cost of LOCATE
(§2.2 item 10: ~80–120 lines *and eight tape images*) is the single
largest storage item on the tape side of a ULX3S port. But treat
`MOUNT-REEL … CHANNEL XX UNIT Y` as notice that the simplification has a
known expiry date, probably before the first mounting message. Note
separately that MCP's minimum configuration (`C22-6678-1` p.6, via
`docs/exchange_and_io.md` §2) wants **four** 729 IVs — system output,
alternate system output, system read, system write — so the
simplification certainly fails for *running* MCP whatever happens at
initialization.

**What would settle it in one search.** Grep rendered pages of
`MCP_Mar63_001-249.pdf` / `MCP_Mar63_250-445.pdf` for `$LOC` in the tape
IOD, as `docs/NEXT.md` §5h already proposes for the disk. One hit turns
this from leaning to established.

---

## §4. Bounded negatives and open questions

### 4.1 Bounded negatives — searched, and not there

1. **RefMan pp.129–136 (PDF 132–139) never give an on-tape *label* or
   *header* format.** All eight pages were read. The chapter defines
   gaps, blocks, tape marks, parity and the byte converter, and stops.
   Any "system tape" structure is software convention.
2. **RefMan pp.133–136 never mention a record length field, a record
   count, or a block header.** Record length is implicit in the gaps
   (rule 12) and nowhere else.
3. **RefMan printed p.136 = PDF p.139 states positively that a 729 IV
   has no Signal key.** This is the negative that resolves
   `C22-6678-1` p.29 step 4 — the key is on the adapter.
4. **`C22-6678-1` pp.29–30 never say how many words the IPL read
   transfers, nor where in core MCP lands.** The figure and the
   procedure are operator-facing only.
5. **`C22-6678-1` pp.29–30 never use the words "file", "tape mark",
   "record" or "label" about the master system tape.** "Portion" is the
   only structural word on the page.
6. **`C22-6678-1` Appendix B, printed pp.43–46, all four pages read,
   contains no LOCATE-a-unit operation.** `MLOC`/`$LOC` is Locate Arc
   (disk) and is explicitly invalid for tape.
7. **Appendix B gives no CONTROL octal codes.** It names macros and the
   status bits each may set; the octal is only in RefMan printed p.132.
8. **`ja_uc1a`'s loader flowchart (PDF p.3) uses no Space File and no
   tape mark.** Navigation is read-forward plus "Backspace To First
   Selection" plus Rewind.
9. **`ka_ul1`'s tape writer (PDF p.17) writes no tape mark and no
   label.** One `W`, one block, then UNLOAD. A bootable 7030 tape has no
   mandatory preamble.
10. **`ka_ul1`'s prose (PDF pp.1–3 = printed pp.1–4) never describes the
    on-tape byte layout.** The format is implicit in the control word,
    not documented. The listing is the only authority, and the listing
    shows a straight image write.
11. **`C28-6379-0` is not about IPL.** Printed p.3: "The IBM 7030 system
    loader consists of two programs: (1) the resume load program of MCP,
    with the loader as a subroutine, and (2) the Binary and Symbolic
    Subroutine (BSS) processor." Cover abstract and printed p.3 read;
    it handles relocatable/absolute binary *card* decks for problem
    programs. Nothing here constrains the tape unit.
12. **RefMan printed p.132's REWIND entry does not say the SEOP status
    bit is cleared at completion**, and neither does printed p.121. The
    clear is inferred from KA UL1's polling loop (rule 31).
13. **No document read here gives a model number for the "adapter
    unit".** `C22-6678-1` p.29 says "adapter unit", `ka_ul1` printed p.2
    says "Tape Adapter Unit (TAU)", the Reference Manual says "tape
    control", and `docs/exchange_and_io.md` §2 identifies the machine as
    an IBM 7613 from the physical-planning manual. I did not confirm
    that TAU and 7613 are the same box.

### 4.2 Open questions

1. **Does MCP's initialization program issue `LOCATE`?** §3.6. The
   decisive source is the MCP source listing
   (`MCP_Mar63_001-249.pdf` / `MCP_Mar63_250-445.pdf`, 451 pages, no
   text layer, still unread), not any manual.
2. **What is the on-tape structure of the master system tape?** How many
   files, is the MCP portion first, is there a label record, is it found
   by reading or by spacing. Unresolved; §3.2 gives the best available
   analogue and flags it as an analogue.
3. **A conflict, recorded rather than averaged.** RefMan printed p.132 =
   PDF p.135 says REWIND AND UNLOAD gives "**No channel signal… upon
   completion of the operation**". `C22-6678-1` printed p.45 lists
   `$UNLD` as reporting "**CS** — `$UNLD` completed and new tape at load
   point". Both read first-hand. Possible reconciliations (none
   verified): MCP's CS is the *operator remounting* a new reel, which
   the wording "new tape" supports; or MCP's table is loose. An
   implementer should follow the Reference Manual and treat the MCP
   entry as describing the operator cycle.
4. **Does the model need ECC mode at all?** IPL resets to no-ECC (rule
   5) and never leaves it. If MCP writes its scratch tapes in ECC mode,
   the 12-byte / 72-bit word layout of rule 14 becomes load-bearing.
   Unestablished.
5. **Three tape diagnostic decks named but absent.** `docs/NEXT.md` §5h
   already names `JA EE3` (BX/TAPE), `JA CE1`/`CE2` (tape) and
   `JA ES1D` (I/O single channel) from
   `7030_SystemTestPrograms_Aug61.pdf`. None is in `docs/`. Those are
   the runnable oracles this contract lacks; `ka_ul1` PDF p.17 is
   currently the only executable tape code in the repository, and its
   I/O portion is ten instructions long (LOC, CCW, BB, W, CCW, BB,
   UNLOAD, CCW, BB, B — the trailing `XW` is the control word, not an
   instruction).
