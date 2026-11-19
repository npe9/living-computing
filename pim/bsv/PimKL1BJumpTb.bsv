// PimKL1BJumpTb.bsv -- KL1-B unconditional jump.
//
// The PIMOS encoding is `c16_exe`: opcode 0x67 and a 16-bit label in
// bits 15-0.  The semantics (pc = label) follow the mnemonic; the
// "exe" family marks it as execution control, not a goal-record
// operation.
//
// Program (6 words):
//   0x00 jump 0x04     ; pc = 4
//   0x01 halt          ; filler (fall-through would stop here)
//   0x02 halt          ; filler
//   0x03 halt          ; filler
//   0x04 put_integer 7, r1
//   0x05 proceed
//
// Pass: r1 == INT 7, so the jump landed at 0x04 and the put_integer ran.
// A fall-through halts at 0x01 and leaves r1 unset.
//
// Observed failure set (2026-11-19): making the jump fall through
// (pcR <= pcR + 1) made only this testbench print
//   r1=aaaaaaaaaa / PimKL1BJumpTb: FAIL
// while the twelve other KL1-B testbenches passed.  Reverted; green.
package PimKL1BJumpTb;

import PimKL1B::*;

(* synthesize *)
module mkPimKL1BJumpTb(Empty);

  PimKL1B pu <- mkPimKL1B;
  Reg#(Bit#(4)) idx <- mkReg(0);
  Reg#(Bool) started <- mkReg(False);

  function Word prog(Bit#(4) i);
    case (i)
      0: return 40'h23_67_00_00_04;  // jump 0x04
      1: return 40'h23_71_00_00_00;  // halt (filler)
      2: return 40'h23_71_00_00_00;  // halt (filler)
      3: return 40'h23_71_00_00_00;  // halt (filler)
      4: return 40'h23_31_01_00_07;  // put_integer 7, r1
      default: return 40'h23_60_00_00_00;  // proceed
    endcase
  endfunction

  rule load if (idx < 6);
    pu.load(zeroExtend(idx), prog(idx));
    idx <= idx + 1;
  endrule

  rule start0 if (idx == 6 && !started);
    pu.start(0);
    started <= True;
  endrule

  rule run if (started && !pu.halted());
    pu.step();
  endrule

  rule check if (pu.halted());
    Word r1 = pu.readReg(1);
    $display("r1=%h", r1);
    if (r1 == 40'h02_00_00_00_07)
      $display("PimKL1BJumpTb: PASS");
    else
      $display("PimKL1BJumpTb: FAIL");
    $finish;
  endrule

endmodule

endpackage
