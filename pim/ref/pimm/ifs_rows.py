"""The rows of ref/pimm/ifs_sweep.py: one per held IFS PIMOS archive
(43, plus Distributed Pool's PIMOS archive and AITEC's H9-07, which hold
PIMOS objects), how its documentation says to run it, what it printed,
and PINNED, the outcome observed.  The evidence for each row (file:line
in the archive) is docs/ifs_apps.md.

A row's keys: no (the catalogue number, icot_software_survey.md 3),
archive (under docs/nonlocal/ifs), doc (where the procedure is), serve
(regex over member names, and where to serve: None flat in HOME, 'DIR/'
the tree below DIR as HOME>A>B, '>sys>user>X>' flat in that directory),
typed (the lines, at the shell's prompt; `listener` first where the
documentation types at the Listener), printed (value, citation), needs
('simpos' / 'other': the outcome rule of ifs_sweep.CLASSIFY), budget
(instructions), static (outcome, first stop) for a row not run, and
note.  `{KL1}` in a typed line is the served .kl1 files' names, sorted,
quoted and comma-separated (OURS: for a package whose documentation
says only "compile all the .kl1 files").
"""

SIMPOS_BUDGET = 60_000_000   # the KL1 half tried: enough to see its compile through or stop

# The prompt checkpoint's login task package is pimos (the Listener:
# "DEFAULT PACKAGE : pimos"), and PIMOS refuses to register a user's
# module there: loading pia_s2.exe as is gave `module registration error
# : pimos:: ...` for every module and `Load Failed` (OBSERVED 2026-11-26).
# A user's login would have had its own package; rows that load objects
# first set the task package to work, R8's and R9's package (OURS).
WORK = 'setenv task:package=work'

# name -> (outcome, the first stop's beginning): OBSERVED, see ifs_apps.md
PINNED = {
    'mgtp': ('RUNS-DIFFERS', '-'),
    'mgtp_tarZ': ('RUNS-DIFFERS', '- (code identical to mgtp.tgz: row mgtp)'),
    'mgtp_n': ('STOPS', 'model: enqueue_goal_to_processor '),
    'h907_nseq': ('STOPS', 'model: set_heap_alert at N'),
    'h907_nseq+alt': ('STOPS', 'model: wait_value of a variable with itself'),
    'h907_nogc': ('STOPS', 'model: wait_value of a variable with itself'),
    'h907_shell': ('STOPS', 'model: enqueue_goal_to_processor '),
    'aya': ('STOPS', 'missing: !ERROR! unable to open file : ayaparse'),
    'aya+alt': ('STOPS', 'model: wait_value of a variable with itself'),
    'gdcc': ('STOPS', 'compile: [12] *** Syntax Error ***'),
    'laputa': ('BUDGET', 'budget'),
    'multialign': ('RUNS-NO-ORACLE', '-'),
    'multialign+alt': ('RUNS-NO-ORACLE', '-'),
    'multialign_run': ('STOPS', 'model: enqueue_goal_to_processor '),
    'dpool': ('STOPS', 'model: clause_info at N'),
    'ldlib': ('STOPS', 'model: wait_value of a variable with itself'),
    'ldlib+alt': ('STOPS', 'model: wait_value of a variable with itself'),
    'ppss': ('BUDGET', 'budget'),
    'colodex': ('BUDGET', 'budget'),
    'colodex+alt': ('BUDGET', 'budget'),
    'mmi': ('STOPS', 'model: enqueue_goal_to_processor '),
    'rodin': ('BUDGET', 'budget'),
    'rodin+alt': ('STOPS', 'memory: the heap full'),
    'dulcinea': ('STOPS', 'model: a goal failed inside a shoen'),
    'dulcinea+alt': ('STOPS', 'model: a goal failed inside a shoen'),
    'aligndp': ('NEEDS-SIMPOS', 'budget'),
    'alignsa': ('NEEDS-SIMPOS', 'budget'),
    'cbcdss': ('NEEDS-SIMPOS', 'budget'),
    'celplace': ('NEEDS-SIMPOS', 'budget'),
    'cohlex': ('NEEDS-SIMPOS', 'model: a goal failed inside a shoen'),
    'consort': ('NEEDS-SIMPOS', 'fep: FepError: device N: request [221]'),
    'consort+alt': ('NEEDS-SIMPOS', 'fep: FepError: device N: request [221]'),
    'desq': ('NEEDS-SIMPOS', 'fep: FepError: device N: request [221]'),
    'desq+alt': ('NEEDS-SIMPOS', 'fep: FepError: device N: request [221]'),
    'examds': ('NEEDS-SIMPOS', 'budget'),
    'gog_kl1': ('NEEDS-SIMPOS', 'budget'),
    'gog_kl1+alt': ('NEEDS-SIMPOS', 'budget'),
    'gpsstap': ('NEEDS-SIMPOS', 'budget'),
    'logisim': ('NEEDS-SIMPOS', 'budget'),
    'logisim+alt': ('NEEDS-SIMPOS', 'budget'),
    'lsirout': ('NEEDS-SIMPOS', 'budget'),
    'mendels': ('NEEDS-SIMPOS', '-'),
    'pmonitor': ('NEEDS-SIMPOS', 'missing: !ERROR! unable to open file : chart_ctl'),
    'pmonitor+alt': ('NEEDS-SIMPOS', 'missing: !ERROR! unable to open file : chart_ctl'),
    'seqanal': ('NEEDS-SIMPOS', 'budget'),
    'seqanal+alt': ('NEEDS-SIMPOS', 'budget'),
    'sme': ('NEEDS-SIMPOS', 'budget'),
    'exreps': ('NEEDS-SIMPOS', 'budget'),
    'kl1graph': ('NEEDS-SIMPOS', 'budget'),
    'strtgysh': ('NEEDS-SIMPOS', 'budget'),
    'argus_v': ('NEEDS-SIMPOS', 'budget'),
    'voronoi': ('NEEDS-SIMPOS', 'budget'),
    'kappa_p': ('NEEDS-SIMPOS', 'budget'),
    'objects': ('RUNS-NO-ORACLE', '-'),
    'editalign': ('NEEDS-OTHER', 'fep: FepError: device N: request [801]'),
    'editalign+alt': ('NEEDS-OTHER', 'fep: FepError: device N: request [801]'),
    'mssd': ('NEEDS-OTHER', 'model: wait_value of a variable with itself'),
    'quixote': ('NEEDS-OTHER', 'other: a UNIX client '),
    'qxt_motif': ('NEEDS-OTHER', 'other: Quixote Ver.III '),
    'robot': ('NEEDS-OTHER', 'other: GDCC source only '),
    'p_chal': ('NEEDS-OTHER', 'other: GDCC v2.5 programs '),
    'pax': ('NEEDS-SIMPOS', 'simpos: the DCG-to-KL1 translator is ESP '),
    'helic2': ('NEEDS-OTHER', 'damaged: about 390 of the 590 files README lists are missing '),
}


