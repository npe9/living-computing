// The window hardware on the ULX3S (mkWinUlx3s): the framebuffer box,
// the scan-out and the DVI serializer in their three clock domains,
// with a self-test that draws a test card and starts the picture.
// docs/simpos/window_hardware_plan.md H3 (§5.1-§5.4).  ALL OURS.
//
// Clock domains (plan §5.2):
//   sys   the board's 25 MHz (the module's default clock): mkWinFbBox,
//         its frame port A, the self-test;
//   pclk  the pixel clock, 74 MHz for mode 0 (the PLL's CLKOS): the
//         frame's port B and mkWinScanOut;
//   sclk  the shift clock, 370 MHz, 5 x pclk from the same VCO (CLKOP):
//         mkWinTmdsSer.
// The crossings:
//   sys -> pclk, the frame: the DP16KD's two clocked ports (WinFrame.bsv);
//   sys -> pclk, control: one mkSyncFIFO of scan commands (start, stop,
//         cursor shape and place), dispatched in the pixel domain
//         (mkWinScanPix).  The cursor position still takes effect at the
//         next frame start (mkWinCursor);
//   pclk -> sclk: the characters and the pixel toggle, through
//         mkNullCrossingWire (no synchronizer for the word: the clocks
//         are phase-locked; the toggle is synchronized inside the
//         serializer, which takes its load phase from it: WinScanOut.bsv
//         mkWinTmdsSer).  bsv/run_win_fpga.sh checks the routed delay.
// Resets: the system reset (the Verilog top holds it until the PLL
// locks) is synchronized into pclk and sclk by mkAsyncReset.
//
// The self-test (mkWinSelfTest) reads two block-RAM load files made by
// psi/winscan.py for its `mode0` case: win_stream.hex (the drawing
// stream, psi/winfb.py's 104-bit command records, up to 512) and
// win_scan.hex (the scan configuration: mode, pan, cursor, 8 shapes;
// winscan.py's header).  It sends every command to the box and counts
// the statuses (any not OK lights the error LED), loads the cursor
// shapes and position, and starts the scan-out.  The same mkWinCore is
// the design under test of bsv/WinUlx3sTb.bsv, which runs the three
// clocks in Bluesim and checks the picture against the Python view.
//
// Board pins (the Verilog top bsv/WinUlx3sTop.v, pins bsv/ulx3s_win.lpf):
//   led[0] the self-test done   led[1] a status not OK
//   led[2] blinks every 16 frames (the pixel domain runs)
//   led[7] PLL lock (in the Verilog top)
package WinUlx3s;

import BRAMCore::*;
import Clocks::*;
import FIFOF::*;
import GetPut::*;
import ClientServer::*;
import Vector::*;
import WinFbBox::*;
import WinScanOut::*;

typedef union tagged {
   Tuple3#(WinVideoMode, Bit#(7), Bit#(10)) SStart;
   void SStop;
   Tuple4#(Bit#(3), Bit#(4), Bit#(16), Bit#(16)) SShape;
   Tuple4#(Bool, Bit#(12), Bit#(11), Bit#(3)) SPlace;
} WinScanCmd deriving (Bits);

// ======================================================================
// the scan-out in the pixel domain, commanded from the current (system)
// domain through a synchronizing FIFO
interface WinScanPix;
   method Action cmd(WinScanCmd c);       // system domain
   method WinTmdsOut out;                 // pixel domain
   method Bool tog;                       // pixel domain
endinterface

module mkWinScanPix#(WinFbScan fb, Clock pclk, Reset prst)(WinScanPix);
   Clock clk <- exposeCurrentClock;
   Reset rst <- exposeCurrentReset;
   SyncFIFOIfc#(WinScanCmd) cq <- mkSyncFIFO(4, clk, rst, pclk);
   WinScanOut scan <- mkWinScanOut(fb, clocked_by pclk, reset_by prst);

   rule dispatch;
      WinScanCmd c = cq.first;
      cq.deq;
      case (c) matches
         tagged SStart {.m, .px, .py}: scan.start(m, px, py);
         tagged SStop: scan.stop;
         tagged SShape {.s, .r, .mk, .im}: scan.cursorShape(s, r, mk, im);
         tagged SPlace {.on, .x, .y, .s}: scan.cursorPlace(on, x, y, s);
      endcase
   endrule

   method Action cmd(WinScanCmd c) = cq.enq(c);
   method WinTmdsOut out = scan.out;
   method Bool tog = scan.tog;
endmodule

// ======================================================================
interface WinCore;
   method Bool done;                      // system domain
   method Bool err;
   interface Server#(WinFbCmd, WinFbRsp) dbg;   // the box, once done
   method WinTmdsOut out;                 // pixel domain
   method Bool tog;
   method Bool blink;
endinterface

