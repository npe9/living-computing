#!/usr/bin/env python3
"""Vectors for EspLinkTb.bsv, the expected side computed by the ESP32's C.

    python3 esplink_vectors.py ESPLINK_REF DIR

ESPLINK_REF is esplink_ref.c built against the relay's relay.c (the codec
the ESP32 runs). Everything the testbench expects comes from it: the
encoded link bytes of every frame the FPGA sends (relay_encode), and the
frames and counters that relay_feed gives for the byte stream the FPGA
receives. This script only chooses the inputs:

TX (SONIC -> link): the 276 frames the SONIC sent in the join
(sonic_tests/join_echo.trace.gz "T" lines), then edge cases. These are
1 and 14 bytes; lengths 248..262 of nonzero bytes, so the 254-byte COBS
blocks end at every place relative to the type byte and the CRC; 508 and
762 of 0xFF; 60 zeros; 1518 random; 1518 of 0x01. A 1519-byte frame comes
last, which relay_encode refuses: the RTL must drop it and count txTooLong.

RX (link -> SONIC): the 339 frames the SONIC received in the join (the "X"
lines), each relay_encode'd, interleaved with bad input. That input is
test_ethrelay.py's test_bad_packets_dropped stream (bad CRC, COBS running
off the end, a runt, 2000 bytes past RELAY_MAX_WIRE, an unknown type, and
undelimited line noise), plus:
  * status (0x53) packets, good but not frames;
  * a frame of 1519 bytes, too long a body (cobs_decode -1: bad_cobs);
  * 1530 wire bytes that decode to 1524 body bytes (bad_cobs);
  * exactly RELAY_MAX_WIRE + 1 bytes (overflow);
  * 4- and 5-byte bodies (bad_len), a 13-byte frame (bad_len), and a
    1518-byte frame (good);
  * a run of idle 0x00 bytes;
  * one byte of a good packet sent with a bad stop bit: its data bits are
    intact, so the C (which has no UART) takes the packet; the RTL must
    count one framing error and still pass the byte on.

Files (hex, one record a line, a record with bit "valid" 0 ends a list):
  txin.hex   {valid, last, data}    frames into the EspLink tx port
  txw.hex    {valid, data}          the expected link bytes out of txd
  rxw.hex    {valid, badstop, data} link bytes driven onto rxd
  rxf.hex    {valid, last, data}    the good frames expected out of rx
  expect.hex the expected counters: good bad_crc bad_cobs bad_len
             overflows bad_type framing lost txTooLong (16 bits each)
"""
import gzip
import os
import random
import struct
import subprocess
import sys
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(HERE)),
                                "tests"))
import test_ethrelay as tr    # noqa: E402  (packet(), the bad stream's parts)

TRACE = os.path.join(HERE, "sonic_tests", "join_echo.trace.gz")


def c_encode(ref, frames):
    inp = "".join(f.hex() + "\n" for f in frames)
    out = subprocess.run([ref, "enc"], input=inp, capture_output=True,
                         text=True, check=True).stdout.split("\n")
    return [None if o == "TOOLONG" else bytes.fromhex(o)
            for o in out[:len(frames)]]


def c_decode(ref, stream):
    out = subprocess.run([ref, "dec"], input=stream.hex(),
                         capture_output=True, text=True,
                         check=True).stdout.split("\n")
    frames, counts = [], None
    for line in out:
        if line.startswith("F "):
            frames.append(bytes.fromhex(line[2:]))
        elif line.startswith("C "):
            counts = [int(x) for x in line[2:].split()]
    return frames, counts


