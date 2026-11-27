# The IFS applications for PIMOS, run on the PIM/m model

*2026-11-26; rerun 2026-11-27 on master bc9a6dd3, after the KL1
floating-point merge (which added `set_constant` and the float
built-ins, the first sweep's two largest stops); three partial reruns
the same day, after model and runner changes (section 2).* Every application in the held ICOT Free Software tree
(`nonlocal/ifs`, `nonlocal/IFS_MANIFEST.md`) that was written for PIMOS,
run on the PIM/m reference model the way its own documentation says, and
sorted by what happened. This is triage: no model feature was added for
it. The product is the ranking of first stops (section 4): which missing
piece of the model, of PIMOS's environment or of the FEP stand-in would
let the most applications run.

The runner is `ref/pimm/ifs_sweep.py`, the rows (one per application,
with its procedure and its printed result) `ref/pimm/ifs_rows.py`, the
committed outcome of the last sweep `docs/ifs_sweep_results.json`.

## 1. The route

R8's and R9's (`pimos_roadmap.md` R8, R9): the PIMOS login prompt
checkpoint (`lockstep_shell.load`), forked once per row, each row's
files served as home files of that process only
(`longrun_ipl.add_home_file`; objects as `fep.FileData`, so `ls`'s pins
are untouched), and the lines its documentation types played into the
shell or the Listener (`lockstep_shell.play`). A row ends when the model
refuses an instruction, the FEP stand-in a request, the machine has
nothing left to run, or its instruction budget is spent.

What the runner adds to the environment, each OURS and each recorded in
the code where it is done:

- **The package work.** The prompt's task package is `pimos`, and PIMOS
  refuses to register a user's module there (`module registration
  error : pimos:: X` for every module of `pia_s2.exe`, `system.sav`,
  `mgtpv0`, `backet`, then `Load Failed`, OBSERVED). A user's login would
  have had its own package; every row that names no package itself has
  `setenv task:package=work` typed first (R8's and R9's package).
- **The collector on.** R7G's copying collector (`pimm_gc.py`) with a
  heap limit of 50M cells. The prompt's heap is 77.8M cells of 134.2M,
  most of it the IPL's garbage; the first collection is made at once and
  leaves 2,239,232 live cells (OBSERVED, from the prompt); the copy goes
  above hp first and back to the bottom next, so the limit must fit in
  the 56.4M cells above the prompt's heap. A first sweep had 130M: the
  first collection then came with no room for its to-space
  (`gc: the to-space is full`) or not at all (`heap full`), and 14 rows
  stopped on memory (OBSERVED, superseded).
- **Text in EUC.** Several archives keep their text in 7-bit JIS
  (rodin's INSTALL:61,101 asks for the conversion when the files go to
  the FEP); `jis_to_euc` does it, as the PSI's file transfer would.
- **Directories.** Files go where the documentation puts them: flat in
  the home, as a tree below it (`HOME>prog>compile>rodin.com`), or in an
  absolute directory the documentation names (`>sys>user>cgs>`,
  `>sys>user>MENDEL>`), with the listings PIMOS's wildcards read
  (`compile"Bel>*.kl1"`).
- **Two FEP services the stand-in lacks, in the runner only**:
  `fep#write_open` (202) with its putb, flush and close, the written
  bytes kept and compared with the printed results too (pia_s2 writes
  its alignment to `test.res`); `fep#beep` (113) on a window
  (mendels); and `fep#pathname` (221) on a directory device, which the
  shell's `cd` asks (cohlex; the answer `PSI::` and the path, as a
  file's, INFERENCE). `ref/pimm/fep.py` is unchanged. These were
  FepError stops in the first sweep, so each was a FEP stand-in gap,
  not the application's.
- **The directories on the way, wildcards, versions, `..` and 221 on a
  written file (2026-11-27), in the runner only**: 204 on the root `>`
  and on each directory on the way to a served one (`>sys`,
  `>sys>user`), each directory listing the directories in it (by name,
  no version: no period, a directory to `shell/utils/pathname.kl1`
  `is_directory_or_file/4`); 237 with any wildcard, the listing's
  entries that match it (`*` and `?`, a file matched without its
  version, INFERENCE; fep.py serves `*.*` only, as the FEP tapes pin);
  a served file opened by its listed name with `.1`; a `..` node in a
  204 path resolved (INFERENCE that the FEP resolves it); and 221 on a
  file the runner's 202 opened, `PSI::` + the path + `.1` (the request
  as on a read file, `bios/fep_module/file_dvc.kl1` device_io1 318-321,
  which every open's device reaches; the new file's version 1,
  INFERENCE). The shell expands a wildcard from the root: for
  `compile(["*.mac"])` in `>sys>user>pmpsi>cohlex` it opens
  `directory(">", normal(Dir,_,_))` and asks `listing("sys", S)`, then
  each directory down the path (`pathname.kl1` 183-189, `checkNode`
  254-283), so a root the FEP refuses fails that unification inside
  the shell's task (cohlex and dulcinea, OBSERVED: their `a goal failed
  inside a shoen`, section 4). Each OURS (`install_listing`,
  `install_write_files`), checked without a checkpoint by `--check`
  (`services_check`, section 8).
- **The Listener's take, typed out.** In the first sweep every `take`
  typed at the Listener stopped at `set_constant` (OBSERVED 2026-11-26;
  the instruction is on master since the float merge, and in the rerun
  no take stops there: each `+alt` row now meets the same stop as its
  plain row, or the budget, except rodin's and h907_nseq's, section 4).
  Such a row has a second
  try (`NAME+alt`): the command file's commands typed one by one at the
  Listener (`{TAKE file}`, `expand_take`; a take inside expanded too, a
  last command without its full stop given one). Two variants first
  tried the files at the shell; the shell reads a command file line by
  line, so a command spread over lines is a `*** Syntax Error ***`
  (OBSERVED, superseded).

## 2. Outcomes

- **RUNS-MATCHES**: ran to the end and printed what the documentation
  prints (compared without white space, in the window and in the files
  it wrote).
- **RUNS-DIFFERS**: ran to the end and printed something else.
- **RUNS-NO-ORACLE**: ran to the end; the documentation prints nothing to
  compare with.
- **STOPS / STOPS(float)**: the first stop named. A refused floating-point
  operation is marked STOPS(float); floating point is on master since
  the float merge, and no row of the rerun has such a stop (since the
  second partial rerun mssd, a NEEDS-OTHER row, has a `float:` stop:
  a float built-in waiting on an unbound input, which has no stub).
- **BUDGET**: still running, without an error, when its instruction
  budget was spent.
- **NEEDS-SIMPOS**: the application has an ESP half that runs on the
  PSI under SIMPOS (its window, its user interface); the KL1 half was
  run where it could be, and its stop is still recorded.
- **NEEDS-OTHER**: a UNIX client, a program not held, a damaged archive.

The rules, in order (`ifs_sweep.py` header, CLASSIFY): a memory shortage;
a refused instruction (float if it names floating point); a FEP error; a
model failure; the window's first error line (`!ERROR!`, `Illegal`,
the shell's and the Listener's syntax errors, `Module not found`,
`Load Failed`, `unable to open`) as `missing:` or `compile:`; the
budget; else the printed values. A row's `ignore` patterns skip errors
its documentation shows as expected (MGTP's manual order compiles
`otter` before the module it calls).

Counted once per application (46 rows that are no other row's variant;
the `+alt` rows and the variants `h907_nogc`, `h907_shell`,
`multialign_run` are second tries). The rerun of 2026-11-27 beside the
first sweep's counts:

| Outcome | Applications (2026-11-27) | First sweep (2026-11-26) |
|---|---|---|
| RUNS-MATCHES | 0 | 0 |
| RUNS-DIFFERS | 2 (`mgtp` and its second archive `mgtp_tarZ`) | 2 |
| RUNS-NO-ORACLE | 2 (`objects`: all 16 held objects load; `multialign`: `load.pia` takes, `Load Succeeded`) | 1 |
| STOPS | 5 | 10 |
| STOPS(float) | 0 | 2 |
| BUDGET | 7 (`laputa`, `ppss`, `colodex`, `rodin`, `mgtp_n`, `h907_nseq`, `dulcinea`) | 1 |
| NEEDS-SIMPOS | 23 (20 of them undetermined: budget spent while compiling) | 23 (10 undetermined) |
| NEEDS-OTHER | 7 | 7 |

No row stops at `set_constant` or at a float built-in any more: of
the 14 behind set_constant and the 5 behind float, 9 now spend their
budget compiling (ppss, colodex, rodin, aligndp, celplace, examds,
gog_kl1, logisim, seqanal), 4 stop at `wait_value on a structure`
(ldlib, dulcinea, consort, desq, which were their "next" stops; with
kappa_p, as before, it is now the largest first stop, 5), and the
other 6 meet new stops: mmi a second PE,
h907_nseq `get_heap_size`, gdcc a Listener syntax error on its
documented query, editalign the FEP socket request, pmonitor its
missing `chart_ctl`; multialign's take now loads `pia_s2.exe` and ends.

**Partial rerun, 2026-11-27, after `wait_value` on modules and
`get_heap_size` on one PE** (`ref_wait_value.py`; section 4). The ten
rows pinned at the two stops removed were rerun from a rebuilt
checkpoint (`--run ... kappa_p ldlib ldlib+alt dulcinea dulcinea+alt
consort consort+alt desq desq+alt h907_nseq`, 350 s ten at a time) and
merged into the committed summary (`--summary --update DIR`); a model
stop ends a run, so no other row can change. What the five met at
`wait_value`, OBSERVED with each pair logged from a private copy: a
module against the integer 0 or an atom, at a macro file's load (every
pair a module `{27h, ...}` and `{00h, 0}` or `{02h, atom}`, 1 to 4 per
row), so the guard fails and the next clause is taken, as VPIM does.
Their next stops: ldlib `wait_value of a variable with itself` (after
the library's modules compile, at `xia.mac`), dulcinea `a goal failed
inside a shoen` (at `compile["rosi>meta>Copy>*.kl1", ...]`, past
`meta.mac`), consort and desq the FEP `pathname` request (221) on
`unload([bignum_macro],"kl1>bignum_macro")` after both macro files
load, kappa_p the budget (compiling, past `isch.mac`, 60M; now
undetermined); h907_nseq passes `get_heap_size` and stops at the next
built-in, `set_heap_alert`. The outcome counts do not change (STOPS 8,
NEEDS-SIMPOS 23); the undetermined are 21.

**Second partial rerun, 2026-11-27, after `wait_value` of a variable
with itself, `enqueue_goal_to_processor` on one PE and
`set_heap_alert`** (`ref_node_alert.py`; section 4). The eleven rows
pinned at the three stops were rerun from the same prompt checkpoint
(`--run ... mgtp_n h907_nseq h907_nseq+alt h907_nogc h907_shell aya+alt
multialign_run ldlib ldlib+alt mmi mssd`, eleven at once, 1,347 s,
aya+alt the last) and merged with `--summary --update`; `mgtp` run
apart with the changed model repeats its committed run exactly
(26,598,077 instructions, 21,497 reductions), not merged. Their next
stops: the four H9-07 rows `enqueue_goal_with_priority` of 12
arguments; mmi the guard `list` (23:E3); ldlib and ldlib+alt the
window's `!ERROR![misc.kl1@0] *** Syntax Error ***` (there before,
behind the model stop, which the rules take first: not examined),
compiling on to their 80M budget; mssd `b_floating_point_multiply`
waiting on an unbound input with no stub (a `float:` stop; the row
stays NEEDS-OTHER); mgtp_n, multialign_run and aya+alt their budgets
(150M, 60M, 400M; aya+alt past `ayagen.kl1` into `cllib.kl1`). Counts:
STOPS 7, BUDGET 5 (mgtp_n), the rest unchanged; the undetermined are 22.

**Third partial rerun, 2026-11-27, after `enqueue_goal_with_priority`
of more than 11 arguments, the guard `list`, the model's
`unification_failure` and the runner's directory and written-file
services** (`ref_prio_list.py`; `--check`'s `services_check`; sections
1 and 4). The twelve rows pinned at the four stops were rerun from the
same prompt checkpoint (`--run ... h907_nogc h907_shell h907_nseq
h907_nseq+alt dulcinea dulcinea+alt cohlex consort consort+alt desq
desq+alt mmi`, twelve at once, 1,256 s, the two 400M rows the
last) and merged with `--summary --update`. The runner's changes reach
every row, so the rows that could meet them were looked for in the
lines each row types and the command files it takes (no model run): a
wildcard, a `..`, a `cd` or an absolute path; beyond these twelve only
gdcc (a `*` in its query, not a path) and gog_kl1 (absolute file names,
no wildcard; INFERENCE, from its committed run, which spent its budget
compiling and so never met the root's refusal: the shell walks from
the root for a wildcard only) have one, so no other row was rerun. The
rerun ran at 9d7bfb79. (`unification_failure` came after it; a model
stop ends a run, and the only rows that met it are cohlex and
dulcinea, which no longer do.) Their next stops: h907_nseq, h907_nogc
and h907_shell run the query `main:main(50,ns,A)` to their budgets
(150M, 400M, 400M), past the 12-argument goal; h907_nseq+alt too, its
stop now the window's first error, the shell's `*** Syntax Error ***`
on the `take("Nseq")` typed before the Listener (there since the first
sweep, behind the model stop); dulcinea and dulcinea+alt compile past
`rosi>meta>Copy`, `Share` and `Common`, unload `metalib` and are in
`Bel>belief.kl1` at 150M; cohlex compiles `layout1.mac` and is in its
86 `.kl1` files at 60M; consort, desq and their +alt rows unload
`bignum_macro` and `long_macro` and compile on, in `c_util.kl1` at 60M;
mmi, past `list` after `" Now intializing DIS?? "`, meets
`enqueue_goal_to_processor` of 13 arguments with the node unbound
(section 4). Counts: STOPS 5, BUDGET 7 (h907_nseq, dulcinea),
NEEDS-SIMPOS 23 (20 undetermined); the undetermined are 27.

**No application matches its printed result.** MGTP/G (No.22) runs to
the end and prints the four 6-Queens models, all of them and each
correct, with 21,497 reductions where the manual prints 18,759; R9
(`pimos_roadmap.md`) explains 3,801 of the difference (our merger
stub's runs) and has no source for the rest. The sweep's mgtp row
repeats R9's run exactly (26,598,077 instructions, 21,497 reductions,
OBSERVED with the collector on), so the collector changes nothing there.
The nearest to a match are past the first stop: `multialign_run`
(No.75) loads the held `pia_s2.exe`, takes the documented query
(DOC.pia:27-60) and writes the start of its output file (`test.res`:
the sequences,
`Cut_ratio = 97`, `(U,V,S) = (7,1,0)`); past `enqueue_goal_to_processor`
(its `@node` goals made on the one PE since 2026-11-27) it computes to
its 60M budget with no more output yet. `mgtp_n` (No.91) compiles its
1,871 lines and runs the documented query to its 150M budget, also
past that stop, without the result printed yet.

## 3. The table

One row per application (43 archives, the H9-07 contract archive and
the KLIC-apps Distributed Pool for PIMOS), plus the second tries. "No."
is the IFS catalogue number. Generated by `ifs_sweep.py --markdown`
from the committed results.

| Row | No. | Archive | Outcome | First stop | Second stop (+alt) | Typed (procedure) | Printed result | Last window line / stop |
|---|---|---|---|---|---|---|---|---|
| mgtp | 22 | `solver-prover/pimos/MGTP/mgtp.tgz` | RUNS-DIFFERS | - |  | `compile; !package work; preotter; otter; !attach clause clause_trans_o; q6.clause; !exit; relink(hyper_o); relink(work::hyper_o); listener; default_package(w...` | `18759 reductions` (manualE.tex:235 (MGTP/G/MERC, N=6)) | 26,598,077 instr.; [6] ; doc mgtp/manualE.tex:86-128, 214-240 |
| mgtp_tarZ | 22 (unlinked copy) | `solver-prover/pimos/mgtp.tar.Z` | RUNS-DIFFERS | - (code identical to mgtp.tgz: row mgtp) |  | (not run) | none |  |
| mgtp_n | 91 | `solver-prover/pimos/MGTP-N/MGTP-N-KL1.tgz` | BUDGET | budget |  | `setenv task:package=work; listener; compile(["mgtpv0","util"]).; statistics.; print_length(100).; print_depth(20).; mgtpv0: main(1,5,3,[((0,0,0),p(i({4},i(n(...` | `Result = unsat` (INSTALL.j:106); `Ncalc = 18` (INSTALL.j:107) | 150,000,001 instr.; [5] ; doc INSTALL.j:25-130 |
| h907_nseq | 97/H9-07 | `contract-research/97/DH9-07/H9-07.tgz` | BUDGET | budget | compile: Shell>> *** Syntax Error *** | `listener; take("Nseq").; compile("SYN002-1-020dom_merc.kl1").; load("mgtpNS7").; ns(50).` | `Number of Failed Branches = 43782` (aitec19980402.log:26); `unsat` (aitec19980402.log:29) | 150,000,001 instr.; [28] ; doc nseq/pim/Nseq.com; documents/manual.tex:834; aitec19980402.log:1-33 |
| h907_nogc | 97/H9-07 | `contract-research/97/DH9-07/H9-07.tgz` | BUDGET | budget |  | `listener; compile("SYN002-1-020dom_merc.kl1").; load("mgtpNS7").; main:main(50,ns,A).` | `Number of Failed Branches = 43782` (aitec19980402.log:26); `Number of Models = 0` (aitec19980402.log:27); `unsat` (aitec19980402.log:29) | 400,000,001 instr.; [3] ; doc aitec19980402.log:1-33 (the session as logged, Nseq.com's gc step left out) |
| h907_shell | 97/H9-07 | `contract-research/97/DH9-07/H9-07.tgz` | BUDGET | budget |  | `package:define(mgtp,pimos); setenv task:package=mgtp; load("SYN002-1-020dom_merc"); load("mgtpNS7"); relink(main,problem); listener; default_package(mgtp).; ...` | `Number of Failed Branches = 43782` (aitec19980402.log:26); `Number of Models = 0` (aitec19980402.log:27); `unsat` (aitec19980402.log:29) | 400,000,001 instr.; [2] ; doc aitec19980402.log:1-33 with the held objects: the problem's compile stops at the shell as at the Listener (wait_value of a variable with itself, OBSERVED 2026-11-26), so the held SYN002-1-020dom_merc.sav is loaded instead (aliases.com l_syn2), then mgtpNS7.sav, relink(main,problem) (aliases.com r), and the query at the Listener |
| aya | 73 | `symbolic-proc/pimos/aya.tar.Z` | STOPS | missing: !ERROR! unable to open file : ayaparse | budget | `take("ayainst.com"); compile; prime.aya; !exit; listener; prime:top(20).` | `2 3 5 7 11 13 17 19` (doc/INSTALL:55-63) | 150,000,001 instr.; =>  :- module sceneCl .; doc doc/INSTALL:18-63 |
| gdcc | 18 | `kbms-clp/pimos/gdcc.tar.gz` | STOPS | compile: [12] *** Syntax Error *** |  | `take("gdcc.init"); alloc(0,X,Y), alg#X**2 + Y**2 = 1, alg#(X-1)**2 + (Y-1)**2 = 1.` | `Y = -X + 1` (README:55); `X**2 = X` (README:56) | 44,162,140 instr.; Shell>> ; doc README:37-56 |
| laputa | 51 | `natural-lang/pimos/laputa.tar.Z` | BUDGET | budget |  | `compile([{KL1}])` | none | 200,000,001 instr.; Shell>> ; doc INSTALL:23; jikken.data:5-60 |
| multialign | 75 | `exper-apps/pimos/multialign.tar.Z` | RUNS-NO-ORACLE | - | - | `setenv task:package=work; listener; take"load.pia".` | none | 4,811,047 instr.; [3] ; doc INSTALL:32-34; DOC.pia:27-123 |
| multialign_run | 75 | `exper-apps/pimos/multialign.tar.Z` | BUDGET | budget |  | `setenv task:package=work; take"load.pia"; listener; pia_s2:top(["KLGQGCFGEVWMGTWNGTTRVAIKTLKPGTMSPEAFLQEAQVMKKLRHEKLVQLYAVVSEEPIYIVTEYMSKGSLLDFLK","KLGGGQYGE...` | `Count = 33` (DOC.pia:61); `Energy = -19749` (DOC.pia:62) | 60,000,001 instr.; [1] ; doc DOC.pia:27-60 (the query as printed, its comments dropped, one line), after the load as in multialign+alt |
| dpool | 86 | `symbolic-proc/klic-apps/d-pool/dpool_pimos.tgz` | STOPS | model: clause_info at 83600795 |  | `setenv task:package=work; listener; load("obj>owner-migration>dpool.sav").; compile(["dp_bench","dp_bench_main_int"]).; dp_bench:test_pool(2,int,put_cc,10,0,...` | none | 14,774,768 instr.; [3] ; doc INSTALL:28-35; test/eval_access.com:14 |
| ldlib | 74 | `symbolic-proc/pimos/ldlib.tar.Z` | STOPS | compile: !ERROR![misc.kl1@0] *** Syntax Error *** | compile: !ERROR![misc.kl1@0] *** Syntax Error *** | `listener; take("Make.com").; compile_all.` | none | 80,000,001 instr.; !ERROR! This module can't be accessed :pimosx; doc INSTALL:11-24 |
| ppss | 30 | `solver-prover/pimos/ppss.tar.Z` | BUDGET | budget |  | `compile(["a_builtin","andTran2","andor_io","apool","atpimos","ioutil","mode_analyzer","orTran","ppri","rand1024","spcc","tandor","top","utandor"]); listener;...` | none | 80,000,001 instr.; =>  :- module andor_top .; doc INSTALL:45-47; README:53-66 |
| colodex | 66 | `exper-apps/pimos/colodex.tar.Z` | BUDGET | budget | budget | `listener; take("s.com").; test_ex:t.` | none | 80,000,001 instr.; Compile File : PSI::>sys>user>pmpsi>process2.kl1.1; doc install:23-25; Par-Par/test_ex.kl1:14 |
| mmi | 71 | `exper-apps/pimos/mmi.tar.Z` | STOPS | model: enqueue_goal_to_processor (7, 3860442298), 13 arguments |  | `setenv task:package=work; listener; load("system.sav").; main:go.; 0.; 10.` | none | 33,908,393 instr.; [2] " Now intializing DIS?? "; doc README:120-176 |
| rodin | 70 | `exper-apps/pimos/rodin.tar.Z` | BUDGET | budget | memory: RuntimeError: heap full: past the heap limit | `listener; take("prog>compile>rodin").` | none | 150,000,001 instr.; [7] ProgFile =["prog>move>from_conf","prog>move>from_exp","prog>move>find_util","prog>move; doc INSTALL:122-135; USAGE:31-64 |
| dulcinea | 42 | `natural-lang/pimos/dulcinea.tar.Z` | BUDGET | budget | budget | `listener; take "install.com".` | none | 150,000,001 instr.; =>  :- module belief .; doc INSTALL:6-9; install.com:1-23; doc/manual-e:11-37 |
| aligndp | 55 | `exper-apps/pimos/aligndp.tar.Z` | NEEDS-SIMPOS | budget |  | `compile([{KL1}])` | none | 60,000,001 instr.; =>  :- module input .; doc INSTALL:21-25; dp_color.kl1:57 string_io |
| alignsa | 56 | `exper-apps/pimos/alignsa.tar.Z` | NEEDS-SIMPOS | budget |  | `compile([{KL1}])` | none | 60,000,001 instr.; =>  :- module sa .; doc INSTALL:22-27; io3.kl1:31-34 string_io |
| cbcdss | 69 | `exper-apps/pimos/cbcdss.tar.Z` | NEEDS-SIMPOS | budget |  | `compile([{KL1}])` | none | 60,000,001 instr.; Shell>> ; doc INSTALL:48-50; car.kl1:20-65 string_io car##car_top |
| celplace | 57 | `exper-apps/pimos/celplace.tar.Z` | NEEDS-SIMPOS | budget |  | `compile(["top","main","an1mat1","an_module1","init","util","overlap","rn"])` | none | 60,000,001 instr.; Compile File : PSI::>sys>user>pmpsi>util.kl1.1; doc INSTALL:128-137; top.kl1:43 string_io |
| cohlex | 65 | `exper-apps/pimos/cohlex.tar.Z` | NEEDS-SIMPOS | budget |  | `take("cohlex>Makefile")` | none | 60,000,001 instr.;  The value of compile: distribution is [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15] . ; doc INSTALL:17-27; alien3.kl1:14 string_io |
| consort | 63 | `exper-apps/pimos/consort.tar.Z` | NEEDS-SIMPOS | budget | budget | `listener; take("kl1_source>comp_4p.com").` | none | 60,000,001 instr.; =>  :- module c_util .; doc INSTALL:12-20; main.kl1:23,44 string_io user##esp_io_kl1 (desq's ESP) |
| desq | 64 | `exper-apps/pimos/desq.tar.Z` | NEEDS-SIMPOS | budget | budget | `listener; take("kl1_source>comp_4p.com").` | none | 60,000,001 instr.; =>  :- module c_util .; doc INSTALL:13-49 |
| examds | 67 | `exper-apps/pimos/examds.tar.Z` | NEEDS-SIMPOS | budget |  | `take("mdl_demo>cmpMDL5gc.inf")` | none | 60,000,001 instr.; Shell>> ; doc INSTALL:481-535; mdl_demo/ReadMe.doc:10-30 (model_main:run, the KL1-alone learning part) |
| gog_kl1 | 53 | `exper-apps/pimos/gog-kl1.tar.Z` | NEEDS-SIMPOS | budget | budget | `listener; take("make.com").` | none | 60,000,001 instr.; [4] compile[">sys>user>cgs>capcd",">sys>user>cgs>capture",">sys>user>cgs>client",">sys>use; doc INSTALL.e:104-107; commu.kl1:34-35 string_io |
| gpsstap | 60 | `exper-apps/pimos/gpsstap.tar.Z` | NEEDS-SIMPOS | budget |  | `take("async.com")` | none | 60,000,001 instr.; =>  :- module planUtil .; doc INSTALL:207-223; planTop.kl1:183 string_io |
| logisim | 59 | `exper-apps/pimos/logisim.tar.Z` | NEEDS-SIMPOS | budget | budget | `listener; take("compile.com").` | none | 60,000,001 instr.; [2] compile["batch","block","data","dbms","demo_io","diag","dsp_lib","engine","expand","fi; doc README:34-51; interface.kl1:335-341 string_io |
| lsirout | 58 | `exper-apps/pimos/lsirout.tar.Z` | NEEDS-SIMPOS | budget |  | `compile(["top_l","part1","part2","part3","top_p","dists","masters","lines","terminals","utilities"])` | none | 60,000,001 instr.; [terminals.kl1@0] Compile Module : terminals; doc INSTALL:53-67; part1.kl1:37 string_io |
| mendels | 61 | `exper-apps/pimos/mendels.tar.Z` | NEEDS-SIMPOS | - |  | `package:define(mendel,user) .; setenv task:package = mendel .; load(">sys>user>MENDEL>mendel.exe") .; relink([mendel,tableau_main,execute_main,mdl_compiler,m...` | none | 6,157,417 instr.; Shell>> package>>; doc readme.e:33-39; shell.com1:20-21, 39-44 typed (the system ships prebuilt as mendel.exe) |
| pmonitor | 62 | `exper-apps/pimos/pmonitor.tar.Z` | NEEDS-SIMPOS | missing: !ERROR! unable to open file : chart_ctl | missing: !ERROR! unable to open file : chart_ctl | `listener; take("pm_kl1.com").` | none | 60,000,001 instr.; Compile File : PSI::>sys>user>pmpsi>select.kl1.1; doc INSTALL:11-13; pm.tex:65-78 |
| seqanal | 68 | `exper-apps/pimos/seqanal.tar.Z` | NEEDS-SIMPOS | budget | budget | `listener; take(cmpfiles).` | none | 60,000,001 instr.; Compile File : PSI::>sys>user>pmpsi>print.kl1.1; doc INSTALL:11-44; ga.kl1:14-19 string_io |
| sme | 32 | `solver-prover/pimos/sme.tar.Z` | NEEDS-SIMPOS | budget |  | `compile([{KL1}])` | none | 60,000,001 instr.; =>  :- module util2 .; doc INSTALL:20-79; sme.doc:21; sm_dev_mg.esp:4-5 |
| exreps | 6 | `symbolic-proc/pimos/exreps.tar.Z` | NEEDS-SIMPOS | budget |  | `compile([{KL1}])` | none | 60,000,001 instr.; Shell>> ; doc README:29-31; scrio92.kl1:20-22 string_io |
| kl1graph | 7 | `symbolic-proc/pimos/kl1graph.tar.Z` | NEEDS-SIMPOS | budget |  | `compile([{KL1}])` | none | 60,000,001 instr.; Compile File : PSI::>sys>user>pmpsi>q_program.kl1.1; doc README:22-24; DOC/ppuserman.tex:30 |
| strtgysh | 8 | `symbolic-proc/pimos/strtgysh.tar.Z` | NEEDS-SIMPOS | budget |  | `compile([{KL1}])` | none | 60,000,001 instr.; Shell>> ; doc INSTALL:7-50 (also a UNIX Prolog step first) |
| argus_v | 31 | `solver-prover/pimos/argus-v.tar.Z` | NEEDS-SIMPOS | budget |  | `listener &; compile; !take "compile.com"; !exit` | none | 60,000,001 instr.; COMPILE> ; doc INSTALL:137-150; MPX/mpx.kl1:82 string_io |
| voronoi | 20 | `kbms-clp/pimos/voronoi.tar.Z` | NEEDS-SIMPOS | budget |  | `compile([{KL1}])` | none | 60,000,001 instr.; =>  :- module vline .; doc INSTALL:18-41; demo3.gdcc:38-70 string_io (the .gdcc files need GDCC's shell) |
| kappa_p | 13 | `kbms-clp/pimos/kappa-p.tar.Z` | NEEDS-SIMPOS | budget |  | `take("KL1comp.com")` | none | 60,000,001 instr.; Compilation Time = 3054 [MSEC]; doc INSTALL:18-66; 7 .esp catalogued as a required step |
| objects | - | `contract-research/97/DH9-07/H9-07.tgz` | RUNS-NO-ORACLE | - |  | `setenv task:package=work; listener; load("gc").; load("SYN002-1-020dom_merc").; load("SYN009-1dom_merc").; load("SYN036-4dom_merc").; load("test2_445").; loa...` | none | 72,652,650 instr.; [17] ; doc the object files of the IFS tree whose magic is 5502h/5602h (asm/unlsav.py decodes each): load(...) at the Listener, one after another |
| editalign | 76 | `exper-apps/pimos/editalign.tar.Z` | NEEDS-OTHER | fep: FepError: device 40: request [801, b'', b'#p#m#p#s#i', b''] | fep: FepError: device 39: request [801, b'', b'#p#m#p#s#i', b''] | `setenv task:package=work; listener; take"load.com".; dp_new:go.` | none | 9,278,947 instr.; [3] ; doc INSTALL:50-79; socket.kl1:10-46 |
| mssd | 84 | `exper-apps/pimos/mssd.tar.Z` | NEEDS-OTHER | float: b_floating_point_multiply waiting on an unbound input (no stub) |  | `compile; cp1,wavelet,geometric1,data,calcH5,main5_p,socket5; !exit` | none | 50,539,275 instr.; =>  :- module main .; doc parallel/compile.me:5; test.me:5; socket5.kl1:186-224 |
| quixote | 11 | `kbms-clp/pimos/quixote.tar.gz` | NEEDS-OTHER | other: a UNIX client (C, X11R5, GNU Emacs) over a PIMOS socket, port 5678 (qifServer.kl1:50-70) |  | (not run) | none |  |
| qxt_motif | 83 | `exper-apps/pimos/qxt_motif.tar.Z` | NEEDS-OTHER | other: Quixote Ver.III (quixote.sav, not held) and its UNIX client (INSTALL:33-64) |  | (not run) | none |  |
| robot | 16 | `kbms-clp/pimos/robot.tar.Z` | NEEDS-OTHER | other: GDCC source only (3 .gdcc files, no .kl1); needs GDCC's shell and alg solver (row gdcc) and its save file not shi |  | (not run) | none |  |
| p_chal | 17 | `kbms-clp/pimos/p-chal.tar.Z` | NEEDS-OTHER | other: GDCC v2.5 programs (pchal.gdcc); needs GDCC's shell (row gdcc), loads from >sys>user>ksatoh>gdcc (shell.com:12-19 |  | (not run) | none |  |
| pax | 39 | `natural-lang/pimos/pax.tar.Z` | NEEDS-SIMPOS | simpos: the DCG-to-KL1 translator is ESP (TRANS/*.esp), run in the SIMPOS debugger (README:23-25); no translated grammar |  | (not run) | none |  |
| helic2 | 54 | `exper-apps/pimos/helic2.tar.Z` | NEEDS-OTHER | damaged: about 390 of the 590 files README lists are missing (compile.param, listener.com, CBR>BG>*.exe, ...); plib.sav  |  | (not run) | none |  |

The held objects, one line per file loaded (rows `objects` and `gdcc`):

| Row | Object | Result |
|---|---|---|
| objects | `gc.sav` | Load Succeeded |
| objects | `SYN002-1-020dom_merc.sav` | Load Succeeded |
| objects | `SYN009-1dom_merc.sav` | Load Succeeded |
| objects | `SYN036-4dom_merc.sav` | Load Succeeded |
| objects | `test2_445.sav` | Load Succeeded |
| objects | `mgtpNS7.sav` | Load Succeeded |
| objects | `mgtp-NS-pim7-noRT.sav` | Load Succeeded |
| objects | `obj>owner-migration>dpool.sav` | Load Succeeded |
| objects | `obj>owner-fixed>dpool.sav` | Load Succeeded |
| objects | `obj>access-info>dpool.sav` | Load Succeeded |
| objects | `mmi_system.sav` | Load Succeeded |
| objects | `rf.exe` | Load Succeeded |
| objects | `pia_s2.exe` | Load Succeeded |
| objects | `tpia_s2.exe` | Load Succeeded |
| objects | `mdllibrary.exe` | Load Succeeded |
| objects | `mendel.exe` | Load Succeeded |
| gdcc | `shell.sav` | Load Succeeded |
| gdcc | `alg.sav` | Load Succeeded |
| gdcc | `simplex_if.sav` | Load Succeeded |
| gdcc | `bool.sav` | Load Succeeded |
| gdcc | `parser.sav` | Load Succeeded |

## 4. The stops, ranked

The main product of this work. First, how many applications each stop
is the first one of, with each application's next stop where a second
try (an `+alt` row, or a variant such as `h907_shell`) got past the
first. Then the applications still compiling when their budget ran out
(no stop, listed apart). Then every stop met, first or next: the number
of applications each stands in front of. Generated by `--markdown`
(`ifs_sweep.ranking`).

| Rank | First stop | Applications | Each, with its next stop (second try) |
|---|---|---|---|
| 1 | `compile: !ERROR![misc.kl1@0] *** Syntax Error ***` | 1 | ldlib (next: compile: !ERROR![misc.kl1@0] *** Syntax Error ***) |
| 2 | `compile: [12] *** Syntax Error ***` | 1 | gdcc |
| 3 | `damaged: about 390 of the 590 files README lists are missing ` | 1 | helic2 |
| 4 | `fep: FepError: device N: request [801]` | 1 | editalign (next: fep: FepError: device N: request [801]) |
| 5 | `float: b_floating_point_multiply waiting on an unbound input ` | 1 | mssd |
| 6 | `missing: !ERROR! unable to open file : ayaparse` | 1 | aya (next: budget) |
| 7 | `missing: !ERROR! unable to open file : chart_ctl` | 1 | pmonitor (next: missing: !ERROR! unable to open file : chart_ctl) |
| 8 | `model: clause_info at N` | 1 | dpool |
| 9 | `model: enqueue_goal_to_processor ` | 1 | mmi |
| 10 | `other: GDCC source only ` | 1 | robot |
| 11 | `other: GDCC v2.5 programs ` | 1 | p_chal |
| 12 | `other: Quixote Ver.III ` | 1 | qxt_motif |
| 13 | `other: a UNIX client ` | 1 | quixote |
| 14 | `simpos: the DCG-to-KL1 translator is ESP ` | 1 | pax |

undetermined, the budget spent with no stop (27): mgtp_n, h907_nseq (next: compile: Shell>> *** Syntax Error ***; budget), laputa, ppss, colodex (next: budget), rodin (next: memory: the heap full), dulcinea (next: budget), aligndp, alignsa, cbcdss, celplace, cohlex, consort (next: budget), desq (next: budget), examds, gog_kl1 (next: budget), gpsstap, logisim (next: budget), lsirout, seqanal (next: budget), sme, exreps, kl1graph, strtgysh, argus_v, voronoi, kappa_p

every stop met, first or next (applications it stands in front of):
- `compile: Shell>> *** Syntax Error ***`: 1 (h907_nseq)
- `memory: the heap full`: 1 (rodin)

What each is:

- **Gone since the first sweep: `set_constant` (was 14, every one
  first) and `b_integer_to_floating_point` (was 5 first, 8 in all).**
  The KL1-B instruction `23:10` (`set_constant`, the integer 32768 as
  a goal's argument, OBSERVED operand `23:10010000` `00:00008000` in
  the first sweep) and the float built-ins came with the KL1
  floating-point merge. In the rerun no row refuses either, and no
  row is STOPS(float). Every take typed at the Listener now runs past
  the point where the first sweep stopped; what the 19 meet instead is
  in the table (section 2's paragraph). The first sweep's INFERENCE
  that gdcc's set_constant came from `gdcc:go` is consistent with the
  rerun (the whole `gdcc.init` take, `gdcc:go` last, now runs and opens
  GDCC's window) but still not observed: nothing refuses set_constant
  any more, so where it was met is not shown.
- **`wait_value on a structure` (was 5 first, 5 in all): done
  2026-11-27.** The guard `X = Y` on two words neither atomic, a
  string, a list nor a vector: now VPIM's `klb_equal` and
  `f_EqualStruct` (`interpreter/klb_compare.psl.c` 91-97,
  `functions/f_reduce_passive_unify.psl.c` 45-105) on both reference
  models (`pimm.py` `equal_other`, `ref_wait_value.py`); met as a
  module against 0 or an atom (paragraph in section 2). Before: kappa_p met it at once; ldlib,
  dulcinea, consort and desq in their Listener take (their "next" stop
  in the first sweep; the +alt rows the same). It was the
  largest stop, all in compiles or macro loads (ldlib after two
  compiled modules, dulcinea at `meta.mac`, consort at
  `bignum_macro.mac`).
- **`enqueue_goal_to_processor (0, 1)` (was 2 first, 4 in all): done
  2026-11-27 on the one-PE reference.** A goal sent to node 1
  (`@node`): mgtp_n's load balancing (nodes 1 to 5, INSTALL.j's
  `main(1,5,...)`), mmi's `main:go`, H9-07's `main:main(50,ns,A)`,
  multialign's query (`multialign_run`). `pimm.py` now makes the goal
  of any integer node here, as the single-processor systems do: PDSS
  compiles `enqueue_to_node` to a plain `enqueue_goal`
  (`compiler/outp.kl1` 360-363; "Because PDSS is a single processor
  system, there is no processor pointing function", `doc.e/pdss.tex`
  71-72), and KLIC built for one node enqueues a goal for another node
  number locally (`runtime/sched.c` 277-289). A DECLARED DIFFERENCE,
  OURS: on PIM/m a node outside the shoen's range is the exception
  `range_overflow` (`e-shoen.tex` 491-514; VPIM `klb_fork.psl.c`
  1068-1070), which the multi-PE model `pimm_pe.py` keeps
  (`ref_node_alert.py`). A node that is not an integer is still
  refused. Next: mgtp_n runs its documented query to its 150M budget
  (compiled, then `[2]`..`[5]` and the query, OBSERVED), multialign_run
  computes to its 60M budget (`test.res` as before: the sequences,
  `Cut_ratio = 97`, `(U,V,S) = (7,1,0)`, no more yet), mmi stops at the
  guard `list` (23:E3, `inst_tab.kl1`:190; "Succeeds if X is a
  list", suspends on an unbound X, PIMOS manual `e-builtin.tex` 62-66,
  PRINTED; the model lacks it) after
  `" Now intializing DIS?? "`, and H9-07's four rows at
  `enqueue_goal_with_priority` of 12 arguments (below).
- **`wait_value of a variable with itself` (was 2 first, 4 in all):
  done 2026-11-27.** The guard `X = Y` with X and Y the same unbound
  variable, refused before; now it waits on the variable, as VPIM's
  `klb_equal` does ("when undefined, it suspends even if both point to
  the same variable", `interpreter/klb_compare.psl.c` 36-43; PDSS
  `passive_unify` the same; INFERENCE for PIM/m, whose microcode is
  not held), on both models (`ref_node_alert.py`). Met while compiling:
  H9-07's SYN002 problem, ldlib at `xia.mac`, mssd, and aya's
  `ayagen.kl1`. Next: ldlib (and ldlib+alt): its first window error
  is `!ERROR![misc.kl1@0] *** Syntax Error ***` (earlier in the take,
  there before but behind the model stop), then past `xia.mac`
  `!ERROR! This module can't be accessed :pimosx` at `klib.mac`, then
  its 80M budget spent; mssd compiles all seven files and stops
  at `b_floating_point_multiply waiting on an unbound input (no stub)`
  (a float built-in with no waiting stub: a `float:` stop, the row
  NEEDS-OTHER); h907_nogc and
  h907_nseq+alt compile the problem, load `mgtpNS7` and meet the
  12-argument goal; aya+alt compiles `ayagen.kl1` (where it waited
  before, after 371,289,179 instructions) and is in `cllib.kl1` at its
  400M budget (undetermined).
- **`get_heap_size`** (h907_nseq; done 2026-11-27, on one PE as on the
  PEs, `pimm.Machine.i_get_heap_size`, `ref_wait_value.py`). H9-07's
  `mgtp_gc:allocate(80)`, after `gc.sav` ("the GC auto-start program",
  `documents/manual.tex` 824) loads at the Listener, calls the built-in
  `22:FE`, which the one-PE reference `pimm.py` lacked.
- **`set_heap_alert`** (h907_nseq; done 2026-11-27 on both models,
  `pimm.Machine.i_set_heap_alert`, `ref_node_alert.py`).
  `set_heap_alert(Size, ^Alarm)`, 22:FD, after VPIM
  (`klb_pimos.psl.c` 163-181 and 209-351, the firing in
  `f_event_self_int.psl.c` 67-116): Alarm is the heap's use at once when
  the use is past Size, else the alert is armed and Alarm bound to the
  use at the first goal switch after it passes Size (after the
  collection; VPIM checks at each growth of the heap top, INFERENCE
  that the goal switch is within a reduction of it); a second request
  binds the first Alarm to `[]`; Size at or above get_heap_size's Size
  (`range_overflow`) and a Size not an integer (`illegal_input`) are
  refused, loud; an unbound Size waits; the armed Alarm is a root of
  the collector (`str_gc_pre_post.psl.c` 2.11). What H9-07 asks,
  OBSERVED from a private copy logging the call: `set_heap_alert(
  53673920, A)`, 80% of the Size 67,092,480 that get_heap_size reports,
  at a use of 3,577,109; armed. That Size is half the memory above the
  heap's start, not the sweep's 50M-cell heap limit (section 1), so the
  runner's own collection comes first at 50M and the alert does not
  fire within it: a gap of the runner's heap (OURS), recorded, not
  changed. Next: all four H9-07 rows (h907_nseq, +alt, h907_nogc,
  h907_shell) reached `enqueue_goal_with_priority (0, 3000), 12
  arguments` in the query (below).
- **`enqueue_goal_with_priority` of 12 arguments** (the four H9-07
  rows; done 2026-11-27 on both models, `ref_prio_list.py`). A goal of
  12 with `@priority(3000)`: the compiler packs a goal with a pragma as
  it packs a plain one, the arguments from the 11th on in a vector in
  the 11th (PIMOS `library/compiler/newnorm.kl1` 907-909,
  `normalize_body_goal(Goal@Pragma)` calls `pack_body_goal` first;
  `pack.kl1` 13-29), and the instruction's arity is the unpacked
  goal's (newnorm.kl1 893-901), so the vector is spread as
  `enqueue_goal` spreads it; the priority is still dropped. Next: the
  query runs to the budget on h907_nseq, h907_nogc and h907_shell
  (undetermined); h907_nseq+alt's stop is now its window's first error
  (section 2's third rerun).
- **The guard `list`** (mmi; done 2026-11-27 on both models,
  `ref_prio_list.py`): 23:E3, "Succeeds if X is a list", suspends on an
  unbound X, fails on anything else (PIMOS manual `e-builtin.tex`
  62-68, PRINTED); `[]` is not a list (PDSS `emulate.c` 685, VPIM
  `klb_index.psl.c` 117-127). Next: **`enqueue_goal_to_processor` of
  13 arguments with the node unbound** (mmi, now first): `Goal@node(P)`
  with P not yet bound waits on P through the stub `to_processor N`,
  which `asm/pimm_stubs.py` has for N up to 11 (`TO_PROCESSOR_MAX`);
  a packed goal of 13 does not fit it. Not built here (the stubs are
  shared with the Bluespec core's layout).
- **A syntax error on GDCC's documented query** (gdcc, new): after the
  take, GDCC's window is a KL1 Listener with `change_macro(gdcc::
  gdcc_expander)` and the rest of `gdcc.com` (OBSERVED: `End of take`);
  the query of README:51-53 typed there is `[12] *** Syntax Error ***`
  with the mark after `alg #`, before `X **2`, and the echo shows
  `(X-1)` read as `(Xmint(1))`. INFERENCE, not separated: the
  Listener's reader lacks an operator GDCC declares (`**` or the infix
  `#`), or the query belongs in a reader GDCC's shell installs.
- **`clause_info`** (dpool): an instruction the model lacks, met at
  `dp_bench:test_pool` after Distributed Pool's objects and benchmark
  have loaded and compiled.
- **`a goal failed inside a shoen`** (cohlex, dulcinea; separated and
  gone 2026-11-27). OBSERVED from a private copy logging the failure:
  a body unification of the 4-vector `normal(Dir,_,_)` with the atom
  `abnormal` in the file request filter's `-directory$$$enu$1/4`
  (`server/fep/file/fileRfil.kl1` 117-126), right after the FEP
  stand-in answered 204 on the root `>` with 5. The shell's wildcard
  expansion walks an absolute path from the root and writes
  `directory(">", normal(Dir,_,_))` (`shell/utils/pathname.kl1`
  183-189): it takes the root for granted, so PIMOS on a FEP that
  refuses it would report a `unification_failure` there, correctly.
  The cause was the stand-in's (the runner's directory service had no
  root); both rows now get the root and the directories on the way,
  237 with a wildcard, the listed `name.1` opened and `..` resolved
  (section 1). The model's half: a failed body unification inside a
  shoen was refused; it is now reported as the exception
  `unification_failure` (10, Info `{Pe, DataX, DataY}`, `kernel/
  builtin/excpt_tbl.kl1` 56, 209-215; VPIM
  `f_reduce_exception_handler.psl.c` 79-96), the body going on at the
  next instruction as VPIM's does (`klb_unify_bound.psl.c` 263-269,
  371-374), on both reference models for the one-cell `get_*`
  (`ref_prio_list.py`; a structure's or a built-in's failure is still
  refused; the Bluespec core has no such path). Next:
  their compiles run to the budget (undetermined).
- **FEP `fep#pathname` (221) on a written file** (consort, desq; done
  2026-11-27, in the runner, where the written files are): the same
  request as on a read file (`bios/fep_module/file_dvc.kl1`
  device_io1 318-321, reached from every open of device_create/5,
  21-44); answered `PSI::` + the path + `.1` (the new file's version,
  INFERENCE). `fep.py` serves no write-open, so the answer lives beside
  the runner's 202, not in the stand-in (a DECLARED placement; its
  tapes are unchanged). Next: both unload both macro files and compile
  on to the budget.
- **FEP `fep#create_socket` (801)** (editalign, now first; its take
  loads and `dp_new:go` asks for the socket): the X/Motif front end
  over TCP; NEEDS-OTHER anyway.
- **Missing files** (the archives' own): aya's parser is shipped as
  `src/ayaparse.k1l` (a one for the ell; served as `ayaparse.kl1` in the
  second try, OURS); pmonitor's `pm_kl1.com` compiles a `chart_ctl` the
  archive does not hold (now its first stop: the `!ERROR!` line, then
  the budget spent on the other compiles).
- **Memory, `heap full: past the heap limit`** (rodin+alt, new): the
  take typed out compiles rodin's library and is in its eighth file
  (`prog>input>exclusion.kl1`) at 62,322,163 instructions when the
  heap passes the runner's 50M-cell collector limit (section 1). The
  plain rodin row (the take at the Listener) is still compiling at its
  150M budget. A limit of the runner's heap, not of the model's
  instruction set: not separated whether a larger limit would fit.
- **Undetermined (the budget spent, no stop): 27 applications** (11 in
  the first sweep; new: ppss, colodex, rodin, aligndp, celplace,
  examds, gog_kl1, logisim, seqanal, each past its old set_constant or
  float stop; kappa_p past `wait_value` on a module; mgtp_n, running
  its query, past `@node`; h907_nseq past the 12-argument goal;
  dulcinea and cohlex past the root directory; consort and desq past
  221). Most were still compiling: the PIMOS compiler on the
  model costs about 50,000 instructions a source line (mgtp_n: 1,871
  lines compiled and its query begun in 104,283,213; aya's 14,441 lines
  took 371M to its stop, OBSERVED), and laputa has 60,483 lines,
  argus_v 23,387, gog_kl1 17,300, gpsstap 11,750. What they will meet
  is not observed. INFERENCE from a pattern count over the first
  eleven's sources (`\d+\.\d+` and the `$$` operators, a loose one):
  every one but kl1graph has files with float literals or float
  arithmetic, and all but sme and kl1graph have files with `@node`, so
  (float being in now) a second PE is the likely next stop.

## 5. The held objects

Among these applications' `.sav` and `.exe` files, 21 are whole PIMOS
objects (magic `5502` or `5602`, decoded by
`asm/unlsav.py`): mmi's `system.sav`, editalign's `rf.exe`, multialign's
`pia_s2.exe` and `tpia_s2.exe`, GDCC's five `.sav`, H9-07's seven,
mendels' `mendel.exe` and `mdllibrary.exe`, Distributed Pool's three.
Four were damaged by a JIS text conversion (they begin `1b 24 42`,
ESC $ B, before the magic): `failN.exe`, `rodin.sav`, `cbr.exe`,
`cbr_eng.exe`; rodin is rebuilt from its sources instead (rodin's
INSTALL:122-130 allows it). `plib.sav` and `failN.exeF` are text. Row
`objects` loads the 16 whole ones no other row loads into the package
work, the H9-07 problems before the provers that call them (loaded
first, `mgtpNS7` is `Load Failed`, `undefined module : work::
problem`, OBSERVED): all 16 `Load Succeeded`. GDCC's five are loaded
by row gdcc's `gdcc.init`, all five `Load Succeeded` (both in the table
under section 3). The 16 `.sav` objects among the 21 (mmi 1, GDCC 5,
H9-07 7, Distributed Pool 3) all load.

## 6. The ESP halves: SIMPOS demonstrations

From the sweep, not from the documentation alone:

1. **mendels (No.61).** The only NEEDS-SIMPOS application whose KL1 half
   runs to its user prompt: `mendel.exe` (the held object) loads into
   the package mendel, the relink succeeds, `mendel .` opens its window
   and asks for input: its own window, titled "ESP Package?", two beeps
   and the prompt `package>>` (mendels' `package.kl1`:60-77
   read_window), whose answer goes to `ckcreate_esp_device`, the ESP
   class package on the PSI. The rest is MENDELS's ESP half. The strongest demonstration candidate.

   **The two halves linked (2026-11-27, `psi/mendels.py`,
   `psi/test_mendels.py`).** `package>>` asks the ESP *package* name
   (package.kl1:60-77 reads it from `mendel.pac` when that file is in the
   task directory, readme.e:18-28), not the user directory: answering
   `mendel` goes on to 601 `mendel##mendel_esp_device`, where `fep.py`
   alone stops (FepError, 6,160,384 instructions). The user directory
   (readme.e:37-39) is asked later, by the ESP half's own dialog
   (init_path.esp). The documented installation (`mendel.pac` served in
   `>sys>user>MENDEL>KL1>`, `mdllibrary.exe` in `>sys>user>MENDELuser>SYSTEM>`;
   install.e) asks no `package>>` at all. On that route, with the 601s
   and 620s carried to the PSI (`fep_bridge.BridgeFep`), the ESP half
   compiled by `espc.py` (the archive's 108 ESP files as the package
   `mendel`; 18 items dropped by the parser, 689 predicates refused) and
   run on kl0:
   - the loader's "WAIT !" window, the package load (library_utility),
     `mendel_esp_device` io(0, "start");
   - the path dialog, "Input User Path Name>" in a pmacs_window, answered
     `>sys>user>MENDELuser`, then `y` (screen
     `docs/simpos/screens/mendels_path.png`);
   - `load_library` to the KL1 half, which loads `mdllibrary.exe` from
     the path typed and answers `loaded_library(normal([mendel::example1,
     mendel::example2, mendel::example3]))`;
   - the ESP half reads it and goes on into `mendel_main`'s create/1,
     which stops at the first SIMPOS class not stood in:
     `temporary_menu:create/3` (7,075,533 PIM/m instructions, 21
     exchanges; tape `psi/mendels_tapes/doc.json`, replayed by
     test_mendels). Next: temporary_menu, then MENDELS's own windows
     (mendel_window, garnet_window, library_window, ...), which need the
     graphics side of SIMPOS's window system.
   The stand-ins added for it are listed in `psi/README.md` "MENDELS".
2. **aligndp (No.55) and logisim (No.69).** Each has one ESP file
   (`dna3d.esp`, 503 lines; `simulation.esp`, 1,691) that reaches the
   KL1 half through `pimfep##as_pimos_string_io_device`, the FEP string
   I/O SIMPOS's login already uses. Their KL1 halves stopped only at
   float in the first sweep (aligndp at once, logisim past the
   Listener's take); in the rerun, with float in, both are still
   compiling at the 60M budget (undetermined).
3. **alignsa (No.56) and lsirout (No.57).** One and two ESP files (547
   and 756 lines), the same string-I/O link; their KL1 compiles were
   still running at the budget (undetermined).
4. **sme (No.32) and colodex (No.66).** sme has 16 ESP files; colodex
   one 320-line `demo.esp` with the string-I/O link, but 30,232 lines of
   KL1, now past the old set_constant stop and compiling at the budget
   (in `process2.kl1`, the third file, at 80M).

## 7. Running it

```sh
# the rows, their archives and budgets (no model run)
python3 -I ref/pimm/ifs_sweep.py --list
# the sweep: every row, forked from the prompt checkpoint (R8's)
python3 -I ref/pimm/ifs_sweep.py --run PROMPT.pkl DIR --jobs 10
# some rows, or a long run with a larger budget
python3 -I ref/pimm/ifs_sweep.py --run PROMPT.pkl DIR --budget 1200000000 aya+alt
# the outcome table and the ranking, from a run or the committed summary
python3 -I ref/pimm/ifs_sweep.py --report [DIR]
# the committed summary, refused if it classifies a row otherwise
python3 -I ref/pimm/ifs_sweep.py --summary DIR
# a partial rerun (the rows a model change can alter) into the committed summary
python3 -I ref/pimm/ifs_sweep.py --summary --update DIR
# the checkpoint-free check (run_tests.sh)
python3 -I ref/pimm/ifs_sweep.py --check
```

PROMPT.pkl is the machine at the shell's prompt, as R8 and MP1 use it
(`lockstep_shell.py` header): the IPL's link saved by
`longrun_ipl.py --reference --save LINK.pkl` (15-50 min), then
`longrun_ipl.py --load LINK.pkl --go --fep --save-prompt PROMPT.pkl`;
about 1.1 GB, not committed.
The sweep of 2026-11-26 ran every row, ten at a time, in 2,504 s on a
16-core machine at a load average of 150 to 250 (each fork about 40,000
to 50,000 instructions a second, 250 MB). aya+alt was run on its own
with `--budget 1200000000` and stopped at 371,289,179 instructions; its
row's budget is now 400M so that a plain sweep reproduces it.
The rerun of 2026-11-27 (master bc9a6dd3): LINK.pkl in 987 s (16.5
min), PROMPT.pkl from it in 41 s, the sweep ten at a time in 2,159 s at
a load average of about 7 before it started, and aya+alt alone with
`--budget 1200000000` beside it in 1,698 s, stopping at 371,289,179
instructions again (the plain sweep's 400M row the same). The
results go to DIR (NAME.json each, the window's last 200,000
characters); `--summary DIR` writes `docs/ifs_sweep_results.json` (the
stop, the error lines, the window's last 4,000 characters, the written
files, the loads), which `--report` and `--check` read without a
checkpoint.

## 8. Injections

`--check` (in `run_tests.sh`) makes these, in its own process, against
the committed summary; each must be reported for exactly the rows
named. OBSERVED 2026-11-27, against the summary after the third
partial rerun (the stop rows are the first row with a model stop, now
dpool: mgtp_n and the H9-07 rows have none since their queries run to
their budgets):

| Injection | Reported |
|---|---|
| dpool's stop removed (`nothing left to run`) | dpool |
| dpool's stop made a float stop (and classified `float:`) | dpool |
| mgtp's printed value made its own window line, `21497 reductions` (the match path) | mgtp |
| `needs simpos` dropped from aligndp | aligndp |
| ERROR_MARK made to match nothing (the window's error lines unseen) | aya, gdcc, h907_nseq+alt, ldlib, ldlib+alt, pmonitor, pmonitor+alt |
| mgtp's printed value altered (the archive lookup, `oracles`) | mgtp |

And one in the source (applied, run, reverted from a copy, `--check`
PASS again): `classify` with its float branch removed (every refused
instruction a `model:` stop). Against the first sweep's summary it
made `--check` FAIL on exactly the eight float rows (ppss, mmi,
rodin+alt, aligndp, celplace, examds, logisim+alt, seqanal+alt).
The rerun's summary has no float row, and the same injection left
`--check` PASS (OBSERVED 2026-11-27); so the float-stop case above now
also checks that the injected stop is classified `float:`, and with
the branch removed `--check` FAILs on that case alone (OBSERVED).
After the second partial rerun the summary has a float stop again
(mssd), and the same injection makes `--check` FAIL on mssd's pin
alone (OBSERVED 2026-11-27, a private copy; again after the third
partial rerun).

`--check` also runs `services_check`: the runner's directory and
written-file services (section 1) on a bare `fep.Fep`, no checkpoint,
16 requests and their answers (the root and `>sys>user` opened and
listed, `listing("sys")`, `"*"`, `"cohlex"`, `"*.*"` with the
directory in it, `"*.mac"`, `a.mac.1` opened and `a.mac.2` not,
`HOME>cohlex>..` opened and its pathname, `>sys>other` refused, 221 on
a written file). Injections into a private copy, OBSERVED 2026-11-27,
the services lines reported all of them: the root and the way not
served (4: the root and `>sys>user` answered 5, their 237 FepError);
no wildcard listing (4: 237 FepError for each wildcard but `*.*`); the
wildcard matched against the whole entry, version and all (1:
`*.mac` empty); directories not listed (4); no versioned open (1);
`..` not resolved (2: 5, and 221 FepError); no 221 on a written file
(1). Each is written in `services_check`'s docstring. The oracle check finds all 19 printed values in the archive files their
rows cite.

## 9. Open

- set_constant and float: done (the float merge); the rerun of
  2026-11-27 is the sweep after them.
- `wait_value` on a module and `get_heap_size` on one PE: done
  2026-11-27 (partial rerun, section 2). The Bluespec core still
  refuses wait_value on a module (`PimmStages.bsv`, `E unimp`): no
  lockstep reaches it.
- `wait_value` of a variable with itself, `enqueue_goal_to_processor`
  on one PE and `set_heap_alert`: done 2026-11-27 (second partial
  rerun, section 2). The Bluespec core still refuses all three
  (`PimmStages.bsv` 1016-1017: one variable twice `E unimp`; rule
  `toProcessor`, 1502-1513: a node other than 0 `E unimp`; no
  set_heap_alert at all): no lockstep reaches them.
- `enqueue_goal_with_priority` of more than 11 arguments, the guard
  `list`, `unification_failure` inside a shoen, and the runner's root
  directory, wildcard listing, versioned opens, `..` and 221 on a
  written file: done 2026-11-27 (third partial rerun, section 2). The
  Bluespec core still refuses more than 11 arguments with a priority
  (`PimmStages.bsv`, `E unimp`), has no `list` guard and no
  unification failure path: no lockstep reaches them.
- The heap alert and the runner's limit: get_heap_size's Size (67.1M)
  is not the sweep's 50M heap limit, so H9-07's 80% alert cannot fire
  before the runner collects; whether Size should report the limit
  when one is set is open (OURS either way).
- The first stops now, ranked (section 4), not built here: one each,
  among them `enqueue_goal_to_processor` of 13 arguments with the node
  unbound (mmi: the stub `to_processor N` goes to 11, `asm/pimm_stubs.py`
  `TO_PROCESSOR_MAX`; the packed goal would need its arity carried
  through the wait), a float built-in waiting with no stub (mssd),
  ldlib's syntax error on `misc.kl1`, `clause_info` (dpool), the heap
  limit (rodin+alt), GDCC's query syntax, h907_nseq+alt's shell syntax
  error on `take("Nseq")` (behind the model stop until now).
- The undetermined twenty-seven: a longer run each (`--budget`), hours apiece
  at the measured rate; or the Bluesim core, if faster.
- The multi-PE four (mgtp_n, mmi, H9-07, multialign) run on one PE now
  (their `@node` goals made here); on the multi-PE model (`pimm_pe.py`),
  whose agent owns that code, they are still to be run as placed.
- mgtp's reduction count (R9's open item).
- GDCC: `gdcc:go` does open its window (a Listener with GDCC's macro
  expander) and the query typed there is a syntax error; whether the
  Listener's reader lacks GDCC's operators or the runner types the
  query into the wrong reader is not separated.
- cohlex: separated (section 4): the runner's directory service had no
  root; the model's own refusal of the failure is gone too.
- The runner's directory services are INFERENCE in form: what a PSI's
  FEP lists in `>` and `>sys>user` (here only the directories on the
  way to a served one), how its 237 matches a wildcard (here fnmatch's,
  a file without its version), that it resolves `..`; and they stay in
  the runner, not `fep.py`, whose tapes pin 237 with `*.*` alone.
- mendels: done 2026-11-27 (§6 item 1): the prompt asks the package
  name, and the two halves run linked as far as mendel_main's
  temporary_menu. Next: stand in temporary_menu and MENDELS's windows.
