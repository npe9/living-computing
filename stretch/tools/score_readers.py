#!/usr/bin/env python3
"""Score several independent readings of MCP listing pages, alone and voted.

    python3 tools/score_readers.py MULTIDIR

MULTIDIR holds pNNN/<reader>.tsv from tools/multi_read.py.  Truth is
strap/listing_truth.py: what the landed deck asserts, keyed by LINE.

ROW PAIRING is strap/listing_read.py's: the LINE column of the
reference reader (vis_full_300) is fitted, and every reader is sampled
at each fitted line's y -- all readers share the full-page frame.

FIELDS, both compared on all nine characters:
    LOCATION   "221515.00"      BINARY half word 1, octal part "221512.40"

ALPHABET CONSTRAINT: strap/listing_read.py.
"""
import collections
import glob
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "strap"))
import listing_truth  # noqa: E402
from listing_read import LOC_X, BIN_X, load, fit_lines, field_at  # noqa: E402

REF = "vis_full_300"


def main(multidir):
    pages = sorted(int(os.path.basename(d)[1:]) for d in glob.glob(os.path.join(multidir, "p*")))
    readers = sorted(os.path.basename(f)[:-4] for f in glob.glob(os.path.join(multidir, "p%03d" % pages[0], "*.tsv")))
    stat = {r: collections.Counter() for r in readers}
    per_row = []                     # (field, truth, {reader: value})
    fits = []
    for pg in pages:
        truth = listing_truth.truth(pg)
        if not truth:
            continue
        d = os.path.join(multidir, "p%03d" % pg)
        obs = {r: load(os.path.join(d, r + ".tsv")) for r in readers}
        f = fit_lines(obs[REF])
        if f is None:
            print(f"p.{pg}: LINE column unreadable, page skipped")
            continue
        y0, pitch, agree, n = f
        fits.append((pg, agree, n))
        for line, (loc, b1) in truth.items():
            y = y0 + (line - 1) * pitch
            for field, want, xw in (("loc", loc, LOC_X), ("bin", b1, BIN_X)):
                if not want:
                    continue
                vals = {}
                for r in readers:
                    v = field_at(obs[r], y, pitch, xw)
                    stat[r][field + "_n"] += 1
                    if v:
                        vals[r] = v
                        stat[r][field + "_read"] += 1
                        if v == want:
                            stat[r][field + "_ok"] += 1
                per_row.append((field, want, vals, pg, line))

    print(f"pages scored: {len(fits)}; LINE-column fit agreement "
          f"{sum(a for _, a, _ in fits)}/{sum(n for _, _, n in fits)} line reads\n")
    for field, name in (("loc", "LOCATION"), ("bin", "BINARY half 1")):
        print(f"{name}  (rows with truth: {stat[readers[0]][field + '_n']})")
        print(f"   {'reader':14s} {'coverage':>9s} {'accuracy':>9s}")
        for r in readers:
            s = stat[r]
            n, rd, ok = s[field + "_n"], s[field + "_read"], s[field + "_ok"]
            print(f"   {r:14s} {100*rd/n:8.1f}% {100*ok/max(1,rd):8.2f}%")
        rows = [x for x in per_row if x[0] == field]
        for k in (2, 3, 4, 5):
            cov = ok = 0
            for _, want, vals, _, _ in rows:
                c = collections.Counter(vals.values())
                if not c:
                    continue
                v, cnt = c.most_common(1)[0]
                if cnt >= k and (len(c) == 1 or c.most_common(2)[1][1] < cnt):
                    cov += 1
                    ok += (v == want)
            print(f"   VOTE >={k} agree {100*cov/len(rows):7.1f}% {100*ok/max(1,cov):8.2f}%")
        # CROSS-ENGINE: a value both a Vision and a tesseract reader read
        cov = ok = 0
        for _, want, vals, _, _ in rows:
            vv = {v for r, v in vals.items() if r.startswith("vis")}
            tv = {v for r, v in vals.items() if r.startswith("tes")}
            both = vv & tv
            if len(both) == 1:
                cov += 1
                ok += (next(iter(both)) == want)
        print(f"   VISION+TESS agree {100*cov/len(rows):6.1f}% {100*ok/max(1,cov):8.2f}%")
        # INDEPENDENCE: when A is wrong, how often is B wrong THE SAME WAY?
        print("   shared error, P(B same wrong | A wrong), A = row, B = column")
        print("   " + " " * 14 + "".join(f"{r[:3]+r[-4:]:>9s}" for r in readers))
        for a in readers:
            cells = []
            for b in readers:
                aw = same = 0
                for _, want, vals, _, _ in rows:
                    if a in vals and vals[a] != want and b in vals:
                        aw += 1
                        same += (vals[b] == vals[a])
                cells.append("        -" if a == b else (f"{same:>4d}/{aw:<4d}" if aw else "      n/a"))
            print(f"   {a:14s}" + "".join(cells))
        # unanimous disagreement with the deck: every reader that read it agrees, and not with the deck
        sus = [(pg, line, want, vals) for _, want, vals, pg, line in rows
               if len(vals) >= 4 and len(set(vals.values())) == 1
               and next(iter(vals.values())) != want]
        print(f"   ALL >=4 readers agree AGAINST the deck: {len(sus)}")
        for pg, line, want, vals in sus[:10]:
            print(f"      p.{pg} line {line}: deck {want}  readers {next(iter(vals.values()))}")
        print()


if __name__ == "__main__":
    main(sys.argv[1])
