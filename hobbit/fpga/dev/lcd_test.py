#!/usr/bin/env python3
"""Verilator test of the Lcdisp device (LcdLcdisp.bsv) and its HDMI scan-out
(hdmi_scan.v + hdmi_tmds.v tmds_enc) against p9term.LcdPanel, the Python
model p9boot runs the kernel with.  ulx3s_plan.md step 4.

    python3 hobbit/fpga/dev/lcd_test.py [--writes LCD_WRITES.BIN] [--quick]

Three runs of lcd_tb (lcd_sim_top.v), each compared with the model:

  synthetic   directed and random requests the 8½ recording does not
              exercise: cells never written (must stay level 0), ctl data
              with junk above bit 5 and more than two ctl writes in a row,
              data junk above bit 7, every byte-enable value, offsets other
              than 0 and 4, reads (answered, no effect), 1100 data writes
              after one ctl (columns 768.. are overruns; a counter that
              wrapped at 1024 would rewrite columns 0..75), and 20,000
              random requests.  The panel is read back through the RAM's
              pixel-clock port after 3 points and at the end, and compared
              whole with LcdPanel's; the overrun count and one response
              per request are checked too.
  recorded    the LCD writes s9term made in the 8½ session
              (lcd_capture.py; docs/p9boot.md "8½ as `tor`"), compared
              whole at a quarter, half, three quarters and the end; then
              one scanned-out frame, decoded from the TMDS words, is turned
              back to portrait (by the mapping of hdmi_scan.v's header,
              written here independently) and compared with LcdPanel.grey()
              and with tests/net/8half_ls.png, the live run's screenshot.
              The frame is written to build/lcd/test/frame_8half.png
              (1024 x 768, as a monitor shows it) and frame_8half_
              portrait.png.
  pattern     the test bitstream's own writer (lcd_pattern.v) drives the
              port; the panel and a scanned frame are compared with
              PATTERN below fed to LcdPanel.

lcd_tb also checks the raster of every scanned frame (totals, sync widths
and polarities, porches, red = green = blue).  Exit status 0 only if every
comparison holds.

Discrimination (bug injected in the RTL, the test run, the patch reversed;
OBSERVED failures, 2026-11-24, recorded in hdmi_lcd.md "Bug injections"):
see that section; each injection is listed with the exact lines that
failed.

--writes defaults to build/lcd/lcd_writes.bin (lcd_capture.py makes it,
~11 min, or fetch the committed lcd_writes_8half.bin.gz, which this script
uses when the build copy is missing).  --quick skips the recorded run.
"""

import gzip
import hashlib
import os
import random
import shutil
import struct
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
HOBBIT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(HOBBIT, "tools"))
sys.path.insert(0, os.path.join(HOBBIT, "tests"))

import p9term  # noqa: E402

W, H = p9term.LCD_W, p9term.LCD_H
OUT = os.path.join(HOBBIT, "fpga", "build", "lcd", "test")
SIM = os.path.join(HOBBIT, "fpga", "build", "lcd", "sim")
COMMITTED = os.path.join(HERE, "lcd_writes_8half.bin.gz")
FAILS = []


def check(cond, what):
    print(("ok    " if cond else "FAIL  ") + what)
    if not cond:
        FAILS.append(what)


# ---- build --------------------------------------------------------------

