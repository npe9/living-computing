# WP5.1 evidence: interrupts, faults, and the PIMOS interface

Scope: the documented evidence for Stage 4 of `plan.md` (WP5.1), plus a
single-PE diagnostic plan that uses only documented behaviour. Citations are
to printed page numbers where the source has them; otherwise to the archive
path and section/file. "Confirmed" means the cited text states it;
"unknown" means the corpus does not state it. Every model-side claim cites
the repository file and line, because the model's interfaces are model-defined.

Sources used:

| Key | Document / archive |
|---|---|
| `M92` | H. Nakashima et al., "Architecture and Implementation of PIM/m", FGCS '92 vol. 1, printed pp. 425-435 |
| `TR389` | T. Shinogi et al., "Macro-call Instruction for the Efficient KL1 Implementation on PIM", ICOT TR-389, June 1988 |
| `MAN` | PIMOS manual, `pimosman.tar.Z`, decompressed `Eman/*.tex` (title page dated 1991-10) |
| `SRC` | PIMOS source, `pimos.tar.Z`, decompressed `pimos/src/` and `pimos/protocol/` |
| `MODEL` | `pim/bsv/*.bsv` (the Bluespec model in this repository) |

The manual's own title page is `Eman/e-top.tex`: "PIMOS manual", date line
1991-10. `Eman/e-cover.tex` is not present (only `e-cover1.tex`). The PIMOS
source identifies itself separately in `SRC/bios/boot/bios.kl1`:
`version = "V3.0"`, `date = "13-Apr-92"`. The manual and the source are not
the same build; do not cite the source date as the manual's date.

## 1. Documented interrupt sources

Two different things are called "interrupt" in this corpus: a hardware
signal into the PE, and the PIMOS message-level interruption of a device or
task. They are documented at different layers and must not be merged.

### 1.1 Hardware-level interrupts

| Source | Citation | Status |
|---|---|---|
| NU read-buffer tail interrupt: "The read buffer holds a whole packet and raises an interrupt when the packet tail arrives." | `M92` p. 427; quoted in `docs/pim_architecture.md` §1 and in `bsv/PimNU.bsv` header | Confirmed as a documented NU behaviour. The packet header/trailer layout and the interrupt's destination are not stated. |
| Interrupt request register in the PE's dedicated registers; hardware flags "such as the ALU condition code or an interrupt flag are readable as the tag of dedicated registers and can therefore be macro-call conditions" | `TR389` p. 9 (register list) and p. 7 (flags as macro-call conditions); quoted in `docs/kl1_architecture.md` §4 | Confirmed that the register and flag exist. The bit position, the set of interrupt sources wired to it, and the acknowledge/clear protocol are not stated. |
| Timer interrupt delivered as a message (`wake_up`) | `MAN` `Eman/e-ioctrl.tex` §Timers, printed pp. 368-370: `on_at`/`on_after` instantiate `wake_up`; "Timer devices implemented by the system timer can be acquired on machines that have system clocks built-in, such as PIM and Multi-PSI" | Confirmed as a documented PIMOS timer mechanism. It is a message to a timer device, not a PE interrupt line; the manual does not say how the system timer reaches the PE. |
| User attention key (`^C`) on a window device | `MAN` `Eman/e-ioctrl.tex` §Device abort/attention processing, printed pp. 355-356; `Eman/e-listener.tex` §Interruption of Execution (label `listener:attention`) | Confirmed as a documented user interrupt. "currently only window device is available" (`e-ioctrl.tex`, p. 356). |
| SCSI interrupt vector | `SRC` `src/bios/scsi/scsi_blt.kl1:20` `scsi_init(SCSI_Obj,TargetInterruptVector,Info)`; `src/macro/pimos/scsi.vmac` maps `scsi#scsi_init` | Confirmed only that a target interrupt vector argument exists. The vector layout, the interrupt sources, and the handler entry are not documented in the corpus. |

