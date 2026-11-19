// PimKL1BGuardBacktrackTb.bsv -- guard-failure backtrack path.
//
// Tests that a guard failure (equal mismatch) backtracks to the else
// label when a choice point is active.
//
// Program (9 words):
//   0x00 put_integer r0, 7   ; r0 = INT 7
//   0x01 put_integer r1, 8   ; r1 = INT 8  (different from r0 -> equal fails)
//   0x02 try_me_else 0x06    ; push CP(label=6), fall through to 0x03
//   0x03 equal r0, r1        ; guard fails -> backtrack to 0x06
//   0x04 halt                ; reached only if equal does not backtrack
//   0x05 halt                ; filler
//   0x06 put_integer r2, 42  ; sentinel (backtrack target)
//   0x07 halt                ; expected stop
//   0x08 halt                ; filler
//
// Pass: halted at pc 0x08 (halt at 0x07 executed) and r2 == INT 42.
// Observed failure set (2026-11-19):
//   Equal guard halts instead of backtracking -> pc=0x04 / r2 uninitialized.
package PimKL1BGuardBacktrackTb;

import PimKL1B::*;

(* synthesize *)
module mkPimKL1BGuardBacktrackTb(Empty);

  PimKL1B pu <- mkPimKL1B;
  Reg#(Bit#(4)) idx <- mkReg(0);
  Reg#(Bool) started <- mkReg(False);

  function Word prog(Bit#(4) i);
    case (i)
      0: return 40'h23_31_00_00_07;  // put_integer r0, 7
      1: return 40'h23_31_01_00_08;  // put_integer r1, 8
      2: return 40'h23_68_00_00_06;  // try_me_else 0x06
      3: return 40'h23_f2_00_01_00;  // equal r0, r1
      4: return 40'h23_71_00_00_00;  // halt (reached on no-backtrack)
      5: return 40'h23_71_00_00_00;  // halt (filler)
      6: return 40'h23_31_02_00_2a;  // put_integer r2, 42
      7: return 40'h23_71_00_00_00;  // halt (expected stop)
      default: return 40'h23_71_00_00_00;  // halt (filler)
    endcase
  endfunction

  rule load if (idx < 9);
    pu.load(zeroExtend(idx), prog(idx));
    idx <= idx + 1;
  endrule

  rule start0 if (idx == 9 && !started);
    pu.start(0);
    started <= True;
  endrule

  rule run if (started && !pu.halted());
    pu.step();
  endrule

  rule check if (pu.halted());
    Word pc = pu.pc();
    Word r2 = pu.readReg(2);
    $display("pc=%h r2=%h", pc, r2);
    if (pc[11:0] == 12'h008 && r2 == {8'h02, 24'h0, 8'h2a})
      $display("PimKL1BGuardBacktrackTb: PASS");
    else
      $display("PimKL1BGuardBacktrackTb: FAIL");
    $finish;
  endrule

endmodule

endpackage
