#!/usr/bin/env python3
"""Step 3n (2026-11-25): the held SIMPOS FEP on kl0 logs into PIMOS.

    python3 psi/test_fep_bridge.py          the in-suite tests (~10 s)
    FEP_BRIDGE_PKL=PKL python3 psi/test_fep_bridge.py
        also the live run (PIMOS from the IPL's link checkpoint PKL on
        ref/pimm/pimm.py, ~30 s, ~15 GB resident), checked against the tape

What is checked (psi/fep_bridge.py has the boundary):
  - Assembler: the held pimfep##fep_message_assembler assemble/3 gives,
    word for word, the packet ref/pimm/fep.py's pack_message gives (five
    messages, one of each argument kind), and its disassemble/3 decodes
    PIMOS's own packets of the reference run (601, 620 io(0..1), 70, 60,
    127).
  - Scripted: the PSI side alone, fed the messages PIMOS sent the FEP in
    the pinned reference run (ref/pimm/longrun_ipl.py --go --fep --type
    pwd on the link checkpoint, its log), up to its login service's io(1):
    the held front end, replier and server answer each as fep.py did,
    the user types at the first quiet exchange, and the requester sends
    NI, the login record, as fep.login_record with RP "pmpsi".
  - Tape: the live run's exchanges (psi/fep_bridge_tapes/login_pwd.json),
    replayed on the PSI side alone: each packet the PSI sends equals the
    live run's, the requester's window shows PIMOS's three login texts,
    and the shell window's texts (fep.py's) are those of the pinned shell
    run, lockstep_shell.APPS['pwd'].

Fault injections (2026-11-25; each into the file from a backup copy,
the backup copied back after and checked with cmp; the OBSERVED failures
of this file, the live test skipped):
  F1 kl0.py op_substring_7 (16, 32): the low half first:
     Assembler.test_assemble_is_pack_message FAIL, Scripted FAIL, Tape FAIL
     (disassemble passes: it reads 32 to 16 only)
  F2 kl0.py op_substring_7 16/32: U = 1, not 0:
     Assembler.test_assemble_is_pack_message ERROR (create_argument_string_list
     /5 @125 fails, so assemble/3 has no solution), Scripted FAIL, Tape FAIL
  F3 kl0.py op_string_element: a 32-bit element read unsigned:
     Assembler.test_disassemble ERROR, Scripted FAIL, Tape FAIL
  F4 kl0.py op_get_integer: the immediate read unsigned:
     Assembler.test_disassemble ERROR, Scripted FAIL, Tape FAIL
  F5 standin/list_index.esp add_last/4: the entry the term {'$$void',
     Object, Key} again (step 3m's): Scripted FAIL, Tape FAIL
  F6 standin/string.esp append/3: a 16-bit string always (step 3m's):
     Assembler.test_assemble_is_pack_message FAIL, Scripted FAIL, Tape FAIL
  F7 fep_bridge.py PsiSide.run: the user's events at the first idle, not
     the first quiet one: Scripted FAIL, Tape FAIL
  F8 kl0.py pathname_remote_or_local: the local part not given: Tape FAIL
  F11 kl0.py world_root_path: Root ">" ++ the logical name, not the
     directory's full name: Tape FAIL
  Not observed here, recorded as such (no test in this file fails):
  F9 blt 0d object/3 always failing.  Traced (2026-11-25, the replay with
     object/3 logged): it is met three times, all at the front end's
     delete_remote_stream/2 @879, always on the atom nil, and fails
     there, so its success branch is not on this path.  The row is needed
     only so that the run does not refuse; test_kl0.py Step3nRows
     test_object pins it (F9 FAILS there).
  F10 exterminate/1 not giving the processor away.  Traced: three
     string-I/O device processes (devices 25, 26, 29) exterminate
     themselves, each as exit_program/1's last call, so nothing of theirs
     runs after it either way.  test_espc.py test_step3n_exterminate
     discriminates it (F10 FAILS there).
"""
import json
import os
import struct
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fep_bridge as B  # noqa: E402

K = B.K
espc = B.espc
fepm = B.fepm
J = fepm.jis
TAPE = os.path.join(HERE, 'fep_bridge_tapes', 'login_pwd.json')


def machine():
    lib = K.load_six()
    for t in espc.standins():
        lib.add(t)
    return K.Machine(lib, max_steps=600000)


