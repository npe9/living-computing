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
      end else begin
        if (kind == DevTape) begin
          TapeIndex ti = truncate(x.devIdx); // safe: confirmed < TapeWords above
          if (x.isWrite)
            ioDev.writeTapeWord(ti, st.readWord(x.memAddr));
          else if (!x.skip)
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
          if (x.isWrite)
            ioDev.writePrinterWord(di, st.readWord(x.memAddr));
          else if (!x.skip)
            st.writeWord(x.memAddr, ioDev.readerWord(di));
        end
        // else: SKIP flag set on a READ (p.107) -- the device cursor
        // and memory address still advance below exactly as if the
        // word had been transferred, but core storage is left
        // untouched for this word.
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
      return False;
    end else if (pendingIdxWrite matches tagged Valid .p) begin
      // Part 2 of a progressive-indexing instruction: nothing was
      // fetched this call, and PC already advanced on part 1.
      st.writeIndex(tpl_1(p), tpl_2(p));
      pendingIdxWrite <= tagged Invalid;
      return False;
    end else begin
      HWordAddr pc = pcReg;
      HalfWord32 hw0 = readHW(st, pc);
      InstrLen len = instrLen(hw0);
      Maybe#(HalfWord32) hw1 = (len == Full) ? tagged Valid (readHW(st, pc + 1))
                                              : tagged Invalid;
      DecodedInstr di = decode(hw0, hw1);
      let {next, vflPending, ioStart} <- execute(st, ioDev, pc, len, di);
      pcReg <= next;
      pendingIdxWrite <= vflPending;
      ioPending <= ioStart;
      return next == pc;
    end
  endmethod

  method HWordAddr getPC() = pcReg;
  method Action setPC(HWordAddr a); pcReg <= a; endmethod

  interface mem = st;
  interface io = ioDev;
endmodule

endpackage