def main():
    ref, out = sys.argv[1], sys.argv[2]
    rnd = random.Random(7030)
    sent, recv = [], []
    with gzip.open(TRACE, "rt") as f:
        for line in f:
            p = line.split()
            if p[0] == "T":
                sent.append(bytes.fromhex(p[1]))
            elif p[0] == "X":
                recv.append(bytes.fromhex(p[2]))

    # ---- TX
    tx = list(sent)
    tx.append(bytes([0x5A]))
    tx.append(bytes(rnd.randrange(1, 256) for _ in range(14)))
    for n in range(248, 263):
        tx.append(bytes(rnd.randrange(1, 256) for _ in range(n)))
    tx += [b"\xff" * 508, b"\xff" * 762, bytes(60),
           bytes(rnd.randrange(256) for _ in range(1518)), b"\x01" * 1518,
           bytes(rnd.randrange(256) for _ in range(1519))]
    enc = c_encode(ref, tx)
    assert enc[-1] is None and all(e is not None for e in enc[:-1])
    txw = b"".join(e for e in enc if e is not None)

    # ---- RX
    p = tr.packet(tr.T_ETH, bytes(range(1, 61)))
    bad = [
        p[:5] + bytes([p[5] ^ 1]) + p[6:],                 # bad CRC
        bytes([0x40, 1, 2, 3]) + b"\0",                    # COBS off the end
        tr.packet(tr.T_ETH, bytes(13)),                    # runt
        b"\x01" * 2000 + b"\0",                            # > MAX_WIRE
        tr.packet(0x99, bytes(60)),                        # unknown type
        bytes([0x13, 0x37, 0xff]),                         # noise, no 0x00
        tr.packet(tr.T_STATUS, b"\x01\x02\x00\x07"),       # status: good
        tr.packet(tr.T_ETH, bytes(rnd.randrange(256) for _ in range(1519))),
        (b"\xff" + b"\x11" * 254) * 6 + b"\0",             # body 1524
        b"\x22" * 1531 + b"\0",                            # MAX_WIRE + 1
        tr.cobs_encode(b"\x45" + struct.pack("<I", zlib.crc32(b"\x45"))
                       [:3]) + b"\0",                      # 4-byte body
        tr.packet(tr.T_ETH, b""),                          # 5-byte body
        tr.packet(tr.T_STATUS, b""),                       # status, empty
        b"\0" * 9,                                         # idle fill
    ]
    good_enc = c_encode(ref, recv + [
        bytes(rnd.randrange(256) for _ in range(1518)), b"\x00" * 14])
    stream = bytearray()
    badstop = set()
    for i, g in enumerate(good_enc):
        if i % 20 == 3 and bad:
            stream += bad.pop(0)
        if i == 200:
            # a byte with a bad stop bit, in the middle of a packet
            pk = bytearray(g)
            badstop.add(len(stream) + 10)
            stream += pk
            continue
        stream += g
    assert not bad
    frames, counts = c_decode(ref, bytes(stream))

    # ---- files
    with open(os.path.join(out, "txin.hex"), "w") as f:
        for fr in tx:
            for i, b in enumerate(fr):
                f.write("%03x\n" % (0x200 | (i == len(fr) - 1) << 8 | b))
        f.write("000\n")
    with open(os.path.join(out, "txw.hex"), "w") as f:
        for b in txw:
            f.write("%03x\n" % (0x100 | b))
        f.write("000\n")
    with open(os.path.join(out, "rxw.hex"), "w") as f:
        for i, b in enumerate(stream):
            f.write("%03x\n" % (0x200 | (i in badstop) << 8 | b))
        f.write("000\n")
    with open(os.path.join(out, "rxf.hex"), "w") as f:
        for fr in frames:
            for i, b in enumerate(fr):
                f.write("%03x\n" % (0x200 | (i == len(fr) - 1) << 8 | b))
        f.write("000\n")
    good, bad_crc, bad_cobs, bad_len, ovf, bad_type = counts
    with open(os.path.join(out, "expect.hex"), "w") as f:
        f.write("".join("%04x" % v for v in (
            good, bad_crc, bad_cobs, bad_len, ovf, bad_type, len(badstop), 0,
            1)) + "\n")
    print("esplink_vectors: tx %d frames (%d link bytes, 1 too long); "
          "rx %d link bytes -> %d frames, good %d bad_crc %d bad_cobs %d "
          "bad_len %d overflows %d bad_type %d, framing %d" % (
              len(tx), len(txw), len(stream), len(frames), good, bad_crc,
              bad_cobs, bad_len, ovf, bad_type, len(badstop)))


if __name__ == "__main__":
    main()
