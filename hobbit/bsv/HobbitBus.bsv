// HobbitBus.bsv -- the ATT92010 synchronous bus face and the memory stub
// behind it.
//
// Evidence.  Every signal below is one of the pins printed in Figure 1-1
// (printed p. 1-2) and described in the December 1992 data sheet's Table 1
// (pin information, pp. 5-10), and every protocol rule is from Appendix A
// of the January 1993 Programmer's Reference Manual:
//
//   A.1  Bus Protocol          pp. A-1/A-2  BGRANT/BREQ/BGACK ownership,
//                                           the dead cycle between owners,
//                                           BREQ while an I/O transaction
//                                           is pending.
//   A.2  Surrendering the Bus  p. A-2      BGRANT deasserted: finish the
//                                           transaction, then drop BGACK.
//   A.3  Bus Transaction Types p. A-4      START begins, DTACK ends; BERR
//                                           or HRESET with DTACK ends in
//                                           error; LOCK through the write;
//                                           IOC[1:0] = 0 ends a block.
//   A.3.1 Read Transactions    p. A-4      text reads are double-word;
//                                           data reads are single/double/
//                                           quad; loopback when idle.
//   A.3.2 Write Transactions   p. A-4      single/double/quad.
//   A.3.3 Interlocked Transfer p. A-6      RMW, LOCK held through the write,
//                                           one dead cycle after it.
//   A.3.4 Block Data Transfer  p. A-6      double/quad; each beat is a
//                                           single-word transfer; HA[3:2]
//                                           increments and IOC[1:0]
//                                           decrements; retry resumes where
//                                           it was aborted.
//   A.4.1 Bus Retry            p. A-6      abort, mask DTACK, rerun after
//                                           RETRY deasserts.
//   A.4.2 Bus Error            p. A-6      BERR with DTACK ends the
//                                           transaction in error.
//   A.4.3 Reset                p. A-8      HRESET aborts the current cycle.
//
// Byte order is pp. 1-3/1-4: big-endian data numbers byte 0 as HD[31:24]
// (BE3), little-endian data numbers byte 0 as HD[7:0] (BE0), and text is
// always big-endian (p. 1-4 note).  The data sheet's Table 1 prints the
// byte-enable encoding (BE0 -> HD[7:0] ... BE3 -> HD[31:24]) and the
// byte/half replication on HD during sub-word writes.
//
// Model convention.  The pins are represented as positive-true booleans
// and a Bit#(4) byte-enable with 1 = enabled, although the physical pins
// are active-low; a comment at each field states the pin polarity.  The
// bus is synchronous and pipelined: a transaction's START/HA/BE are
// driven in one clock and its DTACK/data are returned in the next, so a
// new START may be asserted in the same clock that the previous
// transaction's DTACK arrives (Figure A-3, printed p. A-5, shows START in
// consecutive bus cycles 14 and 15).  That is what makes the core's A = 1
// choice (one 32-bit word per clock, HobbitTypes.bsv) true at the bus.
//
// The memory stub is a 256-word (1 Kbyte) array behind the bus.  The
// printed machine has no on-chip program memory (p. A-1); the stub is the
// board's memory for this model and the only thing the core can reach.
// Its `peek` method is a testbench probe, never used by the machine.
//
// The wrapper's `setHold`/`setBgrant`/`setRetry`/`setBerr`/`setWait`
// methods are the external devices and the central arbiter for the
// testbench; the core sees only the master interface.

package HobbitBus;

import Vector::*;
import FIFOF::*;
import RegFile::*;
import HobbitTypes::*;

// ---------------------------------------------------------------------
// Sizes and bursts.
// ---------------------------------------------------------------------
typedef enum { BUS_BYTE, BUS_HALF, BUS_WORD } BusSize deriving (Eq, Bits);

// A.3.4 (p. A-6): the supported block sizes are double- and quad-word.
// BUS_SINGLE is accepted by the interface for a one-beat block so the
// testbench can compare it with a plain single access.
typedef enum { BUS_SINGLE, BUS_DOUBLE, BUS_QUAD } BusBurst deriving (Eq, Bits);

