// The window frame memory (mkWinFrame): the 1-bit 1280 x 1024 frame,
// 81,920 x 16-bit words, banked by hand into 80 block RAMs of 1,024 x 16
// (one ECP5 DP16KD each), with two ports in two clock domains.
// docs/simpos/window_hardware_plan.md H3 (§2.3, §5.1, §5.2).  OURS.
//
// Why banked by hand: the plan's sizing skeleton (§5.1, Appendix A)
// measured an inferred single 81,920-word array failing its pixel clock
// at 64.99 MHz on the 80:1 output mux; the banked skeleton with a
// registered mux closed at 87.93-98.31 MHz.  This module is that
// structure in BSV.
//
//   port A  the current (system) clock: the drawing engine and the dump
//           of mkWinFbBox.  put(write, addr, data); read the word TWO
//           cycles later (WinFrameLatA): the request is registered, then
//           every bank is put (a write enables only its bank), and the
//           80:1 mux after the banks is combinational on the registered
//           bank select.  H0/H1 had one cycle (mkBRAMCore2); the box now
//           waits a cycle after each frame read (WinFbBox.bsv fWait), so
//           its read-modify-write and copy cycle counts grew (its header).
//   port B  the pixel clock `pclk` (a parameter; the benches pass the
//           current clock for the one-clock bench): read only, for
//           mkWinScanOut's fetch.  put(addr); the word is `read` exactly
//           WinFrameLatB = 4 cycles later:
//             0  put: the address registered (fan-out to 80 banks)
//             1  every bank reads that offset
//             2  ten 8:1 muxes registered (bank bits [2:0])
//             3  one 10:1 mux registered (bank bits [6:3])
//             4  read
// Each bank is mkSyncBRAMCore2(1024, False, clk, rst, pclk, prst): the
// DP16KD's two ports are independently clocked, so the system-to-pixel
// crossing of the frame is the block RAM itself (plan §5.2).  A read on
// port B of a word port A writes in the same period gets either word (a
// one-pixel tear, never a hang); nothing depends on it.
package WinFrame;

import BRAMCore::*;
import Vector::*;

// The scan-out's read of the frame (port B): put a word address, read
// the word WinFrameLatB cycles later.  (H2 defined it in WinFbBox.bsv
// with a one-cycle read; H3 moved it here with the banked latency.)
interface WinFbScan;
   method Action put(Bit#(17) addr);
   method Bit#(16) read;
endinterface

typedef 80 FrameBanks;
typedef 2 WinFrameLatA;
typedef 4 WinFrameLatB;

interface WinFrame;
   interface BRAM_PORT#(Bit#(17), Bit#(16)) a;
   interface WinFbScan b;                 // clocked by pclk
endinterface

module mkWinFrame#(Clock pclk, Reset prst)(WinFrame);
   Clock clk <- exposeCurrentClock;
   Reset rst <- exposeCurrentReset;
   Integer nb = valueOf(FrameBanks);

   Vector#(FrameBanks, BRAM_DUAL_PORT#(Bit#(10), Bit#(16))) bank <-
      replicateM(mkSyncBRAMCore2(1024, False, clk, rst, pclk, prst));

   // ---- port A (system clock) -------------------------------------------
   // put only sets a wire and one rule drives the 80 banks: were the
   // banks driven in the method, bsc would inline them into every rule
   // of the box that calls put, and each bank's address and data would
   // get a mux over those rules (MEASURED: about 4,000 LUT4 more).
   Reg#(Bit#(7)) selA <- mkRegU;
   RWire#(Tuple3#(Bool, Bit#(17), Bit#(16))) putA <- mkRWire;

   // the request registered, then the banks: the 80-way fan-out starts
   // at a flop (H3: driven straight from the box's address logic, the
   // system clock reached 19.31 MHz, MEASURED)
   Reg#(Maybe#(Tuple3#(Bool, Bit#(17), Bit#(16)))) reqA <- mkReg(tagged Invalid);

   (* fire_when_enabled, no_implicit_conditions *)
   rule portA;
      reqA <= putA.wget;
      if (reqA matches tagged Valid {.write, .addr, .d}) begin
         Bit#(7) bk = addr[16:10];
         // every bank reads (or one writes): the enables are one net
         for (Integer i = 0; i < nb; i = i + 1)
            bank[i].a.put(write && bk == fromInteger(i), addr[9:0], d);
         selA <= bk;
      end
   endrule

   // ---- port B (pixel clock) --------------------------------------------
   Reg#(Maybe#(Bit#(17))) addrB <- mkReg(tagged Invalid, clocked_by pclk, reset_by prst);
   RWire#(Bit#(17)) putB <- mkRWire(clocked_by pclk, reset_by prst);
   Reg#(Bit#(7)) bk1 <- mkRegU(clocked_by pclk, reset_by prst);
   Reg#(Bit#(4)) bk2 <- mkRegU(clocked_by pclk, reset_by prst);
   Vector#(10, Reg#(Bit#(16))) m8 <- replicateM(mkRegU(clocked_by pclk, reset_by prst));
   Reg#(Bit#(16)) word <- mkRegU(clocked_by pclk, reset_by prst);

   (* fire_when_enabled, no_implicit_conditions *)
   rule pipeB;
      addrB <= putB.wget;
      if (addrB matches tagged Valid .ad)
         for (Integer i = 0; i < nb; i = i + 1)
            bank[i].b.put(False, ad[9:0], ?);
      bk1 <= fromMaybe(0, addrB)[16:10];
      // the 8:1 muxes on bk1[2:0]
      for (Integer k = 0; k < 10; k = k + 1) begin
         Vector#(8, Bit#(16)) g = newVector;
         for (Integer j = 0; j < 8; j = j + 1) g[j] = bank[8 * k + j].b.read;
         m8[k] <= g[bk1[2:0]];
      end
      bk2 <= bk1[6:3];
      Vector#(10, Bit#(16)) h = readVReg(m8);
      word <= h[bk2];
   endrule

   interface BRAM_PORT a;
      method Action put(Bool write, Bit#(17) addr, Bit#(16) d) =
         putA.wset(tuple3(write, addr, d));
      method Bit#(16) read;
         function Bit#(16) rd(BRAM_DUAL_PORT#(Bit#(10), Bit#(16)) m) = m.a.read;
         Vector#(FrameBanks, Bit#(16)) v = map(rd, bank);
         return v[selA];
      endmethod
   endinterface
   interface WinFbScan b;
      method Action put(Bit#(17) addr) = putB.wset(addr);
      method Bit#(16) read = word;
   endinterface
endmodule

endpackage
