// PimmSdBlock.bsv -- the ULX3S microSD slot as a block server: SPI mode,
// 512-byte block reads, and nothing else.  ALL OURS: our own design.
//
// Informed by, not copied from:
//   - stretch/bsv/sd_reference/ (TapeSourceSD.bsv; its SD core is a
//     third-party native-mode reader imported as Verilog, and
//     stretch/docs/tape_data_path.md §1 gives the slot's pins);
//   - ~/src/ulx3s-experiments/flute-lx50/src/Sd_Host.v (a
//     board-proven native 4-bit host on a register bus, driven by
//     software; it is not a block reader, and no licence file was found
//     beside it, so none of it is imported here) and that project's
//     constraints/ulx3s_85f.lpf lines 45-57 (the pins, verified on this
//     board, "microSD slot in SPI mode");
//   - the SD Physical Layer Simplified Specification's SPI mode (CMD0,
//     CMD8, CMD55+ACMD41, CMD58, CMD16, CMD17, the R1 response, the 0xFE
//     data token), as recalled: NOT a document held in this repository.
//
// READ-ONLY BY CONSTRUCTION: the only commands this module can send are
// CMD0, CMD8, CMD55, ACMD41, CMD58, CMD16 and CMD17 (READ_SINGLE_BLOCK);
// there is no write command in it, and no state that drives a card's
// data line (SPI mode: CS, SCLK and MOSI out, MISO in), so no tristate
// either: the pins are split by nature (sd_d3 = CS, sd_clk = SCLK,
// sd_cmd = MOSI, sd_d0 = MISO; sd_d1, sd_d2 are not driven).
//
// What it does: after `powerUpCycles`, 80 clocks with CS high at the slow
// clock, then CMD0 (R1 must be 01h), CMD8 0x1AA (R1 01h and the echo:
// a version 2 card; R1 with bit 2, illegal command: version 1),
// CMD55+ACMD41 (HCS set for version 2) until R1 is 00h, CMD58 (OCR bit
// 30, CCS: block addressing, else byte addressing and CMD16 512), then
// the fast clock.  A read: CMD17 (the block number, or the block times
// 512 on a byte-addressed card), R1 00h, the 0xFE token, 512 bytes, two
// CRC bytes (NOT checked: OURS), one byte with CS high.  Every wait has a
// bound, and a failure answers the request with an `err` byte; a failed
// initialization answers every request so (until reset: FIRE1 on the
// board).  The clock: SCLK half period `slowHalf` system cycles during
// initialization (25 MHz / 64 = 390 kHz with 32), `fastHalf` after
// (25 MHz / 4 = 6.25 MHz with 2).  MISO is sampled at the end of the
// high half, a half period after the card launched it on the falling
// edge.

package PimmSdBlock;

import ClientServer::*;
import GetPut::*;
import FIFOF::*;
import StmtFSM::*;
import PimmSdTypes::*;

