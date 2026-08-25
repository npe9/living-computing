// StretchCore.bsv
//
// Top-level, non-pipelined IBM 7030 core: fetch, decode, execute, one
// instruction per `step()` call. See bsv/README.md "Scope" for why this
// is NOT the famous lookahead/pipelined microarchitecture -- this
// module targets ISA-level correctness only.

package StretchCore;

import StretchTypes::*;
import StretchStorage::*;
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
  // and then advances the PC. Both calls return False (never a halt
  // condition: only a taken branch can make next==pc, and progressive
  // indexing only applies to VFL ops, which never branch). Callers
  // that just loop on step() until it returns True need no changes to
  // account for this -- see StretchExecute.bsv's VflInt case for why
  // this is a real two-cycle split rather than a same-cycle
  // convenience: it's the fix for a genuine bsc scheduler limitation,
  // not a stylistic choice.
  method ActionValue#(Bool) step();
  method HWordAddr getPC();
  method Action setPC(HWordAddr a);
  interface StretchStorage mem;  // direct access for test setup/inspection
endinterface

module mkStretchCore(StretchCore);
  StretchStorage st <- mkStretchStorage;
  Reg#(HWordAddr) pcReg <- mkReg(0);
  Reg#(Maybe#(Tuple2#(Bit#(4), IndexWord))) pendingIdxWrite <- mkReg(tagged Invalid);

  method ActionValue#(Bool) step();
    if (pendingIdxWrite matches tagged Valid .p) begin
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
      let {next, vflPending} <- execute(st, pc, len, di);
      pcReg <= next;
      pendingIdxWrite <= vflPending;
      return next == pc;
    end
  endmethod

  method HWordAddr getPC() = pcReg;
  method Action setPC(HWordAddr a); pcReg <= a; endmethod

  interface mem = st;
endmodule

endpackage
