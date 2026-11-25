#!/usr/bin/env python3
"""sysram_filter.py -- give the SoC core's arrays a read port on the
system clock (fpga/README.md, "The core's arrays on the system clock").

    python3 fpga/sysram_filter.py IN.v OUT.v

IN.v is bsc's mkHobbitSocCpu.v.  Every `RegFile` instance in it (bsc's
array primitive: one write port, five *combinational* read ports) is
renamed `HobbitSysRegFile` (rtl/hobbit_sysregfile.v), which is the same
array with each read port registered on the free-running system clock,
and the module gains a `SYSCLK` input that every such instance gets.

Why this is exact: the core runs on a gated copy of the system clock and
never sees the system-clock edges between two of its own edges.  Its
registers hold there, so every array address is a function of held state
and of the adapter's inputs (rdData, the window), which the adapter also
holds once it has settled.  A read port registered on the system clock
therefore shows, a system clock after its address settles, exactly the
word a combinational read would; hobbit_soc_mem waits `SETTLE` system
clocks after the last change before it samples the probes or fires.
rtl/hobbit_sysregfile.v checks this at every core edge in simulation
(`HOBBIT_SIM`): a read port that disagrees with a combinational read of
its array stops the run.

Nothing else in the netlist changes, and the BSV is untouched: Bluesim
and every other build keep bsc's own RegFile.
"""
import re
import sys


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    src = open(sys.argv[1]).read()
    head = "module mkHobbitSocCpu(CLK,"
    if src.count(head) != 1:
        sys.exit("sysram_filter: no `%s` in %s" % (head, sys.argv[1]))
    src = src.replace(head, "module mkHobbitSocCpu(SYSCLK,\n\t\t      CLK,", 1)
    decl = "  input  CLK;\n"
    if src.count(decl) < 1:
        sys.exit("sysram_filter: no CLK declaration in %s" % sys.argv[1])
    src = src.replace(decl, "  input  SYSCLK;\n" + decl, 1)
    # `  RegFile #(...) name(.CLK(CLK),` -> HobbitSysRegFile with SYSCLK.
    pat = re.compile(r"^(  )RegFile( #\((?:[^()]|\([^()]*\))*\)\s+\S+\()\.CLK\(CLK\),",
                     re.M)
    src, n = pat.subn(r"\1HobbitSysRegFile\2.SYSCLK(SYSCLK), .CLK(CLK),", src)
    if re.search(r"^  RegFile\b", src, re.M):
        sys.exit("sysram_filter: a RegFile instance was not rewritten")
    open(sys.argv[2], "w").write(src)
    sys.stderr.write("sysram_filter: %d RegFile instance(s) on SYSCLK\n" % n)


if __name__ == "__main__":
    main()
