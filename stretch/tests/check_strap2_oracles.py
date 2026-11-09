#!/usr/bin/env python3
"""check_strap2_oracles.py -- how far strap/strap2 reproduces what is printed.

Runs on strap/strap2, through strap2_shim.py:
  - every verify_*.py that takes no argument and runs no model;
  - verify_mcp_page.py for every page run_tests.sh registers;
and compares the image of every deck with strap_asm's.

The counts are pinned so that the reach claimed in docs/strap2/README.md is the
reach measured.  The image comparison's only allowed differences are KNOWN below.

Injections, measured 2026-11-09, each reverted from a saved copy and compared
(the counts are FAIL lines, and a row may fail in more than one script):
  written tail ignored            7, among them p43, merge_dds_guard, syn_chain_reg,
                                  page 261 and the image comparison
  XW refill taken as 24 bits      121
  .L not counted in words         377
  a 19-bit integer scaled         35
"""
import glob
import os
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

SKIP = {"verify_mcp_page.py",           # takes a page number, run below
        "verify_problem_1_9.py"}        # takes a method and runs the model
PIN_VERIFY = 273
PIN_PAGES = 351
# p.33 makes only a CNOP a NOP.  strap_asm also puts a NOP in the half word it
# rounds over before a DR(N) or DRZ(N).  Those halves are never executed and no
# listing prints them, so no oracle can decide; strap2 follows the guide.
KNOWN = {"mcp_bootstrap_p131.strap", "mcp_bootstrap_p210.strap",
         "mcp_bootstrap_p268.strap", "mcp_bootstrap_p274.strap",
         "mcp_bootstrap_p358.strap", "mcp_bootstrap_p363.strap",
         "mcp_bootstrap_p371.strap"}


def run(args):
    r = subprocess.run([sys.executable, "strap2_shim.py"] + args, cwd=HERE,
                       capture_output=True, text=True, timeout=600)
    last = [ln for ln in (r.stdout + r.stderr).splitlines()
            if "FAIL" in ln or "Error" in ln][:1]
    return args, r.returncode == 0, (last[0][:150] if last else "")


def main():
    scripts = sorted(os.path.basename(p) for p in glob.glob(os.path.join(HERE, "verify_*.py")))
    # verify_merge_dds_guard.py writes a stripped dds into a real deck for a
    # moment, so it runs alone: in the pool it failed its neighbour
    # verify_syn_chain_reg.py one time in four.
    alone = ["verify_merge_dds_guard.py"]
    jobs = [[s] for s in scripts if s not in SKIP and s not in alone]
    suite = open(os.path.join(HERE, "run_tests.sh")).read()
    pages = sorted({int(n) for n in re.findall(r"verify_mcp_page\.py (\d+)", suite)})
    n_verify = len(jobs) + len(alone)
    jobs += [["verify_mcp_page.py", str(p)] for p in pages]
    fails = 0
    ok_verify = ok_pages = 0
    with ThreadPoolExecutor(10) as ex:
        results = list(ex.map(run, jobs))
    results += [run([s]) for s in alone]
    for args, ok, last in results:
        if ok:
            if args[0] == "verify_mcp_page.py":
                ok_pages += 1
            else:
                ok_verify += 1
        else:
            fails += 1
            print(f"FAIL {' '.join(args)}: {last}")
    print(f"listing oracles on strap2: {ok_verify} of {n_verify}; MCP pages: {ok_pages} of {len(pages)}")
    if ok_verify != PIN_VERIFY or ok_pages != PIN_PAGES:
        print(f"FAIL the pinned reach is {PIN_VERIFY} and {PIN_PAGES}")
        fails += 1
    r = subprocess.run([sys.executable, "strap2_compare.py"], cwd=HERE,
                       capture_output=True, text=True, timeout=900)
    same = 0
    for ln in r.stdout.splitlines():
        m = re.match(r"(\S+)\s+(\S+\.strap): (.*)", ln)
        if m and not (m.group(1) == "words" and m.group(2) in KNOWN):
            print(f"FAIL image: {ln[:170]}")
            fails += 1
    print(r.stdout.splitlines()[-1] if r.stdout else r.stderr[-300:])
    print("ALL CHECKS PASSED" if not fails else f"{fails} CHECK(S) FAILED")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
