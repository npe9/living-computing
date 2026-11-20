// PimKL1BSetAtomTb.bsv -- discriminating test for set_atom operand.
//
// The model used to hardcode atom 0 in set_atom (0x00).
// This testbench verifies the operand c is used as the atom ID.
//
// Program (3 words):
//   set_atom 0, 4          ; args[0] = ATOM 4
//   put_integer 7, r1      ; r1 = INT 7
//   proceed                ; halt (empty queue)
//
// Pass: args[0] == ATOM 4.
// Fail: set_atom ignores operand c and writes ATOM 0.
//
// Observed failure set (2026-11-19): with c forced to 0, a0 = 0600000000
// and only this testbench fails (MiscTb still passes because it uses atom 0).
package PimKL1BSetAtomTb;

import PimKL1B::*;

(* synthesize *)
module mkPimKL1BSetAtomTb(Empty);

  PimKL1B pu <- mkPimKL1B;
  Reg#(Bit#(4)) idx <- mkReg(0);
  Reg#(Bool) started <- mkReg(False);

  function Word prog(Bit#(4) i);
    case (i)
      0: return 40'h23_00_00_00_04;  // set_atom 0, 4  (args[0] = ATOM 4)
      1: return 40'h23_31_01_00_07;  // put_integer 7, r1
      default: return 40'h23_60_00_00_00;  // proceed
    endcase
  endfunction

  rule load if (idx < 3);
    pu.load(zeroExtend(idx), prog(idx));
    idx <= idx + 1;
  endrule

  rule start0 if (idx == 3 && !started);
    pu.start(0);
    started <= True;
  endrule

  rule run if (started && !pu.halted());
    pu.step();
  endrule

  rule check if (pu.halted());
    Word a0 = pu.readArg(0);
    $display("a0=%h", a0);
    if (a0 == 40'h06_00_00_00_04)
      $display("PimKL1BSetAtomTb: PASS");
    else
      $display("PimKL1BSetAtomTb: FAIL");
    $finish;
  endrule

endmodule

endpackage
