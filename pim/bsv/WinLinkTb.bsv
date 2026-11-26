// WinLinkTb: a host on both ends of mkWinLink's UART lines, the box behind
// it.  HAND-WRITTEN (committed); driven by bsv/run_win_link.sh, whose
// header records the injected faults and what each was observed to fail.
// OURS (docs/simpos/window_hardware_plan.md H6).
//
// In the working directory, at time 0:
//   win_link_in.hex  the down bytes, one a line (tools/winlink.py encode)
//   win_link_n.hex   their count, one hex line
//   win_font.hex     test_11's f822 words (psi/winfb.py fonthex)
// It writes win_link_out.hex: every byte read on the link's transmit line,
// one a line, which tools/winlink.py check judges.
//
// The host side keeps the link's flow-control rule (WinLink.bsv): it sends
// the bytes of frame k (k = byte / 18) only while k < answers + 8, where
// answers counts the status and error records read so far.  It stops when
// every byte is sent and the line has been idle for 400,000 cycles (longer
// than any one command: a full-screen xor fill is ~157,000).
package WinLinkTb;

import RegFile::*;
import FIFOF::*;
import GetPut::*;
import ClientServer::*;
import Connectable::*;
import WinFbBox::*;
import WinLink::*;

typedef 4 BenchDiv;           // clock cycles a bit in the bench

(* synthesize *)
module mkWinLinkTb(Empty);
   Integer div = valueOf(BenchDiv);
   RegFile#(Bit#(20), Bit#(8)) inb <- mkRegFileLoad("win_link_in.hex", 0, 'hfffff);
   RegFile#(Bit#(1), Bit#(32)) nfile <- mkRegFileLoad("win_link_n.hex", 0, 0);
   Clock clk <- exposeCurrentClock;
   Reset rst <- exposeCurrentReset;
   WinFbBox box <- mkWinFbBox("win_font.hex", clk, rst);
   WinLink link <- mkWinLink(div);
   mkConnection(link.box, box.server);

   WinUartTx host <- mkWinUartTx(div);           // the host's transmitter
   WinUartRx hrx <- mkWinUartRx(div, "WinLinkTb host");

   Reg#(File) fout <- mkReg(InvalidFile);
   Reg#(Bool) started <- mkReg(False);
   Reg#(Bit#(32)) i <- mkReg(0);
   Reg#(Bit#(32)) answers <- mkReg(0);
   Reg#(Bit#(32)) idle <- mkReg(0);
   Reg#(Bit#(32)) cycles <- mkReg(0);
   Reg#(Bit#(32)) nout <- mkReg(0);
   // the up record being read: position and length
   Reg#(Bit#(16)) rPos <- mkReg(0);
   Reg#(Bit#(8)) rType <- mkReg(0);
   Reg#(Bit#(16)) rLen <- mkReg(0);

   rule lines;
      link.rxd(host.txd);
      hrx.rxd(link.txd);
   endrule

   rule open (!started);
      File f <- $fopen("win_link_out.hex", "w");
      if (f == InvalidFile) begin
         $display("WinLinkTb: cannot open win_link_out.hex");
         $finish(1);
      end
      fout <= f;
      started <= True;
   endrule

   Bit#(32) n = nfile.sub(0);
   rule send (started && i < n && (i / 18) < answers + 8);
      host.bytes.put(inb.sub(truncate(i)));
      i <= i + 1;
   endrule

   rule receive (started);
      let b <- hrx.bytes.get;
      $fwrite(fout, "%02h\n", b);
      nout <= nout + 1;
      // count records: 5A SEQ TYPE LEN payload CRC CRC
      if (rPos == 2) rType <= b;
      if (rPos == 3) rLen <= zeroExtend(b);
      Bool endRec = rPos >= 4 && rPos == rLen + 5;
      if (endRec) begin
         rPos <= 0;
         if (rType != 1) answers <= answers + 1;
      end
      else rPos <= rPos + 1;
   endrule

   Reg#(Bool) done <- mkReg(False);
   Reg#(Bit#(32)) lastNout <- mkReg(0);
   (* descending_urgency = "receive, report" *)
   rule report (done);
      $fclose(fout);
      $display("WinLinkTb: %0d bytes down, %0d bytes up, %0d answers, %0d cycles",
               n, nout, answers, cycles);
      $finish(0);
   endrule

   rule tick (started);
      cycles <= cycles + 1;
      // idle: cycles since nout last changed
      idle <= (nout != lastNout) ? 0 : idle + 1;
      lastNout <= nout;
      if (i == n && idle == 400000) done <= True;
      if (cycles == 200000000) begin
         $display("WinLinkTb: no end after %0d cycles", cycles);
         $finish(1);
      end
   endrule
endmodule

endpackage
