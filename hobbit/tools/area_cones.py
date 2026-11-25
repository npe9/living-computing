#!/usr/bin/env python3
"""area_cones.py -- attribute a flat synth_ecp5 netlist of mkHobbitSocCpu
to the state elements its logic feeds (fpga/area_cpu.sh writes the JSON).

bsc flattens the core into one Verilog module, so yosys has no hierarchy to
report.  What survives is the *name of every state element*: a flip-flop's
Q net is `core_c_mmu_tlbText[123]`, a LUT RAM's output net names its
RegFile instance.  This script labels every sink (flip-flop D/CE/LSR,
LUT-RAM write port, block RAM input, module output port) by its element
name, then walks the combinational netlist backwards from the sinks: each
combinational cell gets the set of sink groups its output can reach.

A cell whose cone reaches exactly one group is that group's own logic.  A
cell reaching several groups is shared logic, and is reported under the
smallest common prefix of those groups (so a TLB match that feeds three
PDU registers lands on "core_c_pdu").  The same walk is done forwards
from the *sources* (flip-flop Q, LUT-RAM and block RAM outputs, inputs)
for the --by-source table, which is where a large read mux shows up.

Cost unit: LUT-equivalents = LUT4 + 2 x CCU2C + 6 x TRELLIS_DPR16X4, the
formula that reproduces nextpnr's "Total LUT4s" (fpga/README.md "Area").

    python3 tools/area_cones.py fpga/build/area-base/cpu.json [--depth N]
                                [--by-source] [--top mkHobbitSocCpu]

--depth N cuts each group name to N underscore-separated components
after the `core_c_` prefix (default 2: `mmu_tlbText`).
"""

import argparse
import collections
import json
import re
import sys

COST = {"LUT4": 1, "CCU2C": 2, "TRELLIS_DPR16X4": 6, "PFUMX": 0,
        "L6MUX21": 0}
COMBOS = False
SEQ = {"TRELLIS_FF", "DP16KD", "TRELLIS_DPR16X4", "MULT18X18D"}


def group_of(name, depth):
    name = name.lstrip("\\")
    name = re.sub(r"\[\d+\]$", "", name)
    name = re.sub(r"\$(D_IN|EN|D_OUT|Q_OUT|DOB|DOA).*$", "", name)
    m = re.match(r"(core_c_)?([A-Za-z0-9]+(?:_[A-Za-z0-9]+)*)", name)
    if not m:
        return name
    parts = m.group(2).split("_")
    pre = "core." if m.group(1) else ""
    return pre + "_".join(parts[:depth])


