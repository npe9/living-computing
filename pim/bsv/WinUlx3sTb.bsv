// WinUlx3sTb: the board design's core (WinUlx3s.bsv mkWinCore) and the
// serializer in their three clock domains, in Bluesim.
// HAND-WRITTEN (not a generated bench); docs/simpos/window_hardware_plan.md
// H3.  Driven by bsv/run_win_tb.sh, whose header records the injected
// faults and what each failed.
//
// The clocks (Bluesim time units; the board's ratios approximately):
//   sclk  period 2             (370 MHz on the board)
//   pclk  sclk / 5, period 10  (74 MHz; mkClockDivider, so phase-locked
//                               to sclk as the PLL's two outputs are)
//   sys   period 27, unrelated (25 MHz; 2.7 pixel clocks, not 2.96, so
//                               the crossing's phase drifts over a frame)
// The resets: the system reset synchronized into pclk and sclk by
// mkAsyncReset, as mkWinUlx3s does.  The one difference from mkWinUlx3s
// is the pclk -> sclk crossing: mkWinCrossModel (WinCrossModel.bsv), which
// poisons a read of the characters on the edges where they change, in
// place of a bare mkNullCrossingWire.
//
// In the working directory, at time 0: win_font.hex, win_stream.hex,
// win_scan.hex (the self-test's load files, as bsv/run_win_fpga.sh makes
// them: psi/winscan.py's `mode0` case), win_ulx3s_tb.hex (two words: P0,
// the first pixel clock of the serializer window, counted from the frame
// start; NS, its length).  It writes:
//   win_tmds.bin     the characters from the frame-start mark on, N
//                    (win_scan.hex word 20) pixel clocks, as WinScanOutTb
//   win_ser_px.hex   the characters of pixel clocks P0 .. P0 + NS - 1
//   win_ser.bin      the serializer's pins over that window, one byte a
//                    shift clock (WinTmdsSerTb's format)
//   win_frame.pbm    the frame dumped through the box after the capture
// and prints "WinUlx3sTb: self-test done ..." with the error flag.
package WinUlx3sTb;

import Clocks::*;
import RegFile::*;
import GetPut::*;
import ClientServer::*;
import Vector::*;
import WinFbBox::*;
import WinScanOut::*;
import WinCrossModel::*;
import WinUlx3s::*;

