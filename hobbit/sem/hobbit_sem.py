#!/usr/bin/env python3
"""hobbit_sem.py -- an independent one-instruction model of the ATT92010.

The model is the specification side of the repository's HRI (Hobbit
Retirement Interface) check: one call to ``step()`` retires (or refuses)
exactly one parcel-encoded instruction, starting from an architectural
pre-state and with no pipeline, prefetch buffer, decoded-instruction-cache
or branch-folding hardware.  It does carry the Chapter 4 cycle account
that the record's trailing ``cyc`` field reports.  HRI is the Hobbit
analogue of riscv-formal's RISC-V Formal Interface (RVFI); the check is a
per-instruction trace comparison against the Bluespec core, not a formal
proof.  The returned record is the HRI line the core is expected to
reproduce field by field; see ``hobbit/sem/README.md`` for the exact
field definitions and the manual page behind every field.

Cycle account
-------------

``cyc`` is the instruction's occupancy in core clock cycles, measured
between HRI retirements (for the first record, from the core's start to
its retirement).  The base values are the printed Chapter 4 tables
(pp. 4-3..4-5, Tables 4-32..4-36), transcribed in ``CHAPTER4`` below with
a printed page and table caption on every row.  They are used under the
four assumptions printed on p. 4-1: the instruction fetches in the
instruction cache (the prefetch buffer assumption), only stack-offset,
immediate, register, absolute-for-jumps/calls and PC-relative modes are
used, stack offsets are captured in the stack cache, and no data hazards
occur.  Consistently with those assumptions no Table 4-37..4-40 delay is
added: this model has no instruction fetch, operand access or data type
delay, and the two delay families the manual duplicates (Tables 4-38 and
4-40, p. 4-6/p. 4-7) are not applied at all.

The manual defines the memory symbols A (single word), D (double word)
and Q (quad word) on p. 4-2 but prints no cycle values for them.  The
model chooses one cycle per 32-bit word, because its backing memory is a
single-cycle 32-bit word store: ``A_CYC = 1``, ``D_CYC = 2``,
``Q_CYC = 4``.  These are model choices, not manual facts.  Table 4-36's
ENTER row is ``1 + (Q.E)``; the model reads E as the number of 16-byte
blocks the pp. 3-19/3-20 flush loop actually moves, rounded up for a
partial block.  Table 4-36 prices CATCH at a flat 1 even though CATCH
refills the cache (p. 3-10); no refill term is invented.  The
unimplemented-opcode row is ``7 + A`` (p. 4-5, Table 4-36), the sequence
FLUSHD/FLUSHDCE take (pp. 3-22, 3-23).

Branch timing uses the printed p. 4-7 folding rule and Table 4-35
(p. 4-5).  A folded one-parcel unconditional JMP takes 0 (p. 4-3 note)
and an unfolded one takes 1.  For a conditional jump the model compares
the branch's Y/N prediction bit with the direction it actually took and
uses Table 4-35's rows; the distance to the compare that last wrote
PSW.F selects the incorrect-prediction row.  Where the printed table has
no row at all -- an incorrectly predicted conditional jump whose
PSW.F was not set by a compare (TESTC/TESTV and the reset value are the
other flag sources) -- the model raises ``Refusal`` instead of inventing
a cycle count.

The modelled subset includes the multi-cycle arithmetic
(MUL/MUL3, DIV/DIV3, REM/REM3, UDIV, UREM), the interlocked
ADDI/ANDI/ORI, tagged TADD/TSUB, DQM, MOVA, LDRAA, CLRE, TESTC/TESTV,
the kernel transfers KCALL/KRET/CRET, and the three- and five-parcel
forms of the dyadic instructions.  Arithmetic flags follow the printed
operation lines; the two places the PRM does not pin down -- a MUL
cycle count inside its printed Min 3/Max 20 range and the rounding
direction of "two's complement division" -- are named model choices in
``hobbit/sem/README.md``.  The fixed HRI line has one write slot, so an
instruction with several architectural stores (the interlocked forms'
accumulator save, a DQM block, KCALL's frame) reports its primary
destination and applies the rest to ``state.memory``; that record
limitation is also stated in the README.

Everything here is written from the printed ATT92010 Programmer's
Reference Manual (January 1993) and deliberately does not import or read
``hobbit/bsv`` or ``hobbit/asm``.  That independence is the point: the
model and the core must agree without sharing an implementation.

Only the standard library is used.

CLI (fixed contract)::

    python3 hobbit/sem/hobbit_sem.py --image IMAGE --sp HEX --msp HEX \
        [--max-steps N] [--part 92010|92020S [--borrow-92010-timing]]

``--part`` selects the part (``PARTS``; default 92010, unchanged).  The
92020S differs only where a source says so (docs/att92020.md): its ID
register, and refusals (``Unsourced92020``) where no source says what it
does -- the encodings its Wait For Interrupt may occupy, a FLUSHPBE
whose address and target differ in bit 10 (Be's two 1994 kernels
disagree there), and its timing unless --borrow-92010-timing.

IMAGE is text, one 32-bit word per line, eight hex digits, ascending
addresses from 0.  The parcel at an even address is in bits 31:16 and the
parcel at the following odd address in bits 15:0.  Entry is at 0.
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Tuple

MASK32 = 0xFFFFFFFF

# --- PSW bits used by this model (Table 1-8, printed pp. 1-14..1-16) -----
# The PSW is kept in the state as a 32-bit word; only these bits matter.
PSW_F = 1 << 4          # flag (compare / tagged arithmetic / jump condition)
PSW_C = 1 << 5          # carry
PSW_V = 1 << 6          # overflow
PSW_SP = 1 << 9         # 1 = SP is the current stack pointer (CSP)
PSW_USER = 1 << 10      # 0 = kernel, 1 = user (not used, recorded for clarity)
PSW_E = 1 << 11         # enter guard
PSW_USER_LE = 1 << 15   # user little-endian data (p. 1-3; _little_endian)
PSW_VIRTUAL = 1 << 16   # virtual addressing (not modelled)

SCSIZE = 256            # 64 words, p. 1-5


# --- Part selection: ATT92010 (default) or ATT92020S ---------------------
# docs/att92020.md is the evidence for every value here.  No AT&T 92020
# data sheet, programmer's reference or errata has been found, so the
# 92020S column rests on contemporaneous trade press (Microprocessor
# Report 7:14, 25 Oct 1993; AT&T's press release of 18 Oct 1993; CBR,
# 17 Oct 1993) and on Be's 1994 kernels (the ID compare in _main1, the
# FLUSHPBE workaround in _flushpbe_020).  What none of them gives is
# refused, not guessed: see ``Unsourced92020``.
@dataclass(frozen=True)
class Part:
    name: str
    # JTAG ID register (Table 1-4, p. 1-11 field layout).
    ident: int
    # Prefetch buffer bytes (92010: p. 1-1 "3 Kbyte"; 92020S: MPR 7:14
    # p. 1, CBR).  Recorded only: this model has no prefetch buffer and
    # prices every fetch as a hit (the p. 4-1 assumption).
    pfb_bytes: int
    # Stack cache bytes (92010: p. 1-5; 92020S: CBR "256-byte stack
    # cache").  Equal for both parts; SCSIZE is used.
    stack_cache_bytes: int
    # True when the printed Chapter 4 tables are this part's own.  The
    # 92020S has no published timing; its runs must opt in explicitly to
    # borrowing the 92010 tables (State.borrow_92010_timing).
    own_timing: bool


PARTS: Dict[str, Part] = {
    # Mask two (version 1, part code 0, manufacturer 0x3B), the model's
    # historical choice (System.ident).
    "92010": Part("92010", 0x1000003B, 3072, 256, True),
    # 0x0E33D03B: the constant Be's March and November 1994 kernels
    # compare the ID register with before printing "Running on Hobbit 020
    # processor" (_main1, CMPEQ $0x0e33d03b,R4 after CALL _get_id).
    # Version 0, part code 0xE33D, manufacturer 0x03B by p. 1-11's
    # layout.  Which 92020 part or mask answers with it is not stated.
    "92020S": Part("92020S", 0x0E33D03B, 6144, 256, False),
}

# Parts named in the sources but refused: their multiplexed bus changes
# every memory access's cost and no figure for it exists (MPR 7:14 p. 1:
# "each transaction requires an extra cycle").
REFUSED_PARTS = {
    "92020M": "multiplexed 32-bit address/data bus; no bus timing sourced",
    "92020MX": "multiplexed bus and a 3 Kbyte prefetch buffer; no bus "
               "timing sourced",
}


def part_info(name: str) -> Part:
    """The ``Part`` called ``name``; a ValueError for anything else."""
    if name in PARTS:
        return PARTS[name]
    if name in REFUSED_PARTS:
        raise ValueError("part %s is refused: %s (docs/att92020.md)"
                         % (name, REFUSED_PARTS[name]))
    raise ValueError("unknown part %r; known: %s" % (name, ", ".join(PARTS)))

# --- Chapter 4 memory parameters (printed p. 4-2, no values printed) -----
# The manual defines A, D and Q (p. 4-2) as the memory access times for a
# single, double and quad word, but prints no cycle values for them.  These
# are model choices, not manual facts: one core cycle per 32-bit word of the
# model's single-cycle word memory, so a double word costs two word cycles
# and a quad word four.  Every table cell that contains A, D or Q is
# resolved with these names, never with an inline constant.
A_CYC = 1               # memory access, single word
D_CYC = 2               # memory access, double word (two words)
Q_CYC = 4               # memory access, quad word (four words)
# Table 4-34's last cell, "M quad-word to M quad-word", is printed 8.S
# (p. 4-4; read from the page image, not only the text layer), and S is
# not among p. 4-2's symbols.  The cell was refused until 1st Edition
# Plan 9's compiler executed the instruction (a structure copy); a
# program cannot be run with a refusal in the middle of it.  S is read
# here as a single-word access, i.e. A: the row above it prices two
# double-word accesses as 2.D, and a quad word moved memory to memory is
# eight word accesses, four read and four written.  A choice, like A, D
# and Q themselves; `Presumably 8.Q` (docs/timing.csv) would give 32.
S_CYC = A_CYC

# Table 4-33 (printed p. 4-4) prints MUL and MUL3 only as a range,
# "Min 3 / Max 20", and calls them data dependent; no page prints the
# dependence.  The one-instruction model must report one number, so it
# takes the printed maximum and names the choice here.  This is a model
# decision, not a manual fact (README, choice 24).
MUL_CYC = 20


@dataclass(frozen=True)
class CycleRow:
    """One printed Chapter 4 execution-time cell.

    ``cycles`` is the printed cell with A/D/Q substituted (one of the three
    named parameters above).  It is ``None`` where the printed cell is not
    a fixed number: a Min/Max range (MUL), the JMP fold/no-fold pair, the
    ENTER expression whose E is computed per instruction, or the Table 4-34
    ``8.S`` cell whose S p. 4-2 never defines.  ``source`` is the printed
    page and printed caption of the table the row appears in.
    """

    table: str
    op: str
    variant: str
    cycles: Optional[int]
    source: str
    note: str = ""


# The printed pages are the manual's own folios; the captions are the ones
# printed on those pages (Table 4-32..4-40, not the body text's 4-1..4-9;
# see hobbit/docs/timing_tables.md section 1).  Rows for instructions this
# model refuses are transcribed too: the table is the chapter's data, and
# the refusal is made by the instruction decoder, not by rewriting timings.
CHAPTER4: Tuple[CycleRow, ...] = (
    # --- Table 4-32, Simple Instruction, printed p. 4-3 -----------------
    CycleRow("Table 4-32", "ADD", "", 1, "p. 4-3 Table 4-32"),
    CycleRow("Table 4-32", "ADD3", "", 1, "p. 4-3 Table 4-32"),
    CycleRow("Table 4-32", "ADDI", "", 2, "p. 4-3 Table 4-32",
             "Printed ADD1 in Table 4-32; Table 3-1 and p. 3-6 print ADDI."),
    CycleRow("Table 4-32", "AND", "", 1, "p. 4-3 Table 4-32"),
    CycleRow("Table 4-32", "AND3", "", 1, "p. 4-3 Table 4-32"),
    CycleRow("Table 4-32", "ANDI", "", 2, "p. 4-3 Table 4-32"),
    CycleRow("Table 4-32", "CALL", "", 1, "p. 4-3 Table 4-32"),
    CycleRow("Table 4-32", "CLRE", "", 1, "p. 4-3 Table 4-32"),
    CycleRow("Table 4-32", "CMP", "", 1, "p. 4-3 Table 4-32",
             "CMP is not a Table 3-1 mnemonic; this row covers CMPEQ, "
             "CMPGT and CMPHI (p. 3-13)."),
    CycleRow("Table 4-32", "CPU", "", 0, "p. 4-3 Table 4-32",
             "Prefix only; a CPU-prefix IC miss adds a Table 4-37 penalty."),
    CycleRow("Table 4-32", "FLUSHI", "", 1, "p. 4-3 Table 4-32"),
    CycleRow("Table 4-32", "FLUSHP", "", 1, "p. 4-3 Table 4-32"),
    CycleRow("Table 4-32", "FLUSHPBE", "", 1, "p. 4-3 Table 4-32"),
    CycleRow("Table 4-32", "FLUSHPTE", "", 1, "p. 4-3 Table 4-32"),
    CycleRow("Table 4-32", "JMP", "", None, "p. 4-3 Table 4-32",
             "Printed Min 0, Max 1: 0 folded, 1 unfolded (p. 4-3 note)."),
    CycleRow("Table 4-32", "LDRAA", "", 1, "p. 4-3 Table 4-32"),
    CycleRow("Table 4-32", "MOV", "", 1, "p. 4-3 Table 4-32"),
    CycleRow("Table 4-32", "MOVA", "", 1, "p. 4-3 Table 4-32"),
    CycleRow("Table 4-32", "NOP", "", 1, "p. 4-3 Table 4-32"),
    CycleRow("Table 4-32", "OR", "", 1, "p. 4-3 Table 4-32"),
    CycleRow("Table 4-32", "OR3", "", 1, "p. 4-3 Table 4-32"),
    CycleRow("Table 4-32", "ORI", "", 2, "p. 4-3 Table 4-32"),
    CycleRow("Table 4-32", "RETURN", "", 2, "p. 4-3 Table 4-32",
             "RETURNs are always indirect; do not add an indirection "
             "delay (p. 4-3 note)."),
    CycleRow("Table 4-32", "POPN", "", 2, "p. 4-3 Table 4-32"),
    CycleRow("Table 4-32", "SHL", "", 1, "p. 4-3 Table 4-32"),
    CycleRow("Table 4-32", "SHL3", "", 1, "p. 4-3 Table 4-32"),
    CycleRow("Table 4-32", "SHR", "", 1, "p. 4-3 Table 4-32"),
    CycleRow("Table 4-32", "SHR3", "", 1, "p. 4-3 Table 4-32"),
    CycleRow("Table 4-32", "SUB", "", 1, "p. 4-3 Table 4-32"),
    CycleRow("Table 4-32", "SUB3", "", 1, "p. 4-3 Table 4-32"),
    CycleRow("Table 4-32", "TADD", "", 1, "p. 4-3 Table 4-32"),
    CycleRow("Table 4-32", "TESTC", "", 1, "p. 4-3 Table 4-32"),
    CycleRow("Table 4-32", "TESTV", "", 1, "p. 4-3 Table 4-32"),
    CycleRow("Table 4-32", "TSUB", "", 1, "p. 4-3 Table 4-32"),
    CycleRow("Table 4-32", "USHR", "", 1, "p. 4-3 Table 4-32"),
    CycleRow("Table 4-32", "USHR3", "", 1, "p. 4-3 Table 4-32"),
    CycleRow("Table 4-32", "XOR", "", 1, "p. 4-3 Table 4-32"),
    CycleRow("Table 4-32", "XOR3", "", 1, "p. 4-3 Table 4-32"),
    # --- Table 4-33, Multi-Cycle Arithmetic, printed p. 4-4 -------------
    CycleRow("Table 4-33", "DIV", "", 38, "p. 4-4 Table 4-33"),
    CycleRow("Table 4-33", "DIV3", "", 38, "p. 4-4 Table 4-33"),
    CycleRow("Table 4-33", "MUL", "", None, "p. 4-4 Table 4-33",
             "Printed Min 3, Max 20; data dependent."),
    CycleRow("Table 4-33", "MUL3", "", None, "p. 4-4 Table 4-33",
             "Printed Min 3, Max 20; data dependent."),
    CycleRow("Table 4-33", "REM", "", 38, "p. 4-4 Table 4-33"),
    CycleRow("Table 4-33", "REM3", "", 38, "p. 4-4 Table 4-33"),
    CycleRow("Table 4-33", "UDIV", "", 38, "p. 4-4 Table 4-33"),
    CycleRow("Table 4-33", "UREM", "", 38, "p. 4-4 Table 4-33"),
    # --- Table 4-34, DQM Instructions, printed p. 4-4 ------------------
    CycleRow("Table 4-34", "DQM", "Constant to SC double-word", 3,
             "p. 4-4 Table 4-34"),
    CycleRow("Table 4-34", "DQM", "Constant to SC quad-word", 5,
             "p. 4-4 Table 4-34"),
    CycleRow("Table 4-34", "DQM", "Constant to M double-word",
             1 + D_CYC, "p. 4-4 Table 4-34", "Printed 1 + D."),
    CycleRow("Table 4-34", "DQM", "Constant to M quad-word",
             1 + Q_CYC, "p. 4-4 Table 4-34", "Printed 1 + Q."),
    CycleRow("Table 4-34", "DQM", "SC double-word to SC double-word", 4,
             "p. 4-4 Table 4-34"),
    CycleRow("Table 4-34", "DQM", "SC quad-word to SC quad-word", 8,
             "p. 4-4 Table 4-34"),
    CycleRow("Table 4-34", "DQM", "SC/M double-word to M/SC double-word",
             2 + D_CYC, "p. 4-4 Table 4-34", "Printed 2 + D."),
    CycleRow("Table 4-34", "DQM", "SC/M quad-word to M/SC quad-word",
             4 + D_CYC, "p. 4-4 Table 4-34",
             "Printed 4 + D: a quad-word transfer priced with D, not Q. "
             "The manual gives no correction."),
    CycleRow("Table 4-34", "DQM", "M double-word to M double-word",
             2 * D_CYC, "p. 4-4 Table 4-34", "Printed 2.D."),
    CycleRow("Table 4-34", "DQM", "M quad-word to M quad-word", None,
             "p. 4-4 Table 4-34",
             "Printed 8.S; S is not in the p. 4-2 abbreviation list and is "
             "undefined, so no cycle value is encoded."),
    # --- Table 4-35, Conditional Jump, printed p. 4-5 ------------------
    CycleRow("Table 4-35", "JMP(F/N)(Y/N)",
             "Correct prediction, folded", 0, "p. 4-5 Table 4-35"),
    CycleRow("Table 4-35", "JMP(F/N)(Y/N)",
             "Correct prediction, unfolded", 1, "p. 4-5 Table 4-35"),
    CycleRow("Table 4-35", "JMP(F/N)(Y/N)",
             "Incorrect prediction, jump after compare", 3,
             "p. 4-5 Table 4-35"),
    CycleRow("Table 4-35", "JMP(F/N)(Y/N)",
             "Incorrect prediction, jump 2 instructions after compare", 2,
             "p. 4-5 Table 4-35"),
    CycleRow("Table 4-35", "JMP(F/N)(Y/N)",
             "Incorrect prediction, jump 3 instructions after compare", 1,
             "p. 4-5 Table 4-35"),
    CycleRow("Table 4-35", "JMP(F/N)(Y/N)",
             "Incorrect prediction, unfolded, 4 or more instructions "
             "after compare", 1, "p. 4-5 Table 4-35"),
    CycleRow("Table 4-35", "JMP(F/N)(Y/N)",
             "Incorrect prediction, folded, 4 or more instructions "
             "after compare", 0, "p. 4-5 Table 4-35"),
    # --- Table 4-36, Miscellaneous Instruction, printed p. 4-5 ---------
    CycleRow("Table 4-36", "CATCH", "", 1, "p. 4-5 Table 4-36",
             "A flat 1; no refill term is printed even though CATCH fills "
             "the cache in 16-byte blocks (pp. 3-10..3-11)."),
    CycleRow("Table 4-36", "CRET", "", 11 + Q_CYC,
             "p. 4-5 Table 4-36", "Printed 11 + Q."),
    CycleRow("Table 4-36", "ENTER", "", None, "p. 4-5 Table 4-36",
             "Printed 1 + (Q.E); E is computed per instruction from the "
             "pp. 3-19/3-20 flush loop (see _enter_offset)."),
    CycleRow("Table 4-36", "KCALL", "", 8 + D_CYC + A_CYC,
             "p. 4-5 Table 4-36", "Printed 8 + D + A."),
    CycleRow("Table 4-36", "KRET", "", 10 + D_CYC,
             "p. 4-5 Table 4-36", "Printed 10 + D."),
    CycleRow("Table 4-36", "Unimplemented opcode", "",
             7 + A_CYC, "p. 4-5 Table 4-36",
             "Printed 7 + A; FLUSHD and FLUSHDCE take this sequence "
             "(pp. 3-22, 3-23)."),
    CycleRow("Table 4-36", "Exception", "", 9 + D_CYC + A_CYC,
             "p. 4-5 Table 4-36", "Printed 9 + D + A."),
)

# Fixed per-mnemonic rows the decoder can look up.  Table 4-32 has one row
# per mnemonic; Tables 4-33 and 4-36 do too.  Table 4-34 is keyed by DQM
# form and Table 4-35 by branch condition, so neither is in this map.
_CYCLE_BY_OP: Dict[str, CycleRow] = {}
for _row in CHAPTER4:
    if _row.table in ("Table 4-32", "Table 4-33", "Table 4-36"):
        if _row.cycles is not None:
            assert _row.op not in _CYCLE_BY_OP, _row.op
            _CYCLE_BY_OP[_row.op] = _row

# ---------------------------------------------------------------------------
# State and record
# ---------------------------------------------------------------------------

@dataclass
class Timing:
    """Cycle-accounting state carried between instructions (not architectural).

    ``retired`` counts HRI records produced before the current instruction,
    so it is also the index the current record will have.  ``last_compare``
    is the ``retired`` index of the most recent CMPEQ/CMPGT/CMPHI, or -1.
    ``last_flag_source`` records what last wrote PSW.F: ``"compare"``,
    ``"other"`` (TESTC/TESTV), or ``"none"`` (reset).  Table 4-35 is
    indexed by distance from a compare, so the other sources have no
    printed incorrect-prediction row.

    ``prev_foldable`` says whether the instruction that retired immediately
    before could receive a folded one-parcel branch under the printed
    p. 4-7 rule; ``None`` means no instruction has retired yet.
    """

    retired: int = 0
    last_compare: int = -1
    last_flag_source: str = "none"
    prev_foldable: Optional[bool] = None


@dataclass
class State:
    """Architectural pre-state for one instruction.

    ``pc`` is the address of the instruction; ``sp`` and ``msp`` are the
    stack-cache bounds of printed p. 1-5 (SP is the inclusive lower bound,
    MSP the exclusive upper bound); ``psw`` carries only the bits this
    model uses; ``memory`` is a sparse byte-addressed image represented as
    a dict of word address -> 32-bit word (big-endian byte order);
    ``timing`` carries the non-architectural Chapter 4 account.
    """

    pc: int = 0
    sp: int = 0
    msp: int = 0
    psw: int = PSW_SP
    memory: Dict[int, int] = field(default_factory=dict)
    timing: Timing = field(default_factory=Timing)
    # Interrupt-stack pointer and vector base (Table 1-6 p. 1-13, p. 1-20).
    # They are architectural but have no field in the fixed HRI line; only
    # KCALL, KRET and CRET read or write them, and those instructions are
    # outside the core's implemented subset.  The CLI defaults are harness
    # values, not reset values (the manual does not print a reset ISP or VB).
    isp: int = 0x40
    vb: int = 0
    # CONFIG bit 16, kernel little-endian (Table 1-2, p. 1-10).  Only this
    # one CONFIG bit is modelled; it selects the data byte order at kernel
    # level as PSW bit 15 does at user level (p. 1-3).
    config_kl: bool = False
    # The stack cache's 64 words, indexed by address bits 7:2, or None.
    #
    # None (the default) keeps the model's original simplification: the
    # cache is invisible, every word lives in ``memory``, and only the
    # SP/MSP bounds are tracked.  That is exact for a program that reads
    # only what it has written.  It is *not* what the part does for a word
    # that was never written since it came into the window: ENTER extends
    # the window downward without loading anything, so such a word reads
    # whatever the cache slot last held (another frame's word, 256*k bytes
    # away), and a later flush writes that stale slot to memory (the
    # printed loops, pp. 3-19, 3-10).  1e's za copies such a word
    # (a structure with a never-assigned member), so a run that must agree
    # with the Bluespec core record for record sets this to 64 zeros
    # (tools/p9run.py) and the model then keeps the array: operands inside
    # [SP, MSP) are read from and stored to it, ENTER's flush copies
    # 16-byte blocks from it to memory, CATCH's fill copies them back.
    cache: Optional[List[int]] = None
    # The privileged machine (``System`` below), or None.  None is the
    # original one-instruction user-level model, unchanged: CSP = ISP,
    # virtual addressing, the CPU escape and the control registers are
    # refused.  A ``System`` enables them; see its docstring.
    system: Optional["System"] = None
    # Set by step() while it decodes the instruction after a CPU escape
    # (p. 3-14); False at every instruction boundary.
    cpu_prefix: bool = False
    # The part modelled: "92010" (default) or "92020S" (``PARTS``).
    part: str = "92010"
    # A 92020S run must set this to have cyc priced from the 92010's
    # Chapter 4 tables (no 92020 timing is published); without it every
    # 92020S step is refused.  Ignored for the 92010.
    borrow_92010_timing: bool = False

    @property
    def csp(self) -> int:
        """The current stack pointer (PSW bit 9, Table 1-8 p. 1-15).

        Without a ``System`` the model refuses CSP = ISP before decoding,
        so this is always SP there."""
        if self.system is not None and not (self.psw & PSW_SP):
            return self.isp
        return self.sp


# --- The privileged machine ------------------------------------------------
# CONFIG bits (Table 1-2, pp. 1-9..1-10).
CONFIG_KL = 1 << 16     # kernel little endian
CONFIG_PX = 1 << 17     # PC extension of 16-bit absolute addresses
CONFIG_SE = 1 << 18     # stack cache enable
CONFIG_T1IE = 1 << 24   # TIMER1 interrupt enable
CONFIG_T1X = 1 << 23    # TIMER1 counts only in kernel mode
CONFIG_T1CI = 1 << 22   # TIMER1 counts instructions
CONFIG_T2IE = 1 << 31
CONFIG_T2X = 1 << 30
PSW_IPL_SHIFT = 12      # bits 14:12 (Table 1-8 p. 1-15)

# Table 1-24 (p. 1-26): the register numbers of the CPU-modified mode 7.
REG_MSP, REG_ISP, REG_SP, REG_CONFIG, REG_PSW, REG_SHAD, REG_VB, \
    REG_STB, REG_FAULT, REG_ID, REG_TIMER1, REG_TIMER2 = range(1, 13)
REG_NAMES = {1: "MSP", 2: "ISP", 3: "SP", 4: "CONFIG", 5: "PSW", 6: "SHAD",
             7: "VB", 8: "STB", 9: "FAULT", 10: "ID", 11: "TIMER1",
             12: "TIMER2"}

# Table 1-26 (p. 1-38): exception identifiers.
EXC_ZDIV, EXC_TRACE, EXC_ILLINS, EXC_ALIGN, EXC_PRIV, EXC_REG, \
    EXC_FETCH, EXC_READ, EXC_WRITE = range(1, 10)

# STE / PTE bits (Tables 2-1, 2-2, 2-3, pp. 2-5..2-7).
STE_V, STE_W, STE_U, STE_S = 1, 2, 4, 8
PTE_V, PTE_W, PTE_U, PTE_R, PTE_M = 1, 2, 4, 8, 16


@dataclass
class System:
    """The privileged state of the part, for running a kernel.

    Everything here is from the printed PRM (January 1993).  It is off
    (``State.system is None``) for every user-level run, so the original
    model, its tests and its refusals are unchanged.  With it:

    * the control registers of §1.5 (pp. 1-8..1-20) exist and the CPU
      escape (p. 3-14) reads and writes them (mode 7, Table 1-22/1-24);
    * PSW bit 9 = 0 makes ISP the current stack pointer (p. 1-12, p. 1-15);
    * PSW bit 16 turns on the MMU walk of Chapter 2 (pp. 2-1..2-8);
    * CONFIG.PX extends 16-bit absolute addresses (Table 1-2, p. 1-10);
    * the exception, interrupt and unimplemented-instruction sequences of
      §1.11 (pp. 1-37..1-40) are performed instead of stopping;
    * physical memory and devices are ``bus``: ``bus.read(pa)`` returns a
      32-bit word (or raises ``BusError``), ``bus.write(pa, data, mask)``
      stores the lanes of ``mask`` (bit 3 = bits 31:24, the record's
      convention), so a device register is never read to be written.

    Not modelled, stated: the TLBs and NPSRs (p. 2-1) -- every access walks
    the tables, which is the same as the part for software that flushes
    after changing a table (p. 2-5, FLUSHPTE p. 3-27), and different only
    for software that relies on a stale entry; the instruction cache and
    prefetch buffer (FLUSHI/FLUSHP/FLUSHPBE are then no-ops: text is read
    from memory at every fetch); tracing (PSW bits 7, 8); the Chapter 4
    timing of anything the printed tables do not price (``untimed``).
    """

    bus: object = None
    config: int = 0                 # p. 1-9: 0 on reset
    shad: int = 0                   # p. 1-35: 0 on an external reset
    stb: int = 0
    fault: int = 0
    timer1: int = 0
    timer2: int = 0
    # The JTAG ID (Table 1-4, p. 1-11): version 1 (mask two), part 0,
    # manufacturer 0x3B.  Which mask the 1993 boards carried is not
    # printed; mask two is a choice.
    ident: int = 0x1000003B
    # Overflowed timers whose interrupt (level 1, Table 1-2) is pending.
    timer1_pending: bool = False
    timer2_pending: bool = False
    # Mnemonics whose Chapter 4 cost could not be resolved (cyc = 0).
    untimed: Dict[str, int] = field(default_factory=dict)
    # Set while KCALL and the event sequences make their own accesses
    # (the interrupt stack, the vector table) at kernel level.
    kernel_level: bool = False
    # Events taken, for the harness: (kind, ident, pc) tuples, newest last.
    events: List[Tuple[str, int, int]] = field(default_factory=list)
    # A harness choice, off by default: a CRET whose restored MSP is more
    # than the cache size above SP (p. 1-13: stack-cache results then
    # "unpredictable") fills the cache to SP + 256 and sets MSP there,
    # i.e. its CATCH portion stops when the cache is full (p. 3-10)
    # instead of being refused.  1e's notify() builds such frames, and
    # its _exception entry (raml.s) resets an MSP above SP + SCSIZE.
    cret_clamp: bool = False
    cret_clamps: int = 0


@dataclass
class Record:
    """The HRI (Hobbit Retirement Interface) record for one instruction."""

    pc: int
    insn0: int
    insn1: int
    sp_before: int
    sp_after: int
    msp_before: int
    msp_after: int
    mem_we: int
    mem_addr: int
    mem_wdata: int
    mem_wmask: int
    trap: int
    cyc: int = 0
    reason: str = ""

    def line(self) -> str:
        """Return the fixed one-line HRI form used by the trace differ."""
        return (
            "HRI pc=%04x insn=%04x%04x sp=%08x>%08x msp=%08x>%08x "
            "we=%d addr=%08x data=%08x mask=%02x trap=%d cyc=%d"
            % (
                self.pc & MASK32,
                self.insn0 & 0xFFFF,
                self.insn1 & 0xFFFF,
                self.sp_before & MASK32,
                self.sp_after & MASK32,
                self.msp_before & MASK32,
                self.msp_after & MASK32,
                self.mem_we,
                self.mem_addr & MASK32,
                self.mem_wdata & MASK32,
                self.mem_wmask & 0xFF,
                self.trap,
                self.cyc,
            )
        )


# ---------------------------------------------------------------------------
# Traps
# ---------------------------------------------------------------------------

class Trap(Exception):
    """An instruction that takes the unimplemented-instruction sequence.

    This is the only exception that produces a ``trap=1`` HRI line: the
    p. 1-39 sequence stores the opcode's own PC at ``*(CSP)`` and vectors
    through ``*(VB+12)``.  The one-instruction model reports the store and
    stops; the handler fetch is outside it.
    """

    def __init__(self, reason: str):
        super().__init__(reason)
        self.reason = reason


class Unimplemented(Trap):
    """FLUSHD / FLUSHDCE: implemented by the unimplemented sequence."""


class TrappedNiladic(Trap):
    """Niladic 0x200..0x3FF: the same sequence through VB+8 (p. 1-40).
    Raised only with a ``System``; without one these are refused."""


class Refusal(Exception):
    """A legal instruction or state outside this one-instruction subset.

    The adjudication's convention C2: a later refusal is *not* an HRI
    ``trap=1`` line.  The caller must not compare it as a retirement; the
    CLI reports it on stderr and stops.
    """

    def __init__(self, reason: str, parcels: Optional[List[int]] = None):
        super().__init__(reason)
        self.reason = reason
        self.parcels = parcels or []


class FetchFault(Refusal):
    """The parcel stream cannot be read (a fetch fault, not a trap)."""


class AlignmentFault(Refusal):
    pass


class IllegalInstruction(Refusal):
    pass


class Unsupported(Refusal):
    pass


class MemoryFault(Refusal):
    """An MMU translation fault (p. 2-3): exception 7 (fetch), 8 (read) or
    9 (write), with the faulting virtual address for FAULT (p. 1-39)."""

    def __init__(self, reason: str, ident: int, va: int):
        super().__init__(reason)
        self.ident = ident
        self.va = va & MASK32


class PrivilegeViolation(Refusal):
    """Exception 5 (Table 1-26): a privileged operation at user level."""


class UnimplementedRegister(Refusal):
    """Exception 6 (Table 1-26): CPU register 0 or 0xD..0xF (p. 1-27)."""


class Unsourced92020(Unsupported):
    """A 92020S case no source settles: refused, never guessed.

    The reserved encodings are where the 92020's Wait For Interrupt
    instruction (MPR 7:14 p. 1; AT&T press release 18 Oct 1993) must
    live, and its encoding is not known; a FLUSHPBE whose own address
    and target disagree in bit 10 is what Be's November 1994 kernel
    avoids on the 020, while its March kernel does exactly that
    (docs/att92020.md)."""


class ZeroDivide(Unsupported):
    """Exception 1 (Table 1-26, p. 3-17).  Without a ``System`` it is an
    ``Unsupported`` refusal, as before."""


class BusError(Refusal):
    """The machine model has nothing at a physical address.

    The part would take exception 0xA/0xB (Table 1-26) on an external bus
    error; the harness instead stops, because an undecoded address in a
    boot is a gap in the machine model, not a behaviour to emulate."""


# Refusals that are architectural exceptions when a ``System`` is present.
def _exception_ident(exc: Refusal) -> Optional[int]:
    if isinstance(exc, MemoryFault):
        return exc.ident
    if isinstance(exc, AlignmentFault):
        return EXC_ALIGN
    if isinstance(exc, IllegalInstruction):
        return EXC_ILLINS
    if isinstance(exc, PrivilegeViolation):
        return EXC_PRIV
    if isinstance(exc, UnimplementedRegister):
        return EXC_REG
    if isinstance(exc, ZeroDivide):
        return EXC_ZDIV
    return None


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------

def _sx(value: int, bits: int) -> int:
    """Sign-extend the low ``bits`` of ``value``."""
    value &= (1 << bits) - 1
    sign = 1 << (bits - 1)
    return (value ^ sign) - sign


def _in_cache(state: State, w: int) -> bool:
    """Does word address ``w`` hit the stack cache (p. 1-5, p. 1-12)?

    With a ``System`` the cache also has to be enabled (CONFIG.SE,
    Table 1-2 p. 1-10: "A 0 disables the stack cache from accessing")."""
    if state.cache is None or not (state.sp <= w < state.msp):
        return False
    sysm = state.system
    return sysm is None or bool(sysm.config & CONFIG_SE)


def _read_word(state: State, reader: Optional[Callable[[int], Optional[int]]],
               addr: int) -> int:
    """Read the big-endian word containing ``addr`` from overlay or image.

    Unwritten memory reads as zero.  This is a modelling choice (the PRM
    does not define a value for uninitialised memory); it is stated in the
    README so a trace difference cannot hide behind it.
    """
    w = addr & ~3
    if _in_cache(state, w):
        return state.cache[(w >> 2) & 63] & MASK32
    return _memory_word(state, reader, w)


def _translate(state: State, va: int, kind: str) -> int:
    """Chapter 2's walk: virtual word address -> physical (pp. 2-1..2-8).

    ``kind`` is "fetch", "read" or "write" (the three faults of p. 2-3).
    Physical addressing (PSW bit 16 = 0, Table 1-8 p. 1-14) is the
    identity.  The STE is at STB[31:12] : va[31:22] (p. 2-4); a nonpaged
    STE (bit 3 = 1, Table 2-2 p. 2-6) maps base[31:22] : va[21:0] if the
    page number va[21:12] is within the bound field (bits 21:12, "from
    4,096 bytes (0x0) to 4 MBs (0x3FF)"); a paged STE (Table 2-1 p. 2-5)
    points at a page table whose entry is at STE[31:12] : va[21:12]
    (p. 2-6) and maps PTE[31:12] : va[11:0] (p. 2-8).  The user bit is
    checked at user level and the writable bit on every store ("all valid
    segments/pages can be read", "can be accessed by the kernel", Tables
    2-2 and 2-3).  R and M are set in the memory copy of the PTE (Table
    2-3, p. 2-7).  There is no TLB (``System`` docstring).
    """
    if not (state.psw & PSW_VIRTUAL):
        return va & MASK32
    sysm = state.system
    bus = sysm.bus
    ident = {"fetch": EXC_FETCH, "read": EXC_READ, "write": EXC_WRITE}[kind]
    user = bool(state.psw & PSW_USER) and not sysm.kernel_level
    write = kind == "write"
    seg = (va >> 22) & 0x3FF
    ste = bus.read((sysm.stb & 0xFFFFF000) | (seg << 2)) & MASK32
    if not (ste & STE_V):
        raise MemoryFault("%s fault: segment 0x%03x of 0x%08x has no valid "
                          "STE (p. 2-3)" % (kind, seg, va), ident, va)
    page = (va >> 12) & 0x3FF
    if ste & STE_S:
        if page > ((ste >> 12) & 0x3FF):
            raise MemoryFault("%s fault: 0x%08x is beyond the bound of "
                              "nonpaged STE 0x%08x (Table 2-2)"
                              % (kind, va, ste), ident, va)
        if user and not (ste & STE_U):
            raise MemoryFault("%s fault: user access to kernel segment "
                              "0x%08x (Table 2-2)" % (kind, va), ident, va)
        if write and not (ste & STE_W):
            raise MemoryFault("write fault: segment of 0x%08x is not "
                              "writable (Table 2-2)" % va, ident, va)
        return (ste & 0xFFC00000) | (va & 0x003FFFFF)
    pte_addr = (ste & 0xFFFFF000) | (page << 2)
    pte = bus.read(pte_addr) & MASK32
    if not (pte & PTE_V):
        raise MemoryFault("%s fault: page of 0x%08x has no valid PTE "
                          "(p. 2-3)" % (kind, va), ident, va)
    if user and not (pte & PTE_U):
        raise MemoryFault("%s fault: user access to kernel page 0x%08x "
                          "(Table 2-3)" % (kind, va), ident, va)
    if write and not (pte & PTE_W):
        raise MemoryFault("write fault: page of 0x%08x is not writable "
                          "(Table 2-3)" % va, ident, va)
    want = PTE_R | (PTE_M if write else 0)
    if pte & want != want:
        bus.write(pte_addr, pte | want, 0xF)
    return (pte & 0xFFFFF000) | (va & 0xFFF)


def _memory_word(state: State,
                 reader: Optional[Callable[[int], Optional[int]]],
                 w: int, kind: str = "read") -> int:
    """The word of memory at ``w``, behind the stack cache."""
    if state.system is not None:
        return state.system.bus.read(_translate(state, w, kind)) & MASK32
    if w in state.memory:
        return state.memory[w] & MASK32
    if reader is not None:
        value = reader(w)
        if value is not None:
            return value & MASK32
    return 0


def _store_word(state: State, w: int, value: int, mask: int = 0xF) -> None:
    """Store a whole word: into the stack cache inside [SP, MSP) when the
    cache is modelled (p. 1-5, p. 1-12), otherwise into memory.

    With a ``System`` the memory store goes to the bus with its byte
    lanes (``mask``) and ``value`` carries only those lanes; inside the
    cache it is merged into the cached word."""
    if _in_cache(state, w):
        if state.system is not None and mask != 0xF:
            expanded = 0
            for bit in range(4):
                if mask & (1 << bit):
                    expanded |= 0xFF << (8 * bit)
            old = state.cache[(w >> 2) & 63]
            value = (old & ~expanded) | (value & expanded)
        state.cache[(w >> 2) & 63] = value & MASK32
    elif state.system is not None:
        state.system.bus.write(_translate(state, w, "write"),
                               value & MASK32, mask)
    else:
        state.memory[w] = value & MASK32


def _memory_store(state: State, w: int, value: int) -> None:
    """A whole word to memory, behind the stack cache (flushes)."""
    if state.system is not None:
        state.system.bus.write(_translate(state, w, "write"),
                               value & MASK32, 0xF)
    else:
        state.memory[w] = value & MASK32


def cache_flush(state: State,
                reader: Optional[Callable[[int], Optional[int]]],
                top: int, blocks: int) -> None:
    """ENTER's flush (p. 3-19): ``blocks`` 16-byte blocks, from the one
    below ``top`` downward, are copied from the stack cache to memory."""
    if state.cache is None:
        return
    if state.system is not None and not (state.system.config & CONFIG_SE):
        return
    for b in range(blocks):
        base = (top - 16 * (b + 1)) & MASK32
        for k in range(4):
            a = base + 4 * k
            _memory_store(state, a, state.cache[(a >> 2) & 63])


def cache_fill(state: State,
               reader: Optional[Callable[[int], Optional[int]]],
               lo: int, hi: int) -> None:
    """CATCH's fill (pp. 3-10, 3-11): the words of [lo, hi) are copied
    from memory into the stack cache."""
    if state.cache is None:
        return
    if state.system is not None and not (state.system.config & CONFIG_SE):
        return
    for a in range(lo, hi, 4):
        state.cache[(a >> 2) & 63] = _memory_word(state, reader, a)


def _fetch_word(state: State, reader: Optional[Callable[[int], Optional[int]]],
                addr: int) -> int:
    """Read one instruction word, distinguishing absent memory from zero."""
    w = addr & ~3
    if state.system is not None:
        return state.system.bus.read(_translate(state, w, "fetch")) & MASK32
    if w in state.memory:
        return state.memory[w] & MASK32
    if reader is not None:
        value = reader(w)
        if value is not None:
            return value & MASK32
    raise FetchFault("fetch-fault: no instruction word at 0x%08x" % w)


def _fetch_parcel(state: State, reader: Optional[Callable[[int], Optional[int]]],
                  addr: int) -> int:
    """Fetch the 16-bit parcel at ``addr`` (bit 0 is ignored, p. 1-4)."""
    addr &= ~1
    word = _fetch_word(state, reader, addr)
    return (word >> 16) & 0xFFFF if (addr & 2) == 0 else word & 0xFFFF


def _fetch_instruction(state: State,
                       reader: Optional[Callable[[int], Optional[int]]],
                       at: Optional[int] = None
                       ) -> Tuple[int, List[int], int]:
    """Fetch and length-decode one instruction (pp. 1-21..1-25)."""
    pc = (state.pc if at is None else at) & ~1
    parcels: List[int] = []
    try:
        p0 = _fetch_parcel(state, reader, pc)
        parcels.append(p0)
        if (p0 & 0x8000) == 0:
            length = 1
        elif (p0 & 0xC000) == 0x8000:
            length = 3
        else:                               # (p0 & 0xC000) == 0xC000
            length = 5
        for i in range(1, length):
            parcels.append(_fetch_parcel(state, reader, pc + 2 * i))
    except FetchFault as exc:
        raise FetchFault(exc.reason, parcels)
    return pc, parcels, length


# ---------------------------------------------------------------------------
# Operand addressing (PRM §1.7, Tables 1-21..1-24, pp. 1-25..1-27)
# ---------------------------------------------------------------------------

@dataclass
class Operand:
    size: int               # 1, 2 or 4 bytes
    signed: bool
    ea: int = 0             # effective byte address (memory operands)
    imm: int = 0            # immediate value (mode 0xF / 1-parcel imm5/wai5)
    is_imm: bool = False
    reg: int = -1           # control register (CPU-prefixed mode 7), or -1


def _abs_addr(field_value: int, width: int,
              state: Optional[State] = None) -> int:
    """Absolute address from a 16- or 32-bit field.

    The PRM (p. 1-23) makes the upper half come from CONFIG bit 17 (PC
    extension) when set: "bits 28:16 are replaced with 0 and bits 31:29
    ... are copied from bits 31:29 of the program counter".  Without a
    ``System`` CONFIG is fixed at its reset value of zero (p. 1-36), so
    16-bit absolute addresses are zero-extended.
    """
    if width != 16:
        return field_value & MASK32
    value = field_value & 0xFFFF
    if (state is not None and state.system is not None
            and state.system.config & CONFIG_PX):
        value |= state.pc & 0xE0000000
    return value


def _resolve_general(state: State,
                     reader: Optional[Callable[[int], Optional[int]]],
                     field_value: int, mode: int, width: int) -> Operand:
    """Decode a Table 1-21 general addressing mode.

    ``width`` is 16 for a three-parcel instruction and 32 for a
    five-parcel instruction; it selects the extension rule of p. 1-23.

    After a CPU prefix (``state.cpu_prefix``, System only) Table 1-22
    (p. 1-26) applies instead: mode 7 is a control register numbered by
    the field's low four bits (p. 1-27), the word modes 0xC..0xF are
    unchanged, and no other mode is defined for the pair (an illegal
    instruction, p. 1-39: "An unimplemented instruction is illegal if it
    follows a CPU instruction and contains an illegal addressing mode").
    """
    if state.cpu_prefix:
        if mode == 0x7:
            reg = field_value & 0xF
            if reg == 0 or reg > REG_TIMER2:
                raise UnimplementedRegister(
                    "unimplemented register 0x%x (Table 1-24 p. 1-26, "
                    "p. 1-27)" % reg)
            return Operand(4, False, reg=reg)
        if mode < 0xC:
            raise IllegalInstruction(
                "illegal: operand mode 0x%x after CPU (Table 1-22, "
                "p. 1-26)" % mode)
    if mode == 0xF:                                  # $data, immediate
        value = _sx(field_value, 16) if width == 16 else (field_value & MASK32)
        return Operand(4, True, imm=value, is_imm=True)

    if mode == 0xC:                                  # *$addr:W
        return Operand(4, True, ea=_abs_addr(field_value, width, state))

    if mode == 0xD:                                  # Roffset:W
        return Operand(4, True,
                       ea=(state.csp + _sx(field_value, width)) & MASK32)

    if mode == 0xE:                                  # *Roffset:W
        off = _sx(field_value, width)
        if off & 3:
            raise AlignmentFault(
                "alignment: stack-offset-indirect offset 0x%x is not "
                "word-aligned (p. 1-27)" % off)
        pointer = _read_word(state, reader, (state.csp + off) & MASK32)
        return Operand(4, True, ea=pointer)

    if 0 <= mode <= 0xB:
        size = 1 if mode in (0x0, 0x1, 0x4, 0x5, 0x8, 0x9) else 2
        signed = mode in (0x0, 0x2, 0x4, 0x6, 0x8, 0xA)
        if mode < 0x4:                               # *$addr:B/UB/H/UH
            ea = _abs_addr(field_value, width, state)
        else:                                        # Roffset or *Roffset
            off = _sx(field_value, width)
            ea = (state.csp + off) & MASK32
            if mode >= 0x8:                          # indirect
                if off & 3:
                    raise AlignmentFault(
                        "alignment: stack-offset-indirect offset 0x%x is "
                        "not word-aligned (p. 1-27)" % off)
                ea = _read_word(state, reader, ea)
        return Operand(size, signed, ea=ea)

    raise Unsupported("unsupported: operand mode 0x%x (Table 1-21, p. 1-25)"
                      % mode)


def _stk5(state: State, field_value: int) -> Operand:
    """One-parcel stk5: zero-extended then multiplied by four (p. 1-21)."""
    return Operand(4, True, ea=(state.csp + (field_value << 2)) & MASK32)


def _istk5(state: State, reader: Optional[Callable[[int], Optional[int]]],
           field_value: int) -> Operand:
    """One-parcel istk5: word stack offset indirect (p. 1-22)."""
    pointer = _read_word(state, reader,
                         (state.csp + (field_value << 2)) & MASK32)
    return Operand(4, True, ea=pointer)


def _imm5(field_value: int) -> Operand:
    """One-parcel imm5: sign-extended (p. 1-21)."""
    return Operand(4, True, imm=_sx(field_value, 5), is_imm=True)


def _wai5(field_value: int) -> Operand:
    """One-parcel wai5: unsigned, multiplied by four (p. 1-22)."""
    return Operand(4, True, imm=(field_value << 2) & MASK32, is_imm=True)


def _read_control(state: State, reg: int) -> int:
    """A control register read through mode 7 (Table 1-24, p. 1-26).

    Reserved bits read 0: bits 3:0 of ISP, MSP, SP, SHAD and VB (Tables
    1-5, 1-6, 1-9, 1-10, 1-14), bits 15:0 of CONFIG (Table 1-2), bits
    10:0 of STB (Table 1-11).  Register 0 and 0xD..0xF are the
    unimplemented-register exception 6 (p. 1-27; p. 3-14 calls register 0
    an "unimplemented instruction exception", and Table 1-26's
    identifier 6 is followed)."""
    sysm = state.system
    if reg == REG_MSP:
        return state.msp & ~0xF & MASK32
    if reg == REG_ISP:
        return state.isp & ~0xF & MASK32
    if reg == REG_SP:
        return state.sp & ~0xF & MASK32
    if reg == REG_CONFIG:
        return sysm.config & 0xFFFF0000
    if reg == REG_PSW:
        return state.psw & MASK32
    if reg == REG_SHAD:
        return sysm.shad & ~0xF & MASK32
    if reg == REG_VB:
        return state.vb & ~0xF & MASK32
    if reg == REG_STB:
        return sysm.stb & 0xFFFFF800
    if reg == REG_FAULT:
        return sysm.fault & MASK32
    if reg == REG_ID:
        # The 92010 keeps System.ident (a harness may pick mask one); any
        # other part answers with its own sourced ID (PARTS).
        if state.part != "92010":
            return part_info(state.part).ident
        return sysm.ident & MASK32
    if reg == REG_TIMER1:
        return sysm.timer1 & MASK32
    if reg == REG_TIMER2:
        return sysm.timer2 & MASK32
    raise UnimplementedRegister(
        "unimplemented register 0x%x (Table 1-24 p. 1-26, p. 1-27)" % reg)


def _write_control(state: State, reg: int, value: int) -> None:
    """A control register write through mode 7, at retirement.

    "When the SP is the direct destination ... the MSP is updated with
    the same value. This defines an empty stack cache" (p. 1-13).  SHAD
    follows a written CSP (p. 1-16: "any time the CSP is modified"), but
    not a PSW write that changes which pointer is the CSP (p. 1-15: the
    program must then MOV the new pointer to SHAD itself).  Writing STB
    flushes the TLBs (p. 1-18), which this model does not have.  ID
    writes do nothing (p. 1-11)."""
    sysm = state.system
    value &= MASK32
    if reg == REG_MSP:
        state.msp = value & ~0xF
    elif reg == REG_ISP:
        state.isp = value & ~0xF
        if not (state.psw & PSW_SP):
            sysm.shad = state.isp
    elif reg == REG_SP:
        state.sp = state.msp = value & ~0xF
        if state.psw & PSW_SP:
            sysm.shad = state.sp
    elif reg == REG_CONFIG:
        sysm.config = value & 0xFFFF0000
        state.config_kl = bool(sysm.config & CONFIG_KL)
    elif reg == REG_PSW:
        # Bits 3:0 "must be written with 0" and 31:17 are reserved
        # (Table 1-8, pp. 1-14, 1-16).
        state.psw = value & 0x0001FFF0
    elif reg == REG_SHAD:
        sysm.shad = value & ~0xF
    elif reg == REG_VB:
        state.vb = value & ~0xF
    elif reg == REG_STB:
        sysm.stb = value & 0xFFFFF800
    elif reg == REG_FAULT:
        sysm.fault = value
    elif reg == REG_ID:
        pass
    elif reg == REG_TIMER1:
        sysm.timer1 = value
    elif reg == REG_TIMER2:
        sysm.timer2 = value
    else:
        raise UnimplementedRegister(
            "unimplemented register 0x%x (Table 1-24 p. 1-26, p. 1-27)"
            % reg)


def _reserved_encoding(state: State, what: str) -> None:
    """Refuse an encoding the model does not implement for the 92010
    (an unassigned subcode, or a one-parcel ``unimp*`` cell the model
    already refused).

    On the 92010 it is outside the model (``Unsupported``), as before.
    On the 92020S it may be the Wait For Interrupt instruction, whose
    existence is sourced (MPR 7:14 p. 1; AT&T press release, 18 Oct
    1993) and whose encoding is not, so the refusal says so."""
    if state.part == "92020S":
        raise Unsourced92020(
            "unsourced (92020S): %s is not an implemented 92010 "
            "instruction and may be the 92020's Wait For Interrupt, whose "
            "encoding no source gives (docs/att92020.md)" % what)
    raise Unsupported("unsupported: %s" % what)


def _little_endian(state: State) -> bool:
    """Data byte order for the current execution level (p. 1-3, p. 1-4).

    "The User mode is set via the program status word (PSW) UL-bit ...
    The Kernel mode is set via the configuration register (CONFIG)
    KL-bit."  Text is always big-endian (p. 1-4 note): the parcel at the
    even address is bits 31:16 in either mode, so only the byte and
    half-word operand lanes below depend on this.
    """
    if state.psw & PSW_USER:
        return bool(state.psw & PSW_USER_LE)
    return state.config_kl


def _lane_shift(state: State, ea: int, size: int) -> int:
    """Bit position of a byte or half-word operand inside its word.

    Figure 1-2 (big-endian): BYTE0 is bits 31:24.  Figure 1-3
    (little-endian): BYTE0 is bits 7:0.
    """
    off = ea & 3
    if _little_endian(state):
        return 8 * off
    return 8 * (4 - size - off)


def _read_lanes(state: State,
                reader: Optional[Callable[[int], Optional[int]]],
                op: Operand) -> int:
    """A byte or half-word operand's word.  The bus still returns the
    whole word; a bus with a ``read_mask`` attribute is told, for the
    length of the read, which byte lanes the operand uses (the mask as
    for a store, bit 3 = bits 31:24), so a device with a register per
    byte (tools/beboot.py's display card) reads only the one addressed.
    A hook for the board models; the processor's behaviour is unchanged."""
    bus = state.system.bus if state.system is not None else None
    if bus is None or not hasattr(bus, "read_mask"):
        return _read_word(state, reader, op.ea)
    bus.read_mask = (((1 << op.size) - 1)
                     << (_lane_shift(state, op.ea, op.size) // 8))
    try:
        return _read_word(state, reader, op.ea)
    finally:
        bus.read_mask = 0xF


def _load(state: State, reader: Optional[Callable[[int], Optional[int]]],
          op: Operand) -> int:
    """Read and extend an operand (p. 1-3, p. 1-4, p. 1-28)."""
    if op.is_imm:
        return op.imm
    if op.reg >= 0:
        return _read_control(state, op.reg)
    if op.size == 4:
        if op.ea & 3:
            raise AlignmentFault(
                "alignment: word access to 0x%08x is not word-aligned "
                "(p. 1-4)" % op.ea)
        return _read_word(state, reader, op.ea)
    word = _read_lanes(state, reader, op)
    off = op.ea & 3
    if op.size == 2:
        if op.ea & 1:
            raise AlignmentFault(
                "alignment: half-word access to 0x%08x is not "
                "half-word-aligned (p. 1-4)" % op.ea)
        value = (word >> _lane_shift(state, op.ea, 2)) & 0xFFFF
        if op.signed and (value & 0x8000):
            value -= 0x10000
        return value
    # size == 1: bits 31:24 hold the byte at the lowest address when the
    # data is big-endian (Figure 1-2, p. 1-4), bits 7:0 when it is
    # little-endian (Figure 1-3).
    value = (word >> _lane_shift(state, op.ea, 1)) & 0xFF
    if op.signed and (value & 0x80):
        value -= 0x100
    return value


def _prepare_store(state: State,
                   reader: Optional[Callable[[int], Optional[int]]],
                   op: Operand, value: int) -> Tuple[int, int, int, int]:
    """Return (word address, new word value, bus data, byte mask).

    The record's byte-mark convention is fixed here and in the README:
    mask bit 3 is bits 31:24 of the word and bit 0 is bits 7:0 -- the
    byte at the word address in big-endian data, the byte at word address
    + 3 in little-endian data (Figures 1-2 and 1-3, p. 1-4).  The data
    word is the lane placement the bus would carry.  A word write has mask 0xF and
    data == value.
    """
    if op.is_imm:
        raise IllegalInstruction("illegal: store to an immediate operand")

    if op.size == 4:
        if op.ea & 3:
            raise AlignmentFault(
                "alignment: word access to 0x%08x is not word-aligned "
                "(p. 1-4)" % op.ea)
        word_addr = op.ea
        mask = 0xF
        data = value & MASK32
    elif op.size == 2:
        if op.ea & 1:
            raise AlignmentFault(
                "alignment: half-word access to 0x%08x is not "
                "half-word-aligned (p. 1-4)" % op.ea)
        word_addr = op.ea & ~3
        shift = _lane_shift(state, op.ea, 2)
        mask = 0x3 << (shift // 8)
        data = (value & 0xFFFF) << shift
    else:  # size == 1
        word_addr = op.ea & ~3
        shift = _lane_shift(state, op.ea, 1)
        mask = 1 << (shift // 8)
        data = (value & 0xFF) << shift

    if state.system is not None and not _in_cache(state, word_addr):
        # The bus takes the lanes; a device register is not read to be
        # written (``_store_word``).
        old = 0
    else:
        old = _read_word(state, reader, word_addr)
    expanded = 0
    for bit in range(4):
        if mask & (1 << bit):
            expanded |= 0xFF << (8 * bit)
    new_word = (old & (~expanded & MASK32)) | (data & expanded)
    return word_addr, new_word, data, mask


# ---------------------------------------------------------------------------
# Arithmetic flags (pp. 1-29..1-30)
# ---------------------------------------------------------------------------

def _add_result(psw: int, dst: int, src: int) -> Tuple[int, int, int]:
    a, b = dst & MASK32, src & MASK32
    raw = a + b
    result = raw & MASK32
    carry = 1 if raw > MASK32 else 0
    overflow = 1 if ((a ^ result) & (b ^ result) & 0x80000000) else 0
    new_psw = ((psw & ~(PSW_C | PSW_V))
               | (PSW_C if carry else 0)
               | (PSW_V if overflow else 0))
    return result, new_psw, carry


def _sub_result(psw: int, dst: int, src: int) -> Tuple[int, int, int]:
    a, b = dst & MASK32, src & MASK32
    result = (a - b) & MASK32
    borrow = 1 if a < b else 0
    overflow = 1 if ((a ^ b) & (a ^ result) & 0x80000000) else 0
    new_psw = ((psw & ~(PSW_C | PSW_V))
               | (PSW_C if borrow else 0)
               | (PSW_V if overflow else 0))
    return result, new_psw, borrow


def _mul_result(psw: int, dst: int, src: int, width: int
                ) -> Tuple[int, int, int]:
    """MUL/MUL3 product and flags (p. 3-34).

    "The PSW carry bit is set to 1 if the product of the operands as
    unsigned values overflows the destination (or accumulator);
    similarly, the PSW overflow bit is set to 1 if the product of the
    operands as signed values overflows the destination (or
    accumulator)."  ``width`` is the destination operand's byte width
    (four for MUL3's accumulator).  The product is computed at 32 bits
    and the destination store truncates it, as p. 3-3 shows the
    untruncated result surviving a byte destination.
    """
    a, b = dst & MASK32, src & MASK32
    unsigned = a * b
    signed = _sx(a, 32) * _sx(b, 32)
    bits = 8 * width
    carry = 1 if unsigned > (1 << bits) - 1 else 0
    overflow = 1 if (signed < -(1 << (bits - 1))
                     or signed > (1 << (bits - 1)) - 1) else 0
    new_psw = ((psw & ~(PSW_C | PSW_V))
               | (PSW_C if carry else 0)
               | (PSW_V if overflow else 0))
    return unsigned & MASK32, new_psw, carry


def _divide(dst: int, src: int) -> Tuple[int, int, int]:
    """One signed/unsigned division (pp. 3-17, 3-39).

    Returns (quotient, remainder, overflow).  The PRM says only "Two's
    complement division is performed" (p. 3-17) and that REM is defined
    in terms of DIV (p. 1-28); it does not print a rounding rule.  This
    model takes the standard two's-complement truncation: the quotient
    truncates toward zero and the remainder has the dividend's sign.
    That reading is named in the README, not presented as a printed
    fact.  Division by zero is the zero-divide exception (p. 3-17),
    which is an event outside this one-instruction model.
    """
    a = _sx(dst & MASK32, 32)
    b = _sx(src & MASK32, 32)
    if b == 0:
        raise ZeroDivide(
            "unsupported: divide-by-zero exception (p. 3-17); the event "
            "sequence is outside this model")
    quotient = abs(a) // abs(b)
    if (a < 0) != (b < 0):
        quotient = -quotient
    remainder = a - quotient * b
    overflow = 1 if (a == -0x80000000 and b == -1) else 0
    return quotient & MASK32, remainder & MASK32, overflow


def _udivide(dst: int, src: int) -> Tuple[int, int]:
    """Unsigned division and remainder (pp. 3-48, 3-49)."""
    a, b = dst & MASK32, src & MASK32
    if b == 0:
        raise ZeroDivide(
            "unsupported: divide-by-zero exception (p. 3-48); the event "
            "sequence is outside this model")
    return a // b, a % b


# ---------------------------------------------------------------------------
# Stack-cache bookkeeping (pp. 1-5..1-8, 3-10..3-11, 3-19..3-21, 3-38, 3-40)
# ---------------------------------------------------------------------------

def _check_stack_state(state: State) -> None:
    if state.sp & 0xF or state.msp & 0xF:
        raise Unsupported(
            "unpredictable: SP/MSP are not quad-word aligned "
            "(SP=0x%08x MSP=0x%08x; p. 1-5, Table 1-10/1-6)"
            % (state.sp, state.msp))
    if state.msp < state.sp or (state.msp - state.sp) > SCSIZE:
        raise Unsupported(
            "unpredictable: MSP must satisfy SP <= MSP <= SP+256 "
            "(SP=0x%08x MSP=0x%08x; p. 1-13)"
            % (state.sp, state.msp))
    if state.sp > MASK32 - SCSIZE:
        raise Unsupported(
            "unsupported: stack cache at SP=0x%08x would cross the 32-bit "
            "address boundary (p. 1-5)" % state.sp)


def _check_interrupt_stack(state: State, need_vb: bool = False) -> None:
    """ISP (and, for KCALL, VB) are quad-aligned; low bits are reserved.

    ISP: Table 1-6 (p. 1-13) and p. 1-12; VB: Table 1-14 (p. 1-20).
    The manual does not print either reset value, so the State defaults
    are harness choices (README).
    """
    if state.isp & 0xF:
        raise Unsupported(
            "unpredictable: ISP 0x%08x is not quad-word aligned "
            "(p. 1-12, Table 1-6 p. 1-13)" % state.isp)
    if state.isp < 16:
        raise Unsupported(
            "unpredictable: ISP 0x%08x cannot hold the 16-byte event "
            "frame (p. 1-12, p. 3-29)" % state.isp)
    if need_vb and state.vb & 0xF:
        raise Unsupported(
            "unpredictable: VB 0x%08x is not quad-word aligned "
            "(Table 1-14, p. 1-20)" % state.vb)


def _enter_flush_blocks(state: State, target: int) -> int:
    """Blocks the ENTER stack-offset flush loop moves (pp. 3-19..3-20).

    The pseudocode runs ``while (MSP > SHAD && MSP - target > SCSIZE)`` and
    subtracts 16 from MSP per iteration, each iteration writing one 16-byte
    block from the stack cache to memory.  ``SHAD`` is the cache's lower
    bound, which this model keeps equal to SP (p. 1-5), so the loop can move
    at most ``(MSP - SP) / 16`` valid blocks.  A final partial block counts
    as one iteration (the loop rounds up).  Table 4-36 prices each such
    block as a quad-word memory access Q (p. 4-5).
    """
    desired = state.msp - target - SCSIZE
    if desired <= 0:
        return 0
    blocks = (desired + 15) // 16
    valid = max(0, (state.msp - state.sp) // 16)
    return min(blocks, valid)


def _enter_offset(state: State, target: int) -> Tuple[int, int, int, int]:
    """ENTER stack-offset form (pp. 3-19..3-21).

    Returns (new_sp, new_msp, new_psw, flush_blocks).  The cache is flushed
    from the top until at most SCSIZE bytes remain.  By default the model
    keeps only the SP/MSP bounds (every cache write is already visible
    through the ordinary-memory model); with ``State.cache`` set, step()
    copies the flushed blocks from the array to memory (``cache_flush``).
    ``flush_blocks`` is the Chapter 4 E term for Table 4-36's
    ``1 + (Q.E)``, and the number of blocks that copy moves.
    """
    if target > state.sp:
        raise Unsupported(
            "unpredictable: ENTER target 0x%08x wrapped above SP 0x%08x "
            "(p. 3-21)" % (target, state.sp))
    if target > state.msp:
        raise Unsupported(
            "unpredictable: ENTER would leave SP 0x%08x above MSP 0x%08x "
            "(p. 3-21)" % (target, state.msp))
    blocks = _enter_flush_blocks(state, target)
    flushed = (state.msp - target) > SCSIZE
    new_msp = min(state.msp, target + SCSIZE)
    new_psw = state.psw & ~PSW_E
    if not flushed:
        new_psw |= PSW_E
    return target, new_msp, new_psw, blocks


def _catch_msp(state: State, target: int) -> int:
    """CATCH fill bound (pp. 3-10..3-11).

    The cache is filled upward from MSP in 16-byte blocks until MSP is at
    least ``target`` or the 64-word cache is full.  A target that is not a
    multiple of 16 is rounded up to the next multiple, as p. 3-11 says.
    """
    if state.msp < state.sp:
        raise Unsupported(
            "unpredictable: CATCH requires MSP >= SP (p. 3-11)")
    if target <= state.msp:
        return state.msp
    blocks = (target - state.msp + 15) // 16
    new_msp = state.msp + blocks * 16
    limit = state.sp + SCSIZE
    if new_msp > limit:
        new_msp = limit
    return new_msp


def _popn(state: State, offset: int) -> Tuple[int, int]:
    """POPN: SHAD = CSP = CSP + src; MSP follows a new SP above it."""
    if offset < 0:
        raise IllegalInstruction(
            "illegal: POPN negative offset -0x%x (p. 3-38)" % (-offset))
    new_sp = (state.sp + offset) & MASK32
    if new_sp < state.sp:
        raise Unsupported(
            "unpredictable: POPN offset 0x%x wraps the stack pointer "
            "(p. 3-38)" % offset)
    new_sp &= ~0xF          # SP bits 3:0 are reserved (Table 1-10, p. 1-17)
    new_msp = state.msp
    if new_sp > new_msp:
        new_msp = new_sp
    return new_sp, new_msp


def _return(state: State, reader: Optional[Callable[[int], Optional[int]]],
            offset: int) -> Tuple[int, int, int]:
    """RETURN: fetch PC, then advance SP, ignoring the offset's low 4 bits."""
    if offset < 0:
        raise IllegalInstruction(
            "illegal: RETURN negative offset -0x%x (p. 3-40)" % (-offset))
    if offset & 3:
        raise AlignmentFault(
            "alignment: RETURN PC word offset 0x%x is not word-aligned "
            "(p. 3-40)" % offset)
    read_addr = (state.sp + offset) & MASK32
    if read_addr < state.sp:
        raise Unsupported(
            "unpredictable: RETURN offset 0x%x wraps the stack pointer "
            "(p. 3-40)" % offset)
    new_pc = _read_word(state, reader, read_addr)
    delta = offset & ~0xF
    new_sp = (state.sp + delta) & MASK32
    new_msp = state.msp
    if new_sp > new_msp:
        new_msp = new_sp
    return new_pc, new_sp, new_msp


def _isp_enter(state: State, target: int) -> Tuple[int, int]:
    """ENTER with CSP = ISP: "SHAD = ISP = target", no cache traffic, and
    "PSW.E = 1" (pp. 3-19, 3-20).  Returns (new_isp, new_psw)."""
    return target & ~0xF & MASK32, state.psw | PSW_E


def _isp_popn(state: State, offset: int) -> int:
    """POPN with CSP = ISP: ISP += src (p. 3-38), quad-aligned (p. 1-12)."""
    if offset < 0:
        raise IllegalInstruction(
            "illegal: POPN negative offset -0x%x (p. 3-38)" % (-offset))
    return (state.isp + offset) & ~0xF & MASK32


def _isp_return(state: State,
                reader: Optional[Callable[[int], Optional[int]]],
                offset: int) -> Tuple[int, int]:
    """RETURN with CSP = ISP: PC = *(ISP + src), ISP += src (p. 3-40)."""
    if offset < 0:
        raise IllegalInstruction(
            "illegal: RETURN negative offset -0x%x (p. 3-40)" % (-offset))
    if offset & 3:
        raise AlignmentFault(
            "alignment: RETURN PC word offset 0x%x is not word-aligned "
            "(p. 3-40)" % offset)
    new_pc = _read_word(state, reader, (state.isp + offset) & MASK32)
    return new_pc, (state.isp + (offset & ~0xF)) & MASK32


# ---------------------------------------------------------------------------
# word32 and flow32 operands
# ---------------------------------------------------------------------------

def _word32_value(state: State,
                  reader: Optional[Callable[[int], Optional[int]]],
                  field_value: int, mode: int, width: int) -> int:
    """Value of a Table 3-2 ``word32`` operand.

    Modes 0xC and 0xE are memory values; mode 0xD is the stack-offset
    address itself (CATCH/ENTER interpret it as a new MSP target); mode
    0xF is the immediate value.
    """
    if mode == 0xD:
        return (state.csp + _sx(field_value, width)) & MASK32
    if mode == 0xF:
        return (_sx(field_value, 16) if width == 16
                else field_value & MASK32) & MASK32
    if mode == 0xC:
        addr = _abs_addr(field_value, width, state)
        if addr & 3:
            raise AlignmentFault(
                "alignment: word32 absolute address 0x%08x is not "
                "word-aligned (p. 1-4)" % addr)
        return _read_word(state, reader, addr)
    if mode == 0xE:
        off = _sx(field_value, width)
        if off & 3:
            raise AlignmentFault(
                "alignment: stack-offset-indirect offset 0x%x is not "
                "word-aligned (p. 1-27)" % off)
        return _read_word(state, reader, (state.csp + off) & MASK32)
    raise IllegalInstruction(
        "illegal: CATCH/ENTER operand mode 0x%x is not word32 "
        "(Tables 1-21, 3-2, pp. 1-25, 3-4)" % mode)


def _flow_target(state: State,
                 reader: Optional[Callable[[int], Optional[int]]],
                 field_value: int, mode: int, width: int,
                 name: str) -> int:
    """Decode a Table 1-23 CALL/JMP flow32 target (p. 1-26, p. 1-27).

    The 10-bit CALL/JMP offsets are multiplied by two (p. 1-21); the
    16- and 32-bit Label fields are byte offsets used as they stand,
    because p. 1-21 scales only the 10-bit fields.  That choice is called
    out in the README.
    """
    if mode == 0xC:                                  # **$addr
        addr = _abs_addr(field_value, width, state)
        if addr & 3:
            raise AlignmentFault(
                "alignment: %s absolute-indirect address 0x%08x is not "
                "word-aligned (p. 1-4)" % (name, addr))
        return _read_word(state, reader, addr)
    if mode == 0xD:                                  # *Roffset
        off = _sx(field_value, width)
        if off & 3:
            raise AlignmentFault(
                "alignment: %s stack-offset-indirect offset 0x%x is not "
                "word-aligned (p. 1-27)" % (name, off))
        return _read_word(state, reader, (state.csp + off) & MASK32)
    if mode == 0xE:                                  # Label
        return ((state.pc & ~1) + _sx(field_value, width)) & MASK32
    if mode == 0xF:                                  # *$addr
        return _abs_addr(field_value, width, state)
    raise IllegalInstruction(
        "illegal: %s operand mode 0x%x is not flow32 (Table 1-23, p. 1-26)"
        % (name, mode))


# ---------------------------------------------------------------------------
# Chapter 4 cycle helpers
# ---------------------------------------------------------------------------

# Table 4-35 rows keyed by their printed row text (p. 4-5).
_COND_CYCLES: Dict[str, Optional[int]] = {
    row.variant: row.cycles for row in CHAPTER4
    if row.table == "Table 4-35"
}


def _fixed_cycles(op: str) -> int:
    """Resolved cycles for a fixed Table 4-32/4-33/4-36 row."""
    row = _CYCLE_BY_OP.get(op)
    if row is None or row.cycles is None:
        raise RuntimeError("Chapter 4 has no fixed row for %r" % op)
    return row.cycles


def _foldable_target(length: int, p0: int) -> bool:
    """Can a one-parcel branch fold into this instruction? (p. 4-7)

    The printed rule: a one-parcel branch folds into a previous one- or
    three-parcel instruction unless that instruction is another jump of any
    kind, a one-parcel instruction with a five-bit opcode in 0x00..0x07, or
    any three-parcel monadic instruction.  A five-parcel instruction is not
    a fold target, because p. 4-7 limits a fold to a previous one- or
    three-parcel instruction.  The manual does not enumerate "another jump
    of any kind"; every encoding in this model that changes PC (KCALL,
    CALL, the stack class, JMP and the four conditional jumps) already falls
    under the 0x00..0x07 or three-parcel-monadic clause, so those clauses
    decide every case this model can execute.
    """
    if length == 1:
        return ((p0 >> 10) & 0x1F) >= 0x08
    if length == 3:
        return ((p0 >> 8) & 0x3F) != 0x00
    return False


def _conditional_jump_cycles(taken: bool, predicted_taken: bool,
                             folded: bool, timing: Timing) -> int:
    """Table 4-35 (printed p. 4-5), under the p. 4-7 folding rule.

    The rows without a folded/unfolded qualifier -- "jump after compare",
    "2 instructions after compare" and "3 instructions after compare" --
    apply to both folded and unfolded branches.  Only the "4 or more" rows
    split: unfolded 1, folded 0.  The manual prints no row for an incorrect
    prediction whose PSW.F was not set by a compare; this model refuses
    rather than inventing one.
    """
    if taken == predicted_taken:
        key = ("Correct prediction, folded" if folded
               else "Correct prediction, unfolded")
        value = _COND_CYCLES[key]
    else:
        if timing.last_flag_source != "compare" or timing.last_compare < 0:
            raise Refusal(
                "unsupported: conditional-jump prediction was wrong but "
                "PSW.F did not come from a compare; Table 4-35 (p. 4-5) "
                "prints no penalty row for that case")
        distance = timing.retired - timing.last_compare - 1
        if distance <= 0:
            key = "Incorrect prediction, jump after compare"
        elif distance == 1:
            key = "Incorrect prediction, jump 2 instructions after compare"
        elif distance == 2:
            key = "Incorrect prediction, jump 3 instructions after compare"
        elif folded:
            key = ("Incorrect prediction, folded, 4 or more instructions "
                   "after compare")
        else:
            key = ("Incorrect prediction, unfolded, 4 or more instructions "
                   "after compare")
        value = _COND_CYCLES[key]
    assert value is not None, key
    return value


_DQM_BY_VARIANT: Dict[str, Optional[int]] = {
    row.variant: row.cycles for row in CHAPTER4 if row.table == "Table 4-34"
}


def _sc_contains(state: State, addr: int) -> bool:
    """Is ``addr`` in the stack cache? (p. 1-5: SP <= ADDR < MSP.)"""
    return state.sp <= (addr & MASK32) < state.msp


def _dqm_cycles(state: State, constant: bool, src_addr: int,
                dst_addr: int, quad: bool) -> int:
    """Table 4-34 (printed p. 4-4) cell for one DQM transfer.

    The rows are selected by where the source and destination live: the
    stack cache (``SC``) when the address is inside ``[SP, MSP)``
    (p. 1-5), memory (``M``) otherwise, and ``Constant`` for source mode
    0xF.  The quad-word ``M`` to ``M`` row is the printed ``8.S``, and
    ``S`` is not defined on p. 4-2; it is resolved with the model's
    ``S_CYC`` (a choice, stated at its definition).
    """
    size = "quad-word" if quad else "double-word"
    dst_sc = _sc_contains(state, dst_addr)
    if constant:
        variant = ("Constant to SC " if dst_sc else "Constant to M ") + size
    else:
        src_sc = _sc_contains(state, src_addr)
        if src_sc and dst_sc:
            variant = "SC %s to SC %s" % (size, size)
        elif src_sc or dst_sc:
            variant = "SC/M %s to M/SC %s" % (size, size)
        else:
            variant = "M %s to M %s" % (size, size)
    value = _DQM_BY_VARIANT[variant]
    if value is None:
        # The printed 8.S cell; S is the model's S_CYC (see its comment).
        return 8 * S_CYC
    return value


def _retirement_cycles(mnemonic: str, folded: bool,
                       branch_taken: Optional[bool],
                       branch_predicted: Optional[bool],
                       flush_blocks: int, timing: Timing,
                       dqm_cycles: Optional[int] = None) -> int:
    """Chapter 4 occupancy of one retiring instruction.

    Base rows come from Tables 4-32, 4-33 and 4-36 (printed pp. 4-3..4-5)
    under the p. 4-1 assumptions; no Table 4-37..4-40 delay is added.  The
    ENTER row is 1 + (Q.E), E being the p. 3-19/3-20 flush blocks.  JMP is
    0 folded and 1 unfolded (Table 4-32 note, p. 4-3); the four conditional
    jumps use Table 4-35.
    """
    if mnemonic == "ENTER":
        # Table 4-36, p. 4-5: printed 1 + (Q . E), with E = flush blocks.
        return 1 + Q_CYC * flush_blocks
    if mnemonic == "DQM":
        # Table 4-34, p. 4-4: the cell is selected by operand location
        # and size; the caller resolved it with _dqm_cycles.
        if dqm_cycles is None:
            raise RuntimeError("DQM without a resolved Table 4-34 cell")
        return dqm_cycles
    if mnemonic in ("MUL", "MUL3"):
        # Table 4-33, p. 4-4: printed Min 3 / Max 20, data dependent.
        # MUL_CYC is the named model choice (printed maximum).
        return MUL_CYC
    if mnemonic in ("JMPFN", "JMPFY", "JMPTN", "JMPTY"):
        if branch_taken is None or branch_predicted is None:
            raise RuntimeError("conditional jump without a prediction")
        return _conditional_jump_cycles(branch_taken, branch_predicted,
                                        folded, timing)
    if mnemonic == "JMP":
        # Table 4-32, p. 4-3: Min 0 / Max 1, and the p. 4-3 note explains
        # that a folded unconditional jump takes no time, otherwise one.
        return 0 if folded else 1
    if mnemonic in ("CMPEQ", "CMPGT", "CMPHI"):
        # Table 4-32 prints one "CMP" row (p. 4-3); p. 3-13 gives it to all
        # three compare mnemonics.
        return _fixed_cycles("CMP")
    return _fixed_cycles(mnemonic)


# ---------------------------------------------------------------------------
# step()
# ---------------------------------------------------------------------------

def step(state: State,
         memory_reader: Optional[Callable[[int], Optional[int]]] = None
         ) -> Tuple[Record, State]:
    """Execute exactly one instruction.

    ``memory_reader`` is called with a word-aligned address and returns a
    32-bit word, or ``None`` when the address is not present.  The
    state's own ``memory`` overlay is consulted first, so writes made by
    earlier steps are visible.

    On a retired instruction the state is updated and returned.  On the
    unimplemented-instruction sequence the HRI record carries ``trap=1``
    and the p. 1-39 PC save at CSP; PC/SP/MSP/PSW remain at their
    pre-state values.  A ``Refusal`` is raised for a legal instruction or
    state outside the subset, including a fetch fault; the caller must
    not compare it as a retirement (adjudication convention C2).

    The record's ``cyc`` is the printed Chapter 4 occupancy under the
    p. 4-1 assumptions; ``state.timing`` carries the previous
    instruction's foldability and the compare that last wrote PSW.F so
    that Table 4-35 and the p. 4-7 folding rule can be applied.  A timing
    case with no printed row (an incorrectly predicted conditional jump
    whose flag did not come from a compare) raises ``Refusal`` and emits
    no HRI line.
    """
    pre_pc = state.pc & ~1
    pre_sp = state.sp & MASK32
    pre_msp = state.msp & MASK32
    insn0 = 0
    insn1 = 0

    try:
        # --- the part (PARTS): an unknown or refused one stops here ------
        if state.part == "92010":
            part = None                         # the fast, default path
        else:
            try:
                part = part_info(state.part)
            except ValueError as exc:
                raise Unsupported("unsupported: %s" % exc)
        if (part is not None and not part.own_timing
                and not state.borrow_92010_timing):
            raise Unsourced92020(
                "unsourced (%s): no Chapter 4 timing is published for this "
                "part; set borrow_92010_timing (CLI --borrow-92010-timing) "
                "to price cyc from the 92010's tables (docs/att92020.md)"
                % part.name)
        # --- state limitations, not instruction semantics -----------------
        if state.system is None and state.psw & PSW_VIRTUAL:
            raise Unsupported(
                "unsupported: virtual addressing (PSW bit 16); this model "
                "implements the physical address space only (p. 2-1)")
        if state.system is None and not (state.psw & PSW_SP):
            raise Unsupported(
                "unsupported: CSP is ISP (PSW bit 9 = 0); the interrupt "
                "stack is outside this model (p. 1-12)")
        _check_stack_state(state)
        # CSP = ISP (System only): "The ISP is not associated with the
        # stack cache" (p. 1-12), so ENTER, POPN and RETURN move ISP with
        # no cache traffic and CATCH is a no-op (pp. 3-10, 3-19..3-20).
        isp_mode = state.system is not None and not (state.psw & PSW_SP)

        pc, parcels, length = _fetch_instruction(state, memory_reader)
        insn0 = parcels[0]
        insn1 = parcels[1] if len(parcels) > 1 else 0
        next_pc = (pc + 2 * length) & MASK32
        if state.system is not None and length == 1 and parcels[0] == 0x2C00:
            # The CPU escape (niladic 0x0B/0x0, p. 3-14): "The instruction
            # following CPU is considered part of the CPU instruction"; an
            # event saves the CPU's PC, and the PC advances by four or six
            # parcels.  Only the three- and five-parcel forms have the
            # mode fields CPU modifies (Table 1-22, p. 1-26).
            _, parcels, length = _fetch_instruction(state, memory_reader,
                                                    pc + 2)
            if length == 1:
                raise IllegalInstruction(
                    "illegal: CPU followed by a one-parcel instruction "
                    "0x%04x (p. 3-14, Table 1-22)" % parcels[0])
            insn1 = parcels[0]
            next_pc = (pc + 2 + 2 * length) & MASK32
            state.cpu_prefix = True
        new_sp = state.sp
        new_msp = state.msp
        new_psw = state.psw
        new_isp = state.isp
        store: Optional[Tuple[Operand, int]] = None
        # Additional architectural stores the fixed one-write HRI line cannot
        # carry: the accumulator save of the interlocked instructions
        # (p. 3-6), the remaining words of a DQM block (p. 3-18) and the
        # PC/PSW words of KCALL's event frame (p. 3-29).  The record's one
        # write is the instruction's primary destination; these are applied
        # to memory as well and named in the README.
        extra_stores: List[Tuple[Operand, int]] = []
        # Chapter 4 accounting for this instruction (filled in by the decoder).
        mnemonic = ""
        folded = False
        branch_taken: Optional[bool] = None
        branch_predicted: Optional[bool] = None
        flush_blocks = 0
        dqm_cycles: Optional[int] = None
        # A one-parcel branch folds into the instruction immediately before it
        # (p. 4-7); the previous instruction's class decides whether it can.
        if (length == 1
                and ((parcels[0] >> 10) & 0x1F) in (0x03, 0x04, 0x05, 0x06,
                                                  0x07)):
            folded = bool(state.timing.prev_foldable)

        # =================================================================
        # One-parcel instructions (Table 1-15/1-16/1-17, p. 1-22)
        # =================================================================
        if length == 1:
            p0 = parcels[0]
            op = (p0 >> 10) & 0x1F
            src5 = (p0 >> 5) & 0x1F
            dst5 = p0 & 0x1F

            if op == 0x00:                            # KCALL imm10
                # p. 3-29: the 10-bit immediate is zero-extended and
                # multiplied by four; the source value, the return PC and
                # the PSW go to ISP-12/-8/-4 and ISP -= 16.
                mnemonic = "KCALL"
                _check_interrupt_stack(state, need_vb=True)
                src_value = ((p0 & 0x3FF) << 2) & MASK32
                frame = state.isp
                store = (Operand(4, True, ea=(frame - 12) & MASK32),
                         src_value)
                extra_stores = [
                    (Operand(4, True, ea=(frame - 8) & MASK32), next_pc),
                    (Operand(4, True, ea=(frame - 4) & MASK32), state.psw),
                ]
                new_isp = (frame - 16) & MASK32
                next_pc = _vector_word(state, memory_reader, state.vb)
                # "PSW = PSW & 0xFFFF0000": kernel level, ISP selected
                # as CSP, tracing/interrupts inhibited (p. 3-29).
                new_psw = state.psw & 0xFFFF0000
            elif op == 0x01:                          # CALL pcrel10
                mnemonic = "CALL"
                return_pc = next_pc
                target = (pc + (_sx(p0 & 0x3FF, 10) << 1)) & MASK32
                store = (Operand(4, True, ea=state.csp), return_pc)
                next_pc = target
            elif op == 0x02:                          # stack class
                sub = p0 & 0x3
                stk8 = (p0 >> 2) & 0xFF
                if sub == 0x0:                        # ENTER stk8
                    mnemonic = "ENTER"
                    # One-filled, not sign-extended: field 0 -> -4096,
                    # field 0xFF -> -16 (p. 1-21, p. 3-20).
                    offset = _sx(((0xFFFFFF00 | stk8) << 4) & MASK32, 32)
                    target = (state.csp + offset) & MASK32
                    if isp_mode:
                        new_isp, new_psw = _isp_enter(state, target)
                    else:
                        new_sp, new_msp, new_psw, flush_blocks = (
                            _enter_offset(state, target))
                elif sub == 0x1:                      # CATCH stk8
                    mnemonic = "CATCH"
                    if not isp_mode:
                        target = (state.sp + (stk8 << 4)) & MASK32
                        new_msp = _catch_msp(state, target)
                elif sub == 0x2:                      # RETURN stk8
                    mnemonic = "RETURN"
                    if isp_mode:
                        new_pc, new_isp = _isp_return(state, memory_reader,
                                                      stk8 << 4)
                    else:
                        new_pc, new_sp, new_msp = _return(
                            state, memory_reader, stk8 << 4)
                    next_pc = new_pc
                else:                                 # POPN stk8
                    mnemonic = "POPN"
                    if isp_mode:
                        new_isp = _isp_popn(state, stk8 << 4)
                    else:
                        new_sp, new_msp = _popn(state, stk8 << 4)
            elif op == 0x03:                          # JMP pcrel10
                mnemonic = "JMP"
                next_pc = (pc + (_sx(p0 & 0x3FF, 10) << 1)) & MASK32
            elif op in (0x04, 0x05, 0x06, 0x07):      # JMP(F/N)(Y/N)
                mnemonic = ("JMPFN", "JMPFY", "JMPTN", "JMPTY")[op - 4]
                target = (pc + (_sx(p0 & 0x3FF, 10) << 1)) & MASK32
                # T jumps when F=1; F jumps when F=0.  The low bit of the
                # opcode is the static Y (taken) / N (not taken) prediction
                # (Table 1-15, p. 1-22; p. 3-28).
                jump_if_true = op in (0x06, 0x07)
                branch_predicted = op in (0x05, 0x07)
                flag = bool(state.psw & PSW_F)
                branch_taken = flag == jump_if_true
                if branch_taken:
                    next_pc = target
            elif op == 0x0A:                          # MOV wai5, stk5
                mnemonic = "MOV"
                store = (_stk5(state, dst5),
                         _load(state, memory_reader, _wai5(src5)))
            elif op == 0x0B:                          # niladic
                sub = p0 & 0x3FF
                if sub == 0x002:
                    mnemonic = "NOP"
                    pass                              # NOP
                elif sub == 0x000:
                    raise Unsupported(
                        "unsupported: CPU register escape (niladic "
                        "0x0B/0x0; p. 3-14); control registers are not "
                        "modelled")
                elif 0x200 <= sub <= 0x3FF and state.system is not None:
                    raise TrappedNiladic(
                        "trapped niladic 0x%03x (VB+8; Table 1-17 p. 1-22, "
                        "p. 1-40)" % sub)
                elif 0x200 <= sub <= 0x3FF:
                    raise Unsupported(
                        "unsupported: trapped niladic 0x%03x (VB+8; "
                        "Table 1-17 p. 1-22, p. 1-40)" % sub)
                elif sub == 0x006:
                    raise Unimplemented(
                        "unsupported: FLUSHD (niladic 0x0B/0x6); there is "
                        "no data cache and the unimplemented-instruction "
                        "sequence is taken (p. 3-22)")
                elif sub == 0x001:                      # KRET
                    mnemonic = "KRET"
                    if state.psw & PSW_USER and state.system is not None:
                        raise PrivilegeViolation(
                            "privilege violation: KRET at user level "
                            "(p. 3-30)")
                    if state.psw & PSW_USER:
                        raise Unsupported(
                            "unsupported: privilege violation; KRET is "
                            "privileged (p. 3-30)")
                    _check_interrupt_stack(state)
                    next_pc = _read_word(state, memory_reader,
                                         (state.isp + 8) & MASK32)
                    new_psw = _read_word(state, memory_reader,
                                         (state.isp + 12) & MASK32)
                    new_isp = (state.isp + 16) & MASK32
                elif sub == 0x003 and state.system is not None:
                    # p. 3-24; no decoded-instruction cache is modelled
                    # (System docstring), so there is nothing to mark.
                    mnemonic = "FLUSHI"
                elif sub == 0x004 and state.system is not None:
                    mnemonic = "FLUSHP"                 # p. 3-25, likewise
                elif sub == 0x003:
                    raise Unsupported(
                        "unsupported: FLUSHI (niladic 0x0B/0x3; p. 3-24)")
                elif sub == 0x004:
                    raise Unsupported(
                        "unsupported: FLUSHP (niladic 0x0B/0x4; p. 3-25)")
                elif sub == 0x005:                      # CRET
                    mnemonic = "CRET"
                    if state.psw & PSW_USER and state.system is not None:
                        raise PrivilegeViolation(
                            "privilege violation: CRET at user level "
                            "(pp. 3-15, 3-16)")
                    if state.psw & PSW_USER:
                        raise Unsupported(
                            "unsupported: privilege violation; CRET is "
                            "privileged (pp. 3-15, 3-16)")
                    _check_interrupt_stack(state)
                    # SP = *(ISP+0); unconditional CATCH to *(ISP+4);
                    # MSP = *(ISP+4); PC = *(ISP+8); PSW = *(ISP+12);
                    # ISP += 16 (p. 3-15).  The cache is refilled, not
                    # written to memory, so the record has no store.
                    fetched_sp = _read_word(state, memory_reader,
                                            state.isp) & ~0xF
                    fetched_msp = _read_word(state, memory_reader,
                                             (state.isp + 4) & MASK32) & ~0xF
                    if (state.system is not None
                            and state.system.cret_clamp
                            and fetched_msp - fetched_sp > SCSIZE):
                        fetched_msp = fetched_sp + SCSIZE
                        state.system.cret_clamps += 1
                    if (fetched_msp < fetched_sp
                            or fetched_msp - fetched_sp > SCSIZE):
                        raise Unsupported(
                            "unpredictable: CRET restores SP=0x%08x "
                            "MSP=0x%08x, outside SP <= MSP <= SP+256 "
                            "(p. 1-13)" % (fetched_sp, fetched_msp))
                    if fetched_sp > MASK32 - SCSIZE:
                        raise Unsupported(
                            "unsupported: CRET restores SP=0x%08x whose "
                            "stack cache would cross the 32-bit address "
                            "boundary (p. 1-5)" % fetched_sp)
                    new_sp = fetched_sp
                    new_msp = fetched_msp
                    next_pc = _read_word(state, memory_reader,
                                         (state.isp + 8) & MASK32)
                    new_psw = _read_word(state, memory_reader,
                                         (state.isp + 12) & MASK32)
                    new_isp = (state.isp + 16) & MASK32
                elif sub == 0x008:                      # TESTV
                    mnemonic = "TESTV"
                    f = bool(state.psw & PSW_V)
                    new_psw = ((state.psw & ~(PSW_F | PSW_V))
                               | (PSW_F if f else 0))
                elif sub == 0x009:                      # TESTC
                    mnemonic = "TESTC"
                    f = bool(state.psw & PSW_C)
                    new_psw = ((state.psw & ~(PSW_F | PSW_C))
                               | (PSW_F if f else 0))
                elif sub == 0x00A:                      # CLRE
                    mnemonic = "CLRE"
                    new_psw = state.psw & ~PSW_E
                else:
                    _reserved_encoding(
                        state, "niladic subcode 0x%03x (Table 1-17, "
                        "p. 1-22)" % sub)
            elif op == 0x0D:                          # ADD3 wai5, stk5
                mnemonic = "ADD3"
                result, new_psw, _ = _add_result(
                    state.psw,
                    _load(state, memory_reader, _stk5(state, dst5)),
                    _load(state, memory_reader, _wai5(src5)))
                store = (Operand(4, True, ea=(state.csp + 4) & MASK32),
                         result)
            elif op == 0x0E:                          # AND3 imm5, stk5
                # p. 3-7: the one-parcel encodings are 0x0E AND3 imm5,stk5
                # and 0x0F AND stk5,stk5; "Acc = dst & src" and
                # "dst &= src" with C, V and F unchanged.
                mnemonic = "AND3"
                result = (_load(state, memory_reader, _stk5(state, dst5))
                          & _load(state, memory_reader, _imm5(src5)))
                store = (Operand(4, True, ea=(state.csp + 4) & MASK32),
                         result & MASK32)
            elif op == 0x0F:                          # AND stk5, stk5
                mnemonic = "AND"
                result = (_load(state, memory_reader, _stk5(state, dst5))
                          & _load(state, memory_reader, _stk5(state, src5)))
                store = (_stk5(state, dst5), result & MASK32)
            elif op == 0x10:                          # CMPEQ imm5, stk5
                mnemonic = "CMPEQ"
                src1 = _load(state, memory_reader, _imm5(src5))
                src2 = _load(state, memory_reader, _stk5(state, dst5))
                f = (src1 & MASK32) == (src2 & MASK32)
                new_psw = (state.psw & ~PSW_F) | (PSW_F if f else 0)
            elif op == 0x11:                          # CMPGT stk5, stk5
                mnemonic = "CMPGT"
                src1 = _load(state, memory_reader, _stk5(state, src5))
                src2 = _load(state, memory_reader, _stk5(state, dst5))
                f = _sx(src1 & MASK32, 32) > _sx(src2 & MASK32, 32)
                new_psw = (state.psw & ~PSW_F) | (PSW_F if f else 0)
            elif op == 0x12:                          # CMPGT imm5, stk5
                mnemonic = "CMPGT"
                src1 = _load(state, memory_reader, _imm5(src5))
                src2 = _load(state, memory_reader, _stk5(state, dst5))
                f = _sx(src1 & MASK32, 32) > _sx(src2 & MASK32, 32)
                new_psw = (state.psw & ~PSW_F) | (PSW_F if f else 0)
            elif op == 0x13:                          # CMPEQ stk5, stk5
                mnemonic = "CMPEQ"
                src1 = _load(state, memory_reader, _stk5(state, src5))
                src2 = _load(state, memory_reader, _stk5(state, dst5))
                f = (src1 & MASK32) == (src2 & MASK32)
                new_psw = (state.psw & ~PSW_F) | (PSW_F if f else 0)
            elif op == 0x14:                          # ADD imm5, stk5
                mnemonic = "ADD"
                result, new_psw, _ = _add_result(
                    state.psw,
                    _load(state, memory_reader, _stk5(state, dst5)),
                    _load(state, memory_reader, _imm5(src5)))
                store = (_stk5(state, dst5), result)
            elif op == 0x15:                          # ADD3 imm5, stk5
                mnemonic = "ADD3"
                result, new_psw, _ = _add_result(
                    state.psw,
                    _load(state, memory_reader, _stk5(state, dst5)),
                    _load(state, memory_reader, _imm5(src5)))
                store = (Operand(4, True, ea=(state.csp + 4) & MASK32),
                         result)
            elif op == 0x16:                          # ADD stk5, stk5
                mnemonic = "ADD"
                result, new_psw, _ = _add_result(
                    state.psw,
                    _load(state, memory_reader, _stk5(state, dst5)),
                    _load(state, memory_reader, _stk5(state, src5)))
                store = (_stk5(state, dst5), result)
            elif op == 0x17:                          # ADD3 stk5, stk5
                mnemonic = "ADD3"
                result, new_psw, _ = _add_result(
                    state.psw,
                    _load(state, memory_reader, _stk5(state, dst5)),
                    _load(state, memory_reader, _stk5(state, src5)))
                store = (Operand(4, True, ea=(state.csp + 4) & MASK32),
                         result)
            elif op == 0x18:                          # MOV stk5, stk5
                mnemonic = "MOV"
                store = (_stk5(state, dst5),
                         _load(state, memory_reader, _stk5(state, src5)))
            elif op == 0x19:                          # MOV istk5, stk5
                mnemonic = "MOV"
                store = (_stk5(state, dst5),
                         _load(state, memory_reader,
                               _istk5(state, memory_reader, src5)))
            elif op == 0x1A:                          # MOV stk5, istk5
                mnemonic = "MOV"
                store = (_istk5(state, memory_reader, dst5),
                         _load(state, memory_reader, _stk5(state, src5)))
            elif op == 0x1B:                          # MOV istk5, istk5
                mnemonic = "MOV"
                store = (_istk5(state, memory_reader, dst5),
                         _load(state, memory_reader,
                               _istk5(state, memory_reader, src5)))
            elif op == 0x1C:                          # MOV imm5, stk5
                mnemonic = "MOV"
                store = (_stk5(state, dst5),
                         _load(state, memory_reader, _imm5(src5)))
            elif op == 0x1D:                          # MOVA stk5, stk5
                mnemonic = "MOVA"
                # "The address of the source operand is calculated and
                # stored in the destination" (p. 3-33); both fields are
                # word stack offsets here.
                store = (_stk5(state, dst5), _stk5(state, src5).ea)
            elif op in (0x1E, 0x1F):                  # SHL3/SHR3 uimm5, stk5
                # Table 1-15 row 11 (p. 1-22): opcode 0x1E is SHL3.CS and
                # 0x1F is SHR3.CS, the one-parcel "C" (5-bit immediate
                # source) and "S" (5-bit word stack offset, scaled by 4)
                # forms.  p. 3-41: "SHL3: Acc = dst << Unsigned(src)";
                # p. 3-42: "SHR3: Acc = dst >> src" with the sign bit
                # copied as bits are shifted rightward.  Both pages print
                # the one-parcel encoding as uimm5, stk5.  Only the
                # low-order five bits of the source select the count (the
                # uimm5 field is already five bits); p. 3-41/3-42 say
                # nothing about C, V or F, so the PSW is unchanged.  For
                # SHL3/SHR3 the result goes to the accumulator at CSP+4
                # and the destination word is left unchanged (pp. 3-41,
                # 3-42; p. 1-7, Figure 1-4).
                mnemonic = "SHL3" if op == 0x1E else "SHR3"
                count = src5 & 0x1F
                dst_value = _load(state, memory_reader, _stk5(state, dst5))
                if op == 0x1E:
                    result = (dst_value << count) & MASK32
                else:
                    result = (_sx(dst_value & MASK32, 32) >> count) & MASK32
                store = (Operand(4, True, ea=(state.csp + 4) & MASK32),
                         result)
            else:
                _reserved_encoding(
                    state, "1-parcel opcode 0x%02x (Table 1-15, p. 1-22)"
                    % op)

        # =================================================================
        # Three- and five-parcel instructions
        # (Tables 1-18/1-19/1-20, pp. 1-24..1-25)
        # =================================================================
        else:
            p0 = parcels[0]
            opcode = (p0 >> 8) & 0x3F
            smode = (p0 >> 4) & 0xF
            dmode = p0 & 0xF
            width = 16 if length == 3 else 32
            if length == 3:
                field_src = parcels[1]
                field_dst = parcels[2]
            else:
                field_src = (parcels[1] << 16) | parcels[2]
                field_dst = (parcels[3] << 16) | parcels[4]

            if opcode == 0x00:
                if length == 5:
                    raise Unsupported(
                        "unsupported: five-parcel opcode 0x00 (Table 1-20, "
                        "p. 1-25)")
                sub = dmode            # low nibble; Table 1-19, p. 1-24
                # PRM p. 1-23: a three-parcel monadic operand is 32 bits,
                # OPERAND-HI in parcel 2 and OPERAND-LO in parcel 3.  The
                # dyadic forms below keep their 16-bit source/destination.
                mono = (parcels[1] << 16) | parcels[2]
                if sub == 0x1:                          # CALL
                    mnemonic = "CALL"
                    return_pc = next_pc
                    target = _flow_target(state, memory_reader, mono,
                                          smode, 32, "CALL")
                    store = (Operand(4, True, ea=state.csp), return_pc)
                    next_pc = target
                elif sub == 0x2:                        # RETURN
                    mnemonic = "RETURN"
                    if smode != 0xD:
                        raise IllegalInstruction(
                            "illegal: RETURN operand mode 0x%x (only "
                            "word stack offset, p. 3-40)" % smode)
                    if isp_mode:
                        new_pc, new_isp = _isp_return(state, memory_reader,
                                                      _sx(mono, 32))
                    else:
                        new_pc, new_sp, new_msp = _return(
                            state, memory_reader, _sx(mono, 32))
                    next_pc = new_pc
                elif sub == 0x3:                        # JMP
                    mnemonic = "JMP"
                    next_pc = _flow_target(state, memory_reader, mono,
                                           smode, 32, "JMP")
                elif sub in (0x4, 0x5, 0x6, 0x7):       # conditional
                    mnemonic = ("JMPFN", "JMPFY", "JMPTN", "JMPTY")[sub - 4]
                    if smode not in (0xE, 0xF):
                        raise IllegalInstruction(
                            "illegal: conditional jump operand mode 0x%x; "
                            "indirect modes are not allowed (p. 3-28)"
                            % smode)
                    target = _flow_target(state, memory_reader, mono,
                                          smode, 32, "JMP")
                    jump_if_true = sub in (0x6, 0x7)
                    branch_predicted = sub in (0x5, 0x7)
                    flag = bool(state.psw & PSW_F)
                    branch_taken = flag == jump_if_true
                    if branch_taken:
                        next_pc = target
                elif sub == 0x8:                        # CATCH
                    mnemonic = "CATCH"
                    target = _word32_value(state, memory_reader,
                                            mono, smode, 32)
                    if not isp_mode:
                        new_msp = _catch_msp(state, target)
                elif sub == 0x9:                        # ENTER
                    mnemonic = "ENTER"
                    if smode == 0xD:
                        raw = _sx(mono, 32)
                        if raw >= 0:
                            raise IllegalInstruction(
                                "illegal: ENTER stack offset 0x%x is not "
                                "negative; ENTER R0 included (p. 3-21)"
                                % raw)
                        offset = raw & ~0xF
                        target = (state.csp + offset) & MASK32
                        if isp_mode:
                            new_isp, new_psw = _isp_enter(state, target)
                        else:
                            new_sp, new_msp, new_psw, flush_blocks = (
                                _enter_offset(state, target))
                    elif isp_mode:
                        target = _word32_value(state, memory_reader,
                                                mono, smode, 32)
                        new_isp, new_psw = _isp_enter(state, target)
                    else:
                        target = _word32_value(state, memory_reader,
                                                mono, smode, 32)
                        target &= ~0xF
                        new_sp = target
                        new_msp = target
                        new_psw = state.psw & ~PSW_E  # unconditional flush
                        # p. 3-19 flushes every valid block (while MSP >
                        # SHAD, and SHAD is the cache's lower bound, SP).
                        flush_blocks = max(0, (state.msp - state.sp) // 16)
                elif sub == 0xF:                        # POPN
                    mnemonic = "POPN"
                    if smode != 0xD:
                        raise IllegalInstruction(
                            "illegal: POPN operand mode 0x%x (only "
                            "word stack offset, p. 3-38)" % smode)
                    if isp_mode:
                        new_isp = _isp_popn(state, _sx(mono, 32))
                    else:
                        new_sp, new_msp = _popn(
                            state, _sx(mono, 32))
                elif sub == 0x0:                        # KCALL
                    mnemonic = "KCALL"
                    _check_interrupt_stack(state, need_vb=True)
                    src_value = _word32_value(state, memory_reader,
                                              mono, smode, 32)
                    frame = state.isp
                    store = (Operand(4, True, ea=(frame - 12) & MASK32),
                             src_value)
                    extra_stores = [
                        (Operand(4, True, ea=(frame - 8) & MASK32),
                         next_pc),
                        (Operand(4, True, ea=(frame - 4) & MASK32),
                         state.psw),
                    ]
                    new_isp = (frame - 16) & MASK32
                    next_pc = _vector_word(state, memory_reader, state.vb)
                    new_psw = state.psw & 0xFFFF0000
                elif sub == 0xA:                        # LDRAA
                    mnemonic = "LDRAA"
                    # p. 3-31: the destination address is calculated as
                    # for a JMP and stored in the accumulator.
                    target = _flow_target(state, memory_reader, mono,
                                          smode, 32, "LDRAA")
                    store = (Operand(4, True, ea=(state.csp + 4) & MASK32),
                             target)
                elif sub in (0xB, 0xC) and state.system is not None:
                    # FLUSHPTE (p. 3-27) / FLUSHPBE (p. 3-26): the operand
                    # is an address; with no TLB, NPSR or prefetch buffer
                    # modelled there is no entry to mark invalid.
                    mnemonic = "FLUSHPTE" if sub == 0xB else "FLUSHPBE"
                    target = _word32_value(state, memory_reader, mono,
                                           smode, 32)
                    if sub == 0xC and state.part == "92020S" and smode == 0xD:
                        # Table 3-2 (p. 3-4): word32 is "A 32-bit value"
                        # in modes >= 0xC, and FLUSHPBE invalidates "the
                        # quad-word at src" (p. 3-26), so FLUSHPBE R20
                        # names the word held in R20 -- as Be's
                        # _flushpbe_020 uses it (it tests that word's bit
                        # 10) -- not the slot's address, which is the
                        # CATCH/ENTER reading _word32_value gives.
                        target = _read_word(
                            state, memory_reader,
                            (state.csp + _sx(mono, 32)) & MASK32)
                    elif sub == 0xC and state.part == "92020S" and smode == 0xE:
                        # Stack offset indirect: the value reading gives
                        # the word the pointer points at, while p. 3-27's
                        # FLUSHPTE note ("the address is moved into the
                        # stack cache and the stack offset indirect
                        # addressing mode is used") and Be's FLUSHPTE *R4
                        # read it as the pointer itself.  Which address
                        # the bit-10 rule applies to is not settled.
                        raise Unsourced92020(
                            "unsourced (92020S): FLUSHPBE with a stack-"
                            "offset-indirect operand; its target address "
                            "is ambiguous (Table 3-2 p. 3-4 against "
                            "p. 3-27) and the 020 rule depends on it "
                            "(docs/att92020.md)")
                    if (sub == 0xC and state.part == "92020S"
                            and ((pc ^ target) >> 10) & 1):
                        # Be's November 1994 kernel runs FLUSHPBE on the
                        # 020 only from an address whose bit 10 equals
                        # the target's (_flushpbe_020 picks the copy at
                        # _pbe_off or _pbe_on, and _main1 checks they
                        # have not moved); its March kernel pairs them
                        # the other way.  The model follows the later
                        # kernel and refuses the other case; no document
                        # found settles it (docs/att92020.md).
                        raise Unsourced92020(
                            "unsourced (92020S): FLUSHPBE at 0x%08x of "
                            "0x%08x, address bit 10 differs; Be's 020 "
                            "workarounds disagree (November avoids this, "
                            "March does only this) and no 92020 document "
                            "says what happens (docs/att92020.md)"
                            % (pc, target & MASK32))
                elif sub == 0xB:
                    raise Unsupported(
                        "unsupported: FLUSHPTE (monadic 0x00/0xB; p. 3-27)")
                elif sub == 0xC:
                    raise Unsupported(
                        "unsupported: FLUSHPBE (monadic 0x00/0xC; p. 3-26)")
                elif sub == 0xD:
                    raise Unimplemented(
                        "unsupported: FLUSHDCE (monadic 0x00/0xD); no data "
                        "cache, unimplemented sequence (p. 3-23)")
                else:
                    _reserved_encoding(
                        state, "monadic subcode 0x%x (Table 1-19, p. 1-24)"
                        % sub)

            elif opcode == 0x06:                        # MOV
                mnemonic = "MOV"
                src_op = _resolve_general(state, memory_reader, field_src,
                                          smode, width)
                dst_op = _resolve_general(state, memory_reader, field_dst,
                                          dmode, width)
                store = (dst_op, _load(state, memory_reader, src_op))

            elif opcode in (0x20, 0x23, 0x30, 0x33):    # SUB/ADD/SUB3/ADD3
                mnemonic = {0x20: "SUB", 0x23: "ADD",
                            0x30: "SUB3", 0x33: "ADD3"}[opcode]
                src_op = _resolve_general(state, memory_reader, field_src,
                                          smode, width)
                dst_op = _resolve_general(state, memory_reader, field_dst,
                                          dmode, width)
                src = _load(state, memory_reader, src_op)
                dst = _load(state, memory_reader, dst_op)
                to_acc = opcode in (0x30, 0x33)
                if opcode in (0x23, 0x33):
                    result, new_psw, _ = _add_result(state.psw, dst, src)
                else:
                    result, new_psw, _ = _sub_result(state.psw, dst, src)
                store = ((Operand(4, True, ea=(state.csp + 4) & MASK32)
                          if to_acc else dst_op), result)

            elif opcode in (0x1D, 0x1E, 0x1F):          # CMPGT/CMPHI/CMPEQ
                mnemonic = {0x1D: "CMPGT", 0x1E: "CMPHI",
                            0x1F: "CMPEQ"}[opcode]
                src1_op = _resolve_general(state, memory_reader, field_src,
                                           smode, width)
                src2_op = _resolve_general(state, memory_reader, field_dst,
                                           dmode, width)
                src1 = _load(state, memory_reader, src1_op)
                src2 = _load(state, memory_reader, src2_op)
                if opcode == 0x1D:                      # signed greater
                    f = _sx(src1 & MASK32, 32) > _sx(src2 & MASK32, 32)
                elif opcode == 0x1E:                    # unsigned higher
                    f = (src1 & MASK32) > (src2 & MASK32)
                else:                                   # equal
                    f = (src1 & MASK32) == (src2 & MASK32)
                new_psw = (state.psw & ~PSW_F) | (PSW_F if f else 0)

            elif opcode in (0x01, 0x02, 0x03):          # ORI/ANDI/ADDI
                mnemonic = {0x01: "ORI", 0x02: "ANDI", 0x03: "ADDI"}[opcode]
                src_op = _resolve_general(state, memory_reader, field_src,
                                          smode, width)
                dst_op = _resolve_general(state, memory_reader, field_dst,
                                          dmode, width)
                src = _load(state, memory_reader, src_op)
                old = _load(state, memory_reader, dst_op)
                if opcode == 0x01:
                    result = old | src
                elif opcode == 0x02:
                    result = old & src
                else:
                    result = (old + src) & MASK32
                # pp. 3-6, 3-8, 3-37: the original destination goes to
                # the accumulator, and carry/overflow are not affected.
                acc = Operand(4, True, ea=(state.csp + 4) & MASK32)
                if (dst_op.size == 4 and not dst_op.is_imm
                        and dst_op.ea == acc.ea):
                    # p. 3-6 note: "If R4 is the destination, after the
                    # interlocked instruction completes, R4 is the
                    # previous value of R4; hence, no operation."
                    store = (dst_op, old)
                else:
                    store = (dst_op, result)
                    extra_stores = [(acc, old)]

            elif opcode in (0x25, 0x35, 0x27, 0x37, 0x2F, 0x05):
                mnemonic = {0x25: "REM", 0x35: "REM3", 0x27: "DIV",
                            0x37: "DIV3", 0x2F: "UDIV",
                            0x05: "UREM"}[opcode]
                src_op = _resolve_general(state, memory_reader, field_src,
                                          smode, width)
                dst_op = _resolve_general(state, memory_reader, field_dst,
                                          dmode, width)
                src = _load(state, memory_reader, src_op)
                dst = _load(state, memory_reader, dst_op)
                to_acc = opcode in (0x35, 0x37)
                if opcode in (0x27, 0x37, 0x25, 0x35):
                    quotient, remainder, overflow = _divide(dst, src)
                    if opcode in (0x27, 0x37):
                        result = quotient
                        # p. 3-17: V is set only for 0x80000000 / -1 and
                        # cleared otherwise; C is unchanged.
                        new_psw = ((state.psw & ~PSW_V)
                                   | (PSW_V if overflow else 0))
                    else:
                        result = remainder
                        # p. 3-39: V is always cleared; C is unchanged.
                        new_psw = state.psw & ~PSW_V
                else:
                    quotient, remainder = _udivide(dst, src)
                    result = quotient if opcode == 0x2F else remainder
                    # pp. 3-48, 3-49: C is always cleared; V unchanged.
                    new_psw = state.psw & ~PSW_C
                store = ((Operand(4, True, ea=(state.csp + 4) & MASK32)
                          if to_acc else dst_op), result)

            elif opcode in (0x26, 0x36):                # MUL/MUL3
                mnemonic = "MUL3" if opcode == 0x36 else "MUL"
                src_op = _resolve_general(state, memory_reader, field_src,
                                          smode, width)
                dst_op = _resolve_general(state, memory_reader, field_dst,
                                          dmode, width)
                src = _load(state, memory_reader, src_op)
                dst = _load(state, memory_reader, dst_op)
                to_acc = opcode == 0x36
                width_bytes = 4 if to_acc else dst_op.size
                result, new_psw, _ = _mul_result(state.psw, dst, src,
                                                 width_bytes)
                store = ((Operand(4, True, ea=(state.csp + 4) & MASK32)
                          if to_acc else dst_op), result)

            elif opcode in (0x0C, 0x0D):                # TADD/TSUB
                mnemonic = "TADD" if opcode == 0x0C else "TSUB"
                src_op = _resolve_general(state, memory_reader, field_src,
                                          smode, width)
                dst_op = _resolve_general(state, memory_reader, field_dst,
                                          dmode, width)
                src = _load(state, memory_reader, src_op)
                dst = _load(state, memory_reader, dst_op)
                if (src & 3) or (dst & 3):
                    # p. 3-44 / p. 3-47: a tagged operand sets F and
                    # leaves C and V as they were; nothing is stored.
                    new_psw = (state.psw & ~PSW_F) | PSW_F
                else:
                    if opcode == 0x0C:
                        result, new_psw, _ = _add_result(state.psw, dst, src)
                    else:
                        result, new_psw, _ = _sub_result(state.psw, dst, src)
                    f = bool(new_psw & PSW_V)
                    new_psw = ((new_psw & ~PSW_F) | (PSW_F if f else 0))
                    if not f:
                        store = (dst_op, result)

            elif opcode in (0x21, 0x22, 0x24, 0x31, 0x32, 0x34):
                # Bitwise OR/AND/XOR and their `[3]` forms: Tables 1-18 and
                # 1-20 print 0x21 OR, 0x22 AND, 0x24 XOR, 0x31 OR3,
                # 0x32 AND3, 0x34 XOR3; the pages print "dst |= src",
                # "dst &= src", "dst ^= src" (p. 3-36 OR, p. 3-7 AND,
                # p. 3-51 XOR) and the `[3]` forms write the accumulator
                # instead (p. 3-1, p. 1-7).  C, V and F are unchanged.
                mnemonic = {0x21: "OR", 0x22: "AND", 0x24: "XOR",
                            0x31: "OR3", 0x32: "AND3", 0x34: "XOR3"}[opcode]
                src_op = _resolve_general(state, memory_reader, field_src,
                                          smode, width)
                dst_op = _resolve_general(state, memory_reader, field_dst,
                                          dmode, width)
                src = _load(state, memory_reader, src_op)
                dst = _load(state, memory_reader, dst_op)
                if opcode == 0x21 or opcode == 0x31:
                    result = dst | src
                elif opcode == 0x22 or opcode == 0x32:
                    result = dst & src
                else:
                    result = dst ^ src
                to_acc = opcode in (0x31, 0x32, 0x34)
                store = ((Operand(4, True, ea=(state.csp + 4) & MASK32)
                          if to_acc else dst_op), result & MASK32)

            elif opcode in (0x2C, 0x2D, 0x2E, 0x3C, 0x3D, 0x3E):
                # Shifts: 0x2C SHR, 0x2D USHR, 0x2E SHL and their `[3]`
                # forms 0x3C/0x3D/0x3E (Tables 1-18/1-20).  p. 3-41 SHL:
                # "dst <<= Unsigned(src)", zeros fill; p. 3-42 SHR: the
                # sign bit is copied into the vacated bits; p. 3-50 USHR:
                # zeros fill.  Only the low-order five bits of the source
                # select the count, and the `[3]` forms leave the
                # destination unchanged and write the accumulator.
                mnemonic = {0x2C: "SHR", 0x2D: "USHR", 0x2E: "SHL",
                            0x3C: "SHR3", 0x3D: "USHR3", 0x3E: "SHL3"}[opcode]
                src_op = _resolve_general(state, memory_reader, field_src,
                                          smode, width)
                dst_op = _resolve_general(state, memory_reader, field_dst,
                                          dmode, width)
                count = _load(state, memory_reader, src_op) & 0x1F
                value = _load(state, memory_reader, dst_op)
                if opcode in (0x2E, 0x3E):              # SHL[3]
                    result = (value << count) & MASK32
                elif opcode in (0x2C, 0x3C):            # SHR[3], arithmetic
                    result = (_sx(value & MASK32, 32) >> count) & MASK32
                else:                                   # USHR[3], logical
                    result = (value & MASK32) >> count
                to_acc = opcode in (0x3C, 0x3D, 0x3E)
                store = ((Operand(4, True, ea=(state.csp + 4) & MASK32)
                          if to_acc else dst_op), result & MASK32)

            elif opcode == 0x04:                        # MOVA
                mnemonic = "MOVA"
                # p. 3-33: source must be a word addressing mode
                # (0xC/0xD/0xE); the Notes make an immediate, register
                # or register destination illegal.  The printed
                # footnote and Notes conflict on the immediate source;
                # the more specific Notes are followed (README).
                if smode not in (0xC, 0xD, 0xE):
                    raise IllegalInstruction(
                        "illegal: MOVA source mode 0x%x is not a word "
                        "mode (p. 3-33)" % smode)
                if dmode == 0x7:
                    raise IllegalInstruction(
                        "illegal: MOVA register destination (p. 3-33)")
                src_op = _resolve_general(state, memory_reader, field_src,
                                          smode, width)
                dst_op = _resolve_general(state, memory_reader, field_dst,
                                          dmode, width)
                store = (dst_op, src_op.ea)

            elif opcode == 0x07:                        # DQM
                mnemonic = "DQM"
                if dmode == 0xF:
                    raise IllegalInstruction(
                        "illegal: DQM immediate destination (p. 3-18)")
                if dmode in (0x0, 0x4, 0x8):
                    quad = False
                elif dmode in (0xC, 0xD, 0xE):
                    quad = True
                else:
                    # p. 3-18's description says alignment fault and its
                    # Notes say illegal sequence; the Notes are followed.
                    raise IllegalInstruction(
                        "illegal: DQM destination mode 0x%x (p. 3-18)"
                        % dmode)
                if smode not in (0xC, 0xD, 0xE, 0xF):
                    raise IllegalInstruction(
                        "illegal: DQM source mode 0x%x is not a word "
                        "mode (p. 3-18)" % smode)
                constant = smode == 0xF
                if constant:
                    src_value = _word32_value(state, memory_reader,
                                              field_src, smode, width)
                    src_addr = 0
                else:
                    src_op = _resolve_general(state, memory_reader,
                                              field_src, smode, width)
                    src_addr = src_op.ea
                    src_value = 0
                dst_op = _resolve_general(state, memory_reader, field_dst,
                                          dmode, width)
                dst_addr = dst_op.ea
                bound = 0x10 if quad else 0x8
                if src_addr & (bound - 1):
                    raise AlignmentFault(
                        "alignment: DQM source 0x%08x is not %d-byte "
                        "aligned (p. 3-18)" % (src_addr, bound))
                if dst_addr & (bound - 1):
                    raise AlignmentFault(
                        "alignment: DQM destination 0x%08x is not "
                        "%d-byte aligned (p. 3-18)" % (dst_addr, bound))
                words = 4 if quad else 2
                if constant:
                    values = [src_value] * words
                else:
                    if src_addr > MASK32 - 4 * (words - 1):
                        raise Unsupported(
                            "unpredictable: DQM source block at 0x%08x "
                            "wraps the 32-bit address space" % src_addr)
                    values = [_read_word(state, memory_reader,
                                         (src_addr + 4 * i) & MASK32)
                              for i in range(words)]
                if dst_addr > MASK32 - 4 * (words - 1):
                    raise Unsupported(
                        "unpredictable: DQM destination block at 0x%08x "
                        "wraps the 32-bit address space" % dst_addr)
                dqm_cycles = _dqm_cycles(state, constant, src_addr,
                                         dst_addr, quad)
                # The fixed one-write line carries the lowest-addressed
                # word; the remaining words are applied to memory too.
                store = (Operand(4, True, ea=dst_addr), values[0])
                extra_stores = [
                    (Operand(4, True, ea=(dst_addr + 4 * i) & MASK32),
                     values[i]) for i in range(1, words)
                ]

            else:
                # Every remaining cell of Tables 1-18 and 1-20 is printed
                # "unimp*": "The unimplemented instruction sequence is
                # performed" (pp. 1-24, 1-25), and "there are no tests
                # performed on the addressing modes of unimplemented
                # dyadic instructions" (p. 1-39).  These are the opcodes
                # an operating system emulates -- 1e's floating point
                # (FMOV 0x11, FADD 0x2b, ...) lives here.
                raise Trap(
                    "unimplemented: %s opcode 0x%02x (Table 1-%d, p. 1-%d; "
                    "sequence p. 1-39)"
                    % ("five-parcel" if length == 5 else "three-parcel",
                       opcode, 20 if length == 5 else 18,
                       25 if length == 5 else 24))

        # --- Chapter 4 occupancy, then the one architectural write -------
        sysm = state.system
        state.cpu_prefix = False
        if sysm is None:
            cyc = _retirement_cycles(mnemonic, folded, branch_taken,
                                     branch_predicted, flush_blocks,
                                     state.timing, dqm_cycles)
        else:
            # A kernel restores PSW.F with KRET/CRET and executes the
            # privileged instructions; where Chapter 4 prints no cell the
            # boot must not stop for a timing reason, so cyc is 0 and the
            # mnemonic is counted in System.untimed.
            try:
                cyc = _retirement_cycles(mnemonic, folded, branch_taken,
                                         branch_predicted, flush_blocks,
                                         state.timing, dqm_cycles)
            except (Refusal, RuntimeError):
                cyc = 0
                key = mnemonic or "?"
                sysm.untimed[key] = sysm.untimed.get(key, 0) + 1
        reg_store: Optional[Tuple[Operand, int]] = None
        if store is not None and store[0].reg >= 0:
            # "if there is a register write in user mode, a privilege
            # violation exception sequence ... is performed" (p. 1-27).
            if state.psw & PSW_USER:
                raise PrivilegeViolation(
                    "privilege violation: write of %s at user level "
                    "(p. 1-27)" % REG_NAMES[store[0].reg])
            reg_store, store = store, None
            if (state.part == "92020S" and reg_store[0].reg == REG_CONFIG
                    and reg_store[1] & 0xFFFF):
                # Reserved (=0) on the 92010 (Table 1-2, p. 1-10); the
                # 92020 may give them a meaning (its larger prefetch
                # buffer, its wait state) and no 92020 CONFIG table has
                # been found.  Checked here, before anything is committed.
                raise Unsourced92020(
                    "unsourced (92020S): CONFIG write 0x%08x sets reserved "
                    "bits 15:0, whose 92020 meaning no source gives "
                    "(docs/att92020.md)" % (reg_store[1] & MASK32))
        if sysm is not None and mnemonic == "KCALL":
            # KCALL's frame goes to the interrupt stack at kernel level
            # (a fault there resets the part, p. 3-29), from any level.
            sysm.kernel_level = True
        if sysm is not None and extra_stores:
            # Translate every store before making any, so that a write
            # fault (p. 2-3) leaves no half-done instruction behind.
            for op_, _v in ([store] if store else []) + extra_stores:
                w = op_.ea & ~3 & MASK32
                if not op_.is_imm and op_.reg < 0 and not _in_cache(state, w):
                    _translate(state, w, "write")
        pre_isp = state.isp & MASK32
        pre_psw = state.psw

        mem_we = 0
        mem_addr = 0
        mem_wdata = 0
        mem_wmask = 0
        if store is not None:
            store_op, store_value = store
            word_addr, new_word, mem_wdata, mem_wmask = _prepare_store(
                state, memory_reader, store_op, store_value)
            _store_word(state, word_addr, new_word, mem_wmask)
            mem_we = 1
            mem_addr = word_addr
        for extra_op, extra_value in extra_stores:
            extra_addr, extra_word, _, extra_mask = _prepare_store(
                state, memory_reader, extra_op, extra_value)
            _store_word(state, extra_addr, extra_word, extra_mask)

        # The stack cache's contents, when modelled: ENTER flushes blocks
        # from the top of the window before the pointers move, CATCH fills
        # the words it brings in.  (No instruction both stores and moves
        # SP or MSP, so the stores above used the window they belong to.)
        if state.cache is not None:
            if mnemonic == "ENTER" and flush_blocks:
                cache_flush(state, memory_reader, pre_msp, flush_blocks)
            elif mnemonic == "CATCH" and (new_msp & MASK32) > pre_msp:
                cache_fill(state, memory_reader, pre_msp, new_msp & MASK32)
        if sysm is not None and mnemonic == "ENTER" and not isp_mode:
            # p. 3-21: "the target address and the new MSP, if the MSP is
            # updated, are checked to verify that stores are valid at the
            # current execution level.  If [not], a read fault exception,
            # exception type 8 ... is flagged for ENTER.  The exception is
            # processed after any stack flushing is completed."  SP and
            # MSP are left as they were (the flushed blocks are also still
            # in the cache), so the ENTER restarts: 1e's trap.c maps the
            # stack page ("CATCH/ENTER will generate a read fault when
            # checking the new SP/MSP values") and returns to it.
            checks = [new_sp & MASK32]
            if (new_msp & MASK32) != pre_msp:
                checks.append(new_msp & MASK32)
            for va in checks:
                try:
                    _translate(state, va & ~3, "write")
                except MemoryFault as fault:
                    raise MemoryFault(
                        "read fault: ENTER's check of 0x%08x (p. 3-21): %s"
                        % (va, fault.reason), EXC_READ, va)

        state.pc = next_pc & ~1
        state.sp = new_sp & MASK32
        state.msp = new_msp & MASK32
        state.psw = new_psw & MASK32
        state.isp = new_isp & MASK32
        if sysm is not None:
            sysm.kernel_level = False
            _system_retire(state, mnemonic, reg_store, pre_sp, pre_isp,
                           pre_psw, cyc, folded)
        record = Record(
            pc=pc, insn0=insn0, insn1=insn1,
            sp_before=pre_sp, sp_after=state.sp,
            msp_before=pre_msp, msp_after=state.msp,
            mem_we=mem_we, mem_addr=mem_addr,
            mem_wdata=mem_wdata, mem_wmask=mem_wmask,
            trap=0, cyc=cyc,
        )
        # The record just produced becomes the previous instruction for
        # folding, and its index is this instruction's compare distance base.
        timing = state.timing
        timing.prev_foldable = _foldable_target(length, parcels[0])
        if mnemonic in ("CMPEQ", "CMPGT", "CMPHI"):
            timing.last_compare = timing.retired
            timing.last_flag_source = "compare"
        elif mnemonic in ("TESTC", "TESTV"):
            timing.last_flag_source = "other"
        timing.retired += 1
        return record, state

    except Trap as exc:
        state.cpu_prefix = False
        if state.system is not None:
            return _system_trap(state, exc, pre_pc, pre_sp, pre_msp,
                                insn0, insn1), state
        # The unimplemented-instruction sequence (p. 1-39): the opcode's
        # own PC is stored at *(CSP) and the part then vectors through
        # *(VB+12).  The one-instruction model reports that one store as
        # the instruction's one architectural write and stops; the
        # handler fetch is out of scope (adjudication convention C2).
        trap_addr = pre_sp & ~3
        trap_data = pre_pc
        trap_mask = 0xF
        try:
            word_addr, new_word, trap_data, trap_mask = _prepare_store(
                state, memory_reader,
                Operand(4, True, ea=pre_sp), pre_pc)
            _store_word(state, word_addr, new_word)
            trap_addr = word_addr
        except Refusal:
            # The state cannot represent the save (for example an
            # unaligned SP); still report the fixed word write.
            pass
        record = Record(
            pc=pre_pc, insn0=insn0, insn1=insn1,
            sp_before=pre_sp, sp_after=pre_sp,
            msp_before=pre_msp, msp_after=pre_msp,
            mem_we=1, mem_addr=trap_addr,
            mem_wdata=trap_data, mem_wmask=trap_mask,
            trap=1, cyc=_fixed_cycles("Unimplemented opcode"),
            reason=exc.reason,
        )
        return record, state

    except Refusal as exc:
        # A fetch fault, an illegal encoding, an alignment fault, a state
        # limitation, or a legal instruction outside this model's subset.
        # C2: this is a refusal outside the HRI comparison, not trap=1.
        state.cpu_prefix = False
        if state.system is not None:
            state.system.kernel_level = False
        if not exc.parcels and insn0:
            exc.parcels = [insn0, insn1]
        if state.system is not None:
            ident = _exception_ident(exc)
            if ident is not None:
                return _system_exception(state, exc, ident, pre_pc, pre_sp,
                                         pre_msp, insn0, insn1), state
        raise


# ---------------------------------------------------------------------------
# The privileged machine's retirement and event sequences (System only)
# ---------------------------------------------------------------------------

def _system_retire(state: State, mnemonic: str,
                   reg_store: Optional[Tuple[Operand, int]],
                   pre_sp: int, pre_isp: int, pre_psw: int,
                   cyc: int, folded: bool) -> None:
    """What a retiring instruction does to the System's state.

    * A CPU-prefixed destination register is written last (p. 3-14).
    * SHAD: CRET and KRET set it to the new CSP, KCALL to the new ISP
      (pp. 3-15, 3-29, 3-30); otherwise it follows a change of the pointer
      that was the CSP when the instruction began (p. 1-16, "any time the
      CSP is modified").
    * CRET's CATCH portion fills [SP, MSP) "consistently with the restored
      PSW current stack pointer and virtual/physical addressing mode bits"
      (p. 3-15): under the new PSW, and only when the new CSP is SP (with
      CSP = ISP, CATCH is a no-op, p. 3-10).
    * The timers count (Table 1-2, p. 1-9; Tables 1-12, 1-13 p. 1-19).
    """
    sysm = state.system
    if reg_store is not None:
        _write_control(state, reg_store[0].reg, reg_store[1])
    if mnemonic in ("CRET", "KRET"):
        sysm.shad = state.isp if not (state.psw & PSW_SP) else state.sp
    elif mnemonic == "KCALL":
        sysm.shad = state.isp
    elif pre_psw & PSW_SP:
        if state.sp != pre_sp:
            sysm.shad = state.sp
    elif state.isp != pre_isp:
        sysm.shad = state.isp
    if mnemonic == "CRET" and state.psw & PSW_SP and state.msp > state.sp:
        _cret_catch(state)
    _count_timers(state, cyc, 0 if folded else 1)


def _cret_catch(state: State) -> None:
    """CRET's CATCH portion (p. 3-15), after SP, PC and PSW are restored.

    "The target MSP is fetched prior to the CATCH portion executing, but
    the MSP is not updated until the CATCH portion completes"; the
    portion runs "consistently with the restored PSW", and a CATCH whose
    stores are not valid flags a read fault, exception 8 (p. 3-11).  So
    the fill proceeds block by block upward from SP (the cache having
    been discarded) and, if a block faults, the exception sequence
    (p. 1-38) is taken there with the *restored* PC and PSW, MSP at the
    blocks already filled, and SHAD = the restored SP -- the event's
    ``SP = SHAD`` must not undo the new SP.  The order inside CRET is not
    printed beyond that; this is the reading 1e's trap.c relies on
    ("CATCH/ENTER will generate a read fault when checking the new
    SP/MSP values", handled as a user stack fault)."""
    sysm = state.system
    target = state.msp
    lo = state.sp
    try:
        for base in range(lo, target, 16):
            cache_fill(state, None, base, base + 16)
            state.msp = base + 16
    except MemoryFault as exc:
        state.msp = base
        sysm.shad = state.sp
        sysm.fault = exc.va & ~3
        _event_sequence(state, [(-12, EXC_READ), (-8, state.pc),
                                (-4, state.psw)], 4)
        sysm.events.append(("exception", EXC_READ, state.pc))
        return
    state.msp = target


def _count_timers(state: State, cycles: int, instructions: int) -> None:
    """Advance TIMER1/TIMER2 by one retirement (Table 1-2, p. 1-9).

    TIMER1: bit 22 selects instructions (1) or clock cycles (0); bit 23
    restricts counting to kernel level ("If 1, the timer only increments
    in kernel mode (PSW execution level bit is 0)" -- the kernel's
    machine.h comments T1X "counts only in user mode"; the printed PRM is
    followed).  TIMER2: bits 29:25 = 0 cycles, 1 instructions, 0x1F off;
    the other codes are not printed and leave the timer stopped here.
    Bit 30 is TIMER2's kernel-only bit.  An overflow from 0xFFFFFFFF to 0
    with the enable bit (24, 31) set leaves a level-one interrupt pending.
    Cycles are the record's Chapter 4 ``cyc``.
    """
    sysm = state.system
    cfg = sysm.config
    kernel = not (state.psw & PSW_USER)
    if kernel or not (cfg & CONFIG_T1X):
        n = instructions if cfg & CONFIG_T1CI else cycles
        if n:
            total = sysm.timer1 + n
            if total > MASK32 and cfg & CONFIG_T1IE:
                sysm.timer1_pending = True
            sysm.timer1 = total & MASK32
    sel = (cfg >> 25) & 0x1F
    if sel in (0, 1) and (kernel or not (cfg & CONFIG_T2X)):
        n = instructions if sel == 1 else cycles
        if n:
            total = sysm.timer2 + n
            if total > MASK32 and cfg & CONFIG_T2IE:
                sysm.timer2_pending = True
            sysm.timer2 = total & MASK32


def _vector_word(state: State,
                 reader: Optional[Callable[[int], Optional[int]]],
                 addr: int) -> int:
    """A read of the vector table (KCALL p. 3-29, the event sequences).

    With a ``System`` it is made at kernel level whatever the PSW says:
    the table "should always be available" (p. 1-20) and a fault reading
    it resets the part (pp. 1-35, 3-29), so it is not subject to the
    user-level check.  1e's trap.c depends on this: an unimplemented
    instruction at user level reads the vector and then takes a *fetch*
    fault at the kernel handler's address (its "_vector2/_vector3"
    case), which is possible only if the vector read itself succeeded."""
    sysm = state.system
    if sysm is None:
        return _read_word(state, reader, addr)
    saved = sysm.kernel_level
    sysm.kernel_level = True
    try:
        return _read_word(state, reader, addr)
    finally:
        sysm.kernel_level = saved


def _event_word(state: State, addr: int) -> int:
    """A read during an event sequence; a fault there resets the part
    (p. 1-35), which this model reports instead of performing."""
    try:
        return _vector_word(state, None, addr)
    except MemoryFault as exc:
        raise Unsupported("reset: memory fault on 0x%08x during event "
                          "processing (p. 1-35): %s" % (addr, exc.reason))


def _event_push(state: State, words: List[Tuple[int, int]]) -> None:
    sysm = state.system
    for off, value in words:
        addr = (state.isp + off) & MASK32
        try:
            word_addr, new_word, _, mask = _prepare_store(
                state, None, Operand(4, True, ea=addr), value)
            _store_word(state, word_addr, new_word, mask)
        except MemoryFault as exc:
            raise Unsupported("reset: memory fault on the interrupt stack "
                              "at 0x%08x (p. 1-35): %s" % (addr, exc.reason))
    del sysm


def _event_sequence(state: State, frame: List[Tuple[int, int]],
                    vector: int) -> None:
    """The common part of pp. 1-37 and 1-38:

        if (CSP = ISP) ISP = SHAD else SP = SHAD
        *(ISP-12) = exception identifier    (exceptions only)
        *(ISP-8) = PC ; *(ISP-4) = PSW
        ISP -= 16 ; SHAD = ISP
        PC = *(VB + vector) ; PSW &= 0xFFFF0000

    The frame's values are taken before anything changes; the stores and
    the vector read are made at kernel level (PSW bits 15:0 already
    cleared): the sequence's own accesses cannot depend on the level it
    is leaving.  The PRM does not say this in words; a fault on them
    resets the part (p. 1-35), which the model reports.
    """
    sysm = state.system
    if not (state.psw & PSW_SP):
        state.isp = sysm.shad & ~0xF
    else:
        state.sp = sysm.shad & ~0xF
    state.psw &= 0xFFFF0000
    _event_push(state, frame)
    state.isp = (state.isp - 16) & MASK32
    sysm.shad = state.isp
    new_pc = _event_word(state, (state.vb + vector) & MASK32)
    state.pc = new_pc & ~1


def _system_exception(state: State, exc: Refusal, ident: int, pre_pc: int,
                      pre_sp: int, pre_msp: int, insn0: int,
                      insn1: int) -> Record:
    """The exception sequence (p. 1-38) for Table 1-26's identifiers.

    The PC saved is the instruction's own (for a fetch fault, the target
    that could not be fetched: the model faults when it fetches there,
    so ``pre_pc`` is that target, as p. 1-34 requires).  FAULT gets the
    word-aligned virtual address for identifiers 8 and 9 (p. 1-39).

    The record costs Table 4-36's Exception row, ``9 + D + A`` (p. 4-5).
    It was 0 until 2026-11-24; the timing twin (``hobbit_timing.py``)
    found the difference on the s9term boot's first 3,000,000 records
    (7 exceptions).  An interrupt has no record of its own and stays
    uncharged (Table 4-36 prints no interrupt row)."""
    sysm = state.system
    if ident in (EXC_READ, EXC_WRITE) and isinstance(exc, MemoryFault):
        sysm.fault = exc.va & ~3
    psw = state.psw
    _event_sequence(state, [(-12, ident), (-8, pre_pc), (-4, psw)], 4)
    sysm.events.append(("exception", ident, pre_pc))
    return Record(pc=pre_pc, insn0=insn0, insn1=insn1,
                  sp_before=pre_sp, sp_after=state.sp,
                  msp_before=pre_msp, msp_after=state.msp,
                  mem_we=0, mem_addr=0, mem_wdata=0, mem_wmask=0,
                  trap=1, cyc=9 + D_CYC + A_CYC,
                  reason="exception 0x%x: %s" % (ident, exc.reason))


def _system_trap(state: State, exc: Trap, pre_pc: int, pre_sp: int,
                 pre_msp: int, insn0: int, insn1: int) -> Record:
    """The unimplemented-instruction sequence (p. 1-39), or the trapped
    niladic one (p. 1-40), completed:

        *(CSP) = PC of unimplemented opcode
        PC = *(VB + 12)        (VB + 8 for a trapped niladic)

    PSW, ISP and SP are not changed."""
    sysm = state.system
    csp = state.csp
    word_addr, new_word, data, mask = _prepare_store(
        state, None, Operand(4, True, ea=csp), pre_pc)
    _store_word(state, word_addr, new_word, mask)
    vector = 8 if isinstance(exc, TrappedNiladic) else 12
    state.pc = _event_word(state, (state.vb + vector) & MASK32) & ~1
    sysm.events.append(("niladic" if vector == 8 else "unimplemented",
                        vector, pre_pc))
    return Record(pc=pre_pc, insn0=insn0, insn1=insn1,
                  sp_before=pre_sp, sp_after=pre_sp,
                  msp_before=pre_msp, msp_after=pre_msp,
                  mem_we=1, mem_addr=word_addr, mem_wdata=data,
                  mem_wmask=mask, trap=1,
                  cyc=_fixed_cycles("Unimplemented opcode"),
                  reason=exc.reason)


def interrupt_accepted(state: State, level: int) -> bool:
    """Is an interrupt at ``level`` (0..6, Table 1-25) accepted now?

    "Interrupts are accepted when the requesting device level (IL[2:0])
    is less than interrupt priority level or equal to 0" (Table 1-8,
    p. 1-15).  NMI's edge sensitivity (p. 1-37) is the caller's."""
    ipl = (state.psw >> PSW_IPL_SHIFT) & 7
    return level == 0 or level < ipl


def take_interrupt(state: State, level: int,
                   vector: Optional[int] = None) -> None:
    """The interrupt sequence (p. 1-37), between two instructions.

    ``vector`` defaults to VB + 16 + 4 x level; the timers use VB + 44
    and VB + 48 (Table 1-14, p. 1-20).  The PC saved is the instruction
    that has not yet executed (``state.pc``)."""
    sysm = state.system
    if vector is None:
        vector = 16 + 4 * level
    pc = state.pc & ~1
    _event_sequence(state, [(-8, pc), (-4, state.psw)], vector)
    sysm.events.append(("interrupt", vector, pc))


# ---------------------------------------------------------------------------
# Image loading and CLI
# ---------------------------------------------------------------------------

class ImageReader:
    """Sparse image: word address -> 32-bit word; absent addresses return None."""

    def __init__(self, words: Dict[int, int]):
        self.words = words

    def __call__(self, address: int) -> Optional[int]:
        return self.words.get(address & ~3)


class WordBus:
    """The ``System.bus`` of the CLI's privileged mode (``--system``):
    physical memory as a sparse dict of words (the image at 0, the
    ``--poke`` words), unwritten words reading 0, and no devices."""

    def __init__(self, words: Dict[int, int]):
        self.words = dict(words)

    def read(self, pa: int) -> int:
        return self.words.get(pa & ~3 & MASK32, 0)

    def write(self, pa: int, data: int, mask: int) -> None:
        w = pa & ~3 & MASK32
        expanded = 0
        for bit in range(4):
            if mask & (1 << bit):
                expanded |= 0xFF << (8 * bit)
        old = self.words.get(w, 0)
        self.words[w] = (old & ~expanded & MASK32) | (data & expanded)


def load_image(path: str) -> Dict[int, int]:
    """Load the fixed one-word-per-line image format.

    Blank lines and text from a first ``#`` are ignored so that
    ``demo.s`` can carry the hand-encoded listing beside each word.
    """
    words: Dict[int, int] = {}
    with open(path, "r", encoding="utf-8") as handle:
        for lineno, raw in enumerate(handle, 1):
            line = raw.split("#", 1)[0].strip()
            if not line:
                continue
            token = line.split()[0]
            if len(token) != 8:
                raise ValueError(
                    "%s:%d: expected one 8-hex-digit word, got %r"
                    % (path, lineno, token))
            try:
                value = int(token, 16)
            except ValueError:
                raise ValueError(
                    "%s:%d: %r is not a hex word" % (path, lineno, token))
            words[len(words) * 4] = value & MASK32
    return words


def _parse_hex(text: str) -> int:
    return int(text, 16) & MASK32


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Independent one-instruction ATT92010 Hobbit model.")
    parser.add_argument("--image", required=True,
                        help="text image: one 8-hex-digit 32-bit word per line")
    parser.add_argument("--sp", required=True, help="initial SP (hex)")
    parser.add_argument("--msp", required=True, help="initial MSP (hex)")
    parser.add_argument("--isp", default="0x40",
                        help="initial ISP (hex; default 0x40)")
    parser.add_argument("--vb", default="0x0",
                        help="initial VB (hex; default 0x0)")
    parser.add_argument("--psw", default="0x200",
                        help="initial PSW (hex; default 0x200, CSP = SP; "
                             "0x8600 adds user level and user "
                             "little-endian data, p. 1-3)")
    parser.add_argument("--system", action="store_true",
                        help="the privileged machine (System): the "
                             "exception sequences, the MMU walk when the "
                             "PSW's V bit is set, physical memory = the "
                             "image plus --poke words (the goldens' "
                             "privileged harness, tests/golden/README.md)")
    parser.add_argument("--stb", default="0x0",
                        help="with --system: the segment table base (hex)")
    parser.add_argument("--poke", action="append", default=[],
                        metavar="ADDR=WORD",
                        help="with --system: a physical word (hex), e.g. "
                             "a segment- or page-table entry; repeatable")
    parser.add_argument("--max-steps", type=int, default=10000,
                        help="maximum instructions to execute (default 10000)")
    parser.add_argument("--stop-at-image-end",
                        action=argparse.BooleanOptionalAction,
                        default=True,
                        help="stop when the next PC equals the image length "
                             "in bytes, without executing past the end "
                             "(default: on)")
    parser.add_argument("--part", default="92010",
                        help="the part modelled: 92010 (default) or 92020S "
                             "(docs/att92020.md); 92020M/MX are refused")
    parser.add_argument("--borrow-92010-timing", action="store_true",
                        help="92020S only: price cyc from the 92010's "
                             "Chapter 4 tables (no 92020 timing is "
                             "published); without it a 92020S run is "
                             "refused at its first step")
    args = parser.parse_args(argv)

    try:
        part_info(args.part)
    except ValueError as exc:
        parser.error(str(exc))
    if args.max_steps < 0:
        parser.error("--max-steps must be non-negative")

    try:
        sp = _parse_hex(args.sp)
        msp = _parse_hex(args.msp)
        isp = _parse_hex(args.isp)
        vb = _parse_hex(args.vb)
        psw = _parse_hex(args.psw)
    except ValueError:
        parser.error("--sp, --msp, --isp, --vb and --psw must be "
                     "hexadecimal numbers")

    if sp & 0xF or msp & 0xF or isp & 0xF or vb & 0xF:
        parser.error("--sp, --msp, --isp and --vb must be quad-word "
                     "(16-byte) aligned")

    try:
        image = load_image(args.image)
    except (OSError, ValueError) as exc:
        print("hobbit_sem: %s" % exc, file=sys.stderr)
        return 2

    reader = ImageReader(image)
    state = State(pc=0, sp=sp, msp=msp, psw=psw, isp=isp, vb=vb,
                  part=args.part,
                  borrow_92010_timing=args.borrow_92010_timing)
    if args.part != "92010" and args.borrow_92010_timing:
        print("hobbit_sem: part %s, cyc priced from the 92010's Chapter 4 "
              "tables (no 92020 timing is published)" % args.part,
              file=sys.stderr)
    if args.poke and not args.system:
        parser.error("--poke needs --system")
    if args.system:
        words = dict(image)
        try:
            for item in args.poke:
                a, sep, v = item.partition("=")
                if not sep:
                    raise ValueError(item)
                words[_parse_hex(a) & ~3] = _parse_hex(v)
            stb = _parse_hex(args.stb)
        except ValueError:
            parser.error("--poke wants ADDR=WORD in hex; --stb hex")
        # SHAD = SP, the goldens' pre-state (tests/golden/README.md; p. 1-15
        # requires it after a direct write of PSW bit 9).
        state.system = System(bus=WordBus(words), stb=stb, shad=sp)
    image_len = len(image) * 4

    for _ in range(args.max_steps):
        # C1: no instruction's last parcel lies at or beyond the image
        # end, so stop before fetching the word at image_len.
        if args.stop_at_image_end and (state.pc & ~1) == image_len:
            break
        try:
            record, state = step(state, reader)
        except Refusal as exc:
            # C2: a fetch fault, an illegal encoding, an alignment fault,
            # a state limitation, or a legal instruction outside the
            # subset is a refusal outside the HRI comparison, not trap=1.
            p0 = exc.parcels[0] if exc.parcels else 0
            p1 = exc.parcels[1] if len(exc.parcels) > 1 else 0
            print("REFUSED pc=%04x insn=%04x%04x reason: %s"
                  % ((state.pc & ~1), p0, p1, exc.reason),
                  file=sys.stderr)
            return 0
        print(record.line())
        if record.trap:
            print(record.reason, file=sys.stderr)
            # The privileged machine performs the sequence and goes on at
            # the vector; the stop rules are then the image end and
            # --max-steps (tests/golden/README.md, the privileged harness).
            if not args.system:
                return 0
    else:
        print("hobbit_sem: stopped after %d steps without a trap"
              % args.max_steps, file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
