# SIMPOS system structure as the held ICOT reports state it

Scope: every SIMPOS, ESP or PSI report held in `pim/docs/nonlocal/lit/trtm/`. Citations take the form
`REPORT pNN`, where NN is the **PDF page index** of `trtm/<report>.pdf`, not the printed folio. Each
listing header gives the folio.

Transcriptions are in `listings/`. Per-report notes with fuller detail are in
`parts/<report>.structure.md`, and this file is a synthesis of them.

Labels used below:
- **TRANSLATION**: my rendering of Japanese text.
- **INFERENCE**: anything not stated in a report.

Each section separates **REIMPLEMENTABLE** material (printed precisely enough to code from) from
**SKETCHED** material (described only).

How each report was read:
- Read by eye at 300 dpi throughout: TM-100, TR-524, TR-283, TR-046, TR-061, TR-056, TR-059, TM-061,
  TM-065, TM-079, TM-125 and TM-126. For TR-046/056/059/061 the prose was read from OCR text and every
  code, table and figure page by eye.
- Read from OCR text, with figures and tables by eye: the remaining SIMPOS reports. Coverage is in
  `coverage.tsv`.

The papers themselves say their code is partial. For example, TM-100 p7: "Although we give several ESP
codes as examples, they are not complete."

---

## 0. Language substrate: ESP as SIMPOS uses it (REIMPLEMENTABLE at semantics level)

- **Class syntax.** The parts are, in order: nature (inheritance), class slots, class clauses,
  `instance`, instance slots, instance clauses, `local`, `end.` TM-065 also has a macro-bank part.
  Sources: TM-100 p4 (`listings/tm0100_p04.esp`), TM-065 p8, TM-079 p7 (Japanese).
- **Inheritance.** Clauses of the same predicate are OR'ed in nature-list order, and slots are merged.
  `*` in the nature list marks the class's own position. Sources: TM-061 p4, TM-100 p4.
- **Demons.** `before` and `after` demons are AND'ed around the primary predicate, as in Flavors.
  Sources: TM-100 p3, TM-065 p7-8. Printed use: `bounded_post_queue` (TM-100 p17-18), with_border and
  with_label (TM-065 p15).
- **Calls.**
  - Method call: `:m(Obj, ...)`; class method call: `:m(#class, ...)`; local predicates: plain Prolog.
  - Slot access: `Obj!slot`; slot assignment: `Obj!slot := V`.
  - Slot initialiser: `(slot := V :- Goal)`.
  - Qualified forms: `:class:method(...)` (used in TM-100 p16, `:channel:send`) and `pkg##class`
    (TM-388 pp93-94, OCR only).
- **Object representation.** An object is a KL0 heap vector. Element 0 is the code executed on an
  operation call, the remaining elements are slots, and the object pointer is the vector's address.
  Sources: TM-065 p6 Fig. 2.1, TR-055 p9-11.
- **Method lookup.** By name and arity at run time. Inheritance is analysed at linkage or registration
  time, and method call and slot access are in firmware. Sources: TR-285 p8, TM-100 p18, TM-125 p20-22.
- **KL0 features SIMPOS relies on:**
  - multi-level cut (catch/throw);
  - bind_hook (said to be unused in SIMPOS);
  - exception hook;
  - persistent alternatives;
  - strings and vectors;
  - hardware-register built-ins for the memory manager and device handlers.

  Sources: TR-086 p4, TR-285 p5-6.
- **Packages.** These are named only in the reports in scope, apart from the following:
  - TM-388 pp93-94 (OCR only) describes package environments such as `with_simpos`, which inherit the
    system package `simpos`.
  - TR-283 p5: a class is identified by its "class complete name" (package, class).

## 1. Layers -- the reports disagree, so each version is given

