# MCP's I/O control tables, and a transcription checked against them

`docs/C22-6728-1_7030_MCP_Sys_Analysis_Guide.pdf`, **Appendix A,
"Symbolic I-O Control Tables"**, printed pp.261-268. **PDF page =
printed page.**

This note exists for two reasons. The first is that it is an
**independent check on a transcription**: `decks/mcp_bootstrap_p17`
and `p18` were read off the MCP listing's BINARY OUTPUT column and
verified bit-for-bit against it, and this appendix — a different
document, written for a different purpose, by people documenting
rather than coding — names the same bits, with the same polarities,
in the same tables. The second is that it is the specification any
IOCD work has to be built against.

## The check

| MCP row (transcribed) | the row's own comment | Appendix A |
|---|---|---|
| p.17 line 23 `CM1111(BU,1),.25($5)` | `-CHANNEL NOT AVAILABLE BIT TO ON` | **.25 SCHAVL** — "0 Channel is available / 1 Channel is not available… **It is set at IPL**" |
| p.17 line 44 `CM0000(BU,1),.25($3)` | `-YES * CHANNEL AVAILABLE FLAG TO ON` | same bit, written ZERO — and zero is the *available* state |
| p.17 line 24 `CM1111(BU,1),.29($5)` | `-NOT ASSIGNED BIT ON IN CST` | **.29 SUNASG** — "0 Unit is assigned / 1 Unit is not assigned" |
| p.18 line 9 `CM1111(BU,1),.27($3)` | `-YES * MULTI BIT TO ON IN CST` | **.27 SMULTI** — "0 Single-unit channel / 1 Multi-unit channel… It is set at IPL" |
| p.18 line 21 `CM1111(BU,1),.28($15)` | `-UNIT AVAILABLE BIT TO ON` | **.28 SUNAVL** — "1 Unit is not available… exists in the channel status table for single unit channels and **in the unit status table for multi-unit channels**" |
| p.18 line 22 `CM1111(BU,1),.29($15)` | `-UNIT NOT ASSIGNED BIT TO ON` | **.29 SUNASG**, likewise "in the unit status table of multi-unit channels" |
| p.18 line 5 `SV,$15,0.0($3)` | `-INSERT UNIT STATUS TABLE ADDRESS IN CST` | **.00-.17 SUNAA** (single) / **.00-.27 SUNNA** (multi) — "the address of the first entry in the unit status table for the channel" |

**THE POLARITIES ARE THE SHARP PART.** Three of these bits mean the
NEGATIVE: 1 is *not* available, *not* assigned. A transcription that
had `CM1111` and `CM0000` the wrong way round would still assemble,
still match a listing read carelessly, and still look plausible — and
it would disagree with this table everywhere. It does not.

**AND SO IS THE CST/UST SPLIT.** `SUNAVL` and `SUNASG` live in the
CHANNEL status table for a single-unit channel and in the UNIT status
table for a multi-unit one. Printed p.18 sets them indexed by **$15**,
which printed p.18 line 5 has just pointed at the unit status table,
on a path that printed p.18 line 9 reached by setting SMULTI. Two
documents agreeing about which table a bit is in, through an index
register.

## What else the appendix gives, unused so far

- **`.32-.49 SARCAD`**, multi-unit channels only: "the arc address of
  the last arc to be located on the disk… set by the actuator
  whenever a locate or read or write of the disk is completed." So
  MCP keeps its own copy of the arc address register the 7612 holds
  (`docs/disk_subsystem.md` §2.5) — the software mirror of the
  hardware cursor.
- **`.56-.58 SUNIT`**: which of up to eight units is selected on a
  multi-unit channel. The 7613 tape control's "up to eight 729 IVs,
  one active at a time" (`docs/resuscitation_roadmap.md` §4), in a
  three-bit field.
- `.26 SCHOP`, `.30 SUNSUP`, `.31 SSETUP`, `.32 SOWNER`, `.46 SSEOP`,
  `.61 SREL`, `.62 SUNRES`, `.63 SOVRES` — operating state, set by
  the actuator and receptor, none of it touched at IPL.

## The correction this forces: IOCD cards are NOT read from a reader

`docs/boot_plan.md` M3++ item **A3** said the next step was "an IOCD
card deck for the reader, which `strap/cards.py` can already punch".
**The evidence says that is wrong**, and it is worth stating before
anyone punches a deck.

`C22-6678-1` printed p.29, "INITIALIZING THE SYSTEM", gives the
operator procedure in six numbered steps. The input is:

> "The current MCP master system tape is file protected and mounted
> on any tape unit dialed to zero. Density for this unit is set to
> HIGH and the unit is made READY."

and the options are **console binary keys** — 0-23 time, 32-55 date,
28 suppress messages, 29 I/O status report, 30 rejected job count,
31 abnormal MCP mode. The six steps are: select options, set time and
date in the keys, press IPL, press Signal on the adapter unit, do the
I/O status report if wanted, mount the system tapes as directed.
**No card deck is mounted and no reader is mentioned.**

That agrees with the listing. Printed p.17 does not issue a card
READ: it **searches `X BUFER`** — the buffer the PROSA read filled
from the tape — with `BB,1.44($4)` and steps through it with
`CB+,$4`. And printed p.13 line 38 names that buffer
`X BUFER SYN,X IN END + 2000.0  - SLOTS LEFT FOR IOCD + IODS`.

**So the IOCD cards are card IMAGES ON THE SYSTEM TAPE**, put there
when the system was built — which is what the off-line IBM 1401 is
for (`C22-6678-1` p.6 requires one; card-to-tape is its first listed
job). A3 is therefore about the tape's content, not about the 7503.

**WHAT WOULD OVERTURN THIS**: a page that describes the IOCD card's
own format and says it is read at initialization.

**PRINTED p.40 HAS NOW BEEN READ AND DOES NOT OVERTURN IT** — see
`docs/mcp_tape_manufacture.md` §2.3b for what it does give, which is
the whole punched MCP deck in order with its eight PUNIDs. Its item 4
is "IOD cards", the problem-program card of p.8, and **IOCD is not in
the list at all**. "Format of the Input Tape" on the same page is
about the JOB stream, not the system tape.

So the IOCD card's own format is **still not located**, and the
places left to look are: the System Analysis Guide's IPL section
(`C22-6728-1`, sampled but not read for this question), its
UPDATE-30 writeup (printed **pp.228** ff. -- NOT §215, which is
Debugging Aids; verified 2026-10-28 against two running heads,
"Debugging Aids 215" on PDF page 215 and "Debugging Aids 221" on PDF
page 221, confirming PDF page == printed page for this edition), and the bulletin `C22-6718` which p.40 cites and
which is not in `docs/`. Recorded as open rather than guessed at —
printed p.17's usage shows a 12-bit Hollerith field pair for the
channel and a two-letter equipment code looked up in `X EQP T`, which
is enough to *recognise* an IOCD card and not enough to *write* one.

**NOTE ALSO** that the IOD card of `C22-6678-1` printed p.8 is a
DIFFERENT card: it is a problem program's symbolic I/O definition —
column 1 "B", columns 2-9 an IODNAME, columns 63-66 and 67-72 filled
in by the processors — and it describes a *logical* unit a job wants,
not a *physical* one the machine has. Two similar names, two
different purposes, and `X BUFER`'s comment names both.

## The chain from an IOCD card to the ASSIGN reject, traced 2026-10-26

`docs/NEXT.md` records that ASSIGN rejects and that `TAREJX` names
the reason -- `I/O REQ. INCOMP WITH MACH CONF.` What it did not
record is the mechanism, which is four transcribed pages and no
inference:

| step | page | what it does |
|---|---|---|
| 1 | p.17 | processes the IOCD cards, one per channel, into the channel status table |
| 2 | p.35 | `X EQPT` maps the card's equipment LETTERS to type CODES |
| 3 | p.72 | `TA9` clears the machine-configuration counts and recounts them from the channel status table |
| 4 | p.66 | `TCHEK` compares each type's REQUEST COUNT against its MACH CONF COUNT and rejects |
| 5 | p.74 | `TAREJX` sets `T MESSY` as the reason and the caller sees no disposition bit |

**Step 4 is the decision, and it is three instructions:**

```
TCHEK   LF, TRCAD(TX1)      line  9  -REQUEST COUNT TO ACC
        BRZ, TCONT          line 10  -NO REQUEST
        KF, TMCAD(TX1)      line 11  -COMPARE MACHINE CONF. COUNT
        BZAH, TCONT         line 12  -IF REQUEST IS OK
        CM1111, TRJECT(TIXE) line 13 -REJECT PP FOR REQ IS TO HIGH
```

So a reject needs a type whose REQUEST COUNT is **non-zero** (line 10
would otherwise skip it) and **greater than** its conf count.

### THE TABLE IS THREE WORDS AND THEY CAN BE READ DIRECTLY

printed p.64 line 6 is the REQUEST VALIDITY CHECK TABLE: `T DISK` at
`003652.00`, eight rows of `TYPE CODE, MACH CONF, REQ CNT`, one byte
each. Eight rows x three bytes is 24 bytes, which is **exactly three
words**, `0o3652`-`0o3654` = **1962-1964**.

As ASSEMBLED -- only DISK has a count, and it is the static default
before `TA9` has run:

```
word 1962  0x0101000200000300
word 1963  0x0004000005000006
word 1964  0x0000070000080000
```

What `TA9` SHOULD leave, given that `strap/prosa.py`'s deck is
`DK`/`RD`/`PR`/`TP(2 units)`/`CN` and p.35 maps those letters to
codes 1/3/5/8/2, if every request count is zero:

```
word 1962  0x0101000201000301     DISK 1, CONSOLE 1, READER 1
word 1963  0x0004000005010006     PUNCH 0, PRINTER 1, IQS 0
word 1964  0x0000070000080200     EXTRA 0, TAPE 2
```

**The equipment-letter mapping is not assumed.** printed p.35 lines
18-39 are `DD(BU,4)` constants: `DK`=1, `CN`=2, `RD`=3, `PU`=4,
`PR`=5, `TP`=octal 10 = 8 -- the same eight codes p.64's rows are
keyed by, in the same order.

> **THIS IS A MEASUREMENT, NOT A HYPOTHESIS, AND IT HAS NOT BEEN
> TAKEN YET.** Three words of the boot's final state say which type
> asked for more than the machine has, and therefore whether the
> fault is in the fixture's deck, in `TA9`'s count, or in whatever
> sets the request counts. `gen_tb.py:129` prints the actual value on
> a mismatch, so three checks with an impossible expectation read the
> table out of a boot run. Until those three numbers exist, **no
> explanation of the reject should be written down** -- two have
> already been written ahead of the evidence this week and both were
> wrong (see `docs/NEXT.md`, the supersession of `46ba25d`).

### The three outcomes, pre-registered

Written down before the probe runs, because the failure mode this
week has been fitting an explanation to whichever number appeared:

| conf bytes read back | what it means |
|---|---|
| `1,0,0,0,0,0,0,0` — the STATIC table | **`TA9` never ran.** The reject is not about a count being exceeded; the configuration was never installed, and the IOCD cards are not reaching p.72. |
| `1,1,1,0,1,0,0,2` | **`TA9` ran and counted this fixture's deck correctly.** Then whichever type has `REQ CNT > MACH CONF` is the culprit and p.66 line 13 is doing its job on a request the fixture should not be making. |
| all zero, type codes `1..8` intact | **Mid-pass.** p.72 line 10's `CM0000, TMCAD(TIXG)` cleared them and the halt caught the table between clear and recount. The probe must move earlier and says nothing about the reject. |

**`TIOREQ`'s first words settle the cheaper half.** The I/O request
table is printed p.62 line 28, `TIOREQ DRZ(BU,64),(TIOC)` with
`TIOC = 80`, at `003373.0` = word **1787**. If it is zero, there are
no requests at all, p.66 line 10's `BRZ` skips every row, line 13
never runs — and the chain above would be right about the machinery
and **wrong about which test fires.**

> **The addressing is verified rather than assumed.** `gen_tb.py:266`
> emits `core.mem.readWordReq(<addr>)` and `readWordReq` takes a
> `WordAddr`, so the check's address string is a WORD index, not a bit
> address. `prosa.XINEND_WORD` is 2870, the same range as 1962 and
> 1787. This is the same class of unit error as the sign that had to
> be superseded in `a2d66b8`, so it was checked against the emitted
> BSV and not against the shape of the neighbouring checks.

### Outcome (c) is RULED OUT, and (b) is predicted, before the run

`TA9` is not reached unconditionally. printed p.65 lines 6-9 are
ASSIGN's entry:

```
TASIGN  SWAPI, 12, $1, TASAVE   line 6  -SAVE INDEXES
        LX, TCTWDX, 0.0($15)    line 7  -OVERLAP AND MACHINE CONF TEST
        CM0000(BU,6), TMODE     line 8  -RESET INDICATORS
        BZXVZ, TA9              line 9  -IF A MACH CNF CHANGE
```

and p.65 line 9 is `TA9`'s **only** caller anywhere in the decks. So
whether the configuration is ever counted turns on one branch, and
every link in it is sourced:

* **The caller's word.** printed p.27 line 9 is `X242 XW,-1,0,0,4`,
  commented `-MODE`, and `$15` points at it (line 5's
  `LVI,$15,X242`). Assembled, it is `0x000001c000000000`.
* **Its fields.** `StretchTypes.bsv:90-97` gives `IndexWord` as
  `addr` IBM bits 0-23, `sign` bit 24, `flag` bit 25. The word has
  bit 23 (magnitude 1), bit 24 (sign) and bit 25 — so the value is
  **-1** and the `4` is the index FLAG.
* **The branch sense.** `ind_XVZ` is set from `x.addr == 0`
  (`StretchExecute.bsv:952`), and `opcodes.py:285-290`'s
  `BBZ`/`BZBZ` pairs fix the convention: `BZ<ind>` branches when the
  indicator is ZERO. `addr` is 1, so `XVZ` is 0, so **the branch is
  taken and `TA9` runs.**

> **AND TA9 CLEARS THE FIELD THAT BROUGHT IT THERE.** printed p.72
> line 5 is `CM0000(BU,24), 0.0($15)` — "CLEAR CON FIG CHANGE" — which
> zeroes the caller word's 24-bit value. So `-1` means "the
> configuration changed, count it", `TA9` counts once, and every later
> ASSIGN call finds zero and skips it.
>
> **That rules out outcome (c).** The counts cannot be caught between
> the clear and the recount at the halt, because `TA9` ran once, early,
> and ran to completion. **Outcome (b) is the prediction**: the conf
> bytes read `1,1,1,0,1,0,0,2` and some type's request count exceeds
> its conf count. If the probe shows the static table instead, this
> derivation is wrong somewhere and the branch is the place to look.

## >>> THE NUMBERS, AND THEY MATCH NONE OF THE THREE PREDICTIONS <<< 2026-10-26

