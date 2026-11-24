# SIMPOS shell and top level: specification from the held evidence

SIMPOS, the operating system of ICOT's PSI machines, is lost. This document puts together what the
held reports, screenshots, IFS application sources and compiled packages say about its top level:
boot to login, the login file, the system menu, the Coordinator, how a program is started, the
shell, the debugger as listener, error windows, interrupt keys and logout. The aim is that a
stand-in can be written from it which behaves on screen, and towards the held programs, like the
real thing. Anything interpolated is labelled INFERENCE.

Sibling documents: `window.md` (window classes, the window manipulator itself), `librarian.md`
(Librarian, packages, command files). This file mentions those only where the top level invokes
them.

---------------------------------------------------------------------------------------------------

## 0. Scope, conventions, sources, versions

### 0.1 Scope

In scope: the classes of `partition_shell.tsv` (38 classes: as_program and its relatives, process,
coordinator, user, world, messenger, stop_watch, throw/error/failure/abort_handler, the debugger
family, inspector, interpreter, trace, call_counter). Also the top-level texts and dialogues
(system menu, login file, shell, debugger, error windows) whatever class owns them.

### 0.2 Conventions

- **Arity counts the receiver**, as `required/` does: `:create(#process,P)` is `create/2`,
  `:goal(Obj)` is `goal/1`. `printed/classes.tsv` does not count it; its numbers were converted.
- `class`/`instance` in the tables = class method (receiver a class object `#c`) or instance method.
- **Grades**:
  - PRINTED: code or dialogue printed in an ICOT report.
  - PRINTED-INTERFACE: a signature or call form printed without a body.
  - PROSE: described in text (reports, IFS INSTALL/README files).
  - SCREENSHOT: read off a screen image (report figure or video frame).
  - USAGE: meaning taken from application code that calls SIMPOS (IFS source, or a compiled
    package run under kl0).
  - COPY: code that is itself a copy of SIMPOS. Here this means the CAL debugger
    (`cal-esp/deb2.12/`, DEC-20 directory `<SIMPOS.E.DEBUGGER>`) and cil's Librarian copy
    (`spec_ds##library_utility`).
  - INFERENCE: this document's interpolation.
- **Citations**:
  - Reports: `TM-134 p69` = PDF page index of `lit/trtm/tm0134.pdf`. The folio is given when the
    notes give it.
  - IPSJ papers by record id + page (`IPSJ 36239 p4`). Mitsubishi Denki Giho as `Giho 8609 p16`
    (PDF page of `journals/mitsubishi_giho/8609.pdf`).
  - Video as `segment@seconds` (`simpos.wmv@10`).
  - IFS source as archive-relative `path:line`.
  - Compiled packages as `pkg##class pred/arity (ptf)`.
  - Pointers to the readers' notes as `(notes: x.md §n)`. The notes are under `subsystems/notes/`.
- `«?»` marks an illegible glyph. Japanese is translated (TRANSLATION) and quoted in Japanese only
  where the word itself matters.
- Copyright rule: papers are paraphrased. IFS source is described, quoting at most a line. ICOT
  TR/TM listings are transcribed.

### 0.3 Sources by weight

| weight | source | what it gives | era |
|---|---|---|---|
| 1 | TM-100 p8-p11 (printed source, `printed/listings/tm0100_p08..p11.esp`) | `process` and `as_program` bodies | 1985 (design 1984) |
| 1 | TR-046 p26-p28, TR-061 p13 (printed source) | Coordinator `default_translation_table`, `system_menu` | 1984 design |
| 2 | TM-134 p66-p72 (Mitsubishi ESP programming text) | login, system menu, debugger dialogue, process start | 1.0, 1985 |
| 2 | TM-181 p3-p5, TM-143 p3, TM-229 p5-p7 = IPSJ 36239 p4-p7, Giho 8609 p16 | system menus, debugger, error window | 1.x-2.50, 1985-86 |
| 2 | TM-785 p3, p6, p25; TM-786 p4-p5 | login-file menu entries, `$ call`, librarian error menu | 5.0, 1989 |
| 2 | TM-112 p7-p19, TM-115 p25, p109; TM-125 p8, p23; TM-126 p6 | cold boot, status line, double right click, 1.00 debugger | 1.00, 1985 |
| 3 | ICOT museum video (`simpos.wmv`, `esp.wmv`, `melco.wmv`) | system menu, Debugger Menu, status line | 2.50 / "A00", ~1986-87 |
| 3 | IFS `login.com` files (5), INSTALL/README prose (15 archives) | login-file language, shell lines, logout, user registration | 3.0-8.1, 1988-93 |
| 3 | IFS application code (B-scan, `required/requirements.tsv`) | USAGE of every method below | 3.0-8.1 |
| 3 | COPY: `cal-esp/deb2.12/` (SIMPOS debugger derivative), `cil/src/ds_bep.esp:1773-3518` (Librarian copy) | debugger internals, abort keys | 1986-91 |
| 4 | compiled packages (`ptf.md`): pimfep, pimmcsp, kappa, ... | login stand-in, coordinator `information/3`, process modes | 1989-94 |

### 0.4 Versions

| tag | date | evidence of the top level |
|---|---|---|
| design | 1984 | TR-046, TR-057, TR-061, TM-079: Coordinator, experts, translation table, no shell |
| 0.7 / 0.8 | 84/12, 85/2 | timeline only (TM-229 p9; IPSJ 36239 p8) |
| 1.00 | 85/4 (screens May-Jul 85) | TM-112, TM-115, TM-125, TM-126, TM-134; goal prompt `:-` |
| 1.x / 1.5 | 85/9-85/11 | TM-143 (system menu with `generalist`, `terminal`) |
| 2.00 | 86/3 (screens Apr 86) | Giho 8609 p16; goal prompt `?-` |
| 2.10 | Jun 86 | TM-181. trtm_progsys read the footer as 2.10 at 96 ppi x3-6; `printed/listings/TM-181_p03_system_menu.txt` and `trtm_window.md` say 2.19. **This document follows 2.10.** |
| 2.50 | 86/7 (screens Sep 86) | IPSJ 36239 = TM-229; video `melco.wmv@50` |
| A00 | ~1986-87? | video status line `SIMPOS Version A00` (`esp.wmv@108`). INFERENCE: Mitsubishi product numbering, like the "B00" of Giho 8907 p34. **Not** the same as PSI-III's A22. |
| 3.0-5.x | 86/12-1989 | sum, knov archives; TM-785/786 (screens 5.0) |
| 6.x, 7.x, 8.x | 1989-93 | cil (6.1 copy, 8.1), disc 6.2, cal-esp/papyrus 7.0, kwic/fuzclust 7.1, kappa2 7/8 |
| A22 | PSI-III | kappa2/INSTALL:20 |

**Where sources conflict, the spec follows the held programs (3.0-7.1/A22)** and lists the
earlier form as a variant with its version.

---------------------------------------------------------------------------------------------------

## 1. Class structure

### 1.1 The pieces of the top level and who owns them

| piece | class(es) | grade | citation |
|---|---|---|---|
| Coordinator: the background process that owns the system menu, the key table, the whiteboard and the abort handler | `coordinator` (class object `#coordinator`; also `simpos##coordinator`) | PROSE (1984-86), USAGE (1988-93) | TR-057 p7; TR-061 p7; TM-225 p7; cil/src/es_gin.esp:70; cal-esp/deb2.12/dmenu.esp:865 |
| key bindings | `default_translation_table` (1984) | PRINTED | TR-046 p28; TR-061 p13 |
| system menu | `system_menu` (1984), built as a `multi_column_menu` | PRINTED | TR-046 p27 |
| an expert (1984) | `e_process` (is-a process) with `e_program`, `e_window`, `e_port`; pool `e_process_pool` | PROSE | TR-061 p12 Fig 1; TR-057 p7; TM-079 p14 |
| a program | user class with nature `as_program`, entry `:goal/1` | PRINTED | TM-100 p11; TM-134 p69 |
| program kinds | `as_server_program`, `as_interrupt_program`, `as_trap_program`, `as_boot_program`, 1.00 `as_e_program` | USAGE / PROSE | ptf.md S1; TM-115 p109; STRUCTURE §10 |
| a process | `process` (subclasses `interrupt_process`, `boot_process`) | PRINTED | TM-100 p7-p13 |
| the user | `user`; registration database `user_list`; `user_process_profile` | USAGE | kappa2 sources; ptf.md S2 |
| logical names | `world` | USAGE | pimfep##simpos_user create/4 (ptf) |
| message boxes | `messenger` (class methods only) | USAGE | cil/src/INSTALL.esp:23 |
| exceptions | `throw`, `error`, `failure`, `event`, `as_event_handler`, `abort_handler` | USAGE | §2.10 |
| listener | `debugger` (system-menu target), `interpreter`, `inspector`, `trace` | SCREENSHOT/USAGE | §5.4 |
| shell | system-menu target `shell`; `shell_transient` login item | PROSE/USAGE | §5.3 |

### 1.2 Programs: the `as_program` family

```
as_program                      printed source TM-100 p11 (1985): create/2, goal/1, assign/1,
  |                             resign/1, resign_core/1, invoke/1
  +-- (user program classes)    nature as_program; define instance :goal/1
as_e_program                    1.00 only: "inherit ... as_e_program and add an entry in the
                                system menu" (TM-115 p109, PROSE)
as_server_program               started by a network connection request (§2.3)
as_interrupt_program            nature of pimscsi classes (ptf); no source user
as_trap_program                 nature of pimmcsp##yield_trap_handler (ptf)
as_boot_program                 the program run by the boot process (TM-100 p6, p13; STRUCTURE §10)
```

- **Census** (USAGE). 170 IFS user classes in 14 programs reach a program nature: 164
  `as_program`, 6 `as_server_program`, plus 4 `as_event_handler` handlers (notes: ifs_libshell §1.4).
  In the compiled packages 143 classes reach `simpos##as_program`; 102 declare it (notes: ptf S1).
- **Combination.**
  - A program class mixes `as_program` with anything: `as_class_with_lock, as_program`
    (kappa2/kappa2/utility/tool/LOADER.ESP:20-22), `as_program, with_user_window` (TM-134 p70).
  - A window is not part of `as_program`. Programs create their windows in `:goal/1` (TM-134 p70;
    TM-153 p28; video `esp.wmv@129-149`).
  - The 1984 design gave each expert an automatic `e_window` (TR-061 p7). The 1985+ direct path is
    the one the held programs use (VARIANT, notes: trtm_window W8).
- `as_demo_program` (IPSJ 36239 p5) is **not** a SIMPOS class. The Librarian screenshot on the same
  page catalogues it out of the user's `demo.esp`, as the first class of that file. Its
  `:initiation_end/1` is therefore application code.

### 1.3 Process

`process` has natures `with_link, waiting_frame` and class slots `ready_queue`, `instance_array`
(TM-100 p7, PRINTED). Instance slots (TM-100 p8, PRINTED): `context`, `priority`, `sub_priority`,
`mask_count`, `suspend_reason`, `suspend_reasons`, `suspend_flag`, `status` (nil = dead, dormant,
suspended, ready, active), `parent_process`, `children_processes`, `killer_process`,
`invocation_stack`, `resources`, `world`, `user`, `interpreter_instance`, `clock`.

So a process carries a world (logical names) and a user. A new process inherits both from its
creator (STRUCTURE §2; TM-100 p8). Login is the act of giving the first user process a user and a
world (§4.1).

---------------------------------------------------------------------------------------------------

## 2. Classes and methods

Every row of `coverage_shell.tsv` (115 required methods) is in the tables below, with its use count
`uses/programs`. "UNSPECIFIED" = required, but nothing held says what it does. "misattributed" =
the B-scan put a send on this class that belongs elsewhere; it is kept so the surface stays whole.
Methods that are not in `requirements.tsv` but appear in the evidence are added, with `-` for
uses.

### 2.1 `as_program`

**Role.** Mixin that makes a class a program: something a process runs. TM-100 p11 prints part of
the class (PRINTED, 1985):

```
class  as_program  has
:create(Class, Program) :- !, :new(Class, Program), ! ;
instance
:goal(Program) ;                  % default top-level goal, overridden by the user
:assign(Program) :- !, :self(#process, Process), :add_program(Process, Program), ! ;
:resign(Program) :- !, :self(#process, Process), :remove_program(Process, Any_program),
        ( :no_program(Process), !, :die(Process) ; true ), ! ;
:resign_core(Program) :- !, :self(#process, Process), :remove_program(Process, Any_program), ! ;
:invoke(Program) :- !, :assign(Program),
        ( :goal(Program), !, :resign(Program) ; :resign(Program), fail ), ! ;
end.
```

