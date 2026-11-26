# The route to SIMPOS booting to a top level (2026-11-25)

The owner asked to "step back from the census" and write the concrete
path from what exists now (`psi/librarian.py`, `psi/kl0.py`,
`psi/espc.py` and the stand-ins in `psi/standin/`) to SIMPOS booting to
a top level. This page gives:

- what the PSI does first;
- which classes and processes must run, and in what order;
- what the console and the FEP must answer;
- which of these exist today, and what blocks each.

It then names the first step that is unblocked. Step 3i took B2, step
3j B3, step 3k B4 for the FEP timer, and step 3l B5 to B8 as labelled
stand-ins, under the owner's rule of 2026-11-25 (§4.4). Step 3m took the
login requester through its prompts and a local login to the held login
server and replier (§4.5); §6 is the path from SIMPOS to PIMOS.

Labels, as elsewhere in `docs/simpos/`:

- **PRINTED**: printed in an ICOT report. The page images were read by
  eye. "Prose" means the page describes the step but prints no code.
- **HELD**: held compiled code (`.ptf` cells) or held ICOT source.
- **USAGE**: what held callers send, with no definition.
- **INFERENCE**: our reading of the sources.
- **OURS**: a choice made here.
- **UNKNOWN**: no source found.

The page numbers are PDF pages of `docs/nonlocal/lit/trtm/`, with the
printed folio where it differs.

## 1. The target

**"A top level"** is the state in which a user can start a program by
hand. SIMPOS gives two such states, each PRINTED:

1. The **system menu**, after login. A double right click opens it, and
   an item starts a program in a new process (TM-134 p66, p71; TM-112
   p16; `subsystems/shell.md` §4.3, §5.1 d).
2. The **debugger's listener** (`?-`), itself a system-menu item
   (TM-134 p67-p71; `shell.md` §5.4).

For PIM/m, the top level that matters is one particular system menu: the
one built by `psdpim/INSTALL.DIR/login.com` (HELD, JIS text, decoded
2026-11-25; stamped `icpsi277::>sys>csp>INSTALL.DIR>login.com.8`,
26-Oct-89). Its second column has the items
`{"Pseudo Multi-PSI", pimmcsp##pseudo_csp_main_program}` and
`{"Login PIMOS", pimfep##pimos_login_requester}`. Its `define` clause sets
`me` to `user:pmpsi` and `pimos` to `>sys>csp>PIMOS.DIR`. So the route
ends where that menu is up and `pimos_login_requester` can be started
from it.

## 2. The route

| # | Step | Source | Exists today | Blocked by |
|---|---|---|---|---|
| B0 | The console processor loads the microcode and starts the IPL | PRINTED prose: TM-112 p7 (1.00 cold boot); TR-087 p11 §5.3; HELD: psdpim `INSTALL` (the `sys*` trio to `/usr/psi/simpos/csp`) | `syspsi`, `sysinit`, `sysidat` are held; the microword is decoded (`../psi_microword.md`) | Not on the route for now. `kl0.py` (OURS) stands in for the KL0 firmware (README §5 step 4). |
| B1 | The IPL loads SIMPOS from the fixed disk and links it | PRINTED prose: TR-087 p11 §5.3; TM-100 p18; `ESPtex/overview-e.tex`:1150-1180 | Substituted: `librarian.py` loads the 1,455 held class templates; `espc.py` compiles the stand-ins (36 before step 3l; 48 files in `psi/standin/` after it, 50 after step 3m) | SUBSTITUTED, OURS. The IPL image is not held (`layers/FORMATS.md` §4). |
| **B2** | **The hardware creates and activates the boot process, which runs the boot program** | PRINTED prose: TM-100 p6, p13; TR-056 p21; HELD: `pimmcsp##pseudo_pe_process` `release/1` | **Step 3i:** stand-ins `boot_process` and `as_boot_program` (INTERPOLATED); the machine's first process is the boot process; the printed `as_program` `invoke/1` runs a boot program in it | **DONE as a stand-in** (§4). The real boot program is lost. |
| **B3** | **The boot process brings itself under the supervisor, and the multiple-process environment starts on it** | PRINTED prose: TR-056 p16, p19, p21; TM-100 p6, p13; TR-055 p5; PRINTED code: `process:activate/2`, `suspend/2`, `resume/2` (TM-100 Fig. 3.1), `stream` `put/2`, `get/2` (Fig. 3.6); HELD: `pseudo_pe_process` `release/1`, `$or$5/2` | **Step 3j:** `status/3`, `clear_masks/1`, `entry_of_invoke/2`, class `context`, `boot_process` `create/2` and `activate/2`, all INTERPOLATED; a dispatcher in `kl0.py` (OURS). A second process runs, and the two talk through a stream | **DONE as a stand-in** (§4). The real supervisor is lost. |
| B4 | Device handlers are instantiated and activated | PRINTED prose: TR-059 p30 (folio 28); TM-100 p6; PRINTED code: part of `interrupt_process` (TM-100 Fig. 3.4) | Step 3j: not the SIMPOS handlers, but PIM/m's FEP devices run as processes: the held `pimos_timer` `create_timer/9` runs to its end under the supervisor. **Step 3k:** blt 6f (KNOWN-PLAINTEXT) and `boot_process:request/3` (INTERPOLATED); a request to the timer's device process round-trips: `close` (60), `get_count` (301), `get_date_time` (304) (§4.3) | **DONE for the FEP timer, as a stand-in.** The SIMPOS handlers stay lost: their classes and the device list are not held, and `interrupt_process` is printed only in part (its dispatch is elided). Not reached: `on_after` (303) and `terminate_core` (blt 90 has a row since step 3k, but reads a hardware PCB word). |
| B5 | Supervisor services: the system directory, the library, users, worlds, the file system | PRINTED interfaces: TR-056 p20-p25 (library, `directory`, worlds), TR-524 App. A (file classes), TR-059 p23-p27 | `library` partly modelled in Python (step 3f); `pathname` HELD-SOURCE. **Step 3l:** `directory` (`retrieve/3,4` and the node methods, INTERPOLATED) over an OURS tree built from the HELD psdpim archive and its `INSTALL` placement; `node_full_name/3` (INFERENCE) | **DONE as a stand-in** (§4.4). The real file system is lost; the tree holds only what PIM/m installs. |
| B6 | The coordinator and the window system start | PRINTED 1984 code: TR-046 p26-p28, TR-061 p13; prose `shell.md` §1.1; window mixins (TM-065, TM-125) | `pmacs_window` and `standard_editor` stand-ins, minimal. **Step 3l:** a coordinator process (OURS state and selectors, INTERPOLATED behaviour) reads `me:login.com` through `standard_input_file` (INTERPOLATED; reader OURS), applies its `define`, holds its `menu`, answers `information/3`; `standard_io_window` and `font` (OURS bodies, held selectors) | **The coordinator: DONE as a stand-in** (§4.4). The window system only as far as the login requester's first prompt: a window is a transcript and an input stream; no bitmap, no menu window (the menu is a list). |
| B7 | Login: the user, the world, `me:login.com`, the system-menu items | PRINTED prose: TM-134 p66, p68; TM-181 p3; TM-229 p5-p6; HELD code: `pimfep##simpos_user` `create/4`, `setup_process/2` | the process slots `user` and `world` (PRINTED, TM-100 Fig. 3.1) with interpolated accessors. **Step 3l:** `user`, `world`, `password_list` (INTERPOLATED from the held sends; registry and password OURS); the held `create/4` and `setup_process/2` run to their ends | **DONE as a stand-in** (§4.4). |
| B8 | The top level: the system menu starts a program in a new process | PRINTED dialogue: TM-134 p71 (`:create(#c,O). :create(#process,P). :activate(P,O).`) | `activate/2` runs since step 3j; since step 3k the printed `create/2` runs, its `create_core(PROCESS, ...)` corrected to `Class` (labelled, printed text kept). **Step 3l:** `invoke_system_menu`, then `{select, "Login PIMOS"}` (events OURS) start the held `pimfep##pimos_login_requester` in a new process | **REACHED as a stand-in** (§4.4). The started program puts its first prompt and waits for a FEP node name; every process waits. Step 3m (§4.5): keyboard input takes it through its three prompts and a local login to the held server and replier. |

