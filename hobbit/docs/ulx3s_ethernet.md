# Ethernet for the Hobbit on the ULX3S

Step 6 of `docs/ulx3s_plan.md`.  The 1e kernel's network device is a
National DP83932 SONIC (`devether.c`, registers at 0xA4400000, IRQ 9,
`docs/plan9_kernel_inventory.md` §3.9), and `/boot` reaches the file
server by BOOTP, ARP and IL 17008 (`docs/qemu_1e_server.md`, "Transport
for the Hobbit terminal").  The ULX3S has no Ethernet jack.  This
document gives two ways to give it one, sharing one FPGA design:

1. **Now, no hardware to buy:** the on-board ESP32 relays raw frames over
   WiFi to `tools/qemu1e/hub.py`, the hub the QEMU 1e file server already
   sits on.  Firmware: `fpga/esp32_ethrelay/`.  Tested on the host.
2. **Later, wired:** an RMII PHY on the J1 header, with a MAC in the FPGA.
   The PMOD survey and the part to buy are in "PMOD survey" below.

Status, 2026-11-24:

| piece | state | evidence |
|---|---|---|
| link protocol (C, `main/relay.c`) | written, tested on the host | `tests/test_ethrelay.py`, 6 tests, 3 injections (observed failure sets in its header) |
| host relay (`host/relay_host.c`) | written, tested | the same test: against a real `Hub`, and a replay of s9term's whole recorded session |
| `hub.py` ports off localhost | added (`HUB:HOST:PEER`, `HUB:learn`) | `test_learning_port`.  The `(h, p)` form is unchanged |
| ESP-IDF firmware glue (`main/main.c`) | written, **not compiled for the target** | No ESP-IDF is installed here.  The API calls were checked against the ESP-IDF v5.3 documentation, the sdkconfig names against v5.3.2's Kconfig files |
| FPGA link (`esplink`) and SONIC subset (`sonic`) | specified below; no RTL yet | — |
| ESP32 programming | procedure written, **not run** (the board is in use by another session) | — |

## 1. Architecture

```
 Hobbit core ── device bus (12-bit offset) ──┐
                                             │
                   ┌─────────────────────────┴──────┐
 SDRAM arbiter ◄── │ sonic: SONIC-subset engine      │ ── irq (IRQ 9)
  (DMA port)       │  registers, descriptor walker,  │
                   │  CAM/filter, FCS append         │
                   └──────────────┬──────────────────┘
                                  │ frame port (frames, no FCS)
                ┌─────────────────┴───────────────┐
                │                                 │
        esplink (now)                      RMII MAC (later)
  COBS+CRC over UART, 2.5 Mbaud         LAN8720A PHY on J1
                │                                 │
        ESP32 (GPIO16/17)                     copper
                │ WiFi, UDP
        tools/qemu1e/hub.py ── QEMU fs9 (1e file server)
```

The engine talks to the frame port only: whole Ethernet frames,
destination address first, no preamble and no FCS.  That is the hub's
framing and QEMU's dgram netdev framing as well.  So the ESP32 link
and a wired MAC are interchangeable behind it.

## 2. The ESP32 on the ULX3S

### Pins

From emard's `doc/constraints/ulx3s_v20.lpf` (github.com/emard/ulx3s,
fetched 2026-11-24; its own comments quoted in the last column):

| FPGA site | lpf name | ESP32 | strap? | use here |
|---|---|---|---|---|
| F1 | `wifi_en` | EN | — | drive high to run the ESP32 (the current Hobbit bitstream drives it low) |
| L2 | `wifi_gpio0` | GPIO0 | **yes**: low at reset = download mode | drive high, or leave it to its pull-up |
| K3 | `wifi_rxd` | U0RXD (GPIO3) | — | UART0: ESP-IDF console.  The FPGA may ignore it |
| K4 | `wifi_txd` | U0TXD (GPIO1) | — | UART0: ESP-IDF log |
| **L1** | `wifi_gpio16` | GPIO16 | no | **link: FPGA → ESP32** ("Serial1 RX") |
| **N3** | `wifi_gpio17` | GPIO17 | no | **link: ESP32 → FPGA** ("Serial1 TX") |
| H1 | `wifi_gpio4` = `sd_d[1]` | GPIO4 | no | optional RTS (ESP32 → FPGA) |
| N4 | `wifi_gpio5` | GPIO5 (LED) | yes (SDIO timing) | unused.  lpf: "pull down or drive 0 for esp32 programming" |
| J3 | `wifi_gpio2` = `sd_d[0]` | GPIO2 | **yes** | unused.  Do not drive it |
| K1 | `wifi_gpio12` = `sd_d[2]` | GPIO12 (MTDI) | **yes**: high = 1.8 V flash | unused.  No pull-up (the lpf sets PULLMODE=NONE) |
| K2, H2, J1 | `sd_d[3]`, `sd_clk`, `sd_cmd` | GPIO13, 14, 15 | 15 = MTDO (log on/off) | unused |
| F4/E3, G3/F3, H4/G5 | `gp/gn11..13` | GPIO26/25, 33/32, 35/34 | no | **kept for the wired PHY** (section 8).  The firmware leaves them as inputs |

