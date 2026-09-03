// StretchCore.bsv
//
// Top-level, non-pipelined IBM 7030 core: fetch, decode, execute, one
// instruction per `step()` call. See bsv/README.md "Scope" for why this
// is NOT the famous lookahead/pipelined microarchitecture -- this
// module targets ISA-level correctness only.

package StretchCore;

import Vector::*;
import StretchTypes::*;
import StretchStorage::*;
import StretchIO::*;
import StretchDecode::*;
import StretchExecute::*;

interface StretchCore;
  // Fetch+decode+execute exactly one instruction; returns True iff the
  // instruction branched to its own address (the "BEW, $" halt idiom,
  // C22-6531 p.14 -- "$" is the location counter, so this targets the
  // instruction itself). Runners that assemble and load real STRAP
  // programs use this to stop instead of a fixed step count -- see
  // stretch/strap/gen_tb.py.
  //
  // A progressive-indexing VFL instruction (Reference Manual p.21)
  // takes TWO calls to step() to complete -- the manual's own words:
  // "An operation in which progressive indexing is specified is
  // executed in two parts." The first call does everything except the
  // index-register write-back and does NOT advance the PC; the second
  // call (with no new instruction fetched) performs just that write
  // and then advances the PC.
  //
  // An RD or W input-output instruction (Reference Manual "IBM 7619
  // Exchange", pp.104-127) similarly takes MULTIPLE calls to complete:
  // the first call fetches the control word, starts the transfer, and
  // DOES advance the PC (matching the manual: "the computer then
  // proceeds to the execution of the next instruction"), but every
  // subsequent call moves exactly one more word of the block and
  // fetches nothing new until the whole block has moved -- see the
  // ioPending case below and StretchIO.bsv's file header for why this
  // makes the transfer synchronous from the program's point of view
  // (no genuine CPU/IO overlap) even though the real hardware overlaps
  // them. Both mechanisms return False on every call that isn't the
  // final one (a taken branch is the only way next==pc, and neither
  // progressive indexing nor an I/O transfer branches) -- callers that
  // just loop on step() until it returns True need no changes to
  // account for either.
  method ActionValue#(Bool) step();
  method HWordAddr getPC();
  method Action setPC(HWordAddr a);
  interface StretchStorage mem;  // direct access for test setup/inspection
  interface StretchIO io;        // simulated device access for test
                                  // setup/inspection -- see StretchIO.bsv
endinterface

