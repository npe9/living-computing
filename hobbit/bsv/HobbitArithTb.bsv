// HobbitArithTb.bsv -- the area re-implementations of the EU's multiply
// and divide (docs/fpga_area.md, milestone 1) against the forms they
// replaced, which stay in HobbitCore.bsv as references:
//
//   * divUnit(sgn, a, b), one 32-bit unsigned restoring divider on the
//     operands' magnitudes, against divSigned (the former 64-bit signed
//     division plus multiply-back) for DIV/REM, and against bsc's own
//     `/` and `%` for UDIV/UREM;
//   * mulArith (one 32 x 32 product, the signed one derived from it)
//     against mulArithRef (two 64 x 64 products), for every width the
//     datapath asks for (1, 2, 4 bytes), result and both flags.
//
// Operands: every pair of a 34-value edge set (0, +-1, +-2, the
// extremes, powers of two either side, byte and half-word bounds), then
// N_RANDOM pairs from two 32-bit LFSRs, one per clock: the raw LFSR pair
// when bit 3 of the count is set, otherwise a pair with its magnitudes
// shrunk (a >> k, and b >> j on odd counts) and its signs flipped by
// bits 1 and 2, so that small quotients and small divisors are hit as
// often as large ones.  b == 0 is skipped for division: the datapath
// raises the exception and never uses the result.
//
// Run: bsv/run_arith.sh (tests/run_tests.sh).  Result, 2026-11-24:
// "SUMMARY arith: 401156 operand pairs, 0 failures".  Discriminating,
// OBSERVED 2026-11-24: with divUnit's remainder sign taken from the
// divisor (`na ? -ur : ur` made `nb ? -ur : ur`), 192971 failing checks,
// every one a "FAIL rem" line; with mulArith's correction for a negative
// b dropped (`((b[31] == 1'b1) ? {a, 32'd0} : 64'd0)` made `64'd0`),
// 33616 failing checks, every one a "FAIL mul" line; rc=1 both times.
// Each was reverted from a copy of the file, which compared identical.
package HobbitArithTb;

import HobbitTypes::*;
import HobbitCore::*;

typedef 400000 N_RANDOM;

function Word edgeVal(Bit#(6) i);
  case (i)
    0: return 32'h00000000;
    1: return 32'h00000001;
    2: return 32'hFFFFFFFF;
    3: return 32'h00000002;
    4: return 32'hFFFFFFFE;
    5: return 32'h80000000;
    6: return 32'h7FFFFFFF;
    7: return 32'h80000001;
    8: return 32'h7FFFFFFE;
    9: return 32'h00000003;
    10: return 32'hFFFFFFFD;
    11: return 32'h00000007;
    12: return 32'hFFFFFFF9;
    13: return 32'h0000007F;
    14: return 32'h00000080;
    15: return 32'hFFFFFF80;
    16: return 32'hFFFFFF7F;
    17: return 32'h000000FF;
    18: return 32'h00007FFF;
    19: return 32'h00008000;
    20: return 32'hFFFF8000;
    21: return 32'hFFFF7FFF;
    22: return 32'h0000FFFF;
    23: return 32'h00010000;
    24: return 32'hFFFF0000;
    25: return 32'h40000000;
    26: return 32'hC0000000;
    27: return 32'h55555555;
    28: return 32'hAAAAAAAA;
    29: return 32'h12345678;
    30: return 32'hEDCBA988;
    31: return 32'h0000000A;
    32: return 32'hFFFFFFF6;
    33: return 32'h00010001;
    default: return 0;
  endcase
endfunction

function Word lfsr(Word x) =
  { x[30:0], x[31] ^ x[21] ^ x[1] ^ x[0] };

(* synthesize *)
module mkHobbitArithTb(Empty);
  Reg#(Bit#(6)) ei <- mkReg(0);
  Reg#(Bit#(6)) ej <- mkReg(0);
  Reg#(Bool) edges <- mkReg(True);
  Reg#(Word) ra <- mkReg(32'h1D872B41);
  Reg#(Word) rb <- mkReg(32'h6C1F0A93);
  Reg#(Bit#(32)) n <- mkReg(0);
  Reg#(Bit#(32)) checks <- mkReg(0);
  Reg#(Bit#(32)) fails <- mkReg(0);

  function ActionValue#(Bit#(32)) check(Word a, Word b) =
    actionvalue
      Bit#(32) f = 0;
      // Bluesim evaluates a `/` whatever guards it, and a C++ division by
      // zero is undefined: the compiler may then assume the divisor is
      // nonzero and fold the guard away (observed here: b == 0 tested
      // false for b = 0).  So the references never see a zero divisor.
      Bool nz = (b != 32'd0);
      Word bs = nz ? b : 32'd1;
      match { .q, .r, .o } = divSigned(a, bs);
      match { .sq, .sr } = divUnit(True, a, bs);
      match { .uq, .ur } = divUnit(False, a, bs);
      Word wq = a / bs;
      Word wr = a % bs;
      if (nz) begin
        if (sq != q) begin
          $display("FAIL div a=%08x b=%08x got %08x want %08x", a, b, sq, q);
          f = f + 1;
        end
        if (sr != r) begin
          $display("FAIL rem a=%08x b=%08x got %08x want %08x", a, b, sr, r);
          f = f + 1;
        end
        if (uq != wq) begin
          $display("FAIL udiv a=%08x b=%08x got %08x want %08x", a, b, uq, wq);
          f = f + 1;
        end
        if (ur != wr) begin
          $display("FAIL urem a=%08x b=%08x got %08x want %08x", a, b, ur, wr);
          f = f + 1;
        end
      end
      for (Integer k = 0; k < 3; k = k + 1) begin
        Word sz = (k == 0) ? 1 : ((k == 1) ? 2 : 4);
        let m = mulArith(a, b, sz);
        let w = mulArithRef(a, b, sz);
        if ((m.r != w.r) || (m.c != w.c) || (m.v != w.v)) begin
          $display("FAIL mul a=%08x b=%08x sz=%0d got %08x c%0d v%0d want %08x c%0d v%0d",
                   a, b, sz, m.r, pack(m.c), pack(m.v), w.r, pack(w.c), pack(w.v));
          f = f + 1;
        end
      end
      return f;
    endactionvalue;

  rule edgePairs (edges);
    let f <- check(edgeVal(ei), edgeVal(ej));
    fails <= fails + f;
    checks <= checks + 1;
    if (ej == 33) begin
      ej <= 0;
      if (ei == 33) edges <= False; else ei <= ei + 1;
    end else
      ej <= ej + 1;
  endrule

  rule randomPairs (!edges && n < fromInteger(valueOf(N_RANDOM)));
    Word a = ra >> ra[4:0];
    Word b = rb >> (n[0] == 1'b1 ? rb[9:5] : 5'd0);
    Word a2 = (n[1] == 1'b1) ? -a : a;
    Word b2 = (n[2] == 1'b1) ? -b : b;
    // One check per clock: the raw pair when n[3] is set, otherwise the
    // shrunk and sign-flipped pair.
    Bool raw = (n[3] == 1'b1);
    let f <- check(raw ? ra : a2, raw ? rb : b2);
    fails <= fails + f;
    checks <= checks + 1;
    ra <= lfsr(ra);
    rb <= lfsr(lfsr(rb));
    n <= n + 1;
  endrule

  rule done (!edges && n == fromInteger(valueOf(N_RANDOM)));
    $display("SUMMARY arith: %0d operand pairs, %0d failures", checks, fails);
    if (fails != 0) $display("FAIL arith");
    $finish(0);
  endrule
endmodule

endpackage
