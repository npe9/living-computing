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
// fetch/display distance.  From lead to characters is 19 clocks (H3
// added a register after the lead counters and one between the pixel's
// composition and the encoders, for the pixel clock's Fmax).
//
// mkWinTmdsSer, below, is the 10:1 serializer in the shift-clock domain;
// bsv/WinTmdsSerTb.bsv runs it at a 5:1 clock relation in Bluesim, at
// each of the five offsets.  The scan-out and the box's port B run on
// one clock in WinScanOutTb; bsv/WinUlx3sTb.bsv runs them in the pixel
// clock against the box's system clock (H3), as the board does.
//
// Unimplemented cases fail loud: a word-queue overflow or underflow, or
// a start less than 19 clocks after a stop (the pipeline drains itself
// in that time), stops the simulation.
package WinScanOut;

import Vector::*;
import RegFile::*;
import FIFOF::*;
import WinFrame::*;

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
   // the mode's sums, registered at start (H3: summed from t every clock
   // they were the pixel clock's critical path, 73.26 MHz, MEASURED)
   Reg#(Bit#(12)) htm1 <- mkReg(0);        // total - 1
   Reg#(Bit#(11)) vtm1 <- mkReg(0);
   Reg#(Bit#(12)) hs0 <- mkReg(0);         // sync start, end
   Reg#(Bit#(12)) hs1 <- mkReg(0);
   Reg#(Bit#(11)) vs0 <- mkReg(0);
   Reg#(Bit#(11)) vs1 <- mkReg(0);
   Reg#(Bit#(12)) haM1 <- mkReg(0);        // the last active pixel

   method Action start(WinVideoMode m);
      t <= m; run <= True; hx <= 0; vy <= 0;
      htm1 <= m.ha + m.hf + m.hs + m.hb - 1;
      vtm1 <= m.va + m.vf + m.vs + m.vb - 1;
      hs0 <= m.ha + m.hf; hs1 <= m.ha + m.hf + m.hs;
      vs0 <= m.va + m.vf; vs1 <= m.va + m.vf + m.vs;
      haM1 <= m.ha - 1;
   endmethod
   method Action stop;
      run <= False;
   endmethod
   method Action step;
      if (run) begin
         if (hx == htm1) begin
            hx <= 0;
            vy <= (vy == vtm1) ? 0 : vy + 1;
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
         hsA: run && hx >= hs0 && hx < hs1,
         vsA: run && vy >= vs0 && vy < vs1,
         inWin: de && u < t.fw && v < t.fh,
         lineEnd: hx == haM1,
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

typedef struct { Bool ok; Bool isB; Bool half; } FetchTag deriving (Bits);

