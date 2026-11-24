# A 1st Edition Plan 9 file server in QEMU

The Hobbit kernel `s9term` is a 1e *terminal*: its `/boot` takes its
root from a file server (`docs/s9term.md`; boot section `il tcp incon
9600 19200`).  1e speaks the 1993 9P (Tnop, Tsession, 28-byte names),
which no current server speaks, so the server is 1e itself: the 386
port from the same `plan9-1e.tar.bz2`, run in `qemu-system-i386`.

**Status 2026-11-23.**

| step | result |
|---|---|
| 1. how 1e PC was started; what QEMU must present | worked out from the sources, below |
| 2. boot a shipped kernel to its console | **yes**: the distribution floppy's `9dos` boots to `rc` |
| 3. a kfs with the 1e release on it, made by 1e's tools | **yes**: 1e's `disk/kfs -r` + `disk/mkext`, whole release (12,131 files, 391,570,750 bytes, every path and length checked over 9P), 11m24s |
| 4. serve it; probe it from the host | **yes over TCP 564**: `p9probe.py` Tnop/Tsession/Tattach/walk/read, four files byte-identical to the tarball |
| 4'. the terminal boot path over IL 17008 | **yes**: the shipped `9pc` in a second QEMU, joined by a `dgram` netdev, gets BOOTP from 1e's `ip/bootp`, mounts its root over IL 17008, runs `/386/init` and the release's `termrc` from the kfs, and lists `/hobbit` at its `%` prompt |
| 5. CPU server | not done; what it takes is below |

Three bytes-level patches to the shipped kernels were needed for QEMU's
devices, each found with a QEMU trace (below).  Every path and length
of the release is served (checked over 9P, section 4; eight files also
byte-compared against the tarball), but the kfs is not a copy of
the 1993 file server's metadata: the mkfs archive format has no time
field, so every file is dated at provisioning; owner and group are all
`sys`; and modes are the tarball's owner bits copied to group and other
(section 3).

Everything is reproduced by `tools/qemu1e/build.sh` (tarball to
provisioned disks) and checked by `tools/qemu1e/probe-tcp.sh` and
`tools/qemu1e/il_term_test.py`.  Artifacts go under `build/qemu/`
(gitignored).  No download: the only input is the tarball already in
the project (`/tmp/p9/plan9-1e.tar.bz2`, sha256
`8718e279aa35b10a9391f330976d31c177bad00de40e7f0f67232ffa54fb7d77`,
`docs/plan9_port.md`); no DOS was needed.

## 1. How a 1e PC was started

From `sys/doc/pcconfig.ms` (Presotto, "Configuring a PC"):

* The release ships a 1.44 MB floppy image, `sys/lib/pcdisk`, "a stand
  alone Plan 9 system that uses the DOS file system on the floppy as its
  own file system".  Its tree is also in `sys/lib/pc/`.
* From DOS: `C> a:b.com`; `b.com` asks where to boot from, default
  `fd!0!9dos` (`sys/src/boot/pc/bmain.c` `main`, `booter[]`: `h!x!y`
  Plan 9 partition, `fd!x!y` / `hd!x!y` DOS file).
* The kernel asks `root is from (tcp, il, local)[local]`, then
  `user[none]` and `password` ("it'll believe any 8 character password").
* A hard disk is then partitioned with `disk/prep` and made a kfs with
  `disk/kfs -rf /dev/hd0fs` (steps 25-30).

The shipped kernels (configurations in `sys/src/9/pc/`):

| file | config | boot methods (observed prompt) | root |
|---|---|---|---|
| `sys/lib/pc/9dos` (on the floppy, stripped, 348,584 bytes) | `dos` | `(local, il, tcp)[local!#f/fd0disk]` | `local` execs `/fs` = the embedded `dossrv` (`misc dossrv.root`) on the floppy |
| `386/9dos` (572,868 bytes, symbols) | `dos` | same | same |
| `386/9pc` (583,255 bytes, symbols) | `pc` | `(il, tcp, 9600, 19200, incon)` | network only |

