// PimKL1BConstFailTb.bsv -- the wait_constant unequal (failure) case.
//
// Program:
//   set_value 8, r1
//   wait_constant r1, 7   ; unequal -> the interpreter must halt here
//   (constant word)
//   put_value r1, r3      ; must not run
//   proceed
//
// Pass: the interpreter halts and r3 is not int 8 (the value put_value
// would copy from r1 if the unequal wait_constant did not halt).
//
// Observed injection (2026-11-19): changing the wait_constant comparison
// from != to == makes this test reach put_value, printing
// "const fail case: r3=0200000008" and "PimKL1BConstFailTb: FAIL"; the
// equal case PimKL1BTb also prints FAIL. Reverting restores both.
package PimKL1BConstFailTb;

import PimKL1B::*;

(* synthesize *)
module mkPimKL1BConstFailTb(Empty);

  PimKL1B pu <- mkPimKL1B;
  Reg#(Bit#(4)) idx <- mkReg(0);
  Reg#(Bool) started <- mkReg(False);

  function Word prog(Bit#(3) i);
    case (i)
      0: return {8'h23, 32'h14080100};  // set_value 8, r1
      1: return {8'h23, 32'ha0010000};  // wait_constant r1, <next word>
      2: return {8'h02, 32'h00000007};  // the 40-bit constant: int 7
      3: return {8'h23, 32'h34010300};  // put_value r1, r3
      default: return {8'h23, 32'h60000000};  // proceed
    endcase
  endfunction

  rule load if (idx < 5);
    pu.load(zeroExtend(idx), prog(truncate(idx)));
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
    $display("const fail case: r3=%h", r3);
    if (r3 != {8'h02, 24'h0, 8'h08})
      $display("PimKL1BConstFailTb: PASS");
    else
      $display("PimKL1BConstFailTb: FAIL");
    $finish;
  endrule

endmodule

endpackage
