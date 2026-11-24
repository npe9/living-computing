# ifs_libshell: the Librarian and the shell/top level, as the held IFS material shows them

Agent: ifs_libshell. Date: 2026-11-24.

**Sources**
- IFS archive tree, read-only:
  `scratchpad/simpos2/extract/ifs_simpos/<archive>/`.
- Papyrus source: `scratchpad/simposspec/B/x/papyrus_src`.
- ESP manual TeX: `scratchpad/simpos2/extract/ESPtex{,-j}`.

**Citations**
- Archive files are cited as `<archive>/<path>:<line>`.
- Japanese text was decoded from ISO-2022-JP. Some archives (kwic-esp, icotext) had their ESC bytes
  stripped, so they were decoded by hand-restoring the ESC bytes.
- Translations are marked TRANSLATION.
- Grades follow RULES: PRINTED / PRINTED-INTERFACE / USAGE / PROSE / SCREENSHOT / INFERENCE.
  - The IFS README/INSTALL files count as PROSE.
  - Application code counts as USAGE.
  - Code that is itself SIMPOS (see "POSSIBLE SIMPOS CODE") is graded USAGE, with the provenance
    stated.

**Arity**: the receiver is counted, as in `required/`.

---------------------------------------------------------------------------------------------------

## 0. Versions the held material names (PROSE)

| archive | SIMPOS version stated | machine | citation |
|---|---|---|---|
| sum | "SIMPOS 3.0, 3.2, 4.0, 5.0"; ESP version 2 | (12MW) | sum/INSTALL:7-8 |
| knov | SIMPOS 5.1 | PSI-II | knov/INSTALL:10 |
| disc | SIMPOS 6.2 | OKI-PSI-II | disc/INSTALL:7-9 |
| euod | "SIMPOS v.6 or v.7"; "ESP v.0.0"; at least 12MW | PSI-II or PSI-UX | euod/INSTALL:1-5 |
| cal-esp | "SIMPOS Version 7.0" (Japanese: 7.0 or later) | PSI II, PSI III | cal-esp/INSTALL:14, INSTALL.j:15 |
| papyrus | "Simpos 7.0 -" | - | papyrus/INSTALL:4 |
| fuzclust | SIMPOS 7.1 | Mitsubishi PSI II | fuzclust/fuzclust/README:89, INSTALL.j:4 |
| icotext, kwic-esp, utter, txtstrct | SIMPOS 7.1 | PSI-II | icotext/INSTALL:15; kwic-esp/INSTALL:14; utter/INSTALL:9; txtstrct/INSTALL:4 |
| kappa2 | "SIMPOS Version 7 or 8" (PSI-II); "SIMPOS Version A22" (PSI-III); Kvif server needs A22 | PSI-II/III | kappa2/INSTALL:7-8, :20 |
| cil | SIMPOS 8.1 | PSI-II | cil/INSTALL:6 |
| gog-esp | "SIMPOS" (no number); 1992-93 releases | PSI/UX | gog-esp/INSTALL.e:8-9, README.e:11-13 |
| chal | "standard PSI-II or standard PSI-UX" | - | chal/INSTALL:2 |
| cil source comments | "SIMPOS 6.1" (patch class), "V6.11", "simpos8.0" | - | cil/src/ds_bep.esp:1774, :25; ds_brs.esp:606 |

---------------------------------------------------------------------------------------------------

## 1. SHELL / TOP LEVEL

### 1.1 The login file `login.com` (command language of the top level)

The file is read at login.
- "Logout and login again" is required after every edit. Prose to this effect appears in
  cal-esp/INSTALL:43, euod/INSTALL:42, utter/INSTALL:73, txtstrct/INSTALL:14 and
  papyrus/INSTALL:55.
- Its place is the user's home directory, `me:login.com` (cal-esp/INSTALL:38) or
  `>sys>user>kappa>login.com` for user kappa (kappa2/INSTALL:30).
- The Japanese text says "the login file login.com directly under logical name me:"
  (kwic-esp/INSTALL.j:143, TRANSLATION).

It is a set of Prolog-syntax clauses with **0-arity heads**. Each head is one section. This
summary is USAGE, from all seven held login files:
disc/login.com, fuzclust/fuzclust/install/login.com, gog-esp/login.com, kappa2/kappa2/login.com,
kappa2/kappa2/init/sample/login.com, and the fragments printed in INSTALL files.

| head | body | meaning | citations |
|---|---|---|---|
| `menu :- ...` | a conjunction of zero or more option goals, then `items_list(Columns)` | defines the **system menu** | disc/login.com:3-47; gog-esp/login.com:6-24; kappa2/kappa2/login.com:9-32 |
| `define :- "Name" := ["Path", ...], ...` | comma-separated `:=` pairs; the right side is a **list** of pathnames | defines **logical names / worlds**: "Name:" resolves through the listed directories. A path may itself start with a logical name defined earlier ("src" := ["cgs:source"]) or a built-in one ("user:", "me:"). Absolute paths start `>sys>` | disc/login.com:49-55; gog-esp/login.com:30-58; kappa2/kappa2/login.com:34-83; utter/INSTALL:69-71 |
| `package :- Name .` | one atom | the user's **default package** at login (`user` when there is none) | disc/login.com:57 (`tjbunmyaku`); fuzclust .../login.com:20 (`user`); gog-esp/login.com:60 (`cgs`); kappa2/kappa2/login.com:85 (`kappa`); cal-esp/INSTALL:39 (`cal_user`); papyrus/INSTALL:48 (`papyrus`) |
| `shell_transient :- [ {Name,'pkg##class'}, ... ]` | a list of 2-vectors; the class is a **quoted atom** holding `##` | registers **shell commands**: typing `Name` in the shell runs that `as_program` class. More in 1.3 | gog-esp/login.com:26-28; kappa2/kappa2/login.com:87-101; kappa2/kappa2/init/sample/login.com:45-59 |

**Menu options seen before `items_list`** (USAGE):
- `area_limit(free)`: gog-esp/login.com:7. INFERENCE: it gives processes started from the menu an
  unlimited area limit. Compare the `set_area_limit_execution` arguments in 1.4.
- `font("font:test_11.font")`: kappa2/kappa2/login.com:10. The system-menu font, given as a file
  under the logical name `font:`. INSTALL copies fonts to `>sys>font` (kappa2/INSTALL:36), so
  `font:` = `>sys>font` (INFERENCE).

**`items_list([Column1, Column2, ...])`** (USAGE)
- It takes a **list of columns**. Each column is a list of `{"Label", Target}` 2-vectors.
- In every held file the first column repeats the standard SIMPOS items, so these are
  probably the defaults that the user's file restates (INFERENCE). They are:

```
{"debugger",debugger} {"pmacs",pmacs} {"file",file_manipulator} {"librarian",librarian}
{"shell",shell} {"spooler",spooler_manipulator} {"pattern editor",pattern_editor}
```

- Copies are at disc/login.com:6-12, fuzclust/fuzclust/install/login.com:5-11, gog-esp/login.com:9-17
  and kappa2/kappa2/login.com:12-18.
- Variants:
  - kappa writes `simpos##pmacs` (kappa2/kappa2/login.com:13).
  - fuzclust adds `{"document",document##document_processor}` (fuzclust .../login.com:12).
  - gog adds `{"CMT",cmt##cmt_user_manipulator}` and `{"diff",user##my_dif}`
    (gog-esp/login.com:14-15).

So the standard targets are bare atoms naming SIMPOS classes: debugger, pmacs, file_manipulator,
librarian, shell, spooler_manipulator, pattern_editor. They are USAGE (as target names); that the
targets are classes is INFERENCE from the user items.

**Target forms seen** (USAGE)
- A bare atom, which is a class in the default/simpos package: `grape_system`, `cgs_start`,
  `demo`, `se_main`, `cgs_utility`, `ctx_system`, `papyrus`.
- `pkg##class`: `tjbunmyaku##demo_sentence`, `kappa##kappaMOP_manager`,
  `contrainte##cal`, `spec_ms##coordinator`, `yourei_v2##sysLoader`.
- knov writes the target as `#knov`: "add the class name "#knov" at the menu item"
  (knov/INSTALL:21-22, README:102). sum likewise registers `#run_text_analyzer`, `#run_you_edit`
  and `#run_wkm` (sum/INSTALL:35-37). These are PROSE. INFERENCE: they mean the same as a bare
  atom, or they reflect an older (SIMPOS 3-5) syntax.
- `no_select`: a **non-selectable label/separator** item.
  - Column titles: `{"SYSTEM MENU", no_select}`, `{"DEMO MENU    ", no_select}`
    (disc/login.com:5,13); `{"<Kappa>", no_select}` (kappa2/.../init/sample/login.com:20).
  - Blank spacers: `{"", no_select}` (same file :22).
  - A disabled entry: `{"5:conjbun    ", no_select}` (disc/login.com:23).
- The papyrus demo sub-system's icon command file holds only `items_list([]).`
  (papyrus_src/demo/EDITOR/icon.com.1:5). It is the same term as a fact, not inside `menu :-`.

**Meaning of selecting an item** (PROSE)
- The program starts in a new process. Each program is an `as_program` subclass with `:goal/1`
  (section 1.4).
- Process: "Click twice the right button of the mouse -> The system menu appears. Select
  "librarian" ... -> The shape of the mouse cursor changes. Specify the coordinates of left-top and
  right-bottom corner of the window" (utter/INSTALL:30-38).
  - The Japanese text says the cursor becomes 鍵形 (lit. "key-shaped"; likely 鉤形, a corner-hook
    shape). TRANSLATION, utter/INSTALL.j:34.
- gog: "Define the size of the window using the mouse, and the window will be displayed"
  (gog-esp/INSTALL.e:25, 46).
- cal: "Select the item titled "CAL" from the system menu by clicking the left button of the mouse"
  (cal-esp/INSTALL:44-45).
- So: double right click opens the system menu, a left click selects, and a two-corner sweep sets
  the new window's rectangle.

**System-menu sub-items named in prose (beyond login.com)**
- `SYSTEM MENU --> [others] --> [user] --> [maintenance] --> [register]` registers a user. Fields
  printed: `Username`, `Password`, `Rank : general`; the reply is `User cgs registered`
  (gog-esp/INSTALL.e:24-31). PROSE (screen transcript).
- `SYSTEM MENU ---> [logout] ---> [yes]` (gog-esp/INSTALL.e:34). PROSE.
- Login prompt transcript: `user     > superuser <CR>` / `password > superuser <CR>`
  (gog-esp/INSTALL.e:19-20, 37-38). PROSE.
- "select TCP-IP menu from System menu then select "reset network""
  (fuzclust/fuzclust/README:139). PROSE.
- "process manipulator", whose item `parent` "show[s] all process"
  (fuzclust/fuzclust/README:144-152). PROSE.
- "file manipulator": "define logical name", "make subdirectory", Copy and Catalog in its
  "directory menu".
  - The Copy prompts are `Copy>` and `To>`; the Catalog prompt is `Catalogue>`
    (fuzclust/fuzclust/INSTALL.j:65-88, TRANSLATION).
  - The file manipulator can also "Define worlds" (disc/INSTALL:23-25).
  - PROSE.

