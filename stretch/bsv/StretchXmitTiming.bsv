// StretchXmitTiming.bsv -- the time of a TRANSMIT (T, TB, TI, TBI), by
// DESTINATION (docs/fidelity_plan.md A7, 2026-11-27).
//
// This package is the clock of the I-box's transmit loop and nothing
// else: the constants, the charge they make, and the one-counter module
// (mkXmitPacer) that holds each word of the loop to its period.  The
// words themselves are moved by mkXmitBox (StretchIBox.bsv), which owns
// a pacer.  It imports StretchTypes only, so its bench (mkXmitTimingTb,
// tests/run_xmit_timing_test.sh) builds in seconds.
//
// >>> WHAT THE 7030 CHARGES: THE DESTINATION, NOT THE SOURCE. <<<
// Perf. Char. Vol. 1 Table 9, "I-BOX TIMES - TRANSMIT INSTRUCTIONS"
// (printed p.3-14, PDF 32; no text layer, read on the page image):
//
//     T (EM -> EM)   1.2 usec + dec + LA dr   loop 3.0 usec   term 3.6 usec
//     T (EM -> XS)   1.2 usec + dec + LA dr   loop 4.2 usec   term  .6 usec
//     T (XS -> EM)   1.2 usec + dec + LA dr   loop 3.0 usec   term 3.6 usec
//     T (XS -> XS)   1.2 usec + dec + LA dr   loop 4.2 usec   term  .6 usec
//     T (IR -> EM)   1.2 usec + dec + LA dr   loop 7.2 usec   term 3.6 usec
//     T (IR -> XS)   1.2 usec + dec + LA dr   loop 7.2 usec   term  .6 usec
//     Note: Transmit to EM and IR identical in time.
//
// The loop time is set by where the word GOES: 3.0 us = 10 clocks to core
// (EM) or to an internal register (IR, "identical"), 4.2 us = 14 clocks
// to index storage (XS), whichever of EM and XS it came from.  The
// atlas measured the same thing (Vol. 2 PDF 107, printed 100, "TRANSMIT";
// least squares on atlas_data's transcription, 2026-11-27): every T
// column is a straight line in the word count n to within 0.13 clock,
// slope 10.03-10.05 clocks into EXTERNAL or INTERNAL, 14.06 into I-BOX,
// whether the source is EXTERNAL or I-BOX.
//
// >>> THE MODEL USED TO CHARGE THE SOURCE READ. <<<  Before this
// package, rl_xmit read a word, waited for the response and wrote it, so
// a word cost what the READ cost: 2 clocks from index storage, 10 or 17
// from core (17 when the next read waited out the previous write's unit
// cycle).  Its fixed part was budgetClocks' 2 * 7 + the dispatch clock =
// 15, from any source to any destination.  docs/atlas_oracle.md "Where
// the model is furthest off" item 2 has the diagnosis: T median -48 (down
// to -152), TI -29, 0 of 58 cells within 3 clocks.
//
// >>> WHAT IS NOT CHARGED HERE, AND WHY. <<<
// - AN INTERNAL-REGISTER SOURCE.  Table 9 gives IR -> EM and IR -> XS a
//   7.2 us (24-clock) loop; PDF 107 measures 22 (int_ext, int_int) and
//   18 (int_ibox), with a fixed part of 28.  The atlas generator does not
//   build the internal columns, so no number of the model's could be
//   checked against either.  An IR source is charged as an EM source.
//   OPEN, recorded in fidelity_plan.md A7.
// - SWAP.  Table 9 (cont'd) (printed p.3-15, PDF 33) prints swap times,
//   but the atlas has no swap page and mkXmitBox's swap is a three-phase
//   exchange that is not this loop.  A SWAP keeps budgetClocks' charge and
//   its old per-word time, unchanged.
// - PDF 106's flat TI columns (every TI whose source is I-BOX or INTERNAL
//   prints its 1WD figure at every n).  UNEXPLAINED; the generator does
//   not run them above 1WD (atlas_oracle.md item 2).

package StretchXmitTiming;

import StretchTypes::*;

// What a transmit tells the instruction unit about its time, decided in
// the Transmit arm (StretchExecute) BEFORE it writes: the receiving
// address of the FIRST word, and whether the count was immediate.  It is
// decided there, not recomputed later, because a transmit may overwrite
// the index register its own address was modified by.
typedef struct {
  Bool     immediate;   // TI / TBI: the count is instruction bits 51-54
  WordAddr dst;         // the first word's receiving address
} XmitTiming deriving (Bits, Eq, FShow);

// Index storage is words 16-31 (Reference Manual printed p.20, "index
// registers ... addresses 16 through 31").  Everything else, the internal
// registers 0-15 included, takes core's time (Table 9's note).
function Bool xmitToIndexStorage(WordAddr a) = (a >= 16) && (a <= 31);

