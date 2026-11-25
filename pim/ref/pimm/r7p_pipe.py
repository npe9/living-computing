#!/usr/bin/env python3
"""R7P on the reference: why the primer's pipe fails on the held PIMOS,
and that one atom of ICOT's code is the whole cause.

    python3 ref/pimm/r7p_pipe.py PROMPT.pkl

PROMPT.pkl is the machine saved at the shell's prompt (bsv/README.md,
"The lockstep from a saved machine").  The line typed is the primer's
pipe as printed (primer25.tex:1879):

    grep(":-") <= file("sample1.kl1") | lc

Two runs from the checkpoint, each in a process of its own (fork):

1. As held.  The job has `<=` and no `=>`, so the shell asks for its
   `in` only (shell/main/job.kl1:66-68); task_stdio gives it the
   inherited `out_inter` (kernel/stdio/std.kl1:20-23, 51-54, 96-99) and
   its switch is task_std_handler:in_outInter.  The last stage, lc,
   asks only for `in` (shell/main/tos.kl1:80), so it inherits
   `out_inter` from the job: make_branch(out_inter).  in_outInter
   answers that with `out(...)` (kernel/stdio/stdhdl.kl1:299-305), and
   lc's vector becomes {in, out, *}, for which
   task_stdio:invoke_std_handler/3 has no clause (std.kl1:281-296): a
   reduction failure.  Checked here: the goal of invoke_std_handler/3
   that fails has the vector {in(..), out(..), *}; the window gets
   nothing.
2. Patched.  The one cell of the linked binary that writes that `out`
   (task_std_handler's code, the clause for out_inter of in_outInter:
   `write_atom out`; the switch_on_constant arm for out_inter leads to
   it, and the in_out_inter arm after it writes out_inter) changed to
   `write_atom out_inter`, in memory, on the reference only.  The
   pipe then runs: `$$$ Line = 5 $$$`, the lines of the primer's
   sample1.kl1 (primer25.tex:592-605) that hold ":-".

So the failure is in the held PIMOS 3.6 (source and binary agree), not
in either model.  The patch is a change to ICOT's code, made to show
the cause; it is NOT the models' behaviour and is not used anywhere
else.  The same line on both models as held: APPS `pipe_primer`
(lockstep_shell.py); the same pipe in the manual's `<= .. | .. =>`
form, which the held code serves: APPS `pipe_grep`.

Ends `r7p pipe: PASS` when both runs are as described.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', '..', 'asm'))
import lockstep_shell as ls  # noqa: E402
import longrun_ipl as lr  # noqa: E402
import pimm  # noqa: E402

LINE = 'grep(":-") <= file("sample1.kl1") | lc'
WRITE_ATOM = 0x23           # the opcode byte of write_atom (asm/kbndis.py)


class Count:
    """The trace, counted, not kept."""
    def __init__(self):
        self.lines = 0
        self.instructions = 0

    def append(self, line):
        self.lines += 1
        if line[0] == 'I':
            self.instructions += 1


def names(m, loaded):
    """{atom number: name}, {module address: name} from Loaded,
    normal(Atoms, Modules, ..) (longrun_ipl.check reads it so)."""
    b = m.vbase(m.deref(loaded))
    el = [m.deref(m.mem[b + i]) for i in range(5)]
    aname = {}
    for n, a in m.term(el[1]):
        if isinstance(a, str) and a.startswith('#') and isinstance(n, tuple):
            aname[int(a[1:], 16)] = lr.text_of(n[1])
    mods = {}
    w = el[2]
    while w[0] & ~1 == pimm.LIST:
        r = m.deref(m.mem[w[1]])
        na = m.deref(m.mem[m.vbase(r)])
        mods[m.deref(m.mem[m.vbase(r) + 1])[1]] = aname.get(na[1])
        w = m.deref(m.mem[w[1] + 1])
    return aname, mods


def predicates(m, mod):
    """{code address: (name atom, arity)} of every predicate head in the
    module object at mod ({PREDH, arity << 24 | offset} two cells before
    the code, the name atom two before that: pimm.py i_code_to_predicate)"""
    out = {}
    n = m.mem[mod][1] & 0xffffff
    for k in range(1, n + 1):
        if m.mem[mod + k][0] == pimm.PREDH:
            out[mod + k + 2] = (m.mem[mod + k - 2][1], m.mem[mod + k][1] >> 24)
    return out


def the_cell(m, aname, mods):
    """The address of the `write_atom out` of in_outInter's clause for
    make_branch(out_inter): in task_std_handler, the switch_on_constant
    whose table has out_inter and in_out_inter (its 7 arms: in, out,
    inter, in_out, in_inter, out_inter, in_out_inter), the arm for
    out_inter followed to its clause, the clause's first write_atom"""
    atom = {v: k for k, v in aname.items()}
    mod = [a for a, n in mods.items() if n == 'task_std_handler']
    assert len(mod) == 1, mod
    mod = mod[0]
    preds = predicates(m, mod)
    entry = [c for c, (na, ar) in preds.items() if aname.get(na) == 'in_outInter' and ar == 8]
    assert len(entry) == 1, entry
    n = m.mem[mod][1] & 0xffffff
    later = [c for c in preds if c > entry[0]]
    end = min(later) - 4 if later else mod + n + 1      # the next predicate's name cell
    hits = []
    for a in range(entry[0], end):
        t, v = m.mem[a]
        if t == 0x23 and v >> 24 == 0x2c and v & 0xffff == 7:     # switch_on_constant _,_,7
            table = [m.mem[a + 1 + 2 * k] for k in range(7)]
            if [aname.get(x[1]) for x in table] == ['in', 'out', 'inter', 'in_out', 'in_inter',
                                                    'out_inter', 'in_out_inter']:
                arm = a + 1 + 2 * 5
                hits.append(arm + 2 + (m.mem[arm + 1][1] & 0xffff))
    assert len(hits) == 1, hits
    for a in range(hits[0], hits[0] + 40):
        t, v = m.mem[a]
        if t == 0x23 and v >> 24 == WRITE_ATOM:
            assert v & 0xffffff == atom['out'], hex(v)
            return a, (t, v), atom['out_inter']
    raise AssertionError('no write_atom in the out_inter clause')


