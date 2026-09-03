"""opcodes.py -- IBM 7030 "Stretch" instruction encodings for the STRAP
assembler.

This table is the assembler-side twin of the decoder in
stretch/bsv/StretchDecode.bsv and the executor in
stretch/bsv/StretchExecute.bsv. Every bit pattern here was copied from
those two files (which were themselves derived from the primary sources
-- see stretch/bsv/README.md), NOT re-derived independently, so that the
STRAP source language and the Bluespec model share one ground truth: an
instruction this assembler emits decodes, on the BSV model, to exactly
the DecodedInstr the assembler intended. This is the codesign contract
this project is for.

Citations:
  - C22-6531 "7030 Symbolic Assembly Program / Simulator" (1960), for
    STRAP-1 syntax: the twelve symbolic instruction formats, arithmetic
    expressions and bit-address notation, system symbols, and the
    pseudo-operations (DD, VF, CF, RF, SYN, END, CNOP). See
    stretch/docs/C22-6531_7030xasm-sim_1960.pdf.
  - IBM 7030 Reference Card X22-6533-1 and Reference Manual 22-6530-2,
    via stretch/bsv/StretchDecode.bsv / StretchExecute.bsv, for the
    exact opcode bit values.
"""

# ---------------------------------------------------------------------
# VFL integer arithmetic / radix conversion, 6-bit "code" field
# (StretchDecode.isVflIntCode). Format 7: OP(dds), A24(I), OF7(I').
# ---------------------------------------------------------------------
VFL_INT_CODES = {
    "+":     0b000001,
    "+MG":   0b100001,
    "L":     0b000101,
    "LWF":   0b100101,
    "M+":    0b001001,
    "M+MG":  0b101001,
    "M+1":   0b101011,
    "ST":    0b001101,
    "SRD":   0b101101,
    "K":     0b010001,
    "KF":    0b110001,
    "KE":    0b010011,
    "KFE":   0b110011,
    "KR":    0b010101,
    "KFR":   0b110101,
    "LTRS":  0b111101,
    "*":     0b011001,
    "LFT":   0b001011,
    "*+":    0b111001,
    "/":     0b011101,
    "LCV":   0b000011,
    "LTRCV": 0b100011,
    "CV":    0b011011,
    "DCV":   0b111011,
}
# "-" is "+" with the invert-sign modifier (see StretchExecute.bsv /
# bsv/README.md "Executed"), not a distinct 6-bit code.
VFL_INT_MINUS_BASE = "+"

# ---------------------------------------------------------------------
# Floating point, 7-bit "code" field (StretchDecode.isValidFpCode).
# Format 1: OP(dds), A18(I). Half-word.
# ---------------------------------------------------------------------
FP_CODES = {
    "+":    0b0000010,
    "+MG":  0b0100010,
    "L":    0b0000110,
    "LWF":  0b0100110,
    "M+":   0b0001010,
    "M+MG": 0b0101010,
    "ST":   0b0001110,
    "K":    0b0010010,
    "KMG":  0b0110010,
    "KR":   0b0010110,
    "KMGR": 0b0110110,
    "*":    0b0011010,
    "/":    0b0011110,
    "R/":   0b0111110,
    "SRT":  0b1101110,
    "D+":   0b1000010,
    "D+MG": 0b1100010,
    "DL":   0b1000110,
    "DLWF": 0b1100110,
    "SRD":  0b0101110,
    "SLO":  0b1001110,
    "D*":   0b1011010,
    "LFT":  0b1001010,
    "*+":   0b0111010,
    "D/":   0b1011110,
    "F+":   0b1010010,
    "SHF":  0b1110010,
    "E+":   0b1010110,
    "E+I":  0b1110110,
}

# ---------------------------------------------------------------------
# Direct index arithmetic, 5-bit "code" field
# (StretchDecode.isValidDirIndexOp). Format 3: OP,J,A19(I). Half-word.
# ---------------------------------------------------------------------
DIR_INDEX_CODES = {
    "LX":   0b00001,
    "LV":   0b00011,
    "LC":   0b00101,
    "LR":   0b00111,
    "SX":   0b10001,
    "SV":   0b10011,
    "SC":   0b10101,
    "SR":   0b10111,
    "V+":   0b01011,
    "V+C":  0b01101,
    "V+CR": 0b01111,
    "KV":   0b01001,
    "KC":   0b11001,
    "RNX":  0b11111,
    "LVE":  0b11011,
    "SVA":  0b11101,
}

