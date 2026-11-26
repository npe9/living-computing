// StretchPAU.bsv -- mkPAU, THE PARALLEL ARITHMETIC UNIT, as one multi-cycle
// box (docs/fidelity_plan.md A4, 2026-11-26).
//
// >>> WHAT THIS IS <<<  The two boxes the E-box's floating-point and
// divide arms reached -- the floating-point box (mkFpBox: the FP multiply
// and the add's datapath, StretchFpBox.bsv until this file) and the
// divider (mkDivBox: the FP and VFL divides, StretchDivBox.bsv until this
// file; both files deleted 2026-11-26, see the history) -- become ONE
// stateful module with one request method, one responseReady poll and one
// response value: the mkFBox / mkRISCV_MBox shape (AGENTS.md, "Idiomatic
// Bluespec"), and the 7030's own.  Buchholz, "Planning a Computer System",
// §14.4, printed p.208 (PDF 233): "The arithmetic unit consists of a
// parallel unit for floating-point operations and a serial unit for
// variable-field-length operations ... Operations on the floating-point
// fraction and also variable-field-length binary multiply and divide
// operations are performed by the parallel unit."  One parallel unit, not
// two boxes.  mkSAU (StretchSAU.bsv) is the other half.
//
// >>> THE CLOCKS ARE THE OLD BOXES', EXACTLY (the relocation). <<<  Every
// class steps as its old box stepped: the multiply twelve multiplier bits
// a clock, four clocks (SOURCED: Buchholz printed p.210, Table 2); the add
// one clock (Table 2's one execution cycle); the divide 24 restoring steps
// a clock (CHOSEN, `coreDivBitsPerCycle`), with a floating-point divide
// held for the 7030's reduction-loop walk (SOURCED: Buchholz Figs. 14.11,
// 14.12).  So every instruction's time is what it was; fidelity_plan.md A4
// records the run that shows it.
//
// >>> SINCE STEP 3 (2026-11-26): THE ADD'S DATA-DEPENDENT TIME. <<<  Two
// changes, each behind a switch (THE STEPPING SWITCHES, below):
//   * `*+`'s sum is the unit's.  One FpMulAdd request runs the four
//     multiply passes and then an add pass on rg_ab's product, so the
//     E-box arm no longer calls fpAddDouble (pauChainMulAdd).
//   * Table 2's add-class terms are charged from the add pass's own
//     shift, normalization count, recomplement and forced zero: 1 cycle
//     a further pre-shift of 4, 2 a further normalization of 6, 2 for a
//     recomplement, 2 for a forced zero.  They go through `fpExtra`,
//     which mkEBox.boxCharge reads as it reads the divide's, onto `*+`
//     (pauMa*) and onto the plain adds (pauAddStep, pauAddForcedZero).
// The answers are unchanged (mkPauStepTb checks them bit for bit).
// fidelity_plan.md A4 records the atlas before and after each.
//
// >>> THE REGISTERS (Buchholz p.208; R23-9732 3.8.x). <<<  p.208: "The two
// units use the same arithmetic registers, namely a double-length
// accumulator of 128 bits (the left part being called register A and the
// right part register B), and a double-length operand register of 128 bits
// (C and D)."  The CE charts name the fraction spans the parallel unit
// works on: "AB 12-107" (96 bits), "A 12-59" and "C 12-59" (48 bits each)
// (docs/sau_pau_spec.md §2 item 1).  So, in this unit:
//   * `rg_ab`, 96 bits, the AB fraction 12-107: the MULTIPLY's product
//     register (the multiplier enters in its low half and leaves twelve
//     bits a pass while the product grows in from the top) and the
//     DIVIDE's dividend-and-quotient register (the dividend leaves at the
//     top a bit a step and the quotient enters at the bottom).  The old
//     boxes had one each (mkFpBox's rg_p, mkDivBox's rg_dq).
//   * `rg_cd`, 48 bits, the C fraction 12-59: the multiplicand and the
//     divisor.  The old boxes had one each (the multiply read it out of its
//     request; mkDivBox's rg_dvs).
//   * one state machine and one pass counter (mkFpBox's rg_ctr and
//     rg_state, mkDivBox's).
// That the multiplicand sits in C and the product in AB is a READING of
// p.208 and Fig. 14.7 ("A,B registers", "C,D registers" into the "Carry
// propagate adder 100 bits"), not a register transfer the pages print;
// the model's accumulator and operand registers are still StretchStorage's,
// and these are the unit's working copies.
//
// >>> WHAT IS NOT SHARED YET <<<
//   * The FP add's whole request (alignment shift, sum, normalization in
//     one clock), as mkFpBox had it.  The shifter is not walked a step a
//     clock; its time is charged from the counts (step 3).
//   * The remainder register and the divide's reduction-loop walk.
//   * THE VFL MULTIPLIER, still mkSAU's `rl_mul` (StretchSAU.bsv).  The
//     sources make it THIS unit's (docs/sau_pau_spec.md §6;
//     fidelity_plan.md A4 records the decision with its pages).  Moving it
//     changes mkSAU's internals, which this relocation leaves alone.
//
// >>> ONLY ONE CLASS IS EVER IN FLIGHT. <<<  mkEBox holds one instruction,
// a held instruction asks one box and waits for it, and an I-box
// instruction run beside a held one is REFUSED if it would ask a box
// (mkEBox.start).  A new request restarts the unit whatever it was doing;
// in particular a floating-point request clears a divide's walk, so an
// abandoned divide's walk can never hold back the next answer
// (mkPauMixTb vector 6).  With two boxes that could not happen, because
// the floating-point box never looked at the divider's walk.
//
// The old boxes' own headers follow, each under its own heading; "the box"
// in them now means that class of mkPAU.
//
// =====================================================================
// THE FLOATING-POINT CLASS (mkFpBox's header, 2026-11-19)
// =====================================================================
// StretchFpBox.bsv -- the FLOATING-POINT BOX: the expensive datapath of
// fpArithClass (StretchExecute.bsv) as a multi-cycle box.
//
// >>> WHY A BOX (AGENTS.md, "Idiomatic Bluespec") <<<  fpArithClass is
// the second-largest combinational function in the model, and the
// owner's rule is that its expensive datapath lives in "MULTI-CYCLE,
// stateful 'box' sub-modules ... instantiated once, with request/
// response methods" -- Piccolo's and Flute's mkFBox -- not inlined into
// the E-box rule.  This box has mkVflBox's shape (StretchSAU.bsv):
// instantiated ONCE in mkEBox (boxKind 4), reached through execute()'s
// `NeedBox` bail, a request method, a responseReady poll and a response
// value.  The request is a tagged union so that further classes join it
// without a new box.
//
// STAGE 1 (2026-11-19, plan §1c step 5f) MOVES THE MULTIPLY: the whole
// of fpMul (MULTIPLY, `*`) and fpMulDouble (MULTIPLY DOUBLE, `D*`, and
// the product half of MULTIPLY AND ADD, `*+`).  Those were three inlined
// 48 x 48 -> 96 multipliers, each followed by a 96-bit normalizer, in
// the E-box rule.  Here there is ONE multiplier, twelve bits wide, and
// ONE copy of each normalizer.  The box hands back the whole FpResult /
// FpdResult -- exponent, normalized fraction, generated/propagated, ZM --
// computed by fpMulProd / fpMulDoubleProd (StretchFP.bsv) from the
// product it formed, so the arm in fpArithClass only places the answer.
//
// STAGE 2 (2026-11-19) MOVES THE ADD'S DATAPATH: the alignment shift,
// the 97-bit add or subtract and the post-normalization of ADD (`+`,
// `+MG`), ADD TO MEMORY (`M+`, `M+MG`), ADD DOUBLE (`D+`, `D+MG`) and
// ADD TO FRACTION (`F+`).  Those were four inlined copies of a 96-bit
// shifter, a 97-bit adder, a 96-bit magnitude comparator and a 96-bit
// normalizer in the E-box rule (fpAdd twice, fpAddDouble twice).  (NOT
// all of them: the preparation still normalizes an UNFLAGGED survivor of
// a flagged pair, F204E4's rule, in the arm; and `*+`'s sum is still a
// whole fpAddDouble in its arm, the one full copy of this datapath left
// in the E-box rule.)  Here there is
// ONE, the parallel unit's: Buchholz printed p.210 (PDF 235),
// "the shifter and adder extend to 96 bits.  This makes it possible to
// have almost the same speed for single- and double-length arithmetic."
// fpArithClass keeps the PREPARATION (fpAddPrep / fpAddDoublePrep in
// StretchFP.bsv: the flagged-operand rules of Fig. 23, the "difference
// exceeds 95" rule, the noisy extension of p.87), which answers those
// cases itself and makes NO request, as a zero divisor makes none of
// the divide box; the box applies the FINISH (fpAddFinish /
// fpAddDoubleFinish) to its sum and hands back the whole FpResult /
// FpdResult, as for the multiply.
//
// THE BOX'S ADDER IS ITS OWN, NOT THE REFERENCE'S.  p.210: "Subtractions
// are carried out in 1s complement form with automatic end-around
// carry, but the result is always converted to absolute-value form with
// separate sign."  And Perf. Char. Vol. 1 Table 2 note 1 (printed p.3-6,
// PDF 24): "the operand which is pre-shifted will be complemented.
// Recomplementing will only occur if the complemented (following pre-
// shift) fraction is larger in magnitude than unshifted fraction."  So
// fpBoxAddSum complements the SHIFTED fraction, adds, takes the end-
// around carry when there is one and recomplements when there is not.
// The one-step reference, fpAddSumRef (StretchFP.bsv, the code the arms
// ran before), compares the magnitudes and subtracts the smaller from
// the larger.  The two agree on every input (the testbench checks them
// against each other through fpAdd / fpAddDouble); they are different
// circuits, which is what makes that check worth having.
//
// WHAT IS NOT WALKED: the shifter's step.  p.210: "The shifter is
// capable of shifting up to four positions to the right and up to six
// positions to the left at one time ... For longer shifts the operation
// is repeated automatically."  Table 2 charges that repetition ("1 cycle
// for each additional pre-shift of 4", "2 cycles for each additional
// norm. of 6", "2 cycles if recomplement is necessary").  This box does
// the whole shift, sum and normalization in ONE clock, Table 2's
// minimum EXECUTION ("+ (Add) ... 1 cycle (norm <= 6)"); that the four
// pre-execution cycles are spent before the request (operand transfer
// and exponent compare) is an INFERENCE from the table's two columns,
// not a printed statement.  The instruction's time is eboxClocks' flat
// 5, as before: the data-dependent terms are the open item "Make the FP
// values data-dependent" in docs/NEXT.md, and walking the shifter here
// would only lengthen the hold without them.
//
// ---------------------------------------------------------------------
// WHAT IS SOURCED, AND IT IS THE RATE
// ---------------------------------------------------------------------
// Two sources, and they agree:
//
//   * Buchholz (ed.), "Planning a Computer System", §14.4, text layer of
//     docs/Planning_A_Computer_System.pdf.  Printed p.208 (PDF 233):
//     "Operations on the floating-point fraction and also variable-
//     field-length binary multiply and divide operations are performed
//     by the PARALLEL unit."  Printed p.210 (PDF 235): "To expedite the
//     execution of the multiply instructions, 12 BITS OF THE MULTIPLIER
//     ARE HANDLED IN ONE CYCLE. ... The action is from right to left".
//     Printed p.211 (PDF 236): the multiples are summed in carry-save
//     adders "and, DURING THE LAST CYCLE, into the carry propagate adder
//     ... THE FOUR CYCLES when multiplicand multiples are added".
//   * Performance Characteristics Vol. 1, Table 2 (printed p.3-3, PDF
//     21, text layer): "*(Multiply)  5 cycles [pre-execution]  4 cycles
//     (norm. <= 6) [execution]", and the same for D*.
//
// So a 48-bit multiplier is FOUR cycles of twelve bits: request at T,
// the four passes at T+1 .. T+4, the answer readable at T+4 (mkVflBox's
// CReg note says why).  The fourth pass also does the post-
// normalization of up to six places, which Table 2 includes in the four
// execution cycles; a longer normalization ("2 cycles for each
// additional norm. of 6") is NOT walked by the box -- the instruction's
// time is still eboxClocks' minimum (StretchTiming.bsv), as before.
//
// THE MULTIPLIER IS THE FIRST ARGUMENT (`a`).  For `*+` that is Ref.
// Manual printed p.98's "the operand specified by the effective address,
// designated as the multiplier" (fpArithClass asks with `a: opnd, b:
// ftv`).  For `*` and `D*` the arm passes the accumulator first; which
// operand feeds the twelve-bit groups cannot be observed outside the box
// (the product is the same number), so nothing depends on it.
//
// THE SAME MULTIPLIER AS mkVflBox, ON THE REAL MACHINE.  p.208 puts the
// VFL binary multiply in the same parallel unit.  The model keeps two
// boxes (this one and mkVflBox) because each was moved out of a
// different function; merging them is open, in docs/NEXT.md.
//
// WHAT IS NOT MODELLED, said once (as in mkVflBox): the 7030's 3-bit
// recoding and carry-save partial product.  The box adds the exact
// 48 x 12 partial product each pass in ordinary binary.
//
// ---------------------------------------------------------------------
// TIME
// ---------------------------------------------------------------------
// The instruction's time is still eboxClocks' (`*` and `D*` 9, `*+` 20,
// the add class 5).  As for every box, mkEBox takes the box's clocks off that budget
// (StretchCore's rl_exec_resume).  What the HOLD costs -- the held look-
// ahead level, and the resume clock taking rl_prepare's slot -- is
// measured in microarchitecture_plan.md §1c step 5f and bsv/README.md.
//
// THE LEVEL IS RELEASED WHEN THIS BOX ANSWERS (2026-11-19, confined
// 2026-11-20, and in the hold clocks again since 2026-11-23).  In the clock the box has answered for a look-ahead level,
// the resume yields once to the instruction unit, which may start ONE I-box
// instruction beside the held level (StretchCore's yieldToPrepare note;
// mkEBox start()'s "beside" refusal).  So the one-clock add costs the
// instruction unit nothing it did not cost inline
// (decks/fp_mplus_ds_not_df.strap's 981 pin held; since the interruption
// recovery, 2026-11-20, it is 1056, and 981 with the recovery's window
// injected off -- the release itself is unchanged).  Until 2026-11-23 NOT
// during the hold clocks: an instruction started there commits before the level's
// indicators are set, and the 7030 undoes such advance on an interruption
// (Perf. Char. Vol. 1 printed p.3-24; Buchholz §15.6; Ref. Manual p.48),
// which the model could not until 2026-11-20 (StretchCore rl_int_recover;
// and a store made there waits in a store level, the deferIboxStores
// note).  SINCE 2026-11-23 the hold clocks are open too (StretchCore
// liftHoldClocks; decks/fp_box_hold_store.strap).  Where a box-held
// multiply's interruption lands is pinned by
// decks/fp_box_interrupt_landing.strap.  The
// interlock is unchanged: the level stays in the look-ahead until the
// resume retires it, so iboxHazard holds back an instruction that reads or
// writes what it writes (decks/fp_box_release_interlock.strap).
// The divider, the decimal adder and the VFL multiplier release their
// level the same way since 2026-11-23 (StretchCore boxReleases, plan §1c 5f
// stage 3).
//
// NOT YET IN THE BOX: MULTIPLY AND ADD's sum (`*+`: its product comes
// from here, its fpAddDouble still runs in the arm, because a re-run
// that asked the box a second time would get the multiply's answer
// back -- mkEBox's "good for one run only"; it needs a chained request),
// COMPARE (fpCompare, the same subtraction with the result discarded),
// and the square root.
// ---------------------------------------------------------------------
// =====================================================================
// THE DIVIDE CLASS (mkDivBox's header, 2026-11-15 .. 2026-11-17)
// =====================================================================
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
// >>> SUPERSEDED 2026-11-17: the rule IS in the sources, in Buchholz,
// "Planning a Computer System", Figs. 14.11-14.12 (printed pp.214-215,
// PDF 239-240).  mkDivBox now walks it for the floating-point divide's
// time -- see "THE 7030'S REDUCTION LOOP" below.  mkFpDivBox, this
// standalone sketch, still uses its fixed 6 and is not the core's box. <<<
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
package StretchPAU;