function Bit#(3) burstBeats(BusBurst b);
  case (b)
    BUS_DOUBLE: return 3'd2;
    BUS_QUAD:   return 3'd4;
    default:    return 3'd1;
  endcase
endfunction

// IOC[1:0] is the number of words remaining minus one (A.3.4: the
// microprocessor decrements IOC[1:0] for each access and the transfer
// ends when IOC[1:0] = 0 with DTACK, p. A-4).  A double-word transfer
// therefore starts at 1 and a quad-word at 3; a single word is 0.
function Bit#(2) burstIoc(BusBurst b);
  case (b)
    BUS_DOUBLE: return 2'd1;
    BUS_QUAD:   return 2'd3;
    default:    return 2'd0;
  endcase
endfunction

// ---------------------------------------------------------------------
// Byte order and byte enables (pp. 1-3/1-4, data sheet Table 1 p. 10).
//
// The data sheet prints the physical lane assignment independent of
// endianness: BE0 marks HD[7:0], BE1 HD[15:8], BE2 HD[23:16], BE3
// HD[31:24].  Which byte *address* lands in which lane is the endianness
// choice: big-endian byte 0 is the most significant byte (HD[31:24]),
// little-endian byte 0 is the least significant (HD[7:0]).
// ---------------------------------------------------------------------
function Bit#(2) byteLane(Bit#(2) addrLow, Bool little);
  return little ? addrLow : (2'd3 - addrLow);
endfunction

function Bit#(4) beFor(Word addr, BusSize sz, Bool little);
  Bit#(2) a = addr[1:0];
  case (sz)
    BUS_BYTE: return 4'b0001 << byteLane(a, little);
    BUS_HALF: begin
      if (little)
        return (a[1] == 1'b0) ? 4'b0011 : 4'b1100;
      else
        return (a[1] == 1'b0) ? 4'b1100 : 4'b0011;
    end
    default: return 4'b1111;
  endcase
endfunction

// A.3 (p. A-4) and the data sheet p. 8: on byte writes the active byte is
// replicated on the inactive bytes of HD; on half-word writes the active
// half-word is replicated on the inactive half-word.
function Word replicateSub(Word data, BusSize sz);
  case (sz)
    BUS_BYTE: return {data[7:0], data[7:0], data[7:0], data[7:0]};
    BUS_HALF: return {data[15:0], data[15:0]};
    default:  return data;
  endcase
endfunction

// The read side of the same rule: the byte-strobes say which bytes of the
// fetched word the instruction will extract (p. 1-4).
function Word extractSub(Word word, Word addr, BusSize sz, Bool little);
  Bit#(2) a = addr[1:0];
  case (sz)
    BUS_BYTE: begin
      Bit#(2) lane = byteLane(a, little);
      Bit#(8) b = word[7:0];
      case (lane)
        2'd0: b = word[7:0];
        2'd1: b = word[15:8];
        2'd2: b = word[23:16];
        default: b = word[31:24];
      endcase
      return zeroExtend(b);
    end
    BUS_HALF: begin
      Bool high = little ? (a[1] == 1'b1) : (a[1] == 1'b0);
      return high ? zeroExtend(word[31:16]) : zeroExtend(word[15:0]);
    end
    default: return word;
  endcase
endfunction

// ---------------------------------------------------------------------
// The printed pins (Figure 1-1 p. 1-2; data sheet Table 1 pp. 5-10).
// ---------------------------------------------------------------------
typedef struct {
  Bool    start;    // START, active-low pin; True = asserted for one cycle
  Bool    read;     // RD, active-low; True = read
  Bool    dtri;     // D/T (DTRI): True = data, False = text (pin high for
                    // data, low for text, data sheet p. 10)
  Bool    ncache;   // NCACHE, active-low; True = asserted (not cacheable)
  Bool    lock;     // LOCK, active-low; True = asserted
  Bit#(2) ioc;      // IOC[1:0] word count remaining minus one
  Word    ha;       // HA[31:2], word address (low two bits zero)
  Bit#(4) be;       // BE[3:0], 1 = byte enabled (pin active-low)
  Word    hd;       // HD[31:0] write data (replicated per the data sheet)
  Bool    breq;     // BREQ, active-low; True = asserted
  Bool    bgack;    // BGACK, active-low; True = asserted
} BusPins deriving (Bits);

typedef struct {
  Bool dack;        // DTACK, active-low; True = asserted
  Bool berr;        // BERR, active-low; True = asserted
  Bool retry;       // RETRY, active-low; True = asserted
  Bool hold;        // HOLD, active-low; True = asserted
  Bool bgrant;      // BGRANT, active-low; True = asserted
  Word hd;          // HD[31:0] read data
} BusResp deriving (Bits);

function BusPins defaultBusPins();
  return BusPins { start: False, read: True, dtri: True, ncache: True,
                   lock: False, ioc: 0, ha: 0, be: 0, hd: 0,
                   breq: False, bgack: False };
endfunction

function BusResp defaultBusResp();
  return BusResp { dack: False, berr: False, retry: False,
                   hold: False, bgrant: True, hd: 0 };
endfunction

// ---------------------------------------------------------------------
// One bus transaction as the master issues it.
// ---------------------------------------------------------------------
typedef struct {
  Bool    read;
  Bool    text;     // True = text (D/T low)
  Word    addr;
  Bit#(4) be;
  Word    data;     // write data, already replicated for a sub-word
  Bit#(2) ioc;
  Bool    ncache;
  Bool    lock;
  Bool    blk;      // part of a double/quad block
  Bool    blkLast;  // last beat of the block (IOC = 0)
} BusTx deriving (Bits);

function BusTx defaultBusTx();
  return BusTx { read: True, text: False, addr: 0, be: 0, data: 0,
                 ioc: 0, ncache: True, lock: False, blk: False,
                 blkLast: True };
endfunction

function BusTx txFromPins(BusPins p);
  return BusTx { read: p.read, text: !p.dtri, addr: p.ha, be: p.be,
                 data: p.hd, ioc: p.ioc, ncache: p.ncache,
                 lock: p.lock, blk: False, blkLast: False };
endfunction

function BusPins pinsFromTx(BusTx t, Bool breq, Bool bgack);
  return BusPins { start: True, read: t.read, dtri: !t.text,
                   ncache: t.ncache, lock: t.lock, ioc: t.ioc,
                   ha: t.addr, be: t.be, hd: t.data,
                   breq: breq, bgack: bgack };
endfunction

// ---------------------------------------------------------------------
// Core-facing requests.  The core issues at most one read and one write
// in a clock; a read is issued immediately and a coincident write is
// queued (the stack cache can write a flushed word and request a refill
// word in the same clock).  Two reads in one clock are outside the
// contract: the prefetch fill runs only at boot, before the core starts,
// and the stack cache is the only reader afterwards.
// ---------------------------------------------------------------------
typedef struct { Word addr; BusSize size; } BusRead deriving (Bits);
typedef struct { Word addr; Word data; BusSize size; } BusWrite deriving (Bits);

function BusWrite defaultWrite();
  return BusWrite { addr: 0, data: 0, size: BUS_WORD };
endfunction
typedef struct {
  Word             addr;
  BusBurst         burst;
  Bool             text;
  Bool             write;
  Vector#(4, Word) data;
} BusBlockReq deriving (Bits);

function BusBlockReq defaultBlockReq();
  return BusBlockReq { addr: 0, burst: BUS_SINGLE, text: False,
                       write: False, data: replicate(0) };
endfunction

typedef struct {
  Bool             active;
  Word             addr;       // next beat's address
  Bit#(2)          ioc;        // next beat's IOC[1:0]
  Bit#(3)          remaining;  // beats left including the next one
  Bool             text;
  Bool             write;
  Vector#(4, Word) data;
  Bit#(3)          beat;       // next data index for a block write
} BusBlockState deriving (Bits);

function BusBlockState defaultBlockState();
  return BusBlockState { active: False, addr: 0, ioc: 0, remaining: 0,
                         text: False, write: False, data: replicate(0),
                         beat: 0 };
endfunction

// ---------------------------------------------------------------------
// The slave side: what the memory stub exposes to the master and to the
// testbench.
// ---------------------------------------------------------------------
interface HobbitBusSlave;
  method BusResp respond(BusPins p);
  method Action commit(BusPins p);
  method Bool hold();
  method Bool bgrant();
endinterface

// The core's memory port.  Single accesses are one-clock transactions:
// the master drives START/HA/BE/HD and the slave returns DTACK and HD in
// the same clock, and the master latches the word.  That is the zero-
// wait-state case of the printed protocol (Figures A-2/A-3, pp. A-3/A-5,
// show the address phase and the DTACK phase in consecutive bus cycles
// when the slave needs a clock); `setWait` inserts that wait state for the
// testbench.  Block moves are a registered engine, one beat per clock
// (A.3.4, p. A-6), because the master must hold the beat count across
// clocks.
interface HobbitBusMaster;
  method Action readDataWord(Word addr);
  method Action readSub(Word addr, BusSize sz);
  method Action readTextWord(Word addr, Bit#(2) ioc);
  method Action readTextLine(Word addr);
  method Action readBlock(Word addr, BusBurst burst, Bool text);
  method Action writeWord(Word addr, Word data);
  method Action writeSub(Word addr, Word data, BusSize sz);
  method Action writeBlock(Word addr, BusBurst burst,
                           Vector#(4, Word) data);

  method Word readData();       // single-access data
  method Word blockBeat();      // current block beat
  method Bool blockDone();
  method Bool blockBusy();

  method Action setEndian(Bool little);
  method Action setNcache(Bool asserted);
  method Action setLock(Bool asserted);
  method Action resetBus();

  method Bool busy();
  method Bool retried();
  method Bool busError();
  method Bool overrun();
  method Bool granted();
  method Bool breq();
  method Bool bgack();
  method BusPins pins();
  method BusPins writePins();
  method BusPins blockPins();
  method BusResp response();
  method BusResp writeResponse();
  method BusResp blockResponse();
endinterface

// ---------------------------------------------------------------------
// Memory stub.
// ---------------------------------------------------------------------
interface HobbitBusMemStub;
  interface HobbitBusSlave busSlave;
  method Word peek(Word addr);
  method Action setRetry(Bool v);
  method Action setBerr(Bool v);
  method Action setWait(Bool v);
  method Bool retryInjected();
  method Bool berrInjected();
  method Bool waitInjected();
endinterface

module mkHobbitBusMemStub#(Reg#(Bool) holdR, Reg#(Bool) bgrantR)
                          (HobbitBusMemStub);
  // 256 words = 1 Kbyte.  The smoke image, its data and its stack all fit
  // below 0x400; the 256-bit written mask is the size the old memory used
  // (docs/area_analysis.md, "Program memory").  One write port, one
  // combinational read, one `upd` call site.
  RegFile#(Bit#(8), Word) m <- mkRegFileFull;
  Reg#(Bit#(256)) written <- mkReg(0);
  Reg#(Bool) retryR <- mkReg(False);
  Reg#(Bool) berrR <- mkReg(False);
  Reg#(Bool) waitR <- mkReg(False);

  function Bit#(8) idx(Word a) = truncate(a >> 2);

  function Word readWord(Word a);
    let i = idx(a);
    return (written[i] == 1'b1) ? m.sub(i) : 32'd0;
  endfunction

  function Word mergeBytes(Word old, Word d, Bit#(4) be);
    Word r = old;
    for (Integer i = 0; i < 4; i = i + 1) begin
      if (be[i] == 1'b1) begin
        Bit#(8) b = truncate(d >> (8 * i));
        Word mask = 32'h000000FF << (8 * i);
        r = (r & ~mask) | (zeroExtend(b) << (8 * i));
      end
    end
    return r;
  endfunction

  // The response is combinational in the pins the master presents this
  // clock.  DTACK is asserted for a START that the slave can complete;
  // RETRY masks DTACK (A.4.1, p. A-6) and BERR is asserted with DTACK
  // (A.4.2, p. A-6).  A testbench-injected wait state holds DTACK low,
  // which is the printed address-phase/data-phase split.
  function BusResp respondF(BusPins p);
    Bool done = p.start && !waitR;
    return BusResp { dack:  done && !retryR && !berrR,
                     berr:  done && berrR,
                     retry: done && retryR,
                     hold:  holdR,
                     bgrant: bgrantR,
                     hd:    (p.start && p.read) ? readWord(p.ha) : 32'd0 };
  endfunction

  method Word peek(Word a) = readWord(a);
  method Action setRetry(Bool v);
    retryR <= v;
  endmethod
  method Action setBerr(Bool v);
    berrR <= v;
  endmethod
  method Action setWait(Bool v);
    waitR <= v;
  endmethod
  method Bool retryInjected() = retryR;
  method Bool berrInjected() = berrR;
  method Bool waitInjected() = waitR;

  interface HobbitBusSlave busSlave;
    method BusResp respond(BusPins p) = respondF(p);
    method Action commit(BusPins p);
      if (p.start && !p.read && !retryR && !berrR && !waitR) begin
        Word merged = mergeBytes(readWord(p.ha), p.hd, p.be);
        m.upd(idx(p.ha), merged);
        written <= written | (256'd1 << idx(p.ha));
      end
    endmethod
    method Bool hold() = holdR;
    method Bool bgrant() = bgrantR;
  endinterface
endmodule

// ---------------------------------------------------------------------
// Bus master.
// ---------------------------------------------------------------------
module mkHobbitBusMaster#(HobbitBusSlave slave)(HobbitBusMaster);
  // structure follows Flute (Bluespec, Inc., Apache-2.0) -- see
  // docs/bluespec_architecture.md: a box with a registered boundary, one
  // rule for the multi-cycle block engine, no logic inlined into a stage.

  Reg#(Word) rdDataR <- mkReg(0);
  Reg#(BusPins) rdPinsR <- mkReg(defaultBusPins());
  Reg#(BusResp) rdRespR <- mkReg(defaultBusResp());

  // A write's result is separate from a read's: the stack cache can issue
  // a flush write and a refill read in the same clock.
  Reg#(BusPins) wrPinsR <- mkReg(defaultBusPins());
  Reg#(BusResp) wrRespR <- mkReg(defaultBusResp());

  // Block engine: a request register with a sequence number, so the
  // caller writes only the request and the engine only its own state.
  Reg#(Maybe#(BusBlockReq)) blkReqR <- mkReg(tagged Invalid);
  Reg#(Bit#(8)) blkSeqR <- mkReg(0);
  Reg#(Bit#(8)) blkSeenR <- mkReg(0);
  Reg#(BusBlockState) blkR <- mkReg(defaultBlockState());
  Reg#(Bool) blkActiveR <- mkReg(False);
  Reg#(Bool) blkDoneR <- mkReg(False);
  Reg#(Word) blkDataR <- mkReg(0);
  Reg#(BusPins) blkPinsR <- mkReg(defaultBusPins());
  Reg#(BusResp) blkRespR <- mkReg(defaultBusResp());
  Reg#(Bool) overrunR <- mkReg(False);

  // Configuration and ownership.  The setters write these directly; no
  // separate status rule can be starved by a caller that fires often.
  Reg#(Bool) bgackR <- mkReg(True);
  Reg#(Bool) endianR <- mkReg(False);     // big-endian, p. 1-4
  Reg#(Bool) ncacheR <- mkReg(True);      // physical addressing, p. 1-9
  Reg#(Bool) lockR <- mkReg(False);

  function Bool newBlkReq() =
    isValid(blkReqR) && (blkSeqR != blkSeenR);

  // ---- pin builders ------------------------------------------------
  function BusPins pinsRead(Word addr, BusSize sz, Bool text, Bit#(2) ioc,
                            Bool blk, Bool blkLast);
    Bool ok = !slave.hold() && slave.bgrant() && !blkActiveR;
    return BusPins { start: ok, read: True, dtri: !text,
                     ncache: ncacheR, lock: lockR, ioc: ioc, ha: addr,
                     be: beFor(addr, sz, endianR), hd: 0,
                     breq: !slave.bgrant(), bgack: bgackR };
  endfunction

  function BusPins pinsWrite(Word addr, Word data, BusSize sz);
    Bool ok = !slave.hold() && slave.bgrant() && !blkActiveR;
    return BusPins { start: ok, read: False, dtri: True,
                     ncache: ncacheR, lock: lockR, ioc: 0, ha: addr,
                     be: beFor(addr, sz, endianR),
                     hd: replicateSub(data, sz),
                     breq: !slave.bgrant(), bgack: bgackR };
  endfunction

  function BusPins pinsBlock(Word addr, Bool write, Bool text, Bit#(2) ioc,
                             Bool blkLast, Word data);
    Bool ok = !slave.hold() && slave.bgrant();
    return BusPins { start: ok, read: !write, dtri: !text,
                     ncache: ncacheR, lock: lockR, ioc: ioc, ha: addr,
                     be: 4'hF, hd: write ? data : 0,
                     breq: !slave.bgrant(), bgack: True };
  endfunction

  // A.1/A.2 pp. A-1/A-2: BGACK follows BGRANT; a block in progress
  // finishes before ownership is relinquished.
  rule arb;
    if (slave.bgrant()) bgackR <= True;
    else bgackR <= False;
  endrule

  // A.3.4 (p. A-6): each beat is a single-word transfer, HA[3:2]
  // increments, IOC[1:0] decrements, and the transfer ends when IOC = 0
  // with DTACK.  HOLD suspends further beats.
  rule blockStep (newBlkReq() || blkActiveR);
    Bool canStart = !slave.hold() && slave.bgrant();
    if (canStart) begin
      if (!blkActiveR && newBlkReq()) begin
        BusBlockReq b = validValue(blkReqR);
        Bit#(3) beats = burstBeats(b.burst);
        Word d = b.write ? b.data[0] : 0;
        BusPins p = pinsBlock(b.addr, b.write, b.text,
                              burstIoc(b.burst), (beats == 1), d);
        BusResp r = slave.respond(p);
        if (b.write) slave.commit(p);
        blkPinsR <= p;
        blkRespR <= r;
        blkDataR <= r.hd;
        blkDoneR <= (beats == 1);
        blkSeenR <= blkSeqR;
        if (beats > 1) begin
          blkR <= BusBlockState { active: True, addr: b.addr + 4,
                                  ioc: truncate(beats - 2),
                                  remaining: beats - 1,
                                  text: b.text, write: b.write,
                                  data: b.data, beat: 1 };
          blkActiveR <= True;
        end else begin
          blkR <= defaultBlockState();
          blkActiveR <= False;
        end
      end else begin
        Bit#(3) rem = blkR.remaining;
        Word d = blkR.write ? blkR.data[blkR.beat] : 0;
        BusPins p = pinsBlock(blkR.addr, blkR.write, blkR.text,
                              blkR.ioc, (rem == 1), d);
        BusResp r = slave.respond(p);
        if (blkR.write) slave.commit(p);
        blkPinsR <= p;
        blkRespR <= r;
        blkDataR <= r.hd;
        blkDoneR <= (rem == 1);
        if (rem > 1) begin
          blkR <= BusBlockState { active: True, addr: blkR.addr + 4,
                                  ioc: blkR.ioc - 1,
                                  remaining: rem - 1,
                                  text: blkR.text, write: blkR.write,
                                  data: blkR.data, beat: blkR.beat + 1 };
          blkActiveR <= True;
        end else begin
          blkR <= defaultBlockState();
          blkActiveR <= False;
        end
      end
    end
    if (newBlkReq() && blkActiveR) overrunR <= True;
  endrule

  // ---- single accesses ---------------------------------------------
  method Action readDataWord(Word addr);
    BusPins p = pinsRead(addr, BUS_WORD, False, 0, False, True);
    BusResp r = slave.respond(p);
    rdPinsR <= p;
    rdRespR <= r;
    if (r.dack) rdDataR <= r.hd;
  endmethod

  method Action readSub(Word addr, BusSize sz);
    BusPins p = pinsRead(addr, sz, False, 0, False, True);
    BusResp r = slave.respond(p);
    rdPinsR <= p;
    rdRespR <= r;
    if (r.dack) rdDataR <= r.hd;
  endmethod

  // A.3.1 p. A-4: a text read is a word transfer with D/T low and the
  // IOC[1:0] beat count of the double-word text read it belongs to.
  // Figure A-2 (p. A-3) shows START at bus cycles 11 and 15 with IOC = 1
  // then 0.  The core's prefetch uses this per-beat form.
  method Action readTextWord(Word addr, Bit#(2) ioc);
    BusPins p = pinsRead(addr, BUS_WORD, True, ioc, False, True);
    BusResp r = slave.respond(p);
    rdPinsR <= p;
    rdRespR <= r;
    if (r.dack) rdDataR <= r.hd;
  endmethod

  method Action writeWord(Word addr, Word data);
    BusPins p = pinsWrite(addr, data, BUS_WORD);
    BusResp r = slave.respond(p);
    slave.commit(p);
    wrPinsR <= p;
    wrRespR <= r;
  endmethod

  method Action writeSub(Word addr, Word data, BusSize sz);
    BusPins p = pinsWrite(addr, data, sz);
    BusResp r = slave.respond(p);
    slave.commit(p);
    wrPinsR <= p;
    wrRespR <= r;
  endmethod

  // ---- block requests ----------------------------------------------
  method Action readTextLine(Word addr);
    blkReqR <= tagged Valid (BusBlockReq { addr: addr, burst: BUS_DOUBLE,
                                           text: True, write: False,
                                           data: replicate(0) });
    blkSeqR <= blkSeqR + 1;
  endmethod

  method Action readBlock(Word addr, BusBurst burst, Bool text);
    blkReqR <= tagged Valid (BusBlockReq { addr: addr, burst: burst,
                                           text: text, write: False,
                                           data: replicate(0) });
    blkSeqR <= blkSeqR + 1;
  endmethod

  method Action writeBlock(Word addr, BusBurst burst,
                           Vector#(4, Word) data);
    blkReqR <= tagged Valid (BusBlockReq { addr: addr, burst: burst,
                                           text: False, write: True,
                                           data: data });
    blkSeqR <= blkSeqR + 1;
  endmethod

  // ---- methods -----------------------------------------------------
  method Word readData() = rdDataR;
  method Word blockBeat() = blkDataR;
  method Bool blockDone() = blkDoneR;
  method Bool blockBusy() = blkActiveR || newBlkReq();

  method Action setEndian(Bool little);
    endianR <= little;
  endmethod
  method Action setNcache(Bool asserted);
    ncacheR <= asserted;
  endmethod
  method Action setLock(Bool asserted);
    lockR <= asserted;
  endmethod
  method Action resetBus();
    endianR <= False;
    ncacheR <= True;
    lockR <= False;
  endmethod

  method Bool busy() =
    blkActiveR || newBlkReq() || rdPinsR.start || wrPinsR.start;
  method Bool retried() =
    rdRespR.retry || wrRespR.retry || blkRespR.retry;
  method Bool busError() =
    rdRespR.berr || wrRespR.berr || blkRespR.berr;
  method Bool overrun() = overrunR;
  method Bool granted() = bgackR;
  method Bool breq() =
    rdPinsR.breq || wrPinsR.breq || blkActiveR || newBlkReq();
  method Bool bgack() = bgackR;
  method BusPins pins() = blkActiveR ? blkPinsR : rdPinsR;
  method BusPins writePins() = wrPinsR;
  method BusPins blockPins() = blkPinsR;
  method BusResp response() = rdRespR;
  method BusResp writeResponse() = wrRespR;
  method BusResp blockResponse() = blkRespR;
endmodule

// ---------------------------------------------------------------------
// The core-facing memory: master + stub + the arbiter/device controls.
// ---------------------------------------------------------------------
interface HobbitBusMem;
  interface HobbitBusMaster master;
  method Word peek(Word addr);
  method BusPins pins();
  method BusPins writePins();
  method BusPins blockPins();
  method BusResp response();
  method BusResp writeResponse();
  method BusResp blockResponse();
  method Action setHold(Bool v);
  method Action setBgrant(Bool v);
  method Action setRetry(Bool v);
  method Action setBerr(Bool v);
  method Action setWait(Bool v);
  method Bool retried();
  method Bool busError();
  method Bool overrun();
  method Bool granted();
  method Bool breq();
  method Bool bgack();
  method Bool start();
  method Bool read();
  method Bool dtri();
  method Bool ncache();
  method Bool lock();
  method Bit#(2) ioc();
  method Word ha();
  method Bit#(4) be();
  method Word hd();
endinterface

module mkHobbitBusMem(HobbitBusMem);
  Reg#(Bool) holdR <- mkReg(False);
  Reg#(Bool) bgrantR <- mkReg(True);       // the central arbiter grants us

  HobbitBusMemStub stub <- mkHobbitBusMemStub(holdR, bgrantR);
  HobbitBusMaster mst <- mkHobbitBusMaster(stub.busSlave);

  method Word peek(Word addr) = stub.peek(addr);
  method BusPins pins() = mst.pins();
  method BusPins writePins() = mst.writePins();
  method BusPins blockPins() = mst.blockPins();
  method BusResp response() = mst.response();
  method BusResp writeResponse() = mst.writeResponse();
  method BusResp blockResponse() = mst.blockResponse();
  method Action setHold(Bool v);
    holdR <= v;
  endmethod
  method Action setBgrant(Bool v);
    bgrantR <= v;
  endmethod
  method Action setRetry(Bool v);
    stub.setRetry(v);
  endmethod
  method Action setBerr(Bool v);
    stub.setBerr(v);
  endmethod
  method Action setWait(Bool v);
    stub.setWait(v);
  endmethod
  method Bool retried() = mst.retried();
  method Bool busError() = mst.busError();
  method Bool overrun() = mst.overrun();
  method Bool granted() = mst.granted();
  method Bool breq() = mst.breq();
  method Bool bgack() = mst.bgack();
  method Bool start() = mst.pins().start;
  method Bool read() = mst.pins().read;
  method Bool dtri() = mst.pins().dtri;
  method Bool ncache() = mst.pins().ncache;
  method Bool lock() = mst.pins().lock;
  method Bit#(2) ioc() = mst.pins().ioc;
  method Word ha() = mst.pins().ha;
  method Bit#(4) be() = mst.pins().be;
  method Word hd() = mst.pins().hd;

  interface HobbitBusMaster master = mst;
endmodule

// ---------------------------------------------------------------------
// HobbitMem adapter: the core's existing word interface, implemented
// over the bus master.  The core, the MMU faces and the stack cache keep
// their HobbitMem ports; this adapter is the only implementation the
// harnesses hand them, so every access goes over the Appendix A bus.
// readReq/readData keep the one-clock latency the core's A = 1 timing
// assumes; write commits in the same clock; peek is the testbench probe.
// ---------------------------------------------------------------------
module mkHobbitMemBus#(HobbitBusMem mem)(HobbitMem);
  method Action readReq(Word a);
    mem.master.readDataWord(a);
  endmethod
  method Word readData() = mem.master.readData();
  method Action write(Word a, Word v);
    mem.master.writeWord(a, v);
  endmethod
  method Word peek(Word a) = mem.peek(a);
endmodule

endpackage
