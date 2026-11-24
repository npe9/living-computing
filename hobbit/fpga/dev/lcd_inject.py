#!/usr/bin/env python3
"""The bug injections of lcd_test.py's header: put one bug at a time into
the RTL (an exact one-place string replacement), run lcd_test.py, print its
FAIL lines, reverse the exact patch and check the file's sha256 is back.

    python3 hobbit/fpga/dev/lcd_inject.py [--full] [NAME ...]

--full includes the recorded 8½ run (lcd_test.py without --quick).  Run
it on a clean tree and check `git diff` is empty afterwards.
"""
import hashlib, os, subprocess, sys
D =os.path.dirname(os.path.abspath(__file__))
INJ = [
 ("quad-shift-4", "LcdLcdisp.bsv", "quad <= truncate({quad, wdata[5:0]});", "quad <= truncate({quad, wdata[3:0]});"),
 ("ctl-no-col-reset", "LcdLcdisp.bsv", "         col  <= 0;\n", "         col  <= col;\n"),
 ("col-wraps-1024", "LcdLcdisp.bsv", "            col <= col + 1;\n         end\n         else\n            ovr <= ovr + 1;", "         end\n         else\n            ovr <= ovr + 1;\n         col <= col + 1;"),
 ("honour-be0", "LcdLcdisp.bsv", "else if (write && addr == 12'h004) begin", "else if (write && addr == 12'h004 && be[0] == 1) begin"),
 ("data-any-offset", "LcdLcdisp.bsv", "else if (write && addr == 12'h004) begin", "else if (write && addr[2] == 1) begin"),
 ("row-order-reversed", "hdmi_scan.v", "wire [1:0] level = rd_data[2 * r2 +: 2];", "wire [1:0] level = rd_data[2 * (2'd3 - r2) +: 2];"),
 ("grey-inverted", "hdmi_scan.v", "dbg_grey <= de2 ? { level, level, level, level } : 8'd0;", "dbg_grey <= de2 ? ~{ level, level, level, level } : 8'd0;"),
 ("rotation-direction", "hdmi_scan.v", "wire [9:0]  px   = 10'd767 - vc;", "wire [9:0]  px   = vc;"),
 ("pixel-offset-1", "hdmi_scan.v", "wire [1:0] level = rd_data[2 * r2 +: 2];", "wire [1:0] level = rd_data[2 * r1 +: 2];"),
 ("hsync-active-high", "hdmi_scan.v", "wire hs0 = !((hc >= H_ACT + H_FP)", "wire hs0 =  ((hc >= H_ACT + H_FP)"),
 ("tmds-no-dc-balance", "hdmi_tmds.v", "end else if ((cnt > 0 && diff > 0) || (cnt < 0 && diff < 0)) begin", "end else if (1'b0) begin"),
 ("tmds-xnor-choice", "hdmi_tmds.v", "wire       xn  = (n1d > 4) || (n1d == 4 && !d[0]);", "wire       xn  = (n1d > 4) || (n1d == 4 &&  d[0]);"),
]

def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()

only = sys.argv[1:]
full = "--full" in only
only = [o for o in only if o != "--full"]
for name, f, old, new in INJ:
    if only and name not in only:
        continue
    p = os.path.join(D, f)
    s = open(p).read()
    assert s.count(old) == 1, (name, s.count(old))
    before = sha(p)
    open(p, "w").write(s.replace(old, new))
    try:
        args = ["python3", os.path.join(D, "lcd_test.py")] + ([] if full else ["--quick"])
        r = subprocess.run(args, capture_output=True, text=True)
        fails = [l for l in r.stdout.splitlines() if l.startswith("FAIL") or "lcd_tb: FAIL" in l]
        err = r.stderr.strip().splitlines()[-3:] if r.returncode not in (0, 1) else []
    finally:
        t = open(p).read()
        assert t.count(new) == 1
        open(p, "w").write(t.replace(new, old))
    assert sha(p) == before, name
    print("### %s (%s)%s" % (name, f, " [full]" if full else ""))
    for l in fails:
        print("   ", l)
    for l in err:
        print("    ERR", l)
    sys.stdout.flush()