All three have `cpuserver = 0` (the `port` section of each config).
No shipped kernel embeds kfs as its boot root: `kfs.root` is in the
`misc` of `pcdisk`, `nomad` and `3170disk` only, none of which is
shipped built.  So the server boots `9dos` with the floppy as root and
runs kfs as a second file system (section 3).

Devices the `pc`/`dos` kernels drive (`dev` sections; `sys/src/9/pc/`):

| device | driver | QEMU |
|---|---|---|
| console | CGA text at 0xB8000 + PC keyboard (`cga.c`, `devvga.c:812 screenputs`, `kbd.c`); no serial console (`devuart.c` `uartspecial`'s only caller is the serial mouse, `kbd.c:278`) | `-vga std`, read by QMP `pmemsave`, typed by QMP `send-key` |
| disk | `devhard.c`: AT/IDE at 0x1F0, IRQ 14, CHS from IDENTIFY words 1/3/6, drives from CMOS 0x12 | `-drive if=ide` (two drives: see 2b) |
| floppy | `devfloppy.c` | `-drive if=floppy` |
| ether | `devether.c` probes WD8003, 3C503, NE2000 (`ether2000.c`: I/O 0x300..0x360, IRQ 2 = 9), 3C509; one controller | `-device ne2k_isa,iobase=0x300,irq=9` |
| serial | `devuart.c` `#t/eia0,1` | `-serial` |

Memory is sized by probing up to 16 MB (`main.c confinit`, `i<17`):
`-m 16` gives `2800 free pages, 11200K bytes`.  QEMU machine `isapc`,
CPU `486`.

## 2. Booting without DOS

`tools/qemu1e/mkfloppy.py`.  The floppy's boot sector (from
`disk/format`, `sys/src/cmd/disk/format.c bootprog`) loads the file in
the *first* root-directory slot, if it is `PLAN9   SYS`, to 0x0800:0000
and jumps there (disassembled: compare at 0xd7-0xe1, load of 128
sectors at 0x11a-0x13c, `ljmp $0x800,$0` at 0x14d).  `format -b` writes
`/386/b.com` there (`format.c:370`), but the shipped image was made
without it: slot 0 is `B.COM`, and there is no `PLAN9.SYS`.

b.com is a DOS .COM: `sys/src/boot/pc/l.s` copies DS:0000.. to 0x80000
and jumps to 0x8000:lowcore, lowcore linked at 0x8008011d, i.e. it
expects the image at DS:0100 behind a PSP.  So `PLAN9.SYS` is b.com
behind a 256-byte prefix starting `jmp 0x100` (e9 fd 00) that stands in
for the PSP, placed in slot 0 and contiguous.  This is the one
substitution in the boot path, in place of DOS.  Observed:

```
cmdreadywait failed 0x0
cmdreadywait failed 0x0
Choose one of the following boot methods
        h!x!y - boot from Plan 9 hard disk 'x' partition 'y'
        fd!x!y - boot from DOS floppy disk 'x' file 'y'
        hd!x!y - boot from DOS hard disk 'x' file 'y'

boot from[default==fd!0!9dos]:
```

then, after Return (the kernel clears the screen):

```
2800 free pages, 11200K bytes, swap 46400K, highwater 560K, headroom 700K
NE2000 I/O addr 300 width 16 addr 4000 size 16384 irq 2: 52 54 00 12 34 56
root is from (local, il, tcp)[local!#f/fd0disk]:
user[none]: glenda
password:
        The Plan 9 distribution floppy is configured to bring
        ...
init: starting /bin/rc
% ls -l /
d-rwxrwxrwx M 5 bill   trog      0 Dec 22 12:25 /386
--rw-rw-rw- M 5 bill   trog 348584 Dec 22 12:25 /9dos
...
```

(The NE2000 line appears with the patched kernel and `-device ne2k_isa`.)

### 2a. Three QEMU differences, patched in the kernel

`tools/qemu1e/patch_kernel.py` applies each as a byte-pattern match on
8c's code for one source line, requiring exactly one match; all three match once each in the floppy
`9dos`, `386/9dos` and `386/9pc` (`386/9dos`: file offsets 0x23ae7/
0x23af1, 0x1ef49, 0x1e44b, the same as `9pc`).  The patched kernels
exist only under `build/qemu/`; `tools/qemu1e/SHA256SUMS` pins the four
inputs and the three patched outputs, and `build.sh` checks it.  The
floppy images and disks are not pinned: `mcopy` stamps files with the
host time, and `fs.img` is written by a running kfs (and both depend on
those dates).

