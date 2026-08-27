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
// General core storage (addresses 32 and up) is backed by real BRAM
// (`mkBRAM1Server`, latency 1) -- the endpoint of the BRAM-backed-
// storage migration described across this project's git history and
// docs/phase2_arm_inventory.md. Addresses 0-31 stay a Vector of plain
// registers: the Special Storage Assignment table (p.111, "does not
// include internal computer registers and index registers") makes this
// an architectural boundary, not just a simulation convenience, and it
// lets `readAccLeft`/`readAccRight` (addresses 8/9) stay always-instant
// value methods (see their own comment below) rather than paying a
// request/response round trip.
//
// This module took two migration steps to reach BRAM, both preserved
// in git history for the reasoning: RegFile was ruled out (its
// Verilog primitive hard-caps reads at 5 ports, `sub[5]` in
// RegFile.bs, and this design's execute stage has far more than 5
// distinct call sites that could read a word in a given cycle even
// though only one is ever live at once); a plain Vector of registers
// was used as an interim step (unlimited read ports, but
// elaboration cost explodes past a few hundred words -- 512 words
// took 1m54s to elaborate, 1024 didn't finish in 2 minutes, versus
// BRAM's 0.275s at 8192 words in isolation, confirmed by probe). The
// tradeoff BRAM's latency-1 access introduces (a read genuinely spans
// a clock cycle, unlike the Vector's same-cycle reads) is what forced
// `readWordReq`/`readWordResp`'s request/response shape and the
// per-case-arm FSM staging throughout StretchCore.bsv/
// StretchExecute.bsv -- see docs/phase2_arm_inventory.md for the full
// conversion history.
//
// MemWords below still bounds the simulated core to a window near
// address 0 (a simulation-capacity choice, not an architectural one --
// the 18-bit, 262,144-word address space is still what the *types*
// model, see WordAddr in StretchTypes.bsv; addresses at or beyond
// MemWords just read as 0 and discard writes, the same as a real
// machine addressing beyond its installed core would trip AD, Address
// Invalid, on real hardware -- not modeled here, see bsv/README.md
// "Scope"). Kept at the same value Phase 1/2 developed against
// (isolating a capacity change from this latency-handling change, one
// candidate cause per commit); bumping it now that BRAM's elaboration
// cost is confirmed cheap at scale is a separate, later step.

package StretchStorage;

import Vector::*;
import BRAM::*;
import DefaultValue::*;
import StretchTypes::*;

typedef 256 MemWords;
typedef Bit#(TLog#(MemWords)) MemIndex;

interface StretchStorage;
  // Read a full 64-bit word, request/response style: issue the
  // request in one rule, collect the answer in a LATER rule (never
  // the same one). Deliberately NOT pipelined (no support for issuing
  // request N+1 in the same rule that collects request N's response,
  // the way a real BRAM port allows -- confirmed possible in
  // isolation, scratchpad/bram_probe/BramProbe4.bsv, but not built
  // here): every multi-read arm just pays one full request-then-
  // response round trip per read, serialized. This is a correctness
  // project, not a performance one, and the test harness's step cap
  // (2000, see strap/gen_tb.py) has ample room. No runtime guard
  // against calling readWordResp with no request outstanding,
  // matching this codebase's existing FSM style
  // (`pendingIdxWrite`/`ioPending` in StretchCore.bsv have none
  // either) -- correctness here rests on the FSM's own structure
  // being right, checked by code review and the regression suite, not
  // a runtime check.
  //
  // STRONGER, EASY-TO-MISS REQUIREMENT: readWordResp() MUST be called
  // on the cycle immediately following readWordReq() -- never with an
  // idle cycle in between. The implementation mediates the BRAM
  // response through a `Wire`/`mkDWire` (see mkStretchStorage's
  // `bramResp`/`drainBram`), which only holds its value for the ONE
  // cycle it's written; a caller that lets a cycle pass before
  // collecting the response gets back a silent, wrong `0` -- no error,
  // no hang, just data loss. Verified empirically (not just reasoned
  // about): a probe that requests, waits one idle cycle, then collects
  // returned 0 instead of the written value. Every current caller in
  // `StretchCore.step()`'s FSM (fetchPending/execPending/ioPending)
  // already satisfies this by construction, since step() IS the
  // core's own per-cycle clock action and each of those branches
  // collects the response as literally the first thing the very next
  // step() call does -- but this is a real precondition on the
  // interface, not an accident of the current call sites, and any
  // future caller (or FSM restructuring) must preserve it.
  method Action readWordReq(WordAddr a);
  method ActionValue#(Word64) readWordResp();

  // Write a full 64-bit word. Read-only/protected addresses silently
  // ignore the write (this models "permanently protected" locations;
  // it does not yet raise the protection-violation interrupt -- out of
  // scope, see README). Single-cycle Action throughout -- a write
  // never needs to observe its own completion, so there's nothing for
  // a caller to wait on even with a genuinely latent BRAM backing.
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

