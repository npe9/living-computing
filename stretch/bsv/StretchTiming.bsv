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
// 0.6 us per byte, 0.6 us termination) -- REPLACED for VFL and the
// connectives on 2026-11-16 by the per-operation throughput Perf. Char.
// Vol. 2's atlas measures (eboxClocks' VflInt and Connective arms say
// why and cite the page for each number). The budget covers the
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
        5'b11111: 16;  // RNX    9.0 + dec (Table 4, EM column; LAdr, LAAR not charged)
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
      // >>> THE E-BOX TIME OF A VFL OPERATION DEPENDS ON THE OPERATION,
      // 2026-11-16. <<<  It used to be `8 + 2 * bytes` for every one of
      // them, L and `/` and LCV alike, and Perf. Char. Vol. 2's atlas
      // (docs/atlas_oracle.md, "Where the model is furthest off" item 1)
      // measured the result: `/` (BU,64,8) 25 clocks against a printed
      // 96, LCV 25 against 168.
      //
      // WHY THE OLD "0.28 us" AGAINST THE M+ PAGE DID NOT SURVIVE IN
      // SEQUENCE -- the diagnosis, and it is structural, not a lost
      // charge.  budgetClocks (`2 * iboxCycles + eboxClocks`, the serial
      // sum the 0.28 us was computed from) is charged ONLY on the I-box
      // dispatch path (StretchCore's startExecute / rl_exec_resume's
      // OwnerIbox arm).  A VFL instruction never takes that path: it is
      // E-box class and goes through a look-ahead level, where
      // rl_prepare charges `ibusy = 2 * iboxCycles` (12 clocks) at load
      // and rl_au_remove charges `ebusy = eboxClocks` at removal, and
      // the two counters run CONCURRENTLY.  So a homogeneous sequence
      // runs at max(prep, E-box) and not prep + E-box.  Measured on the
      // atlas's own M+ page (PDF 117 ni_ext, 48 cases, 2026-11-16): every
      // row is max(14.02, 8 + 2 * bytes + 1) -- 14 = the 12-clock
      // preparation plus 2, and +1 = the removal clock (`ebusy` reaches
      // 0 one clock after the charge runs out: rl_au_remove fires on
      // `ebusy == 0`, so an E-box time of N occupies N + 1 clocks; the
      // self-test's L(BU,64,8) measured 24.999 against a charge of 24
      // before this change, and 27.998 against 27 after it).  The
      // overlap itself is RIGHT, and the 7030's pages show it: on PDF
      // 120 L's INDEXING columns equal its NO INDEXING ones from
      // (BU,32,8) on, i.e. the extra 0.6 us of indexed preparation is
      // hidden behind the E-box once the E-box is the longer.  What was
      // wrong is that the E-box charge was too small to be the longer.
      //
      // SO EACH NUMBER BELOW IS THE E-BOX OCCUPANCY THE ATLAS MEASURES:
      // the printed throughput, in clocks, of the page's NO INDEXING /
      // EXTERNL OPERAND column (no forwarding, direct addressing, offset
      // 0, full-word instruction address), less the one removal clock.
      // They are FITS TO PRINTED PAGES, each cited, not mechanisms; where
      // the time depends on the data (Table 3's z, w, c, s, u, the divide
      // quotient) the fit is a measurement AT THE ATLAS'S OPERANDS --
      // the standard operand (444...4)16 in the accumulator, a memory
      // operand of +1 for divide (PDF 113) -- and says so.  The fit's
      // residual on PDF 116-142 (6,098 cases, every column) is
      // tabulated in docs/atlas_oracle.md.
      //
      // BYTES.  Table 3's .6(x/y) (Vol. 1 printed p.3-7, PDF 25), with
      // printed p.3-10's (PDF 28) x and y: x = the field length unsigned,
      // the field less the byte size signed; y = 8 binary, the byte size
      // decimal.  Plus ONE byte when signed: Table 3's preamble (printed
      // p.3-6, PDF 24) "Signed operations can be computed by adding .6
      // microseconds to the pre-execution time", and the pages agree --
      // L (B,8,1) 4.80 against (BU,8,8) 4.20 (PDF 120).  A signed field
      // no longer than its sign byte has x = 0: L (B,1,1) and (D,4,4)
      // print 4.20, one byte, not two.  (The preamble's list of
      // operations that pay nothing for a sign is honoured where a page
      // agrees and overruled where one does not: SRD at offset 0 prints
      // ST's signed rows cell for cell, PDF 125 against 124.)
      Bit#(7) len_ = effLength(v.a.length);
      Bit#(4) bsz  = effByteSize(v.a.bs);
      Bool    sgn  = (v.m.unsign == 0);
      Bool    dec  = (v.m.decimal == 1);
      Bit#(8) x = !sgn ? zeroExtend(len_)
                : (len_ > zeroExtend(bsz)) ? zeroExtend(len_) - zeroExtend(bsz) : 0;
      Bit#(8) y = dec ? zeroExtend(bsz) : 8;
      Bit#(8) b0 = (x + y - 1) / y;              // data bytes
      Bit#(16) s = sgn ? 1 : 0;
      Bit#(16) b = zeroExtend(b0) + s;           // bytes, sign byte included
      Bit#(16) fl = zeroExtend(len_);
      Bool fullU = !sgn && len_ == 64;           // a whole unsigned word
      // Decimal digits of an FL-bit binary field, ceil(FL * log10 2),
      // as ceil(FL * 77 / 256) -- exact for every FL from 1 to 64.
      Bit#(16) dig = (fl * 77 + 255) / 256;
      Bit#(16) e = 0;
      case (v.code)
        // L, LWF, +, +MG: 12 + 2 bytes.  PDF 120 (L), 121 (LWF), 116 (+),
        // 118 (+MG): L (BU,8,8) 4.20 = 14, (BU,64,8) 8.40 = 28, (DU,64,4)
        // 13.20 = 44.  Table 3 prints 1.8 + .6(x/y) + .6 for all four, a
        // full word of 7.2 us; the measured full word is 8.40, so the
        // E-box's fixed part is 3.6 us, not 2.4.  (+'s unsigned decimal
        // rows sit about one clock higher and its binary rows from 8 bits
        // on about half a clock; the signed decimal rows are exact.  Not
        // charged.)
        6'b000101, 6'b100101, 6'b000001, 6'b100001: e = 12 + 2 * b;
        // M+, M+MG, ST, SRD -- the STORING operations.  "All VFL stores
        // are fetch-and-stores" (Vol. 1 printed p.2-3, PDF 10, item 6).
        // PDF 117 (M+), 119 (M+MG), 124 (ST), 125 (SRD, offset 0) print
        // the same column: 22.1 clocks at one or two bytes (6.63 / 6.93
        // us), then 18 + 2 bytes (ST (DU,32,4) 10.21 = 34.0), less 2
        // for a whole unsigned 64-bit field (ST (BU,64,8) 9.61 = 32.0
        // against 34) -- a FIT: K, which stores nothing, shows the same
        // -2, and the signed (D,64,4) does not.  SRD's rounding
        // pre-execution is added below as before.
        6'b001001, 6'b101001, 6'b001101, 6'b101101:
          e = ((b < 3) ? 21 + b : 18 + 2 * b) - (fullU ? 2 : 0);
        // M+1: flat.  PDF 126: 6.33 us = 21.1 at every unsigned field,
        // 6.63 = 22.1 signed beyond the sign byte.  Table 3's .6(c + 1)
        // counts carries, and +1 into 444...4 carries out of no byte.
        6'b101011: e = (sgn && len_ > zeroExtend(bsz)) ? 22 : 21;
        // K, KE, KR: 10 + 2 bytes, 8 + 2 for a whole unsigned word.
        // PDF 127-129: K (BU,32,8) 5.40 = 18, (BU,64,8) 7.20 = 24.  A
        // FIT, one byte over KF: it is not Table 3's w/r term, which
        // against the 64-bit standard operand would be seven bytes at
        // (BU,8,8) and is flat one on the page.
        6'b010001, 6'b010011, 6'b010101: e = 10 + 2 * b - (fullU ? 2 : 0);
        // KF, KFE, KFR: 8 + 2 bytes -- Table 3's own equation exactly,
        // 1.8 + .6(x/y) + .6.  PDF 130-132: KF (BU,64,8) 7.20 = 24.
        6'b110001, 6'b110011, 6'b110101: e = 8 + 2 * b;
        // *: 36 clocks, +2 signed, +2 at 64 bits.  PDF 133: (BU,8,8)
        // 10.80, (B,8,1) 11.40, (BU,64,8) 11.40, (B,64,1) 12.01.  Table 3:
        // 6.0 + 3.9 + .6 = 10.5 us, 35 clocks.
        6'b011001: e = 36 + 2 * s + ((len_ == 64) ? 2 : 0);
        // /: 66 + 4 bytes, +44 signed.  PDF 134: (BU,16,8) 22.21 = 74,
        // (BU,32,8) 24.61 = 82, (B,8,1) 35.42 = 118, (B,16,1) 36.61 = 122.
        // A MEASUREMENT AT ONE DIVIDEND AND A DIVISOR OF ONE: the page
        // says so, and PDF 41 says "The present measurements for /, D/
        // and R/ do not give a realistic timing".  Table 3's Q (printed
        // p.3-9) is the data-dependent law; this is not it.  The divide
        // box's own clocks are INSIDE this figure (rl_exec_resume
        // subtracts boxClocks from it).
        6'b011101: e = 66 + 4 * b + 44 * s;
        // *+: PDF 135.  46 clocks (13.80 us) while the field is at most
        // a byte (unsigned) or shorter than one (signed: (B,1,1) 14.41 =
        // 48), else max(60, 50 + 2 ceil(x/8)) -- (BU,16,8) 18.01 = 60,
        // (BU,64,8) 19.81 = 66.  Table 3: 7.8 + (3.0 + Add) + .6.
        6'b111001: e = (len_ < 8 || (!sgn && len_ == 8)) ? 46 + 2 * s
                   : max(60, 50 + 2 * zeroExtend((x + 7) / 8));
        // LFT, LTRS: 44 binary, 66 decimal, +16 above 48 bits.  PDF 122
        // and 123 print the same page: (BU,8,8) 13.20 = 44, (DU,8,4)
        // 19.81 = 66, (DU,64,4) 24.60 = 82.  Table 3 (printed p.3-8):
        // 2.4 + .6(v/y + 3) + .6, v = 96 binary, 92 decimal, "if the
        // effective FL is greater than 48 bits, add .6(t/8 - 1)" -- 40
        // and 62 clocks, 4 under the pages.
        6'b001011, 6'b111101: e = (dec ? 66 : 44) + ((len_ > 48) ? 16 : 0);
        // LCV.  Binary to decimal, PDF 136: 18 + 2 FL + 2 ceil(u/8), u
        // the decimal result of ceil(FL log10 2) digits -- Table 3's B-D
        // LCV, 2.4 + .6(x + u/8 + 1) + .6 (printed p.3-8), plus 6 clocks:
        // (BU,8,8) 11.40 = 38, (BU,48,8) 39.02 = 130.  Decimal to binary:
        // 76 + 3 digits, 74 + 3 digits signed -- (DU,32,4) 30.01 = 100,
        // (D,32,4) 28.21 = 94; Table 3's D-B LCV (14.7 us at a full
        // word) is far below every row of the page.
        6'b000011: e = dec ? (sgn ? 74 : 76) + 3 * zeroExtend(b0)
                       : 18 + 2 * fl + 2 * ((dig + 1) / 2);
        // LTRCV.  Binary to decimal, PDF 137: 22 + 2 FL, plus Table 3's
        // ".6(FLc/8 - 1)" once the converted field passes 48 bits --
        // Table 3's B-D LTRCV, 2.4 + .6(x + 3) + .6, plus 6 clocks:
        // (BU,32,8) 25.81 = 86, (BU,48,8) 39.62 = 132, (BU,64,8) 51.02 =
        // 170.  Decimal to binary: flat 102 (30.61 us), 118 above 48
        // bits (35.41).
        6'b100011: e = dec ? ((len_ > 48) ? 118 : 102)
                       : 22 + 2 * fl + ((4 * dig > 48) ? 2 * ((4 * dig + 7) / 8 - 1) : 0);
        // CV and DCV, PDF 138 and 139: flat in the field, because the
        // operand is the accumulator -- "for convert (CV) and convert
        // double (DCV) the accumulator was originally +1 at offset 20"
        // (PDF 113).  CV 6.00 us = 20 binary, 22.14 = 73.8 decimal; DCV
        // 6.00 = 20 binary, 5.40 = 18 decimal, at every row.  FITTED TO
        // THE PAGE AND NOT MEASURABLE BY THE ORACLE (atlas_oracle.py has
        // no CV/DCV generator), and a measurement at that one
        // accumulator: Table 3's s is "the accumulator field specified by
        // the offset minus all leading zeros" (printed p.3-9, p.3-10).
        6'b011011: e = dec ? 74 : 20;
        6'b111011: e = dec ? 18 : 20;
        // (DCV executes since 2026-11-16 -- G2.3, mkCvtBox, whose 6 and 4
        // clocks fit inside these -- and this row is its time.  CV, LCV
        // and LTRCV use the same box since 2026-11-17; their rows here
        // are unchanged, and the box's clocks come off them.)
        // Anything else (no other code is a VflInt operation): L's law.
        default: e = 12 + 2 * b;
      endcase
      // SRD (VFL STORE ROUNDED, code 101101).  Table 3 (Vol. 1 printed
      // p.3-7, PDF 25, read in the image) gives it ST's execution and
      // termination, .6(x/y) and .6, and a pre-execution time of 3.0 us
      // where ST has 1.8: 1.2 us = 4 clocks more, full word total 8.4
      // against 7.2.  Vol. 2's SRD page (printed p.118, PDF 125) is
      // measured at OFFSET 0 only, and there it equals the ST page
      // (printed p.117) cell for cell to 0.01 us (each page's SUM line:
      // 272 values, 3738.81 against 3738.83 us) -- which is the
      // Reference Manual's "A STORE ROUNDED with zero offset specified is
      // equivalent to a STORE" (printed p.64).  So the 4 clocks are
      // charged at a nonzero offset only.  CHOSEN where the two meet:
      // Table 3 does not mention the offset, and no page measures SRD at
      // a nonzero one.  The offset tested is the instruction's own
      // (v.a.offset); execute() rounds at the offset as the second index
      // leaves it (vflSecondIndex), which this function, having no
      // storage, cannot see -- a second-indexed SRD whose offset moves
      // to or from 0 is charged by its written offset.  A refused SRD
      // (decimal) is charged too, like every refused operation here.
      // Pinned by decks/vfl_srd.strap's CYCLES check (header).
      Bit#(16) srdRound = (v.code == 6'b101101 && v.a.offset != 0) ? 4 : 0;
      // DECIMAL *, *+ AND / ARE LTRS'S ACTION (Reference Manual printed
      // pp.68-70; batch10's mkDecBox), and are charged as LTRS -- now
      // PDF 123's measured decimal LTRS figure, 66 clocks (19.81 us), 82
      // above 48 bits (24.60), rather than Table 3's formula (printed
      // p.3-8), which batch10 charged as 16 + 2 bytes and which sits 4
      // clocks under the page at its own full word.  CHOSEN for the three
      // arithmetic codes: their own pages (PDF 133 *, 134 /, 135 *+)
      // print binary rows only, so no measurement of decimal * / *+
      // exists; LTRS's is the nearest.
      Bool decLtrsAction = dec && (v.code == 6'b011001 || v.code == 6'b111001
                                   || v.code == 6'b011101);
      if (decLtrsAction) e = 66 + ((len_ > 48) ? 16 : 0);
      // Less the removal clock (see above): the atlas figure is the
      // occupancy, and rl_au_remove adds the one clock itself.
      return e - 1 + srdRound;
    end
    // NOT GIVEN THE SAME TREATMENT, deliberately.  The connectives have
    // no VflMod -- no sign and no radix bit -- so p.3-10's x and y have
    // no referent here, and p.3-10 belongs to Table 3, "EQUATIONS FOR
    // SAU INSTRUCTIONS", whose instruction list (ST, L, M+, K, KI, KF,
    // KR, KRI, KE, LTRS, LCV, ...) does not include them.
    //
    // >>> AND VOL. 2 *DOES* HAVE A CONNECTIVE PAGE.  THE DECLARED
    // BYTE SIZE IS SOURCED, AND IT WAS RIGHT ALL ALONG. <<<
    //
    // This comment used to end "unsourced, and recorded as such in
    // docs/NEXT.md 5g rather than fixed by analogy", and said Vol. 2
    // had no connective page.  **PDF 140 is one** -- "VFL
    // INSTRUCTION C0011, NO FORWARDING, DIRECT ADDRESSING, OFFSET 0,
    // INSTRUCTION AT FULL WORD ADDRESS" -- and it is the one
    // experiment that pins the byte count, because it VARIES THE
    // BYTE SIZE AT FIXED FIELD LENGTH.  Rendered and read:
    //
    //   (BU, 8,1)  8.40     (BU,16,1) 13.20     (BU,32,1) 13.20
    //   (BU, 8,2)  6.00     (BU,32,2) 13.20     (BU,48,3) 13.20
    //   (BU, 8,8)  4.20     (BU,64,4) 13.20
    //
    // All 35 rows obey  t = 3.6 + 0.6 * ceil(FL / byte size)  us to
    // 0.01, with the DECLARED byte size -- confirming this code
    // rather than correcting it.  The obvious "fix" from Table 3's
    // glossary, y = 8, was drafted and the page refuted it.
    //
    // TWO CORRECTIONS THE PAGE DOES MAKE:
    //
    // 1. THE CONSTANT.  iboxCycles returns 6 here, doubled to 12
    //    clocks = 3.6 us, and this used to add a further 8 clocks =
    //    2.40 us for Table 3's "1.8 us pre-execution + 0.6 us
    //    termination".  The measured law has NO such constant: those
    //    two are ENTIRELY OVERLAPPED with the I-box preparation.  All
    //    34 in-range rows sat at a uniform 2.40 us too high.
    //
    // 2. A SIXTEEN-BYTE CAP that no table states.  (BU,32,1) is
    //    thirty-two bytes and reads 13.20 -- identical to (BU,16,1).
    //    Every row needing more than sixteen bytes reads the
    //    sixteen-byte time.  It is the 35th row, the one that did not
    //    fit the law, and it is why the law holds on the other 34.
    //
    // (THE TWO CLASSES AGREE NOW.  This paragraph used to say the VflInt
    // arm's constant had been measured against the M+ page "to a mean
    // error of 0.28 us" and so disagreed with this one; that figure was
    // the serial budget, not a measurement, and in sequence the M+ page
    // sat 7-11 clocks low.  Measured in sequence, L and C0011 have the
    // same law, 12 + 2 * bytes: PDF 120 against PDF 140.)
    //
    // POINT 1 ABOVE IS SUPERSEDED IN ITS CONCLUSION, 2026-11-16: the
    // constant is not "overlapped with the I-box preparation" in
    // sequence; it is the E-box's.  Point 1 was right that the SERIAL
    // budget carried 2.40 us too much.
    tagged Connective .c: begin
      Bit#(7) len_ = effLength(c.a.length);
      Bit#(4) bsz  = effByteSize(c.a.bs);
      Bit#(8) raw  = (zeroExtend(len_) + zeroExtend(bsz) - 1) / zeroExtend(bsz);
      Bit#(8) bytes = (raw > 16) ? 16 : raw;
      Bit#(16) cb  = zeroExtend(raw);     // CM: no cap (below)
      Bit#(16) cap = zeroExtend(bytes);
      // >>> 2026-11-16: THE PAGE'S LAW IS NOW THE E-BOX TIME, AND CT AND
      // CM HAVE THEIR OWN. <<<  `2 * bytes` relied on the 12-clock
      // preparation being charged IN SERIES with it, and on the look-
      // ahead path it is not (the VflInt arm above has the diagnosis):
      // C0011 measured max(14, 2 * bytes + 1) in sequence, mean -6.90
      // clocks against PDF 140.  So the whole measured time is the
      // E-box's, less rl_au_remove's removal clock:
      //   C   (PDF 140)  12 + 2 * bytes, sixteen-byte cap -- the law above.
      //   CT  (PDF 142)  8 + 2 * bytes, cap 16, never under 12: (BU,64,8)
      //                  7.20 us = 24, (BU,16,1) 12.00 = 40, (BU,8,8) 3.61
      //                  = 12.  The test-only connective, K's shape.
      //   CM  (PDF 141)  16 + 2 * bytes with NO cap -- (BU,32,1) 24.01 us =
      //                  80, thirty-two bytes -- and 20 + bytes below four
      //                  bytes ((BU,8,8) 6.33 = 21.1, (BU,8,4) 6.63 =
      //                  22.1).  The storing connective: "All VFL stores
      //                  are fetch-and-stores" (Vol. 1 printed p.2-3).
      // Other suffixes (the immediate forms) have no transcribed page and
      // are charged as C.
      Bit#(16) e = (c.suffix == conn_CM) ? ((cb < 4) ? 20 + cb : 16 + 2 * cb)
                 : (c.suffix == conn_CT) ? max(12, 8 + 2 * cap)
                 : 12 + 2 * cap;
      return e - 1;
    end
    default: return 0;
  endcase
endfunction

function Bit#(16) budgetClocks(DecodedInstr d, Bool taken) =
  2 * iboxCycles(d, taken) + eboxClocks(d);

endpackage
