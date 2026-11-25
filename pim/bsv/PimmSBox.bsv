// PIM/m core: the string box.  Multi-cycle string built-ins over
// memory.  A string is {STRG, address} -> {CDESC, pad << 27 | type <<
// 24 | words}, then `words` cells of 32 bits with the elements packed
// from the top; type 3 is 8-bit elements, 4 is 16-bit, 5 is 32-bit
// (library/kbn/kbnheap.kl1 string_cdesc; the IPL image's message
// strings decode this way).
//
//   info(s)            a = {INT, length}, b = {INT, element bits}
//   element(s, i)      a = {INT, element i}
//   newStr(n, bits)    a = a new string of n zero elements
//   poke(s, i, w)      word i := w in place: for the test bench only
//   show(s)            the string's descriptor and words as `S` trace lines
//   hashStr(s)         a = the hash code of the string (PDSS's function)
//   equal(s1, s2)      ok is whether the strings are the same, word for word
//   tryElement(s, i)   the same for a guard: ok is False when i is
//                      out of range
//   changeSize(s,bits) a = s with elements of `bits` bits (8, 16, 32).
//                      "The smallest index element occupies the
//                      highest order bits" and widening pads with zero
//                      elements (PIMOS manual, change_element_size):
//                      with the elements packed from the top that is
//                      the same words under another descriptor, so the
//                      words are copied as they are (the padding of a
//                      string is zero)
//   stringOp(op, s1, p1, n, p2, s2)
//                      a = a copy of s1 in which each of the n
//                      elements from p1 is replaced by operation `op`
//                      (0..15, the manual's table "General String
//                      Operations") of itself and the element of s2
//                      from p2; b = s2.  The copy is made first, then
//                      one word is rewritten per element.
//   search(s, i, e, c) a = {INT, the index of the first element equal
//                      to c from i to e, e included}, from the rear when
//                      e < i; -1 if none (search_character).  One word
//                      read per element
//   setElement(s,i,e)  a = a copy of s with element i set to e.  The
//                      machine could update in place when s is singly
//                      referenced; without MRB this box always copies.
//
// An index out of range, a size other than 8, 16 or 32 (new strings: 8
// or 16), strings of different sizes in stringOp, or a pointer that
// is not at a descriptor stops the simulation: the built-in's
// exception is not modelled.
package PimmSBox;

import FIFO::*;
import PimmGen::*;
import PimmTypes::*;
import PimmMem::*;
import PimmGBox::*;

typedef struct { Cell a; Cell b; Bool ok; } SResult deriving (Bits);