1. **NE2000 PROM** (`ether2000.c reset`).  The probe reads the station
   PROM with 16-bit DMA into `ushort buf[16]` and requires
   `buf[0x0E] == 0x57 && buf[0x0F] == 0x57`.  QEMU's NE2000 doubles each
   PROM byte into both halves; `-trace ne2000_*` shows data-port reads
   `0x5252 0x5454 0x0000 0x1212 0x3434 0x5656 ... 0x5757 0x5757`, and the
   unpatched kernel says `#l: no free devices`.  Patch: the two
   `movzwl` become `movzbl` (compare the low byte).
2. **IDENTIFY race** (`devhard.c hardident`/`hardintr`).  `hardintr`
   ends IDENTIFY with `cp->cmd = Cident2` and a `wakeup`; `hardident`
   sleeps on `cmddone` (`cp->cmd == 0`).  QEMU completes IDENTIFY and
   raises IRQ 14 inside the `outb` of the command, before the process is
   asleep (`-trace ide_*,pic_*`: one IRQ 14, 256 data words read, no
   further command; boot stops at `fs...`).  That the wakeup is lost
   because it comes first is *inferred* from the source; the trace shows
   only the IRQ, the data, and then nothing.  Patch: store 0 instead of
   Cident2, so `cmddone` is already true when `hardident` sleeps.
3. **Undrained probe sector** (`devhard.c hardprobe`).  hardprobe
   smallocs `buf` but never sets `cp->buf`, so `hardintr` skips the
   `inss` and the sector stays in the drive.  QEMU ignores commands
   while DRQ is set, so the next one (SET FEATURES) never interrupts
   (trace: status 0x58 after the probe, then 0xEF with no IRQ).  Patch:
   hardprobe's set-up sets `cp->buf = buf` (dropping a redundant
   `cp->dp = dp`; see the script's docstring).

### 2b. Two IDE drives

`cmdreadywait` polls the status register *before* selecting the drive
(`devhard.c:415-424`, then `Pdh` is written).  The BIOS leaves the slave
selected; with no slave QEMU reads status 0, and both b.com and the
kernel print `cmdreadywait failed` and find no disk.  With a second
drive attached the status is ready, and `#w` shows `hd0disk`,
`hd0partition`, `hd1disk`, `hd1partition`.  The second drive is used
anyway (the archive, below).  No patch.

## 3. The kfs, made by 1e

`tools/qemu1e/build.sh`:

* `mkdisk.py --fs 1024`: a 1 GB raw image, whole 16x63 cylinders (the
  geometry QEMU reports and devhard uses: a 64 MiB image appears as
  67,092,480 bytes), with the partition table `disk/prep` would write
  (`prep.c write_table`: `plan9 partitions\nfs 0 2096639\n`) in the
  sector `hardpart` reads (`cap/512-1`, `devhard.c:824-890`).
* `mkarchive.py`: the release (plus `tools/qemu1e/overlay`, below) as a
  `disk/mkfs -a` archive, in mkfs's header format
  (`mkfs.c:395-399`: `"%s %luo %s %s %d\n"`, owner/group `sys` as mkfs
  defaults, data after each file header, `end of archive`), attached raw
  as the second drive.  `/adm` comes first.  It is read from the
  tarball, not from the host extraction: the release has 33 names that
  differ from another only in case (`sys/src/cda/lde` and `LDE`,
  `devpost/Hb` and `HB`, `*/bin/cda/lde`, `rc/bin/ape/cc`, ...), and the
  case-insensitive macOS extraction silently keeps one of each pair (35
  tarball entries lost; the first provisioning, from the extraction, had
  12,097 files).  The files `floppies.sh` takes from the extraction are
  not among them (`SHA256SUMS`).
  `--list` writes every path and length for the probe's walk (section 4).
