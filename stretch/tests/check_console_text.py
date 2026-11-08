"""Read what MCP typed on the console out of a simulation log.

usage: check_console_text.py LOG "TEXT" ["TEXT" ...]

The log carries "CONSOLE <i> <hex>" lines (tests/gen_tb.py's
console_dump).  The words are decoded eight bytes at a time through the
IQS character set (strap/charsets.py, the 89 set MCP's messages are
assembled in), the control characters MCP types between lines are
dropped, and every TEXT must appear somewhere in what is left.

A message is looked for WHEREVER it was typed, not at a word index: the
index depends on how many words every earlier message took, which is
MCP's business, and a check pinned to it would fail for a change that
moved nothing a reader of the console would see.

Prints PASS/FAIL per TEXT and the decoded console, and exits non-zero
on any FAIL.
"""
import re
import sys

import charsets

IQS_CHAR = {code: ch for ch, code in charsets.IQS.items()}


def console_text(log):
    # The core logs every word as it is typed (StretchCore.bsv,
    # CONSOLE_TYPED), which is the whole paper; the end-of-run CONSOLE
    # dump is only the last ConsoleWords of it, since the buffer wraps.
    typed = [int(h, 16) for h in
             re.findall(r"^CONSOLE_TYPED ([0-9a-f]{16})$", log, re.M)]
    words = dict(enumerate(typed))
    if not typed:
        for m in re.finditer(r"^CONSOLE (\d+) ([0-9a-f]{16})$", log, re.M):
            words[int(m.group(1))] = int(m.group(2), 16)
    out = []
    for i in range(max(words) + 1 if words else 0):
        w = words.get(i, 0)
        for b in range(8):
            out.append(IQS_CHAR.get((w >> (56 - 8 * b)) & 0xFF, ""))
    return "".join(out)


def main(argv):
    log = open(argv[1]).read()
    text = console_text(log)
    if not text:
        print("FAIL console_dump: no CONSOLE lines in the log")
        return 1
    fails = 0
    for want in argv[2:]:
        if want in text:
            print(f"PASS console_types {want!r}")
        else:
            print(f"FAIL console_types {want!r}")
            fails += 1
    print("console:", " ".join(text.split()))
    if fails:
        print(f"{fails} TEST(S) FAILED")
        return 1
    print("ALL TESTS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
