#!/usr/bin/env python3
"""Lockstep from a saved machine: PIMOS on the Bluespec core, from the
end of the IPL's link or from the shell's prompt, through the lines
typed, compared line by line with the reference model.

    python3 ref/pimm/lockstep_shell.py make PKL DIR [--type LINE ...]
        DIR/heap.hex     the saved machine's heap, for the bench's memory
        DIR/script.hex   the RESTORE operations, then RUN and POLL as
                         longrun_ipl.py go() runs, then the device tape
        DIR/trace        the reference model's trace of that script
        DIR/want.json    its counts, the console, the stop
    sim_pimm_shell | python3 ref/pimm/lockstep_shell.py compare DIR
    python3 ref/pimm/lockstep_shell.py splices PKL [--type LINE ...]
        the reference alone: the merger's splices onto a non-empty list
    python3 ref/pimm/lockstep_shell.py apps PKL DIR [NAME ...]
        the commands past the shell (APPS below, or those named): PKL
        loaded once, DIR/heap.hex written once, then each command
        played from the prompt in a forked process of its own into
        DIR/NAME/checkpoint (run by bsv/run_pimm_apps.sh)

Run by bsv/run_pimm_shell.sh.  NOT part of run_tests.sh: the saved
machines are ~1.1 GB pickles that the IPL's link makes in 15-50 min
(longrun_ipl.py --reference --save), not kept in git.

PKL is either
  - the machine after the link (longrun_ipl.py --save FILE): the script
    then begins as go() does, a new variable BootInfo, the goals
    top:go_pimos1(Loaded, BootInfo) and ipl:make_boot_info(BootInfo)
    spawned (ARGC, SPAWN), and the device fep.py attached as go()
    attaches it; or
  - the machine at the shell's prompt (longrun_ipl.py --load FILE --go
    --fep --save-prompt FILE2): run dry after the login, the window's
    getl held by the device, one RECEIVE waiting in the SCSI box.

What of the saved machine is not in its memory is given to the core by
RESTORE operations, silently (driver.py): the heap pointer, new_atom's
counter, the clock (pimm.py steps, as ticks and the instructions since
the last one), the SCSI commands so far and the waiting commands (all
four of the box's state a saved machine can hold: the run queue, the
merger's lists and the current shoen are empty between runs, asserted
here).  The heap goes into the bench's memory as a file (PimmMem.bsv);
cells below the heap are the image's, unchanged (checked here).  The
argument and working registers are not given: a goal loads what it
reads, so their contents between runs are never read (if one were, the
traces would part).

The reference runs with Machine.ahead off (what only it has is
refused), unlike longrun_ipl.py's go(): the run is then what the core
must do too.  Its counts are the same as go()'s.

The device on the core is the tape (driver.py): the answers the
reference's fep.py gave, in order.  Fep.idle(), the scripted login and
the lines typed, is the reference's alone and is not an operation: it
changes only what the next POLL's answer is.

Pinned (PINNED below, measured on both models, bsv/run_pimm_shell.sh):
see bsv/README.md "The lockstep from a saved machine".

Observed injections (2026-11-24, from the prompt checkpoint made with
the login ID 1, before P-f3, shutdown / yes; each
RESTORE word of the script replaced by a silent SLOT 15):
  0 (heap pointer)  FAIL at line 4, instruction 0: M 77959241 / M 32768
  1, 2, 3 (new_atom's counter, the clock)  PASS: not caught.  The
    window runs no new_atom and nothing that reads the clock (each
    would write a register the trace shows: inferred, not counted)
  4 (SCSI command count)  FAIL at line 6231, instruction 718:
    R 11 0000000080 / R 11 0000000000
  31 (the waiting RECEIVE)  FAIL at line 1, instruction 0:
    B 7 1 0820004000 2 16384 / Q
The splice-order injection into PimmGBox (lockstep_merge.py's header)
fails the same run at line 8429.

Observed injections on the commands past the shell (2026-11-24, the
prompt checkpoint with the login ID 0, run_pimm_apps.sh KEEP=1; the
same SLOT 15 in place of the RESTORE word):
  echo_new_atom, 1  FAIL at line 25012, instruction 8124:
    R 8 0200012731 / R 8 0200010000
  echo_new_atom, 2 and 3  PASS (no clock read)
  compile_exit, 1  PASS (no new_atom)
  compile_exit, 2  FAIL at line 828137, instruction 234242:
    R 9 000007611f / R 9 000000022a
  compile_exit, 3  FAIL at the same line: R 9 000007611f / R 9 000007611e
  compile_missing, 2  FAIL at line 1484817, instruction 288608:
    R 9 000007619f / R 9 00000002aa
  compile_missing, 3  PASS, as predicted: the checkpoint is 236
    instructions past a tick, and the one system_timer read falls 357
    after a tick, so the core's late tick has come by then
Re-observed 2026-11-25 from R7L's prompt checkpoint (from instruction
8,595,408; 112 instructions past a tick, not 236), DROPPED re-pinned:
  echo_new_atom, 1  FAIL at line 27640, instruction 8124:
    R 8 0200012731 / R 8 0200010000
  echo_new_atom, 2 and 3; compile_exit, 1  PASS
  compile_exit, 2  FAIL at line 902215, instruction 235341:
    R 9 0000076135 / R 9 000000022c
  compile_exit, 3  PASS, as predicted: the read falls 264 after a tick,
    past the 112, so the core's late tick has come by then
  compile_missing, 2  FAIL at line 1568167, instruction 289707:
    R 9 00000761b6 / R 9 00000002ad
  compile_missing, 3  FAIL at the same line, as predicted (63 after a
    tick): R 9 00000761b6 / R 9 00000761b5, one tick short
  pwd, 16-26  as before (lines 1, 1, 1, 1, 1, 1, 12, 4, 4101-4103)
(bsv/README.md, "Which RESTOREs the commands check"; pinned in DROPPED
below, run by run_pimm_apps.sh INJECT=1 or --inject WORK.)
"""
import json
import os
import pickle
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', '..', 'asm'))
import driver  # noqa: E402
import fep as fepm  # noqa: E402
import pimm  # noqa: E402
import longrun_ipl as longrun  # noqa: E402
import lockstep_cons as cons  # noqa: E402

