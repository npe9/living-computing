// StretchDivBox.bsv -- the floating-point divide as ITERATIVE HARDWARE
// rather than a combinational answer plus a charged budget.
//
// >>> THE POINT, IN THE OWNER'S WORDS: "you aren't trying to EMULATE
// Stretch's timings, you are trying to REPRODUCE them", and "stalls
// etc should happen as actual stalls, not as faked rules." <<<
//
// Today `fpDivFrac` (StretchFP.bsv) performs all 96 restoring-division
// iterations combinationally in ONE clock, and `eboxClocks` charges a
// flat 4 for `/` -- a number its own comment calls a floor, because
// Performance Characteristics Vol. 1 Table 2 adds "2 cycles for each
// additional reduction loop (number of cycles is data dependent)" and
// nothing here computes that. Two notions of completion result: the
// answer exists, and separately a budget has not yet expired.
//
// This module is the first box. It is DELIBERATELY STANDALONE and
// nothing in the core instantiates it yet: a box should be testable
// without instantiating all of storage, which is also how Flute keeps
// `mkIntDiv` (~/src/Flute/src_Core/CPU/IntMulDiv.bsv) separate from its
// CPU, and it means this cannot destabilise the 5,633-check suite while
// its shape is being settled.
//
// ---------------------------------------------------------------------
// WHAT IS SOURCED, AND IT IS THE STRUCTURE
// ---------------------------------------------------------------------
// R23-9732 (7101 CPU CE manual) section 3.8 is nineteen per-instruction
// TIMING CHARTS, which docs/source_audit.md's Audit 3 lists as unmined
// and its goal table calls "the first real per-cycle source" for M1.
// Two of them were read at the ink:
//
//   Figure 3.8.19, SAU DIVIDE (TIMING), PDF 243 / printed 8-23:
//     "GATE COUNTER ADDER TO REG & SUB SHIFT AMOUNT FROM CTR"
//     "(D3, CTR=0, TRUE RESULT)" -> "FINAL DVDE TGR"
//     "REDUCTION CYCLES JUST LIKE FP"
//
//   Figure 3.8.15 sheet 2, PDF 240 / printed 8-17/8-18, which names the
//   phases -- Trial Reduction Cycle, Intermediate Reduction Cycles,
//   Last Reduction Cycle -- and says, twice:
//     "Number of Reduction or Dummy Cycles Depend Upon Number of
//      Quotient Bits Developed per Step (Cycle)"
//
// So: a counter-driven loop of trial / intermediate / last reduction
// cycles, developing SEVERAL quotient bits per cycle, ending when the
// shift counter reaches zero. The divide is NOT 96 single-bit steps.
// That shape is what the state machine below implements.
//
// ---------------------------------------------------------------------
// >>> AND WHAT IS INVENTED, WHICH IS EXACTLY ONE NUMBER <<<
// ---------------------------------------------------------------------
// How many quotient bits a given cycle develops. Figure 3.8.15
// attributes it to the "Multiple Selection Circuits", which are ALDs
// this volume does not reproduce, so the rule is [NOT IN THE SOURCES].
//
// `divBitsPerCycle` below is therefore INVENTED and says so, following
// the precedent docs/microarchitecture_roadmap.md sets for the
// look-ahead: "Any LA-internal count written in Bluespec is invented
// and must say so." Six is chosen because the same chart's note --
// an intermediate cycle may be a dummy "if more than 6 quotient bits
// were developed on the previous reduction cycle" -- is the only
// number on the page, and it bounds a step rather than fixing one.
// IT IS NOT CALIBRATED AGAINST THE ATLAS. Doing that is the next step
// and needs Perf. Char. Vol. 2's measured divide page.
//
// THE ANSWER, BY CONTRAST, IS NOT INVENTED AND NOT APPROXIMATE: the
// loop performs the same 96 restoring steps `fpDivFrac` does, just
// several per clock instead of all of them at once, so the quotient and
// remainder are bit-identical. The testbench asserts exactly that.
package StretchDivBox;

import StretchTypes::*;
import StretchFP::*;

