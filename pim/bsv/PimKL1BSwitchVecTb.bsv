// PimKL1BSwitchVecTb.bsv -- switch_on_non_vector (0x2b): a non-vector
// jumps to the label; a vector halts loudly.
//
// switch_on_non_vector R, Ari, Label is r_r_c16_i, two words
// (klb_opr.kl1 334-348): word 0 = op 0x2b | R<<16 | Ari<<8, word 1 = the
// label.  Ari is an output register (regass.kl1 361-362) that receives
// the vector's arity for the switch_on_constant that follows it
// (index.kl1 900-902).  The model has no vector layout, so it executes
// only the non-vector half: jump to the label.  On a vector it halts
// rather than fall through with Ari unwritten.  tagVector = 0x07 is the
// model's own convention; no modelled instruction builds a vector.
//
// Program:
//   0x00  tag=0x23 op=0x2b R=r0 Ari=r3   first word
//   0x01  label=0x04                     second word
//   0x02  put_integer r1, 7              fall-through marker
//   0x03  halt
//   0x04  put_integer r2, 9              jump target
//   0x05  halt
//
// Two runs, one model instance each:
//   not-a-vector (r0 = INT 5): two steps; r2 == INT 9, r1 != INT 7.
//   vector       (r0 = VEC 5): one step; halted() is True.
//
// Observed failure sets (2026-11-19, each injection run across all 25
// KL1-B benches, the other 24 passing both times):
//   c40Jump forced False (never jump): this bench prints
//     not-a-vector r1=0200000007 r2=aaaaaaaaaa / vector halted=1 / FAIL.
//   0x2b arm made noAction (vector falls through): this bench prints
//     not-a-vector r1=aaaaaaaaaa r2=0200000009 / vector halted=0 / FAIL.
// Both reverted; green.

package PimKL1BSwitchVecTb;

import StmtFSM::*;
import PimKL1B::*;

(* synthesize *)
module mkPimKL1BSwitchVecTb(Empty);
  PimKL1B pu1 <- mkPimKL1B;
  PimKL1B pu2 <- mkPimKL1B;

  Reg#(Word) r1a <- mkReg(0);
  Reg#(Word) r2a <- mkReg(0);
  Reg#(Bool) haltb <- mkReg(False);

  function Word mkWord(Bit#(8) tag, Bit#(32) v);
    return {tag, v};
  endfunction

  Stmt test = seq
    // --- not-a-vector run: r0 = INT 5 -> jump taken ---
    pu1.load(12'h000, mkWord(8'h23, {8'h2b, 8'h00, 8'h03, 8'h00}));
    pu1.load(12'h001, mkWord(8'h00, 32'h00000004));
    pu1.load(12'h002, mkWord(8'h23, {8'h31, 8'h01, 16'h0007}));
    pu1.load(12'h003, mkWord(8'h23, {8'h71, 24'h000000}));
    pu1.load(12'h004, mkWord(8'h23, {8'h31, 8'h02, 16'h0009}));
    pu1.load(12'h005, mkWord(8'h23, {8'h71, 24'h000000}));
    pu1.setReg(0, mkWord(8'h02, 32'h00000005));
    pu1.start(zeroExtend(12'h000));
    pu1.step();
    pu1.step();
    r1a <= pu1.readReg(1);
    r2a <= pu1.readReg(2);

    // --- vector run: r0 = VEC 5 -> loud halt ---
    pu2.load(12'h000, mkWord(8'h23, {8'h2b, 8'h00, 8'h03, 8'h00}));
    pu2.load(12'h001, mkWord(8'h00, 32'h00000004));
    pu2.load(12'h002, mkWord(8'h23, {8'h31, 8'h01, 16'h0007}));
    pu2.load(12'h003, mkWord(8'h23, {8'h71, 24'h000000}));
    pu2.load(12'h004, mkWord(8'h23, {8'h31, 8'h02, 16'h0009}));
    pu2.load(12'h005, mkWord(8'h23, {8'h71, 24'h000000}));
    pu2.setReg(0, mkWord(8'h07, 32'h00000005));
    pu2.start(zeroExtend(12'h000));
    pu2.step();
    haltb <= pu2.halted();

    $display("PimKL1BSwitchVecTb: not-a-vector r1=%h r2=%h", r1a, r2a);
    $display("PimKL1BSwitchVecTb: vector      halted=%d", haltb);
    if (r2a == 40'h02_00_00_00_09 && r1a != 40'h02_00_00_00_07 && haltb)
      $display("PimKL1BSwitchVecTb: PASS");
    else
      $display("PimKL1BSwitchVecTb: FAIL");
    $finish;
  endseq;

  mkAutoFSM(test);
endmodule

endpackage
