#!/usr/bin/env python3
"""ASCII to the scan codes the release's `kbd.c` decodes.

The release's `sys/src/9/hobbit/screen.c` calls `kbdinit(2)`: the
console's input is a scan-code keyboard on Quart channel 2 (600 baud,
odd parity), and `rawkbdputc` turns each code into a character through
`keymap[]` (or `skeymap[]` while a shift key is down); a code with the
`Up` bit (0x80) set is a release, ignored except for the modifiers.
s9term has no `kbd.c` (docs/s9term.md), a kernel linked from the release
(`9term`, docs/plan9_boot_plan.md A3) has.

The tables are read out of the vendored `kbd.c` itself (its enums and
the two arrays), not retyped.  `encode(text)` gives, for each character,
the first scan code whose `keymap[]` entry is that character (press,
release); failing that, the first `skeymap[]` one, wrapped in `Lshift`
press and release.  `\\r` is typed as the key whose code maps to `\\n`
(Return): rawkbdputc hands `\\n` itself to kbdputc, there is no
`kbdcr2nl` on this path.  Other control characters are Lctrl and the
letter (rawkbdputc's `ch &= 0x1f`).  A character no key produces raises ValueError.

  python3 tools/p9scancode.py 'echo hello|wc'   # prints the codes
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
KBD_C = os.path.join(HERE, "plan9-1e", "sys", "src", "9", "hobbit", "kbd.c")
UP = 0x80


def _cvalue(tok, names):
    tok = tok.strip()
    m = re.fullmatch(r"'(\\?.)'", tok)
    if m:
        s = m.group(1)
        return {"\\n": 10, "\\t": 9, "\\b": 8, "\\\\": 92,
                "\\'": 39}.get(s, ord(s[-1]))
    m = re.fullmatch(r"\(?(-?)(0x[0-9a-fA-F]+|\d+)\)?", tok)
    if m:
        return (-1 if m.group(1) else 1) * int(m.group(2), 0)
    if tok in names:
        return names[tok]
    m = re.fullmatch(r"(.+)<<(.+)", tok)
    if m:
        return _cvalue(m.group(1), names) << _cvalue(m.group(2), names)
    raise ValueError("kbd.c: cannot evaluate %r" % tok)


def read_tables(path=KBD_C):
    """(keymap, skeymap, names) from kbd.c's enums and arrays."""
    with open(path) as f:
        src = re.sub(r"/\*.*?\*/", "", f.read(), flags=re.S)
    names = {}
    for name, val in re.findall(r"^#define\s+(\w+)\s+(.+?)\s*$", src, re.M):
        names[name] = _cvalue(val, names)
    for body in re.findall(r"enum\s*\{(.*?)\}", src, re.S):
        for item in body.split(","):
            if "=" in item:
                name, val = item.split("=", 1)
                names[name.strip()] = _cvalue(val, names)
    tables = {}
    for name in ("keymap", "skeymap"):
        m = re.search(r"static short %s\[\]\s*=\s*\{(.*?)\};" % name, src,
                      re.S)
        toks = re.findall(r"'(?:\\.|[^'\\])'|[^,\s]+", m.group(1))
        tables[name] = [_cvalue(t, names) for t in toks]
    return tables["keymap"], tables["skeymap"], names


class Encoder:
    def __init__(self, path=KBD_C):
        self.keymap, self.skeymap, self.names = read_tables(path)
        self.shift = self.names["Lshift"]

    def key(self, ch):
        c = 10 if ch == 13 else ch
        if c < 0x20 and c not in (8, 9, 10, 27):
            # rawkbdputc: `if(ctrled) ch &= 0x1f`; the small keymap values
            # are the modifier codes themselves, not characters.
            ctrl = self.names["Lctrl"]
            return bytes([ctrl]) + self.key(c | 0x60) + bytes([ctrl | UP])
        if c in self.keymap:
            k = self.keymap.index(c)
            return bytes([k, k | UP])
        if c in self.skeymap:
            k = self.skeymap.index(c)
            return bytes([self.shift, k, k | UP, self.shift | UP])
        raise ValueError("kbd.c: no key types %r" % chr(ch))

    def encode(self, text):
        return b"".join(self.key(c) for c in bytes(text))


def main(argv):
    enc = Encoder()
    for arg in argv:
        print(" ".join("%02x" % b for b in enc.encode(arg.encode())))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
