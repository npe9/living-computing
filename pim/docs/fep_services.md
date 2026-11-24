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
| U6 | Whether the kernel's client expects a reply to 70, and what the FEP answers to the request it interrupts | Tracing `receive(Vars, Result)` after `device_abort0` in `file_dvc.kl1` and `scsi_fep.kl1`'s sender; the PSI's `abort_timer`, `device_abort/1` |
| U7 | The form of `File_names` (237, 238) and of `Attributes` (222) | `server/fep/file/dir_dvc.kl1`, `file_dvcb.kl1` (held, not read for this) and `pimos_directory` |
| U8 | Whether the held object asks for `pimos:autoload.tbl`, and whether its Fep and SCSI modules equal this source (the patch files) | The run itself; `asm/kl1decomp.py` on `pimm_patch_fepsv360E.sav` and `pimm_patch_scsifep360E.sav` |
| U9 | Which window is the login shell's standard I/O (the console of step 15 or a new one), and whether a user with no partition gets the "Enter your partition ?" dialogue (`server/login/login/login_p.kl1`) | Reading `login_sv.kl1`:1517-1541 with `login_p.kl1`; then the run |
| U10 | How `pimos:` and `me:` were resolved on the PSI. Held: they are SIMPOS logical names (`object/INSTALL`:8-9; `login.com` defines `pimos` as `>sys>csp>PIMOS.DIR` and `me` as `user:pmpsi`); `docs/simpos/` and `psi/` were searched for `pimos.init`, `autoload` and `simpos_user_device`: nothing beyond a format note | Nothing more is needed for a stand-in: serve `pimos:NAME` from the held `object/`, as INSTALL installs it |
