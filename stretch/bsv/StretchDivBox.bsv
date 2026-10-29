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
// `divBitsPerCycle` below is therefore STILL NOT PROVEN, and says so.
// But it is no longer a number picked out of the air, and that changed
// on 2026-10-29 when the same figure was read for a different reason:
//
// >>> SIX IS THE MACHINE'S SHIFTER WIDTH, AND IT IS PRINTED IN THREE
// PLACES. <<<
//   * Vol. 1 Table 2, FOUR times, as the unit in which shifts are
//     charged: "2 cycles for each additional divisor shift OF 6",
//     "each additional dividend shift OF 6", "remainder norm. <= 6",
//     "norm. <= 6".
//   * Figure 3.8.19's divisor-normalization half: "(D3, BIT 2-0
//     SHIFT <= 6)", beside a lane labelled "NORMALIZATION LOOP".
//   * Figure 3.8.15 sheet 2: an intermediate cycle may be a dummy "if
//     more than 6 QUOTIENT BITS were developed on the previous
//     reduction cycle".
//
// So Table 2's "of 6" is not a grouping convention chosen by whoever
// wrote the table -- it is the width of the shifter, and the "+2 per
// additional shift of 6" is a NORMALISATION LOOP being counted from
// outside. That is why the divisor normalisation below is written as
// an actual loop: its cycle count then matches Table 2's rule BY
// CONSTRUCTION rather than by a formula evaluating the rule.
//
// >>> ONE DISCREPANCY, RECORDED RATHER THAN TUNED AWAY. <<<  This loop
// spends ONE cycle per shift of six; Table 2 charges TWO ("2 cycles for
// each additional divisor shift of 6").  Figure 3.8.19 shows the
// normalisation lane pulsing D4 and D3 in pairs, so a plausible reading
// is that one loop pass IS two machine cycles -- but that is a reading,
// not a statement, and no page says it.  The loop therefore reports its
// own passes (`normCycles`) and the test asserts those; converting
// passes to Table 2's cycles is left until something prints the rule.
//
// What remains unproven is only that the REDUCTION loop develops the
// same 6 bits a shift cycle moves. The sources bound it ("more than 6"
// forces a dummy cycle) without fixing it, and the atlas cannot settle
// it -- its divide pages divide by one and then by zero, which skips
// the loop entirely (docs/atlas_reading_guide.md).
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
// >>> AND THIS ONE IS SOURCED, unlike the line above. <<<  The shifter
// moves at most six places in a normalisation cycle: figure 3.8.19's
// "(D3, BIT 2-0 SHIFT <= 6)", and Table 2 charging shifts in units of
// six four separate times.  Named so the injection can move it.
Integer divShiftWidth = 6;
Integer divTotalBits    = 96;

typedef enum { DivIdle, DivNorm, DivTrial, DivReduce, DivLast, DivDone }
  DivState deriving (Bits, Eq, FShow);

