// HobbitCoreMmuStoreTb.bsv -- a byte store into a page with no valid
// entry is a write fault, exception 9, at the store's own PC.
//
// The core makes a byte or half-word store as read, merge, write: EU_S1
// reads the word the destination lives in.  The part writes the byte
// lanes and makes no read, and the reference translates the store as a
// write (p. 2-3; Table 1-26, p. 1-38: 0x9 data write fault), so a fault
// on that read is the store's write fault, not a read fault (0x8).
// Found at record 308,543,068 of the s9term join on the core: /boot's
// `MOV *R24:UB,*R8:B` into a page not yet mapped, after which the
// kernel's `_exception` stored the ID 8 where the reference stored 9
// (docs/conformance_1to1.md §1d row 14).  The record of an operand fault
// is the privileged core's (mkHobbitCoreSystem), so this is checked on
// the event the MMU core raises, as HobbitCoreMmuTb checks its fetch
// fault.
//
// Program (asm/hobbit_asm.py):
//   0x000  86FD 5000 0008   MOV $0x5000, R8   -- page 5, invalid
//   0x006  86F8 0005 0008   MOV $5, *R8:B     -- the byte store
//   0x00c  2C02 2C02        NOP; NOP
// Segment 0 paged, its table at 0x1000 (Table 2-1, p. 2-5); page 0 ->
// frame 0, cache/user/writable/valid; every other page invalid (Table
// 2-3, p. 2-7).  The frame is *(ISP-12)=ID, *(ISP-8)=PC, *(ISP-4)=PSW,
// ISP -= 16 (p. 1-38).
//
// Observed 2026-11-24 with the core before the fix (HobbitCore.bsv as of
// e808abbf): core_event_id and core_frame_id fail (0x8 for 0x9), nothing
// else.

package HobbitCoreMmuStoreTb;

import Vector::*;
import HobbitTypes::*;
import HobbitMmu::*;
import HobbitCore::*;

(* synthesize *)
module mkHobbitCoreMmuStoreTb(Empty);

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

  function Word imageWord(Bit#(16) i);
    case (i)
      0: return 32'h86FD5000;
      1: return 32'h000886F8;
      2: return 32'h00050008;
      default: return 32'h2C022C02;
    endcase
  endfunction

  rule load (st < 4);
    mem.write(zeroExtend(st) << 2, imageWord(st));
    st <= st + 1;
  endrule

  rule loadSeg (st == 4);
    tbl.write(32'h0000, 32'h00001001);
    st <= 5;
  endrule

  rule loadPage (st == 5);
    tbl.write(32'h1000, 32'h00000807);
    st <= 6;
  endrule

  rule setup (st == 6);
    core.setVb(32'h00000000);
    core.setIsp(32'h00000100);
    core.setShad(32'h00000100);
    core.eventMemWrite(32'h004, 32'h00000100);
    core.prefetchImage();
    st <= 7;
  endrule

  rule waitReady (st == 7);
    cycles <= cycles + 1;
    if (core.prefetchReady()) begin
      core.startPsw(32'h00000100, 32'h00000180, 32'h00010200);
      st <= 8;
    end else if (cycles > 5000) begin
      $display("FAIL prefetch timeout");
      st <= 10;
    end
  endrule

  rule count (st == 8);
    cycles <= cycles + 1;
    if (core.eventTaken()) st <= 9;
    else if (cycles > 25000) begin
      $display("FAIL event timeout");
      st <= 10;
    end
  endrule

  rule report (st == 9);
    let a <- chkf(core.eventTaken(), "core_event_taken");
    let b <- chkwf(zeroExtend(core.eventId()), "core_event_id", 32'h9);
    let c <- chkwf(core.savedPc(), "core_saved_pc_store", 32'h00000006);
    let d <- chkwf(core.eventMemRead(32'h0F4), "core_frame_id", 32'h9);
    let e <- chkwf(core.eventMemRead(32'h0F8), "core_frame_pc",
                   32'h00000006);
    let f <- chkwf(core.eventPc(), "core_event_pc", 32'h00000100);
    passes <= passes + b2w(a) + b2w(b) + b2w(c) + b2w(d) + b2w(e) + b2w(f);
    fails  <= fails + b2w(!a) + b2w(!b) + b2w(!c) + b2w(!d) + b2w(!e) +
                      b2w(!f);
    st <= 10;
  endrule

  rule done (st == 10);
    $display("CORE MMU STORE RESULT %0d PASS %0d FAIL", passes, fails);
    $finish;
  endrule

endmodule

endpackage
