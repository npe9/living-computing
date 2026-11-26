#!/usr/bin/env python3
"""R8 item: why a file with one aborted module is not loaded at all,
traced on the reference model (2026-11-26).  OURS, not in the suite: it
needs a prompt checkpoint (bsv/README.md, "The lockstep from a saved
machine"), ~1.1 GB, not in git.

    python3 ref/pimm/r8_entry_trace.py PROMPT.pkl

Serves fact.kl1 with only `:- public` lines added (fact_pub.kl1, a
private entry of longrun_ipl.HOME_FILES in this process only), types
compile / !package work / fact_pub / !exit / listener /
default_package(work). / fact:fact(10,R). and prints, at each entry to
two of the loader's predicates, the arguments the decision rests on:

  kl1_self_cal:watch_compile/17 (library/loader/selfcal.kl1:46-87):
      PrevStatus, CompStatus, AsmStatus, LoadStatus, Status, Name
  kl1_compiler_distributer:flush/6 (library/loader/dstrbt.kl1:676-686):
      St, ...

The predicates are found by their place in the code (the instruction
at a predicate head's entry, its name atom four cells before:
pimm.py i_code_to_predicate) and named by arity and argument shape,
not by name: the atoms of modules loaded from the kernel's .sav files
have no names in the reference (pimm.term prints them '#hex').  Which
atom is `normal` and which `abnormal` is read from which clause's
message appears (INFERENCE): `Compile Aborted : top` is
watch_compile's third clause, (normal, abnormal, _, _).

Observed 2026-11-26 (from the R8 second half's prompt checkpoint,
8,595,408 instructions; the run 2,102,064 instructions, the Listener's
` Nonexistent module>> fact`), in this order:
  watch_compile? #11540/17 at 29121251: [#100e4, #10123, #100e4, #100e4, #117ac]  (top)
  flush? #1011e/6 at 28479283: St #10123
  watch_compile? #11540/17 at 29121251: [#100e4, #100e4, #100e4, #100e4, #12737]  (fact)
and on fact_r8.kl1 (control, APPS pkl1_fact, 1,335,291 instructions,
` R = 3628800`): one watch_compile, #100e4 x4, then flush/6 with
#100e4.  (The arguments printed are 0-3 and 5; #1011e is also the
functor of the flush(Done) message, as the predicate's name.)  So
fact's own compile is normal; the file's status is abnormal as soon as
top's is (dstrbt.kl1:89-121, wait_done and check_status: the first abnormal status
binds it, before the later modules are done, which is why flush/6 is
entered before fact's watch_compile), and flush/6 takes its `otherwise` clause:
report_total_error only, no flush_0, so neither the loader table's
flush (registration) nor relink runs.  docs/binary_reverse_engineering.md
1.4, "R8, the other four".
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lockstep_shell as ls  # noqa: E402
import longrun_ipl as L  # noqa: E402
import pimm  # noqa: E402

TYPED = ['compile', '!package work', 'fact_pub', '!exit', 'listener', 'default_package(work).',
         'fact:fact(10,R).']
CONTROL = ['compile', '!package work', 'fact_r8', '!exit', 'listener', 'default_package(work).',
           'fact:fact(10,R).']


class Null:
    def write(self, s):
        pass


def watch(m):
    """print the arguments at each entry of a predicate of arity 17
    whose arguments 0-3 are atoms (watch_compile), or of arity 6 whose
    third argument is a list headed by a structure of the predicate's
    own name (flush/6, called with MESG = [flush(Done)|_])"""
    cells, seen, orig = m.cells, {}, m.event

    def ev(text):
        if text[0] == 'I':
            pc = int(text.split()[1])
            k = seen.get(pc)
            if k is None:
                k = None
                h, nm = cells[pc - 2], cells[pc - 4]
                if h[0] == pimm.PREDH and nm[0] & ~1 == pimm.ATOM and h[1] >> 24 in (17, 6):
                    k = (nm[1], h[1] >> 24)
                seen[pc] = k or False
            if k:
                args = [m.term(m.reg[i]) for i in range(6)]
                name = m.im.atom(k[0])
                if k[1] == 17 and all(isinstance(a, str) for a in args[:4]):
                    print('watch_compile? %s/17 at %d: %r' % (name, pc, args[:4] + args[5:]))
                # MESG = [flush(Done)|_]: pimm.term gives a list with an
                # unbound tail as ('|', car, cdr)
                elif k[1] == 6 and isinstance(args[0], str) and isinstance(args[2], tuple) \
                        and args[2][0] == '|' and isinstance(args[2][1], tuple) \
                        and args[2][1][0] == name:
                    print('flush? %s/6 at %d: St %r' % (name, pc, args[0]))
        orig(text)
    m.event = ev


def main():
    m, loaded, info, kind = ls.load(sys.argv[1])
    m.ahead = False
    L.HOME_FILES['fact_pub.kl1'] = (L.HOME_FILES['fact.kl1'][0], None, None, L.PKL1_HEAD,
                                    (('after', 5, ':- public top/0.'),
                                     ('after', 21, ':- public fact/2.')))
    for typed in (TYPED, CONTROL):
        pid = os.fork()
        if pid == 0:
            print('==', typed[2], flush=True)
            watch(m)
            log0 = len(m.fep.log)
            sink = ls.Sink(Null())
            _o, _e, stop, dev = ls.play(m, loaded, kind, list(typed), sink)
            print('%d instructions, %s; the answer %r' % (sink.instructions, stop,
                                                         [t for _d, t in dev.log[log0:]][-2]))
            sys.stdout.flush()
            os._exit(0)
        os.waitpid(pid, 0)


if __name__ == '__main__':
    main()
