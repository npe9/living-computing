#!/usr/bin/env python3
"""Format and traceability checker for the hand-derived golden traces.

The retirement record is the HRI line -- the Hobbit Retirement Interface,
this project's analogue of riscv-formal's RISC-V Formal Interface (RVFI) --
whose fields are fixed by the repository contract.  A line that still starts
with the retired `RVFI ` prefix is a format error here, never a line that is
silently skipped.

Standard library only, and deliberately not a simulator.  It checks

  * the fixed image format (one 8-digit lowercase word per line, ascending
    from address 0, parcel at even address in bits 31:16),
  * the fixed HRI line format, field by field, and the HRI prefix itself,
  * that each line's `insn` field really is the first two parcels of the
    instruction the image holds at `pc`,
  * that SP and MSP are continuous from line to line and quad-aligned,
  * that the pc sequence is one an instruction of this set can produce,
  * that every retirement line is matched, one for one and in order, by an
    `Lnn.` entry of the sibling `.md`, quoting it verbatim and citing a
    printed page or table.

Usage:  python3 check_golden.py [directory]
Exit status 0 when everything passes, 1 with one message per violation.
"""

import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

HEX_RE = re.compile(r"^[0-9a-f]{8}$")
HRI_RE = re.compile(
    r"^HRI pc=(?P<pc>[0-9a-f]{4}) insn=(?P<insn>[0-9a-f]{8}) "
    r"sp=(?P<spb>[0-9a-f]{8})>(?P<spa>[0-9a-f]{8}) "
    r"msp=(?P<mb>[0-9a-f]{8})>(?P<ma>[0-9a-f]{8}) "
    r"we=(?P<we>[01]) addr=(?P<addr>[0-9a-f]{8}) data=(?P<data>[0-9a-f]{8}) "
    r"mask=(?P<mask>[0-9a-f]{2}) trap=(?P<trap>[01])$")
LNN_RE = re.compile(r"^L(\d\d)\. `(HRI .*)`$", re.M)
# The record used to be called RVFI.  A stale prefix must be reported as a
# format error, not treated as an unknown line.
STALE_RE = re.compile(r"^RVFI\b")
PAGE_RE = re.compile(
    r"(Table \d+-\d+|T\d+-\d+|pp?\. \d+-\d+|section \d+\.\d+)")

# One-parcel control transfers, opcode in bits 14:10: CALL, JMP and the four
# conditional jumps (Table 1-15, p. 1-22).
P1_BRANCH = {0x01, 0x03, 0x04, 0x05, 0x06, 0x07}
# Three-parcel monadic subcodes KCALL, CALL, RETURN, JMP, JMPFN/FY, JMPTN/TY
# (Table 1-19, p. 1-24).
P3_SUBCODE_BRANCH = {0x0, 0x1, 0x2, 0x3, 0x4, 0x5, 0x6, 0x7}


def load_image(path, errs):
    """Return (words, parcels) or None.  parcels maps byte address -> parcel."""
    with open(path, "r", encoding="ascii") as f:
        text = f.read()
    if not text.endswith("\n"):
        errs.append("%s: last line is not newline-terminated" % path)
    lines = text.split("\n")
    if lines and lines[-1] == "":
        lines.pop()
    if not lines:
        errs.append("%s: empty image" % path)
        return None
    words = []
    for n, line in enumerate(lines, start=1):
        if not HEX_RE.match(line):
            errs.append("%s:%d: not one 8-digit lowercase word: %r"
                        % (path, n, line))
            return None
        words.append(int(line, 16))
    parcels = {}
    for i, w in enumerate(words):
        parcels[4 * i] = (w >> 16) & 0xFFFF     # even address in bits 31:16
        parcels[4 * i + 2] = w & 0xFFFF         # odd address in bits 15:0
    return words, parcels


def parcel_count(first, where, errs):
    """Parcel count from the length prefix: bit 15 = 0, 10, 11 (pp. 1-21..1-24)."""
    if first >> 15 == 0:
        return 1
    if first >> 14 == 2:
        return 3
    if first >> 14 == 3:
        return 5
    errs.append("%s: parcel %04x carries an undocumented length prefix"
                % (where, first))
    return None


def is_branch(first, count):
    if count == 1:
        return (first >> 10) in P1_BRANCH
    if count == 3 and (first >> 8) & 0x3F == 0:
        return (first & 0xF) in P3_SUBCODE_BRANCH
    return False