The link uses GPIO16/17 because neither of them is a strap pin.  The
GPIO12-15 group, the ESP32's only IO_MUX SPI pins, is shared with the SD
card and holds three straps.  The Flute session already lost a bring-up
to those straps: `~/src/ulx3s-experiments/flute-lx50/notes/ulx3s-peripherals-plan.md`
(lx44, "ESP32: no reply") blames GPIO2 = `sd_d0` and GPIO15 = `sd_cmd`.
Its lpf notes that this board's efuse forces VDD_SDIO to 3.3 V, so a
high GPIO12 is harmless on that board.  Do not rely on that for other
boards.

**What the relay bitstream drives:** `wifi_en` = 1 (after the FPGA's own
reset), `wifi_gpio0` = 1, L1 = UART TX (idle high).  N3 is an input
(UART RX) with PULLMODE=UP.  Every SD/strap pin is an input with no
pull, except `sd_d[0]` and `sd_d[3]`, which keep their default pull-ups.
GPIO0 is high, so GPIO2's level does not matter.

### Link: UART, not SPI

| | UART2 on GPIO16/17 (chosen) | SPI slave on GPIO12-15 |
|---|---|---|
| bit rate | 2.5 Mbaud: 25 MHz / 10 and 80 MHz APB / 32, both exact.  5 Mbaud (/5, /16) is the ESP32's maximum (`SOC_UART_BITRATE_MAX` 5000000, esp-idf v5.3.2 `soc_caps.h`) | "The SPI slaves are designed to operate at up to 10 MHz" (ESP-IDF SPI slave docs).  From 25 MHz without a PLL: 6.25 MHz |
| payload rate | 250 KB/s (8N1) | 0.78-1.25 MB/s before handshake turnaround |
| pins | 2 (+1 RTS), no straps | 4 + 2 handshake lines.  GPIO12 and 15 are straps |
| ESP32 driver limits | 128-byte HW FIFO, driver rings in RAM | DMA needs SPI modes 1 and 3, lengths a multiple of 4, a re-armed transaction per transfer |
| FPGA logic | a UART and a COBS framer | SPI master, handshake FSM, length negotiation |

Section 4 shows the UART's rate is ample for the IL boot, so the
simpler, strap-free link wins.  SPI is the upgrade path if a later
workload needs it.

## 3. The link protocol

`fpga/esp32_ethrelay/main/relay.h` defines the protocol:

    COBS( type[1] | payload[n] | crc32[4] little-endian ) 0x00

* COBS (Cheshire and Baker 1999) leaves no 0x00 in the body, so 0x00
  delimits packets.  After an error the receiver resynchronises at the
  next 0x00.  Overhead: one code byte per 254 body bytes, plus the
  delimiter.  A 1514-byte frame is 1526 link bytes; 1518 is 1530.
* The CRC is the Ethernet FCS's (reflected 0xEDB88320, init and final
  xor all ones), computed over the type and the payload.  The FPGA can
  share it with the FCS that the SONIC engine appends on receive.
* `type` 0x45 'E' is an Ethernet frame, 14..1518 bytes, exactly the
  hub's datagram.  0x53 'S' is a status text from the ESP32 ("ethrelay:
  wifi connecting", "ethrelay: up"), which the FPGA may drop.  Any
  other type is counted and dropped.
* A packet with a bad CRC, broken COBS, a runt or oversize length, or
  an unknown type is dropped and counted.  Line noise with no 0x00 of
  its own merges into the packet after it, so that one packet is lost
  as well (`test_bad_packets_dropped` pins this behaviour).
