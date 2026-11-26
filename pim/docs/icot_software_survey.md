# ICOT / FGCS software: what existed, what we hold, what is public, what is lost

Survey written 2026-11-20. It answers one question for the PIM/m
reconstruction: of the software that ran on the ICOT machines (PSI,
PSI-II, PSI-III alias PSI/UX, Multi-PSI, the PIMs, and the later UNIX
ports), which do we hold, which can be downloaded today, and which is
gone and would have to be rewritten.

It builds on, and does not repeat, `pimos_roadmap.md`,
`pimos_boot_requirements.md`, `pimos_binaries.md`,
`pseudo_pimm_firmware.md`, `gap_analysis.md`, `icot_databases.md` and
`literature_gaps.md` (section 9 and Appendix D).

**Labels used on every claim.**

- Evidence: **READ** = opened in this session and the statement seen
  (how is stated); **CATALOGUE** = from a catalogue, index or abstract
  page only; **SECONDARY** = taken from another document, including
  this project's earlier notes, and not re-opened here.
- Status: **HELD** = in `docs/nonlocal/`, verified by listing the
  archive in this session; **PUBLIC** = downloadable ("verified" means
  an HTTP 200 and the right magic bytes were seen on 2026-11-20;
  "listed" means only a directory listing or link was seen);
  **CITED-ONLY** = documented to have existed, no copy found;
  **UNKNOWN**.

Hosts: `AIST` = `https://www.airc.aist.go.jp/aitec-icot/ICOT/`,
`UEDA` = `https://www.uedalab.jp/AITEC_ICOT_ARCHIVES/ICOT/` (same
tree; only UEDA serves directory listings).

## 0. Summary

1. **What we hold is the whole KL1 side of one configuration and none
   of the layer beneath it in readable form.** HELD: PIMOS 3.6 in
   source (485 `.kl1` files under `src/`, counted here; 502 in the whole
   archive with `src_util/`), the matching object set (the
   IPL image and 20 `.sav` module sets; `pimos.ipl` names exactly those
   20, checked here), the manual, and the Pseudo PIM/m package for
   PSI-III: KL0 and KL1 firmware and the console, front-end and SCSI
   software, **all as binaries** (microcode images and compiled ESP
   package files). No source of any firmware, of SIMPOS, of the ESP
   system, of the CSP or of the FEP side is held, and none was found
   anywhere.
2. **Every PIMOS file the boot path loads is held; three things on
   the path are missing as something executable.** (Two small
   artifacts are missing or mismatched on the firmware side: the patch
   file `pimm_patch.com` that `boot.init` names is not in the archive,
   and the held firmware lacks `scsi_transfer`, which the object set
   uses once. *Note 2026-11-23: that one use is the listener's
   command pass-through, module `listener_cmd_builtin` in
   `pimm_debugger360E.sav` (source `src/debugger/listener/com_built.kl1`:135,
   `do_command(scsi_transfer(...))`), found with `asm/unlsav.py`'s
   reader; no boot or system path calls it, so the mismatch matters
   only if a user types that command.*) (a) The KL1 firmware:
   the machine that interprets KL1-B, with scheduler, suspension,
   shoen, GC. Held only as PSI-III microcode. (b) The console
   processor's boot functions (clear, init, impl, patch, ipl, start).
   Held only as compiled ESP for SIMPOS. (c) The front-end processor:
   the SIMPOS program at the other end of the SCSI link that serves
   files, windows, timers, string I/O and sockets to PIMOS. Held only
   as compiled ESP (`pimfep.ptf`, `pimscsi.ptf`). All three must be
   reconstituted; section 1 sizes each and says from what.
3. **The FEP is better documented by what we hold than the earlier
   notes assumed.** The PIMOS source contains the client of every FEP
   service and the numeric command codes (`src/macro/pimos/pimos/pimos.vmac`,
   105 `fep#` definitions, with argument comments), the
   packet assembly over SCSI (`src/bios/fep_module/scsi_fep.kl1`, 628
   lines), and the FEP-side package file gives the class and method
   names of the real server, including a `fep_command_code_table`
   whose names match the PIMOS codes. What has no source is the
   IPL-time variant (`scsi_fep_file`, `scsi_fep_module`,
   `scsi_fep_general`, `scsi_fep_util`, `ipl*`, `top`: object code
   only, SECONDARY from `pimos_boot_requirements.md`).
4. **The ICOT Free Software catalogue has 100 numbered entries; 98
   have at least one compressed archive (checked per entry by magic
   bytes), all of which answer today.** Every one of the 156
   file links on the 100 abstract pages returned HTTP 200 on AIST on
   2026-11-20; 116 distinct files are compressed archives by magic
   bytes, 100,608,737 bytes in all (Content-Length). Entries 26 (QUTE)
   and 27 (SAM) have a catalogue page and no archive ("[??K]"), and no
   file for them is in the tree. By environment field (a package can
   count twice): 49 name PIMOS, 32 name SIMPOS, 10 KLIC, 6 Common ESP,
   21 plain UNIX/C/Prolog or other. Of the 32 that name SIMPOS, 14 are
   the KL1 system itself or KL1 packages with a front-end half (3, 4,
   31, 32, 39, 53, 55-61, 64) and 18 name SIMPOS without PIMOS; of
   those 18, entry 7 is a KL1 tool for the pseudo Multi-PSI and entry
   27 has no archive, leaving 16 ESP applications for SIMPOS. We hold 8 files from 6 entries (1, 2,
   3, 4, 72, 85). *Corrected 2026-11-23: true when written; later on
   2026-11-20 the whole IFS tree was fetched as data (1,724 files,
   nothing unpacked or run), so all 150 files the abstract pages link,
   the 116 archives among them, are now held
   (`nonlocal/IFS_MANIFEST.md` §1, "Catalogue coverage"). The "HELD"
   marks in section 3 and the "download now" list in 5.1 predate that
   fetch.*
5. **IFS is applications and the KL1 system. It is not the machines'
   system software.** Not in IFS and not found anywhere: SIMPOS, the
   ESP compiler and runtime, any KL0 firmware source, the Multi-PSI
   and PIM/m KL1 microcode, the real CSP and its manual, FEP sources,
   the CAL cross system, the PSL translator for VPIM, the PIMOS
   internal file system, Common ESP (commercial). Section 4.
6. **The 16 ESP applications for SIMPOS are stranded.** They need
   SIMPOS on a PSI, or Common ESP, and neither is obtainable. The 49 PIMOS/KL1
   packages are what a booted PIMOS can run; several also need an
   ESP part on the FEP (windows, string I/O devices), which is a
   reconstitution item of its own.

## 1. The reconstruction path: every component, and where it stands

Goal: simulate PIM/m, boot PIMOS 3.6 from the held object files, run
applications. Sizes are measured in this session from the held
archives unless marked. "Job" is this survey's assessment, not a
measurement.

