// HobbitQuart.bsv -- the Philips/Signetics SC68C94 QUART at IOBASE + 0x100,
// the subset 1st Edition Plan 9's deveia.c uses, behind the ULX3S plan's
// "Device bus contract" (hobbit/docs/ulx3s_plan.md):
//
//   req(addr[11:0] offset in the 0x100-byte window, wdata, be[3:0], write)
//   resp -> rdata, one response per request (latency 1-2 clocks)
//   irq   IRQN (the board's IRQQUART, io.h bit 1), active high here
//
// Behavioural reference: tools/p9boot.py's Quart and QUART_CHOICES, which
// cite the SC68C94 product specification (27 April 1994; docs/devices/
// MANIFEST.md, README.md "Quart") and record the resolved contradictions
// this RTL follows: FIFOs 8 deep, interrupt priority by numeric bid (the
// largest wins), an empty transmitter bids 0x78|ch with GIBC = 7, the
// counter bids 0x15/0x17 (channel b / d).  hobbit/fpga/dev/quart/
// run_replay.sh replays register-access traces (the kernel's own, captured
// from a p9boot run, and directed ones) into this RTL and the Python model
// and compares every read, every fault, the irq line, IL6 and every
// transmitted byte.
//
// Registers (word index = addr[7:2], io.h's Quart):
//   per channel (a = DUART base + 0..3, b = + 8..11)
//     mr  R/W  MR1 then MR2 through the MR pointer (MrReset points at MR1)
//     sr  R    RxRDY 0x01 (FIFO not empty), FFULL 0x02 (eight held),
//              TxRDY 0x04 (enabled, FIFO not full), TxEMT 0x08 (enabled,
//              FIFO empty, shifter idle).  Error bits never set: an error
//              on the pin is a fault instead (below).
//     csr W    stored; the pin's rate is the clksPerBit parameter
//     cr  W    RxEnable 1, RxDisable 2, TxEnable 4, TxDisable 8, MrReset
//              0x10, RxReset 0x20 (disable, flush), TxReset 0x30 (disable,
//              flush), ErrReset 0x40, BrkReset 0x50, BrkStop 0x70 (no
//              error or break state exists, so no-ops).  BrkStart 0x60 and
//              commands 0x80..0xF0 are not implemented: fault.
//     rxfifo R pop (empty reads 0)      txfifo W push
//   per DUART: acr, imr, ctu, ctl, opr, iopcra, iopcrb W (opr/ctu/ctl R:
//     the written value), ipcr/ipr R 0, isr R, start R (counter on),
//     stop R (clears CtrRDY; the counter runs on, 1994 p. 319)
//   global: bcr[4] R/W, pwrup, nak, ack W, cir/gicr/gibcr R, update W
//     (latch the winning bid), grxfifo R / gtxfifo W (channel gicr),
//     icr R/W, brg W, setclk normal (0x2F) W
//
// isr: TxRDYa 0x01 / TxRDYb 0x10 = transmitter enabled and its FIFO empty
// (MR0[5:4] = 00 at reset: "8 bytes empty", 1994 p. 312); RxRDYa 0x02 /
// RxRDYb 0x20 = a byte held; CtrRDY 0x08.  irq = any (isr & imr), i.e. a
// bid above ICR's threshold 0.  Bids (1994 p. 311, 321; reprint p. 333):
// receiver (n<<5)|0x0C|ch (n held, 8 coded 7), transmitter
// (free<<4)|0x08|ch (8 free coded 7), counter 0x14|ch with ch = b (1) or
// d (3).  The numerically largest wins.
//
// Counter/timer: started by a read of `start` (acr[6:4] must be 111, timer
// mode on X1/CLK / 16, and the count non-zero, else fault as p9boot's
// _period stops the run); CtrRDY is set every 2 * count ticks of the C/T
// clock.  The C/T clock is the SoC clock times ctNum/ctDen (a fractional
// divider: the real part's X1/16 is 3.6864 MHz / 16 = 230400 Hz, so a
// board at F Hz passes ctNum/ctDen = 230400/F reduced).
//
// Channels.  Channel 0 is the console: 8N1 on the txd/rxd pins at
// clksPerBit SoC clocks a bit; its mr1/mr2 must say 8 bits, no parity, one
// stop bit (0x13 / 0x07, what uartsetup writes) when a byte goes out or
// comes in, else fault.  Channels 1, 2 and 3 (2 = keyboard, 3 = mouse)
// are byte streams: txOut gets bytes as the transmitter takes them from
// its FIFO (the consumer's pace is the line's), rxIn puts a byte into the
// receive FIFO and blocks while the receiver is disabled or the FIFO is
// full, which is the Python model's "held on the line".
//
// Where the RTL and the Python model knowingly differ (both documented in
// QuartReplayTb.bsv's header): the model's transmitter is instantaneous,
// so its sr/isr always show an empty FIFO; the RTL has the real 8-deep
// FIFO and shifter, and the two agree whenever the FIFO has drained.  The
// pin's receiver cannot hold a byte "on the line": a byte that finds the
// FIFO full waits in the shift register (one, as the part's), and a
// further one, a byte while the receiver is disabled, or a framing error
// is a fault.
//
// Faults (fail loud): sticky `fault`, `faults` count (one per faulting
// event), `faultInfo` = the code of the last (see FaultKind), and a
// $display in Bluesim.  Everything p9boot.Quart stops on is a fault
// (partial writes, unmodelled registers, a counter in another mode), and
// so is everything the model accepts but this RTL does not implement:
// bcr or icr non-zero (bids and threshold assume 0), pwrdn, X1/CLK / 2,
// BrkStart and the 0x80..0xF0 commands, a txfifo write while the
// transmitter is disabled or its FIFO full.

