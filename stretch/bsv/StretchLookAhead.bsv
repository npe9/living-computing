// StretchLookAhead.bsv
//
// The four-level look-ahead as a stage module (idiomatic-Bluespec
// rewrite step 5b, docs/microarchitecture_plan.md §1c): it owns the
// level ring and its head/tail/count, collects arriving operands and
// issues fetches every clock (collect), and gives the core's decision
// arms the levels plus the three things they do to them -- retire the
// head, load a new level at the tail, cancel everything on a wrong
// branch guess.

package StretchLookAhead;

import Vector::*;
import StretchTypes::*;
import StretchStorage::*;

interface LookAhead;
  method Action collect();                  // every clock: gather arrivals, issue one fetch
  method Vector#(4, LaLevel) levels();      // the levels after this clock's arrivals
  method Bit#(2) head();
  method Bit#(2) tail();
  method Bit#(3) count();
  method LaLevel headLevel();
  method Action retireHead();               // free the head, release levels waiting on it
  method Action load(LaLevel lv);           // a new level at the tail
  method Action cancelAll();                // wrong guess: every level, tail = head
endinterface

// Retire the head level: free it, release any level waiting on it.
function Vector#(4, LaLevel) releaseHead(Vector#(4, LaLevel) nl, Bit#(2) head);
  nl[head].valid = False;
  for (Integer k = 0; k < 4; k = k + 1)
    if (nl[k].waitFor matches tagged Valid .w &&& w == head) nl[k].waitFor = tagged Invalid;
  return nl;
endfunction

module mkLookAhead #(StretchStorage st) (LookAhead);
  // ---- Stage 3a: the look-ahead (docs/microarchitecture_plan.md §6,
  // Buchholz ch.15, Cocke & Kolsky §III.C). Four levels in a ring;
  // E-box-class instructions (VFL, connectives, floating point) leave
  // the instruction unit into a level with their operand address, the
  // levels' fetches are issued ahead through their own bus channels,
  // and the arithmetic unit removes levels in order, executing each
  // once its operand is present. A level whose operand address equals
  // that of an earlier unretired level waits for that level to retire
  // before fetching (a store ahead of a load to the same word: the
  // LAAR's job, here done conservatively for any earlier level). In
  // this first cut an I-box-class instruction waits for the levels to
  // drain before executing (no recovery levels yet), and so does a
  // load behind a progressive-indexing instruction, whose index
  // register is modified only at execution.
  // Two ports (mkCReg): port 0 is collect() (the core's every-clock
  // rl_la_fetch), port 1 every other method (called from the core's
  // decision arms, which run after it in the same clock) -- the one
  // intra-clock ordering the old monolithic step() relied on, now
  // explicit.
  Vector#(4, Array#(Reg#(LaLevel))) la <- replicateM(mkCReg(2, LaLevel{valid: False, kind: Whole, di: tagged Invalid,
        pc: 0, len: Half, da: tagged Invalid, data: tagged Invalid, fetchIssued: False,
        waitFor: tagged Invalid, branch: False, target: 0, storeAddr: tagged Invalid}));
  function Vector#(4, LaLevel) laRead(Integer port);
    Vector#(4, LaLevel) v = newVector;
    for (Integer k = 0; k < 4; k = k + 1) v[k] = la[k][port];
    return v;
  endfunction
  function Action laWrite(Integer port, Vector#(4, LaLevel) v) =
    action
      for (Integer k = 0; k < 4; k = k + 1) la[k][port] <= v[k];
    endaction;
  Reg#(Bit#(2)) laHead  <- mkReg(0);
  Reg#(Bit#(2)) laTail  <- mkReg(0);
  Reg#(Bit#(3)) laCount <- mkReg(0);

  method Action collect();
    Vector#(4, LaLevel) nl = laRead(0);
    for (Integer k = 0; k < 4; k = k + 1)
      if (nl[k].valid && nl[k].fetchIssued && !isValid(nl[k].data) && st.laReady(fromInteger(k))) begin
        let d <- st.laResp(fromInteger(k));
        nl[k].data = tagged Valid d;
      end
    Bool issuedLa = False;
    for (Integer k = 0; k < 4; k = k + 1)
      if (!issuedLa && nl[k].valid && isValid(nl[k].da) && !nl[k].fetchIssued && !isValid(nl[k].waitFor)) begin
        st.laReq(fromInteger(k), validValue(nl[k].da));
        nl[k].fetchIssued = True;
        issuedLa = True;
      end
    laWrite(0, nl);
  endmethod

  method Vector#(4, LaLevel) levels() = laRead(1);
  method Bit#(2) head() = laHead;
  method Bit#(2) tail() = laTail;
  method Bit#(3) count() = laCount;
  method LaLevel headLevel() = laRead(1)[laHead];

  method Action retireHead();
    laWrite(1, releaseHead(laRead(1), laHead));
    laHead <= laHead + 1; laCount <= laCount - 1;
  endmethod

  method Action load(LaLevel lv);
    for (Integer k = 0; k < 4; k = k + 1)
      if (fromInteger(k) == laTail) la[k][1] <= lv;
    laTail <= laTail + 1; laCount <= laCount + 1;
  endmethod

  method Action cancelAll();
    Vector#(4, LaLevel) nl = laRead(1);
    for (Integer k = 0; k < 4; k = k + 1) nl[k].valid = False;
    laWrite(1, nl);
    laTail <= laHead; laCount <= 0;
  endmethod
endmodule

endpackage
