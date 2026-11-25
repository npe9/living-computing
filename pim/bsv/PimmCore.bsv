// PIM/m core: memory, registers, the boxes, the two stages, and the
// rules that move an instruction between them and take the next goal.
//
// A goal is made by loading the argument registers and spawning it;
// `run` then takes goals from the ready queue, newest first, until the
// queue is empty (Idle) or the model stops loud.  A goal that cannot
// choose a clause is written back to memory, hooked on the variables
// it waits for, and woken when one is bound.
package PimmCore;

import FIFO::*;
import Vector::*;
import PimmGen::*;
import PimmTypes::*;
import PimmMem::*;
import PimmRegs::*;
import PimmDBox::*;
import PimmHBox::*;
import PimmGBox::*;
import PimmSBox::*;
import PimmVBox::*;
import PimmMBox::*;
import PimmNBox::*;
import PimmShBox::*;
import PimmScsiBox::*;
import PimmPBox::*;
import PimmStages::*;
import PimmTBox::*;

interface PimmCore;
  method Action newVar;                         // a fresh unbound variable
  method ActionValue#(Cell) newVarResult;
  method Action setArg(Bit#(8) n, Cell w);      // argument n (from 1) of the goal being built
  method Action spawn(Addr pc, Bit#(8) argn);
  // the spawned goal's record is written: the bench waits for it, so
  // that the next argument register it loads is not traced before the
  // record's cells
  method ActionValue#(Addr) spawned;
  method Action run;
  method ActionValue#(End) finished;
  // between runs: bind or compare two terms, look at a term
  method Action unifyReq(Cell a, Cell b);
  method ActionValue#(Bool) unifyDone;
  method Action derefReq(Cell w);
  method ActionValue#(Cell) derefResp;
  // between runs: make strings
  method Action newString(Bit#(32) n, Bit#(32) bits);
  method Action setElement(Cell s, Bit#(32) i, Bit#(32) e);
  method Action pokeWord(Cell s, Bit#(32) i, Bit#(32) w);
  method ActionValue#(Cell) stringResult;
  // the SCSI device, outside the core (PimmScsiBox.bsv): what the core
  // puts on the bus, the device's answers, and the device's turn when
  // the machine has run dry (a = the commands that finished)
  method ActionValue#(ScsiOut) scsiReq;
  method Action scsiResp(ScsiIn r);
  method Action scsiPoll;
  method ActionValue#(Bit#(32)) scsiPolled;
  // a checkpoint (ref/pimm/lockstep_shell.py), between runs, the queues
  // empty: what of a saved machine is not in its memory.  0 the heap
  // pointer; 1..3 the exec stage's (PimmExec.restore); 4, 16..31 the
  // SCSI box's (PimmScsiBox.restore).  Nothing is traced
  method Action restore(Bit#(8) which, Cell c);
  // R8: the driver's ALARM: the clock moved on to the armed alarm's time
  method Action skipToAlarm;
endinterface

// heap: "" for an empty heap, else a checkpoint's heap (PimmMem)
module mkPimmCore#(String image, String heap)(PimmCore);
  PimmMem   mem   <- mkPimmMem(image, heap);
  PimmRegs  regs  <- mkPimmRegs;
  PimmFetch fetch <- mkPimmFetch(mem.port[0]);
  PimmHBox  hbox  <- mkPimmHBox(mem.port[1]);
  PimmDBox  dbox  <- mkPimmDBox(mem.port[2]);
  PimmGBox  gbox  <- mkPimmGBox(mem.port[3], regs);
  PimmSBox  sbox  <- mkPimmSBox(mem.port[4], gbox);
  PimmVBox  vbox  <- mkPimmVBox(mem.port[6], gbox);
  PimmMBox  mbox  <- mkPimmMBox;
  PimmNBox  nbox  <- mkPimmNBox(mem.port[7], gbox);
  PimmShBox shbox <- mkPimmShBox(mem.port[8], gbox, dbox, regs);
  PimmScsiBox scsi <- mkPimmScsiBox(mem.port[9], gbox, dbox);
  PimmPBox  pbox  <- mkPimmPBox(mem.port[10], dbox);
  PimmTBox  tbox  <- mkPimmTBox(gbox, dbox);
  PimmExec  exec  <- mkPimmExec(regs, dbox, hbox, gbox, sbox, vbox, mbox, nbox, mem.port[5], shbox, scsi, pbox, tbox);

  FIFO#(Bool) runQ   <- mkFIFO;
  FIFO#(End)  endQ   <- mkFIFO;
  FIFO#(Bool) unifyQ <- mkFIFO;
  Reg#(Bool)  outsideUnify <- mkReg(False);   // a unifyReq is in the data box
  Reg#(Bool)  outsideWake  <- mkReg(False);   // ... and its wake in the goal box
  Reg#(Addr)  takenPc <- mkRegU;              // a goal of a shoen being checked
  // R8: the next goal is asked for here, the alarm fired first if its
  // time has come (pimm.py run: before pick)
  FIFO#(Bool) pickQ  <- mkFIFO;
  Reg#(Bool)  firing <- mkReg(False);

  rule toExec;
    let f <- fetch.out;
    exec.enq(f);
  endrule

  (* descending_urgency = "advance, reduction_ended, begin_run, goal_checked" *)
  rule advance;
    let s <- exec.out;
    case (s) matches
      tagged Next .pc: fetch.enq(pc);
      tagged Stop .e:
        // the reduction is over: the goal's shoen gets its reductions
        // and loses one (the shoen box; nothing for the root), then on
        // to the next goal
        if (e == EndDone || e == EndSusp) shbox.endReduction(exec.reductions);
        else endQ.enq(e);
    endcase
  endrule

  rule reduction_ended;
    shbox.ended;
    pickQ.enq(True);
  endrule

  rule begin_run;
    runQ.deq;
    pickQ.enq(True);
  endrule

  rule pick_or_fire (!firing);
    pickQ.deq;
    if (tbox.armed && reached(tbox.time_, exec.now[31:0])) begin
      tbox.fire(exec.now[31:0]);
      firing <= True;
    end
    else gbox.pickup;
  endrule

  rule alarm_fired (firing);
    tbox.fired;
    firing <= False;
    gbox.pickup;
  endrule

  rule next_goal;
    let m <- gbox.picked;
    case (m) matches
      tagged Valid .pc: begin
        // a goal of a shoen is checked first (shoen stage 3): run,
        // discarded (its shoen aborted) or parked (stopped)
        if (gbox.shoen != 0) begin
          takenPc <= pc;
          shbox.check(gbox.takenGoal);
        end
        else begin
          exec.newGoal;
          fetch.enq(pc);
        end
      end
      tagged Invalid: begin
        $display("Q");
        endQ.enq(EndIdle);
      end
    endcase
  endrule

  rule goal_checked;
    let k <- shbox.checked;
    if (k == 0) begin
      exec.newGoal;
      fetch.enq(takenPc);
    end
    else begin
      $display(k == 1 ? "E aborted" : "E park");
      pickQ.enq(True);
    end
  endrule

  rule outside_unified (outsideUnify);
    let r <- dbox.unifyResult;
    outsideUnify <= False;
    case (r) matches
      tagged UWake .s: begin
        gbox.wake(s);
        outsideWake <= True;
      end
      tagged UOk: unifyQ.enq(True);
      tagged UGoal .q: begin         // put off to a goal: the next run does it
        gbox.unifyGoal(q.a, q.b);
        outsideWake <= True;
      end
      default:    unifyQ.enq(False);
    endcase
  endrule

  rule outside_woke (outsideWake);
    gbox.done;
    outsideWake <= False;
    unifyQ.enq(True);
  endrule

  method Action newVar = gbox.newVar;
  method ActionValue#(Cell) newVarResult = gbox.newVarResult;
  method Action setArg(Bit#(8) n, Cell w) = regs.wa(n, w);
  method Action spawn(Addr pc, Bit#(8) argn) =
    gbox.record(fromInteger(lay_READY), pc, argn, True, True);
  method ActionValue#(Addr) spawned = gbox.recordResult;
  method Action run = runQ.enq(True);
  method ActionValue#(End) finished;
    endQ.deq;
    return endQ.first;
  endmethod
  method Action unifyReq(Cell a, Cell b);
    dbox.unify(a, b);
    outsideUnify <= True;
  endmethod
  method ActionValue#(Bool) unifyDone;
    unifyQ.deq;
    return unifyQ.first;
  endmethod
  method Action derefReq(Cell w) = dbox.deref(w);
  method ActionValue#(Cell) derefResp = dbox.derefResult;
  method Action newString(Bit#(32) n, Bit#(32) bits) = sbox.newStr(n, bits);
  method Action setElement(Cell s, Bit#(32) i, Bit#(32) e) = sbox.setElement(s, i, e);
  method Action pokeWord(Cell s, Bit#(32) i, Bit#(32) w) = sbox.poke(s, i, w);
  method ActionValue#(Cell) stringResult;
    let r <- sbox.result;
    return r.a;
  endmethod
  method ActionValue#(ScsiOut) scsiReq = scsi.devReq;
  method Action scsiResp(ScsiIn r) = scsi.devResp(r);
  method Action scsiPoll = scsi.poll;
  method ActionValue#(Bit#(32)) scsiPolled = scsi.polled;
  method Action skipToAlarm;
    if (!tbox.armed) fatal("ALARM with no alarm armed");
    else exec.skip(tbox.time_ - exec.now[31:0]);
  endmethod
  method Action restore(Bit#(8) which, Cell c);
    if (which == 0) gbox.setHp(cellAddr(c));
    else if (which < 4) exec.restore(which, c.val);
    else scsi.restore(which, c);
  endmethod
endmodule

endpackage
