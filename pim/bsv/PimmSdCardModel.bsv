// PimmSdCardModel.bsv -- a microSD card in SPI mode, for Bluesim: the
// other end of mkPimmSdBlock's pins, so the reader runs in simulation
// before any board does.  ALL OURS, and only as good as our reading of
// the SD SPI protocol (the same recollection mkPimmSdBlock was written
// from; see its header): it checks the reader's framing, addressing,
// byte order and timing against one model of a card, NOT against a card.
//
// BLUESIM ONLY (its data is the host image file through
// PimmSdBlockFile's BDPI functions, read-only).  It answers CMD0 (01h),
// CMD8 (01h and the echo; or 05h if `version1`), CMD55 (01h or 00h),
// ACMD41 (01h `busyTries` times, then 00h), CMD58 (the OCR, CCS set if
// `blockAddressed`), CMD16 (00h), CMD17 (00h, `tokenDelay` bytes of FFh,
// FEh, the 512 bytes, two CRC bytes; a block past the image's end: R1
// 40h, parameter error).  Every R1 comes after one byte of FFh (NCR 1).
// Any other command: R1 04h (illegal), which the reader treats as a
// failure.  Commands are taken only with CS low; MISO is 1 with CS high.
// It has no write command either.

package PimmSdCardModel;

import FIFOF::*;
import Vector::*;
import PimmSdBlockFile::*;

