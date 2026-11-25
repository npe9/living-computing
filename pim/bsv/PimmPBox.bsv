// PIM/m core: the passive-unification box, the guard X = Y (wait_value)
// when either side is a list or a vector (2026-11-25).
//
// The meaning is VPIM's (functions/f_reduce_passive_unify.psl.c
// f_EqualStruct 41-109 and f_Equal_Sub 166-312, structures/
// str_passive_unify.psl.c the unify stack), as ref/pimm/pimm.py
// passive() has it, step for step:
//
//   start(a, b)    two words, dereferenced and bound (the exec stage has
//                  dealt with an unbound one), at least one a list or a
//                  vector.  They are the first pair.
//   a pair         an unbound X is Wait (at X's variable), then an
//                  unbound Y; a module or a code against anything is
//                  equal only to the same tag and value; types that
//                  differ are NotEqual; integers and atoms by value;
//                  strings by descriptor and words; the null vector is
//                  equal; a long vector after its size (NotEqual if the
//                  sizes differ), a list (2 elements, car and cdr) or a
//                  short vector: the frame in hand is pushed, even one
//                  at its end, and the structure's elements are the
//                  pairs that follow.  Anything else (a float, ...):
//                  Refused.
//   the next pair  element crp of the frame in hand, X's then Y's, each
//                  read and taken (a reference to the cell if it is an
//                  unbound variable) and dereferenced through the data
//                  box; at the frame's end the stack is popped until a
//                  frame with elements left; the stack empty: Equal.
//   the stack      512 frames of (crp, size, X's first element, Y's
//                  first element): VPIM's bound (_LOCAL_MEM_UNIFY_STACK_
//                  AREA_SIZE 0x800 words, basics/bsc_mem_map.psl.c:90, 4
//                  words a frame), not PIM/m's, which is not held.  A
//                  513th push is Refused (VPIM suspends there with a
//                  DEBUG warning and no variable to wake the goal).
//
// The box has its own memory port (reads only: nothing is traced) and
// uses the data box for each element's dereference; the exec stage
// waits on result.  VPIM's dereference writes the result back into the
// structure (f_DerefElementReg): not done here, as not in the reference.
package PimmPBox;

import FIFO::*;
import RegFile::*;
import PimmGen::*;
import PimmTypes::*;
import PimmMem::*;
import PimmDBox::*;

typedef enum { PEqual, PNotEqual, PWait, PRefused } PKind deriving (Bits, Eq, FShow);
typedef struct { PKind k; Cell v; } PResult deriving (Bits);

interface PimmPBox;
  method Action start(Cell a, Cell b);
  method ActionValue#(PResult) result;
endinterface

