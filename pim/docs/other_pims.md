# The other PIM machines and Multi-PSI: what survives, verdicts, rungs

Third goal of the owner's order ("PIM/m, PSI and then the other PIM
machines", `pimos_roadmap.md` §2): Multi-PSI, PIM/p, PIM/c, PIM/i and
PIM/k. This document runs the searches `environment_audit.md` area L
and §5 listed as not run, fills one held / documented / lost table per
machine, gives a verdict per machine with its oracle, ranks the
machines, and proposes rungs for the cheapest one, Multi-PSI/V2.
Research only: no model, test or tool changed. Dated 2026-11-26.

Labels as in `literature_gaps.md` "The other PIMs: detail" §0:
IMG (read from the page image), TXT (good text layer), OCR (tesseract
only; Japanese OCR is not used for any number unless also IMG), HTML;
and the audit's OURS / INFERENCE / HELD-SOURCE / PRINTED. Paths are
relative to `pim/docs/nonlocal/` unless they start with `pim/`.

## 0. Answer in brief

- **Multi-PSI/V2 is the cheapest by a wide margin**, and at the KL1-B
  level it is mostly built already. PIM/m's firmware is the Multi-PSI/V2
  microprogram converted, the KL1-B is binary compatible, and PIMOS's
  `machine_type` is `mpsi` for both machines. That last point is READ,
  in the 1995 `pimos.h` that the 2026-11-23 search found
  (`archive_search_notes.md` Task 3). A Multi-PSI build of PIMOS 3.6
  differs from the held PIM/m build in three configuration switches.
  The first is `fep_interface`, which is `kl1_network` instead of `scsi`
  (13 sites). The second is `ipl_parameter`, `no` instead of `yes`
  (1 site). The third is `extended_floating_point`, `no` instead of
  `yes` (27 sites). These 41 sites are in 26 files. Every module that
  the `kl1_network` branches name is in the 3.6 tree (§2.7, a crude grep). The
  network is documented to the byte unit: 8 x 8 mesh, 9-bit channel
  units, path tables, 200 ns, 5 MB/s. PIMOS's own compiler runs on the
  model: R8 was reached 2026-11-25/26, with eight pkl1 samples compiled
  and run. Compiling PIMOS's own modules with it has not been tried, so
  rebuilding PIMOS for `mpsi` (MP1) is the first open step, not a done
  one. Rebuilding for `pimm` first gives a check: the result must match
  the held objects. The verdict is two-level. At the KL1-B and system level a
  reproduction is FEASIBLE, with oracles we did not write. At the PSI-II
  microcode level it is NOT FEASIBLE: the KL1 firmware (16 K steps of
  53-bit microinstructions, TM-671 p. 18, IMG) is lost, and the held
  control store is PSI-III code.
- **PIM/p, PIM/c, PIM/i and PIM/k share one gate: the VPIM toolchain
  is lost.** That toolchain is the PSL-to-C converter and its "virtual
  hardware", the PSL-to-native compilers, and the compiler front end
  that emits VPIM's KL1-B. TR-574 (IMG) describes all three. VPIM's
  KL1-B is a different instruction set from the one the held PIMOS
  compiler emits (§2.6). Beyond that gate, every per-machine code
  artefact is lost: native code, macro libraries, microcode, templates,
  assemblers, object sets and CSPs. Each of the four is therefore a
  reconstruction labelled OURS. The only oracles are published figures
  and PIMOS's own source. Ranked by what is published at instruction
  level and what a model could be checked against: **PIM/p**, then
  **PIM/i**, then **PIM/c**, then **PIM/k** (§3).
- **Multi-PSI/V1** is not ranked. Its KL1 system was written in ESP and
  ran on SIMPOS on PSI-I machines (TR-237 §4.1, TXT/OCR in English).
  Neither is held, and nothing outside was searched for them. SIMPOS is
  the PSI track's own gate (P4).
- **Proposed rungs MP1..MP6** for Multi-PSI/V2 are in §4. Each builds on
  rungs already set: R8 (reached), M1..M3 (reached on the reference
  model 2026-11-26, `multi_pe.md` §5), M4..M5 (not reached), and P3/P5
  (the CSP, not started).

## 1. Search record (2026-11-26)

