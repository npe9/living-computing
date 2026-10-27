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
  // A method of its own rather than writeWord, because a CONNECT TO
  // MEMORY writes its result field in the same arm through a dynamic
  // address bsc cannot prove is not word 7.  Writes the counter
  // fields and reads nothing.
  method Action setConnectiveCounts(Bit#(7) lzc, Bit#(7) aoc);

  // The left-zeros count alone, for the floating-point division
  // arms (Reference Manual printed p.94).  A method rather than a
  // writeWord to location 7, for the reason the counter registers'
  // own comment gives.
  method Action setLeftZerosCount(Bit#(7) lzc);
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
  // WORD 7 IS KEPT IN PIECES, AND ITS TWO COUNTERS HAVE EXACTLY ONE
  // WRITER EACH.  That is the whole design, and it is forced.
  //
  // The counters are set by two things -- every connective sets both
  // (Reference Manual printed pp.75-76) and the floating-point
  // division arms set the left-zeros count (p.94) -- which live in
  // different arms of execute()'s case and are therefore provably
  // exclusive.  What is NOT provable is writeWord: a CONNECT TO
  // MEMORY stores its result field through a DYNAMIC address in the
  // same arm that sets the counts, and bsc cannot see that the
  // address is not 7.  Routing the counters through writeWord at all
  // makes every connective a scheduling conflict, and no assignment
  // of CReg ports fixes it -- nine arrangements were tried and each
  // moved the conflict rather than removing it.
  //
  // SO writeWord DOES NOT WRITE THE COUNTER FIELDS.  A program that
  // stores to word 7 changes the other fifty bits and leaves the
  // counts alone.  **This is a documented simplification, not the
  // architecture** -- the manual makes location 7 an ordinary
  // addressable word -- and it is the same one this model already
  // makes for the indicator register, where writeWord(11) is a
  // no-op and the write is folded in elsewhere.  Nothing in the
  // corpus stores to word 7; MCP reads it (printed p.17's "$LZC+.3")
  // and never writes it.
  //
  // IBM bit n is model bit 63-n: 0-16 is [63:47], the left-zeros
  // count at 17-23 is [46:40], 24-43 is [39:20], the all-ones count
  // at 44-50 is [19:13], and 51-63 is [12:0].
  Reg#(Bit#(17)) zocHi  <- mkReg(0);   // IBM 0-16
  Reg#(Bit#(7))  zocLzc <- mkReg(0);   // IBM 17-23, counters only
  Reg#(Bit#(20)) zocMid <- mkReg(0);   // IBM 24-43
  Reg#(Bit#(7))  zocAoc <- mkReg(0);   // IBM 44-50, counters only
  Reg#(Bit#(13)) zocLo  <- mkReg(0);   // IBM 51-63

  function Word64 composeWord7();
    return { zocHi, zocLzc, zocMid, zocAoc, zocLo };
  endfunction
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
    indicators <= ind;
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
      // `!isValid(storeTail)` is the crossing-field tail's half of the
      // same ordering: `storeQ.notEmpty` is read BEFORE this clock's
      // enqueue, so without it a read could issue on the very clock
      // the tail is queued and see the head word changed and the tail
      // word not.
      if (!busUsed && !issued && !storeQ.notEmpty && !isValid(storeTail)) begin
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
    return storeQ.notFull && !isValid(storeTail);
  endmethod

  method Action writeWordTail(WordAddr a, Word64 v);
    storeTailW.wset(MemReq{ write: True, addr: a, data: v, tag: 0 });
  endmethod

  method Bool storeTailPending();
    return isValid(storeTail);
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
      addrInterruptAddr: interruptionAddress <= v;   // permanently protected on real HW; not enforced
      addrUpperBoundary: boundaryReg <= v;           // permanently protected on real HW; not enforced
      addrMaintenanceBits: maintenanceBits <= v;
      addrChannelAddress: noAction; // read-only ("b" footnote)
      addrOtherCpuBits: otherCpuBits <= v;
      addrLeftZerosCount: begin
                     // The counter fields are deliberately NOT
                     // written here -- see the registers' comment.
                     zocHi  <= v[63:47];
                     zocMid <= v[39:20];
                     zocLo  <= v[12:0];
                   end
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
    zocLzc <= lzc;
    zocAoc <= aoc;
  endmethod

  method Action setLeftZerosCount(Bit#(7) lzc);
    zocLzc <= lzc;
  endmethod



endmodule

endpackage
