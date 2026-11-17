#!/usr/bin/env python3
"""atlas_oracle.py -- the atlas oracle (docs/source_audit.md G4.1).

Perf. Char. Vol. 2's per-instruction atlas is transcribed in
tests/perf_char_vol2_atlas.txt.  For every transcribed case this script can
express as a STRAP program it builds the program the way the atlas's own
generator did, runs it on the mkStretchCore model, and reports the
RESIDUAL: model minus printed, in clocks of 0.3 us (docs/clock_unit.md).

IT IS A MEASUREMENT, NOT A TEST.  It never fails on a residual; the exit
status is non-zero only if the harness itself is broken (a build failure,
a --selftest failure); a case that does not assemble or does not halt is
listed under COULD NOT BE RUN, never folded into the residuals.  It is NOT run by
run_tests.sh: tests/check_atlas_data.py is the fast check that is.

    python3 tests/atlas_oracle.py                 # every expressible case
    python3 tests/atlas_oracle.py --pdf 120       # one page
    python3 tests/atlas_oracle.py --pdf 120 --col ni_ext --rows
    python3 tests/atlas_oracle.py --selftest      # the harness's own checks
    python3 tests/atlas_oracle.py --list          # what is / is not expressible
    python3 tests/atlas_oracle.py --tsv out.tsv   # every case, machine-readable

HOW A NUMBER IS MADE -- GENER'S WAY (Vol. 2 PDF 37-39).  One instruction is
replicated a thousand times, "after which a count branch (with an original
count of 10) is inserted", and "this sequence is then executed 10 times":
10,000 executions, closed by ten count branches, timed as one interval.
This script generates exactly that sequence (BODY_COPIES x LOOP_COUNT) and
divides by 10,000, so -- like the printed figure -- its number is a
THROUGHPUT that carries the ten count branches, not an isolated latency.
The set-up instructions and the halt are removed by subtracting a BASELINE
run of the same program with an empty body and no count branch.

ONE BUILD, MANY RUNS.  The testbench (bsv/StretchAtlasTb.bsv, a gitignored
build product like every Stretch*Tb.bsv) is generated ONCE with a fixed
start address and a fixed-size FASTLOAD image named by a RELATIVE path.
Each case then only rewrites that hex file in its own scratch directory and
reruns the same Bluesim binary, about a third of a second a case.  The
binary is rebuilt when any hand-written bsv/*.bsv is newer than it; that
first build takes several minutes.

WHAT IS ASSUMED, because the volume does not print it (each is echoed in
the report's header so a residual is never read without it):
  * EXTERNL WB XOVR: the field starts FL//2 bits before a word boundary.
  * INDEXING: the index register is $X5, containing zero (PDF 113 says only
    "an index register containing zero").
  * INVERT SIGN OF INSTRUCTION: the VFL operation's invert-sign modifier
    bit, set by XORing the assembled word (STRAP's "N" suffix is not
    implemented for every operation; the bit is the one that separates
    "-" from "+").
  * The accumulator's initial contents where PDF 113 names none: the
    standard operand (444...4)16.
  * The VFL INTERNL, IMMED. and ACCUM. (CV/DCV) columns and the FP pages
    (PDF 42-101) have generators of their own (vfl_case's internal branch,
    _imm_case, _cv_case, fp_case); what each takes from PDF 40 and PDF
    113-114, and what each CHOOSES, is in their comments and ASSUMPTIONS.
"""
import argparse
import concurrent.futures
import glob
import os
import re
import subprocess
import sys
import tempfile
import time
from decimal import Decimal

HERE = os.path.dirname(os.path.abspath(__file__))
STRETCH = os.path.dirname(HERE)
BSV = os.path.join(STRETCH, "bsv")
sys.path[:0] = [os.path.join(STRETCH, "strap"), HERE]

from atlas_data import load_atlas, CLOCK_US       # noqa: E402

BSC_HOME = "/opt/homebrew/Cellar/bsc/2026.01"     # as run_program.sh pins it
MODULE = "StretchAtlasTb"
IMAGE_NAME = "atlas_image.hex"
IMAGE_WORDS = 1200            # fixed image size the one testbench loads
PAD_BASE = 0o200000           # padding words (zeros) are written from here
START_ADDR = 0o2000           # START, a full-word address; fixed in the build
BODY_ADDR = 0o3000
STEP_CAP = 20_000_000
BODY_COPIES = 1000            # GENER: "until a thousand instructions"
LOOP_COUNT = 10               # GENER: "a count branch (with an original count of 10)"
STD = 0x4444444444444444      # PDF 113: "A standard operand (444 ..... 4)16"
VFL_INVERT_BIT = 0x800        # the bit separating "-(BU,8,8)" from "+(BU,8,8)"
EXACT = 0.1                   # clocks.  A printed figure is good to +-0.01 us
                              # (PDF 39), a thirtieth of a clock, and both it
                              # and the model's figure carry the count
                              # branches (0.017 clock here); 0.1 clock is the
                              # smallest band that calls two such figures
                              # the same whole number of clocks.

ASSUMPTIONS = [
    "WB XOVR columns, no forwarding: field starts FL//2 bits before a word "
    "boundary (with forwarding, PDF 114's bit 60, .74 octal)",
    "INDEXING columns: indexed by $X5, which holds zero (a half-word "
    "branch by $X1, its one-bit K field's only choice)",
    "TRANSMIT: the I-box block is 18.0 for source and destination "
    "(ibox_ibox transmits onto itself); external 10000.0 -> 50000.0 (octal)",
    "branch SUCCESS columns: each copy branches to the next copy, a "
    "half-word on; the condition is set once in the set-up and stays",
    "INVERT SIGN blocks: VFL invert-sign modifier bit XORed into the word",
    "accumulator starts as the standard operand unless PDF 113 says otherwise",
    "no-forwarding external operands rotate over 150000.0-150003.0 (octal), "
    "I-box operands over $X0-$X3 (PDF 114)",
    "VFL INTERNL columns (forwarding only): 8.0 and 8.60 (PDF 114's (10.0)8 "
    "and (10.74)8); the operand is what the accumulator set-up left there",
    "VFL IMMED. pages: address field forced to (444444)16 (PDF 114) by XOR "
    "over a zero immediate; accumulator as on the direct page (PDF 113)",
    "CV/DCV: accumulator +1 at offset 20 (PDF 113); the unused address names "
    "150000.0 (Ref. Manual p.72: not used)",
    "FP: external 100011-100014 (octal) rotated, or 100011 alone with "
    "forwarding (PDF 40 prints 1000011, which an 18-bit address cannot hold)",
    "FP: I-box operands are the whole word stored into $X9-$X12 ($X9 with "
    "forwarding); internal operand $R, set to the memory word by TI",
    "FP blocks: XPFN = the one with exponent flag on and exponent sign "
    "negative, XPFP the same positive, U,V FLAGS = data flags U and V on; a "
    "load page's accumulator is the normalized one; FT = accumulator word",
    "FP KR/KMGR AH ON/OFF: set once by K of 2 against 1 / 1 against 2",
    "FP E+I / SHF: the column's number is the address operand as STRAP "
    "assembles a literal (bits 0-10, decimal; SHF left)",
]


