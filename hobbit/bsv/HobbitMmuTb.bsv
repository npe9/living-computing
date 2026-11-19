// HobbitMmuTb.bsv -- Bluesim checks for the ATT92010 MMU and the
// page-fault-to-exception path.
//
// Every expected value is derived from a printed table of the January
// 1993 Programmer's Reference Manual: the virtual-address fields
// (Figures 2-1/2-2, p. 2-2), the segment-table entry layouts
// (Tables 2-1/2-2, pp. 2-5/2-6), the page-table entry layout
// (Table 2-3, p. 2-7), the exception IDs (Table 1-26, p. 1-38) and the
// vector offsets (Table 1-14, p. 1-20).
//
// Table layout loaded by this testbench:
//
//   STB = 0
//   segment 0: paged, page table at 0x400
//   segment 1: nonpaged, base 1 (0x00400000), bound 0x10 (64 KB)
//   segment 2: invalid
//   segment 3: nonpaged, base 2 (0x00800000), bound 0 (4 KB),
//              kernel-only, read-only
//
//   page 0 -> frame 0      (identity: the event region)
//   page 1 -> frame 0x20   (VA 0x00001123 -> PA 0x00020123)
//   page 2 -> frame 0x30, kernel-only, read-only
//   page 3 -> invalid
//
// The last check raises the p. 1-38 exception sequence on an MMU read
// fault and verifies the printed vector (VB+4), the saved ID/PC/PSW in
// the interrupt frame (ISP-12, -8, -4), the new ISP/SHAD (ISP-16) and
// the FAULT register (p. 1-39).
//
// `chkf`/`chkwf` print one PASS/FAIL line and return the result; each
// rule sums its own results into the two counters exactly once, because
// two writes to one register in a clock are a scheduling conflict.

package HobbitMmuTb;

import Vector::*;
import HobbitTypes::*;
import HobbitMmu::*;
import HobbitEvents::*;

