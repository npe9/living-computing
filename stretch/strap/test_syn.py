#!/usr/bin/env python3
"""test_syn.py -- pure-Python regression test for strap_asm.py's SYN
pseudo-op (C22-6531 p.31), run directly against assemble()'s symbol
table -- no Bluesim/STRAP program run needed, since SYN is entirely an
assembler-side symbol-resolution feature with no new machine-instruction
semantics to verify on the model. Exercises exactly the class of bug
this feature's own history warns about (see strap_asm.py's module
docstring): SYN silently taking the location counter instead of
evaluating its operand, and SYN's forward-reference tolerance ("this
may possibly mean as late as pass 3 of Strap-1").

Run standalone: `./test_syn.py`. Wired into run_tests.sh alongside the
other regression blocks.
"""

import sys

from strap_asm import assemble, AssemblerError, eval_expr

FAILS = 0


def check(label, got, expected):
    global FAILS
    if got == expected:
        print(f"PASS {label} = {got!r}")
    else:
        print(f"FAIL {label} = {got!r}, expected {expected!r}")
        FAILS += 1


def expect_error(label, thunk):
    global FAILS
    try:
        thunk()
    except AssemblerError as e:
        print(f"PASS {label} raised AssemblerError: {e}")
        return
    print(f"FAIL {label} did not raise AssemblerError")
    FAILS += 1


# ---------------------------------------------------------------------
# C22-6531 p.31 "Example B", transcribed verbatim except for dropping
# its ALF/DDI line (DDI is separately out of scope for this assembler,
# see module docstring -- unrelated to SYN and not needed for the
# values this test actually checks). The manual states the worked
# answer directly: "the address arithmetic JIM + RIP is done correctly,
# yielding an answer of 179" (389 + -210).
# ---------------------------------------------------------------------
prog = assemble("""
JIM     SYN(B, 24), 389
RIP     SYN(B, 24), -210
""")
check("Example B: JIM", prog.symtab['JIM'], 389)
check("Example B: RIP", prog.symtab['RIP'], -210)
check("Example B: JIM+RIP", eval_expr('JIM+RIP', prog.symtab, 0), 179)

# ---------------------------------------------------------------------
# Bare SYN with no (dds) at all -- the shape the DCP Maintenance
# Compool actually uses throughout (`NAME SYN, Y`, no parens), and a
# plain bit-address literal as Y instead of an integer.
# ---------------------------------------------------------------------
prog = assemble("""
BASE    SYN, 4006.6
""")
check("bare SYN, bit-address literal", prog.symtab['BASE'], 4006 * 64 + 6)

# ---------------------------------------------------------------------
# Genuine forward reference: A's operand names B, which is only defined
# by a SYN statement appearing LATER in the source. This is exactly the
# capability the module docstring calls out as needing a
# forward-reference-aware pass -- and exactly what the old, reverted
# code (silently using the location counter) could never have gotten
# right, since B doesn't exist in the symbol table at all on a single
# top-to-bottom pass.
# ---------------------------------------------------------------------
prog = assemble("""
A       SYN, B+1
B       SYN, 100
""")
check("forward reference: B", prog.symtab['B'], 100)
check("forward reference: A (= B+1, B defined later)", prog.symtab['A'], 101)

# Chained forward reference, three deep, out of order.
prog = assemble("""
X       SYN, Y+1
Y       SYN, Z+1
Z       SYN, 10
""")
check("chained forward reference: X", prog.symtab['X'], 12)

# ---------------------------------------------------------------------
# A SYN with no data description that names a plain integer via a
# preceding DD/DDI-defined symbol works the same as the manual's
# example; a SYN whose expression can never resolve (undefined symbol)
# must raise, not silently default to 0 or the location counter.
# ---------------------------------------------------------------------
expect_error(
    "undefined SYN reference raises",
    lambda: assemble("""
BAD     SYN, NOSUCHSYMBOL+1
"""))

expect_error(
    "circular SYN reference raises",
    lambda: assemble("""
P       SYN, Q+1
Q       SYN, P+1
"""))

if FAILS == 0:
    print("ALL TESTS PASSED")
    sys.exit(0)
else:
    print(f"{FAILS} TEST(S) FAILED")
    sys.exit(1)
