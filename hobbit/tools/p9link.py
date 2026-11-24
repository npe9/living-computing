#!/usr/bin/env python3
"""p9link.py -- the host side of the ULX3S SoC's host link: the kernel load.

Builds the byte stream that loads the shipped 1e kernel onto the Hobbit
SoC over the FTDI UART (hobbit/fpga/rtl/hostlink.v's protocol;
fpga/README.md, "The host link") and starts it:

  * `B` frames writing the fpi image into the ROM block (physical 0x20+,
    `p9boot.Rom`);
  * `B` frames writing RAM: the kernel's text and data and the ROM's
    hand-off page PPage0 (memsize, argc, env, the fpi vector), exactly the
    memory `p9boot.Boot` starts from (`load_kernel`, `rom_handoff`);
  * `G` with the kernel's entry.

    p9link.py emit OUT [--image IMAGE] [--sparse] [--words N]

`--sparse` sends only the words that are not zero.  That is enough when RAM
is known to be zero, as in the co-simulation's SDRAM model
(fpga/sim/run_soc.sh with SOC_LOAD).  Without it, every word of the 8 MB the
kernel is told about is sent, because a powered-up SDRAM holds no particular
value.

The stream is checked by the co-simulation: `fpga/sim/run_soc.sh` with
`SOC_LOAD=1` loads the SoC with this stream through the UART pins, with no
back door, and must reach the same MATCH as the back-door load.

Not here yet: the board-side session that sends the stream over a serial
port and then answers `F` frames from p9boot's device models.  No serial
port is opened by this file.
"""
import argparse
import pathlib
import struct
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import p9boot          # noqa: E402

ROM_WORDS = 0x4000     # the SoC's ROM block: physical 0x0000-0x3FFF


def frames(words, maxn):
    """Group {addr: value} into runs of consecutive words, at most maxn
    each, and yield `B` frames (big-endian fields)."""
    addrs = sorted(words)
    i = 0
    while i < len(addrs):
        a0 = addrs[i]
        run = [words[a0]]
        i += 1
        while (i < len(addrs) and addrs[i] == a0 + 4 * len(run)
               and len(run) < maxn):
            run.append(words[addrs[i]])
            i += 1
        yield b"B" + struct.pack(">IH", a0, len(run)) + b"".join(
            struct.pack(">I", w) for w in run)


def load_stream(image, sparse, maxn):
    boot = p9boot.Boot(image)
    out = []
    rom = {a: w for a, w in boot.rom.words.items() if a < ROM_WORDS}
    out.extend(frames(rom, maxn))
    b = boot.board
    if sparse:
        ram = {a: w for a, w in b.ram.items()
               if b.ram_lo <= a < b.ram_hi and w}
    else:
        ram = {a: b.ram.get(a, 0) for a in range(b.ram_lo, b.ram_hi, 4)}
    out.extend(frames(ram, maxn))
    out.append(b"G" + struct.pack(">I", boot.k["entry"]))
    return out, len(rom), len(ram), boot.k["entry"]


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    e = sub.add_parser("emit", help="write the load stream to a file")
    e.add_argument("out")
    e.add_argument("--image", default=str(HERE / "plan9-1e" / "hobbit" /
                                          "s9term"))
    e.add_argument("--sparse", action="store_true",
                   help="send only nonzero RAM words (RAM known zero)")
    e.add_argument("--words", type=int, default=256,
                   help="words per B frame (1-65535)")
    args = ap.parse_args(argv)
    if not 1 <= args.words <= 0xFFFF:
        ap.error("--words must be 1-65535")
    fr, nrom, nram, entry = load_stream(args.image, args.sparse, args.words)
    data = b"".join(fr)
    with open(args.out, "wb") as f:
        f.write(data)
    print("p9link: %d frames, %d ROM words, %d RAM words, G %08x, %d bytes"
          % (len(fr), nrom, nram, entry, len(data)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
