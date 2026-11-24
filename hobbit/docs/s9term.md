# `s9term`: the kernel image the 1st Edition ships

`tools/plan9-1e/hobbit/s9term` (550,846 bytes, sha256
`b0b85affdd16454fd35c97e0a24ef6421ae3f35380b9acc523a6e2c6d8a6786f`, in
`tools/SHA256SUMS`) is the one Hobbit kernel
image in `plan9-1e.tar.bz2`.  It is the oracle for A3's link
(`docs/plan9_boot_plan.md`).  Everything below is read from the file at
the offsets given; `python3 tools/p9exec.py tools/plan9-1e/hobbit/s9term`
prints the header and runs the checks, and `tests/test_p9exec.py` pins
each number in this document (both are in `tests/run_tests.sh`).

**Summary.**  It is a `zl -H1` image, not stripped (8,136 symbols and a
32,602-byte pc/line table), linked at 0x80004000 with entry `_startup`,
for the `term` configuration (21 devices, 4 streams), with an embedded
26,796-byte boot program.  It was built on **1992-11-07** (KERNDATE)
from sources *older* than the ones the release ships (dated 3 January
1993): files differ in which functions they define, and libc's `rune.c`
differs from the shipped `libc.a`.  So s9term fixes the format, the
layout rules, the configuration and the link order, but a kernel built
from the vendored sources will not be byte-identical to it.

## Header (offset 0x00..0x4f)

The link line (`sys/src/9/hobbit/mkfile`, `9bart 9term 9termlocal`):

    zl -o 9term -l -R4 -H1 -T0x80004000 -E0x80004000 \
        raml.z term.z bootterm.root.z libram.a -lgnot -lg -lc

`-H1` is zl's "boot" header (`zl/obj.c` main, `case 1`: `HEADR =
20L+60L`).  `zl/asm.c` `asmb` writes it, `case 1`, as twenty words with
`lput` (two big-endian `SPUT`s; `swizflag` is already 0, so unlike the
text these are not byte-reversed) -- a MIPS-style COFF file header and
optional header:

| word | offset | value | what asm.c writes |
|---|---|---|---|
| 0 | 0x00 | 0x01610000 | `0x161L<<16`: magic 0x161, 0 sections |
| 1 | 0x04 | 0 | time and date |
| 2 | 0x08 | 0x00046e84 | `HEADR+textsize+datsize` = 80 + 219,968 + 70,388 (the symbol table's offset) |
| 3 | 0x0c | 0x000379e0 | `symsize`: 227,808 bytes = 8,136 records of 28 |
| 4 | 0x10 | 0x00380007 | optional-header size 0x38, flags 7 |
| 5 | 0x14 | 0x0197011f | `(407<<16)\|0437`: decimal 407 = 0x197 (the Z_MAGIC number), version 0x11f |
| 6 | 0x18 | 0x00035b40 | text 219,968 |
| 7 | 0x1c | 0x000112f4 | data 70,388 |
| 8 | 0x20 | 0x000180ac | bss 98,476 |
| 9 | 0x24 | 0x80004000 | entry (`-E0x80004000`) |
| 10 | 0x28 | 0x80004000 | text base (`-T`) |
| 11 | 0x2c | 0x80039b40 | data base = text base + text (`-R4`, no `-D`) |
| 12 | 0x30 | 0x8004ae34 | bss base = data base + data |
| 13 | 0x34 | 0xffffffff | "gp reg mask" |
| 14 | 0x38 | 0x00007f5a | `lcsize`: pc/line table 32,602 bytes |
| 15-17 | 0x3c | 0 | |
| 18 | 0x48 | 0xffffffff | "gp value ??" |
| 19 | 0x4c | 0 | "complete mystery" |

The file is exactly `80 + text + data + syms + lcsize` = 550,846 bytes:

| section | file offsets | addresses |
|---|---|---|
| text | 0x00050..0x35b8f | 0x80004000..0x80039b3f |
| data | 0x35b90..0x46e83 | 0x80039b40..0x8004ae33 |
| bss | (none) | 0x8004ae34..0x80062edf (`end` = 0x80062ee0) |
| symbols | 0x46e84..0x7e863 | |
| pc/line | 0x7e864..0x867bd | |

There is no padding between sections (`asmb` case 1 seeks to
`HEADR+textsize`, then `HEADR+textsize+datsize`).  The text is stored as
in a user binary -- little-endian 32-bit words, the earlier parcel in
the high half (`cflush` swizzles while `swizflag` is set) -- and the
data as the target's little-endian words, unswizzled.  The first parcels
at the entry, `2c04 2c03 2c00 c6f7 …`, are `raml.s:13-14`'s `FLUSHP;
FLUSHI` (niladic 0x0B subcodes 4, 3) and the `CPU` escape of `MOV
$(PM|PE|IE|SE|PX|KL), %CONFIG`.

The linker-defined symbols agree with the header: `etext` 0x80039b40,
`bdata` 0x80039b40, `edata` 0x8004ae34, `end` 0x80062ee0 (`pass.c:84-86`).

## Symbols: not stripped

8,136 entries of 28 bytes (`putsymb`: 4-byte big-endian value, type,
20-byte name, 3 pad).  By type: `T` 874, `t` 186, `D` 188, `d` 126,
`B` 65, `b` 31, `f` 132 (file-name components), `z` 1,470 (include
history), `p` 2,096, `a` 1,909, `m` 1,059 (params, autos, frames).
Every `T/t` value lies in the text and every `D/d/B/b` value in
data+bss (`check_kernel`).

The `z` records carry each function's file and include history (indices
into the `f` names), which is how the per-file statements below are
made: the first function of each object carries its history.

## What the image says about its build

### KERNDATE

`kerndate` (`D`, 0x80039c74, file offset 0x35cc4) = **721,110,517** =
1992-11-07 04:28:37 UTC.  mkdevc emits `ulong kerndate = KERNDATE;`
and the mkfile compiles `$CONF.c` with ``'-DKERNDATE='`{date -n}``.

