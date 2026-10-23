# living-computing

Recreations of historical computers, one directory per machine, built
from the scanned primary documents for each: the vendor reference
manuals, the pocket cards, and the diagnostic and operating-system
listings that printed IBM's own assembler output alongside the source.
The aim is not a collection of emulators that run plausible programs,
but models in which every encoding and every behaviour can be traced to
a printed page, and in which the programs that run are the real
historical ones, transcribed row by row and checked against the machine
code the listing prints next to them.

**One machine has substance.** `stretch/` (the IBM 7030) is 697 tracked
files: a STRAP-1 assembler in Python, a Bluespec model of the machine,
303 card decks, 226 verify scripts, and 55 scanned PDFs of primary
sources. The other 23 directories are stubs — a sourced README and an
empty `bsv/`. 496 commits since 2026-08-24, almost all of them in
`stretch/`.

## Method

The working rules live in [`AGENTS.md`](AGENTS.md); this is what they
amount to.

**Encodings come from primary sources, cited by page.** AGENTS.md rule 4:
encodings and semantics come from the manuals and listings in
`stretch/docs/`, cited by page. Several of those PDFs have no text
layer, so the page image is read. An instruction's meaning is never
inferred from how a listing happens to use it.

**Transcribed machine code is the oracle.** AGENTS.md rule 3: anything
taken from a historical listing is transcribed *with* the printed
machine-code column, and the assembler's output is checked against that
column by `stretch/strap/listing_oracle.py` before the program is run on
the model. IBM's own assembler output is the strongest oracle in the
project — it is a bit-exact statement of what the machine was supposed
to encode, printed in 1963, with no opportunity for this project to have
influenced it.

**Two declared standards, and every test says which it meets.** From
`stretch/docs/NEXT.md` ("The bar"):

* *Transcription* — a listing row checked bit-exactly by a verify
  script.
* *Manual-derived* — hand-written from a primary source, stated as the
  weaker standard in the program's own header.

The distinction is kept in the open rather than averaged away. The
interruption mechanism, for instance, is still manual-derived only, and
storage protection's *rule* has a deck behind it while its *behaviour*
test is still hand-written.

**A green test is only evidence about faults its inputs could have made
visible.** This rule outranks both standards. A new test is proven
discriminating by injecting the specific bug it is meant to catch,
watching the predicted checks fail and nothing else, and reverting; the
*observed* failure set is written into the test's header, not the
predicted one. Claims about timing need a documented number behind them,
and claims about coverage are measured, not asserted.

**Unimplemented means loud.** The model's scope is "decode completely,
execute partially, document the rest": an instruction the model does not
implement fails visibly instead of quietly doing something close. This is
what turns a gap into a finding. On 2026-10-23, MCP's printed p.40 was
found to contain a `SWAP` — an instruction four separate files in this
repo asserted that nothing in the corpus executed, three words from the
UNCODE subroutine's exit, with a documented caller. All four were
corrected rather than quietly edited, and the refusal still stands,
recorded as a survival with an expiry date.

## Status

| directory | machine | state |
|---|---|---|
| `stretch/` | IBM 7030 "Stretch" (1961) | **the live project** — assembler, Bluespec model, boots MCP from tape |
| `atlas/` | Ferranti / Manchester Atlas (1962) | stub |
| `b5000/` | Burroughs B5000 (1961) | stub |
| `baby/` | Manchester Baby / SSEM (1948) | stub |
| `cdc6600/` | CDC 6600 (1964) | stub |
| `colossus/` | Colossus (1944) | stub |
| `cray1/` | Cray-1 (1976) | stub |
| `edsac/` | EDSAC (1949) | stub |
| `eniac/` | ENIAC (1945) | stub |
| `ias/` | IAS Machine (1952) | stub |
| `ibm1401/` | IBM 1401 (1959) | stub |
| `ibm701/` | IBM 701 (1952) | stub |
| `ibm704/` | IBM 704 (1954) | stub |
| `ibm7090/` | IBM 7090 (1959) | stub |
| `mark1/` | Manchester Mark 1 / Ferranti Mark 1 (1949–51) | stub |
| `pdp1/` | DEC PDP-1 (1959) | stub |
| `pdp11/` | DEC PDP-11 (1970) | stub |
| `pdp8/` | DEC PDP-8 (1965) | stub |
| `risc1/` | Berkeley RISC I (1981) | stub |
| `s360/` | IBM System/360 (1964) | stub |
| `univac1/` | UNIVAC I (1951) | stub |
| `vax/` | DEC VAX-11/780 (1977) | stub |
| `whirlwind/` | Whirlwind I (1951) | stub |
| `z3/` | Zuse Z3 (1941) | stub |

