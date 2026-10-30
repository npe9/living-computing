#!/usr/bin/env python3
"""A SECOND READING of a listing page's LOCATION column, by OCR.

>>> THIS IS A CROSS-CHECK, NOT A SOURCE. <<<  The deck is transcribed
by reading the page; Rule 3 of this project is that printed machine
code is transcribed and checked, not inferred, and an OCR pass on a
1963 drum-printer scan is not a transcription.  Measured on printed
p.86 at 600 dpi with a digit whitelist, tesseract 5.5 returns roughly
85% of the location column correctly -- "004754.0" for 004754.00,
"00476.31" for 004760.31, a dropped digit every few lines.  Transcribe
from that and the image gets a wrong word in it that nothing notices
until it costs an afternoon.

WHAT IT IS GOOD FOR is disagreement.  Two independent readings of the
same column, one by eye and one by machine, agree on most lines; the
ones they differ on are exactly the lines worth rendering at 900 dpi
and looking at again.  That is cheaper than re-reading every line
twice, and it is the same discipline the deck's own listing comments
serve -- a second record that has to match.

    python3 mcp_ocr.py PRINTED_PAGE [X0 W]   # x in 300-dpi pixels

prints "line N: LOCATION" for everything it can read, so a caller can
diff it against the SYMBOLS dict they wrote by eye.

The default column window comes from mcp_columns.py's measurement of
printed p.83 and p.86, where LINE+LOCATION sit at roughly x 700-1300
in 300-dpi pixels.  Pass X0 and W to move it; mcp_columns.py prints the
runs for any page.
"""
import re
import subprocess
import sys
import os
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
PDF = os.path.join(HERE, "..", "docs", "MCP_Mar63_001-249.pdf")
DPI = 600


def ocr_column(printed, x0_300=725, w_300=575):
    page = printed + 7
    # NOT /tmp.  pdftoppm writes there happily and tesseract then
    # reports "image file not found" for the very file that exists --
    # the two processes do not see the same /tmp under this sandbox.
    # tempfile honours TMPDIR, so both see the same directory.
    tmpdir = tempfile.mkdtemp(prefix="mcp_ocr_")
    out = os.path.join(tmpdir, f"p{printed}")
    scale = DPI // 300
    subprocess.run(["pdftoppm", "-f", str(page), "-l", str(page),
                    "-r", str(DPI), "-png",
                    "-x", str(x0_300 * scale), "-y", str(720),
                    "-W", str(w_300 * scale), "-H", str(4200),
                    PDF, out], check=True, capture_output=True)
    png = next(out + s for s in (f"-{page:03d}.png", f"-{page}.png")
               if os.path.exists(out + s))
    # NOT text=True: leptonica writes bytes to stderr that are not
    # UTF-8 (a PNG header turned up there), and the decode blows up
    # before any OCR output is seen.  Capture bytes, decode leniently.
    r = subprocess.run(["tesseract", png, "stdout", "--psm", "6",
                        "-c", "tessedit_char_whitelist=0123456789.*"],
                       capture_output=True)
    return r.stdout.decode("utf-8", errors="replace")


def parse(text):
    """(line_number, location) for every row OCR could read fully.

    A row is "NN* LLLLLL.BB".  Anything that does not match that shape
    exactly is DROPPED rather than guessed at -- a half-read address is
    worse than a missing one, because it looks like a reading.
    """
    out = []
    for raw in text.splitlines():
        s = raw.strip()
        # The LINE NUMBER is often dropped or merged by OCR ("*004753.00"
        # with no number, ".11*004755.27" with a leading dot), so it is
        # OPTIONAL here.  The LOCATION is the datum worth having and it
        # must be complete -- six octal digits, a point, two more -- or
        # the row is dropped.  A half-read address is worse than a
        # missing one because it looks like a reading.
        m = re.search(r"(?:(\d{1,2})\*)?\s*([0-7]{6}\.[0-7]{2})\s*$", s)
        # OCTAL DIGITS ARE 0-7, so a location containing an 8 or a 9 is
        # not a disagreement with the page -- it is impossible, and
        # therefore an OCR error.  printed p.87 produced "800512.71"
        # where the page reads 005012.71.  Rejecting them here keeps the
        # cross-check's disagreements meaningful: every row it DOES
        # report is at least a well-formed address.
        if m and m.group(2):
            out.append((int(m.group(1)) if m.group(1) else None,
                        m.group(2)))
    return out


def main():
    if len(sys.argv) < 2:
        raise SystemExit(f"usage: {sys.argv[0]} PRINTED_PAGE [X0_300 W_300]")
    printed = int(sys.argv[1])
    kw = {}
    if len(sys.argv) > 3:
        kw = dict(x0_300=int(sys.argv[2]), w_300=int(sys.argv[3]))
    text = ocr_column(printed, **kw)
    rows = parse(text)
    print(f"printed p.{printed}: {len(rows)} rows read cleanly "
          f"(a dropped row means OCR, not the page)")
    for n, loc in rows:
        print(f"  line {str(n) if n is not None else '??':>2}: {loc}")


if __name__ == "__main__":
    main()