(* synthesize *)
module mkHobbitMmuTb(Empty);

  MmuTables tbl <- mkMmuTableMem;
  HobbitMmu mmu <- mkHobbitMmu(tbl);
  HobbitEventMem em <- mkHobbitEventMem;
  HobbitEvents ev <- mkHobbitEvents(em, mmu);

  Reg#(Bit#(32)) passes <- mkReg(0);
  Reg#(Bit#(32)) fails  <- mkReg(0);
  Reg#(Bit#(8))  st     <- mkReg(0);
  Reg#(Bit#(4))  li     <- mkReg(0);

  function Bit#(32) b2w(Bool b) = zeroExtend(pack(b));

  function ActionValue#(Bool) chkf(Bool ok, String label) =
    actionvalue
      if (ok) $display("PASS %s", label);
      else    $display("FAIL %s", label);
      return ok;
    endactionvalue;

  function ActionValue#(Bool) chkwf(Word got, String label, Word want) =
    actionvalue
      if (got == want) $display("PASS %s = 0x%08x", label, got);
      else $display("FAIL %s = 0x%08x, want 0x%08x", label, got, want);
      return (got == want);
    endactionvalue;

  // ---- table load ----------------------------------------------------
  function Word loadAddr(Bit#(4) i);
    case (i)
      4'd0: return 32'h000;   // STE 0
      4'd1: return 32'h004;   // STE 1
      4'd2: return 32'h008;   // STE 2
      4'd3: return 32'h00C;   // STE 3
      4'd4: return 32'h1000;  // PTE 0
      4'd5: return 32'h1004;  // PTE 1
      4'd6: return 32'h1008;  // PTE 2
      default: return 32'h100C; // PTE 3
    endcase
  endfunction

  function Word loadData(Bit#(4) i);
    case (i)
      // Table 2-1 p. 2-5: page table base 0x400, cache 1, segment 0,
      // valid 1.
      4'd0: return 32'h00001001;
      // Table 2-2 pp. 2-5/2-6: base 0x00400000, bound 0x10,
      // cache 1, segment 1, user 1, writable 1, valid 1.
      4'd1: return 32'h0041080F;
      // Invalid.
      4'd2: return 32'h00000000;
      // Table 2-2: base 0x00800000, bound 0, cache 0, segment 1,
      // user 0, writable 0, valid 1.
      4'd3: return 32'h00800009;
      // Table 2-3 p. 2-7: frame 0, cache 1, user 1, writable 1,
      // R = 0, M = 0, valid 1.
      4'd4: return 32'h00000807;
      // frame 0x20, same protection.
      4'd5: return 32'h00020807;
      // frame 0x30, cache 1, user 0, writable 0, valid 1.
      4'd6: return 32'h00030801;
      // frame 0x40, cache 1, user 1, writable 1, valid 1.
      default: return 32'h00040807;
    endcase
  endfunction

  function MmuReq req(Word va, Bool text, Bool wr, Bool user) =
    MmuReq { va: va, isText: text, isWrite: wr, user: user,
             enabled: True };

  MmuReq qPage1  = req(32'h00001123, False, False, False);
  MmuReq qPage1W = req(32'h00003123, False, True,  False);
  MmuReq qPage0  = req(32'h00000123, True,  False, False);
  MmuReq qNonp   = req(32'h00401234, False, False, False);
  MmuReq qBound  = req(32'h00420000, False, False, False);
  MmuReq qInvSeg = req(32'h00800000, False, False, False);
  MmuReq qRoWr   = req(32'h00002100, False, True,  False);
  MmuReq qUserRd = req(32'h00002100, False, False, True);
  MmuReq qKernRd = req(32'h00002100, False, False, False);

  // ---- load ----------------------------------------------------------
  rule load (st == 0);
    if (li < 8) begin
      tbl.write(loadAddr(li), loadData(li));
      li <= li + 1;
    end else begin
      ev.memWrite(32'h004, 32'h00001234);   // VB+4, exception vector
      st <= 1;
    end
  endrule

  // ---- step 1: STB, then a data walk ---------------------------------
  rule s1 (st == 1);
    mmu.setStb(32'h00000000);
    st <= 2;
  endrule

  rule s2 (st == 2);
    let r = mmu.translate(qPage1);
    let a <- chkf(r.fault == MMU_OK && r.valid, "paged_walk_ok");
    let b <- chkwf(r.pa, "paged_walk_pa", 32'h00020123);
    let c <- chkf(!r.hit, "paged_walk_miss");
    passes <= passes + b2w(a) + b2w(b) + b2w(c);
    fails  <= fails + b2w(!a) + b2w(!b) + b2w(!c);
    mmu.noteData(qPage1);
    st <= 3;
  endrule

  rule s3 (st == 3);
    let r = mmu.translate(qPage1);
    let a <- chkf(r.hit && (r.pa == 32'h00020123), "paged_tlb_hit");
    let b <- chkf(mmu.tlbValid(False, 0), "data_tlb_valid0");
    let c <- chkwf(zeroExtend(mmu.tlbEntry(False, 0).ppn),
                  "data_tlb_ppn", 32'h00020);
    // p. 2-7/2-8: the first reference set R in the memory copy.
    let d <- chkf((tbl.read(32'h1004) & 32'h8) == 32'h8, "pte_r_set");
    passes <= passes + b2w(a) + b2w(b) + b2w(c) + b2w(d);
    fails  <= fails + b2w(!a) + b2w(!b) + b2w(!c) + b2w(!d);
    mmu.noteData(qPage1);   // a hit
    mmu.noteText(qPage0);
    st <= 4;
  endrule

  rule s4 (st == 4);
    let r = mmu.translate(qPage0);
    let a <- chkf(r.hit && (r.pa == 32'h00000123), "text_tlb_hit_identity");
    let b <- chkf(mmu.tlbValid(True, 0), "text_tlb_valid0");
    let rn = mmu.translate(qNonp);
    let c <- chkwf(rn.pa, "nonpaged_pa", 32'h00401234);
    let d <- chkf(!rn.paged && !rn.hit, "nonpaged_walk");
    passes <= passes + b2w(a) + b2w(b) + b2w(c) + b2w(d);
    fails  <= fails + b2w(!a) + b2w(!b) + b2w(!c) + b2w(!d);
    mmu.noteText(qPage0);   // a hit
    mmu.noteData(qNonp);
    st <= 5;
  endrule

  rule s5 (st == 5);
    let r = mmu.translate(qNonp);
    let a <- chkf(r.hit && (r.pa == 32'h00401234), "npsr_hit");
    let b <- chkf(mmu.npsrEntry(False).valid, "npsr_valid");
    let c <- chkwf(zeroExtend(mmu.npsrEntry(False).base),
                  "npsr_base", 32'h1);
    let d <- chkwf(zeroExtend(mmu.npsrEntry(False).bound),
                  "npsr_bound", 32'h10);
    let rb = mmu.translate(qBound);
    let ri = mmu.translate(qInvSeg);
    let e <- chkf(rb.fault == MMU_READ_FAULT, "nonpaged_bound_fault");
    let f <- chkf(ri.fault == MMU_READ_FAULT, "invalid_segment_fault");
    passes <= passes + b2w(a) + b2w(b) + b2w(c) + b2w(d) +
                      b2w(e) + b2w(f);
    fails  <= fails + b2w(!a) + b2w(!b) + b2w(!c) + b2w(!d) +
                      b2w(!e) + b2w(!f);
    st <= 6;
  endrule

  rule s6 (st == 6);
    let rw = mmu.translate(qRoWr);
    let ru = mmu.translate(qUserRd);
    let rk = mmu.translate(qKernRd);
    let a <- chkf(rw.fault == MMU_WRITE_FAULT, "readonly_write_fault");
    let b <- chkf(ru.fault == MMU_READ_FAULT, "user_kernel_fault");
    let c <- chkf((rk.fault == MMU_OK) && (rk.pa == 32'h00030100),
                 "kernel_read_ok");
    passes <= passes + b2w(a) + b2w(b) + b2w(c);
    fails  <= fails + b2w(!a) + b2w(!b) + b2w(!c);
    mmu.noteData(qPage1W); // a write to page 1 for M/R writeback
    st <= 7;
  endrule

  rule s7 (st == 7);
    // p. 2-7: the write set M as well as R in the memory copy.
    let a <- chkf((tbl.read(32'h100C) & 32'h18) == 32'h18, "pte_rm_set");
    let b <- chkf(mmu.pteWrites() >= 1, "pte_writeback_count");
    passes <= passes + b2w(a) + b2w(b);
    fails  <= fails + b2w(!a) + b2w(!b);
    // p. 2-8: FLUSHPTE invalidates the effective address's entry.
    mmu.flushPte(32'h00001000);
    st <= 8;
  endrule

  rule s8 (st == 8);
    let a <- chkf(!mmu.tlbValid(False, 0), "flushpte_data");
    passes <= passes + b2w(a);
    fails  <= fails + b2w(!a);
    // Re-walk the page, then check a data reference hits.
    mmu.noteData(qPage1);
    st <= 9;
  endrule

  rule s9 (st == 9);
    let a <- chkf(mmu.tlbValid(False, 2), "refill_after_flushpte");
    passes <= passes + b2w(a);
    fails  <= fails + b2w(!a);
    // A write to STB flushes every TLB and NPSR entry (p. 2-8).
    mmu.setStb(32'h00000000);
    st <= 10;
  endrule

  rule s10 (st == 10);
    let a <- chkf(!mmu.tlbValid(False, 2) && !mmu.tlbValid(True, 0),
                 "stb_write_flushes");
    let b <- chkf(!mmu.npsrEntry(False).valid, "stb_write_flushes_npsr");
    let c <- chkwf(mmu.hits(), "mmu_hits", 2);
    let d <- chkwf(mmu.misses(), "mmu_misses", 5);
    let e <- chkwf(mmu.walks(), "mmu_walks", 5);
    passes <= passes + b2w(a) + b2w(b) + b2w(c) + b2w(d) + b2w(e);
    fails  <= fails + b2w(!a) + b2w(!b) + b2w(!c) + b2w(!d) + b2w(!e);
    // ---- page fault -> exception sequence --------------------------
    // V = 1, kernel, IPL = 0 (p. 1-15); VB = 0, ISP = 0x100.
    ev.setIsp(32'h00000100);
    ev.setShad(32'h00000100);
    let c0 = noEventCauses();
    c0.readFault = True;
    c0.pc = 32'h00000ABC;
    c0.va = 32'h0000DEAD;
    c0.psw = 32'h00010000;
    c0.vb = 32'h00000000;
    ev.raise(c0);
    st <= 11;
  endrule

  rule s11 (st == 11);
    if (ev.done()) begin
      let r = ev.result();
      let a <- chkf(r.taken && (r.cls == EV_READ_FAULT),
                   "fault_event_class");
      let b <- chkwf(zeroExtend(r.id), "fault_event_id", 32'h8);
      let c <- chkwf(r.vector, "fault_event_vector", 32'h00001234);
      let d <- chkwf(r.savedPc, "fault_saved_pc", 32'h00000ABC);
      let e <- chkwf(r.savedPsw, "fault_saved_psw", 32'h00010000);
      let f <- chkwf(r.newPsw, "fault_new_psw", 32'h00010000);
      let g <- chkwf(r.newIsp, "fault_new_isp", 32'h000000F0);
      let h <- chkwf(r.newShad, "fault_new_shad", 32'h000000F0);
      let i <- chkwf(r.faultReg, "fault_register", 32'h0000DEAD);
      let j <- chkwf(ev.memRead(32'h0F4), "frame_id_word", 32'h8);
      let k <- chkwf(ev.memRead(32'h0F8), "frame_pc_word", 32'h00000ABC);
      let l <- chkwf(ev.memRead(32'h0FC), "frame_psw_word", 32'h00010000);
      passes <= passes + b2w(a) + b2w(b) + b2w(c) + b2w(d) +
                        b2w(e) + b2w(f) + b2w(g) + b2w(h) +
                        b2w(i) + b2w(j) + b2w(k) + b2w(l);
      fails  <= fails + b2w(!a) + b2w(!b) + b2w(!c) + b2w(!d) +
                        b2w(!e) + b2w(!f) + b2w(!g) + b2w(!h) +
                        b2w(!i) + b2w(!j) + b2w(!k) + b2w(!l);
      ev.ack();
      st <= 12;
    end
  endrule

  rule s12 (st == 12);
    $display("MMU RESULT %0d PASS %0d FAIL", passes, fails);
    $finish;
  endrule

endmodule

endpackage