# ---------------------------------------------------------------------------
# The harness: one testbench, many images
# ---------------------------------------------------------------------------

def _env():
    e = dict(os.environ)
    e["BLUESPECDIR"] = BSC_HOME + "/libexec/lib"
    e["PATH"] = BSC_HOME + "/bin:" + e.get("PATH", "")
    return e


def _assemble(src):
    from strap_asm import assemble
    return assemble(src)


def _program(setup, body, data, loop):
    """GENER's shape.  `body` is the list of replicated instruction lines."""
    s = ["        SLC, (8)%o.0" % START_ADDR]
    first = True
    for line in setup + ["B, BODY"]:
        s.append(("START   " if first else "        ") + line)
        first = False
    s.append("        SLC, (8)%o.0" % BODY_ADDR)
    lines = list(body)
    if loop:
        # The count register is $X15: PDF 105 puts transmit's I-box
        # operands in "$2 through $14", and a 13-word TRANSMIT into 18.0
        # overwrote the $X14 this once used -- two cases never halted.
        lines.append("CB, $X15, BODY")
    lines.append("B, $")
    first = True
    for line in lines:
        s.append(("BODY    " if first else "        ") + line)
        first = False
    s.append("ATLCNT  XW, 0, %d, 0" % LOOP_COUNT)
    s.append("ATLZERO DD(BU,64,8), 0")
    s.append("ATLSTD  DD(BU,64,8), %d" % STD)
    s.append("ATLONE  DD(BU,64,8), 1")
    s += data
    s.append("        END, START")
    return "\n".join(s) + "\n"


def _image(src, xor_body=0, n_body=0):
    prog = _assemble(src)
    assert prog.end_pc == START_ADDR * 2, "START moved: %r" % prog.end_pc
    words = dict(prog.words)
    if xor_body:
        for i in range(n_body):
            words[BODY_ADDR + i] ^= xor_body
    words = sorted(words.items())
    if len(words) > IMAGE_WORDS:
        raise ValueError("image has %d words, the testbench loads %d"
                         % (len(words), IMAGE_WORDS))
    used = {a for a, _ in words}
    pad, a = [], PAD_BASE
    while len(words) + len(pad) < IMAGE_WORDS:
        if a not in used:
            pad.append((a, 0))
        a += 1
    return words + pad


def _write_image(words, path):
    with open(path, "w") as f:
        for addr, val in words:
            f.write("%024x\n" % ((addr << 64) | val))


def sim_path():
    return os.path.join(BSV, MODULE + "_sim")


def build_needed():
    sim = sim_path()
    if not (os.path.exists(sim) and os.path.exists(sim + ".so")):
        return True
    t = os.path.getmtime(sim + ".so")
    srcs = [p for p in glob.glob(os.path.join(BSV, "*.bsv"))
            if not re.search(r"Stretch\w*Tb\.bsv$", p)]
    if any(os.path.getmtime(p) > t for p in srcs):
        return True
    # ...or the testbench this script would generate is not the one on disk
    return _tb_text() != _read(os.path.join(BSV, MODULE + ".bsv"))


def _read(p):
    try:
        with open(p) as f:
            return f.read()
    except OSError:
        return None


def _tb_text():
    import gen_tb
    src = _program(["LX, $X15, ATLCNT"], [], [], loop=False)
    prog = _assemble(src)
    prog.words = dict(_image(src))
    # gen_tb writes the FASTLOAD image as a side effect, to the relative
    # path it is given; let it do that in a scratch directory, not here.
    here = os.getcwd()
    with tempfile.TemporaryDirectory(prefix="atlas-") as td:
        os.chdir(td)
        try:
            return gen_tb.generate(MODULE, prog, [], step_cap=STEP_CAP,
                                   cycle_bound=STEP_CAP - 1,
                                   fast_load=IMAGE_NAME)
        finally:
            os.chdir(here)


def build(verbose=True):
    """Generate and compile the one testbench.  Several minutes."""
    t0 = time.time()
    with open(os.path.join(BSV, MODULE + ".bsv"), "w") as f:
        f.write(_tb_text())
    bsc = BSC_HOME + "/bin/bsc"
    os.makedirs(os.path.join(BSV, "build"), exist_ok=True)
    os.makedirs(os.path.join(BSV, "simbuild"), exist_ok=True)
    cmds = [
        [bsc, "-sim", "-simdir", "simbuild", "-bdir", "build", "-info-dir",
         "build", "-g", "mk" + MODULE, "-u", MODULE + ".bsv",
         "+RTS", "-K512m", "-RTS"],
        [bsc, "-sim", "-simdir", "simbuild", "-bdir", "build", "-e",
         "mk" + MODULE, "-o", MODULE + "_sim", "+RTS", "-K512m", "-RTS"],
    ]
    if verbose:
        print("building %s (several minutes the first time) ..." % MODULE,
              file=sys.stderr, flush=True)
    for c in cmds:
        r = subprocess.run(c, cwd=BSV, env=_env(), capture_output=True, text=True)
        if r.returncode != 0:
            sys.stderr.write(r.stdout[-4000:] + r.stderr[-4000:])
            raise SystemExit("atlas_oracle: bsc failed")
    if verbose:
        print("built in %.0f s" % (time.time() - t0), file=sys.stderr, flush=True)


_CYC = re.compile(r"^(PASS|FAIL) cycles = (\d+)", re.M)


def run_image(words):
    """Run one image; return the clock count at halt, or None if the run
    hit the step cap (did not halt)."""
    with tempfile.TemporaryDirectory(prefix="atlas-") as td:
        _write_image(words, os.path.join(td, IMAGE_NAME))
        r = subprocess.run([sim_path()], cwd=td, env=_env(),
                           capture_output=True, text=True)
    out = r.stdout
    if "step cap" in out:
        return None
    m = _CYC.search(out)
    if not m:
        raise SystemExit("atlas_oracle: no cycle count in simulator output:\n"
                         + out[-2000:] + r.stderr[-2000:])
    return int(m.group(2))


