// >>> SUPERSEDED 2026-11-25 BY mkSAU (StretchSAU.bsv; docs/fidelity_plan.md
// A3 half (a)). <<<  Nothing imports this package or instantiates its
// module any more, and the suite no longer builds its testbench: the
// datapath, the vectors and the measured injections below were moved,
// unchanged in rate and value, into the serial arithmetic unit.  The file
// is kept, not deleted, until the owner approves its removal (AGENTS.md:
// deleting a file not created in the session is asked first).  The text
// below is as it stood.
//
// StretchCvtBox.bsv -- the RADIX CONVERTER for every radix conversion
// (CV, LCV, LTRCV, DCV), as a multi-cycle box.
//
// >>> WHY A BOX (AGENTS.md, "Idiomatic Bluespec") <<<  CONVERT DOUBLE
// (DCV, code 59) converts a 96-bit binary field to as many as 29 decimal
// digits, or up to 32 decimal digits to binary.  StretchALU's
// binaryToBcd did the first inline -- twenty-four 96-bit dividers in one
// combinational function, which its own note said "belongs on that
// list" of datapaths that must go multi-cycle.  DCV was not added to
// that list: it is the third box, beside mkDivBox and mkDecBox, with the
// same shape -- instantiated once in mkEBox, reached through execute()'s
// `NeedBox` bail, a request method, a responseReady poll and a response
// value, and execute() re-run with the answer.
//
// SINCE 2026-11-17 CV, LCV AND LTRCV USE IT TOO, and the inline
// binaryToBcd and bcdToBinary are deleted (docs/fpga_feasibility.md
// 10.6).  CV's 48 bits and LCV's and LTRCV's 64 are at most twenty
// digits; a decimal field of another byte size reaches the box as
// four-bit digits (StretchALU's decFieldDigits).  Every caller's budget
// in eboxClocks (DCV's decimal 18 clocks is the smallest of the four)
// holds the box's 6 and 4 clocks.
//
// ---------------------------------------------------------------------
// WHAT IT COMPUTES
// ---------------------------------------------------------------------
// Reference Manual 22-6530-2 printed p.74 (PDF 77), Convert Double:
// "A field from the accumulator is converted as an integer from binary
// to decimal or from decimal to binary depending on the setting of the
// radix modifier."  The box converts the MAGNITUDE; the caller chooses
// the field, the offset, the sign and the indicators.
//
//   * toDec: `v` is a binary integer (the caller gives 96 bits).  The
//     answer is its 32-digit BCD value, digit 0 in bits 3:0.  2^96 is
//     29 digits, so 32 hold every answer exactly; the caller keeps the
//     low 24 ("a maximum of 24 significant digits") and reads Partial
//     Field from the rest.  DOUBLE DABBLE, most significant bit first:
//     for each bit every digit of five or more gets three added, then
//     the whole is shifted left one with the bit coming in at the
//     bottom.  `cvtBitsPerCycle` bits a clock.
//   * !toDec: `v` is 32 BCD digits.  The answer is their binary value
//     (10^32 needs 107 bits; 128 hold it).  HORNER, most significant
//     digit first: r = 10r + d, `cvtDigitsPerCycle` digits a clock.
//     A "digit" above nine is taken at its binary value, as
//     bcdToBinary does; the manual defines no check (docs/
//     spec_decimal.md 1d).
//
// ---------------------------------------------------------------------
// THE RATES ARE CHOSEN, not sourced
// ---------------------------------------------------------------------
// mkEBox takes a box's clocks off the E-box budget (StretchCore's
// rl_exec_resume), so the box must finish inside DCV's budget, which is
// eboxClocks' DCV term (StretchTiming.bsv: 8 clocks binary-to-decimal, 6
// decimal-to-binary, from the Vol. 2 atlas page PDF 139).  Sixteen bits
// a clock is six clocks for 96 bits; eight digits a clock is four for
// 32.  Neither number is the SAU's; when a source for its conversion
// cycle is read, these are the two to replace.
package StretchCvtBox;

