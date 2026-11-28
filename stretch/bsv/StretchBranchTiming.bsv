// StretchBranchTiming.bsv -- the I-box time of the half-word branches the
// I-box resolves itself: COUNT AND BRANCH (CB, CBZ and their +/-/H forms)
// and BRANCH ON an INDEX INDICATOR (BXL, BZXL, ... "Bind for XF, XVLZ,
// XVZ, XVGZ, XCZ, XL, XE, XH", Perf. Char. Vol. 1 printed p.3-23 item 7,
// PDF 41).  docs/fidelity_plan.md A7 part 2, 2026-11-28.
//
// This package is a clock table and nothing else: constants and one pure
// function, charged by StretchCore's iboxBudget at both places an I-box
// instruction completes.  It imports StretchTypes only, so its bench
// (mkBranchTimingTb, tests/run_branch_timing_test.sh) builds in seconds.
// Clocks are 0.3 us (docs/clock_unit.md).  The model's period for an
// I-box instruction is its budget plus the dispatch clock (StretchCore
// rl_prepare: the instruction completes in the dispatch clock and `ibusy`
// counts the budget after it), so a page figure of P clocks is a budget
// of P - 1.
//
// >>> WHAT THE PAGES PRINT. <<<
// Vol. 1 Table 8, "I-BOX TIMES - INDEX BRANCHES" (printed p.3-14, PDF 32;
// page image):  CB (Successful) 4.2 usec + dec, CB (Unsuccessful) 3.6
// usec + dec, "dec" = 0.6 us (printed p.3-18, PDF 36): 16 and 14 clocks.
// Vol. 2 PDF 112 (printed 105), "BRANCHING CB BIND", read on the page
// image; CONSEC and NONCON print the same figure on every row:
//
//                     SUCC   UNSUCC   ix SUCC  ix UNSUCC   (us; clocks)
//     CB CBZ (+-H)    4.82   4.52     5.12     5.12        16.07 15.07 17.07 17.07
//     BXL BZXL        4.52   2.26     4.67     2.86        15.07  7.53 15.57  9.53
//     BAL BZAL       19.78   7.20    20.08     7.21        65.93 24.00 66.93 24.03
//
// ("ix" = BRANCH ADDRESS INDEX, the right-hand four columns, printed
// p.104, PDF 111.)
//
// >>> CB. <<<
// - NOT TAKEN: Table 8's 14 clocks, and the page's 15.07 is 14 + the
//   dispatch clock, as every I-box immediate on PDF 109 is (LVI, V+I ...:
//   Table 5's 2.4 + dec = 10, printed 3.31 us = 11.03).  Budget 14:
//   unchanged from budgetClocks' 2 * 7.
// - TAKEN: Table 8's 16 clocks, and the page prints 16.07, NOT 16 + the
//   dispatch clock.  TR00.722 printed p.35 (PDF 37) says why the
//   preparation clock is not added: the branch-address fetch is started
//   in the second cycle of the CB, so "the new instruction word has
//   arrived and been checked by the time the CB instruction is completely
//   executed.  The normal instruction preparation is restarted
//   immediately".  So the taken CB's 16 clocks run from its own dispatch
//   clock: a budget of 15.  RECONSTRUCTION of which clock overlaps; the
//   16 is Table 8's and the page's.
// - INDEXED: the page prints +2.00 clocks not taken (15.07 -> 17.07) and
//   +1.00 taken (16.07 -> 17.07).  The 2 is the page's own columns (BXL's
//   not-taken pair, 7.53 -> 9.53, is the same 2).  The sentence nearest to
//   it, "each indexing operation requires 0.6 us" (printed p.3-18, PDF
//   36), is written of VFL decoding, so it is cited as consistent, not as
//   the source.  Taken, the index is not additive: the page fits a FLOOR,
//   budget = max(not-taken budget, 15) -- the branch takes the longer of
//   its own work and Table 8's 16 clocks to the new instruction --
//   unindexed max(14, 15) = 15, indexed max(16, 15) = 16.  The floor form
//   is RECONSTRUCTION; it reproduces all four CB cells.
// - CBR: NOT CHANGED (Table 8's CBR rows stay budgetClocks' 12 / 11
//   cycles).  The atlas generator does not build the CBR rows (the refill
//   word is not described, printed p.104), so no number here could be
//   checked against them.
//
// >>> BXL: AN INDEX-INDICATOR BRANCH DOES NOT LOAD THE FOUR LEVELS. <<<
// No table in Vol. 1 has a Bind row.  The model charged every branch on
// indicator 6 cycles, "Blosk fig.10: decode + 5 execution cycles": TR00.722
// Fig. 10 (printed p.38, PDF 40), whose five cycles are a test fetch and
// the four look-ahead loads OP, F, ST, BR of a branch the I-box cannot
// decide.  An index-indicator branch is not that: "If it were [an index
// result indicator], we would not have to guess but could test for the
// branch in the I unit's updated indicator register" (printed p.37, PDF
// 39), and it is "executed entirely within the I-box" (Perf. Char.
// printed p.3-23 item 7).  So Fig. 10 does not time it.  What does is a
// FIT to PDF 112's four BXL cells, with nothing held out:
// - NOT TAKEN: budget 6 (period 7 against 7.53), the I-box floor of Table
//   7's NOP, 1.2 + dec (printed p.3-13, PDF 31), CHOSEN as the analogy: a
//   decode and a test, no fetch and no level.  The page's half clock is
//   not chased (a figure that is not a whole number of clocks is not
//   budget-bound).
// - INDEXED NOT TAKEN: + 2, CB's term (period 9 against 9.53).
// - TAKEN: budget 14 (period 15 against 15.07), the 3.6 + dec of Table 7's
//   B, with the dispatch clock ADDED -- unlike CB's, whose 16 the page
//   prints without it.  No source says why the two differ; it is the
//   fit.  With CB's floor form, max(not-taken, 14), so indexed is also 14
//   (period 15 against 15.57).
//
// >>> BAL (an arithmetic indicator): NOT HERE. <<<  The guessed branch,
// its four levels and the wrong-way recovery are StretchCore's
// (rl_prepare's guess arm, rl_au_remove, rl_recover).  No page decomposes
// PDF 112's 24 clocks not taken or the 42 more a wrong guess costs, and
// the page does not spell out the ARITH RESULT IND environment; recorded
// in fidelity_plan.md A7, the model left as it was.