**Console (CSP) break** (PROSE, fuzclust/fuzclust/README:143-159). To kill system-spawned
processes:
1. "Push BREAK key to STOP SIMPOS!!"
2. Answer `Do you want to Halt? (Y/N/T)` with `T`.
3. Kill with `> K nn` (nn = process number).
4. "Type Return without any character to continue to SIMPOS", which "shows the notification of
   terminated processes".

INFERENCE: this is the console-processor (CSP) monitor, not SIMPOS.

### 1.2 Program start-up paths seen

| path | example | citation | grade |
|---|---|---|---|
| system-menu item from `login.com` | most archives | see 1.1 | PROSE+USAGE |
| shell command via `shell_transient` | kappa `loading`, `far` | kappa2/kappa2/login.com:87-101 | USAGE |
| shell `alias` + command line | `$ alias dtc yourei_v2##dbDeclTableCompiler.` | kwic-esp/INSTALL:91-99 | PROSE |
| shell `call <class>` | "invoke shell, and execute "call cil_install"" | cil/INSTALL:18 | PROSE |
| debugger window: a method call typed as a goal | `:init_start(#cgs_main). <CR>` | gog-esp/INSTALL.e:56 | PROSE |
| debugger window: a method call | euod: "Call the method :convert in a debugger window" | euod/INSTALL:56 | PROSE |
| PIMOS shell (not SIMPOS) | `cd "demo>KL1_SAV"`, `load("plib")`, `listener &`; then in the listener `program_executor.` | papyrus/INSTALL:63-74 | PROSE |
| P-CHAL top level (application's own) | `?- ['meeting.cal'].`, `?- halt.` | chal/README:34-109 | PROSE |

### 1.3 The SIMPOS shell (シェル)

**Prompt and commands** (PROSE; kwic-esp/INSTALL:89-99 and INSTALL.j:118-128, where the Japanese
says the underlined part is what the user types)

```
$ alias dtc yourei_v2##dbDeclTableCompiler.
$ dtc +s { ltbroot:source>kwic>standard.decl.
$ alias dbm yourei_v2##dbD_Maker.
$ dbm overwrite +s &source ltbroot:source>kwic>*.cil.
```

- Prompt `$`.
- `alias Name pkg##class.` binds a command name to a program class. Compare `shell_transient`,
  which does the same from login.com.
- A command line ends with `.`.
- Arguments are words; `+s` looks like an option.
- `{` (read the following as standard input?) and `&source` (a named argument or variable?) are
  not explained here. [Superseded by 1.5: `&source` is a named value; `{` is probably stdin
  redirection.]
- Wildcard pathnames (`*.cil`) are passed through.
- `call cil_install`: run a class (cil/INSTALL:18; INSTALL.j:18 says シェルを起動し、call cil_install
  を実行する). PROSE.

**What a shell command class receives** (USAGE)

These are kappa's ten `.SHELL` files, catalogued by kappa2/kappa2/utility/tool/CATALOG2.COM:7-21.
Each is a class `kappaXXX_process` with `nature as_program;` and an instance `:goal(Obj)`. Pattern
(kappa2/kappa2/utility/tool/CCTPR.SHELL:21-46; KSTPR.SHELL:19-49; LDTPR.SHELL:26-56):

```
:goal(Obj) :-
    :self(#process, Proc),
    :set_area_limit_execution(Proc,free,default,free,middle,nil,nil),
    :standard_input(Proc, Stdin),       % shell stdin  (redirectable)
    :standard_output(Proc, Stdout),     % shell stdout (redirectable)
    :standard_message(Proc, Stderr),    % message stream (prompts/errors)
    :get_arguments(Obj, Args),          % list of argument STRINGS
    ...
    :close_output(Message) ...
```

- `:get_arguments(Obj, Args)` (as_program, get_arguments/2) returns a **list of strings**:
  - `Arguments = [Table_nameS, Copy_tableS]`, then `:enter_atom(#symbolizer,...)`
    (CCTPR.SHELL:29-31).
  - Usage text `"Command Table New_table"` (CCTPR.SHELL:43).
- Option parsing in LDTPR.SHELL:80-88 (local `check_args`) expects the tokens
  `"-"`, `"s"`/`"t"`, `NUM` as **three separate strings**. The usage line is
  `loading [-t NUM] [-s NUM] TableName` (LDTPR.SHELL:35).
  - INFERENCE: the shell's tokenizer splits `-s` into `-` and `s`. [Superseded by 1.5: kwic's
    converter produces the same sign-then-name pair.]
- KSTPR.SHELL:31-48 prompts on the message stream (`Format> `, `Condition> `), reads the answers
  from standard input with `:getl`, and writes records to standard output with
  `:putf(File,"\q.\n",[Record])` (:136).
  - So stdin/stdout are redirectable streams, and messages are separate. This is USAGE.
- Exit idiom (LDTPR.SHELL:43-56):
  - The first `:goal/1` clause ends in `fail`.
  - A second `:goal/1` clause then closes stdin/stdout and sleeps 5 s:
    `:create(#alarm_watch,W)`, `:create(#time,T)`, `:set_value(T,0,0,5,0)`, `:on_after(W,T)`,
    `:wait(W)`.
  - KSTPR.SHELL:51-62 has the same as a commented-out `after:goal`.
  - INFERENCE: the window or pipe needs time to flush before the process ends.
- Shell commands may still open windows: `:create(#window_without_label,
  [permission(out),size(100,50),position(0,0)],Win)`, `:activate(Win)` ... `:kill(Win)` as a
  progress counter (KSTPR.SHELL:65-67, 74; LDTPR.SHELL:64-66).

**`shell_transient` entries** (USAGE)
- kappa2/kappa2/login.com:89-100 maps
  `far -> 'superuser##file_backup'`,
  `make_sort_table -> kappaMST_process`, `search_pattern -> kappaSDT_process`,
  `create_copy_table -> kappaCCT_process`, `delete_table -> kappaDTT_process`,
  `create_table -> kappaCTT_process`, `search_record -> kappaKST_process`,
  `loading -> kappaLDT_process`, `unloading -> kappaULT_process`,
  `read_index -> kappaRIT_process`, `delete_record -> kappa_delete_tool`,
  `update_record -> kappa_update_tool`.
- gog-esp/login.com:27 has only `{far,'superuser##file_backup'}`.
  - `superuser##file_backup` is a class in package `superuser`, apparently SIMPOS-supplied.
    `required/` lists `file_backup` with create/2, restore/3, set_input/2 and set_output/2.
  - INFERENCE: `far` is a file-archive (backup/restore) command, and "transient" means a command
    run as a short-lived process.
- Defect seen: kappa2/kappa2/init/sample/login.com:57 has `'kappa##kappa_delete_れcord_tool'`.
  A JIS hiragana れ was typed for "re"; the main login.com:99 has `kappa_delete_tool`.

### 1.4 Programs: `as_program` and relatives (USAGE census)

Method: the B-scan JSON (`simposspec/B/raw/*.json`), using the transitive natures of every user
class, then `progcls.py`; output in `work/ifs_libshell/progclasses.txt`.

**Census**
- 170 user classes in 14 programs reach a SIMPOS program nature:
  - `as_program`: 164;
  - `as_server_program`: 6
    (fuzclust env_getter, participant, talk_input, talk_output; gog-esp remote_player;
    kappa2 kappa_remote_user);
  - `as_event_handler` (handler, not program): 4 more.
- No held class inherits `as_interrupt_program`, `as_trap_program` or `as_boot_program` in source.
  They appear only as `simpos##` refs in compiled packages (partition_shell tiers).

Methods those classes define (counts over the 170):

| method | n | notes |
|---|---|---|
| instance `goal/1` | 165 | **the entry point**: `:goal(Program)`. All program work happens here. |
| class `create/2` | 27 | usually `:create(Class,Obj) :- :new(Class,Obj)` (e.g. kappa2/kappa2/utility/tool/CCTPR.SHELL:11-12), so a creator can pass extra state |
| class `cut_off/1`, instance `cut_off/1` | 13 / 6 | cleanup hook; cil coordinator_body `:cut_off(C) :- reset` (cil/src/ms_cdn.esp:120-121). INFERENCE: called when the process is cut off / killed |
| instance `exit/1`, class `exit/1` | 1 / 4 | cil coordinator `:exit(C) :- :cut_off(C!coordinator_body)` (cil/src/ms_cdn.esp:53-54). INFERENCE: SIMPOS calls `:exit` on the program when it ends from outside |
| instance `exit_rtn/1` | 7 | application-defined |
| instance `initiate/2`, `initiate/1` | 7 / 2 | application-defined |
| instance `current_state/2` | 2 | **"current state for SIMPOS saver"**: it fills a SIMPOS `initiation_table` with `{Key,Value}` pairs. Comments: cil/src/ms_cdn.esp:537-548; "set current state into the given initiation table for SIMPOS process saver", cil/src/ds_brs.esp:2654 and ds_edt.esp:1453. USAGE+PROSE |

**How a program creates another process** (USAGE, cil/src/ms_cdn.esp:343-349):

```
:create(Class, Program),
Process_mode = [free, free, query, middle],
:create(#process, Process, Process_mode),
:activate(Process, Program)
```

- So `process` create/3 takes a 4-element mode list, and activate/2 takes a program object. The
  process runs `:goal(Program)`.
- INFERENCE about the mode list: area-limit, area-limit, a query/situation mode (`query`), and
  priority `middle`.
- Shell commands instead set `:set_area_limit_execution(Proc, free, default, free, middle, nil,
  nil)`: process set_area_limit_execution/7 (kappa .SHELL files).
- cil_install uses `:set_area_limit_execution(Context, free, free, free, free, _, _)` on
  `:context(Me, Context)` (cil/src/INSTALL.esp:44-46).

**How programs reach the user** (USAGE)
- Messages: `:show(#messenger, String)` (cil/src/INSTALL.esp:23) and
  `:show(#messenger, Msg, [font(F)])` (cil/src/ms_cdn.esp:87).
- Windows: `:create(#standard_io_window,[size(manipulator),permission(out),position(manipulator)],W),
  :show(W)` (cil/src/ds_bep.esp:3339-3343). INFERENCE: `size(manipulator)`/`position(manipulator)`
  ask SIMPOS to let the user sweep the rectangle, matching the prose in 1.1.
- Selector menus: `:instantiate(#selector_menu, {single_select, Title, size(W,H), CommandItems,
  ObjectItems}, Sel)`, `:activate(Sel, mouse)`, `:read(Sel, Code)` (cil/src/ms_cdn.esp:230-252).
  Here the item 4-vector is `{String, common, Code, _}`.
- Its own process number: `:self(#process,P)`, `:get_number(#process,P,N)` (ms_cdn.esp:219-220;
  cal-esp/deb2.12/winpar.esp:127-131). The number appears in window labels.
- The user: `:user(Process,User)`, `:local_name(User,Name)`. A login name `simpos` is mapped to
  `me` (cil/src/ds_bep.esp:3142-3145).
