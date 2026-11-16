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

// ---------------------------------------------------------------------
// ONE RESTORING STEP, shared by both boxes in this file so that there
// is exactly one statement of the arithmetic.  Shift the next dividend
// bit into the partial remainder, subtract the divisor if it goes, and
// report the quotient bit.  `fpDivFrac` (StretchFP.bsv) is 96 of these
// in a row; the boxes are the same 96, a few per clock.
// ---------------------------------------------------------------------
function Tuple3#(Bit#(49), Bit#(96), Bit#(1))
    divRestoringStep(Bit#(49) rem0, Bit#(96) dvd0, Bit#(48) d);
  Bit#(49) rem = { rem0[47:0], dvd0[95] };
  Bit#(96) dvd = { dvd0[94:0], 1'b0 };
  // ONE SUBTRACTOR, and its borrow IS the comparison: written as
  // `if (rem >= d) rem = rem - d` this synthesised a comparator's
  // carry chain beside the subtractor's, twice the arithmetic for the
  // same answer (measured on mkDivBox: 1,664 CCU2C before).
  Bit#(50) diff = {1'b0, rem} - {2'b0, d};
  Bit#(1)  qb   = ~diff[49];
  if (qb == 1) rem = diff[48:0];
  return tuple3(rem, dvd, qb);
endfunction

// ---------------------------------------------------------------------
// THE BOX THE CORE ACTUALLY INSTANTIATES (2026-11-15): mkDivBox.
//
// WHY IT EXISTS.  The model has to fit a ULX3S (ECP5-85F, about 84,000
// logic cells).  The VFL divide arm of execute() was `dvd / dsrSafe`
// and `dvd % dsrSafe` on 96 bits with a variable divisor -- measured
// alone at 118,755 LUT4 + 22,896 CCU2C, twice the FPGA by itself --
// and the floating-point arms inlined fpDivFrac's 96 unrolled
// subtract-and-select stages three times over (/, R/, D/).  All of
// that is now this one module, instantiated once in mkEBox and reached
// through execute()'s `NeedBox` bail (see ExecDispatch).
//
// ONE DATAPATH SERVES BOTH UNITS, and that is sourced: R23-9694
// printed p.121 says of the VFL divide "AS IN MULTIPLY, THIS OPERATION
// IS ACTUALLY PERFORMED BY PAU", and figure 3.8.19 says of the SAU
// divide's loop "REDUCTION CYCLES JUST LIKE FP".  96-bit dividend,
// 48-bit divisor: the double- and single-precision fraction lengths.
// The integer divide needs all 96 quotient bits; the floating-point
// divide takes the low 49, which is exactly what fpDivFrac's 49-bit
// shift register keeps.  The remainder is below the divisor, so 48
// bits hold it.
//
// >>> WHAT IS INVENTED HERE, AND IT IS AGAIN ONE NUMBER -- BUT A
// DIFFERENT ONE, CHOSEN FOR A DIFFERENT REASON. <<<
// `coreDivBitsPerCycle` is 24.  It is NOT a claim about the 7030 and
// it is NOT mkFpDivBox's 6.  It is the smallest rate at which the box
// answers inside the SMALLEST existing divide budget: eboxClocks
// charges floating-point `/` 4 clocks, and 96 bits in four reduction
// clocks is 24 a clock -- request at T, reductions at T+1 .. T+4, the
// answer taken at T+4 (mkDivBox's CReg note says why it is readable
// in the clock of the last reduction).
// This step replaces combinational hardware with iterative hardware
// and keeps the E-BOX's time: the core subtracts the clocks the box
// took from the budget it charges afterwards.  >>> IT DOES NOT KEEP
// EVERY INSTRUCTION'S TIME, AND THAT WAS MEASURED, 2026-11-16. <<<
// While the divide waits on the box its look-ahead level is held, so
// the instruction unit cannot execute an I-box instruction alongside
// it (rl_prepare's `!ebox.busyFor(OwnerLA)`, and the held level still
// counts in iboxHazard).  The old divide completed and retired in its
// first clock, and the I-box overlapped the budget countdown.  So a
// divide followed by I-box work now takes longer:
//   halt clocks, before the box -> after it at 24 / 48 / 96 bits a
//   clock (4 / 2 / 1 box clocks), measured on the eight moved decks:
//     fp_arith_f217b   220 -> 236 / 228 / 224   (+4 per box clock)
//     fp_arith_f217wb  205 -> 221 / 213 / 209   (+4 per box clock)
//     fp_arith_f217xb  201 -> 217 / 209 / 205   (+4 per box clock)
//     fp_arith_f217we  142 -> 150 / 146 / 144   (+2 per box clock)
//     fp_zm_cleared    563 -> 571 / 567 / 565   (+2 per box clock)
//     fp_arith_f217d   750 -> 754 / 750 / 750   (only above 2 clocks)
//     fp_arith_f217a   475 -> 477 / 477 / 477   (+2, constant)
//     fp_arith_f217c   180 -> 181 / 181 / 181   (+1, constant)
//   The other eight FP-divide decks, the three VFL-divide decks, MCP's
//   bootstrap and all thirteen CYCLES-checked suite entries are unchanged.
// The per-box-clock rows are that hold window, since they shrink with
// the box.  The two constant rows are something else and are not yet
// explained.  Getting the overlap back needs the I-box to run during a
// box wait, which is rl_prepare's business.  Making the box's own
// count BE the time is a later, sourced step, and when
// it comes this constant goes and mkFpDivBox's structure -- trial,
// intermediate and last reduction cycles, the normalisation loop --
// comes in.  For the same reason this box has none of those phases:
// each would be a clock the 4-clock budget does not have.
//
// THE COST OF 24: twenty-four 49-bit subtract-and-select stages
// chained in one clock.  That is a quarter of what fpDivFrac chained,
// and one instance instead of four, but it is still a long path; it is
// an area fix, not yet a clock-rate fix.
//
// >>> OPEN, AND SOURCED: CLOCKS PER REDUCTION PASS. <<<  A
// transcription of R23-9732's PAU/SAU timing charts made alongside
// this work (figures 3.8.15, PDF 239-241; 3.8.19, PDF 243; 3.8.20
// RECIPROCAL DIVIDE, PDF 244) reports that every normalisation and
// every reduction pass on 3.8.15 and 3.8.19 is drawn as one D3 period
// plus one D4 period -- TWO clock periods per pass -- and that the
// zero-divisor case is drawn as four periods.  mkFpDivBox below
// spends ONE clock per pass and its header records that discrepancy
// against Table 2 as unresolved.  THAT REPORT WAS NOT RE-READ AT THE
// INK FOR THIS CHANGE and is recorded as a pointer for the timing
// step, not as a finding: read the three figures before building on
// it.  Nothing in mkDivBox depends on it.
// ---------------------------------------------------------------------
typedef struct {
  Bit#(96) dvd;
  Bit#(48) dvs;
} DivReq deriving (Bits, Eq, FShow);

typedef struct {
  Bit#(96) q;      // all 96 quotient bits
  Bit#(48) rem;    // the remainder, which is below the divisor
} DivRsp deriving (Bits, Eq, FShow);

// >>> INVENTED, to fit the existing 4-clock budget.  See above. <<<
Integer coreDivBitsPerCycle = 24;

interface DivBox;
  method Action request(DivReq r);
  method Bool responseReady();
  // A VALUE, NOT AN ActionValue: taking the answer changes nothing in
  // the box.  The caller knows whether it is waiting (mkEBox's
  // `boxWait`), so the box needs no "idle again" state, and `request`
  // is then the ONLY method that writes the box's state -- which is
  // what lets one caller rule poll, take and re-request in one clock.
  method DivRsp response();
endinterface

typedef enum { CDivIdle, CDivReduce, CDivDone } CoreDivState
  deriving (Bits, Eq, FShow);

(* synthesize *)
module mkDivBox(DivBox);
  // >>> CREGS, AND THE PORT ASSIGNMENT IS THE SCHEDULE. <<<
  // rl_reduce reads and writes port 0; every method reads and writes
  // port 1.  So the rule is ordered BEFORE all of the methods, and no
  // rule of this module falls between two of them.  With plain Regs
  // the first build failed with bsc's G0096 ("requires dynamic
  // scheduling, which is not supported by Bluesim"): mkEBox.resume
  // polls responseReady (which must read rg_state before rl_reduce
  // writes it) and may call request (which writes what rl_reduce
  // reads, so must come after it) -- rl_reduce between two method
  // calls of one caller rule, across a synthesis boundary.
  //
  // THE CONSEQUENCE FOR TIME: a method sees rl_reduce's update in the
  // same clock, so the answer is readable in the clock of the last
  // reduction, not the one after.  request at clock T, reductions at
  // T+1 .. T+4, answer taken at T+4.  See coreDivBitsPerCycle.
  Reg#(CoreDivState) rg_state[2] <- mkCReg(2, CDivIdle);
  // ONE 96-BIT REGISTER HOLDS THE DIVIDEND AND THE QUOTIENT: the
  // dividend leaves at the top a bit at a time and the quotient bit
  // that step developed enters at the bottom, so after 96 steps the
  // register is the quotient.
  Reg#(Bit#(96))     rg_dq[2]    <- mkCReg(2, 0);
  Reg#(Bit#(49))     rg_rem[2]   <- mkCReg(2, 0);
  // Written only by request, read only by rl_reduce: rule before
  // method, which is the order the CRegs already impose.
  Reg#(Bit#(48))     rg_dvs      <- mkReg(0);
  // Reduction clocks still to do.  It counts CLOCKS, not steps, and
  // every clock does exactly coreDivBitsPerCycle steps: guarding each
  // step on a step counter (as mkFpDivBox does, where the rate need
  // not divide 96) put a wide select behind every step (measured at
  // 32 a clock: 9,325 LUT4 with the guard, 4,284 without).  So the
  // rate MUST divide 96, and elaboration refuses one that does not.
  Reg#(Bit#(8))      rg_ctr[2]   <- mkCReg(2, 0);
  Integer coreDivClocks = divTotalBits / coreDivBitsPerCycle;
  if (coreDivClocks * coreDivBitsPerCycle != divTotalBits)
    error("mkDivBox: coreDivBitsPerCycle must divide 96");

  rule rl_reduce (rg_state[0] == CDivReduce);
    Bit#(49) rem = rg_rem[0];
    Bit#(96) dq  = rg_dq[0];
    for (Integer k = 0; k < coreDivBitsPerCycle; k = k + 1) begin
      match {.r2, .d2, .qb} = divRestoringStep(rem, dq, rg_dvs);
      rem = r2;
      dq  = { d2[95:1], qb };
    end
    rg_rem[0] <= rem; rg_dq[0] <= dq; rg_ctr[0] <= rg_ctr[0] - 1;
    if (rg_ctr[0] == 1) rg_state[0] <= CDivDone;
  endrule

  // >>> NO METHOD HAS AN IMPLICIT CONDITION, ON PURPOSE. <<<  The
  // caller polls responseReady(), as every caller of StretchStorage
  // polls its handshake.  The first version guarded response() on
  // CDivDone, and bsc -- which does not push a method's condition
  // inside the `if` that calls it -- made that the condition of the
  // WHOLE of mkEBox.resume(): no instruction could resume from an
  // operand read unless the divider happened to hold a result, and
  // decks/vfl_divide.strap ran to the step cap on its first load.
  // The smoke test passed, because nothing in it waits for a read.
  method Action request(DivReq r);
    rg_dq[1]    <= r.dvd;
    rg_dvs      <= r.dvs;
    rg_rem[1]   <= 0;
    rg_ctr[1]   <= fromInteger(coreDivClocks);
    rg_state[1] <= CDivReduce;
  endmethod

  method Bool responseReady() = (rg_state[1] == CDivDone);

  method DivRsp response() = DivRsp { q: rg_dq[1], rem: rg_rem[1][47:0] };
endmodule

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
        match {.r2, .d2, .qb} = divRestoringStep(rem, dvd, rg_dvs);
        rem = r2;
        dvd = d2;
        q   = { q[47:0], qb };
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

// ---------------------------------------------------------------------
// mkDivBox's OWN TESTBENCH, in the same file for the same reason
// mkDivBoxTb is.  THREE ASSERTIONS PER VECTOR:
//
//   AGAINST THE OPERATORS.  q == dvd / dvs and rem == dvd % dvs on 96
//   bits -- the very expressions this box replaced in execute()'s VFL
//   divide arm.  They are fine in a testbench; they are what did not
//   fit in an FPGA.
//
//   AGAINST fpDivFrac.  The low 49 quotient bits and the remainder,
//   which is what the floating-point arms take.
//
//   THE CLOCK COUNT, a LITERAL 4: request at clock T, four reduction
//   clocks T+1 .. T+4, and the answer is taken at T+4.  4 is eboxClocks' budget for floating-point `/`, the
//   smallest divide budget there is, and the core relies on the box
//   fitting it (StretchCore's rl_exec_resume).
//
// The vectors are the cases the VFL arm's manual pages name: dividend
// below divisor, both at maximum width, a remainder one below the
// divisor, a one-bit divisor, a quotient needing all 96 bits.  (A zero
// divisor is never sent: p.70's "THE DIVISION IS NOT ATTEMPTED".)
// ---------------------------------------------------------------------
typedef 8 NCoreDivVec;

(* synthesize *)
module mkCoreDivBoxTb(Empty);
  DivBox         box    <- mkDivBox;
  Reg#(Bit#(4))  idx    <- mkReg(0);
  Reg#(Bit#(8))  fails  <- mkReg(0);
  Reg#(Bool)     issued <- mkReg(False);
  Reg#(Bool)     done   <- mkReg(False);
  Reg#(Bit#(16)) clk    <- mkReg(0);
  Reg#(Bit#(16)) t0     <- mkReg(0);

  rule rl_clk; clk <= clk + 1; endrule

  function Bit#(96) dvdOf(Bit#(4) i) =
    case (i)
      0: 96'h000000000000_000000000005;   // dividend below divisor
      1: 96'hffffffffffff_ffffffffffff;   // maximum by maximum
      2: 96'hffffffffffff_ffffffffffff;   // maximum by one: q is 96 bits
      3: 96'h000000000000_0000000000ef;   // 239 / 60, MCP's clock divide
      4: 96'h123456789abc_def012345678;
      5: 96'h800000000000_000000000000;
      6: 96'h000000000001_fffffffffffd;   // remainder = divisor - 1
      default: 96'h000000000000_000000000000;   // zero dividend
    endcase;
  function Bit#(48) dvsOf(Bit#(4) i) =
    case (i)
      0: 48'h000000000007;
      1: 48'hffffffffffff;
      2: 48'h000000000001;
      3: 48'h00000000003c;
      4: 48'h00000fedcba9;
      5: 48'h800000000001;
      6: 48'hffffffffffff;
      default: 48'h000000000003;
    endcase;

  Integer expClocks = 4;   // a LITERAL: see the header

  rule rl_issue (!done && !issued);
    box.request(DivReq { dvd: dvdOf(idx), dvs: dvsOf(idx) });
    issued <= True;
    t0 <= clk;
  endrule

  rule rl_collect (!done && issued && box.responseReady());
    let got = box.response();
    Bit#(96) dvd = dvdOf(idx);
    Bit#(96) dvs = zeroExtend(dvsOf(idx));
    Bit#(96) wq  = dvd / dvs;
    Bit#(96) wr  = dvd % dvs;
    let fq = fpDivFrac(dvd, dvsOf(idx));
    Bit#(16) took = clk - t0;
    if (got.q != wq || zeroExtend(got.rem) != wr) begin
      $display("FAIL coredivbox[%0d] vs operators: q=%h want %h, rem=%h want %h",
               idx, got.q, wq, got.rem, wr);
      fails <= fails + 1;
    end else if (got.q[48:0] != tpl_1(fq) || {1'b0, got.rem} != tpl_2(fq)) begin
      $display("FAIL coredivbox[%0d] vs fpDivFrac: q49=%h want %h, rem=%h want %h",
               idx, got.q[48:0], tpl_1(fq), got.rem, tpl_2(fq));
      fails <= fails + 1;
    end else if (took != fromInteger(expClocks)) begin
      $display("FAIL coredivbox[%0d] clocks = %0d, want %0d", idx, took, expClocks);
      fails <= fails + 1;
    end else
      $display("PASS coredivbox[%0d] q=%h rem=%h in %0d clocks", idx, got.q, got.rem, took);
    issued <= False;
    if (idx == fromInteger(valueOf(NCoreDivVec) - 1)) done <= True;
    else idx <= idx + 1;
  endrule

  rule rl_finish (done);
    if (fails == 0) $display("ALL TESTS PASSED");
    else $display("%0d TEST(S) FAILED", fails);
    $finish(0);
  endrule
endmodule

endpackage
