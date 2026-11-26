// WinTmdsEncTb: mkWinTmdsEnc (bsv/WinScanOut.bsv) on its own, fed every
// byte from every disparity state, long constant runs, random data with
// blanking bursts and all four control inputs (psi/winscan.py `encvec`).
// HAND-WRITTEN.  The scan-out only ever encodes three levels (0x00,
// 0xff, 0x20), and a decoder recovers a byte whichever disparity branch
// was taken, so this bench is where the encoder's branches are pinned:
// psi/winscan.py `enccheck` compares every character with wintmds.encode
// (DVI 1.0 Fig. 3-5) and checks the running disparity.
//
//   win_tmds_in.hex   line 0 the count N, then N lines of 11 bits:
//                     DE << 10 | C1C0 << 8 | D
//   win_tmds_out.hex  N characters, three hex digits a line ([9:0])
package WinTmdsEncTb;

import RegFile::*;
import WinScanOut::*;

(* synthesize *)
module mkWinTmdsEncTb(Empty);
   RegFile#(Bit#(15), Bit#(16)) vec <- mkRegFileLoad("win_tmds_in.hex", 0, 32767);
   WinTmdsEnc enc <- mkWinTmdsEnc;
   Reg#(Bit#(15)) i <- mkReg(1);
   Reg#(Bool) primed <- mkReg(False);
   Reg#(File) fo <- mkReg(InvalidFile);
   Reg#(Bool) started <- mkReg(False);

   rule open (!started);
      File f <- $fopen("win_tmds_out.hex", "w");
      if (f == InvalidFile) begin
         $display("WinTmdsEncTb: cannot open the output file");
         $finish(1);
      end
      fo <= f;
      started <= True;
   endrule

   // put input i; the character of input i - 1 is out this cycle
   rule step (started);
      Bit#(16) n = vec.sub(0);
      if (primed) $fwrite(fo, "%03h\n", enc.sym);
      if (zeroExtend(i) == n + 1) begin
         $fclose(fo);
         $display("WinTmdsEncTb: %0d characters", n);
         $finish(0);
      end
      else begin
         Bit#(16) x = vec.sub(i);
         enc.put(x[10] == 1, x[9:8], x[7:0]);
         primed <= True;
         i <= i + 1;
      end
   endrule
endmodule

endpackage