# (the saved machine, the lines typed) -> (trace lines, instructions),
# measured on both models 2026-11-24 (bsv/run_pimm_shell.sh), with the
# login ID 0 (fep.py LOGIN, P-f3; the link row was 20107047, 8766339
# with the ID 1, the prompt rows the same)
PINNED = {
    ('prompt', ('shutdown', 'yes')): (912901, 180147),
    ('prompt', ('cat <= file("pimos:pimos.groups")',)): (778956, 174057),
    ('link', ('shutdown', 'yes')): (20435590, 8775555),
    # the commands past the shell, APPS (bsv/run_pimm_apps.sh)
    ('prompt', ('pwd',)): (238706, 29867),
    ('prompt', ('echo("a b c")',)): (517878, 119086),
    ('prompt', ('echo([a,b,c])',)): (549572, 128432),
    ('prompt', ('echo(zorkqx)',)): (525706, 122214),
    ('prompt', ('usage(echo)',)): (559339, 134283),
    ('prompt', ('help',)): (340013, 36685),
    ('prompt', ('who',)): (594630, 148036),
    ('prompt', ('set hl=20', 'history')): (460085, 56133),
    ('prompt', ('rs', '')): (866760, 191871),
    ('prompt', ('versions',)): (640392, 114507),
    ('prompt', ('compile', '!exit')): (1108374, 256137),
    # 2026-11-25: compile_missing types sample2 (the old sample1 row's
    # counts, the same run but for the name); compile_sample1, the
    # primer's file served from the home directory
    ('prompt', ('compile', 'sample2', '!exit')): (1859522, 319530),
    ('prompt', ('compile', 'sample1', '!exit')): (4546925, 974813),
    # compile_work: the same file into the package work, loaded
    ('prompt', ('compile', '!package work', 'sample1', '!exit')): (4865583, 1009886),
    # R7L (2026-11-25), measured on both models from a prompt checkpoint
    # made with R7L's resource model (shoen records of 11 cells; every row
    # of APPS re-measured so, bsv/run_pimm_apps.sh): ts past set_timer's
    # alarm to its table; the Listener's sieve
    ('prompt', ('ts', '')): (705103, 160945),
    ('prompt', ('compile', '!package work', 'sample1', '!exit', 'listener',
                'default_package(work).', 'sample1:sieve([1,2,3],E,O).')): (7144906, 1575086),
    # R7P (2026-11-25), the pipe: measured on the reference
    # (docs/binary_reverse_engineering.md 1.4, "R7P, the pipe"), then on
    # both models by bsv/run_pimm_apps.sh
    ('prompt', ('echo("a b c") | lc',)): (1325831, 311242),
    ('prompt', ('echo("a b c") | cat | lc',)): (2123497, 501560),
    ('prompt', ('grep(":-") <= file("sample1.kl1") | lc => window("out")',)): (2038170, 465694),
    ('prompt', ('grep(":-") <= file("sample1.kl1") | lc',)): (957748, 286597),
    # R7 ls (2026-11-25): the home directory through 204 and 237, the
    # listing's form INFERENCE (fep.listing), on both models
    ('prompt', ('ls',)): (768488, 164287),
    # R7G (2026-11-25): gc, and r7g_gc.py's session, on both models
    # (the core's collector, bsv/PimmGcBox.bsv), the K lines included
    ('prompt', ('gc',)): (368543, 89179),
    ('prompt', ('gc', 'compile', '!package work', 'sample1', '!exit', 'gc', 'listener',
                'default_package(work).', 'sample1:sieve([1,2,3],E,O).')): (7880429, 1752873),
}
# The commands past the shell (2026-11-24; docs/binary_reverse_engineering.md
# 1.4, "Commands past the shell", has each against what the primers and
# the manual print): name -> (the lines typed at the prompt, the window's
# text after them as the reference model writes it: every putb of a
# window or string-I/O window, in order).  bsv/run_pimm_apps.sh runs
# them all on both models (measured 2026-11-24; the counts in PINNED)
APPS = {
    'pwd': (('pwd',),
        (' The value of task: directory is ">sys>user>pmpsi" . \n', 'Shell>> ')),
    'echo_string': (('echo("a b c")',),
        ('"a b c"\n', 'Shell>> ')),
    'echo_list': (('echo([a,b,c])',),
        ('[a,b,c]\n', 'Shell>> ')),
    'echo_new_atom': (('echo(zorkqx)',),
        ('zorkqx\n', 'Shell>> ')),
    'usage_echo': (('usage(echo)',),
        ('Usage : echo(Data)\n', 'Shell>> ')),
    'help': (('help',),
        (' stop | stop JobNo\n kill , kill JobNo , kill all ,\n fore , fore JobNo ,\n back , back JobNo ,\n status  ,  exit  ,  help ,\n history [ N ] ,\n  ( N must be a positive integer. ) ,\n last_error , inspect ,\n alias Key [ = Value ] , unalias Key , alias ,\n  ( Key must be a atom. ) ,\n  ( Value must be a string. ) ,\n cd Directory , popd , dirs ,\n pushd [ Directory | Number ] ,\n take FileName ,\n do [ CmdLine1, CmdLine2, ... ] ,\n  ( Each CmdLine must be a string. ) ,\n\n getenv , getenv Key ,\n unsete', 'nv Key ,\n setenv Key = Value ,\n\n get , get Key ,\n unset Key ,\n  ( Key = rscinc | rscinc(JobNo) | prompt | echo\n          | node | minprio | maxprio | hl\n          | pl | pd | pal | psl | dir )\n set Key = Value ,\n    rscinc = Inc | rscinc(JobNo) = Inc\n      ( Inc = N | {High, Low} | infinite )\n      ( 1000000000 >= N, High, Low > 0 )\n  | prompt = Prompt\n  | echo = on | off\n  | node = NodeNo      ( NodeNo > 0 )\n  | minprio = Min | maxprio = Max\n      ( 4000 >= Min, Max > 0 )\n  | hl = Len', 'gth\n      ( Length >= 0  |  Length = infinite )\n  | pl = Length      | pd = Depth\n  | pal = Length     | psl = Length\n      ( Length >= 0  ,  Depth >= 0 )\n', 'Shell>> ')),
    'who': (('who',),
        ('pimos:  0  20-May-1993  00:00:30  0  0  pmpsi  local  \n', 'Shell>> ')),
    'history': (('set hl=20', 'history'),
        (' The value of hl is 20 .\n', 'Shell>> ', '  4 : history \n', 'Shell>> ')),
    # R7L (2026-11-25): from the checkpoint made with R7L's resource model
    # the shell's task is resource 10 (was 9) and its first atom 7 (was
    # 5): the IDs are given in the order the resources are registered,
    # and the boot to the prompt now registers two more before them (the
    # same 10 in ts's table); the tree is otherwise the same
    'rs': (('rs', ''),
        ('+-----+-------+-------+\n|RscID|RscType|RscName|\n+-----+-------+-------+\n10 , task , "shell:shell" \n   1 , std_switch , "inOutInter" \n   2 , in_out_inter , "inOutInter" \n   7 , atom , "atom" \n   26 , atom , "atom" \n   28 , task , "Job_1" \n      1 , std_switch , "inOutInter" \n      6 , atom , "atom" \n      9 , task , "rs:go" \n         1 , std_switch , "inOutInter" \n         3 , in_out_inter , "inOutInter" \n         7 , atom , "atom" \n         11 , atom , "atom" \n      10 , in_out_inter ,', ' "inOutInter" \n', 'OK? ', 'Shell>> ')),
    'versions': (('versions',),
        (' Module not found !! ( versions:go ) \n  [ Job#1, Node#0, PE#0 ]\n', 'Shell>> ', ' Job 1 was aborted . \n')),
    'compile_exit': (('compile', '!exit'),
        ('** KL1 Compiler **\n', 'COMPILE> ', 'Shell>> ')),
    # (2026-11-25: sample1 is now a home file, longrun_ipl.HOME_FILES, so
    # the missing file is the primer's sample2, which the home lacks)
    'compile_missing': (('compile', 'sample2', '!exit'),
        ('** KL1 Compiler **\n', 'COMPILE> ', '!ERROR! unable to open file : sample2\n', 'Total Number of Error : 1\n', 'COMPILE> ', 'Shell>> ')),
    # the primer's sample1 (primer25.tex:592-605) from the home
    # directory (longrun_ipl.home_file), R7; the whole compile since
    # 2026-11-25 (docs/binary_reverse_engineering.md 1.4, "R7, the
    # compile against the primer": the registration error is PIMOS's
    # protection for the login user pimos)
    'compile_sample1': (('compile', 'sample1', '!exit'),
        ('** KL1 Compiler **\n', 'COMPILE> ',
         'Compile File : PSI::>sys>user>pmpsi>sample1.kl1.1\n',
         "!WARNING! no with_macro declaraion. assumed `pimos'.\n[sample1.kl1@0] Compile Module : sample1\n",
         '=>  :- module sample1 .\n',
         'Compile Succeeded : sample1\n\n',
         '!ERROR! module registration error : pimos:: sample1\n',
         'Total Number of Warning : 1\nTotal Number of Error : 1\n',
         'COMPILE> ', 'Shell>> ')),
    # the same into the package `work` (the compiler's `!package`,
    # pimosman e-compiler.tex:437-440): the module is loaded, as the
    # primer's `"nak::sample1" Loaded` (primer25.tex:1297); r7_sieve.py
    # runs it
    'compile_work': (('compile', '!package work', 'sample1', '!exit'),
        ('** KL1 Compiler **\n', 'COMPILE> ',
         'Package : work\n!WARNING! not included in the working packages : work\n',
         'COMPILE> ',
         'Compile File : PSI::>sys>user>pmpsi>sample1.kl1.1\n',
         "!WARNING! no with_macro declaraion. assumed `pimos'.\n[sample1.kl1@0] Compile Module : sample1\n",
         '=>  :- module sample1 .\n',
         'Compile Succeeded : sample1\n\n',
         '"work:: sample1" Loaded\n',
         'Total Number of Warning : 1\n',
         'COMPILE> ', 'Shell>> ')),
    # `ts` (2026-11-25): past add_bignum, then (R7L) past set_timer to a
    # time still to come, the alarm (pimm.py i_set_timer, fire_alarm;
    # bsv/PimmTBox.bsv): the task table after on_after(10000)
    # (kernel/task/int_hdl.kl1:39-88), then its `OK? `, answered by
    # the empty line typed
    'ts': (('ts', ''),
        ('+------+--------+------+--------+-----------+\n|TaskID|TaskName|Status|RscLimit|ConsumedRsc|\n+------+--------+------+--------+-----------+\n10 , "shell:shell" , running,2000000000,14668\n   28 , "Job_1" , running,1000000000,1720\n      9 , "ts:go" , running,2000000000,2324\n',
         'OK? ', 'Shell>> ')),
    # R7L (2026-11-25): the Listener, and in it the primer's goal
    # sample1:sieve([1,2,3],E,O) (primer25.tex:1343-1349), compiled into
    # work as compile_work, the Listener told so by its own
    # default_package(work). (pimosman e-listener.tex:2508-2522).  The
    # answer is ` E =[2]` where the primer prints `E = [2]`: the held
    # unparser puts a space between a variable and a special atom and
    # none after `=` before `[` (utility/ioutls/uparse.kl1:573-604,
    # checkQuote), and the Listener prints the vector {=, variable(K),
    # WT} with it (debugger/listener/buffer.kl1:97-106): the held
    # source's text, not a slip of the model
    'listener_sieve': (('compile', '!package work', 'sample1', '!exit', 'listener',
                        'default_package(work).', 'sample1:sieve([1,2,3],E,O).'),
        ('** KL1 Compiler **\n', 'COMPILE> ',
         'Package : work\n!WARNING! not included in the working packages : work\n',
         'COMPILE> ',
         'Compile File : PSI::>sys>user>pmpsi>sample1.kl1.1\n',
         "!WARNING! no with_macro declaraion. assumed `pimos'.\n[sample1.kl1@0] Compile Module : sample1\n",
         '=>  :- module sample1 .\n',
         'Compile Succeeded : sample1\n\n',
         '"work:: sample1" Loaded\n',
         'Total Number of Warning : 1\n',
         'COMPILE> ', 'Shell>> ',
         '*** KL1 LISTENER (V 3.600 20-May-93) ***\nDEFAULT PACKAGE   : pimos\nCURRENT DIRECTORY : >sys>user>pmpsi\n\n',
         '[1] ', '\n', '[2] ', ' E =[2]\n O =[1,3]\n\n', '[3] ')),
    # R7P (2026-11-25), the pipe (pimosman e-shell.tex:140-227, the
    # grammar and its examples; docs/binary_reverse_engineering.md 1.4,
    # "R7P, the pipe").  The manual's Example 1 form `a | b`: lc
    # (shell/utils/lc.kl1) counts the one line echo writes
    'pipe_echo': (('echo("a b c") | lc',),
        ('$$$ Line = 1 $$$\n', 'Shell>> ')),
    # three stages, so tos.kl1's createMed (55-68) is run: cat passes
    # the line on
    'pipe_three': (('echo("a b c") | cat | lc',),
        ('$$$ Line = 1 $$$\n', 'Shell>> ')),
    # the primer's pipe (primer25.tex:1879) in the manual's job form
    # `a <= in | b => out` (e-shell.tex:227): grep(":-") reads the
    # primer's sample1.kl1 (the home file, longrun_ipl.HOME_FILES) and
    # lc counts its lines with ":-": 5, the count of the primer's text
    # (primer25.tex:592-605: the module and public declarations and
    # the three clause heads).  lc's output goes to the window "out"
    # (fep.py's window device; the text is its putb)
    'pipe_grep': (('grep(":-") <= file("sample1.kl1") | lc => window("out")',),
        ('$$$ Line = 5 $$$\n', 'Shell>> ')),
    # the primer's line as printed: the held PIMOS fails it.  The job
    # has `<=` and no `=>`, so its stdio is {in, out_inter}, served by
    # task_std_handler:in_outInter, whose make_branch(out_inter) answers
    # `out` (kernel/stdio/stdhdl.kl1:299-305; the linked binary agrees,
    # task_std_handler cell 1567 write_atom out); lc's vector is then
    # {in, out, *} and task_stdio:invoke_std_handler/3 has no clause for
    # it (kernel/stdio/std.kl1:281-296): a reduction failure, then the
    # run dry, lc's get_std raises unanswered.  Nothing written.
    # ref/pimm/r7p_pipe.py changes that one atom on the reference and
    # the same line counts 5
    'pipe_primer': (('grep(":-") <= file("sample1.kl1") | lc',),
        ()),
    # R7 ls (2026-11-25): ls.kl1 opens the directory (204), lists "*.*"
    # (237) and prints each entry with its directory in front (shell/
    # utils/pathname.kl1 loop/5), one a line.  The FEP's answer is
    # INFERENCE from that reader (fep.listing: entries LF-ended, a file
    # with its version), so the line is ours too: the primer prints no
    # ls.  The home has the one file, sample1.kl1.  Injection (OBSERVED
    # 2026-11-25): home_listing without the version (".1") gives
    # ' >sys>user>pmpsi>sample1.kl1>' (taken for a directory) and the
    # counts (768817, 164311): FAIL against this row and PINNED
    'ls': (('ls',),
        (' >sys>user>pmpsi>sample1.kl1.1\n', 'Shell>> ')),
    # R7G (2026-11-25): the shell's gc (shell/utils/gc.kl1 go/0:
    # collect_garbage on each processor; nothing written), then the
    # collection at the next goal switch on both models, INFERENCE/OURS
    # (ref/pimm/pimm_gc.py, bsv/PimmGcBox.bsv): one line
    # `K gc 32768 77892213 77892213 79768684 a8652141`.  gc_listener is
    # ref/pimm/r7g_gc.py's session: a second K line, `K gc 77892213
    # 82173730 32768 2452104 638807af`, back to the heap's base.
    # Injections in PimmGcBox.bsv, OBSERVED on gc (each FAIL at the line
    # given, every line before it identical): the links pass clearing
    # every link: line 198,832, the K line's checksum 0e81de44; a mixed
    # block's unbound variable not moved in: the same line, `... 79768686
    # 763810b1`; a waiting SCSI command's first variable not moved: line
    # 254,630, the core's `E error: scsi: a waiting command's variable
    # was not free` where the reference writes it
    'gc': (('gc',),
        ('Shell>> ',)),
    'gc_listener': (('gc', 'compile', '!package work', 'sample1', '!exit', 'gc', 'listener',
                     'default_package(work).', 'sample1:sieve([1,2,3],E,O).'),
        ('Shell>> ', '** KL1 Compiler **\n', 'COMPILE> ', 'Package : work\n!WARNING! not included in the working packages : work\n', 'COMPILE> ', 'Compile File : PSI::>sys>user>pmpsi>sample1.kl1.1\n', "!WARNING! no with_macro declaraion. assumed `pimos'.\n[sample1.kl1@0] Compile Module : sample1\n", '=>  :- module sample1 .\n', 'Compile Succeeded : sample1\n\n', '"work:: sample1" Loaded\n', 'Total Number of Warning : 1\n', 'COMPILE> ', 'Shell>> ', 'Shell>> ', '*** KL1 LISTENER (V 3.600 20-May-93) ***\nDEFAULT PACKAGE   : pimos\nCURRENT DIRECTORY : >sys>user>pmpsi\n\n', '[1] ', '\n', '[2] ', ' E =[2]\n O =[1,3]\n\n', '[3] ')),
}
POISON = (0xff, 0xdeadbeef)     # a heap cell the saved machine never wrote
T0 = time.time()


