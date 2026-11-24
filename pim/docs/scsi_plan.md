# Getting SCSI up: plan (2026-11-23)

The owner asked for "a plan to get scsi up". This is it. The status it
starts from, and the plan's rungs S0..S7, each with what verifies it.

## 1. Where it stands

- PIMOS reaches its banner on the reference model ("PIMOS V 3.600
  20-May-93", `longrun_ipl.py --reference --go`), runs on through
  `scsi_where` and stops 1,722 instructions into `pim:go/4` at
  `scsi_init`: no device attached. On the Bluespec core the whole
  IPL load is identical (447,739,516 trace lines); `--go` has not been
  run there.
- `scsi_init` (22:DF) and `scsi_command` (22:DB) exist on the
  **reference model only** (`pimm.py` `i_scsi_init`, `i_scsi_command`,
  `scsi_poll`; `docs/pimm_semantics.md` rows). Their values are OURS,
  those of the PIMOS source's stand-in `bios/scsi/scsi_blt.kl1`
  (buffer 16000, `{0,0,0}`, `{16000,8,4,0}`); the firmware's are not
  held.
- The device is `ref/pimm/fep.py` (OURS, written from the PIMOS side
  of the protocol): a processor-type SCSI target at unit 7, SEND on
  LUN 0, RECEIVE on LUN 1, and only the IPL's file commands
  (`read_open` 201, `getb` 210, `close` 60, `abort` 70); anything else
  raises `FepError`.
- `ref/pimm/ref_scsi.py` runs the body of `ipl:boot0/0` on them: the
  IPL reads its list and its files through its own SCSI stack (parts
  one file, two files, characters, late, odd, small buffer; `--real`
  for the held `pimos.ipl`). No Bluespec side, no lockstep.
- What `--go` reaches is **not** the IPL's SCSI use but the kernel's:
  `pim:go/4` opens its own link to the FEP (the kernel's
  `bios/fep_module/*` and `server/fep/*`), and through it the console
  window, files, string I/O, the timer and sockets.

## 2. What is sourced and what is not

| Layer | Source | Status |
|---|---|---|
| SCSI bus use by PIMOS (CDBs, units, LUNs, directions) | `bios/scsi/scsi_common.kl1`, `scsi_processor.kl1`, `scsi_handler.kl1`, `SAM.kl1`, `DAM*.kl1` | HELD, source |
| Packet layer (8-byte header, continued packets, message encoding) | `bios/fep_module/scsi_fep.kl1`, the image's `scsi_fep_module`; `docs/binary_reverse_engineering.md` 1.4 | HELD, source and object |
| Device protocols, PIMOS side (file, directory, window, string I/O, timer, socket; `fep#` codes in `macro/pimos/pimos/pimos.vmac`, 104 live) | `bios/fep_module/*_dvc.kl1`, `server/fep/{fep,file,window,string_io,timer,socket}/*.kl1` | HELD, source |
| The built-ins themselves (what the firmware did on `scsi_command`, interrupts, `TargetInterruptVector`) | none | LOST: OURS, kept to the stand-in `scsi_blt.kl1` |
| The FEP side (a PSI running SIMPOS and `pimfep.ptf`, `pimscsi.ptf`) | `.ptf` compiled ESP only (`pimfep` 24 classes) | HELD-BINARY-ONLY; runs only with SIMPOS (roadmap §9, P5) |

So every byte PIMOS sends and expects is fixed by held source. What
is ours is the built-ins' machine-level behaviour and, until P5,
the FEP's answers, which are written to satisfy the PIMOS side and
labelled.

## 3. The rungs

**S0. The kernel's FEP conversation, on the reference model.** Give
`longrun_ipl.py --go` the device (`Machine.fep = fep.FEP()`), as
`ref_scsi.py` does, and run until `fep.py` raises `FepError` on the
first command it does not know. Repeat: each stop names one `fep#`
command and its device; implement its answer in `fep.py` from the
PIMOS source of that device (cited file:line, the answer OURS where
the source leaves a choice), and record the sequence. Verified by: the
run goes further each time; the commands PIMOS sends are decoded and
listed in order in `docs/binary_reverse_engineering.md` 1.4 (a new
"the kernel's FEP conversation" part). Expected order, from
`pim:go/4`'s source (to be confirmed by the run): the FEP's
configuration (`conf_dvc`), the console window (`win_dvc`,
`strio_dvc`), the timer (`time_dvc`), files for `pimos.conf` and the
rest of the system.

**S1. The device interface on the Bluespec core.** A new box,
`bsv/PimmScsiBox.bsv`, in the idiomatic structure (request/response
methods, its own rules), owning `scsi_init` and `scsi_command`:
- `scsi_init`: the same three constants as the reference (OURS).
- `scsi_command`: waits for the vector of seven, reads the CDB
  string, and for SEND reads the buffer's bytes out (DMA from the
  heap), for RECEIVE writes the reply into the buffer string and binds
  `Data`, `TransferredLength`, `Id`, `Result`, `NewObj` as the
  reference does; the "not finished yet" path binds `Id` and `NewObj`
  first and the rest when the device answers.
- The device is outside the core, on a port of `mkPimmCore`
  (`scsiReq`/`scsiResp`), so that the same core can later face a
  live FEP.

