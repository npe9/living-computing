#!/usr/bin/env python3
"""check_disk_image.py -- checks for the simulated 353's image file
(STRETCH_DISK / STRETCH_DISK_SAVE, bsv/host_tape.c;
docs/disk_subsystem.md §9c).  Driven by tests/run_disk_image_test.sh.

The format is the tape's: 8 bytes per word, big-endian, word i at byte
8*i, i = arc*512 + word.  A saved image is the whole unit, exactly
2^21 * 8 = 16,777,216 bytes.

  check_disk_image.py size  IMAGE
      The saved file is exactly one 353 long.  This is the only check
      that sees a save which drops the last arc: P1's IPL leaves arc
      4095 zero, so its contents cannot tell.
  check_disk_image.py ipl   IMAGE TAPE
      The 33 arcs MCP's P1 run wrote hold the words of the IPL tape
      they came from, at the tape offsets pinned below, and every other
      arc is zero.  The expected words come from the TAPE, never from an
      earlier save.
  check_disk_image.py dump  LOG [IMAGE]
      What decks/io_disk_image.strap read (the MEMDUMP lines in LOG)
      is what IMAGE holds at those arcs, with a short IMAGE zero-filled
      here, independently of host_tape.c.  No IMAGE: every word zero.
  check_disk_image.py short OUT
      Write the short synthetic image the zero-fill check loads.
"""
import re
import sys

DISK_WORDS = 1 << 21
ARC = 512

# WHAT MCP'S P1 RUN LEAVES ON THE DISK, MEASURED 2026-11-24 from a
# saved image: arcs 0-32 (33 arcs, not only the 24 of IPL's first
# 12,288-word WRITE), each one a 512-word run of the IPL tape, and
# nothing else.  Arc a is tape words TAPE_BASE + TAPE_STRIDE*a onward:
# the PROSA part of the tape is prosa.tape_words()'s 513-word records
# (gen_mcp_boot_tb.py, "IT IS WRITTEN IN prosa.tape_words()'s CHUNKED
# FORM"), so successive arcs sit 513 tape words apart.  Arcs 16, 22 and
# 23 are zero ON THE TAPE too, which is why no single arc is required
# to be non-zero; 10,805 words of the 33 arcs are.
IPL_ARCS = 33
TAPE_BASE = 370
TAPE_STRIDE = 513

# io_disk_image.strap's reads, in its order: (arc, words).
READS = [(0, 8), (32, 8), (33, 2), (4095, 2)]

# THE SHORT IMAGE: arcs 0..31 whole, 5 words of arc 32, then 3 bytes of
# a sixth.  So arc 32 word 5 is a PARTIAL word (its last 5 bytes are
# zero-filled) and words 6-7, arc 33 and arc 4095 lie past the end.
SHORT_WORDS = 32 * ARC + 5
SHORT_TAIL = bytes([0xA5, 0x5A, 0xC3])


def words_of(data):
    """Big-endian words, a short last word zero-filled."""
    data = data + bytes(-len(data) % 8)
    return [int.from_bytes(data[8 * i:8 * i + 8], "big")
            for i in range(len(data) // 8)]


def word_at(words, i):
    return words[i] if i < len(words) else 0


def fail(msg):
    print(f"FAIL {msg}")
    return 1


def cmd_size(image):
    n = len(open(image, "rb").read())
    if n != DISK_WORDS * 8:
        return fail(f"disk_image_size: {image} is {n} bytes, "
                    f"expected {DISK_WORDS * 8}")
    print(f"PASS disk_image_size = {n} bytes (2^21 words)")
    return 0


def cmd_ipl(image, tape):
    disk = words_of(open(image, "rb").read())
    tw = words_of(open(tape, "rb").read())
    bad = 0
    nonzero = 0
    for arc in range(IPL_ARCS):
        got = disk[arc * ARC:(arc + 1) * ARC]
        base = TAPE_BASE + TAPE_STRIDE * arc
        want = [word_at(tw, base + w) for w in range(ARC)]
        nonzero += sum(1 for v in want if v)
        diff = [w for w in range(ARC) if got[w] != want[w]]
        if diff:
            w = diff[0]
            bad += fail(f"disk_image_ipl_arc{arc}: {len(diff)} words differ "
                        f"from tape words {base}.., first "
                        f"at word {w}: {got[w]:016x}, expected {want[w]:016x}")
    if nonzero != 10805:
        bad += fail(f"disk_image_ipl_nonzero: the pinned tape words hold "
                    f"{nonzero} non-zero words, measured 10805")
    print(f"{'PASS' if not bad else 'FAIL'} disk_image_ipl_arcs: arcs 0-"
          f"{IPL_ARCS - 1} = tape words {TAPE_BASE} + {TAPE_STRIDE}*arc, "
          f"{nonzero} of them non-zero")
    rest = [i for i in range(IPL_ARCS * ARC, DISK_WORDS) if disk[i]]
    if rest:
        bad += fail(f"disk_image_rest_zero: {len(rest)} non-zero words past "
                    f"arc {IPL_ARCS - 1}, first at word {rest[0]}")
    else:
        print(f"PASS disk_image_rest_zero: arcs {IPL_ARCS}-4095 are zero")
    return 1 if bad else 0


def cmd_dump(log, image=None):
    words = words_of(open(image, "rb").read()) if image else []
    dump = [int(m.group(1), 16) for m in
            re.finditer(r"^MEMDUMP \d+ ([0-9a-fA-F]{16})$",
                        open(log).read(), re.M)]
    want = [word_at(words, arc * ARC + w) for arc, n in READS
            for w in range(n)]
    if len(dump) != len(want):
        return fail(f"disk_image_read_count: {len(dump)} MEMDUMP words, "
                    f"expected {len(want)}")
    bad = 0
    k = 0
    for arc, n in READS:
        for w in range(n):
            if dump[k] != want[k]:
                bad += fail(f"disk_image_read_arc{arc}_word{w} = "
                            f"{dump[k]:016x}, expected {want[k]:016x}")
            k += 1
    nz = sum(1 for v in want if v)
    print(f"{'PASS' if not bad else 'FAIL'} disk_image_read: {len(want)} "
          f"words read off the disk, {nz} non-zero, "
          f"{'from ' + image if image else 'no image'}")
    return 1 if bad else 0


def cmd_short(out):
    data = bytearray()
    for i in range(SHORT_WORDS):
        # Non-zero in every byte, distinct per word.
        data += (0x5100000000000000 | (i * 0x0101_0101 + 0x1111_1111)
                 ).to_bytes(8, "big")
    data += SHORT_TAIL
    open(out, "wb").write(bytes(data))
    print(f"wrote {out}: {len(data)} bytes ({SHORT_WORDS} words + "
          f"{len(SHORT_TAIL)} bytes)")
    return 0


def main(argv):
    cmd, args = argv[1], argv[2:]
    fn = {"size": cmd_size, "ipl": cmd_ipl, "dump": cmd_dump,
          "short": cmd_short}[cmd]
    return fn(*args)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
