# `tools/p9boot.py` — the shipped kernel on the reference model (A4)

`tools/p9boot.py` boots `tools/plan9-1e/hobbit/s9term`, the kernel image
the 1e release ships for the Hobbit terminal, on `sem/hobbit_sem.py`, the
reference (one-instruction) model.  It loads the `-H1` image at its own
addresses, starts at the entry in kernel mode in the PRM's reset state,
and models the devices the kernel touches, from `io.h`, the device
drivers in `tools/plan9-1e/sys/src/9/hobbit/` and the PRM.  It uses the
image's own symbol table (`docs/s9term.md`) to say which function is
executing.  s9term was built from sources older than the release ships,
so every device sequence below was checked against s9term's disassembly,
not only against the C.

```sh
# The first console line (the regression test, ~2.1 M instructions, 25 s):
python3 hobbit/tools/p9boot.py hobbit/tools/plan9-1e/hobbit/s9term \
    --max-steps 4000000 --until '\n'
# On to the boot program's prompt (see "How far it gets"; ~30 s):
python3 hobbit/tools/p9boot.py hobbit/tools/plan9-1e/hobbit/s9term \
    --max-steps 400000000 --progress 20000000 \
    --until 'root is from' --out console
```

`--out DIR` writes the console bytes, one file per channel; `--until TEXT` stops once the
screen has shown TEXT; `--progress N` prints where the PC is every N
instructions.  The run prints each first-reached function with its
instruction number, every exception and interrupt the model takes (the
first 100), the model time, and the bytes of each console channel.

## The console

The kernel prints to two places, and both are captured:

* **`screenputs`** — the terminal's own screen.  The kernel draws text
  into a bitmap in RAM (`screen.c`: `gscreen.base = xalloc(...)`) and
  copies it to the LCD controller (`Lcd` below).  The harness reads the
  string at `screenputs`'s entry (arguments at CSP+4, CSP+8) rather than
  decoding pixels: a *harness tap*, which changes no state.
* **`uart0`** — s9term's `printq` also goes to Quart channel 0 (the
  `uartputs` path, `\n` as `\r\n`), which is what a serial console would
  show.  These are the bytes the device model collected.

**Bitmap screen, the minimum chosen.**  The screen is plain RAM plus a
write-only LCD register pair that counts writes; no pixels are
interpreted.

**The console's input is Quart channel 0, not a scan-code keyboard.**
The shipped `screen.c` calls `kbdinit(2)` (the `kbd.c` scan-code
keyboard on channel 2 at 600 baud), but s9term has no `kbdinit` and no
`kbd.c` (`docs/s9term.md`: its `screen.c` predates `kbd.c`).  Tapping
`eiaspecial` in the run shows what the image does instead:

| step | call |
|---:|---|
| 127,557 | `eiaspecial(0, &printq, &kbdq.IOQ (0x8004fdfc), 19200)` |
| 127,705 | `eiaspecial(3, 0, &mouseq, 1200)` |

and `kbdq.putc` (kbdq+0x1034) then holds `kbdcr2nl`.  So the console is a
serial terminal on channel 0 at 19200 baud 8N1 -- output and input --
taking ASCII, CR made NL; channel 2 is never set up.  `--type
TEXT=REPLY` (CHOICES `console-input`) types REPLY on that line once the
screen has shown TEXT: `--type 'il]: =\r'` answers the prompt with
Return.  The mouse (channel 3) gets nothing.

Text reaches the screen ~0.4-0.5 M instructions before the serial line:
s9term's `putstrn` draws it first (`screenputs`, the font blitted in
software) and then calls `uartputs` (from `putstrn+0x96` / `+0xd0`):
pageinit's line is at `screenputs` at 2,131,084 and at `uartputs` at
2,621,219.  A reply typed with no `--think` delay arrives while the
prompt is still being drawn, so on channel 0 its echo (`\r\n`) comes
before the prompt; on the screen the order is the prompt, then `\n`.

## Milestones (2026-11-23)