// ---------------------------------------------------------------
// The byte engine: one SPI mode-0 byte, MSB first.
// ---------------------------------------------------------------
interface SdSpiByte;
   method Action start(Bit#(8) tx, Bool fast);
   method ActionValue#(Bit#(8)) result;
   method Bit#(1) sclk;
   method Bit#(1) mosi;
   method Action miso(Bit#(1) v);
endinterface

module mkSdSpiByte#(Integer slowHalf, Integer fastHalf)(SdSpiByte);
   Reg#(Bool)     busy  <- mkReg(False);
   Reg#(Bool)     high  <- mkReg(False);
   Reg#(Bool)     fastR <- mkReg(False);
   Reg#(UInt#(3)) bitN  <- mkReg(0);
   Reg#(UInt#(8)) cnt   <- mkReg(0);
   Reg#(Bit#(8))  txSh  <- mkReg(8'hff);
   Reg#(Bit#(8))  rxSh  <- mkReg(0);
   Reg#(Bit#(1))  sclkR <- mkReg(0);
   Reg#(Bit#(1))  mosiR <- mkReg(1);
   Reg#(Bit#(1))  misoR <- mkReg(1);     // the pad, registered
   Wire#(Bit#(1)) misoW <- mkDWire(1);
   FIFOF#(Bit#(8)) resF <- mkFIFOF;

   rule rl_pad;
      misoR <= misoW;
   endrule

   UInt#(8) half = fromInteger(fastR ? fastHalf - 1 : slowHalf - 1);

   rule rl_count (busy && cnt != 0);
      cnt <= cnt - 1;
   endrule

   rule rl_edge (busy && cnt == 0);
      cnt <= half;
      if (!high) begin               // rising edge: the card takes MOSI
         sclkR <= 1;
         high <= True;
      end
      else begin                     // end of the high half: take MISO, fall
         Bit#(8) rx = rxSh << 1 | zeroExtend(misoR);
         rxSh <= rx;
         sclkR <= 0;
         high <= False;
         if (bitN == 7) begin
            busy <= False;
            mosiR <= 1;
            resF.enq(rx);
         end
         else begin
            bitN <= bitN + 1;
            txSh <= txSh << 1;
            mosiR <= txSh[6];
         end
      end
   endrule

   method Action start(Bit#(8) tx, Bool fast) if (!busy);
      busy <= True; high <= False; bitN <= 0; fastR <= fast;
      cnt <= fromInteger(fast ? fastHalf - 1 : slowHalf - 1);
      txSh <= tx; mosiR <= tx[7]; sclkR <= 0;
   endmethod
   method ActionValue#(Bit#(8)) result;
      resF.deq;
      return resF.first;
   endmethod
   method Bit#(1) sclk = sclkR;
   method Bit#(1) mosi = mosiR;
   method Action miso(Bit#(1) v);
      misoW <= v;
   endmethod
endmodule

// ---------------------------------------------------------------
// The block reader
// ---------------------------------------------------------------
interface PimmSdBlock;
   interface SdBlockServer blocks;
   method Bool ready;                    // initialized
   method Bool failed;                   // initialization failed
   method Bit#(8) lastR1;                // for a person with a logic probe
   (* always_ready *) method Bit#(1) sd_clk;
   (* always_ready *) method Bit#(1) sd_cs_n;     // sd_d3
   (* always_ready *) method Bit#(1) sd_mosi;     // sd_cmd
   (* always_ready, always_enabled *) method Action sd_miso(Bit#(1) v);   // sd_d0
endinterface

module mkPimmSdBlock#(Integer powerUpCycles, Integer slowHalf, Integer fastHalf)(PimmSdBlock);
   SdSpiByte spi <- mkSdSpiByte(slowHalf, fastHalf);
   FIFOF#(SdBlockReq)  reqF  <- mkFIFOF;
   FIFOF#(SdBlockByte) respF <- mkFIFOF;

   Reg#(Bit#(1))   csR    <- mkReg(1);
   Reg#(Bool)      fast   <- mkReg(False);
   Reg#(Bool)      readyR <- mkReg(False);
   Reg#(Bool)      failR  <- mkReg(False);
   Reg#(Bool)      v2     <- mkReg(False);
   Reg#(Bool)      ccs    <- mkReg(False);
   Reg#(Bit#(8))   rx     <- mkReg(0);
   Reg#(Bit#(8))   r1     <- mkReg(8'hff);
   Reg#(Bit#(32))  extra  <- mkReg(0);
   Reg#(UInt#(32)) n      <- mkReg(0);
   Reg#(UInt#(32)) tries  <- mkReg(0);
   Reg#(Bool)      ok     <- mkReg(False);
   // the command in hand, for the one command sequencer
   Reg#(Bit#(6))   cIdx   <- mkReg(0);
   Reg#(Bit#(32))  cArg   <- mkReg(0);
   Reg#(Bit#(8))   cCrc   <- mkReg(0);

   function Stmt xfer(Bit#(8) b) = seq
      spi.start(b, fast);
      action let r <- spi.result; rx <= r; endaction
   endseq;

   // a command frame, then R1 (at most 10 bytes of FFh before it)
   Stmt sendCmd = seq
      xfer(8'hff);
      xfer({2'b01, cIdx});
      xfer(cArg[31:24]);
      xfer(cArg[23:16]);
      xfer(cArg[15:8]);
      xfer(cArg[7:0]);
      xfer(cCrc);
      action n <= 0; r1 <= 8'hff; endaction
      while (n < 10 && r1[7] == 1) seq
         xfer(8'hff);
         action r1 <= rx; n <= n + 1; endaction
      endseq
   endseq;
   FSM cmdFsm <- mkFSM(sendCmd);

   function Stmt command(Bit#(6) idx, Bit#(32) arg, Bit#(8) crc) = seq
      action cIdx <= idx; cArg <= arg; cCrc <= crc; endaction
      cmdFsm.start;
      await(cmdFsm.done);
   endseq;
   // four more bytes after R1 (R7, R3)
   Stmt four = seq
      n <= 0;
      while (n < 4) seq
         xfer(8'hff);
         action extra <= extra << 8 | zeroExtend(rx); n <= n + 1; endaction
      endseq
   endseq;

   Stmt init = seq
      action n <= 0; csR <= 1; fast <= False; endaction
      while (n < fromInteger(powerUpCycles)) n <= n + 1;
      n <= 0;
      while (n < 10) seq xfer(8'hff); n <= n + 1; endseq    // 80 clocks, CS high
      csR <= 0;
      action ok <= True; tries <= 0; endaction
      command(0, 0, 8'h95);                                  // GO_IDLE_STATE
      if (r1 != 8'h01) ok <= False;
      if (ok) seq
         command(8, 32'h000001aa, 8'h87);                   // SEND_IF_COND
         if (r1 == 8'h01) seq
            four;
            if (extra[11:0] == 12'h1aa) v2 <= True; else ok <= False;
         endseq
         else if (r1[2] == 1) v2 <= False;                   // illegal: version 1
         else ok <= False;
      endseq
      if (ok) seq
         r1 <= 8'h01;
         while (r1 != 8'h00 && tries < 20000 && ok) seq
            command(55, 0, 8'h65);                          // APP_CMD
            command(41, v2 ? 32'h40000000 : 0, 8'h77);      // SD_SEND_OP_COND
            if (r1[7] == 1 || (r1 & 8'hfe) != 0) ok <= False;
            tries <= tries + 1;
         endseq
         if (r1 != 8'h00) ok <= False;
      endseq
      if (ok) seq
         command(58, 0, 8'hfd);                             // READ_OCR
         if (r1 != 8'h00) ok <= False;
         else seq four; ccs <= v2 && extra[30] == 1; endseq
      endseq
      if (ok && !ccs) seq
         command(16, 512, 8'h15);                           // SET_BLOCKLEN 512
         if (r1 != 8'h00) ok <= False;
      endseq
      csR <= 1;
      xfer(8'hff);
      action fast <= True; readyR <= ok; failR <= !ok; endaction
   endseq;

   Stmt readOne = seq
      csR <= 0;
      command(17, ccs ? reqF.first.block : reqF.first.block << 9, 8'hff);   // READ_SINGLE_BLOCK
      if (r1 != 8'h00) respF.enq(SdBlockByte { data: 0, last: True, err: True });
      else seq
         action n <= 0; rx <= 8'hff; endaction
         while (n < 160000 && rx == 8'hff) seq xfer(8'hff); n <= n + 1; endseq
         if (rx != 8'hfe) respF.enq(SdBlockByte { data: 0, last: True, err: True });
         else seq
            n <= 0;
            while (n < 512) seq
               xfer(8'hff);
               action
                  respF.enq(SdBlockByte { data: rx, last: n == 511, err: False });
                  n <= n + 1;
               endaction
            endseq
            xfer(8'hff);                                    // CRC, not checked
            xfer(8'hff);
         endseq
      endseq
      csR <= 1;
      xfer(8'hff);
      reqF.deq;
   endseq;

   Stmt main = seq
      init;
      while (True) seq
         await(reqF.notEmpty);
         if (failR) action
            respF.enq(SdBlockByte { data: 0, last: True, err: True });
            reqF.deq;
         endaction
         else readOne;
      endseq
   endseq;
   FSM mainFsm <- mkFSM(main);
   Reg#(Bool) started <- mkReg(False);
   rule rl_start (!started);
      mainFsm.start;
      started <= True;
   endrule

   interface Server blocks;
      interface Put request = toPut(reqF);
      interface Get response = toGet(respF);
   endinterface
   method Bool ready = readyR;
   method Bool failed = failR;
   method Bit#(8) lastR1 = r1;
   method Bit#(1) sd_clk = spi.sclk;
   method Bit#(1) sd_cs_n = csR;
   method Bit#(1) sd_mosi = spi.mosi;
   method Action sd_miso(Bit#(1) v) = spi.miso(v);
endmodule

endpackage