A stub is a `README.md` on a fixed template — machine, year, the people
and the place, what the machine introduced with concrete figures, the
line `Bluespec implementation: bsv/ (not started)`, and the sources that
would be used — plus a `bsv/` directory holding only `.gitkeep`. They
are sourced notes on what each machine was, not scaffolding for code
that exists.

## `stretch/`

See [`stretch/README.md`](stretch/README.md) for the machine's own
summary and the directory layout. In brief:

* `stretch/strap/` — a STRAP-1 assembler in Python (`strap_asm.py`),
  plus the host-side tooling the machine needs: the 7030 character sets,
  card and tape image builders, the MCP tape image, and
  `listing_oracle.py`, which checks assembled output against a listing's
  printed machine-code column. STRAP-II postdates STRAP-1 and the
  assembler has not been checked against it.
* `stretch/bsv/` — a Bluespec model of the 7030, roughly 13,900 lines of
  hand-written Bluespec across the decoder, the execute unit, storage,
  the look-ahead, the variable-field-length unit, and the exchange and
  I/O. The testbenches are generated and gitignored.
* `stretch/decks/` — 303 STRAP decks: transcriptions of the scanned
  diagnostic and MCP listings, and test programs written to pin model
  behaviour.
* `stretch/tests/` — 226 `verify_*.py` scripts, the testbench
  generators, and `run_tests.sh`.
* `stretch/docs/` — 55 scanned primary PDFs plus this project's
  structured notes on them, including `boot_plan.md` (the plan for
  booting the extant 7030 software) and `NEXT.md` (the standing work
  queue).

### Where the MCP boot stands

The current work is booting IBM's real Master Control Program — the
7030's operating system — from a tape image manufactured by this repo's
own assembler out of the March 1963 source listing. There is no extant
machine-readable artifact of MCP; every tape has to be built from the
scan.

What runs, as of 2026-10-23 (`stretch/docs/boot_plan.md` §A5, §A8, §A10):

* MCP's IPL bootstrap and initialization execute, covering printed
  pp.15–36 of the listing.
* It configures itself from an IOCD card — the card's column format is
  printed, and the fixture punches a real one through the 7030's own
  card code. Getting those cards onto the system tape the way the real
  system did, rather than fed by the testbench, is still open
  (`boot_plan.md` A3's remaining piece).
* It types `DATE OF IPL TAPE` on the operator's console, and reads the
  three words the console scans from its switches.
* It hands off to the prime routine at half-word 2284 = `002166.00`,
  which printed p.37 line 45 names `S PRIME`. Printed p.38 line 4 is the
  same address under the name `Y UNCOD`: the prime routine and the
  UNCODE subroutine are the same entry, which neither page says on its
  own. The program counter then reaches `002422.00`, `S CA6`, the
  convert-to-six-bit-BCD routine, runs it against the character tables
  on printed p.44, and calls `S BRK8` at `002502.00` — "break card into
  fields", which printed p.38 had predicted at that address five pages
  before the page holding it was opened.
* With `S BRK8` transcribed (printed p.45) the run goes more than twice
  as far and **ends where MCP means to end**: it runs the whole UNCODE
  path, decides the card is "NOT IOD OR REEL CARD", and takes its own
  error exit, which displays the error address in the CE console and
  loops. Why the card is rejected is the current question — the first
  time in this project that MCP has made a decision about its input and
  said so. Transcribing the routine's tables (printed p.46) halved the
  run, from 12.8 to 6.0 million steps, and did **not** change the
  answer: the missing tables were the plausible cause and are not the
  cause.

As of 2026-10-23, printed pages **2 through 46** of the MCP listing
are transcribed bit-exactly. Transcription runs ahead of execution,
and pages transcribed before the pages that define their symbols have
repeatedly served as predictions — printed p.39 confirmed three
symbols at exactly the addresses p.38's binary output had implied,
including one whose half-word selector bit would have put it half a
word wrong, and printed p.44 confirmed all four of p.43's.

## Running the tests

```
cd stretch/tests && ./run_tests.sh
```

This is the whole regression suite: the pure-Python assembler tests
first, then the Bluesim smoke test, then every STRAP program with a
verified expected result. It must be green before a commit. A full run
takes roughly thirteen minutes, by `run_tests.sh`'s own note, so run it
in the background.

The verifiers are written to be run *from* `stretch/tests/` — they open
their decks as `../decks/NAME.strap`, and `run_tests.sh` sets
`PYTHONPATH` but does not `cd` for you. The Python tests need only
Python 3; the model tests need Bluespec's `bsc` and Bluesim.

## Contributing

Read [`AGENTS.md`](AGENTS.md) first. It is the authority on how work is
verified here, what the current direction is, and what an agent working
in this repository may do without asking.
