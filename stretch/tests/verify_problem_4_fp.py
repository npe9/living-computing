#!/usr/bin/env python3
"""verify_problem_4_fp.py PROBLEM [--sub OLD NEW]... -- the floating-point
problems of C22-6578 Chapter 4, checked against the NUMBER THE PAGE ASKS
FOR instead of against a word copied from the model.

A deck in ../decks/problem_4_*.strap is run on the model through
run_program.sh with a DUMP of its data words.  Two kinds of check:

  exact    a word worked by hand in the deck's header, compared bit for
           bit.  These go to gen_tb as ordinary checks, with the halt PC.
  within   a floating word (Reference Manual printed pp.78-79: bit 0
           exponent flag, 1-10 exponent magnitude, 11 exponent sign,
           12-59 fraction, 60 sign, 61-63 flags) decoded and compared
           with the real number the problem statement defines, computed
           here in sixty-digit decimal arithmetic FROM THE OPERAND WORDS
           AS ASSEMBLED (so a decimal literal's own truncation is not
           charged to the program).  The bound is in UNITS of the
           expected value's 48-bit fraction, 2**(e-48) with 2**(e-1) <=
           |want| < 2**e, and each problem's bound is justified in its
           deck.  The units observed are printed, so a bound that is
           slack by a factor of ten shows.

WHY A BOUND AND NOT A WORD.  Pinning the low bits needs an independent
bit-exact model of the 7030's double-length arithmetic; the only one in
the project IS the thing under test.  A word copied from its output
would agree with it by construction.  So the low bits are not pinned and
the decks say so.  What the bound does catch is measured: every deck
records a data-side injection and what failed.

THE REACH IS PRINTED AND A SHORT ONE FAILS: a check whose word is absent
from the dump is a failure, not a skip, and so is a run that printed no
"ALL TESTS PASSED".  The exit status is the verdict.

--sub OLD NEW replaces the one occurrence of the text OLD in the deck
with NEW in a temporary copy (the deck itself is never written) -- the
injection mechanism; OLD must occur exactly once.
"""
import os
import re
import subprocess
import sys
import tempfile
from decimal import Decimal as D, getcontext

getcontext().prec = 60
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'strap'))

PI = D('3.14159265358979323846264338327950288419716939937510582097494')


def fp_value(w):
    """A floating word as an exact Decimal; None if the exponent flag is on."""
    if w >> 63:
        return None
    e = (w >> 53) & 0x3FF
    if (w >> 52) & 1:
        e = -e
    v = D((w >> 4) & ((1 << 48) - 1)) / D(1 << 48) * (D(2) ** e)
    return -v if (w >> 3) & 1 else v


def units(got, want):
    """|got - want| in units of want's 48-bit fraction."""
    if want == 0:
        return D(0) if got == 0 else D('Infinity')
    e = 0
    a = abs(want)
    while a >= 1:
        a /= 2
        e += 1
    while a < D('0.5'):
        a *= 2
        e -= 1
    return abs(got - want) / (D(2) ** (e - 48))


# ---------------------------------------------------------------------
# The problems.  Each entry: deck, module, halt label, dump = (first
# symbol, last symbol), exact = [(label, symbol-or-"addrIndex(n)", word)],
# within = [(label, result symbol, function of the image -> Decimal,
# bound in units)].  `img` maps a symbol to its assembled floating value.
# ---------------------------------------------------------------------

def p4_11(sym):
    xw14 = sym['XW14'] // 64
    exact = [('E%d_sentinel' % k, 'E%d' % k, 7) for k in (1, 2, 3, 4, 5, 8)]
    exact += [('R6_sentinel', 'R6', 7), ('R7_sentinel', 'R7', 7),
              ('E6_plus800_flagged', 'E6', 0x814C800000000000),
              ('E7_minus800_bit10', 'E7', 0x816C800000000000),
              ('x14_value14_count0', 'addrIndex(14)', (14 << 46) | xw14)]
    # What the PROGRAM computes, as a real number: 2**(x * RLN2) with RLN2
    # the one-word constant as assembled.  e**x itself is off from that
    # by up to 1.39 |x| units (the deck's header), so both are checked:
    # the tight one against the program's own number, the loose one
    # against the page's.
    ln2 = D(2).ln()
    within = [('R%d_two_to_x%d_times_RLN2' % (k, k), 'R%d' % k,
               (lambda img, k=k: (img('X%d' % k) * img('RLN2') * ln2).exp()), 4)
              for k in (1, 2, 3, 4, 5, 8)]
    within += [('R%d_exp_x%d' % (k, k), 'R%d' % k,
                (lambda img, k=k: img('X%d' % k).exp()),
                (lambda img, k=k: 8 + 2 * abs(img('X%d' % k))))
               for k in (1, 2, 3, 4, 5, 8)]
    return dict(module='StretchP411Tb',
                halt='HALT', dump=('X1', 'E8'), exact=exact, within=within)


def exp_as_programmed(img, x):
    """EXP's result as a real number: 2**(x * RLN2), RLN2 as assembled."""
    return (x * img('RLN2') * D(2).ln()).exp()


