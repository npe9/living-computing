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
      0: return {8'h23, 32'h14070100};  // set_value 7, r1
      1: return {8'h23, 32'h25010000};  // write_value r1 -> heap[0]
      2: return {8'h23, 32'h24020000};  // write_variable r2 -> heap[1]
      3: return {8'h23, 32'h14000300};  // set_value 0, r3
      4: return {8'h23, 32'hbd030400};  // get_bound_value r3, r4
      5: return {8'h23, 32'h14010500};  // set_value 1, r5
      6: return {8'h23, 32'hbd050600};  // get_bound_value r5, r6
      default: return {8'h23, 32'h60000000};  // proceed
    endcase
  endfunction

  rule load if (idx < 8);
    pu.load(zeroExtend(idx), prog(truncate(idx)));
    idx <= idx + 1;
  endrule

  rule start if (idx == 8 && !started);
    pu.start(0);
    started <= True;
  endrule

  rule run if (started && !pu.halted());
    pu.step();
  endrule

  rule check if (pu.halted());
    Word r4 = pu.readReg(4);
    Word r6 = pu.readReg(6);
    $display("r4=%h r6=%h", r4, r6);
    if (r4 == {8'h02, 24'h0, 8'h07} && r6[39:32] == 8'h01)
      $display("PimKL1BTb: PASS");
    else
      $display("PimKL1BTb: FAIL");
    $finish;
  endrule

endmodule

endpackage