When a program is invoked, it is pushed on the process's invocation stack and `:goal(Program)`
runs. When the goal ends it is popped, and a process whose stack empties dies (TM-100 p11 prose).
TM-134 p72 says the same for users: when the goal ends, by success or failure, the process
terminates and the instance's slots are lost (PROSE, 1.0).

| kind | method/arity | uses | args and meaning | grade | citation |
|---|---|---|---|---|---|
| class | `create/2` | 55/10 | `:create(Class,Obj)`: calls `:new(Class,Obj)`. Users override it, or hang demons on it (27 IFS classes, 25 compiled), to pass state or set slots. TM-134's example puts slot setup in an `after :create(Class,Obj)` demon | PRINTED | TM-100 p11; TM-134 p69-70; kappa2/kappa2/utility/tool/CCTPR.SHELL:11-12; pimmcsp##multi_psi_csp_manager create/2 after-demon (ptf) |
| class | `new/2` | 39/7 | `:new(Class,Obj)`, the plain allocator. Its owner is the root class, not as_program (INFERENCE: every class answers it, TM-115 p12). Also typed at the debugger | PRINTED | TM-100 p11; TM-134 p67; pimfep##remote_pimfep_executor new/2 after-demon (ptf) |
| class | `get_slot/3` | 6/1 | `:get_slot(#c,SlotName,Value)`: read a class slot by name, e.g. `:get_slot(#talk_window,input_window,W)`. Owner is the root object class (INFERENCE). misattributed | USAGE | fuzclust/fuzclust/src/input.talk:28; fuzclust/fuzclust/src/hikaku.comp:932 |
| class | `set_slot/3` | 4/1 | class-slot write by name. misattributed (as above) | USAGE | fuzclust/fuzclust/src/ahp_tool.graph:23 |
| class | `whiteboard/2` | 5/1 | really `:whiteboard(#simpos##coordinator,WB)`. The B-scan did not resolve the qualified receiver. misattributed: see coordinator | USAGE | cil/src/es_gin.esp:70 |
| class | `goal/2` | 2/1 | `:goal(Class,ArgL)`, kwic's macro-inserted class method. It saves the standard devices, converts ArgL (§5.3.4), does `:new`, `:save_arguments`, `:goal/1`, then restores the devices. A kwic stand-in for a shell call, not SIMPOS (INFERENCE) | USAGE | kwic-esp-002/kwic-esp/src/v2_tool.mac:39-47; dbDM.esp:30 |
| class | `ordinary/5` | 1/1 | sent to `#display_board`, a gog class. misattributed, application | USAGE | gog-esp/PBM_CMD.ESP:104 |
| class | `select_kakari_structure/3` | 1/1 | icotext's own class method. misattributed, application | USAGE | icotext/src/kkr_main.esp:90 |
| instance | `goal/1` | - | `:goal(Obj)`: **the program body**, run in the process that the program was activated in. Defined by 165 of the 170 IFS program classes. The as_program default has no clauses | PRINTED | TM-100 p11; TM-134 p69; TM-115 p109; TM-786 p5; ifs_libshell §1.4 |
| instance | `assign/1`, `resign/1`, `resign_core/1`, `invoke/1` | - | invocation-stack protocol, as printed above. `:invoke` is what activation calls (INFERENCE from TM-100 p8: `:activate` takes `:entry_of_invoke(Program,Entry)`) | PRINTED | TM-100 p11 |
| instance | `exit/1` | - | called on the program when it is ended from outside (INFERENCE). Demons on it in pimfep, pimmcsp and pimscsi prove SIMPOS defines a primary | USAGE | ptf S1; cil/src/ms_cdn.esp:53-54 |
| instance | `cut_off/1` | - | cleanup hook, apparently on kill (INFERENCE); 13 class / 6 instance definitions | USAGE | cil/src/ms_cdn.esp:120-121; kwic-esp/src/searchMan.esp (before:cut_off) |
| instance | `current_state/2` | - | defined by programs: fills a SIMPOS `initiation_table` with `{Key,Value}` pairs "for SIMPOS process saver" | USAGE + PROSE (comment) | cil/src/ms_cdn.esp:537-548; cil/src/ds_brs.esp:2654 |
| instance | `set_slot/3` | 161/2 | `:set_slot(Obj,SlotName,Value)`: write an instance slot by name. Neither fuzclust nor knov defines it. Owner is the root object class (INFERENCE). misattributed to as_program because the receivers are programs | USAGE | fuzclust/fuzclust/src/ahp_menu.comp:19-22; pimmutil##dummy_fep overrides it (ptf) |
| instance | `get_slot/3` | 151/2 | `:get_slot(Obj,SlotName,Value)`, reflective read. As above | USAGE | fuzclust/fuzclust/src/ahp_menu.comp:37 |
| instance | `get_arguments/2` | 10/1 | `:get_arguments(Prog,Args)`: the shell command line as a **list of strings**; an option is split into sign and name strings (§5.3.4) | USAGE | kappa2/kappa2/utility/tool/CCTPR.SHELL:29-31; LDTPR.SHELL:80-88 |
| instance | `parse_arguments/2` | 3/1 | `:parse_arguments(Prog,{Positional,Named})`. Named = list of `{NameString,Value}`; Value `"+"`/`"-"` for options | USAGE | kwic-esp-002/kwic-esp/src/dbDM.esp:41; dtCompiler.esp:42; v2_tool.mac:92-102 |
| instance | `save_arguments/2` | - | setter that stores the argument list before `:goal/1` (INFERENCE: as_program; unattributed in requirements.tsv:3353) | USAGE | kwic-esp-002/kwic-esp/src/v2_tool.mac:45 |
| instance | `initiation_table/2` | 1/1 | `:initiation_table(Prog,T)`: T is the table saved for this program by the process saver, or 0 when none. Read at "login initiation". INFERENCE: this is probably a real as_program method, the program side of the login auto-creation of PSs (TM-229 p6). It is the one CAL-debugger row that is not counted as misattributed | USAGE (COPY) | cal-esp/deb2.12/init.esp:656 |
| instance | `initial_setting/2` | 1/1 | `:initial_setting(Prog,T)`: apply that table. Defined by the CAL debugger; whether SIMPOS calls it is UNSPECIFIED | USAGE (COPY) | cal-esp/deb2.12/init.esp:658 |
| instance | `class_object/2` | 8/3 | `:class_object(Obj,Class)`: the class object of an instance. A root-object method (INFERENCE) | USAGE | cal-esp/deb2.12/deb.esp:179; kwic-esp-002/kwic-esp/src/kwMan.esp:222 |
| instance | `refute/3` | 7/1 | `:refute(Obj,Method,ArgVector)`: send Method with the vector's elements as arguments. A generic method on objects, printed for windows in TM-785 | PRINTED-INTERFACE (unowned) | TM-785 p32; euod/PROOF/proof1.esp:89; TM-388 App. G |
| instance | `method/3` | 1/1 | `:method(Obj,Name,Arity)`: succeeds if Obj has that method. papyrus uses `:method(Object,show,1)` to test whether a slot holds a live object (USAGE) | USAGE | papyrus_src/demo/EDITOR/editor_def.esp.1:38 (papyrus inner source.tar); cil/src/ds_bep.esp:3189-3203 |
| instance | `delete_items/2` | 1/1 | a menu or window method, sent to a window (`:delete_items(Window,Id)`). misattributed; see window.md | USAGE | euod/RULED/ruled1.esp:950 |
| instance | `do_state/3` | 9/1 | CAL-debugger internal (`as_state_menu_processing`). misattributed | COPY | cal-esp/deb2.12/purs.esp:621; stat.esp:23 |
| instance | `get_state_switch/4` | 7/1 | CAL-debugger internal. misattributed | COPY | cal-esp/deb2.12/purs.esp:637 |
| instance | `get/3` | 6/1 | CAL-debugger internal. UNSPECIFIED. misattributed | COPY | cal-esp/deb2.12/purs.esp:228 |
| instance | `set_leash/2` | 6/1 | CAL "Mode_Leash" window (`as_gate_menu_processing`). misattributed | COPY | cal-esp/deb2.12/purs.esp:597; gmenu.esp:22 |
| instance | `get_leash/2` | 1/1 | as above | COPY | cal-esp/deb2.12/purs.esp:600 |
| instance | `mam_do_menu/2` | 5/1 | `as_debugger_menu_processing`. misattributed | COPY | cal-esp/deb2.12/purs.esp:787; dmenu.esp:17 |
| instance | `get_inspector/2` | 2/1 | as above: the debugger's inspector slot | COPY | cal-esp/deb2.12/purs.esp:500 |
| instance | `set_mode/3` | 3/1 | CAL entry gate mode. misattributed | COPY | cal-esp/deb2.12/purs.esp:587 |
| instance | `set_prompt/2` | 1/1 | super-command `set_prompt("system_mode>")`. misattributed | COPY | cal-esp/deb2.12/purs.esp:143, 975-1021 |
| instance | `reset_prompt/1` | 1/1 | super-command. misattributed | COPY | cal-esp/deb2.12/purs.esp:145 |
| instance | `get_default_class/2` | 1/1 | CAL internal. UNSPECIFIED | COPY | cal-esp/deb2.12/purs.esp:168 |
| instance | `reset_window/1` | 1/1 | super-command `reset_window` | COPY | cal-esp/deb2.12/purs.esp:179 |
| instance | `set_debugger_font/2` | 1/1 | super-command font items | COPY | cal-esp/deb2.12/purs.esp:340 |
| instance | `select_font_from_menu/2` | 1/1 | super-command `font` | COPY | cal-esp/deb2.12/purs.esp:494 |
| instance | `select_package_from_menu/2` | 1/1 | super-command `package` | COPY | cal-esp/deb2.12/purs.esp:710 |
| instance | `with_vars_window/2` | 1/1 | super-command `with_vars_window` | COPY | cal-esp/deb2.12/purs.esp:552 |
| instance | `set_title/1` | 1/1 | CAL internal (retitle the debugger window) | COPY | cal-esp/deb2.12/purs.esp:706 |

Slots read on as_program receivers (`!code`, `!selected_key`, `!menu`, `!debugger_window`,
`!trace_pane`, `!default_package`, `!parent_process`, `!p` ...) are the applications' own slots
(USAGE, requirements.tsv). TM-100 p11 declares no as_program slot.

### 2.2 Other program natures

| class | kind | method/arity | uses | meaning | grade | citation |
|---|---|---|---|---|---|---|
| as_e_program | nature | - | - | 1.00 nature for programs started from the system menu. Absent later; TM-786/785 put plain as_program classes in the menu | PROSE | TM-115 p109 |
| as_interrupt_program | nature | - | 1 (ptf) | nature of a pimscsi class; an interrupt-process program (INFERENCE from STRUCTURE §2) | USAGE | ptf S1 |
| as_trap_program | nature | - | 1 (ptf) | nature of pimmcsp##yield_trap_handler | USAGE | ptf S1 |
| as_boot_program | nature | - | - | program run by the single `boot_process` | PROSE | TM-100 p6, p13; TR-056 p21 |

### 2.3 `as_server_program`

**Role.** A program started on a PSI when a remote node asks for a connection by service name. The
requester uses `:spawn(#net_spawn_user,Node,"talk_output",Line,nil,_,Status)`. The server's
`:goal/1` first accepts the request, then reads who asked. USAGE (fuzclust talk, 7.1).

| kind | method/arity | uses | args and meaning | grade | citation |
|---|---|---|---|---|---|
| instance | `give_answer/3` | 6/3 | `:give_answer(Prog,Answer,nil)`: answer the connection request. Answers seen: `success` (accept), `invalid_user` (refuse) | USAGE | fuzclust/fuzclust/src/input.talk:30; fuzclust/fuzclust/src/output.talk:41, 47; pimfep##remote_pimfep_invoker goal/1 (ptf) |
| instance | `convert_con_req/6` | 4/2 | `:convert_con_req(Prog,Node,Type,User,_,_)`: decode the connection request into requesting node, type and user | USAGE | fuzclust/fuzclust/src/input.talk:31; fuzclust/fuzclust/src/output.talk:27 |
| instance | `get_line/2` | 4/3 | `:get_line(Prog,Line)`: the network line object (an `nline`) of this connection; freed with `:free(Line)` | USAGE | fuzclust/fuzclust/src/output.talk:29 |
| instance | `get_slot/3` | 4/1 | reflective slot read (as 2.1). misattributed | USAGE | fuzclust/fuzclust/src/envget.ctl:19 |
| instance | `set_slot/3` | 3/1 | reflective slot write | USAGE | fuzclust/fuzclust/src/part.grape:128 |

### 2.4 `process`

