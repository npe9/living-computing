#!/usr/bin/env python3
"""check_spelling_checker_does_not_degrade.py -- the checker must not
quietly check LESS than it claims.

`check_symbol_spellings.py` had two independent paths that made it
verify a smaller corpus while still printing PASS.  Both were found by
page transcribers who happened to instrument it, not by the suite --
which could never have caught either, because run_tests.sh exports
PYTHONPATH and never patches DECKS.  THAT IS THE POINT OF THIS FILE:
the suite's own happy path is exactly where a silent degradation
hides.

  1. _as_bit() wrapped "import strap_asm" in a bare try/except.  Run
     without `strap` on PYTHONPATH the import failed, every address
     came back symbolic, and the !SYM branch of collect() -- guarded
     by "if bit is not None" -- dropped every block.  MEASURED on one
     corpus: 1080 definitions bare against 1312 with PYTHONPATH, PASS
     both ways.

  2. collect(deck_dir=DECKS) bound the default at DEF time, so the
     obvious idiom -- import the module, set DECKS elsewhere, call
     main() -- was a silent no-op.  MEASURED: with DECKS patched to an
     empty directory, collect() still returned 1155 addresses.

MEASURED INJECTIONS, both run, with the values they actually printed.

  A.  Restore the bare "import strap_asm" inside _as_bit AND remove
      the module-level sys.path fix -- both, because with the path
      fixed the swallowed import succeeds anyway and nothing degrades.
      THREE checks fail, not one:
          real_corpus_is_read                        False
          literal_address_resolves_to_an_int         False
          launch_count_is_independent_of_pythonpath  1080 vs 1312

  B.  Restore "def collect(deck_dir=DECKS)":
          module_DECKS_is_resolved_at_call_time      1155 vs 0
"""
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import check_symbol_spellings as c                        # noqa: E402


def main():
    fails = 0

    def check(name, got, want):
        nonlocal fails
        ok = got == want
        if not ok:
            fails += 1
        print(f"{'PASS' if ok else 'FAIL'} {name} = {got}"
              f"{'' if ok else f' expected {want}'}")

    # 1. The argument is actually used.
    empty = tempfile.mkdtemp()
    check("deck_dir_argument_is_honoured", len(c.collect(empty)[0]), 0)

    # 2. The module global is resolved at CALL time, which is what the
    #    patch-then-call idiom depends on.
    saved = c.DECKS
    try:
        c.DECKS = empty
        check("module_DECKS_is_resolved_at_call_time",
              len(c.collect()[0]), 0)
    finally:
        c.DECKS = saved

    # 3. The real corpus is non-trivial, so a zero above means the
    #    directory and not a parser that stopped reading.
    corpus = len(c.collect()[0])
    check("real_corpus_is_read", corpus > 1000, True)

    # 4. A literal address resolves to an INT.  If strap_asm were
    #    unimportable this returns None and every !SYM block vanishes.
    check("literal_address_resolves_to_an_int",
          isinstance(c._as_bit("(8)5464.40"), int), True)

    # 5. THE REGRESSION THAT MATTERS: the count must not depend on how
    #    the process was launched.  Run the checker as a subprocess
    #    TWICE -- once with PYTHONPATH scrubbed, which is how every
    #    ad-hoc run was made, and once with `strap` on it, which is
    #    what run_tests.sh does -- and compare the two.
    #
    #    Compare the SAME quantity both times.  An earlier draft of
    #    this file compared the subprocess's definition count against
    #    an in-process count of ADDRESS KEYS and failed 1312 against
    #    1155 -- a bug in the test, not in the checker.
    def run(pythonpath):
        env = dict(os.environ)
        if pythonpath is None:
            env.pop("PYTHONPATH", None)
        else:
            env["PYTHONPATH"] = pythonpath
        out = subprocess.run([sys.executable, "check_symbol_spellings.py"],
                             cwd=HERE, env=env, capture_output=True, text=True)
        for tok in out.stdout.split():
            if tok.isdigit():
                return int(tok)
        return None

    bare = run(None)
    with_path = run(os.path.join(HERE, "..", "strap"))
    check("launch_count_is_independent_of_pythonpath", bare, with_path)
    check("launch_count_is_not_degraded", bare is not None and bare > 1000,
          True)

    if fails:
        print(f"\n{fails} TEST(S) FAILED")
    else:
        print("\nALL TESTS PASSED")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