### B0. The console processor (PRINTED prose, HELD files)

- SIMPOS 1.00, cold boot (TM-112 p7, eye-read; `shell.md` §4.1): power
  on and wait for `>` on the CSP console. Type `B`, then `deb`. Answer
  `1` and feed the floppies `EXEC`, `WINDOW`, `EDITOR`, `SUPER`, then the
  application floppy. "A login message will appear on the PSI bitmap
  screen."
- PSI-III (PSI/UX): psdpim `INSTALL` copies `syspsi`, `sysinit` and
  `sysidat` "to /usr/psi/simpos/csp as unix files on PSI-III", so the
  console side loads them from the Unix host (`layers/FORMATS.md` §3).
- The console processor serves only the built-ins `read_console` and
  `display_console` (TR-087 p11 §5.2, page image read 2026-11-25). It is
  "provided primarily for hardware and firmware debugging".
- The PSI-III console's command language is not held. The pseudo-CSP's
  `boot.init` (`power on`, `boot on`, `clear`, `init`, `impl`, `patch`,
  `ipl`, `start`) boots PIM/m, not SIMPOS. Applying it to the PSI-III is
  INFERENCE (`layers/FORMATS.md` §4).

### B1. The IPL (PRINTED prose)

- TR-087 p11 §5.3 (page image read 2026-11-25): "a rather flexible
  initial program loader was implemented in ESP. Using this IPL, modules
  of programs to be debugged are separately compiled, partially linked
  and stored in flexible disks ... Loading from the flexible disk and the
  final linkage are done by the IPL on PSI itself."
- TM-100 p18 gives the date: "In May, the IPL became operational".
- `overview-e.tex`:1150-1180 (1990): the IPL "Loads SIMPOS stored on the
  fixed disk to main memory", in user, developer or system mode.
- USAGE: `:is_ipl_class_object(#library, ClassId)`, true for classes in
  the IPL image (cal-esp `deb2.12/pmod.esp`:387;
  `subsystems/librarian.md`). So the IPL image holds class objects.
- On the route this step is **substituted** (OURS). `librarian.py`
  builds the class objects from the held templates, and `espc.py`
  compiles the stand-ins into package `simpos`.
- kappa2's `init/ipl.com` (HELD) is an application command file. It
  `load`s `kappa##kappa_loader` and refutes `:ipl_load(#kappa_loader,
  [...], 270)`. Its `ipl_load/3` (`utility/tool/LOADER.ESP`:62-66) creates
  a process and activates it, so it is blocked at B3. That SIMPOS's own
  IPL runs it is not stated anywhere held.

### B2. The boot process (PRINTED prose, HELD call site)

- TM-100 p6 (folio 4), page image read 2026-11-25: "Another kind of
  special process is a boot process, which is created and activated by
  the hardware, not by another process, when the system is bootstrapped.
  The multiple process environment in SIMPOS is initiated on the boot
  process. The supervisor must make it under its control, after the
  system has started."
