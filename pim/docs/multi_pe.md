# PIM/m with more than one PE: the evidence, the rungs, and M1

Written 2026-11-26. This is the plan of record for `pimos_roadmap.md`
§7's first bullet, multiple PEs: goal distribution (`@node`), inter-PE
messages, distributed unification and the export tables. It has three
parts: what the held sources say (§1-§2), the design choices that are
ours (§3), and the rungs M1.. with their oracles (§4). §5 is the status.

Labels as everywhere in `pim/`: PRINTED (a held document or file says
it), HELD-SOURCE (held code does it), INFERENCE (our reading, with the
reason), OURS (a choice of this project). The extracted archives used
here (`nonlocal/psdpim.tar.Z`, `pimos.tar.Z`, `pimosman.tar.Z`,
`vpim.tar.Z`, `pimosobj.tar.Z`) are read in a scratch directory; the
Pseudo PIM/m texts are decoded with `asm/psdpim.py --text FILE` (the
line numbers below are of that tool's output) and the compiled ESP with
`asm/ptfdump.py`.

## 0. Answer in brief

- **The real PIM/m firmware is lost, and with it the PIM/m's own
  message bytes.** No held file gives the network packet's byte layout
  for PIM/m or the firmware's inter-PE routines in readable form.
- **The held Pseudo PIM/m archive is a multi-PE system in its
  configuration and console.** Its `PIMM.CONFIG` describes an 8 x 4
  grid of PEs, PIM/m's cabinet (32 PEs, `M92` pp. 425-426), with one
  PE in use and commented-out settings for 2, 4 and 8. Its
  `PIMM.PARAM` is headed "FOR PSEUDO MULTI-PSI" and sizes a per-PE
  "Network Comm. Area", a Read Packet Buffer, the four export/import
  tables and the WTC throw and supply units. The console
  (`pimmcsp.ptf`) runs Pseudo Multi-PSI PEs round-robin with a
  reduction quota, clears their "Network Communication Area", and
  names the 26 message kinds with their codes. Whether the held
  firmware `pimm.MEkbn` itself runs several pseudo PEs is NOT
  established: its body is not read (`pseudo_pimm_microcode.md`).
- **The message codes are read** (new): the console's
  `kl1_message_order_macro` pairs `m_throw` .. `m_profile_request`
  with `00` .. `17` (hex) and `m_multi_cont`, `m_multi_last` with `1E`,
  `1F`; the order is VPIM's `_NW_` numbering exactly where both define a
  code (0-10, 14-23). `literature_gaps.md` §6 had them as unknown.
- **PIM/m used the VPIM / Multi-PSI design for the inter-PE data.**
  PIMOS's own tag table (`debugger/inspector/tagtbl.kl1`) holds the
  exported-variable tags `EUNDF`, `EHOOK`, `EMHOK`, the read hook
  `RHOOK`, the external cells `EXREF`, `EXVAL`, and the foster-parent
  record tags `FPREC`, `FPRECt`: the machinery of TM-1044 chapter 9.
- **`@node(N)` is one instruction**, `enqueue_goal_to_processor`
  (23:65); `@processor` is commented out of the compiler. On PIM/m a
  node is a PE and the processor number inside it is always 0 (manual,
  PRINTED).
- **Printed oracles exist**: the primer's `sample9` with its printed
  placement order, the manual's exception rules for a bad node number,
  and PIMOS's own `gc` and `seqgc` commands, whose collections over
  the nodes follow from their source. MGTP/G (R9) is not a multi-PE
  oracle; MGTP-N (IFS No. 91, "only executable on PIM/m") is a later
  one: its manual prints a 1-PE run's statistics and the goals for 64
  and 256 PEs, but no per-PE figure (§1.5).
- **Rungs M1..M7** are in §4. M1: N separate machines,
  `current_node`, `Goal@node(K)` as a `%throw_goal`, and the `%unify`
  that binds an exported variable, checked by PIMOS's own compiled
  `seqgc` and `gc` modules from `pimm_shell360E.sav` on 1, 2 and 4 PEs
  under two schedules. M2 and M3 add reading across PEs and the
  white/black tables, M4 the shoen across PEs, and M5 PIMOS booted on
  1, 2 and 4 PEs running the primer's `sample9` and R8's qsort with
  `@node` from its prompt (a long runner). Their status is in §5.

## 1. What the held sources say

### 1.1 The Pseudo PIM/m archive (`nonlocal/psdpim.tar.Z`)

| What | Where | Label |
|---|---|---|
| `pes([[@,@,@,@], ... [*,@,@,@], ...])`: eight rows of four, one `*`; three commented alternatives with two, four and eight `*` (2 x 1, 2 x 2, 4 x 2 blocks). Header: "Released at 21-Nov-91 by ICOT 1st lab. Firm Gr." | `SYSTEM.DIR/PIMM.CONFIG`, lines 1-37 | PRINTED |
| `*` marks a PE in use, the grid is the PE array | the counts 1, 2, 4, 8 of the four settings, and 8 x 4 = 32 = one PIM/m cabinet (`M92` pp. 425-426) | INFERENCE |
| "MPSI.PARAM ... *** FOR PSEUDO MULTI-PSI ***" | `PIMM.PARAM`, lines 1-2 | PRINTED |
| `pmp_ncas` 16'1800: "PMP Network Comm. Area Size (for one PE in memory words)", "must be less than the size of the Read Packet Buffer" | `PIMM.PARAM`, lines 43-46 | PRINTED |
| Read Packet Buffer 16'3000-16'AFFF; Multi-Packet Queue Tables for FEP and PE (16'170, 16'180); Original Network Path Table (16'1000) | lines 52-77 | PRINTED |
| Black export hash 16'800 entries, black export table 16'1200 ("4 * Entry"), black import hash 16'800, black import table 16'800 ("5 * Entry"), white export 16'1000, white import 16'1000; "The White Import Table must be at the last of the Area 5 (for Pseudo Multi PSI)" | lines 94-127 | PRINTED |
| `wtctu` 16'400 "WTC Throw Unit", `wtcsu` 16'1000000 "WTC Supply Unit", `rsctu`, `rscsu`, `rsclm` (resource throw, supply, limit) | lines 128-138 | PRINTED |
| The WTC throw unit is VPIM's `_WTC_THROW_GOAL_UNIT` 0x400 (2^10) | VPIM `functions/f_int_cl_send_throw_goal.psl.c`:116 | HELD-SOURCE, agreeing |
| `$GO/PIMos`: "starts CPU and throws a boot goal to the boot PE"; start address 2000 (Multi-PSI), 200 (Pseudo MPSI) | `pimmcsp.ptf` text, lines 523-524, 588-589 | PRINTED |
| `$NETClear`: "clears the Network Communication Area of the PEs and the FEP(s) (for the Pseudo-MPSI)" | lines 660-664 | PRINTED |
| `$SCHedule` (Pseudo-MPSI only): "the menu of the Pseudo PE Schedule rules"; class `roundrobin_scheduler` with `begin_pe`, `reduction`, `quota`, `next_pe` | lines 713-715, 4069-4081 | PRINTED (names) |
| The pseudo PEs are run in turn, each for a quota of reductions | the method names | INFERENCE |
| Classes `pseudo_pe_process`, `pseudo_mpsi_network_handler`, `kl1_network_area`, `csp_import_export_table_inspector`, `csp_network_inspector`, `kl1_message_handler`, `multipacket_manager` | lines 20-260 | PRINTED (names) |
| Message names `%READY %START %STOP %ABORT %READ %RELEACE %UNIFY %EXCEPTION %GUARD_FAILURE %UNIFICATION_FAILURE %RAISED %REQUEST_WTC %SUPPLY_WTC %SUPPLY_RESOURCE %ASK_STATISTICS %ANSWER_STATISTICS`; "A read message was thrown to PE\d"; "Throw_goal & read Messages were thrown from FEP\d to PE\d" | lines 4989-5004, 8230-8231 | PRINTED |
| The FEP side encodes thrown goals: `make_throw_goal_packet`, `encode_shoen_id_for_throw_goal`, `encode_priority`, `encode_arguments`, `encode_code`, `get_WEC`, `exref_mrb`, `exval_mrb` | lines 4855-4930 | PRINTED (names) |
| Black/white import/export entry fields | `pseudo_pimm_firmware.md` §2 | PRINTED |
| The decode table has an entry for `enqueue_goal_to_processor` (23:65, `4a022014:03 06034c67:83`), `current_processor` (22:EB) and `current_node` (22:EE) | `asm/psdpim.py --table`, `--table 2` | PRINTED (bits); the routines are not read |

**The message codes.** `asm/ptfdump.py pimmcsp kl1_message_order_macro`
prints the macro class's constants: `16 "00"` .. `16 "17"`, then
`16 "1E"`, `16 "1F"`, 26 in all, and its symbols are the 26 names
`m_throw m_ready m_terminated m_start m_stop m_abort m_read
m_answer_value m_release m_unify m_exception m_guard_failure
m_unification_failure m_raised m_request_wtc m_supply_wtc m_return_wtc
m_request_resource m_supply_resource m_return_resource m_ask_statistics
m_answer_statistics m_profile_information m_profile_request
m_multi_cont m_multi_last` (`pimmcsp.ptf` text 4033-4060). Pairing
the n-th name with the n-th constant (INFERENCE: the counts agree and
the class has no other constants) gives `m_throw` 0, `m_read` 6,
`m_answer_value` 7, `m_release` 8, `m_unify` 9, `m_exception` 10,
`m_guard_failure` 11 .. `m_raised` 13, `m_request_wtc` 14 ..
`m_profile_request` 23, `m_multi_cont` 30, `m_multi_last` 31. VPIM
(`structures/str_int_cl_packet.psl.c`:71-105) numbers `_NW_THROW_GOAL`
0 .. `_NW_EXCEPTION` 10, leaves 11-13 "for stream optimisation, not
implemented", and has `_NW_REQUEST_WTC` 14 .. `_NW_SHOEN_PROFILE_REQUEST`
23 in the same order as the console; VPIM's 24-29 (`PIMS_SHUTDOWN`, the
BEXID messages, `NAK_START/STOP`) are not in the console's list. This
is console-side and Pseudo Multi-PSI-side evidence: it is the code the
CSP and FEP speak, which the firmware must decode, not a reading of
the firmware.

### 1.2 PIMOS (`nonlocal/pimos.tar.Z`, `pimosman.tar.Z`)

| What | Where | Label |
|---|---|---|
| `Goal@node(N)` compiles to `create_to_processor`/`enqueue_to_processor`; the `@processor` pragma is commented out | `library/compiler/newnorm.kl1`:839-844, 903-905; `comp.kl1`:330-347 | HELD-SOURCE |
| `enqueue_goal_to_processor` is 23:65 `r_c16_c8_exe` (the `r_c16_c8_ext` form commented out); `current_processor` 22:EB `r_r_r`, `current_node` 22:EE `r_r` | `library/assembler/inst_tab.kl1`:84-85, 343, 347 | HELD-SOURCE |
| `export_entry`, `import_entry`, `structure_entry` are functions 0-2 of 23:76 | `inst_tab.kl1`:124-131; compiler `blt.kl1`:347-352 | HELD-SOURCE; no PIMOS source calls them |
| "A node is a set of 1 or more processors, such as a cluster ... In Multi-PSI a single node is a single processor"; a goal without `@node` runs on its parent's node | `Eman/e-syntax.tex`:405-412 | PRINTED |
| The node number in exception data is "the cluster number ... converted to a relative value"; "the processor number will always be zero on PIM/m and Multi-PSI systems" | `Eman/e-shoen.tex`:420-429 | PRINTED |
| On PIM/m and Multi-PSI an atom as the node is `illegal_input` and an out-of-range number `range_overflow`, both reported as built-in `enqueue_goal_to_node` with ArgV {node, code} | `Eman/e-shoen.tex`:486-490, 509-514 | PRINTED |
| A goal sent to another node runs there in a new "foster parent shoen" | `Eman/e-shoen.tex`:304 | PRINTED |
| `current_node(^NodeNumber, ^TotalNode)`, 0 <= NodeNumber < TotalNode, never suspends | `Eman/e-builtin.tex`:1490-1497 | PRINTED |
| The primer's load distribution chapter: `sample7` (`a@node(0), a@node(1), a@node(2)`), `sample8` (a variable node "is suspended until the variable is instantiated to a number"), `sample9:distribute(8)`: "If only 4 nodes are available, the goals will be distributed to nodes number 0 through 3, in the order 0,1,2,3,0,1,2,3" | `primer25.tex`:1090-1175 | PRINTED |
| The shell variable `node` (`set node = 0` in the manual's `shell.com`), `setShlVar(node, ...)` checked against `current_node`; the `cn` command prints "Current node" and "Number of node" | `Eman/e-shell.tex`:997; `shell/main/comexe.kl1`:217-222; `shell/utils/cn.kl1` | PRINTED, HELD-SOURCE |
| 113 `@node` sites in the PIMOS tree: the boot (`bios/boot/bios.kl1`:383, `scsi_man.kl1`:63, 499, 506, `sysTman.kl1`:39), stdio (`kernel/stdio/std.kl1`, `s-server.kl1`), tasks (`kernel/task/*.kl1`), the FEP servers, the loader (`library/loader/dstrbt.kl1`:145), the shell's `gc`, `seqgc`, `job` | grep of `src`, `src_util` | HELD-SOURCE |
| `gc:go/0` sends `gcCall(M)@node(PE)` to every other node through one merger and collects on its own node when the merger's output closes; `seqgc:go/0` visits the nodes one at a time (0, 1, .., skipping its own), each round waiting for the merger output `[]`, then its own node | `shell/utils/gc.kl1`, `shell/utils/seqgc.kl1` (whole) | HELD-SOURCE |
| Both are compiled in the held objects: `pimm_shell360E.sav` modules 22 (`gc`, 3 predicates) and 33 (`seqgc`, 4), no external calls | `asm/unlsav.py` | MEASURED |
| The PIMOS load-balancing utility (STB, MLB; IFS, Mitsubishi, 1992) uses `current_node` and `@node` | `src_util/parallel/{STB,MLB}.kl1`, `README` | HELD-SOURCE |

### 1.3 VPIM (`nonlocal/vpim.tar.Z`) and TM-1044

VPIM is the runtime of the other PIMs in PSL source, with its manual
TM-1044 (`DOCUMENT/TM-1044.j`, Japanese). Chapter 9 (`s9.tex`,
`s9-message.tex`, `s9-network.tex`, `s9-msg-kl1data.tex`) is the
inter-cluster machinery; `functions/f_int_cl_*.psl.c` is its code.

- **Two sends, and PIM/m's is the cluster one.** VPIM's
  `i_ExecEnqueue` (`interpreter/klb_fork.psl.c`:1040-1133) sends a goal
  for `ENQUEUE_TO_CLUSTER` as a `%throw_goal` message
  (`f_Send_IntClMsg_ThrowGoal_Sub`, 1075), after an out-of-bounds check
  against the foster parent's node range (1069), and for
  `ENQUEUE_TO_PROCESSOR` to another processor of the same
  shared-memory cluster (`f_SendGoalToPE_in_cluster`, 1127). PIM/m has
  one memory per PE (`M92` p. 430: a remote reference is a PE and an
  export entry) and one processor per node (§1.2). So PIM/m's 23:65
  to another node is VPIM's cluster branch, the message (INFERENCE,
  from those two statements; the PIM/m compiler having only the one
  instruction).
- **A variable node waits** (`klb_fork.psl.c`:406-447): a goal hooked
  on the number. Already on both models (`lockstep_tproc.py`).
- **Message formats** (VPIM's "logical packet", one 40-bit word per
  item; "on the real PIM the packet format will differ per machine",
  `functions/f_int_cl_msg_type.psl.c` §3): `%throw_goal` = kind, shoen
  ID, WTC, the shoen's priority range, resource, profiling flag, the
  node range (minimum node, count), the goal's priority, the code (the
  module's structure ID, its external reference, WEC, offset), the
  arity, the arguments (`f_int_cl_send_throw_goal.psl.c`:15-60).
  `%unify` = kind, shoen ID, WTC, priority, profiling flag, node range,
  argument 1 (the external reference), argument 2 (level-1 copy)
  (`f_int_cl_recv_unify.psl.c`:9-35). External reference ID: 8-bit
  cluster, 4 flag bits, 20-bit export offset (`f_int_cl_msg_type.psl.c`
  §4).
- **Exporting a variable** (TM-1044 `s9-msg-kl1data.tex`:269-300): the
  cell's type becomes `EUNDF`/`EHOOK`/`EMHOK` and a pointer to it goes
  in the export table; the message carries `WEXREF` (white, single
  reference) or `BEXREF` and a WEC (black). **White import**
  (`s9.tex`:199-215): a white import record holding the external ID
  (tag `INT`) and a one-word external cell pointing at it, the cell's
  tag the message's; "the white import table is allocated in the
  system's fixed area" so the collector does not move it.
- **Copy levels**: level 0 for a thrown goal's arguments, level 1 for
  `%unify` and `%answer_value` values (TM-1044 §9.2; TR-715 5.4.1, in
  `literature_gaps.md` Gap 6.6).

### 1.4 The literature

`literature_gaps.md` §6 and Appendix A Gap 6 already hold what the
English reports say (TR-715, TR-390, TR-466, TR-531, TR-585; `M92`
pp. 427, 430-431): the Multi-PSI/V2 packet (header, message order byte,
body, tail), the six named messages with measured sizes and costs, the
four table kinds and their entry layouts (which the Pseudo PIM/m
parameter sizes match), WEC arithmetic, safe and unsafe references,
the unification table, and that a channel between two PEs is FIFO
(TR-390 3.1). For PIM/m itself only `M92` speaks: export entries never
move, remote reference = PE + export entry, MRB-off and MRB-on tables
(INFERENCE: PIM/m's white and black, chosen by the MRB, as TR-466
4.3.1 says for Multi-PSI), modules fetched by global identifier, 9-bit
packet bytes and hardware-assembled 40-bit words.

### 1.5 What is not held

- The PIM/m firmware's message bytes and its inter-PE routines; the
  Pseudo PIM/m microcode body (held, not read).
- Whether `pimm.MEkbn` runs several pseudo PEs or one (§1.1).
- How a PE gets a module's code the first time (`M92` p. 430-431 in
  outline; `library/loader/dstrbt.kl1` distributes at load time; not
  read further).
