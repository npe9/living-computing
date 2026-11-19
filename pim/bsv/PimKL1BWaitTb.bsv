// PimKL1BWaitTb.bsv -- KL1-B wait_list and wait_integer.
//
// Semantics from TR-246 p. 5 (passive unification): wait_list fails if
// the dereferenced value is not a list; wait_integer is the PIMOS
// r_c16 variant of wait_constant.  The model's failure action is a
// loud halt (the same stand-in as wait_value/wait_constant).
//
// Program:
//   put_list r1            -> r1 = LIST(HP)
//   wait_list r1           -> r1 is a list, continue
//   put_integer r2, 7      -> r2 = INT 7
//   wait_integer r2, 7     -> deref(r2) == INT 7, continue
//   proceed
//
// Pass: r1[39:32] == LIST and r2 == INT 7 and r3 == r1.  r3 is written
// only after both waits, so an early halt leaves r3 unset and fails.
//
// Observed failure set (2026-11-19): swapping the two constant bytes in
// the wait_integer comparison made only this testbench print
//   r1=0500000000 r2=0200000007 r3=aaaaaaaaaa / PimKL1BWaitTb: FAIL
// while the five other KL1-B testbenches passed.  Reverted; green.
package PimKL1BWaitTb;

import PimKL1B::*;

(* synthesize *)
module mkPimKL1BWaitTb(Empty);

  PimKL1B pu <- mkPimKL1B;
  Reg#(Bit#(4)) idx <- mkReg(0);
  Reg#(Bool) started <- mkReg(False);

  function Word prog(Bit#(4) i);
    case (i)
      0: return 40'h23_2e_01_00_00;   // put_list r1
      1: return 40'h23_a6_01_00_00;   // wait_list r1
      2: return 40'h23_31_02_00_07;   // put_integer r2, 7
      3: return 40'h23_a1_02_00_07;   // wait_integer r2, 7
      4: return 40'h23_34_01_03_00;   // put_value r1, r3
      default: return 40'h23_60_00_00_00;  // proceed
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
    let r1 = pu.readReg(1);
    let r2 = pu.readReg(2);
    let r3 = pu.readReg(3);
    $display("r1=%h r2=%h r3=%h", r1, r2, r3);
    if (r1[39:32] == 8'h05 && r2 == 40'h02_00_00_00_07 && r3 == r1)
      $display("PimKL1BWaitTb: PASS");
    else
      $display("PimKL1BWaitTb: FAIL");
    $finish;
  endrule

endmodule

endpackage
