#!/usr/bin/env python3
"""Find things in the OCR'd MCP listing without rendering a page.

THE OCR IS A FINDING AID, NOT A SOURCE.  Every character in these
files came from tesseract on a 1963 drum-printer scan, and
docs/listing_typography.md is forty sections of why that scan cannot
be trusted a glyph at a time.  Nothing here may be transcribed into a
deck.  What it is for is the question that used to cost a render:
WHICH PAGE, and roughly WHICH LINE.

Page numbering: MCP_Mar63_001-249 PDF page N is printed page N-7
(docs/NEXT.md's offset table).  The second volume starts at printed
p.250.

Usage:
    listing_index.py sym TPICA          -- pages naming a symbol
    listing_index.py addr 004604        -- pages showing an address
    listing_index.py page 80            -- dump one printed page
    listing_index.py grep 'CONVERT BE'  -- free text
"""
import os
import re
import sys

OCR = os.path.join(os.path.dirname(os.path.abspath(__file__)))
VOLS = [("MCP_Mar63_001-249.txt", 7, 1, 249),
        ("MCP_Mar63_250-445.txt", -249, 250, 445)]


def pages(ocrdir):
    """Yield (printed_page, text) for every page of both volumes."""
    for fname, off, lo, hi in VOLS:
        path = os.path.join(ocrdir, fname)
        if not os.path.exists(path):
            continue
        cur, buf = None, []
        for line in open(path, errors="replace"):
            m = re.match(r'===== \S+ PDF page (\d+) =====', line)
            if m:
                if cur is not None:
                    yield cur, "".join(buf)
                cur, buf = int(m.group(1)) - off, []
            else:
                buf.append(line)
        if cur is not None:
            yield cur, "".join(buf)


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        return 2
    ocrdir = os.environ.get("MCP_OCR", "docs/ocr")
    mode, arg = sys.argv[1], sys.argv[2]
    hits = 0
    for pg, text in pages(ocrdir):
        if mode == "page":
            if pg == int(arg):
                print(text)
                return 0
            continue
        if mode == "sym":
            # the listing prints "T PICA" where a deck writes TPICA
            pat = re.compile(r'\b' + r'\s*'.join(re.escape(c) for c in arg) + r'\b')
        elif mode == "addr":
            pat = re.compile(re.escape(arg))
        else:
            pat = re.compile(arg)
        for i, line in enumerate(text.splitlines(), 1):
            if pat.search(line):
                print("p.%-4d %s" % (pg, line.strip()[:110]))
                hits += 1
    if mode != "page":
        print("-- %d line(s)" % hits, file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
