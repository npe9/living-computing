#!/usr/bin/env python3
"""Step 3o (2026-11-26): the SIMPOS boot route's B8 top level, the
debugger as the ESP listener (docs/simpos/boot_route.md §4.9).  OURS.

    python3 -I psi/test_boot_route.py           the tests (~10 s)
    python3 -I psi/test_boot_route.py --png DIR  also write the screen
                                                 (DIR/debugger_dialogue.png)

The run is window M6/M7's (test_espc.py Window.later_run, psi/fep_bridge.py
PsiSide with no PIMOS): boot, login as pmpsi, the coordinator, the status
band; the user's events go on the coordinator's stream in batches, each at
the next quiet moment (window M1's event pump: {mouse, ...} and {key, Code}
events, the keys to the selected window's typed/2 and its getl/2).

  - test_step3o_dialogue: the right button opens the SYSTEM MENU and the
    left button on its first item, `debugger` (the HELD login.com's
    {"debugger", simpos##debugger}), starts the debugger stand-in
    (standin/debugger.esp) in a new process: the windows `debugger_1` and
    `Variable Window`.  TM-134 PDF p71's dialogue is typed, with the held
    pimfep##pimos_login_requester in place of the printed-in-part
    hypocycloid_drawer:
        :- :create(#pimfep##pimos_login_requester,Req).   > Success !!
        :- :create(#process,Proc).                        > Success !!
        :- :activate(Proc,Req).                           > Success !!
        :-
    The prompt comes back at once (TM-134: ":activate returns at once"),
    while the requester runs in Proc, a child of the debugger's process,
    and shows its window, which takes the keyboard.  The three answers
    typed then take it through the same dialogue as the menu path's
    (test_espc.py test_step3m_keyboard, the oracle): its prompts, the
    echoed name, no password echo, `Network error.`, two beeps.  The
    Variable Window shows `Req = $pimos_login_requester,` and
    `Proc = $process;`.
  - test_step3o_variables: a click back on the debugger's window selects
    it; `:create(#process,Proc).` fails (`> Fail !!`: Proc keeps its value
    from the earlier goal, and a new process is not it); a line that is
    not a goal is `> Syntax error !!` (OURS text); `:create(#process,P2).`
    succeeds and P2 joins the Variable Window.
  - test_step3o_subroutine_form: the subroutine form (TM-134 PDF p69,
    folio 65; shell.md §5.1 b', TM-786 p5) `:create(#pimfep##
    pimos_login_requester,R), :goal(R).` runs the requester in the
    DEBUGGER's process: no prompt comes back while it runs; it is the
    debugger's process that waits in the requester's read.
  - test_step3o_reader: psi/esp_reader.py read_goal on the printed goals,
    and login.com still reads as before.

Injections, OBSERVED (2026-11-26; each into a private copy of psi/, the
worktree untouched; this file, test_espc.py and test_kl0.py run;
test_espc.py and test_kl0.py stayed OK in all six):
  D1 debugger.esp bind/2 does not give a name its earlier value (every
     goal's variables fresh): test_step3o_dialogue and
     test_step3o_variables FAIL (the run is refused at the third goal's
     activate/2, sent to an unbound receiver); nothing else.
  D2 debugger.esp: a send of activate/2 runs the object's goal/1 in the
     debugger's own process (the subroutine form in place of the process
     form): test_step3o_dialogue and test_step3o_variables FAIL; nothing
     else.
  D3 kl0.py debugger_variable_lines: `;` after every binding:
     test_step3o_dialogue and test_step3o_variables FAIL; nothing else.
  D4 esp_reader.py: a method call's arguments read in reverse (the
     receiver last): test_step3o_reader, _dialogue, _variables and
     _subroutine_form FAIL; nothing else (login.com has no method call).
  D5 debugger.esp: a failed goal answered `> Success !!`:
     test_step3o_variables FAIL only.
  T1 alarm_watch.esp: on_at/2 fails: test_step3o_timer_alarms FAIL only
     (the census does not reach on_at/2: test_espc.py's census pins OK).
"""
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import kl0 as K  # noqa: E402
import test_espc as T  # noqa: E402