Printed source exists for creation, activation, resume and suspend (TM-100 p7-p13, PRINTED;
summarised in STRUCTURE §2). The hard limit is 63 processes, about 50 of them usable (TR-056 p19).

| kind | method/arity | uses | args and meaning | grade | citation |
|---|---|---|---|---|---|
| class | `self/2` | 211/10 | `:self(#process,P)`: the current process | PRINTED (in as_program source) | TM-100 p11; cal-esp/cal2.12/control.esp:65 |
| class | `create/2` | 64/11 | `:create(#process,P)`: a new dormant process with a hardware context. It inherits world and user from the creator; priority 0. Fails when contexts run out | PRINTED | TM-100 p8; TM-134 p71; TM-112 p8 |
| class | `create/3` | 9/3 | `:create(#process,P,Mode)`. Mode is a 4-element list: `[free,free,query,middle]` (cil), `[free,default,free,middle]` (kappa), `[free,default,free,small]` (pimfep), `[free,free,free,free]` (kappa). INFERENCE: three area limits, then priority `small`/`middle` (or a query mode) | USAGE | cil/src/ms_cdn.esp:347-348; kappa2/kappa2/utility/tool/LOADER.ESP:53,65; pimfep##pimos_timer create_timer/9 (ptf) |
| class | `get_number/3` | 29/5 | `:get_number(#process,P,N)`: the process number, which window labels and error titles show | USAGE | cil/src/ms_cdn.esp:219-220; cal-esp/deb2.12/winpar.esp:127-131 |
| class | `get_process/3` | 3/2 | `:get_process(#process,P,N)`: the process with number N | USAGE | cal-esp/deb2.12/purs.esp:544 |
| instance | `activate/2` | 60/12 | `:activate(P,Program)`: set the entry point from the program (`:entry_of_invoke`), make P ready; `:goal(Program)` runs in P. **Returns at once** | PRINTED | TM-100 p8-p9; TM-134 p71; TM-225 p6 |
| instance | `activate/3` | - | `:activate(Process,Program,Goal)`: 1984 VARIANT | PRINTED | TR-056 p18 |
| instance | `terminate/1` | - | `:terminate(P)`: end process P | PRINTED-INTERFACE | TM-225 p6 |
| instance | `exterminate/1` | 8/3 | `:exterminate(P)`: kill another process. Used for timer and helper processes. INFERENCE: = terminate in later versions | USAGE | kappa2/kappa2/kernel/svm/SVCTL.ESP:800 |
| instance | `post/1` | 1/1 | `:post(P)`: sent to the process of an already-running tool after `:show`-ing its window again, instead of creating a new one. INFERENCE: wake (resume) the process | USAGE | papyrus_src/demo/EDITOR/editor_def.esp.1:25-28 |
| instance | `set_package/2` | 2/1 | `:set_package(P,Pkg)`: the process's default package, which governs unqualified class names typed in it | USAGE | chal/cal_start.esp:13; cil/src/ds_bep.esp:3037 |
| instance | `get_package/2` | - | read it | USAGE | cil/src/ds_bep.esp:3147 |
| instance | `set_area_limit_execution/7` | 2/1 | `(P,free,default,free,middle,nil,nil)` in kappa shell commands; `(P,free,free,free,free,nil,nil)` in gog and the CAL debugger's `area_limit_off`. INFERENCE: three area limits (heap/stack/trail?), priority, two hooks | USAGE | gog-esp/DEBUG.ESP:89; kappa2/kappa2/utility/tool/CCTPR.SHELL:21-46; cal-esp/deb2.12/purs.esp:541-545 |
| instance | `set_sub_priority/2` | - | `:set_sub_priority(P,2)` before activate | SCREENSHOT | Giho 8609 p16 |
| instance | `standard_input/2`, `standard_output/2`, `standard_message/2` | - | the process's three standard streams. For the shell and the debugger they are the window (TM-388 p82). A shell command reads stdin, writes stdout, and prompts on the message stream | PRINTED (macro text) + USAGE | TM-388 p82; kappa2/kappa2/utility/tool/KSTPR.SHELL:31-48 |
| instance | `set_standard_input/2`, `set_standard_output/2`, `set_standard_message/2` | - | rebind them | USAGE | kwic-esp-002/kwic-esp/src/v2_tool.mac:39-47 |
| instance | `user/2` | - | the process's user object | USAGE | cil/src/ds_bep.esp:3142-3145 |
| instance | `set_user/2`, `set_world/2`, `set_access_mode/2`, `set_passwords/2` | - | login-time setup of a process (receiver INFERENCE) | USAGE | pimfep##simpos_user setup_process/2 (ptf) |
| instance | `catch/5` | - | `:catch(P,"Skip this class",Obj,Method,ArgVector)`: run the call. If an error menu comes up it gains the item `Skip this class`, whose choice makes the call fail (INFERENCE) | USAGE (COPY) | cil/src/ds_bep.esp:2007-2008 |
| instance | `throwing_hook/7` | - | `(P,O1,M1,A1,O2,M2,A2)`: run O1:M1(A1), with O2:M2(A2) as cleanup on a throw (INFERENCE) | USAGE (COPY) | cil/src/ds_bep.esp:2186-2188 |
| instance | `refute_in/5` | - | `:refute_in(P,[{#error,#failure,_}],Obj,Method,Args)`: run the call with a catcher for events of the listed classes; the call fails instead of raising the error menu (INFERENCE) | USAGE | kappa2/kappa2/kernel/hlc/HLCMNG.ESP:212-222 |
| instance | `get_library_environment/3`, `set_library_environment/3`, `check_library_environment/3` | - | per-process Librarian modes; see librarian.md | USAGE (COPY) | cil/src/ds_bep.esp:3229-3238 |

### 2.5 `coordinator`

**Role** (PROSE). A background ("work-behind") process. It is not an expert. It manages the
experts through the key table of each window. It sends key commands to experts, creates, deletes
and activates them through `system_menu`, and lets experts communicate through the whiteboard
(TR-057 p7-8, 1984). By 1986 it also has "a UNIX-like shell", always runs in the background, can be
called at any time, and can force-terminate a running program (TM-225 p7). The 1986 structure
figure puts coordinator and shell in one cell (IPSJ 36239 Fig 2-1). The 1984 design had no
shell: "there is no explicit supervising process such as Shell in Unix" (TR-057 p7).

**1984 data model** (PROSE, TR-061 p12 Fig 1; TR-057 p8; TM-079 p14):
- An expert = `e_process` (a process), which has an `e_program`, an `e_window` (its communication
  window) and an `e_port` (message box for pre-agreed partners).
- All experts are in an `e_process_pool`.
- Each user has a **directory to create experts**: expert names and program names. It inherits
  from the system's common directory (the standard experts). The user may change it, and the key
  command table too. This directory became the login file's `menu` item (INFERENCE).

| kind | method/arity | uses | args and meaning | grade | citation |
|---|---|---|---|---|---|
| class | `login_user/2` | 5/2 | `:login_user(#coordinator,Name)`: the logged-in user's **name** (stored as `user_name`) | USAGE | kappa2/kappa2/kernel/net/REMAITR.ESP:230; kwic-esp/src/kwMan.esp:505; kappa##kappaMDU_kappa_interface create/2 (ptf) |
| class | `get_instance/2` | 4/3 | `:get_instance(#coordinator,C)`: the coordinator object | USAGE | cal-esp/deb2.12/dmenu.esp:865; kwic-esp/src/searchMan.esp:278 |
| class | `information/3` | 3/1 | `:information(#coordinator,Key,Value)`: **the value of a user item of the login file** (§4.2.6). kwic's comment says `login_file_item` is "the item name used when the init file name is given in login.com". Keys seen: `kwic_constant_file_path`, `drt_alias`, `query_yourei_constant` (value `on`), `pimfep_superviser_initial_information` (a 4-list), `pimos_login_additional_function` (`on`). INFERENCE: it fails when the item is absent, since every caller has a fallback clause | USAGE + PROSE (comment, kwic doc) | kwic-esp/src/systems.esp:297, 327, 364; kwic-esp-002/kwic-esp/src/dbUtil.esp:225; kwic-esp/doc/classSpec.IO1:345-351; pimfep##pimos_fep_superviser create_window/1, pimfep##pimos_login_requester read/4 (ptf) |
| class | `whiteboard/2` | 2/1 | `:whiteboard(#coordinator,WB)`: the system whiteboard object. Also sent as `#simpos##coordinator` (5 uses booked under as_program). cil defines its own `spec_ms##coordinator` (cil/src/ms_cdn.esp:43), so cil's unqualified sends may be to that class; kappa's and the qualified cil send are certainly SIMPOS's | USAGE | kappa2/kappa2/user_if/pb/pcn.esp:4840; cil/src/es_gin.esp:70; cil/src/es_ins.esp:80 |
| instance | `get_whiteboard/2` | - | `:get_whiteboard(C,WB)` on the instance | USAGE (COPY) | cal-esp/deb2.12/dmenu.esp:866 |
| instance | `abort/2` | - | `:abort(C,H)`: the coordinator's **abort handler**. Its `window` slot holds the abort menu, and it has slots `size_w`, `size_h`, `position_w`, `position_h`. kwic swaps in its own menu and restores the original | USAGE | kwic-esp/src/searchMan.esp:278-292 |

**Whiteboard object** (USAGE): `:write(WB,Term)` (kappa2/kappa2/user_if/pb/pcn.esp:4841;
cal-esp/deb2.12/dmenu.esp:861) and `:read(WB,Term)` (dmenu.esp:853-854). It is one shared slot for
ad-hoc transfer between tools: "one mouse click" (TR-057 p8). The `From Whiteboard` / `To
Whiteboard` items of the Debugger Menu, Pmacs menu, inspector `from_WB` and the file manipulator
are its user interface (§5.4; IPSJ 36239 p5-p7).

**1984 coordinator commands** (PRINTED, TR-046 p28): the translation table sends
`{Cmd,E_process,Arg3,Arg4}` to `#coordinator`, with Cmd one of `kill`, `lull`, `arouse`, `status`,
`visit`, `memorize`, `broadcast`, `remember`, `invoke_system_menu`, `read`, `write`. Table in §3.4.

### 2.6 `user`, `world`, `user_process_profile`, `network_login_user`

| class | kind | method/arity | uses | args and meaning | grade | citation |
|---|---|---|---|---|---|---|
| user | class | `login_user/2` | 1/1 | `:login_user(#user,U)`: the logged-in **user object**; `:local_name(U,Name)` gives its name string | USAGE | kappa2/kappa2/user_if/pb/kcm.esp:78-80 |
| user | class | `user/2` | 2/1 | `:user(#simpos##user,U)`: the user object of the current process (comment: "Login_user_object is SIMPOS_user_object") | USAGE | kappa2/kappa2/kernel/svm/SVCTL.ESP:1698-1707 |
| user | class | `user_list/2` | 2/1 | `:user_list(#user,L)`: the registered users, an index keyed by name string (`:get_at(L,U,NameS)`) | USAGE | kappa2/kappa2/utility/mdu/USER.ESP:452-454 |
| user | class | `identify/4` | - | `:identify(#user,Name,Password,U)`: check a login and return the user | USAGE | pimfep##simpos_user create/4 (ptf, kl0 run) |
| user | instance | `local_name/2` | - | the user's name string | USAGE | kappa2/kappa2/user_if/pb/kcm.esp:79 |
| user | instance | `initial_mode/2` | - | the user's access mode (rank). Compared with a privilege | USAGE | kappa2/kappa2/utility/mdu/USER.ESP:455 |
| user | instance | `passwords/3` | - | UNSPECIFIED; read at process setup | USAGE | pimfep##simpos_user setup_process/2 (ptf) |
| world | class | `create/2` | - | `:create(#world,W)`: an empty logical-name environment | USAGE | pimfep##simpos_user create/4 (ptf) |
| world | instance | `define/3` | - | `:define(W,"me",[Dir])`: bind a logical name to a directory list (searched in order) | USAGE | same |
| world | instance | `set_default_logical_name/2` | - | `(W,"me")`: the default directory, used when a pathname names none | USAGE | same; TM-229 p5 (PROSE) |
| world | class | `world/2` | - | `:world(#world,W)`: the current world (INFERENCE) | USAGE | pimmutil##pmpsi_system_switcher goal/1 (ptf) |
| user_process_profile | class | `get_user_profile/5` | - | `(#user_process_profile,new,1,_,_)`. UNSPECIFIED beyond the call | USAGE | pimfep##as_pimos_login_requester connect_server/4 (ptf) |
| network_login_user | class | `login_user_list/3` | 3/1 | `:login_user_list(#network_login_user,Members,nil)`: users logged in on the network, to build a talk menu | USAGE | fuzclust/fuzclust/src/decide_par.ctl:121 |