def p4_12(sym):
    xw14 = sym['XW14'] // 64
    halt = sym['ERR'] // 32 - 1           # the BEW printed above ERR

    def t_prog(img):
        return exp_as_programmed(img, -img('EKS'))

    def u_prog(img):
        return 2 * img('EKS') * exp_as_programmed(img, t_prog(img))

    def t_true(img):
        return (-img('EKS')).exp()

    def u_true(img):
        return 2 * img('EKS') * t_true(img).exp()

    exact = [('x15_second_call', 'addrIndex(15)', (sym['RTURN'] + 32 + 64) << 40),
             ('x14_value14_count0', 'addrIndex(14)', (14 << 46) | xw14)]
    within = [
        ('TEMP_t_as_programmed', 'TEMP', t_prog, 4),
        ('TEMP1_u_as_programmed', 'TEMP+1', u_prog, 4),
        ('ACC_f_as_programmed', 'ACC',
         lambda img: u_prog(img) / (1 - t_prog(img)).sqrt(), 4),
        ('TEMP_exp_minus_x', 'TEMP', t_true, 16),
        ('TEMP1_2x_exp_t', 'TEMP+1', u_true, 16),
        ('ACC_f_of_pi', 'ACC',
         lambda img: u_true(img) / (1 - t_true(img)).sqrt(), 16),
    ]
    return dict(module='StretchP412Tb', halt=halt, dump=(8, 'WON'),
                exact=exact, within=within)


PROBLEMS = {'4.11': ('problem_4_11.strap', p4_11),
            '4.12': ('problem_4_12.strap', p4_12)}


def main():
    args = sys.argv[1:]
    subs = []
    while '--sub' in args:
        i = args.index('--sub')
        subs.append((args[i + 1], args[i + 2]))
        del args[i:i + 3]
    if len(args) != 1 or args[0] not in PROBLEMS:
        raise SystemExit("usage: verify_problem_4_fp.py %s [--sub OLD NEW]..."
                         % '|'.join(sorted(PROBLEMS)))
    from strap_asm import assemble
    deck_name, spec_fn = PROBLEMS[args[0]]
    with open(os.path.join(HERE, '..', 'decks', deck_name)) as f:
        src = f.read()
    for old, new in subs:
        if src.count(old) != 1:
            raise SystemExit("--sub: %r occurs %d times, need exactly 1"
                             % (old, src.count(old)))
        src = src.replace(old, new)
        print("INJECTED: %r -> %r" % (old, new))
    prog = assemble(src)
    sym = prog.symtab
    spec = spec_fn(sym)

    def word_of(s):
        if isinstance(s, int):
            return s
        if '+' in s:                      # SYMBOL+words
            base, off = s.split('+')
            return sym[base] // 64 + int(off)
        return sym[s] // 64

    def img(s):
        return fp_value(prog.words[word_of(s)])

    first, last = word_of(spec['dump'][0]), word_of(spec['dump'][1])
    halt = spec['halt']
    checks = ["PC=%d" % (halt if isinstance(halt, int) else sym[halt] // 32),
              "DUMP=%d,%d" % (first, last - first + 1),
              "STEPS=%d" % spec.get('steps', 2000000)]
    for label, where, word in spec['exact']:
        addr = where if where.startswith('addrIndex') else str(word_of(where))
        checks.append("%s:%s=0x%X" % (label, addr, word))
    with tempfile.TemporaryDirectory() as tmp:
        deck = os.path.join(tmp, deck_name)
        with open(deck, 'w') as f:
            f.write(src)
        r = subprocess.run(["./run_program.sh", deck, spec['module']] + checks,
                           cwd=HERE, capture_output=True, text=True)
    shown = [ln for ln in r.stdout.splitlines()
             if ln.startswith(('PASS', 'FAIL', 'ALL TESTS', 'StretchCore'))]
    print("\n".join(shown))
    fails = 0
    if r.returncode != 0:
        print(r.stdout[-1500:], r.stderr[-1500:])
        print("FAIL run_program.sh exit status", r.returncode)
        fails += 1
    if any(ln.startswith('FAIL') for ln in shown):
        fails += 1
    if not any(ln.startswith('ALL TESTS PASSED') for ln in shown):
        print("FAIL the run printed no ALL TESTS PASSED")
        fails += 1
    dump = {int(a): int(v, 16)
            for a, v in re.findall(r"^MEMDUMP (\d+) ([0-9a-f]{16})$", r.stdout, re.M)}
    n_within = 0
    for label, where, fn, bound in spec['within']:
        n_within += 1
        if where == 'ACC':
            # The accumulator as the program left it: $L is word 8, and
            # its sign is bit 4 of the sign byte register, word 10
            # (C22-6578 printed p.55; Reference Manual printed p.86).
            # Bits 60-63 of word 8 are fraction bits 49-52, not a sign.
            if 8 not in dump or 10 not in dump:
                print("FAIL %s: words 8 and 10 are not in the dump" % label)
                fails += 1
                continue
            a = 8
            dump = dict(dump)
            dump[8] = (dump[8] & ~0xF) | (((dump[10] >> 59) & 1) << 3)
        else:
            a = word_of(where)
        if a not in dump:
            print("FAIL %s: word %d is not in the dump" % (label, a))
            fails += 1
            continue
        want = fn(img)
        got = fp_value(dump[a])
        if got is None:
            print("FAIL %s: %016x has its exponent flag on; want %.17E"
                  % (label, dump[a], want))
            fails += 1
            continue
        u = units(got, want)
        if callable(bound):
            bound = bound(img)
        ok = u <= bound
        print("%s %s = %016x = %.17E, want %.17E, off %.2f units (bound %.0f)"
              % ("PASS" if ok else "FAIL", label, dump[a], got, want, u, bound))
        if not ok:
            fails += 1
    print("verify_problem_4_fp %s: %d exact checks and the PC through gen_tb, "
          "%d within-bound checks, %d dumped words read"
          % (args[0], len(spec['exact']), n_within, len(dump)))
    if len(dump) != last - first + 1:
        print("FAIL the dump is short: %d of %d words" % (len(dump), last - first + 1))
        fails += 1
    print("ALL CHECKS PASSED" if not fails else "FAILED")
    return 1 if fails else 0


if __name__ == '__main__':
    sys.exit(main())
