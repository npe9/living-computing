#!/usr/bin/env python3
"""verify_mktape.py -- mktape.py's IPL tape image, round-tripped
through the exact byte-for-byte reader bsv/sd_reference/host_tape.c
uses, and checked against the assembly it came from.

WHAT THIS DOES AND DOES NOT PROVE.  It proves the image is the words
the assembler produced, in the order and byte-order the Bluesim and
SD legs will read them, with a correctly formed control word in front.
It does NOT prove the 7030 would boot it: nothing here runs the model,
because the IPL mechanism it needs (NEXT.md 5k items 6 and 7) is not
built yet.  That is the point of the milestone order in
docs/boot_plan.md -- the image format can be settled, and tested,
before the hardware that consumes it exists.
"""
import struct
import subprocess
import sys
import tempfile
import os

from strap_asm import assemble

PROGRAM = "programs/io_tape.strap"


def read_as_host_tape_c_does(path):
    """host_tape.c: 8 bytes per word, w = (w << 8) | b[k].
    Big-endian -- byte 0 of the record is IBM bits 0-7, the leftmost
    byte of the word."""
    img = []
    with open(path, "rb") as f:
        while True:
            b = f.read(8)
            if len(b) != 8:
                break
            w = 0
            for k in range(8):
                w = (w << 8) | b[k]
            img.append(w)
    return img


def main():
    failed = 0
    with tempfile.TemporaryDirectory() as td:
        out = os.path.join(td, "t.tape")
        r = subprocess.run([sys.executable, "mktape.py", PROGRAM, out],
                           capture_output=True, text=True)
        if r.returncode != 0:
            print("FAIL mktape.py exited", r.returncode)
            print(r.stderr)
            sys.exit(1)

        prog = assemble(open(PROGRAM).read())
        img = read_as_host_tape_c_does(out)

        cw = img[0]
        data_addr = (cw >> 46) & 0x3FFFF
        ready = (cw >> 45) & 1
        chain = (cw >> 38) & 1
        count = (cw >> 18) & 0x3FFFF
        refill = cw & 0x3FFFF

        lo, hi = min(prog.words), max(prog.words)

        def check(name, got, want):
            nonlocal failed
            if got == want:
                print(f"PASS {name} = {got}")
            else:
                print(f"FAIL {name} = {got}, expected {want}")
                failed += 1

        # The control word, against Reference Manual printed p.126's
        # description of what location 4 must contain.
        check("cw_dataAddr_is_program_start", data_addr, lo)
        check("cw_count_covers_the_image", count, hi - lo + 1)
        check("cw_refill_is_1_as_MCP_uses", refill, 1)
        check("cw_unitReady", ready, 1)
        # The refilled word is the LAST in the chain here, so it must
        # not itself chain -- otherwise the exchange would try to
        # refill again off the end of the program.
        check("cw_does_not_chain", chain, 0)
        check("image_is_control_word_plus_body", len(img), 1 + count)

        # Every word, in order, against the assembly.
        bad = 0
        for i in range(count):
            want = prog.words.get(lo + i, 0)
            if img[1 + i] != want:
                if bad < 5:
                    print(f"FAIL word {lo+i}: tape {img[1+i]:016x}, "
                          f"assembly {want:016x}")
                bad += 1
        if bad:
            failed += bad
        else:
            print(f"PASS all {count} words match the assembly, in order")

    print()
    if failed:
        print(f"{failed} TEST(S) FAILED")
        sys.exit(1)
    print("ALL TESTS PASSED")


if __name__ == "__main__":
    main()
