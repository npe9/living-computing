"""IBM 7030 Performance Characteristics (March 8, 1961) — machine-readable timings.

Every number here was read off a 300-dpi (or finer) render of the PDF page
named in its `src` field, with an image reader, NOT off OCR text.  Each entry
carries its own citation so a failing assertion names the page to go re-read.

Units: microseconds, except CLOCK_US itself.  `None` means the cell is blank
on the page.  A string value means the page gives a rule, not a number — the
string is the page's own words.

Companion prose/spec: spec_timing.md in this directory.

Documents:
  V1 = docs/7030_Performance_Characteristics_Vol1_Mar61.pdf   (71 pp)
  V2 = docs/7030_Performance_Characteristics_Vol2_Mar61.pdf   (189 pp)

Page-number offsets, verified from printed footers:
  V1 ch.3:  printed 3-N  = PDF N+18
  V1 ch.4:  printed 4-N  = PDF N+42
  V2 listings:          printed N = PDF N-3
  V2 atlas landscape:   printed N = PDF N-7
Cite V2 by PDF page.
"""

# ---------------------------------------------------------------------------
# 1. The clock
# ---------------------------------------------------------------------------

CLOCK_US = 0.3
"""V1 printed p.3-2, PDF 20: "the basic machine cycles, which is presently
0.3 microsecond"."""

DEC_US = 0.6
"""The "+ dec" of Tables 4-8.  Tables 4-8 only say `dec = decade`
(V1 printed p.3-11, PDF 29, ABBREVIATIONS).  The VALUE comes from
V1 printed p.3-18, PDF 36: "The decoding time of I-box instructions is
0.6 microsecond. Since these instructions are executed in the I-box, the
decoding time has been included in the execution times."
NOTE: the project plan and StretchTiming.bsv cite p.3-17 for this; it is
p.3-18."""

FP_DECODE_RATE_US = 1.2
"""V1 printed p.3-17, PDF 35: "For a sequence of floating point instructions
the decoding rate is one instruction per 1.2 microseconds"."""

VFL_DECODE_MIN_US = 3.6
VFL_DECODE_PER_EXTRA_LEVEL_US = 0.6
VFL_DECODE_PER_INDEXING_US = 0.6
"""V1 printed p.3-18, PDF 36: "The minimum time is 3.6 microseconds which
includes the loading of two LA levels. Each addition[al] level requires an
additional 0.6 microseconds, and each indexing operation requires 0.6
microseconds"."""

IBOX_EBOX_TIME_US = 1.2
"""V1 printed p.3-18, PDF 36: I-box instructions' "E-box time is only
1.2 microseconds"."""

MEMORY_READOUT_US = 1.0
MEMORY_RECYCLE_US = 2.2
MEMORY_SYSTEM_RATE_US = 0.3
"""V1 printed p.3-15, PDF 33: "a 7030 box has a readout time of 1 us and a
recycle time of 2.2 us, yet in the 7030 system information can be obtained at
the rate of one word every 0.3 us"."""

INTERLEAVE_FOUR_BOX_US = 2.2   # four words every 2.2 us
INTERLEAVE_TWO_BOX_US = 4.4    # four words every 4.4 us
"""V1 printed p.3-17, PDF 35."""

# The manual is SILENT on: the value of an I-box control cycle in clocks;
# the LAAR / LAdr / LAMT times that Tables 4-8 add symbolically; the number
# of words a Table 9 "Loop time" covers.

# ---------------------------------------------------------------------------
# 2. TABLE 2. FLOATING POINT INSTRUCTION TIMES  (V1 printed 3-3..3-5, PDF 21-23)
#    Unit: CYCLES of 0.3 us.  Columns verbatim: Instruction | Pre-execution |
#    Execution.
# ---------------------------------------------------------------------------

TABLE2 = {
    # key -> dict(pre_cycles, exec_cycles, pre_extra, exec_extra, src)
    # pre_cycles/exec_cycles are the BASE under the stated condition.
    "ADD_CLASS": dict(
        members=["+", "+MG", "M+", "M+MG", "K", "KMG", "KR", "KMGR"],
        pre_cycles=4, pre_condition="pre shift <= 3",
        pre_extra="1 cycle for each additional pre-shift of 4",
        exec_cycles=1, exec_condition="norm <= 6",
        exec_extra=["2 cycles for each additional norm. of 6",
                    "2 cycles if recomplement is necessary - note 1",
                    "2 cycles if forced zero occurs as result of 'mag.' operation"],
        src="V1 PDF 21 (printed 3-3)"),
    "D+": dict(
        members=["D+", "D+MG", "F+"],
        pre_cycles="Same as Add Class", exec_cycles="Same as Add class",
        exec_extra=["1 cycle if immediate next instruction is floating point"],
        src="V1 PDF 21"),
    "LOAD_CLASS": dict(
        members=["L", "LWF", "LFT", "ST"],
        pre_cycles=2, exec_cycles=1, exec_condition="norm <= 6",
        exec_extra=["2 cycles for each additional norm. of 6"],
        src="V1 PDF 21"),
    "DL": dict(
        members=["DL", "DLWF"],
        pre_cycles=2, exec_cycles=1, exec_condition="norm <= 6",
        exec_extra=["2 cycles for each additional norm of 6",
                    "1 cycle if immediate next instruction is floating point"],
        src="V1 PDF 21"),
    "SRD": dict(members=["SRD"], pre_cycles=3, exec_cycles=1,
                exec_condition="norm <= 6",
                exec_extra=["2 cycles for each additional norm of 6"],
                src="V1 PDF 21"),
    "SLO": dict(members=["SLO"], pre_cycles=2, exec_cycles=17,
                exec_condition="unnormalized",
                exec_extra=["15 cycles if normalized and there are no leading "
                            "zeros in intermediate fraction",
                            "2 cycles for each norm. of 6 or less"],
                src="V1 PDF 21 (prints the opcode as SL-phi)"),
    "SHF": dict(members=["SHF"], pre_cycles=4, pre_condition="shift <= 3",
                pre_extra="1 cycle for each additional shift of 4",
                exec_cycles=1,
                exec_extra=["1 cycle if immediate next operation is floating point"],
                note="Applies to both left and right shift",
                src="V1 PDF 22 (printed 3-4)"),
    "E+": dict(members=["E+", "E+I"], pre_cycles=1, exec_cycles=5,
               exec_condition="norm <= 6",
               exec_extra=["2 cycles for each additional norm. of 6",
                           "1 cycle if immediate next operation is floating point"],
               note="NOTE 2: 'will most likely be changed in the near future "
                    "to three pre-execution and three execution cycles' "
                    "(V1 PDF 24) -- these two numbers are PROVISIONAL",
               src="V1 PDF 22"),
    "*": dict(members=["*"], pre_cycles=5, exec_cycles=4,
              exec_condition="norm. <= 6",
              exec_extra=["2 cycles for each additional norm. of 6"],
              src="V1 PDF 22"),
    "D*": dict(members=["D*"], pre_cycles=5, exec_cycles=4,
               exec_condition="norm <= 6",
               exec_extra=["2 cycles for each additional norm. of 6",
                           "1 cycle if immediate next operation is floating point"],
               src="V1 PDF 22"),
    "*+": dict(members=["*+"], pre_cycles=3,
               pre_note="cannot enter execution cycles until Factor is available",
               exec_cycles=17, exec_condition="pre shift <= 3 and norm <= 6",
               exec_extra=["1 cycle for each additional pre-shift of 4",
                           "2 cycles for each additional norm. of 6",
                           "2 cycles if recomplement is necessary - note 1",
                           "1 cycle if immediate next operation is floating point"],
               src="V1 PDF 22"),
    "R/": dict(members=["R/"], pre_cycles=2, exec_cycles=2,
               exec_extra=["plus all pre-execution and execution cycles of Divide"],
               src="V1 PDF 22"),
    "/": dict(members=["/"], pre_cycles=2, pre_condition="divisor shift <= 6",
              pre_extra="2 cycles for each additional divisor shift of 6",
              exec_cycles=2, exec_condition="dividend shift <= 6",
              exec_extra=["2 cycles for each additional dividend shift of 6 or "
                          "total of 3 cycles if dividend is all zero",
                          "2 cycles for initial reduction loop if dividend is normalized",
                          "3 cycles for initial dividend pass if dividend has leading zeros",
                          "2 cycles for each additional reduction loop "
                          "(number of cycles is data dependent)",
                          "2 cycles if final remainder has to be complemented",
                          "1 cycle - all"],
              zero_divisor=dict(pre_cycles=3, exec_cycles=2,
                                note="3 cycles pre-execution and 2 cycles "
                                     "execution instead of previous"),
              src="V1 PDF 23 (printed 3-5)"),
    "D/": dict(members=["D/"], pre_cycles="Same as Divide",
               exec_cycles="Same as Divide plus 6 cycles (remainder norm <= 6)",
               exec_extra=["2 cycles for each additional remainder norm. of 6"],
               src="V1 PDF 23"),
    "SRT": dict(members=["SRT"], pre_cycles=2, exec_cycles=106,
                exec_condition="norm. <= 6",
                exec_extra=["1 cycle if operation began with a 'B' pulse",
                            "2 cycles for each additional norm of 6"],
                src="V1 PDF 23"),
}

