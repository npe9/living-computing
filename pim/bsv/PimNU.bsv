// PimNU.bsv -- Network Control Unit, per-port FIFO model.
//
// Documented facts (M92 = Nakashima et al., "Architecture and
// Implementation of PIM/m", FGCS '92 vol. 1, printed pages 425-435;
// see docs/pim_architecture.md):
//
//   * "The NU switches four adjacent-PE channel pairs plus the CPU
//      pair."                                                     p.427
//   * "A packet byte is 9 bits: 8 data bits plus a mark bit for
//      header/trailer."                                           p.427
//   * "Routing uses a RAM path table indexed by destination PE
//      number; each entry holds a 2-bit direction code (straight,
//      left, right, arrived)."                                    p.427
//   * "The read buffer holds a whole packet and raises an interrupt
//      when the packet tail arrives."                             p.427
//   * "The NU transmits one packet byte per four machine cycles,
//      independent of physical distance, using FIFO output buffers
//      and back-pressure rather than per-byte acknowledgements."  p.427
//
// Model: each input port has its own output FIFO.  The crossbar's
// destination routing is NOT modelled: the route-table argument is
// accepted for interface compatibility but unused.  The decision to
// stay per-port is recorded in plan.md WP4.1.  The output side is a
// separate port type so a consumer can dequeue a byte; the earlier
// single-port shape had no way to consume a byte and its put method
// conflicted with the move rule.
//
// Unknown and therefore NOT invented here: the packet header layout,
// the packet payload format, the meaning of the mark bit beyond
// header/trailer, the exact 2-bit direction encoding, the CPU-pair
// protocol, and the arbitration order between the five crossbar inputs.
// The module models the documented mechanism and marks the rest
// unknown; see docs/pim_architecture.md section 1.

package PimNU;

import Vector::*;

typedef Bit#(9)  PacketByte;
typedef Bit#(2)  Direction;
typedef 5        NumPorts;

interface PimNUInPort;
  method Action put(PacketByte b);
  method Bool ready();
endinterface

interface PimNUOutPort;
  method Maybe#(PacketByte) get();
  method Action deq();
  method Bool ready();
endinterface

typedef Vector#(NumPorts, PimNUInPort) PimNUInPorts;
typedef Vector#(NumPorts, PimNUOutPort) PimNUOutPorts;

interface PimNU;
  interface PimNUInPorts in_;
  interface PimNUOutPorts out;
  method Bool packetTail();
endinterface

module mkPimNU#(Vector#(256, Direction) routeTable)(PimNU);
  Vector#(NumPorts, Reg#(Maybe#(PacketByte))) inBuf <- replicateM(mkReg(Invalid));
  Vector#(NumPorts, Reg#(Maybe#(PacketByte))) outBuf <- replicateM(mkReg(Invalid));
  Vector#(NumPorts, Reg#(Bit#(2))) rate <- replicateM(mkReg(0));
  PulseWire tailPulse <- mkPulseWireOR;

  for (Integer i = 0; i < valueOf(NumPorts); i = i + 1) begin
    // The documented rate is one byte per four machine cycles; the
    // counter ticks every cycle, independently of the output buffer.
    rule tick (rate[i] != 0);
      rate[i] <= rate[i] - 1;
    endrule

    rule move (inBuf[i] matches tagged Valid .b
               &&& outBuf[i] matches tagged Invalid
               &&& rate[i] == 0);
      outBuf[i] <= tagged Valid b;
      inBuf[i] <= tagged Invalid;
      rate[i] <= 3;
      if (b[8] == 1) tailPulse.send();
    endrule
  end

  Vector#(NumPorts, PimNUInPort) inVec = newVector;
  for (Integer i = 0; i < valueOf(NumPorts); i = i + 1) begin
    inVec[i] = interface PimNUInPort;
      method Action put(PacketByte b) if (inBuf[i] matches tagged Invalid);
        inBuf[i] <= tagged Valid b;
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