- TM-100 p13 (folio 11): "A boot process is a sole instance of class
  'boot_process', which executes the boot program inheriting class
  'as_boot_program'. After initiation, this boot process goes under
  control of the supervisor, and acts exactly as an ordinary process. For
  this to be possible, class 'boot_process' inherits class 'process' and
  overrides the predicates, :create and :activate."
- TR-056 p21 (folio 19), page image read 2026-11-25: the overrides exist
  "so that the boot process comes under control of the supervisor after
  the system has started, by the boot process itself calling these
  operations."
- HELD, found in step 3i: `pimmcsp##pseudo_pe_process` is a held subclass
  of `simpos##process`, the Pseudo-Multi-PSI's PE process. Its pool cell
  18 is `#simpos##boot_process`, the only held reference to the class.
  `release/1` (@177-189) does three things:
  - `:status(Self, dormant, on_release)` (@17a-17e);
  - `:get_instance(#boot_process, Boot)` (@17f-183);
  - `:request(Boot, release, Self)` (@184-189).

  So the boot process has a class method `get_instance/2`, and it still
  takes requests after boot (USAGE). What `request/3` does is not held.
- No held class inherits `as_boot_program`
  (`subsystems/notes/ifs_libshell.md` §1.4). The boot program is lost.

### B3. Under the supervisor (DONE as a stand-in, step 3j)

The boot process must call its own `create` and `activate`, and other
processes must be activated and run. The printed `process:activate/2`
(TM-100 Fig. 3.1, PDF p8-p9; `psi/standin/process.esp`) sends:

1. `:status(Process, dormant, on_activate)`;
2. `:entry_of_invoke(Program, Entry)`;
3. `:set_entry_point(Process!context, Entry)`, `:activate(
   Process!context)` and `:set_priority(Process!context, 0)`, which are
   hardware;
4. `:clear_masks(Process)`;
5. `:add(#process!ready_queue, Process)`, on a class slot with no
   printed initial value.

None of these is printed. Until step 3j each was refused. The sources
that step 3j wrote them from:

- **`status/3`** has five call sites, none with a body:
  - the printed `activate/2`: `(dormant, on_activate)`;
  - held `pseudo_pe_process release/1` @17a-17e: `(dormant,
    on_release)`;
  - held `pseudo_pe_process $or$5/2` @3a9-3bc, reached from
    `terminate_core/1`, found in step 3j by a sweep of the compiled
    cells of all eleven packages: clause 1 `(suspended, dormant)`,
    clause 2 `(ready, dormant)` and then a removal from a queue.

  In `$or$5/2` the third argument is a status (`dormant`), and the
  second clause is reached only when the first clause's `status/3`
  fails. So `:status(P, Old, New)` makes P's status New if it is Old, and
  fails otherwise (INTERPOLATED). `on_activate` and `on_release` are
  transient statuses, the "and some others" of the printed slot comment.
  Step 3h's search of source text could not find this; the cells could.
- **`entry_of_invoke/2`** is sent to the program. TM-100 p6: "when a new
  process is activated, the activate predicate is called with a program
  as an argument, because the program instance should be pushed into the
  invocation stack of the new process". The printed `invoke/1` does that
  push. So the entry is the program's `invoke/1` (INTERPOLATED); its form
  `{Program, invoke}` is OURS.
- **`context`**: TR-055 p5 (63 contexts, four stacks each; "process
  dispatching must be controlled by software"), TR-056 p19 (a register
  set, a stack group and heap memory per process; at most 63), and the
  calls of Fig. 3.1. Held: `pseudo_pe_process` reads `context` and sends
  `get_number/2`. Stood in as an object with a number, an entry, a
  priority and a state (INTERPOLATED).
