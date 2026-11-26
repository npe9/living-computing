// WinScanOutTb: a command stream drawn by mkWinFbBox, then one frame (and
// a few lines more) of mkWinScanOut's TMDS characters captured.
// HAND-WRITTEN (not a generated bench).  Driven by bsv/run_win_tb.sh,
// whose header records the injected faults and what each failed.
//
// In the working directory, at time 0:
//   win_stream.hex   the drawing stream (psi/winfb.py's format), with end
//   win_font.hex     test_11's f822 words
//   win_scan.hex     the scan configuration (psi/winscan.py `config`:
//                    mode, pan, cursor, shapes, capture length, a cursor
//                    move during the capture)
// It writes:
//   win_frame.pbm    the frame after the stream (the dump at `end`)
//   win_tmds.bin     the characters from the frame-start mark on, 4 bytes
//                    a pixel clock (psi/winscan.py's header)
//   win_frame2.pbm   the frame dumped again after the capture (the
//                    cursor must not be in it)
// psi/winscan.py `check` decodes win_tmds.bin against the reference view.
package WinScanOutTb;

import RegFile::*;
import FIFOF::*;
import GetPut::*;
import ClientServer::*;
import Vector::*;
import WinFbBox::*;
import WinScanOut::*;

typedef 65536 MaxCmds;