| # | Component | Source held? | Binary held? | Documentation | Reconstitute? | Size of what exists / from what |
|---|---|---|---|---|---|---|
| 1 | **KL1-B instruction set, PIM/m dialect** (what the microcode decodes) | No | Yes, for the Pseudo PIM/m: `psdpim/PMPSI.DIR/pimm.MEkbn`, 506,624 B, PSI-III microcode | Encoding from the PIMOS assembler source (HELD); TR-246, TR-389 (HELD PDFs); PIMOS manual `e-builtin.tex` (HELD) | **Yes** (under way) | 197 instruction names used by the object set, 54 modelled (SECONDARY, `gap_analysis.md`; that was 2026-11-20: 128 on both models on 2026-11-23, `ref/pimm/README.md`). From: PIMOS compiler and assembler source, PDSS C source (sibling dialect, HELD), VPIM (HELD), the microcode binary |
| 2 | **KL1 runtime in firmware**: goal queue and priorities, suspension, shoen, exceptions, MRB, GC, code and module objects | No | Same file as 1 | PIMOS manual `e-shoen.tex`; console text gives two record layouts (`pseudo_pimm_firmware.md`); TR/TM reports | **Yes**. The largest single job | From PDSS `emulator/` (28,441 lines of C, SECONDARY from `MANIFEST.md`), VPIM `src/` (185 PSL files, SECONDARY), the microcode once its datapath fields are read |
| 3 | **CSP boot functions**: clear, init, impl (load microcode), patch, ipl (load `.kbn` and `.sym`), start | No | Yes: `INSTALL.DIR/pimmcsp.ptf`, 1,496,186 B, 281 ESP classes (names READ); `pimmutil.ptf` 477,374 B, 51 classes (corrected 2026-11-23 from 50: `asm/ptfdump.py` lists 51 class records, `binary_reverse_engineering.md` §4.1); `mpsicspR.ptf` (remote CSP) 183,078 B, 30 classes | `SYSTEM.DIR/boot.init` (READ, decoded: `impl(...,"/usr/psi/pimos/kl1/pimm.MEkbn")`, `patch(on,"pmpsi:pimm_patch.com")`, `ipl(on,"pimos:pimm_ipl.kbn","pimos:pimm_ipl.sym")`, `start(pimos,"20c")`); `PIMM.PARAM`, `PIMM.CONFIG`; PIMOS 3.0 primer (PUBLIC, READ). The CSP operating manual is CITED-ONLY | **Yes**, minimal | Small: place the `.kbn` at its load address, set the start address, provide the console. The `.kbn` format is decoded (`pimos_binaries.md`). Not held: `pimm_patch.com`, which `boot.init` names and the archive does not contain |
| 4 | **IPL image** `pimm_ipl.kbn` (+ `.sym`, `.ldb`) | Partly: 8 of its 20 modules have same-named source; `ipl`, `ipl_loader`, `ipl_module`, `ipl_pool`, `ipl_link_table`, `ipl_scsi`, `ipl_file_decoder`, `top` and four `scsi_fep_*` do not (SECONDARY) | Yes: 92,160 B | Japanese PIMOS 3.0 manual section 6.1 (PUBLIC; SECONDARY reading) | No: run as held | 20 modules, 349 predicates (SECONDARY). Its FEP exchange must be read out of the object code |
| 5 | **`pimos.ipl`** module list | n/a (text) | Yes: 1,678 B | same | No | READ, decoded here: 8 base sets in the order kernel, shell, utility, library, debugger, server, bios, macro; then 12 patch sets (macro, hash, tel, fepsv, driver, modu, mkdir, shutl, scsifep, libvar, newpg, lis). Paths `>sys>csp>PIMOS.DIR>pimm_*360E.sav`. All 20 are held; no held `.sav` is unlisted |
| 6 | **PIMOS module sets** (`.sav`) | Yes, `pimos.tar.Z` `src/`: kernel 42 files / 14,444 lines; bios 35 / 11,557; server 97 / 33,162; shell 45 / 9,272; library 95 / 37,015; utility 43 / 19,048; debugger 116 / 28,392; macro 3 `.kl1` + macro files. Version string `3.600` (READ) | Yes: `pimm_{kernel,bios,server,shell,library,utility,debugger,macro}360E.sav`, 193,026 to 1,316,520 B | Manual, `pimosman.tar.Z` (HELD, LaTeX); typeset `pimosman.ps.Z` PUBLIC verified, 866,355 B | No | Whether the 1994 objects were compiled from exactly this source is unchecked (SECONDARY) |
| 7 | **The 12 patch sets** `pimm_patch_*360E.sav` | Not as such: no patch directory in the source; whether `src/` already includes the patched text is unchecked | Yes: 2,584 to 125,986 B each, dated 1994-05-12 | none | No | Three concern the front end: `fepsv` (14,142 B), `scsifep` (14,288 B), `tel` (33,026 B) |
| 8 | **KL1 compiler, assembler, loader, unloader** (inside `library`) | Yes: `src/library/compiler` 44 files / 17,943 lines; `assembler` 5 / 1,501; `loader` 14 / 5,468; `unloader` 9 / 2,338; `kbn` 5 / 1,036 | Yes, in `pimm_library360E.sav` | Manual `e-compiler.tex` | No | Needed to run any application that ships as source (all of IFS) |
| 9 | **FEP transport**: the SCSI processor-device link and its packets | PIMOS side yes: `src/bios/fep_module/scsi_fep.kl1` (628 lines), `src/bios/scsi/` (7 files / 2,539 lines), `protocol/scsi.prt`. FEP side no | FEP side yes: `pimscsi.ptf`, 114,074 B, 23 classes | none found | **Yes** (FEP end) | Class names READ: `scsi`, `scsi_handler`, `scsi_device`, `scsi_communicator`, `scsi_low_if`, `scsi_user_if`, `scsi_common_if`, `scsi_macro*`, `packet`, `packet32`, `pseudo_scsi`, `pseudo_scsi_handler`, `scsi_device_bus_management`, `scsi_device_interrupt_management`, `mbus_allocator`, `hmcb_log`, `scsi_error`, `scsi_load_test`, `scsi_dummy_handler`, `pseudo_scsi_log_dump`. Methods seen: `make_CDB`, `make_CDB6`, `inquiry`, `test_unit_ready`, `request_sense`, `receive_command`. On the Pseudo PIM/m the link is `pseudo_scsi` (no bus). Job: small once the IPL's exchange is disassembled; from `scsi_fep.kl1` (`send_packet`, `fep#packet_last`, `fep#packet_continued`) |
| 10 | **FEP services**: file, directory, window, timer, string_io, socket, login, remote variants | PIMOS side yes: `src/bios/fep_module/` (17 files / 6,396 lines: `file_dvc`, `dir_dvc`, `win_dvc`, `time_dvc`, `strio_dvc`, `soc_dvc`, `fep_dvc`, `fep_rcvr`, ...), `src/server/fep/` (30 files / 11,487 lines), command codes in `src/macro/pimos/pimos/pimos.vmac` (105 `fep#Name => Number` definitions, e.g. `fep#create_window => 104`, `fep#read_open => 201`, `fep#on_after => 303`, `fep#string_io => 600`, `fep#create_socket => 801`). FEP side no | FEP side yes: `pimfep.ptf`, 266,512 B, 47 classes | PIMOS manual `e-ioctrl.tex`, `e-strio.tex`, `e-io*.tex` (HELD); PIMOS 1.5 manual appendix on string I/O devices (PUBLIC) | **Yes** (FEP end). Second largest job | Section 1.1 below. Boot needs file read only; login and shell need window and timer; applications add string_io and sockets |
| 11 | **Atom, module, user, pipe, login, telnet, profiling, SCSI servers** | Yes: `src/server/{atom 3/636, module 8/2,242, user 13/2,346, pipe 5/1,123, login 23/10,111, telnet 5/2,291, profiler 8/1,861, scsi 2/1,065}` (files / lines) | Yes, in `pimm_server360E.sav` (845,940 B) | Manual `e-server*.tex` | No | These run on PIMOS, not on the FEP |
| 12 | **Configuration**: `pimos.conf`, `pimos.logins`, `pimos.groups`, `pimos.com`, `shell.com`, `login.com`, `init.com` | n/a (text, two-byte JIS) | Yes | Commented in the files (READ: `system(0,0,"login",login:go([{0,local,0},{0,tcpip,0}],[],off))`) | No | `init.com` starts `mpsimpc##csp_slave_csp_main`: a SIMPOS-side script, not a PIMOS one |
| 13 | **PIMOS internal file system** (disks on PIM, FGCS'92 pp. 278-285) | No (absent from `src/`; SECONDARY, `icot_databases.md` 6.4) | UNKNOWN | FGCS'92 paper; TM-1254 | Only if wanted | Not on the boot path. PIMOS reaches files through the FEP in this configuration |
| 14 | **Virtual machine and disk simulator** (`src/vm`: `vm`, `sim`, `DKS`, `DKSF`, `scsi_disk`) | Yes: 9 files / 4,413 lines | UNKNOWN whether in the object set | FGCS'92 PIMOS overview 4.5.4 (READ) | No | Test scaffolding of the file system effort |
| 15 | **ParaGraph**, performance meter, load-balancing library | Yes, including the FEP halves in ESP: `src_util/paragraph` 83 `.esp` / 18,261 lines; `pmeter` 7 `.esp`; `pmeter_c` 10 `.c` + 8 `.h`; `plib` 14 `.kl1`; `parallel` 3 `.kl1` + `balman.ps.Z` | Yes: `object/paragraph.ptf`, 1,020,476 B (compiled ESP) | FGCS'92 ParaGraph paper | FEP half: only if wanted | The only ESP source we hold |
| 16 | **Applications** (IFS, 49 PIMOS packages) | Not held; PUBLIC verified | none (source distributions) | per package | No | Need #8 running. Many also load an ESP part on the FEP |
| 17 | **SIMPOS and the ESP system** under the real FEP and CSP | No | No (the `.ptf` files are applications of it, not it) | ESP manuals PUBLIC (listed); SIMPOS manuals CITED-ONLY | Was "not planned"; **in the plan since 2026-11-23** at the owner's request, as a later track gated on finding SIMPOS (`pimos_roadmap.md` section 9). The host-side stand-ins for #3, #9, #10 remain the route to a running PIMOS | Section 4 |
| 18 | **Real PIM/m microcode and CSP** | No | No | TM-1213, TM-1021/1022, TM-850, TR-742, TR-799 | n/a | The Pseudo PIM/m is the nearest surviving thing; section 4 |

### 1.1 The FEP side in detail

**What `pimfep.ptf` is.** A SIMPOS package template file: compiled
ESP, package `pimfep`, built against `simpos` (header strings
`using_env simpos version lversion lib50 release`), 266,512 B, dated
1994-05-12. Its text is two-byte JIS and was extracted with
`asm/psdpim.py --text INSTALL.DIR/pimfep.ptf` (2,912 strings, 1,134
distinct). READ. The 47 class names in its header:

`as_pimos_device`, `as_pimos_login_requester`,
`as_pimos_string_io_device`, `closed_device_table`,
`fep_command_code_table`, `fep_device_table`, `fep_message_assembler`,
`fep_node_table`, `fep_scsi_output`, `message_converter`,
`net_spawn_user`, `network_process_name`, `nise_scsi_fep`,
`nise_scsi_stream`, `pimfep_message_log`, `pimfep_message_receiver`,
`pimfep_message_sender`, `pimos_directory`,
`pimos_fep_initiation_table`, `pimos_fep_superviser`, `pimos_file`,
`pimos_login_requester`, `pimos_remote_login_replier`,
`pimos_remote_login_server`, `pimos_remote_login_socket_table`,
`pimos_scsi_front_end`, `pimos_socket_manager`,
`pimos_socket_manager_table`, `pimos_socket_receiver`,
`pimos_standard_io_window`, `pimos_string_io_invoker`,
`pimos_tcpip_socket`, `pimos_timer`, `pimos_window`,
`pimos_window_editor`, `pimos_window_process`, `pimscsi_fep`,
`pseudo_scsi_fep`, `remote_pimfep_executor`, `remote_pimfep_invoker`,
`remote_stream`, `scsi_fep_macro`, `scsi_stream`, `simpos_user`,
`simpos_user_device`, `sline_fep`, `sline_scsi_stream`.

Reading of the names (this survey's, from the names and method lists
only; the compiled code was not read):

| Role | Classes | Method names seen in the class's string block |
|---|---|---|
| Top level and supervision | `pimos_scsi_front_end`, `pimos_fep_superviser`, `pimos_fep_initiation_table` | `set_fep_type`, `set_self_node_name`, `device_create`, `create_device`, `disassemble`, `assemble`, `get_device_id`, `report_to_server`, `all_device_end`, `shutdown_scsi`, `test_scsi`, `error_report_mode`; the supervisor has a log window and menus |
| Three transports | `pimscsi_fep` + `scsi_stream` (real SCSI), `pseudo_scsi_fep` (Pseudo PIM/m, same machine), `nise_scsi_fep` + `nise_scsi_stream`, `sline_fep` + `sline_scsi_stream` | `set_lun`, `receive_command`, `analyze_command`, `send_data`, `receive_data`, `inquiry`, `test_unit_ready`, `request_sence` [sic] |
| Message layer | `fep_message_assembler`, `message_converter`, `fep_command_code_table`, `pimfep_message_sender`, `pimfep_message_receiver`, `pimfep_message_log` | `get_command`, `divide_message`, `append_message`, `connection_flag`, `assemble`, `disassemble`, `pad_string`, `create_argument_list` |
| Devices | `as_pimos_device` (base), `pimos_file`, `pimos_directory`, `pimos_window` (+ `_process`, `_editor`, `pimos_standard_io_window`), `pimos_timer`, `as_pimos_string_io_device` + `pimos_string_io_invoker`, `pimos_tcpip_socket` + socket manager classes, `fep_device_table`, `closed_device_table` | file: `read_open`, `write_open`, `append_open`, `getb`, `putb`, `ungetb`, `flush`, `end_of_file`, `attributes`, `pathname`; directory: `make_directory`, `listing_all`, `delete`, `undelete`, `purge`, `expunge`, `kill`, wildcard forms; timer: `create_timer`, `on_at`, `on_after`, `get_count`, `get_date_time` |
| Login and remote FEPs | `pimos_login_requester`, `as_pimos_login_requester`, `pimos_remote_login_*`, `remote_pimfep_invoker`, `remote_pimfep_executor`, `remote_stream`, `fep_node_table`, `net_spawn_user`, `simpos_user`, `simpos_user_device` | |

The string block of `fep_command_code_table` is the command
vocabulary of the FEP protocol, in this order (READ): `normal
control_c attention continue abnormal aborted wake_up disconnected
reset next_attention close abort terminate create create_window
create_with_buffer get_max_size getl putb flush beep set_size
set_inside_size get_inside_size set_position_by_mouse set_position
get_position reshape_by_mouse reshape set_title get_title set_font
get_font select_buffer activate deactivate show hide clear buffer_name
file read_open write_open append_open directory make_directory getb
end_of_file pathname listing_all delete undelete purge expunge kill
timer create_timer get_count on_at on_after get_date_time string_io
create_string_io remote_window remote_file remote_timer
remote_string_io node_name ungetb attributes deleted_all creation_fail
all_device_end remote_echo_check device_end socket create_socket bind
listen accept connect set_socket_option so_debug so_reuseaddr
so_keepalive send_timeout receive_timeout connect_hostname
fep_attributes jiskanji sjis`. The numbers are not in the text; they
are on the PIMOS side, in `pimos.vmac`.

**What `pimscsi.ptf` is.** Package `pimscsi`, 114,074 B, 23 classes
(row 9 above) plus a `cmt` class (cartridge tape: `cmt_lun`,
`cmt_unit`). *(Note 2026-11-23: 24 class records in all, `cmt`
included, as `asm/ptfdump.py pimscsi` lists them and
`binary_reverse_engineering.md` §4.1 counts them: the two counts agree.)* It is the SIMPOS SCSI driver that makes the PSI a SCSI
*processor device*: it uses SIMPOS classes `interrupt_process`,
`as_interrupt_program`, `channel`, `mbus_allocator`. `pseudo_scsi`
has `header`, `tail`, `buffer1`, `buffer2` slots: the in-memory
stand-in for the bus on the Pseudo PIM/m.

**What PIMOS expects of the FEP** (READ in `pimos.tar.Z` unless
marked):

- A SCSI processor-type unit. The BIOS asks the SCSI handler for its
  `configuration`, keeps the `processor` entries, and connects each as
  a FEP (`scsi_fep.kl1`, `fep_config/2`, `connectFEP/4`). Boot target
  is unit 7, send LUN 0, receive LUN 1 (SECONDARY,
  `pimos_binaries.md`).
- Packets built by `send_packet/6` in an 8-bit string buffer, 32-bit
  fields written with `int32_to_str8`: bytes 0-3 device id, 4-7
  packet flag (`fep#packet_last` = 0, `fep#packet_continued` = 1),
  8-11 command code, 12-15 argument count N, then (from offset 16) N
  four-byte argument lengths, then the argument data (data starts at
  `16 + N*4`). A message of fewer than three elements is a 16-byte
  packet. `{-1,fep#terminate}` closes the link. Byte order within a
  field and the continuation rules are in `int32_to_str8` and
  `send_packet1..3` and were not transcribed.
- The whole code table, from `pimos.vmac` (READ; 105 definitions, 104 distinct names;
  checked 2026-11-23: the 105th is a commented-out repeat, line 74
  `%%      fep#putb => 111`, so 104 definitions outside comments, all distinct,
  which is the count `binary_reverse_engineering.md` §4.3 gives):
  status `nil 0, normal 1, eod 2, control_c 3, attention 3, continue
  4, abnormal 5, aborted 6, yes 7, no 8, wake_up 9, disconnected 10,
  end 11`; control `reset 50, next_attention 51, close 60, abort 70,
  terminate 80`; window `window 100, create 101, create_with_buffer
  102, get_max_size 103, create_window 104, getl 110, putb 111, flush
  112, beep 113, ungetb 114, set_size 120, set_inside_size 121,
  get_inside_size 122, set_position_by_mouse 123, set_position 124,
  get_position 125, reshape_by_mouse 126, reshape 127, set_title 130,
  get_title 131, set_font 132, get_font 133, select_buffer 140,
  activate 141, deactivate 142, show 143, hide 144, clear 145,
  buffer_name 146`; file `file 200, read_open 201, write_open 202,
  append_open 203, directory 204, make_directory 205, getb 210,
  end_of_file 220, pathname 221, attributes 222, listing 230, delete
  231, undelete 232, purge 233, deleted 234, expunge 235,
  next_filename 236, listing_all 237, deleted_all 238, kill 239,
  fep_attributes 240`; timer `timer 300, get_count 301, on_at 302,
  on_after 303, get_date_time 304, create_timer 310`; **`ipl 400`,
  `symbol 500`**; string I/O `string_io 600, create_string_io 601, io
  620`; remote `remote_window 700, remote_file 701, remote_timer 702,
  remote_string_io 703, remote_socket 704, node_name 710`; socket
  `socket 800, create_socket 801, bind 802, listen 803, accept 804,
  connect 805, set_socket_option 806, so_debug 807, so_reuseaddr 808,
  so_keepalive 809, send_timeout 810, receive_timeout 811,
  connect_hostname 812`; character codes `jiskanji 0, euc 1, jis 2,
  sjis 3`. Every name in the FEP-side `fep_command_code_table` string
  block above occurs here except `creation_fail`, `all_device_end`,
  `remote_echo_check`, `device_end`, which are FEP-internal or later
  additions. Conversely 17 PIMOS names are absent from that string
  block (`nil`, `eod`, `yes`, `no`, `window`, `listing`, `deleted`,
  `next_filename`, `io`, `ipl`, `symbol`, `remote_socket`, `end`,
  `packet_last`, `packet_continued`, `euc`, `jis`). `fep#ipl` (400,
  commented `ipl(?ipl,^st,?cdr)`) and `fep#symbol` (500) are defined
  and then used nowhere else in the released source: they look like
  the device classes of the IPL-time loader, whose modules have no
  source. Whether the IPL's file fetch uses them is the first thing
  the IPL disassembly should settle. *Settled 2026-11-20/23, against
  the inference above: the IPL does not use them.
  `binary_reverse_engineering.md` §1.4 finds no 400 or 500 in the
  decompiled `ipl*` and `scsi_fep_*` modules (the IPL fetches its
  files with `read_open` 201 and `getb` 210), §4.3 finds no class in
  `pimfep.ptf` that tests 400 or 500, and on 2026-11-23 the body of
  `ipl:boot0` ran on the reference model against `ref/pimm/fep.py`,
  which serves only 201, 210, 60 and 70 and raises on anything else,
  and the run completes (`python3 ref/pimm/ref_scsi.py`; our model of the FEP, and
  only the path `boot0` takes).*
- Device classes opened by code: `fep#window` family (`create_window
  => 104`), `fep#file` (`read_open => 201`), `fep#timer` (`on_after
  => 303`), `fep#string_io => 600` (`create_string_io => 601`),
  remote devices (`remote_string_io => 703`), `fep#socket`
  (`create_socket => 801`). Common status codes: `nil 0, normal 1, eod
  2, control_c/attention 3, continue 4, abnormal 5, aborted 6, yes 7,
  no 8, wake_up 9`.
- The servers started at boot: `fep_server`, `atom_server`,
  `module_server`, `user_server`, `pipe_server`, `profiling_server`,
  and under `:- switch(fep_interface). :- case(scsi).` the SCSI
  request server (SECONDARY, `icot_databases.md` 6.4; the switch was
  seen here in five files).
- Login: `pimos.conf` starts `login:go([{0,local,0},{0,tcpip,0}],[],
  off)`: a login server reachable from FEP 0 and over TCP/IP, so the
  FEP must offer a login requester window (`pimos_login_requester`)
  or the socket device.

**Size of the FEP job** (assessment). The real FEP is 47 + 23 ESP
classes in 380 KB of compiled code on top of SIMPOS windows, files
and network. A stand-in does not need the SIMPOS half. It needs the
packet codec (from `scsi_fep.kl1`), a device table, and one handler
per command actually issued: for R4/R5 the file read path only; for
R6 a line-oriented window and the timer; for applications string_io
and directory operations. The PIMOS clients (17 + 30 files, 17,883
lines) are the specification. The open part is the IPL-time
protocol, which has object code only. It is not wholly foreign to
the source, by predicate name (compared here with `asm/kbndis.py`;
names only, bodies not compared): `scsi_fep_module` shares 21 of its
38 predicate names with `bios/fep_module/scsi_fep.kl1`;
`scsi_fep_file` 11 of 17 with the device modules (`win_dvc.kl1`,
`time_dvc.kl1`, `strio_dvc.kl1` equally); `scsi_fep_general` 3 of 3
with the `*Rdvc.kl1` files; `scsi_fep_util` 3 of 6 with
`fep_util.kl1`; `ipl_scsi` almost none (its own `open_file`,
`wait_file_request`, `send_message`, `wait_command_status`). So the
IPL's packet layer is probably a variant of `scsi_fep.kl1`
(`msg_to_str8`, `padding`, `copy_str8_elements` are its additions)
and its file fetch is the unsourced part.

## 2. The software stack, machine by machine

Each line: what the layer was, evidence, status.

### 2.1 PSI (PSI-I, 1984; Mitsubishi, Oki)

| Layer | What | Evidence | Status |
|---|---|---|---|
| Firmware | KL0 interpreter in microcode | FGCS'84 "Hardware Design and Implementation of the Personal Sequential Inference Machine (PSI)" and "A Microprogrammed Interpreter ..." (`Museum/FGCS/FGCS84en-proc/84eANGC2-1.pdf`, `-2.pdf`; titles READ in the index, papers not read) | CITED-ONLY (no listing or binary found) |
| Console | CSP, the console processor | "コンソール・プロセッサ(CSP)操作説明書 : 逐次型推論マシンPSI説明書", ICOT 1985.4, note "MP7003-1" (CiNii record `BN13167682`, READ) | Manual: one catalogued copy, JAIST library. Software: not found |
| OS | SIMPOS: kernel, supervisor, I/O medium systems (window, file, network), programming systems (coordinator, debugger/interpreter, editor/transducer, library) | Yokoi, Uchida et al., "Sequential Inference Machine: SIM - Its Programming and Operating System", FGCS'84 (`84eR&D-5.pdf`, READ by OCR) | CITED-ONLY. Manuals: three 1985 SIMPOS manuals catalogued at JAIST (SECONDARY) |
| Language | ESP (compiled to KL0), "Unique Features of ESP" FGCS'84 | ESP manuals at `ifs/manuals/esp/` (4 archives, 167K-585K; listing READ) | Manuals PUBLIC (listed). Compiler and runtime: part of SIMPOS, not found |
| Applications | 16 IFS packages are ESP applications for SIMPOS (12, 15, 19, 21, 23, 28, 29, 40, 41, 45-50, 52) | abstract pages (READ) | PUBLIC, but not runnable without SIMPOS or Common ESP |

### 2.2 PSI-II (1986-87)

| Layer | What | Evidence | Status |
|---|---|---|---|
| Firmware | KL0 microcode; PSI-II firmware papers TM-261, TM-353, TM-354, TM-212, TM-213 | titles only (SECONDARY, `literature_gaps.md` section 9) | Papers PUBLIC (listed). Microcode: not found |
| OS | SIMPOS (later versions) | "Basic PSI/SIMPOS Operating Manual (1),(2)", "Basic System Administration Manual for PSI/SIMPOS Systems" are cited by the PIMOS 3.0 primer (READ, `primer25.tex` line 70) | Manuals CITED-ONLY |
| KL1 system | **Pseudo Multi-PSI**: KL1 firmware beside KL0, CSP program `mpsicsp##pseudo_csp_main_program`, firmware file `pmpsi:kl1kp.kbn`, patch `pmpsi:kl1pat.com` | primer (READ, lines 96-127, 385-391); `pimosobj` `INSTALL` (READ): "machines: PSI-II or PSI-UX / systems: Pseudo PIM/M system or Psuedo Multi-PSI system" | The PSI-II firmware files the primer names (`kl1kp.kbn`, `kl1pat.com`, the `.mbn` images) are not in IFS and were not found. The released package is for PSI-III; IFS newsletter E05 (READ) calls that one too a "Pseudo Multi-PSI" for which "a PSI-III is required", and its `login.com` menu entry is "Pseudo Multi-PSI" |
| As front end | A PSI-II is the FEP and CSP host of a Multi-PSI ("connected with icpsi383 (which is also PSI-II machine) as FEP") | primer (READ, line 436) | software not found |

### 2.3 PSI-III, sold as PSI/UX

| Layer | What | Evidence | Status |
|---|---|---|---|
| Hardware relation | "In Japan, the PSI-III is commercially available as the PSI/UX from Mitsubishi Electric" | `psdpim/README` (READ) | |
| Host arrangement | SIMPOS files live under a UNIX path: "copy ./PMPSI.DIR/syspsi, sysinit, sysidat to /usr/psi/simpos/csp as unix files on PSI-III"; `boot.init` loads `/usr/psi/pimos/kl1/pimm.MEkbn` | `psdpim/INSTALL`, `boot.init` (READ) | That PSI/UX runs SIMPOS beside UNIX is an inference from these paths |
| Firmware | "PMPSI.DIR  KL0 and KL1 firmware": `pimm.MEkbn` 506,624 B, `syspsi` 262,400 B, `sysinit` 66,544 B, `sysidat` 8,576 B. KL0 and KL1 microprograms are "dynamically swapped" | `README`, listing (READ); IFS abstract 003 (READ) | **HELD, binary only.** Which of the four files is the KL0 firmware is not established. *(Note 2026-11-23: narrowed, not proven. `INSTALL` sends `syspsi`, `sysinit`, `sysidat` to SIMPOS's `/usr/psi/simpos/csp` and `boot.init` loads `pimm.MEkbn` as the KL1 `impl` file, so the KL0 firmware is the `sys*` trio. Within it, `syspsi` is probably the control store: 32,768 eight-byte records, the full 32K x 64-bit WCS, and its words `0..57ff` equal image 1 of `pimm.MEkbn` (`pseudo_pimm_microcode.md` §2). `sysidat` is the KL0 decode table (`binary_reverse_engineering.md` §4.2). No document names the file's role; a PSI-III document or the CSP's micro loader read out of `pimmcsp.ptf` would settle it.)* `pimm.MEkbn` is partly decoded (`pseudo_pimm_microcode.md`) |
| Console | Pseudo PIM/m CSP: `pimmcsp.ptf` (281 classes: `csp_ipl`, `csp_micro_loader`, `csp_boot_menu`, `csp_goal_record_inspector`, `csp_susp_record_inspector`, `csp_shoen_traverse`, `pseudo_memory`, `pseudo_pe_process`, `random_scheduler`, `pimos_file_manager`, `pimos_timer_manager`, ...); `pimmutil.ptf` (51 by class record, corrected 2026-11-23 from 50: `micro_reverse_assembler`, `micro_field_modifier`, `kl1_step`, `firm_utility`, `h_meter`, `csp_param_file_maker`, ...); `mpsicspR.ptf` (30: `remote_csp*`, `csp_command_parser`, `pe_registers`, `kl1_tag`) | names READ | **HELD, compiled ESP only** |
| Front end | `pimfep.ptf`, `pimscsi.ptf` | section 1.1 | **HELD, compiled ESP only** |
| OS | SIMPOS for PSI-III; the Librarian loads `.ptf` files | `INSTALL` (READ) | not found |
| Catalogue contradiction | IFS abstract 003 says "Language: ESP, microprogram / Source Code: 2.5 MB"; the archive has no source of either | READ both | recorded in section 7 |

### 2.4 Multi-PSI (V1, then V2 of up to 64 PSI-II processors)

| Layer | What | Evidence | Status |
|---|---|---|---|
| Firmware | KL1-B interpreted by microcode; boot images `.mbn` (CLEAR, INIT, IMPL), KL1 kernel `.kbn`, patch `.com` | primer CSP auto-boot panel (READ, lines 385-391); TR-715, TM-662 and others (SECONDARY) | **Not found.** The `.mbn` files are not in any archive |
| Console | "Multi-PSI CSP" on the FEP PSI: Monitor Panel, CSP Command Window, Console Panel; "REMOTE CSP" from another PSI | primer (READ) | Software not found (the held `mpsicspR.ptf` is the remote half). "Multi-PSI/V2 Console System (CSP) Operating Manual" CITED-ONLY |
| OS | PIMOS: "The first version of PIMOS was implemented on Multi-PSI in 1988"; earlier development used "a sequential implementation" (PDSS) | Chikayama, "Operating System PIMOS and Kernel Language KL1", FGCS'92 (`92eRERR-2.pdf`, READ by OCR) | PIMOS 1.5 manual PUBLIC (listed: `ifs/manuals/pimos/man15.ps.Z`, 322K); PIMOS 1.x-2.5 code not found; "PIMOS 2.5 Manual" CITED-ONLY (primer cites it 19 times) |
| Boot tooling | "CAL" cross system that produced the `.kbn` up to PIMOS 2.5 | Japanese PIMOS 3.0 manual 6.1 (SECONDARY, Appendix D) | Not found |
| I/O | "Earlier versions of PIMOS operating on ... Multi-PSI left all the external input and output to its I/O front-end processor, PSI" | FGCS'92 PIMOS paper 4.4 (READ) | |

### 2.5 PIM/m (Mitsubishi, 1991)

| Layer | What | Evidence | Status |
|---|---|---|---|
| Firmware | KL1 microcode, converted from Multi-PSI/V2; same scheduling policy ("the kernel language implementation on the system used the identical scheduling policy as the Multi-PSI system") | FGCS'92 PIMOS paper section 5 (READ); TR-742, FGCS'92 pp. 425-435 (HELD) | **Not found.** Nearest survivor: the Pseudo PIM/m microcode for PSI-III (HELD binary) |
| Console / maintenance | CSP for PIM/m | TM-1213 "PIM/m maintenance architecture and CSP" (SECONDARY) | Paper PUBLIC; software not found |
| Front end | PIM/m front-end processor; SCSI to processors | TM-1021, TM-1022 (SECONDARY); FGCS'92 PIMOS paper 4.4 (READ) | FEP software: `pimfep`/`pimscsi` (HELD binary) are the PSI-III-side packages |
| OS | PIMOS 3.x: "In 1991 ... PIM/m and its KL1 implementation was made available ... After revising the low-level I/O mechanism to fit the system to this new platform, PIMOS began working almost immediately" | same (READ) | **HELD**: source 3.600, objects "360E" |
| File system | on-PIM file system over SCSI disks | FGCS'92 pp. 278-285 (SECONDARY) | not in the release |

### 2.6 PIM/p, PIM/c, PIM/i, PIM/k

| Layer | What | Evidence | Status |
|---|---|---|---|
| KL1 runtime | VPIM, in PSL, common to all four; ran first as "an emulator of PIM running on a commercially available parallel processor" | IFS abstract 002 (CATALOGUE); FGCS'92 PIMOS paper (READ) | **HELD** (`vpim.tar.Z`: `src/` basics 28, functions 77, interpreter 33, primitives 4, structures 48 entries; `DOCUMENT/` with TM-1044 in Japanese). Read-only: no PSL translator, headers or build files (SECONDARY, `MANIFEST.md`) |
| PSL translator, per-machine back ends, machine microcode (PIM/c), native code generators (PIM/p, /i, /k) | TM-1044; per-machine TRs (SECONDARY) | **Not found** |
| OS | PIMOS, ported unchanged | FGCS'92 PIMOS paper (READ) | same source; per-machine BIOS variants not identified in the release |

### 2.7 UNIX: the ports and descendants

| System | What | Status |
|---|---|---|
| PDSS V2.52.20 | KL1-B emulator in C, compiler in KL1 and Prolog, Micro PIMOS (`mpimos/`, 35 modules as `.kl1`/`.asm`/`.sav` triples), Emacs interface (`emacs/`, 6 files), 80 tests, manual | **HELD** (IFS 1) |
| pkl1 | experimental KL1-to-C (1993) | **HELD** (IFS 72) |
| KLIC | 1.x (IFS 78), 2.002 (IFS 85), 1.500/2.000/2.001 (`klic-old/`), 3.001 (`KLIC-New/`), 3.002 (`pub/klic/v3.0/`), later 3.003-3.014 outside the archive | 2.002 **HELD**; the rest PUBLIC (3.001 and older listed here; later ones SECONDARY, Appendix D item 7) |
| Common ESP (CESP) 3.3 | ESP on UNIX (SUN4). "CESP is not part of the ICOT Free Software"; requests to `cesp-request@air.co.jp` (AI Language Research Institute) | IFS newsletter E01 and E06 (READ). **Not found**; commercial |
| KLIC ports of applications | Quixote (79), Kappa (87), GDCC (88), MGTP (90-92), alignment programs (93-95), new HELIC-II (100), D-Pool (86) | PUBLIC verified (section 3) |

### 2.8 Languages, tools and applications across the machines

| Item | Ran on | Where it survives |
|---|---|---|
| KL0 | PSI family machine language | no implementation found; KL0 built-in predicate manual (1985) catalogued at JAIST (SECONDARY) |
| ESP | SIMPOS | manuals PUBLIC; system not found; 83 + 7 `.esp` source files HELD in `pimos/src_util` |
| KL1 compilers | PIMOS's own (KL1-B for PIM/m and Multi-PSI): HELD source and object. PDSS's: HELD. KLIC's KL1-to-C: HELD. VPIM-side compilers for PIM/p, /c, /i, /k: not found |
| PSL | VPIM implementation language | translator not found |
| A'UM-90 | UNIX | IFS 5, PUBLIC verified (`aum-1.2c.tar.Z`, 1,118,529 B) |
| AYA | PIMOS 3.5 and later | IFS 73, PUBLIC verified |
| GDCC, CAL, CHAL, P-CHAL, Consort | PIMOS (18, 17, 63), SIMPOS (19, 15), CESP (14), KLIC (88) | PUBLIC verified |
| Quixote, micro-Quixote, Kappa-II, Kappa-P, Helios | see `icot_databases.md` | PUBLIC verified (11, 12, 13, 79, 80, 87, 89) |
| PIMOS programming environment | listener, inspector, tracer (`src/debugger`: 116 files, 28,392 lines), shell, ParaGraph, profiler | HELD |
| Other KL1 tools | ExReps (6), kl1graph (7), strategy shell (8), load distribution library (74), PerformanceMonitor (62), MENDELS ZONE (61) | PUBLIC verified |
| Theorem proving | MGTP (22, 81, 82, 90, 91, 92), Argus/V (31), BMTP (24) | PUBLIC verified |
| Legal reasoning | HELIC-II (54), new HELIC-II (100) | PUBLIC verified |
| Genetic information processing | 55, 56, 68, 75, 76, 77, 83, 84, 93-99 | PUBLIC verified |
| LSI CAD | 57, 58, 59, 65, 66, 69, 70 | PUBLIC verified |
| Go | GOG sequential (52, ESP), parallel (53, KL1 + ESP) | PUBLIC verified |
| Natural language | 33-51 | PUBLIC verified |
| Databases | `icot_databases.md` | |

## 3. The ICOT Free Software catalogue, complete

Sources, all READ on 2026-11-20: the catalogue index
`AIST/Museum/IFS/abst/ifs-catalogue.html` (100 numbered titles); the
100 abstract pages `AIST/Museum/IFS/abst/NNN.html` (each HTTP 200;
machine, environment, language and "Source Code" size are theirs);
`AIST/ifs/README` (last modified 15-Apr-1996; directory map and change
log); the UEDA directory listings under `ifs/` (138 directories
outside `contract-research/` walked).

**Link check.** Every file link on the 100 abstract pages was
requested from AIST with a HEAD and then a 4-byte ranged GET: 156
links, 156 answered 200; 116 distinct files begin `1f 9d` (compress)
or `1f 8b` (gzip), the other 40 are README, INSTALL and manual text
files. The byte counts in the table are the Content-Length headers,
not the catalogue's bracketed sizes, which are sometimes wrong
(`icot_databases.md` section 7). No archive other than the eight
marked HELD was downloaded or opened. `Z` = compress, `gz` = gzip.
*Corrected 2026-11-23: true when this table was made. Later on
2026-11-20 every file in the table was fetched as data, nothing
unpacked or run (`nonlocal/IFS_MANIFEST.md`), so every row is now held,
under `nonlocal/ifs/<path>`, except the eight marked HELD, which stay
in `nonlocal/` itself. The HELD marks are left as they were.*
Paths are under `ifs/`.

| No. | Name | Machine / environment | Language | "Source Code" per page | Files: Content-Length bytes (size printed on the page; HTTP status, type) |
|---|---|---|---|---|---|
| 1 | KL1 Programming Environment on Unix: PDSS | UNIX machine / UNIX, (GNU Emacs) | C, KL1, (Prolog, Emacs Lisp) | 3 MB | `symbolic-proc/unix/pdss.tar.Z` 2564373 B (page: 2,564K; 200, Z) **HELD** |
| 2 | Parallel and Distributed KL1 Language Processor: VPIM | PIM, Multi-PSI / PIMOS | PSL | 4.7 MB | `symbolic-proc/unix/vpim.tar.Z` 1761111 B (page: 1,761K; 200, Z) **HELD** |
| 3 | KL1 Pseudo Parallel System for PSI-III | PSI-III / SIMPOS | ESP, microprogram | 2.5 MB | `symbolic-proc/pim-psi/psdpim.tar.Z` 1354121 B (page: 1,354K; 200, Z) **HELD** |
| 4 | OS for Parallel Inference Machines: PIMOS | PIM, Multi-PSI / SIMPOS | KL1 | 5.5 MB | `symbolic-proc/pim-psi/pimos.tar.Z` 2932865 B (page: 2,933K; 200, Z) **HELD**<br>`symbolic-proc/pim-psi/pimosobj.tar.Z` 2631847 B (page: 2,632K; 200, Z) **HELD**<br>`symbolic-proc/pim-psi/pimosman.tar.Z` 592865 B (page: 593K; 200, Z) **HELD**<br>`symbolic-proc/pim-psi/pimosman.ps.Z` 866355 B (page: 866K; 200, Z) |
| 5 | A Concurrent Object-oriented Language: A'UM-90 | UNIX machine / UNIX | A'UM-90 | 3MB | `symbolic-proc/unix/aum-1.2c.tar.Z` 1118529 B (page: 1,119K; 200, Z)<br>`symbolic-proc/unix/aum-pat-1.2b.Z` 2860 B (page: 3K; 200, Z) |
| 6 | Experimental Reflective Programming System: ExReps | PSI / PIMOS, pseudo Multi-PSI | KL1 | 2.0 MB | `symbolic-proc/pimos/exreps.tar.Z` 132021 B (page: 132K; 200, Z) |
| 7 | Programming Environment for KL1 with Program Visualization | PSI / SIMPOS, pseudo multi PSI | KL1 | 2 MB | `symbolic-proc/pimos/kl1graph.tar.Z` 198627 B (page: 199K; 200, Z) |
| 8 | Strategy Management Shell | PIM / PIMOS 3.0 | KL1, ESP | 400 KB | `symbolic-proc/pimos/strtgysh.tar.Z` 429686 B (page: 430K; 200, Z) |
| 9 | CLP Language: cu-Prolog | UNIX machine / UNIX | cu-Prolog | 0.4 MB | `kbms-clp/unix/cuprolog/README` 3263 B (200, txt)<br>`kbms-clp/unix/cuprolog/CHANGES` 2720 B (200, txt)<br>`kbms-clp/unix/cuprolog/INSTALL` 2232 B (200, txt)<br>`kbms-clp/unix/cuprolog/cupdoc.tar.gz` 136474 B (200, gz)<br>`kbms-clp/unix/cuprolog/cupsrc.tar.gz` 211847 B (page: 108K; 200, gz) |
| 10 | Dynamical Programming DP | Sparc, PIM / UNIX, PIMOS | C, KL1 | 250KB, 500KB | `kbms-clp/unix/dp.tgz` 193556 B (page: 194K; 200, gz) |
| 11 | Knowledge Representation Language: QUIXOTE | Multi-PSI / PIMOS | QUIXOTE | 3 MB | `kbms-clp/pimos/quixote.tar.gz` 1447226 B (page: 1,447K; 200, gz) |
| 12 | Nested Relational Database Management System: Kappa-II | PSI / SIMPOS | ESP | 12 MB | `kbms-clp/simpos/kappa2.tar.Z` 5710659 B (page: 5,711K; 200, Z)<br>`kbms-clp/simpos/kappa2d1.tar.Z` 5332175 B (page: 5,332K; 200, Z)<br>`kbms-clp/simpos/kappa2d2.tar.Z` 4857043 B (page: 4,857K; 200, Z)<br>`kbms-clp/simpos/kappa2d3.tar.Z` 9995265 B (page: 9,995K; 200, Z) |
| 13 | Parallel Database Management System:Kappa-P | PIM / PIMOS 3.45 | KL1 | 6MB | `kbms-clp/pimos/kappa-p.tar.Z` 1897310 B (page: 1,897K; 200, Z) |
| 14 | Constraint Logic Programming Language: CAL in CESP | UNIX machine / UNIX, CESP, GMP | CAL in CESP | 1 MB | `kbms-clp/cesp/cal-cesp.tar.Z` 314597 B (page: 315K; 200, Z) |
| 15 | Hierarchical Constraint Logic Programming Language: CHAL | PSI / SIMPOS | CHAL | 61 KB | `kbms-clp/simpos/chal.tar.Z` 76001 B (page: 76K; 200, Z) |
| 16 | Robot Design Support System | Multi PSI / PIMOS | GDCC | 33 KB | `kbms-clp/pimos/robot.tar.Z` 40243 B (page: 40K; 200, Z) |
| 17 | Hierarchical Constraint Parallel Solver: P-CHAL | Multi-PSI / PIMOS | GDCC | 17 KB | `kbms-clp/pimos/p-chal.tar.Z` 24422 B (page: 24K; 200, Z) |
| 18 | Parallel Constraint Logic Programming System: GDCC | Multi-PSI / PIMOS | KL1 | 1.2 MB | `kbms-clp/pimos/gdcc.tar.gz` 404964 B (page: 405K; 200, gz) |
| 19 | Constraint Logic Programming Language: CAL in ESP | PSI / SIMPOS | CAL in ESP | 1.3 MB | `kbms-clp/simpos/cal-esp.tar.Z` 722127 B (page: 722K; 200, Z) |
| 20 | Voronoi Diagram Construction Program | Multi-PSI / PIMOS | GDCC | 260 KB | `kbms-clp/pimos/voronoi.tar.Z` 96449 B (page: 96K; 200, Z) |
| 21 | Knowledge Verification System: KNOV | PSI-II / SIMPOS | ESP | 3 MB | `kbms-clp/simpos/knov.tar.Z` 243661 B (page: 244K; 200, Z) |
| 22 | Parallel Model Generation Theorem Prover: MGTP | PIM / PIMOS | KL1 | 2 KB | `solver-prover/pimos/MGTP/README` 492 B (200, txt)<br>`solver-prover/pimos/MGTP/mgtp.tgz` 20229 B (page: 20K; 200, gz) |
| 23 | Program Generation System: PAPYRUS | PSI / SIMPOS | ESP | 4 MB | `solver-prover/simpos/papyrus.tar.Z` 3781351 B (page: 3,781K; 200, Z) |
| 24 | Boyer-Moore Theorem Prover: BMTP | UNIX machine / UNIX | SICSTUS Prolog | 400 KB | `solver-prover/unix/bmtp.tar.Z` 98661 B (page: 99K; 200, Z) |
| 25 | Forward Chaining Inference System: KORE/IE | UNIX machine / UNIX | Quintus Prolog | 113 KB | `solver-prover/unix/kore-ie.tar.Z` 79379 B (page: 79K; 200, Z) |
| 26 | Functional Language: QUTE | DEC2060 / TOPS20 | QUTE | 4 KB | none: the page prints "[??K]" and links no file |
| 27 | SAM - A Symbolic and Algebraic Manipulation System on PSI | PSI-II / SIMPOS | ESP | 600 KB | none: the page prints "[??K]" and links no file |
| 28 | Reasoning System: EUODHILOS | PSI / SIMPOS | ESP | 1.7 MB | `solver-prover/simpos/euod.tar.Z` 272988 B (page: 273K; 200, Z) |
| 29 | Fuzzy Clustering Tool | PSI-II / SIMPOS | ESP | - | `solver-prover/simpos/fuzclust.tar.Z` 406058 B (page: 406K; 200, Z) |
| 30 | Parallel Problem Solving System | Multi-PSI / PIMOS | KL1 | 0.3 MB | `solver-prover/pimos/ppss.tar.Z` 71957 B (page: 72K; 200, Z) |
| 31 | Argus Verification System: Argus/V | Multi-PSI / PIMOS, SIMPOS | KL1, ESP | 1 MB | `solver-prover/pimos/argus-v.tar.Z` 391868 B (page: 392K; 200, Z) |
| 32 | A Structure-Mapping Engine: SME | PIM/m, Multi-PSI / PIMOS 3.4, SIMPOS | KL1 | 0.44 MB | `solver-prover/pimos/sme.tar.Z` 179759 B (page: 180K; 200, Z) |
| 33 | Morphological Dictionary for Japanese | independent / independent | C | 3.5MB | `natural-lang/unix/morphdic.tar.gz` 1154303 B (page: 1,154K; 200, gz) |
| 34 | LUG & Grammar rules(A grammar descriptive framework and the grammar rules written in the form) | Independent / Independent | Prolog | 1.8 MB | `natural-lang/unix/lug.tar.Z` 831995 B (page: 832K; 200, Z)<br>`natural-lang/unix/lug-fse.tar.Z` 1497881 B (page: 1,498K; 200, Z)<br>`natural-lang/unix/lug-man.tar.Z` 1543118 B (page: 1,543K; 200, Z) |
| 35 | Dependency Grammar for Japanese:RDG | UNIX machine / UNIX | SICStus Prolog | 80 KB | `natural-lang/unix/rdg.tar.Z` 113197 B (page: 113K; 200, Z) |
| 36 | A Sentence Retrieval Tool: KWIC(on CESP) | SPARC / UNIX, Motif/Nemacs | CESP | 4 MB (including Text DB) | `natural-lang/cesp/kwic-cesp.tar.Z` 1278705 B (page: 1,279K; 200, Z) |
| 37 | Morphological Analyzing Program | UNIX machine / UNIX | CESP | 0.3 MB (Without dictionary) | `natural-lang/cesp/morphana.tar.Z` 402305 B (page: 402K; 200, Z) |
| 38 | Grammar Writing Support System: LINGUIST | UNIX machine / UNIX | CESP | 1.5 MB | `natural-lang/cesp/linguist.tar.Z` 557373 B (page: 557K; 200, Z) |
| 39 | Parallel Parsing System: PAX | PSI, Multi-PSI / SIMPOS, PIMOS | ESP, KL1 | 1.5 KB | `natural-lang/pimos/pax.tar.Z` 74787 B (page: 75K; 200, Z) |
| 40 | Linguistic Knowledge Description Language | PSI-II / SIMPOS | ESP | 2.5 MB | `natural-lang/simpos/cil.tar.gz` 986072 B (page: 986K; 200, gz) |
| 41 | The Syntactic Analyzer | PSI / SIMPOS | ESP | 1.5 MB | `natural-lang/unix/synana.tar.Z` 167303 B (page: 167K; 200, Z) |
| 42 | Experimental System for Argument Text Generation: Dulcinea | Multi-PSI or pseudo-PIM/m / PIMOS | KL1 | 2MB | `natural-lang/pimos/dulcinea.tar.Z` 872997 B (page: 873K; 200, Z) |
| 43 | Japanese Sentence Generator | UNIX machine / UNIX | CESP, SICStusProlog | 1.1 MB | `natural-lang/unix/jpnsgen.tar.Z` 389856 B (page: 390K; 200, Z) |
| 44 | A Sentence Dividing Tool | UNIX machine / UNIX | CESP | 85 KB | `natural-lang/cesp/sdiv.tar.Z` 81295 B (page: 81K; 200, Z) |
| 45 | Summarizing Support System | PSI / SIMPOS | ESP | 3 MB | `natural-lang/simpos/sum.tar.Z` 195947 B (page: 196K; 200, Z) |
| 46 | A Support System for Generating Controled Jpanese Text and Semantic Structures: ICOTEXT | PSI-II / SIMPOS | ESP | 4MB | `natural-lang/simpos/icotext.tar.Z` 523584 B (page: 524K; 200, Z) |
| 47 | A Sentence Retrieval Tool: KWIC(on ESP) | PSI-II / SIMPOS | ESP | 11 MB (including Text DB) | `natural-lang/simpos/kwic-esp.tar.Z` 1923883 B (page: 1,924K; 200, Z)<br>`natural-lang/simpos/kwic-esp-002.tar.Z` 2052449 B (page: 2,052K; 200, Z) |
| 48 | Experimental Dialogue System with Pragmatics-based Utterance Selection Mechanism | PSI / SIMPOS | ESP | 1.0 MB | `natural-lang/simpos/utter.tar.Z` 550256 B (page: 550K; 200, Z) |
| 49 | Text Structure Analysis System | PSI / SIMPOS | ESP | 5.0 MB | `natural-lang/simpos/txtstrct.tar.Z` 316355 B (page: 316K; 200, Z) |
| 50 | An Experimental Discourse Analyzer | PSI-II / SIMPOS | ESP | 1.0 MB | `natural-lang/simpos/disc.tar.Z` 345165 B (page: 345K; 200, Z) |
| 51 | A Parallel Processing Based Natural Language Analysis Tool: Laputa | Multi-PSI / PIMOS 3.1 | KL1 | 8.0 MB | `natural-lang/pimos/laputa.tar.Z` 536877 B (page: 537K; 200, Z) |
| 52 | Go Playing Game System "GOG"(The Sequential Version) | PSI / SIMPOS | ESP | 1.5 MB | `exper-apps/simpos/gog-esp.tar.Z` 712127 B (page: 712K; 200, Z) |
| 53 | Go Playing Game System "GOG"(The Parallel Version) | Multi-PSI / PIMOS, SIMPOS | KL1, ESP | 1.5 MB | `exper-apps/pimos/gog-kl1.tar.Z` 833891 B (page: 834K; 200, Z) |
| 54 | A Parallel Leagal Reasoning System: HELIC-II | PIM, Multi-PSI / PIMOS | KL1 | 1.7 MB | `exper-apps/pimos/helic2.tar.Z` 775279 B (page: 775K; 200, Z) |
| 55 | Multiple Sequence Alignment by 3-dim DP | PIM / PIMOS, SIMPOS | KL1, ESP | 0.5 MB | `exper-apps/pimos/aligndp.tar.Z` 93019 B (page: 93K; 200, Z) |
| 56 | Multiple Sequence Alignment by Parallel Simulated Annealing | PIM / PIMOS, SIMPOS | KL1, ESP | 0.4 MB | `exper-apps/pimos/alignsa.tar.Z` 98269 B (page: 98K; 200, Z) |
| 57 | Standard Cell Placement Experimental System | Multi-PSI, PIM / PIMOS, SIMPOS | KL1, ESP | 750KB(KL1) | `exper-apps/pimos/celplace.tar.Z` 261658 B (page: 262K; 200, Z) |
| 58 | LSI Routing Program | Multi-PSI, PIM / PIMOS, SIMPOS | KL1, ESP | 0.5 MB | `exper-apps/pimos/lsirout.tar.Z` 89311 B (page: 89K; 200, Z) |
| 59 | Parallel Logic Simulator | Multi-PSI, PIM / PIMOS, SIMPOS | KL1, ESP | 0.4 MB | `exper-apps/pimos/logisim.tar.Z` 2122305 B (page: 2,122K; 200, Z) |
| 60 | Group Problem Solving System for Task Allocation Problems | Multi-PSI / PIMOS, SIMPOS | KL1, ESP | 1.0 MB | `exper-apps/pimos/gpsstap.tar.Z` 293448 B (page: 293K; 200, Z) |
| 61 | A Concurrent Program Development System: MENDELS ZONE | Multi-PSI / PIMOS, SIMPOS | ESP, KL1 | 10 MB | `exper-apps/pimos/mendels.tar.Z` 1000839 B (page: 1,001K; 200, Z) |
| 62 | KL1 Execution Data Collecting Tool: PerformanceMonitor | pseudo Multi-PSI / PIMOS | KL1 | 200KB | `exper-apps/pimos/pmonitor.tar.Z` 377005 B (page: 377K; 200, Z) |
| 63 | Combined Constraint solver: Consort | Multi-PSI / PIMOS | KL1 | 1.9 MB | `exper-apps/pimos/consort.tar.Z` 374917 B (page: 375K; 200, Z) |
| 64 | Design support system based on qualitative reasoning: Desq | MultiPSI / PIMOS, SIMPOS | ESP, KL1 | 4.0 MB | `exper-apps/pimos/desq.tar.Z` 793847 B (page: 794K; 200, Z) |
| 65 | Experimental Parallel Hierarchical Recursive Layout System: Co-HLEX | Multi-PSI, PIM / PIMOS | KL1 | 3.5 MB | `exper-apps/pimos/cohlex.tar.Z` 397388 B (page: 397K; 200, Z) |
| 66 | A Cooperative Logic Design Expert System | PIM, Multi-PSI / PIMOS 3.0, | KL1 | 3 MB | `exper-apps/pimos/colodex.tar.Z` 491641 B (page: 492K; 200, Z) |
| 67 | Experimental Adaptive Model-based Diagnostic System | Multi-PSI / PIMOS | KL1 | 2.4 MB | `exper-apps/pimos/examds.tar.Z` 1047721 B (page: 1,048K; 200, Z) |
| 68 | Experimental Sequence Analysis System | PIM / PIMOS | KL1 | 200 KB | `exper-apps/pimos/seqanal.tar.Z` 168832 B (page: 169K; 200, Z) |
| 69 | Case-Based Circuit Design Support System | PIM/m, Multi-PSI / PIMOS 3.4 | KL1 | 6 MB | `exper-apps/pimos/cbcdss.tar.Z` 1049915 B (page: 1,050K; 200, Z) |
| 70 | High Level Synthesis System: RODIN | Multi-PSI / PIMOS V3.4 | KL1 | 3.5 MB | `exper-apps/pimos/rodin.tar.Z` 902970 B (page: 903K; 200, Z) |
| 71 | A Diagnostic and Control Expert System based on a Plant Model | Multi-PSI / PIMOS 3.01 | KL1 | 3.1 MB | `exper-apps/pimos/mmi.tar.Z` 421351 B (page: 421K; 200, Z) |
| 72 | Portable KL1 processing system:experimental version | UNIX machine / UNIX | C, Prolog | 0.1 MB | `symbolic-proc/unix/pkl1.tar.Z` 130871 B (page: 131K; 200, Z) **HELD** |
| 73 | Process oriented programming language AYA | Multi-PSI, PIM/m / PIMOS V3.5 and later | KL1 | 50 KB | `symbolic-proc/pimos/aya.tar.Z` 235617 B (page: 236K; 200, Z) |
| 74 | KL1 Load Distribution Library | PIM / PIMOS | KL1 | 0.1MB | `symbolic-proc/pimos/ldlib.tar.Z` 123055 B (page: 123K; 200, Z) |
| 75 | Multiple Sequence Alignment by Parallel Iterative Aligner | PIM/m / PIMOS | KL1 | 0.42 MB | `exper-apps/pimos/multialign.tar.Z` 178138 B (page: 178K; 200, Z) |
| 76 | Intelligent Refiner for Multiple Sequence Alignment | PIM/m / UNIXS, PIMOS | KL1, C | 1.73 MB | `exper-apps/pimos/editalign.tar.Z` 770441 B (page: 770K; 200, Z) |
| 77 | Protein Structure Visualization System: Protein-View | SGI IRIS / IRIX | GNU C++ | 1.6 MB | `exper-apps/unix/proview/README` 3201 B (200, txt)<br>`exper-apps/unix/proview/DOC` 958 B (200, txt)<br>`exper-apps/unix/proview/DOC.pia` 19224 B (200, txt)<br>`exper-apps/unix/proview/INSTALL` 979 B (200, txt)<br>`exper-apps/unix/proview/proview.tgz` 645939 B (page: 646K; 200, gz) |
| 78 | KLIC version 1: An implementation of KL1 for general purpose computers | UNIX machine / UNIX | C, Prolog | 0.4 MB | `symbolic-proc/unix/klic/README1` 874 B (200, txt)<br>`symbolic-proc/unix/klic/readme/README.klic` 4564 B (200, txt)<br>`symbolic-proc/unix/klic/INSTALL` 5283 B (200, txt)<br>`symbolic-proc/unix/klic/tutorial/KL1TUT.info` 98985 B (200, txt)<br>`symbolic-proc/unix/klic/tutorial/tutorial.tex` 96556 B (200, txt)<br>`symbolic-proc/unix/klic/tutorial/Makefile` 470 B (200, txt)<br>`symbolic-proc/unix/klic/klic.tgz` 831858 B (200, gz) |
| 79 | Knowledge Representation Language: Quixote KLIC version | UNIX machine / KLIC, UNIX | Quixote KLIC version | 6 MB | `kbms-clp/klic/bigqxt/README` 4129 B (200, txt)<br>`kbms-clp/klic/bigqxt/INSTALL` 4710 B (200, txt)<br>`kbms-clp/klic/bigqxt/qxtall.tgz` 605445 B (page: 700K; 200, gz)<br>`kbms-clp/klic/bigqxt/qxtdoc.tgz` 96659 B (page: 104K; 200, gz)<br>`kbms-clp/klic/bigqxt/qxtclient.tgz` 68831 B (page: 158K; 200, gz)<br>`kbms-clp/klic/bigqxt/qxtserver.tgz` 431105 B (page: 429K; 200, gz) |
| 80 | Knowledge Representation Language: micro-Quixote | Independent / UNIX, MS-DOS | micro-Quixote | 199 KB | `kbms-clp/unix/m-qxt.tgz` 104599 B (page: 1,046K; 200, gz) |
| 81 | Parallel Theorem Prover: MGTP/G Prolog Version | UNIX/PC / UNIX/MS-DOS | Prolog | 60 KB | `solver-prover/unix/MGTP-G/MGTP-G-Prolog.tgz` 555296 B (page: 553K; 200, gz) |
| 82 | Parallel Theorem Prover: MGTP/N Prolog Version | UNIX/PC / UNIX/MS-DOS | Prolog | 60KB | `solver-prover/unix/MGTP-N/MGTP-N-Prolog.tar.gz` 596980 B (page: 573K; 200, gz) |
| 83 | Protein Motif Knowledge-Base and Retriever Based on Quixote | PIM / PIMOS | KL1 | 280 KB | `exper-apps/pimos/qxt_motif.tar.Z` 771707 B (page: 772K; 200, Z) |
| 84 | Protein Structure Prediction Based on Multi Level Description | PIM / PIMOS | KL1 | 5 MB | `exper-apps/pimos/mssd.tar.Z` 791607 B (page: 792K; 200, Z) |
| 85 | KLIC version 2: A parallel implementation of KL1 for general-purpose computers | UNIX machine, etc / UNIX | C | 3.5 MB | `symbolic-proc/unix/klic/README1` 874 B (200, txt)<br>`symbolic-proc/unix/klic/readme/README.klic` 4564 B (200, txt)<br>`symbolic-proc/unix/klic/INSTALL` 5283 B (200, txt)<br>`symbolic-proc/unix/klic/tutorial/KL1TUT.info` 98985 B (200, txt)<br>`symbolic-proc/unix/klic/tutorial/tutorial.tex` 96556 B (200, txt)<br>`symbolic-proc/unix/klic/tutorial/Makefile` 470 B (200, txt)<br>`symbolic-proc/unix/klic/klic-2.002.tgz` 951411 B (200, gz) **HELD** |
| 86 | Distributed Pool | PIM/UNIX machine / PIMOS/UNIX, KLIC | KL1 | 0.2 MB | `symbolic-proc/klic-apps/d-pool/README` 1530 B (200, txt)<br>`symbolic-proc/klic-apps/d-pool/dpool_klic.tgz` 168923 B (200, gz)<br>`symbolic-proc/klic-apps/d-pool/dpool_pimos.tgz` 226194 B (200, gz) |
| 87 | Parallel Database Management System : Kappa (KLIC version) | UNIX machine / UNIX, KLIC | KL1, C | 6 MB | `kbms-clp/klic/kappa/README` 8001 B (200, txt)<br>`kbms-clp/klic/kappa/kappa.tgz` 764969 B (page: 765K; 200, gz) |
| 88 | Parallel Constraint Logic Programming System : GDCC (KLIC version) | UNIX machine / UNIX, KLIC | KL1, C | 6 MB | `kbms-clp/klic/gdcc/GDCC4.0.tgz` 114079 B (page: 114K; 200, gz) |
| 89 | Heterogeneous Distributed Cooperative Problem-Solving System : Helios | UNIX machine / UNIX | C | 0.9 MB | `kbms-clp/unix/helios/README` 5033 B (200, txt)<br>`kbms-clp/unix/helios/helios.tgz` 3699824 B (page: 3,700K; 200, gz) |
| 90 | MGTP/G (KL1 version/KLIC version) | PIM/UNIX machine / PIMOS/UNIX, KLIC | KL1, Prolog | 160 KB | `solver-prover/klic/MGTP-G/README` 939 B (200, txt)<br>`solver-prover/klic/MGTP-G/MGTP-G.tgz` 561540 B (page: 561K; 200, gz) |
| 91 | MGTP/N ( Model Distribution ) ( KL1 version ) | PIM / PIMOS | KL1 | 50 KB | `solver-prover/pimos/MGTP-N/README` 881 B (200, txt)<br>`solver-prover/pimos/MGTP-N/MGTP-N-KL1.tgz` 565196 B (page: 565K; 200, gz) |
| 92 | Constraint MGTP (Prolog version/KL1 version /KLIC version) | PIM/UNIX machine / PIMOS/UNIX, KLIC | Prolog/KL1 | 0.2 MB | `solver-prover/klic/CMGTP/README` 1713 B (200, txt)<br>`solver-prover/klic/CMGTP/CMGTP.tar.gz` 596602 B (page: 597K; 200, gz) |
| 93 | Multiple Sequence Alignment by Parallel Iterative Improvement Method (KLIC version) | UNIX Machine / UNIX, KLIC | KL1, C | 3 MB | `exper-apps/klic/pia_klic.tar.gz` 1205549 B (page: 626K; 200, gz) |
| 94 | Multiple Sequence Alignment by Genetic Algorithm | PIM/UNIX Machine / PIMOS/UNIX, KLIC | KL1 | 0.3 MB | `exper-apps/klic/alignga/README` 17136 B (200, txt)<br>`exper-apps/klic/alignga/INSTALL` 4559 B (200, txt)<br>`exper-apps/klic/alignga/COPYRIGHT` 5344 B (200, txt)<br>`exper-apps/klic/alignga/image.tgz` 262134 B (200, gz)<br>`exper-apps/klic/alignga/software.tgz` 1114067 B (page: 1,114K; 200, gz) |
| 95 | Multiple RNA-Sequence Alignment Considering Stem Regions | PIM/UNIX Machine / PIMOS/UNIX, KLIC | KL1 | 0.3 MB | `exper-apps/klic/RNASA.tar.Z` 162264 B (page: 162K; 200, Z) |
| 96 | Knowledge Base of Biological Reactions | UNIX machine / UNIX, Motif, u-QUIXOTE | C, g++, QUIXOTE | 0.4 MB | `exper-apps/unix/pathway/README` 2753 B (200, txt)<br>`exper-apps/unix/pathway/pathway.tgz` 954905 B (page: 955K; 200, gz) |
| 97 | Successive State Splitting of Protein Hidden Markov Network | UNIX machine / UNIX, Motif | C | 0.1 MB | `exper-apps/unix/ssshmm/README` 1885 B (200, txt)<br>`exper-apps/unix/ssshmm/DOC` 1271 B (200, txt)<br>`exper-apps/unix/ssshmm/ssshmm.tgz` 24376 B (page: 24K; 200, gz) |
| 98 | DNA Sequence Analysis using Discriminant Analysis | UNIX Machine / UNIX | C | 100 KB | `exper-apps/unix/Quant2/README` 2286 B (200, txt)<br>`exper-apps/unix/Quant2/Quant2.tar.gz` 30146 B (page: 30K; 200, gz) |
| 99 | DNA Sequence Analysis using Hidden Markov Model and Genetic Algorithm | UNIX Machine / UNIX | C | 250 KB | `exper-apps/unix/HMMGene/README` 3320 B (200, txt)<br>`exper-apps/unix/HMMGene/HMMGene.tgz` 61148 B (page: 61K; 200, gz) |
| 100 | Legal reasoning system : new HELIC-II | PIM/UNIX machine / PIMOS/UNIX, KLIC | KL1 | 20 MB | `exper-apps/klic/helic2/README` 5501 B (200, txt)<br>`exper-apps/klic/helic2/cui/README` 2763 B (200, txt)<br>`exper-apps/klic/helic2/cui/cui.tgz` 431803 B (page: 4,690K; 200, gz)<br>`exper-apps/klic/helic2/drs/README` 2051 B (200, txt)<br>`exper-apps/klic/helic2/drs/drs.tgz` 377183 B (page: 685K; 200, gz)<br>`exper-apps/klic/helic2/gui/README` 2798 B (200, txt)<br>`exper-apps/klic/helic2/gui/gui.tgz` 1105311 B (page: 1,204K; 200, gz) |

**Observations on the catalogue.**

- Entries 26 (QUTE, "DEC2060 / TOPS20") and 27 (SAM, PSI-II / SIMPOS /
  ESP) print "[??K]" and link nothing; no `qute` or `sam` file is in
  the UEDA listing although `ifs/README` gives directories for both.
  They were catalogued and never deposited, or were withdrawn.
- `ifs/README`'s directory map disagrees with the catalogue for
  entries 66-70: it lists `colodex [66]`, `examds [67]`, `seqanal
  [68]`, `cbcdss [69]`, `rodin [70]` with descriptions shifted by one
  against the names. The abstract pages are taken as authoritative.
- Entry 4's page gives "Environment: SIMPOS" for PIMOS; entry 2's
  gives "Machine: PIM, Multi-PSI / Environment: PIMOS" for VPIM. Both
  describe where the thing is hosted, not what it is.
- Entry 22 (MGTP) prints "Source Code: 2 KB" and entry 39 (PAX) "1.5
  KB"; the archives are 20,229 and 74,787 bytes compressed. Misprints.

**In the `ifs/` tree but outside the numbered catalogue** (UEDA
listing READ; sizes as listed):

| Path | Contents | Status |
|---|---|---|
| `manuals/pimos/` | `man15.ps.Z` 322K (PIMOS manual 1.5, English), `man30.j.ps.Z` 1.6M (PIMOS 3.0, Japanese), `primer15.j.tex.Z` 42K, `primer25.tex.Z` 36K (the English "PIMOS 3.0 Introductory Manual"; fetched and READ here, 37,207 B) | PUBLIC; primer verified |
| `manuals/kl1/` | `kl1-text.tar.Z` 197K, `kl1-tut.ps.Z` 120K, `kl1-tut.j.ps.Z` 263K, `kl1-tut.dvi.Z` 58K | PUBLIC (listed) |
| `manuals/esp/` | `ESPps.tar.Z` 362K, `ESPps-j.tar.Z` 585K, `ESPtex.tar.Z` 167K, `ESPtex-j.tar.Z` 179K | PUBLIC (listed) |
| `symbolic-proc/klic-system/klic-old/` (also under `unix/klic/klic-old/`) | `klic-1.500.tgz` 741K, `klic-2.000.tgz` 918K, `klic-2.001.tgz` 929K | PUBLIC (listed) |
| `symbolic-proc/KLIC-New/` (also `unix/KLIC-New/`) | `klic-3.001.tgz` 812K, with `COPYRIGHT-JIPDEC` | PUBLIC (listed) |
| `solver-prover/pimos/mgtp.tar.Z` | 43K, an MGTP archive no page links | PUBLIC (listed) |
| `kbms-clp/klic/bigqxt/server-org.tgz` | 1.1M | PUBLIC (listed) |
| `exper-apps/klic/helic2/{cui,drs,gui}/` | new HELIC-II also laid out unpacked, file by file | PUBLIC (listed) |
| `newsletter/E01.920701` ... `E09.950331`, `J01` ... `J09` | IFS newsletters; E01, E04-E09 fetched here (HTTP 200) and searched by keyword, E01 and E04 passages read | PUBLIC verified |
| `INFO.tar.Z` 21K, `README`, `README.j` | licence, character codes, CESP and KLIC notes | PUBLIC; `README` READ |
| `contract-research/` | AITEC-funded work FY1995-98 (186 directories walked, not analysed) | PUBLIC (listed) |

A second copy of the 1995 state of the tree, re-packed, is at the CMU
AI Repository,
`https://www.cs.cmu.edu/afs/cs/project/ai-repository/ai/areas/icot/`
(HTTP 200 here; top-level entries `apps/`, `kbms_clp/`,
`manuals/`, `newsltr/`, `nlp/`, `reasonng/`, `symbolic/`, `cesp.txt`,
`info.tgz` READ).

That copy has now been compared file by file with ours
(`nonlocal/CMU_MANIFEST.md`, 2026-11-26). We walked all 31 directories and matched each of
its 100 `.tgz` packages by its `.ltv` listing (member names and sizes)
against the held archives, then downloaded 20 files and compared them by hash:
- 8 are byte-identical once decompressed. These include `pimos`, `pimosobj`,
  `psdpim`, `pimosman`, `pdss`, `pkl1` and `vpim`, all the 12 May 1994
  release we hold.
- 79 have the same members as our copies.
- 5 hold, in one bundle, files that AIST keeps as separate files.
- 4 are earlier releases: Quixote, proview, kl1graph, and cu-Prolog 3.1.
- 4 exist only at CMU: **KLIC 1.000, 1.100, 1.210 and 1.410** (Dec 1993 to
  Jun 1994, older than the 1.500 we held). They are now in
  `nonlocal/cmu/` with the IFS terms.

The CMU copy has no other PIMOS version and no SIMPOS, PSI microcode,
firmware, window system, Pmacs or ESP compiler.

**What the catalogue means for a booted PIMOS.** The 49 PIMOS entries
are source distributions for PIMOS 3.0 to 3.5 (the pages name "PIMOS
3.0", "3.01", "3.1", "3.4", "3.45", "V3.5 and later"); ours is 3.6.
Of them, 13 also name SIMPOS in the environment field or ESP in the
language field (8, 31, 32, 39, 53, 55-61, 64): those have a front-end
half. Others carry ESP parts without saying so in those fields
(Quixote 11 and Kappa-P 13 do, per `icot_databases.md` section 7).
Small packages that name only PIMOS and KL1 are the natural first
applications: MGTP (22; 20,229 B), the Parallel Problem Solving
System (30; 71,957 B), the load distribution library (74; 123,055 B),
AYA (73; 235,617 B), MGTP/N (91; 565,196 B). Whether any of these
has an undeclared ESP part is unchecked: none was opened.

## 4. Not in IFS: lost, unpublished or not found

For each: evidence that it existed, what was searched, and who might
hold it. "Searched" refers to this session's checks plus Appendix D of
`literature_gaps.md` (SECONDARY: 23,910 crawled paths of the UEDA
mirror searched by file name for `psi`, `simpos`, `esp`, `kl0`, `csp`,
`fep`, `kbn`, `firm`, `micro`, `cesp`; bitsavers indexes; CiNii and
NDL catalogues; museum pages; GitHub).

| Item | Evidence it existed | Copy found? | Who might hold it |
|---|---|---|---|
| **SIMPOS** (kernel, supervisor, window/file/network, PMACS editor, librarian, debugger, shell, spooler, pattern editor) | FGCS'84 SIM paper (READ); `login.com` in both held archives lists `simpos##debugger`, `simpos##pmacs`, `simpos##file_manipulator`, `simpos##librarian`, `simpos##shell`, `simpos##spooler_manipulator`, `simpos##pattern_editor` (READ); `.ptf` files reference `simpos##` classes (READ) | **None.** Not in IFS; no disk image, tape or source anywhere searched | Mitsubishi Electric (sold PSI, PSI-II, PSI/UX); the JAIST PSI if its disks survive; ICOT alumni |
| **ESP compiler, linker, runtime; the Librarian and `.ptf` format** | ESP manuals (PUBLIC); `INSTALL`: "load them as package template files with the SIMPOS Librarian" (READ) | None. No description of the `.ptf` format found | as above |
| **Common ESP (CESP)** | IFS newsletters E01, E06 (READ): not part of IFS; AI Language Research Institute, `cesp-request@air.co.jp`; SUN4 (SECONDARY) | None | AIR's successors; Mitsubishi Electric Computer Systems (Tokyo) |
| **KL0 firmware** for PSI, PSI-II | FGCS'84 hardware papers; IFS abstract 003 ("ESP and the operating system ... are executed by a KL0 language processor", READ) | PSI-III only, as binary inside `psdpim/PMPSI.DIR` (HELD; which file not established; probably `syspsi`, with `sysidat` as its decode table, see the note in 2.3). No source, no PSI-I/II image | Mitsubishi, Oki |
| **Multi-PSI KL1 microcode** (`.mbn` images, `kl1kp.kbn`, `kl1pat.com`) and **Pseudo Multi-PSI for PSI-II** | primer (READ) | None | Mitsubishi; ICOT alumni (K. Nakajima and colleagues are the authors of the Multi-PSI KL1 implementation reports, SECONDARY) |
| **PIM/m KL1 microcode** (real machine) and the microassembler, "Microlint" checker | TR-742; TM-849 (SECONDARY) | None. Pseudo PIM/m microcode binary HELD | Mitsubishi; the National Museum of Nature and Science if media came with the machine |
| **Firmware patch file** `pmpsi:pimm_patch.com` for the Pseudo PIM/m | named in held `boot.init` (READ) | Not in `psdpim.tar.Z` | probably never released; `patch(on,...)` may fail soft |
| **CSP software** for Multi-PSI and PIM/m | primer; TM-1213 (SECONDARY) | Pseudo PIM/m CSP and remote CSP as compiled ESP (HELD). Real CSP: none | as above |
| **CSP operating manuals** | "Multi-PSI/V2 Console System (CSP) Operating Manual", "(Pseudo) Multi-PSI System Administration Manual" (primer bibliography, READ); PSI CSP manual 1985 (catalogue, SECONDARY) | 1985 PSI manual: one catalogued copy (JAIST library). Others: none | JAIST; Mitsubishi |
| **SIMPOS manuals** | "Basic PSI/SIMPOS Operating Manual (1),(2)", "Basic System Administration Manual for PSI/SIMPOS Systems" (primer bibliography, READ); three 1985 manuals (catalogue, SECONDARY) | 1985 ones: JAIST library. Later: none | JAIST; Mitsubishi |
| **FEP sources** (`pimfep`, `pimscsi` ESP source) | the `.ptf` files (HELD) | Binary only | ICOT alumni; never in IFS |
| **IPL source** (`ipl*`, `top`, `scsi_fep_file/module/general/util`) | object code in `pimm_ipl.kbn` (SECONDARY) | Object only; absent from `pimos.tar.Z` | PIMOS group alumni |
| **CAL cross system** (built `.kbn` up to PIMOS 2.5; a SIMPOS program) | Japanese PIMOS 3.0 manual 6.1 (SECONDARY); commented-out menu entry `{"CAL", cal##cal_manipulator}` in held `login.com` (READ). Not the CLP language CAL of IFS 14/19 | None | as SIMPOS |
| **PIMOS 1.x, 2.x, 3.0-3.5** code and the "PIMOS 2.5 Manual" | primer; manuals 1.5 and 3.0-J (PUBLIC) | Manuals 1.5 and 3.0-J only. Code: only 3.6 | ICOT alumni |
| **PIMOS internal file system** | FGCS'92 pp. 278-285; TM-1254 (SECONDARY) | Not in the source release; binary UNKNOWN | PIMOS group alumni |
| **PSL translator and VPIM build system; per-PIM back ends** | VPIM README (SECONDARY) | None | Fujitsu, Hitachi, Oki, Toshiba |
| **QUTE (IFS 26), SAM (IFS 27)** | catalogue pages (READ) | No archive in the tree | unknown |
| **Any emulator** of PSI, PSI-II, PSI-III, Multi-PSI or a PIM | ICOT had a PSI-II microprogram simulator (one of TM-212, 213, 261, 353, 354 by title; SECONDARY, which number not checked) | None found | |

### 4.1 Where copies were looked for outside the ICOT archive

Searched on 2026-11-20 by a delegated search in this session; rows
are SECONDARY (its report, with its own opened/hit distinction kept)
unless marked READ, which this survey re-opened itself.

| Place | Result | Evidence |
|---|---|---|
| Software Heritage | KLIC only: `github.com/GunterMueller/KLIC`, `github.com/CesarBallardini/kl1c`, `github.com/keyasuda/klic-docker`, Debian and Ubuntu `klic` package origins. Nothing for `pimos`, `icot`, `kl1`, `simpos`, `fgcs`, `aitec`, `PDSS`. Origin search is not exhaustive (an archived origin was missing from its own keyword listing) | origin-search API, opened. READ here: `origin/search/pimos` and `/klic` return only unrelated origins |
| GitHub, GitLab | No emulator, no SIMPOS, no ESP compiler, no KL0. Found: KLIC re-hosts and packaging; two 2024 re-uploads of IFS packages (PIMOS; MGTP/N Prolog), search hits only; new, unrelated implementations of the language family: `gitlab.com/ovf/fleng` ("A compiler for the concurrent logic programming languages FGHC, Strand, KL1 and PCN"), `github.com/tadashi9e/my_little_ghc_compiler`. Codeberg not searched (rate limit) | search APIs. READ here: GitHub repository search `PIMOS ICOT` gives 1 hit; `SIMPOS PSI`, `KL1 PIMOS`, `ICOT free software` give 0 |
| Computer History Museum | The catalogue is searchable (JSON POST to `collections/catalog/search-catalog`; a nonsense-word control returned 0), contrary to Appendix D. Keyword ICOT with type software: 0; with type physical object: 0. Holdings are paper: FGCS'81 proceedings (102659252), a 1982 status report (102659253), FGCS Editorial Bulletin 1(2) 1983 (102719259), a 1991 committee report (102810199). `102785625-05-01-acc.pdf` is the Proceedings of the Second International Logic Programming Conference, Uppsala 1984, with the SIMPOS/ESP papers. Catalogue 102774812 "ICOT" is an unrelated US company. No ICOT participant among the oral histories | opened |
| IT History Society, `ithistory.org/node/22506` | A "MELCOM PSI" stub copied from the IPSJ museum; no holdings | opened |
| Internet Archive | No SIMPOS, PIMOS or PSI manuals or software. A second copy of the CMU ICOT tree exists inside the 2019 crawl `warc_www_cs_cmu_edu-afs-cs-project-ai-repository-ai_20191020` (one 5.2 GB WARC; 1,072 captures under `areas/icot/`). The book of "Prime Time Freeware for AI" 1-1 (1994; `primetimefreewar0000unse`) lists `areas/icot/` and `areas/icot/manuals/esp/`, so that CD-ROM carried IFS; the disc image was not found | metadata and CDX opened |
| Overseas sites with ICOT machines | `AIST/Museum/IExchange/ie-J.html` lists PSI installations abroad: Argonne (June 1990 - March 1992), NIH (October 1990 - October 1992), Lawrence Berkeley Laboratory (December 1990 - July 1992), SICS (August 1990 - 1994), ANU (August 1991 - 1994), University of Oregon (from January 1993); Bristol used "PIM interface software on UNIX machines" and had no PSI. A Multi-PSI was taken to Argonne for a workshop in October 1989. The pseudo-parallel environment "is on PSI-2 and was lent"; later PSI-3 "with a UNIX machine as front end" was introduced. Final-evaluation pages: NIH "Using the PSI II and III machines loaned to the NIH" (057); ANU "two Psi-2 workstations ... very difficult to maintain properly will be re-placed by ... Psi-3" (078). The end dates read as loan periods. No evidence of anything surviving at any of the sites. Imperial College and Weizmann are not on the list | opened (Japanese page; the English `ie-E.html` returns 500) |
| Custody of the masters | "ICOT Free Software (IFS) ... was transferred to JIPDEC at July 1995. October 1st 1996, JIPDEC established Research Institute for Advanced Information Technology (AITEC)" (`AIST/Museum/NEWS/aitec-news-E.html`). JIPDEC still serves FGCS documents (`jipdec.or.jp/archives/publications/J0005062`, the 1993 final evaluation report). Who holds the masters today, and when AITEC closed, were not found | opened |
| Former researchers' pages | One search each for Chikayama, Nakashima, Taki, K. Nakajima, Tick, Furukawa, Nishida and for Oki: no page hosting software or documents, no oral history on what became of the machines | searches only |
| Common ESP | `AIST/Museum/IFS/INFO/cesp-E.html`: "CESP is not part of the ICOT Free Software, instead being available from MITSUBISHI ELECTRIC COMPUTER SYSTEMS(TOKYO) CORP. (MTC)"; Ver. 3.3, SUN4, SunOS 4.0.3-4.1.2; apply "by Fax or Postal mail". No download, mirror or current vendor page | opened |
| Museums | JAIST and IPSJ statements READ here (section 5.2). Kahaku index: no PIM entry. IPSJ heritage certification of PSI or PIM: undetermined | |
| Japanese blogs, forums, X | nothing on surviving hardware or software | searches only |

**What this adds.** (a) The PSI-II pseudo-parallel system, which is
not in IFS, was physically lent to at least five sites abroad; those
are the places outside Japan where a Pseudo Multi-PSI and its SIMPOS
once were. All appear to have been loans that ended by 1994. (b) The
PIM models were reached from Bristol through "PIM interface software
on UNIX machines". This survey's inference, not a statement in the source:
a UNIX-side front end for the PIMs existed by the final stage. No
copy found; nothing by that name is among the IFS packages. (c) The
only body shown to have taken formal custody of ICOT's software is
JIPDEC.

## 5. Acquisition and reconstitution list, by how much each unblocks

### 5.1 Download now (public; link status as stated)

*Done (note 2026-11-23): every item below is now held as data.
Rows 1-7 are under `nonlocal/ifs/` (`IFS_MANIFEST.md`, 2026-11-20):
`symbolic-proc/pim-psi/pimosman.ps.Z`, `manuals/pimos/primer25.tex.Z`,
`man30.j.ps.Z`, `man15.ps.Z`, `manuals/esp/ESPtex.tar.Z`,
`ESPps.tar.Z`, `solver-prover/pimos/MGTP/mgtp.tgz`,
`symbolic-proc/pimos/aya.tar.Z`, `ldlib.tar.Z`,
`symbolic-proc/klic-apps/d-pool/dpool_pimos.tgz`, `newsletter/E01`-`E09`
and `J01`-`J09`, `symbolic-proc/KLIC-New/klic-3.001.tgz`,
`symbolic-proc/klic-system/klic-old/`. Row 8's TM-1021, TM-1022,
TM-1213 and TM-671 are in `nonlocal/lit/trtm/` (`LIT_MANIFEST.md`).
The table is kept as the record of why each was wanted.*

| Priority | Item | URL (under AIST unless noted) | Why |
|---|---|---|---|
| 1 | Typeset PIMOS manual | `ifs/symbolic-proc/pim-psi/pimosman.ps.Z` (verified: 200, 866,355 B, compress magic) | Page-citable form of the held LaTeX. The roadmap lists it as "not found"; it is there |
| 2 | PIMOS 3.0 Introductory Manual and the Japanese 3.0 manual | `ifs/manuals/pimos/primer25.tex.Z` (verified), `man30.j.ps.Z` (listed, 1.6M) | CSP boot panel, FEP numbering, login procedure, IPL chapter 6.1 |
| 3 | PIMOS manual 1.5 | `ifs/manuals/pimos/man15.ps.Z` (listed, 322K) | Appendix on writing a string I/O device on the FEP in ESP: the FEP device interface from the user's side |
| 4 | ESP manuals | `ifs/manuals/esp/ESPtex.tar.Z` (listed, 167K) and `ESPps.tar.Z` | Needed to read the method and class structure in the `.ptf` files and the 90 held `.esp` files |
| 5 | First applications | `ifs/solver-prover/pimos/MGTP/mgtp.tgz` (verified, 20,229 B); `symbolic-proc/pimos/aya.tar.Z`, `ldlib.tar.Z`; `symbolic-proc/klic-apps/d-pool/dpool_pimos.tgz` | Rung R9 candidates with no FEP half |
| 6 | IFS newsletters | `ifs/newsletter/E01...E09` (verified for E01, E04-E09) | Release history of PIMOS and the Pseudo PIM/m (both "version-up" 29 March and 12 May 1994, matching the two file dates in the held archives) |
| 7 | KLIC 3.001 and the old KLICs | `ifs/symbolic-proc/KLIC-New/klic-3.001.tgz`, `klic-system/klic-old/` (listed) | Reference implementation for answers (R8 oracle); completeness |
| 8 | Unlisted TMs on the front end and CSP | `Museum/TRTM/TM/TMpdf/tm1021.pdf`, `tm1022.pdf`, `tm1213.pdf`, `tm0671.pdf` (SECONDARY: verified in Appendix D) | The only prose on the PIM/m FEP and CSP |

### 5.2 Ask for (not public)

| Priority | What | Whom, and why they might have it |
|---|---|---|
| 1 | Source of the IPL modules and of `pimfep`/`pimscsi`; the CSP manual | Former PIMOS and Multi-PSI group members. The object set and `.ptf` files were built from them in 1994 for the IFS release, so they existed at ICOT's closure |
| 2 | Any SIMPOS distribution for PSI/UX (it lived in UNIX files under `/usr/psi/simpos`) | Mitsubishi Electric; a surviving PSI/UX would carry it on an ordinary UNIX file system, which is the most recoverable form any SIMPOS could take |
| 3 | The JAIST holdings: the collection "also includes ICOT PSI and other symbolic processing computers. Dynamic preservation of some machines has been tried" (`https://museum.ipsj.or.jp/en/satellite/JAIST.html`, READ); the 1985 CSP operating manual, "MP7003-1", held by the JAIST library alone (`https://ci.nii.ac.jp/ncid/BN13167682`, READ: 1 holding of 1); four more 1985 manuals there (SECONDARY) | JAIST. A PSI kept running, or its disks, is the only lead to a SIMPOS that this survey found |
| 4 | Whatever media accompany the preserved PIM/m and PIM/p | National Museum of Nature and Science, Tokyo. IPSJ museum page READ here: "Today, the PIM/p and PIM/m are preserved at the National Science Museum in Tokyo" |
| 5 | Common ESP 3.3 | Successors of AI Language Research Institute and Mitsubishi Electric Computer Systems |
| 6 | PIMOS internal file system, earlier PIMOS versions, PSL translator | alumni; the PIM manufacturers |
| 7 | The archive masters, and anything ICOT did not publish | JIPDEC, to which IFS "was transferred ... at July 1995" (SECONDARY, section 4.1) |
| 8 | The "Prime Time Freeware for AI" 1-1 CD-ROM (1994) | collectors, libraries: a dated third copy of the IFS tree; low value, nothing new expected |

### 5.3 Rewrite (reconstitute), in dependency order

| Order | What | From what | Unblocks |
|---|---|---|---|
| 1 | KL1-B executor and runtime for the PIM/m dialect (rows 1, 2 of section 1) | PIMOS compiler/assembler source, PDSS, VPIM, the Pseudo PIM/m microcode | everything |
| 2 | CSP stand-in: load `.kbn` at its address, console sink, start | `boot.init`, the decoded `.kbn` header, primer | R4 |
| 3 | FEP stand-in, boot subset: SCSI processor unit, packet codec, file read | `scsi_fep.kl1`, `pimos.vmac`, disassembly of the IPL's `scsi_fep_*` modules; names cross-checked against `pimfep.ptf` | R4, R5 |
| 4 | FEP stand-in, interactive subset: login requester, line window, timer | `win_dvc.kl1`, `time_dvc.kl1`, `server/fep/window`, `server/fep/timer`, manual `e-ioctrl.tex` | R6 |
| 5 | FEP stand-in, application subset: directories, string_io devices, sockets | `dir_dvc.kl1`, `strio_dvc.kl1`, `soc_dvc.kl1`; PIMOS 1.5 manual appendix | R7-R9 |
| 6 | FEP halves of individual applications (ESP window programs) | each package's ESP source | only for applications that have one |

SIMPOS, the ESP system and the real CSP are not on this list: the
stand-ins replace them. That is a substitution, and the model's
documents should say so wherever a rung is claimed.

## 6. Searched for and not found

This session's own checks:

- File-name search of the UEDA `ifs/` listing (1,731 entries, 138
  directories outside `contract-research/`) for `qute`, `sam`: no
  file. Files not linked from any abstract page: section 3.
- In `pimos.tar.Z`: any use of `fep#ipl` or `fep#symbol` outside
  `pimos.vmac`: none. Any source for the patch sets as such: none.
- In `psdpim.tar.Z`: `pimm_patch.com`: absent. A mnemonic file for
  the microcode reverse assembler: absent (SECONDARY). Any ESP source:
  none.
- `asm/psdpim.py --text` on `object/paragraph.ptf`: the tool reads
  only members of `psdpim.tar.Z`; the file was scanned with an ad hoc
  two-byte reader instead (1,389 names, among them `ParaGraph`,
  `as_pimos_string_io_device`, `pimos_user_exit`).
- GitHub repository search API: `PIMOS ICOT` (1), `SIMPOS PSI` (0),
  `KL1 PIMOS` (0), `ICOT free software` (0). Software Heritage origin
  search: `klic`, `pimos` (unrelated origins only).
- Not attempted here: opening any IFS archive other than the eight
  held; reading the compiled code of any `.ptf`; searching the object
  set for the file system server.

The delegated search's queries (SECONDARY, as it reported them).
Returned nothing useful: Software Heritage `pimos`, `icot`, `kl1`,
`simpos`, `fgcs`, `aitec`, `uedalab`, `PDSS`; GitHub `ICOT free
software`, `KL1 PIMOS`, `SIMPOS`, `PSI machine emulator`, `KL0`, `ESP
SIMPOS`, `Multi-PSI`, `pdss kl1`, `ICOT`, `fifth generation computer`,
`guarded horn clauses`, `ICOT fifth generation`, `PSI-II`, `inference
machine ICOT`, `PDSS`, `ESP ICOT`, `kl1 concurrent logic`, `AITEC
ICOT`, `SIMPOS ESP`, `CESP prolog`, and `in:readme` forms of `SIMPOS`,
`"Multi-PSI"`, `KL0 ICOT`, `"PSI machine" prolog`, `ICOT ESP prolog`;
GitLab `KLIC`, `PIMOS`, `ICOT`; Internet Archive `ICOT`, `SIMPOS`,
`PIMOS`, `KL1`, `KLIC`, `MELCOM PSI`, `"ICOT Journal"`, `"ICOT Free
Software"`, `"parallel inference machine"`, `"sequential inference
machine"`, `新世代コンピュータ技術開発機構`, `"第五世代コンピュータ"`,
`creator:ICOT`, `PTF AI CD-ROM`; Computer History Museum `MELCOM PSI`,
`KL1`, `ESP SIMPOS`, `Mitsubishi inference`, `Prime Time Freeware`;
web 「SIMPOS ソース」, 「ICOT PSI 保存」, 「マルチPSI 保存」, 「PIM/m
国立科学博物館」, 「CESP Common ESP」, 「PSI 推論マシン 実機 保存 SIMPOS
現存」, `"Prime Time Freeware for AI" CD-ROM ISO image download`, a PSI
emulator query, oral-history queries, and one query per researcher
(中島浩, 瀧和男, 中島克人, Evan Tick, 古川康一/西田健次, 沖電気, 近山隆).
Returned something: Software Heritage `klic`, `mgtp`; GitHub `PIMOS`,
`MGTP`, `KLIC KL1`, `KL1 compiler`, `ICOT prolog`; Internet Archive
`"Fifth Generation Computer Systems"`, `"Prime Time Freeware"`,
`"ai-repository"`; Computer History Museum `ICOT`, `"fifth generation
computer"`, `SIMPOS`, `PIMOS`, `Multi-PSI`.

Earlier searches (catalogues, bitsavers, museums, vendor journals,
Wayback) and their query lists are in `literature_gaps.md` Appendix D
and are not repeated.

**Not found by anyone, stated plainly:** a PSI, Multi-PSI or PIM
emulator; SIMPOS in any form; an ESP compiler or runtime; Common ESP;
KL0 or KL1 microcode source; the Multi-PSI or real PIM/m microcode in
any form; the real CSP; the CSP and SIMPOS manuals of the PSI-II/III
era; source for the IPL and the FEP; the CAL cross system; the UNIX
"PIM interface software"; the PIMOS file system; who holds ICOT's
masters.

## 7. Contradictions recorded

- **`pimosman.ps.Z`.** `pimos_roadmap.md` section 6 lists it as
  wanted and `literature_gaps.md` section 9 says it "was not found";
  Appendix D and `icot_databases.md` give it at
  `ifs/symbolic-proc/pim-psi/`. Checked here: HTTP 200, 866,355 B,
  bytes `1f 9d`. It exists.
- **Source or binary.** IFS abstract 003 says of the Pseudo PIM/m
  "Language: ESP, microprogram / Source Code: 2.5 MB". The archive
  holds compiled packages and microcode images and no source. The
  catalogue's "Source Code" field means size of the distribution.
- **Which PSI.** `pimosobj` `INSTALL`: "machines: PSI-II or PSI-UX".
  `psdpim` `README`: PSI-III, sold as PSI/UX. The PIMOS `README`:
  "The pseudo-parallel system for PSI-UX is distributed as a part of
  the ICOT Free Software." So the object set is meant for either; the released
  pseudo system installs on PSI-III, and the PSI-II firmware files the
  primer names are not in it. The names "Pseudo Multi-PSI" and
  "Pseudo PIM/m" are both used of the released package (newsletter
  E05; `login.com`; `README`).
- **Package names.** The primer's menu uses `mpsicsp##...`; the held
  `login.com` uses `pimmcsp##pseudo_csp_main_program` and
  `pimfep##pimos_login_requester`, and comments out `mpsiutil##...`
  entries; held `init.com` calls `mpsimpc##csp_slave_csp_main`. The
  held `mpsicspR.ptf` declares package `mpsicsp`. The Multi-PSI and
  PIM/m console systems were parallel package families.
- **Start address.** Primer: "start address 202" with `pimos.kbn`
  (SECONDARY). Held `boot.init`: `start(pimos,"20c")` with
  `pimm_ipl.kbn`. Different builds. How `20c` relates to the start
  address in the `.kbn` header (`0xE0001E81`, SECONDARY,
  `pimos_binaries.md`) is not reconciled. *Note 2026-11-23: still
  open, but these are two different quantities. `0xE0001E81` is the
  IPL image's own entry, cell `0x1e81` = 7,809 of an image loaded at
  `0xE0000000`, which is `ipl:boot/0` (`asm/kbndis.py --check`; the
  `.ldb` agrees). `20c`, `202` and the help text's `200` (Pseudo
  MPSI, "KL1 Start Address") and `2000` (Multi-PSI, "Micro Start
  Address") are the start addresses given to the CSP's `GO/PIMos`, which "starts CPU
  and throws a boot goal to the boot PE". That `boot.init`'s
  `start(pimos,"20c")` is that same command is INFERENCE from the names
  and the help text's "$GO/PIMos <Start Address>". `20c` is not an offset into
  the image: cell `0x20c` is in the middle of
  `ipl_file_decoder:check_GC_element/8` (measured with `kbndis.Image`).
  `PIMM.PARAM` also has `stadr 16'204` ("Firmware debug use only") and
  `bmadr 16'2E6` ("Boot Module Address"). What `20c` addresses would be
  settled by the CSP's `GO/PIMos` code in `pimmcsp.ptf`, or by the
  firmware's start-up path in `pimm.MEkbn`.*
- **File names in `pimos.ipl`.** The Japanese manual gives
  `mpsi_bios.sav` or `ppim_bios.sav` etc. (SECONDARY); the held list
  uses `pimm_*360E.sav`, and loads kernel first, macro last.
- **Firmware and object set.** The held firmware has no decode entry
  for `scsi_transfer`, which the object set uses once (SECONDARY,
  `pseudo_pimm_firmware.md`). *Note 2026-11-23: both statements stand.
  The one use is the listener's `do_command(scsi_transfer(...))`
  (module `listener_cmd_builtin`, `pimm_debugger360E.sav`;
  `src/debugger/listener/com_built.kl1`:135), a command a user types.
  Nothing on the boot or system paths uses it, so the firmware and
  the object set fit everywhere except that one command.*
- **`ifs/README` against the catalogue** for entries 66-70 (section
  3).
- **Dates.** `ifs/README` says "Last Modified on 15-Apr-1996"; the
  UEDA listing dates the file 1997-04-15. *(Note 2026-11-23: the text's
  date is confirmed in the held copy, `nonlocal/ifs/README` line 3.
  The two are dates of two things, the text's own date and the
  server's file time, so they do not contradict each other.)*

## 8. Sources

Opened in this session (READ):

- Held archives, listed with `zcat < X.tar.Z | tar tf -`:
  `pimos.tar.Z`, `pimosobj.tar.Z`, `pimosman.tar.Z`, `psdpim.tar.Z`,
  `pdss.tar.Z`, `vpim.tar.Z`, `pkl1.tar.Z`; `MANIFEST.md`,
  `SHA256SUMS`. Unpacked in a scratch directory (not in the
  repository): `psdpim` (`README`, `INSTALL`, `boot.init`,
  `usercom.init`, `PIMM.CONFIG`, the five `.ptf` files as text),
  `pimosobj` (`INSTALL`, `pimos.ipl`, `pimos.conf`, `*.com`),
  `pimos` (`README`, `src/bios/fep_module/scsi_fep.kl1`,
  `src/macro/pimos/pimos/pimos.vmac`, file and line counts).
- `AIST/ifs/README`; `AIST/Museum/IFS/abst/ifs-catalogue.html`;
  `AIST/Museum/IFS/abst/001.html` ... `100.html`.
- UEDA directory listings under `ifs/`.
- `AIST/ifs/newsletter/E01.920701`, `E04.921023`, `E05.930127`,
  `E06.931014`, `E07.940114`, `E08.940705`, `E09.950331` (keyword
  search; the CESP and Pseudo PIM/m passages read).
- `AIST/ifs/manuals/pimos/primer25.tex.Z` ("PIMOS 3.0 Introductory
  Manual", PIMOS Development Group).
- T. Yokoi, S. Uchida and ICOT Third Laboratory, "Sequential
  Inference Machine: SIM - Its Programming and Operating System",
  FGCS'84; `UEDA/Museum/FGCS/FGCS84en-proc/84eR%26D-5.pdf` (scan;
  OCR).
- T. Chikayama, "Operating System PIMOS and Kernel Language KL1",
  FGCS'92 vol. 1; `UEDA/Museum/FGCS/FGCS92en-proc1/92eRERR-2.pdf`
  (scan; OCR).
- Index pages of the FGCS'84, '88 (vols 1, 3) and '92 (vol. 1)
  proceedings under `UEDA/Museum/FGCS/`.
- `https://museum.ipsj.or.jp/en/computer/other/0002.html`;
  `https://museum.ipsj.or.jp/en/satellite/JAIST.html`;
  `https://ci.nii.ac.jp/ncid/BN13167682` (CiNii record of the 1985
  CSP operating manual).
- `https://www.cs.cmu.edu/afs/cs/project/ai-repository/ai/areas/icot/`
  (listing).

Used without re-opening (SECONDARY): this directory's
`literature_gaps.md` (section 9, Appendix D), `icot_databases.md`,
`pimos_boot_requirements.md`, `pimos_binaries.md`,
`pseudo_pimm_firmware.md`, `gap_analysis.md`, `nonlocal/MANIFEST.md`;
and through them TR-246, TR-389, TR-715, TR-742, TR-799, TM-212,
TM-213, TM-261, TM-353, TM-354, TM-662, TM-671, TM-849, TM-850,
TM-1021, TM-1022, TM-1044, TM-1213, TM-1254, the Japanese PIMOS 3.0
manual, the JAIST catalogue records, and FGCS'92 pp. 278-285 and
425-435.