interface FpDivBox;
  method Bool requestReady();
  // `dvs` is the RAW divisor: the box normalises it itself, in a loop,
  // because that loop's length is what Table 2 charges for.
  method Action request(Bit#(96) dvd, Bit#(48) dvs);
  method Bool responseReady();
  method ActionValue#(Tuple2#(Bit#(49), Bit#(49))) response();
  // Reduction cycles actually taken: the timing oracle reads this
  // rather than a table being charged on the operation's behalf.
  method Bit#(16) cyclesTaken();
  method Bit#(16) normCycles();
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
  Reg#(Bit#(48))  rg_dvs   <- mkRegU;    // the divisor, being normalised
  Reg#(Bit#(16))  rg_norm  <- mkReg(0);  // normalisation cycles, reported

  // THE DIVISOR NORMALISATION LOOP (figure 3.8.19's left half, the lane
  // labelled "NORMALIZATION LOOP").  It shifts at most SIX places a
  // cycle -- "(D3, BIT 2-0 SHIFT <= 6)" on that chart -- so a divisor
  // needing 13 places takes three passes, and Table 2's "2 cycles for
  // each additional divisor shift of 6" falls out of the loop instead
  // of being evaluated as a formula.  A zero divisor would never
  // normalise, so it exits on the counter rather than on the top bit;
  // the caller suppresses the whole operation in that case anyway
  // (p.93's ZD), which is also what makes the atlas's divide pages
  // useless.
  rule rl_norm (rg_state == DivNorm);
    rg_cyc  <= rg_cyc + 1;
    rg_norm <= rg_norm + 1;
    if (rg_dvs[47] == 1 || rg_dvs == 0)
      rg_state <= DivTrial;
    else begin
      Bit#(6) lead = 0;
      for (Integer k = 0; k < divShiftWidth; k = k + 1)
        if (rg_dvs[47 - k] == 0 && lead == fromInteger(k)) lead = fromInteger(k + 1);
      rg_dvs <= rg_dvs << lead;
    end
  endrule

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
        if (rem >= {1'b0, rg_dvs}) begin
          rem = rem - {1'b0, rg_dvs};
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
    rg_dvs   <= dvs;
    rg_d     <= { 1'b0, dvs };   // kept for FShow/debug; the loop uses rg_dvs
    rg_rem   <= 0;
    rg_q     <= 0;
    rg_ctr   <= fromInteger(divTotalBits);
    rg_cyc   <= 0;
    rg_norm  <= 0;
    rg_state <= DivNorm;
  endmethod

  method Bool responseReady() = (rg_state == DivDone);

  method ActionValue#(Tuple2#(Bit#(49), Bit#(49))) response()
      if (rg_state == DivDone);
    rg_state <= DivIdle;
    return tuple2(rg_q, rg_rem);
  endmethod

  method Bit#(16) cyclesTaken() = rg_cyc;
  // Reported separately so a test can check Table 2's divisor-shift
  // rule on its own, without the reduction loop's unproven term.
  method Bit#(16) normCycles() = rg_norm;
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

  // >>> RAW DIVISORS NOW, chosen for their LEADING-ZERO COUNTS. <<<
  // The box normalises internally, so these exercise the
  // normalisation loop at 0, 1, 7, 15 and 47 leading zeros.
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
      0: 48'h800000000000;   // 0 leading zeros
      1: 48'h400000000000;   // 1
      2: 48'h010000000000;   // 7
      3: 48'h000100000000;   // 15
      default: 48'h000000000001;  // 47
    endcase;
  // LITERALS, not a formula -- see the note below.  The loop shifts at
  // most 6 a cycle and then spends one more cycle observing that the
  // divisor is normalised, so it is ceil(lz/6) + 1: 1, 2, 3, 4, 9.
  function Bit#(16) expNormOf(Bit#(4) i) =
    case (i) 0: 1; 1: 2; 2: 3; 3: 4; default: 9; endcase;

  // >>> AND A LITERAL AGAIN, FOR THE REASON THE LAST VERSION OF THIS
  // TEST FAILED TO CATCH ITS OWN INJECTION. <<<  An expectation
  // computed from the constant under test is not an expectation.
  // 18 = 1 trial + 16 reduction (96 restoring steps at 6 a cycle) + 1
  // last, and the normalisation cycles are added per vector.
  Integer expAfterNorm = 18;

  rule rl_issue (!done && !issued && box.requestReady());
    box.request(dvdOf(idx), dvsOf(idx));
    issued <= True;
  endrule

  rule rl_collect (!done && issued && box.responseReady());
    Bit#(16) took  = box.cyclesTaken();
    Bit#(16) norm  = box.normCycles();
    let got <- box.response();
    // The answer is the division by the NORMALISED divisor, which is
    // what the box computes and what p.93 specifies.
    Bit#(48) raw  = dvsOf(idx);
    UInt#(6) lz   = countZerosMSB(raw);
    Bit#(48) nrm  = (raw == 0) ? 0 : (raw << lz);
    let want = fpDivFrac(dvdOf(idx), nrm);
    if (tpl_1(got) != tpl_1(want) || tpl_2(got) != tpl_2(want)) begin
      $display("FAIL divbox[%0d] answer: q=%h want %h, rem=%h want %h",
               idx, tpl_1(got), tpl_1(want), tpl_2(got), tpl_2(want));
      fails <= fails + 1;
    end else if (norm != expNormOf(idx)) begin
      $display("FAIL divbox[%0d] normalisation cycles = %0d, want %0d",
               idx, norm, expNormOf(idx));
      fails <= fails + 1;
    end else if (took != expNormOf(idx) + fromInteger(expAfterNorm)) begin
      $display("FAIL divbox[%0d] cycles = %0d, want %0d", idx, took,
               expNormOf(idx) + fromInteger(expAfterNorm));
      fails <= fails + 1;
    end else
      $display("PASS divbox[%0d] q=%h rem=%h in %0d cycles (%0d normalising)",
               idx, tpl_1(got), tpl_2(got), took, norm);
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
