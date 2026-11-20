#!/usr/bin/env python3
"""test_cpu_symbol.py -- "$CPU" is word 6 (Other CPU), not indicator 11.5.

Pure Python, no Bluesim.  The one name in both opcodes.INDICATOR_BITS and
opcodes.SYSTEM_SYMBOLS is CPU, and until 2026-11-19 every "$name" path
looked the indicator names up first, so "$CPU" assembled to 11.5.

THE SOURCES (page images read 2026-11-19; PDF page in parentheses):
  * C22-6531 printed p.15 (PDF 16), Special Registers: "6.0  $CPU  Other CPU".
  * C22-6531 printed p.56 (PDF 57), Appendix A:
      "$ CPUS 1 CPU Signal 11 5"   and   "$ CPU 2 Other CPU 6 0-18".
  * C28-6129 printed p.10 (PDF 14), STRAP II special register symbols:
      "Other CPU  $CPU  6.0".
  * C28-6129 printed p.43 (PDF 46), Appendix A: the same two rows.
  * C22-6531 printed p.65 (PDF 66), the "indicator mnemonics which may be
    used in BIND": "CPU  Other CPU  11.5" -- the bare BRANCH mnemonic.
    C28-6129 printed p.52 (PDF 55) prints that entry as "CPUS CPU Signal
    11.5".  IBM's SSIP listing assembles BCPUZ to 1575.02 C6, indicator 5
    (tests/verify_ssip_sip17_listing.py).
Every source that prints a "$CPU" gives 6.0; the indicator's "$" name is
$CPUS.  The bare CPU of BCPU/BCPUZ stays indicator 5.  (Appendix A's
footnote column puts 1, "system symbol" only, on CPUS and 2, "both an
indicator mnemonic and a system symbol", on CPU -- consistent with CPU
being a branch mnemonic as well as the $ name of word 6.)

FOUR "$name" SITES are fixed, each read through opcodes.INDICATOR_SYMBOLS:
  A strap_asm.eval_system_symbol      (the address)
  B strap_asm.system_symbol_dds       (the default dds)
  C strap_asm INDMK mask fields       (the bit number)
  D strap2/optable.system_symbol      (the STRAP II reconstruction)

DISCRIMINATION, OBSERVED 2026-11-19 (each site reverted alone to
INDICATOR_BITS, run, restored by the exact inverse patch, git diff clean):
  site A reverted: FAIL  $CPU SYN value; $CPU in an expression;
                   B,$CPU equals B,6.0
  site B reverted: FAIL  $CPU has no indicator dds
  site C reverted: FAIL  INDMK,$CPU fails loud
  site D reverted: FAIL  strap2 $CPU value and dds
  Controls ($CPUS, INDMK,$CPUS, BCPUZ == BCPUSZ, strap2 $CPUS) passed in
  every run.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "strap"))

from strap_asm import (assemble, AssemblerError, eval_expr,  # noqa: E402
                       system_symbol_dds)
from strap2.optable import system_symbol, dds13                # noqa: E402

FAILS = 0


def check(label, got, expected):
    global FAILS
    if got == expected:
        print(f"PASS {label} = {got!r}")
    else:
        print(f"FAIL {label} = {got!r}, expected {expected!r}")
        FAILS += 1


WORD6 = 6 * 64          # 6.0, Other CPU
CPUS = 11 * 64 + 5      # 11.5, CPU Signal

# -- site A: the address -------------------------------------------------
p = assemble("""
A       SYN, $CPU
B       SYN, $CPUS
C       SYN, 6.0
""")
check("$CPU SYN value (C22-6531 p.15/p.56, C28-6129 p.10: 6.0)",
      p.symtab['A'], WORD6)
check("control: $CPUS SYN value (Appendix A: 11 5)", p.symtab['B'], CPUS)
check("$CPU in an expression ($CPU+.19, the register's last bit + 1)",
      eval_expr('$CPU+.19', p.symtab, 0), WORD6 + 19)
w1 = assemble("        B, $CPU\n").words
w2 = assemble("        B, 6.0\n").words
check("B,$CPU equals B,6.0", w1, w2)

# -- site B: the default dds ---------------------------------------------
# C28-6129 printed pp.10-11: class 3 (indicator bits) are (BU,1,8).  $CPU
# is class 2, a special register, which this assembler does not give a
# dds yet (strap_asm.system_symbol_dds docstring) -- so None, not BU,1,8.
check("$CPU has no indicator dds", system_symbol_dds('$CPU'), None)
check("control: $CPUS has the indicator dds",
      system_symbol_dds('$CPUS'), 'BU,1,8')

# -- site C: INDMK --------------------------------------------------------
try:
    assemble("        INDMK,$CPU\n")
    print("FAIL INDMK,$CPU fails loud: it assembled")
    FAILS += 1
except AssemblerError as e:
    check("INDMK,$CPU fails loud (word 6 is not an indicator bit)",
          "outside a word's bits 0-63" in str(e), True)
check("control: INDMK,$CPUS sets bit 5 alone",
      assemble("        INDMK,$CPUS\n").words, {32: 1 << (63 - 5)})

# -- the branch mnemonic is untouched -------------------------------------
bz = assemble("        BCPUZ, 40.0\n").words
bzs = assemble("        BCPUSZ, 40.0\n").words
check("control: BCPUZ assembles as BCPUSZ (both indicator 5)", bz, bzs)
check("control: BCPUZ's low byte is C6, as SSIP prints 1575.02 C6",
      (bz[32] >> 32) & 0xFF, 0xC6)

# -- site D: the STRAP II reconstruction ----------------------------------
check("strap2 $CPU value and dds (6.0, BU,64,8)", system_symbol('CPU'),
      (WORD6, dds13("BU", 0, 8)))
check("control: strap2 $CPUS value and dds (11.5, BU,1,8)",
      system_symbol('CPUS'), (CPUS, dds13("BU", 1, 8)))

print()
if FAILS:
    print(f"test_cpu_symbol: {FAILS} FAIL")
    sys.exit(1)
print("test_cpu_symbol: all PASS")
