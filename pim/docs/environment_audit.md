# Environment audit: what a full reconstruction of the PIM/m installation needs, and where each piece stands

Written 2026-11-23. An audit, not a plan: it records for every piece of
the installation what is held, in what form, how well it is documented,
what is only cited, what is lost, and what this project has built. It
cites the project's own notes rather than re-deriving them; where those
notes disagree, both readings are given and the newer named. Where the
audit made its own check, the row says "this audit" with the command or
file:line. Everything else is cited to a file and section or line, or
marked INFERENCE.

## 1. Purpose, goal, vocabulary, sources

### 1.1 The goal

The owner, 2026-11-23, in-session: the goal is **"to recreate the
entire operating environment"** (`pimos_roadmap.md` §2). That is the
installation, not PIMOS alone:

- the PIM/m machine (processing elements, network, memory, caches, and
  the KL1-B firmware with its scheduler, garbage collector and shoen);
- PIMOS and everything it loads: libraries, compiler, tools, utilities,
  applications;
- the PSI beside it (KL0 microcode, ESP, SIMPOS) acting as console
  processor (CSP: clear, init, load microcode, IPL, start) and
  front-end processor (FEP: files, windows, timers, string I/O and
  sockets over SCSI);
- the devices, the media and the documentation.

Done is R1..R9 of `pimos_roadmap.md` §2 together with P0..P5 of its §9.
The owner's order of work, relayed 2026-11-23: **PIM/m first, then the
PSI, then the other PIM machines.** This document follows that order:
areas A-F and H-K are the PIM/m installation, area G the PSI, area L
the other PIM machines and Multi-PSI.

A caution on area A, from the sources: PIM/m has **no clusters, no
shared memory and no cache-coherence protocol**. Each processing element
(PE) has its own local memory and direct-mapped caches, and PEs meet only
over the 2-D mesh (`pim_architecture.md` §1, §6, citing `M92` p. 426,
`TR659` p. 7, `OV92` p. 63). Cluster and coherence items therefore sit
in area L (PIM/p, PIM/c, PIM/i, PIM/k), not in A.

### 1.2 Status vocabulary (used in every row)

| Label | Meaning |
|---|---|
| HELD-SOURCE | source text is held in `docs/nonlocal/` (or a sub-archive), checksummed |
| HELD-OBJECT | compiled object of software whose source is (or might be) separate; runnable on a matching machine |
| HELD-BINARY-ONLY | a binary (microcode image, compiled package) with no source held |
| DOCUMENTED | a held document specifies it well enough to rebuild (cited) |
| PARTIAL | held or documented in part; the row says which part |
| CITED-ONLY | known to exist from a citation; not located |
| LOST | searched for and not found; the row cites the record of the search |
| NOT-SEARCHED | no search for it is on record. This is a claim about the record, not about the world |
| UNKNOWN | the record does not settle it |

"Our status" uses: none; ref (the host reference model `ref/pimm/pimm.py`
alone); both (reference model and Bluespec core `bsv/Pimm*.bsv` in
lockstep); bench (the older `bsv/PimKL1B.bsv`); doc (written up, no
code). Rungs are R1..R9 (`pimos_roadmap.md` §2) and P0..P5 (§9).

A held document is not a read one. Many reports are on disk and unread;
the rows say so ("held, not read").

### 1.3 Sources of this audit

Read for it: `AGENTS.md`; in `pim/docs/`: `pimos_roadmap.md`,
`gap_analysis.md`, `pimos_boot_requirements.md`,
`icot_software_survey.md`, `binary_reverse_engineering.md`,
`pimm_semantics.md`, `kl1_encoding.md` (head), `kl1_model_status.md`,
`pim_architecture.md`, `pseudo_pimm_firmware.md`,
`pseudo_pimm_microcode.md` (head, §18, §20), `pimos_binaries.md`
(SCSI section), `icot_databases.md` (§6.4), `literature_gaps.md` (§7,
§8, "The other PIMs", Appendix D consolidated lists, by grep);
`pim/plan.md`, `pim/bsv/README.md`, `pim/ref/pimm/README.md`; the
manifests `nonlocal/MANIFEST.md`, `IFS_MANIFEST.md`, `LIT_MANIFEST.md`,
`ICOT_OTHER_MANIFEST.md`; headers of `ref/pimm/fep.py`,
`asm/pimm_stubs.py`, `asm/pimm_layout.py`.

Scratch material used read-only (session scratch, not in the
repository; `<scratch>` below is
`/private/tmp/claude-501/-Users-npe-src-living-computing-pim/01b03f2f-1efc-495c-9771-b09885a1fa2f/scratchpad`):
the extracted PIMOS source `<scratch>/pimos/pimos/src`, VPIM
`<scratch>/vpim/vpim`, the manual `<scratch>/man/Eman`, the 3.6 objects
`<scratch>/objx/object`, an agent's shoen specification
`<scratch>/shoen_research/report.txt`. The P0 search's working
manifest was read twice while it ran (136 rows, then 154 at 17:14 on
2026-11-23); its result is now the committed report
`docs/psi_acquisition.md` (commit 7e9dabe6), with 64 new ICOT reports
in `nonlocal/lit/trtm/`, 27 IPSJ papers in `nonlocal/lit/ipsj/` and an
addendum of 2026-11-23 in `nonlocal/LIT_MANIFEST.md`. Area G and §5
cite that report, not the scratch.

Checks made by this audit, 2026-11-23 (all read-only):

- grep of the PIMOS source tree for per-machine `:- case(...)`
  branches (area L);
- a listing of every `.tar.Z`/`.tgz`/`.tar.gz` under `nonlocal/ifs/`
  (298 archives, 30,521 members; list in
  `<scratch>/audit/ifs_members.tsv`), and the first eight bytes of each
  `.sav` member found (areas F and L);
- the cover pages of the held English manual (`e-cover1.tex`,
  `e-v30.tex`).

The working tree had uncommitted changes in `bsv/PimmStages.bsv`,
`ref/pimm/longrun_ipl.py` and `ref/pimm/pimm.py` when this was written
(git status at session start): another agent's work in flight. Model
status below is as the committed docs state it.

## 2. Summary by major component

In the owner's order: PIM/m installation, then the PSI, then the other
PIM machines.

| # | Component | Held form | Documentation | Lost | Our status (2026-11-23) | Blocking what |
|---|---|---|---|---|---|---|
| 1 | PIM/m PE hardware (PU, CU, NU, local memory) | papers only; photos | `M92` pp. 425-435, TR-733, TR-564, TR-742, TR-799, TM-1074, TM-1159 (held); per-stage latencies, cache/memory timing not published (`pim_architecture.md` §7) | design documents, microinstruction-level manuals (none ever located) | bench diagnostic PE (`PimPU`), labelled model ISA; no caches; not used by the KL1-B core | cycle accuracy (§7 of roadmap); not on the path to R8 |
| 2 | PIM/m network (NU, 2-D mesh) | papers only | `M92` p. 427 mechanism; packet format and arbitration not printed | packet/frame encoding | bench mesh (`PimMesh.bsv`), all MODEL choices | multi-PE work after R8 |
| 3 | KL1-B instruction set (PIM/m dialect) | encoding table in PIMOS assembler source; 726,053 instructions of real object code; decode table in Pseudo PIM/m firmware | encoding DOCUMENTED (`kl1_encoding.md`); semantics PARTIAL (`pimm_semantics.md`: 112 rows) | the machine's own per-instruction definition (firmware) | 116 instructions on both models (`bsv/README.md`) | R3..R8 (each missing instruction stops a run) |
| 4 | KL1-B runtime (scheduler, priorities, suspension, shoen, GC, exceptions, inter-PE) | real PIM/m firmware LOST; Pseudo PIM/m microcode HELD-BINARY-ONLY; PDSS (C) and VPIM (PSL) sibling sources HELD | behaviour from manuals, Multi-PSI/V2 TRs, PDSS, VPIM; field layouts partly read from microcode (`pseudo_pimm_microcode.md` §17-18) | PIM/m microcode in any form (`icot_software_survey.md` §4, §6) | our own layouts (`asm/pimm_layout.py`), one ready list, no priorities, no shoen, no GC, no exceptions | R4 (shoen at boot step 1, `gap_analysis.md` §1) and everything after |
| 5 | Boot: IPL image, symbols, CSP boot functions | `pimm_ipl.kbn`, `.sym`, `.ldb`, `pimos.ipl`, `boot.init` HELD; IPL modules object only | `.kbn` format DOCUMENTED (`pimos_boot_requirements.md` §0.3); boot sequence decompiled (`binary_reverse_engineering.md` §1.3-1.4) | IPL module source; `pimm_patch.com`; real CSP software and manual | IPL loads and links all 20 files on BOTH models, 447,739,516 trace lines identical (`bsv/run_pimm_longrun.sh`, 2026-11-23); on ref alone `pim:go/4` then shows the banner and stops at `scsi_where` (`longrun_ipl.py --reference --go`) | R5 |
| 6 | PIMOS 3.6 (kernel, servers, shell, debugger, utility, library, macro, bios) | source (485 `.kl1` under `src/`) and 1994 objects (20 `.sav`, 502 modules) HELD | manual V3.0 (Nov 1991, LaTeX and PostScript) HELD; source is the patched May-1994 text (INFERENCE, `binary_reverse_engineering.md` §2) | PIMOS 1.x-3.5 code; the internal file system | `hasher:hash/3` from a `.sav` runs on both (R2); kernel not entered | R5..R8 |
| 7 | KL1 toolchain (compiler, assembler, loader, unloader, kbn) | HELD-SOURCE and HELD-OBJECT | manual `e-compiler.tex`; source | CAL cross system (built `.kbn` to PIMOS 2.5) | encoding transcribed; tools not run on any model | R7, R8 (and every IFS application shipped as source) |
| 8 | FEP link and services, PIM/m side | PIMOS clients HELD-SOURCE; IPL-time client object only | `scsi_fep.kl1`, `pimos.vmac` (105 codes), IPL packet layout (`binary_reverse_engineering.md` §1.4) | none on this side | `fep.py` (OURS) serves the IPL's file reads on ref only | R4 on Bluespec; window/timer for R6 |
| 9 | Applications (IFS) | all 98 entries with files HELD as archives (`IFS_MANIFEST.md`); members listed by this audit, none unpacked; 25 of 43 PIMOS packages carry `.esp` FEP halves; 16 PIMOS-format `.sav` found (§F) | per-package docs inside archives (not read) | QUTE (26), SAM (27): no archive | none | R9 |
| 10 | Devices and media (disks, SCSI, consoles, network, tape) | none (no disk or tape image of any ICOT system) | SCSI side from PIMOS source (`pimos_binaries.md`); PIM/m disks from `M92` p. 426 | every installation disk/tape | `scsi_command` against `fep.py` on ref only | R4 on Bluespec; R6+ |
| 11 | Documentation | 2.18 GB of literature (`LIT_MANIFEST.md`), PIMOS/KL1/ESP manuals, IFS newsletters HELD | n/a | CSP manuals (Multi-PSI/V2, PIM/m), SIMPOS manuals of PSI-II/III era, PIMOS 2.5 manual: CITED-ONLY | many held reports unread | interpretation everywhere |
| 12 | Our scaffolding | n/a | `pimm_semantics.md`, `pimm_layout.py`, `pimm_stubs.py`, `fep.py` headers | n/a | in use; each labelled OURS | to be replaced as sources are read |
| 13 | PSI hardware and KL0 microcode (PSI-I/II/III) | PSI-III control store `syspsi`, `sysidat`, `sysinit` HELD-BINARY-ONLY; papers | TR-265 (PSI-II, held, read); PSI-I well documented, PSI-III thin, no microinstruction-format document (`psi_acquisition.md` §3); TM-862: PSI-III and the PIM/m PE are one chip | KL0 source; PSI-I/II microcode; any PSI emulator (searched 2026-11-23) | `sysidat` read as the KL0 decode table; nothing executed | P1, P2 |
| 14 | SIMPOS and ESP | ESP manuals HELD (volumes 1 and 3 of 4, not opened by the project); SIMPOS none | 24 SIMPOS reports now held (`psi_acquisition.md` §5); other manuals CITED-ONLY | SIMPOS (all forms) and the PSI's ESP system: LOST, searched 2026-11-23 twice (`psi_acquisition.md` §1, §2, §9; classes partly printed, §7 below); Common ESP CITED-ONLY (tape only) | none | P3, P4; every ESP application and FEP half |
| 15 | CSP and FEP software (ESP, for SIMPOS) | `pimmcsp`, `pimmutil`, `mpsicspR`, `pimfep`, `pimscsi` `.ptf` HELD-BINARY-ONLY; `paragraph.ptf` with source | container parsed (`asm/ptfdump.py`); command table recovered | their ESP source | container and tables read; KL0 opcodes about ten named | P3, P5 |
| 16 | Other PIM machines (PIM/p, /c, /i, /k) and Multi-PSI | papers; VPIM source (all PIMs but PIM/m) HELD; PIMOS source has `mpsi`, `pimp`, `pimc`, `pimi`, `vpim` branches | `literature_gaps.md` "The other PIMs"; TM-1044 | all their firmware, back ends, PSL translator, per-machine object sets, Multi-PSI `.mbn` | none | the third phase of the owner's order |

## 3. Detailed inventory

Columns: item | needed for | held? (path, form) | documented? | status
| our status | notes and evidence. Paths under `nonlocal/` are
`pim/docs/nonlocal/`.

### A. PIM/m hardware

| Item | Needed for | Held? | Documented? | Status | Ours | Notes |
|---|---|---|---|---|---|---|
| System shape: up to 256 PEs, 16x16 mesh, 32 PEs per cabinet (8x4) | multi-PE (roadmap §7) | papers: `docs/FGCS92_Volume_1.pdf` (`M92`), `nonlocal/tr/TR-0742.pdf`; photos `nonlocal/pim-m/photos/` (9) | yes, `pim_architecture.md` §1 (`M92` pp. 425-426) | DOCUMENTED | bench: `PimMesh.bsv` (w x h, XY routes, MODEL) | photos are of the machine, not evidence of layout |
| PE pipeline D/A/R/S/E | cycle accuracy | papers | stage roles only (`pim_architecture.md` §2, `M92` p. 428); no per-stage latency, interlock or branch penalty (§7) | PARTIAL | bench `PimStages`/`PimE` (diagnostic ISA, two E phases collapsed, labelled); the KL1-B core is sequential, "no timing claimed" (`bsv/README.md`) | the Pseudo PIM/m microcode is the only possible source of step counts (`binary_reverse_engineering.md` §3) |
| The PU chip: one processor for PIM/m (KL1) and the PSI-III / PSI/UX (ESP) | cycle accuracy; P1 | TM-862, TM-858, TR-799, TM-1159, TM-1074, TR-564 (`nonlocal/lit/trtm/`, `nonlocal/tr/`, `nonlocal/tm/`) | TM-862: "PU has capability to execute two different type logic programming languages, KL1 for PIM/m and ESP for the AI workstation" (`psi_acquisition.md` §3); `M92` p. 426 | DOCUMENTED (identity); PARTIAL (internals) | bench `PimPU` only | the held PSI-III microprogram (`pimm.MEkbn`) therefore runs on PIM/m's own PU; see area G's note |
| Datapath registers (An/Xn 32w, WR 32w, PC, SP, XR/YR, MAR1/2, MDR1/2) | cycle accuracy, firmware reading | papers | names and roles (`pim_architecture.md` §6, `M92` p. 427); An/Xn split not stated | PARTIAL | bench `PimE` (16/16 split MODEL) | the `rassy` tables name 32 + 8 + special registers (`binary_reverse_engineering.md` §3); agreement with `M92` not checked |
| Word and tags: 40-bit, 8-bit tag | everything | PIMOS source `debugger/inspector/tagtbl.kl1` (59 tags), `library/kbn/kbnheap.kl1` | numeric tag values from PIMOS source (`pimos_boot_requirements.md` §0.3); not printed in any PIM/m paper (`pim_architecture.md` §3) | DOCUMENTED (from software) | both models use the real tags | the `GOAL` tag's value: in `rassy` (`into`=00 .. `goal`=3c, `binary_reverse_engineering.md` §3); the 60th console tag (`pseudo_pimm_firmware.md` §2) |
| MRB (multiple reference bit), SRP/COL | GC fidelity, reuse | papers | `M92` pp. 428-430; position in tag not stated (`pim_architecture.md` §3); low tag bit is OUR reading (`pimos_boot_requirements.md` §0.3) | PARTIAL | both: bit kept, `set_vector_element` in place on it; nothing reclaimed (`pimm_semantics.md` "The MRB") | rules taken from PDSS where `M92` is silent |
| Writable control store 32K x 64 bit; decode RAM; tag-jump RAM | firmware | papers; the Pseudo PIM/m decode table is in `pimm.MEkbn` | mechanism `M92` pp. 426-429; 64-bit field layout TR-733 fig. 4 (`literature_gaps.md` §8; `nonlocal/lit/trtm/tr0733.pdf`) | PARTIAL | bench `PimPU` WCS (diagnostic); `asm/mekbn.py` reads the Pseudo PIM/m words | `pim_architecture.md` §5 says the layout is "not printed anywhere in these sources" (it read `M92`, `OV92`, `TR659` only); `literature_gaps.md` §8 found TR-733 fig. 4 later. Both stand; the newer finding is the second *2026-11-23: `mekbn.py` now decodes by the PSI-III layout of Nakashima's thesis Fig. 3-25, which the held stores fit better than TR-733 fig. 4 in bits 36..23 (`psi_microword.md` section 7; `pim_architecture.md` section 5).* |
| Local memory: 16 M words x 40 bit per PE | memory sizing | papers | `M92` p. 426 | DOCUMENTED | both models: 2^27 cells (128 M), OURS, chosen because nothing is reused (`gap_analysis.md` B8) | our memory is 8x the machine's per-PE memory; a run that needs it would not have fitted a PIM/m PE without GC (INFERENCE) |
| Instruction cache 1K words, data cache 4K words, direct-mapped | cycle accuracy | papers | sizes and mapping (`pim_architecture.md` §6); write policy, hit/miss latency not stated | PARTIAL | none ("no cache", `gap_analysis.md` §D) | |
| Shared memory, clusters, coherence protocol | n/a for PIM/m | — | PIM/m has none (`TR659` p. 7, `OV92` p. 63, via `pim_architecture.md` §6) | not applicable | — | see area L for the cluster machines |
| Inter-PE network: NU 5x5 crossbar, 9-bit packet byte, RAM route table, 1 byte / 4 cycles | multi-PE | papers | mechanism `M92` p. 427; frame format, port numbering, arbitration not printed (`pim_architecture.md` §10) | PARTIAL | bench `PimNU`, `PimLink`, `PimNURouted`, `PimMesh` (MODEL choices, tested) | message contents (KL1 inter-PE messages) are area B |
| Machine cycle 65 ns | timing | papers | `M92` p. 426, `OV92` p. 62, `TR659` p. 6 | DOCUMENTED | not used | Both figures are printed (§6 item 4): 60 ns in TR-564 p. 2, FGCS'92 Vol. 1 p. 45 Fig. 7 and TR-799; 65 ns in `M92`, `OV92`, TM-1074 and TR-733 (FGCS'92 Vol. 1 p. 43 prints 50 under PIM/m, probably swapped with PIM/c). 65 ns is probably worst case and 60 ns typical (INFERENCE). Any timing claim must name which figure it uses. *(Cell rewritten 2026-11-23; it said: `gap_analysis.md` §D says "60 ns cycle", `pim_architecture.md` says 65 ns from three sources, 65 ns is the cited figure.)* |
| SCSI attachment (one PE in eight has a SCSI board, 670 MB disk and the FEP) | I/O | papers | TR-733 via `literature_gaps.md` §8; `M92` p. 426 (four 670 MB disks per cabinet) | PARTIAL | `scsi_init`/`scsi_command` on ref only | SCSI controller chip, interrupt wiring: not documented in anything read |
| Console attachment (CSP, maintenance architecture) | boot | `nonlocal/lit/trtm/tm1213.pdf` | TM-1213 read from page images (`literature_gaps.md` §8a); IPSJ 122850 (PIM/m maintenance architecture and console processor) is now held in `nonlocal/lit/ipsj/` (`psi_acquisition.md` §5), not read | PARTIAL | none | how the CSP reaches the PE (bus, registers) is in TM-1213 as far as it goes; not transcribed here |
| Real PIM/m hardware | reference | National Museum of Nature and Science, Tokyo (IPSJ page, `icot_software_survey.md` §5.2) | — | UNKNOWN (preserved, not examined) | — | whether media came with it: unknown (`literature_gaps.md` Appendix D, ranked item 2) |