`user_process_profile` is referenced by 2 compiled programs and has no required methods; `world` by
3 (partition_shell.tsv).

### 2.7 `messenger`

A class-only message box (USAGE). It pops up a message and, for `confirm`, waits to be
acknowledged. Arguments: a string, or `{Format,ArgList}` (putf-style). Options list:
`[font(F)]`, `[beep,font(F)]`.

| kind | method/arity | uses | meaning | grade | citation |
|---|---|---|---|---|---|
| class | `show/2` | 86/2 | `:show(#messenger,String)` or `{Format,Args}`: show a message and go on | USAGE | cil/src/INSTALL.esp:23; euod/PROOF/proof1.esp:51, 72 (68 euod sites); pimfep##remote_pimfep_executor message/3 (ptf) |
| class | `show/3` | 14/2 | `:show(#messenger,Msg,[font(F)])` | USAGE | cil/src/ms_cdn.esp:87; cil/src/es_gin.esp:4251 |
| class | `confirm/2` | 14/3 | `:confirm(#messenger,String)`: show and wait for acknowledgement. Every held caller ignores any answer (it is followed by `!, fail` or by more work), so the minimum is to succeed after the click (INFERENCE) | USAGE | euod/PROOF/proof2.esp:166 (`" Not applicable... "`); fuzclust/fuzclust/src/get_rui.att:332 |
| class | `confirm/3` | 4/2 | `:confirm(#messenger,{Format,List},[beep,font(F)])`, `(…,"  Kappa mode error !! ",[font(F)])` | USAGE | fuzclust/fuzclust/src/hikaku.comp:777; kappa2/kappa2/utility/luu/LUUPROC.ESP:111 |
| class | `comfirm/2` | 2/1 | misspelling in fuzclust. If SIMPOS has no such method it raises an undefined-method error (INFERENCE). A stand-in should not add it | USAGE | fuzclust/fuzclust/src/datamng.grape:104 |

### 2.8 `stop_watch`

| kind | method/arity | uses | meaning | grade | citation |
|---|---|---|---|---|---|
| class | `create/2` | 24/6 | `:create(#stop_watch,W)` | USAGE (DOC-unowned by name) | cal-esp/cal2.12/control.esp:145 |
| instance | `start/1` | 22/6 | start timing | USAGE | cal-esp/cal2.12/control.esp:440 |
| instance | `stop/1` | 27/6 | stop timing. Callers guard it with `(:stop(W);true)`, so it may fail when not running (INFERENCE) | USAGE | cal-esp/cal2.12/control.esp:438 |
| instance | `reset/1` | 10/4 | zero it | USAGE | cal-esp/cal2.12/control.esp:439 |
| instance | `show/2` | 10/5 | `:show(W,Time)`: Time is a time object; `:get_count(Time,Ms)` gives milliseconds | USAGE | cal-esp/cal2.12/control.esp:260-263 |

### 2.9 Debugger, inspector, interpreter, trace, call_counter

The debugger classes are known almost only through the CAL debugger, which derives from the
SIMPOS debugger source (COPY; DEC-20 directory `<SIMPOS.E.DEBUGGER>`, cal-esp/deb2.12/save.esp:10).
Its structure is in §5.4.6.

| class | kind | method/arity | uses | meaning | grade | citation |
|---|---|---|---|---|---|---|
| debugger | (target) | - | - | system-menu target class `debugger` (login.com `{"debugger",debugger}`). Slots `font`, `user_command_items` are read by CAL | USAGE | disc/login.com:6; TM-785 p6 |
| debugger_gate | class | `new/2` | 5/1 | a port gate (CALL/EXIT/...) object | COPY | cal-esp/deb2.12/init.esp:693 |
| debugger_gate | instance | `set/3` | 10/1 | set a gate's switch (trace/leash) | COPY | cal-esp/deb2.12/init.esp:704 |
| debugger_error | class | `raise/5` | 9/1 | `:raise(#debugger_error,_,{},string#"Fail ... \q and \q",[A,B])`: raise a debugger error with a putf message | COPY | cal-esp/deb2.12/cm.esp:466 |
| debugger_error | class | `raise/4` | 3/1 | shorter form | COPY | cal-esp/deb2.12/dmenu.esp:555 |
| debugger_error_with_retry | class | `raise/4` | 1/1 | the same, with a retry item in the error menu (INFERENCE from the name) | COPY | cal-esp/deb2.12/winpar.esp:267 |
| debugger_recorder | class | `save/3` | 1/1 | UNSPECIFIED | COPY | cal-esp/deb2.12/break.esp:109 |
| debugger_stop_watch | class | `create/2` | 1/1 | timing for the `time_on` super-command (INFERENCE) | COPY | cal-esp/deb2.12/cm.esp:1189 |
| debugger_variable_with_name | class | `check_and_set/4` | 1/1 | bind a named top-level variable | COPY | cal-esp/deb2.12/dmenu.esp:699 |
| debugger_variable_with_name | class | `check_and_get/4` | 1/1 | read one | COPY | cal-esp/deb2.12/dmenu.esp:777 |
| dummy_debugger | class | `new/2` | 1/1 | UNSPECIFIED | COPY | cal-esp/deb2.12/init.esp:688 |
| as_debugger_goal_input, as_debugger_input_buffer_processing | nature | - | - | input mixins of the debugger window: `prompt/2`, `get_input_strings_list/2`, `save_input_strings/2` (the "From Last Input" history) | COPY | cal-esp/deb2.12/io.esp:17; dmenu.esp:379, 1039, 1144 |
| trace_exception_handler | class | `set_trace_switch/2` | 11/1 | `(#trace_exception_handler,3)` before tracing | COPY | cal-esp/deb2.12/cm.esp:719 |
| trace_exception_handler | class | `set_exception_handler/1` | 1/1 | install the trace trap handler | COPY | cal-esp/deb2.12/cm.esp:720 |
| trace_exception_handler | class | `reset_exception_handler/1` | 2/1 | remove it after the goal | COPY | cal-esp/deb2.12/cm.esp:610 |
| trace_exception_handler | class | `trace_enable/1` | 1/1 | UNSPECIFIED | COPY | cal-esp/deb2.12/dmenu.esp:495 |
| interpreter | class | `create/3` | 1/1 | make an interpreter for a debugger | COPY | cal-esp/deb2.12/deb.esp:212 |
| interpreter | class | `interpret/2` | 5/2 | `:interpret(#interpreter,Goal)`: run Goal interpretively (INFERENCE) | USAGE | cil/src/cil_kl0.esp:314 |
| inspector | class | `create/2` | 2/2 | create an inspector | USAGE | cal-esp/deb2.12/pmod.esp:686 |
| inspector | class | `create/3` | 1/1 | with a parameter | COPY | cal-esp/deb2.12/dmenu.esp:535 |
| inspector | instance | `inspect/2` | 1/1 | `:inspect(I,Obj)`: open on an object | USAGE | kappa2/kappa2/user_if/pb/pcn.esp:4835 |
| trace | class | `trace/2` | 1/1 | `:trace(#trace,X)`. UNSPECIFIED | USAGE | kwic-esp-002/kwic-esp/src/autoTracer.esp:23 |
| trace | class | `trace/1` | - | `:trace(#trace)` | USAGE | pimfep##as_pimos_string_io_device trace_string_io/1 (ptf) |
| call_counter | class | `new/2`, `initial/1`, `count_start/1`, `count_stop/1`, `count_reset/1`, `set_process_number/3`, `set_all_process/2`, `reset_all_process/1`, `set_class/2`, `get_package/2`, `set_best/2`, `get_best/2`, `set_threshold/2`, `get_threshold/2`, `set_filename/2`, `get_filename/2`, `predicate_output_to_file/3` | 1/1 each | the call-count profiler, driven by the CAL debugger's super-commands. The ESP manual lists `:predicate_output_to_window(#call_counter,list,data)` and siblings | COPY + PROSE (manual) | cal-esp/deb2.12/purs.esp:355-423; ESPtex/program-e.tex:10198-10233 |
| debug | class | `deb/2`, `activate_window/1`, `deactivate_window/1` | 3, 3, 1 | sum's own classes (tier X: defined in another IFS app); not SIMPOS | USAGE | sum/src/anaphora.v32:242; sum/src/top_menu.v32:109, 130 |
| peek | class | `activate_window/1`, `deactivate_window/1` | 3, 1 | as above | USAGE | sum/src/top_menu.v32:109, 130 |
| dbg_win | class | `dbg_opn/2` | 1/1 | as above | USAGE | sum/src/you_edit.v32:75 |

### 2.10 Exceptions: `throw`, `error`, `failure`, `event`, `as_event_handler`, `abort_handler`

| class | kind | method/arity | uses | meaning | grade | citation |
|---|---|---|---|---|---|---|
| throw | class | `raise/2` | 11/4 | `:raise(#throw,Tag)`: unwind to a catcher. Tags seen: `abort`, `abort_input`, `abort_interpreter`, `break`, `cancel_input`, `syntax_error`, `execution_error` | USAGE | cil/src/ms_msm.esp:391; cal-esp/deb2.12/winpar.esp:259; kappa2/kappa2/user_if/pb/typewin.esp:103 |
| throw | class | `raise/1` | 1/1 | `:raise(#throw)`: no tag | USAGE | kappa2/kappa2/kernel/hlc/HLCMNG.ESP:416 |
| error, failure | ref | - | 3/1 | event classes named in `refute_in` catcher lists `[{#error,#failure,_}]` | USAGE | kappa2/kappa2/kernel/hlc/HLCMNG.ESP:217 |
| as_event_handler | class | `new/2` | 1/1 | make a handler. A handler class defines `:invoke(H,Event,Info,_,_)` (invoke/5) | USAGE | kappa2/kappa2/kernel/hlc/HLCMNG.ESP:29, 412-416 |
| event | class | `make_message_string/4` | 2/1 | format an event as text (for the error window, INFERENCE) | USAGE | kwic-esp-002/kwic-esp/src/searchMan.esp:325 |
| abort_handler | class | `create/2` | - | `:create(#abort_handler,H)` | USAGE | pimfep##nise_scsi_fep goal/1 (ptf) |
| abort_handler | instance | `abort/3` | - | `:abort(H,Process,exterminate_fep)`: abort another process with a reason | USAGE | pimfep##pimos_fep_superviser refute_sub_command/2 (ptf) |

Situation model (PROSE): each process has a situation stack of handlers, and an `event` hierarchy
covers errors (warning, fatal, normal) and help. Recovery means resume, fail, return to a
resumption point, or kill. "The applicable recovery methods are shown as a menu, so the user
recovers by menu selection only" (TM-181 p5; TR-087 p9-10; TR-285 p10; STRUCTURE §2). The window
this produces is §6.

---------------------------------------------------------------------------------------------------

## 3. Data formats

### 3.1 System-menu item (login file)

`{Label, Target}`, a 2-vector.

| part | forms | grade | citation |
|---|---|---|---|
| Label | a string `"debugger"` (every held login.com, TM-786 p5) or a quoted atom `'debugger'` (TM-785 p6, p25). **Accept both** | PRINTED + USAGE | TM-786 p5; TM-785 p6 |
| Target | a bare class atom (`debugger`, `pmacs`, `file_manipulator`, `librarian`, `shell`, `spooler_manipulator`, `pattern_editor`, user classes) resolved in the user's package environment; `pkg##class` (`drawing##psi_drawing_tool`, `simpos##pmacs`); `no_select` = a non-selectable line (title or spacer) | USAGE + PRINTED | disc/login.com:5-12; kappa2/kappa2/login.com:12-18; TM-785 p25 |
| Target, 3.0-5.x prose | `#knov`, `#run_wkm`: "add the class name "#knov" at the menu item". INFERENCE: same meaning, older spelling; a stand-in should strip a leading `#` | PROSE | knov/INSTALL:21-22; sum/INSTALL:35-37 |
| `area_limit(free)` | a goal before `items_list`: area limit for processes started from the menu (INFERENCE) | USAGE | gog-esp/login.com:7 |
| `font("font:test_11.font")` | a goal before `items_list`: the menu font, by logical pathname | USAGE | kappa2/kappa2/login.com:10 |

`items_list([Col1, Col2, ...])` takes a list of columns, each a list of items. Every held file
begins column 1 with the seven standard tools in the same order (§4.3). INFERENCE: the user file
restates the defaults. Whether omitting `menu` gives the defaults is UNSPECIFIED.

### 3.2 Shell command table entry

