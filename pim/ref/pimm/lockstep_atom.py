#!/usr/bin/env python3
"""Lockstep: the atom-number server of top:go1/4, supply_atom_number,
and a merger input bound to a vector.

    python3 ref/pimm/lockstep_atom.py --script FILE     write the script
    sim_pimm_driver | python3 ref/pimm/lockstep_atom.py compare
    python3 ref/pimm/lockstep_atom.py --reference       the reference alone

top:go1/4 (cell 17391), the goal top:go/4 runs in the BIOS's shoen,
as decompiled (asm/kl1decomp.py top; the held source does not have
it):

    go1(A, B, C, D) :- true |
        current_node(E, F), merge(G, H),
        predicate_to_code(module#top, go_pimos, 3, I),
        shoen:execute(I, {A, B, D}, [start|J], K), bios_monitor(K, J, C),
        throw_atom_number_client(0, E, F, 512, 15872, H, L),
        wait_for_atom_server_end(M),
        atom_number_server(G, C, M, 16384, 8192, 16777216, L).
    throw_atom_number_client(A, _, B, C, D, E, F) :- true |
        supply_atom_number(C, D, G), throw_atom_number_client(G, A, B, E, F).
    throw_atom_number_client(A, B, C, D, E) :- wait(A) |
        throw_atom_number_client(B, C, D, E).
    throw_atom_number_client(A, B, C, D) :- integer(A), integer(B), A < B |
        C = {E, F}, G := A + 1, throw_atom_number_client(G, B, F, D),
        atom_number_client(D, 0, E, A)@processor(A).
    otherwise.  throw_atom_number_client(_, _, A, _) :- true | A = [].
    atom_number_client(A, _, B, _) :- wait(A) | B = [].
    alternatively.
    atom_number_client(A, B, C, D) :- wait(B) |
        C = [{D, E, F}|G], atom_number_client(A, E, F, G, D).
    atom_number_client(A, _, _, B, _) :- wait(A) | B = [].
    alternatively.
    atom_number_client(_, [], [], A, _) :- true | A = [].
    atom_number_client(A, B, C, D, E) :- integer(B), integer(C) |
        supply_atom_number(B, C, F), atom_number_client(A, F, D, E).

and the server, atom_number_server/7 with check_overflow/10: a request
{P, X, Y} is answered X = Next + Size, Y = Size, and Next becomes
Next + Size, while Next < Limit - Size (else a warning, or near the
limit X = Next + Size, Y = Limit - Next).  When C is bound it binds L
= 0, which ends the clients; when its input closes it binds M = 0 and
wait_for_atom_server_end/1 shows "Atom Server End********".

supply_atom_number(X, Y, ^Done), 22:B9 r_r_r, two inputs and an output
(PIMOS library/assembler/inst_tab.kl1:249, library/compiler/blt.kl1:
747-750).  NO MANUAL ENTRY, and nothing in PDSS, VPIM or the PIMOS
source says what it does (searched 2026-11-23; docs/pimm_semantics.md
says where).  What the code forces: the inputs are integers (the
client tests them); Done is waited for, and each time it is bound the
processor's client asks the server for another block, so Done is "give
me more", bound by the machine at some later time, NOT at once (bound
at once, the client would ask again and again, to the server's limit).
What the code does NOT force: what X and Y are.  As (first number,
count) the first call (512, 15872) ends at 16384, the server's first
Next, but the server's answers would then skip 16384..24575; as
(end, count) the answers are contiguous from 16384 but the first call
is not a range; the near-limit answer fits neither.  So which numbers
a processor hands out is not inferred.  HERE (OURS, the narrowest the
code needs): the inputs must be integers (waited for, as any body
built-in) and are dropped; Done is a fresh variable that no model ever
binds, as new_atom (ours, a counter from 10000h) draws on no range.
So the clients never start unless something binds Done: in this test
the BENCH does, standing in for the machine taking the range into use.

The merger input bound to a vector: throw_atom_number_client/4's C =
{E, F}, the merger's input H.  "When a vector is unified to an MHV, as
many input streams (MHVs) as the arity of the vector are added to the
merger process and each element of the vector is unified to each new
input stream" (TR-466 3.3; TR-483 2.7.2, as quoted in docs/
literature_gaps.md).  Here (docs/pimm_semantics.md `merge`): the
input that was bound ends and each element gets a ready goal of the
stub merge_in, the last element's first; the count goes up by the
size less one.  Both models make each goal through the argument
registers (a1 the element, a2 the record), as enqueue_goal does.  A
vector of seven or more is refused on both models.

Parts, and what each must leave (written from the code above before
the first run; the order the goals run in is the model's, newest
first):
  go1          current_node gives 0 and 1 (at cell 17391); one call
               supply_atom_number(512, 15872), its Done left unbound;
               the merger's count 1
  first range  the bench binds that Done to 0 (OURS): one client is
               thrown (TotalNode = 1), H = {E, F}, the merger's count
               1 - 1 + 2, then F = [] makes it 1; the client asks, the
               server answers {0, 24576, 8192}, and the client calls
               supply_atom_number(24576, 8192)
  second range the bench binds the second Done: the server answers
               {0, 32768, 8192}, a third call
  BIOS ends    the bench binds C = shut (what bios_monitor/3 does when
               the BIOS's report closes): the server binds L = 0, the
               client closes its input, the merger's count is 0 and
               its output closed: the server's input was exactly
               [{0, 24576, 8192}, {0, 32768, 8192}]; the console is
               given "Atom Server End********"
At the end four goals wait: the BIOS shoen's control/2 and report/2
(shoen:execute/4), bios_monitor/3 on the report, and go_pimos/3 in
the shoen on D.

Observed fault injections into the Bluespec, 2026-11-23, each run
alone (bsv/run_pimm_lockstep.sh atom) and restored from a copy:
  supply: Done bound at once to 0     go1, line 209: R 0 0 for the
                                      fresh variable
  merger box: count not raised        first range, line 172: the count
    by the vector's size              written 0 for 2
  merger vector: one goal only        first range, line 181: the
                                      second element's a1 not written
  merger vector: a2 the stream        first range, line 174
  merger vector refused (the gate     first range, line 172: E unimp
    of before 2026-11-23)
NOT caught (both injected, both PASSED):
  - supply_atom_number taking a non-integer: every call has integers;
  - the merger taking an unbound element without its MRB: by the time
    the merger's goal on H runs, the client has bound E and the
    recursion F (newest goal first), so no element is unbound.
Five of seven caught.
Re-pinned at the merge with shoen stage 2 (2026-11-23), 1251 -> 1255
trace lines, both models still identical and every check passing.
top:go1/4 starts the BIOS's shoen (shoen:execute/4), and the only
change merged under this test is shoen stage 2, whose record has two
more cells and writes its reduction count at the end of each run; that
the 4 lines are those writes is expected, not counted line by line.
Re-pinned for shoen stage 3 (2026-11-23), 1255 -> 1257 trace lines, no
value changed: the shoen record has one more cell, SH_MASK, written at
create (1 shoen made: 1 lines), and start_shoen empties the parked
list, SH_GOAL := 0 (1 starts: 1 lines); counted on the reference's
trace (both writes, nothing else new).
Re-pinned for the merger timing change (2026-11-24, docs/
pimm_semantics.md merge: a woken goal of merge_in goes on the
merger's list, taken before the ready queue), 1257 -> 1300 trace
lines, both models identical and every check passing (the server
still asked exactly the two requests).  The goals run in another
order, and each pickup that splices the list writes one link more.
The injections' line numbers above are as observed before it.
Re-pinned for R8 (2026-11-25), 1300 -> 1565 trace lines, every value
unchanged: a shoen now starts with no resource (VPIM's
_INIT_SHOEN_RESOURCE is 0), so the BIOS's shoen has three more record
cells written at create (SH_RSC_HI/LO/FLAGS), its first goal parks (one
`E park`), resource_low goes to top:bios_monitor/3, and the monitor
answers add_resource and allow_resource_report on the Control: 112 more
instructions and 4 more goals, counted on the reference's trace against
the base commit's (aab75b28).
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', '..', 'asm'))
import driver  # noqa: E402
import pimm  # noqa: E402
import lockstep_cons as cons  # noqa: E402

PINNED = dict(parts=4, lines=1565)
I = lambda v: (pimm.INT, v & 0xffffffff)           # noqa: E731
GO1 = 17391                 # top:go1/4, its first instruction current_node 4, 5
MERGE = GO1 + 2             # merge 6, 6
SUPPLIED = {'go1': [(512, 15872)],
            'first range': [(512, 15872), (24576, 8192)],
            'second range': [(512, 15872), (24576, 8192), (32768, 8192)],
            'BIOS ends': [(512, 15872), (24576, 8192), (32768, 8192)]}
COUNT = {'go1': 1, 'first range': 1, 'second range': 1, 'BIOS ends': 0}
REQUESTS = [(0, 24576, 8192), (0, 32768, 8192)]
CONSOLE = {'go1': [], 'first range': [], 'second range': [],
           'BIOS ends': ['Atom Server End********']}
WAITING = 4


def script():
    im = pimm.kbndis.Image()
    names = {name: n for n, name in im.sym.items()}
    assert pimm.predicate(im, 'top', 'go1/4') == GO1
    s = driver.Script()
    s.label('go1')
    for i in range(4):
        s.newvar(i)                                # A, B, C, D
    for a in range(1, 5):
        s.arg(a, a - 1)
    s.spawn(GO1, 4)
    s.run()
    for k, label in enumerate(('first range', 'second range')):
        m = s.live()
        assert len(m.supplied) == k + 1
        s.label(label)
        s.setslot(4, m.supplied[k][2])             # that call's Done
        s.unifyc(4, I(0))
        s.run()
    s.label('BIOS ends')
    s.unifyc(2, (pimm.ATOM, names['shut']))
    s.run()
    return s


def merger(lines, load):
    """The merger record go1's merge made (the R 254 after its I line:
    {INT, its address}) and the output variable written into it first
    (M lines are relative to the load address)."""
    i = [k for k, ln in enumerate(lines) if ln.startswith('I %d ' % MERGE)][0]
    rec = [int(ln.split()[2][2:], 16) for ln in lines[i:] if ln.startswith('R 254 ')][0]
    out = [ln.split()[2] for ln in lines[i:] if ln.startswith('M %d ' % (rec - load))][0]
    return rec, (int(out[:2], 16), int(out[2:], 16))


def check(m, snaps, parts):
    bad = []
    lines = parts.get('go1', [])
    i = lines.index([ln for ln in lines if ln.startswith('I %d ' % GO1)][0])
    if lines[i + 1:i + 3] != ['R 4 %02x%08x' % (pimm.INT, 0), 'R 5 %02x%08x' % (pimm.INT, 1)]:
        bad.append(('current_node at go1', lines[i + 1:i + 3]))
    rec, out = merger(lines, m.load)
    for k in SUPPLIED:
        got = snaps.get(k)
        want = (SUPPLIED[k], COUNT[k], CONSOLE[k])
        if got != want:
            bad.append((k, got, want))
    t = m.term(out)
    if t != [REQUESTS[0], REQUESTS[1]]:
        bad.append(('the server was asked', t))
    if m.nsusp != WAITING:
        bad.append(('%d goals left waiting, expected %d' % (m.nsusp, WAITING),))
    return bad, rec


def main(argv):
    s = script()
    if '--script' in argv:
        s.write(argv[argv.index('--script') + 1])
        return 0
    kept, snaps = {}, {}
    play = s.play

    def keeping():
        for what, lines in play():
            kept[what] = lines
            m = s.machine
            rec, _out = merger(kept['go1'], m.load)
            snaps[what] = ([x[:2] for x in m.supplied], pimm.signed(m.mem[rec + 1][1]),
                           cons.console(lines))
            yield what, lines
    s.play = keeping
    if '--reference' in argv:
        n = sum(len(v) for _k, v in s.play())
        bad, _rec = check(s.machine, snaps, kept)
        print(bad, n)
        return 1 if bad else 0
    ok, m = driver.compare(s, sys.stdin, 'pimm lockstep atom', PINNED)
    if not ok:
        return 1
    bad, _rec = check(m, snaps, kept)
    if bad:
        print('pimm lockstep atom: FAIL %r' % (bad[:3],))
        return 1
    print('pimm lockstep atom: PASS (top:go1/4\'s atom-number server on the Bluespec core, %d '
          'trace lines identical to the reference model: current_node at its image site, '
          'supply_atom_number three times, a merger input bound to a vector of two, the '
          'server answering two requests and ending)' % s.counts['lines'])
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