def _pia_query(archive):
    """DOC.pia:27-60, the query as printed, `%` comments dropped, joined"""
    import re

    lines = archive('exper-apps/pimos/multialign.tar.Z')['DOC.pia'].decode('latin-1').split('\n')
    q = lines[26:60]
    assert q[0].startswith('[8] pia_s2:top(') and q[-1] == ').', (q[0], q[-1])
    q[0] = q[0][len('[8] '):]
    return ''.join(re.sub(r'%.*', '', x).strip() for x in q)


def _mgtp_typed():
    import lockstep_shell as ls
    return list(ls.APPS['mgtp_q6'][0])


# The second try, past the Listener's take (every take typed at the
# Listener stopped at set_constant, OBSERVED 2026-11-26; since the
# float merge added it, each +alt row meets its plain row's stop or the
# budget, but rodin+alt the heap limit and h907_nseq+alt its own,
# OBSERVED 2026-11-27): the command
# file's commands typed at the Listener one by one ({TAKE NAME},
# ifs_sweep.expand_take; a take inside expanded too), then the goals.
# OURS: the documentation has the Listener take the file.  (A first
# version took the files at the shell instead: the shell reads a
# command file line by line, so every command spread over lines is a
# `*** Syntax Error ***`, OBSERVED for ldlib, consort, rodin.)
# h907_nseq's file is shell syntax and runs at the shell; multialign's
# load.pia likewise (`Load Succeeded`, OBSERVED).
ALTS = {
    'h907_nseq': ['take("Nseq")', 'listener', 'compile("SYN002-1-020dom_merc.kl1").',
                  'load("mgtpNS7").', 'main:main(50,ns,A).'],
    'consort': ['listener', '{TAKE kl1_source>comp_4p.com}'],
    'desq': ['listener', '{TAKE kl1_source>comp_4p.com}'],
    'gog_kl1': ['listener', '{TAKE make.com}'],
    'logisim': ['listener', '{TAKE compile.com}'],
    'pmonitor': ['listener', '{TAKE pm_kl1.com}'],
    'seqanal': ['listener', '{TAKE cmpfiles}'],
    'ldlib': ['listener', '{TAKE Make.com}', 'compile_all.'],
    'colodex': ['listener', '{TAKE s.com}', 'test_ex:t.'],
    'multialign': [WORK, 'take"load.pia"'],
    'dulcinea': ['listener', '{TAKE install.com}'],
    'editalign': [WORK, 'listener', '{TAKE load.com}', 'dp_new:go.'],
}


