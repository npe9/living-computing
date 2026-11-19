// PimLinkTb.bsv -- Two-PE connected-link testbench.
//
// Model-derived: the sources document the NU's per-port FIFO and the
// one-byte-per-four-cycles rate, but the link layer itself is not
// described beyond the adjacent-PE channel pair (M92 p.427).  This
// testbench bridges two mkPimNU instances back-to-back and checks
// that packet bytes flow end-to-end with the documented rate.
//
// Discriminating power (observed 2026-11-19, not predicted):
//   * `rate[i] <= 0` in mkPimNU: FAIL move gap = 2, want 4.

package PimLinkTb;

import Vector::*;
import StmtFSM::*;
import PimNU::*;
import PimLink::*;

(* synthesize *)
module mkPimLinkTb(Empty);
  PimNU nu0 <- mkPimNU(replicate(0));
  PimNU nu1 <- mkPimNU(replicate(0));

  // Port 0: nu0 -> nu1   Port 1: nu1 -> nu0
  // Separate ports avoid testbench/link deq conflicts.
  Empty link0 <- mkPimLink(nu0.out[0], nu1.in_[0]);
  Empty link1 <- mkPimLink(nu1.out[1], nu0.in_[1]);

  Reg#(Bit#(32)) cycles <- mkReg(0);
  Reg#(Bit#(4))  phase <- mkReg(0);
  Reg#(Bool)     ok    <- mkReg(True);

  // Rate measurement for port 0 (nu0 -> nu1)
  Reg#(Bit#(32)) lastMove <- mkReg(0);
  Reg#(Bit#(32)) gap     <- mkReg(0);
  Reg#(Bit#(32)) moves   <- mkReg(0);
  Reg#(Bool)     prevValid <- mkReg(False);
  Reg#(Bool)     tailSeen <- mkReg(False);

  rule count;
    cycles <= cycles + 1;
  endrule

  rule tailWatch (nu0.packetTail());
    tailSeen <= True;
  endrule

  // Detect output-valid transitions on nu1.out[0].
  rule watchArrival;
    let v = !nu1.out[0].ready();
    if (v && !prevValid) begin
      moves <= moves + 1;
      gap <= cycles - lastMove;
      lastMove <= cycles;
    end
    prevValid <= v;
  endrule

  // Fail fast instead of hanging.
  rule watchdog (cycles > 500);
    $display("FAIL: timeout at cycle %0d, phase %0d", cycles, phase);
    ok <= False;
    $finish;
  endrule

  // Phase 2 pump state.
  Reg#(Bool) pumping <- mkReg(False);
  Reg#(Bit#(9)) nextByte <- mkReg(0);
  Reg#(Bit#(9)) expectByte <- mkReg(0);
  Reg#(Bit#(32)) pumpMoves <- mkReg(0);

  rule pumpIn (pumping);
    nu0.in_[0].put(nextByte);
    nextByte <= nextByte + 1;
  endrule

  rule pumpOut (pumping);
    let got = nu1.out[0].get();
    if (got != tagged Valid expectByte) begin
      $display("FAIL: pump byte = ", fshow(got), ", want ", fshow(expectByte));
      ok <= False;
    end
    expectByte <= expectByte + 1;
    pumpMoves <= pumpMoves + 1;
    nu1.out[0].deq();
  endrule

  Stmt test = seq
    // ---- Phase 1: send one byte nu0 -> nu1, assert arrival and tail. ----
    action
      tailSeen <= False;
      phase <= 1;
    endaction
    await(nu0.in_[0].ready());
    action
      nu0.in_[0].put(9'h101);
      phase <= 2;
    endaction
    await(!nu1.out[0].ready());
    if (nu1.out[0].get() != tagged Valid 9'h101) action
      $display("FAIL: nu1 byte = ", fshow(nu1.out[0].get()));
      ok <= False;
    endaction
    if (!tailSeen) action
      $display("FAIL: tailPulse not seen for 9'h101");
      ok <= False;
    endaction
    action
      nu1.out[0].deq();
      phase <= 3;
    endaction

    // ---- Phase 2: send back nu1 -> nu0 on port 1, assert arrival. ----
    await(nu1.in_[1].ready());
    action
      nu1.in_[1].put(9'h001);
      phase <= 4;
    endaction
    await(!nu0.out[1].ready());
    if (nu0.out[1].get() != tagged Valid 9'h001) action
      $display("FAIL: nu0 byte = ", fshow(nu0.out[1].get()));
      ok <= False;
    endaction
    action
      nu0.out[1].deq();
      phase <= 5;
    endaction

    // ---- Phase 3: rate check -- pump 4 bytes and measure gap. ----
    action
      pumping <= True;
      nextByte <= 9'h010;
      expectByte <= 9'h010;
      phase <= 6;
    endaction
    await(pumpMoves == 4);
    action
      pumping <= False;
      phase <= 7;
    endaction
    if (gap != 4) action
      $display("FAIL: move gap = %0d, want 4", gap);
      ok <= False;
    endaction

    // ---- Report. ----
    action
      if (ok) $display("PimLinkTb: PASS");
      else    $display("PimLinkTb: FAIL");
    endaction
    $finish;
  endseq;

  mkAutoFSM(test);
endmodule

endpackage