Not documented: a PE interrupt vector table, interrupt priority, interrupt
mask/acknowledge sequence, or a mapping from the NU/timer/SCSI signals to a
PE interrupt number. `M92` pp. 425-435 describe the NU and PE but print no
interrupt architecture. `TR389` p. 9 names an interrupt request register but
gives no bit assignment. This is a gap, not a confirmed absence.

### 1.2 PIMOS message-level interruption

The PIMOS manual defines interruption as a message/stream mechanism, not as a
PE interrupt:

| Source | Citation | Status |
|---|---|---|
| Abort line: "used to receive abort requests from PIMOS" | `MAN` `Eman/e-ioctrl.tex` §I/O Control, printed p. 355; §Device abort/attention processing, p. 356 | Confirmed. Implemented as a variable instantiated to the atom `abort` (p. 356). |
| Attention line: "used to inform PIMOS of interrupt from the user" | same | Confirmed. Instantiated to the atom `attention` on `^C` or `c+l-c`; "currently only window device is available" (p. 356). |
| Task interruption by the user | `MAN` `Eman/e-listener.tex` §Interruption of Execution, label `listener:attention`; `Eman/e-task.tex` "Messages to the task control stream" (`stop`, `abort`) | Confirmed. The listener interrupts a task's execution and offers resume/cancel; the task control stream has `stop` and `abort`. |
| SCSI "TargetInterruptVector" | `SRC` `src/bios/scsi/scsi_blt.kl1:20` | Source-inferred only; no manual section documents it. |

The model's equivalent signal is `PimNU.packetTail()` (`bsv/PimNU.bsv:60`,
implemented at line 115 as `tailPulse._read()`), asserted when a packet byte
with bit 8 set moves to an output port (`PimNU.bsv` move rule). The model
exposes it as a standalone signal; it is not an input to `PimPU`
(`bsv/PimPU.bsv:32-39` lists only `start`, `halted`, `error`, `readReg`,
`readMem`, `pc`). `PimNUTb.bsv:63` watches it. So the documented NU tail
interrupt is modelled as a pulse and tested in isolation; it is not wired to
the PE. That is a model gap, not a documented PIM/m claim.

## 2. Fault and trap sources and the documented response

### 2.1 Hardware/model faults

| Source | Documented response | Citation | Status |
|---|---|---|---|
| Undefined opcode reaching the execute stage | Model sets `error()`; the PE stops (`running` is cleared by the fault rule) | `MODEL` `bsv/PimE.bsv:185-187` (`errorReq` is "an undefined opcode reached E"), `bsv/PimPU.bsv:196-197` (`rule fault (running && !errorR && (estage.errorReq() \|\| regs.badWrite()))`) | Model-defined; not a historical PIM/m claim. |
| Illegal register write (`regs.badWrite()`) | Same `error()` latch | `bsv/PimPU.bsv:196`; `badWrite` is defined in `bsv/PimStages.bsv:65` (interface) and `:116` (implementation), "a microinstruction named an unwritable register" | Model-defined. |
| `halt` instruction | `halted()` latches; PC stops advancing | `bsv/PimPU.bsv:192-194`; `docs/isa.md` opcode `0x01` | Model-defined; the ISA table is generated from `asm/pimasm.py`. |
| PIM/m hardware fault/exception (parity, ECC, bus error, illegal address) | "not documented" | `M92` pp. 425-435; `TR659` pp. 1-9; `docs/pim_architecture.md` "Not stated" § | Unknown. The corpus prints no PE fault vector, no ECC/parity report path, and no machine-check response. |

`docs/pim_architecture.md` §"Not stated" (lines 400-420) lists the
architecture gaps; it does not list a fault/trap mechanism, because the
sources do not give one. The model's `error()` is therefore the only
fault response the repository can currently exercise.

### 2.2 KL1/PIMOS exceptions (software faults)

The manual documents exceptions as a KL1/Shoen mechanism, and the source
enumerates the firmware exception kinds:

| Source | Documented response | Citation | Status |
|---|---|---|---|
| Shoen exception management: "Manages the exceptions taking place during shoen execution. Failed execution (such as absence of the candidate for the goal, and failed unification) is also treated as exception." | Exception is reported to the innermost parent shoen whose mask matches the tag; the goal that caused it is replaced by the goal given by the exception manager | `MAN` `Eman/e-shoen.tex` §Shoen Function, printed p. 290 (label `shoen`); exception report protocol at label `shoen-report-protocol` | Confirmed. |
| `shoen:raise/3` | Creates an exception with a tag and data | `MAN` `Eman/e-shoen.tex` printed p. 300-301 (label `shoen:raise`) | Confirmed. |
| Exception kinds and their data | `illegal_input`, `range_overflow`, `out_of_bounds`, `integer_overflow`, `integer_zero_divide`, `invalid_floating_point`, `arity_error`, `undefined_module`, `illegal_merger_input`, `reduction_failure`, `unification_failure`, `deadlock`, `merger_deadlock`, `trace`, `spy`, `raised`, etc. | `MAN` `Eman/e-shoen.tex` printed pp. 297-299 (label `language-defined-exceptions`) | Confirmed as a manual list. |
| Exception translation table (firmware format) | Maps each exception kind to a message/term; lists `illegal_input`, `range_overflow`, `out_of_bounds`, `integer_overflow`, `integer_zero_divide`, `invalid_floating_point`, `arity_error`, `undefined_module`, `illegal_merger_input`, `reduction_failure`, `unification_failure`, `deadlock`, `merger_deadlock`, `trace`, `spy`, `raised` | `SRC` `src/kernel/builtin/excpt_tbl.kl1:1-80` | Source-inferred (firmware format), consistent with the manual's list. |
| Standard error reporting | `shoen:raise(pimos_tag#error, '$PIMOS$'(Error,Info), Data)`; the shell/listener formats it | `MAN` `Eman/e-error.tex` §Standardly Supplied Error Reporting (label `error`) | Confirmed. |
| Task abort/exception report | `abort` message; report stream `aborted`, `terminated`, `exception(Node, ExcCode, ExcArgV, NewCode, NewArgV)` | `MAN` `Eman/e-task.tex` §Messages to the task control stream and §Messages from the task report stream | Confirmed. |

What is **not** documented: a KL1-B or PIM/m hardware trap instruction that
maps a machine fault to a KL1 exception. The exception table is a firmware
translator for report messages; it does not state how a hardware fault
reaches it. The corpus also does not give the exception tag bit assignment
(`e-shoen.tex` points to Table `language-defined-exception` for the bit
layout, but the table itself is not in the acquired `.tex` files — the
`\begin{table}` block is absent). Treat the tag numbering as unknown.

## 3. The PIMOS interface

### 3.1 Manual-documented sections

The manual is `pimosman.tar.Z`, decompressed to `Eman/*.tex`. The chapters
that define the user/system interface are:

| Manual file | Section / label | Printed page(s) | Interface it defines |
|---|---|---|---|
| `e-kl1.tex` | KL1 Language Specification (label `kl1`) | 221 | KL1 as the hardware/software interface; includes `e-modeexp`, `e-syntax`, `e-builtin`, `e-shoen` |
| `e-builtin.tex` | KL1 built-in predicates | 264-289 | Built-in predicate set and their exceptions |
| `e-shoen.tex` | Shoen Function (label `shoen`) | 290-302 | Execution control, resource management, exception management, `shoen:raise`, report stream |
| `e-io.tex` | I/O Management (label `io`) | 332-333 | I/O device model |
| `e-ioctrl.tex` | I/O Control (label `io-control`) | 355-374 | Message formats, abort/attention lines, device hierarchy, timers |
| `e-ioutls.tex` | I/O utilities | 339 | Timer/stream utilities |
| `e-ioutltim.tex` | Timer utilities (label `timer-utility`) | 350 | Time-unit conversion |
| `e-task.tex` | Tasks (label `task`) | no PAGE marker; section in `e-rsc.tex` | Task control/report streams, `stop`, `abort`, `exception` |
| `e-rsc.tex` | Resource Management and Execution Management (label `resource-exec`) | no PAGE marker | Resource/task management |
| `e-proginfo.tex` | Program Management (label `program`) | no PAGE marker | Atom/module tables |
| `e-protocol.tex` | Protocol Definitions (label `protocol`) | no PAGE marker | Protocol definition language and system protocols |
| `e-error.tex` | Standardly Supplied Error Reporting (label `error`) | no PAGE marker | Error message format |
| `e-listener.tex` | Listener (label `listener`) | no PAGE marker | Interactive task control, interruption |
| `e-network.tex` | Setting of Network Environment (label `network`) | no PAGE marker | Network login |
| `e-inspecto.tex` | Inspector | no PAGE marker | Output interruption |
| `e-compiler.tex` | Compiler | no PAGE marker | Compilation interface |