- The default package: `:get_package(Process,Pkg)` (ds_bep.esp:3147, 3027) and
  `:set_package(Process,Pkg)` (ds_bep.esp:3037).
- Librarian mode per process: `:get_library_environment(Process,Name,Mode)`,
  `:set_library_environment(Process,Name,Mode)` and
  `:check_library_environment(Process,Name,Value)` (ds_bep.esp:3229-3238, 2991).
  - Names seen: `catalogue_mode`, `error_mode`, `skip_mode`, `source_file_mode`, `node_name`
    (value `"my_node"` = local) (ds_bep.esp:3369-3372, 1969-1970).
  - cil_install sets `error_mode` off to "hold" librarian messages (INSTALL.esp:47-48).
- Error-skip and unwind helpers on `process` (USAGE, ds_bep.esp):
  - `:catch(Process, "Skip this class", Obj, Method, ArgVector)`: process catch/5 (:2007-2008,
    2100-2101). INFERENCE: it runs `Obj:Method(Args)`, and if an error menu is raised it offers
    the item "Skip this class", which makes the call fail.
  - `:throwing_hook(Process, Obj1, M1, Args1, Obj2, M2, Args2)`: process throwing_hook/7
    (:2186-2188, 2441-2442, 2580-2582). INFERENCE: it runs Obj1:M1(Args1), and on a throw/abort
    runs the cleanup Obj2:M2(Args2), as an unwind-protect.
- Abort polling inside output (ds_bep.esp:3477-3488): `:read_sense(Window,C)`. The codes
  `mouse#mm`, `control#"c"` and `key#abort` abort. It prints `aborted.` and fails.

### 1.5 Shell argument protocol (kwic rsx_tool_macro; kappa2 .SHELL)

Version/year: kwic-esp and kwic-esp-002 (same text in both copies; INSTALL says SIMPOS 7.1, §0); kappa2 utility/tool (files dated '91-'92, (C)1992).

- `:goal(Class, ArgL)` (class goal/2) is a macro-inserted class method in the kwic tools (USAGE, kwic-esp-002/kwic-esp/src/v2_tool.mac:39-47, macro `inserta` body). The body saves the three standard devices, converts ArgL, does `:new(Class,I)`, `:save_arguments(I,Arguments)`, `:goal(I)`, then restores the devices with `:set_standard_input/output/message` (USAGE, same lines). Its only held caller is dbDM's `:test` (dbDM.esp:9-46), so it is kwic's programmatic stand-in for invoking the tool as the shell would, not proven to be what the shell itself calls (INFERENCE).
- Macros `'STANDARD_DEVICES'` / `'CLOSE_STANDARD_DEVICES'` expand to `:standard_input/2`, `:standard_output/2`, `:standard_message/2` sends and `:input_closed`/`:output_closed` checks (USAGE, v2_tool.mac:25-37). A process carries three standard streams that are rebound per command (INFERENCE from the save/restore pattern).
- ArgL element conversion (USAGE, v2_tool.mac:60-89):
  - positional atom -> string via `:get_value_string(#fncFunction,...)`;
  - `+(Opts)` / `-(Opts)` -> for each option, two strings in the order **Value, NameString**, i.e. `"+","s"` or `"-","c"` (`'$MAKE_NAMED_ARGUMENTS$'(NameAtom,Value,[Value,NameString|Tail],Tail)`, :82-83);
  - `&([{Name,Value},...])` -> three strings `"&", NameString, Value` (:85-89);
  - `stdIn(S)`, `stdOut(S)`, `stdMsg(S)` -> `:set_standard_input/output/message(Me,S)`, nothing added to the list (:71-76);
  - anything else is dropped (:80).
- So a tool receives a FLAT LIST OF STRINGS in which an option is the sign string followed by the name string. This is exactly what kappa2/kappa2/utility/tool/LDTPR.SHELL:80-88 check_args expects for `-s NUM`: `"-","s",NUM` (USAGE). INFERENCE: the real shell tokenizes `-s` / `+s` into sign and name, and both kwic and kappa follow that convention.
- `:parse_arguments(Obj,{Positional,Named})` (instance parse_arguments/2) is **inherited from as_program**: the B-scan resolves all three sends (kwic-esp-002/kwic-esp/src/dbDM.esp:41, dbUtil.esp:68, dtCompiler.esp:42) as self-inherited with as_program the only nature, and required/requirements.tsv:1600 lists it under as_program. Named is a list of `{Name,Value}` pairs, as `'CHECK_OPTIONS'` (v2_tool.mac:92-102) shows: Value `"+"`/`"-"` sorts the first character of Name into plus/minus option lists, other pairs pass through. USAGE.
- `:save_arguments(I,Arguments)` (instance save_arguments/2) is sent once (v2_tool.mac:45) and is defined nowhere in kwic; the B-scan leaves it unattributed (required/requirements.tsv:3353). INFERENCE: also an as_program method (the setter that the shell uses before `:goal/1`), pairing with get_arguments/2.
- `:get_arguments(Self,L)` (as_program get_arguments/2) is what the kappa2 .SHELL programs use (USAGE, kappa2/kappa2/utility/tool/CCTPR.SHELL:29-31, LDTPR.SHELL:26-56). .SHELL pattern: `:set_area_limit_execution(P,free,default,free,middle,nil,nil)`, the standard_* devices, then get_arguments.
- Help grammar in dbDM (TRANSLATION, kwic-esp-002/kwic-esp/src/dbDM.esp:52-100): `(KEY) <Options>`; positional MakeMode overwrite | index_only | esp; `+q +D +I +s` (s = save catalogued objects (登録したオブジェクトをセーブ)); `-R -c`; `&source(path)` (wildcards allowed; if omitted, source is read from standard input), `&dic_class`, `&dic_package`, `&dic_file`, `&error_mode(skip|quit)`, `&def_jukugo`. So the install line `dbm overwrite +s &source ltbroot:...>*.cil` is positional `overwrite`, option `+s`, named value `&source` (resolves the §1.3 OPEN item on `&source`).
- dtCompiler help (kwic-esp-002/kwic-esp/src/dtCompiler.esp:54-60): options `+o +s -C -c &package &name`; "the declaration is read from standard input". So `{` in `dtc +s { file` is probably shell stdin redirection (INFERENCE; no shell grammar held).
- Interactive path: `:get_interpreter(Window,Inter)`, `:command_interpret(Inter)` (USAGE, kwic-esp-002/kwic-esp/src/dbDM.esp:9-46; cil/src/ds_brs.esp:64,91; cil/src/ds_edt.esp:65,98; cil/src/ms_msm.esp:497-498; kwic-esp/src/displays.esp:644): a window owns a command interpreter that runs a read-execute loop (INFERENCE).

---------------------------------------------------------------------------------------------------

## 2. LIBRARIAN

### 2.1 How users drive the Librarian (PROSE, install procedures)

Starting it:
- Select `librarian` from the system menu, then sweep the window (utter/INSTALL:28-38;
  gog-esp/INSTALL.e:44-46).
- The librarian runs in its own window, with a **command menu**.

**Librarian menu items/commands named** (verbatim from the prose):

| item path | prompt / result | citation |
|---|---|---|
| `Package` -> `Other Command` -> `Load package template` (utter; English spelling "Load packge template" at :48) | prompt `Directory Name> >sys>user>utter>PTF` -> "A window is created." -> select `LOAD ALL` -> "After a few minutes packages are created." | utter/INSTALL:40-58; INSTALL.j:40-56 |
| `Package` -> `Other command` -> `Load one package` | "input the file names" | papyrus/INSTALL:39-41 |
| `Package` item: "Define the new package named "euodhilos"" | - | euod/INSTALL:31-33 |
| `package` command, subcommand `set_default_package` | sets the default package (既定値パッケージ) | kwic-esp/INSTALL.j:106-107 (TRANSLATION); English: "set default package to yourei_v2" (INSTALL:84) |
| `catalogue` command | "catalogue "ltbroot:source>kwic>*.mac"", then *.esp | kwic-esp/INSTALL.j:108-110; INSTALL:85 |
| `save` command, its `menu` subcommand, then `SAVE ALL` | saves everything | kwic-esp/INSTALL.j:111 (TRANSLATION: "select the menu subcommand of the save command and select "SAVE ALL"") |
| `Execute` | prompt `Command>`; the user types `fxd("cgscmp.com").` | gog-esp/INSTALL.e:49-50; INSTALL.j:49-50 |
| `Execute` | "type "CATALOG.COM"" (prompt unnamed) | kappa2/INSTALL:39; INSTALL.j:39-40 (librarianで、Executeを選択し、プロンプトに対しCATALOG.COMと入力する) |
| "Open a catalog window. Select the "catalog" item in the menu." | input `BUP>*.esp,CALC>*.esp,...` (comma-separated wildcard list), then the "save" item, then return | euod/INSTALL:43-50 |
| "Save templates" | - | kappa2/INSTALL:40 |
| "Set the following classes as public class using librarian" | `[alg, bool, cal, setgb, smplx, smplx3, solver]` | cal-esp/INSTALL:32-33 |
| "Create the "contrainte" package (ENVIRONMENT: simpos)" | - | cal-esp/INSTALL:22-23 |
| "Create the "contrainte" package environment (ELEMENTS: [contrainte, simpos])" | - | cal-esp/INSTALL:24-25 |
| "Create "cal_user" package (ENVIRONMENT: contrainte)" | "This package inherits the package environment" | cal-esp/INSTALL:26-28 |
| "Set current package to ..." | - | cal-esp/INSTALL:29 |
| "Save ... package, ... package, and ... package environment" | - | cal-esp/INSTALL:35-36 |
| "Define the following packages by using librarian. jo_exk, tjbunmyaku, unilingua" / "Set default package" | - | disc/INSTALL:14-18 |
| "invoke librarian, and catalogue me:cil>src>INSTALL.esp" | the Japanese says コンパイルする (compile) | cil/INSTALL:17; INSTALL.j:17 |
| "Catalogue *.V32" ... "If error message is displayed, skip that class." ... "the system asks if you want to save all asserted predicates, then always save them. Never retract them." | save asks about **asserted predicates** | sum/INSTALL:18-22, 26-29 |
| Catalogue with package name 'gip', then save templates | - | kappa2/INSTALL:55-56 |

**Model the prose implies** (PROSE, with the version in each source)
- A **package** has an **environment**. Its default is `simpos`.
- A **package environment** is a named list of packages (ELEMENTS), and it can be saved.
- Classes may be made **public**, i.e. visible to inheriting packages.
- There is a **current/default package** for cataloguing.
- **Catalogue** compiles source into templates and class objects in the current package.
- **Save** writes templates (template files).
- **Package template files** can be loaded from a directory (utter's PTF directory holds the
  compiled `.ptf` packages).

cal-esp (SIMPOS 7.0) gives the most explicit form of this model.

Other routes to cataloguing:
- The pmacs editor: chal/INSTALL:5-11 has `M-x set_package` (prompt `Package Name(user):`) and
  `M-x catalogue_and_save` ("System outputs some messages of calaloging").
