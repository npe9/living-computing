# The route to SIMPOS booting to a top level (2026-11-25)

The owner asked to "step back from the census" and write the concrete
path from what exists now (`psi/librarian.py`, `psi/kl0.py`,
`psi/espc.py` and the stand-ins in `psi/standin/`) to SIMPOS booting to
a top level. This page gives:

- what the PSI does first;
- which classes and processes must run, and in what order;
- what the console and the FEP must answer;
- which of these exist today, and what blocks each.

It then names the first step that is unblocked. Step 3i took it
(§4).

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
| B1 | The IPL loads SIMPOS from the fixed disk and links it | PRINTED prose: TR-087 p11 §5.3; TM-100 p18; `ESPtex/overview-e.tex`:1150-1180 | Substituted: `librarian.py` loads the 1,455 held class templates; `espc.py` compiles 36 stand-ins | SUBSTITUTED, OURS. The IPL image is not held (`layers/FORMATS.md` §4). |
| **B2** | **The hardware creates and activates the boot process, which runs the boot program** | PRINTED prose: TM-100 p6, p13; TR-056 p21; HELD: `pimmcsp##pseudo_pe_process` `release/1` | **Step 3i:** stand-ins `boot_process` and `as_boot_program` (INTERPOLATED); the machine's first process is the boot process; the printed `as_program` `invoke/1` runs a boot program in it | **DONE as a stand-in** (§4). The real boot program is lost. |
| B3 | The boot process brings itself under the supervisor, and the multiple-process environment starts on it | PRINTED prose: TR-056 p21; TM-100 p6; PRINTED code: `process:activate/2` (TM-100 Fig. 3.1) | `process:create/3` (INTERPOLATED) makes a second process, dormant | **BLOCKED**: `process:status/3`, `entry_of_invoke/2`, class `context` and the dispatcher are not printed; `boot_process`'s own `create` and `activate` are not printed; `kl0.py` runs one process. |
| B4 | Device handlers are instantiated and activated | PRINTED prose: TR-059 p30 (folio 28); TM-100 p6; PRINTED code: part of `interrupt_process` (TM-100 Fig. 3.4) | nothing | BLOCKED on B3. The handler classes and the device list are lost. |
| B5 | Supervisor services: the system directory, the library, users, worlds, the file system | PRINTED interfaces: TR-056 p20-p25 (library, `directory`, worlds), TR-524 App. A (file classes), TR-059 p23-p27 | `library` partly modelled in Python (step 3f); `pathname` HELD-SOURCE | BLOCKED in part: no `directory`, `user`, `world` or file system stand-in. |
| B6 | The coordinator and the window system start | PRINTED 1984 code: TR-046 p26-p28, TR-061 p13; prose `shell.md` §1.1; window mixins (TM-065, TM-125) | `pmacs_window` and `standard_editor` stand-ins, minimal | BLOCKED on B3: the coordinator is a process of its own. The window bodies are lost (`subsystems/window.md`). |
| B7 | Login: the user, the world, `me:login.com`, the system-menu items | PRINTED prose: TM-134 p66, p68; TM-181 p3; TM-229 p5-p6; HELD code: `pimfep##simpos_user` `create/4`, `setup_process/2` | the process slots `user` and `world` (PRINTED, TM-100 Fig. 3.1) with interpolated accessors | BLOCKED: `user` and `world` are known by USAGE only; reading `login.com` needs B5's file system. |
| B8 | The top level: the system menu starts a program in a new process | PRINTED dialogue: TM-134 p71 (`:create(#c,O). :create(#process,P). :activate(P,O).`) | — | BLOCKED on B3 (`activate/2`) and B6. |

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

### B3. Under the supervisor (BLOCKED)

The boot process must call its own `create` and `activate`, and other
processes must be activated. The printed `process:activate/2` (TM-100
Fig. 3.1, PDF p8-p9; `psi/standin/process.esp`) sends:

1. `:status(Process, dormant, on_activate)`;
2. `:entry_of_invoke(Program, Entry)`;
3. `:set_entry_point(Process!context, Entry)` and `:activate(
   Process!context)`, which are hardware.

None of these is printed. What is held:

- **`status/3`** has two call sites:
  - the printed `activate/2` (TM-100 Fig. 3.1), with `dormant,
    on_activate`;
  - `pseudo_pe_process release/1` @17a-17e (HELD, pimmcsp, found in
    step 3i), with `dormant, on_release`.

  So the third argument names the event (INFERENCE). Step 3h searched
  the held archives' source text only and found no definition. The
  compiled packages hold none for a process either (MEASURED
  2026-11-25 over the eleven packages): the only held `status/3`
  definitions are on pimscsi's own SCSI objects (`pseudo_scsi`,
  `scsi_communicator`), which do not inherit `process`.
