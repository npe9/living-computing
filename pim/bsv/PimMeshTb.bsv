// PimMeshTb.bsv -- 4 x 4 routed PIM/m mesh testbench.
//
// The mesh topology, PE numbering, route-table encoding and arbitration
// order are model-defined (see the MODEL block in PimMesh.bsv); the
// packet format is model-defined (see PimNURouted.bsv).  This
// testbench fixes the dimension to 4 (16 PEs), so PE = y*4 + x and the
// opposite corner of PE i is PE 15 - i.
//
// Checks, in order:
//   (a) four-byte packet PE 0 -> PE 15 (header, two payload bytes,
//       tail) is delivered byte-for-byte to PE 15's CPU out port, and
//       PE 15's packetTail pulse fires;
//   (b) the reverse two-byte packet PE 15 -> PE 0 is delivered to
//       PE 0's CPU out port;
//   (c) deadlock-directed all-to-opposite-corner traffic: every PE
//       injects a two-byte packet to PE 15 - i, all headers in one
//       cycle and all tails in one cycle, and every PE must receive its
//       packet within the watchdog bound (a bounded-cycle check; on
//       timeout the watchdog names each PE that is short);
//   (d) one byte per four cycles on the last link into a PE: a
//       four-byte packet PE 0 -> PE 1 is received with arrival gaps of
//       exactly four cycles.
//
// Each received byte is compared with the byte expected for the current
// phase; an unexpected byte is reported as FAIL immediately and the
// per-port got-count reports which PE is short.
//
// Run from bsv/: ./run_mesh_tb.sh
//
// Discriminating power: see the "observed injected failure" note after
// the phase checks below (filled in from an actual bug injection, not
// predicted).

package PimMeshTb;

import Vector::*;
import StmtFSM::*;
import PimNU::*;
import PimMesh::*;

typedef 4 TbDim;
typedef TMul#(TbDim, TbDim) NumPEs;

