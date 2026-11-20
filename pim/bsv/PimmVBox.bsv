// PIM/m core: the vector box.  Multi-cycle vector built-ins over
// memory.  A vector of n = 1..6 elements is {VECTn, address} -> n
// cells, no header (library/kbn/kbnheap.kl1); the empty vector is
// {VECT0, 0}.  Longer vectors have a descriptor and are not handled:
// the caller must not ask.
//
//   element(v, i)        a = element i; if that cell is an unbound
//                        variable, a reference to it
//   newVec(n)            a = a new vector of n cells holding integer 0
//                        ("All elements of the vector are initialized
//                        with integer 0", PIMOS manual, new_vector)
//   setElement(v, i, e)  a = a copy of v with element i replaced by e,
//                        b = the old element i.  The machine updates
//                        in place when v is singly referenced; without
//                        MRB this box always copies.  An unbound
//                        element is copied as a reference to the old
//                        cell, so the variable stays one variable.
//
// The caller checks that v is a vector of 1..6 elements, i is in range
// and n is at most 6.
package PimmVBox;

import FIFO::*;
import PimmGen::*;
import PimmTypes::*;
import PimmMem::*;
import PimmGBox::*;

typedef struct { Cell a; Cell b; } VResult deriving (Bits);

interface PimmVBox;
  method Action element(Cell v, Bit#(32) i);
  method Action newVec(Bit#(32) n);
  method Action setElement(Cell v, Bit#(32) i, Cell e);
  method ActionValue#(VResult) result;
endinterface

typedef enum { VKElem, VKNew, VKSet } VKind deriving (Bits, Eq);
typedef struct { VKind k; Cell v; Bit#(3) i; Cell e; } VReq deriving (Bits);
typedef enum { VIdle, VElem, VAlloc, VFill, VCopyRd, VCopyWr } VState deriving (Bits, Eq);

// the number of elements of a short vector, from its tag
function Bit#(3) vectorSize(Cell c) = truncate((c.tag - tag_VECT0o) >> 1);

module mkPimmVBox#(MemPort mem, PimmGBox gbox)(PimmVBox);
  Reg#(VState)   st    <- mkReg(VIdle);
  Reg#(VReq)     rq    <- mkRegU;
  Reg#(Addr)     dst   <- mkRegU;     // the new vector
  Reg#(Bit#(3))  k     <- mkRegU;     // the cell in hand
  Reg#(Cell)     oldEl <- mkRegU;     // the element replaced
  FIFO#(VReq)    reqQ  <- mkFIFO;
  FIFO#(VResult) resQ  <- mkFIFO;

  Addr src = cellAddr(rq.v);
  // a new vector's size: i for newVec, the old vector's for setElement
  Bit#(3) n = rq.k == VKNew ? rq.i : vectorSize(rq.v);
  function Addr off(Bit#(3) j) = zeroExtend(j);
  // what is taken from a cell: its value, or a reference to it if it
  // is an unbound variable
  function Cell taken(Cell c, Addr a) = isUnboundCell(c) ? mkCell(tag_REFo, absAddr(a)) : c;

  function Action answer(Cell a, Cell b);
    action
      resQ.enq(VResult { a: a, b: b });
      st <= VIdle;
    endaction
  endfunction

  rule accept (st == VIdle);
    let q = reqQ.first;
    reqQ.deq;
    rq <= q;
    k <= 0;
    if (q.k == VKElem) begin
      mem.read(cellAddr(q.v) + off(q.i));
      st <= VElem;
    end
    else if (q.k == VKNew && q.i == 0) answer(mkCell(tag_VECT0o, 0), ?);
    else begin
      gbox.alloc(zeroExtend(q.k == VKNew ? q.i : vectorSize(q.v)));
      st <= VAlloc;
    end
  endrule

  rule gotElem (st == VElem);
    let c <- mem.data;
    answer(taken(c, src + off(rq.i)), ?);
  endrule

  rule gotAlloc (st == VAlloc);
    let a <- gbox.allocResult;
    dst <= a;
    st <= (rq.k == VKNew) ? VFill : VCopyRd;
  endrule

  rule fill (st == VFill);
    mem.write(dst + off(k), intC(0));
    if (k + 1 == n) answer(mkCell(tag_VECT0o + (zeroExtend(n) << 1) + 1, absAddr(dst)), ?);
    else k <= k + 1;
  endrule

  rule copyRd (st == VCopyRd);
    mem.read(src + off(k));
    st <= VCopyWr;
  endrule

  rule copyWr (st == VCopyWr);
    let c <- mem.data;
    Cell old = taken(c, src + off(k));
    mem.write(dst + off(k), k == rq.i ? rq.e : old);
    if (k == rq.i) oldEl <= old;
    if (k + 1 == n) answer(mkCell(rq.v.tag, absAddr(dst)), k == rq.i ? old : oldEl);
    else begin
      k <= k + 1;
      st <= VCopyRd;
    end
  endrule

  method Action element(Cell v, Bit#(32) i) =
    reqQ.enq(VReq { k: VKElem, v: v, i: truncate(i), e: ? });
  method Action newVec(Bit#(32) nn) = reqQ.enq(VReq { k: VKNew, v: ?, i: truncate(nn), e: ? });
  method Action setElement(Cell v, Bit#(32) i, Cell e) =
    reqQ.enq(VReq { k: VKSet, v: v, i: truncate(i), e: e });
  method ActionValue#(VResult) result;
    resQ.deq;
    return resQ.first;
  endmethod
endmodule

endpackage
