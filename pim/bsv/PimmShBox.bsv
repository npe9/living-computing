// PIM/m core: the shoen box.  Stages 1 to 3 of the shoen:
// create_shoen, start_shoen, termination, shoen_statistics,
// remove_shoen; (stage 3) the exception path, stop_shoen, abort_shoen
// and the check of a goal taken from the ready queue.  No resource or
// profile: the exec stage refuses those built-ins.
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
//
// Stage 3 (docs/pimm_semantics.md "Shoen"; ref/pimm/pimm.py exception,
// taken_check, i_stop_shoen, i_abort_shoen say what is sourced where):
//   create(mask)  as above, the mask kept in SH_MASK after SH_REMOVE
//   start(h)      also a STOPPED shoen; every goal of its parked list
//                 (SH_GOAL, linked through G_LINK) is released, then the
//                 list is emptied (SH_GOAL := 0)
//   exception     the innermost shoen from the current one up whose
//                 mask AND tag is not 0 (none: ok = False, before any
//                 write); NewCode, NewArgv fresh; a READY goal
//                 apply(NewCode, NewArgv) of the current shoen; for a
//                 reduction failure (argn > 0) ArgV, a vector of
//                 r[0..argn); Info {0, b, c}; the message {2, num, Info,
//                 NewCode, NewArgv} on the found shoen's stream
//   stop(h)       11, then STARTED becomes STOPPED
//   abort(h)      a shoen at or above the current one: ok = False; 1,
//                 then, unless it has terminated, it terminates as at an
//                 ordinary end (12, the removal, the parent's reductions
//                 and count)
//   check(g)      the goal just taken: 0 run, 1 aborted (a TERMINATED or
//                 REMOVED shoen at or above its own), 2 parked (on the
//                 list of the innermost STOPPED one: status SUSPENDED,
//                 G_LINK := the list, SH_GOAL := g).  Answered by checked
//
// Reporting a message: two new cells {INT, code}{UNDF}; the stream's
// tail (the record's reference, followed through references by the
// data box) is unified with the list cell, the goal box waking the
// goals that waited on it; the record's tail is then the new cell.  A
// tail that someone has bound to a value stops the simulation.
//
// R8 (2026-11-25), the resource (ref/pimm/pimm.py end_reduction,
// taken_check, i_add_shoen_resource, i_allow_shoen_resource_report,
// remove say what is sourced where; the PIMOS manual e-shoen.tex:31,
// 42, 179, 224, 246):
//   create        the resource left (SH_RSC_HI, SH_RSC_LO, a signed 64
//                 bits) 0 and the flags (SH_RSC_FLAGS) 0, after the mask
//   endReduction  a run of n > 0 reductions first takes 2n from the
//                 resource left of the current shoen and of each above
//                 it, innermost first
//   check(g)      a shoen with no resource left (<= 0) stops the goal as
//                 a STOPPED one does; if the innermost such shoen is an
//                 exhausted one and its report-disallowed flag is off,
//                 the flag is set and resource_low (6) reported, then
//                 the goal parked
//   addResource   resource_added (5), then H:L added to the resource
//                 left; a STARTED shoen with some left now releases its
//                 parked list (start's path)
//   allowReport   resource_report_allowed (7), then the flag cleared
//   removal       {14, H, L}: the resource left, 0 if none
package PimmShBox;

import FIFO::*;
import PimmGen::*;
import PimmTypes::*;
import PimmMem::*;
import PimmDBox::*;
import PimmGBox::*;
import PimmRegs::*;

typedef struct { Cell a; Cell b; Bool ok; } ShResult deriving (Bits);

