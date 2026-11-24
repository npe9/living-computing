#!/usr/bin/env python3
"""rtc_iic_inject.py -- prove rtc_iic_check.py discriminating: inject one
bug at a time into Rtc.bsv / Iic.bsv, run the check, print the sequences
that fail, and revert by applying the injection's own diff in reverse
(AGENTS.md: never `git checkout` a file to revert).  Refuses to start
unless both files are clean against git.

    python3 hobbit/fpga/dev/rtc_iic_inject.py [ID ...]     (~15 s each)

The observed failure sets are written in rtc_iic_check.py's header.
"""
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
FILES = ["Rtc.bsv", "Iic.bsv"]

INJ = [
    ("R1", "the divider does not restart on a load", "Rtc.bsv",
     "         div <= 1;            // the load cycle counts as the first",
     "         div <= 0;            // the load cycle counts as the first"),
    ("R2", "leap year from the units digit only", "Rtc.bsv",
     "   Bit#(4) s = (zeroExtend(y[4]) << 1) + y[3:0];",
     "   Bit#(4) s = y[3:0];"),
    ("R3", "a new snapshot on every R/W control write", "Rtc.bsv",
     "            if (v[7:6] != 0 && was[7:6] == 0) begin",
     "            if (v[7:6] != 0) begin"),
    ("R4", "weekday table: March 2 -> 3", "Rtc.bsv",
     "                   1: 0;  2: 3;  3: 2;",
     "                   1: 0;  2: 3;  3: 3;"),
    ("R5", "clock register reads ignore the held set", "Rtc.bsv",
     "            resp.enq(zeroExtend(field(isHeld ? held : now, reg_)));",
     "            resp.enq(zeroExtend(field(now, reg_)));"),
    ("R6", "April has 31 days", "Rtc.bsv",
     "      8'h04, 8'h06, 8'h09, 8'h11: return 8'h30;",
     "      8'h06, 8'h09, 8'h11: return 8'h30;"),
    ("R7", "NVRAM index from addr[11:1]", "Rtc.bsv",
     "      Bit#(11) idx = addr[12:2];",
     "      Bit#(11) idx = addr[11:1];"),
    ("R8", "a clock register write without W is accepted", "Rtc.bsv",
     "            if (!isHeld || control[7] == 0)",
     "            if (False)"),
    ("I1", "the repeated START's address taken as a data byte", "Iic.bsv",
     "                  if (slave[7:1] == devEeprom && ptrSet)",
     "                  if (False)"),
    ("I2", "LRB inverted", "Iic.bsv",
     "                  lrb   <= !known(s0);",
     "                  lrb   <= known(s0);"),
    ("I3", "BB reads busy, not free", "Iic.bsv",
     "                                 pack(!busy)}));",
     "                                 pack(busy)}));"),
    ("I4", "0xC0 does not complete the byte in progress", "Iic.bsv",
     "               else if ((d & ctlPIN) != 0 && reading)\n"
     "                  pin <= False;   // the byte in progress completes\n",
     ""),
    ("I5", "the LED latch's write count not kept", "Iic.bsv",
     "                        ledN <= ledN + 1;",
     "                        ledN <= ledN;"),
    ("I6", "an S0 read with ACK does not advance the pointer", "Iic.bsv",
     "               ptr <= ptr + 1;",
     "               ptr <= ptr;"),
    ("I7", "S0 readable with ESO off", "Iic.bsv",
     "         else if ((ctl & ctlESO) == 0) begin\n"
     "            resp.enq(0);",
     "         else if (False) begin\n"
     "            resp.enq(0);"),
]


def git(*a, **k):
    return subprocess.run(["git"] + list(a), cwd=HERE, capture_output=True,
                          text=True, **k)


def clean():
    return git("diff", "--quiet", "--", *FILES).returncode == 0


def main():
    only = sys.argv[1:]
    if not clean():
        raise SystemExit("Rtc.bsv / Iic.bsv have uncommitted changes")
    for ident, what, f, old, new in INJ:
        if only and ident not in only:
            continue
        path = os.path.join(HERE, f)
        text = open(path).read()
        assert text.count(old) == 1, ident
        open(path, "w").write(text.replace(old, new))
        diff = git("diff", "--", f).stdout
        try:
            r = subprocess.run([sys.executable, "rtc_iic_check.py"],
                               cwd=HERE, capture_output=True, text=True)
        finally:
            with tempfile.NamedTemporaryFile("w", suffix=".patch",
                                             delete=False) as p:
                p.write(diff)
            rv = git("apply", "-R", p.name)
            os.unlink(p.name)
            if rv.returncode or not clean():
                raise SystemExit("%s: reverse patch failed: %s"
                                 % (ident, rv.stderr))
        tail = [l for l in r.stdout.split("\n") if "sequences agree" in l]
        print("%s %s: %s" % (ident, what,
                              tail[-1] if tail else r.stderr[-400:]))
        for line in r.stdout.split("\n"):
            if line.endswith("FAIL"):
                print("    " + " ".join(line.split()[:-3]))
        sys.stdout.flush()
    print("Rtc.bsv and Iic.bsv clean:", clean())


if __name__ == "__main__":
    main()
