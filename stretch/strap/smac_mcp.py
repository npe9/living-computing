#!/usr/bin/env python3
"""smac_mcp.py -- RECONSTRUCTION of SMAC's generator library for the MCP
macro-instructions, written in SMAC's own Generator Language (J28-6128)
and run by strap/smac.py.

>>> A RECONSTRUCTION.  IBM's library tape is not known to survive.  The
>>> expansions are IBM's, read in the ink from C22-6678-1 (MCP Reference
>>> Manual, June 1964).  The generators that produce them are written
>>> here. <<<

THE GENERAL RULE, C22-6678-1 printed p.14: "MOP, parameter 1, parameter
2, etc." -- the STRAP II mnemonic prefixed by M -- is expanded "by the
macro-generator (SMAC)" to
        B,$MCP
        ,$OP
"followed, in consecutive half-words, by the specified parameters".
Null parameters are written ("including null parameters").  pp.14-15
show the I/O and control-word forms, which are the same rule.  Every
pseudo-op of Appendix A (printed p.42) gets a generator of this form.
In Generator Language that is one MOUTV with N (J28-6128 p.10): set 1
puts out the two-line head once without moving; set 2 puts out one
",/1/" per argument.

AppendixA lists 77 codes.  73 have a macro form printed somewhere in the
manual (pp.14-28 and Appendix B, pp.43-46).  Four do not: $SPFLS,
$BSFLS, $STRG and $FECRG.  They get the general rule too, because
p.14 states it for every pseudo-operation.  That is marked as an
inference in GENERAL_ONLY below.

TWO PSEUDO-OPS DEPART FROM THE RULE, as printed, read in the ink:

$SCR, printed pp.19-20.  Macro "MSCR, FWA.(I), N.(I), END":
        B,$MCP          (p.19 prints "B, MCP": a misprint, every other
        ,$SCR            expansion and p.48's hand-coded $SCR have $MCP)
        ,FWA.(I)
        ,N.(I)
        ,0.             "(described as "M." following)"
        B,END'          END RETURN
        (normal return)
"The macro-generator reserves a half-word for M. ... the end return is
given to the half-word preceding the normal return, where a branch
instruction has been constructed by the macro-generator, using the
programmer symbol END as the address."  p.48's hand-coded calling
sequence (B,$MCP / ,$SCR / LVE,,CW+1.0 / ,1.0 / ,0 / B,EOJ) has the
same layout.

$FETCH, printed p.21.  Macro "MFETCH, TTAAAAAA, RELFWA.(I), FWA.(I),
, N.(I), ERROR, END" (printed on two lines; the comma at the line
break is read as typographic, not as a null parameter):
        B,$MCP
        ,$FETCH
        (AX)DD(BU,48,6),TTAAAAAAX
        ,RELFWA.(I)
        ,FWA.(I)
        ,N.(I)
        ,0.             (described as "M." following)
        B,ERROR'        Error return
        B,END'          End return
        (normal return)
The type-area name becomes a 48-bit alphanumeric DD.  The trailing X
is the (AX) entry's END-OF-STATEMENT CHARACTER: C28-6129 printed p.16
(quoted in strap/charsets.py): "The second character in the entry mode
field is known as the end-of-statement character ... This character is
not compiled."  p.47's "(IQSX)...DOWNX" and "(IQS*)...*" are the same
device.

$ABEX, printed p.23, prints the macro as a bare "MABEX" but its
expansion carries ",FWA.(I)".  The general rule produces both forms:
MABEX alone gives two half-words, MABEX,FWA gives three.  Both are
kept.

THE BASIC SET.  J28-6128 p.2: "Except for a very basic set, the
operations in SMAC are specified by the user."  The bulletin does not
list the basic set.  C22-6678-1 p.47, a SMAC program, ends "MEND,INIT".
MEND appears nowhere else in the manuals held.  CHOSEN: MEND,X is
SMAC's end statement and is put out as STRAP's END,X.  That is
inferred from p.47's use alone, and labelled so.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from opcodes import MCP_PSEUDO_OPS_1964            # noqa: E402
from smac import Library                           # noqa: E402

# Appendix A codes with no printed macro form (see the header).
GENERAL_ONLY = ("SPFLS", "BSFLS", "STRG", "FECRG")


def _cards(rows):
    return "\n".join((" " + tag.ljust(8) + var).rstrip() for tag, var in rows)


def general(op):
    """The p.14 rule as a Generator Language generator."""
    return _cards([
        ("", "MBGEN"),
        ("", "MOUTV,1,SKHEAD,0,N,SKPARM,1"),
        ("", "MEXIT"),
        ("SKHEAD", "MBSKL"),
        ("/2/", "B,$MCP"),
        ("", ",$" + op),
        ("SKPARM", "MBSKL"),
        ("", ",/1/"),
        ("", "MEGEN"),
    ])


SCR = _cards([
    ("", "MBGEN"),
    ("", "MOUTF,SKSCR,3"),
    ("", "MEXIT"),
    ("SKSCR", "MBSKL"),
    ("/2/", "B,$MCP"),
    ("", ",$SCR"),
    ("", ",/4/"),
    ("", ",/5/"),
    ("", ",0.'    M."),
    ("", "B,/6/'  END RETURN"),
    ("", "MEGEN"),
])

FETCH = _cards([
    ("", "MBGEN"),
    ("", "MOUTF,SKFETCH,6"),
    ("", "MEXIT"),
    ("SKFETCH", "MBSKL"),
    ("/2/", "B,$MCP"),
    ("", ",$FETCH"),
    ("", "(AX)DD(BU,48,6),/4/X"),
    ("", ",/5/"),
    ("", ",/6/"),
    ("", ",/7/"),
    ("", ",0.'    M."),
    ("", "B,/8/'  ERROR RETURN"),
    ("", "B,/9/'  END RETURN"),
    ("", "MEGEN"),
])

MEND = _cards([
    ("", "MBGEN"),
    ("", "MOUTF,SKEND,1"),
    ("", "MEXIT"),
    ("SKEND", "MBSKL"),
    ("/2/", "END,/4/"),
    ("", "MEGEN"),
])

SPECIAL = {"SCR": SCR, "FETCH": FETCH}


def library():
    lib = Library()
    for op in MCP_PSEUDO_OPS_1964:
        lib.add(["M" + op], SPECIAL.get(op) or general(op))
    lib.add(["MEND"], MEND)
    return lib
