// PimKL1BCpTb.bsv -- choice-point backtrack path.
//
// Tests try_me_else pushing a choice point and fail popping it.
// The CP saves the else-label, argPtr, narg, and HP; on backtrack
// those are restored and PC jumps to the label.
//
// Program (7 words):
//   0x00 try_me_else 0x04   ; push CP(label=4), fall through to 0x01
//   0x01 fail               ; pop CP, backtrack to 0x04
//   0x02 halt               ; reached only if fail does not backtrack
//   0x03 halt               ; filler
//   0x04 put_integer r0, 42 ; sentinel (backtrack target)
//   0x05 halt               ; stop
//   0x06 halt               ; filler
//
// Pass: halted at pc 0x06 (halt at 0x05 executed).
// Observed failure set (2026-11-19):
//   Injected bug: fail branch changed to "haltR <= True" unconditionally
//   (removing the cpsp > 0 guard) -> pc=0x02 / PimKL1BCpTb: FAIL.
//   The sixteen other KL1-B testbenches and smoke/neg tests remained PASS.
package PimKL1BCpTb;

import PimKL1B::*;

(* synthesize *)
module mkPimKL1BCpTb(Empty);

  PimKL1B pu <- mkPimKL1B;
  Reg#(Bit#(4)) idx <- mkReg(0);
  Reg#(Bool) started <- mkReg(False);

  function Word prog(Bit#(4) i);
    case (i)
      0: return 40'h23_68_00_00_04;  // try_me_else 0x04
      1: return 40'h23_73_00_00_00;  // fail
      2: return 40'h23_71_00_00_00;  // halt (reached on no-backtrack)
      3: return 40'h23_71_00_00_00;  // halt (filler)
      4: return 40'h23_31_00_00_2a;  // put_integer r0, 42
      5: return 40'h23_71_00_00_00;  // halt (expected stop)
      default: return 40'h23_71_00_00_00;  // halt (filler)
    endcase
  endfunction

  rule load if (idx < 7);
    pu.load(zeroExtend(idx), prog(idx));
    idx <= idx + 1;
  endrule

  rule start0 if (idx == 7 && !started);
    pu.start(0);
    started <= True;
  endrule

  rule run if (started && !pu.halted());
    pu.step();
  endrule

  rule check if (pu.halted());
    Word pc = pu.pc();
    $display("halt pc=%h", pc);
    if (pc[11:0] == 12'h006)
      $display("PimKL1BCpTb: PASS");
    else
      $display("PimKL1BCpTb: FAIL");
    $finish;
  endrule

endmodule

endpackage
