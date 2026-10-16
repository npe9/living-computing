// TapeSourceFile.bsv -- the Bluesim leg of TapeSource: a host file,
// read through BDPI, exactly the mechanism ~/src/alto-bluespec uses for
// its Diablo 31 disk pack (src/Disk.bsv:18-23, sim/host.c:315-368).
//
// This is Bluesim-only on purpose: `import "BDPI"` has no Verilog
// backend, so this package must NOT be in the hierarchy a board
// bitstream elaborates. That is the whole reason for the two-module
// split -- see docs/tape_data_path.md.

package TapeSourceFile;

import StretchTypes::*;
import TapeSource::*;
import ClientServer::*;
import GetPut::*;
import FIFOF::*;

// Value (not Action) imports: a BDPI function whose result type is not
// Action/ActionValue may be called in a value context, which is what
// makes a host file readable from inside a rule at all. This is the
// resolution of StretchIO.bsv's "$fopen/$fgetc are Actions" note.
import "BDPI" function Bit#(32) host_tape_loaded();
import "BDPI" function Bit#(32) host_tape_words();
import "BDPI" function Bit#(64) host_tape_read_word(Bit#(32) idx);
import "BDPI" function Action   host_tape_write_word(Bit#(32) idx, Bit#(64) d);

module mkTapeSourceFile(TapeSource);
   FIFOF#(TapeRequest)  reqF  <- mkLFIFOF;
   FIFOF#(TapeResponse) respF <- mkLFIFOF;

   rule rl_serve;
      let r = reqF.first; reqF.deq;
      Bit#(32) idx  = zeroExtend(r.addr);
      Bool     past = idx >= host_tape_words();
      if (r.write && !past)
         host_tape_write_word(idx, r.data);
      respF.enq(TapeResponse { data: past ? 0 : host_tape_read_word(idx),
                               atEnd: past });
   endrule

   interface Server words;
      interface Put request  = toPut(reqF);
      interface Get response = toGet(respF);
   endinterface
   method Bool         mediaPresent = (host_tape_loaded() != 0);
   method TapeWordAddr capacity     = truncate(host_tape_words());
endmodule

endpackage
