// PimNURouted.bsv -- Network Control Unit with a routed 5x5 crossbar.
//
// Documented facts (M92 = Nakashima et al., "Architecture and
// Implementation of PIM/m", FGCS '92 vol. 1, printed pages 425-435;
// see docs/pim_architecture.md section 1):
//
//   * "The NU switches four adjacent-PE channel pairs plus the CPU
//      pair."                                                     p.427
//   * "A packet byte is 9 bits: 8 data bits plus a mark bit for
//      header/trailer."                                           p.427
//   * "Routing uses a RAM path table indexed by destination PE
//      number; each entry holds a 2-bit direction code (straight,
//      left, right, arrived)."                                    p.427
//   * "The NU transmits one packet byte per four machine cycles,
//      independent of physical distance, using FIFO output buffers
//      and back-pressure rather than per-byte acknowledgements."  p.427
//
// MODEL -- every choice named here is invented by this model.  M92
// gives the path table and the four direction-code names, not their
// encoding, not the port numbering, and no arbitration order:
//
//   * Port numbering: 0 = North, 1 = East, 2 = South, 3 = West,
//     4 = CPU.
//   * Direction encoding: the 2-bit table entry is the absolute
//     output port, 0 = North, 1 = East, 2 = South, 3 = West.
//   * "Arrived" is not a table code: a packet whose destination PE
//     equals this NU's own PE is routed to the CPU port (4) by the
//     own-PE comparison, which wins over the table entry.  The
//     own-PE entry of the table is therefore a don't-care.
//   * Packet format: the first byte of a packet is the header.  Its
//     mark bit (bit 8) is 1 and bits [7:0] are the destination PE.
//     Payload bytes have mark bit 0.  The last byte is the tail: mark
//     bit 1 and bits [7:0] are the last payload byte.  Each input
//     port tracks its own packet state, so the five ports may carry
//     five interleaved packets.
//   * Per-input classification: a marked byte on an idle input is a
//     header (it records the destination and enters the packet); a
//     marked byte on an in-packet input is a tail (it leaves the
//     packet); an unmarked byte is payload.  The header is routed
//     using its own destination; payload and tail are routed using
//     the stored destination.
//   * Arbitration: when several inputs target one output, fixed
//     priority, lowest input-port index wins.  Losers stay in their
//     one-byte input buffer, so their put() stays back-pressured
//     until the byte finally moves.
//   * packetTail() pulses when a tail byte is moved into the CPU
//     output buffer (port 4).  It does not pulse for a header or a
//     payload delivered to the CPU, nor for a tail delivered to any
//     other port.
//
// The per-port FIFO model in PimNU.bsv (route table accepted but
// unused) is left untouched so the existing two-PE tests keep using
// it; this module reuses its types and interface.

package PimNURouted;

import Vector::*;
import PimNU::*;

// Absolute output port for one destination PE.  MODEL: own PE -> CPU.
function Bit#(3) routeOf(Bit#(8) myPE, Vector#(256, Direction) rt, Bit#(8) d);
  return (d == myPE) ? 3'd4 : {1'b0, rt[d]};
endfunction

