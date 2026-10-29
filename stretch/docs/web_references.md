# Web references — SECONDARY sources, and what each is good for

> **>>> NONE OF THESE MAY BE CITED FOR AN ENCODING OR A SEMANTIC. <<<**
> `AGENTS.md` rule 4 says those come from the primary sources in
> `docs/`, cited by printed page. A web page is for ORIENTATION, for
> CROSS-CHECKING a reading, and above all for FINDING primary sources —
> several of these link to scans this project does not yet hold. Where
> a page makes a claim that bears on the model, it is recorded below
> with its status, not folded into the design.

Each entry says whether it has been **read** first-hand or merely
**listed**, the same distinction `docs/source_audit.md` keeps for the
paper corpus.

---

## Mark Smotherman (Clemson) — the most useful secondary set

Smotherman's pages are unusual among web sources in that they quote and
cite IBM primary documents directly, including ones in this corpus.

### `https://mark.people.clemson.edu/stretch_superscalar.html` — "Was Stretch Superscalar?" — **READ 2026-10-29**

Argues Stretch does **not** meet the strict definition of superscalar
(sustained throughput above one instruction per cycle), and the
reasoning is directly relevant to M2:

* **Two serialisation points** are named as what prevents it —
  instructions pass one at a time through the I-unit's execution
  register, and the E-unit processes the oldest look-ahead levels
  sequentially.
* Quotes a primary source: *"All instructions eventually are loaded
  into lookahead"*, and *"Each I-box instruction results in one
  (sometimes more) level of LA being loaded."*
* Cites the 1961 Performance Characteristics manual for *"one
  instruction per 1.2 µs"* on floating-point sequences.
* Performance estimates of 500 KIPS to 1.2 MIPS, i.e. CPI of 3.3 to
  1.4 against a 600 ns control cycle.

> **WHY THIS MATTERS HERE: the second quotation independently
> corroborates something this project already derived.**
> `docs/NEXT.md` records "**and every I-box instruction loads a level
> too** — that is what actually throttles the I-box", taken from Table
> A-2. An outside reading of the same machine reaches the same
> sentence. That is a cross-check, not a new fact.
>
> **AND THE 600 ns CONTROL CYCLE IS A DISCREPANCY TO RESOLVE, NOT TO
> ADOPT.** This project works in 0.3 µs machine cycles, and
> `docs/microarchitecture_roadmap.md` G1.0 already carries an open item
> about the clock unit (Bloch denies a machine cycle; the 7101 has two
> phases A/B). A secondary source using 600 ns is a data point for that
> item and nothing more.

### `https://mark.people.clemson.edu/stretch.html` — "Organization Sketch of IBM Stretch" — **READ 2026-10-29**

The orientation page: organisation, the look-ahead's origin (Amdahl and
Backus's "asynchronous non-sequential control", refined by Cocke and
Kolsky through timing simulation into **four levels**), and the
instruction unit described as "a pipelined computer on its own". Gives
169,100 transistors and a **2.1 µs** memory cycle.

**Its bibliography is the real value**: links to Backus, Amdahl and
Kolsky papers, patents, technical reports, CHM-digitised documents, and
oral histories — i.e. a route to primary material.

> Note the memory-cycle number. `docs/microarchitecture_roadmap.md` M3
> records an unresolved disagreement — 2.2 µs in Perf. Char., 2.1 in
> plan §A.7, 2.0 in Buchholz — and the model runs 2.1. **This page
> saying 2.1 settles nothing**; it is a fourth voice in a dispute whose
> resolution has to come from a printed page.

### Also by Smotherman, **LISTED, not yet read**

* `https://mark.people.clemson.edu/kolsky_cocke.html` — Kolsky and
  Cocke, i.e. the people who sized the look-ahead by simulation.
  Likely the most relevant unread page for M2.
* `https://people.computing.clemson.edu/~mark/eager.html` — eager
  execution, which is what Stretch's guessed branch plus recovery
  actually is.
* `https://people.computing.clemson.edu/~mark/acs_organization.html` —
  IBM ACS, Stretch's successor project.

*(The `people.computing.clemson.edu/~mark/…` form 301-redirects to
`mark.people.clemson.edu/…`; use the latter.)*

---

## Machine and artefact references — **all LISTED, not yet read**

* `https://www.computerhistory.org/collections/catalog/102716145` —
  CHM catalogue entry for a 7030 **engineering console**. Catalogue
  records are useful for the physical machine and for locating scans.
* `https://ed-thelen.org/comp-hist/vs-ibm-stretch.html` — Ed Thelen's
  Stretch page, part of a long-running computer-history archive.
* `https://computer-history.info/Page4.dir/pages/IBM.7030.Stretch.dir/`
  — another archive collection of 7030 material.

## Treat with caution

* `https://grokipedia.com/page/IBM_7030_Stretch` — an AI-generated
  encyclopedia page. **Not a source.** Recorded only so that a future
  reader who finds it knows it has been seen and deliberately not
  used; anything it says needs checking against a document before it
  is repeated.

---

## The rule for adding to this file

State whether the page was READ or merely LISTED, and when a page makes
a claim that touches the model, say what the project already holds and
whether this agrees, disagrees or is silent. **A secondary source that
agrees is a cross-check; one that disagrees is an open item, not a
correction.** Two are already open above: the 600 ns control cycle and
the 2.1 µs memory cycle.
