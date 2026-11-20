// PimKL1BSwitchConstTb.bsv -- switch_on_constant (0x2c): jump to the
// matching key's label, or to the else label when no key matches.
//
// switch_on_constant R, [K=Label, ...], Else is r_c16_c16_16s_sw
// (klb_opr.kl1 470-482; entries built by make_label, 504-535):
//   word 0     tag 0x23, op 0x2c | R<<16 | Length
//   2 words per entry: the constant K, then a data word (tag 0x00)
//                      with the else label in bits 31-16 and K's
//                      label in bits 15-0.
// Semantics from the compiler: equal -> K's label, no match -> Else
// (optimize.kl1 30-42 rewrites a one-entry switch to wait_atom /
// wait_constant; index.kl1 507-509 emits it after the type switch).
// Model conventions, not sourced: the entries are scanned in order,
// one per step(); labels are absolute model addresses (the assembler
// emits relative ones); an unbound value halts (it would suspend).
//
// Program:
//   0x00  switch_on_constant r0, 2 entries
//   0x01    K = ATOM 0x0a
//   0x02    else 0x0b, label 0x05
//   0x03    K = ATOM 0x0b
//   0x04    else 0x0b, label 0x08
//   0x05  put_integer r1, 1 ; 0x06 halt      first key's target
//   0x08  put_integer r1, 2 ; 0x09 halt      second key's target
//   0x0b  put_integer r1, 3 ; 0x0c halt      else target
//
// Four runs, one model instance each, r1 preset to INT 0:
//   r0 = ATOM 0x0b (second key) -> r1 == INT 2
//   r0 = ATOM 0x0c (no key)     -> r1 == INT 3
//   r0 = ATOM 0x0a (first key)  -> r1 == INT 1
//   r0 = unbound (tag 0x01)     -> halted with pc still 0
//
// Observed failure sets (2026-11-19, each injection run across all 26
// KL1-B benches, the other 25 passing every time; printed as
// second-key / no-key / first-key r1, then the unbound line):
//   key compare forced False: 0200000003 / 0200000003 / 0200000003,
//     halted=1 pc=0000000000, FAIL.
//   else label taken from bits 15-0: 0200000002 / 0200000002 /
//     0200000001, halted=1 pc=0000000000, FAIL.
//   scan index never advances: "FAIL (watchdog)" -- the second-key run
//     never halts.
//   unbound check removed: 0200000002 / 0200000003 / 0200000001,
//     halted=1 pc=000000000d, FAIL (the unbound value took the else
//     label).
// All reverted; green.
package PimKL1BSwitchConstTb;

import StmtFSM::*;
import PimKL1B::*;

(* synthesize *)
module mkPimKL1BSwitchConstTb(Empty);
  // One model instance per run: second key, no key, first key, unbound.
  PimKL1B puB <- mkPimKL1B;
  PimKL1B puN <- mkPimKL1B;
  PimKL1B puA <- mkPimKL1B;
  PimKL1B puU <- mkPimKL1B;

  Reg#(Word) r1B <- mkReg(0);
  Reg#(Word) r1N <- mkReg(0);
  Reg#(Word) r1A <- mkReg(0);
  Reg#(Bool) hU  <- mkReg(False);
  Reg#(Word) pcU <- mkReg(0);
  Reg#(Bit#(16)) watchdog <- mkReg(0);

  function Stmt loadProg(PimKL1B pu, Word r0);
    return seq
      pu.load(12'h000, 40'h23_2c_00_00_02);   // switch_on_constant r0, 2 entries
      pu.load(12'h001, 40'h06_00_00_00_0a);   //   K = ATOM 0x0a
      pu.load(12'h002, 40'h00_00_0b_00_05);   //   else 0x0b, label 0x05
      pu.load(12'h003, 40'h06_00_00_00_0b);   //   K = ATOM 0x0b
      pu.load(12'h004, 40'h00_00_0b_00_08);   //   else 0x0b, label 0x08
      pu.load(12'h005, 40'h23_31_01_00_01);   // put_integer r1, 1
      pu.load(12'h006, 40'h23_71_00_00_00);   // halt
      pu.load(12'h007, 40'h23_71_00_00_00);   // halt
      pu.load(12'h008, 40'h23_31_01_00_02);   // put_integer r1, 2
      pu.load(12'h009, 40'h23_71_00_00_00);   // halt
      pu.load(12'h00a, 40'h23_71_00_00_00);   // halt
      pu.load(12'h00b, 40'h23_31_01_00_03);   // put_integer r1, 3
      pu.load(12'h00c, 40'h23_71_00_00_00);   // halt
      pu.setReg(0, r0);
      pu.setReg(1, 40'h02_00_00_00_00);       // r1 = INT 0: no marker ran
      pu.start(0);
    endseq;
  endfunction

  function Stmt runToHalt(PimKL1B pu);
    return seq
      while (!pu.halted()) pu.step();
    endseq;
  endfunction

  Stmt test = seq
    loadProg(puB, 40'h06_00_00_00_0b);  runToHalt(puB);  r1B <= puB.readReg(1);
    loadProg(puN, 40'h06_00_00_00_0c);  runToHalt(puN);  r1N <= puN.readReg(1);
    loadProg(puA, 40'h06_00_00_00_0a);  runToHalt(puA);  r1A <= puA.readReg(1);
    loadProg(puU, 40'h01_00_00_00_00);  runToHalt(puU);
    hU <= puU.halted();
    pcU <= puU.pc();

    $display("PimKL1BSwitchConstTb: second-key r1=%h no-key r1=%h first-key r1=%h",
             r1B, r1N, r1A);
    $display("PimKL1BSwitchConstTb: unbound halted=%d pc=%h", hU, pcU);
    if (r1B == 40'h02_00_00_00_02 && r1N == 40'h02_00_00_00_03
        && r1A == 40'h02_00_00_00_01 && hU && pcU == 0)
      $display("PimKL1BSwitchConstTb: PASS");
    else
      $display("PimKL1BSwitchConstTb: FAIL");
    $finish;
  endseq;

  mkAutoFSM(test);

  // A model that never halts (a scan that never ends) must fail, not hang.
  rule tick;
    watchdog <= watchdog + 1;
    if (watchdog == 2000) begin
      $display("PimKL1BSwitchConstTb: FAIL (watchdog)");
      $finish;
    end
  endrule
endmodule

endpackage