def s16(b):
    s = K.Str('')
    s.set_codes([int.from_bytes(b[i:i + 2], 'big') for i in range(0, len(b), 2)])
    return s


def pk(dev, msg):
    return struct.pack('>ii', dev, 0) + fepm.pack_message(msg)


class Assembler(unittest.TestCase):
    def test_assemble_is_pack_message(self):
        m = machine()
        for msg in ([16, 1, s16(J('ab'))], [16, 1], [24, 1, s16(fepm.login_record(**fepm.LOGIN))],
                    [23, 1, s16(bytes(2))], [17, 1, 33742, 30045]):
            m.reset()
            (sol,) = K.call_class_method(m, 'pimfep##fep_message_assembler', 'assemble',
                                         [K.Vec(msg), K.Var()], limit=1)
            r = K.deref(sol[1])
            self.assertEqual(r.type, 32)
            args = [b''.join(c.to_bytes(2, 'big') for c in K.deref(a).codes())
                    if isinstance(K.deref(a), K.Str) else a for a in msg[2:]]
            want = msg[0].to_bytes(4, 'big') + bytes(4) + fepm.pack_message([msg[1]] + args)
            self.assertEqual(B.from_str32(r), want, msg)

    def test_disassemble(self):
        m = machine()
        got = []
        for dev, msg in ((23, [601, b'', 0, 0, J('pimos_remote_login_replier')]), (23, [620, 0, b'']),
                         (24, [620, 0, J('local')]), (24, [620, 1, J('  ')]),
                         (26, [620, 0, b'\x00\x05\x00\x00' + J('pmpsi')]), (26, [70]), (26, [60]),
                         (28, [127, 200, 200, 47, 14])):
            m.reset()
            (sol,) = K.call_class_method(m, 'pimfep##fep_message_assembler', 'disassemble',
                                         [B.to_str32(pk(dev, msg)), K.Var()], limit=1)
            v = K.resolve(sol[1])
            got.append([x.codes() if isinstance(x, K.Str) else x for x in v.args])
        self.assertEqual(got, [
            [23, 601, [], 0, 0, K.Str('pimos_remote_login_replier').codes()],
            [23, 620, 0, []],
            [24, 620, 0, K.Str('local').codes()],
            [24, 620, 1, K.Str('  ').codes()],
            [26, 620, 0, [5, 0] + K.Str('pmpsi').codes()],
            [26, 70], [26, 60],
            [28, 127, 200, 200, 47, 14]])


# PIMOS's messages to the FEP in the pinned reference run, in its order,
# for the login replier (23) and the two servers (24 local, 25 tcpip)
SCRIPT = [
    [(23, [601, b'', 0, 0, J('pimos_remote_login_replier')])],
    [(23, [620, 0, b''])],
    [(24, [601, b'', 0, 0, J('pimos_remote_login_server')])],
    [(24, [620, 0, J('local')])],
    [(24, [620, 1, J('  ')]), (25, [601, b'', 0, 0, J('pimos_remote_login_server')])],
    [(25, [620, 0, J('tcpip')])],
]


class Scripted(unittest.TestCase):
    def test_login_service_and_login(self):
        psi = B.PsiSide()
        out, n = [], [0]

        def exchange(raws):
            out.extend(B.show(r) for r in raws)
            if n[0] >= len(SCRIPT):
                return []
            s = SCRIPT[n[0]]
            n[0] += 1
            return [pk(d, msg) for d, msg in s]
        stop = psi.run(exchange)
        self.assertEqual(stop.cause, 'would suspend')
        ni = fepm.login_record(**dict(fepm.LOGIN, rp='pmpsi'))
        # the reference run's FEP answers (fep.py's), and then the PSI's NI
        self.assertEqual(out, [[23, 0, 1], [23, 0, 1, b''], [24, 0, 1], [24, 0, 1, b''],
                               [25, 0, 1], [25, 0, 5], [24, 0, 1, ni]])
        self.assertEqual(psi.user_at, len(SCRIPT) + 1)
        self.assertEqual(psi.requester_window(), [
            ('put', 'Enter FEP node name--------->'), ('typed', 'local'),
            ('put', 'Enter your PIMOS user name-->'), ('typed', 'pimos'),
            ('put', 'Enter your PIMOS password--->'), ('put', 'Your request is accepted.')])


