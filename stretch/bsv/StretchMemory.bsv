// StretchMemory.bsv -- the 7030's core memory units and memory bus
// control unit, stage 1 of docs/microarchitecture_plan.md.
//
// SOURCES. Buchholz, Planning a Computer System (1962) §14.1 (p.202):
// "The core memory consists of several units of 16,384 words,
// operating on a 2.1-µsec read-write cycle. Each unit is self-contained
// and has its own clock, addressing circuits, data registers, and
// checking circuits. A typical 7030 system may have six memory units.
// To achieve a high degree of overlap, addresses are interleaved. The
// first four units share a block of 65,536 addresses, so that four
// consecutive word addresses lie in four different memory units. The
// next two units share a block of 32,768 addresses with two-way
// interleaving." §14.3 (pp.205-206): "The memory bus unit monitors the
// requests for storing in or fetching from memory and sets up a
// priority scheme ... the exchange and disk synchronizer will get
// highest priority, followed by the CPU. In the CPU the operand-fetch
// mechanism, the look-ahead unit, has priority over the instruction-
// fetch mechanism. Altogether the memory bus unit receives requests
// from and assigns priority to eight different channels. Since access
// to a memory unit can be independently initiated from several
// sources, a busy condition can exist. Here again, the memory bus
// tests for the busy conditions and delays the requesting unit until
// the desired memory unit is ready. The return address identifying the
// requesting unit is remembered, and the information is forwarded when
// it becomes available. Requests for stores and fetches can be
// processed at a rate of one every 0.3 µsec. If no busy or priority
// conditions exist, the time to return the word to the requesting unit
// is 1.6 µsec, a direct function of the memory read-out time." Blosk,
// TR00.722 p.19: every external fetch "involve[s] sending an 18 bit
// word address and a three bit return address to the bus control
// unit."
//
// TIME BASE. One Bluespec clock = one E-box cycle = 0.3 µs (7030
// Performance Characteristics vol.1 p.3-2, "the basic machine cycles,
// which is presently 0.3 microsecond"). So a memory unit is busy for
// 7 clocks per access (2.1 µs) and presents read data 5 clocks after
// accepting the request (~1.6 µs, the read-out time); the remainder of
// the cycle is the destructive-read regeneration during which the unit
// cannot accept another request.
//
// SCOPE OF THIS STAGE. One requester (the CPU's StretchStorage, which
// serializes the core's reads and queues its writes); the arbiter's
// eight-channel priority scheme becomes real when the look-ahead and
// the exchange are separate requesters (plan stages 3 and later). No
// ECC modeling (the I checker's cycle is charged in the instruction
// unit, stage 2). Addresses at or beyond the installed 98,304 words
// (six units) are "nonexistent": reads return 0, writes are dropped
// (the real machine's address-invalid indication is not yet modeled).

package StretchMemory;

import BRAM::*;
import Vector::*;
import DefaultValue::*;
import StretchTypes::*;

typedef 6     NumUnits;
typedef 16384 UnitWords;
typedef Bit#(14) UnitIndex;
typedef 98304 InstalledWords;            // 4 x 16K interleaved + 2 x 16K interleaved
Integer memCycleClocks = 7;              // 2.1 us at 0.3 us per clock
Integer memReadClocks  = 5;              // ~1.6 us read-out

function Bool installed(WordAddr a) = (a < fromInteger(valueOf(InstalledWords)));

