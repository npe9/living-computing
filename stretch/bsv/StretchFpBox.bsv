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
// The instruction's time is still eboxClocks' (`*` and `D*` 9, `*+` 20).
// As for every box, mkEBox takes the box's clocks off that budget
// (StretchCore's rl_exec_resume).  What the HOLD costs -- the held look-
// ahead level, and the resume clock taking rl_prepare's slot -- is
// measured in microarchitecture_plan.md §1c step 5f and bsv/README.md.
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

typedef union tagged {
  FpMulReq FpMul;
} FpReq deriving (Bits, Eq, FShow);

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

typedef enum { FpIdle, FpMulPass, FpDone } FpState
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

  // NO IMPLICIT CONDITIONS, for mkDivBox's reason.
  method Action request(FpReq q);
    case (q) matches
      tagged FpMul .m: begin
        rg_mul[1]   <= m;
        rg_p[1]     <= zeroExtend(m.a.frac);
        rg_ctr[1]   <= fromInteger(passes);
        rg_state[1] <= FpMulPass;
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
// ---------------------------------------------------------------------
typedef 11 NFpVec;

(* synthesize *)
module mkFpBoxTb(Empty);
  FpBox          box    <- mkFpBox;
  Reg#(Bit#(4))  idx    <- mkReg(0);
  Reg#(Bit#(8))  fails  <- mkReg(0);
  Reg#(Bool)     issued <- mkReg(False);
  Reg#(Bool)     done   <- mkReg(False);
  Reg#(Bit#(16)) clk    <- mkReg(0);
  Reg#(Bit#(16)) t0     <- mkReg(0);

  rule rl_clk; clk <= clk + 1; endrule

  function FpNum n(Bit#(1) ef, Bit#(10) em, Bit#(1) es, Bit#(48) f, Bit#(1) sg) =
    FpNum { ef: ef, em: em, es: es, frac: f, sign: sg, flags: 3'b000 };

  function FpMulReq reqOf(Bit#(4) i) =
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

  function FpRsp refOf(FpMulReq m) =
    m.dbl ? tagged FpRspDouble fpMulDouble(m.a, m.b, m.normalized, m.noisy)
          : tagged FpRspSingle fpMul(m.a, m.b, m.normalized, m.noisy);

  rule rl_issue (!done && !issued);
    box.request(tagged FpMul reqOf(idx));
    issued <= True;
    t0 <= clk;
  endrule

  rule rl_collect (!done && issued && box.responseReady());
    FpRsp    got  = box.response();
    FpRsp    want = refOf(reqOf(idx));
    Bit#(16) took = clk - t0;
    Bool litOk = True;
    if (idx == 1) litOk = (fpRspSingle(got).res.frac == 48'hFFFFFFFFFFFE);
    if (idx == 2) litOk = (fpRspDouble(got).res.frac == 96'hFFFFFFFFFFFE000000000001);
    if (pack(got) != pack(want)) begin
      $display("FAIL fpbox[%0d]: got ", idx, fshow(got));
      $display("               want ", fshow(want));
      fails <= fails + 1;
    end else if (!litOk) begin
      $display("FAIL fpbox[%0d]: literal fraction wrong: ", idx, fshow(got));
      fails <= fails + 1;
    end else if (took != 4) begin
      $display("FAIL fpbox[%0d] clocks = %0d, want 4", idx, took);
      fails <= fails + 1;
    end else
      $display("PASS fpbox[%0d] in %0d clocks", idx, took);
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