| What | How | Result |
|---|---|---|
| ICOT TR/TM archive, per machine | **Title-only** pass over `lit/trtm/TRlist.html` and `TMlist.html` (the archive's own indexes). Patterns: `PIM/[pcik]`, `ＰＩＭ／[ｐｃｉｋ]`, `Multi-PSI`, `マルチＰＳＩ`, `並列推論マシン`, `Parallel Inference Machine`, `PIM`, `VPIM`, `KL1-B`, `PSL`, `cluster`/`クラスタ`, `PSI-II`, `firmware`/`ファームウェア`, `microprogram`/`マイクロプログラム`, `PIMOS`. Each hit was checked against all of `nonlocal/` by number and by SHA-256 | About 88 index lines (55 TR, 33 TM, by the pattern set's grep) on the machines or on PIM in general; 16 reports not on disk. Every one of the 16 answered on the AIST host (HTTP 206 to a range probe) and was fetched. One of them, TR-389, turned out byte-identical to the held `nonlocal/tr0389.pdf`, which leaves **15 new**. Three of the 15 are cited and committed (§5). The other twelve stay in scratch, unread: TR-211, 304, 349, 412, 448 (the shared-memory KL1 work that led to the PIM cluster), TR-526 (Multi-PSI load balancing), TR-572, TR-774, TM-503 (PIMOS functional design, 102 pp.), TM-891 (Taki tutorial, 128 pp.), TM-1037 and TM-1211 (the KL1-to-C plan that led to KLIC). The unlisted convention TMs (`literature_gaps.md` Appendix E) are all on disk already: TM-210..213, 259..261, 346, 353..359, 526, 530, 531, 572, 662, 671, 767, 779, 846, 847, 849, 911, 922, 923, 1000, 1010..1012, 1018, 1090, 1091, 1096..1098, 1127, 1247 |
| TR/TM contents | Read for this audit: TR-237 (English, OCR); TM-671 pp. 17-18 (IMG); TM-526 header (IMG); TR-574 pp. 1-4 (OCR); TR-704 and TR-755 abstracts (OCR, English); TM-958 contents (OCR, English). For topic only, OCR in Japanese: TM-212, TM-261, TM-359, TM-922, TM-923, TM-1000, TM-1011, TM-1090 | §2 rows |
| IPSJ papers held in `lit/ipsj/` | Titles taken from the 260 records in `lit/records/ipsj/` and matched to the 193 held PDFs | Papers on Multi-PSI, PSI-II, VPIM, PIM/c, PIM/i, PIM/k and PIM/p are held as PDF (ids in §2 and §6 item 4). `literature_gaps.md` Appendix D lists most of them as "resolved-not-read". **Read here:** 田中 et al., 「並列推論マシンPIM/c ―CPUについて―」, IPSJ 40th convention 2L-2, 1990, p. 1179 (`ipsj/118806_*`, IMG). `literature_gaps.md` §10a item 1 named this paper as the likeliest source of PIM/c's microinstruction fields; §2.3 gives the result |
| House journals held | `pdftotext` and grep of the 17 Fujitsu Sci. Tech. J. issues and 18 Mitsubishi Denki Giho issues under `lit/journals/` | FSTJ: no PIM/p article (V26 N1 mentions PSI-II only; V29 N2 cites Multi-PSI TRs). Giho 62(12) 1988 (Multi-PSI hardware) and 66(6) 1992 (PIM/m) are already cited by `literature_gaps.md`. Hitachi, Oki and Toshiba pages: the queries in `literature_gaps.md` "detail" §8 cover them; they were not repeated |
| FGCS'88/'92/'94 | Held under `lit/fgcs/`; per-machine papers already extracted in `literature_gaps.md` "detail" §1-6 | nothing new searched |
| PIMOS 3.6 source, per-machine code | grep in a scratch copy of `pimos.tar.Z`: `switch(machine)` and `switch(machine_type)` (41 sites in 26 files), every `case(...)`, every configuration switch, and the `kl1_network` branches' module references | §2.7. This repeats and extends `archive_search_notes.md` Task 3 (2026-11-23) |
| The machine-configuration header | `pimos.h`, the 1995 copy in `ifs/symbolic-proc/klic-apps/d-pool/dpool_pimos.tgz` (3 identical copies), already found 2026-11-23 | its table is `archive_search_notes.md` Task 3; used here for the per-machine builds |
| VPIM | grep of a scratch copy of `vpim.tar.Z` | no conditional compilation per machine, as Task 3 found. New here: the primitive layer (`src/primitives/prim.psl.c`, 85 `#PSL_define`) calls 79 `_`-prefixed "virtual hardware" primitives. Only 5 of them are held as C (`_function_fast.c`). VPIM's KL1-B opcode table (`p_opecode_table.psl.c`) is a different numbering and set from PIMOS's `inst_tab.kl1` |
| IFS, all 307 archives | `gzip -dc` over every archive, byte grep for `pimi_scsi`, `pim_scsi`, `case(pim[pcik])`, `define(machine…)`, `switch(machine`; and, in a second pass, `mpsi_*.sav`, `mpsi_*.kbn`, `mpsi_*.mbn` and `ppim_*.sav` (members or text; 307 archives, none failed `gzip -t`) | the first pass matches only `dpool_pimos.tgz`. The second matches only `manuals/pimos/man30.j.ps.Z`, which names `mpsi_bios.sav` and `ppim_bios.sav`, so no Multi-PSI or PIM/p object set is held. IFS abstracts with a Machine line: 17 name Multi-PSI alone, 11 more name Multi-PSI with PIM or PIM/m, and none names PIM/p, c, i or k |
| Not repeated | the CMU AI Repository ICOT tree (another agent); the web queries of `literature_gaps.md` "detail" §8 and `psi_acquisition.md` §4 | — |

## 2. Held, documented, lost: per machine

Columns as area L's. "Held" = on disk under `pim/docs/nonlocal/`.

### 2.1 Multi-PSI/V2 (Mitsubishi / ICOT, 1988)

