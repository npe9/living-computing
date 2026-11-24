<!-- The working notes of the 2026-11-23 search INSIDE the held archives
(a delegated agent), kept as written. Its tables (a 36,953-row census of
every IFS archive member, 6 MB) and scripts stayed in the session's
scratch space and are not in git; this file is the record. Summary and
the audit status changes: environment_audit.md section 7. -->

# Inside-held-material search, 2026-11-23

Scratch root: `<S>` = /private/tmp/claude-501/-Users-npe-src-living-computing-pim/01b03f2f-1efc-495c-9771-b09885a1fa2f/scratchpad/inside
Extracted copies: `<S>/x/<archive>/`; my scripts: `<S>/bin/`; raw outputs: `<S>/notes/`; converted words: `<S>/conv/`.
Archive paths below are relative to `pim/docs/nonlocal/`. Nothing in the repo was edited, built or committed.

## Task 1: PIMOS unloader files

Magic (READ, `pimos/src/library/unloader/unlver.kl1` `marker/2`; `encoder.kl1`; `decoder.kl1` `check_magic_number`):
5502 module file, no comment; 5602 package file, no comment (header followed by the package atom
name, `put_atom_name`); 5702 module file with comment (L1 L2 then the comment); 5802 commented
package; 5902 term_encode. 5602 is therefore NOT "the same family by inference" only: it is the
package form, and the IPL (5502h/5702h only) refuses it. `asm/unlsav.py` treats 5602 as 5502 and
mis-parses (`length=2147483648`); stripping the package atom (words 3..12) to a 5502 copy
(`<S>/conv/simplex_if_as5502.sav`) parses all 15 modules.

Module info vector (MEASURED): `[Day, Ms, Day, Ms, SourcePath, Day, Ms, Includes]`; Day counts from
1901-01-01 (fits mgtpNS7.kl1 header date 1997-06-23 and bool.sav mtime 1992-07-15 exactly).
The module magic term is 2555905 = 0x00270001 in all 268 modules of the 25 undamaged files except plib.sav.1's 6 (no info vector, an older module layout, INFERENCE); the same value as the PIMOS 3.6 objects.

`savsum.py` = unlsav's parser over every module; "unknown-opcode" ratio 3-10%, same as the 3.6
objects (pimm_bios 1625/27838); most files leave the same 2 trailing words `0000 xxxx` as the 3.6
objects; gc.sav leaves 61 and simplex_if.sav 34 (zero padding after the 2). Externals checked against 440 source modules + 480
modules defined in the 3.6 object set (`buffer`, `variable`, `mklib`, `pimos` are object-only).

| file (archive!member) | bytes | magic | modules (package) | compiled (Day) | FEP/source host | externals not in PIMOS 3.6 |
|---|---|---|---|---|---|---|
| kbms-clp/pimos/gdcc.tar.gz!bool.sav | 37,554 | 5502 | 3 (bool) | 1992-07-15..16 | icpsi358 | none |
| !alg.sav | 148,574 | 5502 | 18 (alg) | 1993-02-19..04-26 | icpsi572 | var (in shell.sav/simplex_if) |
| !shell.sav | 221,466 | 5502 | 21 (gdcc) | 1992-04-21..1993-02-23 | icpsi572 | none |
| !parser.sav | 124,788 | 5502 | 10 (parser) | 1993-01-11 | icpsi572 | list, wconvert (in shell.sav) |
| !simplex_if.sav | 182,784 | **5602** package `simplex` | 15 | 1992-05-19 | icpsi276 | none |
| exper-apps/pimos/mmi.tar.Z!system.sav | 379,356 | 5502 | 63 (V1) | 1992-08-05..07 | tspsi223 user pmpsi | none |
| symbolic-proc/klic-apps/d-pool/dpool_pimos.tgz!dpool/obj/owner-fixed/dpool.sav | 56,426 | 5502 | 4 (yamauchi) | 1995-03-30 | UNIX paths /home/yamauchi | none |
| !owner-migration/dpool.sav | 86,716 | 5502 | 4 (masaki) | 1995-02-24 | /home/masaki | none |
| !access-info/dpool.sav | 89,702 | 5502 | 4 (masaki) | 1995-03-07..20 | /home/masaki | none |
| contract-research/97/DH9-07/H9-07.tgz!H9-07/nseq/pim/mgtpNS7.sav | 31,640 | 5502 | 1 main (mgtp) | 1997-06-23 | icpsi705 user pimm | problem (any problem .sav) |
| !mgtp-NS-pim7-noRT.sav | 30,118 | 5502 | 1 main (mgtp) | 1997-04-28 | icpsi705 | problem |
| !SYN002-1-020dom_merc.sav | 5,038 | 5502 | 1 problem | 1997-06-23 | icpsi705 | none (no extcalls) |
| !SYN009-1dom_merc.sav | 4,384 | 5502 | 1 problem | 1997-03-26 | icpsi705 | none |
| !SYN036-4dom_merc.sav | 98,054 | 5502 | 1 problem | 1997-06-23 | icpsi705 | none |
| !test2_445.sav | 8,544 | 5502 | 1 problem | 1997-04-18 | icpsi705 | none |
| !gc.sav | 1,280 | 5502 | 1 mgtp_gc (vista) | 1992-02-17 | icpsi167 | none |
| exper-apps/pimos/rodin.tar.Z!rodin/prog/load/rodin.sav | 643,183 | JIS-damaged 5502 | 111 | - | - | not decoded |

