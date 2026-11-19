// PimKL1BStructTb.bsv -- hand-assembled KL1-B structure-building program.
//
// The semantics are TR-246 p. 7 (images of pages 6-7 of
// docs/nonlocal/tr0246.pdf):
//   put_list Ai        : Ai = list HP
//   put_constant C, Ai : Ai = C
//   write_constant C   : (HP) = C, HP advanced by the word length
//
// Program (10 words, the c40 instructions carry a second word):
//   put_list r1              ; r1 = LIST HP (HP is 0 here)
//   put_constant r2, K1      ; r2 = K1
//   write_constant K2        ; heap[0] = K2, HP = 1
//   set_value 0, r4          ; r4 = int 0 (the model's set_value convention)
//   get_bound_value r4, r5   ; r5 = heap[0]
//   put_constant r3, K3      ; r3 = K3
//   proceed
// Pass: r1 == LIST 0, r2 == K1, r5 == K2, r3 == K3.
//
// Observed failure set (2026-11-19): injecting tagVar in place of
// tagList in the put_list rule made only this testbench print
//   r1=0100000000 ... PimKL1BStructTb: FAIL
// while PimKL1BTb, PimKL1BFailTb and PimKL1BConstFailTb still passed.
// Reverted; the suite then printed r1=0500000000 and PASS.
package PimKL1BStructTb;

import PimKL1B::*;

module mkPimKL1BStructTb(Empty);

  PimKL1B pu <- mkPimKL1B;
  Reg#(Bit#(4)) idx <- mkReg(0);
  Reg#(Bool) started <- mkReg(False);

  function Word prog(Bit#(4) i);
    case (i)
      0: return {8'h23, 32'h2e010000};  // put_list r1
      1: return {8'h23, 32'h30020000};  // put_constant r2, K1
      2: return {8'h02, 24'h0, 8'h11};  // K1
      3: return {8'h23, 32'h20000000};  // write_constant K2
      4: return {8'h02, 24'h0, 8'h22};  // K2
      5: return {8'h23, 32'h14000400};  // set_value 0, r4
      6: return {8'h23, 32'hbd040500};  // get_bound_value r4, r5
      7: return {8'h23, 32'h30030000};  // put_constant r3, K3
      8: return {8'h02, 24'h0, 8'h33};  // K3
      default: return {8'h23, 32'h60000000};  // proceed
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

  Reg#(Bit#(3)) checkIdx <- mkReg(0);
  Reg#(Word) r1v <- mkReg(0);
  Reg#(Word) r2v <- mkReg(0);
  Reg#(Word) r3v <- mkReg(0);
  Reg#(Word) r5v <- mkReg(0);

  rule readR1 if (pu.halted() && checkIdx == 0);
    r1v <= pu.readReg(1);
    checkIdx <= 1;
  endrule

  rule readR2 if (pu.halted() && checkIdx == 1);
    r2v <= pu.readReg(2);
    checkIdx <= 2;
  endrule

  rule readR3 if (pu.halted() && checkIdx == 2);
    r3v <= pu.readReg(3);
    checkIdx <= 3;
  endrule

  rule readR5 if (pu.halted() && checkIdx == 3);
    r5v <= pu.readReg(5);
    checkIdx <= 4;
  endrule

  rule check if (checkIdx == 4);
    $display("r1=%h r2=%h r3=%h r5=%h", r1v, r2v, r3v, r5v);
    if (r1v == {8'h05, 20'h0, 12'h0}
        && r2v == {8'h02, 24'h0, 8'h11}
        && r3v == {8'h02, 24'h0, 8'h33}
        && r5v == {8'h02, 24'h0, 8'h22})
      $display("PimKL1BStructTb: PASS");
    else
      $display("PimKL1BStructTb: FAIL");
    $finish;
  endrule

endmodule

endpackage
