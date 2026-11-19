// PimUlx3s.bsv -- ULX3S board top level for the PIM/m processing element.
//
// The board provides a 25 MHz clock and an active-low reset.  The PIM/m
// local store lives in the board's 32 MB SDRAM through the Flute ULX3S
// SDRAM controller; the PIM starts once the controller's power-up
// sequence has finished.  The lower eight LEDs show the low bits of the
// PC; the top LED shows halt.
//
// The hex images are loaded at elaboration from generated/*.hex, so run
// asm/pimasm.py before compiling this module to Verilog.

package PimUlx3s;

import PimPU::*;
import PimStages::*;
import PimTypes::*;
import PimSdramStore::*;
import Sdram_Controller::*;
import Memory::*;

interface PimUlx3sIfc;
  method Bit#(8) led();
  method Bool sdram_init_done;
  method Bit#(1) sdram_cke;
  method Bit#(1) sdram_cs_n;
  method Bit#(1) sdram_ras_n;
  method Bit#(1) sdram_cas_n;
  method Bit#(1) sdram_we_n;
  method Bit#(2) sdram_ba;
  method Bit#(13) sdram_a;
  method Bit#(2) sdram_dqm;
  method Bit#(16) sdram_dq_out;
  method Bit#(1) sdram_dq_oe;
  method Action sdram_dq_in(Bit#(16) v);
endinterface

(* synthesize *)
module mkPimUlx3s#(Bit#(1) rst_n)(PimUlx3sIfc);
  Sdram_Controller_IFC sdram <- mkSdram_Controller(25_000_000);
  LocalStore store <- mkPimSdramStore(sdram.mem_server);
  PimPU pu <- mkPimPU(store);
  Reg#(Bool) started <- mkReg(False);

  rule start (!started && rst_n == 1 && sdram.init_done);
    pu.start();
    started <= True;
  endrule

  method Bit#(8) led();
    let pc = pu.pc();
    return {pack(pu.halted()), 1'b0, pc[5:0]};
  endmethod

  method Bool sdram_init_done = sdram.init_done;
  method Bit#(1) sdram_cke = sdram.sdram_cke;
  method Bit#(1) sdram_cs_n = sdram.sdram_cs_n;
  method Bit#(1) sdram_ras_n = sdram.sdram_ras_n;
  method Bit#(1) sdram_cas_n = sdram.sdram_cas_n;
  method Bit#(1) sdram_we_n = sdram.sdram_we_n;
  method Bit#(2) sdram_ba = sdram.sdram_ba;
  method Bit#(13) sdram_a = sdram.sdram_a;
  method Bit#(2) sdram_dqm = sdram.sdram_dqm;
  method Bit#(16) sdram_dq_out = sdram.sdram_dq_out;
  method Bit#(1) sdram_dq_oe = sdram.sdram_dq_oe;
  method Action sdram_dq_in(Bit#(16) v) = sdram.sdram_dq_in(v);
endmodule

endpackage
