// StretchDiskSource.bsv -- the 353 disk storage platter, behind an
// interface, exactly as StretchTapeSource.bsv holds the 729's reel.
// docs/disk_subsystem.md §5.4.
//
// WHY AN INTERFACE AND NOT A Vector IN StretchIO.  A disk unit is
// 2,097,152 words (Reference Manual printed p.157), which is 16 MiB
// and is never going to be registers.  The tape learned this lesson
// first and the shape is copied from it deliberately: a small source
// (block RAM since 2026-11-25; see below) to test against, and room
// for a host-file or SD-backed one behind the same three methods.
//
// THE GEOMETRY IS ARCHITECTURAL AND IS NOT NEGOTIABLE, even in the
// small source.  Printed p.157: "Each disk storage area is subdivided
// into 4096 (2^12) addressable locations called arcs... An arc
// contains 512 words of information and is the smallest addressable
// unit in the disk system."  So ArcWords is 512 here whatever the
// source's capacity is, because the tail-zero-fill rule on a short
// WRITE (printed p.160) is defined in terms of it and a test that
// used a smaller arc would be testing a machine that never existed.
//
// WHAT THE SMALL SOURCE IS FOR.  DiskWordsSmall is two arcs.  That is
// the least that can exercise the three things the arc structure
// actually does: a transfer that fits inside one arc, a transfer that
// crosses an arc boundary, and a short write whose tail has to be
// zero-filled to the end of its arc.
//
// A Vector OF REGISTERS, AND THE FIRST ATTEMPT WAS A RegFile WITH AN
// INITIALISING RULE.  It cost a whole suite run, so it is written
// down here rather than remembered.
//
// mkRegFileFull does not initialise, and a disk that reads back
// garbage before anything is written to it would make every test
// depend on simulator start-up state.  The obvious fix -- a rule that
// sweeps the array writing zeros, with `if (inited)` on readReq and
// write so nobody reads it early -- IS THE EXACT TRAP
// StretchTapeSource.bsv's header already records, in its fourth
// paragraph.  bsc lifts a method's implicit condition into the
// predicate of EVERY RULE THAT CALLS IT, unguarded and not per
// if/else arm, so `ioDev_disk_inited` appeared in rl_io's predicate:
//
//     Rule: rl_io
//     Predicate: ioDev_disk_inited && tick.whas && ...
//
// which turned off the whole input-output path -- tape, reader,
// printer and disk -- for the 1024 clocks the sweep took.  MCP's
// bootstrap does its first tape READ well inside that window, and
// the suite caught it as three failures in "MCP'S OWN BOOTSTRAP
// RUNS" with the PC stopped at 000124.40.  The same trap, the same
// symptom, the same file to have read first.
//
// A Vector of Regs has no guard to lift and no rule to schedule:
// mkReg(0) initialises it at elaboration and that is the end of it.
// The cost was 1024 x 64 flip-flops, which Bluesim does not care about
// and a bitstream does: fpga_feasibility.md §11 measured 65,536 of the
// whole core's 102,219 TRELLIS_FF in `ioDev_disk_img_*`, and a Vector
// of Reg can never become block RAM.
//
// SO THE PLATTER IS NOW A BRAMCore, AND POWER-ON ZERO IS A BITMASK
// (2026-11-25, fidelity_plan.md F0/F2).  Three properties carry over
// from the Vector, and each is why this shape and not another:
//
//   1. NO GUARD.  mkBRAMCore2's put and read have no implicit
//      condition (unlike BRAM.bsv's server wrappers, whose FIFOs would
//      lift into rl_io exactly as the init sweep did), and the written
//      mask is a plain register.  rl_io's predicate is unchanged; the
//      schedule file is the check.
//   2. ONE CLOCK OF LATENCY, THE SAME ONE.  A BRAM read put in clock N
//      is on its output in N+1, and the CReg already made respReady
//      true in N+1.  So the response arrives in the same clock it did
//      from the registers and no cycle count moves.  The CReg stays, as
//      the pending flag.
//   3. ZERO UNTIL WRITTEN.  A BRAM's power-on contents are not zero
//      (bsc's BRAM2.v initialises to 'hAAAA..., and Bluesim has its own
//      pattern), and a sweep is the trap above.  So one bit per word
//      says "written", latched beside the read request and ANDed onto
//      the data.  1,024 flip-flops instead of 65,536, and no rule.
//
// Port a reads, port b writes, so a write can never disturb a read's
// held output.  The transfer FSM never reads and writes the disk in
// one clock (a transfer is one direction), so the same-address
// collision BRAMs leave undefined cannot arise.
//
// `peek` IS GONE from the interface.  A BRAM cannot answer
// combinationally, and nothing called it: every disk test reads the
// platter back through the machine (tests/gen_disk_tb.py's header says
// why that is the stronger check) or through the host image file.
//
// A bitstream will still mount SDRAM through this same interface
// (the disk plan's D3, mkDiskSourceSdram) for the full 2^21 words; this
// module is the two-arc unit-test platter, now in four DP16KD.

