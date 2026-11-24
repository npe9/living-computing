# Getting SCSI up: plan (2026-11-23)

The owner asked for "a plan to get scsi up". This is it. The status it
starts from, and the plan's rungs S0..S7, each with what verifies it.

## 1. Where it stands

- PIMOS reaches its banner on the reference model ("PIMOS V 3.600
  20-May-93", `longrun_ipl.py --reference --go`), runs on through
  `scsi_where` and stops 1,722 instructions into `pim:go/4` at
  `scsi_init`: no device attached. *(2026-11-23, S0 begun: with the
  device, `longrun_ipl.py --reference --go --fep`, `scsi_init` passes
  and the model stops after 3,612 instructions at the guard
  instruction `multiply`, not implemented, in `scsi:check_lun/4`,
  during the kernel's bus scan, before any `scsi_command`. So the FEP
  conversation is still empty. `docs/binary_reverse_engineering.md`
  1.4, "The kernel's FEP conversation". `--save`/`--load` cache the
  machine after the link.)* *(Later 2026-11-23: guard `multiply`,
  `save`/`restore`, `diff` and `wait_value` on vectors on both models;
  `fep.py` answers INQUIRY to unit 7 and TEST UNIT READY to the absent
  units 0-5 (OURS, sourced in 1.4); `--go` makes BootInfo with the
  IPL's `make_boot_info/1`. The kernel's bus scan completes: 8 SCSI
  commands, 12,912 instructions; no FEP packet yet. The stop is
  `enqueue_goal_to_processor` with an unbound node number, a choice
  about the firmware recorded in 1.4 with VPIM's and KLIC's reading
  (wait for the number) and PDSS's (ignore it).)* *(2026-11-24: the
  wait implemented from VPIM, as the session lead decided; then
  `system_timer`/`set_timer` (the clock at 0, ours), signed
  `write_integer`, `wait_vector_0`, `apply` with `{}`, `diff` of a
  structure and an atom, all on both models; `fep.py` answers the
  kernel's FIRST FEP MESSAGE, `append_open` of `pimos:pimos.syslog`
  (accepted, ours). 23,348 instructions, 10 SCSI commands, the console
  still the banner alone; the stop `jump`, not implemented (1.4).)*
  *(Later 2026-11-24, from a cached machine made afresh: `jump`,
  `set_marked_variable`, the general `wait_vector` and
  `multiply_bignum_by_word` on both models; `fep.py` answers the
  kernel's timer device, `create_timer` and `get_date_time` (a fixed
  clock, ours). 65,482 instructions, the console the banner alone; the
  stop `subtract_bignum` on a `32#{0}` made from our clock at 0, a
  decision about the clock (1.4).)* *(Later 2026-11-24: the clock
  advances with the instructions, one tick every 423 (1.4);
  `subtract_bignum`, `get_constant`, body `vector/3`,
  `code_to_predicate`, the unification of long vectors and
  `add_shoen_resource` on both models; `fep.py` answers the timer's
  `close`. 92,797 instructions, the console the banner alone; the stop
  `fep_attributes` (240) on a file device, whose values only the FEP
  has (1.4).)* *(Later 2026-11-24, the login and the shell (2026-11-24, following
  `docs/fep_services.md` §6 and §7): `fep.py` answers 240 (Dir `">"`),
  the `pimos:` files from the held object, the string-I/O devices of
  the login service, the window calls, and holds the server's `io(1)`
  and the window's `getl`; `longrun_ipl.py` gives the device its
  scripted event (the login of §7.5) when PIMOS idles; eleven more
  instructions on both models (`lockstep_login.py`,
  `lockstep_shoen3.py`, `lockstep_alt.py`). 8,587,092 instructions
  (8,586,110 before the merger timing change of 2026-11-24):
  the local login service starts, the tcpip one is refused, the login
  `pimos` (user `pmpsi`) is accepted, the window `PIMOS CONSOLE` is
  made and the shell writes `Shell>> ` to it; the run ends with its
  `getl` held, 1,220 goals waiting (1.4). With `--type shutdown`
  the line is taken and the command starts; with the merger acting in
  the order of the unifications on both models (2026-11-24,
  `pimm_semantics.md` merge) and `fep.py` answering `shutdown_body`'s
  string-I/O window, `pimos_standard_io_window`, it runs to `PIMOS
  END********` (8,766,339 instructions); `cat <= file("pimos:pimos.groups")`
  reads that file through `pimos:` (1.4, "A command typed").)* On the Bluespec core the whole
  IPL load is identical (447,739,516 trace lines, 2026-11-23, before
  the merger timing change); `--go` has not been
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

