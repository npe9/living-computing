// PIM/m core: the goal box.  It owns the heap pointer and the ready
// queue and does everything that touches goal records and suspension
// records in memory (layouts: asm/pimm_layout.py, this project's
// design), one request at a time, one memory operation per cycle:
//
//   newVar      a fresh unbound cell; answers the reference to it
//   record      write a goal record from r0.. or from the argument
//               registers a1..; a READY one goes on the ready queue
//   waitRecord  write the suspended goal of a body built-in that must
//               wait (asm/pimm_stubs.py): its code is the stub, its
//               arguments the instruction's operands; an output
//               operand gets a fresh variable, in the record and in
//               the register
//   unifyGoal   a READY goal of the stub unify_step with arguments
//               a, b, 0: the unification of two structures put off
//               (PimmDBox.bsv UGoal); answered through done
//   alloc       heap cells for another box
//   hook        add a goal to the goals waiting on an unbound cell
//   wake        walk a suspension list; each goal still SUSPENDED
//               becomes READY and goes on the ready queue, or, a goal
//               of the stub merge_in, at the end of the merger's list
//   pickup      the goals the merger's list gained since the last
//               pickup go to its front, in the order they were made
//               ready; take its first goal, or else the newest ready
//               goal: mark it TAKEN, load its arguments into r0..,
//               answer its code address; or answer Invalid when both
//               are empty
//
// The merger's list (2026-11-24, docs/pimm_semantics.md, merge): a
// woken goal of merge_in runs before any other goal, so a message
// bound to a merger input reaches the output before anything the
// binding reduction spawned runs, in the order of the unifications,
// and a merger's own output reaching another merger goes ahead of
// what was already waiting.  VPIM, KLIC and PDSS act AT the
// unification; acting at the next goal switch instead is OURS.
//
// The shoen (asm/pimm_layout.py, docs/pimm_semantics.md "Shoen": this
// project's design).  A goal record's status cell also says which
// shoen the goal belongs to: {INT, shoen << 2 | status}, the shoen as
// its record's address (an Addr is relative to the load address), 0
// the root, which has no record.  `shoen` is the current shoen: that
// of the goal last taken, 0 once the queue is empty (what a bench
// makes between runs is the root's).  A record written by record,
// waitRecord or unifyGoal belongs to the current shoen and, unless
// that is the root, adds one to its count (carried over from PDSS,
// record.h number_of_children), after its last cell.  The rest of the
// shoen is PimmShBox.bsv, which uses:
//
//   recordFor   the SUSPENDED first goal of a new shoen, from the
//               argument registers: it belongs to the shoen given and
//               is not counted (the new record's count starts at 1)
//   unpark      a goal parked that way becomes READY and goes on the
//               ready queue, as a woken goal does
//   applyGoal   (stage 3) a READY goal of apply's stub with arguments
//               a, b, of the current shoen and counted there, as
//               unifyGoal makes its goal: the goal that waits for an
//               exception's handler; answered through done
//   takenGoal   the record of the goal the last pickup took
//
// The heap only grows between collections (PimmGcBox.bsv); running out
// of memory stops the simulation.  R7G stage 5 (2026-11-25), the heap
// limit (ref/pimm/pimm_gc.py, "When memory runs out", INFERENCE/OURS):
// with a limit set (setLimit, RESTORE 5; 0 none), an allocation that
// takes hp - lo past the limit less heapInsurance (VPIM's
// _HEAP_END_INSURANCE_OFST) sets heapLow, which asks the collector for a
// collection at the next goal switch as collect_garbage does; once the
// heap has been collected (gcSet), one past the limit itself stops the
// simulation ("heap full: past the heap limit", VPIM's panic).
package PimmGBox;

import FIFO::*;
import Vector::*;
import PimmGen::*;
import PimmTypes::*;
import PimmMem::*;
import PimmRegs::*;