(* synthesize *)
module mkWinUlx3sTb(Empty);
   Clock sclk <- mkAbsoluteClockFull(2, 1'b0, 1, 1);
   Reset sInit <- mkInitialReset(2, clocked_by sclk);
   ClockDividerIfc div <- mkClockDivider(5, clocked_by sclk, reset_by sInit);
   Clock pclk = div.slowClock;
   Clock sys <- mkAbsoluteClockFull(7, 1'b0, 13, 14);
   Reset sysRst <- mkInitialReset(4, clocked_by sys);
   Reset prst <- mkAsyncReset(2, sysRst, pclk);
   Reset srst <- mkAsyncReset(2, sysRst, sclk);

   WinCore core <- mkWinCore("win_font.hex", "win_stream.hex", "win_scan.hex", pclk, prst,
                             clocked_by sys, reset_by sysRst);
   ReadOnly#(Vector#(3, Bit#(10))) wx <-
      mkNullCrossingWire(sclk, core.out.sym, clocked_by pclk, reset_by prst);
   ReadOnly#(Bool) tx <- mkNullCrossingWire(sclk, core.tog, clocked_by pclk, reset_by prst);
   WinCrossModel xm <- mkWinCrossModel(wx, tx, clocked_by sclk, reset_by srst);
   WinTmdsSer ser <- mkWinTmdsSer(xm.w, xm.tog, clocked_by sclk, reset_by srst);

   // ---- the pixel domain: the characters ------------------------------
   RegFile#(Bit#(8), Bit#(32)) cfg <- mkRegFileLoad("win_scan.hex", 0, 159,
                                                    clocked_by pclk, reset_by prst);
   RegFile#(Bit#(1), Bit#(32)) tbc <- mkRegFileLoad("win_ulx3s_tb.hex", 0, 1,
                                                    clocked_by pclk, reset_by prst);
   Reg#(Bool) pOpen <- mkReg(False, clocked_by pclk, reset_by prst);
   Reg#(File) fT <- mkReg(InvalidFile, clocked_by pclk, reset_by prst);
   Reg#(File) fPx <- mkReg(InvalidFile, clocked_by pclk, reset_by prst);
   Reg#(Bool) cap <- mkReg(False, clocked_by pclk, reset_by prst);
   Reg#(Bit#(32)) n <- mkReg(0, clocked_by pclk, reset_by prst);
   Reg#(Bool) capDone <- mkReg(False, clocked_by pclk, reset_by prst);
   Reg#(Bool) serOn <- mkReg(False, clocked_by pclk, reset_by prst);

   rule pixOpen (!pOpen);
      File t <- $fopen("win_tmds.bin", "wb");
      File x <- $fopen("win_ser_px.hex", "w");
      if (t == InvalidFile || x == InvalidFile) begin
         $display("WinUlx3sTb: cannot open the output files");
         $finish(1);
      end
      fT <= t; fPx <= x; pOpen <= True;
   endrule

   rule pixCapture (pOpen && !capDone);
      WinTmdsOut o = core.out;
      if (cap || o.start) begin
         Bit#(32) w = {pack(o.start), 1'b0, o.sym[2], o.sym[1], o.sym[0]};
         $fwrite(fT, "%c%c%c%c", w[31:24], w[23:16], w[15:8], w[7:0]);
         Bool inSer = n >= tbc.sub(0) && n < tbc.sub(0) + tbc.sub(1);
         if (inSer)
            $fwrite(fPx, "%03h %03h %03h\n", o.sym[0], o.sym[1], o.sym[2]);
         Bool last = n + 1 == cfg.sub(20);
         serOn <= inSer && !last;
         cap <= True;
         if (last) begin
            $fclose(fT); $fclose(fPx);
            capDone <= True;
         end
         n <= n + 1;
      end
   endrule

   // ---- the shift domain: the pins over the window -----------------------
   ReadOnly#(Bool) serOnX <- mkNullCrossingWire(sclk, serOn, clocked_by pclk, reset_by prst);
   Reg#(File) fS <- mkReg(InvalidFile, clocked_by sclk, reset_by srst);
   Reg#(Bit#(2)) sPh <- mkReg(0, clocked_by sclk, reset_by srst);   // 0 closed 1 open 2 on 3 done
   rule serOpen (sPh == 0);
      File f <- $fopen("win_ser.bin", "wb");
      fS <= f; sPh <= 1;
   endrule
   rule serCap (sPh == 1 || sPh == 2);
      if (serOnX) begin
         Vector#(4, Bit#(2)) p = ser.pins;
         $fwrite(fS, "%c", {p[3], p[2], p[1], p[0]});
         sPh <= 2;
      end
      else if (sPh == 2) begin
         $fclose(fS);
         sPh <= 3;
      end
   endrule

   // ---- the system domain: wait, then dump the frame ---------------------
   ReadOnly#(Bool) doneX <- mkNullCrossingWire(sys, capDone, clocked_by pclk, reset_by prst);
   Reg#(Bit#(2)) yPh <- mkReg(0, clocked_by sys, reset_by sysRst);
   Reg#(File) fF <- mkReg(InvalidFile, clocked_by sys, reset_by sysRst);
   Reg#(Bit#(17)) words <- mkReg(0, clocked_by sys, reset_by sysRst);
   Reg#(Bit#(32)) cyc <- mkReg(0, clocked_by sys, reset_by sysRst);
   Reg#(Bit#(32)) doneAt <- mkReg(0, clocked_by sys, reset_by sysRst);
   Reg#(Bool) doneSeen <- mkReg(False, clocked_by sys, reset_by sysRst);

   rule sysCount;
      cyc <= cyc + 1;
      if (cyc == 50000000) begin
         $display("WinUlx3sTb: timeout (self-test done %0d, capture done %0d)",
                  core.done, doneX);
         $finish(1);
      end
   endrule
   rule noteDone (core.done && !doneSeen);
      doneSeen <= True; doneAt <= cyc;
   endrule
   rule dumpReq (yPh == 0 && doneX && core.done);
      File f <- $fopen("win_frame.pbm", "wb");
      fF <= f;
      core.dbg.request.put(WinFbCmd { op: 'h70, a: replicate(0) });
      yPh <= 1;
   endrule
   rule dumpRsp (yPh == 1);
      let r <- core.dbg.response.get;
      if (r.isData) begin
         if (words == 0) $fwrite(fF, "P4\n1280 1024\n");
         $fwrite(fF, "%c%c", r.data[15:8], r.data[7:0]);
         words <= words + 1;
      end
      else begin
         $fclose(fF);
         $display("WinUlx3sTb: self-test done at system cycle %0d, error %0d, %0d words dumped",
                  doneAt, core.err, words);
         $finish(0);
      end
   endrule
endmodule

endpackage