| instructions | reached |
|---:|---|
| 0 | `_startup` (physical, PSW = 0) |
| 2,064 | `_virtual` — the first instruction after the CRET that turns on the MMU |
| 125,203 | `main` |
| 125,437 | `confinit` |
| 2,088,445 | `mmuinit` |
| 2,127,625 | first `print` (pageinit's) |
| 2,131,084 | `screenputs` has the whole first line |
| 2,621,219 | first byte on Quart channel 0 (`uartputs`) |
| 2,635,067 | `clockinit` |
| ~2,650,000 | `chandevreset`: `iicreset`, `eiareset`, `rtcreset`, `inconreset`, `dkreset`, `scsireset`, `wrenreset`, `etherreset` |
| 2,859,426 | `touser` — the first CRET to user mode (initcode) |
| 2,859,432 | first exception: the CRET's CATCH read fault on the user stack, handled by `fault` |
| 2,869,118 | `sysexec` of `/boot` |
| 2,877,513 | `/boot` running in user mode, demand-paging its text |
| 2,907,111 | `alarmkproc`; then `runproc` idles waiting for the clock |

The first console line, byte for byte, on both channels:

```
1364 free pages, 5456K bytes, swap 27856K, highwater 272K, headroom 340K
```

## How far it gets

At the counter rate the hardware formula gives (one tick per 0.569 s,
QUART_CHOICES `counter-period`) the run reaches `/boot`'s prompt after
**286,977,189 instructions** and 14.367 s of model time, 26 clock
interrupts, in 30-60 s of host time: 283,995,808 of those
instructions are laps of the idle loop that the idle skip (below)
retires without executing.  (Before the EEPROM answered, CHOICES
`iic`, it was 286,970,654: `iicreset`'s read adds 6,535.)

With `--counter-period 0.04` (25 Hz) the same prompt comes after
**22,537,089 instructions** (1.145 s of model time, 26 clock
interrupts), which `tests/test_p9boot.py` `PromptTest` pins.  Before
the EEPROM answered it was 22,530,554, measured first without the idle
skip (6 minutes of host time) and reproduced exactly with it (29 s);
the table is from those runs (add 6,535 from `iicreset` on):

| instructions | reached |
|---:|---|
| 3,291,609 | the first `clockintr` (Quart CtrRDY through `eiaintr`) |
| 22,488,849 | `/boot` after its `sleep(1000)`: `sysopen("#c/cons")` |
| 22,504,334 | `envopen`/`envread` of `#e/cputype`, `#e/terminal` |
| 22,526,752 | an ENTER into the next user stack page: exception 8 by p. 3-21's check, mapped by `fault`, restarted |
| 22,530,554 | the prompt is on the screen |

The screen then holds, byte for byte (`--out` writes it):

```
1364 free pages, 5456K bytes, swap 27856K, highwater 272K, headroom 340K
root is from (il, tcp, incon, 9600, 19200)[il]: 
```

The prompt goes to `#c/cons`, which s9term writes to the screen and then
(0.44 M instructions later, see the console above) to Quart channel 0.

Typing Return at it (`--type 'il]: =\r'`, the default counter rate) takes
`il`: `kbdcr2nl`, the echo, `etherattach` starting the
SONIC's kproc, and the screen shows

```
1364 free pages, 5456K bytes, swap 27856K, highwater 272K, headroom 340K
root is from (il, tcp, incon, 9600, 19200)[il]: 
sonic ether: 52 54 00 00 0b 0b
```

At **287,845,754** instructions (14.4 s of model time) `/boot` sends
its BOOTP request through the SONIC (`tests/test_p9boot.py`
`NetworkTest`, with `--pcap`):

```
52:54:00:00:0b:0b > ff:ff:ff:ff:ff:ff IP 0.0.0.0 > 255.255.255.255
UDP 68 > 67 len 372 BOOTP request htype 1 hlen 6 xid 00000000
chaddr 52:54:00:00:0b:0b file '' vend 'p9  '
```

406 bytes, IP header checksum good: the destination, the EEPROM's
address as source and in `chaddr`, type 0x0800 and `p9  ` all decode,
which checks the SONIC's byte lanes and CAM order at once.

With nobody answering (a Wire with no peer), `/boot` sends the request
ten times, 14.2 s of model time apart (its 1 s alarm is 25 ticks of
0.569 s), each wait ended by an alarm note, and then asks
`My IP address[0.0.0.0]: ` at 3,131,202,766 instructions (156.6 s of
model time, ~55 s of host time; `NoServerTest`).  Each note's return is
a CRET with MSP more than 256 bytes above SP (CHOICES `cret-msp`).

### The join: root from the 1e file server in QEMU

`tools/p9join.py` (after `tools/qemu1e/build.sh`) boots the 1e 386 file
server in QEMU (`docs/qemu_1e_server.md`: `9dos.q`, kfs, `rc /serve
10.9.0.1 255.255.255.0`, its NE2000 on `-netdev dgram`
127.0.0.1:10901 ⇄ 10902) and s9term on the model with the SONIC's wire
on the other end of that UDP pair, types Return at `root is from` and at
`user[none]`, and stops at `init: starting`.  Observed 2026-11-23:

```
...
root is from (il, tcp, incon, 9600, 19200)[il]: 
sonic ether: 52 54 00 00 0b 0b
user[none]: 
arp: rcvd for 10.9.0.1
nop...session...time...
init: starting /bin/rc
```

**310,933,347 instructions** (304,331,328 of them retired idle laps),
15.58 s of model time, 150 s of host time; 277 frames.  The server's
log shows `ip/bootp: reply to 10.9.0.2 525400000b0b /hobbit/s9term p9
255.255.255.0 10.9.0.1 10.9.0.1 10.9.0.1` and `listen: il call for
il17008`.  On the wire, in order: the BOOTP request and the server's
reply (yiaddr 10.9.0.2, file `/hobbit/s9term`, vend `p9  255.255.255.0
10.9.0.1 10.9.0.1 10.9.0.1`); `/boot` ARPs for 10.9.0.1 and gets the
reply; the IL connection to `il!10.9.0.1!17008`; Tnop, Tsession, the
attach as `none` (no auth server: user `none` needs none); the time
from the root's access time, written to the timekeeper
(1993-01-03 12:02:05, CHOICES `rtc`); then `/hobbit/init` read from the
server and run: `init: starting /bin/rc` is printed by the init binary
the server sent.  No CRET was clamped on this path.

The first run stopped at `setrtc` (no device at IONAK+0x3FE0): the
timekeeper was added for the second.

The live join is not deterministic: the server runs at QEMU's speed and
the wall clock.  A third run (on the committed code, while the
regression suite loaded the host) printed `error dialing
10.9.0.1!17008` and `panic: boot process died`.  The server's own pcap
shows why: 8.7 ms after the Hobbit's IL sync (id 26000) it sent a sync
with **ack 0**, and only 0.14 ms later the proper one (ack 26000).
s9term's `stil.c`, in Ilsyncer, hangs up on a sync whose ack is not its
start ("connection rejected"), as the source says it should.  Replaying
that run's pcap reproduces the failure exactly (the replay is also a
debugging tool).  The cause is in "The ack-0 sync" below.

A fourth run (committed code, `--until` that never matches, 360 M
instructions) went past init: `/bin/rc` from the server ran on the
Hobbit and printed, as the server's own console does for glenda,

```
init: starting /bin/rc
Can't cd /usr/none
lib/profile: rc: .: can't open
init: rc exit status: rc 9:can't cd
```

(1515 frames, 18.1 s of model time, 389 s of host time; `/usr/none`
does not exist on the release's file system).  A fifth run, `--until
'% '`, went on to init's restart and **rc's prompt**:

```
init: rc exit status: rc 9:can't cd

init: starting /bin/rc
% 
```

at 618,458,635 instructions (601,206,616 retired idle laps), 31.0 s of
model time, 456 s of host time, 1455 frames: an interactive rc on the
Hobbit with its root from the 1e file server.

`tests/net/join_init.pcap` is the `--pcap` of the run to `init` above
(nanosecond stamps, so whole cycles); replaying it (`--ether-replay`)
re-runs the model with the server's frames delivered at their recorded
cycle offsets from the model frame they followed, and every one of the
model's 277-frame exchange matches the recording byte for byte, to the
same instruction count (310,933,347), in ~60 s of CPU, without QEMU:

```sh
python3 hobbit/tools/p9boot.py hobbit/tools/plan9-1e/hobbit/s9term \
    --max-steps 400000000 --type 'il]: =\r' --type 'user[none]: =\r' \
    --ether-replay hobbit/tests/net/join_init.pcap --until 'init: starting'
```

It is kept as the record of the first join.  `JoinReplayTest` now
replays `tests/net/join_echo.pcap` instead: the first 615 frames of the
lockstep run of "Commands at rc's prompt" below, through init, termrc,
init's restart of rc, and `echo hello` typed at `% ` and run, to
715,867,166 instructions (700,303,728 idle-skipped), 35.9 s of model
time, ~3 min of CPU (174 s measured):

```sh
python3 hobbit/tools/p9boot.py hobbit/tools/plan9-1e/hobbit/s9term \
    --max-steps 800000000 --type 'il]: =\r' --type 'user[none]: =\r' \
    --type '% =echo hello\r' --ether-replay hobbit/tests/net/join_echo.pcap \
    --until 'echo hello\nhello\n% '
```

A lockstep recording replays like a free-running one: the model's
frames carry model time and the console bytes are typed at screen text,
so the run is reproduced instruction for instruction (the replay typed
`echo hello` at step 711,879,422, as the live run did).

Live and free-running (`p9join.py --free-run`, the only mode until
2026-11-23's lockstep), busy model time runs ~200 times slower than the
wall clock while idle time is paced to it (ETHER_CHOICES `peer`), so the
server sees a slow terminal: in the run to `init`, 56 of the server's
143 frames are Dataquery resends of data messages already sent (each
answered by a State from the Hobbit), 10 for the first one; in the run
to `% `, 407 Dataquery resends against 265 data messages, and the
server's clock ran 355 s while the model's ran 16.6 s between the first
and last frame.  Neither stopped the boot.

### One time base: the lockstep (ETHER_CHOICES `lockstep`)

Since 2026-11-23 `p9join.py` runs the two machines on one time base.
The server's time is its own tick counter, `MACHP(0)->ticks` (pc/clock.c
`m->ticks++`, HZ 20), read from guest memory with QMP `pmemsave` at an
address found in `9dos.q` itself (clock()'s first instructions, `mov
m,%eax; incl 12(%eax)`: `m` is 0x8003b004).  QEMU is paused with QMP
`stop` while the model is busy; every 20,000 model instructions, if the
server is a tick or more behind, it is resumed (`cont`) until its ticks
have caught up with model time, then stopped again.  While the model is
idle with nothing due, the server runs and the model waits for it, up
to the model's next timed event or the server's next datagram, which is
stamped with the server's time.  QEMU's `stop` pauses its virtual clock,
so the guest sees no time pass while paused (measured: 0 ticks in 5 s
stopped).

QEMU also runs with `-icount shift=4` (each guest instruction 16 ns of
its virtual time).  The choice was measured (`build/a5/clocktest.py`
then `race.py`, scratch):

| server clock | free, per wall second | catching up 4 s of server time |
|---|---:|---:|
| QEMU's host clock (no icount) | 0.98 s | 4.06 s of wall |
| `-icount shift=4` | 7.6-8.9 s (load-dependent) | 0.35 s of wall |

`-icount` alone cannot pair the clocks: the 1e 386 kernel never halts
(port/proc.c `runproc` spins, so `sleep=on|off` never applies), and its
time then follows QEMU's throughput, 8 times the wall clock and varying
with the host's load; `shift=auto` would track the host clock, which the
model cannot keep up with.  Under the lockstep that does not matter (the
server is run by its own ticks), and icount makes catching up 8 times
cheaper and keeps host scheduling out of the guest's time (the ack-0
sync below).  By design the server should be ahead of the model by at
most about a tick (50 ms) plus a monitor round trip; measured, the skew
runs from -0.63 to +0.12 s.  The positive side fits that bound.  The
negative excursions (11 frames of 591 in run 3 below 0.15 s) are all
server-to-Hobbit frames that reached the model up to 0.63 s of server
time after the server's pcap stamped them, often two sent apart
delivered at one model instant (frames 422 and 423 of run 3: sent at
6.656 and 6.979 s, both taken at model time 7.287 s).  Why the model
read them that late is not explained.

Measured on live runs to `% ` (IL counts from the Hobbit's pcap; skew
is the server's pcap stamp minus the model's for the same frame, both
counted from the first frame):

| run | frames | server Dataquery resends | server data | skew | server ran |
|---|---:|---:|---:|---|---:|
| free-running (2026-11-23, earlier) | 1455 | 407 | 265 | server clock 355 s vs model 16.6 s | wall clock |
| lockstep, no icount | 587 | 1 | 259 | -0.02 .. +0.23 s | 31 s of wall |
| lockstep, icount 4 (6 runs, below) | 587-595 | 1-5 | 259 | -0.63 .. +0.12 s | 4-5 s of wall |

**Reliability.**  Six consecutive live runs with the lockstep and
`-icount shift=4` (`p9join.py --until '% '`, 2026-11-23, the host's load
average 58-85; the kfs already had /usr/none, "The user" below), and two more (one without icount, one with the command
script of step 3 below), all reached rc's `% ` with no failure:

| run | instructions (idle-skipped) | model time | host time | frames | server resends |
|---|---:|---:|---:|---:|---:|
| 1 | 704,903,691 (690,745,356) | 35.32 s | 258 s | 595 | 5 |
| 2 | 771,905,606 (757,761,120) | 38.67 s | 255 s | 587 | 1 |
| 3 | 768,913,081 (754,755,988) | 38.52 s | 244 s | 591 | 3 |
| 4 | 729,920,371 (715,752,340) | 36.57 s | 249 s | 591 | 2 |
| 5 | 712,906,549 (698,763,784) | 35.72 s | 234 s | 587 | 1 |
| 6 | 686,918,200 (672,777,344) | 34.42 s | 221 s | 587 | 1 |

The runs differ by up to 3 s of model time because the Hobbit's clock
ticks every 0.569 s and init's and /boot's sleeps end on ticks: a reply
that lands just after a tick waits for the next one.  The free-running
fifth run of the earlier session took 456 s of host time to the same
prompt; the lockstep's runs take about half that, because the server no
longer floods a slow terminal with resends.

With the lockstep the kernel's 1 s alarms still take 14.2 s of model
time (the counter period, below): that is model time, and the server now
agrees with it, so it no longer costs anything but idle laps.

### The user: `none`, with 1e's PC-floppy home

s9term's `/boot` asks `user[none]:`, and Return takes `none`, the
unauthenticated user every 1e file server accepts.  init (`sys/src/cmd/
init.c` rcexec, service `terminal`) then runs `rc -c '/rc/bin/termrc;
home=/usr/$user; cd; . lib/profile'`.  On the release's file system that
failed (`Can't cd /usr/none`, `lib/profile: rc: .: can't open`): the
release's `/usr` holds only `tor`.  termrc itself did run: the old run's
pcap carries the reads of `/rc/bin/termrc`, `/bin/ndb/cs` and
`/lib/ndb/local` (termrc starts `ndb/cs`; its `*hobbit*` case binds `#t`;
nothing it does prints).

What 1e itself did for `none`: the PC install floppy's tree
(`sys/lib/pc/usr/none/lib/profile`, mkfs'd onto the floppy) gives `none`
a home whose `lib/profile` is empty.  The kfs now has the same
(tools/qemu1e/overlay/usr/none, refreshed with `overlay.sh`), so init's
`rc -c` runs termrc, cds to `/usr/none`, sources the empty profile and
exits; init prints nothing for an empty status, sleeps 1 s and starts a
plain interactive `rc`, and the screen shows

```
nop...session...time...
init: starting /bin/rc

init: starting /bin/rc
% 
```

The alternative, `tor`, is the release's demonstration account
(install.ms: "a stub account we put on the distribution to show you how
a proper user's directory should be set up"); its `lib/profile` binds
`$home/tmp` and `$home/bin` and, for `service=terminal`, ends in `exec
8½ -i 8½start -s -f $font`: the window system, which wants the
bitmap device (`/dev/bitblt`) and the mouse on Quart channel 3, neither
of which is modelled beyond the LCD's write counter.  So the console
stays plain rc as `none`; `glenda` (the server's own console user)
would fail the same way as `none` did, with no `/usr/glenda`.

### The ROM's fpi (CHOICES `fpi-rom`)

The first live run of the command script (step 3 below) stopped at `za
hello.s`: za's start-up executes a five-parcel opcode 0x11 (a floating-
point instruction; the Hobbit has no FPU), the unimplemented-instruction
sequence (p. 1-39) vectored through VB+12, and the PC went to
0xC0000F00, the sentinel the harness had put in PPage0+0x74.  raml.s's
`_virtual` copies that word into the niladic and unimplemented vectors
("fpi"); roml.s, the boot ROM, stores `$fprt0(SB)` there.  So the 1e
Hobbit's floating point is interpreted by code in the boot ROM, entered
in the trapping process's own mode (the sequence does not change the
PSW) through VROMBASE, which raml.s maps user-executable onto the ROM at
PROMBASE (`NPSTE(PROMBASE, 128, STE_U|STE_V)`).  The release ships no
ROM image, but it ships the interpreter's sources (`fprt0.s`,
`fpihobbit.c`, `fpi.c`) and the mkfile's own rule for a standalone one:

```
fpi.out:	fprt0.$O fpihobbit.$O fpi.$O
	$LD -l -R4 -T0xE0000020 $prereq
```

`tools/p9kbuild.py fpi` follows it with the shipped `za`, `zc` and `zl`
run on the reference model (`za fprt0.s`, `zc -w -Dram fpihobbit.c`,
`zc -w -Dram fpi.c`, 7.0 M instructions; `zl -l -R4 -T0xC0000020
-o fpi.out fprt0.z fpihobbit.z fpi.z`, 2.3 M), with the one change that
the text goes to 0xC0000020 -- the rule's offset in the ROM's segment --
instead of 0xE0000020, which no kernel mapping covers.  The product,
`tools/p9kbuild/fpi.rom` (13,070 bytes, text 6,328, no data or bss,
entry `fprt0` = 0xC0000020, sha256 7905396250041775...), is loaded at
PROMBASE+0x20 and its entry put in PPage0+0x74; nothing else of the ROM
is modelled (`--no-fpi` restores the sentinel).  `p9kbuild.py fpi
--check` rebuilds it and compares.  Where the real ROM put fprt0 is not
known and does not matter: the kernel takes the address from PPage0.
With it, za's FMOV is interpreted and za goes on (one unimplemented
event, then its own page faults).

### Commands at rc's prompt: the A5 gate

`p9join.py` with `--type` scripts the console; each line is typed (on
Quart channel 0, CR made NL by the kernel's `kbdcr2nl`) once the screen
shows the next `% `:

```sh
python3 hobbit/tools/p9join.py --until 'end of script\n% ' \
    --max-steps 6000000000 --out DIR \
    --type '% =echo hello\r' --type '% =ls /hobbit | wc\r' \
    --type '% =cat /lib/ndb/local\r' --type '% =cd /usr/none\r' \
    --type '% =za hello.s\r' --type '% =zl hello.z -lc\r' \
    --type '% =ls -l\r' --type '% =sum hello.z z.out\r' \
    --type '% =z.out\r' --type '% =echo end of script\r'
```

Live, 2026-11-23 (lockstep, icount 4): **840,583,000 instructions**
(789,666,868 retired idle laps), 42.2 s of model time, 732 s of host
time, 1108 frames.  The screen, byte for byte (`tests/net/a5_screen.txt`,
2127 bytes, sha256 9437c51b...; the serial line's copy, `\n` as `\r\n`
and the echo interleaved as described in "The console", is
`tests/net/a5_uart0.txt`, 2235 bytes), with the middle of `cat` cut here:

```
init: starting /bin/rc

init: starting /bin/rc
% echo hello
hello
% ls /hobbit | wc
      6       6      83
% cat /lib/ndb/local
#
# systems on the local network
...
udp=bootp	port=67
% cd /usr/none
% za hello.s
% zl hello.z -lc
% ls -l
--rw-rw-rw- M 4 sys  sys  183 Jan  3 07:00 hello.s
--rw-rw-r-- M 4 none sys  255 Jan  3 07:01 hello.z
d-rwxrwxrwx M 4 sys  sys    0 Jan  3 07:00 lib
--rwxrwxr-x M 4 none sys 2014 Jan  3 07:01 z.out
% sum hello.z z.out
b3769ed2    255 hello.z
4b4798a2   2014 z.out
% z.out
hello 1e
% echo end of script
end of script
% 
```

Each output was checked against an independent source:

| command | checked against | result |
|---|---|---|
| `echo hello` | `p9run.py echo hello` (the shipped echo on the reference model, no kernel): `hello\n` | same |
| `ls /hobbit \| wc` | the release's `/hobbit` has 6 entries (`bin include init lib mkfile s9term`, release.list); the shipped `wc` under p9run on those six as `/hobbit/NAME` lines prints `      6       6      83` (p9run cannot run `ls` on a directory, so the path form is ls(1)'s, not measured) | same |
| `cat /lib/ndb/local` | the release's `lib/ndb/local` (1414 bytes; the kfs is the release, the qemu1e additions went to the floppy's copy) | byte-identical |
| `za hello.s`, `zl hello.z -lc` | `p9run.py za hello.s` and `zl hello.z -lc` on the same file, then the shipped `sum` under p9run on their outputs: `b3769ed2 255 hello.z`, `4b4798a2 2014 z.out` | same sums and sizes |
| `z.out` | `p9run.py z.out`: `hello 1e` | same |