| Source | Layering as stated |
|---|---|
| TM-100 p4-5 Fig. 2.1 (`listings/tm0100_p05.txt`) | Programming system {Coordinator; Editor, Interpreter/Debugger, Librarian} / OS = I/O medium systems {Window, Network, File, Printer} / Supervisor {Process, Pool, Stream, World, Timer} / Kernel {Processor, Memory, Device} / Hardware |
| TM-065 p11 Fig. 3.1 | Same as TM-100, but "Library" for Librarian |
| TM-061 p6 Fig. 3.1 | Adds トランスデューサ (transducer) and has ライブラリアン (librarian); no Printer and no Timer |
| TR-055 p2, p6-7 | Kernel (processor, memory incl. GC, I/O device) / basic-constructs (supervisor: pools, streams, processes, worlds, channels, ports) / i/o medium (file, window, network) |
| TR-056 p4-5 | Kernel (hardware resources) / supervisor (software resources: pools, streams, processes, environments) / i/o medium systems |
| TR-057 p3, p5 | Kernel / supervisor / I/O media. The programming system is experts plus a coordinator |
| TR-086 p4 | A different split: a "kernel operating system" that *includes* the window, file and network systems, plus the programming system |
| TM-079 p4 (handwritten; `listings/tm0079_p04.txt`) | Tree. Supervisor gets 時計 (clock); kernel gets IPL |
| TM-143 p2 (1985, Japanese) | Five groups: kernel (processor, memory, device, IPL); supervisor (process, pool, stream, world, clock, remote object, kana-kanji, system tracer, situation); I/O media (window, file, network); programming system (coordinator, editor, transducer, librarian, interpreter/debugger); manipulators |
| TM-229 p3-4 (1986) | Kernel now includes GC and kana-kanji conversion in the keyboard handler. Supervisor = process, pool, stream, wildcard, directory, user management. I/O media add font, symbolizer, magnetic tape and printer |
| TR-714 p4 (PSI/UX, 1991) | Kernel I/O handlers and part of the I/O subsystem replaced by UNIX emulation; PS and applications keep object-code compatibility |

Points that are consistent across reports:
- The whole system, device handlers included, is written in ESP. Sources: TR-524 p3, TR-283 p3,
  TM-143 p6, TM-181 p3.
- Code size grew from about 90K lines (TR-086 p10, Oct 1984) to 145K lines / 960 classes (v1.5,
  TM-143 p6), 200K / 1,448 (v2.1, TM-181 p3) and 230K / 1,400 (TR-285 p5).
- The supervisor alone was 135 classes / 6,000 lines in 1984 (TR-056 p31).

## 2. Process model

**REIMPLEMENTABLE** (TM-100 p7-13, `listings/tm0100_p07..p13.esp`; TR-056 p17-21):

- **`process`.** Natures `with_link` (ready queue) and `waiting_frame` (stream wait queue). Class slots
  `ready_queue` and `instance_array`. The instance slots are listed in classes.tsv.
- **States.** running, ready, suspended, dormant (TM-100 p5, TR-056 p18). The status slot also allows
  `nil` (dead) and "(active) and some others" (TM-100 p8).
- **Creation.**
  - `:create(#process, P)` allocates a hardware context with `:create(#context, N, Stack, Ctx)`, and
    fails if hardware processes are exhausted.
  - The new process inherits `world` and `user` from its creator. It starts at priority 0 and
    sub_priority 0 with status dormant.
  - There is a hard limit of 63 processes, of which several are interrupt processes, leaving about 50
    for ordinary use (TR-056 p19, TR-055 p4-5, TR-086 p11, TR-524 p11).
- **Activation.** `:activate(P, Program)` sets the context entry point from the program, makes the
  process ready and enqueues it. TR-056 p18 gives `:activate(Process, Program, Goal)` with 3 arguments;
  this is a VARIANT against TM-100's 2.
- **Suspend and resume.** Implemented as a reason set: a list of reasons plus a fast path for one
  stream reason. A process is ready only when both are clear. Every transition is bracketed by
  `:inhibit_interrupt(#process)` / `:allow_interrupt(#process)`, with nesting counted in `mask_count`.
