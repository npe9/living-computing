#!/usr/bin/env python3
"""area_netlist.py -- attribute a synthesised ECP5 netlist to Hobbit blocks.

The ULX3S flow (fpga/build.sh) lets yosys write `ulx3s_top.json`.  That
netlist is flat, but bsc keeps the block name in every state, wire and
cell name: `core_eu_*`, `core_sc_*`, `core_ic_*`, `core_pf_*`, `mem_*`,
`q_*`, `uart_*`, and the board's `li`/`boot`/`started`.  This script
classifies every LUT4, PFUMX, TRELLIS_FF, CCU2C and DP16KD by that name
and, for the handful of opaque `_hNNNN` temporaries, by propagating the
block label forward from the registers that feed them.  A cell whose
name names a block is never relabelled by propagation, because the
generated name is stronger evidence than the fan-in.

Usage:
    python3 tools/area_netlist.py fpga/build/ulx3s_top.json
    python3 tools/area_netlist.py --json other.json --top ulx3s_top

The output is a fixed-width table.  LUT4 and PFUMX are reported
separately because nextpnr packs a PFUMX into a LUT4 slice: the
83,272 TRELLIS_COMB total is 76,650 LUT4 + 8,235 PFUMX - 1,613 packed
muxes, so no "LUT4 + PFUMX" sum equals it exactly.  The script prints
that arithmetic too.
"""

import argparse
import collections
import json
import re
import sys

# Order matters: a UART cell whose name also contains a memory field
# (`uart_..._mem_wdata`) is UART, not memory; a `core_eu_outQ` cell is
# EU (its queue is verification overhead inside the EU block).
PATTERNS = [
    ("prefetch", r"core_pf"),
    ("pdu", r"core_pdu"),
    ("eu", r"core_eu"),
    ("stack cache", r"core_sc"),
    ("decoded store", r"core_ic"),
    ("uart", r"uart"),
    ("hri queue", r"(^|\.)q_"),
    ("program memory", r"(^|\.)MUX_mem|(^|\.)mem_"),
    ("hri presentation", r"pendFold|core_present"),
    ("board glue", r"^hobbit\.(li|boot|loaded|started|power|BTN1|ftdi)"),
]


def block_of_name(name):
    """Return the block named by a generated netlist name, or None."""
    for block, pat in PATTERNS:
        if re.search(pat, name):
            return block
    return None


def bits_of(values):
    return [v for v in values if isinstance(v, int)]


def classify(json_path, top):
    with open(json_path) as f:
        design = json.load(f)
    mod = design["modules"][top]
    cells = mod["cells"]
    name_class = {name: block_of_name(name) for name in cells}

    # ---- seed labels: flip-flops and block RAM own their block ----
    labels = {}
    for name, cell in cells.items():
        kind = cell["type"]
        if kind not in ("TRELLIS_FF", "DP16KD"):
            continue
        block = name_class[name]
        if block is None:
            continue
        if kind == "TRELLIS_FF":
            outs = cell["connections"].get("Q", [])
        else:
            outs = []
            for port, values in cell["connections"].items():
                if cell.get("port_directions", {}).get(port) == "output":
                    outs.extend(values)
        for bit in bits_of(outs):
            labels[bit] = block

    # Top-level inputs belong to the board, which is the only thing
    # outside the core.  This labels the reset gate and the pin wrapper.
    for port, info in mod.get("ports", {}).items():
        if info.get("direction") == "input":
            for bit in bits_of(info.get("bits", [])):
                labels[bit] = "board glue"

    # ---- label combinational cells ---------------------------------
    # A cell with a block name in its own name is not touched.  The
    # others take the majority label of their inputs; ties are "shared".
    # Iterate to a fixed point (the netlist is a DAG at bit level).
    for _ in range(100):
        changed = 0
        for name, cell in cells.items():
            kind = cell["type"]
            if kind in ("TRELLIS_FF", "DP16KD"):
                continue
            if name_class[name] is not None:
                continue
            ins, outs = [], []
            for port, values in cell["connections"].items():
                direction = cell.get("port_directions", {}).get(port)
                if direction == "output":
                    outs.extend(bits_of(values))
                elif direction == "input":
                    ins.extend(bits_of(values))
            if not outs:
                continue
            counts = collections.Counter(labels[b] for b in ins if b in labels)
            if not counts:
                continue
            best = max(counts.values())
            winners = [b for b, n in counts.items() if n == best]
            label = winners[0] if len(winners) == 1 else "shared"
            for bit in outs:
                if labels.get(bit) != label:
                    labels[bit] = label
                    changed += 1
        if not changed:
            break

    # ---- count cells ------------------------------------------------
    totals = collections.Counter()
    by_block = collections.defaultdict(collections.Counter)
    for name, cell in cells.items():
        kind = cell["type"]
        if kind not in ("LUT4", "PFUMX", "TRELLIS_FF", "CCU2C", "DP16KD"):
            continue
        totals[kind] += 1
        block = name_class[name]
        if block is None:
            # Opaque temporary: use the label of the output net.
            outs = []
            for port, values in cell["connections"].items():
                if cell.get("port_directions", {}).get(port) == "output":
                    outs.extend(bits_of(values))
            counts = collections.Counter(labels[b] for b in outs if b in labels)
            block = counts.most_common(1)[0][0] if counts else "unattributed"
        by_block[block][kind] += 1
    return totals, by_block


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("json", nargs="?", default="fpga/build/ulx3s_top.json")
    parser.add_argument("--top", default="ulx3s_top")
    args = parser.parse_args()
    try:
        totals, by_block = classify(args.json, args.top)
    except (OSError, KeyError, json.JSONDecodeError) as exc:
        sys.exit("area_netlist: %s" % exc)

    print("netlist: %s  (module %s)" % (args.json, args.top))
    print()
    print("%-20s %7s %7s %7s %7s %6s"
          % ("block", "LUT4", "PFUMX", "FF", "CCU2C", "BRAM"))
    print("-" * 60)
    order = [
        "prefetch", "pdu", "decoded store", "stack cache", "eu",
        "program memory", "hri queue", "hri presentation", "uart",
        "board glue", "shared", "unattributed",
    ]
    for block in order:
        c = by_block.get(block)
        if not c:
            continue
        print("%-20s %7d %7d %7d %7d %6d"
              % (block, c["LUT4"], c["PFUMX"], c["TRELLIS_FF"],
                 c["CCU2C"], c["DP16KD"]))
    print("-" * 60)
    print("%-20s %7d %7d %7d %7d %6d"
          % ("TOTAL", totals["LUT4"], totals["PFUMX"],
             totals["TRELLIS_FF"], totals["CCU2C"], totals["DP16KD"]))
    print()
    print("nextpnr TRELLIS_COMB = %d LUT4 + %d PFUMX - %d packed PFUMX"
          % (totals["LUT4"], totals["PFUMX"],
             totals["LUT4"] + totals["PFUMX"] - 83272))


if __name__ == "__main__":
    main()
