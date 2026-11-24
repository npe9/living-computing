// LcdLcdisp.bsv: the Hobbit board's LCD, io.h `Lcdisp` at IOACK 0x3000,
// as a device behind the bring-up plan's register port
// (hobbit/docs/ulx3s_plan.md "Device bus contract"), with its 768 x 1024 x
// 2-bit panel held in ECP5 block RAM and a second, read-only port on the
// pixel clock for the HDMI scan-out (hdmi_scan.v).
//
// The protocol is p9term.LcdPanel.write (hobbit/tools/p9term.py), which is
// s9term's screenupdate (0x80026368) read as a panel (TERM_CHOICES 'lcd'):
//
//   +0 ctl   quad := ((quad << 6) | (data & 0x3F)) & 0xFF;  col := 0
//   +4 data  if col < 768: the cells (col, 4*quad + r), r = 0..3, take bits
//            2r+1..2r of data & 0xFF;  col := col + 1 (past 768: an overrun)
//
// Everything else the model ignores is ignored here too: the byte enables,
// data bits 31..8, and writes to any other offset.  The device is write-only
// (the kernel never reads it; the model stops on a read): a read answers 0.
// Every request, read or write, gets exactly one response (rdata 0).
//
// Storage: one 8-bit word per (quad, col), the four cells of one data write,
// at address quad * 768 + col: 256 * 768 = 196,608 bytes, one RAM write per
// data write.  Cell (x, y) is bits 2(y&3)+1..2(y&3) of word (y>>2)*768 + x.
// `col` saturates at 768: every column >= 768 is an overrun in the model, so
// holding it at 768 until the next ctl write is the same device (a 10-bit
// counter that wrapped at 1024 would write column 0 again; the synthetic
// sequence in lcd_test.py checks this).
//
// The RAM is bsc's BRAMCore dual-clock RAM (Verilog BRAM2): port A on the
// device's clock, port B on the pixel clock, no FIFO between them.  Block
// RAM powers up as zero on the ECP5, which is the model's initial panel
// (level 0 everywhere); the simulation and synthesis builds define
// BSV_NO_INITIAL_BLOCKS so BRAM2's 2'b10 fill is not used.

package LcdLcdisp;

import BRAMCore :: *;
import FIFOF    :: *;

typedef 768  LcdW;
typedef 1024 LcdH;
typedef TMul#(TDiv#(LcdH, 4), LcdW) LcdWords;     // 196608
typedef Bit#(18) LcdAddr;

interface LcdScan;
   // pixel-clock domain: data() is the word at the address given to read()
   // one pixel clock earlier (two with the output register; LcdScanLatency)
   (* always_ready *) method Action read(LcdAddr a);
   (* always_ready *) method Bit#(8) data;
endinterface

interface Lcdisp;
   // the register port of ulx3s_plan.md
   method Action req(Bit#(12) addr, Bit#(32) wdata, Bit#(4) be, Bool write);
   method ActionValue#(Bit#(32)) resp;
   // debug: data writes past column 767 since reset (LcdPanel.overruns)
   (* always_ready *) method Bit#(32) overruns;
   interface LcdScan scan;
endinterface

(* synthesize *)
module mkLcdisp#(Clock pclk)(Lcdisp);
   Clock clk <- exposeCurrentClock;
   // hasOutputRegister: the read mux of the ~96 block RAMs gets a register
   BRAM_DUAL_PORT#(LcdAddr, Bit#(8)) mem <-
      mkSyncBRAMCore2(valueOf(LcdWords), True, clk, noReset, pclk, noReset);
   Reg#(Bit#(8))  quad <- mkReg(0);
   Reg#(Bit#(10)) col  <- mkReg(0);
   Reg#(Bit#(32)) ovr  <- mkReg(0);
   FIFOF#(Bit#(32)) rsp <- mkFIFOF;

   method Action req(Bit#(12) addr, Bit#(32) wdata, Bit#(4) be, Bool write);
      rsp.enq(0);
      if (write && addr == 12'h000) begin
         quad <= truncate({quad, wdata[5:0]});
         col  <= 0;
      end
      else if (write && addr == 12'h004) begin
         if (col < 768) begin
            LcdAddr base = (zeroExtend(quad) << 9) + (zeroExtend(quad) << 8);
            mem.a.put(True, base + zeroExtend(col), wdata[7:0]);
            col <= col + 1;
         end
         else
            ovr <= ovr + 1;
      end
   endmethod

   method ActionValue#(Bit#(32)) resp;
      rsp.deq;
      return rsp.first;
   endmethod

   method Bit#(32) overruns = ovr;

   interface LcdScan scan;
      method Action read(LcdAddr a);
         mem.b.put(False, a, ?);
      endmethod
      method Bit#(8) data = mem.b.read;
   endinterface
endmodule

endpackage
