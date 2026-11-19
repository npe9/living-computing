// PimKL1BMiscTb.bsv -- remaining untested KL1-B stand-ins.
//
// Covers put_variable/get_value (argument-register moves) and
// set_atom/read_atom (the placeholder atom representation).  The atom
// table is not modelled, so set_atom writes tagAtom with value 0 and
// read_atom only checks the tag; the doc labels that a gap.
//
// Program (7 words):
//   put_integer 7, r1      ; r1 = INT 7
//   put_variable r1, r2    ; r2 = UREF(r1)
//   get_value r2, r3       ; r3 = r2
//   set_atom 0, 0          ; args[0] = ATOM
//   read_atom              ; args[0] is ATOM, argPtr advances
//   put_value r1, r4       ; checked write after the read
//   proceed
//
// Pass: r2 == r3 == UREF(1), args[0] carries tagAtom, r4 == INT 7.
//
// Observed failure set (2026-11-19): changing put_variable's tag to
// tagInt made only this testbench print
//   r2=0200000001 r3=0200000001 r4=0200000007 a0=0600000000
//   PimKL1BMiscTb: FAIL
// while the eleven other KL1-B testbenches passed.  Reverted; green.
package PimKL1BMiscTb;

import PimKL1B::*;

(* synthesize *)
module mkPimKL1BMiscTb(Empty);

  PimKL1B pu <- mkPimKL1B;
  Reg#(Bit#(4)) idx <- mkReg(0);
  Reg#(Bool) started <- mkReg(False);

  function Word prog(Bit#(4) i);
    case (i)
      0: return 40'h23_31_01_00_07;  // put_integer 7, r1
      1: return 40'h23_33_01_02_00;  // put_variable r1, r2
      2: return 40'h23_bc_02_03_00;  // get_value r2, r3
      3: return 40'h23_00_00_00_00;  // set_atom 0, 0
      4: return 40'h23_b3_00_00_00;  // read_atom
      5: return 40'h23_34_01_04_00;  // put_value r1, r4
      default: return 40'h23_60_00_00_00;  // proceed
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
    Word r2 = pu.readReg(2);
    Word r3 = pu.readReg(3);
    Word r4 = pu.readReg(4);
    Word a0 = pu.readArg(0);
    $display("r2=%h r3=%h r4=%h a0=%h", r2, r3, r4, a0);
    if (r2 == 40'h01_00_00_00_01
        && r3 == 40'h01_00_00_00_01
        && a0[39:32] == 8'h06
        && r4 == 40'h02_00_00_00_07)
      $display("PimKL1BMiscTb: PASS");
    else
      $display("PimKL1BMiscTb: FAIL");
    $finish;
  endrule

endmodule

endpackage
