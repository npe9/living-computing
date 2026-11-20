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
import ConfigReg::*;   // see intDueCalc below
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
  // the operand channel, independent of it, lower bus priority (above
  // a floating-point look-ahead level's fetch: see memCtl).
  method Action fetchReq(Bit#(1) y, WordAddr a);
  method Bool fetchReady(Bit#(1) y);
  method ActionValue#(Word64) fetchResp(Bit#(1) y);
  // The core-storage word stored on the previous clock, if any: the
  // instruction unit compares it with its prefetched words (program
  // store compare) and invalidates a match.
  method Maybe#(WordAddr) recentStore();
  // Look-ahead level channels (stage 3): one outstanding operand
  // fetch per level, return tags 3-6, priority above the Y buffers
  // (Buchholz §14.3) unless `fp`: a floating-point level's fetch yields
  // to a waiting Y fetch (R23-9732 Figure 3.1.21; see memCtl).
  method Action laReq(Bit#(2) lvl, WordAddr a, Bool fp);
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

  // THE TAIL WORD OF A VFL FIELD THAT CROSSES A WORD BOUNDARY.
  //
  // Sixty-four is not a multiple of six, so a program that stores
  // 6-bit characters one after another eventually stores one that
  // straddles two storage words.  MCP does exactly that: printed
  // p.43 line 49 of its Hollerith-to-BCD converter is
  // "ST(V+I)(BU,6,6),.6($5)", and character ten of every card lands
  // at bits 60-65.  Two words have to change, and `writeWord` can
  // move one.
  //
  // WHY THIS IS A SECOND METHOD AND NOT A SECOND writeWord CALL.
  // `writeWord` hands its request to the `storeW` RWire, and an
  // RWire takes one value per clock; a second call in the same rule
  // is the G0004 conflict recorded in StretchExecute.bsv's header
  // ("the underlying RegFile likewise accepts only one write per
  // rule").  This method writes a REGISTER instead, which memCtl
  // drains into the store queue on the FOLLOWING clock -- so the
  // caller may call writeWord and writeWordTail in one rule, because
  // they touch different state.
  //
  // THE HEAD GOES THROUGH writeWord AND THE TAIL THROUGH HERE, in
  // that order, and the queue preserves it.  Reads are held off while
  // a tail is pending (see memCtl) exactly as they are held off while
  // the queue is non-empty, so no channel can see the first word
  // changed and the second not.
  //
  // CORE STORAGE ONLY.  The tail is drained to the store queue, which
  // is the core-storage path; it does not run the special-address
  // dispatch writeWord's `case` does.  A crossing field whose SECOND
  // word is special (below 32) is therefore refused on the execute
  // side rather than handled here -- see StretchExecute.bsv's ST arm.
  method Action writeWordTail(WordAddr a, Word64 v);

  // True on the one clock a tail is waiting to be queued.  The core
  // folds it into `busyXfer` so no instruction is armed while it
  // waits -- the same stall rl_xmit's multi-word transfer uses, for
  // the same reason: one more writer would have nowhere to go.
  method Bool storeTailPending();
  // A store the MBCU has not yet accepted: queued, or a crossing
  // field's tail still held.  The LAAR stays busy until "the proper
  // operand ... is fetched, checked, and accepted by the MBCU" (Perf.
  // Char. Vol. 1 printed p.3-20); StretchCore's laarBusy reads this.
  method Bool storesPending();

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
  // THE INPUT-OUTPUT STATUS REPORT, Reference Manual printed p.118
  // ("Setting up of Input-Output Indicators", read in the ink).
  // ioReportReady is the page's two conditions: "1. The five
  // input-output status indicators (EPGK, UK, EE, EOP, and CS) in the
  // indicator register have previously been reset to zero ... 2. The
  // interruption system is currently enabled."  ioStatus either makes a
  // report -- Valid {EPGK,UK,EE,EOP,CS} and the channel -- setting the
  // indicators "as a group at one time" and the channel address
  // register with them, or (Invalid) resets the channel address
  // register, which p.119 says happens when "the system is in a
  // condition to accept the next set of input-output indicators".
  method Bool ioReportReady();
  method Action ioStatus(Maybe#(Tuple2#(Bit#(5), Bit#(7))) r);
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

  // THE MASK REGISTER, word 12, read as one word -- for the
  // MASK-DEPENDENT half of the address alarms.  p.32: when an alarm's
  // mask bit is one "the operation is terminated and an interruption
  // occurs"; when it is zero "the indicator is set, but the operation
  // proceeds".  The execute side needs that bit to decide whether to
  // suppress, and it pulls the field apart itself, exactly as
  // protViolates does with readBoundaries.
  //
  // THIS IS NOT THE SHAPE THE COMMENT BELOW WARNS ABOUT.  That warning
  // is about a CORE RULE running every clock reading `mask` and
  // `interruptionAddress` together to decide an interruption -- which
  // forced an ordering between readWordResp and writeWord that the
  // harness's loader could not satisfy.  This is a plain Reg read used
  // inside execute(), the same shape readBoundaries has had since DS,
  // and `mask` is already a ConfigReg for the intDueCalc reason below.
  method Word64 readMask();

  // IS AN INTERRUPTION DUE, AND WHERE DOES IT GO?  Answered HERE, not
  // in the core, and latched: Valid(N, EIA) when p.48's three
  // conditions hold -- "interruption requires the mask bit to be 1, the
  // indicator bit to be 1, and the mechanism to be enabled" -- where N
  // is the leftmost such indicator's number and EIA the word address
  // its routine starts at.
  //
  // THIS LIVES IN STORAGE BECAUSE OF WHAT IT READS.  The obvious shape
  // -- expose readMask() and readInterruptAddr() and let the core
  // combine them -- compiles mkStretchCore and then breaks the SMOKE
  // TEST with G0004: readWordResp() reads every special register
  // through lookupSpecial, writeWord() writes them, and a new read of
  // `mask` from a core rule that runs every clock forces an ordering
  // between those two exported methods that the harness's own loader
  // rule cannot satisfy.  Reading `mask`, `indicators`, `irqEn` and
  // `interruptionAddress` from inside the module that owns them costs
  // the core nothing: it reads one register.
  //
  // Latched rather than combinational for the same reason irqEnabled
  // and readBoundaries are plain Reg reads -- the core needs this in a
  // rule PREDICATE.  The cost is one clock of delay before an
  // interruption is taken, which no program can observe and which is
  // late rather than early.
  method Maybe#(Tuple2#(Bit#(6), WordAddr)) interruptDue();

  // ONE PULSE OF THE 1,024-PER-SECOND OSCILLATOR (Ref. Manual printed
  // p.34).  Called from StretchCore's rl_clock, which owns the divider
  // and only runs while the machine is operating; what a pulse DOES to
  // location 1 is oscillatorStep in this file.  It lives here because
  // the two counters and the indicator register it touches are this
  // module's registers -- the same reason interruptDue() is computed
  // here rather than in the core.
  method Action oscillatorPulse();

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

  // The two connective counts (Reference Manual printed pp.75-76).
  // A method of its own rather than writeWord: it wins over a store
  // into word 7 in the same clock (printed p.76, "set at the end";
  // commitCounts).  Writes the counter fields and reads nothing.
  method Action setConnectiveCounts(Bit#(7) lzc, Bit#(7) aoc);

  // The left-zeros count alone, for the floating-point division
  // arms (Reference Manual printed p.94).  A method rather than a
  // writeWord to location 7, for the reason the counter registers'
  // own comment gives.
  method Action setLeftZerosCount(Bit#(7) lzc);

  // The memory bus control unit's count of accepted READ requests
  // (StretchMemory's MBCU.readCount): test observation only, read by
  // gen_tb's MEMREADS= check.
  method Bit#(32) memReads();
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
  // look-ahead has priority over the instruction fetch), except that a
  // floating-point level yields to a waiting 1Y/2Y fetch (R23-9732
  // Figure 3.1.21, 2026-11-17; see memCtl).
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
  // Which look-ahead level's pending fetch belongs to a floating-point
  // instruction (laReq's `fp`): such a fetch yields the bus to a waiting
  // 1Y/2Y fetch (memCtl).
  Vector#(4, Reg#(Bool))                   chFpLevel <- replicateM(mkReg(False));
  Vector#(4, RWire#(Bool))                 fpReqW    <- replicateM(mkRWire);
  Vector#(NumTags, PulseWire)              takeW     <- replicateM(mkPulseWire);
  RWire#(MemReq)   storeW <- mkRWire;   // writeWord (core storage) this clock
  // The crossing-field tail: the wire a writeWordTail call lands on,
  // and the register memCtl parks it in for one clock.  memCtl is the
  // ONLY writer of the register -- the same discipline every other
  // register in this module keeps, and the reason the wire exists at
  // all (see memCtl's own header).
  RWire#(MemReq)   storeTailW <- mkRWire;
  Reg#(Maybe#(MemReq)) storeTail <- mkReg(tagged Invalid);
  Reg#(Bool)       irqEn  <- mkConfigReg(False); // interrupt system: reset = disabled (ConfigReg: intDueCalc)
  Reg#(Maybe#(WordAddr)) recentStoreReg <- mkReg(tagged Invalid); // see recentStore()
  function Bool memInRange(WordAddr a) = installed(a);
  function Bool isSpecialAddr(WordAddr a) = (a < 32);

  // Named CPU registers backing addresses 0-31.
  // addr 1: bits 0-18 the interval timer, 28-63 the time clock.
  // ConfigReg, and written by exactly one rule (oscillatorStep below):
  // the oscillator steps it independently of whatever instruction is
  // executing, so writeWord can no longer assign it directly.  A plain
  // Reg read from a new reader would also join the G0095 path the
  // mkConfigReg choices in this file exist to break.
  Reg#(Word64) intervalTimerAndClock <- mkConfigReg(0);
  RWire#(Bit#(28)) timerW <- mkRWire;   // word 1 IBM bits 0-27 stored this clock
  RWire#(Word64)   indW   <- mkRWire;   // setIndicatorBits' value this clock
  RWire#(Word64)   indStW <- mkRWire;   // a STORE into word 11 this clock (writeWord)
  RWire#(Maybe#(Tuple2#(Bit#(5), Bit#(7)))) ioW <- mkRWire; // ioStatus this clock
  // EPGK..CS, indicators 9-13: IBM bits 9-13 are model bits 54-50.
  Word64 ioStatusMask = 64'h1F << (63 - 13);
  // THE OSCILLATOR PULSE IS A PulseWireOR, AND THAT IS NOT A STYLE CHOICE.
  // oscillatorPulse() is part of this interface, so at mkStretchCore's
  // synthesized boundary it is also an EXPORTED method (`mem_oscillatorPulse`)
  // that bsc must assume the harness might call in the same clock as
  // StretchCore's rl_clock calls it.  With a plain mkPulseWire those are two
  // `wset`s on one wire, bsc makes them conflict, the exported method wins the
  // urgency contest -- and rl_clock's `fire_when_enabled` then fails outright:
  //   Error (G0005): The assertion `fire_when_enabled' failed for rule
  //   `RL_rl_clock' because it is blocked by rule mem_oscillatorPulse
  // which is the SILENT-TICK-DROP hazard check_schedule.py exists to catch,
  // reported for once by the compiler.  mkPulseWireOR makes several senders in
  // one clock legal (they OR), the conflict disappears, and rl_clock keeps its
  // assertion.  The same clock pulsed twice is still one pulse, which is the
  // right answer anyway: there is one oscillator.
  PulseWire oscPulse <- mkPulseWireOR; // the oscillator fired this clock
  PulseWire tsFired  <- mkPulseWire;   // ... and the timer went 1 -> 0
  Reg#(Word64) interruptionAddress   <- mkConfigReg(0); // addr 2 (ConfigReg: intDueCalc)
  Reg#(Word64) boundaryReg           <- mkReg(0); // addr 3
  // See the interruptDue() comment in the interface above.
  Reg#(Maybe#(Tuple2#(Bit#(6), WordAddr))) intDueReg <- mkReg(tagged Invalid);
  Reg#(Word64) maintenanceBits       <- mkReg(0); // addr 4
  Reg#(Word64) channelAddress        <- mkReg(0); // addr 5
  Reg#(Word64) otherCpuBits          <- mkReg(0); // addr 6
  // WORD 7 IS TWO COUNTERS AND NOTHING ELSE, AND THEY HAVE ONE WRITER.
  //
  // Reference Manual printed p.36: the left-zeros counter is bits 17-23
  // of location 7, the all-ones counter bits 44-50.  printed p.34: "Not
  // all bit positions in locations 0-15 are assigned to specific
  // functions.  Those bit positions that are not so assigned are always
  // zero.  Information stored in these positions is not recoverable."
  // So the other fifty bits of word 7 are not kept at all: they read 0.
  //
  // The counters are written by three things: every connective
  // (setConnectiveCounts, printed pp.75-76), the floating-point division
  // arms and LTRS (setLeftZerosCount / setConnectiveCounts, p.36, p.94),
  // and A STORE INTO LOCATION 7 (writeWord), which p.34 makes an
  // ordinary addressable word and p.76 does not exempt: the counts "are
  // not changed as an inherent part of any other non-connective
  // operations", so an ST or M+ into word 7 lands.  The three arrive on
  // wires and commitCounts below is the registers' one writer -- word
  // 11's shape (indStW, commitIndicators).  Until 2026-11-17 writeWord
  // did not write the counter fields at all (a CM's store reaches word 7
  // through a dynamic address in the same arm that sets the counts, and
  // two writers of one register in one rule would not schedule), so an
  // ST or M+ into word 7 lost its count bits and the unassigned bits were
  // kept as stored.
  //
  // THE ORDER, printed p.76: "The counts are set at the end of the
  // connective operations".  So in the same clock the counts win over
  // the store.  A CM whose crossing tail is word 7 writes the tail the
  // NEXT clock (rl_tail_write); its counts are put into the tail word
  // before it leaves the E-box (StretchExecute's countsOverTail), so they
  // win there too.
  //
  // IBM bit n is model bit 63-n: the left-zeros count at 17-23 is
  // [46:40], the all-ones count at 44-50 is [19:13].
  Reg#(Bit#(7))  zocLzc <- mkReg(0);   // IBM 17-23
  Reg#(Bit#(7))  zocAoc <- mkReg(0);   // IBM 44-50
  RWire#(Word64)  w7StW  <- mkRWire;   // a STORE into word 7 this clock (writeWord)
  RWire#(Bit#(7)) lzcW   <- mkRWire;   // a count set this clock
  RWire#(Bit#(7)) aocW   <- mkRWire;

  function Word64 composeWord7();
    return { 17'b0, zocLzc, 20'b0, zocAoc, 13'b0 };
  endfunction

  (* fire_when_enabled, no_implicit_conditions *)
  rule commitCounts;
    Bit#(7) lzc = zocLzc;
    Bit#(7) aoc = zocAoc;
    if (w7StW.wget matches tagged Valid .v) begin
      lzc = v[46:40];
      aoc = v[19:13];
    end
    if (lzcW.wget matches tagged Valid .l) lzc = l;   // p.76: set at the end
    if (aocW.wget matches tagged Valid .a) aoc = a;
    zocLzc <= lzc;
    zocAoc <= aoc;
  endrule
  Reg#(Word64) accLeft               <- mkReg(0); // addr 8
  Reg#(Word64) accRight              <- mkReg(0); // addr 9
  Reg#(Word64) accSignByte           <- mkReg(0); // addr 10, IBM bits 0-7 (BSV 63:56) only
  Reg#(Word64) indicators            <- mkConfigReg(0); // addr 11 (ConfigReg: intDueCalc)
  // addr 12. IBM bits 0-19 are always one and 48-63 always zero, so
  // only IBM 20-47 -- model bits 43-16, twenty-eight of them -- are
  // writable. This used to be 64'hFFFF_0000_0000_0000 with a
  // {16'hFFFF, v[47:16], 16'h0000} write mask, which forces only IBM
  // 0-15 and leaves thirty-two bits writable; the register, its write
  // masker and StretchTypes' own comment all said 0-19 while the code
  // did 0-15. Nothing drives word 12 in the transcribed diagnostic, so
  // this was never caught by a test -- found by a code review against
  // the Appendix A field table.
  Reg#(Word64) mask                  <- mkConfigReg(64'hFFFFF000_00000000); // ConfigReg: intDueCalc
  Reg#(Word64) remainder             <- mkReg(0); // addr 13
  Reg#(Word64) factor                <- mkReg(0); // addr 14
  Reg#(Word64) transit                <- mkReg(0); // addr 15
  Vector#(16, Reg#(Word64)) xreg      <- replicateM(mkReg(0)); // addr 16-31

  // p.48: "a mechanism develops the number of the leftmost actuated
  // indicator whose mask bit is one ... the developed number is added
  // to the contents of the interruption address register to form the
  // effective interruption address."
  //
  // LEFTMOST IS THE LOWEST INDICATOR NUMBER, which is the HIGHEST index
  // of the Bit#(64): IBM bit n is index 63-n everywhere in this model.
  // p.48 says why the choice of leftmost matters -- "the leftmost one
  // identification defines the relative priority of actuated indicators
  // if more than one has its corresponding mask bit turned on".
  //
  // THE TABLE IS 48 SUCCESSIVE FULL-WORD LOCATIONS, so N counts WORDS.
  // p.48: "The initial instruction for a routine occupies all or half
  // of a location in a table of 48 successive full-word locations.  The
  // address of the first location is contained in the interruption
  // address register.  The interruption address register contains 18
  // bits and has address 2.0."  Bits 0-17 of word 2 are indices 63-46,
  // read exactly as the boundary registers are.
  // THE REGISTERS IT READS ARE ConfigRegs, AND THAT IS WHAT MAKES IT
  // SCHEDULE.  A plain rule reading `indicators`/`mask`/
  // `interruptionAddress` while the exported writeWord also writes them
  // is a read-before-write ordering, and combined with the core's rules
  // that closes a loop through the synthesized boundary: bsc rejects it
  // with G0095, "a path containing rules was detected between the
  // scheduling of method mem_writeWord and its execution", naming
  // mem_writeWord -> rl_prepare -> intDueCalc -> mem_writeWord.
  // mkConfigReg breaks exactly that: the read is unordered against the
  // write and always yields the value at the start of the clock, which
  // is the semantics this rule already wanted.
  rule intDueCalc;
    Word64 pending = indicators & mask;
    Bit#(6) n = 0;
    Bool found = False;
    for (Integer i = 63; i >= 0; i = i - 1)
      if (!found && pending[i] == 1) begin
        found = True;
        n = fromInteger(63 - i);
      end
    WordAddr iar = interruptionAddress[63:46];
    intDueReg <= (irqEn && found)
                 ? tagged Valid tuple2(n, iar + zeroExtend(n))
                 : tagged Invalid;
  endrule

  // ---- WORD 1: THE INTERVAL TIMER AND THE TIME CLOCK ----------------
  //
  // This rule is the ONE writer of intervalTimerAndClock.
  //
  // Reference Manual printed p.34 (PDF 37), INTERVAL TIMER, read
  // first-hand: "The value of the interval timer reading is stored in
  // core storage and occupies bit positions 0 through 18 of location 1.
  // It is continually stepped down by pulses originating from a stable
  // oscillator.  Each time the oscillator delivers a pulse, the value of
  // the timer is read out, decremented by one, and returned to core
  // storage."  And: "Whenever it goes from one to zero, it turns on the
  // time signal indicator in the indicator register.  The next
  // oscillator pulse then sets the timer to all ones unless the program
  // in the meantime has changed its contents.  The timer does not stop
  // after reaching zero."
  //
  // Printed p.35 (PDF 38), TIME CLOCK: "a number 36 bits long which is
  // continually stepped up by pulses originating from the same 1024
  // cycle per second oscillator which controls the updating of the
  // interval timer.  The two clocks are updated consecutively in the
  // same time interval."  "The value of the clock occupies bits 28-63 of
  // location 1."  "When the clock reaches its maximum reading of all
  // ones, the next oscillator pulse sets it to all zeros.  No indication
  // is given when the clock recycles to zero."
  //
  // ONE PULSE, ONE RULE, because the manual describes one oscillator and
  // "the two clocks are updated consecutively in the same time
  // interval" -- a single event, not two that could be separated.  The
  // divider that decides when a pulse happens is StretchTiming.bsv's
  // oscPulseNumer/oscPulseDenom, driven from StretchCore's rl_clock.
  //
  // THE RELOAD NEEDS NO SPECIAL CASE, and that is worth saying because
  // it looks as though it must.  p.34 describes the step off zero as a
  // RELOAD -- "sets the timer to all ones" -- but 0 - 1 modulo 2^19 IS
  // all ones, so a plain modular decrement realizes the printed rule
  // exactly, INCLUDING its "unless the program in the meantime has
  // changed its contents" clause, since a program change simply leaves a
  // different value for the pulse to decrement.  The deck agrees bit for
  // bit: jb_ax5b routine 1258 TEST 2 block I589/I5810 sets the timer to
  // zero and expects I58K1, printed "777777.40 00" -- all ones in bits
  // 0-18 and nothing else (verify_ax5b_1258_test2_listing.py).  The same
  // holds for p.35's clock recycle, all ones -> all zeros, which is a
  // plain modular increment.
  //
  // TS FIRES ON THE EDGE, NOT ON THE VALUE.  "Whenever it goes FROM ONE
  // TO ZERO" -- the test is on the value BEFORE the step, and the
  // difference is not academic.  A rule that fired when the NEW value is
  // zero would also fire on the reload step, every 2^19 ticks turning
  // into every tick; and because this model forces mask bits 0-19 to one
  // (see `mask` above) TS is permanently masked on and outranks DS and
  // every PG indicator in intDueCalc's leftmost-wins scan, so every
  // enabled program would take a TS interruption it never took before.
  // docs/NEXT.md 5 predicted exactly that failure.
  // decks/interval_timer_steps.strap block 3a is the check that tells
  // the two rules apart, and it is one instruction long.
  //
  // BITS 19-27 ARE CLEARED BY THE STEP.  p.34's programming note: bit
  // positions 19 through 27 "are unused and appear between the interval
  // timer and the time clock", and bits 19-24 set into location 1 by a
  // STORE VALUE "remain there until the first time the interval timer is
  // stepped down".  Deck witness: 1258 TEST 2 block I5811/I5812 sets the
  // timer to I58K2 ("1.77 00": bits 0-18 = 3, bits 19-23 = 11111),
  // expects BIT17 ("1.00 00": the value 2 with 19-23 clear) after the
  // step, and widens its own printed error text from "0-18." to "0-23."
  // exactly there to say that those five bits are in scope.
  //
  // A PROGRAM STORE IN THE SAME CLOCK IS APPLIED FIRST, AND THEN
  // STEPPED.  Both cannot be "the" value of location 1 for this clock,
  // and the manual arbitrates no such race -- on real hardware there is
  // none, the oscillator being asynchronous to everything the CPU does.
  // Store-then-step is chosen because it is what p.34's "unless the
  // program in the meantime has changed its contents" describes: the
  // program's value is the one the next pulse acts on.  No test can
  // observe the choice (it needs a store landing in the same 0.3 us as a
  // pulse, one clock in 3255, and the difference is one tick); it is
  // pinned here so that it is a decision and not an accident of the
  // order two statements happen to be written in.
  (* fire_when_enabled, no_implicit_conditions *)
  rule oscillatorStep;
    Word64 w1 = intervalTimerAndClock;
    if (timerW.wget matches tagged Valid .lh)
      w1 = {lh, w1[35:0]};   // p.35: the right half is not program-writable
    if (oscPulse) begin
      Bit#(19) t = w1[63:45];   // IBM 0-18,  the interval timer
      Bit#(36) c = w1[35:0];    // IBM 28-63, the time clock
      if (t == 1) tsFired.send();
      w1 = { t - 1,        // down one, modulo 2^19: p.34's reload, exactly
             9'b0,         // IBM 19-27, cleared by the step (programming note)
             c + 1 };      // up one, modulo 2^36: p.35, and nothing is raised
    end
    intervalTimerAndClock <= w1;
  endrule

  // THE ONE WRITER OF `indicators`.  setIndicatorBits used to assign the
  // register directly.  The interval timer's TIME SIGNAL will make the
  // oscillator a SECOND, non-exclusive writer -- a pulse is independent
  // of whatever instruction is executing -- and a plain Reg cannot take
  // two writes in one clock.  The funnel is the shape this file already
  // uses for core-storage writes (`storeW` and memCtl below): the method
  // sets a wire, one rule commits.  Callers are unaffected, including
  // the standing rule that an instruction must call setIndicatorBits at
  // most once per clock -- two calls are now a double wset, which bsc
  // rejects exactly as it rejected the double register write.
  (* fire_when_enabled, no_implicit_conditions *)
  rule commitIndicators;
    Word64 ind = fromMaybe(indicators, indW.wget);
    // A STORE INTO THE INDICATOR REGISTER, Reference Manual printed p.37:
    // "Bit positions 0-19 of the indicator register can be read, but not
    // loaded.  Any attempt to store into these positions has no effect.
    // Bit positions 20-63 may either be read or loaded. ... When an
    // instruction calls for storing into any part of the indicator
    // register, the result in bits 20-63 of the indicator register will
    // be the same as if this operation had acted upon any other storage
    // location whose initial contents were the same as those of the
    // indicator register at the start of execution of the instruction.
    // The setting of any of the indicators 20-63 that would normally
    // occur as part of the store operation is overridden by this
    // result."  The stored word was built from word 11 as read at the
    // start of the instruction (the read-modify-write every store
    // does), so IBM 20-63 (model 43:0) are taken from it whole, over
    // whatever the instruction's own setIndicatorBits wrote there; IBM
    // 0-19 (model 63:44) keep the instruction's value.  TS and the I/O
    // report below are in 0-19 and are OR-ed on afterwards as before.
    if (indStW.wget matches tagged Valid .sv)
      ind = {ind[63:44], sv[43:0]};
    // TIME SIGNAL IS INDICATOR 4.  Reference Manual printed p.44,
    // "Attention Request": "4. Time Signal (TS).  The interval timer
    // has become zero."  IBM bit n is index 63-n everywhere in this
    // model.
    //
    // IT IS OR-ED ON TOP of whatever the executing instruction wrote,
    // which decides one corner: an instruction that CLEARS TS in the
    // same clock as a pulse that sets it leaves TS on.  That is the
    // faithful answer -- the pulse genuinely happened, and p.48 has the
    // interruption mechanism turn an indicator off before the routine
    // runs, not before the condition recurs -- and it is also the only
    // answer a single committing rule can give.
    Bit#(6) tsIndex = 63 - ind_TS;
    if (tsFired) ind[tsIndex] = 1;
    // AN INPUT-OUTPUT STATUS REPORT IS OR-ED ON TOP TOO, for TS's reason:
    // the exchange is independent of the instruction being executed.
    // EPGK..CS are indicators 9-13, consecutive, in p.113's order.
    if (ioW.wget matches tagged Valid (tagged Valid {.s, .ch})) begin
      ind[63 - ind_EPGK] = ind[63 - ind_EPGK] | s[4];
      ind[63 - ind_UK]   = ind[63 - ind_UK]   | s[3];
      ind[63 - ind_EE]   = ind[63 - ind_EE]   | s[2];
      ind[63 - ind_EOP]  = ind[63 - ind_EOP]  | s[1];
      ind[63 - ind_CS]   = ind[63 - ind_CS]   | s[0];
    end
    indicators <= ind;
  endrule

  // THE CHANNEL ADDRESS REGISTER'S ONE WRITER.  Printed p.119: "The
  // register has word address 5 and corresponds to bit positions 12
  // through 18" -- model bits 51:45 -- and the program can only read it
  // (writeWord's addrChannelAddress arm is a no-op).
  (* fire_when_enabled, no_implicit_conditions *)
  rule commitChannelAddress;
    if (ioW.wget matches tagged Valid .r)
      case (r) matches
        tagged Valid {.s, .ch}: channelAddress <= zeroExtend(ch) << 45;
        tagged Invalid:         channelAddress <= 0;
      endcase
  endrule

  // The one rule that moves requests to the bus and responses back.
  // Every register it writes is written nowhere else; the methods
  // communicate with it through the wires above, so a method call
  // and this rule never race on a register.
  (* fire_when_enabled, no_implicit_conditions *)
  rule memCtl;
    // Stores: enqueue this clock's store (if any); issue the oldest
    // queued store when its unit is free.
    //
    // A CROSSING FIELD'S TAIL GOES FIRST.  Its two words belong to ONE
    // instruction and the head was queued last clock, so the tail is
    // older in program order than anything arriving now.  The core
    // holds off arming for the clock the tail waits
    // (storeTailPending, folded into busyXfer), so nothing SHOULD
    // arrive -- and the $display says so rather than the comment,
    // because "should" is a claim and a message is a measurement.
    //
    // >>> AND THE MESSAGE FIRED, SO THE TAIL IS NOW RETRIED RATHER THAN
    // DROPPED. <<<  Measured on the MCP boot, 2026-10-26: five tails --
    // to words 1240, 1241, 1243, 1244 and 1246 -- met a FULL queue and
    // the old code discarded them, `tailNext` having been set Invalid
    // unconditionally.  That is half a VFL field written and half
    // silently not, which no program can recover from and no indicator
    // reports.
    //
    // RETRYING IS SAFE AND IT TERMINATES.  `writeReady()` is
    // `storeQ.notFull && !isValid(storeTail)`, so while a tail is
    // pending the core arms no further store, and `memCtl` drains one
    // queued store every clock the addressed unit is free -- so the
    // queue cannot stay full with nothing else arriving.  Holding the
    // tail one more clock is exactly the wait the comment above already
    // claims the core performs.
    Maybe#(MemReq) tailNext = storeTail;
    if (storeTail matches tagged Valid .t) begin
      if (storeQ.notFull) begin
        storeQ.enq(t);
        recentStoreReg <= tagged Valid t.addr;
        tailNext = tagged Invalid;
      end else begin
        // Keep it: tailNext stays `storeTail` and this rule tries again
        // next clock.
        //
        // AND recentStoreReg STAYS VALID WHILE THE TAIL IS HELD, which
        // is the conservative direction and not the obvious one.  A
        // first draft set it Invalid here, reasoning that "nothing was
        // stored so the compare must not claim otherwise".  THAT IS
        // BACKWARDS.  `recentStore()` is the PROGRAM STORE COMPARE
        // (StretchIBox.bsv:253): a Valid address invalidates a
        // prefetched word and rewinds the fetch stream, so Valid is the
        // safe value and Invalid means "no store touched this word".
        // The tail is still pending and WILL be written, so reporting
        // Invalid would let the I-box keep a prefetched copy of a word
        // that is about to change -- exactly the self-modifying-code
        // hazard printed p.3's channel search depends on.  Reporting it
        // every clock the tail is held costs a redundant invalidate and
        // cannot be wrong.
        recentStoreReg <= tagged Valid t.addr;
        $display("StretchStorage: store queue full, CROSSING-FIELD TAIL to %0d HELD", t.addr);
      end
      if (storeW.wget matches tagged Valid .r)
        $display("StretchStorage: write to %0d arrived while a crossing-field tail was pending and was LOST", r.addr);
    end
    else if (storeW.wget matches tagged Valid .r) begin
      if (storeQ.notFull) storeQ.enq(r);
      else $display("StretchStorage: store queue full, write to %0d LOST", r.addr);
      recentStoreReg <= tagged Valid r.addr;
    end else
      recentStoreReg <= tagged Invalid;
    if (storeTailW.wget matches tagged Valid .t2) tailNext = tagged Valid t2;
    storeTail <= tailNext;
    Bool busUsed = False;
    if (storeQ.notEmpty && mbcu.canAccept(storeQ.first.addr)) begin
      mbcu.put(storeQ.first);
      storeQ.deq;
      busUsed = True;
    end
    // Read channels, in bus priority order: the operand channel, the
    // look-ahead levels, then the instruction buffers (Buchholz §14.3) --
    // EXCEPT that a floating-point level's fetch yields to a 1Y/2Y fetch.
    //
    // >>> AN FP LOOK-AHEAD LOAD WAITS FOR THE INSTRUCTION FETCH,
    // 2026-11-17. <<<  Buchholz §14.3: "In the CPU the operand-fetch
    // mechanism, the look-ahead unit, has priority over the instruction-
    // fetch mechanism."  For floating point the built machine's CE manual
    // says the other thing, in the logic: R23-9732 (CPU 7101, 2/1/62)
    // Figure 3.1.21, "ZL FP4 TRIGGER AND ZL FP6 TRIGGER" (PDF 85, printed
    // 1-43/1-44, read in the page image), turns on FPL2E -- the floating-
    // point look-ahead load that sends the operand request -- only under
    // "NOT IC FETCH PRIORITY", and otherwise "BLOCK TYPE 2 LD TO LA".
    // Blosk, TR00.722 printed p.30 (PDF 32), describes the same cycle of
    // his Figure 6 (FP preparation): the next instruction-word fetch
    // "conflicts with the operand fetch of the lookahead load cycle.
    // Since IC controls have priority, the IC fetch is made ... The
    // lookahead load cycle holds up its fetch during this cycle".
    // SCOPED TO FP: both sources describe the FP load. The VFL pages were
    // read on 2026-11-18 (Blosk Fig. 7, PDF 34; R23-9732 Figs 3.1.1,
    // 3.1.3 and 3.1.24, PDF 63, 65 and 88) and do not settle it. No VFL
    // priority test is drawn, and the IF latch's wire "TO LA LD SEQ
    // VFL2-5" has its effect on undrawn ALD pages (docs/NEXT.md). So VFL
    // and connective levels keep Buchholz's order.
    // (A global reorder was measured first: it broke
    // decks/int_timing_bracket's interruption and moved twenty VFL pins;
    // docs/NEXT.md.)  MEASURED on the atlas (docs/atlas_oracle.md,
    // "Closing the residuals" item 13).
    Bool yWaiting = False;
    for (Integer y = 1; y <= 2; y = y + 1)
      if (chPending[y] matches tagged Valid .ya &&& !chIssued[y] &&& mbcu.canAccept(ya))
        yWaiting = True;
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
      // `!isValid(storeTail)` is the crossing-field tail's half of the
      // same ordering: `storeQ.notEmpty` is read BEFORE this clock's
      // enqueue, so without it a read could issue on the very clock
      // the tail is queued and see the head word changed and the tail
      // word not.
      //
      // >>> AND `storeW` IS THE SAME HOLE, FOR THE PLAIN STORE, WHICH
      // THIS GATE DID NOT COVER. <<<  The comment above states the
      // mechanism and then guards only the tail against it.  A store
      // arriving THIS clock lands on `storeW` and is enqueued further
      // up this very rule, so `storeQ.notEmpty` -- read before that
      // enqueue -- is False for it.  With an empty queue, a pending
      // read therefore issued to memory on the same clock as a store to
      // the same word, and read the PRE-STORE value.  A one-clock
      // window, open only when the queue happened to be empty, which is
      // why it showed up as a timing-dependent corruption rather than
      // as a reproducible wrong answer.
      //
      // MEASURED: printed p.64's REQUEST VALIDITY CHECK TABLE came out
      // of the MCP boot with four type bytes wrong, five decks said the
      // two loops that write it are correct in isolation, and the
      // corrupted bytes CHANGED when look-ahead level occupancy changed
      // -- see docs/mcp_io_tables.md and docs/spec_lookahead.md.
      //
      // `storeTailW` is included for the same reason one clock earlier:
      // a crossing field's head goes through `writeWord` and its tail
      // through `writeWordTail` in the SAME clock, so a read must not
      // slip between them either.
      Bool fpYields = (c >= 3) && chFpLevel[c - 3] && yWaiting;
      if (!busUsed && !issued && !fpYields && !storeQ.notEmpty && !isValid(storeTail)
          && !isValid(storeW.wget) && !isValid(storeTailW.wget)) begin
        if (pr matches tagged Valid .a &&& mbcu.canAccept(a)) begin
          mbcu.put(MemReq{ write: False, addr: a, data: 0, tag: fromInteger(c) });
          issued = True;
          busUsed = True;
        end
      end
      if (reqW[c].wget matches tagged Valid .a) begin
        // >>> A NEW REQUEST DISCARDS THE RESPONSE STILL HELD FOR THE OLD
        // ONE. <<<  This channel protocol is "one read outstanding at a
        // time", so a response that has not been taken by the time a
        // NEW address is requested belongs to an address nobody is
        // asking about any more, and keeping it is not conservative --
        // it is a wrong answer waiting to be collected.
        //
        // HOW IT WAS REACHED.  A look-ahead level that issues a fetch
        // and is then retired, or cancelled by `cancelAll()` on a wrong
        // branch guess, leaves its word sitting in `chResp`; nothing in
        // StretchLookAhead.bsv tells storage the level is gone.  The
        // ring then wraps, a NEW level is loaded at the same position
        // with a different `da`, issues its own `laReq`, and on the next
        // clock `collect()` sees `st.laReady(k)` already true and takes
        // the DEAD LEVEL'S WORD as its own.
        //
        // MEASURED, with the CM writeback logging its own base word:
        // the clear loop wrote word 1964 using a base of
        // 0x0000060100602540, which is WORD 1962's content -- the
        // previous level's fetch, collected by the next level at the
        // same ring position.  writeFieldWithHi's precondition is that
        // `hi` is the word most recently read AT THAT ADDRESS, and this
        // is precisely how it was being violated.  See
        // docs/mcp_io_tables.md for the bisection that found the window.
        if (isSpecialAddr(a))
          ps = tagged Valid a;
        else begin
          pr = tagged Valid a;
          issued = False;
        end
        rs = tagged Invalid;
        if (!isSpecialAddr(a)) ps = tagged Invalid;
      end
      if (c >= 3) if (fpReqW[c - 3].wget matches tagged Valid .f) chFpLevel[c - 3] <= f;
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
      addrLeftZerosCount: return composeWord7();
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
  method Action laReq(Bit#(2) lvl, WordAddr a, Bool fp);
    Bit#(3) c = 3 + zeroExtend(lvl);
    reqW[c].wset(a);
    fpReqW[lvl].wset(fp);
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
    return storeQ.notFull && !isValid(storeTail);
  endmethod

  method Action writeWordTail(WordAddr a, Word64 v);
    storeTailW.wset(MemReq{ write: True, addr: a, data: v, tag: 0 });
  endmethod

  method Bool storeTailPending();
    return isValid(storeTail);
  endmethod

  method Bool storesPending();
    return storeQ.notEmpty || isValid(storeTail);
  endmethod

  method Action writeWord(WordAddr a, Word64 v);
    case (a)
      addrZero: noAction; // writes to Zero are discarded (permanently protected)
      // Word 1's LEFT half only.  Reference Manual printed p.35: of the
      // time clock, "its setting, however, cannot be altered under
      // program control.  Any attempt to store into the right half of
      // location 1 is suppressed, and indicator AD, address invalid, is
      // turned on."  The suppression is modelled here (bits 28-63 are
      // simply not taken from v); raising AD for the attempt is not, and
      // neither is p.34's restriction of the LEFT half to SV/SC/SR/SVA
      // while disabled -- that one is enforced on the EXECUTE side, by
      // protViolates' DS check.  See bsv/README.md "Scope".
      //
      // IT IS A WIRE AND NOT AN ASSIGNMENT because the oscillator steps
      // the same register; oscillatorStep is its one writer.
      addrIntervalTimer: timerW.wset(v[63:36]);
      // WORD 2 HOLDS IA IN BITS 0-17 AND NOTHING ELSE.  Reference Manual
      // printed p.35 (PDF p.38): "Bits 0-17 of location 2 form the
      // interruption address register"; printed p.48 (PDF p.51): it
      // "contains 18 bits and has address 2.0"; pocket card X22-6533-1
      // (pcard-1.png), "2,P Interruption Address 18 0-17".  And printed
      // p.34 (PDF p.37): "Not all bit positions in locations 0-15 are
      // assigned to specific functions.  Those bit positions that are not
      // so assigned are always zero.  Information stored in these
      // positions is not recoverable" -- its one exception, the
      // programming note, is location 1's bits 19-27.  So bits 18-63 of
      // a store are dropped (decks/ia_width_18bit.strap).  Until
      // 2026-11-19 this arm kept all 64 bits.  The permanent protection
      // (printed p.31) is checked on the execute side, protViolates in
      // StretchExecute.bsv, not here.
      addrInterruptAddr: interruptionAddress <= {v[63:46], 46'b0};
      // WORD 3 HOLDS THE BOUNDARIES IN BITS 0-17, 32-49 AND 57 AND
      // NOTHING ELSE.  Reference Manual printed p.35 (PDF p.38),
      // "Address Boundaries": "The upper boundary register occupies bit
      // positions 0-17 of location 3.  The lower boundary register
      // occupies bit positions 32-49 of location 3.  The boundary
      // control bit ... is located in bit 57 of location 3."  Pocket
      // card X22-6533-1 (pcard-1.png), SPECIAL STORAGE ASSIGNMENT: "3,P
      // Upper Boundary 18 0-17", "3,P Lower Boundary 18 32-49", "3,P
      // Boundary Control Bit 1 57".  printed p.34 (PDF p.37): the bits
      // of locations 0-15 not so assigned "are always zero.  Information
      // stored in these positions is not recoverable."  So bits 18-31,
      // 50-56 and 58-63 of a store are dropped
      // (decks/boundary_width.strap).  Until 2026-11-19 this arm kept
      // all 64 bits; protViolatesEn (StretchExecute.bsv) only ever read
      // [63:46], [31:14] and [6], so only a read-back could see it.  The
      // permanent protection (printed p.31) is checked on the execute
      // side, not here.
      addrUpperBoundary: boundaryReg <= {v[63:46], 14'b0, v[31:14], 7'b0, v[6], 6'b0};
      addrMaintenanceBits: maintenanceBits <= v;
      addrChannelAddress: noAction; // read-only ("b" footnote)
      // WORD 6 HOLDS THE OTHER-CPU REGISTER IN BITS 0-18 AND NOTHING
      // ELSE.  Reference Manual printed p.35 (PDF p.38), "Other CPU
      // Bits": "the other CPU register, bits 0-18 of location 6"; pocket
      // card X22-6533-1, "6 Other CPU Bits 19 0-18"; and p.34's rule
      // that unassigned bits of locations 0-15 are always zero.  So bits
      // 19-63 of a store are dropped (decks/other_cpu_width.strap).
      // Until 2026-11-19 this arm kept all 64 bits.  A MODELLING CHOICE,
      // recorded in docs/NEXT.md: printed p.36 (PDF p.39) says the
      // register "is provided only in computers which are to be used in
      // multi-computer systems.  When not present, these bit positions
      // behave like the bit positions of address 0" -- i.e. read zero.
      // This model keeps the register PRESENT (bits 0-18 settable) and
      // signals no other computer; decks/exic_addr.strap uses bit 0 of
      // word 6 as a flag and depends on that.
      addrOtherCpuBits: otherCpuBits <= {v[63:45], 45'b0};
      // Word 7: the counters only, through commitCounts (see there).
      addrLeftZerosCount: w7StW.wset(v);
      addrAccLeft: accLeft <= v;
      addrAccRight: accRight <= v;
      addrAccSignByte: accSignByte <= {v[63:56], 56'b0};   // IBM bits 0-7: the sign byte
      // THE INDICATOR REGISTER TAKES A STORE IN BITS 20-63 (Reference
      // Manual printed p.37; pocket card X22-6533-1 footnote c, "Bit
      // positions 0-19 are read only").  It goes through a wire because
      // the instruction's own setIndicatorBits writes the same register
      // in the same clock; commitIndicators merges the two, the store
      // winning in 20-63 as p.37 says.  Until 2026-11-16 this arm was a
      // no-op (a "SIMPLIFICATION" that silently lost C22-6578 Problem
      // 3.9's ST(BU,3),$AL and MCP p.356's CM1111(BU,1),$IND.63).
      // The arms that FOLD a store into `ind` themselves (Z, BB, the
      // half-word index stores, StretchExecute.bsv) never call this.
      addrIndicators: indStW.wset(v);
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
  method Bool ioReportReady() =
    irqEn && (indicators & ioStatusMask) == 0;
  method Action ioStatus(Maybe#(Tuple2#(Bit#(5), Bit#(7))) r);
    ioW.wset(r);
  endmethod
  method Word64 readBoundaries() = boundaryReg;
  method Word64 readMask() = mask;
  method Maybe#(Tuple2#(Bit#(6), WordAddr)) interruptDue() = intDueReg;
  method Action oscillatorPulse();
    oscPulse.send();
  endmethod

  method Action setIrqEnabled(Bool e);
    irqEn <= e;
  endmethod

  method Action setIndicatorBits(Word64 v);
    indW.wset(v);   // committed by commitIndicators; see there
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
    return composeWord7();
  endmethod

  method Action setConnectiveCounts(Bit#(7) lzc, Bit#(7) aoc);
    lzcW.wset(lzc);
    aocW.wset(aoc);
  endmethod

  method Action setLeftZerosCount(Bit#(7) lzc);
    lzcW.wset(lzc);
  endmethod

  method Bit#(32) memReads() = mbcu.readCount();



endmodule

endpackage
