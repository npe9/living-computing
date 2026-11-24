// PIM/m core: the shoen box.  Stages 1 and 2 of the shoen:
// create_shoen, start_shoen, termination, shoen_statistics and
// remove_shoen, nothing more (no stop, abort, resource, profile or
// exception: the exec stage refuses those built-ins).
//
// What is PIM/m-sourced here: the handle's tag (38h SHREC, PIMOS
// debugger/inspector/tagtbl.kl1) and the report stream's codes (8
// started, 12 terminated: the image's shoen:report/2, cell 15818, and
// PIMOS macro/pimos/pimos/pimos.vmac:177-199).  The shoen record
// (asm/pimm_layout.py) is this project's design.  The count of live
// goals and child shoen, the parked first goal and when a message is
// reported are carried over from PDSS (emulator/shoen.c, emulate.c)
// and VPIM (functions/f_shoen_control.psl.c, f_shoen_with_fp.psl.c),
// the siblings: not PIM/m-sourced (docs/pimm_semantics.md "Shoen").
//
//   create        a shoen record: count 1, DORMANT, its parent the
//                 current shoen; a fresh Report variable; the first
//                 goal, a goal of apply's stub on the argument
//                 registers a1 (Code), a2 (Argv), which the exec stage
//                 has loaded: it belongs to the new shoen and is
//                 parked (SUSPENDED, on no queue, on no variable);
//                 then one more on the parent's count, unless that is
//                 the root (PDSS shoen.c:123-178: "prec->
//                 number_of_children = 1; ... prec->parent = parent;
//                 number_of_children++", the goal "(OBJ *)dc_apply").
//                 a = the reference to Report, b = the handle
//   start(h)      a DORMANT shoen: 8 is reported first, then it is
//                 STARTED (VPIM f_shoen_control.psl.c:324-330 reports
//                 before the state changes), then the goal box
//                 releases the parked goal.  ok = it was dormant
//   endReduction  the reduction of a goal has ended (proceed or
//                 suspend): one less on the current shoen's count.
//                 At 0 it is TERMINATED, 12 is reported, and its
//                 parent loses one in turn (PDSS emulate.c:340
//                 "if(--number_of_children == 0){ terminate_shoen();
//                 }", shoen.c:280-309).  The root: nothing, and no
//                 memory traffic.  Answered by ended.  Stage 2: the
//                 run's reductions n (the exec stage's count: each
//                 execute, and the proceed) are first added to the
//                 shoen's reduction cell, and a terminated shoen's
//                 total to its parent's (PDSS shoen.c:293); a shoen
//                 whose remove came first is removed at termination
//   statistics(h) 10 (statistics_started), then {9, H, L}, H:L twice
//                 the reduction cell (PIMOS manual e-shoen.tex:234:
//                 "twice of the number of reductions"; 10 then 9 at
//                 once is VPIM's, f_shoen_control.psl.c:691-727)
//   remove(h)     a terminated shoen: {14, 0, 0} (return_resource: no
//                 resource here, OURS), the report stream closed (its
//                 tail unified with []), the status REMOVED; one not
//                 terminated: its remove cell set, removed when it
//                 terminates (VPIM f_shoen_control.psl.c:547-575,
//                 f_shoen_with_fp.psl.c:69-71); one removed already:
//                 ok = False
//
// Reporting a message: two new cells {INT, code}{UNDF}; the stream's
// tail (the record's reference, followed through references by the
// data box) is unified with the list cell, the goal box waking the
// goals that waited on it; the record's tail is then the new cell.  A
// tail that someone has bound to a value stops the simulation.
// resource_low (6) is never reported: there is no resource model.
package PimmShBox;

import FIFO::*;
import PimmGen::*;
import PimmTypes::*;
import PimmMem::*;
import PimmDBox::*;
import PimmGBox::*;

typedef struct { Cell a; Cell b; Bool ok; } ShResult deriving (Bits);

