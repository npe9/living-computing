// HobbitEventTb.bsv -- Bluesim checks for ATT92010 event processing.
//
// Every expected value is a printed table or sequence of the January
// 1993 Programmer's Reference Manual:
//
//   * priority order, p. 1-40;
//   * interrupt levels, Table 1-25 p. 1-36, and acceptance when the
//     request level is less than PSW.IPL or equal to 0, p. 1-36;
//   * interrupt sequence, p. 1-37: *(ISP-8)=PC, *(ISP-4)=PSW,
//     ISP-=16, SHAD=ISP, PC=*(VB+16+4*level), PSW&=0xFFFF0000;
//   * exception sequence, p. 1-38: *(ISP-12)=ID, *(ISP-8)=PC,
//     *(ISP-4)=PSW, ISP-=16, SHAD=ISP, PC=*(VB+4);
//   * unimplemented instruction / trapped niladic, pp. 1-39/1-40:
//     *(CSP)=PC, PC=*(VB+12) or *(VB+8);
//   * reset, p. 1-35: SHAD=0, PSW=0, PC=0;
//   * exception identifiers, Table 1-26 p. 1-38;
//   * vector table offsets, Table 1-14 p. 1-20;
//   * PSW bit layout, Table 1-8 pp. 1-14/1-16 (V=16, IPL=14:12,
//     EL=10, CSP=9, TBB=8, TI=7, F=4).
//
// The MMU is a null port (all translations are physical, PSW.V = 0) for
// these sequence checks; the V=1 page-fault-to-exception path is checked
// in HobbitMmuTb.bsv against a real table.
//
// Each event takes three steps: raise, wait for done and check, then one
// idle cycle for the ack.  `chkf`, `chkExc` and `chkInt` return a Bool
// and print one PASS/FAIL line; each rule writes the two counters once.

package HobbitEventTb;

import Vector::*;
import HobbitTypes::*;
import HobbitMmu::*;
import HobbitEvents::*;

