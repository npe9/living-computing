// PIM/m core: memory, the boxes, the two stages, and the rules that
// move an instruction between them.  One reduction at a time: start a
// goal at a code address with its arguments in r0.., and it runs until
// it ends (done, failed, suspended, or the model stopping loud).
// There is no goal queue yet: a suspended goal is reported, not kept.
package PimmCore;

import FIFO::*;
import Vector::*;
import PimmTypes::*;
import PimmMem::*;
import PimmDBox::*;
import PimmHBox::*;
import PimmStages::*;

interface PimmCore;
  method Action setReg(Bit#(8) r, Cell w);
  method Action poke(Addr a, Cell w);
  method Action start(Addr pc);
  method ActionValue#(End) finished;
  // look at a term after a reduction
  method Action derefReq(Cell w);
  method ActionValue#(Cell) derefResp;
endinterface

module mkPimmCore#(String image)(PimmCore);
  PimmMem   mem   <- mkPimmMem(image);
  PimmFetch fetch <- mkPimmFetch(mem.port[0]);
  PimmHBox  hbox  <- mkPimmHBox(mem.port[1]);
  PimmDBox  dbox  <- mkPimmDBox(mem.port[2]);
  PimmExec  exec  <- mkPimmExec(dbox, hbox);

  FIFO#(Addr) startQ <- mkFIFO;
  FIFO#(End)  endQ   <- mkFIFO;

  rule toExec;
    let f <- fetch.out;
    exec.enq(f);
  endrule

  (* descending_urgency = "advance, begin_goal" *)
  rule advance;
    let s <- exec.out;
    case (s) matches
      tagged Next .pc: fetch.enq(pc);
      tagged Stop .e:  endQ.enq(e);
    endcase
  endrule

  rule begin_goal;
    startQ.deq;
    exec.newGoal;
    fetch.enq(startQ.first);
  endrule

  method Action setReg(Bit#(8) r, Cell w) = exec.setReg(r, w);
  method Action poke(Addr a, Cell w) = dbox.poke(a, w);
  method Action start(Addr pc) = startQ.enq(pc);
  method ActionValue#(End) finished;
    endQ.deq;
    return endQ.first;
  endmethod
  method Action derefReq(Cell w) = dbox.deref(w);
  method ActionValue#(Cell) derefResp = dbox.derefResult;
endmodule

endpackage