- The file manipulator's Catalog command (fuzclust INSTALL.j:84-88).

### 2.2 Command files (`*.com`, `CATALOG.COM`), read in full

**Form** (USAGE)
- A command file holds **one Prolog list term** `[Item, Item, ...]`.
- Comments are `%` lines, also trailing ones (`% rename NET.MACRO`).
- Every held file was read: gog-esp/cgscmp.com (218 lines; 11 lines are not path entries), kappa's
  33 `.COM`s, and kappa2/kappa2/init/ipl.com.

**Items seen**

| item | arity as written | meaning (from use + cil `library_utility` dispatch, 4.1) | citation |
|---|---|---|---|
| `make_environment(Env, [Pkg,...])` | 2 | create package environment Env with those elements | gog-esp/cgscmp.com:2 (`make_environment(cgs_env,[simpos])`) |
| `save_environment(Env)` | 1 | save it | cgscmp.com:3 |
| `make_package(Pkg, Env)` | 2 | create package Pkg with environment Env | cgscmp.com:4 |
| `save_package(Pkg)` | 1 | save package (template) | cgscmp.com:5 |
| `use_package(Pkg)` | 1 | set the current package for the following items | cgscmp.com:6 |
| `fxds([Path,...])` | 1 | catalogue the listed files **in order**: macro banks (`*.macro`, `*.MAC`) first, then ESP | cgscmp.com:7-214; kappa2/kappa2/kernel/hlc/CATALOG2.COM:7-120 etc. |
| `save_all_classes` | 0 | save every catalogued class | cgscmp.com:215 |
| `command(Path)` | 1 | **run another command file** (nesting) | kappa2/kappa2/CATALOG.COM:2-6; kernel/CATALOG.COM:7-29; tool/CATALOG.COM:7-9; net/CATALOG.COM:7-9 |
| `load(Pkg##Class)` | 1 | load (make) a class | kappa2/kappa2/init/ipl.com:7 (`load(kappa##kappa_loader)`) |
| `refute(Goal)` | 1 | **execute a goal**, here a method call | ipl.com:8-11: `refute(:ipl_load(#kappa##kappa_loader, ['kappa##kappaMDU','kappa##kappaLUU_process','kappa##pb_manager'],270))` |