DEBUGGER_ITEM_AT = (700, 589)   # the SYSTEM MENU at fep_bridge.MENU_AT: column 1, row 1
DEBUGGER_WINDOW_AT = (900, 150)  # inside debugger_1 (standin/debugger.esp places it)
TEXT_AT = (723, 60)             # debugger_1's first text cell
VARIABLES_AT = (723, 320)       # the Variable Window's
C = K.ClassRef('simpos##coordinator')
SCREEN_SHA = '70c7df826ab1df7d7222b435d3019e0e33edf0b69c3ed8d7fca904d8da7106fc'

DIALOGUE = [':create(#pimfep##pimos_login_requester,Req).', ':create(#process,Proc).',
            ':activate(Proc,Req).']
# test_espc.py test_step3m_keyboard's dialogue, the menu path's
REQUESTER = [('put', 'Enter FEP node name--------->'), ('typed', 'local'),
             ('put', 'Enter your PIMOS user name-->'), ('typed', 'pimos'),
             ('put', 'Enter your PIMOS password--->'), ('put', 'Network error.'),
             ('event', K.Atom('beep')), ('event', K.Atom('beep'))]


def walk(t):
    return T.Standins._walk(t)


def history(m, w):
    """W's history as ('put', text), ('typed', text), ('event', e)."""
    out, typed = [], []
    for e in reversed(walk(m.get_slot(w, 'history'))):
        if isinstance(e, K.Str):
            out.append(('put', e.text))
        elif isinstance(e, int) and e == 13:
            t = K.Str('')
            t.set_codes(typed)
            out.append(('typed', t.text))
            typed = []
        elif isinstance(e, int):
            typed.append(e)
        else:
            out.append(('event', e))
    return out


def asked(goal, answer):
    return [('put', ':- '), ('typed', goal), ('put', answer), ('put', '')]