module mkStretchCore(StretchCore);
  StretchStorage st <- mkStretchStorage;
  StretchIO ioDev <- mkStretchIO;
  Reg#(HWordAddr) pcReg <- mkReg(0);
  Reg#(Maybe#(Tuple2#(Bit#(4), IndexWord))) pendingIdxWrite <- mkReg(tagged Invalid);
  Reg#(Maybe#(IoXfer)) ioPending <- mkReg(tagged Invalid);

  // The instruction unit's instruction buffers 1Y/2Y and IC controls
  // (docs/microarchitecture_plan.md stage 2a; Blosk TR00.722 pp.7-10,
  // 25; CE manual figs 3.1.1-3.1.5). Each Y holds one 64-bit
  // instruction word fetched ahead of the instruction counter through
  // its own bus channel (StretchStorage.fetchReq/fetchReady/fetchResp,
  // return tags 1Y/2Y); a word is usable one I-checker cycle (two
  // clocks) after it arrives. The IC controls keep both filled with
  // the next words in sequence (`nextFetch`), free a Y once the
  // instruction counter has passed its word, and invalidate both on a
  // taken branch, a setPC, or a store to a prefetched word (program
  // store compare, Blosk p.21). A fetch still in flight for an
  // invalidated Y is discarded on arrival.
  Vector#(2, Reg#(YReg)) yr <- replicateM(mkReg(YReg{valid: False, pending: False,
                                                      discard: False, addr: 0, data: 0, chk: 0}));
  Reg#(WordAddr) nextFetch <- mkReg(0);
  // Restart requests (branch taken inside step(); setPC from outside)
  // as sequence numbers, so each register has exactly one writer.
  Reg#(Bit#(8)) branchSeq  <- mkReg(0);   // written in step()'s branch paths
  Reg#(Bit#(8)) restartSeq <- mkReg(0);   // written by setPC
  Reg#(Bit#(8)) restartSeen <- mkReg(0);  // written at the top of step()
  Reg#(Bit#(8)) branchSeen  <- mkReg(0);

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

  // In-progress execute() call that bailed out waiting on a
  // BRAM-eligible read (docs/phase2_arm_inventory.md's per-case-arm
  // staging; execute()'s own header comment in StretchExecute.bsv has
  // the full contract). Invalid: no execute() call in flight (either
  // none has been attempted yet this instruction, or the most recent
  // attempt completed). Valid tuple3(pc, len, di): execute() was
  // called for this decoded instruction and returned a
  // needsRead -- a request for that address was issued last cycle;
  // execPrefetch/execPrefetchCount (below) track what's been collected
  // so far, so the NEXT call to execute() can pick up with one more
  // slot filled.
  Reg#(Maybe#(Tuple3#(HWordAddr, InstrLen, DecodedInstr))) execPending <- mkReg(tagged Invalid);
  Reg#(Vector#(2, Word64)) execPrefetch <- mkReg(replicate(0));
  Reg#(Bit#(2)) execPrefetchCount <- mkReg(0);

  // Call execute() for a freshly decoded instruction (prefetchCount=0
  // -- no arm has been given anything yet). Either it completes
  // outright (the common case today, since only VflInt L can bail),
  // committing exactly as execute() always did, or it bails and this
  // starts execPending's own FSM instead. Shared by both fetchPending
  // completion paths (Half- and Full-length) below, so the dispatch
  // logic isn't duplicated between them.
  function ActionValue#(Bool) startExecute(HWordAddr pc, InstrLen len, DecodedInstr di) =
    actionvalue
      let {next, vflPending, ioStart, needsRead} <-
        execute(st, ioDev, pc, len, di, replicate(0), 0);
      if (needsRead matches tagged Valid .a) begin
        st.readWordReq(a);
        execPending <= tagged Valid tuple3(pc, len, di);
        execPrefetchCount <= 0;
        return False;
      end else begin
        pcReg <= next;
        pendingIdxWrite <= vflPending;
        ioPending <= ioStart;
        if (next != pc + ((len == Full) ? 2 : 1)) branchSeq <= branchSeq + 1;
        return next == pc;
      end
    endactionvalue;

  // Look up a prefetched, checked instruction word.
  function Maybe#(Word64) yLookup(WordAddr w);
    Maybe#(Word64) r = tagged Invalid;
    for (Integer k = 0; k < 2; k = k + 1)
      if (yr[k].valid && yr[k].chk == 0 && yr[k].addr == w) r = tagged Valid yr[k].data;
    return r;
  endfunction

  method ActionValue#(Bool) step();
    // ---- IC controls: run every clock, before the instruction FSM ----
    Vector#(2, YReg) ny = readVReg(yr);
    Bool restart = (restartSeq != restartSeen) || (branchSeq != branchSeen);
    WordAddr nf = nextFetch;
    WordAddr pcw = pcReg[18:1];
    for (Integer k = 0; k < 2; k = k + 1) begin
      // Program store compare: a store to a prefetched word invalidates it.
      if (st.recentStore() matches tagged Valid .sw &&& ny[k].addr == sw && (ny[k].valid || ny[k].pending)) begin
        ny[k].valid = False;
        if (ny[k].pending) ny[k].discard = True;
      end
      // Restart (taken branch or setPC): drop everything buffered.
      if (restart) begin
        ny[k].valid = False;
        if (ny[k].pending) ny[k].discard = True;
      end
      // Collect an arrived word; usable after the I-checker cycle.
      if (ny[k].pending && st.fetchReady(fromInteger(k))) begin
        let d <- st.fetchResp(fromInteger(k));
        ny[k].pending = False;
        if (ny[k].discard) ny[k].discard = False;
        else begin ny[k].valid = True; ny[k].data = d; ny[k].chk = 2; end
      end else if (ny[k].valid && ny[k].chk != 0)
        ny[k].chk = ny[k].chk - 1;
      // Free a word the instruction counter has passed.
      if (ny[k].valid && ny[k].addr < pcw) ny[k].valid = False;
    end
    if (restart) begin
      nf = pcw;
      restartSeen <= restartSeq;
      branchSeen <= branchSeq;
    end
    // Issue at most one prefetch per clock into a free Y, in order.
    Bool issued = False;
    for (Integer k = 0; k < 2; k = k + 1)
      if (!issued && !ny[k].valid && !ny[k].pending && !restart) begin
        st.fetchReq(fromInteger(k), nf);
        ny[k].pending = True; ny[k].discard = False; ny[k].addr = nf; ny[k].chk = 0;
        nf = nf + 1;
        issued = True;
      end
    writeVReg(yr, ny);
    nextFetch <= nf;

    if (ioPending matches tagged Valid .x) begin
      // Service one word of an in-flight RD/W transfer. See this
      // interface's step() doc above and StretchIO.bsv's file header.
      // Capacity is device-kind-dependent: the tape's TapeWords is
      // deliberately smaller than the reader/printer's DeviceWords
      // (see StretchIO.bsv) so this is where that distinction has to
      // be made, not a single shared constant.
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
        return False;
      end else if (!st.writeReady()) begin
        // The store queue is full: the exchange waits for the memory
        // bus before moving the next word (a RD-direction word is a
        // store; the W-direction path is also held so the two
        // directions keep the same per-word pacing).
        return False;
      end else if (x.isWrite && !ioReadIssued) begin
        // W-direction (memory->device), first visit to this word:
        // issue the read request and wait. ioPending/x are left
        // untouched (same devIdx/memAddr/remaining next call), so the
        // NEXT call's `x` still names this same word once the
        // response is ready.
        st.readWordReq(x.memAddr);
        ioReadIssued <= True;
        return False;
      end else if (x.isWrite && !st.responseReady()) begin
        // W-direction: the memory read is in flight; wait for it.
        return False;
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
        return False;
      end
    end else if (pendingIdxWrite matches tagged Valid .p) begin
      // Part 2 of a progressive-indexing instruction: nothing was
      // fetched this call, and PC already advanced on part 1.
      st.writeIndex(tpl_1(p), tpl_2(p));
      pendingIdxWrite <= tagged Invalid;
      return False;
    end else if (execPending matches tagged Valid .ep &&& !st.responseReady()) begin
      // Operand still in flight from memory: stall.
      return False;
    end else if (execPending matches tagged Valid .ep) begin
      // Resume an execute() call that bailed out waiting on a
      // BRAM-eligible read -- collect the response into the next
      // prefetch slot and try again. See execPending's own comment
      // above and execute()'s header comment in StretchExecute.bsv
      // for the full contract.
      HWordAddr pc       = tpl_1(ep);
      InstrLen len        = tpl_2(ep);
      DecodedInstr di     = tpl_3(ep);
      Word64 v <- st.readWordResp();
      Vector#(2, Word64) newPrefetch = execPrefetch;
      newPrefetch[execPrefetchCount] = v;
      Bit#(2) newCount = execPrefetchCount + 1;
      let {next, vflPending, ioStart, needsRead} <-
        execute(st, ioDev, pc, len, di, newPrefetch, newCount);
      if (needsRead matches tagged Valid .a) begin
        st.readWordReq(a);
        execPrefetch <= newPrefetch;
        execPrefetchCount <= newCount;
        return False;
      end else begin
        pcReg <= next;
        pendingIdxWrite <= vflPending;
        ioPending <= ioStart;
        execPending <= tagged Invalid;
        if (next != pc + ((len == Full) ? 2 : 1)) branchSeq <= branchSeq + 1;
        return next == pc;
      end
    end else begin
      // Preparation: transfer the next instruction from the Y buffers
      // (both halves of a full-word instruction, which may straddle
      // 1Y/2Y) and execute it; stall until the word(s) are buffered
      // and checked. (Stage 2a has no separate Z register yet: the
      // Y-to-Z transfer, index fetch and modification cycles are
      // charged in stage 2b.)
      HWordAddr pc = pcReg;
      if (!st.writeReady())
        return False; // a storing instruction could find the queue full: wait
      else if (yLookup(pc[18:1]) matches tagged Valid .w0) begin
        HalfWord32 hw0 = (pc[0] == 0) ? w0[63:32] : w0[31:0];
        InstrLen len = instrLen(hw0);
        if (len == Half) begin
          DecodedInstr di = decode(hw0, tagged Invalid);
          let done <- startExecute(pc, len, di);
          return done;
        end else begin
          HWordAddr pc1 = pc + 1;
          if (yLookup(pc1[18:1]) matches tagged Valid .w1) begin
            HalfWord32 hw1 = (pc1[0] == 0) ? w1[63:32] : w1[31:0];
            DecodedInstr di = decode(hw0, tagged Valid hw1);
            let done <- startExecute(pc, Full, di);
            return done;
          end else
            return False;
        end
      end else
        return False;
    end
  endmethod

  method HWordAddr getPC() = pcReg;
  method Action setPC(HWordAddr a);
    pcReg <= a;
    restartSeq <= restartSeq + 1;
  endmethod

  interface mem = st;
  interface io = ioDev;
endmodule

endpackage
