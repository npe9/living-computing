// StretchDecBox.bsv -- the DECIMAL ADDER, as a multi-cycle box.
//
// >>> WHY A BOX (AGENTS.md, "Idiomatic Bluespec") <<<  Decimal VFL
// arithmetic needs a 32-digit BCD add/subtract with decimal carry,
// complementation and recomplementation.  Written as a function inside
// execute() it would be one more 128-bit combinational datapath inlined
// into the E-box rule, at every call site -- the shape
// docs/fpga_feasibility.md §10 measures as the reason the model does not
// fit the ULX3S.  So it is mkDivBox's shape instead (StretchDivBox.bsv,
// the mkFBox / mkRISCV_MBox pattern): instantiated ONCE in mkEBox,
// reached through execute()'s `NeedBox` bail, a request method, a
// responseReady poll and a response value.  The arms of vflIntOp that
// need a decimal sum -- +, +MG, M+, M+1, M+MG and decimal SRD's
// rounding -- ask for it and are re-run with the answer.
//
// ---------------------------------------------------------------------
// WHAT IT COMPUTES, AND WHERE THAT IS PRINTED
// ---------------------------------------------------------------------
// Reference Manual 22-6530-2 printed p.60 (PDF 63), ADD, Radix: the
// radix modifier "determines the properties of the adder, and controls
// complementation and recomplementation when the effective operand
// signs are unlike.  In decimal arithmetic, four-bit bytes are used ...
// and a carry occurs from one byte to the next when a sum byte exceeds
// 9."  Printed p.57: "In decimal operations, the accumulator is treated
// as 32 four-bit digit positions."
//
// So the box adds two 32-digit operands `a` and `b`, digit by digit:
//
//   * LIKE SIGNS (`sub` False): r = a + b mod 10^32, and `carry` is
//     the carry out of digit 31 -- the caller's Lost Carry.
//   * UNLIKE SIGNS (`sub` True): COMPLEMENT b (nines' complement plus
//     an initial carry of one: a + (10^32 - 1 - b) + 1) and add.  An
//     END CARRY means a >= b and the sum is a - b; `carry` is True.
//     NO end carry means a < b and the sum is the tens' complement of
//     b - a, so a SECOND PASS RECOMPLEMENTS it (nines' complement
//     plus one again) and `carry` is False: the caller takes b's sign.
//     That second pass is the "recomplementation" p.60 names, and it
//     costs a pass of clocks, as it would have on the machine.
//
// The caller turns that into a signed result exactly as smAdd does for
// binary (StretchALU.bsv): like signs keep a's sign; unlike signs keep
// a's sign if a >= b (so an all-zero result keeps the accumulator's
// sign -- p.60's "the sign remains as it was before the operation
// began") and take b's otherwise.
//
// ---------------------------------------------------------------------
// WHAT IS NOT IN THE SOURCES, SAID HERE ONCE
// ---------------------------------------------------------------------
// * INVALID DIGITS (1010-1111).  The Reference Manual defines no check
//   (docs/spec_decimal.md 1d: no indicator, and p.58 says of unwanted
//   bits only that they are ignored).  The digit step below is the
//   textbook one -- binary add, and if the sum exceeds nine subtract
//   ten and carry.  FOR AN ADD TO ZERO THAT IS SOURCED: C22-6578
//   printed p.15 (PDF 16), Problem 2.3 Method 4's comment (b), read in
//   the page image: "In the decimal load the 4-bit bytes will not be
//   altered if they contain what appears to be decimal information.
//   Otherwise, carry propagation and assimilation will occur.  The byte
//   (1 1 1 1)2, for instance, will become (0101)2 with a carry to the
//   higher byte."  decDigitStep(15, 0, 0) is (5, 1).  An invalid digit
//   met by a subtraction (the nines' complement of 1010-1111 is
//   negative in four bits) has NO source; whatever this produces there
//   is not a claim about the machine.
// * BYTE SIZE BELOW FOUR WITH UNLIKE SIGNS.  p.58: "normal decimal
//   results may not be produced if two operands are involved whose
//   effective signs are unlike, owing to the complementing procedure
//   used."  The box receives four-bit digits whatever the storage byte
//   size was (the caller zero-extends, p.58: "each byte of the storage
//   operand is converted to a four-bit byte for processing by the
//   addition of high-order zeros"), so it produces the NORMAL result.
//   The abnormal one is not described anywhere this project has.
// * THE RATE: `decDigitsPerCycle` -- see its declaration.
// ---------------------------------------------------------------------
package StretchDecBox;