`shell_transient :- [ {Name, 'Pkg##Class'}, ... ].` Name is an atom. The class is a **quoted atom
containing `##`** (kappa2/kappa2/login.com:87-101; gog-esp/login.com:26-28). The shell's
`alias Name pkg##class.` does the same interactively (kwic-esp/INSTALL:91-99).

### 3.3 Command line and arguments (shell)

| element | written | delivered to the program (`:get_arguments/2`) | grade | citation |
|---|---|---|---|---|
| positional word | `overwrite`, `TableName`, wildcard `ltbroot:source>kwic>*.cil` | one string each, unexpanded | USAGE | kwic-esp/INSTALL:95-99; CCTPR.SHELL:29-31 |
| option | `+s`, `-t NUM` | two strings, sign then name: `"+","s"`; a value follows as a third string | USAGE | kwic-esp-002/kwic-esp/src/v2_tool.mac:82-83; kappa2/kappa2/utility/tool/LDTPR.SHELL:80-88 |
| named value | `&source path` | three strings `"&","source",Path` | USAGE | v2_tool.mac:85-89; dbDM.esp:52-100 |
| stdin redirection | `{ file` | stdin of the command reads the file (INFERENCE from dtCompiler's "read from standard input") | PROSE + INFERENCE | kwic-esp/INSTALL:96; dtCompiler.esp:54-60 |
| line end | `.` | ends the command | PROSE | kwic-esp/INSTALL:95-99 |

`:parse_arguments(P,{Positional,Named})` gives the same as a pair (§2.1).

### 3.4 Key and mouse codes at the top level

| code | 1984 binding (TR-046 p28 / TR-061 p13, PRINTED) | later evidence |
|---|---|---|
| `mouse#rr` (double right) | `invoke_system_menu` | "Clicking double right will always make the system menu prompt out" (TM-112 p16, 1.00); two right clicks (TM-134 p66, TM-181 p3, utter/INSTALL:30) |
| `control#"s"` | bound **twice**: `status` (first clause) and `invoke_system_menu`. As printed the first clause shadows the second, so `control#"s"` gives `status`. `trtm_window` W8 states the system-menu binding as live; this document does not | - |
| `control#"k"` | `kill` the window's expert | - |
| `control#"l"` | `lull` (suspend). The `l`/`1` glyph is ambiguous | system menu "suspend" (TM-143 p3, PROSE) |
| `control#"a"` | `arouse` (resume) | - |
| `mouse#l` | `visit` (select the window and its expert) | single left in an unselected window selects it (TM-112 p10) |
| `control#"m"` | `memorize` | - |
| `control#"b"` | `broadcast` | - |
| `control#"v"` | `remember` | - |
| `control#"r"` / `control#"w"` | read / write the whiteboard | `From/To Whiteboard` menu items (§5.4) |
| any other | "send character as it is" | - |
| `control#"c"`, `key#abort`, `mouse#mm` | - | abort an output loop (polled with `:read_sense/2`; prints `aborted.` and fails) (cil/src/ds_bep.esp:3477-3488, COPY) |
| `control#"z"` | - | application end key (TM-134 p70); `C-x C-z` ends an input form (TM-786 p6) |
| BREAK (console) | - | stops SIMPOS into the CSP monitor (§6.4) |

The 1984 table has the signature `:look_up(Table,Window,Key,Destination,Command,HelpString)`
(look_up/6). It lives in a slot of the `e_window`. User tables inherit `default_translation_table`
and override keys (TR-046 p13-15; TR-061 p6-9, PROSE). The held programs never send `look_up`.

### 3.5 Object print forms at the listener

| form | meaning | grade | citation |
|---|---|---|---|
| `$hypocycloid_drawer`, `$window` | an instance, printed by class name | SCREENSHOT | TM-134 p68; TM-181 p4; IPSJ 36239 p6 |
| `$window@1:4087FC` | an instance in the inspector: class, `@`, area, `:`, hex address | SCREENSHOT | IPSJ 36239 p6 |
| `#eight_puzzle` | a class object | SCREENSHOT | Giho 8609 p16 |
| `loc@1:25C066` | a location (heap address) | SCREENSHOT | Giho 8609 p16 |
| `"Pmacs ..."` | a long string, abbreviated | SCREENSHOT | TM-181 p4 |
| `'$atom$B008'(...)` | compiler-generated predicate (if-then-else expansion, INFERENCE) | SCREENSHOT | IPSJ 36239 p6 |

---------------------------------------------------------------------------------------------------

## 4. Screen behaviour: boot, login, status line, system menu

### 4.1 Boot and login

**Cold boot, SIMPOS 1.00** (TM-112 p7, PROSE, eye-read). The console is the green CSP console.
1. Power on; wait for `>` on the CSP console.
2. `B` CR (boot).
3. `deb` CR; the console asks `... (0/1)`.
4. Put floppies in drive 1 and press `1`: `EXEC`, `WINDOW`, `EDITOR`, `SUPER` in any order, then
   the application floppy last. INFERENCE: these are the 1.00 boot volumes (executive, window
   system, editor, supervisor).
5. Each floppy prompts `EXEC (Y/N)`, then `Another volume (Y/N)`.
6. After `n`, the date and other questions (CR accepts).
7. "a login message will appear on the PSI bitmap screen".

Cross-compiled programs could only be linked in at boot from floppy (TM-112 p7). Start-up of a
program took about 30 s (TM-112 p8). Later systems boot from the fixed disk; the IPL "loads SIMPOS
stored on the fixed disk", with modes User / Developer / System (ESPtex/overview-e.tex:1150-1180,
PROSE, 1990). IPL command files such as kappa's `>sys>kappa>ipl.com` preload classes
(kappa2/kappa2/init/ipl.com:6-12; librarian.md).

**Login.**

| version | dialogue | grade | citation |
|---|---|---|---|
| 1.0 | SIMPOS waits for a user name, then a password. A registered user types his own. An **unregistered user types `me` for both**, and is logged in as a general user. The screen then goes blank; the status line shows `USER : me` | PROSE + SCREENSHOT | TM-134 p66, p68 |
| 1.00 | status line `USER : me` on all TM-112/115 screens | SCREENSHOT | TM-115 p25-26; TM-112 p25 |
| 7.x (1992-93) | `user     > superuser` CR, `password > superuser` CR. `superuser` exists with password `superuser` on a fresh system | PROSE (transcript) | gog-esp/INSTALL.e:19-20, 37-38 |
| PIMOS front end on SIMPOS (1990s) | pimmcsp `pimos_local_login_requester` prompts `Enter SIMPOS user name>` and `Enter SIMPOS password>` | USAGE (pool constants) | ptf S2 |

The PIMOS login requesters (`pimfep##pimos_login_requester`, a `login.com` menu entry, with the
prompts `Enter FEP node name--------->` etc.) are **PIMOS's** login, run as an ordinary SIMPOS
program; they are not SIMPOS's own login dialogue (`pim/docs/fep_services.md` §6.9). Only their
window and menu classes are SIMPOS's.

What login does (PROSE, TM-181 p3; TM-229 p5-6 = IPSJ 36239 p4):
1. sets the system-menu items;
2. sets the directory logical names, by default `me:` = `>sys>user><login name>`, and a default
   directory used when none is given;
3. runs an initialisation program;
4. creates PSs (editor, debugger, ...) automatically, with their windows at given positions.

**What login does, as code** (USAGE, `pimfep##simpos_user` class create/4, run under kl0; ptf S2).
This PIM-FEP class wraps SIMPOS's own login:

```
:identify(#user, Name, Password, U),
:create(#world, W),
:append(#pathname, "user:", Name, Dir),
:define(W, "me", [Dir]),
:set_default_logical_name(W, "me")
```

Its `setup_process/2` then sends `set_user/2`, `password_list/2`, `initial_mode/2`,
`set_access_mode/2`, `passwords/3`, `set_passwords/2` and `set_world/2`. So a logged-in process
carries a user, an access mode, passwords and a world. `me:` is `user:<name>`, and `user:` is
`>sys>user` (INFERENCE from TM-143 p3 and every held home directory `>sys>user>NAME`).

Users: registered, with ranks; `>sys>user>NAME` homes; remote users written `node!user`; a
superuser exists (IPSJ 115247 (4E-8) p1-p2, PRINTED; notes: ipsj). Registration in 7.x is via system menu
`[others] -> [user] -> [maintenance] -> [register]`, sweep a window, then `Username :`,
`Password :`, `Rank     : general`, reply `User cgs registered` (gog-esp/INSTALL.e:24-31, PROSE).

### 4.2 The login file

#### 4.2.1 Name and place

| version | name | grade | citation |
|---|---|---|---|
| 2.50 / A00 (1986-87) | `login.cmd`, versioned (`login.cmd.2`) in the user's directory | SCREENSHOT | video `esp.wmv@163-169`; IPSJ 36239 p7 (`login.c?d.2`) |
| 5.0 (1989) | "login file" (ログインファイル) | PRINTED | TM-785 p6; TM-786 p5 |
| 7.x-8.x | `login.com` in the home directory, `me:login.com`; for user kappa `>sys>user>kappa>login.com` | PROSE + USAGE | cal-esp/INSTALL:38; kappa2/INSTALL:30; kwic-esp/INSTALL.j:143 |

1986 papers call it the "initialisation file" (初期化ファイル) (TM-229 p5). It is read at login only:
"Logout and login again" after every edit (cal-esp/INSTALL:43; euod/INSTALL:42; utter/INSTALL:73).
**Spec: the stand-in reads `me:login.com`** (held programs). It may accept `login.cmd` as the 2.x
variant.

#### 4.2.2 Syntax

Prolog-syntax clauses with **0-arity heads**, one per item, terminated by `.`, `%` comments.
Seven held files (USAGE): disc/login.com, fuzclust/fuzclust/install/login.com, gog-esp/login.com,
kappa2/kappa2/login.com, kappa2/kappa2/init/sample/login.com, plus INSTALL fragments.

| head | body | meaning | grade | citation |
|---|---|---|---|---|
| `menu` | zero or more option goals (`area_limit(free)`, `font(Path)`), then `items_list(Columns)` | the EXPERTS part of the system menu (§3.1) | PRINTED + USAGE | TM-785 p6, p25; TM-786 p5; disc/login.com:3-47 |
| `define` | `"Name" := ["Path", ...]` pairs joined by `,` | logical names: `Name:` resolves through the listed directories in order. Paths may start with a logical name defined earlier, with `user:` / `me:`, or with `>sys>`. **`"me"` may be redefined** (`"me" := ["user:kappa"]`) | USAGE | kappa2/kappa2/login.com:34-83; disc/login.com:49-55 |
| `package` | one atom | the default package of the user's processes (`user` when none) | USAGE | disc/login.com:57; kappa2/kappa2/login.com:85; cal-esp/INSTALL:39 |
| `shell_transient` | a list of `{Name,'Pkg##Class'}` | shell commands (§3.2) | USAGE | kappa2/kappa2/login.com:87-101 |
| any other atom | a term | **user item**, readable by programs as `:information(#coordinator,Head,Value)` (§2.5). The value is the clause body | USAGE + PROSE | kwic-esp/src/systems.esp:297, 364; dbUtil.esp:225; kwic-esp/doc/classSpec.IO1:345-351 |

No held login file has a user item, but kwic documents one (PROSE, TRANSLATION,
kwic-esp/doc/classSpec.IO1:345-351, 533-540). Its "3. login file" section says DRT command aliases
are registered by setting a `'drt_alias'` item in the login file, in the form

```
drt_alias :- <alias>, <alias>, ... .
<alias> ::= <replacing name> := <replaced command name>
```

An external command class is written `#<class name>` in the replaced-command position. The callers
read other value forms: a string (kwic init-file path), the conjunction above walked as
`(Element, Rest)` (dbUtil.esp:229-231), an atom `on`, a 4-element list (pimfep). That any atom head
is allowed is INFERENCE.

Schematic example. It is built from the held forms and is not a copy of any one file. The
`my_tool_init_file` item is INFERENCE, modelled on kwic's `kwic_constant_file_path`.

```
menu :-
    font("font:test_11.font"),
    items_list(
      [ [ {"debugger", debugger}, {"pmacs", pmacs}, {"file", file_manipulator},
          {"librarian", librarian}, {"shell", shell},
          {"spooler", spooler_manipulator}, {"pattern editor", pattern_editor} ],
        [ {"MY TOOLS", no_select},
          {"tool", mypkg##my_tool} ] ] ).
define :-
    "me" := [ "user:alice" ],
    "src" := [ "me:source" ].
package :- mypkg .
shell_transient :- [ {far, 'superuser##file_backup'} ].
my_tool_init_file :- "me:tool.ini" .
drt_alias :- ls := list, rep := #mypkg##my_report .
```

#### 4.2.3 Known defect in a held file

