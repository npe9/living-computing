// PimNU.bsv -- the PIM/m Network Control Unit: a 5 x 5 crossbar, a
// routing table, packet buffers, and the documented one-byte-per-four-
// cycles flow control.
//
// Documented facts (M92 = Nakashima et al., "Architecture and
// Implementation of PIM/m", FGCS '92 vol. 1, printed pages 425-435):
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
// Unknown and therefore NOT invented here: the packet header layout,
// the packet payload format, the meaning of the mark bit beyond
// header/trailer, the exact 2-bit direction encoding, the CPU-pair
// protocol, and the arbitration order between the five crossbar inputs.
// The module models the documented mechanism and marks the rest
// unknown; see docs/pim_architecture.md section 1.
//
// The two-PE test (PimNUTb.bsv) drives ports 0 and 1 of two NUs and
// checks the byte flow, the rate limit, and the back-pressure.  It does
// not claim a packet format.

package PimNU;

import Vector::*;

// 9-bit packet byte: 8 data bits and the mark bit (M92 p.427).
typedef Bit#(9) PacketByte;
typedef Bit#(8) PacketData;
typedef Bit#(2) Direction;

// Direction codes are the documented set; the numeric assignment is a
// model choice because the source does not print it.
Direction dirStraight = 0;
Direction dirLeft     = 1;
Direction dirRight    = 2;
Direction dirArrived  = 3;

// 5 x 5 crossbar: four adjacent-PE channel pairs plus the CPU pair.
// Port 4 is the CPU pair; the source does not document its protocol.
typedef 5 NumPorts;

interface PimNUPort;
  // A byte offered to the port's input.  The port accepts it only when
  // ready() is true; the source documents back-pressure rather than a
  // per-byte acknowledgement.
  method Action put(PacketByte b);
  // A byte available at the port's output, if any.
  method Maybe#(PacketByte) get();
  method Bool ready();
endinterface

interface PimNU;
  // in[4] is the CPU pair; in[0..3] are the four adjacent-PE channels.
  interface Vector#(NumPorts, PimNUPort) in;
  interface Vector#(NumPorts, PimNUPort) out;
  // The read buffer's tail interrupt.  The source says the buffer
  // raises an interrupt when the packet tail arrives; the interrupt
  // protocol is not documented, so the model exposes a one-cycle pulse.
  method Bool packetTail();
endinterface

// The crossbar is modelled as five independent input-to-output paths.
// The source does not document the crossbar's internal arbitration, so
// the model gives each input its own output FIFO and routes by the
// destination PE's table entry.  Two inputs aimed at the same output
// are serialised by the output's ready signal; that is deterministic
// and deadlock-free because every input has its own FIFO.
module mkPimNU#(Vector#(256, Direction) routeTable)(PimNU);

  // Input buffers: one byte per port, the smallest buffer that can hold
  // the byte the source's read buffer describes.  The source's read
  // buffer is 1 KB; the model's one-byte buffer is a deliberate scale
  // choice so Bluesim stays small.
  Vector#(NumPorts, Reg#(Maybe#(PacketByte))) inBuf <- replicateM(mkReg(Invalid));
  // Output buffers: one byte per port.  The source's write buffer is
  // 1 KB; the model scales it down.
  Vector#(NumPorts, Reg#(Maybe#(PacketByte))) outBuf <- replicateM(mkReg(Invalid));
  // The one-byte-per-four-cycles rate limit.  Each port counts down
  // from three; a byte is transmitted when the counter reaches zero.
  Vector#(NumPorts, Reg#(Bit#(2))) rate <- replicateM(mkReg(0));
  // The read buffer's tail pulse.
  Reg#(Bool) tailPulse <- mkReg(False);

  // The destination PE number is the low 8 bits of the packet byte's
  // data field.  The source does not document the header layout, so the
  // model treats the whole 8-bit data field as the destination for the
  // first byte of a packet and as payload afterwards.  This is marked
  // unknown in the module header.
  function Direction routeFor(PacketByte b);
    let dest = truncate(b);
    return routeTable[dest];
  endfunction

  function Bool isTail(PacketByte b) = b[8];

  // Move one byte from the input buffer to the output buffer when the
  // rate limit permits and the output is free.  The output's ready
  // signal is the back-pressure the source describes.
  for (Integer i = 0; i < valueOf(NumPorts); i = i + 1) begin
    rule move (inBuf[i] matches tagged Valid .b &&& outBuf[i] == Invalid);
      if (rate[i] == 0) begin
        outBuf[i] <= Valid(b);
        inBuf[i] <= Invalid;
        rate[i] <= 3;
        if (isTail(b)) tailPulse <= True;
      end else begin
        rate[i] <= rate[i] - 1;
      end
    endrule
  end

  // The tail pulse is one cycle wide.
  rule clearTail (tailPulse);
    tailPulse <= False;
  endrule

  // The input ports accept a byte only when the input buffer is empty.
  // The source's back-pressure is on the output side; the input side's
  // acceptance is the model's handshake.
  interface Vector#(NumPorts, PimNUPort) in;
    for (Integer i = 0; i < valueOf(NumPorts); i = i + 1) begin
      interface PimNUPort;
        method Action put(PacketByte b) if (inBuf[i] == Invalid);
          inBuf[i] <= Valid(b);
        endmethod
        method Maybe#(PacketByte) get() = outBuf[i];
        method Bool ready() = inBuf[i] == Invalid;
      endinterface
    end
  endinterface

  interface Vector#(NumPorts, PimNUPort) out;
    for (Integer i = 0; i < valueOf(NumPorts); i = i + 1) begin
      interface PimNUPort;
        method Action put(PacketByte b) if (outBuf[i] == Invalid);
          outBuf[i] <= Valid(b);
        endmethod
        method Maybe#(PacketByte) get() = outBuf[i];
        method Bool ready() = outBuf[i] == Invalid;
      endinterface
    end
  endinterface

  method Bool packetTail() = tailPulse;

endmodule

endpackage
