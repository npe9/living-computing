// EspLink.bsv -- the FPGA end of the ULX3S ESP32 Ethernet relay link.
//
// Protocol: hobbit/fpga/esp32_ethrelay/main/relay.h (the C the ESP32 runs);
// design: hobbit/docs/ulx3s_ethernet.md sections 3 and 6.5.  One link
// packet is
//
//     COBS( type | payload | crc32 little-endian ) 0x00
//
// over an 8N1 UART at clksPerBit clocks a bit (25 MHz / 2.5 Mbaud = 10).
// The frame side is the SONIC's frame port (Sonic.bsv FrameByte):
//
//   tx  frames from the SONIC: gathered whole (2 KB), then sent as one
//       0x45 packet: the CRC over 0x45 and the frame, a COBS encoder that
//       scans ahead for the next zero (at most 254 bytes) before each code
//       byte, then 0x00.  A frame over 1518 bytes is dropped and counted.
//       No byte starts while `rts` (the ESP32's RTS, FPGA pin H1) is high.
//   rx  the UART's bytes are decoded as relay_feed (relay.c) does: a
//       streaming COBS decoder, the type byte, a 4-byte delay line that
//       keeps the CRC out of the frame, and at the 0x00 the checks in
//       relay_feed's order (COBS, length >= 5, CRC, type, frame length
//       14..1518).  A 0x45 packet's frame bytes go to the SONIC as they
//       are decoded; its last byte carries `bad` when any check failed, so
//       the SONIC drops it.  Other types are swallowed.
//
// Counters (stats) are relay_dec's: good, bad_crc, bad_cobs, bad_len,
// overflows, bad_type, plus UART framing errors and bytes lost because
// the decoder could not keep up (its input FIFO full).
package EspLink;

import FIFOF    :: *;
import GetPut   :: *;
import RegFile  :: *;
import StmtFSM  :: *;
import BRAMFIFO :: *;
import Sonic    :: *;

export EspLinkStats(..);
export EspLink(..);
export mkEspLink;
export mkEspLink25M;

typedef struct {
  Bit#(16) good; Bit#(16) badCrc; Bit#(16) badCobs; Bit#(16) badLen;
  Bit#(16) overflows; Bit#(16) badType; Bit#(16) framing; Bit#(16) lost;
  Bit#(16) txTooLong;
} EspLinkStats deriving (Bits, Eq, FShow);