TABLE2_NOTE1 = (
    "When fraction signs are unlike, the operand which is pre-shifted will be "
    "complemented.  Recomplementing will only occur if the complemented "
    "(following pre-shift) fraction is larger in magnitude than unshifted "
    "fraction.  If fraction signs are alike no complementing occurs."
)  # V1 printed p.3-6, PDF 24

TABLE2_NOTE2 = (
    "Add Exponent and Add Immediate to Exponent will most likely be changed in "
    "the near future to three pre-execution and three execution cycles."
)  # V1 printed p.3-6, PDF 24

# ---------------------------------------------------------------------------
# 3. TABLE 3. EQUATIONS FOR SAU INSTRUCTIONS (V1 printed 3-7..3-9, PDF 25-27)
#    Columns verbatim: Operation Code | Pre-execution Time | Execution Time |
#    Termination Time | Full Word Total | Comments.   Unit: microseconds.
# ---------------------------------------------------------------------------

TABLE3_GLOSSARY = {   # V1 printed p.3-10, PDF 28, verbatim
    "DD": "Dividend",
    "DR": "Divisor",
    "DDL": "Dividend length",
    "DRL": "Divisor length",
    'L "0"': "Leading zero's",
    '#L "0"': "Number of leading zero's",
    "DDL or DRL": "Dividend or divisor length which ever is greater",
    "OS": "Offset",
    "FL": "Field length",
    "BS": "Byte size",
    "B - D": "Binary to decimal",
    "D - B": "Decimal to binary",
    "R": "8 in Binary - 4 in decimal",
    "S": "Accumulator field specified by the offset minus all leading zero's",
    "T": "Field length less all zone bits",
    "U": "Result field",
    "V": "96 in binary - 92 in decimal",
    "W": "The number of accumulator significant bits greater than the field length",
    "X": "Field length in unsigned operations - field length minus the byte "
         "size in signed operations",
    "Y": "8 in binary operations and byte size in decimal operations",
    "Z": "One for a carry out of the last x/y byte plus one for a carry out of "
         "each succeeding 8 bit byte in binary or 4 bit byte in decimal",
    "C": "The number of times a carry results from an 8 bit byte in binary or "
         "a 4 bit byte in decimal",
}

TABLE3_SIGNED_RULE = (
    "All equations were developed for unsigned operations.  Signed operations "
    "can be computed by adding .6 microseconds to the pre-execution time.  An "
    "additional .6 microseconds must be added if the result of the operation "
    "requires complementing.  The following operations require no additional "
    "time when signed: SRD, C, CM, CT, CV, DCV, LCV (D-B), LTRCV (D-B), LTRS, "
    "LFT."
)  # V1 printed p.3-6, PDF 24

# (op, pre_us, exec_expr, term_us, full_word_total_us, comment, src)
TABLE3 = [
    ("+",            1.8, ".6(x/y + z)", 0.6, 7.2,
     "Unlike signs CD > AB, add .6(OS/r + x/y + Z + 1) to the execution time.",
     "V1 PDF 25"),
    ("+MG",          1.8, ".6(x/y + z)", 0.6, 7.2,
     "Unlike signs CD > AB, add .6 to the execution time.", "V1 PDF 25"),
    ("L",            1.8, ".6(x/y)", 0.6, 7.2, "", "V1 PDF 25"),
    ("LWF",          1.8, ".6(x/y)", 0.6, 7.2, "", "V1 PDF 25"),
    ("M+",           1.8, ".6(x/y)", 0.6, 7.2,
     "Unlike signs AB > CD, add .6(x/y + 1) to the execution time.", "V1 PDF 25"),
    ("M+MG",         1.8, ".6(x/y)", 0.6, 7.2,
     "Unlike signs AB > CD, add .6(x/y + 1) to the execution time.", "V1 PDF 25"),
    ("M+1",          1.8, ".6(c + 1)", 0.6, 3.0,
     "Unlike signs, execution time = .6(x/y) when true result or .6(2x/y + 1) "
     "when complement result.", "V1 PDF 25"),
    ("ST",           1.8, ".6(x/y)", 0.6, 7.2, "", "V1 PDF 25"),
    ("SRD",          3.0, ".6(x/y)", 0.6, 8.4,
     "No additional time required when operation is signed.", "V1 PDF 25"),
    ("K",            1.8, ".6(x/y + w/r)", 0.6, 7.2, "", "V1 PDF 25"),
    ("KF",           1.8, ".6(x/y)", 0.6, 7.2, "", "V1 PDF 25"),
    ("KE",           1.8, ".6(x/y + w/r)", 0.6, 7.2, "", "V1 PDF 25"),
    ("KFE",          1.8, ".6(x/y)", 0.6, 7.2, "", "V1 PDF 25"),
    ("KR",           1.8, ".6(x/y + w/r)", 0.6, 7.2, "", "V1 PDF 26"),
    ("KFR",          1.8, ".6(x/y)", 0.6, 7.2, "", "V1 PDF 26"),
    ("C",            1.8, ".6(x/y)", 0.6, 7.2, "", "V1 PDF 26"),
    ("CM",           1.8, ".6(x/y)", 0.6, 7.2, "", "V1 PDF 26"),
    ("CT",           1.8, ".6(x/y)", 0.6, 7.2, "", "V1 PDF 26"),
    ("LTRS",         2.4, ".6(v/y + 3)", 0.6, 9.6,
     "If the effective FL is greater than 48 bits, add .6(t/8 - 1) to the "
     "execution time.", "V1 PDF 26"),
    ("LFT",          2.4, ".6(v/y) + 3", 0.6, 9.6,
     "If the effective FL is greater than 48 bits, then add .6(t/8 - 1) to the "
     "execution time.  [NOTE: the page prints the '+ 3' OUTSIDE the "
     "parenthesis for LFT and INSIDE for LTRS, yet gives both the same Full "
     "Word Total 9.6; LTRS's form is the consistent one.]", "V1 PDF 26"),
    ("LCV B-D",      2.4, ".6(x + u/8 + 1)", 0.6, 45.3, "", "V1 PDF 26"),
    ("LCV D-B",      2.4, ".6(x/y + t/4 + u/8 + 4)", 0.6, 14.7, "", "V1 PDF 26"),
    ("LTRCV B-D",    2.4, ".6(x + 3)", 0.6, 29.4,
     "If the converted field length is greater than 48 bits, add "
     ".6(FLc/8 - 1) to the execution time.", "V1 PDF 26"),
    ("LTRCV D-B",    2.4, ".6(x/y + 16)", 0.6, 21.6,
     "If the field length to be converted after all zone bits have been "
     "removed is greater than 48 bits, add .6(t/8 - 1) to the execution time.",
     "V1 PDF 26"),
    ("CV B-D",       2.4, ".6(s + u/8 + 1)", 0.6, 37.2, "", "V1 PDF 26"),
    ("DCV B-D",      2.4, ".6(s + u/8 + 1)", 0.6, 63.0, "", "V1 PDF 27"),
    ("CV D-B",       2.4, ".6(s/4 + 1)", 0.6, 10.8, "", "V1 PDF 27"),
    ("DCV D-B",      2.4, ".6(s/4 + 2)", 0.6, 18.6, "", "V1 PDF 27"),
    ("*",            6.0, "3.9", 0.6, 10.5, "", "V1 PDF 27"),
    ("*+",           7.8, "3.0 + Add exec. time", 0.6, 18.6, "", "V1 PDF 27"),
    ("/",            5.4, "Q", 0.6, 24.0,
     'Q = .6( DR L"0"/6 + (DDL or DRL)/8 + A + (97 - DRL)/8 + 1 ) ; '
     'A = 1. Zero DD - (DDL - DRL)/6 ; '
     '2. Leading zero\'s -(1 + #L"0"/6 + (DDL - DRL - #L"0")/4) ; '
     '3. Complement Result. - Add 1 to A2.', "V1 PDF 27"),
]