The `e-*.tex` files without PAGE markers are included in the same manual but
the acquired archive does not carry the page comments; cite the file and
label, not a page number. `e-top.tex` shows the chapter order: KL1 (2), I/O
management (3), program management (4), resource/execution (5), then the
appendices. The `\input` order in `e-kl1.tex` is `e-modeexp`, `e-syntax`,
`e-builtin`, `e-shoen`.

### 3.2 Source modules that define the interface

| Source path | Role | Status |
|---|---|---|
| `protocol/resource.prt` | Protocol definition language source: general request, window/file/timer request filters (`genreq_filter`, `winreq_filter`, `filereq_filter`, `timerreq_filter`) | Source; the manual's `e-protocol.tex` documents the language. |
| `protocol/scsi.prt` | SCSI request/processor/sequential filters; `scsi_descriptor`, `scsi_common_protocol` | Source only. |
| `protocol/profiler.prt` | Profiling request/stream filters | Source only. |
| `protocol/pipeRfil.prt` | Pipe request/stream filters | Source only. |
| `src/kernel/task/int_hdl.kl1` | General-request handler: `execute`, `status`, `abort`, `set_gids`; `handler/6` and `get_relative_node/2` | Source; the manual's `e-task.tex` and `e-rsc.tex` describe the messages. |
| `src/kernel/task/task_hdl.kl1` | Task handler (`handler/10`, `handler/11`, `ohandler/5`) | Source; manual describes task streams. |
| `src/kernel/task/raisehdl.kl1` | Exception/raise handling | Source; manual describes `shoen:raise`. |
| `src/kernel/task/status.kl1`, `monitor.kl1`, `resources.kl1`, `copy.kl1`, `genRfil.kl1`, `genRhdl.kl1`, `genRtrn.kl1` | Task status, monitoring, resource, copy/rename helpers | Source only. |
| `src/kernel/builtin/excpt_tbl.kl1` | Exception translation table (firmware format) | Source; manual lists the exception kinds but not the translation table. |
| `src/kernel/builtin/shoen.kl1` | Shoen implementation | Source; manual documents the interface. |
| `src/bios/boot/bios.kl1` | `:- module pim.` `go/4` — the boot entry; `go(CSPParam,Atoms,Modules,Comments)`; `scsi_manager:create`, `initiate_device`, `predicate_to_code(module#init,go,0,PIMOS_TOP)` | Source only; the manual does not document the boot entry. |
| `src/bios/boot/fep.kl1`, `scsi_man.kl1`, `scsi_conf.kl1`, `timer.kl1`, `sysTdvc.kl1`, `sysTman.kl1`, `syslog.kl1`, `console.kl1`, `jtoa.kl1`, `mpsi.kl1` | BIOS device managers and console | Source only. |
| `src/vm/vm.kl1` | `:- module vm.` `go/0` calls `pim:go(CSPParam,Atoms,Modules,Comments)`; builds module/atom tables and boot info | Source only. |
| `src/bios/fep_module/*.kl1` | FEP device drivers (dir, file, fep, scsi, soc, strio, time, win) | Source only. |
| `src/bios/scsi/scsi_blt.kl1` | SCSI init with `TargetInterruptVector` | Source only. |

