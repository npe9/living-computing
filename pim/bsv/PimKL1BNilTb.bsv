// PimKL1BNilTb.bsv -- KL1-B put_nil / write_nil.
//
// NIL is one of the TR-246 p. 3 tags (the model's tagNil = 0x04).  The
// PIMOS encodings are put_nil (r) and write_nil (no operand); the
// put_*/write_* semantics are TR-246 p. 7 (store a structure element /
// arrange an argument register).
//
// Program (5 words):
//   put_nil r1            ; r1 = NIL
//   write_nil             ; heap[0] = NIL, HP = 1
//   set_value 0, r4       ; r4 = INT 0 (the model's set_value convention)
//   get_bound_value r4, r5; r5 = heap[0]
//   proceed
//
// Pass: r1 == NIL and r5 == NIL.
//
// Observed failure set (2026-11-19): changing put_nil's tag to tagInt
// made only this testbench print
//   r1=0200000000 r5=0400000000 / PimKL1BNilTb: FAIL
// while the thirteen other KL1-B testbenches passed.  Reverted; green.
package PimKL1BNilTb;

import PimKL1B::*;

(* synthesize *)
module mkPimKL1BNilTb(Empty);

  PimKL1B pu <- mkPimKL1B;
  Reg#(Bit#(4)) idx <- mkReg(0);
  Reg#(Bool) started <- mkReg(False);

  function Word prog(Bit#(4) i);
    case (i)
      0: return 40'h23_32_01_00_00;  // put_nil r1
      1: return 40'h23_22_00_00_00;  // write_nil
      2: return 40'h23_14_00_04_00;  // set_value 0, r4
      3: return 40'h23_bd_04_05_00;  // get_bound_value r4, r5
      default: return 40'h23_60_00_00_00;  // proceed
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
    Word r1 = pu.readReg(1);
    Word r5 = pu.readReg(5);
    $display("r1=%h r5=%h", r1, r5);
    if (r1 == 40'h04_00_00_00_00 && r5 == 40'h04_00_00_00_00)
      $display("PimKL1BNilTb: PASS");
    else
      $display("PimKL1BNilTb: FAIL");
    $finish;
  endrule

endmodule

endpackage