(* synthesize *)
module mkHobbitEventTb(Empty);

  MmuTables tbl <- mkMmuTableMem;
  HobbitMmu mmu <- mkHobbitMmu(tbl);
  HobbitEventMem em <- mkHobbitEventMem;
  HobbitEvents ev <- mkHobbitEvents(em, mmu);

  Reg#(Bit#(32)) passes <- mkReg(0);
  Reg#(Bit#(32)) fails  <- mkReg(0);
  Reg#(Bit#(16)) st     <- mkReg(0);
  Reg#(Bit#(5))  li     <- mkReg(0);

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

  function ActionValue#(Bool) chkExc(EventResult r, Bit#(4) id, Word vec,
                                     Word pc, Word psw, Word newIsp) =
    actionvalue
      let ok = (r.taken) && (r.id == id) && (r.vector == vec) &&
               (r.savedPc == pc) && (r.savedPsw == psw) &&
               (r.newIsp == newIsp) && (r.newShad == newIsp) &&
               (r.newPsw == (psw & 32'hFFFF0000));
      if (ok)
        $display("PASS exception id=0x%01x vector=0x%08x isp=0x%08x",
                 id, r.vector, r.newIsp);
      else
        $display("FAIL exception id want 0x%01x, got 0x%01x vector=0x%08x pc=0x%08x psw=0x%08x isp=0x%08x",
                 id, r.id, r.vector, r.savedPc, r.savedPsw, r.newIsp);
      return ok;
    endactionvalue;

  function ActionValue#(Bool) chkInt(EventResult r, Word vec, Word pc,
                                     Word psw, Word newIsp) =
    actionvalue
      let ok = (r.taken) && (r.cls == EV_INTERRUPT) &&
               (r.vector == vec) && (r.savedPc == pc) &&
               (r.savedPsw == psw) && (r.newIsp == newIsp) &&
               (r.newShad == newIsp) &&
               (r.newPsw == (psw & 32'hFFFF0000));
      if (ok)
        $display("PASS interrupt vector=0x%08x isp=0x%08x", r.vector, r.newIsp);
      else
        $display("FAIL interrupt got class=%0d vector=0x%08x isp=0x%08x",
                 pack(r.cls), r.vector, r.newIsp);
      return ok;
    endactionvalue;

  function EventCauses baseCause(Word pc, Word psw, Word sp, Word vb);
    let c = noEventCauses();
    c.pc = pc; c.psw = psw; c.sp = sp; c.vb = vb;
    return c;
  endfunction

  // ---- vector table load (Table 1-14, p. 1-20) ----------------------
  function Word vecAddrOf(Bit#(5) i);
    case (i)
      5'd0: return 32'h004;   // exception
      5'd1: return 32'h008;   // niladic
      5'd2: return 32'h00C;   // unimplemented
      5'd3: return 32'h010;   // NMI
      5'd4: return 32'h014;   // level 1
      5'd5: return 32'h018;   // level 2
      5'd6: return 32'h01C;   // level 3
      default: return 32'h020; // level 4
    endcase
  endfunction

  function Word vecDataOf(Bit#(5) i);
    case (i)
      5'd0: return 32'h00004000;
      5'd1: return 32'h00008000;
      5'd2: return 32'h0000C000;
      5'd3: return 32'h00001000;
      5'd4: return 32'h00001400;
      5'd5: return 32'h00001800;
      5'd6: return 32'h00003000;
      default: return 32'h00002000;
    endcase
  endfunction

  rule load (st == 0);
    if (li < 8) begin
      ev.memWrite(vecAddrOf(li), vecDataOf(li));
      li <= li + 1;
    end else if (li == 8) begin
      // Segment 0 paged, page table at 0x1000 (Table 2-1, p. 2-5).
      tbl.write(32'h0000, 32'h00001001);
      li <= li + 1;
    end else if (li == 9) begin
      // Page 0 -> frame 0, cache/user/writable/valid (Table 2-3, p. 2-7).
      tbl.write(32'h1000, 32'h00000807);
      li <= li + 1;
    end else
      st <= 1;
  endrule

  // ===================================================================
  // A. reset (p. 1-35): SHAD = 0, PSW = 0, PC = 0.
  // ===================================================================
  rule a0 (st == 1);
    ev.setIsp(32'h00000100);
    ev.setShad(32'h00000100);
    let c = baseCause(32'h00000123, 32'hFFFFFFFF, 32'h200, 32'h0);
    c.reset = True;
    ev.raise(c);
    st <= 2;
  endrule
  rule a1 (st == 2);
    if (ev.done()) begin
      let r = ev.result();
      let a <- chkf(r.cls == EV_RESET, "reset_class");
      let b <- chkwf(r.vector, "reset_pc", 0);
      let c <- chkwf(r.newPsw, "reset_psw", 0);
      let d <- chkwf(r.newShad, "reset_shad", 0);
      passes <= passes + b2w(a) + b2w(b) + b2w(c) + b2w(d);
      fails  <= fails + b2w(!a) + b2w(!b) + b2w(!c) + b2w(!d);
      ev.ack();
      st <= 3;
    end
  endrule
  rule a2 (st == 3); st <= 4; endrule

  // ===================================================================
  // B. interrupt IL=3, IPL=7, CSP=SP (p. 1-36/1-37).
  //    PSW = 0x0001F7F0: V, IPL 7, EG, EL=0, CSP=1, TBB, TI, F.
  // ===================================================================
  rule b0 (st == 4);
    ev.setIsp(32'h00000100);
    ev.setShad(32'h00000100);
    let c = baseCause(32'h00000200, 32'h0001F7F0, 32'h00000200, 32'h0);
    c.interrupt = True; c.il = 3;
    ev.raise(c);
    st <= 5;
  endrule
  rule b1 (st == 5);
    if (ev.done()) begin
      let r = ev.result();
      let a <- chkInt(r, 32'h00003000, 32'h00000200, 32'h0001F7F0,
                      32'h000000F0);
      let b <- chkwf(r.newPsw, "int_psw_low_cleared", 32'h00010000);
      let c <- chkwf(ev.memRead(32'h0F8), "int_frame_pc", 32'h00000200);
      let d <- chkwf(ev.memRead(32'h0FC), "int_frame_psw", 32'h0001F7F0);
      passes <= passes + b2w(a) + b2w(b) + b2w(c) + b2w(d);
      fails  <= fails + b2w(!a) + b2w(!b) + b2w(!c) + b2w(!d);
      ev.ack();
      st <= 6;
    end
  endrule
  rule b2 (st == 6); st <= 7; endrule

  // ===================================================================
  // C. interrupt IL=3 with IPL=2 is inhibited (p. 1-36).
  // ===================================================================
  rule c0 (st == 7);
    ev.setIsp(32'h00000100);
    let c = baseCause(32'h00000200, 32'h00002000, 32'h200, 32'h0);
    c.interrupt = True; c.il = 3;
    ev.raise(c);
    st <= 8;
  endrule
  rule c1 (st == 8);
    if (ev.done()) begin
      let r = ev.result();
      let a <- chkf(!r.taken, "int_inhibited");
      passes <= passes + b2w(a);
      fails  <= fails + b2w(!a);
      ev.ack();
      st <= 9;
    end
  endrule
  rule c2 (st == 9); st <= 10; endrule

  // ===================================================================
  // D. NMI: IL=0 is accepted at IPL=0 (p. 1-36).
  // ===================================================================
  rule d0 (st == 10);
    ev.setIsp(32'h00000100);
    ev.setShad(32'h00000100);
    let c = baseCause(32'h00000210, 32'h00000000, 32'h200, 32'h0);
    c.interrupt = True; c.il = 0;
    ev.raise(c);
    st <= 11;
  endrule
  rule d1 (st == 11);
    if (ev.done()) begin
      let r = ev.result();
      let a <- chkInt(r, 32'h00001000, 32'h00000210, 0, 32'h000000F0);
      passes <= passes + b2w(a);
      fails  <= fails + b2w(!a);
      ev.ack();
      st <= 12;
    end
  endrule
  rule d2 (st == 12); st <= 13; endrule

  // ===================================================================
  // E. IL=7 means no interrupt (Table 1-25, p. 1-36).
  // ===================================================================
  rule e0 (st == 13);
    let c = baseCause(32'h00000220, 32'h00007000, 32'h200, 32'h0);
    c.interrupt = True; c.il = 7;
    ev.raise(c);
    st <= 14;
  endrule
  rule e1 (st == 14);
    if (ev.done()) begin
      let r = ev.result();
      let a <- chkf(!r.taken, "int_il7_none");
      passes <= passes + b2w(a);
      fails  <= fails + b2w(!a);
      ev.ack();
      st <= 15;
    end
  endrule
  rule e2 (st == 15); st <= 16; endrule

  // ===================================================================
  // F. CSP=ISP (PSW bit 9 = 0): ISP = SHAD first (p. 1-37).
  //    ISP is 0x100 but SHAD is 0x300, so the frame is at 0x2F8.
  // ===================================================================
  rule f0 (st == 16);
    ev.setIsp(32'h00000100);
    ev.setShad(32'h00000300);
    let c = baseCause(32'h00000230, 32'h00007000, 32'h200, 32'h0);
    c.interrupt = True; c.il = 1;
    ev.raise(c);
    st <= 17;
  endrule
  rule f1 (st == 17);
    if (ev.done()) begin
      let r = ev.result();
      let a <- chkInt(r, 32'h00001400, 32'h00000230, 32'h00007000,
                      32'h000002F0);
      let b <- chkwf(ev.memRead(32'h2F8), "int_cspisp_frame_pc",
                     32'h00000230);
      passes <= passes + b2w(a) + b2w(b);
      fails  <= fails + b2w(!a) + b2w(!b);
      ev.ack();
      st <= 18;
    end
  endrule
  rule f2 (st == 18); st <= 19; endrule

  // ===================================================================
  // G..Q. exception identifiers (Table 1-26, p. 1-38), vector VB+4.
  // ===================================================================
  function EventCauses mkExc(Word pc, Word psw, Word sp, Word vb);
    return baseCause(pc, psw, sp, vb);
  endfunction

  // divide by zero, ID 0x1
  rule g0 (st == 19);
    ev.setIsp(32'h100); ev.setShad(32'h100);
    let c = mkExc(32'h777, 32'h0, 32'h200, 32'h0); c.divZero = True;
    ev.raise(c); st <= 20;
  endrule
  rule g1 (st == 20);
    if (ev.done()) begin
      let r = ev.result();
      let a <- chkExc(r, 4'h1, 32'h4000, 32'h777, 0, 32'hF0);
      let b <- chkwf(ev.memRead(32'h0F4), "exc_id_word", 32'h1);
      passes <= passes + b2w(a) + b2w(b); fails <= fails + b2w(!a) + b2w(!b);
      ev.ack(); st <= 21;
    end
  endrule
  rule g2 (st == 21); st <= 22; endrule

  // trace, ID 0x2
  rule h0 (st == 22);
    ev.setIsp(32'h100); ev.setShad(32'h100);
    let c = mkExc(32'h888, 32'h0, 32'h200, 32'h0); c.trace = True;
    ev.raise(c); st <= 23;
  endrule
  rule h1 (st == 23);
    if (ev.done()) begin
      let r = ev.result();
      let a <- chkExc(r, 4'h2, 32'h4000, 32'h888, 0, 32'hF0);
      passes <= passes + b2w(a); fails <= fails + b2w(!a);
      ev.ack(); st <= 24;
    end
  endrule
  rule h2 (st == 24); st <= 25; endrule

  // illegal, ID 0x3
  rule i0 (st == 25);
    ev.setIsp(32'h100); ev.setShad(32'h100);
    let c = mkExc(32'h999, 32'h0, 32'h200, 32'h0); c.illegal = True;
    ev.raise(c); st <= 26;
  endrule
  rule i1 (st == 26);
    if (ev.done()) begin
      let r = ev.result();
      let a <- chkExc(r, 4'h3, 32'h4000, 32'h999, 0, 32'hF0);
      passes <= passes + b2w(a); fails <= fails + b2w(!a);
      ev.ack(); st <= 27;
    end
  endrule
  rule i2 (st == 27); st <= 28; endrule

  // alignment, ID 0x4
  rule j0 (st == 28);
    ev.setIsp(32'h100); ev.setShad(32'h100);
    let c = mkExc(32'hAAA, 32'h0, 32'h200, 32'h0); c.align = True;
    ev.raise(c); st <= 29;
  endrule
  rule j1 (st == 29);
    if (ev.done()) begin
      let r = ev.result();
      let a <- chkExc(r, 4'h4, 32'h4000, 32'hAAA, 0, 32'hF0);
      passes <= passes + b2w(a); fails <= fails + b2w(!a);
      ev.ack(); st <= 30;
    end
  endrule
  rule j2 (st == 30); st <= 31; endrule

  // privilege, ID 0x5
  rule k0 (st == 31);
    ev.setIsp(32'h100); ev.setShad(32'h100);
    let c = mkExc(32'hBBB, 32'h0, 32'h200, 32'h0); c.privilege = True;
    ev.raise(c); st <= 32;
  endrule
  rule k1 (st == 32);
    if (ev.done()) begin
      let r = ev.result();
      let a <- chkExc(r, 4'h5, 32'h4000, 32'hBBB, 0, 32'hF0);
      passes <= passes + b2w(a); fails <= fails + b2w(!a);
      ev.ack(); st <= 33;
    end
  endrule
  rule k2 (st == 33); st <= 34; endrule

  // unimplemented register, ID 0x6
  rule l0 (st == 34);
    ev.setIsp(32'h100); ev.setShad(32'h100);
    let c = mkExc(32'hCCC, 32'h0, 32'h200, 32'h0); c.unimpReg = True;
    ev.raise(c); st <= 35;
  endrule
  rule l1 (st == 35);
    if (ev.done()) begin
      let r = ev.result();
      let a <- chkExc(r, 4'h6, 32'h4000, 32'hCCC, 0, 32'hF0);
      passes <= passes + b2w(a); fails <= fails + b2w(!a);
      ev.ack(); st <= 36;
    end
  endrule
  rule l2 (st == 36); st <= 37; endrule

  // fetch fault, ID 0x7
  rule m0 (st == 37);
    ev.setIsp(32'h100); ev.setShad(32'h100);
    let c = mkExc(32'hDDD, 32'h0, 32'h200, 32'h0); c.fetchFault = True;
    ev.raise(c); st <= 38;
  endrule
  rule m1 (st == 38);
    if (ev.done()) begin
      let r = ev.result();
      let a <- chkExc(r, 4'h7, 32'h4000, 32'hDDD, 0, 32'hF0);
      passes <= passes + b2w(a); fails <= fails + b2w(!a);
      ev.ack(); st <= 39;
    end
  endrule
  rule m2 (st == 39); st <= 40; endrule

  // data read fault, ID 0x8, FAULT = operand-aligned address (p. 1-39)
  rule n0 (st == 40);
    ev.setIsp(32'h100); ev.setShad(32'h100);
    let c = mkExc(32'h0F00, 32'h0, 32'h200, 32'h0);
    c.readFault = True; c.va = 32'h1234;
    ev.raise(c); st <= 41;
  endrule
  rule n1 (st == 41);
    if (ev.done()) begin
      let r = ev.result();
      let a <- chkExc(r, 4'h8, 32'h4000, 32'h0F00, 0, 32'hF0);
      let b <- chkwf(r.faultReg, "read_fault_register", 32'h1234);
      passes <= passes + b2w(a) + b2w(b); fails <= fails + b2w(!a) + b2w(!b);
      ev.ack(); st <= 42;
    end
  endrule
  rule n2 (st == 42); st <= 43; endrule

  // data write fault, ID 0x9, FAULT saved
  rule o0 (st == 43);
    ev.setIsp(32'h100); ev.setShad(32'h100);
    let c = mkExc(32'h0F10, 32'h0, 32'h200, 32'h0);
    c.writeFault = True; c.va = 32'h5678;
    ev.raise(c); st <= 44;
  endrule
  rule o1 (st == 44);
    if (ev.done()) begin
      let r = ev.result();
      let a <- chkExc(r, 4'h9, 32'h4000, 32'h0F10, 0, 32'hF0);
      let b <- chkwf(r.faultReg, "write_fault_register", 32'h5678);
      passes <= passes + b2w(a) + b2w(b); fails <= fails + b2w(!a) + b2w(!b);
      ev.ack(); st <= 45;
    end
  endrule
  rule o2 (st == 45); st <= 46; endrule

  // I/O bus fault, ID 0xA
  rule p0 (st == 46);
    ev.setIsp(32'h100); ev.setShad(32'h100);
    let c = mkExc(32'h0F20, 32'h0, 32'h200, 32'h0); c.busError = True;
    ev.raise(c); st <= 47;
  endrule
  rule p1 (st == 47);
    if (ev.done()) begin
      let r = ev.result();
      let a <- chkExc(r, 4'hA, 32'h4000, 32'h0F20, 0, 32'hF0);
      passes <= passes + b2w(a); fails <= fails + b2w(!a);
      ev.ack(); st <= 48;
    end
  endrule
  rule p2 (st == 48); st <= 49; endrule

  // MMU table walk bus fault, ID 0xB
  rule q0 (st == 49);
    ev.setIsp(32'h100); ev.setShad(32'h100);
    let c = mkExc(32'h0F30, 32'h0, 32'h200, 32'h0); c.walkFault = True;
    ev.raise(c); st <= 50;
  endrule
  rule q1 (st == 50);
    if (ev.done()) begin
      let r = ev.result();
      let a <- chkExc(r, 4'hB, 32'h4000, 32'h0F30, 0, 32'hF0);
      passes <= passes + b2w(a); fails <= fails + b2w(!a);
      ev.ack(); st <= 51;
    end
  endrule
  rule q2 (st == 51); st <= 52; endrule

  // ===================================================================
  // R. unimplemented instruction (p. 1-39): *(CSP)=PC, PC=*(VB+12).
  //    PSW bit 9 = 1 (CSP = SP), so the save is at SP.
  // ===================================================================
  rule r0 (st == 52);
    ev.setIsp(32'h100); ev.setShad(32'h100);
    let c = mkExc(32'hABC, 32'h00000200, 32'h200, 32'h0);
    c.unimp = True;
    ev.raise(c); st <= 53;
  endrule
  rule r1 (st == 53);
    if (ev.done()) begin
      let r = ev.result();
      let a <- chkwf(r.vector, "unimp_vector", 32'h0000C000);
      let b <- chkwf(ev.memRead(32'h200), "unimp_csp_save", 32'hABC);
      let c <- chkwf(r.newPsw, "unimp_psw_unchanged", 32'h00000200);
      let d <- chkwf(r.newIsp, "unimp_isp_unchanged", 32'h100);
      let e <- chkwf(r.cspStoreAddr, "unimp_store_addr", 32'h200);
      let f <- chkwf(r.cspStoreData, "unimp_store_data", 32'hABC);
      passes <= passes + b2w(a) + b2w(b) + b2w(c) + b2w(d) + b2w(e) + b2w(f);
      fails  <= fails + b2w(!a) + b2w(!b) + b2w(!c) + b2w(!d) + b2w(!e) + b2w(!f);
      ev.ack(); st <= 54;
    end
  endrule
  rule r2 (st == 54); st <= 55; endrule

  // ===================================================================
  // S. trapped niladic (p. 1-40): same save, PC=*(VB+8).
  // ===================================================================
  rule s0 (st == 55);
    ev.setIsp(32'h100); ev.setShad(32'h100);
    let c = mkExc(32'hABE, 32'h00000200, 32'h200, 32'h0);
    c.unimp = True; c.niladic = True;
    ev.raise(c); st <= 56;
  endrule
  rule s1 (st == 56);
    if (ev.done()) begin
      let r = ev.result();
      let a <- chkwf(r.vector, "niladic_vector", 32'h00008000);
      let b <- chkwf(ev.memRead(32'h200), "niladic_csp_save", 32'hABE);
      passes <= passes + b2w(a) + b2w(b); fails <= fails + b2w(!a) + b2w(!b);
      ev.ack(); st <= 57;
    end
  endrule
  rule s2 (st == 57); st <= 58; endrule

  // ===================================================================
  // T. priority (p. 1-40): trace (3) beats fetch fault (4), illegal
  //    (5), unimp (6), align (8), privilege (10) and divide by zero
  //    (11) when all are raised together.
  // ===================================================================
  rule t0 (st == 58);
    ev.setIsp(32'h100); ev.setShad(32'h100);
    let c = mkExc(32'h0, 32'h0, 32'h200, 32'h0);
    c.trace = True; c.fetchFault = True; c.illegal = True;
    c.unimp = True; c.align = True; c.privilege = True;
    c.divZero = True;
    ev.raise(c); st <= 59;
  endrule
  rule t1 (st == 59);
    if (ev.done()) begin
      let r = ev.result();
      let a <- chkf(r.cls == EV_TRACE, "priority_trace_over_lower");
      let b <- chkwf(zeroExtend(r.id), "priority_trace_id", 32'h2);
      passes <= passes + b2w(a) + b2w(b); fails <= fails + b2w(!a) + b2w(!b);
      ev.ack(); st <= 60;
    end
  endrule
  rule t2 (st == 60); st <= 61; endrule

  // ===================================================================
  // U. priority: interrupt (2) beats trace (3).
  // ===================================================================
  rule u0 (st == 61);
    ev.setIsp(32'h100); ev.setShad(32'h100);
    let c = mkExc(32'h0, 32'h00007000, 32'h200, 32'h0);
    c.trace = True; c.fetchFault = True; c.interrupt = True; c.il = 3;
    ev.raise(c); st <= 62;
  endrule
  rule u1 (st == 62);
    if (ev.done()) begin
      let r = ev.result();
      let a <- chkf(r.cls == EV_INTERRUPT, "priority_interrupt_over_trace");
      let b <- chkwf(r.vector, "priority_interrupt_vector", 32'h3000);
      passes <= passes + b2w(a) + b2w(b); fails <= fails + b2w(!a) + b2w(!b);
      ev.ack(); st <= 63;
    end
  endrule
  rule u2 (st == 63); st <= 64; endrule

  // ===================================================================
  // V. priority: reset (1) beats everything.
  // ===================================================================
  rule v0 (st == 64);
    ev.setIsp(32'h100); ev.setShad(32'h100);
    let c = mkExc(32'h0, 32'h00007000, 32'h200, 32'h0);
    c.reset = True; c.interrupt = True; c.il = 3; c.trace = True;
    c.divZero = True;
    ev.raise(c); st <= 65;
  endrule
  rule v1 (st == 65);
    if (ev.done()) begin
      let r = ev.result();
      let a <- chkf(r.cls == EV_RESET, "priority_reset_first");
      let b <- chkwf(r.vector, "priority_reset_vector", 0);
      passes <= passes + b2w(a) + b2w(b); fails <= fails + b2w(!a) + b2w(!b);
      ev.ack(); st <= 66;
    end
  endrule
  rule v2 (st == 66); st <= 67; endrule

  rule done (st == 67);
    $display("EVENT RESULT %0d PASS %0d FAIL", passes, fails);
    $finish;
  endrule

endmodule

endpackage
