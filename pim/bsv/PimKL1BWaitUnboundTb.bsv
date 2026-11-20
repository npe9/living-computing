// PimKL1BWaitUnboundTb.bsv -- wait (0xe0) halts on an unbound variable.
//
// Semantics: wait is passive unification; it waits for its argument to be
// bound.  The model has no suspension mechanism, so it halts loudly on an
// unbound UREF instead of silently proceeding.  This test proves that a
// wait on an unbound variable stops the model before the sentinel executes.
//
// Program:
//   0: wait r1                     ; r1 is UREF (unbound) -> halt
//   1: put_integer r2, 99          ; sentinel; must NOT execute
//   2: halt
//
// Pass: halted and r2 != INT 99 (sentinel never ran).  An unwritten
// RegFile cell reads as 0xaaaaaaaaaa in Bluesim, so the check is "not
// the sentinel value" rather than "zero".
//
// Observed failure set (2026-11-19): reverting the 0xe0 arm to noAction
// and rebuilding, PimKL1BWaitUnboundTb prints:
//   r2=0200000063
//   PimKL1BWaitUnboundTb: FAIL
// PimKL1BNoopTb still prints r2=020000002a / PASS (its wait argument is
// bound).  The other KL1-B testbenches also remain PASS.  Reverted via
// the exact reverse patch; green.
package PimKL1BWaitUnboundTb;

import PimKL1B::*;

(* synthesize *)
module mkPimKL1BWaitUnboundTb(Empty);

  PimKL1B pu <- mkPimKL1B;
  Reg#(Bit#(4)) idx <- mkReg(0);
  Reg#(Bool) started <- mkReg(False);

  function Word prog(Bit#(4) i);
    case (i)
      0: return 40'h23_e0_01_00_00;   // wait r1 (unbound)
      1: return 40'h23_31_02_00_63;   // put_integer r2, 99 (sentinel)
      default: return 40'h23_71_00_00_00;  // halt
    endcase
  endfunction

  rule load if (idx < 3);
    pu.load(zeroExtend(idx), prog(idx));
    idx <= idx + 1;
  endrule

  rule start if (idx == 3 && !started);
    pu.setReg(1, {8'h01, 24'h0, 8'h00});  // r1 = UREF 0 (unbound)
    pu.start(0);
    started <= True;
  endrule

  rule run if (started && !pu.halted());
    pu.step();
  endrule

  rule check if (pu.halted());
    Word r2 = pu.readReg(2);
    $display("r2=%010x", r2);
    if (r2 != 40'h02_00_00_00_63)
      $display("PimKL1BWaitUnboundTb: PASS");
    else
      $display("PimKL1BWaitUnboundTb: FAIL");
    $finish;
  endrule

endmodule

endpackage