So on the Hobbit, with its root on the 1e file server, rc reads the
console, `cat` reads a file from the server's disk, and `za` and `zl`
assemble and link a program inside the boot, which then runs.  The
assembler needed the ROM's fpi (above); 1e's `zl` wants `-lc` given (no
default library), as under p9run.

The whole session replays without QEMU: `tests/net/a5_session.pcap`
is the run's `--pcap` (1108 frames), and replaying it with the same
script (`build/a5/rep_all.py`, scratch, or `p9boot.py --ether-replay
hobbit/tests/net/a5_session.pcap` with the twelve `--type` answers and
`--until 'end of script\n% '`) stopped at the same 840,583,000
instructions, every model frame as recorded, with a screen
byte-identical to `tests/net/a5_screen.txt` (536 s of CPU, 2026-11-24;
too long for `tests/run_tests.sh`, which replays the first 615 frames).
The same replay with `--no-fpi` (FP traps to the bare ROM vector) stops
at `% za hello.s` with "read of the boot ROM at physical 0x00000f00",
784,817,814 instructions, the screen 1784 bytes long: the ROM fpi is
what lets za run.

### The ack-0 sync (the server's IL race)

Read against the server's own `sys/src/9/port/stil.c` (1e tarball), the
failed run's server pcap (`build/a5/join3/`, copied from that run):