import Vector::*;
import StretchTypes::*;
import StretchFP::*;

// =====================================================================
// THE FLOATING-POINT CLASS: its requests, its adder, its answers
// =====================================================================
// >>> SOURCED: Buchholz printed p.210, "12 bits of the multiplier are
// handled in one cycle"; Table 2's four execution cycles. <<<  A width,
// so a typedef; it must divide 48 (elaboration refuses one that does not).
typedef 12 FpMulGroup;
Integer fpMulBitsPerCycle = valueOf(FpMulGroup);
Integer fpMulBits         = 48;

// THE MULTIPLY REQUEST: the two operands as fpMul takes them, already
// sign-modified by the caller, and the two mode bits.  `dbl` selects
// MULTIPLY DOUBLE's whole 96-bit result (fpMulDoubleProd) over
// MULTIPLY's high half (fpMulProd).
typedef struct {
  FpNum a;          // the multiplier (see the header)
  FpNum b;          // the multiplicand
  Bool  normalized;
  Bool  noisy;
  Bool  dbl;
} FpMulReq deriving (Bits, Eq, FShow);

// THE ADD REQUEST: what the preparation hands on (StretchFP.bsv's
// FpAddDp, the datapath's inputs, and FpAddCtx, what the finish needs),
// and which result shape: `dbl` for ADD DOUBLE and ADD TO FRACTION.
typedef struct {
  FpAddDp  dp;
  FpAddCtx ctx;
  Bool     dbl;
} FpAddReq deriving (Bits, Eq, FShow);

// MULTIPLY AND ADD (`*+`) AS ONE CHAINED REQUEST (A4 step 3, 2026-11-26):
// the multiply as FpMul's (MULTIPLY DOUBLE's, unnormalized: p.99), then,
// in the unit, ADD DOUBLE of the accumulator and the product -- the
// preparation (fpAddDoublePrep), and on the datapath path one add pass.
// R23-9732 Fig. 3.8.13 (PDF 237, printed 8-13/8-14) draws exactly that
// sequence in the parallel unit: the multiply ring (MR1, MR2, MC) and then
// the add's pre-shift and normalize (T2, T3, END OPN), with no hand-back
// between them.  `acc` is the accumulator as ADD DOUBLE takes it.
typedef struct {
  FpMulReq mul;
  FpDouble acc;
  Bool     normalized;
  Bool     noisy;
} FpMulAddReq deriving (Bits, Eq, FShow);

typedef union tagged {
  FpMulReq    FpMul;
  FpAddReq    FpAdd;
  FpMulAddReq FpMulAdd;
} FpReq deriving (Bits, Eq, FShow);

// >>> THE STEPPING SWITCHES (fidelity_plan.md A4 step 3). <<<
// pauChainMulAdd: `*+`'s sum is the unit's (one FpMulAdd request) rather
// than the E-box arm's fpAddDouble.  The answer is the same either way
// (mkPauFpTb's m-vectors check it); the unit spends ONE MORE CLOCK, the add
// pass, so the hold is 5 clocks, not 4.
Bool pauChainMulAdd = True;
// The time terms of `*+`'s add, charged on top of eboxClocks' 20 through
// mkEBox.boxCharge (the divide's fpExtra route).  Perf. Char. Vol. 1 Table 2,
// printed p.3-4 (PDF 22), the *+ row's execution column: "17 cycles (pre
// shift <= 3 and norm <= 6) / 1 cycle for each additional pre-shift of 4 /
// 2 cycles for each additional norm. of 6 / 2 cycles if recomplement is
// necessary - note 1".
Bool pauMaPreshift = True;
Bool pauMaNorm     = True;
Bool pauMaRecomp   = True;
// R23-9732 Fig. 3.8.13's alternative path: "IF ACCUMULATOR EXPONENT IS
// SMALLER USE THIS TIMING", END OPN at period 13 against the main path's
// 10 -- three periods.  Table 2 has no such term.  OFF (2026-11-26): the
// alternative path is the route by which the ACCUMULATOR, not the product,
// goes through the pre-shifter, and Table 2's pre-shift term already
// charges that shift, so both would count it twice; and the chart's periods
// are not Table 2's cycles.  The atlas sees the switch only on PDF 88's
// `int` columns of NEG *+ (a CHOSEN internal operand), where it moves the
// row away: 65 -> 68 clocks against the printed 56 (fidelity_plan.md A4).
Bool pauMaAccSmaller = False;
// The same three terms on the PLAIN add class (+, +MG, M+, M+MG, D+, D+MG,
// F+, the add requests mkEBox makes).  Table 2, printed p.3-3 (PDF 21), the
// add row: "4 cycles (pre shift <= 3) / 1 cycle for each additional
// pre-shift of 4" pre-execution and "1 cycle (norm <= 6) / 2 cycles for
// each additional norm. of 6 / 2 cycles if recomplement / 2 cycles if forced
// zero" execution.  Each term follows its pauMa switch above; this switch
// turns the plain add's charge on or off as a whole.  OFF (2026-11-26):
// measured on the FP atlas it helps D+, + and the totals (76.8% -> 77.3%
// within 1, 94.6% -> 95.1% within 3 over the `*+` step) but moves 274
// cells away, mostly M+ / M+MG, which already run long (+0.78 median) for a
// reason outside this unit, and +MG's NEG rows, by the forced zero
// (fidelity_plan.md A4).  It waits for the M+ store path.
Bool pauAddStep = False;
// Table 2's "2 cycles if forced zero": the forced zero of ADD TO MAGNITUDE
// (Ref. Manual p.83; FpAddSum.forcedZero).  Only +MG, M+MG and D+MG can
// reach it, so it never moves `*+`.
Bool pauAddForcedZero = True;

// Table 2's add-class terms for one add pass: the pre-shift loop's
// repeats (the shifter moves four places right at a time, Buchholz printed
// p.210), the normalization's (six left at a time, two cycles each), and
// the recomplement.
function Bit#(16) pauAddTerms(FpAddDp d, FpAddSum s, Bool recomp);
  Bit#(16) sh = zeroExtend(pack(d.shift));
  Bit#(16) ps = (sh > 3) ? (sh - 3 + 3) / 4 : 0;
  Bit#(16) nl = (s.adj < 0) ? zeroExtend(pack(-s.adj)) : 0;
  Bit#(16) nm = (nl > 6) ? 2 * ((nl - 6 + 5) / 6) : 0;
  return (pauMaPreshift ? ps : 0) + (pauMaNorm ? nm : 0)
       + ((pauMaRecomp && recomp) ? 2 : 0)
       + ((pauAddForcedZero && s.forcedZero) ? 2 : 0);
endfunction

// THE BOX'S ADDER (see the header): 1s complement with end-around carry
// on the pre-shifted operand, then the forced-zero rule and the
// normalization exactly as fpAddSumRef applies them.
function Tuple2#(FpAddSum, Bool) fpBoxAddSumR(FpAddDp d);
  // The alignment: the smaller-exponent fraction moves right.
  Bit#(96) fsh = d.fs >> d.shift;
  Bool     sub = (d.bigSign != d.smlSign);
  Bit#(97) t   = zeroExtend(d.fb) + zeroExtend(sub ? ~fsh : fsh);
  Bit#(97) sum;
  Bit#(1)  sign;
  // Whether this add recomplemented (Table 2 note 1).
  Bool     recomp = sub && t[96] == 0;
  if (!sub) begin
    sum = t; sign = d.bigSign;
  end else if (t[96] == 1) begin
    // The end-around carry: fb was the larger, and fb - fsh is t + 1
    // with the carry dropped.
    sum = zeroExtend(t[95:0] + 1); sign = d.bigSign;
  end else begin
    // No carry: the complemented, pre-shifted fraction was the larger
    // (or they were equal), so the result is RECOMPLEMENTED into
    // absolute-value form and takes that operand's sign.
    sum = zeroExtend(~t[95:0]); sign = d.smlSign;
  end
  // An exact cancellation's sign (p.82): fpAddSumRef's tie rule.
  if (sub && sum == 0) sign = d.tieSign;
  Bool forcedZero = False;
  if (d.magTest && sum != 0 && sign != d.okSign) begin
    forcedZero = True; sum = 0; sign = d.okSign;
  end
  let {f96, adj, lostCarry} = fpNormalize96Wide(sum[96], sum[95:0], d.normalized, d.noisy);
  return tuple2(FpAddSum { frac: f96, adj: adj, lc: lostCarry, zero: (sum == 0),
                           sign: sign, forcedZero: forcedZero }, recomp);