class Step3o(unittest.TestCase):
    later_run = T.Window.later_run
    keys = staticmethod(T.Standins.keys)

    def debugger_run(self, *batches):
        """Open the menu, choose `debugger`, then BATCHES (each a list of
        events, given at the next quiet moment).  -> (machine, frame,
        stop, the debugger, its process, {title: window})"""
        import fep_bridge as FB
        L = FB.mouse
        m, fr, stop = self.later_run([L('rr', *FB.MENU_AT), L('l', *DEBUGGER_ITEM_AT)], *batches)
        progs = [(K.deref(n), K.deref(p)) for n, p in (walk(x) for x in walk(m.get_slot(C, 'programs')))]
        (dp,) = [p for n, p in progs if n == K.Atom('simpos##debugger')]
        top = K.deref(K.resolve(m.get_slot(m.get_slot(dp, 'invocation_stack'), 'elements')).args[0])
        self.assertEqual(top.cid, 'simpos##debugger')
        ws = {m.get_slot(w, 'title').text: w for w in walk(m.get_slot(C, 'windows'))}
        return m, fr, stop, top, dp, ws

    def variables(self, m, d):
        return [(K.deref(n).name, K.deref(v)) for n, v in (walk(x) for x in walk(m.get_slot(d, 'variables')))]

    def test_step3o_dialogue(self):
        import windev
        m, fr, stop, d, dp, ws = self.debugger_run(*[self.keys(g) for g in DIALOGUE],
                                                   self.keys('local'), self.keys('pimos'), self.keys('secret'))
        self.assertEqual(stop.cause, 'would suspend')
        self.assertIn('no process is ready', stop.detail)
        (req_title,) = [t for t in ws if t.startswith('Pimos remote login ')]
        self.assertEqual(sorted(ws), sorted(['debugger_1', 'Variable Window', req_title]))
        w, v, rw = ws['debugger_1'], ws['Variable Window'], ws[req_title]
        # the debugger: three goals, three successes, the prompt again at
        # once (before the requester's dialogue, which went to its window)
        self.assertEqual(history(m, w), sum((asked(g, '> Success !!') for g in DIALOGUE), [])
                         + [('put', ':- ')])
        self.assertEqual(windev.read_cells(fr, TEXT_AT[0], TEXT_AT[1], 44, 10)[:9],
                         [':- :create(#pimfep##pimos_login_requester,Re', 'q).', '> Success !!', '',
                          ':- :create(#process,Proc).', '> Success !!', '', ':- :activate(Proc,Req).',
                          '> Success !!'])
        self.assertEqual([t.text for t in reversed(walk(m.get_slot(v, 'transcript')))],
                         ['Req = $pimos_login_requester,', 'Proc = $process;'])
        self.assertEqual(windev.read_cells(fr, VARIABLES_AT[0], VARIABLES_AT[1], 44, 2),
                         ['Req = $pimos_login_requester,', 'Proc = $process;'])
        # Req and Proc: the requester and the process running it, a child
        # of the debugger's process, which itself is the coordinator's child
        vs = dict(self.variables(m, d))
        req, proc = vs['Req'], vs['Proc']
        self.assertEqual(req.cid, 'pimfep##pimos_login_requester')
        self.assertEqual(proc.cid, 'simpos##process')
        self.assertIsNot(proc, dp)
        self.assertIs(m.get_slot(proc, 'parent_process'), dp)
        self.assertIs(m.get_slot(dp, 'parent_process'), m.get_slot(C, 'process'))
        top = K.deref(K.resolve(m.get_slot(m.get_slot(proc, 'invocation_stack'), 'elements')).args[0])
        self.assertIs(top, req)
        self.assertIs(m.get_slot(req, 'window'), rw)
        # the requester's dialogue is the menu path's (test_step3m_keyboard)
        self.assertEqual(history(m, rw), REQUESTER)
        self.assertEqual(m.get_slot(req, 'password_counter'), 7)
        self.assertIs(m.get_slot(C, 'selected'), rw)
        # both wait: the requester for a key, the debugger in its getl/2
        self.assertEqual(m.get_slot(proc, 'status'), K.Atom('suspended'))
        self.assertEqual(m.get_slot(dp, 'status'), K.Atom('suspended'))
        # the whole frame (docs/simpos/screens/debugger_dialogue.png, written
        # by --png from this run)
        self.assertEqual(windev.pbm_sha256(fr), SCREEN_SHA)

    def test_step3o_variables(self):
        import fep_bridge as FB
        m, fr, stop, d, dp, ws = self.debugger_run(
            *[self.keys(g) for g in DIALOGUE],
            [FB.mouse('l', *DEBUGGER_WINDOW_AT)] + self.keys(':create(#process,Proc).', 'create a process.',
                                                             ':create(#process,P2).'))
        self.assertEqual(stop.cause, 'would suspend')
        w, v = ws['debugger_1'], ws['Variable Window']
        self.assertIs(m.get_slot(C, 'selected'), w)
        self.assertEqual(history(m, w)[-13:],
                         asked(':create(#process,Proc).', '> Fail !!')
                         + asked('create a process.', '> Syntax error !!')
                         + asked(':create(#process,P2).', '> Success !!') + [('put', ':- ')])
        vs = self.variables(m, d)
        self.assertEqual([n for n, _ in vs], ['Req', 'Proc', 'P2'])
        self.assertEqual(vs[2][1].cid, 'simpos##process')
        self.assertIsNot(vs[2][1], vs[1][1])
        self.assertIs(m.get_slot(vs[2][1], 'parent_process'), dp)
        self.assertEqual([t.text for t in reversed(walk(m.get_slot(v, 'transcript')))],
                         ['Req = $pimos_login_requester,', 'Proc = $process,', 'P2 = $process;'])

    def test_step3o_subroutine_form(self):
        m, fr, stop, d, dp, ws = self.debugger_run(
            self.keys(':create(#pimfep##pimos_login_requester,R), :goal(R).'), self.keys('local'))
        self.assertEqual(stop.cause, 'would suspend')
        (req_title,) = [t for t in ws if t.startswith('Pimos remote login ')]
        rw = ws[req_title]
        # no answer and no prompt: the debugger runs the requester itself
        self.assertEqual(history(m, ws['debugger_1']),
                         [('put', ':- '), ('typed', ':create(#pimfep##pimos_login_requester,R), :goal(R).')])
        self.assertEqual(history(m, rw), REQUESTER[:3])
        top = K.deref(K.resolve(m.get_slot(m.get_slot(dp, 'invocation_stack'), 'elements')).args[0])
        self.assertIs(top, d)
        self.assertEqual(m.get_slot(dp, 'status'), K.Atom('suspended'))
        self.assertEqual(self.variables(m, d), [])

    def test_step3o_reader(self):
        import esp_reader as R
        t, names = R.read_goal(K, ':create(#hypocycloid_drawer,300,Cyc).')
        self.assertEqual(repr(t), '{:,{create,{#,hypocycloid_drawer},300,%r}}' % names[0][1])
        self.assertEqual([n for n, _ in names], ['Cyc'])
        t, names = R.read_goal(K, ':create(#simshow##simshow,S), :goal(S).')
        self.assertEqual([n for n, _ in names], ['S'])
        self.assertEqual(K.deref(t.args[0]), K.Atom(','))
        self.assertIs(K.deref(K.deref(t.args[2]).args[1]).args[1], names[0][1])
        for bad in ('create(#process,P)', ':create.', ':create(#process,P). :x(A).', '#.'):
            with self.assertRaises(ValueError):
                R.read_goal(K, bad)
        # the login file's terms are unchanged (test_espc.py
        # test_step3l_b6_b8 reads it whole)
        terms = R.read_terms(K, '"me" := [ "user:pmpsi" ] , x :- y . p :- q##r .')
        self.assertEqual(repr(terms[1]), '{:-,p,q##r}')


