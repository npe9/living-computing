// PIM/m core: the shoen box.  Stage 1 of the shoen: create_shoen,
// start_shoen and termination, nothing more (no stop, abort, remove,
// statistics, resource, profile or exception: the exec stage refuses
// those built-ins).
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
//                 memory traffic.  Answered by ended
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
  method Action endReduction;
  method Action ended;
endinterface

typedef union tagged {
  void Create;
  Cell Start;
  void EndReduction;
} ShReq deriving (Bits);

typedef enum { ShIdle, ShC1, ShC2, ShC3, ShC4, ShC5, ShC6, ShC7,
               ShS1, ShS2, ShS3, ShS4, ShS5,
               ShE1, ShE2, ShE3, ShE4,
               ShR1, ShR2, ShR3, ShR4, ShR5, ShR6, ShR7, ShR8 } ShState deriving (Bits, Eq);

module mkPimmShBox#(MemPort mem, PimmGBox gbox, PimmDBox dbox)(PimmShBox);
  Reg#(ShState)  st     <- mkReg(ShIdle);
  Reg#(Addr)     sh     <- mkRegU;     // the shoen record in hand
  Reg#(Addr)     parent <- mkRegU;
  Reg#(Cell)     var_   <- mkRegU;     // create: the Report variable
  Reg#(Bit#(32)) code   <- mkRegU;     // the message being reported
  Reg#(ShState)  after  <- mkRegU;     // ... and where to go on from
  Reg#(Addr)     lcell  <- mkRegU;     // ... and its list cell
  FIFO#(ShReq)    reqQ <- mkFIFO;
  FIFO#(ShResult) resQ <- mkFIFO;
  FIFO#(Bool)     endQ <- mkFIFO;

  Addr shCount  = fromInteger(lay_SH_COUNT);
  Addr shStatus = fromInteger(lay_SH_STATUS);
  Addr shParent = fromInteger(lay_SH_PARENT);
  Addr shReport = fromInteger(lay_SH_REPORT);
  Addr shGoal   = fromInteger(lay_SH_GOAL);

  function Action answer(Cell a, Cell b, Bool ok);
    action
      resQ.enq(ShResult { a: a, b: b, ok: ok });
      st <= ShIdle;
    endaction
  endfunction

  function Action report(Bit#(32) c, ShState next);
    action
      code <= c;
      after <= next;
      st <= ShR1;
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
      tagged EndReduction: begin
        if (gbox.shoen == 0) endQ.enq(True);       // the root: nothing
        else begin
          sh <= gbox.shoen;
          mem.read(gbox.shoen + shCount);
          st <= ShE1;
        end
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
    report(fromInteger(lay_REPORT_TERMINATED), ShE3);
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
      mem.read(cellAddr(c) + shCount);
      st <= ShE1;
    end
  endrule

  // ---- a message on the report stream of sh --------------------------
  rule report1 (st == ShR1);
    gbox.alloc(2);
    st <= ShR2;
  endrule

  rule report2 (st == ShR2);
    let a <- gbox.allocResult;
    lcell <= a;
    mem.write(a, intC(code));
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
  method Action endReduction = reqQ.enq(tagged EndReduction);
  method Action ended = endQ.deq;
endmodule

endpackage