- **Programs.**
  - A program is an instance of a class inheriting `as_program` (full listing printed, TM-100 p11).
  - Each process has an invocation stack. `:invoke` = assign, then `:goal`, then resign. The process
    dies when its stack empties.
  - Usage pattern: `:create(#parrot, Prog), :create(#process, P), :activate(P, Prog)` (TM-100 p11,
    TM-225 p6).
- **Interrupt processes.**
  - Trap handlers, device handlers and the garbage collector are interrupt processes. They are
    dispatched by hardware, not by the supervisor (TM-100 p6, TR-056 p20).
  - `interrupt_process` overrides `:resume` / `:suspend` (TM-100 p12-13), so stream code need not
    care which kind of process it is waking.

**SKETCHED:**
- **Scheduling policy.** Priority "Corresponds to interrupt level" (TM-100 p8). Scheduling is
  "non-preemptive, not time slicing" (TR-524 p8). No dispatcher code, ready-queue discipline,
  time-slice or sub_priority semantics are printed.
- **Interrupt-process internals.** The trap, release and allocate steps are elided ("...") in the
  print (TM-100 p12-13).
- **Process switch cost.** 20 ms falling to 2 ms (TM-100 p18), or 21 ms to 2 ms (TM-143 p8); 1 ms on
  PSI-II (TR-524 p29).
- **PCBs.** On PSI-II, process control blocks live in the firmware "System Area" (TM-444 p35, OCR
  only, not eyed).
- **Exceptions: situation and event** (TR-087 p9-10, TR-285 p10, TM-143 p2, TM-181 p5).
  - Each process has a situation stack of handlers, and an `event` class hierarchy covers error
    (warning, fatal, normal) and help.
  - Recovery options: resume, fail, return to a resumption point, or kill the process. An error menu
    offers them.
  - No method names are printed. TM-785 p3 shows such an error menu as text.

## 3. Memory, heap and GC (SKETCHED; mostly firmware)

- **Areas.** PSI has 256 areas, each a heap or a stack. A process needs control, local, global and
  trail stacks (TR-055 p4-5), plus a heap (TR-213 p4-5). There is logical-to-physical translation but
  no virtual memory and no paging to disk (TR-055 p4, TR-056 p6).
- **GC process** (TR-213 p4, Japanese, eyed; TRANSLATION):
  - It starts when a physical-page request finds no free page.
  - Stage 1 reclaims unused pages of shrunk stacks.
  - Stage 2 calls the built-in `collect-garbage(ProcessTable)`: microcoded mark and sliding
    compaction, per selected process.
  - This is the only GC policy described at the SIMPOS level.
- **Reclaim rules.** Heap is reclaimed only by GC, and the global stack only by backtracking
  (TM-143 p8). The system menu has a "garbage collection" item (TM-181 p3).
- **Not given:** the memory manager's classes, the `area` class (named in TM-065 p10), page
  sizes, and how areas are allocated per process.

## 4. Streams, pools, channels, ports, semaphores and events

**REIMPLEMENTABLE:**
- **`stream`** (TM-100 p14-15). FIFO; `:put` / `:get`; a get on an empty stream suspends the caller with
  reason `stream(S)`. The waiting queue and post queue are held as slots, not natures, and p14 explains
  why.
- **`channel`** (TM-100 p15). `:send(Ch, Msg, Sender)` / `:receive(Ch, Msg, Sender)`. Messages carry
  the reply channel. The post queue is a `post_queue_for_message`.
- **`port`** (TM-100 p16). A channel plus an `out_port` list. Send fans out copies of the message
  through a tap over that list.
- **`bounded_channel` / `bounded_post_queue`** (TM-100 p17-18). A semaphore guards the post queue
  through before and after demons.
- **`semaphore` and `event`** (TR-056 p13, bodies printed). A semaphore is a stream of the atom
  `token`. An event is post = put and wait = get.
- **Pools** (TR-056 p6-12, interfaces printed; `as_bucket` :get body and generic `tap` :get body
  printed):
  - `as_pool`; `sequence` with subclasses `array` and `list`;
  - `index`, built on `hash_array`; `sparse array`;
  - `bucket`, with path keys;
  - `tap`, for sequential access.
