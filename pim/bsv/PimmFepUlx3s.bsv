// PimmFepUlx3s.bsv -- the FEP emulator on the ULX3S, with a self-test in
// place of the PIM/m core.  ALL OURS.
//
// mkPimmFepUlx3s (synthesized; Verilog top PimmFepTop.v, pins
// ulx3s_fep.lpf, build run_fepemu_fpga.sh) is mkPimmFepSelfTest over
// mkPimmSdBlock, the microSD slot in SPI mode.  The self-test plays the
// IPL's part, through the emulator's own command interface (the one
// the core's scsi_command will drive):
//   1. reads the card's directory itself (block 0, then the first
//      directory block): entry 0's name, length and sum (mkfepcard.py
//      puts pimos:pimos.ipl first);
//   2. TEST UNIT READY; SEND read_open of that name, as the IPL packs it
//      (device 0: {201, 4 arguments: "", 0, 0, the name}); RECEIVE,
//      status 1 wanted;
//   3. SEND getb 7936, RECEIVE, until status 2 (end of data), summing
//      the bytes given and counting them;
//   4. SEND close, RECEIVE, status 1 wanted;
//   5. PASS if every status was as wanted and the count and the sum are
//      the directory's.
// Then it reports, at 115200 8N1 on the FTDI line the FPGA transmits on
// (ftdi_rxd, L4: "FPGA transmits to ftdi" in ulx3s_v20.lpf; the name is
// the FTDI chip's side), every 2^25 cycles (1.3 s), so a terminal can be
// attached at any time:
//   "PIMFEP PASS n=0000068e s=00019246 want n=0000068e s=00019246\r\n"
//   ("FAIL" and the step number, 1..5, where it stopped, otherwise).
// LEDs: 0 card initialized, 1 card failed, 2 emulator mounted the card,
// 3 PASS, 4 FAIL, 7..5 the step.
//
// It ONLY READS: mkPimmSdBlock has no write command, and nothing here
// asks for one.

package PimmFepUlx3s;

import ClientServer::*;
import GetPut::*;
import FIFOF::*;
import Vector::*;
import List::*;
import BRAMCore::*;
import StmtFSM::*;
import PimmSdTypes::*;
import PimmSdBlock::*;
import PimmFepEmu::*;

// ---------------------------------------------------------------
// A UART transmitter, 8N1.
// ---------------------------------------------------------------
interface UartTx;
   interface Put#(Bit#(8)) chars;
   method Bit#(1) txd;
endinterface

