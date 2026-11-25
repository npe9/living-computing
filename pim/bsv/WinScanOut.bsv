// The window scan-out (mkWinScanOut): video timing, the 1-bit pixel
// fetch from the framebuffer's port B, the hardware cursor, and the TMDS
// (DVI) encoders.  docs/simpos/window_hardware_plan.md H2 (§2.2, §2.6).
//
// OURS SCAFFOLDING, NOT A RECONSTRUCTION.  The PSI's CRT controller is
// not documented (plan §1.1, §1.2).  The Python reference is
// psi/winscan.py (modes, timing model, view, cursor; its header is the
// specification of everything here) with psi/wintmds.py (the TMDS
// encoder, transcribed from DVI 1.0 Fig. 3-5 p29; its header cites the
// pages).  bsv/run_win_tb.sh decodes this module's characters in Python
// and compares them with those references.
//
// Sourced facts: the TMDS encode algorithm and the four control
// characters (DVI 1.0 Fig. 3-5 p29, written there q_out[0:9], bit 0
// first: here they are [9:0] values, so 00 is 'b1101010100); channel 0
// carries C0 = HSYNC and C1 = VSYNC, channels 1 and 2 CTL0-3 held low
// (Fig. 3-2 p26, §3.2.1); the mode timings of modes 0, 1, 3 (SECONDARY:
// Linux drm_edid.c, see psi/winscan.py).  Mode 2's timing is OURS (the
// plan's).  The frame's bit order (MSB = leftmost dot) and 1 = black
// are psi/winfb.py's.
//
// The modes (winMode; one table, chosen at start by the system side):
//   0  1920x1080@30 (CEA-861 VIC 34), the frame letterboxed 1:1 at (320,28)
//   1  1280x1024@60 (VESA DMT 0x23) -- 108 MHz, beyond the ECP5 PLL (plan)
//   2  1280x1024 reduced blanking @49.4 (OURS: 1440 x 1054 at 75 MHz)
//   3  640x480@60 (DMT 0x04), the frame reduced 2:1 by a 2x2 OR, from
//      frame row panY (OURS: 2:1 gives 512 rows for 480 lines)
// A custom timing (any WinVideoMode) is accepted too; the benches use
// small ones.  Requirements: front porch, sync and back porch >= 1 each.
//
// Structure (the idiomatic-Bluespec pattern: each stage its own module
// with an interface; one orchestration rule moves the bundles):
//   mkWinTiming   the lead position counters and the sync/DE/window
//                 signals at the lead position;
//   mkWinFetch    at the first dot of each 16-dot (1:1) or 8-pixel (2:1)
//                 group in the window, reads its word (2:1: its two
//                 rows' words) on the box's scan port; the words go into
//                 a small FIFO that the display stage drains, one entry
//                 per group;
//   mkWinCursor   the 8 shapes of 16 x 16 (mask, image) and the position;
//                 the system side writes a pending position that is
//                 latched at the frame start (plan §5.2);
//   a 16-stage delay line (in the orchestration rule) carries the lead
//                 signals to the display stage, which composes the pixel
//                 (frame dot, cursor, border) and feeds
//   mkWinTmdsEnc  x 3, the DVI encoder (a stateful box: the running
//                 disparity), one per channel.
// The pipeline is fixed-rate (a DVI sink cannot stall), so the stages
// are registers, not FIFOs, except the word queue, which absorbs the
// fetch/display distance.  From lead to characters is 17 clocks.
//
// mkWinTmdsSer, below, is the 10:1 serializer in the shift-clock domain;
// bsv/WinTmdsSerTb.bsv runs it at a 5:1 clock relation in Bluesim.  The
// scan-out itself and the box's port B run on one clock in
// WinScanOutTb, so the DP16KD's system-to-pixel crossing is H3's.
//
// Unimplemented cases fail loud: a word-queue overflow or underflow, or
// a start less than 17 clocks after a stop (the pipeline drains itself
// in that time), stops the simulation.
package WinScanOut;

import Vector::*;
import RegFile::*;
import FIFOF::*;
import WinFbBox::*;

typedef struct {
   Bit#(12) ha; Bit#(12) hf; Bit#(12) hs; Bit#(12) hb;
   Bit#(11) va; Bit#(11) vf; Bit#(11) vs; Bit#(11) vb;
   Bool hpos; Bool vpos;                 // True: the sync pulse is high
   Bit#(12) x0; Bit#(11) y0;             // the window in the active area
   Bit#(12) fw; Bit#(11) fh;             //   (display pixels)
   Bool half;                            // the 2:1 reduction
} WinVideoMode deriving (Bits, Eq, FShow);