// Is the byte buffered on this input a candidate for output port j?
function Bool candFor(Maybe#(PacketByte) b, Bit#(3) t, Bit#(3) j);
  if (b matches tagged Valid .x) return t == j;
  else return False;
endfunction

// Locked arbitration: when the output port is locked to one input, only
// that input is a candidate; otherwise every input is a candidate.
function Bool lockCand(Maybe#(Bit#(3)) l,
                       Vector#(NumPorts, Reg#(Maybe#(PacketByte))) ib,
                       Vector#(NumPorts, Reg#(Bit#(3))) tp,
                       Bit#(3) j);
  if (l matches tagged Valid .li) begin
    return candFor(ib[li], tp[li], j);
  end else begin
    return candFor(ib[0], tp[0], j)
        || candFor(ib[1], tp[1], j)
        || candFor(ib[2], tp[2], j)
        || candFor(ib[3], tp[3], j)
        || candFor(ib[4], tp[4], j);
  end
endfunction

// Lock-aware per-input candidacy: when the output port is locked, only the
// locked input may move; otherwise any input whose byte targets j may move.
function Bool canMove(Bit#(3) i, Maybe#(Bit#(3)) l,
                      Maybe#(PacketByte) b, Bit#(3) t, Bit#(3) j);
  case (l) matches
    tagged Valid .li: return li == i &&& candFor(b, t, j);
    tagged Invalid: return candFor(b, t, j);
  endcase
endfunction

module mkPimNURouted#(Bit#(8) myPE, Vector#(256, Direction) routeTable)(PimNU);
  Vector#(NumPorts, Reg#(Maybe#(PacketByte))) inBuf <- replicateM(mkReg(Invalid));
  Vector#(NumPorts, Reg#(Maybe#(PacketByte))) outBuf <- replicateM(mkReg(Invalid));
  Vector#(NumPorts, Reg#(Bit#(2))) rate <- replicateM(mkReg(0));
  // MODEL: per-input packet state and the output port the buffered
  // byte is headed for (computed once, when the byte is accepted).
  Vector#(NumPorts, Reg#(Bool)) inPacket <- replicateM(mkReg(False));
  Vector#(NumPorts, Reg#(Bit#(8))) destPE <- replicateM(mkReg(0));
  Vector#(NumPorts, Reg#(Bit#(3))) tgtPort <- replicateM(mkReg(0));
  Vector#(NumPorts, Reg#(Bool)) isTail <- replicateM(mkReg(False));
  Vector#(NumPorts, Reg#(Bool)) isHeader <- replicateM(mkReg(False));
  // MODEL: output lock.  A header locks its output port to its input until
  // the tail moves, so byte-level arbitration cannot separate a header from
  // its tail (which would deliver a header and a tail from different packets
  // on the same output port).
  Vector#(NumPorts, Reg#(Maybe#(Bit#(3)))) lock <- replicateM(mkReg(Invalid));
  PulseWire tailPulse <- mkPulseWireOR;

  for (Integer j = 0; j < valueOf(NumPorts); j = j + 1) begin
    Bit#(3) jj = fromInteger(j);

    // The documented one-byte-per-four-cycles rate, per output port.
    rule tick (rate[j] != 0);
      rate[j] <= rate[j] - 1;
    endrule

    // Crossbar move into output j.  MODEL: lowest input index wins;
    // the losing bytes stay buffered and keep their put() blocked.
    // A header locks the output port to its input until the tail moves,
    // so byte-level arbitration cannot separate a header from its tail.
    rule move (outBuf[j] matches tagged Invalid &&& rate[j] == 0
               &&& lockCand(lock[j], inBuf, tgtPort, jj));
      if (canMove(0, lock[j], inBuf[0], tgtPort[0], jj)) begin
        outBuf[j] <= inBuf[0];
        inBuf[0] <= tagged Invalid;
        isTail[0] <= False;
        isHeader[0] <= False;
        if (jj == 3'd4 && isTail[0]) tailPulse.send();
        if (isHeader[0]) lock[j] <= tagged Valid 0;
        else if (isTail[0]) lock[j] <= tagged Invalid;
      end
      else if (canMove(1, lock[j], inBuf[1], tgtPort[1], jj)) begin
        outBuf[j] <= inBuf[1];
        inBuf[1] <= tagged Invalid;
        isTail[1] <= False;
        isHeader[1] <= False;
        if (jj == 3'd4 && isTail[1]) tailPulse.send();
        if (isHeader[1]) lock[j] <= tagged Valid 1;
        else if (isTail[1]) lock[j] <= tagged Invalid;
      end
      else if (canMove(2, lock[j], inBuf[2], tgtPort[2], jj)) begin
        outBuf[j] <= inBuf[2];
        inBuf[2] <= tagged Invalid;
        isTail[2] <= False;
        isHeader[2] <= False;
        if (jj == 3'd4 && isTail[2]) tailPulse.send();
        if (isHeader[2]) lock[j] <= tagged Valid 2;
        else if (isTail[2]) lock[j] <= tagged Invalid;
      end
      else if (canMove(3, lock[j], inBuf[3], tgtPort[3], jj)) begin
        outBuf[j] <= inBuf[3];
        inBuf[3] <= tagged Invalid;
        isTail[3] <= False;
        isHeader[3] <= False;
        if (jj == 3'd4 && isTail[3]) tailPulse.send();
        if (isHeader[3]) lock[j] <= tagged Valid 3;
        else if (isTail[3]) lock[j] <= tagged Invalid;
      end
      else begin
        outBuf[j] <= inBuf[4];
        inBuf[4] <= tagged Invalid;
        isTail[4] <= False;
        isHeader[4] <= False;
        if (jj == 3'd4 && isTail[4]) tailPulse.send();
        if (isHeader[4]) lock[j] <= tagged Valid 4;
        else if (isTail[4]) lock[j] <= tagged Invalid;
      end
      // The documented one-byte-per-four-cycles rate: reload the countdown
      // whenever a byte enters this output port.  Without this the counter
      // reaches zero once and stays there, so the spacing collapses to the
      // input supply rate instead of the documented four cycles.
      rate[j] <= 3;
    endrule
  end

  Vector#(NumPorts, PimNUInPort) inVec = newVector;
  for (Integer i = 0; i < valueOf(NumPorts); i = i + 1) begin
    inVec[i] = interface PimNUInPort;
      method Action put(PacketByte b) if (inBuf[i] matches tagged Invalid);
        inBuf[i] <= tagged Valid b;
        // MODEL: header / payload / tail classification.  The header
        // is routed by its own destination; everything else by the
        // destination stored when the header arrived.
        if (b[8] == 1) begin
          if (!inPacket[i]) begin
            destPE[i] <= b[7:0];
            tgtPort[i] <= routeOf(myPE, routeTable, b[7:0]);
            inPacket[i] <= True;
            isHeader[i] <= True;
            isTail[i] <= False;
          end
          else begin
            tgtPort[i] <= routeOf(myPE, routeTable, destPE[i]);
            inPacket[i] <= False;
            isHeader[i] <= False;
            isTail[i] <= True;
          end
        end
        else begin
          tgtPort[i] <= routeOf(myPE, routeTable, destPE[i]);
          isHeader[i] <= False;
          isTail[i] <= False;
        end
      endmethod
      method Bool ready() = case (inBuf[i]) matches
        tagged Invalid: True;
        tagged Valid .x: False;
      endcase;
    endinterface;
  end

  Vector#(NumPorts, PimNUOutPort) outVec = newVector;
  for (Integer i = 0; i < valueOf(NumPorts); i = i + 1) begin
    outVec[i] = interface PimNUOutPort;
      method Maybe#(PacketByte) get() = outBuf[i];
      method Action deq() if (outBuf[i] matches tagged Valid .b);
        outBuf[i] <= tagged Invalid;
        // The lock is released by the tail moving into this output port
        // (see the move rule), NOT by a byte leaving it.  Releasing here
        // lets the next packet's header enter the port as soon as the
        // current header is dequeued, so the two packets' bytes
        // interleave on the link and the destination NU misclassifies
        // the second header as a tail.  Observed on the mesh as PE 12
        // receiving a header for PE 8 inside its own packet stream.
      endmethod
      method Bool ready() = case (outBuf[i]) matches
        tagged Invalid: True;
        tagged Valid .x: False;
      endcase;
    endinterface;
  end

  interface in_ = inVec;
  interface out = outVec;
  method Bool packetTail() = tailPulse._read();
endmodule

endpackage