module mkWinCore#(String fontFile, String progFile, String cfgFile,
                  Clock pclk, Reset prst)(WinCore);
   WinFbBox box <- mkWinFbBox(fontFile, pclk, prst);
   WinScanPix pix <- mkWinScanPix(box.scan, pclk, prst);

   BRAM_PORT#(Bit#(9), Bit#(104)) prog <- mkBRAMCore1Load(512, False, progFile, False);
   BRAM_PORT#(Bit#(8), Bit#(32)) cfg <- mkBRAMCore1Load(160, False, cfgFile, False);

   Reg#(Bit#(4)) st <- mkReg(0);
   Reg#(Bit#(9)) idx <- mkReg(0);
   Reg#(Bit#(9)) nst <- mkReg(0);
   Reg#(Bit#(9)) nCmd <- mkReg(0);
   Reg#(Bool) bad <- mkReg(False);
   Reg#(Bit#(8)) ci <- mkReg(0);
   Vector#(20, Reg#(Bit#(16))) c <- replicateM(mkReg(0));
   Integer sDone = 10;

   // 0, 1: the stream, one command each two cycles, to its end record
   rule progReq (st == 0);
      prog.put(False, idx, ?);
      st <= 1;
   endrule
   rule progCmd (st == 1);
      Bit#(104) v = prog.read;
      Bit#(8) op = v[103:96];
      Vector#(6, Bit#(16)) a = newVector;
      for (Integer i = 0; i < 6; i = i + 1)
         a[i] = v[95 - 16 * i : 80 - 16 * i];
      if (op[7:4] == 0 || idx == 511) begin
         nCmd <= idx;
         st <= 2;
      end
      else begin
         box.server.request.put(WinFbCmd { op: op, a: a });
         idx <= idx + 1;
         st <= 0;
      end
   endrule
   // the statuses while the self-test owns the box
   rule progRsp (st < fromInteger(sDone));
      let r <- box.server.response.get;
      if (!r.isData) begin
         nst <= nst + 1;
         if (r.status != 0) bad <= True;
      end
   endrule
   rule drawn (st == 2 && nst == nCmd);
      st <= 3; ci <= 0;
   endrule
   // 3, 4: configuration words 0-19
   rule cfgReq (st == 3);
      cfg.put(False, ci, ?);
      st <= 4;
   endrule
   rule cfgRd (st == 4);
      c[ci] <= truncate(cfg.read);
      if (ci == 19) begin
         st <= 5; ci <= 32;
      end
      else begin
         ci <= ci + 1; st <= 3;
      end
   endrule
   // 5, 6: the 128 cursor shape rows (words 32-159)
   rule shapeReq (st == 5);
      cfg.put(False, ci, ?);
      st <= 6;
   endrule
   rule shapeSend (st == 6);
      Bit#(32) w = cfg.read;
      Bit#(8) s = ci - 32;
      pix.cmd(tagged SShape tuple4(s[6:4], s[3:0], w[31:16], w[15:0]));
      if (ci == 159) st <= 7;
      else begin
         ci <= ci + 1; st <= 5;
      end
   endrule
   rule place (st == 7);
      pix.cmd(tagged SPlace tuple4(c[16] != 0, truncate(c[17]), truncate(c[18]),
                                   truncate(c[19])));
      st <= 8;
   endrule
   rule go (st == 8);
      Bit#(16) fl = c[9];
      WinVideoMode custom = WinVideoMode {
         ha: truncate(c[1]), hf: truncate(c[2]),
         hs: truncate(c[3]), hb: truncate(c[4]),
         va: truncate(c[5]), vf: truncate(c[6]),
         vs: truncate(c[7]), vb: truncate(c[8]),
         hpos: fl[0] == 1, vpos: fl[1] == 1,
         x0: truncate(c[10]), y0: truncate(c[11]),
         fw: truncate(c[12]), fh: truncate(c[13]), half: fl[2] == 1 };
      pix.cmd(tagged SStart tuple3(c[0] < 4 ? winMode(truncate(c[0])) : custom,
                                   truncate(c[14]), truncate(c[15])));
      st <= fromInteger(sDone);
   endrule

   // the pixel domain: a frame counter for the LED
   Reg#(Bit#(5)) frames <- mkReg(0, clocked_by pclk, reset_by prst);
   rule countFrames (pix.out.start);
      frames <= frames + 1;
   endrule

   method Bool done = st == fromInteger(sDone);
   method Bool err = bad;
   interface Server dbg;
      interface Put request;
         method Action put(WinFbCmd x) if (st == fromInteger(sDone));
            box.server.request.put(x);
         endmethod
      endinterface
      interface Get response;
         method ActionValue#(WinFbRsp) get if (st == fromInteger(sDone));
            let r <- box.server.response.get;
            return r;
         endmethod
      endinterface
   endinterface
   method WinTmdsOut out = pix.out;
   method Bool tog = pix.tog;
   method Bool blink = frames[4] == 1;
endmodule

// ======================================================================
// The board module.  pclk and sclk come from the PLL in the Verilog top
// (bsv/WinUlx3sTop.v); the default clock is the 25 MHz oscillator.
interface WinUlx3s;
   (* always_ready *) method Bit#(8) pins;   // lane i {D1, D0} at [2i+1:2i]; sclk
   (* always_ready *) method Bit#(2) led;    // {err, done}; sys
   (* always_ready *) method Bool blink;     // pclk
endinterface

(* synthesize *)
module mkWinUlx3s#(Clock pclk, Clock sclk)(WinUlx3s);
   Reset rst <- exposeCurrentReset;
   Reset prst <- mkAsyncReset(2, rst, pclk);
   Reset srst <- mkAsyncReset(2, rst, sclk);
   WinCore core <- mkWinCore("win_font.hex", "win_stream.hex", "win_scan.hex", pclk, prst);
   ReadOnly#(Vector#(3, Bit#(10))) wx <-
      mkNullCrossingWire(sclk, core.out.sym, clocked_by pclk, reset_by prst);
   ReadOnly#(Bool) tx <- mkNullCrossingWire(sclk, core.tog, clocked_by pclk, reset_by prst);
   WinTmdsSer ser <- mkWinTmdsSer(wx, tx, clocked_by sclk, reset_by srst);

   method Bit#(8) pins = pack(ser.pins);
   method Bit#(2) led = {pack(core.err), pack(core.done)};
   method Bool blink = core.blink;
endmodule

endpackage
