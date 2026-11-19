// HobbitCoreMmuTb.bsv -- the integrated path: PSW.V = 1, a fetch
// translation fault, and the printed p. 1-38 exception sequence.
//
// The program is a three-parcel absolute JMP (Table 1-23, p. 1-26) to
// 0x2000.  Segment 0 is paged (Table 2-1, p. 2-5) with page 0 mapped
// identity and page 2 invalid (Table 2-3, p. 2-7), so the fetch of the
// target has no mapping.  p. 1-38 says a fault on the target of a JMP
// saves the target PC, not the JMP's PC; the event vector is VB+4
// (Table 1-14, p. 1-20) and the frame is *(ISP-12)=ID, *(ISP-8)=PC,
// *(ISP-4)=PSW with ISP -= 16 and SHAD = ISP.
//
// This is the integration check for the requirement "with PSW.V = 1 the
// core's accesses go through the MMU; a fault raises the event sequence
// rather than a silent trap".  The standalone sequence checks are in
// HobbitEventTb.bsv and the mapping/TLB checks in HobbitMmuTb.bsv.

package HobbitCoreMmuTb;

import Vector::*;
import HobbitTypes::*;
import HobbitMmu::*;
import HobbitCore::*;

(* synthesize *)
module mkHobbitCoreMmuTb(Empty);

  HobbitMem mem <- mkHobbitMem;
  MmuTables tbl <- mkMmuTableMem;
  MemCycles mcyc = defaultMemCycles();
  HobbitCore core <- mkHobbitCoreMmu(mem, 32'hFFFFFFFF, mcyc, tbl);

  Reg#(Bit#(32)) passes <- mkReg(0);
  Reg#(Bit#(32)) fails  <- mkReg(0);
  Reg#(Bit#(16)) st     <- mkReg(0);
  Reg#(Bit#(32)) cycles <- mkReg(0);

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

  // ---- image and tables ---------------------------------------------
  // 0x000: 80F3 0000 = three-parcel monadic JMP, smode 0xF (absolute)
  //        (Table 1-19 p. 1-24; Table 1-23 p. 1-26).
  // 0x004: 2000 0000 = the 32-bit target, low half 0x2000; p3 = 0.
  rule load0 (st == 0);
    mem.write(32'h000, 32'h80F30000);
    st <= 1;
  endrule

  rule load1 (st == 1);
    mem.write(32'h004, 32'h20000000);
    st <= 2;
  endrule

  rule load2 (st == 2);
    // Segment 0: paged, page table at 0x1000, valid (Table 2-1).
    tbl.write(32'h0000, 32'h00001001);
    st <= 3;
  endrule

  rule load3 (st == 3);
    // Page 0 -> frame 0, cache/user/writable/valid (Table 2-3).
    // Page 2 is left unwritten: zero means invalid (bit 0 = 0).
    tbl.write(32'h1000, 32'h00000807);
    st <= 4;
  endrule

  rule setup (st == 4);
    core.setVb(32'h00000000);
    core.setIsp(32'h00000100);
    core.setShad(32'h00000100);
    // VB+4 = exception vector (Table 1-14, p. 1-20).
    core.eventMemWrite(32'h004, 32'h00000100);
    core.prefetchImage();
    st <= 5;
  endrule

  rule waitReady (st == 5);
    if (core.prefetchReady()) begin
      // V = 1 (bit 16), kernel, IPL = 0 (Table 1-8, pp. 1-14/1-15).
      core.startPsw(32'h00000100, 32'h00000180, 32'h00010000);
      st <= 6;
    end else if (cycles > 5000) begin
      $display("FAIL prefetch timeout");
      st <= 8;
    end
  endrule

  rule count (st == 6);
    cycles <= cycles + 1;
    if (core.eventTaken()) st <= 7;
    else if (cycles > 20000) begin
      $display("FAIL event timeout");
      st <= 8;
    end
  endrule

  rule report (st == 7);
    let a <- chkf(core.eventTaken(), "core_event_taken");
    let b <- chkwf(core.eventPc(), "core_event_pc", 32'h00000100);
    let c <- chkwf(zeroExtend(core.eventId()), "core_event_id", 32'h7);
    let d <- chkwf(core.savedPc(), "core_saved_pc_target", 32'h00002000);
    let e <- chkwf(core.savedPsw(), "core_saved_psw", 32'h00010000);
    let f <- chkwf(core.psw(), "core_new_psw", 32'h00010000);
    let g <- chkwf(core.isp(), "core_new_isp", 32'h000000F0);
    let h <- chkwf(core.shad(), "core_new_shad", 32'h000000F0);
    let i <- chkwf(core.eventMemRead(32'h0F4), "core_frame_id", 32'h7);
    let j <- chkwf(core.eventMemRead(32'h0F8), "core_frame_pc",
                   32'h00002000);
    let k <- chkwf(core.eventMemRead(32'h0FC), "core_frame_psw",
                   32'h00010000);
    let l <- chkf(core.mmuFaults() >= 1, "core_mmu_fault_counted");
    passes <= passes + b2w(a) + b2w(b) + b2w(c) + b2w(d) +
                      b2w(e) + b2w(f) + b2w(g) + b2w(h) +
                      b2w(i) + b2w(j) + b2w(k) + b2w(l);
    fails  <= fails + b2w(!a) + b2w(!b) + b2w(!c) + b2w(!d) +
                      b2w(!e) + b2w(!f) + b2w(!g) + b2w(!h) +
                      b2w(!i) + b2w(!j) + b2w(!k) + b2w(!l);
    st <= 8;
  endrule

  rule done (st == 8);
    $display("CORE MMU RESULT %0d PASS %0d FAIL", passes, fails);
    $finish;
  endrule

endmodule

endpackage