# ---------------------------------------------------------------------
# Immediate index arithmetic, 4-bit "code" field, from the exact-16
# case list in StretchExecute.bsv's ImmIndex switch (pocket card
# "IMMEDIATE INDEX ARITHMETIC" table). Format 4: OP,J,imm. Half-word.
# ---------------------------------------------------------------------
IMM_INDEX_CODES = {
    "LVI":    0b0001,
    "LVNI":   0b1001,
    "LCI":    0b0010,
    "LRI":    0b0011,
    "C+I":    0b0000,
    "C-I":    0b1000,
    "V+I":    0b0101,
    "V+IC":   0b0110,
    "V+ICR":  0b0111,
    "V-I":    0b1101,
    "V-IC":   0b1110,
    "V-ICR":  0b1111,
    "KVI":    0b0100,
    "KVNI":   0b1100,
    "KCI":    0b1010,
    # 0b1011 = LVS ("Load Value with Sum", format 12's own variable-in-
    # -number-field format -- StretchExecute.bsv leaves it unimplemented
    # and this assembler does not encode it either; see README).
}

# Immediate index ops whose operand is "bits 0-17 of the address part"
# (an 18-bit count/refill integer in the TOP 18 bits of the 19-bit
# field, Reference Manual p.25) rather than a 19-bit value-field
# address. See strap_asm.py's IMM_INDEX emit case.
IMM_INDEX_COUNT_OPS = {"LCI", "LRI", "C+I", "C-I", "KCI"}

# ---------------------------------------------------------------------
# Count and Branch / Count, Branch, and Refill, format 5's mnemonic
# table: (v, refill, bz) per mnemonic, source pcard-3.png "INDEX
# BRANCHING" box --
#   CB   Count and Branch           ab10010c
#   CBR  Count, Branch, and Refill  ab10011c
#   ab = 00 leave value unchanged   ab = 01 add half to value
#   ab = 10 add one to value        ab = 11 subtract one from value
#   c = 0 branch if count non-zero  c = 1 branch if count zero
# Mnemonic grammar: CB[R][Z][H|+|-] -- "R" sets refill=1, "Z" sets
# bz=1 (branch if count zero, else the default is branch if non-
# -zero), and the trailing suffix picks ab: none=00 (unchanged),
# H=01 (add half), +=10 (add one), -=11 (subtract one). Not inferred
# from listing usage alone (the same mistake corrected twice for the
# SIC finding, see docs/archival_inventory.md) -- cross-checked
# against real occurrences transcribed from docs/jb_ax4b_ibox-4.pdf
# section 150 (routine 150, pp.155-165): plain CB and CB+ (p.155,
# IBR1-IBR14, "COUNT TO n + BRANCH" / "COUNT TO ZERO NO BRANCH" --
# i.e. bz=0 in all of them, matching the table's default), CBH and
# CB- (p.156, IBR21-IBR34, same bz=0 pattern), CBR and CBR+ (p.159,
# IBR97-IBR105, "NO REFILL" vs "REFILL" comments matching refill=0/1),
# and CBRZH / CBRZ- (p.165, "SHOULD BRANCH + REFILL, C TO 0" --
# bz=1). Encoder (enc_count_branch) already accepted the full
# (v, refill, bz) space before this table existed -- StretchExecute.
# bsv's CountBranch arm consults all three fields (cb.v, cb.refill,
# cb.branchIfZero), confirmed by reading the arm in full before
# building this table (see the archival_inventory.md entry for the
# reasoning: don't add a mnemonic for a field the model decodes but
# never uses).
# ---------------------------------------------------------------------
CB_CODES = {
    "CB":      (0b00, 0, 0),
    "CBH":     (0b01, 0, 0),
    "CB+":     (0b10, 0, 0),
    "CB-":     (0b11, 0, 0),
    "CBZ":     (0b00, 0, 1),
    "CBZH":    (0b01, 0, 1),
    "CBZ+":    (0b10, 0, 1),
    "CBZ-":    (0b11, 0, 1),
    "CBR":     (0b00, 1, 0),
    "CBRH":    (0b01, 1, 0),
    "CBR+":    (0b10, 1, 0),
    "CBR-":    (0b11, 1, 0),
    "CBRZ":    (0b00, 1, 1),
    "CBRZH":   (0b01, 1, 1),
    "CBRZ+":   (0b10, 1, 1),
    "CBRZ-":   (0b11, 1, 1),
}