package StretchDiskSource;

import StretchTypes::*;
import Vector::*;
import BRAMCore::*;

// A word index into one disk unit: 2^21 words (printed p.157).
typedef Bit#(21) DiskIndex;

// One bit wider, room for "one past the end" -- the same idiom as
// IoXfer.devIdx against DeviceIndex and TapePos against TapeIndex.
typedef Bit#(22) DiskPos;

// The arc address register's width: 4096 arcs, printed p.157.
typedef Bit#(12) ArcAddr;

// Words per arc, printed p.157.  Architectural; see the header.
Integer arcWords = 512;

// The small source's capacity, in words: two arcs.  See the header.
typedef 1024 DiskWordsSmall;

interface DiskSource;
  // Request / poll / collect, the same contract as TapeSource, and
  // for the same reason: a caller that assumes the response is ready
  // in the clock it asked is wrong against an SD card.
  method Action readReq(DiskIndex i);
  method Bool respReady();
  method ActionValue#(Word64) readResp();

  // Posted, but only when canWrite() says so.  A source backed by
  // SDRAM or a card cannot take a word every clock, and the caller
  // must wait rather than lose it.  An EXPLICIT Bool rather than an
  // implicit guard on write, for the reason this file's header gives:
  // bsc would lift a guard into the predicate of rl_io, the one rule
  // that moves every device's words, and stop the tape and the reader
  // with it.  rl_io polls it exactly as it polls st.writeReady().
  method Bool canWrite();
  method Action write(DiskIndex i, Word64 v);

  // How many words this source holds.  The transfer FSM tests devIdx
  // against it, so it has to come from the implementation.  A DiskPos,
  // one bit wider than an index, because a full 353 holds 2^21 words
  // and DiskIndex cannot say 2^21.
  method DiskPos capacity();
endinterface

module mkDiskSourceSmall(DiskSource);
  // The platter: port a reads, port b writes.  No output register, so
  // a read put in clock N is on `a.read` in N+1 -- the latency the
  // CReg below already gave.  See the header.
  BRAM_DUAL_PORT#(Bit#(TLog#(DiskWordsSmall)), Word64) img
      <- mkBRAMCore2(valueOf(DiskWordsSmall), False);
  // One bit per word: has it been written since power-on?
  Reg#(Bit#(DiskWordsSmall)) written <- mkReg(0);

  // THE SAME CReg AS THE TAPE, AND FOR THE SAME REASON.  Port 0 is
  // ordered before port 1 within a clock, so readResp and readReq are
  // both callable from one rule with no conflict and there is no rule
  // of our own to order against the caller.  StretchTapeSource.bsv's
  // header records the three designs that failed before this one; all
  // three would fail here identically.  It now holds only whether a
  // response is pending and whether it is real data (False: out of
  // range or never written, which reads zero).
  Reg#(Maybe#(Bool)) resp[2] <- mkCReg(2, tagged Invalid);

`ifdef DISK_WRITE_STALL
  // A TEST MODE, for tests/run_disk_stall_test.sh: the source accepts a
  // write on one clock in four, and a write offered on any other clock
  // is LOST, as a full SDRAM write buffer would lose it.  A caller that
  // honours canWrite() loses nothing; one that ignores it shows up as
  // missing words on the platter.
  Reg#(Bit#(2)) stall <- mkReg(0);
  rule rl_stall; stall <= stall + 1; endrule
  Bool ok = (stall == 0);
`else
  Bool ok = True;
`endif

  // POWER-ON CONTENTS ARE ZERO, which is this model's choice and not
  // the manual's: printed p.157 says nothing about what an unwritten
  // arc reads back.  `written` is what makes the choice free -- no
  // rule, no guard, nothing for bsc to lift.
  method Action readReq(DiskIndex i);
    Bit#(TLog#(DiskWordsSmall)) idx = truncate(i);
    Bool inRange = (i < fromInteger(valueOf(DiskWordsSmall)));
    img.a.put(False, idx, ?);
    resp[1] <= tagged Valid (inRange && written[idx] == 1);
  endmethod

  method Bool respReady() = isValid(resp[0]);

  method ActionValue#(Word64) readResp();
    Bool isData = validValue(resp[0]);
    resp[0] <= tagged Invalid;
    return isData ? img.a.read : 64'd0;
  endmethod


  method Bool canWrite() = ok;

  method Action write(DiskIndex i, Word64 v);
    Bit#(TLog#(DiskWordsSmall)) idx = truncate(i);
    if (!ok)
      $display("StretchDiskSource: WRITE LOST at disk word %0d (canWrite was False)", i);
    else if (i < fromInteger(valueOf(DiskWordsSmall))) begin
      img.b.put(True, idx, v);
      written[idx] <= 1;
    end
  endmethod

  method DiskPos capacity() = fromInteger(valueOf(DiskWordsSmall));
endmodule

endpackage