// >>> CHOSEN, not sourced. <<<  Digits processed per clock.  The 7030's
// serial arithmetic unit handled a decimal field a byte at a time, and
// the time that costs is ALREADY charged, from Perf. Char. Vol. 1 Table
// 3, by eboxClocks (StretchTiming.bsv: .6 us per byte with y = the byte
// size in decimal).  mkEBox takes the box's clocks OFF that budget
// (StretchCore's rl_exec_resume), so the box must fit inside the
// smallest one: 8 + 2 x 1 byte = 10 clocks.  Eight digits a clock is a
// pass of 4 clocks and a recomplemented subtraction 8, which fits; one
// digit a clock (32 or 64) would overrun every short field.  When a
// source for the SAU's decimal cycle is read this is the number to
// replace.  It must divide 32 (elaboration refuses one that does not).
Integer decDigitsPerCycle = 8;
Integer decDigits         = 32;

typedef struct {
  Bit#(128) a;     // 32 BCD digits, digit 0 in bits 3:0
  Bit#(128) b;
  Bool      sub;   // True: effective signs unlike, compute |a - b|
} DecReq deriving (Bits, Eq, FShow);

typedef struct {
  Bit#(128) r;     // the result magnitude, 32 BCD digits
  // like signs: the carry out of digit 31 (Lost Carry).
  // unlike signs: True if a >= b (end carry, no recomplement), False
  // if the result was recomplemented (b > a).
  Bool      carry;
} DecRsp deriving (Bits, Eq, FShow);

// ONE DECIMAL DIGIT STEP, shared by both passes so there is one
// statement of the digit arithmetic: binary add of two digits and a
// carry; above nine, subtract ten (add six, drop the fifth bit) and
// carry one.
function Tuple2#(Bit#(4), Bit#(1)) decDigitStep(Bit#(4) x, Bit#(4) y, Bit#(1) c);
  Bit#(5) s = zeroExtend(x) + zeroExtend(y) + zeroExtend(c);
  if (s > 9) return tuple2(truncate(s - 10), 1);
  else       return tuple2(truncate(s), 0);
endfunction

// The nines' complement of one digit.
function Bit#(4) nines(Bit#(4) d) = 4'd9 - d;

interface DecBox;
  method Action request(DecReq r);
  method Bool responseReady();
  // A VALUE, as mkDivBox's is: see that interface's note.
  method DecRsp response();
endinterface

typedef enum { DecIdle, DecAdd, DecRecomp, DecDone } DecState
  deriving (Bits, Eq, FShow);

