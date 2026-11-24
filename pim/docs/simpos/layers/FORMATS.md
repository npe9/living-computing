# Formats: package templates, control store, boot, disk

Labels:

- **KNOWN**: printed in a cited source.
- **MEASURED**: observed in the held files. The probe is named. Probes are read-only and use the
  repo's `pim/asm/ptfdump.py`; mine are in `C/tools/`.
- **UNKNOWN**.

Held files are in `pim/docs/nonlocal/psdpim.tar.Z` (extracted to `C/x/psd/psdpim/`) and the
other repo archives. Container-level parsing is already documented in
`pim/docs/binary_reverse_engineering.md` §4; it is not repeated here.

## 1. The object / template / source triple

**KNOWN.**

- OVW lines 2041–2116: the librarian catalogues an ESP source file. The compiler produces:
  - a **class template**, the load module;
  - a **class object**, the runtime class.
- The library keeps the source file and the class-template file.
- psdpim `INSTALL`: the `.ptf` files are copied in and "load[ed] as package template files
  with the SIMPOS Librarian".

So a `.ptf` is a **package template file**, a package's class templates. It is **not** a memory
image. The class objects are built from it at load time by the librarian/loader.

**MEASURED.** Six `.ptf` files are held:

| File | Classes |
|---|---|
| `pimfep` | 47 |
| `pimscsi` | 24 |
| `pimmcsp` | 281 |
| `pimmutil` | 51 |
| `mpsicspR` | 30 |
| `paragraph` | 121 |

`paragraph` is the only package with matching source (83 `.esp` files, a slightly older version:
"3200" in the source against "3500" in the object).

**UNKNOWN.**