endfunction

function FpAddSum fpBoxAddSum(FpAddDp d) = tpl_1(fpBoxAddSumR(d));

// The answer: MULTIPLY's FpResult or MULTIPLY DOUBLE's FpdResult, tagged
// by which was asked.
typedef union tagged {
  FpResult  FpRspSingle;
  FpdResult FpRspDouble;
} FpRsp deriving (Bits, Eq, FShow);

function FpResult fpRspSingle(FpRsp r);
  if (r matches tagged FpRspSingle .s) return s;
  else return unpack(0);
endfunction

function FpdResult fpRspDouble(FpRsp r);
  if (r matches tagged FpRspDouble .d) return d;
  else return unpack(0);
endfunction

// =====================================================================
// THE DIVIDE CLASS: its constants, its step, its requests, its walk
// =====================================================================
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
// the box.  The two constant rows are something else; they are not
// explained, but a measurement (below) shows they come from the same
// I-box/E-box interleave.  Re-measured on batch3 (the look-ahead
// carry work) at 4 box clocks: every number above is unchanged.
// >>> WHY "PARK THE DIVIDE AND LET THE I-BOX RUN" DOES NOT GET THE
// OLD CLOCKS BACK, MEASURED 2026-11-16. <<<  A version that retired
// the level at once and wrote the results when the box answered
// gave the old clocks on the decks with no early consumer: f217a 475
// and f217c 180, so those residues go with the hold.  But six decks
// failed their own checks (f217b, f217d, f217wb, f217xb, f217xd,
// fp_zm_cleared): the I-box read the result before it was written.
// Traced on F217B, with clocks counted from reset: the divide's
// operand arrives at clock 56, and the `BB $SB` that tests the
// quotient's sign runs at clock 57 in BOTH runs.  The old combinational
// divide wrote the quotient at 56, but a 4-clock box answers at 60.  The
// old halt clocks therefore depend on the quotient being there one clock
// after the operand.  No multi-clock box gives that, parked or held,
// unless the I-box is made to wait for it (an iboxHazard term), and
// that wait is the slowdown above.  Getting the overlap back needs the
// I-box to run during a box wait, which is rl_prepare's business.
// [The halt-clock table above is from the 4-clock box.  Since
// 2026-11-17 an FP divide holds the box for its walk, 8-24 clocks on
// the test vectors, and is charged Table 2's time, so those figures are
// STALE for the FP decks; they were not re-measured.]
// Making the box's own
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
// against Table 2 as unresolved.  [RE-READ AT THE INK 2026-11-17 for
// "THE 7030'S REDUCTION LOOP": two numbered pulses per reduction cycle,
// and sheet 3's note 2 makes one pulse 300 ns, i.e. one clock -- so
// Table 2's "2 cycles for each additional reduction loop" is the chart's
// two pulses.]  THAT REPORT WAS NOT RE-READ AT THE
// INK FOR THIS CHANGE and is recorded as a pointer for the timing
// step, not as a finding: read the three figures before building on
// it.  Nothing in mkDivBox depends on it.
// ---------------------------------------------------------------------
typedef struct {
  Bit#(96) dvd;
  Bit#(48) dvs;
  // A FLOATING-POINT divide's Table-2 fixed terms (fpDivFixedClocks,
  // StretchFP.bsv), never 0 for one; 0 means "not a floating-point
  // divide" -- the VFL divide -- and no reduction walk is run, so the
  // VFL divide's clocks are exactly what they were.
  Bit#(8)  fpFixed;
  Bool     fpDbl;  // D/: Table 2 adds the remainder normalization
} DivReq deriving (Bits, Eq, FShow);

typedef struct {
  Bit#(96) q;      // all 96 quotient bits
  Bit#(48) rem;    // the remainder, which is below the divisor
  // A floating-point divide's time over eboxClocks' zero-divisor floor
  // of 5 (see THE 7030'S REDUCTION LOOP below); 0 for the VFL divide.
  Bit#(16) fpExtra;
} DivRsp deriving (Bits, Eq, FShow);

// ---------------------------------------------------------------------
// >>> THE 7030'S REDUCTION LOOP, WALKED FOR ITS LENGTH (2026-11-17). <<<
//
// THE PROBLEM IT CLOSES.  eboxClocks charged FP `/` 4 clocks, Table 2's
// minimum "before the data-dependent reduction loops", and the atlas
// (Perf. Char. Vol. 2 PDF 54-56, 85-87, a normalized 1 divided by a
// normalized 1) measured /, D/ and R/ 16-21 clocks LONGER than the
// model (docs/atlas_oracle.md).  The missing clocks are the loops.
//
// WHAT IS SOURCED.
//  * Perf. Char. Vol. 1 Table 2, printed p.3-5 (PDF 23), the / row:
//    "2 cycles for initial reduction loop if dividend is normalized",
//    "2 cycles for each additional reduction loop (number of cycles is
//    data dependent)", "2 cycles if final remainder has to be
//    complemented", and "If zero divisor 3 cycles pre-execution and 2
//    cycles execution instead of previous".  D/ (same page): "Same as
//    Divide plus 6 cycles (remainder norm <= 6) 2 cycles for each
//    additional remainder norm. of 6".  R/ (printed p.3-4, PDF 22): "2
//    cycles" + "2 cycles plus all pre-execution and execution cycles of
//    Divide".  The fixed terms are fpDivFixedClocks (StretchFP.bsv).
//  * THE ALGORITHM, Buchholz (ed.), "Planning a Computer System",
//    printed pp.213-216 (PDF 238-241), read at the page image: one of
//    three divisor multiples, 1, 3/4 and 3/2, chosen per add cycle from
//    "3 high-order bits of the normalized previous remainder and 5
//    high-order bits of the normalized divisor" by Fig. 14.11 (p.214);
//    the new remainder is normalized, the shifts out are the quotient
//    bits (Fig. 14.12, p.215); "As many as six shifts can be carried
//    out in the same cycle as one addition; if more shifts are needed,
//    extra cycles are used without addition" (p.216).  Fig. 14.11 as
//    read (r = the remainder's top three bits in true form, d = the
//    divisor's top five):
//        r = 100: 3/4 if d >= 10101, else 1
//        r = 101: 3/4 if d >= 11001, 3/2 if d <= 10001, else 1
//        r = 110: 3/4 if d >= 11110, 3/2 if d <= 10100, else 1
//        r = 111: 3/2 if d <= 10111, else 1
//    A Python prototype of exactly this walk (exact fractions, 4,000
//    random normalized pairs) develops the right quotient on every
//    pair, never shifts fewer than two places after an add (p.216:
//    "The scheme always permits at least two shifts after each add
//    cycle" -- a check on the reading of Fig. 14.11), and averages
//    3.4 quotient bits per add-and-shift cycle against p.215's "On the
//    average, 3.5 quotient bits are generated each cycle".
//  * THE CYCLE STRUCTURE, R23-9732 figure 3.8.15 sheet 2 (PDF 240,
//    printed 8-17/8-18): a Trial Reduction Cycle, then Intermediate
//    Reduction Cycles each two clock periods long, "Any one or more of
//    these intermediate reduction cycles could be a dummy cycle. That
//    is if more than 6 quotient bits were developed on the previous
//    reduction cycle this would be just a shift cycle", and a Last
//    Reduction Cycle entered on "Ctr = 0"; the second divide cycle
//    (SDC) gates "47" into the shift counter when the trial result is
//    true and "48" when it is complement, and every cycle "Subtract[s]
//    Shift Amount from Counter Register".  Then "Add Back 1x Divisor"
//    -- "done if the last reduction cycle caused the result to be
//    complement" -- which is Table 2's +2.  (Sheet 3, PDF 241, note 2:
//    a shortened termination "shortens the operation by 300
//    nanoseconds", so one numbered pulse is one 0.3 us clock.)
//
// >>> RECONSTRUCTION, AND WHAT DECIDED IT. <<<  Whether the SDC is a
// reduction loop of its own or shifts in the same cycle is not
// printed.  Counted as its own additional loop, a normalized 1 divided
// by a normalized 1 (trial remainder zero, so every later cycle is a
// six-place dummy: 47 = 6+6+6+6+6+6+6+5, eight cycles) takes
// 2 + 2 + 2 + 2*(1 + 8) + 1 = 25 clocks, and the atlas prints exactly
// 25 for it (7.50 us, PDF 54) -- the same Table-2-sum calibration the
// atlas shows on * (2.70 us = 5 + 4) and D* (3.00 us = 5 + 4 + "1
// cycle if immediate next instruction is floating point").  Not
// counted, 23.  The prototype's mean over random operands with the SDC
// counted is 38 clocks, 11.4 us, against PDF 41's "The average divide
// time should be about 10 us" (10.8 us without it).  The SDC is
// counted; the alternative is recorded here and in NEXT.md.  Note
// that 1/1 is the FASTEST possible divide under this law (every cycle
// shifts the full six), which is what PDF 41 means by "do not give a
// realistic timing".
// Also RECONSTRUCTION: the remainder's magnitude is taken in true
// (two's-complement) form, where the 7030 normalizes a ones'
// complement; the dividend bits below the 48-bit window enter as the
// remainder shifts; D/ uses DIVIDE's counter (47/48) for its 49-bit
// quotient; a ZERO remainder costs D/ only the base 6 (no sheet shows
// a zero remainder being normalized).
//
// THE ANSWER IS NOT AFFECTED: the quotient and remainder are still the
// restoring steps above.  The walk is the loop's LENGTH only, run one
// 7030 reduction cycle per box clock beside the restoring steps; the
// box answers when both are done.
// ---------------------------------------------------------------------
function Bit#(8) divPer6(Bit#(8) sh) =
  (sh <= 6) ? 0 : 2 * ((sh - 6 + 5) / 6);