- **Stream and channel pools.** Multi-source get (TR-056 p16-17).

**SKETCHED:**
- Source and sink channels for keyboard and screen (TR-056 p17).
- The priority-stream variant (TM-100 p7, TR-056 p14).
- Bag, set and sorted sequence: "planned" (TR-056 p10).
- The hash function is not specified.

## 5. Environment: directories, worlds, library, global and permanent objects

**REIMPLEMENTABLE (interface level)** (TR-056 p21-28, TR-059 p20-28):

- **Per-process environment.** Each process has a program invocation, a library and a directory
  (TR-056 p22).
- **`directory`.** `:find` / `:bind` / `:remove`. The system root is held in a class slot of
  `directory` (the "universe", TR-057 p5): `:root(#directory, R)`.
- **Pathnames.**
  - `>A>B>C` resolves from the system root; `A>B` resolves in the process's world.
  - `:retrieve(#as_global_object, Obj, Path)`.
  - `:link(Volume, ">disk1>volume1")` grafts a volume's root directory file into the tree (TR-059
    p26-27).
- **`world`.** A sequence of directories; the first match wins (TR-056 p24-25).
  - Login-time logical names: `me:` = `>sys>user><login>` (TM-143 p3).
  - World aliases: `snoopy:humm.txt` (TR-524 p9).
- **`as_permanent_object`.**
  - Store and restore bodies are printed (TR-059 p22, `listings/TR-059_p22.esp`).
  - Each class supplies `:decode` (object to record) and `:encode` (record to object), naming as
    printed.
  - Records live in a per-class instance file (a table file). The `record_pointer` is file plus marker.
- **`directory_file`.** Name to record pointer: `:bind` / `:find` / `:replace` / `:rename`. A
  permanent directory is an in-memory cache of a directory file (TR-059 p23-28).

**SKETCHED:**
- `as_global_object` protection, profile, versions and locking: "still under consideration"
  (TR-056 p26-27).
- `user` and `group` classes: they "must be defined" (TR-056 p26).
- User management: ranks and passwords are described in TR-524 p15-18, but no classes are given.

## 6. File system

**REIMPLEMENTABLE (API and semantics):**
- **Files** (TR-059 p10-20; `listings/TR-059_p11..p19.esp`):
  - Mixin `as_file`. File kinds: binary, table, heap and index.
  - `:open/:create(#file, F, Name)`, `:close`, `:remove`.
  - Buffer: `:record_data`, `:data_size`, `:set_data_size`.
  - File marker: `:position`, `:set_position`, `:start_marker`, `:end_marker`.
  - Direct access: `:read`, `:write`, `:add`, `:delete`.
  - File tap: `:tap`, with tap `:read`, `:write`, `:move`, and so on.
  - Index buffer and index marker.
- **Classes `file` and `binary_file`, two editions** (TM-065 p12-13 and TM-061 p6-8; diffs in
  `listings/VARIANTS_tm0061_vs_tm0065.txt`):
  - Class slot `pool_of_files`.
  - Class methods `:create`, `:make` and `:open` are printed with bodies.
  - Instance-method bodies are elided ("...").
  - The real `file` also inherits `as_permanent_object`, `as_resource` and `with_lock` (TM-065 p13).
- **Distributed file system, 1987-89** (TR-524; the Appendix A source is `listings/tr0524_p37.esp` and
  `tr0524_p38.esp`):
  - Classes: `binary_file` (natures remote_binary_file, binary_file_accessor, local_binary_file,
    p_binary_file, logical_file, with_retrieval), `local_binary_file`, `logical_file`,
    `local_logical_file`, `binary_file_accessor`, `file_accessor`, `remote_binary_file` and `buffer`.
    Their bodies dispatch through `:g_call` → `:l_call` / `:r_call`.
  - Open modes: exclusive, input, output, shared. Request modes: suppress, immediate.
  - Normal and express message priorities; asynchronous `submit` / `wait` / `probe`.
  - Consistency semantics; the password and access-list capability algorithm (ranks super_U, super_A,
    super_N; rights `fdma` and `rwa`).
  - File names `name.ext.version`; global names `host::>sys>user>...` (TR-524 p9-18).