// THE LOOP, per word.  Table 9: 3.0 us to EM and IR, 4.2 us to XS.
Bit#(16) xmitLoopToCore  = 10;
Bit#(16) xmitLoopToIndex = 14;
function Bit#(16) xmitLoopClocks(WordAddr dst) =
  xmitToIndexStorage(dst) ? xmitLoopToIndex : xmitLoopToCore;

// THE FIXED PART, F, for T: 38 clocks to core or internal, 32 to index
// storage (PDF 107's fits: 38.15-38.21 and 32.13-32.17).  Composed as
//   set-up        1.2 us = 4  (Table 9)
//   decoding      0.6 us = 2  (Table 9's "+ dec"; Vol. 1 printed p.3-18,
//                              PDF 36: "The decoding time of I-box
//                              instructions is 0.6 us")
//   termination   3.6 us = 12 to EM, 0.6 us = 2 to XS (Table 9)
//   remainder     20 to EM, 24 to XS -- FIT to PDF 107.  It holds Table 9's
//                 "LA dr", which the table prints with no number (PDF 105,
//                 printed 98: "LA is emptied before the actual transmission
//                 of information"), and whatever else GENER's back-to-back
//                 sequence costs.  The two remainders differ, so Table 9's
//                 terminations are not wholly serial in sequence (DERIVED).
Bit#(16) xmitSetupClocks      = 4;
Bit#(16) xmitDecodeClocks     = 2;
Bit#(16) xmitTermToCore       = 12;
Bit#(16) xmitTermToIndex      = 2;
Bit#(16) xmitFitRemainderCore  = 20;   // FIT, PDF 107
Bit#(16) xmitFitRemainderIndex = 24;   // FIT, PDF 107

// TI IS 2 CLOCKS CHEAPER (PDF 106, printed 99, "TRANSMITI", against PDF
// 107: fixed parts 36.15 against 38.19 to EXTERNAL, 30.19 against 32.17
// to I-BOX, slopes equal).  DERIVED: the one I-box cycle (0.6 us) that
// fetches the index word holding the count -- Blosk TR00.722 Fig. 9 (printed
// p.36, PDF 38), "XF/Z_J", and printed p.35 (PDF 37): "After decoding,
// the first cycle fetches the index word that contains the count".  An
// immediate count has no such word.  Table 9 (cont'd)'s note says the
// immediate option does "not affect the timing"; the measurement is taken
// over the table.
Bit#(16) xmitCountWordClocks = 2;

function Bit#(16) xmitFixedClocks(XmitTiming t) =
  xmitSetupClocks + xmitDecodeClocks
  + (xmitToIndexStorage(t.dst) ? xmitTermToIndex + xmitFitRemainderIndex
                               : xmitTermToCore  + xmitFitRemainderCore)
  - (t.immediate ? xmitCountWordClocks : 0);

// THE I-BOX BUDGET A TRANSMIT LEAVES AT ITS DISPATCH: F plus the first
// word's loop, less the dispatch clock the instruction unit spends before
// `ibusy` starts counting (the same clock budgetClocks' 2*7 = 14 sat on
// top of, measured 15.02 at 1WD).  The words after the first are mkXmitBox's,
// each held to its own xmitLoopClocks by a pacer, and `ibusy` does not
// count down while they move (StretchCore's note on `ib`), so a transmit
// of n words costs F + sum of the n loops, the first word's destination
// setting F.  CHOSEN: a run that crosses from index storage into core
// (word 31 to 32) takes F from its first word and each loop from its own.
function Bit#(16) xmitFirstBudget(XmitTiming t) =
  xmitFixedClocks(t) + xmitLoopClocks(t.dst) - 1;

// ---- The loop's period: one counter ----
//
// `startWord` starts a word's period when its read is issued; `due` is True
// from the clock the period has run out.  A word issued at clock c may
// be written at c + L - 1 at the earliest, and the next word's read then
// issues at c + L: L clocks a word.  L IS A FLOOR, NOT A FIXED RATE: a
// read that takes longer (a busy unit) still holds the write.  Blosk Fig.
// 9 starts the next fetch before the previous store has left, which is
// why the 7030's rate is the loop's and not the memory's; the model
// issues the next read at the start of the period, and where the memory
// is still slower than the period the memory sets the rate (recorded in
// fidelity_plan.md A7, measured there).
interface XmitPacer;
  method Action startWord(WordAddr dst);
  method Bool   due;
endinterface

module mkXmitPacer(XmitPacer);
  Reg#(Bit#(16))   left   <- mkReg(0);
  RWire#(WordAddr) beginW <- mkRWire;

  (* fire_when_enabled, no_implicit_conditions *)
  rule rl_tick;
    if (beginW.wget matches tagged Valid .d)
      left <= xmitLoopClocks(d) - 2;   // due at c + L - 1 (see above)
    else if (left != 0)
      left <= left - 1;
  endrule

  method Action startWord(WordAddr dst);
    beginW.wset(dst);
  endmethod
  method Bool due = (left == 0);
endmodule