module mkWinFetch#(WinFbScan fb)(WinFetch);
   Integer lat = valueOf(WinFrameLatB);
   FIFOF#(Tuple2#(Bit#(16), Bit#(16))) q <- mkUGSizedFIFOF(4);
   // the reads in flight: tag i was issued i + 1 cycles ago; the word of
   // the last one is fb.read now (port B's fixed latency, WinFrame.bsv)
   Vector#(WinFrameLatB, Reg#(Maybe#(FetchTag))) fly <- replicateM(mkReg(tagged Invalid));
   Reg#(Bool) pendB <- mkReg(False);      // 2:1: row B's read goes next cycle
   Reg#(Bit#(16)) wA <- mkReg(0);
   Reg#(Bit#(12)) rowB <- mkReg(0);
   Reg#(Bit#(12)) colR <- mkReg(0);
   RWire#(Tuple4#(WinVideoMode, Bit#(7), Bit#(10), WinLead)) leadW <- mkRWire;
   // H3, for the pixel clock: the lead signals are registered on entry
   // (stage 1), and the group's row, column and readability are
   // registered before the address is formed (stage 2); each adds one
   // clock between the lead and the read, well inside the delay line
   Reg#(Maybe#(Tuple4#(Bool, Bit#(12), Bit#(12), Bool))) grp <- mkReg(tagged Invalid);
   Reg#(Maybe#(Tuple4#(WinVideoMode, Bit#(7), Bit#(10), WinLead))) leadR <- mkReg(tagged Invalid);

   function Bool readable(Bit#(12) r, Bit#(12) c) = r < 1024 && c < 80;
   function Bit#(17) addrOf(Bit#(12) r, Bit#(12) c) =
      zeroExtend(r) * 80 + zeroExtend(c);
   Action overflow =
      action
         $display("WinScanOut: word queue overflow");
         $finish(1);
      endaction;

   // every cycle, whether or not the lead stage stepped: issue at most
   // one read, retire the oldest
   (* fire_when_enabled, no_implicit_conditions *)
   rule pipe;
      leadR <= leadW.wget;
      // stage 1: the first pixel of a group in the window: its row and column
      Maybe#(Tuple4#(Bool, Bit#(12), Bit#(12), Bool)) g1 = tagged Invalid;
      if (leadR matches tagged Valid {.t, .panX, .panY, .l}) begin
         Bit#(4) k = t.half ? zeroExtend(l.u[2:0]) : l.u[3:0];
         Bit#(12) col = (t.half ? l.u >> 3 : l.u >> 4) + zeroExtend(panX);
         Bit#(12) rA = (t.half ? zeroExtend(l.v) << 1 : zeroExtend(l.v)) + zeroExtend(panY);
         if (k == 0 && l.inWin) g1 = tagged Valid tuple4(readable(rA, col), rA, col, t.half);
      end
      grp <= g1;
      // stage 2: the read(s)
      Maybe#(FetchTag) issue = tagged Invalid;
      if (pendB) begin
         Bool ok = readable(rowB, colR);
         if (ok) fb.put(addrOf(rowB, colR));
         issue = tagged Valid FetchTag { ok: ok, isB: True, half: True };
         pendB <= False;
      end
      else if (grp matches tagged Valid {.ok, .rA, .col, .half}) begin
         if (ok) fb.put(addrOf(rA, col));
         issue = tagged Valid FetchTag { ok: ok, isB: False, half: half };
         rowB <= rA + 1; colR <= col;
         pendB <= half;
      end
      fly[0] <= issue;
      for (Integer i = 1; i < lat; i = i + 1) fly[i] <= fly[i - 1];
      if (fly[lat - 1] matches tagged Valid .g) begin
         Bit#(16) w = g.ok ? fb.read : 0;
         if (g.isB) begin
            if (!q.notFull) overflow;
            q.enq(tuple2(wA, w));
         end
         else if (g.half) wA <= w;
         else begin
            if (!q.notFull) overflow;
            q.enq(tuple2(w, 0));
         end
      end
   endrule

   method Action lead(WinVideoMode t, Bit#(7) panX, Bit#(10) panY, WinLead l);
      leadW.wset(tuple4(t, panX, panY, l));
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
   // the cursor at window pixel (u, v), in two pixel clocks (H3
   // follow-up: done in one, the position subtract, the plane RAM's read
   // and the dot select missed the 74 MHz pixel clock on a seed, MEASURED
   // 72.94 MHz): look gives (inside the 16 x 16, the dot's column, the
   // plane row's address); a clock later planeRow(address) gives the row,
   // mask << 16 | image.  At a frame start the pending position counts.
   method Tuple3#(Bool, Bit#(4), Bit#(7)) look(Bool fs, Bit#(12) u, Bit#(11) v);
   method Bit#(32) planeRow(Bit#(7) a);
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
   // a shape row likewise (so a command dispatcher may call shape and
   // start in one rule: WinUlx3s.bsv mkWinScanPix)
   RWire#(Tuple2#(Bit#(7), Bit#(32))) shapeW <- mkRWire;
   rule commitShape (shapeW.wget matches tagged Valid {.a, .v});
      planes.upd(a, v);
   endrule

   method Action shape(Bit#(3) s, Bit#(4) r, Bit#(16) mask, Bit#(16) image);
      shapeW.wset(tuple2({s, r}, {mask, image}));
   endmethod
   method Action place(Bool on, Bit#(12) x, Bit#(11) y, Bit#(3) s);
      placeW.wset(WinCursorPos { on: on, x: x, y: y, s: s });
   endmethod
   method Action frameStart;
      act <= pend;
   endmethod
   method Tuple3#(Bool, Bit#(4), Bit#(7)) look(Bool fs, Bit#(12) u, Bit#(11) v);
      WinCursorPos c = fs ? pend : act;
      Bit#(12) du = u - c.x;
      Bit#(11) dv = v - c.y;
      Bool hit = c.on && du < 16 && dv < 16;
      return tuple3(hit, du[3:0], {c.s, dv[3:0]});
   endmethod
   method Bit#(32) planeRow(Bit#(7) a) = planes.sub(a);
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
// flute-lx50's serializer).  Clocked by the SHIFT clock.  Bit 0 of each
// character is sent first (DVI 1.0 §3.2.3 p30).  The clock lane sends
// 'b0000011111 (five ones, then five zeros: one period a character).
//
// THE LOAD PHASE (H3).  `w` is the pixel domain's three characters and
// `tog` a pixel-domain bit that flips every pixel clock (mkWinScanOut's
// `tog`), both read without a synchronizer (mkNullCrossingWire).  H2's
// serializer ran a free one-hot phase from reset and sampled `w` on
// ph[2]: nothing tied that phase to the pixel clock's edge, so on the
// board it would land on whichever of the five alignments reset gave
// it, the edge where `w` changes included (H2's uncaught injection
// #14).  Here, as flute-lx50's `dvi_ser` does, the phase is taken from
// the pixel clock: `tog` passes two flops (t1, t2, a synchronizer: t1
// may go metastable), their difference is registered (e), and e
// restarts the one-hot phase ph.  Every decision is a flop set from
// the phase a clock ahead: sm, the sample enable (from ph's next value
// bit WinSerSmp = 4), and two load flags a lane, copied from a flop set from bit
// WinSerLd - 1 = 0 (so loading as if set from bit WinSerLd = 1).
// Timeline: if the pixel edge launching `w` and `tog` is shift edge s0,
// t1 takes the new `tog` at s0 or s1, e is set at s1 or s2, ph = 00001
// from s2 or s3, and h samples `w` at s2 or s3 (bit 4 of ph's next
// value is set four clocks after the restart, so sm is set at s6 or s7,
// and five clocks are one pixel: s7 or s8 is s2 or s3 of the next
// pixel) and the next change is at s5: the word path has two shift
// periods from launch (5.40 ns at 370 MHz) and two of hold.  The shift
// registers load h two clocks after it is sampled, through the copy h2.  bsv/run_win_fpga.sh
// checks nextpnr's pclk -> sclk delay against one period, and
// WinTmdsSerTb and WinUlx3sTb model the unsafe sample ages
// (WinCrossModel.bsv, run_win_tb.sh).  The flops a clock ahead are the
// skeleton's fix for its 225 MHz mod-5 counter (plan §5.1); e and sm
// are H3's (the shift clock's critical path ran from t1/t2 through the
// phase logic to the 30 sample enables, 319.69 MHz, then to the load
// flags, 358.94 MHz, MEASURED), and so are lq, the per-lane sm, the
// eight half-lane ld and h2 (below).  Every remaining shift-clock path
// is one flop, at most one LUT, and a route: on 3 seeds the shift clock
// closed at 384.76-418.24 MHz (run_win_fpga.sh, 2026-11-25).
typedef 4 WinSerSmp;
typedef 1 WinSerLd;

interface WinTmdsSer;
   method Vector#(4, Bit#(2)) pins;      // per lane {D1, D0}
endinterface

module mkWinTmdsSer#(ReadOnly#(Vector#(3, Bit#(10))) w, ReadOnly#(Bool) tog)(WinTmdsSer);
   // no reset (H3): a reset net to 70 flops at 370 MHz was the shift
   // clock's critical path (255.62 MHz, MEASURED); the phase needs none,
   // since the first change of `tog` sets it, and nothing else holds state
   Reg#(Bool) t1 <- mkReg(False, reset_by noReset);
   Reg#(Bool) t2 <- mkReg(False, reset_by noReset);
   Reg#(Bool) e <- mkReg(False, reset_by noReset);
   Reg#(Bit#(5)) ph <- mkReg(1, reset_by noReset);
   // one sample enable a lane (ten flops each, not thirty for one)
   Vector#(3, Reg#(Bool)) sm <- replicateM(mkReg(False, reset_by noReset));
   // two load flags a lane, each for five bits, copied from one flop lq
   // that is set a clock earlier still: one flag for ten bits was the
   // shift clock's critical path on seed 2 (367.11 MHz), and eight flags
   // set from the phase logic were next (317.46-365.76 MHz, MEASURED)
   Reg#(Bool) lq <- mkReg(False, reset_by noReset);
   Vector#(8, Reg#(Bool)) ld <- replicateM(mkReg(False, reset_by noReset));
   Vector#(3, Reg#(Bit#(10))) h <- replicateM(mkReg(0, reset_by noReset));
   // h copied every clock: h is loaded into sh two clocks after it is
   // sampled, a two-clock path that nextpnr 0.6 can only time as one
   // (h -> sh was the shift clock's critical path, 343.52 MHz on seed 1,
   // MEASURED); h2 splits it into two one-clock paths, same latency
   Vector#(3, Reg#(Bit#(10))) h2 <- replicateM(mkReg(0, reset_by noReset));
   Vector#(4, Reg#(Bit#(10))) sh <- replicateM(mkReg(0, reset_by noReset));

   (* fire_when_enabled, no_implicit_conditions *)
   rule shift;
      t1 <= tog; t2 <= t1;
      e <= t1 != t2;
      Bit#(5) phn = e ? 'b00001 : {ph[3:0], ph[4]};
      ph <= phn;
      lq <= phn[valueOf(WinSerLd) - 1] == 1;
      for (Integer i = 0; i < 8; i = i + 1) ld[i] <= lq;
      for (Integer i = 0; i < 3; i = i + 1) begin
         sm[i] <= phn[valueOf(WinSerSmp)] == 1;
         if (sm[i]) h[i] <= w[i];
         h2[i] <= h[i];
      end
      for (Integer i = 0; i < 4; i = i + 1) begin
         Bit#(10) nx = (i == 3) ? 'b0000011111 : h2[i];
         Bit#(10) sr = sh[i] >> 2;
         sh[i] <= {ld[2 * i + 1] ? nx[9:5] : sr[9:5], ld[2 * i] ? nx[4:0] : sr[4:0]};
      end
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
   method Bool tog;                      // flips every pixel clock (the serializer's phase)
   // the composed pixel the encoders take (H7s, the virtual monitor's
   // tap, bsv/WinHostDev.bsv): DE, the sync LEVELS {vsync, hsync}, the
   // 8-bit level (00 a set dot, ff a clear one, 20 the border)
   method Tuple3#(Bool, Bit#(2), Bit#(8)) video;
endinterface

typedef struct {
   Bool de; Bool hsA; Bool vsA; Bool inWin; Bool last;
   Bit#(4) k; Bool cm; Bool ci; Bool fstart;
   Bit#(4) cu; Bit#(7) ca;      // the cursor's column and plane row (dl[0] only)
} WinDl deriving (Bits);

typedef 16 DlDepth;

module mkWinScanOut#(WinFbScan fb)(WinScanOut);
   WinTiming timing <- mkWinTiming;
   WinFetch fetch <- mkWinFetch(fb);
   WinCursor cursor <- mkWinCursor;
   Vector#(3, WinTmdsEnc) enc <- replicateM(mkWinTmdsEnc);

   WinDl blank = WinDl { de: False, hsA: False, vsA: False, inWin: False,
                         last: False, k: 0, cm: False, ci: False, fstart: False,
                         cu: 0, ca: 0 };
   Vector#(DlDepth, Reg#(WinDl)) dl <- replicateM(mkReg(blank));
   Reg#(Bool) outStart <- mkReg(False);
   Reg#(Bool) togR <- mkReg(False);
   Reg#(WinLead) leadQ <- mkReg(unpack(0));
   // the composed pixel, registered before the encoders (H3)
   Reg#(Tuple4#(Bool, Bit#(2), Bit#(8), Bool)) px <- mkReg(tuple4(False, 0, 0, False));
   Reg#(Bit#(7)) panX <- mkReg(0);
   Reg#(Bit#(10)) panY <- mkReg(0);

   RWire#(Tuple3#(WinVideoMode, Bit#(7), Bit#(10))) startW <- mkRWire;
   PulseWire stopW <- mkPulseWire;

   // the orchestration rule: one pixel clock
   (* fire_when_enabled, no_implicit_conditions *)
   rule tick;
      WinVideoMode t = timing.mode;
      // the lead signals, registered (H3, for the pixel clock: the
      // position counters' compare and subtract logic no longer sits in
      // front of the cursor and fetch logic)
      leadQ <= timing.lead;
      WinLead l = leadQ;

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
      match {.chit, .cu, .ca} = cursor.look(l.fstart, l.u, l.v);
      Bit#(4) k = t.half ? zeroExtend(l.u[2:0]) : l.u[3:0];
      Bit#(4) gl = t.half ? 7 : 15;
      dl[0] <= WinDl { de: l.de, hsA: l.hsA, vsA: l.vsA, inWin: l.inWin,
                       last: l.inWin && (k == gl || l.u == t.fw - 1 || l.lineEnd),
                       k: k, cm: l.inWin && chit, ci: False, fstart: l.fstart,
                       cu: cu, ca: ca };
      // the cursor's second clock, between dl[0] and dl[1]
      WinDl d0 = dl[0];
      Bit#(32) row = cursor.planeRow(d0.ca);
      Bit#(5) ci5 = 15 - zeroExtend(d0.cu);
      d0.cm = d0.cm && row[16 + ci5] == 1;
      d0.ci = row[ci5] == 1;
      dl[1] <= d0;
      for (Integer i = 2; i < valueOf(DlDepth); i = i + 1)
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
      px <= tuple4(e.de, c0, lev, e.fstart);
      match {.pde, .pc0, .plev, .pfs} = px;
      enc[0].put(pde, pc0, plev);
      enc[1].put(pde, 0, plev);
      enc[2].put(pde, 0, plev);
      outStart <= pfs;
      togR <= !togR;
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
   method Bool tog = togR;
   method Tuple3#(Bool, Bit#(2), Bit#(8)) video;
      match {.pde, .pc0, .plev, .pfs} = px;
      return tuple3(pde, pc0, plev);
   endmethod
endmodule

endpackage
