#!/usr/bin/env python3
"""hobbit_timing.py -- the timing twin: base `cyc` per HRI record.

An independent timing model of the ATT92010, fed by a retirement stream
(HRI lines), the memory image the stream ran from, and a board-and-policy
file (`hobbit_timing_board.txt`).  It is milestone C2 of
`docs/cycle_accuracy_plan.md` (§3.1): **base times only**, under the
four assumptions of PRM p. 4-1, so it charges no Table 4-37..4-40 delay
and no Table 2-4 translation; it gives each record the cycle count of
the printed row that prices it and names the row.

Independence (the plan's contract).  This file imports nothing from
`sem/hobbit_sem.py`, `bsv/`, `asm/`, `tools/cyc_classify.py` or
`tools/p9trace_cmp.py`.  Its opcode tables are transcribed again from
the page images of PRM Tables 1-15..1-20 (printed pp. 1-22..1-25), its
cycle cells are read from `docs/timing.csv` (the Chapter 4 transcription,
validated by `tools/check_timing.py`) and evaluated here, and its
folding and compare-distance rules are written from p. 4-7, Table 4-35
(p. 4-5) and the data sheet (DS pp. 26, 27, 32-33).  The one import is
`tools/p9exec.py`, a reader of the 1e executable format, used only to
map a program's text.

What the twin keeps, and how it differs from a one-instruction model:

* **Folding by the static rule.**  A one-parcel JMP or conditional jump
  is folded when the record before it is the instruction *physically*
  before it (its pc plus its length is the jump's pc), retired (not a
  trap record), and a p. 4-7 host: a one-parcel instruction with a
  five-bit opcode outside 0x00..0x07, or a three-parcel instruction that
  is not monadic, and in either case a "non-branching operation" (p. 4-7
  first paragraph; so KRET and CRET, which transfer control, are not
  hosts).  A five-parcel instruction is never a host (p. 4-7: "a previous
  one- or three-parcel instruction"; DS p. 26 likewise), and a
  three-parcel jump never folds (DS p. 27: "all jumps must be encoded as
  three-parcel and, hence, will not be folded").  A jump reached by a
  transfer -- a taken branch, a KRET, an interrupt, the return from a
  trap -- is not folded: the decoded entry that carries the fold is the
  host's, and the transfer did not go through the host.
* **Compare distance by retirement.**  Table 4-35 indexes a mispredicted
  jump by how many instructions after its compare it is.  The twin counts
  retired records (trap records do not retire); the board's `distance =
  slots` leaves folded branches out of the count instead.
* **The flag's provenance.**  Table 4-35 prices a misprediction only by
  the distance from a *compare*.  PSW.F is also written by TESTC/TESTV
  (pp. 3-44, 3-46), TADD/TSUB (pp. 3-42, 3-47), KRET/CRET (the restored
  PSW) and a CPU-prefixed write of PSW, and it is unknown after a trap
  record whose handler the stream does not show.  A misprediction whose
  flag came from any of those is **undetermined**: no printed row prices
  it, and the twin says so rather than choosing one.
* **Whether a jump was taken** is read from the next record's pc (or the
  `I` line of a kernel boot's replay record, when an interrupt came
  between them).  The last record's jump is undetermined.

Usage:

    python3 sem/hobbit_timing.py TRACE [--hex IMAGE | --aout EXE |
        --boot-rec FILE] [--board FILE] [--compare] [--per-record]
        [--examples N] [--limit N]

`--compare` checks the twin's `cyc` against the trace's own `cyc` field
(the reference model's for a `p9run.py`/`p9coreboot.py` trace, the
hand-derived one for a golden `.trace`) and prints every disagreement,
grouped, with the twin's row.  Exit 0 when every determined record
agrees, 1 otherwise.  `--per-record` prints one line per record: index,
pc, mnemonic, the twin's `cyc` (or `-`), the trace's, and the row.
"""

