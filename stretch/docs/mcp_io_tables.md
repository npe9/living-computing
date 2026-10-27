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
(`C22-6728-1`, sampled but not read for this question), its §215
UPDATE 30 writeup, and the bulletin `C22-6718` which p.40 cites and
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
