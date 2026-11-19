// StretchVflBox.bsv -- the VFL ARITHMETIC BOX: the expensive datapath of
// vflIntOp (StretchExecute.bsv) as a multi-cycle box.
//
// >>> WHY A BOX (AGENTS.md, "Idiomatic Bluespec") <<<  vflIntOp is the
// largest combinational function in the model, and the owner's rule is
// that its expensive datapath lives in "MULTI-CYCLE, stateful 'box'
// sub-modules ... instantiated once, with request/response methods" (the
// mkFBox / mkRISCV_MBox / mkShifter_Box shape), not inlined into a rule.
// This box is mkDecBox's shape (StretchDecBox.bsv): instantiated ONCE in
// mkEBox, reached through execute()'s `NeedBox` bail, a request method, a
// responseReady poll and a response value.
//
// STAGE 1 (2026-11-18) MOVES ONE CLASS: THE BINARY MULTIPLY.  The 48 x 48
// product of VFL `*` (code 011001) and of `*+` (MULTIPLY AND ADD, code
// 111001), which were two inlined `Bit#(96) prod = a * b` -- two full
// 96-bit combinational multipliers in the E-box rule.  The request is a
// tagged union so that the next classes join it without a new box.
//
// ---------------------------------------------------------------------
// WHAT IS SOURCED, AND IT IS THE RATE
// ---------------------------------------------------------------------
// Buchholz (ed.), "Planning a Computer System", §14.4 "Arithmetic Unit",
// read in the text layer of docs/Planning_A_Computer_System.pdf:
//
//   * printed p.208 (PDF 233): "Operations on the floating-point fraction
//     and also variable-field-length binary multiply and divide
//     operations are performed by the PARALLEL unit."  So this is the
//     PAU's multiplier, the one the floating-point fraction uses, and not
//     the serial unit's byte loop.  (R23-9694 printed p.121 says the same
//     of the VFL divide, "AS IN MULTIPLY, THIS OPERATION IS ACTUALLY
//     PERFORMED BY PAU", cited in StretchDivBox.bsv.)
//   * printed p.210 (PDF 235): "To expedite the execution of the multiply
//     instructions, 12 BITS OF THE MULTIPLIER ARE HANDLED IN ONE CYCLE.
//     ... The action
//     is from right to left".
//   * printed p.211 (PDF 236): the multiplicand multiples are summed in
//     carry-save adders, "and, DURING THE LAST CYCLE, into the carry
//     propagate adder for accumulation of the carries.  Since no
//     propagation of carries is required in THE FOUR CYCLES when
//     multiplicand multiples are added, this operation is fast".
//
// So a 48-bit multiplier is FOUR cycles of twelve bits, right to left,
// and the final carry assimilation shares the fourth: request at T, the
// four passes at T+1 .. T+4, the answer readable at T+4 (the CReg note
// below says why).  `vflMulBitsPerCycle` is that 12.
//
// WHAT IS NOT MODELLED, said once: the recoding.  The 7030 decodes each
// 12-bit group as four 3-bit groups into even multiples of the
// multiplicand (Fig. 14.8) and keeps the partial product in carry-save
// form between cycles.  The box below adds the exact 48 x 12 partial
// product each pass in ordinary binary.  The product is the same number
// either way; only the internal representation differs, and nothing
// outside the box can observe it.
//
// ---------------------------------------------------------------------
// TIME
// ---------------------------------------------------------------------
// The instruction's time is still eboxClocks' (StretchTiming.bsv: binary
// `*` 36 + 2s or more, `*+` 46 + 2s or more, from Perf. Char. Vol. 2's
// atlas).  As for every box, mkEBox takes the box's clocks off that
// budget (StretchCore's rl_exec_resume), and 4 fits inside the smallest
// of them many times over.  What the hold costs instead -- the held
// look-ahead level stops I-box instructions overlapping the countdown --
// is measured for this box in microarchitecture_plan.md §1c step 5e.
// ---------------------------------------------------------------------
package StretchVflBox;

// >>> SOURCED: Buchholz printed p.210, "12 bits of the multiplier are
// handled in one cycle". <<<  A width, so a typedef; it must divide 48
// (elaboration refuses one that does not).
typedef 12 VflMulGroup;
Integer vflMulBitsPerCycle = valueOf(VflMulGroup);
Integer vflMulBits         = 48;

// THE MULTIPLY REQUEST: the two 48-bit magnitudes, already truncated to
// their low 48 bits by the caller (printed p.68: "only the 48 low-order
// bits of the oversized operand are used").  Signs and Partial Field
// stay with the caller; the box multiplies magnitudes only.
typedef struct {
  Bit#(48) mcand;   // the multiplicand
  Bit#(48) mpr;     // the multiplier, consumed twelve bits a cycle
} VflMulReq deriving (Bits, Eq, FShow);