The manual documents the *message* interface (streams, protocols, message
names, result formats); the source documents the *implementation* (filters,
handlers, boot sequence). The manual does not document the boot entry or the
protocol `.prt` filters; the source does not document the message semantics.
Both are needed, and the split is explicit above.

### 3.3 What the "PIMOS interface" is, in one paragraph

PIMOS is written in KL1 and runs on PIM/m (`SRC/README` §1; `MAN`
`e-kl1.tex` p. 221). The user interface is a set of KL1 message streams:
the general request device, request devices (window/file/timer/string), task
control and report streams, and the Shoen control/report streams (`MAN`
`e-ioctrl.tex` p. 355; `e-task.tex`; `e-shoen.tex` p. 290). The PE interface
is the KL1 abstract machine plus the microprogrammed KL1-B instruction set
(`M92` p. 426; `TR389` p. 3), and the boot entry is `pim:go/4`
(`SRC/bios/boot/bios.kl1`), called by `vm:go/0` (`SRC/vm/vm.kl1`). The manual
does not document the PE register map or the boot entry; the model's
`PimPU` interface is therefore model-defined, not historical.

## 4. Single-PE diagnostic proposal

The goal is to exercise only behaviour the sources document or the model
explicitly labels as model-defined. The model's diagnostic surface is the
`PimPU` interface (`bsv/PimPU.bsv:32-39`) and, for the NU tail signal,
`PimNU.packetTail()` (`bsv/PimNU.bsv:60`). No interrupt input exists on
`PimPU`, so the diagnostic cannot drive a PE interrupt; it can drive the
documented NU tail signal and the model's fault paths.

### 4.1 What to drive

| Drive | Mechanism | Documented basis |
|---|---|---|
| Start the PE | `pu.start()` | Model interface; `PimSmoke.bsv` uses it |
| Execute to `halt` | Load a program ending in `halt` (`docs/isa.md` opcode `0x01`) | ISA table; `PimPU.bsv:192` |
| Undefined opcode | Load a word whose opcode is not in `docs/isa.md` | `PimE.bsv:184-186` labels it "an undefined opcode reached the model" |
| Illegal register write | Use a model-defined write check (`regs.badWrite()`) | `PimPU.bsv:196` |
| NU packet tail | Put a packet byte with bit 8 set; read `packetTail()` | `M92` p. 427; `PimNU.bsv` move rule; `PimNUTb.bsv:63` |
| Timer message | Send `create`/`on_after` to a timer request device | `MAN` `e-ioctrl.tex` pp. 368-370 |
| User attention | Instantiate the window attention line to `attention` | `MAN` `e-ioctrl.tex` p. 356 |

### 4.2 What to assert

1. **Halt**: after `start`, the program reaches `halt`; `halted()` is true,
   `error()` is false, and `pc()` equals the address after the `halt` word
   (the model's `PimSmoke` checks `halted` and `pc`; `PimSmoke.bsv` lines
   49-60).
2. **Undefined opcode**: `error()` latches and `halted()` stays false; the
   `running` register clears (`PimPU.bsv:196-197`). The model's smoke test
   prints "FAIL: undefined opcode" only if the program is malformed, so a
   dedicated negative test is needed. Status (2026-11-19): written in
   `bsv/PimNegativeTests.bsv`, run by `bsv/run_neg_tb.sh`; the injection
   that comments out `errorSeen <= True;` in `PimE.bsv` produces "FAIL:
   undefined opcode did not latch error()" and "PimNegTb: FAIL".
3. **Legal opcode**: `error()` stays false for every opcode in `docs/isa.md`.
   Status (2026-11-19): the same testbench loads a one-word `halt` program
   and asserts `error()` stays false while `halted()` rises.
4. **NU tail**: `packetTail()` pulses exactly once for a packet byte whose
   bit 8 is set, and not for a byte whose bit 8 is clear; `PimNUTb` already
   asserts this (header lines 1-20; `watchTail` at line 63).