### Configuration: `term`

* `conffile` (0x80039c40, file 0x35c90) points at 0x8004acf6 (file
  0x46d46): `"term"`.
* `devchar` (0x80039b78, file 0x35bc8) points at 0x8004ace0 (file
  0x46d30): the 21 bytes **`/ce|psMd2trikSwlaPIbT`** and a NUL -- one
  character per device in the order of `sys/src/9/hobbit/term`'s `dev`
  section: root cons env pipe proc srv mnt dup iic eia rtc incon dk scsi
  wren ether arp iproute ip bit kprof.
* `devtab` (0x800469a4, file 0x429f4): 21 entries of 13 function
  pointers; the reset pointers are `rootreset`, `consreset`, …,
  `kprofreset` in the same order.
* `streaminit` (`T`, 0x800043d6) calls `newqinfo` with `urpinfo`
  (0x80045724), `ipinfo` (0x80047cd4), `asyncinfo` (0x8003e304),
  `fcallinfo` (0x8003e434): `term`'s `stream` section, in order.
* `term`'s `port` section: `cpuserver` = 0 (0x80039ca0), `islcd` = 1
  (0x80039be0), `cfslen` = `fslen` = 0.

**`devchar` is bytes, the vendored `mkdevc` emits runes.**  The shipped
`sys/src/9/port/mkdevc` writes `Rune *devchar=L"…"`, and `Rune` is a
`ushort` (`hobbit/include/u.h:7`), so a kernel built from it would hold
2-byte characters there.  The image holds 1-byte ones: the `mkdevc` that
built it emitted a `char` string.  That is the first sign of the drift
below.

### The boot program (`bootterm.root.c`) and `initcode`