interface PimmShBox;
  method Action create(Cell mask);
  method Action start(Cell handle);
  method ActionValue#(ShResult) result;
  method Action endReduction(Bit#(32) n);
  method Action ended;
  method Action statistics(Cell handle);
  method Action remove(Cell handle);
  method Action addResource(Cell handle, Bit#(32) hi, Bit#(32) lo);   // 2026-11-24; R8 the amount
  method Action allowReport(Cell handle);   // 2026-11-24
  // stage 3
  method Action exception(Bit#(32) num, Bit#(32) tag, Cell b, Cell c, Bit#(8) argn);
  method Action stop(Cell handle);
  method Action abort(Cell handle);
  method Action check(Addr g);
  method ActionValue#(Bit#(2)) checked;
endinterface

typedef union tagged {
  Cell Create;
  Cell Start;
  Bit#(32) EndReduction;
  Cell Stats;
  Cell Remove;
  struct { Cell h; Bit#(32) hi; Bit#(32) lo; } AddRes;
  Cell AllowRep;
  struct { Bit#(32) num; Bit#(32) tag; Cell b; Cell c; Bit#(8) argn; } Exception;
  Cell Stop;
  Cell Abort;
  Addr Check;
} ShReq deriving (Bits);

typedef enum { ShIdle, ShC1, ShC2, ShC3, ShC4, ShC5, ShC6, ShC7,
               ShS1, ShS2, ShS3, ShS4, ShS5,
               ShE1, ShE2, ShE3, ShE4,
               ShR1, ShR2, ShR3, ShR4, ShR5, ShR6, ShR7, ShR8,
               ShC8, ShC9, ShE0, ShE0b, ShT1, ShT2, ShQ1, ShQ2, ShQ3, ShM1, ShM2,
               ShV1, ShV2, ShV3, ShV4, ShK1, ShK2, ShK3, ShK4, ShK5,
               ShC10, ShS6,
               ShX1, ShX2, ShX3, ShX4, ShX5, ShX6, ShX7, ShX8, ShX9, ShX10, ShX11, ShX12,
               ShX13, ShX14, ShX15, ShX16,
               ShP1, ShP2, ShA1, ShA2, ShA3, ShA4,
               ShH1, ShH2, ShH3, ShH4, ShH5, ShH6,
               // R8: the resource
               ShC11, ShC12, ShC13, ShN1, ShN2, ShN3, ShN4,
               ShH7, ShH8, ShH9, ShH11, ShU1, ShU2, ShU3, ShU4, ShU5,
               ShW1, ShW2, ShY1, ShY2, ShN5, ShU6 } ShState deriving (Bits, Eq);

module mkPimmShBox#(MemPort mem, PimmGBox gbox, PimmDBox dbox, PimmRegs regs)(PimmShBox);
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
  // stage 3
  Reg#(Cell)     mask   <- mkRegU;     // create: the exception mask
  Reg#(Addr)     g      <- mkRegU;     // start: the parked goal in hand; check: the goal
  Reg#(Bit#(32)) xnum   <- mkRegU;     // an exception: its number, tag, Info's b and c
  Reg#(Bit#(32)) xtag   <- mkRegU;
  Reg#(Cell)     xb     <- mkRegU;
  Reg#(Cell)     xc     <- mkRegU;
  Reg#(Bit#(8))  xn     <- mkRegU;     // ... ArgV's size (0: c as given)
  Reg#(Bit#(8))  xi     <- mkRegU;
  Reg#(Addr)     xt     <- mkRegU;     // ... the shoen it goes to
  Reg#(Cell)     xnc    <- mkRegU;     // ... NewCode, NewArgv
  Reg#(Cell)     xna    <- mkRegU;
  Reg#(Addr)     xa     <- mkRegU;     // ... a vector being written
  Reg#(Addr)     park   <- mkRegU;     // check: the innermost stopped shoen, or 0
  Reg#(Bool)     aborting <- mkReg(False);  // the end of a termination answers abort
  // R8: the resource
  Reg#(Bool)     parkStop <- mkRegU;   // check: park is a STOPPED shoen (else exhausted)
  Reg#(Bit#(32)) rhi    <- mkRegU;     // a resource left's high half, as read
  Reg#(Bit#(64)) rleft  <- mkRegU;     // add: the resource left after the add
  Reg#(Bit#(32)) ahi    <- mkRegU;     // add: the amount
  Reg#(Bit#(32)) alo    <- mkRegU;
  FIFO#(Bit#(2))  chkQ <- mkFIFO;
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
  Addr shMask   = fromInteger(lay_SH_MASK);
  Addr shRscHi  = fromInteger(lay_SH_RSC_HI);
  Addr shRscLo  = fromInteger(lay_SH_RSC_LO);
  Addr shRscFl  = fromInteger(lay_SH_RSC_FLAGS);
  Bit#(32) rscDisallowed = fromInteger(lay_RSC_REPORT_DISALLOWED);
  Addr gLink    = fromInteger(lay_G_LINK);
  Addr gStatus  = fromInteger(lay_G_STATUS);

  function Action answer(Cell a, Cell b, Bool ok);
    action
      resQ.enq(ShResult { a: a, b: b, ok: ok });
      st <= ShIdle;
    endaction
  endfunction

  // the end of a termination cascade: answers endReduction, or abort
  function Action endOf();
    action
      if (aborting) begin
        aborting <= False;
        answer(?, ?, True);
      end
      else begin
        endQ.enq(True);
        st <= ShIdle;
      end
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

  // the removal of a terminated shoen: return_resource with the
  // resource left (R8; ShY1, ShY2), the close, then on to next
  function Action removal(ShState next);
    action
      afterK <= next;
      mem.read(sh + shRscHi);
      st <= ShY1;
    endaction
  endfunction

  rule accept (st == ShIdle);
    reqQ.deq;
    case (reqQ.first) matches
      tagged Create .m: begin
        mask <= m;
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
          if (n == 0) begin
            mem.read(gbox.shoen + shRed);
            st <= ShE0;
          end
          else begin                                // R8: the resource first
            mem.read(gbox.shoen + shRscHi);
            st <= ShN1;
          end
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
      tagged Exception .q: begin
        xnum <= q.num;
        xtag <= q.tag;
        xb <= q.b;
        xc <= q.c;
        xn <= q.argn;
        if (gbox.shoen == 0) answer(?, ?, False);    // outside every shoen
        else begin
          xt <= gbox.shoen;
          mem.read(gbox.shoen + shMask);
          st <= ShX1;
        end
      end
      tagged Stop .h: begin
        sh <= cellAddr(h);
        report(fromInteger(lay_REPORT_STOPPED), ShP1);
      end
      // add_resource: resource_added, then the amount added (R8, ShU*)
      tagged AddRes .q: begin
        sh <= cellAddr(q.h);
        ahi <= q.hi;
        alo <= q.lo;
        report(fromInteger(lay_REPORT_RESOURCE_ADDED), ShU1);
      end
      // allow_resource_report: resource_report_allowed, then the flag
      // cleared (R8, ShW*)
      tagged AllowRep .h: begin
        sh <= cellAddr(h);
        report(fromInteger(lay_REPORT_RESOURCE_REPORT_ALLOWED), ShW1);
      end
      tagged Abort .h: begin
        sh <= cellAddr(h);
        if (gbox.shoen == cellAddr(h)) answer(?, ?, False);
        else if (gbox.shoen == 0) begin
          mem.read(cellAddr(h) + shStatus);
          st <= ShA2;
        end
        else begin
          mem.read(gbox.shoen + shParent);     // walking up from the current shoen
          st <= ShA1;
        end
      end
      tagged Check .q: begin
        g <= q;
        park <= 0;
        sh <= gbox.shoen;
        mem.read(gbox.shoen + shStatus);
        st <= ShH1;
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
    st <= ShC10;
  endrule

  // stage 3: the exception mask
  rule create10 (st == ShC10);
    mem.write(sh + shMask, intC(mask.val));
    st <= ShC11;
  endrule

  // R8: no resource yet, reports allowed
  rule create11 (st == ShC11);
    mem.write(sh + shRscHi, intC(0));
    st <= ShC12;
  endrule

  rule create12 (st == ShC12);
    mem.write(sh + shRscLo, intC(0));
    st <= ShC13;
  endrule

  rule create13 (st == ShC13);
    mem.write(sh + shRscFl, intC(0));
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
    if (c.val != fromInteger(lay_DORMANT) && c.val != fromInteger(lay_STOPPED)) answer(?, ?, False);
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

  // the parked list, in its order: the next goal's link is read before
  // the goal box rewrites it; then the list is emptied
  rule start4 (st == ShS4);
    let c <- mem.data;
    if (c.val == 0) begin
      mem.write(sh + shGoal, intC(0));
      answer(?, ?, True);
    end
    else begin
      g <= cellAddr(c);
      mem.read(cellAddr(c) + gLink);
      st <= ShS6;
    end
  endrule

  rule start6 (st == ShS6);
    let c <- mem.data;
    code <= c;                     // the next on the list
    gbox.unpark(g);
    st <= ShS5;
  endrule

  rule start5 (st == ShS5);
    gbox.done;
    if (code.val == 0) begin
      mem.write(sh + shGoal, intC(0));
      answer(?, ?, True);
    end
    else begin
      g <= cellAddr(code);
      mem.read(cellAddr(code) + gLink);
      st <= ShS6;
    end
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
    else endOf;
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
    if (c.val == 0) endOf;
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

  // ---- stage 3: an exception ------------------------------------------
  // the shoen that takes it: the innermost whose mask AND the tag is not 0
  rule exc1 (st == ShX1);
    let c <- mem.data;
    if ((c.val & xtag) != 0) begin
      gbox.newVar;
      st <= ShX3;
    end
    else begin
      mem.read(xt + shParent);
      st <= ShX2;
    end
  endrule

  rule exc2 (st == ShX2);
    let c <- mem.data;
    if (c.val == 0) answer(?, ?, False);      // none: refused
    else begin
      xt <= cellAddr(c);
      mem.read(cellAddr(c) + shMask);
      st <= ShX1;
    end
  endrule

  // NewCode, NewArgv, and the goal apply(NewCode, NewArgv) of the current
  // shoen, which waits for the handler
  rule exc3 (st == ShX3);
    let v <- gbox.newVarResult;
    xnc <= v;
    gbox.newVar;
    st <= ShX4;
  endrule

  rule exc4 (st == ShX4);
    let v <- gbox.newVarResult;
    xna <= v;
    gbox.applyGoal(xnc, v);
    st <= ShX5;
  endrule

  rule exc5 (st == ShX5);
    gbox.done;
    if (xn == 0) gbox.alloc(3);
    else gbox.alloc(zeroExtend(xn));
    st <= xn == 0 ? ShX8 : ShX6;
  endrule

  // a reduction failure's ArgV: r[0..xn) as they stand
  rule exc6 (st == ShX6);
    let a <- gbox.allocResult;
    xa <= a;
    mem.write(a, regs.r(0));
    xi <= 1;
    st <= ShX7;
  endrule

  rule exc7 (st == ShX7);
    if (xi == xn) begin
      xc <= mkCell(tag_VECT0o + (xn << 1), absAddr(xa));
      gbox.alloc(3);
      st <= ShX8;
    end
    else begin
      mem.write(xa + zeroExtend(xi), regs.r(xi));
      xi <= xi + 1;
    end
  endrule

  // Info {Pe, b, c}: one processor, Pe = 0
  rule exc8 (st == ShX8);
    let a <- gbox.allocResult;
    xa <= a;
    mem.write(a, intC(0));
    st <= ShX9;
  endrule

  rule exc9 (st == ShX9);
    mem.write(xa + 1, xb);
    st <= ShX10;
  endrule

  rule exc10 (st == ShX10);
    mem.write(xa + 2, xc);
    gbox.alloc(5);
    st <= ShX11;
  endrule

  // the message {2, num, Info, NewCode, NewArgv}
  rule exc11 (st == ShX11);
    let a <- gbox.allocResult;
    vaddr <= a;
    mem.write(a, intC(fromInteger(lay_REPORT_EXCEPTION)));
    st <= ShX12;
  endrule

  rule exc12 (st == ShX12);
    mem.write(vaddr + 1, intC(xnum));
    st <= ShX13;
  endrule

  rule exc13 (st == ShX13);
    mem.write(vaddr + 2, mkCell(tag_VECT0o + 6, absAddr(xa)));
    st <= ShX14;
  endrule

  rule exc14 (st == ShX14);
    mem.write(vaddr + 3, xnc);
    st <= ShX15;
  endrule

  rule exc15 (st == ShX15);
    mem.write(vaddr + 4, xna);
    sh <= xt;
    code <= mkCell(tag_VECT0o + 10, absAddr(vaddr));
    after <= ShX16;
    st <= ShR1;
  endrule

  rule exc16 (st == ShX16);
    answer(?, ?, True);
  endrule

  // ---- stage 3: stop (11 reported first) --------------------------------
  rule stop1 (st == ShP1);
    mem.read(sh + shStatus);
    st <= ShP2;
  endrule

  rule stop2 (st == ShP2);
    let c <- mem.data;
    if (c.val == fromInteger(lay_STARTED)) mem.write(sh + shStatus, intC(fromInteger(lay_STOPPED)));
    answer(?, ?, True);
  endrule

  // ---- stage 3: abort ----------------------------------------------------
  // a shoen at or above the current one is refused
  rule abort1 (st == ShA1);
    let c <- mem.data;
    if (c.val == 0) begin
      mem.read(sh + shStatus);
      st <= ShA2;
    end
    else if (cellAddr(c) == sh) answer(?, ?, False);
    else mem.read(cellAddr(c) + shParent);
  endrule

  rule abort2 (st == ShA2);
    let c <- mem.data;
    xnum <= c.val;
    report(fromInteger(lay_REPORT_ABORTED), ShA3);
  endrule

  rule abort3 (st == ShA3);
    if (xnum == fromInteger(lay_TERMINATED)) answer(?, ?, True);
    else begin
      mem.read(sh + shRed);
      st <= ShA4;
    end
  endrule

  // it terminates now: the end of a reduction's termination, answering abort
  rule abort4 (st == ShA4);
    let c <- mem.data;
    red <= c.val;
    aborting <= True;
    st <= ShE2;
  endrule

  // ---- stage 3: the goal just taken ----------------------------------------
  rule check1 (st == ShH1);
    let c <- mem.data;
    if (c.val == fromInteger(lay_TERMINATED) || c.val == fromInteger(lay_REMOVED)) begin
      chkQ.enq(1);
      st <= ShIdle;
    end
    else if (park == 0 && c.val == fromInteger(lay_STOPPED)) begin
      park <= sh;
      parkStop <= True;
      mem.read(sh + shParent);
      st <= ShH2;
    end
    else if (park == 0) begin          // R8: has it resource left?
      mem.read(sh + shRscHi);
      st <= ShH7;
    end
    else begin
      mem.read(sh + shParent);
      st <= ShH2;
    end
  endrule

  rule check7 (st == ShH7);
    let c <- mem.data;
    rhi <= c.val;
    mem.read(sh + shRscLo);
    st <= ShH8;
  endrule

  // exhausted: none left (signed, <= 0)
  rule check8 (st == ShH8);
    let c <- mem.data;
    Int#(64) left = unpack({rhi, c.val});
    if (left <= 0) begin
      park <= sh;
      parkStop <= False;
    end
    mem.read(sh + shParent);
    st <= ShH2;
  endrule

  // an exhausted shoen whose reports are allowed: the flag set, then
  // resource_low reported to it, then the goal parked
  rule check9 (st == ShH9);
    let c <- mem.data;
    if ((c.val & rscDisallowed) != 0) begin
      mem.read(g + gStatus);
      st <= ShH3;
    end
    else begin
      mem.write(park + shRscFl, intC(c.val | rscDisallowed));
      sh <= park;
      report(fromInteger(lay_REPORT_RESOURCE_LOW), ShH11);
    end
  endrule

  rule check11 (st == ShH11);
    mem.read(g + gStatus);
    st <= ShH3;
  endrule

  rule check2 (st == ShH2);
    let c <- mem.data;
    if (c.val != 0) begin
      sh <= cellAddr(c);
      mem.read(cellAddr(c) + shStatus);
      st <= ShH1;
    end
    else if (park == 0) begin
      chkQ.enq(0);
      st <= ShIdle;
    end
    else if (!parkStop) begin
      mem.read(park + shRscFl);
      st <= ShH9;
    end
    else begin
      mem.read(g + gStatus);
      st <= ShH3;
    end
  endrule

  // parked: SUSPENDED, on the stopped shoen's list
  rule check3 (st == ShH3);
    let c <- mem.data;
    mem.write(g + gStatus, intC({c.val[31:2], 2'd1}));
    st <= ShH4;
  endrule

  rule check4 (st == ShH4);
    mem.read(park + shGoal);
    st <= ShH5;
  endrule

  rule check5 (st == ShH5);
    let c <- mem.data;
    mem.write(g + gLink, c);
    st <= ShH6;
  endrule

  rule check6 (st == ShH6);
    mem.write(park + shGoal, intC(absAddr(g)));
    chkQ.enq(2);
    st <= ShIdle;
  endrule

  // ---- R8: the resource taken at the end of a run ----------------------
  // 2 for each of the run's red reductions, from sh and each shoen above
  rule charge1 (st == ShN1);
    let c <- mem.data;
    rhi <= c.val;
    mem.read(sh + shRscLo);
    st <= ShN2;
  endrule

  rule charge2 (st == ShN2);
    let c <- mem.data;
    Bit#(64) l = {rhi, c.val};
    Bit#(64) r = l - (zeroExtend(red) << 1);
    if (l[63] == 1 && r[63] == 0) fatal("the resource left of a shoen past 64 bits");
    else begin
      rleft <= r;
      mem.write(sh + shRscHi, intC(r[63:32]));
      st <= ShN3;
    end
  endrule

  rule charge3 (st == ShN3);
    mem.write(sh + shRscLo, intC(rleft[31:0]));
    st <= ShN5;
  endrule

  rule charge5 (st == ShN5);
    mem.read(sh + shParent);
    st <= ShN4;
  endrule

  // the top: then the reductions and the count, from the current shoen
  rule charge4 (st == ShN4);
    let c <- mem.data;
    if (c.val == 0) begin
      sh <= gbox.shoen;
      mem.read(gbox.shoen + shRed);
      st <= ShE0;
    end
    else begin
      sh <= cellAddr(c);
      mem.read(cellAddr(c) + shRscHi);
      st <= ShN1;
    end
  endrule

  // ---- R8: add_resource after its report ---------------------------------
  rule addRes1 (st == ShU1);
    mem.read(sh + shRscHi);
    st <= ShU2;
  endrule

  rule addRes2 (st == ShU2);
    let c <- mem.data;
    rhi <= c.val;
    mem.read(sh + shRscLo);
    st <= ShU3;
  endrule

  // a sum of 2^63 or more is refused (return_resource: not modelled)
  rule addRes3 (st == ShU3);
    let c <- mem.data;
    Int#(66) l = signExtend(unpack({rhi, c.val}));
    Int#(66) s = l + unpack(zeroExtend({ahi, alo}));
    if (s >= unpack(66'h0_8000_0000_0000_0000))
      fatal("add_shoen_resource past 2^63 (return_resource)");
    else begin
      Bit#(64) r = truncate(pack(s));
      rleft <= r;
      mem.write(sh + shRscHi, intC(r[63:32]));
      st <= ShU4;
    end
  endrule

  rule addRes4 (st == ShU4);
    mem.write(sh + shRscLo, intC(rleft[31:0]));
    st <= ShU6;
  endrule

  rule addRes6 (st == ShU6);
    mem.read(sh + shStatus);
    st <= ShU5;
  endrule

  // a STARTED shoen with some left: its parked goals released, as start's
  rule addRes5 (st == ShU5);
    let c <- mem.data;
    Int#(64) left = unpack(rleft);
    if (left > 0 && c.val == fromInteger(lay_STARTED)) st <= ShS3;
    else answer(?, ?, True);
  endrule

  // ---- R8: allow_resource_report after its report -----------------------
  rule allow1 (st == ShW1);
    mem.read(sh + shRscFl);
    st <= ShW2;
  endrule

  rule allow2 (st == ShW2);
    let c <- mem.data;
    mem.write(sh + shRscFl, intC(c.val & ~rscDisallowed));
    answer(?, ?, True);
  endrule

  // ---- R8: the removal's return_resource: what is left, 0 if none -------
  rule remove3 (st == ShY1);
    let c <- mem.data;
    rhi <= c.val;
    mem.read(sh + shRscLo);
    st <= ShY2;
  endrule

  rule remove4 (st == ShY2);
    let c <- mem.data;
    Bit#(64) l = {rhi, c.val};
    if (l[63] == 1) l = 0;
    reportVec(fromInteger(lay_REPORT_RETURN_RESOURCE), l[63:32], l[31:0], ShK1);
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

  method Action create(Cell m) = reqQ.enq(tagged Create m);
  method Action start(Cell handle) = reqQ.enq(tagged Start handle);
  method ActionValue#(ShResult) result;
    resQ.deq;
    return resQ.first;
  endmethod
  method Action endReduction(Bit#(32) n) = reqQ.enq(tagged EndReduction n);
  method Action ended = endQ.deq;
  method Action statistics(Cell handle) = reqQ.enq(tagged Stats handle);
  method Action addResource(Cell handle, Bit#(32) hi, Bit#(32) lo) =
    reqQ.enq(tagged AddRes { h: handle, hi: hi, lo: lo });
  method Action allowReport(Cell handle) = reqQ.enq(tagged AllowRep handle);
  method Action remove(Cell handle) = reqQ.enq(tagged Remove handle);
  method Action exception(Bit#(32) num, Bit#(32) tag, Cell b, Cell c, Bit#(8) argn) =
    reqQ.enq(tagged Exception { num: num, tag: tag, b: b, c: c, argn: argn });
  method Action stop(Cell handle) = reqQ.enq(tagged Stop handle);
  method Action abort(Cell handle) = reqQ.enq(tagged Abort handle);
  method Action check(Addr goal) = reqQ.enq(tagged Check goal);
  method ActionValue#(Bit#(2)) checked;
    chkQ.deq;
    return chkQ.first;
  endmethod
endmodule

endpackage
