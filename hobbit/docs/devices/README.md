# The Hobbit board's devices against their data sheets

`docs/p9boot.md` ("Modelling choices") and the `*_CHOICES` tables in
`tools/p9boot.py` record how the reference model's devices behave.  The
release ships no data sheets, so many of those choices were inferences from
the drivers or borrowed from QEMU.  This file checks each choice against the
vendors' own documents, listed in `MANIFEST.md`.  The PDFs are on disk here
but not in git; `sh fetch.sh` gets them.

Citations: book page "p." and file page "PDF p." (`MANIFEST.md` gives each
book's offset).  The model was read at `tools/p9boot.py` as of commit
4b71d5cd (2026-11-24).  This document changes no code.  The contradictions
below are for whoever next edits `p9boot.py`.

Verdicts:
- **confirms**: the sheet says what the model does.
- **refines**: the model is right for what the driver does, but the sheet adds
  a detail, a timing, or a source in place of "(QEMU)".
- **contradicts**: the part does something else.
- **unsettled**: the sheets point both ways.

## Summary of contradictions

1. **Quart FIFO depth is 8, not 3.** The receive and transmit FIFOs each hold
   eight characters, and FFULL means all eight are full.  The model's
   `RX_FIFO = 3` and `sr` FFULL "at three" are wrong (`sr`, `rx`).
2. **Quart interrupt priority is a numeric bid, and the model's order is
   backwards.**  With the bidding registers at their reset value (the shipped
   `deveia.c` never writes `bcr`), the counter/timer has the *lowest*
   priority.  An empty transmitter outranks a receiver holding 1 to 3 bytes;
   a receiver holding 4 or more outranks everything.  The model has counter >
   receiver > transmitter (`cir`).
3. **Quart transmit interrupt values.** An empty transmitter reports type
   x10 with its free-byte count in CIR bits 6:4.  That is CIR 0x78|ch, read
   by `eiaintr` as `TxAvail1` (0x18), and GIBC is the free count (7).  The
   model reports CIR 0x08 and `gibcr` = 1, so the driver writes one byte per
   interrupt where the part lets it write up to seven (`cir`).
4. **Quart counter channel code.** The counter of DUART ab reports channel b
   (01), and the counter of cd reports channel d (11).  The model gives
   `gicr` = 2·duart (0 or 2) and CIR 0x14.  The part gives 0x15 or 0x17
   (`cir`; harmless to `eiaintr`, which masks the type and uses the channel's
   DUART).
5. **SONIC receive status includes the RCR configuration bits.** The status
   word is loaded from the Receive Control Register, so bits 15:9 (ERR, RNT,
   BRD, PRO, AMC, LB1, LB0) are copied in.  The model writes only
   PRX|BC|LPKT.  `devether.c` tests only Prx/Fae/Crc, so this is harmless
   (`receive`).
6. **SONIC CDP after Load CAM** points past the CAM Enable word, not at it
   (`cam`; harmless).
7. **IIC repeated START: unsettled, probably wrong.**  By the PCF8584 sheet,
   the 0xA5 that `eepromread` writes to S0 before setting STA goes out at once
   as a data byte.  The EEPROM then advances its word address to 1, and the
   following read starts at EEPROM byte 1, not 0.  The model keeps the
   pointer at 0 (`repeated-start`).  See the IIC section for why this is not
   settled.
8. Timing the model compresses to zero, which the sheets now give:
   - the WD33C93A's selection timeout arrives after the programmed 200 ms;
   - a Quart transmitter needs one character time per byte.

`docs/p9boot.md` also says the bidding registers "are written by eiasetup".
The shipped `deveia.c` `eiasetup` writes only `ack` and `icr`.  s9term's
older `eiasetup` was not checked.

## The board

**Finding: a Hobbit board that Bell Labs built itself.** It is not the EO
communicator, not an AT&T Microelectronics development board, and not the
BeBox prototype.  No manual, schematic or board name survives.

Evidence:

- **Primary (1st edition, verified 2026-11-24).** Rob Pike, "The Various
  Ports", *Plan 9 Programmer's Manual* 1st ed. vol. 2, on the Hobbit
  operating system: "This system runs only on a home-built board, so it's
  probably not of much interest."  On the compiler: "You probably don't have
  a Hobbit, but we're including the compiler because the chip may grow to
  have a wider audience …"
  - Source: <https://plan9.io/sources/contrib/steve/historic/1st-edition/volume2/01port.ps>,
    36,332 bytes, sha256
    `5f018893c79c01b70d93fc1f3f2e67cf2da253e4284918fb739c5f7086112b6a`.
- **Primary (1st edition, verified).** booting(8), 1st edition, has a Hobbit
  entry: "The ROM uses some variables in non-volatile RAM for booting …
  'e -i'", and "Currently, Hobbit boards boot only using incon."  Its example
  is `e bootfile /sys/src/9/hobbit/9cpub -- incon!nj/astro/Nfs`.
  - Source: <https://typewritten.org/Manual/Bell/Plan9/1ed/man8/booting.html>.
  - The NVRAM variables are the MK48T02's RAM; `incon` is IRQ 5 in `io.h`.
- **Secondhand, from Bell Labs' Plan 9 group** (Jim McKie on 9fans):
  - 2005-07-22: "The firmware we used in the Hobbit boards we built a few
    years ago was a Plan 9 Hobbit kernel with a different address mapping …"
    (<https://inbox.vuxu.org/9fans/e52f84653f54086c30082f91ab0673d5@plan9.bell-labs.com/>).
  - 2006-01-31: "when I did the boot ROM for the Hobbit boards …"
    (<https://inbox.vuxu.org/9fans/5e571fa65ee3c57240eec513554d9eba@plan9.bell-labs.com/>).
  - 2001-05-23: he refers to "the western-digital one used in the hobbit
    board", which matches the WD33C93A
    (<https://inbox.vuxu.org/9fans/20010523130248.21311199C0@mail.cse.psu.edu/>).
- **Ruled out by the device mix.** The kernel drives discrete parts: an
  SC68C94, an MK48T02, its own interrupt registers at IONAK+0x80, a SONIC, a
  WD33C93A and a PCF8584.  It drives none of the AT&T 9201x companion chips.
  - **EO 440/880.** Microprocessor Report vol. 6 no. 15 (18 Nov 1992,
    <https://www.cecs.uci.edu/~papers/mpr/MPR/ARTICLES/061509.pdf>) says EO
    uses the whole Hobbit chip set except the ISA bridge, i.e. the 92011,
    which carries its own UART, RTC, interrupt controller and DRAM
    controller.
  - **AT&T development boards.** The ones MPR describes (vol. 6 no. 14,
    28 Oct 1992, <https://www.cecs.uci.edu/~papers/mpr/MPR/ARTICLES/061403.pdf>)
    are an ISA-bus board with standard ISA peripherals and a board with the
    full chip set.
  - **BeBox Hobbit prototype.** It had RAM at 0x08000000 and AT/PS/2
    keyboard and mouse (<https://mail.typewritten.org/Projects/Be/9308000058.html>).
    This board has RAM at 0x80000000 and a 600-baud serial keyboard.
  - These are inferences from the articles against `io.h`, not statements in
    them.
- **The name "Bart's LCD"** (`io.h`) and the `bart` kernel configuration
  suggest Bart Locanthi, who designed the Blit and the Gnot at Bell Labs.
  No source ties him to this board; this is a guess from the name.
- **The companion chips.** The best surviving description of the 9201x
  companion chips is MPR 061403 (above).  Their December 1992 data sheets
  are cited on a BeBox history page but were not found online.  They would
  not describe this board.

## Quart: Signetics/Philips SC68C94 (`QUART_CHOICES`, `deveia.c`)

`io.h` calls the part "Signetics 68C94".  The 68C94 is the 68000-bus member
of the SC26C94/SC68C94 QUART pair: four UARTs in two DUART blocks, plus the
bidding interrupt system and the global registers at 0x20..0x2F.  The
register offsets in `io.h` (word index = A5:0) match the data sheet's
Table 1.

Two editions are on disk, and they differ:

| Point | 1990 preliminary (IC19) | 1994 product spec | Which the kernel follows |
|---|---|---|---|
| 0x2D..0x2F (writes) | Test 3; Set X1/CLK normal; ÷2 (p. 225, PDF p. 232) | BRG Rate; Set X1/CLK ÷2; Set X1/CLK normal (p. 306, PDF p. 307) | 1994: `io.h` has `brg` at 0x2D, `setclk[2]` at 0x2E..0x2F |
| FIFO byte counts (bids, GIBC) | count − 1 (p. 227, 229, PDF p. 234, 236) | the actual count; 8 is coded as 7 (p. 309, PDF p. 310) | 1994: `eiaintr` reads `gibcr & 7` bytes and loops until CIR type 0. With count − 1, a single received byte would give GIBC 0, nothing would be read, and the loop would never end |
| ICR threshold at reset | 3Fh (p. 236, PDF p. 243) | 00 (p. 321, PDF p. 322) | moot: `eiasetup` writes `icr = 0` |
| BCR resets | break 001, change of state 00 (p. 237, PDF p. 244) | break 000, change of state 00, C/T 00 (p. 322, PDF p. 323) | the shipped driver never writes `bcr` |

The table below uses the 1994 edition unless it says otherwise.

| Choice | The data sheet | Verdict |
|---|---|---|
| `sr`: TxRDY\|TxEMT while enabled; RxRDY with a byte; FFULL "at three" | Receive and transmit FIFOs are 8 deep ("8-byte Receive FIFOs and 8-byte Transmit FIFOs", 1990 p. 226, PDF p. 233). SR[1] FFULL is set when "all eight FIFO positions are occupied"; SR[2] TxRDY is cleared "when the TxFIFO is full (eight bytes)" (p. 317, PDF p. 318). | **contradicts** (depth 8). TxRDY/TxEMT with instant transmission is otherwise consistent |
| `rx`: three-byte FIFO; a byte that finds it full waits on the line (no overrun) | 8 deep (above). A character that finds the FIFO full waits in the shift register; a further character overruns: the shift register is lost and SR[4] is set (1990 p. 227, PDF p. 234) | **contradicts** (depth); the waiting is **refined** (one more char waits in the shift register, then overrun) |
| `cr`: enables, MrReset (mr pointer to MR1), RxReset, TxReset act; the rest ignored | CR[7:4] commands: 1 reset MR pointer (to MR1), 2 reset receiver, 3 reset transmitter, 4 reset error status, … B set MR pointer to MR0 (p. 316, PDF p. 317). The part has MR0 (watchdog, FIFO interrupt levels), reachable only through command B, which `deveia.c` never issues | **confirms**; refines: MR0 exists and stays 0 |
| `isr`: TxRDYa/b while enabled; CtrRDY until `stop` is read; RxRDYa/b with data | ISR bits 0 TxRDYa, 1 RxRDYa, 3 counter ready, 4 TxRDYb, 5 RxRDYb (p. 318..319, PDF p. 319..320). TxRDY in ISR means the free count reaches MR0[5:4]'s level, which at reset (00) is **8 bytes empty** (p. 312, PDF p. 313). In timer mode ISR[3] "is reset by a stop counter command. The command, however, does not stop the C/T" (p. 319, PDF p. 320) | **confirms** (with the FIFO always empty, as the model transmits at once) |
| `counter`: started by reading `start`; CtrRDY every 2·count/(3.6864 MHz/16) | ACR[6:4] = 111: timer, clock X1/CLK ÷ 16 (Table 4, p. 318, PDF p. 319); `deveia.c` writes acr = 0xF0 = BRGSet2\|TimerD16. The square wave's frequency is the C/T clock "divided by twice the value of the CTUR CTLR", and ISR[3] is set once per cycle of the square wave (1990 p. 226, PDF p. 233; 1994 p. 319, PDF p. 320) | **confirms** |
| `counter-period`: s9term's count 0xFFFF gives 0.569 s; its HZ is 25 | The formula stands. The only clock knobs are the X1/CLK ÷2 command (0x2E in the 1994 map) and the BRG rate register (0x2D). Both are unused by the drivers, and ÷2 would make the clock slower, not faster. With acr 0xF0 no setting of this part turns 65535 into 25 Hz. The undivided-X1 timer mode (acr 0xE0) would give 28 Hz, but s9term writes 0xF0 | **refines**: the data sheet supports "the kernel's clock ran slow (or the count was not the shipped one)". It cannot mean the part ran at 25 Hz with that count |
| `cir`: update latches counter, then receiver, then transmitter; CIR 0x14/0x0C/0x08; gicr = 2·duart for the counter; tx gibcr = 1 | CIR = [#bytes 7:5][type 4:2][channel 1:0]. Types: 000 none, 001 change of state, x10 transmit, 011 receive, 100 break, 101 C/T, 111 receive with error (p. 321, PDF p. 322). The winning bid is the numerically largest (Table 1 *Bidding Format*, article reprint p. 333, PDF p. 334, read from the page image). Bid formats: receiver = [count 7:5][error][1][1][ch]; transmitter = [0][free count 6:4][1][0][ch]; C/T = [BCR 2 bits 7:6][0][1][0][1][ch]. "The channel address for C/T ab will be encoded as channel b (01) … C/T cd … channel d (11)" (p. 311, 321; PDF p. 312, 322). With BCR = 0: C/T bid 0x15/0x17; receiver with n bytes 0x2C..0xEC (n<<5 \| 0x0C \| ch); empty transmitter 0x78 \| ch. So rx (n ≥ 4) > tx-empty > rx (n = 1..3) > counter. The reprint: "the receivers are biased to have highest priority … A counter/timer that has not timed out will not bid" | **contradicts**: order, the counter's channel (b/d, not a/c), the transmit CIR (0x78\|ch, type 0x18) and transmit GIBC (free count, not 1). Nothing pending: the bus floats to FFh, i.e. no bid, and CIR type 000 reads as "no interrupt" (p. 311, 321; PDF p. 312, 322), so the model's CIR 0 **confirms** |
| `irq`: IRQ 1 while any isr bit is enabled in imr | IRQN is asserted when the winning bid exceeds the ICR threshold; ISR&IMR only admits a source to the bidding (p. 318, PDF p. 319). `eiasetup` writes `icr = 0`, and every bid is non-zero (hard-wired bits) | **confirms** (equivalent with threshold 0) |
| `bcr` "written by eiasetup" (p9boot.md) | shipped `deveia.c` writes no `bcr` | doc error (s9term not checked) |

## WD33C93A (`WD_CHOICES`, `scsi.c`)

| Choice | The data sheet | Verdict |
|---|---|---|
| `reset`: after Creset, status 0x01 with Eaf (own ID 0x08), else 0x00, and an interrupt | Reset-state interrupts: 0000 0000 "reset … with no advanced features enabled"; 0000 0001 "successfully completed a Reset command with advanced features enabled" (PDF p. 32). Own ID register: FS1 FS0 0 EHP **EAF** ID2 ID1 ID0, i.e. EAF is bit 3 = 0x08 (PDF p. 23). The errata list says "bit 4, Own ID" (PDF p. 7); the register figure and `scsi.c` (`Eaf = 0x08`) agree on bit 3 | **confirms** |
| `no-targets`: every selection ends with status 0x42 and an interrupt | 0100 0010: "A timeout occurred during a Select or Reselect command. The state … is disconnected" (PDF p. 34). The timeout comes after the Timeout Period register's time: value = Tper·Fclk/80 (PDF p. 26). `ctlrreset` writes `(200*ClkFreq)/80`, i.e. 200 ms | **refines**: status right; the real chip interrupts 200 ms after the select, the model at once |
| `irq`: IRQ 10 while Intrpend | INT (aux status bit 7) is "reset when the SCSI Status register is read" (PDF p. 18) | **confirms** |
| register access (class docstring): the address advances after data accesses except at Rcmd 0x18, Rdata 0x19 | "the Address register will automatically increment … with the exception of the following locations: Auxiliary Status register, Data register, and the Command register" (PDF p. 23) | **refines**: 0x1F does not advance either (the driver never selects it) |

## IIC: PCF8584 and the PCF8582 EEPROM (`IIC_CHOICES`, `deviic.c`)

The PCF8584 sheet is the 1997 edition and the EEPROM sheet the 1997
PCF85xxC-2 family (`MANIFEST.md`, "Dates").

| Choice | The data sheet | Verdict |
|---|---|---|
| `bus`: S1 read = PIN 0x80, LRB 0x08 ("Nak"), BB 0x01 ("Busfree"); S0' and S2 through ES1 before ESO | S1 status: PIN, 0, STS, BER, LRB/AD0, AAS, LAB, BB (block diagram, p. 556, PDF p. 557). BB: "A zero indicates that the bus is busy" (p. 565, PDF p. 566), so 1 = free, as the driver's `Busfree` says. BER (0x10) is the driver's `Buserr`. Register select: ESO = 0 with ES1/ES2 picks S0' (own address), S2 (clock) or S3 (vector) (Table 5, p. 563). `iicreset`'s S2 = 0x18 is 8 MHz, and SCL bits 00 are 90 kHz (the driver's name says 100 kHz) | **confirms** |
| `repeated-start`: the 0xA5 written to S0 before STA is the repeated START's address, not a data byte | Three passages: (1) "In the transmitter mode data is transmitted to the I2C-bus as soon as it is written to the S0 shift register if the serial I/O is enabled (ESO = 1)" (§6.7, p. 561, PDF p. 562). (2) Table 7: STA = 1, STO = 0 in MST/TRM is "REPEAT START: same as for SLV/REC", i.e. "transmit START + address" (p. 563, PDF p. 564). (3) Fig. 8: load **45H** into S1 (no PIN), "The current contents of register S0 is NOT clocked out", then write the slave address to S0 (p. 570, PDF p. 571). The driver does the reverse: S0 = 0xA5 first, then S1 = **0xC5** (PIN\|ESO\|STA\|ACK). By (1) the 0xA5 goes out as a data byte to the EEPROM, then (2) sends START + S0 (still 0xA5) as the address. On the EEPROM: "The lower 8 bits of the word address are incremented after each transmission of a data byte (read or write)" (p. 637, PDF p. 638), and the write is only programmed after a STOP (p. 635, PDF p. 636). So nothing is written, but the read would start at **word 1** | **unsettled, probably contradicts.** The model keeps the pointer at 0. It matters only for which EEPROM bytes fill `Eeprom`, and the image is invented anyway (`eeprom`). A real board's image would be laid out one byte up |
| `receive`: first S0 read after the address returns the address byte; each S0 read with ACK set starts the next byte; 0xC0 completes the byte in progress | "The first read of the S0 register is a 'dummy read' of the slave address which should be discarded" (Fig. 7 note, p. 569, PDF p. 570; §6.7 remark 2, p. 561). The data sheet's sequence ends with 40H (ACK = 0, negative acknowledge), then a read, then C3H (STOP). Writing PIN = 1 "all status bits are reset to logic 0" (§6.8.1.1, p. 562, PDF p. 563). The driver's 0xC0 is PIN\|ESO with ACK = 0 | **confirms** the dummy read; the 0xC0 handling stays a model choice |
| `eeprom`: contents | PCF8582: 256 x 8 (p. 630). The contents are the board's, so no data sheet can say | choice (no source) |

## MK48T02 timekeeper (`CHOICES` `rtc`, `devrtc.c`)

| Choice | The data sheet | Verdict |
|---|---|---|
| One 2K timekeeper: NVRAM bytes 0..2039 then control, sec, min, hour, day, date, month, year in BCD; a byte per word | Register map at 7F8..7FF: control (W, R, S, calibration 4:0), seconds (bit 7 ST), minutes, hours (bit 7 KS), day 01-07 (bit 6 FT), date, month, year 00-99, all BCD; the RAM is 2K x 8 (Fig. 5, data sheet p. 7/14, PDF p. 1030). `io.h`: IONAK 0x2000 + 0x7F8·4 = 0x3FE0 = RTCADDR, NVRAMLEN 2040 | **confirms** |
| RTCREAD (0x40) / RTCWRITE (0x80) freeze the registers; clearing RTCWRITE loads them | "Updating is halted when a '1' is written into the 'Read' bit … the registers reflect the count … at the moment the Halt command was issued". "Setting the Write bit to a '1', like the Read Bit, halts updates … Resetting the Write bit to a '0' then transfers those values to the actual TIMEKEEPER counters" (PDF p. 1030) | **confirms** |
| The clock runs from 1993-01-03 | board state, not a data-sheet matter; ST (seconds bit 7) = 1 would stop the oscillator | choice |

## SONIC: National DP83932B (`SONIC_CHOICES`, `devether.c`)

Data sheet pages are in the 1992 LAN Databook (book p. 1-N = PDF p. N+9).

| Choice | The data sheet | Verdict |
|---|---|---|
| `registers`: reset cr = Rst\|Stp\|Rxdis; writing cr with Rst clear while in reset only leaves reset "(QEMU)" | "During hardware reset, bits 7, 4, and 2 are set" (RST, STP, RXDIS). "if the RST bit is set, two writes to the Command Register are required to issue a command to the SONIC; one to clear the RST bit, and one to issue the command." Software reset: bits 9, 8, 1, 0 cleared, bits 7 and 2 set, the rest unaffected (§4.3.1, p. 1-314, PDF p. 323) | **confirms**; the source is now the data sheet, not QEMU |
| `isr`: write-one-to-clear; IRQ 9 while isr & imr | "A bit is cleared by writing '1' to it. Writing a '0' to any bit has no effect." (§4.3.6, p. 1-324, PDF p. 333) | **confirms** |
| `rra`: 4-word resource at urra:rrp; rrp += 16; wraps rea → rsa | RRA registers concatenate with URRA; the SONIC "finishes reading the RRA and automatically wraps" (§3.4.1, p. 1-302, PDF p. 311); in 32-bit mode each 16-bit field is a long word, "upper word (D<31:16>) is not used" | **confirms** |
| `cam`: cdc entries of (cep, cap0..2) at urra:cdp "(QEMU)"; each cap two address bytes low byte first; then CE; isr Lcd | The CDA "resides in the same 64k byte block of memory as the Receive Resource Area"; descriptor = CEP, CAP0, CAP1, CAP2, then one CAM Enable word; "When the SONIC completes the Load CAM command, the CDP register points to the next location after the CAM Enable field and the CDC equals zero … sets the Load CAM Done (LCD) bit" (§4.1.1, p. 1-310, PDF p. 319). Byte order: address 10 20 30 40 50 60 loads CAP0 = 2010h, CAP1 = 4030h, CAP2 = 6050h (§4.3.10, p. 1-328, PDF p. 337) | **confirms** (the upper half from URRA is now the data sheet, not QEMU); **contradicts** in one detail: CDP ends past the CE word, the model leaves it on it |
| `transmit`: status 0x0001 (PTX) | TXpkt.status = TCR bits <10:0> plus NC4..NC0 collisions in bits 15:11 (§3.5.1.2, p. 1-308, PDF p. 317); a clean send with no collisions is PTX | **confirms** |
| `receive`: byte count = frame + 4; status Prx (\| Bc, \| Lpkt); EOL keeps the descriptor (Rde), re-read at the next frame; still EOL → dropped and counted in mpt | Byte count runs "from the start of Destination Address to the end of FCS". The status field "is loaded from the contents of the Receive Control register", so RCR bits 15:9 (ERR, RNT, BRD, PRO, AMC, LB1, LB0) appear in it, with MC, BC, LPKT, CRS, COL, CRCR, FAER, LBK, PRX below (Fig. 3-6, p. 1-304, PDF p. 313). With EOL = 1 "the SONIC maintains ownership of the descriptor by not writing to the RXpkt.in_use field" and flags RDE; at the next reception "It re-reads the same RXpkt.link … If the SONIC still finds EOL = 1, reception ceases"; RBWC < EOBC fetches the next resource (§3.4.5..3.4.6, p. 1-306, PDF p. 315). MPT counts a packet missed for "lack of memory resources" (§4.3.11, p. 1-328, PDF p. 337) | **confirms** the flow, the byte count, the EOL handling and MPT; **contradicts** the status value (the RCR configuration bits are missing; harmless to `devether.c`) |
| descriptor words zero-extended "(QEMU's 32-bit mode)" | "In 32-bit mode the upper word, D<31:16>, is not used" (p. 1-302, 1-304) | **unsettled**: the sheet does not say what the SONIC drives on D<31:16> when it writes. `devether.c` compares whole words with Host = 0 and Interface = ~0, which suggests the board read zeros |
| `filter`, `dma` | address recognition by PRO/BRD/CAM (§1.x, §4.3.3); not re-checked in detail | not checked |

## Not covered by a data sheet

- **The interrupt registers** at IONAK+0x80 (`mask0/1`, `status0/1`) and the
  IOCTL latch (`SCSIENABLE`, `IOENABLE`) are board logic.  The choices
  `irq-level` and `irq-status` remain inferences.
- **`Lcdisp`.** A 768 x 1024, 2-bit display.  `screenupdate` writes a row
  address in two 6-bit pieces to `ctl` (y>>8, then (y>>2)&0x3F), then four
  bytes per 4 x 4 pixel group to `data`; `NT` code adds a column address.
  No controller part is named.  CHOICES `lcd` (accept and count writes)
  stays a choice.
- **The keyboard** (serial, Quart port, 600 baud, odd parity) and the
  **Incon** (Datakit) board.