import argparse
import csv
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
HOBBIT = os.path.dirname(HERE)
TIMING_CSV = os.path.join(HOBBIT, "docs", "timing.csv")
BOARD = os.path.join(HERE, "hobbit_timing_board.txt")

LINE = re.compile(
    r"^HRI pc=([0-9a-f]+) insn=([0-9a-f]+) sp=([0-9a-f]+)>([0-9a-f]+) "
    r"msp=([0-9a-f]+)>([0-9a-f]+) we=(\d) addr=([0-9a-f]+) "
    r"data=([0-9a-f]+) mask=([0-9a-f]+) trap=(\d) cyc=(\d+)")

# ---------------------------------------------------------------------------
# Opcode tables, from the page images
# ---------------------------------------------------------------------------

# Table 1-15 (p. 1-22), one-parcel opcode[4:0].  "stack" is Table 1-16,
# "niladic" Table 1-17; None is "unimp*".
ONE = {
    0x00: "KCALL", 0x01: "CALL", 0x02: "stack", 0x03: "JMP",
    0x04: "JMPFN", 0x05: "JMPFY", 0x06: "JMPTN", 0x07: "JMPTY",
    0x08: None, 0x09: None, 0x0A: "MOV", 0x0B: "niladic",
    0x0C: None, 0x0D: "ADD3", 0x0E: "AND3", 0x0F: "AND",
    0x10: "CMPEQ", 0x11: "CMPGT", 0x12: "CMPGT", 0x13: "CMPEQ",
    0x14: "ADD", 0x15: "ADD3", 0x16: "ADD", 0x17: "ADD3",
    0x18: "MOV", 0x19: "MOV", 0x1A: "MOV", 0x1B: "MOV",
    0x1C: "MOV", 0x1D: "MOVA", 0x1E: "SHL3", 0x1F: "SHR3",
}
STACK = {0: "ENTER", 1: "CATCH", 2: "RETURN", 3: "POPN"}      # Table 1-16
# Table 1-17, subcode[9:0]; 0x006 FLUSHD is printed "FLUSHD*" (the
# unimplemented sequence, p. 3-22); subcodes >= 0x200 are "trap".
NILADIC = {0x000: "CPU", 0x001: "KRET", 0x002: "NOP", 0x003: "FLUSHI",
           0x004: "FLUSHP", 0x005: "CRET", 0x006: "FLUSHD",
           0x008: "TESTV", 0x009: "TESTC", 0x00A: "CLRE"}
# Table 1-19 (p. 1-24), monadic subcode; 0xD is "FLUSHDCE*", 0xE "unimp*".
MONADIC = {0x0: "KCALL", 0x1: "CALL", 0x2: "RETURN", 0x3: "JMP",
           0x4: "JMPFN", 0x5: "JMPFY", 0x6: "JMPTN", 0x7: "JMPTY",
           0x8: "CATCH", 0x9: "ENTER", 0xA: "LDRAA", 0xB: "FLUSHPTE",
           0xC: "FLUSHPBE", 0xD: "FLUSHDCE", 0xE: None, 0xF: "POPN"}
# Tables 1-18 (p. 1-24) and 1-20 (p. 1-25), opcode[5:3] rows x [2:0].
_GRID = [
    ["monadic", "ORI", "ANDI", "ADDI", "MOVA", "UREM", "MOV", "DQM"],
    [None, None, None, None, "TADD", "TSUB", None, None],
    [None] * 8,
    [None, None, None, None, None, "CMPGT", "CMPHI", "CMPEQ"],
    ["SUB", "OR", "AND", "ADD", "XOR", "REM", "MUL", "DIV"],
    [None, None, None, None, "SHR", "USHR", "SHL", "UDIV"],
    ["SUB3", "OR3", "AND3", "ADD3", "XOR3", "REM3", "MUL3", "DIV3"],
    [None, None, None, None, "SHR3", "USHR3", "SHL3", None],
]
DYADIC = {(r << 3) | c: _GRID[r][c] for r in range(8) for c in range(8)}