# ---------------------------------------------------------------------------
# 4. TABLES 4-9: the I-box times.  Unit: microseconds, BEFORE adding `dec`.
#    Where the page writes a symbolic addend (LAAR, LAdr, LAMT) it is kept as
#    a string in the `extra` list; the manual gives no number for any of them.
# ---------------------------------------------------------------------------

# TABLE 4. I-BOX TIMES - DIRECT INDEX   V1 printed p.3-11, PDF 29
# Columns verbatim: Instruction | Address in EM | Address in XS | Address in IR
TABLE4 = {
    # instr: (EM, XS, IR) where each is (us_or_None, [extras])
    "LX":        ((4.8, []),        (4.8, []),        (4.2, ["LAdr"])),
    "LV,LC,LR":  ((4.2, []),        (4.2, []),        (3.6, ["LAdr"])),
    "SX":        ((1.2, ["LAAR"]),  (4.2, []),        (1.2, ["LAAR"])),
    "SV,SC,SR":  ((4.2, ["LAAR"]),  (5.4, []),        (3.6, ["LAdr", "LAAR"])),
    "SV,SC,SR to TC": ((None, []),  (6.0, ["LAdr"]),  (None, [])),
    "V+":        ((4.2, []),        (4.2, []),        (3.6, ["LAdr"])),
    "V+C":       ((4.2, []),        (4.8, []),        (4.2, ["LAdr"])),
    "V+CR (EM)": ((8.4, []),        (9.0, []),        (8.4, ["LAdr"])),
    "V+CR (XS)": ((7.2, []),        (7.8, []),        (7.2, ["LAdr"])),
    "KV,KC":     ((4.2, []),        (4.2, []),        (3.6, ["LAdr"])),
    "RNX":       ((9.0, ["LAdr", "LAAR"]), (None, []), (None, [])),
    "LVE":       ((7.8, []),        (6.6, []),        (6.6, ["LAdr"])),
    "LVE as object INSN of LVE": ((4.8, ["additional"]), (3.6, ["additional"]),
                                  (3.0, ["additional", "LAdr", "4.2 if LAMT"])),
    "SVA":       ((4.2, ["LAAR"]),  (5.4, []),        (3.6, ["LAdr", "LAAR"])),
    "SVA to TC": ((None, []),       (6.0, ["LAdr"]),  (None, [])),
}
TABLE4_ABBREV = {   # verbatim from the page
    "dec": "decade",
    "LAAR": "Look-ahead address register",
    "LAdr": "Look-ahead drain",
    "LAMT": "Look-ahead empty",
    "TC": "Time clock",
}
TABLE4_SRC = "V1 printed p.3-11, PDF 29"

# TABLE 5. I-BOX TIMES - IMMEDIATE INDEX   V1 printed p.3-11, PDF 29
# Columns verbatim: Instruction | Basic Time | Variations
TABLE5 = {
    "LVI,LCI,LRI,LVNI": (2.4, ""),
    "V+I,V-I":          (2.4, ""),
    "V+IC,V-IC":        (3.0, "Also V +- ICR where Count != 0"),
    "V+ICR,V-ICR":      (7.2, "1.2 usec less if Refill from X5"),
    "C+I,C-I":          (2.4, ""),
    "KVI,KVNI,KCI":     (2.4, ""),
    "LVS":              (5.4, "Additional 1.8 usec per ADD"),
}
TABLE5_SRC = "V1 printed p.3-11, PDF 29"

# TABLE 6. I-BOX TIMES - MISCELLANEOUS   V1 printed pp.3-12/3-13, PDF 30/31
TABLE6 = {
    "R (from EM)":  ((7.8, ["LAAR"]), (7.2, []), (6.6, ["LAAR", "LAdr"])),
    "R (from XS)":  ((5.4, ["LAAR"]), (5.4, []), (4.2, ["LAAR", "LAdr"])),
    "RCZ (C != 0)": ((4.2, []),       (3.0, []), (3.0, ["LAdr"])),
    "Z":            ((1.2, ["LAAR"]), (3.6, []), (1.2, ["LAAR"])),
}
TABLE6_SRC = "V1 printed p.3-12, PDF 30"

# EX: a recipe, not a number (V1 PDF 30).  Step 3's instruction-fetch time
# depends on the address of the executed instruction:
TABLE6_EX_FETCH_US = [
    ("0.0, 0.32",   4.8),
    ("1.0, 1.32",   6.0),
    ("2.0, 2.32",   7.8),
    ("3.0, 3.32",   7.8),
    ("4.0, 4.32",   7.8),
    ("5.0 -> 11.32", 11.2),
    ("12.0, 12.32", 7.8),
    ("13.0 -> 14.32", 5.4),
    ("15.0, 15.32", 4.8),
    ("16.0 -> 30.32", 4.2),
    ("31.0, 31.32", 6.0),
    ("32.0 -> up",  5.4),
]
TABLE6_EX_RECIPE = [
    "Decode time, plus",
    "Always begins with Look-ahead drain, plus",
    "Instruction fetch time as follows: [TABLE6_EX_FETCH_US]",
    "Add decode and execution time for given instruction",
    "Always ends with LA drain, plus",
    "Add 3.0 usec for fetch of next instruction",
]
TABLE6_EXIC_RECIPE = [   # V1 printed p.3-13, PDF 31
    "Decode time, plus",
    "Always begins with a Look-ahead drain; 4.2 usec to fetch the "
    "psuedo-instruction counter are overlapped with the Look-ahead drain if "
    "the ps IC is in EM; 3.0 usec if the ps IC is in XS",
    "Instruction fetch time = 6.0 usec",
    "Stepping of psuedo-instruction counter: add LAAR time if psIC in EM; "
    "add .6 usec time if psIC in XS",
    "Add decode and execution time for given instructions",
    "Always ends with LA drain, plus",
    "Add 3.0 usec for fetch of next instruction",
]

