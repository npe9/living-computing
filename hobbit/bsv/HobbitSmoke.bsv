// HobbitSmoke.bsv -- Bluesim smoke test for the ATT92010 Hobbit model.
//
// The program is smoke.hex, in the repository's fixed image format
// (one 32-bit word per line, ascending from address 0; the parcel at an
// even address is bits 31:16).  run_smoke.sh regenerates the BSV word
// table from that file, so the bytes the spec runs and the bytes the
// model loads are one source.  Encodings and pages are cited per test
// below; the module comments record the modelled subset and its pages.
//
// Test evidence:
//   (a) CALL at 0x000 pushes 0x002 at CSP=0x100; sub_a RETURNs; the
//       program copies the saved word to 0x304 and marks 0x300.
//   (b) sub_b ENTERs 64 bytes, writes a local, RETURNs; then the main
//       code ENTERs 32, writes the accumulator at CSP+4, ADDs into it,
//       copies it out, and POPNs 32.
//   (c) sub_c ENTERs 144 bytes (flushing one quad to MSP=0x170),
//       RETURNs, then CATCH 176 refills four quad-words from memory,
//       including the sentinel at 0x180.
//   (d) CMPEQ sets PSW.F; a folded JMPTY is taken, the same folded
//       JMPTY is not taken after F is cleared, and a JMPTY after a
//       three-parcel monadic CATCH is unfurled and taken.
//   (e) a three-parcel opcode 0x08 (Table 1-18 "unimp") traps at 0x0BA.
//       The trap retires last, reporting the p. 1-39 sequence's store
//       *(CSP) = faulting PC as we=1, addr=CSP, data=0x000000BA.
//
// The core prints one HRI line per retired instruction; this harness
// prints its PASS/FAIL summary after all of them.  HRI is the Hobbit
// Retirement Interface, the Hobbit analogue of riscv-formal's RVFI;
// checking is retire-trace comparison, not a yosys formal proof.
//
// What each check catches:
//   e_trap_pc              an unimplemented opcode that does not trap, or
//                          a trap that records the wrong faulting PC
//   a_call_returned        CALL not transferring, or RETURN not returning
//   a_return_pc_value      CALL not storing the next PC at CSP (p. 3-9)
//   b_enter_return         ENTER/RETURN frame arithmetic (p. 3-19, 3-39)
//   b_accumulator_add      accumulator not at CSP+4, or ADD not writing dst
//   b_popn                 POPN not adding its operand to SP (p. 3-38)
//   c_enter_return         the large-frame ENTER path or its RETURN
//   c_catch_refills        CATCH not refilling (p. 3-10)
//   c_catch_msp            refill not advancing MSP to the target
//   c_catch_refilled_data  refill reading the wrong memory address
//   d_folded_jmpty_*       a folded JMPTY with the wrong condition sense
//   d_unfurled_jmpty_taken a JMPTY after a 3-parcel monadic wrongly folded
//   d_fold_count           p. 4-7 folding not detected or not counted
//   min_sp_reached         ENTER not lowering SP
//   stack_final_sp         RETURN/POPN not restoring SP
//   cpu_escape_rejected    the p. 3-14 CPU escape not rejected
//
// Discrimination, observed 2026-11-19: with isFoldable forced to False
// and catchTo made a no-op, exactly these four checks failed and nothing
// else did: c_catch_refills, c_catch_msp, c_catch_refilled_data,
// d_fold_count.  Both injections were reverted and the suite returned to
// 17 PASS.

package HobbitSmoke;

import Vector::*;
import HobbitTypes::*;
import HobbitDecode::*;
import HobbitCore::*;
import SmokeImage::*;