// mkStretchStorage: models the full 18-bit (262,144-word) core address
// space, matching the largest configuration described on p.19 ("18
// high-order bits address full words"). Addresses 0-31 are intercepted
// below per the Special Storage Assignment table; 32 and up are
// BRAM-backed (latency 1, real request/response access) -- see file
// header for the migration history and why 0-31 stays Reg-backed.
module mkStretchStorage(StretchStorage);

  // General core storage, addresses 32 upward (0-31 are special, per
  // the Special Storage Assignment table). Indexed by the raw
  // truncated address, same as the Vector this replaced -- addresses
  // 0-31 simply never reach this path (intercepted below), so the
  // first 32 BRAM slots go unused; keeping the indexing arithmetic
  // identical to the pre-BRAM design was judged lower-risk than
  // reclaiming those 32 slots via an address translation.
  BRAM_Configure cfg = defaultValue;
  cfg.latency = 1; // the only latency this bsc's BRAM library
                    // actually supports (0 is rejected outright,
                    // "latency must be either 1 or 2" -- see
                    // docs/phase2_arm_inventory.md); 2 was never
                    // needed once the request/response interface
                    // above already tolerates arbitrary same-request
                    // latency.
  BRAM1Port#(MemIndex, Word64) mem <- mkBRAM1Server(cfg);
  function Bool memInRange(WordAddr a) = (a < fromInteger(valueOf(MemWords)));
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

  // readWordReq/readWordResp's deferral state. Valid a: the request
  // was for special (Reg-backed) address `a` (or an address beyond
  // MemWords); resolve by reading live Reg state at response time,
  // not from BRAM. Invalid: the request went to BRAM; resolve via
  // mem.portA.response.get().
  Reg#(Maybe#(WordAddr)) pendingSpecial <- mkReg(tagged Invalid);

  // Mediates mem.portA.response.get()'s implicit "response available"
  // condition: get() carries an implicit condition, and bsc conjoins
  // the implicit conditions of every method call *statically reachable*
  // in a rule into that rule's overall firing predicate -- it does not
  // narrow the predicate per case-arm/branch. If readWordResp() called
  // get() directly, any caller rule that ALSO calls readWordReq() in a
  // different branch (exactly StretchCore.step()'s FSM shape) would
  // silently gain "and a BRAM response happens to be available right
  // now" as part of its firing condition -- true only after a request
  // was already issued -- so the rule can never fire on the first pass
  // and the whole simulation hangs with zero output, spinning at 100%
  // CPU with no forward progress. Draining get() in an internal rule
  // keeps that implicit condition local to this module; readWordResp()
  // then just reads the wire, an ordinary (unconditional) value read.
  // Diagnosed via bisection down to a two-line case-arm repro
  // (readWordReq in one arm, readWordResp in another arm of the same
  // rule) that hung with mem.portA.response.get() called directly and
  // ran clean once mediated through this wire. See
  // docs/phase2_arm_inventory.md step 9.
  //
  // TRADE-OFF this fix introduces, load-bearing for every caller (see
  // readWordResp's own interface comment above for the full
  // statement): a DWire holds its value for exactly the cycle it's
  // written. drainBram fires and writes bramResp on whatever cycle the
  // BRAM's response becomes ready; if readWordResp() isn't called that
  // SAME cycle, the value is gone (next cycle's default mkDWire(0)) --
  // a silent wrong `0`, not a hang or an error. A plain `Reg` doesn't
  // avoid this trade-off, it just moves it: a Reg would delay the
  // value by one more cycle and break every current caller's timing
  // instead. The actual fix is the invariant documented on
  // readWordResp() (call it the cycle immediately after
  // readWordReq()), not a different storage primitive here.
  Wire#(Word64) bramResp <- mkDWire(0);

  rule drainBram;
    let v <- mem.portA.response.get();
    bramResp <= v;
  endrule

  // Special-register lookup, used only by readWordResp when the
  // pending request named a non-BRAM address. Every address 0-31 is
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
          return 0; // out of range (>= MemWords)
    endcase
  endfunction

  method Action readWordReq(WordAddr a);
    if (isSpecialAddr(a) || !memInRange(a)) begin
      pendingSpecial <= tagged Valid a;
    end else begin
      pendingSpecial <= tagged Invalid;
      MemIndex idx = truncate(a);
      mem.portA.request.put(BRAMRequest{
        write: False, responseOnWrite: False, address: idx, datain: ? });
    end
  endmethod

  method ActionValue#(Word64) readWordResp();
    if (pendingSpecial matches tagged Valid .a) begin
      return lookupSpecial(a);
    end else begin
      return bramResp;
    end
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
        else if (memInRange(a)) begin
          MemIndex idx = truncate(a);
          mem.portA.request.put(BRAMRequest{
            write: True, responseOnWrite: False, address: idx, datain: v });
        end
        // else: out of range, discard
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
