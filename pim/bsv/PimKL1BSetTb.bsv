// PimKL1BSetTb.bsv -- KL1-B set_* / read_* argument tranche.
//
// Semantics are TR-246 p. 7 ("Set_* writes into a goal record's argument
// save area") and p. 5 (read_constant / read_integer / read_nil are
// passive unification reads).  The model keeps the argument save area in
// a small register file, args[Gi], and advances argPtr on each read.
//
// Program (14 words; the c40 instructions carry a second word):
//   set_constant C, 0    ; args[0] = C
//   set_integer 7, 1     ; args[1] = INT 7
//   set_nil 2            ; args[2] = NIL
//   set_list 3           ; args[3] = LIST(HP)
//   set_value 7, r1      ; r1 = INT 7
//   set_value 9, r2      ; r2 = INT 9
//   read_constant C      ; argPtr 0 -> 1
//   read_integer 7       ; argPtr 1 -> 2
//   put_value r1, r5     ; checked write immediately after the read
//   read_nil             ; argPtr 2 -> 3
//   put_value r2, r6     ; checked write immediately after the read
//   proceed
//
// A read opcode that wrongly consumes the next instruction as a second
// word skips one of the put_value instructions, so r5 or r6 stays
// uninitialised.  Pass: the reads do not halt, args[0..3] hold C, INT 7,
// NIL and LIST(0), and r5 == INT 7, r6 == INT 9.
//
// Observed failure set (2026-11-19): adding 0xb1 back to isC40 (the
// advertised read_integer defect) made only this testbench print
//   ... r5=aaaaaaaaaa r6=aaaaaaaaaa / PimKL1BSetTb: FAIL
// while the six other KL1-B testbenches passed.  Reverted; green.
package PimKL1BSetTb;

import PimKL1B::*;

(* synthesize *)
module mkPimKL1BSetTb(Empty);

  PimKL1B pu <- mkPimKL1B;
  Reg#(Bit#(4)) idx <- mkReg(0);
  Reg#(Bool) started <- mkReg(False);

  function Word prog(Bit#(4) i);
    case (i)
      0:  return 40'h23_10_00_00_00;  // set_constant C, 0
      1:  return 40'h02_00_00_00_33;  // C = INT 0x33
      2:  return 40'h23_11_01_00_07;  // set_integer 7, 1
      3:  return 40'h23_12_02_00_00;  // set_nil 2
      4:  return 40'h23_18_03_00_00;  // set_list 3
      5:  return 40'h23_14_07_01_00;  // set_value 7, r1
      6:  return 40'h23_14_09_02_00;  // set_value 9, r2
      7:  return 40'h23_b0_00_00_00;  // read_constant C
      8:  return 40'h02_00_00_00_33;  // C
      9:  return 40'h23_b1_00_00_07;  // read_integer 7
      10: return 40'h23_34_01_05_00;  // put_value r1, r5
      11: return 40'h23_b2_00_00_00;  // read_nil
      12: return 40'h23_34_02_06_00;  // put_value r2, r6
      default: return 40'h23_60_00_00_00;  // proceed
    endcase
  endfunction

  rule load if (idx < 14);
    pu.load(zeroExtend(idx), prog(idx));
    idx <= idx + 1;
  endrule

  rule start if (idx == 14 && !started);
    pu.start(0);
    started <= True;
  endrule

  rule run if (started && !pu.halted());
    pu.step();
  endrule

  rule check if (pu.halted());
    Word a0 = pu.readArg(0);
    Word a1 = pu.readArg(1);
    Word a2 = pu.readArg(2);
    Word a3 = pu.readArg(3);
    Word r5 = pu.readReg(5);
    Word r6 = pu.readReg(6);
    $display("a0=%h a1=%h a2=%h a3=%h r5=%h r6=%h", a0, a1, a2, a3, r5, r6);
    if (a0 == 40'h02_00_00_00_33
        && a1 == 40'h02_00_00_00_07
        && a2 == 40'h04_00_00_00_00
        && a3 == 40'h05_00_00_00_00
        && r5 == 40'h02_00_00_00_07
        && r6 == 40'h02_00_00_00_09)
      $display("PimKL1BSetTb: PASS");
    else
      $display("PimKL1BSetTb: FAIL");
    $finish;
  endrule

endmodule

endpackage