interface PimmGBox;
  method Action newVar;
  method ActionValue#(Cell) newVarResult;
  method Action record(Bit#(2) status, Addr code, Bit#(8) argn, Bool fromArgv, Bool wantResult);
  method Action waitRecord(Addr code, Bit#(3) argn, Vector#(7, Bit#(8)) operands, Bit#(7) outs);
  method ActionValue#(Addr) recordResult;       // of record (if asked) and waitRecord
  method Action unifyGoal(Cell a, Cell b);
  method Action alloc(Addr cells);
  method ActionValue#(Addr) allocResult;
  method Action hook(Addr g, Addr v);
  method Action wake(Bit#(32) s);
  method Action done;                           // a hook or a wake has finished
  method Action pickup;
  method ActionValue#(Maybe#(Addr)) picked;
  // the shoen
  method Addr shoen;                            // the current shoen's record, 0 = the root
  method Action recordFor(Addr sh, Addr code, Bit#(8) argn);   // answered by recordResult
  method Action unpark(Addr g);                // answered by done
  method Action applyGoal(Cell a, Cell b);     // answered by done
  method Addr takenGoal;
  // a checkpoint (ref/pimm/lockstep_shell.py): the heap pointer of the
  // machine saved, between runs, the queues empty
  method Action setHp(Addr a);
  // R7G stage 5: the heap limit in cells (RESTORE 5), and the request an
  // allocation past it less the insurance makes
  method Action setLimit(Addr a);
  method Addr limitOf;
  method Bool heapLow;
  // R7G, the garbage collector (PimmGcBox.bsv), at a goal switch: the
  // roots it moves, and what it gives back
  method Addr hpOf;
  method Addr rqOf;
  method Addr mqOf;
  method Addr mwHOf;
  method Addr mwTOf;
  method Action gcSet(Addr nrq, Addr nmq, Addr nmwH, Addr nmwT, Addr nhp, Addr ncur, Addr nlo);
endinterface

typedef union tagged {
  void NewVar;
  struct { Bit#(2) status; Addr code; Bit#(8) argn; Bool fromArgv; Bool want; } Record;
  struct { Addr code; Bit#(3) argn; Vector#(7, Bit#(8)) operands; Bit#(7) outs; } WaitRecord;
  struct { Cell a; Cell b; } UnifyGoal;
  struct { Cell a; Cell b; } ApplyGoal;
  Addr Alloc;
  struct { Addr g; Addr v; } Hook;
  Bit#(32) Wake;
  void Pickup;
  struct { Addr sh; Addr code; Bit#(8) argn; } RecordFor;
  Addr Release;
} GReq deriving (Bits);

typedef enum { GIdle, GRec1, GRec2, GRec3, GRecArgs, GUg1, GUg2, GUg3, GUg4, GUg5, GUg6, GWArg, GWArg2, GHook1, GHook2, GHook3,
               GWk0, GWk1, GWk2, GWk3, GWk3a, GWk3b, GWk4, GWk5,
               GPkS, GPk1, GPk2, GPk3, GPk4, GPk5,
               GPk0, GCnt0, GCnt, GUgCnt0, GUgCnt, GRl1, GRl2 } GState deriving (Bits, Eq);

module mkPimmGBox#(MemPort mem, PimmRegs regs)(PimmGBox);
  Reg#(Addr)   hp <- mkReg(fromInteger(heapStart));   // the next free cell
  Reg#(Addr)   rq <- mkReg(0);                        // the newest ready goal, or 0
  Reg#(Addr)   mq <- mkReg(0);                        // the merger's list: its first goal, or 0
  Reg#(Addr)   mwH <- mkReg(0);                       // goals of merge_in woken since the last
  Reg#(Addr)   mwT <- mkReg(0);                       // pickup: the first and the last, or 0
  Reg#(Bool)   fromMq <- mkReg(False);                // the goal picked is the merger list's
  // R7G stage 5: the heap limit (0 none), the heap's first live cell as
  // the last collection left it, whether there was one, the request
  Reg#(Addr)   limit <- mkReg(0);
  Reg#(Addr)   heapLo <- mkReg(fromInteger(heapStart));
  Reg#(Bool)   collected <- mkReg(False);
  Reg#(Bool)   low <- mkReg(False);

  Reg#(GState)  st    <- mkReg(GIdle);
  Reg#(Cell)    ugA   <- mkRegU;
  Reg#(Cell)    ugB   <- mkRegU;
  Reg#(Addr)    g     <- mkRegU;
  Reg#(Bit#(8)) i     <- mkRegU;
  Reg#(Bit#(8)) n     <- mkRegU;
  Reg#(Bit#(2)) rStatus <- mkRegU;
  Reg#(Addr)    code  <- mkRegU;
  Reg#(Bool)    rFromArgv <- mkRegU;
  Reg#(Bool)    rWant <- mkRegU;
  Reg#(Bool)    rBuiltin <- mkRegU;   // a waitRecord: arguments are operands
  Reg#(Vector#(7, Bit#(8))) rOps <- mkRegU;
  Reg#(Bit#(7)) rOuts <- mkRegU;
  Reg#(Addr)    vAddr <- mkRegU;
  FIFO#(Addr)   allocQ <- mkFIFO;
  Reg#(Addr)    var_  <- mkRegU;
  Reg#(Addr)    sAddr <- mkRegU;
  Reg#(Bit#(32)) s    <- mkRegU;
  Reg#(Addr)    cur   <- mkReg(0);    // the current shoen's record, 0 = the root
  Reg#(Addr)    rSh   <- mkRegU;      // the shoen of the record being written
  Reg#(Bool)    rCount <- mkRegU;     // ... and whether the record is counted there
  Reg#(Bool)    ugApply <- mkReg(False);   // the goal of unifyGoal is applyGoal's

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
  // a status cell: the goal's shoen above the two status bits
  function Cell statusCell(Addr sh, Bit#(2) status);
    Bit#(32) sh32 = zeroExtend(sh);
    return intC((sh32 << 2) | zeroExtend(status));
  endfunction
  Addr shCount = fromInteger(lay_SH_COUNT);

  function Action take(Addr cells);
    action
      Bit#(TAdd#(AddrBits, 1)) next = zeroExtend(hp) + zeroExtend(cells);
      if (next[valueOf(AddrBits)] == 1) fatal("heap full");
      hp <= truncate(next);
      if (limit != 0) begin
        Bit#(TAdd#(AddrBits, 1)) used = next - zeroExtend(heapLo);
        Bit#(TAdd#(AddrBits, 1)) lim = zeroExtend(limit);
        Bit#(TAdd#(AddrBits, 1)) ins = fromInteger(heapInsurance);
        if (collected && used > lim) fatal("heap full: past the heap limit");
        if (used > (lim > ins ? lim - ins : 0)) low <= True;
      end
    endaction
  endfunction

  function Action recordEnd();
    action
      if (rStatus == ready) rq <= g;
      if (rWant) recQ.enq(g);
      st <= GIdle;
    endaction
  endfunction

  // the record's last cell is written: it is counted on its shoen
  function Action recordDone();
    action
      if (rCount) st <= GCnt0;
      else recordEnd;
    endaction
  endfunction

  rule count (st == GCnt0);
    mem.read(rSh + shCount);
    st <= GCnt;
  endrule

  rule counted (st == GCnt);
    let c <- mem.data;
    mem.write(rSh + shCount, intC(c.val + 1));
    recordEnd;
  endrule

  rule accept (st == GIdle);
    reqQ.deq;
    case (reqQ.first) matches
      tagged NewVar: begin
        take(1);
        mem.write(hp, mkCell(tag_UNDF, 0));
        varQ.enq(mkCell(tag_REFo, absAddr(hp)));
      end
      tagged Record .q: begin
        g <= hp;
        take(gArgs + zeroExtend(q.argn));
        rStatus <= q.status;
        code <= q.code;
        n <= q.argn;
        rFromArgv <= q.fromArgv;
        rWant <= q.want;
        rBuiltin <= False;
        rSh <= cur;
        rCount <= cur != 0;
        mem.write(hp + gLink, intC(q.status == ready ? linkOf(rq) : 0));
        st <= GRec1;
      end
      tagged WaitRecord .q: begin
        g <= hp;
        take(gArgs + zeroExtend(q.argn));
        rStatus <= suspended;
        code <= q.code;
        n <= zeroExtend(q.argn);
        rWant <= True;
        rBuiltin <= True;
        rSh <= cur;
        rCount <= cur != 0;
        rOps <= q.operands;
        rOuts <= q.outs;
        mem.write(hp + gLink, intC(0));
        st <= GRec1;
      end
      tagged UnifyGoal .q: begin
        g <= hp;
        take(gArgs + 3);
        ugA <= q.a;
        ugB <= q.b;
        ugApply <= False;
        mem.write(hp + gLink, intC(linkOf(rq)));
        st <= GUg1;
      end
      tagged ApplyGoal .q: begin
        g <= hp;
        take(gArgs + 2);
        ugA <= q.a;
        ugB <= q.b;
        ugApply <= True;
        mem.write(hp + gLink, intC(linkOf(rq)));
        st <= GUg1;
      end
      tagged Alloc .cells: begin
        take(cells);
        allocQ.enq(hp);
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
        if (mwH != 0) begin
          // the goals woken since the last pickup go to the list's front
          mem.write(mwT + gLink, intC(linkOf(mq)));
          mq <= mwH;
          mwH <= 0;
          mwT <= 0;
        end
        st <= GPkS;
      end
      tagged RecordFor .q: begin
        g <= hp;
        take(gArgs + zeroExtend(q.argn));
        rStatus <= suspended;
        code <= q.code;
        n <= q.argn;
        rFromArgv <= True;
        rWant <= True;
        rBuiltin <= False;
        rSh <= q.sh;
        rCount <= False;
        mem.write(hp + gLink, intC(0));
        st <= GRec1;
      end
      tagged Release .q: begin
        g <= q;
        mem.read(q + gStatus);
        st <= GRl1;
      end
    endcase
  endrule

  // ---- the goal of a unification put off ---------------------------
  rule ug1 (st == GUg1);
    mem.write(g + gStatus, statusCell(cur, ready));
    st <= GUg2;
  endrule
  rule ug2 (st == GUg2);
    mem.write(g + gCode, intC(absAddr(ugApply ? applyStub : unifyStepStub)));
    st <= GUg3;
  endrule
  rule ug3 (st == GUg3);
    mem.write(g + gArgn, intC(ugApply ? 2 : 3));
    st <= GUg4;
  endrule
  rule ug4 (st == GUg4);
    mem.write(g + gArgs, ugA);
    st <= GUg5;
  endrule
  function Action ugEnd();
    action
      rq <= g;
      if (cur != 0) st <= GUgCnt0;
      else begin
        doneQ.enq(True);
        st <= GIdle;
      end
    endaction
  endfunction
  rule ug5 (st == GUg5);
    mem.write(g + gArgs + 1, ugB);
    if (ugApply) ugEnd;          // apply's goal has two arguments
    else st <= GUg6;
  endrule
  rule ug6 (st == GUg6);
    mem.write(g + gArgs + 2, intC(0));
    ugEnd;
  endrule

  rule ugCount (st == GUgCnt0);
    mem.read(cur + shCount);
    st <= GUgCnt;
  endrule

  rule ugCounted (st == GUgCnt);
    let c <- mem.data;
    mem.write(cur + shCount, intC(c.val + 1));
    doneQ.enq(True);
    st <= GIdle;
  endrule

  // ---- record ------------------------------------------------------
  rule rec1 (st == GRec1);
    mem.write(g + gStatus, statusCell(rSh, rStatus));
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
    else st <= rBuiltin ? GWArg : GRecArgs;
  endrule

  rule recArgs (st == GRecArgs);
    mem.write(g + gArgs + zeroExtend(i), rFromArgv ? regs.a(i + 1) : regs.r(i));
    if (i + 1 == n) recordDone;
    else i <= i + 1;
  endrule

  // a waiting built-in's arguments: an input operand's register, or a
  // fresh variable for an output operand (which the register also gets)
  function Action nextWArg();
    action
      if (i + 1 == n) recordDone;
      else begin
        i <= i + 1;
        st <= GWArg;
      end
    endaction
  endfunction

  rule wArg (st == GWArg);
    Bit#(3) k = truncate(i);
    if (rOuts[k] == 1) begin
      vAddr <= hp;
      take(1);
      mem.write(hp, mkCell(tag_UNDF, 0));
      st <= GWArg2;
    end
    else begin
      mem.write(g + gArgs + zeroExtend(i), regs.r(rOps[k]));
      nextWArg;
    end
  endrule

  rule wArg2 (st == GWArg2);
    Bit#(3) k = truncate(i);
    Cell v = mkCell(tag_REFo, absAddr(vAddr));
    mem.write(g + gArgs + zeroExtend(i), v);
    regs.wr(rOps[k], v);
    nextWArg;
  endrule

  // ---- hook --------------------------------------------------------
  rule hook1 (st == GHook1);
    let c <- mem.data;
    sAddr <= hp;
    take(fromInteger(lay_S_SIZE));
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
    if (c.val[1:0] == suspended) begin       // the goal's shoen stays
      $display("W %0d", g);
      mem.write(g + gStatus, intC({c.val[31:2], ready}));
      st <= GWk3;
    end
    else st <= GWk4;
  endrule

  rule wk3 (st == GWk3);
    mem.read(g + gCode);
    st <= GWk3a;
  endrule

  // a goal of merge_in goes at the end of the merger's list, any other
  // on the ready queue
  rule wk3a (st == GWk3a);
    let c <- mem.data;
    if (c.val == absAddr(mergeInStub)) begin
      mem.write(g + gLink, intC(0));
      if (mwH == 0) begin
        mwH <= g;
        mwT <= g;
        st <= GWk4;
      end
      else st <= GWk3b;
    end
    else begin
      mem.write(g + gLink, intC(linkOf(rq)));
      rq <= g;
      st <= GWk4;
    end
  endrule

  rule wk3b (st == GWk3b);
    mem.write(mwT + gLink, intC(absAddr(g)));
    mwT <= g;
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
  rule pkS (st == GPkS);
    if (mq != 0) begin
      $display("G %0d", mq);
      g <= mq;
      fromMq <= True;
      mem.read(mq + gStatus);
      st <= GPk0;
    end
    else if (rq != 0) begin
      $display("G %0d", rq);
      g <= rq;
      fromMq <= False;
      mem.read(rq + gStatus);
      st <= GPk0;
    end
    else begin
      cur <= 0;
      pickQ.enq(tagged Invalid);
      st <= GIdle;
    end
  endrule

  // the goal's shoen is the current shoen from here on
  rule pk0 (st == GPk0);
    let c <- mem.data;
    cur <= truncate(c.val >> 2);
    mem.read(g + gLink);
    st <= GPk1;
  endrule

  rule pk1 (st == GPk1);
    let c <- mem.data;
    if (fromMq) mq <= truncate(c.val);
    else rq <= truncate(c.val);
    mem.write(g + gStatus, statusCell(cur, taken));
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

  // ---- release: a parked goal goes on the ready queue ---------------
  rule rl1 (st == GRl1);
    let c <- mem.data;
    $display("W %0d", g);
    mem.write(g + gStatus, intC({c.val[31:2], ready}));
    st <= GRl2;
  endrule

  rule rl2 (st == GRl2);
    mem.write(g + gLink, intC(linkOf(rq)));
    rq <= g;
    doneQ.enq(True);
    st <= GIdle;
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
  method Action waitRecord(Addr c, Bit#(3) argn, Vector#(7, Bit#(8)) operands, Bit#(7) outs) =
    reqQ.enq(tagged WaitRecord { code: c, argn: argn, operands: operands, outs: outs });
  method Action unifyGoal(Cell a, Cell b) = reqQ.enq(tagged UnifyGoal { a: a, b: b });
  method Action applyGoal(Cell a, Cell b) = reqQ.enq(tagged ApplyGoal { a: a, b: b });
  method Addr takenGoal = g;
  method Action alloc(Addr cells) = reqQ.enq(tagged Alloc cells);
  method ActionValue#(Addr) allocResult;
    allocQ.deq;
    return allocQ.first;
  endmethod
  method Action hook(Addr goal, Addr v) = reqQ.enq(tagged Hook { g: goal, v: v });
  method Action wake(Bit#(32) list) = reqQ.enq(tagged Wake list);
  method Action done = doneQ.deq;
  method Action pickup = reqQ.enq(tagged Pickup);
  method ActionValue#(Maybe#(Addr)) picked;
    pickQ.deq;
    return pickQ.first;
  endmethod
  method Addr shoen = cur;
  method Action recordFor(Addr sh, Addr c, Bit#(8) argn) =
    reqQ.enq(tagged RecordFor { sh: sh, code: c, argn: argn });
  method Action unpark(Addr goal) = reqQ.enq(tagged Release goal);
  method Action setHp(Addr a) if (st == GIdle);
    hp <= a;
  endmethod
  method Addr hpOf = hp;
  method Addr rqOf = rq;
  method Addr mqOf = mq;
  method Addr mwHOf = mwH;
  method Addr mwTOf = mwT;
  method Action setLimit(Addr a) if (st == GIdle);
    limit <= a;
  endmethod
  method Addr limitOf = limit;
  method Bool heapLow = low;
  method Action gcSet(Addr nrq, Addr nmq, Addr nmwH, Addr nmwT, Addr nhp, Addr ncur, Addr nlo) if (st == GIdle);
    heapLo <= nlo;
    collected <= True;
    low <= False;
    rq <= nrq;
    mq <= nmq;
    mwH <= nmwH;
    mwT <= nmwT;
    hp <= nhp;
    cur <= ncur;
  endmethod
endmodule

endpackage