Read out of a boot run, five probe checks and then a wider window of
thirteen. **The table was NOT relocated** -- `TTYARA` still reads
`0x01ea8000002007a7`, whose value field is `0x01ea80` = 125568 =
`1962 x 64`, and `TCOMBO` (24), word 1961, 1965 and 1966 are all
byte-identical to the assembled image. Only the table's own 24 bytes
changed:

| row | static (type, conf, req) | runtime | |
|---|---|---|---|
| DISK | (1, 1, 0) | **(0, 0, 1)** | changed |
| CONSOLE | (2, 0, 0) | **(1, 0, 0)** | changed |
| READER | (3, 0, 0) | **(37, 0, 0)** | changed |
| PUNCH | (4, 0, 0) | (4, 0, 0) | . |
| PRINTER | (5, 0, 0) | (5, 0, 0) | . |
| IQS | (6, 0, 0) | (6, 0, 0) | . |
| EXTRA | (7, 0, 0) | **(0, 0, 0)** | changed |
| TAPE | (8, 0, 0) | **(0, 0, 0)** | changed |

and `TIOREQ` (words 1787-1789) is **all zero**.

### What is now MEASURED, not inferred

1. **The reject is explained, and the four-page chain was right about
   WHICH test fires.** DISK's row has `REQ CNT` = 1 and `MACH CONF` =
   0. p.66 line 9 loads 1, line 10's `BRZ` does not skip it, line 11
   compares against 0, line 12's `BZAH` does not take the OK exit, and
   line 13 sets the reject bit. **One non-zero byte against one zero
   byte is the whole reject.**
2. **`TA9` RAN.** DISK's conf went 1 -> 0, which only p.72 line 10's
   `CM0000, TMCAD(TIXG)` does. So the `BZXVZ` derivation was right.
3. **`TA9` CLEARED THE COUNTS AND NEVER PUT THEM BACK.** Every conf
   byte is zero, including the three channels whose IOCD cards MCP
   demonstrably processed.
4. **AND THREE TYPE BYTES ARE CORRUPTED.** `CONSOLE` 2 -> 1,
   `READER` 3 -> 37, `EXTRA` 7 -> 0, `TAPE` 8 -> 0. **The counting
   loop has no business writing a type byte at all.**

> **ALL THREE PRE-REGISTERED OUTCOMES WERE WRONG**, and it is worth
> saying so plainly. (a) said the static table; it is not. (b) said
> `1,1,1,0,1,0,0,2`; the conf bytes are all zero. (c) said all-zero
> conf with the type codes INTACT; the conf bytes are zero but four
> type codes are not intact. The pre-registration still did its job --
> it stopped the fourth reading from being dressed up as a prediction.

### THE HYPOTHESIS THIS POINTS AT -- labelled, and not yet tested

`TA9`'s write target is computed, not indexed, and the computation is
VFL arithmetic at two different offsets:

```
line 17  L, TEQUIP(TIXF), 40      -GET EQUIP FOR MACH CONF
line 19  *(BU,24), TCOMBO, 40     -COMPUTE LOC WITHIN TABLE
line 20  -(BU,24), T2COMB, 20
line 21  L(BU,64), $R, 20         -LEFT SHIFT TO VF
line 22  LV, TIXG, $R
line 26  M+, TDISK(TIXG)          -ADD CONFIGURATION TO TABLE
```

**The intended address is arithmetic this project can check.**
`TCOMBO`'s value field is 24 and `T2COMB` is p.63 line 22's
`VF, TTYBC+TMACBC` = 8 + 8 = **16**, so the offset is
`code*24 - 16`: for DISK (code 1) that is bit 8, exactly row 0's conf
byte, and for each later code exactly that row's conf byte. The
intent is unambiguous.

**So if `TIXG` comes out wrong, `M+` writes into a NEIGHBOURING byte
-- which is a type byte -- and no conf byte ever receives its
count. That is precisely the symptom measured above.** And the
operations that compute it are `*(BU,24)` at offset 40 and `-(BU,24)`
at offset 20: VFL multiply with an offset, which **was built in this
session**.

> **NOT A CONCLUSION.** The symptom fits, the arithmetic is sourced,
> and the suspect instruction is new -- but "fits" is what the last
> two wrong explanations also did. The test is a deck that runs
> p.72 lines 17-22's exact sequence for each of the eight equipment
> codes and checks `TIXG` against `code*24 - 16`, with a measured
> injection. That deck is the next thing to write, and it needs no
> boot run to be decisive.

## THE CHANNEL STATUS TABLE IS PERFECT, AND THE WRITES ARE ONE BYTE LOW

Two more probe runs. `TCHSXW` (printed p.67 line 84, `(8)2152.0` =
word 1130, inside the communication region) reads
`0x02bf800000900000`, whose value field is `0x02bf80` = 180096 =
**word 2814**. Decoding `TEQUIP` — p.63 line 10's `SYN(BU,4), 0.52`,
so IBM bits 52-55, which is `(w >> 8) & 0xF`:

| word | channel | TEQUIP | device | IOCD card |
|---|---|---|---|---|
| 2814 | 0 | 1 | DISK | `(0, "DK", ())` |
| 2846 | 32 | 3 | READER | `(32, "RD", ())` |
| 2847 | 33 | 5 | PRINTER | `(33, "PR", ())` |
| 2848 | 34 | 8 | TAPE | `(34, "TP", (2,0))` |
| 2849 | 35 | 2 | CONSOLE | `(35, "CN", ())` |

**Every card MCP was given is in the table with the right code.** So
the configuration reached `TA9` and the fault is not upstream: p.72
line 17's `L, TEQUIP(TIXF), 40` has something to load and line 18's
`BRZ, TB9B` has no reason to skip.

### The writes land at `code*24 - 24`, not `code*24 - 16`

The changed bytes of the conf table are flat 0, 1, 2, 3, 6, 18, 21.
Against the intended offset and against one eight bits lower:

| device | code | intended byte | `-24` byte | measured |
|---|---|---|---|---|
| DISK | 1 | 1 | 0 | **hit** |
| CONSOLE | 2 | 4 | 3 | **hit** |
| READER | 3 | 7 | 6 | **hit** |
| PRINTER | 5 | 13 | 12 | miss |
| TAPE | 8 | 22 | 21 | **hit** |

**Four of five land exactly one byte low**, which is what subtracting
24 instead of 16 would do — and 24 is `TCOMBO`'s value, sitting at bit
0 of the same word whose bit 32 holds `T2COMB`'s 16. PRINTER is the
one miss and is not explained.

### >>> AND THE ASSEMBLER IS VINDICATED, SO THE MODEL IS IMPLICATED <<<

p.72's checked rows carry IBM's own printed machine code:

```
line 19  004227.40  003650.00 80  030024.21 90     *(BU,24),TCOMBO,40
line 20  004230.40  003650.40 80  030012.30 10     -(BU,24),T2COMB,20
line 21  004231.40  000011.00 80  000012.20 50     L(BU,64),$R,20
line 22  004232.40  000011.20 30                   LV,TIXG,$R
```

Line 20's operand address is **`003650.40`** — bit offset octal 40 =
32 — and it compiles bit-exactly against the listing. So `T2COMB` is
ADDRESSED correctly, and word 1960's bits 32-55 really do hold 16
(`0x0000180000001000`, `(w >> 8) & 0xFFFFFF` = 16). The printed
offsets confirm themselves too: 40 prints as `24.2` and 20 as `12.3`,
octal 24 = 20 and octal 12 = 10, each half the decimal offset, exactly
as the seven-bit-field-straddling-the-dot rule predicts.

