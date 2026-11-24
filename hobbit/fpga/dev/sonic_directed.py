#!/usr/bin/env python3
"""A directed SONIC trace: the paths the kernel's join does not take.

    python3 sonic_directed.py sonic_tests/directed.trace.gz

The join (sonic_tests/join_echo.trace.gz) receives every frame into a
fresh buffer (eobc = buffer words - 2, so Lpkt and Rrra on each frame),
never runs out of receive descriptors, never refuses a frame, and sends
one single-fragment descriptor per Txp.  This script drives a fresh
p9boot.Sonic, on a real p9boot.Board memory, through the rest, and
records it with sonic_trace.tap in the same trace format:

* several frames packed into one buffer (Lpkt only when the buffer runs
  low; one frame leaves exactly eobc words, which is not yet low), the
  Rrra wrap from rea to rsa;
* the filter: unicast to the CAM entry, unicast elsewhere and multicast
  refused (rcr without Pro), broadcast with and without Brd, a CAM entry
  loaded but not enabled, Pro accepting any unicast, the receiver off;
* running out of descriptors: Rde with the descriptor kept, a frame
  dropped while the link still has EOL (mpt), then the link freed and the
  next frame taking the kept descriptor's path (in_use, crda = link,
  Pktrx);
* transmit: two chained descriptors in one Txp, fragments at byte
  offsets 1, 2 and 3 and of length 0, then a second Txp that starts at the
  descriptor the EOL link left in ctda;
* isr write-one-to-clear and imr, so irq rises and falls; rsa..rwp
  dropping bits 1:0; Rst and the leaving of reset; Rxdis/Rxen; registers
  the model only stores.

Every value is the model's: the script only chooses the inputs.
"""
import gzip
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
HOBBIT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(HOBBIT, "tools"))
sys.path.insert(0, os.path.join(HOBBIT, "sem"))
sys.path.insert(0, HERE)

import p9boot        # noqa: E402
import sonic_trace   # noqa: E402

BASE = 0x80600000     # descriptor area (physical); upper half 0x8060
U = BASE >> 16
EA = bytes([0x52, 0x54, 0x00, 0x00, 0x0B, 0x0B])
OTHER = bytes([0x52, 0x54, 0x00, 0x12, 0x34, 0x56])

# register byte offsets (io.h Sonic: register i at 4*i)
CR, DCR, RCR, TCR, IMR, ISR, UTDA, CTDA = [4 * i for i in range(8)]
URDA, CRDA = 4 * 0x0D, 4 * 0x0E
EOBC, URRA, RSA, REA, RRP, RWP = [4 * i for i in (0x13, 0x14, 0x15, 0x16,
                                                  0x17, 0x18)]
CE, CDP, CDC = 4 * 0x25, 4 * 0x26, 4 * 0x27
RSC, MPT, DCR2 = 4 * 0x2B, 4 * 0x2E, 4 * 0x3F


def frame(dst, n, seed):
    body = bytes((seed * 7 + i * 13) & 0xFF for i in range(n - 14))
    return dst + OTHER + b"\x08\x00" + body