CONDITIONAL = {"JMPFN": False, "JMPFY": True, "JMPTN": False, "JMPTY": True}
COMPARES = {"CMPEQ", "CMPGT", "CMPHI"}
FLAG_WRITERS = {"TESTC": "TESTC", "TESTV": "TESTV", "TADD": "TADD",
                "TSUB": "TSUB", "KRET": "KRET", "CRET": "CRET"}
# p. 4-7's first paragraph folds a branch into a "non-branching
# operation": these one-parcel instructions with opcode >= 0x08 transfer
# control and are not hosts.
BRANCHING_NILADIC = {"KRET", "CRET"}
UNIMPLEMENTED = {"FLUSHD", "FLUSHDCE"}       # pp. 3-22, 3-23


def plen(p0):
    """Parcel count from the first parcel's top bits (pp. 1-21, 1-23, 1-24)."""
    if not p0 & 0x8000:
        return 1
    return 3 if (p0 & 0xC000) == 0x8000 else 5


class Insn:
    """What the twin needs to know about one record's instruction."""

    __slots__ = ("name", "length", "cpu", "parcels", "host_ok", "smode",
                 "dmode")

    def __init__(self):
        self.name = None
        self.length = 1
        self.cpu = False
        self.parcels = []
        self.host_ok = False
        self.smode = self.dmode = None


def decode(pc, insn, parcel_at):
    """Decode the instruction a record retired.

    The record carries the first two parcels; the rest come from
    ``parcel_at`` (None where the image does not hold them)."""
    d = Insn()
    p0, p1 = insn >> 16, insn & 0xFFFF
    if p0 == 0x2C00:                          # CPU, Table 1-17 subcode 0
        d.cpu = True
        inner = decode(pc + 2, (p1 << 16) | (parcel_at(pc + 4) or 0),
                       parcel_at)
        inner.cpu = True
        inner.length += 1
        return inner
    n = plen(p0)
    d.length = n
    d.parcels = [p0, p1] + [parcel_at(pc + 2 * k) for k in range(2, n)]
    if n == 1:
        op = (p0 >> 10) & 0x1F
        name = ONE[op]
        if name == "stack":
            name = STACK[p0 & 3]
            if name == "ENTER":
                d.smode = 0xD                 # stk8 is a stack offset
        elif name == "niladic":
            sub = p0 & 0x3FF
            name = "trapped niladic" if sub >= 0x200 else NILADIC.get(sub)
        d.name = name
        d.host_ok = (op >= 0x08 and name is not None
                     and name not in BRANCHING_NILADIC
                     and name not in UNIMPLEMENTED
                     and name != "trapped niladic")
        return d
    op = (p0 >> 8) & 0x3F
    d.smode, d.dmode = (p0 >> 4) & 0xF, p0 & 0xF
    if n == 3 and op == 0:
        d.name = MONADIC[p0 & 0xF]
        d.host_ok = False                     # p. 4-7, third exception
        return d
    d.name = None if (n == 5 and op == 0) else DYADIC[op]
    d.host_ok = (n == 3 and d.name is not None)
    return d


# ---------------------------------------------------------------------------
# The printed cells (docs/timing.csv) and the board
# ---------------------------------------------------------------------------

def read_board(path):
    board = {}
    with open(path) as fh:
        for raw in fh:
            line = raw.split("#", 1)[0].strip()
            if not line:
                continue
            key, _, value = line.partition("=")
            board[key.strip()] = value.strip()
    for sym in ("A", "D", "Q", "S", "MUL"):
        board[sym] = int(board[sym])
    return board


