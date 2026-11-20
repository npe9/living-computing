// PIM/m core: the goal box.  It owns the heap pointer and the ready
// queue and does everything that touches goal records and suspension
// records in memory (layouts: asm/pimm_layout.py, this project's
// design), one request at a time, one memory operation per cycle:
//
//   newVar      a fresh unbound cell; answers the reference to it
//   record      write a goal record from r0.. or from the argument
//               registers a1..; a READY one goes on the ready queue
//   hook        add a goal to the goals waiting on an unbound cell
//   wake        walk a suspension list; each goal still SUSPENDED
//               becomes READY and goes on the ready queue
//   pickup      take the newest ready goal: mark it TAKEN, load its
//               arguments into r0.., answer its code address; or
//               answer Invalid when the queue is empty
//
// The heap only grows; running out of memory stops the simulation.
package PimmGBox;

import FIFO::*;
import PimmGen::*;
import PimmTypes::*;
import PimmMem::*;
import PimmRegs::*;

interface PimmGBox;
  method Action newVar;
  method ActionValue#(Cell) newVarResult;
  method Action record(Bit#(2) status, Addr code, Bit#(8) argn, Bool fromArgv, Bool wantResult);
  method ActionValue#(Addr) recordResult;
  method Action hook(Addr g, Addr v);
  method Action wake(Bit#(32) s);
  method Action done;                           // a hook or a wake has finished
  method Action pickup;
  method ActionValue#(Maybe#(Addr)) picked;
endinterface

typedef union tagged {
  void NewVar;
  struct { Bit#(2) status; Addr code; Bit#(8) argn; Bool fromArgv; Bool want; } Record;
  struct { Addr g; Addr v; } Hook;
  Bit#(32) Wake;
  void Pickup;
} GReq deriving (Bits);

typedef enum { GIdle, GRec1, GRec2, GRec3, GRecArgs, GHook1, GHook2, GHook3,
               GWk0, GWk1, GWk2, GWk3, GWk4, GWk5,
               GPk1, GPk2, GPk3, GPk4, GPk5 } GState deriving (Bits, Eq);

module mkPimmGBox#(MemPort mem, PimmRegs regs)(PimmGBox);
  Reg#(Addr)   hp <- mkReg(fromInteger(heapStart));   // the next free cell
  Reg#(Addr)   rq <- mkReg(0);                        // the newest ready goal, or 0

  Reg#(GState)  st    <- mkReg(GIdle);
  Reg#(Addr)    g     <- mkRegU;
  Reg#(Bit#(8)) i     <- mkRegU;
  Reg#(Bit#(8)) n     <- mkRegU;
  Reg#(Bit#(2)) rStatus <- mkRegU;
  Reg#(Addr)    code  <- mkRegU;
  Reg#(Bool)    rFromArgv <- mkRegU;
  Reg#(Bool)    rWant <- mkRegU;
  Reg#(Addr)    var_  <- mkRegU;
  Reg#(Addr)    sAddr <- mkRegU;
  Reg#(Bit#(32)) s    <- mkRegU;

  FIFO#(GReq)          reqQ  <- mkFIFO;
  FIFO#(Cell)          varQ  <- mkFIFO;
  FIFO#(Addr)          recQ  <- mkFIFO;
  FIFO#(Bool)          doneQ <- mkFIFO;
  FIFO#(Maybe#(Addr))  pickQ <- mkFIFO;

  Addr gLink   = fromInteger(lay_G_LINK);
  Addr gStatus = fromInteger(lay_G_STATUS);
  Addr gCode   = fromInteger(lay_G_CODE);
  Addr gArgn   = fromInteger(lay_G_ARGN);
  Addr gArgs   = fromInteger(lay_G_ARGS);
  Addr sNext   = fromInteger(lay_S_NEXT);
  Addr sGoal   = fromInteger(lay_S_GOAL);
  Bit#(2) ready     = fromInteger(lay_READY);
  Bit#(2) suspended = fromInteger(lay_SUSPENDED);
  Bit#(2) taken     = fromInteger(lay_TAKEN);

  function Bit#(32) linkOf(Addr a) = (a == 0) ? 0 : absAddr(a);

  function Action alloc(Addr cells);
    action
      Bit#(TAdd#(AddrBits, 1)) next = zeroExtend(hp) + zeroExtend(cells);
      if (next[valueOf(AddrBits)] == 1) fatal("heap full");
      hp <= truncate(next);
    endaction
  endfunction

  function Action recordDone();
    action
      if (rStatus == ready) rq <= g;
      if (rWant) recQ.enq(g);
      st <= GIdle;
    endaction
  endfunction

  rule accept (st == GIdle);
    reqQ.deq;
    case (reqQ.first) matches
      tagged NewVar: begin
        alloc(1);
        mem.write(hp, mkCell(tag_UNDF, 0));
        varQ.enq(mkCell(tag_REFo, absAddr(hp)));
      end
      tagged Record .q: begin
        g <= hp;
        alloc(gArgs + zeroExtend(q.argn));
        rStatus <= q.status;
        code <= q.code;
        n <= q.argn;
        rFromArgv <= q.fromArgv;
        rWant <= q.want;
        mem.write(hp + gLink, intC(q.status == ready ? linkOf(rq) : 0));
        st <= GRec1;
      end
      tagged Hook .q: begin
        g <= q.g;
        var_ <= q.v;
        mem.read(q.v);
        st <= GHook1;
      end
      tagged Wake .w: begin
        s <= w;
        st <= GWk0;
      end
      tagged Pickup: begin
        if (rq == 0) pickQ.enq(tagged Invalid);
        else begin
          $display("G %0d", rq);
          g <= rq;
          mem.read(rq + gLink);
          st <= GPk1;
        end
      end
    endcase
  endrule

  // ---- record ------------------------------------------------------
  rule rec1 (st == GRec1);
    mem.write(g + gStatus, intC(zeroExtend(rStatus)));
    st <= GRec2;
  endrule

  rule rec2 (st == GRec2);
    mem.write(g + gCode, intC(absAddr(code)));
    st <= GRec3;
  endrule

  rule rec3 (st == GRec3);
    mem.write(g + gArgn, intC(zeroExtend(n)));
    i <= 0;
    if (n == 0) recordDone;
    else st <= GRecArgs;
  endrule

  rule recArgs (st == GRecArgs);
    mem.write(g + gArgs + zeroExtend(i), rFromArgv ? regs.a(i + 1) : regs.r(i));
    if (i + 1 == n) recordDone;
    else i <= i + 1;
  endrule

  // ---- hook --------------------------------------------------------
  rule hook1 (st == GHook1);
    let c <- mem.data;
    sAddr <= hp;
    alloc(fromInteger(lay_S_SIZE));
    mem.write(hp + sNext, intC(isHook(c) ? c.val : 0));
    st <= GHook2;
  endrule

  rule hook2 (st == GHook2);
    mem.write(sAddr + sGoal, intC(absAddr(g)));
    st <= GHook3;
  endrule

  rule hook3 (st == GHook3);
    mem.write(var_, mkCell(tag_HOOKo, absAddr(sAddr)));
    doneQ.enq(True);
    st <= GIdle;
  endrule

  // ---- wake --------------------------------------------------------
  rule wk0 (st == GWk0);
    if (s == 0) begin
      doneQ.enq(True);
      st <= GIdle;
    end
    else begin
      mem.read(truncate(s) + sGoal);
      st <= GWk1;
    end
  endrule

  rule wk1 (st == GWk1);
    let c <- mem.data;
    g <= truncate(c.val);
    mem.read(truncate(c.val) + gStatus);
    st <= GWk2;
  endrule

  rule wk2 (st == GWk2);
    let c <- mem.data;
    if (c.val == zeroExtend(suspended)) begin
      $display("W %0d", g);
      mem.write(g + gStatus, intC(zeroExtend(ready)));
      st <= GWk3;
    end
    else st <= GWk4;
  endrule

  rule wk3 (st == GWk3);
    mem.write(g + gLink, intC(linkOf(rq)));
    rq <= g;
    st <= GWk4;
  endrule

  rule wk4 (st == GWk4);
    mem.read(truncate(s) + sNext);
    st <= GWk5;
  endrule

  rule wk5 (st == GWk5);
    let c <- mem.data;
    s <= c.val;
    st <= GWk0;
  endrule

  // ---- pickup ------------------------------------------------------
  rule pk1 (st == GPk1);
    let c <- mem.data;
    rq <= truncate(c.val);
    mem.write(g + gStatus, intC(zeroExtend(taken)));
    st <= GPk2;
  endrule

  rule pk2 (st == GPk2);
    mem.read(g + gCode);
    st <= GPk3;
  endrule

  rule pk3 (st == GPk3);
    let c <- mem.data;
    code <= truncate(c.val);
    mem.read(g + gArgn);
    st <= GPk4;
  endrule

  rule pk4 (st == GPk4);
    let c <- mem.data;
    n <= truncate(c.val);
    i <= 0;
    if (c.val == 0) begin
      pickQ.enq(tagged Valid code);
      st <= GIdle;
    end
    else begin
      mem.read(g + gArgs);
      st <= GPk5;
    end
  endrule

  rule pk5 (st == GPk5);
    let c <- mem.data;
    regs.wr(i, c);
    if (i + 1 == n) begin
      pickQ.enq(tagged Valid code);
      st <= GIdle;
    end
    else begin
      i <= i + 1;
      mem.read(g + gArgs + zeroExtend(i) + 1);
    end
  endrule

  method Action newVar = reqQ.enq(tagged NewVar);
  method ActionValue#(Cell) newVarResult;
    varQ.deq;
    return varQ.first;
  endmethod
  method Action record(Bit#(2) status, Addr c, Bit#(8) argn, Bool fromArgv, Bool wantResult) =
    reqQ.enq(tagged Record { status: status, code: c, argn: argn,
                             fromArgv: fromArgv, want: wantResult });
  method ActionValue#(Addr) recordResult;
    recQ.deq;
    return recQ.first;
  endmethod
  method Action hook(Addr goal, Addr v) = reqQ.enq(tagged Hook { g: goal, v: v });
  method Action wake(Bit#(32) list) = reqQ.enq(tagged Wake list);
  method Action done = doneQ.deq;
  method Action pickup = reqQ.enq(tagged Pickup);
  method ActionValue#(Maybe#(Addr)) picked;
    pickQ.deq;
    return pickQ.first;
  endmethod
endmodule

endpackage