interface PimmShBox;
  method Action create;
  method Action start(Cell handle);
  method ActionValue#(ShResult) result;
  method Action endReduction(Bit#(32) n);
  method Action ended;
  method Action statistics(Cell handle);
  method Action remove(Cell handle);
endinterface

typedef union tagged {
  void Create;
  Cell Start;
  Bit#(32) EndReduction;
  Cell Stats;
  Cell Remove;
} ShReq deriving (Bits);

typedef enum { ShIdle, ShC1, ShC2, ShC3, ShC4, ShC5, ShC6, ShC7,
               ShS1, ShS2, ShS3, ShS4, ShS5,
               ShE1, ShE2, ShE3, ShE4,
               ShR1, ShR2, ShR3, ShR4, ShR5, ShR6, ShR7, ShR8,
               ShC8, ShC9, ShE0, ShE0b, ShT1, ShT2, ShQ1, ShQ2, ShQ3, ShM1, ShM2,
               ShV1, ShV2, ShV3, ShV4, ShK1, ShK2, ShK3, ShK4, ShK5 } ShState deriving (Bits, Eq);

module mkPimmShBox#(MemPort mem, PimmGBox gbox, PimmDBox dbox)(PimmShBox);
  Reg#(ShState)  st     <- mkReg(ShIdle);
  Reg#(Addr)     sh     <- mkRegU;     // the shoen record in hand
  Reg#(Addr)     parent <- mkRegU;
  Reg#(Cell)     var_   <- mkRegU;     // create: the Report variable
  Reg#(Cell)     code   <- mkRegU;     // the message being reported
  Reg#(ShState)  after  <- mkRegU;     // ... and where to go on from
  Reg#(Addr)     lcell  <- mkRegU;     // ... and its list cell
  Reg#(Bit#(32)) red    <- mkRegU;     // reductions being added, or reported
  Reg#(Bit#(32)) vcode  <- mkRegU;     // a message {vcode, vhi, vlo}
  Reg#(Bit#(32)) vhi    <- mkRegU;
  Reg#(Bit#(32)) vlo    <- mkRegU;
  Reg#(ShState)  vnext  <- mkRegU;     // ... where to go on from
  Reg#(Addr)     vaddr  <- mkRegU;     // ... its three cells
  Reg#(ShState)  afterK <- mkRegU;     // where to go on from a removal
  FIFO#(ShReq)    reqQ <- mkFIFO;
  FIFO#(ShResult) resQ <- mkFIFO;
  FIFO#(Bool)     endQ <- mkFIFO;

  Addr shCount  = fromInteger(lay_SH_COUNT);
  Addr shStatus = fromInteger(lay_SH_STATUS);
  Addr shParent = fromInteger(lay_SH_PARENT);
  Addr shReport = fromInteger(lay_SH_REPORT);
  Addr shGoal   = fromInteger(lay_SH_GOAL);
  Addr shRed    = fromInteger(lay_SH_REDUCTIONS);
  Addr shRemove = fromInteger(lay_SH_REMOVE);

  function Action answer(Cell a, Cell b, Bool ok);
    action
      resQ.enq(ShResult { a: a, b: b, ok: ok });
      st <= ShIdle;
    endaction
  endfunction

  function Action report(Bit#(32) c, ShState next);
    action
      code <= intC(c);
      after <= next;
      st <= ShR1;
    endaction
  endfunction

  // a message {c, h, l}: its three cells, then as report
  function Action reportVec(Bit#(32) c, Bit#(32) h, Bit#(32) l, ShState next);
    action
      vcode <= c;
      vhi <= h;
      vlo <= l;
      vnext <= next;
      st <= ShV1;
    endaction
  endfunction

  // the removal of a terminated shoen: return_resource, the close, then
  // on to next
  function Action removal(ShState next);
    action
      afterK <= next;
      reportVec(fromInteger(lay_REPORT_RETURN_RESOURCE), 0, 0, ShK1);
    endaction
  endfunction

  rule accept (st == ShIdle);
    reqQ.deq;
    case (reqQ.first) matches
      tagged Create: begin
        parent <= gbox.shoen;
        gbox.alloc(fromInteger(lay_SH_SIZE));
        st <= ShC1;
      end
      tagged Start .h: begin
        sh <= cellAddr(h);
        mem.read(cellAddr(h) + shStatus);
        st <= ShS1;
      end
      tagged EndReduction .n: begin
        if (gbox.shoen == 0) endQ.enq(True);       // the root: nothing
        else begin
          sh <= gbox.shoen;
          red <= n;
          mem.read(gbox.shoen + shRed);
          st <= ShE0;
        end
      end
      tagged Stats .h: begin
        sh <= cellAddr(h);
        mem.read(cellAddr(h) + shRed);
        st <= ShQ1;
      end
      tagged Remove .h: begin
        sh <= cellAddr(h);
        mem.read(cellAddr(h) + shStatus);
        st <= ShM1;
      end
    endcase
  endrule

  // ---- create ------------------------------------------------------
  rule create1 (st == ShC1);
    let a <- gbox.allocResult;
    sh <= a;
    mem.write(a + shCount, intC(1));
    st <= ShC2;
  endrule

  rule create2 (st == ShC2);
    mem.write(sh + shStatus, intC(fromInteger(lay_DORMANT)));
    st <= ShC3;
  endrule

  rule create3 (st == ShC3);
    mem.write(sh + shParent, intC(parent == 0 ? 0 : absAddr(parent)));
    gbox.newVar;
    st <= ShC4;
  endrule

  rule create4 (st == ShC4);
    let v <- gbox.newVarResult;
    var_ <= v;
    mem.write(sh + shReport, v);
    gbox.recordFor(sh, applyStub, 2);
    st <= ShC5;
  endrule

  rule create5 (st == ShC5);
    let g <- gbox.recordResult;
    mem.write(sh + shGoal, intC(absAddr(g)));
    st <= ShC8;
  endrule

  // no reductions yet, no remove
  rule create8 (st == ShC8);
    mem.write(sh + shRed, intC(0));
    st <= ShC9;
  endrule

  rule create9 (st == ShC9);
    mem.write(sh + shRemove, intC(0));
    if (parent == 0) answer(var_, mkCell(tag_SHREC, absAddr(sh)), True);
    else st <= ShC6;
  endrule

  // the child is one of its parent's
  rule create6 (st == ShC6);
    mem.read(parent + shCount);
    st <= ShC7;
  endrule

  rule create7 (st == ShC7);
    let c <- mem.data;
    mem.write(parent + shCount, intC(c.val + 1));
    answer(var_, mkCell(tag_SHREC, absAddr(sh)), True);
  endrule

  // ---- start -------------------------------------------------------
  rule start1 (st == ShS1);
    let c <- mem.data;
    if (c.val != fromInteger(lay_DORMANT)) answer(?, ?, False);
    else report(fromInteger(lay_REPORT_STARTED), ShS2);
  endrule

  rule start2 (st == ShS2);
    mem.write(sh + shStatus, intC(fromInteger(lay_STARTED)));
    st <= ShS3;
  endrule

  rule start3 (st == ShS3);
    mem.read(sh + shGoal);
    st <= ShS4;
  endrule

  rule start4 (st == ShS4);
    let c <- mem.data;
    gbox.unpark(cellAddr(c));
    st <= ShS5;
  endrule

  rule start5 (st == ShS5);
    gbox.done;
    answer(?, ?, True);
  endrule

  // ---- the end of a reduction ----------------------------------------
  // the reductions first: the run's, or a terminated child's total
  rule end0 (st == ShE0);
    let c <- mem.data;
    let r = c.val + red;
    red <= r;
    mem.write(sh + shRed, intC(r));
    st <= ShE0b;
  endrule

  rule end0b (st == ShE0b);
    mem.read(sh + shCount);
    st <= ShE1;
  endrule

  rule end1 (st == ShE1);
    let c <- mem.data;
    mem.write(sh + shCount, intC(c.val - 1));
    if (c.val == 1) st <= ShE2;
    else begin
      endQ.enq(True);
      st <= ShIdle;
    end
  endrule

  rule end2 (st == ShE2);
    mem.write(sh + shStatus, intC(fromInteger(lay_TERMINATED)));
    report(fromInteger(lay_REPORT_TERMINATED), ShT1);
  endrule

  // a remove that came before the end: the shoen is removed now
  rule endT1 (st == ShT1);
    mem.read(sh + shRemove);
    st <= ShT2;
  endrule

  rule endT2 (st == ShT2);
    let c <- mem.data;
    if (c.val != 0) removal(ShE3);
    else st <= ShE3;
  endrule

  rule end3 (st == ShE3);
    mem.read(sh + shParent);
    st <= ShE4;
  endrule

  rule end4 (st == ShE4);
    let c <- mem.data;
    if (c.val == 0) begin
      endQ.enq(True);
      st <= ShIdle;
    end
    else begin
      sh <= cellAddr(c);
      mem.read(cellAddr(c) + shRed);     // red: the child's total
      st <= ShE0;
    end
  endrule

  // ---- statistics ------------------------------------------------------
  rule stats1 (st == ShQ1);
    let c <- mem.data;
    red <= c.val;
    report(fromInteger(lay_REPORT_STATISTICS_STARTED), ShQ2);
  endrule

  // twice the reductions, as 64 bits: high, low
  rule stats2 (st == ShQ2);
    reportVec(fromInteger(lay_REPORT_STATISTICS), red >> 31, red << 1, ShQ3);
  endrule

  rule stats3 (st == ShQ3);
    answer(?, ?, True);
  endrule

  // ---- remove ----------------------------------------------------------
  rule remove1 (st == ShM1);
    let c <- mem.data;
    if (c.val == fromInteger(lay_REMOVED)) answer(?, ?, False);
    else if (c.val == fromInteger(lay_TERMINATED)) removal(ShM2);
    else begin
      mem.write(sh + shRemove, intC(1));
      answer(?, ?, True);
    end
  endrule

  rule remove2 (st == ShM2);
    answer(?, ?, True);
  endrule

  // ---- a message {vcode, vhi, vlo} -------------------------------------
  rule vec1 (st == ShV1);
    gbox.alloc(3);
    st <= ShV2;
  endrule

  rule vec2 (st == ShV2);
    let a <- gbox.allocResult;
    vaddr <= a;
    mem.write(a, intC(vcode));
    st <= ShV3;
  endrule

  rule vec3 (st == ShV3);
    mem.write(vaddr + 1, intC(vhi));
    st <= ShV4;
  endrule

  rule vec4 (st == ShV4);
    mem.write(vaddr + 2, intC(vlo));
    code <= mkCell(tag_VECT0o + 6, absAddr(vaddr));
    after <= vnext;
    st <= ShR1;
  endrule

  // ---- the close of the report stream, the status REMOVED ---------------
  rule close1 (st == ShK1);
    mem.read(sh + shReport);
    st <= ShK2;
  endrule

  rule close2 (st == ShK2);
    let t <- mem.data;
    dbox.deref(t);
    st <= ShK3;
  endrule

  rule close3 (st == ShK3);
    let t <- dbox.derefResult;
    if (!isRef(t)) fatal("the report stream of a shoen is bound");
    else begin
      dbox.unify(t, mkCell(tag_ATOMo, 0));
      st <= ShK4;
    end
  endrule

  rule close4 (st == ShK4);
    let r <- dbox.unifyResult;
    case (r) matches
      tagged UOk: begin
        mem.write(sh + shStatus, intC(fromInteger(lay_REMOVED)));
        st <= afterK;
      end
      tagged UWake .s: begin
        gbox.wake(s);
        st <= ShK5;
      end
      default: fatal("the report stream of a shoen did not close");
    endcase
  endrule

  rule close5 (st == ShK5);
    gbox.done;
    mem.write(sh + shStatus, intC(fromInteger(lay_REMOVED)));
    st <= afterK;
  endrule

  // ---- a message on the report stream of sh --------------------------
  rule report1 (st == ShR1);
    gbox.alloc(2);
    st <= ShR2;
  endrule

  rule report2 (st == ShR2);
    let a <- gbox.allocResult;
    lcell <= a;
    mem.write(a, code);
    st <= ShR3;
  endrule

  rule report3 (st == ShR3);
    mem.write(lcell + 1, mkCell(tag_UNDF, 0));
    st <= ShR4;
  endrule

  rule report4 (st == ShR4);
    mem.read(sh + shReport);
    st <= ShR5;
  endrule

  rule report5 (st == ShR5);
    let t <- mem.data;
    dbox.deref(t);
    st <= ShR6;
  endrule

  rule report6 (st == ShR6);
    let t <- dbox.derefResult;
    if (!isRef(t)) fatal("the report stream of a shoen is bound");
    else begin
      dbox.unify(t, mkCell(tag_LISTo, absAddr(lcell)));
      st <= ShR7;
    end
  endrule

  rule report7 (st == ShR7);
    let r <- dbox.unifyResult;
    case (r) matches
      tagged UOk: begin
        mem.write(sh + shReport, mkCell(tag_REFo, absAddr(lcell + 1)));
        st <= after;
      end
      tagged UWake .s: begin
        gbox.wake(s);
        st <= ShR8;
      end
      default: fatal("the report stream of a shoen did not take a message");
    endcase
  endrule

  rule report8 (st == ShR8);
    gbox.done;
    mem.write(sh + shReport, mkCell(tag_REFo, absAddr(lcell + 1)));
    st <= after;
  endrule

  method Action create = reqQ.enq(tagged Create);
  method Action start(Cell handle) = reqQ.enq(tagged Start handle);
  method ActionValue#(ShResult) result;
    resQ.deq;
    return resQ.first;
  endmethod
  method Action endReduction(Bit#(32) n) = reqQ.enq(tagged EndReduction n);
  method Action ended = endQ.deq;
  method Action statistics(Cell handle) = reqQ.enq(tagged Stats handle);
  method Action remove(Cell handle) = reqQ.enq(tagged Remove handle);
endmodule

endpackage
