// StretchDiskSourceFile.bsv -- a DiskSource the full size of a 353,
// held in host memory, for the Bluesim builds that run MCP.
//
// WHY THIS EXISTS.  MCP's IPL writes 12,288 words to the disk
// (measured 2026-11-07: a WRITE from core 4870 that is still 11,264
// words short when it reaches word 1024).  mkDiskSourceSmall holds two
// arcs, 1024 words, so that WRITE ran off the end of the volume and
// rl_io gave it End Exception -- the "unit runs out of material" arm.
// Once the exchange learned to report status (decks/io_status_report),
// MCP received that EE as soon as it enabled and took its disk error
// path: an artifact of the model's disk size, not anything a 7030
// would have done.  A 353 holds 2^21 words (Reference Manual printed
// p.157), and this source holds exactly that.
//
// BLUESIM ONLY, FOR THE REASON StretchTapeSourceFile.bsv GIVES:
// `import "BDPI"` has no Verilog back end, so StretchIO.bsv selects
// this module only under -D HOST_TAPE, the define the host-file builds
// already carry.  A bitstream keeps mkDiskSourceSmall (and, later, an
// SD card behind the same interface).
//
// POWER-ON CONTENTS ARE ZERO, the same choice mkDiskSourceSmall makes
// and for the same reason (printed p.157 says nothing): host_tape.c
// callocs the image.  No image file is loaded or written back -- MCP
// formats its own disk at IPL (printed pp.15-16), so nothing needs one
// yet.

package StretchDiskSourceFile;

import StretchTypes::*;
import StretchDiskSource::*;

import "BDPI" function Bit#(64) host_disk_read_word(Bit#(32) idx);
import "BDPI" function Action   host_disk_write_word(Bit#(32) idx,
                                                     Bit#(64) d);

module mkDiskSourceFile(DiskSource);
  // One clock of latency and the same CReg as every other source; see
  // StretchTapeSource.bsv's header for why.
  Reg#(Maybe#(Word64)) resp[2] <- mkCReg(2, tagged Invalid);

  method Action readReq(DiskIndex i);
    resp[1] <= tagged Valid host_disk_read_word(zeroExtend(i));
  endmethod

  method Bool respReady() = isValid(resp[0]);

  method ActionValue#(Word64) readResp();
    let v = validValue(resp[0]);
    resp[0] <= tagged Invalid;
    return v;
  endmethod

  method Bool canWrite() = True;   // host memory never refuses

  method Action write(DiskIndex i, Word64 v);
    host_disk_write_word(zeroExtend(i), v);
  endmethod

  method Word64 peek(DiskIndex i) = host_disk_read_word(zeroExtend(i));

  // 2^21 words, printed p.157: every DiskIndex is in range.
  method DiskPos capacity() = fromInteger(2097152);
endmodule

endpackage