| Item | Held? | Documented? | Status | Notes |
|---|---|---|---|---|
| Configuration | TR-237, TM-359, TM-671, TR-715; Giho 62(12) 1988 pp. 1100-1105 | 8 PEs per cabinet, at most 8 cabinets = 64 PEs, 8 x 8 two-dimensional grid; base clock 5 MHz; each PE has 16 M words (80 MB) of main memory; the PEs run on one clock, and the network can be switched between synchronous and asynchronous mode (Giho table 1, TXT). Up to four FEPs. Each FEP is a PSI-II with a network interface (FENWC); the master FEP also has the maintenance-bus controller (MPC) (TM-671 p. 17, IMG) | DOCUMENTED | each PE is "basically a PSI-II CPU" with stop-interrupt registers added (TM-671 §2.2, IMG) |
| Network | TR-715 §3.2, Fig. 2; TR-390; TM-306; TM-260; TR-393; IPSJ 113879, 15329, 24868 | Channel of 9 data bits plus parity plus busy; bit 8 marks header and tail; 5 MB/s each way; 200 ns synchronous transfer; 48-byte output buffer per channel; 4 KB write and read buffers at the PE port; wormhole routing, x before y, through a software-set path table; each channel FIFO (`literature_gaps.md` Appendix A §6.1). Physical PE addressing is the only mode in use (TM-671 §2.4, IMG) | DOCUMENTED | `multi_pe.md` §3 already takes per-pair FIFO from TR-390 |
| Maintenance path | TM-671 §2.5 (IMG) | An 8-bit single-master bus. A per-PE CSIFR register starts and stops the CPU and holds a microinstruction that the PE can be switched to execute | DOCUMENTED (function); register layout not published | relevant only at microcode level |
| KL1 firmware (`.mbn`, `kl1kp.kbn`, `kl1pat.com`) | none | TM-671 p. 18 (IMG): "16 K steps of 53-bit microinstructions, about 0.1 MB", loaded into every PE over the maintenance path; TR-715, TR-531, TR-585, TR-466, TR-469 give its behaviour, message sizes and step counts | **LOST** (`icot_software_survey.md` §4) | PIM/m's microprogram is this one converted (`literature_gaps.md` "The other PIMs"); the held `pimm.MEkbn` is PSI-III code |
| PSI-II microinstruction | none | 53 bits (TR-265, `literature_gaps.md` §8); ZEUS simulator (TM-212, OCR) | LOST (format not published) | blocks only the microcode-level verdict |
| KL1-B instruction set | `pimos/src/library/assembler/inst_tab.kl1` (the encoding, `kl1_encoding.md`) | TM-662 (code format), TR-715 | HELD-SOURCE | the same `machine_type` (`mpsi`) as PIM/m (`pimos.h`) |
| PIMOS build configuration | `pimos.h` (1995 dpool copy) `case(mpsi)` | `fep_interface kl1_network`, `ipl_parameter no`, `extended_floating_point no`; otherwise PIM/m's settings | HELD (dated 1995, two years after the 3.6 release; INFERENCE, unverified, that 3.6 used the same) | §2.7 |
| PIMOS source branches | 3.6 tree: 13 `fep_interface` sites in 11 files; 9 `case(kl1_network)` branches in 6 of them (`bios/boot/scsi_man.kl1` x3, `bios/boot/scsi_conf.kl1`, `bios/scsi/{scsi_blt,DAMC,scsi_common,DAM,scsi_processor}.kl1`) | — | HELD-SOURCE; the modules the branches call are in the tree (§2.7) | — |
| PIMOS object set for `mpsi` (`mpsi_*.sav`, `mpsi_bios.sav`) | none; the 3.0 manual names `mpsi_bios.sav` (`icot_software_survey.md` §7) | — | not in any held file (searched 2026-11-26, §1); outside sources still open (audit §5 item 12); **rebuildable** with the held compiler (MP1) | the IFS byte grep for `mpsi_*.sav`/`.kbn`/`.mbn` and `ppim_*.sav` matched only the Japanese 3.0 manual `man30.j.ps.Z`, which names `mpsi_bios.sav` and `ppim_bios.sav` |
| The held `pimm_*` objects on a "Pseudo Multi-PSI" | `pimosobj` `INSTALL`: "Pseudo PIM/M system or Psuedo Multi-PSI system" on "PSI-II or PSI-UX" | — | OPEN CONTRADICTION (§6 item 1) | not a held Multi-PSI build |
| CSP and FEP software | `mpsicspR.ptf` (remote CSP half, 30 classes, `psdpim`); CSP command form `PE番号 @ コマンド` (TM-671 §4.1, IMG), the `PE00(00) @ DC>` prefix of the manual's transcripts | CSP and FEP were ESP on SIMPOS, "over 3 MB of source" (TM-671 §4, IMG); manual "Multi-PSI/V2 Console System (CSP) Operating Manual" CITED-ONLY | LOST except `mpsicspR.ptf` (HELD-BINARY-ONLY) | the PSI track's P3/P5 decide whether `mpsicspR.ptf` can run |
| Applications | 28 IFS entries whose abstract's Machine line names Multi-PSI (17 Multi-PSI only: 11, 17, 18, 20, 30, 31, 39, 42, 51, 53, 60, 61, 62, 63, 67, 70, 71) | — | HELD-SOURCE (per entry) | period programs; MP5's candidates |
| Measurements | TR-715 Fig. 10, TR-531, TR-563, TR-585; TM-1260 (append 125 / 114 KRPS at 200 ns, `literature_gaps.md` §6) | message counts, sizes and microstep counts; KRPS | PRINTED | sizes and counts are oracles; step counts and KRPS need the lost microcode (not claimable) |
| Sibling KL1 | PDSS (`pdss.tar.Z`, "widely compatible with the KL1 system found on Multi-PSI"); TM-958 (PDSS 2.52 manual plus source listings: byte-code interpreter in C, MicroPIMOS, KL1 compiler, 214 pp., OCR contents page) | — | HELD-SOURCE | answer oracle beside KLIC |