function PacketByte headerTo(Bit#(8) dest) = {1'b1, dest};
function PacketByte tailOf(Bit#(8) payload) = {1'b1, payload};

// Expected bytes for the named-checked packets.
function PacketByte testAByte(Bit#(8) i);
  case (i)
    0: return 9'h10F;   // header, destination PE 15
    1: return 9'h0A1;   // payload
    2: return 9'h0B2;   // payload
    default: return 9'h1C3;  // tail carrying the last payload byte
  endcase
endfunction

function PacketByte testBByte(Bit#(8) i);
  case (i)
    0: return 9'h100;   // header, destination PE 0
    default: return 9'h15A;  // tail
  endcase
endfunction

function PacketByte testDByte(Bit#(8) i);
  case (i)
    0: return 9'h101;   // header, destination PE 1
    1: return 9'h031;   // payload
    2: return 9'h042;   // payload
    default: return 9'h153;  // tail
  endcase
endfunction

// Bytes expected at each PE in each phase.
function Bit#(8) expectedLen(Bit#(3) mode, Bit#(8) j);
  case (mode)
    1: return (j == 8'd15) ? 8'd4 : 8'd0;  // (a) PE 0 -> PE 15
    2: return (j == 8'd0)  ? 8'd2 : 8'd0;  // (b) PE 15 -> PE 0
    3: return 8'd2;                        // (c) all-to-opposite
    4: return (j == 8'd1)  ? 8'd4 : 8'd0;  // (d) PE 0 -> PE 1
    default: return 8'd0;
  endcase
endfunction

(* synthesize *)
module mkPimMeshTb(Empty);
  PimMesh#(TbDim) mesh <- mkPimMesh;

  Reg#(Bit#(32)) cycles <- mkReg(0);
  Reg#(Bit#(8))  phase  <- mkReg(0);
  Reg#(Bit#(3))  mode   <- mkReg(0);
  Reg#(Bit#(32)) totalBytes <- mkReg(0);
  Reg#(Bit#(8))  li <- mkReg(0);
  Reg#(Bit#(8))  k  <- mkReg(0);

  Vector#(NumPEs, Reg#(Bit#(8)))  gotCount <- replicateM(mkReg(0));
  Vector#(NumPEs, Reg#(Bool))     bad      <- replicateM(mkReg(False));
  Vector#(NumPEs, Reg#(Bool))     tailSeen <- replicateM(mkReg(False));
  Vector#(NumPEs, Reg#(Bit#(32))) arrivals <- replicateM(mkReg(0));
  Vector#(NumPEs, Reg#(Bit#(32))) lastArrival <- replicateM(mkReg(0));
  Vector#(NumPEs, Reg#(Bit#(32))) gap <- replicateM(mkReg(0));
  Vector#(NumPEs, Reg#(Bool))     prevValid <- replicateM(mkReg(False));

  // Test (c) expected bytes, indexed by receiving PE.  Port j receives
  // from sender 15-j, whose destination is j.
  Vector#(NumPEs, PacketByte) cHdr = newVector;
  Vector#(NumPEs, PacketByte) cTail = newVector;
  for (Integer j = 0; j < valueOf(NumPEs); j = j + 1) begin
    cHdr[j]  = headerTo(fromInteger(j));
    cTail[j] = tailOf(fromInteger(64 + (15 - j)));  // 0x40 + sender
  end

  rule count;
    cycles <= cycles + 1;
  endrule

  // Bounded-cycle check for every phase.  On timeout, name each PE
  // that is short so a deadlocked or misrouted packet is identifiable.
  rule watchdog (cycles > 5000);
    for (Integer j = 0; j < valueOf(NumPEs); j = j + 1)
      if (gotCount[j] != expectedLen(mode, fromInteger(j)))
        $display("FAIL: PE %0d got %0d of %0d bytes in phase %0d, mode %0d",
                 j, gotCount[j], expectedLen(mode, fromInteger(j)), phase, mode);
    $display("FAIL: timeout at cycle %0d, phase %0d, mode %0d",
             cycles, phase, mode);
    $display("PimMeshTb: FAIL");
    $finish;
  endrule

  for (Integer j = 0; j < valueOf(NumPEs); j = j + 1) begin
    // Receive and check one byte, then dequeue it so the next byte can
    // move.  gotCount counts every byte seen (including unexpected
    // ones), so a missing byte shows up as a short count.
    rule recv (mesh.cpuOut[j].get() matches tagged Valid .b);
      Bit#(8) n = gotCount[j];
      Bit#(8) len = expectedLen(mode, fromInteger(j));
      PacketByte want = (mode == 3'd1) ? testAByte(n)
                      : (mode == 3'd2) ? testBByte(n)
                      : (mode == 3'd3) ? ((n == 0) ? cHdr[j] : cTail[j])
                      : testDByte(n);
      if (n >= len) begin
        $display("FAIL: PE ", j, " unexpected byte ", fshow(b),
                 " (phase ", phase, ", mode ", mode, ")");
        bad[j] <= True;
      end
      else if (b != want) begin
        $display("FAIL: PE ", j, " byte ", n, " = ", fshow(b),
                 ", want ", fshow(want), " (phase ", phase, ", mode ", mode, ")");
        bad[j] <= True;
      end
      gotCount[j] <= n + 1;
      totalBytes <= totalBytes + 1;
      mesh.cpuOut[j].deq();
    endrule

    rule watchTail (mesh.packetTail()[j]);
      tailSeen[j] <= True;
    endrule

    // One-byte-per-four-cycles check: record the gap between output
    // valid transitions on this port.
    rule watchArrival;
      let v = !mesh.cpuOut[j].ready();
      if (v && !prevValid[j]) begin
        arrivals[j] <= arrivals[j] + 1;
        gap[j] <= cycles - lastArrival[j];
        lastArrival[j] <= cycles;
      end
      prevValid[j] <= v;
    endrule
  end

  Stmt test = seq
    // ------------------------------------------------------------
    // Common reset: quiet the network, clear every per-PE counter.
    // ------------------------------------------------------------
    action
      mode <= 0;
      phase <= 0;
    endaction
    for (li <= 0; li < fromInteger(valueOf(NumPEs)); li <= li + 1) seq
      action
        gotCount[li] <= 0;
        bad[li] <= False;
        tailSeen[li] <= False;
      endaction
    endseq

    // ------------------------------------------------------------
    // (a) PE 0 -> PE 15: header, two payload bytes, tail.
    // ------------------------------------------------------------
    action
      totalBytes <= 0;
      mode <= 3'd1;
      phase <= 1;
    endaction
    for (k <= 0; k < 4; k <= k + 1) seq
      await(mesh.cpuIn[0].ready());
      action
        mesh.cpuIn[0].put(testAByte(k));
      endaction
    endseq
    await(totalBytes >= 4);
    for (li <= 0; li < fromInteger(valueOf(NumPEs)); li <= li + 1) seq
      action
        if (gotCount[li] != expectedLen(3'd1, li)) begin
          $display("FAIL: PE %0d got %0d of %0d bytes in phase 1",
                   li, gotCount[li], expectedLen(3'd1, li));
          bad[li] <= True;
        end
      endaction
    endseq
    action
      if (!tailSeen[15]) begin
        $display("FAIL: PE 15 packetTail pulse missing for the PE 0 -> PE 15 packet");
        bad[15] <= True;
      end
      phase <= 2;
    endaction

    // ------------------------------------------------------------
    // (b) PE 15 -> PE 0: header and tail.
    // ------------------------------------------------------------
    action
      mode <= 0;
      totalBytes <= 0;
    endaction
    for (li <= 0; li < fromInteger(valueOf(NumPEs)); li <= li + 1) seq
      action
        gotCount[li] <= 0;
        bad[li] <= False;
        tailSeen[li] <= False;
      endaction
    endseq
    action
      mode <= 3'd2;
      phase <= 3;
    endaction
    for (k <= 0; k < 2; k <= k + 1) seq
      await(mesh.cpuIn[15].ready());
      action
        mesh.cpuIn[15].put(testBByte(k));
      endaction
    endseq
    await(totalBytes >= 2);
    for (li <= 0; li < fromInteger(valueOf(NumPEs)); li <= li + 1) seq
      action
        if (gotCount[li] != expectedLen(3'd2, li)) begin
          $display("FAIL: PE %0d got %0d of %0d bytes in phase 2",
                   li, gotCount[li], expectedLen(3'd2, li));
          bad[li] <= True;
        end
      endaction
    endseq
    action
      if (!tailSeen[0]) begin
        $display("FAIL: PE 0 packetTail pulse missing for the PE 15 -> PE 0 packet");
        bad[0] <= True;
      end
      phase <= 4;
    endaction

    // ------------------------------------------------------------
    // (c) Deadlock-directed: every PE sends to its opposite corner.
    // All 16 headers enter in one cycle; then all 16 tails enter in
    // one cycle once every CPU input buffer has drained.  A missing
    // packet is named by the watchdog/per-PE check above/below.
    // ------------------------------------------------------------
    action
      mode <= 0;
      totalBytes <= 0;
    endaction
    for (li <= 0; li < fromInteger(valueOf(NumPEs)); li <= li + 1) seq
      action
        gotCount[li] <= 0;
        bad[li] <= False;
        tailSeen[li] <= False;
      endaction
    endseq
    action
      mode <= 3'd3;
      phase <= 5;
    endaction
    action
      mesh.cpuIn[0].put(headerTo(8'd15));
      mesh.cpuIn[1].put(headerTo(8'd14));
      mesh.cpuIn[2].put(headerTo(8'd13));
      mesh.cpuIn[3].put(headerTo(8'd12));
      mesh.cpuIn[4].put(headerTo(8'd11));
      mesh.cpuIn[5].put(headerTo(8'd10));
      mesh.cpuIn[6].put(headerTo(8'd9));
      mesh.cpuIn[7].put(headerTo(8'd8));
      mesh.cpuIn[8].put(headerTo(8'd7));
      mesh.cpuIn[9].put(headerTo(8'd6));
      mesh.cpuIn[10].put(headerTo(8'd5));
      mesh.cpuIn[11].put(headerTo(8'd4));
      mesh.cpuIn[12].put(headerTo(8'd3));
      mesh.cpuIn[13].put(headerTo(8'd2));
      mesh.cpuIn[14].put(headerTo(8'd1));
      mesh.cpuIn[15].put(headerTo(8'd0));
    endaction
    action
      mesh.cpuIn[0].put(tailOf(8'h40 + 8'd0));
      mesh.cpuIn[1].put(tailOf(8'h40 + 8'd1));
      mesh.cpuIn[2].put(tailOf(8'h40 + 8'd2));
      mesh.cpuIn[3].put(tailOf(8'h40 + 8'd3));
      mesh.cpuIn[4].put(tailOf(8'h40 + 8'd4));
      mesh.cpuIn[5].put(tailOf(8'h40 + 8'd5));
      mesh.cpuIn[6].put(tailOf(8'h40 + 8'd6));
      mesh.cpuIn[7].put(tailOf(8'h40 + 8'd7));
      mesh.cpuIn[8].put(tailOf(8'h40 + 8'd8));
      mesh.cpuIn[9].put(tailOf(8'h40 + 8'd9));
      mesh.cpuIn[10].put(tailOf(8'h40 + 8'd10));
      mesh.cpuIn[11].put(tailOf(8'h40 + 8'd11));
      mesh.cpuIn[12].put(tailOf(8'h40 + 8'd12));
      mesh.cpuIn[13].put(tailOf(8'h40 + 8'd13));
      mesh.cpuIn[14].put(tailOf(8'h40 + 8'd14));
      mesh.cpuIn[15].put(tailOf(8'h40 + 8'd15));
    endaction
    // Bounded wait: the watchdog at cycle 5000 names any short PE.
    await(totalBytes >= 32);
    for (li <= 0; li < fromInteger(valueOf(NumPEs)); li <= li + 1) seq
      action
        if (gotCount[li] != 8'd2)
          $display("FAIL: PE %0d got %0d of 2 bytes in the all-to-opposite phase",
                   li, gotCount[li]);
        if (!tailSeen[li])
          $display("FAIL: PE %0d packetTail pulse missing in the all-to-opposite phase", li);
        if (gotCount[li] != 8'd2 || !tailSeen[li])
          bad[li] <= True;
      endaction
    endseq
    action
      phase <= 6;
    endaction

    // ------------------------------------------------------------
    // (d) Rate: four-byte packet PE 0 -> PE 1, adjacent link.
    // ------------------------------------------------------------
    action
      mode <= 0;
      totalBytes <= 0;
      arrivals[1] <= 0;
      gap[1] <= 0;
      lastArrival[1] <= cycles;
    endaction
    for (li <= 0; li < fromInteger(valueOf(NumPEs)); li <= li + 1) seq
      action
        gotCount[li] <= 0;
        bad[li] <= False;
        tailSeen[li] <= False;
      endaction
    endseq
    action
      mode <= 3'd4;
      phase <= 7;
    endaction
    for (k <= 0; k < 4; k <= k + 1) seq
      await(mesh.cpuIn[0].ready());
      action
        mesh.cpuIn[0].put(testDByte(k));
      endaction
    endseq
    await(totalBytes >= 4);
    action
      if (gotCount[1] != 8'd4)
        $display("FAIL: PE 1 got %0d of 4 bytes in the rate phase", gotCount[1]);
      if (arrivals[1] != 4)
        $display("FAIL: PE 1 saw %0d output-valid transitions, want 4", arrivals[1]);
      if (gap[1] != 4)
        $display("FAIL: PE 1 arrival gap = %0d, want 4 cycles", gap[1]);
      if (!tailSeen[1])
        $display("FAIL: PE 1 packetTail pulse missing in the rate phase");
      if (gotCount[1] != 8'd4 || arrivals[1] != 4 || gap[1] != 4 || !tailSeen[1])
        bad[1] <= True;
      phase <= 8;
    endaction

    // ------------------------------------------------------------
    // Summary.
    // ------------------------------------------------------------
    for (li <= 0; li < fromInteger(valueOf(NumPEs)); li <= li + 1) seq
      action
        if (bad[li]) $display("FAIL: PE %0d reported an error", li);
      endaction
    endseq
    action
      if (bad[0] || bad[1] || bad[2] || bad[3]
          || bad[4] || bad[5] || bad[6] || bad[7]
          || bad[8] || bad[9] || bad[10] || bad[11]
          || bad[12] || bad[13] || bad[14] || bad[15])
        $display("PimMeshTb: FAIL");
      else
        $display("PimMeshTb: PASS");
    endaction
    $finish;
  endseq;

  // Discriminating power -- observed injected failure, 2026-11-19, not
  // predicted.  Injection: `lock[i] <= Invalid;` restored in the deq
  // method of PimNURouted.bsv (the output lock is released as soon as a
  // header leaves the port, so the next packet's header can interleave
  // on the same link).  Observed set, verbatim:
  //   FAIL: PE           5 byte   1 = 'h101, want 'h14a (phase   5, mode 3)
  //   FAIL: PE           6 byte   1 = 'h102, want 'h149 (phase   5, mode 3)
  //   FAIL: PE           9 byte   1 = 'h10d, want 'h146 (phase   5, mode 3)
  //   FAIL: PE          10 byte   1 = 'h10e, want 'h145 (phase   5, mode 3)
  //   FAIL: PE           4 byte   1 = 'h100, want 'h14b (phase   5, mode 3)
  //   FAIL: PE           3 byte   1 = 'h107, want 'h14c (phase   5, mode 3)
  //   FAIL: PE          12 byte   1 = 'h108, want 'h143 (phase   5, mode 3)
  //   FAIL: PE          15 byte   1 = 'h10b, want 'h140 (phase   5, mode 3)
  //   FAIL: PE 0 got 0 of 2 bytes in phase 5, mode 3
  //   FAIL: PE 1 got 0 of 2 bytes in phase 5, mode 3
  //   FAIL: PE 2 got 0 of 2 bytes in phase 5, mode 3
  //   FAIL: PE 7 got 0 of 2 bytes in phase 5, mode 3
  //   FAIL: PE 8 got 0 of 2 bytes in phase 5, mode 3
  //   FAIL: PE 11 got 0 of 2 bytes in phase 5, mode 3
  //   FAIL: PE 13 got 0 of 2 bytes in phase 5, mode 3
  //   FAIL: PE 14 got 0 of 2 bytes in phase 5, mode 3
  //   FAIL: timeout at cycle 5001, phase 5, mode 3
  //   PimMeshTb: FAIL
  // The wrong bytes are headers for other destinations ('h101 = header
  // to PE 1, 'h102 = header to PE 2, ...), i.e. header interleaving on
  // the link, and the all-zero PEs are the packets that never arrive.
  // Reverting the injection restores PASS.

  mkAutoFSM(test);
endmodule

endpackage
