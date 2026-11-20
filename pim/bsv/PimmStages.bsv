// PIM/m core: the two stages.
//
//   mkPimmFetch  reads the cell at a code address
//   mkPimmExec   decodes it and carries it out: the register file, the
//                clause-selection state (the alternative clause, and
//                whether a guard met an unbound variable), using the
//                data box and the hash box for everything multi-cycle
//
// The machine is sequential here: the next fetch waits for the
// instruction before it.  No timing is claimed.
package PimmStages;

import FIFO::*;
import RegFile::*;
import PimmGen::*;
import PimmTypes::*;
import PimmMem::*;
import PimmDBox::*;
import PimmHBox::*;

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
  method Action setReg(Bit#(8) r, Cell w);     // untraced: a goal's arguments
  method Action enq(Fetched f);
  method ActionValue#(Step) out;
endinterface

typedef enum { XDecode, XDeref1, XDeref2, XUnify, XHash } XState deriving (Bits, Eq);

module mkPimmExec#(PimmDBox dbox, PimmHBox hbox)(PimmExec);
  RegFile#(Bit#(8), Cell) regs <- mkRegFileFull;
  Reg#(Maybe#(Addr)) alt     <- mkReg(tagged Invalid);  // next clause on guard failure
  Reg#(Bool)         waiting <- mkReg(False);           // a guard wanted a variable bound
  FIFO#(Fetched)     inQ     <- mkFIFO;
  FIFO#(Step)        outQ    <- mkFIFO;
  Reg#(XState)       st      <- mkReg(XDecode);
  Reg#(Cell)         opA     <- mkRegU;

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

  function Action wreg(Bit#(8) r, Cell w);
    action
      regs.upd(r, w);
      traceR(r, w);
    endaction
  endfunction

  function Action guardFail();
    action
      if (alt matches tagged Valid .a) finish(tagged Next a);
      else stop(EndError);
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
      if (waiting) stop(EndSusp);
      else begin
        alt <= tagged Invalid;
        finish(tagged Next (pc + 1));
      end
    end
    else if (op == op_suspend) stop(waiting ? EndSusp : EndFail);
    else if (op == op_switch_on_non_integer || op == op_hash_on_constant
             || op == op_not_less_than || op == op_b_add || op == op_b_subtract) begin
      dbox.deref(regs.sub(x));
      st <= XDeref1;
    end
    else if (op == op_put_integer) begin
      wreg(x, intCell(c16));
      finish(tagged Next (pc + 1));
    end
    else if (op == op_get_integer) begin
      dbox.unify(regs.sub(x), intCell(c16));
      st <= XUnify;
    end
    else if (op == op_get_value) begin
      dbox.unify(regs.sub(x), regs.sub(y));
      st <= XUnify;
    end
    else if (op == op_collect_value) finish(tagged Next (pc + 1));  // MRB reclamation: not modelled
    else if (op == op_proceed) stop(EndDone);
    else stop(EndUnimp);
  endrule

  rule deref1 (st == XDeref1);
    let a <- dbox.derefResult;
    if (op == op_switch_on_non_integer) begin
      if (isRef(a)) waiting <= True;
      finish(tagged Next (isInt(a) ? pc + 1 : labelOf(pc, c16)));
    end
    else if (op == op_hash_on_constant) begin
      if (isRef(a)) waiting <= True;
      hbox.lookup(pc, a, c16, !isRef(a));
      st <= XHash;
    end
    else begin
      opA <= a;
      dbox.deref(regs.sub(y));
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
      if (isRef(a) || isRef(b)) waiting <= True;
      if (isInt(a) && isInt(b) && ia >= ib) finish(tagged Next (pc + 1));
      else guardFail;
    end
    else if (!isInt(a) || !isInt(b))
      stop(EndUnimp);     // a body built-in waiting on a variable, or its exception
    else begin
      // body arithmetic: r[z] := r[x] op r[y]
      wreg(z, mkCell(tag_INTo, pack(op == op_b_add ? ia + ib : ia - ib)));
      finish(tagged Next (pc + 1));
    end
  endrule

  rule hashed (st == XHash);
    let t <- hbox.target;
    finish(tagged Next t);
  endrule

  rule unified (st == XUnify);
    let r <- dbox.unifyResult;
    case (r)
      UOk:    finish(tagged Next (pc + 1));
      UFail:  stop(EndFail);
      UUnimp: stop(EndUnimp);
    endcase
  endrule

  method Action newGoal;
    alt <= tagged Invalid;
    waiting <= False;
  endmethod

  method Action setReg(Bit#(8) r, Cell w) = regs.upd(r, w);
  method Action enq(Fetched f) = inQ.enq(f);
  method ActionValue#(Step) out;
    outQ.deq;
    return outQ.first;
  endmethod
endmodule

endpackage
