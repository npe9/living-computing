# Getting tape data into the model: one interface, two sources

Status: **design and recommendation, with measurements.** Nothing in
`bsv/` was changed to produce it. Every number below is either a
command run in this worktree (quoted so it can be re-run), a citation
to a file on this machine (path given), or explicitly marked as an
inference or as recollection. Measurements taken 2026-10-16, on a
machine at load average ~180, so CPU times are real and wall times are
not comparable to a quiet machine.

The question answered: **how to represent the MCP master system tape
with the ULX3S's SD card or another data source**, with one interface
the rest of the model sees, so that Bluesim reads a host file and the
FPGA reads the card without the model forking into two versions.

Where the tape *content* comes from is a separate problem (no
machine-readable 7030 artifact is known to exist; see
`docs/archival_inventory.md`). This note assumes the image will exist
as a file and designs the path that carries it.

---

## 0. The answer in one paragraph

Give the tape a **request/response interface**,
`Server#(TapeRequest, TapeResponse)`, the sibling of the
`MemoryServer#(addr,256)` that
`~/src/ulx3s-experiments/flute-ulx3s/src/Sdram_Controller.bsv` already
presents on this board. `StretchIO` stops owning tape storage and
instead exposes the matching `Client`, which the testbench or the
board top level connects with `mkConnection` — the same shape as that
file's own `mkConnection(sdram_master.memory, sdram.memory)`. Then
write three implementations of the one interface:
`mkTapeSourceVector` (today's 16-word `Vector`, so the regression
suite stays green), `mkTapeSourceFile` (a host file through
`import "BDPI"`, Bluesim only), and `mkTapeSourceSD` (the microSD
card, bitstream only). **The split is forced, not stylistic**: §5
shows, with the error message, that a BDPI import compiles to a
Verilog VPI task that yosys refuses. The measured cost of the SD leg
is **788 LUT4 / 720 FF / 112 CCU2C / 2 DP16KD**, against **1,025 LUT4
and 1,024 FF given back** by taking the tape `Vector` out of
`mkStretchIO` (§7.4). Both are *standalone* synthesis deltas, so
`docs/fpga_feasibility.md` §2.5's caveat applies — a flattened core
may optimise either figure differently — but on this evidence area is
not the reason to say no.

---

## 1. The ULX3S SD socket, as the files on this machine give it

### 1.1 The pinout — verified here, not recalled

`~/src/ulx3s-experiments/bluespec-ulx3s/toolchain/prjtrellis/examples/ulx3s/ulx3s_v20.lpf`,
whose own third line is `## ULX3S v2.x.x and v3.0.x`, lines 112–128:

```
## SD card "sdcard", "usb" sheet
LOCATE COMP "sd_clk"  SITE "H2";   # sd_clk            WiFi_GPIO14
LOCATE COMP "sd_cmd"  SITE "J1";   # sd_cmd_di (MOSI)  WiFi GPIO15
LOCATE COMP "sd_d[0]" SITE "J3";   # sd_dat0_do (MISO) WiFi GPIO2
LOCATE COMP "sd_d[1]" SITE "H1";   # sd_dat1_irq       WiFi GPIO4
LOCATE COMP "sd_d[2]" SITE "K1";   # sd_dat2           WiFi_GPIO12
LOCATE COMP "sd_d[3]" SITE "K2";   # sd_dat3_csn       WiFi GPIO13
LOCATE COMP "sd_wp"   SITE "P5";   # not connected
LOCATE COMP "sd_cdn"  SITE "N5";   # not connected
IOBUF PORT "sd_clk"  PULLMODE=UP IO_TYPE=LVCMOS33 DRIVE=4;
...   (same for sd_cmd, sd_d[0..3], sd_wp, sd_cdn)
IOBUF PORT "sd_d[2]" ... ; # WiFi GPIO12 pulldown bootstrapping requirement
```

Three facts follow directly, with no recollection involved:

- **Voltage is LVCMOS33**, every SD signal, stated in the file.
- **All six SD signals are on ECP5 bank 6**, resolved on this machine
  from Project Trellis' own I/O database rather than from memory:

  ```sh
  cd /opt/homebrew/share/trellis/database/ECP5/LFE5U-85F
  python3 -c "import json; d=json.load(open('iodb.json')); ..."
  ```

  | lpf name | site | bank | special function | DQS group |
  |---|---|---|---|---|
  | `sd_clk`  | H2 | 6 | **`PCLKT6_0`** (primary clock input) | LDQ53 |
  | `sd_cmd`  | J1 | 6 | — | LDQSN53 |
  | `sd_d[0]` | J3 | 6 | `GR_PCLK6_1` | LDQ53 |
  | `sd_d[1]` | H1 | 6 | — | LDQ53 |
  | `sd_d[2]` | K1 | 6 | — | LDQ53 |
  | `sd_d[3]` | K2 | 6 | — | LDQ53 |
  | `sd_wp`   | P5 | 6 | — (lpf: not connected) | LDQ89 |
  | `sd_cdn`  | N5 | 6 | — (lpf: not connected) | LDQ89 |

  `sd_clk` landing on a primary clock *input* pad is incidental for a
  host (the FPGA drives that pin), but it means the pad has the
  routing to be clocked from, should a card-side or clock-loopback
  design ever want it.
- **There is no card-detect and no write-protect signal.** Both pads
  exist and both are commented "not connected" in the constraints
  file. A tape model therefore cannot ask "is a card inserted"; it can
  only ask "did the reader get a sector out of it". `mkTapeSourceSD`
  below defines `mediaPresent` that way for exactly this reason.

### 1.2 Four-bit SD mode: possible on the pins, absent from every core found

The pins for 4-bit mode are **present and constrained** — `sd_d[1..3]`
are brought out, which SPI mode does not need. So the board does not
restrict you to SPI or to 1-bit SD.

What the *gateware* found on this machine does is another matter, and
it is 1-bit:
`~/src/bsoc-cursor/FPGA-SDcard-Reader/RTL/sd_reader.v:21` says in its
own comment "this design do not use sddat1~sddat3", and its port list
has `sddat0` only. So: **4-bit is a board capability, not an
available-today capability** — see §2 for the one 4-bit thing found
and why it does not count.

### 1.3 Which revisions have the socket — partly established, partly not

**Established from a file here:** the constraints file that contains
the SD section declares itself `## ULX3S v2.x.x and v3.0.x`, so the
socket and that exact pinout are documented for v2.x.x and v3.0.x.

**Established indirectly:** the SD pin comments name each signal's
ESP32 alias (`WiFi_GPIO14`, `WiFi GPIO15`, `WiFi GPIO2`, …), i.e. the
SD bus is **shared with the ESP32** on this board. That is a real
constraint on §3's "use the ESP32" option and on anything that assumes
the ESP32 is quiescent.