def common_prefix(groups):
    split = [g.split("_") for g in groups]
    out = []
    for comps in zip(*split):
        if all(c == comps[0] for c in comps):
            out.append(comps[0])
        else:
            break
    return "_".join(out) if out else "(several)"


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("json")
    ap.add_argument("--top", default="mkHobbitSocCpu")
    ap.add_argument("--depth", type=int, default=2)
    ap.add_argument("--by-source", action="store_true")
    ap.add_argument("--rows", type=int, default=45)
    ap.add_argument("--combos", action="store_true",
                    help="key shared logic by its exact sink set (<= 4 groups)")
    a = ap.parse_args()
    global COMBOS
    COMBOS = a.combos

    d = json.load(open(a.json))
    mod = d["modules"][a.top]
    cells = mod["cells"]
    # Best name for each net bit: prefer a non-$ name.
    bitname = {}
    for nn, info in mod["netnames"].items():
        if nn.startswith("$"):
            continue
        for i, b in enumerate(info["bits"]):
            if isinstance(b, int):
                old = bitname.get(b)
                cand = nn
                if old is None or (info.get("hide_name", 0) == 0 and len(cand) < len(old)):
                    bitname[b] = cand

    drivers = {}
    sinks = collections.defaultdict(list)
    for cn, c in cells.items():
        for p, bits in c["connections"].items():
            dirn = c.get("port_directions", {}).get(p)
            for b in bits:
                if not isinstance(b, int):
                    continue
                if dirn == "output":
                    drivers[b] = cn
                else:
                    sinks[b].append(cn)

    def cell_outname(cn, c):
        for p, bits in c["connections"].items():
            if c.get("port_directions", {}).get(p) == "output":
                for b in bits:
                    if isinstance(b, int) and b in bitname:
                        return bitname[b]
        # an input name (a RAM's write data) as a fallback
        for p, bits in c["connections"].items():
            for b in bits:
                if isinstance(b, int) and b in bitname:
                    return bitname[b]
        return cn

    # Sink groups: every sequential cell, plus output ports.
    gidx = {}
    def gid(g):
        if g not in gidx:
            gidx[g] = len(gidx)
        return gidx[g]

    seqgroup = {}
    for cn, c in cells.items():
        if c["type"] in SEQ:
            seqgroup[cn] = gid(group_of(cell_outname(cn, c), a.depth))
    portbits = {}
    for pn, info in mod["ports"].items():
        g = gid("port." + pn)
        for b in info["bits"]:
            if isinstance(b, int):
                portbits.setdefault(b, []).append((info["direction"], g))

    comb = [cn for cn, c in cells.items() if c["type"] not in SEQ]
    # mask[cn] = bitmask of sink groups reachable from cn's outputs.
    mask = {}

    def outbits(c):
        return [b for p, bits in c["connections"].items()
                if c.get("port_directions", {}).get(p) == "output"
                for b in bits if isinstance(b, int)]

    sys.setrecursionlimit(1000000)
    # Iterative DFS over the combinational DAG.
    for root in comb:
        if root in mask:
            continue
        stack = [(root, False)]
        while stack:
            cn, done = stack.pop()
            if cn in mask and not done:
                continue
            c = cells[cn]
            succ = []
            m = 0
            for b in outbits(c):
                for (dirn, g) in portbits.get(b, []):
                    if dirn == "output":
                        m |= 1 << g
                for s in sinks.get(b, []):
                    if s in seqgroup:
                        m |= 1 << seqgroup[s]
                    else:
                        succ.append(s)
            if not done:
                pending = [s for s in succ if s not in mask]
                if pending:
                    mask[cn] = None  # in progress marker
                    stack.append((cn, True))
                    for s in pending:
                        stack.append((s, False))
                    continue
            for s in succ:
                ms = mask.get(s)
                if ms:
                    m |= ms
            mask[cn] = m

    names = {v: k for k, v in gidx.items()}

    def attribute(maskmap):
        own = collections.Counter()
        kinds = collections.defaultdict(collections.Counter)
        for cn in comb:
            c = cells[cn]
            cost = COST.get(c["type"], 0)
            m = maskmap.get(cn) or 0
            gs = [names[i] for i in range(len(names)) if (m >> i) & 1]
            if not gs:
                key = "(dead)"
            elif len(gs) == 1:
                key = gs[0]
            elif COMBOS:
                key = "{" + ",".join(sorted(gs))[:200] + "}" if len(gs) <= 4 else "shared:%d groups:%s" % (len(gs), common_prefix(gs))
            else:
                key = "shared:" + common_prefix(gs)
            own[key] += cost
            kinds[key][c["type"]] += 1
        return own, kinds

    own, kinds = attribute(mask)
    # Sequential cells by their own group.
    seqcost = collections.Counter()
    seqk = collections.defaultdict(collections.Counter)
    for cn, g in seqgroup.items():
        t = cells[cn]["type"]
        seqcost[names[g]] += COST.get(t, 0)
        seqk[names[g]][t] += 1

    keys = set(own) | set(seqcost)
    tot = sum(own.values()) + sum(seqcost.values())
    print("netlist %s: %d LUT-equivalents (LUT4 + 2 CCU2C + 6 DPR16X4)" % (a.json, tot))
    print("%-44s %8s %7s %6s %5s %6s %5s" % ("sink group (cone)", "LUTeq", "LUT4", "CCU2C", "DPR", "FF", "BRAM"))
    rows = sorted(keys, key=lambda k: -(own[k] + seqcost[k]))
    for k in rows[:a.rows]:
        kk = kinds[k]; sk = seqk[k]
        print("%-44s %8d %7d %6d %5d %6d %5d" % (k[:44], own[k] + seqcost[k], kk["LUT4"],
              kk["CCU2C"], sk["TRELLIS_DPR16X4"], sk["TRELLIS_FF"], sk["DP16KD"]))
    rest = sum(own[k] + seqcost[k] for k in rows[a.rows:])
    print("%-44s %8d" % ("(%d more groups)" % max(0, len(rows) - a.rows), rest))

    if a.by_source:
        # Forward from sources: which state element's fan-out cone.
        srcg = {}
        for cn, g in seqgroup.items():
            srcg[cn] = g
        smask = {}
        order = []
        # topological order of comb cells by Kahn on comb->comb edges
        indeg = collections.Counter()
        succs = collections.defaultdict(list)
        for cn in comb:
            for b in outbits(cells[cn]):
                for s in sinks.get(b, []):
                    if s not in seqgroup:
                        succs[cn].append(s)
                        indeg[s] += 1
        q = collections.deque(cn for cn in comb if indeg[cn] == 0)
        while q:
            cn = q.popleft(); order.append(cn)
            for s in succs[cn]:
                indeg[s] -= 1
                if indeg[s] == 0:
                    q.append(s)
        for cn in order:
            c = cells[cn]
            m = 0
            for p, bits in c["connections"].items():
                if c.get("port_directions", {}).get(p) == "output":
                    continue
                for b in bits:
                    if not isinstance(b, int):
                        continue
                    dcell = drivers.get(b)
                    if dcell is None:
                        for (dirn, g) in portbits.get(b, []):
                            if dirn == "input":
                                m |= 1 << g
                    elif dcell in seqgroup:
                        m |= 1 << seqgroup[dcell]
                    else:
                        m |= smask.get(dcell, 0)
            smask[cn] = m
        sown, _ = attribute(smask)
        print()
        print("%-44s %8s" % ("source group (fan-out cone)", "LUTeq"))
        for k, v in sown.most_common(a.rows):
            print("%-44s %8d" % (k[:44], v))


if __name__ == "__main__":
    main()
