// PimmSdBlockFile.bsv -- the card as a host image file, for Bluesim.
// ALL OURS.  The same SdBlockServer as mkPimmSdBlock (the microSD slot),
// so mkPimmFepEmu runs unchanged on pim/tools/mkfepcard.py's image.
//
// BLUESIM ONLY: `import "BDPI"` has no Verilog form yosys takes (the
// split stretch/docs/tape_data_path.md §5 measured for its tape: a BDPI
// import compiles to a Verilog VPI task).  No board top imports this
// package.  The C side (PimmSdBlockFile.c) opens the image named by the
// environment variable PIMM_SD_IMAGE READ-ONLY ("rb") and never writes.
// The pattern is stretch/bsv/sd_reference/TapeSourceFile.bsv +
// host_tape.c (value-typed BDPI functions, callable inside a rule).

package PimmSdBlockFile;

import ClientServer::*;
import GetPut::*;
import FIFOF::*;
import PimmSdTypes::*;

import "BDPI" function Bit#(32) pimm_sd_blocks();
import "BDPI" function Bit#(8)  pimm_sd_byte(Bit#(32) block, Bit#(32) ix);

// `latency` cycles before each block's first byte (0 for none): a card
// is not instant, and the emulator must not depend on it being so.
module mkPimmSdBlockFile#(Integer latency)(SdBlockServer);
   FIFOF#(SdBlockReq)  reqF  <- mkFIFOF;
   FIFOF#(SdBlockByte) respF <- mkFIFOF;
   Reg#(Bit#(10))      ix    <- mkReg(0);
   Reg#(UInt#(16))     wait_ <- mkReg(0);
   Reg#(Bool)          going <- mkReg(False);

   rule rl_start (reqF.notEmpty && !going);
      going <= True;
      ix <= 0;
      wait_ <= fromInteger(latency);
   endrule

   rule rl_wait (going && wait_ != 0);
      wait_ <= wait_ - 1;
   endrule

   rule rl_byte (going && wait_ == 0);
      let b = reqF.first.block;
      if (b >= pimm_sd_blocks()) begin
         respF.enq(SdBlockByte { data: 0, last: True, err: True });
         reqF.deq; going <= False;
      end
      else begin
         Bool last = ix == 511;
         respF.enq(SdBlockByte { data: pimm_sd_byte(b, zeroExtend(ix)), last: last, err: False });
         ix <= ix + 1;
         if (last) begin reqF.deq; going <= False; end
      end
   endrule

   interface Put request = toPut(reqF);
   interface Get response = toGet(respF);
endmodule

endpackage
