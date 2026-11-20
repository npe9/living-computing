// PIM/m core: the two stages.
//
//   mkPimmFetch  reads the cell at a code address
//   mkPimmExec   decodes it and carries it out: the clause-selection
//                state (the alternative clause, and the variables
//                guards met unbound), using the data box, the hash box
//                and the goal box for everything multi-cycle
//
// The machine is sequential here: the next fetch waits for the
// instruction before it.  No timing is claimed.
package PimmStages;

import FIFO::*;
import RegFile::*;
import PimmGen::*;
import PimmTypes::*;
import PimmMem::*;
import PimmRegs::*;
import PimmDBox::*;
import PimmHBox::*;
import PimmGBox::*;

interface PimmFetch;
  method Action enq(Addr pc);
  method ActionValue#(Fetched) out;
endinterface

module mkPimmFetch#(MemPort mem)(PimmFetch);
  FIFO#(Addr) pcs <- mkFIFO;

  method Action enq(Addr pc);
    mem.read(pc);
    pcs.enq(pc);
  endmethod

  method ActionValue#(Fetched) out;
    let c <- mem.data;
    pcs.deq;
    return Fetched { pc: pcs.first, word: c };
  endmethod
endmodule

interface PimmExec;
  method Action newGoal;                       // clear the clause-selection state
  method Action enq(Fetched f);
  method ActionValue#(Step) out;
endinterface

typedef enum { XDecode, XDeref1, XDeref2, XNote2, XUnify, XWake, XHash,
               XSusp1, XSusp2, XSusp3 } XState deriving (Bits, Eq);

