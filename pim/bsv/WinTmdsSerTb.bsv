// WinTmdsSerTb: mkWinTmdsSer (bsv/WinScanOut.bsv) at the plan's clock
// relation: the bench clock is the shift clock, the pixel clock is it
// divided by 5 (mkClockDivider), as the one EHXPLLL gives 370 / 74 MHz
// (plan §5.2).  HAND-WRITTEN.
//
// In the pixel domain three mkWinTmdsEnc encode a pattern (64-clock
// lines, 44 active; channel 0's C1C0 cycles through 00 01 10 11 a line;
// LFSR data, different on each channel) and log their characters to
// win_ser_px.hex.  The characters cross to the shift domain through a
// mkNullCrossingWire (no synchronizer, as in the hardware: phase-locked
// clocks).  The serializer's pins (per lane D0 then D1, an ODDRX1F's
// order) are written to win_ser.bin, one byte a shift clock:
// lane 3 (clock) << 6 | lane 2 << 4 | lane 1 << 2 | lane 0, each {D1, D0}.
// psi/winscan.py `sercheck` rebuilds the serial streams (bit 0 of each
// character first, DVI 1.0 §3.2.3), finds the character boundary on the
// clock lane, and requires every data lane to carry exactly the logged
// characters at one common boundary and latency.
package WinTmdsSerTb;

import Clocks::*;
import Vector::*;
import WinScanOut::*;

typedef 3000 Pixels;

(* synthesize *)
module mkWinTmdsSerTb(Empty);
   Clock sclk <- exposeCurrentClock;
   ClockDividerIfc div <- mkClockDivider(5);
   Reset prst <- mkAsyncResetFromCR(1, div.slowClock);

   // ---- the pixel domain ----------------------------------------------
   Vector#(3, WinTmdsEnc) enc <- replicateM(mkWinTmdsEnc(clocked_by div.slowClock, reset_by prst));
   Reg#(Bit#(16)) pn <- mkReg(0, clocked_by div.slowClock, reset_by prst);
   Reg#(Bit#(16)) lfsr <- mkReg('hace1, clocked_by div.slowClock, reset_by prst);
   Reg#(File) fpx <- mkReg(InvalidFile, clocked_by div.slowClock, reset_by prst);
   function Bit#(10) symOf(WinTmdsEnc e) = e.sym;
   ReadOnly#(Vector#(3, Bit#(10))) wx <- mkNullCrossingWire(sclk, map(symOf, enc),
                                                            clocked_by div.slowClock,
                                                            reset_by prst);

   rule pixel;
      File f = fpx;
      if (pn == 0) begin
         f <- $fopen("win_ser_px.hex", "w");
         fpx <= f;
      end
      else if (pn <= fromInteger(valueOf(Pixels)))
         $fwrite(f, "%03h %03h %03h\n", enc[0].sym, enc[1].sym, enc[2].sym);
      else if (pn == fromInteger(valueOf(Pixels)) + 1)
         $fclose(f);
      Bool de = pn[5:0] < 44;
      Bit#(2) c = pn[7:6];
      Bit#(8) d0 = lfsr[7:0];
      Bit#(8) d1 = lfsr[15:8];
      enc[0].put(de, c, d0);
      enc[1].put(de, 0, d1);
      enc[2].put(de, 0, d0 ^ d1 ^ pn[7:0]);
      lfsr <= {lfsr[14:0], lfsr[15] ^ lfsr[13] ^ lfsr[12] ^ lfsr[10]};
      pn <= pn + 1;
   endrule

   // ---- the shift domain ------------------------------------------------
   WinTmdsSer ser <- mkWinTmdsSer(wx);
   Reg#(Bit#(32)) sn <- mkReg(0);
   Reg#(File) fs <- mkReg(InvalidFile);

   rule capture;
      File f = fs;
      if (sn == 0) begin
         f <- $fopen("win_ser.bin", "wb");
         fs <= f;
      end
      Vector#(4, Bit#(2)) p = ser.pins;
      $fwrite(f, "%c", {p[3], p[2], p[1], p[0]});
      if (sn == 5 * (fromInteger(valueOf(Pixels)) + 4)) begin
         $fclose(f);
         $display("WinTmdsSerTb: %0d shift clocks", sn + 1);
         $finish(0);
      end
      sn <= sn + 1;
   endrule
endmodule

endpackage
