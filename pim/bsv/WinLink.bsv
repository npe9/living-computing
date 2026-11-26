// The window host link (mkWinLink): the box's commands down and its answers
// up over a UART, 8N1.  docs/simpos/window_hardware_plan.md §3.4, H6 (its
// RTL half).  ALL OURS: the PSI's display was local to its CPU; this link
// lets a host running kl0 drive the board.  The frame format, the
// receiver's rules and the error codes are frozen in tools/winlink.py's
// header, which is the specification; bsv/run_win_link.sh checks this
// file against it byte for byte.
//
// Structure (the box pattern: each part its own module and rules):
//   mkWinUartRx    the line in: a two-flop synchronizer, the start bit
//                  checked at its middle, 8 data bits LSB first sampled at
//                  their middles, the stop bit checked (a byte with a bad
//                  stop bit is dropped: it shows as a CRC or LEN error)
//   mkWinUartTx    the line out
//   mkWinLinkRx    the frame receiver: hunt for A5, SEQ, LEN, 13 payload
//                  bytes, CRC-16/CCITT-FALSE; commands and error records
//   mkWinLinkTx    the record sender: statuses, a dump's or a read's data
//                  in records of at most 64 words (gathered first, so LEN
//                  is the real count), error records and input event records
//                  (H5/H7s: TYPE 3, WinInput.bsv's records; only between
//                  records, after the box's answers and the errors)
//   mkWinLink      the three behind one Client of the box
// `div` is the clock cycles a bit: 25 for 1 Mbaud on the board's 25 MHz
// (plan §3.4's target; 217 for 115,200), 4 in the bench.
//
// Flow control (OURS): the host keeps at most 8 commands unanswered (it
// sees every answer's SEQ); the link holds 16, so a host that keeps to it
// never overruns the receiver.  A byte arriving into a full queue is
// dropped with a message (simulation): the frame it was in then fails its
// CRC, so the loss is reported up, never drawn.
package WinLink;

import FIFOF::*;
import GetPut::*;
import ClientServer::*;
import Vector::*;
import WinFbBox::*;
import WinInput::*;