* Flow control: the FPGA side must always accept a whole packet (a
  2 KB buffer).  Towards the ESP32 the UART driver's RX ring buffers the
  data.  RTS on GPIO4/H1 is optional (`CONFIG_RELAY_UART_RTS_GPIO`).

## 4. Throughput, and whether IL boots at this rate

Measured on the host relay: `test_session_replay` replays all 1108
frames of s9term's recorded session (`tests/net/a5_session.pcap`, from
/boot's BOOTP request through `echo hello`'s output, 27.7 s of model
time).  The relay paces the link at 2.5 Mbaud, and each run of frames
in one direction is sent as one burst.  Every frame arrived intact and
in order, with none dropped and at most 6 queued.  The replay took
**1.7-1.8 s against a 1.51 s link model** (377,045 link bytes × 10 /
2.5e6).  The rest is the turnaround of 942 direction changes.

The link model, for the same session (`packet()` in the test):

| direction | frames | frame bytes | link bytes | 1 Mbaud | 2.5 Mbaud | 5 Mbaud |
|---|---|---|---|---|---|---|
| Hobbit → server | 486 | 36,251 | 39,653 | 0.40 s | 0.16 s | 0.08 s |
| server → Hobbit | 622 | 332,985 | 337,392 | 3.37 s | 1.35 s | 0.67 s |

At 2.5 Mbaud the link is busy for 1.5 s of a 27.7 s session, about
5%.  The session spends its time in the model's execution, not on the
wire.

**IL's timers** (`sys/src/9/port/stil.c` in the release):
`Iltickms = 100`, `Fasttime = 4*Iltickms`, and `Starttimer` scales the
timeouts by the smoothed RTT, which is never below `Iltickms`.  So IL
retransmits after **400 ms at the earliest**, and hangs up after
`Slowtime` = 20 s × rtt/100 ms.  The window is `Defaultwin = 20`
messages.

* The largest burst in the session is 6 frames, 7,680 bytes (one 8 KB
  9P Rread fragmented by IP).  It drains in **30.9 ms at 2.5 Mbaud**
  (15.4 ms at 5).  A full-size frame takes 6.1 ms.  Both are far
  inside 400 ms.
* WiFi adds a few ms of round trip.  Modem sleep would add up to a
  beacon interval (about 100 ms) to every inbound frame, so the
  firmware turns power save off (`esp_wifi_set_ps(WIFI_PS_NONE)`).
* A lost frame costs IL at least 400 ms and no more.  A lost BOOTP
  reply is retried every second, 10 times (`boot/ip.c`, `alarm(1000)`
  in a `tries++ < 10` loop), and then `/boot` asks for an IP address by
  hand.  A lost ARP reply is re-asked every second for ever (`boot/ip.c`
  `arp`).

**Conclusion:** at 2.5 Mbaud the IL boot is limited by the core, not by
the link.  A worst-case IL window of 20 full 8 KB messages, 160 KB, would
drain in 0.65 s and could trigger one retransmission at 400 ms.  It is
not seen in the recording, because 9P under `/boot` has one request
outstanding.  Raise the rate to 5 Mbaud (Kconfig `RELAY_UART_BAUD`, and
the FPGA divider 5) if that becomes a problem.

**WiFi MTU.** The hub's datagram is the whole frame, so a 1514-byte
frame is a 1542-byte IP datagram.  That exceeds WiFi's 1500-byte MTU,
so the datagram is fragmented in both directions.  ESP-IDF leaves
reassembly off by default (`CONFIG_LWIP_IP4_REASSEMBLY` default n).
`sdkconfig.defaults` turns it on and raises the limits a 6-frame burst
needs:

* `LWIP_IP_REASS_MAX_PBUFS` from 10 to 40
* `LWIP_UDP_RECVMBOX_SIZE` from 6 to 32
* the WiFi RX buffers to 16 static and 64 dynamic

The names, defaults and ranges were checked against esp-idf v5.3.2
`components/lwip/Kconfig` and `components/esp_wifi/Kconfig`.

## 5. Firmware: `fpga/esp32_ethrelay/`

| file | role |
|---|---|
| `main/relay.h`, `main/relay.c` | the link protocol, portable C (also built on the host) |
| `main/main.c` | ESP-IDF v5.3 glue: WiFi STA with power save off, UART2 driver, a UDP socket, two tasks (`link_rx`: UART → frames → `sendto`; `net_rx`: `recv` → packets → `uart_write_bytes`) |
| `main/Kconfig.projbuild` | menu "Ethernet relay": SSID, password, hub host/port, local port, baud, pins, ring sizes |
| `sdkconfig.defaults` | the lwIP/WiFi settings above |
| `host/relay_host.c` | the relay on POSIX, for the test |
| `.gitignore` | `build/`, and `sdkconfig`, which will hold the WiFi password |