- Any per-PE figure for a PIM/m run that the model could match: the
  FGCS'92 PIM/m figures are times; MGTP/G's manual prints reductions
  for one engine and no node count. MGTP-N's English manual
  (`MGTP-N-KL1/mgtp-manual-E.ps.gz` in IFS No. 91, read 2026-11-26 as
  text, page by its `%%Page` number) prints one run in full on the
  **1-PE** configuration, `mgtp:do([{0,0}],[{0,0}],...,S,0)@node(0)`:
  its `distribute`/`store`/`reach` progress lines, the statistics
  `S=[..., model:1758, kept:1753, tested:1757, keptG:61, distr:1797,
  distrG:183, ...]` and `65247574 reductions 729807 msec` (p. 57,
  PRINTED); then only the goals for 64 and 256 PIM/m PEs and 32 and
  128 PIM/p PEs (`...@node(63)`, `@node(254)`), with no output printed
  for them (p. 57, PRINTED). Its CMGTP chapter gives a speedup only as
  a ratio of times (256 PEs against 62: 3.97, limited-branch scheme;
  the per-scheme run-time monitors are figures 6.8-6.10, pictures; p.
  72, PRINTED). So no per-PE count is printed; the 1-PE statistics are
  an answer a multi-PE run must reproduce (M6).

