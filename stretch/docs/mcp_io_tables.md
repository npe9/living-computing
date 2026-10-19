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
