// TapeSource.bsv -- the one interface the rest of the model sees for
// tape media, and the in-bitstream implementation of it.
//
// Sibling of ~/src/ulx3s-experiments/flute-ulx3s/src/Sdram_Controller.bsv:
// that module presents MemoryServer#(addr,256) and the SoC connects it
// with mkConnection. This presents Server#(TapeRequest,TapeResponse)
// and the testbench or the board top level connects it the same way.

package TapeSource;

import StretchTypes::*;
import ClientServer::*;
import GetPut::*;
import FIFOF::*;
import Vector::*;

// 2^24 eight-byte words = 134 MB, more than a 2400 ft 729 IV reel
// holds at 556 bpi, so the address never has to be the limit.
typedef Bit#(24) TapeWordAddr;

typedef struct {
   Bool         write;
   TapeWordAddr addr;
   Word64       data;    // ignored when write == False
} TapeRequest deriving (Bits, Eq, FShow);

typedef struct {
   Word64 data;
   Bool   atEnd;         // addr was past the end of the mounted image
} TapeResponse deriving (Bits, Eq, FShow);

interface TapeSource;
   interface Server#(TapeRequest, TapeResponse) words;
   (* always_ready *) method Bool         mediaPresent;
   (* always_ready *) method TapeWordAddr capacity;
endinterface

// ---------------------------------------------------------------
// mkTapeSourceVector -- exactly today's StretchIO storage, behind the
// new interface. Keeps tests/run_tests.sh green: gen_tape_tb.py still
// pre-loads and post-checks, and io_tape.strap still reaches End
// Exception by running off the end.
// ---------------------------------------------------------------
// nWords is a Bit#(24), not an Integer, so the module can keep its own
// (* synthesize *) boundary -- bsc: "A parameter of the module uses the
// type `Integer' which is not in the Bits class" (T0043).
(* synthesize *)
module mkTapeSourceVector#(TapeWordAddr nWords)(TapeSource);
   Vector#(16, Reg#(Word64)) img <- replicateM(mkReg(0));
   FIFOF#(TapeRequest)  reqF  <- mkLFIFOF;
   FIFOF#(TapeResponse) respF <- mkLFIFOF;

   rule rl_serve;
      let r = reqF.first; reqF.deq;
      Bool past = r.addr >= nWords;
      Bit#(4) i = truncate(r.addr);
      if (r.write && !past) img[i] <= r.data;
      respF.enq(TapeResponse { data: past ? 0 : img[i], atEnd: past });
   endrule

   interface Server words;
      interface Put request  = toPut(reqF);
      interface Get response = toGet(respF);
   endinterface
   method Bool mediaPresent = True;
   method TapeWordAddr capacity = nWords;
endmodule

endpackage