def main():
    out = sys.argv[1]
    board = p9boot.Board()
    s = p9boot.Sonic(board, lambda: 0)
    log = []
    sonic_trace.tap(s, board, log)
    sent = []

    class Wire:
        def transmit(self, f, t):
            log.append("T %s" % f.hex())
            sent.append(f)
    s.wire = Wire()

    def W(off, v):
        s.write(off, v, 0xF)

    def R(off):
        return s.read(off)

    def put(pa, v):                      # the kernel's memory writes
        board.set_word(pa, v)

    def put_bytes(pa, data):
        for i, c in enumerate(data):
            a = pa + i
            board.write(a & ~3, c << (8 * (a & 3)), 1 << (a & 3))

    # --- reset, as devether.c, then leave reset
    R(CR)
    W(CR, 0x0080)
    W(DCR, 0x0420)
    W(CR, 0x0000)
    R(CR)
    # stored-only registers and the masked pointers
    W(TCR, 0x1234)
    W(DCR2, 0xBEEF)
    R(TCR)
    R(DCR2)
    for off in (RSA, REA, RRP, RWP):
        W(off, 0x0123)
        R(off)

    # --- receive resources: two 64-word buffers, rsa..rea holds two
    rra = BASE + 0x100
    bufs = [BASE + 0x1000, BASE + 0x1400]
    for i, b in enumerate(bufs):
        put(rra + 16 * i + 0, b & 0xFFFF)
        put(rra + 16 * i + 4, b >> 16)
        put(rra + 16 * i + 8, 0x0100)      # 256 words = 512 bytes
        put(rra + 16 * i + 12, 0)
    W(URRA, U)
    W(RSA, rra & 0xFFFF)
    W(REA, (rra + 32) & 0xFFFF)
    W(RRP, rra & 0xFFFF)
    W(RWP, (rra + 48) & 0xFFFF)              # never reached
    W(EOBC, 0x0040)                          # Lpkt below 64 words
    W(CR, 0x0100)                            # Rrra
    R(RRP)

    # --- receive descriptors: three, the last with EOL
    rda = BASE + 0x200
    for i in range(3):
        d = rda + 0x20 * i
        for k in range(7):
            put(d + 4 * k, 0)
        put(d + 20, ((rda + 0x20 * (i + 1)) & 0xFFFF) | (1 if i == 2 else 0))
        put(d + 24, 1)                       # in_use: the SONIC's
    W(URDA, U)
    W(CRDA, rda & 0xFFFF)

    # --- CAM: entry 0 our address, entry 3 another, only 0 enabled
    cda = BASE + 0x400
    for n, (ent, ea) in enumerate(((0, EA), (3, OTHER))):
        p = cda + 16 * n
        put(p, ent)
        put(p + 4, ea[1] << 8 | ea[0])
        put(p + 8, ea[3] << 8 | ea[2])
        put(p + 12, ea[5] << 8 | ea[4])
    put(cda + 32, 0x0001)                    # CE word
    W(CDP, cda & 0xFFFF)
    W(CDC, 2)
    W(CR, 0x0200)                            # Lcam
    R(CE)
    R(CDP)
    R(ISR)
    W(ISR, 0xFFFF)
    R(ISR)

    # --- the filter, receiver still off
    W(IMR, 0x0640)                           # Pktrx | Txdn | Rde
    W(RCR, 0x0000)
    s.receive(frame(EA, 60, 1))              # receiver off: dropped
    W(CR, 0x0008)                            # Rxen
    R(CR)
    s.receive(frame(OTHER, 64, 2))           # CAM entry 3 not enabled
    s.receive(frame(b"\xff" * 6, 60, 3))     # broadcast without Brd
    s.receive(frame(b"\x01\x00\x5e\x00\x00\x01", 60, 4))   # multicast
    s.receive(frame(EA, 61, 5))              # ours: descriptor 0
    R(ISR)
    W(ISR, 0x0400)
    R(ISR)
    W(RCR, 0x2000)                           # Brd
    s.receive(frame(b"\xff" * 6, 99, 6))     # descriptor 1, Bc
    W(ISR, 0x0400)
    s.receive(frame(EA, 150, 7))             # descriptor 2: EOL, Rde
    R(ISR)
    R(CRDA)
    s.receive(frame(EA, 70, 8))              # still EOL: mpt
    R(MPT)
    put(rda + 0x40 + 20, (rda + 0x60) & 0xFFFF)   # free the link
    for k in range(7):
        put(rda + 0x60 + 4 * k, 0)
    put(rda + 0x60 + 20, (rda & 0xFFFF) | 1)
    put(rda + 0x60 + 24, 1)
    W(ISR, 0xFFFF)
    # the kept descriptor; 52 bytes (28 words) leave exactly eobc (64)
    # words: no Lpkt yet (rbwc < eobc is strict)
    s.receive(frame(EA, 52, 9))
    R(ISR)
    R(CRDA)
    R(RSC)
    R(RRP)
    W(RCR, 0x3000)                           # Pro | Brd
    W(ISR, 0xFFFF)
    # frame 9's link had EOL again: free it to descriptor 0, which now ends
    # the list, so frame 10 is received (and not counted in mpt)
    put(rda + 0x60 + 20, rda & 0xFFFF)
    put(rda + 20, ((rda + 0x20) & 0xFFFF) | 1)
    put(rda + 24, 1)
    s.receive(frame(OTHER, 66, 10))          # Pro: any unicast; Lpkt, Rrra wraps
    R(ISR)
    R(RSC)
    R(RRP)
    W(CR, 0x0004)                            # Rxdis
    R(CR)
    s.receive(frame(EA, 60, 11))             # off again
    W(CR, 0x0008)
    R(MPT)

    # --- transmit: two chained descriptors, odd fragments
    tda = BASE + 0x600
    tb = BASE + 0x2000
    f1 = frame(OTHER, 80, 20)
    f2 = frame(b"\xff" * 6, 60, 21)
    f3 = frame(OTHER, 64, 22)
    frags = [(tb + 1, f1[:5]), (tb + 0x102, b""), (tb + 0x203, f1[5:65]),
             (tb + 0x302, f1[65:])]
    put(tda + 8, len(f1))
    put(tda + 12, len(frags))
    for i, (pa, data) in enumerate(frags):
        put_bytes(pa, data)
        put(tda + 16 + 12 * i, pa & 0xFFFF)
        put(tda + 20 + 12 * i, pa >> 16)
        put(tda + 24 + 12 * i, len(data))
    t2 = tda + 0x80
    put(tda + 16 + 12 * len(frags), t2 & 0xFFFF)
    put_bytes(tb + 0x400, f2)
    put(t2 + 8, len(f2))
    put(t2 + 12, 1)
    put(t2 + 16, (tb + 0x400) & 0xFFFF)
    put(t2 + 20, (tb + 0x400) >> 16)
    put(t2 + 24, len(f2))
    t3 = tda + 0x100
    put(t2 + 28, (t3 & 0xFFFF) | 1)          # EOL
    put_bytes(tb + 0x502, f3)
    put(t3 + 8, len(f3))
    put(t3 + 12, 1)
    put(t3 + 16, (tb + 0x502) & 0xFFFF)
    put(t3 + 20, (tb + 0x502) >> 16)
    put(t3 + 24, len(f3))
    put(t3 + 28, (tda & 0xFFFF) | 1)
    W(UTDA, U)
    W(CTDA, tda & 0xFFFF)
    W(ISR, 0xFFFF)
    W(CR, 0x0002)                            # Txp: f1, f2
    R(ISR)
    R(CTDA)
    W(ISR, 0x0200)
    W(CR, 0x0002)                            # Txp from ctda (EOL kept): f3
    R(CTDA)
    R(ISR)
    W(IMR, 0)
    R(ISR)
    W(CR, 0x0080)                            # Rst again
    R(CR)
    W(CR, 0x0000)
    R(CR)

    assert sent == [f1, f2, f3], "the model did not send the frames"
    with gzip.open(out, "wt") as f:
        f.write("# directed p9boot.Sonic events (sonic_directed.py)\n")
        for line in log:
            f.write(line + "\n")
    print("sonic_directed: %d events, mpt %d" % (len(log),
                                                 s.regs[s.MPT]))


if __name__ == "__main__":
    main()