`kappa2/kappa2/init/sample/login.com:57` has `'kappa##kappa_delete_れcord_tool'`, with a JIS
hiragana れ typed for "re". The main file has `kappa_delete_tool`. A faithful stand-in reports this
class as not found when the item is chosen (INFERENCE).

#### 4.2.4 Other login-time settings (1986 prose, not seen in held files)

The initialisation program and the auto-created PSs with window positions (TM-229 p5-6) have no
held syntax. The `initiation_table/2` / `current_state/2` pair (§2.1) is the program side of that
mechanism (INFERENCE). Mail: a new-mail notice is shown at login (IPSJ 36239 p7, PROSE).

### 4.3 The system menu

Invocation: double right click anywhere (TM-112 p16; TM-134 p66; TM-181 p3). The menu is "SIMPOS's
command processor" and can be called at any time. It starts, terminates, suspends and resumes
processes (TM-143 p3; TM-181 p3; TM-229 p5). It is a pop-up titled `SYSTEM MENU` (SCREENSHOT).
Left click selects (TM-134 p66).

Two columns:
- **EXPERTS** (header `Experts`): programs that may run as several instances at once. Per user,
  from the login file. The user may add his own and delete unused ones.
- **MEDIA SYSTEMS**: one instance each. Fixed. The 1984 source builds this part as the class's
  "invariant part" (`get_invariant_part/2`, TR-046 p27).

**1984 source** (TR-046 p27, PRINTED, abridged in print):
`:create(System_menu_class, Directory, System_menu)` = create/3 makes a list of experts from the
user's Directory (`make_from_to`), puts it before the invariant part, and creates a
`#multi_column_menu` from the list. The invariant part is built once into the class slot
`menu_list` from `:create(#menu_item, 'window', common, window, _, Item)` (create/6) and the same
for `'file'`.

**Item lists by version** (verbatim):

| version | EXPERTS | MEDIA SYSTEMS | grade | citation |
|---|---|---|---|---|
| 1.x (Nov 1985) | `generalist`, `debugger`, `editor`, `file_manipulator`, `librarian`, `terminal` | `window_manipulator`, `network`, `shell`, `whiteboard`, `login`, `shut down` | SCREENSHOT | TM-143 p3 |
| 2.10 (Jun 1986) | `debugger`, `pmacs`, `librarian`, `file_manipulator`, `spooler`, `font_editor`, `edips` | `user process list`, `window manipulator`, `network`, `shell`, `whiteboard`, `kanakan initiate`, `garbage collection`, `login`, `shut down` | SCREENSHOT | TM-181 p3 (`printed/listings/TM-181_p03_system_menu.txt`, whose "2.19" footer is read here as 2.10) |
| 2.50 (Sep 1986) | `Debugger`, `Pmacs`, `File`, `Librarian`, `Font_editor`, `Edips`, `Spooler`; second column (user demos) `Escher`, `Oekaki`, `Queens`, `Squares`, `Bounce` | as 2.10 | SCREENSHOT | IPSJ 36239 p4 (600 dpi; = TM-229 p5) |
| A00 video (~1986-87) | `Experts`(?), `8puzzle`, `debugger`, `edips`, `pmacs`, `file_manipulator`, `librarian`, `spooler`, `font_editor` | `MEDIA SYSTEMS`, `user process list`, `window manipulator`, `network`, `shell`, `whiteboard`[?], 2 words illegible, `garbage collect[ion]`[?], `login`/`logout`[?], 2 words illegible | SCREENSHOT (VHS) | `simpos.wmv@9.6-11.3`, `@59.7-62.0` |
| 5.0 (TM-785 p25 prints only `{'debugger',debugger}`, `{'pmacs',pmacs}` before the elision); 6.2-8.x login file defaults | `debugger`, `pmacs`, `file`, `librarian`, `shell`, `spooler`, `pattern editor` (labels; targets in §3.1) | not in the login file. Named in prose: `logout` (with confirm `yes`), `others` -> `user` -> `maintenance` -> `register`, a `TCP-IP` submenu with `reset network`, a `process manipulator` | USAGE + PROSE | disc/login.com:5-12; gog-esp/INSTALL.e:24, 34; fuzclust/fuzclust/README:139, 144 |

Notes:
- TM-229 (ICOT TM, 1986-09-29) and IPSJ 36239 (SIG-DPS, 1986-09-29) carry the same sections,
  screens and demo items. They are one paper (INFERENCE), so one witness. The 600 dpi 36239
  readings are preferred over the TM-229 scan, which is below glyph resolution (notes:
  trtm_progsys "NOTE ON GRADES").
- 1.x has `editor` (Edips, TM-143 p3); from 2.10 the editor is listed by name (`pmacs`, `edips`).
  The A00 video shows `pmacs`, not `editor`, contradicting `source_notes.md:39` (notes: video §3).
- In disc/login.com column 1 starts with `{"SYSTEM MENU", no_select}`: the menu title can be
  restated as a non-selectable item.
- Whether `Experts` / `MEDIA SYSTEMS` are selectable is UNSPECIFIED. In 2.50 and A00 they look like
  headers.
- Menu look (SCREENSHOT, video): the item under the mouse is boxed with a thin rectangle, not
  inverted (`simpos.wmv@10.9`, `@60`); a small `×` marks it (`simpos.wmv@132`).

**Selecting an EXPERTS item** (PROSE + SCREENSHOT):
1. A small pop-up titled with the program name offers `create` and `kill` (video `simpos.wmv@49`,
   title `file_manipulator`, second item cut to `k…`). The same mechanism titled `WHICH ?` with
   `create` / `kill` appears in `prolog.wmv@14-15`. INFERENCE: the pop-up appears when an instance
   exists, offering a new instance or killing an existing one. TM-134 p67: "show the system menu,
   select the debugger and kill".
2. `create`: "The shape of the mouse cursor changes. Specify the coordinates of left-top and
   right-bottom corner of the window" (utter/INSTALL:30-38). The Japanese says the cursor becomes
   a corner shape (utter/INSTALL.j:34). Left click, move, left click (TM-134 p66). An outline
   rectangle follows the sweep (video `simpos.wmv@53-55`).
3. The tool's window appears with label `<program>_<n>` (§4.4), and the program runs in a new
   process: `:create(#process,P)`, `:activate(P,Prog)`, where Prog = `:create(TargetClass,Prog)`
   (INFERENCE: the held login.com targets are as_program classes; TM-786 p5 says start by menu,
   by shell and by debugger are "identical after start").

Programs that should take the swept rectangle create their window with `size(manipulator)` and
`position(manipulator)` (cil/src/ds_bep.esp:3339-3349; IPSJ 36239 p5). INFERENCE: the sweep is done
by the window's creation, not by the menu. See window.md.

**MEDIA SYSTEMS items** (meaning; PROSE unless marked):

| item | meaning | citation |
|---|---|---|
| `user process list` | list of the user's processes; select to control them (INFERENCE from name). The 7.x `process manipulator`'s `parent` "show[s] all process" | fuzclust/fuzclust/README:144-152 |
| `window manipulator` | change a window's position, size and attributes by mouse. Its menu (1985): SHOW, HIDE, RESHAPE, MOVE, EXPAND, MENU, PERMISSION, ATTRIBUTE, HARDCOPY, SUPERIOR, INFERIOR, EXIT. **Details: window.md** | TM-125 p8 (PRINTED-INTERFACE); TM-229 p8; video `simpos.wmv@117` |
| `network` | network functions (talk, mail, remote file) | IPSJ 36239 p7 |
| `shell` | starts the shell (§5.3) | TM-181 p3; TM-786 p5 |
| `whiteboard` | the whiteboard (show or edit it, INFERENCE) | TM-181 p3 |
| `kanakan initiate` | start kana-kanji conversion (the third letter might be `s`) | TM-181 p3 |
| `garbage collection` | force a GC: "GC can also be forced from the system menu" | Giho 9106 p86 Table 2; ESPtex/overview-e.tex:1150-1180 |
| `login` | log in (or change user; UNSPECIFIED) | TM-143 p3; TM-181 p3 |
| `logout` | 7.x: `SYSTEM MENU ---> [logout] ---> [yes]` | gog-esp/INSTALL.e:34 |
| `shut down` | "all windows vanish and it ends" | TM-134 p67 |

### 4.4 The status line and window names

- Two lines across the bottom of the screen, white on black (TM-115 p25-26).
- Line 1 left: `USER : <name>`. Line 2 left: `SIMPOS Version <v>` (`1.00`, `2.10`, `2.50`, `A00`).
- Middle: a reverse-video box with the name of the **selected window** (TM-112 p9). Long names are
  truncated (34 characters shown, TM-115 p26).
- Right: `DD-Mon-YY Weekday hh:mm:ss`, e.g. `23-May-85 Thursday 20:22:44` (TM-115 p25).
- 1986: `SWAPPED` and `spool` indicator boxes (TM-153 p28; Giho 8609 p16).
- The same band carries kana-kanji conversion input and its key help, e.g.
  `>MENU(PF16) PF10=ON_OFF, PF0-PF6=MANAGE_KEY, PF7=CANCEL.` (IPSJ 36239 p6; `simpos.wmv@108-113`).
- Menu-item documentation strings are shown on the status line (TM-125 p14, PROSE).
- Grades: SCREENSHOT unless marked.

Window and process names, by version:
- 1.x-2.50: tools are labelled `<program>_<n>` with small numbers that look like a per-program
  counter: `debugger_1`, `debugger_3`, `librarian_1`, `pmacs_1`, `file_manipulator_2` (TM-134 p68;
  video). `Debugger_4` is capitalised in IPSJ 36239 p6. In 2.10 n is **not** the process number:
  `debugger_4( process «?»7 )` (TM-181 p5).
- 5.0 and later: n equals the process number, `librarian_59( process 59 )` (TM-785 p3). The 5.0
  Librarian window is titled `librarian 49 (default: user)`, i.e. name, number and default package
  (IPSJ 118681 p1 Fig 1, read by eye at high resolution; web_search_2026-11-24.md reads 40). The CAL copy appends the process number
  to its labels (cal-esp/deb2.12/winpar.esp:104-131, COPY). INFERENCE: the rule changed between
  2.50 and 5.0.
- Unnamed windows show `<class>/<k>` for the k-th instance, e.g. `pattern_display_window/2`
  (TM-112 p18; TM-115 p111).

---------------------------------------------------------------------------------------------------

## 5. Program start, the shell and the debugger

### 5.1 The four ways to start a program

| # | from | form | runs in | version | grade | citation |
|---|---|---|---|---|---|---|
| a | debugger, subroutine form | `:- :new(#c,O).` then `:- :initiate(O).` (any user method) | the **debugger's process**; the debugger waits until it ends | 1.0 | PRINTED (dialogue) | TM-134 p67, p69 |
| a' | debugger, method call on a class | `:drawing(#drawing##psi_drawing_tool)`, `:generate(#drawing##drawing_class_generator)`, `:init_start(#cgs_main).` | the calling process | 5.0-7.x | PRINTED + PROSE | TM-785 p6, p25; gog-esp/INSTALL.e:56 |
| b | debugger, process form | `:create(#c,O).` `:create(#process,P).` `:activate(P,O).` -> `:goal(O)` in P; `:activate` returns at once and the prompt reappears | a new process | 1.0- | PRINTED | TM-134 p71; TM-112 p8 |
| b' | debugger, inline goal | `:create(#simshow##simshow,S), :goal(S).` | the debugger's process | 5.0 | PRINTED | TM-786 p5 |
| c | shell | `$ call simshow##simshow`; `call cil_install`; or a `shell_transient`/`alias` name with arguments | a new process (INFERENCE) | 5.0-8.1 | PRINTED + PROSE | TM-786 p5; cil/INSTALL:18 |
| d | system menu | login-file item `{"simshow",simshow##simshow}` | a new process | 1.00 (as_e_program), 5.0- | PRINTED + PROSE | TM-786 p5; TM-785 p6; TM-115 p109 |

TM-786 p5: the three start modes of SIMSHOW behave identically after start (PROSE).

Programs that start other programs do (b) themselves, optionally with a mode list or area limits:

```
:create(Class, Program), :create(#process, P, [free,free,query,middle]), :activate(P, Program)
```

(cil/src/ms_cdn.esp:343-349, USAGE.) Giho 8609 p16 shows `:set_sub_priority(P,2)` between create
and activate (SCREENSHOT).

### 5.2 Process life and ending

- `:goal/1` returning, by success or failure, ends the process; the instance and its slots are gone
  (TM-134 p72; TM-100 p11).
- To keep data, use a file, do not end the process (wait on a stream), or use class slots saved
  before end and restored in the next `after :create` (TM-134 p72, PROSE). Class slots survive only
  until shut down.
