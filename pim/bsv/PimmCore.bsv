// PIM/m core: memory, registers, the boxes, the two stages, and the
// rules that move an instruction between them and take the next goal.
//
// A goal is made by loading the argument registers and spawning it;
// `run` then takes goals from the ready queue, newest first, until the
// queue is empty (Idle) or the model stops loud.  A goal that cannot
// choose a clause is written back to memory, hooked on the variables
// it waits for, and woken when one is bound.
package PimmCore;

import FIFO::*;
import Vector::*;
import PimmGen::*;
import PimmTypes::*;
import PimmMem::*;
import PimmRegs::*;
import PimmDBox::*;
import PimmHBox::*;
import PimmGBox::*;
import PimmSBox::*;
import PimmVBox::*;
import PimmStages::*;

interface PimmCore;
  method Action newVar;                         // a fresh unbound variable
  method ActionValue#(Cell) newVarResult;
  method Action setArg(Bit#(8) n, Cell w);      // argument n (from 1) of the goal being built
  method Action spawn(Addr pc, Bit#(8) argn);
  method Action run;
  method ActionValue#(End) finished;
  // between runs: bind or compare two terms, look at a term
  method Action unifyReq(Cell a, Cell b);
  method ActionValue#(Bool) unifyDone;
  method Action derefReq(Cell w);
  method ActionValue#(Cell) derefResp;
  // between runs: make strings
  method Action newString(Bit#(32) n, Bit#(32) bits);
  method Action setElement(Cell s, Bit#(32) i, Bit#(32) e);
  method ActionValue#(Cell) stringResult;
endinterface

module mkPimmCore#(String image)(PimmCore);
  PimmMem   mem   <- mkPimmMem(image);
  PimmRegs  regs  <- mkPimmRegs;
  PimmFetch fetch <- mkPimmFetch(mem.port[0]);
  PimmHBox  hbox  <- mkPimmHBox(mem.port[1]);
  PimmDBox  dbox  <- mkPimmDBox(mem.port[2]);
  PimmGBox  gbox  <- mkPimmGBox(mem.port[3], regs);
  PimmSBox  sbox  <- mkPimmSBox(mem.port[4], gbox);
  PimmVBox  vbox  <- mkPimmVBox(mem.port[6], gbox);
  PimmExec  exec  <- mkPimmExec(regs, dbox, hbox, gbox, sbox, vbox, mem.port[5]);

  FIFO#(Bool) runQ   <- mkFIFO;
  FIFO#(End)  endQ   <- mkFIFO;
  FIFO#(Bool) unifyQ <- mkFIFO;
  Reg#(Bool)  outsideUnify <- mkReg(False);   // a unifyReq is in the data box
  Reg#(Bool)  outsideWake  <- mkReg(False);   // ... and its wake in the goal box

  rule toExec;
    let f <- fetch.out;
    exec.enq(f);
  endrule

  (* descending_urgency = "advance, begin_run" *)
  rule advance;
    let s <- exec.out;
    case (s) matches
      tagged Next .pc: fetch.enq(pc);
      tagged Stop .e:
        if (e == EndDone || e == EndSusp) gbox.pickup;   // on to the next goal
        else endQ.enq(e);
    endcase
  endrule

  rule begin_run;
    runQ.deq;
    gbox.pickup;
  endrule

  rule next_goal;
    let m <- gbox.picked;
    case (m) matches
      tagged Valid .pc: begin
        exec.newGoal;
        fetch.enq(pc);
      end
      tagged Invalid: begin
        $display("Q");
        endQ.enq(EndIdle);
      end
    endcase
  endrule

  rule outside_unified (outsideUnify);
    let r <- dbox.unifyResult;
    outsideUnify <= False;
    case (r) matches
      tagged UWake .s: begin
        gbox.wake(s);
        outsideWake <= True;
      end
      tagged UOk: unifyQ.enq(True);
      default:    unifyQ.enq(False);
    endcase
  endrule

  rule outside_woke (outsideWake);
    gbox.done;
    outsideWake <= False;
    unifyQ.enq(True);
  endrule

  method Action newVar = gbox.newVar;
  method ActionValue#(Cell) newVarResult = gbox.newVarResult;
  method Action setArg(Bit#(8) n, Cell w) = regs.wa(n, w);
  method Action spawn(Addr pc, Bit#(8) argn) =
    gbox.record(fromInteger(lay_READY), pc, argn, True, False);
  method Action run = runQ.enq(True);
  method ActionValue#(End) finished;
    endQ.deq;
    return endQ.first;
  endmethod
  method Action unifyReq(Cell a, Cell b);
    dbox.unify(a, b);
    outsideUnify <= True;
  endmethod
  method ActionValue#(Bool) unifyDone;
    unifyQ.deq;
    return unifyQ.first;
  endmethod
  method Action derefReq(Cell w) = dbox.deref(w);
  method ActionValue#(Cell) derefResp = dbox.derefResult;
  method Action newString(Bit#(32) n, Bit#(32) bits) = sbox.newStr(n, bits);
  method Action setElement(Cell s, Bit#(32) i, Bit#(32) e) = sbox.setElement(s, i, e);
  method ActionValue#(Cell) stringResult;
    let r <- sbox.result;
    return r.a;
  endmethod
endmodule

endpackage