// ---- The bench: one vector per destination, literal Table 9 / PDF 107 ----
//
// Run by tests/run_xmit_timing_test.sh.  Part 1 checks the charge
// (xmitLoopClocks, xmitFixedClocks, xmitFirstBudget) for T and TI into
// core, an internal register, and index storage, and both edges of index
// storage (15, 16, 31, 32), against literal numbers.  Part 2 begins a
// period into core and one into index storage on a pacer and checks `due`
// every clock against a literal table.
//
// INJECTIONS, 2026-11-27, each made, observed and reversed by the inverse
// sed (the file was new, so the check was a grep of the restored line and
// a green rerun):
//   A. xmitLoopToIndex 14 -> 10: FAIL xmit_charge[2] [3] [7] [8] [11] and
//      xmit_pace[19]-[22] (due one period early); nothing else.
//   B. xmitToIndexStorage's upper edge 31 -> 32: FAIL xmit_charge[9] only.
//   C. xmitCountWordClocks 2 -> 0 (TI charged as T): FAIL xmit_charge[1]
//      [3] [5] [10] [11], the five immediate vectors; nothing else.
//   D. the pacer's start value L - 2 -> L - 1 (a period one clock long):
//      FAIL xmit_pace[9] and [23] only.
// The deck-level injection (the pacer's stall disabled in mkXmitBox) is
// recorded at the two transmit_time decks' runs in tests/run_tests.sh.
typedef 12 NXmitVec;

module mkXmitTimingTb(Empty);
  Reg#(Bit#(8))  idx   <- mkReg(0);
  Reg#(Bit#(8))  fails <- mkReg(0);
  Reg#(Bit#(8))  clk   <- mkReg(0);
  XmitPacer      pacer <- mkXmitPacer;

  // (destination, immediate) -> (loop, fixed, first budget)
  function Tuple2#(WordAddr, Bool) inOf(Bit#(8) i) =
    case (i)
      0:  tuple2(18'o10000, False);   // T  to core:   L 10, F 38
      1:  tuple2(18'o10000, True);    // TI to core:   L 10, F 36
      2:  tuple2(20,        False);   // T  to XS:     L 14, F 32
      3:  tuple2(20,        True);    // TI to XS:     L 14, F 30
      4:  tuple2(8,         False);   // T  to IR (8, $L): as core
      5:  tuple2(8,         True);    // TI to IR
      6:  tuple2(15,        False);   // the edge below XS: core
      7:  tuple2(16,        False);   // the first XS word
      8:  tuple2(31,        False);   // the last XS word
      9:  tuple2(32,        False);   // the first core word above XS
      10: tuple2(18'o50000, True);
      default: tuple2(30,   True);
    endcase;
  function Tuple3#(Bit#(16), Bit#(16), Bit#(16)) wantOf(Bit#(8) i) =
    case (i)
      0, 4, 6, 9: tuple3(10, 38, 47);
      1, 5, 10:   tuple3(10, 36, 45);
      2, 7, 8:    tuple3(14, 32, 45);
      default:    tuple3(14, 30, 43);   // 3, 11
    endcase;

  rule rl_charge (idx < fromInteger(valueOf(NXmitVec)));
    match {.d, .imm} = inOf(idx);
    XmitTiming t = XmitTiming { immediate: imm, dst: d };
    let got  = tuple3(xmitLoopClocks(d), xmitFixedClocks(t), xmitFirstBudget(t));
    let want = wantOf(idx);
    if (got == want) $display("PASS xmit_charge[%0d]", idx);
    else begin
      $display("FAIL xmit_charge[%0d]: got ", idx, fshow(got));
      $display("                    want ", fshow(want));
      fails <= fails + 1;
    end
    idx <= idx + 1;
  endrule

  // Part 2, clock by clock.  Clock 0 begins a word into core (L 10): due
  // is False at clocks 1-8 and True at clock 9 = c + L - 1.  Clock 10
  // begins one into index storage (L 14): False at 11-22, True at 23.
  // Clock 0's and clock 10's own `due` read the counter before the begin
  // (it is 0, idle), and are not checked.
  Bit#(8) nPacer = 26;
  rule rl_pace (idx == fromInteger(valueOf(NXmitVec)) && clk < nPacer);
    if (clk == 0)  pacer.startWord(18'o10000);
    if (clk == 10) pacer.startWord(20);
    Bool want = (clk == 9) || (clk == 23) || (clk >= 24);
    if (clk != 0 && clk != 10) begin
      if (pacer.due == want) $display("PASS xmit_pace[%0d] due=%0d", clk, pacer.due);
      else begin
        $display("FAIL xmit_pace[%0d]: due=%0d, want %0d", clk, pacer.due, want);
        fails <= fails + 1;
      end
    end
    clk <= clk + 1;
  endrule

  rule rl_finish (idx == fromInteger(valueOf(NXmitVec)) && clk == nPacer);
    if (fails == 0) $display("ALL TESTS PASSED");
    else $display("%0d TEST(S) FAILED", fails);
    $finish(0);
  endrule
endmodule

endpackage
