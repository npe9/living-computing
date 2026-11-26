// The window box's memory stages (H3 follow-up, 2026-11-25).  OURS.
// docs/simpos/window_hardware_plan.md §2.4, §5.1.
//
// mkWinMemPipe: a pipelined read/write front for one RAM port, so that
// several reads are in flight (the idiomatic-Bluespec request/response
// stage of mkFBox's and Piccolo's memory paths, not an inlined wait).
//
//   read(p, addr)   a read whose word goes to response port p (0 or 1);
//                   allowed when canRead(p): CREDITS.  A port's credit
//                   counts its reads in flight plus its words queued, and
//                   is at most `depth`, the depth of its response FIFO,
//                   so a word coming out of the RAM always finds room
//                   (the RAM cannot stall).
//   write(addr, d)  a write; no credit.
//   rsp[p]          the words of port p's reads, in issue order.
//
// One put a cycle: read and write conflict (they are the RAM's one port).
// The RAM's word is valid exactly `lat` cycles after its put and only for
// that cycle: the next put (a read or a write) changes it (for the frame,
// WinFrame.bsv's selA and every bank's output).  So a tag (the response
// port) walks a `lat`-deep shift register beside the RAM, and the word is
// captured into the port's FIFO in the cycle its tag comes out.  A word
// is thus first visible to a consumer lat + 1 cycles after its read.
//
// Two response ports let two readers share one RAM without having to
// consume in each other's order: the blit's source stream (port 0) and
// the read-modify-write stage's destination reads (port 1) both read the
// frame during a frame-to-frame copy.  A port's words are in that port's
// issue order; the two ports are independent.
//
// Self-checks (simulation): a read without a credit, a capture into a
// full FIFO (a lost word) and a dequeue of an empty port stop the run.
//
// mkWinPendQ: the read-modify-write stage's queue of writes not yet made,
// 4 deep, with `has(addr)`: an item that reads a word must wait while an
// earlier write to that word is still in the queue (a horizontal run of
// line dots, or a wide pen, reads the word its previous dots write).
package WinMemPipe;

import BRAMCore::*;
import FIFOF::*;
import Vector::*;

interface WinRspPort;
   method Bool notEmpty;
   method Bit#(16) first;
   method Action deq;
endinterface

interface WinMemPipe;
   method Bool canRead(Bit#(1) p);
   method Action read(Bit#(1) p, Bit#(20) addr);
   method Action write(Bit#(20) addr, Bit#(16) d);
   interface Vector#(2, WinRspPort) rsp;
endinterface

// the deepest RAM latency the shift register is built for
typedef 4 WinPipeMaxLat;

module mkWinMemPipe#(BRAM_PORT#(a, Bit#(16)) mem, Integer lat, Integer depth, String name)(WinMemPipe)
   provisos (Bits#(a, na), Add#(na, _x, 20));
   if (lat < 1 || lat > valueOf(WinPipeMaxLat) || depth < 1 || depth > 15)
      error("mkWinMemPipe: latency 1..4 and depth 1..15 only");

   Vector#(2, FIFOF#(Bit#(16))) q <- replicateM(mkUGSizedFIFOF(depth));
   Vector#(2, Reg#(UInt#(4))) cnt <- replicateM(mkReg(0));
   Vector#(2, PulseWire) dqP <- replicateM(mkPulseWire);
   RWire#(Bit#(1)) rdTag <- mkRWire;
   Vector#(WinPipeMaxLat, Reg#(Maybe#(Bit#(1)))) stage <- replicateM(mkReg(tagged Invalid));

   (* fire_when_enabled, no_implicit_conditions *)
   rule step;
      stage[0] <= rdTag.wget;
      for (Integer i = 1; i < lat; i = i + 1) stage[i] <= stage[i - 1];
      if (stage[lat - 1] matches tagged Valid .p)
         for (Integer i = 0; i < 2; i = i + 1)
            if (p == fromInteger(i)) begin
               if (!q[i].notFull) begin
                  $display("%s: response port %0d overflow (a word lost)", name, i);
                  $finish(1);
               end
               q[i].enq(mem.read);
            end
      for (Integer i = 0; i < 2; i = i + 1) begin
         UInt#(4) inc = (rdTag.wget == tagged Valid fromInteger(i)) ? 1 : 0;
         UInt#(4) dec = dqP[i] ? 1 : 0;
         cnt[i] <= cnt[i] + inc - dec;
      end
   endrule

   function WinRspPort mkPort(Integer i);
      return (interface WinRspPort;
                 method Bool notEmpty = q[i].notEmpty;
                 method Bit#(16) first = q[i].first;
                 method Action deq;
                    if (!q[i].notEmpty) begin
                       $display("%s: dequeue of empty response port %0d", name, i);
                       $finish(1);
                    end
                    q[i].deq;
                    dqP[i].send;
                 endmethod
              endinterface);
   endfunction

   method Bool canRead(Bit#(1) p) = cnt[p] < fromInteger(depth);
   method Action read(Bit#(1) p, Bit#(20) addr);
      if (!(cnt[p] < fromInteger(depth))) begin
         $display("%s: read on port %0d without a credit", name, p);
         $finish(1);
      end
      mem.put(False, unpack(truncate(addr)), ?);
      rdTag.wset(p);
   endmethod
   method Action write(Bit#(20) addr, Bit#(16) d);
      mem.put(True, unpack(truncate(addr)), d);
   endmethod
   interface rsp = genWith(mkPort);
endmodule

// ---------------------------------------------------------------------
interface WinPendQ#(type t);
   method Action enq(t x);
   method t first;
   method Action deq;
   method Bool has(Bit#(20) addr);
endinterface

module mkWinPendQ#(function Bit#(20) key(t x))(WinPendQ#(t))
   provisos (Bits#(t, nt));
   Vector#(4, Reg#(t)) d <- replicateM(mkRegU);
   Vector#(4, Reg#(Bool)) v <- replicateM(mkReg(False));
   Reg#(Bit#(2)) hd <- mkReg(0);
   Reg#(Bit#(2)) tl <- mkReg(0);
   RWire#(t) enqW <- mkRWire;
   PulseWire deqW <- mkPulseWire;

   (* fire_when_enabled, no_implicit_conditions *)
   rule update;
      Vector#(4, Bool) nv = readVReg(v);
      if (enqW.wget matches tagged Valid .x) begin
         d[tl] <= x;
         nv[tl] = True;
         tl <= tl + 1;
      end
      if (deqW) begin
         nv[hd] = False;
         hd <= hd + 1;
      end
      writeVReg(v, nv);
   endrule

   function Bool hit(Bit#(20) a, Integer i) = v[i] && key(d[i]) == a;

   method Action enq(t x) if (!v[tl]);
      enqW.wset(x);
   endmethod
   method t first if (v[hd]) = d[hd];
   method Action deq if (v[hd]);
      deqW.send;
   endmethod
   method Bool has(Bit#(20) a);
      Bool r = False;
      for (Integer i = 0; i < 4; i = i + 1) r = r || hit(a, i);
      return r;
   endmethod
endmodule

endpackage