def define_rows(row0, archive):
    def row(name, **kw):
        if name in ALTS:
            kw['alt'] = ALTS[name]
        if name in ('consort', 'desq'):
            # comp_4p.com:1 cd ">sys>user>desq": the files are served
            # below the home, so the cd is not typed (OURS)
            kw['drop'] = [r'^cd ']
        row0(name, **kw)
    S = SIMPOS_BUDGET
    # ================= KL1 alone, with a documented example ===========
    row('mgtp', no=22, archive='solver-prover/pimos/MGTP/mgtp.tgz',
        doc='mgtp/manualE.tex:86-128, 214-240',
        serve=[],       # R9's home files (longrun_ipl.HOME_FILES: mgtp.tgz, q6.clause)
        typed=_mgtp_typed(),
        printed=[(' 18759 reductions', 'manualE.tex:235 (MGTP/G/MERC, N=6)',
                  '\\mbox{MGTP/G/MERC} &      18759&')],
        note='R9 (lockstep_shell.APPS mgtp_q6): the 4 models of 6-Queens, all and only the '
             'solutions (brute force, not printed); the printed value is the reduction count',
        ignore=[r'undefined module : (work|pimos):: mgtp', r'non existent module : hyper_o'],
        budget=60_000_000)
    row('mgtp_tarZ', no='22 (unlinked copy)', archive='solver-prover/pimos/mgtp.tar.Z',
        static=('RUNS-DIFFERS', '- (code identical to mgtp.tgz: row mgtp)'),
        note='diff -r against MGTP/mgtp.tgz: only README and README.j differ')
    row('mgtp_n', no=91, archive='solver-prover/pimos/MGTP-N/MGTP-N-KL1.tgz',
        doc='INSTALL.j:25-130',
        serve=[(r'\.kl1$', None)],
        # INSTALL.j:25-31's st., pl., pd. are the site's aliases (a
        # timer, print length 10 => 100, depth 4 => 20, as the
        # transcript shows): typed as the Listener's own commands, and
        # the package work first (a compile into pimos is refused,
        # `module registration error : pimos:: mgtpv0`, OBSERVED
        # 2026-11-26).  OURS
        typed=[WORK, 'listener', 'compile(["mgtpv0","util"]).', 'statistics.',
               'print_length(100).', 'print_depth(20).',
               'mgtpv0: main(1,5,3,'
               '[((0,0,0),p(i({4},i(n({4}),{6}))),p(i({5},i(n({5}),{7})))),'
               '((0,0,0),p(i({4},i({6},{4}))),p(i({5},i({7},{5})))),'
               '((0,0,0),p(i(i({4},i({6},{8})),i({6},i({4},{8})))),'
               'p(i(i({5},i({7},{9})),i({7},i({5},{9}))))),'
               '((0,0,0),p(i(i({4},{6}),i(i({8},{4}),i({8},{6})))),'
               'p(i(i({5},{7}),i(i({9},{5}),i({9},{7}))))),'
               '((0,0,0),p(i(i({4},{6}),i(i(n({4}),{6}),{6}))),'
               'p(i(i({5},{7}),i(i(n({5}),{7}),{7}))))],'
               '[gen(p({1}),p(i({1},{3})),p({3}))],'
               '[tst(p(i(i(a,i(a,b)),i(a,b))))],'
               '(1,1,2,YYNN),Result,Ncalc,Delta) .'],
        printed=[('Result = unsat', 'INSTALL.j:106'), ('Ncalc = 18', 'INSTALL.j:107')],
        budget=150_000_000)
    row('h907_nseq', no='97/H9-07', archive='contract-research/97/DH9-07/H9-07.tgz',
        doc='nseq/pim/Nseq.com; documents/manual.tex:834; aitec19980402.log:1-33',
        serve=[(r'nseq/pim/[^/]+\.(sav|com|kl1)$', None)],
        typed=['listener', 'take("Nseq").', 'compile("SYN002-1-020dom_merc.kl1").',
               'load("mgtpNS7").', 'ns(50).'],
        printed=[('Number of Failed Branches = 43782', 'aitec19980402.log:26'),
                 ('unsat', 'aitec19980402.log:29')],
        budget=150_000_000)
    row('h907_nogc', alt_of='h907_nseq', no='97/H9-07', archive='contract-research/97/DH9-07/H9-07.tgz',
        doc='aitec19980402.log:1-33 (the session as logged, Nseq.com\'s gc step left out)',
        serve=[(r'nseq/pim/[^/]+\.(sav|com|kl1)$', None)],
        typed=['listener', 'compile("SYN002-1-020dom_merc.kl1").', 'load("mgtpNS7").',
               'main:main(50,ns,A).'],
        printed=[('Number of Failed Branches = 43782', 'aitec19980402.log:26'),
                 ('Number of Models = 0', 'aitec19980402.log:27'),
                 ('unsat', 'aitec19980402.log:29')],
        note='second stop: past h907_nseq\'s first (Nseq.com\'s gc.sav step); aliases.com '
             'ns(N) is main:main(N,ns,A) (aliases.com:37)',
        budget=400_000_000)
    row('h907_shell', alt_of='h907_nseq', no='97/H9-07', archive='contract-research/97/DH9-07/H9-07.tgz',
        doc='aitec19980402.log:1-33 with the held objects: the problem\'s compile stops '
            'at the shell as at the Listener (wait_value of a variable with itself, '
            'OBSERVED 2026-11-26), so the held SYN002-1-020dom_merc.sav is loaded instead '
            '(aliases.com l_syn2), then mgtpNS7.sav, relink(main,problem) (aliases.com r), '
            'and the query at the Listener',
        serve=[(r'nseq/pim/[^/]+\.(sav|com|kl1)$', None)],
        typed=['package:define(mgtp,pimos)', 'setenv task:package=mgtp',
               'load("SYN002-1-020dom_merc")', 'load("mgtpNS7")', 'relink(main,problem)',
               'listener', 'default_package(mgtp).', 'main:main(50,ns,A).'],
        printed=[('Number of Failed Branches = 43782', 'aitec19980402.log:26'),
                 ('Number of Models = 0', 'aitec19980402.log:27'),
                 ('unsat', 'aitec19980402.log:29')],
        note='the package mgtp is the log\'s ("mgtp:: problem" Updated, line 9)',
        budget=400_000_000)
    row('aya', no=73, archive='symbolic-proc/pimos/aya.tar.Z',
        doc='doc/INSTALL:18-63',
        serve=[(r'^src/[^/]+$', None)],
        typed=['take("ayainst.com")', 'compile', 'prime.aya', '!exit', 'listener',
               'prime:top(20).'],
        # the archive names the parser src/ayaparse.k1l (a one for the
        # ell): `!ERROR! unable to open file : ayaparse`, OBSERVED.  The
        # second try serves it as ayaparse.kl1 too (OURS)
        alt=['take("ayainst.com")', 'compile', 'prime.aya', '!exit', 'listener',
             'prime:top(20).'],
        serve_alt=[(r'^src/ayaparse\.k1l$', 'ayaparse.kl1')],
        # the second try's compile of the 21 files (14,441 lines) runs
        # past 150M instructions; it stops at 371,289,179 (OBSERVED
        # 2026-11-26, with --budget 1200000000): the row's budget, for
        # the alt row only (ifs_sweep.row: budget_alt)
        budget_alt=400_000_000,
        printed=[('\n2\n3\n5\n7\n11\n13\n17\n19\n', 'doc/INSTALL:55-63')],
        budget=150_000_000)
    row('gdcc', no=18, archive='kbms-clp/pimos/gdcc.tar.gz',
        doc='README:37-56',
        serve=[(r'^[a-z_]+\.sav$', None), (r'^gdcc\.(init|com)$', None),
               (r'^compile\.param$', None)],
        typed=['take("gdcc.init")',
               'alloc(0,X,Y), alg#X**2 + Y**2 = 1, alg#(X-1)**2 + (Y-1)**2 = 1.'],
        printed=[('Y = -X + 1', 'README:55'), ('X**2 = X', 'README:56')],
        budget=150_000_000)
    row('laputa', no=51, archive='natural-lang/pimos/laputa.tar.Z',
        doc='INSTALL:23; jikken.data:5-60',
        serve=[(r'\.kl1$', None)],
        typed=['compile([{KL1}])'],
        note='"compile every file" (INSTALL:23); the example needs all 55 (60,483 lines)',
        budget=200_000_000)
    row('multialign', no=75, archive='exper-apps/pimos/multialign.tar.Z',
        doc='INSTALL:32-34; DOC.pia:27-123',
        serve=[(r'^src/[^/]+$', None)],
        typed=[WORK, 'listener', 'take"load.pia".'],
        note='the prebuilt pia_s2.exe loaded; the printed run is 12,963,187,445 reductions '
             '(DOC.pia:122), beyond any budget here, so only the load is tried',
        budget=40_000_000)
    row('multialign_run', alt_of='multialign', no=75,
        archive='exper-apps/pimos/multialign.tar.Z',
        doc='DOC.pia:27-60 (the query as printed, its comments dropped, one line), after the '
            'load as in multialign+alt',
        serve=[(r'^src/[^/]+$', None)],
        typed=[WORK, 'take"load.pia"', 'listener', _pia_query(archive)],
        printed=[('Count = 33', 'DOC.pia:61'), ('Energy = -19749', 'DOC.pia:62')],
        note='the printed run is 12,963,187,445 reductions on PIM/m (DOC.pia:122): only its '
             'first stop is in reach',
        budget=S)
    row('dpool', no=86, archive='symbolic-proc/klic-apps/d-pool/dpool_pimos.tgz',
        doc='INSTALL:28-35; test/eval_access.com:14',
        serve=[(r'^dpool/obj/', 'dpool/'), (r'^dpool/test/dp_bench[^/]*\.kl1$', None)],
        typed=[WORK, 'listener', 'load("obj>owner-migration>dpool.sav").',
               'compile(["dp_bench","dp_bench_main_int"]).',
               'dp_bench:test_pool(2,int,put_cc,10,0,1000).'],
        note='INSTALL types load("./obj/owner-migration/dpool.sav") (a UNIX-style path); '
             'typed with PIMOS\'s ">" instead',
        budget=80_000_000)
    row('ldlib', no=74, archive='symbolic-proc/pimos/ldlib.tar.Z',
        doc='INSTALL:11-24',
        serve=[(r'^src/[^/]+/[^/]+$', None)],
        typed=['listener', 'take("Make.com").', 'compile_all.'],
        note='Make.com names files bare: src/ served flat (INSTALL:11-24 copies them so)',
        budget=80_000_000)
    row('ppss', no=30, archive='solver-prover/pimos/ppss.tar.Z',
        doc='INSTALL:45-47; README:53-66',
        serve=[(r'^ppss/src/', None)],
        typed=['compile(["a_builtin","andTran2","andor_io","apool","atpimos","ioutil",'
               '"mode_analyzer","orTran","ppri","rand1024","spcc","tandor","top","utandor"])',
               'listener', 'andor_top:go(["compute.ar2","cycle.ar2"]).'],
        note='one rand*.kl1 by world count (INSTALL:45-47): rand1024 (OURS, the smallest)',
        budget=80_000_000)
    row('colodex', no=66, archive='exper-apps/pimos/colodex.tar.Z',
        doc='install:23-25; Par-Par/test_ex.kl1:14',
        serve=[(r'^colodex/Par-Par/', None)],
        typed=['listener', 'take("s.com").', 'test_ex:t.'],
        note='the Par-Par part, the KL1-alone goal test_ex:t (readme:117-133)',
        budget=80_000_000)
    row('mmi', no=71, archive='exper-apps/pimos/mmi.tar.Z',
        doc='README:120-176',
        serve=[(r'^system\.sav$', None), (r'^(DIS|MMI|TOTAL)/', '/')],
        typed=[WORK, 'listener', 'load("system.sav").', 'main:go.', '0.', '10.'],
        note='the held system.sav loaded (README:120-121 puts it in the current directory), '
             'then main:go, demand generation (0.), quit (10.) (README:159-176)',
        budget=80_000_000)
    row('rodin', no=70, archive='exper-apps/pimos/rodin.tar.Z',
        doc='INSTALL:122-135; USAGE:31-64',
        serve=[(r'^rodin/(prog|data)/.*(?<!\.sav)$', 'rodin/')],
        typed=['listener', 'take("prog>compile>rodin").'],
        note='rodin.sav is damaged (a JIS text conversion put ESC $ B before the magic): '
             'rebuilt from source as INSTALL:122-130 says',
        budget=150_000_000,
        alt=['listener', '{TAKE prog>compile>rodin}'])
    row('dulcinea', no=42, archive='natural-lang/pimos/dulcinea.tar.Z',
        doc='INSTALL:6-9; install.com:1-23; doc/manual-e:11-37',
        serve=[(r'^(rosi|Bel|soc1|soc2|sancho|dul)/', '/'), (r'^(install\.com|aliases)$', None)],
        typed=['listener', 'take "install.com".'],
        budget=150_000_000)
    # ================= KL1 half of an application with an ESP half ===
    for name, no, arc, serve, typed, doc in [
        ('aligndp', 55, 'exper-apps/pimos/aligndp.tar.Z', [(r'\.kl1$', None)],
         ['compile([{KL1}])'], 'INSTALL:21-25; dp_color.kl1:57 string_io'),
        ('alignsa', 56, 'exper-apps/pimos/alignsa.tar.Z', [(r'\.kl1$', None)],
         ['compile([{KL1}])'], 'INSTALL:22-27; io3.kl1:31-34 string_io'),
        ('cbcdss', 69, 'exper-apps/pimos/cbcdss.tar.Z', [(r'\.kl1$', None)],
         ['compile([{KL1}])'], 'INSTALL:48-50; car.kl1:20-65 string_io car##car_top'),
        ('celplace', 57, 'exper-apps/pimos/celplace.tar.Z', [(r'\.kl1$', None)],
         ['compile(["top","main","an1mat1","an_module1","init","util","overlap","rn"])'],
         'INSTALL:128-137; top.kl1:43 string_io'),
        # INSTALL:17-27: the files in ME>cohlex, take("cohlex>Makefile")
        # at the shell.  The archive's name is `Makefile.` (an empty
        # extension); served also as cohlex>Makefile, the name INSTALL
        # types (OURS).  Its cd("cohlex") asks fep#pathname of the
        # directory (FepError 221 before ifs_sweep.install_write_files
        # served it, OBSERVED 2026-11-26)
        ('cohlex', 65, 'exper-apps/pimos/cohlex.tar.Z',
         [(r'^cohlex/[^/]+$', '/'), (r'^cohlex/Makefile\.$', 'cohlex>Makefile')],
         ['take("cohlex>Makefile")'], 'INSTALL:17-27; alien3.kl1:14 string_io'),
        ('consort', 63, 'exper-apps/pimos/consort.tar.Z',
         [(r'^consort/src/kl1_source/', 'consort/src/')],
         ['listener', 'take("kl1_source>comp_4p.com").'],
         'INSTALL:12-20; main.kl1:23,44 string_io user##esp_io_kl1 (desq\'s ESP)'),
        ('desq', 64, 'exper-apps/pimos/desq.tar.Z', [(r'^desq/src/kl1_source/', 'desq/src/')],
         ['listener', 'take("kl1_source>comp_4p.com").'], 'INSTALL:13-49'),
        # INSTALL:507-511: step 8, the shell's take of me:mdl_demo>
        # cmpMDL5gc.inf (me: the home), the files in their directories
        # (step 7's Utility>comp names >sys>user>DILEX2, not run: OURS)
        ('examds', 67, 'exper-apps/pimos/examds.tar.Z', [(r'^examds/(mdl_demo|mdl_DB)/', 'examds/')],
         ['take("mdl_demo>cmpMDL5gc.inf")'],
         'INSTALL:481-535; mdl_demo/ReadMe.doc:10-30 (model_main:run, the KL1-alone learning part)'),
        ('gog_kl1', 53, 'exper-apps/pimos/gog-kl1.tar.Z',
         [(r'^gog-kl1/kl1/[^/]+\.kl1$', '>sys>user>cgs>'), (r'^gog-kl1/make\.com$', None)],
         ['listener', 'take("make.com").'], 'INSTALL.e:104-107; commu.kl1:34-35 string_io'),
        ('gpsstap', 60, 'exper-apps/pimos/gpsstap.tar.Z', [(r'^gpsstap/async/', None)],
         ['take("async.com")'], 'INSTALL:207-223; planTop.kl1:183 string_io'),
        ('logisim', 59, 'exper-apps/pimos/logisim.tar.Z', [(r'^logisim/[^/]+\.(kl1|com)$', None)],
         ['listener', 'take("compile.com").'], 'README:34-51; interface.kl1:335-341 string_io'),
        ('lsirout', 58, 'exper-apps/pimos/lsirout.tar.Z', [(r'^lsirout/KL1/', None)],
         ['compile(["top_l","part1","part2","part3","top_p","dists","masters","lines",'
          '"terminals","utilities"])'], 'INSTALL:53-67; part1.kl1:37 string_io'),
        ('mendels', 61, 'exper-apps/pimos/mendels.tar.Z',
         [(r'^mendels/m[a-z]+\.exe$', '>sys>user>MENDEL>')],
         ['package:define(mendel,user) .', 'setenv task:package = mendel .',
          'load(">sys>user>MENDEL>mendel.exe") .',
          'relink([mendel,tableau_main,execute_main,mdl_compiler,mendel_package,esp_utility,'
          'graph,decomp,net,scc,prim])', 'mendel .'],
         'readme.e:33-39; shell.com1:20-21, 39-44 typed (the system ships prebuilt as '
         'mendel.exe)'),
        ('pmonitor', 62, 'exper-apps/pimos/pmonitor.tar.Z',
         [(r'^pmonitor/[^/]+\.(kl1|com)$', None)],
         ['listener', 'take("pm_kl1.com").'], 'INSTALL:11-13; pm.tex:65-78'),
        ('seqanal', 68, 'exper-apps/pimos/seqanal.tar.Z', [(r'^seqanal/kl1/', None)],
         ['listener', 'take(cmpfiles).'], 'INSTALL:11-44; ga.kl1:14-19 string_io'),
        ('sme', 32, 'solver-prover/pimos/sme.tar.Z', [(r'\.kl1$', None)],
         ['compile([{KL1}])'], 'INSTALL:20-79; sme.doc:21; sm_dev_mg.esp:4-5'),
        ('exreps', 6, 'symbolic-proc/pimos/exreps.tar.Z', [(r'^exreps/[^/]+\.kl1$', None)],
         ['compile([{KL1}])'], 'README:29-31; scrio92.kl1:20-22 string_io'),
        ('kl1graph', 7, 'symbolic-proc/pimos/kl1graph.tar.Z', [(r'\.kl1$', None)],
         ['compile([{KL1}])'], 'README:22-24; DOC/ppuserman.tex:30'),
        ('strtgysh', 8, 'symbolic-proc/pimos/strtgysh.tar.Z', [(r'^src/KL1/', None)],
         ['compile([{KL1}])'], 'INSTALL:7-50 (also a UNIX Prolog step first)'),
        ('argus_v', 31, 'solver-prover/pimos/argus-v.tar.Z',
         [(r'^[A-Za-z]+/[^/]+\.kl1$', '/'), (r'^compile\.com$', None)],
         ['listener &', 'compile', '!take "compile.com"', '!exit'],
         'INSTALL:137-150; MPX/mpx.kl1:82 string_io'),
        ('voronoi', 20, 'kbms-clp/pimos/voronoi.tar.Z', [(r'^src/[^/]+\.kl1$', None)],
         ['compile([{KL1}])'],
         'INSTALL:18-41; demo3.gdcc:38-70 string_io (the .gdcc files need GDCC\'s shell)'),
        ('kappa_p', 13, 'kbms-clp/pimos/kappa-p.tar.Z', [(r'^src/', 'src/')],
         ['take("KL1comp.com")'], 'INSTALL:18-66; 7 .esp catalogued as a required step'),
    ]:
        row(name, no=no, archive=arc, serve=serve, typed=typed, doc=doc, needs='simpos',
            budget=S)
    # ================= the held PIMOS objects, each loaded ============
    H9 = 'contract-research/97/DH9-07/H9-07.tgz'
    DP = 'symbolic-proc/klic-apps/d-pool/dpool_pimos.tgz'
    objs = [('gc', H9), ('mgtpNS7', H9), ('mgtp-NS-pim7-noRT', H9),
            ('SYN002-1-020dom_merc', H9), ('SYN009-1dom_merc', H9), ('SYN036-4dom_merc', H9),
            ('test2_445', H9)]
    row('objects', no='-', archive=H9,
        doc='the object files of the IFS tree whose magic is 5502h/5602h (asm/unlsav.py '
            'decodes each): load(...) at the Listener, one after another',
        serve=[(r'nseq/pim/[^/]+\.sav$', None, H9),
               (r'^dpool/obj/', 'dpool/', DP),
               (r'^system\.sav$', 'mmi_system.sav', 'exper-apps/pimos/mmi.tar.Z'),
               (r'^src/pimos/rf\.exe$', None, 'exper-apps/pimos/editalign.tar.Z'),
               (r'^src/t?pia_s2\.exe$', None, 'exper-apps/pimos/multialign.tar.Z'),
               (r'^mendels/m[a-z]+\.exe$', None, 'exper-apps/pimos/mendels.tar.Z')],
        # the problems before the provers: mgtpNS7 and mgtp-NS-pim7-noRT
        # call work::problem, and loaded first they are `Load Failed`
        # (`undefined module : work:: problem`, OBSERVED 2026-11-26)
        typed=([WORK, 'listener']
               + ['load("%s").' % n for n, _a in sorted(objs, key=lambda o: o[0].startswith('mgtp'))]
               + ['load("obj>%s>dpool.sav").' % v
                  for v in ('owner-migration', 'owner-fixed', 'access-info')]
               + ['load("mmi_system.sav").', 'load("rf.exe").', 'load("pia_s2.exe").',
                  'load("tpia_s2.exe").', 'load("mdllibrary.exe").', 'load("mendel.exe").']),
        note='gdcc\'s five are loaded by row gdcc (gdcc.init)', budget=80_000_000)
    # ================= needs another host, or damaged =================
    row('editalign', no=76, archive='exper-apps/pimos/editalign.tar.Z',
        doc='INSTALL:50-79; socket.kl1:10-46',
        serve=[(r'^src/pimos/[^/]+$', None)],
        typed=[WORK, 'listener', 'take"load.com".', 'dp_new:go.'],
        needs='other', note='the front end is a UNIX X/Motif program over a TCP socket '
        '(go/0 connects to 192.50.194.198:1192)', budget=S)
    row('mssd', no=84, archive='exper-apps/pimos/mssd.tar.Z',
        doc='parallel/compile.me:5; test.me:5; socket5.kl1:186-224',
        serve=[(r'^ProteinStruct/parallel/[^/]+\.kl1$', None)],
        typed=['compile', 'cp1,wavelet,geometric1,data,calcH5,main5_p,socket5', '!exit'],
        needs='other', note='results go to a remote TCP peer not in the archive; the rest '
        'of the package is C++ for SGI IRIX', budget=S)
    row('quixote', no=11, archive='kbms-clp/pimos/quixote.tar.gz',
        static=('NEEDS-OTHER', 'other: a UNIX client (C, X11R5, GNU Emacs) over a PIMOS '
                'socket, port 5678 (qifServer.kl1:50-70)'),
        note='the KL1 server is 129 files (83,939 lines); qxtv3.com builds it (INSTALL:13-19)')
    row('qxt_motif', no=83, archive='exper-apps/pimos/qxt_motif.tar.Z',
        static=('NEEDS-OTHER', 'other: Quixote Ver.III (quixote.sav, not held) and its UNIX '
                'client (INSTALL:33-64)'))
    row('robot', no=16, archive='kbms-clp/pimos/robot.tar.Z',
        static=('NEEDS-OTHER', 'other: GDCC source only (3 .gdcc files, no .kl1); needs '
                'GDCC\'s shell and alg solver (row gdcc) and its save file not shipped'))
    row('p_chal', no=17, archive='kbms-clp/pimos/p-chal.tar.Z',
        static=('NEEDS-OTHER', 'other: GDCC v2.5 programs (pchal.gdcc); needs GDCC\'s '
                'shell (row gdcc), loads from >sys>user>ksatoh>gdcc (shell.com:12-19)'))
    row('pax', no=39, archive='natural-lang/pimos/pax.tar.Z',
        static=('NEEDS-SIMPOS', 'simpos: the DCG-to-KL1 translator is ESP (TRANS/*.esp), '
                'run in the SIMPOS debugger (README:23-25); no translated grammar is shipped'))
    row('helic2', no=54, archive='exper-apps/pimos/helic2.tar.Z',
        static=('NEEDS-OTHER', 'damaged: about 390 of the 590 files README lists are missing '
                '(compile.param, listener.com, CBR>BG>*.exe, ...); plib.sav is text, cbr.exe '
                'and cbr_eng.exe JIS-converted'))
