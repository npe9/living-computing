// PimNURoutedTb.bsv -- Bluesim testbench for the routed PIM/m NU crossbar.
//
// One NU, myPE = 0.  Route table (MODEL, see PimNURouted.bsv):
// destination 1 -> East (output port 1), destination 2 -> South
// (output port 2), destination 0 -> don't-care, because the own-PE
// comparison routes the packet to the CPU port (4) before the table
// is consulted.
//
// Byte encoding: bit 8 is the mark bit, bits [7:0] are data.  A
// header is marked and carries the destination PE, so the header for
// PE 1 is 9'h101.  (The task sketch wrote 9'h001, but bit 8 of
// 9'h001 is 0, which is a payload byte under the packet format; the
// header in this testbench is therefore the marked 9'h101.)
//
// Checks:
//   (a) a packet injected at the CPU port (in_[4]) and addressed to
//       PE 1 appears byte for byte on East (out[1]), header 9'h101,
//       payload 9'h000, tail 9'h100 in that order, and no tail
//       interrupt is raised;
//   (b) a packet addressed to PE 0 and injected at in_[0] appears on
//       the CPU port (out[4]) and packetTail() pulses exactly when
//       its tail is delivered;
//   (c) simultaneous injection on in_[0] and in_[1], both addressed
//       to PE 1: input 0 wins (lowest index) and its whole packet
//       (header, payload, tail) completes on output 1 before input 1's
//       header can enter the same port.  The output lock holds from a
//       packet's header until its tail moves, so input 1 stays
//       back-pressured while input 0's packet is in flight and its
//       packet follows once the lock releases;
//   (d) output 1 moves one byte per four machine cycles while input 0
//       is kept full and output 1 is drained.
//
// Run from bsv/: ./run_nu_routed_tb.sh
//
// Discriminating power (observed 2026-11-19, not predicted):
//   * routeOf changed to drop the own-PE check
//     (return {1'b0, rt[d]};) so a packet addressed to this PE
//     follows the table (dest 0 -> table entry 0 -> North) instead
//     of the CPU port:
//       FAIL: timeout at cycle 601, phase 2, pumping 0
//       (no "PimNURoutedTb: PASS" line; check (b) never sees a byte
//       on out[4])
//   * `rate[j] <= 3;` deleted from the move rule in PimNURouted.bsv
//     (the counter reaches zero once and stays there, so the
//     four-cycle pacing is never enforced):
//       FAIL: (d) output move gap = 2, want 4
//       PimNURoutedTb: FAIL

package PimNURoutedTb;

import Vector::*;
import StmtFSM::*;
import PimNU::*;
import PimNURouted::*;

