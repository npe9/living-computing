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
  one.
- **Rungs M1..M7** are in §4. M1: N separate machines,
  `current_node`, `Goal@node(K)` as a `%throw_goal`, and the `%unify`
  that binds an exported variable, checked by PIMOS's own compiled
  `seqgc` and `gc` modules from `pimm_shell360E.sav` on 1, 2 and 4 PEs
  under two schedules. Its status is in §5.

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
  for one engine and no node count; MGTP-N's manual (IFS No. 91) was
  not read for figures.

## 2. Oracles for the multi-PE rungs

| Oracle | What it fixes | Label |
|---|---|---|
| `seqgc:go/0` from `pimm_shell360E.sav` | on N nodes run from node c: N collections, one per node, in the order 0, 1, .., N-1 without c, then c (each round's `%unify` comes after its collection, `proceedGcCall/1`); N-1 throws, N-1 `%unify` | HELD-SOURCE, its dataflow |
| `gc:go/0` from the same file | N collections, one per node; c's after every other node's `%unify`; N-1 throws, N-1 `%unify` | HELD-SOURCE |
| KL1's semantics | placement does not change an answer: every multi-PE run's results equal the one-PE run's and KLIC 2.002's | the language |
| The primer's `sample9` | the placement order 0,1,2,3,0,1,2,3 for `distribute(8)` on 4 nodes | PRINTED |
| The manual's exception rules | an atom node is `illegal_input`, an out-of-range one `range_overflow` | PRINTED |
| MGTP-N (IFS No. 91), STB/MLB, Distributed Pool | larger programs written for several nodes | HELD-SOURCE; answers as KLIC's or the papers' |

## 3. Choices that are ours

- **Separate memories.** Each PE is its own `pimm.Machine`, heap and
  registers its own (PIM/m: one memory per PE, `M92`).
- **The same code on every PE.** The modules are loaded once and the
  loaded machine copied to every PE, so a code address means the same
  on each and a thrown goal carries it as `{COD, address}`. OURS
  scaffolding: PIM/m sends the module's global identifier and fetches
  the module on demand (`M92` pp. 430-431); that is a later rung.
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
- **Node numbers are absolute** for goals of the root (no shoen); the
  relative numbering of a shoen's node range (`e-shoen.tex`:428) waits
  for the shoen rung.

## 4. The rungs

| Rung | Observable | Oracle | Needs |
|---|---|---|---|
| M1 | N PEs; `current_node` gives (k, N) on PE k; `Goal@node(K)` with K another PE sends `%throw_goal` and the goal runs on K; an unbound argument is exported and the importer's body unification of it with an atomic value sends `%unify` home, which binds it and wakes its waiters | `seqgc:go/0` and `gc:go/0` (§2) on 1, 2, 4 PEs, under two schedules | the reference model only |
| M2 | Reading an external reference: a guard or `wait` on an imported cell sends `%read`, the goal waits on an `RHOOK`, `%answer_value` brings a level-1 copy; structures exported at level 0 (a list one cons at a time); a reference coming home resolves to the local cell | KL1 programs whose answer must not depend on placement: the pkl1 samples of R8 with `@node` added (OURS), KLIC 2.002 as the answer; the primer's `sample9` | M1 |
| M3 | The tables as the machine had them: white and black by MRB with WEC (TR-390 §7, unit 2^24), `%release`, the exported variable retagged `EUNDF`/`EHOOK` (TM-1044), the tables at fixed addresses and as roots of the collector | an injected leak or double release failing a check; a collection with live exports | M2 |
| M4 | The shoen across PEs: foster parents (`FPREC`), WTC (`wtctu`, `wtcsu`), `%terminated`, `%ready`, resource messages, exceptions for a bad node number | the manual's `range_overflow`/`illegal_input`; a shoen spread over nodes terminating once | M3 |
| M5 | PIMOS boots on N PEs (its 113 `@node` sites), and the shell's `cn`, `gc`, `seqgc`, `set node` run | `cn.kl1`'s printout; §2's collection counts through the shell | M4; code fetch by module identifier |
| M6 | A period multi-node program: MGTP-N, STB/MLB, Distributed Pool | its answer (KLIC's, the manual's) | M5 |
| M7 | The Bluespec core: N cores on `PimMesh.bsv`, or one core whose network port is answered from a recorded tape (as `lockstep_scsi.py` answers the SCSI port), in lockstep with the reference | the reference's per-PE traces | M1 on the reference (the tape) |

**Why M1 is not on the core in this step.** The core is one PE. In
lockstep it would need a network port: the messages a PE receives come
from other PEs, so on a single core they must be a tape recorded from
the reference (the bench's device tape is the pattern), and the
instructions that send (`enqueue_goal_to_processor` to another node,
a unification of an `EXREF`) need a new port and box on the core. That
is the shape of M7, not a small change inside this rung.

## 5. Status

*(Filled in as rungs are reached.)*
