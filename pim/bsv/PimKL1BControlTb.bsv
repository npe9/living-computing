// PimKL1BControlTb.bsv -- KL1-B goal-queue control path.
//
// TR-246 p. 3: the ready queue is a FIFO of goal records; `proceed`
// takes the head.  The model's stand-in: `enqueue_goal` appends a label
// to an 8-entry queue, `execute` jumps to its label, `proceed` pops the
// head and jumps, and `halt` stops.
//
// The test proves FIFO order, not just "does not crash": the two
// enqueued labels are 0x08 and 0x0C, and the halt lands at 0x08 only if
// the head is the first enqueued goal.  A LIFO queue would pop 0x0C and
// halt there instead.  The halt PC is checked exactly (0x09, the
// address after the halt instruction at 0x08).
//
// Program (13 words):
//   0x00 enqueue_goal 0, 0x08   ; queue[0] = 8
//   0x01 enqueue_goal 0, 0x0C   ; queue[1] = 12
//   0x02 execute 0, 0x04        ; jump to 0x04
//   0x03 halt                   ; filler
//   0x04 proceed                ; pop head -> 0x08
//   0x05 halt                   ; filler
//   0x06 halt                   ; filler
//   0x07 halt                   ; filler
//   0x08 halt                   ; expected stop
//   0x09 halt                   ; filler
//   0x0A halt                   ; filler
//   0x0B halt                   ; filler
//   0x0C halt                   ; LIFO would stop here
//
// Pass: halted at pc 0x09 (halt at 0x08 executed).
// Observed failure set (2026-11-19): changing the proceed pop to
// goals.sub(rqt - 1) (LIFO) made only this testbench print
//   halt pc=000000000d / PimKL1BControlTb: FAIL
// while the nine other KL1-B testbenches passed.  Reverted; green.
package PimKL1BControlTb;

import PimKL1B::*;

(* synthesize *)
module mkPimKL1BControlTb(Empty);

  PimKL1B pu <- mkPimKL1B;
  Reg#(Bit#(4)) idx <- mkReg(0);
  Reg#(Bool) started <- mkReg(False);

  function Word prog(Bit#(4) i);
    case (i)
      0:  return 40'h23_63_00_00_08;  // enqueue_goal 0, 0x08
      1:  return 40'h23_63_00_00_0c;  // enqueue_goal 0, 0x0C
      2:  return 40'h23_61_00_00_04;  // execute 0, 0x04
      3:  return 40'h23_71_00_00_00;  // halt (filler)
      4:  return 40'h23_60_00_00_00;  // proceed
      5:  return 40'h23_71_00_00_00;  // halt (filler)
      6:  return 40'h23_71_00_00_00;  // halt (filler)
      7:  return 40'h23_71_00_00_00;  // halt (filler)
      8:  return 40'h23_71_00_00_00;  // halt (expected stop)
      9:  return 40'h23_71_00_00_00;  // halt (filler)
      10: return 40'h23_71_00_00_00;  // halt (filler)
      11: return 40'h23_71_00_00_00;  // halt (filler)
      default: return 40'h23_71_00_00_00;  // halt (LIFO stop)
    endcase
  endfunction

  rule load if (idx < 13);
    pu.load(zeroExtend(idx), prog(idx));
    idx <= idx + 1;
  endrule

  rule start0 if (idx == 13 && !started);
    pu.start(0);
    started <= True;
  endrule

  rule run if (started && !pu.halted());
    pu.step();
  endrule

  rule check if (pu.halted());
    Word pc = pu.pc();
    $display("halt pc=%h", pc);
    if (pc[11:0] == 12'h009)
      $display("PimKL1BControlTb: PASS");
    else
      $display("PimKL1BControlTb: FAIL");
    $finish;
  endrule

endmodule

endpackage
