// TapeSourceSD.bsv -- the hardware leg of TapeSource: a microSD card
// read over the 1-bit SD bus, behind the same
// Server#(TapeRequest,TapeResponse) that mkTapeSourceFile presents.
//
// The SD protocol itself is NOT reimplemented. It is
// ~/src/bsoc-cursor/FPGA-SDcard-Reader/RTL/{sd_reader,sdcmd_ctrl}.v
// (401 lines of Verilog-2001, measured at 469 LUT4 / 308 TRELLIS_FF /
// 98 CCU2C / 0 BRAM by yosys 0.51 synth_ecp5), imported with
// `import "BVI"` through a shim that splits its `inout sdcmd` into
// out/oe/in -- the same shape Sdram_Controller.bsv uses for
// sdram_dq_out / sdram_dq_oe / sdram_dq_in.
//
// Tape words are read sequentially, so the buffer is a ping-pong pair
// of 512-byte sectors (64 Word64 each) in one DP16KD: 8,192 of its
// 18,432 bits. One sector of buffered play is 512 byte-times =
// 8.19 ms at the Exchange's documented 16 us/byte worst case, against
// ~1 ms to refill it, so after the first sector of a block the
// response FIFO never runs dry in steady state.

package TapeSourceSD;

import StretchTypes::*;
import TapeSource::*;
import ClientServer::*;
import GetPut::*;
import FIFOF::*;
import BRAMCore::*;

