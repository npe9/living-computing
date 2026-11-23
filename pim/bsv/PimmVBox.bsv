// PIM/m core: the vector box.  Multi-cycle vector built-ins over
// memory.  A vector of n = 1..6 elements is {VECTn, address} -> n
// cells, no header; the empty vector is {VECT0, 0}.  A vector of 7 or
// more is {VECT, a} -> {VDESC, a+3}, {INT, n}, {INT, n}, then the n
// elements (library/kbn/kbnheap.kl1, the linker's heap writer: the
// only source, the IPL image holds no such vector).  Why the length
// is there twice is not known; this box reads the first and writes
// both.
//
//   info(v)              a = the number of elements, b = a reference
//                        to the first
//   element(v, i)        a = element i; if that cell is an unbound
//                        variable, a reference to it
//   newVec(n)            a = a new vector of n cells holding integer 0
//                        ("All elements of the vector are initialized
//                        with integer 0", PIMOS manual, new_vector)
//   build(n)             a = a new vector of n >= 7 cells, not
//                        written; b = a reference to the first (for
//                        put_vector, whose write_* fill it)
//   toModule(v)          a = the module object made of v's cells:
//                        {MOD, a} -> {CDESC, element 0's value}, then
//                        the other elements as they are
//                        (library/loader/loader.kl1: "First Element
//                        is for CDESC created by new_module"; the
//                        shape is that of the image's modules).  A
//                        copy; ok is False if element 0 is not the
//                        integer 06 << 24 | size - 1, or an element
//                        is an unbound cell in place (a reference
//                        to a variable is copied: the loader puts
//                        one where another module will be)
//   setElement(v, i, e)  a = a copy of v with element i replaced by e,
//                        b = the old element i.  When v's MRB is
//                        off (the path to it is single) the update
//                        is in place and a = v, unless the cell is
//                        itself an unbound variable.  In a copy an
//                        unbound element is a reference to the old
//                        cell, so the variable stays one variable,
//                        and the elements are marked.
//
// The caller checks that v is a vector of at least one element.  The
// box checks i against the size: ok is False when it is out of range
// (nothing is allocated then).
package PimmVBox;

import FIFO::*;
import PimmGen::*;
import PimmTypes::*;
import PimmMem::*;
import PimmGBox::*;

typedef struct { Cell a; Cell b; Bool ok; } VResult deriving (Bits);

