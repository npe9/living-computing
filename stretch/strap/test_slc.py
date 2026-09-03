#!/usr/bin/env python3
"""test_slc.py -- pure-Python regression test for strap_asm.py's SLC
pseudo-op ("Set Location Counter", C22-6531 p.32), run directly
against assemble()'s symbol table and word image -- no Bluesim run
needed, since SLC is entirely an assembler-side placement feature.
Pins down each rule the manual states: Y is a bit-address expression
(a bare integer counts as BITS, not words); the next statement is
"subject to rounding upward conventions"; Y must be evaluable when
reached (no forward references) and positive; the name field is
ignored. The companion verify_ibox1_listing.py checks what SLC is
actually FOR -- placing a real listing's code at its own addresses.

Run standalone: `./test_slc.py`. Wired into run_tests.sh.
"""

import sys

from strap_asm import assemble, AssemblerError

FAILS = 0


def check(label, got, expected):
    global FAILS
    if got == expected:
        print(f"PASS {label} = {got!r}")
    else:
        print(f"FAIL {label} = {got!r}, expected {expected!r}")
        FAILS += 1


def expect_error(label, src, must_contain):
    global FAILS
    try:
        assemble(src)
    except AssemblerError as e:
        if must_contain in str(e):
            print(f"PASS {label} raised AssemblerError: {e}")
        else:
            print(f"FAIL {label} raised the wrong error: {e} (wanted {must_contain!r})")
            FAILS += 1
        return
    print(f"FAIL {label} did not raise")
    FAILS += 1


# 1. Word-address form: "W.B" places the next statement at word W.
p = assemble("""
        SLC, 2860.0
HERE    L(BU,64,8), K
        BEW, $
K       DD(BU,64,8), 7
        END, HERE
""")
check("SLC 2860.0 places HERE at word 2860", p.symtab['HERE'], 2860 * 64)
check("assembled word actually lands at 2860", 2860 in p.words, True)
check("nothing at the default origin (word 32)", 32 in p.words, False)
check("END resolves to the relocated start", p.end_pc, 2860 * 2)

# 2. A bare integer is a BIT count (p.32: "added in as a 24-bit address
# field; i.e., as an integral number of bits"), not a word count.
p = assemble("""
        SLC, 192
HERE    LVI, $1, 5
        END, HERE
""")
check("SLC 192 (bits) = word 3", p.symtab['HERE'], 3 * 64)

# 3. Rounding upward: a full-word instruction after an unaligned SLC
# lands at the next full word; a bit-precise DD does not round.
p = assemble("""
        SLC, 5.32
FULL    L(BU,64,8), FULL
        SLC, 9.3
BITS    DD(BU,8,8), 1
        END, FULL
""")
check("full-word instruction after SLC 5.32 rounds up to 6.0", p.symtab['FULL'], 6 * 64)
check("DD after SLC 9.3 stays at 9.3 (bit-precise, no rounding)", p.symtab['BITS'], 9 * 64 + 3)

# 4. Symbolic Y: a location-counter symbol defined above, a SYN
# resolvable by then (eager resolution), and "$" meaning the current
# location counter.
p = assemble("""
BASE    SYN, 100.0
        SLC, BASE+2.0
A       LVI, $1, 1
        SLC, $+4.0
B       LVI, $1, 2
        SLC, A+1.0
C       LVI, $1, 3
        END, A
""")
check("SLC via SYN + offset", p.symtab['A'], 102 * 64)
check("SLC via $ (LC after A's half-word = 102.32, +4.0 = 106.32)", p.symtab['B'], 106 * 64 + 32)
check("SLC backwards via an earlier label", p.symtab['C'], 103 * 64)

# 5. Errors: forward reference, negative, and the ignored name field
# (p.32 "Any symbol A appearing in the name field is ignored" -- so
# referencing it must be an undefined-symbol error, never silently the
# new location).
expect_error("forward reference in SLC", """
        SLC, LATER
LATER   LVI, $1, 1
        END, LATER
""", "not yet defined")
expect_error("negative SLC", """
        SLC, -64
X       LVI, $1, 1
        END, X
""", "negative")
expect_error("SLC name field is ignored (reference fails as undefined)", """
NAME    SLC, 40.0
X       B, NAME
        END, X
""", "undefined symbol")
expect_error("SLC with no operand", """
        SLC
X       LVI, $1, 1
        END, X
""", "needs a location operand")

if FAILS:
    print(f"{FAILS} TEST(S) FAILED")
    sys.exit(1)
print("ALL TESTS PASSED")