* `bootcode` (0x8003e48c, file 0x3a4dc), `bootlen` (0x80039ba4) =
  **26,796**.  `mkroot` strips `boot.out` and dumps its bytes, so the
  array is a whole 1e executable with its big-endian `Exec` header:
  magic 0x197, text 0x5cf8 (23,800), data 0xb94 (2,964), bss 0x4d0,
  syms 0 (stripped), entry 0x66d2, spsz 0, pcsz 0; 32 + 23,800 + 2,964
  = 26,796 = `bootlen`.  The protocols compiled into it are `term`'s
  `boot` section (il tcp incon 9600 19200); the binary itself is not
  analysed here.
* `initcode` (0x80047b6c, file 0x43bbc): magic 0x197, text 0x14, data
  8, bss 0, syms 0, entry 0x1020 -- the 60-byte `initcode` program
  `init.h` embeds (`zl -l -s -H2 -T0x1020 -R4`, mkfile).

### Link order and library members

Text order is load order: zl lays objects out as it reads them, and
reads an archive (`obj.c` `objfile`) by scanning its `__.SYMDEF` from
the start, loading the member that defines each still-undefined symbol
it meets, and rescanning until a pass loads nothing.  So within one
archive members appear in symbol-table order, and a member needed only
by one loaded later in the same pass comes after it.

| from | first function (address) | members, in text order |
|---|---|---|
| `raml.z` | `_startup` 0x80004000 | `raml.s` |
| `term.z` | `streaminit` 0x800043d6 | `term.c` (`consdebug`) |
| `bootterm.root.z` | (data only) | `bootterm.root.c` |
| `libram.a` | `pusharg` 0x80004422 | rammain mmu page pgrp proc qlock sysproc devroot devcons devenv devpipe devproc devsrv devmnt devdup deveia devrtc devincon devdk devscsi scsi devwren deviic devether devarp deviproute devip tcpinput tcpoutput tcptimer tcpif stil devkprof sturp stip stasync stfcall stream fcall scsibuf screen devbit trap alarm alloc chan clock dev fault taslock segment swap net print queue sysfile bbmalloc |
| `-lgnot` | `_setdda` 0x800346c4 | gsegment gaddr gpoint gsubfstring gtexture gbitblt gbitbltclip (and `defont0`, data only) |
| `-lg` | `add` 0x80038272 | arith clipline rectclip |
| `-lc` | `abs` 0x80038992 | abs atol crypt memchr memcmp rune strcat strncpy strtol strtoul utflen utfrune, then memmove.s memset.s strchr.s strcmp.s strcpy.s strlen.s strncmp.s |

The `-lg` and `-lc` members are in the shipped archives' member order
(indices 2, 10, 26 in `libg.a`; 62 … 137 in `libc.a`); `-lgnot`'s are
not (`gbitbltclip`, member 5, follows `gbitblt`, member 11; `defont0`,
member 1, comes last), which is the second-pass case above.  Every
library member named here exists in the vendored `libg.a`, `libgnot.a`
and `libc.a`.

Not linked, though `mkfile`'s `OBJ` puts them in `libram.a`: `latin1`,
`fprt0`, `fpihobbit`, `fpi` (nothing referenced them) and `kbd.c` (see
below).  `libram.a`'s own order is not recoverable from the image: only
the members loaded, in the order they were needed.

**The interrupt stubs at the end of the text.**  `_vectorD` is at
0x800042ac, in source order, but `_vectorC` … `_vector0` (raml.s:182-230)
are at 0x80039abe..0x80039b3f, after libc.  Each stub is `MOV $n, R0;
JMP _exception`.  `pass.c` `xfol` drops a `JMP` whose target has not
been placed and continues at the target (pass.c:240-247), so
`_vectorD`'s jump pulls `_exception` and everything after it into line;
the remaining stubs are placed only once the rest of the program has
been, where their jumps go back to the `_exception` already placed.  This
matches the layout; the exact path through `xfol` that places them last
has not been traced step by step.

## Not the shipped sources