def check_trace(stem, parcels, words, errs):
    tpath = stem + ".trace"
    mpath = stem + ".md"
    with open(tpath, "r", encoding="ascii") as f:
        text = f.read()
    if not text.endswith("\n"):
        errs.append("%s: last line is not newline-terminated" % tpath)
    lines = text.split("\n")
    if lines and lines[-1] == "":
        lines.pop()
    if not lines:
        errs.append("%s: empty trace" % tpath)
        return

    image_end = 4 * len(words)
    expect = None          # pc this line must have, None after a branch
    prev = None
    traps = 0
    last = len(lines) - 1

    for i, line in enumerate(lines):
        where = "%s:%d" % (tpath, i + 1)
        if STALE_RE.match(line):
            errs.append("%s: starts with the retired RVFI prefix; the record is "
                        "the HRI (Hobbit Retirement Interface) line: %r"
                        % (where, line))
            continue
        m = HRI_RE.match(line)
        if not m:
            errs.append("%s: does not match the fixed HRI format: %r"
                        % (where, line))
            continue
        g = {k: int(v, 16) for k, v in m.groupdict().items()}
        if i == 0 and g["pc"] != 0:
            errs.append("%s: first line is not at the entry, pc=%04x"
                        % (where, g["pc"]))
        if expect is not None and g["pc"] != expect:
            errs.append("%s: pc=%04x but the previous instruction leads to %04x"
                        % (where, g["pc"], expect))
        expect = None
        if g["pc"] & 1:
            errs.append("%s: pc is not parcel-aligned" % where)
        if g["pc"] + 2 > image_end:
            errs.append("%s: pc=%04x is outside the image (end %04x)"
                        % (where, g["pc"], image_end))
            continue
        first = parcels[g["pc"]]
        if (g["insn"] >> 16) != first:
            errs.append("%s: insn high half %04x is not the image parcel %04x "
                        "at pc=%04x" % (where, g["insn"] >> 16, first, g["pc"]))
        count = parcel_count(first, where, errs)
        if count is None:
            continue
        if g["pc"] + 2 * count > image_end:
            errs.append("%s: %d-parcel instruction at %04x runs past the image "
                        "end %04x" % (where, count, g["pc"], image_end))
        want_lo = parcels[g["pc"] + 2] if count > 1 else 0
        if (g["insn"] & 0xFFFF) != want_lo:
            errs.append("%s: insn low half %04x should be %04x for a %d-parcel "
                        "instruction"
                        % (where, g["insn"] & 0xFFFF, want_lo, count))
        for name in ("spb", "spa", "mb", "ma"):
            if g[name] & 0xF:
                errs.append("%s: %s=%08x sets pointer bits that do not exist "
                            "(p. 1-17, p. 1-13)" % (where, name, g[name]))
        if g["we"] == 0:
            if g["addr"] or g["data"] or g["mask"]:
                errs.append("%s: we=0 but addr/data/mask are not zero" % where)
        else:
            if g["mask"] == 0:
                errs.append("%s: we=1 with an empty mask" % where)
            if g["mask"] & 0xF0:
                errs.append("%s: mask %02x uses bits above the four data bytes"
                            % (where, g["mask"]))
        if g["trap"]:
            traps += 1
            if i != last:
                errs.append("%s: trap=1 but the run continues" % where)
        if prev is not None:
            if prev["spa"] != g["spb"]:
                errs.append("%s: sp before %08x does not continue the previous "
                            "line's after-value %08x"
                            % (where, g["spb"], prev["spa"]))
            if prev["ma"] != g["mb"]:
                errs.append("%s: msp before %08x does not continue the previous "
                            "line's after-value %08x"
                            % (where, g["mb"], prev["ma"]))
        if not is_branch(first, count):
            expect = g["pc"] + 2 * count
        if i == last and not g["trap"] and expect != image_end:
            errs.append("%s: the last instruction ends at %04x, not at the image "
                        "end %04x; the model would fetch padding"
                        % (where, expect, image_end))
        prev = g

    if traps > 1:
        errs.append("%s: %d trap lines, at most one allowed" % (tpath, traps))

    if not os.path.exists(mpath):
        errs.append("%s: missing" % mpath)
        return
    with open(mpath, "r", encoding="utf-8") as f:
        md = f.read()
    hits = LNN_RE.findall(md)
    if len(hits) != len(lines):
        errs.append("%s: %d Lnn entries for %d trace lines"
                    % (mpath, len(hits), len(lines)))
    for i, (num, quoted) in enumerate(hits):
        if int(num) != i + 1:
            errs.append("%s: entry %s is out of order (expected %02d)"
                        % (mpath, num, i + 1))
            continue
        if i >= len(lines):
            errs.append("%s: entry %s has no trace line" % (mpath, num))
            continue
        if quoted != lines[i]:
            errs.append("%s: entry %s does not quote trace line %d verbatim"
                        % (mpath, num, i + 1))
    starts = [m.start() for m in re.finditer(r"^L\d\d\. ", md, re.M)]
    for i, s in enumerate(starts):
        end = starts[i + 1] if i + 1 < len(starts) else len(md)
        if not PAGE_RE.search(md[s:end]):
            errs.append("%s: entry L%02d cites no printed page or table"
                        % (mpath, i + 1))


def main(argv):
    root = argv[1] if len(argv) > 1 else HERE
    stems = sorted(f[:-4] for f in os.listdir(root) if f.endswith(".hex"))
    if not stems:
        print("%s: no .hex images found" % root)
        return 1
    errs = []
    for stem in stems:
        full = os.path.join(root, stem)
        loaded = load_image(full + ".hex", errs)
        if loaded is None:
            continue
        words, parcels = loaded
        check_trace(full, parcels, words, errs)
    for e in errs:
        print(e)
    if errs:
        print("%d problem(s) across %d image(s)" % (len(errs), len(stems)))
        return 1
    print("ok: %d image(s); formats, state continuity and traceability all check"
          % len(stems))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