def build():
    bsc = os.environ.get("BSC_BIN") or sorted(
        __import__("glob").glob("/opt/homebrew/Cellar/bsc/*/bin/bsc"))[-1]
    bdir = os.path.realpath(os.path.join(os.path.dirname(bsc), "..",
                                         "libexec", "lib"))
    env = dict(os.environ, BLUESPECDIR=bdir)
    vdir = os.path.join(SIM, "bsc")
    os.makedirs(vdir, exist_ok=True)
    subprocess.run([bsc, "-verilog", "-g", "mkLcdisp", "-u", "-vdir", vdir,
                    "-bdir", vdir, "-info-dir", vdir, "-p",
                    HERE + ":" + bdir + "/Libraries",
                    os.path.join(HERE, "LcdLcdisp.bsv")],
                   check=True, env=env, stdout=subprocess.DEVNULL)
    obj = os.path.join(SIM, "obj")
    subprocess.run(["verilator", "--cc", "--exe", "--build", "-O2",
                    "-Wno-fatal", "-Wno-lint", "-Wno-style",
                    "-DBSV_NO_INITIAL_BLOCKS", "--top-module", "lcd_sim_top",
                    "--Mdir", obj, "-o", "lcd_tb",
                    os.path.join(HERE, "lcd_sim_top.v"),
                    os.path.join(vdir, "mkLcdisp.v"),
                    os.path.join(bdir, "Verilog", "BRAM2.v"),
                    os.path.join(bdir, "Verilog", "FIFO2.v"),
                    os.path.join(HERE, "hdmi_scan.v"),
                    os.path.join(HERE, "hdmi_tmds.v"),
                    os.path.join(HERE, "lcd_pattern.v"),
                    os.path.join(HERE, "lcd_tb.cpp")],
                   check=True, stdout=subprocess.DEVNULL)
    return os.path.join(obj, "lcd_tb")


# ---- requests, the model, the RTL's buffer ------------------------------

def rec(addr, data, be=0xF, write=True):
    return (addr & 0xFFF, data & 0xFFFFFFFF, be & 0xF, write)


def pack(reqs):
    return b"".join(struct.pack("<HBBI", a | (0x8000 if w else 0), be, 0, d)
                    for a, d, be, w in reqs)


def model(reqs, points):
    """LcdPanel fed the requests (reads skipped: the model refuses them);
    {point: level bytes} after each request count in points, and 'end'."""
    lcd = p9term.LcdPanel()
    snaps = {}
    for i, (a, d, be, w) in enumerate(reqs, 1):
        if w:
            lcd.write(a, d, be)
        if i in points:
            snaps[i] = bytes(lcd.level)
    snaps["end"] = bytes(lcd.level)
    return lcd, snaps