Build (ESP-IDF v5.3, not yet done):

```sh
cd hobbit/fpga/esp32_ethrelay
idf.py set-target esp32
idf.py menuconfig        # Ethernet relay: SSID, password, hub host = this host's LAN address
idf.py build
```

The host side: the file server stays on the hub's loopback port, and the
board gets a learning port reachable from the LAN:

```sh
python3 hobbit/tools/qemu1e/hub.py 10902:10901 10911:learn
```

`HUB:learn` binds 0.0.0.0 and sends to whichever address last sent to
it, so the ESP32's DHCP address need not be known.  The ESP32 must send
first.  The Hobbit's first frame is its BOOTP request, so it does.  The
host firewall must let UDP 10911 in.  The `hobbit` entry in
`tools/qemu1e/ndb.local` holds the MAC that the ESP32 path must carry:
`ether=525400000b0b`, read by the kernel from the IIC EEPROM.  The
relay does not touch addresses.

Test on the host: `python3 hobbit/tests/test_ethrelay.py` (also run by
`tests/run_tests.sh`).  See the test's docstring for what each check is
evidence of, and for the injected bugs it catches.

## 6. FPGA side: `sonic` and `esplink` (specification)

Paths for the RTL when it is written: `fpga/dev/sonic*`, `fpga/dev/esplink*`.
Provenance goes in `fpga/IP_PROVENANCE.md`.  Both modules are BSV,
per the plan's device bus contract.

### 6.1 Register port (the plan's device bus contract)

```bsv
interface DevPort;                                   // in the device
  method Action req(Bit#(12) addr, Bit#(32) wdata, Bit#(4) be, Bool write);
  method ActionValue#(Bit#(32)) resp;                // one per req, any latency
  method Bool irq;                                   // level
endinterface
```

The SONIC's registers are 16-bit values at word offsets (io.h `Sonic`:
register *i* at byte offset 4*i*, 0x00 `cr` to 0xFC `dcr2`).  Reads
return the value zero-extended.  Writes take `wdata[15:0]` when `be[1:0]`
is not 0.  `irq = (isr & imr) != 0`, wired to IRQ 9 (`IRQSONIC`).

### 6.2 The subset, from `tools/p9boot.py` `Sonic` / `SONIC_CHOICES`

The Python model boots the shipped kernel to rc and runs A5's whole
command script.  The RTL implements exactly what it implements, and
stops loud (an error flag and a status bit) wherever the model raises
`Stop`.

* Registers kept: cr, dcr, rcr, tcr, imr, isr, utda, ctda, urda, crda,
  eobc, urra, rsa, rea, rrp, rwp, cep, cap2-0, ce, cdp, cdc, sr, rsc,
  mpt.  Every other offset is plain storage: it reads back what was
  written.
* Reset: `cr = Rst|Stp|Rxdis`.  Writing cr with Rst clear while in reset
  only leaves reset.
* `isr` is write-one-to-clear.  rsa, rea, rrp and rwp drop bits 1:0.
* Commands, done as DMA sequences, with cr's bit cleared at the end:
  **Rrra** (read a 4-word resource at urra:rrp, advance rrp by 16, wrap
  rea → rsa), **Lcam** (cdc entries of cep, cap0-2 from urra:cdp, then
  the CE word; isr Lcd), **Txp** (walk utda:ctda descriptors: size,
  fragment count, per fragment ptr0/ptr1/size, link; send each frame on
  the frame port; status word = 0x0001; ctda = link; stop at EOL; isr
  Txdn).  Rxen, Rxdis, Stp, St and Htx only set or clear bits.  Any other
  command bit stops.
* Receive: filter (rcr Pro: any unicast; Brd: broadcast; an enabled
  CAM match).  Write the frame **plus its CRC-32 FCS**, padded to 4 bytes
  with 0xFF, at crba.  Fill the descriptor at urda:crda: status
  Prx(|Bc)(|Lpkt when fewer than eobc words remain), byte count = frame
  + 4, buffer pointer, rsc.  Handle the link and EOL exactly as in
  `Sonic.receive` (Rde, mpt, in_use = 0, Pktrx).  Lpkt runs Rrra.  A
  frame with no descriptor is dropped and mpt is incremented.