// ---------------------------------------------------------------
// The imported Verilog core, via a shim (sd_reader_shim.v).
// ---------------------------------------------------------------
interface SDReaderPrim;
   method Action           startRead(Bit#(32) sector);
   (* always_ready *) method Bool     busy;
   (* always_ready *) method Bool     done;
   (* always_ready *) method Bool     outEn;
   (* always_ready *) method Bit#(9)  outAddr;
   (* always_ready *) method Bit#(8)  outByte;
   (* always_ready *) method Bit#(1)  sdclk;
   (* always_ready *) method Bit#(1)  sdcmdOut;
   (* always_ready *) method Bit#(1)  sdcmdOe;
   (* always_ready, always_enabled *) method Action sdcmdIn(Bit#(1) v);
   (* always_ready, always_enabled *) method Action sddat0(Bit#(1) v);
endinterface

import "BVI" sd_reader_shim =
module mkSDReaderPrim #(Integer clkDiv) (SDReaderPrim);
   parameter CLK_DIV  = clkDiv;
   parameter SIMULATE = 0;

   default_clock clk(clk);
   default_reset rstn(rstn);

   method startRead(rsector) enable(rstart);
   method rbusy    busy();
   method rdone    done();
   method outen    outEn();
   method outaddr  outAddr();
   method outbyte  outByte();
   method sdclk    sdclk();
   method sdcmd_o  sdcmdOut();
   method sdcmd_oe sdcmdOe();
   method sdcmdIn(sdcmd_i) enable((* inhigh *) EN_sdcmd_i);
   method sddat0(sddat0_i) enable((* inhigh *) EN_sddat0_i);

   schedule (busy, done, outEn, outAddr, outByte,
             sdclk, sdcmdOut, sdcmdOe, sdcmdIn, sddat0)
         CF (busy, done, outEn, outAddr, outByte,
             sdclk, sdcmdOut, sdcmdOe, sdcmdIn, sddat0);
   schedule startRead C  startRead;
   schedule startRead CF (busy, done, outEn, outAddr, outByte,
                          sdclk, sdcmdOut, sdcmdOe, sdcmdIn, sddat0);
endmodule

// ---------------------------------------------------------------
// The board-facing pin bundle, in Sdram_Controller.bsv's style.
// ---------------------------------------------------------------
interface SDPins;
   (* always_ready *) method Bit#(1) sd_clk;
   (* always_ready *) method Bit#(1) sd_cmd_out;
   (* always_ready *) method Bit#(1) sd_cmd_oe;
   (* always_ready, always_enabled *) method Action sd_cmd_in(Bit#(1) v);
   (* always_ready, always_enabled *) method Action sd_dat0_in(Bit#(1) v);
endinterface

interface TapeSourceSD;
   interface TapeSource tape;
   interface SDPins     pins;
endinterface

// baseLba: the 512-byte sector at which the tape image starts.
// clkDiv:  sd_reader's CLK_DIV (1 for a 0-25 MHz clk, 2 for 25-50 MHz).
module mkTapeSourceSD #(Integer clkDiv, Bit#(32) baseLba) (TapeSourceSD);

   SDReaderPrim prim <- mkSDReaderPrim(clkDiv);

   // Two sectors, 64 Word64 each. Bank = addr[6]. Measured at 2
   // DP16KD, not 1: 128 x 64 = 8,192 bits would fit in one 18 kbit
   // block, but a DP16KD port is at most 36 bits wide, so a 64-bit
   // word needs two blocks side by side. (yosys synth_ecp5, see
   // docs/tape_data_path.md.)
   // DUAL port, not single: with mkBRAMCore1 bsc reported
   //   Rule "rl_collect" was treated as more urgent than "rl_lookup".
   //   Conflicts: calls to sbuf.put vs. sbuf.put   (G0010)
   // -- i.e. filling one bank would block serving the other, which is
   // exactly what the ping-pong exists to avoid. Port a is the fill
   // (write) side, port b the serve (read) side; a DP16KD is natively
   // dual-ported, so this costs nothing.
   BRAM_DUAL_PORT#(Bit#(7), Word64) sbuf <- mkBRAMCore2(128, False);

   FIFOF#(TapeRequest)  reqF  <- mkFIFOF;
   FIFOF#(TapeResponse) respF <- mkFIFOF;

   // Which sector each bank holds, and whether it holds one.
   Reg#(Bit#(32)) bankLba0 <- mkReg(0);
   Reg#(Bit#(32)) bankLba1 <- mkReg(0);
   Reg#(Bool)     bankOk0  <- mkReg(False);
   Reg#(Bool)     bankOk1  <- mkReg(False);

   Reg#(Bit#(1)) fillBank <- mkReg(0);
   Reg#(Bool)    filling  <- mkReg(False);

   // Byte -> Word64 assembler. Bytes arrive MSB-first inside the
   // sector, and a 7030 word is bits 0..63 left to right, so a plain
   // shift-left assembly puts byte 8w at bits 0-7 of word w.
   Reg#(Bit#(64)) acc  <- mkReg(0);

   // One outstanding lookup (BRAM read is one cycle late).
   Reg#(Bool)     wait1  <- mkReg(False);
   Reg#(Bool)     wait1End <- mkReg(False);

   function Bit#(32) lbaOf(TapeWordAddr a) = baseLba + zeroExtend(a >> 6);
   function Bit#(6)  wordInSector(TapeWordAddr a) = truncate(a);

   // ---- fill side ----
   // Gated on `filling`, not on prim.outEn alone: sd_reader re-issues
   // CMD17 by itself when sddat_stat reaches RTIMEOUT (sd_reader.v's
   // READING2 arm), and its init sequence runs without this module
   // asking, so a byte stream can arrive that no fill of ours
   // requested. Without the guard those bytes would land in whichever
   // bank fillBank happens to name.
   rule rl_collect (filling && prim.outEn);
      Bit#(64) a = {acc[55:0], prim.outByte};
      acc <= a;
      if (prim.outAddr[2:0] == 3'b111)
         sbuf.a.put(True, {fillBank, prim.outAddr[8:3]}, a);
   endrule

   rule rl_fill_done (filling && prim.done);
      filling <= False;
      if (fillBank == 0) bankOk0 <= True; else bankOk1 <= True;
   endrule

   // ---- serve side ----
   rule rl_lookup (!wait1);
      let r = reqF.first;
      Bit#(32) want = lbaOf(r.addr);
      Bool hit0 = bankOk0 && bankLba0 == want;
      Bool hit1 = bankOk1 && bankLba1 == want;
      if (hit0 || hit1) begin
         reqF.deq;
         Bit#(1) b = hit0 ? 0 : 1;
         sbuf.b.put(False, {b, wordInSector(r.addr)}, ?);
         wait1    <= True;
         wait1End <= False;
      end
      else if (!filling && !prim.busy) begin
         // Miss: take the bank the next sequential read is least
         // likely to want, start it, and leave the request queued.
         Bit#(1) b = (bankOk0 && bankLba0 == want + 1) ? 1 : 0;
         fillBank <= b;
         if (b == 0) begin bankOk0 <= False; bankLba0 <= want; end
         else        begin bankOk1 <= False; bankLba1 <= want; end
         filling <= True;
         prim.startRead(want);
      end
   endrule

   rule rl_reply (wait1);
      respF.enq(TapeResponse { data: sbuf.b.read, atEnd: wait1End });
      wait1 <= False;
   endrule

   interface TapeSource tape;
      interface Server words;
         interface Put request  = toPut(reqF);
         interface Get response = toGet(respF);
      endinterface
      // No card-detect line is wired on the ULX3S (sd_cdn is marked
      // "not connected" in ulx3s_v20.lpf), so "media present" is
      // "the reader got a sector out of it".
      method Bool         mediaPresent = bankOk0 || bankOk1;
      method TapeWordAddr capacity     = maxBound;
   endinterface

   interface SDPins pins;
      method Bit#(1) sd_clk     = prim.sdclk;
      method Bit#(1) sd_cmd_out = prim.sdcmdOut;
      method Bit#(1) sd_cmd_oe  = prim.sdcmdOe;
      method Action  sd_cmd_in(Bit#(1) v)  = prim.sdcmdIn(v);
      method Action  sd_dat0_in(Bit#(1) v) = prim.sddat0(v);
   endinterface
endmodule

// The synthesis boundary. mkTapeSourceSD itself takes an Integer
// parameter (sd_reader's CLK_DIV is a Verilog parameter, so it has to
// be a compile-time Integer), and bsc will not give an Integer-
// parameterised module its own module: "A parameter of the module uses
// the type `Integer' which is not in the Bits class" (T0043). One
// wrapper that pins the board's values fixes that.
(* synthesize *)
module mkTapeSourceSD_ULX3S(TapeSourceSD);
   // CLK_DIV = 1 is sd_reader's own recommendation for a 0-25 MHz clk;
   // baseLba = 2048 is the usual first-partition LBA, so the image can
   // be dd'd over partition 1 of an otherwise ordinary card.
   let m <- mkTapeSourceSD(1, 2048);
   return m;
endmodule

endpackage
