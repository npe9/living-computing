package TapeTb;

import StretchTypes::*;
import TapeSource::*;
import TapeSourceFile::*;
import ClientServer::*;
import GetPut::*;

(* synthesize *)
module mkTapeTb(Empty);
   TapeSource src <- mkTapeSourceFile;
   Reg#(Bit#(8)) i <- mkReg(0);
   Reg#(Bit#(8)) n <- mkReg(0);

   rule rl_ask (i < 6);
      src.words.request.put(TapeRequest { write: False,
                                          addr: zeroExtend(i),
                                          data: 0 });
      i <= i + 1;
   endrule

   rule rl_get;
      let r <- src.words.response.get;
      $display("word %0d = %016x  atEnd=%0d  present=%0d  cap=%0d",
               n, r.data, r.atEnd, src.mediaPresent, src.capacity);
      n <= n + 1;
      if (n == 5) $finish(0);
   endrule
endmodule

endpackage