module mkUartTx#(Integer divisor)(UartTx);
   FIFOF#(Bit#(8)) q <- mkSizedFIFOF(4);
   Reg#(Bit#(10))  sh  <- mkReg('1);
   Reg#(UInt#(4))  n   <- mkReg(0);
   Reg#(UInt#(16)) cnt <- mkReg(0);

   rule rl_load (n == 0);
      sh <= {1'b1, q.first, 1'b0};      // stop, data LSB first, start
      q.deq;
      n <= 10;
      cnt <= fromInteger(divisor - 1);
   endrule
   rule rl_shift (n != 0);
      if (cnt == 0) begin
         cnt <= fromInteger(divisor - 1);
         sh <= {1'b1, sh[9:1]};
         n <= n - 1;
      end
      else cnt <= cnt - 1;
   endrule

   interface Put chars = toPut(q);
   method Bit#(1) txd = n == 0 ? 1 : sh[0];
endmodule

// ---------------------------------------------------------------
// The self-test.
// ---------------------------------------------------------------
interface FepSelfTest;
   method Bit#(8) led;
   method Bool finished;
   method Bool passed;
   method Bit#(1) txd;
endinterface

module mkPimmFepSelfTest#(SdBlockServer sd, Bool cardReady, Bool cardFailed,
                          Integer uartDivisor, Integer reportCycles)(FepSelfTest);
   PimmFepEmu emu  <- mkPimmFepEmu;
   UartTx     uart <- mkUartTx(uartDivisor);
   BRAM_PORT#(Bit#(8), Bit#(8)) nameMem <- mkBRAMCore1(256, False);

   Reg#(Bool)      phaseEmu <- mkReg(False);   // the card: False the self-test's, True the emulator's
   Reg#(UInt#(3))  step   <- mkReg(0);
   Reg#(Bool)      fin    <- mkReg(False);
   Reg#(Bool)      pass   <- mkReg(False);
   Reg#(Bit#(32))  dirFirst <- mkReg(0);
   Reg#(UInt#(32)) nameLen <- mkReg(0);
   Reg#(Bit#(32))  wantLen <- mkReg(0);
   Reg#(Bit#(32))  wantSum <- mkReg(0);
   Reg#(Bit#(32))  gotLen  <- mkReg(0);
   Reg#(Bit#(32))  gotSum  <- mkReg(0);
   Reg#(UInt#(32)) k      <- mkReg(0);
   Reg#(UInt#(32)) cnt    <- mkReg(0);
   Reg#(Bit#(32))  acc    <- mkReg(0);
   Reg#(Bit#(32))  status <- mkReg(0);
   Reg#(Bit#(32))  dlen   <- mkReg(0);
   Reg#(Bool)      bad    <- mkReg(False);
   Reg#(Bool)      eod    <- mkReg(False);
   Reg#(Bit#(8))   bt     <- mkReg(0);
   Reg#(UInt#(32)) timer  <- mkReg(0);

   // the FEP's clock (setTime, get_date_time's time of day): a counter in
   // 1/16 msec, one tick every 1,563 cycles (1/16 msec at 25 MHz, OURS).
   // The self-test does not ask the time; the clock is driven so that the
   // board's build holds the emulator's time path
   Reg#(Bit#(48))  ticks  <- mkReg(0);
   Reg#(UInt#(11)) pre    <- mkReg(0);
   rule rl_clock;
      if (pre == 1562) begin pre <= 0; ticks <= ticks + 1; end
      else pre <= pre + 1;
      emu.setTime(ticks);
   endrule

   // the card, shared: the self-test's direct reads first, then the emulator
   FIFOF#(SdBlockByte) direct <- mkFIFOF;
   rule rl_emu_req (phaseEmu);
      let r <- emu.card.request.get; sd.request.put(r);
   endrule
   rule rl_emu_resp (phaseEmu);
      let b <- sd.response.get; emu.card.response.put(b);
   endrule
   rule rl_direct_resp (!phaseEmu);
      let b <- sd.response.get; direct.enq(b);
   endrule

   // one block, bytes [from, from+n) noted by `take`
   function Stmt readBlock(Bit#(32) blk, function Action take(UInt#(32) i, Bit#(8) b)) = seq
      sd.request.put(SdBlockReq { block: blk });
      action k <= 0; bad <= False; endaction
      while (k < 512 && !bad) action
         let b = direct.first; direct.deq;
         if (b.err) bad <= True;
         else take(k, b.data);
         k <= k + 1;
      endaction
   endseq;

   function Action noteHeader(UInt#(32) i, Bit#(8) b) = action
      if (i >= 12 && i < 16) dirFirst <= dirFirst << 8 | zeroExtend(b);
   endaction;
   function Action noteEntry(UInt#(32) i, Bit#(8) b) = action
      if (i < 4) nameLen <= unpack(pack(nameLen) << 8 | zeroExtend(b));
      else if (i >= 8 && i < 12) wantLen <= wantLen << 8 | zeroExtend(b);
      else if (i >= 12 && i < 16) wantSum <= wantSum << 8 | zeroExtend(b);
      else if (i >= 16 && i < 256) nameMem.put(True, truncate(pack(i - 16)), b);
   endaction;

   function Vector#(12, Bit#(8)) cdbOf(Bit#(8) op, Bit#(8) lun, UInt#(24) n);
      Vector#(12, Bit#(8)) c = replicate(0);
      Bit#(24) b = pack(n);
      c[0] = op; c[1] = lun << 5; c[2] = b[23:16]; c[3] = b[15:8]; c[4] = b[7:0];
      return c;
   endfunction
   function Action command(Bit#(8) op, Bit#(32) lun, Bit#(2) dir, UInt#(24) n) =
      emu.cmd.request.put(FepCmd { unit: 7, lun: lun, cdbLen: 5, cdb: cdbOf(op, truncate(lun), n),
                                   dir: dir, length: n });

   // the words of a request, after the 8-byte header of zeros (device 0,
   // flag 0)
   function Bit#(32) openWord(UInt#(32) i) = case (i)
      0: 201; 1: 4; 2: 0; 3: 32'hffffffff; 4: 32'hffffffff; 5: pack(nameLen);
      default: 0; endcase;
   function Bit#(8) wordByte(Bit#(32) w, UInt#(32) i) =
      case (i % 4) 0: w[31:24]; 1: w[23:16]; 2: w[15:8]; default: w[7:0]; endcase;
   function UInt#(32) pad4(UInt#(32) n) = unpack((~pack(n) + 1) & 3);
   UInt#(32) openLen = 8 + 32 + nameLen + pad4(nameLen);
   function Bit#(32) getbWord(UInt#(32) i) = case (i)
      0: 210; 1: 1; 2: 32'hffffffff; default: 7936; endcase;     // {210, 1 argument: 7936}
   function Bit#(32) closeWord(UInt#(32) i) = i == 0 ? 60 : 0;   // {60, no arguments}

   // a RECEIVE: the answer, then its bytes: the status at 8, the
   // length at 16, the data from 20
   Stmt receive = seq
      command(8'h08, 1, 2, 16000);
      action
         let a <- emu.cmd.response.get;
         if (a.kind != FepDone) bad <= True;
         cnt <= zeroExtend(a.count); k <= 0; status <= 0; dlen <= 0;
      endaction
      while (k < cnt) action
         let b <- emu.recvData.get;
         if (k >= 8 && k < 12) status <= status << 8 | zeroExtend(b);
         if (k >= 16 && k < 20) dlen <= dlen << 8 | zeroExtend(b);
         if (k >= 20 && k < 20 + unpack(dlen)) begin
            gotSum <= gotSum + zeroExtend(b);
            gotLen <= gotLen + 1;
         end
         k <= k + 1;
      endaction
   endseq;
   Stmt sendDone = seq
      action
         let a <- emu.cmd.response.get;
         if (a.kind != FepDone) bad <= True;
      endaction
   endseq;

   function Action hexTo(Bit#(32) v, UInt#(32) i);
      Bit#(4) d = v[31 - 4 * i : 28 - 4 * i];
      return uart.chars.put(d < 10 ? zeroExtend(d) + 48 : zeroExtend(d) + 87);
   endfunction
   function Stmt putc(Integer c) = seq uart.chars.put(fromInteger(c)); endseq;
   function Stmt text(String s);
      Stmt r = seq noAction; endseq;
      List#(Char) cs = stringToCharList(s);
      for (Integer i = 0; i < length(cs); i = i + 1)
         r = seq r; putc(charToInteger(cs[i])); endseq;
      return r;
   endfunction
   function Stmt hex(Bit#(32) v) = seq
      k <= 0;
      while (k < 8) action hexTo(v, k); k <= k + 1; endaction
   endseq;

   Stmt run = seq
      await(cardReady || cardFailed);
      step <= 1;
      if (cardReady) seq
         readBlock(0, noteHeader);
         if (!bad) readBlock(dirFirst, noteEntry);
      endseq
      action phaseEmu <= True; if (cardFailed || bad || nameLen == 0 || nameLen > 240) fin <= True; endaction
      if (!fin) seq
         // 2: TEST UNIT READY, read_open, RECEIVE
         step <= 2;
         command(8'h00, 0, 0, 0);
         sendDone;
         command(8'h0a, 0, 1, truncate(openLen));
         k <= 0;
         while (k < openLen) seq
            if (k < 8) noAction;
            else if (k < 40) noAction;
            else if (k < 40 + nameLen) nameMem.put(False, truncate(pack(k - 40)), ?);
            action
               emu.sendData.put(k < 8 ? 0 : k < 40 ? wordByte(openWord((k - 8) / 4), k - 8)
                                : k < 40 + nameLen ? nameMem.read : 0);
               k <= k + 1;
            endaction
         endseq
         sendDone;
         receive;
         if (bad || status != 1) fin <= True;
      endseq
      if (!fin) seq
         // 3: getb to the end of data
         action step <= 3; gotLen <= 0; gotSum <= 0; eod <= False; endaction
         while (!eod && !bad) seq
            command(8'h0a, 0, 1, 24);
            k <= 0;
            while (k < 24) action
               emu.sendData.put(k < 8 ? 0 : wordByte(getbWord((k - 8) / 4), k - 8));
               k <= k + 1;
            endaction
            sendDone;
            receive;
            if (status == 2) eod <= True;
            else if (status != 1) bad <= True;
         endseq
         if (bad) fin <= True;
      endseq
      if (!fin) seq
         // 4: close
         step <= 4;
         command(8'h0a, 0, 1, 16);
         k <= 0;
         while (k < 16) action
            emu.sendData.put(k < 8 ? 0 : wordByte(closeWord((k - 8) / 4), k - 8));
            k <= k + 1;
         endaction
         sendDone;
         receive;
         if (bad || status != 1) fin <= True;
      endseq
      if (!fin) action
         step <= 5;
         pass <= gotLen == wantLen && gotSum == wantSum;
      endaction
      fin <= True;
      // the report, again and again
      while (True) seq
         text("PIMFEP ");
         if (pass) text("PASS"); else seq text("FAIL step "); uart.chars.put(48 + zeroExtend(pack(step))); endseq
         text(" n="); hex(gotLen); text(" s="); hex(gotSum);
         text(" want n="); hex(wantLen); text(" s="); hex(wantSum);
         putc(13); putc(10);
         timer <= 0;
         while (timer < fromInteger(reportCycles)) timer <= timer + 1;
      endseq
   endseq;
   FSM fsm <- mkFSM(run);
   Reg#(Bool) started <- mkReg(False);
   rule rl_go (!started);
      fsm.start; started <= True;
   endrule

   method Bit#(8) led = {pack(step), pack(fin && !pass), pack(pass),
                         pack(emu.mounted == MountOk), pack(cardFailed), pack(cardReady)};
   method Bool finished = fin;
   method Bool passed = pass;
   method Bit#(1) txd = uart.txd;
endmodule

// ---------------------------------------------------------------
// The board.
// ---------------------------------------------------------------
interface PimmFepUlx3sIfc;
   (* always_ready *) method Bit#(8) led;
   (* always_ready *) method Bit#(1) uart_tx;      // ftdi_rxd
   (* always_ready *) method Bit#(1) sd_clk;
   (* always_ready *) method Bit#(1) sd_cs_n;      // sd_d3
   (* always_ready *) method Bit#(1) sd_mosi;      // sd_cmd
   (* always_ready, always_enabled *) method Action sd_miso(Bit#(1) v);   // sd_d0
endinterface

// 25 MHz: a 10 ms power-up wait, 390 kHz then 6.25 MHz card clock,
// 115200 baud (217 cycles a bit), a report every 2^25 cycles
(* synthesize *)
module mkPimmFepUlx3s(PimmFepUlx3sIfc);
   PimmSdBlock sd <- mkPimmSdBlock(250000, 32, 2);
   FepSelfTest st <- mkPimmFepSelfTest(sd.blocks, sd.ready, sd.failed, 217, 33554432);
   method Bit#(8) led = st.led;
   method Bit#(1) uart_tx = st.txd;
   method Bit#(1) sd_clk = sd.sd_clk;
   method Bit#(1) sd_cs_n = sd.sd_cs_n;
   method Bit#(1) sd_mosi = sd.sd_mosi;
   method Action sd_miso(Bit#(1) v) = sd.sd_miso(v);
endmodule

endpackage