(* synthesize *)
module mkWinScanOutTb(Empty);
   RegFile#(Bit#(16), Bit#(104)) stream <- mkRegFileLoad("win_stream.hex", 0, fromInteger(valueOf(MaxCmds) - 1));
   RegFile#(Bit#(8), Bit#(32)) cfg <- mkRegFileLoad("win_scan.hex", 0, 159);
   // one clock: the box's own clock is the scan port's (WinUlx3sTb runs two)
   Clock clk <- exposeCurrentClock;
   Reset rst <- exposeCurrentReset;
   WinFbBox box <- mkWinFbBox("win_font.hex", clk, rst);
   WinScanOut scan <- mkWinScanOut(box.scan);

   Reg#(Bit#(4)) ph <- mkReg(0);
   Reg#(File) fFrame <- mkReg(InvalidFile);
   Reg#(File) fFrame2 <- mkReg(InvalidFile);
   Reg#(File) fTmds <- mkReg(InvalidFile);
   Reg#(Bit#(16)) idx <- mkReg(0);
   Reg#(Bit#(17)) words <- mkReg(0);
   Reg#(Bit#(32)) cycles <- mkReg(0);
   Reg#(Bit#(32)) drawn <- mkReg(0);
   Reg#(Bit#(8)) si <- mkReg(0);
   Reg#(Bool) cap <- mkReg(False);
   Reg#(Bit#(32)) n <- mkReg(0);
   Reg#(Bool) secondDump <- mkReg(False);
   Reg#(Bit#(32)) nst <- mkReg(0);
   Reg#(Bool) frameDone <- mkReg(False);
   Vector#(32, Reg#(Bit#(32))) c <- replicateM(mkReg(0));
   Reg#(Bit#(5)) ci <- mkReg(0);

   rule count;
      cycles <= cycles + 1;
   endrule

   rule open (ph == 0);
      File f <- $fopen("win_frame.pbm", "wb");
      File f2 <- $fopen("win_frame2.pbm", "wb");
      File t <- $fopen("win_tmds.bin", "wb");
      if (f == InvalidFile || f2 == InvalidFile || t == InvalidFile) begin
         $display("WinScanOutTb: cannot open the output files");
         $finish(1);
      end
      fFrame <= f; fFrame2 <= f2; fTmds <= t;
      ph <= 8;
   endrule

   // 8: the configuration's first 32 words into registers
   rule load (ph == 8);
      c[ci] <= cfg.sub(zeroExtend(ci));
      if (ci == 31) ph <= 1;
      ci <= ci + 1;
   endrule

   // 1: the stream; `end` becomes the dump that writes win_frame.pbm
   rule feed (ph == 1);
      Bit#(104) v = stream.sub(idx);
      Bit#(8) op = v[103:96];
      Vector#(6, Bit#(16)) a = newVector;
      for (Integer i = 0; i < 6; i = i + 1)
         a[i] = v[95 - 16 * i : 80 - 16 * i];
      if (op[7:4] == 0) begin
         box.server.request.put(WinFbCmd { op: 'h70, a: replicate(0) });
         ph <= 2;
      end
      else begin
         box.server.request.put(WinFbCmd { op: op, a: a });
         if (idx == fromInteger(valueOf(MaxCmds) - 1)) begin
            $display("WinScanOutTb: no end record");
            $finish(1);
         end
         idx <= idx + 1;
      end
   endrule

   // every response: dump words to the current image; the status of the
   // final dump (phase 2) or of the second dump (phase 7) moves on
   rule drain;
      let r <- box.server.response.get;
      File f = secondDump ? fFrame2 : fFrame;
      if (r.isData) begin
         if (words == 0) $fwrite(f, "P4\n1280 1024\n");
         $fwrite(f, "%c%c", r.data[15:8], r.data[7:0]);
         words <= (words == 81919) ? 0 : words + 1;
      end
      else if (!secondDump) begin
         // statuses arrive in command order; the final dump's is number idx
         nst <= nst + 1;
         if (ph == 2 && nst == zeroExtend(idx)) begin
            $fclose(fFrame);
            frameDone <= True;
         end
      end
      else if (ph == 7) begin
         $fclose(fFrame2); $fclose(fTmds);
         $display("WinScanOutTb: drawn in %0d cycles, %0d clocks captured, %0d cycles in all",
                  drawn, n, cycles);
         $finish(0);
      end
   endrule

   // 3: the cursor shapes, then the position and the start
   rule afterDraw (ph == 2 && frameDone);
      drawn <= cycles;
      ph <= 3;
   endrule

   rule shapes (ph == 3);
      Bit#(32) w = cfg.sub(32 + si);
      scan.cursorShape(si[6:4], si[3:0], w[31:16], w[15:0]);
      if (si == 127) ph <= 4;
      si <= si + 1;
   endrule
   rule go (ph == 4);
      Bit#(32) m = c[0];
      Bit#(32) fl = c[9];
      WinVideoMode custom = WinVideoMode {
         ha: truncate(c[1]), hf: truncate(c[2]),
         hs: truncate(c[3]), hb: truncate(c[4]),
         va: truncate(c[5]), vf: truncate(c[6]),
         vs: truncate(c[7]), vb: truncate(c[8]),
         hpos: fl[0] == 1, vpos: fl[1] == 1,
         x0: truncate(c[10]), y0: truncate(c[11]),
         fw: truncate(c[12]), fh: truncate(c[13]), half: fl[2] == 1 };
      scan.cursorPlace(c[16] != 0, truncate(c[17]), truncate(c[18]),
                       truncate(c[19]));
      scan.start(m < 4 ? winMode(truncate(m)) : custom,
                 truncate(c[14]), truncate(c[15]));
      ph <= 5;
   endrule

   // 5: capture N clocks from the frame-start mark
   rule capture (ph == 5);
      WinTmdsOut o = scan.out;
      Bool on = cap || o.start;
      if (on) begin
         Bit#(32) w = {pack(o.start), 1'b0, o.sym[2], o.sym[1], o.sym[0]};
         $fwrite(fTmds, "%c%c%c%c", w[31:24], w[23:16], w[15:8], w[7:0]);
         cap <= True;
         if (c[21] != 0 && n == c[21])
            scan.cursorPlace(c[22] != 0, truncate(c[23]),
                             truncate(c[24]), truncate(c[25]));
         if (n + 1 == c[20]) begin
            scan.stop;
            ph <= 6;
         end
         n <= n + 1;
      end
      else if (cycles - drawn > 100000) begin
         $display("WinScanOutTb: no frame-start mark");
         $finish(1);
      end
   endrule

   // 6: the frame again, to show the cursor never entered it
   rule dump2 (ph == 6);
      box.server.request.put(WinFbCmd { op: 'h70, a: replicate(0) });
      secondDump <= True;
      ph <= 7;
   endrule
endmodule

endpackage