package StretchBranchTiming;

import StretchTypes::*;

// Which I-box branch, classified by the caller (StretchCore, which has
// StretchIBox's indexIndicator).
typedef enum { BtCountBranch, BtIndexIndicator } BranchTimingKind deriving (Bits, Eq, FShow);

// The terms, in clocks.
Bit#(16) cbNotTakenClocks   = 14;  // Table 8 CB (Unsuccessful) 3.6 + dec
Bit#(16) cbTakenClocks      = 16;  // Table 8 CB (Successful) 4.2 + dec, from the dispatch clock
Bit#(16) branchIndexClocks  = 2;   // PDF 112 BRANCH ADDRESS INDEX, not taken
Bit#(16) bxlNotTakenClocks  = 6;   // FIT, PDF 112 BXL; Table 7 NOP's 1.2 + dec
Bit#(16) bxlTakenClocks     = 15;  // FIT, PDF 112 BXL 15.07: Table 7 B's 3.6 + dec (14) + the dispatch clock

// The budget `ibusy` counts after the dispatch clock.
function Bit#(16) branchBudget(BranchTimingKind k, Bool indexed, Bool taken);
  Bit#(16) nt = ((k == BtCountBranch) ? cbNotTakenClocks : bxlNotTakenClocks)
                + (indexed ? branchIndexClocks : 0);
  Bit#(16) tk = ((k == BtCountBranch) ? cbTakenClocks : bxlTakenClocks) - 1;
  return taken ? max(nt, tk) : nt;
endfunction

// >>> THE BENCH, mkBranchTimingTb (tests/run_branch_timing_test.sh). <<<
// Eight literal vectors, every (kind, indexed, taken), each the budget
// that gives PDF 112's period with the dispatch clock: CB 14 / 15 / 16 /
// 16 (periods 15, 16, 17, 17 against 15.07, 16.07, 17.07, 17.07), BXL
// 6 / 14 / 8 / 14 (7, 15, 9, 15 against 7.53, 15.07, 9.53, 15.57).
// INJECTIONS, observed 2026-11-28, each reverted by the inverse patch:
//   cbTakenClocks 16 -> 17 (the dispatch clock added to Table 8's 16):
//     FAIL [1] only (16 for 15; [3] is max(16, 16) either way).
//   branchIndexClocks 2 -> 0 (no branch-address index term):
//     FAIL [2] [3] [6] (14, 15, 6).
//   bxlNotTakenClocks 6 -> 12 (the old flat "decode + 5" of Fig. 10):
//     FAIL [4] [6] (12, 14).
//   an additive taken index, branchBudget's `max(nt, tk)` -> `tk +
//   (indexed ? branchIndexClocks : 0)`:  FAIL [3] (17) and [7] (16).
Integer nBranchVec = 8;

module mkBranchTimingTb(Empty);
  Reg#(Bit#(8)) idx   <- mkReg(0);
  Reg#(Bit#(8)) fails <- mkReg(0);

  // vector i: kind = i[2] (0 CB, 1 BXL), indexed = i[1], taken = i[0]
  function Bit#(16) wantOf(Bit#(8) i) =
    case (i)
      0: 14;  1: 15;  2: 16;  3: 16;     // CB
      4: 6;   5: 14;  6: 8;   default: 14;   // BXL
    endcase;

  rule rl_charge (idx < fromInteger(nBranchVec));
    BranchTimingKind k = (idx[2] == 1) ? BtIndexIndicator : BtCountBranch;
    Bit#(16) got = branchBudget(k, idx[1] == 1, idx[0] == 1);
    if (got == wantOf(idx))
      $display("PASS branch_budget[%0d] ", idx, fshow(k), " indexed=%0d taken=%0d -> %0d",
               idx[1], idx[0], got);
    else begin
      $display("FAIL branch_budget[%0d] ", idx, fshow(k), " indexed=%0d taken=%0d: got %0d, want %0d",
               idx[1], idx[0], got, wantOf(idx));
      fails <= fails + 1;
    end
    idx <= idx + 1;
  endrule

  rule rl_finish (idx == fromInteger(nBranchVec));
    if (fails == 0) $display("ALL TESTS PASSED");
    else $display("%0d TEST(S) FAILED", fails);
    $finish(0);
  endrule
endmodule

endpackage