// Interleave map (Buchholz §14.1): four-way over the first 65,536
// words, two-way over the next 32,768.
function Bit#(3) unitOf(WordAddr a);
  if (a < 65536) return {1'b0, a[1:0]};
  else return {2'b10, a[0]};
endfunction

function UnitIndex indexOf(WordAddr a);
  if (a < 65536) return a[15:2];
  else begin
    Bit#(18) rel = a - 65536;
    return rel[14:1];
  end
endfunction

// Return tag (Blosk p.19: "a three bit return address to the bus
// control unit ... indicates which Y register in this I unit, or which
// of the four lookahead levels is to receive the word"). Here: 0 =
// the operand channel (execute()'s own follow-up reads and the
// testbenches), 1 = 1Y, 2 = 2Y, 3-6 = look-ahead levels 1-4.
typedef Bit#(3) RetTag;
typedef 7 NumTags;   // 0 operand, 1-2 = 1Y/2Y, 3-6 = look-ahead levels 1-4
typedef struct { Bool write; WordAddr addr; Word64 data; RetTag tag; } MemReq deriving (Bits, Eq, FShow);

// ---------------------------------------------------------------------
// One 16K-word memory unit.
// ---------------------------------------------------------------------
interface MemoryUnit;
  method Bool free();                              // can accept a request this clock
  method Action request(Bool write, UnitIndex idx, Word64 data, RetTag tag);
  method Bool dataReady();                         // read data presented
  method RetTag dataTag();
  method ActionValue#(Word64) takeData();
endinterface

module mkMemoryUnit(MemoryUnit);
  BRAM_Configure cfg = defaultValue;
  cfg.latency = 1;
  BRAM1Port#(UnitIndex, Word64) ram <- mkBRAM1Server(cfg);

  Reg#(Bit#(4))        busy    <- mkReg(0);   // clocks left in the current cycle
  Reg#(Bit#(4))        readDue <- mkReg(0);   // clocks until read data is presented
  Reg#(Word64)         raw     <- mkReg(0);   // BRAM read-out, held until due
  Reg#(Maybe#(Word64)) dataOut <- mkReg(tagged Invalid);
  Reg#(RetTag)         tagReg  <- mkReg(0);   // return tag of the read in progress

  RWire#(Tuple4#(Bool, UnitIndex, Word64, RetTag)) reqW <- mkRWire;
  PulseWire takeW <- mkPulseWire;

  rule drain;
    let v <- ram.portA.response.get();
    raw <= v;
  endrule

  // ram.portA.request.put carries an implicit "request FIFO not
  // full" condition; with at most one request per 7 clocks it is
  // always true, so it is left in the rule's guard rather than
  // asserted away.
  (* fire_when_enabled *)
  rule tick;
    if (reqW.wget matches tagged Valid {.wr, .idx, .d, .t}) begin
      ram.portA.request.put(BRAMRequest{ write: wr, responseOnWrite: False,
                                          address: idx, datain: d });
      busy    <= fromInteger(memCycleClocks);
      readDue <= wr ? 0 : fromInteger(memReadClocks);
      tagReg  <= t;
    end else begin
      if (busy != 0) busy <= busy - 1;
      if (readDue > 1) readDue <= readDue - 1;
      else if (readDue == 1) readDue <= 0;
    end
    // Present read data when due; a take clears it (a take and a new
    // presentation never coincide: one read outstanding per unit).
    if (readDue == 1) dataOut <= tagged Valid raw;
    else if (takeW) dataOut <= tagged Invalid;
  endrule

  method Bool free() = (busy == 0);
  method Action request(Bool write, UnitIndex idx, Word64 data, RetTag tag);
    reqW.wset(tuple4(write, idx, data, tag));
  endmethod
  method Bool dataReady() = isValid(dataOut);
  method RetTag dataTag() = tagReg;
  method ActionValue#(Word64) takeData();
    takeW.send();
    return validValue(dataOut);
  endmethod
endmodule

// ---------------------------------------------------------------------
// Memory bus control unit (single requester for now -- see header).
// ---------------------------------------------------------------------
interface MBCU;
  method Bool canAccept(WordAddr a);      // target unit free (nonexistent: always)
  method Action put(MemReq r);            // only when canAccept(r.addr)
  method Bool respReady(RetTag t);        // a response for tag t is waiting
  method ActionValue#(Word64) takeResp(RetTag t);
endinterface

module mkMBCU(MBCU);
  Vector#(NumUnits, MemoryUnit) units <- replicateM(mkMemoryUnit);
  // One response slot per return tag (a requester has at most one
  // read outstanding per tag). Reads of nonexistent addresses answer
  // 0 through the same slots.
  Vector#(NumTags, Reg#(Maybe#(Word64))) resp <- replicateM(mkReg(tagged Invalid));
  RWire#(MemReq) putW <- mkRWire;
  Vector#(NumTags, PulseWire) takeW <- replicateM(mkPulseWire);

  (* fire_when_enabled, no_implicit_conditions *)
  rule route;
    Vector#(NumTags, Maybe#(Word64)) r = readVReg(resp);
    for (Integer t = 0; t < valueOf(NumTags); t = t + 1)
      if (takeW[t]) r[t] = tagged Invalid;
    // Collect every unit presenting data this clock into its tag's slot.
    for (Integer i = 0; i < valueOf(NumUnits); i = i + 1)
      if (units[i].dataReady()) begin
        let d <- units[i].takeData();
        r[units[i].dataTag()] = tagged Valid d;
      end
    if (putW.wget matches tagged Valid .q) begin
      if (installed(q.addr))
        units[unitOf(q.addr)].request(q.write, indexOf(q.addr), q.data, q.tag);
      else if (!q.write)
        r[q.tag] = tagged Valid 0;
    end
    writeVReg(resp, r);
  endrule

  method Bool canAccept(WordAddr a);
    return !installed(a) || units[unitOf(a)].free();
  endmethod
  method Action put(MemReq r);
    putW.wset(r);
  endmethod
  method Bool respReady(RetTag t) = isValid(resp[t]);
  method ActionValue#(Word64) takeResp(RetTag t);
    takeW[t].send();
    return validValue(resp[t]);
  endmethod
endmodule

endpackage
