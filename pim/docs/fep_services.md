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
  Compiled ESP: names, arities and literals only. Sections 1 to 5 were
  written with no method body read. **Section 6 reads the method
  bodies** (`psi/fepread/`) and settles U1 to U5 and the PSI half of
  U6; where a sentence of sections 1 to 5 says the PSI side is not
  known, section 6 is the later word.
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
  (`pimos.vmac`:159-162, C). The PSI answers Code 0 (§6.3).
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
its local `get_class_object/3`; the code has since been read and says
so (§6.4).

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
  they are methods of `pimos_window_editor`, and
  `pimos_standard_io_window` is a string-I/O program, not the window
  device (§6.4, §6.8).

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
  name for them; the PSI sends them only to another FEP (§6.6).

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
    there is in §6.5: the ID is 0 for the first login, the strings
    are 16-bit, and RN, RP are never null.
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

Since §6 the right-hand column is smaller: five of 240's seven
values, the replies to `io(0, ..)` and to the replier's commands, and
NI's ID and Node are read from the PSI's code (§6.3-6.5), not OURS.

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
`simpos_user_device` (the real requester always sends an RN and RP,
§6.5; a login with RN = RP = 0 would be OURS), status 5 for
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
  the PSI assembles none either (§6.7), but it answers the request
  the 70 interrupts with status 6, which `fep.py` does not. Whether
  the kernel's client waits for that is U6.
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
| U1 | **SETTLED but for two SIMPOS values (§6.3).** The PSI's answer to 240 is `{Id, 1, 0, "SIMPOS " ++ V, Host, "V0.45", ">", ".", ""}`. Still open: V (`:version` of `simpos##version`) and Host (`:get_my_node` of `simpos##network_node_name`), which SIMPOS supplies | SIMPOS's `version` class (not in the held packages), or a photograph or log of a PSI's version line; PIMOS shows neither value in the start, so a stand-in may choose both (OURS) |
| U2 | **SETTLED (§6.5).** NI is `[ID, len Node, n1..n4] ++ Node ++ RN ++ RP ++ UN ++ UP`, 16-bit; ID is the smallest free integer from 0; Node `"local"`; RN, RP are the SIMPOS user's local name and password, never null. Still open: nothing in the layout; H and L of the requester's own message rest on unwitnessed arithmetic opcodes (they do not reach PIMOS) | A document giving the KL0 built-in numbers, or the interpreter run against `paragraph`'s source |
| U3 | **SETTLED (§6.4).** `io(0, "")` on the replier and `io(0, "local")` on the server answer `""`; replier command 1 answers one character 0 (sent) or 1; `simpos_user_device` answers the user's directory from SIMPOS's `pathname`, or `">"`. Still open: the directory string a real SIMPOS user gets (SIMPOS's `remote_or_local/6`, not held) | P5 (pimfep under SIMPOS); a stand-in may answer `">"`, the PSI's own fallback |
| U4 | **SETTLED (§6.2, §6.8).** 127, 132, 143 are `pimos_window_editor` `reshape/7`, `set_font/4`, `show/3`; all 63 codes have a PSI handler. Still open: `refute/3` (SIMPOS's, not held) is taken to call the method named, from the arities; the 8-element `get_max_size` has no PSI clause | The `refute` method of SIMPOS's object class; a grep of the patch files' objects for a sender of the 8-element 103 (U8) |
| U5 | **SETTLED (§6.6).** 900-903 pass only between FEPs; on the PIM/m's own link 903 is logged and dropped and the others are not made. Still open: nothing for PIMOS. Grade: READ FROM CONSTANTS, with the clause chaining of `fep_scsi_output put/4` (unwitnessed `c2`/`d3`) as the one INFERENCE under "903 is dropped" | A KL0 opcode document, or the first close on the real link |
| U6 | **PARTLY (§6.7).** PSI half settled: no reply to 70; the interrupted timer, `io`, `getl`, socket `getb`/`accept` request is answered `{Id, 6}`; nothing found for a file or directory request. Still open: whether the kernel's client expects a reply to 70 (the PIMOS half), and what `tag_catch/9` does to a file request in progress | Tracing `receive(Vars, Result)` after `device_abort0` in `file_dvc.kl1` and `scsi_fep.kl1`'s sender; SIMPOS's `tag_catch` |
| U7 | The form of `File_names` (237, 238) and of `Attributes` (222) | `server/fep/file/dir_dvc.kl1`, `file_dvcb.kl1` (held, not read for this) and `pimos_directory` |
| U8 | Whether the held object asks for `pimos:autoload.tbl`, and whether its Fep and SCSI modules equal this source (the patch files) | The run itself; `asm/kl1decomp.py` on `pimm_patch_fepsv360E.sav` and `pimm_patch_scsifep360E.sav` |
| U9 | Which window is the login shell's standard I/O (the console of step 15 or a new one), and whether a user with no partition gets the "Enter your partition ?" dialogue (`server/login/login/login_p.kl1`) | Reading `login_sv.kl1`:1517-1541 with `login_p.kl1`; then the run |
| U10 | How `pimos:` and `me:` were resolved on the PSI. Held: they are SIMPOS logical names (`object/INSTALL`:8-9; `login.com` defines `pimos` as `>sys>csp>PIMOS.DIR` and `me` as `user:pmpsi`); `docs/simpos/` and `psi/` were searched for `pimos.init`, `autoload` and `simpos_user_device`: nothing beyond a format note | Nothing more is needed for a stand-in: serve `pimos:NAME` from the held `object/`, as INSTALL installs it |

## 6. The PSI side, read from `pimfep.ptf` (2026-11-24)

The compiled method bodies of `pimfep.ptf` were read with
`psi/fepread/` (`ptfread.py` lists a predicate with its constant pool
resolved; `fepfacts.py` computes what this section states;
`python3 -I psi/fepread/check.py` pins it, 38 checks). Nothing was
executed: there is no KL0 interpreter in this tree, and no SIMPOS.

**How it was read, and the grades.** No held document gives KL0 opcode
numbers, so an instruction is named only where a witness shows what it
does: 36 readings stand beside the held ESP source of the same clause
in `paragraph.ptf`, 4 beside the PIMOS source for the other end of the
same message (`psi/fepread/witness.py`, checked). The opcodes used
without a witness are listed there too.

- **READ FROM CONSTANTS**: the value is a literal (integer, string,
  atom, class reference, selector) in the cells, placed by witnessed
  instructions.
- **CROSS-END**: as above, and PIMOS's source independently expects
  the same thing.
- **INFERENCE**: rests on an unwitnessed opcode, or on the name of a
  SIMPOS method whose code is not held.

What a SIMPOS call *returns* is never known here: `simpos##` classes
are not held. Such values are named by the call that produces them.

**Mechanics found on the way** (MEASURED on the six PIM packages;
for `psi/README.md` "Cell numbering" and the KL0 interpreter):

- A hash-switch table spans `mask+1 + 2*keys + 2` cells. With that
  span all 9,815 predicates end four cells before the next entry and
  every local call lands on an entry; 142 of them hold a table, with
  no miss. The header word `ptfdump.py` calls `size` is the miss
  offset (cell + 2 + word), not a size.
- The trailer's terms are cells 2 to h2-1 of the class's code object,
  one top-level term a cell (`8b00 0d00 n` is one term, a class
  reference by symbol number): all 47 classes of `pimfep`, 548 of the
  554 of the six packages. An instruction's negative 16-bit operand
  addresses cell + 2 + operand, a pool cell or a predicate.
- `0308 n` is an 8-bit string of n bytes (not n words).
- In a method the receiver is in the last argument register, the
  other arguments in r0 upward.

### 6.1 How a command reaches its handler

READ in `pimos_scsi_front_end` (the main loop `$or$0/3`: `get/3`,
`get_command/2`, `command_type/2`, `refute_command/3`,
`check_fep_end/4`):

1. `command_type/2` sorts the command number: `server` for 103, 240,
   70, 80, 901, 902; `device_create` for 104, 102, 201-205, 310, 601,
   801; `device` for every other number (the last clause has no test).
2. `server`: the message is disassembled into a vector and matched by
   the clauses of `refute_server_command/3`, on (length, command):
   (6, 103), (3, 240), (2, 70), (2, 902), (2, 80), (2, 901).
3. `device_create`: `fep_device_class/2` gives the class
   (104, 102 `pimos_window_process`; 201-203 `pimos_file`; 204, 205
   `pimos_directory`; 310 `pimos_timer`; 601
   `pimos_string_io_invoker`; 801 `pimos_tcpip_socket`), and
   `:refute(Class, Name, Args)` is sent with the command's name from
   `fep_command_code_table`. Args is the message vector with three
   more elements, so the class method has arity message length + 4.
   The node argument is tested first (`is_self_node/2`): a 16-bit
   string that is empty, or equal to the FEP's own node name, or the
   same IP address, is this FEP; any other node forwards the message
   to that FEP (`get_node_stream/3`), or fails the creation.
4. `device`: the raw message is put on the stream of the device with
   that id (`device_table`, `get_at/5`). The device's own process
   takes it (`as_pimos_device` local `refute/3`), converts the command
   number to its name and sends `:refute(Device, Name, Vector)`; a
   failure is answered `{Id, 5}`. For a window the device
   (`pimos_window_process put/2`) hands the message to its
   `pimos_window`, whose `kl1_message/2` does the same on the window's
   **editor**. So a device command is the instance method of that
   name, with arity PIMOS's argument count + 3.

`refute/3` is not in `pimfep.ptf`. That it calls the named method with
the vector's elements is INFERENCE, from the arities: they fit in all
63 rows below.

### 6.2 The 63 commands and their PSI handlers

Generated by `python3 -I psi/fepread/fepfacts.py handlers`. The name
is `fep_command_code_table`'s for the code; the class is the device
class of §6.1; the method was found by name and arity.

| Code | Name | PIMOS device (§2) | PSI handler |
|---|---|---|---|
| 60 | close | every | `as_pimos_device close/3` |
| 70 | abort | every | `pimos_scsi_front_end refute_server_command/3, a 2-element message` |
| 80 | terminate | link | `pimos_scsi_front_end refute_server_command/3, a 2-element message` |
| 201 | read_open | file | `class pimos_file read_open/10` |
| 202 | write_open | file | `class pimos_file write_open/10` |
| 203 | append_open | file | `class pimos_file append_open/10` |
| 240 | fep_attributes | file | `pimos_scsi_front_end refute_server_command/3, a 3-element message` |
| 210 | getb | file; socket | `pimos_file getb/4`; `pimos_tcpip_socket getb/4` |
| 220 | end_of_file | file | `pimos_file end_of_file/3` |
| 111 | putb | file; window; socket | `pimos_file putb/4`; `pimos_window_editor putb/4`; `pimos_tcpip_socket putb/5` |
| 112 | flush | file; window; socket | `pimos_file flush/3`; `pimos_window_editor flush/3`; `pimos_tcpip_socket flush/3` |
| 221 | pathname | file; directory | `pimos_file pathname/3`; `pimos_directory pathname/3` |
| 222 | attributes | file | `pimos_file attributes/3` |
| 204 | directory | directory | `class pimos_directory directory/10` |
| 205 | make_directory | directory | `class pimos_directory make_directory/10` |
| 237 | listing_all | directory | `pimos_directory listing_all/4` |
| 231 | delete | directory | `pimos_directory delete/4` |
| 239 | kill | directory | `pimos_directory kill/4` |
| 232 | undelete | directory | `pimos_directory undelete/4` |
| 238 | deleted_all | directory | `pimos_directory deleted_all/4` |
| 233 | purge | directory | `pimos_directory purge/4` |
| 235 | expunge | directory | `pimos_directory expunge/3` |
| 310 | create_timer | timer | `class pimos_timer create_timer/9` |
| 301 | get_count | timer | `pimos_timer get_count/3` |
| 302 | on_at | timer | `pimos_timer on_at/4` |
| 303 | on_after | timer | `pimos_timer on_after/4` |
| 304 | get_date_time | timer | `pimos_timer get_date_time/3` |
| 601 | create_string_io | string_io | `class pimos_string_io_invoker create_string_io/10` |
| 620 | io | string_io | `as_pimos_string_io_device io/5` |
| 104 | create_window | window | `class pimos_window_process create_window/9` |
| 102 | create_with_buffer | window | `class pimos_window_process create_with_buffer/10` |
| 103 | get_max_size | window | `pimos_scsi_front_end refute_server_command/3, a 6-element message` |
| 110 | getl | window | `pimos_window_editor getl/3` |
| 113 | beep | window | `pimos_window_editor beep/3` |
| 114 | ungetb | window | `pimos_window_editor ungetb/4` |
| 121 | set_inside_size | window | `pimos_window_editor set_inside_size/5` |
| 120 | set_size | window | `pimos_window_editor set_size/3` |
| 124 | set_position | window | `pimos_window_editor set_position/5` |
| 123 | set_position_by_mouse | window | `pimos_window_editor set_position_by_mouse/3` |
| 127 | reshape | window | `pimos_window_editor reshape/7` |
| 126 | reshape_by_mouse | window | `pimos_window_editor reshape_by_mouse/3` |
| 130 | set_title | window | `pimos_window_editor set_title/4` |
| 132 | set_font | window | `pimos_window_editor set_font/4` |
| 140 | select_buffer | window | `pimos_window_editor select_buffer/4` |
| 146 | buffer_name | window | `pimos_window_editor buffer_name/3` |
| 141 | activate | window | `pimos_window_editor activate/3` |
| 142 | deactivate | window | `pimos_window_editor deactivate/3` |
| 143 | show | window | `pimos_window_editor show/3` |
| 144 | hide | window | `pimos_window_editor hide/3` |
| 145 | clear | window | `pimos_window_editor clear/3` |
| 122 | get_inside_size | window | `pimos_window_editor get_inside_size/3` |
| 125 | get_position | window | `pimos_window_editor get_position/3` |
| 131 | get_title | window | `pimos_window_editor get_title/3` |
| 133 | get_font | window | `pimos_window_editor get_font/3` |
| 801 | create_socket | socket | `class pimos_tcpip_socket create_socket/9` |
| 802 | bind | socket | `pimos_tcpip_socket bind/4` |
| 803 | listen | socket | `pimos_tcpip_socket listen/4` |
| 804 | accept | socket | `pimos_tcpip_socket accept/4` |
| 805 | connect | socket | `pimos_tcpip_socket connect/4` |
| 812 | connect_hostname | socket | `pimos_tcpip_socket connect_hostname/5` |
| 806 | set_socket_option | socket | `pimos_tcpip_socket set_socket_option/4, pimos_tcpip_socket set_socket_option/5, pimos_tcpip_socket set_socket_option/6` |
| 810 | send_timeout | socket | `pimos_tcpip_socket send_timeout/4` |
| 811 | receive_timeout | socket | `pimos_tcpip_socket receive_timeout/4` |

- **Every code PIMOS sends has a handler** of the right arity. One
  form has none: `get_max_size` with User and Password
  (`bios/fep_module/win_dvc.kl1`:44, an 8-element message). The PSI
  matches only the 6-element form of line 37. The window server sends
  that one (`server/fep/window/winRdvc.kl1`:182); no sender of the
  other was found outside `bios/`.
- **Handled on the PSI, never sent by PIMOS**: 901 and 902 (server
  keys, §6.6); `ungetb` (114) on a file (`pimos_file ungetb/4`);
  commands 1 and 2 of `simpos_user_device` (§6.4).
- **Named in the PSI's table with no handler found**: the stream tags
  of §2.8, 400 `ipl`, 710 `node_name`, the option values 807-809, and
  900, 903 (internal, §6.6).
- A 60 to any device: `as_pimos_device close/3` answers `{Id, 1}`,
  then `{Id, 903}` (which does not reach PIMOS, §6.6) and marks the
  device closed. `pimos_tcpip_socket` has its own `close/3`;
  `pimos_file` and `pimos_window_editor` add an after-demon.
- 80: answered `{Id, 11}` with the id of the request (PIMOS sends
  -1): `fep#end`, which ends PIMOS's receiver (§1). CROSS-END.
- Timer: `get_count` answers `{Id, 1, Count}`, `get_date_time`
  `{Id, 1, A, B}` from `:get_count(DateTime, A, B)` of
  `simpos##date_time`, an alarm `{Id, 1, 9}`. CROSS-END with §2.4.

### 6.3 U1: the answer to 240. SETTLED but for two SIMPOS values

`refute_server_command/3`, clause `{Id, 240, Node}`, calls `$or$3/4`.
If Node is this FEP (§6.1 step 3) it calls local `fep_attributes/7`
and answers the 9-vector `{Id, 1, A0, .., A6}` with the seven results
in order; for another node the message is forwarded; if that fails,
`{Id, 5}`.

| Element | Value | Where it comes from | Grade |
|---|---|---|---|
| Code | 0 | `get_integer r0, 0`. 0 is `fep#jiskanji`: paths are 16-bit JIS as bytes (§2.2) | READ FROM CONSTANTS |
| OS | `"SIMPOS "` ++ V | `:version(#simpos##version, V)`, then `:append(#simpos##string, ["SIMPOS ", V], OS)`. V is not held | constant READ; V UNKNOWN |
| Host | the node name | `:get_my_node(#simpos##network_node_name, Host)`. Not held | UNKNOWN value |
| FepVer | `"V0.45"` | `:pimfep_version(#pimos_scsi_front_end, FepVer, _, _)`, which reads the class attribute `version`; its initial value in the template is `"V0.45"` (beside `creation_date` `"14-Jan-94"`, `comment` `"mkdir/rmdir, all_device_end"`). No method of the package writes the attribute | READ FROM CONSTANTS |
| Dir | `">"` | pool constant | CROSS-END: PIMOS uses this element as the path delimiter between directory and name (`server/fep/file/fileRdvc.kl1`:125, 326-359), and `>` is SIMPOS's |
| FileVer | `"."` | pool constant | READ FROM CONSTANTS |
| Comment | `""` | pool constant | READ FROM CONSTANTS |

All strings are 16-bit JIS. §5's guess that FepVer is "V0.45" is now
read, not inferred. For a stand-in: Code 0, OS `"SIMPOS "` plus a
version text of our choosing (OURS), Host a node name (OURS), the
other four as above.

### 6.4 U3: the three string-I/O programs. SETTLED

601 (`pimos_string_io_invoker` class `create_string_io/10`): Name
must be a 16-bit string; it is made an atom
(`:enter_atom(#simpos##symbolizer, ..)`), the class object of that
name is taken from `simpos##library` (`get_class_object/3`), an
instance is created and its process started; `{Id, 1}` when the
process reports `normal`. That 601 makes an object of the class named
(§2.5) is now READ.

620 (`as_pimos_string_io_device io/5`, `do_io/6`): calls the object's
own `io/4` as `:io(Obj, Command, To_fep, From_fep)` and answers
`{Id, 1, From_fep}`. From_fep left unbound is sent as `""`; otherwise
it must be a 16-bit string. If `io/4` fails, `{Id, 5}` (§6.1 step 4).

| Program | Command | What `io/4` does | From_fep |
|---|---|---|---|
| `pimos_remote_login_replier` | 0 (PIMOS: `io(0, "")`) | starts its socket table and listener | `""` |
| | 1 (a text for the user) | sends the text to the requester whose ID is element 0 | one character: 0 if it was sent, 1 if not |
| | 2 (`[ID]`) | closes that requester's socket | `""` |
| `pimos_remote_login_server` | 0 with `"local"`, `"lia"` or `"tcpip"` | sets the server type (`local_login`, `lia`, `tcpip`) and opens that listener; any other text fails | `""` |
| | 1 | waits for a login request (§6.5); needs command 0 first | the NI of §6.5 |
| `simpos_user_device` | 0 with `[len(Name), len(Pass)] ++ Name ++ Pass` | `:identify(#pimfep##simpos_user, Name, Pass, User)`, or `:regist` if that fails; then the user's `world`, its default logical name L, `:root_path(World, L ++ ":", P)`, `:remote_or_local(#simpos##pathname, P, _, Dir, _, _)` | Dir; `">"` if the last steps fail |
| | 1, 2 (PIMOS never sends them) | the user's `fullname`, `nickname` | that string |

Grades: the three `""`, the 0/1 character, the three type names and
the `">"` fallback are READ FROM CONSTANTS. `simpos_user_device`'s
argument layout is CROSS-END (`melt/4` takes the string apart exactly
as `confirm.kl1`:301-323 builds it). What `remote_or_local/6` returns
(a directory path of the user's home, by the names) is INFERENCE; a
stand-in may answer any directory string, or `">"`.

PIMOS also opens `"pimos_standard_io_window"` by 601
(`server/user/pass_body.kl1`:68, `su_body.kl1`:51,
`shutdown_b.kl1`:42). Its `io/4` switches on the Command as a window
code: 104, 60, 130, 124, 121, 141, 142, 111, 110, 112, 145. That is
why those keys are in a string-I/O class (§2.6); it is not the window
device. Not needed for a login.

### 6.5 U2: the login record. SETTLED

**What the requester sends** (`as_pimos_login_requester` local
`create_message/3`; the transport is a SIMPOS port for a local login,
a LIA or TCP/IP socket otherwise):

    "PimosLogin" H L n1 n2 n3 n4  RN RP UN UP

all in 16-bit characters: the ten letters; H and L, the total length
of the four strings divided by 256 and its remainder; n1..n4, the
lengths of RN, RP, UN, UP, each as one character; then the strings.
(The template constant is `"PimosLoginHL1234"`; elements 10-15 are
overwritten.)

- UN and UP are what the user typed (§6.7); both must be 16-bit
  strings, or the requester writes "Illigal input.".
- RN is `:local_name` and RP `:user_password` of the SIMPOS user of
  the requester's own process (`:self(#simpos##process, P)`,
  `:user(P, U)`). **A local login sends them too**: there is no null
  form. Their values are SIMPOS's.

**What the server answers the pending `io(1)` with**
(`pimos_remote_login_server` `receive/2`, `remote_node_name/5`,
`reassemble_message/3`, `receive_message/5`), a 16-bit string:

| Element | Value |
|---|---|
| 0 | ID: the smallest integer from 0 not in use as a key of the replier's socket table (`pimos_remote_login_socket_table get_key/4`). The first login is 0 |
| 1 | length of Node |
| 2-5 | n1..n4 as received: lengths of RN, RP, UN, UP |
| then | Node, RN, RP, UN, UP |

Node is `"local"` for a local login (constant); for `lia` and `tcpip`
it is looked up from the peer's address (SIMPOS tables). This is
PIMOS's `get_node_info/3` layout (§3 step 12): CROSS-END. The record
is built as `"IN"` ++ lengths ++ Node ++ strings with elements 1 and
0 then overwritten, so the two letters never arrive.

Before answering, the server sends the requester "Your request is
accepted." and hands the connection to the replier, which then
carries PIMOS's texts (§3 steps 13, 16) to the user's window. Each
reply to the requester is `"PimosLogin"`, H, L, text.

Ranges: a length is one 16-bit character; the requester does not
check a bound. Grade: the layout is READ FROM CONSTANTS and
CROSS-END; the arithmetic (divide, multiply, subtract) rests on
unwitnessed built-in opcodes, INFERENCE for H and L only.

### 6.6 U5: 900-903 are FEP-to-FEP. SETTLED: PIMOS does not receive them

A `pimos_scsi_front_end` has a type, given at creation: `pimscsi`
(the PIM/m's SCSI link), `pseudo_scsi`, `nise_scsi`, `sline`, or
`remote_fep` (`remote_pimfep_invoker`: this FEP serving another FEP
over the network).

| Code | Where it is made | Where it goes |
|---|---|---|
| 903 `device_end` | `as_pimos_device close/3`, after the `{Id, 1}` of every close | `fep_scsi_output put/4`: if the type is not `remote_fep` and the command is 903, the message is **logged and not sent**. On a `remote_fep` it goes to the other FEP, whose `pimfep_message_receiver refute_internal_command/4` consumes it (`internal`) |
| 900 `creation_fail` | `pimos_scsi_front_end` `$or$4/3` (before the answer to 103 and 240) and `create_device/4` | only when `:fep_type(Fep, remote_fep)` holds; consumed by the other FEP's receiver, which removes its table entry for the id |
| 901 `all_device_end` | `delete_remote_stream/2` (`{0, 901}` to a node's stream); `check_fep_end/4` | to another FEP, or on a `remote_fep`; a received `{_, 901}` is taken in silence |
| 902 `remote_echo_check` | `pimfep_message_receiver receive_first_message/2` | to another FEP; a `remote_fep` echoes a received `{_, 902}` |

READ FROM CONSTANTS for the codes, the type atoms and the tests. The
test that drops 903 is `put/4`'s second clause: type `\==`
`remote_fep` (`blt 65`, witnessed as `\==` in `paragraph`'s
`color_line_v draw_std/2`), the command `==` 903 (`blt 62`,
witnessed), a cut, `log/2`; the third clause is the one with `put/2`.
What is left as INFERENCE is only that a failed test goes on to the
next clause (`c2`, `d3`: the unwitnessed clause-chain opcodes every
multi-clause predicate here uses). In support, not proof: PIMOS has
no name and no receiver clause for 900-903 (§2.8). So on the PIM/m's
own link none of the four is sent, and §5's
question about PIMOS's receiver does not arise. (The 900 and 901 in
`remote_pimfep_executor` number its own console texts, not commands.)

### 6.7 U6, the PSI half: 70 gets no reply; the interrupted request gets status 6

`refute_server_command/3`, clause `{Id, 70}`: the device is looked up
and `abort_device/4` sends `:abort(AbortHandler, pimos_abort,
DeviceProcess)` (for a device on another FEP it forwards the
message). **No reply to the 70 is assembled.** READ.

The device process runs each interruptible request under
`tag_catch/9` with the tag `pimos_abort` and an abort method:

| Device | Request | Abort method | Answer to the interrupted request |
|---|---|---|---|
| timer | `on_at`, `on_after` | `abort_timer/3` | `{Id, 6}` |
| string I/O | `io` | `abort_string_io/2`, then the class's `device_abort/1` | `{Id, 6}` |
| window | `getl` (if one is pending) | `abort_command/1`, editor's `abort_getl/1` | `{Id, 6}` |
| socket | `getb`, `accept` | `abort_getb/3`, `abort_accept/3` | `{Id, 6}` |
| file, directory | any | `as_pimos_device abort_loop/1` only | none found |

6 is `fep#aborted`. The `{Id, 6}` vectors are READ FROM CONSTANTS;
what `tag_catch/9` and `abort/3` do is INFERENCE from their names
(SIMPOS). The PIMOS half (whether its client waits for anything after
70) is still §5's.

### 6.8 U4: the window commands

127, 132 and 143 are `pimos_window_editor` `reshape/7`, `set_font/4`
and `show/3`, reached as in §6.1 step 4; so are the other 21 window
commands of §6.2. Each answers `{Id, 1}` (READ in those three).
SETTLED. `pimos_window_editor` inherits `simpos##standard_editor`
and `pimos_window` `simpos##pmacs_window`: the window is a PMACS
editor buffer, which is where echo and line editing come from (not
held).

### 6.9 The login dialogue on the PSI's screen

The dialogue is `pimfep##pimos_login_requester` (`login.com`'s menu
entry, §3). READ at the level of selectors and constants; the window
and menu classes are SIMPOS's.

1. `initiate/1`: a `simpos##standard_io_window` created with
   `[{size, {ch, 40}, {ch, 7}}, {position, manipulator}, {nature,
   [with_icon]}]`, font `"font:test_11.font"`, title
   `"Pimos remote login "` ++ the process number. Two menus are built
   from files of terms: `"PIMOS FEPs"` from `me:pimos.feps` (default
   item `"local"`) and `"PIMOS USERs"` from `me:pimos.uids` (default
   `"me"`), each with an `"ABORT"` item.
2. `read/4`: clear, show; `putl` **"Enter FEP node name--------->"**,
   read a line (a first character 0x2121, a JIS space, opens the FEPs
   menu when the additional function is on); the answer `exit` ends
   the program. `putl` **"Enter your PIMOS user name-->"**, a line
   (or the USERs menu). `putl` **"Enter your PIMOS password--->"**,
   echo inhibited, characters read up to code 13, echo permitted,
   window cleared.
3. The node name `"local"`, or this node's own, makes a local login;
   another is looked up, **"Unknown FEP node name."** if not found.
4. The request is sent (§6.5). Texts from the PIMOS side are shown
   with `show` and `putl`: first the server's **"Your request is
   accepted."**, then PIMOS's own (§3 steps 13, 16). After the
   exchange the window beeps twice and waits for a key.

Every string of the four login classes (52 with repeats; all decode
as JIS X 0208; `fepfacts.py strings` lists each with its predicate):

| Class | Text | Shown when |
|---|---|---|
| `pimos_login_requester` | `Enter FEP node name--------->`, `Enter your PIMOS user name-->`, `Enter your PIMOS password--->` | the three prompts (`read/4`) |
| | `Pimos remote login ` | window title (`title_string/1`) |
| | `font:test_11.font` | font of window and menus |
| | `PIMOS FEPs`, `PIMOS USERs`, `ABORT`, `local`, `me` | menu titles and items |
| | `me:pimos.feps`, `me:pimos.uids` | files read for the menus (not shown) |
| | `close`, `exit` | compared with the input (not shown) |
| `as_pimos_login_requester` | `Receive timeout.`, `Network error.`, `Network error`, `Illigal input.`, `Unknown FEP node name.` | errors, written to the window |
| | `PimosLoginHL1234`, `PimosLogin`, `local`, `::pimos_remote_login_server`, `pimos_remote_login_server`, `process`, `spawn` | protocol and addressing (not shown) |
| `pimos_remote_login_server` | `Your request is accepted.` | sent to the requester, which shows it |
| | `PimosLogin`, `IN`, `local`, `lia`, `tcpip`, and the addressing strings above | not shown |
| `pimos_remote_login_replier` | `PimosLogin`, one character 0, one character 1 | not shown |

To reproduce the screen exactly: the characters are full-width JIS.
The run of dashes in the prompts is JIS 215d (MINUS SIGN, U+2212),
not a hyphen, and `>` is 2164; `.` is 2125, `:` 2127, `_` 2132; the
spaces are 2121. "Illigal" is the binary's spelling.

The texts PIMOS sends through the replier ("Login procedure starts.",
"OK. Your initial program starts.", "Good luck!", "Login incorrect")
are in PIMOS's source (§3), not in `pimfep.ptf`.

### 6.10 What this changes for the stand-in (`ref/pimm/fep.py`)

- 240: answer `[1, 0, "SIMPOS ...", host, "V0.45", ">", ".", ""]`
  (strings 16-bit).
- `io(0, "")` on the replier and `io(0, "local")` on the server:
  `[1, ""]`. Replier commands 1 and 2: `[1, "\0"]` and `[1, ""]`.
- The scripted login's NI: `[0, 5, n1, n2, n3, n4] ++ "local" ++ RN
  ++ RP ++ UN ++ UP`, with RN and RP real strings (a SIMPOS user and
  password, OURS), not zeros. So PIMOS will confirm them through
  `simpos_user_device` (§3 step 14), which answers `[1, Dir]`; `">"`
  is the PSI's own fallback.
- 60: one reply `[1]`; no 903 (§6.6, with its one INFERENCE). 70: no reply; a pending timer, `io`
  or `getl` on that device is answered `[6]`. 80: `[11]`.
- No 900-903 ever.
