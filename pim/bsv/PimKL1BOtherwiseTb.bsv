// PimKL1BOtherwiseTb.bsv -- otherwise (0x6a) commits the choice point.
//
// Semantics: otherwise N, label discards the current choice point (the
// alternative clause) and jumps to the label with arity N, like execute
// with a CP commit.  Halts if there is no choice point to commit.
//
// Program:
//   0: try_me_else 3              ; push CP (else label = 3)
//   1: otherwise 3                ; pop CP, jump to 3
//   2: put_integer r1, 99         ; sentinel; must NOT execute
//   3: put_integer r2, 42         ; sentinel; must execute
//   4: halt
//
// Pass: halted, r2 == INT 42, r1 != INT 99.
//
// Observed failure set (2026-11-19): making otherwise a noAction (no pop,
// no jump) falls through to word 2, so r1 becomes INT 99 and the test
// prints
//   r1=0200000063 r2=020000002a
//   PimKL1BOtherwiseTb: FAIL
// The other KL1-B testbenches remain PASS.  Reverted; green.
package PimKL1BOtherwiseTb;

import PimKL1B::*;

(* synthesize *)
module mkPimKL1BOtherwiseTb(Empty);

  PimKL1B pu <- mkPimKL1B;
  Reg#(Bit#(4)) idx <- mkReg(0);
  Reg#(Bool) started <- mkReg(False);

  function Word prog(Bit#(4) i);
    case (i)
      0: return 40'h23_68_00_00_03;   // try_me_else 3
      1: return 40'h23_6a_00_00_03;   // otherwise 3
      2: return 40'h23_31_01_00_63;   // put_integer r1, 99 (sentinel)
      3: return 40'h23_31_02_00_2a;   // put_integer r2, 42
      default: return 40'h23_71_00_00_00;  // halt
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
    Word r1 = pu.readReg(1);
    Word r2 = pu.readReg(2);
    $display("r1=%010x r2=%010x", r1, r2);
    if (r2 == 40'h02_00_00_00_2a && r1 != 40'h02_00_00_00_63)
      $display("PimKL1BOtherwiseTb: PASS");
    else
      $display("PimKL1BOtherwiseTb: FAIL");
    $finish;
  endrule

endmodule

endpackage