function Bit#(16) crc16Byte(Bit#(16) c0, Bit#(8) b);
   Bit#(16) c = c0 ^ (zeroExtend(b) << 8);
   for (Integer i = 0; i < 8; i = i + 1)
      c = (c[15] == 1) ? ((c << 1) ^ 'h1021) : (c << 1);
   return c;
endfunction

// ---------------------------------------------------------------------
interface WinUartRx;
   (* always_ready, always_enabled *) method Action rxd(Bit#(1) b);
   interface Get#(Bit#(8)) bytes;
endinterface

module mkWinUartRx#(Integer div, String name)(WinUartRx);
   Wire#(Bit#(1)) rxW <- mkBypassWire;
   Reg#(Bit#(1)) s1 <- mkReg(1);
   Reg#(Bit#(1)) s2 <- mkReg(1);
   Reg#(Bool) busy <- mkReg(False);
   Reg#(UInt#(16)) cnt <- mkReg(0);
   Reg#(UInt#(4)) n <- mkReg(0);
   Reg#(Bit#(8)) sh <- mkReg(0);
   FIFOF#(Bit#(8)) q <- mkUGSizedFIFOF(8);

   (* fire_when_enabled, no_implicit_conditions *)
   rule sample;
      s1 <= rxW;
      s2 <= s1;
      if (!busy) begin
         if (s2 == 0) begin
            busy <= True; cnt <= fromInteger(div / 2 - 1); n <= 0;
         end
      end
      else if (cnt != 0) cnt <= cnt - 1;
      else begin
         cnt <= fromInteger(div - 1);
         if (n == 0) begin
            if (s2 != 0) busy <= False;          // a glitch, not a start bit
            else n <= 1;
         end
         else if (n <= 8) begin
            sh <= {s2, sh[7:1]};
            n <= n + 1;
         end
         else begin
            busy <= False;
            if (s2 == 1) begin
               if (q.notFull) q.enq(sh);
               else $display("%s: receive queue full, a byte dropped", name);
            end
         end
      end
   endrule

   method Action rxd(Bit#(1) b);
      rxW <= b;
   endmethod
   interface Get bytes;
      method ActionValue#(Bit#(8)) get if (q.notEmpty);
         q.deq;
         return q.first;
      endmethod
   endinterface
endmodule

// ---------------------------------------------------------------------
interface WinUartTx;
   interface Put#(Bit#(8)) bytes;
   (* always_ready *) method Bit#(1) txd;
endinterface

module mkWinUartTx#(Integer div)(WinUartTx);
   FIFOF#(Bit#(8)) q <- mkSizedFIFOF(4);
   Reg#(Bit#(10)) sh <- mkReg('1);
   Reg#(UInt#(4)) n <- mkReg(0);              // bits still to send
   Reg#(UInt#(16)) cnt <- mkReg(0);

   rule load (n == 0);
      sh <= {1'b1, q.first, 1'b0};               // stop, data, start (sent LSB first)
      q.deq;
      n <= 10; cnt <= fromInteger(div - 1);
   endrule
   rule shift (n != 0);
      if (cnt != 0) cnt <= cnt - 1;
      else begin
         sh <= {1'b1, sh[9:1]};
         n <= n - 1;
         cnt <= fromInteger(div - 1);
      end
   endrule

   interface bytes = toPut(q);
   method Bit#(1) txd = (n == 0) ? 1 : sh[0];
endmodule

// ---------------------------------------------------------------------
typedef enum { RHunt, RSeq, RLen, RPay, RCrcH, RCrcL } RxState deriving (Bits, Eq);

typedef struct { Bit#(8) code; Bit#(8) expected; } LinkErr deriving (Bits);
Bit#(8) eCRC = 1;
Bit#(8) eLEN = 2;
Bit#(8) eSEQ = 3;

interface WinLinkRx;
   interface Put#(Bit#(8)) bytes;
   interface Get#(Tuple2#(Bit#(8), WinFbCmd)) cmds;
   interface Get#(LinkErr) errs;
endinterface

module mkWinLinkRx(WinLinkRx);
   FIFOF#(Bit#(8)) inQ <- mkFIFOF;
   FIFOF#(Tuple2#(Bit#(8), WinFbCmd)) cmdQ <- mkSizedFIFOF(16);
   FIFOF#(LinkErr) errQ <- mkSizedFIFOF(4);
   Reg#(RxState) st <- mkReg(RHunt);
   Reg#(Bit#(8)) rSeq <- mkRegU;
   Reg#(Bit#(8)) expSeq <- mkReg(0);
   Reg#(Bit#(16)) crc <- mkRegU;
   Reg#(Bit#(4)) idx <- mkRegU;
   Reg#(Vector#(13, Bit#(8))) pay <- mkRegU;
   Reg#(Bit#(8)) crcHi <- mkRegU;

   rule step;
      Bit#(8) b = inQ.first;
      inQ.deq;
      case (st)
         RHunt: if (b == 'ha5) begin st <= RSeq; crc <= 'hffff; end
         RSeq:  begin rSeq <= b; crc <= crc16Byte(crc, b); st <= RLen; end
         RLen:  if (b != 13) begin
                   errQ.enq(LinkErr { code: eLEN, expected: expSeq });
                   st <= RHunt;
                end
                else begin crc <= crc16Byte(crc, b); idx <= 0; st <= RPay; end
         RPay:  begin
                   Vector#(13, Bit#(8)) p = pay;
                   p[idx] = b;
                   pay <= p;
                   crc <= crc16Byte(crc, b);
                   idx <= idx + 1;
                   if (idx == 12) st <= RCrcH;
                end
         RCrcH: begin crcHi <= b; st <= RCrcL; end
         RCrcL: begin
                   st <= RHunt;
                   if ({crcHi, b} != crc)
                      errQ.enq(LinkErr { code: eCRC, expected: expSeq });
                   else begin
                      if (rSeq != expSeq) errQ.enq(LinkErr { code: eSEQ, expected: expSeq });
                      Vector#(6, Bit#(16)) a = newVector;
                      for (Integer k = 0; k < 6; k = k + 1)
                         a[k] = {pay[1 + 2 * k], pay[2 + 2 * k]};
                      cmdQ.enq(tuple2(rSeq, WinFbCmd { op: pay[0], a: a }));
                      expSeq <= rSeq + 1;
                   end
                end
      endcase
   endrule

   interface bytes = toPut(inQ);
   interface cmds = toGet(cmdQ);
   interface errs = toGet(errQ);
endmodule

// ---------------------------------------------------------------------
typedef enum { THdr, TData, TEvt, TCrcH, TCrcL } TxPhase deriving (Bits, Eq);

interface WinLinkTx;
   interface Put#(Bit#(8)) seqs;              // the SEQ of each command sent to the box
   interface Put#(WinFbRsp) rsps;             // the box's answers
   interface Put#(LinkErr) errs;
   interface Put#(WinEvent) events;
   interface Get#(Bit#(8)) bytes;
endinterface

module mkWinLinkTx(WinLinkTx);
   FIFOF#(Bit#(8)) seqQ <- mkSizedFIFOF(16);
   FIFOF#(WinFbRsp) rspQ <- mkFIFOF;
   FIFOF#(LinkErr) errQ <- mkFIFOF;
   FIFOF#(WinEvent) evQ <- mkFIFOF;
   FIFOF#(Bit#(8)) outQ <- mkFIFOF;
   Reg#(Vector#(10, Bit#(8))) evB <- mkRegU;   // an event record's payload
   Reg#(UInt#(4)) eI <- mkRegU;
   Reg#(Bit#(8)) evSeq <- mkReg(0);           // event records counted mod 256

   Reg#(Bool) busy <- mkReg(False);           // inside a record
   Reg#(TxPhase) ph <- mkRegU;
   Reg#(Vector#(6, Bit#(8))) hdr <- mkRegU;   // the record's first bytes
   Reg#(UInt#(3)) hN <- mkRegU;               // how many
   Reg#(UInt#(3)) hI <- mkRegU;
   Reg#(Bool) isData <- mkRegU;
   Reg#(Bool) isEvt <- mkReg(False);
   Reg#(UInt#(7)) wLeft <- mkRegU;            // data words still to send
   // a data record's words are gathered first (at most 64), so that its
   // LEN is known when the header goes out: a read (prim a) answers any
   // number of words, not a multiple of 64 (before 2026-11-26 every record
   // claimed 64 and a short read took the next answer's words)
   FIFOF#(Bit#(16)) dBuf <- mkSizedFIFOF(64);
   Reg#(UInt#(7)) dCnt <- mkReg(0);           // words in dBuf
   Reg#(Bool) loByte <- mkRegU;
   Reg#(Bit#(16)) crc <- mkRegU;

   function Action begin6(Vector#(6, Bit#(8)) h, UInt#(3) cnt, Bool d, Bool ev) =
      action
         busy <= True; ph <= THdr; hdr <= h; hN <= cnt; hI <= 0; isData <= d; isEvt <= ev;
         loByte <= False; crc <= 'hffff;
      endaction;

   // gather the box's data words, outside a data record, up to 64
   rule gather (!(busy && isData) && rspQ.first.isData && dCnt < 64);
      dBuf.enq(rspQ.first.data); rspQ.deq;
      dCnt <= dCnt + 1;
   endrule

   // a new record: the box's answer first, else an error.  A data record
   // goes when 64 words are gathered or the answer's data has ended (its
   // status is next); gather and startData are never enabled together.
   (* descending_urgency = "startData, gather" *)
   rule startData (!busy && dCnt != 0 && (dCnt == 64 || !rspQ.first.isData));
      begin6(unpack({8'h0, 8'h0, {1'b0, pack(dCnt)} << 1, 8'd1, seqQ.first, 8'h5a}), 4, True, False);
      wLeft <= dCnt; dCnt <= 0;
   endrule
   rule startStatus (!busy && dCnt == 0 && !rspQ.first.isData);
      WinFbRsp r = rspQ.first;
      rspQ.deq; seqQ.deq;
      begin6(unpack({8'h0, r.status, 8'd1, 8'd0, seqQ.first, 8'h5a}), 5, False, False);
   endrule
   (* descending_urgency = "startData, startStatus, startErr, startEvt" *)
   rule startErr (!busy);
      LinkErr e = errQ.first;
      errQ.deq;
      begin6(unpack({e.expected, e.code, 8'd2, 8'd2, e.expected, 8'h5a}), 6, False, False);
   endrule
   rule startEvt (!busy);
      WinEvent e = evQ.first;
      evQ.deq;
      begin6(unpack({8'h0, 8'h0, 8'd10, 8'd3, evSeq, 8'h5a}), 4, False, True);
      evB <= unpack({e.t[7:0], e.t[15:8], e.flags, e.c[7:0], e.c[15:8], e.b[7:0], e.b[15:8],
                     e.a[7:0], e.a[15:8], e.kind});
      eI <= 0; evSeq <= evSeq + 1;
   endrule

   rule sendHdr (busy && ph == THdr);
      Bit#(8) b = hdr[hI];
      outQ.enq(b);
      if (hI != 0) crc <= crc16Byte(crc, b);
      hI <= hI + 1;
      if (hI + 1 == hN) ph <= isData ? TData : (isEvt ? TEvt : TCrcH);
   endrule
   rule sendData (busy && ph == TData);
      Bit#(16) w = dBuf.first;
      Bit#(8) b = loByte ? w[7:0] : w[15:8];
      outQ.enq(b);
      crc <= crc16Byte(crc, b);
      loByte <= !loByte;
      if (loByte) begin
         dBuf.deq;
         wLeft <= wLeft - 1;
         if (wLeft == 1) ph <= TCrcH;
      end
   endrule
   rule sendEvt (busy && ph == TEvt);
      Bit#(8) b = evB[eI];
      outQ.enq(b);
      crc <= crc16Byte(crc, b);
      eI <= eI + 1;
      if (eI == 9) ph <= TCrcH;
   endrule
   rule sendCrcH (busy && ph == TCrcH);
      outQ.enq(crc[15:8]); ph <= TCrcL;
   endrule
   rule sendCrcL (busy && ph == TCrcL);
      outQ.enq(crc[7:0]); busy <= False;
   endrule

   interface seqs = toPut(seqQ);
   interface rsps = toPut(rspQ);
   interface errs = toPut(errQ);
   interface events = toPut(evQ);
   interface bytes = toGet(outQ);
endmodule

// ---------------------------------------------------------------------
interface WinLink;
   (* always_ready, always_enabled *) method Action rxd(Bit#(1) b);
   (* always_ready *) method Bit#(1) txd;
   interface Client#(WinFbCmd, WinFbRsp) box;
   interface Put#(WinEvent) events;           // up as TYPE 3 records
endinterface

module mkWinLink#(Integer div)(WinLink);
   WinUartRx urx <- mkWinUartRx(div, "WinLink");
   WinUartTx utx <- mkWinUartTx(div);
   WinLinkRx lrx <- mkWinLinkRx;
   WinLinkTx ltx <- mkWinLinkTx;
   FIFOF#(WinFbCmd) toBox <- mkFIFOF;

   rule rxBytes;
      let b <- urx.bytes.get;
      lrx.bytes.put(b);
   endrule
   rule command;
      match {.s, .c} <- lrx.cmds.get;
      toBox.enq(c);
      ltx.seqs.put(s);
   endrule
   rule errors;
      let e <- lrx.errs.get;
      ltx.errs.put(e);
   endrule
   rule txBytes;
      let b <- ltx.bytes.get;
      utx.bytes.put(b);
   endrule

   method Action rxd(Bit#(1) b) = urx.rxd(b);
   method Bit#(1) txd = utx.txd;
   interface Client box;
      interface Get request = toGet(toBox);
      interface Put response = ltx.rsps;
   endinterface
   interface events = ltx.events;
endmodule

endpackage
