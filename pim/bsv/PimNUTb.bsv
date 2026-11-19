// PimNUTb.bsv -- Bluesim testbench for the PIM/m network unit.
//
// Two PEs (input/output ports 0 and 1) put one packet each.  The
// testbench checks:
//   * the documented one-byte-per-four-cycles move rate;
//   * back-pressure: in_.ready drops while the input buffer is full;
//   * the read-buffer tail interrupt (bit 8 of the packet byte);
//   * two ports move independently in the same cycle.
//
// The NU model is per-port (the crossbar route table is not modelled;
// see plan.md WP4.1), so a byte put on port i appears on output port i.
//
// Run from bsv/: ./run_nu_tb.sh
//
// Discriminating power (observed 2026-11-19, not predicted):
//   * rate[i] <= 3 changed to rate[i] <= 0:
//       FAIL: move gap = 2, want 4
//       PimNUTb: FAIL
//   * if (b[8] == 1) tailPulse.send(); removed:
//       FAIL: tail interrupt not seen for 9'h101
//       PimNUTb: FAIL

package PimNUTb;

import Vector::*;
import StmtFSM::*;
import PimNU::*;

(* synthesize *)
module mkPimNUTb(Empty);
  PimNU nu <- mkPimNU(replicate(0));

  Reg#(Bit#(32)) cycles <- mkReg(0);
  Reg#(Bit#(4)) phase <- mkReg(0);
  Reg#(Bool) ok <- mkReg(True);
  Reg#(Bool) tailSeen <- mkReg(False);
  Reg#(Bit#(32)) moves0 <- mkReg(0);
  Reg#(Bit#(32)) moves1 <- mkReg(0);
  Reg#(Bit#(32)) lastMove0 <- mkReg(0);
  Reg#(Bit#(32)) lastMove1 <- mkReg(0);
  Reg#(Bit#(32)) gap0 <- mkReg(0);
  Reg#(Bool) prevValid0 <- mkReg(False);
  Reg#(Bool) prevValid1 <- mkReg(False);

  // Phase 2 pump state.
  Reg#(Bool) pumping <- mkReg(False);
  Reg#(Bit#(9)) nextByte <- mkReg(0);
  Reg#(Bit#(9)) expectByte <- mkReg(0);
  Reg#(Bit#(32)) pumpMoves <- mkReg(0);

  rule count;
    cycles <= cycles + 1;
  endrule

  // Fail fast instead of hanging if the FSM waits on a condition that
  // never comes true.
  rule watchdog (cycles > 200);
    $display("FAIL: timeout at cycle %0d, phase %0d, pumping %0d",
             cycles, phase, pumping);
    $finish;
  endrule

  rule watchTail (nu.packetTail());
    tailSeen <= True;
  endrule

  // Detect output-valid transitions (the move rule's effect).
  rule watchMoves;
    let v0 = !nu.out[0].ready();
    let v1 = !nu.out[1].ready();
    if (v0 && !prevValid0) begin
      moves0 <= moves0 + 1;
      gap0 <= cycles - lastMove0;
      lastMove0 <= cycles;
    end
    if (v1 && !prevValid1) begin
      moves1 <= moves1 + 1;
      lastMove1 <= cycles;
    end
    prevValid0 <= v0;
    prevValid1 <= v1;
  endrule

  // Phase 2: keep port 0's pipeline full and check every byte and gap.
  // Two rules, not one: a single rule calling both put and deq would
  // carry both implicit conditions in its guard (input empty AND output
  // full), which is never true after the output is drained.
  rule pumpIn (pumping);
    nu.in_[0].put(nextByte);
    nextByte <= nextByte + 1;
  endrule

  rule pumpOut (pumping);
    let got = nu.out[0].get();
    if (got != tagged Valid expectByte) begin
      $display("FAIL: pump byte = ", fshow(got), ", want ", fshow(expectByte));
      ok <= False;
    end
    expectByte <= expectByte + 1;
    pumpMoves <= pumpMoves + 1;
    nu.out[0].deq();
  endrule

  Stmt test = seq
    // ---- Phase 1: two PEs, simultaneous move. ----
    await(nu.in_[0].ready() && nu.in_[1].ready());
    action
      nu.in_[0].put(9'h101);
      nu.in_[1].put(9'h002);
      phase <= 1;
    endaction
    await(!nu.out[0].ready() && !nu.out[1].ready());
    if (nu.out[0].get() != tagged Valid 9'h101) action
      $display("FAIL: port 0 byte = ", fshow(nu.out[0].get()));
      ok <= False;
    endaction
    if (nu.out[1].get() != tagged Valid 9'h002) action
      $display("FAIL: port 1 byte = ", fshow(nu.out[1].get()));
      ok <= False;
    endaction
    if (!tailSeen) action
      $display("FAIL: tail interrupt not seen for 9'h101");
      ok <= False;
    endaction
    if (lastMove0 != lastMove1) action
      $display("FAIL: ports moved in different cycles: %0d vs %0d",
               lastMove0, lastMove1);
      ok <= False;
    endaction
    // Back-pressure: fill the input buffers while the output buffers
    // are still full.  The move cannot fire, so in_.ready must drop.
    action
      nu.in_[0].put(9'h003);
      nu.in_[1].put(9'h004);
      phase <= 2;
    endaction
    if (nu.in_[0].ready() || nu.in_[1].ready()) action
      $display("FAIL: in_.ready true while the move is blocked");
      ok <= False;
    endaction
    action
      nu.out[0].deq();
      nu.out[1].deq();
      phase <= 3;
    endaction
    await(!nu.out[0].ready() && !nu.out[1].ready());
    if (nu.out[0].get() != tagged Valid 9'h003) action
      $display("FAIL: port 0 second byte = ", fshow(nu.out[0].get()));
      ok <= False;
    endaction
    if (nu.out[1].get() != tagged Valid 9'h004) action
      $display("FAIL: port 1 second byte = ", fshow(nu.out[1].get()));
      ok <= False;
    endaction
    action
      nu.out[0].deq();
      nu.out[1].deq();
      phase <= 4;
    endaction
    // ---- Phase 2: rate. ----
    action
      tailSeen <= False;
      pumping <= True;
      nextByte <= 9'h010;
      expectByte <= 9'h010;
      phase <= 5;
    endaction
    // Wait for four pumped bytes, then check the gap.
    await(pumpMoves == 4);
    action
      pumping <= False;
      phase <= 6;
    endaction
    if (gap0 != 4) action
      $display("FAIL: move gap = %0d, want 4", gap0);
      ok <= False;
    endaction
    if (tailSeen) action
      $display("FAIL: tail interrupt seen for a non-tail byte");
      ok <= False;
    endaction
    // Report.
    action
      if (ok) $display("PimNUTb: PASS");
      else    $display("PimNUTb: FAIL");
    endaction
    $finish;
  endseq;

  mkAutoFSM(test);
endmodule

endpackage