interface EspLink;
  interface Put#(FrameByte) tx;       // from the SONIC
  interface Get#(FrameByte) rx;       // to the SONIC
  (* always_ready *) method Bit#(1) txd;
  (* always_ready, always_enabled *) method Action pins(Bit#(1) rxd,
                                                       Bit#(1) rts);
  (* always_ready *) method EspLinkStats stats;
  (* always_ready *) method Bool txIdle;
endinterface

Integer maxFrame = 1518;
Integer maxBody = 1 + 1518 + 4;                 // RELAY_MAX_BODY
Integer maxWire = 1523 + 1523 / 254 + 2;        // RELAY_MAX_WIRE

module mkEspLink#(Integer clksPerBit)(EspLink);
  Bit#(16) cpb = fromInteger(clksPerBit);

  // ------------------------------------------------------------ pins
  Reg#(Bit#(1)) rxd1 <- mkReg(1);
  Reg#(Bit#(1)) rxd2 <- mkReg(1);
  Reg#(Bit#(1)) rts1 <- mkReg(1);
  Reg#(Bit#(1)) rts2 <- mkReg(1);
  Wire#(Bit#(1)) rxdIn <- mkBypassWire;
  Wire#(Bit#(1)) rtsIn <- mkBypassWire;

  rule sync;
    rxd1 <= rxdIn; rxd2 <= rxd1;
    rts1 <= rtsIn; rts2 <= rts1;
  endrule

  // ------------------------------------------------------------ UART TX
  FIFOF#(Bit#(8)) txByteQ <- mkSizedFIFOF(4);
  Reg#(Bit#(10)) txSh <- mkReg('1);
  Reg#(Bit#(4))  txLeft <- mkReg(0);
  Reg#(Bit#(16)) txCnt <- mkReg(0);
  Reg#(Bool)     txBusy <- mkReg(False);

  rule uartTxStart (!txBusy && rts2 == 0);
    txSh <= {1'b1, txByteQ.first, 1'b0};
    txByteQ.deq;
    txLeft <= 9;
    txCnt <= cpb - 1;
    txBusy <= True;
  endrule

  rule uartTxBit (txBusy);
    if (txCnt != 0) txCnt <= txCnt - 1;
    else if (txLeft == 0) begin txBusy <= False; txSh <= '1; end
    else begin
      txSh <= {1'b1, txSh[9:1]};
      txLeft <= txLeft - 1;
      txCnt <= cpb - 1;
    end
  endrule

  // ------------------------------------------------------------ TX framer
  RegFile#(Bit#(11), Bit#(8)) txBuf <- mkRegFileFull;
  Reg#(Bit#(12)) txIn <- mkReg(0);
  Reg#(Bool)     txTooBig <- mkReg(False);
  Reg#(Bit#(32)) txCrcR <- mkReg(crc32Byte('1, 8'h45));
  Reg#(Bool)     txReady <- mkReg(False);
  PulseWire      txSet <- mkPulseWire;
  PulseWire      txClr <- mkPulseWire;
  Reg#(Bit#(16)) txTooLongN <- mkReg(0);

  rule txFlag (txSet || txClr);
    txReady <= txSet;
  endrule

  Reg#(Bit#(12)) total <- mkReg(0);      // body length: n + 5
  Reg#(Bit#(32)) fcs <- mkReg(0);
  Reg#(Bit#(12)) pos <- mkReg(0);
  Reg#(Bit#(9))  kk <- mkReg(0);
  Reg#(Bit#(9))  q <- mkReg(0);
  Reg#(Bool)     scan <- mkReg(False);
  Reg#(Bool)     more <- mkReg(False);

  function Bit#(8) body(Bit#(12) x);
    Bit#(12) n = total - 5;
    Bit#(8) b = 8'h45;
    if (x == 0) b = 8'h45;
    else if (x <= n) b = txBuf.sub(truncate(x - 1));
    else begin
      Bit#(2) y = truncate(x - n - 1);
      b = truncate(fcs >> {y, 3'b0});
    end
    return b;
  endfunction

  Stmt encode = seq
    action
      total <= txIn + 5;
      fcs <= ~txCrcR;
      txIn <= 0;                          // put is held off by txReady
      txCrcR <= crc32Byte('1, 8'h45);
      pos <= 0;
      more <= True;
    endaction
    while (more) seq
      action kk <= 0; scan <= True; endaction
      while (scan) action
        if (kk < 254 && pos + zeroExtend(kk) < total
            && body(pos + zeroExtend(kk)) != 0)
          kk <= kk + 1;
        else scan <= False;
      endaction
      txByteQ.enq(truncate(kk + 1));
      q <= 0;
      while (q < kk) action
        txByteQ.enq(body(pos + zeroExtend(q)));
        q <= q + 1;
      endaction
      action
        if (kk == 254) pos <= pos + 254;
        else if (pos + zeroExtend(kk) == total) more <= False;
        else pos <= pos + zeroExtend(kk) + 1;
      endaction
    endseq
    txByteQ.enq(0);
    txClr.send;
  endseq;
  FSM encFsm <- mkFSM(encode);

  rule encStart (txReady && encFsm.done);
    encFsm.start;
  endrule

  // ------------------------------------------------------------ UART RX
  FIFOF#(Bit#(8)) rxByteQ <- mkSizedFIFOF(16);
  Reg#(Bit#(4))  rxBit <- mkReg(0);       // 0 idle, 1 start, 2..9 data, 10 stop
  Reg#(Bit#(16)) rxCnt <- mkReg(0);
  Reg#(Bit#(8))  rxSh <- mkReg(0);
  Reg#(Bit#(16)) framingN <- mkReg(0);
  Reg#(Bit#(16)) lostN <- mkReg(0);

  rule uartRx;
    Bit#(1) v = rxd2;
    if (rxBit == 0) begin
      if (v == 0) begin rxBit <= 1; rxCnt <= cpb / 2; end
    end
    else if (rxCnt != 0) rxCnt <= rxCnt - 1;
    else if (rxBit == 1) begin
      if (v == 0) begin rxBit <= 2; rxCnt <= cpb - 1; end
      else rxBit <= 0;                    // a glitch, not a start bit
    end
    else if (rxBit <= 9) begin
      rxSh <= {v, rxSh[7:1]};
      rxBit <= rxBit + 1;
      rxCnt <= cpb - 1;
    end
    else begin
      rxBit <= 0;
      if (v == 0) framingN <= framingN + 1;
      if (rxByteQ.notFull) rxByteQ.enq(rxSh);
      else lostN <= lostN + 1;
    end
  endrule

  // ------------------------------------------------------------ RX decoder
  FIFOF#(FrameByte) outQ <- mkSizedBRAMFIFOF(2048);
  Reg#(Bit#(12)) wireN <- mkReg(0);       // encoded bytes of this packet
  Reg#(Bool)     ovf <- mkReg(False);
  Reg#(Bool)     cobsBad <- mkReg(False);
  Reg#(Bit#(8))  rem <- mkReg(0);
  Reg#(Bool)     pendZero <- mkReg(False);
  Reg#(Bool)     started <- mkReg(False);
  Reg#(Bit#(12)) bodyN <- mkReg(0);
  Reg#(Bit#(8))  typ <- mkReg(0);
  Reg#(Bit#(32)) dl <- mkReg(0);          // the last 4 body bytes
  Reg#(Bit#(32)) rcrc <- mkReg('1);
  Reg#(Maybe#(Bit#(8))) held <- mkReg(tagged Invalid);
  Reg#(Bit#(16)) goodN <- mkReg(0);
  Reg#(Bit#(16)) badCrcN <- mkReg(0);
  Reg#(Bit#(16)) badCobsN <- mkReg(0);
  Reg#(Bit#(16)) badLenN <- mkReg(0);
  Reg#(Bit#(16)) ovfN <- mkReg(0);
  Reg#(Bit#(16)) badTypeN <- mkReg(0);

  rule decode;
    Bit#(8) b = rxByteQ.first;
    rxByteQ.deq;
    if (b != 0) begin
      if (wireN == fromInteger(maxWire)) ovf <= True;
      else begin
        wireN <= wireN + 1;
        // the body bytes this wire byte yields: a pending zero, then b
        // unless b is a code byte
        Bool code = rem == 0;
        Bool emitZero = code && started && pendZero;
        Bool emitB = !code;
        Bit#(12) nb = bodyN;
        Bit#(8) t = typ;
        Bit#(32) d = dl;
        Bit#(32) c = rcrc;
        Maybe#(Bit#(8)) h = held;
        Bool bad = cobsBad;
        Maybe#(FrameByte) out = tagged Invalid;
        // at most one of emitZero / emitB is true in one byte
        if (emitZero || emitB) begin
          Bit#(8) x = emitZero ? 0 : b;
          if (nb == fromInteger(maxBody)) bad = True;   // cobs_decode: -1
          else begin
            if (nb == 0) begin t = x; c = crc32Byte('1, x); end
            else begin
              if (nb >= 5) begin
                // the oldest of the 4 held back leaves the delay line
                Bit#(8) leaving = d[7:0];
                c = crc32Byte(c, leaving);
                if (h matches tagged Valid .hb &&& t == 8'h45)
                  out = tagged Valid FrameByte {data: hb, last: False,
                                                bad: False};
                h = tagged Valid leaving;
              end
              d = {x, d[31:8]};
            end
            nb = nb + 1;
          end
        end
        if (code) begin
          rem <= b - 1;
          pendZero <= b != 8'hFF;
          started <= True;
        end
        else rem <= rem - 1;
        if (out matches tagged Valid .o) outQ.enq(o);
        bodyN <= nb; typ <= t; dl <= d; rcrc <= c; held <= h;
        cobsBad <= bad;
      end
    end
    else begin
      // the delimiter: relay_feed's checks, in its order
      Bool empty = wireN == 0 && !ovf;
      Bool good = False;
      if (empty) noAction;
      else if (ovf) ovfN <= ovfN + 1;
      else if (cobsBad || rem != 0) badCobsN <= badCobsN + 1;
      else if (bodyN < 5) badLenN <= badLenN + 1;
      else if (~rcrc != dl) badCrcN <= badCrcN + 1;
      else if (typ == 8'h45) begin
        if (bodyN - 5 < 14 || bodyN - 5 > fromInteger(maxFrame))
          badLenN <= badLenN + 1;
        else begin goodN <= goodN + 1; good = True; end
      end
      else if (typ == 8'h53) goodN <= goodN + 1;
      else badTypeN <= badTypeN + 1;
      if (held matches tagged Valid .hb &&& typ == 8'h45)
        outQ.enq(FrameByte {data: hb, last: True, bad: !good});
      wireN <= 0; ovf <= False; cobsBad <= False; rem <= 0;
      pendZero <= False; started <= False; bodyN <= 0; typ <= 0;
      dl <= 0; rcrc <= '1; held <= tagged Invalid;
    end
  endrule

  // ------------------------------------------------------------ methods
  interface Put tx;
    method Action put(FrameByte fb) if (!txReady);
      Bit#(12) n = txIn;
      Bool big = txTooBig;
      Bit#(32) c = txCrcR;
      if (n == fromInteger(maxFrame)) big = True;
      else begin
        txBuf.upd(truncate(n), fb.data);
        n = n + 1;
        c = crc32Byte(c, fb.data);
      end
      if (fb.last && big) begin
        // too long for a link packet (relay_encode returns 0): dropped
        txTooLongN <= txTooLongN + 1;
        n = 0;
        big = False;
        c = crc32Byte('1, 8'h45);
      end
      else if (fb.last) txSet.send;
      txIn <= n;
      txTooBig <= big;
      txCrcR <= c;
    endmethod
  endinterface

  interface Get rx = toGet(outQ);

  method Bit#(1) txd = txSh[0];
  method Action pins(Bit#(1) rxd, Bit#(1) rts);
    rxdIn <= rxd;
    rtsIn <= rts;
  endmethod
  method EspLinkStats stats = EspLinkStats {
    good: goodN, badCrc: badCrcN, badCobs: badCobsN, badLen: badLenN,
    overflows: ovfN, badType: badTypeN, framing: framingN, lost: lostN,
    txTooLong: txTooLongN};
  method Bool txIdle = !txReady && !txBusy && !txByteQ.notEmpty;
endmodule

// The ULX3S build: 25 MHz, 2.5 Mbaud.
(* synthesize *)
module mkEspLink25M(EspLink);
  EspLink l <- mkEspLink(10);
  return l;
endmodule

endpackage
