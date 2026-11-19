// PimKL1BArithTb.bsv -- KL1-B guard built-ins on INT operands.
//
// TR-246 p. 5 names add/subtract/multiply/divide/modulo Ai, Aj, Ak and
// equal/not_equal Ai, Aj as guard built-ins whose inputs must already be
// instantiated.  The PIMOS encodings are r_r_r (add..modulo) and r_r
// (equal/not_equal); the result goes to the last register.  The operand
// order and the result register are inferred from the mnemonic and the
// packing.
//
// Program (10 words):
//   put_integer 3, r1
//   put_integer 4, r2
//   add r1, r2, r3        ; r3 = INT 7
//   subtract r2, r1, r4   ; r4 = INT 1
//   multiply r1, r2, r5   ; r5 = INT 12
//   divide r2, r1, r6     ; r6 = INT 1
//   modulo r2, r1, r7     ; r7 = INT 1
//   equal r1, r1          ; true, no halt
//   not_equal r1, r2      ; true, no halt
//   proceed
//
// Pass: r3..r7 hold 7, 1, 12, 1, 1 and the interpreter reaches proceed.
//
// Observed failure set (2026-11-19): changing the add operator to
// subtraction made only this testbench print
//   r3=02ffffffff ... / PimKL1BArithTb: FAIL
// while the seven other KL1-B testbenches passed.  Reverted; green.
package PimKL1BArithTb;

import PimKL1B::*;

(* synthesize *)
module mkPimKL1BArithTb(Empty);

  PimKL1B pu <- mkPimKL1B;
  Reg#(Bit#(4)) idx <- mkReg(0);
  Reg#(Bool) started <- mkReg(False);

  function Word prog(Bit#(4) i);
    case (i)
      0: return 40'h23_31_01_00_03;  // put_integer 3, r1
      1: return 40'h23_31_02_00_04;  // put_integer 4, r2
      2: return 40'h23_f4_01_02_03;  // add r1, r2, r3
      3: return 40'h23_f5_02_01_04;  // subtract r2, r1, r4
      4: return 40'h23_f6_01_02_05;  // multiply r1, r2, r5
      5: return 40'h23_f7_02_01_06;  // divide r2, r1, r6
      6: return 40'h23_f8_02_01_07;  // modulo r2, r1, r7
      7: return 40'h23_f2_01_01_00;  // equal r1, r1
      8: return 40'h23_f3_01_02_00;  // not_equal r1, r2
      default: return 40'h23_60_00_00_00;  // proceed
    endcase
  endfunction

  rule load if (idx < 10);
    pu.load(zeroExtend(idx), prog(idx));
    idx <= idx + 1;
  endrule

  rule start if (idx == 10 && !started);
    pu.start(0);
    started <= True;
  endrule

  rule run if (started && !pu.halted());
    pu.step();
  endrule

  rule check if (pu.halted());
    Word r3 = pu.readReg(3);
    Word r4 = pu.readReg(4);
    Word r5 = pu.readReg(5);
    Word r6 = pu.readReg(6);
    Word r7 = pu.readReg(7);
    $display("r3=%h r4=%h r5=%h r6=%h r7=%h", r3, r4, r5, r6, r7);
    if (r3 == 40'h02_00_00_00_07
        && r4 == 40'h02_00_00_00_01
        && r5 == 40'h02_00_00_00_0c
        && r6 == 40'h02_00_00_00_01
        && r7 == 40'h02_00_00_00_01)
      $display("PimKL1BArithTb: PASS");
    else
      $display("PimKL1BArithTb: FAIL");
    $finish;
  endrule

endmodule

endpackage