# ---------------------------------------------------------------------
# Unconditional branch / "misc" ops, 3-bit "code" field
# (StretchDecode.isValidUncondBranchOp / isValidMiscOp).
# Format 2: OP, A19(I). Half-word.
# ---------------------------------------------------------------------
UNCOND_BRANCH_CODES = {
    "BE":  0b000,
    "BD":  0b001,
    "B":   0b010,
    "BR":  0b011,
    "BEW": 0b100,
    "NOP": 0b110,
}
MISC_CODES = {
    "R":   0b000,
    "RCZ": 0b001,
    "EX":  0b010,
    "EXIC":0b011,
    "Z":   0b100,
}

# ---------------------------------------------------------------------
# Indicator names -> bit number in word 11 (StretchTypes.bsv ind_*).
# Used both for $<name> system symbols and for parsing Branch-on-
# -Indicator mnemonics B[Z]<name>[Z] (C22-6531 Appendix A footnote 2).
# ---------------------------------------------------------------------
# Non-indicator system symbols, C22-6531 Appendix A (p.56), as
# (word, first bit) of the register field they name -- "$R" is the
# right half of the accumulator, word 9, so "KV,$X15,$R" (I-Box 4
# section 138) compares against word 9's bits 0-24. Index registers
# ($X0..$X15 / $0..$15) and the indicator names (INDICATOR_BITS, word
# 11) are handled separately in strap_asm.eval_system_symbol. $MASK's
# bit column is not legible enough on the scan to record; add it from
# the page if a program ever needs it. $E/$M/$N/$PI are mathematical
# constants (footnote 12), not addresses, and are not supported.
SYSTEM_SYMBOLS = {
    "AOC": (7, 44),   # All Ones Count, 44-50
    "BC":  (3, 57),   # Boundary Control
    "CA":  (5, 12),   # Channel Address, 12-18
    "CPU": (6, 0),    # Other CPU, 0-18
    "FT":  (14, 0),   # Factor
    "IA":  (2, 0),    # Interruption Address, 0-17
    "IND": (11, 0),   # Indicators
    "IT":  (1, 0),    # Interval Timer, 0-18
    "L":   (8, 0),    # Left Half of Accumulator
    "LB":  (3, 32),   # Lower Boundary, 32-49
    "LZC": (7, 17),   # Left Zeros Count, 17-23
    "MB":  (4, 0),    # Maintenance Bits
    "R":   (9, 0),    # Right Half of Accumulator
    "RM":  (13, 0),   # Remainder
    "SB":  (10, 0),   # Sign Byte, 0-7
    "TC":  (1, 28),   # Time Clock, 28-63
    "TR":  (15, 0),   # Transit
    "UB":  (3, 0),    # Upper Boundary, 0-17
    "Z":   (0, 0),    # Word Number Zero
}

INDICATOR_BITS = {
    "MK": 0, "IK": 1, "IJ": 2, "EK": 3, "TS": 4, "CPUS": 5, "EKJ": 6,
    "UNRJ": 7, "CBJ": 8, "EPGK": 9, "UK": 10, "EE": 11, "EOP": 12,
    "CS": 13, "OP": 15, "AD": 16, "USA": 17, "EXE": 18, "DS": 19,
    "DF": 20, "IF": 21, "LC": 22, "PF": 23, "ZD": 24, "IR": 25,
    "LS": 26, "PSH": 27, "XPFP": 28, "XPO": 29, "XPH": 30, "XPL": 31,
    "XPU": 32, "ZM": 33, "RU": 34, "TF": 35, "UF": 36, "VF": 37,
    "XF": 38, "BTR": 39, "DTR": 40,
    "XCZ": 48, "XVLZ": 49, "XVZ": 50, "XVGZ": 51, "XL": 52, "XE": 53,
    "XH": 54, "MOP": 55, "RLZ": 56, "RZ": 57, "RGZ": 58, "RN": 59,
    "AL": 60, "AE": 61, "AH": 62, "NM": 63,
}
# Sort longest-name-first so a greedy match doesn't stop early (e.g. so
# "AL" in "BZAL" isn't mis-tried before a hypothetical longer name that
# shares its prefix).
INDICATOR_NAMES_BY_LENGTH = sorted(INDICATOR_BITS, key=len, reverse=True)

