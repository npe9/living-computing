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

  // Instruction-fetch channels for the instruction unit's 1Y/2Y
  // buffers (y = 0 or 1): the same request/ready/response protocol as
  // the operand channel, independent of it, lower bus priority.
  method Action fetchReq(Bit#(1) y, WordAddr a);
  method Bool fetchReady(Bit#(1) y);
  method ActionValue#(Word64) fetchResp(Bit#(1) y);
  // The core-storage word stored on the previous clock, if any: the
  // instruction unit compares it with its prefetched words (program
  // store compare) and invalidates a match.
  method Maybe#(WordAddr) recentStore();
  // Look-ahead level channels (stage 3): one outstanding operand
  // fetch per level, return tags 3-6, priority above the Y buffers
  // (Buchholz §14.3: the look-ahead over the instruction fetch).
  method Action laReq(Bit#(2) lvl, WordAddr a);
  method Bool laReady(Bit#(2) lvl);
  method ActionValue#(Word64) laResp(Bit#(2) lvl);

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

  // THE INTERRUPT-SYSTEM ENABLE BIT.  One flip-flop, no nesting:
  // BRANCH ENABLED sets it, BRANCH DISABLED clears it, BRANCH ENABLED
  // AND WAIT sets it, and all three act UNCONDITIONALLY and BEFORE the
  // branch (p.40).  Reset state is DISABLED (p.53, for both IPL and
  // initial power-on).
  //
  // Nothing else of the interrupt system exists yet.  The bit is here
  // because STORAGE PROTECTION is gated on it -- p.45's DS/DF/IF
  // definitions each say "while the interruption system was enabled"
  // -- and protection is the smallest piece of the interrupt system
  // observable without the interruption mechanism itself.
  //
  // A plain Reg read, deliberately: the execute stage decides
  // protection on its own side (see protViolates there) rather than
  // storage reporting a suppression back across the module boundary.
  // The reporting version does not schedule -- bsc lifts the wire's
  // read into the rule predicate, which then conflicts with the same
  // rule writing it.
  method Bool irqEnabled();
  method Action setIrqEnabled(Bool e);

  // THE ADDRESS BOUNDARY REGISTERS, word 3, read as one word.  p.31:
  // "The upper boundary and lower boundary registers are located in
  // bits 0-17 and 32-49, respectively, of storage location 3", and
  // "the boundary control bit, bit 57 of storage location 3,
  // determines which condition will cause an address monitoring
  // signal."  The fields are pulled apart on the EXECUTE side, in
  // protViolates, for the same scheduling reason irqEnabled is a plain
  // Reg read: a readWord() in a rule that also writes storage is the
  // G0004 conflict that killed the first design.
  method Word64 readBoundaries();

  method IndexWord readIndex(Bit#(4) j);
  method Action writeIndex(Bit#(4) j, IndexWord v);
  // All sixteen index words at once: the instruction unit snapshots
  // them when it guesses a branch and restores them on a wrong guess
  // (standing for the look-ahead's index-recovery levels, plan §6d).
  method Vector#(16, Word64) snapshotIndex();
  method Action restoreIndex(Vector#(16, Word64) v);

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
  method Word64 readAccSign();   // address 10, the accumulator sign byte register
  // Address 14, the factor register. MULTIPLY AND ADD reads it as its
  // multiplicand (Ref. Manual p.98) and needs it in the same cycle it
  // executes, exactly as it needs the accumulator, so it gets the same
  // combinational treatment. Word 14 is Reg-backed for the same reason
  // 8-10 are: 0-31 never move to BRAM.
  method Word64 readFactor();
  // Address 7, the zeros/ones counts.  DIVIDE writes the left zeros
  // count into IBM bits 17-23 and must not disturb the all-ones count
  // at 44-50, so the arm needs to read the word first.
  method Word64 readZerosOnesCounts();
endinterface

// mkStretchStorage: the CPU's view of storage. Addresses 0-31 are
// intercepted below per the Special Storage Assignment table; 32 and
// up go to the memory units behind the MBCU (StretchMemory.bsv) --
// see file header.
module mkStretchStorage(StretchStorage);

  // The memory bus and units (StretchMemory.bsv), and this module's
  // request bookkeeping. Seven read channels, one per return tag:
  // 0 = the operand channel (execute()'s follow-up reads and the
  // testbenches'), 1 = 1Y, 2 = 2Y (the instruction unit's buffers),
  // 3-6 = look-ahead levels 1-4. Each channel has at most one read
  // outstanding; the bus is offered requests in the order stores,
  // operand read, look-ahead levels, 1Y, 2Y (Buchholz §14.3: the
  // look-ahead has priority over the instruction fetch).
  // A special (register-backed) address answers on the next clock on
  // any channel. Reads on every channel are issued only while the
  // store queue is empty: store->load ordering for operands, and a
  // conservative form of the program-store compare (Blosk p.21) for
  // instruction fetches, so a prefetched word is never older than a
  // store the program has already made to it.
  MBCU mbcu <- mkMBCU;
  FIFOF#(MemReq) storeQ <- mkUGSizedFIFOF(8); // unguarded: memCtl checks
                                              // notFull/notEmpty itself, so no
                                              // implicit condition is hoisted into it
  Vector#(NumTags, Reg#(Maybe#(WordAddr))) chPending <- replicateM(mkReg(tagged Invalid));
  Vector#(NumTags, Reg#(Bool))             chIssued  <- replicateM(mkReg(False));
  Vector#(NumTags, Reg#(Maybe#(Word64)))   chResp    <- replicateM(mkReg(tagged Invalid));
  Vector#(NumTags, Reg#(Maybe#(WordAddr))) chSpecial <- replicateM(mkReg(tagged Invalid));
  Vector#(NumTags, RWire#(WordAddr))       reqW      <- replicateM(mkRWire);
  Vector#(NumTags, PulseWire)              takeW     <- replicateM(mkPulseWire);
  RWire#(MemReq)   storeW <- mkRWire;   // writeWord (core storage) this clock
  Reg#(Bool)       irqEn  <- mkReg(False);  // interrupt system: reset = disabled
  Reg#(Maybe#(WordAddr)) recentStoreReg <- mkReg(tagged Invalid); // see recentStore()
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
  Reg#(Word64) accSignByte           <- mkReg(0); // addr 10, IBM bits 0-7 (BSV 63:56) only
  Reg#(Word64) indicators            <- mkReg(0); // addr 11
  // addr 12. IBM bits 0-19 are always one and 48-63 always zero, so
  // only IBM 20-47 -- model bits 43-16, twenty-eight of them -- are
  // writable. This used to be 64'hFFFF_0000_0000_0000 with a
  // {16'hFFFF, v[47:16], 16'h0000} write mask, which forces only IBM
  // 0-15 and leaves thirty-two bits writable; the register, its write
  // masker and StretchTypes' own comment all said 0-19 while the code
  // did 0-15. Nothing drives word 12 in the transcribed diagnostic, so
  // this was never caught by a test -- found by a code review against
  // the Appendix A field table.
  Reg#(Word64) mask                  <- mkReg(64'hFFFFF000_00000000);
  Reg#(Word64) remainder             <- mkReg(0); // addr 13
  Reg#(Word64) factor                <- mkReg(0); // addr 14
  Reg#(Word64) transit                <- mkReg(0); // addr 15
  Vector#(16, Reg#(Word64)) xreg      <- replicateM(mkReg(0)); // addr 16-31

  // The one rule that moves requests to the bus and responses back.
  // Every register it writes is written nowhere else; the methods
  // communicate with it through the wires above, so a method call
  // and this rule never race on a register.
  (* fire_when_enabled, no_implicit_conditions *)
  rule memCtl;
    // Stores: enqueue this clock's store (if any); issue the oldest
    // queued store when its unit is free.
    if (storeW.wget matches tagged Valid .r) begin
      if (storeQ.notFull) storeQ.enq(r);
      else $display("StretchStorage: store queue full, write to %0d LOST", r.addr);
      recentStoreReg <= tagged Valid r.addr;
    end else
      recentStoreReg <= tagged Invalid;
    Bool busUsed = False;
    if (storeQ.notEmpty && mbcu.canAccept(storeQ.first.addr)) begin
      mbcu.put(storeQ.first);
      storeQ.deq;
      busUsed = True;
    end
    // Read channels, in bus priority order: the operand channel, the
    // look-ahead levels, then the instruction buffers.
    Integer order[7] = {0, 3, 4, 5, 6, 1, 2};
    for (Integer oi = 0; oi < valueOf(NumTags); oi = oi + 1) begin
      Integer c = order[oi];
      Maybe#(WordAddr) pr = chPending[c];
      Bool issued = chIssued[c];
      Maybe#(Word64) rs = chResp[c];
      Maybe#(WordAddr) ps = chSpecial[c];
      if (takeW[c]) begin rs = tagged Invalid; ps = tagged Invalid; end
      if (mbcu.respReady(fromInteger(c))) begin
        let v <- mbcu.takeResp(fromInteger(c));
        rs = tagged Valid v;
        pr = tagged Invalid;
        issued = False;
      end
      // Every read waits for queued stores to leave the queue: store->
      // load ordering for the operand channel (a load after a store to
      // the same word must see the store; the look-ahead's LAAR
      // forwarding replaces this in stage 3) and the conservative
      // program-store compare for the instruction channels.
      if (!busUsed && !issued && !storeQ.notEmpty) begin
        if (pr matches tagged Valid .a &&& mbcu.canAccept(a)) begin
          mbcu.put(MemReq{ write: False, addr: a, data: 0, tag: fromInteger(c) });
          issued = True;
          busUsed = True;
        end
      end
      if (reqW[c].wget matches tagged Valid .a) begin
        if (isSpecialAddr(a))
          ps = tagged Valid a;
        else begin
          pr = tagged Valid a;
          issued = False;
        end
      end
      chPending[c] <= pr;
      chIssued[c]  <= issued;
      chResp[c]    <= rs;
      chSpecial[c] <= ps;
    end
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
      addrIntervalTimer: return intervalTimerAndClock;
      addrInterruptAddr: return interruptionAddress;
      addrUpperBoundary: return boundaryReg;
      addrMaintenanceBits: return maintenanceBits;
      addrChannelAddress: return channelAddress;
      addrOtherCpuBits: return otherCpuBits;
      addrLeftZerosCount: return zerosOnesCounts;
      addrAccLeft: return accLeft;
      addrAccRight: return accRight;
      addrAccSignByte: return accSignByte;
      addrIndicators: return indicators;
      addrMask: return mask;
      addrRemainder: return remainder;
      addrFactor: return factor;
      addrTransit: return transit;
      default:
        if (a >= addrIndexBase && a < addrIndexBase + 16)
          return xreg[a - addrIndexBase];
        else
          return 0; // unreachable: only addresses 0-31 are routed here
    endcase
  endfunction

  method Bool responseReady();
    return isValid(chSpecial[0]) || isValid(chResp[0]);
  endmethod

  method Action readWordReq(WordAddr a);
    reqW[0].wset(a);
  endmethod

  method ActionValue#(Word64) readWordResp();
    takeW[0].send();
    if (chSpecial[0] matches tagged Valid .a)
      return lookupSpecial(a);
    else
      return validValue(chResp[0]);
  endmethod

  method Action fetchReq(Bit#(1) y, WordAddr a);
    Bit#(3) c = 1 + zeroExtend(y);
    reqW[c].wset(a);
  endmethod

  method Bool fetchReady(Bit#(1) y);
    Bit#(3) c = 1 + zeroExtend(y);
    return isValid(chSpecial[c]) || isValid(chResp[c]);
  endmethod

  method ActionValue#(Word64) fetchResp(Bit#(1) y);
    Bit#(3) c = 1 + zeroExtend(y);
    takeW[c].send();
    if (chSpecial[c] matches tagged Valid .a)
      return lookupSpecial(a);
    else
      return validValue(chResp[c]);
  endmethod

  // Look-ahead level channels (level 0-3 -> tags 3-6), same protocol.
  method Action laReq(Bit#(2) lvl, WordAddr a);
    Bit#(3) c = 3 + zeroExtend(lvl);
    reqW[c].wset(a);
  endmethod

  method Bool laReady(Bit#(2) lvl);
    Bit#(3) c = 3 + zeroExtend(lvl);
    return isValid(chSpecial[c]) || isValid(chResp[c]);
  endmethod

  method ActionValue#(Word64) laResp(Bit#(2) lvl);
    Bit#(3) c = 3 + zeroExtend(lvl);
    takeW[c].send();
    if (chSpecial[c] matches tagged Valid .a)
      return lookupSpecial(a);
    else
      return validValue(chResp[c]);
  endmethod

  method Maybe#(WordAddr) recentStore();
    return recentStoreReg;
  endmethod

  method Bool writeReady();
    return storeQ.notFull;
  endmethod

  method Action writeWord(WordAddr a, Word64 v);
    case (a)
      addrZero: noAction; // writes to Zero are discarded (permanently protected)
      addrIntervalTimer: intervalTimerAndClock <= v; // simplification: full word writable; real HW
                                      // splits timer(read/write except store-type ops)
                                      // vs clock(read-only) -- see README "Scope".
      addrInterruptAddr: interruptionAddress <= v;   // permanently protected on real HW; not enforced
      addrUpperBoundary: boundaryReg <= v;           // permanently protected on real HW; not enforced
      addrMaintenanceBits: maintenanceBits <= v;
      addrChannelAddress: noAction; // read-only ("b" footnote)
      addrOtherCpuBits: otherCpuBits <= v;
      addrLeftZerosCount: zerosOnesCounts <= v;
      addrAccLeft: accLeft <= v;
      addrAccRight: accRight <= v;
      addrAccSignByte: accSignByte <= {v[63:56], 56'b0};   // IBM bits 0-7: the sign byte
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
      addrIndicators: noAction;
      addrMask: mask <= {20'hFFFFF, v[43:16], 16'h0000};   // IBM 0-19 = 1, 48-63 = 0 always
      addrRemainder: remainder <= v;
      addrFactor: factor <= v;
      addrTransit: transit <= v;
      default:
        if (a >= addrIndexBase && a < addrIndexBase + 16)
          xreg[a - addrIndexBase] <= v;
        else
          storeW.wset(MemReq{ write: True, addr: a, data: v, tag: 0 }); // nonexistent
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

  method Bool irqEnabled() = irqEn;
  method Word64 readBoundaries() = boundaryReg;
  method Action setIrqEnabled(Bool e);
    irqEn <= e;
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

  method Vector#(16, Word64) snapshotIndex() = readVReg(xreg);
  method Action restoreIndex(Vector#(16, Word64) v);
    writeVReg(xreg, v);
  endmethod

  method Word64 readAccSign();
    return accSignByte;
  endmethod

  method Word64 readAccLeft();
    return accLeft;
  endmethod

  method Word64 readAccRight();
    return accRight;
  endmethod

  method Word64 readFactor();
    return factor;
  endmethod

  method Word64 readZerosOnesCounts();
    return zerosOnesCounts;
  endmethod

endmodule

endpackage