**S2. The device on the bench: a replay of the reference's device.**
The lockstep bench is scripted, not live. So the reference model,
playing the script, records each SCSI command and the device's answer
in order, and `driver.py` writes them into the script as data (a
"device tape"). The Bluespec bench answers `scsiReq` from the tape
and prints every command it is given (unit, LUN, CDB, the bytes of a
SEND) as trace lines (`B ...`), which the reference prints too: so
the bytes the core puts on the bus are compared line by line, not
assumed. The waiting path is recorded as the point where the
reference ran dry (`scsi_poll`), which the lockstep makes the same
point on both models. Verified by: S3.

**S3. Lockstep of the IPL's file service.** `lockstep_scsi.py`:
`ref_scsi.py`'s parts (one file, two files, characters, late, odd,
small buffer) on both models, the checks `ref_scsi.py` makes plus the
bus lines. Discriminating by injection into `PimmScsiBox.bsv` (a SEND
byte wrong, the length off by one, the RECEIVE written one cell off,
`Id` not counted, the waiting path binding everything at once,
`Result` nonzero), observed first differences in the header; what is
not caught recorded. Then `ref_scsi.py`'s gate (`Machine.ahead` for
`scsi_init`/`scsi_command`) is removed.

**S4. The real IPL by SCSI on both models.** `longrun_ipl.py` gains a
`--scsi` mode in which the IPL reads the held `pimos.ipl` list and
every system file through its own SCSI stack and `fep.py` (instead of
the bench serving `load/4`), run on both models and pinned. This is
the real boot path of `ipl:boot0/0` minus the shoen of `boot/0`.

**S5. `pim:go/4` past `scsi_init` on both models.** S0's FEP
conversation on the Bluespec core, through the tape, as far as S0
reached on the reference; pinned; each new device's first exchange
with its own lockstep part.

**S6. A live FEP.** For an interactive console (typing to PIMOS's
listener), the bench's tape is replaced by a pipe to `fep.py` running
beside Bluesim (the `srv/` probe-server pattern), the device port
unchanged. Not lockstep: the lockstep stays on the tape.

**S7. The real FEP (joins P5).** `pimfep.ptf` and `pimscsi.ptf` run
under a SIMPOS reconstruction (or its stubs) on a PSI model and
replace `fep.py` behind the same port. Its answers then check every
OURS answer of `fep.py`; differences are recorded, not smoothed.

### Status (2026-11-23)

- **S1 done.** `bsv/PimmScsiBox.bsv`: `init`/`initInfo`/`command`/
  `result` from the exec stage (a small hook in `PimmStages.bsv`),
  `poll`/`polled` from the bench; the device on `mkPimmCore`'s port
  `scsiReq`/`scsiResp`. The buffer size is the device's (asked by
  `scsi_init`, `B init`), as on the reference.
- **S2 done.** The reference records each device answer
  (`Machine.scsi_tape`); `driver.py` writes them after the script's
  END (`TAPE` word, "The device tape"); the script's new `POLL` is the
  dry-machine poll. Both models print a `B` line per try (unit, LUN,
  CDB, direction, length, a SEND's bytes); the bench's from what the
  core sent. Extension needed and taken: `POLL` (the flow had no
  "the machine has run dry" point of its own) and the tape; a long
  vector (seven elements) is built from `NEWVAR`/`UNIFY`/`PTR`, no new
  operation.
- **S3 in part.** `ref/pimm/lockstep_scsi.py` runs `scsi_init` and
  `scsi_command` in lockstep at their sites (`scsi:create/2`,
  `scsi:command_executer/2`): TEST UNIT READY, SEND, RECEIVE, a reply
  cut in two, both waiting paths, an element waited for; injections
  in its header. `scsi_command`'s `Machine.ahead` gate (waiting on an
  element) is removed. `ref_scsi.py`'s six IPL parts are written as
  scripts and pass `ref_scsi.check` and the bus check under
  `lockstep_scsi.py --reference`, but are NOT on the core: the IPL
  binds a merger input to a vector (`scsi_fep_general:
  request_device_io/5`), which the core refuses. The suite's run FAILS
  once the reference stops refusing it without `Machine.ahead`, so
  that they are moved in and pinned then.

## 4. Order and dependencies

S0 and S1 are independent and go first, in parallel. S2 needs S1.
S3 needs S2. S4 needs S3. S5 needs S0 and S4. S6 needs S5. S7 needs
the PSI and SIMPOS rungs (roadmap §9). R6 of the roadmap (the
listener's prompt) is reached inside S5.

## 5. Open questions it will meet

- The firmware's `scsi_command`: interrupts and the
  `TargetInterruptVector`, a command that never completes, a bus
  reset (`scsi_abort`, `scsi_reset`, `scsi_bus_reset`: 7 uses in the
  objects, none on the IPL's path).
- `getb`'s unit (bytes or 16-bit characters): the IPL does not fix it;
  `file_dvcb.kl1` counts bytes (`getb(Size)` asks `Size*2+1`).
- The FEP's real buffer size and answers to configuration requests:
  `pimfep.ptf`'s constants may give them (read its strings and
  literal table before choosing).
- Whether PIM/m's console (`display_console`) goes over SCSI at all or
  to the CSP; the trace's console stays as it is until a source says.