// >>> INVENTED. See the header. <<<  Quotient bits developed per
// reduction cycle. 96 restoring steps at this rate is the loop count.
Integer divBitsPerCycle = 6;
Integer divTotalBits    = 96;

typedef enum { DivIdle, DivTrial, DivReduce, DivLast, DivDone }
  DivState deriving (Bits, Eq, FShow);

interface FpDivBox;
  method Bool requestReady();
  method Action request(Bit#(96) dvd, Bit#(48) dvs);
  method Bool responseReady();
  method ActionValue#(Tuple2#(Bit#(49), Bit#(49))) response();
  // Reduction cycles actually taken: the timing oracle reads this
  // rather than a table being charged on the operation's behalf.
  method Bit#(16) cyclesTaken();
endinterface

(* synthesize *)
module mkFpDivBox(FpDivBox);
  Reg#(DivState)  rg_state <- mkReg(DivIdle);
  Reg#(Bit#(96))  rg_dvd   <- mkRegU;
  Reg#(Bit#(49))  rg_d     <- mkRegU;
  Reg#(Bit#(49))  rg_rem   <- mkReg(0);
  Reg#(Bit#(49))  rg_q     <- mkReg(0);
  Reg#(Bit#(8))   rg_ctr   <- mkReg(0);   // restoring steps still to do
  Reg#(Bit#(16))  rg_cyc   <- mkReg(0);

  // THE TRIAL REDUCTION CYCLE (fig 3.8.15's name). One cycle of setup
  // before the loop proper, which is what the chart shows preceding the
  // intermediate cycles.
  rule rl_trial (rg_state == DivTrial);
    rg_cyc   <= rg_cyc + 1;
    rg_state <= DivReduce;
  endrule

  // AN INTERMEDIATE REDUCTION CYCLE: develop up to `divBitsPerCycle`
  // quotient bits, and "SUB SHIFT AMOUNT FROM CTR" (fig 3.8.19).
  rule rl_reduce (rg_state == DivReduce);
    Bit#(49) rem = rg_rem;
    Bit#(49) q   = rg_q;
    Bit#(96) dvd = rg_dvd;
    Bit#(8)  n   = rg_ctr;
    for (Integer k = 0; k < divBitsPerCycle; k = k + 1)
      if (n != 0) begin
        rem = { rem[47:0], dvd[95] };
        dvd = { dvd[94:0], 1'b0 };
        if (rem >= rg_d) begin
          rem = rem - rg_d;
          q   = { q[47:0], 1'b1 };
        end else
          q   = { q[47:0], 1'b0 };
        n = n - 1;
      end
    rg_rem <= rem; rg_q <= q; rg_dvd <= dvd; rg_ctr <= n;
    rg_cyc <= rg_cyc + 1;
    // "(D3, CTR=0, TRUE RESULT) -> FINAL DVDE TGR": the counter
    // reaching zero is what ends the loop, not a count of iterations
    // decided in advance.
    rg_state <= (n == 0) ? DivLast : DivReduce;
  endrule

  rule rl_last (rg_state == DivLast);
    rg_cyc   <= rg_cyc + 1;
    rg_state <= DivDone;
  endrule

  method Bool requestReady() = (rg_state == DivIdle);

  method Action request(Bit#(96) dvd, Bit#(48) dvs) if (rg_state == DivIdle);
    rg_dvd   <= dvd;
    rg_d     <= { 1'b0, dvs };
    rg_rem   <= 0;
    rg_q     <= 0;
    rg_ctr   <= fromInteger(divTotalBits);
    rg_cyc   <= 0;
    rg_state <= DivTrial;
  endmethod

  method Bool responseReady() = (rg_state == DivDone);

  method ActionValue#(Tuple2#(Bit#(49), Bit#(49))) response()
      if (rg_state == DivDone);
    rg_state <= DivIdle;
    return tuple2(rg_q, rg_rem);
  endmethod

  method Bit#(16) cyclesTaken() = rg_cyc;
endmodule

// ---------------------------------------------------------------------
// THE BOX'S OWN TESTBENCH.  It lives here rather than in a
// Stretch*Tb.bsv file because that pattern is gitignored (the 294
// generated testbenches), and this one is hand-written and must be
// committed -- the same reason mkStretchTb lives inside StretchSmoke.
//
// TWO ASSERTIONS, AND THEY ARE DIFFERENT IN KIND:
//
//   THE ANSWER is checked against `fpDivFrac`, the combinational divide
//   the model has always used.  It must be BIT-IDENTICAL: the box does
//   the same 96 restoring steps, several per clock instead of all at
//   once, so there is no approximation to tolerate.  This is the
//   assertion that would catch a broken datapath.
//
//   THE CYCLE COUNT is checked against the loop's own arithmetic --
//   one trial cycle, ceil(96 / divBitsPerCycle) reduction cycles, one
//   last cycle.  This is the assertion that makes the TIMING
//   structural: it reads what the FSM actually took, not what a table
//   says it should have cost.  It is NOT a claim that 18 is what an
//   IBM 7030 took; divBitsPerCycle is invented (see the header) and
//   calibrating it against Perf. Char. Vol. 2's measured divide page
//   is the next step.
// ---------------------------------------------------------------------
typedef 5 NDivVec;

(* synthesize *)
module mkDivBoxTb(Empty);
  FpDivBox      box    <- mkFpDivBox;
  Reg#(Bit#(4)) idx    <- mkReg(0);
  Reg#(Bit#(8)) fails  <- mkReg(0);
  Reg#(Bool)    issued <- mkReg(False);
  Reg#(Bool)    done   <- mkReg(False);

  // Divisors are pre-normalised (>= 2^47), which is what fpDivFrac's
  // own comment requires of its caller.
  function Bit#(96) dvdOf(Bit#(4) i) =
    case (i)
      0: 96'h000000000001_000000000000;
      1: 96'h800000000000_000000000000;
      2: 96'h123456789abc_def012345678;
      3: 96'hffffffffffff_ffffffffffff;
      default: 96'h000000000000_000000000001;
    endcase;
  function Bit#(48) dvsOf(Bit#(4) i) =
    case (i)
      0: 48'h800000000000;
      1: 48'hffffffffffff;
      2: 48'hc000000000ff;
      3: 48'h800000000001;
      default: 48'h800000000000;
    endcase;

  // >>> A LITERAL, NOT A FORMULA, AND THE FIRST VERSION OF THIS TEST
  // WAS WRONG BECAUSE IT WAS A FORMULA. <<<  It read
  // `1 + ceil(divTotalBits / divBitsPerCycle) + 1`, which is computed
  // FROM the constant under test, so changing divBitsPerCycle from 6
  // to 8 moved the FSM and its own expectation together and the test
  // still passed.  An expectation derived from the thing it checks is
  // not an expectation.  Eighteen is 1 trial + 16 reduction cycles
  // (96 restoring steps at 6 per cycle) + 1 last.
  Integer expCycles = 18;

  rule rl_issue (!done && !issued && box.requestReady());
    box.request(dvdOf(idx), dvsOf(idx));
    issued <= True;
  endrule

  rule rl_collect (!done && issued && box.responseReady());
    Bit#(16) took = box.cyclesTaken();
    let got <- box.response();
    let want = fpDivFrac(dvdOf(idx), dvsOf(idx));
    if (tpl_1(got) != tpl_1(want) || tpl_2(got) != tpl_2(want)) begin
      $display("FAIL divbox[%0d] answer: q=%h want %h, rem=%h want %h",
               idx, tpl_1(got), tpl_1(want), tpl_2(got), tpl_2(want));
      fails <= fails + 1;
    end else if (took != fromInteger(expCycles)) begin
      $display("FAIL divbox[%0d] cycles = %0d, want %0d", idx, took, expCycles);
      fails <= fails + 1;
    end else
      $display("PASS divbox[%0d] q=%h rem=%h in %0d cycles",
               idx, tpl_1(got), tpl_2(got), took);
    issued <= False;
    if (idx == fromInteger(valueOf(NDivVec) - 1)) done <= True;
    else idx <= idx + 1;
  endrule

  rule rl_finish (done);
    if (fails == 0) $display("ALL TESTS PASSED");
    else $display("%0d TEST(S) FAILED", fails);
    $finish(0);
  endrule
endmodule

endpackage
