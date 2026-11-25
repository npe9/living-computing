# Reverse engineering the binaries: what a bounded probe recovered, and what finishing would take

Written 2026-11-20 in answer to the owner's question, "see if you can
reverse engineer the binaries and what that would take". Each of the
binary-only components in `docs/nonlocal/` was actually attacked for a
bounded time; this note records how far that got, what completing it
needs, and what it buys on the way to booting PIMOS 3.6.

**Labels.** MEASURED = output of a tool run in this session (the tool
is named). READ = from a named file. INFERENCE = a conclusion not
itself checked. DERIVED = worked out by hand from MEASURED or READ
material and not executed.

**Tools added (all read-only, all read the archives directly).**

| Tool | What it does |
|---|---|
| `asm/kl1decomp.py` | KL1-B object code of the IPL image back to KL1 clauses. `MODULE [PRED/N]`, `--check`, `--fidelity MODULE SOURCE` |
| `asm/savsrc.py` | the 502 modules of the 20 `.sav` files against the held source, by predicate set. `--modules`, `--patches`, `--diff MOD` |
| `asm/ptfdump.py` | container, classes, predicates and constant tables of the compiled ESP packages (`.ptf`). `PKG [CLASS] [--pairs] [--list]`, `--opcodes`, `--check` |

## 0. Answer in brief

| # | Component | Probe result | Feasibility | What it unblocks |
|---|---|---|---|---|
| 1 | IPL image, 12 modules with no source | all 349 predicates decompile to readable KL1 (1,023 clauses); boot sequence and the FEP packet format are read out below | **done as a prototype; mechanical to finish** | gap C2 (the front end at boot), C3, B2; a specification for `scsi_command` at R4 |
| 2 | the 20 `.sav` files | 501 of 502 modules have a source module; source is the *patched* text; the IPL image's source-backed modules are different (where datable, older) text | **done** (predicate-set depth) | says which oracle to trust per module |
| 3 | Pseudo PIM/m microcode | not re-derived. New: the firmware's own reverse assembler is held as compiled ESP and its field-value tables already come out | **research today; mechanical once the KL0 code of `rassy` is read** | B1, B4, B6, B7, B8 and cycle counts; not on the shortest path to R4 |
| 4 | compiled ESP packages (`.ptf`) | container fully parsed (554 classes); the FEP's command table recovered (99 of 105 codes equal PIMOS's, none differ); opcode *set* identified against `sysidat`; opcode *names* not | **container done; KL0 disassembler mechanical with a research tail** | C2, C4 from the FEP's side; component 3 through `rassy` |
| 5 | others | `.ldb` and `.sym` are text; `paragraph.ptf` has source (the known plaintext for 4); `sysinit` not characterised | — | — |

**Single most valuable next step:** name the KL0 opcodes from the
`paragraph.ptf` / `src_util/paragraph/*.esp` pair, then read two
targets with the result: `pimmutil##rassy` (gives the complete
microinstruction format, component 3) and about 4,700 cells of
`pimfep` (message assembly, dispatch, file service). For the boot path
alone nothing more is needed from the binaries: section 1.3 and 1.4
are enough to write the front-end stand-in for R4.

## 1. The IPL image: KL1-B decompiles to KL1

### 1.1 What was built (MEASURED, `python3 asm/kl1decomp.py --check`)

`kl1decomp.py` walks a predicate's code symbolically, one walk per path
through the indexing instructions (`try_me_else`, `switch_on_*`,
`hash_on_constant`). Passive instructions bind the head's variables to
patterns, guard built-ins become guard goals, the rest body goals; a
path that reaches `proceed` or `execute` prints as one clause.

- Instruction boundaries: 349 of 349 predicates sweep to exactly their
  end; 1,183 labels, none off an instruction boundary.
- 349 predicates give 1,023 clauses; no path limit hit; all 144
  instruction names in the image are handled, none left as raw.
- Structured constants (`put_structured_constant`) are resolved from
  the image: strings, vectors, lists, module references.
- `read_eagerly` is printed as `alternatively.` (INFERENCE from where
  it stands, between clause groups, e.g. `top:top_level_monitor/4`).

**Fidelity against source** (clause count per predicate; contents
compared by hand for three predicates only, so this is reach, not
depth):

| Module | predicates | same name/arity in source | same clause count | source |
|---|---|---|---|---|
| `jis_to_ascii` | 3 | 3 | 3 | `bios/boot/jtoa.kl1` |
| `shoen` | 22 | 21 | 21 | `kernel/builtin/shoen.kl1` |
| `scsi_common` | 13 | 13 | 12 | `bios/scsi/scsi_common.kl1` |
| `scsi` | 9 | 5 | 4 | `bios/scsi/scsi_handler.kl1` |
| `scsi_builtin` | 2 | 2 | 2 | `bios/scsi/scsi_blt.kl1` |
| `scsi_processor` | 3 | 1 | 1 | `bios/scsi/scsi_processor.kl1` |
| `exception_table` | 14 | 3 | 1 | `kernel/builtin/excpt_tbl.kl1` |
| `builtin_utility` | 8 | 4 | 0 | `kernel/builtin/string.kl1` |

- Hand-compared and equal: `scsi_common:check_completion_code/4` is
  the source's three clauses, same guards, same bodies (the compiler
  adds `integer(A)`).
- **All 8 predicates whose clause count differs were read against the
  source; none is a decompiler artefact.** Each is different text in
  the image:
  - `builtin_utility` `substring/5`, `copy_string_elements/7`,
    `append_string/2`, `append_string/3`: the image has the clauses
    the held `string.kl1` keeps only as comments (the 16-bit guards,
    `append_string([],S) :- S = ""`), so the image is the **older**
    text.
  - `scsi:request_manager/3`: the image's handler knows only
    `processor` devices, and its `version/1` string is "SCSI KL1
    Handler Release 1.6 03-Jul-91"; the held `scsi_handler.kl1` says
    "Release 2.1 03-Feb-92" (and lists 1.5 and 2.0 before it, not
    1.6: a side branch, INFERENCE).
  - `scsi_common:check_inquiry_command/4`: one normal clause where
    the source has five (by length).
  - `exception_table` `translate_profiling_data/2`,
    `get_builtin_name/3`: same clause structure as the source's
    `/4` and `/5` forms without their two threaded arguments, and
    different result terms. The source file is under `:- switch
    (machine_type)`, `:- case(mpsi)`; which is older is not
    established.
- None of these files' `:- switch` branches gives the image's text
  (`scsi_common.kl1`, `scsi_handler.kl1` switch on `fep_interface`
  around the whole module, not around these predicates).
- So the IPL image's source-backed modules are a weaker oracle than
  assumed: `exception_table` shares 3 of 14 predicates with the source
  file, where the same module in `pimm_kernel360E.sav` shares 16 of 16
  (`python3 asm/savsrc.py --diff exception_table`).
- One oddity is the object's, not the tool's: `ipl_scsi:check_status/6`
  tests its first argument for 1 in both clauses, before and after
  `otherwise` (cells 7466 and 7476 are the same `wait_integer`), so
  its "cannot initiate file device" clause can never run.

**Limits of the prototype** (each seen in the output):

- No variable names, comments or macro forms: `fep#read_open` comes
  back as `201`, `string#"..."` as a string.
- Clause order inside a group is discovery order, not source order.
- HEURISTIC: of the paths ending at the same exit with the same
  constant keys, the shortest head and guard is printed. Without it an
  else-branch reprints a clause with the earlier clause's pattern
  still attached (`reply_with_attention/4` printed 11 clauses for 5).
  It could hide a clause in a predicate where two source clauses share
  compiled code and differ only in a non-constant pattern; none seen.
- The compiler merges clauses with identical bodies under one
  `switch_on_constant` (`reply_with_attention`: `reset` and
  `next_attention` share one body); these print as separate clauses.
- A body built-in that waits for an input prints before the goal that
  produces the input; read bodies as dataflow, not sequence.
- It reads the `.kbn` image only. The `.sav` files hold the same
  instruction words (`asm/unlsav.py`); feeding them in needs the
  label and external-reference forms of that container. Not done.

**A defect found in passing** (MEASURED): `kbndis.py` names every
function-numbered opcode by its first table entry. In the image the 9
"`export_entry`" are `tag_and_value`, and the 8
"`floating_point_equal`" are 4 `floating_point_not_less_than` and 4
`floating_point_to_integer` (all in `ipl_pool`, hashing float keys).
`gap_analysis.md` B2's `export_entry` and the census names for
opcodes `6e 6f 76 fc fd` (tag 23) and `be bf ce cf` (tag 22) inherit
this. `kl1decomp.py` decodes the function number (`klb_opr.kl1`
`p({f_r_r,F}...)`: bits 23-16).

### 1.2 Which no-source modules have near-source (MEASURED)

`scsi_fep_module` (38 predicates) against `bios/fep_module/scsi_fep.kl1`
(43): 8 share name and arity, and the packet layout is the same
(1.4). `scsi_fep_file` matches `bios/fep_module/file_dvc.kl1` in its
message shapes (`device_create`, `{DevID, fep#read_open, Node,
Username, Password, Pathname}`, READ at `file_dvc.kl1` lines 19-26).
The IPL modules are an earlier, smaller generation of the kernel's FEP
client, not a different protocol.

### 1.3 What `ipl:boot/0` does, through to the first front-end request

Clauses are `kl1decomp.py` output with constants named by hand from
`macro/pimos/pimos/pimos.vmac` (the `fep#` names are READ there; the
numbers are in the object code). Everything in this section is READ
from the decompiled code unless marked.

```
ipl:boot :-
    predicate_to_code(module#ipl, boot0, 0, Code),
    shoen:execute(Code, {}, [start|Ctl], Report),      % a shoen for the IPL
    ipl_monitor(Report, Ctl, Done),
    wait_finish(Done).                                 % then halt(0)

ipl:boot0 :-
    scsi_fep_module:create(0, 0, 7, 0, 1, 0, normal(Fep)),
    ipl_scsi:scsi(Fep, GeneralTail, FileReq, ScsiEnd),
    ipl_files(FileReq, "pimos:pimos.ipl", OpenReqs, Files),
    ipl_loader:load(Files, OpenReqs, Close, Loaded),
    top:go(Loaded, BootInfo, GeneralTail, ScsiEnd),
    make_boot_info(BootInfo),
    close(Close).
```

The variable names are chosen here (INFERENCE from use); the object
has none. `GeneralTail` is the tail of the general request stream
after the `{200, ...}` request (`ipl_scsi:wait_file_request/6`
unifies it); `top:go/4` binds it to 0 at once, which is the
end-of-stream value `scsi_fep_general:request_device_io/5` waits for.