(* synthesize *)
module mkHobbitSmoke(Empty);

  HobbitMem mem <- mkHobbitMem;
  HobbitCore core <- mkHobbitCore(mem, 32'hFFFFFFFF);
  HobbitDecode chkdec <- mkHobbitDecode;

  Reg#(Bit#(16)) li <- mkReg(0);
  Reg#(Bool) loaded <- mkReg(False);
  Reg#(Bool) started <- mkReg(False);
  Reg#(Bool) finished <- mkReg(False);
  Reg#(Bool) reported <- mkReg(False);
  Reg#(Bit#(32)) cycles <- mkReg(0);

  // Shared golden pre-state: CONFIG = 0, PC = 0 (p. 1-35), PSW = 0x200
  // (bit 9 = 1 selects SP as CSP, Table 1-8 sheet 2, p. 1-15), therefore
  // SHAD = 0x100, SP = 0x100, MSP = 0x180.  This model always uses
  // CSP = SP and sets SHAD = SP.
  Word sp0  = 32'h00000100;
  Word msp0 = 32'h00000180;

  // ------------------------------------------------------------------
  // The program image is smoke.hex (the project's fixed image format);
  // run_smoke.sh turns it into generated/SmokeImage.bsv, so the bytes
  // the spec runs and the bytes this model loads are the same file.
  // ------------------------------------------------------------------

  // ------------------------------------------------------------------
  // Load the image, then reset the core at PC = 0 and run.
  // ------------------------------------------------------------------
  rule load (!loaded);
    if (zeroExtend(li) < imageLength()) begin
      mem.write(zeroExtend(li) << 2, imageWord(li));
      li <= li + 1;
    end else
      loaded <= True;
  endrule

  rule start (!started && loaded);
    core.start(sp0, msp0);
    started <= True;
  endrule

  rule count (started && !finished);
    cycles <= cycles + 1;
    if (core.halted() && !core.hriValid()) finished <= True;
    else if (cycles > 20000) finished <= True;
  endrule

  // ------------------------------------------------------------------
  // Checks.
  // ------------------------------------------------------------------
  function Action chk(Bool ok, String label, Word got, Word want) =
    action
      if (ok) $display("PASS %s = 0x%08x", label, got);
      else    $display("FAIL %s = 0x%08x, want 0x%08x", label, got, want);
    endaction;

  function Action chkb(Bool ok, String label) =
    action
      if (ok) $display("PASS %s", label);
      else    $display("FAIL %s", label);
    endaction;

  rule report (finished && !reported);
    reported <= True;

    if (!core.faulted())
      $display("FAIL timeout: program did not reach its trap in %0d cycles", cycles);

    chk(core.faulted() && (core.faultPc() == 32'h000000BA),
        "e_trap_pc", core.faultPc(), 32'h000000BA);

    chk(mem.read(32'h00000300) == 32'h000000A1,
        "a_call_returned", mem.read(32'h00000300), 32'h000000A1);
    chk(mem.read(32'h00000304) == 32'h00000002,
        "a_return_pc_value", mem.read(32'h00000304), 32'h00000002);
    chk(mem.read(32'h00000308) == 32'h000000B2,
        "b_enter_return", mem.read(32'h00000308), 32'h000000B2);
    chk(mem.read(32'h0000030C) == 32'h0000000D,
        "b_accumulator_add", mem.read(32'h0000030C), 32'h0000000D);
    chk(mem.read(32'h00000310) == 32'h000000B3,
        "b_popn", mem.read(32'h00000310), 32'h000000B3);
    chk(mem.read(32'h00000314) == 32'h000000C1,
        "c_enter_return", mem.read(32'h00000314), 32'h000000C1);
    chk(core.refills() == 32'd4, "c_catch_refills", core.refills(), 32'd4);
    chk(core.msp() == 32'h000001B0, "c_catch_msp", core.msp(), 32'h000001B0);
    chkb(core.cached(32'h00000180) &&
         (core.cacheWord(32'h00000180) == 32'hCAFEF00D),
         "c_catch_refilled_data");
    chk(mem.read(32'h00000318) == 32'h000000D1,
        "d_folded_jmpty_taken", mem.read(32'h00000318), 32'h000000D1);
    chk(mem.read(32'h0000031C) == 32'h000000D2,
        "d_folded_jmpty_not_taken", mem.read(32'h0000031C), 32'h000000D2);
    chk(mem.read(32'h00000320) == 32'h000000D4,
        "d_unfurled_jmpty_taken", mem.read(32'h00000320), 32'h000000D4);
    chk(core.folded() == 32'd2, "d_fold_count", core.folded(), 32'd2);
    chk(core.minSp() == 32'h00000070, "min_sp_reached", core.minSp(), 32'h00000070);
    chk(core.sp() == 32'h00000100, "stack_final_sp", core.sp(), 32'h00000100);

    let cpui = chkdec.decode(0, mkParcels(16'h2C00, 16'h0000, 16'h0000,
                                          16'h0000, 16'h0000, 16'h0000));
    chkb(cpui.tr == TR_CPU, "cpu_escape_rejected");

    $finish;
  endrule

endmodule

endpackage