- **File manager topology** (TR-059 p28-32):
  - The file manager is a process. Files are `io_port`s connected to a manager channel held in a class
    slot.
  - Each device handler is an interrupt process with a handler channel. A volume is a device port.
  - Both are instantiated during boot.

**SKETCHED or absent:**
- **Volume and VTOC.** Volume descriptor (id, VTOC, root directory file, free page pool). The VTOC is
  an instance file of file objects whose first entry describes itself. Page tables are multi-level,
  and regions grow dynamically (TR-059 p6-10, TR-055 p16-18).
- **No byte layouts.** Pages are 1 KB, with a 4-page allocation block (TR-524 p9). Writes are
  through a disk-handler LRU cache on close (TR-524 p9-10).
- Physical file, directory and volume classes are unnamed (TR-524).
- Floppy files: "only limited part of the facilities" (TR-059 p32).
- Magnetic tape: named only (TM-229 p3).

## 7. Window system, menus, coordinator

**REIMPLEMENTABLE (interface level):**
- **Mixin construction, with bodies** (TM-065 p15-16, TM-061 p8):
  - `bare_window`, `with_border`, `with_label`, `window_with_border_and_label`.
  - Before and after demons for refresh and initialize. Refresh clears the area, then redraws the
    border, then the label.
- **TM-125 chapter 5** (p13-19, `listings/tm0125_p13.esp`). About 45 method signatures with one-line
  semantics, no bodies:
  - creation options (Table 1);
  - text output: write, move_cursor, insert, delete, scroll ...;
  - graphics: `:draw_line`, `:draw_rectangle`, `:draw_string`, with line width, line type and ALU
    arguments;
  - markers;
  - input: `:read` / `:read_sense`, with input codes `mouse$r`, `mouse$m`, `mouse$l`, `mouse$rr`,
    `scroll_request(Off)`, `abort`;
  - `:kill`.

  The owning class of each method is not stated, so attributing them to `window` is INFERENCE.
- **Window states.**
  - Five states: selected, shown, exposed, overlapped, deactivated. Tables give input and output
    behaviour per state (TR-046 p23 Table 2; TR-057 p6 Table 3-1, `listings/TR-057_p06.txt`).
  - TR-055 p18-20 gives a different, three-plus-selected model, and TM-125 p4-8 uses exposed/deexposed
    and shown/unshown with output permissions WAIT, NOTIFY, OUTPUT and SHOW. These are VARIANTS
    across 1984-85.
- **Hierarchy.** `as_superior` / `as_inferior` slots, with SCREEN at the root (TR-046 p9, p13;
  TM-125 p5).
- **Coordinator** (TR-061 p12 Fig. 1, TR-046):
  - An expert is an `e_process` (is-a process), which has an `e_program`, an `e_window` and an
    `e_port`.
  - `e_process_pool` holds the experts; there is also a whiteboard.
  - Key bindings are an ESP class `default_translation_table` with
    `:look_up(Table, Window, Key, Dest, Command, Help)`. The source is printed three times: TR-046
    p26 (abridged), TR-046 p28, TR-061 p13. The variants are recorded, not harmonized.
  - `system_menu` source: TR-046 p27, partial.
- **Measurement-window nature order** (TM-125 p20). labeled_sash, as_scroll, as_output, as_graphics,
  as_markers, as_input, as_mouse_input, user_window.

**SKETCHED:**
- **Class catalogue.** "About 120 classes", of which 69 are named with one-line roles (TM-125 p8-13,
  `listings/tm0125_p08_classes.txt`). A Japanese parts list is in TM-143 p6. The internal classes
  (window_manager, display, screen, status_line, logical_mouse, window_message) are named only.
