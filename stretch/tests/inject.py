#!/usr/bin/env python3
"""inject.py -- run a list of source mutations against a verifier and
report, for each, whether anything caught it.

This project's convention is that every claim gets a MEASURED
INJECTION: break the code in a named way, run the test, and record
the address or the check that fails.  An injection that SURVIVES is
reported as surviving, because it says something true about the test.

>>> BUT TWO MECHANICAL FAULTS PRODUCE A FALSE "SURVIVED", AND BOTH
WERE HIT ON 2026-10-22 WITHIN AN HOUR OF EACH OTHER. <<<

1. A STALE .pyc.  A one-character mutation leaves the file the SAME
   SIZE, and restoring it can land in the same second, so CPython's
   (mtime, size) staleness check can reuse bytecode compiled from the
   INJECTED source -- or, worse, the test can run against the
   PREVIOUS injection's bytecode.  This harness clears __pycache__
   between steps and runs with -B and PYTHONDONTWRITEBYTECODE.

2. A NON-UNIQUE ANCHOR.  "if not stmt.fields or not
   stmt.fields[0].strip():" occurs EIGHT times in strap_asm.py, once
   per pseudo-operation that checks for a null field.  A
   str.replace(old, new, 1) against it patched the FIRST one -- a
   different pseudo-operation entirely -- and the injection was
   reported as surviving when it had never been applied.  This
   harness refuses an anchor that does not occur exactly once.

Both faults fail in the same direction, which is the dangerous one:
they make a test look stronger than it is.

Usage:
    python3 inject.py GOOD_COPY VERIFIER INJECTIONS_PY [SRC]

GOOD_COPY     an untouched copy of the file to mutate
VERIFIER      a script in tests/, run with PYTHONPATH=../strap:.
INJECTIONS_PY a file evaluating to [(name, old_text, new_text), ...]
SRC           the file to mutate (default strap/strap_asm.py)

The source file is restored from GOOD_COPY after every step and
again at the end; the caller should diff the two to confirm.
"""
import shutil
import subprocess
import sys

GOOD = sys.argv[1]
TEST = sys.argv[2]
INJ = eval(open(sys.argv[3]).read())
SRC = sys.argv[4] if len(sys.argv) > 4 else 'strap/strap_asm.py'
ENV = {'PYTHONPATH': '../strap:.', 'PATH': '/usr/bin:/bin',
       'PYTHONDONTWRITEBYTECODE': '1'}


def clear_cache():
    for d in ('strap/__pycache__', 'tests/__pycache__'):
        shutil.rmtree(d, ignore_errors=True)


def main():
    for name, old, new in INJ:
        shutil.copy(GOOD, SRC)
        s = open(SRC).read()
        n = s.count(old)
        if n != 1:
            raise SystemExit(
                f"{name}: anchor occurs {n} times, not once -- an injection "
                f"against a non-unique anchor patches the wrong site and "
                f"reports as SURVIVED")
        open(SRC, 'w').write(s.replace(old, new, 1))
        clear_cache()
        r = subprocess.run([sys.executable, '-B', TEST], cwd='tests',
                           capture_output=True, text=True, env=ENV)
        out = (r.stdout + r.stderr).splitlines()
        bad = [l for l in out
               if l.startswith('FAIL') or 'FAILED' in l or 'Error' in l]
        print("=== " + name)
        if not bad:
            print("    SURVIVED -- nothing caught it")
        for l in bad[:6]:
            print("    " + l[:150])
    shutil.copy(GOOD, SRC)
    clear_cache()
    print("restored")


if __name__ == '__main__':
    main()
