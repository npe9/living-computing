// WinInputTb: the input box (WinInput.bsv mkWinInput) at the wire level,
// plan §3.3 (2): two PS/2 device models (mkWinPs2Dev) clock the script's
// bytes into the receivers' pins, and every record out is written for
// tools/wininput.py compare.  HAND-WRITTEN (committed); driven by
// bsv/run_win_input.sh, whose header records the injected faults and what
// each was observed to fail.  OURS (window hardware H5).
//
// In the working directory, at time 0:
//   win_kbd.hex, win_mouse.hex   one line a byte: FAULT (4 bits), WAIT in
//                                ms (12), BYTE (8) (wininput.py bytes)
//   win_input_n.hex              two lines: the two files' byte counts
// It writes win_input_out.txt: one record a line, "KIND A B C FLAGS T" (A..T
// in hex), and ends when both devices are idle and nothing has come out
// for 50 ms.
//   mkWinInputTb       scaled: a bit 12 cycles, filter 2, timeout 200, a
//                      ms 100 cycles
//   mkWinInputTbBoard  the board's: a bit 2,000 cycles (80 us at 25 MHz,
//                      12.5 kHz), filter 8, timeout 25,000, a ms 25,000
package WinInputTb;

import RegFile::*;
import GetPut::*;
import WinInput::*;

module mkWinInputBench#(Integer half, Integer filt, Integer timeout, Integer msDiv)(Empty);
   RegFile#(Bit#(16), Bit#(24)) kf <- mkRegFileLoad("win_kbd.hex", 0, 'hffff);
   RegFile#(Bit#(16), Bit#(24)) mf <- mkRegFileLoad("win_mouse.hex", 0, 'hffff);
   RegFile#(Bit#(1), Bit#(32)) nf <- mkRegFileLoad("win_input_n.hex", 0, 1);
   WinInput inp <- mkWinInput(filt, timeout, msDiv);
   WinPs2Dev kd <- mkWinPs2Dev(half);
   WinPs2Dev md <- mkWinPs2Dev(half);
   Reg#(Bit#(32)) ki <- mkReg(0);
   Reg#(Bit#(32)) mi <- mkReg(0);
   Reg#(File) fout <- mkReg(InvalidFile);
   Reg#(Bool) started <- mkReg(False);
   Reg#(Bit#(32)) quiet <- mkReg(0);
   Reg#(Bit#(32)) nrec <- mkReg(0);
   Reg#(Bit#(64)) cycles <- mkReg(0);

   function Ps2DevReq req(Bit#(24) w) =
      Ps2DevReq { b: w[7:0], fault: w[23:20], delay: zeroExtend(w[19:8]) * fromInteger(msDiv) };

   rule wires;
      inp.kbd(kd.clk, kd.dat);
      inp.mouse(md.clk, md.dat);
   endrule
   rule open (!started);
      File f <- $fopen("win_input_out.txt", "w");
      fout <= f; started <= True;
   endrule
   rule sendK (started && ki < nf.sub(0));
      kd.req.put(req(kf.sub(truncate(ki))));
      ki <= ki + 1;
   endrule
   rule sendM (started && mi < nf.sub(1));
      md.req.put(req(mf.sub(truncate(mi))));
      mi <= mi + 1;
   endrule
   (* descending_urgency = "out, tick" *)
   rule out (started);
      let e <- inp.events.get;
      $fwrite(fout, "%0d %04h %04h %04h %02h %04h\n", e.kind, e.a, e.b, e.c, e.flags, e.t);
      quiet <= 0; nrec <= nrec + 1;
   endrule
   rule tick (started);
      cycles <= cycles + 1;
      Bool done = ki == nf.sub(0) && mi == nf.sub(1) && kd.idle && md.idle;
      quiet <= done ? quiet + 1 : 0;
      if (quiet == fromInteger(50 * msDiv)) begin
         $fclose(fout);
         $display("WinInputTb: %0d records, %0d cycles", nrec, cycles);
         $finish(0);
      end
   endrule
endmodule

(* synthesize *)
module mkWinInputTb(Empty);
   mkWinInputBench(6, 2, 200, 100);
endmodule

(* synthesize *)
module mkWinInputTbBoard(Empty);
   mkWinInputBench(1000, 8, 25000, 25000);
endmodule

endpackage
