# STRAP II: the specification and the host-side reconstruction

IBM's STRAP II is lost. These three files specify it from C22-6729, its
internals guide. `strap/strap2/` implements them host-side and is
RECONSTRUCTION, in the order `../reconstruction_plan.md` gives. A 7030 program
that assembles its own source to the same bits comes after it.

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

## How far the code reaches

`strap/strap2/` follows the guide's phases: Pass 1 writes expanded units in
Fig. 20's bits, with GETFLD's coded expressions (App. C) inside them; UITER and
Pass 2a keep the two location counters and resolve the cascade of special
symbols; Pass 2b decodes each unit and fills in the word. It is not `strap_asm`
restructured, but it borrows `opcodes.py`, `strap_asm`'s `enc_*` encoders and its
numeric DD literal parser as leaf facts. Measured 2026-11-09:

| check | result |
|---|---|
| `tests/check_strap2_coded.py` | Figs. 28 and 29 pp.200-201, bit for bit (208, 447 and 196 bits) |
| `tests/check_strap2.py` | what the guide says and `strap_asm` does not do, by hand |
| listing oracles run on strap2 (`check_strap2_oracles.py`) | 273 of 273 `verify_*.py`; 351 of 351 MCP pages |
| image of every deck against `strap_asm`'s | 719 the same; 7 with the known difference below; 1 both refuse |

The known difference: `strap_asm` puts a NOP in a half word rounded over before
a DR(N) or DRZ(N), and p.33 makes only a CNOP a NOP. strap2 follows the guide. No
listing prints those halves, so no oracle can decide.

**Not yet written:** Fig. 26's numeric DD (MQDD, MQDNUM, DNUM); a DD length
resting on a later symbol; DDI; IOD and REEL (MIOD, NMCP); the MIBA and MBSPEC
corrections; the coprocessor; DUPLI; relocation; subscripts with dimensions; the
system symbols' register-length dds; MULTI's equal-value test; and OUTPUT's
listing, to be compared with C22-6678-1 p.48 and CHM 102633945. An unwritten path
refuses loudly.

**What building it found:**

- **A8 is the Reference Manual p.166 48-character set.** All nine values the
  guide prints match it. This is DERIVED, not stated. `;` is given 0o035, CHOSEN.
- **Radix is per field, not per instruction.** The listing has
  `LFI(BU,8),(8)..,8`, contrary to the reading of p.70.
- **`$` before an operation suppresses the end mark** (p.25, Fig. 20's bit p).
  This explains the listing's `$B,Q GO$A`, previously unexplained.
- **The value model subsumes `strap_asm`'s text hacks.** VALUE keeps the bit-style
  and integer parts apart, and INSERT adds them by the address function: 18-bit
  (B>>6)+I, 19-bit (B>>5)+I, 24-bit B+I, LX and SX (B>>5)+(I<<1).
- **Page decks' stand-in SYNs must sit under the page's TAIL.** Real tails
  require it, so `decks/mcp_bootstrap_p43.strap` and `p261` moved theirs.
- **The two sources disagree on UNTAIL:** C28-6129 p.38 says "all levels up to and
  including", guide p.125 says otherwise. Unresolved.

**CHOSEN in the code:** the function layout (`symtab.FUNCTION`, 324 bits; Zst<n>
is bit n of it); the op-table index and entries, built lazily (`optable.py`); the
A8 value of `;`; the extra-unit code ZIEXT2; a lone `$` coded as symbolic `$`
plus absolute 0 with `.L` and `+`; and a card scaffold, `cards.deck_cards`,
turning free-form decks into 80 columns.

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
