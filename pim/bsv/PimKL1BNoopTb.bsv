// PimKL1BNoopTb.bsv -- discriminating test for three no-op stand-ins.
//
// read_variable_without_deref (0xa7), wait (0xe0) and collect_value
// (0x1d) appear in real PIMOS binaries.  As stand-ins they are no-ops
// rather than halts, so the model can step past them and reach later
// instructions.  This test proves that each one advances PC without
// halting, because a sentinel register is written only after all three
// have executed.
//
// Program:
//   0: put_integer r1, 42
//   1: read_variable_without_deref r1   ; 0xa7
//   2: wait r1                           ; 0xe0
//   3: collect_value r1                  ; 0x1d
//   4: put_value r1, r2                  ; sentinel
//   5: halt
//
// Pass: halted and r2 == INT 42.
//
// Observed failure set (2026-11-19): deleting the 0xa7 case makes the
// model halt at word 1, so r2 stays zero and the test prints
//   r2=0000000000 / PimKL1BNoopTb: FAIL.
// Deleting the 0xe0 case halts at word 2 with the same effect.
// Deleting the 0x1d case halts at word 3 with the same effect.
// In each injection the ten other KL1-B testbenches remain PASS.
// Reverted; green.
package PimKL1BNoopTb;

import PimKL1B::*;

(* synthesize *)
module mkPimKL1BNoopTb(Empty);

  PimKL1B pu <- mkPimKL1B;
  Reg#(Bit#(4)) idx <- mkReg(0);
  Reg#(Bool) started <- mkReg(False);

  function Word prog(Bit#(4) i);
    case (i)
      0: return 40'h23_31_01_00_2a;   // put_integer r1, 42
      1: return 40'h23_a7_01_00_00;   // read_variable_without_deref r1
      2: return 40'h23_e0_01_00_00;   // wait r1
      3: return 40'h23_1d_01_00_00;   // collect_value r1
      4: return 40'h23_34_01_02_00;   // put_value r1, r2
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

  rule step if (started && !pu.halted());
    pu.step();
  endrule

  rule finish if (started && pu.halted());
    $display("r2=%010x", pu.readReg(2));
    if (pu.readReg(2) == 40'h02_00_00_00_2a)
      $display("PimKL1BNoopTb: PASS");
    else
      $display("PimKL1BNoopTb: FAIL");
    $finish;
  endrule
endmodule

endpackage
