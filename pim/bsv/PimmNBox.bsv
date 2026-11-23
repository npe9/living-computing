// PIM/m core: the merger box.  merge(In, ^Out) "creates a built-in
// constant time merger" (PIMOS manual).  On the machine a merger input
// is a cell of its own tag (MGHOK) pointing at a merger record
// {output variable}{number of inputs} (TR-466 3.3), and the merger
// acts when that cell is unified.  HERE a merger input is a goal
// waiting on the input stream (the exec stage makes it; its code is
// the stub merge_in, asm/pimm_stubs.py, not a PIM/m instruction), and
// this box does the memory work of its three steps:
//
//   create(out)       three cells: {out}{INT 1}{UNDF}: the record
//                     (output, count) and the first input variable.
//                     a = a reference to the variable, b = {INT,
//                     the record's address}
//   cons(list, rec)   an element arrives: a new list cell {the car}
//                     {UNDF}; the record's output becomes that new
//                     variable.  a = the new list, b = the old output
//                     (the exec stage unifies the two), c = the cdr,
//                     the stream to go on with
//   close(rec)        an input ends: the count goes down.  a = the
//                     output, ok = the count reached 0 (the exec stage
//                     then unifies the output with [])
//
// A car or cdr cell that is an unbound variable is taken as a
// reference to it.
package PimmNBox;

import FIFO::*;
import PimmGen::*;
import PimmTypes::*;
import PimmMem::*;
import PimmGBox::*;

typedef struct { Cell a; Cell b; Cell c; Bool ok; } NResult deriving (Bits);

interface PimmNBox;
  method Action create(Cell out);
  method Action cons(Cell list, Cell rec);
  method Action close(Cell rec);
  method ActionValue#(NResult) result;
endinterface

typedef enum { NKCreate, NKCons, NKClose } NKind deriving (Bits, Eq);
typedef struct { NKind k; Cell v; Cell rec; } NReq deriving (Bits);
typedef enum { NIdle, NCr1, NCr2, NCr3, NCo1, NCo2, NCo3, NCo4, NCo5, NCo5b, NCo6, NCl1, NCl1b, NCl2 }
  NState deriving (Bits, Eq);

module mkPimmNBox#(MemPort mem, PimmGBox gbox)(PimmNBox);
  Reg#(NState)   st   <- mkReg(NIdle);
  Reg#(NReq)     rq   <- mkRegU;
  Reg#(Addr)     obj  <- mkRegU;     // the cells taken
  Reg#(Cell)     out  <- mkRegU;     // the record's output
  Reg#(Bit#(32)) cnt  <- mkRegU;
  FIFO#(NReq)    reqQ <- mkFIFO;
  FIFO#(NResult) resQ <- mkFIFO;

  Addr rec  = cellAddr(rq.rec);
  Addr list = cellAddr(rq.v);
  function Cell taken(Cell c, Addr a) = isUnboundCell(c) ? mkCell(tag_REFo, absAddr(a)) : c;

  function Action answer(Cell a, Cell b, Cell c, Bool ok);
    action
      resQ.enq(NResult { a: a, b: b, c: c, ok: ok });
      st <= NIdle;
    endaction
  endfunction

  rule accept (st == NIdle);
    let q = reqQ.first;
    reqQ.deq;
    rq <= q;
    case (q.k)
      NKCreate: begin
        gbox.alloc(3);
        st <= NCr1;
      end
      NKCons: begin
        mem.read(cellAddr(q.rec));
        st <= NCo1;
      end
      NKClose: begin
        mem.read(cellAddr(q.rec) + 1);
        st <= NCl1;
      end
    endcase
  endrule

  // ---- create
  rule create1 (st == NCr1);
    let a <- gbox.allocResult;
    obj <= a;
    mem.write(a, rq.v);
    st <= NCr2;
  endrule

  rule create2 (st == NCr2);
    mem.write(obj + 1, intC(1));
    st <= NCr3;
  endrule

  rule create3 (st == NCr3);
    mem.write(obj + 2, mkCell(tag_UNDF, 0));
    answer(mkCell(tag_REFo, absAddr(obj + 2)), intC(absAddr(obj)), ?, True);
  endrule

  // ---- an element
  rule cons1 (st == NCo1);
    let c <- mem.data;
    out <= c;
    gbox.alloc(2);
    st <= NCo2;
  endrule

  rule cons2 (st == NCo2);
    let a <- gbox.allocResult;
    obj <= a;
    mem.read(list);
    st <= NCo3;
  endrule

  rule cons3 (st == NCo3);
    let c <- mem.data;
    mem.write(obj, taken(c, list));
    st <= NCo4;
  endrule

  rule cons4 (st == NCo4);
    mem.write(obj + 1, mkCell(tag_UNDF, 0));
    st <= NCo5;
  endrule

  rule cons5 (st == NCo5);
    mem.write(rec, mkCell(tag_REFo, absAddr(obj + 1)));
    st <= NCo5b;
  endrule

  rule cons5b (st == NCo5b);
    mem.read(list + 1);
    st <= NCo6;
  endrule

  rule cons6 (st == NCo6);
    let c <- mem.data;
    answer(mkCell(tag_LISTo + 1, absAddr(obj)), out, taken(c, list + 1), True);
  endrule

  // ---- an input ends
  rule close1 (st == NCl1);
    let c <- mem.data;
    cnt <= c.val - 1;
    mem.write(rec + 1, intC(c.val - 1));
    st <= NCl1b;
  endrule

  rule close1b (st == NCl1b);
    mem.read(rec);
    st <= NCl2;
  endrule

  rule close2 (st == NCl2);
    let c <- mem.data;
    answer(c, ?, ?, cnt == 0);
  endrule

  method Action create(Cell o) = reqQ.enq(NReq { k: NKCreate, v: o, rec: ? });
  method Action cons(Cell l, Cell r) = reqQ.enq(NReq { k: NKCons, v: l, rec: r });
  method Action close(Cell r) = reqQ.enq(NReq { k: NKClose, v: ?, rec: r });
  method ActionValue#(NResult) result;
    resQ.deq;
    return resQ.first;
  endmethod
endmodule

endpackage