Integer cvtBinBits        = 96;
Integer cvtBitsPerCycle   = 16;
Integer cvtDigits         = 32;
Integer cvtDigitsPerCycle = 8;

typedef struct {
  Bool      toDec;   // True: binary -> decimal
  Bit#(128) v;       // toDec: the binary value (low 96 bits used);
                     // else 32 BCD digits, digit 0 in bits 3:0
} CvtReq deriving (Bits, Eq, FShow);

typedef struct {
  Bit#(128) r;       // toDec: 32 BCD digits; else the binary value
} CvtRsp deriving (Bits, Eq, FShow);

// One double-dabble step: adjust every digit of five or more by three,
// then shift the bit in.
function Bit#(128) dabble(Bit#(128) d, Bit#(1) b);
  for (Integer k = 0; k < 32; k = k + 1) begin
    Bit#(4) dg = d[4*k+3:4*k];
    if (dg >= 5) d[4*k+3:4*k] = dg + 3;
  end
  return { d[126:0], b };
endfunction

interface CvtBox;
  method Action request(CvtReq r);
  method Bool responseReady();
  // A VALUE, as mkDivBox's and mkDecBox's are (no implicit condition).
  method CvtRsp response();
endinterface

typedef enum { CvtIdle, CvtToDec, CvtToBin, CvtDone } CvtState
  deriving (Bits, Eq, FShow);