- **The dispatcher and the scheduler**: TR-056 p16 ("A ready process is
  in a ready queue waiting to be run by the dispatcher"), p21 (an
  ordinary process, when activated, "is placed in the ready queue by the
  supervisor"; resume "calls the software scheduler"). Neither is
  printed. The printed `suspend/2` takes the running process out of the
  ready queue, and the printed `get/2` reads the stream right after it,
  so the processor must change hands in between. The dispatcher in
  `kl0.py` is OURS: it switches after the printed `suspend/2` has made
  the running process suspended, and when a process's program has ended.
  It takes the first ready process in the queue. No preemption; priority
  is ignored.
- **`boot_process` `create/2` and `activate/2`** (INTERPOLATED, from
  TM-100 p13 and TR-056 p21): the printed process methods without what
  does not apply to a process the hardware already runs. `create/2`
  gives the boot process a context (number 0), and makes the ready
  queue, a list (OURS). `activate/2` sets no entry point (the boot
  program is already running), makes the boot process ready and queues
  it.

What runs now (`psi/test_espc.py` `test_step3j_supervisor`): a probe
boot program, in the shape of held kappa2 `ITRSES.ESP`:111-116 and
`MOPMANAGER.ESP`:165-172 (CORRECTED step 3k: first cited :162-168,
`source_check_2026-11-24.md` §10.4) with `MOPKAPPA.ESP` `goal/1`, does:

1. `:create(#boot_process, B)` and `:activate(B, Prog)`;
2. makes a stream, a child program holding it, and a process
   (`create/3`, `[free,free,free,free]`);
3. `:activate(P, Child)`, then `:get(S, X)`.

The boot process suspends, and the dispatcher starts the child process
at its entry. In it, `:self(#process, P)` is the child process, the child
program is on top of its stack, and its parent is the boot process. The
child `:put`s `created`, which resumes the boot process. The child's
program ends, and it dies (status `nil`). The boot process gets
`created`.

The held `pseudo_pe_process release/1` now passes `status/3` (`dormant`
becomes `on_release`) and stops at the boot process's `request/3`, which
is not stood in. With status `nil` it fails at `status/3`. (Step 3k:
`request/3` is stood in, and `release/1` runs to its end, §4.3.)

What stays open, labelled in the stand-ins:

- `instance_array` (printed class slot) is not filled, and `add_child/2`
  is not stood in, so `children/2` stays empty. (Step 3k: both done;
  `instance_array` is an OURS heap vector of 63, filled by the printed
  `create_core/3`.)
- A dead process is not taken out of the ready queue (`die/1` does not
  do it); the dispatcher skips it.
- The printed `create/2` now reaches its `:create_core(PROCESS, ...)`.
  `PROCESS`, in capitals as printed, is a fresh variable, so it stops
  there (`unbound receiver`). No correction was made: `create/3` is the
  form the held callers on the route use. (Step 3k: corrected to `Class`,
  labelled CORRECTED, the printed text kept in the comment; the printed
  `create/2` now makes a process.)
- In the census the process is the boot process before its own `create`
  and `activate`. So the 11 device creators' `activate/2` now stop at
  the missing ready queue, not at `status/3`.

### B4-B6. Devices, services, coordinator (B4 BLOCKED for SIMPOS's handlers; B5, B6 stood in by step 3l, §4.4)

- TR-059 p30 (folio 28), page image read 2026-11-25: "A device handler is
  instantiated and activated during a system boot-up procedure." A
  handler is an interrupt process, dispatched by hardware. The devices
  are disk, floppy disk, magnetic tape, printer and bitmap display
  (`overview-e.tex`, the kernel table), with keyboard and mouse.
  `interrupt_process` is printed in part (TM-100 Fig. 3.4): its
  `%TRAP TO PROCESS`, `%RELEASE PROCESSOR` and `%ALLOCATE PROCESSOR`
  steps are elided. No handler class is held. B4 stays BLOCKED.
- Step 3j ran PIM/m's FEP devices, which are ordinary processes, not
  SIMPOS handlers (`psi/test_espc.py` `test_step3j_fep_device`). Under
  the supervisor, the held `pimos_timer` `create_timer/9` runs to its
  end:
  1. it activates the device's process (@48);
  2. it waits on the creation-status stream (@4c);
  3. the device process runs its held `goal/1` and puts `normal`;
  4. the creator puts the creation reply `{16, 1}`.

  The device process then waits in `see/2` on its input stream. Given a
  request, it takes it in its own process. In step 3j it stopped at blt
  6f (`list_to_vector`, unwitnessed then) in `fep_message_assembler
  disassemble/3` @a9. Step 3k passes that stop (§4.3).
- TR-056 p22-p25: the root directory is kept in a class slot of
  `directory` (`:root(#directory, Root)`). Pathnames are retrieved with
  `:retrieve`, and a process's world with `:world(#process, World)`.
  TR-524 Table 3 (p36) lists `directory` `retrieve/c` and `make/c`.
  `local_logical_file` (p37) sends `:retrieve(#directory, Lfile,
  Pathname, FullPathname)`.
- The coordinator is the background process that owns the system menu,
  the key table, the whiteboard and the abort handler (`shell.md` §1.1,
  §2.5). It needs a process of its own, which B3 now provides. Its class
  is lost.

### B7. Login (stood in by step 3l, §4.4)

- What login does (PRINTED prose, TM-181 p3, TM-229 p5-p6):
  1. set the system-menu items;
  2. set the logical names, with `me:` = `>sys>user><name>`;
  3. run an initialisation program;
  4. create processes for the editor, debugger and so on.
- As code (HELD, `pimfep##simpos_user` `create/4`, `shell.md` §4.1),
  in this order:
  1. `:identify(#user, Name, Password, U)`;
  2. `:create(#world, W)`;
  3. `:append(#pathname, "user:", Name, Dir)`;
  4. `:define(W, "me", [Dir])`;
  5. `:set_default_logical_name(W, "me")`.

  Then `setup_process/2` sets the process's user, world, access mode
  and passwords.
- Exists: `pathname` (HELD-SOURCE) and the printed process slots `user`
  and `world`, with interpolated accessors.
- Missing until step 3l: `user` (`identify/4` is one census stop) and
  `world`, both known by USAGE only. Step 3l stands them in (§4.4).

### B8. The top level (reached as a stand-in by step 3l, §4.4)

The 1.0 debugger dialogue (TM-134 p71, PRINTED) starts a program in a
new process: `:create(#c,O).`, `:create(#process,P).`,
`:activate(P,O).` A system-menu item does the same (TM-786 p5, TM-785
p6). Every way to start a program in its own process goes through
`activate/2`, which runs since step 3j (B3). The printed `create/2`,
which the dialogue uses, stopped at its own `create_core(PROCESS, ...)`
until step 3k corrected it (§B3). The kappa2 and Tour callers use
`create/3`.

## 3. What the console and the FEP must answer

- **SIMPOS's own boot needs no FEP.** On the PSI, the "front end" is the
  console processor (B0). It loads the microcode and serves
  `read_console` and `display_console` (TR-087 p11). On a PSI/UX it is
  the Unix host. The bitmap display, keyboard, mouse and disks are the
  PSI's own devices, driven by SIMPOS's handlers (B4). The byte protocol
  between the PSI and its console is not held (UNKNOWN). On this route,
  Python takes the console's place.
- **The FEP in this project is the PSI itself.** Once SIMPOS is at its
  top level, `Login PIMOS` (`pimfep##pimos_login_requester`) and the
  `pimfep` and `pimscsi` programs answer PIMOS's FEP commands
  (`../fep_services.md` §6). Their own SIMPOS needs are what the
  censuses measure: `directory:retrieve/3,4` (B5), the `pmacs_window`
  protocol (B6), and, until step 3k, blt 6f in every device's request
  path. Step 3j settled `process:status/3` and the second process that
  `stream:see/2` needed (B3).

## 4. The steps taken

### 4.1 B2 (step 3i)

B0 and B1 are substituted. B2 is the first step whose inputs exist:

- printed prose that says what the boot process is;
- a held call site;
- the printed `as_program` `invoke/1`, which runs a program in the
  calling process.

B3 onward were blocked then (step 3j took B3, §4.2).

**What was built** (`psi/standin/`, labelled in each file):

- `boot_process.esp` (INTERPOLATED):
  - nature `process`;
  - a class slot `instance` (name OURS);
  - `get_instance/2`, from the held call site;
  - `boot/2` (selector OURS), the hardware's act: `:new`, record the
    sole instance, set status `active`, the printed status slot's
    parenthesised value (TM-100 Fig. 3.1).
- `as_boot_program.esp` (INTERPOLATED, nature `as_program`, INFERENCE).
- `process.esp` `self/2`: when no process exists yet, the one made is
  the boot process. So the machine's first process is a
  `simpos##boot_process`, as on the PSI. Before, it was a plain process.
- `kl0.py`:
  - `SIMPOS_MODELS` refuses `boot_process`'s class `create/2`,
    `create/3` and instance `activate/2`. They are overridden (PRINTED)
    and their bodies are not printed. Otherwise the inherited process
    versions would run in their place.
  - Dispatch finds a model along the receiver's inheritance order. So
    the boot process inherits the step 3g `suspend/2` model, unless a
    class before the model's class defines the method itself.

**The test** (`psi/test_espc.py` `test_step3i_boot`): a probe boot
program, an OURS test class with nature `as_boot_program`, is created
with the printed `as_program` `create/2` and run with the printed
`invoke/1` on a fresh machine. During its goal:

- `:self(#process, P)` is the boot process, a `simpos##boot_process`;
- `:get_instance(#boot_process, B)` gives the same object;
- the program is on top of P's invocation stack;
- P's status is `active`.

After `invoke/1`:

- the stack is empty;
- P's status is `nil`: the printed `resign/1` lets a process whose
  stack empties die (TM-100 p11).

The test also pinned the B3 blockers, as they were before step 3j:

- `:activate(Boot, Program)` and `:create(#boot_process, X)` refuse with
  the override message.
- A second process from `process:create/3` has the boot process as its
  parent, and its `activate/2` refuses at `process:status/3`.
- The held `pseudo_pe_process release/1` stops at `status/3` with
  `(dormant, on_release)`.

The census effect and the fault injections are in `../../psi/README.md`
("Step 3i: the boot process").

### 4.2 B3 (step 3j)

The four gates of §B3 are stood in, each from its call sites and the
printed prose, each method labelled in its file (the basis table is
`../../psi/README.md`, "Step 3j"):

- `process.esp`: `status/3` and `clear_masks/1` (INTERPOLATED);
  `create/3` now makes a context as the printed `create/2` does;
- `as_program.esp`: `entry_of_invoke/2` (INTERPOLATED, the file's only
  method that is not PRINTED);
- `context.esp`: new (INTERPOLATED);
- `boot_process.esp`: `create/2` and `activate/2` (INTERPOLATED);
  `create/3` stays refused;
- `kl0.py`: the dispatcher (OURS). The `suspend/2` model runs the
  printed body for a process under the supervisor and then dispatches.
  For any other process it still refuses `would suspend`.

Also `as_resource.esp` (INTERPOLATED, from `pseudo_scsi` and kappa2
`KP_POOL.ESP`): `assign/1`, `assigned/1` and `resign/1`, membership in
the printed process slot `resources`. It is not on the route.

At the end of step 3j, B3 ran as a stand-in. B4 was blocked, because
the SIMPOS handlers are lost. The FEP devices went one step further and
stopped at blt 6f.

### 4.3 B4 for the FEP timer (step 3k)

The basis table is `../../psi/README.md`, "Step 3k". What was added:

- **blt 6f `list_to_vector(L, ^V, ^Tail)`** (`psi/kl0_opcodes.tsv`,
  KNOWN-PLAINTEXT). Four held source clauses with held cells settle the
  operands (`source_check_2026-11-24.md` §10.1). Two parts are
  INFERENCE: the tail of an improper list, and that the elements are
  shared.
- **`boot_process:request/3`** (INTERPOLATED, `standin/boot_process.esp`):
  - `request(Boot, release, Process)` calls `release_core(Process)`;
  - any other request refuses with `unsupported_request`.

  The basis is the one held send (`pseudo_pe_process release/1`
  @184-189). No held cell sends `release_core/1` itself. That the call
  is synchronous is OURS.
- **What the held `release/1` then needs:**
  - `process:add_child/2` and `remove_child/2` (INTERPOLATED, the
    printed `children_processes` slot; `remove_child`'s send is
    `$or$3/1` @36c-374);
  - `context:release/1` (INTERPOLATED, @35f-361);
  - blt 94 `set_pcb_entry(N, I, V)`, an INFERENCE row. Its basis is the
    `pseudo_pe_process` methods `set_pcb_entry/4` and `pcb_entry/4`, and
    the slot comment "Hardware PCB" (TM-100 p8).

  `create/3` now records the child in its parent.
- **What the timer's requests need:**
  - `time:now/2` and `get_count/2`, and the new class `date_time` with
    `now/2` and `get_count/3`, all INTERPOLATED from `pimos_timer`
    `get_count/3` @86-8e and `get_date_time/3` @be-d0. The clock values
    are class attributes (OURS).
  - `put_integer`'s immediate is sign-extended (INFERENCE). Its basis is
    `packet_generator abs/2` @280-287, and the -1 length word of the
    reply.
  - A negative element of a 32-bit string is stored in two's complement.
  - `resolve_value` copies the cells of a stored list. Without the copy,
    the ready queue lost the boot process when a list element was a
    variable that backtracking unbound. Its basis is TM-388 p110 (folio
    98); the copy itself is OURS.

**The run** (`psi/test_espc.py` `test_step3k_b4`). On a fresh machine,
the boot process creates the timer with the held `create_timer/9`. It
then puts a request on the device's input stream and waits on the
output stream. The device process takes the request in its own process,
the held handler answers, and the boot process gets the reply:

| Command | Reply (32-bit words) | After |
|---|---|---|
| 60 `close` | `[16, 0, 1, 0]` | the device process's `close_flag` is `closed` |
| 301 `get_count`, clock 1234 | `[16, 0, 1, 1, 0xffffffff, 1234]` | the device process waits in `see/2` again (suspended) |
| 304 `get_date_time`, date 33000, time 45678 | `[16, 0, 1, 2, 0xffffffff, 0xffffffff, 33000, 45678]` | as for 301 |

`test_step3j_supervisor` also runs the held `release/1` to its end:

- the process's context and its parent, world and user become `nil`;
- the context's state becomes `released`;
- the PCB entries `(n, 24)` and `(n, 8)` become 0, and `(n, 12)` becomes `nil`;
- the boot process's children no longer include it.

The PE status stays `on_release`, because the held `release_core` does
not change it.

**Where the boot route stops now.**

- B4 runs for the FEP timer as a stand-in: its requests round-trip
  through its device process under the supervisor.
- Not reached in B4:
  - `on_after` (303) is the timer's alarm, and it needs an alarm process;
  - `terminate_core`: blt 90 (`pcb`, read in `$or$5` @3bb) now has a
    row, its operands KNOWN-PLAINTEXT from kappa2 `LUUTIME.ESP`:107.
    But it reads word 15 of the PCB, which nothing on the route writes,
    so it refuses there (the hardware's own words are not modelled).
    No test runs `terminate_core`.
- The SIMPOS handlers themselves are still lost.
- B5 to B8 are as in §2.

### 4.4 B5 to B8 (step 3l)

Under the owner's rule of 2026-11-25 ("It's okay to infer what you don't
have"). The basis table, the injections and the census are in
`../../psi/README.md`, "Step 3l"; every inference is listed in
`source_check_2026-11-24.md` §11.

- **B5** (`test_step3l_b5`). `psi/simpos_fs.py` mounts a file tree
  (OURS) of what a PSI with PIM/m installed holds: the HELD psdpim
  archive's files, placed by the HELD `psdpim/INSTALL` lines, `me:` =
  `>sys>user>pmpsi` (INFERENCE). `directory:retrieve/3,4` resolves
  `>`-absolute names, `Alias:rest` through the calling process's world,
  bare names under its default logical name, and `.N` versions. A miss
  fails, as the held callers' fallback clauses require. The held
  `pimos_file check_file_size/1` runs on it (a hit, a directory, a
  miss), and the held `net_spawn_user set_default_node/2` runs through
  `node_full_name/3`.
- **B7** (`test_step3l_b7`). The held `pimfep##simpos_user create/4`
  and `setup_process/2` run to their ends on the stand-ins `user`,
  `world` and `password_list`: a wrong password or an unknown user
  fails; after login the process's world resolves `me:login.com` and a
  bare `login.com`.
- **B6** (`test_step3l_b6_b8`). The boot program logs in, then starts a
  coordinator process. It reads the HELD `me:login.com` (three clauses:
  `menu`, `define`, `package`), defines `me:`, `root:`, `sys:`, `pmpsi:`,
  `mpsi:` and `pimos:` in the world (three are checked by the test), keeps the menu's two columns (7 and 3 items),
  and answers `information(package, user)`.
- **B8** (`test_step3l_b6_b8`). The events `invoke_system_menu` (the
  printed action's name, TR-046 PDF p28) and `{select, "Login PIMOS"}`
  (OURS) make the coordinator create `pimfep##pimos_login_requester`
  and activate it in a new process, its child, which shares the world.
  A select with no menu shown starts nothing.
- **B8, the prompt** (`test_step3l_b8_prompt`). The held requester runs
  `goal/1`, `initiate/1` and `read/4` on the stand-ins
  `standard_io_window` and `font` (bodies OURS; selectors and argument
  order HELD, `:create(#standard_io_window, Opts, W)` @af-b4,
  `:create(#font, "font:test_11.font", F)` @b9-be) and
  `process:get_number/3` (INFERENCE). It titles its window `Pimos remote
  login N` (its held `title_string/1`), puts `Enter FEP node
  name--------->` and waits in `read/2`.

**Where the route stops now.** Every process waits: the login
requester for a node name typed in its window, the coordinator for an
event, the boot program on its own stream. This is §1's target, the
system menu up and `Login PIMOS` started from it, reached with
stand-ins. Until step 3m keyboard input to a window was not modelled
(§4.5 takes it on). The real window classes are lost
(`subsystems/window.md`).

### 4.5 The login requester's dialogue and a local login (step 3m)

The basis, the injections and the census are in `../../psi/README.md`,
"Step 3m"; every inference is listed in `source_check_2026-11-24.md` §12.

- **Keyboard input** (`test_step3m_keyboard`, OURS path). Coordinator
  events `{key, Code}` go to a keyboard stream; the window that was
  last shown (`show/1`) reads it. `read/2` gives one code, `getl/2`
  reads to RETURN, `input_data/2` gives codes back, and
  `inhibit_echo/1` stops the echo around the password. The held
  requester's `read/4`, `check_code/4` and `read_password/3` run. It puts
  all three prompts and takes the node `local`, the user name and the
  password.
- **No server** (`test_step3m_keyboard`). The requester makes its port
  (`standin/port.esp`). Its `connect_server/4` asks
  `:local_server_socket(#pimos_remote_login_server, SS)`, which is held
  code (@32-38) and fails while the slot is `none`. The requester then
  writes `Network error.`, beeps twice and waits for a key. For a node
  that is not known it writes `Unknown FEP node name.` instead.
- **A local login** (`test_step3m_local_login`). A probe program (OURS)
  stands in for PIMOS's side. It makes the held
  `pimos_remote_login_replier` and sends it `io(0, "")`, makes the held
  `pimos_remote_login_server` and sends it `io(0, "local")` and
  `io(1, "  ")`, then sends the replier PIMOS's texts. All of these are
  the requests `login.kl1` makes through 620 (`../fep_services.md` §7.3
  rows 1-9). The window then shows:

  ```
  Enter FEP node name--------->   local
  Enter your PIMOS user name-->   pimos
  Enter your PIMOS password--->   (not echoed)
  Your request is accepted.
  Login procedure starts.
  OK. Your initial program starts.<LF>
  Good luck!<LF>
  (beep, beep: the requester waits for a key; a key ends its process)
  ```

  The server's answer to `io(1)`, NI, is byte for byte
  `ref/pimm/fep.py`'s `login_record` for node `local`, RN `pmpsi`, RP
  `pmpsi`, UN `pimos`, UP `""`, ID 0 (§6.3).

**Where the route stops now.** The login requester has done its work
and waits for a key, and so does every other process. What is still
missing is the wire: the real PIMOS on the far side of
`fep_message_assembler`, in place of the probe (§6.4).

### 4.6 The window drawn (window milestones M0, M3, M5; 2026-11-25)

The same run now draws. The basis, the injections and the census are in
`../../psi/README.md`, "Window M0, M3, M5"; the plan is
`window_environment_plan.md` §5.

- **The font is read** (M0). `font:test_11.font`, which the held
  requester names (`initiate/1` @b9), is the HELD file from psdpim's
  FONT.DIR, placed under `font:` (directory and alias OURS) and decoded
  by the display device.
- **The window is drawn** (M3's core, M5). `standard_io_window`'s
  methods hand the drawing to a pane (`standin/window_pane.esp`, OURS),
  which sends device primitives (`simpos##bitmap_display`,
  `../../psi/windev.py`, OURS) that run as winfb commands. The held
  requester's own sends draw everything: its `create/3` size option
  makes a 40×7-cell window, `set_title/2` puts `Pimos remote login N` in
  the label strip, `putl/2` writes the prompts and the replies, the
  echo writes the typed name, and the password draws nothing.
- **The screen at the password prompt**, read back from the frame
  (`test_win_m5_login_screen`; `screens/login_pimos_password.png`):

  ```
  +- Pimos remote login 3 -------------------+
  | Enter FEP node name--------->            |
  | local                                    |
  | Enter your PIMOS user name-->            |
  | pimos                                    |
  | Enter your PIMOS password--->            |
  | #   (the block cursor; "sec" typed)      |
  +------------------------------------------+
  ```

  After the local login the requester's `clear/1` (@12c) empties it and
  the four replies follow (`screens/login_pimos_login.png`).

## 5. Next

B5 to B8 run as stand-ins (§4.4). The requester's dialogue and a local
login run (§4.5). Open, in order:

1. The wire from SIMPOS to PIMOS (§6.4): substring/7 from 16 to 32 bits
   in `fep_message_assembler` (@122), then a 620 request through
   `take_argument` in place of the probe's direct `io/4`.
2. The FEP census side items: blt 0d (10 stops in each FEP census) and
   blt a8 (2); `get_interpreter/2` and `has_been_reshaped/1`; the
   timer's `on_after` (303) with an alarm process; `terminate_core`'s
   PCB word 15. (`create/3`'s `instance_array` entry was measured in
   step 3l: it breaks every census row that creates a process outside
   the supervisor, so it stays out; `../../psi/README.md` "Step 3k".)
3. B4's SIMPOS device handlers (lost).

**B5's `directory`, examined in step 3i (PARTIAL; stood in by step 3l,
§4.4).** The interface is
printed (TR-056 p22-p24; TR-524 p36-p37), and the held callers settle
what a miss does: it fails, and the caller takes another clause.
- `pimfep##pimos_fep_superviser` local `full_pathname/1` @1bc: clause 1
  sends `retrieve/4` (@1c4) and cuts (@1c5). Its alternative (`c0`
  @1c6) asks `information/3` for the image file name and sends
  `retrieve/4` again (@1d7).
- `pimfep##pimos_file` local `remove/2` @1d7: clause 1 sends
  `retrieve/4` (@1de) and `is_directory/1`. Clause 2 (`c2` @1e3) is the
  other case.
- `check_file_size/1` @3d1 has one clause: `retrieve/3` (@3d7),
  `not_directory/1`, `size/2`. A miss fails it.

No stand-in was written. A hit needs entries, and the entries are the
file system's (B5's other half, not held). A directory with no entries
would only turn the census's `retrieve` refusals into failures, which is
not progress. A directory with entries would be OURS. So `directory`
waits for the file system.

## 6. SIMPOS to PIMOS (step 3m, 2026-11-25)

The connection is a local login, from the "Login PIMOS" item of the
system menu to PIMOS's login task. It runs on the PSI as far as the
login record PIMOS gets, and back from PIMOS's texts to the user's
window (§4.5, `test_step3m_local_login`). Cells were read with
`psi/fepread/ptfread.py` (pimfep, 2026-11-25).

### 6.1 The path

1. **The requester** (`pimfep##pimos_login_requester`, HELD). It is
   started from the system menu (B8) and puts its three prompts. Its
   `as_pimos_login_requester login_request/4` (@69b-6c9) then calls
   `get_fep_address/4` (`local` is a local login), `create_message/3`
   (the record, §6.2), `get_socket/3` (`:create(#port, S)`) and
   `connect_server/4` (@5cb-5e4). That last call asks the server class
   for its listening stream, makes a second port L, connects S to L
   and puts L on the stream. Then it calls `send_message/4`
   (`:send(S, Msg)`) and `receive/3` (`receive_block/7`). The receive
   waits on S: `who_is_connecting_to(S)` gives `[L]`, and the alarm
   watch is set to send a `timeout` message to S from L after 120000.
2. **The port** (`standin/port.esp`). TM-100 Fig. 3.8 prints its
   `send/3`: a port with one connected port puts the message, with its
   sender set, on that port. `connect/2` links the two ports both ways
   (INFERENCE). Each end receives on its own port what the other end
   sends.
3. **The server** (`pimfep##pimos_remote_login_server`, HELD, on the
   same PSI). PIMOS's `io(0, "local")` initiates it and makes its
   listening stream. Its `io(1, "  ")` runs `receive/2` and then
   `$or$0/4`: `accept/5` gets L from the stream, `remote_node_name/5`
   gives `local`, and `receive_message/5` (@3cf) runs. That last call
   runs `receive_block/3` (waits on L), `reassemble_message/3` (NI),
   `send_reply/4` (`Your request is accepted.`) and `grant_socket/4`.
   For a local login, `grant_socket/4` files L in the replier's socket
   table under the login's ID (@755-762). NI is the answer to PIMOS's
   620 `io(1)`.
4. **The replier** (`pimfep##pimos_remote_login_replier`, HELD). It must
   exist first. Its `io(0, "")` runs `initiate/1`, which initiates the
   socket table class (`pimos_remote_login_socket_table initiate/1`).
   Without that, `grant_socket/4` fails and the server answers `close`.
   `initiate_listener/1` takes its second clause, `true`, because the
   network subsystem is not installed. After that, every `io(1, [ID] ++
   Text)` finds L under ID and sends the text on it. `io(2, [ID])`
   removes the entry and sends `close`.
5. **The requester again.** It shows each text (`check_message/4`,
   `show_message/3`, `write/2`) until `close`. Then `wait/1` beeps
   twice and waits for a key. A key ends it (`exit_program/1`).
6. **PIMOS** (`login.kl1`, KL1). It decodes NI (`get_node_info/3`,
   1244-1258), checks UN and UP against `pimos.logins`, and answers
   through the replier (`../fep_services.md` §7.3). In step 3m a probe
   (OURS) sends those answers. `ref/pimm/fep.py` stands in for the
   same exchange on the PIMOS side.

### 6.2 The message formats (observed in the run, read against §6.5 of `../fep_services.md`)

| Message | From, to | Content |
|---|---|---|
| login request | requester S to L | the 512-element 16-bit `buffer_string`: `PimosLogin`, H = 0, L = 15 (the strings' total length), n1..n4 = 5 5 5 0, then RN `pmpsi`, RP `pmpsi`, UN `pimos`, UP `""`, zero-padded |
| accept reply | server L to S | `PimosLogin`, 0, 25, `Your request is accepted.` |
| text | replier L to S | `PimosLogin`, 0, the text's length, the text. The buffer is reused, so elements past the length are stale (`Good luck!<LF>itial program starts.`): the length word bounds the text |
| close | either | the atom `close`, not a string |
| timeout | the alarm, never sent | the atom `timeout` |
| NI | server to PIMOS (620 reply) | `[ID, len Node, len RN, len RP, len UN, len UP]` ++ Node ++ RN ++ RP ++ UN ++ UP; `reassemble_message/3` builds it from `IN`, the four lengths, `local` and the strings, then sets elements 0 and 1 |

### 6.3 The first link, checked in Python

`test_step3m_local_login` imports `ref/pimm/fep.py` read-only and
compares the server's NI with `fep.login_record`. NI, as big-endian
16-bit words, is

`0000 0005 0005 0005 0005 0000` + `local` `pmpsi` `pmpsi` `pimos`

It equals `login_record(id=0, node='local', rn='pmpsi', rp='pmpsi',
un='pimos', up='')`. It does **not** equal `fep.LOGIN`, whose RP is
`''`. The difference is RP only, and both values are OURS. The PSI
side's password is the one the probe boot logged in with (B7, `pmpsi`
/ `pmpsi`). `fep.py`'s comes from its own LOGIN constant. Section §6.5
of `../fep_services.md` says the real requester's RN and RP are never
null. That favours a non-empty RP, but `fep.py` (outside this step's
scope) was not changed.

### 6.4 What is missing

- **The wire.** The probe calls the server's and the replier's held
  `io/4` directly. On the real path PIMOS's 620 frames reach them
  through `fep_message_assembler`. That path still stops at
  `substring/7` taking 16-bit elements as 32-bit (@122, unwitnessed;
  the recipes census's `get_title/3` row).
- **The clock.** No alarm fires (`alarm_watch` stand-in), so the
  requester's 120000 and the server's 60000 timeouts never happen.
- **lia and tcpip.** Only `local_login` runs. `network_subsystem` is not
  installed (OURS), and the requester's `lia` and `tcpip` branches need
  `user_process_profile`, network groups and sockets that are lost.
- **RP.** See §6.3.
- **PIMOS itself.** The probe sends `login.kl1`'s texts in the order of
  §7.3 for a login that succeeds. It checks nothing.
