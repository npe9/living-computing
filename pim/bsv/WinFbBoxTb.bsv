// WinFbBoxTb: a command stream through mkWinFbBox, the frame out as PBM.
// HAND-WRITTEN (not a generated bench; pim/bsv/.gitignore ignores no
// *Tb.bsv).  Driven by bsv/run_win_tb.sh, whose header records the
// injected faults and what each was observed to fail.
//
// In the working directory, at time 0:
//   win_stream.hex   the stream (psi/winfb.py's format: one 104-bit
//                    record a line, $readmemh-readable), ending in `end`
//   win_font.hex     test_11's f822 words (psi/winfb.py fonthex)
// It writes:
//   win_frame.pbm    one PBM P4 image per `dump` and one at `end`
//   win_status.txt   each command's status, two hex digits a line
// which run_win_tb.sh compares with psi/winfb.py's for the same stream.
// It prints the cycle count from reset to the last image.
package WinFbBoxTb;

import RegFile::*;
import FIFOF::*;
import GetPut::*;
import ClientServer::*;
import Vector::*;
import WinFbBox::*;

typedef 65536 MaxCmds;

(* synthesize *)
module mkWinFbBoxTb(Empty);
   RegFile#(Bit#(16), Bit#(104)) stream <- mkRegFileLoad("win_stream.hex", 0, fromInteger(valueOf(MaxCmds) - 1));
   // one clock: the box's own clock is the scan port's (WinUlx3sTb runs two)
   Clock clk <- exposeCurrentClock;
   Reset rst <- exposeCurrentReset;
   WinFbBox box <- mkWinFbBox("win_font.hex", clk, rst);

   Reg#(Bool) started <- mkReg(False);
   Reg#(File) fFrame <- mkReg(InvalidFile);
   Reg#(File) fStatus <- mkReg(InvalidFile);
   Reg#(Bit#(16)) idx <- mkReg(0);
   Reg#(Bool) sentEnd <- mkReg(False);
   FIFOF#(Bool) finalQ <- mkSizedFIFOF(4);   // per command sent: is it the final dump
   Reg#(Bit#(17)) words <- mkReg(0);          // data words of the current image
   Reg#(Bit#(32)) cycles <- mkReg(0);
   Reg#(Bit#(32)) cmds <- mkReg(0);

   rule count;
      cycles <= cycles + 1;
   endrule

   rule open (!started);
      File f <- $fopen("win_frame.pbm", "wb");
      File s <- $fopen("win_status.txt", "w");
      if (f == InvalidFile || s == InvalidFile) begin
         $display("WinFbBoxTb: cannot open the output files");
         $finish(1);
      end
      fFrame <= f; fStatus <= s;
      started <= True;
   endrule

   rule feed (started && !sentEnd);
      Bit#(104) v = stream.sub(idx);
      Bit#(8) op = v[103:96];
      Vector#(6, Bit#(16)) a = newVector;
      for (Integer i = 0; i < 6; i = i + 1)
         a[i] = v[95 - 16 * i : 80 - 16 * i];
      if (op[7:4] == 0) begin
         // end: the final image
         box.server.request.put(WinFbCmd { op: 'h70, a: replicate(0) });
         finalQ.enq(True);
         sentEnd <= True;
      end
      else begin
         box.server.request.put(WinFbCmd { op: op, a: a });
         finalQ.enq(False);
         cmds <= cmds + 1;
         if (idx == fromInteger(valueOf(MaxCmds) - 1)) begin
            $display("WinFbBoxTb: no end record in %0d lines", valueOf(MaxCmds));
            $finish(1);
         end
         idx <= idx + 1;
      end
   endrule

   rule drain (started);
      let r <- box.server.response.get;
      if (r.isData) begin
         if (words == 0) $fwrite(fFrame, "P4\n1280 1024\n");
         $fwrite(fFrame, "%c%c", r.data[15:8], r.data[7:0]);
         words <= (words == 81919) ? 0 : words + 1;
      end
      else begin
         Bool fin = finalQ.first;
         finalQ.deq;
         if (fin) begin
            $fclose(fFrame); $fclose(fStatus);
            $display("WinFbBoxTb: %0d commands, %0d cycles", cmds, cycles);
            $finish(0);
         end
         else $fwrite(fStatus, "%02h\n", r.status);
      end
   endrule
endmodule

endpackage