- The class-object layout in memory (beyond TH App A's object descriptor, KL0.md §5).
- The library catalogue format.

## 2. Inside a class template (MEASURED unless marked)

**Body.** A body is a sequence of tagged cells (tags as in KL0.md §2): predicate headers, then
code (`pmi`/`blt` instruction cells, constants, hash-switch tables).

**Predicate header.** A header is the quadruple

> (name atom, integer `qual<<16 | kind<<8 | arity`, `predh` cell `arity<<24 | code offset`, 0)

The integer field reads as follows (probe `C/tools/kinds.py`, census over all six packages):

| Kind | Meaning | Count | Evidence |
|---|---|---|---|
| 0x25 | class-method primary | 589 | header atoms match source class methods |
| 0x35 | instance-method primary | 3,256 | ditto |
| 0x27 | class after-demon | 16 | `after:create/3` in what_shell_window, profiler_view_window and time_graph_window; `new/2` |
| 0x36 | instance before-demon | 22 | `before:kill/1` (p_wswin.esp:57); `simpos_user_device io/4` has 36, 37 and 35 together |
| 0x37 | instance after-demon | 46 | INFERENCE, from the io/4 triple; no paragraph source witness |
| 0x22 | class slot-init predicate | 15 | `register/1` in as_pg_color_window |
| 0x32 | instance slot-init or generated predicate | 57 | `display_pos/1` = p_tgraph.esp:81 `(display_pos:=L :- ...)`; also `$tail/1`, `$header/1` |
| 0x11 | local predicate | 3,559 | |
| 0x12 | compiler-generated `$or$N` (body disjunction) | 1,904 | |

From the bit pattern, 0x2x appears to mean class, 0x3x instance and 0x1x local. In the low nibble,
5 = primary, 6 = before, 7 = after and 2 = slot init (INFERENCE).

- Kind 0x26 (class before-demon) was not observed.
- The qualifier (1, 2 or 3) on primaries is **UNKNOWN**. All neck-cut methods seen had 2.

**Trailer.** Measured on what_shell_window and as_pg_color_window, the fields come in this order:

1. class-name atom;
2. class id;
3. `template`;
4. two integers (e.g. 33529 / 33950, then 56553654 / 576xxxxx: probably compiler version and
   timestamp, INFERENCE);
5. a vector of class-method code entries;
6. a class-slot vector (name, flag, initial value);
7. a vector of instance-method codes;
8. instance-slot vectors (`win 16 0`: name, flag 16 = attribute?, initial value);
9. a vector of local offsets;
10. **`[self, declared natures...]`**, verbatim from the source `nature` list. It is not
    linearised;
11. the referenced-classes vector and the union vector;
12. constants.

The field meanings in items 5–11 are INFERENCE from two classes. Their exact grammar is
**UNKNOWN** until a parser accepts all 554 classes.

*Update 2026-11-23:* `pim/psi/librarian.py` parses the trailer of all 1,455 held classes, in 11
packages, as 13 terms. These fields are now MEASURED and checked against source:

- the slot flags (0x10 attribute, 0x02 init predicate, 0x01 `is Class`);
- the kinds 0x26 (one, in kappa) and 0x37 (119 matched to kappa source);
- a dynamic-predicate field.

The two "unqualified natures" below are slot names, not natures. See `pim/psi/README.md`. Linearisation, method combination and the
method and slot hash tables are therefore the **loader's** job (TH App A p.244; KNOWN).

**Code samples.**

- `:putf(W,F):-!, :putf(W!win,F);` compiles to:
  - `dc 02`;
  - put atom `win`;
  - `blt 27 01 02 01` (slot read);
  - `74 01 02 00` plus the selector `putf/2`.
- Local switch tables are `hash op cd00 mask m, n keys` (e.g. `fep_command_code_table:convert/2`,
  95 keys; `kl0_tag:conv/2`, 49 keys).

**Dependencies on SIMPOS** (MEASURED, probe `C/tools/deps.py`, output `C/x/deps.txt`):

- 143 distinct `simpos##` classes are named by the held templates. The most named are
  symbolizer 142, string 101, process 90, font 84, as_program 55, standard_io_window 39, time 38,
  list 37, stream 32, library 32.
- All 554 trailers parse: each contains its own id and `template`.
- **Directly:** 172 of 554 classes name no `simpos##` class and have no unresolved unqualified
  nature.
- **Transitively:** following the held classes they name (qualified, or an unqualified local name),
  **102** have no path to `simpos##` or to an unheld package:

  | Package | Transitively free |
  |---|---|
  | paragraph | 55 (mostly icon/image data classes, `*_version`, `with_what_scroll`, `array_index_buffer`) |
  | pimmcsp | 33 |
  | mpsicsp | 7 |
  | pimmutil | 4 |
  | pimscsi | 2 (`scsi_common_if`, `scsi_macro_if`) |
  | pimfep | 1 (`fep_command_code_table`) |

- Two pimmcsp classes have unqualified natures (`my_node_manager`, `node_manager`) found in no
  held package.
- Caveat (the measurement is a lower bound on dependency): trailers only. It does not see
  unqualified non-nature class references outside the package, or messages sent to SIMPOS objects
  passed in at run time. "Free" means "names nothing outside", not "proven to run alone".

## 3. Firmware files: `PMPSI.DIR/syspsi`, `sysinit`, `sysidat`

KNOWN (psdpim `INSTALL`): these three are copied "to /usr/psi/simpos/csp as unix files on
PSI-III". So on the PSI-III (PSI/UX) the console side loads them from the Unix host, not from
SIMPOS.

MEASURED, new (`xxd`). The 256-byte header begins with three little-endian 32-bit words:

| File | Word 0 | Word 1 = count of 8-byte words | Word 2 | Size check |
|---|---|---|---|---|
| syspsi | 0x00000000 | 0x8000 | 3 | 256 + 0x8000·8 = 262,400 ✓ |
| sysinit | 0x5000 | 0x205e | 0x5000 | 256 + 0x205e·8 = 66,544 ✓ |
| sysidat | 0x6800 | 0x0410 | 0x5000 | 256 + 0x410·8 = 8,576 ✓ |

- Word 0 is probably the load address and word 2 is UNKNOWN.
- At byte 0x40 there is an **EBCDIC** stamp. syspsi reads `50.17 11-06'92`; sysinit and sysidat
  read `00.00 00-00'00`. So the stamp is version 50.17, dated 1992 (day/month order UNKNOWN).
- syspsi is the 32K-word control store. sysidat is the KL0 decode table, 1,024 entries indexed by
  class·256 + opcode (binary_reverse_engineering.md §4.2).
- sysinit is **UNKNOWN**: probably initial memory or register contents.
- Microword format: see the other agent's work.

## 4. Boot / IPL

**KNOWN, history.**

- TR-086 pp.8–10 and TR-087 pp.11–13: in 1984 the SIMPOS IPL was "implemented in ESP" and
  "included many modules of the kernel operating system and also run-time support routines of
  ESP".
- Modules are "separately compiled, partially linked and stored in flexible disks". Loading and
  **final linkage are done by the IPL on PSI itself**.
- The IPL reference is Ueda, Tojo and Kurokawa, *IPL Scheme of SIMPOS*, IPSJ 29th conf. 4E-9, 1984,
  in Japanese, **not held**.

**KNOWN, structure.** OVW lines 1047–1473: the kernel IPL has user, developer and system modes.

**MEASURED, the Pseudo-PIM boot script (not PSI-III SIMPOS boot).** `SYSTEM.DIR/boot.init` (dated 17-May-91) is a console
(CSP) command file: `power on`, `boot on`, `clear`, `init`, `impl /usr/psi/pimos/kl1/pimm.MEkbn`,
`patch pmpsi:pimm_patch.com`, `ipl pimos:pimm_ipl.kbn`, `ipl pimos:pimm_ipl.sym`, `start pimos 20c`.
JIS `!'` is a colon (logical-name prefix). Several arguments read "Don't care on Pseudo".

INSTALL puts this file in SIMPOS `me:`, so it is the script of the pseudo-CSP (an ESP program
running under SIMPOS) for booting PIM/m. It is **not** evidence of how the PSI-III console boots
SIMPOS. By analogy (INFERENCE) a console:

1. loads microcode (`impl`);
2. patches it;
3. loads a memory image with its symbol file (`ipl … .kbn/.sym`);
4. starts at an address.

The only PSI-III-side evidence is INSTALL's `/usr/psi/simpos/csp` line (§3).

The SIMPOS equivalent (the SIMPOS `.kbn` IPL image) is **not held**.

**UNKNOWN:**

- the `.kbn` IPL-image format beyond the microcode `.kbn` 5-byte words that the repo already reads;
- the start address;
- the initial register and PCB contents a SIMPOS image expects.

## 5. Text encoding (MEASURED, new)

SIMPOS text files hold **16-bit JIS X 0208** characters, ASCII letters included:

- row 0x23 for alphanumerics (`#b#o#o#t` = "boot");
- row 0x21 for symbols (`!!` = space, `!$` = `,` region, etc.).

Seen in `boot.init`, `login.com`, `usercom.init` and `PIMM.PARAM`. This matches ESP's default
`double_bytes` strings (ESP.md §1).

`login.com` names the SIMPOS tools of the PSI/UX environment as `simpos##` classes:

| Menu item | Class |
|---|---|
| debugger | `simpos##debugger` |
| pmacs | `simpos##pmacs` |
| file | `simpos##file_manipulator` |
| librarian | `simpos##librarian` |
| shell | `simpos##shell` |
| spooler | `simpos##spooler_manipulator` |
| pattern editor | `simpos##pattern_editor` |

It also shows logical names, e.g. `sys` = `>sys>csp>SYSTEM.DIR`.

## 6. Disk and file system

**KNOWN** (TR-524, *The SIMPOS Distributed File System*):

- Each volume has, in a fixed area, a **volume descriptor**: the volume id, a **VTOC**, the root
  directory file and a **free page pool**.
- The VTOC is an object storage of file objects (an "instance file").
- File blocks were one page, later four pages. The page size is 1 KB if "4K bytes" = 4 pages
  (INFERENCE).
- The i-node table and free-block map are cached in memory and written back on close.
- Path names look like `>sys>user>gee>humm.txt`, and global names are `Host::LocalName`.

TR-059 p.9 also describes the VTOC-as-object-storage idea.

**UNKNOWN:**

- every byte offset;
- the sector size;
- the descriptor and VTOC record layouts;
- the floppy formats.

No disk image is held, so **nothing about the on-disk format is MEASURED**. A reconstruction needs
either a held SIMPOS volume or must define its own format, which is acceptable only if the goal
does not require reading real PSI media.