function WinVideoMode winMode(Bit#(2) m);
   case (m)
      0: return WinVideoMode { ha: 1920, hf: 88, hs: 44, hb: 148,
                               va: 1080, vf: 4, vs: 5, vb: 36,
                               hpos: True, vpos: True,
                               x0: 320, y0: 28, fw: 1280, fh: 1024, half: False };
      1: return WinVideoMode { ha: 1280, hf: 48, hs: 112, hb: 248,
                               va: 1024, vf: 1, vs: 3, vb: 38,
                               hpos: True, vpos: True,
                               x0: 0, y0: 0, fw: 1280, fh: 1024, half: False };
      2: return WinVideoMode { ha: 1280, hf: 48, hs: 32, hb: 80,
                               va: 1024, vf: 3, vs: 7, vb: 20,
                               hpos: True, vpos: False,
                               x0: 0, y0: 0, fw: 1280, fh: 1024, half: False };
      default: return WinVideoMode { ha: 640, hf: 16, hs: 96, hb: 48,
                               va: 480, vf: 10, vs: 2, vb: 33,
                               hpos: False, vpos: False,
                               x0: 0, y0: 0, fw: 640, fh: 480, half: True };
   endcase
endfunction

// the signals of the lead position
typedef struct {
   Bool de; Bool hsA; Bool vsA;          // DE; the syncs active (not levels)
   Bool inWin;                           // an active pixel in the window
   Bool lineEnd;                         // the last active pixel of a line
   Bit#(12) u; Bit#(11) v;               // window coordinates (wrapping)
   Bool fstart;                          // the frame's first pixel
} WinLead deriving (Bits);

typedef struct {
   Bool start;
   Vector#(3, Bit#(10)) sym;             // channel 0 (blue), 1, 2 (red)
} WinTmdsOut deriving (Bits);

// ======================================================================
interface WinTiming;
   method Action start(WinVideoMode m);
   method Action stop;
   method Action step;
   method WinVideoMode mode;
   method WinLead lead;
endinterface

module mkWinTiming(WinTiming);
   Reg#(WinVideoMode) t <- mkReg(winMode(0));
   Reg#(Bool) run <- mkReg(False);
   Reg#(Bit#(12)) hx <- mkReg(0);
   Reg#(Bit#(11)) vy <- mkReg(0);

   Bit#(12) ht = t.ha + t.hf + t.hs + t.hb;
   Bit#(11) vt = t.va + t.vf + t.vs + t.vb;

   method Action start(WinVideoMode m);
      t <= m; run <= True; hx <= 0; vy <= 0;
   endmethod
   method Action stop;
      run <= False;
   endmethod
   method Action step;
      if (run) begin
         if (hx == ht - 1) begin
            hx <= 0;
            vy <= (vy == vt - 1) ? 0 : vy + 1;
         end
         else hx <= hx + 1;
      end
   endmethod
   method WinVideoMode mode = t;
   method WinLead lead;
      Bool de = run && hx < t.ha && vy < t.va;
      Bit#(12) u = hx - t.x0;
      Bit#(11) v = vy - t.y0;
      return WinLead {
         de: de,
         hsA: run && hx >= t.ha + t.hf && hx < t.ha + t.hf + t.hs,
         vsA: run && vy >= t.va + t.vf && vy < t.va + t.vf + t.vs,
         inWin: de && u < t.fw && v < t.fh,
         lineEnd: hx == t.ha - 1,
         u: u, v: v,
         fstart: run && hx == 0 && vy == 0 };
   endmethod
endmodule

// ======================================================================
interface WinFetch;
   method Action lead(WinVideoMode t, Bit#(7) panX, Bit#(10) panY, WinLead l);
   method Bool ready;
   method Tuple2#(Bit#(16), Bit#(16)) first;
   method Action deq;
endinterface

module mkWinFetch#(WinFbScan fb)(WinFetch);
   FIFOF#(Tuple2#(Bit#(16), Bit#(16))) q <- mkUGSizedFIFOF(4);
   Reg#(Bit#(2)) ph <- mkReg(0);          // 0 idle; 1 row A answered; 2 row B answered
   Reg#(Bool) vA <- mkReg(False);         // the read was made (else the word is 0)
   Reg#(Bool) vB <- mkReg(False);
   Reg#(Bit#(16)) wA <- mkReg(0);
   Reg#(Bit#(12)) rowB <- mkReg(0);
   Reg#(Bit#(12)) colR <- mkReg(0);

   function Bool readable(Bit#(12) r, Bit#(12) c) = r < 1024 && c < 80;
   function Bit#(17) addrOf(Bit#(12) r, Bit#(12) c) =
      zeroExtend(r) * 80 + zeroExtend(c);
   function Action push(Bit#(16) a, Bit#(16) b);
      action
         if (!q.notFull) begin
            $display("WinScanOut: word queue overflow");
            $finish(1);
         end
         q.enq(tuple2(a, b));
      endaction
   endfunction

   method Action lead(WinVideoMode t, Bit#(7) panX, Bit#(10) panY, WinLead l);
      Bit#(4) k = t.half ? zeroExtend(l.u[2:0]) : l.u[3:0];
      Bit#(12) col = (t.half ? l.u >> 3 : l.u >> 4) + zeroExtend(panX);
      Bit#(12) rA = (t.half ? zeroExtend(l.v) << 1 : zeroExtend(l.v)) + zeroExtend(panY);
      if (ph == 1) begin
         Bit#(16) a = vA ? fb.read : 0;
         if (t.half) begin
            wA <= a;
            Bool ok = readable(rowB, colR);
            vB <= ok;
            if (ok) fb.put(addrOf(rowB, colR));
            ph <= 2;
         end
         else begin
            push(a, 0);
            ph <= 0;
         end
      end
      else if (ph == 2) begin
         push(wA, vB ? fb.read : 0);
         ph <= 0;
      end
      else if (k == 0 && l.inWin) begin
         // the first pixel of a group in the window: its word(s)
         Bool ok = readable(rA, col);
         vA <= ok;
         if (ok) fb.put(addrOf(rA, col));
         rowB <= rA + 1; colR <= col;
         ph <= 1;
      end
   endmethod
   method Bool ready = q.notEmpty;
   method Tuple2#(Bit#(16), Bit#(16)) first = q.first;
   method Action deq = q.deq;
endmodule

// ======================================================================
typedef struct {
   Bool on; Bit#(12) x; Bit#(11) y; Bit#(3) s;
} WinCursorPos deriving (Bits);

interface WinCursor;
   method Action shape(Bit#(3) s, Bit#(4) r, Bit#(16) mask, Bit#(16) image);
   method Action place(Bool on, Bit#(12) x, Bit#(11) y, Bit#(3) s);
   method Action frameStart;
   // (covered with mask 1, image dot) at window pixel (u, v); at a frame
   // start the pending position is the one that counts
   method Tuple2#(Bool, Bool) at(Bool fs, Bit#(12) u, Bit#(11) v);
endinterface

module mkWinCursor(WinCursor);
   RegFile#(Bit#(7), Bit#(32)) planes <- mkRegFileFull;   // mask << 16 | image
   Reg#(WinCursorPos) pend <- mkReg(WinCursorPos { on: False, x: 0, y: 0, s: 0 });
   Reg#(WinCursorPos) act <- mkReg(WinCursorPos { on: False, x: 0, y: 0, s: 0 });
   // a write from the system side lands after this cycle's pixel
   RWire#(WinCursorPos) placeW <- mkRWire;
   rule commit (placeW.wget matches tagged Valid .p);
      pend <= p;
   endrule

   method Action shape(Bit#(3) s, Bit#(4) r, Bit#(16) mask, Bit#(16) image);
      planes.upd({s, r}, {mask, image});
   endmethod
   method Action place(Bool on, Bit#(12) x, Bit#(11) y, Bit#(3) s);
      placeW.wset(WinCursorPos { on: on, x: x, y: y, s: s });
   endmethod
   method Action frameStart;
      act <= pend;
   endmethod
   method Tuple2#(Bool, Bool) at(Bool fs, Bit#(12) u, Bit#(11) v);
      WinCursorPos c = fs ? pend : act;
      Bit#(12) du = u - c.x;
      Bit#(11) dv = v - c.y;
      Bool hit = c.on && du < 16 && dv < 16;
      Bit#(32) row = planes.sub({c.s, dv[3:0]});
      Bit#(5) i = 15 - zeroExtend(du[3:0]);
      return tuple2(hit && row[16 + i] == 1, row[i] == 1);
   endmethod
endmodule

// ======================================================================
// The TMDS encoder of DVI 1.0 Fig. 3-5 p29 (psi/wintmds.py `encode` is
// the same figure in Python).  put registers one character; sym is it.
interface WinTmdsEnc;
   method Action put(Bool de, Bit#(2) c, Bit#(8) d);
   method Bit#(10) sym;
endinterface

module mkWinTmdsEnc(WinTmdsEnc);
   Reg#(Bit#(10)) q <- mkReg('b1101010100);
   Reg#(Int#(6)) cnt <- mkReg(0);

   method Action put(Bool de, Bit#(2) c, Bit#(8) d);
      if (!de) begin
         cnt <= 0;
         case (c)
            0: q <= 'b1101010100;        // q_out[0:9] = 0010101011
            1: q <= 'b0010101011;        //              1101010100
            2: q <= 'b0101010100;        //              0010101010
            3: q <= 'b1010101011;        //              1101010101
         endcase
      end
      else begin
         UInt#(4) nd = countOnes(d);
         Bool xn = nd > 4 || (nd == 4 && d[0] == 0);
         Bit#(8) qm = 0;
         qm[0] = d[0];
         for (Integer i = 1; i < 8; i = i + 1)
            qm[i] = xn ? ~(qm[i - 1] ^ d[i]) : (qm[i - 1] ^ d[i]);
         Bit#(1) qm8 = xn ? 0 : 1;
         Int#(6) ones = unpack(zeroExtend(pack(countOnes(qm))));
         Int#(6) bal = ones - (8 - ones);           // N1 - N0 of q_m[0:7]
         if (cnt == 0 || bal == 0) begin
            q <= {~qm8, qm8, (qm8 == 1) ? qm : ~qm};
            cnt <= (qm8 == 0) ? cnt - bal : cnt + bal;
         end
         else if ((cnt > 0 && bal > 0) || (cnt < 0 && bal < 0)) begin
            q <= {1'b1, qm8, ~qm};
            cnt <= cnt + ((qm8 == 1) ? 2 : 0) - bal;
         end
         else begin
            q <= {1'b0, qm8, qm};
            cnt <= cnt - ((qm8 == 0) ? 2 : 0) + bal;
         end
      end
   endmethod
   method Bit#(10) sym = q;
endmodule

// ======================================================================
// The 10:1 serializer of the plan's §2.2/§5.2: four lanes (channels 0-2
// and the clock) at five shift clocks a pixel, two bits a shift clock
// into an ODDRX1F (D0 goes out first, then D1; plan Appendix A and
// flute-lx50's lx49 serializer).  Clocked by the SHIFT clock; it reads
// the pixel domain's three characters through `w`, a crossing without
// a synchronizer (mkNullCrossingWire in the bench), which is right only
// because both clocks come from one PLL VCO and the word is sampled
// (h <= w) on a phase where it is stable (plan §5.2).  Bit 0 of each
// character is sent first (DVI 1.0 §3.2.3 p30).  The clock lane sends
// 'b0000011111 (five ones, then five zeros: one period a character).
// The one-hot phase and the per-lane load flags set a clock early are
// the skeleton's fix for its 225 MHz mod-5 counter (plan §5.1).
interface WinTmdsSer;
   method Vector#(4, Bit#(2)) pins;      // per lane {D1, D0}
endinterface

module mkWinTmdsSer#(ReadOnly#(Vector#(3, Bit#(10))) w)(WinTmdsSer);
   Reg#(Bit#(5)) ph <- mkReg(1);
   Vector#(4, Reg#(Bool)) ld <- replicateM(mkReg(False));
   Vector#(3, Reg#(Bit#(10))) h <- replicateM(mkReg(0));
   Vector#(4, Reg#(Bit#(10))) sh <- replicateM(mkReg(0));

   (* fire_when_enabled, no_implicit_conditions *)
   rule shift;
      ph <= {ph[3:0], ph[4]};
      for (Integer i = 0; i < 4; i = i + 1) ld[i] <= ph[3] == 1;
      if (ph[2] == 1)
         for (Integer i = 0; i < 3; i = i + 1) h[i] <= w[i];
      for (Integer i = 0; i < 3; i = i + 1)
         sh[i] <= ld[i] ? h[i] : sh[i] >> 2;
      sh[3] <= ld[3] ? 'b0000011111 : sh[3] >> 2;
   endrule

   method Vector#(4, Bit#(2)) pins;
      function Bit#(2) two(Reg#(Bit#(10)) r) = r[1:0];
      return map(two, sh);
   endmethod
endmodule

// ======================================================================
interface WinScanOut;
   method Action start(WinVideoMode m, Bit#(7) panX, Bit#(10) panY);
   method Action stop;
   method Action cursorShape(Bit#(3) s, Bit#(4) r, Bit#(16) mask, Bit#(16) image);
   method Action cursorPlace(Bool on, Bit#(12) x, Bit#(11) y, Bit#(3) s);
   method WinTmdsOut out;
endinterface

typedef struct {
   Bool de; Bool hsA; Bool vsA; Bool inWin; Bool last;
   Bit#(4) k; Bool cm; Bool ci; Bool fstart;
} WinDl deriving (Bits);

typedef 16 DlDepth;

module mkWinScanOut#(WinFbScan fb)(WinScanOut);
   WinTiming timing <- mkWinTiming;
   WinFetch fetch <- mkWinFetch(fb);
   WinCursor cursor <- mkWinCursor;
   Vector#(3, WinTmdsEnc) enc <- replicateM(mkWinTmdsEnc);

   WinDl blank = WinDl { de: False, hsA: False, vsA: False, inWin: False,
                         last: False, k: 0, cm: False, ci: False, fstart: False };
   Vector#(DlDepth, Reg#(WinDl)) dl <- replicateM(mkReg(blank));
   Reg#(Bool) outStart <- mkReg(False);
   Reg#(Bit#(7)) panX <- mkReg(0);
   Reg#(Bit#(10)) panY <- mkReg(0);

   RWire#(Tuple3#(WinVideoMode, Bit#(7), Bit#(10))) startW <- mkRWire;
   PulseWire stopW <- mkPulseWire;

   // the orchestration rule: one pixel clock
   (* fire_when_enabled, no_implicit_conditions *)
   rule tick;
      WinVideoMode t = timing.mode;
      WinLead l = timing.lead;

      // the lead stage: counters, fetch, cursor
      if (startW.wget matches tagged Valid {.m, .px, .py}) begin
         timing.start(m);
         panX <= px; panY <= py;
         if (fetch.ready) begin
            $display("WinScanOut: start before the last frame's words drained");
            $finish(1);
         end
      end
      else begin
         if (stopW) timing.stop;
         else timing.step;
         fetch.lead(t, panX, panY, l);
      end
      if (l.fstart) cursor.frameStart;
      match {.cm, .ci} = cursor.at(l.fstart, l.u, l.v);
      Bit#(4) k = t.half ? zeroExtend(l.u[2:0]) : l.u[3:0];
      Bit#(4) gl = t.half ? 7 : 15;
      dl[0] <= WinDl { de: l.de, hsA: l.hsA, vsA: l.vsA, inWin: l.inWin,
                       last: l.inWin && (k == gl || l.u == t.fw - 1 || l.lineEnd),
                       k: k, cm: l.inWin && cm, ci: ci, fstart: l.fstart };
      for (Integer i = 1; i < valueOf(DlDepth); i = i + 1)
         dl[i] <= dl[i - 1];

      // the display stage
      WinDl e = dl[valueOf(DlDepth) - 1];
      match {.wa, .wb} = fetch.first;
      Bit#(4) i0 = 15 - e.k;
      Bit#(4) j0 = 15 - {e.k[2:0], 1'b0};
      Bit#(4) j1 = 14 - {e.k[2:0], 1'b0};
      Bool dot = t.half ? (wa[j0] | wa[j1] | wb[j0] | wb[j1]) == 1 : wa[i0] == 1;
      if (e.inWin) begin
         if (!fetch.ready) begin
            $display("WinScanOut: word queue underflow");
            $finish(1);
         end
         if (e.last) fetch.deq;
      end
      Bool black = e.cm ? e.ci : dot;
      Bit#(8) lev = !e.inWin ? 'h20 : (black ? 'h00 : 'hff);
      Bit#(2) c0 = {pack(e.vsA == t.vpos), pack(e.hsA == t.hpos)};
      enc[0].put(e.de, c0, lev);
      enc[1].put(e.de, 0, lev);
      enc[2].put(e.de, 0, lev);
      outStart <= e.fstart;
   endrule

   method Action start(WinVideoMode m, Bit#(7) px, Bit#(10) py);
      startW.wset(tuple3(m, px, py));
   endmethod
   method Action stop = stopW.send;
   method Action cursorShape(Bit#(3) s, Bit#(4) r, Bit#(16) mask, Bit#(16) image) =
      cursor.shape(s, r, mask, image);
   method Action cursorPlace(Bool on, Bit#(12) x, Bit#(11) y, Bit#(3) s) =
      cursor.place(on, x, y, s);
   method WinTmdsOut out;
      function Bit#(10) symOf(WinTmdsEnc e) = e.sym;
      return WinTmdsOut { start: outStart, sym: map(symOf, enc) };
   endmethod
endmodule

endpackage