class Tape(unittest.TestCase):
    WINDOW = [('put', 'Enter FEP node name--------->'), ('typed', 'local'),
              ('put', 'Enter your PIMOS user name-->'), ('typed', 'pimos'),
              ('put', 'Enter your PIMOS password--->'), ('put', 'Your request is accepted.'),
              # PIMOS's own texts (login.kl1), through the bridge
              ('put', 'Login procedure starts.'),
              ('put', 'OK. Your initial program starts.<000a>'),
              ('put', 'Good luck!<000a>'),
              # the held requester's wait/1 after a login (step 3m)
              ('event', 'beep'), ('event', 'beep')]

    def test_replay(self):
        stop, psi, left, t = B.replay(TAPE)
        self.assertEqual((stop.cause, left), ('would suspend', []))
        self.assertEqual(psi.requester_window(), self.WINDOW)
        self.assertEqual([tuple(x) for x in t['result']['window']], self.WINDOW)
        # the shell window is fep.py's: its texts are the pinned shell run's
        sys.path.insert(0, os.path.join(HERE, '..', 'ref', 'pimm'))
        import lockstep_shell
        lines, texts = lockstep_shell.APPS['pwd']
        self.assertEqual(t['lines'], list(lines))
        self.assertEqual([x for _d, x in t['result']['log']], ['Shell>> '] + list(texts))
        self.assertEqual({d for d, _x in t['result']['log']}, {28})


CONSOLE_TAPE = os.path.join(HERE, 'fep_bridge_tapes', 'console_pwd.json')


class Console(unittest.TestCase):
    """Window M4 (2026-11-25): PIMOS's shell window, its 104 device, is
    the PSI's (BridgeFep.BRIDGED).  The live run (s3_merger.pkl, 28 s)
    recorded psi/fep_bridge_tapes/console_pwd.json; the user (OURS) logs
    in by the mouse and types `pwd` into the console once PIMOS's 110
    waits.  login_pwd.json (step 3n, the window fep.py's) still replays
    (Tape above)."""

    def test_replay(self):
        stop, psi, left, t = B.replay(CONSOLE_TAPE)
        self.assertEqual((stop.cause, left), ('would suspend', []))
        self.assertEqual(psi.requester_window(), Tape.WINDOW)
        self.assertEqual(t['shell'], ['pwd'])
        # fep.py answered none of the window's messages: no log, nothing held
        self.assertEqual((t['result']['log'], t['result']['held']), ([], {}))
        # PIMOS's messages to its window, in order, and the PSI's answers
        to, back = [], []
        for e in t['exchanges']:
            to += [B.show(bytes.fromhex(r)) for r in e['to_psi']]
            back += [B.show(bytes.fromhex(r)) for r in e['from_psi']]
        to28 = [p[2:] for p in to if p[0] == 28]
        self.assertEqual(to28, [
            [104, b'', J('pmpsi'), J('pmpsi')], [127, 200, 200, 47, 14],
            [130, J('PIMOS CONSOLE')], [132, J('font:test_11.font')], [143],
            [70], [70], [70], [112], [111, J('Shell>> ')], [112], [112], [110],
            [111, J(' The value of task: directory is ">sys>user>pmpsi" . \n')],
            [112], [111, J('Shell>> ')], [112], [112], [110]])
        back28 = [p[2:] for p in back if p[0] == 28]
        # {Id, 1} to each but the 70s (abort: no reply, as fep.py's and
        # the login servers' 70s, fep_services.md 6.7) and the last 110,
        # which waits; the first
        # 110's answer is the line the user typed, from the editor's buffer
        self.assertEqual(back28, [[1]] * 5 + [[1]] * 4 + [[1, J('pwd')]] + [[1]] * 5)
        self.assertEqual((psi.user_at, psi.shell_at), (6, 19))

    @unittest.skipUnless(os.environ.get('FEP_BRIDGE_PKL'), 'set FEP_BRIDGE_PKL to the link checkpoint')
    def test_live(self):
        with open(CONSOLE_TAPE) as f:
            t = json.load(f)
        result, _psi, _pim = B.live(os.environ['FEP_BRIDGE_PKL'], t['shell'])
        self.assertEqual(json.loads(json.dumps(result)), t['result'])


if __name__ == '__main__':
    unittest.main()