**Not established:** anything about revisions *earlier* than v2.0. I
searched this machine for EMARD's board manual —
`find ~/src -maxdepth 6 -iname 'MANUAL.md'` returned seven files, none
of them the ULX3S manual — and `find ~/src -maxdepth 4 -iname '*ulx3s*'`
turns up four project directories, bitstreams and `.lpf` files but no
board documentation or schematic. §8 records this as a gap rather than
filling it from memory.

---

## 2. Existing cores, in order of fit — with paths

Searched: `~/src` (683 top-level directories) for filenames matching
`*sdcard*`, `*sd_card*`, `*sdspi*`, `*sd_spi*`, `*sdmmc*`,
`sd_controller*`; for the SD-initialisation signature
`ACMD41|acmd41|CMD55` across `*.v *.sv *.bsv *.vhd *.py`; and for
`sd_clk` and `spi` across `*.bsv`. Results, best fit first.

### 2.1 `~/src/bsoc-cursor/FPGA-SDcard-Reader` — the recommendation

WangXuan95's FPGA SDcard File Reader, present in full (RTL + an
iverilog testbench + a card model):

| file | lines | what |
|---|---|---|
| `RTL/sdcmd_ctrl.v` | 139 | SD command/response shifter, CRC7, clock divider |
| `RTL/sd_reader.v` | 262 | card init (CMD0/8/55/ACMD41/2/3/7/16) + CMD17 sector read |
| `RTL/sd_file_reader.v` | 575 | the above + MBR/FAT16/FAT32 parsing, reads a named file |
| `SIM/sd_fake.v` | 658 | **a card model**, so the host side can be tested without hardware |
| `SIM/tb_sd_file_reader.v` | 455 | the testbench that drives it |

Verilog-2001, no vendor primitives, tri-state `sdcmd` only. Measured
here with the installed open flow:

```sh
yosys -p 'read_verilog sdcmd_ctrl.v sd_reader.v; synth_ecp5 -top sd_reader; stat'
```

| core | LUT4 | TRELLIS_FF | CCU2C | PFUMX | L6MUX21 | BRAM | yosys CPU |
|---|---|---|---|---|---|---|---|
| `sd_reader` (sector read) | **469** | **308** | **98** | 60 | 18 | 0 | 0.87 s |
| `sd_file_reader` (+ FAT16/32) | **2,211** | **1,159** | **461** | 249 | 8 | 0 | — |

Two warnings, both expected and both benign for this flow: "Yosys has
only limited support for tri-state logic" (`sdcmd_ctrl.v:41`, the one
`assign sdcmd = sdcmdoe ? sdcmdout : 1'bz` — §6.3 removes it), and
"Replacing memory `fname` with list of registers" in the FAT version.

The FAT layer costs **4.7× the LUT4 and 4.7× the carry cells** of raw
sector reading. That ratio decides §4's recommendation.

### 2.2 `~/src/bsoc-cursor/bluespec-ip/src/HighSpeed/SDMMC/` — Bluespec, and it does not compile

This is the find that would have been the headline — a 1,748-line
Bluespec SD/MMC controller family, in the user's own tree, including
`SDMMC_WideBus.bsv` (234 lines) which is explicitly **4-bit mode**
(`ACMD6`, `Bit#(4) sddat_out/sddat_oe`), the one 4-bit implementation
anywhere in the search.

It is generated code. `SDMMC_Reader.bsv`'s header says "Translated
from sd_reader.v" and "Implementation Status: [IMPLEMENTATION]", and
`SDMMC_Reader.bsv:178` has the comment "// Would trigger CMD17 in
separate rule" where the CMD17 issue should be. So I compiled it
rather than citing it:

```sh
bsc -verilog -p ~/src/bsoc-cursor/bluespec-ip/src/HighSpeed/SDMMC:+ \
    -g mkSDMMC_Reader -u .../SDMMC_Reader.bsv
Error: ".../SDMMC_Reader.bsv", line 181, column 8: (P0022)
  Attributes not allowed for method
```

That is an `(* always_ready *)` on a method *definition* inside the
module body, which belongs on the interface declaration. Three
compiles, three distinct failure classes:

1. `SDMMC_Reader.bsv:181` — `(P0022) Attributes not allowed for method`.
2. After mechanically moving every such attribute, the same error
   reappears at `SDMMC_CMD.bsv:179`, and after that at a dozen more
   sites (14 attribute lines in `SDMMC_Reader.bsv`, 16 in
   `SDMMC_CMD.bsv`, 13 in `SDMMC_MultiBlock.bsv`, 7 each in
   `SDMMC_Proper.bsv` and `SDMMC_Data.bsv`, 5 in `SDMMC_WideBus.bsv`).
3. With all of those stripped, a real type error:
   `SDMMC_CMD.bsv:118: (T0031) ... no instances of the form
   Bits#(Integer, 7)`.

**Verdict: not usable as found.** It is a sketch in the right shape,
not a core. If 4-bit mode is ever wanted, `SDMMC_WideBus.bsv` is worth
reading for its structure, but the working 4-bit reference would have
to come from elsewhere. I stopped after the third error rather than
keep repairing generated code.

### 2.3 Also found, and why each is not the answer

| path | what it is | why not |
|---|---|---|
| `~/src/bsoc-cursor/github-cores/litesdcard/` | LiteSDCard (LiteX/migen), with `emulator/verilog/sd_{link,phy}.v` | Python-generated gateware; brings LiteX's build system with it. The right answer *if* the project adopts LiteX (`docs/fpga_feasibility.md` §3.5 lists that as a live option), wrong answer as a drop-in. |
| `~/src/Apple-II_MiSTer/sys/sd_card.sv`, `~/src/NES_MiSTer/sys/sd_card.sv`, `~/src/MiSTerLaggy_MiSTer/sys/sd_card.sv` | MiSTer's `sd_card` | This is the **card side**, not the host side: it presents a fake SD card to a core and services it from the HPS ARM over a MiSTer-specific bus. No ARM here. |
| `~/src/sv-yosys/third_party/cvw/testbench/sdc/sdModel.sv` | CORE-V Wally's SD card model | A simulation model, like `sd_fake.v`; useful for testing, not for synthesis. |
| `~/src/alto-bluespec/src/Disk.bsv` + `sim/host.c` | the user's own Bluespec Alto, Diablo 31 disk via BDPI | **Not an SD core, but the single most relevant thing found** — it is the proven answer to §5. See there. |

---

## 3. The alternatives, compared

Capacities and costs are measured where the table says "measured" and
inferred where it says so. "Bluespec difficulty" is relative to what
this project already does.