# TABLE 7. I-BOX TIMES - UNCONDITIONAL BRANCH   V1 printed p.3-13, PDF 31
# Columns verbatim: Instruction | Basic Time | SIC to EM | SIC to XS
TABLE7 = {
    "B":   ((3.6, []), (4.8, ["LAAR"]), (4.2, [])),
    "BR":  ((4.8, []), (6.0, ["LAAR"]), (5.4, [])),
    "BE":  ((3.6, ["LAdr (if previously disabled)"]),
            (4.8, ["LAAR", "LAdr (if previously disabled)"]),
            (4.2, ["LAdr (if previously disabled)"])),
    "BEW": ("Setup time as above on BE", None, None),
    "NOP": ((1.2, []), "Same as Basic", "Same as Basic"),
    "BD":  ((4.8, ["2 LA drains"]), (6.0, ["2 LA drains"]), (5.4, ["2 LA drains"])),
}
TABLE7_SRC = "V1 printed p.3-13, PDF 31"

# TABLE 8. I-BOX TIMES - INDEX BRANCHES   V1 printed p.3-14, PDF 32
TABLE8 = {
    "CB (Successful)":   ((4.2, []), (6.6, ["LAAR"]), (7.2, [])),
    "CB (Unsuccessful)": ((3.6, []), (3.6, []),        (3.6, [])),
    "CBR (EM) (Succ)":   ((6.6, []), (9.0, ["LAAR"]), (9.6, [])),
    "CBR (XS) (Succ)":   ((6.0, []), (8.4, ["LAAR"]), (9.0, [])),
    "CBR (EM) (Unsucc)": ((6.0, []), (6.0, []),        (6.0, [])),
    "CBR (XS) (Unsucc)": ((5.4, []), (5.4, []),        (5.4, [])),
}
TABLE8_NOTE = ("CBR behaves like CB if Refill is not to be taken.  "
               "Ex: CBR, branch on count != zero")
TABLE8_SRC = "V1 printed p.3-14, PDF 32"

# TABLE 9. I-BOX TIMES - TRANSMIT INSTRUCTIONS  V1 printed pp.3-14/3-15, PDF 32/33
# Columns verbatim: Instruction | Setup time | Loop time | Termination time
# Setup time is "1.2 usec + dec + LA dr" for EVERY row of both halves.
# THE MANUAL IS SILENT on how many words one "Loop time" covers.
TABLE9_SETUP_US = 1.2
TABLE9_SETUP_EXTRAS = ["dec", "LA dr"]
TABLE9_TRANSMIT = {           # (loop_us, termination_us)
    "T (EM -> EM)": (3.0, 3.6),
    "T (EM -> XS)": (4.2, 0.6),
    "T (XS -> EM)": (3.0, 3.6),
    "T (XS -> XS)": (4.2, 0.6),
    "T (IR -> EM)": (7.2, 3.6),
    "T (IR -> XS)": (7.2, 0.6),
}
TABLE9_TRANSMIT_NOTE = "Transmit to EM and IR identical in time."
TABLE9_SWAP = {
    "S (EM -> EM)": (6.0, 1.8),
    "S (EM -> XS)": (6.6, 1.8),
    "S (EM -> IR)": (9.6, 1.8),
    "S (XS -> EM)": (6.0, 1.8),
    "S (XS -> XS)": (7.2, 1.8),
    "S (XS -> IR)": (10.8, 1.8),
    "S (IR -> EM)": (9.6, 1.8),
    "S (IR -> XS)": (10.2, 1.8),
    "S (IR -> IR)": (15.0, 1.8),
}
TABLE9_SWAP_NOTE = ("The immediate/direct and the forward/backward options do "
                    "not affect the timing of either transmit or swap.")
TABLE9_SRC = "V1 printed pp.3-14/3-15, PDF 32/33"

# ---------------------------------------------------------------------------
# 5. Volume 2's MEASURED atlas.  These are THROUGHPUT times from GENER's
#    thousand-instruction sequences (V2 PDF 37), not isolated latencies.
# ---------------------------------------------------------------------------

V2_METHOD = (
    "A subroutine (GENER) was written to handle the generation of a long "
    "sequence of instructions, the execution of that sequence, the calculation "
    "of execution time, and the conversion and printing of that time. ... This "
    "series is then reproduced until a thousand instructions are available "
    "after which a count branch (with an original count of 10) is inserted."
)  # V2 printed p.34, PDF 37
V2_CAVEAT = ("The following are representative times of 7030 instructions. "
             "They will be updated when more information becomes available.")

# --- I-BOX INSTRUCTIONS, V2 printed p.102, PDF 109 -------------------------
# Column headings verbatim:
#   EXTERNAL OPERAND** INTERNAL OPERAND ** INDEX OPERAND** IMMEDIATE
#   DIRECT  EFFECTIVE  DIRECT  EFFECTIVE  DIRECT  EFFECTIVE
# "EFFECTIVE" = the operand address was indexed (by a register holding zero).
V2_IBOX_COLUMNS = ["ext_direct", "ext_effective", "int_direct", "int_effective",
                   "idx_direct", "idx_effective", "immediate"]
V2_IBOX = {
    # us; None = blank on the page
    "LX":    (5.73, 6.33, 6.93, 7.53, 5.72, 6.33, None),
    "LV":    (5.42, 5.87, 5.88, 6.48, 5.27, 5.87, 3.31),
    "LC":    (5.42, 5.87, 5.88, 6.48, 5.27, 5.87, 3.31),
    "LR":    (5.42, 5.87, 5.88, 6.48, 5.27, 5.87, 3.31),
    "SX":    (3.46, 3.61, 3.01, 3.31, 5.12, 5.73, None),
    "SV":    (7.81, 7.82, 7.83, 7.83, 6.33, 6.93, None),
    "SC":    (7.81, 7.82, 7.83, 7.83, 6.33, 6.93, None),
    "SR":    (7.81, 7.82, 7.83, 7.83, 6.33, 6.93, None),
    "V+":    (5.27, 5.87, 5.87, 6.48, 5.27, 5.87, 3.31),
    "V+C":   (5.27, 5.87, 5.87, 6.48, 5.87, 6.48, 3.92),
    "V+CR_unsuccessful": (5.27, 5.88, 5.88, 6.48, 5.88, 6.48, 3.92),
    "V+CR_successful":   (9.34, 9.94, 9.94, 10.54, 9.94, 10.54, 8.13),
    "KV":    (5.27, 5.87, 5.87, 6.48, 5.27, 5.87, 3.31),
    "KC":    (5.27, 5.87, 5.87, 6.48, 5.27, 5.87, 3.31),
    "LVNI":  (None, None, None, None, None, None, 3.31),
    "V-I":   (None, None, None, None, None, None, 3.31),
    "V-IC":  (None, None, None, None, None, None, 3.92),
    "V-ICR_unsuccessful": (None, None, None, None, None, None, 3.92),
    "V-ICR_successful":   (None, None, None, None, None, None, 8.13),
    "C+I":   (None, None, None, None, None, None, 3.31),
    "C-I":   (None, None, None, None, None, None, 3.31),
    "KVNI":  (None, None, None, None, None, None, 3.31),
    "R":     (11.42, 11.43, 10.83, 10.84, 7.68, 8.29, None),
    "RCZ_a": (5.27, 5.87, 5.87, 6.48, 4.07, 4.67, None),
    "RCZ_b": (11.42, 11.43, 10.83, 10.84, 7.68, 8.29, None),
    "RNX":   (12.96, 13.56, None, None, None, None, None),
}
V2_IBOX_SRC = "V2 printed p.102, PDF 109 (read at 300 dpi; the EXTERNAL/" \
              "INTERNAL columns re-verified at 500 dpi on a crop, and the " \
              "INDEX/IMMEDIATE columns likewise)"