Unlsav prints `_` (0x2132) as `2` (it keeps the low byte): `print2constraint2set` is `print_constraint_set`.

Self-contained: gdcc's five are one set (cross-references between files), needing only PIMOS 3.6
modules; MGTP main + one problem file; dpool and mmi need only PIMOS. Source is held for all except
gc.sav and mgtp-NS-pim7-noRT.sav (KLIC sibling mgtp-NS-pim7-noRTF6.kl1 only).
Environments stated: gdcc "PIMOS v3.5 or above", "PSI-2, PSI-UX"; mmi "PIMOS Ver.3.0
(PIMOS(3000)/CAL(0192)/CSP(0334)/KL1(012107)/KL0(019200)/ParaG(3010)), SIMPOS 7.1, M-PSI-2, M-PSI-3, 16 PEs";
dpool: PIMOS via cfep/UNIX FEP; MGTP: run log `H9-07/nseq/pim/aitec19980402.log` (icpsi705, user pimm).

### Further unloader files found by first bytes (task 2), all decoded fully by unlsav's parser

| archive!member | bytes | modules | compiled | host | externals |
|---|---|---|---|---|---|
| exper-apps/klic/alignga/software.tgz!software/gav/PIM/gav.unload | 112,542 | 28 | 1994-11-07..1995-01-09 | icpsi559 | PIMOS only |
| !software/gav/PIM/dayhoff.unload | 12,904 | 1 | 1994-11-07 | icpsi559 | none |
| exper-apps/pimos/editalign.tar.Z!src/pimos/rf.exe | 167,186 | 28 | 1993-03-30 | icpsi551 | shoen |
| exper-apps/pimos/multialign.tar.Z!src/pia_s2.exe | 79,004 | 14 | 1993-03-25 | icpsi551 | PIMOS only |
| !src/tpia_s2.exe | 118,376 | 21 | 1993-04-01 | icpsi551 | PIMOS only |
| exper-apps/pimos/mendels.tar.Z!mendels/mendel.exe | 76,098 | 16 | 1992-05-20 | tspsi316 | PIMOS only (compile, load, relink, shell...) |
| !mendels/mdllibrary.exe | 1,632 | 3 | 1992-07-16 | tspsi579 | none |
| solver-prover/simpos/papyrus.tar.Z!source.tar!demo/P_TERM/KL1_SAV/papyrus.sav.1 | 23,856 | 8 | 1992-04-09 | icpsi180 | `$plib$timer` (in plib.sav.1) |
| !demo/P_TERM/KL1_SAV/plib.sav.1 | 23,978 | 6 ($plib$window, file, timer, string_io, error, plib) | no info vector | - | PIMOS only |

