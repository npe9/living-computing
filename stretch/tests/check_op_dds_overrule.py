#!/usr/bin/env python3
"""An operation and a data description that disagree (C28-6129 printed p.7).

p.7: "Cases can arise from programmer errors in which a data description
and an operation are not mutually consistent (when the operation mnemonic
specifies a floating point operation and the use mode in the data
description is binary unsigned, for example).  In this case the
operation overrules."  It does not say what is compiled: the op's no-dds
default (C22-6729 p.140 Box 5) and the dds's own d bit (Fig. 25 p.193)
are both live readings, and they differ on BU and DU.  No printed row is
a witness (the two "DL(BU," rows in the listing reading are names ending
in D, read in the ink: MCP printed p.188 line 8, p.368 line 32).  So both
directions are REFUSED by name, in strap_asm and in the STRAP II host's
op table, where before they raised a bare KeyError.  An unknown op with a
dds now gets the ordinary "unknown mnemonic" error, not a KeyError.

Checks:
  refused   FP-only op with a VFL dds (BU, B, DU, D; a sign-modified
            form) and VFL-only op with N or U: AssemblerError naming p.7
  unknown   an unknown op with a VFL or FP dds: "unknown mnemonic"
  optable   lookup() gives None for all of these
  controls  ambiguous ops (K, L) take either dds; LN(BU), STN(B,..),
            -MG(BU) stay VFL; SRT(N), E+(U) stay FP; M+1(BU) stays VFL

MEASURED INJECTIONS (each on a copy, reverted by cmp):
    control (before and after)               PASS
    the FP-only refusal removed              FAIL refused (SRT(BU) falls to
                                             "unknown mnemonic")
    the VFL-only refusal removed             FAIL refused (M+1(N) KeyError)
    the N/U branch's unknown guard removed   FAIL unknown (XYZ(N) KeyError)
    the VFL branch's unknown guard removed   FAIL unknown, optable (KeyError)
    strap_asm as it was before the fix       FAIL refused, unknown, optable
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "strap"))
import strap_asm as a                      # noqa: E402
from strap2 import optable                  # noqa: E402

failures = []


def check(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + ("" if ok else ": " + detail))
    if not ok:
        failures.append(name)


def assemble(stmt):
    try:
        a.assemble(" " + stmt + "\n")
        return "ok"
    except a.AssemblerError as e:
        return "AE:" + str(e)
    except Exception as e:                  # the old failure mode
        return type(e).__name__ + ":" + str(e)


REFUSED = ["SRT(BU),100", "SHF(B),3", "DL(DU),100", "E-(D),1", "KMG(BU),100",
           "M+1(N),100", "M+1(U),100"]
UNKNOWN = ["XYZ(BU),100", "XYZ(N),100"]
CONTROLS = ["K(N),100", "K(BU),100", "L(U),100", "L(B,24),100", "LN(BU),100",
            "STN(B,24,8),100", "-MG(BU),100", "SRT(N),100", "E+(U),1",
            "M+1(BU),100", "SRT,100", "M+1,100"]

bad = [(s, r) for s in REFUSED for r in [assemble(s)]
       if not (r.startswith("AE:") and "p.7" in r and "overrules" in r)]
check("refused: op and dds disagree -> AssemblerError citing p.7", not bad, str(bad))

bad = [(s, r) for s in UNKNOWN for r in [assemble(s)]
       if not (r.startswith("AE:") and "unknown mnemonic" in r)]
check("unknown op with a dds -> 'unknown mnemonic'", not bad, str(bad))

bad = [(s, r) for s in CONTROLS for r in [assemble(s)] if r != "ok"]
check("controls assemble", not bad, str(bad))

LOOK = [("SRT", "BU", None), ("SHF", "B", None), ("DL", "DU", None),
        ("M+1", "N", None), ("XYZ", "BU", None), ("XYZ", "N", None),
        ("SRT", "N", "fp"), ("M+1", "BU", "vfl"), ("K", "N", "fp"),
        ("K", "BU", "vfl")]
bad = []
for op, mode, want in LOOK:
    try:
        e = optable.lookup(op, mode)
        got = None if e is None else e.kind
    except Exception as ex:
        got = type(ex).__name__
    if got != want:
        bad.append((op, mode, got, want))
check("optable: refused and unknown are None, controls keep their kind", not bad, str(bad))

if failures:
    print(f"*** {len(failures)} CHECK(S) FAILED ***")
    sys.exit(1)
print("ALL CHECKS PASSED")
