// StretchTapeSourceFile.bsv -- a TapeSource backed by a host file, so
// a tape image can be bigger than the sixteen registers
// mkTapeSourceVector holds.  docs/boot_plan.md M0 step 1.
//
// WHY THIS EXISTS.  The register-backed source is sixteen words.
// MCP's IPL bootstrap is 369 (printed p.2's control word: count
// 0o560 = 368, plus the control word itself), so M3 cannot even be
// attempted until a tape can hold more than sixteen words.  Nothing
// else about the path changes: the interface, the chaining, the IPL
// mechanism and mktape.py's image format are all already built and
// tested against the Vector source.
//
// BLUESIM ONLY, AND THE GUARD IS NOT OPTIONAL.  `import "BDPI"` has
// no Verilog back end.  bsc will happily emit a .v for a module that
// uses one -- as VPI wrappers -- and then yosys fails with
//   ERROR: Can't resolve function name '\$imported_host_tape_read_word'
// so this package must never be in the hierarchy a bitstream
// elaborates.  That is why StretchIO.bsv selects it behind
// `ifdef HOST_TAPE` rather than instantiating it directly.
//
// THE $fopen NOTE IN StretchIO.bsv IS OBSOLETE, and this is the
// evidence.  That header says bsc's file primitives "are Actions, so
// a block transfer would unroll into a statically-sequenced chain of
// file accesses".  True of $fopen/$fgetc, irrelevant here: a BDPI
// function whose result type is NOT Action may be called in a VALUE
// context, which is what makes a host file readable from inside a
// rule.  The idiom is the user's own, from
// ~/src/alto-bluespec/src/Disk.bsv:18-23, which reads a Diablo 31
// pack exactly this way.

package StretchTapeSourceFile;

import StretchTypes::*;
import StretchTapeSource::*;
import Vector::*;

// Value imports -- NOT Action.  That is the whole trick.
import "BDPI" function Bit#(32) host_tape_loaded();
import "BDPI" function Bit#(32) host_tape_words();
import "BDPI" function Bit#(64) host_tape_read_word(Bit#(32) idx);
import "BDPI" function Action   host_tape_write_word(Bit#(32) idx,
                                                     Bit#(64) d);

module mkTapeSourceFile(TapeSource);
  // One clock of latency, the same as mkTapeSourceVector, and for the
  // same reason: a caller that assumes readResp is available in the
  // clock it requested is wrong against every source.  The CReg is
  // also the same choice and for the same scheduling reason -- see
  // StretchTapeSource.bsv's header, which records the three designs
  // that failed before it.
  Reg#(Maybe#(Word64)) resp[2] <- mkCReg(2, tagged Invalid);

  method Action readReq(TapeIndex i);
    Bit#(32) idx = zeroExtend(i);
    Bool inRange = (idx < host_tape_words());
    resp[1] <= tagged Valid (inRange ? host_tape_read_word(idx) : 64'd0);
  endmethod

  method Bool respReady() = isValid(resp[0]);

  method ActionValue#(Word64) readResp();
    let v = validValue(resp[0]);
    resp[0] <= tagged Invalid;
    return v;
  endmethod

  // Writes land in the in-memory image only.  host_tape.c keeps
  // write-back to the file as a separate commit, the way
  // alto-bluespec's host_disk_commit() does, and nothing here calls
  // it: a 7030 program writing its own boot tape is boot_plan.md M2,
  // not M0.
  method Action write(TapeIndex i, Word64 v);
    host_tape_write_word(zeroExtend(i), v);
  endmethod

  method Word64 peek(TapeIndex i);
    Bit#(32) idx = zeroExtend(i);
    return (idx < host_tape_words()) ? host_tape_read_word(idx) : 64'd0;
  endmethod

  // The real reel length, which is the point: the End Exception test
  // in StretchCore asks the source rather than a typedef, so "the
  // unit runs out of material" (RefMan p.121) now means what the
  // mounted image actually contains.  No media mounted reports 0,
  // which makes every transfer end-except immediately rather than
  // reading zeros and looking like a successful load of nothing.
  method TapeIndex capacity() =
    (host_tape_loaded() != 0) ? truncate(host_tape_words()) : 0;
endmodule

endpackage
