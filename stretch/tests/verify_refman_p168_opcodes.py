#!/usr/bin/env python3
"""verify_refman_p168_opcodes.py -- strap/opcodes.py against the
Reference Manual's own COMPLETE OPERATION AND MODIFIER LIST.

>>> 22-6530-2 printed pp.168-169 = PDF pp.171-172 is the normative
opcode table for the whole machine, and this project had never opened
it. <<<  strap/README.md's "Next steps" item 2 asks for exactly this
cross-check; opcodes.py's own comments cite the X22-6533 POCKET CARD
for the connective and input-output values, a summary rather than the
manual.  Found by the back-matter sweep in docs/NEXT.md.

HOW THE PAGE STATES A CODE, because that is half of what is checked
here.  Each block gives a TEMPLATE over a named bit range and then the
operation values that go in the x's:

    INTEGER ARITHMETIC     bits 51-63   ssbxxxxx1iiii
    RADIX CONVERSION       bits 51-63   ssbxxxxx1iiii
    CONNECTIVE             bits 51-63   ccccxx111iiii
    FLOATING POINT         bits 18-31   nssxxxxx10iiii
    DIRECT INDEX           bits 19-31   jjjjxxxx1iiii
    IMMEDIATE INDEX        bits 19-31   jjjj10000xxxx
    UNCONDITIONAL BRANCH   bits 19-31   xxx000000iiii
    MISCELLANEOUS          bits 19-31   xxx100000iiii
    INDEX BRANCHING        bits 19-31   jjjjxx1001xxi
    INPUT-OUTPUT           bits 51-63   xxxx10000iiii
    TRANSMIT               bits 51-63   jjjjfdx10iiii
    INDEXING MODES (VFL)   bits 32-34   ppp

opcodes.py stores a slightly different slice of some of these -- the
VFL tables keep the trailing literal 1, the floating-point table keeps
the trailing 10 -- so each check below applies the template's own rule
to the printed digits and compares.  THAT IS DELIBERATE: a test that
only compared numbers would pass with the template misread, and the
template is where an encoding bug would live.

EVERY CHECK IS TWO-WAY.  A code that disagrees fails, and so does a
mnemonic present on one side and not the other, which is the half
that catches an operation quietly added to the assembler.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                os.pardir, "strap"))
import opcodes

# ---- printed p.168 ---------------------------------------------------
# INTEGER ARITHMETIC OPERATIONS; bits 51-63, "ssbxxxxx1iiii"
P168_INTEGER = {
    "+": "00000", "+MG": "10000", "L": "00010", "LWF": "10010",
    "M+": "00100", "M+MG": "10100", "M+1": "10101", "ST": "00110",
    "SRD": "10110", "K": "01000", "KF": "11000", "KE": "01001",
    "KFE": "11001", "KR": "01010", "KFR": "11010", "LTRS": "11110",
    "*": "01100", "LFT": "00101", "*+": "11100", "/": "01110",
}
# RADIX CONVERSION OPERATIONS; bits 51-63, same template
P168_RADIX = {
    "LCV": "00001", "LTRCV": "10001", "CV": "01101", "DCV": "11101",
}
# CONNECTIVE OPERATIONS; bits 51-63, "ccccxx111iiii"
P168_CONNECTIVE = {"C": "00", "CM": "01", "CT": "10"}
# FLOATING POINT OPERATIONS; bits 18-31, "nssxxxxx10iiii"
P168_FP = {
    "+": "00000", "+MG": "01000", "L": "00001", "LWF": "01001",
    "M+": "00010", "M+MG": "01010", "ST": "00011", "K": "00100",
    "KMG": "01100", "KR": "00101", "KMGR": "01101", "*": "00110",
    "/": "00111", "R/": "01111", "SRT": "11011", "D+": "10000",
    "D+MG": "11000", "DL": "10001", "DLWF": "11001", "SRD": "01011",
    "SLO": "10011", "D*": "10110", "LFT": "10010", "*+": "01110",
    "D/": "10111", "F+": "10100", "SHF": "11100", "E+": "10101",
    "E+I": "11101",
}
# DIRECT INDEX ARITHMETIC; bits 19-31, "jjjjxxxx1iiii"
P168_DIR_INDEX = {
    "LX": "0000", "LV": "0001", "LC": "0010", "LR": "0011",
    "SX": "1000", "SV": "1001", "SC": "1010", "SR": "1011",
    "V+": "0101", "V+C": "0110", "V+CR": "0111", "KV": "0100",
    "KC": "1100", "RNX": "1111", "LVE": "1101", "SVA": "1110",
}

# ---- printed p.169 ---------------------------------------------------
# IMMEDIATE INDEX ARITHMETIC; bits 19-31, "jjjj10000xxxx"
P169_IMM_INDEX = {
    "LVI": "0001", "LCI": "0010", "LRI": "0011", "LVNI": "1001",
    "V+I": "0101", "V+IC": "0110", "V+ICR": "0111", "V-I": "1101",
    "V-IC": "1110", "V-ICR": "1111", "C+I": "0000", "C-I": "1000",
    "KVI": "0100", "KVNI": "1100", "KCI": "1010", "LVS": "1011",
}
# UNCONDITIONAL BRANCHING; bits 19-31, "xxx000000iiii"
P169_UNCOND = {"B": "010", "BR": "011", "BE": "000", "BD": "001",
               "BEW": "100", "NOP": "110"}
# MISCELLANEOUS OPERATIONS; bits 19-31, "xxx100000iiii"
P169_MISC = {"R": "000", "RCZ": "001", "EX": "010", "EXIC": "011",
             "Z": "100"}
# INPUT-OUTPUT OPERATIONS; bits 51-63, "xxxx10000iiii".  The page
# spells the SEOP forms "RD(SEOP)"; opcodes.py spells them "RDSEOP".
P169_IO = {
    "RD": "0000", "W": "0001", "CTL": "0010", "LOC": "0011",
    "REL": "1001", "RD(SEOP)": "0100", "W(SEOP)": "0101",
    "CTL(SEOP)": "0110", "LOC(SEOP)": "0111", "REL(SEOP)": "1101",
    "CCW": "1000",
}
# INDEX BRANCHING; bits 19-31, "jjjjxx1001xxi".  Operation 0 is CB and
# 1 is CBR -- the printed "Operations" column -- and the two modifier
# groups are the xx value field and the i count-zero test:
#   00 leave value unchanged   01 add half to value
#   10 add one to value        11 subtract one from value
#   i = 0 branch if count non-zero, 1 branch if count zero
P169_CB_VALUE = {"": "00", "H": "01", "+": "10", "-": "11"}
# TRANSMIT OPERATIONS; bits 51-63, "jjjjfdx10iiii".  Operation 0 is T
# and 1 is SWAP; f = 0 forward / 1 backward; d = 0 direct count /
# 1 immediate count.
# INDEXING MODES FOR VARIABLE FIELD LENGTH OPERATIONS; bits 32-34
P169_INDEXING_MODES = {
    "direct": "000", "immediate": "100",
    "V+": "001", "V+C": "010", "V+CR": "011",
    "V-": "101", "V-C": "110", "V-CR": "111",
}

fails = []


def check(name, got, want):
    ok = got == want
    print("%-4s %s = %s%s" % ("PASS" if ok else "FAIL", name, got,
                              "" if ok else ", expected %s" % (want,)))
    if not ok:
        fails.append(name)


def compare(name, printed, stored, rule):
    """Two-way: every mnemonic on both sides, every value equal."""
    want = {m: rule(bits) for m, bits in printed.items()}
    check("%s_mnemonics" % name, sorted(stored), sorted(want))
    bad = {m: (stored[m], want[m]) for m in sorted(set(stored) & set(want))
           if stored[m] != want[m]}
    check("%s_codes" % name, bad, {})


def main():
    # VFL integer and radix conversion share one template and one table
    # in opcodes.py.  "ssbxxxxx1iiii": opcodes.py keeps xxxxx AND the
    # literal 1 that follows it, so the stored code is the printed five
    # digits shifted up one with a 1 underneath.
    printed_vfl = dict(P168_INTEGER)
    printed_vfl.update(P168_RADIX)
    compare("vfl_int", printed_vfl, opcodes.VFL_INT_CODES,
            lambda b: (int(b, 2) << 1) | 1)

    # "nssxxxxx10iiii": the stored code keeps xxxxx and the literal 10.
    compare("fp", P168_FP, opcodes.FP_CODES,
            lambda b: (int(b, 2) << 2) | 0b10)

    # "jjjjxxxx1iiii": xxxx and the literal 1.
    compare("dir_index", P168_DIR_INDEX, opcodes.DIR_INDEX_CODES,
            lambda b: (int(b, 2) << 1) | 1)

    # "jjjj10000xxxx": the four x's are at the END, nothing trails them,
    # so the stored code is the printed digits unchanged.  That this
    # rule DIFFERS from the three above is the point of writing the
    # templates out.
    compare("imm_index", P169_IMM_INDEX, opcodes.IMM_INDEX_CODES,
            lambda b: int(b, 2))

    # "xxx000000iiii" and "xxx100000iiii": three digits, unshifted.
    compare("uncond_branch", P169_UNCOND, opcodes.UNCOND_BRANCH_CODES,
            lambda b: int(b, 2))
    compare("misc", P169_MISC, opcodes.MISC_CODES, lambda b: int(b, 2))

    # "xxxx10000iiii": four digits, unshifted.  opcodes.py spells the
    # SEOP forms without the parentheses the page prints.
    io_printed = {m.replace("(", "").replace(")", ""): b
                  for m, b in P169_IO.items()}
    compare("io", io_printed, opcodes.IO_OP, lambda b: int(b, 2))

    # "ccccxx111iiii": opcodes.py stores the xx operation plus the
    # literal 111 as one five-bit suffix.  THIS IS THE ONE THE MANUAL
    # NOW SETTLES: opcodes.py's comment credits the X22-6533 pocket
    # card for these values, a summary rather than the manual.
    compare("connective", P168_CONNECTIVE, opcodes.CONNECTIVE_SUFFIX,
            lambda b: (int(b, 2) << 3) | 0b111)

    # INDEXING MODES, bits 32-34.  opcodes.py keys them by the
    # immediate-index mnemonic that selects each one.
    want = {"V+I": 1, "V+IC": 2, "V+ICR": 3,
            "V-I": 5, "V-IC": 6, "V-ICR": 7}
    check("indexing_modes", opcodes.PROGRESSIVE_SECONDARY_OP, want)
    # and the printed digits agree with those numbers.
    check("indexing_modes_match_page",
          {k: int(P169_INDEXING_MODES[k.replace("I", "")
                                      .replace("C R", "CR")], 2)
           for k in ("V+I", "V+IC", "V+ICR", "V-I", "V-IC", "V-ICR")},
          want)
    # Direct addressing is 000 and immediate is 100 -- the field that
    # settled LFI on MCP printed p.18, "4 for immediate and 0 for
    # direct", here printed rather than inferred.
    check("indexing_mode_direct", int(P169_INDEXING_MODES["direct"], 2), 0)
    check("indexing_mode_immediate",
          int(P169_INDEXING_MODES["immediate"], 2), 4)

    # INDEX BRANCHING.  opcodes.py stores (value-modifier, refill,
    # count-zero) per spelled-out mnemonic; the page gives the three
    # pieces separately.  Rebuild the sixteen names from the page.
    want = {}
    for refill_s, refill in (("", 0), ("R", 1)):
        for zero_s, zero in (("", 0), ("Z", 1)):
            for val_s, val in P169_CB_VALUE.items():
                want["CB" + refill_s + zero_s + val_s] = (int(val, 2),
                                                          refill, zero)
    check("index_branching", opcodes.CB_CODES, want)
    # CB+ is "add one to value", which is the one this project leans on:
    # one in bit position 17 of a 24-bit address is SIXTY-FOUR BITS, one
    # word, and CBH -- "add half" -- is a half word.
    check("cb_plus_is_add_one", opcodes.CB_CODES["CB+"][0], 0b10)
    check("cb_h_is_add_half", opcodes.CB_CODES["CBH"][0], 0b01)

    # TRANSMIT, "jjjjfdx10iiii": operation 0 is T and 1 is SWAP, f is
    # forward/backward and d is direct/immediate count.  opcodes.py
    # stores (backward, immCount, swap).
    want = {}
    for swap_s, swap in (("T", 0), ("SWAP", 1)):
        for back_s, back in (("", 0), ("B", 1)):
            for imm_s, imm in (("", 0), ("I", 1)):
                want[swap_s + back_s + imm_s] = (back, imm, swap)
    check("transmit", opcodes.TRANSMIT_CODES, want)

    print("ALL CHECKS PASSED" if not fails
          else "%d CHECK(S) FAILED" % len(fails))
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