| source | capacity | bandwidth | LUT/BRAM cost | Bluespec difficulty | swap media without a host? |
|---|---|---|---|---|---|
| **microSD, 1-bit SD bus** (`sd_reader`) | the card | ~0.52 MB/s at a 25 MHz clk (§7.1, derived from the RTL) | **measured 788 LUT4 / 720 FF / 112 CCU2C / 2 DP16KD** for the whole path incl. buffers (§7.4) | moderate: one `import "BVI"`, one 4-line tri-state split, ~170 lines of BSV — written and compiled, §6 | **yes** |
| microSD, 1-bit SD bus + FAT (`sd_file_reader`) | the card | same | measured core alone 2,211 LUT4 / 1,159 FF / **461 CCU2C** | same, one module swapped | yes, and the file is named, not dd'd |
| **SPI flash** (board's config flash) | **16,777,216 B measured** (`~/src/ulx3s-experiments/ulx3s-bitstreams/flash-backups/ulx3s-factory-20261001.bin`), minus a **1,107,757 B** bitstream (`flute-ulx3s/build/ulx3s_top.bit`) → ≈15 MB nominally free | ~3 MB/s at 25 MHz, 1-bit SPI (inference) | an SPI master is smaller than an SD host; I did not measure one, so no number. **Plus the awkward part:** the config CCLK is not a normal pad — `ulx3s_v20.lpf:86` has `#LOCATE COMP "flash_clk" SITE "U3"` *commented out*, and reaching it from user logic needs the ECP5 `USRMCLK` primitive (recollection about ECP5, not verified here) | low once `USRMCLK` works | no — reflashing needs the host and the programmer |
| **ESP32** (on-board) | whatever wifi delivers | low | needs a whole ESP32↔FPGA link that does not exist | **highest** | yes (over wifi) |
| **USB-serial** (FT231X) | unbounded, streamed | 3 Mbit/s advertised (cited in `docs/fpga_feasibility.md` §3.5) | a UART RX is ~100–200 LUT4 (inference); `~/src/ulx3s-experiments/.../src/Uart.bsv` exists | low, and **the project needs this path anyway** to load programs (§3.5) | no — host must stay attached |
| **BRAM/`Vector`** (status quo) | **16 words** | combinational | **measured 1,025 LUT4 + 1,024 FF** of the current `mkStretchIO` (§7) | zero — it is what exists | n/a |
| **SDRAM staging** | 32 MB on board | 256 bits / 29 clocks, per `Sdram_Controller.bsv`'s own header | driver exists and is understood; needs the §3.3 interposer | low *after* the interposer, blocked before it | no, but it is a destination, not a source |

### What I recommend, and why

**microSD, 1-bit SD bus, `sd_reader` with raw sector (LBA) addressing,
behind the `TapeSource` interface, with the host-file BDPI source used
in Bluesim.** Four reasons, in order of weight:

1. **It is the only option that is simultaneously big enough for a
   reel and swappable without a host.** A 2400 ft 729 IV reel at
   556 bpi is about 16 MB of data; SPI flash can hold one but only via
   the programmer, serial needs the host attached, and the `Vector`
   holds sixteen words. "Put a different tape on the drive" should be
   "put a different card in the slot".
2. **It is close to free.** The SD path measures 788 LUT4 / 720 FF /
   112 CCU2C / 2 DP16KD, and removing the tape `Vector` from
   `mkStretchIO` gives back 1,025 LUT4 and 1,024 FF. Net ≈ **−237
   LUT4, −304 FF, +112 CCU2C, +2 DP16KD** (§7.4) — standalone deltas,
   with §2.5's flattening caveat. Against the ~41,070 CCU2C figure
   reported to me for the whole core, +112 is **+0.27 %**.
3. **The one interface makes the decision reversible.**
   `Server#(TapeRequest, TapeResponse)` says nothing about the backing
   store, so "stage the image into SDRAM at power-up and serve the
   tape from there" is a fourth implementation of the same interface
   later, not a redesign. That is why this note does not have to
   decide SD-versus-SDRAM now.
4. **It can be tested before hardware exists.** `SIM/sd_fake.v` (658
   lines) is a card model; `mkTapeSourceSD`'s generated Verilog plus
   `sd_fake.v` is a cosimulation under iverilog or verilator that
   checks the hardware leg without a board.

Against `sd_file_reader`'s FAT convenience: **461 CCU2C versus 98**,
on a design already reported at ~98 % of an 85F's carry cells. Start
raw (`dd if=mcp.tape of=/dev/diskN seek=2048`, one command) and keep
FAT as a one-line module swap for when area allows. Both are
implementations of the same `TapeSource`; nothing above them changes.

USB-serial is the honourable second place and is **not** in
competition: it is already on the critical path for loading programs
(§3.5), and the first bring-up will very likely use it for the tape
too, because it needs no new core at all. The argument for SD is that
a machine that boots MCP from a card you can hand to someone is the
thing the project is for.

---

## 4. The interface

### 4.1 Why it is a `Server`, and why `StretchIO` exposes a `Client`

`Sdram_Controller.bsv:69` presents
`interface MemoryServer #(Bits_per_Raw_Mem_Addr, Bits_per_Raw_Mem_Word)`
and `ULX3S_Top.bsv` connects it with
`mkConnection(sdram_master.memory, sdram.memory)`. The tape wants the
identical shape, so:

```bsv
typedef Bit#(24) TapeWordAddr;        // 2^24 words = 134 MB

typedef struct {
   Bool         write;
   TapeWordAddr addr;
   Word64       data;    // ignored when write == False
} TapeRequest deriving (Bits, Eq, FShow);

typedef struct {
   Word64 data;
   Bool   atEnd;         // addr was past the end of the mounted image
} TapeResponse deriving (Bits, Eq, FShow);

interface TapeSource;
   interface Server#(TapeRequest, TapeResponse) words;
   (* always_ready *) method Bool         mediaPresent;
   (* always_ready *) method TapeWordAddr capacity;
endinterface
```

The *placement* matters as much as the shape. The obvious move —
`module mkStretchIO#(TapeSource tape)(StretchIO)` — is **blocked**:
`docs/fpga_feasibility.md` §1.2 already records bsc refusing separate
code generation for `mkLookAhead` and friends with
"Separate code generation for module `mkLookAhead', which has an
interface argument, is not supported", and a `TapeSource` argument
would do the same to `mkStretchIO` and hence to the §2.4 measurement
and to `mkStretchCore`'s own `(* synthesize *)` boundary.

So the source is instantiated **outside** the core and the core
exposes the other half of the pair — exactly how Flute exposes a
memory master:

```bsv
// in StretchIO's interface, replacing readTapeWord/writeTapeWord:
interface Client#(TapeRequest, TapeResponse) tape_client;
```

and in `StretchCore`'s interface, forwarded up. The Bluesim testbench
then does

```bsv
TapeSource src <- mkTapeSourceFile;                 // or mkTapeSourceVector
mkConnection(core.tape_client, src.words);
```

and the board top level does

```bsv
TapeSourceSD sd <- mkTapeSourceSD_ULX3S;
mkConnection(core.tape_client, sd.tape.words);
```

One model, two top levels, and the core's synthesis boundary intact.

### 4.2 What changes in `StretchIO.bsv` and `StretchCore.bsv`

Quoted, not applied (this note changed no existing file):

- `StretchIO.bsv`: delete `Vector#(TapeWords, Reg#(Word64)) tapeImg`
  and the `readTapeWord`/`writeTapeWord` methods; add the `Client`
  sub-interface plus a one-entry request FIFO and response FIFO.
  **Keep `tapePos`, `setTapePos` and everything in the file's "TAPE
  POSITION", "CONTROL FUNCTIONS" and `TapeWords` discussion exactly as
  it is** — position, REWIND and BACKSPACE BLOCK are properties of the
  *drive*, which stays in `StretchIO`; only the *medium* moves out.
  `TapeWords` stops being the medium's size and becomes the drive's
  idea of where end-of-tape is, which is now `src.capacity`.
- `StretchCore.bsv`: the `ioPending` FSM's tape arm stops calling
  `io.readTapeWord(i)` combinationally and instead enqueues a
  `TapeRequest` and waits for the response. §6.2 is about what that
  wait means.
- `tests/gen_tape_tb.py`: unchanged in intent — it still pre-loads and
  post-checks a 16-word tape, but through `mkTapeSourceVector`'s own
  loader methods rather than through `core.io`. This is the point of
  keeping `mkTapeSourceVector`: `tests/run_tests.sh` is the project's
  correctness oracle (AGENTS.md "How work is verified here"), and
  `decks/io_tape.strap` reaches End Exception by running off
  the end of a 16-word tape. That test must keep passing unchanged,
  and with `mkTapeSourceVector` it does.

---

## 5. The `$fopen` constraint, resolved: BDPI, and it is already proven in this user's tree

`StretchIO.bsv:40-48` says device storage is pre-loaded `Vector`s
because "bsc's `$fopen`/`$fgetc` are Actions, so a block transfer
would unroll into a statically-sequenced chain of file accesses
fighting the same one-write-per-rule constraint".

**That is true of `$fopen`/`$fgetc` and it is not binding, because
those are not the mechanism to use.** The mechanism is
`import "BDPI"` with a **value** result type — a foreign function
whose result is not `Action`/`ActionValue` may be called in a value
context, inside a rule, as many times as the rule likes, with no
Action sequencing at all.

This is not a guess. `~/src/alto-bluespec` — the user's own Bluespec
Alto — does exactly this for its Diablo 31 disk pack
(`src/Disk.bsv:18-23`):

```bsv
import "BDPI" function Bit#(32) host_disk_loaded();
import "BDPI" function Bit#(16) host_disk_cylinders();
import "BDPI" function Bit#(16) host_disk_read_word(Bit#(32) idx);
import "BDPI" function Action   host_disk_write_word(Bit#(32) idx, Bit#(16) data);
import "BDPI" function Action   host_disk_select(Bit#(32) cyl, Bit#(32) head, Bit#(32) sec);
import "BDPI" function Action   host_disk_commit();
```

with `sim/host.c:315-368` on the other side (`load_disk()` slurps the
`.dsk`, `host_disk_read_word` is a plain array index) and the image
path taken from the environment (`sim/host.c:206`, `ALTO_DISK`). The
link is one extra argument to the second bsc invocation
(`alto-bluespec/Makefile`):

```make
$(BSC) -sim -e $(TOP) -bdir $(BUILD) -simdir $(BUILD) \
    -o $(BUILD)/alto-sim -Xc -I$(ROM) -Xc -I$(SIM) \
    $(BUILD)/$(TOP).ba $(SIM)/host.c
```

`stretch/bsv/build.sh`'s second line is already that shape, so the
change there is one filename.

### 5.1 Tested here, end to end

`TapeSourceFile.bsv` (reproduced in §6.2), a six-word host image, and
a four-rule testbench, built and run on this machine:

```sh
bsc -sim -p src:…/stretch/bsv:+ -g mkTapeTb -u src/TapeTb.bsv
bsc -sim -e mkTapeTb -o tape_sim sim/host_tape.c
STRETCH_TAPE=tape.img ./tape_sim
```

```
host_tape: mounted …/tape.img, 6 words
word 0 = 0101010101010101  atEnd=0  present=1  cap=6
word 1 = 0202020202020202  atEnd=0  present=1  cap=6
word 2 = 0303030303030303  atEnd=0  present=1  cap=6
word 3 = 0404040404040404  atEnd=0  present=1  cap=6
word 4 = 0505050505050505  atEnd=0  present=1  cap=6
word 5 = 0606060606060606  atEnd=0  present=1  cap=6
```

Six streaming reads, one per rule firing, from a host file, with no
`$fopen` anywhere and no pre-load phase. **The constraint in
`StretchIO.bsv`'s header is real about the primitive it names and does
not apply to a streaming source.** That header should be amended when
this lands.

### 5.2 And here is why the two-module split is forced

The obvious objection is "then why not use `mkTapeSourceFile` on the
board too?" Measured answer. bsc *does* give a BDPI import a Verilog
form — as a VPI task:

```
$ bsc -verilog … -g mkTapeSourceFile -u src/TapeSourceFile.bsv
VPI wrapper files created: …/vpi_wrapper_host_tape_read_word.{c,h}
Verilog file created: …/mkTapeSourceFile.v
```

and that Verilog is fine for a VPI-capable simulator and useless for
synthesis:

```
$ yosys -p 'read_verilog mkTapeSourceFile.v; synth_ecp5 -top mkTapeSourceFile'
mkTapeSourceFile.v:144: ERROR: Can't resolve function name
  `\$imported_host_tape_read_word'
```

So `TapeSourceFile.bsv` must not be in the hierarchy a bitstream
elaborates. Two packages, one interface, chosen at the top level — not
a `` `ifdef ``, not two models.

---

## 6. Real Bluespec, compiled

All three packages below were typechecked and code-generated on this
machine with the Homebrew bsc the project pins
(`/opt/homebrew/Cellar/bsc/2026.01/bin/bsc`, `BLUESPECDIR` set as
`build.sh` sets it), against the real `StretchTypes.bsv` from
`bsv/`. Sources are in this session's scratchpad at
`scratchpad/tape/src/`.

### 6.1 `TapeSource.bsv` — the interface and the in-bitstream `Vector`

```bsv
package TapeSource;

import StretchTypes::*;
import ClientServer::*;
import GetPut::*;
import FIFOF::*;
import Vector::*;

typedef Bit#(24) TapeWordAddr;

typedef struct {
   Bool         write;
   TapeWordAddr addr;
   Word64       data;
} TapeRequest deriving (Bits, Eq, FShow);

typedef struct {
   Word64 data;
   Bool   atEnd;
} TapeResponse deriving (Bits, Eq, FShow);

interface TapeSource;
   interface Server#(TapeRequest, TapeResponse) words;
   (* always_ready *) method Bool         mediaPresent;
   (* always_ready *) method TapeWordAddr capacity;
endinterface

// nWords is a Bit#(24), not an Integer, so the module can keep its own
// (* synthesize *) boundary -- bsc: "A parameter of the module uses the
// type `Integer' which is not in the Bits class" (T0043).
(* synthesize *)
module mkTapeSourceVector#(TapeWordAddr nWords)(TapeSource);
   Vector#(16, Reg#(Word64)) img <- replicateM(mkReg(0));
   FIFOF#(TapeRequest)  reqF  <- mkLFIFOF;
   FIFOF#(TapeResponse) respF <- mkLFIFOF;

   rule rl_serve;
      let r = reqF.first; reqF.deq;
      Bool past = r.addr >= nWords;
      Bit#(4) i = truncate(r.addr);
      if (r.write && !past) img[i] <= r.data;
      respF.enq(TapeResponse { data: past ? 0 : img[i], atEnd: past });
   endrule

   interface Server words;
      interface Put request  = toPut(reqF);
      interface Get response = toGet(respF);
   endinterface
   method Bool mediaPresent = True;
   method TapeWordAddr capacity = nWords;
endmodule

endpackage
```

`bsc -verilog -g mkTapeSourceVector`: *Verilog file created*, no
errors, no warnings. The `Integer`-parameter note in the comment is a
real bsc error I hit and fixed, not a hypothetical; it recurs in §6.3.

### 6.2 `TapeSourceFile.bsv` — the Bluesim leg

```bsv
package TapeSourceFile;

import StretchTypes::*;
import TapeSource::*;
import ClientServer::*;
import GetPut::*;
import FIFOF::*;

// Value (not Action) imports: a BDPI function whose result type is not
// Action/ActionValue may be called in a value context, which is what
// makes a host file readable from inside a rule at all. This is the
// resolution of StretchIO.bsv's "$fopen/$fgetc are Actions" note.
import "BDPI" function Bit#(32) host_tape_loaded();
import "BDPI" function Bit#(32) host_tape_words();
import "BDPI" function Bit#(64) host_tape_read_word(Bit#(32) idx);
import "BDPI" function Action   host_tape_write_word(Bit#(32) idx, Bit#(64) d);

module mkTapeSourceFile(TapeSource);
   FIFOF#(TapeRequest)  reqF  <- mkLFIFOF;
   FIFOF#(TapeResponse) respF <- mkLFIFOF;

   rule rl_serve;
      let r = reqF.first; reqF.deq;
      Bit#(32) idx  = zeroExtend(r.addr);
      Bool     past = idx >= host_tape_words();
      if (r.write && !past)
         host_tape_write_word(idx, r.data);
      respF.enq(TapeResponse { data: past ? 0 : host_tape_read_word(idx),
                               atEnd: past });
   endrule

   interface Server words;
      interface Put request  = toPut(reqF);
      interface Get response = toGet(respF);
   endinterface
   method Bool         mediaPresent = (host_tape_loaded() != 0);
   method TapeWordAddr capacity     = truncate(host_tape_words());
endmodule

endpackage
```

`bsc -sim -g mkTapeSourceFile`: four *Foreign import file created*
lines and *Elaborated module file created*, no errors. Run under
Bluesim against a real file in §5.1. The C side
(`scratchpad/tape/sim/host_tape.c`, 55 lines) is `load_disk()` from
`alto-bluespec/sim/host.c` with the record layout changed: the image
is read big-endian, eight bytes to a word, because byte 0 of a record
is IBM bits 0–7 — the leftmost byte of the word.

### 6.3 `TapeSourceSD.bsv` — the hardware leg

The SD protocol is *not* reimplemented; `sd_reader.v` is imported.
`sd_reader` has `inout sdcmd`, which an `import "BVI"` would rather
not see, so a shim splits it into out/oe/in — the same shape
`Sdram_Controller.bsv` already uses for
`sdram_dq_out`/`sdram_dq_oe`/`sdram_dq_in`. The shim is a 4-line edit
to two files, not a wrapper with a tri-state in it:

```verilog
// sdcmd_ctrl.v: replace `inout sdcmd,` with
    output wire         sdcmd_o,
    output wire         sdcmd_oe,
    input  wire         sdcmd_i,
// and replace
//   assign sdcmd = sdcmdoe ? sdcmdout : 1'bz;
//   wire sdcmdin = sdcmdoe ? 1'b1 : sdcmd;
// with
assign sdcmd_o  = sdcmdout;
assign sdcmd_oe = sdcmdoe;
wire   sdcmdin  = sdcmdoe ? 1'b1 : sdcmd_i;
// sd_reader.v: same three ports on its own port list, passed down.
```

Then:

```bsv
interface SDReaderPrim;
   method Action           startRead(Bit#(32) sector);
   (* always_ready *) method Bool     busy;
   (* always_ready *) method Bool     done;
   (* always_ready *) method Bool     outEn;
   (* always_ready *) method Bit#(9)  outAddr;
   (* always_ready *) method Bit#(8)  outByte;
   (* always_ready *) method Bit#(1)  sdclk;
   (* always_ready *) method Bit#(1)  sdcmdOut;
   (* always_ready *) method Bit#(1)  sdcmdOe;
   (* always_ready, always_enabled *) method Action sdcmdIn(Bit#(1) v);
   (* always_ready, always_enabled *) method Action sddat0(Bit#(1) v);
endinterface

import "BVI" sd_reader_shim =
module mkSDReaderPrim #(Integer clkDiv) (SDReaderPrim);
   parameter CLK_DIV  = clkDiv;
   parameter SIMULATE = 0;

   default_clock clk(clk);
   default_reset rstn(rstn);

   method startRead(rsector) enable(rstart);
   method rbusy    busy();
   method rdone    done();
   method outen    outEn();
   method outaddr  outAddr();
   method outbyte  outByte();
   method sdclk    sdclk();
   method sdcmd_o  sdcmdOut();
   method sdcmd_oe sdcmdOe();
   method sdcmdIn(sdcmd_i) enable((* inhigh *) EN_sdcmd_i);
   method sddat0(sddat0_i) enable((* inhigh *) EN_sddat0_i);

   schedule (busy, done, outEn, outAddr, outByte,
             sdclk, sdcmdOut, sdcmdOe, sdcmdIn, sddat0)
         CF (busy, done, outEn, outAddr, outByte,
             sdclk, sdcmdOut, sdcmdOe, sdcmdIn, sddat0);
   schedule startRead C  startRead;
   schedule startRead CF (busy, done, outEn, outAddr, outByte,
                          sdclk, sdcmdOut, sdcmdOe, sdcmdIn, sddat0);
endmodule
```

and the source itself — a ping-pong of two 512-byte sectors, with the
fill side and the serve side on opposite ports of one dual-port block
RAM:

```bsv
module mkTapeSourceSD #(Integer clkDiv, Bit#(32) baseLba) (TapeSourceSD);

   SDReaderPrim prim <- mkSDReaderPrim(clkDiv);

   // Two sectors, 64 Word64 each. Bank = addr[6].
   // DUAL port, not single: with mkBRAMCore1 bsc reported
   //   Rule "rl_collect" was treated as more urgent than "rl_lookup".
   //   Conflicts: calls to sbuf.put vs. sbuf.put   (G0010)
   // -- i.e. filling one bank would block serving the other, which is
   // exactly what the ping-pong exists to avoid.
   // Measured at 2 DP16KD, not 1: 128 x 64 = 8,192 bits would fit in
   // one 18 kbit block, but a DP16KD port is at most 36 bits wide.
   BRAM_DUAL_PORT#(Bit#(7), Word64) sbuf <- mkBRAMCore2(128, False);

   FIFOF#(TapeRequest)  reqF  <- mkFIFOF;
   FIFOF#(TapeResponse) respF <- mkFIFOF;

   Reg#(Bit#(32)) bankLba0 <- mkReg(0);   Reg#(Bool) bankOk0 <- mkReg(False);
   Reg#(Bit#(32)) bankLba1 <- mkReg(0);   Reg#(Bool) bankOk1 <- mkReg(False);
   Reg#(Bit#(1))  fillBank <- mkReg(0);   Reg#(Bool) filling <- mkReg(False);
   Reg#(Bit#(64)) acc      <- mkReg(0);
   Reg#(Bool)     wait1    <- mkReg(False);
   Reg#(Bool)     wait1End <- mkReg(False);

   function Bit#(32) lbaOf(TapeWordAddr a) = baseLba + zeroExtend(a >> 6);
   function Bit#(6)  wordInSector(TapeWordAddr a) = truncate(a);

   // ---- fill side: bytes arrive MSB-first inside the sector, and a
   // 7030 word is bits 0..63 left to right, so a plain shift-left
   // assembly puts byte 8w at bits 0-7 of word w.
   //
   // Gated on `filling`, not on prim.outEn alone: sd_reader re-issues
   // CMD17 by itself when sddat_stat reaches RTIMEOUT (sd_reader.v's
   // READING2 arm), and its init sequence runs without this module
   // asking, so a byte stream can arrive that no fill of ours
   // requested; without the guard those bytes would land in whichever
   // bank fillBank happens to name. Adding the guard also made the
   // design smaller (972 -> 788 LUT4), because yosys can then prune
   // the unconditional write path.
   rule rl_collect (filling && prim.outEn);
      Bit#(64) a = {acc[55:0], prim.outByte};
      acc <= a;
      if (prim.outAddr[2:0] == 3'b111)
         sbuf.a.put(True, {fillBank, prim.outAddr[8:3]}, a);
   endrule

   rule rl_fill_done (filling && prim.done);
      filling <= False;
      if (fillBank == 0) bankOk0 <= True; else bankOk1 <= True;
   endrule

   // ---- serve side
   rule rl_lookup (!wait1);
      let r = reqF.first;
      Bit#(32) want = lbaOf(r.addr);
      Bool hit0 = bankOk0 && bankLba0 == want;
      Bool hit1 = bankOk1 && bankLba1 == want;
      if (hit0 || hit1) begin
         reqF.deq;
         Bit#(1) b = hit0 ? 0 : 1;
         sbuf.b.put(False, {b, wordInSector(r.addr)}, ?);
         wait1 <= True;  wait1End <= False;
      end
      else if (!filling && !prim.busy) begin
         // Miss: do not evict the bank the next sequential read wants.
         Bit#(1) b = (bankOk0 && bankLba0 == want + 1) ? 1 : 0;
         fillBank <= b;
         if (b == 0) begin bankOk0 <= False; bankLba0 <= want; end
         else        begin bankOk1 <= False; bankLba1 <= want; end
         filling <= True;
         prim.startRead(want);
      end
   endrule

   rule rl_reply (wait1);
      respF.enq(TapeResponse { data: sbuf.b.read, atEnd: wait1End });
      wait1 <= False;
   endrule

   interface TapeSource tape;
      interface Server words;
         interface Put request  = toPut(reqF);
         interface Get response = toGet(respF);
      endinterface
      // No card-detect line is wired on the ULX3S (sd_cdn is marked
      // "not connected" in ulx3s_v20.lpf), so "media present" is
      // "the reader got a sector out of it".
      method Bool         mediaPresent = bankOk0 || bankOk1;
      method TapeWordAddr capacity     = maxBound;
   endinterface

   interface SDPins pins;
      method Bit#(1) sd_clk     = prim.sdclk;
      method Bit#(1) sd_cmd_out = prim.sdcmdOut;
      method Bit#(1) sd_cmd_oe  = prim.sdcmdOe;
      method Action  sd_cmd_in(Bit#(1) v)  = prim.sdcmdIn(v);
      method Action  sd_dat0_in(Bit#(1) v) = prim.sddat0(v);
   endinterface
endmodule

// The synthesis boundary. mkTapeSourceSD takes an Integer parameter
// (sd_reader's CLK_DIV is a Verilog parameter, so it has to be a
// compile-time Integer) and bsc will not give such a module its own
// module (T0043). One wrapper pinning the board's values fixes that.
(* synthesize *)
module mkTapeSourceSD_ULX3S(TapeSourceSD);
   let m <- mkTapeSourceSD(1, 2048);
   return m;
endmodule
```

`bsc -verilog -g mkTapeSourceSD_ULX3S`: *Verilog file created*, one
remaining warning —

```
(G0010) Rule "m_rl_fill_done" was treated as more urgent than
"m_rl_lookup". Conflicts: m_bankOk0.write vs. m_bankOk0.read,
m_filling.write vs. m_filling.read …
```

— which is the intended ordering (a bank that became valid this cycle
is visible to the lookup next cycle) and is the ordinary
sequential-composition warning, not a bug. `mkConfigReg` on
`bankOk0/1` and `filling` would silence it at the cost of letting the
lookup see the fill's result in the same cycle; I left it noisy and
documented rather than quiet and subtle.

The `(* always_ready *)`/`(* always_enabled *)` on `outEn`/`outAddr`/
`outByte` are load-bearing: `rl_collect` reads them every cycle with
no handshake, which is how `sd_reader` delivers a sector (one byte per
`outen` pulse, address supplied, no back-pressure possible). If the
consumer could ever not be ready, those bytes would be lost — which is
the whole reason the buffer is a BRAM behind the stream and not a FIFO
in front of the Exchange.

---

## 7. Latency, buffering and what the Exchange actually needs

### 7.1 The numbers

| quantity | value | source |
|---|---|---|
| Exchange channel, worst documented byte rate | **one byte every 16 µs** (62.5 kB/s) | Reference Manual p.104, quoted at `docs/exchange_and_io.md:125` |
| 729 IV at 556 bpi ("high density"), average word period | **170 µs/word** = 21.25 µs/byte = **47 kB/s** | Reference Manual p.130, quoted at `docs/exchange_and_io.md:1112` |
| 729 IV at 200 bpi, average word period | 474 µs/word = 59.25 µs/byte | same |
| SD sector | 512 bytes | SD spec; `sd_reader` issues CMD16 with `'h200` |
| `sd_reader` sdclk | ≈ clk / 6 at `CLK_DIV=1` | my reading of `sdcmd_ctrl.v:90-98`: `clkdivr = clkdiv+1 = 3`, sdclk toggles at `clkcnt==clkdivr` and `clkcnt==2*clkdivr`, so a period is ≈ 2·clkdivr clk cycles. **Derived, not measured in simulation.** |
| planned core clock | **3.3333 MHz** | `docs/fpga_feasibility.md` §3.4 |
| board clock | 25 MHz on pin G2 | `ulx3s_v20.lpf:6` |

The caller's working figure of ~10⁵ bytes/s is about 2× the number
this repository's own primary-source citation supports; I used
**16 µs/byte** as the conservative denominator below (it is the
channel's maximum, not the 729's rate), which makes every margin
quoted here a lower bound.

### 7.2 Why one 512-byte sector of buffering is enough, and where it is not

Play time in one buffered sector, at the conservative 16 µs/byte:
**512 × 16 µs = 8.19 ms.** (At the 729 IV's actual 21.25 µs/byte it is
10.9 ms.)

Refill time for one sector, 4096 bits at 1-bit SD:

| reader clock | sdclk (≈clk/6) | 512-byte sector | margin vs 8.19 ms |
|---|---|---|---|
| 25 MHz (board) | 4.17 MHz | **0.98 ms** | **8.3×** |
| 3.3333 MHz (core, §3.4) | 0.56 MHz | **7.37 ms** | **1.11×** |

**This is the one real design constraint the measurement produced: put
`mkTapeSourceSD` in the 25 MHz domain, not the emulated-machine
domain.** At the core clock a sector refill is 90 % of a sector of
play, so any command overhead, any retry, or a slow card eats the
whole margin. At 25 MHz there is 8× headroom. The §3.4 PLL exists
anyway, `mkStretchCore` is single-clock with no CDC primitives in it,
and the crossing is two `SyncFIFOIfc`s on the request and response
sides of the `Server` — which is also exactly where
`docs/fpga_feasibility.md` §3.3 already says the system's only domain
crossing belongs.

With the reader in the fast domain and the bank it is not serving
prefetched, the steady state is: a sector's worth of words served from
BRAM at one clock each while the other bank fills in 0.98 ms, which is
an eighth of the time available. **The response FIFO never runs dry
after the first sector of a sequential pass.**

### 7.3 The stall, which Bluespec gives you for free, and the honest part

The model's tape read is becoming `readResp` instead of a
combinational `readTapeWord(i)`. The *implicit condition on the
response FIFO is the stall*: `StretchCore`'s `ioPending` rule simply
does not fire until the word is there. No state machine, no timeout,
no "wait" counter — the absence of a response is the back-pressure.
That also means `step()`'s `RDY_step` now depends on the tape, which
propagates to `gen_tb.py`'s `rule run` guard; a testbench that polls
`core.step()` unconditionally would stall silently instead of
erroring, so the loader needs a stall counter and a loud failure
(class (b) work, one register and one `$display`).

What buffering cannot fix, and should not be claimed to:

- **The first sector of a block is unhideable.** A READ that starts at
  a sector the buffer does not hold pays ~1 ms before its first word.
- **REWIND and BACKSPACE BLOCK are unhideable** for the same reason:
  they move `tapePos` to somewhere the prefetcher did not predict.
  (They are also *faster* than the real drive, which had to physically
  move tape, so the error is in the forgiving direction.)
- **The real machine would have overlapped all of it.** This model
  "completes an entire block transfer SYNCHRONOUSLY ... with no other
  instruction executing until the transfer drains"
  (`StretchIO.bsv:16-19`), so SD latency appears as extra CPU stall
  that the 7030 would not have had. That is an *Exchange asynchrony*
  problem — the Exchange is "a separate special-purpose, fixed-program
  computer" (`docs/exchange_and_io.md:73`) and modelling it as one is
  explicitly out of scope today. Prefetching makes the steady-state
  stall ~0 words; it does not make the model's I/O concurrent, and no
  amount of buffering will.
- **The 7030's own overrun rule is the thing to model eventually, not
  the SD card's latency.** The manual's word-weight formula
  (`2560/(T-11)`, `docs/exchange_and_io.md:1092`) and "non-buffered
  units (tape) have non-zero weights, and stalling one loses data and
  raises Unit Check" describe a machine where *the tape* cannot wait.
  A faithful model would give the tape a 170 µs word period and raise
  Unit Check when the Exchange misses it. The SD path makes that
  possible for the first time, because there is finally a real device
  with real timing behind the channel.

### 7.4 Measured area, both directions

New, measured — the whole SD path including the imported core, the
shim, the ping-pong buffer and the `Server` FIFOs:

```sh
yosys -s full.ys    # sdcmd_ctrl_split.v sd_reader_shim.v
                    # mkTapeSourceSD_ULX3S.v FIFO2.v BRAM2.v
                    # synth_ecp5 -top mkTapeSourceSD_ULX3S; stat
```

| | LUT4 | TRELLIS_FF | CCU2C | PFUMX | L6MUX21 | DP16KD |
|---|---|---|---|---|---|---|
| **`mkTapeSourceSD_ULX3S`, whole path** | **788** | **720** | **112** | 148 | 15 | **2** |

(With `rl_collect` ungated it was 972 LUT4 / 250 PFUMX / 94 L6MUX21
and the same FF, CCU2C and BRAM count; the `filling` guard of §6.3
both fixes the stale-fill hazard and lets yosys prune 184 LUT4.)

Given back, measured — `mkStretchIO` with the tape `Vector` and its
two accessor methods removed, built and synthesised with the same bsc
and the same yosys script as the baseline so the delta is comparable
(scripts in `scratchpad/iodelta/`):

| `mkStretchIO` | LUT4 | TRELLIS_FF | PFUMX | L6MUX21 |
|---|---|---|---|---|
| as in the repo today | 8,102 | 5,317 | 3,351 | 1,202 |
| with `tapeImg` removed | 7,077 | 4,293 | 3,208 | 1,061 |
| **delta** | **−1,025** | **−1,024** | −143 | −141 |

The baseline reproduces `docs/fpga_feasibility.md` §2.4 exactly
(8,102 / 5,317 / 3,351 / 1,202), which is the check that the two
measurements are on the same footing. The −1,024 flip-flops are
precisely 16 × 64, as predicted.

**Net**: ≈ **−237 LUT4, −304 TRELLIS_FF, +112 CCU2C, +2 DP16KD** —
and both halves of that are *standalone* synthesis numbers, to which
`docs/fpga_feasibility.md` §2.5's caveat applies verbatim ("standalone
synthesis keeps every port of each module live, so the flattened core
could optimise some of it away"). The −1,025 is a solid standalone
delta; that the flattened core gives back the same amount is not
established.
Against the ~41,070 CCU2C reported to me for the whole core (a figure
from another measurement, not reproduced here — the only CCU2C number
I found in the repo is `mkStretchStorage`'s 57 at
`docs/fpga_feasibility.md:285`), +112 is **+0.27 %**, and 2 DP16KD is
0.96 % of an 85F's 208 or 1.85 % of a 45F's 108. The tape data path is
not what decides whether this design fits.

---

## 8. Bounded negatives, and what I could not establish

**Searched and not found** (so these are claims with a search behind
them, not assumptions):

- **No working Bluespec SD core, anywhere on this machine.** Searched
  `~/src` for `sdcard|sd_card|sdspi` and for `spi` across every
  `*.bsv`, and for `ACMD41|acmd41|CMD55` across `*.v *.sv *.bsv *.vhd
  *.py`. The only candidate,
  `~/src/bsoc-cursor/bluespec-ip/src/HighSpeed/SDMMC/`, fails to
  compile in three distinct ways (§2.2). `~/src/alto-bluespec/src/Disk.bsv`
  is Bluespec and is about media, but it is BDPI, not SD.
- **No SD-related anything in `stretch/`.** `docs/fpga_feasibility.md`
  §3.5 had already established there is no `.lpf`, no board top level
  and no `yosys`/`nextpnr` rule in the project; the tape data path is
  new work on top of new work.
- **No ULX3S board manual or schematic on this machine.**
  `find ~/src -maxdepth 6 -iname 'MANUAL.md'` → seven unrelated files;
  `find ~/src -maxdepth 4 -iname '*ulx3s*'` → project directories,
  `.lpf` files, bitstreams, no documentation.

**Could not be established, and is left open rather than guessed:**

1. **ULX3S revisions before v2.0.** The constraints file covers
   "v2.x.x and v3.0.x"; whether v1.x had the socket, and on which
   pins, is unknown here. Anything I could say about it would be
   recollection.
2. **Whether 4-bit SD mode is usable on this board in practice.** The
   pins are there (§1.2) and `sd_d[2]` carries a note about an ESP32
   "pulldown bootstrapping requirement", which suggests the shared
   ESP32 lines have constraints a 4-bit host would have to respect. No
   working 4-bit core was found, and I did not attempt one.
3. **The SPI flash free-region map.** 16,777,216 B total (a full-chip
   dump the user themselves took) and a 1,107,757 B 85F bitstream are
   both measured; "≈15 MB free" is arithmetic, *not* a verified layout.
   Where ULX3S multiboot expects its images, and therefore which
   offsets are safe for a tape image, is not established locally.
   Also: that the 16 MiB file is a *full-chip* dump rather than a
   16 MiB read of a larger chip is an inference from its size.
4. **`sd_reader`'s sdclk rate is derived from the RTL, not simulated.**
   §7.1's `clk/6` comes from reading `sdcmd_ctrl.v:90-98`. The
   conclusion that matters (put the reader in the 25 MHz domain) holds
   under any divider in that neighbourhood, but the exact 0.98 ms
   should be confirmed by running `SIM/tb_sd_file_reader.v` against
   `sd_fake.v`.
5. **`mkTapeSourceSD` is a typechecked design, not a verified
   controller.** It generates Verilog and synthesises to real cells;
   nothing has driven it against a card model. The next step is
   exactly that: `mkTapeSourceSD_ULX3S.v` plus `sd_fake.v` under
   iverilog or verilator, which is why §2.1 counts `sd_fake.v` as part
   of the find. The specific thing that cosim should check first is
   the stale-fill hazard §6.3's `filling` guard exists for: whether
   `sd_reader` ever asserts `outen` outside a fill this module asked
   for (its init sequence, or its own CMD17 retry on `RTIMEOUT`).
6. **`capacity = maxBound` on the SD source disables End Exception,
   and nothing here says where the real number comes from.**
   `StretchIO.bsv:83-88` makes "a count that would run the transfer
   past a device's capacity ends the block early with End Exception
   (EE) + End of Operation (EOP)" an implemented path, and
   `decks/io_tape.strap` tests it. §4.2 says `TapeWords`
   becomes "the drive's idea of where end-of-tape is, which is now
   `src.capacity`" — but `mkTapeSourceSD` returns `maxBound`, because
   a raw LBA has no end marker, so on hardware the model's one "unit
   runs out of material" path becomes unreachable. The two statements
   are in tension and this note does not resolve them. The image's
   word count has to come from somewhere: a header sector ahead of
   `baseLba`, a build-time parameter on `mkTapeSourceSD_ULX3S`, or the
   drive keeping its own `TapeWords` limit and ignoring
   `src.capacity`. Of the three the header sector is the one that
   survives swapping cards, which is the whole point of §3's
   recommendation — but it is unwritten work, and `mkTapeSourceFile`
   does have the real count (`host_tape_words()`), so the Bluesim leg
   and the hardware leg currently differ in exactly this observable.
7. **Write support is absent.** `sd_reader` reads only; a tape WRITE
   to an SD-backed source has nowhere to go. `mkTapeSourceSD` silently
   drops writes today, which is wrong — it should raise Unit Check, or
   the drive should refuse a WRITE when `!writeable`. The interface
   has room for a `writeable` method; adding an SD *writer* is a
   separate core and separate work.
8. **No `nextpnr-ecp5`, so no routed utilisation or timing for any of
   this.** `docs/fpga_feasibility.md` §2.6 records the exact reason
   (a missing `libboost_python38-mt.dylib`). Every area figure here is
   post-`synth_ecp5` cell counts, which is what the rest of that note
   uses too, and no claim is made about whether the SD path meets
   timing at 25 MHz.
9. **The 41,070 CCU2C figure is not mine.** It was given to me as
   context. I report deltas against it without re-deriving it; the
   only CCU2C count I found in the repository is 57, for
   `mkStretchStorage`.
