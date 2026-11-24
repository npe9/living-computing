"""Run held predicates under kl0 with every SIMPOS send STUBBED (recorded, then
succeeds binding nothing). Read-only use of psi/kl0.py; nothing is written to the repo."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ptf_load as load
import kl0
from kl0 import Machine, Refusal, ClassRef, Instance, Var, Atom, Barrier, deref, resolve, StepLimit
L = load.lib()
kl0._RECORDS.update(load.records())

EXTRA = os.environ.get('PTF_EXTRA', '1') == '1'

class Stub(Machine):
    # OURS, not in kl0_opcodes.tsv: pmi b7 = put_vector_n (A, _, n), witnessed
    # by paragraph##type_switch_rs_icon draw_box/5 @6e `b7 00 00 07` against
    # p_icon.esp:70 `{draw_line,{X,Y+1,X+W-1,Y+1,2,solid,reset}}` (7 elements);
    # pmi b4 = put_vector_4: paragraph##what_manipulator_shell init_message/2
    # @121 `b4 00`, void + 3 unify_variable, against p_wshell.esp:112 `{Hid,Tag,Time,Pe}`.
    def __init__(self, *a, **k):
        Machine.__init__(self, *a, **k)
        self.log = []
        if EXTRA:
            self.handlers[('pmi', 'b4')] = self.op_put_vector_4
            self.handlers[('pmi', 'b7')] = self.op_put_vector_n
            # INFERENCE (series b2..b4): b5/b6 = put_vector_5/6
            self.handlers[('pmi', 'b5')] = lambda code, off, a, b, c, v: self._pv(a, 5, code, off)
            self.handlers[('pmi', 'b6')] = lambda code, off, a, b, c, v: self._pv(a, 6, code, off)
            # blt 40 = add A,B,^R: draw_box/5 @4d `40 05 03 01` then `46 01 01 0a`
            # against p_icon.esp:70 `X+W-1` (R may differ from A there).
            self.handlers[('blt', '40')] = self.op_add3
            self.handlers[('blt', '45')] = lambda code, off, a, b, c, v: self._ar(code, off, c, self.x[a], b, 1)
            self.handlers[('blt', '46')] = lambda code, off, a, b, c, v: self._ar(code, off, c, self.x[a], b, -1)
    def _ar(self, code, off, r, x, y, sgn):
        x, y = deref(x), deref(y)
        # OURS: arithmetic on an unknown (a stubbed SIMPOS result) gives a fresh variable
        self.x[r] = x + sgn * y if isinstance(x, int) and isinstance(y, int) else Var()
        self.nxt(code, off)
    def op_add3(self, code, off, a, b, c, v):
        self._ar(code, off, c, self.x[a], self.x[b], 1)
    def _pv(self, a, n, code, off):
        new = kl0.Vec([Var() for _ in range(n)])
        self.x[a] = new
        self.S = [new.args, 0]
        self.nxt(code, off)
    def op_put_vector_4(self, code, off, a, b, c, v):
        self._pv(a, 4, code, off)
    def op_put_vector_n(self, code, off, a, b, c, v):
        self._pv(a, c, code, off)
    def dispatch(self, recv, name, arity):
        r = deref(recv)
        try:
            return Machine.dispatch(self, recv, name, arity)
        except Refusal as e:
            if e.cause not in ('simpos', 'unbound receiver', 'no method', 'receiver not an object'):
                raise
            args = [resolve(self.x[i]) for i in range(arity - 1)]
            self.log.append((e.cause, r if not isinstance(r, Var) else '_', name, arity, args))
            self.proceed()

def show(t, d=0):
    t = deref(t)
    if d > 12: return '...'
    if isinstance(t, kl0.Cons):
        out = []
        while isinstance(t, kl0.Cons):
            out.append(show(t.args[0], d+1)); t = deref(t.args[1])
        return '[' + ','.join(out) + ('' if t is kl0.NIL else '|' + show(t, d+1)) + ']'
    if isinstance(t, kl0.Vec):
        a = t.args
        if a and isinstance(deref(a[0]), Atom):
            return show(a[0]) + '(' + ','.join(show(x, d+1) for x in a[1:]) + ')'
        return '{' + ','.join(show(x, d+1) for x in a) + '}'
    if isinstance(t, kl0.Str):
        return 'string#"%s"' % load.dejis(t.text)
    if isinstance(t, Instance):
        return '<inst %s>' % t.cid
    return load.dejis(repr(t))

def run(cid, label, nsol=1, max_steps=20000, args=None):
    """label like 'local create_menu/2' or 'class go/1' or 'instance draw/1'."""
    m = Stub(L, max_steps=max_steps)
    t = L.templates[cid]
    sec, sel = label.split()
    name, n = sel.rsplit('/', 1); n = int(n)
    res = dict(cid=cid, label=label, sols=0, err=None)
    try:
        if sec == 'local':
            p = [p for p in t.locals if p.name == name and p.arity == n][0]
            code = m.code(cid)
            regs = args or [Var() for _ in range(n)]
            g = m.solve((code, p.offset), regs + [Barrier(0)])
            # solve() resets; set barrier after first step: emulate enter_pred
            for _ in g:
                res['sols'] += 1
                res.setdefault('args', []).append([show(a) for a in regs])
                if res['sols'] >= nsol: break
        else:
            recv = ClassRef(cid) if sec == 'class' else kl0.make_instance(m, cid)
            regs = (args or [Var() for _ in range(n - 1)]) + [recv]
            for _ in m.solve_send(recv, name, regs):
                res['sols'] += 1
                res.setdefault('args', []).append([show(a) for a in regs[:-1]])
                if res['sols'] >= nsol: break
    except Refusal as e:
        res['err'] = 'REFUSED %s: %s' % (e.cause, e.detail)
    except StepLimit:
        res['err'] = 'step limit'
    except Exception as e:
        res['err'] = 'PYERR %r' % e
    res['sends'] = [(c, show(r) if not isinstance(r, str) else r, '%s/%d' % (nm, a), [show(x) for x in args]) for c, r, nm, a, args in m.log]
    return res

def report(res):
    print('### %s %s -> sols=%d %s' % (res['cid'], res['label'], res['sols'], res['err'] or ''))
    for a in res.get('args', []):
        print('   result args:', ', '.join(a))
    for c, r, sel, args in res['sends']:
        print('   SEND %s:%s(%s)%s' % (r, sel, ', '.join(args), '' if c == 'simpos' else '  [%s]' % c))

if __name__ == '__main__':
    cid = sys.argv[1]
    for lab in sys.argv[2:]:
        report(run(cid, lab))