def evaluate(cell, board, E=0):
    """Evaluate a printed cycle cell: `5 + 2D`, `1 + (Q·E)`, `8·S`."""
    expr = cell.replace("·", "*")
    expr = re.sub(r"(\d)\s*([A-Z(])", r"\1*\2", expr)
    env = {"A": board["A"], "D": board["D"], "Q": board["Q"],
           "S": board["S"], "E": E}
    if not re.fullmatch(r"[0-9A-Z+*() ]+", expr):
        raise ValueError("cell %r" % cell)
    return int(eval(expr, {"__builtins__": {}}, env))   # noqa: S307


class Rows:
    """timing.csv, keyed for lookup: per spelling, per DQM form, per
    Table 4-35 condition and per Table 4-36 instruction."""

    def __init__(self, path, board):
        self.board = board
        self.by_op = {}
        self.by_variant = {}
        with open(path, newline="", encoding="utf-8") as fh:
            for row in csv.DictReader(fh):
                if row["op"] and row["kind"] in ("instruction", "misc"):
                    self.by_op[row["op"]] = row
                for s in filter(None, row["covers"].split(";")):
                    self.by_op.setdefault(s.strip(), row)
                if row["variant"]:
                    self.by_variant[row["variant"]] = row

    def fixed(self, name):
        """(cycles, row id) of a Table 4-32/4-33/4-36 row."""
        row = self.by_op[name]
        if row["kind"] == "instruction":
            lo, hi = int(row["min"]), int(row["max"])
            if lo != hi:
                if name in ("MUL", "MUL3"):
                    return self.board["MUL"], row["id"] + " (board MUL)"
                raise KeyError("%s has a range and no reading" % name)
            return lo, row["id"]
        return evaluate(row["time"], self.board), row["id"]

    def variant(self, text, E=0):
        row = self.by_variant[text]
        return evaluate(row["time"], self.board, E), row["id"]


# ---------------------------------------------------------------------------
# Inputs
# ---------------------------------------------------------------------------

def read_trace(path, limit=None):
    out = []
    with open(path, errors="replace") as fh:
        for raw in fh:
            m = LINE.match(raw)
            if m:
                g = m.groups()
                out.append(tuple(int(x, 16) for x in g[:11]) + (int(g[11]),))
                if limit and len(out) >= limit:
                    break
    return out


class Memory:
    """The image the stream ran from, plus the stream's own writes (so a
    pointer a DQM reads can be known); a word nobody wrote or loaded is
    unknown (None)."""

    def __init__(self):
        self.words = {}

    def load_hex(self, path):
        with open(path) as fh:
            for k, line in enumerate(l for l in fh if l.strip()):
                self.words[4 * k] = int(line.strip(), 16)

    def load_aout(self, path):
        sys.path.insert(0, os.path.join(HOBBIT, "tools"))
        import p9exec  # noqa: E402  (the 1e executable reader only)
        exe = p9exec.read(path)
        n = exe["text"] // 4
        for k, w in enumerate(p9exec._words(exe, exe["text_off"], n)):
            self.words[p9exec.TEXTBASE + 4 * k] = w

    def load_boot_rec(self, path):
        """`M addr word` lines; returns {record index: next pc} from the
        `I n level pc` lines.  n counts the records retired before the
        interrupt (p9coreboot.py writes its running count), so the
        interrupted record is index n - 1: on the s9term boot, `I 2b78cc`
        follows the record at line 2,848,972, pc 0x800041e4, whose
        successor 0x800041ec is the line's pc."""
        after = {}
        with open(path) as fh:
            for line in fh:
                f = line.split()
                if f and f[0] == "M":
                    self.words[int(f[1], 16)] = int(f[2], 16)
                elif f and f[0] == "I":
                    after[int(f[1], 16) - 1] = int(f[3], 16)
        return after

    def parcel(self, addr):
        w = self.words.get(addr & ~3)
        if w is None:
            return None
        return (w & 0xFFFF) if addr & 2 else (w >> 16)

    def word(self, addr):
        return self.words.get(addr & ~3)

    def write(self, addr, data, mask):
        if mask == 0xF:
            self.words[addr & ~3] = data
            return
        old = self.words.get(addr & ~3)
        if old is None:
            self.words.pop(addr & ~3, None)
            return
        keep = 0
        for b in range(4):
            if mask >> b & 1:
                keep |= 0xFF << (8 * b)
        self.words[addr & ~3] = (old & ~keep) | (data & keep)