V2_IBOX_NOTES = (
    "The page prints two unlabelled V+CR rows and two unlabelled RCZ rows. "
    "V2 printed p.101 (PDF 108) says 'Conditional refill operations were "
    "tested for both conditions', so the two V+CR rows are refill-not-taken "
    "and refill-taken; the labels here are that inference and are NOT on the "
    "page.  The same is true of RCZ_a/RCZ_b."
)

# --- VFL M+, V2 printed p.110, PDF 117 -------------------------------------
# Heading verbatim: VFL INSTRUCTION M+   NO FORWARDING   DIRECT ADDRESSING
#                   OFFSET 0   INSTRUCTION AT FULL WORD ADDRESS
# Column headings verbatim, under NO INDEXING then INDEXING:
#   EXTERNL OPERAND | EXTERNL WB XOVR | I-BOX OPERAND | INTERNL OPERAND |
#   INTERNL WB XOVR
V2_VFL_COLUMNS = ["ni_ext", "ni_ext_wbx", "ni_ibox", "ni_int", "ni_int_wbx",
                  "ix_ext", "ix_ext_wbx", "ix_ibox", "ix_int", "ix_int_wbx"]
V2_VFL_MPLUS = {
    # (mode, field length, byte size) -> the ten columns.  The two INTERNL
    # columns are blank throughout this page.
    ("BU", 1, 8):  (6.63, None, 10.88, None, None, 6.92, None, 11.48, None, None),
    ("BU", 8, 8):  (6.63, 15.96, 10.88, None, None, 6.92, 15.97, 11.48, None, None),
    ("BU", 16, 8): (6.93, 16.56, 11.48, None, None, 7.23, 16.57, 12.09, None, None),
    ("BU", 32, 8): (7.84, 17.76, 12.69, None, None, 7.84, 17.77, 13.30, None, None),
    ("BU", 48, 8): (9.02, 18.97, 13.90, None, None, 9.03, 18.98, 14.51, None, None),
    ("BU", 64, 8): (9.61, 19.57, 14.51, None, None, 9.62, 19.58, 15.11, None, None),
    ("B", 1, 1):   (6.63, None, 10.88, None, None, 6.93, None, 11.48, None, None),
    ("B", 8, 1):   (6.93, 16.56, 11.48, None, None, 7.23, 16.57, 12.09, None, None),
    ("B", 16, 1):  (7.23, 17.16, 12.09, None, None, 7.53, 17.17, 12.69, None, None),
    ("B", 32, 1):  (8.42, 18.36, 13.29, None, None, 8.44, 18.38, 13.90, None, None),
    ("B", 48, 1):  (9.61, 19.57, 14.51, None, None, 9.62, 19.58, 15.11, None, None),
    ("B", 64, 1):  (10.80, 20.78, 15.72, None, None, 10.81, 20.79, 16.32, None, None),
    ("DU", 4, 4):  (6.63, None, 10.88, None, None, 6.92, None, 11.48, None, None),
    ("DU", 8, 4):  (6.93, 16.56, 11.48, None, None, 7.23, 16.57, 12.09, None, None),
    ("DU", 16, 4): (7.84, 17.77, 12.69, None, None, 7.84, 17.77, 13.29, None, None),
    ("DU", 32, 4): (10.21, 20.17, 15.11, None, None, 10.22, 20.18, 15.72, None, None),
    ("DU", 48, 4): (12.60, 22.58, 17.53, None, None, 12.60, 22.59, 18.13, None, None),
    ("DU", 64, 4): (14.40, 24.39, 19.34, None, None, 14.40, 24.40, 19.94, None, None),
    ("D", 4, 4):   (6.63, None, 10.88, None, None, 6.93, None, 11.48, None, None),
    ("D", 8, 4):   (6.93, 16.56, 11.48, None, None, 7.23, 16.57, 12.09, None, None),
    ("D", 16, 4):  (7.84, 17.76, 12.69, None, None, 7.84, 17.77, 13.29, None, None),
    ("D", 32, 4):  (10.21, 20.17, 15.11, None, None, 10.22, 20.19, 15.72, None, None),
    ("D", 48, 4):  (12.60, 22.58, 17.53, None, None, 12.60, 22.59, 18.13, None, None),
    ("D", 64, 4):  (15.01, 24.99, 19.94, None, None, 15.00, 25.00, 20.55, None, None),
}
V2_VFL_MPLUS_INVERT_SIGN = {
    # second block on the same page, headed "INVERT SIGN OF INSTRUCTION"
    ("BU", 1, 8):  (7.23, None, 12.09, None, None, 7.53, None, 12.69, None, None),
    ("BU", 8, 8):  (7.23, 17.16, 12.09, None, None, 7.53, 17.17, 12.69, None, None),
    ("BU", 16, 8): (8.42, 18.36, 13.30, None, None, 8.44, 18.38, 13.90, None, None),
    ("BU", 32, 8): (10.80, 20.78, 15.72, None, None, 10.81, 20.79, 16.32, None, None),
    ("BU", 48, 8): (13.20, 23.18, 18.13, None, None, 13.20, 23.20, 18.74, None, None),
    ("BU", 64, 8): (12.31, 22.95, 17.22, None, None, 12.31, 22.97, 17.83, None, None),
    ("B", 1, 1):   (6.63, None, 10.88, None, None, 6.92, None, 11.48, None, None),
    ("B", 8, 1):   (6.93, 16.56, 11.49, None, None, 7.23, 16.57, 12.09, None, None),
    ("B", 16, 1):  (7.23, 17.16, 12.09, None, None, 7.53, 17.17, 12.69, None, None),
    ("B", 32, 1):  (8.43, 18.36, 13.30, None, None, 8.44, 18.38, 13.90, None, None),
    ("B", 48, 1):  (9.62, 19.57, 14.51, None, None, 9.62, 19.58, 15.11, None, None),
    ("B", 64, 1):  (10.80, 20.78, 15.71, None, None, 10.81, 20.79, 16.32, None, None),
    ("DU", 4, 4):  (7.23, None, 12.09, None, None, 7.53, None, 12.69, None, None),
    ("DU", 8, 4):  (8.42, 18.36, 13.30, None, None, 8.44, 18.38, 13.90, None, None),
    ("DU", 16, 4): (10.80, 20.77, 15.72, None, None, 10.81, 20.79, 16.32, None, None),
    ("DU", 32, 4): (15.60, 25.59, 20.55, None, None, 15.61, 25.60, 21.15, None, None),
    ("DU", 48, 4): (20.40, 30.41, 25.38, None, None, 20.40, 30.43, 25.98, None, None),
    ("DU", 64, 4): (19.51, 30.78, 24.48, None, None, 19.51, 30.80, 25.08, None, None),
    ("D", 4, 4):   (6.63, None, 10.88, None, None, 6.93, None, 11.48, None, None),
    ("D", 8, 4):   (6.93, 16.56, 11.48, None, None, 7.23, 16.57, 12.09, None, None),
    ("D", 16, 4):  (7.84, 17.77, 12.69, None, None, 7.84, 17.77, 13.30, None, None),
    ("D", 32, 4):  (10.21, 20.17, 15.11, None, None, 10.22, 20.19, 15.71, None, None),
    ("D", 48, 4):  (12.60, 22.58, 17.53, None, None, 12.60, 22.59, 18.13, None, None),
    ("D", 64, 4):  (15.01, 24.99, 19.95, None, None, 15.01, 25.01, 20.55, None, None),
}
V2_VFL_MPLUS_SRC = "V2 printed p.110, PDF 117, read at 300 dpi"
V2_VFL_MPLUS_PF_ROWS = [("B", 1, 1), ("D", 4, 4)]  # both blocks: a 'PF' mark
                                                   # appears at the right of
                                                   # these rows; the page does
                                                   # not define 'PF'.

