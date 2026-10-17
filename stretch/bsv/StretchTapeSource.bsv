// StretchTapeSource.bsv
//
// WHERE A TAPE UNIT'S DATA COMES FROM, behind one interface, so that
// the model does not have to know.
//
// WHY THIS EXISTS, and it is not primarily about FPGAs.  Until this
// file, StretchIO.bsv's tape was `Vector#(16, Reg#(Word64))` read by a
// COMBINATIONAL, RANDOM-ACCESS, ALWAYS-READY value method:
//
//     method Word64 readTapeWord(TapeIndex i) = tapeImg[i];
//
// No magnetic tape has ever behaved that way.  A real 729 is strictly
// sequential and takes real time to deliver a byte, which is why the
// Reference Manual can speak of backspacing and of beginning- and
// end-of-tape conditions at all.  The zero-latency random-access tape
// was a simulation convenience, and the file's own comments already
// admitted as much.
//
// THIS PROJECT HAS MADE EXACTLY THIS MISTAKE BEFORE AND WRITTEN IT
// DOWN.  StretchStorage.bsv's header, on core storage:
//
//   "Reads take a variable number of clocks (the target unit's read-out
//    time plus any wait for a busy unit); callers must NOT assume any
//    fixed latency, which is exactly the assumption the previous BRAM
//    version baked in (a DWire that held the answer for one cycle)."
//
// So the request/ready/response shape below is not a new idea borrowed
// from somewhere else: it is the same correction, applied to the one
// device that still had the old shape, and spelled the same way
// (`readReq` / `respReady` / `readResp` against StretchStorage's
// `readWordReq` / `responseReady` / `readWordResp`).
//
// WHAT IT BUYS, in order of how much it matters:
//
//   1. FIDELITY.  A latent source is what a tape IS.  Making the
//      caller tolerate a wait removes an assumption the real machine
//      never justified.
//   2. A SWAPPABLE BACKING STORE.  An SD-card-backed source, a host
//      file read at run time, or an SDRAM region can all implement
//      this interface.  None of them can implement a combinational
//      value method, so the old shape foreclosed every one of them.
//   3. SCALE.  TapeWords is 16.  A real master system tape is bounded
//      below by what the initialization program loads into core --
//      98,304 words, 768 KB -- which is already far past what belongs
//      in registers or in ECP5 block RAM.
//
// WHAT IS DELIBERATELY NOT HERE.  No tape marks, no file structure, no
// variable-length records, no density, no unit numbering, no
// end-of-tape.  Those are tape SEMANTICS and they belong to whatever
// drives this interface; this file answers only "where do the bytes
// come from, and when are they ready".  Keeping the two apart is the
// point: the semantics are the same whether the bytes arrive from a
// Vector or from a card.
//
// `peek` IS NOT PART OF THE MACHINE.  It is the testbench's direct
// window on the image (strap/gen_tb.py and strap/gen_tape_tb.py
// pre-load the tape and check it afterwards through
// StretchIO's readTapeWord/writeTapeWord, which forward to `peek` and
// `write`).  Nothing in StretchExecute or the transfer FSM may call
// it -- a real program cannot see a tape except by moving it.

package StretchTapeSource;

import StretchTypes::*;
import Vector::*;

// Sixteen words, as before.  Deliberately small: strap/programs/
// io_tape.strap's End Exception check depends on a transfer being able
// to run off the end of the image, which a realistically sized tape
// would make tedious to provoke.  The typedef lives here rather than
// in StretchIO.bsv so that an implementation of this interface does
// not have to import the module it plugs into.
typedef 16 TapeWords;

// THE INDEX WIDTH IS DECOUPLED FROM THE IMAGE SIZE, 2026-10-17.
// TapeIndex used to be TLog#(TapeWords) -- four bits, because the
// register-backed image is sixteen words.  That tied every caller to
// one implementation's size: a file- or SD-backed source holds a reel.
//
// TapeWords CANNOT SIMPLY BE RAISED, which is worth saying because it
// is the obvious move.  strap/programs/io_tape.strap reaches End
// Exception by running a 20-word transfer off the end of a 16-word
// tape, and gen_tape_tb.py's CCWJ/CCWP expectations encode "16 of 20
// words transferred".  Sixteen is load-bearing for that test, so the
// Vector source keeps it and the TYPE widens instead.
typedef Bit#(24) TapeIndex;

// One bit wider than TapeIndex, room for "one past the end" (== 16)
// once the tape is fully drained -- the same idiom as IoXfer.devIdx
// against StretchIO.DeviceIndex.  See StretchIO.bsv's "TAPE POSITION".
typedef Bit#(25) TapePos;   // one wider than TapeIndex: room for
                            // "one past the end", the same idiom as
                            // IoXfer.devIdx against DeviceIndex

