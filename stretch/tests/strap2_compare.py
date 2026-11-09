#!/usr/bin/env python3
"""strap2_compare.py [decks...] -- assemble decks with both assemblers and compare.

strap_asm is scaffolding, so a difference is a question and not a verdict, but
it is verified against the listings across this corpus, so a difference needs
explaining.  Prints one line per deck that differs, then the counts.
"""
import glob
import os
import sys
from concurrent.futures import ProcessPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "strap"))
import strap_asm                # noqa: E402
import strap2                   # noqa: E402


def one(path):
    src = open(path).read()
    base = os.path.basename(path)
    try:
        a = strap_asm.assemble(src)
    except strap_asm.AssemblerError as x:
        a = None
        aerr = str(x)
    try:
        b = strap2.assemble(src, strap_asm.DEFAULT_ORIGIN_BITS)
    except Exception as x:     # noqa: BLE001  a crash is a result here
        if a is None:
            return base, "both-refuse", ""
        return base, "strap2-refuses", f"{type(x).__name__}: {x}"[:150]
    if a is None:
        return base, "strap_asm-refuses", aerr[:150]
    wa = {k: v for k, v in a.words.items()}
    wb = {k: v for k, v in b.words.items()}
    diff = [k for k in sorted(set(wa) | set(wb)) if wa.get(k, 0) != wb.get(k, 0)]
    if diff:
        k = diff[0]
        return base, "words", (f"{len(diff)} words; first {k:o}: "
                               f"asm {wa.get(k, 0):016x} strap2 {wb.get(k, 0):016x}")
    syms = [s for s in a.symtab if s in b.symtab and a.symtab[s] != b.symtab[s]]
    miss = [s for s in a.symtab if s not in b.symtab]
    if syms or miss:
        s = (syms + miss)[0]
        return base, "symbols", f"{len(syms)} differ, {len(miss)} missing; {s}: {a.symtab[s]} {b.symtab.get(s)}"
    if a.end_pc != b.end_pc:
        return base, "end", f"{a.end_pc} {b.end_pc}"
    return base, "same", ""


if __name__ == "__main__":
    paths = sys.argv[1:] or sorted(glob.glob(os.path.join(HERE, "..", "decks", "*.strap")))
    counts = {}
    with ProcessPoolExecutor() as ex:
        for base, how, detail in ex.map(one, paths):
            counts[how] = counts.get(how, 0) + 1
            if how not in ("same", "both-refuse"):
                print(f"{how:18} {base}: {detail}")
    print(counts)