JIS-damaged unloader files (16-bit words written as ISO-2022-JP text; full-width ASCII folded to ASCII):
helic2.tar.Z!helic2/LEGAL/RBR/PROGRAM/plib.sav (33,174; the IFS copyright header is prepended as text, so
the damage was done when the release was stamped), helic2!LEGAL/CBR/REASON/bin/cbr.exe (122,711),
cbr_eng.exe (122,820), cbcdss.tar.Z!cbsdss/failN.exe (20,003; module node1, package pmpsi, host mkpsi000),
rodin.sav. `bin/rodin_unjis.py` (K mode = word verbatim, A mode = one byte = one word, letters at a
code-tag position = 0x23xx atom tag) recovers helic2 plib.sav WHOLE: 6/6 modules, 11,989 words, and
against papyrus's undamaged plib.sav.1 every one of 1,425 differing words is a fold (0x00b vs the
full-width b, incl. 0x2121 space, 0x2170 `$`): structure byte-exact, character words need context.
rodin 4/111, cbr/cbr_eng 2/10, failN 0/167: extra single-byte losses (e.g. 0x0002 and 0x000a written as
one byte without a mode switch); mechanism not settled.

## Task 2: census

`bin/census.py` read all 310 top-level archives + 95 nested ones (one level) + 2,835 loose files under
ifs/ and icot-other/ (36,953 rows, `notes/census_ifs.tsv`, columns container, member, size, first 16 bytes,
flags, string hits). One nested archive failed to open (contract-research/96/DH8-26/H8-26.tgz!H8-26.tgz).
contract-research holds 88 project directories (95: 20, 96: 27, 97: 22, 98: 19) and 88 report directories, 184 subdirectories in all; all walked. The survey's "186 directories walked" is a count of the server walk; no contradiction established. The one unopened nested archive, H8-26.tgz!H8-26.tgz, is 0 bytes.

- No `.kbn`, `.mbn`, `.sym`, `.ldb`, firmware or microcode file; no `pimm_patch.com`; no `mpsi_*`/`ppim_*`
  object file. The one `A5 C3..C9` hit (pia_klic/ATTENTION.j) is EUC text, not a PDSS save.
- `.com` (335): PIMOS listener/shell command files and SIMPOS command files (kappa-p 120, kappa2 51,
  helic2 24, rodin 22, quixote 15, mmi 10...). gdcc.com, Nseq.com, aliases.com read: listener scripts.
  None is a CSP/firmware patch file.
- **pimos.h**: symbolic-proc/klic-apps/d-pool/dpool_pimos.tgz!dpool/src/{owner-fixed,owner-migration,
  access-info}/pimos.h (6,037 bytes, identical, (C)1995): the PIMOS machine-configuration header that
  75 files of the 3.6 source `include("pimos.h")` but which no held PIMOS archive contains
  (pimos, pimosobj, pimosman, psdpim, vpim, pkl1, pdss: 0 members). Table in task 3.
