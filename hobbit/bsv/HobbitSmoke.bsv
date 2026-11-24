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
// The core prints one HRI line per retired instruction (41 in this
// program); this harness prints its PASS/FAIL summary after all of them.
// HRI is the Hobbit Retirement Interface, the Hobbit analogue of
// riscv-formal's RVFI; checking is retire-trace comparison, not a yosys
// formal proof.
//
// Cycle checks (Chapter 4, printed pp. 4-3..4-5):
//   cyc_mov_one_cycle          MOV at 0x0002 reports 1  (Table 4-32)
//   cyc_add_one_cycle          ADD at 0x001C reports 1  (Table 4-32)
//   cyc_popn_two_cycles        POPN at 0x0024 reports 2 (Table 4-32)
//   cyc_return_two_cycles      RETURN at 0x00D2 reports 2 (Table 4-32)
//   cyc_folded_branch_zero      folded JMPTY at 0x003C reports 0 (p. 4-3)
//   cyc_unfolded_jmpty_one      unfurled JMPTY at 0x00AA reports 1 (Table 4-35)
//   cyc_enter_r32_one           ENTER R-32 at 0x0016 flushes 0 blocks: 1
//   cyc_enter_1block_5          ENTER R-144 at 0x00F0 flushes 1 block:
//                               1 + Q.E = 1 + 4.1 = 5 (Table 4-36)
//   cyc_catch_one               CATCH at 0x0034 reports 1 (Table 4-36)
//   cyc_trap_7_plus_a           unimplemented opcode at 0x00BA: 7 + A = 8
//   cyc_add_imm_one_cycle       three-parcel ADD $100,R0 is ADD: 1
//                               (Table 4-32 prices the mnemonic, p. 4-3)
//   ori_opcode_01_two_cycles    opcode 0x01 is ORI (p. 3-37; ADDI is 0x03,
//                               p. 3-6), interlocked: 2 (Table 4-32)
//   cyc_enter_8block_33         ENTER $0xC0 over SP 0x100/MSP 0x180,
//                               E = 8 blocks: 1 + 4.8 = 33 (Table 4-36)
//   cyc_enter_flush_32_clocks   a real eight-block write-back takes
//                               32 clocks in the stack-cache box (Q = 4)
//
// The last three are timing-table and box checks: smoke.hex has no ADDI
// and no eight-block ENTER (golden 004 executes the latter end to end).
// They exercise the same instrCycles()/enterFlushBlocks() definitions
// the execution unit uses, and the box check measures the real
// write-back rather than a counter.
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
import HobbitStackCache::*;
import HobbitBus::*;
import SmokeImage::*;

