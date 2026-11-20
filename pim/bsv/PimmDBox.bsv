// PIM/m core: the data box.  Multi-cycle dereference and unification
// over memory, one request at a time.
//
//   deref(w)     follow REF cells until a non-reference or a reference
//                to an unbound (UNDF) cell; that word is the result
//   unify(a, b)  dereference both; bind an unbound side to the other
//                (one memory write, traced), or compare two integers
//                or two atoms.  Anything else is UUnimp: this box does
//                not yet unify structures, strings, or hooked variables.
package PimmDBox;

import FIFO::*;
import PimmGen::*;
import PimmTypes::*;
import PimmMem::*;

typedef enum { UOk, UFail, UUnimp } UResult deriving (Bits, Eq, FShow);

interface PimmDBox;
  method Action deref(Cell w);
  method ActionValue#(Cell) derefResult;
  method Action unify(Cell a, Cell b);
  method ActionValue#(UResult) unifyResult;
  method Action poke(Addr a, Cell d);     // an untraced write, for a testbench
endinterface

typedef enum { DIdle, DChase, DArrived } DState deriving (Bits, Eq);

typedef union tagged {
  Cell Deref;
  struct { Cell a; Cell b; } Unify;
  struct { Addr a; Cell d; } Poke;
} DReq deriving (Bits);

module mkPimmDBox#(MemPort mem)(PimmDBox);
  Reg#(DState)  st      <- mkReg(DIdle);
  Reg#(Cell)    cur     <- mkRegU;      // the word being followed
  Reg#(Cell)    first   <- mkRegU;      // unify: side a, dereferenced
  Reg#(Cell)    pending <- mkRegU;      // unify: side b, not yet followed
  Reg#(Bool)    isUnify <- mkReg(False);
  Reg#(Bool)    second  <- mkReg(False);
  FIFO#(DReq)    reqQ   <- mkFIFO;
  FIFO#(Cell)    derefQ <- mkFIFO;
  FIFO#(UResult) unifyQ <- mkFIFO;

  function Action chase(Cell w);
    action
      cur <= w;
      if (isRef(w)) begin
        mem.read(cellAddr(w));
        st <= DChase;
      end
      else st <= DArrived;
    endaction
  endfunction

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
      tagged Poke .p: mem.write(p.a, p.d);
    endcase
  endrule

  rule follow (st == DChase);
    let c <- mem.data;
    if (c.tag == tag_UNDF) st <= DArrived;          // cur refers to an unbound cell
    else chase(c);
  endrule

  rule arrived (st == DArrived);
    if (!isUnify) begin
      derefQ.enq(cur);
      st <= DIdle;
    end
    else if (!second) begin
      first <= cur;
      second <= True;
      chase(pending);
    end
    else begin
      let a = first;
      let b = cur;
      UResult r = UOk;
      if (isRef(a)) begin
        if (!(isRef(b) && b.val == a.val)) begin
          mem.write(cellAddr(a), b);
          traceM(cellAddr(a), b);
        end
      end
      else if (isRef(b)) begin
        mem.write(cellAddr(b), a);
        traceM(cellAddr(b), a);
      end
      else if ((a.tag | 1) != (b.tag | 1)) r = UFail;
      else if (isInt(a) || isAtom(a)) r = (a.val == b.val) ? UOk : UFail;
      else r = UUnimp;
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
  method Action poke(Addr a, Cell d) = reqQ.enq(tagged Poke { a: a, d: d });
endmodule

endpackage