// Fig. 14.11.  r3 = 3'b1xx, the normalized remainder's top three bits
// in true form; d5 = the normalized divisor's top five.  0 = 1x,
// 1 = 3/4, 2 = 3/2.
function Bit#(2) divMultiple(Bit#(3) r3, Bit#(5) d5);
  Bit#(2) m = 0;
  case (r3)
    3'b100: m = (d5 >= 5'b10101) ? 1 : 0;
    3'b101: m = (d5 >= 5'b11001) ? 1 : ((d5 <= 5'b10001) ? 2 : 0);
    3'b110: m = (d5 >= 5'b11110) ? 1 : ((d5 <= 5'b10100) ? 2 : 0);
    default: m = (d5 <= 5'b10111) ? 2 : 0;
  endcase
  return m;
endfunction

// >>> INVENTED, to fit the old 4-clock budget of FP `/`.  See above.
// Since 2026-11-17 the FP divide's TIME no longer depends on this: it
// is Table 2 plus the walked reduction loop (fpExtra). <<<
Integer coreDivBitsPerCycle = 24;

// =====================================================================
// mkPAU
// =====================================================================
// THE REQUEST: the floating-point box's (FpReq: multiply or add) or the
// divider's (DivReq: FP or VFL divide).  mkEBox's BoxReq already names
// which; BoxFp and BoxDiv both land here.
typedef union tagged {
  FpReq  PauFp;
  DivReq PauDiv;
} PauReq deriving (Bits, Eq, FShow);

// THE ANSWER, tagged by the class that was asked.
typedef union tagged {
  FpRsp  PauRspFp;
  DivRsp PauRspDiv;
} PauRsp deriving (Bits, Eq, FShow);

// The caller's views, as mkSAU's sauDecRsp: the caller knows which class
// it asked (mkEBox's boxKind), and a view of the other class is zero.
function FpRsp pauFpRsp(PauRsp r);
  if (r matches tagged PauRspFp .f) return f;
  else return unpack(0);
endfunction

function DivRsp pauDivRsp(PauRsp r);
  if (r matches tagged PauRspDiv .d) return d;
  else return unpack(0);
endfunction

interface PAU;
  method Action request(PauReq r);
  method Bool responseReady();
  method Bit#(16) fpExtra();
  // A VALUE, NOT AN ActionValue: taking the answer changes nothing in
  // the unit.  The caller knows whether it is waiting (mkEBox's
  // `boxWait`), so the unit needs no "idle again" state, and `request`
  // is then the ONLY method that writes the unit's state -- which is
  // what lets one caller rule poll, take and re-request in one clock.
  // (mkDivBox's note.  The first divider guarded its response on its
  // done state, and bsc -- which does not push a method's condition
  // inside the `if` that calls it -- made that the condition of the WHOLE
  // of mkEBox.resume(): no instruction could resume from an operand read
  // unless the divider happened to hold a result.)
  method PauRsp response();
endinterface

typedef enum { PauIdle, PauMulPass, PauAddPass, PauDivReduce, PauDone }
  PauState deriving (Bits, Eq, FShow);

(* synthesize *)
module mkPAU(PAU);
  // >>> CREGS, AND THE PORT ASSIGNMENT IS THE SCHEDULE (mkDivBox's). <<<
  // The rules read and write port 0; every method reads and writes port
  // 1.  So the rules are ordered BEFORE all of the methods, and no rule of
  // this module falls between two of them.  With plain Regs the divider's
  // first build failed with bsc's G0096 ("requires dynamic scheduling,
  // which is not supported by Bluesim"): mkEBox.resume polls responseReady
  // (which must read the state before a rule writes it) and may call
  // request (which writes what a rule reads, so must come after it) -- a
  // rule between two method calls of one caller rule, across a synthesis
  // boundary.
  //
  // THE CONSEQUENCE FOR TIME: a method sees the rule's update in the same
  // clock, so the answer is readable in the clock of the last pass, not
  // the one after.  Request at clock T, passes at T+1 .. T+n, the answer
  // taken at T+n.
  Reg#(PauState)  rg_state[2] <- mkCReg(2, PauIdle);
  // Which class the answer is (response()'s view).  Written only by
  // request, read only by response: rg_dvs's discipline in mkDivBox.
  Reg#(Bool)      rg_isDiv    <- mkReg(False);
  // THE AB FRACTION (see the header): product register / dividend-and-
  // quotient register.
  Reg#(Bit#(96))  rg_ab[2]    <- mkCReg(2, 0);
  // THE C FRACTION: the multiplicand / the divisor.  Written only by
  // request, read only by the rules: rule before method, which is the
  // order the CRegs already impose.
  Reg#(Bit#(48))  rg_cd       <- mkReg(0);
  // Passes still to do: multiply passes, or divide reduction clocks.  It
  // counts CLOCKS, not steps, and every divide clock does exactly
  // coreDivBitsPerCycle steps: guarding each step on a step counter (as
  // mkFpDivBox does, where the rate need not divide 96) put a wide select
  // behind every step (measured at 32 a clock: 9,325 LUT4 with the
  // guard, 4,284 without).  So the rate MUST divide 96, and elaboration
  // refuses one that does not.
  Reg#(Bit#(8))   rg_ctr[2]   <- mkCReg(2, 0);

  // The floating-point class's own: the multiply's request (its exponents,
  // signs, flags and modes, for fpMulProd), the add's request, the answer.
  Reg#(FpMulReq)  rg_mul[2]   <- mkCReg(2, unpack(0));
  Reg#(FpAddReq)  rg_add[2]   <- mkCReg(2, unpack(0));
  Reg#(FpRsp)     rg_rsp[2]   <- mkCReg(2, unpack(0));
  // `*+` (FpMulAdd): the accumulator and the add's modes, written by
  // request and read by rl_mul; whether the add pass charges Table 2's
  // terms; and the time over eboxClocks' 20 (fpExtra).
  Reg#(Bool)      rg_chain    <- mkReg(False);
  Reg#(FpDouble)  rg_acc      <- mkReg(unpack(0));
  Reg#(Bool)      rg_maNorm   <- mkReg(False);
  Reg#(Bool)      rg_maNoisy  <- mkReg(False);
  Reg#(Bool)      rg_terms[2] <- mkCReg(2, False);
  Reg#(Bit#(16))  rg_fpX[2]   <- mkCReg(2, 0);

  // The divide's own: the partial remainder.
  Reg#(Bit#(49))  rg_rem[2]   <- mkCReg(2, 0);

  // THE WALK (see THE 7030'S REDUCTION LOOP above).  Fixed point with
  // 50 fraction bits: the divisor is vf << 2, so 3/4 and 3/2 of it are
  // exact.  rg_wAdd counts Table 2's "additional reduction loops".
  Reg#(Bool)      rg_wBusy[2] <- mkCReg(2, False);
  Reg#(Int#(56))  rg_wR[2]    <- mkCReg(2, 0);
  Reg#(Bit#(48))  rg_wDl[2]   <- mkCReg(2, 0);
  Reg#(Bit#(6))   rg_wCtr[2]  <- mkCReg(2, 0);
  Reg#(Bit#(8))   rg_wAdd[2]  <- mkCReg(2, 0);
  Reg#(Int#(56))  rg_wD4      <- mkReg(0);
  Reg#(Bit#(8))   rg_wFixed   <- mkReg(0);
  Reg#(Bool)      rg_wDbl     <- mkReg(False);

  Integer passes = fpMulBits / fpMulBitsPerCycle;
  if (passes * fpMulBitsPerCycle != fpMulBits)
    error("mkPAU: FpMulGroup must divide 48");
  Integer coreDivClocks = divTotalBits / coreDivBitsPerCycle;
  if (coreDivClocks * coreDivBitsPerCycle != divTotalBits)
    error("mkPAU: coreDivBitsPerCycle must divide 96");

  // THE MULTIPLY, ONE PASS: the low twelve multiplier bits times the
  // multiplicand, added into the high half, the register shifted right
  // twelve.  On the last pass the product is complete and the result is
  // formed from it.
  rule rl_mul (rg_state[0] == PauMulPass);
    FpMulReq m = rg_mul[0];
    Bit#(48)          hi = rg_ab[0][95:48];
    Bit#(48)          lo = rg_ab[0][47:0];
    Bit#(FpMulGroup)  g  = truncate(lo);
    Bit#(TAdd#(48, FpMulGroup)) pp =
      pack(unsignedMul(UInt#(48)'(unpack(rg_cd)), UInt#(FpMulGroup)'(unpack(g))));
    Bit#(TAdd#(TAdd#(48, FpMulGroup), 1)) s = zeroExtend(hi) + zeroExtend(pp);
    // The partial product never exceeds 96 bits (mkVflBox's note), so
    // the truncation drops only zeros.
    Bit#(96) np = truncate({s, lo} >> fpMulBitsPerCycle);
    rg_ab[0]  <= np;
    rg_ctr[0] <= rg_ctr[0] - 1;
    if (rg_ctr[0] == 1 && rg_chain) begin
      // `*+`: the product, then ADD DOUBLE's preparation against the
      // accumulator.  Flagged operands and a difference over 95 are
      // answered here; anything else takes the add pass.
      FpdResult  pr = fpMulDoubleProd(m.a, m.b, m.normalized, m.noisy, np);
      FpdAddPrep p  = fpAddDoublePrep(rg_acc, pr.res, rg_maNorm, rg_maNoisy, False);
      if (p.viaDp) begin
        rg_add[0]   <= FpAddReq { dp: p.dp, ctx: p.ctx, dbl: True };
        rg_terms[0] <= True;
        Bool accSmaller = fpExp(fpdHead(rg_acc)) < fpExp(fpdHead(pr.res));
        rg_fpX[0]   <= (pauMaAccSmaller && accSmaller) ? 3 : 0;
        rg_state[0] <= PauAddPass;
      end else begin
        rg_rsp[0]   <= tagged FpRspDouble p.early;
        rg_state[0] <= PauDone;
      end
    end else if (rg_ctr[0] == 1) begin
      rg_rsp[0] <= m.dbl
        ? tagged FpRspDouble fpMulDoubleProd(m.a, m.b, m.normalized, m.noisy, np)
        : tagged FpRspSingle fpMulProd(m.a, m.b, m.normalized, m.noisy, np);
      rg_state[0] <= PauDone;
    end
  endrule

  // THE ADD: one pass, Table 2's one execution cycle (mkFpBox's header).
  rule rl_add (rg_state[0] == PauAddPass);
    FpAddReq q = rg_add[0];
    match {.sm, .rc} = fpBoxAddSumR(q.dp);
    if (rg_terms[0]) rg_fpX[0] <= rg_fpX[0] + pauAddTerms(q.dp, sm, rc);
    rg_rsp[0] <= q.dbl ? tagged FpRspDouble fpAddDoubleFinish(q.ctx, sm)
                       : tagged FpRspSingle fpAddFinish(q.ctx, sm);
    rg_state[0] <= PauDone;
  endrule

  // THE DIVIDE'S LENGTH: one 7030 reduction cycle a clock (THE 7030'S
  // REDUCTION LOOP above), beside the restoring steps.
  rule rl_walk (rg_wBusy[0]);
    Int#(56) r = rg_wR[0];
    Bit#(56) mag = pack((r < 0) ? -r : r);
    // Places to shift until |r| >= 1/2 (bit 49): a zero remainder never
    // gets there and is shifted six a cycle until the counter runs out.
    UInt#(6) czm = countZerosMSB(mag);
    Bit#(6) lead = (czm >= 6) ? (pack(czm) - 6) : 0;
    Bit#(6) ctr = rg_wCtr[0];
    Bit#(6) sh = (lead < 6) ? lead : 6;
    if (ctr < sh) sh = ctr;
    Bit#(48) dl = rg_wDl[0];
    // The dividend's next `sh` bits enter at the remainder's low end.
    Bit#(48) inb = (sh == 0) ? 0 : (dl >> (6'd48 - sh));
    r = (r << sh) + unpack(zeroExtend(inb) << 2);
    dl = dl << sh;
    ctr = ctr - sh;
    if (ctr != 0 && sh == lead) begin
      Bit#(56) m2 = pack((r < 0) ? -r : r);
      Bit#(3) r3 = (m2[50] == 1) ? 3'b111 : m2[49:47];
      Bit#(5) d5 = truncate(pack(rg_wD4) >> 45);
      Int#(56) dm = case (divMultiple(r3, d5))
                      1: (rg_wD4 - (rg_wD4 >> 2));
                      2: (rg_wD4 + (rg_wD4 >> 1));
                      default: rg_wD4;
                    endcase;
      r = (r < 0) ? r + dm : r - dm;
    end
    rg_wR[0] <= r; rg_wDl[0] <= dl; rg_wCtr[0] <= ctr;
    rg_wAdd[0] <= rg_wAdd[0] + 1;
    if (ctr == 0) rg_wBusy[0] <= False;
  endrule

  // THE DIVIDE'S ANSWER: coreDivBitsPerCycle restoring steps a clock.
  rule rl_reduce (rg_state[0] == PauDivReduce);
    Bit#(49) rem = rg_rem[0];
    Bit#(96) dq  = rg_ab[0];
    for (Integer k = 0; k < coreDivBitsPerCycle; k = k + 1) begin
      match {.r2, .d2, .qb} = divRestoringStep(rem, dq, rg_cd);
      rem = r2;
      dq  = { d2[95:1], qb };
    end
    rg_rem[0] <= rem; rg_ab[0] <= dq; rg_ctr[0] <= rg_ctr[0] - 1;
    if (rg_ctr[0] == 1) rg_state[0] <= PauDone;
  endrule

  // >>> NO METHOD HAS AN IMPLICIT CONDITION, ON PURPOSE (see response). <<<
  method Action request(PauReq q);
    case (q) matches
      tagged PauFp .f: begin
        rg_isDiv    <= False;
        rg_fpX[1]   <= 0;
        // A divide abandoned mid-walk must not hold this answer back:
        // responseReady waits on the walk (see the header).
        rg_wBusy[1] <= False;
        case (f) matches
          tagged FpMul .m: begin
            rg_chain    <= False;
            rg_terms[1] <= False;
            rg_mul[1]   <= m;
            rg_ab[1]    <= zeroExtend(m.a.frac);
            rg_cd       <= m.b.frac;
            rg_ctr[1]   <= fromInteger(passes);
            rg_state[1] <= PauMulPass;
          end
          tagged FpAdd .ar: begin
            rg_chain    <= False;
            // Table 2's add-class terms on a plain add (pauAddStep).
            rg_terms[1] <= pauAddStep;
            rg_add[1]   <= ar;
            rg_state[1] <= PauAddPass;
          end
          tagged FpMulAdd .ma: begin
            rg_chain    <= True;
            rg_terms[1] <= False;
            rg_acc      <= ma.acc;
            rg_maNorm   <= ma.normalized;
            rg_maNoisy  <= ma.noisy;
            rg_mul[1]   <= ma.mul;
            rg_ab[1]    <= zeroExtend(ma.mul.a.frac);
            rg_cd       <= ma.mul.b.frac;
            rg_ctr[1]   <= fromInteger(passes);
            rg_state[1] <= PauMulPass;
          end
        endcase
      end
      tagged PauDiv .r: begin
        rg_isDiv    <= True;
        rg_ab[1]    <= r.dvd;
        rg_cd       <= r.dvs;
        rg_rem[1]   <= 0;
        rg_ctr[1]   <= fromInteger(coreDivClocks);
        rg_state[1] <= PauDivReduce;
        // The trial reduction cycle, here, as the request is taken:
        // subtract the divisor once.  The second divide cycle loads the
        // counter, 47 on a true result and 48 on a complement (fig. 3.8.15
        // sheet 2), and is itself the first additional loop -- see THE
        // 7030'S REDUCTION LOOP.
        Int#(56) d4 = unpack(zeroExtend(r.dvs) << 2);
        Int#(56) x4 = unpack(zeroExtend(r.dvd[95:48]) << 2);
        Int#(56) tr = x4 - d4;
        rg_wD4      <= d4;
        rg_wFixed   <= r.fpFixed;
        rg_wDbl     <= r.fpDbl;
        rg_wR[1]    <= tr;
        rg_wDl[1]   <= r.dvd[47:0];
        rg_wCtr[1]  <= (tr < 0) ? 48 : 47;
        rg_wAdd[1]  <= 1;
        rg_wBusy[1] <= (r.fpFixed != 0);
      end
    endcase
  endmethod

  method Bool responseReady() = (rg_state[1] == PauDone) && !rg_wBusy[1];

  // `*+`'s time over eboxClocks' 20 (0 for every other request); read
  // with the answer, as the divide's fpExtra is.
  method Bit#(16) fpExtra() = rg_fpX[1];

  method PauRsp response();
    Bit#(48) rem = rg_rem[1][47:0];
    Bit#(8) rn = 0;
    if (rg_wDbl) begin
      UInt#(6) lz = countZerosMSB(rem);
      rn = 6 + ((rem == 0) ? 0 : divPer6(zeroExtend(pack(lz))));
    end
    Bit#(16) t = zeroExtend(rg_wFixed) + 2 * zeroExtend(rg_wAdd[1])
               + ((rg_wR[1] < 0) ? 2 : 0) + zeroExtend(rn);
    DivRsp d = DivRsp { q: rg_ab[1], rem: rem,
                        fpExtra: (rg_wFixed == 0) ? 0 : t - 5 };
    return rg_isDiv ? tagged PauRspDiv d : tagged PauRspFp rg_rsp[1];
  endmethod
endmodule

// =====================================================================
// mkFpDivBox: THE STANDALONE DIVIDE SKETCH (StretchDivBox.bsv's first
// box, 2026-10), not instantiated by the core, kept with its testbench
// =====================================================================
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
// mkFpDivSketchTb (was mkDivBoxTb): mkFpDivBox's OWN TESTBENCH.  It lives here rather than in a
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
module mkFpDivSketchTb(Empty);
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
// mkPauDivTb (was mkCoreDivBoxTb, mkDivBox's own testbench; since
// 2026-11-26 it drives mkPAU with divide requests), in the same file
// for the same reason mkFpDivSketchTb (was mkDivBoxTb) is.  THREE ASSERTIONS PER VECTOR:
//
//   AGAINST THE OPERATORS.  q == dvd / dvs and rem == dvd % dvs on 96
//   bits -- the very expressions this box replaced in execute()'s VFL
//   divide arm.  They are fine in a testbench; they are what did not
//   fit in an FPGA.
//
//   AGAINST fpDivFrac.  The low 49 quotient bits and the remainder,
//   which is what the floating-point arms take.
//
//   THE CLOCK COUNT, a LITERAL 4 for a VFL request: request at clock T,
//   four reduction clocks T+1 .. T+4, and the answer is taken at T+4.
//   It used to be 4 for every request, eboxClocks' old budget for
//   floating-point `/`.  Since 2026-11-17 a FLOATING-POINT request
//   (vectors 8-11, fpFixed 7) also walks the 7030's reduction loop, one
//   loop a clock, and answers when both are done: literal clocks and a
//   literal fpExtra per vector (clocksOf, extraOf).
//
//   INJECTIONS, MEASURED 2026-11-17 (each reverted from a saved copy,
//   verified with cmp): see tests/run_tests.sh at run_divbox_test.sh.
//
// The vectors are the cases the VFL arm's manual pages name: dividend
// below divisor, both at maximum width, a remainder one below the
// divisor, a one-bit divisor, a quotient needing all 96 bits.  (A zero
// divisor is never sent: p.70's "THE DIVISION IS NOT ATTEMPTED".)
// ---------------------------------------------------------------------
typedef 13 NCoreDivVec;

(* synthesize *)
module mkPauDivTb(Empty);
  PAU            box    <- mkPAU;
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
      7: 96'h000000000000_000000000000;   // zero dividend
      // 8-11: FLOATING-POINT divides (fpFixed 7), normalized fractions
      8: 96'h800000000000_000000000000;   // 1/1, the atlas's case
      9: 96'h800000000000_000000000000;   // 1/(3/2): 1/2 by 3/4
      10: 96'hffffffffffff_000000000000;
      11: 96'haaaaaaaaaaaa_000000000000;
      // 12: D/ (fpDbl): remainder 1, 47 leading zeros, so Table 2's
      // "6 cycles (remainder norm <= 6)" + 2 * ceil(41/6) = 20.
      default: 96'h800000000000_000000000001;
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
      7: 48'h000000000003;
      8: 48'h800000000000;
      9: 48'hc00000000000;
      10: 48'h800000000001;
      11: 48'hd55555555555;
      default: 48'h800000000000;
    endcase;
  // >>> THE FP VECTORS' TIME, LITERALS (2026-11-17). <<<  fpExtra and the
  // box's clocks, from an integer mirror of rl_walk written separately in
  // Python and cross-checked against an exact-fraction prototype of
  // Buchholz Fig. 14.11/14.12.  Vector 8, 1/1: 9 additional loops, extra
  // 20, so `/` is 5 + 20 = 25 clocks, the atlas's 7.50 us (PDF 54).
  // A VFL vector (0-7) has extra 0 and the literal 4 clocks.
  function Bit#(16) extraOf(Bit#(4) i) =
    case (i) 8: 20; 9: 40; 10: 54; 11: 30; 12: 40; default: 0; endcase;
  function Bit#(16) clocksOf(Bit#(4) i) =
    case (i) 8: 8; 9: 17; 10: 24; 11: 13; 12: 8; default: 4; endcase;


  rule rl_issue (!done && !issued);
    box.request(tagged PauDiv DivReq { dvd: dvdOf(idx), dvs: dvsOf(idx),
                                       fpFixed: (idx >= 8) ? 7 : 0, fpDbl: (idx == 12) });
    issued <= True;
    t0 <= clk;
  endrule

  rule rl_collect (!done && issued && box.responseReady());
    let got = pauDivRsp(box.response());
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
    end else if (took != clocksOf(idx)) begin
      $display("FAIL coredivbox[%0d] clocks = %0d, want %0d", idx, took, clocksOf(idx));
      fails <= fails + 1;
    end else if (got.fpExtra != extraOf(idx)) begin
      $display("FAIL coredivbox[%0d] fpExtra = %0d, want %0d", idx, got.fpExtra, extraOf(idx));
      fails <= fails + 1;
    end else
      $display("PASS coredivbox[%0d] q=%h rem=%h in %0d clocks, fpExtra %0d",
               idx, got.q, got.rem, took, got.fpExtra);
    issued <= False;
    if (idx == fromInteger(valueOf(NCoreDivVec) - 1)) done <= True;
    else idx <= idx + 1;
  endrule

  // fpDivFixedClocks (StretchFP.bsv), Table 2's divide terms outside
  // the loop, against LITERALS worked from printed p.3-5 by hand:
  //   (vs, ds, zero, top)  pre + dividend + initial + 1
  //   (0, 0, F, 1)         2 + 2 + 2 + 1 =  7   the atlas's 1/1
  //   (7, 0, F, 1)         4 + 2 + 2 + 1 =  9   divisor shift 7
  //   (13, 0, F, 1)        6 + 2 + 2 + 1 = 11   divisor shift 13
  //   (0, 13, F, 1)        2 + 6 + 2 + 1 = 11   dividend shift 13
  //   (0, 0, T, 0)         2 + 3 + 3 + 1 =  9   zero dividend
  //   (0, 0, F, 0)         2 + 2 + 3 + 1 =  8   leading zeros left
  Reg#(Bool) fixedDone <- mkReg(False);
  rule rl_fixed (!fixedDone);
    Bit#(8) n = 0;
    Vector#(6, Bit#(8)) got  = newVector;
    Vector#(6, Bit#(8)) want = newVector;
    got[0] = fpDivFixedClocks(0, 0, False, 1);   want[0] = 7;
    got[1] = fpDivFixedClocks(7, 0, False, 1);   want[1] = 9;
    got[2] = fpDivFixedClocks(13, 0, False, 1);  want[2] = 11;
    got[3] = fpDivFixedClocks(0, 13, False, 1);  want[3] = 11;
    got[4] = fpDivFixedClocks(0, 0, True, 0);    want[4] = 9;
    got[5] = fpDivFixedClocks(0, 0, False, 0);   want[5] = 8;
    for (Integer k = 0; k < 6; k = k + 1)
      if (got[k] != want[k]) begin
        $display("FAIL fpDivFixedClocks case %0d = %0d, want %0d", k, got[k], want[k]);
        n = n + 1;
      end
    if (n == 0) $display("PASS fpDivFixedClocks, 6 literal cases");
    fixedDone <= True;
    fails <= fails + n;
  endrule

  rule rl_finish (done && fixedDone);
    if (fails == 0) $display("ALL TESTS PASSED");
    else $display("%0d TEST(S) FAILED", fails);
    $finish(0);
  endrule
endmodule


// ---------------------------------------------------------------------
// mkPauFpTb (was mkFpBoxTb, mkFpBox's own testbench; since 2026-11-26 it
// drives mkPAU with floating-point requests), in the same file, as the
// SAU's are in StretchSAU.bsv: the unit is testable without storage.
//
// THREE CHECKS PER VECTOR:
//   (a) the whole answer, bit for bit, against the ONE-STEP REFERENCE --
//       fpMul / fpMulDouble (StretchFP.bsv), the code the E-box ran before
//       this box, which form the product with one `*`.  The reference
//       SHARES fpMulProd / fpMulDoubleProd with the box, so this checks
//       the twelve-bit-a-pass PRODUCT and the box's WIRING (which operand
//       goes where, which result shape is returned) -- not the exponent
//       or normalization logic, which the suite's FP decks check;
//   (b) a LITERAL clock count, 4 (Table 2's four execution cycles,
//       Buchholz p.211's "four cycles");
//   (c) for vectors 1 and 2, a LITERAL fraction, worked by hand: on the
//       flagged path the fraction is the unnormalized product, and
//       (2^48 - 1)^2 = 2^96 - 2^49 + 1 = FFFFFFFFFFFE_000000000001.
//
// The vectors place multiplier (`a.frac`) bits in each twelve-bit group
// in turn, and cover both result shapes:
//   0  0.5 x 0.5, normalized              single  group 3 (bit 47)
//   1  XFP x N, all-ones fractions        single  all groups, literal frac
//   2  XFP x N, all-ones fractions        DOUBLE  all groups, literal frac
//   3  0x000000000ABC x 0x123456789ABC   single  group 0 only (bit 11 set)
//   4  0x000000FFF000 x 0x123456789ABC   single  group 1 only (bit 23 set)
//   5  0x800000000001 squared, normalized DOUBLE  groups 0 and 3
//   6  dense multiplier, noisy normalized DOUBLE  all groups
//   7  zero multiplier, normalized (ZM)   single  none
//   8  multiplier 0x000000000001 (bit 0)  single  group 0, bit 0 only
//   9  operands with DIFFERENT FLAGS (101 x 010) DOUBLE: res.flags = a.flags
//  10  XFP x XFP, different exponents    DOUBLE: Fig.32's tie to `a`
//      (9 and 10 are the two vectors an a/b swap can change; the
//      others are symmetric in everything but the multiplier's groups)
//
// INJECTIONS, OBSERVED 2026-11-19 (each in a scratch copy of this file
// built against the real StretchFP.bsv; the real file never edited):
//   A  the register shifted right ELEVEN a pass, not twelve
//      (`>> (fpMulBitsPerCycle - 1)`): vectors 0-6 and 8-10 FAIL on the
//      answer; 7 (zero multiplier) passes.  10 failed.
//   B  each group's top bit dropped (`g = truncate(lo) & 12'h7FF`):
//      0-6, 9 and 10 FAIL; 7 and 8 (no group top bit set) pass.  9 failed.
//   C  a and b swapped into fpMulProd / fpMulDoubleProd (the wiring):
//      ONLY 9 and 10 FAIL, the two vectors built for it.  2 failed.
//   D  one extra, idle pass (the counter started at five, the register
//      not written on the first): every vector's answer right, all 11
//      FAIL on "clocks = 5, want 4".
//   A was also applied to the REAL file once, to show the core reaches
//   the box: jb_af1c F214A (`*`), F214D and F216B (`*+`) each FAIL on SEN
//   and PC (the error stop, half-word 1416).  Reversed; cmp clean.
//
// THE ADD (stage 2): 17 more vectors, a0-a16, each built by the
// PREPARATION (fpAddPrep / fpAddDoublePrep) from its operands -- a vector
// the preparation answers by itself FAILS as "not a datapath vector" --
// and checked three ways: the whole answer bit for bit against fpAdd /
// fpAddDouble (the preparation, fpAddSumRef, the finish), so against a
// DIFFERENT adder from the box's (see the header); the LITERAL clock
// count 1 (Table 2's one execution cycle); and seven LITERALS, worked by
// hand, in rl_collect.  Shift amounts 0, 1, 2, 3, 4, 7, 47, 48 and 95:
//   a0  F219A1: FPK38 + (N) FPK35, noisy, shift 48 (literal aaaaaaaaaaad)
//   a1  0.75 + 0.75, shift 0, carry out, normalized right one
//   a2  shift 3, unnormalized carry out (LC)
//   a3  shift 4, unlike signs, end-around carry
//   a4  shift 1, unlike signs, RECOMPLEMENT (the shifted fraction larger)
//   a5  shift 47, unlike signs
//   a6  shift 48, unnormalized, like signs
//   a7  shift 95, noisy normalized, unlike signs (PSH)
//   a8  M+ exact cancellation, equal exponents (accIsB tie; literal)
//   a9  1/2 - (1/2 - 2^-48): a 47-place normalization (literal)
//   a10 +MG forced zero (literal);  a11 M+MG forced zero
//   a12 DOUBLE, F208D5: lost carry, 96 zero bits, LS (literal)
//   a13 DOUBLE, D+MG forced zero, shift 7
//   a14 DOUBLE, noisy, a 91-place normalization (literal)
//   a15 DOUBLE, shift 2, recomplement
//   a16 `+` exact cancellation, equal exponents (the accumulator's sign,
//       which here is NOT the shifted operand's; literal)
//
// INJECTIONS INTO THE ADD, OBSERVED 2026-11-19 (each in a scratch copy of
// this file built against the real StretchFP.bsv; the 11 multiply
// vectors pass in every one):
//   E  no end-around carry (`t[95:0]`, not `t[95:0] + 1`): a3, a9, a14
//      FAIL.  The other unlike-sign vectors with a carry (a5, a7, a13)
//      pass: by inspection, not traced, the missing unit lands below the
//      bits the result keeps.  3 failed.
//   F  no recomplement (`t[95:0]`, not `~t[95:0]`): a4, a8, a15, a16
//      FAIL.  4 failed.
//   G  the alignment one place short (`d.shift - 1` for a non-zero
//      shift): a0, a2, a3, a4, a5, a6, a12, a15 FAIL; a7 (shift 95),
//      a13 (shift 7), a10 and a11 (forced zeros, zero whatever the sum)
//      and the unshifted a1, a8, a9, a14 pass.  8 failed.
//   H  the forced-zero rule switched off: a10, a11, a13 FAIL, the three
//      forced zeros.  3 failed.
//   I  one extra, idle pass (a CReg flag that skips rl_add's first
//      clock): every answer right, all 17 add vectors FAIL on "clocks =
//      2, want 1".
//   J  the exact-cancellation sign rule removed (`if (sub && sum == 0)
//      sign = d.tieSign;`): ONLY a16 FAILS.  a8 cannot see it: on M+'s
//      tie the accumulator is the shifted operand, whose sign the
//      recomplement branch already gives.  1 failed.
//   (E-H and J were re-run with a16 in place, the same day, and gave
//   the sets above.)
//   E was also applied to the REAL file, to show the core reaches the
//   box: jb_af1c F204B (`M+` sign modifiers) FAILS on SEN and PC (the
//   error stop, half-word 1416); F205A, F206A, F208A, F208D1-D6, F212XA
//   and F219A-D pass under it.  Reversed by the inverse edit; cmp clean.
// ---------------------------------------------------------------------
typedef 11 NFpMulVec;
typedef 17 NFpAddVec;
typedef TAdd#(NFpMulVec, NFpAddVec) NFpVec;

// One add vector: the operands as fpAdd / fpAddDouble take them.
typedef struct {
  Bool     dbl;
  FpNum    a;
  FpNum    b;
  FpDouble da;
  FpDouble db;
  Bool     normalized;
  Bool     noisy;
  Bool     addMag;
  Bool     accIsB;
} FpAddVec deriving (Bits, Eq, FShow);

(* synthesize *)
module mkPauFpTb(Empty);
  PAU            box    <- mkPAU;
  Reg#(Bit#(5))  idx    <- mkReg(0);
  Reg#(Bit#(8))  fails  <- mkReg(0);
  Reg#(Bool)     issued <- mkReg(False);
  Reg#(Bool)     done   <- mkReg(False);
  Reg#(Bit#(16)) clk    <- mkReg(0);
  Reg#(Bit#(16)) t0     <- mkReg(0);

  rule rl_clk; clk <= clk + 1; endrule

  function FpNum n(Bit#(1) ef, Bit#(10) em, Bit#(1) es, Bit#(48) f, Bit#(1) sg) =
    FpNum { ef: ef, em: em, es: es, frac: f, sign: sg, flags: 3'b000 };
  function FpDouble dn(Bit#(10) em, Bit#(96) f, Bit#(1) sg) =
    FpDouble { ef: 0, em: em, es: 0, frac: f, sign: sg, flags: 3'b000 };
  FpNum    z1 = unpack(0);
  FpDouble z2 = unpack(0);
  function FpAddVec sv(FpNum a, FpNum b, Bool nrm, Bool nsy, Bool mg, Bool aib) =
    FpAddVec { dbl: False, a: a, b: b, da: z2, db: z2, normalized: nrm, noisy: nsy,
               addMag: mg, accIsB: aib };
  function FpAddVec dv(FpDouble a, FpDouble b, Bool nrm, Bool nsy, Bool mg) =
    FpAddVec { dbl: True, a: z1, b: z1, da: a, db: b, normalized: nrm, noisy: nsy,
               addMag: mg, accIsB: False };

  function FpMulReq mulOf(Bit#(5) i) =
    case (i)
      0: FpMulReq { a: n(0, 1, 0, 48'h800000000000, 0), b: n(0, 1, 0, 48'h800000000000, 0),
                    normalized: True, noisy: False, dbl: False };
      1: FpMulReq { a: n(1, 5, 0, 48'hFFFFFFFFFFFF, 1), b: n(0, 3, 0, 48'hFFFFFFFFFFFF, 0),
                    normalized: True, noisy: False, dbl: False };
      2: FpMulReq { a: n(1, 5, 0, 48'hFFFFFFFFFFFF, 1), b: n(0, 3, 0, 48'hFFFFFFFFFFFF, 0),
                    normalized: True, noisy: False, dbl: True };
      3: FpMulReq { a: n(0, 7, 1, 48'h000000000ABC, 0), b: n(0, 2, 0, 48'h123456789ABC, 1),
                    normalized: True, noisy: False, dbl: False };
      4: FpMulReq { a: n(0, 7, 0, 48'h000000FFF000, 1), b: n(0, 2, 1, 48'h123456789ABC, 1),
                    normalized: False, noisy: False, dbl: False };
      5: FpMulReq { a: n(0, 9, 0, 48'h800000000001, 0), b: n(0, 9, 1, 48'h800000000001, 0),
                    normalized: True, noisy: False, dbl: True };
      6: FpMulReq { a: n(0, 4, 1, 48'h0FEDCBA98765, 0), b: n(0, 6, 0, 48'h0FFF0FFF0FFF, 1),
                    normalized: True, noisy: True, dbl: True };
      7: FpMulReq { a: n(0, 3, 0, 48'h000000000000, 0), b: n(0, 3, 0, 48'h555555555555, 0),
                    normalized: True, noisy: False, dbl: False };
      8: FpMulReq { a: n(0, 2, 0, 48'h000000000001, 0), b: n(0, 2, 0, 48'hFFFFFFFFFFFF, 0),
                    normalized: True, noisy: True, dbl: False };
      9: FpMulReq { a: FpNum { ef: 0, em: 3, es: 0, frac: 48'hC00000000000, sign: 0, flags: 3'b101 },
                    b: FpNum { ef: 0, em: 4, es: 1, frac: 48'hA00000000000, sign: 1, flags: 3'b010 },
                    normalized: True, noisy: False, dbl: True };
      default: FpMulReq { a: n(1, 100, 0, 48'h900000000000, 0), b: n(1, 900, 0, 48'hB00000000000, 1),
                          normalized: True, noisy: False, dbl: True };
    endcase;

  // jb_af1c's FPK38 (exponent +50, fraction 555555555555) and FPK35
  // (exponent +2, fraction aaaaaaaaaaaa), decks/fp_arith_f219a.strap.
  FpNum fpk38 = fpFromWord(64'h0645555555555550);
  FpNum fpk35 = fpFromWord(64'h004AAAAAAAAAAAA0);

  function FpAddVec addOf(Bit#(5) k) =
    case (k)
      0:  sv(fpk38, fpk35, True, True, False, False);
      1:  sv(n(0, 5, 0, 48'hC00000000000, 0), n(0, 5, 0, 48'hC00000000000, 0), True, False, False, False);
      2:  sv(n(0, 8, 0, 48'hFFFFFFFFFFFF, 0), n(0, 5, 0, 48'h800000000000, 0), False, False, False, False);
      3:  sv(n(0, 9, 0, 48'h900000000000, 0), n(0, 5, 0, 48'hF00000000000, 1), True, False, False, False);
      4:  sv(n(0, 10, 0, 48'h000000000001, 0), n(0, 9, 0, 48'h800000000000, 1), True, False, False, False);
      5:  sv(n(0, 50, 0, 48'h800000000000, 1), n(0, 3, 0, 48'hFFFFFFFFFFFF, 0), True, False, False, False);
      6:  sv(n(0, 60, 0, 48'hABCDEF012345, 0), n(0, 12, 0, 48'hFFFFFFFFFFFF, 0), False, False, False, False);
      7:  sv(n(0, 100, 0, 48'h800000000000, 0), n(0, 5, 0, 48'hFFFFFFFFFFFF, 1), True, True, False, False);
      8:  sv(n(0, 4, 0, 48'h123456789ABC, 0), n(0, 4, 0, 48'h123456789ABC, 1), True, False, False, True);
      9:  sv(n(0, 6, 0, 48'h800000000000, 0), n(0, 6, 0, 48'h7FFFFFFFFFFF, 1), True, False, False, False);
      10: sv(n(0, 3, 0, 48'h800000000000, 0), n(0, 7, 0, 48'h800000000000, 1), True, False, True, False);
      11: sv(n(0, 3, 0, 48'h800000000000, 1), n(0, 7, 0, 48'h800000000000, 0), True, False, True, True);
      12: dv(dn(50, 96'hFFFFFFFFFFFF400000000000, 0), dn(3, 96'h600000000000000000000000, 0), False, False, False);
      13: dv(dn(2, 96'h800000000000000000000000, 0), dn(9, 96'h800000000000000000000000, 1), True, False, True);
      14: dv(dn(20, 96'h800000000000000000000000, 0), dn(20, 96'h7FFFFFFFFFFFFFFFFFFFFFF0, 1), True, True, False);
      15: dv(dn(5, 96'h100000000000000000000000, 0), dn(3, 96'hF00000000000000000000000, 1), True, False, False);
      default: sv(n(0, 4, 0, 48'h123456789ABC, 0), n(0, 4, 0, 48'h123456789ABC, 1), True, False, False, False);
    endcase;

  Bit#(5) nMul = fromInteger(valueOf(NFpMulVec));
  Bool    isAdd = (idx >= nMul);
  FpAddVec av   = addOf(idx - nMul);
  FpAddPrep  sp = fpAddPrep(av.a, av.b, av.normalized, av.noisy, av.addMag, av.accIsB);
  FpdAddPrep dp = fpAddDoublePrep(av.da, av.db, av.normalized, av.noisy, av.addMag);
  Bool     viaDp = av.dbl ? dp.viaDp : sp.viaDp;
  FpAddReq areq  = av.dbl ? FpAddReq { dp: dp.dp, ctx: dp.ctx, dbl: True }
                          : FpAddReq { dp: sp.dp, ctx: sp.ctx, dbl: False };
  FpRsp    aref  = av.dbl ? tagged FpRspDouble fpAddDouble(av.da, av.db, av.normalized, av.noisy, av.addMag)
                          : tagged FpRspSingle fpAdd(av.a, av.b, av.normalized, av.noisy, av.addMag, av.accIsB);

  function FpRsp mulRefOf(FpMulReq m) =
    m.dbl ? tagged FpRspDouble fpMulDouble(m.a, m.b, m.normalized, m.noisy)
          : tagged FpRspSingle fpMul(m.a, m.b, m.normalized, m.noisy);

  FpReq    req   = isAdd ? tagged FpAdd areq : tagged FpMul mulOf(idx);
  FpRsp    want  = isAdd ? aref : mulRefOf(mulOf(idx));
  Bit#(16) wantK = isAdd ? 1 : 4;

  rule rl_issue (!done && !issued);
    box.request(tagged PauFp req);
    issued <= True;
    t0 <= clk;
  endrule

  rule rl_collect (!done && issued && box.responseReady());
    FpRsp    got  = pauFpRsp(box.response());
    Bit#(16) took = clk - t0;
    Bit#(5)  k    = idx - nMul;
    Bool litOk = True;
    if (idx == 1) litOk = (fpRspSingle(got).res.frac == 48'hFFFFFFFFFFFE);
    if (idx == 2) litOk = (fpRspDouble(got).res.frac == 96'hFFFFFFFFFFFE000000000001);
    // The add's literals, worked by hand (none read off the reference):
    //   a0  F219A1's wanted answer, aaaaaaaaaaad (decks/fp_arith_f219a.strap)
    //   a8  an exact cancellation of M+ on equal exponents: zero fraction,
    //       LS on, and the ACCUMULATOR's sign, minus (p.82; here `b`)
    //   a9  1/2 - (1/2 - 2^-48): 2^-48, normalized to 800000000000
    //   a10 +MG of a negative sum: forced zero, fraction 0, LS off (p.89)
    //   a12 F208D5: the carry out of the 96 bits is lost, all 96 left are
    //       zero, LS and LC on (fpAddDouble's note)
    //   a14 a difference of 10 (hex) normalized 91 places in noisy mode:
    //       800...0 with ones in the 91 vacated places
    //   a16 a8's operands through `+` (the accumulator is `a`): zero
    //       fraction, LS on, and the accumulator's sign, PLUS (p.82)
    if (isAdd && k == 0) litOk = (fpRspSingle(got).res.frac == 48'hAAAAAAAAAAAD);
    if (isAdd && k == 8) litOk = (fpRspSingle(got).res.frac == 0 && fpRspSingle(got).ls
                                  && fpRspSingle(got).res.sign == 1);
    if (isAdd && k == 9) litOk = (fpRspSingle(got).res.frac == 48'h800000000000);
    if (isAdd && k == 10) litOk = (fpRspSingle(got).res.frac == 0 && !fpRspSingle(got).ls);
    if (isAdd && k == 12) litOk = (fpRspDouble(got).res.frac == 0 && fpRspDouble(got).ls
                                   && fpRspDouble(got).lc);
    if (isAdd && k == 14) litOk = (fpRspDouble(got).res.frac == 96'h87FFFFFFFFFFFFFFFFFFFFFF);
    if (isAdd && k == 16) litOk = (fpRspSingle(got).res.frac == 0 && fpRspSingle(got).ls
                                   && fpRspSingle(got).res.sign == 0);
    if (isAdd && !viaDp) begin
      $display("FAIL fpbox[a%0d]: the preparation answered it; not a datapath vector", k);
      fails <= fails + 1;
    end else if (pack(got) != pack(want)) begin
      if (isAdd) $display("FAIL fpbox[a%0d]: got ", k, fshow(got));
      else       $display("FAIL fpbox[%0d]: got ", idx, fshow(got));
      $display("               want ", fshow(want));
      fails <= fails + 1;
    end else if (!litOk) begin
      if (isAdd) $display("FAIL fpbox[a%0d]: literal wrong: ", k, fshow(got));
      else       $display("FAIL fpbox[%0d]: literal fraction wrong: ", idx, fshow(got));
      fails <= fails + 1;
    end else if (took != wantK) begin
      if (isAdd) $display("FAIL fpbox[a%0d] clocks = %0d, want %0d", k, took, wantK);
      else       $display("FAIL fpbox[%0d] clocks = %0d, want %0d", idx, took, wantK);
      fails <= fails + 1;
    end else begin
      if (isAdd) $display("PASS fpbox[a%0d] in %0d clocks", k, took);
      else       $display("PASS fpbox[%0d] in %0d clocks", idx, took);
    end
    issued <= False;
    if (idx == fromInteger(valueOf(NFpVec) - 1)) done <= True;
    else idx <= idx + 1;
  endrule

  rule rl_finish (done);
    if (fails == 0) $display("ALL TESTS PASSED");
    else $display("%0d TEST(S) FAILED", fails);
    $finish(0);
  endrule
endmodule

// ---------------------------------------------------------------------
// mkPauMixTb, NEW WITH THE MERGE (2026-11-26).  The floating-point and
// divide classes now share the AB and C registers, the pass counter and
// the state machine, so a request must not see what the previous class
// left there.  This issues the classes back to back, each request in the
// clock the previous answer is taken (the same clock mkEBox can
// re-request in), in an order where a stale register would show:
//   0  FP multiply, XFP x N all-ones, single (mkPauFpTb vector 1): leaves
//      the product in rg_ab and the multiplicand in rg_cd
//   1  VFL divide, 239 / 60 (MCP's clock divide; q 3, rem 59): rg_ab is
//      the product
//   2  FP add, 0.75 + 0.75 (mkPauFpTb a1): the answer view after a divide
//   3  FP divide, 1/1 (mkPauDivTb vector 8): walks; fpExtra 20
//   4  FP multiply DOUBLE, all-ones (mkPauFpTb vector 2): after a walk
//   5  VFL divide, max / max (mkPauDivTb vector 1): two requests after a
//      divide that left a remainder of 59
//   6  AN ABANDONED DIVIDE: an FP divide (mkPauDivTb vector 10, 24
//      clocks) is asked and, two clocks later, before it answers, an FP
//      multiply (mkPauFpTb vector 0) is asked over it.  The multiply's
//      answer and its 4 clocks are checked.
// The FP answers are checked bit for bit against the one-step reference
// (fpMul / fpMulDouble / fpAdd), as in mkPauFpTb; the divides against
// `/` and `%` and the literal fpExtra and clocks of mkPauDivTb.
// INJECTIONS, OBSERVED 2026-11-26 (each in a scratch copy of this file;
// the three PAU testbenches run on each; reverted, cmp clean):
//   P  the FP request not clearing the walk (`rg_wBusy[1] <= False`
//      deleted): mix 6 FAILS alone (clocks 22, want 4).  mkPauFpTb,
//      mkPauDivTb and mkFpDivSketchTb pass: none abandons a divide.
//   Q  the divide's request not clearing the remainder (`rg_rem[1] <= 0`
//      deleted): mix 3 FAILS alone (it follows mix 1's remainder of 59,
//      across the FP add in between); mkPauDivTb fails 1, 4, 5, 6, 7, 8,
//      10, 11, 12 (each after a vector that left a remainder, or after
//      vector 0's 5); mkPauFpTb and mkFpDivSketchTb pass.
// ---------------------------------------------------------------------
typedef 7 NPauMixVec;

(* synthesize *)
module mkPauMixTb(Empty);
  PAU            box     <- mkPAU;
  Reg#(Bit#(4))  idx     <- mkReg(0);
  Reg#(Bit#(8))  fails   <- mkReg(0);
  Reg#(Bool)     issued  <- mkReg(False);
  Reg#(Bool)     done    <- mkReg(False);
  Reg#(Bool)     aborted <- mkReg(False);
  Reg#(Bit#(16)) clk     <- mkReg(0);
  Reg#(Bit#(16)) t0      <- mkReg(0);

  rule rl_clk; clk <= clk + 1; endrule

  function FpNum n(Bit#(1) ef, Bit#(10) em, Bit#(1) es, Bit#(48) f, Bit#(1) sg) =
    FpNum { ef: ef, em: em, es: es, frac: f, sign: sg, flags: 3'b000 };
  FpMulReq mul0 = FpMulReq { a: n(0, 1, 0, 48'h800000000000, 0), b: n(0, 1, 0, 48'h800000000000, 0),
                             normalized: True, noisy: False, dbl: False };
  FpMulReq mul1 = FpMulReq { a: n(1, 5, 0, 48'hFFFFFFFFFFFF, 1), b: n(0, 3, 0, 48'hFFFFFFFFFFFF, 0),
                             normalized: True, noisy: False, dbl: False };
  FpMulReq mul2 = FpMulReq { a: n(1, 5, 0, 48'hFFFFFFFFFFFF, 1), b: n(0, 3, 0, 48'hFFFFFFFFFFFF, 0),
                             normalized: True, noisy: False, dbl: True };
  FpNum    ad   = n(0, 5, 0, 48'hC00000000000, 0);
  FpAddPrep ap  = fpAddPrep(ad, ad, True, False, False, False);
  FpAddReq add1 = FpAddReq { dp: ap.dp, ctx: ap.ctx, dbl: False };
  DivReq   div1 = DivReq { dvd: 96'hffffffffffff_ffffffffffff, dvs: 48'hffffffffffff,
                           fpFixed: 0, fpDbl: False };
  DivReq   div8 = DivReq { dvd: 96'h800000000000_000000000000, dvs: 48'h800000000000,
                           fpFixed: 7, fpDbl: False };
  DivReq   div10 = DivReq { dvd: 96'hffffffffffff_000000000000, dvs: 48'h800000000001,
                            fpFixed: 7, fpDbl: False };
  DivReq   divM = DivReq { dvd: 96'h000000000000_0000000000ef, dvs: 48'h00000000003c,
                           fpFixed: 0, fpDbl: False };

  function PauReq reqOf(Bit#(4) i) =
    case (i)
      0: tagged PauFp (tagged FpMul mul1);
      1: tagged PauDiv divM;
      2: tagged PauFp (tagged FpAdd add1);
      3: tagged PauDiv div8;
      4: tagged PauFp (tagged FpMul mul2);
      5: tagged PauDiv div1;
      default: tagged PauDiv div10;    // 6: abandoned two clocks in
    endcase;
  function Bool isDivRsp(PauRsp r);
    case (r) matches
      tagged PauRspDiv .*: return True;
      default: return False;
    endcase
  endfunction
  function Bool isDivOf(Bit#(4) i) = (i == 1 || i == 3 || i == 5);
  function FpRsp fpWantOf(Bit#(4) i) =
    case (i)
      0: tagged FpRspSingle fpMul(mul1.a, mul1.b, True, False);
      2: tagged FpRspSingle fpAdd(ad, ad, True, False, False, False);
      4: tagged FpRspDouble fpMulDouble(mul2.a, mul2.b, True, False);
      default: tagged FpRspSingle fpMul(mul0.a, mul0.b, True, False);
    endcase;
  function DivReq divOf(Bit#(4) i) =
    case (i) 1: divM; 3: div8; default: div1; endcase;
  function Bit#(16) clocksOf(Bit#(4) i) =
    case (i) 2: 1; 3: 8; default: 4; endcase;
  function Bit#(16) extraOf(Bit#(4) i) = (i == 3) ? 20 : 0;

  rule rl_first (!done && !issued);
    box.request(reqOf(idx));
    issued <= True;
    t0 <= clk;
  endrule

  // Vector 6: two clocks after the abandoned divide was asked, ask the
  // multiply over it.
  rule rl_abandon (!done && issued && idx == 6 && !aborted && clk == t0 + 2);
    box.request(tagged PauFp (tagged FpMul mul0));
    aborted <= True;
    t0 <= clk;
  endrule

  rule rl_collect (!done && issued && box.responseReady() && (idx != 6 || aborted));
    PauRsp   got  = box.response();
    Bit#(16) took = clk - t0;
    Bool     ok   = True;
    if (isDivOf(idx)) begin
      DivRsp   g   = pauDivRsp(got);
      DivReq   r   = divOf(idx);
      Bit#(96) dvs = zeroExtend(r.dvs);
      Bit#(96) wq  = r.dvd / dvs;
      Bit#(96) wr  = r.dvd % dvs;
      if (!isDivRsp(got) || g.q != wq || zeroExtend(g.rem) != wr) begin
        $display("FAIL pau mix[%0d] divide: q=%h want %h, rem=%h want %h", idx, g.q, wq, g.rem, wr);
        ok = False;
      end else if (g.fpExtra != extraOf(idx)) begin
        $display("FAIL pau mix[%0d] fpExtra = %0d, want %0d", idx, g.fpExtra, extraOf(idx));
        ok = False;
      end
    end else begin
      if (pack(got) != pack(tagged PauRspFp fpWantOf(idx))) begin
        $display("FAIL pau mix[%0d] floating point: got ", idx, fshow(got));
        $display("                 want ", fshow(fpWantOf(idx)));
        ok = False;
      end
    end
    if (ok && took != clocksOf(idx)) begin
      $display("FAIL pau mix[%0d] clocks = %0d, want %0d", idx, took, clocksOf(idx));
      ok = False;
    end
    if (ok) $display("PASS pau mix[%0d] in %0d clocks", idx, took);
    else fails <= fails + 1;
    if (idx == fromInteger(valueOf(NPauMixVec) - 1)) begin
      done <= True;
      issued <= False;
    end else begin
      box.request(reqOf(idx + 1));
      t0 <= clk;
      idx <= idx + 1;
    end
  endrule

  rule rl_finish (done);
    if (fails == 0) $display("ALL TESTS PASSED");
    else $display("%0d TEST(S) FAILED", fails);
    $finish(0);
  endrule
endmodule

// ---------------------------------------------------------------------
// mkPauStepTb (fidelity_plan.md A4 step 3, 2026-11-26): MULTIPLY AND ADD
// (`*+`) as one chained request, and the time terms of its add.  Each
// vector is an FpMulAdd request (the multiply as the `*+` arm asks it:
// MULTIPLY DOUBLE, unnormalized, noisy off), checked three ways:
//   (a) the whole answer, bit for bit, against the arm's old one-step
//       form, fpAddDouble(acc, fpMulDouble(opnd, factor).res, ...) --
//       fpAddSumRef, a different adder from the unit's;
//   (b) the LITERAL clocks: 5 on the datapath path (four multiply passes
//       and the add pass), 4 when the preparation answers (flagged);
//   (c) the LITERAL fpExtra, worked by hand from Table 2 (printed p.3-4)
//       and Fig. 3.8.13's alternative path, one term per vector:
//   0  acc 1 (.1 x 2^1) + 1 x 1 (product .01 x 2^2): acc exponent smaller
//      (shift 1): extra 0 with pauMaAccSmaller off (the default), 3 with
//      it on (Fig. 3.8.13's alternative path); sum .1 x 2^2 (literal)
//   1  acc 4096 (.1 x 2^13) + 1 x 1: shift 11, ceil((11-3)/4) = 2 extra
//      pre-shift cycles: extra 2
//   2  acc -(.001 x 2^2) + 1 x 1, equal exponents: the unshifted fraction
//      is the smaller, so the add recomplements: extra 2; sum .001 x 2^2
//      normalized to .1 x 2^0, positive (literal)
//   3  acc -((.01 - 2^-12) x 2^2) + 1 x 1, normalized: recomplements and
//      the difference 2^-12 normalizes 11 places, one additional pass of
//      six: extra 2 + 2 = 4
//   4  vector 3 unnormalized (U): no normalization: extra 2
//   5  acc XPFN (flagged): the preparation answers, no add pass: extra 0,
//      4 clocks
//   6  acc .1 x 2^-10 + 1 x 1: shift 12, ceil(9/4) = 3 pre-shift cycles:
//      extra 3 (6 with pauMaAccSmaller on: the acc is the smaller)
//   7  a plain MULTIPLY after them (mkPauFpTb vector 0): extra 0, 4 clocks
// and two PLAIN ADDS (FpAdd, single, normalized; pauAddStep), 1 clock:
//   8  ADD, acc 4096 (.1 x 2^13) + 1: shift 12, ceil((12-3)/4) = 3 extra
//      pre-shift cycles: terms 3; sum 4097 (checked against fpAdd)
//   9  ADD TO MAGNITUDE (+MG), acc 1 + (-2): shift 1, no recomplement
//      (the larger-exponent fraction is the minuend), and the negative sum
//      is forced to zero (Ref. Manual p.83): terms 2
//   For 8 and 9 the terms are checked as pauAddTerms' literal value, and
//   the unit's fpExtra as 0: pauAddStep is off, so the plain add is not
//   charged (with it on, fpExtra is the terms, 3 and 2).
// INJECTIONS, OBSERVED 2026-11-26: each switch set False in a scratch copy
// of this file, with mkPauStepTb, mkPauFpTb, mkPauDivTb, mkFpDivSketchTb and
// mkPauMixTb run on each copy (copy deleted after):
//   pauMaPreshift    step 1 (0, want 2), 6 (0, want 3), 8 (terms 0, want 3)
//   pauMaNorm        step 3 (2, want 4)
//   pauMaRecomp      step 2 (0, want 2), 3 (2, want 4), 4 (0, want 2)
//   pauMaAccSmaller  (default off; injected ON) step 0 (3, want 0),
//                    6 (6, want 3)
//   pauAddStep       (default off; injected ON) step 8 (fpExtra 3, want
//                    0), 9 (fpExtra 2, want 0)
//   pauAddForcedZero step 9 (terms 0, want 2)
// The other four were each set False.  Each injection fails
// exactly those vectors; every other bench passes each time.
// (pauChainMulAdd is the E-box arm's choice, not this unit's: the atlas
// run with every term off and the chain on matches the base on PDF 57/88
// within 0.05 clock on all 320 rows, fidelity_plan.md A4.)
// ---------------------------------------------------------------------
typedef 10 NPauStepVec;

(* synthesize *)
module mkPauStepTb(Empty);
  PAU            box    <- mkPAU;
  Reg#(Bit#(4))  idx    <- mkReg(0);
  Reg#(Bit#(8))  fails  <- mkReg(0);
  Reg#(Bool)     issued <- mkReg(False);
  Reg#(Bool)     done   <- mkReg(False);
  Reg#(Bit#(16)) clk    <- mkReg(0);
  Reg#(Bit#(16)) t0     <- mkReg(0);

  rule rl_clk; clk <= clk + 1; endrule

  FpNum one = FpNum { ef: 0, em: 1, es: 0, frac: 48'h800000000000, sign: 0, flags: 3'b000 };
  function FpDouble dd(Bit#(1) ef, Bit#(10) em, Bit#(1) es, Bit#(96) f, Bit#(1) sg) =
    FpDouble { ef: ef, em: em, es: es, frac: f, sign: sg, flags: 3'b000 };
  function FpDouble accOf(Bit#(4) i) =
    case (i)
      0: dd(0, 1, 0, 96'h800000000000_000000000000, 0);
      1: dd(0, 13, 0, 96'h800000000000_000000000000, 0);
      2: dd(0, 2, 0, 96'h200000000000_000000000000, 1);
      3, 4: dd(0, 2, 0, 96'h3FF000000000_000000000000, 1);
      5: dd(1, 1, 1, 96'h800000000000_000000000000, 0);
      default: dd(0, 10, 1, 96'h800000000000_000000000000, 0);
    endcase;
  function Bool nrmOf(Bit#(4) i) = (i != 4);
  FpMulReq mq = FpMulReq { a: one, b: one, normalized: False, noisy: False, dbl: True };
  FpMulReq m0 = FpMulReq { a: one, b: one, normalized: True, noisy: False, dbl: False };
  FpNum    big  = FpNum { ef: 0, em: 13, es: 0, frac: 48'h800000000000, sign: 0, flags: 3'b000 };
  FpNum    mtwo = FpNum { ef: 0, em: 2, es: 0, frac: 48'h800000000000, sign: 1, flags: 3'b000 };
  FpNum    addA = (idx == 8) ? big : one;
  FpNum    addB = (idx == 8) ? one : mtwo;
  Bool     addM = (idx == 9);
  FpAddPrep ap  = fpAddPrep(addA, addB, True, False, addM, False);
  Bool     plain = (idx == 7);
  Bool     isAdd = (idx == 8 || idx == 9);
  FpReq    req  = isAdd ? tagged FpAdd FpAddReq { dp: ap.dp, ctx: ap.ctx, dbl: False }
                : plain ? tagged FpMul m0
                        : tagged FpMulAdd FpMulAddReq { mul: mq, acc: accOf(idx),
                                                        normalized: nrmOf(idx), noisy: False };
  FpRsp    want = isAdd ? tagged FpRspSingle fpAdd(addA, addB, True, False, addM, False)
                : plain ? tagged FpRspSingle fpMul(one, one, True, False)
                        : tagged FpRspDouble fpAddDouble(accOf(idx), fpMulDouble(one, one, False, False).res,
                                                         nrmOf(idx), False, False);
  function Bit#(16) extraOf(Bit#(4) i) =
    case (i) 1: 2; 2: 2; 3: 4; 4: 2; 6: 3; default: 0; endcase;
  // Vectors 8 and 9: Table 2's terms of the add itself, literal.
  match {.tSum, .tRc} = fpBoxAddSumR(ap.dp);
  Bit#(16) termsGot  = pauAddTerms(ap.dp, tSum, tRc);
  Bit#(16) termsWant = (idx == 8) ? 3 : 2;
  function Bit#(16) clocksOf(Bit#(4) i) = (i == 8 || i == 9) ? 1 : (i == 5 || i == 7) ? 4 : 5;

  rule rl_issue (!done && !issued);
    box.request(tagged PauFp req);
    issued <= True;
    t0 <= clk;
  endrule

  rule rl_collect (!done && issued && box.responseReady());
    FpRsp    got  = pauFpRsp(box.response());
    Bit#(16) x    = box.fpExtra();
    Bit#(16) took = clk - t0;
    FpdResult g   = fpRspDouble(got);
    Bool litOk = True;
    if (idx == 0) litOk = (g.res.frac == 96'h800000000000_000000000000 && g.res.em == 2 && g.res.sign == 0);
    if (idx == 2) litOk = (g.res.frac == 96'h800000000000_000000000000 && g.res.em == 0 && g.res.sign == 0);
    if (pack(got) != pack(want)) begin
      $display("FAIL pau step[%0d]: got ", idx, fshow(got));
      $display("               want ", fshow(want));
      fails <= fails + 1;
    end else if (!litOk) begin
      $display("FAIL pau step[%0d]: literal wrong: ", idx, fshow(got));
      fails <= fails + 1;
    end else if (took != clocksOf(idx)) begin
      $display("FAIL pau step[%0d] clocks = %0d, want %0d", idx, took, clocksOf(idx));
      fails <= fails + 1;
    end else if (x != extraOf(idx)) begin
      $display("FAIL pau step[%0d] fpExtra = %0d, want %0d", idx, x, extraOf(idx));
      fails <= fails + 1;
    end else if (isAdd && termsGot != termsWant) begin
      $display("FAIL pau step[%0d] terms = %0d, want %0d", idx, termsGot, termsWant);
      fails <= fails + 1;
    end else
      $display("PASS pau step[%0d] in %0d clocks, fpExtra %0d", idx, took, x);
    issued <= False;
    if (idx == fromInteger(valueOf(NPauStepVec) - 1)) done <= True;
    else idx <= idx + 1;
  endrule

  rule rl_finish (done);
    if (fails == 0) $display("ALL TESTS PASSED");
    else $display("%0d TEST(S) FAILED", fails);
    $finish(0);
  endrule
endmodule

endpackage
