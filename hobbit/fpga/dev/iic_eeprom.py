#!/usr/bin/env python3
"""Write iic_eeprom.hex, the PCF8582's 256 bytes for mkIic's RegFileLoad,
from tools/p9boot.py eeprom_image() (IIC_CHOICES['eeprom']), so the RTL's
EEPROM and the model's cannot drift.  One byte per line, two hex digits.

    python3 iic_eeprom.py [--ea XX:XX:XX:XX:XX:XX] [--clock MHZ] [OUT]
    python3 iic_eeprom.py --check        # iic_eeprom.hex == the model's

Layout (io.h struct Eeprom; what reads it: iic.md "What the EEPROM
holds"): 0..4 magic a6 00 d9 20 10, 5..10 ether address (devether.c),
11 mask, 12 clock in MHz (clock.c delay()), 13 dsp, 14 pcb, 15 rev,
16..255 zero.
"""
import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
HOBBIT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(HOBBIT, "tools"))
sys.path.insert(0, os.path.join(HOBBIT, "sem"))

import p9boot  # noqa: E402

DEFAULT = os.path.join(HERE, "iic_eeprom.hex")


def image(ea=p9boot.EEPROM_EA, clock=None):
    img = bytearray(p9boot.eeprom_image(ea))
    if clock is not None:
        img[12] = clock
    return bytes(img)


def hexlines(img):
    return "".join("%02x\n" % b for b in img)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out", nargs="?", default=DEFAULT)
    ap.add_argument("--ea", help="ether address (default the model's, "
                    "52:54:00:00:0b:0b)")
    ap.add_argument("--clock", type=int, help="Eeprom.clock, MHz: the "
                    "CPU clock delay() is calibrated for (default %d)"
                    % (p9boot.CPU_HZ // 1000000))
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    ea = (bytes(int(x, 16) for x in a.ea.split(":")) if a.ea
          else p9boot.EEPROM_EA)
    text = hexlines(image(ea, a.clock))
    if a.check:
        with open(a.out) as f:
            if f.read() != text:
                raise SystemExit("%s differs from p9boot.eeprom_image()"
                                 % a.out)
        print("%s matches p9boot.eeprom_image()" % a.out)
        return
    with open(a.out, "w") as f:
        f.write(text)


if __name__ == "__main__":
    main()