(* synthesize *)
module mkCvtBox(CvtBox);
  // CREGS WITH THE PORT ASSIGNMENT AS THE SCHEDULE, for mkDivBox's
  // reason: rules on port 0, methods on port 1.
  Reg#(CvtState)  rg_state[2] <- mkCReg(2, CvtIdle);
  Reg#(Bit#(128)) rg_src[2]   <- mkCReg(2, 0);   // bits/digits still to take, top first
  Reg#(Bit#(128)) rg_r[2]     <- mkCReg(2, 0);
  Reg#(Bit#(8))   rg_ctr[2]   <- mkCReg(2, 0);

  Integer decClocks = cvtBinBits / cvtBitsPerCycle;
  Integer binClocks = cvtDigits / cvtDigitsPerCycle;
  if (decClocks * cvtBitsPerCycle != cvtBinBits)
    error("mkCvtBox: cvtBitsPerCycle must divide 96");
  if (binClocks * cvtDigitsPerCycle != cvtDigits)
    error("mkCvtBox: cvtDigitsPerCycle must divide 32");

  rule rl_todec (rg_state[0] == CvtToDec);
    Bit#(128) s = rg_src[0];
    Bit#(128) r = rg_r[0];
    for (Integer k = 0; k < cvtBitsPerCycle; k = k + 1) begin
      r = dabble(r, s[95]);
      s = s << 1;
    end
    rg_src[0] <= s; rg_r[0] <= r;
    rg_ctr[0] <= rg_ctr[0] - 1;
    if (rg_ctr[0] == 1) rg_state[0] <= CvtDone;
  endrule

  rule rl_tobin (rg_state[0] == CvtToBin);
    Bit#(128) s = rg_src[0];
    Bit#(128) r = rg_r[0];
    for (Integer k = 0; k < cvtDigitsPerCycle; k = k + 1) begin
      r = (r << 3) + (r << 1) + zeroExtend(s[127:124]);
      s = s << 4;
    end
    rg_src[0] <= s; rg_r[0] <= r;
    rg_ctr[0] <= rg_ctr[0] - 1;
    if (rg_ctr[0] == 1) rg_state[0] <= CvtDone;
  endrule

  method Action request(CvtReq q);
    rg_src[1]   <= q.toDec ? (q.v & ((128'd1 << 96) - 1)) : q.v;
    rg_r[1]     <= 0;
    rg_ctr[1]   <= fromInteger(q.toDec ? decClocks : binClocks);
    rg_state[1] <= q.toDec ? CvtToDec : CvtToBin;
  endmethod

  method Bool responseReady() = (rg_state[1] == CvtDone);

  method CvtRsp response() = CvtRsp { r: rg_r[1] };
endmodule

// ---------------------------------------------------------------------
// mkCvtBox's OWN TESTBENCH, in the same file, as mkDecBoxTb is in
// StretchDecBox.bsv.  The expectations are LITERALS (the decimal ones
// are the number written out; the binary ones were computed with Python
// integers, not with a second converter in Bluespec), and each vector
// asserts a literal clock count: 6 binary-to-decimal, 4 back.
//
//   0  2^96 - 1 = 79228162514264337593543950335 (29 digits, the most)
//   1  zero
//   2  one
//   3  10^24, the first 25-digit value (DCV's Partial Field boundary)
//   4  10^24 - 1, twenty-four nines
//   5  32 nines to binary = 10^32 - 1 = (16)4EE2D6D415B85ACEF80FFFFFFFF
//   6  1 to binary
//   7  1234 to binary = (16)4D2
// ---------------------------------------------------------------------
typedef 8 NCvtVec;

(* synthesize *)
module mkCvtBoxTb(Empty);
  CvtBox         box    <- mkCvtBox;
  Reg#(Bit#(4))  idx    <- mkReg(0);
  Reg#(Bit#(8))  fails  <- mkReg(0);
  Reg#(Bool)     issued <- mkReg(False);
  Reg#(Bool)     done   <- mkReg(False);
  Reg#(Bit#(16)) clk    <- mkReg(0);
  Reg#(Bit#(16)) t0     <- mkReg(0);

  rule rl_clk; clk <= clk + 1; endrule

  function CvtReq reqOf(Bit#(4) i) =
    case (i)
      0: CvtReq { toDec: True,  v: 128'hFFFFFFFFFFFFFFFFFFFFFFFF };
      1: CvtReq { toDec: True,  v: 0 };
      2: CvtReq { toDec: True,  v: 1 };
      3: CvtReq { toDec: True,  v: 128'hD3C21BCECCEDA1000000 };
      4: CvtReq { toDec: True,  v: 128'hD3C21BCECCEDA0FFFFFF };
      5: CvtReq { toDec: False, v: 128'h99999999999999999999999999999999 };
      6: CvtReq { toDec: False, v: 1 };
      default: CvtReq { toDec: False, v: 128'h1234 };
    endcase;
  function Bit#(128) wantOf(Bit#(4) i) =
    case (i)
      0: 128'h79228162514264337593543950335;
      1: 0;
      2: 1;
      3: 128'h1000000000000000000000000;
      4: 128'h999999999999999999999999;
      5: 128'h4EE2D6D415B85ACEF80FFFFFFFF;
      6: 1;
      default: 128'h4D2;
    endcase;
  function Bit#(16) clocksOf(Bit#(4) i) = (i <= 4) ? 6 : 4;

  rule rl_issue (!done && !issued);
    box.request(reqOf(idx));
    issued <= True;
    t0 <= clk;
  endrule

  rule rl_collect (!done && issued && box.responseReady());
    Bit#(128) got = box.response().r;
    Bit#(16) took = clk - t0;
    if (got != wantOf(idx)) begin
      $display("FAIL cvtbox[%0d]: r=%h, want %h", idx, got, wantOf(idx));
      fails <= fails + 1;
    end else if (took != clocksOf(idx)) begin
      $display("FAIL cvtbox[%0d] clocks = %0d, want %0d", idx, took, clocksOf(idx));
      fails <= fails + 1;
    end else
      $display("PASS cvtbox[%0d] r=%h in %0d clocks", idx, got, took);
    issued <= False;
    if (idx == fromInteger(valueOf(NCvtVec) - 1)) done <= True;
    else idx <= idx + 1;
  endrule

  rule rl_finish (done);
    if (fails == 0) $display("ALL TESTS PASSED");
    else $display("%0d TEST(S) FAILED", fails);
    $finish(0);
  endrule
endmodule

endpackage