interface PimmSdCardModel;
   (* always_ready, always_enabled *)
   method Action pins(Bit#(1) sclk, Bit#(1) cs_n, Bit#(1) mosi);
   (* always_ready *) method Bit#(1) miso;
   method UInt#(32) reads;          // CMD17s answered
endinterface

module mkPimmSdCardModel#(Bool blockAddressed, Bool version1, Integer busyTries,
                          Integer tokenDelay)(PimmSdCardModel);
   Wire#(Bit#(1)) sclkW <- mkBypassWire;
   Wire#(Bit#(1)) csW   <- mkBypassWire;
   Wire#(Bit#(1)) mosiW <- mkBypassWire;
   Reg#(Bit#(1))  sclkPrev <- mkReg(0);
   Reg#(UInt#(4)) bitc  <- mkReg(0);
   Reg#(Bit#(8))  rxSh  <- mkReg(0);
   Reg#(Bit#(8))  txSh  <- mkReg(8'hff);
   Reg#(Bit#(1))  misoR <- mkReg(1);
   Reg#(UInt#(3)) inFrame <- mkReg(0);       // bytes of a command frame taken
   Vector#(6, Reg#(Bit#(8))) frame <- replicateM(mkReg(0));
   // unguarded: rl_edges takes from it only if it is not empty, and must
   // fire every cycle whether it is or not
   FIFOF#(Bit#(8)) outQ <- mkUGSizedFIFOF(1024);
   Reg#(UInt#(16)) acmdCount <- mkReg(0);
   Reg#(Bool)      appCmd <- mkReg(False);
   Reg#(UInt#(32)) nReads <- mkReg(0);
   // a CMD17 being answered: the data bytes are made one at a time
   Reg#(Bool)      sending <- mkReg(False);
   Reg#(Bit#(32))  sBlock  <- mkReg(0);
   Reg#(UInt#(16)) sIx     <- mkReg(0);

   // a whole command frame, to be answered
   FIFOF#(Tuple2#(Bit#(8), Bit#(32))) cmdQ <- mkFIFOF;
   // the answer's bytes, given to outQ one a cycle
   Reg#(Vector#(6, Bit#(8))) stage <- mkReg(replicate(8'hff));
   Reg#(UInt#(3)) stageN <- mkReg(0);
   Reg#(UInt#(3)) stageK <- mkReg(0);

   rule rl_respond (stageN == 0);
      match {.cmdByte, .arg} = cmdQ.first; cmdQ.deq;
      Bit#(6) idx = cmdByte[5:0];
      Bool app = appCmd;
      appCmd <= cmdByte[5:0] == 55;
      Vector#(6, Bit#(8)) v = replicate(8'hff);   // v[0]: NCR
      UInt#(3) nb = 2;
      case (idx)
         0: v[1] = 8'h01;
         8: if (version1) v[1] = 8'h05;
            else begin
               v[1] = 8'h01; v[2] = 0; v[3] = 0; v[4] = {4'h0, arg[11:8]}; v[5] = arg[7:0]; nb = 6;
            end
         55: begin v[1] = acmdCount >= fromInteger(busyTries) ? 8'h00 : 8'h01; end
         41: if (app) begin
                if (acmdCount >= fromInteger(busyTries)) v[1] = 8'h00;
                else begin v[1] = 8'h01; acmdCount <= acmdCount + 1; end
             end
             else v[1] = 8'h04;
         58: begin
                v[1] = 8'h00; v[2] = blockAddressed ? 8'hc0 : 8'h80; v[3] = 8'hff; v[4] = 8'h80;
                v[5] = 0; nb = 6;
             end
         16: v[1] = arg == 512 ? 8'h00 : 8'h40;
         17: begin
                Bit#(32) blk = blockAddressed ? arg : arg >> 9;
                if (blk >= pimm_sd_blocks() || (!blockAddressed && arg[8:0] != 0)) v[1] = 8'h40;
                else begin
                   v[1] = 8'h00;
                   sending <= True; sBlock <= blk; sIx <= 0;
                   nReads <= nReads + 1;
                end
             end
         default: v[1] = 8'h04;
      endcase
      stage <= v; stageN <= nb; stageK <= 0;
   endrule

   rule rl_stage (stageN != 0 && outQ.notFull);
      outQ.enq(stage[stageK]);
      stageK <= stageK + 1;
      if (stageK + 1 == stageN) stageN <= 0;
   endrule

   // a CMD17's token and data, behind R1, as room allows
   rule rl_data (sending && stageN == 0 && outQ.notFull);
      UInt#(16) d = fromInteger(tokenDelay);
      if (sIx < d) outQ.enq(8'hff);
      else if (sIx == d) outQ.enq(8'hfe);
      else if (sIx < d + 513) outQ.enq(pimm_sd_byte(sBlock, zeroExtend(pack(sIx - d - 1))));
      else outQ.enq(8'h00);                  // CRC
      if (sIx == d + 514) sending <= False;
      sIx <= sIx + 1;
   endrule

   rule rl_edges;
      sclkPrev <= sclkW;
      if (csW == 1) begin
         bitc <= 0; misoR <= 1; txSh <= 8'hff; inFrame <= 0;
      end
      else if (sclkPrev == 0 && sclkW == 1) begin         // rising: take MOSI
         Bit#(8) rx = rxSh << 1 | zeroExtend(mosiW);
         rxSh <= rx;
         bitc <= bitc + 1;
         if (bitc == 7) begin
            if (inFrame == 0 && rx[7:6] == 2'b01) begin
               frame[0] <= rx; inFrame <= 1;
            end
            else if (inFrame != 0 && inFrame < 5) begin
               frame[inFrame] <= rx; inFrame <= inFrame + 1;
            end
            else if (inFrame == 5) begin                  // the CRC byte: a whole frame
               inFrame <= 0;
               cmdQ.enq(tuple2(frame[0], {frame[1], frame[2], frame[3], frame[4]}));
            end
         end
      end
      else if (sclkPrev == 1 && sclkW == 0) begin         // falling: next MISO bit
         if (bitc == 8) begin
            Bit#(8) nx = 8'hff;
            if (outQ.notEmpty) begin nx = outQ.first; outQ.deq; end
            txSh <= nx; misoR <= nx[7]; bitc <= 0;
         end
         else begin
            misoR <= txSh[6]; txSh <= txSh << 1;
         end
      end
   endrule

   method Action pins(Bit#(1) sclk, Bit#(1) cs_n, Bit#(1) mosi);
      sclkW <= sclk; csW <= cs_n; mosiW <= mosi;
   endmethod
   method Bit#(1) miso = misoR;
   method UInt#(32) reads = nReads;
endmodule

endpackage