* Descriptor words are 32-bit, holding 16-bit values zero-extended
  (dcr Dw32).  Packet bytes go in address order, in little-endian lanes
  (CONFIG.KL).

### 6.3 DMA master port (to the SoC's SDRAM arbiter)

The engine masters memory for descriptors and buffers.  The SoC agent
owns the arbiter, so the contract is fixed here:

```bsv
typedef struct {
  Bit#(32) addr;      // physical byte address, bits 1:0 = 0 (word aligned)
  Bool     write;
  Bit#(32) wdata;     // little-endian lanes: byte at addr+i in wdata[8i+7:8i]
  Bit#(4)  be;        // byte enables, writes only
} SonicDmaReq deriving (Bits, Eq, FShow);

interface SonicDma;                    // the engine's side
  interface Get#(SonicDmaReq) req;     // the arbiter takes requests when it can
  interface Put#(Bit#(32))    rdata;   // one per READ, in request order
endinterface
```

* One 32-bit word per request.  The arbiter may stall either side for
  any number of cycles, and the engine has at most 4 reads outstanding.
* Writes are posted (no response).  The arbiter keeps this port's
  requests in order: a read after a write to the same word returns the
  written data.  A write must reach memory before the engine raises
  the isr bit that tells the kernel about it: the engine issues the
  isr update only after its last write has been *accepted*, and the
  arbiter guarantees that accepted writes are visible to the core's
  later reads.  That is the one ordering rule the core's bus must also
  honour.
* Addresses are physical.  The kernel's PADDR is the identity
  (`SONIC_CHOICES['dma']`), and RAM is at 0x80000000 (`ulx3s_plan.md`
  memory map).  An address outside RAM sets an error bit and stops the
  engine; it never wraps.
* The bandwidth needed is small: a 10 Mb/s-class stream is about
  1.25 MB/s, about 320 k words/s plus descriptors.  Bursts are not
  needed.  A later `len` field can add them without changing the
  single-word case.
* Receive writes whole words (the engine assembles them; the padding to
  4 bytes makes the last word whole).  Transmit fragments may start on
  any byte: the engine reads words and extracts the bytes.

### 6.4 Frame port (engine ↔ link or MAC)

```bsv
typedef struct { Bit#(8) data; Bool last; Bool bad; } FrameByte deriving (Bits);

interface FramePort;                   // the link/MAC side
  interface Get#(FrameByte) rx;        // frames to the engine; `bad` is meaningful on `last`
  interface Put#(FrameByte) tx;        // frames from the engine; `bad` ignored
endinterface
```

The bytes are the frame from its destination address, with no FCS.  An
RX frame whose `last` byte carries `bad` (a link CRC error, or an RMII
FCS error) is discarded by the engine, and nothing is committed to
memory or descriptors.  The engine writes into the buffer as bytes
arrive, and advances crba and the descriptor only on a good `last`.

### 6.5 `esplink`

`mkEspLink#(Integer clksPerBit)` provides a `FramePort` and the two pins
(`txd` to L1, `rxd` from N3).  It is an 8N1 UART (16x oversampled RX, or
a mid-bit sample at 10 clocks a bit), plus:

* TX: CRC-32 over 0x45 and the frame, then a streaming COBS encoder,
  which needs a 254-byte look-ahead buffer (one EBR block), then the
  0x00 delimiter.
* RX: a streaming COBS decoder, a 4-byte delay line so the trailing CRC
  is not passed on, and a CRC check at the 0x00 that sets `bad` on
  `last`.  The first body byte is the type.  A non-0x45 packet is
  swallowed.
* Counters readable for debugging: good, bad_crc, bad_cobs, overflow
  (the same as `relay_dec`).

Its test: Bluesim or Verilator runs the Python reference codec's
vectors from `tests/test_ethrelay.py` (`packet()`) through the RTL in
both directions, including the bad-packet stream of
`test_bad_packets_dropped`, and compares byte for byte.

## 7. Programming the ESP32 (procedure, not run)

**Not done.**  The board is in use by another session.  Nothing here
runs `openFPGALoader`, `esptool` or `fujprog`, or opens a
`/dev/cu.usbserial*` port.  When the owner grants a hardware window:

