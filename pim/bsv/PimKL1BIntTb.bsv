// PimKL1BIntTb.bsv -- KL1-B integer-building pair.
//
// The mnemonics and operand packing are the PIMOS assembler's
// (docs/kl1_encoding.md): put_integer is r_c16 (register in bits 23-16,
// 16-bit constant in bits 15-0); write_integer is c24 (24-bit constant
// in bits 23-0).  The semantics -- Ai = INT constant, (HP) = INT
// constant with HP advanced -- follow the put_*/write_* family of
// TR-246 p. 7 and are labelled inferred from the mnemonic and operand
// type, not documented prose.
//
// Program (5 words):
//   put_integer r1, 0x1234   ; r1 = INT 0x1234
//   write_integer 0xABCDEF   ; heap[0] = INT 0xABCDEF, HP = 1
//   set_value 0, r4          ; r4 = int 0 (the model's set_value convention)
//   get_bound_value r4, r5   ; r5 = heap[0]
//   proceed
//
// Observed failure set (2026-11-19): injecting tagVar in place of tagInt
// in the put_integer rule made only this testbench print
//   r1=0100001234 r5=0200abcdef / PimKL1BIntTb: FAIL
// while the four other KL1-B testbenches still passed.  Reverted; the
// suite then printed r1=0200001234 and PASS.
package PimKL1BIntTb;

import PimKL1B::*;

(* synthesize *)
module mkPimKL1BIntTb(Empty);

  PimKL1B pu <- mkPimKL1B;
  Reg#(Bit#(4)) idx <- mkReg(0);
  Reg#(Bool) started <- mkReg(False);

  function Word prog(Bit#(4) i);
    case (i)
      0: return {8'h23, 32'h31011234};  // put_integer r1, 0x1234
      1: return {8'h23, 32'h21ABCDEF};  // write_integer 0xABCDEF
      2: return {8'h23, 32'h14000400};  // set_value 0, r4
      3: return {8'h23, 32'hbd040500};  // get_bound_value r4, r5
      default: return {8'h23, 32'h60000000};  // proceed
    endcase
  endfunction

  rule load if (idx < 5);
    pu.load(zeroExtend(idx), prog(idx));
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
    Word r1 = pu.readReg(1);
    Word r5 = pu.readReg(5);
    $display("r1=%h r5=%h", r1, r5);
    if (r1 == {8'h02, 16'h0, 16'h1234} && r5 == {8'h02, 8'h0, 24'hABCDEF})
      $display("PimKL1BIntTb: PASS");
    else
      $display("PimKL1BIntTb: FAIL");
    $finish;
  endrule
endmodule

endpackage
