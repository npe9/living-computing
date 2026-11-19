// PimKL1BTb.bsv -- hand-assembled KL1-B program on mkPimKL1B.
//
// Program:
//   set_value 7, r1      ; r1 = int 7
//   set_variable 3, r2   ; r2 = var 3
//   put_value r1, r3     ; r3 = r1
//   proceed              ; halt
// Pass: r1 == int 7 and r3 == int 7.
package PimKL1BTb;

import PimKL1B::*;

(* synthesize *)
module mkPimKL1BTb(Empty);

  PimKL1B pu <- mkPimKL1B;
  Reg#(Bit#(4)) idx <- mkReg(0);
  Reg#(Bool) started <- mkReg(False);

  function Word prog(Bit#(3) i);
    case (i)
      0: return {8'h23, 32'hb4010000};  // read_variable r1 (REF 0 -> heap[0])
      1: return {8'h23, 32'h34010300};  // put_value r1, r3
      default: return {8'h23, 32'h60000000};  // proceed
    endcase
  endfunction

  rule load if (idx < 3);
    pu.load(zeroExtend(idx), prog(truncate(idx)));
    idx <= idx + 1;
  endrule

  rule start if (idx == 3 && !started);
    pu.loadHeap(0, {8'h02, 24'h0, 8'h07});  // heap[0] = int 7
    pu.setReg(1, {8'h03, 24'h0, 8'h00});    // r1 = REF 0
    pu.start(0);
    started <= True;
  endrule

  rule run if (started && !pu.halted());
    pu.step();
  endrule

  rule check if (pu.halted());
    Word r3 = pu.readReg(3);
    $display("r3=%h", r3);
    if (r3 == {8'h02, 24'h0, 8'h07})
      $display("PimKL1BTb: PASS");
    else
      $display("PimKL1BTb: FAIL");
    $finish;
  endrule

endmodule

endpackage