class Step3oTimer(unittest.TestCase):
    """Step 3o, open item 2 of boot_route.md §5 (B4 for the FEP timer): the
    alarms 303 on_after and 302 on_at round-trip through the held
    pimos_timer in its device process (test_espc.py test_step3k_b4's probe,
    b4_run).  The held local on_after/4 @10c-131 and on_at/4 @136-
    (fepread/ptfread.py, 2026-11-26) make an alarm_watch and a time,
    set_count/2, on_after/2 or on_at/2, wait/1, inhibit_forced_event/1, and
    reply {1, 9} by reply_message/2 (@12b-131: `pmi 47 00 00 01`, `47 00
    00 09`): the alarm `{Id, 1, 9}`, 9 = wake_up, which is what PIMOS's
    waiter reads (docs/fep_services.md §2.4, time_dvc.kl1:254-257).  No
    clock is modelled (standin/alarm_watch.esp: wait/1 returns at once), so
    the alarm comes at once; on_at/2 is stood in by step 3o (until then 302
    refused at simpos##alarm_watch:on_at/2, not in the stand-in)."""

    @classmethod
    def setUpClass(cls):
        import espc
        cls.ts = espc.standins()

    B4_PROBES = T.Standins.B4_PROBES

    def alarm_run(self, code, count):
        """test_espc.py Standins.b4_run with the request's argument: the
        Count after a length word -1, as PIMOS sends it (§2.4)."""
        import espc
        ts, failed = espc.compile_text(self.B4_PROBES, 'simpos')
        self.assertFalse(failed)
        lib = K.load_six()
        for t in list(self.ts) + ts:
            lib.add(t)
        m = K.Machine(lib, max_steps=400000)
        (prog,) = K.call_class_method(m, 'simpos##b4_boot', 'create', [K.Var()])[0]
        m.class_slots, m.saved = {}, {}
        req = K.Str('', 32)
        req.set_codes([16, 0, code, 1, 0xffffffff, count])
        m.set_slot(prog, 'req', req)
        m.reset()
        self.assertTrue(any(True for _ in m.solve_send(prog, 'invoke', [prog])))
        return m, {e.name.split('$')[-1]: K.deref(v)
                   for e, v in zip(m.lib.build(prog.cid).instance_slots, prog.slots)}

    def test_step3o_timer_alarms(self):
        for code in (303, 302):
            m, s = self.alarm_run(code, 5000)
            # the creation reply (the probe's first get), then the alarm
            self.assertEqual(s['r1'].codes(), [16, 0, 1, 0], code)
            self.assertEqual(s['r2'].codes(), [16, 0, 1, 1, 0xffffffff, 9], code)
            # the device process waits in see/2 again
            ((dp, _regs),) = m.saved.values()
            self.assertEqual(m.get_slot(dp, 'status'), K.Atom('suspended'), code)


def write_png(out):
    t = Step3o()
    m, fr, stop, d, dp, ws = t.debugger_run(*[t.keys(g) for g in DIALOGUE],
                                            t.keys('local'), t.keys('pimos'), t.keys('secret'))
    import windev
    path = os.path.join(out, 'debugger_dialogue.png')
    with open(path, 'wb') as f:
        f.write(windev.png_bytes(fr))
    print(path, windev.pbm_sha256(fr))


if __name__ == '__main__':
    if len(sys.argv) == 3 and sys.argv[1] == '--png':
        write_png(sys.argv[2])
    else:
        unittest.main()