Held but not read, all bearing on A: TM-850 (PIM/m PE architecture),
TM-849 (Microlint), TM-1021, TM-1022 (FEP) (`literature_gaps.md`
line 1389: "resolved, not read (titles read)"; all on disk in
`nonlocal/lit/trtm/`).

### B. PIM/m firmware: the KL1-B machine

What PDSS, VPIM and `psdpim` are, stated once: **PDSS** V2.52.20 is a
KL1-B interpreter in C by the PIMOS group, a sibling dialect (save magic
`0xA5C3`-`0xA5C9`, other opcode numbers) that builds and runs here
(`pimos_boot_requirements.md` §0.1, "PDSS runs"). **VPIM** is the
runtime of every PIM except PIM/m, in PSL, read-only, with no
translator (`nonlocal/MANIFEST.md` §1a). **`psdpim`** is the Pseudo
PIM/m: PIM/m's KL1 firmware rebuilt as PSI-III microcode
(`pimm.MEkbn`), binary only, the system the 3.6 objects were built to
run on. None is PIM/m; `psdpim` is the closest (same firmware line,
`literature_gaps.md` "The other PIMs").

Instruction families, with the object-set census
(`pimos_boot_requirements.md` §0.5). Per-family coverage by the models
is not on record: the model documents give only the total (116 on both
when this audit was written; 128 since the merge of 2026-11-23,
`bsv/README.md`, `ref/pimm/README.md`), and the rows of the next table say per family what
is known.

| Family | Object set: mnemonics | uses | IPL image: mnemonics | uses |
|---|---|---|---|---|
| unification/structure | 56 | 504,586 | 51 | 8,143 |
| goal control | 14 | 117,634 | 9 | 2,197 |
| heap/gc/profile | 8 | 57,556 | 4 | 911 |
| indexing | 6 | 20,821 | 6 | 429 |
| guard type/compare | 8 | 9,923 | 7 | 547 |
| string/vector built-ins | 18 | 7,222 | 13 | 287 |
| integer arithmetic | 21 | 5,176 | 18 | 397 |
| code/module/atom objects | 13 | 1,228 | 11 | 51 |
| device | 14 | 563 | 5 | 137 |
| float | 16 | 485 | 2 | 8 |
| bignum/extended integer | 9 | 322 | 0 | 0 |
| shoen/priority/processor | 19 | 278 | 17 | 48 |
| extended float | 43 | 259 | 1 | 1 |
| **total** | **245** | **726,053** | **144** | **13,156** |

