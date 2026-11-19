// PimKL1BGetTb.bsv -- KL1-B active-unification get_* reads.
//
// TR-246 p. 6 lists get_constant/get_integer/get_nil/get_atom among the
// active-unification instructions, which never suspend.  The model's
// behaviour: compare the dereferenced argument register with the
// constant/type and halt loudly on a mismatch; get_constant also binds
// an unbound REF cell to the constant.
//
// Program (8 words):
//   put_integer 7, r1      ; r1 = INT 7
//   get_integer 7, r1      ; equal -> continue
//   get_constant C, r1     ; equal -> continue
//   C                      ; INT 7
//   get_nil r2             ; r2 = NIL (test setup)
//   get_atom r3            ; r3 = ATOM (test setup)
//   put_value r1, r4       ; checked write after the gets
//   proceed
//
// Pass: the four get_* instructions do not halt, r1 stays INT 7 and
// r4 == INT 7.  A get_* that halts or skips leaves r4 unset.
//
// Observed failure set (2026-11-19): changing get_integer's comparison
// to val[15:0] + 1 made only this testbench print
//   r1=0200000007 r4=aaaaaaaaaa / PimKL1BGetTb: FAIL
// while the eight other KL1-B testbenches passed.  Reverted; green.
package PimKL1BGetTb;

import PimKL1B::*;

(* synthesize *)
module mkPimKL1BGetTb(Empty);

  PimKL1B pu <- mkPimKL1B;
  Reg#(Bit#(4)) idx <- mkReg(0);
  Reg#(Bit#(2)) startStep <- mkReg(0);
  Reg#(Bool) started <- mkReg(False);

  function Word prog(Bit#(4) i);
    case (i)
      0: return 40'h23_31_01_00_07;  // put_integer 7, r1
      1: return 40'h23_b9_01_00_07;  // get_integer 7, r1
      2: return 40'h23_b8_01_00_00;  // get_constant C, r1
      3: return 40'h02_00_00_00_07;  // C = INT 7
      4: return 40'h23_ba_02_00_00;  // get_nil r2
      5: return 40'h23_c0_03_00_00;  // get_atom r3
      6: return 40'h23_34_01_04_00;  // put_value r1, r4
      default: return 40'h23_60_00_00_00;  // proceed
    endcase
  endfunction

  rule load if (idx < 8);
    pu.load(zeroExtend(idx), prog(idx));
    idx <= idx + 1;
  endrule

  rule start0 if (idx == 8 && startStep == 0);
    pu.setReg(2, {8'h04, 24'h0, 0});  // r2 = NIL
    startStep <= 1;
  endrule

  rule start1 if (startStep == 1);
    pu.setReg(3, {8'h06, 24'h0, 0});  // r3 = ATOM
    startStep <= 2;
  endrule

  rule start2 if (startStep == 2 && !started);
    pu.start(0);
    started <= True;
    startStep <= 3;
  endrule

  rule run if (started && !pu.halted());
    pu.step();
  endrule

  rule check if (pu.halted());
    Word r1 = pu.readReg(1);
    Word r4 = pu.readReg(4);
    $display("r1=%h r4=%h", r1, r4);
    if (r1 == 40'h02_00_00_00_07 && r4 == 40'h02_00_00_00_07)
      $display("PimKL1BGetTb: PASS");
    else
      $display("PimKL1BGetTb: FAIL");
    $finish;
  endrule

endmodule

endpackage
