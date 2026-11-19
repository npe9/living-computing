// PimKL1BBindTb.bsv -- KL1-B get_* binding-on-unbound path.
//
// Tests that get_integer binds an unbound REF cell instead of
// backtracking.  get_nil and get_atom share the same three-way
// structure (equal / bind-on-Var / backtrack-or-halt) and the
// GuardBacktrackTb already exercises the mismatch path; this test
// exercises the bind-only path.
//
// Program (3 words):
//   set_variable 0, r0       ; r0 = UREF(0)
//   get_integer r0, 0x2a     ; deref(UREF(0)) = tagVar -> bind r0 to INT 42
//   halt
//
// Pass: r0 == INT 42.
// Observed failure set (2026-11-19):
//   Removing the tagVar binding branch from get_integer so it always
//   backtrackOrHalt() on mismatch -> r0=0100000000, PimKL1BBindTb: FAIL.
package PimKL1BBindTb;

import PimKL1B::*;

module mkPimKL1BBindTb(Empty);

  PimKL1B pu <- mkPimKL1B;
  Reg#(Bit#(4)) idx <- mkReg(0);
  Reg#(Bool) started <- mkReg(False);

  function Word prog(Bit#(4) i);
    case (i)
      0: return {8'h23, 32'h13_00_00_00};  // set_variable 0, r0
      1: return {8'h23, 32'hB9_00_00_2A};  // get_integer r0, 42
      default: return {8'h23, 32'h71_00_00_00};  // halt
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
    Word r0 = pu.readReg(0);
    $display("r0=%h", r0);
    if (r0 == {8'h02, 24'h0, 8'h2a})
      $display("PimKL1BBindTb: PASS");
    else
      $display("PimKL1BBindTb: FAIL");
    $finish;
  endrule

endmodule

endpackage
