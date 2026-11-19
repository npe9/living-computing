// PimKL1BSuspendTb.bsv -- KL1-B suspend with an empty ready queue.
//
// TR-246 p. 7: suspend hooks the goal onto the variables it blocked on
// and returns to the ready queue.  The model's stand-in appends the
// label to the ready queue; with the queue empty before the append, the
// only goal left is the just-appended one, so the jump target is that
// label.
//
// The regression this pins: the PC block used to read goals.sub(rqt) in
// the same cycle the enqueue wrote goals[rqt], so it read the stale
// cell (0xaaaaaaaa...), not the label it had just appended.
//
// Program (5 words):
//   0x00 suspend 0, 0x04   ; queue <- 0x04, jump to it (empty before)
//   0x01 halt              ; filler
//   0x02 halt              ; filler
//   0x03 halt              ; filler
//   0x04 halt              ; expected stop
//
// Pass: halted at pc 0x05 (halt at 0x04 executed).  With the stale read
// the jump lands at 0xaaa and the halt pc is 0xaab.
//
// Observed failure set (2026-11-19): restoring goals.sub(rqt) (the stale
// read) made only this testbench print
//   halt pc=aaaaaaaaab / PimKL1BSuspendTb: FAIL
// while the ten other KL1-B testbenches passed.  Reverted; green.
package PimKL1BSuspendTb;

import PimKL1B::*;

(* synthesize *)
module mkPimKL1BSuspendTb(Empty);

  PimKL1B pu <- mkPimKL1B;
  Reg#(Bit#(4)) idx <- mkReg(0);
  Reg#(Bool) started <- mkReg(False);

  function Word prog(Bit#(4) i);
    case (i)
      0: return 40'h23_69_00_00_04;  // suspend 0, 0x04
      1: return 40'h23_71_00_00_00;  // halt (filler)
      2: return 40'h23_71_00_00_00;  // halt (filler)
      3: return 40'h23_71_00_00_00;  // halt (filler)
      default: return 40'h23_71_00_00_00;  // halt (0x04, expected stop)
    endcase
  endfunction

  rule load if (idx < 5);
    pu.load(zeroExtend(idx), prog(idx));
    idx <= idx + 1;
  endrule

  rule start0 if (idx == 5 && !started);
    pu.start(0);
    started <= True;
  endrule

  rule run if (started && !pu.halted());
    pu.step();
  endrule

  rule check if (pu.halted());
    Word pc = pu.pc();
    $display("halt pc=%h", pc);
    if (pc[11:0] == 12'h005)
      $display("PimKL1BSuspendTb: PASS");
    else
      $display("PimKL1BSuspendTb: FAIL");
    $finish;
  endrule

endmodule

endpackage