## 2. Oracles for the multi-PE rungs

| Oracle | What it fixes | Label |
|---|---|---|
| `seqgc:go/0` from `pimm_shell360E.sav` | on N nodes run from node c: N collection requests (the `collect_garbage` guards), one per node, in the order 0, 1, .., N-1 without c, then c; a round's `%unify` is sent before that node's collection is made (`proceedGcCall/1` is a tail call, and the collection waits for a goal switch); N-1 throws, N-1 `%unify` | HELD-SOURCE, its dataflow |
| `gc:go/0` from the same file | N requests and N collections, one per node; c's request after every other node's `%unify` was sent; the others' order not fixed; N-1 throws, N-1 `%unify` | HELD-SOURCE |
| KL1's semantics | placement does not change an answer: every multi-PE run's results equal the one-PE run's and KLIC 2.002's | the language |
| The primer's `sample9` | the placement order 0,1,2,3,0,1,2,3 for `distribute(8)` on 4 nodes | PRINTED |
| The manual's exception rules | an atom node is `illegal_input`, an out-of-range one `range_overflow` | PRINTED |
| MGTP-N (IFS No. 91), STB/MLB, Distributed Pool | larger programs written for several nodes; for MGTP-N the manual's 1-PE run, whose model statistics (`model:1758`, `kept:1753`, ...) a run on more PEs must give again (§1.5); no per-PE figure printed | HELD-SOURCE; PRINTED (MGTP-N manual p. 57); others as KLIC's or the papers' |

## 3. Choices that are ours

- **Separate memories.** Each PE is its own `pimm.Machine`, heap and
  registers its own (PIM/m: one memory per PE, `M92`).
- **The same code on every PE.** The modules are loaded once and the
  loaded machine copied to every PE (OURS scaffolding). Since M4/M5 a
  code or module word in the heap goes as its module's number and
  offset, each PE taking its own copy, and a module made after the
  split is fetched (§5, M4): PIM/m sends the module's global
  identifier and fetches the module on demand (`M92` pp. 430-431).
  Until then a thrown goal carried it as `{COD, address}`.
- **Messages are VPIM's logical packets** (§1.3), one word per item,
  fields we do not model sent as 0. The kind codes are the console's
  (§1.1). No PIM/m byte format is invented.
- **Delivery**: each ordered pair of PEs is a FIFO (TR-390 3.1); a PE
  decodes every message waiting for it at a goal switch, before it
  takes its next goal (TR-715 3.3, "decoded at a slit of reductions").
- **Scheduling**: the PEs run in turn, PE 0 first, each for a quota of
  goals (the console's `roundrobin_scheduler`, §1.1, INFERENCE as to
  the unit). Every M1 check is run with two quotas, 1 and 1,000,000,
  and must give the same answer under both: what the pins hold is the
  program's, not the scheduler's.
- **Node numbers are absolute**, for goals of the root and of a shoen
  alike: the relative numbering of a shoen's node range
  (`e-shoen.tex`:428) is not modelled (open at M4, §5).

## 4. The rungs

