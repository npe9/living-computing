#!/usr/bin/env python3
"""Record every write s9term makes to the LCD (`Lcdisp`, IOACK 0x3000)
during the 8½ session of docs/p9boot.md "8½ as `tor`", replayed with no
QEMU exactly as tests/test_p9term.py EightHalfReplayTest does it with
P9TERM_8HALF=ls (tests/net/8half.pcap plus the live run's input log).

Output (all in OUT, default hobbit/fpga/build/lcd):

  lcd_writes.bin   one 5-byte record per write, in order:
                     byte 0  bit 0 = register (0 ctl, 1 data), bits 7..4
                             = the byte-enable mask p9boot passed
                     bytes 1..4  the 32-bit data word, little-endian
  lcd_level.bin    p9term.LcdPanel.level at the end: 768*1024 bytes, one
                   2-bit cell per byte, row major
  lcd_model.png    the same panel as grey (level 3 white): LcdPanel.grey()
  screen.png       the kernel bitmap (gscreen), p9boot --screen's dump

The record format is what fpga/dev/lcd_tb.cpp replays.  The run also
replays lcd_writes.bin into a fresh LcdPanel and checks it reproduces
the live panel, so the recording is complete.

    python3 hobbit/fpga/dev/lcd_capture.py [--q1] [OUT]

--q1 stops at the live run's first screenshot (1.39 G steps) instead of
its end (2.99 G steps).
"""

import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
HOBBIT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(HOBBIT, "tools"))
sys.path.insert(0, os.path.join(HOBBIT, "tests"))

import p9boot  # noqa: E402
import p9term  # noqa: E402
import test_p9term as T  # noqa: E402


def replay(path):
    """A fresh p9term.LcdPanel fed the recording."""
    lcd = p9term.LcdPanel()
    with open(path, "rb") as f:
        d = f.read()
    for i in range(0, len(d), 5):
        k = d[i]
        lcd.write(4 * (k & 1), struct.unpack_from("<I", d, i + 1)[0], k >> 4)
    return lcd


def main(argv):
    q1 = "--q1" in argv
    argv = [a for a in argv if a != "--q1"]
    out = argv[0] if argv else os.path.join(HOBBIT, "fpga", "build", "lcd")
    os.makedirs(out, exist_ok=True)
    boot = p9boot.Boot(T.S9TERM)
    boot.script = [(b"il]: ", b"\r"), (b"user[none]: ", b"tor\r"),
                   (b"password: ", b"password\r")]
    rep = p9boot.Replay(T.HALF_PCAP, p9boot.EEPROM_EA)
    boot.attach(p9boot.Wire(boot.sonic.clock, replay=rep))
    boot.set_inputs(["at-cycle %d stop" % T.HALF["q1"][0]] if q1
                    else T.HALF_INPUT)
    rec = open(os.path.join(out, "lcd_writes.bin"), "wb")
    lcd = boot.lcd
    real = lcd.write

    def write(off, data, mask):
        if off in (0, 4):
            rec.write(struct.pack("<BI", (off >> 2) | ((mask & 0xF) << 4),
                                  data & 0xFFFFFFFF))
        else:
            print("lcd_capture: write to +0x%x not recorded" % off,
                  file=sys.stderr)
        real(off, data, mask)

    lcd.write = write
    status = boot.run(4000000000)
    rec.close()
    print("status:", status)
    info, pix = boot.screen_pixels()
    digest = p9boot.screen_digest(pix)
    want = T.HALF["q1" if q1 else "ls"]
    print("steps %d cycles %d pixels sha256 %s (recorded %s)" % (
        boot.steps, boot.cycles, digest, want[2]))
    print("panel_check (bad, written):", boot.panel_check())
    print("writes: ctl %d data %d overruns %d" % (
        lcd.writes[0], lcd.writes[4], lcd.overruns))
    with open(os.path.join(out, "lcd_level.bin"), "wb") as f:
        f.write(bytes(lcd.level))
    boot.dump_lcd(os.path.join(out, "lcd_model.png"))
    boot.dump_screen(os.path.join(out, "screen.png"))
    again = replay(os.path.join(out, "lcd_writes.bin"))
    ok = again.level == lcd.level
    print("replayed recording == live panel:", ok)
    return 0 if ok and digest == want[2] else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