# ---------------------------------------------------------------------------
# The twin
# ---------------------------------------------------------------------------

def _sx(v, bits):
    v &= (1 << bits) - 1
    return v - (1 << bits) if v >> (bits - 1) else v


class Twin:
    def __init__(self, rows, board, mem, after=None):
        self.rows = rows
        self.board = board
        self.mem = mem
        self.after = after or {}
        self.retired = 0          # records counted for Table 4-35
        self.cmp_at = None        # self.retired value of the last compare
        self.flag = "reset"       # what last wrote PSW.F

    # -- rules -------------------------------------------------------------
    def enter_blocks(self, rec, d):
        """E of Table 4-36's 1 + (Q·E): the 16-byte iterations of the
        p. 3-19 flush loop, read from the record's SP/MSP.  With SP and
        MSP both unchanged the CSP was the ISP and no data moved (p. 3-20,
        "If the SP is not the CSP, no data traffic ... is performed")."""
        spb, spa, mspb, mspa = rec[2], rec[3], rec[4], rec[5]
        if spb == spa and mspb == mspa:
            return 0
        if d.smode == 0xD:      # flush only as much as necessary
            low = max(mspa, spb)
        else:                   # flush unconditionally, down to SHAD = SP
            low = spb
        return max(0, math.ceil((mspb - low) / 16))

    def dqm(self, rec, d):
        """Table 4-34's form: double or quad by the destination mode,
        constant source, and SC or M by whether each address is in the
        stack cache's window [SP, MSP) (p. 1-5).  The destination is the
        record's write; the source address is formed from the source
        field (Table 1-21)."""
        quad = d.dmode in (0xC, 0xD, 0xE)
        size = "quad-word" if quad else "double-word"
        spb, mspb = rec[2], rec[4]

        def sc(a):
            return spb <= a < mspb
        if not rec[6]:
            return None, "DQM record without a write"
        dst_sc = sc(rec[7])
        if d.smode == 0xF:
            return self.rows.variant(
                "Constant to %s %s" % ("SC" if dst_sc else "M", size))
        n = d.length - (1 if d.cpu else 0)
        p = d.parcels
        if n == 3:
            field = p[1]
            val16 = _sx(field, 16)
        else:
            if p[1] is None or p[2] is None:
                return None, "DQM source field not in the image"
            val16 = _sx((p[1] << 16) | p[2], 32)
        csp = spb
        if d.smode == 0xD:
            src = (csp + val16) & 0xFFFFFFFF
        elif d.smode == 0xE:
            ptr = self.mem.word((csp + val16) & 0xFFFFFFFF)
            if ptr is None:
                return None, "DQM source pointer not known to the twin"
            src = ptr
        elif d.smode == 0xC and n == 5:
            src = val16 & 0xFFFFFFFF
        elif d.smode == 0xC:
            # p. 1-23: a 16-bit absolute field is extended by CONFIG's PC
            # extension bit -- bits 31:29 from the PC, 28:16 zero -- or,
            # with the bit 0, by zeros.
            src = d.parcels[1] & 0xFFFF
            if self.board.get("config_px") == "1":
                src |= rec[0] & 0xE0000000
        else:
            return None, "DQM source mode 0x%x not resolved" % d.smode
        src_sc = sc(src)
        if src_sc and dst_sc:
            form = "SC %s to SC %s" % (size, size)
        elif src_sc or dst_sc:
            form = "SC/M %s to M/SC %s" % (size, size)
            if quad and self.board.get("dqm_scm_qw") == "2100":
                return (4 + self.board["Q"],
                        "t434_scm_qw_msc_qw (2100 4 + Q)")
        else:
            form = "M %s to M %s" % (size, size)
        return self.rows.variant(form)

    def folded(self, recs, i, d):
        """p. 4-7 / DS pp. 26-27, applied to the static predecessor."""
        if d.length != 1 or d.cpu:
            return False
        if i == 0:
            return False
        prev = recs[i - 1]
        if prev[10] or (i - 1) in self.after:
            return False
        pd = self.decoded[i - 1]
        if prev[0] + 2 * pd.length != recs[i][0]:
            return False
        if pd.cpu:
            # the prefixed instruction's own encoding decides, if the
            # board lets a CPU-prefixed instruction be a host at all
            return (self.board.get("fold_into_cpu_prefixed") == "yes"
                    and pd.host_ok)
        return pd.host_ok

    def taken(self, recs, i, d):
        if i in self.after:
            nxt = self.after[i]
        elif i + 1 < len(recs):
            nxt = recs[i + 1][0]
        else:
            return None
        return nxt != (recs[i][0] + 2 * d.length) & 0xFFFFFFFF

    # -- one record ----------------------------------------------------------
    def price(self, recs, i):
        """(cycles or None, row or reason, mnemonic, folded)."""
        rec = recs[i]
        d = self.decoded[i]
        name = d.name
        if rec[10]:                                   # a trap record
            # The unimplemented and trapped-niladic sequences store the
            # PC at *(CSP) (pp. 1-39, 1-40), so their record has a write;
            # an exception's frame goes to the interrupt stack and its
            # record has none (docs/p9boot.md, "Exceptions as the
            # reference records them").
            if rec[6] and name == "trapped niladic":
                c, row = self.rows.fixed(self.board["trapped_niladic"])
                return c, row, name, False
            if rec[6]:
                c, row = self.rows.fixed("Unimplemented opcode")
                return c, row, name or "unimp", False
            c, row = self.rows.fixed("Exception")
            return c, row, name or "unimp", False
        if name is None:
            return None, "no opcode in Tables 1-15..1-20", "unimp", False
        fold = False
        if name in CONDITIONAL:
            fold = self.folded(recs, i, d)
            taken = self.taken(recs, i, d)
            if taken is None:
                return None, "direction unknown (last record)", name, fold
            if taken == CONDITIONAL[name]:
                key = ("Correct prediction, folded" if fold
                       else "Correct prediction, unfolded")
                c, row = self.rows.variant(key)
                return c, row, name, fold
            if self.flag != "compare" or self.cmp_at is None:
                return (None, "mispredicted; PSW.F from %s, not a compare "
                        "(Table 4-35 prints no row)" % self.flag, name, fold)
            dist = self.retired - self.cmp_at - 1
            if dist <= 0:
                key = "Incorrect prediction, jump after compare"
            elif dist == 1:
                key = "Incorrect prediction, jump 2 instructions after compare"
            elif dist == 2:
                key = "Incorrect prediction, jump 3 instructions after compare"
            else:
                key = ("Incorrect prediction, %s, 4 or more instructions "
                       "after compare" % ("folded" if fold else "unfolded"))
            c, row = self.rows.variant(key)
            return c, "%s (dist %d)" % (row, dist), name, fold
        if name == "JMP":
            fold = self.folded(recs, i, d)
            return (0 if fold else 1), "t432_jmp (%s)" % (
                "folded" if fold else "unfolded"), name, fold
        if name == "ENTER":
            E = self.enter_blocks(rec, d)
            r = self.rows.by_op["ENTER"]
            return (evaluate(r["time"], self.board, E),
                    "%s (E=%d)" % (r["id"], E), name, False)
        if name == "DQM":
            c, row = self.dqm(rec, d)
            return c, row, name, False
        c, row = self.rows.fixed(name)
        if d.cpu:
            c0, _ = self.rows.fixed("CPU")
            c += c0
            row += " + t432_cpu"
        return c, row, name, False

    def after_record(self, rec, d, fold):
        """Advance the compare distance and the flag's provenance."""
        if rec[10]:
            self.flag = "a trap's handler (not in the stream)"
            return
        if d.name in COMPARES:
            self.cmp_at = self.retired
            self.flag = "compare"
        elif d.name in FLAG_WRITERS:
            self.flag = FLAG_WRITERS[d.name]
        elif d.cpu and d.dmode == 7:
            n = d.length - 1
            dst = d.parcels[2] if n == 3 else d.parcels[4]
            if dst is None or (dst & 0xF) == 5:
                self.flag = "a CPU-prefixed write of PSW"
        if not (fold and self.board.get("distance") == "slots"):
            self.retired += 1

    def run(self, recs):
        self.decoded = [decode(r[0], r[1], self.mem.parcel) for r in recs]
        out = []
        for i, rec in enumerate(recs):
            c, why, name, fold = self.price(recs, i)
            out.append((c, why, name, fold))
            self.after_record(rec, self.decoded[i], fold)
            if rec[6]:
                self.mem.write(rec[7], rec[8], rec[9])
        return out


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _rowkey(why):
    return re.sub(r" \(dist \d+\)| \(E=\d+\)", "", why)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("trace")
    img = ap.add_mutually_exclusive_group()
    img.add_argument("--hex", help="a golden word image (address 0 up)")
    img.add_argument("--aout", help="the 1e executable the trace ran")
    img.add_argument("--boot-rec", help="p9coreboot.py's boot.rec")
    ap.add_argument("--board", default=BOARD)
    ap.add_argument("--compare", action="store_true")
    ap.add_argument("--per-record", action="store_true")
    ap.add_argument("--examples", type=int, default=3)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--config-px", choices=("0", "1"),
                    help="override the board's CONFIG PC-extension bit")
    a = ap.parse_args(argv)

    board = read_board(a.board)
    if a.config_px:
        board["config_px"] = a.config_px
    rows = Rows(TIMING_CSV, board)
    mem = Memory()
    after = {}
    if a.hex:
        mem.load_hex(a.hex)
    elif a.aout:
        mem.load_aout(a.aout)
    elif a.boot_rec:
        after = mem.load_boot_rec(a.boot_rec)
    recs = read_trace(a.trace, a.limit)
    twin = Twin(rows, board, mem, after)
    out = twin.run(recs)

    if a.per_record:
        for i, (rec, (c, why, name, _f)) in enumerate(zip(recs, out)):
            print("%d %x %s %s %d %s" % (i, rec[0], name,
                                         "-" if c is None else c, rec[11],
                                         why))
    total = sum(c for c, _w, _n, _f in out if c is not None)
    undet = [(i, o) for i, o in enumerate(out) if o[0] is None]
    print("twin: %d records, sum of determined cyc %d, %d undetermined"
          % (len(recs), total, len(undet)))
    groups = {}
    for i, (c, why, name, _f) in undet:
        groups.setdefault(("-", why, name), []).append(i)
    if a.compare:
        agree = 0
        for i, (rec, (c, why, name, _f)) in enumerate(zip(recs, out)):
            if c is None:
                continue
            if c == rec[11]:
                agree += 1
            else:
                groups.setdefault(((c, rec[11]), _rowkey(why), name),
                                  []).append(i)
        det = len(recs) - len(undet)
        print("twin = trace on %d of %d determined records" % (agree, det))
    for (pair, why, name), idx in sorted(groups.items(),
                                         key=lambda kv: -len(kv[1])):
        tag = ("undetermined" if pair == "-"
               else "twin %d trace %d" % pair)
        print("  %-20s %7d  %-8s %s" % (tag, len(idx), name, why))
        for i in idx[:a.examples]:
            print("      record %d pc=%x" % (i, recs[i][0]))
    if a.compare:
        bad = sum(len(v) for (p, _w, _n), v in groups.items() if p != "-")
        return 1 if bad else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
