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


def _unit_of(v):
    """2**(e-48) for 2**(e-1) <= |v| < 2**e."""
    e = 0
    a = abs(v)
    while a >= 1:
        a /= 2
        e += 1
    while a < D('0.5'):
        a *= 2
        e -= 1
    return D(2) ** (e - 48)


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


def p4_13(sym, src=None):
    from strap_asm import assemble
    main = sym['MAIN'] // 64
    x15 = (sym['MAIN'] + 64) << 40        # LVI, $15, $+1.0 at MAIN

    def f(img, x, e):
        t = e(img, -x)
        return 2 * x * e(img, t) / (1 - t).sqrt()

    def rule(e):
        # s * sum of w (f(t + s z) + f(t - s z)), a = 0 and b = 1 so s = t
        # = 1/2 exactly; the nodes and weights are the words AS ASSEMBLED
        # from the page's fifteen-digit decimals, erratum and all.  NOT as
        # assembled: b.  The printed "DD(N), 1.0" is one unit below 1 under
        # STRAP II (P and Q above), so s = t = 1/2 - 2**-49 in the program;
        # the rule keeps the problem's interval [0, 1], and that unit is
        # inside the bound (3.11 units measured 2026-11-16, 2.11 on b = 1).
        def g(img):
            h = D('0.5')
            tot = D(0)
            for i in range(4):
                z, w = img('LEGQ8X+%d' % i), img('LEGQ8W+%d' % i)
                tot += w * (f(img, h + h * z, e) + f(img, h - h * z, e))
            return h * tot
        return g

    # b is the printed DD(N), 1.0: one unit below 1 under STRAP II (deck header)
    exact = [('P_minus_half_b_minus_a', 'LEGQ8P', 0x003FFFFFFFFFFFF8),
             ('Q_half_b_plus_a', 'LEGQ8Q', 0x003FFFFFFFFFFFF0),
             ('x2_restored', 'addrIndex(2)', 0),
             ('x15_restored', 'addrIndex(15)', x15),
             ('LEGQ82_saved_x2', 'LEGQ82', 0),
             ('LEGQ8F_saved_x15', 'LEGQ8F', x15),
             ('x14_value14_count0', 'addrIndex(14)',
              (14 << 46) | (sym['XW14'] // 64))]
    # SVA, $2, LEGQ8A / LEGQ8B: the two "B, $" become "B, SUBR".  The
    # expected words are the same deck assembled with that written out.
    if src is not None:
        patched = src.replace("LEGQ8A  B, $", "LEGQ8A  B, SUBR").replace(
            "LEGQ8B  B, $", "LEGQ8B  B, SUBR")
        assert src.count("LEGQ8A  B, $") == 1 and src.count("LEGQ8B  B, $") == 1
        pw = assemble(patched).words
        for lab in ('LEGQ8A', 'LEGQ8B'):
            exact.append(('%s_branch_is_SUBR' % lab, lab, pw[sym[lab] // 64]))
    within = [('ANS_rule_as_programmed', 'ANS', rule(exp_as_programmed), 8),
              ('ANS_eight_point_rule', 'ANS',
               rule(lambda img, x: x.exp()), 16)]
    return dict(module='StretchP413Tb', halt=2 * (main + 5) + 1,
                dump=('MAIN', 'TEMP'), exact=exact, within=within,
                steps=4000000)


def p4_10(sym):
    """LNX, printed pp.44-45.  The argument is XARG, one per run."""
    def parts(img, q, fln2, consts):
        x = img('XARG')
        e = 0
        f = x
        while f >= 1:
            f /= 2
            e += 1
        while f < D('0.5'):
            f *= 2
            e -= 1
        z = (f - q) / (f + q)
        acc = D(0)
        for c in consts:                  # CONST order: 1/17 first
            acc = acc * z * z + c
        return x, e, f, z, 2 * z * acc, (2 * e - 1) * fln2 / D(2) ** 48

    def prog(img):
        consts = [img('CONST+%d' % i) for i in range(9)]
        return parts(img, img('Q'), img('FLN2'), consts)

    def page(img):
        # the page's constants exactly, Q as PRINTED (1/1.41421356205080)
        consts = [D(1) / (2 * k + 1) for k in range(8, -1, -1)]
        return parts(img, 1 / D('1.41421356205080'),
                     D(2).ln() * D(2) ** 47, consts)

    def scale(img):
        _, _, _, _, t2, t1 = prog(img)
        return max(abs(t1), abs(t2))

    exact = [('TEMP_is_x', 'TEMP', None),
             ('x1_value7_count0', 'addrIndex(1)', (7 << 46) | (sym['XW1'] // 64))]
    within = [('TEMP1_Z', 'TEMP+1', lambda img: prog(img)[3], 4,
               lambda img: abs(prog(img)[3])),
              ('TEMP2_ln_F_over_q', 'TEMP+2', lambda img: prog(img)[4], 4, scale),
              ('ACC_as_programmed', 'ACC',
               lambda img: prog(img)[4] + prog(img)[5], 4, scale),
              ('ACC_page_as_printed', 'ACC',
               lambda img: page(img)[4] + page(img)[5], 16, scale)]
    return dict(module='StretchP410Tb', halt='HALT', dump=(8, 'XARG'),
                exact=exact, within=within,
                report=lambda img, got: "ACC - ln x = %.4E (the misprinted "
                "sqrt2 predicts -2.279E-10)" % (got - img('XARG').ln()))


def _frac_exp(v):
    """(f, e) with v = f 2**e, 1/2 <= |f| < 1; f carries the sign."""
    e = 0
    f = abs(v)
    while f >= 1:
        f /= 2
        e += 1
    while f < D('0.5'):
        f *= 2
        e -= 1
    return (f if v >= 0 else -f), e


def p4_9m1(sym, fp_store=False):
    """COSF, printed p.43.  The argument is XARG, one per run.  fp_store:
    the last card as "SRDN(N),$L" (PROBLEMS '4.9m1fp')."""
    def a_of(img):
        return img('XARG') * img('TPI')        # exact: two 48-bit fractions

    def trunc48(v):
        f, e = _frac_exp(v)
        return D(int(f * 2 ** 48)) / D(2) ** 48 * D(2) ** e

    def y_full(img):
        a = a_of(img)
        return a * trunc48(a)

    def round48(v):
        # STORE ROUNDED: one added at fraction bit 49, then truncated (p.96)
        f, e = _frac_exp(v)
        m = int(abs(f) * 2 ** 49) + 1
        r = D(m >> 1) / D(2) ** 48 * D(2) ** e
        return r if v >= 0 else -r

    def as_programmed(img):
        yt = round48(y_full(img))
        acc = y_full(img)
        for i in range(7):
            acc = (1 - acc * img('CONST+%d' % i)) * yt
        return 1 - acc / 2

    def bug_bit(img):
        f, _ = _frac_exp(a_of(img))
        return int(abs(f) * 2 ** 49) & 1

    exact = [('x2_value7_count0', 'addrIndex(2)', (7 << 46) | (sym['XW2'] // 64))]
    # AS STRAP ASSEMBLES THE PRINTED CARD (settled 2026-11-16, the deck's
    # header and tests/check_srdn_dollar_l.py): "SRDN,$L" is the VFL STORE
    # ROUNDED, (BU,64,8) at offset 0, which "is equivalent to a STORE"
    # (Reference Manual printed p.64).  An unsigned 64-bit field at offset 0
    # is accumulator bits 64-127, word 9, and "The contents of the
    # accumulator ... are not changed by this operation", so at the halt
    # word 8 equals word 9 exactly.  cos 2 pi x is not left anywhere: the
    # book's COSF is wrong in the ink.  The cosine checks are '4.9m1fp',
    # the card with the floating-point dds written in.
    within = [('TEMP_A_squared', 'TEMP', lambda img: round48(y_full(img)), 4)]
    same = [('W8_is_W9_vfl_srd_offset0_is_a_store', 8, 9)]
    if fp_store:
        # "SRDN(N),$L": the floating-point SRD into location 8, Reference
        # Manual printed p.80 -- the rounded word's bits 0-59 go to
        # accumulator 0-59 and its bits 60-63 (sign, as changed by the N
        # modifier, and flags; p.96) to $SB bits 4-7.  So the answer is
        # read as the accumulator, words 8 and 10, and $SB 4-7 must be
        # 0000: -cos negated is plus, and the flags are off.
        within += [('ACC_series_as_programmed', 'ACC', as_programmed, 4),
                   ('ACC_cos_2_pi_x', 'ACC', lambda img: (2 * PI * img('XARG')).cos()
                    if hasattr(D, 'cos') else _cos(2 * PI * img('XARG')), 8)]
        same = []
    return dict(module='StretchP49M1Tb', halt='HALT', dump=(8, 'XARG'),
                exact=exact, within=within, same=same,
                bits=[('SB_4_7_plus_no_flags', 10, 56, 4, 0)] if fp_store else [],
                # (the location-8 operand bug this predicted is fixed;
                # kept as a record of the hand prediction)
                pre=lambda img: "HAND PREDICTION: A = 2 pi x is %s, word 8 "
                "bit 60 after *(N) = fraction bit 49 of A = %d, so the "
                "location-8 bug %s" % (
                    "negative" if a_of(img) < 0 else "positive", bug_bit(img),
                    "BITES (y = -A**2)" if bug_bit(img) != (a_of(img) < 0)
                    else "does not bite"))


def _cos(v):
    """cos by its series, sixty digits; |v| < 1."""
    term = D(1)
    tot = D(1)
    for k in range(1, 40):
        term *= -v * v / ((2 * k - 1) * (2 * k))
        tot += term
    return tot


PROBLEMS = {'4.9m1': ('problem_4_9_method1.strap', p4_9m1),
            '4.9m1fp': ('problem_4_9_method1.strap',
                        lambda sym: p4_9m1(sym, fp_store=True)),
            '4.10': ('problem_4_10.strap', p4_10),
            '4.11': ('problem_4_11.strap', p4_11),
            '4.13': ('problem_4_13.strap', p4_13),
            '4.12': ('problem_4_12.strap', p4_12)}


def main():
    args = sys.argv[1:]
    subs = []
    known_wrong = set()
    if '--known-wrong' in args:
        i = args.index('--known-wrong')
        known_wrong = set(args[i + 1].split(','))
        del args[i:i + 2]
    while '--sub' in args:
        i = args.index('--sub')
        subs.append((args[i + 1], args[i + 2]))
        del args[i:i + 3]
    xarg = None
    if len(args) == 1 and ':' in args[0]:
        args[0], xarg = args[0].split(':', 1)
    if len(args) != 1 or args[0] not in PROBLEMS:
        raise SystemExit("usage: verify_problem_4_fp.py %s [--sub OLD NEW]..."
                         % '|'.join(sorted(PROBLEMS)))
    from strap_asm import assemble
    deck_name, spec_fn = PROBLEMS[args[0]]
    with open(os.path.join(HERE, '..', 'decks', deck_name)) as f:
        src = f.read()
    if xarg is not None:
        m = re.search(r"^XARG    DD\(N\), .*$", src, re.M)
        subs.insert(0, (m.group(0), "XARG    DD(N), " + xarg))
    if args[0] == '4.9m1fp':
        # the floating-point dds written into the printed "SRDN,$L"
        subs.append(("        SRDN,$L\n", "        SRDN(N),$L\n"))
    for old, new in subs:
        if src.count(old) != 1:
            raise SystemExit("--sub: %r occurs %d times, need exactly 1"
                             % (old, src.count(old)))
        src = src.replace(old, new)
        print("INJECTED: %r -> %r" % (old, new))
    prog = assemble(src)
    sym = prog.symtab
    spec = spec_fn(sym, src) if args[0] == '4.13' else spec_fn(sym)

    def word_of(s):
        if isinstance(s, int):
            return s
        if '+' in s:                      # SYMBOL+words
            base, off = s.split('+')
            return sym[base] // 64 + int(off)
        return sym[s] // 64

    def img(s):
        return fp_value(prog.words[word_of(s)])

    if 'pre' in spec:
        print(spec['pre'](img))
    first, last = word_of(spec['dump'][0]), word_of(spec['dump'][1])
    halt = spec['halt']
    checks = ["PC=%d" % (halt if isinstance(halt, int) else sym[halt] // 32),
              "DUMP=%d,%d" % (first, last - first + 1),
              "STEPS=%d" % spec.get('steps', 2000000)]
    for label, where, word in spec['exact']:
        if word is None:
            word = prog.words[sym['XARG'] // 64]
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
    failed_within = set()
    for entry in spec['within']:
        label, where, fn, bound = entry[:4]
        scale = entry[4] if len(entry) > 4 else None
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
        u = units(got, want) if scale is None else (
            abs(got - want) / _unit_of(scale(img)))
        if callable(bound):
            bound = bound(img)
        ok = u <= bound
        print("%s %s = %016x = %.17E, want %.17E, off %.2f units (bound %.0f)"
              % ("PASS" if ok else "FAIL", label, dump[a], got, want, u, bound))
        if not ok:
            failed_within.add(label)
            if label not in known_wrong:
                fails += 1
        if where == 'ACC' and 'report' in spec:
            print("NOTE " + spec['report'](img, got))
    for label, a, b in spec.get('same', []):
        # two dumped words equal, bit for bit
        n_within += 1
        if a not in dump or b not in dump:
            print("FAIL %s: word %d or %d is not in the dump" % (label, a, b))
            fails += 1
            continue
        ok = dump[a] == dump[b]
        print("%s %s: word %d = %016x, word %d = %016x"
              % ("PASS" if ok else "FAIL", label, a, dump[a], b, dump[b]))
        if not ok:
            failed_within.add(label)
            if label not in known_wrong:
                fails += 1
    for label, a, lsb, width, want in spec.get('bits', []):
        # a field of a dumped word, compared exactly; lsb counts from the
        # right (IBM bits 4-7 of word 10 are lsb 56, width 4)
        n_within += 1
        if a not in dump:
            print("FAIL %s: word %d is not in the dump" % (label, a))
            fails += 1
            continue
        got = (dump[a] >> lsb) & ((1 << width) - 1)
        ok = got == want
        print("%s %s = %X, want %X" % ("PASS" if ok else "FAIL", label, got, want))
        if not ok:
            failed_within.add(label)
            if label not in known_wrong:
                fails += 1
    for label, a, want4 in spec.get('low4', []):
        # the stored word's bits 60-63, sign and flags, compared exactly
        n_within += 1
        if a not in dump:
            print("FAIL %s: word %d is not in the dump" % (label, a))
            fails += 1
            continue
        got4 = dump[a] & 0xF
        ok = got4 == want4
        print("%s %s = %X, want %X" % ("PASS" if ok else "FAIL", label, got4, want4))
        if not ok:
            failed_within.add(label)
            if label not in known_wrong:
                fails += 1
    print("verify_problem_4_fp %s: %d exact checks and the PC through gen_tb, "
          "%d within-bound checks, %d dumped words read"
          % (args[0], len(spec['exact']), n_within, len(dump)))
    if len(dump) != last - first + 1:
        print("FAIL the dump is short: %d of %d words" % (len(dump), last - first + 1))
        fails += 1
    if known_wrong:
        # KNOWN WRONG: a model finding, registered so the suite stays green
        # while the finding is open.  The run passes only if EXACTLY these
        # within-bound checks fail; one that starts passing is a failure
        # too, so a fix cannot go unnoticed.
        if failed_within == known_wrong:
            print("KNOWN WRONG, as documented: %s" % ','.join(sorted(known_wrong)))
        else:
            print("FAIL known-wrong set changed: documented %s, failed now %s"
                  % (sorted(known_wrong), sorted(failed_within)))
            fails += 1
    print("ALL CHECKS PASSED" if not fails else "FAILED")
    return 1 if fails else 0


if __name__ == '__main__':
    sys.exit(main())
