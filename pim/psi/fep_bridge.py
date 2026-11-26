#!/usr/bin/env python3
"""The bridge between PIMOS on the PIM/m reference model and the held
SIMPOS FEP on the PSI's KL0 interpreter (step 3n, 2026-11-25).  OURS.

    python3 psi/fep_bridge.py live PKL [--type LINE ...] [--record TAPE]
        PKL: a machine ref/pimm/longrun_ipl.py --reference --save wrote
        (the IPL's link, ~1.1 GB, not in git).  PIMOS runs from it on
        ref/pimm/pimm.py; the PSI side boots on psi/kl0.py; the bridge
        carries the login's and the console's FEP messages both ways.
        LINE: a line the user types into PIMOS's console window on the
        PSI (window M4; before it, fep.py's scripted getl answer).
        TAPE: every exchange written (psi/fep_bridge_tapes/, in git),
        replayed by `replay` without the PIM/m
    python3 psi/fep_bridge.py replay TAPE
        the PSI side alone, fed PIMOS's messages from TAPE, each
        exchange checked against what the live run's PSI side sent

The boundary.  The real PIM/m's FEP was a PSI running pimfep: PIMOS's
SCSI packets reached `pimfep##pimos_scsi_front_end` (HELD) through the
PSI's SCSI driver (pimscsi; its link to the bus is lost, and the
hardware is not modelled).  The bridge stands in for that driver and
the bus, and nothing else:

  - PIM/m side: `BridgeFep`, a subclass of ref/pimm/fep.py's Fep (read
    only; fep.py and pimm.py are not changed).  A device PIMOS makes by
    601 (create_string_io: the login replier and servers,
    simpos_user_device) is the PSI's: its creation and every later
    message to it are passed whole, as the packet PIMOS sent (device id,
    flag 0, then fep.py's pack_message body).  Since window M4
    (2026-11-25) so is a device PIMOS makes by 104 (create_window: the
    shell's console, PIMOS CONSOLE) and every later message to it (127,
    130, 132, 143, 70, 111, 112, 110): the PSI's held
    pimfep##pimos_window_process / pimos_window / pimos_window_editor
    answer them and draw the window (psi/standin/pmacs_window.esp).
    Everything else (the files of pimos:, the timer, 240, the directory)
    is still fep.py's.
  - PSI side: a front end made with the held class method create/6
    (type `pimscsi`, node "PSI", an input and an output stream) and run
    in a process of its own; the packets go on its input stream as
    32-bit strings (the elements the held fep_message_assembler reads:
    get_device_id/3 element 0, connection_flag/3 element 1,
    get_command/3 element 2, get_command testing the string's size 32,
    @14-44), by the idle interrupt (psi/kl0.py Machine.interrupt: when
    every PSI process waits).  What the held front end puts on its
    output stream (32-bit strings, fep_scsi_output's) is taken from the
    stream's post queue at the same moment and given to fep.py's
    RECEIVE queue as bytes, the words high byte first.
  - The order (OURS, deterministic): the PSI runs until every process
    waits; then its output goes to the PIM/m, the PIM/m runs until it
    has nothing to run (as longrun_ipl.go: run, scsi_poll, alarms),
    and the packets PIMOS sent for the PSI's devices since are put on
    the front end's input stream.  The run ends when neither side has
    anything for the other.
  - The user: the PSI's mouse and keyboard, coordinator events (window
    M6: the right button opens the system menu, the left button on
    "Login PIMOS" starts the requester; then {key, Code} for the
    requester's three answers, local / pimos / empty), put on the
    coordinator's event stream by the idle interrupt at the first
    exchange where PIMOS has nothing for the PSI (its login service has
    started: the server's held io(1) waits).  Queued at the boot, as in
    step 3m, they reach the requester before PIMOS's server exists and
    it writes "Network error.".  Window M4: the shell's lines (--type)
    are a second batch, the left button in the console and the keys,
    given at the first quiet exchange after PIMOS's console has had a
    110 (getl).  A tape from before M4 (login_pwd.json: no `shell`) has
    the lines fep.py's, as that run's window was.
  - Alarms: PIMOS's are fep.py's and longrun_ipl.go's (alarm_skip); no
    PSI timer is on this path, so kl0 has no clock.

What is OURS here and nowhere else: the routing by 601, the 32-bit
packing (the inverse of what the held assembler was measured to give,
psi/test_fep_bridge.py), the exchange order, the moment the user types,
the boot program b3n_boot, the node name "PSI" (fep.py's 240 Host).
Inferences the run rests on are listed in
docs/simpos/source_check_2026-11-24.md §13 (dated 2026-11-25).

A run (2026-11-25, live, s3_merger.pkl from the IPL's link): 30 s, 15.2
GB resident (the pickle's machine); PIMOS 8,626,676 instructions; 12
exchanges; the tape psi/fep_bridge_tapes/login_pwd.json (5 KB) replays
the PSI side alone in 2 s.  Window M4's run (2026-11-25, the same
checkpoint, 28 s, PIMOS 8,626,640 instructions): 26 exchanges, the
shell's line given at the 19th, the run ending as the second getl waits; psi/fep_bridge_tapes/console_pwd.json (8 KB) replays in
about 3 s; its result carries the final screen's PBM sha256 and dots.
"""
import json
import os
import struct
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', 'ref', 'pimm'))
sys.path.insert(0, os.path.join(HERE, '..', 'asm'))
import espc  # noqa: E402
import kl0 as K  # noqa: E402
import simpos_fs as FS  # noqa: E402
import fep as fepm  # noqa: E402