1. **The shoen comes first.** `shoen:execute/4` is the first thing
   executed; `ipl_monitor/3` answers `resource_low` with
   `add_resource(1073741823, -1), allow_resource_report`, prints
   exceptions on the console ("EXCEPTION WAS OCCURRED in IPL : error
   code:") and ends with "SCSI-FEP END********".
2. **`scsi_fep_module:create(0, 0, 7, 0, 1, 0, R)`**: processor 0,
   SCSI object argument 0, target unit 7, send LUN 0, receive LUN 1,
   first device id 0. (The names are INFERENCE from
   `bios/boot/bios.kl1`, which gives the same five numbers as
   Cluster, Processor, Unit, Send_LUN, Receive_LUN.) It runs
   `scsi:create/2` on processor 0, which executes the built-in
   `scsi_init(^Obj, ^Vec, ^Info)`.
3. `[get_info(I)]` to the SCSI handler returns `normal(MaxLUN,
   MaxBuffer)`, `MaxBuffer` being element 0 of `scsi_init`'s `Info`.
   **The firmware chooses the packet buffer size**; the image has no
   constant for it (the non-built-in stub in `scsi_blt.kl1` says
   16000).
4. `[processor(7, 0, S)]` opens the send device. Because the LUN is
   0, the handler issues **TEST UNIT READY** first (CDB of FIVE
   bytes as the built-in is given it, not the six this document
   first said: `new_string(5, 8, CDB)` in the decompiled
   `scsi_common:test_unit_ready/6`, `scsi#group_0_command_size => 5`
   in `macro/pimos/scsi/scsi.vmac` line 38, and five bytes observed
   in the run of 1.4; whether the firmware put a sixth, the control
   byte of a SCSI group 0 command, on the bus is not known;
   `scsi_common.kl1` lines 21-42, READ). `[processor(7, 1, R)]` opens
   the receive device with no command (its LUN is not 0).
5. Two byte strings of `MaxBuffer` bytes are made (send and receive
   buffers); an id manager, a sender and a receiver start.
6. `ipl_scsi:scsi/4` sends the *general* request stream, as vectors
   whose last element is the next request:
   `{50, Abort, Attention, St, Next}` (`fep#reset`), then
   `{200, File, St, Next}` (`fep#file`), then on the file stream
   `{50, ...}` again. **None of these reaches the wire**:
   `scsi_fep_general:request_device_io/5` and
   `scsi_fep_file:request_device_process/4` answer them with status 1
   locally.
7. `ipl_files/4` asks `open("pimos:pimos.ipl", F)`; `ipl_scsi` turns
   it into `{201, 0, 0, "pimos:pimos.ipl", File, St, Next}`
   (`fep#read_open`; that the two zeros are user and password is
   INFERENCE from `file_dvc.kl1`'s `{fep#read_open, Username,
   Password, Pathname, ...}`). `scsi_fep_file` takes device
   id 0 from the id manager and sends the message
   `{0, 201, "", 0, 0, "pimos:pimos.ipl"}`. **This is the first
   front-end request.** On the bus (DERIVED; then EXECUTED on the
   reference model, 2026-11-23, `ref/pimm/ref_scsi.py`: the TEST UNIT
   READY, this SEND, the RECEIVE with `MaxBuffer` 16000 = `003e80`,
   and the `getb` of item 8 came out byte for byte as derived here;
   see "Run" at the end of 1.4):

   ```
   SEND (0Ah) to unit 7 LUN 0, CDB 0a 00 00 00 48, 72 bytes:
   00000000            device id 0
   00000000            fep#packet_last
   000000c9            201, fep#read_open
   00000004            four arguments
   00000000 ffffffff ffffffff 0000001e     "" , integer, integer, 30 bytes
   00000000            (user)
   00000000            (password)
   2370 2369 236d 236f 2373 2127 2370 2369 236d 236f 2373 2125 2369 2370 236c 0000
                       "pimos:pimos.ipl" in two-byte JIS, padded to 4

   RECEIVE (08h) from unit 7 LUN 1, CDB 08 20 <MaxBuffer, 3 bytes>;
   the expected answer is 16 bytes:
   00000000 00000000 00000001 00000000      id 0, last, fep#normal, no arguments
   ```
8. Then, per read: `getb` is `{0, 210, 7936}` (24 bytes:
   `00000000 00000000 000000d2 00000001 ffffffff 00001f00`), and the
   answer `{0, 1, String}` carries the data as a byte string, which the
   IPL widens to 16-bit elements; status 2 (`fep#eod`) ends the file.
   The unit of 7936 (bytes or 16-bit characters) is not determined
   by the IPL (run both ways, same result; "Run" at the end of 1.4,
   which also gives what the kernel source says).
9. `ipl:decompose/2` splits the text of `pimos.ipl` at 16-bit code 10
   (line feed) and skips from JIS `%` (`2173`) to the end of the line.
   Each name is opened the same way (device ids 1, 2, ...),
   `ipl_loader` reads it as 16-bit words through
   `ipl_file_decoder:decode/8`, sum-checks it, and prints "IPL
   loading", then "Link Modules ...".
10. `top:go/4` meanwhile starts the atom-number server (clients ask
    with `supply_atom_number`; the server's constants are 16384,
    8192 and 16777216, INFERENCE first number, range size and limit)
    and waits for the loader. On
    `normal(Atoms, Modules, Status, Code)`, with `Code` =
    `predicate_to_code` of `go/4` in the module the atom table gives
    for `"pim"`, it runs `apply(Code, {BootInfo, Atoms, Modules,
    Status})`. Failure prints "No PIMOS Top Module", "No PIMOS Top
    Predicate : pim:go/4" or "IPL Failed" and halts.
11. `BootInfo` is a 16-bit string: elements 0-4 = 0, 0, 7, 0, 1,
    element 16 = the length of the path, the path from element 17.
    The held `bios.kl1` documents the length at element 5 and the path
    from 6 (`decompose_boot_info`, READ at lines 364-378). This does
    not matter for boot: `go2` there is under `:- switch
    (ipl_parameter)`; one branch takes elements 0-4 and discards the
    path, the other ignores the string and uses the constants 0, 0, 7,
    0, 1. Which branch `pimm_bios360E.sav` was built with is not
    determined; both give the same five numbers.

### 1.4 The packet and message format the IPL speaks (READ from `scsi_fep_module`, `scsi_fep_file`, `scsi_processor`)

*(The whole command set and the order of the start, from the PIMOS source: `docs/fep_services.md`.)*

**SCSI level.** One built-in, `scsi_command(Obj, {Unit, LUN, CDB,
Length, Dir, Buffer, 0}, ^Data, ^TransferredLength, ^Id, ^Result,
^NewObj)` (operand directions from `compiler/blt.kl1`). The IPL uses
three commands, all to unit 7:

| Command | CDB (5 bytes are set; a string of 5) | Dir | LUN |
|---|---|---|---|
| TEST UNIT READY | `00 LUN<<5 ...` | none | 0, once |
| SEND | `0a LUN<<5 len>>16 len>>8 len` | 1 | 0 |
| RECEIVE | `08 LUN<<5 len>>16 len>>8 len` | 2 | 1 |

What the built-in must return (READ from the decompiled
`scsi_common:analyze_scsi_command_result/7`, which equals the
source's lines 153-157):

- `Result` is one integer: status byte = `Result /\ 1Eh`, completion
  code = `(Result >> 8) /\ FFh`, detail = `Result >> 16`. **Success is
  `Result` = 0** (status 0, completion code 0, by
  `check_completion_code/4`); completion-code bit 3 gives
  `no_status`, status 2 makes the handler issue REQUEST SENSE
  (`check_condition`, source line 163).
- `Data` must be an 8-bit string (`check_send_command`,
  `check_receive_command`).
- `TransferredLength` must be the true byte count on RECEIVE: the
  receiver takes the payload as bytes 8 to `TransferredLength`
  (`receive_packet2_1/9`, `receive_packet3/9`: `Length - 8`).

**Packet level** (all fields 32 bits, big-endian):

```
 0  device id
 4  0 = last packet of the message, 1 = continued
 8  command (request) or status (reply)
12  n = number of arguments
16  n words: -1 for an integer, else the byte length of a string
16+4n  the arguments in order: an integer as 4 bytes; a string as its
       bytes, padded with zeros to a multiple of 4
```

- A 16-bit string is sent as its bytes (length = 2 x characters); a
  received string is widened back to 16 bits.
- A message longer than the buffer is cut: every piece repeats the
  8-byte header, pieces but the last have flag 1, and the receiver
  joins pieces by device id (`receive_packet2_1`, a pool keyed by id).
- This is the same layout as the kernel's `scsi_fep.kl1`
  (`send_packet/6`, `send_packet1/8`: id at 0, flag at 4, command at
  8, count at 12, lengths from 16; READ at lines 266-340). Two
  generations of the client agree.

**Message level.**

- A request is `{Id, Command, Args...}`; a reply is `{Id, Status,
  Results...}` matched to its waiter by `Id`. `Id` is chosen by the
  PIMOS side, 0 upward, one per opened device.
- One RECEIVE is issued per message sent, except after `{Id, 70}`
  (`fep#abort`), which expects none.
- A reply whose status is 3 (`fep#attention`) is unsolicited: it sets
  the device's attention variable and a further RECEIVE is issued.
- Status 1 = normal, 2 = end of data, 5 = abnormal (set locally on a
  send failure), 6 = aborted (set locally).

| Request (wire) | Reply | Seen in |
|---|---|---|
| `{Id, 201, "", 0, 0, Path}` read_open (202 write, 203 append likewise) | `{Id, 1}` | `scsi_fep_file:device_create/5` |
| `{Id, 210, N}` getb | `{Id, 1, String}` or `{Id, 2, ...}` | `device_io/7`, `ipl_scsi:wait_command_status/5` |
| `{Id, 111, String}` putb | `{Id, St}` | `device_io/7` |
| `{Id, 112}` flush; `{Id, 220}` end_of_file; `{Id, 221}` pathname; `{Id, 222}` attributes | `{Id, St, ...}` | `device_io/7` |
| `{Id, 60}` close | `{Id, _}` | `device_io/7`, `device_terminate/5` |
| `{Id, 70}` abort | none | `device_io/7`, `scsi_sender/6` |

Not used by the IPL: `fep#ipl` (400) and `fep#symbol` (500). The IPL
reads its files through the ordinary file service. (MEASURED: no 400
or 500 in the decompiled `ipl*`, `scsi_fep_*` modules; the front end's
side agrees, section 4.)

**Run** (EXECUTED on the reference model alone, 2026-11-23:
`python3 ref/pimm/ref_scsi.py`, against a model of the FEP written
from this section, `ref/pimm/fep.py`; the firmware's choices it had
to make are labelled OURS there and in `docs/pimm_semantics.md`).
The body of `ipl:boot0` without `top:go/4` reads a file list and
loads the files it names through the IPL's own stack; the answer of
`load/4` is the one the bench-served run gets
(`lockstep_link.py`). What the run adds to the reading above:

- **The bytes of 1.3 items 7 and 8 are right**, all of them. The
  second request is `getb` (24 bytes), answered here with
  `{0, 1, <the 86 bytes of a one-line list>}`; a second `getb` gets
  `{0, 2}`, then `{0, 60}` (close, 16 bytes) is sent and answered
  before device 1 is opened.
- **The loader asks again after the end of data**: a `.sav` file gets
  two `getb` answered `{Id, 2}` before its close (the list gets
  one). A front end must go on answering end of data.
- **The unit of 7936 is not determined by the IPL.** It passes the
  number through and joins whatever comes: a front end that gives
  7,936 bytes a `getb` and one that gives 15,872 load the same files
  to the same answer (parts "two files" and "characters"). The held
  kernel source counts BYTES: `server/fep/file/file_dvcb.kl1` turns
  the user's `getb(Size)` (16-bit elements) into
  `Size2 = Size*2`, asks the front end for `{fep#getb, Size2+1}` and
  counts what comes as 8-bit elements (lines 301, 397-400, 510-534,
  READ); `file_dvc.kl1` line 390 asks for `Size*3+1`. The same
  front end served the IPL and then the kernel in one boot, so
  bytes is the reading with a source. It stays an INFERENCE: the
  kernel's code only needs the front end to give AT LEAST what it
  counts in bytes (it keeps what is left over), so a front end
  counting characters would satisfy it too; the kernel's client is
  a later generation than the IPL's; and a commented-out
  `send_message_getb` in the same file passes `Size` unchanged for
  code 0. The front end's own `getb/4` (`pimfep.ptf`, `pimos_file`)
  is not decoded. `fep.py` takes bytes by default, as OURS.
  Arithmetic only: 16 + 4 + 15,872 = 15,892 fits the stand-in's
  16,000 as well.
- **Widening is `change_element_size(S, 16, S1)`**
  (`scsi_fep_module:str8_to_msg3/8` through `str8_to_str16/2`): two
  bytes an element, the first the high byte, and an odd byte count
  gets a zero byte at the END of that reply (the built-in's rule in
  the manual). So every `getb` reply must have an even number of
  bytes: with 1,001 bytes a reply the zero bytes land inside the
  file and `load/4` answers `abnormal("internal error while reading
  unloaded file")` (part "odd", observed).
- **The IPL does not ask for the rest of a continued reply.**
  `receive_packet2_1/9` stores a piece whose flag is 1 and goes back
  to `receive_packet/6` on the SAME request list; a RECEIVE is only
  issued per message sent (and once more after an attention). So a
  reply cut into pieces stops the boot: with a 512-byte buffer the
  IPL takes the first piece of a 2,604-byte reply and issues nothing
  more (part "small buffer", observed). The kernel's receiver
  (`scsi_fep.kl1` lines 473-558) loops on RECEIVE with no request
  list and has no such limit. So `MaxBuffer` must hold a whole
  `getb` reply: at least 7,956 bytes if 7936 counts bytes, 15,892 if
  characters.
- **`TransferredLength` too large is harmless for a reply in one
  packet** (narrowing "must be the true byte count" above, which
  holds for a continued reply, whose pieces are joined by that
  length): with the buffer's length returned instead, the same
  files load to the same answer; the IPL cuts a one-packet reply by
  the message's own length words (an injection in `ref_scsi.py`'s
  header; only one-packet replies were run). `Data`, though, must
  be the whole buffer: the IPL uses it as its next buffer, and an
  exact-length string makes the next RECEIVE longer than its buffer
  (another injection there).
- **A check condition is followed up**: with TEST UNIT READY
  answered 2 the handler sends REQUEST SENSE, CDB `03 00 00 00 08`,
  direction in, 8 bytes (an injection, observed; not served).
- The RECEIVE for a reply reaches the built-in AFTER its SEND in
  this model's goal order (never before, in every part), so the
  built-in's "not finished yet" path is only run by a test device
  that refuses each RECEIVE once (part "late").
- On the held `pimos.ipl` (`--real 130`: stopped after 130
  commands): the twenty names, then `pimm_kernel360E.sav` read to
  its end (408,482 bytes in 52 replies) and `pimm_shell360E.sav`
  opened as device 2; the console is given "IPL loading", "PIMM
  KERNEL     :3.600:25-Nov-93", "PIMM SHELL      :3.600:25-Nov-93"
  (a system file's own title, where a patch file shows its path).
  7.3 M heap cells, 14.2 M instructions; 388 s, measured with seven
  other runs on the machine, so an upper bound.

Not run: `top:go/4` and both shoens, a failing open, abort,
attention, a message sent in more than one packet.

**What an emulator for R4 must do** (DERIVED; the reference model's
prototype does this, see "Run"): implement `scsi_init`
(return a buffer size) and `scsi_command` for the three CDBs above,
returning `Result` 0 and the true length;
answer `read_open` with `{Id, 1}`, `getb` with `{Id, 1, bytes}` then
`{Id, 2}`, `close` with `{Id, st}`; serve `pimos.ipl` and the 20
`.sav` files under the names `pimos.ipl` gives. No window, timer or
string I/O is touched before `pim:go/4`.

**The kernel's FEP conversation** (rung S0 of `docs/scsi_plan.md`;
EXECUTED on the reference model alone, 2026-11-23:
`python3 ref/pimm/longrun_ipl.py --reference --save FILE --go --fep`,
then `--load FILE --go --fep`, the same result).
`pim:go/4` is run after the whole link with `ref/pimm/fep.py`
attached as `ref_scsi.py` attaches it, and the commands that wait for
the device are given it again whenever the machine runs dry.

- **First run (2026-11-23, rung S0 begun): the conversation was empty.**
  `scsi_init` passed (OURS values, `docs/pimm_semantics.md`), no
  `scsi_command` was issued: 3,612 instructions, the stop the guard
  instruction `multiply` (`23:F6`) in the loaded module `scsi`,
  `check_lun/4` (`bios/scsi/scsi_handler.kl1`:119-122, `LUN =<
  ((ExtLUN * 2040) + 7)`, ExtLUN 4, `scsi_init`'s Info element 2, OURS),
  for unit 0 LUN 0 of the kernel's bus scan.
- **The loop since** (each stop, what was done; the instructions on both
  models with a lockstep test, the FEP answers in `fep.py`):

  | Stop | Done | Instructions run |
  |---|---|---|
  | guard `multiply` in `scsi:check_lun/4` | implemented (`lockstep_gmul.py`; with it `save`/`restore`, which its test site needs) | 3,612 |
  | `FepError`: INQUIRY to unit 7 | answered (below) | 5,066 |
  | guard `diff` in `scsi_manager:create_scsi_device/9` (`Type \= non_existent`) | implemented (`lockstep_rdvc.py`) | 5,198 |
  | `FepError`: TEST UNIT READY to unit 5 | an absent unit answered (below) | 5,447 |
  | `enqueue_goal_to_processor` with an unbound number, `bios.kl1`:383 `scsi_fep:create(..)@node(Cluster)` | not the machine: the bench's BootInfo was unbound; `longrun_ipl.py --go` now runs the IPL's own `make_boot_info/1` on it, as `ipl:boot0` does (item 11 of 1.3) | 6,500 |
  | `wait_value` on two vectors, `keyed_bag`, the key `{0,0,0}` | implemented for vectors of atomic elements (`lockstep_pvec.py`) | 10,781 |
  | `enqueue_goal_to_processor` with an unbound number, `scsi_manager:check_lpid_pool/7` (`bios/boot/scsi_man.kl1`:499/506, `create_scsi_device(..)@node(Cluster)`, Cluster from an `LPID_POOL` `get` in the same body) | waited for, from VPIM (`lockstep_tproc.py`; below) | 12,912 |
  | `system_timer` in `system_timer_manager:create/3`, then `set_timer` | implemented, the clock at 0, OURS (`lockstep_timer.py`) | 13,695 |
  | `write_integer` with bit 23 set, `scsi_fep:check_data_size1/6` `L = [-1\|NL]` | the 24 bits are signed, the assembler's c24 form (`lockstep_wint.py`) | 14,482 |
  | `FepError`: the kernel's first FEP message, `append_open` of `pimos:pimos.syslog` | answered (below) | 15,331 |
  | `wait_vector_0`, `scsi_fep:receive_packet2_1/8` | implemented (`lockstep_alt.py`) | 16,104 |
  | `apply(Code, {})`, a predicate of no argument | implemented (`lockstep_apply.py`) | 17,501 |
  | `diff` of a structure and an atom, `task_handler` | succeeds, as KLIC and PDSS have it (`lockstep_rdvc.py`) | 22,630 |
  | `enqueue_goal_to_processor` waiting, 10 arguments | the stub's limit raised from 9 to 11 | 22,902 |
  | `jump`, in a module the boot loads | implemented (`lockstep_alt.py`) | 23,348 |
  | `set_marked_variable` | implemented (`lockstep_alt.py`) | 23,498 |
  | `wait_vector`, the general form for 7 or more | implemented (`lockstep_alt.py`) | 28,156 |
  | `FepError`: device 17, `create_timer` (310) | answered (below) | 61,795 |
  | `FepError`: device 17, `get_date_time` (304) | answered (below) | 64,017 |
  | `multiply_bignum_word` (`multiply_bignum_by_word`), `timer_calc:trans` | implemented, after VPIM (`lockstep_bignum.py`) | 65,471 |
  | `subtract_bignum(32#{}, 32#{0})`, the `32#{0}` from the clock at 0 (`timeSdvc.kl1`) | the clock now advances with the instructions (`pimm.py` `INSTRUCTIONS_PER_TICK`, `lockstep_timer.py`), so the bignum is not `{0}`; `subtract_bignum` implemented, after VPIM (`lockstep_bignum.py`) | 65,482 |
  | `FepError`: device 17, `close` (60), the timer device's end | answered (the table of FEP answers) | 66,016 |
  | `get_constant` | implemented (`lockstep_alt.py`) | 72,642 |
  | body `vector/3` (`b_vector`) | implemented (`lockstep_alt.py`) | 74,704 |
  | `code_to_predicate` | implemented (`lockstep_alt.py`) | 74,724 |
  | unification of two vectors of seven or more | the `unify_step` goal, the sizes compared in its steps (`lockstep_alt.py`) | 74,759 |
  | `add_shoen_resource` | implemented, `resource_added` reported (`lockstep_shoen3.py`) | 75,014 |
  | `FepError`: device 18, `fep_attributes` (240) | answered (`docs/fep_services.md` §6.3, §7.8; below) | 92,797 |
  | `search_character`, reading `pimos.conf` | implemented (`lockstep_alt.py`) | 139,747 |
  | `FepError`: device 20, `flush` (112) of a read file | answered `[1]` (`file_dvc.kl1`:314) | 6,675,822 |
  | nothing left to run, no login: `pimos.conf` read as `with_console` then `end_of_file` | the kernel asks `getb` for `Size*2+1` bytes and a reply of an odd count is widened by a zero byte, so the data came one byte late; the stand-in now counts the kernel's `getb` in characters (`Fep(getb_unit=2)`, OURS from this observation, since READ from `pimfep##pimos_file` getb/4, row below; the IPL works either way) | 7,754,386 |
  | the login: PIMOS idles with the server's `io(1)` pending | the scripted login of §7.5 at the idle (`Fep.idle()`, `longrun_ipl.py` `go()`) | 8,067,269 (the event) |
  | `enqueue_goal_external` of 12 arguments | the vector spread as `enqueue_goal`'s (`lockstep_load.py`'s instruction; the spread `lockstep_login.py`) | 8,144,967 |
  | `unbound` | implemented, after VPIM (`lockstep_login.py`) | 8,145,997 |
  | guard `extended_floating_point` | implemented, a type test (`lockstep_login.py`) | 8,146,451 |
  | guard `module` | implemented (`lockstep_login.py`) | 8,147,246 |
  | `apply` of a vector of 7 or more | implemented (`lockstep_login.py`) | 8,192,723 |
  | `add_extended` (and the three others) | implemented, after VPIM (`lockstep_login.py`) | 8,194,757 |
  | `allow_shoen_resource_report` | implemented, `resource_report_allowed` reported (`lockstep_shoen3.py`) | 8,194,822 |
  | guard `bignum_not_less_than` (and `bignum_less_than`) | implemented, after VPIM (`lockstep_login.py`) | 8,247,127 |
  | `create_shoen` with `{MinPrio, MaxPrio}`, `{MinNode, NumNode}` (`shoen:execute1/7`) | accepted and dropped as the integers are (`lockstep_shoen3.py`) | 8,256,632 |
  | `enqueue_goal` of 17 arguments | the spread of a vector of 7 or more (`lockstep_login.py`) | 8,463,929 |
  | **the shell's prompt**: `Shell>> ` written to the window (111), its `getl` (110) held | the end of rung R6's first half (`docs/fep_services.md` §7.6) | 8,587,092, 1,220 goals waiting (8,586,110 before the merger timing change of 2026-11-24) |

  The counts after the login are those of the run with `getb_unit=2`;
  the two before it (139,747 and 6,675,822) are from runs before that
  change.

  The clock (2026-11-24, the session lead's decision): one tick of the system timer (1/16 msec, 48 bits, manual `e-builtin.tex`:1537-1549) every 423 instructions executed. The rate is 615 KLIPS on `append` (`M92` p. 425) at this image's 11 instructions per `append/3` reduction (`scsi_fep_module`); equal cost per instruction is OURS. `get_date_time` keeps the date 20-May-1993; its time of day follows the same clock, so midnight is the boot.

  240 (device 18, a file device made by `fep_file_device:device_create/5`, `bios/fep_module/file_dvc.kl1`:43-52, `{DevID, 240, Node}`, `fep#fep_attributes`, `pimos.vmac`:87; the reply read by `fep_util:set_value/2` as `{DevID, Status, Code, OS, Host, FepVer, Dir, FileVer, Comment}`, the seven values kept by `server/fep/fep/fep_sv.kl1` `get_fep_attributes5`) is answered `[1, 0, "SIMPOS V7", "PSI", "V0.45", ">", ".", ""]` in JIS (`fep.py` `ATTRIBUTES`): the fifth value is the path delimiter, `">"` for SIMPOS (`docs/fep_services.md` §7.8, `fileRdvc.kl1`:124-126); OS must begin `"SIMPOS"` (§7.8, `file_dvcb.kl1`:557-562); `"V0.45"` is `pimfep.ptf`'s `pimos_scsi_front_end` version; `"V7"` and `"PSI"` are OURS (§6.3).

  The FEP answers added for the login (`ref/pimm/fep.py`, 2026-11-24, following `docs/fep_services.md` §6 and §7.5; the commands the run gave are in `longrun_ipl.py`'s log):

  | Command | Answer | Source |
  |---|---|---|
  | 201 `read_open` of `pimos:NAME` | the held `pimosobj.tar.Z` `object/NAME` (`longrun_ipl.py` `kernel_file`; held and read: `pimos.conf`, `pimos.logins`, `pimos.groups`), 5 when not there (`autoload.tbl`) | §7.2 |
  | 201 of `me:NAME` or of the home `>sys>user>RN>NAME` | 5 (`me:pimos.init`, `shell.com`, `pimos.com`: INSTALL puts none there, so the prompt is the default) | §7.2, §7.8 |
  | 210 `getb` of the kernel | the count read in characters (`getb_unit=2`): first OURS, from the run (above); READ 2026-11-24 from the held PSI side: `pimfep##pimos_file` local `getb/4` @259-25a makes `new_string(S, Size, 16)` (`a7 00 00 10`, `1c 00 03 00`; A3 is the message's Size by the arity rule of `fep_services.md` §6.1, its one INFERENCE), sends `:getb/3` to the SIMPOS file and replies `substring(S, 0, N)` (@263): at most Size 16-bit characters (`docs/simpos/source_check_2026-11-24.md` §4) | the run; `pimfep.ptf` |
  | 112 `flush` of a read file | `[1]` | `file_dvc.kl1`:314 |
  | 601 `create` of a string-I/O device `pimos_remote_login_replier`, `pimos_remote_login_server`, `simpos_user_device` | `[1]`; any other name refused | §6.4, §7.5 |
  | 620 `io(0, ..)`, `io(2, ..)` on the replier | `[1, ""]` | §6.4, §7.5 |
  | 620 `io(1, Text)` on the replier | `[1, "\0"]` (one character, 0: sent), the text written to the stand-in's log. §7.5 has `""`; §6.4's reading of `pimfep.ptf` is kept, and PIMOS reads neither | §6.4 |
  | 620 `io(0, "local")` / `io(0, "tcpip")` on the server | `[1, ""]` / `[5]` (the tcpip service refused, `CANNOT MAKE A TCPIP LOGIN SERVICE!!`) | §7.5 |
  | 620 `io(1, ..)` on the local server | held; answered at the idle with `[1, NI]`, the login record: Node `"local"`, RN `"pmpsi"` (SOURCED, INSTALL's user), RP `""`, UN `"pimos"`, UP `""` (HELD FILE: `pimos.logins`, all six with empty passwords), ID 1 (OURS, §7.5; §6.5 has 0 for a first login) | §6.5, §7.5 |
  | 620 `io(0, ..)` on `simpos_user_device` | `[1, ">sys>user>" ++ RN]` | §7.5, `login_p.kl1`:63 |
  | 104 `create` of a window | `[1]` | §6.8, §7.5 |
  | 127, 130, 132, 141, 142, 143, 111 `putb`, 112 `flush` on a window | `[1]`; a 111's text written to the log | §6.8, §7.5 |
  | 110 `getl` on a window | held; answered at the idle by the next typed line, `[1, LINE]` in JIS with no newline (`Fep(lines=..)`, `longrun_ipl.py --type LINE`; the event list OURS, the reply's form `bios/fep_module/win_dvc.kl1`:307-312; whether the FEP sends a newline is not known, §7.5). Without `--type` the run ends there | §7.5 |
  | 60 `close` of a string-I/O device or a window | `[1]` | §4, §7.5 |
  | 70 on a held request | `[6]` (met at the shutdown: the local server's held `io(1)`; a 70 on anything else has no reply) | §6.7, §7.1 |
  | 601 `create` of the string-I/O device `pimos_standard_io_window` (added 2026-11-24 for `shutdown`) | `[1]` | §6.4, `shutdown_b.kl1`:41-42 |
  | 620 `io(104, ..)`, `io(130, ..)`, `io(141, ..)`, `io(111, Text)` on it (added 2026-11-24) | `[1, ""]`, OURS: the PSI's class is not held; the window device's own 104/130/141/111 answer `{Id, 1}` (§2.6) and a 620 reply carries a string (§6.4). A 111's text to the log | §2.6, §6.4 |
  | 620 `io(110, "")` on it (added 2026-11-24) | held, as a window's 110; answered at the idle by the next typed line, `[1, LINE]` | §7.5 |
  | 60 `close` of the file append-opened (`pimos:pimos.syslog`, at PIMOS's end; added 2026-11-24) | `[1]`, as a read file's close; the appended bytes stay in `Fep.appended`. The FEP emulator (`bsv/PimmFepEmu.bsv`) follows it, and the 601/620 rows above and the `{-1, 80}` row below, since 2026-11-24 (until then it refused this 60: `bsv/run_fepemu.sh`'s `direct_kernel` tape FAILed at its command 49, "emulator refused (why 7); fep.py done") | §2.2 |
  | `{-1, 80}`, `fep#terminate`, when the link's stream closes at PIMOS's end (added 2026-11-24) | no reply (none is read); noted as `Fep.terminated` | §1, `scsi_fep.kl1`:234 |
  | the typed line's characters (2026-11-24) | `"`, `(`, `)`, `=` added to `fep.py`'s JIS table, from PIMOS's own `server/telnet/code_cv.kl1`:154-182 (`table_ascii_to_jis`) | `code_cv.kl1` |

  What the console shows: `PIMOS V 3.600 20-May-93`, `LOCAL  LOGIN SERVICE STARTS ***`, 0, `CANNOT MAKE A TCPIP LOGIN SERVICE!!`, 0; the replier's texts `Login procedure starts.`, `OK. Your initial program starts.`, `Good luck!` in the stand-in's log; the window `PIMOS CONSOLE` (127: at 200, 200, 47 by 14) and in it `Shell>> `, as §7.6 predicts.

  **A command typed (2026-11-24, rung R6's second half: reached on the reference model, see the end of this item).**
  `longrun_ipl.py --load FILE --go --fep --type shutdown --type yes`
  (`shutdown` is the one command whose run the manual prints whole:
  `e-sysman.tex`:121-144). The held 110 is answered `[1, "shutdown"]`;
  the window device then sends a 70 with nothing held (no reply, §6.7);
  the shell resolves `get_code pimos shutdown go 0` and the job runs
  `shutdown:go`, `privilege:execute(shutdown_body:go, ..)`, a task by
  `execute_super`, and `shutdown_body:go` asks
  `getenv(task:make_window)`. Under the merger timing before
  2026-11-24 the run then stopped: 8,673,642
  instructions, nothing left to run, 1,388 goals waiting, the second
  line never asked for. Nothing was refused. The cause is a wait
  cycle (traced with probes outside the tree):
  - the privilege task's `getenv` waits behind that task's
    `internal_handler:env_check/5` (`kernel/task/int_hdl.kl1`:481,
    493-499), which sent `get_info(Uid, _)` to the user table with Uid
    UNBOUND: the task's Info is not yet built, because
    `param_check3`'s `node_check` waits for the parent's
    `task:io_node` (336-340);
  - the parent (the job's task) holds its environment in its own
    `env_check`, waiting for its `get_info(101, _)`;
  - in the user table's `keyed_set` (`utility/pool/k_bag.kl1`:479)
    the unbound-key request is AHEAD of the 101 one: the guard
    `Key >= 0` suspends with the table, and the 101 request waits on
    its output. The job's request was issued at about 8,656,499
    instructions, the privilege task's at about 8,663,512: the table
    took them in the other order.
  The order is the model's merger: a merger input here is a goal
  (`merge_in`), so a message reaches the output only when that goal
  runs, and on the LIFO ready queue it runs after everything its
  waker's reduction spawned (docs/pimm_semantics.md, the merger,
  "after a goal switch, not at the unification": OURS). VPIM
  (`f_reduce_merger_unify.psl.c`: the MGHOK cell, a vector's elements
  connected in the same unification), KLIC (`runtime/gmerge.c`: the
  merger object's unify method appends the message during the
  unification) and PDSS (`emulator/unify.c` `active_unify_stream_*`)
  agree: the merger acts AT the unification. Two probes, the tree not
  edited: (a) the woken `merge_in` goals lifted to the top of the
  ready queue at the end of each reduction, and (b) a merger vector's
  elements readied first-element-first: either way the cycle does not
  form, `shutdown_body` takes its third branch (`make_window` and
  `top_task` both absent from the job's environment,
  `shutdown_b.kl1`:39-53) and asks for a string-I/O device
  `pimos_standard_io_window` (601), which `fep.py` refuses (FepError,
  8,689,393 instructions with (a)). **Changed on both models
  (2026-11-24)**: a woken `merge_in` goes on a merger's list taken
  before the ready queue, in the order the goals were woken
  (`pimm_semantics.md`, merge; `lockstep_merge.py`); every count after
  the first merger moved (the lockstep pins, `ref_scsi.py`'s heap
  cells; the wire is the same). The untyped run (a cache made afresh
  under the new rule) now ends at 8,587,092 instructions, 1,220 goals
  waiting, the same console and device log, but NOT the same FEP
  conversation: 119 messages for 118 (old rule run from its own
  cache, compared line by line): the timer's 304 answers another time
  (it is counted from the instructions), a 70 on the timer device
  (17) is new, the closes of devices 20, 21, 22 come in another order
  and the `Shell>> ` write (111) comes earlier. A tape recorded from
  the login before this change does not match it; with `--type shutdown
  --type yes` the cycle does not form, `shutdown_body` takes its third
  branch and the run stops at the 601 of `pimos_standard_io_window`
  (FepError, 8,690,718 instructions).

  **The shutdown runs to its end (2026-11-24, reference model).** With
  the answers in the table above (601 of `pimos_standard_io_window`,
  its 620s, the 60 on the syslog file, 80): `io(104, {324, 328, 40,
  6})`, `io(130, "SHUTDOWN")`, `io(141)`, `io(111, "Really(yes/no)?")`,
  `io(110)` answered "yes" by the second typed line; `wait_ans`
  (`shutdown_b.kl1`:71-73) raises `shut_down`; the devices are closed
  (the replier, the window, the string-I/O window, the server's held
  `io(1)` aborted with 70 and answered 6, the syslog file), then `{-1,
  80}`. Console: `Shutdown started`, `User Server End`, `Statistics in
  PIMOS:`, 0, 790104, `PIMOS END********`; the run ends at 8,766,339
  instructions, nothing left to run, 253 goals waiting.
  `longrun_ipl.py --load FILE --go --fep --type shutdown --type yes`.

  Why the third branch: the shell's `start_main` (`shell/main/
  shell.kl1`:88-103) finds `task:make_window` unset and `task:top_task`
  set (by `login_p:top`, `login_p.kl1`:94) and UNSETS `top_task`
  before running; `make_window` is set only by the telnet login
  (`tlogin.kl1`:93, `no`). So a command typed to a local login's shell
  has neither, and `shutdown_body` takes the third branch, a window of
  its own titled SHUTDOWN. The first branch (`make_window = no`,
  "Shutdown procedure starts." then "Really(yes/no)? " on the job's
  own I/O) is a telnet login's: READ from the code, not run. The
  second (`top_task` set) is the login as the user `shutdown`, the
  manual's footnote (held `pimos.logins`: program
  `pimos::shutdown:go`): `login_p:top` sets `top_task` and applies the
  program with no shell between. A probe outside the tree (`fep.py`'s
  login record with UN `shutdown`, then the line `yes`) gave "Shutdown
  procedure starts." and "Really(yes/no)? " on the `PIMOS CONSOLE`
  window, then the same console lines to `PIMOS END********` (769,710
  for the count): the second branch, run once, not in the suite.
  The earlier reading here, that the manual's transcript is the first
  branch's (a window made for the job), is WITHDRAWN: the branch with
  a window of its own is the third, and the manual's "displayed in the
  window" fits it as well as the others.

  Against the manual (`e-sysman.tex`:121-144), line by line
  (re-checked against the primary sources 2026-11-24,
  `docs/simpos/source_check_2026-11-24.md` §3):
  - **Which versions.** The manual is PIMOS V3.0 (`Eman/e-v30.tex`:4,
    `e-cover1.tex`:5; its boot log prints `V 3.000`,
    `e-sysman.tex`:106; files dated 17 Mar 1993). The held source and
    object are 3.600 of 20-May-93 (`kernel/init/version.kl1`:15-21;
    files dated 1994). The Japanese V3.0 manual (`ifs/manuals/pimos/
    man30.j.ps.Z`) prints the same transcript, `login Server End` and
    `000954C2` included, so it is not a slip of the English
    translation. No V3.0 source is held.
  - "Reply yes to the shutdown confirmation message that is displayed
    in the window": the third branch's window. The manual prints
    `\keyin{Really(yes/no) ?}{yes}` (the PostScript of the V1.5 manual,
    `man15.ps`, and of the Japanese V3.0 manual typeset the same space
    before `?`). The source's third branch writes `Really(yes/no)?`
    (`server/user/shutdown_b.kl1`:51; no space before `?`), the first
    and second `Really(yes/no)? ` (:23, :36). The two PIMOS primers
    print the source's form: `Really(yes/no)? yes` (`ifs/manuals/pimos/
    primer25.tex.Z`:460, `primer15.j.tex.Z`:524). So the space before
    `?` is the manual's own typesetting, CONTRADICTED by the primers and
    the source; the model writes the held source's string.
  - `Shutdown started`: the same (`kernel/init/init.kl1`:313).
  - `login Server End`: ours `User Server End`, the held source's
    (`server/login/init/usersvman.kl1`:195, outside any machine switch)
    and the held object's (`pimm_server360E.sav`, the only `Server End`
    string in `pimosobj`). `login Server End` is in no held source,
    object or archive (`pimos`, `pimosobj`, `psdpim`, `vpim`, `pdss`,
    `klic`, searched as bytes). The held source does name the job the
    user server runs "Login Server" (`server/user/user_sv.kl1`:29-31,
    `name("Login Server")`), so a V3.0 message naming it is plausible;
    that the string changed between 3.0 and 3.6 stays INFERENCE.
  - `Statistics in PIMOS:` then two integers: the same line
    (`bios/boot/bios.kl1`:144-147); the values are the report's
    `statistics(ResH, ResL)`, high and low words (`e-task.tex`:84
    `statistics(High_resoc, Low_resoc)`), counting two per reduction
    (`e-shoen.tex`:42, "1 for goal creation and 1 for termination of
    the reduction"): the manual's 0 and 000954C2h (611,522 = 2 x
    305,761, a V3.0 Multi-PSI run), ours 0 and 790,104 (C0E58h, 2 x
    395,052, `ref/pimm/pimm.py` `i_shoen_statistics`, which reports
    twice the shoen's reductions). Both are run counts of different
    runs, versions and machines: no source makes them comparable.
  - `PIMOS END********`: the same (`bios.kl1`:167).
  - The prefix `DC> ` and the `(  INTo) 00 00000000` form of an integer
    are the CSP's display, not PIMOS's strings: HELD in the PSI's CSP
    package `pimmcsp.ptf`, class `csp_halt_messages`
    (`python3 -I psi/fepread/ptfread.py pimmcsp --strings`: `'DC> '`
    for `display_console_word/3`, the format `'(\6s) \s \s'` for
    `display_console_word/2`, a tag right-aligned in six, then two
    words; the tag names `INTo`, `ATOMo`, ... in `csp_help_command`).
    The `PE00(00) @ ` part is not a literal there (not traced). This
    model's console list has the bare strings and integers.

  **A second command: a file read through `pimos:` (2026-11-24).**
  `--type 'cat <= file("pimos:pimos.groups")'` (`cat`, `e-shutil.tex`:
  152-154; `<=` the job's standard input, `e-shell.tex`:218-226): the
  shell read-opens `pimos:pimos.groups` (201, device 34), one `getb`,
  writes its two lines to the window (111) and closes the file (60);
  `cat` stops at the file's empty last line, as the manual says, and
  the shell writes `Shell>> ` again: 8,760,685 instructions, 1,224
  goals waiting, the next `getl` held. The text written is the held
  file's. No transcript of it is printed in the manual. Needed
  `fep.py`'s JIS table to have `"`, `(`, `)`, `=` (row above).

  The counts from `jump` on are from a cached machine made afresh with
  `longrun_ipl.py --reference --save` on 2026-11-24 (the run that made
  it gives 23,348 at `jump`, as the earlier cache patched with the new
  stubs did).

  The console is still the banner alone, `PIMOS V 3.600 20-May-93`.
  With the BootInfo string the cluster of `create_os_device/3` is bound
  where without it it was not: so the held `pimm_bios360E.sav` takes
  `decompose_boot_info`'s elements, not the constants branch of 1.3
  item 11 (INFERENCE from the two runs).
- **The conversation so far** (every command the device is given, in
  order; `python3 ref/pimm/longrun_ipl.py --load FILE --go --fep`):

  | # | Unit, LUN | Command | Answer (all OURS where not the source's) |
  |---|---|---|---|
  | 1 | 7, 0 | TEST UNIT READY, CDB `00 00 00 00 00` | Result 0 |
  | 2 | 7, 0 | INQUIRY, CDB `12 00 00 00 ff`, 255 bytes in | 5 bytes `03 00 07 00 00`: device type 3 (processor, `scsi.vmac`:82), not removable, byte 2 7, additional length 0. The values are the source's own canned answer for a front end it does not ask, `normal(scsi#processor,0,7,"")` (`scsi_man.kl1`, `inquiry/8` under `fep_interface` `kl1_network`); the length is OURS, the least that gives that answer (`scsi_common.kl1`:99-106). No inquiry data was found in `pimscsi.ptf` or `pimfep.ptf` (`asm/ptfdump.py`: the classes `scsi_device`, `scsi_handler`, `pseudo_scsi`, `scsi_communicator`, `scsi_device_bus_management` have `sense` and nothing of the kind) |
  | 3-8 | 5, 4, 3, 2, 1, 0; LUN 0 | TEST UNIT READY | no device: Result `800h`, completion code 8, which PIMOS reads as `abnormal(no_status(8,0))` (`scsi_common.kl1`:186-199: bit 3 of the completion code is the only failure code the source names); the scan then drops the unit with no message (`scsi_man.kl1` `inquiry/8`'s last clause). OURS, a choice about the lost built-in, not the FEP; the manual's boot log finds unit 7 only (`e-sysman.tex`:103-112, "SCSI UNITS FOUND", then 7 and 0) |

  | 9 | 7, 0 | SEND, the packet of device 16: `append_open` (203, `macro/pimos/pimos/pimos.vmac`:69), `{16, 203, "", 0, 0, "pimos:pimos.syslog"}` in JIS, the kernel's syslog (`bios/boot/syslog.kl1` `wait_status1/3`, on every boot) | accepted, `[1]` (normal), OURS: the stand-in keeps what is appended in memory (`Fep.appended`), as a FEP holding the file would append to it. PIMOS also takes an abnormal answer, with "SYSLOG ERROR: reason / cannot open file pimos:pimos.syslog" on the console (`syslog.kl1`); the real FEP's answer is not held |
  | 10 | 7, 1 | RECEIVE, the reply | as before |
  | 11-12 | 7, 0 then 1 | SEND and RECEIVE, device 17: `create_timer` (310, `pimos.vmac`:146), `{17, 310, Node, User, Password}`, the kernel's timer device (`bios/fep_module/time_dvc.kl1` `device_create/5`) | accepted, `[1]`, OURS: a FEP that has a timer. `reply/9` goes on to `device_process`, the timer's requests; an abnormal answer would end the device |
  | 13-14 | 7, 0 then 1 | SEND and RECEIVE, device 17: `get_date_time` (304, `pimos.vmac`:95), `{17, 304}` (`time_dvc.kl1` `device_io1/13`: the reply `{Status, Date, Time}`) | `[1, 33742, T]`, OURS, the same on every run. The date is the banner's, 20-May-1993, as PIMOS counts dates (days from 01-Jan-1901, `utility/timer/date.kl1` `get_date_count`). T, milliseconds from midnight (`utility/timer/time.kl1`), follows the machine's clock (`pimm.py` `timer()`, 2026-11-24; it was 0): midnight is the moment the processor booted. PIMOS keeps the difference of the two as its time equation (`server/fep/fep/time_sv.kl1` `wait_date_time/2`, `compare/4`). In the long run T = 28,927: the cached machine's clock includes the whole IPL load |
  | 15-16 | 7, 0 then 1 | SEND and RECEIVE, device 17: `close` (60), `{17, 60}`, the timer device's end when its stream ends (`time_dvc.kl1` `device_io1/13`, then `device_terminate/5`) | accepted, `[1]`, OURS, as a file's close (2026-11-24) |

  The FEP commands of this table are all on the FEP emulator's tapes
  (`bsv/PimmFepEmu.bsv`; 2026-11-24, below): INQUIRY to unit 7; TEST
  UNIT READY to units 0-5; the packets `append_open` (203),
  `create_timer` (310), `get_date_time` (304) and the timer's `close`
  (60).

  Unit 6 is PIM/m's own (`scsi_where`) and is not asked.
  The FEP emulator (`bsv/PimmFepEmu.bsv`, `bsv/run_fepemu.sh`) answers
  every command of the table above as `fep.py` does, byte for byte
  (2026-11-24): the tape `ref/pimm/fep_tapes/kernel.tape` is this
  conversation recorded from the run (`ref/pimm/record_fep.py --kernel
  PKL`), and `direct_kernel.tape` its edges. `putb` (111), which the
  syslog sends next by the source, is refused there as `fep.py` refuses
  it today.
  2026-11-24, later: the emulator follows `fep.py` to the shell's
  prompt. Every answer of the login run above (240, the pimos: files
  and the 5s for `autoload.tbl`, `me:` and the home, 601/620 for the
  replier, the servers and `simpos_user_device`, the window calls, 110
  held, 60 on string-I/O and windows, 70 on a held request [6], 112 on
  a read file, getb counted in characters) and the event: the held
  io(1) is a RECEIVE that stays outstanding (not ready at every poll)
  until `Fep.idle()`'s scripted login, which the emulator takes from
  the card's script (`tools/mkfepcard.py` writes `fep.Fep().script`
  and `fep.ATTRIBUTES` there, and `--held` the held object directory as
  pimos:NAME). `kernel.tape` re-recorded to the prompt (175 calls, 126
  answered, the clock and 2 events on the tape: 8,586,110 instructions,
  the same as `longrun_ipl.py --load ... --go --fep`); `direct_kernel`
  holds every new answer's edges. All equal on the three benches
  (`bsv/run_fepemu.sh`); the design and the recipe for the next answer
  (a scripted line for the held 110 is a new card, not new hardware):
  `bsv/PimmFepEmu.bsv`'s header.
  2026-11-24, after the merger change and the typed shutdown: the
  emulator also answers 601 of `pimos_standard_io_window`, its 620
  io 104/130/141/111 (`[1, ""]`) and 110 (held, answered by the event),
  60 on the append-opened file (`[1]`) and `{-1, 80}` (no reply).
  `kernel.tape` re-recorded under the merger rule and on to PIMOS END
  (`record_fep.py --kernel PKL --type shutdown --type yes`: 220 calls,
  155 answered, 4 events; 8,766,339 instructions), `late.tape`
  re-recorded (its RECEIVE retries move under the merger rule), the
  other IPL parts re-recorded for the clock lines alone, and
  `direct_kernel` given the new answers' edges and errors (377 commands,
  14 events). 9 tapes, all equal on the three benches.
- **Goal@node(N) with N unbound** (decided 2026-11-24 by the session
  lead: follow VPIM, which KLIC agrees with; implemented, `lockstep_tproc.py`,
  labelled "carried over from VPIM, agreeing with KLIC; the PIM/m
  firmware's behaviour is not held"). The readings, as recorded:
  `Goal@node(N)` with N unbound: the cluster number comes from a pool's
  answer in the same clause body, so on every boot the number is
  unbound when the goal is made, and refusing cannot be the machine's
  behaviour. VPIM, PIM's own virtual machine (`vpim.tar.Z`,
  `src/interpreter/klb_fork.psl.c` `klb_enqueue_to_processor`, its
  comment at lines 406-447, EUC Japanese): when Rpe is unbound, (1)
  the goal's arguments are made a vector, (2) the goal record is
  reclaimed, (3) a D-code goal `dcode_enqueue_processor(Processor,
  Code, Argv) :- integer(Processor) | dcode_apply(Code,Argv)@processor
  (Processor)` is made and hooked on Rpe: the goal WAITS for the
  number. KLIC agrees (`runtime/sched.c` `enqueue_throw_goal`, 267-330:
  a goal of `wait_penum_preds` waits for the node number). PDSS, a
  single processor, drops the number at compile time
  (`compiler/outp.kl1`:360-363: `enqueue_to_processor` and
  `enqueue_to_node` become `enqueue_goal`), which would let a later
  non-zero number pass silently. The VPIM reading is a parked goal of
  a new stub on both models (`asm/pimm_stubs.py` `TO_PROCESSOR`); the
  stubs were appended, so no earlier stub moved and no pin changed.

What the source says comes next (READ, not run; to be confirmed by
the run once guard `multiply` exists; the build switches of the
held object were not checked):

1. (CONFIRMED by the run, in the order 7, then 5 down to 0.) The bus
   scan sends TEST UNIT READY to each unit 0-7 except its own,
   6 (`scsi_where`'s answer). That is `scsi_man.kl1`:198-216 and
   `test_unit_ready/7` (218-227), with the CDB from
   `scsi_common.kl1`:35-42. A unit that answers gets an INQUIRY:
   CDB `12 00 00 00 ff`, 255 bytes in (`scsi_common.kl1`:60-70,
   `scsi#inquiry_data_max` 255, `macro/pimos/scsi/scsi.vmac`:42). The
   device type must be 3, processor (`scsi.vmac`:82,
   `scsi_man.kl1`:409-411). `fep.py` today refuses every unit but 7
   and every CDB but TEST UNIT READY, SEND and RECEIVE. The answer for
   an absent unit is a choice about the lost built-in, not about the
   FEP. In the source, a completion code with bit 3 set is `no_status`
   (`scsi_common.kl1`:197-199), and the unit is then skipped
   (`test_unit_ready/7`'s last clause).
2. `scsi_fep:create/2` (`bios/fep_module/scsi_fep.kl1`) uses device
   ids from 16 (`create(16, ...)`, line 23), not the IPL's 0. It makes
   its two packet buffers as long as `scsi_manager`'s `get_info`
   answer, `normal(8, 16384)` (`scsi_man.kl1`:138-141): 16,384 bytes,
   not `scsi_init`'s 16,000. Its receiver keeps one RECEIVE
   outstanding at all times (lines 476-558). It leaves a received
   string 8-bit (`str8_to_msg3`, 606-611), with no widening as in the
   IPL. It sends `{-1, 80}` (`fep#terminate`) when its stream closes
   (232-235).
3. The first device messages, by `bios.kl1`:383-394
   (`create_os_device1/2`): the console is a dummy that sends nothing
   (`bios/boot/console.kl1`). The system timer
   (`bios/boot/sysTman.kl1`) either uses `system_timer`/`current_node`
   or, for the boot FEP timer, `timer:create/3`
   (`bios/boot/timer.kl1`): `fep#create` then on_after, that is
   `{Id, 310, Node, 0, 0}` `create_timer` (`time_dvc.kl1`:34) and
   `{Id, 303, Count}`. The syslog is opened with
   `{Id, 203, Node, 0, 0, "pimos:pimos.syslog"}` `append_open`
   (`bios/boot/syslog.kl1`:33, `file_dvc.kl1`:39), then `putb` (111).
   This is not the plan's expected "`conf_dvc` first". A `normal`
   reply must carry exactly the results the caller's vector has
   (`fep_utility:set_value/2`, `fep_util.kl1`), or the results are set
   to `fep#nil`.

`pimfep.ptf` was not needed for a FEP message yet: the commands met so
far are SCSI ones (above). What was extracted for the next run
(`python3 asm/ptfdump.py pimfep CLASS`):

- `pimos_scsi_front_end`: version "V0.45", "14-Jan-94", comment
  "mkdir/rmdir, all_device_end", title "PIM-FEP".
- The string literals of `pimos_fep_superviser` (log and menu texts,
  "pimos:pimfep.image") and of `scsi_stream` (its error texts).
- No buffer size, configuration answer or time was found among
  `pimos_file`, `pimos_timer`, `scsi_stream` and `pimscsi_fep`'s
  literals. Their large integers, 1001-1265 and 33950, are not yet
  read.

### 1.5 Feasibility, effort, order

- **Feasibility: done as a prototype, mechanical to finish.**
- **Effort to finish:** (a) a `.sav` front end for `kl1decomp.py`
  (the container is already parsed by `unlsav.py`; needs labels and
  the external-call form), so the 502 object modules can be read the
  same way; (b) checking clause *contents* against source
  automatically (parse source clauses to the same normal form;
  today only counts are compared); (c) an executable check: run a
  decompiled predicate's clauses and its object code on the same
  inputs in `ref/pimm/pimm.py`. Nothing has to be found.
- **Unblocks:** C2 is now specified from the IPL's side (1.3, 1.4);
  B2's loader (`ipl_module`, `ipl_link_table`, `ipl_loader`: 70
  predicates, readable, not yet read through); C3 (the atom-number
  protocol, step 10).
- **Not determined:** the buffer size `scsi_init` returns on the
  machine; the unit of `getb`'s count; `string_operation`'s
  sub-operation 3 (used as a substring copy; argument order read off
  the uses, not settled); what `scsi_init`'s first two results must
  be (the object is passed back to `scsi_command`; the second is
  ignored).

## 2. The 20 `.sav` object files against the held source

MEASURED with `python3 asm/savsrc.py` (predicate heads of every module
against the clauses of the source file declaring the same module).

- **Version.** Each base file's comment decodes as `PIMM <SET>
  :3.600:25-Nov-93`; the source's `kernel/init/version.kl1` says `"3.600"`,
  `"20-May-93"` (READ). The patch files carry no comment and are dated
  1994-05-12 in the archive. *Note 2026-11-23: both dates are in the
  objects, and they belong to two different things. "25-Nov-93" is
  each base file's comment, once in each of the eight base `.sav`.
  "20-May-93" is the string constant of `pimos_version:date/1`, once,
  in `pimm_kernel360E.sav`. Both were found by searching the files for
  the dates as two-byte JIS strings, and when `pim:go/4` runs on the
  reference model it prints "PIMOS V 3.600 20-May-93"
  (`ref/pimm/longrun_ipl.py --reference --go`). So the compiled version
  module agrees with the held source. 25-Nov-93 is probably the date
  the sets were built or unloaded (INFERENCE).*
- **Coverage.** 502 modules; 501 have a source module of the same
  name (the exception is `ifdef_filter`, 91 predicates, in
  `library`). 12,120 predicates excluding 224 compiler-made `$` ones.

| Object predicates | Count | Explanation |
|---|---|---|
| same name and arity in the source module | 8,839 (72.9%) | |
| same name, other arity | 1,114 | `:- local_implicit` / `-->` clauses: the compiler adds arguments (`kl1cmp_optimize`: `optimize1/1` in source, `optimize1/5` and `/7` in object) |
| name starts with `+` | 719 | request filters generated from protocol descriptions (`genRfil.kl1` style) |
| other | 1,357 | mostly the same generated filters and the macro modules (`.mac` files the crude reader does not parse); not classified further |
| in `ifdef_filter` | 91 | no source module |

- 360 modules have every object predicate in source; 344 have
  identical predicate sets. In `bios` all 473 predicates are in
  source.
- **Depth.** This compares predicate *names*, not code. No `.sav`
  module was decompiled and compared clause by clause (1.5 (a)).

**The patches, and what the source is** (`python3 asm/savsrc.py
--patches`). 24 patch modules in 12 files; 22 replace a module of a
base file, 2 are new (`mkdir`, `rmdir`).

| Where base and patch differ in predicate set | patch in source | base in source |
|---|---|---|
| `fep_server` (fepsv) | 36 of 36 | 28 of 33 |
| `hasher` (hash) | 9 of 9 | 9 of 10 |
| `listener_cmd_directory` (lis) | 21 of 21 | 19 of 22 |
| `hmonitor`, `rmonitor`, `xhmonitor`, `xrmonitor` (newpg) | 20/20, 21/21, 23/23, 23/23 | 10/20, 11/21, 16/23, 16/23 |
| `x_profile_tcpip` (newpg) | 32 of 32 | 28 of 32 |

- **The held source is the patched text.** Wherever a patch changes a
  module's predicates, the source has the patch's set and not the
  base's. INFERENCE: `pimos.tar.Z` `src/` is the May 1994 state, so
  for a patched module the *patch* `.sav` is the object of the held
  source, and the base module is older.
- 13 patch modules have the same predicate set as their base and
  differ in instruction count by 0 to 83 (`scsi_fep` 1,840 to 1,838;
  `telnet_session` 4,831 to 4,865); two are identical in both
  (`kl1_library_variable_pool`, and `kl1cmp_macro_driver` in
  `patch_driver`; the same module is patched again by `patch_modu`,
  10,853 to 10,907). `filereq_filter` (mkdir) gains 3 generated
  predicates.
- `pimos_core` (macro) has no parsed source predicates either way
  (`.mac`).
- Three patches touch the front-end path: `fepsv`, `scsifep`, `mkdir`
  (which replaces `fep_directory_device` and
  `fep_file_request_device` of `bios`).

**Feasibility: done** at predicate-set depth. **Effort for
instruction depth:** 1.5 (a), then a clause-shape diff over 502
modules. **Buys:** evidence that source is the oracle for the
loaded system (with the patches applied last, as `pimos.ipl` orders
them), and the warning that it is *not* for the IPL image (1.1).

## 3. The Pseudo PIM/m microcode

State of knowledge is in `pseudo_pimm_microcode.md` (under edit by
another agent; READ 2026-11-20, sections "Answer in brief", 4, 6,
13-20) and `literature_gaps.md` Appendix C. Not re-derived here.

*Who ran what.* Sections 3 and 4 were probed by a second agent of
this session, which wrote `ptfdump.py`. Re-run afterwards by the
author of this note: `ptfdump.py --check`, `--opcodes`, the package
and `pimfep` class listings, `pimmutil rassy` with and without
`--pairs`, and the command-code comparison of 4.3. Everything else
marked MEASURED in sections 3 and 4 is that agent's run, reported and
not repeated: the microcode sizes, the header and call-target counts
of 4.1, the `sysidat` / `pimm.MEkbn` identity, the opcode readings
of 4.2, the hash-table keys and per-class figures of 4.3.

**Size** (MEASURED: `asm/psdpim.py`, `asm/mekbn.py --check` passes,
`--entries`): the KL1 microprogram is image 2 of `pimm.MEkbn`, 26,624
addresses, 18,343 non-zero 64-bit words; 324 populated KL1 decode
entries are its instruction entry points. Image 1 (22,528 addresses,
17,496 non-zero) is identical to `syspsi` `0..57ff`, the KL0 side.
Subroutines are not counted in the doc (222 call sites lead to a
return).

**How much of the word is understood** (INFERENCE, a tally of the
doc's statements, not a measurement): 55 of 64 bit positions have at
least one verified use; about 23 of 64 have every value characterised
(JMPF, the 16-bit EM, the three memory strobes, bit 57). Untouched:
bit 63, SD2 38-37, ALF 28-26, 18, 17-16, all condition codes, most
register numbers. Field boundaries are TR-733 fig. 4's geometry,
confirmed for JMPF and EM only. *Corrected 2026-11-23: the
boundaries are now Nakashima's Fig. 3-25 (`psi_microword.md` sections
3 and 7; `pim_architecture.md` section 5): bit 63 is DBGF (zero in
99.6%), ALF is 28-27 with 0 add, 1 subtract and EM2 the operation for
2 and 3 (`rassy`'s ALU table below, confirmed at the `and`, `or`,
`shift_left`, `shift_right` entries), JMPF is 26-23, 18 is MCF, 17-16
TGIF. Still uncharacterised: CNDF's conditions, SD2F and AS2F beyond
`rassy`'s values, MCF, TGIF 3, JMPF's bit 26.*

**New in this probe: the firmware's reverse assembler is in the
archive** (MEASURED, `python3 asm/ptfdump.py pimmutil rassy`).
`INSTALL.DIR/pimmutil.ptf` class `rassy`: 15,713 cells, 98 predicates,
one per field with TR-733's names (`ccf dstf sc1f sc2f sd1f sd2f
as1f_and_as2f as2f adf alf jmpf cndf mcf tgif` and a `set_up_*`
extractor each), with the string "version 1.3 (5-June-1989 by MTC
KATAYAMA)" (the second agent reported "1.4 (15-June-1989 by
A.KATAYAMA)"; only the 1.3 string was found on re-reading). *Checked
2026-11-23: `asm/ptfdump.py pimmutil CLASS` over all 51 classes of
`pimmutil` gives one version string, "version 1.3 (5-June-1989 by MTC
KATAYAMA)", in `rassy`. The 1.4 report is not borne out by the file;
the other `.ptf` packages were not searched.*
That it is this processor's format is INFERENCE from its vocabulary:
`pipeline_cancel`, `ic_trap`, `dc_trap_d`, `KL1F`, `GMI`, `MRP`,
`SUSPF`, `CGCF`, and the KL1 tag names `into` = `00` .. `goal` = `3c`
(which also gives the `GOAL` tag's value, open in
`pseudo_pimm_firmware.md`).

Its clause heads and constants already give value tables, before any
KL0 disassembler (`--pairs`; which predicate each run of pairs belongs
to was assigned by reading the listing, not by a tool):

| Field | Values |
|---|---|
| source to adder (`sd1f`, `adf`) | 0 nop, 1 xr, 2 yr (`adf`), 4 mdr1, 5 mdr2, 6 mar1, 7 mar2 |
| second source (`sd2f`, `as2f`) | 0 nop/0, 1 yr, 2 mdr1, 3 mdr2 |
| `ccf` | 1 wait_mdr1, 2 wait_mdr2, 4 wait, 5 undo, 6 reset_TRB, 15 cancel |
| register file | 0 cgp, 1 ap, 2 cpr, 3 cfpp, 4 gsp, 5 crr, 6 ccc, 7 ssp, 8 sst, 9 fvp, 10 flp, 11 fgp, 12 fwep, 13 fwip, 14 rcnt, 15 hp, 16-30 wr10-wr1e, 31 pstr |
| second bank | 0 dr/nop, 1 sr, 2 gr, 3 lc, 4 pc, 5 ir, 6 rfar, 7 rvfr |
| special registers | 8 alf_cc, 9 sw, 10 refr, 12 tdar, 16 jr, 17 mstkar, 18 mstkdr, 19 mstk, 20 mpc, 24-27 wcs0-3, 28/29 gevc_low/high, 30 mcr, 31 msr, 32 bpr, 33 imskr, 34 istr, 36 dpt_refr, 49 edr, 54 adr_refr, 55 adr_abr |
| ALU | 0 +, 2 add_with_carry, 3 add_with_one, 4 -, 5 reverse_sub, 6 sub_with_carry, 7 sub_with_one, 8 and, 9 or, 10 pass_as2, 11 xor, 12 shift_left, 13 shift_left_rotate, 14 shift_right_32m, 15 shift_right_arithmetic |
| memory commands (constants; numbering not recovered) | read / write `marN mdrN`, with `++`; `write_stack ++`; `unify_write`; `write_byte`; `write_hword`; `read_TRB_top`; `exec_misc_read/write`; `set_misc_command` |
| conditions (constants; numbering not recovered) | alf_zero, alf_sign, alf_carry, alf_overflow, alf_same_tag, alf_equal, alf_less, alf_high, alf_less_zero, over_flow, less, excond_0/1, lc_zero, branch_condition, mm_trap, sw00-02, CGCF, SUSPF, exsw00-02, micro_trap, slit_check, PMPF, non_KL0, GMI, KL1F, MRP, COL, interrupt, interrupt_all, trcmd, csbrk, ic_trap, dc_trap_d, dc_trap_e, ovf_trap |
| dispatch | `case_tag_setup mdrN k` (k 0-7), `case_gc_setup mdrN`, `eop`, `return`, `goto jr`, operand extraction `ir/8`, `ir/16`, `ir/24`, signed forms |

- Agreement with the other agent's independent fit: `mekbn.py` has
  `XR, MDR1, MDR2, MAR1, MAR2 = 1, 4, 5, 6, 7` and `SRC_YR = 1`.
- Possible conflict, not resolved: `rassy`'s `ccf` is a value table;
  the microcode doc reads CCF as separate strobe bits.
- Not recovered: the bit positions (they are in the `set_up_*` code),
  the numbering of memory commands and conditions, which table applies
  in which mode. `set_mnemonic_file` loads an optional label file that
  is not held.
- A second reverse assembler, `pimmutil##csp_micro_reverse_assembler_main`
  (17,281 cells; `am293`, `i_mode`), is a different format, INFERENCE
  the PSI-II / Multi-PSI one.
- Also held as compiled ESP in `pimmcsp`: `csp_goal_record_inspector`
  (989 cells), `csp_goal_queue_inspector` (869), `csp_goal_converter`
  (1,947), `csp_susp_record_inspector` (341),
  `csp_suspend_stack_inspector` (540), `csp_fp_record_inspector`
  (3,057). The goal-record layout that `pseudo_pimm_firmware.md` says
  "is in the compiled code" is in the first three.

**What a full microcode disassembler still needs:** bit positions and
value sets for ALF, the condition field, SD2, bits 63, 18, 17-16; the
register maps and their bank selection; the memory-command numbering. *(2026-11-23: the bit positions are now
Nakashima's Fig. 3-25, and ALF's values are read (above); the value
sets of CNDF, SD2F, MCF and TGIF 3 are still needed.)*
Two routes: (1) decompile `rassy` (15,713 cells; needs component 4's
KL0 disassembler), which is the authority; (2) go on fitting in
`mekbn.py`, now seeded with the tables above. No held report gives
the value tables: TR-733 fig. 4 has names and widths; TM-849
(Microlint), TM-212 (ZEUS) and TM-850 are listed unread in
`literature_gaps.md` and might.

**Feasibility: research today; mechanical once `rassy` is read.**
Then 18,343 words and 324 entry points disassemble by table.
**Buys:** authoritative semantics and step counts for every KL1-B
instruction; goal and suspension record layouts (B6, B7); the
priority mechanism (B4); `save`/`restore` (B1); MRB and the collector
(B8). None is on the shortest path to R4; all of it changes the
runtime the path is built on, and it is the only source of cycle
counts.

## 4. The compiled ESP packages (`.ptf`)

### 4.1 Container (MEASURED, `python3 asm/ptfdump.py --check`: PASS)

All six files (five in `psdpim` `INSTALL.DIR`, and
`pimosobj`'s `object/paragraph.ptf`) are one format, 16-bit
big-endian words:

- File: `0001`, package name, attributes (`using_env` = simpos,
  `version`, `lversion` = lib50, `release`), class names, then one
  record per class.
- Class record: length; `version` and `class_id` (`pkg##class`); a
  symbol table of two-byte JIS names; a body `1b00, L, h1, h2`, the
  cells `h2..L-1`, and a trailer of terms.
- Cells: `20xx`/`21xx` + 32 bits = an instruction of class 0 / 1
  (opcode in the top byte, three operand bytes: the shape of KL1-B);
  `60rr sym` an instruction with an atom; `01aa sym` an atom or a
  method selector of arity aa; `0000` integer; `0a00` float; `2400`
  predicate head (`arity << 24 | offset`); `a000 ...` a hash table.
- Predicate: name, `kind << 8 | arity`, head, 0, code.
- Trailer: class links, method vectors, slot (attribute) names,
  superclasses, used classes, constants. INFERENCE that it fills
  cells `0..h2-1`: in `scsi_fep_macro` 105 constant references land
  on cells 15..119, all below `h2` = 120.

| Check | Result |
|---|---|
| classes whose cells land exactly on `L` | 554 of 554 (2026-11-24, once a hash table is counted as `mask+1 + 2*keys + 2` cells, `ptfdump.table_span`; with the table's size word + 1, as before, 552, and the two `pimmcsp` classes overshot) |
| predicate headers with code two cells after the head | 9,815 of 9,815 (2026-11-24, same numbering; the earlier "8,230 of 9,839, 1,609 not understood" was the size-word numbering drifting after hash tables) |
| header kinds | `11` local 3,609; `12` local 2,205; `35` instance method 3,256; `25` class method 589; the other five kinds 156 (`22` 15, `27` 16, `32` 57, `36` 22, `37` 46; named in `simpos/layers/FORMATS.md` §2). Recounted 2026-11-24 with the fixed numbering; before it, 3,559 and 1,904 |
| local call target = cell + 2 + signed 16 bits | every one lands on a head (2026-11-24): opcode `60` 5,390 of 5,390, `61` 2,646 of 2,646, `62` 1,916 of 1,916 (before the numbering fix: 4,131/5,214, 1,949/2,556, 1,384/1,851) |

| Package | Classes | Cells | Class-0 instr. | Class-1 instr. | Symbols |
|---|---|---|---|---|---|
| `pimfep` | 47 | 28,935 | 18,658 | 1,765 | 2,747 |
| `pimscsi` | 24 | 12,977 | 8,311 | 1,147 | 1,086 |
| `pimmcsp` | 281 | 156,090 | 103,403 | 9,158 | 14,217 |
| `pimmutil` | 51 | 54,615 | 40,312 | 3,223 | 3,085 |
| `mpsicspR` | 30 | 15,616 | 9,629 | 723 | 2,124 |
| `paragraph` | 121 | 93,582 | 56,580 | 14,804 | 5,705 |

(`icot_software_survey.md` says 23 classes for `pimscsi` and 50 for
`pimmutil`; the files hold 24 and 51.) *Note 2026-11-23: for `pimscsi`
the survey's own text says "23 classes ... plus a `cmt` class", which
makes 24, so there is no disagreement there. For `pimmutil`, 50 was an
undercount; the survey is corrected to 51 in place.*

### 4.2 Is the instruction encoding identifiable

- **The opcode set: yes** (MEASURED, `ptfdump.py --opcodes`).
  `PMPSI.DIR/sysidat` is the KL0 decode table, 1,024 entries indexed
  by class x 256 + opcode, 214 populated in class 0 and 241 in class
  1. Every opcode the six packages use has an entry: 236,893 class-0
  and 30,820 class-1 instructions (2026-11-24, fixed numbering; 228,536 and 30,052 before), 101 and 111 distinct opcodes, none
  missing.
- `sysidat`'s classes 0-1 are the table at the head of `pimm.MEkbn`'s
  classes 0-1 (496 of 512 entries byte-identical): the "PMI"/"BLT"
  classes `pseudo_pimm_firmware.md` could not match are the KL0
  instructions.
- **Dead end:** the task's suggestion that `syspsi` holds the table.
  `syspsi`, `sysinit` and `sysidat` are 8-byte words after a 256-byte
  header (32,768, 8,286 and 1,040 words), not the 5-byte `.kbn` words
  `psdpim.words()` assumes; read that way `syspsi` shows spurious
  "entries". `syspsi` is the 32K control store; the table is
  `sysidat`.
- **The opcode names: not from a document we hold.**
  `docs/nonlocal/tr` and `tm` hold TR-564, TR-742, TR-799, TM-1074,
  TM-1159, hardware papers. `literature_gaps.md` names the PSI-II
  sources: TR-265 (instruction word: class 2 bits, code 8, operand 24,
  the shape seen here), TM-444 (KL0 on PSI-II), TM-261/353/354
  (firmware; titles only). None was opened in this probe.
- **Names from known plaintext: started.** `paragraph.ptf` is compiled
  ESP whose source is held (`pimos.tar.Z`
  `src_util/paragraph/*.esp`, 83 files, 18,261 lines, against 121
  classes). Not the identical version (`paragraph_version` is "3500"
  in the object, "3200" in `version.esp`), but classes pair up.
  Readings so far (INFERENCE, one to three witnesses each):

| Opcode | Reading | Witness |
|---|---|---|
| `f0` | proceed | `:kill(Obj):-!;` compiles to `dc 01`, `f0` |
| `dc n` / `dd` | neck cut, arity n / with environment | same |
| `73` + selector, `74` + selector | method call / last call | `:create(...):-!, :new(Class,Obj)` gives `74 01 02` `new/2` |
| `60`, `61`, `62` | local call / execute | target rule above |
| `27 r, int16` | get_integer | every recovered table |
| `60rr` atom cell | get atom (rr < `80`) / put atom | tables |
| `29 r, rel` | get constant from the pool | `Res = "normal"` |
| `5f n`, `6e` | allocate / deallocate | bracket multi-call bodies |
| `20`, `a0`-`a4` | get/put variable/value family | not separated |
| class 1 `27` | slot access | `Class!version` |

### 4.3 The front end's side of the protocol (`pimfep.ptf`)

**Command codes** (MEASURED, re-run: `ptfdump.py pimfep
fep_command_code_table --pairs` against `pimos.vmac`, 104 `fep#`
definitions outside comments). `fep_command_code_table:convert` holds
102 code/name pairs, 100 distinct names: **98 have the number PIMOS
gives them, none differs.** FEP only: `creation_fail` 900,
`all_device_end` 901, `remote_echo_check` 902, `device_end` 903.
PIMOS names not in that table: `window` 100, `listing` 230, `deleted`
234, `next_filename` 236, `symbol` 500, `remote_socket` 704, and the
two packet flags. A second table, `scsi_fep_macro:expand/7` (the
FEP's own `fep#Name` expander), has 105 entries with the same
integers; its names as listed below, and "99 of 105 equal to
`pimos.vmac`, `getl_without_echo` 112 and `kill_window` 60 FEP-only",
are the second agent's reading, not re-run.

```
nil=0 normal=1 eod=2 control_c=3 attention=3 continue=4 abnormal=5 aborted=6 yes=7 no=8
wake_up=9 disconnected=10 end=11 reset=50 next_attention=51 close=60 abort=70 terminate=80
window=100 create=101 create_with_buffer=102 get_max_size=103 create_window=104
getl=110 putb=111 flush=112 beep=113 ungetb=114 set_size=120 set_inside_size=121
get_inside_size=122 set_position_by_mouse=123 set_position=124 get_position=125
reshape_by_mouse=126 reshape=127 set_title=130 get_title=131 set_font=132 get_font=133
select_buffer=140 activate=141 deactivate=142 show=143 hide=144 clear=145 buffer_name=146
file=200 read_open=201 write_open=202 append_open=203 directory=204 make_directory=205
getb=210 end_of_file=220 pathname=221 attributes=222 delete=231 undelete=232 purge=233
expunge=235 listing_all=237 deleted_all=238 kill=239 fep_attributes=240
timer=300 get_count=301 on_at=302 on_after=303 get_date_time=304 create_timer=310
ipl=400 string_io=600 create_string_io=601 io=620
remote_window=700 remote_file=701 remote_timer=702 remote_string_io=703 node_name=710
socket=800 create_socket=801 bind=802 listen=803 accept=804 connect=805
set_socket_option=806 so_debug=807 so_reuseaddr=808 so_keepalive=809 send_timeout=810
receive_timeout=811 connect_hostname=812 creation_fail=900 all_device_end=901
remote_echo_check=902 device_end=903 packet_last=0 packet_continued=1
getl_without_echo=112 kill_window=60 jiskanji=0 euc=1 jis=2 sjis=3
```

**Dispatch** (MEASURED: hash-table keys; INFERENCE: what they mean).
`pimos_scsi_front_end` (2,437 cells; 4 class, 31 instance, 8 local
predicates) has the dispatcher, local `command_type/2` (1,591 cells).
Its hash keys are 103, 240, 70, 80, 901, 902 and the ten
device-creating commands 104, 102, 201-205, 310, 601, 801, plus the
atoms `error`, `network_error`. `refute_command/3` sends
`disassemble/3`, `get_device_id/3`, `get_at/5`, `assemble/3`, `put/2`:
a message is taken apart, routed by device id through
`fep_device_table`, and the reply assembled. Everything else is
dispatched by the device object (ESP method call on the command), so
the per-device command set is the method list of the device class.

**IPL-time service.** No class tests for 400 or 500 outside the two
tables; `symbol` is not a symbol in the package. Together with 1.4
(the IPL never sends them): the boot uses `read_open` and `getb` on a
`pimos_file`, nothing special. (A reading of what is absent, on both
sides; neither side was executed.) *(Note 2026-11-23: the IPL side has
since been executed on the reference model, `ref/pimm/ref_scsi.py`
against our `ref/pimm/fep.py`, which raises on any request it does not
serve. See §1.4, "Run". The FEP side is still a reading.)*

**Message framing.** `fep_message_assembler` (503 cells; class
methods `get_command/3`, `get_device_id/3`, `connection_flag/3`,
`assemble/3`, `disassemble/3`, `divide_message/4`, `append_message/3`,
`pad_string/2`; locals `create_argument_string_list/5`,
`take_argument/5`, `padding/5`, `divide_message_loop/4`). The names
match the layout of 1.4 (device id, a connection flag, a command,
arguments, padding, division into pieces); the code was not read, so
the layout itself is established from the PIMOS side only.

**Service classes** (MEASURED; predicates class/instance/local,
cells):

| Class | Preds | Cells | Methods seen |
|---|---|---|---|
| `pimos_file` | 4/18/15 | 1,157 | class `create/9`, `read_open/10`, `write_open/10`, `append_open/10`; instance `getb/4`, `putb/4`, `ungetb/4`, `end_of_file/3`, `close/3`, `flush/3`, `pathname/3`, `attributes/3` |
| `pimos_directory` | 2/13/3 | 516 | |
| `pimos_timer` | 1/8/3 | 349 | `create_timer/9`, `on_after`, `on_at`, `get_count`, `get_date_time`, `abort_timer` |
| `pimos_window`, `_process`, `_editor`, `pimos_standard_io_window` | 1/7/0, 3/13/3, 0/29/25, 0/7/22 | 218, 456, 1,394, 762 | window keys in `pimos_standard_io_window`: 104, 60, 130, 124, 121, 141, 142, 111, 110, 112, 145 |
| `as_pimos_string_io_device`, `pimos_string_io_invoker` | 0/10/5, 1/0/3 | 237, 191 | |
| `as_pimos_device` (base) | 2/19/8 | 557 | |
| `pimos_tcpip_socket` | 1/41/15 | 1,518 | |
| `scsi_stream`, `fep_scsi_output`, `pseudo_scsi_fep`, `pimscsi_fep` | 1/15/26, 1/11/7, 0/1/2, 1/4/1 | 1,296, 438, 177, 201 | transport |
| `pimfep_message_receiver`, `_sender` | 1/16/11, 1/18/15 | 594, 959 | |
| `fep_device_table` | 0/12/7 | 499 | |

`python3 asm/ptfdump.py pimfep CLASS` lists every predicate with the
selectors it sends. The call graph is recoverable as predicate to
selector/arity and predicate to local predicate; which class receives
a send is not (ESP dispatches on the object). On the Pseudo PIM/m the
link itself is in `pimscsi`: `pseudo_scsi_handler` has
`send_packet_to_fep`, `send_buffering_packet_to_PE`,
`change_packet_16_to_8`, `write_packet`.

### 4.4 Feasibility, effort

- **Container, class and method listing, fact tables: done.**
- **KL0 disassembler: mechanical with a research tail.** To build:
  names and operand formats for 212 opcodes (101 class 0, 111 class
  1). Material: the `paragraph` pair (71,384 instructions with
  source), and the microcode entry of each opcode as a tie-breaker.
  The ten commonest class-0 opcodes (`a2 20 73 a0 a4 a7 a3 27 5f f0`)
  are 121,668 of 236,893 uses, so a few dozen paired clauses settle
  most of the volume (INFERENCE); the 111 built-in opcodes are the
  tail, each needing a source witness or a document (TM-444, TR-265,
  TM-261/353/354; a KL0 built-in manual is catalogued and not
  obtained, `literature_gaps.md`). Also to settle: `h1`. (The 1,609
  "irregular headers" were a cell-numbering error, fixed 2026-11-24, 4.1;
  the trailer is decoded by `psi/librarian.py`.)
- **Decompiling the FEP services for a faithful stand-in: mechanical
  after that.** For boot: `fep_message_assembler` (503 cells),
  `pimos_scsi_front_end` `command_type/2` + `refute_command/3`
  (1,708), `pimos_file` (1,157), `scsi_stream` (1,296): about 4,700
  cells, each checkable against the PIMOS client source and section
  1.4. All services: 47 classes, 28,935 cells. The SIMPOS classes
  they call (`simpos##...`) are not held, so a decompiled FEP is a
  specification to re-implement against, not something to run.
- **Unblocks:** C2 and C4 from the server's side; the command numbers
  are settled now from both sides. For R4 it adds nothing section 1
  does not already give. It is the route to component 3 (`rassy`) and
  to the goal-record inspectors.

## 5. Other binary-only items

| Item | What it is | Status |
|---|---|---|
| `object/pimm_ipl.ldb` (17,340 B) | two-byte JIS **text**, 777 lines: the image's atom names, then per module its name, address, length, table address and public predicates (name, arity, address), then load, end and start addresses and `ipl boot 0` | MEASURED by decoding; readable, agrees with `kbndis.py` on the start (`E0001E81`); nothing to reverse |
| `object/pimm_ipl.sym` | text atom table | already used by `kbndis.py` |
| `object/paragraph.ptf` (1,020,476 B) | compiled ESP with held source | the known plaintext of section 4 |
| `PMPSI.DIR/syspsi` | 32,768 x 64-bit control store, KL0/SIMPOS microcode (by shape, the README's "KL0 and KL1 firmware" and INSTALL sending it to SIMPOS's `csp` directory: probable, not proven; no document names its role) | same job as component 3, larger; not needed for PIMOS |
| `PMPSI.DIR/sysidat` | KL0 decode table | read (4.2) |
| `PMPSI.DIR/sysinit` (8,286 words at `5000`) | not characterised | open |
| `FONT.DIR/*.font`, `csp.icon` | SIMPOS bitmap fonts and an icon | not examined; console cosmetics |
| `pimm_patch.com` | named by `boot.init`, **not in the archive** | cannot be recovered; `icot_software_survey.md` |

## 6. Recommended order

1. **Write the R4 front-end stand-in from sections 1.3 and 1.4.** No
   further reverse engineering needed. Check it by replaying the
   derived packets through the image's own `scsi_fep_module` once
   `scsi_command` exists in the model.
2. **Give `kl1decomp.py` a `.sav` front end** (two operand forms to
   add, 1.5 (a); nothing to find). Tells which `ipl_parameter` branch
   the bios was built with (1.3 step 11), lets the kernel's
   `scsi_fep` and `fep_server` patches be read as loaded, and makes
   source-versus-object comparison clause-deep.
3. **Name the KL0 opcodes from the `paragraph` pair** (the one
   open-ended item; the 30 commonest first).
4. **Decompile `pimmutil##rassy`**: the microinstruction format from
   its own tool. Hand the tables in section 3 to the microcode work
   now; they are usable as seeds before step 3 lands.
5. **Decompile the pimfep boot path** (about 4,700 cells), then the
   goal-record inspectors in `pimmcsp`, then the remaining services
   as R5-R6 need them.

## 7. Could not determine

- The buffer size `scsi_init` returns on the machine, and the unit of
  `getb`'s count (1.3).
- Which `ipl_parameter` branch `pimm_bios360E.sav` was built with
  (harmless either way, 1.3 step 11).
- Clause-level identity of any `.sav` module with its source.
- KL0 opcode names beyond the ten rows of 4.2; `h1`;
  the hash table's size word (the irregular headers and the two
  overshooting classes were a cell-numbering error, 4.1).
- The FEP's own message header code (names only).
- `rassy`'s bit positions and the numbering of its memory commands
  and conditions; whether its 1989 date matches the PIM/m chips in
  every field.
- What `sysinit` is.
- Dead ends recorded above: `syspsi` as a decode table (wrong word
  size); a TR for KL0 opcodes among the held PDFs (none).