interface PimmVBox;
  method Action info(Cell v);
  method Action element(Cell v, Bit#(32) i);
  method Action markElement(Cell v, Bit#(32) i);
  method Action newVec(Bit#(32) n);
  method Action build(Bit#(32) n);
  method Action toModule(Cell v);
  method Action setElement(Cell v, Bit#(32) i, Cell e);
  method ActionValue#(VResult) result;
endinterface

typedef enum { VKInfo, VKElem, VKMark, VKNew, VKSet, VKBuild, VKMod } VKind deriving (Bits, Eq);
typedef struct { VKind k; Cell v; Bit#(32) i; Cell e; } VReq deriving (Bits);
typedef enum { VIdle, VDesc, VLen, VGo, VElem, VAlloc, VHdr, VFill, VCopyRd, VCopyWr,
               VModHead, VModRd, VModWr, VSetRd }
  VState deriving (Bits, Eq);

// the number of elements of a short vector, from its tag
function Bit#(3) vectorSize(Cell c) = truncate((c.tag - tag_VECT0o) >> 1);
function Bool isLongVector(Cell c) = (c.tag & 8'hfe) == 8'h1e;

module mkPimmVBox#(MemPort mem, PimmGBox gbox)(PimmVBox);
  Reg#(VState)   st    <- mkReg(VIdle);
  Reg#(VReq)     rq    <- mkRegU;
  Reg#(Addr)     src   <- mkRegU;     // the old vector's first element
  Reg#(Bit#(32)) n     <- mkRegU;     // the number of elements
  Reg#(Addr)     obj   <- mkRegU;     // the new vector: what its word points at
  Reg#(Addr)     dst   <- mkRegU;     // ... and its first element
  Reg#(Bit#(2))  h     <- mkRegU;     // the descriptor cell in hand
  Reg#(Bit#(32)) k     <- mkRegU;     // the element in hand
  Reg#(Cell)     oldEl <- mkRegU;     // the element replaced
  FIFO#(VReq)    reqQ  <- mkFIFO;
  FIFO#(VResult) resQ  <- mkFIFO;

  Bool long = n > 6;
  function Addr off(Bit#(32) j) = truncate(j);
  // what is taken from a cell: its value, or a reference to it if it
  // is an unbound variable
  // the cell goes on holding it, so what is taken has its MRB on
  function Cell taken(Cell c, Addr a) = isUnboundCell(c) ? mkCell(tag_REFx, absAddr(a)) : marked(c);
  Bit#(8) newTag = long ? 8'h1f : tag_VECT0o + (truncate(n) << 1) + 1;

  function Action answer(Cell a, Cell b, Bool ok);
    action
      resQ.enq(VResult { a: a, b: b, ok: ok });
      st <= VIdle;
    endaction
  endfunction

  rule accept (st == VIdle);
    let q = reqQ.first;
    reqQ.deq;
    rq <= q;
    k <= 0;
    h <= 0;
    if (q.k == VKNew || q.k == VKBuild) begin
      n <= q.i;
      st <= VGo;
    end
    else if (isLongVector(q.v)) begin
      mem.read(cellAddr(q.v));
      st <= VDesc;
    end
    else begin
      src <= cellAddr(q.v);
      n <= zeroExtend(vectorSize(q.v));
      st <= VGo;
    end
  endrule

  rule gotDesc (st == VDesc);
    let c <- mem.data;
    src <= cellAddr(c);
    mem.read(cellAddr(rq.v) + 1);
    st <= VLen;
  endrule

  rule gotLen (st == VLen);
    let c <- mem.data;
    n <= c.val;
    st <= VGo;
  endrule

  rule go (st == VGo);
    if (rq.k == VKInfo) answer(intC(n), mkCell(tag_REFo, absAddr(src)), True);
    else if (rq.k == VKNew && n == 0) answer(mkCell(tag_VECT0o, 0), ?, True);
    else if ((rq.k == VKElem || rq.k == VKMark || rq.k == VKSet) && rq.i >= n) answer(?, ?, False);
    else if (rq.k == VKSet && rq.v.tag[0] == 0) begin
      // the path to the vector is single: in place, unless the cell is
      // itself an unbound variable
      mem.read(src + off(rq.i));
      st <= VSetRd;
    end
    else if (rq.k == VKElem || rq.k == VKMark) begin
      mem.read(src + off(rq.i));
      st <= VElem;
    end
    else if (rq.k == VKMod) begin
      if (n == 0) answer(?, ?, False);
      else begin
        mem.read(src);
        st <= VModHead;
      end
    end
    else begin
      gbox.alloc(off(long ? n + 3 : n));
      st <= VAlloc;
    end
  endrule

  rule setInPlace (st == VSetRd);
    let c <- mem.data;
    if (isUnboundCell(c)) begin
      gbox.alloc(off(long ? n + 3 : n));
      st <= VAlloc;
    end
    else begin
      mem.write(src + off(rq.i), rq.e);
      answer(rq.v, c, True);
    end
  endrule

  rule gotElem (st == VElem);
    let c <- mem.data;
    // markElement: the element's MRB on in the vector too (PDSS
    // b_vector_element, mark_element)
    if (rq.k == VKMark && !isUnboundCell(c) && marked(c) != c) mem.write(src + off(rq.i), marked(c));
    answer(taken(c, src + off(rq.i)), ?, True);
  endrule

  // new_module: element 0 must be the descriptor's value
  rule modHead (st == VModHead);
    let c <- mem.data;
    if ((c.tag & 8'hfe) != tag_INTo || c.val != ((32'h06000000) | (n - 1))) answer(?, ?, False);
    else begin
      oldEl <= c;
      gbox.alloc(off(n));
      st <= VAlloc;
    end
  endrule

  rule modRd (st == VModRd);
    if (k == n) answer(mkCell(tag_MOD, absAddr(obj)), ?, True);
    else begin
      mem.read(src + off(k));
      st <= VModWr;
    end
  endrule

  rule modWr (st == VModWr);
    let c <- mem.data;
    if (isUnboundCell(c)) answer(?, ?, False);
    else begin
      mem.write(obj + off(k), c);
      k <= k + 1;
      st <= VModRd;
    end
  endrule

  rule gotAllocMod (st == VAlloc && rq.k == VKMod);
    let a <- gbox.allocResult;
    obj <= a;
    mem.write(a, mkCell(tag_CDESC, oldEl.val));
    k <= 1;
    st <= VModRd;
  endrule

  rule gotAlloc (st == VAlloc && rq.k != VKMod);
    let a <- gbox.allocResult;
    obj <= a;
    dst <= long ? a + 3 : a;
    st <= long ? VHdr : (rq.k == VKNew) ? VFill : VCopyRd;
  endrule

  rule header (st == VHdr);
    mem.write(obj + zeroExtend(h), h == 0 ? mkCell(tag_VDESC, absAddr(dst)) : intC(n));
    h <= h + 1;
    if (h == 2) begin
      if (rq.k == VKBuild)
        answer(mkCell(newTag, absAddr(obj)), mkCell(tag_REFo, absAddr(dst)), True);
      else st <= (rq.k == VKNew) ? VFill : VCopyRd;
    end
  endrule

  rule fill (st == VFill);
    mem.write(dst + off(k), intC(0));
    // new_vector's is the only reference: MRB off
    if (k + 1 == n) answer(mkCell(newTag & 8'hfe, absAddr(obj)), ?, True);
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
    // the copy is a new vector: MRB off
    if (k + 1 == n) answer(mkCell(rq.v.tag & 8'hfe, absAddr(obj)), k == rq.i ? old : oldEl, True);
    else begin
      k <= k + 1;
      st <= VCopyRd;
    end
  endrule

  method Action info(Cell v) = reqQ.enq(VReq { k: VKInfo, v: v, i: ?, e: ? });
  method Action element(Cell v, Bit#(32) i) =
    reqQ.enq(VReq { k: VKElem, v: v, i: i, e: ? });
  method Action markElement(Cell v, Bit#(32) i) =
    reqQ.enq(VReq { k: VKMark, v: v, i: i, e: ? });
  method Action newVec(Bit#(32) nn) = reqQ.enq(VReq { k: VKNew, v: ?, i: nn, e: ? });
  method Action build(Bit#(32) nn) = reqQ.enq(VReq { k: VKBuild, v: ?, i: nn, e: ? });
  method Action toModule(Cell v) = reqQ.enq(VReq { k: VKMod, v: v, i: ?, e: ? });
  method Action setElement(Cell v, Bit#(32) i, Cell e) =
    reqQ.enq(VReq { k: VKSet, v: v, i: i, e: e });
  method ActionValue#(VResult) result;
    resQ.deq;
    return resQ.first;
  endmethod
endmodule

endpackage
