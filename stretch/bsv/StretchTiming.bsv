// StretchTiming.bsv
//
// The instruction-unit and E-box time budgets, as pure tables (the
// EX_ALU_functions shape: combinational helpers as plain functions,
// not module state). Moved out of StretchCore in the idiomatic-Bluespec
// rewrite step 5b (docs/microarchitecture_plan.md §1c); the numbers and
// their sources are unchanged.

package StretchTiming;

import StretchTypes::*;
import StretchDecode::*;   // decodeHalfWord for SIC's inner half-word
import StretchVFL::*;      // effLength/effByteSize for the VFL time budget

// ---- Stage 2b: instruction-unit timing (docs/microarchitecture_plan.md
// §6a). Each instruction carries a time budget in clocks (one clock =
// 0.3 us; one I-box control cycle = 2 clocks = 0.6 us as shipped),
// taken from IBM's own numbers: for I-box instructions the
// Performance Characteristics tables 4-8 ("basic time + dec", dec =
// 0.6 us, addresses in external memory), for floating point the
// 2-cycle preparation of Blosk fig.6 plus table 2's E-box cycles,
// for VFL the 6-cycle minimum preparation (+1 per indexing op, Perf.
// Char. p.3-17) plus table 3's SAU equation (1.8 us pre-execution,
// 0.6 us per byte, 0.6 us termination). The budget covers the
// instruction's own memory waits when memory is free: it is started
// at dispatch and whatever is left when the semantics complete
// (execute() and its operand reads) holds the next preparation, so
// a busy memory unit adds delay while a free one does not. Without
// the look-ahead (stage 3) E-box time is not overlapped with the
// next preparation -- a documented stage-2 simplification.

// ---- THE 1,024-PER-SECOND OSCILLATOR, as a clock divider -------------
//
// Reference Manual printed p.34 (PDF 37), "Interval Timer", read
// first-hand (the page has no text layer): "The oscillator operates at
// 1,024 (2^10) cycles per second, or a pulse about every
// millisecond."  Printed p.35 says the time clock is stepped by "the
// same 1024 cycle per second oscillator which controls the updating of
// the interval timer", so there is ONE divider here and not two.
//
// One model clock is 0.3 us -- IBM 7030 Performance Characteristics
// Vol. 1, printed p.3-2: "the basic machine cycles, which is presently
// 0.3 microsecond" -- the same figure every budget above is
// denominated in.
//
// THE RATIO IS NOT AN INTEGER, AND THE EXACT RATIONAL IS CHEAP:
//
//     (1/1024) s / 0.3 us = 976.5625 us / 0.3 us
//                         = 9765625/3000 = 78125/24
//                         = 3255.2083... model clocks per tick
//
// Rounding that to 3255 would run the timer about 64 ppm fast, and the
// error accumulates without bound -- which matters, because a
// cycle-accurate replica is a stated goal (AGENTS.md, "Current
// direction") and a wrong rounding here becomes a drift nobody later
// can attribute.  So the divider is a Bresenham accumulator on the
// exact rational instead: add oscPulseNumer every clock and emit a
// pulse, subtracting oscPulseDenom, whenever the accumulator reaches
// it.  That gives EXACTLY 24 pulses per 78125 clocks -- nineteen
// intervals of 3255 clocks and five of 3256 -- with zero long-run
// drift and at most one clock of jitter on any single interval.
//
// AND THE JITTER IS THE HONEST PART, not a compromise.  p.34 calls the
// source "a stable oscillator": a free-running crystal with no stated
// relationship to the CPU's 0.3 us cycle, and nothing in either manual
// makes a pulse synchronous with a machine cycle.  A fixed integer
// period would be the model artifact; a period that is 3255 clocks
// most of the time and 3256 sometimes is what an asynchronous
// 1,024 Hz source looks like when it is sampled by a 3.33 MHz clock.
//
// 78124 + 24 = 78148 < 2^17, so the accumulator (StretchCore's
// `oscAcc`) is seventeen bits and cannot overflow.
Integer oscPulseNumer = 24;      // ticks        -- exactly, per p.34/p.35
Integer oscPulseDenom = 78125;   // model clocks -- and Perf. Char. p.3-2