def say(text):
    print('%6.0fs %s' % (time.time() - T0, text), file=sys.stderr, flush=True)


class Sink:
    """The reference's trace, to a file; the console's lines kept, the
    instructions counted."""

    def __init__(self, f):
        self.f = f
        self.lines = 0
        self.instructions = 0
        self.kept = []

    def append(self, line):
        self.f.write(line)
        self.f.write('\n')
        self.lines += 1
        c = line[0]
        if c == 'I':
            self.instructions += 1
        elif c in 'CS':
            self.kept.append(line)


def load(path):
    with open(path, 'rb') as f:
        m, loaded, info = pickle.load(f)
    say('loaded %s' % path)
    return m, loaded, info, ('prompt' if 'prompt' in info else 'link')


def typed(argv):
    return [argv[i + 1] for i, a in enumerate(argv) if a == '--type']


def write_heap(m, path):
    """The heap, heap's first cell to hp, as the bench's memory loads
    it: one addressed block, a cell never written given POISON."""
    base = m.load + pimm.HEAP
    mem = m.mem
    n = len(m.cells)
    for i in range(pimm.HEAP):
        assert (mem.get(m.load + i) == list.__getitem__(m.cells, i)) if i < n \
            else m.load + i not in mem, 'a cell below the heap is not the image\'s: %d' % i
    gaps = 0
    with open(path, 'w') as f:
        f.write('@%x\n' % pimm.HEAP)
        chunk = []
        for a in range(base, m.hp):
            c = mem.get(a)
            if c is None:
                c = POISON
                gaps += 1
            chunk.append('%02x%08x\n' % c)
            if len(chunk) >= 1 << 16:
                f.write(''.join(chunk))
                chunk = []
        f.write(''.join(chunk))
    say('heap written: %d cells, %d never written' % (m.hp - base, gaps))
    return gaps