- Shell commands end `:goal/1` with a clause that closes stdin/stdout and sleeps 5 s through an
  `alarm_watch` before the process ends (kappa2/kappa2/utility/tool/LDTPR.SHELL:43-56). INFERENCE:
  the output pipe needs time to drain.
- Killing: system menu -> tool -> `kill` (TM-134 p67); a process `:exterminate/1`; the 1984
  `control#"k"` key; the CSP BREAK `K nn` (§6.4).

### 5.3 The shell

#### 5.3.1 History

There is no shell in the 1984 design (TR-057 p7). `shell` is a MEDIA SYSTEMS item from 1.x
(TM-143 p3). In 1986 the Coordinator "also has a UNIX-like shell, and program execution by it is
also possible" (TM-225 p7, PROSE). In 5.0-8.1 the shell starts programs by class name (TM-786 p5;
cil/INSTALL:18).

#### 5.3.2 Screen

The shell is a window whose standard ports are the window itself (TM-388 p82, PRINTED). It is a
system-menu item (MEDIA SYSTEMS in 1.x-2.50; column 1 of every later login file as
`{"shell",shell}`). Prompt `$` (TM-786 p5, PRINTED). Its window label is presumably `shell_<n>`
(INFERENCE from §4.4). Every character-input window is "a window with Pmacs functions", so Pmacs
line editing applies to shell input (TM-229 p5, PROSE, 1986).

#### 5.3.3 Commands

| command | meaning | grade | citation |
|---|---|---|---|
| `call Pkg##Class` / `call class` | create the class's program and run it | PRINTED + PROSE | TM-786 p5; cil/INSTALL:18 |
| `alias Name pkg##class.` | bind a command name to a program class for this shell | PROSE | kwic-esp/INSTALL:91-99 |
| `Name args... .` | run a command bound by `alias` or by login.com `shell_transient`, with arguments (§3.3) | PROSE + USAGE | kwic-esp/INSTALL:95-99; kappa2/kappa2/login.com:87-101 |
| `far ...` | `superuser##file_backup` (file archive, INFERENCE) in both login files that have shell_transient | USAGE | gog-esp/login.com:27 |

Two of the printed lines (kwic-esp/INSTALL:91-99, the part the user types); the other two have the
same shape (`alias dbm ...`, then `dbm overwrite +s &source <path>>*.cil.`):

```
$ alias dtc yourei_v2##dbDeclTableCompiler.
$ dtc +s { ltbroot:source>kwic>standard.decl.
```

#### 5.3.4 What a command program sees (USAGE; kappa .SHELL files, kwic)

1. `:self(#process,P)`, then optionally `:set_area_limit_execution(P,free,default,free,middle,nil,nil)`.
2. `:standard_input(P,In)`, `:standard_output(P,Out)`, `:standard_message(P,Msg)`. stdin and stdout
   are redirectable streams; prompts and errors go to the message stream.
3. `:get_arguments(Prog,Args)`: the flat string list of §3.3. Usage lines are printed on error, e.g.
   `loading [-t NUM] [-s NUM] TableName` (kappa2/kappa2/utility/tool/LDTPR.SHELL:35).
4. Prompts such as `Format> ` and `Condition> ` go on the message stream; answers are read with
   `:getl` from stdin; records go to stdout with `:putf(File,"\q.\n",[R])` (KSTPR.SHELL:31-48, 136).
5. A command may still open windows, e.g. a `window_without_label` progress counter
   (KSTPR.SHELL:65-67).

Citations: kappa2/kappa2/utility/tool/CCTPR.SHELL:21-46; LDTPR.SHELL:26-88; KSTPR.SHELL:19-136;
kwic-esp-002/kwic-esp/src/v2_tool.mac:25-102.

#### 5.3.5 Unknown

The full shell grammar: pipes, `}` output redirection, `&` background, built-ins other than `call`
and `alias`, error texts. None of it is held (gaps).

### 5.4 The debugger as listener

#### 5.4.1 Role

"The debugger is for debugging but also works as an ESP listener" (TM-181 p4; TM-143 p4). It runs
goal sequences of registered methods and built-ins. Calls work the same for interpretive and
compiled code; trace works only in interpretive code (TM-181 p4; TM-225 p7). Compiled code is
traced "just like a simple built-in predicate invocation" (TR-057 p8). The debugger's standard
ports are its window (TM-388 p82). In 1989 the debugger inherits the Pmacs editor, so trace output
can be edited and saved (Giho 8907 p34, PROSE).

#### 5.4.2 Prompt and answers

| version | goal prompt | after a goal | bindings | grade | citation |
|---|---|---|---|---|---|
| 1.00 (1985) | `:- ` | `> Success !!` or `> Fail !!` | in the `Variable Window` sub-window: `Object1 = $hypocycloid_drawer,` / `Object2 = $hypocycloid_drawer;` (`,` between, `;` after the last) | SCREENSHOT | TM-134 p68, p71; TM-125 p23 (Success); TM-125 p7 Fig 4 (Success, Fail) |
| April 1986 (2.00 by date, INFERENCE) to 2.50 | `?- ` | the binding on the next line, `Window= $moving_window`, then a fresh prompt | `Variable` pane lists the variable names | SCREENSHOT | Giho 8609 p19-20 (Fig 9/10); Giho 8609 p16; video `esp.wmv@118-121` (`A= $move_win`) |
| 2.10 | unclear (`:-` or `?-` at 96 ppi) | ` «?» $my_window` | `Variable` pane | SCREENSHOT | TM-181 p4 |

Input is terminated with `.` (Giho 8609 p20). Text cursor: a solid block. **Spec for the held
programs: `?- `** (INFERENCE: the latest screens, 1986-87, show it; no 3.0+ debugger screen is
held), with `:- ` as the 1.00 variant.

Spy points: no trace is done until a given goal is called; set from the state window (`Spy Points`,
1.00) or the `Set Spy` item (A00) (TM-229 p7, PROSE; TM-126 p6; `simpos.wmv@132`). Debugging works
in a multi-process environment (TM-229 p7).

The prompt can be changed by the super-command `set_prompt("system_mode>")` (CAL, COPY).

#### 5.4.3 Trace line

Format (SCREENSHOT): `(<invocation no.>)<depth> <PORT>[ <kind>]> <goal> ? <answer>`

| example | version | citation |
|---|---|---|
| `(1)0 CALL new> location_element(loc@1:25C066,A),method_call(A,initialize) ? step` | 2.00 | Giho 8609 p16 |
| `(2)1 CALL builtin> location_element(loc@1:25C066,A) ? step` | 2.00 | Giho 8609 p16 |
| `(3)1 CALL> :initialize(#eight_puzzle) ? step` / `(3)1 EXIT> :initialize(#eight_puzzle) ?` | 2.00 | Giho 8609 p16 |
| `(17)1 CALL> :test($my_window) ? step` | 2.10 | TM-181 p4 |
| `(22)2 CALL> :putl($standard_io_window,"Pmacs ...") ? skip_predicate` | 2.10 | TM-181 p4 |
| `(22)2 EXIT> :putl($standard_io_window,"Pmacs ...") ? no_trace` | 2.10 | TM-181 p5 |
| `(742)81 CALL builtin> add(532,7,A) ? step` / `(742)81 EXIT builtin> add(532,7,539)` | 2.50 | IPSJ 36239 p6 |
| `(745)81 unify> do(A,B,C,D,E,F,G) :- less_than(B,0)->...` / `(745)81 pick> ...` | 2.50 | IPSJ 36239 p6 |

- Kinds: `new>` (a goal sequence typed at top level), `builtin>`, none for methods.
- ` ? ` is the leash prompt. Answers seen: `step`, `skip_predicate`, `no_trace`. INFERENCE: typed,
  or inserted by the `Step`/`Skip`/`No trace` menu items.
- Ports (P&C box model): procedure ports `CALL`, `EXIT`, `FAIL`, `REDO`; clause ports `unify`,
  `next`, `pick`, `miss`, `exit`, `redo` (TR-057 p8 Fig 4-1; TM-229 p7; IPSJ 36239 p6).

#### 5.4.4 Menus and sub-windows by version

| version | menu | items, verbatim | grade | citation |
|---|---|---|---|---|
| 1.00 | `Debugger Menu` | `Change State`, `Variable Window`, `Control Menu`, `From Last Input`, `From Whiteboard`, `To Whiteboard`, `Help` | SCREENSHOT | TM-126 p6 Fig 3 |
| 1.00 | state window (4 sub-windows) | mode `trace` / `no trace` / `no debug`; `print depth: 5`, `length: 7`; `State Menu`; `[Trace]`/`[Leash]` grids over `CALL unify pick exit EXIT` / `FAIL next miss redo REDO`, then `CALL EXIT REDO FAIL`; `New`, `Method`, `Compiled`, `Builtin`; `Spy Points` | SCREENSHOT | TM-126 p6 Fig 4; TM-125 p23 Fig 6 |
| 2.00-2.10 | command menu beside the trace | `Method`, `Step`, `Skip`, `Leap`, `Fail`, `Retry`, `No trace`; mode box `PREDICATE` / `clause` | SCREENSHOT | Giho 8609 p16; TM-181 p4 |
| A00 / ~2.50 | `Debugger Menu` | `State`, `Set Spy`, `From last input`, `Input string`, `Inspector`, `To whiteboard`, `From whiteboard`, `Re-display` | SCREENSHOT (VHS) | `simpos.wmv@129-137` |
| 1986-91 (CAL copy) | window labels | `input_string`, `Mode_Leash`, `Command window`, `Variable`, `Debugger Menu`, `Input string`, `To whiteboard`, `From whiteboard`, `State window`, `Operator window`, `Place menu`; process number appended | COPY | cal-esp/deb2.12/winpar.esp:207-227 |
| 1986-91 (CAL copy) | super-command menu | col 1: `library_error_mode(off)`, `reset_inspector`, `get_debugger(DEB)`, ..., `set_prompt("system_mode>")`, `reset_prompt`, `without_vars_window`, `with_vars_window`, `display_vars`, `from_wb(WB)`, `area_limit_off`; col 2: `icon`, `cmenu(off)`, `cmenu(on)`, `heap_on`, `heap_off`, `time_on`, `time_off`, ..., `package`, `font`, `depth(7),length(7)`, `system_help` | COPY | cal-esp/deb2.12/purs.esp:975-1021 (full list in notes: ifs_libshell §4.3) |

Window names: `debugger_<n>`; sub-windows `Variable Window` (1.00) / `Variable` (2.x).

#### 5.4.5 Inspector

Called from the debugger; returns control to it. It shows, searches and changes slot values and KL0
data; structured data's elements are shown as a menu; selecting one descends into it. A value
changed or bound in the inspector is passed back to the debugger (TM-229 p7; IPSJ 36239 p6,
PROSE). Screen (2.50, SCREENSHOT, IPSJ 36239 p6): window `Inspector`, subtitle `$window@1:4087FC`,
slot list (name, value), a `Memory` history pane (`Variables`, `Predicate`, objects), a `Command`
pane `exit`, `parameters`, `break`, `from_WB`.

#### 5.4.6 Structure of the CAL copy (how a stand-in debugger can be organised)

`cal_debugger` has natures `command_interpreter, ..., save_debugger_state, as_program`
(cal-esp/deb2.12/deb.esp:20, COPY). Its pieces:
- `command_interpreter`, the top loop: `do_top_loop_of_command_interpreter/2`,
  `get_goal_with_situation/2`, `interpret_with_abort_situation/2`.
- `as_cal_debugger_entry`: port gates for call, exit, fail, redo, unify, next, pick, miss,
  proc_call, proc_exit, proc_fail, proc_redo, spy_entry.
- The windows: debugger_window, trace_pane, variable_menu, control_menu, top_menu, state_window,
  gate_window.

Pane classes: variable_menu = `standard_scrolling_menu`, control_menu =
`standard_superior_window`, top_menu = `standard_temporary_multi_select_menu`, state_window =
`standard_temporary_choice_window` (winpar.esp:379-460). Notes: ifs_libshell §4.3.

### 5.5 Execute windows (the Librarian's `Execute` item)

The other top-level command line is the Librarian's `Execute` item. It runs Librarian command
files and is the install path of most held programs. Details are in librarian.md; the dialogue as
the user sees it:

| step | text | grade | citation |
|---|---|---|---|
| create a Librarian, put the floppy in unit 0, choose the Librarian's `Execute` | - | PROSE (translation) | TM-785 p3 |
| prompt | `Command>` | PROSE | TM-785 p3; TM-786 p4 (`Command>fdd(" simshow.com")`) |
| run a command file from floppy | `fdd("drawing.com")` Return; the system asks `FDD mount ok?`, then for a unit number; type `0` with no Return; about 1 minute | PROSE (translation) | TM-785 p3 |
| run one from disk (7.x) | `fxd("cgscmp.com").` (gog); kappa's prose has the user type just `CATALOG.COM` | PROSE | gog-esp/INSTALL.e:49-50; kappa2/INSTALL:39 |
| error: package exists | `Error occurred in librarian_59( process 59 )`, `Package drawing already exists` (the §6.1 window) | SCREENSHOT | TM-785 p3 |

`fxd` is ambiguous: cil's Librarian copy maps an `fxd(P)` command item to *catalogue P*
(cil/src/ds_bep.esp:3395, COPY), while gog types it at `Execute` to run a command file. This is
open in librarian.md.

---------------------------------------------------------------------------------------------------

## 6. Error and interrupt texts

### 6.1 The error window

Layout, stable 1986-1989 (SCREENSHOT):

```
Error occurred in <window/process name>( process <n> )
<message lines>
---------------------------------
Error handling menu:
  <item>
  ...
```

The title line and `Error handling menu:` are inverse bars (TM-785 p3). Note there is no space
before `(` and one after it.

| situation | message | items | version | citation |
|---|---|---|---|---|
| illegal input at the debugger (`X := W.`) | `Error found by esp_macro_expander:` / blank / `illegal slot assignment: A := A` | `Continue`, `Cancel this input`, `Kill this process` | 2.10 | TM-181 p5 (title `Error occurred in debugger_4( process «?»7 )`) |
| Librarian `Execute` of an install file when the package exists | `Package drawing already exists` / `Cannot load package_template_file` | `Erase existing package and continue`, `Inspect the information of this event`, `Return to librarian top level` | 5.0 | TM-785 p3 (title `Error occurred in librarian_59( process 59 )`) |
| after `Erase existing package and continue` | confirm menu titled `Really?` | `ERASE`, `STOP` | 5.0 | TM-785 p3 |
| a call made under `:catch(P,"Skip this class",...)` | (the error) | adds `Skip this class` (INFERENCE) | 6.1 copy | cil/src/ds_bep.esp:2007-2008 |
| `debugger_error_with_retry` | (the message) | a retry item (INFERENCE from the class name) | CAL | cal-esp/deb2.12/winpar.esp:267 |

Item semantics (PROSE + INFERENCE): `Continue` resumes; `Cancel this input` abandons the current
top-level input and re-prompts; `Kill this process` ends the process; `Inspect the information of
this event` opens the inspector on the event object; `Return to <tool> top level` throws to the
tool's top loop. TR-087/TR-285 list the recovery kinds: resume, fail, return to a resumption point,
kill (STRUCTURE §2).

### 6.2 Other top-level messages

| text | where | grade | citation |
|---|---|---|---|
| `> Success !!`, `> Fail !!` | listener answers, 1.00 | SCREENSHOT | TM-134 p68; TM-125 p7 (Fig 4) |
| `aborted.` | output loop aborted by `control#"c"` etc. | COPY | cil/src/ds_bep.esp:3477-3488 |
| `illegal command` | Librarian command item not understood | COPY | cil/src/ds_bep.esp:3381-3411 |
| `User cgs registered` | user registration | PROSE | gog-esp/INSTALL.e:31 |
| `Class ... does not exist.` (クラス … がありません。), ` is not found !`, ` !!! Error !!!` | pimmcsp error window for a missing class | USAGE | pimmcsp pimos_remote_login get_class_obj/2 (ptf) |
| `This system has no librarian window interface!!` | library_error when a menu command runs without a window | COPY | cil/src/ds_bep.esp:1845-1856 |

### 6.3 Abort and interrupt

- 1984 keys (§3.4): kill `control#"k"`, lull `control#"l"`, arouse `control#"a"`, status
  `control#"s"`, all sent to the Coordinator for the window's expert.
- Held programs (COPY, cil): a long output loop polls `:read_sense(Window,C)`. `mouse#mm`,
  `control#"c"` and `key#abort` abort it: it prints `aborted.` and fails.
- The Coordinator owns an abort handler with an abort menu window (`:abort(#coordinator instance,H)`,
  §2.5). INFERENCE: this menu is what the abort key shows, offering the processes to abort.
- `:raise(#throw,abort)` and the tags of §2.10 unwind to a catcher.

### 6.4 Console break (outside SIMPOS)

The CSP console can stop SIMPOS (PROSE, fuzclust/fuzclust/README:143-159):
1. Push BREAK.
2. Answer `Do you want to Halt? (Y/N/T)` with `T`.
3. Kill with `> K nn` (nn = process number).
4. Type Return on an empty line to continue SIMPOS, which "shows the notification of terminated
   processes".

INFERENCE: this is the CSP monitor; a stand-in need not reproduce it.

### 6.5 Logout and shut down

- `logout` -> `yes` (7.x; gog-esp/INSTALL.e:34).
- `shut down`: "all windows vanish and it ends" (TM-134 p67).
- 1.x-2.50 have `login` in MEDIA SYSTEMS and no visible `logout`; the A00 video row 9 reads
  `login` or `logout` (poor). What 1.x does on `login` while logged in is UNSPECIFIED.
- What happens to running processes at logout is UNSPECIFIED.

---------------------------------------------------------------------------------------------------

## 7. Stand-in notes: minimum behaviour for the held programs, in build order

1. **`process` and `as_program`** from the TM-100 source:
   - `:create(#process,P)`, `:create(#process,P,Mode)` (accept any 4-list),
     `:activate(P,Prog)` running `:invoke(Prog)` -> `:goal(Prog)` in a new thread of control.
   - `:self/2`, `:get_number/3`, `:get_process/3`, `:exterminate/1` (call the program's
     `:cut_off/1` and `:exit/1` if defined, INFERENCE), `:set_area_limit_execution/7` (accept and
     ignore), `:set_sub_priority/2`, `:set_package/2`.
   - `as_program` class `:create/2` = `:new/2` (programs override it).
   - The process carries user, world, package and the three standard streams.
   - Uses: process 389 plus as_program create/2 and new/2 94, i.e. 483.
2. **Generic object methods** that the B-scan booked on as_program: `:get_slot/3`, `:set_slot/3`
   (instances and classes), `:class_object/2`, `:refute/3`, `:method/3`. 338 uses (345 with the
   two as_server_program slot rows). They belong in the root class (INFERENCE), which is outside
   this partition; whichever document covers the root object class should take them.
3. **`messenger`**: `show/2,3` puts up a message pop-up (string or `{Format,Args}`, options
   `font/1`, `beep`) and returns. `confirm/2,3` does the same and waits for a click, then succeeds.
   120 uses (122 with the misspelt `comfirm/2`, which should not be added).
4. **`stop_watch`**: create/start/stop/reset/show with a millisecond count via `:get_count/2`.
   93 uses.
5. **Login.**
   - A login window with `user     > ` / `password > ` prompts (7.x form). `me`/`me` accepted for
     an unregistered user (1.0). `superuser`/`superuser` exists.
   - Then build the world: `me` = `user:<name>`, `user:` = `>sys>user`, `font:` = `>sys>font`.
   - Read `me:login.com`. Apply `define`, `package` and `shell_transient`; keep `menu`; store all
     other heads for `:information(#coordinator,Key,V)`, failing on an unknown key.
   - Show the status line (§4.4).
   - `pimfep##simpos_user`'s create/4 is the call sequence to reproduce (§4.1).
6. **Coordinator**:
   - `login_user/2` (name), `get_instance/2`, `information/3`, `whiteboard/2` plus the instance's
     `get_whiteboard/2`, `abort/2`.
   - A whiteboard object with `read/2` and `write/2`.
7. **System menu.**
   - Double right click opens `SYSTEM MENU`: login-file columns, then a fixed MEDIA SYSTEMS column.
     For the held era, use the 2.50 list plus `logout`; INFERENCE for 7.x, whose full list is
     unknown.
   - Selecting a class item: `create`/`kill` pop-up when an instance exists. On `create`, make the
     program, a process and activate.
   - `no_select` items are inert.
   - An unknown class reports an error window (§6.1) with `Kill this process` (INFERENCE).
8. **`user`**: `login_user/2` (object), `user/2`, `user_list/2` (index by name), `identify/4`;
   instance `local_name/2`, `initial_mode/2`. **`world`**: `create/2`, `define/3`,
   `set_default_logical_name/2`.
9. **Shell window.**
   - `$ ` prompt; `call C`, `alias N C.`, transient commands.
   - Tokenise options into sign and name strings and `&name value` into three strings; `{ file` =
     stdin.
   - Start the class in a new process with the shell's streams bound and arguments readable by
     `get_arguments/2` and `parse_arguments/2`.
   - Wait for the process to end before the next prompt (INFERENCE).
10. **Debugger window** (listener).
    - `?- ` prompt; read a goal ending in `.`; run it in the debugger's process.
    - Print bindings as `Var= value` (objects `$class`), or `> Fail !!` (INFERENCE that 2.x still
      prints Fail).
    - `Variable` pane. Trace lines in the §5.4.3 format if tracing is implemented.
    - The held programs only need the listener; GOG's install types `:init_start(#cgs_main).`
11. **Error window** (§6.1) for uncaught errors in any process: `Error occurred in
    <name>( process <n> )`, the message, `Error handling menu:` with `Continue`, `Cancel this
    input` (listener only), `Kill this process`.
    - `:catch/5`, `:throwing_hook/7`, `:refute_in/5`, `throw` `raise/1,2` and
      `as_event_handler` dispatch (`invoke/5`) must interact with it.
12. **Server and network programs** (`as_server_program`: `give_answer/3`, `convert_con_req/6`,
    `get_line/2`; `network_login_user`) only when the network stand-in exists.
13. **Not needed by any held program**: the 1984 translation table, `e_process`, `look_up/6`; the
    CAL-debugger classes (`debugger_gate` ...). cal-esp brings its own copies, but they call
    `trace_exception_handler` and `interpreter` (UNSPECIFIED, 15 + 6 uses).

---------------------------------------------------------------------------------------------------

## 8. Coverage

Computed from `coverage_shell.tsv` (115 required class/instance methods on the 38 shell classes):

```
cd pim/docs/simpos/subsystems/coverage
awk -F'\t' 'NR>1{n[$7]++; u[$7]+=$5; N++; U+=$5} END{for(k in n) printf "%s\t%d\t%d\n",k,n[k],u[k]; print "TOTAL\t"N"\t"U}' coverage_shell.tsv
```

| status | methods | uses |
|---|---|---|
| DOC-class | 4 | 218 |
| DOC-unowned | 11 | 53 |
| USAGE | 31 | 739 |
| USAGE-unowned | 10 | 45 |
| NONE | 59 | 198 |
| total | 115 | 1,253 |

So 15 of 115 methods (13%) have documentary support, but they carry 271 of 1,253 uses (22%). With
USAGE added, 56 methods (49%) and 1,055 uses (84%) have a stated meaning. The DOC-unowned rows on
`create/2` and `new/2` (stop_watch, inspector, debugger_stop_watch, interpreter, call_counter,
debugger_gate, dummy_debugger, as_event_handler) are name-only matches: a printed `create/2`
exists, but not on that class.

By class (uses): as_program 505 (35 methods), process 389 (10), messenger 120 (5), stop_watch 93
(5), as_server_program 21 (5), call_counter 17 (17), trace_exception_handler 15 (4), debugger_gate
15 (2), coordinator 14 (4), throw 12 (2), debugger_error 12 (2), others ≤ 7 each.

Adjusted reading (this document's own, not the script's):
- 18 CAL-debugger `as_program` rows (49 uses: do_state, get_state_switch, get, set_leash,
  get_leash, mam_do_menu, get_inspector, set_mode, set_prompt, reset_prompt, get_default_class,
  reset_window, set_debugger_font, select_font_from_menu, select_package_from_menu,
  with_vars_window, set_title, initial_setting) are misattributed COPY internals. 17 of them are
  NONE rows; `set_mode/3` is USAGE-unowned. `initiation_table/2` is kept apart as probably real.
- `process self/2` (211 uses) is PRINTED in the as_program source (TM-100 p11), although the
  script counts it as USAGE.
- `set_slot/3` and `get_slot/3` (322 uses including class forms) are generic object methods, not
  as_program's.
- On that reading the genuinely unknown shell surface is small: `trace_exception_handler` (15),
  the `call_counter` setters (17), `post/1`, `trace/2`, `debugger_recorder`, `dummy_debugger` and
  `user_process_profile get_user_profile/5`. The large unknowns are behavioural (§5.3.5, gaps
  file), not missing method names.
