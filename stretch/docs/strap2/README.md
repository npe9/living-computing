# STRAP II: the specification

IBM's STRAP II is lost. These three files specify it from C22-6729, its
internals guide. The code that will implement them is reconstruction, in the
order `../reconstruction_plan.md` gives: host-side first, then a 7030 program
that assembles its own source to the same bits.

| file | covers |
|---|---|
| `formats.md` | COMREC, disk output, the unit, tables, coded expressions, errors 1-148, relocation, the deck, the memory map |
| `pass1.md` | the order of a card block, GETFLD, GETCHA, MQDD and the other Pass 1 routines, what fills each unit field |
| `pass2.md` | UITER, the two location counters, DECODE, INSERT, NEXT, TABMAN, VALUE, OUTPUT, the listing |

## How far to trust them

Three agents read the guide separately, each in the ink for its own scope, on
2026-11-08. Each file states the pages it did not read and lists the
contradictions it found. In `formats.md`, UNSPECIFIED is weaker for pp.15-172,
which it swept by OCR only; `pass1.md` and `pass2.md` read most of those pages.

Checked by a second reader against the ink: **Fig. 20 p.189 only**, every field
of the control word and fixed portion, which `formats.md` and `pass1.md` agree
with. The rest is one reader's work and should be reread before it is relied on.
A disagreement between these files is a reason to go back to the page.

## What the guide does not give

The implementation has to choose these, and label each choice CHOSEN:

1. **The symbol function's layout.** 231 bits, named by scattered ZST symbols,
   and tabulated on no page found. The names and meanings survive.
2. **The operation tables.** No contents, no op-index bits and no pseudo-op
   select numbers. The operations themselves are known from C28-6129, the
   Reference Manual and `strap/opcodes.py`.
3. **GETFLD's syntax-matrix cells.** pp.83-84 give only the legends; Appendix F
   constrains the cells.
4. **The A8, A6 and CC code tables**, of which nine A8 values are seen.
5. **Card details:** the check sum, the sequence scheme and the row order.
   Absolute formats are in C28-6129 pp.22-23, and the listing's loader
   (`../bss_loader_spec.md`) shows a check sum being read.
6. **Which error flag is which**, and most errors' exact detection points.

Items 1-4 are internal: they cannot change the object code. So the oracles still
apply to what comes out: the code columns of the MCP listing and of C22-6678-1
p.48, all STRAP II's own output, and CHM 102633945, a page of STRAP's own code.