1. Load emard's passthru bitstream into the FPGA's SRAM, not flash:
   `fpga/passthru/passthru-v20-85f/ulx3s_85f_passthru.bit` from
   github.com/emard/ulx3s-bin.
   `openFPGALoader -b ulx3s ulx3s_85f_passthru.bit`.
   The passthru (`rtl/ulx3s_v20_passthru_wifi.vhd` in
   github.com/emard/ulx3s-passthru) wires FTDI TXD/RXD to the ESP32's
   UART0.  It maps (nDTR, nRTS) to (EN, GPIO0) the way esptool's
   auto-reset expects:

   | DTR | RTS | EN | IO0 |
   |---|---|---|---|
   | 1 | 1 | 1 | 1 |
   | 0 | 0 | 1 | 1 |
   | 1 | 0 | 0 | 1 |
   | 0 | 1 | 1 | 0 |

   It also drives GPIO2 (`sd_d(0)`) low for a short time after release,
   so the ROM enters download mode.  Holding BTN0 holds GPIO0 low.
2. `idf.py -p /dev/cu.usbserial-<the board's FTDI> flash monitor`.
   That is esptool through the FTDI.  The monitor should print
   "ethrelay: got ip ...".
3. Load the Hobbit relay bitstream again (`openFPGALoader -b ulx3s -r`
   afterwards, as `ulx3s_plan.md` "Hardware windows" requires).

A later bitstream can contain the passthru itself: FTDI DTR/RTS to
EN/GPIO0 while a DIP switch is set.  Then reflashing the ESP32 needs no
bitstream swap.

## 8. PMOD survey: which Ethernet add-on to buy

Sources fetched 2026-11-24.  Header geometry is from emard's `gpio.sch`
and `ulx3s_v20.lpf`.  The manual (`doc/MANUAL.md`) says "4 PMOD
connectors can be made out of it (GND and 3.3V power are on the right
place)".

**PMOD-ordered positions on J1/J2** (four signal rows, then GND and 3V3):

| group | clock-capable pins | taken by |
|---|---|---|
| J1 gp/gn0-3 | gp0, gn0, gp1, gn1 PCLK; gp2/gn2 GR_PCLK | nothing in the Hobbit design (Flute uses 0-1 for JTAG, which does not matter here) |
| J1 gp/gn7-10 | none | free.  Shares row 10 with the next group |
| J1 gp/gn10-13 | gp12/gn12 PCLK; the lpf has `FREQUENCY PORT "gn[12]" 50 MHZ` | the ESP32's GPIO25/26/32-35 (inputs after reset) |
| J2 gp/gn14-17 | gp17 GR_PCLK | the on-board ADC |
| J2 gp/gn21-24 | none | free |
| J2 gp/gn24-27 | — | **5 V in the VCC position: not PMOD-safe** |

**Candidates:**

| part | chip, interface | fits | raw frames | MAC needed | price, stock (2026-11-24) |
|---|---|---|---|---|---|
| **Machdyne Katze** | Microchip LAN8720A, RMII | one PMOD (8 signals; MDIO only on test pads) | all (the MAC is ours) | RMII MAC in the FPGA | €24.95, backorder (machdyne.com) |
| generic / Waveshare LAN8720 "ETH board" | LAN8720A, RMII | 2x7 header, **not a PMOD**: emard's recipe puts it on J1 gp/gn9-13 | all | RMII MAC | about $9, widely stocked (search listing, not fetched) |
| Machdyne Wildkatze | RTL8201F, RMII | one PMOD | all | RMII MAC, and an external 25/50 MHz clock | price not shown |
| Digilent PmodNIC100 | ENC424J600, SPI (14 MHz max) | one PMOD | yes: promiscuous mode, datasheet §10.12 (CRCEN, RUNTEN, UCEN, NOTMEEN, MCEN) | none | **obsolete** (DigiKey; RS out of stock: search listings) |
| WIZnet WIZ850io / Machdyne Hauskatze | W5500, SPI (33.3 MHz guaranteed, 80 MHz "theoretical") | Hauskatze: one PMOD; WIZ850io: wiring needed | MACRAW: **socket 0 only**, up to 16 KB of buffer; Sn_MR MFEN = 0 receives all frames (datasheet v1.1.0).  FCS handling unverified | none | WIZ850io about $20 at Mouser (search listing); Hauskatze €24.95 |
| Machdyne Langkatze | ENC28J60, SPI | one PMOD | yes | none | 10 Mb/s only; €24.95 |
| RTL8211 RGMII PMOD | — | needs two PMODs and a clock-capable RX clock | — | RGMII MAC | none found |

