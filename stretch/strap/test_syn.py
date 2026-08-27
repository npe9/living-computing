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


def expect_error(label, thunk, must_contain=None):
    """must_contain, if given, is checked against the raised message --
    the classification (undefined vs. circular) is real behavior worth
    pinning down, not just "raised something" (a prior version of this
    test only checked that ANY AssemblerError came back, which passed
    even while a plain undefined-symbol case was mislabeled a circular
    reference -- caught by advisor review)."""
    global FAILS
    try:
        thunk()
    except AssemblerError as e:
        if must_contain and must_contain not in str(e):
            print(f"FAIL {label} raised AssemblerError, but missing {must_contain!r}: {e}")
            FAILS += 1
            return
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
# A SYN whose expression can never resolve must raise, not silently
# default to 0 or the location counter -- and the two distinct ways
# that can happen (a plain typo'd/nonexistent symbol vs. a genuine
# mutual-reference cycle) must be reported AS distinct, not both
# collapsed into one "undefined or circular" message that would point
# an undefined-symbol typo at a nonexistent cycle (caught by advisor
# review of this test's first version).
# ---------------------------------------------------------------------
expect_error(
    "undefined SYN reference raises, classified as undefined",
    lambda: assemble("""
BAD     SYN, NOSUCHSYMBOL+1
"""), must_contain='undefined: BAD')

expect_error(
    "circular SYN reference raises, classified as circular",
    lambda: assemble("""
P       SYN, Q+1
Q       SYN, P+1
"""), must_contain='circular: ')

# A -> B -> undefined: A's DIRECT dependency (B) is itself stuck, but
# the reason is transitive -- B depends on something that plainly never
# exists. This must still be reported as "undefined", not "circular",
# even though a naive one-hop check (does A's direct dependency also
# appear in the stuck set?) would call it circular.
expect_error(
    "transitive undefined chain classified as undefined, not circular",
    lambda: assemble("""
A       SYN, B+1
B       SYN, NOSUCHSYMBOL+1
"""), must_contain='undefined: ')

# ---------------------------------------------------------------------
# A SYN operand naming a system symbol ($-prefixed -- an index register
# or indicator bit, C22-6531 p.14-15) must resolve without ever being
# treated as an unresolved programmer symbol: system symbols route
# through eval_system_symbol, entirely outside symtab, so
# referenced_symbols() must not flag them as "missing" and stall the
# fixpoint pass waiting for something that was never going into symtab
# in the first place.
# ---------------------------------------------------------------------
prog = assemble("""
XR5     SYN, $X5
""")
check("SYN operand naming a system symbol ($X5)", prog.symtab['XR5'], 21 * 64)

if FAILS == 0:
    print("ALL TESTS PASSED")
    sys.exit(0)
else:
    print(f"{FAILS} TEST(S) FAILED")
    sys.exit(1)
