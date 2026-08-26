// StretchCore.bsv
//
// Top-level, non-pipelined IBM 7030 core: fetch, decode, execute, one
// instruction per `step()` call. See bsv/README.md "Scope" for why this
// is NOT the famous lookahead/pipelined microarchitecture -- this
// module targets ISA-level correctness only.

package StretchCore;

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

  // In-progress instruction fetch, staged against StretchStorage's
  // readWordReq/readWordResp (docs/phase2_arm_inventory.md's
  // conversion order, step 2 -- the first arm converted to the new
  // two-call convention, chosen because it's bounded (0-2 reads, no
  // case-arm variation) and exercised by every program). Invalid: no
  // fetch in progress (an idle step() either starts a fresh fetch, in
  // the final `else` branch below, or services one of the two other
  // pending-* FSMs above it). Valid tuple3(False, pc, _): a request
  // for the word containing hw0 was issued last cycle at word
  // pc[18:1]; waiting on its response. Valid tuple3(True, pc, hw0):
  // hw0 has already been collected and decoding found the instruction
  // Full-length; a request for the word containing hw1 was issued
  // last cycle at word (pc+1)[18:1]; hw0 is carried through unchanged
  // so it's still on hand once hw1's response arrives. Mirrors
  // pendingIdxWrite's tpl_1/tpl_2 accessor style above rather than a
  // dedicated tagged-union type, for the same reason: this is a
  // 2-state FSM, not worth a new type.
  Reg#(Maybe#(Tuple3#(Bool, HWordAddr, HalfWord32))) fetchPending <- mkReg(tagged Invalid);

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

  method ActionValue#(Bool) step();
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
      end else if (x.isWrite && !ioReadIssued) begin
        // W-direction (memory->device), first visit to this word:
        // issue the read request and wait. ioPending/x are left
        // untouched (same devIdx/memAddr/remaining next call), so the
        // NEXT call's `x` still names this same word once the
        // response is ready.
        st.readWordReq(x.memAddr);
        ioReadIssued <= True;
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
    end else if (fetchPending matches tagged Valid .fp) begin
      // Continue an in-progress fetch -- see fetchPending's own
      // comment above for the two states this covers.
      Bool waitingHw1     = tpl_1(fp);
      HWordAddr pc        = tpl_2(fp);
      HalfWord32 hw0cap   = tpl_3(fp);
      Word64 w <- st.readWordResp();
      if (!waitingHw1) begin
        HalfWord32 hw0 = (pc[0] == 0) ? w[63:32] : w[31:0];
        InstrLen len = instrLen(hw0);
        if (len == Full) begin
          // hw0 collected, instruction is Full-length: issue hw1's
          // request now (same cycle as collecting hw0's response --
          // a real BRAM port allows a request.put() and a prior
          // response.get() in the same rule, confirmed by
          // scratchpad/bram_probe/BramProbe4.bsv) and wait for it.
          st.readWordReq((pc + 1)[18:1]);
          fetchPending <= tagged Valid tuple3(True, pc, hw0);
          return False;
        end else begin
          // Half-length: done fetching, decode+execute now, same as
          // the single-step case below.
          DecodedInstr di = decode(hw0, tagged Invalid);
          let {next, vflPending, ioStart} <- execute(st, ioDev, pc, len, di);
          pcReg <= next;
          pendingIdxWrite <= vflPending;
          ioPending <= ioStart;
          fetchPending <= tagged Invalid;
          return next == pc;
        end
      end else begin
        // hw1 collected (instruction is Full-length by construction --
        // that's the only way this state is ever entered).
        HalfWord32 hw1 = ((pc + 1)[0] == 0) ? w[63:32] : w[31:0];
        DecodedInstr di = decode(hw0cap, tagged Valid hw1);
        let {next, vflPending, ioStart} <- execute(st, ioDev, pc, Full, di);
        pcReg <= next;
        pendingIdxWrite <= vflPending;
        ioPending <= ioStart;
        fetchPending <= tagged Invalid;
        return next == pc;
      end
    end else begin
      // Start a new fetch: issue the request for the word containing
      // hw0 and wait. Nothing else completes this cycle -- unlike the
      // pre-FSM version, even a Half-length instruction now takes (at
      // least) two step() calls total, one to issue the request and
      // one to collect it and execute. Callers that loop on step()
      // until it returns True need no changes (see this interface's
      // own step() doc above).
      HWordAddr pc = pcReg;
      st.readWordReq(pc[18:1]);
      fetchPending <= tagged Valid tuple3(False, pc, 0);
      return False;
    end
  endmethod

  method HWordAddr getPC() = pcReg;
  method Action setPC(HWordAddr a); pcReg <= a; endmethod

  interface mem = st;
  interface io = ioDev;
endmodule

endpackage