The image was built from an earlier revision of the kernel and libc than
the one the release ships.  Evidence, beyond KERNDATE (1992-11-07 vs the
tree's 1993-01-03) and `devchar` above, from comparing the functions the
image defines per source file (its `z` history) with the `TEXT` lines
and C function definitions of the vendored files:

| file | in the vendored source only | in the image only |
|---|---|---|
| `raml.s` | `getcpureg` (raml.s:322) | |
| `deveia.c` | `eiagetport`, `eiarawput`, `eiasetparity`, `eiasetrts` | |
| `scsi.c` | `ctlrreset`, `issue`, `scsiio`, `scsipanic`, `scsiregs`, `scsistatus` | |
| `scsibuf.c` | `scsialloc` | |
| `devether.c` | `etherintr` | `interrupt` |
| `port/devbit.c` | `bitdepth`, `pixreverse` | `bitreverse` |
| `port/devip.c` | `tcproominq` | |
| `port/proc.c` | `unbreak` (proc.c:493) | |

(An earlier version of this table also listed `eiarawprint`,
`eiarawputc` and `eiarawputs` for `deveia.c`; they are inside `#ifdef
notdef` (deveia.c:117-154), so no build defines them.  Found by the
link below, whose function sets give this table exactly.)

and the vendored `screen.c` calls `getcpureg` and `kbdinit` (screen.c:
174-178, 246), neither of which the image has: its `screen.c` predates
`kbd.c`.  The other 50 of the 58 files compared define the same function
names in both (names only; bodies are not compared).

Library code: of the libc functions both s9term and the shipped
binaries (`zc rc zl za mk`, linked against the January `libc.a`)
contain, these have the same size in s9term as in every binary that
has them -- `atol strcat strncpy utfrune memcpy memset strchr strcmp
strcpy strlen strncmp memcmp` -- and these do not: `chartorune` 182 bytes in s9term vs 200 in
all five binaries, `runetochar` 158 vs 176 (`rune.c` changed), `utflen`
48 vs 44 and `memmove` 600 vs 596 (possibly padding before the next
function; not resolved).

**Consequence for A3.**  A link of the vendored sources can be checked
against s9term's *format* (`p9exec.check_kernel`), its configuration
(device and stream lists, conffile, `devtab`), its layout rules (text
base, data rounding, load order) and its library member set, but not
byte for byte.  A byte-exact oracle would need the November 1992
sources, which the release does not contain.

## How these numbers were obtained

* Header, sections, symbols, `etext/bdata/edata/end`: `tools/p9exec.py`
  (`read_kernel`, `kernel_symbols`, `check_kernel`).
* KERNDATE, `devchar`, `conffile`, `devtab`, `streaminit`, `bootcode`,
  `initcode`: `tests/test_p9exec.py` (`TestBuildFacts`), at the offsets
  above.
* Per-file function sets and the library order: the image's `z`/`f`
  history decoded per function, now `tools/p9kcmp.py` (`Image.objects`;
  `tests/test_p9kcmp.py` pins the link-order table above).  The
  function-size comparison was a scratch script and is not in the suite.

## A kernel linked from the vendored tree

`python3 tools/p9kbuild.py link --kgen K` (docs/plan9_boot_plan.md A3)
links `9term` with the release's `zl` on the reference model, and
`python3 tools/p9kcmp.py 9term` compares it with s9term: every item the
format, the link line, the `term` configuration and the generated files
fix agrees (header, entry `_startup`, object and library order,
`kerndate`, `conffile`, `devchar`'s characters -- two bytes each there,
as said above -- `devtab[]`, the stream list, `initcode`); the sizes
differ (text +4,268 bytes, accounted for object by object) and the
functions defined only in one of the two images are exactly the
"Not the shipped sources" table.  `-lgnot`, `-lg` and `-lc` load the same
members in the same order as s9term.

It boots: `tools/p9join.py --image` runs it on the reference model with
its root from the 1e server through A5's command script, the screen
s9term's except for pageinit's line; what the drift above changes at run
time (the kbd.c keyboard on Quart channel 2, no serial console, the 25
Hz clock) is tabled in docs/p9boot.md, "Our 9term".
