#!/usr/bin/env python3
"""The checks of bsv/run_win_fpga.sh on one nextpnr-ecp5 log (window
hardware H3, docs/simpos/window_hardware_plan.md).  OURS.

    python3 -I tools/win_fpga_check.py NEXTPNR.LOG XDOM_NS DP16KD [LABEL...]

nextpnr prints its timing summary twice (after placement, an estimate,
and after routing); the LAST of each line is the routed figure, and only
that is used.  Checked:
  - every "Max frequency for clock" line says PASS (each clock against
    its own constraint: the LPF's 25 MHz, and the PLL outputs nextpnr
    derives from the EHXPLLL parameters);
  - the three clocks are there (the 25 MHz pin, pclk, sclk);
  - DP16KD used = the expected count;
  - THE SERIALIZER'S LOAD PHASE: the "Max delay posedge pclk -> posedge
    sclk" figure is at most XDOM_NS.  nextpnr 0.6 only reports this
    path (it has no multicycle or max-delay constraint between two PLL
    outputs), so this check is the constraint; the budget is derived in
    bsv/WinScanOut.bsv (mkWinTmdsSer) and bsv/run_win_fpga.sh.
The other cross-domain lines are printed, unchecked (each goes through a
synchronizer: the scan command FIFO, the reset synchronizers).
Prints one summary line; exit status 1 if a check fails.
"""
import re
import sys


def main(argv):
    if len(argv) < 3:
        print(__doc__)
        return 2
    log, xdom, want_bram = argv[0], float(argv[1]), int(argv[2])
    label = ' '.join(argv[3:]) or log
    freq, delay, util = {}, {}, {}
    with open(log) as fh:
        for ln in fh:
            m = re.search(r"Max frequency for clock\s+'([^']+)': ([0-9.]+) MHz "
                          r"\((PASS|FAIL) at ([0-9.]+) MHz\)", ln)
            if m:
                freq[m.group(1)] = (float(m.group(2)), m.group(3), float(m.group(4)))
                continue
            m = re.search(r"Max delay (.+?)\s*->\s*(.+?)\s*: ([0-9.]+) ns", ln)
            if m:
                delay[(m.group(1).strip(), m.group(2).strip())] = float(m.group(3))
                continue
            m = re.search(r"^Info:\s+(\w+):\s+(\d+)/\s*(\d+)", ln)
            if m:
                util[m.group(1)] = (int(m.group(2)), int(m.group(3)))
    bad = []

    def clk(key):
        hits = [k for k in freq if key in k]
        if len(hits) != 1:
            bad.append('clock %s: %d matches in the log' % (key, len(hits)))
            return None
        f = freq[hits[0]]
        if f[1] != 'PASS':
            bad.append('%s %.2f MHz FAILS at %.2f' % (key, f[0], f[2]))
        return f

    sysf, pf, sf = clk('clk_25mhz'), clk('$pclk'), clk('$sclk')
    for k, f in freq.items():
        if f[1] != 'PASS' and not any(x in k for x in ('clk_25mhz', '$pclk', '$sclk')):
            bad.append('clock %s FAILS' % k)
    xd = [v for (a, b), v in delay.items() if '$pclk' in a and '$sclk' in b]
    if len(xd) != 1:
        bad.append('pclk -> sclk: %d delay lines (expected one)' % len(xd))
        x = None
    else:
        x = xd[0]
        if x > xdom:
            bad.append('pclk -> sclk %.2f ns > %.2f ns' % (x, xdom))
    bram = util.get('DP16KD', (None, None))[0]
    if bram != want_bram:
        bad.append('DP16KD %s, expected %d' % (bram, want_bram))
    comb = util.get('TRELLIS_COMB', (0, 0))
    ff = util.get('TRELLIS_FF', (0, 0))[0]

    def fs(f):
        return '%.2f' % f[0] if f else '?'
    others = ', '.join('%s -> %s %.2f' % (a.replace('posedge ', '').replace('$glbnet$', '')
                                          .replace('$TRELLIS_IO_IN', ''),
                                          b.replace('posedge ', '').replace('$glbnet$', '')
                                          .replace('$TRELLIS_IO_IN', ''), v)
                       for (a, b), v in sorted(delay.items())
                       if not ('$pclk' in a and '$sclk' in b))
    print('   %s: TRELLIS_COMB %d/%d, TRELLIS_FF %d, DP16KD %s/208; Fmax sys %s (25), '
          'pclk %s (%s), sclk %s (%s) MHz; pclk -> sclk %s ns (<= %.2f checked)'
          % (label, comb[0], comb[1], ff, bram, fs(sysf), fs(pf),
             '%.2f' % pf[2] if pf else '?', fs(sf), '%.2f' % sf[2] if sf else '?',
             '%.2f' % x if x is not None else '?', xdom))
    print('     other cross-domain (unchecked, synchronized): %s' % others)
    for b in bad:
        print('   FAIL %s: %s' % (label, b))
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
