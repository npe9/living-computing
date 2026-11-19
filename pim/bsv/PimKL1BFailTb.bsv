// PimKL1BFailTb.bsv -- the wait_value unequal (failure) case.
//
// Program:
//   set_value 7, r1
//   set_value 8, r2
//   wait_value r1, r2   ; unequal -> the interpreter must halt here
//   put_value r1, r3    ; must not run
//   proceed
//
// Pass: the interpreter halts and r3 is not int 7.
//
// Observed injection (2026-11-19): changing the wait_value comparison
// from != to == makes the interpreter reach put_value, so the run
// prints "fail case: r3=0200000007" and "PimKL1BFailTb: FAIL".
// Reverting restores "fail case: r3=aaaaaaaaaa" and
// "PimKL1BFailTb: PASS".
package PimKL1BFailTb;

import PimKL1B::*;

(* synthesize *)
module mkPimKL1BFailTb(Empty);

  PimKL1B pu <- mkPimKL1B;
  Reg#(Bit#(3)) idx <- mkReg(0);
  Reg#(Bool) started <- mkReg(False);

  function Word prog(Bit#(3) i);
    case (i)
      0: return {8'h23, 32'h14070100};  // set_value 7, r1
      1: return {8'h23, 32'h14080200};  // set_value 8, r2
      2: return {8'h23, 32'ha4010200};  // wait_value r1, r2
      3: return {8'h23, 32'h34010300};  // put_value r1, r3
      default: return {8'h23, 32'h60000000};  // proceed
    endcase
  endfunction

  rule load if (idx < 5);
    pu.load(zeroExtend(idx), prog(idx));
    idx <= idx + 1;
  endrule

  rule start if (idx == 5 && !started);
    pu.start(0);
    started <= True;
  endrule

  rule run if (started && !pu.halted());
    pu.step();
  endrule

  rule check if (pu.halted());
    Word r3 = pu.readReg(3);
    $display("fail case: r3=%h", r3);
    if (r3 != {8'h02, 24'h0, 8'h07})
      $display("PimKL1BFailTb: PASS");
    else
      $display("PimKL1BFailTb: FAIL");
    $finish;
  endrule

endmodule

endpackage
