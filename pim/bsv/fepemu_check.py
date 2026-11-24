#!/usr/bin/env python3
"""The FEP emulator against fep.py, command by command.  ALL OURS.

    python3 bsv/fepemu_check.py SIM [TAPE ...]

For each tape (default: every ref/pimm/fep_tapes/*.tape):
  1. a card image: pim/tools/mkfepcard.py --made-up FILES --decoys (the
     made-up pimos.ipl and .sav files of the part, behind decoy entries
     whose names are a prefix or an extension of a real one); for a tape
     whose files are `pimos:` (the kernel's), the held object directory
     as pimos:NAME, behind its decoys; on every card fep.py's attributes
     and its script (or the tape's `script`), mkfepcard.fep_tables;
  2. fep.py's answers: the tape's commands replayed into a fresh fep.Fep
     (ref/pimm/record_fep.replay), its open_file the one ref_scsi.py's
     machine run used (the held archive, NOT the card: so the card
     builder is checked too);
  3. the vector file for PimmFepEmuTb.c;
  4. the bench SIM (Bluesim: mkPimmFepEmuTb or mkPimmFepEmuSpiTb) with
     PIMM_SD_IMAGE and PIMM_FEP_VECTORS;
  5. every answer line compared with fep.py's: kind (done, not ready,
     refused), result, the count, the bytes; and for each event (the
     tape's `idle`, Fep.idle()) whether a reply was queued.  A line
     missing or over is
     a failure.  A refusal matches any FepError (the why code is shown,
     not compared).
Exit 0 only if every tape matches.  Files go to bsv/build_fepemu/.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PIM = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(PIM, 'ref', 'pimm'))
sys.path.insert(0, os.path.join(PIM, 'tools'))
BUILD = os.path.join(HERE, os.environ.get('FEPEMU_BUILD', 'build_fepemu'))

import record_fep as rec  # noqa: E402
import mkfepcard  # noqa: E402


def vectors(sections):
    out = []
    for opts, cmds in sections:
        out.append([1, opts['getb_unit'], opts['getb_bytes'], opts['lag'], opts['max_buffer']])
        for c in cmds:
            if c[0] == 'ticks':
                out.append([4, c[1] >> 32, c[1] & 0xffffffff])
                continue
            if c == rec.IDLE:
                out.append([3])
                continue
            unit, lun, cdb, length, direction, data = c
            data = data if direction == 1 else b''
            out.append([2, unit & 0xffffffff, lun & 0xffffffff, direction, length, len(cdb)]
                       + list(cdb) + [len(data)] + list(data))
    out.append([0])
    return '\n'.join(' '.join('%x' % x for x in r) for r in out) + '\n'


def expected_lines(answers):
    out = []
    for a in answers:
        if a[0] == 'D':
            out.append(('D', a[1], len(a[2]), a[2].hex() or '-'))
        elif a[0] == 'N':
            out.append(('N',))
        elif a[0] == 'I':
            out.append(('I', int(a[1])))
        else:
            out.append(('E',))
    return out


def bench_lines(text):
    got, end = [], None
    for line in text.splitlines():
        w = line.split()
        if not w:
            continue
        if w[0] == 'A' and w[1] == 'D':
            got.append(('D', int(w[2]), int(w[3]), w[4] if len(w) > 4 else ''))
        elif w[0] == 'A' and w[1] == 'N':
            got.append(('N',))
        elif w[0] == 'A' and w[1] == 'I':
            got.append(('I', int(w[2])))
        elif w[0] == 'A' and w[1] == 'E':
            got.append(('E', int(w[2])))
        elif w[0] == 'END':
            end = line
        elif w[0] == 'FAIL':
            end = line
    return got, end


def show(a):
    if a[0] == 'D':
        h = a[3]
        return 'done %d, %d bytes %s' % (a[1], a[2], h[:48] + ('...' if len(h) > 48 else ''))
    if a[0] == 'I':
        return 'event, %s' % ('a reply queued' if a[1] else 'nothing queued')
    return {'N': 'not ready', 'E': 'refused'}[a[0]] + ('' if len(a) == 1 else ' (why %d)' % a[1])


def first_diff(a, b):
    for i in range(min(len(a), len(b))):
        if a[i] != b[i]:
            return i
    return min(len(a), len(b))


def check_tape(sim, path):
    part, files, sections, script = rec.read_tape(path)
    img = os.path.join(BUILD, part + '.img')
    real = mkfepcard.objects() if files == [rec.OBJECTS] else mkfepcard.made_up(files)
    entries = mkfepcard.decoys(real) + real
    with open(img, 'wb') as fh:
        fh.write(mkfepcard.build(entries, 'PIM/m FEP card (OURS), bsv/fepemu_check.py, part '
                                 + part, mkfepcard.fep_tables(script)))
    want = expected_lines(rec.replay(sections, files, script))
    vec = os.path.join(BUILD, part + '.vec')
    with open(vec, 'w') as fh:
        fh.write(vectors(sections))
    env = dict(os.environ, PIMM_SD_IMAGE=img, PIMM_FEP_VECTORS=vec)
    run = subprocess.run([sim], env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                         universal_newlines=True, timeout=1200)
    with open(os.path.join(BUILD, '%s.%s.out' % (part, os.path.basename(sim))), 'w') as fh:
        fh.write(run.stdout)
    got, end = bench_lines(run.stdout)
    bad = []
    if end is None or not end.startswith('END'):
        bad.append('the bench did not finish: %r' % (end or run.stdout[-300:]))
    if len(got) != len(want):
        bad.append('%d answers, fep.py gave %d' % (len(got), len(want)))
    flat = [c for _, cmds in sections for c in cmds if c[0] != 'ticks']
    for i, (g, x) in enumerate(zip(got, want)):
        if g[:1] == ('E',) and x == ('E',):
            continue
        if g != x:
            c = flat[i]
            what = 'the event' if c == rec.IDLE else 'CDB %s, %d bytes' % (c[2].hex(), c[3])
            msg = 'command %d (%s): emulator %s; fep.py %s' % (i, what, show(g), show(x))
            if g[0] == x[0] == 'D' and g[3] != x[3]:
                k = first_diff(g[3], x[3]) // 2
                msg += '; first byte different: %d' % k
            bad.append(msg)
    kinds = {k: sum(1 for x in want if x[0] == k) for k in 'DNEI'}
    nbytes = sum(x[2] for x in want if x[0] == 'D')
    status = 'PASS' if not bad else 'FAIL'
    print('fepemu %-12s %s: %3d commands (%d done, %d not ready, %d refused), %d events, '
          '%6d bytes back, %s'
          % (part, status, len(want) - kinds['I'], kinds['D'], kinds['N'], kinds['E'],
             kinds['I'], nbytes, (end or '').strip()))
    for b in bad[:6]:
        print('    ' + b)
    return not bad


def main(argv):
    sim = argv[1]
    tapes = argv[2:] or sorted(os.path.join(rec.TAPES, t) for t in os.listdir(rec.TAPES)
                               if t.endswith('.tape'))
    os.makedirs(BUILD, exist_ok=True)
    ok = all([check_tape(sim, t) for t in tapes])
    print('fepemu: %s (%d tapes; the emulator\'s every answer against fep.py\'s)'
          % ('PASS' if ok else 'FAIL', len(tapes)))
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv))