- SIMPOS package files (`0001 len name`, the `.ptf` container): kappa2.tar.Z!kappa2/ptf/kappa.ptf;
  utter.tar.Z!PTF/{fts,qxt,sancho2,tour}.ptf (+ package.dir, a JIS-text package list);
  papyrus.tar.Z!source.tar!demo/PACKAGE/*.pak.1 (10 files).
- PSI font/icon files of PIMOS applications: celplace (GRID36io/arrow/title.font), examds/font (4),
  gog-kl1 (suuji, suuji2 .font; gog/yubi .icon); gog-esp fonts have another header (f822).
- PIM/m version stamps: editalign and multialign INSTALL: "PIMOS:PIMOS/CAL/CSP/KL1/KL0/ParaG
  Version 0000/0000/0117/023500/000000/3200", "PIM/m-CSP Version 01.17", "Machine: PIM model-m or
  Multi-PSI", SIMPOS 8.1 (PSI2) / 8.2 (PSIUX). mmi: PIMOS(3000)/CAL(0192)/CSP(0334)/KL1(012107)/
  KL0(019200)/ParaG(3010). The tuple format is not in the 3.6 source (grep ParaG, CAL().
- FEP/CSP code: only `mpsicsp##pimos_echo_off_window` named inside papyrus plib.sav.1 and
  `pimfep##as_pimos_string_io_device` referenced by papyrus.pak.1 (a class of the held pimfep.ptf).
- `.esp`: 2,476 members; 49 members contain `simpos##`.

## Task 3: machine switches

pimos.h (dpool copy), `:- define(machine, pimm)` selected; cases mpsi, pimm, pimp, pimc, pimk, pimi, pims:

| define | mpsi | pimm | pimp | pimc | pimk | pimi | pims |
|---|---|---|---|---|---|---|---|
| ipl_parameter | no | yes | yes | yes | yes | yes | no |
| double_width_integer, bignum, floating_point | yes | yes | yes | no | no | no | yes |
| apply_tracing/spying, shoen_profile | yes | yes | yes | yes | yes | no | yes |
| processor_profile | yes | yes | yes | no | yes | no | yes |
| fep_interface | kl1_network | scsi | scsi | scsi | scsi | scsi | scsi |
| machine_type | mpsi | **mpsi** | vpim | vpim | vpim | vpim | vpim |
| user_defined_macro, supply_atom_number | yes | yes | no | no | no | no | no |
| extended_floating_point | no | yes | no | no | no | no | no |
| string_operation | yes for all |

`pimi_scsi` / `pim_scsi`: in no IFS member, not in VPIM src, not in pimos.h (agrep over all of ifs/ and
icot-other/: only pimos.h matched `switch(machine`/`case(pimk)`).
VPIM src (185 `.psl.c`): no conditional compilation per machine (PSL directives are `#PSL_`, `#DATA_`,
`#CONST_`, `#ADDR_define` ...); machine differences appear only in comments, 34 files: PIM/p (64-bit
word, byte addressing, local memory from address 0, MRBorRead, deref instruction, 2-word time),
PIM/k (byte addressing, `_ADDRESS_BOUNDARY_MASK` 0xfffffff8 with PIM/p), PIM/i (local memory; GC
masks 0x7f/0x3ff with PIM/k), PIM/c (goal-stack entry 4, CISC opcode table), PIM/s (19 files: console
queues, ms timer, slit-check register, SCSI buffers as strings; VPIM's own runtime, INFERENCE).
Hosts in headers: icot22, ss-pimp2, /usr/pimp/ICOT/V10-scsi. Counts with FILE NAME/LAST SAVED/CREATED lines removed: PIM/p 22 files 54 lines; PIM/s 19 files 43 lines; PIM/k 3 files 10 lines; PIM/i 3 files 4 lines; PIM/c 2 files 2 lines; `PIM/[ik]` 1 file 2 lines. VPIM does hold the firmware side of SCSI (f_scsi_tgt_*, f_scsi_intr_*, str_scsi_record, klb_body_blt_simple_io).

## Task 4: .ptf

ptfdump (via `bin/ptfwrap.py`, monkeypatched `member`) parses all: kappa 797 classes (797 exact),
fts 21, qxt 19, sancho2 18 (17 exact), tour 46; papyrus.pak 176 (176 exact, 110,361 cells);
system_* and cap_* .pak small (1-7 classes; cap_proof 637 KB but 98 cells: data, INFERENCE).
With the five IFS .ptf added, PMI opcodes used rise 101 -> 105, BLT 111 -> 127; still every one has a
sysidat entry. simpos## classes: psdpim+paragraph 144, IFS 152, both 91, union 205
(`notes/ptf_simpos.txt` lists them). Known plaintext: kappa2 holds 651 .esp; 696 of 797 ptf classes
have a same-named ESP class (case-folded); utter holds 74 .esp; papyrus 161 .esp.1.

## Task 5: FGCS'92 PIM/m benchmarks (M92 Table 1: append 1,000 elements; best-path 90,000 nodes;
pentomino 8x5 box; 15-puzzle 5,885 K nodes)

- append: pdss.tar.Z!sample/append.kl1 (422), pkl1.tar.Z!samples/nrev.kl1; KLIC tests.
- best-path: pdss.tar.Z!sample/bestpath.kl1 (493) is a driver calling `bp:bp/8`; no `bp` module anywhere.
  Tutorial versions: manuals/kl1/kl1-text.tar.Z!kl1-text/chuukyu/chu-3.2.tex, beginner/examples.tex;
  the PIMOS manuals' `bestpath(a,z,Path)` example.
- pentomino: not held (only an "R pentomino" Life pattern in contest/1997/life-v1.tar.gz).
- 15-puzzle: symbolic-proc/pimos/ldlib.tar.Z!src/sample/p_15p.kl1 (6,180), p_15pm.kl1 (5,838, Manhattan
  heuristic), tpa_15pm.kl1 (1,608, PA*), tsrtc_15p.kl1 (1,257): KLIB problem code for PIMOS 3.4+;
  not shown to be the M92 program.
- Other period benchmark names: PDSS sample bup, qlay, queen, semi, tri, espascal; KLIC test qlay,
  life, kkqueen, pascal, mastermind, puzzle (Tick's 5x4x3), nqueen; 8-puzzle and queens in ldlib.

## Additions after review (all MEASURED unless marked)

- IPL: `kl1decomp.py ipl_file_decoder check_magic_num/13` shows two accepted magics, one with a comment
  (decode_string) and one without, anything else `abnormal("Illegal IPL File")`; that they are 5702h
  and 5502h is from `gap_analysis.md` (SECONDARY here). So the 5602 package file is refused. Magic
  acceptance is necessary, not sufficient: these are application modules meant for PIMOS's `load`
  (gdcc.init: `package:define(gdcc,pimos)`, then `alg`, `simplex`, `bool`, `parser` each defined over
  `gdcc`, `setenv task:package=...`, `load("shell.sav")`, ...; alg's `var` resolves to `gdcc::var`).
- Opcodes (unlsav op byte of `inst` items): 3.6 objects use 178 distinct, the 25 IFS files 147; three
  are not in the 3.6 set: 0x1b `clause_info` (in kl1_encoding.md; dpool owner-fixed 258, owner-migration
  387) and 0x43 (4), 0x44 (2) in mmi system.sav (1992, PIMOS 3.0), which are absent from kl1_encoding.md:
  version drift, and the mmi file will not run as-is on a 3.6-only opcode set.
- Source join (`bin/srcjoin.py`, `:- module` in the same archive): gdcc 61/67 modules, mmi 53/63,
  dpool 12/12, MGTP 6/7 (gc.sav none), rf.exe 27/28, pia/tpia 31/35, mendel 18/19, gav 29/29;
  papyrus.sav.1 0/8 and plib 0/6 (no KL1 source in papyrus). Some misses are my `2`->`_` renaming.
- First bytes of held firmware (pimm.MEkbn 0042 0000, sysidat 0068 0000, sysinit 0050 0000,
  pimm_ipl.kbn 0000 00e0, .ldb 214e 214f) match no census member; syspsi (zeros) and .sym (JIS spaces)
  match only unrelated Windows .aps/.res files and editalign stem.res.
- Unloader pattern anywhere in a member (`ESC $ B U 02` or `55 02 00 ? ff ff 00 00`): exactly the 30
  files above (25 undamaged + 5 JIS-damaged); nothing new.
- FEP halves (8-bit search): 86 members in 37 archives match; the first match in each is: 66 for `pimfep##as_pimos_string_io_device`, 11 for
  `mpsicsp##as_pimos_string_io_device`, 2 `pimfep##pimos_remote_login_requester`, 2+1
  `mpsicsp/pimmcsp##pseudo_csp_main_program`, 1 `mpsicsp##pimos_echo_off_window` in 37 archives
  (quixote, voronoi, kappa-p, dulcinea, disc, argus-v, sme, papyrus, examds 12, mendels 7, exreps,
  pmonitor, helic2, cbcdss ...): the FEP halves of IFS PIMOS packages inherit one class of the held
  `pimfep.ptf` (or the Multi-PSI one). Search was 8-bit only (not two-byte JIS) except for the
  unloader/ptf work.
- `.esp` naming `simpos##` in their text: 31 members (kappa2 10/651, cil 5/32, cal-esp 4/59, exreps 2/7,
  quixote 2/7, voronoi, kappa-p, gog-esp, gog-kl1, chal, alignsa, aligndp 1 each). Most ESP source
  names SIMPOS classes without the package prefix.
- pimos.h: the 3.6 source tests 19 names with `switch`/`if_equal`/`if_defined`; all 16 names pimos.h
  defines are among them (the other three, `included`, `autoloading`, `increment`, are file-local).
  `switch(ipl_parameter)` is in `bios/boot/bios.kl1:52` only. A 1995 copy of unknown PIMOS version.
- Best-path: the KL1 textbook prints a complete `bestpath` module
  (manuals/kl1/kl1-text.tar.Z!kl1-text/chuukyu/chu-3.2.tex, lines 670-830, several verbatim blocks;
  a small fixed network), and pimosman `Eman/e-listener.tex` shows `bestpath(a,z,Path)` interrupted
  after 1,167,807 msec. Neither is the 90,000-node benchmark.

## Task 6: ESP manuals (ifs/manuals/esp/)

| archive | members (bytes) |
|---|---|
| ESPtex.tar.Z | overview-e.tex 96,154; program-e.tex 364,418 |
| ESPtex-j.tar.Z | overview-j.tex 103,751; program-j.tex 376,006 |
| ESPps.tar.Z | overview-e.ps 304,075 (53 pp); program-e.ps 964,003 (211 pp) |
| ESPps-j.tar.Z | overview-j.ps 670,070 (50 pp); program-j.ps 1,474,622 (212 pp) |

Title pages: "OVERVIEW" and "PROGRAMMING", "ICOT : Institute for New Generation Computer Technology 1990"
(all dated Aug 1992 in the tar). The Overview lists the four SIMPOS manuals: 1 Overview, 2 Operations,
3 Programming, 4 Japanese document edition. Overview sections: ICOT; How to use the manual; Understanding
PSI (knowledge EWS; PSI hardware configuration diagram; "Basic Specifications of PSI Hardware" table for
the PSI II: microprogram 53 bits x 16 KW at 200 or 167 ns; 120-400 KLIPS, "1.4 MLIPS for the latest
machine"; 40-bit word, 8-bit tag; register file 64 W; two-level mapping, area table 17 bits x 8, page
table 17 bits x 96; 26-bit logical address; 8 interrupt levels; cache one set, write back, 4 KW, 4 W/block;
three timers; traps Error, GC call, Class; 23 built-in exceptions, user-definable; IEEE754 FPU option;
memory 1.2 us / 4 words, 7-bit ECC, 40 MB basic, 160 MB max); Understanding SIMPOS (purpose, features,
structure: operating system, programming system); Understanding ESP (object orientation and Prolog,
program configuration, classes, compile and link, object generation, methods, slots, packages, macros,
include, bind hook, KL0 built-in predicates: 8 categories with examples, not a list).
Programming: 1 ESP Programming (data structures, writing a program, a tree-sort example); 4 ESP/SIMPOS
Programming Techniques (object orientation, packages, good programming, data manipulation, execution
control, macros and operators, sorting, speed/memory techniques, evaluation). The "SIMPOS programming
system" part the Overview describes (how programs use the window and file systems) is NOT in the held
Programming volume, English or Japanese (TOC and the .ps page counts agree). No SIMPOS class reference.

## Status changes for environment_audit.md

| item | old | new | evidence |
|---|---|---|---|
| §5 item 1, the 16 `.sav` | not decoded, "56 02 same family INFERENCE" | 15 decode fully with unlsav; 5602 = package file (READ unlver.kl1), decodes after skipping the package atom; dates, hosts, externals tabulated | savsum.txt, dates.txt |
| rodin.sav "possible seventeenth" | undetermined | a 5502 file (111 modules) damaged by a 16-bit-to-JIS text conversion; 4/111 recovered | rodin_decode.txt |
| §F count of PIMOS-format object files | 16 (+1) | 25 undamaged + 5 JIS-damaged (`.exe`, `.unload`, `.sav.1` names) | census, agrep_unl.txt |
| §5 item 2 | names only | members and first bytes of all archives: no firmware, microcode, `.kbn/.mbn/.sym/.ldb`, `pimm_patch.com`, `mpsi_*` objects | census_ifs.tsv, fw_magics.txt |
| §L "PIM/m builds take the mpsi branch of machine_type" | INFERENCE | READ in pimos.h: `case(pimm)` -> `machine_type mpsi` | dpool pimos.h |
| §L / §4.3 PIM/k PIMOS build: "no case(pimk) anywhere" | NOT-SEARCHED elsewhere | `case(pimk)` exists in pimos.h (vpim, no bignum/float, ipl_parameter yes) | same |
| pimos.h itself | not mentioned (75 source files include it) | HELD only in IFS dpool (1995 copy) | agrep, tar -t |
| §5 item 7, `ipl_parameter` branch | unknown | pimos.h sets `ipl_parameter yes` for pimm (for that 1995 header; the 3.6 binary itself not checked) | same |
| §5 item 9, `pimi_scsi`/`pim_scsi` | NOT-SEARCHED elsewhere | not in VPIM src, not in any IFS/icot-other member | agrep_machine.txt |
| §5 item 10 VPIM conditionals | not searched | no per-machine conditional code; differences only in comments (counts above) | grep |
| §G `.ptf` kappa2/utter | not opened | 901 classes, 900 tokenize exactly; opcodes all in sysidat; 205 simpos classes in union; ESP source held for 696/797 kappa classes | ptf_*.txt |
| §G new: papyrus `.pak.1` | - | 10 SIMPOS package files, papyrus.pak 176 classes, with 161 ESP sources | ptfwrap |
| §F FGCS'92 benchmarks | NOT-SEARCHED | append HELD (PDSS sample, pkl1 nrev); best-path driver only + textbook listing; 15-puzzle related KLIB code (ldlib); pentomino NOT FOUND | task 5 |
| §G ESP manuals | held, not read | vols 1 and 3, 1990; vol 3 lacks the window/file-system part; PSI II spec table read | task 6 |
| new: PIM/m version stamp | - | "PIM/m-CSP Version 01.17", PIMOS/CAL/CSP/KL1/KL0/ParaG = 0000/0000/0117/023500/000000/3200 (editalign, multialign INSTALL, 1993) | INSTALL |

## R7/R9 candidates

1. Zero-external modules (load with the IPL loader or `load`, call a predicate, compare with KLIC/source):
   gc.sav (mgtp_gc, 159 cells, no extcalls), SYN002/SYN009/SYN036/test2_445 problem modules (pure
   facts: `preds/1`, `negCls/1`, ...), dayhoff.unload (1 module, a Dayhoff matrix, 1 unknown opcode),
   mdllibrary.exe (3 modules).
2. MGTP set: mgtpNS7.sav + SYN002-1-020dom_merc.sav, run `main:main(50,ns,A)`; expected output recorded
   in H9-07/nseq/pim/aitec19980402.log: "Number of Failed Branches = 43782", "Number of Models = 0",
   "unsat", `genCnt(503)`, 64,089,346 reductions (qc: 65,056,038; mx: 64,075,062). Needs shoen and
   multiple PEs (@node) for the same counts (INFERENCE).
3. gdcc (5 files + gdcc.init/gdcc.com) and dpool (needs `clause_info`), then mmi (needs opcodes 0x43/0x44).
4. Benchmarks: PDSS sample/append, bup, qlay, queen, semi, tri; ldlib 15-puzzle / 8-puzzle / queens.

## Could not do

- rodin, cbr, cbr_eng, failN: lossless reversal; extra byte losses not modelled (stopped by choice).
- Character words of a JIS-damaged file are ambiguous (0x00XX vs full width) outside a parser context.
- String searches were 8-bit; two-byte JIS forms not searched except where stated.
- Did not run any object on a model; did not decompile the IFS objects clause by clause.
- pentomino and the M92 best-path program are not held anywhere searched.
