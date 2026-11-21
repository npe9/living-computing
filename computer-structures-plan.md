# Computer Structures: Principles and Examples inventory

This is the staged inventory for adding the machines and systems described
substantively in Siewiorek, Bell, and Newell, *Computer Structures: Principles
and Examples* (McGraw-Hill, 1982, ISBN 0-07-057302-6). The book is the primary
source for this work. Printed page numbers below are the chapter opening pages
from the book's contents; later implementation work must cite the exact
printed pages for each architectural claim.

The existing repository already has stubs for Atlas, B5000, Manchester Mark 1,
CDC 6600, CRAY-1, PDP-8, PDP-11, System/360, and VAX-11/780. Those entries are
not duplicated here. This change only creates missing, unimplemented-design
skeletons (`README.md`, `plan.md`, `docs/README.md`, and empty `bsv/`).

## Inventory and status

| directory | book system or family | book location | repository status |
|---|---|---:|---|
| `pdp1/` | DEC PDP-1 | Part 1, Sec. 3 | existing |
| `b6500/` | Burroughs B6500 | Ch. 16, p. 244 | new stub |
| `b7500/` | Burroughs B7500 | Ch. 16, p. 244 | new stub |
| `icl2900/` | ICL 2900 series | Ch. 17, p. 251 | new stub |
| `ibm360m91/` | IBM System/360 Model 91 | Ch. 18, p. 300 | new stub |
| `illiac4/` | ILLIAC IV | Ch. 20, p. 306 | new stub |
| `staran/` | STARAN associative array processor | Ch. 21 | new stub |
| `cmmp/` | C.mmp/Hydra | Ch. 22 | new stub |
| `pluribus/` | Pluribus fault-tolerant multiprocessor | Ch. 23 | new stub |
| `imp/` | ARPA Interface Message Processor | Ch. 24, p. 403 | new stub |
| `aloha/` | ALOHA packet-broadcast system | Ch. 25, p. 426 | new stub |
| `ethernet/` | experimental Ethernet | Ch. 26, p. 429 | new stub |
| `star-fault/` | STAR fault-tolerant computer | Ch. 27 | new stub |
| `localess/` | Bell System local ESS processors | Ch. 28, p. 459 | new stub |
| `tandem16/` | Tandem 16 NonStop | Ch. 29, p. 470 | new stub |
| `symbol/` | SYMBOL experimental computer | Ch. 30, p. 489 | new stub |
| `hp9845a/` | Hewlett-Packard 9845A | Ch. 31, p. 508 | new stub |
| `system38/` | IBM System/38 | Ch. 32, p. 533 | new stub |
| `alto/` | Xerox Alto | Ch. 33, p. 549 | new stub |
| `tms1000/` | Texas Instruments TMS 1000 | Ch. 34, p. 587 | new stub |
| `tms1200/` | Texas Instruments TMS 1200 | Ch. 34, p. 587 | new stub |
| `pic1650/` | General Instrument PIC1650 | Ch. 35, p. 602 | new stub |
| `intel8008/` | Intel 8008 | Ch. 37, p. 615 | new stub |
| `intel8080/` | Intel 8080 | Ch. 37, p. 615 | new stub |
| `intel8086/` | Intel 8086 | Ch. 37, p. 615 | new stub |
| `am2900/` | AMD Am2900 bit-sliced family | Chs. 13–15 | new stub |
| `ibm360m30/` | IBM System/360 Model 30 | Ch. 12 | new stub |
| `hp9100a/` | Hewlett-Packard 9100A | Ch. 48, p. 787 | new stub |
| `hp9810/` | Hewlett-Packard 9810 | Ch. 49, p. 801 | new stub |
| `hp9820/` | Hewlett-Packard 9820 | Ch. 49, p. 801 | new stub |
| `hp9830/` | Hewlett-Packard 9830 | Ch. 49, p. 801 | new stub |
| `s370/` | IBM System/370 | Ch. 51, p. 815 | new stub |
| `ibm3030/` | IBM 3030 series | Ch. 52 | new stub |
| `ibm4300/` | IBM 4300 series | Ch. 52 | new stub |

The book also discusses the existing Atlas, B5000, Manchester Mark 1, PDP-8,
PDP-11, CDC 6600, CRAY-1, and System/360 family, plus the existing VAX-11/780.
Those are enrichment and relationship tasks, not new directories.

## Scope of each stub

Each directory deliberately has no simulator yet. Its `README.md` will state
the historical scope, `plan.md` will require a source-backed ISP/PMS and
feature matrix before implementation, `docs/README.md` will identify the book
chapter as the initial source, and `bsv/` will remain empty except for
`.gitkeep`. Unsupported behavior must fail loudly when implementation begins;
no instruction encodings or simulation behavior are inferred from this
inventory.

## Proposed implementation order

1. **Historical and structural systems:** PDP-1, B6500/B7500, ICL 2900,
   System/38, Alto, and the HP calculator family.
2. **Concurrency and fault tolerance:** System/360 Model 30/91, ILLIAC IV,
   STARAN, C.mmp, Pluribus, STAR, ESS, and Tandem 16.
3. **Networks:** IMP, ALOHA, and Ethernet.
4. **Language and microcomputer architectures:** SYMBOL, HP 9845A, TMS
   1000/1200, PIC1650, Intel 8008/8080/8086, and Am2900.
5. **Family extensions:** System/370, IBM 3030/4300, followed by relationship
   and comparison updates to the existing family stubs.

Every batch must add exact printed-page citations, update the relevant
relationship notes, and keep simulation marked unavailable until a
source-backed model and tests exist.

## Completion gates

- Every row above has a repository directory and a source inventory.
- Existing machines remain single entries; family membership is not treated as
  binary compatibility.
- ISP/ISPS, PMS, Kiviat comparisons, and architectural interpretations are
  recorded separately from historical facts.
- Each implemented behavior has a primary-source page and focused tests.
- The repository's existing regression suite remains green.