interface PimmSBox;
  method Action info(Cell s);
  method Action element(Cell s, Bit#(32) i);
  method Action tryElement(Cell s, Bit#(32) i);
  method Action newStr(Bit#(32) n, Bit#(32) bits);
  method Action setElement(Cell s, Bit#(32) i, Bit#(32) e);
  method Action changeSize(Cell s, Bit#(32) bits);
  method Action stringOp(Bit#(4) op, Cell s1, Bit#(32) p1, Bit#(32) n, Bit#(32) p2, Cell s2);
  method Action hashStr(Cell s);
  method Action equal(Cell s1, Cell s2);
  method Action show(Cell s);
  method Action poke(Cell s, Bit#(32) i, Bit#(32) w);
  method Action search(Cell s, Bit#(32) i, Bit#(32) e, Bit#(32) c);
  method ActionValue#(SResult) result;
endinterface

typedef enum { KInfo, KElem, KTry, KNew, KSet, KChg, KOp, KHash, KEq, KShow, KPoke, KSrch } SKind deriving (Bits, Eq);

typedef struct { SKind k; Cell s; Bit#(32) i; Bit#(32) e; Cell s2; Bit#(32) p2; Bit#(4) op; }
  SReq deriving (Bits);

typedef enum { SIdle, SDesc, SDesc2, SElem, SAlloc, SWrDesc, SFill, SCopyRd, SCopyWr,
               SOp0, SOp1, SOp2, SHash1, SHash2, SEq0, SEq1, SEq2, SEq3, SShow1, SShow2, SSrch }
  SState deriving (Bits, Eq);

module mkPimmSBox#(MemPort mem, PimmGBox gbox)(PimmSBox);
  Reg#(SState)   st    <- mkReg(SIdle);
  Reg#(SReq)     rq    <- mkRegU;
  Reg#(Bit#(32)) desc  <- mkRegU;     // the descriptor's value
  Reg#(Addr)     dst   <- mkRegU;     // the new string
  Reg#(Bit#(24)) k     <- mkRegU;     // the word being written
  Reg#(Bit#(32)) j     <- mkRegU;     // stringOp: the element in hand
  Reg#(Bit#(32)) e2    <- mkRegU;     // ... and s2's
  FIFO#(SReq)    reqQ  <- mkFIFO;
  FIFO#(SResult) resQ  <- mkFIFO;

  Addr src = cellAddr(rq.s);
  // a word count or index as an address offset (through 32 bits: the
  // address may be wider or narrower than a word count)
  function Addr toAddr(Bit#(24) v);
    Bit#(32) w = zeroExtend(v);
    return truncate(w);
  endfunction

  // from a descriptor
  // lg: log2 of the element bits (3, 4, 5); a word holds 1 << (5 - lg)
  function Bit#(3)  lgOf(Bit#(32) d) = d[26:24];
  function Bit#(24) wordsOf(Bit#(32) d) = d[23:0];
  function Bit#(32) lengthOf(Bit#(32) d);
    Bit#(32) w = zeroExtend(wordsOf(d));
    return (w << (5 - lgOf(d))) - zeroExtend(d[28:27]);
  endfunction
  function Bit#(32) bitsOf(Bit#(32) d) = 1 << lgOf(d);

  // element i of a string with this descriptor: its word, the shift
  // that brings it to the bottom, its mask
  function Bit#(24) wordIx(Bit#(32) d, Bit#(32) i) = truncate(i >> (5 - lgOf(d)));
  function Bit#(5)  shiftOf(Bit#(32) d, Bit#(32) i);
    Bit#(3) per = 5 - lgOf(d);
    Bit#(5) sub = truncate(i) & ((1 << per) - 1);
    return (((1 << per) - 1 - sub) << lgOf(d));
  endfunction
  function Bit#(32) maskOf(Bit#(32) d) =
    lgOf(d) == 5 ? 32'hffffffff : (lgOf(d) == 4 ? 32'h0000ffff : 32'h000000ff);

  function Bit#(32) operate(Bit#(4) o, Bit#(32) a, Bit#(32) b);
    case (o)
      0: return 0;
      1: return a & b;
      2: return ~a & b;
      3: return b;
      4: return a & ~b;
      5: return a;
      6: return a ^ b;
      7: return a | b;
      8: return ~(a | b);
      9: return ~(a ^ b);
      10: return ~a;
      11: return ~a | b;
      12: return ~b;
      13: return a | ~b;
      14: return ~(a & b);
      default: return 32'hffffffff;
    endcase
  endfunction

  function Action answer(Cell a, Cell b);
    action
      resQ.enq(SResult { a: a, b: b, ok: True });
      st <= SIdle;
    endaction
  endfunction

  rule accept (st == SIdle);
    let q = reqQ.first;
    reqQ.deq;
    rq <= q;
    if (q.k == KNew) begin
      // i = length, e = element bits
      if (q.e != 8 && q.e != 16 && q.e != 32) fatal("new_string: element size not 8, 16 or 32");
      Bit#(3) lgE = q.e == 32 ? 5 : (q.e == 16 ? 4 : 3);
      Bit#(3) sh = 5 - lgE;                     // log2 of the elements in a word
      Bit#(32) words = (q.i + (1 << sh) - 1) >> sh;
      Bit#(32) pad = (words << sh) - q.i;
      desc <= (pad << 27) | (zeroExtend(lgE) << 24) | words;
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
    if (d[26:24] != 3 && d[26:24] != 4 && d[26:24] != 5) fatal("string element type not 8, 16 or 32 bits");
    // changeSize: the same words under a new descriptor
    Bit#(3) lgN = rq.i == 8 ? 3 : (rq.i == 16 ? 4 : 5);
    Bit#(32) len = lengthOf(d);
    Bit#(32) newLen = lgN >= lgOf(d) ? ((len + (1 << (lgN - lgOf(d))) - 1) >> (lgN - lgOf(d)))
                                      : (len << (lgOf(d) - lgN));
    Bit#(32) pad = (zeroExtend(wordsOf(d)) << (5 - lgN)) - newLen;
    Bit#(32) changed = (pad << 27) | (zeroExtend(lgN) << 24) | zeroExtend(wordsOf(d));
    desc <= rq.k == KChg ? changed : d;
    if (rq.k == KInfo)
      answer(intC(lengthOf(d)), intC(bitsOf(d)));
    else if (rq.k == KTry && rq.i >= lengthOf(d)) begin
      resQ.enq(SResult { a: ?, b: ?, ok: False });
      st <= SIdle;
    end
    else if (rq.k == KChg) begin
      if (rq.i != 8 && rq.i != 16 && rq.i != 32) fatal("change_element_size: not 8, 16 or 32");
      gbox.alloc(toAddr(wordsOf(d)) + 1);
      st <= SAlloc;
    end
    else if (rq.k == KPoke) begin
      // the bench's: word i written where it is
      if (rq.i >= zeroExtend(wordsOf(d))) fatal("poke: word out of range");
      mem.write(src + 1 + toAddr(truncate(rq.i)), intC(rq.e));
      answer(rq.s, ?);
    end
    else if (rq.k == KSrch) begin
      // i = Start, e = End, p2 = the code
      if (rq.i >= lengthOf(d) || rq.e >= lengthOf(d)) fatal("search_character: out of range");
      if (lgOf(d) != 5 && (rq.p2 & ~maskOf(d)) != 0) fatal("search_character: code too wide");
      j <= rq.i;
      mem.read(src + 1 + toAddr(wordIx(d, rq.i)));
      st <= SSrch;
    end
    else if (rq.k == KShow) begin
      traceS(c);
      k <= 0;
      if (wordsOf(d) == 0) answer(?, ?);
      else st <= SShow1;
    end
    else if (rq.k == KHash) begin
      // words, then a mix of the first and the last word
      if (wordsOf(d) == 0) answer(intC(0), ?);
      else begin
        mem.read(src + 1);
        st <= SHash1;
      end
    end
    else if (rq.k == KEq) begin
      if (!inMemory(rq.s2.val)) fatal("string pointer outside memory");
      mem.read(cellAddr(rq.s2));
      st <= SEq0;
    end
    else if (rq.k == KOp) begin
      if (!inMemory(rq.s2.val)) fatal("string pointer outside memory");
      mem.read(cellAddr(rq.s2));
      st <= SDesc2;
    end
    else begin
      if (rq.i >= lengthOf(d)) fatal("string index out of range");
      if (rq.k == KElem || rq.k == KTry) begin
        mem.read(src + 1 + toAddr(wordIx(d, rq.i)));
        st <= SElem;
      end
      else begin
        gbox.alloc(toAddr(wordsOf(d)) + 1);
        st <= SAlloc;
      end
    end
  endrule

  rule gotDesc2 (st == SDesc2);
    let c <- mem.data;
    let d2 = c.val;
    if (c.tag != tag_CDESC || lgOf(d2) != lgOf(desc)) fatal("string_operation: strings of different kinds");
    // i = p1, e = n: both ranges must lie inside their strings
    if (rq.i + rq.e > lengthOf(desc) || rq.p2 + rq.e > lengthOf(d2) || rq.i + rq.e < rq.i)
      fatal("string_operation: out of range");
    gbox.alloc(toAddr(wordsOf(desc)) + 1);
    st <= SAlloc;
  endrule

  // stringOp, after the copy: element j of the range
  rule op0 (st == SOp0);
    mem.read(cellAddr(rq.s2) + 1 + toAddr(wordIx(desc, rq.p2 + j)));
    st <= SOp1;
  endrule

  rule op1 (st == SOp1);
    let c <- mem.data;
    e2 <= (c.val >> shiftOf(desc, rq.p2 + j)) & maskOf(desc);
    mem.read(dst + 1 + toAddr(wordIx(desc, rq.i + j)));
    st <= SOp2;
  endrule

  rule op2 (st == SOp2);
    let c <- mem.data;
    let sh = shiftOf(desc, rq.i + j);
    let m = maskOf(desc);
    Bit#(32) e1 = (c.val >> sh) & m;
    mem.write(dst + 1 + toAddr(wordIx(desc, rq.i + j)),
              intC((c.val & ~(m << sh)) | ((operate(rq.op, e1, e2) & m) << sh)));
    if (j + 1 == rq.e) answer(mkCell(tag_STRGx, absAddr(dst)), rq.s2);
    else begin
      j <= j + 1;
      st <= SOp0;
    end
  endrule

  // show: every word to the console trace
  rule show1 (st == SShow1);
    mem.read(src + 1 + toAddr(k));
    st <= SShow2;
  endrule

  rule show2 (st == SShow2);
    let c <- mem.data;
    traceS(c);
    if (k + 1 == wordsOf(desc)) answer(?, ?);
    else begin
      k <= k + 1;
      st <= SShow1;
    end
  endrule

  // hashStr: PDSS's function (emulator/blt_system.c blt_b_hash)
  rule hash1 (st == SHash1);
    let c <- mem.data;
    j <= c.val;
    mem.read(src + toAddr(wordsOf(desc)));
    st <= SHash2;
  endrule

  rule hash2 (st == SHash2);
    let c <- mem.data;
    let a = j;
    let b = c.val;
    answer(intC(zeroExtend(wordsOf(desc)) + a + (a >> 16) + (a >> 24)
                + (b << 1) + (b >> 15) + (b >> 23)), ?);
  endrule

  // equal: the descriptors, then every word (PDSS passive_unify)
  function Action differ();
    action
      resQ.enq(SResult { a: ?, b: ?, ok: False });
      st <= SIdle;
    endaction
  endfunction

  rule eq0 (st == SEq0);
    let c <- mem.data;
    k <= 0;
    if (c != mkCell(tag_CDESC, desc)) differ;
    else if (wordsOf(desc) == 0) answer(?, ?);
    else st <= SEq1;
  endrule

  rule eq1 (st == SEq1);
    mem.read(src + 1 + toAddr(k));
    st <= SEq2;
  endrule

  rule eq2 (st == SEq2);
    let c <- mem.data;
    j <= c.val;
    mem.read(cellAddr(rq.s2) + 1 + toAddr(k));
    st <= SEq3;
  endrule

  rule eq3 (st == SEq3);
    let c <- mem.data;
    if (c.val != j) differ;
    else if (k + 1 == wordsOf(desc)) answer(?, ?);
    else begin
      k <= k + 1;
      st <= SEq1;
    end
  endrule

  // search: element j in hand
  rule srch (st == SSrch);
    let c <- mem.data;
    if (((c.val >> shiftOf(desc, j)) & maskOf(desc)) == rq.p2) answer(intC(j), ?);
    else if (j == rq.e) answer(intC(32'hffffffff), ?);
    else begin
      Bit#(32) nj = rq.e > rq.i ? j + 1 : j - 1;
      j <= nj;
      mem.read(src + 1 + toAddr(wordIx(desc, nj)));
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
    j <= 0;
    if (wordsOf(desc) == 0) answer(mkCell(tag_STRGx, absAddr(dst)), rq.s2);
    else st <= (rq.k == KNew) ? SFill : SCopyRd;
  endrule

  function Action wrote();
    action
      if (k + 1 == wordsOf(desc)) begin
        if (rq.k == KOp && rq.e != 0) st <= SOp0;
        else answer(mkCell(tag_STRGx, absAddr(dst)), rq.s2);
      end
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
    Bit#(32) v = (rq.k == KSet && k == wordIx(desc, rq.i))
                 ? ((c.val & ~(m << sh)) | ((rq.e & m) << sh)) : c.val;
    mem.write(dst + 1 + toAddr(k), intC(v));
    wrote;
  endrule

  function SReq mk(SKind kd, Cell s, Bit#(32) i, Bit#(32) e) =
    SReq { k: kd, s: s, i: i, e: e, s2: ?, p2: ?, op: ? };
  method Action info(Cell s) = reqQ.enq(mk(KInfo, s, ?, ?));
  method Action element(Cell s, Bit#(32) i) = reqQ.enq(mk(KElem, s, i, ?));
  method Action tryElement(Cell s, Bit#(32) i) = reqQ.enq(mk(KTry, s, i, ?));
  method Action newStr(Bit#(32) n, Bit#(32) bits) = reqQ.enq(mk(KNew, ?, n, bits));
  method Action setElement(Cell s, Bit#(32) i, Bit#(32) e) = reqQ.enq(mk(KSet, s, i, e));
  method Action changeSize(Cell s, Bit#(32) bits) = reqQ.enq(mk(KChg, s, bits, ?));
  method Action stringOp(Bit#(4) o, Cell s1, Bit#(32) p1, Bit#(32) n, Bit#(32) p2, Cell s2) =
    reqQ.enq(SReq { k: KOp, s: s1, i: p1, e: n, s2: s2, p2: p2, op: o });
  method Action hashStr(Cell s) = reqQ.enq(mk(KHash, s, ?, ?));
  method Action show(Cell s) = reqQ.enq(mk(KShow, s, ?, ?));
  method Action poke(Cell s, Bit#(32) i, Bit#(32) w) = reqQ.enq(mk(KPoke, s, i, w));
  method Action search(Cell s, Bit#(32) i, Bit#(32) e, Bit#(32) c) =
    reqQ.enq(SReq { k: KSrch, s: s, i: i, e: e, s2: ?, p2: c, op: ? });
  method Action equal(Cell s1, Cell s2) =
    reqQ.enq(SReq { k: KEq, s: s1, i: ?, e: ?, s2: s2, p2: ?, op: ? });
  method ActionValue#(SResult) result;
    resQ.deq;
    return resQ.first;
  endmethod
endmodule

endpackage