// One variant today; the next classes add theirs here.
typedef union tagged {
  VflMulReq VflMul;
} VflReq deriving (Bits, Eq, FShow);

typedef struct {
  Bit#(96) prod;    // the 96-bit product (48 x 48)
} VflRsp deriving (Bits, Eq, FShow);

interface VflBox;
  method Action request(VflReq r);
  method Bool responseReady();
  // A VALUE, as mkDivBox's and mkDecBox's are: see mkDivBox's interface
  // note (a guarded response() became the condition of the whole of
  // mkEBox.resume()).
  method VflRsp response();
endinterface

typedef enum { VflIdle, VflMulPass, VflDone } VflState
  deriving (Bits, Eq, FShow);

(* synthesize *)
module mkVflBox(VflBox);
  // CREGS WITH THE PORT ASSIGNMENT AS THE SCHEDULE, for the reason
  // mkDivBox gives (StretchDivBox.bsv): the rule uses port 0 and every
  // method port 1, so the rule comes before the methods and a caller
  // rule may poll, take and re-request in one clock -- and the answer of
  // the last pass is readable in the clock of that pass.
  Reg#(VflState) rg_state[2] <- mkCReg(2, VflIdle);
  Reg#(Bit#(48)) rg_mcand[2] <- mkCReg(2, 0);
  // THE PRODUCT REGISTER, the textbook right-to-left shift-and-add
  // arrangement: the multiplier starts in the low 48 bits and leaves at
  // the bottom twelve bits a pass, while the partial product grows in
  // from the top.  After the fourth pass it holds the whole product.
  Reg#(Bit#(96)) rg_p[2]     <- mkCReg(2, 0);
  Reg#(Bit#(3))  rg_ctr[2]   <- mkCReg(2, 0);

  Integer passes = vflMulBits / vflMulBitsPerCycle;
  if (passes * vflMulBitsPerCycle != vflMulBits)
    error("mkVflBox: VflMulGroup must divide 48");

  // ONE PASS: the low twelve multiplier bits times the multiplicand,
  // added into the high half, and the register shifted right twelve.
  rule rl_mul (rg_state[0] == VflMulPass);
    Bit#(48)          hi = rg_p[0][95:48];
    Bit#(48)          lo = rg_p[0][47:0];
    Bit#(VflMulGroup) g  = truncate(lo);
    // unsignedMul is UInt#(n) x UInt#(m) -> UInt#(n+m): a 48 x 12
    // multiplier, exactly the width of the pass and no wider.
    Bit#(TAdd#(48, VflMulGroup)) pp =
      pack(unsignedMul(UInt#(48)'(unpack(rg_mcand[0])), UInt#(VflMulGroup)'(unpack(g))));
    Bit#(TAdd#(TAdd#(48, VflMulGroup), 1)) s = zeroExtend(hi) + zeroExtend(pp);
    // {s, lo} >> 12: the partial product can never exceed 96 bits (after
    // k passes it is below 2^(48 + 12k) and sits 48 - 12k bits up), so
    // the truncation drops only zeros.
    Bit#(96) np = truncate({s, lo} >> vflMulBitsPerCycle);
    rg_p[0] <= np;
    rg_ctr[0] <= rg_ctr[0] - 1;
    if (rg_ctr[0] == 1) rg_state[0] <= VflDone;
  endrule

  // NO IMPLICIT CONDITIONS, for mkDivBox's reason.
  method Action request(VflReq q);
    case (q) matches
      tagged VflMul .m: begin
        rg_mcand[1] <= m.mcand;
        rg_p[1]     <= zeroExtend(m.mpr);
        rg_ctr[1]   <= fromInteger(passes);
        rg_state[1] <= VflMulPass;
      end
    endcase
  endmethod

  method Bool responseReady() = (rg_state[1] == VflDone);

  method VflRsp response() = VflRsp { prod: rg_p[1] };
endmodule

// ---------------------------------------------------------------------
// mkVflBox's OWN TESTBENCH, in the same file, as mkDecBoxTb is in
// StretchDecBox.bsv: the box is testable without instantiating storage.
//
// THE EXPECTATIONS ARE LITERALS, not a `*` in the testbench, which
// would be the box checking itself against the operator it replaced.
// They were worked in Python's arbitrary-precision integers, a separate
// implementation, and two are checkable by hand: (2^48 - 1)^2 is
// 2^96 - 2^49 + 1, and 0x123456789ABC x 0xFFF is 0x123456789ABC000 -
// 0x123456789ABC.  Every vector also asserts a LITERAL clock count, 4
// (Buchholz printed p.211's "four cycles").
//
// The vectors place multiplier bits in each twelve-bit group in turn,
// so that a mistake in how one pass hands on to the next shows in some
// vectors and not others:
//   0-1  trivial (0 x 0, 1 x 1)                        group 0 only
//   2    (2^48 - 1)^2, every bit of both operands      all groups
//   3    (2^48 - 1) x 2^12                             group 1 only
//   4    0x123456789ABC x 0xFFF                        group 0 only
//   5    0x123456789ABC x 0xFFF000                     group 1 only
//   6    (2^48 - 1) x 2^47, the top multiplier bit     group 3 only
//   7    a dense pattern across every group            all groups
//   8    (2^47 + 1)^2, the end bits of each operand    groups 0 and 3
//
// INJECTIONS, OBSERVED 2026-11-18 (each reverted from a saved copy,
// verified with cmp):
//   * the top bit of every twelve-bit group dropped (`g = truncate(lo) &
//     12'h7FF`): FAILS 2, 4, 5, 6, 7 and 8 -- every vector whose
//     multiplier has bit 11 of some group set -- and PASSES 0, 1 and 3,
//     the control (their multiplier bits are 0, bit 0 and bit 12).
//   * the pass shift made eleven instead of twelve: fails every vector
//     but 0 (0 x 0).  Predicted beforehand as "only the vectors with
//     multiplier bits above group 0"; that was wrong, because the shift
//     also places the finished product, so vector 1 fails too.
// ---------------------------------------------------------------------
typedef 9 NVflVec;

(* synthesize *)
module mkVflBoxTb(Empty);
  VflBox         box    <- mkVflBox;
  Reg#(Bit#(4))  idx    <- mkReg(0);
  Reg#(Bit#(8))  fails  <- mkReg(0);
  Reg#(Bool)     issued <- mkReg(False);
  Reg#(Bool)     done   <- mkReg(False);
  Reg#(Bit#(16)) clk    <- mkReg(0);
  Reg#(Bit#(16)) t0     <- mkReg(0);

  rule rl_clk; clk <= clk + 1; endrule

  function VflMulReq reqOf(Bit#(4) i) =
    case (i)
      0: VflMulReq { mcand: 48'h0,            mpr: 48'h0 };
      1: VflMulReq { mcand: 48'h1,            mpr: 48'h1 };
      2: VflMulReq { mcand: 48'hFFFFFFFFFFFF, mpr: 48'hFFFFFFFFFFFF };
      3: VflMulReq { mcand: 48'hFFFFFFFFFFFF, mpr: 48'h1000 };
      4: VflMulReq { mcand: 48'h123456789ABC, mpr: 48'hFFF };
      5: VflMulReq { mcand: 48'h123456789ABC, mpr: 48'hFFF000 };
      6: VflMulReq { mcand: 48'hFFFFFFFFFFFF, mpr: 48'h800000000000 };
      7: VflMulReq { mcand: 48'hFEDCBA987654, mpr: 48'h0FFF0FFF0FFF };
      default: VflMulReq { mcand: 48'h800000000001, mpr: 48'h800000000001 };
    endcase;
  function Bit#(96) wantOf(Bit#(4) i) =
    case (i)
      0: 96'h0;
      1: 96'h1;
      2: 96'hFFFFFFFFFFFE000000000001;
      3: 96'hFFFFFFFFFFFF000;
      4: 96'h123333333332544;
      5: 96'h123333333332544000;
      6: 96'h7FFFFFFFFFFF800000000000;
      7: 96'hFECDCB9A98663459678C9AC;
      default: 96'h400000000001000000000001;
    endcase;

  rule rl_issue (!done && !issued);
    box.request(tagged VflMul reqOf(idx));
    issued <= True;
    t0 <= clk;
  endrule

  rule rl_collect (!done && issued && box.responseReady());
    Bit#(96) got  = box.response().prod;
    Bit#(96) want = wantOf(idx);
    Bit#(16) took = clk - t0;
    if (got != want) begin
      $display("FAIL vflbox[%0d]: prod=%h, want %h", idx, got, want);
      fails <= fails + 1;
    end else if (took != 4) begin
      $display("FAIL vflbox[%0d] clocks = %0d, want 4", idx, took);
      fails <= fails + 1;
    end else
      $display("PASS vflbox[%0d] prod=%h in %0d clocks", idx, got, took);
    issued <= False;
    if (idx == fromInteger(valueOf(NVflVec) - 1)) done <= True;
    else idx <= idx + 1;
  endrule

  rule rl_finish (done);
    if (fails == 0) $display("ALL TESTS PASSED");
    else $display("%0d TEST(S) FAILED", fails);
    $finish(0);
  endrule
endmodule

endpackage
