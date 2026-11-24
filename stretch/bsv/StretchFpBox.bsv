// StretchFpBox.bsv -- the FLOATING-POINT BOX: the expensive datapath of
// fpArithClass (StretchExecute.bsv) as a multi-cycle box.
//
// >>> WHY A BOX (AGENTS.md, "Idiomatic Bluespec") <<<  fpArithClass is
// the second-largest combinational function in the model, and the
// owner's rule is that its expensive datapath lives in "MULTI-CYCLE,
// stateful 'box' sub-modules ... instantiated once, with request/
// response methods" -- Piccolo's and Flute's mkFBox -- not inlined into
// the E-box rule.  This box has mkVflBox's shape (StretchVflBox.bsv):
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
package StretchFpBox;

import StretchFP::*;

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

typedef union tagged {
  FpMulReq FpMul;
  FpAddReq FpAdd;
} FpReq deriving (Bits, Eq, FShow);

// THE BOX'S ADDER (see the header): 1s complement with end-around carry
// on the pre-shifted operand, then the forced-zero rule and the
// normalization exactly as fpAddSumRef applies them.
function FpAddSum fpBoxAddSum(FpAddDp d);
  // The alignment: the smaller-exponent fraction moves right.
  Bit#(96) fsh = d.fs >> d.shift;
  Bool     sub = (d.bigSign != d.smlSign);
  Bit#(97) t   = zeroExtend(d.fb) + zeroExtend(sub ? ~fsh : fsh);
  Bit#(97) sum;
  Bit#(1)  sign;
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
  return FpAddSum { frac: f96, adj: adj, lc: lostCarry, zero: (sum == 0),
                    sign: sign, forcedZero: forcedZero };
endfunction

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

interface FpBox;
  method Action request(FpReq r);
  method Bool responseReady();
  // A VALUE, as every box's is: see mkDivBox's interface note (a guarded
  // response() became the condition of the whole of mkEBox.resume()).
  method FpRsp response();
endinterface

typedef enum { FpIdle, FpMulPass, FpAddPass, FpDone } FpState
  deriving (Bits, Eq, FShow);

(* synthesize *)
module mkFpBox(FpBox);
  // CREGS WITH THE PORT ASSIGNMENT AS THE SCHEDULE, mkDivBox's reason
  // (StretchDivBox.bsv): the rule on port 0, every method on port 1.
  Reg#(FpState)  rg_state[2] <- mkCReg(2, FpIdle);
  Reg#(FpMulReq) rg_mul[2]   <- mkCReg(2, unpack(0));
  // THE PRODUCT REGISTER, mkVflBox's right-to-left arrangement: the
  // multiplier starts in the low 48 bits and leaves at the bottom twelve
  // bits a pass while the partial product grows in from the top.
  Reg#(Bit#(96)) rg_p[2]     <- mkCReg(2, 0);
  Reg#(Bit#(3))  rg_ctr[2]   <- mkCReg(2, 0);
  Reg#(FpRsp)    rg_rsp[2]   <- mkCReg(2, unpack(0));
  Reg#(FpAddReq) rg_add[2]   <- mkCReg(2, unpack(0));

  Integer passes = fpMulBits / fpMulBitsPerCycle;
  if (passes * fpMulBitsPerCycle != fpMulBits)
    error("mkFpBox: FpMulGroup must divide 48");

  // ONE PASS: the low twelve multiplier bits times the multiplicand,
  // added into the high half, the register shifted right twelve.  On the
  // last pass the product is complete and the result is formed from it.
  rule rl_mul (rg_state[0] == FpMulPass);
    FpMulReq m = rg_mul[0];
    Bit#(48)          hi = rg_p[0][95:48];
    Bit#(48)          lo = rg_p[0][47:0];
    Bit#(FpMulGroup)  g  = truncate(lo);
    Bit#(TAdd#(48, FpMulGroup)) pp =
      pack(unsignedMul(UInt#(48)'(unpack(m.b.frac)), UInt#(FpMulGroup)'(unpack(g))));
    Bit#(TAdd#(TAdd#(48, FpMulGroup), 1)) s = zeroExtend(hi) + zeroExtend(pp);
    // The partial product never exceeds 96 bits (mkVflBox's note), so
    // the truncation drops only zeros.
    Bit#(96) np = truncate({s, lo} >> fpMulBitsPerCycle);
    rg_p[0]   <= np;
    rg_ctr[0] <= rg_ctr[0] - 1;
    if (rg_ctr[0] == 1) begin
      rg_rsp[0] <= m.dbl
        ? tagged FpRspDouble fpMulDoubleProd(m.a, m.b, m.normalized, m.noisy, np)
        : tagged FpRspSingle fpMulProd(m.a, m.b, m.normalized, m.noisy, np);
      rg_state[0] <= FpDone;
    end
  endrule

  // THE ADD: one pass, Table 2's one execution cycle (see the header).
  rule rl_add (rg_state[0] == FpAddPass);
    FpAddReq q = rg_add[0];
    FpAddSum sm = fpBoxAddSum(q.dp);
    rg_rsp[0] <= q.dbl ? tagged FpRspDouble fpAddDoubleFinish(q.ctx, sm)
                       : tagged FpRspSingle fpAddFinish(q.ctx, sm);
    rg_state[0] <= FpDone;
  endrule

  // NO IMPLICIT CONDITIONS, for mkDivBox's reason.
  method Action request(FpReq q);
    case (q) matches
      tagged FpMul .m: begin
        rg_mul[1]   <= m;
        rg_p[1]     <= zeroExtend(m.a.frac);
        rg_ctr[1]   <= fromInteger(passes);
        rg_state[1] <= FpMulPass;
      end
      tagged FpAdd .ar: begin
        rg_add[1]   <= ar;
        rg_state[1] <= FpAddPass;
      end
    endcase
  endmethod

  method Bool responseReady() = (rg_state[1] == FpDone);

  method FpRsp response() = rg_rsp[1];
endmodule

// ---------------------------------------------------------------------
// mkFpBox's OWN TESTBENCH, in the same file, as mkVflBoxTb is in
// StretchVflBox.bsv: the box is testable without instantiating storage.
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
module mkFpBoxTb(Empty);
  FpBox          box    <- mkFpBox;
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
    box.request(req);
    issued <= True;
    t0 <= clk;
  endrule

  rule rl_collect (!done && issued && box.responseReady());
    FpRsp    got  = box.response();
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

endpackage
