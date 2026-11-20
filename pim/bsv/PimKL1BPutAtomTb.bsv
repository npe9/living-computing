// PimKL1BPutAtomTb.bsv -- put_atom (0x40) and the 0x41-0x5f quick forms.
//
// Semantics: put_atom writes an ATOM word to a register.  The atom ID is
// inline in the instruction: the c field for the generic 0x40 form, and
// the opcode itself (op - 0x40) for the put_atom_1..31 quick forms.
//
// Program:
//   0: put_atom_4 r1              ; r1 = ATOM 4 (opcode 0x44)
//   1: put_atom_6 r2              ; r2 = ATOM 6 (opcode 0x46)
//   2: put_atom r3, 7             ; r3 = ATOM 7 (generic 0x40, c=7)
//   3: halt
//
// Pass: r1 == ATOM 4, r2 == ATOM 6, r3 == ATOM 7.
//
// Observed failure set (2026-11-19): deleting the 0x41-0x5f range check
// (making the default halt) stops the model at word 0, so all three
// registers stay uninitialized (0xaaaaaaaaaa) and the testbench prints
//   r1=aaaaaaaaaa r2=aaaaaaaaaa r3=aaaaaaaaaa
//   PimKL1BPutAtomTb: FAIL
// The other KL1-B testbenches remain PASS.  Reverted via the exact
// reverse patch; green.
package PimKL1BPutAtomTb;

import PimKL1B::*;

(* synthesize *)
module mkPimKL1BPutAtomTb(Empty);

  PimKL1B pu <- mkPimKL1B;
  Reg#(Bit#(4)) idx <- mkReg(0);
  Reg#(Bool) started <- mkReg(False);

  function Word prog(Bit#(4) i);
    case (i)
      0: return 40'h23_44_01_00_00;   // put_atom_4 r1
      1: return 40'h23_46_02_00_00;   // put_atom_6 r2
      2: return 40'h23_40_03_00_07;   // put_atom r3, 7
      default: return 40'h23_71_00_00_00;  // halt
    endcase
  endfunction

  rule load if (idx < 4);
    pu.load(zeroExtend(idx), prog(idx));
    idx <= idx + 1;
  endrule

  rule start if (idx == 4 && !started);
    pu.start(0);
    started <= True;
  endrule

  rule run if (started && !pu.halted());
    pu.step();
  endrule

  rule check if (pu.halted());
    let r1 = pu.readReg(1);
    let r2 = pu.readReg(2);
    let r3 = pu.readReg(3);
    $display("r1=%010x r2=%010x r3=%010x", r1, r2, r3);
    if (r1 == 40'h06_00_00_00_04 && r2 == 40'h06_00_00_00_06
        && r3 == 40'h06_00_00_00_07)
      $display("PimKL1BPutAtomTb: PASS");
    else
      $display("PimKL1BPutAtomTb: FAIL");
    $finish;
  endrule

endmodule

endpackage
