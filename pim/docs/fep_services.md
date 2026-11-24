# The FEP services as PIMOS's source defines them (2026-11-24)

A catalogue of the front-end protocol read from the held PIMOS 3.6
source, so that the next answers of the stand-in `ref/pimm/fep.py`
(OURS) are sourced, not found one stop at a time. Research only:
nothing here was run on a model. The packet and SCSI levels are in
`binary_reverse_engineering.md` §1.4 and are not repeated.

**Sources and how they were read.**

- PIMOS side: `docs/nonlocal/pimos.tar.Z`, paths below relative to its
  `pimos/src/` (EUC-JP; `gzip -dc pimos.tar.Z | tar xf -`). READ.
  The line numbers are of the files as extracted.
- Shipped configuration: `docs/nonlocal/pimosobj.tar.Z`, `object/`
  (`pimos.conf`, `pimos.logins`, `pimos.groups`, `shell.com`,
  `pimos.com`, `login.com`, `init.com`, `pimos.ipl`): two-byte JIS
  X 0208 with no escape sequences; decoded by prefixing `ESC $ B` and
  decoding ISO-2022-JP. READ.
- PSI side: `python3 asm/ptfdump.py pimfep fep_command_code_table
  --pairs` (the FEP's code/name table, re-run for this document) and
  `python3 asm/ptfdump.py pimfep [CLASS]` (class and method lists).
  Compiled ESP: names, arities and literals only; no method body was
  read, so **no argument or reply layout is confirmed by the PSI side.**
- Manual: `docs/nonlocal/pimosman.tar.Z`, `Eman/*.tex`.

**Caveat on the object.** The held boot loads twelve patch files after
the eight system files (`object/pimos.ipl`), among them
`pimm_patch_scsifep360E.sav`, `pimm_patch_fepsv360E.sav`,
`pimm_patch_mkdir360E.sav`, `pimm_patch_tel360E.sav`. Their source is
not held (`binary_reverse_engineering.md` §2), so where a patch
replaces a module below, the object may differ from this reading.
The build switches (`fep_interface`, `machine`, `autoloading`,
`virtual_machine_interface`) of the held object are not known from
the source; the run settles each.

Marks: **P** sourced from the PIMOS source; **C** the name and number
also stand in the PSI's `fep_command_code_table`; **U** unknown.

## 1. The layers on the PIMOS side

1. `bios/fep_module/scsi_fep.kl1`: packets. Device ids from 16
   (line 23). An integer argument is sent with length word -1, a
   16-bit string as its bytes (length 2 x characters), an 8-bit
   string as it is (`check_data_size1/6`, 429-445). A received string
   is left 8-bit; the device modules widen the ones they want 16-bit
   with `fep_utility:str8_to_str16/2` (`fep_util.kl1`:81-86). A reply
   whose status is 3 becomes `{Id, attention}` (573-577); status 11
   (`fep#end`) ends the receiver (544-548). `{-1, 80}`
   (`fep#terminate`) is sent when the link's stream closes (234).
2. `bios/fep_module/fep_dvc.kl1`: the general request. A user of the
   BIOS asks for `fep#window`, `file`, `timer`, `string_io`, `socket`
   (and `remote_*` with a node name); none of these reaches the wire,
   each starts a request device with Node = `""`, or the node name
   (`request_device_io0/5`).
3. `bios/fep_module/{file,dir,win,time,strio,soc}_dvc.kl1`: **the only
   place wire messages are made**, as `send({DevID, Command, Args...},
   Result)` with the reply template `{DevID, Status, Vars...}`.
   `*Rdvc.kl1` give out device ids. Section 2 is this layer, complete
   (every `send({` outside comments, by script).
4. `server/fep/*`: the servers user tasks talk to (protection, code
   conversion, buffering); they drive layer 3 and add no command.
   `bios/boot/{syslog,timer,sysTman,console}.kl1` are the kernel's own
   early users of layer 2.

**The reply rule** (`fep_util.kl1` `set_value/2`, 19-44): a reply is
taken as normal only if its device id matches, its status is 1 and it
has **exactly as many elements as the template**; then the values are
bound. Otherwise the caller gets the reply's status and every result
is set to 0 (`fep#nil`). So an abnormal reply needs only `{Id, St}`;
its further elements are not looked at. A failed SCSI send gives
status 5 locally (`device_abnormal/1`, 70-73).

**Statuses** (`macro/pimos/pimos/pimos.vmac`:19-23, 144, 150; all C):
0 nil, 1 normal, 2 eod, 3 control_c = attention, 4 continue, 5
abnormal, 6 aborted, 7 yes, 8 no, 9 wake_up, 10 disconnected, 11 end.
Status 10 in any reply marks the device's FEP line as gone
(`fep_rcvr.kl1`:81-84, 105-112): every later request on it is answered
`disconnected` locally. `continue` (4) has no user in `bios/`,
`server/`, `kernel/` (grep).

## 2. The commands PIMOS can put on the wire: 63

Request = `{Id, Code, args}`; reply = `{Id, Status, results}`. "s" a
string, "i" an integer. All rows are P for number, layout and reply,
and C for name and number (checked row by row, 2026-11-24: each of
the 63 codes stands in the `--pairs` output under the same name, as do
807-809 and the statuses 0-11); the layouts are P only.

### 2.1 Every device

| Code | Name | Sent at | Args | Reply PIMOS takes |
|---|---|---|---|---|
| 60 | close | every `*_dvc.kl1`, when the device's stream ends (e.g. `file_dvc.kl1`:189, 283, 355; `time_dvc.kl1`:197, 315, 414) | none | `{Id, St}` (`device_terminate`) |
| 70 | abort | every `*_dvc.kl1`, when the abort line is bound (e.g. `file_dvc.kl1`:258, 524) | none | U: only the send's own result is waited for (`device_abort0`, `file_dvc.kl1`:552-560); whether a reply is expected was not traced. The IPL's client expects none (§1.4) |
| 80 | terminate | `scsi_fep.kl1`:234, device id -1 | none | none read |

### 2.2 File (`bios/fep_module/file_dvc.kl1`)

| Code | Name | Line | Args | Normal reply |
|---|---|---|---|---|
| 201 | read_open | 23 | Node s, User, Password, Path s | `{Id, 1}` |
| 202 | write_open | 31 | same | `{Id, 1}` |
| 203 | append_open | 39 | same | `{Id, 1}` |
| 240 | fep_attributes | 50 (written as the number, the macro commented out, 44-49) | Node s | `{Id, 1, Code i, OS s, Host s, FepVer s, Dir s, FileVer s, Comment s}` (51-52); the device ends with the reply, no close |
| 210 | getb | 299 | Size i | `{Id, 1, String}`; status 2 at the end of data |
| 220 | end_of_file | 304 | none | `{Id, 1, EOF}`, EOF 7 (yes) or 8 (no) (`server/fep/file/file_dvcb.kl1`:595-596) |
| 111 | putb | 309 | String s | `{Id, 1}` |
| 112 | flush | 314 | none | `{Id, 1}` |
| 221 | pathname | 319 | none | `{Id, 1, Pathname s}` |
| 222 | attributes | 324 | none | `{Id, 1, Attributes}` |

- User and Password are 0 for the kernel's own opens
  (`bios/boot/syslog.kl1`:33) and for system tasks; for a logged-in
  remote user they are the strings of the login request (section 3).
- **240 must be answered before any open through the file server.**
  The first request of an I/O node asks it once and keeps the answer
  (`server/fep/fep/fep_sv.kl1`:545-551, 597-615, 630-635). Code picks
  the path conversion: 0 = the path's 16-bit JIS as bytes, 1 = EUC,
  **any other value makes every open abnormal**
  (`server/fep/file/fileRdvc.kl1` `convert_upn/8`, 654-674); the six
  strings are widened (0) or converted from EUC (1) (541-558). The
  codes are `fep#jiskanji` 0, `euc` 1, `jis` 2, `sjis` 3
  (`pimos.vmac`:159-162, C). What the PSI answered is not held (U1).
- `getb` through the file server asks for bytes: `Size*2+1` for a
  16-bit read (`file_dvcb.kl1`, §1.4 "the unit of 7936").

### 2.3 Directory (`bios/fep_module/dir_dvc.kl1`)

| Code | Name | Line | Args | Normal reply |
|---|---|---|---|---|
| 204 | directory | 24 | Node s, User, Password, Path s | `{Id, 1}` |
| 205 | make_directory | 34 (as the number) | same | `{Id, 1}` |
| 221 | pathname | 249 | none | `{Id, 1, Pathname s}` |
| 237 | listing_all | 254 | Wildcard s | `{Id, 1, File_names}` |
| 231 | delete | 259 | Wildcard s | `{Id, 1}` |
| 239 | kill | 266 (as the number) | Wildcard s | `{Id, 1}` |
| 232 | undelete | 271 | Wildcard s | `{Id, 1}` |
| 238 | deleted_all | 276 | Wildcard s | `{Id, 1, File_names}` |
| 233 | purge | 281 | Wildcard s | `{Id, 1}` |
| 235 | expunge | 286 | none | `{Id, 1}` |

The form of `File_names` (one string; its separator) was not read (U7).

### 2.4 Timer (`bios/fep_module/time_dvc.kl1`)

| Code | Name | Line | Args | Normal reply |
|---|---|---|---|---|
| 310 | create_timer | 34, 774 | Node s, User, Password | `{Id, 1}` |
| 301 | get_count | 336 | none | `{Id, 1, Count i}` |
| 302 | on_at | 347 | Count i | `{Id, 1, Now}` when the time comes |
| 303 | on_after | 361 | Count i | `{Id, 1, Now}` when the time comes |
| 304 | get_date_time | 371 | none | `{Id, 1, Date i, Time i}` |

- `on_at`/`on_after` use the device up: the stream's rest goes to a
  **new** timer device (a new id and another 310, lines 342-367), and
  the old one is closed (60) once its reply has come.
- The reply's third element is what the waiter gets: 9 (`wake_up`)
  is the alarm; 6 or 0 reads as aborted (`server/fep/timer/
  time_dvc.kl1`:254-257). By the reply rule a status other than 1
  gives 0, so an alarm is `{Id, 1, 9}`.
- Date is days from 01-Jan-1901 and Time milliseconds from midnight
  (§1.4 row 13-14); Count is milliseconds (`time_dvc.kl1`:241-248,
  `trans(msec(N), ..)`).

### 2.5 String I/O (`bios/fep_module/strio_dvc.kl1`)

| Code | Name | Line | Args | Normal reply |
|---|---|---|---|---|
| 601 | create_string_io | 22 | Node s, User, Password, Name s | `{Id, 1}` |
| 620 | io | 223 | Command i, To_fep s | `{Id, 1, From_fep s}` (widened to 16 bits, 224) |

Name selects a program on the FEP. The three names PIMOS uses in its
start, `"simpos_user_device"`, `"pimos_remote_login_replier"`,
`"pimos_remote_login_server"` (section 3), are each the name of a
class in `pimfep.ptf` with an instance method `io/4` (`ptfdump.py
pimfep`: MEASURED). That 601 makes an object of the class named is an
INFERENCE from `pimos_string_io_invoker`'s `create_string_io/10` and
its local `get_class_object/3`; the code was not read.

### 2.6 Window (`bios/fep_module/win_dvc.kl1`)

| Code | Name | Line | Args | Normal reply |
|---|---|---|---|---|
| 104 | create_window | 22 | Node s, User, Password | `{Id, 1}` |
| 102 | create_with_buffer | 30 | Node s, User, Password, Buffer s | `{Id, 1}` |
| 103 | get_max_size | 37, 44 | Node s, [User, Password,] X, Y, Font path s | `{Id, 1, Char, Lines}`; no device stays |
| 110 | getl | 309 | none | `{Id, 1, Line s}` (widened) |
| 111 | putb | 315 | String s | `{Id, 1}` |
| 112 | flush | 320 | none | `{Id, 1}` |
| 113 | beep | 325 | none | `{Id, 1}` |
| 114 | ungetb | 437 | String s | `{Id, 1}` |
| 121 | set_inside_size | 330 | Char, Lines | `{Id, 1}` |
| 120 | set_size | 336 | none | `{Id, 1}` |
| 124 | set_position | 341 | X, Y | `{Id, 1}` |
| 123 | set_position_by_mouse | 347 | none | `{Id, 1}` |
| 127 | reshape | 353 | X, Y, Char, Lines | `{Id, 1}` |
| 126 | reshape_by_mouse | 359 | none | `{Id, 1}` |
| 130 | set_title | 365 | String s | `{Id, 1}` |
| 132 | set_font | 371 | Font path s | `{Id, 1}` |
| 140 | select_buffer | 377 | Buffer name s | `{Id, 1}` |
| 146 | buffer_name | 383 | none | `{Id, 1, Name s}` |
| 141, 142 | activate, deactivate | 389, 394 | none | `{Id, 1}` |
| 143, 144, 145 | show, hide, clear | 399, 404, 409 | none | `{Id, 1}` |
| 122 | get_inside_size | 414 | none | `{Id, 1, Char, Lines}` |
| 125 | get_position | 420 | none | `{Id, 1, X, Y}` |
| 131 | get_title | 425 | none | `{Id, 1, String s}` |
| 133 | get_font | 431 | none | `{Id, 1, Font path s}` |

- Interrupt: a reply `{Id, 3}` at any time is the window's attention
  (control-C), not an answer; one more reply is then still owed
  (`scsi_fep.kl1`:573-577, `fep_rcvr.kl1`:75-80).
- PSI side: the hash keys of `pimos_standard_io_window` are 104, 60,
  130, 124, 121, 141, 142, 111, 110, 112, 145
  (`binary_reverse_engineering.md` §4.3). 127, 132 and 143, which the
  login console sends first (section 3 step 15), are not among them;
  where the PSI handles them was not found (U4).

### 2.7 Socket (`bios/fep_module/soc_dvc.kl1`)

| Code | Name | Line | Args | Normal reply |
|---|---|---|---|---|
| 801 | create_socket | 24 | Node s, User, Password | `{Id, 1}` |
| 802 | bind | 265 | Address | `{Id, 1}` |
| 803 | listen | 271 | Backlog i | `{Id, 1}` |
| 804 | accept | 380 | NewDevID i (PIMOS picks the new socket's id) | `{Id, 1, Address s}` |
| 805 | connect | 283 | Address | `{Id, 1}` |
| 812 | connect_hostname | 291 | Port, Address | `{Id, 1}` |
| 806 | set_socket_option | 298, 305, 312 | one to three of 807 so_debug, 808 so_reuseaddr, 809 so_keepalive (`server/fep/socket/soc_dvc.kl1`:643-650) | `{Id, 1}` |
| 210 | getb | 319 | Size i | `{Id, 1, String, ReturnSize i}` |
| 111 | putb | 327 | String s, Size i | `{Id, 1}` |
| 810, 811 | send_timeout, receive_timeout | 333, 339 | Time i | `{Id, 1}` |
| 112 | flush | 345 | none | `{Id, 1}` |

### 2.8 Names with a number that are never sent

- Stream-level tags, used between PIMOS processes only: 50 reset, 51
  next_attention, 100 window, 101 create (becomes 310 or 601), 200
  file, 300 timer, 600 string_io, 700-704 remote_*, 800 socket
  (`fep_dvc.kl1`). P. Of these 100 and 704 are not in the PSI's table.
- No sender in the held source (grep of `bios/`, `server/`,
  `kernel/`): 230 listing, 234 deleted, 236 next_filename, 400 ipl,
  500 symbol, 710 node_name. 230, 234, 236 and 500 are not in the
  PSI's table either.
- PSI only (`fep_command_code_table`): 900 creation_fail, 901
  all_device_end, 902 remote_echo_check, 903 device_end. PIMOS has no
  name for them; whether the PSI ever sends them to PIMOS is U5.

## 3. The start, from the banner to a shell

KL1 is concurrent: an order is given only where a stream or a wait
enforces it. "Wire" is what the FEP sees. Ids are given out from 16
in order of creation, so the numbers shift with the order.

**A. BIOS** (`bios/boot/bios.kl1`:41-61 the banner and `init:go`,
388-396 `create_os_device1/2`: console, system timer, syslog)

1. Banner (no wire); the bus scan (§1.4, done).
2. Console: a dummy, every `putb`/`getl` answered abnormal locally,
   **no wire** (`bios/boot/console.kl1`:12-33). So `display_console`
   text goes to the machine's console built-in, not to the FEP.
3. System timer: if `set_timer` gives an integer, alarms are local
   and nothing is sent (`bios/boot/sysTman.kl1`:28-33); if not,
   `timer:create` sends 310 and every alarm is a 303 (34-35,
   `bios/boot/timer.kl1`:30, 60-62). The run takes the first branch
   (§1.4 stop table, `system_timer`/`set_timer` implemented).
4. Syslog: **wire 203** `{Id, 203, "", 0, 0, "pimos:pimos.syslog"}`
   (`bios/boot/syslog.kl1`:33). Done. Afterwards only `putb(Buffer)`
   becomes **111** on that device (86-89); the only users found are
   forwarders (`kernel/init/init.kl1`:300-302,
   `kernel/task/raisehdl.kl1`:69-73), so a 111 comes when a task
   writes to the syslog, not at a fixed point of the start. This is a
   negative from a grep for `syslog` in `kernel/`, `server/`,
   `shell/`, `utility/`, `library/`, and it narrows §1.4's "then
   `putb` (111)", which reads the device, not a writer.

**B. The servers**, in this order, chained by an `ok` variable from
each to the next (`kernel/init/init.kl1`:58-73, `start_top`; that each
waits for the one before is the reading of that chain, not traced
into every server): SCSI Server (if
`fep_interface` is `scsi`), Fep, Atom, Module, User, Pipe, Profiling,
User Server Manager (`kernel/init/rsc_init.kl1`:26-47).

5. Fep Server registers its five requests and starts the timer
   server (`server/fep/fep/fep_sv.kl1`:31-75): no wire of its own.
   The timer server: **wire 310** `{Id, 310, "", 0, 0}`, then **304**,
   once, to set the offset between the FEP's date and the machine's
   clock (`server/fep/fep/time_sv.kl1`:13-70). Done; this is where
   the run stands (`subtract_bignum`, §1.4). Then the device's stream
   ends: **60** on the timer (INFERENCE from `time_sv.kl1`:55, the
   stream is closed with the one request).
6. Module Server: **201** `"pimos:autoload.tbl"` unless built with
   `autoloading` = `no` (`server/module/autoload.kl1`:19-29). The
   file is not in `pimosobj.tar.Z`, whose `object/INSTALL` (lines
   8-9) says to copy `object/*` to `pimos:`, so an installation as
   shipped has none. A failed open is taken in silence (`init_1/4`'s
   last clause, 39-41); only an unreadable term gives "Error on read"
   (50-52, 58-60). Which build the object is: the run.
7. The first open through the file server asks **240** first, on a
   device of its own (section 2.2). So 240 comes before the 201 of
   step 6 or, without it, of step 8.
8. User Server starts the "Login Server" task
   (`server/user/user_sv.kl1`:29-32). User Server Manager: **201**
   `"pimos:pimos.conf"` (`server/login/init/usersvman.kl1`:36-38; the
   `vm` build has another path, 31-33), read term by term (210 until
   status 2, then 60), running each `system(Fep, Node, Name, Mod:Goal)`
   (120). The held `pimos.conf` has two live lines: `with_console.`
   and `system(0,0,"login",login:go([{0,local,0},{0,tcpip,0}],[],off)).`
   A failed open prints "pimos.conf Not exit" (59).
9. `login:go`: **201** `"pimos:pimos.logins"` and **201**
   `"pimos:pimos.groups"` on one file request
   (`server/login/login/login.kl1`:460-463), both held. The third
   argument `off`: no log file.

**C. Login service** (per FEP, `login.kl1`:826-833), all string I/O:

10. **601** Name `"pimos_remote_login_replier"`, then **620**
    `io(0, "")` (869-880).
11. For each LAN of the `pimos.conf` line: **601** Name
    `"pimos_remote_login_server"`, then **620** `io(0, "local")`
    (and another device with `io(0, "tcpip")`) (936-960). On a normal
    reply the console gets "LOCAL  LOGIN SERVICE STARTS ***" and the
    FEP number, and **620** `io(1, "  ")` is sent (966-970). **That
    request stays unanswered until someone logs in.** The manual's
    boot log ends the same way (`Eman/e-sysman.tex`:104-112).

    A "login prompt" is therefore not something PIMOS prints.
    The dialogue is the PSI's: "Login PIMOS" in the SIMPOS menu
    (`Eman/e-login.tex`:34-48; `login.com`'s menu entry is
    `pimfep##pimos_login_requester`). PIMOS waits.

**D. A login** (the FEP's move)

12. The FEP answers the pending `io(1)` with `{Id, 1, NI}`. NI's
    elements 0-5 are the request's ID and the lengths of Node, RN,
    RP, UN, UP; the five strings follow; Node `"local"` means this
    FEP (`login.kl1` `get_node_info/3`, 1244-1258; UN, UP the PIMOS
    user and password, RN, RP the FEP's). The unit of an element (the
    reply is widened to 16 bits) is P; what the real requester puts
    there is U2.
13. PIMOS: replier **620** `io(1, [ID] ++ "Login procedure starts.")`;
    the server device re-armed with **620** `io(1, " ")`
    (1005-1012).
14. **201** `"me:pimos.init"` for the console window's place, as the
    remote user RN/RP (1013, 1093-1096). With RN, RP strings the Fep
    server first confirms them: **601** Name `"simpos_user_device"`,
    **620** `io(0, [len(Name), len(Pass)] ++ Name ++ Pass)`, normal
    reply `{Id, 1, Dir}` (`server/fep/fep/confirm.kl1`:23-33, 301-323;
    `conf_dvc.kl1`:43, 67, 79-91). If the open fails the window is
    `"PIMOS CONSOLE"`, at (200,200), 47 x 14 characters, font
    `"font:test_11.font"` (1104-1106, 1169-1173). We hold no
    `pimos.init`, and the shipped set has none (`object/INSTALL`
    puts only `init.com` and `login.com` in `me:`); the manual
    describes its `console_window(Pos, Size, Font).` term
    (`Eman/e-login.tex`:130).
15. The task "login" with that window as its standard I/O: **104**,
    then **127** reshape, **130** set_title, **132** set_font,
    **143** show (`kernel/stdio/s-server.kl1`:262-271, 289-292).
16. After the user and password are checked against `pimos.logins`:
    replier **620** `io(1, "OK. Your initial program starts.")`,
    `io(1, "Good luck!")`, `io(2, [ID])`; on failure
    `io(1, "Login incorrect")`, `io(2, [ID])` (1075-1090).
17. The entry's program runs; for every user of the held
    `pimos.logins` (`super-pimos`, `pimos`, `pmpsi`, `me`, `kiyo`) it
    is `pimos:: shell: login`. The shell takes `home("shell.com")`
    then `home("pimos.com")` (**201** each, absent ones skipped;
    `shell/main/shell.kl1`:283-286), then its loop: prompt, **112**
    flush, **110** getl (354-356), output as **111**. Default prompt
    `"Shell>> "` (330); the held `shell.com` sets its own. The held
    `pimos.com` opens a second shell and a listener in windows of
    their own (104 and the rest again).

**What the source dictates, and what will be OURS.**

| Dictated by the PIMOS source | OURS, until the PSI side runs (P5) |
|---|---|
| Every request's code, arguments and order within a stream; the reply's element count; the statuses | Whether each request succeeds, and every reply's values |
| The file names opened and their modes | The mapping of `pimos:` and `me:` to host files; the contents of `autoload.tbl` and `pimos.init` (not held; the held `pimos.conf`, `.logins`, `.groups`, `shell.com`, `pimos.com` are period files and can be served as they are) |
| 240's reply shape and that Code must be 0 or 1 | The seven values |
| The three string-I/O names, the commands 0, 1, 2 and the layout of NI | The replies to `io(0, ..)`; when a login arrives and with which names; what the replier's texts are shown on |
| The window calls and their parameters | What a window is: where `putb` text goes, where a `getl` line comes from, echo and line editing |
| The date and time units | The clock |

**A minimal honest FEP for R6.** R6 is "Login and a shell prompt; a
shell command that only needs the kernel runs" (`pimos_roadmap.md`
§2), so it needs all of A-D. In order: 203 (done); 310, 304 (done),
60 on a timer; 240; 201 of `pimos:autoload.tbl` answered 5 (if the
build asks; the shipped set has no such file); 201/210/60 for
`pimos.conf`, `pimos.logins`, `pimos.groups`; 601 and 620 command 0
for the replier and the server; then `io(1)` held. **Waypoint:** the
console shows the two LOGIN SERVICE lines, the end of the manual's
boot log; everything up to here is PIMOS's move and can be checked
against that log. Then OURS begins in earnest: a scripted login (an
NI answering the held `io(1)`), 620 commands 1 and 2 on the replier,
`simpos_user_device` (or a login with RN = RP = 0, U3), status 5 for
`me:pimos.init`, 104/127/130/132/143, 201 of the home directory's
`shell.com` and `pimos.com`, then 111/112/110 with the lines of a
script.

## 4. `fep.py` against the source

Agrees:

- 201 and 203 take four arguments and answer `[1]`; 5 for a missing
  file (the reply rule: `{Id, 5}` is enough).
- 310 with three arguments, `[1]`; 304 with `[1, Date, Time]`, the
  element count the template wants.
- 210 `[1, bytes]`, then `[2]` for as long as it is asked; bytes as
  the unit.
- A message is answered only when its last packet has come.

Weaker than the source allows, or to check:

- 60 is answered only for a device opened with 201. The source
  closes every device (a timer after step 5, the appended syslog at
  shutdown, each window). (The other agent has since added a timer
  close; not in this tree.)
- 70 is given no reply for any device. Right for the IPL's client;
  for the kernel's it is U6.
- 80 with device id -1 raises `FepError`.
- No reply is ever unsolicited: no attention (`{Id, 3}`), no deferred
  reply (303's alarm, the pending `io(1)`). The reply queue is one
  FIFO, which is enough, but a reply must be able to stay owed while
  later requests on other devices are answered.
- The device kinds are kept in separate tables (`files`, `appending`,
  `timers`); 111/112/221/222 on a file opened by 202 or 203 are not
  served, though the syslog can send 111 at any time.
- `MAX_BUFFER` 16,000 where the kernel's link uses 16,384 from
  `scsi_manager` (§1.4 item 2): not the FEP's affair, noted there.

Missing, in the order the start will ask (section 3): 60 on a timer;
240; a mapping of `pimos:NAME` to the held `object/` files in the
caller's `open_file` (an absent file already gets 5); 601; 620 with
commands 0, 1, 2 and a reply that can be withheld; 111 on the syslog;
then for a shell 104, 127, 130, 132, 143, 111, 112, 110 on a window,
and 60 on each. Not needed for R6 or a first shell: directory,
socket, 102, 103, 301-303 (unless the BIOS timer takes the FEP
branch), the other window calls.

## 5. Named unknowns

| | Unknown | What would settle it |
|---|---|---|
| U1 | The PSI's answer to 240 (Code, OS, Host, FepVer, Dir, FileVer, Comment). FepVer may be the "V0.45" of `pimos_scsi_front_end` (§1.4): INFERENCE | Decoding `pimfep.ptf`'s handler for key 240 in `pimos_scsi_front_end:command_type/2` (the KL0 disassembler of §4.4), or running `pimfep` under SIMPOS (P5). Until then Code 0 is the choice with a reason: the PSI's own code is 16-bit JIS |
| U2 | The exact NI the PSI's login requester sends (ID's range, whether strings are JIS, a null RN/RP for a local login) | `pimos_remote_login_server`'s `check_message/6` and `as_pimos_login_requester` in `pimfep.ptf`, decoded; or P5 |
| U3 | The replies to `io(0, "")`, `io(0, "local")` (only the status is used by PIMOS, `login.kl1`:966) and `simpos_user_device`'s Dir | The same classes' `io/4` |
| U4 | Where the PSI handles 127, 132, 143 (not keys of `pimos_standard_io_window`) | `ptfdump.py pimfep pimos_window`, `pimos_window_process`, `pimos_window_editor` hash keys |
| U5 | Whether the PSI sends 900-903 to PIMOS, and what PIMOS's receiver does with a status it has no clause for (a reply of status 900 would go through `set_value/2`'s second clause as that status) | The senders in `pimfep_message_sender`; on our side a test with the reference model |
| U6 | **Settled on the PIMOS side (READ, 2026-11-24; §7.1).** 70 gets no reply of its own, in all six device modules. Idle device: `{Id, 70}` is sent and only the send's result is taken (`file_dvc.kl1`:256-260, 552-556); no `receive` is queued. Request outstanding: its `receive(Vars, Result)` is already queued (493-498); `{Id, 70}` is sent and `device_abort1` waits for the send's result **and** the outstanding request's reply (521-525, 578-582). So the FEP owes exactly one reply, that of the interrupted request, with any status (6, `aborted`, gives the caller 6 and zeros by the reply rule); a second packet would be taken as the answer to the device's next request (`fep_rcvr.kl1`:86-92, replies are matched in order). After either the device answers every request `aborted` locally until a `reset` (`device_aborted`, 352-406) | Open on the PSI side only: what status the real FEP gives the interrupted request (`abort_timer`, `device_abort/1` in `pimfep.ptf`) |
| U7 | **Settled on the PIMOS side (READ; §7.1).** Both are ONE string, widened to 16 bits for Code 0 (EUC to JIS for 1), cut at elements of value 10 (LF). `File_names` (237, 238): each name up to an LF; the last may end with the string instead (`server/fep/file/dir_dvc.kl1`:304-339); the result is a list of 16-bit strings. `Attributes` (222): nine fields, the first six strings (Owner, UpdateUser, CDate, CTime, MDate, MTime), then three decimal integers in JIS digits (LinkCnt, FSize, RSize), **every integer field ended by an LF** (the digits are counted to one before the cut, `file_dvcb.kl1`:598-651, 668-691); taken only if 240's OS string begins `"SIMPOS"` (or Code is 1, the UNIX reading), otherwise abnormal (557-576). The object's modules agree with this source in clause counts and integers (`dir_device`, `file_request_device`, `fep_directory_device` are the `mkdir` patch's; §7.1) | The PSI's side (`pimos_directory`, `pimos_file`), not decoded; the date and time strings' format, which PIMOS passes through unread |
| U8 | **Settled to the depth of §7.1** (`python3 asm/fep_services/savpreds.py`). (a) The patch modules ARE the held source: `scsi_fep` differs from its base in `send_packet2/10` and `send_packet3/10` alone, exactly the source's "Remake by Amanuma" (the rounding of a string's length moved, `copy_string_elements` for `substring`: a string argument cut across packets); `fep_server` gains an abort line through the 240 fetch (8 predicates added, 5 dropped, 2 changed); neither changes a code, a layout or the order of commands. (b) The object is built with `fep_interface` = `scsi`, `virtual_machine_interface` not `yes`, `machine` not `vm` (and `mpsi`/`pimm` in the timer), `machine_type` = `mpsi`, `ipl_parameter` = `yes`, `autoloading` not `no`: it asks for `pimos:autoload.tbl`. tcpip, telnet and remote login are not build switches but `pimos.conf` terms | Instruction-level equality with the source was not shown (no compiler is run): the measure is predicate names, clause counts, integers, atoms and the module's constants. `pimos.h`, which sets the switches, is not held |
| U9 | **Settled by reading (§7.3); one link INFERENCE.** The login shell's standard I/O is the "PIMOS CONSOLE" window of step 15: the user's task is made with no `stdio` option (`login_sv.kl1`:1536-1541) and `login_p:top` sets `task:top_task` (`login_p.kl1`:94), which makes `shell:login` use its standard I/O and not a new window (`shell/main/shell.kl1`:101-110). That the task inherits the "login" task's window is INFERENCE (the request handler between them was not traced). No partition dialogue with the held files: `login:go(.., [], off)` has no partition list (`login.kl1`:204-207 makes it `none`), the login server answers `get_part_info` with `[]` (`login_sv.kl1`:961-964), so `login_p:go2` takes its `[]` clause (`login_p.kl1`:29-34); "Enter your partition ?" needs a non-empty list and a `k` at "Confirm(<return> or kill): " (275-277, 485-488), on the task's `inter` window (24) | The run. Not traced: whether the stdio switch sends 141/142, and the wire effect of the login server's `get_date_time` |
| U10 | **Settled (§7.2).** `pimos:` is the SIMPOS directory `>sys>csp>PIMOS.DIR` (`object/login.com`) holding `object/*` (`object/INSTALL`:8): serve `pimos:NAME` from `pimosobj.tar.Z` `object/NAME`. `me:` is `user:pmpsi` and holds only `init.com` and `login.com` (INSTALL:9), which PIMOS never opens: `me:pimos.init` is absent, status 5. A third name space was missed: the shell's `shell.com` and `pimos.com` are opened in the HOME directory the FEP's `simpos_user_device` gives, not in `pimos:` | Nothing for a stand-in. What a real user's home held is not knowable from the held set |

In rows U6-U10 the second column is now the result and the third what
stays open (2026-11-24).

## 7. A login the stand-in can originate

Research and design only: nothing here was run on a model, and no
model file was changed. READ = seen in the held source at the lines
given; MEASURED = a number of `asm/fep_services/savpreds.py`;
INFERENCE and OURS are marked. Paths are under `pimos/src/` as before.

### 7.1 U6-U8: the evidence

**Abort (U6).** The same code stands in all six device modules
(`file`, `dir`, `win`, `time`, `strio`, `soc` `_dvc.kl1`; grep of
`fep#abort` and `device_abort0/1`). For the pending login request the
lines are `bios/fep_module/strio_dvc.kl1`:180-184 (idle), 351-356 (the
`receive` queued once the send has gone), 379-384 (abort with a request
outstanding), 437-441 (`device_abort1(normal, normal, ..)`: both the
abort's send and the request's reply). The sequences:

| Case | PIMOS sends | The FEP owes |
|---|---|---|
| abort, nothing outstanding | `{Id, 70}` | nothing |
| abort, request R outstanding | R, then `{Id, 70}` | one reply, R's: `{Id, St, ..}`. Any status; with St other than 1 only `{Id, St}` is looked at. Nothing for the 70 |
| afterwards | nothing until the user's `reset`; every request is answered 6 locally | nothing |

If the FEP never answers R the device hangs in `device_abort1`: there
is no timeout.

**The probe (U8).** `python3 asm/fep_services/savpreds.py --check`
(PASS; about two seconds; reads `docs/nonlocal/pimosobj.tar.Z` and
`pimos.tar.Z`, writes nothing). It cuts each module of the 20 `.sav`
files into predicates and takes, per predicate, the instruction names
in order, the atoms, integers and hash-table keys, and the number of
`proceed`/`execute` instructions (one per clause body); per module, the
structured constants and external calls. Proved on three known
answers: `kl1_library_variable_pool`, whose 68 predicates are the same
in base and patch; `fep_server`, 8 added and 5 dropped as
`asm/savsrc.py --patches` counts; `scsi_fep`, 43 and none added or
dropped. (The first try called `libvar/3` changed: the hasher orders a
table's keys differently in the two builds. Keys are now compared as a
set. That module's strings do differ, `~t` against `~T`, so the two
are not identical, though `binary_reverse_engineering.md` §2 finds
them so at instruction-count depth.)

**Patch against base** (`--patch MODULE --show`), MEASURED:

| Module (patch file) | Predicates changed | What the change is, READ against the source |
|---|---|---|
| `scsi_fep` (scsifep) | `send_packet2/10`, `send_packet3/10`; 41 the same, the module's constants the same | the base rounds a cut string's length up in `send_packet2` and copies the rest with `substring`; the patch passes the true length and rounds in `send_packet3`, copying with `copy_string_elements`. That is the source's "Remake by Amanuma" (`scsi_fep.kl1`:350-357, 394-417, the old text commented out beside it). Only a string argument cut across two packets is touched; no code, no layout |
| `fep_server` (fepsv) | added `get_fep_stream_wait/6`, `get_fep_stream_and_max_wait/7`, `get_fep_attributes/9`, `get_fep_attributes1/8`, `get_fep_attributes2/8`, `3/8`, `4/10`, `5/10`; dropped `get_fep_attributes/7`, `2/7`, `3/7`, `4/8`, `5/7`; changed `wait_21/9`, `wait_25/10` | an abort line through the start of a request: `wait_21` now calls the two new `get_fep_stream*_wait`, which add a `wait(AB)` clause before the FEP's stream is taken (`fep_sv.kl1`:142-185, 464-474); each `get_fep_attributes*` has a new first clause `wait(AB)` that answers `aborted` and binds the device's attention to `abort` (537-626); `wait_25` has a sixth clause, for `fep_info` under abort. The atoms of the 240 fetch are the same in the dropped and the added predicates (`file`, `remote_file`, `reset`, `fep_attributes`, `attri`, `put`), plus `aborted`/`abort` in each of the new ones (MEASURED); that the order without an abort is unchanged is the reading of the source's commented-out old lines beside the new, not a trace of the base |
| `fep_directory_device`, `dir_device`, `file_request_device`, `fep_file_request_device`, `fep_filter`, `filereq_filter` (mkdir) | 2, 1, 2, 1, 1 and 4 (3 added) | two commands are new in the patch (each diff looked at): 205 `make_directory` (`fep_directory_device:device_create/5` gains the clause with 205; `file_request_device:send_message/9` and `return_values/6` one clause each with the atom `make_directory`, the source's 529-533; `fep_file_request_device:request_device_io0/6` and `fep_filter:trans/3` one clause each) and 239 `kill` (`fep_directory_device:device_io1/8` one clause with 239; `dir_device:send_message/7` two, for Code 0 and 1). 240's handling (`return_values/6`'s `fep_attributes` clause) is not touched |

**Patch against source** (`--source MODULE`), MEASURED: every predicate
of `scsi_fep` (43), `fep_server` (36), `fep_directory_device` (16),
`dir_device` (18), `file_request_device` (37),
`fep_file_request_device` (6) has the source's clause count. Every
integer of a source clause (literal or `fep#` macro, the small ones
too) is among its object predicate's integers in the four `mkdir`
modules; in `scsi_fep` all but `scsi_sender/4`'s -1 and 80, which are
in the module's constants as `{-1,80}`; in `fep_server` all but 0 and
7 in five predicates (`file/3` and its four likes), also inside a
structured constant. Unpatched modules on the same path: `scsi` (8),
`fep_file_device` (18), `fep_string_io_device` (16) agree in full;
`scsi_processor` (4 of 5) and `login_server` (105 of 108) but for a
-1, 0, 1 or 7 of that kind; `login` 120 of 122 (two are compiler-made;
the window default's 200, 47, 14 are in the constants as
`{"PIMOS CONSOLE",{at,200,200},{char,47,14},"font:test_11.font"}`).

What this measure can and cannot tell (`--source MODULE --base`): the
BASE `fep_server` fails it (five predicates not in the source,
`wait_25/10` five clauses for the source's six), and so does the base
`fep_directory_device` (205 and 239 missing, a clause short in two
predicates), so for those the patch, not the base, is the held source.
The base `scsi_fep` passes it as the patch does: the change there
moves arithmetic and adds no clause or constant, and it is the
instruction diff above, read against the "Remake by Amanuma" text,
that identifies the patch as the source. The comparison is one way
(integers the object has beyond the source are not reported) and stops
at names, arities, clause counts and constants: not instruction for
instruction, which needs the compiler run on the source. Within that,
where a patch replaces a module §1-§3 read the right text, and the
"Caveat on the object" at the top is answered for these modules.

**Build switches of the held object**, each decided from the object
(`--has`, `--grep`; `pimos.h`, which sets them, is not in
`pimos.tar.Z`):

| Switch | Value | Evidence in the object |
|---|---|---|
| `fep_interface` | `scsi` | `resource_init` holds `"SCSI Server"` (`kernel/init/rsc_init.kl1`:26-31); `scsi` has `create/2` and no `dummy/0`; `scsi_conf:scsi_where/1` is the built-in `scsi_where` (`bios/boot/scsi_conf.kl1`:76-79) |
| `virtual_machine_interface` | not `yes` | `syslog` holds `"pimos:pimos.syslog"`; no string `>sys>user>me` or `PIMOS/VM` in any file (`bios/boot/syslog.kl1`:29-53, `bios.kl1`:22-51); `pim` holds `"PIMOS "` |
| `machine` | not `vm`; `mpsi` or `pimm` | `user_server_manager` holds `"pimos:pimos.conf"` (`server/login/init/usersvman.kl1`:29-40); `pseudo_system_timer_device` has 19 predicates, not the one of its default branch (`server/fep/timer/timePdvc.kl1`:15-16, 305-306) |
| `machine_type` | `mpsi` | `system_timer_manager:create/3` runs `set_timer` with two registers (`bios/boot/sysTman.kl1`:18-21; the `vpim` form has three) |
| `ipl_parameter` | `yes` | `pim:go2/4` builds its vector of five from five variables (`put_vector_5`, five `write_variable`) and ends in an `execute` after three `enqueue_goal` and two external ones: four goals of the module's own, the `yes` branch's (`bios.kl1`:54-63); the default branch has three and writes 0, 0, 7, 0, 1 (64-74), and neither `go2/4` nor the module's constants hold a 7. The run agrees (§1.4) |
| `autoloading` | not `no` | `autoload` has `init_0/4` and the string `"pimos:autoload.tbl"` (`server/module/autoload.kl1`:19-29): **the object asks for the file** (step 6 of §3) |
| `scsi#scsi_init`, `scsi#scsi_command` | the built-ins | `scsi:create/2` holds the instruction `scsi_init`, `command_executer/2` `scsi_command`; `scsi_builtin`'s KL1 stand-ins are in the file but not called there |

tcpip, lia, telnet and "remote login" are not compiled in or out: the
object holds all of them (`login` has the `tcpip` and `lia` clauses,
`telnet_login` is there), and which of them start is `pimos.conf`'s
`login:go([{0,local,0},{0,tcpip,0}],[],off)`.

### 7.2 Names (U10)

| Name on the wire | On the PSI | The stand-in serves |
|---|---|---|
| `pimos:NAME` | `>sys>csp>PIMOS.DIR` (`object/login.com`, `"pimos" := ..`), filled with `object/*` (`object/INSTALL`:8) | `pimosobj.tar.Z` `object/NAME`. Held and opened by PIMOS: `pimos.conf`, `pimos.logins`, `pimos.groups`. Not there: `autoload.tbl` (5), `pimos.syslog` (made by the append, OURS) |
| `me:NAME` | `user:pmpsi` (`login.com`, `"me" := ..`), holding `init.com` and `login.com` (INSTALL:9), both SIMPOS's own | nothing PIMOS asks for is there: `me:pimos.init` gets 5 |
| `HOME>NAME` | the directory the FEP's `simpos_user_device` gives for the SIMPOS user; PIMOS's own fallback is `">sys>user>" ++ RN` (`server/login/login/login_p.kl1`:61-63) | `shell.com` and `pimos.com` are asked for here and only here (`shell/main/shell.kl1`:575-579, 650-653, then `task:home`, 710-735; no `pimos:` fallback). INSTALL puts none in a home, so 5 for both, and the prompt is the default `"Shell>> "` |

Serving the held `shell.com` and `pimos.com` from the home directory
would be a choice of OURS beyond INSTALL (it gives the prompt
`"Shell<<1>> "` and two more windows, a second shell and a listener).

The held `pimos.logins` (two-byte JIS; the tuple is `{User, Password,
UID, MaxPrio, Dir, Node, Program, Comments}`, `login_sv.kl1`:443-459):

    {"super_pimos","",0,4095,*,0,pimos:: shell: login,[" "]}.
    {"shutdown","",10,4095,*,0,pimos:: shutdown: go,[" "]}.
    {"pimos","",101,4095,*,0,pimos:: shell: login,[" "]}.
    {"pmpsi","",102,3000,*,0,pimos:: shell: login,[" "]}.
    {"me","",103,2000,*,0,pimos:: shell: login,[" "]}.
    {"kiyo","",201,3500,*,0,pimos:: shell: login,[" "]}.

Every password is empty, and an empty password encrypts to itself
(`kernel/table/password.kl1`:12), so the only password that logs in is
the empty string. Every Dir is `*`: the home comes from the FEP.

### 7.3 The local login, message by message (U9)

`>` PIMOS to the FEP, `<` the FEP to PIMOS; S the server device
(`pimos_remote_login_server`), R the replier, each with the id it was
given. Order holds within a device's stream; between devices only
where the source chains them.

| # | Dir | Message | Source |
|---|---|---|---|
| 0 | console | `LOCAL  LOGIN SERVICE STARTS ***`, then the FEP number 0, by `display_console` (no wire) | `login.kl1`:966-968 |
| 1 | > | S: 620 `io(1, "  ")`. **Held by the FEP** | 969 |
| 2 | < | S: `{S, 1, NI}`, the login record (§7.5) | decoded 995-998, 1244-1269 |
| 3 | > | R: 620 `io(1, [ID] ++ "Login procedure starts.")` | 1007-1010, 1215-1219 |
| 4 | > | S: 620 `io(1, " ")`, the next login; held again | 1011 |
| 5 | > | a new device C: 601 `{C, 601, "", RN, RP, "simpos_user_device"}` (the confirm's device is made with RN, RP as its user, `conf_dvc.kl1`:12-18; `server/fep/string_io/strioRdvc.kl1`:167-170), then 620 `io(0, [len RN, len RP] ++ RN ++ RP)`; wants `{C, 1, Dir}`. The Fep server confirms RN, RP before it serves the file request of 1013-1014; with strings it always does, and an empty RN does not skip it (the skip needs the integers 0, 0, which a record cannot give) | `server/fep/fep/confirm.kl1`:23-34, 301-323; `conf_dvc.kl1`:41-44, 64-68, 79-91 |
| 6 | > | file: 201 `"me:pimos.init"`, User RN, Password RP; before it 240 if this I/O node was not yet asked. 5 gives the default window | 1093-1106, 1169-1173 |
| 7 | > | window W: 104 `{W, 104, "", RN, RP}`, then 127 `(200, 200, 47, 14)`, 130 `"PIMOS CONSOLE"`, 132 `"font:test_11.font"`, 143 | 1031-1042; `kernel/stdio/s-server.kl1`:267-271, 288-292; `server/fep/window/winRdvc.kl1`:166-169, `win_dvc.kl1`:498-499 |
| 8 | - | UN, UP checked by the login server against `pimos.logins` (read at step 9 of §3): no wire | 1059-1069 |
| 9 | > | R: 620 `io(1, [ID] ++ "OK. Your initial program starts." ++ LF)`, `io(1, [ID] ++ "Good luck!" ++ LF)`, `io(2, [ID])`. On a wrong name or password instead `io(1, [ID] ++ "Login incorrect")`, `io(2, [ID])`, and nothing more | 1075-1090, 1220-1231 |
| 10 | > | a new device: 601 `"simpos_user_device"`, 620 `io(0, ..)` as in 5: the reply's string is the HOME directory (Dir is `*` in every held entry) | `login_p.kl1`:46-85 |
| 11 | - | the entry's program, `shell:login`, as a task with `io_node`, `remote(RN, RP)`, the user's name, priority and uid, and no `stdio`; `task:home`, `task:directory` = HOME, `task:top_task` = on | `login_sv.kl1`:1517-1541; `login_p.kl1`:88-96 |
| 12 | > | file: 201 `HOME ++ ">" ++ "shell.com"`, then `"pimos.com"` likewise (each asked a second time under `task:home` if the first fails); 5 is taken in silence | `shell/main/shell.kl1`:281-286, 575-579, 643-655, 704-735 |
| 13 | > | W: 111 `"Shell>> "`, 112, 110 | 330, 350-357; `server/fep/window/win_dvc.kl1`:330-336, 481-484 |
| 14 | < | W: `{W, 1, Line}` when a line is typed: the second held reply | |

Every `>` above except 1, 4 and 13's 110 is answered at once with
`{Id, 1}` (or the values named); the replies to R's requests are not
looked at (`_` in 1010, 1080) but must be sent, one each, since each
has a `receive` queued. The `>` in row 12's paths is 240's fifth
value (§7.8). Each device is closed with 60 when its stream ends.

Not traced, so the run may show more: 141/142 from the standard-I/O
switch; what the shell prints before its first prompt; when the
confirm of row 5 recurs (its answer is kept per I/O node and name
while a stream uses it, `confirm.kl1`:62-89).

### 7.4 "Withheld" and "unsolicited" at the SCSI level

PIMOS does not poll, and is not interrupted. READ:

- All commands to the bus go through one process, which issues the
  next command when the built-in has bound `NewSCSI_OBJ`, **not** when
  the command is finished: `object_manager(FROM_USER, SCSI_OBJ) :-
  wait(SCSI_OBJ) | command_executer(..)`, and `command_executer` calls
  `scsi#scsi_command(SCSI_OBJ, V, NewData, TransferredLength, ID,
  Result, NewSCSI_OBJ)` (`bios/scsi/scsi_handler.kl1`:132-143).
  `Result`, `NewData` and `TransferredLength` are plain variables
  bound later; the callers wait on them
  (`scsi_processor.kl1`:100-103).
- The receiver has one RECEIVE outstanding at all times: it issues
  `receive(Buffer, Size, Result)` and the next one only when a packet
  has come (`bios/fep_module/scsi_fep.kl1`:476-479, and again from
  518, 526, 558). The sender issues SENDs on LUN 0 independently
  (232-239).
- `scsi_init`'s `TargetInterruptVector` is thrown away
  (`scsi_handler.kl1`:33, `scsi#scsi_init(SCSI_Obj,_,Info)`): no KL1
  code handles a target's interrupt.
- "Not ready" cannot be an answer. A RECEIVE that ends with
  completion-code bit 3 and length 0 is tried again ten times, each
  with `SCSI: receive retry!!` on the console, then given up
  (`scsi_processor.kl1`:130-133, 160-173); a busy status is an error
  at once (`scsi_common.kl1`:172-175). Either ends the receiver with
  `SCSI I/O Error: receive message`, and every device gets `abnormal`
  (`scsi_fep.kl1`:489-499, 150-154, 183-189). There is no timer in
  these modules.

So a **withheld reply** is nothing on the wire: the FEP has no packet
for that device, and the standing RECEIVE on LUN 1 stays unfinished,
for hours if need be, while SENDs on LUN 0 go on. PIMOS learns that
the reply has come when the built-in binds that RECEIVE's `Result`.
How the firmware held a command open on LUN 1 while running others on
LUN 0 (disconnect and reselection, presumably) is below the built-in
and not in the held source: INFERENCE. What the built-in must do is
fixed, and it is what both models already do (`pimm_semantics.md`,
`scsi_command`: "gives `Id` and `NewObj` at once and leaves the other
three as new variables").

An **unsolicited message** is a packet on that same RECEIVE whose
device has no request outstanding. PIMOS takes exactly one kind: status
3, the attention, which is made `{Id, attention}` whatever follows it
(`scsi_fep.kl1`:573-577) and binds the device's attention variable
without using up a `receive` (`fep_rcvr.kl1`:75-80). Anything else is
matched to the device's next `receive` in order (86-92), so the
replies of one device must come in the order of its requests; between
devices the order is free (`id_manager1`, 144-149, routes by id). A
packet for an id below the next free one that is not in the pool ends
the id manager with `SCSI_FEP internal error.` (161-168), and one for
an id above it matches no clause at all (the guard `DevID =< MaxID`,
146): the FEP must never invent an id.
The login record is therefore not unsolicited: it is the late reply
to request 1 of §7.3, on S's id.

### 7.5 The stand-in's behaviour

The smallest honest one. PIMOS prints no prompt; the FEP decides when
someone logs in.

**When.** The trigger is the FEP's own state, not the console text:
it holds an unanswered 620 with Command 1 on a device made by 601 with
Name `"pimos_remote_login_server"` whose `io(0, "local")` it answered
1, and the bench reports the machine idle (nothing left to run, the
only waiting SCSI command the standing RECEIVE). Then one scripted
event is taken: by default the login below, or, with an operator, the
three answers typed (node, user, password, as the manual's requester
asks them, `Eman/e-login.tex`:44-50). OURS: the idle test and the
script; SOURCED: that the request is the one of `login.kl1`:969.

**The record** NI, the string of `{S, 1, NI}`. On the wire it is an
8-bit string of two bytes an element, the first the high byte (the
reply is widened by `change_element_size(.., 16)`,
`strio_dvc.kl1`:224, `fep_util.kl1`:81-86; byte order §1.4), so an
even number of bytes. Characters are 16-bit JIS X 0208: `"local"` is
compared with the source's `string#"local"`, and the object's strings
are of that code (`"pimos:pimos.syslog"` begins 2370h, 2369h).

| Element | Field | Decoder | Value | Mark |
|---|---|---|---|---|
| 0 | ID | `login.kl1`:1247; echoed as element 0 of every replier text and in `io(2, [ID])` | 1 | OURS (U2: the real requester's range) |
| 1-5 | the lengths of Node, RN, RP, UN, UP, in elements | 1248-1252 | 5, 5, 0, 5, 0 | follow from the strings |
| 6.. | Node | 1253-1258: `"local"` makes the I/O node this FEP's number; any other string is a remote node's name | `"local"` | SOURCED (1256; the manual: "If you login from SIMPOS on the FEP, type ``local.''", `e-login.tex`:46) |
| | RN | the SIMPOS user: the file, window and string-I/O requests' User, the confirm, the default home | `"pmpsi"` | OURS; the name is HELD (`login.com`'s `"me" := ["user:pmpsi"]`), that it is the SIMPOS user is INFERENCE |
| | RP | the SIMPOS password | `""` | OURS |
| | UN | the PIMOS user, looked up in `pimos.logins` | `"pimos"` | HELD FILE (uid 101, `pimos:: shell: login`) |
| | UP | its password, encrypted and compared | `""` | HELD FILE (every entry's is empty) |

**What it answers after that**, each OURS unless marked:

- `io(0, "")` on the replier and `io(0, "local")` on the server:
  `{Id, 1, ""}`; only the status is used (`login.kl1`:883, 966).
- `io(0, "tcpip")` on the second server device (`pimos.conf` asks for
  it): `{Id, 5}`, the stand-in having no network. PIMOS then shows
  `CANNOT MAKE A TCPIP LOGIN SERVICE!!` and 0 (986-989) and goes on.
  Answering 1 instead gives a second STARTS line and a second request
  held for ever; the manual's log has one line.
- `simpos_user_device`, `io(0, [n, m] ++ RN ++ RP)`: `{Id, 1, Dir}`
  with Dir `">sys>user>" ++ RN`, the string PIMOS itself uses when the
  device gives none (SOURCED, `login_p.kl1`:63, 77, 85).
- The replier's `io(1, Text)`: `{Id, 1, ""}`, the text (less its
  first element) written to the stand-in's operator log; `io(2, ..)`
  `{Id, 1, ""}`.
- 201 of `me:pimos.init`, of `HOME>shell.com`, `HOME>pimos.com`:
  `{Id, 5}` (§7.2).
- 104, 127, 130, 132, 143, 111, 112: `{Id, 1}`; a 111's string is
  the window's text.
- 110: held like the login; answered `{Id, 1, Line}` on the next
  scripted event (a line of the script or of the operator), Line in
  16-bit JIS as bytes. Whether the line carries its newline is not
  read (`pimos_standard_io_window`'s `getl`, PSI side).
- 70: by §7.1; an aborted held request is answered `{Id, 6}`.

The script that reaches R6: the login, then one shell command that
needs only the kernel, then nothing: the run ends with the 110 after
the command's output held. Which command, and the manual transcript it
is checked against, is R6's choice (`pimos_roadmap.md` §2) and was not
made here.

### 7.6 What should be seen

| Step | Where | Text | Source |
|---|---|---|---|
| boot | machine console | `PIMOS V 3.600 20-May-93` | the run, §1.4 |
| service | machine console | `LOCAL  LOGIN SERVICE STARTS ***` then `0`; with the tcpip choice above, `CANNOT MAKE A TCPIP LOGIN SERVICE!!` then `0` | `login.kl1`:967-968, 986-988. The manual's log, of a V3.0 Multi-PSI, has `***** xxx LOGIN SERVICE STARTS` and `(  INTo) 00 00000000` (`Eman/e-sysman.tex`:104-111, `e-login.tex`:34-35); the held object has both wordings (in `login` and in `login_error`) |
| login | the requester (operator log) | `Login procedure starts.`, `OK. Your initial program starts.`, `Good luck!` | `login.kl1`:1007, 1077-1078; the manual has no transcript of these |
| window | title | `PIMOS CONSOLE`, at (200, 200), 47 by 14 characters | 1169-1173; "the shell window is displayed" (`e-login.tex`:119) |
| prompt | the window | `Shell>> ` | `shell.kl1`:330; `e-sysman.tex`:127 (`\keyin{Shell>> }{shutdown}`). With the held `shell.com` it would be `Shell<<1>> ` (`e-shell.tex`:993) |

### 7.7 What the models lack

As of this tree (cf71ee6c; another agent is changing `fep.py` and the
bench now). Nothing in the machine: the built-in's deferred completion is in both
(`ref/pimm/pimm.py` `i_scsi_command`, `scsi_poll`;
`bsv/PimmScsiBox.bsv`, "Not finished yet"). No target-initiated
interrupt is needed, because none reaches KL1 (§7.4). What is missing
is around it:

1. **The bench ends where PIMOS idles.** `ref/pimm/longrun_ipl.py`
   `go()` stops when the machine has run dry and `scsi_poll()`
   finishes nothing. With the kernel's receiver that is PIMOS's
   resting state, not an end (`scsi_fep.kl1`:476-479: a RECEIVE always
   waits). Needed: at that point ask the device for its next event
   (a `Fep.idle()`, say, returning whether it queued a reply), poll
   again, and stop only when the script is empty.
2. **`fep.py` cannot owe a reply.** `packet()` queues the reply or
   drops the request (`reply is None`, used for 70 only). Needed: a
   table of held requests by device id (the 620 Command 1, each 110),
   the event script that answers them, and the rule of §7.1 for a 70
   on a held request. Replies of one device stay in request order;
   the single reply FIFO already gives that.
3. **Device kinds.** 601 with the three names, 620 with commands 0,
   1, 2, the window calls of §7.3 rows 7 and 13, 240, the `pimos:`,
   `me:` and home name mapping (§7.2), 60 on every kind (§4's list).
4. **The Bluespec box is polled by the bench only.**
   `mkPimmCore.scsiPoll` is called for the test driver's `POLL`
   (`bsv/PimmDriverTb.bsv`, `ref/pimm/driver.py`); in a core with no
   bench nothing offers a waiting command again. Needed: a rule that
   polls when the goal queue is empty and a command waits (the device's
   interrupt in effect), or a completion pushed from the port. The
   waiting list's four places are enough: one RECEIVE stands, SENDs
   finish at once.
5. **The FEP emulator** (`bsv/PimmFepEmu.bsv`) answers "not ready"
   and is offered the command again, which is right, but has no source
   of events: a scripted login needs a trigger there too (a tape entry
   "at idle, queue this packet"), and the tapes a record kind for it.
6. **A clock** is not needed for the prompt (the BIOS timer is local,
   step 3 of §3), but a 303 alarm would be a third kind of held
   reply, by the same table.

### 7.8 Corrections to the sections above, not made in place

Found while settling U6-U10; the rows belong to the U1-U5 work, so
they are listed here.

- §2.1, row 70: settled (§7.1).
- §2.2, 240: the fifth value, called Dir, is the **path delimiter**:
  it is element 4 of the kept attributes, passed as `Deli` to every
  open (`server/fep/file/fileRdvc.kl1`:124-126) and joined between a
  directory and a file name; `">"` for SIMPOS. The second, OS, must
  begin `"SIMPOS"` for 222 to be read under Code 0
  (`file_dvcb.kl1`:557-562). Both bear on U1.
- §3 step 14 and U3: a login "with RN = RP = 0" cannot come from a
  record (strings always; `login.kl1`:1266-1269), so
  `simpos_user_device` is always asked, and asked again for the home
  directory (§7.3 rows 5 and 10).
- §3 step 16: every replier text has ID as its first element, and the
  two success texts end in LF.
- §3 step 17: the held `pimos.logins` has six entries; the first is
  `super_pimos` (underscore) and `shutdown` runs `pimos:: shutdown:
  go`. `shell.com` and `pimos.com` are asked for in the home
  directory, not `pimos:`, so with INSTALL's layout neither is read.
- §3 step 6 and "A minimal honest FEP": the object does ask for
  `pimos:autoload.tbl` (§7.1).