(* synthesize *)
module mkHobbitSmoke(Empty);

  HobbitBusMem mem <- mkHobbitBusMem;
  HobbitMem phys <- mkHobbitMemBus(mem);
  MemCycles mcyc = defaultMemCycles();
  HobbitCore core <- mkHobbitCore(phys, 32'hFFFFFFFF, mcyc);
  HobbitDecode chkdec <- mkHobbitDecode;

  // A second, independent stack-cache box and memory, used only after the
  // program has retired.  It measures the write-back time of an
  // eight-block ENTER directly (the same Q = 4 engine the core uses).
  HobbitBusMem boxMem <- mkHobbitBusMem;
  HobbitMem boxPhys <- mkHobbitMemBus(boxMem);
  HobbitStackCache box <- mkHobbitStackCache(boxPhys, mcyc);

  Reg#(Bit#(16)) li <- mkReg(0);
  Reg#(Bool) loaded <- mkReg(False);
  Reg#(Bool) started <- mkReg(False);
  Reg#(Bool) finished <- mkReg(False);
  Reg#(Bool) reported <- mkReg(False);
  Reg#(Bit#(32)) cycles <- mkReg(0);

  // Cycle captures, one per checked retirement record.  The monitor rule
  // reads the record the core is retiring this clock, before the core's
  // own retire rule drains it.
  Reg#(Bit#(32)) cyc_mov <- mkReg(0);
  Reg#(Bit#(32)) cyc_add <- mkReg(0);
  Reg#(Bit#(32)) cyc_popn <- mkReg(0);
  Reg#(Bit#(32)) cyc_ret <- mkReg(0);
  Reg#(Bit#(32)) cyc_fold <- mkReg(0);
  Reg#(Bit#(32)) cyc_jmpty <- mkReg(0);
  Reg#(Bit#(32)) cyc_enter_small <- mkReg(0);
  Reg#(Bit#(32)) cyc_enter_1 <- mkReg(0);
  Reg#(Bit#(32)) cyc_catch <- mkReg(0);
  Reg#(Bit#(32)) cyc_trap <- mkReg(0);

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
      phys.write(zeroExtend(li) << 2, imageWord(li));
      li <= li + 1;
    end else
      loaded <= True;
  endrule

  // After the image is in memory, the prefetch buffer warms from the
  // synchronous read port one word per clock (the p. 4-1 "instruction
  // fetches access in the instruction cache" assumption).  The measured
  // run starts only when it is ready.
  Reg#(Bit#(2)) boot <- mkReg(0);

  rule askPrefetch (loaded && (boot == 0));
    core.prefetchImage();
    $display("ASK t=%0d", cycles);
    boot <= 1;
  endrule

  Reg#(Bit#(16)) bootCycles <- mkReg(0);
  rule bootWait (boot == 1);
    bootCycles <= bootCycles + 1;
    if (core.prefetchReady()) begin
      core.start(sp0, msp0);
      $display("START t=%0d", bootCycles);
      started <= True;
      boot <= 2;
    end else if (bootCycles > 2000) begin
      $display("BOOT TIMEOUT ready=%d", pack(core.prefetchReady()));
      $finish;
    end
  endrule

  rule count (started && !finished);
    cycles <= cycles + 1;
    if (cycles < 16 || cycles[9:0] == 0)
      $display("SMOKE t=%0d pc=%08x fault=%d q=%d hv=%d dbg=%016x",
               cycles, core.pc(), pack(core.faulted()),
               pack(core.quiescent()), pack(core.hriValid()),
               core.dbgState());
    if (core.halted() && core.quiescent()) finished <= True;
    else if (cycles > 20000) finished <= True;
  endrule

  // Capture the cycle count of each checked instruction as it retires.
  rule watch (started && core.hriValid());
    let r = core.hri();
    case (r.pc)
      32'h00000002: cyc_mov         <= r.cyc;
      32'h00000016: cyc_enter_small <= r.cyc;
      32'h0000001c: cyc_add         <= r.cyc;
      32'h00000024: cyc_popn        <= r.cyc;
      32'h00000034: cyc_catch       <= r.cyc;
      32'h0000003c: cyc_fold        <= r.cyc;
      32'h000000aa: cyc_jmpty       <= r.cyc;
      32'h000000d2: cyc_ret         <= r.cyc;
      32'h000000f0: cyc_enter_1     <= r.cyc;
      32'h000000ba: cyc_trap        <= r.cyc;
      default: noAction;
    endcase
  endrule

  // ------------------------------------------------------------------
  // Eight-block ENTER write-back measurement (after the program stops).
  // STATE 0: reset the box at the golden pre-state.
  // STATE 1: issue ENTER $0xC0, the golden-004 instruction.
  // STATE 2: count the clocks the box is busy (pp. 3-19/3-20 loop).
  // ------------------------------------------------------------------
  Reg#(Bit#(2)) boxState <- mkReg(0);
  Reg#(Bit#(16)) boxClocks <- mkReg(0);

  // The program memory has one testbench read port (HobbitMem::peek);
  // loading the nine result words through one dynamic-address call site
  // keeps the RegFile inside its port budget.
  Reg#(Bit#(5)) pkIdx <- mkReg(0);
  Reg#(Vector#(16, Word)) pkVals <- mkReg(replicate(0));

  rule peekLoad (finished && (boxState == 3) && (pkIdx < 16));
    pkVals <= update(pkVals, pkIdx[3:0],
                     mem.peek(32'h00000300 + (zeroExtend(pkIdx) << 2)));
    pkIdx <= pkIdx + 1;
  endrule

  rule boxReset (finished && (boxState == 0));
    box.reset(sp0, msp0);
    boxState <= 1;
  endrule

  // ENTER $0xc0 empties an eight-block cache: SP 0x100 -> 0xc0 and
  // MSP 0x180 -> 0xc0 (pp. 3-19/3-20).  The box's own rule starts the
  // flush from this command and advances it one word per clock, so the
  // harness only counts the clocks it stays busy.
  rule boxEnter (boxState == 1);
    box.commit(ScCmd { op: BX_ENTER, we: False, waddr: 0, wdata: 0,
                       spBefore: sp0, mspBefore: msp0,
                       spAfter: 32'h000000C0, mspAfter: 32'h000000C0,
                       target: 32'h000000C0, stackMode: False });
    boxState <= 2;
  endrule

  rule boxCount (boxState == 2);
    if (box.busy())
      boxClocks <= boxClocks + 1;
    else
      boxState <= 3;
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

  rule report (finished && (boxState == 3) && (pkIdx == 16) && !reported);
    reported <= True;

    if (!core.faulted())
      $display("FAIL timeout: program did not reach its trap in %0d cycles", cycles);

    chk(core.faulted() && (core.faultPc() == 32'h000000BA),
        "e_trap_pc", core.faultPc(), 32'h000000BA);

    chk(pkVals[0] == 32'h000000A1,
        "a_call_returned", pkVals[0], 32'h000000A1);
    chk(pkVals[1] == 32'h00000002,
        "a_return_pc_value", pkVals[1], 32'h00000002);
    chk(pkVals[2] == 32'h000000B2,
        "b_enter_return", pkVals[2], 32'h000000B2);
    chk(pkVals[3] == 32'h0000000D,
        "b_accumulator_add", pkVals[3], 32'h0000000D);
    chk(pkVals[4] == 32'h000000B3,
        "b_popn", pkVals[4], 32'h000000B3);
    chk(pkVals[5] == 32'h000000C1,
        "c_enter_return", pkVals[5], 32'h000000C1);
    chk(core.refills() == 32'd4, "c_catch_refills", core.refills(), 32'd4);
    chk(core.msp() == 32'h000001B0, "c_catch_msp", core.msp(), 32'h000001B0);
    chkb(core.cached(32'h00000180) &&
         (core.cacheWord(32'h00000180) == 32'hCAFEF00D),
         "c_catch_refilled_data");
    chk(pkVals[6] == 32'h000000D1,
        "d_folded_jmpty_taken", pkVals[6], 32'h000000D1);
    chk(pkVals[7] == 32'h000000D2,
        "d_folded_jmpty_not_taken", pkVals[7], 32'h000000D2);
    chk(pkVals[8] == 32'h000000D4,
        "d_unfurled_jmpty_taken", pkVals[8], 32'h000000D4);
    chk(core.folded() == 32'd2, "d_fold_count", core.folded(), 32'd2);
    chk(core.minSp() == 32'h00000070, "min_sp_reached", core.minSp(), 32'h00000070);
    chk(core.sp() == 32'h00000100, "stack_final_sp", core.sp(), 32'h00000100);

    let cpui = chkdec.decode(0, mkParcels(16'h2C00, 16'h0000, 16'h0000,
                                          16'h0000, 16'h0000, 16'h0000));
    chkb(cpui.tr == TR_CPU, "cpu_escape_rejected");

    // --- cycle checks, Chapter 4 -----------------------------------
    chk(cyc_mov == 1, "cyc_mov_one_cycle", cyc_mov, 1);
    chk(cyc_add == 1, "cyc_add_one_cycle", cyc_add, 1);
    chk(cyc_popn == 2, "cyc_popn_two_cycles", cyc_popn, 2);
    chk(cyc_ret == 2, "cyc_return_two_cycles", cyc_ret, 2);
    chk(cyc_fold == 0, "cyc_folded_branch_zero", cyc_fold, 0);
    chk(cyc_jmpty == 1, "cyc_unfolded_jmpty_one", cyc_jmpty, 1);
    chk(cyc_enter_small == 1, "cyc_enter_r32_one", cyc_enter_small, 1);
    chk(cyc_enter_1 == 5, "cyc_enter_1block_5", cyc_enter_1, 5);
    chk(cyc_catch == 1, "cyc_catch_one", cyc_catch, 1);
    chk(cyc_trap == 8, "cyc_trap_7_plus_a", cyc_trap, 8);

    // The three-parcel ADD $100,R0 from golden 002 (record insn
    // a3fd0064) is ADD, not ADDI.  Table 4-32 prices the mnemonic at 1
    // for every parcel count and operand mode (p. 4-3).  The interlocked
    // forms are opcodes 0x01 ORI (p. 3-37), 0x02 ANDI (p. 3-8) and 0x03
    // ADDI (p. 3-6), each 2 in Table 4-32.  Until 2026-11-23 this check
    // read 0x01 as ADDI and required it to trap; the s9term boot needs
    // all three (docs/conformance_1to1.md 1d, golden 022).
    let addImmD = chkdec.decode(0, mkParcels(16'hA3FD, 16'h0064, 16'h0000,
                                             16'h0000, 16'h0000, 16'h0000));
    Word addImmC = instrCycles(mkDecInstEntry(addImmD), sp0, msp0, mcyc,
                               False, 0);
    chk(addImmC == 1, "cyc_add_imm_one_cycle", addImmC, 1);

    let oriD = chkdec.decode(0, mkParcels(16'h81FD, 16'h0001, 16'h0008,
                                          16'h0000, 16'h0000, 16'h0000));
    Word oriC = instrCycles(mkDecInstEntry(oriD), sp0, msp0, mcyc, False, 0);
    chkb((oriD.tr == TR_NONE) && (oriD.op == OP_ORI) && (oriC == 2),
         "ori_opcode_01_two_cycles");

    // An ENTER $imm over SP 0x100/MSP 0x180 empties an eight-block
    // cache: 1 + Q.E with E = 8 and Q = 4 is 33 (Table 4-36).
    let enterD = chkdec.decode(0, mkParcels(16'h80F9, 16'h0000, 16'h00C0,
                                            16'h0000, 16'h0000, 16'h0000));
    Word enterC = instrCycles(mkDecInstEntry(enterD), sp0, msp0, mcyc,
                              False, 0);
    chk(enterC == 33, "cyc_enter_8block_33", enterC, 33);

    // The box itself: eight quads at Q = 4 is 32 clocks of write-back.
    Word boxCycW = zeroExtend(boxClocks);
    chk(boxCycW == 32, "cyc_enter_flush_32_clocks", boxCycW, 32);

    $finish;
  endrule

endmodule

endpackage
