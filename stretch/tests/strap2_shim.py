#!/usr/bin/env python3
"""strap2_shim.py SCRIPT [args] -- run a verify_*.py oracle on strap/strap2.

The oracles were written against strap_asm.assemble, and they compare with the
machine code IBM's listings print, so they apply unchanged to any assembler
that keeps its result shape.  The origin is strap_asm's for a deck with no SLC:
STRAP II's own 41 octal (C22-6729 p.33) is tested separately.
"""
import os
import runpy
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "strap"))
import strap_asm                # noqa: E402
import strap2                   # noqa: E402

default_origin = strap_asm.DEFAULT_ORIGIN_BITS


def assemble(source, origin_bits=default_origin):
    return strap2.assemble(source, origin_bits)


strap_asm.assemble = assemble
sys.argv = sys.argv[1:]
sys.path.insert(0, HERE)
runpy.run_path(sys.argv[0], run_name="__main__")