### 2.2 PIM/p (Fujitsu)

| Item | Held? | Documented? | Status | Notes |
|---|---|---|---|---|
| Hardware, instruction forms, pipeline, caches, network | TR-577, TR-770 (= FGCS'92 pp. 414-424), TR-514, TR-453, TR-389 (`nonlocal/tr0389.pdf`), TM-526, TM-530, TM-531, TM-779, TM-1127, IPSJ 15121 (IPSJ Trans. 30(12)), 59752 (J. Inf. Proc. 13(2)) | instruction forms (TR-577 Table 1), tag conditions (Table 2), free-list and deref instructions (Table 3), cache commands (Table 4), the D A T B pipeline, macro-call, IIM 8 K steps, 80 ns as built (`literature_gaps.md` "detail" §1) | DOCUMENTED except final opcode encodings, MRB bit and tag codes | the 1988 opcode tables, TR-389 PDF pp. 17-18, are **held and still not transcribed** |
| KL1-B to native: templates, post-compiler, assembler, linker | none | TM-1067 §4.2.2 (worked expansions), TR-770 §5.2.2 (three template classes), the tool chain `.klb → .asm → .rkp → .kbn` (TM-1067 Fig. 5) | LOST | — |
| IIM macro bodies, runtime library | none | the split into IIM, local memory and shared memory (TR-770 §5.3, Fig. 7) | LOST | — |
| Runtime (VPIM) | `vpim.tar.Z` | TM-1044 | HELD-SOURCE (PSL); the PSL compiler is LOST | §2.6 |
| Simulator | none | TM-1090 (OCR): 8 PEs per process at machine-instruction level; NIU, router, SPC, SCSI and FEP as further processes connected by sockets (4.3BSD) | LOST | — |
| PIMOS build | `pimos.h` `case(pimp)`; 3.6 tree `case(pimp)` at `pimos.vmac`:429, 444, 465 (timer in µs, float limits) | — | HELD-SOURCE (configuration and branches); object set LOST | the compiler that emits VPIM KL1-B is lost (§2.6) |
| Oracles | FGCS'94 pp. 80-89 Table 2 and Fig. 3: one `append` reduction = 28 instructions in 33 clocks, broken down by category; TM-1320 fn. 9; Table 1, 305 / 281 KRPS; TM-1320 tables 8-19 (inter-cluster costs in clocks) | — | PRINTED | the per-reduction instruction count is the one check a model could pass or fail |

### 2.3 PIM/c (Hitachi)

| Item | Held? | Documented? | Status | Notes |
|---|---|---|---|---|
| Hardware | TR-672, TR-671, TR-704, TR-755 (same title as FGCS'92 vol. 2 pp. 723-730; INFERENCE: its preprint), TR-863, TR-871, TR-869, TM-870, TM-1260; IPSJ 118805..118809, 120649..120651 | datapath, micro-step costs (`literature_gaps.md` "detail" §2) | PARTIAL | — |
| **Microinstruction (new)** | IPSJ 40th convention 2L-2, p. 1179 (`ipsj/118806_*`) | 104 bits (already in `literature_gaps.md`); new here: **6 fields and 41 subfields**, IMG, Table 2: Sequence Control (SC) 6 subfields, 28 bits; Execution Unit Control (EUC) 4, 11; Register File Access Control (RFAC) 8, 18; Bus Load Control (BLC) 7, 23; Memory Interface (MI) 7, 14; Miscellaneous (MIS) 9, 10. Table 1: general registers 8 x 2 words, dedicated registers 256 x 2 words; ALU on tagged data; shifter of 1-8 bits; 3 internal buses; 50 ns machine cycle; data and addresses each 5 bytes plus 5 parity bits. Section 3: an 8-way branch on network state in 2 cycles; a 2-way branch on the slit-check flag in 1 cycle; a block transfer of 4 words in 5 cycles (80 MB/s). About 51 K gates on a CMOS gate array | DOCUMENTED to field width; subfield encodings and tag bits NOT published | closes `literature_gaps.md` §10a item 1 only partly |
| Microcode generation | none | TM-1000 (IPSJ 120650): register allocation, control-flow flattening, micro-templates, micro-address generation from VPIM (OCR, matching TR-672's Figs. 6-7, IMG in `literature_gaps.md`) | tools and microcode LOST | the microcode was generated mechanically, so in principle it could be generated again from VPIM, with the templates ours |
| PIMOS build | `pimos.h` `case(pimc)`: no double-width integer, bignum or floating point; no processor profile; `scsi`, `vpim`. 3.6: `case(pimc)` at `pimos.vmac`:432 only (timer unit `usec15`) | — | HELD-SOURCE (configuration); objects LOST | — |
| Oracles | TR-672 Table 2: 416 microsteps for append in version 1, and the savings by cause; FGCS'94 Table 1: 55 / 56 KRPS at 66 ns | — | PRINTED | — |

### 2.4 PIM/i (Oki)

| Item | Held? | Documented? | Status | Notes |
|---|---|---|---|---|
| Processor, instruction list and formats | TR-675; IPSJ 14717 (the journal version, Trans. IPSJ 33(3), 1992, held: `literature_gaps.md` §8 had it as not found online); TM-846, TM-847, TM-1015, TM-1019, TM-1096 | 40-bit LIW in 3-, 2- and 1-field forms; the instruction list in TR-675's appendix (`literature_gaps.md` "detail" §3) | DOCUMENTED (list and formats); encodings partly | IPSJ 14717 not read here |
| Tag | TM-1017 | lock, GC and MRB bits, 5-bit type, 32-bit value | DOCUMENTED | the only published tag layout of the four |
| Compiler path | none | TM-922 (OCR): the ICOT KL1 compiler produces KL1b (the example prints `try_me_else`, `wait_constant`, `proceed`, `suspend`, the mnemonics of the held compiler's `inst_tab.kl1`). An Oki post-compiler then applies a template database to produce PIM/i assembly. This is the pre-VPIM IP89/IP90 system | post-compiler, templates, template generator and assembler LOST | INFERENCE: for the pre-VPIM system the held compiler's KL1-B text output (`library/loader/outKLB.kl1`) is the kind of input the post-compiler read |
| Simulator | none | TM-923 (OCR): register-transfer level, context mapped into memory | LOST | — |
| PIMOS build | `pimos.h` `case(pimi)` turns off tracing, spying and the shoen and processor profiles. 3.6: `case(pimi)` appears only at `scsi.vmac`:14, and it names `pimi_scsi` and `pim_scsi` | — | **missing modules**: no held file declares `pimi_scsi` or `pim_scsi` (IFS grep, 2026-11-23 and here). INFERENCE: the 3.6 timer macro `mdlib#system_timer_unit` has no `pimi` case, so 3.6 is not buildable for PIM/i as released | — |
| Oracles | TR-675 Tables 2-5 (2.5 machine instructions per KL1b, 0.11 library calls per KL1b, 38 % branches); FGCS'94: 65 KRPS at 240 ns | — | PRINTED (pre-VPIM system) | — |

### 2.5 PIM/k (Toshiba)

| Item | Held? | Documented? | Status | Notes |
|---|---|---|---|---|
| Processor | TR-767, TR-768, TR-769, TM-766 | "RISC type 32bits ... 4bits tag", IP1704, 100 ns; nothing else | CITED-ONLY at instruction level | — |
| Caches | TR-767 Table 1 and Appendix tables A.1-A.5 (state tables, not transcribed) | two-level write-invalidate protocol, bus commands | DOCUMENTED | the only reproducible part |
| Runtime | none | hand-ported from VPIM; REF and EXREF merged; tables built only at GC (TR-768) | LOST | — |
| Debugging tools | none | TM-1011 (OCR): reproducible execution, a GC-off mode, data-access history | LOST | — |
| PIMOS build | `pimos.h` `case(pimk)` exists (1995). The 3.6 source has no `case(pimk)`, so the timer branch is undefined (INFERENCE, as for PIM/i) | — | configuration HELD; branches missing in 3.6 | corrects area L's "no `case(pimk)` anywhere" (already corrected in audit §7) |
| Oracles | FGCS'94: 76 KRPS at 100 ns; TR-768: four PEs 3.5 times one PE on 12-queens | — | PRINTED | — |

### 2.6 What the four VPIM machines share

| Item | Held? | Status | Notes |
|---|---|---|---|
| VPIM PSL source (185 files) | `vpim.tar.Z` | HELD-SOURCE | no per-machine conditionals (Task 3) |
| PSL language | TR-574 (IMG/OCR), IPSJ 117943 「VPIM及びその開発言語PSLについて」 (held, not read), TM-1044 | DOCUMENTED (macro language "of about C's expressiveness" for tag architectures, TR-574 §1) | — |
| PSL-to-C converter and "virtual hardware" (the simulation path) | 5 of 79 `_` primitives in `_function_fast.c` | **LOST** (TR-574 Fig. 2, the simulator path) | `pimos.h`'s `case(pims)` is the simulated machine's PIMOS build. INFERENCE from VPIM's comments (`klb_pimos.psl.c`:417, `bsc_slit_check.psl.c`:8) and its README: "PIM/s" is VPIM run as C on a Sequent or a SUN |
| PSL compiler to native code, macro expander | none | LOST | TR-574 §2 |
| KL1 compiler emitting VPIM KL1-B | none | **LOST**. The held compiler emits the Multi-PSI KL1-B (`try_me_else` ... `inst_tab.kl1`). VPIM's opcode table (`p_opecode_table.psl.c`: `RESET_SSP 0x000`, `COMMIT 0x002`, `READ_WAIT 0x010` ...) is another set; its header says Multi-PSI/V2 uses KL1-B opcodes as built-in IDs and that the RISC machines must reuse these virtual numbers so that PIMOS need not be rewritten per machine | the instruction list is FGCS'92 p. 455 Table 6 (Hirata et al.) |

### 2.7 PIMOS 3.6 per-machine code: counts and the module check

grep of a fresh scratch copy of `pimos.tar.Z`, 2026-11-26. These are
counts of text, not a compile.

- `:- switch(machine)` and `:- switch(machine_type)`: 41 sites in 26
  files. Cases: `case(mpsi,pimm)` 20 (19 written without a space, 1
  with), `case(mpsi)` 9, `case(vpim)` 9, `case(pimp)` 3
  (`macro/pimos/pimos/pimos.vmac`:429, 444, 465), `case(pimc)` 1
  (`pimos.vmac`:432), `case(pimi)` 1 (`macro/pimos/scsi/scsi.vmac`:14),
  `case(pimk)` 0. No `switch(machine)` site separates `mpsi` from
  `pimm`.
- The switches whose value differs between `mpsi` and `pimm` in
  `pimos.h`: `fep_interface` 13 sites, `ipl_parameter` 1
  (`bios/boot/bios.kl1`:52), `extended_floating_point` 27. That is 41
  sites in 26 files: `bios/boot/{bios,scsi_conf,scsi_man}.kl1`,
  `bios/scsi/{DAM,DAMC,scsi_blt,scsi_common,scsi_handler,scsi_processor}.kl1`,
  `debugger/inspector/{cmd_insp,cmd_mon,inspvar,unify}.kl1`,
  `kernel/init/rsc_init.kl1`, `library/unloader/{decoder,encoder}.kl1`,
  `macro/pimos/scsi/scsi.vmac`, `server/scsi/scsiRserver.kl1`,
  `utility/ioutls/{bufutil,mklib,token,uparse,variable}.kl1`,
  `utility/pool/{comp,hash}.kl1` and `utility/sorter/sorter.kl1`. That
  both totals are 41 is a coincidence.
- **The module check (crude).** For each of the 9 `case(kl1_network)`
  branches, the text up to the next `case`, `default` or `end_switch`
  was scanned for `name:` calls and `name#` macro references. The
  result was compared with the 480 names declared by `:- module` in the
  tree. Modules called: `scsi_string_io` (`scsi_man.kl1`:84) and
  `shoen` (`scsi_conf.kl1`:50). Both are declared. The other names
  found (`ascii#`, `string#`, `scsi#`, `pimos_tag#`) are macro
  references, not modules. Five of the nine branches are two lines
  long. The check does not follow calls into other files, and it does
  not show that the branches compile.
- `case(pimi)` maps the SCSI built-ins to modules `pimi_scsi` and
  `pim_scsi`. Neither is declared anywhere held. The timer macro
  `mdlib#system_timer_unit` (`pimos.vmac`:424-437) has cases for
  `mpsi,pimm`, `pimp` and `pimc` only, with no `default`. INFERENCE,
  unverified: 3.6 does not compile as released for `pimi` or `pimk`
  (§6 item 3).

## 3. Verdicts and rank

| Rank | Machine | Verdict | What a reproduction is | Oracle (not ours) | Cost |
|---|---|---|---|---|---|
| 1 | **Multi-PSI/V2** | **FEASIBLE** at the KL1-B and system level. NOT FEASIBLE at the PSI-II microcode level (firmware and microinstruction format lost) | The PIM/m reference model and core, with N PEs (M1..M5), the Multi-PSI network (mesh, path tables, 9-bit units, FIFO channels), PIMOS 3.6 rebuilt with `define(machine, mpsi)`, and an FEP node on the network (`kl1_network`) in place of SCSI | (a) the held `pimm_*` objects, which a `pimm` rebuild must reproduce. (b) The manual's Multi-PSI transcripts: `e-sysman.tex`:104-111, the boot (V3.0, so with R5's caveat); 139-144, the shutdown; `e-version.tex` Examples 1 and 2 (the `$version` line and the IPL loading lines). (c) Message sizes and counts printed in TR-715, TR-531 and TR-585. (d) The 28 IFS entries naming Multi-PSI, and PDSS and KLIC as answer oracles | medium: mostly rungs already planned for PIM/m, but gated on MP1 (compiling PIMOS's own modules, not yet tried) and on M4/M5 |
| 2 | **PIM/p** | FEASIBLE ONLY AS A RECONSTRUCTION (OURS): instruction forms published, encodings and toolchain lost | An instruction-level PE model from TR-577 and TR-770 with our own encodings, or TR-389's 1988 tables once transcribed; VPIM compiled by our own PSL compiler; our own KL1-B-for-VPIM front end | the append trace (28 instructions, 33 clocks, by category); TM-1320's clock counts; FGCS'94 tables; PIMOS's `pimp` branches | very high: three lost toolchains |
| 3 | **PIM/i** | RECONSTRUCTION ONLY: instruction list and tag layout published | for the pre-VPIM system, the held compiler's KL1-B through our own post-compiler to a PIM/i model; at most 8 PEs, no network | TR-675's per-KL1b statistics; FGCS'94 KRPS | very high; PIMOS's PIM/i modules are lost |
| 4 | **PIM/c** | RECONSTRUCTION ONLY: microword field widths published (new), subfield encodings not | our own generator from VPIM to a 104-bit microword of our own encoding | TR-672 Table 2 (416 microsteps and the savings); FGCS'94 KRPS | very high |
| 5 | **PIM/k** | NOT FEASIBLE as a machine: no instruction set published | only the two-level cache protocol, from TR-767's state tables | TR-767 Tables 1 and A.1-A.5 | — |
| — | Multi-PSI/V1 | NOT FEASIBLE now: KL1 in ESP on SIMPOS on PSI-I (TR-237 §4.1, §6.1) | — | — | waits on the PSI track (P4) |

**Why PIM/p ranks above PIM/i.** Both have published instruction
forms. PIM/p also has a published per-reduction trace that a model can
be checked against, the opcode tables of TR-389 (held), and PIMOS
branches that exist in 3.6. PIM/i's PIMOS modules are lost and its
published statistics are for the pre-VPIM system. **The shared first
rung for ranks 2-4** would be "VPIM runs", which needs a PSL expander
(OURS, from TR-574, IPSJ 117943 and TM-1044), the 74 missing virtual
hardware primitives (OURS) and a VPIM-KL1-B compiler (OURS, from
FGCS'92 Table 6). Its oracle would be the answers of KLIC and the PIM/m
model, and TR-666's evaluation figures. It is not proposed here: it
waits its turn after Multi-PSI.

## 4. Proposed rungs: Multi-PSI/V2 (MP)

In the form of `multi_pe.md` §4. Each rung is a runnable check, and the
work goes in its own sibling directory when its turn comes
(`pimos_roadmap.md` §10). Rungs already set elsewhere are named, not
restated.

| Rung | Observable | Oracle | Needs |
|---|---|---|---|
| MP0 | This audit: held, documented and lost per machine, with the searches recorded | — | done 2026-11-26 |
| MP1 | PIMOS rebuilt by its own compiler on the model. **(a)** With `pimos.h` set to `pimm`, a chosen set of 3.6 modules is compiled through the home-file service (as R7 compiled `sample1` and R8 the pkl1 samples). The resulting code is compared, module by module, with the same modules decoded from the held `pimm_*360E.sav`. **(b)** The 26 files with `fep_interface`, `ipl_parameter` or `extended_floating_point` switches are compiled again with `mpsi`, giving `mpsi_*` modules. *Status 2026-11-26: (a) done for 25 of the 26 files (all but `scsi.vmac`, a macro file), (b) NOT done: the owner set Multi-PSI aside. `ref/pimm/mp1_rebuild.py` (outside the suite: it needs the ~1.2 GB prompt checkpoint) compiles each file from the shell's prompt by the held compiler through the home-file service (R7's route, `lockstep_shell.py play`; typed `compile`, `!set compile:assemble_mode firm`, `!package pimos`, NAME, `!exit`), `pimos.h` served as held (`pimm`), and compares the module made with the held one in memory, whose code area is checked item by item against `asm/unlsav.py`'s reading of the `.sav`. Result, pinned: 3 identical but for the header (`scsi_conf`, `DAMC`, `comp`), 18 the same but for the header and three orders (GC area, `hash_on_constant` slot keys, predicate-table chains; INFERENCE: the hash function and atom numbers are ours), `bufutil` among them, 4 differ (`token`: a branch target first, as `mklib`'s; `bufutil` and `token` were refused at `integer_to_floating_point` until floats were modelled, `float.md`, and were re-run then; `hash`: the loaded hasher is `pimm_patch_hash360E.sav`'s, which lacks the `extended_floating_point` clause; a probe compile with `mpsi`'s `pimos.h` was identical to it but for the header, so the patch was built with that switch off; `mklib`, `variable`: a branch target first, not explained). No module is word for word: MagicNum is `[]` in every held module (the IPL's decoder drops it, `lockstep_gca.py`) and ModInfoVec is the compile stamp; there is no code relocation. Injections (a constant, an external call, a string in `rsc_init.kl1`) each give `differs` at the change. Left: (b); `bios.kl1`'s `ipl_parameter` answer (needs the `mpsi` build of it, audit §6 item 7); the base-file hasher, `mklib` and `variable`* | (a): the held objects, HELD-BINARY. A difference is a finding about the release (audit §6 item 7: which `ipl_parameter` branch the held bios was built from), not a failure to fix. (b): the source's own `case(kl1_network)` text | R8 (reached: the compiler runs, home files); `pimos.h` (1995 copy, labelled) as a home file; `asm/unlsav.py` |
| MP2 | The Multi-PSI network in the reference model. An 8 x 8 mesh of PEs; packets in 9-bit units with header and tail; per-channel path tables set by software; x-then-y routing; FIFO per channel; 200 ns per unit. M1-M3's messages travel on it and produce the same answers as on the abstract FIFO network | M1-M3's oracles (`seqgc`, `gc`, the heap monitors). The message sizes in bytes that TR-715, TR-531 and TR-585 print for `throw_goal`, `read`, `answer_value`, `unify` and `release` | M1..M3; TR-715 §3 and Fig. 2. The body layout of each message is ours, from VPIM's logical packets (`multi_pe.md` §3), INFERENCE |
| MP3 | The `mpsi` PIMOS boots on N PEs, with its FEP as a node on the network (`fep_interface kl1_network`: `scsi_string_io`, `scsi_conf.kl1`'s branch). The front end is a stand-in, OURS, speaking the protocol that the `kl1_network` branches define, in place of `fep.py`'s SCSI | `e-sysman.tex`:104-111 (with R5's caveat: a V3.0 transcript). R6's shutdown lines against `e-sysman.tex`:139-144. **This oracle does not discriminate**: the manual says it uses Multi-PSI as its example and that other systems start and stop "essentially identical" (`e-sysman.tex`:92), so a `pimm` build passes it too. The check that is specific to `mpsi` is that the boot goes through the `case(kl1_network)` clauses (§2.7), seen in a trace | MP1(b), MP2, M4, M5 |
| MP4 | The Multi-PSI console's output form: `PEnn(nn) @ DC>` prefixes and the `$version` line of `e-version.tex` Example 1 and the IPL loading lines of Example 2 | the manual's two examples. The remote half `mpsicspR.ptf` if P3 runs it | P3, P5 (the PSI track); without them OURS |
| MP5 | A period Multi-PSI application from IFS (the 17 entries naming only Multi-PSI, §2.1) runs on N PEs | its printed results; KLIC 2.002 and PDSS for answers | MP3 |
| MP6 | Bluespec: N cores of the PIM/m core on a mesh module with Multi-PSI parameters, in lockstep with MP2's reference | the reference's traces | M7 |

Not proposed: anything below KL1-B. The PSI-II KL1 microcode, the
53-bit microinstruction and the CSIFR maintenance registers are lost or
unpublished. Cycle counts from TR-715 Fig. 10 and TM-1260's KRPS are
printed, but they are counts of the lost microcode and cannot be
claimed (`plan.md` evidence gate 4).

## 5. Files fetched

Committed to `lit/trtm/`, as the rest of `trtm/` (the AIST-hosted FGCS
Digital Archive permits free academic use without change,
`LIT_MANIFEST.md` "Rights"). They are recorded in `lit/SOURCES.tsv`
(retrieval "fetched 2026-11-26, other PIMs search"), in
`lit/SHA256SUMS` and in the `LIT_MANIFEST.md` addendum of that date:

- `trtm/tr0704.pdf`: TR-704, Nakagawa et al., "Hardware Implementation
  of Dynamic Load Balancing in the Parallel Inference Machine PIM/c"
  (draft, 1991-10).
- `trtm/tr0755.pdf`: TR-755, the same title, 1992-03 (INFERENCE: the preprint of FGCS'92 vol. 2 pp. 723-730).
- `trtm/tm0958.pdf`: TM-958, PDSS 2.52 manual and source listings
  (1990-09, 214 pp.).

The other twelve new reports (§1) are fetchable at
`Museum/TRTM/{TR,TM}/{TR,TM}pdf/` and were not added.

## 6. Open contradictions and items

1. **"Pseudo Multi-PSI" and the held objects.** `pimosobj`'s `INSTALL`
   says the `pimm_*` set runs on a "Pseudo PIM/M system or Psuedo
   Multi-PSI system". `PIMM.PARAM` is headed "FOR PSEUDO MULTI-PSI"
   (`multi_pe.md` §1.1). But `pimos.h` gives a real Multi-PSI build
   `fep_interface kl1_network` and `ipl_parameter no`, and the objects
   carry PIM/m's settings. INFERENCE: on a single PSI the pseudo systems
   both used the PIM/m build, and the pseudo machine's FEP was the same
   PSI. Whether that is so is not established. The objects are recorded
   as a PIM/m build, not a Multi-PSI one.
2. **TM-526's index title.** The archive's index record `TMidx/tm0526.idx` (quoted in `literature_gaps.md` Appendix E; TM-526 is not in `TMlist.html`) titles it 「並列推論マシンPIM/sの概要」,
   but the page reads 「並列推論マシンPIM/pの概要」 (Goto, Shinogi, Kumon,
   Hattori; IMG). "PIM/s" in VPIM's comments and `pimos.h` is something
   else (§2.6).
3. **PIMOS 3.6 for PIM/i and PIM/k.** Both lack a timer branch, and
   PIM/i lacks its SCSI modules (§2.4, §2.5, §2.7). Whether the 3.6 compiler
   rejects an undefined `mdlib#` macro or leaves the term in place is
   not checked. MP1 would answer it at no extra cost.
4. **Not transcribed or not read, though held:** TR-389 PDF pp. 17-18
   (PIM/p 1988 opcode tables); TR-767 Appendix A (PIM/k cache states);
   IPSJ 14717 (PIM/i journal paper), 15121 (PIM/p journal paper),
   117943 (VPIM and PSL), 120649 and 120651 (PIM/c firmware and
   micro-address generation); TR-237's network figures; the 12 reports
   of §1.
