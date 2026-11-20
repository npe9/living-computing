#!/usr/bin/env python3
"""Compare the Bluespec run of a 1e program with the reference run.

Both runs print one HRI line per retirement.  The reference
(`tools/p9run.py --hri`) never executes the kernel-entry stubs -- the
kernel's work happens between two of its steps -- so the Bluespec run's
records whose PC is in the kernel's page are the stub's and are dropped
here; everything else must agree, record by record, in every field
except `cyc`:

    pc insn sp(before>after) msp(before>after) we addr data mask trap

`cyc` is left out on purpose and reported separately: the stub's wait is
host time, and the model charges memory operands and prefetch fills
outside `cyc`.  The count of records whose `cyc` also agrees is printed
so that a change in it is visible.

The comparison stops at the reference run's last record (after `exits`
the machine is still executing; the reference is not).  A Bluespec run
shorter than the reference is a failure.

    python3 tools/p9trace_cmp.py ref.hri core.log [--kpage c00:e00]
"""

import argparse
import re
import sys

LINE = re.compile(
    r"^HRI pc=([0-9a-f]+) insn=([0-9a-f]+) sp=([0-9a-f]+)>([0-9a-f]+) "
    r"msp=([0-9a-f]+)>([0-9a-f]+) we=(\d) addr=([0-9a-f]+) "
    r"data=([0-9a-f]+) mask=([0-9a-f]+) trap=(\d) cyc=(\d+)")
FIELDS = ("pc", "insn", "sp_before", "sp_after", "msp_before", "msp_after",
          "we", "addr", "data", "mask", "trap")


def records(path):
    out = []
    with open(path, errors="replace") as f:
        for raw in f:
            m = LINE.match(raw)
            if m:
                g = m.groups()
                out.append((tuple(int(x, 16) for x in g[:11]), int(g[11]),
                            raw.rstrip("\n")))
    return out


def cyc_classes(ref, dut, klo, khi):
    """Records that agree in everything but cyc, grouped by the first
    parcel's opcode class and the (reference, core) pair of values."""
    user = [r for r in dut if not klo <= r[0][0] < khi]
    groups = {}
    for r, d in zip(ref, user):
        if d[0] != r[0] or d[1] == r[1]:
            continue
        p0 = r[0][1] >> 16
        if p0 & 0x8000 == 0:
            key = "1-parcel opcode 0x%02x" % ((p0 >> 10) & 0x1F)
        else:
            key = "%d-parcel opcode 0x%02x" % (
                3 if (p0 & 0xC000) == 0x8000 else 5, (p0 >> 8) & 0x3F)
            if (p0 >> 8) & 0x3F == 0:
                key += " subcode 0x%x" % (p0 & 0xF)
        groups.setdefault(key, {}).setdefault((r[1], d[1]), 0)
        groups[key][(r[1], d[1])] += 1
    lines = []
    for key in sorted(groups, key=lambda k: -sum(groups[k].values())):
        pairs = sorted(groups[key].items(), key=lambda kv: -kv[1])
        lines.append("  %7d  %-28s %s" % (
            sum(groups[key].values()), key,
            ", ".join("ref %d core %d x%d" % (a, b, n)
                      for (a, b), n in pairs[:6])))
    return "\n".join(lines)


def compare(ref, dut, klo, khi, context=4):
    """Return (ok, text).  `ref` and `dut` are `records()` lists."""
    user = [r for r in dut if not klo <= r[0][0] < khi]
    stub = len(dut) - len(user)
    lines = []
    same_cyc = 0
    for i, r in enumerate(ref):
        if i >= len(user):
            lines.append("FAIL: the Bluespec run has %d records outside the "
                         "kernel page; the reference has %d.  Next expected:"
                         % (len(user), len(ref)))
            lines.append("  ref  %s" % r[2])
            return False, "\n".join(lines)
        d = user[i]
        if d[0] != r[0]:
            bad = [FIELDS[k] for k in range(11) if d[0][k] != r[0][k]]
            lines.append("FAIL at record %d of %d: %s differ"
                         % (i + 1, len(ref), ", ".join(bad)))
            for j in range(max(0, i - context), i):
                lines.append("  both %s" % ref[j][2])
            lines.append("  ref  %s" % r[2])
            lines.append("  core %s" % d[2])
            return False, "\n".join(lines)
        if d[1] == r[1]:
            same_cyc += 1
    lines.append("MATCH: %d records agree in every field but cyc "
                 "(%d also agree in cyc); %d stub records dropped; "
                 "%d Bluespec records after the reference's last"
                 % (len(ref), same_cyc, stub, len(user) - len(ref)))
    return True, "\n".join(lines)


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("ref")
    ap.add_argument("dut")
    ap.add_argument("--kpage", default="c00:e00",
                    help="the kernel page, lo:hi in hex (default c00:e00)")
    ap.add_argument("--cyc", action="store_true",
                    help="also list the records that differ only in cyc, "
                         "by opcode and (reference, core) value")
    args = ap.parse_args(argv)
    klo, khi = (int(x, 16) for x in args.kpage.split(":"))
    ref, dut = records(args.ref), records(args.dut)
    ok, text = compare(ref, dut, klo, khi)
    print(text)
    if args.cyc:
        print(cyc_classes(ref, dut, klo, khi))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