# ---------------------------------------------------------------------------
# 6. TABLE 10 — the benchmark operation mixes.  V1 printed p.4-9, PDF 51.
#    THREE CELLS OF THIS TABLE DO NOT ADD UP; see spec_timing.md §3.1.
# ---------------------------------------------------------------------------

TABLE10_COLUMNS = ["A0", "pseudo_j_level", "A1", "Modified", "A2",
                   "Grid Param.", "Elem 1st Form", "Elem 2nd Form"]

TABLE10 = {
    "Fl. Pt.": {
        "LFT": (144, None, None, None, None, 39, None, None),
        "L":   (257, 1, 437, 633, 651, 243, 7, 7),
        "ST":  (261, 1, 465, 659, 677, 202, 15, 15),
        "+":   (250, None, 394, 581, 581, 195, 28, 28),
        "*":   (220, None, 434, 637, 637, 187, 26, 26),
        "/":   (88, None, 42, 51, 51, 42, 2, 2),
        "*+":  (144, None, None, None, None, 39, None, None),
        "D*":  (None, None, None, None, None, None, 2, None),
        "K":   (None, None, None, None, None, 45, 2, 2),
        "SHF": (None, None, None, None, None, None, 2, None),
        "E+":  (None, None, None, None, None, 69, 4, 4),
        "SRT": (None, None, None, None, None, 4, None, None),
        "Total": (1364, 2, 1772, 2561, 2597, 1065, 88, 84),
    },
    "VFL": {
        "L":   (10, 8, 10, 9, 9, 128, 4, 2),
        "ST":  (2, None, 2, 1, 1, 93, 6, 2),
        "+":   (20, 18, 20, 19, 19, 20, None, None),
        "CM":  (66, 66, 70, 71, 71, 9, None, None),
        "*":   (None, None, None, None, None, 8, None, None),
        "LFT": (None, None, None, None, None, 4, None, None),
        "*+":  (None, None, None, None, None, 4, None, None),
        "-MG": (None, None, None, None, None, 4, None, None),
        "M+1": (None, None, None, None, None, 37, None, None),
        "K":   (None, None, None, None, None, 64, None, None),
        "Total": (98, 92, 102, 100, 100, 371, 10, 4),
    },
    "Indexing": {
        "LZ,LV,LC,SV": (13, 9, 13, 11, 11, 6, None, None),
        "V+":  (60, None, 60, 78, 78, 117, None, None),
        "CB":  (15, 1, 15, 20, 20, 13, None, None),
        "KCI": (12, None, 12, 18, 18, None, None, None),
        "Total": (100, 10, 100, 127, 127, 136, 0, 0),
    },
    "Branching": {
        "B,BD,BEW": (77, 5, 68, 91, 91, 6, 8, 10),
        "BIND": (18, None, 18, 27, 27, 274, 3, 3),
        "BB":   (2, None, 2, 1, 1, 1, None, None),
        "Total": (97, 5, 88, 119, 119, 280, 11, 13),  # Grid col: 6+274+1=281
    },
    "Miscell.": {
        "Z,TI Total": (52, None, 28, 38, 29, 31, 1, 1),
    },
}
TABLE10_GRAND_TOTAL = (1711, 109, 2090, 2945, 2972, 1883, 114, 106)
TABLE10_EXEC_TIME_MS = (5.98, 0.7, 5.57, 7.045, 7.0135, 7.07, 0.38, 0.309)
TABLE10_AVG_US_PER_OP = (3.5, 6.4, 2.7, 2.4, 2.36, 3.8, 3.3, 2.9)
TABLE10_SRC = "V1 printed p.4-9, PDF 51 (re-verified at 400/500 dpi on crops)"
TABLE10_DEFECTS = [
    "Grid Param. Branching: 6+274+1 = 281, printed Total = 280; the printed "
    "Grand Total 1883 is consistent with 280.",
    "Elem 1st Form Grand Total printed 114; section totals sum to 110.",
    "Elem 2nd Form Grand Total printed 106; section totals sum to 102.",
]
TABLE10_BUCKETS = (
    "V1 printed p.4-8, PDF 50: 'certain similar operations have been grouped "
    "together (e.g., / and R/; V+, V-, V+I, V-I; +, M+ under Fl. Pt.)'.  So "
    "these row labels are BUCKETS, not opcodes."
)

# ---------------------------------------------------------------------------
# 7. Published benchmark times (V1 ch.4)
# ---------------------------------------------------------------------------

BENCHMARKS = {
    "GERB2": dict(
        what="Inversion of Hilbert matrix segments, Jordan's elimination; "
             "determinant evaluated as a by-product",
        times_s={10: 0.02, 20: 0.14, 30: 0.43, 40: 0.99, 50: 1.89,
                 60: 3.23, 70: 5.10, 80: 7.55, 90: 10.69, 100: 14.61},
        src="V1 printed p.4-1, PDF 43",
        source_listing="V2 PDF 4-8 (printed 1-5)",
        runnable=False,
        blockers=["DL (load double) and D/ (divide double) are the inner "
                  "loop -- read off V2 PDF 4",
                  "*+ not implemented (named on V1 printed p.4-1)",
                  "SRD, SVA, T not implemented"]),
    "MXM16": dict(
        what="Multiplication of two nxn matrices; elements all normalized "
             "floating point 1.0, in upper memory (32768.0 and beyond); "
             "n = 17k+m",
        times_s={25: 0.20, 50: 1.35, 75: 4.74, 100: 10.71, 125: 21.44},
        also="A simple version from the 7030 programming example book requires "
             "15.5 seconds for 100x100 matrices",
        src="V1 printed p.4-3, PDF 45",
        source_listing="V2 PDF 10-16 (printed 7-13)",
        runnable="closest",
        blockers=["7-page listing with a GENER-based test driver",
                  "inner loop unrolled 17 ways"]),
    "PRIMC": dict(
        what="Sieve of Eratosthenes over octal 17740.40 .. 272777.63 using VFL "
             "arithmetic and automatic program interruption; largest prime "
             "(52,307,665) octal, about 11 million",
        time_s=106.7,
        variant_s=102.7,
        variant_note="replacing the progressive indexing by ordinary indexing "
                     "and adding a V + I instruction",
        src="V1 printed p.4-4, PDF 46",
        source_listing="V2 PDF 18-21 (printed 15-18)",
        runnable=False,
        blockers=["2/3 of the program is an interruption table",
                  "loop exit IS an interrupt (upper memory boundary exceeded)",
                  "uses the boundary control feature"]),
    "MonteCarlo": dict(
        what="Particles through a right-angle bent pipe (Davis, J. Appl. Phys. "
             "1960); exit-area distribution as a function of entry area",
        particles=10000, time_s=33.0,
        src="V1 printed p.4-6, PDF 48",
        source_listing="V2 PDF 22-36 (printed 19-33)",
        runnable=False,
        blockers=["20 cards had to be loaded (contents not printed)",
                  "36 numbers printed on line",
                  "SRT, / not implemented"]),
    "Weather": dict(
        what="One floating-point meteorological variable at a ground point and "
             "four at each vertical k-level; non-linear integro-differential",
        runs_ms={
            "1 AO lower memory": 6.4,
            "2 pseudo j-level lower memory": 0.7,
            "3 AO upper memory": 6.13,
            "4 AO lower(instr)+upper(data)": 5.98,
            "5 A1 lower(instr)+upper(data)": 5.57,
            "6 A1 Modified lower(instr)+upper(data)": 7.045,
            "7 A2 lower(instr)+upper(data)": 7.0135,
        },
        grid_parameters_ms=7.07,   # N = 3, lower memory
        elementary_function_ms=(0.38, 0.309),   # 1st form, 2nd form
        size_runs_1345="one pseudo j-level, two i-levels, three k-levels per i-level",
        size_runs_67="greatly reduced pseudo-j-level, one i-level, nine k-levels",
        src="V1 printed pp.4-6..4-8, PDF 48-50",
        source_listing=None,
        runnable=False,
        blockers=["NO SOURCE LISTING EXISTS in either volume"]),
}