- **`context`**: `simpos##context` is in pseudo_pe_process's pool (cell
  21). Its local `$or$1/3` (@31e-336) sends
  `create_for_pseudo_pe_process/7` to `#context` with the area atoms
  `default`, `query`, `middle`, and then `create_core/4`. Those are a
  context's creation, USAGE only.
- **The dispatcher**: TM-100 Fig. 3.4 elides it (`%RELEASE PROCESSOR
  ...`, `%ALLOCATE PROCESSOR ...`).
- **`kl0.py`** runs one goal at a time. A second process can be made
  (`process:create/3`, INTERPOLATED) but not run.

What would unblock it: a printed or held body of `status/3` and of
`context`; or a stand-in for both, INTERPOLATED, that gives up the
hardware context (OURS: a Python scheduler in `kl0.py`, running each
process's goal as a coroutine). The second is the most work and the most
OURS. It is the gate for every later step.

### B4-B6. Devices, services, coordinator (BLOCKED on B3)

- TR-059 p30 (folio 28), page image read 2026-11-25: "A device handler is
  instantiated and activated during a system boot-up procedure." A
  handler is an interrupt process, dispatched by hardware. The devices
  are disk, floppy disk, magnetic tape, printer and bitmap display
  (`overview-e.tex`, the kernel table), with keyboard and mouse.
- TR-056 p22-p25: the root directory is kept in a class slot of
  `directory` (`:root(#directory, Root)`). Pathnames are retrieved with
  `:retrieve`, and a process's world with `:world(#process, World)`.
  TR-524 Table 3 (p36) lists `directory` `retrieve/c` and `make/c`.
  `local_logical_file` (p37) sends `:retrieve(#directory, Lfile,
  Pathname, FullPathname)`.
- The coordinator is the background process that owns the system menu,
  the key table, the whiteboard and the abort handler (`shell.md` §1.1,
  §2.5). It needs a process of its own (B3).

### B7. Login (BLOCKED)

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
- Missing: `user` (`identify/4` is one census stop) and `world`, both
  known by USAGE only.

### B8. The top level (BLOCKED)

The 1.0 debugger dialogue (TM-134 p71, PRINTED) starts a program in a
new process: `:create(#c,O).`, `:create(#process,P).`,
`:activate(P,O).` A system-menu item does the same (TM-786 p5, TM-785
p6). Every way to start a program in its own process goes through
`activate/2`, which is B3.

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
  censuses measure: `process:status/3` (B3), `directory:retrieve/3,4`
  (B5), the `pmacs_window` protocol (B6), `stream:see/2` with a second
  process to put into it (B3).

## 4. The step taken: B2 (step 3i)

B0 and B1 are substituted. B2 is the first step whose inputs exist:

- printed prose that says what the boot process is;
- a held call site;
- the printed `as_program` `invoke/1`, which runs a program in the
  calling process.

B3 onward are blocked (§2).

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

The test also pins the B3 blockers:

- `:activate(Boot, Program)` and `:create(#boot_process, X)` refuse with
  the override message.
- A second process from `process:create/3` has the boot process as its
  parent, and its `activate/2` refuses at `process:status/3`.
- The held `pseudo_pe_process release/1` stops at `status/3` with
  `(dormant, on_release)`.

The census effect and the fault injections are in `../../psi/README.md`
("Step 3i: the boot process").

## 5. Next

B3 is the gate. In order of preference:

1. Find a body of `status/3`, `entry_of_invoke/2` or `context`. TM-100
   pp7-10 print none. The search should go on to the compiled pimmcsp
   process subclasses, which call these (`pseudo_pe_process`
   `activate/1` @18e-1b0: `get_number/3`, `set_start_code/2`,
   `add_program/2`, `create_name/1`, `set_status/2`, `set_pe_status/2`,
   `suspend/2`), and to the TR/TM pages on the supervisor (TR-056,
   TR-059, TM-100 §2.1).
2. Failing that, a scheduler in `kl0.py` (OURS), with `status/3` and
   `entry_of_invoke/2` INTERPOLATED from their two call sites and
   TM-100 p6 ("the entry of the main program is defined as an instance
   predicate of the program", i.e. `goal/1`).

Then B7's `user` and `world` (USAGE) and B5's `directory`. Then a
coordinator process with a system menu that has the two PIM/m items of
§1.
