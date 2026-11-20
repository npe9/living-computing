// PIM/m core: the string box.  Multi-cycle string built-ins over
// memory.  A string is {STRG, address} -> {CDESC, pad << 27 | type <<
// 24 | words}, then `words` cells of 32 bits with the elements packed
// from the top; type 3 is 8-bit elements, 4 is 16-bit
// (library/kbn/kbnheap.kl1 string_cdesc; the IPL image's message
// strings decode this way).
//
//   info(s)            a = {INT, length}, b = {INT, element bits}
//   element(s, i)      a = {INT, element i}
//   newStr(n, bits)    a = a new string of n zero elements
//   setElement(s,i,e)  a = a copy of s with element i set to e.  The
//                      machine could update in place when s is singly
//                      referenced; without MRB this box always copies.
//
// An index out of range, a size other than 8 or 16, or a pointer that
// is not at a descriptor stops the simulation: the built-in's
// exception is not modelled.
package PimmSBox;

import FIFO::*;
import PimmGen::*;
import PimmTypes::*;
import PimmMem::*;
import PimmGBox::*;

typedef struct { Cell a; Cell b; } SResult deriving (Bits);

interface PimmSBox;
  method Action info(Cell s);
  method Action element(Cell s, Bit#(32) i);
  method Action newStr(Bit#(32) n, Bit#(32) bits);
  method Action setElement(Cell s, Bit#(32) i, Bit#(32) e);
  method ActionValue#(SResult) result;
endinterface

typedef enum { KInfo, KElem, KNew, KSet } SKind deriving (Bits, Eq);

typedef struct { SKind k; Cell s; Bit#(32) i; Bit#(32) e; } SReq deriving (Bits);

typedef enum { SIdle, SDesc, SElem, SAlloc, SWrDesc, SFill, SCopyRd, SCopyWr }
  SState deriving (Bits, Eq);

module mkPimmSBox#(MemPort mem, PimmGBox gbox)(PimmSBox);
  Reg#(SState)   st    <- mkReg(SIdle);
  Reg#(SReq)     rq    <- mkRegU;
  Reg#(Bit#(32)) desc  <- mkRegU;     // the descriptor's value
  Reg#(Addr)     dst   <- mkRegU;     // the new string
  Reg#(Bit#(24)) k     <- mkRegU;     // the word being written
  FIFO#(SReq)    reqQ  <- mkFIFO;
  FIFO#(SResult) resQ  <- mkFIFO;

  Addr src = cellAddr(rq.s);
  function Addr toAddr(Bit#(24) v) = truncate(v);   // a word count or index as an address offset

  // from a descriptor
  function Bool     is16(Bit#(32) d)  = d[26:24] == 4;
  function Bit#(24) wordsOf(Bit#(32) d) = d[23:0];
  function Bit#(32) lengthOf(Bit#(32) d);
    Bit#(32) w = zeroExtend(wordsOf(d));
    return (is16(d) ? (w << 1) : (w << 2)) - zeroExtend(d[28:27]);
  endfunction

  // element i of a string with this descriptor: its word, the shift
  // that brings it to the bottom, its mask
  function Bit#(24) wordIx(Bit#(32) d, Bit#(32) i) = truncate(is16(d) ? (i >> 1) : (i >> 2));
  function Bit#(5)  shiftOf(Bit#(32) d, Bit#(32) i) =
    is16(d) ? (i[0] == 0 ? 16 : 0) : (24 - (zeroExtend(i[1:0]) << 3));
  function Bit#(32) maskOf(Bit#(32) d) = is16(d) ? 32'h0000ffff : 32'h000000ff;

  function Action answer(Cell a, Cell b);
    action
      resQ.enq(SResult { a: a, b: b });
      st <= SIdle;
    endaction
  endfunction

  rule accept (st == SIdle);
    let q = reqQ.first;
    reqQ.deq;
    rq <= q;
    if (q.k == KNew) begin
      // i = length, e = element bits
      if (q.e != 8 && q.e != 16) fatal("new_string: element size not 8 or 16");
      Bool w16 = q.e == 16;
      Bit#(32) words = w16 ? ((q.i + 1) >> 1) : ((q.i + 3) >> 2);
      Bit#(32) pad = (w16 ? (words << 1) : (words << 2)) - q.i;
      desc <= (pad << 27) | ((w16 ? 4 : 3) << 24) | words;
      gbox.alloc(truncate(words + 1));
      st <= SAlloc;
    end
    else begin
      if (!inMemory(q.s.val)) fatal("string pointer outside memory");
      mem.read(cellAddr(q.s));
      st <= SDesc;
    end
  endrule

  rule gotDesc (st == SDesc);
    let c <- mem.data;
    let d = c.val;
    if (c.tag != tag_CDESC) fatal("string without a descriptor");
    if (d[26:24] != 3 && d[26:24] != 4) fatal("string element type not 8 or 16 bits");
    desc <= d;
    if (rq.k == KInfo)
      answer(intC(lengthOf(d)), intC(is16(d) ? 16 : 8));
    else begin
      if (rq.i >= lengthOf(d)) fatal("string index out of range");
      if (rq.k == KElem) begin
        mem.read(src + 1 + toAddr(wordIx(d, rq.i)));
        st <= SElem;
      end
      else begin
        gbox.alloc(toAddr(wordsOf(d)) + 1);
        st <= SAlloc;
      end
    end
  endrule

  rule gotElem (st == SElem);
    let c <- mem.data;
    answer(intC((c.val >> shiftOf(desc, rq.i)) & maskOf(desc)), ?);
  endrule

  rule gotAlloc (st == SAlloc);
    let a <- gbox.allocResult;
    dst <= a;
    st <= SWrDesc;
  endrule

  rule wrDesc (st == SWrDesc);
    mem.write(dst, mkCell(tag_CDESC, desc));
    k <= 0;
    if (wordsOf(desc) == 0) answer(mkCell(tag_STRGx, absAddr(dst)), ?);
    else st <= (rq.k == KNew) ? SFill : SCopyRd;
  endrule

  function Action wrote();
    action
      if (k + 1 == wordsOf(desc)) answer(mkCell(tag_STRGx, absAddr(dst)), ?);
      else begin
        k <= k + 1;
        st <= (rq.k == KNew) ? SFill : SCopyRd;
      end
    endaction
  endfunction

  rule fill (st == SFill);
    mem.write(dst + 1 + toAddr(k), intC(0));
    wrote;
  endrule

  rule copyRd (st == SCopyRd);
    mem.read(src + 1 + toAddr(k));
    st <= SCopyWr;
  endrule

  rule copyWr (st == SCopyWr);
    let c <- mem.data;
    let sh = shiftOf(desc, rq.i);
    let m = maskOf(desc);
    Bit#(32) v = (k == wordIx(desc, rq.i)) ? ((c.val & ~(m << sh)) | ((rq.e & m) << sh)) : c.val;
    mem.write(dst + 1 + toAddr(k), intC(v));
    wrote;
  endrule

  method Action info(Cell s) = reqQ.enq(SReq { k: KInfo, s: s, i: ?, e: ? });
  method Action element(Cell s, Bit#(32) i) = reqQ.enq(SReq { k: KElem, s: s, i: i, e: ? });
  method Action newStr(Bit#(32) n, Bit#(32) bits) = reqQ.enq(SReq { k: KNew, s: ?, i: n, e: bits });
  method Action setElement(Cell s, Bit#(32) i, Bit#(32) e) =
    reqQ.enq(SReq { k: KSet, s: s, i: i, e: e });
  method ActionValue#(SResult) result;
    resQ.deq;
    return resQ.first;
  endmethod
endmodule

endpackage
