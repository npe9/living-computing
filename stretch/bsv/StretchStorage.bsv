// StretchStorage.bsv
//
// Unified word-addressed storage: ordinary core memory AND the CPU
// registers live in the same address space, because on the 7030 they
// really do (IBM 7030 Reference Card, "SPECIAL STORAGE ASSIGNMENT"
// table; see addrZero..addrIndexBase in StretchTypes.bsv). There is no
// separate register file beside memory -- a program reaches the
// accumulator or an index register by loading/storing address 8, 9, or
// 16+j, exactly as it reaches any other word.
//
// General core storage (addresses 32 and up) lives in the memory units
// behind the memory bus control unit (StretchMemory.bsv: six 16K-word
// units, 2.1 us cycle, interleaved -- docs/microarchitecture_plan.md
// stage 1). This module is the CPU's side of that bus: it keeps the
// core's stores in a small in-order queue and issues them, issues one
// outstanding read at a time after any queued stores (so a program's
// own store-then-load ordering holds without the look-ahead's LAAR
// forwarding, which comes in stage 3), and presents the read response
// through an explicit handshake -- `responseReady()` is a plain value
// method the caller polls, and `readWordResp()` consumes the response.
// Reads take a variable number of clocks (the target unit's read-out
// time plus any wait for a busy unit); callers must NOT assume any
// fixed latency, which is exactly the assumption the previous BRAM
// version baked in (a DWire that held the answer for one cycle).
// Addresses 0-31 stay a Vector of plain registers: the Special Storage
// Assignment table (p.111, "does not include internal computer
// registers and index registers") makes this an architectural
// boundary, not just a simulation convenience (on the real machine they
// are index storage and internal transistor registers, Blosk TR00.722
// p.19), and it lets `readAccLeft`/`readAccRight` (addresses 8/9) stay
// always-instant value methods rather than paying a bus round trip.
// A read of a special address answers on the next clock.
//
// Every earlier design note about the BRAM latency-1 backing, its
// implicit-condition hang and its DWire trade-off is preserved in git
// history and docs/phase2_arm_inventory.md; the request/response
// calling convention those steps introduced is what made this change
// local to this file plus three `responseReady()` guards in
// StretchCore.bsv.

package StretchStorage;

import Vector::*;
import FIFOF::*;
import StretchTypes::*;
import StretchMemory::*;

// The 18-bit address space is what the types model; what is installed
// is StretchMemory's InstalledWords (six units). Kept as a name so the
// reasoning in older comments still reads.
typedef InstalledWords MemWords;

