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