(* synthesize *)
module mkPimNURoutedTb(Empty);
  Vector#(256, Direction) rt = update(update(replicate(0), 1, 1), 2, 2);
  PimNU nu <- mkPimNURouted(0, rt);

  Reg#(Bit#(32)) cycles <- mkReg(0);
  Reg#(Bit#(4)) phase <- mkReg(0);
  Reg#(Bool) ok <- mkReg(True);
  Reg#(Bool) tailSeen <- mkReg(False);

  // Phase (d) pump state.
  Reg#(Bool) pumping <- mkReg(False);
  Reg#(Bit#(9)) nextByte <- mkReg(0);
  Reg#(Bit#(9)) expectByte <- mkReg(0);
  Reg#(Bit#(32)) pumpMoves <- mkReg(0);

  // Output-1 move watcher for the rate check.
  Reg#(Bit#(32)) lastMove1 <- mkReg(0);
  Reg#(Bit#(32)) gap1 <- mkReg(0);
  Reg#(Bool) prevValid1 <- mkReg(False);

  rule count;
    cycles <= cycles + 1;
  endrule

  // Fail fast instead of hanging if the FSM waits on a condition that
  // never comes true.
  rule watchdog (cycles > 600);
    $display("FAIL: timeout at cycle %0d, phase %0d, pumping %0d",
             cycles, phase, pumping);
    $finish;
  endrule

  rule watchTail (nu.packetTail());
    tailSeen <= True;
  endrule

  // Detect output-1 valid transitions (the crossbar move's effect).
  rule watchRate;
    let v = !nu.out[1].ready();
    if (v && !prevValid1) begin
      gap1 <= cycles - lastMove1;
      lastMove1 <= cycles;
    end
    prevValid1 <= v;
  endrule

  // Phase (d): keep input 0's buffer full and drain output 1.  Two
  // rules, not one: a single rule calling both put and deq would
  // carry both implicit conditions in its guard, which never holds
  // once the output is drained.
  rule pumpIn (pumping);
    nu.in_[0].put(nextByte);
    nextByte <= nextByte + 1;
  endrule

  rule pumpOut (pumping);
    let got = nu.out[1].get();
    if (got != tagged Valid expectByte) begin
      $display("FAIL: pump byte = ", fshow(got), ", want ", fshow(expectByte));
      ok <= False;
    end
    expectByte <= expectByte + 1;
    pumpMoves <= pumpMoves + 1;
    nu.out[1].deq();
  endrule

  Stmt test = seq
    // ---- (a) CPU port -> East, three bytes in packet order. ----
    await(nu.in_[4].ready());
    action
      nu.in_[4].put(9'h101);              // header: mark 1, destination PE 1
      phase <= 1;
    endaction
    await(!nu.out[1].ready());
    if (nu.out[1].get() != tagged Valid 9'h101) action
      $display("FAIL: (a) header on out[1] = ", fshow(nu.out[1].get()));
      ok <= False;
    endaction
    action nu.out[1].deq(); endaction

    await(nu.in_[4].ready());
    action nu.in_[4].put(9'h000); endaction         // payload
    await(!nu.out[1].ready());
    if (nu.out[1].get() != tagged Valid 9'h000) action
      $display("FAIL: (a) payload on out[1] = ", fshow(nu.out[1].get()));
      ok <= False;
    endaction
    action nu.out[1].deq(); endaction

    await(nu.in_[4].ready());
    action nu.in_[4].put(9'h100); endaction         // tail
    await(!nu.out[1].ready());
    if (nu.out[1].get() != tagged Valid 9'h100) action
      $display("FAIL: (a) tail on out[1] = ", fshow(nu.out[1].get()));
      ok <= False;
    endaction
    action nu.out[1].deq(); endaction

    if (!nu.out[4].ready()) action
      $display("FAIL: (a) unexpected byte on the CPU port");
      ok <= False;
    endaction
    if (tailSeen) action
      $display("FAIL: (a) tail pulse for a packet not addressed to this PE");
      ok <= False;
    endaction

    // ---- (b) packet addressed to PE 0, arrives at the CPU port. ----
    action
      tailSeen <= False;
      phase <= 2;
    endaction
    await(nu.in_[0].ready());
    action nu.in_[0].put(9'h100); endaction         // header: mark 1, destination PE 0
    await(!nu.out[4].ready());
    if (nu.out[4].get() != tagged Valid 9'h100) action
      $display("FAIL: (b) header on out[4] = ", fshow(nu.out[4].get()));
      ok <= False;
    endaction
    if (tailSeen) action
      $display("FAIL: (b) tail pulse on the header");
      ok <= False;
    endaction
    action nu.out[4].deq(); endaction

    await(nu.in_[0].ready());
    action nu.in_[0].put(9'h055); endaction         // payload
    await(!nu.out[4].ready());
    if (nu.out[4].get() != tagged Valid 9'h055) action
      $display("FAIL: (b) payload on out[4] = ", fshow(nu.out[4].get()));
      ok <= False;
    endaction
    if (tailSeen) action
      $display("FAIL: (b) tail pulse on the payload");
      ok <= False;
    endaction
    action nu.out[4].deq(); endaction

    await(nu.in_[0].ready());
    action nu.in_[0].put(9'h1AA); endaction         // tail
    await(!nu.out[4].ready());
    if (nu.out[4].get() != tagged Valid 9'h1AA) action
      $display("FAIL: (b) tail on out[4] = ", fshow(nu.out[4].get()));
      ok <= False;
    endaction
    if (!tailSeen) action
      $display("FAIL: (b) tail interrupt not seen for the CPU packet");
      ok <= False;
    endaction
    action nu.out[4].deq(); endaction

    // ---- (c) two inputs for East, lowest index wins. ----
    // The header locks its output port until the packet's tail moves, so
    // input 0's packet must complete before input 1's header can enter
    // the same port.  Both headers are offered in the same cycle: the
    // lowest input index wins the lock and input 1 is back-pressured.
    action phase <= 3; endaction
    await(nu.in_[0].ready() && nu.in_[1].ready());
    action
      nu.in_[0].put(9'h101);                          // header, destination PE 1
      nu.in_[1].put(9'h101);                          // header, destination PE 1
    endaction
    await(!nu.out[1].ready());
    if (nu.out[1].get() != tagged Valid 9'h101) action
      $display("FAIL: (c) arbitration picked ", fshow(nu.out[1].get()),
               ", want input 0's 9'h101");
      ok <= False;
    endaction
    if (nu.in_[1].ready()) action
      $display("FAIL: (c) losing input 1 was not back-pressured");
      ok <= False;
    endaction
    action nu.out[1].deq(); endaction

    // Input 0's packet continues: payload then tail, which releases the lock.
    await(nu.in_[0].ready());
    action nu.in_[0].put(9'h0A0); endaction
    await(!nu.out[1].ready());
    if (nu.out[1].get() != tagged Valid 9'h0A0) action
      $display("FAIL: (c) in_[0] payload on out[1] = ", fshow(nu.out[1].get()));
      ok <= False;
    endaction
    action nu.out[1].deq(); endaction

    await(nu.in_[0].ready());
    action nu.in_[0].put(9'h100); endaction            // tail
    await(!nu.out[1].ready());
    if (nu.out[1].get() != tagged Valid 9'h100) action
      $display("FAIL: (c) in_[0] tail on out[1] = ", fshow(nu.out[1].get()));
      ok <= False;
    endaction
    action nu.out[1].deq(); endaction

    // The lock is now free: input 1's header follows with its own packet.
    await(!nu.out[1].ready());
    if (nu.out[1].get() != tagged Valid 9'h101) action
      $display("FAIL: (c) in_[1] header on out[1] = ", fshow(nu.out[1].get()));
      ok <= False;
    endaction
    action nu.out[1].deq(); endaction

    await(nu.in_[1].ready());
    action nu.in_[1].put(9'h0B0); endaction
    await(!nu.out[1].ready());
    if (nu.out[1].get() != tagged Valid 9'h0B0) action
      $display("FAIL: (c) in_[1] payload on out[1] = ", fshow(nu.out[1].get()));
      ok <= False;
    endaction
    action nu.out[1].deq(); endaction

    await(nu.in_[1].ready());
    action nu.in_[1].put(9'h100); endaction            // tail
    await(!nu.out[1].ready());
    if (nu.out[1].get() != tagged Valid 9'h100) action
      $display("FAIL: (c) in_[1] tail on out[1] = ", fshow(nu.out[1].get()));
      ok <= False;
    endaction
    action nu.out[1].deq(); endaction
    action phase <= 4; endaction

    // ---- (d) one byte per four cycles on output 1. ----
    action
      pumping <= True;
      nextByte <= 9'h020;                 // payload bytes, mark bit 0
      expectByte <= 9'h020;
      pumpMoves <= 0;
      phase <= 5;
    endaction
    await(pumpMoves == 4);
    action
      pumping <= False;
      phase <= 6;
    endaction
    if (gap1 != 4) action
      $display("FAIL: (d) output move gap = %0d, want 4", gap1);
      ok <= False;
    endaction

    action
      if (ok) $display("PimNURoutedTb: PASS");
      else    $display("PimNURoutedTb: FAIL");
    endaction
    $finish;
  endseq;

  mkAutoFSM(test);
endmodule

endpackage