module mkPimmExec#(PimmRegs regs, PimmDBox dbox, PimmHBox hbox, PimmGBox gbox)(PimmExec);
  Reg#(Maybe#(Addr)) alt     <- mkReg(tagged Invalid);  // next clause on guard failure
  // the variables guards wanted bound, in the order met (a variable
  // met twice is there twice)
  RegFile#(Bit#(4), Addr) noted <- mkRegFileFull;
  Reg#(Bit#(5))      nNoted  <- mkReg(0);
  FIFO#(Fetched)     inQ     <- mkFIFO;
  FIFO#(Step)        outQ    <- mkFIFO;
  Reg#(XState)       st      <- mkReg(XDecode);
  Reg#(Cell)         opA     <- mkRegU;
  Reg#(Addr)         sGoal   <- mkRegU;     // suspending: the record
  Reg#(Bit#(5))      sI      <- mkRegU;     // suspending: the variable being hooked

  // the instruction in hand
  let pc   = inQ.first.pc;
  let ins  = inQ.first.word;
  Bit#(16) op  = { ins.tag, ins.val[31:24] };
  Bit#(8)  x   = ins.val[23:16];
  Bit#(8)  y   = ins.val[15:8];
  Bit#(8)  z   = ins.val[7:0];
  Bit#(16) c16 = ins.val[15:0];

  function Action finish(Step s);
    action
      inQ.deq;
      outQ.enq(s);
      st <= XDecode;
    endaction
  endfunction

  function Action stop(End e);
    action
      case (e)
        EndDone:  $display("E done");
        EndFail:  $display("E fail");
        EndSusp:  $display("E susp");
        EndUnimp: $display("E unimp");
        EndError: $display("E error");
      endcase
      finish(tagged Stop e);
    endaction
  endfunction

  function Action guardFail();
    action
      if (alt matches tagged Valid .a) finish(tagged Next a);
      else stop(EndError);
    endaction
  endfunction

  function Action note(Cell a);
    action
      if (nNoted == 16) fatal("more than 16 variables noted by guards");
      noted.upd(truncate(nNoted), cellAddr(a));
      nNoted <= nNoted + 1;
    endaction
  endfunction

  // The goal goes back to memory as a suspended record, entry = the
  // label, arguments r[0..x), then is hooked on each noted variable.
  function Action suspendGoal();
    action
      gbox.record(fromInteger(lay_SUSPENDED), labelOf(pc, c16), x, False, True);
      st <= XSusp1;
    endaction
  endfunction

  rule decode (st == XDecode);
    traceI(pc, ins);
    if (ins.tag != tag_GMI && ins.tag != tag_KLB) stop(EndError);
    else if (op == op_try_me_else) begin
      alt <= tagged Valid labelOf(pc, c16);
      finish(tagged Next (pc + 1));
    end
    else if (op == op_otherwise) begin
      // clauses below apply only if none above can
      if (nNoted != 0) suspendGoal;
      else begin
        alt <= tagged Invalid;
        finish(tagged Next (pc + 1));
      end
    end
    else if (op == op_suspend) begin
      if (nNoted != 0) suspendGoal;
      else stop(EndFail);
    end
    else if (op == op_switch_on_non_integer || op == op_hash_on_constant
             || op == op_not_less_than || op == op_b_add || op == op_b_subtract) begin
      dbox.deref(regs.r(x));
      st <= XDeref1;
    end
    else if (op == op_put_integer) begin
      regs.wr(x, intCell(c16));
      finish(tagged Next (pc + 1));
    end
    else if (op == op_get_integer) begin
      dbox.unify(regs.r(x), intCell(c16));
      st <= XUnify;
    end
    else if (op == op_get_value) begin
      dbox.unify(regs.r(x), regs.r(y));
      st <= XUnify;
    end
    else if (op == op_collect_value) finish(tagged Next (pc + 1));  // MRB reclamation: not modelled
    else if (op == op_proceed) stop(EndDone);
    else stop(EndUnimp);
  endrule

  rule deref1 (st == XDeref1);
    let a <- dbox.derefResult;
    if (op == op_switch_on_non_integer) begin
      if (isRef(a)) note(a);
      finish(tagged Next (isInt(a) ? pc + 1 : labelOf(pc, c16)));
    end
    else if (op == op_hash_on_constant) begin
      if (isRef(a)) note(a);
      hbox.lookup(pc, a, c16, !isRef(a));
      st <= XHash;
    end
    else begin
      opA <= a;
      dbox.deref(regs.r(y));
      st <= XDeref2;
    end
  endrule

  rule deref2 (st == XDeref2);
    let b <- dbox.derefResult;
    let a = opA;
    Int#(32) ia = unpack(a.val);
    Int#(32) ib = unpack(b.val);
    if (op == op_not_less_than) begin
      // guard: r[x] >= r[y]; an unbound operand is noted and the guard fails
      if (isRef(a) && isRef(b)) begin
        note(a);
        opA <= b;
        st <= XNote2;
      end
      else if (isRef(a) || isRef(b)) begin
        note(isRef(a) ? a : b);
        guardFail;
      end
      else if (isInt(a) && isInt(b) && ia >= ib) finish(tagged Next (pc + 1));
      else guardFail;
    end
    else if (!isInt(a) || !isInt(b))
      stop(EndUnimp);     // a body built-in waiting on a variable, or its exception
    else begin
      // body arithmetic: r[z] := r[x] op r[y]
      regs.wr(z, mkCell(tag_INTo, pack(op == op_b_add ? ia + ib : ia - ib)));
      finish(tagged Next (pc + 1));
    end
  endrule

  rule note2 (st == XNote2);
    note(opA);
    guardFail;
  endrule

  rule hashed (st == XHash);
    let t <- hbox.target;
    finish(tagged Next t);
  endrule

  rule unified (st == XUnify);
    let r <- dbox.unifyResult;
    case (r) matches
      tagged UOk:      finish(tagged Next (pc + 1));
      tagged UWake .s: begin
        gbox.wake(s);
        st <= XWake;
      end
      tagged UFail:    stop(EndFail);
      tagged UUnimp:   stop(EndUnimp);
    endcase
  endrule

  rule woke (st == XWake);
    gbox.done;
    finish(tagged Next (pc + 1));
  endrule

  rule susp1 (st == XSusp1);
    let g <- gbox.recordResult;
    sGoal <= g;
    sI <= 0;
    st <= XSusp2;
  endrule

  rule susp2 (st == XSusp2);
    gbox.hook(sGoal, noted.sub(truncate(sI)));
    st <= XSusp3;
  endrule

  rule susp3 (st == XSusp3);
    gbox.done;
    if (sI + 1 == nNoted) stop(EndSusp);
    else begin
      sI <= sI + 1;
      st <= XSusp2;
    end
  endrule

  method Action newGoal;
    alt <= tagged Invalid;
    nNoted <= 0;
  endmethod

  method Action enq(Fetched f) = inQ.enq(f);
  method ActionValue#(Step) out;
    outQ.deq;
    return outQ.first;
  endmethod
endmodule

endpackage