T0 = time.time()


def say(text):
    print('%6.0fs %s' % (time.time() - T0, text), file=sys.stderr, flush=True)


# -- packets and 32-bit strings ----------------------------------------------

def to_str32(raw):
    """A packet's bytes as the 32-bit string the front end reads."""
    if len(raw) % 4:
        raise ValueError('a packet of %d bytes is not whole words' % len(raw))
    s = K.Str('', 32)
    s.set_codes(list(struct.unpack('>%dI' % (len(raw) // 4), raw)))
    return s


def from_str32(s):
    """The front end's 32-bit output string as the packet's bytes."""
    s = K.deref(s)
    if not isinstance(s, K.Str):
        raise ValueError('the front end put %r, not a string' % (s,))
    return b''.join((c & 0xffffffff).to_bytes(4, 'big') for c in s.codes())


def show(raw):
    """A packet as [device, flag, command or status, args...]."""
    dev, flag = struct.unpack('>ii', raw[:8])
    return [dev, flag] + fepm.unpack_message(raw[8:])


# -- the PIM/m side ----------------------------------------------------------

class BridgeFep(fepm.Fep):
    """fep.py's Fep, but a device made by 601 is the PSI's (module doc)."""

    # 601 (step 3n) and, window M4 (2026-11-25), 104: PIMOS's windows
    BRIDGED = (fepm.CREATE_STRING_IO, fepm.CREATE_WINDOW)

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self.script = [('getl', ln) for ln in kw.get('lines', ())]   # no scripted login
        self.bridged = set()
        self.to_psi = []        # packets for the PSI, not yet given

    def packet(self, data):
        if len(data) < 8:
            raise fepm.FepError('a packet of %d bytes' % len(data))
        dev, flag = struct.unpack('>ii', data[:8])
        self.partial.setdefault(dev, []).append(data[8:])
        if flag == 1:
            return
        if flag != 0:
            raise fepm.FepError('packet flag %d' % flag)
        body = b''.join(self.partial.pop(dev))
        msg = fepm.unpack_message(body)
        if dev in self.bridged or (msg[0] in self.BRIDGED and not self.known(dev)):
            # the PSI's: the whole message, as one packet (OURS: continued
            # packets are joined here, as fep.py joins them)
            self.bridged.add(dev)
            self.messages.append(('>', dev, msg))
            self.to_psi.append(struct.pack('>ii', dev, 0) + body)
            return
        self.messages.append(('>', dev, msg))
        reply = self.request(dev, msg)
        if reply is not None:
            self.answer(dev, reply)

    def from_psi(self, raw):
        """A packet the PSI's front end put out: queued for RECEIVE."""
        dev = struct.unpack('>i', raw[:4])[0]
        if dev not in self.bridged:
            raise fepm.FepError('the PSI answers device %d, which is not its' % dev)
        self.messages.append(('<', dev, fepm.unpack_message(raw[8:])))
        self.replies.append(raw)


class PimSide:
    """PIMOS on ref/pimm/pimm.py from a link checkpoint, its device a
    BridgeFep; run() is longrun_ipl.go's loop up to the point it would
    ask the FEP for a scripted event."""

    def __init__(self, pkl, lines=()):
        import pickle
        import pimm
        import longrun_ipl as longrun
        self.pimm, self.longrun = pimm, longrun
        with open(pkl, 'rb') as f:
            m, loaded, info = pickle.load(f)
        say('loaded %s' % pkl)
        im = m.im
        m.ahead = True
        boot_info = m.new_var()
        m.argv[1], m.argv[2] = pimm.marked(loaded), pimm.marked(boot_info)
        m.record(pimm.READY, pimm.predicate(im, 'top', 'go_pimos1/2'), m.argv[1:3])
        m.spawn(pimm.predicate(im, 'ipl', 'make_boot_info/1'), [boot_info])
        m.tr = longrun.GoTrace()
        self.dev = m.fep = BridgeFep(longrun.kernel_file, getb_unit=2, lines=lines,
                                     list_dir=longrun.home_listing)
        self.m = m

    def run(self):
        """Run until nothing is left to run and no SCSI command finishes;
        the typed lines (fep.py's) are given at idle as go() gives them.
        -> the packets PIMOS sent for the PSI meanwhile."""
        m, dev, pimm = self.m, self.dev, self.pimm
        skips = 0
        while True:
            try:
                m.run(limit=10 ** 12)
            except pimm.Suspend:
                pass
            if m.scsi_poll():
                skips = 0
                continue
            if m.alarm_var is not None:
                skips += 1
                if skips > 100:
                    raise pimm.Unimplemented('100 alarms in a row with nothing else to do')
                m.alarm_skip()
                continue
            skips = 0
            if dev.to_psi:
                break
            if not dev.idle():
                break
            say('pim: a typed line at %d instructions' % m.tr.instructions)
        out, dev.to_psi = dev.to_psi, []
        return out

    def console(self):
        import lockstep_cons as cons
        return cons.console(self.m.tr)


# -- the PSI side ------------------------------------------------------------

# The boot program (OURS probe), as step 3m's b3m_boot: the boot process
# comes under the supervisor, the PSI user pmpsi logs in (B7), the front
# end is made with the held create/6 on the two streams the bridge gives
# (fe_in, fe_out) and started in a process of its own, the coordinator
# starts, and the boot process waits for ever.  The user's events (the
# menu's "Login PIMOS", the keys) are put on the coordinator's stream by
# the bridge later (PsiSide.run), not here
BOOT = '''class b3n_boot has
nature as_boot_program;
instance
attribute fe_in := 0, fe_out := 0, fe := 0;
:goal(Prog) :-
    :create(#boot_process, B), :activate(B, Prog),
    :create(#pimfep##simpos_user, "pmpsi", "pmpsi", SU),
    :self(#process, P), :setup_process(SU, P),
    :create(#pimfep##pimos_scsi_front_end, pimscsi, "PSI", Prog!fe_in, Prog!fe_out, FE),
    Prog!fe := FE,
    :create(#process, P2), :activate(P2, FE),
    :start(#coordinator),
    :create(#stream, Idle), :get(Idle, _);
end.'''


def keys(*lines):
    """Coordinator events for LINES typed, each ended by RETURN (13), as
    step 3m's (test_espc.Standins.keys)."""
    ev = []
    for line in lines:
        for c in K.Str(line).codes() + [13]:
            ev.append(K.Vec([K.Atom('key'), c]))
    return ev


def jstr(text):
    s = K.Str('')
    s.text = text
    return s


def walk(t):
    out, t = [], K.deref(t)
    while isinstance(t, K.Cons):
        out.append(K.deref(t.args[0]))
        t = K.deref(t.args[1])
    return out


def mouse(button, x, y):
    """A coordinator mouse event (window M6, OURS: coordinator.esp)."""
    return K.Vec([K.Atom('mouse'), K.Atom(button), x, y])


# The user's two batches (OURS; window M4/M6, 2026-11-25).  The menu: the
# right button at MENU_AT opens the system menu with its top-left there
# (menu_pane.esp), and the left button on its "Login PIMOS" item starts the
# requester, whose window is centred on that click (window_pane.esp), away
# from PIMOS's console at (200, 200).  The item's place follows from the
# menu's layout with test_11 (11 x 14 cells): columns 176 and 319 dots
# wide, items 16 dots high from 21 dots below the top; "Login PIMOS" is
# column 2, row 2 (psi/test_winfb.py WinM6 pins the drawn menu).  The
# console: the left button inside it selects it (the status band's box
# names it) and the shell's lines are typed to it.
MENU_AT = (640, 560)
LOGIN_ITEM_AT = (978, 605)
CONSOLE_AT = (300, 300)


def login_events(login):
    return [mouse('rr', *MENU_AT), mouse('l', *LOGIN_ITEM_AT)] + keys(*login)


def shell_events(shell):
    return [mouse('l', *CONSOLE_AT)] + keys(*shell)


class PsiSide:
    """SIMPOS's held FEP on kl0: the stand-ins, psi/simpos_fs.py's file
    system, the boot program BOOT with the login typed, and (window M4)
    the shell's lines typed into PIMOS's console window."""

    def __init__(self, login=('local', 'pimos', ''), shell=(), max_steps=20000000):
        ts, failed = espc.compile_text(BOOT, 'simpos')
        if failed:
            raise SystemExit('fep_bridge: the boot program does not compile: %r' % (failed,))
        lib = K.load_six()
        for t in espc.standins() + ts:
            lib.add(t)
        m = K.Machine(lib, max_steps=max_steps)
        FS.mount(m)
        (prog,) = K.call_class_method(m, 'simpos##b3n_boot', 'create', [K.Var()])[0]
        (fi,) = K.call_class_method(m, 'simpos##stream', 'create', [K.Var()])
        (fo,) = K.call_class_method(m, 'simpos##stream', 'create', [K.Var()])
        self.fe_in, self.fe_out = fi[0], fo[0]
        m.set_slot(prog, 'fe_in', self.fe_in)
        m.set_slot(prog, 'fe_out', self.fe_out)
        self.user = login_events(login)
        self.shell = shell_events(shell) if shell else []
        self.user_at = None     # the exchange the login's events were given at
        self.shell_at = None    # the exchange the shell's lines were given at
        self.windows = set()    # devices PIMOS made by 104 (its windows)
        self.getl = False       # a 104 window's 110 has been given
        self.exchanges = 0
        self.m, self.prog = m, prog

    def take_output(self):
        """The front end's output so far, taken from its stream's post
        queue (the SCSI driver's side of the stream: OURS)."""
        m = self.m
        q = m.get_slot(self.fe_out, 'post_queue')
        out = [from_str32(x) for x in walk(m.get_slot(q, 'objects'))]
        m.set_slot(q, 'objects', K.NIL)
        return out

    def run(self, exchange):
        """Boot and run.  EXCHANGE(packets out of the PSI) -> packets for
        it, called whenever every PSI process waits.  -> the refusal that
        ended the run (every process waiting, nothing exchanged)."""
        m = self.m

        def idle(mm):
            out = self.take_output()
            got = exchange(out)
            self.exchanges += 1
            for raw in got:
                p = show(raw)
                if p[2] == fepm.CREATE_WINDOW:
                    self.windows.add(p[0])
                elif p[2] == fepm.GETL and p[0] in self.windows:
                    self.getl = True
            s = m.get_slot(K.ClassRef('simpos##coordinator'), 'events')
            if not got and self.user:
                # the user (OURS): the menu's Login PIMOS and the three
                # answers, given at the first moment both sides are idle
                # (the PSI waits, and PIMOS, given all the PSI wrote, has
                # nothing for it: its login service has started and its
                # server's io(1) waits), on the coordinator's event
                # stream, as step 3m's boot program put them
                ev, self.user = self.user, []
                self.user_at = self.exchanges
                return [(s, e) for e in ev]
            if not got and self.shell and self.getl:
                # window M4 (OURS): the shell's lines, once PIMOS's console
                # waits for one (its 110 given) and PIMOS has nothing more
                ev, self.shell = self.shell, []
                self.shell_at = self.exchanges
                return [(s, e) for e in ev]
            return [(self.fe_in, to_str32(raw)) for raw in got]
        m.idle_hook = idle
        m.reset()
        try:
            any(True for _ in m.solve_send(self.prog, 'invoke', [self.prog]))
        except K.Refusal as e:
            return e
        return None

    def where(self, depth=12):
        """Where the PSI stopped: the instruction and its continuations
        (for reading a refusal)."""
        m = self.m

        def at(pc):
            c, o = pc[0], pc[1]
            return '%s @%x' % (getattr(c, 'id', c), o)
        out = [at(m.pc)] if m.pc and m.pc[0] != 'halt' else []
        k = m.cont
        while k and k != ('halt',) and len(out) < depth:
            out.append(at(k))
            env = k[2]
            k = env.cont if env is not None else None
        return out

    def requester_window(self):
        """The login requester's window history (step 3m's test reading):
        [('put', text) | ('typed', text) | ('event', atom)]."""
        m = self.m
        C = K.ClassRef('simpos##coordinator')
        started = walk(m.get_slot(C, 'started'))
        if not started:
            return None
        p = started[0]
        stack = K.resolve(m.get_slot(m.get_slot(p, 'invocation_stack'), 'elements'))
        if not isinstance(stack, K.Cons):
            return None
        top = K.deref(stack.args[0])
        w = m.get_slot(top, 'window')
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
                out.append(('event', str(e)))
        return out


# -- the runs ----------------------------------------------------------------

def screen(psi):
    """The PSI's framebuffer at the end of a run: its PBM's sha256 and the
    count of set dots (psi/windev.py)."""
    import windev
    fr = windev.device(psi.m).frame
    return dict(sha256=windev.pbm_sha256(fr), dots=fr.count())


def live(pkl, lines=(), record=None):
    """LINES: the shell's lines, typed into PIMOS's console window on the
    PSI (window M4; before it, fep.py's scripted getl answers)."""
    pim = PimSide(pkl)
    psi = PsiSide(shell=lines)
    tape = []

    def exchange(from_psi):
        for raw in from_psi:
            say('psi > pim %r' % (show(raw),))
            pim.dev.from_psi(raw)
        to_psi = pim.run()
        for raw in to_psi:
            say('pim > psi %r' % (show(raw),))
        tape.append(dict(from_psi=[r.hex() for r in from_psi], to_psi=[r.hex() for r in to_psi]))
        return to_psi
    stop = psi.run(exchange)
    result = dict(stop='%s: %s' % (stop.cause, stop.detail) if stop else None,
                  window=psi.requester_window(), console=pim.console(),
                  log=[(d, t) for d, t in pim.dev.log], held=dict(pim.dev.held),
                  instructions=pim.m.tr.instructions,
                  user_at=[psi.user_at, psi.shell_at], screen=screen(psi))
    if record:
        with open(record, 'w') as f:
            json.dump(dict(lines=list(lines), shell=list(lines), exchanges=tape, result=result),
                      f, indent=1)
    return result, psi, pim


def replay(path):
    with open(path) as f:
        t = json.load(f)
    # a tape from before window M4 (no `shell`) typed its lines to fep.py
    psi = PsiSide(shell=t.get('shell', ()))
    tape = list(t['exchanges'])
    seen = []

    def exchange(from_psi):
        if not tape:
            raise AssertionError('the PSI asks for an exchange the tape does not have')
        e = tape.pop(0)
        got = [r.hex() for r in from_psi]
        seen.append(got)
        if got != e['from_psi']:
            raise AssertionError('exchange %d: the PSI sent %r, the live run %r'
                                 % (len(seen), [show(r) for r in from_psi],
                                    [show(bytes.fromhex(r)) for r in e['from_psi']]))
        return [bytes.fromhex(r) for r in e['to_psi']]
    stop = psi.run(exchange)
    return stop, psi, tape, t


def main(argv):
    if len(argv) > 2 and argv[1] == 'live':
        lines = [argv[i + 1] for i, a in enumerate(argv) if a == '--type']
        rec = argv[argv.index('--record') + 1] if '--record' in argv else None
        result, _psi, _pim = live(argv[2], lines, rec)
        for k, v in result.items():
            print('%s: %r' % (k, v))
        return 0
    if len(argv) > 2 and argv[1] == 'replay':
        stop, psi, left, _t = replay(argv[2])
        print('stop: %s: %s' % (stop.cause, stop.detail) if stop else 'stop: none')
        print('window: %r' % (psi.requester_window(),))
        print('exchanges left: %d' % len(left))
        return 0
    print(__doc__)
    return 2


if __name__ == '__main__':
    sys.exit(main(sys.argv))