| Item | Needed for | Held? | Documented? | Status | Ours | Notes |
|---|---|---|---|---|---|---|
| KL1-B encoding (opcode, operands, per family) | R1.. | `pimos.tar.Z` `library/assembler/inst_tab.kl1` (263 encodings), `klb_opr.kl1` | `kl1_encoding.md`; checked against the firmware's decode table both ways (`pseudo_pimm_firmware.md` §1) | DOCUMENTED | both models decode from generated tables (`asm/gen_pimm_bsv.py`) | 13 quick forms used in 1994 are commented out in the 1992 table; names known (`pimos_boot_requirements.md` §0.2) |
| Object-set census: 197 (tag,opcode) pairs, 245 mnemonics with sub-functions, 726,053 instructions | sizing | the 20 `.sav` | `pimos_boot_requirements.md` §0.2, §0.5 | DOCUMENTED | `asm/census.py --check`, `asm/inventory.py` | |
| Unification/structure family (56 mnemonics, 504,586 uses) | R2.. | — | semantics per instruction in `pimm_semantics.md`, from paired source/object, manual, PDSS | PARTIAL | both: most of it; structure-structure unification by OUR stub `unify_step` (PDSS's way) | vectors of 7+ not unified (`pimm_semantics.md` row "unification of two lists") |
| Goal control: `enqueue_goal`, `execute`, `proceed`, `suspend`, `otherwise`, `try_me_else`, `save`/`restore`, `jump` | R2.. | — | `pimm_semantics.md`; `save`/`restore` (17,538 uses) semantics unread (`gap_analysis.md` B1) | PARTIAL | both, except `save`/`restore`, `jump` (not in IPL) | microcode entries `3211`/`3215` named as the place to read them (`gap_analysis.md` B1) |
| Goal record and ready queue | R3.. | microcode (binary) | PIM/m layout not in print; partly read from microcode: `HOOK` points at cell 0, cells 12-14 on one path of `suspend`, 16 cells and cell-15 link INFERENCE (`pseudo_pimm_microcode.md` §18) | PARTIAL | OURS: `asm/pimm_layout.py` (4+n cells, one ready list, newest first) | the console inspectors for goal records are compiled ESP in `pimmcsp` (`binary_reverse_engineering.md` §3); unread |
| Priorities (goal stack per priority, 256-entry Goal Stack Entry Table) | R5.. (PIMOS starts at priority 4050) | `PIMM.PARAM` (binary package) | priority encoding not known (`gap_analysis.md` B4) | PARTIAL | OURS: priority carried and dropped; `calculate_priority_from_minimum` range OURS (`pimm_semantics.md`) | Goal Stack Entry Table use not found in microcode (`pseudo_pimm_microcode.md` §18 "Not recovered") |
| Suspension and resumption (HOOK, MHOOK, DREF, multiple-suspension record) | R3 | microcode | multiple-suspension record's four fields and tags read, order conditional (`pseudo_pimm_microcode.md` §17); siblings' scheme in `literature_gaps.md` §2 | PARTIAL | both: OUR scheme (HOOK -> suspension record always) | known to differ from the documented siblings (`pimm_semantics.md` "Runtime state") |
| Body built-in that waits | R2.. | — | PDSS `body_builtin_suspend`; PIM/m representation unknown | PARTIAL | both: OUR stubs (`asm/pimm_stubs.py`, 71 stubs, 260 cells) | |
| Built-ins: count and provenance | R2..R8 | compiler `library/compiler/blt.kl1`: 87 guard and 120 body built-ins (`pimm_semantics.md`, `asm/bltdir.py`). Three different units: 207 compiler built-ins (language level); 116 KL1-B instructions implemented on both models (`bsv/README.md`; instructions, not built-ins; 128 since later on 2026-11-23, §6 item 2); 112 rows in `pimm_semantics.md`'s table (one per instruction or instruction group); 71 stubs for waiting body built-ins (`asm/pimm_stubs.py`) | manual `e-builtin.tex` for meaning; directions from `blt.kl1` | PARTIAL | 116 instructions on both models when written, 128 now (`bsv/README.md`) | **This audit's count** (reading each of the 112 rows of `pimm_semantics.md` lines 49-165 for the words OURS, PDSS and REFERENCE MODEL ONLY; a hand count, not a script): 8 rows have semantics that are partly OURS (`new_atom` numbering, `calculate_priority_from_minimum` range, `enqueue_goal_with_priority` priority dropped, `enqueue_goal_to_processor` one PE, `read_eagerly` no-op, `scsi_init` values, `scsi_command` waiting, `merge` not the machine's merger); 2 more have only a Bluespec step count of ours (`b_multiply`, guard `modulo`); 17 rows cite PDSS for part of their meaning (e.g. `hash` function, MRB rules, sign of `modulo`); 11 are REFERENCE MODEL ONLY. The rest rest on paired source/object or the manual |
| Shoen built-ins (`create_shoen` .. `shoen_profile`, 10 instructions) and `raise`, `current_node`, `supply_atom_number`, `halt`, `put_console`, `calculate_priority_from_current` | R4 (`ipl:boot/0` calls `shoen:execute/4` first, `gap_analysis.md` §1) | — | encodings and directions from source; protocol from `kernel/builtin/shoen.kl1`, manual `e-shoen.tex`; record field order of the Pseudo PIM/m console (24 and 14 fields, `pseudo_pimm_firmware.md` §2); PDSS and VPIM behaviour | PARTIAL | none: no handler in `pimm.py` for any of them (`<scratch>/shoen_research/report.txt` §7) | that report (an agent's, scratch, not committed) specifies a minimal shoen and lists what is unsourced: when reports 8/12/14 are emitted, whether a shoen with no resource runs, the priority formulas (§8) |
| Exceptions (built-in error -> report to shoen) | R5.. | `kernel/builtin/excpt_tbl.kl1` source | info codes in source and manual; mechanism not | PARTIAL | none: every built-in error stops the model (`gap_analysis.md` B5) | |
| MRB reclamation (`collect_*`, `put_reused_structure`) | R5..R8 heap use | — | `M92` pp. 429-430, TR-248 | PARTIAL | `collect_*` do nothing; reuse always copies (`pimm_semantics.md`) | |
| Garbage collection (free pools, batch copying collector) | R5..R8 | microcode; `PIMM.PARAM` | PIM/m: free pools and a moving batch collector (`M92` p. 430); copying per Pseudo PIM/m strings and Multi-PSI/V2 TR-469, TR-715 (`literature_gaps.md` §7) | PARTIAL | none; memory sized up instead (2^27 cells) | the whole `pimos.ipl` link needs ~73 M cells with no reuse (`gap_analysis.md` B8) |
| Inter-PE: export/import tables, weighted reference counts, messages | multi-PE | `PIMM.PARAM` sizes; VPIM source | entry fields from the console (`pseudo_pimm_firmware.md` §2); Multi-PSI/V2 TR-715, TR-390 (`literature_gaps.md` §6) | PARTIAL | none (one PE, decision 2) | message byte formats unknown (`literature_gaps.md` "Which sibling") |
| Code and module objects (`predicate_to_code`, `new_module`, `apply`, `code`, external calls) | R4 | image and source | TM-662 module format (read, `literature_gaps.md` §8a); `kbn.kl1` | DOCUMENTED (as used) | both | the external-call cache field is not written (`pimm_semantics.md` `execute_external`) |
| Console primitives (`display_console`, `put_console`, `read_console`, `get_console`) | R4, R5 | — | PDSS manual meaning; how PIM/m rendered values unknown | PARTIAL | `display_console` on both (trace lines); others none (`gap_analysis.md` C1) | |
| SCSI primitives (`scsi_init`, `scsi_command`, `scsi_where`, `scsi_transfer`, ...) | R4 | `bios/scsi/scsi_blt.kl1` (stand-in source) | arguments from `compiler/blt.kl1`; values OURS | PARTIAL | ref only (`ref_scsi.py`) | `scsi_transfer` is used once by the objects and absent from the held firmware (`pseudo_pimm_firmware.md` §1). The one use is the listener's typed-command pass-through (`com_built.kl1`:135), not a boot path (§6 item 13) |
| Floats, extended floats, bignums (68 mnemonics, 1,066 uses) | applications | — | manual; `kbnheap.kl1` tags | PARTIAL | none beyond type tests | deferred by design (`pimos_boot_requirements.md` §0.5) |
| Atom-number service (`supply_atom_number`, `new_atom`) | R4, R5 | — | directions only for `supply_atom_number` | PARTIAL | `new_atom` on both with OUR numbering from 10000h (`pimm_semantics.md`); `supply_atom_number` on both, what it does OURS (inputs dropped, Done never bound), `top:go1/4`'s server run with the bench binding Done (`lockstep_atom.py`) | what `supply_atom_number`'s two integers mean (a block's first number or its end) |
| The microprogram itself (`pimm.MEkbn`, 18,343 words, 324 entry points) | fidelity of all of B; cycle counts | `nonlocal/psdpim.tar.Z` `PMPSI.DIR/pimm.MEkbn` | memory datapath read; ~23 of 64 bits fully characterised (INFERENCE tally, `binary_reverse_engineering.md` §3) | HELD-BINARY-ONLY | read-only tools `asm/psdpim.py`, `asm/mekbn.py` | the firmware's own reverse assembler `pimmutil##rassy` is held as compiled ESP and would give the format (`binary_reverse_engineering.md` §3) |
| Real PIM/m microcode, microassembler, Microlint | authenticity | none | TR-742, TM-849 (title) | LOST (`icot_software_survey.md` §4 table, §6 "Not found by anyone") | — | the Pseudo PIM/m is "converted from Multi-PSI/V2" like the real one; how far the two microprograms differ is UNKNOWN |

### C. IPL and boot

The boot sequence on the Pseudo PIM/m, from the held `boot.init`:
clear, init, `impl` (load microcode `/usr/psi/pimos/kl1/pimm.MEkbn`),
`patch(on,"pmpsi:pimm_patch.com")`, `ipl(on,"pimos:pimm_ipl.kbn",
"pimos:pimm_ipl.sym")`, `start(pimos,"20c")` (`icot_software_survey.md`
§1 row 3).

| Item | Needed for | Held? | Documented? | Status | Ours | Notes |
|---|---|---|---|---|---|---|
| IPL heap image `pimm_ipl.kbn` (92,160 B, 20 modules, 349 predicates) | R4 | `nonlocal/pimosobj.tar.Z` `object/` | format from `library/kbn/` source; fully placed (`pimos_boot_requirements.md` §0.3) | HELD-OBJECT | both models load it; `asm/kbn.py --check` | header word 126-127 "Version" `0x01973460` not interpreted (§0.3) |
| IPL module source (`ipl`, `top`, `ipl_loader`, `ipl_module`, `ipl_pool`, `ipl_link_table`, `ipl_scsi`, `ipl_file_decoder`, four `scsi_fep_*`) | R4 understanding | object only | decompiled to KL1, 1,023 clauses (`binary_reverse_engineering.md` §1.1); near-source for `ipl_file_decoder` and `scsi_fep_module` (§1.2) | HELD-OBJECT; source LOST (`icot_software_survey.md` §4 "IPL source": absent from `pimos.tar.Z`) | run as held on both models | the 8 source-backed IPL modules are older text than the held source (`binary_reverse_engineering.md` §1.1) |
| `pimm_ipl.sym` (486 atoms), `pimm_ipl.ldb` (777 lines) | R4 | held, two-byte JIS text | read (`binary_reverse_engineering.md` §5) | HELD | `asm/kbndis.py` joins them | |
| `pimos.ipl` (20 files: 8 base sets then 12 patches) | R4 | held | decoded (`icot_software_survey.md` §1 row 5) | HELD | `lockstep_ipll.py`: the IPL reads it on both models | paths `>sys>csp>PIMOS.DIR>pimm_*360E.sav` |
| `pimos.conf`, `pimos.logins`, `pimos.groups`, `pimos.com`, `shell.com` | R5, R6 | held | commented in the files (`icot_software_survey.md` §1 row 12) | HELD | none | `pimos.conf` starts `login:go([{0,local,0},{0,tcpip,0}],[],off)` |
| `login.com`, `init.com` | P5 | held | SIMPOS-side scripts (`init.com` starts `mpsimpc##csp_slave_csp_main`) | HELD | none | belong to the PSI (area G) |
| `boot.init`, `PIMM.PARAM`, `PIMM.CONFIG`, `usercom.init` | R4 boot fidelity; memory map | `nonlocal/psdpim.tar.Z` `SYSTEM.DIR/` | `boot.init` decoded; `PIMM.PARAM` fixed areas read from console text (`pseudo_pimm_firmware.md` §2) | HELD (binary-encoded text) | none | `PIMM.PARAM`'s area map is not used by the models (`gap_analysis.md` §D) |
| `pimm_patch.com` (firmware patch named by `boot.init`) | R4 boot fidelity | no | none | NOT-SEARCHED beyond `psdpim.tar.Z`, from which it is absent (`icot_software_survey.md` §6); `patch` and `.com` were not among the file-name patterns of the 23,910-path mirror search (survey §4) | — | "probably never released; `patch(on,...)` may fail soft" (survey §4, its inference) |
| Start address | R4 | — | `boot.init` `20c`; primer `202` with `pimos.kbn`; CSP help text `2000`/`200`; `.kbn` header `0xE0001E81` | UNKNOWN (not reconciled) | models start at the header's `ipl:boot/0` | `icot_software_survey.md` §7, `literature_gaps.md` §8 table |
| CSP boot functions (clear, init, impl, patch, ipl, start) as software | R4 (a stand-in), P5 (the real one) | Pseudo PIM/m CSP as compiled ESP (`pimmcsp.ptf`, 281 classes incl. `csp_ipl`, `csp_micro_loader`, `csp_boot_menu`) | names only; the operating manual is CITED-ONLY (`icot_software_survey.md` §4) | HELD-BINARY-ONLY | OUR test harness places the image and starts the goal; no CSP stand-in as such | real PIM/m CSP: LOST (survey §4 "CSP software") |
| What the IPL asks of the front end before `pim:go/4` | R4 | object code | read from decompiled code: `read_open "pimos:pimos.ipl"`, `getb` to end of file, then each `.sav`; TEST UNIT READY, SEND, RECEIVE on unit 7 (`binary_reverse_engineering.md` §1.3-1.4) | DOCUMENTED (derived, "not executed" when written) | ref: `ref_scsi.py` runs `ipl:boot0` through `fep.py` | `fep#ipl` (400) and `fep#symbol` (500) are not used by the IPL (§1.4, §4.3), against the survey's earlier inference |
| The boot as a whole (R4: "Link Modules" on the console) | R4 | — | — | — | ref alone: twenty files load and link NORMAL (73 M cells, 15 min, `longrun_ipl.py --reference`); both: one file (`lockstep_link.py`) and a six-module file (part 2) | R4 not claimed (roadmap §2: rungs are claimed on Bluespec) |
| Whether the IPL expects state left by the PSI's loader | R4 | — | — | UNKNOWN (roadmap §5, "Phase 3") | | |

### D. PIMOS

| Item | Needed for | Held? | Documented? | Status | Ours | Notes |
|---|---|---|---|---|---|---|
| Source 3.6 (`src/`: kernel 42 files, bios 35, server 97, shell 45, library 95, utility 43, debugger 116, macro, vm 9) | R5..R8 oracle | `nonlocal/pimos.tar.Z` (706 entries) | manual V3.0 | HELD-SOURCE | read as oracle by lockstep tests | counts: `icot_software_survey.md` §1 row 6. `src/` is the patched, May-1994 text (INFERENCE from predicate sets, `binary_reverse_engineering.md` §2) |
| Object set 3.6 (8 base `.sav`, "PIMM <SET> :3.600:25-Nov-93") | R5..R8 | `nonlocal/pimosobj.tar.Z` | decoded (`pimos_boot_requirements.md` §0.2); 501 of 502 modules have a same-named source module | HELD-OBJECT | loaded by the IPL on ref (all) and both (single files) | source says `"3.600"`, `"20-May-93"` (`kernel/init/version.kl1`); objects say 25-Nov-93. R5's expected console text follows the source (roadmap §2 R5) |
| 12 patch sets (1994-05-12) | R5.. | same | no prose; 24 patch modules, 22 replace base modules (`binary_reverse_engineering.md` §2) | HELD-OBJECT (source: the held `src/` has the patched predicate sets) | loaded on ref | `ifdef_filter` (91 predicates, `library`) has no source module |
| Kernel: shoen manager, resource, exception, init | R5 | source and object | manual `e-shoen.tex`, `e-rsc.tex`, `e-task.tex` | HELD-SOURCE | not entered | |
| Servers started at boot: `scsi_request_server`, `fep_server`, `atom_server`, `module_server`, `user_server`, `pipe_server`, `profiling_server`, `user_server_manager` | R5, R6 | source and object | `kernel/init/rsc_init.kl1` (`icot_databases.md` §6.4) | HELD-SOURCE | none | |
| FEP device clients: `bios/fep_module/` (17 files), `server/fep/` (30 files) | R4..R8 | source and object | `icot_software_survey.md` §1 rows 9-10; manual `e-ioctrl.tex`, `e-strio.tex`, `e-io*.tex` | HELD-SOURCE | none beyond the IPL's own client | file, directory, window, timer, string_io, socket, remote variants |
| Login, telnet, user, pipe, profiler, atom, module servers | R6 | source and object | manual `e-server*.tex`, `e-login.tex` | HELD-SOURCE | none | |
| Shell | R6 | source and object | manual `e-shell.tex` | HELD-SOURCE | none | R6 oracle is the manual's transcript |
| Listener, inspector, tracer, ParaGraph KL1 side (`src/debugger`, 116 files) | R7 | source and object | manual `e-listener.tex`, `e-inspecto.tex`, `e-debug.tex` | HELD-SOURCE | none | |
| Utility (pools, I/O utilities) | R6.. | source and object | manual `e-util.tex`, `e-ioutls.tex` | HELD-SOURCE | `hasher:hash/3` runs on both (R2) | |
| Library (compiler, assembler, loader, unloader, kbn) | R7, R8 | source and object | area E | HELD-SOURCE | see E | |
| Macro sets (`pimos.vmac` etc.) | R7, R8 | source and object | in source | HELD-SOURCE | read for `fep#` codes | |
| BIOS (boot, SCSI, FEP module) | R5 | source and object | in source; `pimos_binaries.md` "SCSI device" | HELD-SOURCE | none (the IPL's older copies run) | `bios.kl1` `:- switch(ipl_parameter)` branch of the build: not determined (`binary_reverse_engineering.md` §7) |
| `src/vm` (VM interface, disk and SCSI simulators) | none on the boot path | source | FGCS'92 PIMOS paper 4.5.4 | HELD-SOURCE | none | whether it is in the object set: UNKNOWN (survey §1 row 14) |
| PIMOS internal file system (FGCS'92 pp. 278-285; TM-1254) | only if wanted (files come through the FEP here) | not in the source release; in the objects not established | described in print | CITED-ONLY (`icot_databases.md` §6.4) | none | TM-1254 is held (`nonlocal/lit/trtm/tm1254.pdf`), not read |
| PIMOS 1.x, 2.x, 3.0-3.5 code; "PIMOS 2.5 Manual" | IFS applications target 3.0-3.5 | manuals 1.5 (English) and 3.0 (Japanese) held (`nonlocal/ifs/manuals/pimos/`) | — | code LOST (`icot_software_survey.md` §4); 2.5 manual CITED-ONLY | none | |
| Manual edition | all | `nonlocal/pimosman.tar.Z` (LaTeX) and `nonlocal/ifs/symbolic-proc/pim-psi/pimosman.ps.Z` | the English manual is "PIMOS Manual (V 3.0)", ICOT PIMOS Developing Group, November 1991 (this audit: `Eman/e-cover1.tex`; `e-v30.tex` says October 1991) | HELD | — | a 3.0 manual for a 3.6 system: R5's sequence in the manual is a V3.0 transcript (roadmap §2 R5) |

### E. The KL1 toolchain

| Item | Needed for | Held? | Documented? | Status | Ours | Notes |
|---|---|---|---|---|---|---|
| PIMOS KL1 compiler (`library/compiler`, 44 files, 17,943 lines) | R7, R8; every IFS app shipped as source | source and object (`pimm_library360E.sav`) | manual `e-compiler.tex`, `e-preproc.tex` | HELD-SOURCE, HELD-OBJECT | `blt.kl1` read for operand directions (`asm/bltdir.py`); compiler not run | R7's first choice is this compiler compiling one clause (roadmap §2) |
| Assembler (`library/assembler`, 5 files) | R7, R8 | source and object | `kl1_encoding.md` | HELD-SOURCE | its table drives our decoders | |
| Loader, unloader, encoder/decoder (`library/loader` 14 files, `unloader` 9) | R7, R8 | source and object | in source | HELD-SOURCE | `asm/unlsav.py` (OURS) decodes `.sav`; the IPL's own decoder runs on both | |
| `kbn` image builder (`library/kbn`, 5 files) | rebuild of an IPL image | source | `pimos_boot_requirements.md` §0.3 | HELD-SOURCE | `asm/kbn.py` reads | the held image's module-reference form differs from what the 1992 `kbn.kl1` writes (§0.3, "06 and 07 cells") |
| Macro expander, preprocessor | R8 | source and object | `e-preproc.tex` | HELD-SOURCE | none | |
| Rebuilding the object set from source | fidelity check | — | — | NOT-SEARCHED (no attempt on record) | none | needs either PIMOS running (R7) or the compiler run on a host KL1 system; PDSS's compiler is a different dialect (`pimos_boot_requirements.md` §0.5a). Clause-level identity of any `.sav` module with source is not established (`binary_reverse_engineering.md` §7) |
| PDSS's own compiler, Micro PIMOS (`mpimos/`) | oracle only | `nonlocal/pdss.tar.Z` | PDSS manual `doc.e/pdss.tex` | HELD-SOURCE | `ref/pdss/` builds and runs N-queens | PDSS's own `test/` directory never run (`gap_analysis.md` §E) |
| KLIC 2.002 (and 1.500, 2.000, 2.001, 3.001) | R8 answer oracle | `nonlocal/klic-2.002.tgz`; `nonlocal/ifs/symbolic-proc/klic-system/`, `KLIC-New/` | in archives | HELD-SOURCE | not built here (on record) | |
| pkl1 samples (`fact`, `nrev`, `qsort`, `kkqueen`, ...) | R8 | `nonlocal/pkl1.tar.Z` | — | HELD-SOURCE | none | |
| CAL cross system (built `.kbn` up to PIMOS 2.5; a SIMPOS program) | history only | no | Japanese PIMOS 3.0 manual §6.1 (SECONDARY in the survey) | LOST (`icot_software_survey.md` §4) | — | |

### F. Applications

**Counts.** The IFS catalogue has 100 entries; 98 have files; by
environment field 49 name PIMOS, 32 SIMPOS, 10 KLIC, 6 Common ESP
(a package can count twice) (`icot_software_survey.md` §0 item 4). All
150 distinct files linked from the catalogue, and the rest of the
server's `ifs/` tree, are held under `nonlocal/ifs/` since 2026-11-20
(`IFS_MANIFEST.md` §1: 1,408 files, "All 150 are held locally").
Entries 26 (QUTE) and 27 (SAM) have no archive: HEAD and GET return 500
on AIST and 404 on the mirror (`IFS_MANIFEST.md` §1); recorded as LOST
for this audit's purposes (catalogued, never deposited or withdrawn, the
survey's reading). The P0 search tried `sam.tar.Z` again on 2026-11-23
and failed (curl exit 22, `<scratch>/psi_search/downloads/FAILED.tsv`).

`icot_software_survey.md` §0 item 4 ("We hold 8 files from 6 entries"),
§2.1 and §5.1 ("download now") predate the 2026-11-20 IFS acquisition;
`IFS_MANIFEST.md` is newer and is the state. Every one of the 156 file
links on the 100 abstract pages answered HTTP 200 on AIST on
2026-11-20 (`icot_software_survey.md` §3). This audit did not map the
43 archives below onto the 49 catalogue entries that name PIMOS (some
entries have two archives, e.g. MGTP).

**This audit's listing** of the 43 archives under `nonlocal/ifs/*/pimos/`
(member names only; nothing extracted except the first 8 bytes of each
`.sav`). Counts are by file extension, so a package that names ESP or
KL1 files otherwise is undercounted.

- 25 of the 43 contain `.esp` files: a front-end half in ESP for SIMPOS,
  which needs the PSI (area G) or a reimplementation. The survey's
  "Whether any of these has an undeclared ESP part is unchecked"
  (§3) is answered for these 25 by name.
- 18 hold none: `consort`, `editalign`, `mssd`, `multialign`,
  `qxt_motif`, `rodin`, `mmi`, `gdcc`, `p-chal`, `robot`, `laputa`, `pax`,
  both `mgtp` archives, `MGTP-N-KL1`, `ppss`, `aya`, `ldlib`.
- **PIMOS-format object files are in the IFS tree.** Sixteen `.sav`
  members begin with `55 02` or `56 02` (the IPL's `check_magic_num/13`
  handles 5502h and 5702h files, `gap_analysis.md` §B, lines 148-150; that
  `56 02` is of the same family is INFERENCE; the 3.6 kernel set begins `57 02`; PDSS saves begin
  `A5 C3`..`A5 C9`, `nonlocal/MANIFEST.md` §1a): five in
  `kbms-clp/pimos/gdcc.tar.gz` (`bool`, `alg`, `shell`, `simplex_if`,
  `parser`), one in `exper-apps/pimos/mmi.tar.Z` (`system.sav`), three
  `dpool.sav` in `symbolic-proc/klic-apps/d-pool/dpool_pimos.tgz`, seven
  in `contract-research/97/DH9-07/H9-07.tgz` (`nseq/pim/*.sav`, MGTP
  runs). `helic2`'s `plib.sav` begins with text (`%(C)1992`).
  `rodin`'s `rodin.sav` begins `1b 24 42 55 02 00 6f ff`: a three-byte
  JIS escape followed by the same `55 02 00 NN ff` pattern as the
  others; undetermined, a possible seventeenth. Which machine and PIMOS
  version built them, and whether `asm/unlsav.py` decodes them: not checked.
  INFERENCE: they are candidates for R7/R9 that need no compiler run.

| Package (archive under `nonlocal/ifs/`) | Members | `.kl1` | `.esp` | `.sav` | Needs a FEP half? |
|---|---|---|---|---|---|
| `exper-apps/pimos/aligndp.tar.Z` | 22 | 8 | 1 | 0 | yes (1 file) |
| `exper-apps/pimos/alignsa.tar.Z` | 23 | 9 | 1 | 0 | yes (1) |
| `exper-apps/pimos/cbcdss.tar.Z` | 157 | 60 | 73 | 0 | yes |
| `exper-apps/pimos/celplace.tar.Z` | 45 | 8 | 14 | 0 | yes |
| `exper-apps/pimos/cohlex.tar.Z` | 118 | 86 | 8 | 0 | yes |
| `exper-apps/pimos/colodex.tar.Z` | 199 | 178 | 1 | 0 | yes (1) |
| `exper-apps/pimos/consort.tar.Z` | 90 | 66 | 0 | 0 | none by name |
| `exper-apps/pimos/desq.tar.Z` | 155 | 66 | 54 | 0 | yes |
| `exper-apps/pimos/editalign.tar.Z` | 147 | 28 | 0 | 0 | none by name |
| `exper-apps/pimos/examds.tar.Z` | 450 | 78 | 182 | 0 | yes |
| `exper-apps/pimos/gog-kl1.tar.Z` | 287 | 50 | 205 | 0 | yes |
| `exper-apps/pimos/gpsstap.tar.Z` | 274 | 19 | 11 | 0 | yes |
| `exper-apps/pimos/helic2.tar.Z` | 286 | 74 | 53 | 1 (text) | yes |
| `exper-apps/pimos/logisim.tar.Z` | 49 | 23 | 1 | 0 | yes (1) |
| `exper-apps/pimos/lsirout.tar.Z` | 27 | 10 | 2 | 0 | yes |
| `exper-apps/pimos/mendels.tar.Z` | 173 | 26 | 109 | 0 | yes |
| `exper-apps/pimos/mmi.tar.Z` | 85 | 51 | 0 | 1 (`55 02`) | none by name |
| `exper-apps/pimos/mssd.tar.Z` | 450 | 12 | 0 | 0 | none by name |
| `exper-apps/pimos/multialign.tar.Z` | 41 | 22 | 0 | 0 | none by name |
| `exper-apps/pimos/pmonitor.tar.Z` | 63 | 27 | 18 | 0 | yes |
| `exper-apps/pimos/qxt_motif.tar.Z` | 12 | 1 | 0 | 0 | none by name |
| `exper-apps/pimos/rodin.tar.Z` | 212 | 124 | 0 | 1 (`1b 24 42` then `55 02`; undetermined) | none by name |
| `exper-apps/pimos/seqanal.tar.Z` | 57 | 17 | 19 | 0 | yes |
| `kbms-clp/pimos/gdcc.tar.gz` | 93 | 64 | 0 | 5 (`55 02`/`56 02`) | none by name |
| `kbms-clp/pimos/kappa-p.tar.Z` | 564 | 344 | 7 | 0 | yes (page file service also needs a FEP shim, `icot_databases.md` §3.2) |
| `kbms-clp/pimos/p-chal.tar.Z` | 12 | 1 | 0 | 0 | none by name |
| `kbms-clp/pimos/quixote.tar.gz` | 546 | 129 | 7 | 0 | yes |
| `kbms-clp/pimos/robot.tar.Z` | 12 | 0 | 0 | 0 | none by name (no `.kl1` either) |
| `kbms-clp/pimos/voronoi.tar.Z` | 39 | 10 | 9 | 0 | yes |
| `natural-lang/pimos/dulcinea.tar.Z` | 190 | 96 | 1 | 0 | yes (1) |
| `natural-lang/pimos/laputa.tar.Z` | 63 | 55 | 0 | 0 | none by name |
| `natural-lang/pimos/pax.tar.Z` | 22 | 2 | 0 | 0 | none by name |
| `solver-prover/pimos/argus-v.tar.Z` | 104 | 70 | 5 | 0 | yes |
| `solver-prover/pimos/MGTP/mgtp.tgz` | 14 | 4 | 0 | 0 | none by name |
| `solver-prover/pimos/mgtp.tar.Z` | 14 | 4 | 0 | 0 | none by name |
| `solver-prover/pimos/MGTP-N/MGTP-N-KL1.tgz` | 14 | 6 | 0 | 0 | none by name |
| `solver-prover/pimos/ppss.tar.Z` | 24 | 16 | 0 | 0 | none by name |
| `solver-prover/pimos/sme.tar.Z` | 49 | 24 | 16 | 0 | yes |
| `symbolic-proc/pimos/aya.tar.Z` | 37 | 20 | 0 | 0 | none by name |
| `symbolic-proc/pimos/exreps.tar.Z` | 28 | 14 | 7 | 0 | yes |
| `symbolic-proc/pimos/kl1graph.tar.Z` | 50 | 12 | 8 | 0 | yes |
| `symbolic-proc/pimos/ldlib.tar.Z` | 100 | 63 | 0 | 0 | none by name |
| `symbolic-proc/pimos/strtgysh.tar.Z` | 54 | 21 | 2 | 0 | yes |

Other application holdings:

| Item | Needed for | Held? | Documented? | Status | Ours | Notes |
|---|---|---|---|---|---|---|
| PIMOS-version targets of the IFS PIMOS packages (3.0 .. 3.5) vs held 3.6 | R9 | abstract pages `nonlocal/ifs/_catalogue/abst/` | `icot_software_survey.md` §3 | UNKNOWN whether they compile unchanged on 3.6 | none | Kappa-P asks for 3.4/3.45 (`icot_databases.md` §6.4) |
| ESP applications for SIMPOS (16 packages) and Common ESP ones (6) | P4+ (the PSI's own environment) | held as archives (`nonlocal/ifs/*/simpos/`, `*/cesp/`) | per package | HELD-SOURCE (ESP) | none | "stranded" without SIMPOS or Common ESP (`icot_software_survey.md` §0 item 6) |
| KLIC packages (10) | oracle, not the environment | held | — | HELD-SOURCE | none | KLIC, not PIMOS |
| ParaGraph, performance meter, load-balancing library (`src_util/`) | R7 tools | `pimos.tar.Z` `src_util/` (83 `.esp` + KL1); `paragraph.ptf` object | FGCS'92 ParaGraph paper | HELD-SOURCE (ESP and KL1), HELD-OBJECT (`.ptf`) | `paragraph.ptf` used as known plaintext for KL0 (`binary_reverse_engineering.md` §4.2) | `paragraph_version` 3500 in object, 3200 in source |
| PIMOS pools, Distributed Pool, Kappa-P | R9 database candidates | PIMOS source; `dpool_pimos.tgz`; `kappa-p.tar.Z` | `icot_databases.md` §§3.2, 6.5 | HELD | none | |
| FGCS'92 benchmark programs from the PIM/m paper | R9 | not identified as files | `pimos_roadmap.md` §6 | NOT-SEARCHED (as files) | none | |
| KL1 programming contest sources 1996-98 | KLIC-era | `nonlocal/icot-other/pub/contest/` | — | HELD | none | outside the PIM/m era (INFERENCE from dates) |

### H. Devices and media

| Item | Needed for | Held? | Documented? | Status | Ours | Notes |
|---|---|---|---|---|---|---|
| PIM/m disks: four 670 MB per cabinet; one SCSI board per eight PEs | file system, R6+ | none | `M92` p. 426; TR-733 (`literature_gaps.md` §8) | PARTIAL | none | no disk image of any ICOT system was found (`icot_software_survey.md` §6) |
| SCSI target types PIMOS expects: processor (the FEP at unit 7, send LUN 0, receive LUN 1); direct-access disk; sequential (tape) | R4, R6 | source | `pimos_binaries.md` "The SCSI device PIMOS expects"; `bios/scsi/DAM.kl1`, `SAM.kl1` | DOCUMENTED (PIMOS side) | processor target on ref (`fep.py`) | disk and tape paths unexercised |
| The SCSI link on the Pseudo PIM/m (`pseudo_scsi`, no bus) | P5 | `pimscsi.ptf` (binary) | class names (`icot_software_survey.md` §1.1) | HELD-BINARY-ONLY | none | |
| Console / terminal (CSP display, PIMOS windows on the FEP) | R4..R6 | — | window commands from `pimos.vmac`; FEP class list | PARTIAL | console = trace lines (`pimm_semantics.md` `display_console`) | how the console rendered a value: UNKNOWN (`gap_analysis.md` C1) |
| Network: TCP/IP sockets and telnet login through the FEP | R6+ | PIMOS socket and telnet clients (source); FEP `pimos_tcpip_socket` (binary) | `pimos.vmac` socket codes 800-812 | PARTIAL | none | `pimos.conf` opens a `tcpip` login (`icot_software_survey.md` §1.1) |
| Cartridge tape (`cmt` class in `pimscsi`) | media | binary | names only | HELD-BINARY-ONLY | none | |
| File formats on the media: `.sav` (unloader), `.kbn` (heap image), `.sym`/`.ldb` (text), `.ptf` (compiled ESP), `.mbn` (microcode), `.com` (patch / command file) | all | examples of all but `.mbn` | `.sav` and `.kbn` decoded (`pimos_boot_requirements.md`); `.ptf` container parsed (`binary_reverse_engineering.md` §4.1); `.mbn` kind named only (`literature_gaps.md` §8) | PARTIAL | `asm/unlsav.py`, `kbn.py`, `ptfdump.py` | |
| SIMPOS file system on the PSI disk (where `pimos:` and `pmpsi:` live) | P4, P5 | none | TR-059, TR-524 now held, not read (`psi_acquisition.md` §5) | LOST with SIMPOS, searched 2026-11-23 (`psi_acquisition.md` §1) | none | on PSI/UX the SIMPOS files sit under `/usr/psi/...` UNIX paths (`icot_software_survey.md` §2.3, its inference) |
| Installation media of any kind (tapes, disk packs, PSI/UX disks) | everything binary | none | — | LOST as far as searched (`icot_software_survey.md` §4.1, §6; `literature_gaps.md` Appendix D) | — | the most recoverable form a SIMPOS could take is a surviving PSI/UX disk (survey §5.2) |

### I. Documentation

| Item | Needed for | Held? | Documented? | Status | Notes |
|---|---|---|---|---|---|
| PIMOS manual V3.0 (English, LaTeX and PostScript) | R5..R8 | `nonlocal/pimosman.tar.Z`; `nonlocal/ifs/symbolic-proc/pim-psi/pimosman.ps.Z` | — | HELD | the roadmap §6 lists the PostScript as "not fetched"; it is held since 2026-11-20 (`IFS_MANIFEST.md`) |
| PIMOS 1.5 manual (English), 3.0 manual (Japanese), primers 1.5 (J) and 2.5/"3.0 Introductory" (E) | boot panel, FEP numbering, IPL §6.1 | `nonlocal/ifs/manuals/pimos/` | — | HELD | 3.0-J read at §6.1 only, primer's boot panel read (`literature_gaps.md` line 1390); the 1.5 manual's appendix on writing a FEP string-I/O device in ESP not read |
| KL1 manuals and tutorial | language | `nonlocal/ifs/manuals/kl1/` | — | HELD | not read on record |
| ESP manuals (4 archives, English and Japanese, PS and TeX) | G, P3 | `nonlocal/ifs/manuals/esp/` | — | HELD | not opened on record; survey §5.1 item 4 calls them needed |
| PDSS manual | runtime reference | `pdss.tar.Z` `doc.e/pdss.tex` | — | HELD | cited throughout `pimm_semantics.md` |
| VPIM manual TM-1044 (Japanese) | runtime reference | `vpim.tar.Z` `DOCUMENT/` | — | HELD | extracted in `literature_gaps.md` Appendix B |
| PIM/m hardware papers: TR-564, TR-742, TR-799, TM-1074, TM-1159; FGCS'92 `M92`; TR-733 | A | `nonlocal/tr/`, `nonlocal/tm/`, `docs/FGCS92_Volume_1.pdf`, `nonlocal/lit/trtm/` | — | HELD, read | `pim_architecture.md`, `literature_gaps.md` §8 |
| PIM/m and Multi-PSI unlisted TMs: TM-850, TM-849, TM-1021, TM-1022, TM-346, TM-768, TM-551, TM-671, TM-261, TM-353, TM-354, TM-212, TM-213 | A, B, G | `nonlocal/lit/trtm/` | — | HELD, not read | `literature_gaps.md` line 1389 |
| TR-373, TM-1203 (KL1 implementation and PIMOS) | B, D | `nonlocal/lit/trtm/tr0373.pdf`, `tm1203.pdf` | — | HELD | TR-373 read from page images (`literature_gaps.md` line 1372); roadmap §6 and `nonlocal/MANIFEST.md` §3 still list both as wanted. `literature_gaps.md` has 2 mentions of TM-1203 and no record of reading it |
| Multi-PSI/V2 KL1 reports: TR-715, TR-439, TR-585, TR-466, TR-390, TR-469, TR-531, TR-248 | B | `nonlocal/lit/trtm/` | — | HELD, read (`literature_gaps.md` line 1449) | Appendix A |
| PIMOS reports TR-483, TR-764; TM-1254 (file system directories) | D | `nonlocal/lit/trtm/` | — | TR-483, TR-764 read; TM-1254 not read | |
| CSP operating manuals: "Multi-PSI/V2 Console System (CSP) Operating Manual", "(Pseudo) Multi-PSI System Administration Manual", any PIM/m CSP manual | C, G | none | — | CITED-ONLY (`literature_gaps.md` Appendix D, ranked items 1 and 4) | the document that would describe CLEAR/INIT/IMPL/IPL |
| PSI CSP manual 1985 ("MP7003-1"), KL0 built-in predicates manual, SIMPOS operating and user manuals, SIMPOS 1.5 changes (1985) | G | catalogue records only (`nonlocal/lit/records/`) | — | CITED-ONLY: one copy each, JAIST Library (`LIT_MANIFEST.md` §5) | |
| PSI-II/III era SIMPOS manuals ("Basic PSI/SIMPOS Operating Manual (1),(2)", "Basic System Administration Manual for PSI/SIMPOS Systems") | G | none | — | CITED-ONLY (`icot_software_survey.md` §4) | |
| ICOT TR/TM with no PDF in the archive (TR-69, 111, 133, 221, 276, 277, 305, 340, 348, 542, 834; TM-72, 81, 127, 376, 542-544, 688, 723, 901, 902, 917, 1168, 1185, 1280, 1281, 1283) | various | none | — | CITED-ONLY; "can be read at National Diet Library ... and Kawasaki Library" (`literature_gaps.md` Appendix D consolidated) | relevance of most not checked |
| Listings with machine-code columns for PIM/m | encoding oracle (`plan.md` gate 3) | none | — | none found (`plan.md` "Definition of the first milestone", substitution) | the assembler table and the binaries stand in |
| IFS newsletters E01-E09, J01-J09 | release history | `nonlocal/ifs/newsletter/` | — | HELD | E01, E04-E09 read by keyword (`icot_software_survey.md` §8) |

### J. Our stand-ins and scaffolding (each OURS)

| Item | What real piece it stands for | Where | What would replace it |
|---|---|---|---|
| `ref/pimm/fep.py` | the FEP: a PSI running SIMPOS with `pimfep.ptf`/`pimscsi.ptf` | header lists OURS choices: buffer size 16000, reply queueing, status 5 for a missing file, `getb` unit (READ since 2026-11-24 from `pimfep##pimos_file` getb/4: 16-bit characters, `source_check_2026-11-24.md` §4; the comment in `fep.py` still says OURS), end-of-data replies, reply cutting | P5: the held `pimfep.ptf` on a PSI model; short of that, a stand-in rewritten from the decompiled FEP classes (`binary_reverse_engineering.md` §4.4) |
| `asm/pimm_layout.py` goal record (4+n cells: link, status, code, argn, args), suspension record (2 cells), one ready list | the firmware's goal record, suspension records and goal stacks per priority | `asm/pimm_layout.py` lines 1-30 | the microcode's layouts (`pseudo_pimm_microcode.md` §17-18), or Multi-PSI/V2's as documented, labelled (`gap_analysis.md` §3) |
| Memory of 2^27 cells, no reuse | a 16 M-word PE memory with free pools and GC | `asm/pimm_layout.py` `ADDR_BITS = 27` | free lists and a copying collector (B, GC row) |
| `asm/pimm_stubs.py` stubs for waiting body built-ins (71 stubs) | the firmware's waiting built-in | file header | the firmware's mechanism when read |
| `merge_in` (`22:00`) | the merger cell (`MGHOK` tag) acting at unification | `asm/pimm_stubs.py` `MERGE_IN`; `pimm_semantics.md` `merge` | a merger on the `MGHOK` tag as TR-466 3.3 describes |
| `unify_step` (`22:01`) | in-place structure unification | `asm/pimm_stubs.py` `UNIFY_STEP` (PDSS's goal form) | the firmware's unifier |
| `new_atom` numbering from 10000h | `supply_atom_number`'s per-processor ranges | `pimm_semantics.md` `new_atom` | the atom-number server path (`top:atom_number_server/7`) |
| `hash` function | PIM/m's hash built-in | PDSS's `blt_b_hash` | lost with the firmware; any function gives correct tables (`pimm_semantics.md` `hash`) |
| `scsi_init` values `1`, `{0,0,0}`, `{16000,8,4,0}` and `scsi_command`'s waiting | the firmware's SCSI primitives | `pimm_semantics.md` rows | the firmware's routines, or a CSP/FEP-side document |
| Test driver and bench (`ref/pimm/driver.py`, `bsv/PimmDriverTb.bsv`) that make variables, spawn goals and stand in for file buffers | the IPL's caller and the FEP | `ref/pimm/README.md` | the IPL started by a CSP stand-in |
| Trace format (I/R/A/M/E/G/W/Q/C/S lines) | nothing: a lockstep instrument | `pimm_semantics.md` "Trace" | stays |
| Bench model `bsv/PimKL1B.bsv` (invented tags, absolute labels, choice points) and diagnostic ISA `PimPU`/`pimasm.py` | early scaffolding | `kl1_model_status.md`, `isa.md` | already superseded by `Pimm*.bsv` for KL1-B (roadmap §8) |
| Lockstep tests (33 when this audit was written; 39 on 2026-11-23, the default list of `bsv/run_pimm_lockstep.sh`) | — | `ref/pimm/lockstep_*.py` | stay as regression |

### K. Tools used to read the artefacts (ours, read-only)

| Tool | Reads | Doc |
|---|---|---|
| `asm/unlsav.py`, `savdump.py`, `savaddr.py`, `census.py`, `inventory.py`, `namemap.py`, `savsrc.py` | `.sav` object files; census; PDSS name map; source pairing | `pimos_boot_requirements.md`, `binary_reverse_engineering.md` §2 |
| `asm/kbn.py`, `kbndis.py`, `kl1decomp.py` | the IPL image; disassembly; decompilation to KL1 | `pimos_boot_requirements.md` §0.3, `binary_reverse_engineering.md` §1 |
| `asm/bltdir.py` | built-in operand directions from `blt.kl1` | `pimm_semantics.md` |
| `asm/psdpim.py`, `mekbn.py` | `psdpim.tar.Z`, the decode table, the microprogram | `pseudo_pimm_firmware.md`, `pseudo_pimm_microcode.md` |
| `asm/ptfdump.py` | compiled ESP `.ptf` packages | `binary_reverse_engineering.md` §4 |
| `asm/gen_pimm_bsv.py`, `sav2hex.py` | generate tables and memory images for Bluespec | `bsv/README.md` |
| `ref/pdss/` | PDSS port (x86_64, below 2 GB) | `ref/pdss/README.md` |

### G. The PSI (console and front-end processor): hardware, KL0, ESP, SIMPOS, CSP, FEP

**P0 result.** The P0 acquisition search finished on 2026-11-23; its
report is `docs/psi_acquisition.md` (commit 7e9dabe6). In one line
(its opening paragraph): "SIMPOS itself, an ESP compiler or runtime for the PSI, and
any PSI emulator were not found anywhere searched." Searched: ICOT Free
Software and the Waseda mirror listing, GitHub, Internet Archive
metadata, bitsavers, the Wayback index of `icot.or.jp/*` (§1, §4).
Not searched: Software Heritage (API refused an anonymous client), the
Kyoto, Tokyo, Keio and KEK mirrors, Oki's technical review, the
Wayback index beyond `icot.or.jp/*` and the first 600 URLs of
`ftp.icot.or.jp` (§7). It fetched 64 ICOT reports (now in
`nonlocal/lit/trtm/`, page scans with no text layer) and 27 IPSJ papers
(`nonlocal/lit/ipsj/`), recorded in the 2026-11-23 addendum of
`nonlocal/LIT_MANIFEST.md`. "Held" for those below means on disk; the
project has not read them unless a row says so.

**The PSI-III and the PIM/m PE are one chip.** TM-862, opened by the P0
agent: "The microprocessor, called PU (Processing Unit), is also used
as a key component of AI workstations. Thus, PU has capability to
execute two different type logic programming languages, KL1 for PIM/m
and ESP for the AI workstation" (`psi_acquisition.md` §3). This agrees
with `M92` p. 426 (the FEP's CPU kernel is the PIM/m PE,
`pim_architecture.md` §1). Consequences: every paper on either machine's
processor bears on both (areas A and G); the held Pseudo PIM/m
microprogram runs on the very processor PIM/m used, so its datapath
reading (`binary_reverse_engineering.md` §3) is a reading of PIM/m's
PU microinstruction (INFERENCE: the chip is the same; whether the
PIM/m PE board wired its control store, memory and network to the PU
as the PSI-III board did is not stated); and P1 (the PSI-III
microinstruction format) and a cycle-level PIM/m PU are one piece of
work (`psi_acquisition.md` §8).

| Item | Needed for | Held? | Documented? | Status | Ours | Notes |
|---|---|---|---|---|---|---|
| PSI-I hardware (1984) | lineage | TM-001, TM-005, TR-013, TR-014, TR-045, TR-052, TR-075, TR-079, TR-142, TR-213, TR-219, TR-236, TR-274, TM-224; FGCS'84 papers; Giho 60(9) 1986 (`psi_acquisition.md` §3) | "best documented" (same); not read by the project | DOCUMENTED (unread) | none | not the machine of this installation |
| PSI-II hardware (1986-87); the Multi-PSI/V2 PE | lineage; area L | TR-265 (read: 53-bit microinstruction, instruction word `001111 \| class(2) \| code(8) \| operand(24)`, `literature_gaps.md` §8); TM-444, TM-661, TM-859; IPSJ papers (`psi_acquisition.md` §3) | "adequate for the architecture; no microinstruction format" (same) | PARTIAL | none | the held PSI-III microcode does not run on a PSI-II (`pimos_roadmap.md` §9) |
| PSI-III / PSI/UX hardware (the PIM/m PU) | P1, P2; area A | TR-714 (Japanese), TM-862, TM-858, TM-856 (cache); Giho 65(6) 1991; IPSJ papers on the PIM/m element processor and FEP (`psi_acquisition.md` §3) | "thin; no microinstruction-format document found" (same); TR-733 fig. 4 gives a PIM/m 64-bit microinstruction layout (`literature_gaps.md` §8); the full ICCD'90 paper is CITED-ONLY (paywalled) | PARTIAL | none | one chip with the PIM/m PE (above) |
| PSI-III microinstruction format | P1 | `pimmutil##rassy` reverse assembler (compiled ESP) holds the field tables | value tables partly extracted (`binary_reverse_engineering.md` §3); bit positions not; no document (`psi_acquisition.md` §3) | PARTIAL | `asm/mekbn.py` fits | "reading the format is reverse engineering, not transcription" (`psi_acquisition.md` §8); `set_mnemonic_file` loads a label file not held *2026-11-23: `mekbn.py` now decodes by the PSI-III layout of Nakashima's thesis Fig. 3-25, which the held stores fit better than TR-733 fig. 4 in bits 36..23 (`psi_microword.md` section 7; `pim_architecture.md` section 5).* |
| KL0 control store `PMPSI.DIR/syspsi` (32,768 x 64-bit) | P1, P2 | `nonlocal/psdpim.tar.Z` | not read; its words 0..57ff equal image 1 of `pimm.MEkbn` (`binary_reverse_engineering.md` §3) | HELD-BINARY-ONLY | none | which file holds KL0: "not established" (`icot_software_survey.md` §2.3), "not yet determined" (`psi_acquisition.md` §4), `syspsi` "from its size and INSTALL's wording" (`binary_reverse_engineering.md` §4.2, §5). Treat as probable, not settled. The KL0 firmware is the `sys*` trio, with `sysidat` as the decode table; all three docs now say so with the same wording (§6 items 6, 20) |
| KL0 decode table `sysidat` (1,024 entries) | P1 | same | read: indexed class x 256 + opcode; covers every opcode the six `.ptf` files use (`binary_reverse_engineering.md` §4.2) | HELD-BINARY-ONLY, read | `asm/ptfdump.py --opcodes` | |
| `sysinit` (8,286 words at `5000`) | P2 | same | not characterised (`binary_reverse_engineering.md` §5) | HELD-BINARY-ONLY | none | |
| KL0 microcode source; PSI-I and PSI-II microcode | authenticity | none | TR-079, FGCS'84 micro-interpreter paper; TM-261, 353, 354, 212, 213 (held, not read) | LOST: "Nothing for PSI-I or PSI-II" (`psi_acquisition.md` §4); `icot_software_survey.md` §4 | — | |
| KL0 language: instruction set and built-ins | P3 | none as a manual | "no standalone specification in the TR/TM lists"; described piecemeal in TR-079, TM-104, TM-444, TM-661 (`psi_acquisition.md` §2); about ten class-0 opcodes named from `paragraph` (`binary_reverse_engineering.md` §4.2); KL0 built-in predicates manual (1985) CITED-ONLY (JAIST) | PARTIAL | `ptfdump.py` | 212 opcodes to name (`binary_reverse_engineering.md` §4.4) |
| ESP language | P3 | IFS `manuals/esp/`: volumes 1 (Overview) and 3 (Programming) of the four SIMPOS/ESP volumes; TR-005, TR-044 (ESP Reference Manual), TR-285, TM-055, TM-134, TM-146, TM-364, TM-388 (ESP Guide) (`psi_acquisition.md` §2) | held, not read by the project | HELD (documents) | none | volumes 2 (Operations) and 4 not found (same) |
| ESP compiler, linker, runtime; the SIMPOS Librarian | P3, P4 | none | manuals above | LOST, searched 2026-11-23 (`psi_acquisition.md` §2: "The ESP system for the PSI: NOT FOUND") | — | |
| Compiled ESP package format (`.ptf`) | P3 | six packages in `psdpim` and `src_util`; `.ptf` also in IFS `kappa2` and `utter` (`psi_acquisition.md` §1; this audit's listing) | container parsed: 554 classes, all landing exactly; every one of 9,815 predicate headers regular (2026-11-24, hash tables counted as `mask+1 + 2*keys + 2` cells; `binary_reverse_engineering.md` §4.1) | PARTIAL | `asm/ptfdump.py --check` | `paragraph.ptf` + `src_util/paragraph/*.esp` is the known plaintext (version 3500 vs 3200). The `kappa2`/`utter` `.ptf` have not been opened |
| SIMPOS: kernel, supervisor, window, file, network, PMACS editor, librarian, debugger, shell | P4 | none | 24 SIMPOS reports now held (TR-046, 055, 056, 057, 059, 061, 283, 524; TM-009, 061, 065, 079, 100, 112, 115, 125, 126, 143, 161, 181, 229, 401, 785, 786) and IPSJ papers (`psi_acquisition.md` §5); not read by the project. "Not found: a SIMPOS class-library reference" (same) | LOST, searched 2026-11-23 (`psi_acquisition.md` §1: "NOT FOUND, as source, binary, tape or disk image") | none | "P4 (SIMPOS) cannot be reached with what is public": media from a holder, or a reconstruction of the classes the held `.ptf` call (`psi_acquisition.md` §8) |
| SIMPOS operating manuals | P4 | volumes 1 and 3 above | — | volumes 2 and 4 not found; 1985 manuals CITED-ONLY (JAIST); PSI-II/III-era manuals CITED-ONLY (area I) | — | |
| Common ESP (CESP 3.3, SunOS 4) | an alternative ESP host | none | IFS newsletter 1992 (free for academic use from AIR, on tape); CMU `cesp.txt` ("not part of the ICOT Free Software"); `ifs/INFO.tar.Z` 1994 (from Mitsubishi Electric Computer Systems (Tokyo)); an ESP-to-CESP conversion guide (`psi_acquisition.md` §2) | CITED-ONLY: distributed on tape, not online (`psi_acquisition.md` §2) | — | whether CESP could load `.ptf`: not determined (`literature_gaps.md` Appendix D ranked 11) |
| CSP software, Pseudo PIM/m: `pimmcsp.ptf` (281 classes), `pimmutil.ptf` (51 by `ptfdump`, 50 in the survey), `mpsicspR.ptf` (30, remote CSP, package `mpsicsp`) | C (boot), P5 | `nonlocal/psdpim.tar.Z` `INSTALL.DIR/` | class names; console text gives record field orders (`pseudo_pimm_firmware.md` §2) | HELD-BINARY-ONLY | text and containers read | includes goal and suspension record inspectors, micro loader, IPL, a second reverse assembler (PSI-II format, INFERENCE) (`binary_reverse_engineering.md` §3) |
| CSP for real PIM/m and for Multi-PSI | authenticity | none | TM-1213 (held, read); IPSJ 122850 (PIM/m maintenance architecture and console processor, now held, `psi_acquisition.md` §5); TR-237, TM-306, TM-696 (same) | LOST (`icot_software_survey.md` §4 "CSP software") | — | |
| FEP software: `pimfep.ptf` (47 classes), `pimscsi.ptf` (24 by `ptfdump`, 23 in the survey) | P5; the authentic far end of R4..R8 | `nonlocal/psdpim.tar.Z` | command table recovered, 98 of 100 names equal to PIMOS's numbers, none differ (`binary_reverse_engineering.md` §4.3); classes and methods listed (`icot_software_survey.md` §1.1) | HELD-BINARY-ONLY | `fep.py` stands in (area J) | decompiling the boot path is about 4,700 cells, "mechanical" after the KL0 disassembler (`binary_reverse_engineering.md` §4.4) |
| FEP and CSP ESP source | P5 fidelity | none | — | LOST (survey §4 "FEP sources"; not found by P0) | — | |
| Fonts (`FONT.DIR/*.font`), `csp.icon` | P4/P5 cosmetics | `psdpim.tar.Z` | not examined | HELD-BINARY-ONLY | none | |
| The PSI's own devices: bitmap display, keyboard and mouse, disk, Ethernet, printer, SCSI to PIM/m | P4, P5 | none | SIMPOS window, file and network reports and TM-401 (PSI network) now held, unread (`psi_acquisition.md` §5); `ifs/INFO.tar.Z` names PSI-dependent built-ins `word`, `set_system_register`, `address` (§2) | PARTIAL (documents held, unread) | none | |
| PSI/UX's UNIX side (SIMPOS files under `/usr/psi/...`) | P4 | none | `psdpim` `INSTALL`, `boot.init` paths | UNKNOWN; that PSI/UX runs SIMPOS beside UNIX is the survey's inference (§2.3) | — | |
| Any PSI, PSI-II, PSI-III emulator, simulator, FPGA or RTL | P2 shortcut | none | ICOT had a PSI-II microprogram simulator, "ZEUS" (IPSJ paper, `psi_acquisition.md` §3) | LOST, searched 2026-11-23 (`psi_acquisition.md` §4: "NOT FOUND") | — | |
| Surviving PSI hardware | reference | JAIST Collection of Symbolic Processing Computers: "PSI (ICOT)", "Related manuals and materials are also preserved" (`psi_acquisition.md` §4) | — | UNKNOWN (model and working state not stated) | — | not contacted (`psi_acquisition.md` §6) |
| Rungs P0..P5 | — | — | — | P0 done 2026-11-23; P1..P5 not started | none | `pimos_roadmap.md` §9; `psi_acquisition.md` §8 |

### L. The other PIM machines and Multi-PSI

The two families (`literature_gaps.md` "The other PIMs", quoting `OV92`
p. 61): PIM/m and PIM/c interpret KL1-B by horizontal microprogram;
PIM/p, PIM/i and PIM/k run code below KL1-B. By runtime, Multi-PSI/V2
and PIM/m share one microprogrammed KL1-B implementation; PIM/p, /c,
/i, /k take theirs from VPIM. **Relation to the PSI generations:**
Multi-PSI/V2 is up to 64 PSI-II CPUs on an 8x8 mesh (TR-715 §3, via
`literature_gaps.md`); PIM/m's PE CPU is the PSI/UX (PSI-III) CPU
(`M92` p. 426); a PSI-II or PSI/UX was the FEP and CSP host of both
(`icot_software_survey.md` §2.2, §2.5). Multi-PSI/V1: "The Multi-PSI/V1 (up to 6 PEs) used the
first version of the PSI as PEs" (TR-439, via `literature_gaps.md`
line 1883); its KL1 had no inter-PE GC (TR-390, same line). TR-237
("The Parallel Software R&D Tool: Multi-PSI System", 1987) is held
since P0 (`psi_acquisition.md` §5), not read.

**PIMOS builds, this audit's grep** of `<scratch>/pimos/pimos/src`
(the 3.6 source): `:- switch(machine)` has branches `case(mpsi,pimm)`
(19 sites, e.g. `macro/pimos/pimos/pimos.vmac:290, 425, 439, 460`,
`server/profiler/converter.kl1:38`), `case(pimp)`
(`pimos.vmac:429, 444, 465`), `case(pimc)` (`pimos.vmac:432`),
`case(pimi)` (`macro/pimos/scsi/scsi.vmac:14`); **no `case(pimk)`**.
`:- switch(machine_type)` has `case(mpsi)` (9 sites, e.g.
`kernel/builtin/shoen.kl1:13`, `kernel/builtin/excpt_tbl.kl1:17`,
`bios/boot/sysTdvc.kl1:19`) and `case(vpim)` (9 sites, e.g.
`pimos.vmac:383`, `bios/boot/scsi_man.kl1:98`, `bios/boot/sysTdvc.kl1:22`).
Several of those switches also have a `:- default.` branch (e.g.
`bios/boot/scsi_man.kl1:96, 110`). INFERENCE: PIM/m builds take the
`mpsi` branch of `machine_type` (the only named case besides `vpim`;
the `default` branches leave the question open). The `pimi` branch maps SCSI built-ins to
modules `pimi_scsi` and `pim_scsi`; **no source file declares either
module** (this audit: `grep -rl pimi_scsi` finds only `scsi.vmac`). The
only object set held is PIM/m's (`pimm_*`, `pimosobj.tar.Z` `object/`);
the Japanese 3.0 manual names `mpsi_bios.sav` and `ppim_bios.sav`
(`icot_software_survey.md` §7, SECONDARY there). The `pimosobj` `INSTALL`
targets "Pseudo PIM/M system or Psuedo Multi-PSI system" on "PSI-II or
PSI-UX" (this audit read `<scratch>/objx/object/INSTALL`).

**Simulators.** VPIM is "the source code for KL1 language processor of
all models of the PIM except PIM/m", run during development "on
commercial parallel processors (such as Sequent Symmetry) and on
workstations (such as SUN) after translation into C" (VPIM `README`,
read by this audit); the translator is not in the archive
(`nonlocal/MANIFEST.md` §1a). PDSS is "widely compatible with the KL1
system found on Multi-PSI" (same, quoting PDSS `README`).

| Machine | Item | Needed for | Held? | Documented? | Status | Ours | Notes |
|---|---|---|---|---|---|---|---|
| Multi-PSI/V2 | hardware (64 PSI-II PEs, 8x8 mesh, 200 ns) | lineage; L phase | TR-715, TM-696, TM-306 and others (`nonlocal/lit/trtm/`; TM-306 and TM-696 added by P0, `psi_acquisition.md` §5) | behaviour, costs, packet format, free lists, GC; no record field orders (`literature_gaps.md` "The other PIMs" table, Appendix A) | PARTIAL | none | |
| Multi-PSI/V2 | KL1 microcode (`.mbn` CLEAR/INIT/IMPL, `kl1kp.kbn`, `kl1pat.com`) and Pseudo Multi-PSI for PSI-II | L phase | none | primer (read) names the files | LOST (`icot_software_survey.md` §4, "Not found"; the 23,910-path mirror search used `kbn`, `micro`, `firm`, `csp`, `fep` among its patterns, survey §4) | — | the held `psdpim` is for PSI-III; its `mpsicspR.ptf` is the remote half of a Multi-PSI CSP |
| Multi-PSI/V2 | CSP and its manual | L phase | none | manual CITED-ONLY | LOST / CITED-ONLY | — | |
| Multi-PSI/V2 | PIMOS build | L phase | source branches `mpsi` (above); no Multi-PSI object set | — | PARTIAL (source); objects NOT-SEARCHED beyond the IFS tree's file names (see §5) | none | PIMOS 1.x-2.5 ran here first (survey §2.4); that code is LOST |
| Multi-PSI/V2 | simulator | L phase | PDSS (compatible KL1, not a machine simulator) | — | HELD-SOURCE (PDSS) | `ref/pdss/` builds | |
| Multi-PSI/V1 | hardware and KL1 | lineage | TR-237 (held, unread); TR-439, TR-390 mention it | up to 6 PSI-I PEs; no inter-PE GC (`literature_gaps.md` line 1883) | CITED-ONLY (hardware); software NOT-SEARCHED | none | |
| PIM/p (Fujitsu) | hardware | L phase | TR-577, TR-453, TM-1067, TM-1257, TM-1320, FGCS'92 pp. 414-424, FGCS'94 pp. 80-89 (`literature_gaps.md` "detail" §1; held in `lit/`) | instruction and pipeline level | DOCUMENTED (as far as published) | none | MRB bit position not published |
| PIM/p | KL1 native code generator, macro library, firmware | L phase | none | — | LOST (`literature_gaps.md` "detail" §8; `icot_software_survey.md` §2.6) | — | |
| PIM/p | PIMOS build | L phase | `case(pimp)` branches (timer units in usec, float limits); no object set | — | PARTIAL (source); objects NOT-SEARCHED | none | |
| PIM/p, /c, /i, /k | KL1 runtime (VPIM, PSL) | L phase | `nonlocal/vpim.tar.Z` (185 `.psl.c` files) | TM-1044 (Japanese) in the archive; Appendix B of `literature_gaps.md` | HELD-SOURCE (no translator, headers or build files) | none | VPIM's report numbering for shoen differs from PIM/m's (`<scratch>/shoen_research/report.txt` §2) |
| PIM/p, /c, /i, /k | PSL-to-C translator, per-machine back ends | L phase | none | TM-1044 | LOST (`icot_software_survey.md` §4) | — | |
| PIM/p, PIM/m | preserved machines | reference | National Museum of Nature and Science (IPSJ page) | — | UNKNOWN (media not examined) | — | |
| PIM/c (Hitachi) | hardware | L phase | TR-672, TR-671, TM-870, TR-863, TM-1260, FGCS'92 pp. 723-730 | micro-step timing, datapath, word width, firmware generation method | PARTIAL | none | |
| PIM/c | microcode ("KL1B/c" generated from VPIM) | L phase | none | — | LOST (`literature_gaps.md` "detail" §8) | — | |
| PIM/c | PIMOS build | L phase | `case(pimc)` (`pimos.vmac:432`, timer unit `usec15`); no object set | — | PARTIAL; objects NOT-SEARCHED | none | |
| PIM/i (Oki) | hardware | L phase | TR-675, TM-1017, TM-1264 | instruction list and formats; tag layout (lock, GC, MRB, 5-bit type) | PARTIAL | none | |
| PIM/i | native code, library | L phase | none | — | LOST | — | |
| PIM/i | PIMOS build | L phase | `case(pimi)` in `scsi.vmac:14` only; it names modules `pimi_scsi`, `pim_scsi` absent from the source tree | — | PARTIAL; the missing modules NOT-SEARCHED elsewhere | none | |
| PIM/k (Toshiba) | hardware | L phase | TR-767, TR-768, TR-769, TM-766, TM-1260 | cache hierarchy, processor chip name (IP1704) | PARTIAL | none | |
| PIM/k | runtime (VPIM hand-ported), native code | L phase | none beyond VPIM | — | LOST | — | |
| PIM/k | PIMOS build | L phase | no `case(pimk)` anywhere in the 3.6 source (this audit) | — | NOT-SEARCHED elsewhere | none | either PIM/k used a generic (`vpim`/`default`) branch or its build is not in this release (INFERENCE) |
| all four | cluster shared memory and its cache-coherence protocols | L phase | papers | `OV92` p. 63 Table 4 ("write-back coherent protocols", via `pim_architecture.md` §6); per machine in `literature_gaps.md` "detail" | PARTIAL | none | the PIM/m caution of §1.1 applies: none of this is PIM/m |

## 4. What is lost and must be reconstructed, ranked

In the owner's order: PIM/m, then the PSI, then the other PIMs. Within
each machine, by how much of that machine's environment the item
blocks. "Lost" here includes the PIM/m runtime layouts that were never
printed and exist only inside a binary we cannot yet read: they must be
reconstructed whether or not the binary is ever read in full.

### 4.1 PIM/m installation

| Rank | Lost item | Blocks | A reconstruction would rest on | Attainable fidelity |
|---|---|---|---|---|
| 1 | **PIM/m KL1 firmware** (real microcode; and the Pseudo PIM/m microcode's meaning beyond what is read) | every rung from R3 on: scheduler, priorities, suspension, shoen, exceptions, GC, inter-PE | the Pseudo PIM/m microprogram (`pimm.MEkbn`, held binary) read through `pimmutil##rassy` (`binary_reverse_engineering.md` §3, §6 step 4); PIMOS's own use of every built-in (source and objects); the console's record inspectors; Multi-PSI/V2 reports (same firmware line); PDSS (executable sibling); VPIM | behaviour: high where the microprogram is read, otherwise "documented sibling" level, labelled. Cycle counts: only as PSI-III microcode step counts, which are not PIM/m's 65 ns pipeline timings (INFERENCE) |
| 2 | **Shoen and priority machinery** as the firmware did it (part of 1, ranked separately because it gates R4) | R4 (`ipl:boot/0` creates a shoen at its first step) | PIMOS `shoen.kl1` protocol, image's `shoen` module, manual `e-shoen.tex`, Pseudo PIM/m record field orders (24 and 14 fields), PDSS `shoen.c`, VPIM (`<scratch>/shoen_research/report.txt`) | protocol: high (source on both ends); timing of reports and resource defaults: unsourced, must be chosen and labelled (report §5, §8) |
| 3 | **Garbage collector and free pools** | R5..R8 at realistic memory sizes (73 M cells for the link alone without reuse, `gap_analysis.md` B8) | `M92` p. 430; TR-469, TR-715 (Multi-PSI/V2); Pseudo PIM/m "Copying GC" strings and `PIMM.PARAM` limits (`literature_gaps.md` §7) | scheme: medium-high; parameters (pool sizes, trigger): low |
| 4 | **The FEP as it behaved** (its source is lost; binary held; see also 4.2) | authentic I/O for R4..R8: file, window, timer, string I/O, sockets | PIMOS clients (source), `pimos.vmac` codes, decompiled IPL client, `pimfep.ptf` once KL0 is disassembled | protocol: high (both sides' code); window appearance and timing: low |
| 5 | **Real PIM/m CSP software and its manual** | boot fidelity (impl, patch, start; console) | `boot.init`, `PIMM.PARAM`, TM-1213, the Pseudo PIM/m CSP (`pimmcsp.ptf`) | functional: high (small job); the real machine's maintenance path: low |
| 6 | **IPL module source** | nothing functional (objects run); readability | `kl1decomp.py` output; near-source modules | high (the object code is the program) |
| 7 | **`pimm_patch.com`** | exact firmware state at boot | nothing; possibly never released (survey §4) | none; record its absence |
| 8 | **PIMOS internal file system** (in print, not in the release) | only an on-PIM disk configuration; not this one | FGCS'92 pp. 278-285, TM-1254 (held, unread), Kappa-P's client | low-medium; and it would be a new program, labelled |
| 9 | **PIMOS 1.x-3.5 code** | IFS applications written for 3.0-3.5, if they do not run on 3.6 | the 3.6 source; manuals 1.5 and 3.0 | n/a: run on 3.6 and record differences |
| 10 | **PIM/m timing detail** (per-stage latencies, cache and memory latencies, write policy) | cycle accuracy | `M92` (sparse), TM-850 (held, unread), the microcode's step counts | low; most cannot be claimed (`plan.md` evidence gate 4) |
| 11 | **CAL cross system** | nothing for 3.6 (the IPL image is held) | — | not needed |
| 12 | **IFS entries 26 (QUTE) and 27 (SAM)** | two applications | — | none |

### 4.2 The PSI

| Rank | Lost item | Blocks | A reconstruction would rest on | Attainable fidelity |
|---|---|---|---|---|
| 1 | **SIMPOS** (all forms; not found, searched 2026-11-23, `psi_acquisition.md` §1) | P4, hence the authentic CSP and FEP (P5) and every ESP application | the 24 SIMPOS reports and IPSJ papers P0 fetched and ESP/SIMPOS manual volumes 1 and 3 (`psi_acquisition.md` §2, §5); the method and class names the held packages call (`simpos##...`); the 16 + 6 ESP applications as usage evidence | the classes the FEP and CSP call: medium (behaviour as seen from callers); SIMPOS as a whole: low. Labelled a reconstruction (`pimos_roadmap.md` §9) |
| 2 | **ESP compiler, runtime and Librarian** (not found, searched 2026-11-23, `psi_acquisition.md` §2) | P3 (loading `.ptf`), compiling any held `.esp` source (ParaGraph, the 25 FEP halves of §F, the ESP applications) | ESP manuals (held, unopened), TR-044, the `.ptf` container (parsed), `paragraph` known plaintext | runtime for held `.ptf`: medium-high once KL0 opcodes are named. Started 2026-11-24: the Librarian's loader (`psi/librarian.py`) and a KL0 interpreter (`psi/kl0.py`), both OURS. 96 opcodes are named from known plaintext. 303 of the 530 methods of the 104 SIMPOS-free classes run to a solution, and `convert/3` agrees with PIMOS on 96 names. A compiler: a new program, labelled |
| 3 | **KL0 definition** (opcode names, operand formats, built-ins; KL0 microcode source) | P1-P3 | `sysidat`, `syspsi`, the `paragraph` pair, TM-444, TR-265, TR-079, the 1985 KL0 built-in manual (JAIST, CITED-ONLY) | high for opcodes the held code uses (the microcode is held and defines them); the rest unneeded |
| 4 | **PSI-III hardware at microinstruction level** (sequencer, condition codes, I/O); the same PU as PIM/m (TM-862) | P1, P2; PIM/m cycle accuracy | TR-733 fig. 4, `rassy`, TM-858, TM-862, TM-856, TR-714, Giho 65(6) (all held); the held control store | medium for the format, by reverse engineering, "not transcription" (`psi_acquisition.md` §3, §8); no format document exists in what was searched |
| 5 | **FEP and CSP ESP source** | readability; P5 fidelity is reachable from the binaries | decompiled `.ptf` | high once a KL0 disassembler exists |
| 6 | **PSI-II/III-era SIMPOS and CSP manuals** | operating procedure | catalogue records; 1985 manuals at JAIST | — |
| 7 | **Common ESP** (CITED-ONLY: tape, not online, `psi_acquisition.md` §2) | an alternative host for ESP | the conversion guide in `ifs/INFO.tar.Z` | — |
| 8 | **A PSI emulator** (ZEUS; none found, searched 2026-11-23, `psi_acquisition.md` §4) | a shortcut for P2 | — | not needed if P2 is built |

### 4.3 The other PIM machines and Multi-PSI

| Rank | Lost item | Blocks | A reconstruction would rest on | Attainable fidelity |
|---|---|---|---|---|
| 1 | **Multi-PSI/V2 KL1 microcode and Pseudo Multi-PSI for PSI-II** | a Multi-PSI environment | the Pseudo PIM/m firmware (same line, converted); Multi-PSI/V2 reports (Appendix A) | medium for behaviour; the PSI-II microinstruction is 53 bits, so the held PSI-III code is not it |
| 2 | **PSL translator and per-machine back ends (PIM/p, /i, /k native code; PIM/c microcode)** | running VPIM, and any of the four machines | VPIM PSL source (held), TM-1044, per-machine papers | VPIM as a portable runtime: medium (write a PSL translator or port by hand); per-machine back ends: low |
| 3 | **Per-machine PIMOS object sets and BIOS variants** (`mpsi_*`, PIM/p ...; the `pimi_scsi`/`pim_scsi` modules) | booting PIMOS on those machines | the 3.6 source's `machine` and `machine_type` branches; PIMOS's own compiler | medium: rebuild from source once a compiler runs, labelled |
| 4 | **Multi-PSI CSP and its manual** | Multi-PSI boot | primer, `mpsicspR.ptf` | low-medium |
| 5 | **PIMOS 1.x-2.5 (the Multi-PSI years) and the CAL-built `.kbn`** | an authentic 1988-1990 Multi-PSI environment | manuals 1.5, primer | low |

## 5. What has not been searched for yet

Each item: what, and where to look. "No search on record" is the basis;
an item may turn out to be in a document already held.

**Inside what is already held (cheapest first):**

1. The sixteen PIMOS-format `.sav` files in the IFS tree (§F): decode
   with `asm/unlsav.py`; read the file magic's meaning (`5502`/`5602`
   against `5702`), the target machine, the PIMOS version. Places:
   `nonlocal/ifs/kbms-clp/pimos/gdcc.tar.gz`,
   `exper-apps/pimos/mmi.tar.Z`,
   `symbolic-proc/klic-apps/d-pool/dpool_pimos.tgz`,
   `contract-research/97/DH9-07/H9-07.tgz`.
2. Members of all 298 IFS archives for further object or firmware files:
   this audit searched member names for `.sav .kbn .mbn .ptf .sym .ldb`
   (results in §F); not searched: contents, other extensions, the 186
   `contract-research/` directories for PIMOS versions or FEP code
   (`icot_software_survey.md` §3 "not analysed").
3. Held and unread reports: TM-850, TM-849, TM-1021, TM-1022, TM-212,
   TM-213, TM-261, TM-353, TM-354, TM-346, TM-768, TM-551, TM-671
   (`literature_gaps.md` line 1389); TM-1203; TM-1254; TM-444 in full;
   TM-767 (batch GC).
4. Held and unopened manuals: the four ESP manual archives; the PIMOS
   1.5 manual's FEP string-I/O appendix; the Japanese 3.0 manual beyond
   §6.1; the KL1 manuals.
5. The goal-record and suspension inspectors in `pimmcsp`
   (`csp_goal_record_inspector`, `csp_goal_converter`,
   `csp_susp_record_inspector`): they hold the layout
   (`binary_reverse_engineering.md` §3). Needs the KL0 disassembler.
6. The object set for a file-system server (`icot_databases.md` §6.4:
   "not established"; the byte search could not see atom names). Now
   possible with `asm/unlsav.py` and the atom tables.
7. Which `ipl_parameter` branch `pimm_bios360E.sav` was built with, and
   clause-level identity of `.sav` modules with source
   (`binary_reverse_engineering.md` §7).
8. Rebuilding any `.sav` from source (no attempt on record): needs
   PIMOS's compiler running somewhere.
9. `pimi_scsi`, `pim_scsi` and any `case(pimk)` in other held KL1
   (VPIM `src/`, the IFS PIMOS packages): this audit searched only the
   PIMOS source tree.
10. VPIM's per-machine conditionals (which parts are PIM/p-, /c-, /i-,
    /k-specific): not searched; this audit only confirmed by `grep -l`
    that some VPIM files mention the machines.

**Outside (with where to look):**

11. `pimm_patch.com` anywhere but `psdpim.tar.Z`: the CMU AI Repository
    copy of IFS and its `.ltv` listings, the 2019 CMU WARC on
    archive.org, Wayback captures of `ftp.icot.or.jp`.
12. Per-machine PIMOS object sets (`mpsi_*.sav`, `ppim_*.sav`, PIM/p,
    /c, /i, /k builds): the same three places; the Japanese 3.0 manual
    for their names.
13. What P0 did not search (`psi_acquisition.md` §7): Software
    Heritage (API returned no JSON to an anonymous client); the Kyoto,
    Tokyo, Keio and KEK mirrors; Oki's technical review and theses; the
    Wayback index beyond `icot.or.jp/*` and the first 600 URLs of
    `ftp.icot.or.jp`. Holders never contacted (`psi_acquisition.md`
    §6, leads not facts): Mitsubishi Electric (Kamakura/Ofuna); the
    successors of AIR and Mitsubishi Electric Computer Systems (CESP);
    university CESP tapes; the JAIST collection; the ESP and SIMPOS
    authors; JIPDEC; the Waseda laboratory; Oki Electric. Contacting
    anyone needs the owner. Also unsearched: the paywalled NGC 1(1),
    1(2), the SLP'87 PSI-II paper and the full ICCD'90 paper (CITED-ONLY,
    `psi_acquisition.md` §3); and the 64 + 27 newly held documents
    themselves, none yet read by the project (e.g. TR-714 and TM-862
    for P1; the 24 SIMPOS reports for P4).
13a. The `.ptf` packages inside IFS `kappa2` and `utter`
    (`psi_acquisition.md` §1): not opened; more KL0 code to test a
    disassembler on.
14. Media with the preserved PIM/m and PIM/p (National Museum of Nature
    and Science): never asked (survey §5.2 lists it as "ask for").
15. TR/TM numbers with no PDF: National Diet Library, Kawasaki library
    (`literature_gaps.md` Appendix D). Their titles have not been
    checked for relevance.
16. Codeberg (not searched, rate limit, `icot_software_survey.md` §4.1).
17. The FGCS'92 PIM/m benchmark programs as files (roadmap §6 R9
    candidates): the IFS tree and contest sources were not searched for
    them by name.
18. Multi-PSI/V1 software: nothing on record; TR-237 (held since P0)
    not read.
19. Former ICOT and vendor staff for the IPL, FEP and CSP sources
    (survey §5.2 item 1): no contact on record.

## 6. Open contradictions and unknowns found while auditing

**Between documents** (newer stated where the dates allow). *Each item
now ends with its resolution, recorded 2026-11-23 by a documentation
pass. Older statements were corrected in place with dated notes, not
rewritten.*

1. **What is held from IFS.** `icot_software_survey.md` §0 item 4 ("We
   hold 8 files from 6 entries"), §3 ("No archive other than the eight
   marked HELD was downloaded"), §5.1 ("download now", including
   `pimosman.ps.Z`, the PIMOS and ESP manuals, MGTP); `pimos_roadmap.md`
   §6 ("Not fetched yet"); `nonlocal/MANIFEST.md` §3 ("recorded only,
   not downloaded", TR-373 and TM-1203 among them). Newer:
   `IFS_MANIFEST.md` and `LIT_MANIFEST.md` (2026-11-20) hold all of
   these. The older docs were not updated.
   **Resolved.** Every file on those lists is on disk and in a manifest.
   §5.1's rows are under `nonlocal/ifs/`, the TMs under
   `nonlocal/lit/trtm/`. §3 of `MANIFEST.md`: TR-246/389/460/659 are in
   `nonlocal/` itself (`LIT_MANIFEST.md` §8); TR-373, TM-140, TM-1067,
   TM-1203 and the TR/TM index pages are in `lit/trtm/`; the FGCS'92 PIM
   papers are in `lit/fgcs/`; the `-J` abstracts are in
   `ifs/_catalogue/abst/`. One exception: `pim-spec-J.html` is still not
   held (only `-E` is, in `lit/web/`). Dated notes were added at the
   survey's §0 item 4, §3 and §5.1, at `pimos_roadmap.md` §6 (three
   places), and at `MANIFEST.md` "Recorded, not downloaded" and §3.
2. **How many instructions the models implement.** 51 arms in the bench
   model (`pimos_roadmap.md` §1, `pimos_boot_requirements.md` §0.2); 54
   on both models (`gap_analysis.md` §0, 2026-11-20); 116 on both
   (`bsv/README.md`, `ref/pimm/README.md`, newest). The counts describe
   different models and dates; `gap_analysis.md` §0 is stale.
   **Mostly resolved: the READMEs say 128 on both models now**
   (`ref/pimm/README.md`, `bsv/README.md` "State"; it was 116 before
   the merge of ten ported items on 2026-11-23).
   - The task's literal recipe (count `def i_` in `ref/pimm/pimm.py`,
     less those gated by `self.alone(`) gives 131. No handler is gated
     whole; the call appears only in `builtin()` and in one case of
     `i_merge_in`.
   - A name diff against `bsv/Pimm*.bsv` finds every handler with an
     arm except `scsi_init` and `scsi_command`, which are on the
     reference alone. That leaves 129 handlers on both models.
   - Two of the 129, `merge_in` and `unify_step`, are our stubs
     (`asm/pimm_stubs.py`; neither is in `inst_tab.kl1`), which leaves
     127 PIM/m instructions.

   Neither count is exactly 128, and the README's rule is not stated.
   The one-off difference is left open; it would be settled by the
   README naming what it counts. The 51 is the bench model
   `PimKL1B.bsv`, and the 54 is a dated snapshot. Notes were added at
   `gap_analysis.md` §0, `pimos_roadmap.md` §1,
   `pimos_boot_requirements.md` §0.2 and the survey's row 1.
3. **How many lockstep tests.** Seven (`gap_analysis.md` §0), 23
   (`pimm_semantics.md` "The MRB"), 33 (`bsv/README.md`, newest).
   **Resolved: 39 now.** That is the count in
   `grep -o 'for t in.*' bsv/run_pimm_lockstep.sh`, and `bsv/README.md`
   now says "Thirty-nine tests". At this audit's own commit the README
   said thirty-three while the script already listed 37, so the README
   lagged. The 7 and the 23 are true of their dates: the 7 of the
   2026-11-20 snapshot, the 23 of the MRB check. Dated notes were added
   at `gap_analysis.md` §0 and `pimm_semantics.md`, and row J of this
   audit's §3 was updated.
4. **Machine cycle.** `gap_analysis.md` §D: "60 ns cycle";
   `pim_architecture.md` §1, §7: 65 ns from `M92`, `OV92`, `TR659`.
   **Resolved: both are printed, so neither document is wrong.** 60 ns:
   TR-564 PDF p. 3 (printed p. 2) and FGCS'92 Vol. 1 p. 45 Fig. 7, both
   read from the page images in this pass, plus TR-799 Table 3 (OCR).
   65 ns: `M92` p. 426 (PDF p. 459) and `OV92` p. 62 (PDF p. 91), plus
   TM-1074 and TR-733 Table 1. FGCS'92 Vol. 1 p. 43 Table 2 ("Target
   cycle time") prints 50 under PIM/m and 65 under PIM/c, the reverse
   of `OV92` p. 62 Table 2. The other rows agree, so p. 43 is probably
   a transposition (INFERENCE; both pages read from the image). `OV92`
   marks PIM/p's 60 and PIM/c's 50 as † design specifications and
   leaves PIM/m's 65 unmarked. The `literature_gaps.md`
   App. C 2.1 INFERENCE stands: 65 ns is worst case (15.4 MHz, TM-1159)
   and 60 ns typical (16.7 MHz, TR-799). Dated notes were added at
   `gap_analysis.md` §D and `pim_architecture.md` §1 and §7. Open: which
   figure a cycle-accurate model should use. A statement of the clock
   PIM/m was actually run at would settle it.
5. **Microinstruction layout in print.** `pim_architecture.md` §5:
   "not printed anywhere in these sources"; `literature_gaps.md` §8:
   TR-733 fig. 4. Both true of the sources each read; the latter is the
   later finding and `pim_architecture.md` was not amended.
   **Resolved: the layout is printed.** TR-733 fig. 4 (journal p. 76(684),
   TR PDF p. 4; read from the page image in this pass) gives 64 bits:
   CCF 5, DSTF 5, SC1F 5, SC2F 5, SD1F 3, SD2F 2, AS1F 3, AS2F 2, ADF 3,
   ALF 3, JMPF 3, CNDF 4, EM1 6, EM2 6, EM3 4, and five one-bit `*`
   strobes. `pim_architecture.md` §5 and §7 were corrected in place,
   with a dated note. What is still not printed is the field values;
   `rassy` and `pseudo_pimm_microcode.md` read those from binaries.
6. **Which file is the KL0 firmware.** `icot_software_survey.md` §2.3
   "not established"; `binary_reverse_engineering.md` §4.2: `syspsi`
   is the 32K control store, KL0/SIMPOS (same day, later).
   **Narrowed, still open (with item 20).** From the primary files:
   `psdpim/README` calls `PMPSI.DIR` "KL0 and KL1 firmware";
   `SYSTEM.DIR/boot.init` loads `pimm.MEkbn` as the KL1 `impl` file; and
   `INSTALL` copies `syspsi`, `sysinit`, `sysidat` to SIMPOS's
   `/usr/psi/simpos/csp`. So KL0 is in the `sys*` trio. `sysidat` is its
   decode table, and `syspsi` is, by shape, the 32K x 64 store, with its
   words `0..57ff` equal to image 1 of `pimm.MEkbn`. That `syspsi` is
   the KL0 control store is still INFERENCE, because no document names
   its role. The same "probable, not proven" wording is now in the
   survey §2.3 and §4, `psi_acquisition.md` §4 and
   `binary_reverse_engineering.md` §5. What would settle it: the CSP's
   micro loader read out of `pimmcsp.ptf` (which file it loads into
   the WCS), or a PSI-III document.
7. **`fep#ipl` / `fep#symbol`.** `icot_software_survey.md` §1.1 and
   `gap_analysis.md` C2 (first correction) infer they are the IPL's
   device classes; `binary_reverse_engineering.md` §1.4, §4.3 find the
   IPL never sends them and the FEP never tests them. The later reading
   stands (it too was "not executed" when written).
   **Resolved: the IPL does not use them.** There is now executed
   evidence for the IPL side. On 2026-11-23 `ref/pimm/ref_scsi.py` ran
   the body of `ipl:boot0` on the reference model against
   `ref/pimm/fep.py`, which serves only `read_open` 201, `getb` 210,
   `close` 60 and `abort` 70 and raises on anything else, and the run
   completes.
   That covers our FEP model on the path `boot0` takes. The FEP side
   (§4.3) is still a reading. Dated notes were added at the survey's
   §1.1, the second correction in `gap_analysis.md` C2, and
   `binary_reverse_engineering.md` §4.3.
8. **Class counts.** `pimscsi` 23 and `pimmutil` 50 classes (survey)
   against 24 and 51 (`binary_reverse_engineering.md` §4.1, measured).
   **Resolved: 24 and 51.** Re-measured with `python3 asm/ptfdump.py`:
   `pimscsi` has 24 class records and `pimmutil` 51, and `--check`
   passes. For `pimscsi` this was never a disagreement: the survey says
   "23 classes ... plus a `cmt` class". For `pimmutil` the survey's 50
   was corrected to 51 in place (row 3 and §2.3), with dated notes.
9. **`fep#` definitions.** 105 definitions, 104 distinct names (survey
   §1.1); "104 `fep#` definitions outside comments"
   (`binary_reverse_engineering.md` §4.3). Probably the same set
   counted with and without a commented line (INFERENCE).
   **Resolved: the inference holds (measured).** `pimos.vmac` has 105
   `fep#Name =>` occurrences. One is the commented-out line 74,
   `%%      fep#putb => 111`, a repeat of a live name. That leaves 104
   outside comments, all distinct. A note was added at the survey's
   §1.1.
10. **Start address.** `20c` (`boot.init`), `202` (primer, another
    build), `2000`/`200` (CSP help text), `0xE0001E81` (the `.kbn`
    header). Not reconciled (`icot_software_survey.md` §7,
    `literature_gaps.md` §8).
    **Partly resolved; the mapping is open.** These are two kinds of
    quantity, not rival values of one.
    - `0xE0001E81` is the image's own entry: cell 7,809 of an image
      loaded at `0xE0000000`, which is `ipl:boot/0`
      (`asm/kbndis.py --check`; the `.ldb` agrees).
    - `20c`, `202`, `200` and `2000` are arguments to the CSP's
      `GO/PIMos`. The help text calls the Pseudo MPSI one a "KL1 Start
      Address" and the Multi-PSI one a "Micro Start Address", and says
      `GO/PIMos` "throws a boot goal to the boot PE". That
      `start(pimos,"20c")` is `GO/PIMos` is INFERENCE from the names.
    - `20c` is not an offset into the IPL image: cell `0x20c` lies
      inside `ipl_file_decoder:check_GC_element/8` (measured with
      `kbndis.Image`).

    `PIMM.PARAM`'s `stadr 16'204` and `bmadr 16'2E6` belong to the same
    low-address family. What `20c` addresses would be settled by the
    `GO/PIMos` code in `pimmcsp.ptf` or by the firmware's start-up path
    in `pimm.MEkbn`. Notes were added at the survey's §7 and
    `literature_gaps.md` §8.
11. **PIMOS version dates.** Source `version.kl1` "3.600", "20-May-93";
    object comments "3.600:25-Nov-93"; patches 1994-05-12; manual V3.0
    (October/November 1991). R5's expected text was corrected on
    2026-11-23 to follow the source (`pimos_roadmap.md` §2 R5); which
    branch the binary was compiled from is open.
    **Resolved: two dates of two artefacts, both in the objects.** A
    search of the `.sav` files for the dates as two-byte JIS strings
    found "25-Nov-93" once in each of the eight base sets, in the file
    comment ("PIMM BIOS :3.600:25-Nov-93"). It found "20-May-93" once,
    in `pimm_kernel360E.sav`: the constant of `pimos_version:date/1`.
    Run on the reference model, `pim:go/4` prints "PIMOS V 3.600
    20-May-93" (`longrun_ipl.py --reference --go`). So the compiled
    version module agrees with `src/kernel/init/version.kl1`:21.
    25-Nov-93 is probably the date the sets were built (INFERENCE). The
    patch files' 1994-05-12 is an archive time. A note was added at
    `binary_reverse_engineering.md` §2. Still open: whether every
    module was compiled from exactly the held text (item 12).
12. **The IPL image vs the held source.** The IPL's source-backed
    modules are older text than `src/` (`binary_reverse_engineering.md`
    §1.1); the `.sav` modules match the patched `src/` by predicate set
    (§2). So "source is the oracle" holds for the `.sav` set and not for
    the IPL image.
    **Stands; not a contradiction.** Both readings are of different
    artefacts and both are kept. Not re-examined in this pass.
13. **Firmware vs object set.** The held firmware has no decode entry for
    `scsi_transfer`, used once by the 3.6 objects
    (`pseudo_pimm_firmware.md` §1): the firmware build and the object
    set are not an exact pair.
    **Resolved: both statements stand, and the use is harmless to a
    boot.** A scan of the object set with `asm/unlsav.py`'s reader (tag
    22, opcode `dc`) found the single use in `pimm_debugger360E.sav`,
    module `listener_cmd_builtin`: the listener's typed-command
    pass-through, `do_command(scsi_transfer(A,B,C,D,E,F))`
    (`src/debugger/listener/com_built.kl1`:135). Nothing on the boot or
    system paths calls it, so the pair mismatches only on that one
    command. `pimm.MEkbn` and the patch files share the archive date
    1994-05-12. Whether PIM/m's own firmware had `dc` is unknown.
    Notes were added at the survey's §0 and §7 and at
    `pseudo_pimm_firmware.md` §1.
14. **Model memory vs machine memory.** Both models use 2^27 cells
    (`bsv/README.md`); a PIM/m PE had 16 M words (`M92` p. 426). Not a
    contradiction between documents, but a model choice that exceeds
    the machine and should stay labelled.
    **Stands (a labelled model choice).** No change.
15. **Package naming.** Primer `mpsicsp##...` vs held `pimmcsp##...`;
    `mpsicspR.ptf` declares package `mpsicsp` (survey §7).
    **Stands, not a contradiction.** These are parallel package families
    for Multi-PSI and PIM/m, as the survey says. Not re-examined.
16. **CCF field.** `rassy`'s `ccf` is a value table; the microcode doc
    reads CCF as separate strobe bits (`binary_reverse_engineering.md`
    §3, "not resolved").
    **Open, not examined in this pass.** Reading `rassy`'s `set_up_ccf`
    code (the bit extraction) would settle it.
17. **`rassy` version string.** "1.3 (5-June-1989 by MTC KATAYAMA)"
    found on re-reading; an agent reported "1.4 (15-June-1989 ...)"
    (`binary_reverse_engineering.md` §3).
    **Resolved: 1.3.** `asm/ptfdump.py pimmutil CLASS` over all 51
    classes gives exactly one version string, "version 1.3 (5-June-1989
    by MTC KATAYAMA)", in `rassy`. The 1.4 report is not borne out. Other
    packages were not searched. A note was added at
    `binary_reverse_engineering.md` §3.
18. **`ifs/README` vs the catalogue** for entries 66-70, and its date
    (15-Apr-1996 in the text, 1997-04-15 on the listing)
    (`icot_software_survey.md` §7).
    **Date: resolved; entries 66-70: open.** The two dates belong to two
    things, the text's own "Last Modified on 15-Apr-1996" (line 3 of
    the held `nonlocal/ifs/README`) and the server's file time. A note
    was added at the survey's §7. Entries 66-70 were not re-examined.
19. **PIMOS source file count.** `nonlocal/MANIFEST.md` §1: `src/`
    has 502 `.kl1` files; `icot_software_survey.md` §0: 485 under
    `src/` and 502 counting `src_util/`.
    **Resolved: the survey is right.** Counting `.kl1` members of
    `pimos.tar.Z` by second path component gives `src` 485 and
    `src_util` 17, 502 in all. `MANIFEST.md` §1 was corrected in place
    with a dated note: 559 is `src/`'s entry count, and its
    per-directory figures are entries. The object set's 502 modules
    (`asm/census.py`) count a different thing.
20. **KL0 file identity, again.** `psi_acquisition.md` §4 (2026-11-23)
    says which file holds KL0 is "not yet determined" and cites
    `binary_reverse_engineering.md` for `syspsi` "from its size and
    INSTALL's wording": the identification is probable, not proven (see
    item 6).
    **Made consistent; still open (see item 6).** `psi_acquisition.md`
    §4 and `binary_reverse_engineering.md` §5 now carry the same
    "probable, not proven" statement and the same evidence.

**Unknowns this audit adds** (each found while auditing, none settled):

- What the `55 02`/`56 02` magic of the IFS application `.sav` files
  means against the 3.6 set's `57 02`, which machine built them, and
  whether `rodin.sav` (JIS escape then `55 02`) is a seventeenth.
- Whether PIM/k had a PIMOS build branch at all (none in the 3.6
  source).
- Where `pimi_scsi` and `pim_scsi` live.
- How the 18 IFS PIMOS packages with no `.esp` by name do their I/O
  (they may still open FEP windows through PIMOS, which needs only the
  FEP, not an ESP half: INFERENCE).
- Whether the PIM/m PE board wired the PU (one chip with the PSI-III,
  TM-862) to control store and memory as the PSI-III board did, which
  decides how far a reading of the Pseudo PIM/m microprogram is a
  reading of PIM/m.


## 7. Status changes from the three searches of 2026-11-23 (later the same day)

Sections 2-5 above are as first written; these supersede them where
they differ. Sources: `psi_acquisition.md` sections 9 (SIMPOS) and 10
(second broad search), `archive_search_notes.md` (inside the held
archives; tables and scripts kept outside git).

- **PSI microinstruction formats**: NOT FOUND → FOUND, primary
  (Nakashima's thesis, PSI-I 63, PSI-II 53, PSI-III 64 bits;
  `psi_acquisition.md` §10). Changes section 4.2's rank 4 and rows
  naming P1.
- **SIMPOS**: still LOST as software. Its supervisor, file and window
  classes are partly PRINTED in ICOT reports (TM-100, TR-524, TR-046,
  TR-056, TR-059, TM-065, TM-125); the ~300 system classes the held
  applications call are listed (`simpos/required/old_regex_census.tsv (superseded by simpos/required/)`); five PSI-I
  SIMPOS/KL0/CSP manuals are HELD-ELSEWHERE at the JAIST library
  (`psi_acquisition.md` §9). Row 14.
- **Every ICOT TR/TM on SIMPOS, ESP or the PSI**: HELD (87 of 87).
- **The 16 IFS `.sav` files**: undecoded → decoded (`asm/unlsav.py`
  reads all; magic 5502 module, 5602 package, 5702/5802 with comment,
  from `library/unloader/unlver.kl1`); `simplex_if.sav` is a package
  file the IPL refuses. Section 5 item 1.
- **Undamaged KL1 object files in IFS**: 16 → 25 (nine more, in
  alignga, editalign, multialign, mendels, papyrus), plus 5 damaged
  by a text conversion (`rodin.sav` is one: 4 of 111 modules recovered;
  helic2's `plib.sav` recovered whole). Section 3 area F.
- **`pimos.h`**, the machine-configuration header 75 files of the 3.6
  source include and no PIMOS archive holds: FOUND in
  `symbolic-proc/klic-apps/d-pool/dpool_pimos.tgz` (1995). Its
  `case(pimm)`: `machine_type mpsi`, `ipl_parameter yes`,
  `fep_interface scsi`. So "PIM/m takes the `mpsi` branch" is READ, not
  inferred; `case(pimk)` exists (contradicting "none anywhere").
- **Version drift**: `mmi/system.sav` uses opcodes 43h, 44h, known
  neither to `kl1_encoding.md` nor to the 3.6 objects; dpool uses 1Bh
  `clause_info`.
- **`.ptf` files**: opened and parsed (kappa 797 classes, 696 with a
  same-named held ESP source: a known-plaintext pair far larger than
  `paragraph`). Section 5 item 13a.
- **FGCS'92 benchmarks**: append HELD; best-path a driver only (its
  `bp` module not held); 15-puzzle a KLIB version HELD (not shown to
  be the paper's); pentomino NOT FOUND. Section 5 item 17.
- **ESP manuals**: read (PSI II specification table in the Overview;
  the Programming volume lacks the SIMPOS programming-system part).
- **Not found inside**: firmware, microcode, `.kbn`/`.mbn`, `pimm_patch.com`,
  `mpsi_*` objects. **Not found outside**: SIMPOS, the ESP system,
  CESP, KL0 source, the PIM/m firmware, `pimm_patch.com`.
- **R7/R9 candidates** (applications to run): modules with no
  external calls (`gc.sav`, the MGTP problem modules, `dayhoff.unload`,
  `mdllibrary.exe`); then MGTP (`mgtpNS7.sav` with a problem file),
  whose expected output is recorded (`H9-07/nseq/pim/aitec19980402.log`:
  "Number of Failed Branches = 43782", "unsat", 64,089,346 reductions).

## 8. Status on 2026-11-24: held, lost, and what we have rebuilt

Sections 2-7 are as written on 2026-11-23; this section supersedes
their "Our status" column. Counts: `grep -c '    def i_'
ref/pimm/pimm.py` (152), `ls ref/pimm/fep_tapes` (9), the commits named.

### 8.1 Held as source (we read it; nothing to recreate)

| What | Where it is used |
|---|---|
| PIMOS 3.6 (485 `.kl1`, the patched May-1994 text) | every semantic question about the kernel, servers, shell, BIOS; the FEP protocol (`fep_services.md`, 63 wire commands from `bios/fep_module/*_dvc.kl1`) |
| PIMOS's KL1 toolchain (compiler, assembler, loader, unloader) | the encoding (`kl1_encoding.md`); not yet run on a model (R7) |
| `pimos.h` (from dpool, 1995) | the build configuration of PIM/m (`mpsi` branch, SCSI FEP) |
| PDSS (C), VPIM (PSL), KLIC | instruction and runtime semantics where the PIM/m firmware is lost; every borrowed rule is labelled with its source |
| ESP source for three `.ptf` programs (paragraph, kappa2, utter) | known plaintext for the loader and the KL0 interpreter |
| SIMPOS classes printed in ICOT reports (28 of 255 printed classes with source) | the stand-in `simpos##` classes, verbatim where printed |
| PIMOS, KL1, ESP manuals; 385 TR/TM; theses (Nakashima: the PSI microword) | citations throughout |

### 8.2 Held as binary only (we run or decode it)

| What | State |
|---|---|
| `pimm_ipl.kbn` and the 20 PIMOS `.sav` object files with the 1994 patches | the IPL loads and links all of them on both models; PIMOS's start runs 65,482 instructions on the reference model (banner, SCSI bus scan, first FEP messages), 42242945 |
| Pseudo PIM/m microcode | read for field layouts and the decode table (`pseudo_pimm_microcode.md`); not executed |
| PSI-III control store (`syspsi`, `sysidat`, `sysinit`) | decoded by the thesis's microword layout (`asm/mekbn.py`, 5f3651ee); not executed |
| Eleven `.ptf` ESP packages (pimfep, pimscsi, pimmcsp, pimmutil, mpsicspR, kappa, paragraph, fts, qxt, sancho2, tour) | all 1,455 classes load into class objects (`psi/librarian.py`, 220e33bc); method bodies not yet executed |
| IFS application object files (25 whole, 5 damaged) | decoded (`asm/unlsav.py`); none run yet |

### 8.3 Lost, and what stands in for it

| Lost | What we have instead | Still missing |
|---|---|---|
| **PIM/m KL1-B firmware** (the machine's instruction semantics and runtime) | the reference model `ref/pimm/pimm.py` and the Bluespec core, run in lockstep: 152 instruction handlers (149 without three stubs of ours), all on both models; SCSI on the core (cbcfd1cd); shoen stages 1-3: create/start/terminate, statistics, remove, exceptions, `raise`, stop, abort (11cefe3a); 2026-11-24, PIMOS after the login on the core, in lockstep from a saved machine (`bsv/run_pimm_shell.sh`): `shutdown`/`yes` to `PIMOS END` and `cat` from the shell's prompt, every trace line identical (878,180 and 731,110); and the whole of `go()` from the machine after the link, 8,766,339 instructions, 20,107,047 lines (8,766,319 and 20,107,017 with the login ID 0, P-f3, re-run 2026-11-24); twelve commands past the shell from the prompt, `pwd` to `compile` (`bsv/run_pimm_apps.sh`, 29,867 to 318,476 instructions each), every line identical | shoen resource limits (no source gives the allowance or threshold); unification failure inside a shoen; garbage collection; priorities beyond what the boot uses; multiple PEs; the instructions PIMOS's start has not reached yet (found one stop at a time) |
| **PIM/m CSP software and manual; `pimm_patch.com`** | `longrun_ipl.py` does the CSP's part (load, link, `make_boot_info`, start) | the real console procedure |
| **The FEP as software** (the PSI-side program's source; it ran on SIMPOS) | `ref/pimm/fep.py` (OURS), answering from PIMOS's own protocol source; the SD-card FEP emulator in Bluespec (`PimmFepEmu.bsv`), byte-identical to `fep.py` on 9 tapes and 293 commands (c57a2260); 2026-11-24, to the shell's prompt: 714 commands and 12 events, held requests answered by the card's script (the login) | window, socket, directory and most timer services; withheld and unsolicited replies (the login); the PSI's own answer values (being read from `pimfep.ptf`) |
| **SIMPOS** (all forms) | a measured specification (`simpos/README.md`: 367 system classes, 1,440+706 methods, 353 built-ins); route step 1, the Librarian's loader, done; step 3 started (2026-11-24): ten stand-in classes in `psi/standin/`, labelled scaffolding, each method PRINTED or INTERPOLATED: `process` (TM-100 Fig. 3.1 printed body plus interpolated `self/2`), `stream` (TM-100 Fig. 3.6 printed source), and interpolated `list`, `post_queue`, `waiting_queue`, `process_clock`, `with_link`, `waiting_frame`. kl0's `new/2` runs slots initialised by code (TM-388 §3.5; arity-1 convention measured on all 424 held initialisers). `pimfep##pimos_timer:stream/2` now succeeds. Step 3b: macro banks expanded; four string built-ins witnessed; `:refute` modelled; interpolated `string` (`append/3`, `copy/3`), partial `symbolizer` (`string_to_list/3`, `list_to_string/3`) and `process:tag_catch/5,6,9`; `on_after/4` now stops at `process:allow_forced_event/1`. Census of pimfep+pimscsi (`kl0.py census --fep`): 515 of 1,228 methods succeed (501 before step 3b), 51 fail cleanly, 662 refuse. Step 3c: printed `channel`, `bounded_channel`, `bounded_post_queue` (TM-100 Figs. 3.7, 3.10, 3.11); interpolated `post_queue_for_message`, `semaphore`, `list_index` and `hash_index` (layout from kappa2's `KPPOOL.ESP`/`SVHSH_IDX.ESP`), `process:create/3`, `allow_forced_event/1` and accessors, a minimal `standard_editor`; then nine more opcode rows (blt 01 06 10 16 32 33 40 5c 68, known plaintext), three HELD-SOURCE classes from morphana's `_simpos/` copies (`name`, `e_string`, `pathname`, ICOT Free Software) and the symbolizer's integer `get_number/3`, `get_number_string/3`; census 607 of 1,229 succeed, 101 fail (38 on the census's unbound arguments at a type test), 521 refuse. Step 3d: four opcode rows (blt 6e `vector_to_list`, blt 34 `set_subvector`, pmi b0 `{}`, pmi b4 four-element vector; step 3c's "no witness for b0" was wrong) and three wider operand patterns; census totals unchanged, 93 refused methods get further. Step 3d stand-ins: ten INTERPOLATED classes (`as_class_with_lock`, `with_lock`, `as_message`, `message`, `trace`, `common_network`, `network_listener_buffer`, `alarm_watch`, `time`, minimal `pmacs_window`); census 665 of 1,265 succeed, 113 fail, 487 refuse, none moved out of success. Step 3e: 12 opcode rows (pmi ca, b1, b5, b6, b7; blt f2, 9a, 9b, 50, 51, 54, 55) and R != A for blt 40/49; PRINTED `as_program` (TM-100 Fig. 3.3) with an interpolated program stack in `process`; census outcomes `exception` (uncaught `undefined_method:raise/2`, TM-388 p.59) and the cause `receiver a slot constant` (a census artifact: receivers made by new/2); interpolated `network_node_name` and `pmacs_window`'s editor option and `activity` slot; census 787 of 1,403 succeed, 123 fail, 16 raise, 477 refuse, none moved out of success. Source check applied (2026-11-25, `simpos/source_check_2026-11-24.md` §5 Status): stand-in labels and citations re-checked and corrected (P-s1 to P-s20), opcode mnemonics printed in TM-444/TR-236 said so (P-f2), `time` gains get_count/set_count in the generated tables; census unchanged; opcode rows bound to TM-444/TR-236 mnemonics as INFERENCE with counts, blt 19 V != N executed (six packages 310 / 12 / 208; FEP one method from refused to the step limit) | step 2 the KL0 interpreter (in progress); the rest of step 3: pmi c6, blt 0d and 6f, receivers made through their creators, `library:assign/1`, `process:status/3`, `network_node_name:node_full_name/3`, `pmacs_window`'s window protocol; the rest of `symbolizer` (no witnessed atom/string built-in); step 4 the PSI-III microcode emulator |
| **The ESP compiler, runtime and Librarian** | the loader (step 1); an ESP compiler, `psi/espc.py` (OURS, step 3, 2026-11-24). It emits only opcodes in `kl0_opcodes.tsv`, and anything else is refused by name. All 109 paragraph classes with source compile. 243 of 991 compared predicates are cell for cell identical to `paragraph.ptf`; for kappa2, whose macro banks are now expanded (`with_macro`, TM-388 §3.7.3) so all 739 classes compile, 1,361 of 10,641 (109 through a bank rule), for utter 101 of 521. Paragraph with the string built-ins: 247 of 1,051. The compiled paragraph classes, run alone, give `paragraph.ptf`'s answers to every call `test_kl0.py` makes, and no census method has a different outcome (`psi/test_espc.py`) | the compiler's unwitnessed constructs (`X+Y` on registers, `=\=`, macro rules with a tail or `==>` (40 kappa2 predicates), long vectors, `->`, `not`); first-argument indexing; the runtime is the KL0 interpreter (step 2) |
| **KL0's definition** (opcode names, built-ins) | opcodes named only from known-plaintext witnesses (`docs/simpos/layers/KL0.md`) | most opcodes; settled as the interpreter meets them |
| **PIM/m hardware detail** (stage latencies, caches, network packet format) | papers; model choices labelled OURS | cycle accuracy; multi-PE |
| **Disks, tapes, the PIMOS internal file system** | the held object directory served as `pimos:` by the FEP stand-in | any installation image |
| **Other PIMs' firmware, the PSL translator, their PIMOS object sets** | VPIM source (held) | everything for the third phase |
| **IFS QUTE and SAM** | none | both |

### 8.4 What gates the next rungs

- **R5/R6 (PIMOS to a login and a shell):** the FEP services the start
  asks for next (`fep_services.md` §3), then a login the stand-in
  originates. PIMOS prints no login prompt: the dialogue ran on the PSI,
  so the FEP answers PIMOS's pending read with a login record. How PIMOS
  learns that a withheld reply has arrived decides what the SCSI
  built-ins must support.
- **R7 (compiling under PIMOS):** the toolchain is held as source and
  object; it needs the runtime above, and probably GC. (2026-11-24:
  the compiler starts from the shell's prompt and prints its banner
  and prompt, in lockstep on the core, with eleven other commands past
  the shell, `bsv/run_pimm_apps.sh`; compiling a file stops at a
  merger input of a long vector, `binary_reverse_engineering.md` 1.4,
  "Commands past the shell". Not held: a user's home directory, so
  serving a source file to compile is OURS.)
- **The PSI side:** the KL0 interpreter, then stand-in SIMPOS classes
  (started: `process`, `stream`, compiled by `psi/espc.py`), then
  `pimfep.ptf` itself as the front end in place of `fep.py`.
