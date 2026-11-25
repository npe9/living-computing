// PIM/m core: the timer box, the processor's alarm (R7L, 2026-11-25).
// One alarm, as VPIM keeps one for each processor (interpreter/
// klb_pimos.psl.c kblt_b_set_timer: the PE's AlarmTimerVar and
// _SetAlarmTimer; functions/f_event_external_int.psl.c
// f_WakeupGoalByAlarmClock).  ref/pimm/pimm.py i_set_timer,
// fire_alarm and alarm_skip are the reference; the clock itself is the
// exec stage's (PimmStages.bsv ticks, clk), the time `now` given here.
//
//   set(t, now)   set_timer(Time, ^Wakeup): an alarm already armed is
//                 cancelled first, its Wakeup bound to [] (VPIM: "the
//                 cancelling of the earlier request is shown by []");
//                 then a time reached at now ("T2 is after T1 :- T2 &-
//                 T1 < 2^(W-1)", reached below) answers {INT, now}, and
//                 one still to come arms the alarm with a fresh variable,
//                 which is the answer.  Answered by setResult
//   armed, time   the alarm, for the core's check at each goal switch
//                 (PimmCore.bsv pick_or_fire) and the driver's ALARM
//   fire(now)     the alarm's Wakeup bound to {INT, now}, its goals
//                 woken, the alarm cleared.  Answered by fired
//
// A Wakeup that someone else has bound stops the simulation (the
// reference refuses it too).  Binding is the data box's unify, waking
// the goal box's, as the shoen box's report does (PimmShBox.bsv ShR6-8).
package PimmTBox;

import FIFO::*;
import PimmGen::*;
import PimmTypes::*;
import PimmDBox::*;
import PimmGBox::*;

interface PimmTBox;
  method Action set(Bit#(32) t, Bit#(32) now);
  method ActionValue#(Cell) setResult;
  method Bool armed;
  method Bit#(32) time_;
  method Action fire(Bit#(32) now);
  method Action fired;
endinterface

// a time t is reached at now: (now - t) mod 2^32 < 2^31
function Bool reached(Bit#(32) t, Bit#(32) now);
  Bit#(32) d = now - t;
  return d[31] == 0;
endfunction

typedef union tagged {
  struct { Bit#(32) t; Bit#(32) now; } Set;
  Bit#(32) Fire;
} TReq deriving (Bits);

typedef enum { TIdle, TBind1, TBind2, TBind3, TNew } TState deriving (Bits, Eq);

module mkPimmTBox#(PimmGBox gbox, PimmDBox dbox)(PimmTBox);
  Reg#(TState)   st     <- mkReg(TIdle);
  Reg#(Bool)     isArmed <- mkReg(False);
  Reg#(Bit#(32)) atime  <- mkRegU;     // the alarm's time
  Reg#(Cell)     avar   <- mkRegU;     // ... and its Wakeup
  Reg#(Bool)     setting <- mkRegU;    // a bind for set (else for fire)
  Reg#(Bit#(32)) rt     <- mkRegU;     // set: the time asked for
  Reg#(Bit#(32)) rnow   <- mkRegU;     // the time now
  FIFO#(TReq)    reqQ   <- mkFIFO;
  FIFO#(Cell)    resQ   <- mkFIFO;
  FIFO#(Bool)    firedQ <- mkFIFO;

  // set, once no alarm is armed: reached, or armed with a fresh Wakeup
  function Action decide(Bit#(32) t, Bit#(32) now);
    action
      if (reached(t, now)) begin
        resQ.enq(intC(now));
        st <= TIdle;
      end
      else begin
        gbox.newVar;
        st <= TNew;
      end
    endaction
  endfunction

  // the armed alarm's Wakeup bound, then on as setting says
  function Action bound();
    action
      isArmed <= False;
      if (setting) decide(rt, rnow);
      else begin
        firedQ.enq(True);
        st <= TIdle;
      end
    endaction
  endfunction

  rule accept (st == TIdle);
    reqQ.deq;
    case (reqQ.first) matches
      tagged Set .q: begin
        rt <= q.t;
        rnow <= q.now;
        setting <= True;
        if (isArmed) begin                 // the earlier request cancelled
          dbox.deref(avar);
          st <= TBind1;
        end
        else decide(q.t, q.now);
      end
      tagged Fire .now: begin
        if (!isArmed) fatal("timer box: fire with no alarm armed");
        rnow <= now;
        setting <= False;
        dbox.deref(avar);
        st <= TBind1;
      end
    endcase
  endrule

  rule bind1 (st == TBind1);
    let v <- dbox.derefResult;
    if (!isRef(v)) fatal("the Wakeup of set_timer is bound");
    else begin
      dbox.unify(v, setting ? mkCell(tag_ATOMo, 0) : intC(rnow));
      st <= TBind2;
    end
  endrule

  rule bind2 (st == TBind2);
    let r <- dbox.unifyResult;
    case (r) matches
      tagged UOk: bound;
      tagged UWake .s: begin
        gbox.wake(s);
        st <= TBind3;
      end
      default: fatal("the Wakeup of set_timer did not bind");
    endcase
  endrule

  rule bind3 (st == TBind3);
    gbox.done;
    bound;
  endrule

  rule newVar (st == TNew);
    let v <- gbox.newVarResult;
    avar <= v;
    atime <= rt;
    isArmed <= True;
    resQ.enq(v);
    st <= TIdle;
  endrule

  method Action set(Bit#(32) t, Bit#(32) now) = reqQ.enq(tagged Set { t: t, now: now });
  method ActionValue#(Cell) setResult;
    resQ.deq;
    return resQ.first;
  endmethod
  method Bool armed = isArmed;
  method Bit#(32) time_ = atime;
  method Action fire(Bit#(32) now) = reqQ.enq(tagged Fire now);
  method Action fired = firedQ.deq;
endmodule

endpackage