class Case:
    """One printed cell, as a program."""

    def __init__(self, rec, setup, instr_lines, data=(), xor_body=0, note=""):
        self.rec = rec
        self.setup = ["LX, $X15, ATLCNT"] + list(setup)
        self.instr_lines = list(instr_lines)      # rotated to fill the body
        self.data = list(data)
        self.xor_body = xor_body
        self.note = note
        self.model = None       # clocks per instruction (float)
        self.error = None

    target_per_copy = False     # the line holds %d.%d: the copy's successor,
                                # whose address is word.bit; the copies are
                                # HALF-WORD instructions (CB, BI, B), two to
                                # a word, so copy i+1 is at half-word i+1

    def body(self, copies=BODY_COPIES):
        n = len(self.instr_lines)
        lines = [self.instr_lines[i % n] for i in range(copies)]
        if self.target_per_copy:
            lines = [l % ((i + 1) // 2, 32 * ((i + 1) % 2))
                     for i, l in enumerate(lines)]
        return lines

    def images(self, copies=BODY_COPIES):
        body = self.body(copies)
        full = _image(_program(self.setup, body, self.data, loop=True),
                      self.xor_body, len(body))
        base = _image(_program(self.setup, [], self.data, loop=False))
        return full, base

    def measure(self, copies=BODY_COPIES):
        try:
            full, base = self.images(copies)
        except Exception as e:                    # an assembler refusal
            self.error = "does not assemble: %s" % e
            return None
        c_full, c_base = run_image(full), run_image(base)
        if c_full is None or c_base is None:
            self.error = "did not halt within %d clocks" % STEP_CAP
            return None
        self.model = (c_full - c_base) / float(copies * LOOP_COUNT)
        return self.model

    @property
    def printed_cycles(self):
        return float(self.rec.cycles)

    @property
    def residual(self):
        return None if self.model is None else self.model - self.printed_cycles


# ---------------------------------------------------------------------------
# Case builders, one per page class.  Each returns a Case, or a string
# saying why the cell is not expressed.
# ---------------------------------------------------------------------------

_DDS = re.compile(r"^\((BU|B|DU|D),(\d+),(\d+)\)$")

EXT_BASE = 0o150000       # PDF 114: "(150000.0)8 ... (150003.0)8"
INT_WBX_BIT = 0o74        # PDF 114: "internal with word boundary crossover
                          # (10.74)8" -- word 8 ($L), bit 60

# How PDF 113 (printed 106) says the accumulator and the memory operand were
# set for the VFL pages.  mem: what the external/I-box operand words hold.
# acc: set-up lines run once before the body.
_ACC_STD = ["L(BU,64,8), ATLSTD"]
_ACC_ONE = ["L(BU,64,8), ATLONE"]
_ACC_FT_STD = ["LFT(BU,64,8), ATLSTD", "L(BU,64,8), ATLSTD"]
VFL_OPERANDS = {
    # instr: (memory operand, accumulator set-up)
    "+": (STD, _ACC_ONE),         # "the accumulator was initially a low
                                  # order +1, and the memory operand
                                  # +(444...4)16"
    "M+": (1, _ACC_STD),          # "the accumulator was initially
                                  # +(444...4)16 and the memory operand +1"
    "*": (1, _ACC_FT_STD),        # "the accumulator and factor registers
    "*+": (1, _ACC_FT_STD),       # initially contained the standard operand
    "/": (1, _ACC_FT_STD),        # and the memory operand was +1"
}
# Every other VFL instruction: "A standard operand (444 ..... 4)16 was used".
# PDF 113 names no exception for +MG or M+MG, so they get the standard
# operand in both places -- the literal reading, and an assumption.
VFL_STANDARD = ["+MG", "M+MG", "L", "LWF", "LFT", "LTRS", "ST", "SRD", "M+1",
                "K", "KR", "KE", "KF", "KFR", "KFE", "LCV", "LTRCV"]
# PDF 171-189, IMMEDIATE ADDRESSING: each page's instruction is the direct
# one's immediate form (check_atlas_data.IMM_BASE, the same map).
VFL_IMM_BASE = {
    "+I": "+", "+MGI": "+MG", "LI": "L", "LWFI": "LWF", "LFTI": "LFT",
    "LTRSI": "LTRS", "KI": "K", "KRI": "KR", "KEI": "KE", "KFI": "KF",
    "KFRI": "KFR", "KFEI": "KFE", "*I": "*", "/I": "/", "*I+": "*+",
    "LCVI": "LCV", "LTRCVI": "LTRCV", "CI0011": "C0011",
    "CTI0111": "CT0111",
}
# PDF 114: "The 24 bit address of the instruction contained the equivalent
# of the standard operand (444 ...4)16."
IMM_ADDR = 0x444444
# CV and DCV (PDF 138-139, 165-166) head the column ACCUM. OPERAND.  PDF 113:
# "for convert (CV) and convert double (DCV) the accumulator was originally
# +1 at offset 20."  Reference Manual printed p.72: "In the accumulator
# conversion operations, CONVERT and CONVERT DOUBLE, no storage operand is
# required, and the word address, bit address, length, and byte size fields
# of the instruction are not normally used."
_ACC_CV = ["L(BU,64,8), ATLONE, 20"]


def vfl_case(rec):
    m = _DDS.match(rec.row)
    if not m:
        return "row label %r is not a data description" % rec.row
    mode, fl, bs = m.group(1), int(m.group(2)), int(m.group(3))
    instr = rec.instr
    imm = rec.cond.get("addressing") == "immediate"
    if imm:
        if instr not in VFL_IMM_BASE:
            return "no generator for VFL immediate instruction %s" % instr
        instr = VFL_IMM_BASE[instr]
    if instr in ("CV", "DCV"):
        return _cv_case(rec, mode, fl, bs)
    if re.match(r"^C[MT]?[01]{4}$", instr):
        mem, acc = STD, _ACC_STD
    elif instr in VFL_OPERANDS:
        mem, acc = VFL_OPERANDS[instr]
    elif instr in VFL_STANDARD:
        mem, acc = STD, _ACC_STD
    else:
        return "no generator for VFL instruction %s" % instr
    op = rec.instr
    if imm:
        return _imm_case(rec, op, mode, fl, bs, acc)
    if rec.cond.get("addressing") != "direct":
        return "addressing=%s not generated" % rec.cond.get("addressing")
    fwd = rec.cond.get("forwarding") == "yes"
    col = rec.col
    indexed = col.startswith("ix_")
    place = col[3:]
    ix = "($X5)" if indexed else ""
    n_addr = 1 if fwd else 4
    setup = list(acc) + ["LX, $X5, ATLZERO"]
    data = ["        SLC, (8)%o.0" % EXT_BASE]
    data += ["ATLE%d   DD(BU,64,8), %d" % (i, mem) for i in range(5)]
    if place == "ext":
        addrs = ["ATLE%d" % i for i in range(n_addr)]
    elif place == "ext_wbx":
        if fl < 2:
            return "a one-bit field cannot cross a word boundary"
        # PDF 114 (printed 107) gives the FORWARDING run's location:
        # "external with WB crossover (150000.74)8" -- bit 60 whatever the
        # field length.  The no-forwarding pages state none, so they keep
        # the FL//2 assumption (ASSUMPTIONS above).
        start = 0o74 if fwd else 64 - fl // 2
        addrs = ["ATLE%d+.%d" % (i, start) for i in range(n_addr)]
    elif place == "ibox":
        setup += ["LX, $X%d, ATLE0" % i for i in range(n_addr)]
        addrs = ["$X%d" % i for i in range(n_addr)]
    elif place in ("int", "int_wbx"):
        # PDF 114 (printed 107), FORWARDING / DIRECT ADDRESSING: "internal
        # (10.0)8, internal with word boundary crossover (10.74)8" -- the
        # accumulator's left word $L (8.0), and bit 60 of it, so a field of
        # more than 4 bits runs on into $R.  Only the forwarding pages print
        # these columns.  The operand is whatever the accumulator set-up
        # left there (PDF 113 names no internal-operand value): CHOSEN.
        if not fwd:
            return "INTERNL columns are printed only with forwarding"
        if place == "int_wbx" and fl < 2:
            return "a one-bit field cannot cross a word boundary"
        addrs = ["8.0" if place == "int" else "8.%d" % INT_WBX_BIT]
    else:
        return "operand placement %r not generated" % place
    lines = ["%s(%s,%d,%d), %s%s" % (op, mode, fl, bs, a, ix) for a in addrs]
    xor = _vfl_xor(rec)
    if xor is None:
        return "block %r not generated" % rec.block
    return Case(rec, setup, lines, data, xor)


def _vfl_xor(rec):
    if rec.block == "-":
        return 0
    if rec.block == "INVERT SIGN OF INSTRUCTION":
        return VFL_INVERT_BIT
    return None


def _imm_case(rec, op, mode, fl, bs, acc):
    """PDF 171-189.  The instruction is assembled with a zero immediate and
    its 24-bit address field is then set to (444444)16 by XOR, so the field
    holds the standard operand whatever the field length -- PDF 114's words
    -- and not the operand's left-justified leading bits alone, which is
    what STRAP would assemble from a literal (encode_vfl_immediate).  The
    accumulator is set up as for the direct page (PDF 113).  CHOSEN: PDF
    113's "memory operand +1" for *, *+ and / is overruled by PDF 114's
    address contents, which describe this run."""
    xor = _vfl_xor(rec)
    if xor is None:
        return "block %r not generated" % rec.block
    if not rec.col.endswith("_imm"):
        return "immediate page column %r not generated" % rec.col
    ix = "($X5)" if rec.col.startswith("ix_") else ""
    setup = list(acc) + ["LX, $X5, ATLZERO"]
    line = "%s(%s,%d,%d), 0%s" % (op, mode, fl, bs, ix)
    return Case(rec, setup, [line], [], xor | (IMM_ADDR << 40))


def _cv_case(rec, mode, fl, bs):
    """CV / DCV: the operand is the accumulator, +1 at offset 20 (PDF 113);
    the instruction's own offset is the page heading's OFFSET 0.  CHOSEN:
    the unused address field names ATLE0, the first external word, which
    the instruction never reads (Ref. Manual p.72)."""
    xor = _vfl_xor(rec)
    if xor is None:
        return "block %r not generated" % rec.block
    if not rec.col.endswith("_accum"):
        return "CV/DCV column %r not generated" % rec.col
    ix = "($X5)" if rec.col.startswith("ix_") else ""
    setup = list(_ACC_CV) + ["LX, $X5, ATLZERO"]
    data = ["        SLC, (8)%o.0" % EXT_BASE, "ATLE0   DD(BU,64,8), %d" % STD]
    line = "%s(%s,%d,%d), ATLE0%s" % (rec.instr, mode, fl, bs, ix)
    return Case(rec, setup, [line], data, xor)


# --- floating point, PDF 42-101 ----------------------------------------------
# PDF 40 (printed 34C), FLOATING POINT TIMING, read on the page image:
#   "Sequences of operations were generated and timed by GENER."
#   External Operands: "Consecutive memory boxes were used where possible.
#     Cases without forwarding used a repetition of four consecutive
#     addresses 100011_8 to 100014_8.  Cases with forwarding used 1000011_8."
#   I-Box Operands: "Index registers nine to twelve were used in the cases
#     without forwarding and index nine in the cases with forwarding."
#   Internal Operands: "The right half of the accumulator, $R, was used for
#     all cases."
#   Data: "A normalized floating point one (1) was the initial operand
#     unless otherwise specified.  (Cases were run with flagged exponents
#     superimposed.)"
# PDF 41 (printed 34D): "Forwarding merely means using the same operand
# address."
#
# "1000011_8" is seven octal digits (re-read at 300 dpi: it is printed so);
# an FP instruction's address is 18 bits (enc_fp), and 1000011_8 = 262153
# does not fit.  CHOSEN: the forwarding run uses 100011_8, the first of the
# four the no-forwarding run rotates over.
FP_EXT_BASE = 0o100011
FP_IBOX_FIRST = 9             # $X9 .. $X12; $X9 alone with forwarding

# The FP word (Reference Manual, Floating-Point Data Format; StretchFP.bsv's
# fpFromWord): bit 0 exponent flag, 1-10 exponent, 11 exponent sign, 12-59
# fraction, 60 fraction sign, 61-63 data flags T, U, V.
def _fpword(exp=1, frac=1 << 47, ef=0, es=0, flags=0):
    return (ef << 63) | (exp << 53) | (es << 52) | (frac << 4) | flags

FP_ONE = _fpword()                   # +.1 (binary) x 2^+1 = 1, normalized
FP_TWO = _fpword(exp=2)
# The block captions.  CHOSEN (the volume prints only the captions): XPFN is
# the normalized one with the exponent flag on and the exponent sign
# negative ("flagged exponents superimposed"); XPFP the same with the sign
# positive; U,V FLAGS the one with data flags U and V (bits 62, 63) on.
FP_XPFN = _fpword(ef=1, es=1)
FP_XPFP = _fpword(ef=1)
FP_UV = _fpword(flags=0b011)
FP_BLOCKS = {                        # caption: (accumulator, memory operand)
    "NORMALIZED 1.": (FP_ONE, FP_ONE),
    "BOTH OPERANDS WITH XPFN": (FP_XPFN, FP_XPFN),
    "AC EXPNT N. MEM EXPNT XPFN": (FP_ONE, FP_XPFN),
    "AC WITH XPFP. MEM WITH XPFN": (FP_XPFP, FP_XPFN),
    # the load pages (PDF 64-70, 95-101) caption the memory operand alone;
    # the accumulator is the normalized one (CHOSEN)
    "MEMORY OPERAND HAS XPFN": (FP_ONE, FP_XPFN),
    "MEMORY OPERAND HAS U,V FLAGS": (FP_ONE, FP_UV),
    "MEMORY OPERAND HAS XPFP": (FP_ONE, FP_XPFP),
    # E+I (PDF 71) and SHF (PDF 72): no memory operand
    "ADDRESS FIELD NOT INDEXED": (FP_ONE, None),
    "ADDRESS FIELD IS INDEXED": (FP_ONE, None),
}
# Row labels: the normalization modifier (N)/(U) and the sign modifiers,
# NEG = negative (invert) sign and A = absolute sign, STRAP's N / A / NA
# mnemonic suffixes (strip_fp_sign; pocket card "L(N,A,NA)").
_FP_ROW = re.compile(r"^(NEG )?(A)?\((N|U)\)$")
FP_SUFFIX = {(False, False): "", (True, False): "N", (False, True): "A",
             (True, True): "NA"}


def fp_parts(rec):
    """(mnemonic, mode, absSign, invSign) for an FP row, or None."""
    m = _FP_ROW.match(rec.row)
    if not m:
        return None
    neg, ab, mode = bool(m.group(1)), bool(m.group(2)), m.group(3)
    return rec.instr + FP_SUFFIX[(neg, ab)], mode, int(ab), int(neg)


def fp_case(rec):
    parts = fp_parts(rec)
    if parts is None:
        return "FP row label %r is not a modifier set" % rec.row
    op, mode, _, _ = parts
    if rec.block not in FP_BLOCKS:
        return "FP block %r not generated" % rec.block
    acc, mem = FP_BLOCKS[rec.block]
    col = rec.col
    setup = ["LX, $X5, ATLZERO"]
    data = ["ATLFA   DD(BU,64,8), %d" % acc, "ATLFONE DD(BU,64,8), %d" % FP_ONE,
            "ATLFTWO DD(BU,64,8), %d" % FP_TWO]
    if rec.instr in ("E+I", "SHF"):
        # PDF 71 heads its columns EFFECTIVE ADDRESSES / ONE / 2040, PDF 72
        # SHIFT 1 ... SHIFT 95: the address field IS the operand.  The
        # blocks say whether it is indexed (by $X5 = 0, as elsewhere).
        n = int(col.split("_")[1].replace("one", "1"))
        ix = "($X5)" if rec.block == "ADDRESS FIELD IS INDEXED" else ""
        setup += ["LFT(U), ATLFA", "L(U), ATLFA"]
        return Case(rec, setup, ["%s(%s), %d%s" % (op, mode, n, ix)], data)
    fwd = rec.cond.get("forwarding") == "yes"
    indexed, place = col.startswith("ix_"), col[3:]
    ix = "($X5)" if indexed else ""
    data += ["        SLC, (8)%o.0" % FP_EXT_BASE]
    data += ["ATLFM%d  DD(BU,64,8), %d" % (i, mem) for i in range(4)]
    pre = []
    if place == "ext":
        addrs = ["ATLFM%d" % i for i in range(1 if fwd else 4)]
    elif place == "ibox":
        regs = range(FP_IBOX_FIRST, FP_IBOX_FIRST + (1 if fwd else 4))
        # the whole word into the index register's storage location
        pre += ["L(BU,64,8), ATLFM0"] + ["ST(BU,64,8), $X%d" % r for r in regs]
        addrs = ["$X%d" % r for r in regs]
    elif place == "int":
        if not fwd:
            return "INTERNAL is printed blank without forwarding"
        addrs = ["$R"]
    else:
        return "FP column %r not generated" % col
    # KR / KMGR pages are printed twice, AH INDICATOR OFF and ON.  CHOSEN:
    # set it once in the set-up by a compare, 2 against 1 (AH on) or 1
    # against 2 (AL on, AH off), before the accumulator is loaded.
    ah = rec.cond.get("ah_indicator")
    if ah == "on":
        pre += ["L(U), ATLFTWO", "K(U), ATLFONE"]
    elif ah == "off":
        pre += ["L(U), ATLFONE", "K(U), ATLFTWO"]
    # The accumulator.  CHOSEN: the factor register (for *+) holds the same
    # word as the accumulator; the load is unnormalized so the flagged word
    # lands as written; $R (the internal operand) then gets the memory
    # operand by a one-word TRANSMIT, since a load clears it.
    setup += pre + ["LFT(U), ATLFA", "L(U), ATLFA"]
    if place == "int":
        setup += ["TI, 1, ATLFM0, 9.0"]
    lines = ["%s(%s), %s%s" % (op, mode, a, ix) for a in addrs]
    return Case(rec, setup, lines, data)


# --- index arithmetic, PDF 109 ---------------------------------------------
# PDF 108 (printed 101): "The external operands refer to the two lowest
# memory boxes.  The internal operands refer to locations 7.0, 8.0 and 9.0."
IBOX_EXT = (0o10000, 0o50000)       # one word in each of the two lowest boxes
IBOX_DIRECT = ["LX", "LV", "LC", "LR", "SX", "SV", "SC", "SR", "V+", "V+C",
               "KV", "KC"]
IBOX_IMMEDIATE_OF = {"LV": "LVI", "LC": "LCI", "LR": "LRI", "V+": "V+I",
                     "V+C": "V+IC", "KV": "KVI", "KC": "KCI",
                     "LVNI": "LVNI", "V-I": "V-I", "V-IC": "V-IC",
                     "C+I": "C+I", "C-I": "C-I", "KVNI": "KVNI"}
IBOX_UNEXPRESSED = {
    "V+CR#1": "two unlabelled V+CR rows; which is the refill case is not printed",
    "V+CR#2": "two unlabelled V+CR rows; which is the refill case is not printed",
    "V-ICR#1": "two unlabelled V-ICR rows",
    "V-ICR#2": "two unlabelled V-ICR rows",
    "R": "refill: the refill word chain is not described",
    "RCZ#1": "two unlabelled RCZ rows", "RCZ#2": "two unlabelled RCZ rows",
    "RNX": "the old name (X0's refill) the experiment used is not described",
}


def ibox_case(rec):
    if rec.pdf != 109:
        return "PDF %d (LVS, LVE, SVA): no generator" % rec.pdf
    row = rec.row
    if row in IBOX_UNEXPRESSED:
        return "index %s: %s" % (row, IBOX_UNEXPRESSED[row])
    # $X1 is the register operated on: value 8, count 100000 (so that ten
    # thousand count-downs never reach zero), no refill.
    setup = ["LX, $X1, ATLXW", "LX, $X5, ATLZERO", "LX, $X2, ATLXW"]
    data = ["ATLXW   XW, 8, 100000, 0"]
    for i, a in enumerate(IBOX_EXT):
        data += ["        SLC, (8)%o.0" % a, "ATLXE%d  XW, 8, 100000, 0" % i]
    col = rec.col
    if col == "immediate":
        op = IBOX_IMMEDIATE_OF.get(row)
        if op is None:
            return "index %s has no immediate form on the page" % row
        return Case(rec, setup, ["%s, $X1, 8" % op], data)
    if row not in IBOX_DIRECT:
        return "no generator for index instruction %s" % row
    place, mode = col.split("_")
    ix = "($X5)" if mode == "effective" else ""
    if place == "ext":
        addrs = ["ATLXE0", "ATLXE1"]
    elif place == "int":
        addrs = ["7.0", "8.0", "9.0"]
    else:
        addrs = ["$X2"]
    return Case(rec, setup, ["%s, $X1, %s%s" % (row, a, ix) for a in addrs], data)


# --- branches, PDF 112 -------------------------------------------------------
def branch_case(rec):
    col = rec.col
    indexed = col.startswith("ix_")
    kind = col[3:] if indexed else col
    if not kind.endswith("_consec"):
        return ("NONCON columns: a branch 'from one to four instructions' "
                "ahead (PDF 111) skips part of the thousand; how GENER "
                "counted that is not printed")
    succ = kind.startswith("succ")
    # A half-word branch's index field is ONE bit, K (the assembler's
    # enc_count_branch / enc_branch_ind; the model's evalBranch: "K: X1
    # only"), so an indexed branch is indexed by $X1 and nothing else.
    # $X1 therefore holds zero and the COUNTED register is $X2.
    ix = "($X1)" if indexed else ""
    names = rec.row.split()
    setup = ["LX, $X2, ATLXW", "LX, $X1, ATLZERO"]
    data = ["ATLXW   XW, 8, 100000, 0"]
    if names[0].startswith("CBR"):
        return ("CBR: 'success' is a successful REFILL with a count of one "
                "(PDF 111); the refill word is not described")
    if names[0].startswith("CB"):
        # success: CB with a count that never reaches zero branches every
        # time; no success: its CBZ twin, same count, never branches.
        op = names[0] if succ else names[1]
        tmpl = "%s, $X2, BODY+%%d.%%d%s" % (op, ix)
    elif names[0] in ("BXL", "BAL"):
        # the indicator is set once in the set-up and left on: B<ind>
        # branches every time, BZ<ind> never does.
        if names[0] == "BXL":
            setup.append("KVI, $X2, 9")            # 8 < 9: index low
        else:
            setup += ["L(BU,64,8), ATLONE", "K(BU,64,8), ATLSTD"]   # 1 < std
        op = names[0] if succ else names[1]
        tmpl = "%s, BODY+%%d.%%d%s" % (op, ix)
    else:
        return "no generator for branch row %s" % rec.row
    c = Case(rec, setup, [tmpl], data)
    c.target_per_copy = True
    return c


# --- transmit, PDF 106 / 107 -------------------------------------------------
# PDF 105 (printed 98): "external operands in the two lowest memory boxes ...
# The index operands were in $2 through $14 (18.0 through 30.0)."
def transmit_case(rec):
    n = int(rec.row[:-2])
    src, dst = rec.col.split("_")
    if "int" in (src, dst):
        return ("INTERNAL operands are locations 4.0-9.0 (PDF 105), the "
                "boundary and accumulator registers; not generated")
    where = {"ext": ("(8)10000.0", "(8)50000.0"), "ibox": ("18.0", "18.0")}
    if n > 13 and "ibox" in (src, dst):
        return "more words than $2-$14 hold"
    a = where[src][0]
    b = where[dst][1]
    setup = ["LX, $X1, ATLTC"]
    data = ["ATLTC   XW, 0, %d, 0" % n]
    if rec.instr == "TI":
        if n > 15:
            return "TI's immediate count field holds at most 15"
        line = "TI, %d, %s, %s" % (n, a, b)
    else:
        line = "T, 1, %s, %s" % (a, b)
    return Case(rec, setup, [line], data)


BUILDERS = {"VFL": vfl_case, "FP": fp_case, "IBOX": ibox_case, "IBOX2": ibox_case,
            "BRANCH": branch_case, "TRANSMIT": transmit_case}


def build_cases(pages, pdf=None, col=None, instr=None):
    cases, skipped = [], []
    for p in pages:
        if pdf and p.pdf not in pdf:
            continue
        for r in p.records:
            if col and r.col not in col:
                continue
            if instr and r.instr not in instr:
                continue
            if r.kind != "time":
                skipped.append((r, "the page prints %s, not a time" % r.text))
                continue
            b = BUILDERS.get(r.cls)
            c = b(r) if b else "no generator for class %s" % r.cls
            if isinstance(c, Case):
                cases.append(c)
            else:
                skipped.append((r, c))
    return cases, skipped


def measure_all(cases, jobs=8, progress=True):
    t0 = time.time()
    done = [0]

    def one(c):
        c.measure()
        done[0] += 1
        if progress and done[0] % 50 == 0:
            print("  %d/%d cases, %.0f s" % (done[0], len(cases),
                                             time.time() - t0),
                  file=sys.stderr, flush=True)
    with concurrent.futures.ThreadPoolExecutor(jobs) as ex:
        list(ex.map(one, cases))
    return time.time() - t0


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

def _stats(vals):
    vals = sorted(vals)
    n = len(vals)
    if not n:
        return None
    med = vals[n // 2] if n % 2 else (vals[n // 2 - 1] + vals[n // 2]) / 2
    return dict(n=n, mean=sum(vals) / n, med=med, lo=vals[0], hi=vals[-1],
                mabs=sum(abs(v) for v in vals) / n,
                zero=sum(1 for v in vals if abs(v) <= EXACT))


def report(cases, skipped, elapsed, rows=False, out=sys.stdout):
    w = out.write
    ok = [c for c in cases if c.model is not None]
    bad = [c for c in cases if c.model is None]
    w("ATLAS ORACLE -- model minus Perf. Char. Vol. 2, in clocks of 0.3 us\n")
    w("  (a MEASUREMENT: nothing here passes or fails)\n")
    w("  %d cases measured in %.0f s; %d could not be run; %d transcribed "
      "cells have no generator\n" % (len(ok), elapsed, len(bad), len(skipped)))
    w("  assumptions the volume does not print:\n")
    for a in ASSUMPTIONS:
        w("    - %s\n" % a)
    w("\n")
    if rows:
        w("%-4s %-8s %-10s %-11s %-11s %8s %8s %8s %8s\n" % (
            "pdf", "instr", "block", "row", "column", "print us",
            "print cy", "model cy", "resid cy"))
        for c in ok:
            r = c.rec
            w("%-4d %-8s %-10s %-11s %-11s %8s %8.2f %8.2f %+8.2f\n" % (
                r.pdf, r.instr, r.block[:10], r.row,
                r.col, r.text, c.printed_cycles, c.model, c.residual))
        w("\n")
    w("PER PAGE AND COLUMN  (resid = model - printed, clocks; exact = "
      "|resid| <= %.1f)\n" % EXACT)
    w("%-4s %-8s %-11s %4s %6s %7s %7s %7s %7s %7s\n" % (
        "pdf", "instr", "column", "n", "exact", "mean", "median", "min",
        "max", "mean|r|"))
    groups = {}
    for c in ok:
        groups.setdefault((c.rec.pdf, c.rec.instr, c.rec.col), []).append(c.residual)
    for (pdf, ins, col), v in sorted(groups.items()):
        s = _stats(v)
        w("%-4d %-8s %-11s %4d %6d %+7.2f %+7.2f %+7.2f %+7.2f %7.2f\n" % (
            pdf, ins, col, s["n"], s["zero"], s["mean"], s["med"], s["lo"],
            s["hi"], s["mabs"]))
    s = _stats([c.residual for c in ok])
    if s:
        w("\nALL %d CASES: exact %d (%.0f%%), mean %+.2f, median %+.2f, "
          "range %+.2f .. %+.2f, mean |resid| %.2f clocks (%.2f us)\n" % (
              s["n"], s["zero"], 100.0 * s["zero"] / s["n"], s["mean"],
              s["med"], s["lo"], s["hi"], s["mabs"], s["mabs"] * 0.3))
    if bad:
        w("\nCOULD NOT BE RUN (%d):\n" % len(bad))
        why = {}
        for c in bad:
            why.setdefault(c.error.split(":")[0], []).append(c)
        for k, v in sorted(why.items()):
            w("  %4d  %s   e.g. PDF %d %s %s %s\n" % (
                len(v), k, v[0].rec.pdf, v[0].rec.instr, v[0].rec.row,
                v[0].rec.col))
    if skipped:
        w("\nNO GENERATOR (%d transcribed cells):\n" % len(skipped))
        why = {}
        for r, reason in skipped:
            why[reason] = why.get(reason, 0) + 1
        for k, v in sorted(why.items(), key=lambda kv: -kv[1]):
            w("  %4d  %s\n" % (v, k))


def write_tsv(cases, path):
    with open(path, "w") as f:
        f.write("pdf\tprinted\tinstr\tblock\trow\tcolumn\tprinted_us\t"
                "printed_cycles\tmodel_cycles\tresidual_cycles\tnote\n")
        for c in cases:
            r = c.rec
            f.write("%d\t%d\t%s\t%s\t%s\t%s\t%s\t%.4f\t%s\t%s\t%s\n" % (
                r.pdf, r.printed, r.instr, r.block, r.row, r.col, r.text,
                c.printed_cycles,
                "" if c.model is None else "%.4f" % c.model,
                "" if c.model is None else "%+.4f" % c.residual,
                c.error or ""))


# ---------------------------------------------------------------------------
# The harness's own checks: suspect the probe first
# ---------------------------------------------------------------------------

def _decode_fp_half(v):
    """An FP half-word's fields (enc_fp's layout)."""
    return dict(addr=v >> 14, unnorm=(v >> 13) & 1, abs=(v >> 12) & 1,
                inv=(v >> 11) & 1, code=(v >> 4) & 0x7F, idx=v & 0xF)


def fp_encoding_errors(cases, copies=8):
    """Assemble each FP case's body and decode every copy: the operation
    code, the (N)/(U) bit, the two sign-modifier bits, the operand address
    and the index field must be the ones the page's row and column name.
    Returns a list of (case, message)."""
    from opcodes import FP_CODES
    errs = []
    for c in cases:
        if c.rec.cls != "FP":
            continue
        _, mode, ab, inv = fp_parts(c.rec)
        col, blk = c.rec.col, c.rec.block
        fwd = c.rec.cond.get("forwarding") == "yes"
        if c.rec.instr in ("E+I", "SHF"):
            # the operand is effective-address bits 0-11 (Ref. Manual
            # p.102; StretchExecute's SHF / E+I arms read ea[17:6]), so a
            # literal n sits 7 places up the 18-bit address field
            want_addr = [int(col.split("_")[1].replace("one", "1")) << 7]
            want_idx = 5 if blk == "ADDRESS FIELD IS INDEXED" else 0
        else:
            place = col[3:]
            n = 1 if fwd else 4
            want_addr = {"ext": [FP_EXT_BASE + i for i in range(n)],
                         "ibox": [16 + FP_IBOX_FIRST + i for i in range(n)],
                         "int": [9]}[place]
            want_idx = 5 if col.startswith("ix_") else 0
        full, _ = c.images(copies)
        words = dict(full)
        for i in range(copies):
            w = words[BODY_ADDR + i // 2]
            d = _decode_fp_half((w >> 32) if i % 2 == 0 else (w & 0xFFFFFFFF))
            want = dict(addr=want_addr[i % len(want_addr)],
                        unnorm=int(mode == "U"), abs=ab, inv=inv,
                        code=FP_CODES[c.rec.instr], idx=want_idx)
            if d != want:
                errs.append((c, "copy %d decodes %r, wants %r" % (i, d, want)))
                break
    return errs


def _decode_vfl(w):
    return dict(addr=w >> 40, i1=(w >> 32) & 0xF, p=(w >> 29) & 7,
                fl=(w >> 23) & 0x3F, offset=(w >> 13) & 0x7F,
                code=(w >> 4) & 0x3F, inv=int(bool(w & VFL_INVERT_BIT)))


def vfl_new_encoding_errors(cases):
    """The INTERNL, IMMED. and ACCUM. cases, statically: the address field,
    the addressing mode P, the index and the invert-sign bit are the ones
    PDF 113-114 and the page's row and column name."""
    errs = []
    for c in cases:
        r = c.rec
        if r.cls != "VFL":
            continue
        col = r.col
        place = col[3:]
        if place not in ("int", "int_wbx", "imm", "accum"):
            continue
        full, _ = c.images(2)
        d = _decode_vfl(dict(full)[BODY_ADDR])
        # the bit as assembled, before any XOR: a connective's own code
        # uses it, so the INVERT block is judged by the flip, not the value
        bare = _decode_vfl(_assemble(_program(
            c.setup, c.body(1), c.data, loop=False)).words[BODY_ADDR])
        want = dict(i1=5 if col.startswith("ix_") else 0,
                    inv=bare["inv"] ^ int(r.block == "INVERT SIGN OF INSTRUCTION"))
        if place == "int":
            want.update(addr=8 * 64, p=0)
        elif place == "int_wbx":
            want.update(addr=0o10 * 64 + 0o74, p=0)   # PDF 114: (10.74)8
        elif place == "imm":
            want.update(addr=IMM_ADDR, p=4)
        else:
            # CV is VFL code 27, DCV 59 (opcodes; StretchExecute's arms)
            want.update(p=0, offset=0, code={"CV": 27, "DCV": 59}[r.instr])
            # and the set-up must leave PDF 113's "+1 at offset 20": a
            # 64-bit VFL load (code 5) at offset 20 before the body.  A
            # full-word instruction may start on a half-word, so every
            # pair of consecutive half-words of the set-up is decoded.
            words = dict(full)
            halves = []
            for a in range(START_ADDR, BODY_ADDR):
                if a in words:
                    halves += [words[a] >> 32, words[a] & 0xFFFFFFFF]
            if not any(dd["code"] == 5 and dd["offset"] == 20 and dd["fl"] == 0
                       and dd["p"] == 0
                       for dd in (_decode_vfl((halves[i] << 32) | halves[i + 1])
                                  for i in range(len(halves) - 1))):
                errs.append((c, "no L(BU,64,8) at offset 20 in the set-up"))
                continue
        got = {k: d[k] for k in want}
        if got != want:
            errs.append((c, "decodes %r, wants %r" % (got, want)))
    return errs


def _linearity(case):
    tot = {}
    for copies in (250, 500, 1000):
        full, base = case.images(copies)
        a, b = run_image(full), run_image(base)
        if a is None or b is None:
            return None, None
        tot[copies] = a - b
    return (tot[500] - tot[250]) / 2500.0, (tot[1000] - tot[500]) / 5000.0


def selftest(pages):
    """The things that must hold before any residual is believed.
    Returns the number of failures."""
    fails = 0
    recs = {r.key(): r for p in pages for r in p.records}
    # 0. THE GENERATED FP INSTRUCTIONS ARE THE ONES THE PAGES NAME (static,
    #    no simulation): every one of the 9,406 FP cases, decoded copy by
    #    copy.  The sign modifiers ride on irregular mnemonic suffixes.
    fpc, _ = build_cases(pages, pdf=list(range(42, 102)))
    errs = fp_encoding_errors(fpc)
    ok = not errs and len(fpc) > 9000
    print("%s FP encoding: %d FP cases decoded (op code, N/U, NEG, A, "
          "address, index)%s" % ("ok  " if ok else "FAIL", len(fpc),
                                  "" if ok else "; first: PDF %d %s %s %s %s: %s"
                                  % ((errs[0][0].rec.pdf, errs[0][0].rec.instr,
                                      errs[0][0].rec.block, errs[0][0].rec.row,
                                      errs[0][0].rec.col, errs[0][1])
                                     if errs else (0, "", "", "", "", "too few"))))
    fails += not ok
    r = recs.get((120, "L", "-", "(BU,8,8)", "ni_ext"))
    if r is None:
        print("selftest: PDF 120 L (BU,8,8) ni_ext is not transcribed")
        return 1
    # 1. LINEARITY: the clocks one more copy of the instruction costs must
    #    not depend on how many copies the body holds.  (The per-instruction
    #    FIGURE does shrink slightly with the body, by design: it carries the
    #    ten count branches, as GENER's does -- about 170 clocks over 10,000
    #    instructions, 0.017 of a clock each.)
    tot = {}
    for copies in (250, 500, 1000):
        c = vfl_case(r)
        full, base = c.images(copies)
        tot[copies] = run_image(full) - run_image(base)
    s1 = (tot[500] - tot[250]) / 2500.0
    s2 = (tot[1000] - tot[500]) / 5000.0
    cb = tot[1000] - 10000 * s2
    vals = [tot[1000] / 10000.0]
    ok = abs(s1 - s2) < 1e-9
    print("%s linearity: L(BU,8,8) costs %.4f clocks a copy between 250 and "
          "500 copies, %.4f between 500 and 1000; the ten count branches "
          "cost %.0f clocks in all (%.3f a copy at 1000)"
          % ("ok  " if ok else "FAIL", s1, s2, cb, cb / 10000.0))
    fails += not ok
    # 2. THE IMAGE IS THE ONE THAT RAN: a different instruction must give a
    #    different count through the same binary.
    r2 = recs.get((120, "L", "-", "(BU,64,8)", "ni_ext"))
    v2 = vfl_case(r2).measure()
    ok = abs(v2 - vals[-1]) > 1
    print("%s image is live: L(BU,64,8) = %.3f clocks, L(BU,8,8) = %.3f"
          % ("ok  " if ok else "FAIL", v2, vals[-1]))
    fails += not ok
    # 3. THE COUNT BRANCH IS IN THE FIGURE: the baseline run must be much
    #    shorter than one pass of the body.
    c = vfl_case(r)
    full, base = c.images()
    cf, cb = run_image(full), run_image(base)
    ok = cb < 200 and cf > 100 * cb
    print("%s baseline: %d clocks of set-up and halt against %d for the "
          "sequence" % ("ok  " if ok else "FAIL", cb, cf))
    fails += not ok
    # 4. A SUCCESSFUL BRANCH REACHES EVERY COPY: each copy branches to the
    #    next, so the marginal cost of a copy must again be independent of
    #    the body's length.  (The first generator aimed each copy at the
    #    next WORD; the copies are half-words, so the chain doubled its
    #    stride every branch and ran off the body into data -- 76 clocks a
    #    "branch".  This check fails on that generator.)
    r3 = recs.get((112, "CB CBZ", "-", "CB CBZ", "succ_consec"))
    tot = {}
    for copies in (250, 500, 1000):
        c = branch_case(r3)
        full, base = c.images(copies)
        tot[copies] = run_image(full) - run_image(base)
    s1 = (tot[500] - tot[250]) / 2500.0
    s2 = (tot[1000] - tot[500]) / 5000.0
    ok = abs(s1 - s2) < 1e-9
    print("%s branch chain: a successful CB costs %.4f clocks a copy between "
          "250 and 500 copies, %.4f between 500 and 1000"
          % ("ok  " if ok else "FAIL", s1, s2))
    fails += not ok
    # 5. THE NEW VFL COLUMNS ARE ENCODED AS PDF 113-114 SAY (static):
    #    INTERNL at 8.0 / 8.60, IMMED. with (444444)16 in the address field
    #    and P = 4, ACCUM. (CV, DCV) at offset 0; index and invert bits.
    vc, _ = build_cases(pages, pdf=list(range(116, 190)))
    vc = [c for c in vc
          if c.rec.col[3:] in ("int", "int_wbx", "imm", "accum")]
    errs = vfl_new_encoding_errors(vc)
    ok = not errs and len(vc) > 5000
    print("%s VFL INTERNL / IMMED. / ACCUM. encoding: %d cases decoded%s"
          % ("ok  " if ok else "FAIL", len(vc),
             "" if ok else "; first: %r: %s" % ((errs[0][0].rec, errs[0][1])
                                                 if errs else (None, "too few"))))
    fails += not ok
    # 6. FP LINEARITY, on a STORE to the I-box: four FP copies share two
    #    words and write index registers, so the loop counter ($X15) must
    #    survive and each half-word copy must cost the same at every body
    #    length.  (Proven discriminating: with the I-box operands moved to
    #    $X12-$X15, the stores overwrite the count, the 250-copy run
    #    never halts, and this fails.)
    r4 = recs.get((48, "ST", "NORMALIZED 1.", "(N)", "ni_ibox"))
    s1, s2 = _linearity(fp_case(r4))
    ok = s1 is not None and abs(s1 - s2) < 1e-9 and s1 > 1
    print("%s FP linearity: ST(N) to $X9-$X12 costs %s clocks a copy between "
          "250 and 500 copies, %s between 500 and 1000"
          % ("ok  " if ok else "FAIL",
             "?" if s1 is None else "%.4f" % s1,
             "?" if s2 is None else "%.4f" % s2))
    fails += not ok
    # 7. AN IMMEDIATE CASE RUNS AND IS LINEAR: the XORed address field
    #    must leave a word the model executes, at every body length, and
    #    a copy must cost something.  (Proven discriminating: with the XOR
    #    four bits low, (444444)16 << 36, the body is linear at 0.0000
    #    clocks a copy -- the words do not execute as LI -- and only the
    #    "costs something" clause fails it; it was added for that.)
    r5 = recs.get((173, "LI", "-", "(BU,64,8)", "ni_imm"))
    s1, s2 = _linearity(vfl_case(r5))
    ok = s1 is not None and abs(s1 - s2) < 1e-9 and s1 > 1
    print("%s immediate linearity: LI(BU,64,8) costs %s clocks a copy between "
          "250 and 500 copies, %s between 500 and 1000"
          % ("ok  " if ok else "FAIL",
             "?" if s1 is None else "%.4f" % s1,
             "?" if s2 is None else "%.4f" % s2))
    fails += not ok
    return fails


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--pdf", type=int, action="append", help="only this PDF page")
    ap.add_argument("--col", action="append", help="only this column key")
    ap.add_argument("--instr", action="append", help="only this instruction")
    ap.add_argument("--rows", action="store_true", help="print every case")
    ap.add_argument("--tsv", help="write every case to this file")
    ap.add_argument("--list", action="store_true",
                    help="say what is expressible; run nothing")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--jobs", type=int, default=8)
    ap.add_argument("--rebuild", action="store_true")
    a = ap.parse_args()

    pages = load_atlas()
    cases, skipped = build_cases(pages, a.pdf, a.col, a.instr)
    if a.list:
        report([], skipped, 0)
        print("\n%d cases have a generator" % len(cases))
        return 0
    if a.rebuild or build_needed():
        build()
    if a.selftest:
        return 1 if selftest(pages) else 0
    elapsed = measure_all(cases, a.jobs)
    report(cases, skipped, elapsed, rows=a.rows)
    if a.tsv:
        write_tsv(cases, a.tsv)
    return 0


if __name__ == "__main__":
    sys.exit(main())