package HobbitQuart;

import Vector :: *;
import FIFOF :: *;
import RegFile :: *;
import GetPut :: *;

// --------------------------------------------------------------- 8-byte FIFO
// Unguarded methods (callers test count): enq on a full FIFO and deq on an
// empty one are ignored.  All state changes happen in one rule, so enq,
// deq and clear from different rules never conflict.
interface ByteFifo8;
  method Action enq(Bit#(8) b);
  method Action deq;
  method Action clear;
  method Bit#(8) first;
  method Bit#(4) count;
endinterface

module mkByteFifo8(ByteFifo8);
  RegFile#(Bit#(3), Bit#(8)) mem <- mkRegFileFull;
  Reg#(Bit#(3)) rp <- mkReg(0);
  Reg#(Bit#(3)) wp <- mkReg(0);
  Reg#(Bit#(4)) cnt <- mkReg(0);
  RWire#(Bit#(8)) enqW <- mkRWire;
  PulseWire deqW <- mkPulseWire;
  PulseWire clrW <- mkPulseWire;

  (* fire_when_enabled, no_implicit_conditions *)
  rule canon;
    if (clrW) begin
      rp <= 0; wp <= 0; cnt <= 0;
    end
    else begin
      Bool doDeq = deqW && cnt != 0;
      Bool doEnq = isValid(enqW.wget) && cnt != 8;
      if (doEnq) begin
        mem.upd(wp, validValue(enqW.wget));
        wp <= wp + 1;
      end
      if (doDeq) rp <= rp + 1;
      cnt <= cnt + (doEnq ? 1 : 0) - (doDeq ? 1 : 0);
    end
  endrule

  method Action enq(Bit#(8) b) = enqW.wset(b);
  method Action deq = deqW.send;
  method Action clear = clrW.send;
  method Bit#(8) first = mem.sub(rp);
  method Bit#(4) count = cnt;
endmodule

// --------------------------------------------------------------- the Quart
typedef enum {
  FkNone,          // 0
  FkPartialWrite,  // 1 p9boot: "partial write"
  FkBadRead,       // 2 p9boot: read "is not modelled"
  FkBadWrite,      // 3 p9boot: write "is not modelled"
  FkCtrMode,       // 4 p9boot _period: counter in a mode the model lacks
  FkBidCtl,        // 5 bcr != 0: bids assume the reset value
  FkIcr,           // 6 icr != 0: the threshold is assumed 0
  FkCommand,       // 7 cr command not implemented (BrkStart, 0x80..0xF0)
  FkTxDisabled,    // 8 txfifo write with the transmitter disabled
  FkTxFull,        // 9 txfifo write with its FIFO full (byte dropped)
  FkFormat,        // 10 channel 0 byte while mr1/mr2 are not 8N1
  FkRxOverrun,     // 11 channel 0 pin: a byte lost to a full FIFO
  FkRxDisabled,    // 12 channel 0 pin: a byte while the receiver is off
  FkFraming,       // 13 channel 0 pin: stop bit 0
  FkClock,         // 14 pwrdn or X1/CLK / 2: not implemented
  FkOutside        // 15 offset beyond the 0x100-byte window
} FaultKind deriving (Bits, Eq);

interface QuartDebug;
  method Vector#(2, Bit#(16)) ctrExpiries;   // CtrRDY settings so far
  method Vector#(4, Bit#(4)) rxLevel;
  method Bool txIdle;                        // every TX FIFO and shifter
endinterface

interface HobbitQuart;
  method Action req(Bit#(12) addr, Bit#(32) wdata, Bit#(4) be, Bool write);
  method ActionValue#(Bit#(32)) resp;
  (* always_ready *) method Bool irq;
  (* always_ready *) method Bit#(1) txd;
  (* always_ready, always_enabled *) method Action rxd(Bit#(1) v);
  interface Vector#(3, Put#(Bit#(8))) rxIn;    // channels 1, 2, 3
  interface Vector#(3, Get#(Bit#(8))) txOut;   // channels 1, 2, 3
  (* always_ready *) method Bool fault;
  (* always_ready *) method Bit#(16) faults;
  (* always_ready *) method Bit#(16) faultInfo;  // {kind[3:0], 0, reg[5:0], ...}
  interface QuartDebug dbg;
endinterface

typedef struct {
  Bit#(12) addr;
  Bit#(32) wdata;
  Bit#(4) be;
  Bool write;
} QReq deriving (Bits);

module mkHobbitQuart#(Integer clksPerBit, Integer ctNum, Integer ctDen)
                    (HobbitQuart);
  // ---- per channel
  Vector#(4, Reg#(Bit#(8))) mr1 <- replicateM(mkReg(0));
  Vector#(4, Reg#(Bit#(8))) mr2 <- replicateM(mkReg(0));
  Vector#(4, Reg#(Bool)) mrp <- replicateM(mkReg(False));  // True: MR2
  Vector#(4, Reg#(Bit#(8))) csr <- replicateM(mkReg(0));
  Vector#(4, Reg#(Bool)) txEn <- replicateM(mkReg(False));
  Vector#(4, Reg#(Bool)) rxEn <- replicateM(mkReg(False));
  Vector#(4, ByteFifo8) rxF <- replicateM(mkByteFifo8);
  Vector#(4, ByteFifo8) txF <- replicateM(mkByteFifo8);
  // ---- per DUART
  Vector#(2, Reg#(Bit#(8))) acr <- replicateM(mkReg(0));
  Vector#(2, Reg#(Bit#(8))) imr <- replicateM(mkReg(0));
  Vector#(2, Reg#(Bit#(8))) ctu <- replicateM(mkReg(0));
  Vector#(2, Reg#(Bit#(8))) ctl <- replicateM(mkReg(0));
  Vector#(2, Reg#(Bit#(8))) opr <- replicateM(mkReg(0));
  Vector#(2, Reg#(Bit#(8))) iopcra <- replicateM(mkReg(0));
  Vector#(2, Reg#(Bit#(8))) iopcrb <- replicateM(mkReg(0));
  // the counters: owned by rule counter, fed by wires from rule access
  Vector#(2, Reg#(Bool)) running <- replicateM(mkReg(False));
  Vector#(2, Reg#(Bool)) ready <- replicateM(mkReg(False));
  Vector#(2, Reg#(Bit#(17))) ctr <- replicateM(mkReg(0));
  Vector#(2, Reg#(Bit#(17))) reload <- replicateM(mkReg(0));  // 2*count
  Vector#(2, Reg#(Bool)) modeOk <- replicateM(mkReg(False));
  Vector#(2, Reg#(Bit#(16))) expiries <- replicateM(mkReg(0));
  Vector#(2, PulseWire) startW <- replicateM(mkPulseWire);
  Vector#(2, PulseWire) stopW <- replicateM(mkPulseWire);
  Vector#(2, RWire#(Tuple2#(Bit#(17), Bool))) presetW <- replicateM(mkRWire);
  Reg#(Bit#(32)) ctAcc <- mkReg(0);
  // ---- global
  Vector#(4, Reg#(Bit#(8))) bcr <- replicateM(mkReg(0));
  Reg#(Bit#(8)) icr <- mkReg(0);
  Reg#(Bit#(8)) brg <- mkReg(0);
  Reg#(Bit#(8)) cir <- mkReg(0);
  Reg#(Bit#(8)) gicr <- mkReg(0);
  Reg#(Bit#(8)) gibcr <- mkReg(0);
  // ---- the port
  FIFOF#(QReq) reqQ <- mkFIFOF;
  FIFOF#(Bit#(32)) respQ <- mkFIFOF;
  // ---- faults: every rule reports through its own wire, one rule counts
  RWire#(Bit#(16)) faultAccW <- mkRWire;
  RWire#(Bit#(16)) faultCtrW <- mkRWire;
  RWire#(Bit#(16)) faultRxW <- mkRWire;
  Reg#(Bool) faultR <- mkReg(False);
  Reg#(Bit#(16)) nfault <- mkReg(0);
  Reg#(Bit#(16)) finfo <- mkReg(0);
  // ---- channel 0 pins
  Reg#(Bit#(1)) rxS0 <- mkReg(1);
  Reg#(Bit#(1)) rxS1 <- mkReg(1);
  Wire#(Bit#(1)) rxdW <- mkBypassWire;
  Reg#(Bit#(4)) rxBit <- mkReg(0);       // 0 idle, 1 start, 2..9 data, 10 stop
  Reg#(Bit#(16)) rxCnt <- mkReg(0);
  Reg#(Bit#(8)) rxSh <- mkReg(0);
  Reg#(Maybe#(Bit#(8))) rxHold <- mkReg(tagged Invalid);
  Reg#(Bit#(10)) txSh <- mkReg('1);
  Reg#(Bit#(4)) txLeft <- mkReg(0);      // bits still to send after this
  Reg#(Bit#(16)) txCnt <- mkReg(0);
  Reg#(Bool) txBusy <- mkReg(False);

  Bit#(16) cpb = fromInteger(clksPerBit);

  function Bit#(16) fcode(FaultKind k, Bit#(6) idx) =
    {pack(k), 4'b0, 2'b0, idx};

  function Bool is8N1(Integer ch) =
    mr1[ch][4:0] == 5'h13 && mr2[ch][3:0] == 4'h7;

  function Bit#(8) isr(Integer d);
    Integer a = 2 * d;
    Integer b = 2 * d + 1;
    Bit#(8) v = 0;
    if (txEn[a] && txF[a].count == 0) v = v | 8'h01;
    if (rxF[a].count != 0) v = v | 8'h02;
    if (ready[d]) v = v | 8'h08;
    if (txEn[b] && txF[b].count == 0) v = v | 8'h10;
    if (rxF[b].count != 0) v = v | 8'h20;
    return v;
  endfunction

  // The winning bid: (cir, gicr, gibcr); cir 0 when nothing is pending.
  function Tuple3#(Bit#(8), Bit#(8), Bit#(8)) winner;
    Bit#(8) best = 0;
    Bit#(8) bch = 0;
    Bit#(8) bn = 0;
    for (Integer d = 0; d < 2; d = d + 1) begin
      Bit#(8) pend = isr(d) & imr[d];
      for (Integer k = 0; k < 5; k = k + 1) begin
        // the five sources of DUART d: ctr, rx a, rx b, tx a, tx b
        Bit#(8) bit_ = case (k) 0: 8'h08; 1: 8'h02; 2: 8'h20;
                                3: 8'h01; default: 8'h10; endcase;
        Integer ch = case (k) 0: 2 * d + 1; 1: 2 * d; 2: 2 * d + 1;
                              3: 2 * d; default: 2 * d + 1; endcase;
        Bit#(8) chb = fromInteger(ch);
        Bit#(8) bid = 0;
        Bit#(8) n = 0;
        if (k == 0) bid = 8'h14 | chb;
        else if (k <= 2) begin
          Bit#(4) c = rxF[ch].count;
          n = zeroExtend(c > 7 ? 7 : c);
          bid = (n << 5) | 8'h0C | chb;
        end
        else begin
          Bit#(4) free = 8 - txF[ch].count;
          n = zeroExtend(free > 7 ? 7 : free);
          bid = (n << 4) | 8'h08 | chb;
        end
        if ((pend & bit_) != 0 && bid > best) begin
          best = bid; bch = chb; bn = n;
        end
      end
    end
    return tuple3(best, bch, bn);
  endfunction

  // ================================================================ access
  rule access;
    QReq q = reqQ.first;
    reqQ.deq;
    Bit#(6) idx = q.addr[7:2];
    Bit#(8) d8 = q.wdata[7:0];
    Bit#(32) r = 0;
    Maybe#(FaultKind) bad = tagged Invalid;
    Bit#(1) du = idx[4];            // DUART
    Bit#(4) rg = idx[3:0];          // register in the DUART
    Bit#(2) ch = {du, rg[3]};       // channel of the per-channel registers
    Bool perCh = rg[2] == 0;        // 0..3, 8..11

    // a pop of a receive FIFO (rxfifo, grxfifo) and a push to a transmit
    // FIFO (txfifo, gtxfifo), done once below for whichever channel
    Maybe#(Bit#(2)) popCh = tagged Invalid;
    Maybe#(Bit#(2)) pushCh = tagged Invalid;
    Bit#(1) startD = 0;
    Bool doStart = False;
    Bool doStop = False;
    Maybe#(Tuple2#(Bit#(17), Bool)) preset = tagged Invalid;
    Bool flushTx = False;
    Bool flushRx = False;

    if (q.addr[11:8] != 0) bad = tagged Valid FkOutside;
    else if (q.write && q.be != 4'hF) bad = tagged Valid FkPartialWrite;
    else if (!q.write) begin
      // ------------------------------------------------ reads
      if (idx < 6'h20) begin
        if (perCh) case (rg[1:0])
          0: begin
               r = zeroExtend(mrp[ch] ? mr2[ch] : mr1[ch]);
               mrp[ch] <= True;
             end
          1: begin
               Bit#(8) s = 0;
               if (rxF[ch].count != 0) s = s | 8'h01;
               if (rxF[ch].count == 8) s = s | 8'h02;
               if (txEn[ch] && txF[ch].count != 8) s = s | 8'h04;
               if (txEn[ch] && txF[ch].count == 0
                   && !(ch == 0 && txBusy)) s = s | 8'h08;
               r = zeroExtend(s);
             end
          2: bad = tagged Valid FkBadRead;   // cr is write-only
          3: popCh = tagged Valid ch;
        endcase
        else case (rg)
          4, 13: r = 0;                      // ipcr, ipr: inputs all 0
          5: r = zeroExtend(du == 0 ? isr(0) : isr(1));
          6: r = zeroExtend(ctu[du]);
          7: r = zeroExtend(ctl[du]);
          12: r = zeroExtend(opr[du]);
          14: begin                          // start
                Bit#(16) count = {ctu[du], ctl[du]};
                if ((acr[du] & 8'h70) != 8'h70 || count == 0)
                  bad = tagged Valid FkCtrMode;
                else doStart = True;
              end
          15: doStop = True;                 // stop
        endcase
      end
      else case (idx)
        6'h20, 6'h21, 6'h22, 6'h23: r = zeroExtend(bcr[idx[1:0]]);
        6'h28: r = zeroExtend(cir);
        6'h29: r = zeroExtend(gicr);
        6'h2A: r = zeroExtend(gibcr);
        6'h2B: popCh = tagged Valid gicr[1:0];
        6'h2C: r = zeroExtend(icr);
        default: bad = tagged Valid FkBadRead;
      endcase
    end
    else begin
      // ------------------------------------------------ writes
      if (idx < 6'h20) begin
        if (perCh) case (rg[1:0])
          0: begin
               if (mrp[ch]) mr2[ch] <= d8; else mr1[ch] <= d8;
               mrp[ch] <= True;
             end
          1: csr[ch] <= d8;
          2: begin
               Bool tx = txEn[ch];
               Bool rx = rxEn[ch];
               Bool toMr1 = False;
               if (d8[1:0] == 2'b01) rx = True;
               else if (d8[1:0] == 2'b10) rx = False;
               if (d8[3:2] == 2'b01) tx = True;
               else if (d8[3:2] == 2'b10) tx = False;
               case (d8[7:4])
                 0, 4, 5, 7: noAction;      // none, ErrReset, BrkReset, BrkStop
                 1: toMr1 = True;
                 2: begin rx = False; flushRx = True; end
                 3: begin tx = False; flushTx = True; end
                 default: bad = tagged Valid FkCommand;
               endcase
               if (!isValid(bad)) begin
                 txEn[ch] <= tx;
                 rxEn[ch] <= rx;
                 if (toMr1) mrp[ch] <= False;
               end
               else begin flushTx = False; flushRx = False; end
             end
          3: pushCh = tagged Valid ch;
        endcase
        else case (rg)
          4: begin
               acr[du] <= d8;
               preset = tagged Valid tuple2({ctu[du], ctl[du], 1'b0},
                                       (d8 & 8'h70) == 8'h70);
             end
          5: imr[du] <= d8;
          6: begin
               ctu[du] <= d8;
               preset = tagged Valid tuple2({d8, ctl[du], 1'b0},
                                       (acr[du] & 8'h70) == 8'h70);
             end
          7: begin
               ctl[du] <= d8;
               preset = tagged Valid tuple2({ctu[du], d8, 1'b0},
                                       (acr[du] & 8'h70) == 8'h70);
             end
          12: opr[du] <= d8;
          13: iopcra[du] <= d8;
          14: iopcrb[du] <= d8;
          default: bad = tagged Valid FkBadWrite;   // 15: stop is read-only
        endcase
      end
      else case (idx)
        6'h20, 6'h21, 6'h22, 6'h23: begin
            bcr[idx[1:0]] <= d8;
            if (d8 != 0) bad = tagged Valid FkBidCtl;
          end
        6'h24: bad = tagged Valid FkClock;          // power down
        6'h25, 6'h26, 6'h27: noAction;              // power up, nak, ack
        6'h2A: begin                                // update
            match {.c, .g, .n} = winner;
            cir <= c; gicr <= g; gibcr <= n;
          end
        6'h2B: pushCh = tagged Valid gicr[1:0];
        6'h2C: begin
            icr <= d8;
            if (d8 != 0) bad = tagged Valid FkIcr;
          end
        6'h2D: brg <= d8;
        6'h2E: bad = tagged Valid FkClock;          // X1/CLK divided by 2
        6'h2F: noAction;                            // X1/CLK normal
        default: bad = tagged Valid FkBadWrite;
      endcase
    end

    // the transmit push: the part does not load a disabled transmitter
    if (pushCh matches tagged Valid .c &&& !isValid(bad)) begin
      if (!txEn[c]) bad = tagged Valid FkTxDisabled;
      else if (txF[c].count == 8) bad = tagged Valid FkTxFull;
      else if (c == 0 && !is8N1(0)) bad = tagged Valid FkFormat;
    end
    if (!isValid(bad)) begin
      for (Integer i = 0; i < 4; i = i + 1) begin
        Bit#(2) ci = fromInteger(i);
        if (popCh matches tagged Valid .c &&& c == ci
            &&& rxF[i].count != 0) begin
          r = zeroExtend(rxF[i].first);
          rxF[i].deq;
        end
        if (pushCh matches tagged Valid .c &&& c == ci)
          txF[i].enq(d8);
        if (flushTx && ch == ci) txF[i].clear;
        if (flushRx && ch == ci) rxF[i].clear;
      end
      for (Integer i = 0; i < 2; i = i + 1) begin
        if (du == fromInteger(i)) begin
          if (doStart) startW[i].send;
          if (doStop) stopW[i].send;
          if (preset matches tagged Valid .p) presetW[i].wset(p);
        end
      end
    end
    if (bad matches tagged Valid .k) begin
      faultAccW.wset(fcode(k, idx));
      $display("FAULT Quart: %s at +0x%03x (reg 0x%02x) data 0x%08x be %x: kind %0d", q.write ? "write" : "read", q.addr, idx, q.wdata,
               q.be, pack(k));
      r = 0;
    end
    respQ.enq(r);
  endrule

  // ================================================================ counters
  (* fire_when_enabled, no_implicit_conditions *)
  rule counter;
    // the C/T clock: ctNum/ctDen of the SoC clock (Bresenham)
    Bit#(32) acc = ctAcc + fromInteger(ctNum);
    Bool tick = acc >= fromInteger(ctDen);
    ctAcc <= tick ? acc - fromInteger(ctDen) : acc;
    Maybe#(Bit#(16)) f = tagged Invalid;
    for (Integer d = 0; d < 2; d = d + 1) begin
      Bit#(17) rl = reload[d];
      Bool ok = modeOk[d];
      if (presetW[d].wget matches tagged Valid {.v, .m}) begin
        rl = v; ok = m;
        reload[d] <= v; modeOk[d] <= m;
      end
      if (startW[d]) begin
        running[d] <= True;
        ready[d] <= False;
        ctr[d] <= rl - 1;
      end
      else if (running[d] && tick) begin
        if (ctr[d] == 0) begin
          if (!ok || rl == 0) begin
            // p9boot's _tick -> _period stops the run here
            f = tagged Valid fcode(FkCtrMode, fromInteger(16 * d + 14));
            running[d] <= False;
          end
          else begin
            if (!stopW[d]) ready[d] <= True;
            expiries[d] <= expiries[d] + 1;
            ctr[d] <= rl - 1;
          end
        end
        else ctr[d] <= ctr[d] - 1;
        if (stopW[d]) ready[d] <= False;
      end
      else if (stopW[d]) ready[d] <= False;
    end
    if (f matches tagged Valid .c) begin
      faultCtrW.wset(c);
      $display("FAULT Quart: counter expired in a mode the model lacks");
    end
  endrule

  // ================================================================ channel 0
  (* fire_when_enabled, no_implicit_conditions *)
  rule pinRx;
    rxS0 <= rxdW;
    rxS1 <= rxS0;
    Bit#(1) v = rxS1;
    Maybe#(Bit#(16)) f = tagged Invalid;
    Bool fifoFree = rxF[0].count != 8;
    Maybe#(Bit#(8)) hold = rxHold;
    Maybe#(Bit#(8)) put = tagged Invalid;
    // the held byte drains first
    if (hold matches tagged Valid .h &&& fifoFree) begin
      put = tagged Valid h;
      hold = tagged Invalid;
      fifoFree = False;   // one enq a clock
    end
    if (rxBit == 0) begin
      if (v == 0) begin
        rxBit <= 1;
        rxCnt <= cpb / 2;
      end
    end
    else if (rxCnt != 0) rxCnt <= rxCnt - 1;
    else if (rxBit == 1) begin
      // middle of the start bit
      if (v == 0) begin rxBit <= 2; rxCnt <= cpb - 1; end
      else rxBit <= 0;    // a glitch
    end
    else if (rxBit <= 9) begin
      rxSh <= {v, rxSh[7:1]};
      rxBit <= rxBit + 1;
      rxCnt <= cpb - 1;
    end
    else begin
      // middle of the stop bit
      rxBit <= 0;
      if (v == 0) f = tagged Valid fcode(FkFraming, 3);
      else if (!rxEn[0]) f = tagged Valid fcode(FkRxDisabled, 3);
      else if (!is8N1(0)) f = tagged Valid fcode(FkFormat, 3);
      else if (fifoFree) put = tagged Valid rxSh;
      else if (!isValid(hold)) hold = tagged Valid rxSh;
      else f = tagged Valid fcode(FkRxOverrun, 3);
    end
    rxHold <= hold;
    if (put matches tagged Valid .b) rxF[0].enq(b);
    if (f matches tagged Valid .c) begin
      faultRxW.wset(c);
      $display("FAULT Quart: channel 0 receiver, code 0x%04x", c);
    end
  endrule

  (* fire_when_enabled, no_implicit_conditions *)
  rule pinTx;
    if (!txBusy) begin
      if (txF[0].count != 0) begin
        txSh <= {1'b1, txF[0].first, 1'b0};
        txF[0].deq;
        txLeft <= 9;
        txCnt <= cpb - 1;
        txBusy <= True;
      end
    end
    else if (txCnt != 0) txCnt <= txCnt - 1;
    else if (txLeft == 0) begin
      txBusy <= False;
      txSh <= '1;
    end
    else begin
      txSh <= {1'b1, txSh[9:1]};
      txLeft <= txLeft - 1;
      txCnt <= cpb - 1;
    end
  endrule

  (* fire_when_enabled, no_implicit_conditions *)
  rule countFaults;
    Bit#(16) n = nfault;
    Maybe#(Bit#(16)) last = tagged Invalid;
    for (Integer i = 0; i < 3; i = i + 1) begin
      RWire#(Bit#(16)) w = case (i) 0: faultAccW; 1: faultCtrW;
                                    default: faultRxW; endcase;
      if (w.wget matches tagged Valid .c) begin
        n = n + 1;
        last = tagged Valid c;
      end
    end
    if (last matches tagged Valid .c) begin
      faultR <= True;
      nfault <= n;
      finfo <= c;
    end
  endrule

  // ================================================================ methods
  function Put#(Bit#(8)) rxPut(Integer ch);
    return (interface Put;
      method Action put(Bit#(8) b) if (rxEn[ch] && rxF[ch].count != 8);
        rxF[ch].enq(b);
      endmethod
    endinterface);
  endfunction
  function Get#(Bit#(8)) txGet(Integer ch);
    return (interface Get;
      method ActionValue#(Bit#(8)) get if (txF[ch].count != 0);
        txF[ch].deq;
        return txF[ch].first;
      endmethod
    endinterface);
  endfunction

  function Put#(Bit#(8)) rxPut1(Integer i) = rxPut(i + 1);
  function Get#(Bit#(8)) txGet1(Integer i) = txGet(i + 1);

  method Action req(Bit#(12) addr, Bit#(32) wdata, Bit#(4) be, Bool write);
    reqQ.enq(QReq {addr: addr, wdata: wdata, be: be, write: write});
  endmethod
  method ActionValue#(Bit#(32)) resp;
    respQ.deq;
    return respQ.first;
  endmethod
  method Bool irq = (isr(0) & imr[0]) != 0 || (isr(1) & imr[1]) != 0;
  method Bit#(1) txd = txSh[0];
  method Action rxd(Bit#(1) v);
    rxdW <= v;
  endmethod
  interface rxIn = genWith(rxPut1);
  interface txOut = genWith(txGet1);
  method Bool fault = faultR;
  method Bit#(16) faults = nfault;
  method Bit#(16) faultInfo = finfo;
  interface QuartDebug dbg;
    method Vector#(2, Bit#(16)) ctrExpiries = readVReg(expiries);
    method Vector#(4, Bit#(4)) rxLevel;
      function Bit#(4) lvl(ByteFifo8 f) = f.count;
      return map(lvl, rxF);
    endmethod
    method Bool txIdle;
      Bool idle = !txBusy;
      for (Integer i = 0; i < 4; i = i + 1)
        if (txF[i].count != 0) idle = False;
      return idle;
    endmethod
  endinterface
endmodule

// A synthesis wrapper with board-ish parameters (25 MHz, 19200 baud on the
// console, X1/16 = 230400 Hz = 25 MHz * 1152/125000), for yosys alone.
(* synthesize *)
module mkHobbitQuartSynth(HobbitQuart);
  HobbitQuart q <- mkHobbitQuart(1302, 1152, 125000);
  return q;
endmodule

endpackage
