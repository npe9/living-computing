// PimmFepUlx3sTb.bsv -- the board's self-test (PimmFepUlx3s.bsv) in
// Bluesim, before any board: mkPimmFepSelfTest over the SPI reader
// mkPimmSdBlock and the card model mkPimmSdCardModel (PimmSdCardModel.bsv)
// on the image PIMM_SD_IMAGE, the UART line decoded here bit by bit.
// ALL OURS.  The divisors are shorter than the board's (UART 8 cycles a
// bit, card slow clock 4) to keep the run short.  Prints the line the
// board would print, and "fepselftest: PASS" if it says PASS and the LEDs
// agree, else "fepselftest: FAIL".  Run by run_fepemu_fpga.sh.

package PimmFepUlx3sTb;

import PimmSdTypes::*;
import PimmSdBlock::*;
import PimmSdCardModel::*;
import PimmFepUlx3s::*;

(* synthesize *)
module mkPimmFepUlx3sTb(Empty);
   PimmSdBlock     sd   <- mkPimmSdBlock(0, 4, 2);
   PimmSdCardModel card <- mkPimmSdCardModel(True, False, 3, 5);
   FepSelfTest     st   <- mkPimmFepSelfTest(sd.blocks, sd.ready, sd.failed, 8, 1000);

   rule rl_pins;
      card.pins(sd.sd_clk, sd.sd_cs_n, sd.sd_mosi);
      sd.sd_miso(card.miso);
   endrule

   // the UART receiver: a start bit, eight data bits at 8 cycles each,
   // sampled mid-bit
   Reg#(Bool)      inChar <- mkReg(False);
   Reg#(UInt#(8))  t      <- mkReg(0);
   Reg#(UInt#(4))  nb     <- mkReg(0);
   Reg#(Bit#(8))   ch     <- mkReg(0);
   Reg#(Bit#(1))   prev   <- mkReg(1);
   Reg#(UInt#(32)) cycle  <- mkReg(0);
   Reg#(Bool)      sawPass <- mkReg(False);
   Reg#(UInt#(8))  col    <- mkReg(0);

   rule rl_cycle;
      cycle <= cycle + 1;
      if (cycle == 40000000) begin
         $display("\nfepselftest: FAIL (no report in 40,000,000 cycles; LEDs %b)", st.led);
         $finish(1);
      end
   endrule

   rule rl_rx;
      Bit#(1) x = st.txd;
      prev <= x;
      if (!inChar) begin
         if (prev == 1 && x == 0) begin inChar <= True; t <= 11; nb <= 0; end
      end
      else if (t != 0) t <= t - 1;
      else begin
         ch <= {x, ch[7:1]};
         Bit#(8) c = {x, ch[7:1]};
         if (nb == 7) begin
            inChar <= False;
            $write("%c", c);
            if (c == 10) begin
               Bool ok = sawPass && st.passed && st.finished && st.led[3] == 1 && st.led[4] == 0;
               $display("fepselftest: %s (LEDs %b, cycle %0d)", ok ? "PASS" : "FAIL", st.led, cycle);
               $finish(ok ? 0 : 1);
            end
            // "PASS" begins at column 7 of the report
            if (col == 7 && c == 80) sawPass <= True;
            col <= col + 1;
         end
         else begin
            nb <= nb + 1; t <= 7;
         end
      end
   endrule
endmodule

endpackage