| Rung | Observable | Oracle | Needs |
|---|---|---|---|
| M1 | N PEs; `current_node` gives (k, N) on PE k; `Goal@node(K)` with K another PE sends `%throw_goal` and the goal runs on K; an unbound argument is exported and the importer's body unification of it with an atomic value sends `%unify` home, which binds it and wakes its waiters | `seqgc:go/0` and `gc:go/0` (§2) on 1, 2, 4 PEs, under two schedules | the reference model only |
| M2 | Reading an external reference: a guard or `wait` on an imported cell sends `%read`, the reader's goals wait on a variable of its own, the exporter hooks a reply record (VPIM's `RHOOK`) on its variable if unbound, `%answer_value` brings a level-1 copy and the import is given back with `%release`; structures exported at level 0 (a list one cons at a time); a reference coming home resolves to the local cell | PIMOS's own `h_monitor` and `x_h_monitor` (the paragraph profiler's heap meters) on 1, 2, 4 PEs, homes 0 and N-1, against what their source fixes; bench cases on their `reverse/2,3` and `out/2` (§5) | M1 |
| M3 | The tables as the machine had them: white and black by MRB with WEC (TR-390 §7, unit 2^24), `%release` with WEC, an imported ID passed on as VPIM does (the release export, half the WEC, the indirect export), the export table a root of the collector and the import table weak; the exported variable retagged `EUNDF`/`EHOOK` (TM-1044; `EMHOK` not) | the heap monitors of M2 collected at every quiescence, WEC conserved, every entry named by an import; an injected leak or double release failing a check; a collection with live exports | M2 |
| M4 | The shoen across PEs: foster parents (`FPREC`), WTC (`wtctu`, `wtcsu`), `%terminated`, `%ready`, resource messages, exceptions for a bad node number | the manual's `range_overflow`/`illegal_input`; a shoen spread over nodes terminating once | M3 |
| M5 | PIMOS boots on N PEs (its 113 `@node` sites), and the shell's `cn`, `gc`, `seqgc`, `set node` run | `cn.kl1`'s printout; §2's collection counts through the shell | M4; code fetch by module identifier |
| M6 | A period multi-node program: MGTP-N, STB/MLB, Distributed Pool | its answer (KLIC's; for MGTP-N the 1-PE statistics its manual prints, p. 57) | M5 |
| M7 | The Bluespec core: N cores on `PimMesh.bsv`, or one core whose network port is answered from a recorded tape (as `lockstep_scsi.py` answers the SCSI port), in lockstep with the reference | the reference's per-PE traces | M1 on the reference (the tape) |

**Why M1 is not on the core in this step.** The core is one PE. In
lockstep it would need a network port: the messages a PE receives come
from other PEs, so on a single core they must be a tape recorded from
the reference (the bench's device tape is the pattern), and the
instructions that send (`enqueue_goal_to_processor` to another node,
a unification of an `EXREF`) need a new port and box on the core. That
is the shape of M7, not a small change inside this rung.

## 5. Status

**M1 reached on the reference model, 2026-11-26.** `ref/pimm/pimm_pe.py`
(the PEs and the network, §3) and `ref/pimm/m1_gc.py` (the check, in
`run_tests.sh`). `pimm.Machine.run` was split so that a goal switch is
one method, `goal_switch()`, which the PEs call between deliveries;
one machine's traces are byte-identical to before (compared on
`lockstep_tproc`, 2,066,384 lines; `lockstep_shoen3`, 13,165;
`lockstep_merge`, 2,438; `lockstep_shoen`, 5,534; one-machine
`seqgc`, 334).

What runs: PIMOS's compiled `seqgc:go/0` and `gc:go/0`
(`pimm_shell360E.sav`, modules 33 and 22) on (N, c) = (1,0), (2,0),
(2,1), (4,0), (4,2), each under quota 1 and quota 1,000,000: 20 runs,
`m1 gc: PASS (20 runs)`, about a minute (35 s with `M1_CACHE`).
Reductions on the home PE (quota 1 / long quota): `seqgc` N=2 23/25,
N=4 45/51; `gc` N=2 10/12, N=4 18/22; each other PE 2 (`seqgc`) or 1
(`gc`). The difference is the scheduler's (a `waitGcLoopSeq/6` that
suspends once under the long quota), so reductions are printed, not
pinned.

Observed fault injections (each on a private copy of `pimm_pe.py`,
the whole `m1_gc.py` run):

| Injection | Observed |
|---|---|
| every `@node` made local | every N>1 case FAILS under both quotas (request and throw order, one request per node, one collection per node, messages `{0: 0, 9: 0}`); N=1 passes |
| `current_node` gives node 0 everywhere | the c≠0 cases (`seqgc` and `gc`, 2/1 and 4/2) raise `KeyError` (e.g. 3762438966): a collection mid-run drops the loaded code, which is not a root in the bare run; the c=0 cases pass |
| `current_node` gives TotalNode 1 | every N>1 case FAILS (no throws; with c=2 one throw, to PE 0) |
| no `%unify` sent | every N>1 case FAILS under both quotas; the home is left with live exports and 2 or 4 suspended goals |
| `%unify` writes the cell without waking its waiters | all cases PASS under quota 1; under quota 1,000,000 every N>1 case FAILS, and "the two schedules differ": why both quotas are run |
| the raw external word passed as the argument (no import) | raises `Unimplemented: a second unification of external cell (50, 16777217)` |

Not reached, open:

- On the core: M7 (above).
- (Done at M2, below: `current_processor`, `unbound` and
  `to_processor` with another PE; structure arguments.)
- (Done at M3, below: a collection with live tables.)
- Every check of `m1_gc.py` fired under at least one injection (tally
  of the observed FAIL lines: request order, throw order, one
  request/throw per node, one collection per node, messages, node c
  asks after every `%unify` (no-`%unify` and no-wake), PE k left
  (the same two), the two schedules differ (no-wake)). The node-0 and
  no-import injections are caught by a raise, not by a check, and the
  node-0 one only where c is not 0.
- The bare run's loaded code is not a collector root (the node-0
  injection shows it); in PIMOS the module table is. (Done with M4,
  below: the modules are roots and code goes by module number; the
  node-0 injection is now caught by the checks.)
- (Done at M2: structures are exported.)

**M2 reached on the reference model, 2026-11-26.** `ref/pimm/pimm_pe.py`
(reading, answering, releasing, structures at levels 0 and 1) and
`ref/pimm/m2_read.py` (the check, in `run_tests.sh`, after `m1_gc.py`).
`pimm.py` and `pimm_gc.py` are unchanged; `m1_gc.py` still passes.

What is modelled, and from where:

- **Level 0** (a thrown goal's arguments, a level-1 value's elements):
  an integer, an atom or `{}` as it is; anything else exported, an
  unbound variable as `EXREF`, a list, vector or string as `EXVAL`
  (VPIM `f_GetLogicalPacketData_W_*Group`), the tag's low bit the
  path's MRB (PIMOS `tagtbl.kl1` 32h-35h). An imported ID going back to
  its owner goes as it is; to a third PE it is exported again (an
  indirect export, OURS for every path: VPIM forwards the ID itself
  on a white path, `f_Put_EX_inLogicalPacket_Sub` "解放輸出", which
  rung M3 takes up).