interface TapeSource;
  // The runtime read path.  Request, then poll respReady, then
  // collect.  A caller that assumes readResp is available in the same
  // clock as readReq is wrong even against mkTapeSourceVector below,
  // and will be very wrong against a card.
  method Action readReq(TapeIndex i);
  method Bool respReady();
  method ActionValue#(Word64) readResp();

  // The runtime write path.  Writes are posted, not acknowledged --
  // which is already a simplification, and the first thing an
  // SD-backed implementation will have to revisit.
  method Action write(TapeIndex i, Word64 v);

  // Testbench only; see the header.  Not reachable from the ISA.
  method Word64 peek(TapeIndex i);

  // How many words this source actually holds.  The transfer FSM
  // tests devIdx against it to raise End Exception -- "the unit runs
  // out of material" (RefMan p.121) -- so it has to come from the
  // implementation rather than from a typedef.  Before this existed
  // StretchCore read valueOf(TapeWords) directly, which silently
  // assumed the register-backed source.
  method TapeIndex capacity();
endinterface

// The register-backed source: the behaviour StretchIO.bsv had, with
// the access shape it should have had.  One clock of latency, which is
// the smallest number that is not a lie.
module mkTapeSourceVector(TapeSource);
  Vector#(TapeWords, Reg#(Word64)) img <- replicateM(mkReg(0));

  // A CONCURRENT REGISTER, AND NO RULE AT ALL.  Three earlier attempts
  // are recorded here because each failed differently and the last two
  // failed quietly:
  //
  //   1. A `resp` register driven by RWire/PulseWire from an internal
  //      rule, carrying (* fire_when_enabled, no_implicit_conditions *).
  //      bsc: (G0005) the assertion failed for RL_ioDev_tape_step.
  //   2. mkLFIFOF: (G0033), a genuine combinational cycle -- the loopy
  //      FIFO puts deq before enq, so notFull depends on deq's enable,
  //      and the caller calls both readReq and readResp.
  //   3. Plain mkFIFOF: compiled and ran, EXIT=0, 35 checks failed.
  //      bsc had lifted BOTH implicit conditions into the caller --
  //        Rule: rl_io
  //        Predicate: ioDev_tape_respQ.i_notFull &&
  //                   ioDev_tape_respQ.i_notEmpty && ...
  //      -- unguarded, not per if/else arm, so on an empty queue rl_io
  //      could never fire FOR ANY DEVICE.  One FIFO here turned off the
  //      whole I/O path, including the reader and printer.
  //   4. The RWire version with the attributes deleted: compiled, ran,
  //      and hung identically to 3.  Deleting the assertion silenced
  //      the message without fixing what it was reporting.  The wire
  //      design is only correct if the internal rule is ordered AFTER
  //      the caller; bsc's urgency ordering is global, so whether it
  //      is depends on the whole rule set -- a 20-line testbench with
  //      the same if/else shape scheduled it the right way and passed,
  //      while mkStretchCore scheduled it the other way and hung.  A
  //      wire does not persist, so a request written after the reader
  //      has already looked is simply lost, every cycle, forever.
  //
  // A CReg removes the question instead of answering it.  Port 0 is
  // ordered before port 1 within a clock, so readResp (port 0) and
  // readReq (port 1) are both callable from one rule with no conflict,
  // and THERE IS NO RULE OF OUR OWN TO ORDER against the caller.  That
  // is correctness by construction rather than by scheduling luck,
  // which is what the previous three attempts were relying on.
  //
  // Latency is still exactly one clock: readReq writes port 1 on clock
  // N, port 0 reads it on N+1.  Back-to-back request-and-collect in
  // one clock also behaves: port 0 clears, then port 1 sets.
  Reg#(Maybe#(Word64)) resp[2] <- mkCReg(2, tagged Invalid);

  method Action readReq(TapeIndex i);
    // The caller gates on capacity(), so i is in range; the truncate
    // is how a 24-bit address indexes a 16-word Vector, and the guard
    // makes an out-of-range request read zero rather than alias some
    // other word if that contract is ever broken.
    // `truncate` inside a Vector index gives bsc no target width
    // (T0035, "Bit vector of unknown size"), so the narrow index is a
    // named, explicitly typed binding.
    Bit#(TLog#(TapeWords)) idx = truncate(i);
    Bool inRange = (i < fromInteger(valueOf(TapeWords)));
    resp[1] <= tagged Valid (inRange ? img[idx] : 64'd0);
  endmethod

  method Bool respReady() = isValid(resp[0]);

  method ActionValue#(Word64) readResp();
    let v = validValue(resp[0]);
    resp[0] <= tagged Invalid;
    return v;
  endmethod

  method Action write(TapeIndex i, Word64 v);
    Bit#(TLog#(TapeWords)) idx = truncate(i);
    if (i < fromInteger(valueOf(TapeWords))) img[idx] <= v;
  endmethod

  method Word64 peek(TapeIndex i);
    Bit#(TLog#(TapeWords)) idx = truncate(i);
    return (i < fromInteger(valueOf(TapeWords))) ? img[idx] : 64'd0;
  endmethod

  method TapeIndex capacity() = fromInteger(valueOf(TapeWords));
endmodule

endpackage
