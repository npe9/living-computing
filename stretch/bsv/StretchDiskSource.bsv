// StretchDiskSource.bsv -- the 353 disk storage platter, behind an
// interface, exactly as StretchTapeSource.bsv holds the 729's reel.
// docs/disk_subsystem.md §5.4.
//
// WHY AN INTERFACE AND NOT A Vector IN StretchIO.  A disk unit is
// 2,097,152 words (Reference Manual printed p.157), which is 16 MiB
// and is never going to be registers.  The tape learned this lesson
// first and the shape is copied from it deliberately: a register- (in
// fact RegFile-) backed source small enough to test against, and room
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
// The cost is 1024 x 64 flip-flops, which Bluesim does not care
// about and a bitstream would -- but a bitstream will mount an SD
// card through this same interface and never elaborate this module,
// exactly as it will never elaborate mkTapeSourceVector.

package StretchDiskSource;

import StretchTypes::*;
import Vector::*;

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

  // Posted, not acknowledged -- the same simplification TapeSource
  // makes, and the same first thing an SD-backed source must revisit.
  method Action write(DiskIndex i, Word64 v);

  // Testbench only.
  method Word64 peek(DiskIndex i);

  // How many words this source holds.  The transfer FSM tests devIdx
  // against it, so it has to come from the implementation.
  method DiskIndex capacity();
endinterface

module mkDiskSourceSmall(DiskSource);
  Vector#(DiskWordsSmall, Reg#(Word64)) img <- replicateM(mkReg(0));

  // THE SAME CReg AS THE TAPE, AND FOR THE SAME REASON.  Port 0 is
  // ordered before port 1 within a clock, so readResp and readReq are
  // both callable from one rule with no conflict and there is no rule
  // of our own to order against the caller.  StretchTapeSource.bsv's
  // header records the three designs that failed before this one; all
  // three would fail here identically.
  Reg#(Maybe#(Word64)) resp[2] <- mkCReg(2, tagged Invalid);

  // POWER-ON CONTENTS ARE ZERO, which is this model's choice and not
  // the manual's: printed p.157 says nothing about what an unwritten
  // arc reads back.  mkReg(0) is also what makes the choice free --
  // no rule, no guard, nothing for bsc to lift.
  method Action readReq(DiskIndex i);
    Bit#(TLog#(DiskWordsSmall)) idx = truncate(i);
    Bool inRange = (i < fromInteger(valueOf(DiskWordsSmall)));
    resp[1] <= tagged Valid (inRange ? img[idx] : 64'd0);
  endmethod

  method Bool respReady() = isValid(resp[0]);

  method ActionValue#(Word64) readResp();
    let v = validValue(resp[0]);
    resp[0] <= tagged Invalid;
    return v;
  endmethod

  method Action write(DiskIndex i, Word64 v);
    Bit#(TLog#(DiskWordsSmall)) idx = truncate(i);
    if (i < fromInteger(valueOf(DiskWordsSmall))) img[idx] <= v;
  endmethod

  method Word64 peek(DiskIndex i);
    Bit#(TLog#(DiskWordsSmall)) idx = truncate(i);
    return (i < fromInteger(valueOf(DiskWordsSmall))) ? img[idx] : 64'd0;
  endmethod

  method DiskIndex capacity() = fromInteger(valueOf(DiskWordsSmall));
endmodule

endpackage
