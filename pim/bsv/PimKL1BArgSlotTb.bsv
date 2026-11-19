// PimKL1BArgSlotTb.bsv -- argument-slot width (Gi is an 8-bit field).
//
// The model's args area was RegFile#(Bit#(3), Word) and every set_*
// truncated Gi to 3 bits, so Gi >= 8 silently aliased slots 0-7. This
// bench writes slot 8 and slot 0 with different constants and checks
// both read back distinctly.
//
// Program:
//   0: set_constant C8, G8   ; args[8] = C8
//   1: C8
//   2: set_constant C0, G0   ; args[0] = C0
//   3: C0
//   4: proceed
//
// Pass: readArg(8) == C8 and readArg(0) == C0. Under the old 3-bit
// truncation, args[8] aliases args[0], so readArg(8) would equal C0.
//
// Observed failure set (injection: set_constant writes `a & 8'h07`
// instead of `a`, so slot 8 aliases slot 0):
//   a8=aaaaaaaaaa a0=2222222222; PimKL1BArgSlotTb FAIL; the other
//   fourteen benches PASS.
package PimKL1BArgSlotTb;

import PimKL1B::*;

(* synthesize *)
module mkPimKL1BArgSlotTb(Empty);

  PimKL1B pu <- mkPimKL1B;

  // Word layout: tag[8] opcode[8] a[8] b[8] c[8].
  function Word inst(Bit#(8) op, Bit#(8) a) =
      {8'h23, op, a, 8'h00, 8'h00};

  function Word prog(Bit#(12) a);
    case (a)
      0: return inst(8'h10, 8'h08);   // set_constant C8, G8
      1: return 40'h11_1111_1111;     // C8
      2: return inst(8'h10, 8'h00);   // set_constant C0, G0
      3: return 40'h22_2222_2222;     // C0
      default: return 40'h23_60_00_00_00;  // proceed
    endcase
  endfunction

  Reg#(Bit#(12)) idx <- mkReg(0);
  Reg#(Bool) started <- mkReg(False);

  rule load if (idx < 5);
    pu.load(idx, prog(idx));
    idx <= idx + 1;
  endrule

  rule start if (idx == 5 && !started);
    pu.start(0);
    started <= True;
  endrule

  rule run if (started && !pu.halted());
    pu.step();
  endrule

  rule check if (pu.halted());
    let a8 = pu.readArg(8);
    let a0 = pu.readArg(0);
    $display("a8=%h a0=%h", a8, a0);
    if (a8 == 40'h11_1111_1111 && a0 == 40'h22_2222_2222)
      $display("PimKL1BArgSlotTb: PASS");
    else
      $display("PimKL1BArgSlotTb: FAIL");
    $finish;
  endrule

endmodule

endpackage