def levels(buf):
    """The panel, one level a cell row major, from the RAM's bytes (cell
    (x, y) is bits 2(y&3)+1..2(y&3) of byte (y>>2)*768 + x)."""
    planes = [buf.translate(bytes((b >> (2 * r)) & 3 for b in range(256)))
              for r in range(4)]
    out = bytearray()
    for q in range(H // 4):
        for r in range(4):
            out += planes[r][q * W:(q + 1) * W]
    return bytes(out)


def unrotate(frame):
    """hdmi_scan.v's mapping, written again here: display (X, Y) shows
    panel (x, y) = (767 - Y, X), so panel (x, y) is display (y, 767 - x)."""
    out = bytearray(W * H)
    for y in range(H):
        col = frame[y::1024]           # display column X = y, rows Y = 0..767
        for x in range(W):
            out[y * W + x] = col[767 - x]
    return bytes(out)


def diff(a, b):
    n = sum(1 for i in range(len(a)) if a[i] != b[i])
    first = next((i for i in range(len(a)) if a[i] != b[i]), None)
    return n, (None if first is None else (first % W, first // W))


def run(tb, name, reqs=None, pattern=False, points=(), frames=0):
    d = os.path.join(OUT, name)
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(d)
    args = [tb]
    if reqs is not None:
        path = os.path.join(d, "reqs.bin")
        with open(path, "wb") as f:
            f.write(pack(reqs))
        args += ["--writes", path]
    if pattern:
        args.append("--pattern")
    if points:
        args += ["--dump-at", ",".join(str(p) for p in sorted(points))]
    if frames:
        args += ["--frames", str(frames)]
    args.append(d)
    p = subprocess.run(args, capture_output=True, text=True)
    sys.stdout.write("".join("      lcd_tb: " + l + "\n"
                             for l in p.stdout.splitlines()[-6:]))
    check(p.returncode == 0, "%s: lcd_tb's own checks (raster, responses)"
          % name)
    stats = p.stdout.split("requests ")[1].split()
    return d, int(stats[0]), int(stats[4])


def compare_bufs(name, d, snaps):
    for k, want in sorted(snaps.items(), key=lambda kv: str(kv[0])):
        with open(os.path.join(d, "buf_%s.bin" % k), "rb") as f:
            got = levels(f.read())
        n, at = diff(got, want)
        check(n == 0, "%s: panel after request %s equals LcdPanel's "
              "(%d of %d cells differ%s)" % (name, k, n, W * H,
                                             ", first at x,y=%s" % (at,)
                                             if n else ""))


def compare_frame(name, d, want_grey, png_name=None):
    with open(os.path.join(d, "frame.bin"), "rb") as f:
        frame = f.read()
    check(len(frame) == 1024 * 768, "%s: a whole 1024x768 frame" % name)
    por = unrotate(frame)
    n, at = diff(por, want_grey)
    check(n == 0, "%s: scanned frame, turned back to portrait, equals "
          "LcdPanel.grey() (%d differ%s)" % (name, n, ", first at x,y=%s"
                                             % (at,) if n else ""))
    if png_name:
        p9term.write_image(os.path.join(OUT, png_name + ".png"), 1024, 768,
                           frame)
        p9term.write_image(os.path.join(OUT, png_name + "_portrait.png"),
                           W, H, por)
    return por


# ---- the three runs -----------------------------------------------------

def synthetic():
    rnd = random.Random(20261124)
    R = []
    ctl = lambda v: R.append(rec(0, v))
    data = lambda v, be=0xF: R.append(rec(4, v, be))
    # rows 40..43 (quad 10), from junk-laden ctl words, three in a row
    ctl(0xFFFFFF3F)
    ctl(0xABCDEF00)
    ctl(0x1234560A)                     # quad 0x3F, 0xC0, then 0x0A
    for x in range(100):
        data(0x5A00 | (x * 37 & 0xFF), be=x & 0xF)   # junk above bit 7, all masks
    # other offsets, reads: no effect
    for a in (0x8, 0xC, 0x1, 0x2, 0x3, 0x5, 0x6, 0x7, 0xFFC, 0x800):
        R.append(rec(a, 0xFF))
    R.append(rec(0, 0, write=False))
    R.append(rec(4, 0, write=False))
    data(0x00)                          # column 100 continues after them
    # quad 200: 768 columns of 0xE4, then 332 more of 0x1B (overruns: a
    # 10-bit column wrapping at 1024 would put 0x1B in columns 0..75)
    ctl(200 >> 6)
    ctl(200 & 0x3F)
    for x in range(1100):
        data(0xE4 if x < 768 else 0x1B)
    # ctl resets the column: quad 201 written from 0 again after 10
    ctl(3)
    ctl(201 & 0x3F)
    for x in range(10):
        data(0x93)
    ctl(3)
    ctl(201 & 0x3F)
    for x in range(5):
        data(0x6C)
    p1 = len(R)
    for _ in range(20000):
        k = rnd.random()
        if k < 0.03:
            R.append(rec(0, rnd.getrandbits(32), rnd.getrandbits(4)))
        elif k < 0.035:
            R.append(rec(rnd.choice((8, 0xC, 1, 0x100)), rnd.getrandbits(32)))
        elif k < 0.04:
            R.append(rec(rnd.choice((0, 4)), 0, write=False))
        else:
            R.append(rec(4, rnd.getrandbits(32), rnd.getrandbits(4)))
    return R, {120, p1, p1 + 10000}


def pattern_cell(x, y):
    """lcd_pattern.v's cell(), for the model."""
    if x < 8 or x >= 760 or y < 8 or y >= 1016:
        return 0
    if y < 256:
        return x // 192
    if y >= 768:
        return 3 if ((x >> 5) ^ (y >> 5)) & 1 else 1
    if ((x + y) & 63) < 4:
        return 0
    return 3


def pattern_reqs():
    """The requests lcd_pattern.v makes, as screenupdate makes them."""
    R = []
    for q in range(256):
        y = 4 * q
        R.append(rec(0, y >> 8))
        R.append(rec(0, (y >> 2) & 0x3F))
        for x in range(W):
            R.append(rec(4, sum(pattern_cell(x, y + r) << (2 * r)
                                for r in range(4))))
    return R


def recorded_reqs(path):
    with open(path, "rb") as f:
        raw = f.read()
    if path.endswith(".gz"):
        raw = gzip.decompress(raw)
    R = []
    for i in range(0, len(raw), 5):
        k = raw[i]
        R.append(rec(4 * (k & 1), struct.unpack_from("<I", raw, i + 1)[0],
                     k >> 4))
    return R, hashlib.sha256(raw).hexdigest()


def main(argv):
    quick = "--quick" in argv
    path = None
    if "--writes" in argv:
        path = argv[argv.index("--writes") + 1]
    else:
        b = os.path.join(HOBBIT, "fpga", "build", "lcd", "lcd_writes.bin")
        path = b if os.path.exists(b) else COMMITTED
    os.makedirs(OUT, exist_ok=True)
    tb = build()

    print("== synthetic")
    reqs, points = synthetic()
    lcd, snaps = model(reqs, points)
    d, n, ovr = run(tb, "synthetic", reqs, points=points)
    check(n == len(reqs), "synthetic: %d requests issued" % len(reqs))
    check(ovr == lcd.overruns, "synthetic: overruns %d == LcdPanel's %d"
          % (ovr, lcd.overruns))
    compare_bufs("synthetic", d, snaps)
    untouched = sum(1 for v in snaps[120][:40 * W] if v == 0)
    check(untouched == 40 * W, "synthetic: at request 120 the model's rows "
          "0..39 were never written, level 0 (the RTL's are compared "
          "against those zeros)")

    print("== pattern (the test bitstream's writer)")
    preqs = pattern_reqs()
    plcd, psnaps = model(preqs, ())
    d, n, ovr = run(tb, "pattern", pattern=True, frames=1)
    check(n == len(preqs), "pattern: lcd_pattern issued %d requests (%d "
          "expected)" % (n, len(preqs)))
    compare_bufs("pattern", d, psnaps)
    compare_frame("pattern", d, plcd.grey(), "frame_pattern")

    if quick:
        print("== recorded: skipped (--quick)")
    else:
        print("== recorded 8½ session: %s" % path)
        reqs, digest = recorded_reqs(path)
        print("      %d requests, sha256 of the recording %s"
              % (len(reqs), digest))
        N = len(reqs)
        points = {N // 4, N // 2, 3 * N // 4}
        lcd, snaps = model(reqs, points)
        d, n, ovr = run(tb, "recorded", reqs, points=points, frames=1)
        check(n == N, "recorded: %d requests issued" % N)
        check(ovr == lcd.overruns, "recorded: overruns %d == LcdPanel's %d"
              % (ovr, lcd.overruns))
        compare_bufs("recorded", d, snaps)
        por = compare_frame("recorded", d, lcd.grey(), "frame_8half")
        import test_p9term
        w, h, grey = test_p9term.read_png(
            os.path.join(HOBBIT, "tests", "net", "8half_ls.png"))
        n, at = diff(por, grey)
        check((w, h) == (W, H) and n == 0,
              "recorded: scanned frame equals tests/net/8half_ls.png "
              "(%d differ%s)" % (n, ", first at x,y=%s" % (at,) if n else ""))

    print("\n%s: %d failed" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