```
 22.660000 H> sync  id  26000 ack     0  5000>17008
 22.668703 <S sync  id 174100 ack     0 17008>5000
 22.668847 <S sync  id 174100 ack 26000 17008>5000
 23.101285 <S sync  id 174100 ack 26000 ...   (every ~0.4 s, 28 more)
```

The two answers have the same id, so they come from the one new
conversation (`ic->start` = 174100).  Three places send an Ilsync with
`(ic->start, ic->recvd)`: `ilstart` for an active open (the server only
listens), `_ilprocess` in Ilsyncee on the incoming sync (line 431-432:
`ic->recvd = id` and then the send, so its ack is 26000 -- the second
frame), and `ilackproc`'s timer pass for a conversation in Ilsyncee or
Ilsyncer (line 764-769).  So the first frame is `ilackproc`'s, sent
while `recvd` was still 0: after `ilrcvmsg` set `ic->state = Ilsyncee`,
`ic->start` and `ic->recvd = 0` (lines 356-360) and before
`_ilprocess` set `recvd` (line 431).  `ilackproc` sends at once there
because `ilrcvmsg` never calls `Starttimer` for the new conversation:
a freshly allocated Ipconv has `timeout = fasttime = 0`, so the first
pass (`timeout += 100 >= 0`) qualifies.  For `ilackproc` to run inside
that window on a uniprocessor, the receiving kernel process must be
preempted there: pc/clock.c's `clock()` preempts a running kernel
process at any tick when `anyready()`, and `ilackproc` becomes ready
every 100 ms (`tsleep(&ilackr, return0, 0, Iltickms)`).  The 1e IL in
s9term (Ilsyncer) then rejects the connection, correctly.