# ---------------------------------------------------------------------
# Use-mode letters (Data Description "M" field, C22-6531 p.7) ->
# (unsign, decimal) VflMod bits. N/U (floating point) and P
# (properties) are not applicable to VFL/DirIndex encoding.
# ---------------------------------------------------------------------
MODE_BITS = {
    "B":  (0, 0),  # Binary (signed)
    "BU": (1, 0),  # Binary Unsigned
    "D":  (0, 1),  # Decimal (signed) -- decode-only, see README
    "DU": (1, 1),  # Decimal Unsigned -- decode-only, see README
}
MODE_DEFAULT_BS = {"B": 1, "BU": 8, "D": 4, "DU": 4}

# ---------------------------------------------------------------------
# Progressive indexing secondary operation (C22-6531 "Progressive
# Indexing": "Any VFL or Connective operation... may have a second
# operation enclosed in parentheses. The second operation may be V+I,
# V+IC, or V+ICR" -- and, symmetrically, V-I/V-IC/V-ICR) -> the VFL
# address field's P value (Reference Manual p.21: codes 1-3 add the
# instruction's address part into the index value, 5-7 subtract; 2/3
# and 6/7 also count down, 3 and 7 also refill on count zero). This is
# a DIFFERENT namespace from IMM_INDEX_CODES above even though the
# mnemonics are spelled the same way -- format 8 (progressive
# indexing) reuses format 4's mnemonics for the secondary op, but they
# select a VflAddr.p value here, not an ImmIndex.code.
# ---------------------------------------------------------------------
PROGRESSIVE_SECONDARY_OP = {
    "V+I": 1, "V+IC": 2, "V+ICR": 3,
    "V-I": 5, "V-IC": 6, "V-ICR": 7,
}

# ---------------------------------------------------------------------
# Connectives (Reference Manual p.75-77 "Connectives"; opcode values
# from X22-6533 pocket card "CONNECTIVES" table). Same 9-bit opcode
# field VFL arithmetic uses (bits 51-59), split as conn(4)+suffix(5)
# instead of abc(3)+code(6) -- this table gives the fixed 5-bit suffix
# for each of the three connective operations; conn (which of the 16
# logical functions, Figure 20) is the mnemonic's own 4 binary digits,
# parsed directly (see strap_asm.py's classify_connective).
# ---------------------------------------------------------------------
CONNECTIVE_SUFFIX = {
    "C":  0b00111,  # Connect: result -> accumulator field
    "CM": 0b01111,  # Connect to Memory: result -> storage field
    "CT": 0b10111,  # Connect for Test: result discarded, indicators only
}

# ---------------------------------------------------------------------
# Input-Output (Reference Manual "IBM 7619 Exchange" pp.104-127;
# X22-6533 pocket card "INPUT-OUTPUT OPERATIONS" table). The 4-bit OP
# field (instruction bits 51-54): bit weight-4 (the second printed
# digit) is the SEOP flag; the other three bits select the base
# operation. Derived from the pocket card's 9-bit codes (OP + literal
# 10000, e.g. RD=000010000, RDSEOP=010010000) and cross-checked
# independently -- see StretchTypes.bsv's IoOp comment. Only RD/W/CCW/
# REL (and their SEOP forms) are executed by StretchExecute.bsv (see
# StretchIO.bsv's scope note); CTL and LOC assemble here but decode to
# Operation Code Invalid on the model side.
# ---------------------------------------------------------------------
IO_OP = {
    "RD":  0b0000, "W":   0b0001, "CTL": 0b0010, "LOC": 0b0011,
    "CCW": 0b1000, "REL": 0b1001,
    "RDSEOP": 0b0100, "WSEOP": 0b0101, "CTLSEOP": 0b0110, "LOCSEOP": 0b0111,
    "RELSEOP": 0b1101,
}