* On the floppy system, `/kfsinit` (`kfsinit.rc`): `disk/kfs -r -f
  /dev/hd0fs`, `disk/kfscmd allow`, `disk/mkext -u -d /n/kfs /adm`,
  `disk/kfscmd user` (load the release's `/adm/users`; after a ream kfs
  maps `sys` to `none`), `disk/mkext -u -d /n/kfs` (everything), `sync`.

The writer of the archive is a host script; the file system, its
format, and every write into it are 1e's kfs and mkext from the floppy.
Result (`build.out`, 2026-11-23, 11m24s for the whole build):
734 dirs, 12,131 files, 391,570,750 data bytes (the release plus the
three overlay entries of that build; the `usr/none` entries came
later and were put on the built image with `overlay.sh`, so these
counts predate them, and a fresh `build.sh` with them has not been run);
`ls -l /n/kfs` shows the release's top level owned by `sys`; mkext's
stderr is kept in the kfs as `/adm/mkext.log`, which holds only
`done` (5 bytes): no errors.  The probe's `--walk` (section 4) checks
the result from the guest side.  kfs's block size is its
default after a ream, 1024 bytes (`devwren.c:71`), which allows files up
to about 65.8 MB; the largest in the release is under 60 MB.

## 4. Serving

`/serve ipaddr ipmask` (`serve.rc`, on the floppy) starts kfs on
`hd0fs`, mounts it at `/n/kfs`, runs `ip/ipconfig`, 1e's `ip/bootp`,
and `aux/listen il` / `aux/listen tcp` with the kfs's
`/rc/bin/service.9fs` as the *trusted* directory (`-t`; `-d` names a
directory that does not exist, so nothing runs untrusted as `none`).
The two services are qemu1e additions to the served tree
(`tools/qemu1e/overlay/rc/bin/service.9fs/`; the release has no
`il17008`, and its `tcp564` uses exportfs's tree-name preamble):

* `il17008`: bind the kfs's `/386/bin` and `/rc/bin` onto its `/bin`,
  `#c` onto its `/dev`, the kfs onto `/`, `exec /bin/exportfs -s`.
  `-s` serves `/` with no preamble, and `exportsrv.c` answers Tnop and
  Tsession with 3-byte replies, which `boot/nopsession.c` requires.
* `usr/none/lib/profile` (empty) and `usr/none/hello.s`: the user
  `none`'s home, as 1e's own PC install floppy has it
  (`sys/lib/pc/usr/none/lib/profile`, a 0-byte file; the release's
  `/usr` has only `tor`), plus the test program of `tests/p9/hello.s`
  for the Hobbit's `za` (docs/p9boot.md "The user").  mkarchive.py
  makes the directories mode 777 (owner bits copied), so `none` can
  write there through exportfs.
* `tcp564`: the same plus `#Itcp` on `/net` and `-c $3/ctl`, which
  pushes the `fcall` line discipline on the server's end of the TCP
  connection (`exportfs.c pushfcall`; the terminal's `connecttcp`
  pushes it on its end).

exportfs's stderr goes to `/adm/{il17008,tcp564}.err` in the kfs:
`listen` dups the connection onto fd 2 (`listen.c newcall`), and the
first attempt's `bind` errors arrived as the "9P" reply.

### The host probe (TCP)

`tools/qemu1e/probe-tcp.sh` boots the server on QEMU user networking
(`-netdev user,net=10.0.2.0/24,hostfwd=tcp:127.0.0.1:5640-10.0.2.15:564`)
and runs `p9probe.py`, which builds the 1e messages from
`sys/include/fcall.h` and `convS2M.c` (little-endian, NUL-padded 28-byte
names, no length prefix; replies split by their fixed sizes, Rread by
its count) and replays what `/boot` sends: Tnop and Tsession with tag
NOTAG, then the mount driver's Tattach (`devmnt.c mattach`: uname,
aname `""`, auth all zero).  Observed:

```
Tnop     T 32ffff
         R 33ffff
Tsession T 34ffff
         R 35ffff
Tattach  T 3a010001006e6f6e650000000000000000000000000000000000000000000000...
         R 3b01000100010000801f000000
root qid path 0x80000001 vers 31
/ has 31 entries:
  adm/ sys sys 0
  _conform.map sys sys 61448
  386/ sys sys 0
  ...
  hobbit/ sys sys 0
  ...
lib/ndb/local: Tstat local sys sys mode 666 length 1414; read 1414 bytes; identical to host copy
hobbit/s9term: Tstat s9term sys sys mode 777 length 550846; read 550846 bytes; identical to host copy
386/9pc: Tstat 9pc sys sys mode 777 length 583255; read 583255 bytes; identical to host copy
rc/bin/termrc: Tstat termrc sys sys mode 777 length 1781; read 1781 bytes; identical to host copy
sys/lib/troff/font/devpost/Hb: Tstat Hb sys sys mode 666 length 1777; read 1777 bytes; identical to host copy
sys/lib/troff/font/devpost/HB: Tstat HB sys sys mode 666 length 1775; read 1775 bytes; identical to host copy
sys/src/cda/lde/main.c: Tstat main.c sys sys mode 666 length 2705; read 2705 bytes; identical to host copy
sys/src/cda/LDE/main.c: Tstat main.c sys sys mode 666 length 2907; read 2907 bytes; identical to host copy
adm/mkext.log: Tstat mkext.log none none mode 666 length 5; not in the release; contents b'done\n'
walk: server has 13419 paths, list 12865; missing 0, length differs 0, extra 554
  extra /adm/mkext.log 5
  extra /adm/tcp564.err 0
  extra under /bin (bound in by the service): 507
  extra under /dev (bound in by the service): 22
  extra under /net (bound in by the service): 23
PASS
```

The "host copy" is the tarball member (`p9probe.py` reads the tarball
when given one), so the two case-collision pairs are compared with the
release, not with the folded extraction.

The walk (`p9probe.py --walk build/qemu/release.list`) reads every
directory of the served tree over 9P and compares every path and length
with what `mkarchive.py` wrote: none missing, none differing.  The 554
extra paths are what the `tcp564` service binds in (the 386 and rc
binaries unioned on `/bin`, `#c` on `/dev`, `#Itcp` on `/net`) plus
`/adm/mkext.log` and `/adm/tcp564.err`, both written by the server.
Both test machines run with `-snapshot`, so `fs.img` stays as built.

### Transport for the Hobbit terminal: Ethernet, IL 17008

s9term's boot methods are `il tcp incon 9600 19200`
(`hobbit/term`; `docs/s9term.md`), default `il`.

* **Serial is rejected.**  `9600`/`19200` (`boot/async.c configasync`)
  push `async` and `dkmux` on the line and then `dkconnect()`
  (`boot/dk.c`): a Datakit call through a Datakit controller, not a 9P
  byte stream.  Nothing in the tree plays the controller.