def restore_ops(m):
    """The RESTORE operations for what of m is not in its memory."""
    assert m.rq == 0 and m.mq == 0 and m.mwh == 0 and m.mwt == 0 and m.shoen == 0, \
        'the saved machine is not between runs'
    # R7L: no RESTORE carries an alarm (pimm.py alarm_var) or a moved
    # clock; until R7L set_timer to a time still to come was refused, so
    # no saved machine has one
    assert m.alarm_var is None and m.tick_skip == 0, 'the saved machine has an alarm armed'
    # R7G: no RESTORE carries the heap's moved start (pimm_gc.py heap_lo;
    # PimmGcBox's lo starts at the heap's first cell) or a request
    assert not getattr(m, 'heap_lo', None) and not m.gc_request, \
        'the saved machine was collected (R7G): not restorable'
    ops = []

    def R(which, cell):
        ops.append((driver.RESTORE, which, 0, cell))
    R(0, (0, m.hp & pimm.M32))
    R(1, (0, m.next_atom))
    R(2, (0, m.steps // pimm.INSTRUCTIONS_PER_TICK))
    R(3, (0, m.steps % pimm.INSTRUCTIONS_PER_TICK))
    R(4, (0, m.scsi_commands & pimm.M32))
    for c in m.scsi_waiting:
        for which, cell in ((16, (pimm.INT, c['unit'] & pimm.M32)),
                            (17, (pimm.INT, c['lun'] & pimm.M32)),
                            (18, (pimm.INT, c['dir'] & pimm.M32)),
                            (19, (pimm.INT, c['length'] & pimm.M32)),
                            (20, c['cdbw']), (21, (0, len(c['cdb']))),
                            (22, c['word']), (23, (0, len(c['buf']))),
                            (24, c['outs'][0]), (25, c['outs'][1]), (26, c['outs'][2])):
            R(which, cell)
        R(31, (0, 0))
    return ops


def splice_counter(m, stats):
    """Count the merger's splices (pimm.py pick: the goals made ready
    since the last pickup put in front of the merger's list), and those
    onto a list that is not empty."""
    pick = m.pick

    def counted():
        if m.mwh:
            stats['splices'] += 1
            if m.mq:
                stats['onto_nonempty'] += 1
        return pick()
    m.pick = counted


def play(m, loaded, kind, lines, sink, stats=None):
    """The script, performed on the reference as it is made: go()'s
    loop, as bench operations.  Returns (ops, events, stop)."""
    ops = restore_ops(m)
    slot = [(0, 0)] * 16
    outs = []

    def op(o):
        ops.append(o)
        driver.Script._do(m, slot, o, outs, '')
    m.tr = sink
    if stats is not None:
        splice_counter(m, stats)
    im = m.im
    if kind == 'link':
        assert not m.scsi_waiting and m.fep is None
        op((driver.NEWVAR, 0, 0, (0, 0)))
        boot = slot[0]
        op((driver.ARGC, 1, 0, pimm.marked(loaded)))
        op((driver.ARGC, 2, 0, pimm.marked(boot)))
        op((driver.SPAWN, 2, 0, (0, pimm.predicate(im, 'top', 'go_pimos1/2'))))
        op((driver.ARGC, 1, 0, boot))
        op((driver.SPAWN, 1, 0, (0, pimm.predicate(im, 'ipl', 'make_boot_info/1'))))
        dev = m.fep = fepm.Fep(longrun.kernel_file, getb_unit=2, lines=lines,
                               list_dir=longrun.home_listing)
    else:
        dev = m.fep
        dev.open_file = longrun.kernel_file
        dev.list_dir = longrun.home_listing     # R7, ls (a machine saved before it has none)
        dev.script = [('getl', line) for line in lines]
    events = []
    stop = None
    skips = 0
    try:
        while True:
            ops.append((driver.RUN, 0, 0, (0, 0)))
            try:
                m.run(limit=10 ** 12)
            except pimm.Suspend:
                pass
            ops.append((driver.POLL, 0, 0, (0, 0)))
            if m.scsi_poll():
                skips = 0
                continue
            # R7L: an alarm armed, the clock moved on to it (driver
            # ALARM) before a typed line is given: the SCSI device
            # first, then time, then the keyboard.  An alarm armed again
            # and again with nothing else happening would starve the
            # keyboard: refused after 100
            if m.alarm_var is not None:
                skips += 1
                if skips > 100:
                    raise pimm.Unimplemented('100 alarms in a row with nothing else to do')
                ops.append((driver.ALARM, 0, 0, (0, 0)))
                m.alarm_skip()
                continue
            skips = 0
            if not dev.idle():
                break
            events.append(sink.instructions)
            say('fep: a scripted event at %d instructions' % sink.instructions)
        stop = 'nothing left to run, %d goals waiting' % m.nsusp
    except pimm.Unimplemented as e:
        stop = 'refused: %s' % e
    except pimm.Fail as e:
        stop = 'Fail %s' % e
    except fepm.FepError as e:
        stop = 'FepError: %s' % e
    return ops, events, stop, dev


def record(m, loaded, kind, lines, out, before, gaps):
    """Play the lines on m and write the window's files to out: the
    reference's trace, the script and want.json (heap.hex apart)."""
    os.makedirs(out, exist_ok=True)
    tape0 = len(m.scsi_tape)
    log0 = len(m.fep.log) if m.fep is not None else 0
    stats = dict(splices=0, onto_nonempty=0)
    with open(os.path.join(out, 'trace'), 'w', buffering=1 << 22) as f:
        sink = Sink(f)
        ops, events, stop, dev = play(m, loaded, kind, lines, sink, stats)
    s = driver.Script()
    s.ops = ops
    s.write(os.path.join(out, 'script.hex'), m.scsi_tape[tape0:])
    want = dict(kind=kind, typed=lines, lines=sink.lines, instructions=sink.instructions,
                from_instruction=before, to_instruction=before + sink.instructions,
                operations=len(ops), tape=len(m.scsi_tape) - tape0, events=events,
                console=cons.console(sink.kept), stop=stop, heap_gaps=gaps,
                fep_messages=len(dev.messages), held=dev.held,
                window=[t for _d, t in dev.log[log0:]], **stats)
    with open(os.path.join(out, 'want.json'), 'w') as f:
        json.dump(want, f, indent=1, default=str)
    say('made: %r' % (want,))
    return want


def make(argv):
    pkl, out = argv[2], argv[3]
    lines = typed(argv)
    os.makedirs(out, exist_ok=True)
    m, loaded, info, kind = load(pkl)
    m.ahead = '--ahead' in argv
    gaps = write_heap(m, os.path.join(out, 'heap.hex'))
    before = info.get('prompt', {}).get('instructions', 0)
    record(m, loaded, kind, lines, out, before, gaps)
    return 0


def apps(argv):
    """apps PKL DIR [NAME ...]: the prompt checkpoint loaded once, its
    heap written once (DIR/heap.hex), then each command of APPS (or
    those named) played from it in a process of its own (fork), its
    files in DIR/NAME/checkpoint/ with heap.hex linked."""
    pkl, out = argv[2], argv[3]
    names = argv[4:] or list(APPS)
    for n in names:
        if n not in APPS:
            raise SystemExit('lockstep_shell: no command %r in APPS' % n)
    os.makedirs(out, exist_ok=True)
    m, loaded, info, kind = load(pkl)
    if kind != 'prompt':
        raise SystemExit('lockstep_shell: apps runs from a prompt checkpoint')
    m.ahead = False
    gaps = write_heap(m, os.path.join(out, 'heap.hex'))
    before = info['prompt']['instructions']
    bad = 0
    for n in names:
        d = os.path.join(out, n, 'checkpoint')
        pid = os.fork()
        if pid == 0:
            try:
                record(m, loaded, kind, list(APPS[n][0]), d, before, gaps)
                os.symlink(os.path.join('..', '..', 'heap.hex'), os.path.join(d, 'heap.hex'))
            finally:
                os._exit(0 if os.path.exists(os.path.join(d, 'heap.hex')) else 1)
        _p, st = os.waitpid(pid, 0)
        bad += st != 0
    return 1 if bad else 0


def compare(argv):
    d = argv[2]
    with open(os.path.join(d, 'want.json')) as f:
        want = json.load(f)
    name = 'pimm lockstep shell (%s, %s)' % (want['kind'], ' / '.join(want['typed']) or 'nothing typed')
    got = sys.stdin
    first = got.readline()
    while first.startswith('Warning: file'):
        first = got.readline()
    n = ins = 0
    recent = []
    with open(os.path.join(d, 'trace')) as f:
        for w in f:
            g = first if n == 0 else got.readline()
            if g != w:
                print('%s: FAIL at line %d of the trace, instruction %d after the checkpoint'
                      % (name, n, ins))
                print('  reference: %s' % w.rstrip('\n'))
                print('  bluespec:  %s' % (g.rstrip('\n') or '(end of trace)'))
                for prev in recent:
                    print('  after:     %s' % prev)
                return 1
            if w[0] == 'I':
                ins += 1
            recent = (recent + [w.rstrip('\n')])[-6:]
            n += 1
    extra = got.readline() if n else first
    if extra and not (extra.strip() == 'E unimp' and want['stop'].startswith('refused')
                      and not got.readline()):
        # (2026-11-25) a run the reference ends refusing (Unimplemented,
        # no trace line) passes only if the core ends there refusing
        # too, its one last line `E unimp`
        print('%s: FAIL, the Bluespec trace goes on: %s' % (name, extra.strip()))
        return 1
    if n != want['lines'] or ins != want['instructions']:
        print('%s: FAIL, %d lines, %d instructions; the reference made %d, %d'
              % (name, n, ins, want['lines'], want['instructions']))
        return 1
    pin = PINNED.get((want['kind'], tuple(want['typed'])))
    if pin is not None and pin != (n, ins):
        print('%s: FAIL, %d lines, %d instructions, pinned %r' % (name, n, ins, pin))
        return 1
    app = [k for k, (t, _w) in APPS.items() if tuple(t) == tuple(want['typed'])]
    if want['kind'] == 'prompt' and app and APPS[app[0]][1] is not None \
            and want.get('window') != list(APPS[app[0]][1]):
        print('%s: FAIL, the window %r; APPS %r has %r'
              % (name, want.get('window'), app[0], APPS[app[0]][1]))
        return 1
    print('%s: PASS (instructions %d to %d of go(), %d trace lines identical to the reference '
          'model; console %r; window %r; %s; %.0f s to the compare%s)'
          % (name, want['from_instruction'], want['to_instruction'], n, want['console'],
             want.get('window'), want['stop'], time.time() - T0, '' if pin else '; NOT PINNED'))
    return 0


def splices(argv):
    m, loaded, info, kind = load(argv[2])
    stats = dict(splices=0, onto_nonempty=0)

    class Count(Sink):
        def append(self, line):
            if line[0] == 'I':
                self.instructions += 1
    ops, events, stop, dev = play(m, loaded, kind, typed(argv), Count(None), stats)
    print(kind, stats, stop)
    return 0


# The RESTORE injections on the commands past the shell (bsv/README.md,
# "Which RESTOREs the commands check"): (APPS name, RESTORE number) ->
# the trace line the compare fails at with that RESTORE dropped, or
# None for a PASS (not caught; compile_exit's 3 is the control the
# clock's phase predicts, R7L checkpoint 2026-11-25).  run_pimm_apps.sh with INJECT=1 runs them
DROPPED = {
    ('echo_new_atom', 1): 27640, ('echo_new_atom', 2): None, ('echo_new_atom', 3): None,
    ('compile_exit', 1): None, ('compile_exit', 2): 902215, ('compile_exit', 3): None,
    ('compile_missing', 2): 1568167, ('compile_missing', 3): 1568167,
    # the waiting command's fields, 2026-11-25 (bsv/README.md)
    # (the one waiting: unit 7, lun 1, a 5-byte cdb, dir 2, 16384
    # bytes); every one caught, measured 2026-11-25
    ('pwd', 16): 1, ('pwd', 17): 1, ('pwd', 18): 1, ('pwd', 19): 1,
    ('pwd', 20): 1, ('pwd', 21): 1, ('pwd', 22): 12, ('pwd', 23): 4,
    ('pwd', 24): 4101, ('pwd', 25): 4102, ('pwd', 26): 4103,
}


def drop(argv):
    """drop WHICH SRC DST: SRC's first RESTORE of register WHICH (the
    script word 10WW...) replaced by a silent SLOT 15 of the same
    length, so the tape's offset holds"""
    which, src, dst = int(argv[2]), argv[3], argv[4]
    with open(src) as f:
        lines = f.read().split('\n')
    hit = [i for i, w in enumerate(lines) if w.startswith('10%02x' % which)]
    if not hit:
        print('drop: no RESTORE %d in %s' % (which, src))
        return 1
    lines[hit[0]] = '0c0f000000000000'
    with open(dst, 'w') as f:
        f.write('\n'.join(lines))
    return 0


def dropped(argv):
    """dropped NAME WHICH: the start of what the compare must print"""
    want = DROPPED[(argv[2], int(argv[3]))]
    print('PASS' if want is None else 'FAIL at line %d of the trace' % want)
    return 0


def drops(argv):
    """drops [NAME ...]: the pairs of DROPPED, 'NAME WHICH' a line"""
    for (name, which) in DROPPED:
        if len(argv) <= 2 or name in argv[2:]:
            print(name, which)
    return 0


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else ''
    if cmd == 'make':
        sys.exit(make(sys.argv))
    if cmd == 'compare':
        sys.exit(compare(sys.argv))
    if cmd == 'splices':
        sys.exit(splices(sys.argv))
    if cmd == 'apps':
        sys.exit(apps(sys.argv))
    if cmd in ('drop', 'dropped', 'drops'):
        sys.exit(globals()[cmd](sys.argv))
    print(__doc__)
    sys.exit(2)