# ---------------------------------------------------------------------------
# 8. Derived: the budget StretchTiming.bsv computes, for comparison.
#    This mirrors bsv/StretchTiming.bsv so a test can diff the two.
# ---------------------------------------------------------------------------

def stretch_timing_ibox_us(table_us, dec_us=DEC_US):
    """Tables 4-8 'basic time + dec' in microseconds."""
    return table_us + dec_us


def stretch_timing_sau_us(field_length, byte_size, signed, decimal):
    """Table 3's generic SAU shape (pre 1.8 + .6*(x/y) + term .6), with the
    p.3-10 x and y.  This is what StretchTiming.eboxClocks implements for the
    VFL arithmetic class."""
    x = field_length if not signed else max(field_length - byte_size, 0)
    y = byte_size if decimal else 8
    import math
    bytes_ = math.ceil(x / y) if y else 0
    return 1.8 + 0.6 * bytes_ + 0.6


# ---------------------------------------------------------------------------
# 9. Volume 2's measured BRANCH table.  V2 printed p.105, PDF 112.
#    Heading verbatim: BRANCHING CB BIND  NO FORWARDING  DIRECT ADDRESSING
#                      INSTRUCTION AT FULL WORD ADDR
#    Column groups verbatim: NO INDEXING | BRANCH ADDRESS INDEX
#    Columns verbatim: SUCCES CONSEC | UNSUCC CONSEC | SUCCES NONCON |
#                      UNSUCC NONCON   (repeated for the indexed group)
#
#    V2 printed p.104, PDF 111, defines the conditions:
#      "'Consecutive' means that each instruction called for a branch to the
#       next instructions.  'Non-consecutive' means that the branch was to a
#       location from one to four instructions from the one being executed."
#      "For CBR type, the 'success' refers to a successful refill in which the
#       register is refilled with its original contents.  A one was in the
#       count field.  For an unsuccessful CBR the branch was unsuccessful and
#       thus no refill.  The original count in the count field in this case
#       was greater than 10,000."
#      "The right-most four columns of data involved indexed addresses."
V2_BRANCH_COLUMNS = ["succ_consec", "unsucc_consec", "succ_noncon",
                     "unsucc_noncon", "ix_succ_consec", "ix_unsucc_consec",
                     "ix_succ_noncon", "ix_unsucc_noncon"]
V2_BRANCH = {
    "CB CBZ":     (4.82, 4.52, 4.82, 4.52, 5.12, 5.12, 5.12, 5.12),
    "CB+ CBZ+":   (4.82, 4.52, 4.82, 4.52, 5.12, 5.12, 5.12, 5.12),
    "CB- CBZ-":   (4.82, 4.52, 4.82, 4.52, 5.12, 5.12, 5.12, 5.12),
    "CBH CBZH":   (4.82, 4.52, 4.82, 4.52, 5.12, 5.12, 5.12, 5.12),
    "CBR":        (11.14, 4.52, 11.14, 4.52, 11.44, 5.12, 11.44, 5.12),
    "CBR+":       (11.14, 4.52, 11.14, 4.52, 11.44, 5.12, 11.44, 5.12),
    "CBR-":       (11.14, 4.52, 11.14, 4.52, 11.44, 5.12, 11.44, 5.12),
    "CBRH":       (11.14, 4.52, 11.14, 4.52, 11.44, 5.12, 11.44, 5.12),
    # BIND, I-BOX IND  -- branch on an index indicator, resolved in the I-box
    "BXL BZXL":   (4.52, 2.26, 4.52, 2.26, 4.67, 2.86, 4.67, 2.86),
    # BIND, ARITH RESULT IND -- branch on an arithmetic indicator
    "BAL BZAL":   (19.78, 7.20, 19.78, 7.20, 20.08, 7.21, 20.08, 7.21),
}
V2_BRANCH_SRC = "V2 printed p.105, PDF 112"
V2_BRANCH_KEY_FINDING = (
    "A branch on an ARITHMETIC indicator costs 19.78 us taken and 7.20 us not "
    "taken; a branch on an INDEX indicator costs 4.52 / 2.26.  That is the "
    "number StretchTiming.bsv's flat `BranchInd: 6` (= 3.6 us for both) is "
    "missing, and the 19.78 - 7.20 = 12.58 us gap is the cost of the "
    "not-taken guess going wrong that plan section 6d needs."
)

# ---------------------------------------------------------------------------
# 10. Volume 2's measured TRANSMIT table.  V2 printed p.99, PDF 106.
#     Heading verbatim: TRANSMIT.  Columns verbatim:
#       EXTERNAL TO EXTERNAL | EXTERNAL TO INTERNAL | EXTERNAL TO I-BOX |
#       INTERNAL TO INTERNAL | INTERNAL TO EXTERNAL | INTERNAL TO I-BOX |
#       I-BOX TO I-BOX | I-BOX TO EXTERNAL | I-BOX TO INTERNAL
#     Rows are word counts: 1WD, 3WD, 5WD, 7WD, 9WD, 11WD, 13WD, 15WD.
#     V2 printed p.98, PDF 105: "The transmit instructions were timed with the
#     external operands in the two lowest memory boxes and the internal
#     operands in locations 4.0 through 9.0.  The index operands were in $2
#     through $14 (18.0 through 30.0)." / "LA is emptied before the actual
#     transmission of information."
V2_TRANSMIT_COLUMNS = ["ext_ext", "ext_int", "ext_ibox", "int_int", "int_ext",
                       "int_ibox", "ibox_ibox", "ibox_ext", "ibox_int"]
V2_TRANSMIT = {
    1:  (13.84, 13.85, 13.28, 14.47, 14.47, 13.28, 13.28, 13.85, 13.85),
    3:  (19.89, 19.90, 21.69, 14.47, 14.47, 13.28, 13.28, 13.85, 13.85),
    5:  (25.94, 25.94, 30.16, 14.46, 14.47, 13.28, 13.28, 13.85, 13.85),
    7:  (31.97, None, 38.58, None, None, None, 13.27, 13.85, None),
    9:  (37.99, None, 47.00, None, None, None, 13.27, 13.85, None),
    11: (43.99, None, 55.46, None, None, None, 13.27, 13.85, None),
    13: (50.04, None, 63.87, None, None, None, None, 13.85, None),
    15: (56.07, None, None, None, None, None, None, None, None),
}
V2_TRANSMIT_SRC = "V2 printed p.99, PDF 106"
V2_TRANSMIT_SETTLES_TABLE9 = (
    "Table 9 (V1 PDF 32) gives T (EM -> EM) a 'Loop time' of 3.0 us and does "
    "not say what the loop covers.  The measured EXTERNAL TO EXTERNAL column "
    "rises 13.84, 19.89, 25.94, 31.97, 37.99, 43.99, 50.04, 56.07 for 1, 3, 5, "
    "7, 9, 11, 13, 15 words: a slope of 6.04 us per TWO words, i.e. 3.02 us "
    "per word.  So Table 9's 'Loop time' is PER WORD.  This is an inference "
    "from the slope, not a statement on the page: the manual is silent."
)