interface StretchStorage;
  // Read a full 64-bit word, request/response style: issue the
  // request with readWordReq in one rule; on any LATER clock at which
  // responseReady() is true, collect it with readWordResp (which
  // consumes it). One read outstanding at a time. The latency is
  // variable -- next clock for a special (register-backed) address,
  // several clocks for core storage, more if the target memory unit
  // is busy -- so callers poll responseReady() and stall until it is
  // true; they must never assume a fixed count of cycles.
  method Bool responseReady();
  method Action readWordReq(WordAddr a);
  method ActionValue#(Word64) readWordResp();

  // Write a full 64-bit word. Read-only/protected addresses silently
  // ignore the write (this models "permanently protected" locations;
  // it does not yet raise the protection-violation interrupt -- out of
  // scope, see README). A special address is written on the spot; a
  // core-storage write is queued (in order, ahead of any later read)
  // and issued to the bus when its unit is free. writeReady() is
  // false when the queue is full; a caller that ignores it and writes
  // anyway loses the word (reported with $display).
  method Bool writeReady();
  method Action writeWord(WordAddr a, Word64 v);

  // Indicators: read the current 64-bit indicator word, or replace it
  // wholesale. An instruction that changes several indicator bits must
  // compute the combined new value itself (see StretchExecute.bsv's
  // `Ind` helpers) and call setIndicatorBits exactly once -- calling it
  // (or any single-bit variant) more than once per rule is a
  // write/write conflict on the underlying register. See file header.
  method Word64 readIndicators();
  method Action setIndicatorBits(Word64 v);

  method IndexWord readIndex(Bit#(4) j);
  method Action writeIndex(Bit#(4) j, IndexWord v);

  // Dedicated accumulator accessors: addrAccLeft/addrAccRight (8, 9)
  // are compile-time CONSTANTS baked into readAcc/writeAcc
  // (StretchExecute.bsv), never a runtime-computed effective address,
  // so there is no ambiguity to route through the general
  // request/response path above and make nearly every VflInt and
  // Connective arm pay for a round trip it doesn't need. These two
  // addresses are always Reg-backed and always will be (0-31 never
  // moves to BRAM, see file header).
  method Word64 readAccLeft();
  method Word64 readAccRight();
endinterface

// mkStretchStorage: the CPU's view of storage. Addresses 0-31 are
// intercepted below per the Special Storage Assignment table; 32 and
// up go to the memory units behind the MBCU (StretchMemory.bsv) --
// see file header.
module mkStretchStorage(StretchStorage);

  // The memory bus and units (StretchMemory.bsv), and this module's
  // request bookkeeping: an in-order store queue, one outstanding
  // read, and the collected response.
  MBCU mbcu <- mkMBCU;
  FIFOF#(MemReq) storeQ <- mkUGSizedFIFOF(8); // unguarded: memCtl checks
                                              // notFull/notEmpty itself, so no
                                              // implicit condition is hoisted into it
  Reg#(Maybe#(WordAddr)) pendingRead <- mkReg(tagged Invalid);
  Reg#(Bool)             readIssued  <- mkReg(False);
  Reg#(Maybe#(Word64))   resp        <- mkReg(tagged Invalid);
  RWire#(WordAddr) reqW   <- mkRWire;   // readWordReq this clock
  RWire#(MemReq)   storeW <- mkRWire;   // writeWord (core storage) this clock
  PulseWire        takeW  <- mkPulseWire; // readWordResp this clock
  function Bool memInRange(WordAddr a) = installed(a);
  function Bool isSpecialAddr(WordAddr a) = (a < 32);

  // Named CPU registers backing addresses 0-31.
  Reg#(Word64) intervalTimerAndClock <- mkReg(0); // addr 1: bits 0-18 timer, 28-63 clock
  Reg#(Word64) interruptionAddress   <- mkReg(0); // addr 2
  Reg#(Word64) boundaryReg           <- mkReg(0); // addr 3
  Reg#(Word64) maintenanceBits       <- mkReg(0); // addr 4
  Reg#(Word64) channelAddress        <- mkReg(0); // addr 5
  Reg#(Word64) otherCpuBits          <- mkReg(0); // addr 6
  Reg#(Word64) zerosOnesCounts       <- mkReg(0); // addr 7
  Reg#(Word64) accLeft               <- mkReg(0); // addr 8
  Reg#(Word64) accRight              <- mkReg(0); // addr 9
  Reg#(Word64) accSignByte           <- mkReg(0); // addr 10 (bits 0-7 only)
  Reg#(Word64) indicators            <- mkReg(0); // addr 11
  Reg#(Word64) mask                  <- mkReg(64'hFFFF_0000_0000_0000); // addr 12: bits0-19=1,48-63=0
  Reg#(Word64) remainder             <- mkReg(0); // addr 13
  Reg#(Word64) factor                <- mkReg(0); // addr 14
  Reg#(Word64) transit                <- mkReg(0); // addr 15
  Vector#(16, Reg#(Word64)) xreg      <- replicateM(mkReg(0)); // addr 16-31

  // A read of a special (register-backed) address is answered from
  // live register state on the next clock, without touching the bus.
  Reg#(Maybe#(WordAddr)) pendingSpecial <- mkReg(tagged Invalid);

  // The one rule that moves requests to the bus and responses back.
  // Every register it writes is written nowhere else; the methods
  // communicate with it through the wires above, so a method call
  // and this rule never race on a register.
  (* fire_when_enabled, no_implicit_conditions *)
  rule memCtl;
    // Stores: enqueue this clock's store (if any); issue the oldest
    // queued store when its unit is free. Reads are only issued once
    // the store queue is empty, which keeps store->load ordering.
    if (storeW.wget matches tagged Valid .r) begin
      if (storeQ.notFull) storeQ.enq(r);
      else $display("StretchStorage: store queue full, write to %0d LOST", r.addr);
    end
    Bool issuedStore = False;
    if (storeQ.notEmpty && mbcu.canAccept(storeQ.first.addr)) begin
      mbcu.put(storeQ.first);
      storeQ.deq;
      issuedStore = True;
    end
    // Reads.
    Maybe#(WordAddr) pr = pendingRead;
    Bool issued = readIssued;
    Maybe#(Word64) rs = resp;
    if (takeW) rs = tagged Invalid;
    if (mbcu.respReady()) begin
      let v <- mbcu.takeResp();
      rs = tagged Valid v;
      pr = tagged Invalid;
      issued = False;
    end
    if (!issuedStore && !storeQ.notEmpty && !issued) begin
      if (pr matches tagged Valid .a &&& mbcu.canAccept(a)) begin
        mbcu.put(MemReq{ write: False, addr: a, data: 0 });
        issued = True;
      end
    end
    Maybe#(WordAddr) ps = pendingSpecial;
    if (takeW) ps = tagged Invalid;
    if (reqW.wget matches tagged Valid .a) begin
      if (isSpecialAddr(a))
        ps = tagged Valid a;
      else begin
        pr = tagged Valid a;
        issued = False;
      end
    end
    pendingRead <= pr;
    readIssued  <= issued;
    resp        <= rs;
    pendingSpecial <= ps;
  endrule

  // Special-register lookup, used only by readWordResp when the
  // pending request named a special address. Every address 0-31 is
  // covered by one of the named-case arms or the xreg range below --
  // the `default` arm's fallback to 0 is reached only for an address
  // readWordReq classified as "special" because it was beyond
  // MemWords (out of the simulated core's range), never for a true
  // address 0-31.
  function Word64 lookupSpecial(WordAddr a);
    case (a)
      addrZero: return 0; // permanently protected zero, p. "SPECIAL STORAGE ASSIGNMENT"
      1: return intervalTimerAndClock;
      2: return interruptionAddress;
      3: return boundaryReg;
      4: return maintenanceBits;
      5: return channelAddress;
      6: return otherCpuBits;
      7: return zerosOnesCounts;
      8: return accLeft;
      9: return accRight;
      10: return accSignByte;
      11: return indicators;
      12: return mask;
      13: return remainder;
      14: return factor;
      15: return transit;
      default:
        if (a >= addrIndexBase && a < addrIndexBase + 16)
          return xreg[a - addrIndexBase];
        else
          return 0; // unreachable: only addresses 0-31 are routed here
    endcase
  endfunction

  method Bool responseReady();
    return isValid(pendingSpecial) || isValid(resp);
  endmethod

  method Action readWordReq(WordAddr a);
    reqW.wset(a);
  endmethod

  method ActionValue#(Word64) readWordResp();
    takeW.send();
    if (pendingSpecial matches tagged Valid .a)
      return lookupSpecial(a);
    else
      return validValue(resp);
  endmethod

  method Bool writeReady();
    return storeQ.notFull;
  endmethod

  method Action writeWord(WordAddr a, Word64 v);
    case (a)
      addrZero: noAction; // writes to Zero are discarded (permanently protected)
      1: intervalTimerAndClock <= v; // simplification: full word writable; real HW
                                      // splits timer(read/write except store-type ops)
                                      // vs clock(read-only) -- see README "Scope".
      2: interruptionAddress <= v;   // permanently protected on real HW; not enforced
      3: boundaryReg <= v;           // permanently protected on real HW; not enforced
      4: maintenanceBits <= v;
      5: noAction; // Channel Address is read-only ("b" footnote)
      6: otherCpuBits <= v;
      7: zerosOnesCounts <= v;
      8: accLeft <= v;
      9: accRight <= v;
      10: accSignByte <= {56'b0, v[7:0]};
      // SIMPLIFICATION: real hardware lets a generic STORE-type
      // instruction write indicator bits 20-63 directly (Reference
      // Card footnote c: only bits 0-19 are read-only). This
      // implementation treats word 11 as fully read-only via ordinary
      // memory stores instead, because the execute stage separately
      // writes `indicators` exactly once per instruction from its own
      // side effects (setIndicatorBits, see StretchExecute.bsv) and a
      // plain register cannot accept two independent writes in the
      // same rule. Indicators remain fully readable and are still set
      // by every instruction that defines them -- only the "poke via
      // STORE" path is unavailable. See bsv/README.md "Scope".
      11: noAction;
      12: mask <= {16'hFFFF, v[47:16], 16'h0000};     // bits0-19=1, 48-63=0 always
      13: remainder <= v;
      14: factor <= v;
      15: transit <= v;
      default:
        if (a >= addrIndexBase && a < addrIndexBase + 16)
          xreg[a - addrIndexBase] <= v;
        else
          storeW.wset(MemReq{ write: True, addr: a, data: v }); // nonexistent
                                                                // addresses are
                                                                // dropped by the MBCU
    endcase
  endmethod

  // Indicators are read/written as a single combined value per
  // instruction (see bsv/README.md "Toolchain": a plain Reg can only
  // take one `<=` per rule, so an instruction that touches several
  // indicator bits -- e.g. RLZ/RZ/RGZ/RN together -- must compute them
  // all as one Bit#(64) and write once via setIndicatorBits, not via
  // repeated single-bit set calls).
  method Word64 readIndicators();
    return indicators;
  endmethod

  method Action setIndicatorBits(Word64 v);
    indicators <= v;
  endmethod

  method IndexWord readIndex(Bit#(4) j);
    return unpackIndexWord(xreg[j]);
  endmethod

  method Action writeIndex(Bit#(4) j, IndexWord v);
    xreg[j] <= packIndexWord(v);
  endmethod

  method Word64 readAccLeft();
    return accLeft;
  endmethod

  method Word64 readAccRight();
    return accRight;
  endmethod

endmodule

endpackage
