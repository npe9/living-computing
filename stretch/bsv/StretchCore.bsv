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
import StretchIO::*;
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
  // of using a fixed step count -- see stretch/strap/gen_tb.py, whose
  // run rule is `(!core.halted()) core.step(); stepCount++`, so the
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
  method Action step();      // advance the core exactly one clock
  method Bool   halted();    // the last clock's instruction branched to itself
  method HWordAddr getPC();
  method Action setPC(HWordAddr a);
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
  // (the mkFBox/mkMBox shape). The four ebox.exec call sites below are
  // mutually-exclusive branches of step(), so they share this one
  // instance's method port. See StretchExecute's mkEBox comment.
  EBox ebox <- mkEBox(st, ioDev);
  // Step 5b: the instruction buffers (1Y/2Y + IC controls) and the
  // four-level look-ahead are stage modules of their own
  // (StretchIBox.bsv, StretchLookAhead.bsv), the mkCPU_Stage shape;
  // the rules below orchestrate them.
  InstrBuffers ibuf <- mkInstrBuffers(st);
  LookAhead    la   <- mkLookAhead(st);
  // The harness's clock enable and the halt flag it polls (see the
  // rules section below for the contract).
  PulseWire  tick      <- mkPulseWire;
  Reg#(Bool) haltedReg <- mkReg(False);
  Reg#(HWordAddr) pcReg <- mkReg(0);
  Reg#(Maybe#(Tuple2#(Bit#(4), IndexWord))) pendingIdxWrite <- mkReg(tagged Invalid);
  Reg#(Maybe#(IoXfer)) ioPending <- mkReg(tagged Invalid);

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
  function ActionValue#(Bool) startExecute(HWordAddr pc, InstrLen len, DecodedInstr di) =
    actionvalue
      let r <- ebox.start(pc, len, di, replicate(0), 0, OwnerIbox);
      startClk <= clk;
      if (r matches tagged Valid .o) begin
        commitNext(pc, len, o.next);
        pendingIdxWrite <= o.idxWrite;
        ioPending <= o.ioStart;
        Bool taken = (o.next != pc + ((len == Full) ? 2 : 1));
        ibusy <= budgetClocks(di, taken);   // completed in the dispatch clock
        return o.next == pc;
      end else
        return False;
    endactionvalue;

  // =====================================================================
  // Idiomatic-Bluespec rewrite step 4 (docs/microarchitecture_plan.md
  // §1c): the instruction unit's per-clock work as RULES, not one
  // monolithic step() method. The test harness's `step()` is now just a
  // clock enable (the `tick` pulse), and every rule below is gated on
  // it, so the harness keeps the exact control it had: one `step()`
  // call advances the core exactly one clock, and no rule fires while
  // the harness is loading storage or reading results.
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
  Bool armIdx      = !armRecover && !isValid(ioPending) && isValid(pendingIdxWrite);
  Bool resumeReady = ebox.canResume();
  Bool armResume   = !armRecover && !isValid(ioPending) && !isValid(pendingIdxWrite) && resumeReady;
  // (A branch level has no operand and is removed as soon as it is the
  // head with the E-box free, i.e. once every earlier level has retired.)
  Bool headReady   = la.count() != 0 && ebusy == 0 && !ebox.busyFor(OwnerLA)
                     && (!isValid(la.headLevel().da) || isValid(la.headLevel().data));
  Bool armRemove   = !armRecover && !isValid(ioPending) && !isValid(pendingIdxWrite)
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

  // WHEN IT FIRES, AND THE SIMPLIFICATION THAT IS.  p.48: "Interruption
  // is permitted after the execution of an instruction is completed,
  // terminated, or suppressed and before execution of the next
  // instruction" -- an INSTRUCTION boundary.  This model fires it at a
  // QUIESCENT boundary instead: look-ahead empty, E-box idle, no
  // instruction's time budget still running.  On the real machine an
  // interruption drains the look-ahead, so the two coincide whenever
  // the levels are empty; where they differ, this one is LATER, never
  // earlier, and an instruction already loaded into a level will
  // complete before the interruption is taken.  Stated here, in
  // run_tests.sh and in bsv/README.md rather than left to be
  // discovered, and the test's instruction stream is written so the
  // two conditions coincide -- otherwise the test would be evidence
  // only about the weaker rule.
  Bool armInterrupt = !armRecover && !isValid(ioPending) && !isValid(pendingIdxWrite)
                      && !resumeReady && !headReady
                      && !isValid(intPC)          // one instruction, then done
                      && la.count() == 0 && !ebox.busy() && ebusy == 0 && ibusy == 0
                      && isValid(intDue);
  Bool armPrepare  = !armRecover && !isValid(ioPending) && !isValid(pendingIdxWrite)
                     && !resumeReady && !headReady && !armInterrupt;

  (* fire_when_enabled *)
  rule rl_clock (tick);
    clk <= clk + 1;
  endrule

  // ---- Look-ahead: collect arrived operands, issue one fetch ----
  // (No fire_when_enabled on this rule or rl_ic_controls: they share the
  // look-ahead / Y-buffer bus channels with the exported `mem`
  // interface, and at the synthesized boundary bsc must assume the
  // harness could call those methods in a ticked clock. It never does
  // -- the harness ticks only in its run rule -- but that is a harness
  // fact, not something the scheduler can prove here.)
  rule rl_la_fetch (tick);
    la.collect();
  endrule

  // ---- IC controls: run every clock, alongside the instruction FSM ----
  rule rl_ic_controls (tick);
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
  rule rl_recover (tick && armRecover);
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

  rule rl_io (tick && armIo);
    // Service one word of an in-flight RD/W transfer. See this
    // interface's step() doc above and StretchIO.bsv's file header.
    // Capacity is device-kind-dependent: the tape's TapeWords is
    // deliberately smaller than the reader/printer's DeviceWords
    // (see StretchIO.bsv) so this is where that distinction has to
    // be made, not a single shared constant.
    let x = validValue(ioPending);
    DeviceKind kind = kindOf(x.ch);
    Bit#(6) capacity = (kind == DevTape)
      ? fromInteger(valueOf(TapeWords)) : fromInteger(valueOf(DeviceWords));
    if (x.devIdx >= capacity) begin
      // "the unit runs out of material" (p.121): End Exception, not
      // Unit Check -- the block ends early; whatever was already
      // moved stays moved, and the control word reflects exactly
      // that (dataAddr/count as of the last word actually
      // transferred, since this cycle transfers nothing).
      ControlWord cw = ioDev.readChanCW(x.ch);
      cw.ee = 1;
      if (!x.suppressEop) cw.eop = 1;
      ioDev.writeChanCW(x.ch, cw);
      ioPending <= tagged Invalid;
    end else if (!st.writeReady()) begin
      // The store queue is full: the exchange waits for the memory
      // bus before moving the next word (a RD-direction word is a
      // store; the W-direction path is also held so the two
      // directions keep the same per-word pacing).
      noAction;
    end else if (x.isWrite && !ioReadIssued) begin
      // W-direction (memory->device), first visit to this word:
      // issue the read request and wait. ioPending/x are left
      // untouched (same devIdx/memAddr/remaining next call), so the
      // NEXT call's `x` still names this same word once the
      // response is ready.
      st.readWordReq(x.memAddr);
      ioReadIssued <= True;
    end else if (x.isWrite && !st.responseReady()) begin
      // W-direction: the memory read is in flight; wait for it.
      noAction;
    end else begin
      // Either RD-direction (always one call, ioReadIssued unused
      // and stays False) or W-direction with the read response now
      // ready to collect.
      if (kind == DevTape) begin
        TapeIndex ti = truncate(x.devIdx); // safe: confirmed < TapeWords above
        if (x.isWrite) begin
          Word64 v <- st.readWordResp();
          ioDev.writeTapeWord(ti, v);
        end else if (!x.skip)
          st.writeWord(x.memAddr, ioDev.readTapeWord(ti));
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
          ioDev.writePrinterWord(di, v);
        end else if (!x.skip)
          st.writeWord(x.memAddr, ioDev.readerWord(di));
      end
      // else: SKIP flag set on a READ (p.107) -- the device cursor
      // and memory address still advance below exactly as if the
      // word had been transferred, but core storage is left
      // untouched for this word.
      ioReadIssued <= False;
      Bit#(19) rem1 = x.remaining - 1;
      ControlWord cw = ioDev.readChanCW(x.ch);
      cw.dataAddr = x.memAddr + 1;
      cw.count = truncate(rem1);
      if (rem1 == 0) begin
        if (!x.suppressEop) cw.eop = 1;
        ioDev.writeChanCW(x.ch, cw);
        ioPending <= tagged Invalid;
      end else begin
        ioDev.writeChanCW(x.ch, cw);
        ioPending <= tagged Valid IoXfer {
          ch: x.ch, isWrite: x.isWrite, memAddr: x.memAddr + 1,
          devIdx: x.devIdx + 1, remaining: rem1,
          suppressEop: x.suppressEop, skip: x.skip };
      end
    end
    ebusy <= eb;
    haltedReg <= False;
  endrule

  rule rl_idx_write (tick && armIdx);
    // Part 2 of a progressive-indexing instruction: nothing was
    // fetched this call, and PC already advanced on part 1.
    let p = validValue(pendingIdxWrite);
    st.writeIndex(tpl_1(p), tpl_2(p));
    pendingIdxWrite <= tagged Invalid;
    ebusy <= eb;
    haltedReg <= False;
  endrule

  rule rl_exec_resume (tick && armResume);
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
        done = (o.next == pc);
      end
    end
    ebusy <= ebn;
    haltedReg <= done;
  endrule

  rule rl_au_remove (tick && armRemove);
    // Remove the head level into the arithmetic unit: its operand
    // (if any) is present, so the E-box runs with it pre-supplied;
    // any further read it needs, the box holds it for (resume arm).
    Bit#(16) ebn = eb;
    LaLevel h = la.headLevel();
    Vector#(2, Word64) pf = replicate(0);
    Bit#(2) cnt = 0;
    if (h.data matches tagged Valid .d) begin pf[0] = d; cnt = 1; end
    let r <- ebox.start(h.pc, h.len, h.di, pf, cnt, OwnerLA);
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
  rule rl_interrupt (tick && armInterrupt);
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
  endrule

  rule rl_prepare (tick && armPrepare);
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
        Maybe#(WordAddr) da = tagged Invalid;
        Bool loaded = True;
        if (fetchesOperand(di)) begin
          // Side-effect-free probe: execute() with no operand bails
          // out with the address of the operand it needs.
          let {next, vflPending, ioStart, needsRead} <-
            ebox.exec(pc, len, di, replicate(0), 0);
          if (needsRead matches tagged Valid .a) da = tagged Valid a;
          else begin
            // Classified as fetching but completed: treat as executed.
            $display("StretchCore: E-box instruction at %0d executed at preparation (classification mismatch)", pc);
            commitNext(pc, len, next);
            pendingIdxWrite <= vflPending;
            ioPending <= ioStart;
            loaded = False;
          end
        end
        if (loaded) begin
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
          la.load(LaLevel{valid: True, di: di, pc: pc, len: len, da: da,
                          data: tagged Invalid, fetchIssued: False, waitFor: wf,
                          branch: False, target: 0, storeAddr: storeTarget(st, di)});
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
        la.load(LaLevel{valid: True, di: di, pc: pc, len: len, da: tagged Invalid,
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
        let d1 <- startExecute(pc, len, di);
        done = d1;
      end
    end
    ebusy <= eb;
    haltedReg <= done;
  endrule

  method Action step();
    tick.send();
  endmethod
  method Bool halted() = haltedReg;

  method HWordAddr getPC() = pcReg;
  method Action setPC(HWordAddr a);
    pcReg <= a;
    restartSeq <= restartSeq + 1;
    haltedReg <= False;
  endmethod

  interface mem = st;
  interface io = ioDev;
endmodule

endpackage