def run(m, loaded, kind, patch):
    aname, mods = names(m, loaded)
    a, (t, v), oi = the_cell(m, aname, mods)
    if patch:
        dict.__setitem__(m.mem, a, (t, v & ~0xffffff | oi))
    failures = []
    isusp = m.i_suspend

    def watch(pc, x, y, z, c16):
        if not m.waiting and m.shoen:
            c = m.load + pc + 2 + pimm.sx16(c16)
            head = m.mem[c - 2]
            mo = c - 2 - (head[1] & 0xffffff)
            vec = m.deref(m.reg[0])
            kinds = None
            if m.vsize(vec) == 3:
                kinds = []
                for i in range(3):
                    e = m.deref(m.mem[m.vbase(vec) + i])
                    if m.vsize(e):          # kind(Cont, FCode, SShut): {kind, ..}
                        e = m.deref(m.mem[m.vbase(e)])
                    kinds.append(aname.get(e[1], '?'))
            failures.append(('%s:%s/%d' % (mods.get(mo), aname.get(m.mem[c - 4][1]), head[1] >> 24),
                             kinds))
        return isusp(pc, x, y, z, c16)
    m.i_suspend = watch
    sink = Count()
    _ops, _events, stop, dev = ls.play(m, loaded, kind, [LINE], sink)
    window = [t for _d, t in dev.log][4:]       # after the login's and the prompt's
    return dict(cell=a, failures=failures, window=window, stop=stop,
                instructions=sink.instructions, lines=sink.lines)


def main(argv):
    m, loaded, _info, kind = ls.load(argv[1])
    assert kind == 'prompt'
    m.ahead = False
    got = {}
    for patch in (False, True):
        r, w = os.pipe()
        pid = os.fork()
        if pid == 0:
            os.close(r)
            try:
                out = run(m, loaded, kind, patch)
            except BaseException as e:      # noqa: B902 -- reported by the parent
                out = dict(error=repr(e))
            os.write(w, repr(out).encode())
            os._exit(0)
        os.close(w)
        data = b''
        while True:
            chunk = os.read(r, 1 << 16)
            if not chunk:
                break
            data += chunk
        os.waitpid(pid, 0)
        got[patch] = eval(data.decode())                # our own repr
        print('%s: %r' % ('patched' if patch else 'as held', got[patch]))
    held, patched = got[False], got[True]
    ok = (held['failures'] == [('task_stdio:invoke_std_handler/3', ['in', 'out', '*'])]
          and held['window'] == []
          and patched['failures'] == []
          and patched['window'] == ['$$$ Line = 5 $$$\n', 'Shell>> '])
    if not ok:
        print('r7p pipe: FAIL')
        return 1
    print('r7p pipe: PASS (as held, the primer\'s pipe fails at invoke_std_handler/3 with '
          '{in, out, *}, nothing written; with in_outInter\'s answer to make_branch(out_inter) '
          'changed from out to out_inter, cell %x, it writes $$$ Line = 5 $$$)' % held['cell'])
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
