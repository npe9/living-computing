// StretchCore.bsv
//
// Top-level IBM 7030 core: the instruction unit with its 1Y/2Y
// buffers, the four-level look-ahead, and the E-box (StretchExecute's
// mkEBox), as per-clock rules gated by the harness's `step()` clock
// enable. See docs/microarchitecture_plan.md for the staged plan this
// implements and bsv/README.md for the model's scope.

package StretchCore;

import Vector::*;
import StretchTypes::*;
import StretchStorage::*;
import StretchMemory::*;   // installed(): the address-invalid bound,
                            // which rl_xmit needs per word
import StretchIO::*;
import StretchDiskSource::*;  // DiskIndex / ArcAddr / arcWords, for the
                               // disk arms of rl_io
import StretchTapeSource::*;  // TapeWords/TapeIndex and the TapeSource
                              // interface the tape transfer now goes
                              // through; imported names are not
                              // re-exported by StretchIO, so this is
                              // needed even though StretchIO uses them
import StretchDecode::*;
import StretchExecute::*;
import StretchIBox::*;       // mkInstrBuffers, classification, iboxHazard
import StretchLookAhead::*;  // mkLookAhead
import StretchTiming::*;     // iboxCycles/eboxClocks/budgetClocks

interface StretchCore;
  // step() advances the core exactly one clock: every rule in
  // mkStretchCore is gated on the pulse it sends, so nothing moves while
  // the harness is loading storage or reading results. halted() is True
  // once an instruction has branched to its own address (the "BEW, $"
  // halt idiom, C22-6531 p.14 -- "$" is the location counter, so this
  // targets the instruction itself) and stays so until setPC. Runners
  // that assemble and load real STRAP programs poll it to stop instead
  // of using a fixed step count -- see stretch/tests/gen_tb.py, whose
  // run rule is `(!core.halted()) stepCount++` with the run latch up,
  // so the
  // step count at halt is the program's clock count on this model.
  //
  // What one clock does is the per-arm story in the rules below. Two
  // instruction kinds span several clocks in ways worth naming here:
  //
  // A progressive-indexing VFL instruction (Reference Manual p.21)
  // takes TWO clocks to complete -- the manual's own words: "An
  // operation in which progressive indexing is specified is executed in
  // two parts." The first does everything except the index-register
  // write-back and does NOT advance the PC; the second (with no new
  // instruction fetched, rl_idx_write) performs just that write and
  // then advances the PC.
  //
  // An RD or W input-output instruction (Reference Manual "IBM 7619
  // Exchange", pp.104-127) similarly takes MULTIPLE clocks: the first
  // fetches the control word, starts the transfer, and DOES advance the
  // PC (matching the manual: "the computer then proceeds to the
  // execution of the next instruction"), but every subsequent clock
  // moves exactly one more word of the block and fetches nothing new
  // until the whole block has moved -- see rl_io below and
  // StretchIO.bsv's file header for why this makes the transfer
  // synchronous from the program's point of view (no genuine CPU/IO
  // overlap) even though the real hardware overlaps them. Neither
  // mechanism can halt (a taken branch is the only way next==pc, and
  // neither progressive indexing nor an I/O transfer branches).
  // >>> THE MACHINE'S RUN LATCH, NOT A PER-CLOCK POKE FROM THE HARNESS.
  // <<<  `start` raises it, `stop` drops it, and every rule below is
  // gated on it AND on not having halted.  Reference Manual printed
  // p.34 -- "The timer runs whenever the machine is operating" -- is a
  // description of exactly this latch, which is why the oscillator
  // pulse is generated under the same gate.
  method Action start();
  method Action stop();
  method Bool   halted();    // the last clock's instruction branched to itself
  method HWordAddr getPC();
  method Action setPC(HWordAddr a);
  // Press INITIAL PROGRAM LOAD and let a unit raise a channel signal:
  // Reference Manual printed p.126.  See the method body.
  method Action iplStart();
  interface StretchStorage mem;  // direct access for test setup/inspection
  interface StretchIO io;        // simulated device access for test
                                  // setup/inspection -- see StretchIO.bsv
endinterface