function Bit#(16) iboxCycles(DecodedInstr d, Bool taken);
  case (d) matches
    tagged DirIndex .x: return case (x.code)
        5'b00001: 9;   // LX     4.8 + dec
        5'b10001: 3;   // SX     1.2 + dec (+ LAAR)
        5'b01111: 15;  // V+CR   8.4 + dec
        default:  8;   // LV/LC/LR/SV/SC/SR/V+/V+C/KV/KC  4.2 + dec
      endcase;
    tagged ImmIndex .x: return case (x.code)
        4'b0110, 4'b1110: 6;   // V+IC / V-IC   3.0 + dec
        4'b0111, 4'b1111: 13;  // V+ICR / V-ICR 7.2 + dec
        default: 5;            // LVI/LCI/LRI/LVNI/V±I/C±I/KVI/KVNI/KCI  2.4 + dec
      endcase;
    tagged CountBranch .x: return (x.refill == 1) ? (taken ? 12 : 11)   // CBR 6.6/6.0 + dec
                                                   : (taken ? 8 : 7);    // CB  4.2/3.6 + dec
    tagged BranchInd .*: return 6;   // Blosk fig.10: decode + 5 execution cycles
    tagged BranchOrMisc .x: return x.misc
        ? (case (x.code) 3'b100: 3; 3'b001: 8; default: 14; endcase)   // Z / RCZ / R
        : (case (x.code) 3'b110: 3; 3'b011: 9; 3'b001: 11; default: 7; endcase); // NOP / BR / BD (+2 LA drains) / B,BE,BEW
    tagged Sic .x: return 2 + iboxCycles(decodeHalfWord(x.inner), taken); // "SIC to EM" columns: +1.2 us
    tagged Transmit .*: return 7;    // Blosk fig.9: 2 set-up + 5 per word (one word here)
    tagged Fp .*: return 2;          // preparation; E-box cycles added below
    tagged VflInt .v: return 6 + ((v.a.i1 != 0) ? 1 : 0);   // preparation, two LA levels
    tagged Connective .c: return 6 + ((c.a.i1 != 0) ? 1 : 0);
    tagged IoOp .*: return 6;
    default: return 3;
  endcase
endfunction

// E-box clocks for the executing classes (table 2 FP; table 3 SAU:
// 1.8 us + 0.6 us per byte + 0.6 us, bytes = ceil(length / byte size)).
function Bit#(16) eboxClocks(DecodedInstr d);
  case (d) matches
    // >>> TABLE 2 GIVES EVERY FLOATING-POINT INSTRUCTION ITS OWN
    // TIME, AND THIS RETURNED A FLAT 3 FOR ALL OF THEM. <<<
    //
    // The comment it carried, "preparation; E-box cycles added
    // below", was copy-pasted from iboxCycles, where the promise is
    // kept.  THERE IS NO BELOW: budgetClocks is
    // `2 * iboxCycles(d, taken) + eboxClocks(d)` and that is the
    // whole budget.  So a floating-point multiply and a floating-
    // point load cost the same, and Table 10's A0 column spends 220
    // multiplies and 88 divides out of 1,364 floating-point
    // operations.
    //
    // Performance Characteristics Vol. 1 Table 2, printed pp.3-3 to
    // 3-5 (PDF 21-23), is two columns, PRE-EXECUTION and EXECUTION,
    // in machine cycles of 0.3 us.  The values below are their SUM
    // AT THE MINIMUM -- no extra pre-shift, no extra normalization,
    // no recomplement, no forced zero.  The old flat 3 is exactly
    // the L/LWF/LFT/ST row (2 + 1), which is why it was never
    // obviously wrong.
    //
    // >>> THESE ARE MINIMA, AND THE TABLE IS DATA-DEPENDENT. <<<
    // Table 2 adds "1 cycle for each additional pre-shift of 4",
    // "2 cycles for each additional norm. of 6", "2 cycles if
    // recomplement is necessary", and for DIVIDE "2 cycles for each
    // additional reduction loop (number of cycles is data
    // dependent)".  A faithful model computes those from the
    // operands -- StretchFP.bsv already derives the shift and
    // normalize counts to produce the ANSWERS, so the data is in
    // hand -- and this does not yet do it.  Recorded as the next
    // step rather than hidden: these numbers are a floor.
    //
    // ALSO NOT MODELLED: *+'s "cannot enter execution cycles until
    // Factor is available" (Table 2, printed p.3-4).  That is an
    // INTERLOCK, not a duration, and it belongs with the look-ahead
    // work in docs/spec_lookahead.md, not in a cycle count.
    //
    // UNVALIDATED AGAINST THE ORACLE.  Perf. Char. Vol. 2 PDF 37-189
    // is a per-instruction MEASURED timing atlas, one instruction per
    // page, and it -- not Table 2 -- is what these should be checked
    // against.  Vol. 2's numbers are THROUGHPUT over thousand-
    // instruction sequences from the 1961 GENER simulator, not
    // isolated latency, so a constant offset is expected; the
    // connective path already shows one of 2.40 us.  See
    // docs/spec_timing.md.
    tagged Fp .f: return
      // L(6) LWF(38) LFT(74) ST(14) DL(70) DLWF(102): 2 + 1
      (f.code == 7'd6 || f.code == 7'd38 || f.code == 7'd74 ||
       f.code == 7'd14 || f.code == 7'd70 || f.code == 7'd102) ? 3 :
      // SRD(46): 3 + 1
      (f.code == 7'd46) ? 4 :
      // E+(86) E+I(118): 1 + 5
      (f.code == 7'd86 || f.code == 7'd118) ? 6 :
      // *(26) D*(90): 5 + 4
      (f.code == 7'd26 || f.code == 7'd90) ? 9 :
      // *+(58): 3 + 17
      (f.code == 7'd58) ? 20 :
      // /(30): 2 + 2, before the data-dependent reduction loops
      (f.code == 7'd30) ? 4 :
      // D/(94): Divide plus 6 for the remainder normalization
      (f.code == 7'd94) ? 10 :
      // R/(62): 2 + 2 "plus all pre-execution and execution cycles
      // of Divide", so 4 + 4
      (f.code == 7'd62) ? 8 :
      // SLO(78): 2 + 17 unnormalized (15 if normalized with no
      // leading zeros -- the unnormalized figure is the floor)
      (f.code == 7'd78) ? 19 :
      // SRT(110): 2 + 106
      (f.code == 7'd110) ? 108 :
      // The ADD class and everything sharing its shape: + (2),
      // +MG(34), M+(10), M+MG(42), K(18), KMG(50), KR(22),
      // KMGR(54), D+(66), D+MG(98), F+(82), SHF(114).  4 + 1.
      5;
    tagged VflInt .v: begin
      // Table 3's SAU byte count is .6(x/y), and Perf. Char. Vol. 1
      // printed p.3-10 (PDF 28) defines x and y -- NEITHER is the
      // declared field:
      //   x   Field length in unsigned operations - field length minus
      //       the byte size in signed operations
      //   y   8 in binary operations and byte size in decimal operations
      // So the SAU runs 8 bits wide in binary mode whatever byte size
      // the instruction declares, and a signed operation does not pay
      // for its sign byte.  effLength/effByteSize give the DECLARED
      // field, which is what readField/writeField need and what timing
      // must not use -- hence the local x and y rather than a change
      // to those two functions.  Measured against Vol. 2 printed p.110
      // (M+, no forwarding, direct addressing, offset 0, instruction at
      // full word address, NO INDEXING / EXTERNL OPERAND): over its 24
      // rows this takes mean |error| from 4.02 to 0.28 us and worst-case
      // from 33.60 to 1.20, changing 10 rows and leaving 14 identical.
      // The deck suite cannot see it: every one of the 1,106 field specs
      // in decks is (BU,n,8), where both corrections are the
      // identity.  The evidence is the Vol. 2 table, not a passing run.
      Bit#(7) len_ = effLength(v.a.length);
      Bit#(4) bsz  = effByteSize(v.a.bs);
      Bit#(8) x = (v.m.unsign == 1 || len_ <= zeroExtend(bsz))
                    ? zeroExtend(len_)
                    : zeroExtend(len_) - zeroExtend(bsz);
      Bit#(8) y = (v.m.decimal == 1) ? zeroExtend(bsz) : 8;
      Bit#(8) bytes = (x + y - 1) / y;
      return 8 + 2 * zeroExtend(bytes);
    end
    // NOT GIVEN THE SAME TREATMENT, deliberately.  The connectives have
    // no VflMod -- no sign and no radix bit -- so p.3-10's x and y have
    // no referent here, and p.3-10 belongs to Table 3, "EQUATIONS FOR
    // SAU INSTRUCTIONS", whose instruction list (ST, L, M+, K, KI, KF,
    // KR, KRI, KE, LTRS, LCV, ...) does not include them.  Vol. 2 has
    // no connective page either: its 66 instruction headers are all VFL
    // arithmetic.  So the declared byte size stays here until a source
    // says otherwise -- unsourced, and recorded as such in
    // docs/NEXT.md 5g rather than fixed by analogy.
    tagged Connective .c: begin
      Bit#(7) len_ = effLength(c.a.length);
      Bit#(4) bsz  = effByteSize(c.a.bs);
      Bit#(8) bytes = (zeroExtend(len_) + zeroExtend(bsz) - 1) / zeroExtend(bsz);
      return 8 + 2 * zeroExtend(bytes);
    end
    default: return 0;
  endcase
endfunction

function Bit#(16) budgetClocks(DecodedInstr d, Bool taken) =
  2 * iboxCycles(d, taken) + eboxClocks(d);

endpackage