Paths:
- Absolute: `">sys>user>cgs>source>utility>location.macro"`.
- Logical: `"hlc:HLC.MAC"`, `"kappa_tool:update_tool>CATALOG.COM"`.
- The logical names come from login.com's `define` (kappa2/kappa2/login.com:34-83). So kappa's
  CATALOG.COM only works when run as user `kappa` (PROSE: "Login to SIMPOS as user "kappa" to
  validate transferred login.com", kappa2/INSTALL:38).

**How command files are run**:
- From the Librarian `Execute` item. The gog prose has the user type `fxd("cgscmp.com").`
  (gog-esp/INSTALL.e:50), while the kappa prose has the user type just `CATALOG.COM`
  (kappa2/INSTALL:39).
- The earlier report TM-785 p3 shows `fdd("x.com")` from floppy (repo STRUCTURE.md §9).
- These are **variants, not harmonized**:
  - `fxd(String)`: the gog prose, and cil's dispatch (4.1) maps `fxd(P)` to `catalogue`.
  - `fxd(String)` cannot be the same thing as `fxds([...])` inside cgscmp.com. One runs a command
    file; the other catalogues a file list.
  - Yet in cil's library_utility `fxd(P)` means *catalogue P* (ds_bep.esp:3395). Typing
    `fxd("cgscmp.com")` would then catalogue a .com file as ESP source. In cil's dispatch,
    `fxds` is not special-cased (it becomes `:refute(UT,fxds,{List})`).
  - INFERENCE: in the real SIMPOS, `fxd` at the Execute prompt *executes a command file*. cil's
    copy (1988-91 patched) may predate or differ. OPEN.

**Command-file conventions in comments** (USAGE)
- Filenames were shortened for transfer, e.g. `"hlc:HLCIF.MAC", % rename HLC_IF.MACRO`
  (kappa2/kappa2/kernel/hlc/CATALOG2.COM:8-16).
- Version notes: `% Deleted for V4.2  '92/06/30 Tue by Shida(MTC)` (:17-18).
- Commented-out entries are skipped: `%  command("net:CATALOG.COM"),` (kernel/CATALOG.COM:25).

**Gaps in the held tree** (negative results)
- kappa2/kappa2/CATALOG.COM:2,4 calls `utility:CATALOG1.COM` and `utility:CATALOG2.COM`. With
  `"utility" := ["user:kappa>utility"]` (login.com:63) these would be
  `kappa2/kappa2/utility/CATALOG{1,2}.COM`, which are **not in the archive**.
  - Only `utility/tool/CATALOG{1,2}.COM` exist. They catalogue LOADCH/LOADER, the .SHELL files
    and the utility tools.
  - The per-utility CATALOG.COMs (bck, dbc, ...) are never referenced by a held file.
  - INFERENCE: the top-level utility CATALOG1/2 were omitted from the distribution.
- kappa2/kappa2/utility/tool/CATALOG2.COM:10 names `"tool:KAPPA_PURGE.ESP"`. The held file is
  `KAPPA_PURGE.ES`, a truncated name.
- euod/README:43 and INSTALL:21 list a `login.com`, but there is none in the held euod tree.

### 2.3 The ipl.com command file (kappa)

The file is kappa2/kappa2/init/ipl.com:6-12. It is installed to `>sys>kappa` (`kappa2>init>*.* ->
>sys>kappa>*.*`, kappa2/INSTALL:28). It:
- loads class `kappa##kappa_loader`;
- refutes `:ipl_load(#kappa##kappa_loader, [ClassNames], 270)`.

INFERENCE: this is a SIMPOS "IPL command file". It is executed at system start-up to preload
classes into the IPL/system area. 270 is an unexplained number; perhaps an area size or a
priority. [Superseded: LOADER.ESP read; 270 is a class count for a progress meter, see 2.5.] Also in that directory: `start_up.kappa`, `KP_ADDOPE.INC`, `KP_REMOPE.INC`
(kappa2/README:65-66). LOADER.ESP read later: see 2.5.

### 2.4 Sends to the Librarian and system objects (task item 4)

Method: `work/ifs_libshell/rcv.py` over the B-scan sends of all 15 held programs; output `work/ifs_libshell/rcv.txt` (116 receiver/method/arity rows, count, first site). Arity counts the receiver. All USAGE unless marked; the meaning comes from the calling code at the cited site.

**library (class object `#library`)**: the catalogue database itself.
- `get_class_object/3` (160 sites; cal-esp/cal2.12/control.esp:224): name atom (may be `'pkg##class'`) to class object. Also gog-esp/CGS_INSTALLER.esp `:get_class_object(#library,'cgs##cgs_main',CGS)`.
- `make_class_object/2` (28): make (load) a class object for a name.
- `assign/1` (35): `Library = #library, :assign(Library)` before queries (kappa2/kappa2/utility/tool/LOADER.ESP:160-163). INFERENCE: binds the library for the current process/package; meaning not in code.
- `check_info/3` (33): `:check_info(Library,Class,object)` succeeds if the class object is already loaded (LOADER.ESP:170).
- `check_package/2,3`, `check_class_id/3`, `get_class_id/5,6`, `get_class_id_in_package/6`, `get_class_id_in_environment/6`: name/package resolution (cal-esp debugger and cil spec_ds librarian copy).
- `make_package/2`, `make_package_forcedly/2`, `delete_package/2`, `delete_package_forcedly/2`, `delete_environment_forcedly/2`, `change_environment_in_package/3`, `load_package_template/3`, `save_package_template/3`: package lifecycle (cil/src/INSTALL.esp:227-228; cil/src/ms_ist.esp:388,857-859; gog-esp/CGS_INSTALLER.esp:374-376).
- `get_a_code/7`, `get_a_name/8`, `stick_predicate_tap/2`, `is_ipl_class_object/2`, `get_direct_superclasses/3`, `get_direct_referred_classes/3`, `get_exist_class/4`, `set_error_mode/1`, `reset_error_mode/1`: used only by the CAL debugger (cal-esp/deb2.12), i.e. SIMPOS-debugger-derived code (§4.3).
- `catalogue_class/2`, `abolish/2`, `abolish_class_object/2`, `register/2`, `define_public_classes/2`, `get_changed_classes/2`, `get_class_descriptor/6`, `is_name_only_class/3`, `make_class_template_from_internal_format/4`, `update_class_source_file/4`, `get_names/4`: only in cil's SIMPOS-6.1 librarian copy (ds_bep.esp), §4.1.
- `make_class_template/2`, `make_class_template_from_source/3`, `get_version/6`: kappa HLC compiler (kappa2/kappa2/kernel/hlc/HLCLIB.ESP:90-94).
- `write_class_template/2`, `delete/2`, `get_all_predicates_with_information/4`, `get_predicates_with_information/4`: cil ms_mdm.esp.

**library_utility (`:create(#library_utility,L)`)**: the programmatic Librarian (the same object the Librarian window drives; INFERENCE from cil's copy, §4.1).
- instance: `catalogue/3` (13; `:catalogue(U,[Term],_)` catalogues a TERM list, cal-esp/cal2.12/graph.esp:93, or source paths, cil/src/INSTALL.esp), `save/2`, `load/2` (`:load(Library,ClassNameList)`, LOADER.ESP:196), `delete/2`, `get_classes_with_wildcard/5` (kwic dbDM.esp:1131), `get_package/2`, `set_package/2`, `set_output/2`, `remove_output/1` (message window for librarian output; gog-esp/CGS_INSTALLER.esp:341-345), `load_environment_for_package_template/3`, `load_package_template/3` (`.env` and `.ptf` files; CGS_INSTALLER.esp:379-381), `get_direct_superclasses/3` (used as "does package cgs exist", :371), `get_class_id_atom_list/4` (sum).
- class: `assert/3`, `asserta/3`, `assertz/3`, `retract/3`, `retract_all/4`: dynamic clauses in a catalogued class used as a database (`:assertz(#library_utility, Obj!database_class, node(N,L))`, cal-esp/cal2.12/graph.esp:176; the class itself was made by cataloguing a term `class C with_macro macro_data has local end`, graph.esp:90-93). This explains sum's "save all asserted predicates?" librarian prompt (§2.1): asserted clauses live in class templates (INFERENCE).

**process**: `self/2` (211), `create/2` (64), `create/3` (9; mode list), `activate/2` (60), `get_number/3`, `get_process/3`, `exterminate/1`, `post/1`, `set_area_limit_execution/7`, `set_package/2` (chal/cal_start.esp:13). Two mode-list variants seen: `[free,free,query,middle]` (cil ms_cdn.esp:347) and `[free,default,free,middle]` (kappa LOADER.ESP:53,65).

**directory**: `retrieve/3,4` (99), `retrieve_with_wildcard/3,4`, `make/3,4`, `remove/4`, `rename/5`, `delete/3,4`, `kill/3`, `parent_directory/5`, `current_directory/3`, `change_directory/3`, `directory/5,6`.

**coordinator (class)**: `get_instance/2` (cal-esp/deb2.12/dmenu.esp:865), `information/3` (kwic dbUtil.esp:225), `login_user/2` (kappa REMAITR.ESP:230), `whiteboard/2` (kappa pcn.esp:4840). These are sends to SIMPOS's `coordinator`, not cil's same-named class (§4; INFERENCE from package: callers are not in spec_ms).
**user**: `login_user/2` (kappa kcm.esp:78), `user/2`, `user_list/2` (kappa USER.ESP:452).
**debugger**: only `!font`, `!user_command_items` slot reads and the `debugger_*` helper classes, all inside cal-esp/deb2.12 (§4.3).
**inspector**: `create/2,3` (cal debugger), instance `inspect/2` (kappa pcn.esp:4835).
**interpreter**: `create/3` (cal-esp/deb2.12/deb.esp:212), `interpret/2` (cil/src/cil_kl0.esp:314).
**esp_compiler** `compile/4` and **kl0_compiler** `compile_one_predicate/6`: one site each, cal-esp/deb2.12/cm.esp:703-705.
**world, user_process_profile**: no sends in any held program (CHECKED).

### 2.5 kappa ipl.com resolved (USAGE, kappa2/kappa2/utility/tool/LOADER.ESP, (C)1992, updates '91.11.08-'91.12.17 M.Ozawa(MTC))
- `kappa_loader` natures `as_class_with_lock, as_program` (:20-22).
- class `ipl_load/1` and `ipl_load/3`: create a loader instance and run it in a new process `[free,default,free,middle]` (:51-66). ipl_load/3 appends the option class list to `default_load_class` and adds `Number_of_class / 3` to `referred_class_num` (:96-101).
- So `270` in ipl.com is a class count used only to scale a progress meter: `referred_class_num := 118` carries the comment 概算で入れてメータ見ながら調整する。ロードされるクラスの総数は421 (TRANSLATION: "rough estimate, adjusted while watching the meter; total classes loaded is 421") (:27). The meter is a separate checker process `kappa_loader_checker_proc` (:186-190).
- Load path: `:lock(Class)` (as_class_with_lock), filter by `:check_info(#library,C,object)`, then `:load(#library_utility instance, NotLoaded)` (:160-197). Comment: `:lock` has `:unlock` as its own alternative, so no cut may follow it (:144-146, TRANSLATION).
- This resolves the earlier OPEN item on 270.

---------------------------------------------------------------------------------------------------
## 3. OTHER: the ESP manuals (Part B)

Held: ESPtex/overview-e.tex (2859 lines), ESPtex/program-e.tex (10299 lines), the Japanese originals ESPtex-j/overview-j.tex and program-j.tex (decoded with j.py), and ESPps/{overview,program}-e.ps (PostScript renderings dated Aug 1992 in the file mtime). Title page: "ICOT : Institute for New Generation Computer Technology 1990" (PRINTED, ESPtex/overview-e.tex:30). Year tag below: 1990 (English edition).

What is held is volumes 1 and 3 only. Volume 2 (Operations), which is where the librarian, system menu, login and debugger operations would be described, is NOT held (CHECKED, see below).

### 3.1 The four-volume SIMPOS manual set (PROSE, overview-e.tex:186-241; Japanese overview-j.tex:199-249)
1. Overview (this manual; 概説編): features of PSI, SIMPOS and ESP.
2. Operations (操作編): "Basic operations" (enter, compile, debug and execute a sample ESP program) and "Application operations".
3. Programming (プログラミング編): "ESP programming methods", "Basic programming", "SIMPOS programming system" (how programs use the window and file systems), "ESP/SIMPOS programming techniques".
4. Japanese document edition (日本語文書編集編): document layout, Kana-Kanji conversion.
- The Japanese says the set is 4 volumes (４冊分構成), overview-j.tex:199,209 (TRANSLATION).
- The held program-e.tex has only the sections "ESP Programming" (:140) and "ESP/SIMPOS Programming Techniques" (:4309). The "SIMPOS programming system" section (windows, files, I/O built-ins) that the overview promises is NOT in the held file (CHECKED: section list program-e.tex:140-10001).

### 3.2 SIMPOS structure as the overview describes it (PROSE, overview-e.tex)
- Two halves: programming system and operating system (:1047-1106). Figure labels: programming system "Editor/debugger/inspector/librarian"; I/O management "Window/file/network"; supervisor "Process management/user management/pool"; kernel "Memory management/device management/tracer/IPL".
- Kernel table (:1150-1180): GC "can be started from the system menu"; Tracer debugs ESP "at the KL0 machine instruction execution level"; IPL "Loads SIMPOS stored on the fixed disk", modes User / Developer / System.
- Supervisor (:1185-1216): process management (generation, suspension, execution queue, deletion; multi-process scheduling), user management "Registers users and sets the environment for login", pool (array, list, stack, bag, set).
- I/O management: five systems, window, file, network, magnetic tape, printer (:1232-1270).
- Programming system figure (:1290-1340): Pmacs (editor), debugger/inspector, librarian, I/O manipulators (file, window, process, spooler, magnetic tape), other tools (document processing, font editor, graphics editor). "The objects forming the functions are made public, so they can be used by user programs" (:1285 area; PROSE).
- Librarian (:1360-1375): all ESP programs and objects are centrally managed; the user writes source in Pmacs and then runs "the catalog operation with the librarian"; the librarian invokes the compiler internally, so the compiler is transparent; on cataloguing the source is catalogued into the library too, so source-to-code relation is managed.
- Debugger (:1377-1391): "internally invokes the interpreter and runs the direct execution code"; tracing, abort and restart. Inspector (:1393): displays and optionally modifies objects.
- Manipulators: "Of the manipulators displayed in the system menu, the user can select and run" one (:1403); five listed (:1420-1445).
- Compile and link (:2040-2070): the librarian's catalog operation analyses source, resolves inheritance, generates a "class template" (the load module) and a "class object"; only class templates go in the library; source is registered automatically during catalog.
- Package (:2539-2560): `Package-name ## class-name`; prefix `#` for a class object.

The Japanese overview says the same at overview-j.tex:438,754,1135-1139,1611-1613 (checked by eye; no differing claim found).

### 3.3 Packages and package environments (PROSE, program-e.tex:5250-5934, 1990; Japanese program-j.tex:5150-5530)
- A package is a class-name space and "is generated by the librarian"; the source declares its package with the use_package statement (:5262-5263).
- No duplicate class names within a package; duplicate package names are not allowed in one system (:5267,5323).
- "One package can hold only one package environment"; the package/environment link is set when the librarian creates the package (:5331).
- Class reference forms (:5339-5389): `Class`, `Pkg##Class`; `#Class`, `#Pkg##Class`; `nature Pkg##Class`; `Pkg##Class:method(...)`; `class C with_macro Bank has` / `class Pkg##C with_macro Bank has`.
- With a package environment (package name, environment name, environment inheritance) made in the librarian, `##` can be omitted; lookup is local package first, then the packages named by the environment (:5398).
- Only classes externally declared by the librarian (外部宣言) are visible without `##`; internal classes are reachable only with `Pkg##Class` (:5456; Japanese 5320).
- Priority example (:5496-5501): local package first; among environment packages, ambiguity means "Cannot be inherited" unless qualified.
- Standard environment: package environment "simpos" is inherited by the user's environment so SIMPOS classes are reachable by bare name (:5560). Patterns: private package, shared utility package via an environment "with_utility", large-system development, shared data ("with_dictionary") (:5509-5680).
- Binding is static, by registration order (:5688-5932): cataloguing a1 before its referent a2 registers only a2's NAME, a "preliminary reference"; deleting a local class does not fall back to the external one until the referring class is re-registered. This explains why the IFS command files catalogue in dependency order and repeat passes (INFERENCE linking to §2.2).

### 3.4 Macro banks (PROSE, program-e.tex)
- System macro bank name "esp_macro_expander" (:6976); macro banks must be registered before the class that uses them; they are saved with the librarian like classes; a registered macro bank is "loaded automatically as required" (:7269-7271).
- Definition form `macro_bank Name has [nature ...;]` (:7286-7287); `with_macro` on a macro bank (:7301-7309).
- `use_macro (package name ## macro bank name)` declares one bank for a whole source file; if omitted, "esp_macro expander" (sic) is assumed (:7721-7733).
- CONFLICTING VARIANT: the IFS librarian code (cil spec_ds##library_utility, SIMPOS 6.1 patch, §4.1) defaults to `simpos##esp_macro_expander_for_compiler`; the 1990 manual names `esp_macro_expander`. Recorded, not harmonized.

### 3.5 Not in the held manuals
login.com syntax, the system menu item list, the librarian window's commands, command files (fxd/fxds), the shell, and the debugger's command set: none of these appear in overview-e.tex or program-e.tex beyond the one-line mentions above (CHECKED by grep for librarian, catalog, login, system menu, debugger, inspector, interpreter, use_package; hits listed above). They belong to the unheld volume 2 (Operations).

---------------------------------------------------------------------------------------------------
## 4. POSSIBLE SIMPOS CODE

### 4.1 cil: three Librarian classes copied from SIMPOS and patched (cil/src/ds_bep.esp:1773-3518)

**Verdict: this is SIMPOS Librarian source.** It is three classes copied from SIMPOS 6.1, patched
by ICOT's CIL team ("T.S.") and re-catalogued under package `spec_ds`. It is not application code.

**Evidence**
- The file header says `(39) 91. 1.28 by T.S. merge patch class for library_utility`
  (ds_bep.esp:45).
- A comment says `% patch class for library_utility on SIMPOS 6.1` (ds_bep.esp:1774).
- PMACS and DEC-20 edit stamps:
  - `mkpsi000::>sys>user>yasuko>GEN.esp.6, 28-Jul-88` (:1776), before librarian_class_generator.
  - Three stamps before librarian_read_term:
    - `icpsi135::>sys>user>yasuko>READ.esp.2, 22-Jul-88` (:2327);
    - `icpsi123::>sys>user>soft>librarian>READ.esp.7, 26-Feb-88 ... Edit by soft` (:2328);
    - the DEC-20 file `<M-KONDOH.LIBRARIAN>ZREAD.ESP.79,  2-Jul-86 ... Edit by M-KONDOH` (:2329).
  - `mkpsi000::>sys>user>yasuko>UT.esp.2, 29-Jul-88` (:3122), before library_utility.
- Dated change comments run from 88/11/17 to 90/9/20. They name V4.0, V5.0 and V6.0 (:1967, :2369,
  :3035-3036).
- The real `:compile/2`, `:uncompile/2`, `:abolish_interpretive_code/2` and
  `:abolish_compiled_code/2` are **stubbed** as `:compile(_,_);` (:3358-3361).

**Package**
- cil/src/INSTALL.esp:93-105 catalogues ds_bep.esp into `spec_ds`. That package is made with
  environment `simpos` (INSTALL.esp:224-228; ds_bep.esp:64 `use_package(spec_ds).`).
- CIL's back end uses the patched copy explicitly:
  `( library_utility := L :- :create(#spec_ds##library_utility, L) )` (ds_bep.esp:68).
- cil_install itself uses plain `#library_utility` (INSTALL.esp:14), i.e. the real one.
- **Correction to required/NOTES.md**: the class is spec_ds##library_utility. NOTES.md says "spec_ms,
  esp_call, kl0", which is right for `builtin` only.

**Natures referenced only.** These SIMPOS mixins are defined nowhere in cil (grep):
- librarian_version, librarian_delete, librarian_package, librarian_spy, librarian_reference,
  librarian_fdd, librarian_subroutine;
- as_assert_utility, librarian_catalogue, as_class_maker, compiler_error_reporter.

librarian_class_generator and librarian_read_term **are** defined here. They shadow the simpos
classes of the same names, because own-package classes come first.

**Structure revealed:**

```
library_utility            natures librarian_version, librarian_class_generator, librarian_delete,
  (ds_bep.esp:3123)                librarian_package, librarian_spy, librarian_reference,
                                   librarian_fdd, librarian_subroutine, as_assert_utility
librarian_class_generator  nature  librarian_read_term       "mixin_class of library_utility" (:1780):
  (:1777)                  generate class_template/class_object; save class_template_file;
                           catalogue class to library (:1782-1785)
librarian_read_term        natures librarian_catalogue, as_class_maker, compiler_error_reporter
  (:2331)
```

#### 4.1.1 library_utility (ds_bep.esp:3123-3518)

**Class methods**
- `create/2`: "create library_utility without window (for program I/O)" (:3136-3155). It does five
  things:
  - stores the process;
  - takes its name from the login user's local name, mapping `simpos` to `me`;
  - assigns the named yank buffers `class`, `file` and `package` of #editor_yank_buffer;
  - sets the package slot to the process package if `:check_package(#library,P)` holds, else
    `simpos`;
  - calls `:assign(#library)`.
- `create/3`: "with user defined window", i.e. create/2 then `:create_window(UT,W)` (:3160-3162).

**Instance slots** (:3170-3177)
- `standard_output := not_defined`, `text_window := not_defined`, `flash_flag := off`.
- `package`.
- `name` ("login user name (key of dispol)").
- `library_environment is monogyny_list_index` ("mode").
- `yank_on_off := off`, `debug_flag := off`.
- Also used: `response_time_flag` (declared in librarian_read_term) and `subclass_check` (from an
  inherited nature).

| instance method | arity | body summary |
|---|---|---|
| command | 2 | **Command-list interpreter** `:command(UT, Items)`. Local check_command/4 maps:<br>`fxd(Path)` -> `catalogue {[Path]}`<br>`fxd(List)` -> `catalogue {List}`<br>`save(C)` -> `save {[C]}`<br>`load(C)` -> `load {[C]}`<br>`delete(C)` -> `delete {[C]}`<br>Otherwise get_name_and_arg: an atom is a 0-argument command, and a compound `name(A0..A5)` (an ESP vector) gives `{A0..}`. Then `:refute(UT,Name,Args)`: the item is **sent as a method to the library_utility**, with arity = items' args + 1. A failing item is ignored. An unmatched one prints `illegal command` plus the term (:3182-3183, 3381-3411). |
| set_output | 2 | If Output's class is `#librarian_io`: text_window = Output!text, flash on. Else text_window = Output, and flash on iff `:method(Output,flash,1)` (:3189-3203). |
| remove_output | 1 | (:3204-3207) |
| reset_output | 2 | (:3208-3212) |
| set_name, get_name | 2, 2 | (:3214-3216) |
| check_window_object | 2 | (:3218-3223) |
| set_mode | 1 | Copies the process's catalogue_mode, error_mode, skip_mode and source_file_mode into library_environment (:3225-3226, 3368-3376). |
| set_mode | 3 | `:set_library_environment(Process,Name,Mode)` plus a cache (:3228-3234). |
| get_mode | 3 | `:get_library_environment(Process,Name,Mode)` (:3236-3238). |
| get_package | 2 | Process package via `:check_package(#library,P0,P)` (:3240-3243). |
| message | 2/3/4 | Concatenates the parts and puts them to text_window, with flash and abort polling (:3245-3255). |
| writef 3, writet 2 | | to text_window (:3257-3261) |
| putl 2/3/4, putf 3, putt 2 | | to standard_output (:3263-3276) |
| display_text_window | 6 | Prints `- <Type> -`, `- Time: ... -`, `- Heap: N words -` (:3306-3322). |
| response_time | 5 | (:3324-3327) |
| display_response_time | 6 | (:3329-3333) |
| get_library_utility | 2 | Returns itself, "dummy" (:3335). |
| set_response_time_flag | 2 | (:3336-3337) |
| create_window | 2 | standard_io_window `[size(manipulator),permission(out),position(manipulator)]`, then show and set_output (:3339-3343). |
| create_pmacs_window | 2 | pmacs_window `[size(manipulator),position(manipulator)]`, then activate and set_output (:3345-3349). |
| check_subclass | 2 | (:3351-3352) |
| compile, uncompile, abolish_interpretive_code, abolish_compiled_code | 2 each | **stubs** (:3358-3361) |

**Response-time flag bits** (comment table, :3279-3303). Each bit times one step of an operation;
the operation is shown in the last column of the table.

| bit | step timed | operation |
|---|---|---|
| 512 | predicate, slot, classes | menu on |
| 256 | predicate, slot, classes | menu off |
| 257 | predicate, slot, classes, with output to file | menu off |
| 128 | write_class_template | COM |
| 64 | make_class_template | COM |
| 32 | make_class (as_class_maker) | CAT |
| 16 | make_class_template_from_internal_format | READ |
| 8 | abolish_class_object | READ |
| 4 | catalogue_class | READ |
| 2 | expand_definition | READ |
| 1 | gett | READ |

**Messages and keys**
- Messages: `illegal command`, `aborted.`, and the timing strings ` hrs. ` ` min. ` ` sec. `.
- Abort keys while printing: `mouse#mm`, `control#"c"`, `key#abort` (:3477-3488).

#### 4.1.2 librarian_class_generator (ds_bep.esp:1777-2326)

**Slots**
- `load_list_tempo is list` ("for load_all_and_public").
- `load_list is list` ("after :update_class_template_file/3, class_id is added").
- `temp_list is list`.
- Component `temporary_list` (:1793-1797).

| instance method | arity | summary |
|---|---|---|
| catalogue | 2 | `(UT,Paths)`: generate templates and objects, then push the paths and class ids to the named yank buffers (:1799-1803). |
| catalogue | 3 | `(UT,Paths,Ids)` (:1805-1809) |
| catalogue | 4 | `(UT,Paths,Options,Ids)`. Option `save` saves afterwards. `compile`, `compiled` and `check_subclass` are accepted no-ops (:1811-1816, 2046-2055). |
| register | 3 | `(UT,Paths,Ids)`: reads class names without compiling, then `:register(#library,[Id])`. Prints `class <Id>...`, then `   <Id> end.` or `   <Id> fail.` (:1818-1823, 2124-2133). |
| register | 2 | `(UT,Ids)` (:1825-1827) |
| load | 2 | `(UT,ClassIds)`: rebuild from template files. Prints `Loading <id>...`, or `Remote loading <id>...` when the process library_environment node_name is not `"my_node"`. Each class goes through `:catch(Process,"Skip this class",#library,make_class_template,{Id})`. Errors: `Class <c> template file not found `, `Class <c> not catalogued`, `Load <id> failed.` (:1829-1831, 1967-2012). |
| save | 2 | `(UT,ClassIds)`: `:get_class_descriptor(#library,C,_,_,Id,CD)`; if `:check_info(CD,template)`, prints `Saving <id>...` and runs `:catch(Process,"Skip this class",CD,write_class_template,{})`, then prints ` end.`. Errors: `Class <c> template not found.`, `Class <c> not catalogued.`, `Save <id> failed.` (:1836-1838, 2060-2107). |
| save_changed_classes | 1 | `:get_changed_classes(#library,L)`, then save (:1840-1843). |
| save_non_saved_classes | 1 | Builds the save menu from `simpos##librarian_menu`: `:create_menu_for_save(Obj,Menu)`, `:set_position(Menu,350,250)`, `:activate(Menu,mouse)`, `:read_items(Obj,Menu,Ids,_)`, then saves. Without a window it raises library_error "This system has no librarian window interface!!\nYou cannot use this command." (:1845-1856). |
| get_classes_from_source | 3 | Reads class names per file. Prints `- <path> -` and the id list, or `file <f> not found.`. FDD files are read whole via #fdd_binary_file (:1858-1862, 2139-2192). |
| read_and_get | 5 | (:1864-1867) |
| close_and_get | 4 | (:1864-1867) |
| get_temp_list | 3 | (:1870-1871) |

**Term classes in a source file** (:2239-2263)
- Definitions: `class(...)` and `macro_bank(...)`.
- Applied to the file's operator pool: `add_operator(Op,Type,Pre)`; Op may be a list.
- Accepted: `remove_operator/1,2`, `use_macro/1`, `use_package/1`, `include/1`.
- Anything else is "illegal".

**Catalogue routing** (:2018-2041)
1. `:retrieve(#directory,FileObj,Name,Path)`; on failure print `File <f> not found.`.
2. `:remote_or_local(#pathname,Path,_,_,_,RL)` and `:is_fdd(FileObj)` decide among local_disk,
   local_fdd, remote_disk and remote_fdd.
3. Print `Catalogging "<path>"...` and call `:catalogue_remote_or_fdd`.
4. `:make_all_classes(UT,Ids)`.
5. `define_public_classes` "load_all_and_public" (:1945-1962).

**Yank buffers**: file and class lists are pushed to the `#editor_yank_buffer` named yanks "file"
and "class", unless `:named_yank_flag(#named_yank_buffer_subsystem,off)` (:2293-2313).

#### 4.1.3 librarian_read_term (ds_bep.esp:2331-3121)

**Class methods**
- `make_class_template_from_source/3` (:2341-2349).
- `make_class_template_from_catalogued/4` (:2354-2362).
- `make_class_template_for_auto_catalogue/4` (:2364-2378). Its comment gives the **template file
  path** as `">sys>library>Package_name>template>Class_name.template"` and says "This method is
  added from V5.0 for auto catalogue function".

**Slots**
- Attributes: `response_time_flag`, `process`.
- Components: `version`, `include is list`, `temp is list`, `package_name`, `class_name`
  (:2382-2390).

| instance method | arity | summary |
|---|---|---|
| read_term_and_catalogue | 3 | `(UT,FileOrTermOrList,Ids)`. version = `:now(#date_time,V)`. **Since V6.11 (90/9/20) it also accepts class terms and term lists** (:2398-2400, 2593-2613). |
| catalogue_remote_or_fdd | 5 | local_disk catalogues in place. Remote and FDD files: create `>sys>librarian>esp`, copy the file there with `:copy(#file_utility,[F],[Fxd])`, catalogue it, then delete and expunge. The class becomes "discordant" (:2410-2415, 2553-2564, 3073-3089). |
| catalogue_by_tap | 6 | (:2420-2421, 2638-2648) |
| close_and_abolish | 3 | On error, abolish the classes read so far (:2426-2429). |
| set_operators | 4 | (:2434-2455) |
| special_terms | 4 | (:2460-2461) |
| message 2,4 / messsge 3 (sic) / putl 2,3,4 / response_time 5 / display_response_time 6 | | Dummies "for single use" (:2466-2473). |

**Catalogue algorithm** (:2618-3068)
1. The operator pool is preloaded with `macro_bank fx 1180`, `with_macro xfx 1140`,
   `==> xfx/xf 1099` and `with fx/yfx 1098` (:2618-2628).
2. `include("f")` is resolved against the includer's directory with `:parent_directory`, and is
   read only once. If missing: `file not found :\n   "f"` (:2655-2664).
3. `use_package(P)`: `:check_package(#library,P,P1)` sets the package for **later classes in the
   same file** (:2808-2810).
4. `use_macro(M)` auto-loads macro class M via
   `:make_all_classes(UT,[make_class(M,Cmode,Slist,Smode)],[])` (:2818-2834).
5. A term with functor `register`, e.g. `register(C1,C2,...)`, registers the named classes
   (:2812-2816, 3049-3068).
6. `class Name with_macro M has ...` auto-loads M first (:2835-2856).
7. For each class or macro_bank:
   1. `:expand_definition(MacroObj,Def,Pkg,Name,Exp)`. The default macro class is
      **simpos##esp_macro_expander_for_compiler** (:3040).
   2. Print `   <Name>`.
   3. If the class is new, run `:catalogue_class(#library,'##'(Pkg,Name))`.
   4. If it has an object, `:abolish_class_object`.
   5. `:make_class_template_from_internal_format(#library,Name,Exp,Version)` (:2703-2740,
      2864-2876).
   6. macro_bank terms are preprocessed by `:preprocess(#macro_preprocessor,...)` and made at once
      (:2665-2669).
8. Unless the process's `source_file_mode` is off, `:update_class_source_file(#library,C,File,V)`
   runs (:2989-3006).
9. If check_package replaced the process package, the output window is retitled
   `<libname> ( default: <pkg> )` and `:set_package(Process,New)` is called (:3023-3040).

**Messages**
- `illegal source specification :\n\q`
- `illegal source term specification :\n\q`
- `illegal definition :\n\q`
- `illegal operator definition :\n\q`
- `include file not found:\n   \q`
- `illegal macro definition :\n\q`
- `   copy failed.`

**Inherited API used on UT.** These must come from the missing SIMPOS natures:
- `make_all_classes/2,3`, `add_class_name/2`, `add_class_names/2`, `add_file_name/2`
- `add_discordant_class/2`, `remove_discordant_class/2`
- `get_package_and_class/4`, `term_to_string/3`, `zero_position/4`, `mumble/3`
- `new/2`, `refute/3`
- slots `skipped_classes`, `subclass_check`

**`#library` class methods used** (USAGE; meaning from the code)
- `assign/1`, `abolish/2`, `abolish_class_object/2`, `catalogue_class/2`
- `check_info/3`, as `(Id, template | object | template_file)`
- `check_package/2,3`, `define_public_classes/2`, `get_changed_classes/2`
- `get_class_descriptor/6`, which returns CD. CD in turn takes `:check_info(CD,template)` and
  `write_class_template` through catch.
- `get_class_id/6`, `get_class_id_in_environment/6`, `get_class_id_in_package/6`
- `get_class_object/3`, `get_names/4`, `is_name_only_class/3`
- `make_class_template/2` (through catch), `make_class_template_from_internal_format/4`
- `register/2`, `update_class_source_file/4`
- `make_class_object/2` and `check_class_id/3`. On check_class_id, the cil comment "8 =< Info
  means loaded" (cil/src/ms_cdn.esp:69-74, 286-291).
- `make_package/2` and `change_environment_in_package/3` (cil/src/INSTALL.esp:225-228).

### 4.2 cil: builtin (cil/src/cil_kl0.esp:74) is a copy of the SIMPOS interpreter's KL0 built-in module

- Stamp: `<M-KONDOH.SUBROUTINE>BUILT1.ESP.11, 23-Jul-86 14:33:41, Edit by M-KONDOH` (:43).
- Comment: "This module is for local interpreter to execute kl0 builtin predicates" (:45). The
  predicates that "must be interpreted by interpreter itself" are listed: not, the cut family,
  cut_back_to, level, bind_hook, on_back_track (:45-52).
- The compiler renames are listed too (:55-69).
- This is the same author and era as `<M-KONDOH.LIBRARIAN>`.
- INFERENCE: it is the built-in table of the SIMPOS `interpreter` class used by the debugger.
- The 176 pairs are already in required/builtins.tsv.

### 4.3 cal-esp: the CAL debugger (cal-esp/deb2.12/) derives from the SIMPOS debugger source

**Stamps**
- `<SIMPOS.E.DEBUGGER>SAVE.ESP.3, 14-Apr-87 18:43:47, Edit by M-TAJIMA` (save.esp:10). This DEC-20
  directory is literally named SIMPOS.E.DEBUGGER.
- Then `>sys>user>tajima>new_debugger>SAVE.esp.4` (29-Sep-88) and `>sys>user>tajima>debugger>SAVE.esp.3`
  (20-Oct-88) (save.esp:8-9).
- Also `tajima>debugger>MODIFY.esp.7` (modify.esp:8-9), `tajima>new_debugger>PMOD.esp.4` and
  `deb1>PMOD.esp.6` (pmod.esp:8-10), `tajima>deb2>UTIL.esp.2` (util.esp:8).
- Older still: `<ISHIBASHI.EXEC>UTIL.ESP.62, 20-Mar-86` (util.esp:312),
  `<ISHIBASHI.EXEC>VARS.ESP.39, 10-Feb-86` (util.esp:572), and "ver 3.0 Edit by TAJIMA"
  (util.esp:584).
- The later CAL edits are by machida and cal, 1990-91 (deb.esp:8, kernel.esp:8, cm.esp:8).

**Natures it references but does not define**, i.e. SIMPOS classes:
- as_debugger_goal_input, as_debugger_input_buffer_processing (io.esp:20);
- standard_editor (dedit.esp:19), pmacs_window (dmenu.esp:1240), hash_set (pmod.esp:304);
- with_pmacs_window and the window mixins (windows.esp:10).

| class | file:line | natures | role |
|---|---|---|---|
| cal_debugger | deb.esp:20 | command_interpreter, as_cal_debugger_initiation, as_cal_debugger_entry, as_cal_interpreter_information_processing, as_cal_debugger_kernel, as_debugger_break_processing, save_debugger_state, **as_program** | The debugger program: goal/1, goal_with_abort_situation/1, reset_debugger/1, check_child_debugger/1, get_debug_mode/2. |
| command_interpreter | cm.esp:20 | cal_purs_builtin | The top loop: do_top_loop_of_command_interpreter/2, get_goal_with_situation/2, get_goal_with_cancel_situation/3, interpret_with_situation/3, interpret_with_abort_situation/2, break_to_command_interpreter/4, measure_switch/1,2. |
| as_cal_debugger_entry | entry.esp:17 | - | Box-model port slots: call exit fail redo unify next pick miss proc_call proc_exit proc_fail proc_redo spy_entry tracing debug_mode. Methods: set_gate/3, get_gate/3, set_all_gate/2, set_target/3, get_target/3, set_mode/2, check_trace_mode/1,2. |
| as_gate_menu_processing | gmenu.esp:22 | - | The "Mode_Leash" window: gate_window/2, get_leash/2, set_leash/2, set_mode/3. |
| as_state_menu_processing | stat.esp:23 | - | do_state/3, get_state_switch/4, state_window/2, get_default_package/2. |
| save_debugger_state | save.esp:17 | - | save/1, get_current_state/14, get_current_gate/11, get_current_spy_entry/2, get_current_window_place/5. |
| as_debugger_menu_processing | dmenu.esp:17 | - | Slots inspector, library_utility, string_io. Methods: get_inspector/2, get_library_utility/2, mam_do_menu/2, tracing_menu/4, interrupt_menu/4, to_wb/3, from_wb/4. |
| cal_debugger_io | io.esp:17 | 12 mixins, including the SIMPOS ones above | The windows: debugger_window, trace_pane, variable_menu, control_menu, top_menu, state_window, gate_window, operator_window, string_window, spy_window. |
| debugger_window_parameter | winpar.esp:15 | - | Window classes and labels. |
| cal_purs_builtin | purs.esp:9 | - | The super-command menu. |
| trace_protection_manipulator | pmod.esp:600 | as_program, trace_protector | A second program. |
| as_debugger_io_modifier, as_debugger_pane_modifier | modify.esp:12, pmod.esp:15 | - | Class-level undefined_method/4 and undefined_slot/5 (delegation). |

**Window labels** (winpar.esp:207-227)
- "input_string", "Mode_Leash", "Command window", "Variable", "Debugger Menu", "Input string",
  "To whiteboard", "From whiteboard", "State window", "Operator window", "Place menu".
- The process number is appended to the label (:104-131).

**Pane classes** (winpar.esp:379-460)

| pane | class |
|---|---|
| variable_menu | standard_scrolling_menu |
| child_message | popup_window |
| control_menu | standard_superior_window |
| command_pane | standard_menu |
| top_menu | standard_temporary_multi_select_menu |
| state_window | standard_temporary_choice_window |
| gate_window | standard_temporary_superior_window |
| mode_pane | standard_choice_window |
| gate_pane, target_pane, string_command | standard_multi_column_menu |

**Super-command menu** (purs.esp:975-1021, verbatim item strings)
- Column 1: library_error_mode(off), reset_inspector, get_debugger(DEB), get_io(IO),
  get_inspector(INS), get_vars(V), get_pane(Pane), get_debugger_window(DW),
  get_buffer_op_poop(BP) (sic), trace_deb, trace_user, trace_child, trace_simpos,
  get_op_pool(WP), reset_window, reset_mode, set_prompt("system_mode>"), reset_prompt,
  without_vars_window, with_vars_window, get_trace_info(Info), display_vars, from_wb(WB),
  area_limit_off.
- Column 2: icon, cmenu(off), cmenu(on), heap_on, heap_off, time_on, time_off, redo(on),
  redo(off), package, font, repeat_on, repeat_off, repeat(3), test_11, font_13, kanji_16,
  kanji_28, heap_indicator, help_debugger_indicator, depth(100),length(100), depth(7),length(7),
  system_help.

**Consequence for required/**: requirements.tsv attributes as_program slots and methods such as
!debugger_window, !trace_pane, set_leash/2, get_leash/2, mam_do_menu/2, reset_prompt/1,
select_font_from_menu/2, get_slot/3 and do_state/3. These are **CAL-debugger internals defined in
cal-esp**. The B-scan sent them to as_program because that is cal_debugger's only external nature.
They are not requirements on SIMPOS's as_program (INFERENCE).

---------------------------------------------------------------------------------------------------

## WINDOW (pointer section; window facts that the librarian and shell material shows)

The window system proper is another agent's scope (notes/ifs_window.md). Window facts found here:
- New-window rectangle swept by the user: prose in §1.1 (utter/INSTALL:30-38; gog-esp/INSTALL.e:25). In code, `size(manipulator)`, `position(manipulator)` in `:create(#standard_io_window,[size(manipulator),permission(out),position(manipulator)],W)` (cil/src/ds_bep.esp:3339-3343) and `:create(#pmacs_window,[size(manipulator),position(manipulator)],W)` (:3345-3349). INFERENCE: `manipulator` asks for the sweep.
- Shell commands may open small windows: `:create(#window_without_label,[permission(out),size(100,50),position(0,0)],Win)` (kappa2/kappa2/utility/tool/KSTPR.SHELL:65-67).
- Selector menu: `:instantiate(#selector_menu,{single_select,Title,size(W,H),CommandItems,ObjectItems},Sel)`, `:activate(Sel,mouse)`, `:read(Sel,Code)`; item 4-vector `{String,common,Code,_}` (cil/src/ms_cdn.esp:230-252).
- Librarian save menu from `simpos##librarian_menu`, `:set_position(Menu,350,250)`, `:activate(Menu,mouse)` (cil/src/ds_bep.esp:1845-1856).
- Error popups with `no_select` items: `show_error_message(" !!! Wait !!! ",[{" !!! Now loading !!! ",no_select,_,_}])` (kappa2/kappa2/utility/tool/LOADER.ESP:134-137).
- Abort polling `:read_sense(Window,C)` with codes `mouse#mm`, `control#"c"`, `key#abort` (cil/src/ds_bep.esp:3477-3488).
- CAL debugger window labels and pane classes: §4.3 (cal-esp/deb2.12/winpar.esp:207-227, 379-460).
- Window command interpreter: `:get_interpreter/2`, `:command_interpret/1` (§1.5).

## Measured against the required lists

**required/librarian.tsv (24 rows).**
- Confirmed with a meaning from held code or prose (§1.1, §2.2): the heads menu/0, define/0, package/0, shell_transient/0; items_list/1; the items fxds/1, command/1, make_environment/2, save_environment/1, make_package/2, save_package/1, use_package/1, save_all_classes/0, load/1, refute/1; the inner terms area_limit/1, font/1, ipl_load/3 (now explained, §2.5). The rows `,/2`, `:=/2`, `##/2`, `:/1`, `#/1` are syntax, not commands.
- Held facts NOT in librarian.tsv: `fxd/1` typed at the Librarian Execute prompt (gog-esp/INSTALL.e:50; PROSE) and cil's dispatch of `fxd`, `save/1`, `load/1`, `delete/1` items (cil/src/ds_bep.esp:3381-3411); the shell commands `alias` and `call` (PROSE, §1.3); the menu target `no_select`.

**partition_librarian.tsv (32 classes).**
- library_utility (6 class / 20 instance methods in the B-scan): the held sends are in the TSV; the full instance method list of the cil 6.1 copy (35 rows) is in §4.1.1 and the TSV.
- library (46 class methods): 46 `#library` method/arity pairs are rows in the TSV (§2.4).
- The tier-D natures librarian_version, librarian_delete, librarian_package, librarian_reference, librarian_fdd, librarian_subroutine, librarian_spy, as_assert_utility, librarian_catalogue, as_class_maker, compiler_error_reporter are **all natures of the SIMPOS 6.1 librarian copy** (cil/src/ds_bep.esp:3123, 2331); that is stronger evidence than "one program, unconfirmed": they are the real SIMPOS Librarian's mixins (INFERENCE from provenance, §4.1).
- librarian_io, library_error, macro_preprocessor, fdd_binary_file, esp_operator_pool: used by the same copy (§4.1.1-4.1.3).
- Not in partition_librarian or classes.tsv: `librarian_class_generator`, `librarian_read_term` (defined in cil as SIMPOS copies, §4.1), `librarian_menu` (`simpos##librarian_menu`, ds_bep.esp:1845-1856), `librarian` (the system-menu target).
- esp_macro_expander and esp_macro_expander_for_compiler are both present; the 1990 manual names only the first (§3.4).

**partition_shell.tsv (38 classes).**
- as_program (8 class / 27 instance methods): goal/1, create/2, get_arguments/2, parse_arguments/2 confirmed (§1.4, §1.5). save_arguments/2 is missing (unattributed in requirements.tsv:3353; INFERENCE: as_program). The debugger-ish members (do_state/3, get_leash/2, set_leash/2, mam_do_menu/2, reset_prompt/1, select_font_from_menu/2, with_vars_window/2 ...) are CAL-debugger internals (§4.3). Class goal/2 is kwic's macro-inserted method (§1.5).
- process: create/2,3, self/2, activate/2, get_number/3, get_process/3, exterminate/1, post/1, set_area_limit_execution/7, set_package/2, plus catch/5, throwing_hook/7, the library-environment trio and standard_* (§1.4, §1.5).
- coordinator: the 4 class methods get_instance/2, information/3, login_user/2, whiteboard/2 confirmed by site (§2.4).
- user: login_user/2, user/2, user_list/2. inspector: create/2,3, inspect/2. interpreter: create/3, interpret/2.
- world, user_process_profile: 0 methods in partition_shell; no send in held source either (CHECKED below).
- call_counter (tier M, named in ESP manual TeX): confirmed, program-e.tex:10198-10233 lists `:predicate_output_to_window(#call_counter,list,data)` and siblings in the evaluation section.
- debugger_error, debugger_gate, debugger_recorder, debugger_stop_watch, debugger_error_with_retry, debugger_variable_with_name, as_debugger_goal_input, as_debugger_input_buffer_processing: all used only by cal-esp/deb2.12, which derives from the SIMPOS debugger source (§4.3).
- Not in partition_shell or classes.tsv: the system-menu targets `pmacs`, `file_manipulator`, `librarian`, `shell`, `spooler_manipulator`, `pattern_editor` (USAGE as targets in every held login.com; `debugger` is present).

## CHECKED, NOTHING

- No held class inherits as_interrupt_program, as_trap_program or as_boot_program (B-scan census, §1.4).
- No sends to `world` or `user_process_profile` in any of the 15 held programs (rcv.py), and `grep -rnw` over ifs_simpos finds the words only in COPYRIGHT and sum/MAN prose.
- No definition of `parse_arguments/2` or `save_arguments/2` anywhere in the held source (they are only sent; parse_arguments resolves to as_program, §1.5).
- kappa2/kappa2/utility/CATALOG1.COM and CATALOG2.COM (called by kappa2/kappa2/CATALOG.COM:2,4) are not in the archive.
- euod has no login.com although its README:43 and INSTALL:21 list one.
- The ESP manuals held (overview-e/j, program-e/j, ESPps) contain no login.com syntax, system-menu item list, librarian command list, command-file syntax, shell grammar or debugger command set (grep for librarian, catalog, login, system menu, debugger, inspector, interpreter, use_package). The "SIMPOS programming system" section that the overview promises for volume 3 is absent from the held program-e.tex and program-j.tex: program-j.tex:4247-4248 sets `\setcounter{section}{2}` just before "ESP/SIMPOS programming techniques", i.e. the intermediate section was deliberately left out of this file. program-e.tex has only 21 lines mentioning "window", none a window-system API description (examples in object-orientation and package chapters).
- overview-e.tex:2662-2859 (KL0 built-in predicate categories) skimmed for headings only; out of scope.
- ESPps/*.ps were not read separately: they are PostScript renderings (mtime Aug 1992) of the same two English TeX files; the 'librarian' hit counts (11, 6) are consistent with that. Not compared line by line.

## PAGES READ

No PDF page images were read. Files read by eye, in full unless a range is given:
- Every login.com: disc/login.com, fuzclust/fuzclust/install/login.com, gog-esp/login.com, kappa2/kappa2/login.com, kappa2/kappa2/init/sample/login.com; papyrus_src/demo/EDITOR/icon.com.1.
- Every command file: gog-esp/cgscmp.com; all 33 kappa2 *.COM; kappa2/kappa2/init/ipl.com.
- INSTALL/README (English and Japanese) of all 15 archives (sum, knov, disc, euod, cal-esp, papyrus, fuzclust, icotext, kwic-esp, utter, txtstrct, kappa2, cil, gog-esp, chal).
- cil/src/ds_bep.esp:1773-3518; cil/src/ms_cdn.esp (whole); cil/src/INSTALL.esp (whole); cil/src/cil_kl0.esp:1-120.
- cal-esp/deb2.12 class headers and window/menu definitions (§4.3).
- kwic-esp-002/kwic-esp/src/v2_tool.mac, dtCompiler.esp, dbDM.esp:1-140; kappa2 utility/tool/*.SHELL (CCTPR, KSTPR, LDTPR in full; others headers); kappa2/kappa2/utility/tool/LOADER.ESP:1-200; gog-esp/CGS_INSTALLER.esp:335-382; cal-esp/cal2.12/graph.esp:60-95,174-177.
- ESPtex/overview-e.tex:186-245, 1047-1480, 2040-2075, 2539-2620; ESPtex/program-e.tex:5250-5936 and macro-bank lines 6421, 6976, 7269-7310, 7492, 7636-7733; ESPtex-j/overview-j.tex:199-290, 438, 754, 1135-1139, 1611-1613; ESPtex-j/program-j.tex:5150-5530 (spot-checked against the English).

## OPEN QUESTIONS

1. `fxd` vs `fxds` vs `fdd`: in cil's library_utility `fxd(P)` = catalogue P, but gog's prose types `fxd("cgscmp.com")` at Execute to run a command file. Which did real SIMPOS do? (§2.2)
2. Shell syntax: `{` in `dtc +s { file` (probably stdin redirection, from dtCompiler's help). Option tokens: kwic converts `+(s)` to the two strings "+","s" (sign then name) and kappa LDTPR expects "-","s",NUM, so both agree that the shell splits `-s`; the shell's own tokenizer is not held. Also: is `save_arguments/2` an as_program method?
3. Was cil's command/2 dispatch (`:refute(UT,Name,ArgVector)` per item) the same code that the Librarian `Execute` item runs? cil's copy is a 6.1 patch; 8.x may differ.
4. `:assign(#library)`: what it binds (process library? package?). Used before check_info in kappa LOADER.ESP:162.
5. process create/3 mode list: two variants `[free,free,query,middle]` and `[free,default,free,middle]`; which slot is which (area limits, mode, priority) is INFERENCE only.
6. The `#knov` / `#run_wkm` menu-target form in sum/knov prose (SIMPOS 3-5) vs bare atoms in later login.com: older syntax or same meaning?
7. Default macro bank: manual (1990) says `esp_macro_expander`; cil's 6.1 librarian copy uses `simpos##esp_macro_expander_for_compiler`. Different objects or a compiler-side wrapper?
8. Volume 2 (Operations) of the SIMPOS manual set is not held; it is where the librarian, shell and system-menu operations are documented.