typedef struct { Bit#(32) crp; Bit#(32) size; Addr xa; Addr ya; } PFrame deriving (Bits);

typedef enum { PIdle, PPair, PRdX, PDx, PRdY, PDy, PPop,
               PLx, PLy, PLxb, PLyb, PS1, PS2, PS3, PS4 } PState deriving (Bits, Eq);

module mkPimmPBox#(MemPort mem, PimmDBox dbox)(PimmPBox);
  RegFile#(Bit#(9), PFrame) stack <- mkRegFileFull;
  Reg#(Bit#(10)) sp    <- mkReg(0);       // frames on the stack
  Reg#(Bool)     have  <- mkReg(False);   // a frame in hand (not at the top pair)
  Reg#(Bit#(32)) crp   <- mkRegU;         // its next element
  Reg#(Bit#(32)) size  <- mkRegU;
  Reg#(Addr)     xa    <- mkRegU;         // X's first element
  Reg#(Addr)     ya    <- mkRegU;         // Y's
  Reg#(Cell)     x     <- mkRegU;         // the pair in hand
  Reg#(Cell)     y     <- mkRegU;
  Reg#(Addr)     lx    <- mkRegU;         // two long vectors: X's first element
  Reg#(Bit#(32)) ln    <- mkRegU;         // ... and the size
  Reg#(Cell)     sdesc <- mkRegU;         // two strings: X's descriptor
  Reg#(Bit#(32)) sk    <- mkRegU;         // ... the word in hand
  Reg#(Bit#(32)) sw    <- mkRegU;         // ... X's word
  Reg#(PState)   st    <- mkReg(PIdle);
  FIFO#(PResult) resQ  <- mkFIFO;

  function Cell taken(Cell c, Addr a) = isUnboundCell(c) ? mkCell(tag_REFx, absAddr(a)) : marked(c);
  function Bit#(8) ty(Cell c) = c.tag & 8'hfe;

  function Action answer(PKind k, Cell v);
    action
      resQ.enq(PResult { k: k, v: v });
      st <= PIdle;
    endaction
  endfunction

  // the pair was equal and is not a structure: the next one
  function Action advance();
    action
      if (have && crp < size) begin
        mem.read(xa + truncate(crp));
        st <= PRdX;
      end
      else st <= PPop;
    endaction
  endfunction

  // a structure: its elements are the next pairs
  function Action expand(Addr x0, Addr y0, Bit#(32) n);
    action
      if (have && sp == 512) answer(PRefused, ?);
      else begin
        if (have) begin
          stack.upd(truncate(sp), PFrame { crp: crp, size: size, xa: xa, ya: ya });
          sp <= sp + 1;
        end
        have <= True;
        crp <= 0;
        size <= n;
        xa <= x0;
        ya <= y0;
        mem.read(x0);
        st <= PRdX;
      end
    endaction
  endfunction

  rule pair (st == PPair);
    if (isRef(x)) answer(PWait, x);
    else if (isRef(y)) answer(PWait, y);
    else if (x.tag == tag_MOD || x.tag == tag_COD || y.tag == tag_MOD || y.tag == tag_COD) begin
      if (x == y) advance;
      else answer(PNotEqual, ?);
    end
    else if (ty(x) != ty(y)) answer(PNotEqual, ?);
    else if (isInt(x) || isAtom(x)) begin
      if (x.val == y.val) advance;
      else answer(PNotEqual, ?);
    end
    else if (isStrg(x)) begin
      mem.read(cellAddr(x));
      st <= PS1;
    end
    else if (ty(x) == tag_VECT0o) advance;          // the null vector
    else if (ty(x) == tag_VECTo) begin                // two long vectors
      mem.read(cellAddr(x) + 1);
      st <= PLx;
    end
    else if (ty(x) == tag_LISTo) expand(cellAddr(x), cellAddr(y), 2);
    else if ((x.tag & 8'hf0) == tag_VECT0o)
      expand(cellAddr(x), cellAddr(y), zeroExtend((x.tag - tag_VECT0o) >> 1));
    else answer(PRefused, ?);
  endrule

  rule rdX (st == PRdX);
    let c <- mem.data;
    dbox.deref(taken(c, xa + truncate(crp)));
    st <= PDx;
  endrule

  rule dX (st == PDx);
    let v <- dbox.derefResult;
    x <= v;
    mem.read(ya + truncate(crp));
    st <= PRdY;
  endrule

  rule rdY (st == PRdY);
    let c <- mem.data;
    dbox.deref(taken(c, ya + truncate(crp)));
    st <= PDy;
  endrule

  rule dY (st == PDy);
    let v <- dbox.derefResult;
    y <= v;
    crp <= crp + 1;
    st <= PPair;
  endrule

  rule pop (st == PPop);
    if (sp == 0) answer(PEqual, ?);
    else begin
      let f = stack.sub(truncate(sp - 1));
      sp <= sp - 1;
      if (f.crp < f.size) begin
        crp <= f.crp;
        size <= f.size;
        xa <= f.xa;
        ya <= f.ya;
        mem.read(f.xa + truncate(f.crp));
        st <= PRdX;
      end
    end
  endrule

  // two long vectors: {VDESC, the first element}, the size
  rule longX (st == PLx);
    let c <- mem.data;
    ln <= c.val;
    mem.read(cellAddr(y) + 1);
    st <= PLy;
  endrule

  rule longY (st == PLy);
    let c <- mem.data;
    if (c.val != ln) answer(PNotEqual, ?);
    else begin
      mem.read(cellAddr(x));
      st <= PLxb;
    end
  endrule

  rule longXb (st == PLxb);
    let c <- mem.data;
    lx <= cellAddr(c);
    mem.read(cellAddr(y));
    st <= PLyb;
  endrule

  rule longYb (st == PLyb);
    let c <- mem.data;
    expand(lx, cellAddr(c), ln);
  endrule

  // two strings: the descriptors, then every word
  rule str1 (st == PS1);
    let c <- mem.data;
    sdesc <= c;
    mem.read(cellAddr(y));
    st <= PS2;
  endrule

  rule str2 (st == PS2);
    let d <- mem.data;
    Bit#(32) words = zeroExtend(sdesc.val[23:0]);
    if (d != sdesc) answer(PNotEqual, ?);
    else if (words == 0) advance;
    else begin
      sk <= 1;
      mem.read(cellAddr(x) + 1);
      st <= PS3;
    end
  endrule

  rule str3 (st == PS3);
    let c <- mem.data;
    sw <= c.val;
    mem.read(cellAddr(y) + truncate(sk));
    st <= PS4;
  endrule

  rule str4 (st == PS4);
    let d <- mem.data;
    Bit#(32) words = zeroExtend(sdesc.val[23:0]);
    if (d.val != sw) answer(PNotEqual, ?);
    else if (sk == words) advance;
    else begin
      sk <= sk + 1;
      mem.read(cellAddr(x) + truncate(sk + 1));
      st <= PS3;
    end
  endrule

  method Action start(Cell a, Cell b) if (st == PIdle);
    x <= a;
    y <= b;
    have <= False;
    sp <= 0;
    st <= PPair;
  endmethod

  method ActionValue#(PResult) result;
    resQ.deq;
    return resQ.first;
  endmethod
endmodule

endpackage