* **IL** (`boot/ip.c connectil`): BOOTP broadcast to UDP 67, ARP, then
  `il!fs!17008` with no line discipline; 9P messages are IL messages.
  If the user is not `none`, `/boot` first dials `il!auth!17024`
  (`userpasswd.c`); a `none` boot skips it.  Observed with user
  `glenda` (`TERMUSER=glenda il_term_test.py`): this server's
  `aux/listen il` accepts the call and refuses it, logging `il: unknown
  service 'il17024' from '10.9.0.3!5000': file does not exist` (there is
  no auth server); `/boot` prints `boot: password not checked!: file does
  not exist` and goes on: 2 s from the user prompt to `init: starting`,
  `/dev/user` is `glenda`, and the same `ls` passes.  (With nothing at
  all listening on IL, the dial would instead wait for IL's timeout.)
  An unanswered ARP for the fs, auth or gateway address hangs `/boot`
  for ever (`ip.c arp`, no retry bound).
* **TCP** (`connecttcp`): port 564 with `fcall` pushed.  Also served.

The Hobbit's Ethernet chip is the National DP83932 SONIC
(`sys/src/9/hobbit/devether.c:1-4`, `io.h:165-208`: registers at
0xA4400000, IRQSONIC 9, 32-bit descriptors); the model needs a SONIC to
use either IP method.

**The netdev.**  The server's NE2000 is attached to a QEMU `dgram`
netdev: one Ethernet frame per UDP datagram, no other framing.

```
-netdev dgram,id=n0,local.type=inet,local.host=127.0.0.1,local.port=10901,remote.type=inet,remote.host=127.0.0.1,remote.port=10902
-device ne2k_isa,iobase=0x300,irq=9,netdev=n0,mac=52:54:00:12:34:56
```

The terminal side (a second QEMU in the test, the Hobbit model's SONIC
later) sends its frames to 127.0.0.1:10901 and receives on 10902.

**BOOTP.**  1e's `ip/bootp` (`sys/src/cmd/ip/bootp.c`) runs on the
server.  It answers a request only if `/lib/ndb/local` has an entry with
the client's `ether=` and a `bootf=` (`main`, `lookup`), and fills the
vendor field with `"p9  ipmask fs auth ipgw"` (`doreply`), which is what
`/boot` parses (`ip.c ipconfig`: `vend` must start `p9  ` and have four
fields).  `ipinfo` (`sys/src/libndb/ipinfo.c`) takes `fs=`, `auth=`,
`ipgw=` from the client entry or from its subnet, which it finds through
the *class* network's `ipmask`: for 10.9.0.0 that is an `ip=10.0.0.0
ipmask=255.255.255.0` entry.  Without it the first run's reply was
`p9  255.0.0.0 0.0.0.0 0.0.0.0 0.0.0.0` and the terminal ARPed for
0.0.0.0 for ever (seen in `server.pcap`).  `tools/qemu1e/ndb.local` is
appended to the floppy's `/lib/ndb/local`: the network, `fs9`
(10.9.0.1, ether 525400123456), `hobbit` (10.9.0.2, ether
**525400000b0b, a placeholder** for the model's SONIC address,
`bootf=/hobbit/s9term`), `term386` (10.9.0.3, ether 525400123457).
After the root is mounted, `/boot` calls `newkernel()` on a terminal
(`boot.c:115-116`, `cpuflag == 0`), not with the BOOTP file but with
`/<cputype>/9<conffile>` against the first 128 bytes of
`<bootdisk>boot` (`newkernel.c`; `bootdisk` defaults to `#w/hd0`,
`mkboot:66`).  It returns silently if either cannot be opened.  `conffile` is the
second word of `$terminal` (`aux.c getconffile`), but whatever it is,
the release's `/hobbit` holds no `9*` file (only `s9term`, `init`,
`mkfile` and directories), so for the Hobbit nothing happens.  On a
mismatch it would ask `This kernel is out of date.  Copy a new one to
disk?` and, on `y`, overwrite the boot partition.  `bootf=` is needed
only because `bootp` will not answer without it.

### IL: a 9pc terminal boots from the server

`tools/qemu1e/il_term_test.py`: the server as above, and a second QEMU
running the shipped `9pc` (the `pc` terminal configuration, patched,
stripped to fit the floppy: `fd-term.img`) on the other end of the
dgram pair, answering `root is from` with `il` and `user` with `none`.

Observed (`build/qemu/il.out`, 2026-11-23), terminal console:

```
2800 free pages, 11200K bytes, swap 46400K, highwater 560K, headroom 700K
NE2000 I/O addr 300 width 16 addr 4000 size 16384 irq 2: 52 54 00 12 34 57
root is from (il, tcp, 9600, 19200, incon)[local!#f/fd0disk]: il
user[none]:
arp: rcvd for 10.9.0.1
nop...session...time...
init: starting /bin/rc
/bin/dossrv 21: serving #s/dos
gnot: Jan  3 07:00:18: none: ip/ipconfig: lookup: my ip address
Microsoft compatible mouse
Can't cd /usr/none
lib/profile: rc: .: can't open
init: rc exit status: rc 9:can't cd
init: starting /bin/rc
% cat /dev/user; echo; ls -l /hobbit; ls /rc/bin/service.9fs
none
d-rwxrwxrwx M 4 sys sys      0 Jan  3 07:03 /hobbit/bin
d-rwxrwxrwx M 4 sys sys      0 Jan  3 07:04 /hobbit/include
--rwxrwxrwx M 4 sys sys  50636 Jan  3 07:03 /hobbit/init
d-rwxrwxrwx M 4 sys sys      0 Jan  3 07:04 /hobbit/lib
--rw-rw-rw- M 4 sys sys    108 Jan  3 07:03 /hobbit/mkfile
--rwxrwxrwx M 4 sys sys 550846 Jan  3 07:03 /hobbit/s9term
/rc/bin/service.9fs/il17008
/rc/bin/service.9fs/tcp564
%
```