(* synthesize *)
module mkDecBox(DecBox);
  // CREGS WITH THE PORT ASSIGNMENT AS THE SCHEDULE, for exactly the
  // reason mkDivBox gives (StretchDivBox.bsv): the rules use port 0 and
  // every method port 1, so the rules come before the methods and a
  // caller rule may poll, take and re-request in one clock.
  Reg#(DecState)  rg_state[2] <- mkCReg(2, DecIdle);
  // The operands leave at the bottom a pass-width at a time; the result
  // digits enter at the top, so after a pass `rg_r` holds all 32.
  Reg#(Bit#(128)) rg_a[2]     <- mkCReg(2, 0);
  Reg#(Bit#(128)) rg_b[2]     <- mkCReg(2, 0);
  Reg#(Bit#(128)) rg_r[2]     <- mkCReg(2, 0);
  Reg#(Bit#(1))   rg_c[2]     <- mkCReg(2, 0);
  Reg#(Bool)      rg_sub[2]   <- mkCReg(2, False);
  Reg#(Bool)      rg_carry[2] <- mkCReg(2, False);
  Reg#(Bit#(8))   rg_ctr[2]   <- mkCReg(2, 0);

  Integer passClocks = decDigits / decDigitsPerCycle;
  if (passClocks * decDigitsPerCycle != decDigits)
    error("mkDecBox: decDigitsPerCycle must divide 32");
  Integer w = 4 * decDigitsPerCycle;

  // ADD PASS: a + b (b already nines'-complemented for a subtraction,
  // with the initial carry one).
  rule rl_add (rg_state[0] == DecAdd);
    Bit#(128) a = rg_a[0];
    Bit#(128) b = rg_b[0];
    Bit#(1)   c = rg_c[0];
    Bit#(128) r = rg_r[0];
    for (Integer k = 0; k < decDigitsPerCycle; k = k + 1) begin
      match {.d, .c2} = decDigitStep(a[3:0], b[3:0], c);
      c = c2;
      a = a >> 4;
      b = b >> 4;
      r = { d, r[127:4] };
    end
    Bit#(8)   ctr = rg_ctr[0] - 1;
    DecState  st  = DecAdd;
    if (rg_ctr[0] == 1) begin
      rg_carry[0] <= (c == 1);
      if (rg_sub[0] && c == 0) begin
        // No end carry: a < b, and r is the tens' complement of b - a.
        // RECOMPLEMENT: one more pass of nines' complement plus one.
        a   = r;
        c   = 1;
        ctr = fromInteger(passClocks);
        st  = DecRecomp;
      end else
        st  = DecDone;
    end
    rg_a[0] <= a; rg_b[0] <= b; rg_c[0] <= c; rg_r[0] <= r;
    rg_ctr[0] <= ctr; rg_state[0] <= st;
  endrule

  rule rl_recomp (rg_state[0] == DecRecomp);
    Bit#(128) a = rg_a[0];
    Bit#(1)   c = rg_c[0];
    Bit#(128) r = rg_r[0];
    for (Integer k = 0; k < decDigitsPerCycle; k = k + 1) begin
      match {.d, .c2} = decDigitStep(nines(a[3:0]), 0, c);
      c = c2;
      a = a >> 4;
      r = { d, r[127:4] };
    end
    rg_a[0] <= a; rg_c[0] <= c; rg_r[0] <= r;
    rg_ctr[0] <= rg_ctr[0] - 1;
    if (rg_ctr[0] == 1) rg_state[0] <= DecDone;
  endrule

  // NO IMPLICIT CONDITIONS, for mkDivBox's reason (its interface note:
  // a guarded response() became the condition of the whole of
  // mkEBox.resume()).
  method Action request(DecReq q);
    Bit#(128) bc = q.b;
    if (q.sub)
      for (Integer k = 0; k < decDigits; k = k + 1)
        bc[4*k+3:4*k] = nines(q.b[4*k+3:4*k]);
    rg_a[1]     <= q.a;
    rg_b[1]     <= bc;
    rg_r[1]     <= 0;
    rg_c[1]     <= q.sub ? 1 : 0;
    rg_sub[1]   <= q.sub;
    rg_ctr[1]   <= fromInteger(passClocks);
    rg_state[1] <= DecAdd;
  endmethod

  method Bool responseReady() = (rg_state[1] == DecDone);

  method DecRsp response() = DecRsp { r: rg_r[1], carry: rg_carry[1] };
endmodule

// ---------------------------------------------------------------------
// mkDecBox's OWN TESTBENCH, in the same file, as mkCoreDivBoxTb is in
// StretchDivBox.bsv: the box is testable without instantiating storage.
//
// THE EXPECTATIONS ARE LITERALS, worked by hand from p.60's rule -- not
// computed by a second decimal adder in the testbench, which would be
// the box checking itself.  Each vector also asserts a LITERAL clock
// count: 4 for a pass, 8 when the subtraction recomplements.
//
// Vectors 0-4 ARE Reference Manual printed p.60's five ADD examples,
// with the accumulator as `a` and the storage operand shifted two digits
// (offset 8 bits) as `b`: 37600+ + 75679+, 45623+ + 53200-, 53200+ +
// 53200-, 53200- + 53200+, 53201+ + 53200-.
// ---------------------------------------------------------------------
typedef 9 NDecVec;