- **Level 1** (`%unify`'s value, `%answer_value`'s): the list cell, a
  short vector, a long vector with its length, each element at level
  0 (VPIM `f_int_cl_msg_type` section 4 (3)); a string as its
  descriptor and words (OURS: VPIM's table says it is undecided).
- **`%read`** `{6, ID, reply ID}`: the first goal to wait on an
  external cell sends it once; the reader's waiters hook on a fresh
  variable V of its own, exported as the reply ID. The owner answers at
  once if the data is bound, else hooks a reply record on its variable
  (VPIM `f_int_cl_recv_read`: an `RHOOK`; here a goal record with no
  code, OURS, so that hook, wake and collection need nothing new); a
  reply record woken with its variable bound to another variable waits
  again on that one.
- **`%answer_value`** `{7, reply ID, value}` binds V; the external cell
  becomes a reference to V and the import is given back with
  `%release {8, ID}` (VPIM `f_ReceiveAnswerValue_Body`, the RDHOK case:
  OURS that every read keeps its import this way).
- **`%unify`** as at M1, now with a structure value at level 1; a
  unification of an external cell with a variable of this PE makes
  the variable a reference to the cell (VPIM
  `f_Send_IntClMsg_Unify_Sub` (1)). With a read pending, the value is
  also unified with V. Each white export entry gets exactly one
  `%unify` or `%release` (OURS: M2 treats MRB-on and MRB-off alike).
- **`current_processor(^C, ^X, ^Y)`** gives (k, N, 1): PIMOS's
  `mdlib#current_cluster(Cluster, Total)` is `current_processor(Cluster,
  X, Y), Total := X*Y` (`pimos.vmac` 378-381, HELD-SOURCE); N x 1 is
  OURS. **`unbound/2`** gives `{k, Address, X}` (VPIM `kblt_b_unbound`,
  its cluster number); of an external reference VPIM throws a goal to
  the owner: refused. **`get_heap_size(^Size, ^Used)`** (22:FE): Size
  half of the cells from the heap's start to the end of memory (VPIM:
  "one half of the copying collector's heap"), Used the cells in use;
  the values OURS, logged for the check.

The oracle programs are PIMOS's: `h_monitor` and `x_h_monitor` of
`pimm_debugger360E.sav` (HELD-SOURCE `debugger/paragraph/processor/
hmonitor.kl1`, `x_hmonitor.kl1`), the profiler's heap meters. Each
throws `pe_profile` to every node and, per `profile` on its stream,
collects each node's `get_heap_size` as a list of `{Used, UnUsed}`
node 0 first: `h` by binding each node's stream from the home, `x`
by all nodes reading one stream and binding their own back. They are
loaded by `ipl_loader:load/4` and found by their predicate heads,
checked against the source's predicate order. On (N, c) = (1,0),
(2,0), (2,1), (4,0), (4,3), three rounds each, both quotas: every
answer is each PE's own logged heap, each PE asked three times, the
message counts and what is left the same under both quotas, every
import left naming a live entry. Messages (throw, read, answer,
release, unify): `h` N=2 1/8/7/7/3, N=4 3/24/21/21/9; `x` N=2
1/14/13/12/1, N=4 3/42/39/36/3. What is left is the monitors' own
waiting (each node's goal on its stream, the home's on the answers),
with the imports and entries those goals hold.

Bench cases (OURS, on h_monitor's `reverse/2,3` and `out/2`, N = 2
and 4, both quotas): a list of six read across one cons at a time and
reversed back (`rev`), the same with the node a variable bound later
(`node`), with the goal sent on by way of PE 1 (`third`: back home on
2 PEs, on to PE 2 on 4, an indirect export), an ID coming home through
`%unify` (`home`), a reply record that waits again (`chain`), a
variable of the reader bound to an external cell and a `%unify` with
a read pending (`alias`), and `out/2`'s `wait(String)` reading a
string and a vector of seven at level 1 (`wait`). Each pins the
answer, the messages by kind and what is left. Every path the PE code
marks must run (14 of them). `m2 read: PASS (52 runs)`; loading the
file is about 90 s of it, which `M2_CACHE=PATH` saves between runs.

Observed fault injections (each on a private copy of `pimm_pe.py`,
the whole `m2_read.py` run):

| Injection | Observed |
|---|---|
| no `%read` sent | 107 FAIL lines: every N>1 monitor case (each PE asked three times, the answers), every bench answer, message count and table, `PE 1 has S`, the path list |
| a woken reply record not hooked again | 12: `chain` (R, messages, tables) only |
| an ID going home exported again | raises `RuntimeError: heap full` (the reads chase each other round the PEs) |
| no `%release` after `%answer_value` | 44: messages and tables of `rev`, `chain`, `wait`, `node`, `third` |
| `%release` sent twice | 478: `release of a free entry` in every case, bench messages |
| `%unify` keeps the export entry | 30: the tables of every bench case |
| the external cell not made the value after `%unify` | raises `KeyError` (a later read of the given-up import) |
| every `@node` made local | 33: the monitors' asked/answers, the path list (level 1 vector never ran) |
| `current_processor` gives Y = N | 1: builtins |
| `unbound/2` gives node 0 | 1: builtins |
| `%read` frees the entry | raises `Unimplemented: %unify to a released export entry` |
| `%answer_value` keeps the pending read | 502: `pending read has no reply entry` everywhere, bench tables |
| `%unify` keeps the import | 135: `import .. dangles` in every N>1 case, `release of a free entry`, tables, paths |
| delivery LIFO instead of FIFO | nothing: PASS. No case depends on the order within a pair; not caught |

Never fired: `the two schedules differ` (M1's no-wake injection is the
one that showed why both quotas are run), `messages in flight`,
`alias`'s two preconditions, and the refusal of `unbound/2` of an
external reference (since M5 not refused: thrown to the owner, or
`{X}` of an exported value; the `builtins` case checks both).

Not reached at M2, open:

- MRB-on paths are handled as white ones; WEC, black tables, the
  white-path forward of an ID, the exported variable retagged, and a
  collection with live tables: rung M3.
- The pkl1 samples and the primer's `sample9` with `@node` need the
  PIMOS compiler run from a prompt checkpoint; the oracles here are
  programs already compiled in the held image.
- `unbound/2` of an external reference (VPIM throws it to the owner).

**M3 reached on the reference model, 2026-11-26** (the retagging in a
second commit, below). `ref/pimm/pimm_pe.py` (the white and black tables, WEC,
`PECollector`) and `ref/pimm/m3_gc.py` (the check, in `run_tests.sh`
after `m2_read.py`). `pimm_gc.py` gained two empty hooks
(`more_roots`, `after_scan`), a class attribute for the tags that move
into a structure copied after them (`VAR_TAGS`), and `collect()` uses
the machine's own `Collector` if its class names one. One machine is
unchanged: the M1 list of traces is byte-identical (`lockstep_tproc`,
`lockstep_shoen3`, `lockstep_merge`, `lockstep_shoen`, the one-machine
`seqgc` and `gc`; the last two collect an empty heap, so they do not
test the copy), and a real one-machine collection, the one
`m2_read.py`'s loader makes (1,470 live cells of the loaded modules),
gives a byte-identical pickled machine before and after the change.

What is modelled, and from where:

- **White and black.** VPIM chooses by the path's MRB
  (`f_Put_StructureGroup_inLogicalPacket`, `f_Put_UnboundGroup_...`:
  `s_IfMRBoff` white, else black). White: a new entry per export,
  given back by exactly one `%unify` or `%release`, or by coming home.
  Black: one entry per exported address (VPIM
  `s_AllocBlackExpEntry_Sub`; TM-1044 9: the black export table hashed
  by the data's address), each ID sent with `WEC_UNIT` = 2^24 of WEC
  (`D_EXPORT_WEC_UNIT`), the entry's WEC the negative of what it gave
  out; the ID word has the tag's low bit on and an `INT` word of WEC
  follows it (VPIM's black layout, `f_Put_EX_inLogicalPacket_Sub`'s
  diagram; INFERENCE that PIMOS's `x` tags are the black IDs). One
  import per black ID, the WEC of a second arrival added to it (the
  black import table hashed by ID).
- **WEC comes back** with `%read` (half the importer's, rounded down:
  `s_GetExrefIdAndWecBImpRec_Sub` "WEC を半分にしている"), `%unify`
  (all), `%release {8, ID, WEC}` (all), and an ID coming home; the entry
  is reclaimed at 0 (TM-1044 `s9.tex` 432-453).
- **An imported ID passed on** (`f_Put_EX_inLogicalPacket_Sub`): white
  on a white path goes itself and the import is given up (the release
  export); white on a black path is exported again (an indirect
  export, a black entry of this PE); black on a white path with no
  read pending, to an ID imported only once, takes all its WEC and the
  import is given up (`s_GetExrefIdAllWecAndReclaimBImpRec_Sub`,
  `s_IfSingleImport`), else half; with less than 2 it is exported
  again. A black ID received a second time sets the import's flag,
  more than one reference (`s_SetMultiImportFlagBImpRec`). OURS: a
  `%read` always keeps the import and sends half the WEC (VPIM's
  `f_GetExrefIdAndWec_forRead_BEX` takes all of it on a white path to
  a single import), and a `%unify` always sends all of it and gives the
  import up, the cell becoming the value (VPIM keeps half on a black
  path). At M2 every ID going to a
  third PE was exported again: the M2 pins for `home` and `third` move
  (both now leave nothing; `third` on 4 PEs reads L from PE 0 directly,
  11 reads instead of 22), noted in `m2_read.py`.
- **A collection on a PE** (`PECollector`): the export table and the
  bench's words are roots (TR-466 3.2); an external cell is a one-word
  datum; the import table is weak: an import whose cell was not reached
  is released, all its WEC with it (OURS: when and how VPIM's
  collector releases imports was not read here). The PE's
  suspended-goal count is taken again from the copy.

The check runs the M2 heap monitors on the same five (N, c) and both
quotas with every PE collected at quiescence after the start and each
round, then twice more after the bench lets go of the stream: the
answers stay right, at every quiescence each black entry's WEC plus
its importers' is 0, every entry is named by an import (a white one by
one) or is a pending read's reply, the external cells in a heap match
the import table, a second collection releases nothing, and both
quotas give the same; the messages, what is held before the let-go
and what is left after, and the releases by round are pinned per
program and N (and in `m2_read.py` the monitors' messages and
leftovers too). Bench cases, each pinned: `drain` (the bench lets go of
`out/2`'s P: PE 0's collection releases its two imports, PE 1's then
finds out1's goal unreachable, every table empty; releases by round
0, 2, 0), `black` (reverse([], X, X) with X on a marked path: one
entry, two units, one import, released with both), `via` (a black ID
passed on with all its WEC to a third PE, which reads L from PE 0),
`share` (reverse(X, X)@node(N-2) by way of PE 1, X marked twice: PE 1
imports the ID once with the flag set, passes both references on with
half the WEC each and keeps its import; X = [] on PE 0, then every PE
collected: every table empty), and the two indirect exports as units.
Every M3 path marked in `pimm_pe.py` must run. `m3 gc: PASS (36 runs)`.

What the monitors leave: with the stream let go, every one-PE run
collects to nothing, and every N>1 run keeps the goals that wait on
each other across PEs, through the export tables (a per-PE collection with
the export table as a root cannot reclaim a cycle across PEs). The
monitors' own collections release nothing: their imports are live.
Only the bench cases release at a collection, so the monitors'
`fixpoint` check is vacuous; `drain`'s releases by round is the real
one.

Observed fault injections (each on a private copy of `pimm_pe.py`,
`m3_gc.py` and `m2_read.py` both run):

| Injection | Observed |
|---|---|
| a dead import dropped without `%release` | 56 FAIL lines in m3 (drain, black, share: WEC, named, releases, tables); m2 PASS |
| imports made roots of the collector | 25 in m3 (drain, black, share: releases, tables; the path list); m2 PASS |
| an import's cell not moved | raises `KeyError` |
| external cells not in `VAR_TAGS` | nothing: PASS. No external cell is ever inside a block copied after it (each is a one-cell block, referred to only by references): not caught, and by construction not reachable |
| the suspended goals not counted again | 16 in m3 (the monitors' pinned tables, drain's no goal left) |
| `%read` keeps its half of WEC | 6312 in m3 (WEC, named, more WEC returned than given, pins); 450 in m2 (more WEC returned, monitor pins) |
| `%read`'s WEC not added back | 4040 in m3 (WEC, named, pins); 34 in m2 (monitor and bench tables) |
| `%unify`'s WEC not added back | 848 in m3 (WEC, named, pins); 16 in m2 (monitor tables) |
| no black entry reused | raises `KeyError` (the reverse map) |
| a white ID passed on, its import kept | 8 in m3 (via: dangles, pin); 20 in m2 (home, third: dangles, tables) |
| a black ID passed on with all its WEC, its import kept | 8 in m3 (via: dangles, pin); m2 PASS |
| a white ID come home, its entry kept | 4 in m3 (via: named, pin); 6 in m2 (home, third: tables) |
| a black ID imported twice | raises `KeyError` |
| WEC not halved when passed on | raises `Unimplemented: %read to a released export entry` |
| the import flag ignored (all the WEC passed on by one of two references) | raises `KeyError` in `share`; m2 PASS |
| the cell left external after `%answer_value` | raises `KeyError` (both checks) |

Never fired: `cells`, `fixpoint`, `a white entry held twice`, `an
import with no WEC`, `a reply entry imported`, `the two schedules
differ`.

Not reached at M3, open:

- `EMHOK` (several goals' hook kinds) is not modelled; nor is when the
  machine untags a variable whose last entry is freed unbound (OURS:
  at once).
- The tables at fixed addresses: they are Python tables of the PE,
  not memory cells (OURS since M1).
- Cross-PE cycles are not collected: no global collection is
  modelled.
- `cells` and `fixpoint` never fired under an injection; the
  `VAR_TAGS` addition is defensive (above).
- The two OURS simplifications of `%read` and `%unify`'s WEC above.

**The retagging, 2026-11-26.** An exported variable's cell is retagged
while an entry holds it (TM-1044 `s9-msg-kl1data.tex` 269-300; PIMOS
`tagtbl.kl1` 2Ah-2Dh): `UNDF` becomes `EUNDF`, `HOOK` `EHOOK`; a goal
hooked on it keeps `EHOOK`; binding it wakes its goals as a `HOOK`'s
are; when its last entry is freed still unbound it is a plain variable
again (OURS). `pimm.py` gained `Machine.VAR_TAGS = (UNDF, HOOK)` in
place of the literal pair in `term`, `taken`, `new_module` and
`set_vector_element` (behaviour-preserving; `deref`, `bind` and `hook`
are overridden by the PE); `PECollector` treats `EUNDF` as a datum and
`EHOOK` as a hook word. One machine: the M1 trace list byte-identical
again, and `m2_read.py`'s loader collection gives the same pickled
machine. `m3_gc.py` checks at every quiescence that every exported
variable still unbound is retagged and every retagged cell is one an
entry holds. Injections: no retag, 678 FAIL lines in m3 (`exported
variable not retagged` in every monitor and bench case), m2 PASS; no
untag, 4 in m3 (`black`: a retagged cell no entry holds); an `EHOOK`
bound without waking its goals, 73 in m2 (the monitors' answers and
messages, `chain`, `alias`, paths), and m3 raises
`gc: the to-space is full`.

**M4 reached on the reference model, 2026-11-26.** `ref/pimm/pimm_pe.py`
(the shoen across PEs) and `ref/pimm/m4_shoen.py` (the check, in
`run_tests.sh` after `m3_gc.py`). `pimm.py` and `pimm_gc.py` are
unchanged, so one machine's traces are byte-identical by construction;
`m1_gc.py`, `m2_read.py` and `m3_gc.py` still pass (20, 52, 36 runs).

What is modelled, and from where:

- **The shoen ID** is a black export entry of the shoen record
  (`SHREC`) on its home PE, made at its first throw; its WEC is the
  negative of the WTC given out (VPIM's WTC, the weighted throw count,
  kept on the export entry: TM-1044 9; the entry kind OURS). While
  any WTC is out the shoen's goal count holds one more, so it cannot
  terminate until all of it is back; then `ended(sh, 0)` as on one PE.
- **A throw from a shoen** (`f_Send_IntClMsg_ThrowGoal_Sub`) carries the
  ID, `wtctu` = 0x400 of WTC (PARAM line 128; VPIM's
  `_WTC_THROW_GOAL_UNIT` agrees) and `rsctu` = 0x1000 of resource, or
  what is left (PARAM's `rsctu`/`rscsu` preferred to VPIM's 2^16/2^24:
  INFERENCE that the Pseudo PIM/m firmware used its own PARAM).
- **A foster parent** (VPIM `f_Get_FP_Ptr`, `f_InitFPSlots`; the manual,
  `e-shoen.tex`:304, "a new shoen is created on the goal's destination
  node") is made on the goal's PE at the first goal of a shoen there: a
  record of the shoen layout, parent 0 (the top of that PE's chain),
  mask 0 (an exception goes to the shoen), report `INT 0`. It sends
  `%ready {1, ID, WTC, PE}`; the shoen answers `%supply_wtc` (`wtcsu`
  = 0x1000000), sending `%stop` or `%abort` first if it is stopped or
  ended (VPIM `f_ShoenReceiveReady`). It throws on with its own WTC.
  With less than 0x403 the goal waits, counted as a child, and
  `%request_wtc` is sent once (`f_ThrowGoalMsgSusp`); `%supply_wtc`
  sends the waiting goals. When its resource is out it asks
  `%request_resource` once (`f_FPRequestResource_Sub`). The shoen
  supplies `rscsu` = 0x10000 while it has that much not out, and
  otherwise reports `resource_low` (if allowed). The foster parent
  forwards an exception as `%exception {10, ID, WTC, tag,
  number, Info, NewCode, NewArgv}` (`f_Send_IntClMsg_Exception`), the
  shoen reporting it on its own stream; Info's Pe is the foster
  parent's PE. It answers `%ask_statistics` with `%answer_statistics`
  (its consumption since the last report). It ends when its count is
  0, with `%terminated {2, ID, PE, WTC, resource left, used}`
  (`f_FPTerminateWithUnlockFP_Sub`), all its WTC with it.
- **Control.** The shoen's `started`, `stopped` and `aborted` (the
  one-PE report points) are also sent as `%start`, `%stop` and `%abort`
  to every live foster parent (`f_Send_IntClMsg_ToAllFPs`). Each gets
  one WTC unit newly given (OURS: VPIM's control WTC is not read).
  Statistics asks every live foster parent and reports when all have
  answered. A message to a PE with no foster parent of the ID gives
  its WTC back (`%return_wtc`; resource `%return_resource`; statistics
  0).
- **Accounting.** Resource reported back (`%answer_statistics`,
  `%terminated`) is charged to the shoen and those above it, half of it
  its reductions (2 a reduction, `e-shoen.tex`:42), as a local goal's
  is. Resource out at the foster parents is not available to supply.
- **OURS**:
  - Abort at home ends the shoen at once, as on one PE. Late WTC only
    frees the entry, and a woken goal of an ended foster parent is
    discarded.
  - The home and each foster parent are separate records, not VPIM's
    one `FPREC` layout.
  - The tables are Python tables of the PE (as since M1).
- **Code across PEs** (2026-11-26, with M5): a code or module word in
  the heap goes as `{CODE_ID or MODULE_ID, module number << 24 |
  offset}`, the number its place in the loaded order. The receiver
  takes its own copy of that module. VPIM sends a module's external
  reference and an offset (§1.3), and PIM/m fetches the module by its
  global identifier (`M92` pp. 430-431). Every PE has the loaded
  modules, so for them the fetch is a lookup (OURS). A module made
  after the split (one the compiler loads at the prompt) is numbered
  by its PE at its first send. A PE without it copies it from that
  PE at once, without messages (OURS), with what its cells point at
  outside it: strings, vectors and lists, sharing kept, and the cells
  of its calls to other modules (a call cell still unbound is a fresh
  variable, linked where it is called). The modules a PE has are a
  root of its collector (`PE.mods`, moved by it: PIMOS's module table
  is one, and VPIM's `f_GCPreProcedure_Sub` keeps the code area), so
  the M1-M3 refusals of a goal or code word after a collection are
  gone.

The check, `m4_shoen.py`, has seven parts on M1's machine
(`pimm_shell360E.sav`). Each is started by the image's own
`shoen:execute/4`, with `prof`'s `apply_goals/1` placing
`{Code, ArgV, Node}` goals (`apply_with_pgm@node`). They run on
(N, c) = (1,0), (2,0), (2,1), (4,0), (4,3), under quota 1 and quota
1,000,000:

- `spread`: `seqgc:go/0` at node k, so the foster parent throws on.
- `home`: `gc:go/0` at c.
- `stop`: `ipl_pool:hash/3` waits on a home variable at k, with
  `ipl:dummy/2` after it. Statistics are asked while it waits, then
  stop, the variable is bound, then start.
- `abort`: the same with abort.
- `exception`: `ipl:close_fep(shut, 0)` at k, a reduction failure. The
  bench answers NewCode `ipl:dummy/2`.
- `nested`: a shoen made inside a foster parent, read at the home by
  the image's `top:bios_monitor/3`.
- `resource`: a shoen funded with 16. It is low and not terminated,
  then it is funded.
- `collected`: every PE collects before anything runs, so the loaded
  modules move and live only as the collector's roots; then `home`'s
  `gc:go/0`. The bench keeps its code by module number.

What is checked:

- `terminated` comes once and in order.
- Statistics = 2 x the shoen goals' reductions, counted on every PE as
  they end, and `return_resource` = what was added less that.
- The answers: H is bound only after start; the exception's kind and
  Pe.
- After every run, WTC and resource are accounted for.
- At the end there is no foster parent or shoen table, one
  `%terminated` per `%ready`, and nothing left on any PE (after a
  drain for abort and exception).
- Both quotas give the same Reports (numbers aside) and the same
  answers.
- Every M4 path marked in `pimm_pe.py` runs.

`m4 shoen: PASS (80 runs)`, about 5 minutes on a shared machine
with `M4_CACHE`; loading the sav takes about another 90 s without it.
Messages at N=4, c=0, quota 1:

| Part | Messages |
|---|---|
| `spread` | ready 3, supply_wtc 3, throw 4, unify 3, terminated 3, return_wtc 2, request_resource 1, supply_resource 1 |
| `stop` | ready 1, throw 2, read 3, answer 3, release 3, stop 1, start 1, ask_statistics 1, answer_statistics 1, terminated 1 |
| `exception` | exception 1 |

Reductions are printed, not pinned: the schedule moves them, as at M1.

Observed fault injections (each on a private copy of `pimm_pe.py`, the
whole `m4_shoen.py` run; a raise inside one run is that run's FAIL
line):

| Injection | Observed |
|---|---|
| no extra count while WTC is out (the shoen may terminate with goals elsewhere) | 104 FAIL lines: `spread` and `resource` (shoen tables and goals left, one `%terminated` per `%ready`, low but not terminated), `abort`'s order, `exception` (the report, the two schedules differ, `KeyError: 0`), `nested` (the inner shoen, the monitor, PEs left); `stop` raises `start_shoen of a shoen that is not dormant or stopped` |
| `%terminated` gives back no WTC | 416: every part with N>1 (WTC not accounted for, tables and goals left, never terminated) |
| stopped not sent to the foster parents | 8: each N>1 `stop` run raises `start_shoen of a shoen that is not dormant or stopped` (the foster parent ran on and is sent start): caught by the model's refusal, not a check |
| the consumption in `%terminated` not charged | 112: statistics and `return_resource` in `spread`, `home`, `stop`, `exception`, `nested`, `resource`, `collected` |
| a goal to an existing foster parent loses its WTC | 160: `stop` and `abort` (WTC, tables, goals left, terminated) |
| a foster parent never asks for resource | 104: `spread` and `resource` (low but not terminated, one `%terminated` per `%ready`, tables, goals left) |
| M1's `current_node` gives node 0, re-run in `m1_gc.py` with the module roots and code by module number | 18 FAIL lines (request order, throw order, node c asks after every `%unify`, messages): caught by the checks, where at M1 it raised `KeyError` |
| the loaded modules not roots | `collected`: each of its 10 runs raises `KeyError` (the code the bench and the thrown goals name is gone); before that part was added, `m1_gc.py` and `m4_shoen.py` passed |

Never run: `ready while stopped`, `ready while aborted` (a first goal
reaching a PE after the shoen was stopped or ended), `aborted foster
parent drops a waiting throw`.

Not reached at M4, open:

- The exceptions for a bad node number (`illegal_input`,
  `range_overflow`, `e-shoen.tex` 486-514): still refused.
- A shoen's node range and relative node numbers (`e-shoen.tex`:428):
  node numbers are absolute.
- VPIM's control WTC and its abort, which waits for the foster
  parents, are not read (OURS above).

**M5 reached on the reference model, 2026-11-26** (the boot and two
programs from the prompt; the shell's `cn`, `gc`, `seqgc` and `set
node` are not yet run). `ref/pimm/m5_boot.py` is a long runner, NOT in
`run_tests.sh`. It needs the link checkpoint that `longrun_ipl.py
--reference --save` writes (1.1 GB on disk, 14 GB loaded, not in git),
and a full run is about 7 minutes.

What it does:

1. **Slim.** The checkpoint is collected once on its one machine with
   Loaded (load/4's answer: atoms, the 480 modules, comments, entry
   code) a root. The IPL's file data dies and the modules live: from
   73,594,186 heap cells to 1,016,836, a 17 MB pickle (`M5_CACHE`).
   Two checks show the collection is sound. `longrun_ipl.py --load
   SLIM --go --fep` is the same run as from the checkpoint: 8,595,408
   instructions, the same console and FEP conversation, 1,218 goals
   waiting. A `System(1)` of the slim machine gives the same numbers.
2. **The boot on N PEs.** Every PE is a copy. `top:go_pimos1(Loaded,
   BootInfo)` and `ipl:make_boot_info(BootInfo)` are made on PE 0, the
   boot PE (the console's `$GO/PIMos` "throws a boot goal to the boot
   PE", §1.1; that it is PE 0 is OURS). The FEP device is on PE 0, the
   cluster BootInfo names. When the System is quiet, the steps are
   longrun_ipl's: the FEP's waiting commands, then every armed alarm
   (each PE has its own clock: OURS), then the FEP's next scripted
   event.
   The boot goal is made on PE 0 directly, not sent there as a
   `%throw` from the FEP as the console's `$GO/PIMos` does (OURS).
3. **Two programs typed at the prompt**, each in a boot of its own
   (`compile`, `!package work`, the file, `!exit`, `listener`,
   `default_package(work).`, the goal):
   - `sample9`: the primer's `sample9` (`primer25.tex`:1138-1155, as
     printed), `sample9:distribute(8).`
   - `qsort`: R8's `qsort_r8.kl1` with its second recursive call
     placed by its pivot, `qsort(L2, R1, R0)@node(X mod Nodes)` (OURS,
     the least change that spreads the work).

Results on N = 1, 2, 4 under quota 1 and quota 1,000,000:
`m5 boot: PASS (12 runs)`.

- The console and the whole window text equal the N=1 run's. `qsort`
  answers ` R =[2,17,18,27,33,46,65,74,83,94]` on every N, which is
  also the R8 pin.
- `sample9`'s `job_ext` goals go to nodes 0,1,2,3,0,1,2,3 on 4 PEs,
  the primer's printed order, and to 0,1,0,1,... on 2.
- No anomaly. Every run ends with nothing left to run.
- To the prompt: `longrun_ipl.go` on the slim machine and `System(1)`
  give the same instructions (8,595,408), stop, console and FEP
  messages.
- The prompt alone on each N is the baseline for what is left. On 2
  PEs the boot leaves 2 shoens on PE 0 with goals on PE 1 and 2
  foster parents there (on 4 PEs the same on each other PE: PIMOS's
  own per-node goals). After each app the same tables are left, so
  the app's shoens and foster parents are gone. At every end every
  shoen's WTC, resource and foster parents are accounted for
  (`pimm_pe.shoen_accounting`, `m4_shoen.py`'s invariants).
- Goals waiting at the end (1 PE / each other PE): 1,605 / 14. These
  are the boot's and the Listener's own waiting goals, printed, not
  pinned.
- Messages, N=4, quota 1,000,000:

  | Program | Messages |
  |---|---|
  | `sample9` | throw 15, ready 9, terminated 3, read 15, answer 3, release 3, unify 3, supply_wtc 9, return_wtc 3 |
  | `qsort` | throw 23, ready 15, terminated 9, read 40, answer 28, release 28, unify 19, request_resource 3 |

  PIMOS's boot itself places goals on every node, so these counts
  include the boot's.
- Instructions, N=4, quota 1,000,000: PE 0 10,182,092 and 459 on each
  other PE (`sample9`); 10,537,685, 584, 653, 702 (`qsort`).
- The other PEs never call `new_atom` (each PE's counter is printed;
  only PE 0's moves), so a per-PE atom counter is not yet tested.

What M5 needed in `pimm_pe.py`:

- The module fetch (M4 above): `sample9` is compiled on PE 0 after the
  split, and its `job_ext` code goes to the other PEs by its number.
- `unbound/2` of an external reference, which the Listener's printer
  calls on the answer's cells:
  - of an exported value (`EXVAL`, never a variable) it gives `{X}`
    at once (OURS from the tag's meaning);
  - of an exported variable the goal `unbound(X, Result)` (the
    built-in's own stub) is thrown to X's owner, as VPIM's
    `kblt_b_unbound` does, and Result comes back by `%unify`.

Observed fault injections (each on a private copy of `pimm_pe.py`,
`m5_boot.py` run):

| Injection | Observed |
|---|---|
| no module fetch (the code word taken as the sender's address) | 12 FAIL lines: every N>1 run of both programs raises `KeyError` (the module is not in that PE's memory), so its window and stop differ from N=1 |
| `unbound/2` of an external variable answered here as unbound | 1 FAIL line, `qsort` N=2: the window shows ` R =[2,17,18\|B]` |
| `unbound/2` of an exported value sent to the owner too | nothing: PASS. The owner's answer is the same, so both paths are right |
| every `Goal@node` made local | 1 FAIL line: `sample9` N=4 placement order all 0. `qsort`'s answer is the same, as KL1 says it must be |
| `current_node` gives node 0 on every PE | nothing: PASS. Only PE 0 calls it in these programs |

Not reached at M5, open:

- The shell's `cn`, `gc`, `seqgc` and `set node` from the prompt, with
  `cn.kl1`'s printout as the oracle.
- MGTP (R9) with `@node`; the other R8 samples.
- The fetch is a copy made at once, with no messages; PIM/m's code
  fetch messages are not modelled.
- Each PE's own `new_atom` counter (OURS) would collide if two PEs
  made atoms. It is untested, since only PE 0 makes them.
- The boot PE as PE 0 and the FEP on it are OURS. The real system's
  IPL loads pimos.ipl over the network, which is not modelled: the
  link checkpoint is made on one machine and copied.
- The run takes minutes and the checkpoint is not in git, so it is
  not in the suite.