- **standard_io_window.** 10 natures that expand to 40 classes, 121 slots and 527 methods (TM-181 p3).
- **Redisplay rectangle bookkeeping** (TM-126 p5). Other overlap redraw approaches appear in TM-225
  p14-15 (INFERENCE from box labels).
- **Window manipulator items** (TM-125 p8).
- **Character translation.** It happens in the window process. Codes are 16-bit, based on JIS
  (TR-061 p6, TM-181 p5).

## 8. Network: ROAM, PSI-NET, TCP/IP, file transfer

**REIMPLEMENTABLE (protocol semantics):**
- **ROAM** (TR-283; `listings/tr0283_p18..p20.esp`):
  - Proxy and original share a class, distinguished by the slot `object_category`.
  - There is one server process per client per remote node, created by a per-node controller process.
  - Each process has an export and an import table.
  - GOID = (node, export time, process number) per TR-283 p6. TR-524 p35 gives [node#, creationtime]:
    a VARIANT.
  - GMID matches replies to requests. A process waiting for a reply serves any nested request that
    arrives meanwhile.
  - Messages have control, standard and extra fields, carried in fixed-length packets (4200 bytes,
    later 1024 or 1400).
  - **Tag codes are printed** (TR-283 p20-21): request X'0010, reply X'0020; integer 0010, atom 0030,
    list 0070, undefined variable FFFF, class object FF10, exported instance FF20, imported instance
    FF30, and the string and vector variants.
- **User pattern.** Inherit `remote_object` (complete) or `as_remote_object` (incomplete). Each
  external method calls `:g_call`, which calls `:l_call` locally or `:r_call` remotely. On the remote
  side `:x_call` calls `:l_call` (TR-283 p9, p19; TR-524 p20-21). Appendix A of TR-524 is a full
  worked instance.

**SKETCHED:**
- **Earlier remote-object design** (TR-056 p28-31; superseded). Mixins `as_remote_object` and
  `as_pervasive_object`, plus remote directory and remote channel.
- **Machine and network classes.** node, socket, plug and cable (TR-055 p20-21, TR-057 p7, TM-079 p12).
- **PSI-NET** (TM-401 p2-8, TRANSLATION):
  - Components: LIA, BRG, GW over DDX, and NCP with connection and datagram modes.
  - 32-bit process addresses, with symbolic and group names held in a file on each PSI.
  - Applications: talk, mail (via server hosts), remote screen display, bulletin board, and
    file-manipulator remote access built on ROAM.
- **Network layering.** user-user (ROAM), then manager-manager, then handler-handler (session layer),
  then LIA/LIB (TR-283 p10-11).
- **TCP/IP.** Available from spring 1989 (TR-524 p2-3). Planned in TM-401 p12.
- **TELNET and FTP.** No held report describes them. TM-181 p5 mentions PSI-PSI and PSI-VAX file
  transfer, without protocol.
- **Not printed:** the 14 other ROAM classes, field widths, byte order, the controller protocol and the
  network manager classes.

## 9. Librarian, packages, environments, templates

**REIMPLEMENTABLE (rules, not formats):**
- **Three forms per class** (TR-057 p10, TR-087 p9, TM-079 p17, TM-143 p4):
  - class source file (exactly one class);
  - class template (everything except inheritance; interpretive code, plus compiled code on request);
  - class object (built from templates along inheritance; the executable image).
  - The compiler is a subroutine of the library. All predicate calls are indirect.
- **Rebuild rule** (TM-143 p4, TRANSLATION). Changing methods, demons, slots or slot initial values
  forces every inheriting class to be re-registered. A local-predicate change re-registers only that
  class. Classes that merely reference the changed class are never rebuilt. Related classes are
  auto-loaded.
- **Package name resolution.** Own package first, then public classes of inherited packages in ESP
  inheritance order. The usual environment is `with_simpos` (TM-388 pp93-94, OCR only, not eyed).
- **Librarian usage** (TM-785 p3; prior notes on IFS `.COM` files):
  - The librarian runs as a process `librarian_<n>`.
  - Command files run with `fdd("x.com")` from floppy.
  - Packages have a "package template file". The error menu offers "Erase existing package and
    continue".

**SKETCHED:**
- The template, object and package template file **formats**, which no report gives.
- The `library` class API, which is not printed. Usage-derived method names exist outside these reports
  in `pim/docs/simpos/required/old_regex_census.tsv (superseded by simpos/required/)` and are deliberately excluded from classes.tsv.

## 10. Boot sequence, IPL, floppies (SKETCHED throughout)

- **Boot process** (TM-100 p6, p13; TR-056 p21). Created and activated by the hardware. It is the
  sole instance of `boot_process` (inherits process, overrides `:create` and `:activate`) and runs a
  program inheriting `as_boot_program`. It then brings itself under supervisor control.
- **Boot-up instantiation.** Device handlers and the file manager are instantiated during boot-up
  (TR-059 p30, p32).
- **System disk** (TR-059 p32-33). The boot region "stores CSP (Console Processor of PSI) programs, PSI
  firmware programs, IPL (Initial Program Loader), and so on. CSP reads in these programs during system
  boot-up."
- **IPL** (TR-087 p11, TR-086 p8-10, TM-100 p18, TM-143 p2).
  - The IPL is written in ESP and "included many modules of the kernel operating system and also
    run-time support routines of ESP".
  - Modules are separately compiled, partially linked, and stored on flexible disks. The IPL does the
    load and final linkage on the PSI.
  - It became operational in May 1984 (TM-100 p18) or end of April 1984 (TR-086 p10). TM-143 and
    TM-229 place IPL in the kernel.
- **Development path** (TM-143 p6-7). DEC 2060 cross tools, then a DEC LSI-11 (SVP), then floppy, then
  the PSI console (CSP).
- **Not given:** the boot image format, the IPL module list, the floppy format, the order in which
  subsystems are instantiated, or the `as_boot_program` code.

## 11. Debugger, editor, listener, manipulators (SKETCHED)

- **Debugger and interpreter** (TR-057 p8-9 Fig. 4-1, `listings/TR-057_p08.txt`; TM-079 p15).
  - Procedure-and-clause box model. Procedure ports: Call, Exit, Fail, Redo. Clause ports: Unify,
    Next, Pick, Miss, Exit, Redo.
  - Interpretive and compiled code call each other.
  - Debugger state-window items are printed in TM-126 p6: trace/no trace/no debug, leash grid, spy
    points, menu items.
- **Editors.**
  - Edips: structure editor with an operator-precedence grammar and a transducer (TR-057 p9,
    TR-087 p8, TM-079 p16).
  - PMACS: Emacs-like (TM-181 p4).
- **Listener and shell.** A "shell" item appears in the system menu (TM-181 p3), and listeners are named
  in TR-055 p7. Neither is described.
- **System menu.** EXPERTS run as multi-instance processes, MEDIA SYSTEMS as single-instance. Item
  lists: TM-181 p3 (`listings/TM-181_p03_system_menu.txt`), TM-143 p3, TM-229 p5.
- **File manipulator.** Menu items are listed in TM-126 p6 and TM-401 p10, including remote access.

---

## What a reimplementer has, in one line per area

| Area | Coverage |
|---|---|
| Process and stream core | Printed source (TM-100), near complete except dispatch |
| Pools, semaphores, events, permanent objects | Printed interfaces and key bodies (TR-056, TR-059) |
| Distributed-file classes | Printed source with ROAM dispatch (TR-524 App. A) |
| ROAM | Wire tags printed, semantics complete |
| Windows | Mixin source for 4 classes plus about 45 method signatures; the rest are names |
| Coordinator | Translation-table and system-menu source |
| GC, boot, IPL, librarian formats, scheduler, device handlers, on-disk formats, TELNET/FTP | Prose only, or absent |

The missing items are listed in `NAMED_NOT_DEFINED.md`.