and the server's syslog lines:

```
fs9: Jan  3 07:00:17: glenda: /n/kfs/386/bin/ip/bootp: reply to 10.9.0.3 525400123457 /386/9pc p9  255.255.255.0 10.9.0.1 10.9.0.1 10.9.0.1
fs9: Jan  3 07:00:18: glenda: /n/kfs/386/bin/aux/listen: il call for il17008 on chan /net/il/1
```

`server.pcap` (QEMU `filter-dump` on the server's netdev): 2 BOOTP, 2 ARP
(`who-has 10.9.0.1 tell 10.9.0.3`, `is-at 52:54:00:12:34:56`), then
1,121 IL (IP protocol 40) packets.  `nop...session...time...` is
`/boot`'s own progress (`nopsession.c`, `settime.c`); `Can't cd
/usr/none` is the release having no `/usr/none`.

Notes on the terminal: the release's `termrc` (case `generic*`, the
`ident` of a QEMU PC) runs `aux/mouse 1`, which waits for a serial
mouse on COM2; without one it never returns and no prompt appears, so
the test gives the terminal QEMU `-serial msmouse` as its second port.
Its `ip/ipconfig` complains (`lookup: my ip address`) because the
release's ndb does not list 10.9.0.3; /boot had already configured IP.
`sysname` comes out `gnot` for the same reason.

What this shows for s9term: the same `/boot` sequence (BOOTP with
`p9  ` vendor, ARP, IL 17008, Tnop, Tsession, Tattach as `none`) is
answered by this server, from the same `ndb` entries, with only the
Ethernet address in the `hobbit` entry still to fix.

## 5. CPU server

Not attempted.  What it takes:

* a kernel with `cpuserver = 1` (`port` section): none is shipped, so it
  must be built with 1e's `8c`/`8l` (`386/bin/8c`, `8l`) from
  `sys/src/9/pc` -- which can now be done *on* this server, the sources
  and compilers being in the kfs.  The same build can carry the three
  fixes in source and `kfs.root`, giving a server that boots from its
  own kfs (`pcdisk` config) instead of the floppy;
* `/rc/bin/cpurc` (shipped) runs `aux/listen il`/`tcp` with the
  release's `/bin/service`: `il17005` is `#!/bin/cpu -R` (the `cpu`
  service), `il17007` and `tcp17007` are `exportfs -a` (they
  authenticate with `srvauth`, `libauth/srvauth.c`, so an auth server
  -- `auth/keyfs`, the `service.auth` listeners -- is needed too);
* the terminal side is `cpu` (`386/bin/cpu`, and `hobbit/bin/cpu`).

## Files

| path | what |
|---|---|
| `tools/qemu1e/build.sh` | tarball -> `build/qemu/{fd.img,fd-term.img,fs.img,arch.img}` |
| `tools/qemu1e/floppies.sh` | the two floppies alone |
| `tools/qemu1e/qemu1e.py` | QEMU driver: CGA screen by QMP pmemsave, keys by send-key, small script language |
| `tools/qemu1e/mkfloppy.py` | PLAN9.SYS for the boot sector; kernel replacement |
| `tools/qemu1e/patch_kernel.py` | the three kernel patches; `--strip` |
| `tools/qemu1e/mkarchive.py`, `mkdisk.py` | mkfs archive; CHS-sized disks with a prep table |
| `tools/qemu1e/kfsinit.rc`, `serve.rc`, `ndb.local`, `overlay/` | run on / installed into the 1e system |
| `tools/qemu1e/overlay.sh` | refresh `overlay/` in an existing `fs.img` with mkext |
| `tools/qemu1e/probe-tcp.sh`, `p9probe.py` | host 9P probe over TCP 564 |
| `tools/qemu1e/il_term_test.py` | two-QEMU IL boot test |