That much follows from the frames and the code.  What made the
preemption land in a window of a few dozen instructions was not caught:
probing the server as a fake Hobbit (`build/a5/race.py`: BOOTP, ARP,
then IL syncs from new ports, each closed after the answer) gave **0
ack-0 answers in 612 dials** -- 300 on a free-running server, 300 under
`-icount shift=4`, and 12 first dials on freshly booted servers (the
failed run's dial was the first after boot, the case with a fresh
Ipconv and code never translated by QEMU before).  A guess, not
measured: without icount the guest's clock is the host's, so a QEMU
thread descheduled inside the window (the host's load was above 70)
comes back to an overdue timer interrupt; under `-icount` the guest's
clock follows its instructions and that stretch cannot happen.  The
probe saw no difference (0 of 300 either way), so whether icount
changes the rate is not known.  The window itself, a 1e bug, remains.

Without `--counter-period` the clock ticks every 0.569 s of model time,
and `sleep(1000)` (25 ticks) needs ~14 s of model time; with the idle
skip that costs nothing, so the override is no longer needed to get
anywhere.

## The idle skip (CHOICES `idle-skip`)

s9term's idle loop is `runproc`'s `while(runhiq.head==0 &&
runloq.head==0);` after `spllo()` (port/proc.c), which in the image is
four instructions at `runproc+0x08..+0x1e` (0x8000649a):

```
+0x08  dffc 0000 0000 8004 d300   compare $0 with runhiq.head (runhiq+8)
+0x12  1007                       JMPFN +0x20: a process is ready, leave
+0x14  dffc 0000 0000 8004 d418   compare $0 with runloq.head (runloq+8)
+0x1e  1ff5                       JMPTY +0x08: both empty, again
```

It stores nothing, so only an interrupt can end it.  `find_idle_loop`
checks these parcels in the loaded image and refuses to run otherwise.
With the PC at the head, both heads 0, IPL 7, no interrupt asserted, no
timer interrupt enabled, and the last two laps of equal cost, the
harness retires N laps at once: `steps += 4N`, `cycles += N x lap`,
with N the largest number that still ends *before* the next timed
device event (the Quart counter, a scripted console byte, an inbound
frame).  The laps executed after that, the interrupt and everything
after it are the unskipped run's, instruction for instruction:

| run | instructions | cycles | host time |
|---|---:|---:|---:|
| to the prompt, 25 Hz, no skip (before the skip existed) | 22,530,554 | | ~6 min |
| the same with the skip (19,573,088 retired by 25 skips) | 22,530,554 | 22,890,723 | 29 s |
| 3.4 M instructions at a 4 ms tick, no skip / skip (7 skips) | 3,400,000 | 3,757,855 | 34 s / 27 s |

and in the last row the two runs end with the same PC, PSW, stacks,
interrupt and exception lists, functions reached, console bytes, Quart
state and every RAM word (`IdleSkipEquivalenceTest`).  The Hobbit has no
idle, halt or wait instruction (none of Table 3-1's 46 mnemonics, pp.
3-1..3-2, `docs/isa_inventory.md` §2), and s9term spins, so this loop is
the only idle state there is.  With
nothing timed pending, the loop could never end, and the run stops
saying so.

### The clock rate (QUART_CHOICES `counter-period`), reconsidered

s9term's `clockinit` (0x8000f780) loads the counter with a constant:
`acr = 0xF0` (BRGSet2|TimerD16), `ctu:ctl = 0xFFFF` (`MOV $0xffff`,
then `>>8` and `&0xff` into ctu and ctl), where the shipped source
computes `Crystal/(2*16*HZ)` = 4608.  Its HZ is 25 (`tsleep` divides by
MS2HZ = 40; mem.h `HZ 25`).  So the image's software assumes 25 ticks a
second and programs a count that, by the 68C94's timer formula with the
3.6864 MHz crystal deveia.c names, gives 1.76 a second.  Nothing in the
release says which is wrong (a different crystal on the 1992 board, a
counter clock not divided by 16, or a kernel whose clock ran slow); the
default stays the formula, and `--counter-period 0.04` stays a stated
deviation, now needed for nothing but shorter model time.

## The root file system: what `/boot` asks the machine for

s9term's `/boot` (`bootcode`, 26,796 bytes in the image's data) offers,
in order, `il, tcp, incon, 9600, 19200` (the method table's strings,
read from the image: `il`, `tcp`, `incon "config 1 64 restart dk"`,
`9600 "#t/eia1"`, `19200 "#t/eia1"`); the default is **il**.  There is
no `local` method in this image (the release's `termlocal` adds one).
From `sys/src/9/boot/ip.c` and `async.c`, and the strings in the image:

* **il** (default) and **tcp** — 9P over IL (port 17008, auth 17024) or
  TCP, on IP over the **SONIC** ethernet (`#l/ether`, DP83932 at
  0xA4400000, IRQ 9).  `/boot` first broadcasts **BOOTP** on UDP 67 for
  its IP address, mask, gateway and file server address (or prompts "My
  IP address" etc.), then ARPs.  It needs: (1) an ethernet address —
  `myetheraddr` reads `#l/ether`'s address, which `devether.c` takes from
  the IIC EEPROM (`eeprom.ea`), now zero (CHOICES `iic`): the IIC/
  PCF8582 must answer with a real address; (2) the SONIC's transmit
  (`cr` Txp, the TDA descriptors in RAM) and receive (RRA/RDA
  descriptors, Rxen, `isr` PktRx, IRQ 9) — SONIC_CHOICES `no-network` is
  the minimum that passes `reset()` and stops at the first transmit.
  The join to a 1e file server elsewhere is a frame transport for those
  descriptors (e.g. a host tap or socket carrying ethernet frames to
  QEMU's NE2000), with a BOOTP answer from either side.  The 1e 386 file
  server speaks IL, so this is the direct path.
* **incon** — Datakit over the incon board (`#i/ctl`, `dkmux`): needs a
  Datakit peer, not a 9P server.
* **9600 / 19200** — `#t/eia1`, i.e. **Quart channel 1** at 9600 or
  19200 baud, with `push async` and `push dkmux` (`config 1 16 restart dk
  4`) and then `dkconnect`: Datakit URP over the serial line, again a
  Datakit peer rather than raw 9P.  Its needs from the machine are small
  (RxRDY/RxAvail on channel 1, QUART_CHOICES `sr`, `cir`) but the far
  end must speak Datakit.

So the shortest path to a QEMU 1e file server is **il over the SONIC**:
an IIC EEPROM with an ethernet address, SONIC transmit/receive, and a
frame bridge.  Answering the prompt itself needs only Return on the
console line (Quart channel 0): the default is `il`.

## Modelling choices

Each is also a `CHOICES`/`*_CHOICES` entry in `tools/p9boot.py`, printed
nowhere else.  Where the release is silent they are choices, stated as
such.

### The board (`CHOICES`)

* **memsize** — 8 MB of RAM at 0x80000000; `PPage0.memsize` = 8 MB.  The
  ROM measures memory (`rommain.c` `meminit`); a 1993 board's size is not
  in the release.  The first console line depends on it (1364 pages).
* **ram-init** — RAM the image does not load reads as 0.
* **ppage0** — the ROM's hand-off page (`rom.h` `PPage0`): memsize,
  argc = 0, `env.nentry` = 0, everything else 0, except:
* **fpi-vector** — PPage0+0x74, which `_virtual` copies into VB+8 and
  VB+12 (the trapped-niladic and unimplemented-instruction vectors),
  holds a sentinel in the ROM's range: the release ships no ROM image
  (the floating-point interpreter lives there), so reaching it stops the
  run.
* **reset** — PC = the entry, PSW = CONFIG = SHAD = 0 (p. 1-35);
  SP = MSP = ISP = VB = STB = 0 (undefined after reset, p. 1-36).  The
  ROM's state at its jump to the kernel is not known.
* **irq-level** — every board interrupt reaches the part at IL 6:
  s9term's vector table sends only interrupt 6 to `interrupt()`.
* **irq-status** — `Irq.status0/1` are the raw requests (bit n = io.h
  IRQ n); IL 6 is asserted while `status & mask` ≠ 0.
* **clock** — model time is the sum of the records' Chapter 4 cycles at
  20 MHz, the lower of the data sheet's two rated clocks.  It paces the
  Quart counter, the kernel's clock interrupt.
* **iic** — the PCF8584 and the PCF8582 EEPROM answer `deviic.c`
  (IIC_CHOICES, below): `iicreset` reads `io.h`'s `Eeprom`.
* **lcd** — `Lcdisp` at IOACK 0x3000 accepts and counts writes.
* **incon, IOCTL** — latches that record writes; an unexpected read
  stops the run.
* **idle-skip** — `runproc`'s idle loop retired in whole laps up to the
  next timed device event (section above); `--no-idle-skip` turns it off.
* **cret-msp** — `hobbit_sem.System.cret_clamp` is on: a CRET whose
  restored MSP is more than 256 bytes above its SP has its CATCH
  portion stop with the cache full (p. 3-10, "or the cache is full"),
  MSP = SP + 256, instead of the reference model's refusal (p. 1-13
  calls the stack cache's results then unpredictable).  s9term's
  `notify()` builds exactly that frame (it lowers the user SP by 0x170
  for the Ureg, the note and the arguments and keeps MSP), and
  `raml.s`'s `_exception` resets an MSP found above SP + SCSIZE, so the
  kernel expected the state.  The run reports the number clamped.
* **rtc** — `io.h`'s Nvram (IONAK 0x2000, 2040 bytes) and RTCdev (IONAK
  0x3FE0) are one 2K timekeeper, a byte per word in bits 7:0: control,
  sec, min, hour, wday, mday, mon, year in BCD; `devrtc.c`'s RTCREAD
  (0x40) and RTCWRITE (0x80) freeze the registers and load them when
  RTCWRITE clears (the MK48T02 scheme; no data sheet in the release).
  The clock starts at 1993-01-03 12:00:00 UTC (the QEMU server's `-rtc
  base`) and runs on model time.
* **console-input** — the console line is Quart channel 0 (section "The
  console"); `--type TEXT=REPLY` types REPLY there once the screen shows
  TEXT, `--think SECONDS` after it.

### Quart (`QUART_CHOICES`, `io.h` `Quart`/`Duart`, `deveia.c`)

* **sr** — TxRDY|TxEMT while the transmitter is enabled: a byte written
  leaves at once.  RxRDY while the receive FIFO holds a byte, FFULL at
  three.
* **rx** — typed bytes arrive one character time apart (1 start bit,
  mr1's data and parity bits, mr2's stop bits at csr's rate under
  BRGSet2: 0.52 ms at 19200 8N1) into a three-byte FIFO; a byte that
  finds it full, or the receiver disabled, waits on the line (no overrun
  is modelled).  grxfifo/rxfifo pop; an empty FIFO reads 0.
* **cr** — the enable/disable bits and MrReset/RxReset/TxReset change
  state; the rest are accepted and ignored.
* **isr** — TxRDYa/TxRDYb while enabled; CtrRDY once the counter expires,
  until a read of `stop`; RxRDYa/RxRDYb while the FIFO is not empty
  (uartsetup's mr1 has bit 6, FFULL interrupts, clear).
* **counter** — started by a read of `start`; CtrRDY every
  2·count/(3.6864 MHz/16) s.
* **counter-period** — s9term's `clockinit` is older than the release's:
  it writes ctu = ctl = 0xFF (count 65535), a CtrRDY every 0.569 s by the
  formula, while its `tsleep` divides by MS2HZ = 40 (HZ = 25).  The
  default follows the count; `--counter-period 0.04` gives the 25 Hz the
  software assumes, a stated deviation that makes `sleep(1000)` in
  `/boot` last 25 ticks of 0.04 s instead of 25 of 0.569 s.
* **cir** — a write of `update` latches the highest pending enabled
  source: the counter (cir 0x14, gicr = 2·duart), then a receiver (cir
  0x0C RxAvail, gicr = channel, gibcr = bytes in its FIFO), then a
  transmitter (cir 0x08, gicr = channel, gibcr = 1); nothing pending
  reads 0.  The order is a choice: the bidding registers (bcr) that set
  it on the part are written by eiasetup but not modelled.
* **irq** — IRQ 1 while any isr bit is enabled in its DUART's imr.

### WD33C93 (`WD_CHOICES`, `scsi.c`)

* **reset** — after Creset the chip interrupts with status 0x01 if the
  own-ID register has Eaf, else 0x00 (the WD33C93A's two reset codes).
* **no-targets** — every selection ends in selection timeout (0x42).
* **irq** — IRQ 10 while Intrpend is set.

### IIC and the EEPROM (`IIC_CHOICES`, `deviic.c`)

No PCF8584 or PCF8582 data sheet is in the release or the repository;
the behaviour is inferred from `deviic.c`'s code and comments.

* **bus** — S1 reads PIN (clear once a byte has gone or come), LRB
  ("Nak", set when no slave acknowledged), BB ("Busfree", set with no
  START outstanding); S0' and S2 are written through the ES1 select
  before ESO; transfers complete at once.  On the bus: the EEPROM (0xA4)
  and the LED latch (0x40); other addresses are not acknowledged.
* **repeated-start** — `eepromread` writes the read address 0xA5 to S0
  after the word address, reads S1, waits, then sets STA: the byte is
  taken as the repeated START's address, not written to the EEPROM.
* **receive** — the first S0 read after the address returns the address
  byte (the driver: "We get some junk back"); each S0 read with ACK set
  starts the next byte; the control write 0xC0 (ACK off) completes the
  byte in progress.  So `eepromread` stores 17 bytes: the 16 of
  `Eeprom` and one past it, into `rtclock` (EEPROM byte 16 = 0).
* **eeprom** — magic `a6 00 d9 20 10` (`EEPROMMAGIC "A600D92010"` read as
  hex digits; nothing checks it), ether address **52:54:00:00:0b:0b**
  (`--ea`; locally administered, and the address `tools/qemu1e/ndb.local`
  gives the Hobbit, so the 1e server's `ip/bootp` answers it), mask 0,
  clock 20 (MHz: `delay()` loops `ms*1000*clock/2` times, consistent
  with CHOICES `clock`), dsp, pcb, rev 0.  The values of a 1993 board
  are not in the release.  Reading it adds 6,535 instructions before the
  prompt (22,537,089 at 25 Hz).

### SONIC (`SONIC_CHOICES`, `devether.c`)

No DP83932 data sheet is in the release or the repository.  Every point
is what s9term's `devether.c` relies on; where the driver leaves a
detail open, QEMU's model of the same part (`hw/net/dp8393x.c`, read
2026-11-23 from qemu master) is followed, and each such point says so.

* **registers** — io.h's words, 16 bits wide; reset state `cr =
  Rst|Stp|Rxdis`; writing `cr` with Rst clear while in reset only leaves
  reset (QEMU), which `reset()`'s `cr = Rst; dcr = ...; cr = 0` needs.
* **isr** — write-one-to-clear (the driver writes back what it read);
  IRQ 9 while `isr & imr`.
* **rra** — Rrra (and each used-up buffer) reads the 4-word resource at
  `urra:rrp`, advances `rrp` by 16 and wraps it at `rea`; completes at
  once.
* **cam** — Lcam reads `cdc` entries of (cep, cap0..2) at `urra:cdp`
  (the upper half from urra: QEMU), each cap two address bytes low byte
  first (the driver's `cap0 = ea[1]<<8|ea[0]`), then the enable word;
  isr Lcd.
* **transmit** — Txp sends from `utda:ctda` (size, fragment count, per
  fragment ptr0/ptr1/size, link), at once (no line time, no collisions),
  writes status 0x0001 (PTX: neither Host 0 nor Interface ~0, as the
  driver tests), sets `ctda` to the link and goes on unless the link has
  EOL; then isr Txdn.  `ctda` keeping the EOL link makes the next bare
  `cr = Txp` (etheroput) start at the next descriptor (QEMU does the
  same).  No FCS on transmit.
* **receive** — an accepted frame goes into the current buffer with its
  CRC-32 FCS, padded to 4 bytes; the descriptor at `urda:crda` gets
  status Prx (|Bc, |Lpkt when fewer than `eobc` words remain), byte count
  (+4, which etherkproc subtracts), buffer address, sequence number;
  then, unless its link has EOL, `in_use = 0` (Host), `crda = link`, isr
  Pktrx; with EOL the descriptor is kept (isr Rde) and its link re-read
  at the next frame (QEMU).  Lpkt reads the next resource, so with
  `eobc` = buffer words − 2 each frame has its own buffer and buffers
  advance with descriptors, as `etherkproc`'s `rb[rh]` needs.
  Descriptor words are written zero-extended (QEMU's 32-bit mode; the
  driver compares the whole word with Host = 0).
* **filter** — Pro (unicast), Brd (broadcast), an enabled CAM entry;
  transmitted frames are not looped back.
* **dma** — physical addresses (PADDR is the identity) through the
  board's RAM, bytes in the little-endian lanes the kernel uses
  (CONFIG.KL); the first frame checks it.

### The wire (`ETHER_CHOICES`)

`--pcap FILE` writes every frame both ways, stamped with model time.
`--ether-peer HOST:PORT --ether-local HOST:PORT` exchanges frames with
a UDP peer, one raw ethernet frame per datagram (QEMU's `-netdev dgram`
framing); idle model time then runs at the wall clock (the idle skip
waits on the socket for as long as the model time to the next event),
busy time at the model's ~100,000 instructions/s.  `--ether-replay
PCAP` answers with a recorded session's frames; `--ether-script PCAP`
delivers frames at their timestamps.  With nothing attached, a transmit
stops the run.

## What the reference model gained (`hobbit_sem.System`)

All of it exists only when a `State` carries a `System`; without one the
user-level model is unchanged (`tests/test_sem_extended.py`, the golden
programs and `test_p9run.py` are green).  Unit tests:
`tests/test_sem_system.py`, each proved discriminating by injection
(observed failures in its header).

* The CPU escape (0x2C00): mode 7 of the following instruction names a
  control register, 1..12 (Table 1-24, p. 1-26); writes at user level
  are exception 5; register 0 or > 12 is exception 6.  SP writes also set
  MSP; PSW, STB masked to their defined bits; CONFIG.KL switches the
  byte order.
* CSP = ISP when PSW bit 9 is clear (p. 1-12): ENTER, RETURN and POPN
  move the ISP, CATCH is a no-op, stack-offset operands use the ISP.
* SHAD follows the CSP; KCALL, KRET, CRET set it (p. 1-16).
* CONFIG.SE gates the stack cache; CONFIG.PX extends 16-bit absolutes
  with the PC's bits 31:29 (p. 1-23).
* The MMU (Chapter 2): STB → STE → (nonpaged base/bound or PTE), the
  C/S/U/W/V checks, R and M written back; faults 7/8/9 with FAULT.
* The exception (p. 1-38), interrupt (p. 1-37), unimplemented-
  instruction and trapped-niladic sequences (p. 1-39); KCALL's frame and
  every vector read are made at kernel level whatever the PSW's level.
* A CRET whose MSP is more than 256 above SP is refused (p. 1-13),
  unless `System.cret_clamp` (a harness choice, off by default; p9boot
  sets it, CHOICES `cret-msp`) clamps it to SP + 256.
* CRET's CATCH portion (p. 3-15) runs under the restored PSW, block by
  block; a fault is exception 8 at the restored PC with SP kept — 1e's
  `trap.c` relies on it for the first entry to user mode (its "CRET
  fails" and "CATCH/ENTER read fault" comments).
* ENTER's store check of the target and new MSP (p. 3-21): exception 8
  after the flush, SP unchanged, so the kernel maps the next user stack
  page and the ENTER restarts.
* TIMER1/TIMER2 count (Table 1-2), not yet used by s9term.

Not modelled: the TLBs and their flushes (no-ops; the walk is made on
every access), the instruction cache and prefetch, tracing, NMI edge
sensitivity, bus errors other than "no device".

## What blocks next

1. **8½ and the rest of a terminal**: `tor`'s profile (the release's
   model user) execs 8½, which wants `/dev/bitblt` and the mouse (Quart
   channel 3); neither is modelled beyond the LCD's write counter, so
   the console stays plain rc as `none`.
2. **The ack-0 IL sync** (above): a 1e bug in the server's `stil.c`,
   not removed.  It has not been seen since (0 of 612 probe dials, 0 of
   9 live runs); whether `-icount` changes its rate could not be
   measured (0 of 300 dials either way).  A run it hits ends in `panic:
   boot process died`.
3. s9term's clock rate (QUART_CHOICES `counter-period`): whether the
   board's counter ran from a faster clock than the release's formula
   assumes is not settled by anything in the release (above).

## The boot on the core (2026-11-23)

The same boot on the Bluespec core, compared with the reference boot
record by record -- A2's method (one device model, recorded and replayed)
applied to a kernel:

```sh
# record the reference boot, build the core, boot it, compare (the
# reference records at ~62,000 instructions/s; the core's part took
# 15 to 35 minutes on a heavily loaded machine, 2026-11-24):
hobbit/bsv/run_p9kern.sh 2893000 [WORKDIR]
# the same on Verilator (later in the day: 172 s for the whole Bluesim
# run, 67 s for this one with the simulator prebuilt):
P9KERN_SIM=verilator hobbit/bsv/run_p9kern.sh 2893000 [WORKDIR]
# the suite's sample (tests/run_tests.sh): to main and the first ORI
hobbit/bsv/run_p9kern.sh 300000 WORKDIR
```

* `tools/p9coreboot.py record` runs `p9boot.Boot` unchanged -- it
  imports it and wraps `hobbit_sem.step`, `hobbit_sem.take_interrupt`
  and the board's `read`/`write` from outside -- and writes `ref.hri`
  (every retirement record), `functions` (the first-reached functions
  by record number), `console` (the bytes written to Quart channel 0's
  transmit register) and `boot.rec`, the replay: the boot memory (the
  loaded image and the ROM's hand-off page), the entry, every device
  read and write by record number, and every interrupt by record number.
  It turns the idle skip off (`CHOICES['idle-skip']`): the skip retires
  idle-loop laps without executing them, and the core executes every
  lap, so with the skip on the record numbers would not line up.
  Device DMA into RAM (SONIC's descriptors and buffers, after `/boot`
  starts BOOTP) is not in the replay yet: the core's RAM would not see
  it.
* `bsv/P9KernTb.bsv` starts `mkHobbitCoreSystem` at the entry with
  every control register 0, as `Boot` starts the reference (physical
  addressing, CSP = ISP, kernel level).  `bsv/p9kern.c` is its board:
  RAM is a sparse store ([0x80000000, 0x80800000), `CHOICES` memsize),
  and the MMU's table walk reads that same RAM (`pk_peek`), because the
  kernel builds its tables there.
  With `-D P9KERN_FLAT` the board memory is inlined, so every BDPI call
  sits in the one synthesized module, which is the pattern the Verilator
  build needs.  `P9KERN_SIM=verilator bsv/run_p9kern.sh N [WORKDIR]`
  runs that form on Verilator (`bsv/build_p9kern_vl.sh`): its `core.log`
  is byte-identical to Bluesim's at 300,000 and at 2,893,000 records,
  every HRI line with `cyc` included, and at 2,893,000 records the
  simulator alone takes 31 CPU seconds against Bluesim's 92
  (2026-11-24; `docs/bluespec_architecture.md`, "The kernel testbench
  on Verilator").
* `tools/p9coreboot.py compare` streams the two traces and stops at the
  first record that differs in any field but `cyc`
  (`tools/p9trace_cmp.py`'s rule, streamed: a boot is millions of
  records).  `run_p9kern.sh` also requires the core's console to be the
  reference's, byte for byte.

### How device reads and interrupts reach the core (stated choices)

The core makes reads the reference never makes: it fetches operands
ahead, including on mispredicted paths (`docs/conformance_1to1.md` §1c,
§1d).  So a device read cannot be answered by "the next recorded read".
The choices:

1. **A device read is matched by address and by retirement count.**
   The testbench tells the board, every clock, how many records the core
   has retired (`pk_retired`; instructions plus folded branches).  A
   request for physical address `pa` takes the earliest unused `D n pa`
   record with `retired < n <= retired + 8` -- the instruction asking is
   at most a few slots younger than the last one retired.  The same
   request again (an operand fetch retried) gets the same value.  A
   request matching nothing is a read the reference never made: it is
   answered 0 and counted as "unrecorded", and if such an instruction
   ever retired the trace would differ.
2. **A device write is checked, not modelled.**  Each must equal the next
   `W` record (address and value) or the run stops (`P9KERN FAIL`).
   Quart channel 0's transmit register (0xB000010C) is the console: the
   core's console file is made from the core's own writes.  Past the
   reference's last record (the testbench drains the pipeline) writes
   are neither checked nor printed.
3. **An interrupt is delivered at the reference's instruction
   boundary.**  The reference takes an interrupt between two
   instructions; `I n level pc` says after which record, at which level,
   and the PC it saved.  The core is to stop committing once it has
   retired `n` records, take the interrupt at the next instruction's PC
   (which must equal the recorded `pc`, or the run stops), and continue.
   This replays the reference's timing instead of modelling Quart's
   counter on the core: A2's rule (one device model), applied to time.
   Implemented 2026-11-24: the testbench hands the core each recorded
   interrupt through a queue (`armInterrupt`); EU_S3 commits nothing once
   the core's record count reaches `n` (counting the exception records
   the core makes outside EU_S3); the orchestrator then takes the
   interrupt at the PC of the instruction EU_S3 holds, which is dropped
   unexecuted, and hands the saved PC back (`takenInterrupt`) for the
   testbench to check.  If the boundary falls between a host and its
   folded branch -- two records, two reference steps -- the host commits
   alone and squashes to the branch, which the interrupt then saves
   (`splitHere`; not exercised yet).  The first interrupt of the boot is
   after record 2,848,972 (level 6, saved PC 0x800041ec, in `spllo`);
   it is the only one before 2,893,000.

### What the core gained: the privileged machine

`mkHobbitCoreSystem` (`bsv/HobbitCore.bsv`) is `mkHobbitCoreMmu` plus
what a kernel executes, in the structure `docs/bluespec_architecture.md`
describes -- a control-register box, and stage fields carried to the
one commit rule:

* **The CPU escape** (0x2C00, p. 3-14) is fused by the decoder with the
  instruction after it into one decoded entry (`DecodedInstr.cpu`); its
  mode-7 operands name the control registers 1..12 (Table 1-24, p. 1-26),
  and 0 or 13..15 decode as exception 6 (p. 1-27).  A CPU instruction
  waits for an empty pipeline in EU_S1 (`drainFirst`) and squashes
  everything after it at commit (`serialize`), so it reads committed
  state and what follows sees its writes.
* **`mkHobbitCtl`**, the control-register box: CONFIG (with KL and PX),
  TIMER1/2 (registers only; nothing counts them yet), ID (0x1000003B,
  the reference's choice), and the reads of all twelve.  EU_S3's commit
  rule is its only writer (`apply`), KCALL's ISP and SHAD included.  The
  PSW stays the core's register, SP/MSP the stack cache's, ISP/SHAD and
  FAULT the event unit's (which sets FAULT on a read or write fault),
  STB the MMU's.  Reserved bits read
  as 0 and are masked on write (PSW 0x1FFF0, STB 0xFFFFF800, CONFIG
  0xFFFF0000, the pointers' low four bits); an SP write sets MSP = SP
  (p. 1-13); SHAD follows a written CSP (p. 1-16).
* **CSP = ISP** (PSW bit 9 = 0, p. 1-12): stack operands are formed
  from the ISP (EU_S1's `csp`, separate from the cache window, which
  stays SP's); ENTER sets ISP = SHAD = target, RETURN and POPN move the
  ISP, CATCH is a no-op (pp. 3-10, 3-19, 3-38, 3-40), each serializing.
* **CRET** (p. 3-15) and **KRET** (p. 3-30): the frame's words at
  ISP+0/4/8/12 are read through EU_S1's two read ports and two
  pointed-to slots; PC and PSW restored, ISP += 16, SHAD = the new CSP.
  CRET's CATCH portion is issued by EU_S3 one clock after the CRET
  commits, so the data face translates it under the *restored* PSW.
* **ENTER's PSW.E** (Table 1-8, pp. 3-19..3-21), **FLUSHI/FLUSHP**
  (empty the decoded store as the serializing squash refetches),
  **FLUSHPTE** (every TLB entry; a superset of p. 3-27's one entry),
  **CONFIG.PX** (a dyadic three-parcel absolute takes PC[31:29],
  p. 1-23).
* **The interlocked ORI/ANDI/ADDI** (pp. 3-37, 3-8, 3-6), in every core
  (`docs/conformance_1to1.md` §1d #1).
* **Events in the kernel's memory.**  `mkHobbitCoreSystem` takes the
  event unit's memory as a parameter (the testbench's is the board's
  RAM, `pk_peek`/`pk_evwrite`), and its event unit (`mkHobbitEventsSys`)
  translates the frame and the vector read at kernel level whatever the
  level the event interrupts, as the reference does.  KCALL's own frame
  goes through the stack cache's memory port; its first word is written
  in the commit clock under the caller's PSW, so EU_S3 tells the data
  face to translate that write at kernel level (`kernelNow`).  p. 3-29
  says a fault on those writes resets the part; the kernel-level reading
  is the reference's (§1d #7).
* **Exceptions as the reference records them**: an operand read fault
  makes a `trap=1` record of its own (the instruction never commits);
  an exception's record has no write (only the unimplemented-instruction
  sequence's stores `*(CSP) = PC`); CRET's record waits for its CATCH
  portion and carries the MSP the portion reached; a read fault in that
  portion is taken at the restored PC with MSP at the blocks filled
  (§1d #5, #6, #8).
* In the other cores nothing else changes: a CPU instruction is still
  `TR_CPU` and CRET/KRET/FLUSH* the unimplemented sequence, as the
  goldens and the smoke test require.

### How far it gets

Every record matches through **2,893,000**, on the reference as merged
2026-11-23 (EEPROM, rtc and SONIC models; the idle skip off for the
recording).  The record numbers are that reference's; on the one before
it (no EEPROM/rtc reads) the boot reached `netadd` at 2,658,001 and
`userinit` at 2,815,122, and the core matched it through 2,825,000.

| record | reached |
|---:|---|
| 2,064 | `_virtual`: the first CRET, into virtual addressing |
| 125,203 | `main` |
| 126,600 | `tas`'s `ORI` -- found the interlocked forms missing (§1d #1) |
| 2,088,445 | `mmuinit` |
| 2,621,219 | `uartputs`: the first console byte |
| 2,681,671 | `netadd` -- found the wrong-path fault (§1d #2) |
| 2,838,988 | `userinit` |
| 2,848,972 | the first interrupt, level 6, in `spllo` (§1d #3) |
| 2,849,530 | the interrupt return's `CATCH *R4` (§1d #4) |
| 2,883,341 | `touser` |
| 2,883,347 | its CRET to `/boot`: the CATCH portion faults on the user stack (§1d #5) |
| 2,883,355 | the fault handler reads FAULT (§1d #6) |
| 2,886,866 | **`/boot` runs in user mode** (its first instruction, `0x1020`) |
| 2,886,867 | its first fetch fault, a `trap=1` record (§1d #8) |
| 2,888,578 | `/boot`'s first system call, `KCALL` (§1d #7) |

and the console is the reference's, byte for byte:

```
1364 free pages, 5456K bytes, swap 27856K, highwater 272K, headroom 340K
```

### What blocks the core next

1. **A write fault on a committed store** (record 2,893,033, the
   kernel's `evenaddr` writing a user address, `0xffbfffec`): the
   reference takes the exception at the store, which does not retire
   (a `trap=1` record, no write); the core has already retired the store
   when the stack cache's memory port reports the fault, and then takes
   the exception.  A store whose translation can fault has to be checked
   before it commits (or its record held until its write is accepted).
2. **The operand-fault record** (§1d #8) has met no case before record
   2,893,000: no operand read faults there.  It is untested.
3. **Device DMA** (SONIC, once `/boot` starts BOOTP) is not in the
   replay.
4. **The reference walks the tables at every access**; the core's TLBs
   and NPSRs cache entries (the walk writes R/M back when it fills one).
   Software that changes a table and flushes behaves the same on both;
   software that relies on a stale entry, or on R/M being set by an
   access that hit the TLB, would not.  Nothing up to record 2,825,000
   differed.