> **So the encoding is right and the EXECUTION is wrong**, and the
> suspects are the two instructions whose offsets differ: a VFL
> multiply whose product offset is implied, and a VFL subtract reading
> a 24-bit field at bit 32. `docs/NEXT.md`'s PAU unification note has
> `*` carrying the **offset-20 (double-precision)** implied field, and
> an eight-bit error in where that product lands would shift
> everything downstream by exactly the one byte measured here.
>
> **STILL NOT A CONCLUSION.** The test is a self-contained deck that
> runs p.72 lines 17-22 for each equipment code and checks the
> resulting index value against `code*24 - 16`, with a measured
> injection. It needs no boot run, and it decides between the multiply
> and the subtract rather than assuming either.

## >>> AND THAT HYPOTHESIS IS REFUTED TOO -- BY A TEST, THIS TIME BEFORE IT WAS ASSERTED <<<

`decks/mcp_p72_conf_offset.strap` runs printed p.72 lines 17-22 on
their own for every equipment code the fixture presents, and **all
eight checks pass**:

```
code1_disk_offset     = 8        code5_printer_offset = 104
code1_index_value     = 0x80000000000   code8_tape_offset = 176
code2_console_offset  = 32       tcombo_reads_24      = 24
code3_reader_offset   = 56       t2comb_reads_16      = 16
```

The model computes `code*24 - 16` correctly for codes 1, 2, 3, 5 and
8; it reads `TCOMBO` as 24 at bit 0 and `T2COMB` as 16 at bit 32 of
the same word; and `LV` through `$R` lands 8 in the index value. **The
multiply's offset-20 product, the subtract at offset 20, and the
`.40` bit-offset read are all correct.** The deck's two `VF` cards
even assemble word 1053 to `0x0000180000001000`, byte for byte what
the live word 1960 holds.

> That is **three** wrong explanations in this session. The difference
> is that this one was written down as a hypothesis, given a test, and
> killed by the test before anything was built on it. That is the
> process working, and it cost one deck.

### What the measured bytes actually say, re-read without the hypothesis

Going back to the seven changed bytes with the arithmetic cleared of
suspicion, **two of them are correct behaviour**:

* **flat byte 1** (DISK's conf, 1 -> 0) is p.72 line 10's
  `CM0000, TMCAD(TIXG)` doing its job. The clear loop covers bytes
  1, 4, 7, 10, 13, 16, 19 and 22, and every one of those was ALREADY
  zero except DISK's -- so a correct clear changes exactly one byte,
  which is what happened. **The clear loop is fine.**
* **flat byte 2** (DISK's req, 0 -> 1) is p.66 line 3's
  `M+1, TRCAD(TX1)` counting MCP's own request for one disk. Correct.

That leaves **bytes 0, 3, 6, 18 and 21** -- the TYPE bytes of rows 0,
1, 2, 6 and 7, which are codes **1, 2, 3, 7 and 8**. The codes the
IOCD deck actually supplies are **1, 2, 3, 5 and 8**.

> **SO FOUR WRITES LANDED ON THEIR OWN ROW'S TYPE BYTE INSTEAD OF ITS
> CONF BYTE, AND THE FIFTH -- PRINTER, CODE 5 -- LANDED ON CODE 7'S
> ROW.** The first four are eight bits low. The fifth is forty bits
> HIGH. One constant offset error cannot produce both, so the
> remaining fault is not a constant, and guessing which one it is has
> now failed three times.

### The next measurement, and it is a watchpoint, not a guess

Stop inferring the writer from what it wrote. **Instrument the model
to report every write that lands in words 1962-1964, with the
program counter and the value.** `StretchStorage.bsv` funnels core
stores through one place -- the `storeW` RWire and `storeQ` -- so a
single `$display` guarded on the address range names the instruction
responsible, and MCP's own listing then says what that instruction
is. Five writes are expected and their PCs will say whether they come
from p.72 line 26 at all.

## THE WATCHPOINT NAMED THE WRITER, AND THEN CLEARED IT -- 2026-10-26

`StretchStorage` was instrumented to report every write landing in
words 1962-1964, and `StretchCore` to print `pcReg` when it fired
(one register write per rule -- the first attempt drew G0004, which
`rl_xmit`'s own comment warns about). Twenty-three writes:

| writes | PC (half-word) | listing | what |
|---|---|---|---|
| 3 | 82 | — | the image zeroed |
| 3 | 165 | — | a 494-word TRANSMIT, `src 6439 dst 1962`, loading the static table **correctly** |
| 8 | 4389 | `004222.40` | p.72's clear loop |
| rest | 4010, … | | later routines |

printed p.72's checked rows put line 11 (`V+C,T COMBO`) at
`004222.40`, and **line 10, `T CM9 CM0000, T MCAD(T IXG)`, is the only
STORE in the loop.** It ran exactly eight times -- the right count --
and six of the eight writes were right. The two for field offsets
**32** and **128** replaced the whole word instead of clearing one
byte.

### And the loop is CORRECT in isolation

`decks/mcp_p72_clear_loop.strap` runs lines 9-12 over a table whose
twenty-four bytes are all distinct, with `T TYARA`'s count of 8 and
`T COMBO`'s value of 24 decoded from the live index words. **All three
words pass.** Eight conf bytes cleared, nothing else touched. So the
instruction, the 24-bit stride, the 8-bit field at offset 8 and `V+C`'s
count-down are all right.

> **SO THE CORRUPTION DEPENDS ON BOOT CONTEXT, NOT ON THE LOOP** --
> which means memory contention, and that is a very different kind of
> bug from the three already ruled out.

### >>> AND THE SAME RUN REPORTED FIVE SILENTLY DROPPED STORES <<<

```
StretchStorage: store queue full, CROSSING-FIELD TAIL to 1240 LOST
                                                        1241 LOST
                                                        1243 LOST
                                                        1244 LOST
                                                        1246 LOST
```

`bsv/StretchStorage.bsv`'s own comment on that message says the core
"holds off arming for the clock the tail waits (`storeTailPending`,
folded into `busyXfer`), so nothing SHOULD arrive -- and the
`$display` says so rather than the comment, because **'should' is a
claim and a message is a measurement**."

**The measurement now contradicts the claim.** `storeQ` is
`mkUGSizedFIFOF(8)` and it fills during the boot, and when it does a
crossing-field tail is thrown away -- a half-written field, silently.
Words 1240-1246 are not the conf table, so this is not proved to be
the same fault; it is an independent defect found by the same run,
and it is the first mechanism on the list that can corrupt a word
without any instruction being wrong.

**That is where this goes next**, and it is a model bug rather than an
MCP question: either the hold-off is not covering every path that can
enqueue, or depth 8 is not enough, and the `$display` already says
which words to watch.

## >>> RETRACTED: THE FIVE DROPPED STORES WERE MY INSTRUMENTATION <<< 2026-10-27

The section above reports five `CROSSING-FIELD TAIL ... LOST` messages
from the MCP boot and calls them an independent model defect. **They
are an artifact of the watchpoint that found them.** Counting `LOST`
across every boot run of this session:

| run | `bsv/` instrumented | `LOST` |
|---|---|---|
| `probe_run.log` … `probe_run4.log` (testbench probes only) | no | **0** |
| `watch.log`, `watch2.log`, `watch4.log` | **yes** | **5** |
| `boot_verify.log` | no | **0** |
| two full suite runs | no | **0** |

The correlation is exact and it is with my `$display` calls — and, in
`watch4`, an extra rule and register in `StretchCore` — not with the
boot. Adding a rule changes Bluespec's schedule, and the schedule is
what decides whether `storeQ` fills.

> **THIS IS THE FOURTH WRONG FINDING OF THE SESSION AND THE THIRD
> CAUSED BY MY OWN TOOL.** The tell was available immediately and I
> did not look for it: a one-line fix that should only change what
> happens WHEN the queue fills made the messages vanish entirely,
> which means the queue stopped filling, which means the fix was not
> the variable. `stretch-working-method`'s rule -- "two facts from one
> run that cannot both be true" -- applies to two runs as well.

### What survives, and it is smaller

The code really did discard the tail: `tailNext` was set
`tagged Invalid` unconditionally, so a crossing-field tail that met a
full queue was thrown away — half a VFL field written and half not,
with no indicator. **That path is unreachable today**, which is what
`tests/run_tests.sh:2048-2058` already says about the neighbouring
hazard: the collision needs "a multi-cycle E-box retiring two stores
closer together", so "the guard is load-bearing FOR THE REBUILD
rather than for today."

`bsv/StretchStorage.bsv` now **holds** the tail instead of dropping
it, and retrying is safe and terminating because `writeReady()` is
`storeQ.notFull && !isValid(storeTail)` — the core arms no further
store while a tail is pending, and `memCtl` drains one queued store
every clock its unit is free.

> **AND IT HAS NO TEST, WHICH IS WORTH STATING.** No deck in this
> project can reach a full store queue, so the only evidence the
> change is harmless is the suite. It is kept because discarding a
> write is never correct and M1's multi-cycle E-box is what makes the
> path live — not because anything measured demanded it.

## >>> THE REJECT'S ONE BYTE HAS NO REQUEST BEHIND IT <<< 2026-10-27

`T IOREQ` is printed p.62 line 28's `DRZ(BU,64),(TIOC)` with
`TIOC = 80`, at `003373.0` = word **1787**. Thirteen probes across
words 1787-1866 of a boot run **all read zero.**

> **SO MCP HAS NO I/O REQUESTS AT ALL, AND DISK'S REQUEST COUNT IS
> STILL 1.** Those cannot both describe a legitimate request. The
> conclusion committed earlier -- "one non-zero byte against one zero
> byte is the whole reject" -- is still true about the MECHANISM and
> **wrong about the cause**: that byte is not MCP asking for a disk.

### Both clear loops are correct, so neither is the writer

| deck | printed source | result |
|---|---|---|
| `decks/mcp_p72_clear_loop.strap` | p.72 lines 9-12, `CM0000, T MCAD(T IXG)`, `V+C` | **all pass** |
| `decks/mcp_p65_reqcount_clear.strap` | p.65 lines 44-48, `ST, T RCAD(TX1)`, `V+CR` | **all pass** |

Both run over a table whose twenty-four bytes are distinct, with
`T TYARA`'s count of 8 and `T COMBO`'s value of 24 taken from the live
index words, and both have measured injections. Eight conf bytes
cleared in one, eight request counts cleared in the other, nothing
else moved in either.

### What this reframes

p.65 line 50 is `LVI, ..., T IOREQ` and p.66 line 3 is
`T C1 M+1, T RCAD(TX1) -INCREMENT REQUEST COUNT`, so the counts are
accumulated by walking `T IOREQ`. Walking an all-zero table yields
entries whose TYPE field is zero, and type 0 indexes **row 0 -- DISK**.
A phantom type-0 request incrementing DISK's count is consistent with
every byte measured, and p.66 line 1's `BD,$ -ILLEGAL REQUEST` is not
reached, so nothing rejects the blank entry as invalid.

**AND THAT POINTS AT THE FIXTURE.** `strap/prosa.py`'s
`TERMINATOR_CARD` is `(None, None, (), iocd.IOD_CARD_TYPE)` -- an IOD
card with every field blank, present only to END the IOCD scan. But
`C22-6728` printed p.88 says an IOD "perform[s] the same function for
MCP as [it does] for the problem program", and printed p.40's
`Y IODC` converts an **I-O reference number and absolute exit** off
it. A blank IOD is not a no-op to MCP; it is an I/O definition with
no content.

> **NOT YET A CONCLUSION, AND THE TEST IS NAMED.** printed p.62 line 6
> is `T PREFT XW, T IOREQ, 0, (.39)9` -- a pointer to the table with
> **count 0**. If that count still reads 0 at run time, MCP should not
> be walking the table at all and the walk is the model's fault; if it
> reads non-zero, something entered a request and the fixture's IOD
> card is where it came from. **One probe of word
> `0o3346`-ish's pointer settles which**, and it decides whether the
> next change is in `bsv/` or in `strap/prosa.py`.

### The pointer says NINE and the table says NOTHING -- 2026-10-27

`T PREFT` is `(8)3317.0` = word **1743**. At run time it reads
`0x01bec00009000000`:

```
value  0x01bec0 = 114368 = 1787 x 64   -- T IOREQ, correct
count  576
refill 0
```

printed p.62 line 6 declares it `T PREFT XW, T IOREQ, 0, (.39)9` --
**count 0** -- so the count was set at run time, and `576 = 9 x 64`
against a card whose refill operand is a **9**. The arithmetic is
suggestive and the parenthetical entry mode `(.39)` is not sourced
here, so 9-the-entry-count is **read, not proved**.

> **THAT ANSWERS THE EITHER/OR.** The count is NOT zero at run time,
> so MCP has every reason to walk the request table -- the walk is not
> the model inventing work. **What is wrong is that the table it walks
> is empty.** MCP has been told there are nine I/O definitions and
> finds none, and a blank entry's TYPE field of zero indexes row 0,
> which is DISK.
>
> **SO THE NEXT CHANGE IS IN `strap/prosa.py`, NOT IN `bsv/`.** The
> fixture supplies exactly one IOD card, `TERMINATOR_CARD =
> (None, None, (), iocd.IOD_CARD_TYPE)`, with every field blank and
> no I/O definition in it. Everything measured is consistent with MCP
> being correct about a machine whose I/O definitions were never
> punched -- which is the same lesson `prosa.py`'s own comment already
> records about the first IOCD deck: *"A configuration that lies about
> the machine makes MCP correct about the wrong machine."*

**What to do, and what to measure first.** The IOD card's field map is
NOT derived the way the IOCD card's was (`docs/boot_plan.md` has the
IOCD map from p.17's own increments; the IOD's fields are the ones
`C22-6728` printed p.88 declines to give because an IOD "perform[s]
the same function for MCP as [it does] for the problem program").
printed p.40's `Y IODC` lines 14-22 convert "I-O REFERENCE NUMBER AND
ABSOLUTE EXIT" off it, and **that conversion's own increments are the
same derivation method p.17 yielded to** -- so the map is obtainable
from a page already transcribed. Derive it, punch one real IOD, and
the request table should stop being empty.

> And **check the count before believing this too**: if nine
> definitions are expected, a fixture that punches one should move
> `T PREFT`'s count, and that is a probe of word 1743 away.

## >>> CORRECTION: T PREFT WAS NEVER TOUCHED, AND (.39)9 IS THE 576 <<< 2026-10-27

`604421e` said T PREFT's count "was set at run time" because the
static card reads `XW, T IOREQ, 0, (.39)9` and the probe read 576.
**Both halves of that were a misreading.** Assembling printed p.62
alone and comparing:

```
static  word 1743 = 0x01bec00009000000
runtime word 1743 = 0x01bec00009000000
```

**Byte identical.** The word is untouched, and `(.39)9` is a
parenthetical entry placing **9 at bit 39**, which falls inside the
count field (IBM bits 28-45) at `9 << 6` = **576**. The third
operand's `0` is the count OPERAND; the parenthetical overrides it.
So the count was 576 before the machine started and nothing set it.

> **AND THAT IS A STRONGER FACT THAN THE ONE IT REPLACES.** An
> untouched `T PREFT` means MCP's request-table machinery never ran at
> all -- not that it ran and got nine.

## WHERE THE REQUEST TABLE IS BUILT, AND WHY IT IS EMPTY

The builder **is** transcribed. It is MCP-DECODE's IOD path on printed
**pp.52-56**, reached through index register `LXIO` = `$5`, which
printed p.48 line 35 names "I.O. REQUEST TABLE INDEX". `LXIO` is
loaded with `T IOREQ` not by an `LVI` -- which is why grepping for one
found nothing -- but by a **SWAP of eight index words**: p.48 lines
22-29 are the "SWAP AREA FOR EIGHT MCP-DECODE INDICES" at `LTY`, whose
third word is `XW, T IOREQ, TIOC, LIOTBX` (count 80, self-refilling),
and p.52 line 1 is

```
LDECOD  SWAPI, 8, LTY, LIODX
```

which covers `$3..$10` so word three lands in `$5`. p.58 line 5 swaps
them back out on the normal return.

**The chain, end to end:**

| step | page.line | what |
|---|---|---|
| 1 | p.38 L34 | `B, Y IODC` |
| 2 | p.40 L14-22 | convert the card's two fields to binary in `$12` |
| 3 | p.41 L4 | `Y NORR SX, $12, 0.0($14)` -- hand them to the caller |
| 4 | p.52 L1 | `SWAPI, 8` loads `LXIO` = `T IOREQ`, count 80 |
| 5 | p.53 L27 | `SV, LXIO, 0.0(LXPP)` -- the slot's address into the PP table |
| 6 | p.53 L38 | `L, LIREF(LIODX), 0.0` reads the **12-bit reference number** |
| 7 | p.54 L16,19,21 | `ST(BU,4), TTYPE` / `ST(BU,9), TIODSQ` / `V+ICR` to the next slot |
| 8 | p.55 L5,27 | `ST(BU,4), TTYPE` / `ST(BU,7), TRLSYM` |
| 9 | p.56 L24 | `ST(BU,18), TFREEL(LWORKX)` |
| 10 | p.57 | the search and sort already known |

**And the card-to-table link is the 12-bit reference number, not the
18-bit exit.** p.40 line 21's `SF(BU,12,3), $12+.52, 48` writes bit
52; p.48 line 5 declares `LIREF SYN(BU,12), 0.52 -P.P. REFERENCE
NUMBER` at the same width and offset; p.53 line 38's compiled left half
is `000000.64` -- octal 64 = 52 -- with length `014000` = 12. **The
18-bit absolute exit has no located reader** in any transcribed page.

> **SO THE TABLE IS EMPTY BECAUSE MCP-DECODE NEVER RAN.** pp.52-58 are
> the JOB LOADER; they run when a problem program is loaded, and this
> boot has loaded none. An empty request table and an untouched
> `T PREFT` are both exactly what that predicts. **The open question is
> therefore no longer "why is the table empty" but "why is ASSIGN
> being called at all before a job exists", and whether DISK's
> `REQ CNT` of 1 is written by a path that has any business running.**

### A hole worth recording: nothing writes `TLAST`

Every occurrence of `TLAST` in all 72 decks is a **test** --
`BZB, TLAST(LIODX)` (p.57 L13), `BZB, TLAST(LWORKX)` (p.57 L24,
p.58 L20), `BZB, TLAST(TIXA)` (p.65 L49), `BZB, TLAST+1.0(TIXA)`
(p.66 L35), `BZB, TLAST(TIXA)` (p.71 L27), `BZB, TLAST(TIXI)`
(p.74 L25). **No instruction anywhere writes bit 0.18 of an entry**,
and the build path sets `TTYPE`, `TRLSYM`, `TIODSQ` and `TFREEL` but
never the end-of-table marker six branch rows on five pages
interrogate.

Two readings, neither settled: the setter is on an untranscribed page
(pp.1, 5, 7, 9-11 and 81-97 are the gaps; pp.15-80 are complete bar
47, 59 and 60, which compile nothing), **or** a permanently-zero
`TLAST` in a `DRZ` table IS the correct "table exhausted" state and
nothing ever needs to write it. `C22-6728-1`'s `TIOREQ` section is
where to check.

## THE WRITE THAT SETS DISK'S COUNT IS p.66 LINE 3, BY DESIGN -- 2026-10-27

Pairing every watched write with its PC, rather than reading the
sequence in a lump:

| writes | PC | listing | routine |
|---|---|---|---|
| 1-3 | 82 | — | the image zeroed |
| 4-6 | 165 | — | the 494-word TRANSMIT, static table loaded **correctly** |
| 7-14 | 4389 | `004222.40` | p.72's conf-count clear loop, 8 writes |
| 15-22 | 4010 | `003725.00` | p.65's request-count clear loop, 8 writes |
| **23** | **4025** | **`003734.00`** | **p.66 line 3, `T C1 M+1, T RCAD(TX1)`** |

printed p.66's checked rows put `T C1 M+1` at `003733.40`, a full-word
instruction, so PC `003734.00` is inside it. **Zero tail writes**, so
nothing reached the table by another path and these 23 are all of them.

**So DISK's `REQ CNT` of 1 is `-INCREMENT REQUEST COUNT` doing exactly
what it says.** And p.65's loop is visible doing its job correctly in
the same trace: writes 15 and 16 clear flat bytes 2 and 5 -- rows 0 and
1's request counts -- and writes 17-22 leave words 1963 and 1964 alone
because those request bytes were already zero.

> **THE PHANTOM REQUEST IS NOW MEASURED RATHER THAN SUPPOSED.** The
> request table is empty, `T PREFT` is untouched, MCP-DECODE never ran
> -- and p.66 line 3 still counted one request, into row 0, which is
> DISK because a blank entry's TYPE field is zero.

### What is still unexplained, stated exactly

Applying the three correct operations to the assembled table predicts

```
word 1962  0x0100010200000300
word 1963  0x0004000005000006
word 1964  0x0000070000080000
```

and clean runs measure

```
word 1962  0x0000010100002500     <- differs
word 1963  0x0004000005000006     <- matches
word 1964  0x0000000000000000     <- differs
```

Rows 3, 4 and 5 are correct; rows 0, 1, 2, 6 and 7 have wrong TYPE
bytes, **and no loop writes a type byte.** Four decks now say the
loops are right -- clean and with both accumulator halves filled with
ones, which was the one way isolation differed from the boot:

| deck | result |
|---|---|
| `mcp_p72_clear_loop.strap` | pass |
| `mcp_p72_clear_loop_dirty.strap` | pass |
| `mcp_p65_reqcount_clear.strap` | pass |
| `mcp_p65_reqcount_clear_dirty.strap` | pass |

> **SO A LOOP MISBEHAVES ONLY IN THE BOOT, AND THE NEXT DIFFERENCE TO
> TEST IS THE REFILL FIELD.** The decks' pointers are
> `XW, TABLE, 8, 0` -- refill **0**. The live `T TYARA` is
> `0x01ea8000002007a7`, refill **1959**, which is `T TYARA`'s own word:
> self-refilling. p.65 line 47 is `V+CR` where p.72 line 11 is `V+C`,
> and p.66 line 4 is `R, T X1 -REFILL TO BEGINNING OF TABLE`. **None of
> the four decks exercises a refill at all.** That is the remaining
> structural difference between the passing decks and the failing boot,
> and it is one deck away from being settled.
>
> The intermediate VALUES of writes 8 and 12 came from an instrumented
> run and keep the provenance that cost a retraction earlier today; the
> FINAL state above is from clean runs and is the thing to explain.

### Five decks, all green: it is not logic -- 2026-10-27

The refill and the address are both eliminated. `mcp_p72_clear_loop_live.strap`
puts the table at **word 1962** -- MCP's own address -- with a
self-refilling pointer in `LIOTBX`'s shape, assembling to
`0x01ea8000002007a8` against the live `T TYARA`'s
`0x01ea8000002007a7`: same value, same count of 8, refill differing
only because the card sits one word along. **It passes.**

| difference from the boot | deck | result |
|---|---|---|
| none (baseline) | `mcp_p72_clear_loop` | pass |
| fresh accumulator | `mcp_p72_clear_loop_dirty` | pass |
| fresh accumulator | `mcp_p65_reqcount_clear_dirty` | pass |
| table address, refill | `mcp_p72_clear_loop_live` | pass |
| — | `mcp_p65_reqcount_clear` | pass |

> **SO THE FAULT IS NOT IN ANY INSTRUCTION'S LOGIC.** The loop is
> correct with a dirty accumulator, at the boot's own address, with the
> boot's own self-refilling pointer, over a table of distinct bytes,
> eight times, in both offset variants. What is left is what a deck
> cannot reproduce: **the boot's concurrent state** -- look-ahead
> levels loaded, I/O in flight, interruptions armed, the store queue
> carrying other traffic.
>
> That is the same conclusion `6b614b7` reached from the other
> direction and it is now reached by elimination rather than by
> assumption. **It also means the fault belongs to M2.** A VFL
> read-modify-write that is correct in isolation and wrong under
> concurrent memory traffic is a hazard in the store path, and the
> look-ahead is the structure that governs it -- which is the same
> reason `docs/NEXT.md` already gives for M2 preceding M1.

**What NOT to do next:** write a sixth deck. Five have eliminated the
reproducible dimensions. The next measurement has to be taken *in the
boot* -- the instrumented sequence is the only place the wrong value
has ever been seen, and its provenance is exactly what cost a
retraction earlier today, so it needs a probe designed to survive its
own scheduling perturbation: run the SAME instrumented build twice
with the watchpoint reading different address ranges, and check that
the writes to 1962-1964 agree between them.

### The three variant decks were RUN and then REMOVED -- 2026-10-27

`mcp_p72_clear_loop_dirty`, `mcp_p65_reqcount_clear_dirty` and
`mcp_p72_clear_loop_live` are named above and are **not in the
repository.** Each was written, run, given a verified injection, and
deleted, because each pins a NEGATIVE result about a hypothesis that
is now dead and cannot regress independently of the two loops that
remain under test. Eight suite entries went in today for one
investigation; five stay out, and `run_tests.sh` keeps the two decks
that pin the loops against their printed sources plus
`mcp_p72_conf_offset`.

**Each is one edit away from existing again**, which is why deleting
them costs nothing:

| deck | recipe from its surviving sibling |
|---|---|
| `..._dirty` | before `LX, $1, TABPTR`, insert `L(BU,64), DIRTY, 0` and `L(BU,64), DIRTY, 64`; add `DIRTY DD(BU,64,8), -1` |
| `..._live` | `TABPTR XW, TABLE, 8, $` and `SLC, (8)3650.0` before the data, which puts `TABLE` at word 1962 |

All three passed. The findings they establish are in the table above
and in `1e62c3f`; what is NOT kept is the compile time.

## A REAL STORE-TO-LOAD RACE, CLOSED -- AND IT IS NOT THE TABLE'S CAUSE -- 2026-10-27

`bsv/StretchStorage.bsv`'s read-issue gate was

```bluespec
if (!busUsed && !issued && !storeQ.notEmpty && !isValid(storeTail))
```

and the comment above it already states the mechanism: *"`storeQ.notEmpty`
is read BEFORE this clock's enqueue, so without it a read could issue on
the very clock the tail is queued"*. **It then guards only the tail.**

A plain store arriving this clock lands on `storeW` and is enqueued
further up the same rule, so `storeQ.notEmpty` -- read before that
enqueue -- is False for it. With an empty queue a pending read therefore
issued to memory **on the same clock as a store to the same word, and
read the pre-store value.** A one-clock window, open only when the queue
happened to be empty: which is exactly why it presented as
timing-dependent corruption instead of a reproducible wrong answer.

Closed by adding `&& !isValid(storeW.wget) && !isValid(storeTailW.wget)`
-- the second because a crossing field's head and tail are presented in
the same clock, so a read must not slip between them either.

**It is real: behaviour changed.** Word 1964 of the conf table moved from
`0x0000000000000000` to `0x0000060000600000`, and the p.72 clear loop went
from 423 cycles to 421 -- *down*, because holding a read for one clock
lets the store issue a clock earlier. **And nothing derived broke:**
`mcp_indicators_word11` still reads `0x1422`, the value
`tests/gen_mcp_boot_tb.py:952` derives as `AH, OP, RGZ, XE, XVGZ`.

> **BUT IT IS NOT THE TABLE'S CAUSE.** The table is still wrong, and
> still wrong in the type bytes:
>
> | word | expected if correct | measured, race closed |
> |---|---|---|
> | 1962 | `0x0100010200000300` | `0x0000010100002500` |
> | 1963 | `0x0004000005000006` | `0x0004000005000006` |
> | 1964 | `0x0000070000080000` | `0x0000060000600000` |
>
> Row 6's type byte reads `0x06` where the table says `07`, and row 7's
> reads `0x60` where it says `08`. **So there is at least one more
> mechanism**, and the honest position is that closing this one removed a
> real ordering violation and one candidate, not the fault.

**What this changes about the plan.** `850d0d6` made the race a blocker
for M2. That still holds -- results are still timing-dependent -- but the
blocker is now narrower and better evidenced: one hole is closed, the
corruption survived it, and the next step is to find the second writer
path the same way, by gating and measuring rather than by reasoning about
which instruction *ought* to be wrong. Five decks have already shown the
instructions are not.

## >>> THE PC ATTRIBUTION WAS WRONG IN PRINCIPLE, AND THAT IS THE FINDING <<< 2026-10-27

`bd60d0a` paired every watched write with `pcReg` and concluded that
eight writes came from p.72's clear loop at `004222.40` and one from
p.66 line 3. **Under a look-ahead that conclusion does not follow, and
the model's own code says why.**

`StretchCore.bsv:1314-1315` is

```bluespec
la.load(LaLevel{... pc: pc ...});
pcReg <= pc + ((len == Full) ? 2 : 1);
```

**The program counter advances when a level is LOADED. The level
EXECUTES later.** So when an E-box level's store finally lands,
`pcReg` is wherever the I-box has run on to -- by as many instructions
as it managed to load in the meantime. A watchpoint that prints
`pcReg` prints *where the I-box is*, not *which instruction stored*.

> That is the whole point of the structure under investigation, and I
> used an instrument that assumes it away. The right thing to log is
> the **level's own `pc`** -- `h.pc` in `rl_au_remove`, and the
> `storeAddr`-bearing level's `pc` in general -- which is carried in
> `LaLevel` precisely so the instruction can be identified after the
> fact.

**What survives from that trace, and what does not.**

* **Survives:** the final state. The instrumented build's last write to
  each word matches the clean build's probe exactly
  (1962 `0x0000010100002500`, 1963 `0x0004000005000006`, 1964 `0`), so
  the *sequence of values* is describing the same execution. The
  earlier worry that the whole trace was an artifact was too broad:
  only the `LOST` count was.
* **Does not survive:** every attribution of a write to a named
  printed line. Eight writes at one `pcReg` value means eight stores
  landed while the I-box sat at `004222.40`, which is consistent with
  p.72's loop and equally consistent with levels from earlier
  instructions draining behind it.

**And one hypothesis is closed by search rather than by argument.** If
the bad write were a read-modify-write over the wrong BASE WORD, that
base word would be `0x0000060100602540` with byte 4 masked. Assembling
all 72 decks gives 2317 distinct words and **none** matches it -- not
outside byte 4, not on its low 32 bits, not even on the byte pair
`25 40`. So the value is **runtime-derived**, and "the RMW read some
other word of the image" is out.

### The next instrument, specified

1. Log the **level's** `pc` and `kind`, not `pcReg`.
2. Log it at the point the store is *generated* (`rl_au_remove` /
   `execute`'s store sites), not where it is enqueued.
3. Keep the final-state comparison as the provenance check: an
   instrumented run whose final table differs from the clean probe is
   describing a different execution and must be discarded.
4. `tests/gen_tb.py`'s `STEPS=N` gives a **non-perturbing** alternative
   worth using first: run the boot repeatedly with increasing caps and
   probe words 1962-1964, which brackets *when* the table first goes
   wrong without touching `bsv/` at all.

## >>> A NON-PERTURBING BISECTION: THE CORRUPTION IS A 10,000-STEP WINDOW <<< 2026-10-27

Every instrument in this investigation so far has touched `bsv/`, and
one of them manufactured a finding. **This one touches nothing but the
step cap.** `tests/gen_tb.py` already stops a run at `step_cap` and
then runs the checks "against mid-execution state", so setting the cap
and probing words 1962-1964 reads the table *at a chosen moment* with
the model bit-for-bit as committed.

Bisecting the MCP boot:

| steps | word 1962 | word 1964 | PC (half-word) |
|---|---|---|---|
| 2,000,000 | `0` | `0` | — (not yet loaded) |
| 6,000,000 | `0x0101000200000300` | `0x0000070000080000` | correct |
| 6,020,000 | `0x0101000200000300` | `0x0000070000080000` | 2607 |
| 6,030,000 | `0x0101000200000300` | `0x0000070000080000` | 2613 |
| 6,040,000 | `0x0101000200000300` | `0x0000070000080000` | 2617 |
| **6,050,000** | **`0x0101000200000300`** | **`0x0000070000080000`** | **3062** |
| **6,060,000** | **`0x0000060100602500`** | **`0x0000060000600040`** | **4396** |
| 6,200,000 … 18,000,000 | `0x0000060100602500` | `0x0000060000600040` | 4394-4399 |

> **THE WHOLE CORRUPTION HAPPENS IN ONE 10,000-STEP WINDOW**, between
> 6,050,000 and 6,060,000 steps, and nothing touches those words again
> for the next twelve million.

**Three things this settles.**

1. **It is confined to the table.** Words 1959, 1960, 1961, 1965 and
   1966 -- `T TYARA`, `T COMBO`, the `CNOP` filler and the two words
   after -- hold their assembled values at every sample. Whatever
   writes wrongly writes *inside* `003652`-`003654` and nowhere else,
   which rules out a wide or runaway write.
2. **The table is PERFECT until the window.** At 6,050,000 word 1962
   is still `0x0101000200000300`: DISK's conf byte is still **1**, so
   p.72's clear loop has not run. One pass of that routine both clears
   and corrupts.
3. **p.72 is where the machine is.** At 6,050,000 the PC is 3062, well
   away; from 6,060,000 on it sits at 4394-4399, which printed p.72's
   checked rows give as lines 15-19 -- `T A9A`'s per-channel loop.
   **`5279b62` was right to retract attributing individual writes to a
   `pcReg` value; the time bracket reaches the same routine by a method
   that does not depend on that assumption at all.**

### Why this is the method to keep

The bisection costs one boot run per sample and needs no `$display`,
no extra rule and no register, so it cannot change the schedule it is
measuring -- which is exactly what went wrong with the `LOST` messages
(`7738d9d`). **Narrow first, instrument second**: a 10,000-step window
is small enough that a level-pc log inside it will be short enough to
read, and short enough that its provenance can be checked against
these numbers.

## >>> FOUND AND FIXED: A RETIRED LEVEL'S RESPONSE WAS COLLECTED BY THE NEXT ONE <<< 2026-10-27

The 10,000-step window was small enough to instrument. Logging the CM
writeback's own base word at `StretchExecute.bsv`'s `conn_CM` arm --
and checking provenance by confirming the run's final table matched the
bisection exactly -- gave this:

```
word 1962 off  8  base 0x0101000200000300   <- correct, the static table
word 1962 off 32  base 0x0000060101602540   <- ALREADY WRONG
word 1964 off  0  base 0x0000060100602540   <- that is WORD 1962's content
```

`writeFieldWithHi`'s stated precondition is that `hi` is *"the word most
recently read at `ba`'s word address"*. **The fetch for word 1964
returned word 1962's word.**

### The mechanism, in the two files that share it

`StretchLookAhead.bsv`'s `collect()` takes a response whenever
`st.laReady(k)` is true for a valid level with `fetchIssued` set. And
`StretchStorage.bsv`'s read-channel loop, on a NEW request:

```bluespec
if (reqW[c].wget matches tagged Valid .a) begin
  ... pr = tagged Valid a; issued = False;     // new address -- `rs` KEPT
end
```

**Nothing ever discards a channel's held response.** `rs` is cleared
only by `takeW[c]`. So:

1. the level at ring position `k` issues `laReq(k, A)`;
2. it is retired, or **cancelled by `cancelAll()` on a wrong branch
   guess**, before its word is collected -- and neither `retireHead()`
   nor `cancelAll()` tells storage anything;
3. the ring wraps and a new level is loaded at position `k` with
   `da = B`;
4. it issues `laReq(k, B)`, sets `fetchIssued`, and on the next clock
   `collect()` finds `laReady(k)` **already true** from the dead
   level's response -- and takes address A's word as address B's.

**One read outstanding per channel is the protocol** (`StretchStorage`
says so in its own header), so a response not taken by the time a new
address is requested belongs to an address nobody is asking about.
Keeping it is not conservative; it is a wrong answer waiting to be
collected. The fix discards `rs` (and the special-address `ps`) when a
new request arrives.

### What it fixes, measured

Every base word becomes correct, including `word 1964 base
0x0000070000080000` -- its own content. And the table:

| word | before | after |
|---|---|---|
| 1962 | `0x0000060100602500` | **`0x0100000200000300`** |
| 1963 | `0x0004000005000006` | `0x0004000005000006` |
| 1964 | `0x0000060000600040` | **`0x0000070001080000`** |

**All eight TYPE bytes are now intact -- 1, 2, 3, 4, 5, 6, 7, 8 --** the
conf bytes are cleared as p.72 intends, and the MCP boot passes **49 of
49**, `mcp_indicators_word11` included, so the derived `AH` expectation
survives.

### And it separates the model from the fixture

The phantom request did not go away; it **moved**, from row 0 to row 6:

| row | type | conf | req |
|---|---|---|---|
| DISK | 1 | 0 | 0 |
| EXTRA | 7 | 0 | **1** |

So p.66 line 3 still counts one request against an empty request table,
and p.66 line 13 still rejects. **That was never the model's bug.** It
is the fixture's single blank IOD card, and with the corruption gone the
two questions are finally separate: the look-ahead bug is fixed, and
what remains is a deck that declares no I/O.