(* synthesize *)
module mkStretchCore(StretchCore);
  StretchStorage st <- mkStretchStorage;
  StretchIO ioDev <- mkStretchIO;
  // Idiomatic-Bluespec rewrite step 1 (plan §1c): the execute datapath
  // as ONE shared sub-module, not a function inlined at each call site
  // (the mkFBox/mkMBox shape). Its start()/resume() call sites below are
  // mutually-exclusive arms of the rule ladder, so they share this one
  // instance's method ports. See StretchExecute's mkEBox comment.
  // (This said "the four ebox.exec call sites" and "branches of step()";
  // `exec` was the preparation probe and is gone, and step() is now a
  // run latch -- see rl_prepare and `running`.)
  EBox ebox <- mkEBox(st, ioDev);
  // Step 5b: the instruction buffers (1Y/2Y + IC controls) and the
  // four-level look-ahead are stage modules of their own
  // (StretchIBox.bsv, StretchLookAhead.bsv), the mkCPU_Stage shape;
  // the rules below orchestrate them.
  InstrBuffers ibuf <- mkInstrBuffers(st);
  LookAhead    la   <- mkLookAhead(st);
  // The harness's clock enable and the halt flag it polls (see the
  // rules section below for the contract).
  Reg#(Bool) running   <- mkReg(False);   // the run latch; see `start`/`stop`
  Reg#(Bool) haltedReg <- mkReg(False);
  Reg#(HWordAddr) pcReg <- mkReg(0);
  Reg#(Maybe#(Tuple2#(Bit#(4), IndexWord))) pendingIdxWrite <- mkReg(tagged Invalid);
  Reg#(Maybe#(IoXfer)) ioPending <- mkReg(tagged Invalid);
  // A MULTI-WORD TRANSMIT still to drain, the memory-to-memory
  // sibling of ioPending.  Reference Manual printed p.30 and
  // StretchTypes.bsv's XmitXfer; serviced by rl_xmit below.
  Reg#(Maybe#(XmitXfer)) xmitPending <- mkReg(tagged Invalid);
  // rl_xmit's own read-staging flag, the same shape as ioReadIssued:
  // the sending word is a memory READ that takes a clock to come
  // back, so the rule has to remember that it already asked.
  Reg#(Bool) xmitReadIssued <- mkReg(False);
  // SWAP's two extra states.  An exchange needs TWO reads and TWO
  // writes per word and this model has one of each per rule, so a
  // swapped word takes three clocks: read the sending word, read the
  // receiving word and write the sending word's value into it, then
  // write the receiving word's old value back into the sending word.
  // BOTH READS HAPPEN BEFORE EITHER WRITE, which is Reference Manual
  // printed p.30's "at the same time" and the only thing that makes
  // an overlapping swap an exchange rather than a propagation.
  Reg#(Bit#(2)) xmitSwapPhase <- mkReg(0);
  Reg#(Word64)  xmitSwapHeld  <- mkReg(0);
  // HOW MANY CLOCKS A SWAP COSTS, counted rather than reasoned
  // about.  The MCP boot's step count moved by 82 when forward SWAP
  // was built, and "about five clocks a word times six words" is an
  // estimate; this is the number.  Whatever is left of the 82 is MCP
  // running differently afterwards, because Q FIN's index-register
  // restore now actually happens.
  Reg#(Bit#(32)) xmitSwapClocks <- mkReg(0);

  // ---- The interruption mechanism (Ref. Manual p.48) ----
  // Valid while THE ONE instruction at the effective interruption
  // address is in flight, holding that address.  Its Validity is what
  // makes the instruction counter stand still: p.48, "the instruction
  // counter is stepped neither before nor during the execution of the
  // instruction at the effective interruption address; however, the
  // instruction counter can be replaced as the result of a successful
  // branching operation."  So pcReg is not touched while this is
  // Valid, and commitNext below makes the one decision -- branched, or
  // fell through -- in one place.
  Reg#(Maybe#(HWordAddr)) intPC <- mkReg(tagged Invalid);

  // (The 1Y/2Y buffers and their IC controls: `ibuf`, StretchIBox.bsv.)
  // Restart requests (branch taken inside step(); setPC from outside)
  // as sequence numbers, so each register has exactly one writer.
  Reg#(Bit#(8)) branchSeq  <- mkReg(0);   // written in step()'s branch paths
  Reg#(Bit#(8)) restartSeq <- mkReg(0);   // written by setPC
  Reg#(Bit#(8)) restartSeen <- mkReg(0);  // written at the top of step()
  Reg#(Bit#(8)) branchSeen  <- mkReg(0);
  // (The four-level look-ahead ring: `la`, StretchLookAhead.bsv.)
  // ---- Stage 3c (plan §6d): the not-taken guess. A branch on an
  // arithmetic indicator is loaded as a branch level; the instruction
  // unit snapshots the index words and indicators and continues down
  // the fall-through path. When the arithmetic unit reaches the level
  // the indicators are final: guess right, retire; guess wrong, cancel
  // the younger levels and, on the next clock (`recover`), restore the
  // snapshot, reset the instruction counter to the target and refetch.
  Reg#(Bool)                 guessPending <- mkReg(False);
  Reg#(Vector#(16, Word64))  xSnap        <- mkReg(replicate(0));
  Reg#(Word64)               indSnap      <- mkReg(0);
  Reg#(Maybe#(HWordAddr))    recover      <- mkReg(tagged Invalid);
  Reg#(Bit#(16)) ebusy  <- mkReg(0);       // E-box time of the last removed instruction

  // Stage 2b timing registers (the budgets: StretchTiming.bsv).
  Reg#(Bit#(32)) clk      <- mkReg(0);   // clocks since reset
  // The 1,024-per-second oscillator's divider: Bresenham on the exact
  // rational 78125/24 clocks per tick (StretchTiming.bsv's
  // oscPulseNumer/oscPulseDenom, where the derivation and the choice of
  // an exact rational over a rounded integer period are written out).
  Reg#(Bit#(17)) oscAcc   <- mkReg(0);
  Reg#(Bit#(32)) startClk <- mkReg(0);   // dispatch clock of the current instruction
  Reg#(Bit#(16)) ibusy    <- mkReg(0);   // clocks the next preparation must still wait

  // ioPending's own read-staging flag (docs/phase2_arm_inventory.md
  // conversion order, step 3): only a W-direction (memory->device)
  // word needs a genuine BRAM-eligible read (st.memAddr); RD-direction
  // (device->memory) only ever calls st.writeWord, which stays
  // single-cycle, so this flag is meaningless (and left False) for
  // RD-direction transfers. Separate Reg rather than a new IoXfer
  // field (StretchTypes.bsv) -- confined to this FSM's own bookkeeping
  // in StretchCore.bsv, same reasoning as fetchPending living here
  // rather than folded into pcReg.
  Reg#(Bool) ioReadIssued <- mkReg(False);
  // The same staging flag, for the DEVICE side of an RD-direction tape
  // transfer.  ioReadIssued stages the MEMORY read a W-direction
  // transfer needs; this one stages the TAPE read an RD-direction
  // transfer needs, now that a tape source is allowed to take time
  // (StretchTapeSource.bsv).  Two flags rather than one because the
  // two reads are on opposite sides of the transfer and a single
  // transfer never needs both.
  Reg#(Bool) ioTapeReqIssued <- mkReg(False);
  // The disk's equivalent of ioTapeReqIssued: a platter read is a
  // request and a later response, so the rule has to remember that it
  // already asked.  Separate from the tape's because a transfer is
  // one device at a time and sharing the flag would couple two
  // devices that have nothing to do with each other.
  Reg#(Bool) ioDiskReqIssued <- mkReg(False);
  // Set while a CHAINED control word is being fetched from core
  // storage.  Figure 36 (RefMan printed p.109) says that when the
  // count reaches zero with the chain flag on and the block has not
  // ended, the exchange refills the control word and continues; the
  // refill is a core-storage READ, so like every other read in this
  // rule it needs a request/wait/collect staging flag of its own.
  Reg#(Bool) ioRefillIssued <- mkReg(False);

  // ---- INITIAL PROGRAM LOAD (Reference Manual printed p.126) -------
  // iplActive is set by iplStart() and cleared when the load
  // completes.  iplEntry holds the data word address of the REFILLED
  // control word -- the one the tape's first word becomes -- captured
  // at the refill rather than read back at the end, because by then
  // the exchange's copy has walked its dataAddr past the program.
  Reg#(Bool)     iplActive <- mkReg(False);
  Reg#(WordAddr) iplEntry  <- mkReg(0);

  // (An instruction waiting on an operand read is held by the E-box
  // itself -- ebox.busy/busyFor/canResume/pending/resume, step 5c --
  // with the owner tag saying whether the instruction unit dispatched
  // it directly or the look-ahead did.)

  // THE ONE PLACE AN INSTRUCTION'S NEXT ADDRESS IS COMMITTED, so the
  // interruption's "do not step the instruction counter" rule is
  // written once rather than at each completion site.  Ordinarily this
  // is just `pcReg <= next`.  While the interruption instruction is in
  // flight it is not: p.48 says the instruction counter is not stepped
  // for it, "however, the instruction counter can be replaced as the
  // result of a successful branching operation" -- so a fall-through
  // leaves pcReg pointing where it already pointed (at the instruction
  // that had not yet run when the interruption was taken), and a taken
  // branch replaces it.
  //
  // Fall-through is recognised as "next is the address after this
  // instruction", which is exactly how the rest of this file already
  // tells a taken branch from a sequential completion (see the `taken`
  // computations below).
  //
  // IT ALSO OWNS branchSeq, the fetch-stream restart, and that is not
  // tidiness -- it is forced.  Written as a write here PLUS the callers'
  // own `if (taken) branchSeq <= ...`, bsc rejects both callers with
  // G0004, "uses methods that conflict in parallel": two writes to one
  // register from a function call and a statement beside it cannot be
  // ordered, even though two plain assignments could.  So the question
  // "did the instruction stream jump?" has to be answered in the same
  // place as "where does it go next?", which is where it belonged.
  function Action commitNext(HWordAddr pc, InstrLen len, HWordAddr next);
    action
      Bool taken = (next != pc + ((len == Full) ? 2 : 1));
      if (intPC matches tagged Valid .ip) begin
        if (taken) pcReg <= next;   // "replaced as the result of a
                                    //  successful branching operation"
        intPC <= tagged Invalid;
        // Always a restart: the stream jumps back to the instruction
        // counter, the mirror of the jump INTO the interruption.
        branchSeq <= branchSeq + 1;
      end else begin
        pcReg <= next;
        if (taken) branchSeq <= branchSeq + 1;
      end
    endaction
  endfunction

  // Dispatch a freshly decoded I-box-class instruction to the E-box
  // (no operand words yet). Either it completes in this clock,
  // committing exactly as execute() always did, or the E-box holds it
  // for its operand read and the resume arm finishes it.
  // WHAT COUNTS AS A HALT, and why a self-branch is not always one.
  //
  // `halted()` exists for the `BEW, $` idiom -- BRANCH ENABLED AND
  // WAIT to its own address -- which is how every program in this
  // corpus says it is finished, and the harness polls it to stop
  // stepping.  "Branched to its own address" is the test.
  //
  // A COUNT AND BRANCH TO ITS OWN ADDRESS IS A DELAY LOOP, NOT A
  // HALT, and MCP printed p.4 line 32 is one:
  //
  //     LCI,0,(8)377777.0        (131,071 into index 0's count)
  //     CB,0,$                   -- count down, branch to itself
  //
  // the wait after RELEASE DISK.  It branches to its own address
  // 131,071 times and then falls through, so a machine stopped there
  // has not finished: it has been interrupted mid-wait.  Before this
  // test existed the MCP boot run ended after ONE decrement, with
  // 131,070 still in the count, and everything printed pp.15-18 do
  // was unreachable behind it.
  //
  // THE DISCRIMINATOR IS THE INSTRUCTION, NOT THE STATE.  A count
  // branch makes progress by construction -- it writes the index
  // register whether or not it branches -- so no other test is
  // needed, and testing the count instead would make `halted` depend
  // on a value the decision site does not have.
  function Bool isHalt(DecodedInstr di, HWordAddr next, HWordAddr pc);
    Bool selfBranch = (next == pc);
    Bool counting = (case (di) matches
                       tagged CountBranch .*: True;
                       default: False;
                     endcase);
    return selfBranch && !counting;
  endfunction

  function ActionValue#(Bool) startExecute(HWordAddr pc, InstrLen len, DecodedInstr di,
                                           Bool atIntAddr) =
    actionvalue
      let r <- ebox.start(pc, len, di, replicate(0), 0, OwnerIbox, atIntAddr);
      startClk <= clk;
      if (r matches tagged Valid .o) begin
        commitNext(pc, len, o.next);
        pendingIdxWrite <= o.idxWrite;
        ioPending <= o.ioStart;
        xmitPending <= o.xmitStart;
        // >>> A SWAP THAT RUNS SAYS SO. <<<  The question "does any
        // program in this corpus execute a SWAP?" stayed open for
        // four commits and was answered with an indicator trail that
        // can MISS one: tests/gen_tb's op_trail counts RISING EDGES
        // of OP, and a refusal raised while OP is already high leaves
        // no edge.  This cannot be missed, and it is cheap -- it
        // prints only when a swap actually starts.
        if (o.xmitStart matches tagged Valid .xs &&& xs.swap)
          $display("StretchCore: SWAP started at half-word %0d, %0d words", pc, xs.remaining);
        Bool taken = (o.next != pc + ((len == Full) ? 2 : 1));
        ibusy <= budgetClocks(di, taken);   // completed in the dispatch clock
        return isHalt(di, o.next, pc);
      end else
        return False;
    endactionvalue;

  // =====================================================================
  // Idiomatic-Bluespec rewrite step 4 (docs/microarchitecture_plan.md
  // §1c): the instruction unit's per-clock work as RULES, not one
  // monolithic step() method. The harness no longer supplies a pulse
  // per clock at all: it raises the machine's RUN LATCH once with
  // `start()` and drops it with `stop()`, and every rule below is gated
  // on `stepping` (= `running && !haltedReg`). No rule fires while the
  // harness is loading storage or reading results, because the latch is
  // down; and a halted machine stops itself rather than waiting to stop
  // being poked.
  //
  // The rules and how they relate, cycle by cycle:
  //   rl_clock        -- the clock counter.
  //   rl_la_fetch     -- look-ahead: collect arrived operands, issue one
  //                      fetch. Every clock. Writes the levels through
  //                      CReg port 0.
  //   rl_ic_controls  -- the 1Y/2Y instruction-buffer controls. Every
  //                      clock. Reads the Y buffers the preparation arm
  //                      also reads (pre-clock values, hence ConfigReg).
  //   then exactly ONE of the six decision arms, the old if/else-if
  //   ladder, each reading the levels through CReg port 1 (i.e. AFTER
  //   this clock's operand arrivals, as the ladder did):
  //   rl_recover      -- wrong-way branch recovery.
  //   rl_io           -- one word of an in-flight RD/W transfer.
  //   rl_idx_write    -- part 2 of a progressive-indexing instruction.
  //   rl_exec_resume  -- an E-box instruction's operand read arrived.
  //   rl_au_remove    -- the arithmetic unit removes the head level.
  //   rl_prepare      -- the instruction unit prepares the next
  //                      instruction (I-box class executes here).
  // The `halted` result the harness used to get back from step() is
  // now a register the executing arms write (True iff the instruction
  // branched to its own address), read through `halted()`; the harness
  // polls it in its run rule's guard, so the step count at halt is
  // unchanged (verified by the CYCLES<= bounds in the suite).
  //
  // Same-clock ordering, made explicit where the old single method had
  // it implicitly: the levels are mkCReg(2) so rl_la_fetch's arrivals
  // (port 0) are visible to the arms (port 1); `ebusy` counts down in
  // every arm that does not set it; every other register is read in its
  // pre-clock state by every rule, as before.
  Bit#(16) eb = (ebusy != 0) ? ebusy - 1 : 0;   // E-box busy time, counting down

  Bool armRecover  = isValid(recover);
  Bool armIo       = !armRecover && isValid(ioPending);
  // A MULTI-WORD TRANSMIT BLOCKS THE SAME ARMS AN I/O TRANSFER DOES,
  // and for the same reason: it owns the storage write port for as
  // many clocks as it has words left, so nothing else may execute
  // while it drains.  It is ordered AFTER rl_io in this chain because
  // the two cannot coexist -- a transmit is started by an instruction
  // and an instruction cannot start while a transfer is draining --
  // but the ordering is written down rather than assumed.
  Bool armXmit     = !armRecover && !isValid(ioPending) && isValid(xmitPending);
  // A CROSSING VFL FIELD'S TAIL WRITE IS THE THIRD THING THAT MAKES
  // THE MACHINE BUSY, 2026-10-24.  StretchStorage's writeWordTail
  // parks the second word of the store for one clock; while it waits,
  // nothing may be armed, because a newly armed instruction's own
  // write would arrive at the store queue on the clock the tail needs
  // and one of the two would be lost.  Exactly the stall a multi-word
  // transfer gets, for exactly the reason.
  //
  // IT DOES NOT NEED TO BE IN armXmit.  A transmit and a crossing
  // store cannot overlap: a transfer blocks arming through this same
  // boolean, so no ST executes while one drains, and the clock after a
  // crossing ST nothing can be armed either -- so xmitPending cannot
  // become Valid while a tail is pending.  Written down rather than
  // assumed, as with rl_io's ordering above.
  Bool busyXfer    = isValid(ioPending) || isValid(xmitPending)
                     || st.storeTailPending();
  // >>> THE GATE IS `running` ALONE, AND `!haltedReg` IS DELIBERATELY
  // NOT IN IT. <<<  The first version of this gate was
  // `running && !haltedReg`, to stop a halted machine in the same clock
  // the old harness stopped poking it.  StretchSmoke's scheduling
  // tripwire refused it:
  //
  //     FAIL rl_exec_resume is blocked by core rule(s): rl_clock
  //     FAIL rl_prepare     is blocked by core rule(s): rl_clock
  //
  // -- because `rl_clock` would then READ `haltedReg` through its guard
  // while `rl_exec_resume` and `rl_prepare` WRITE it, so bsc must order
  // the clock ahead of them.  `tick`, being a PulseWire, carried no such
  // dependency.  A gate that silently serialises the clock against the
  // instruction unit is worse than the extra clocks it was buying.
  //
  // WHAT THE EXTRA CLOCKS COST: after the machine halts the harness
  // needs two phases to notice and drop the latch (`afterRun`, then
  // `stopRun`), so the core re-executes its halt -- a branch to its own
  // address, which stores nothing -- for those clocks.  The CYCLES
  // bounds and windows are unaffected because they assert on the
  // HARNESS's `stepCount`, which stops the moment `run`'s
  // `!core.halted()` guard goes false.

  Bool armIdx      = !armRecover && !busyXfer && isValid(pendingIdxWrite);
  Bool resumeReady = ebox.canResume();
  Bool armResume   = !armRecover && !busyXfer && !isValid(pendingIdxWrite) && resumeReady;
  // (A branch level has no operand and is removed as soon as it is the
  // head with the E-box free, i.e. once every earlier level has retired.)
  Bool headReady   = la.count() != 0 && ebusy == 0 && !ebox.busyFor(OwnerLA)
                     && (!isValid(la.headLevel().da) || isValid(la.headLevel().data));
  Bool armRemove   = !armRecover && !busyXfer && !isValid(pendingIdxWrite)
                     && !resumeReady && headReady;

  // ---- THE INTERRUPTION MECHANISM (Ref. Manual p.48) ----
  //
  // "Thus, interruption requires the mask bit to be 1, the indicator
  // bit to be 1, and the mechanism to be enabled."  All three are
  // tested inside StretchStorage, which owns all three registers, and
  // arrive here as one latched Maybe: see interruptDue() there for why
  // reading `mask` from a core rule breaks the smoke test's loader
  // rather than this file.
  Maybe#(Tuple2#(Bit#(6), WordAddr)) intDue = st.interruptDue();

  // WHEN IT FIRES.  p.48 says it twice, and the second is the sharper
  // one.  "Interruption Action": "Interruption is permitted after the
  // execution of an instruction is completed, terminated, or suppressed
  // and before execution of the next instruction" -- an INSTRUCTION
  // boundary.  "Mask Register", same page: "occurrence of the
  // corresponding condition will cause program interruption AT THE END
  // OF THE OPERATION DURING WHICH THE INDICATOR IS TURNED ON."  So the
  // interruption belongs to the operation that set the indicator, and
  // must precede the next one.
  //
  // THIS USED TO FIRE LATER, AND THE LATENESS WAS MEASURED.  The
  // condition was the same list plus `ebusy == 0`.  That is the
  // CHARGED TIME of the instruction just removed from a look-ahead
  // level -- the E-box's cycle budget, not a structural busy -- and
  // rl_prepare does NOT wait for it (it gates on `ibusy`, and a
  // retirement hands it no `ibusy`).  So every I-box instruction that
  // fitted inside the budget ran before the interruption could be
  // taken.  `la.count() == 0 && !ebox.busy()` is the structural
  // condition and it is kept; a retired instruction is functionally
  // complete, which is what p.48 asks about.
  //
  // MEASURED, on decks/int_timing_bracket.strap -- a VFL ST whose
  // store is suppressed, bracketed BE / ST / BD the way jb_ax5b routine
  // 1260 brackets every provoked interruption.  With the old condition
  // the interruption needed THREE instructions of slack before the BD
  // to be taken at all, where p.48 allows zero and the deck leaves one;
  // with fewer, the BD disabled the system first and the pending
  // interruption evaporated (StretchStorage's intDueCalc returns
  // Invalid the moment irqEn goes false).  The halt addresses, and the
  // injection that puts `ebusy == 0` back and returns the program to
  // 004110.40, are in that program's own header and in docs/NEXT.md
  // item 3.
  //
  // THE OTHER CANDIDATE WAS RULED OUT BY MEASUREMENT, not by argument.
  // interruptDue() is latched a clock behind the indicator write, and
  // that looked like a second cause; with `ebusy` already dropped, the
  // bracket program passes with the latch in place.  StretchStorage is
  // therefore untouched and its "no program can observe it" note on the
  // latch still stands.
  //
  // WHAT IS STILL NOT MODELLED.  An I-box-class instruction that the
  // I-box has already run AHEAD of a pending level is committed and
  // cannot be taken back, so an indicator set by a level is still not
  // reported before an I-box instruction that overtook it.  The
  // iboxHazard test keeps that case narrow -- every unconditional
  // branch, every branch on a non-index indicator, and every store to
  // an E-box register drains the levels first (Perf. Char. p.3-18:
  // "BD ... empty the LA completely") -- but it is not empty, and
  // closing it needs the look-ahead to be able to unwind.  Stated here,
  // in bsv/README.md and in docs/NEXT.md item 3.  (run_tests.sh's two
  // notes on interruption timing -- in the df_data_fetch_alarm section
  // and the interrupt_pg0 one -- still describe the OLD behaviour and
  // are stale.)
  Bool armInterrupt = !armRecover && !busyXfer && !isValid(pendingIdxWrite)
                      && !resumeReady && !headReady
                      && !isValid(intPC)          // one instruction, then done
                      && la.count() == 0 && !ebox.busy() && ibusy == 0
                      && isValid(intDue);
  Bool armPrepare  = !armRecover && !busyXfer && !isValid(pendingIdxWrite)
                     && !resumeReady && !headReady && !armInterrupt;

  (* fire_when_enabled *)
  rule rl_clock (running);
    clk <= clk + 1;
    // ---- THE OSCILLATOR PULSE ----
    // Reference Manual printed p.34: "The timer runs whenever the
    // machine is operating, which includes also the execution of BRANCH
    // ENABLED AND WAIT."  `stepping` IS this model's "the machine is
    // operating" signal -- a run latch the harness raises once and
    // never while it is loading the program image or reading results --
    // so the pulse is generated here rather than by a free-running rule
    // inside StretchStorage, which would count the timer down through
    // gen_tb.py's loader (one clock per word, thousands of them) and
    // hand the first instruction a timer that was already stale.  BEW
    // does not stop the clock in this model (it is a self-branch the
    // harness leaves running), so p.34's named case needs nothing extra.
    Bit#(17) acc = oscAcc + fromInteger(oscPulseNumer);
    if (acc >= fromInteger(oscPulseDenom)) begin
      acc = acc - fromInteger(oscPulseDenom);
      st.oscillatorPulse();
    end
    oscAcc <= acc;
  endrule

  // ---- Look-ahead: collect arrived operands, issue one fetch ----
  // (No fire_when_enabled on this rule or rl_ic_controls: they share the
  // look-ahead / Y-buffer bus channels with the exported `mem`
  // interface, and at the synthesized boundary bsc must assume the
  // harness could call those methods while the latch is up. It never
  // does -- it reads only between phases -- but that is a harness
  // fact, not something the scheduler can prove here.)
  rule rl_la_fetch (running);
    la.collect();
  endrule

  // ---- IC controls: run every clock, alongside the instruction FSM ----
  rule rl_ic_controls (running);
    Bool restart = (restartSeq != restartSeen) || (branchSeq != branchSeen);
    // While the interruption instruction is in flight the fetch stream
    // follows IT, not the instruction counter -- the counter is
    // deliberately standing still (p.48).
    HWordAddr fetchPC = fromMaybe(pcReg, intPC);
    ibuf.advance(fetchPC[18:1], restart);

    if (restart) begin
      restartSeen <= restartSeq;
      branchSeen <= branchSeq;
    end
  endrule

  (* mutually_exclusive = "rl_recover, rl_io, rl_idx_write, rl_exec_resume, rl_au_remove, rl_prepare" *)
  rule rl_recover (running && armRecover);
    // Wrong-way recovery (Perf. Char. p.3-23): undo the index
    // registers and index indicators the I-box changed ahead, take the
    // branch, and refetch. Charged as the branch's own execution
    // cycles again plus the refill the restart costs.
    let tgt = validValue(recover);
    st.restoreIndex(xSnap);
    Word64 ind = st.readIndicators();
    Word64 keep = ~indexIndMask;
    st.setIndicatorBits((ind & keep) | (indSnap & indexIndMask));
    pcReg <= tgt;
    branchSeq <= branchSeq + 1;
    recover <= tagged Invalid;
    ibusy <= 12;
    ebusy <= eb;
    haltedReg <= False;
  endrule

  rule rl_io (running && armIo);
    // Service one word of an in-flight RD/W transfer. See this
    // interface's step() doc above and StretchIO.bsv's file header.
    // Capacity is device-kind-dependent: the tape's TapeWords is
    // deliberately smaller than the reader/printer's DeviceWords
    // (see StretchIO.bsv) so this is where that distinction has to
    // be made, not a single shared constant.
    let x = validValue(ioPending);
    DeviceKind kind = kindOf(x.ch);
    // THE TAPE'S CAPACITY NOW COMES FROM THE SOURCE, not from a
    // typedef: a file- or SD-backed source holds a reel, and the End
    // Exception test ("the unit runs out of material", p.121) has to
    // ask it rather than assume the 16-word register image.  The
    // reader and printer are still fixed-size Vectors in StretchIO.
    Bit#(25) capacity = (kind == DevTape)
      ? zeroExtend(ioDev.tapeCapacity())
      // THE DISK'S CAPACITY COMES FROM ITS SOURCE TOO, and for the
      // same reason the tape's does: a 353 is 2^21 words (Reference
      // Manual printed p.157) and the small source in
      // StretchDiskSource.bsv is two arcs.  Running off the end is
      // End Exception, exactly as running off the end of a reel is.
      : (kind == DevDisk) ? zeroExtend(ioDev.diskCapacity())
      // THE CONSOLE HAS TWO CAPACITIES, one per direction.  A WRITE
      // walks the paper, DeviceWords of it; a READ scans the switch
      // register, and Reference Manual printed p.150 says how many
      // there are -- "a word weight of 3", and a READ "is
      // automatically terminated when the three words scanned from
      // the switches have been sent to the exchange".  A read asking
      // for more than three therefore ends on the End Exception arm
      // below, which is this model's "the unit runs out of material"
      // (p.121) and the nearest thing the manual gives to
      // "automatically terminated".  MCP asks for exactly three
      // (printed p.21 line 31's "X DCW 2  CW,X LR IN,3,0"), so
      // nothing on the boot path depends on that choice -- but
      // something had to be chosen and this says so.
      : (kind == DevConsole && !x.isWrite)
          ? fromInteger(valueOf(ConsoleSwitchWords))
      : fromInteger(valueOf(DeviceWords));
    if (ioRefillIssued) begin
      // A CHAINED CONTROL WORD IS IN FLIGHT.  This arm is first in the
      // rule on purpose: the End Exception test below looks at devIdx
      // against the device's capacity, and devIdx has already been
      // advanced past the word that exhausted the old count, so that
      // test would fire spuriously while the refill is still pending.
      if (!st.responseReady()) begin
        noAction;
      end else begin
        Word64 ncwW <- st.readWordResp();
        ControlWord n = unpackControlWord(ncwW);
        ioRefillIssued <= False;
        // p.126: "Location 4 at this time should contain another
        // control word specifying the address at which the word
        // immediately following should be stored."  That address is
        // also where the CPU starts, so capture it now, before the
        // transfer walks it forward.
        if (iplActive) iplEntry <= n.dataAddr;
        ioDev.writeChanCW(x.ch, n);
        // p.123: "If the count field in the control word is zero
        // initially, it is interpreted as 2**18."  remaining is
        // Bit#(19) for exactly this.
        ioPending <= tagged Valid IoXfer {
          ch: x.ch, isWrite: x.isWrite,
          memAddr: n.dataAddr, devIdx: x.devIdx,
          remaining: (n.count == 0) ? 19'h40000 : zeroExtend(n.count),
          suppressEop: x.suppressEop, skip: (n.skip == 1),
          untilMark: x.untilMark, zeroFill: x.zeroFill };
      end
    end else if (x.devIdx >= capacity) begin
      // "the unit runs out of material" (p.121): End Exception, not
      // Unit Check -- the block ends early; whatever was already
      // moved stays moved, and the control word reflects exactly
      // that (dataAddr/count as of the last word actually
      // transferred, since this cycle transfers nothing).
      //
      // THE ARC ADDRESS REGISTER IS DELIBERATELY NOT TOUCHED HERE,
      // and this is a judgment rather than a quotation.  Reference
      // Manual printed p.161 says where the register is left after a
      // RELEASE ("at the address of the last arc used unless
      // transmission of that arc has been completed") and says
      // NOTHING about where it is left when a transfer runs off the
      // end of the volume -- which on a real 353 means an arc address
      // beyond 4095, a state the manual does not describe because the
      // twelve-bit field cannot hold one.  Leaving the register alone
      // is the behaviour that makes a following LOCATE the only way
      // to continue, which is what a program would have to do anyway.
      // What would settle it: a disk diagnostic deck, and
      // docs/disk_subsystem.md §6 records that none exists.
      //
      // ioDiskReqIssued needs no clearing on this path.  The arm sits
      // ABOVE the request arms, so the flag is False whenever a word
      // begins, and a word that reaches here has not been requested.
      ControlWord cw = ioDev.readChanCW(x.ch);
      cw.ee = 1;
      if (!x.suppressEop) cw.eop = 1;
      cw.seop = 0;   // completion: see rl_io's other terminal arm
      ioDev.writeChanCW(x.ch, cw);
      ioPending <= tagged Invalid;
    end else if (!st.writeReady()) begin
      // The store queue is full: the exchange waits for the memory
      // bus before moving the next word (a RD-direction word is a
      // store; the W-direction path is also held so the two
      // directions keep the same per-word pacing).
      noAction;
    end else if (x.isWrite && !x.zeroFill && !ioReadIssued) begin
      // W-direction (memory->device), first visit to this word:
      // issue the read request and wait. ioPending/x are left
      // untouched (same devIdx/memAddr/remaining next call), so the
      // NEXT call's `x` still names this same word once the
      // response is ready.
      st.readWordReq(x.memAddr);
      ioReadIssued <= True;
    end else if (x.isWrite && !x.zeroFill && !st.responseReady()) begin
      // W-direction: the memory read is in flight; wait for it.
      noAction;
    end else if (kind == DevDisk && !x.isWrite && !ioDiskReqIssued) begin
      // RD-direction disk, first visit to this word.  Same two-arm
      // request/wait shape as the tape below, and for the same
      // reason: a real platter is not combinational and an SD-backed
      // source will be many clocks.
      //
      // NO SKIP ARM HERE.  Printed p.158: the disk "makes no use of
      // control word flag bits", and StretchExecute zeroes skip in
      // the control word the synchronizer adopts, so x.skip is always
      // False on a disk transfer.
      ioDev.diskReadReq(truncate(x.devIdx));
      ioDiskReqIssued <= True;
    end else if (kind == DevDisk && !x.isWrite && !ioDev.diskRespReady()) begin
      noAction;
    end else if (kind == DevTape && !x.isWrite && !x.skip
                 && !ioTapeReqIssued) begin
      // RD-direction tape, first visit to this word: ask the tape
      // source for it and wait.  As with the W-direction memory read
      // above, ioPending/x are left untouched, so the next call's `x`
      // still names this same word.
      //
      // Under SKIP no request is issued at all: p.107's flag
      // suppresses the core-storage write, and with nothing to store
      // there is nothing to fetch -- the position still advances
      // below, which is the part the manual does require.
      ioDev.tapeReadReq(truncate(x.devIdx));
      ioTapeReqIssued <= True;
    end else if (kind == DevTape && !x.isWrite && !x.skip
                 && !ioDev.tapeRespReady()) begin
      // RD-direction tape: the device read is in flight; wait for it.
      // A register-backed source makes this one clock.  An SD-backed
      // one will make it many, and the point of the arm is that
      // nothing above here has to care.
      noAction;
    end else begin
      // Either RD-direction (tape response now ready to collect, or a
      // reader/printer, which are still combinational) or W-direction
      // with the memory read response now ready to collect.
      // Set by the tape branch below when the word it just
      // collected IS a tape mark.  A LOCAL, not a register: a
      // register written here would not be readable until the next
      // clock, and the termination test twenty lines down has to see
      // it in THIS rule firing.
      Bool markJustRead = False;
      if (kind == DevDisk) begin
        DiskIndex di = truncate(x.devIdx); // safe: checked against
                                            // diskCapacity above
        if (x.isWrite) begin
          if (x.zeroFill) begin
            // THE TAIL OF A SHORT WRITE, printed p.160.  No core read
            // was issued for this word (the two W-direction arms
            // above skip themselves when zeroFill is set), so there
            // is no response to collect and nothing to collect it
            // from -- this phase writes zeros and advances, full stop.
            ioDev.writeDiskWord(di, 64'd0);
          end else begin
            Word64 v <- st.readWordResp();
            ioDev.writeDiskWord(di, v);
          end
        end else begin
          Word64 dv <- ioDev.diskReadResp();
          st.writeWord(x.memAddr, dv);
        end
      end else if (kind == DevTape) begin
        TapeIndex ti = truncate(x.devIdx); // safe: confirmed < TapeWords above
        if (x.isWrite) begin
          Word64 v <- st.readWordResp();
          ioDev.writeTapeWord(ti, v);
        end else if (!x.skip) begin
          Word64 tv <- ioDev.tapeReadResp();
          // A SPACE FILE READS AND DISCARDS.  It has to read -- that
          // is how it sees the mark -- but it is a CONTROL operation
          // and moves nothing into core.  SKIP suppresses the store
          // without issuing the read at all; this suppresses the
          // store while still issuing it, which is a different thing
          // and is why it is not spelled as SKIP.
          if (!x.untilMark) st.writeWord(x.memAddr, tv);
          markJustRead = (tv == tapeMarkWord);
        end
        // Tape position PERSISTS across instructions (StretchIO.bsv
        // "TAPE POSITION"), unlike the reader/printer's devIdx which
        // is always instruction-local -- so unlike the reader/printer
        // branch below, tape also has to write its position back
        // every cycle, not just at the end of the transfer. Advances
        // even under SKIP: the manual says the flag only suppresses
        // the core-storage write, not the device's own motion.
        ioDev.setTapePos(truncate(x.devIdx + 1));
      end else begin
        DeviceIndex di = truncate(x.devIdx); // safe: confirmed < DeviceWords above
        if (x.isWrite) begin
          Word64 v <- st.readWordResp();
          // THE CONSOLE PRINTER AND THE PRINTER STAND-IN DIFFER IN
          // ONE THING: the console keeps its place across
          // instructions (StretchIO.bsv's consolePos), because a
          // console does not restart at the top of the page for each
          // message and MCP writes one message as a chain of control
          // words.
          if (kind == DevConsole) begin
            ioDev.writeConsoleWord(di, v);
            ioDev.setConsolePos(truncate(x.devIdx + 1));
          end else
            ioDev.writePrinterWord(di, v);
        end else if (kind == DevConsole) begin
          // THE CONSOLE'S READ SIDE SCANS THE SWITCHES, and it had to
          // be its own arm: without this the `else` below served a
          // console READ out of the CARD READER's image and moved the
          // card reader's cursor, which was measured on 2026-10-22 as
          // the injection for this very change -- the control word
          // came back with a data word address of X LR IN + 3 and no
          // status bit at all.
          //
          // Reference Manual printed p.150: "A READ instruction
          // received by the console with the keyboard not enabled is
          // automatically terminated when the three words scanned
          // from the switches have been sent to the exchange."
          //
          // NOTHING ADVANCES.  They are SCANNED, so a second READ
          // gets the same three words; the bound is the capacity test
          // above, not a cursor.  SKIP is honoured the way every
          // other READ honours it (p.107: the flag suppresses the
          // core-storage write, not the device).
          if (!x.skip)
            st.writeWord(x.memAddr, ioDev.consoleSwitchWord(truncate(x.devIdx)));
        end else begin
          if (!x.skip)
            st.writeWord(x.memAddr, ioDev.readerWord(di));
          // THE CARD FEEDS whether or not the word was stored: SKIP
          // suppresses the core-storage write, not the device's own
          // motion, which is exactly the rule the tape branch above
          // already follows.  StretchIO.bsv "CARD FEED".
          ioDev.setReaderPos(truncate(x.devIdx + 1));
        end
      end
      // else: SKIP flag set on a READ (p.107) -- the device cursor
      // and memory address still advance below exactly as if the
      // word had been transferred, but core storage is left
      // untouched for this word.
      ioReadIssued <= False;
      ioTapeReqIssued <= False;
      ioDiskReqIssued <= False;
      Bit#(19) rem1 = x.remaining - 1;
      // ONE PAST THE WORD JUST MOVED, and its offset inside its arc.
      // Both are needed twice below -- to decide whether a short disk
      // WRITE still owes its arc a zero-filled tail (printed p.160)
      // and to park the arc address register where printed p.161 says
      // successive arcs leave it.
      Bit#(25) nxtIdx = x.devIdx + 1;
      Bit#(9)  arcOff = nxtIdx[8:0];
      ControlWord cw = ioDev.readChanCW(x.ch);
      // A SPACE FILE moves no data, so it leaves the control word's
      // data address and count alone; RD and W walk both forward.
      // SO DOES A ZERO FILL: the fill is not data, and a count that
      // included it would tell the program it had written more than
      // it asked to.
      if (!x.untilMark && !x.zeroFill) begin
        cw.dataAddr = x.memAddr + 1;
        cw.count = truncate(rem1);
      end
      if (x.untilMark && markJustRead) begin
        // SPACE FILE, p.132: "forward past a tape mark; EE and EOP
        // given".  The position is already one past the mark -- the
        // setTapePos above advances every cycle -- so all that is
        // left is the status the bootstrap tests.  MCP printed p.3
        // lines 45-47 wait for SEOP to clear, REQUIRE EE, and require
        // EPGK clear, then REL(SEOP) to clear EE and EOP again.
        //
        // EE ON A NORMAL COMPLETION is p.132's wording and MCP's own
        // control flow agreeing: "EE and EOP given" attaches End
        // Exception to the FUNCTION, and printed p.3 line 46's
        // BZBZ,X IPL BS+.21 branches to "ERROR IN SPACING" when EE is
        // ZERO.  MCP would not require an error condition to proceed.
        cw.ee = 1;
        if (!x.suppressEop) cw.eop = 1;
        cw.seop = 0;
        ioDev.writeChanCW(x.ch, cw);
        ioPending <= tagged Invalid;
      end else if (x.untilMark) begin
        // Not a mark: keep going, and do NOT let the count run out.
        ioPending <= tagged Valid IoXfer {
          ch: x.ch, isWrite: x.isWrite, memAddr: x.memAddr,
          devIdx: x.devIdx + 1, remaining: 19'h40000,
          suppressEop: x.suppressEop, skip: x.skip, untilMark: True,
          zeroFill: False };
      end else if (rem1 == 0 && kind == DevDisk && x.isWrite
                   && !x.zeroFill && arcOff != 0) begin
        // THE SHORT WRITE OWES ITS ARC A TAIL.  Reference Manual
        // printed p.160: "The data written need not be a multiple of
        // the number of words contained in an arc.  In this case,
        // however, the remainder of the last arc will be
        // automatically filled with zeros."
        //
        // The data phase is over -- its control word is written out
        // here, unchanged from here on -- and the transfer continues
        // in fill mode for the (512 - arcOff) words left in the arc.
        // Nothing is read from core during it and the control word is
        // not touched again, so a COPY CONTROL WORD afterwards shows
        // the data the program asked for and not the fill.
        ioDev.writeChanCW(x.ch, cw);
        ioPending <= tagged Valid IoXfer {
          ch: x.ch, isWrite: True, memAddr: x.memAddr,
          devIdx: nxtIdx,
          remaining: 19'd512 - zeroExtend(arcOff),
          suppressEop: x.suppressEop, skip: False,
          untilMark: False, zeroFill: True };
      end else if (rem1 == 0 && cw.chain == 1) begin
        // FIGURE 36, printed p.109, row (multiple 0, chain 1, count
        // zero, end of block NO): "Chain and continue".  This model
        // has no record structure yet, so it never reports end of
        // block -- which is exactly the row IPL needs, and is why
        // chaining can be built before records (docs/NEXT.md 5k).
        // The row it gets wrong is (0,0,0,No), "Disconnect, then end
        // op.", where a real end of block would give "End operation":
        // a difference in whether a disconnect signal is sent, not in
        // whether the transfer completes.
        //
        // This is THE IPL BLOCKER.  RefMan printed p.126's fixed
        // control word is chain 1, count 1, refill 4: it reads one
        // word off the tape into location 4, and "since the fixed
        // control word is then exhausted, its refill address causes
        // the next control word to be fetched from location 4" --
        // which is the word just read, MCP's own CW(CR).  With chain
        // ignored the machine read that one word and stopped.
        st.readWordReq(zeroExtend(cw.refill));
        ioRefillIssued <= True;
        ioDev.writeChanCW(x.ch, cw);
        // ioPending stays valid so the refill arm above resumes; its
        // remaining/memAddr are placeholders, overwritten from the
        // new control word when it arrives.
        ioPending <= tagged Valid IoXfer {
          ch: x.ch, isWrite: x.isWrite, memAddr: x.memAddr + 1,
          devIdx: x.devIdx + 1, remaining: 0,
          suppressEop: x.suppressEop, skip: x.skip,
          untilMark: x.untilMark, zeroFill: x.zeroFill };
      end else if (rem1 == 0) begin
        if (!x.suppressEop) cw.eop = 1;
        // THE ARC ADDRESS REGISTER, printed p.161: "Associated with
        // each disk is an arc address register.  As successive arcs
        // are used, this register is increased by one for each arc."
        // Parking it at nxtIdx >> 9 gives both halves of that in one
        // expression: an arc that was completed leaves the register
        // on the NEXT arc, and an arc only partly used leaves it on
        // ITSELF -- which is also what p.161's RELEASE rule describes
        // ("left at the address of the last arc used unless
        // transmission of that arc has been completed").  After a
        // zero-filled WRITE the index is arc-aligned by construction,
        // so a short write still advances a whole arc, which is what
        // "the remainder of the last arc will be automatically filled"
        // means for the arc after it.
        if (kind == DevDisk) ioDev.setArcAddr(truncate(nxtIdx >> 9));
        // THE SEOP STATUS BIT IS CLEARED AT COMPLETION, and this half
        // of the rule is NOT a quotation.  Reference Manual p.121 was
        // read whole: it says the bit is set when an SEOP instruction
        // is given, and says nothing about clearing it.  What settles
        // it is that IBM's own code cannot work otherwise.  MCP's
        // bootstrap, printed p.3 line 45, prints
        //     000076.00  000041.30 80  000074.34 02
        //                              BB,X IPL BS+.24,X 8 1
        // which this assembler reproduces bit-for-bit, so the
        // instruction is BB -- branch when the bit is ONE
        // (strap/opcodes.py BB_CODES) -- and its target is the CCW two
        // rows above.  The loop therefore spins while bit 24 is set.
        // Without a clear it never terminates.  ka_ul1's tape-write
        // routine is a second, independent witness.  Usage-based
        // evidence, recorded as such in docs/NEXT.md 5o.
        cw.seop = 0;
        ioDev.writeChanCW(x.ch, cw);
        ioPending <= tagged Invalid;
        // ---- the initial-start signal, p.126 steps 4 and 5 --------
        // "the exchange sends an initial start signal to the
        // computer... The computer, upon receipt of the initial-start
        // signal, fetches and executes the instruction in the location
        // specified by the data word address field of the control word
        // in core storage location 4."
        //
        // A DOCUMENTED DEPARTURE.  p.126 continues: "The address of
        // this instruction, however, is NOT placed in the instruction
        // counter."  This sets the PC to it anyway.  The difference is
        // unobservable for any legal IPL program, because the same
        // page requires that "the first instruction of a program
        // loaded by means of the initial program loading technique
        // must be BRANCH DISABLED" -- a BD replaces the instruction
        // counter itself, so what the PC held beforehand cannot
        // matter.  MCP's bootstrap obeys this: printed p.2 line 24 is
        // "X IPL BS  BD,X BEGIN  -DISABLE AND START IPL".  Modelling
        // the true rule needs the EX subject-swap in mkEBox.resume()
        // and buys nothing until a program breaks the requirement.
        if (iplActive) begin
          pcReg     <= {iplEntry, 1'b0};
          iplActive <= False;
        end
      end else begin
        ioDev.writeChanCW(x.ch, cw);
        ioPending <= tagged Valid IoXfer {
          ch: x.ch, isWrite: x.isWrite, memAddr: x.memAddr + 1,
          devIdx: x.devIdx + 1, remaining: rem1,
          suppressEop: x.suppressEop, skip: x.skip,
          untilMark: x.untilMark, zeroFill: x.zeroFill };
      end
    end
    ebusy <= eb;
    haltedReg <= False;
  endrule

  rule rl_xmit (running && armXmit);
    // Service one word of an in-flight multi-word TRANSMIT.  This is
    // rl_io's shape with the device taken out: a storage read, then a
    // storage write of what came back, one word per clock, because
    // this model writes storage once per rule.
    //
    // THE SPEC IS Reference Manual printed p.30 and the whole of it
    // fits in this rule.  "In forward transmission, the sending and
    // receiving addresses of each successive word transmitted are
    // obtained by incrementing the previous addresses by one."  There
    // is no count to write back and no indicator to fold -- same
    // page: "The count field in the index register is not changed as
    // a result of the operation, and the index result indicators are
    // not affected."  The first word was moved by the Transmit arm in
    // StretchExecute; this drains the rest.
    //
    // PROTECTION IS CHECKED PER WORD, which is the one place this
    // rule does more than copy.  p.30 says an invalid or protected
    // address is "not detected... until the data transmission
    // actually encounters" it, so a transmit that walks into a
    // protected word must stop THERE, with the words before it moved
    // -- not be refused up front.  protViolates is the same test the
    // single-word arm uses; DS terminates the operation (p.32,
    // "storing in core storage is always suppressed, AND THE
    // OPERATION IS ALWAYS TERMINATED").
    //
    // ADDRESS INVALID IS CHECKED PER WORD TOO, and it is not optional
    // -- it is the only thing that bounds a runaway transmit.  p.30,
    // on a direct count field of zero: "A count field of zero is
    // interpreted as 2^18.  Since this many words cannot be
    // transmitted without encountering an invalid address, such a
    // count is never valid.  IT IS NOT DETECTED, HOWEVER, UNTIL THE
    // DATA TRANSMISSION ACTUALLY ENCOUNTERS AN INVALID OR PROTECTED
    // ADDRESS."  So the manual's own answer to "what stops a 2^18
    // transmit" is this check, and a model without it does not merely
    // miss an indicator: 2^18 words is the WHOLE 18-bit address
    // space, so the copy wraps and zeroes every word of core.  That
    // is exactly what happened the first time this rule ran against
    // MCP, whose tape carries no PROSA, so the dictionary it reads
    // the count out of is zeros.
    //
    // `installed` is StretchMemory's bound, the same one the Z arm
    // uses for AD (RefMan printed p.21: "an effective word address...
    // which does not correspond to a core storage location that is
    // physically available").  Both ends are tested: a transmit can
    // run off the top reading as easily as writing.
    let x = validValue(xmitPending);
    // THE NEXT PAIR, written once here because three places want it.
    // p.30: forward obtains each successive pair of addresses "by
    // incrementing the previous addresses by one", backward "by
    // decrementing".
    XmitXfer nextWord = XmitXfer {
      src: x.backward ? x.src - 1 : x.src + 1,
      dst: x.backward ? x.dst - 1 : x.dst + 1,
      remaining: x.remaining - 1, backward: x.backward, swap: x.swap };
    // ONE WRITE, AT THE END OF THE RULE.  Bluespec refuses two
    // Reg writes it cannot order ("methods that conflict in
    // parallel"), so the count is carried in a variable and stored
    // once below.
    Bit#(32) swapClk = xmitSwapClocks + (x.swap ? 1 : 0);
    if (!st.writeReady()) begin
      // The store queue is full: wait for the memory bus, the same
      // way rl_io does.
      noAction;
    end else if (x.swap && xmitSwapPhase == 2) begin
      // PHASE 2: no read.  The receiving word's OLD contents, held
      // since phase 1, go back into the sending word -- the second
      // half of p.30's exchange.  Both ends were checked in phase 0.
      st.writeWord(x.src, xmitSwapHeld);
      xmitSwapPhase <= 0;
      if (x.remaining == 1) begin
        $display("StretchCore: SWAP finished, %0d clocks in rl_xmit",
                 swapClk);
        swapClk = 0;
        xmitPending <= tagged Invalid;
      end else
        xmitPending <= tagged Valid nextWord;
    end else if (!xmitReadIssued) begin
      // PHASE 0 reads the SENDING word, phase 1 the RECEIVING one.
      st.readWordReq((x.swap && xmitSwapPhase == 1) ? x.dst : x.src);
      xmitReadIssued <= True;
    end else if (!st.responseReady()) begin
      noAction;
    end else begin
      Word64 v <- st.readWordResp();
      xmitReadIssued <= False;
      // >>> A SWAP WRITES BOTH ENDS, so BOTH are protection-checked,
      // and both are checked in phase 0 -- before anything has been
      // written for this word -- so a refused pair leaves the words
      // before it moved and this one untouched.  p.30 on an invalid
      // or protected address: it is "not detected... until the data
      // transmission actually encounters" it.
      Bool protBad = protViolates(st, x.dst)
                     || (x.swap && protViolates(st, x.src));
      if (!installed(x.src) || !installed(x.dst)) begin
        st.setIndicatorBits(setBit(st.readIndicators(), ind_AD, 1));
        xmitPending <= tagged Invalid;
        xmitSwapPhase <= 0;
      end else if (protBad) begin
        st.setIndicatorBits(setBit(st.readIndicators(), ind_DS, 1));
        xmitPending <= tagged Invalid;
        xmitSwapPhase <= 0;
      end else if (x.swap && xmitSwapPhase == 0) begin
        // PHASE 0: the sending word is in hand and NOTHING is written
        // yet.  p.30's "at the same time" is this: the receiving word
        // must still be readable when phase 1 asks for it.
        xmitSwapHeld <= v;
        xmitSwapPhase <= 1;
      end else if (x.swap) begin
        // PHASE 1: `v` is the RECEIVING word.  Write the sending
        // word's value into it and keep `v` for phase 2.
        st.writeWord(x.dst, xmitSwapHeld);
        xmitSwapHeld <= v;
        xmitSwapPhase <= 2;
      end else begin
        st.writeWord(x.dst, v);
        xmitPending <= (x.remaining == 1) ? tagged Invalid
                                          : tagged Valid nextWord;
      end
    end
    xmitSwapClocks <= swapClk;
    ebusy <= eb;
    haltedReg <= False;
  endrule

  rule rl_idx_write (running && armIdx);
    // Part 2 of a progressive-indexing instruction: nothing was
    // fetched this call, and PC already advanced on part 1.
    let p = validValue(pendingIdxWrite);
    st.writeIndex(tpl_1(p), tpl_2(p));
    pendingIdxWrite <= tagged Invalid;
    ebusy <= eb;
    haltedReg <= False;
  endrule

  rule rl_exec_resume (running && armResume);
    // The E-box's held instruction gets its operand word: let the box
    // collect it and re-run (it may bail again for a second word);
    // on completion, retire the level or advance the instruction
    // counter according to who dispatched it.
    let ep = ebox.pending();
    HWordAddr pc       = tpl_1(ep);
    InstrLen len        = tpl_2(ep);
    DecodedInstr di     = tpl_3(ep);
    Bool fromLA = ebox.busyFor(OwnerLA);
    Bit#(16) ebn = eb;
    Bool done = False;
    let r <- ebox.resume();
    if (r matches tagged Valid .o) begin
      pendingIdxWrite <= o.idxWrite;
      ioPending <= o.ioStart;
      xmitPending <= o.xmitStart;
      if (o.xmitStart matches tagged Valid .xs &&& xs.swap)
        $display("StretchCore: SWAP started at half-word %0d, %0d words", pc, xs.remaining);
      if (fromLA) begin
        // A look-ahead level's instruction finished: retire it.
        ebn = eboxClocks(di);
        la.retireHead();
      end else begin
        commitNext(pc, len, o.next);
        Bool taken = (o.next != pc + ((len == Full) ? 2 : 1));
        Bit#(32) elapsed = clk - startClk;
        Bit#(16) budget = budgetClocks(di, taken);
        ibusy <= (elapsed >= zeroExtend(budget)) ? 0 : budget - truncate(elapsed);
        done = isHalt(di, o.next, pc);
      end
    end
    ebusy <= ebn;
    haltedReg <= done;
  endrule

  rule rl_au_remove (running && armRemove);
    // Remove the head level into the arithmetic unit: its operand
    // (if any) is present, so the E-box runs with it pre-supplied;
    // any further read it needs, the box holds it for (resume arm).
    Bit#(16) ebn = eb;
    LaLevel h = la.headLevel();
    Vector#(2, Word64) pf = replicate(0);
    Bit#(2) cnt = 0;
    if (h.data matches tagged Valid .d) begin pf[0] = d; cnt = 1; end
    let r <- ebox.start(h.pc, h.len, h.di, pf, cnt, OwnerLA, False);
    if (h.branch) begin
      // The guessed branch, now with final indicators (a branch never
      // waits on an operand, so the result is here).
      let o = validValue(r);
      Bool taken = (o.next != h.pc + ((h.len == Full) ? 2 : 1));
      guessPending <= False;
      if (taken) begin
        // Wrong guess: cancel every younger level, recover next clock.
        la.cancelAll();
        recover <= tagged Valid o.next;
      end else
        la.retireHead();
      ebn = 2 * 6;   // Blosk fig.10: decode + five execution cycles
    end else if (r matches tagged Valid .o) begin
      pendingIdxWrite <= o.idxWrite;
      ioPending <= o.ioStart;
      xmitPending <= o.xmitStart;
      if (o.xmitStart matches tagged Valid .xs &&& xs.swap)
        $display("StretchCore: SWAP started at half-word %0d, %0d words", h.pc, xs.remaining);
      ebn = eboxClocks(h.di);
      la.retireHead();
    end
    // else: the E-box holds the level's instruction for its operand read.
    ebusy <= ebn;
    haltedReg <= False;
  endrule

  // Take the interruption.  Which indicator and which address were
  // decided in StretchStorage's intDueCalc (leftmost masked indicator;
  // EIA = interruption address + N, in WORDS, p.48); what is left here
  // is the part that belongs to the instruction unit -- turn that
  // indicator off, point the fetch stream at the routine, and stop the
  // instruction counter.
  rule rl_interrupt (running && armInterrupt);
    let {n, eia} = validValue(intDue);

    // "After this leftmost indicator has been turned off" -- and only
    // that one: the rest of the masked set stays on and interrupts
    // again, in priority order, before the instruction counter's own
    // next instruction runs (p.48's programming note).
    st.setIndicatorBits(setBit(st.readIndicators(), n, 0));

    HWordAddr epc = {eia, 1'b0};
    intPC <= tagged Valid epc;
    // The instruction stream jumps, so the Y buffers must refill from
    // the new address.  That is what branchSeq does for a taken branch
    // (rl_ic_controls turns a change into `restart`), and an
    // interruption is the same discontinuity: nothing else in this
    // model reaches forward to fetch an address of its own.
    branchSeq <= branchSeq + 1;

    // p.48: the fetch of THIS instruction cannot turn on IF "even
    // though it might lie in the protected area of core storage".
    // Nothing to do here -- IF is not implemented at all (see
    // StretchExecute's protViolates) -- but when it is, this is the
    // fetch that must be exempt.

    // The charged time of the instruction just removed from a level
    // keeps draining across this clock, exactly as it does in every
    // other arm: taking the interruption early (see armInterrupt above)
    // must not also stop the clock the E-box was charged.  Before that
    // change this rule could not fire while `ebusy != 0`, so it never
    // had to decrement it.
    //
    // NOTHING IN THE SUITE TESTS THIS LINE, and that is said here
    // rather than left to be discovered.  No injection removes it, and
    // none could be caught: the three CYCLES<= benchmarks never enable
    // the interruption system, and every test that does interrupt
    // checks a halt address rather than a clock count.
    ebusy <= eb;
  endrule

  rule rl_prepare (running && armPrepare);
    // Preparation: transfer the next instruction from the Y buffers
    // (both halves of a full-word instruction, which may straddle
    // 1Y/2Y); an E-box-class instruction is loaded into a look-ahead
    // level, an I-box-class one executes here once the levels have
    // drained. Stall until the word(s) are buffered and checked.
    Vector#(4, LaLevel) nl = la.levels();
    Bool done = False;
    // While the interruption instruction is in flight, THAT is the
    // instruction being prepared; pcReg is left pointing at the
    // instruction the interruption displaced (p.48).
    HWordAddr pc = fromMaybe(pcReg, intPC);
    Maybe#(Tuple2#(InstrLen, DecodedInstr)) prepared = tagged Invalid;
    if (ibuf.lookup(pc[18:1]) matches tagged Valid .w0) begin
      HalfWord32 hw0 = (pc[0] == 0) ? w0[63:32] : w0[31:0];
      InstrLen len = instrLen(hw0);
      if (len == Half)
        prepared = tagged Valid tuple2(len, decode(hw0, tagged Invalid));
      else begin
        HWordAddr pc1 = pc + 1;
        if (ibuf.lookup(pc1[18:1]) matches tagged Valid .w1) begin
          HalfWord32 hw1 = (pc1[0] == 0) ? w1[63:32] : w1[31:0];
          prepared = tagged Valid tuple2(Full, decode(hw0, tagged Valid hw1));
        end
      end
    end
    Bool progressivePending = False;
    for (Integer k = 0; k < 4; k = k + 1)
      if (nl[k].valid && hasProgressive(nl[k].di)) progressivePending = True;
    if (ebox.busyFor(OwnerIbox))
      noAction;             // an I-box instruction is waiting on its operand read
    else if (ibusy != 0)
      ibusy <= ibusy - 1;   // previous instruction's time budget still running
    else if (!st.writeReady())
      noAction;   // a storing instruction could find the queue full: wait
    else if (prepared matches tagged Valid {.len, .di}
             &&& isEboxClass(di) &&& isValid(intPC)) begin
      // NOT IMPLEMENTED, and loud about it.  An interruption
      // instruction that is E-box class would have to be loaded into a
      // look-ahead level, and a level steps the instruction counter --
      // the one thing p.48 forbids here.  Real interruption tables hold
      // branches and SIC (p.48-49: "a subroutine entered by STORE-
      // INSTRUCTION-COUNTER-IF-BRANCH-DISABLED and returned by BRANCH
      // ENABLED"), all I-box class, so this is a bound on the model
      // rather than on the machine.  Treated as a fall-through so the
      // program keeps running and its own check fails, instead of
      // silently stepping the counter.
      $display("StretchCore: interruption instruction at %0d is E-box class -- not implemented", pc);
      commitNext(pc, len, pc + ((len == Full) ? 2 : 1));
    end
    else if (prepared matches tagged Valid {.len, .di} &&& isEboxClass(di)) begin
      if (la.count() < 4 && !progressivePending) begin
        // ONE derivation of this instruction's addresses, used for both
        // the operand read below and the level's storeAddr further
        // down -- see StretchIBox's prepareExec.
        let prep = prepareExec(st, di);
        Maybe#(WordAddr) da = tagged Invalid;
        if (fetchesOperand(di) && !prep.completesWithoutFetch)
          da = prep.operandAddr;
        // >>> THE PROBE IS GONE, 2026-10-29. <<<  This used to call
        // `ebox.exec` with no operands so that `execute()` would bail
        // out with the address it wanted, and then treat a non-bail as
        // "classified as fetching but completed" and commit the
        // instruction inline.  Execution was therefore both a
        // supposedly side-effect-free query and the operation that
        // commits architectural effects, and every arm had to do no
        // irreversible work before noticing an operand was missing --
        // a contract no type enforced.
        //
        // Both of the probe's answers are now pure, and both were
        // PROVEN against it across the whole corpus before it was
        // removed (docs/ebox_roadmap.md):
        //
        //   the ADDRESS      -- `prep.operandAddr`, not one
        //                       disagreement in 5621 checks;
        //   "ALREADY DONE"   -- `prep.completesWithoutFetch`, zero
        //                       disagreements in 5621 checks, with its
        //                       six causes enumerated by measurement:
        //                       the decimal refusal, progressive with
        //                       index 0, M+/CM crossing a word
        //                       boundary, DF suppression, and AD.
        //
        // An instruction that will finish without reading now simply
        // gets a level with NO operand address, exactly like ST and
        // every other non-fetching E-box instruction, and is dispatched
        // through `ebox.start()` in the ordinary way.  The inline
        // completion path and its "classification mismatch" message are
        // gone with it -- there is no longer a classification to
        // mismatch.
        begin
          // Store-close-to-fetch (plan stage 3a note): if this level
          // fetches word `a`, wait for the NEWEST earlier level that
          // stores to `a` -- every current level is program-earlier
          // than this new one (the tail), and they retire head-first, so
          // waiting for the newest such store covers all older ones.
          //
          // The same wait covers a fetch of one of the E-BOX's OWN
          // registers -- words 7-15, the zeros/ones counts, the
          // accumulator and its sign byte, the indicators, mask,
          // remainder and factor. storeTarget() reports only stores to
          // storage, deliberately: an FP load or add writes the
          // accumulator, not memory. But a VFL or connective
          // instruction may ADDRESS those words, and then the value it
          // wants is one an unretired earlier level is still going to
          // write. There is no address to compare against, so any
          // level fetching 7-15 waits for the newest earlier level,
          // whatever that level does -- the E-box on the real machine
          // is one unit and cannot hand out its accumulator ahead of
          // the operation still in it. Found by jb_af1c F207C1:
          // DL(U),FPK1 immediately followed by CT0011(BU,3),10.5,
          // which read the sign byte as it was BEFORE the load zeroed
          // its flag bits; three half-words of separation and the same
          // pair passes.
          Maybe#(Bit#(2)) wf = tagged Invalid;
          if (da matches tagged Valid .a) begin
            Bool wfound = False;
            for (Integer i = 0; i < 4; i = i + 1) begin
              Bit#(2) pos = la.tail() - 1 - fromInteger(i);
              Bool hz = nl[pos].valid
                        && ((isValid(nl[pos].storeAddr) && validValue(nl[pos].storeAddr) == a)
                            || eboxRegister(a));
              if (!wfound && hz) begin wf = tagged Valid pos; wfound = True; end
            end
          end
          la.load(LaLevel{valid: True, kind: Whole, di: di, pc: pc, len: len, da: da,
                          data: tagged Invalid, fetchIssued: False, waitFor: wf,
                          branch: False, target: 0, storeAddr: prep.storeAddr});
          pcReg <= pc + ((len == Full) ? 2 : 1);
          ibusy <= 2 * iboxCycles(di, False);   // its preparation time
        end
      end
    end else if (prepared matches tagged Valid {.len, .di} &&& di matches tagged BranchInd .bi
                 &&& !indexIndicator(bi.indNum) &&& !isValid(intPC)) begin
      // A branch on an arithmetic indicator: guess not taken (plan
      // §6d). Load it as a branch level with its target, snapshot the
      // index words and indicators, and carry on down the fall-
      // through path. One guess at a time.
      if (!guessPending && la.count() < 4 && !progressivePending) begin
        la.load(LaLevel{valid: True, kind: Whole, di: di, pc: pc, len: len, da: tagged Invalid,
                        data: tagged Invalid, fetchIssued: False, waitFor: tagged Invalid,
                        branch: True, target: effAddr19(st, bi.addr, {3'b0, bi.idx}),
                        storeAddr: tagged Invalid});
        xSnap <= st.snapshotIndex();
        indSnap <= st.readIndicators();
        guessPending <= True;
        pcReg <= pc + ((len == Full) ? 2 : 1);
        ibusy <= 2 * 6;   // the branch's four-level load (Blosk p.39)
      end
    end else if (prepared matches tagged Valid {.len, .di}) begin
      // I-box class: execute ahead of pending levels unless a hazard
      // (plan §6c) says wait; never while the arithmetic unit's own
      // instruction is mid-flight (it owns the resume path).
      if (!ebox.busyFor(OwnerLA) && !iboxHazard(st, guessPending, di, nl)) begin
        let d1 <- startExecute(pc, len, di, isValid(intPC));
        done = d1;
      end
    end
    ebusy <= eb;
    haltedReg <= done;
  endrule

  method Action start();
    running <= True;
  endmethod

  method Action stop();
    running <= False;
  endmethod
  method Bool halted() = haltedReg;

  method HWordAddr getPC() = pcReg;
  method Action setPC(HWordAddr a);
    pcReg <= a;
    restartSeq <= restartSeq + 1;
    haltedReg <= False;
  endmethod

  // p.126: "The exchange automatically stores in the control word
  // location for the channel responsible for the channel signal a
  // fixed control word with the following contents: Data word address
  // = 4, Chain flag = 1, Multiple flag = 0, Skip flag = 0, Count = 1,
  // Refill address = 4", and then "initiates a READ for the indicated
  // channel, using the fixed control word".
  //
  // THE CHANNEL SIGNAL IS NOT SEPARATELY MODELLED.  StretchIO has one
  // tape unit on its own channel with no not-ready/ready transition
  // to raise one, and p.126 says loading works "only from a unit
  // having the selection address 0" -- which is what that unit is.
  // So this method is the key press and the signal together.  Item 7
  // of docs/NEXT.md 5k remains open for the multi-unit case.
  //
  // suppressEop is True because p.126 says "The EOP as well as the EE
  // indications, however, are not turned on upon the completion of
  // the operation."
  method Action iplStart();
    ControlWord fixed = ControlWord {
      dataAddr: 4, unitReady: 1, epgk: 0, uk: 0, ee: 0, eop: 0, cs: 0,
      seop: 0, chain: 1, multiple: 0, skip: 0, count: 1, refill: 4 };
    ioDev.writeChanCW(chanTape, fixed);
    ioPending <= tagged Valid IoXfer {
      ch: chanTape, isWrite: False, memAddr: 4, devIdx: 0,
      remaining: 1, suppressEop: True, skip: False, untilMark: False,
      zeroFill: False };
    iplActive <= True;
  endmethod

  interface mem = st;
  interface io = ioDev;
endmodule

endpackage