**Open MACs** (licence from each repo's LICENSE file):

* **LiteEth** (enjoy-digital): **BSD-2-Clause**, active.  Has an RMII PHY
  (`phy/parallel/rmii.py`: SDR I/O, takes the reference clock from the
  pad or generates it) and an ECP5 RGMII PHY.  It is Migen/LiteX, so it
  is generated to Verilog and is a reference rather than a drop-in core.
* **alexforencich/verilog-ethernet**: MIT, but its README says it is
  superseded by fpganinja/taxi and deprecated.  It has MII, GMII and
  RGMII and **no RMII**, and its DDR primitives have no ECP5 target.
* **fpganinja/taxi**: **CERN-OHL-S-2.0** (strongly reciprocal) or
  commercial.  Not suitable for copying into this public repo under
  other terms.

**Recommendation: the Machdyne Katze (LAN8720A RMII PMOD) on J1 gp/gn0-3.**

* RMII gives raw frames with no chip-side filter, MACRAW socket limit or
  SPI bottleneck.  The W5500 and ENC parts make the SPI bus the
  bottleneck, and the PmodNIC100 is obsolete.
* RMII at 100 Mb/s is 2 bits at 50 MHz.  The MAC is small: preamble/SFD,
  FCS, inter-frame gap, and the LAN8720's 10/100 rate selection.  It
  should be written in BSV behind the same frame port, with LiteEth's
  `rmii.py` (BSD-2) as the reading reference, cited in
  `fpga/IP_PROVENANCE.md`.  No copying is needed.
* On J1 gp/gn0-3 the module's CLK50 (PMOD pin 10) lands on a primary
  clock pin.  Pins 4 and 10 are the row next to GND, which is gp0/gn0,
  and **both** are PCLK.
* It is the only Ethernet PMOD found that is a real PMOD with the PHY's
  own 50 MHz clock.  The Wildkatze needs an external clock.
* **If the Katze stays on backorder,** buy the generic LAN8720 module
  instead.  It has the same PHY, so the MAC is the same and only the lpf
  changes.  Its pins are emard's
  (`ulx3s-misc/examples/eth/rmii/proj/top/top_eth_hex_demo.v`):
  tx_en gn10, tx0 gp10, tx1 gn9, crs_dv gp12, rx0 gn11, rx1 gp11,
  50 MHz clock gn12 (the lpf's 50 MHz port), mdio gn13, mdc gp13.  That
  sits on the ESP32's GPIO25/26/32-35, which the relay firmware never
  configures (they stay inputs).  The ULX3S issue #14 warns that the
  module dies on 5 V: connect GND and 3V3 first.

**Katze pin plan on J1 gp/gn0-3:** Katze pinout from its README: 1
TXD0, 2 TXD1, 3 TXEN, 4 CRS_DV, 5 GND, 6 3V3, 7 RXD0, 8 RXD1, 9 RST_N,
10 CLK50, 11 GND, 12 3V3.

| PMOD row | pins | J1 pair | FPGA sites (gp / gn) |
|---|---|---|---|
| next to GND/3V3 | 4 CRS_DV, 10 CLK50 | gp0/gn0 | B11 / C11, both PCLK |
| | 3 TXEN, 9 RST_N | gp1/gn1 | A10 / A11 |
| | 2 TXD1, 8 RXD1 | gp2/gn2 | A9 / B10 |
| outer | 1 TXD0, 7 RXD0 | gp3/gn3 | B9 / C10 |

Which column (gp or gn) carries pins 1-4 depends on which face of the
header the angled PMOD socket is on.  The lpf says "FEMALE ANGLED (90
deg PMOD) on TOP or MALE VERTICAL (0 deg pins) on BOTTOM", and the
mapping is unverified: check it against the schematic before writing
the lpf.  Either way CLK50 is on a PCLK pin.  Constraints: LVCMOS33,
`FREQUENCY PORT <clk50> 50 MHZ`, PULLMODE=UP on CRS_DV and RXD0/1 (as
Katze's LiteX platform file does).

Not checked: whether the J1 rail labelled `2V5_3V3` is 3.3 V on this
board revision (the manual says 3.3 V; check with a meter before
plugging in).  Also, MDIO is not on the Katze's PMOD pins, so the PHY
runs on its strap defaults (autonegotiation on).