(* synthesize *)
module mkDecBoxTb(Empty);
  DecBox         box    <- mkDecBox;
  Reg#(Bit#(4))  idx    <- mkReg(0);
  Reg#(Bit#(8))  fails  <- mkReg(0);
  Reg#(Bool)     issued <- mkReg(False);
  Reg#(Bool)     done   <- mkReg(False);
  Reg#(Bit#(16)) clk    <- mkReg(0);
  Reg#(Bit#(16)) t0     <- mkReg(0);

  rule rl_clk; clk <= clk + 1; endrule

  function DecReq reqOf(Bit#(4) i) =
    case (i)
      // p.60 example 1: acc 37600+, operand 75679+: like signs.
      0: DecReq { a: 128'h37600, b: 128'h75679, sub: False };
      // example 2: acc 45623+, operand 53200-: unlike, a < b.
      1: DecReq { a: 128'h45623, b: 128'h53200, sub: True };
      // example 3: acc 53200+, operand 53200-: unlike, equal.
      2: DecReq { a: 128'h53200, b: 128'h53200, sub: True };
      // example 4: acc 53200-, operand 53200+: unlike, equal.
      3: DecReq { a: 128'h53200, b: 128'h53200, sub: True };
      // example 5: acc 53201+, operand 53200-: unlike, a > b.
      4: DecReq { a: 128'h53201, b: 128'h53200, sub: True };
      // 32 nines + 1: the carry out of digit 31 (Lost Carry).
      5: DecReq { a: 128'h99999999999999999999999999999999, b: 128'h1, sub: False };
      // a carry rippling across a pass boundary (digit 7 -> 8).
      6: DecReq { a: 128'h99999999, b: 128'h1, sub: False };
      // 0 - 1: recomplement to 1, across all 32 digits.
      7: DecReq { a: 128'h0, b: 128'h1, sub: True };
      // full width: 10^31 - 1 against 10^31 + ... a > b by one digit.
      default: DecReq { a: 128'h10000000000000000000000000000000,
                        b: 128'h00000000000000000000000000000001, sub: True };
    endcase;
  function DecRsp wantOf(Bit#(4) i) =
    case (i)
      0: DecRsp { r: 128'h113279, carry: False };
      1: DecRsp { r: 128'h7577,   carry: False };   // b - a, recomplemented
      2: DecRsp { r: 128'h0,      carry: True };
      3: DecRsp { r: 128'h0,      carry: True };
      4: DecRsp { r: 128'h1,      carry: True };
      5: DecRsp { r: 128'h0,      carry: True };
      6: DecRsp { r: 128'h100000000, carry: False };
      7: DecRsp { r: 128'h1,      carry: False };
      default: DecRsp { r: 128'h09999999999999999999999999999999, carry: True };
    endcase;
  function Bit#(16) clocksOf(Bit#(4) i) = (i == 1 || i == 7) ? 8 : 4;

  rule rl_issue (!done && !issued);
    box.request(reqOf(idx));
    issued <= True;
    t0 <= clk;
  endrule

  rule rl_collect (!done && issued && box.responseReady());
    let got  = box.response();
    let want = wantOf(idx);
    Bit#(16) took = clk - t0;
    if (got != want) begin
      $display("FAIL decbox[%0d]: r=%h carry=%0d, want r=%h carry=%0d",
               idx, got.r, got.carry, want.r, want.carry);
      fails <= fails + 1;
    end else if (took != clocksOf(idx)) begin
      $display("FAIL decbox[%0d] clocks = %0d, want %0d", idx, took, clocksOf(idx));
      fails <= fails + 1;
    end else
      $display("PASS decbox[%0d] r=%h carry=%0d in %0d clocks", idx, got.r, got.carry, took);
    issued <= False;
    if (idx == fromInteger(valueOf(NDecVec) - 1)) done <= True;
    else idx <= idx + 1;
  endrule

  rule rl_finish (done);
    if (fails == 0) $display("ALL TESTS PASSED");
    else $display("%0d TEST(S) FAILED", fails);
    $finish(0);
  endrule
endmodule

endpackage