# ---------------------------------------------------------------------------
# 11. Volume 2's measured CONNECTIVE page.  V2 printed p.133, PDF 140.
#     Heading verbatim: VFL INSTRUCTION C(0011)   NO FORWARDING
#       DIRECT ADDRESSING   OFFSET 0   INSTRUCTION AT FULL WORD ADDRESS
#     Same ten columns as V2_VFL_COLUMNS.  The INTERNL columns are blank.
#
#     THIS IS THE DECISIVE PAGE FOR THE CONNECTIVE BYTE COUNT: it varies the
#     BYTE SIZE at fixed field length, and the time changes with it.  So the
#     divisor is the DECLARED byte size, not the glossary's binary y = 8.
#     StretchTiming.bsv's ceil(len / byte size) is confirmed on 34 of 35 rows
#     to within 0.01 us -- see check_connective_byte_count() below.
V2_VFL_C0011 = {
    # (mode, FL, BS) -> ten columns, as V2_VFL_COLUMNS
    ("BU", 8, 1):  (8.40, 9.60, 8.40, None, None, 8.40, 9.60, 8.40, None, None),
    ("BU", 8, 2):  (6.00, 7.21, 6.00, None, None, 6.00, 7.21, 6.00, None, None),
    ("BU", 8, 3):  (5.40, 6.62, 5.40, None, None, 5.40, 6.92, 5.40, None, None),
    ("BU", 8, 4):  (4.80, 6.32, 4.80, None, None, 4.82, 6.77, 4.80, None, None),
    ("BU", 8, 5):  (4.80, 6.32, 4.80, None, None, 4.82, 6.77, 4.80, None, None),
    ("BU", 8, 6):  (4.80, 6.32, 4.80, None, None, 4.82, 6.77, 4.80, None, None),
    ("BU", 8, 7):  (4.80, 6.32, 4.80, None, None, 4.82, 6.77, 4.80, None, None),
    ("BU", 8, 8):  (4.20, 6.32, 4.20, None, None, 4.82, 6.77, 4.22, None, None),
    ("BU", 16, 1): (13.20, 14.40, 13.20, None, None, 13.20, 14.40, 13.20, None, None),
    ("BU", 16, 2): (8.40, 9.60, 8.40, None, None, 8.40, 9.60, 8.40, None, None),
    ("BU", 16, 3): (7.20, 8.40, 7.20, None, None, 7.20, 8.40, 7.20, None, None),
    ("BU", 16, 4): (6.00, 7.21, 6.00, None, None, 6.00, 7.21, 6.00, None, None),
    ("BU", 16, 5): (6.00, 7.21, 6.00, None, None, 6.00, 7.21, 6.00, None, None),
    ("BU", 16, 6): (5.40, 6.62, 5.40, None, None, 5.40, 6.92, 5.40, None, None),
    ("BU", 16, 7): (5.40, 6.62, 5.40, None, None, 5.40, 6.92, 5.40, None, None),
    ("BU", 16, 8): (4.80, 6.32, 4.80, None, None, 4.82, 6.77, 4.80, None, None),
    ("BU", 32, 1): (13.20, 14.41, 13.20, None, None, 13.20, 14.40, 13.20, None, None),
    ("BU", 32, 2): (13.20, 14.41, 13.20, None, None, 13.20, 14.40, 13.20, None, None),
    ("BU", 32, 3): (10.20, 11.40, 10.20, None, None, 10.20, 11.41, 10.20, None, None),
    ("BU", 32, 4): (8.40, 9.60, 8.40, None, None, 8.40, 9.60, 8.40, None, None),
    ("BU", 32, 5): (7.80, 9.00, 7.80, None, None, 7.80, 9.00, 7.80, None, None),
    ("BU", 32, 6): (7.20, 8.40, 7.20, None, None, 7.20, 8.40, 7.20, None, None),
    ("BU", 32, 7): (6.60, 7.80, 6.60, None, None, 6.60, 7.80, 6.60, None, None),
    ("BU", 32, 8): (6.00, 7.21, 6.00, None, None, 6.00, 7.21, 6.00, None, None),
    ("BU", 48, 3): (13.20, 14.41, 13.20, None, None, 13.20, 14.40, 13.20, None, None),
    ("BU", 48, 4): (10.80, 12.01, 10.80, None, None, 10.80, 12.01, 10.80, None, None),
    ("BU", 48, 5): (9.60, 10.80, 9.60, None, None, 9.60, 10.80, 9.60, None, None),
    ("BU", 48, 6): (8.40, 9.60, 8.40, None, None, 8.40, 9.60, 8.40, None, None),
    ("BU", 48, 7): (7.80, 9.00, 7.80, None, None, 7.80, 9.00, 7.80, None, None),
    ("BU", 48, 8): (7.20, 8.40, 7.20, None, None, 7.20, 8.40, 7.20, None, None),
    ("BU", 64, 4): (13.20, 14.41, 13.20, None, None, 13.20, 14.40, 13.20, None, None),
    ("BU", 64, 5): (11.40, 12.60, 11.40, None, None, 11.40, 12.60, 11.40, None, None),
    ("BU", 64, 6): (10.20, 11.40, 10.20, None, None, 10.20, 11.40, 10.20, None, None),
    ("BU", 64, 7): (9.60, 10.80, 9.60, None, None, 9.60, 10.80, 9.60, None, None),
    ("BU", 64, 8): (8.40, 9.60, 8.40, None, None, 8.40, 9.60, 8.40, None, None),
}
V2_VFL_C0011_SRC = "V2 printed p.133, PDF 140"
V2_VFL_C0011_OMITTED = [("BU", 48, 1), ("BU", 48, 2), ("BU", 64, 1),
                        ("BU", 64, 2), ("BU", 64, 3)]
V2_VFL_C0011_CAP_INFERENCE = (
    "Every combination the page omits needs MORE than 16 bytes (48/1=48, "
    "48/2=24, 64/1=64, 64/2=32, 64/3=22), and the one row present that needs "
    "more, (BU,32,1) at 32 bytes, is measured at 13.20 us -- identical to "
    "(BU,32,2), (BU,48,3) and (BU,64,4), all of which need exactly 16.  So "
    "the SAU byte count is CAPPED AT 16, which is the width of its first "
    "byte-extraction switch matrix (Buchholz fig.14.6).  The manual never "
    "states this; it is an inference from the hole in the table."
)


def check_connective_byte_count(column=0, verbose=False):
    """Reproduce the C5 finding: StretchTiming's connective byte count,
    ceil(field length / DECLARED byte size), reproduces V2 PDF 140 with a
    constant 2.40 us offset on every row whose byte count is <= 16.

    Returns (n_matching, n_total, outliers)."""
    import math
    ok, outliers = 0, []
    rows = [(k, v[column]) for k, v in V2_VFL_C0011.items() if v[column] is not None]
    for (mode, fl, bs), meas in rows:
        b = math.ceil(fl / bs)
        model = VFL_DECODE_MIN_US + 1.8 + 0.6 * b + 0.6
        diff = round(model - meas, 2)
        if verbose:
            print(f"({mode},{fl},{bs}) bytes={b:2d} model={model:5.2f} "
                  f"meas={meas:5.2f} diff={diff:5.2f}")
        if diff == 2.40:
            ok += 1
        else:
            outliers.append(((mode, fl, bs), b, model, meas, diff))
    return ok, len(rows), outliers


if __name__ == "__main__":
    ok, n, out = check_connective_byte_count()
    print(f"connective byte count: {ok}/{n} rows at a constant 2.40 us offset")
    for o in out:
        print("  outlier:", o)
