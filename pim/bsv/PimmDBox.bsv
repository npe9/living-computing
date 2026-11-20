// PIM/m core: the data box.  Multi-cycle dereference and unification
// over memory, one request at a time.
//
//   deref(w)     follow REF cells until a non-reference or a reference
//                to an unbound cell (UNDF, or HOOK when goals wait on
//                it); that word is the result
//   unify(a, b)  dereference both; bind an unbound side to the other
//                (one memory write), or compare two integers or two
//                atoms.  Binding a hooked variable answers UWake with
//                its suspension list: the caller has the goal box wake
//                it.  Anything else is UUnimp: this box does not yet
//                unify structures or strings.
package PimmDBox;

import FIFO::*;
import PimmGen::*;
import PimmTypes::*;
import PimmMem::*;

typedef union tagged {
  void     UOk;
  Bit#(32) UWake;       // bound; goals were waiting: the first suspension record
  void     UFail;
  void     UUnimp;
} UResult deriving (Bits, Eq, FShow);

interface PimmDBox;
  method Action deref(Cell w);
  method ActionValue#(Cell) derefResult;
  method Action unify(Cell a, Cell b);
  method ActionValue#(UResult) unifyResult;
endinterface

typedef enum { DIdle, DChase, DArrived } DState deriving (Bits, Eq);

typedef union tagged {
  Cell Deref;
  struct { Cell a; Cell b; } Unify;
} DReq deriving (Bits);

module mkPimmDBox#(MemPort mem)(PimmDBox);
  Reg#(DState)  st       <- mkReg(DIdle);
  Reg#(Cell)    cur      <- mkRegU;     // the word being followed
  Reg#(Cell)    curCell  <- mkRegU;     // the unbound cell cur refers to, if it does
  Reg#(Cell)    first    <- mkRegU;     // unify: side a, dereferenced
  Reg#(Cell)    firstCell <- mkRegU;
  Reg#(Cell)    pending  <- mkRegU;     // unify: side b, not yet followed
  Reg#(Bool)    isUnify  <- mkReg(False);
  Reg#(Bool)    second   <- mkReg(False);
  FIFO#(DReq)    reqQ   <- mkFIFO;
  FIFO#(Cell)    derefQ <- mkFIFO;
  FIFO#(UResult) unifyQ <- mkFIFO;

  function Action chase(Cell w);
    action
      cur <= w;
      if (isRef(w)) begin
        if (!inMemory(w.val)) fatal("reference outside memory");
        mem.read(cellAddr(w));
        st <= DChase;
      end
      else st <= DArrived;
    endaction
  endfunction

  function UResult bound(Cell was) = isHook(was) ? tagged UWake was.val : tagged UOk;

  rule accept (st == DIdle);
    reqQ.deq;
    case (reqQ.first) matches
      tagged Deref .w: begin
        isUnify <= False;
        chase(w);
      end
      tagged Unify .u: begin
        isUnify <= True;
        second <= False;
        pending <= u.b;
        chase(u.a);
      end
    endcase
  endrule

  rule follow (st == DChase);
    let c <- mem.data;
    if (isUnboundCell(c)) begin        // cur refers to an unbound cell
      curCell <= c;
      st <= DArrived;
    end
    else chase(c);
  endrule

  rule arrived (st == DArrived);
    if (!isUnify) begin
      derefQ.enq(cur);
      st <= DIdle;
    end
    else if (!second) begin
      first <= cur;
      firstCell <= curCell;
      second <= True;
      chase(pending);
    end
    else begin
      let a = first;
      let b = cur;
      UResult r = tagged UOk;
      if (isRef(a)) begin
        if (!(isRef(b) && b.val == a.val)) begin
          mem.write(cellAddr(a), b);
          r = bound(firstCell);
        end
      end
      else if (isRef(b)) begin
        mem.write(cellAddr(b), a);
        r = bound(curCell);
      end
      else if ((a.tag | 1) != (b.tag | 1)) r = tagged UFail;
      else if (isInt(a) || isAtom(a)) r = (a.val == b.val) ? tagged UOk : tagged UFail;
      else r = tagged UUnimp;
      unifyQ.enq(r);
      st <= DIdle;
    end
  endrule

  method Action deref(Cell w) = reqQ.enq(tagged Deref w);
  method ActionValue#(Cell) derefResult;
    derefQ.deq;
    return derefQ.first;
  endmethod
  method Action unify(Cell a, Cell b) = reqQ.enq(tagged Unify { a: a, b: b });
  method ActionValue#(UResult) unifyResult;
    unifyQ.deq;
    return unifyQ.first;
  endmethod
endmodule

endpackage
