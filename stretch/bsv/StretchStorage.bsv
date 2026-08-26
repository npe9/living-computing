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
// General core storage (addresses 32 and up) is backed by a plain
// Vector of registers rather than the standard `RegFile` library
// module: RegFile's Verilog primitive hard-caps reads at 5 ports
// (`sub[5]` in RegFile.bs), and this design's execute stage has far
// more than 5 distinct call sites that read a word in a given cycle
// (readField, readAcc, readHW, per-opcode operand fetches, ...) even
// though only one instruction's worth of them is ever live at once. A
// Vector of registers has no such port limit -- reading a Reg is an
// unrestricted value method. The tradeoff is capacity: MemWords below
// bounds the simulated core to a window near address 0 (documented as a
// simulation-capacity choice, not an architectural one -- the 18-bit,
// 262,144-word address space is still what the *types* model, see
// WordAddr in StretchTypes.bsv; addresses at or beyond MEM_WORDS just
// read as 0 and discard writes, the same as a real machine addressing
// beyond its installed core would trip AD, Address Invalid, on real
// hardware -- not modeled here, see bsv/README.md "Scope").
//
// This module is otherwise combinational-read, single-write-per-cycle:
// adequate for the non-pipelined, one-instruction-per-rule StretchCore
// in this package. A pipelined/lookahead microarchitecture (what made
// the real 7030 famous) would need a genuinely multi-ported memory and
// is out of scope -- see bsv/README.md "Scope".

package StretchStorage;

import Vector::*;
import StretchTypes::*;

typedef 256 MemWords;
typedef Bit#(TLog#(MemWords)) MemIndex;

interface StretchStorage;
  // Read a full 64-bit word at a word address, honoring the
  // special-address semantics below. ActionValue, NOT a plain value
  // method, even though this implementation's answer is still same-
  // cycle for every address (see module header): this is step one of
  // the BRAM-backed-storage migration (bsv/README.md "Next steps"
  // item 6) -- changing every caller's calling CONVENTION (`<-` bind
  // inside an action/actionvalue context, not a bare expression)
  // while the underlying behavior is still guaranteed instant, so a
  // later swap to a genuinely multi-cycle BRAM backing for addresses
  // 32-and-up is a change to THIS METHOD's implementation and to
  // StretchCore.step()'s control flow, not to any of its ~26 callers'
  // syntax a second time. See StretchCore.bsv's step() for why a
  // method call itself still cannot literally span multiple clock
  // cycles in BSV -- that part of the migration is not done by this
  // type change alone.
  method ActionValue#(Word64) readWord(WordAddr a);

  // Write a full 64-bit word. Read-only/protected addresses silently
  // ignore the write (this models "permanently protected" locations;
  // it does not yet raise the protection-violation interrupt -- out of
  // scope, see README). Takes effect on the next clock edge.
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
endinterface

// mkStretchStorage: models the full 18-bit (262,144-word) core address
// space, matching the largest configuration described on p.19 ("18
// high-order bits address full words"). Addresses 0-31 are intercepted
// below per the Special Storage Assignment table; 32 and up are a flat
// RegFile-backed array (combinational read, registered write -- see
// file header for why that is adequate here and where it stops being
// adequate).
module mkStretchStorage(StretchStorage);

  // General core storage, addresses 32 upward (0-31 are special, per
  // the Special Storage Assignment table). See file header for why
  // this is a Vector of registers rather than a RegFile.
  Vector#(MemWords, Reg#(Word64)) mem <- replicateM(mkReg(0));
  function Bool memInRange(WordAddr a) = (a < fromInteger(valueOf(MemWords)));

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

  method ActionValue#(Word64) readWord(WordAddr a);
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
        else if (memInRange(a)) begin
          MemIndex idx = truncate(a);
          return mem[idx];
        end else
          return 0;
    endcase
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
          mem[idx] <= v;
        end
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

endmodule

endpackage