5. **Timer**: `on_after` returns `normal(Now)` and `Now` unifies with
   `wake_up` at the requested time (`MAN` `e-ioctrl.tex` p. 370). This is a
   message-level assertion, not a PE interrupt.
6. **Attention**: `^C` instantiates the attention variable to `attention`
   and the device reports interruption (`MAN` `e-ioctrl.tex` p. 356).

### 4.3 What is unknown and cannot be asserted

- No PE interrupt vector, priority, mask, or acknowledge sequence is
  documented; the diagnostic cannot assert that a NU/timer/SCSI event
  reaches the PE as an interrupt.
- The `PimPU` interface has no interrupt input, so the model cannot receive
  one; the NU tail is a standalone pulse.
- The KL1-B encoding is not in the corpus (`docs/isa.md` "Gaps"), so a
  KL1-B program cannot be loaded; only the model ISA can.
- The exception tag bit assignment is not in the acquired `.tex` files
  (`e-shoen.tex` points to a table that is absent), so the diagnostic cannot
  assert a specific tag value.

## 5. Blockers

1. **No PIM/m interrupt architecture.** `M92` pp. 425-435 and `TR659` pp. 1-9
   document the NU tail interrupt and the PE's interrupt request register,
   but not the vector, priority, mask, or acknowledge path. The model cannot
   implement or test a PE interrupt without inventing one. This is the
   largest gap for WP5.1.
2. **No KL1-B encoding.** The corpus has no KL1-B manual or encoding table
   (`docs/isa.md` "Gaps"; `docs/README.md`). The model's ISA is a diagnostic
   stand-in; a KL1 workload cannot be described as historical PIM/m execution.
3. **No PIMOS-to-PE hardware register map.** The manual documents the message
   interface; the boot entry `pim:go/4` is source-only. The model's `PimPU`
   interface is model-defined. Any claim that the model implements the
   historical PIMOS-to-PE interface would be unsupported.
4. **The NU tail interrupt is not connected to the PE in the model.**
   `PimPU` has no interrupt input; `PimNU.packetTail()` is only observed by
   `PimNUTb`. A single-PE diagnostic can test the pulse, not the delivery.
5. **Exception tag table absent.** `e-shoen.tex` references Table
   `language-defined-exception` for the tag bit layout, but the table is not
   in the acquired `.tex` files. The exception kinds are listed; the numeric
   tags are not.

## Sources read

- `docs/kl1_architecture.md` (TR-389 pp. 7, 9, 13; TR-246 pp. 3-4)
- `docs/pim_architecture.md` (M92 pp. 425-435; "Not stated" §)
- `docs/isa.md` (opcode table, gaps)
- `docs/README.md` (corpus inventory and gaps)
- `docs/nonlocal/MANIFEST.md` (archive paths and checksums)
- `Eman/e-top.tex`, `e-kl1.tex`, `e-builtin.tex`, `e-shoen.tex`,
  `e-io.tex`, `e-ioctrl.tex`, `e-ioutls.tex`, `e-ioutltim.tex`,
  `e-task.tex`, `e-rsc.tex`, `e-proginfo.tex`, `e-protocol.tex`,
  `e-error.tex`, `e-listener.tex`, `e-inspecto.tex`, `e-network.tex`,
  `e-compiler.tex`
- `SRC/README`, `SRC/README.j`, `SRC/protocol/*.prt`,
  `SRC/src/kernel/task/*.kl1`, `SRC/src/kernel/builtin/*.kl1`,
  `SRC/src/bios/boot/bios.kl1`, `SRC/src/bios/scsi/scsi_blt.kl1`,
  `SRC/src/vm/vm.kl1`
- `MODEL` `bsv/PimPU.bsv`, `bsv/PimE.bsv`, `bsv/PimNU.bsv`,
  `bsv/PimNUTb.bsv`, `bsv/PimSmoke.bsv`, `bsv/PimUlx3s.bsv`,
  `bsv/PimPUFormal.bsv`
