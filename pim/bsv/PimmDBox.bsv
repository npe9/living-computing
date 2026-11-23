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
//                it.  Two lists or two vectors of the same size (up to
//                six) answer UGoal: they are not unified here, a goal
//                of the stub unify_step does it (asm/pimm_stubs.py).
//                Anything else is UUnimp.
//   step(a, b, i)  that goal's step: unify element i of a and of b,
//                each taken with its MRB on if its structure's is.
//                The result is unify's.
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
  struct { Cell a; Cell b; } UGoal;   // two lists or two short vectors: the caller
                                      // has the goal box make the goal that unifies
                                      // their elements (PDSS: emulator/unify.c)
} UResult deriving (Bits, Eq);

interface PimmDBox;
  method Action deref(Cell w);
  method ActionValue#(Cell) derefResult;
  method Action unify(Cell a, Cell b);
  method Action step(Cell a, Cell b, Bit#(3) i);
  method ActionValue#(UResult) unifyResult;
endinterface

typedef enum { DIdle, DChase, DArrived, DStep1, DStep2 } DState deriving (Bits, Eq);

typedef union tagged {
  Cell Deref;
  struct { Cell a; Cell b; } Unify;
  struct { Cell a; Cell b; Bit#(3) i; } Step;
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
  // a reference on the way had its MRB on: so has the result (PDSS
  // emulator/deref.c)
  Reg#(Bool)    pathOn   <- mkReg(False);
  FIFO#(DReq)    reqQ   <- mkFIFO;
  FIFO#(Cell)    derefQ <- mkFIFO;
  FIFO#(UResult) unifyQ <- mkFIFO;

  function Action chase(Cell w, Bool on);
    action
      cur <= w;
      pathOn <= on || (isRef(w) && w.tag[0] == 1);
      if (isRef(w)) begin
        if (!inMemory(w.val)) fatal("reference outside memory");
        mem.read(cellAddr(w));
        st <= DChase;
      end
      else st <= DArrived;
    endaction
  endfunction

  // what the step takes from an element cell: a reference to it if it
  // is unbound, else its value; the MRB on if the structure's is
  function Cell elementOf(Cell c, Cell s, Addr at);
    Bool on = s.tag[0] == 1;
    return isUnboundCell(c) ? mkCell(on ? tag_REFx : tag_REFo, absAddr(at)) : (on ? marked(c) : c);
  endfunction
  Reg#(Cell) stepA <- mkRegU;
  Reg#(Cell) stepB <- mkRegU;
  Reg#(Addr) stepI <- mkRegU;

  function UResult bound(Cell was) = isHook(was) ? tagged UWake was.val : tagged UOk;

  rule accept (st == DIdle);
    reqQ.deq;
    case (reqQ.first) matches
      tagged Deref .w: begin
        isUnify <= False;
        chase(w, False);
      end
      tagged Unify .u: begin
        isUnify <= True;
        second <= False;
        pending <= u.b;
        chase(u.a, False);
      end
      tagged Step .q: begin
        isUnify <= True;
        second <= False;
        stepA <= q.a;
        stepB <= q.b;
        stepI <= zeroExtend(q.i);
        mem.read(cellAddr(q.a) + zeroExtend(q.i));
        st <= DStep1;
      end
    endcase
  endrule

  rule step1 (st == DStep1);
    let c <- mem.data;
    first <= elementOf(c, stepA, cellAddr(stepA) + stepI);   // held until b's is read
    mem.read(cellAddr(stepB) + stepI);
    st <= DStep2;
  endrule

  rule step2 (st == DStep2);
    let c <- mem.data;
    pending <= elementOf(c, stepB, cellAddr(stepB) + stepI);
    chase(first, False);
  endrule

  rule follow (st == DChase);
    let c <- mem.data;
    if (isUnboundCell(c)) begin        // cur refers to an unbound cell
      curCell <= c;
      st <= DArrived;
    end
    else chase(c, pathOn);
  endrule

  rule arrived (st == DArrived);
    let arrivedAt = pathOn ? marked(cur) : cur;
    if (!isUnify) begin
      derefQ.enq(arrivedAt);
      st <= DIdle;
    end
    else if (!second) begin
      first <= arrivedAt;
      firstCell <= curCell;
      second <= True;
      chase(pending, False);
    end
    else begin
      let a = first;
      let b = arrivedAt;
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
      else if ((a.tag & 8'hfe) == tag_LISTo
               || ((a.tag & 8'hfe) >= tag_VECT0o + 2 && (a.tag & 8'hfe) <= tag_VECT0o + 12))
        r = tagged UGoal { a: a, b: b };
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
  method Action step(Cell a, Cell b, Bit#(3) i) = reqQ.enq(tagged Step { a: a, b: b, i: i });
  method ActionValue#(UResult) unifyResult;
    unifyQ.deq;
    return unifyQ.first;
  endmethod
endmodule

endpackage