**S1h. The FEP emulator on the ULX3S** (asked for 2026-11-23: "a
scsi emulator on the ulx3s using either sdram, qspi flash or the sd
card"). `fep.py` in hardware, `bsv/PimmFepEmu.bsv`, serving files from
the board's **SD card**, chosen because the SDRAM already holds the
PIM/m local store (`PimUlx3s.bsv`), the QSPI flash holds the bitstream
and is small and awkward to rewrite from the host, and the card is
large, removable and written by the host like the FEP's own disk. The
card image format and its builder are OURS (`tools/mkfepcard.py`); the
reader is SPI mode and read-only by construction (`bsv/PimmSdBlock.bsv`).
STATUS 2026-11-23: verified in Bluesim only. Every command
`ref_scsi.py`'s six parts gave `fep.py` (recorded,
`ref/pimm/record_fep.py`, `ref/pimm/fep_tapes/`), plus a direct sequence
of OURS for what the parts never do (a failed open, abort, a request in
two packets, a reply cut three times, each `FepError`), answered equal to
`fep.py` byte for byte, over the image file and over the SPI reader
with a card model (`bsv/run_fepemu.sh`, in `run_tests.sh`); injected
faults caught (`bsv/PimmFepEmuTb.bsv` header).
STATUS 2026-11-24: it follows `fep.py` into PIMOS's start. Covered, as
`fep.py` on master has them: INQUIRY to unit 7 (`03 00 07 00 00`), TEST
UNIT READY to the absent units 0-5 (Result `800h`, decided in the
emulator because `fep.py` decides it in `Fep.command`, not in the
device port), and `append_open` (203) answered `[1]`. Tapes: `kernel`,
recorded from the real start (`record_fep.py --kernel PKL` on a machine
`longrun_ipl.py --reference --save` wrote: 11 calls, 10 answered, the
start stopping at `jump`), and `direct_kernel`, a direct sequence of
OURS for those answers' edges and every `FepError` next to them (52
commands). 9 tapes, 293 commands, all equal; nine injections into the
new paths each caught. NOT covered, because `fep.py` does not answer
them yet: `putb` (111) and `close` of an appending device (both refused,
as `fep.py` raises); no log is kept, and the card stays read-only. How
to add the next command: the recipe in `bsv/PimmFepEmu.bsv`'s header.
The board top with a self-test synthesizes (10,499 LUT4, 3 DP16KD,
42.50 MHz, 2026-11-24; 10,039 LUT4 and 40.39 MHz before;
`bsv/run_fepemu_fpga.sh`) and its self-test passes in
Bluesim; it has NOT run on a board (the board is in use; programming it
and writing a card are the owner's steps, `bsv/README.md`). Not yet
connected to the core: the adapter to S1's `scsiReq`/`scsiResp` port is
described in `bsv/README.md`; it is the hardware twin of S2's tape and
S6's live FEP, behind the same port.
STATUS 2026-11-24, later: it follows `fep.py` to the shell's prompt
(`longrun_ipl.py --load PKL --go --fep`: 8,586,110 instructions, the
login answered, "Shell>> " on the window, its getl held). Covered:
`create_timer` 310, `get_date_time` 304 (the time of day from a clock
input, `setTime`, as `fep.py` takes `Fep.ticks` from the machine's
timer), the timer's close, `fep_attributes` 240, the pimos: files from
the card (`tools/mkfepcard.py --held` adds the held object directory as
pimos:NAME; absent names 5), 601/620 for the login's replier, servers
and `simpos_user_device`, the window calls, 60 on string-I/O and
windows, 112 on a read file, 70 on a held request [6], and the held
requests with the event that answers them. A held request is seen by
the core as a RECEIVE that stays outstanding (not ready at each poll,
kept in `PimmScsiBox`'s waiting list), and the emulator's `idle` input
(the bench's question when the machine has run dry, `Fep.idle()`)
takes the next entry of a script on the card and answers the lowest
device holding that kind. `fep.py`'s constants (the attributes message,
the script) are on the card (`mkfepcard.fep_tables`), so the scripted
command line another change adds to `fep.py` needs a new card, not new
hardware. Tapes: `kernel` re-recorded to the prompt (175 calls, 2
events; the clock and the events are records on the tape), and
`direct_kernel` with every new answer's edges and errors (309 commands,
10 events, under a script of two logins and two lines). 9 tapes, 714
commands and 12 events, all equal on the three benches; thirteen
injections into the new paths, twelve caught at once and the
thirteenth (the user device's length word, high byte) after a section
for it was added (`bsv/PimmFepEmuTb.bsv`). The board top synthesizes
at 14,799 LUT4, 4,243 FF, 3 DP16KD, 36.69 MHz (PASS at 25 MHz), its
self-test passing in Bluesim on the new `--held` card (54 entries).

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
- **S3 done.** `ref/pimm/lockstep_scsi.py` runs `scsi_init` and
  `scsi_command` in lockstep at their sites (`scsi:create/2`,
  `scsi:command_executer/2`): TEST UNIT READY, SEND, RECEIVE, a reply
  cut in two, both waiting paths, an element waited for; injections
  in its header. `scsi_command`'s `Machine.ahead` gate (waiting on an
  element) is removed, and `ref_scsi.py` no longer sets
  `Machine.ahead`. `ref_scsi.py`'s six IPL parts are on both models
  (`lockstep_scsi.py --part 1..6`, `run_pimm_lockstep.sh`'s
  `scsi@1..6`, since the merger's vector input reached the core in
  master's d1beeb7b): 1,458,322 / 2,683,031 / 2,654,349 / 2,683,403 /
  324,652 / 71,735 trace lines identical, `ref_scsi.check` and the
  bus check on each. The bench now waits for a spawned goal's record
  before its next operation (the IPL parts load an argument register
  right after a SPAWN, and the register's A line was traced before the
  record's M lines). Injections re-done against the six IPL parts
  (2026-11-24, eleven, each against `scsi` and `scsi@1..6`, observed
  sets in `lockstep_scsi.py`'s header): the CDB byte order, unit/LUN
  swapped, the last received byte dropped, TransferredLength, Result,
  two Info elements and the init hook's registers fail all seven; a
  command not ready at a poll dropped or taken as ready fail `scsi`
  only (no IPL part has a command not ready at a poll: counted on the
  tapes); the copy's pad from old memory fails none (unobservable:
  every string's pad is zero).

## 4. Order and dependencies

S0 and S1 are independent and go first, in parallel. S1h needs
nothing; joining it to the core needs S1. S2 needs S1.
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
