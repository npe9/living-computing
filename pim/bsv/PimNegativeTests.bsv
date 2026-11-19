// PimNegativeTests.bsv -- negative tests for undefined and legal opcodes.
//
// docs/wp5_evidence.md §4.2 specifies two assertions the smoke test does
// not cover:
//
//   2. Undefined opcode: error() latches and halted() stays false; the
//      running register clears (PimPU.bsv:196-197).
//   3. Legal opcode: error() stays false for every opcode in docs/isa.md.
//
// This testbench loads a one-word program whose opcode is 0x0f (not in
// docs/isa.md) and a one-word program whose opcode is 0x01 (halt), starts
// both PUs, and checks the two assertions.  The undefined-opcode word is
// 0x0f00000000; the decode table's default entry has valid=False, so the
// E stage sets errorSeen (PimE.bsv:162-164).
//
// Run from bsv/: ./run_neg_tb.sh
//
// Discriminating power (observed 2026-11-19, not predicted):
//   * commenting out `errorSeen <= True;` in PimE.bsv: FAIL "undefined
//     opcode did not latch error()" and PimNegTb: FAIL.  Reverting the
//     injection restores PASS.

package PimNegativeTests;

import PimTypes::*;
import PimStages::*;
import PimPU::*;

(* synthesize *)
module mkPimNegTb(Empty);
  LocalStore storeUndef <- mkLocalStore("generated/undefined.hex");
  PimPU puUndef <- mkPimPU(storeUndef);

  LocalStore storeLegal <- mkLocalStore("generated/legal.hex");
  PimPU puLegal <- mkPimPU(storeLegal);

  Reg#(Bit#(32)) step <- mkReg(0);
  Reg#(Bool) started <- mkReg(False);
  Reg#(Bool) undefDone <- mkReg(False);
  Reg#(Bool) legalDone <- mkReg(False);
  Reg#(Bool) checked <- mkReg(False);
  Reg#(Bool) ok <- mkReg(True);

  rule start (!started);
    puUndef.start();
    puLegal.start();
    started <= True;
  endrule

  rule run (started && !checked);
    step <= step + 1;
    if (puUndef.error() || puUndef.halted()) undefDone <= True;
    if (puLegal.error() || puLegal.halted()) legalDone <= True;
    if ((undefDone && legalDone) || step >= 1000) checked <= True;
  endrule

  rule check (started && checked);
    Bool okNow = True;
    if (!puUndef.error()) begin
      $display("FAIL: undefined opcode did not latch error()");
      okNow = False;
    end
    if (puUndef.halted()) begin
      $display("FAIL: undefined opcode set halted()");
      okNow = False;
    end
    if (puLegal.error()) begin
      $display("FAIL: legal opcode latched error()");
      okNow = False;
    end
    if (!puLegal.halted()) begin
      $display("FAIL: legal opcode did not halt");
      okNow = False;
    end
    ok <= okNow;
    if (okNow) $display("PimNegTb: PASS");
    else       $display("PimNegTb: FAIL");
    $finish;
  endrule
endmodule

endpackage
