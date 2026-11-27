#!/usr/bin/env python3
"""The held PSI-III control stores, read once, for the pu_* inference tools.

Everything is read in memory from docs/nonlocal/psdpim.tar.Z (third-party,
not in git) through asm/psdpim.py and asm/mekbn.py; nothing is extracted.

  psi      syspsi, 32,768 64-bit microinstructions (the PSI-III ESP/KL0 WCS)
  img2     pimm.MEkbn image 2, 0x6800 microinstructions (the KL1 program)
  init     sysinit, 8,286 64-bit words, header load address 0x5000
  idat     sysidat, 1,040 64-bit words, header load address 0x6800
  kl1_wcs  the KL1 configuration of the WCS: image 2 at 0..0x67ff and
           syspsi's 0x6800..0x7fff above it (docs/pu_microcode_inference.md
           section 3 has the evidence that this is how it ran)

Decode roots: KL1 entries from pimm.MEkbn's classes 2/3 (mekbn.Firmware);
KL0 entries from sysidat's classes 0/1 (docs/psi_microword.md 4.4).
Mnemonics: sysinit 0x5b81 + decode index, eight characters, 64-bit
big-endian text (docs/pu_microcode_inference.md section 5).

Usage: imported by asm/pu_cfg.py, asm/pu_sysinit.py, asm/pu_rosetta.py,
asm/pu_smt.py.
"""
import functools
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import mekbn    # noqa: E402
import psdpim   # noqa: E402

INIT_BASE, IDAT_BASE = 0x5000, 0x6800
SHARED_LO = 0x6800            # first syspsi address kept under image 2
IMG1_LEN = 0x5800
MNEMONIC_TABLE = 0x5b80       # header word (count 0x400), names from 0x5b81
DATE_WORD = 0x67ff            # image 2's last word, 2e111993:00000002 (data)


def raw64(raw):
    body = raw[256:]
    return [int.from_bytes(body[i:i + 8], 'little') for i in range(0, len(body) - 7, 8)]


class Stores:
    def __init__(self):
        self.fw = mekbn.Firmware()
        self.psi = mekbn.syspsi()
        self.img2 = self.fw.img2
        self.init = raw64(psdpim.member('PMPSI.DIR/sysinit'))
        self.idat = raw64(psdpim.member('PMPSI.DIR/sysidat'))
        self.init_header = psdpim.member('PMPSI.DIR/sysinit')[:12]
        self.idat_header = psdpim.member('PMPSI.DIR/sysidat')[:12]
        self.kl1_wcs = list(self.img2) + list(self.psi[SHARED_LO:])

    def iw(self, a):
        """sysinit word at its load address a (0x5000..0x705d)."""
        return self.init[a - INIT_BASE]

    # ---- decode entries
    def kl1_roots(self):
        """{address: name} of the KL1 decode entries (classes 2 and 3)."""
        out = {}
        for name, (idx, addr, tag) in self.fw.kl1_entries().items():
            out.setdefault(addr, name)
        return out

    def kl0_start(self, idx):
        """Start address of a class 0/1 entry of sysidat (psi_microword.md 4.4)."""
        r = self.idat[idx]
        if not r:
            return None
        if (r >> 35) & 3 == 0:
            return r & 0x7fff
        return (idx >> 7) << 11 | r & 0x3ff

    def kl0_roots(self):
        """{address: mnemonic} of the KL0 decode entries (sysidat 0..511)."""
        out = {}
        for idx in range(512):
            a = self.kl0_start(idx)
            if a is not None:
                out.setdefault(a, self.mnemonic(idx))
        return out

    def mnemonic(self, idx):
        """sysinit's eight-character name of decode index idx (0..0x3ff)."""
        w = self.iw(MNEMONIC_TABLE + 1 + idx)
        return w.to_bytes(8, 'big').decode('latin1').strip()


@functools.lru_cache(maxsize=1)
def stores():
    return Stores()
