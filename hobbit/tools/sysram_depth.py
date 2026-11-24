#!/usr/bin/env python3
"""sysram_depth.py -- the settle bound for the SoC core's system-clock arrays
(fpga/sysram_filter.py, rtl/hobbit_sysregfile.v, rtl/hobbit_soc_mem.v
SETTLE), from the flat synth_ecp5 netlist fpga/area_cpu.sh writes.

A HobbitSysRegFile read port is a block RAM (DP16KD) whose output register
is clocked by the system clock from the port's current address.  When the
address changes, the port shows the new word one system clock later; a
port whose address is computed from another port's output shows its word
one clock after that one; and so on.  So after the last change to the
core's inputs (a core edge, rdData, the window) the probes are final
after D system clocks, D being the longest chain of block RAM reads on
any combinational path into the probe port.

This script finds every DP16KD, walks each one's address inputs backwards
through the combinational cells (LUT4, CCU2C, PFUMX, L6MUX21, the
combinational-read DPR16X4 and MULT18X18D), and records which DP16KD
outputs and which module inputs (rdData_d, window_w, ...) reach it.  It
then walks the probe port the same way and prints:

  * the chain depth D into `probes` (DP16KD hops), and the deepest chain;
  * which module inputs reach any DP16KD address (a block RAM read that
    depends on rdData or the window would add a settle after each fill);
  * which module inputs reach the probes directly.

    python3 tools/sysram_depth.py fpga/build/area-NAME/cpu.json
"""
import json
import sys
from collections import defaultdict

COMB = {"LUT4", "CCU2C", "PFUMX", "L6MUX21", "TRELLIS_DPR16X4", "MULT18X18D"}
# The combinational inputs of a cell (a DPR16X4's write port is clocked).
COMB_IN = {"TRELLIS_DPR16X4": lambda p: p == "RAD"}


def main():
    path = sys.argv[1]
    top = sys.argv[2] if len(sys.argv) > 2 else "mkHobbitSocCpu"
    mod = json.load(open(path))["modules"][top]
    driver = {}                    # bit -> ("cell", name) | ("port", name)
    for pn, p in mod["ports"].items():
        if p["direction"] == "input":
            for b in p["bits"]:
                driver[b] = ("port", pn)
    cells = mod["cells"]
    for cn, c in cells.items():
        dirs = c.get("port_directions", {})
        for p, bits in c["connections"].items():
            if dirs.get(p) == "output":
                for b in bits:
                    if isinstance(b, int):
                        driver[b] = ("cell", cn)

    def cell_inputs(cn, ports=None):
        c = cells[cn]
        dirs = c.get("port_directions", {})
        for p, bits in c["connections"].items():
            if dirs.get(p) == "input" and (ports is None or ports(p)):
                for b in bits:
                    if isinstance(b, int):
                        yield b

    memo = {}

    def sources(bit):
        """The DP16KDs, TRELLIS_FFs and input ports behind one net."""
        if bit in memo:
            return memo[bit]
        memo[bit] = (frozenset(), frozenset())  # cycle guard
        rams, ports = set(), set()
        stack, seen = [bit], set()
        while stack:
            b = stack.pop()
            if b in seen:
                continue
            seen.add(b)
            d = driver.get(b)
            if d is None:
                continue
            kind, name = d
            if kind == "port":
                ports.add(name)
                continue
            t = cells[name]["type"]
            if t == "DP16KD":
                rams.add(name)
            elif t in COMB:
                stack.extend(cell_inputs(name, COMB_IN.get(t)))
        r = (frozenset(rams), frozenset(ports))
        memo[bit] = r
        return r

    # A block RAM's read side is the port clocked by SYSCLK (its write
    # side, on the core's CLK, lands at the core edge and is not a path).
    sysclk = set(mod["ports"]["SYSCLK"]["bits"])

    def read_side(r):
        conn = cells[r]["connections"]
        for side in "AB":
            if set(conn["CLK" + side]) & sysclk:
                return side
        return None

    # A block RAM with no port on SYSCLK reads on the core's own clock
    # (yosys's mapping of a bsc FIFO's array, e.g. the trace queue): its
    # output is state, like a flip-flop's, and starts no chain.
    rams = [cn for cn, c in cells.items()
            if c["type"] == "DP16KD" and read_side(cn) is not None]
    ramset = set(rams)
    feeds = {}                     # ram -> (rams behind its address, ports)
    for r in rams:
        rs, ps = set(), set()
        side = read_side(r)
        for b in cell_inputs(r, lambda p: p.startswith("AD" + side)):
            a, p = sources(b)
            rs |= a & ramset
            ps |= p
        rs.discard(r)
        feeds[r] = (rs, ps)

    depth = {}

    def dep(r, onpath=()):
        if r in depth:
            return depth[r]
        if r in onpath:
            raise SystemExit("a block RAM read feeds its own address: %s" % r)
        d = 1 + max([dep(x, onpath + (r,)) for x in feeds[r][0]] or [0])
        depth[r] = d
        return d

    for r in rams:
        dep(r)

    prs, pps = set(), set()
    for b in mod["ports"]["probes"]["bits"]:
        if isinstance(b, int):
            a, p = sources(b)
            prs |= a & ramset
            pps |= p
    D = max([depth[r] for r in prs] or [0])
    print("block RAMs: %d; reaching the probes: %d" % (len(rams), len(prs)))
    print("chain depth into probes: %d" % D)
    if prs:
        deepest = max(prs, key=lambda r: depth[r])
        chain = [deepest]
        while feeds[chain[-1]][0]:
            chain.append(max(feeds[chain[-1]][0], key=lambda r: depth[r]))
        print("deepest chain (probe side first):")
        for r in chain:
            print("   ", r)
    inp = set()
    for r in rams:
        inp |= feeds[r][1]
    print("module inputs reaching a block RAM address:",
          ", ".join(sorted(inp)) or "none")
    print("module inputs reaching the probes:", ", ".join(sorted(pps)) or "none")

    # The chain after a change of one module input (rdData when the
    # adapter's read lands, the window when a fill does): the RAM reads
    # that depend on it, however indirectly, in sequence.
    for port in sorted(inp):
        dd = {}

        def dfrom(r):
            if r not in dd:
                below = [dfrom(x) for x in feeds[r][0]]
                hit = port in feeds[r][1] or any(below)
                dd[r] = (1 + max(below or [0])) if hit else 0
            return dd[r]

        print("chain depth after a change of %s: %d into probes, %d into any"
              " port" % (port, max([dfrom(r) for r in prs] or [0]),
                         max([dfrom(r) for r in rams] or [0])))


if __name__ == "__main__":
    main()
