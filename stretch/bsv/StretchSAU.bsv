// StretchSAU.bsv -- mkSAU, THE SERIAL ARITHMETIC UNIT, as one multi-cycle
// box (docs/fidelity_plan.md A3, half (a), 2026-11-25).
//
// >>> WHAT THIS IS <<<  The three boxes the E-box's VFL arms reached --
// the serial adder (mkDecBox), the VFL multiplier (mkVflBox) and the
// radix converter (mkCvtBox), StretchDecBox.bsv, StretchVflBox.bsv and
// StretchCvtBox.bsv until this file (those files deleted 2026-11-25;
// see git history) -- become ONE stateful module with
// one request method, one responseReady poll and one response value: the
// mkFBox / mkRISCV_MBox shape (AGENTS.md, "Idiomatic Bluespec"), and the
// 7030's own: Buchholz, "Planning a Computer System", §14.4, printed
// p.208 (PDF 233), "The arithmetic unit consists of a parallel unit for
// floating-point operations and a serial unit for variable-field-length
// operations" -- one serial unit, not three.
//
// >>> HALF (a): THE CLOCKS ARE TODAY'S, EXACTLY. <<<  Every class steps
// at the rate its old box stepped, so every instruction's time is what
// it was (the VFL and FP atlas TSVs are byte-identical, the suite's
// pins and halt clocks unchanged; fidelity_plan.md A3 records the run):
//   * add / subtract, decimal or binary: `sauAddDigits` (8) digits a
//     clock, a pass of 4 clocks, 8 when the subtraction recomplements;
//   * the 48 x 48 multiply: `sauMulBits` (12, SOURCED: Buchholz printed
//     p.210) multiplier bits a clock, 4 clocks;
//   * the conversions: `sauCvtBits` (16) bits a clock binary-to-decimal,
//     6 clocks for 96 bits; `sauCvtDigits` (8) digits a clock back, 4.
// The add and conversion rates are CHOSEN, not sourced (the old boxes'
// notes, kept below); the machine's is a byte pair per 0.6 us, Buchholz
// printed p.209 (PDF 234), one digit or one bit a pass for the
// conversions (docs/sau_pau_spec.md §5, Figs 3.11.4-3.11.7, 3.11.13,
// 3.11.14).  Putting those in is half (b), and it moves the clocks.
//
// >>> WHAT IS SHARED NOW, AND WHAT IS NOT YET <<<
//   * ONE STATE MACHINE AND ONE REGISTER SET.  The operand register
//     `rg_a` is the adder's augend, the converter's source and the
//     multiplicand; `rg_r` is the adder's sum, the converter's result
//     and the product register; one counter, one state.  The three old
//     boxes had three of each (401 + 149 + 269 = 819 flip-flops,
//     fidelity_plan.md A3 has the after).  Only one class is ever in
//     flight: mkEBox holds one instruction and a held instruction asks
//     one box and waits for it (mkEBox.start: an I-box instruction run
//     beside a held one is REFUSED if it would ask a box).
//   * ONE DIGIT-STEP CHAIN for the add pass and the recomplement pass
//     (mkDecBox had one each).
//   * NOT SHARED: the converter's double dabble and Horner chains, and
//     the 48 x 12 multiplier.  They are the old boxes' datapaths, moved
//     verbatim.  At their chosen widths they are most of the unit's
//     LUTs (the converter alone ~6,000 LUT4), and fidelity_plan.md F1's
//     rule -- the unit at the machine's own width -- is NOT met until
//     (b) steps them a bit or a digit a pass through the serial adder.
//   * THE MULTIPLIER IS THE PARALLEL UNIT'S, and is here only until A4.
//     Buchholz printed p.208: "variable-field-length binary multiply and
//     divide operations are performed by the parallel unit"; R23-9732
//     Figs 3.11.1, 3.8.18 ("WAIT FOR PAU TO MULT AND XFER RESULT TO
//     AB"); docs/sau_pau_spec.md §6 (ONE multiplier, shared with the FP
//     fraction).  The plan put mkVflBox into A3 with the serial boxes;
//     A4's mkPAU takes the `rl_mul` block (and mkFpBox's) as its one
//     multiplier tree, and the SAU then assembles the operand a byte a
//     pass and requests it, as Fig. 3.11.1 draws.
//
// ---------------------------------------------------------------------
// THE ADDER: WHAT IT COMPUTES, AND WHERE THAT IS PRINTED (mkDecBox's text)
// ---------------------------------------------------------------------
// ONE ADDER, DECIMAL CORRECTION SWITCHED IN (2026-11-19, plan §1c step 5e
// stage 3).  Buchholz printed p.208: "variable-field-length (binary or
// decimal) add operations, and logical-connective operations are
// executed by the serial unit".  Printed p.209, of that unit's common
// adder: "True-complement (inversion) circuits, both before and after
// the adder, take care of subtraction.  A decimal-correction circuit is
// switched into the data path when decimal addition or subtraction is
// specified."  So a binary add is the same adder with the correction off
// -- DecReq's `binary`:
//   * the digit step drops the "above nine" correction: four bits add
//     with the carry out of bit 3 as the digit carry (sauDigitStep);
//   * complementing is inversion (ones' complement, 15 - d) instead of
//     nines' (9 - d), so a subtraction is a + ~b + 1 and the second
//     pass recomplements to b - a exactly as the decimal one does;
//   * the passes, the clocks and `carry`'s meaning are the decimal
//     ones: like signs, the carry out of bit 127 (Lost Carry); unlike,
//     True iff a >= b.
// The callers are vflIntOp's families (StretchExecute.bsv): +, +MG, the
// M+ family, the K family, decimal L / LWF, decimal SRD's rounding, ST.
//
// Reference Manual 22-6530-2 printed p.60 (PDF 63), ADD, Radix: the
// radix modifier "determines the properties of the adder, and controls
// complementation and recomplementation when the effective operand
// signs are unlike.  In decimal arithmetic, four-bit bytes are used ...
// and a carry occurs from one byte to the next when a sum byte exceeds
// 9."  Printed p.57: "In decimal operations, the accumulator is treated
// as 32 four-bit digit positions."  So the adder adds two 32-digit
// operands `a` and `b`, digit by digit:
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
// WHAT IS NOT IN THE SOURCES, said once:
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
//   used."  The unit receives four-bit digits whatever the storage byte
//   size was (the caller zero-extends, p.58: "each byte of the storage
//   operand is converted to a four-bit byte for processing by the
//   addition of high-order zeros"), so it produces the NORMAL result.
//   The abnormal one is not described anywhere this project has.
//
// ---------------------------------------------------------------------
// THE MULTIPLIER (mkVflBox's text)
// ---------------------------------------------------------------------
// The 48 x 48 product of VFL `*` (code 011001) and of `*+` (code 111001).
// Buchholz §14.4, read in the text layer of
// docs/Planning_A_Computer_System.pdf:
//   * printed p.210 (PDF 235): "To expedite the execution of the multiply
//     instructions, 12 BITS OF THE MULTIPLIER ARE HANDLED IN ONE CYCLE.
//     ... The action is from right to left".
//   * printed p.211 (PDF 236): the multiplicand multiples are summed in
//     carry-save adders, "and, DURING THE LAST CYCLE, into the carry
//     propagate adder for accumulation of the carries.  Since no
//     propagation of carries is required in THE FOUR CYCLES when
//     multiplicand multiples are added, this operation is fast".
// So a 48-bit multiplier is FOUR cycles of twelve bits, right to left,
// and the final carry assimilation shares the fourth: request at T, the
// four passes at T+1 .. T+4, the answer readable at T+4.
// NOT MODELLED, said once: the recoding.  The 7030 decodes each 12-bit
// group as four 3-bit groups into even multiples of the multiplicand
// (Fig. 14.8) and keeps the partial product in carry-save form between
// cycles.  `rl_mul` adds the exact 48 x 12 partial product each pass in
// ordinary binary.  The product is the same number either way.
//
// ---------------------------------------------------------------------
// THE CONVERTER (mkCvtBox's text)
// ---------------------------------------------------------------------
// Every radix conversion, CV, LCV, LTRCV and DCV.  Reference Manual
// 22-6530-2 printed p.74 (PDF 77), Convert Double: "A field from the
// accumulator is converted as an integer from binary to decimal or from
// decimal to binary depending on the setting of the radix modifier."
// The unit converts the MAGNITUDE; the caller chooses the field, the
// offset, the sign and the indicators.
//   * toDec: `v` is a binary integer (the caller gives 96 bits).  The
//     answer is its 32-digit BCD value, digit 0 in bits 3:0.  2^96 is
//     29 digits, so 32 hold every answer exactly; the caller keeps the
//     low 24 and reads Partial Field from the rest.  DOUBLE DABBLE, most
//     significant bit first: for each bit every digit of five or more
//     gets three added, then the whole is shifted left one with the bit
//     coming in at the bottom.
//   * !toDec: `v` is 32 BCD digits.  The answer is their binary value
//     (10^32 needs 107 bits; 128 hold it).  HORNER, most significant
//     digit first: r = 10r + d.  A "digit" above nine is taken at its
//     binary value; the manual defines no check (spec_decimal.md 1d).
//
// ---------------------------------------------------------------------
// TIME
// ---------------------------------------------------------------------
// UNSTEPPED REQUESTS (half (a)'s contract, still that of the M+ family,
// the K family, SRD's round, the converter and the multiplier): the
// instruction's time is eboxClocks' (StretchTiming.bsv, Perf. Char. Vol.
// 1 Table 3 and the Vol. 2 atlas), and mkEBox takes the unit's clocks
// OFF that budget (StretchCore's rl_exec_resume: boxClocks), so the unit
// must fit inside the smallest budget of each class: 8 + 2 x 1 byte = 10
// clocks for an add (the pass of 2, or 4 recomplemented, fits); DCV's
// decimal 18 for a conversion (6 and 4 fit); `*`'s 36 for the multiply.
//
// >>> HALF (b), 2026-11-25: A STEPPED ADD OWNS ITS TIME. <<<  L and LWF
// decimal, + and +MG in both radices send their passes (SauAddSteps).
// The unit then answers after 2 clocks a pass (Buchholz printed p.209;
// Table 3's .6 a byte): the field's bytes and sign byte, Table 3's z,
// and the recomplement (the switches sauStepZ / sauStepRecomp).
// ownClocks() reports that count, and StretchCore charges the eboxClocks
// row LESS its byte term (sauRowWithUnit since step 2) from the answer, taking
// nothing off.  So the row's byte term is deleted for these, and what the
// row keeps is its fixed part.  WHAT THIS IS NOT: a byte-wide datapath.
// The sum is still made 16 digits a clock inside the stepped time (the
// datapath is never the slower: sauAddDigits' note); only the clock count
// is the stepping's.  Narrowing the datapath to the byte the passes
// describe is F1's work, and it does not change a clock.
// ---------------------------------------------------------------------
package StretchSAU;

// >>> THE RATES (half (a): the old boxes', unchanged) <<<
// Adder: digits a clock.  CHOSEN (mkDecBox's decDigitsPerCycle): it must
// fit the smallest add budget (TIME above) and divide 32.  16 SINCE HALF
// (b) (2026-11-25), was 8: a stepped add's time is its passes, 2 clocks
// each, and the shortest field is one pass, so the datapath must have
// the sum in 2 clocks (4 recomplemented) or it, not the stepping, would
// set the time of a one-byte add.  The byte-wide datapath the stepping
// describes is F1's step, not this one (the header's TIME note).
Integer sauAddDigits = 16;
Integer sauDigits    = 32;
// >>> THE STEPPED TERMS, ONE SWITCH EACH (half (b), 2026-11-25). <<<  A
// stepped add (SauAddSteps.passes != 0) takes 2 clocks a pass (Buchholz
// printed p.209: the serial unit's byte pair per 0.6 us; Table 3's .6
// per term unit).  Its passes are the field's (always), and:
//   * sauStepZ: Table 3's z (glossary printed p.3-10, PDF 28), "One for
//     a carry out of the last x/y byte plus one for a carry out of each
//     succeeding 8 bit byte in binary or 4 bit byte in decimal" -- Fig.
//     3.11.9's passes after EOC1 while a carry propagates.  With unlike
//     signs the propagating state is the BORROW (no carry into the byte):
//     DERIVED, the figure tests CARRY after EOC1 and prints no sense for
//     a subtraction; a complemented addend beyond the field is all ones
//     (nines), so a carry there propagates to the end of the accumulator
//     and could not be what stops the loop.
//   * sauStepRecomp: Table 3's "Unlike signs CD > AB, add .6(os/r + x/y
//     + z + 1) to the execution time" (+), ".6" (+MG): the recomplement
//     pass over the result from the accumulator's right end (Fig. 3.11.9
//     Part 4, "BAAB TO 127").
// Each is the attributing injection for what it moves (fidelity_plan.md
// A3 (b) has the atlas deltas).
Bool sauStepZ      = True;
Bool sauStepRecomp = True;
// STEP 2 (2026-11-25), THE M+ FAMILY (SauStMem, SauStOne):
//   * sauStepMemRecomp: Table 3's M+ / M+MG "Unlike signs AB > CD, add
//     .6(x/y + 1) to the execution time": the recomplement pass over the
//     stored field (Fig. 3.11.11 Part 4's recomplement column, R23-9732
//     PDF 265), when the unit's subtraction has no end carry -- the
//     accumulator's field (AB, the complemented one here) the larger.
//     x/y is the stepped field, the sign byte's pass included: MEASURED,
//     PDF 119's signed M+MG INVERT rows print 2(b + 1) over the like rows
//     with b counting the sign byte (fidelity_plan.md A3 (b) step 2).
//   * sauStepOneCarry: M+1's .6(c + 1), c "the number of times a carry
//     results from an 8 bit byte in binary or a 4 bit byte in decimal"
//     (glossary printed p.3-10, PDF 28): the add-one loop runs from the
//     low byte while a carry comes out of it (Fig. 3.11.2's exit on
//     "like signs and no carry", sau_pau_spec.md section 5).  Off: c = 0.
//   * sauStepOneComp: M+1's unlike signs, ".6(x/y) when true result or
//     .6(2x/y + 1) when complement result" (Table 3's comment column).
//     Off: the true-result count for both.
// STEP 3 (2026-11-25), THE K FAMILY (SauStCmp, SauStCmpF):
//   * sauStepCmpW: K / KE / KR's w/r, "the number of accumulator
//     significant bits greater than the field length" (glossary printed
//     p.3-10, PDF 28) over r.  STEPPED AS ONE PASS when the accumulator
//     has any significant digit beyond the field, none when it has none:
//     DERIVED, the loop past the field ends at the first nonzero byte,
//     which decides the compare.  The literal count (every byte up to
//     the highest significant one) is contradicted by PDF 127-129: K
//     prints exactly one byte over KF at every field below 64 bits
//     against the 64-bit standard operand, where w/r would be 12 bytes at
//     (DU,16,4), and none at a whole unsigned word, where w = 0
//     (fidelity_plan.md A3 (b) step 3 has both measured).
//   * sauStepCmpEarly: the compare decided by the signs (unlike, neither
//     a zero) ends early: the sign byte's pass, one data pass, and K's w
//     pass.  The "+28" of fidelity_plan.md A3: PDF 127-132's INVERT SIGN
//     blocks print 12 unsigned and 14 signed at every length.  DERIVED
//     from sau_pau_spec.md section 5 (3 of 9 paths of Fig. 3.11.12 reach
//     TON SIR without EOC1/EOC2); the pass count is read off the pages.
Bool sauStepCmpW     = True;
// THE LITERAL READING, kept as a switch so the measurement can be re-run:
// w/r = the digits from the field's top up to the accumulator's highest
// significant one.  MEASURED and REJECTED (fidelity_plan.md A3 (b) step
// 3); False is the model.
Bool sauStepCmpWLiteral = False;
Bool sauStepCmpEarly = True;
// STEP 4 (2026-11-26), DECIMAL SRD'S ROUND (SauStRnd): TWO passes.  Fig.
// 3.11.11 Part 2 (R23-9732 PDF 265; sau_pau_spec.md) draws the round as
// two cycles before the store loop: [TOF HK TON RSU] (BAAB moved a digit
// below the field, ADD 4 TO BAAB) and [TOF RSU TON RND] (the digit read
// out with a hot 4 & 1, the carry saved).  Table 3 (printed p.3-7)
// charges SRD a pre-execution of 3.0 us against ST's 1.8: 1.2 us = two
// 0.6 us cycles.  The two agree, and are eboxClocks' 4-clock srdRound.
Integer sauRndPasses = 2;
// STEP 5 (2026-11-26), THE CONVERTERS: sauStepCvtAcc, CV / DCV's
// accumulator terms (s, and u/8 binary to decimal) stepped from the data
// (SauCvtSteps).  Off: only the equations' constants.  The core asks DCV
// decimal-to-binary without them (fidelity_plan.md A3 (b) step 5).
// INJECTION OBSERVED 2026-11-26: False fails mkSauStepTb 24 (6 against
// 26), 25 (4 against 10) and 26 (4 against 6); the rest pass.  The field
// term ignored (rg_cnp <= 1 + sp) fails 26 (4 against 6) and 27 (6
// against 22); the rest pass.
Bool sauStepCvtAcc = True;
Bool sauStepMemRecomp = True;
Bool sauStepOneCarry  = True;
Bool sauStepOneComp   = True;

// Multiplier: SOURCED, Buchholz printed p.210, "12 bits of the multiplier
// are handled in one cycle".  A width, so a typedef; it must divide 48.
typedef 12 SauMulGroup;
Integer sauMulBits  = valueOf(SauMulGroup);
Integer sauMulWidth = 48;
// Converter: CHOSEN (mkCvtBox's cvtBitsPerCycle / cvtDigitsPerCycle), to
// fit DCV's budget.
Integer sauCvtBinBits = 96;
Integer sauCvtBits    = 16;
Integer sauCvtDigits  = 8;

// ---------------------------------------------------------------------
// THE REQUESTS AND ANSWERS OF EACH CLASS, as the E-box's arms build and
// read them (StretchExecute.bsv's BoxReq / BoxRsp keep a tag per class,
// so `boxKindOf` still names the class: StretchCore releases the level
// for the adder (1) and the multiplier (3), not the converter (2)).
// ---------------------------------------------------------------------
// >>> THE PASSES OF AN ADD (half (b), 2026-11-25). <<<  What the unit
// needs to step a request as Fig. 3.11.9 (R23-9732 PDF 263; sau_pau_spec
// §10) steps it, and to time it as Perf. Char. Vol. 1 Table 3 (printed
// p.3-7, PDF 25; glossary printed p.3-10, PDF 28) counts it, at 0.6 us =
// 2 clocks a pass (Buchholz printed p.209, PDF 234):
//   * `passes`: the field's passes, data bytes (x/y) plus the sign byte's
//     pass when signed (StretchVFL's vflBytes).  0 = NOT STEPPED: the
//     unit answers when its datapath has the sum, and the caller's budget
//     keeps the whole eboxClocks row (half (a)'s contract), for every
//     caller not yet moved over (the M+ family, the K family, SRD).
//   * `top`: where the carry is looked at after the field, for Table 3's
//     z: binary, the bit just above the data (offset + x); decimal, the
//     digit just above it (offset/4 + x/y).
//   * `osb`: the bytes below the field, Table 3's os/r (os = the offset,
//     r = 8 binary, 4 decimal), for the recomplement.
//   * `b0`: the data bytes, x/y, for the recomplement.
//   * `mg`: ADD TO MAGNITUDE, whose unlike-signed "CD > AB" result is
//     cleared, not recomplemented: Table 3 charges it .6, one pass.
//   * `cls` (step 2 on, 2026-11-25): WHICH Table 3 equation steps it
//     (SauStepCls below).  `mg` above is SauStAdd's alone.
//   * `early`: SauStCmp / SauStCmpF only, the signs decide the compare
//     (the caller's as / bs, unlike): the compare ends at the sign.
// THE CLASSES, one Table 3 row group each (Vol. 1 printed p.3-7, PDF 25):
//   SauStAdd  +, +MG, L, LWF: .6(x/y + z); unlike CD > AB .6(os/r + x/y +
//             z + 1) for +, .6 for +MG                       (step 1)
//   SauStMem  M+, M+MG: .6(x/y); unlike AB > CD add .6(x/y + 1)
//   SauStOne  M+1: .6(c + 1); unlike .6(x/y) true result, .6(2x/y + 1)
//             complement result
//   SauStCmp  K, KE, KR: .6(x/y + w/r)
//   SauStCmpF KF, KFE, KFR: .6(x/y)
//   SauStRnd  SRD's round: Table 3's pre-execution 3.0 against ST's 1.8
typedef enum { SauStAdd, SauStMem, SauStOne, SauStCmp, SauStCmpF, SauStRnd }
  SauStepCls deriving (Bits, Eq, FShow);

typedef struct {
  Bit#(8) passes;
  Bit#(8) top;
  Bit#(8) osb;
  Bit#(8) b0;
  Bool    mg;
  SauStepCls cls;
  Bool    early;
} SauAddSteps deriving (Bits, Eq, FShow);

SauAddSteps sauNoSteps = SauAddSteps { passes: 0, top: 0, osb: 0, b0: 0, mg: False,
                                       cls: SauStAdd, early: False };

typedef struct {
  Bit#(128) a;     // 32 BCD digits, digit 0 in bits 3:0
  Bit#(128) b;
  Bool      sub;   // True: effective signs unlike, compute |a - b|
  Bool      binary;  // True: decimal correction off (p.209): a and b
                     // are 128-bit binary magnitudes, r likewise
  SauAddSteps steps; // the passes to step (sauNoSteps: not stepped)
} DecReq deriving (Bits, Eq, FShow);

typedef struct {
  Bit#(128) r;     // the result magnitude, 32 BCD digits
  // like signs: the carry out of digit 31 (Lost Carry).
  // unlike signs: True if a >= b (end carry, no recomplement), False
  // if the result was recomplemented (b > a).
  Bool      carry;
} DecRsp deriving (Bits, Eq, FShow);

// THE MULTIPLY REQUEST: the two 48-bit magnitudes, already truncated to
// their low 48 bits by the caller (printed p.68: "only the 48 low-order
// bits of the oversized operand are used").  Signs and Partial Field
// stay with the caller.
typedef struct {
  Bit#(48) mcand;   // the multiplicand
  Bit#(48) mpr;     // the multiplier, consumed twelve bits a cycle
} VflMulReq deriving (Bits, Eq, FShow);

typedef union tagged {
  VflMulReq VflMul;
} VflReq deriving (Bits, Eq, FShow);

typedef struct {
  Bit#(96) prod;    // the 96-bit product (48 x 48)
} VflRsp deriving (Bits, Eq, FShow);

// THE PASSES OF A CONVERSION (half (b) step 5, 2026-11-26): `fixed` is
// what the field decides (StretchVFL's vflCvtFieldPasses; 0 = NOT STEPPED,
// half (a)'s contract); `accS`, for CV and DCV, adds Table 3's
// accumulator terms, stepped from the data: s (binary: the source's
// significant bits; decimal: its significant digits, s/4) and, binary to
// decimal, u/8 (the result's significant digits, two a byte).
typedef struct {
  Bit#(16) fixed;
  Bool     accS;
} SauCvtSteps deriving (Bits, Eq, FShow);

SauCvtSteps sauCvtNoSteps = SauCvtSteps { fixed: 0, accS: False };

typedef struct {
  Bool      toDec;   // True: binary -> decimal
  Bit#(128) v;       // toDec: the binary value (low 96 bits used);
                     // else 32 BCD digits, digit 0 in bits 3:0
  SauCvtSteps steps; // half (b): the passes (sauCvtNoSteps: not stepped)
} CvtReq deriving (Bits, Eq, FShow);

typedef struct {
  Bit#(128) r;       // toDec: 32 BCD digits; else the binary value
} CvtRsp deriving (Bits, Eq, FShow);

// THE UNIT'S OWN REQUEST: one of the three classes.
typedef union tagged {
  DecReq SauAdd;
  VflReq SauMul;
  CvtReq SauCvt;
} SauReq deriving (Bits, Eq, FShow);

// THE UNIT'S OWN ANSWER: the result register and the end carry.  Each
// class reads its own view of it (sauDecRsp / sauVflRsp / sauCvtRsp).
typedef struct {
  Bit#(128) r;
  Bool      carry;   // the adder's; meaningless for the other classes
} SauRsp deriving (Bits, Eq, FShow);

function DecRsp sauDecRsp(SauRsp s) = DecRsp { r: s.r, carry: s.carry };
function VflRsp sauVflRsp(SauRsp s) = VflRsp { prod: truncate(s.r) };
function CvtRsp sauCvtRsp(SauRsp s) = CvtRsp { r: s.r };

// ONE DECIMAL DIGIT STEP: binary add of two digits and a carry; above
// nine, subtract ten (add six, drop the fifth bit) and carry one.
function Tuple2#(Bit#(4), Bit#(1)) decDigitStep(Bit#(4) x, Bit#(4) y, Bit#(1) c);
  Bit#(5) s = zeroExtend(x) + zeroExtend(y) + zeroExtend(c);
  if (s > 9) return tuple2(truncate(s - 10), 1);
  else       return tuple2(truncate(s), 0);
endfunction

// The nines' complement of one digit.
function Bit#(4) nines(Bit#(4) d) = 4'd9 - d;

// THE SERIAL ADDER'S STEP, with the decimal correction switched in or
// not (p.209).  Binary: a plain four-bit add, the carry out of bit 3.
function Tuple2#(Bit#(4), Bit#(1)) sauDigitStep(Bool bin, Bit#(4) x, Bit#(4) y, Bit#(1) c);
  Bit#(5) s = zeroExtend(x) + zeroExtend(y) + zeroExtend(c);
  return bin ? tuple2(s[3:0], s[4]) : decDigitStep(x, y, c);
endfunction

// The complement before (and after) the adder: inversion for binary,
// nines' for decimal.
function Bit#(4) sauComp(Bool bin, Bit#(4) d) = bin ? ~d : nines(d);

// One double-dabble step: adjust every digit of five or more by three,
// then shift the bit in.
function Bit#(128) dabble(Bit#(128) d, Bit#(1) b);
  for (Integer k = 0; k < 32; k = k + 1) begin
    Bit#(4) dg = d[4*k+3:4*k];
    if (dg >= 5) d[4*k+3:4*k] = dg + 3;
  end
  return { d[126:0], b };
endfunction

// TABLE 3's z, from the carries INTO each position (`cv`: binary, bit p
// is the carry into bit p; decimal, bit k is the carry into digit k).
// The passes after the field: one for each byte from `top` up while the
// carry into it is the propagating one (1 like signs, 0 -- a borrow --
// unlike), and while there is a byte there (EOA1: the accumulator's left
// end, bit 127 / digit 31).  Whether the propagation ran off the left end
// is the end carry itself (like signs: the Lost Carry; unlike, its
// absence: the recomplement), so it is not recounted here.
function Bit#(8) sauZ(Bool bin, Bool sub, Bit#(128) cv, Bit#(8) top);
  Bit#(1) prop = sub ? 0 : 1;
  Bit#(8) z = 0;
  Bool    go = True;
  for (Integer j = 0; j < 32; j = j + 1) begin
    Bit#(9) p = zeroExtend(top) + (bin ? fromInteger(8 * j) : fromInteger(j));
    Bool there = bin ? (p < 128) : (p < 32);
    if (go && there) begin
      if (cv[p[6:0]] == prop) z = z + 1;
      else go = False;
    end
  end
  return z;
endfunction

// M+1's c (Table 3; glossary printed p.3-10): the carries out of the
// decimal digits from the low one up, counted while they come -- the
// carries INTO digits `from`, from + 1, ... (`cv`, as sauZ's), stopping
// at the first absent one or at digit `to` (the field's top: a carry
// into it is the carry out of the field's last digit, counted, and the
// loop goes no further).
function Bit#(8) sauRun(Bit#(128) cv, Integer from, Bit#(8) to);
  Bit#(8) c  = 0;
  Bool    go = True;
  for (Integer j = from; j < 32; j = j + 1) begin
    Bool there = fromInteger(j) <= to;
    if (go && there) begin
      if (cv[j] == 1) c = c + 1;
      else go = False;
    end
  end
  return c;
endfunction

// The literal w/r (decimal): the digits of `a` from digit `top` up to its
// highest nonzero one (0 if none).  sauStepCmpWLiteral only.
function Bit#(8) sauSigDigitsAbove(Bit#(128) a, Bit#(8) top);
  Bit#(8) n = 0;
  for (Integer j = 0; j < 32; j = j + 1) begin
    Bit#(4) dg = a[4*j+3:4*j];
    Bit#(8) jj = fromInteger(j);
    if (jj >= top && dg != 0)
      n = jj + 1 - top;
  end
  return n;
endfunction

// Significant bits of a binary value / significant digits of a BCD one
// (the position of the highest nonzero one, plus one; 0 for zero).
function Bit#(16) sauSigBits(Bit#(128) v);
  Bit#(16) n = 0;
  for (Integer j = 0; j < 128; j = j + 1)
    if (v[j] == 1) n = fromInteger(j + 1);
  return n;
endfunction
function Bit#(16) sauSigDigits(Bit#(128) v);
  Bit#(16) n = 0;
  for (Integer j = 0; j < 32; j = j + 1) begin
    Bit#(4) dg = v[4*j+3:4*j];
    if (dg != 0) n = fromInteger(j + 1);
  end
  return n;
endfunction

interface SAU;
  method Action request(SauReq r);
  method Bool responseReady();
  // A VALUE, with no implicit condition, as mkDivBox's is: see that
  // interface's note (a guarded response() became the condition of the
  // whole of mkEBox.resume()).
  method SauRsp response();
  // THE UNIT'S OWN TIME (half (b)): Valid while the answer is a stepped
  // add's (SauAddSteps.passes != 0), and then the clocks its passes took,
  // which responseReady() has waited for.  The E-box charges it in place
  // of the row's byte term (StretchCore's rl_exec_resume).  Invalid for
  // every request that was not stepped.
  // THE TERMINATION (fidelity_plan.md A5 step 1, 2026-11-26).  The part
  // of an instruction's E-box time that the unit does not yet step -- what
  // is left of the timing row once the unit's own clocks are taken off,
  // or the whole row for an instruction the unit does not step at all --
  // runs here, from the answer, as the row's fixed part does on the
  // machine ("END OPN").  It was StretchCore's E-box countdown register.  The
  // look-ahead's head waits on terminated() of BOTH units (the E-box is
  // one unit to Perf. Char. Vol. 1 printed pp.3-17/3-18); it is
  // independent of the datapath state, so a request (an I-box
  // instruction's, beside) may run during it.
  //   terminate(n) -- the instruction just completed owes n more clocks;
  //   holdTerm()   -- this clock does not count (StretchCore calls it in
  //                   the clock after one in which no instruction-unit arm
  //                   fired, which is when that register did not count down);
  //   terminated() -- nothing is owed.
  method Action terminate(Bit#(16) n);
  method Action holdTerm();
  method Bool terminated();
  method Maybe#(Bit#(16)) ownClocks();
endinterface

typedef enum { SauIdle, SauAddPass, SauRecomp, SauMulPass, SauToDec, SauToBin, SauDone }
  SauState deriving (Bits, Eq, FShow);

(* synthesize *)
module mkSAU(SAU);

  // THE TERMINATION (the interface note).  rg_term holds the clocks owed
  // PLUS ONE: terminate() writes port 1 after this clock's reads, and
  // rl_term takes one off at the start of every following clock that is
  // not held, so terminated() -- read on port 1, after rl_term -- sees in
  // clock c+k exactly what that register held in clock c+k (n, n-1, ... 0).
  Reg#(Bit#(16)) rg_term[2] <- mkCReg(2, 0);
  PulseWire      pw_termHold <- mkPulseWire;
  rule rl_term (rg_term[0] != 0 && !pw_termHold);
    rg_term[0] <= rg_term[0] - 1;
  endrule
  // CREGS WITH THE PORT ASSIGNMENT AS THE SCHEDULE, for the reason
  // mkDivBox gives (StretchPAU.bsv, now mkPAU): the rules use port 0 and every
  // method port 1, so the rules come before the methods and a caller
  // rule may poll, take and re-request in one clock -- and the answer of
  // a last pass is readable in the clock of that pass.
  Reg#(SauState)  rg_state[2] <- mkCReg(2, SauIdle);
  // THE OPERAND REGISTER: the adder's augend (leaving at the bottom a
  // pass-width at a time), the converter's source (leaving at the top),
  // the multiplicand (low 48 bits, held).
  Reg#(Bit#(128)) rg_a[2]     <- mkCReg(2, 0);
  // The adder's addend, already complemented for a subtraction.
  Reg#(Bit#(128)) rg_b[2]     <- mkCReg(2, 0);
  // THE RESULT REGISTER: the adder's sum (digits entering at the top, so
  // after a pass it holds all 32), the converter's result, the product
  // register (low 96 bits: the multiplier starts in the low 48 and
  // leaves at the bottom twelve bits a pass while the partial product
  // grows in from the top).
  Reg#(Bit#(128)) rg_r[2]     <- mkCReg(2, 0);
  Reg#(Bit#(1))   rg_c[2]     <- mkCReg(2, 0);
  Reg#(Bool)      rg_sub[2]   <- mkCReg(2, False);
  Reg#(Bool)      rg_bin[2]   <- mkCReg(2, False);
  Reg#(Bool)      rg_carry[2] <- mkCReg(2, False);
  Reg#(Bit#(8))   rg_ctr[2]   <- mkCReg(2, 0);
  // HALF (b): the stepped add's passes, the carries into each position
  // (sauZ's `cv`), the clocks since the request, and the stepped time
  // (set when the add pass ends; responseReady waits for it).
  Reg#(SauAddSteps) rg_steps[2] <- mkCReg(2, sauNoSteps);
  Reg#(Bit#(128)) rg_cv[2]    <- mkCReg(2, 0);
  Reg#(Bit#(16))  rg_el[2]    <- mkCReg(2, 0);
  Reg#(Bit#(16))  rg_own[2]   <- mkCReg(2, 0);
  // Step 3: a significant digit of `a` beyond the field (`top` on), the
  // compare's w pass (sauStepCmpW).  Set at the request.
  Reg#(Bool)      rg_w[2]     <- mkCReg(2, False);
  Reg#(Bit#(8))   rg_wn[2]    <- mkCReg(2, 0);   // the literal w/r's count
  // Step 5: a stepped conversion's passes so far (the field's and s, set
  // at the request; u/8 added when the result is known), and whether the
  // conversion is stepped.
  Reg#(SauCvtSteps) rg_cst[2] <- mkCReg(2, sauCvtNoSteps);
  Reg#(Bit#(16))  rg_cnp[2]   <- mkCReg(2, 0);

  Integer addClocks = sauDigits / sauAddDigits;
  Integer mulClocks = sauMulWidth / sauMulBits;
  Integer decClocks = sauCvtBinBits / sauCvtBits;
  Integer binClocks = sauDigits / sauCvtDigits;
  if (addClocks * sauAddDigits != sauDigits)
    error("mkSAU: sauAddDigits must divide 32");
  if (mulClocks * sauMulBits != sauMulWidth)
    error("mkSAU: SauMulGroup must divide 48");
  if (decClocks * sauCvtBits != sauCvtBinBits)
    error("mkSAU: sauCvtBits must divide 96");
  if (binClocks * sauCvtDigits != sauDigits)
    error("mkSAU: sauCvtDigits must divide 32");

  // THE ADDER: the add pass and the recomplement pass through ONE chain
  // of digit steps.  Add: a + b (b already complemented for a
  // subtraction, with the initial carry one).  Recomplement: the
  // complement of the first pass's sum, plus the carry of one.
  // THE CLOCK OF A REQUEST (half (b)): clocks since it, saturating.  A
  // request writes 0 at port 1, so in the k-th clock after it this reads k.
  rule rl_tick (rg_el[0] != '1);
    rg_el[0] <= rg_el[0] + 1;
  endrule

  rule rl_add (rg_state[0] == SauAddPass || rg_state[0] == SauRecomp);
    Bool      rec = (rg_state[0] == SauRecomp);
    Bool      bin = rg_bin[0];
    Bit#(128) a = rg_a[0];
    Bit#(128) b = rg_b[0];
    Bit#(1)   c = rg_c[0];
    Bit#(128) r = rg_r[0];
    // The decimal carries INTO each digit, for sauZ (the add pass only;
    // a binary request's per-bit carries were taken at the request).
    Bit#(128) cv = rg_cv[0];
    Bit#(8)   d0 = (fromInteger(sauDigits / sauAddDigits) - rg_ctr[0]) * fromInteger(sauAddDigits);
    for (Integer k = 0; k < sauAddDigits; k = k + 1) begin
      Bit#(4) x = rec ? sauComp(bin, a[3:0]) : a[3:0];
      Bit#(4) y = rec ? 0 : b[3:0];
      if (!rec && !bin) cv[d0 + fromInteger(k)] = c;
      match {.d, .c2} = sauDigitStep(bin, x, y, c);
      c = c2;
      a = a >> 4;
      b = b >> 4;
      r = { d, r[127:4] };
    end
    rg_cv[0] <= cv;
    Bit#(8)  ctr = rg_ctr[0] - 1;
    SauState st  = rg_state[0];
    if (rg_ctr[0] == 1) begin
      if (!rec) begin
        // THE STEPPED TIME (half (b)), now that every carry is known:
        // the field's passes, z, and the recomplement if there is one.
        SauAddSteps sp = rg_steps[0];
        Bool     rcp = rg_sub[0] && c == 0;
        // A borrow that runs to the left end is NOT stepped byte by byte:
        // Table 3 charges +MG's "CD > AB" .6 and nothing for the bytes
        // beyond the field (and + its recomplement alone).  MEASURED, on
        // the atlas: counting those passes put +MG INVERT (DU,64,4) 34
        // clocks over PDF 118 (fidelity_plan.md A3 (b)).  DERIVED: Fig.
        // 3.11.9's EHOM1 test (the accumulator's high-order end) ends the
        // loop where nothing beyond is significant.
        Bit#(8)  z   = rcp ? 0 : sauZ(bin, rg_sub[0], cv, sp.top);
        Bit#(16) p16 = zeroExtend(sp.passes);
        Bit#(16) np  = p16;
        case (sp.cls)
          SauStAdd:
            np = p16
               + (sauStepZ ? zeroExtend(z) : 0)
               + ((sauStepRecomp && rcp)
                  ? (sp.mg ? 1 : zeroExtend(sp.osb) + zeroExtend(sp.b0) + zeroExtend(z) + 1)
                  : 0);
          // M+, M+MG: the field's passes, and on AB > CD the
          // recomplement's x/y + 1 (sauStepMemRecomp's note).  No z:
          // Table 3 charges none -- the carry out of the field is the Lost
          // Carry, and Fig. 3.11.11 takes "CYCLES ... FOR PF CK ONLY" after
          // EOC2, which Table 3 does not count.
          SauStMem:
            np = p16 + ((sauStepMemRecomp && rcp) ? p16 + 1 : 0);
          // M+1: like signs, c + 1 (the carries out of the bytes from the
          // low one up, while they come); unlike, x/y, or 2x/y + 1 when
          // the result is complemented (sauStepOne*'s notes).
          SauStOne:
            np = !rg_sub[0]
               ? (sauStepOneCarry ? zeroExtend(sauRun(cv, 1, sp.top)) + 1 : 1)
               : ((sauStepOneComp && rcp) ? 2 * p16 + 1 : p16);
          // K, KE, KR (with w) and KF, KFE, KFR: the field's passes, or
          // on a decision at the signs the sign pass, one data pass and w
          // (sauStepCmp*'s notes).
          SauStCmp, SauStCmpF: begin
            Bit#(16) w = (sp.cls != SauStCmp || !sauStepCmpW) ? 0
                       : sauStepCmpWLiteral ? zeroExtend(rg_wn[0])
                       : (rg_w[0] ? 1 : 0);
            Bit#(16) s = zeroExtend(sp.passes - sp.b0);
            np = (sauStepCmpEarly && sp.early) ? s + 1 + w : p16 + w;
          end
          default: np = p16;
        endcase
        // AN UNSTEPPED REQUEST KEEPS HALF (a)'s TIME, 4 clocks or 8
        // recomplemented, though the datapath now has the sum in 2 or 4.
        // MEASURED: letting the M+ and K families answer at the new
        // datapath's 2 moved their one-digit atlas cases 1 clock faster,
        // away from the pages, as the relocation step did for the stepped
        // ones, with no source behind the move (fidelity_plan.md A3 (b)).
        // They move when they are stepped, not before.
        rg_own[0] <= (sp.passes == 0) ? (rcp ? 8 : 4) : 2 * np;
        rg_carry[0] <= (c == 1);
        if (rg_sub[0] && c == 0) begin
          // No end carry: a < b, and r is the tens' complement of b - a.
          // RECOMPLEMENT: one more pass of complement plus one.
          a   = r;
          c   = 1;
          ctr = fromInteger(addClocks);
          st  = SauRecomp;
        end else
          st  = SauDone;
      end else
        st = SauDone;
    end
    rg_a[0] <= a; rg_b[0] <= b; rg_c[0] <= c; rg_r[0] <= r;
    rg_ctr[0] <= ctr; rg_state[0] <= st;
  endrule

  // THE MULTIPLIER (the parallel unit's, until A4: header).  ONE PASS:
  // the low twelve multiplier bits times the multiplicand, added into
  // the high half, and the product register shifted right twelve.
  rule rl_mul (rg_state[0] == SauMulPass);
    Bit#(96)          p  = truncate(rg_r[0]);
    Bit#(48)          hi = p[95:48];
    Bit#(48)          lo = p[47:0];
    Bit#(SauMulGroup) g  = truncate(lo);
    Bit#(48)          mc = truncate(rg_a[0]);
    // unsignedMul is UInt#(n) x UInt#(m) -> UInt#(n+m): a 48 x 12
    // multiplier, exactly the width of the pass and no wider.
    Bit#(TAdd#(48, SauMulGroup)) pp =
      pack(unsignedMul(UInt#(48)'(unpack(mc)), UInt#(SauMulGroup)'(unpack(g))));
    Bit#(TAdd#(TAdd#(48, SauMulGroup), 1)) s = zeroExtend(hi) + zeroExtend(pp);
    // {s, lo} >> 12: the partial product can never exceed 96 bits (after
    // k passes it is below 2^(48 + 12k) and sits 48 - 12k bits up), so
    // the truncation drops only zeros.
    Bit#(96) np = truncate({s, lo} >> sauMulBits);
    rg_r[0] <= zeroExtend(np);
    rg_ctr[0] <= rg_ctr[0] - 1;
    if (rg_ctr[0] == 1) rg_state[0] <= SauDone;
  endrule

  // THE CONVERTER, binary to decimal: double dabble, `sauCvtBits` bits a
  // clock off the top of the 96-bit source.
  rule rl_todec (rg_state[0] == SauToDec);
    Bit#(128) s = rg_a[0];
    Bit#(128) r = rg_r[0];
    for (Integer k = 0; k < sauCvtBits; k = k + 1) begin
      r = dabble(r, s[95]);
      s = s << 1;
    end
    rg_a[0] <= s; rg_r[0] <= r;
    rg_ctr[0] <= rg_ctr[0] - 1;
    if (rg_ctr[0] == 1) begin
      rg_state[0] <= SauDone;
      // Half (b) step 5: binary to decimal adds u/8 for CV / DCV, the
      // result's digits two a pass; the time is never shorter than the
      // datapath's own (decClocks).
      Bit#(16) u8 = (rg_cst[0].accS && sauStepCvtAcc) ? (sauSigDigits(r) + 1) / 2 : 0;
      Bit#(16) np = rg_cnp[0] + u8;
      if (rg_cst[0].fixed != 0) rg_own[0] <= max(2 * np, fromInteger(decClocks));
    end
  endrule

  // ... and decimal to binary: Horner, `sauCvtDigits` digits a clock off
  // the top.
  rule rl_tobin (rg_state[0] == SauToBin);
    Bit#(128) s = rg_a[0];
    Bit#(128) r = rg_r[0];
    for (Integer k = 0; k < sauCvtDigits; k = k + 1) begin
      r = (r << 3) + (r << 1) + zeroExtend(s[127:124]);
      s = s << 4;
    end
    rg_a[0] <= s; rg_r[0] <= r;
    rg_ctr[0] <= rg_ctr[0] - 1;
    if (rg_ctr[0] == 1) begin
      rg_state[0] <= SauDone;
      if (rg_cst[0].fixed != 0) rg_own[0] <= max(2 * rg_cnp[0], fromInteger(binClocks));
    end
  endrule

  // NO IMPLICIT CONDITIONS, for mkDivBox's reason.  A request starts the
  // unit afresh whatever it was doing; every register a class reads is
  // written here, so nothing of a previous class's run survives into it
  // (mkSauMixTb below checks a sequence of mixed classes).
  method Action request(SauReq q);
    case (q) matches
      tagged SauAdd .d: begin
        Bit#(128) bc = d.b;
        if (d.sub)
          for (Integer k = 0; k < sauDigits; k = k + 1)
            bc[4*k+3:4*k] = sauComp(d.binary, d.b[4*k+3:4*k]);
        rg_a[1]     <= d.a;
        rg_b[1]     <= bc;
        rg_r[1]     <= 0;
        rg_c[1]     <= d.sub ? 1 : 0;
        rg_sub[1]   <= d.sub;
        rg_bin[1]   <= d.binary;
        // Half (b): a binary add's carry into every bit is a ^ b ^ sum of
        // the plain 128-bit add the binary chain makes; a decimal add's
        // carries into each digit are recorded by rl_add as it goes.
        Bit#(128) bsum = d.a + bc + (d.sub ? 1 : 0);
        rg_cv[1]    <= d.binary ? (d.a ^ bc ^ bsum) : 0;
        rg_steps[1] <= d.steps;
        rg_cst[1]   <= sauCvtNoSteps;
        rg_w[1]     <= !d.binary && ((d.a >> {d.steps.top, 2'b00}) != 0);
        rg_wn[1]    <= d.binary ? 0 : sauSigDigitsAbove(d.a, d.steps.top);
        rg_el[1]    <= 0;
        rg_own[1]   <= 0;
        rg_ctr[1]   <= fromInteger(addClocks);
        rg_state[1] <= SauAddPass;
      end
      tagged SauMul (tagged VflMul .m): begin
        rg_a[1]     <= zeroExtend(m.mcand);
        rg_r[1]     <= zeroExtend(m.mpr);
        rg_steps[1] <= sauNoSteps;
        rg_cst[1]   <= sauCvtNoSteps;
        rg_own[1]   <= 0;
        rg_el[1]    <= 0;
        rg_ctr[1]   <= fromInteger(mulClocks);
        rg_state[1] <= SauMulPass;
      end
      tagged SauCvt .v: begin
        rg_a[1]     <= v.toDec ? (v.v & ((128'd1 << 96) - 1)) : v.v;
        rg_r[1]     <= 0;
        rg_steps[1] <= sauNoSteps;
        rg_own[1]   <= 0;
        rg_el[1]    <= 0;
        // Half (b) step 5: the field's passes and, for CV / DCV, s (binary:
        // significant bits of the 96-bit source; decimal: its significant
        // digits, Table 3's s/4).
        Bit#(128) vs = v.toDec ? (v.v & ((128'd1 << 96) - 1)) : v.v;
        Bit#(16)  sp = (v.steps.accS && sauStepCvtAcc)
                     ? (v.toDec ? sauSigBits(vs) : sauSigDigits(vs)) : 0;
        rg_cst[1]   <= v.steps;
        rg_cnp[1]   <= v.steps.fixed + sp;
        rg_ctr[1]   <= fromInteger(v.toDec ? decClocks : binClocks);
        rg_state[1] <= v.toDec ? SauToDec : SauToBin;
      end
    endcase
  endmethod

  // A stepped add is ready when its passes have been stepped as well as
  // its sum made (the datapath is never the slower: sauAddDigits' note).
  method Bool responseReady() = (rg_state[1] == SauDone) && rg_el[1] >= rg_own[1];

  method SauRsp response() = SauRsp { r: rg_r[1], carry: rg_carry[1] };

  method Maybe#(Bit#(16)) ownClocks() =
    (rg_steps[1].passes != 0 || rg_cst[1].fixed != 0) ? tagged Valid rg_own[1] : tagged Invalid;
  method Action terminate(Bit#(16) n);
    rg_term[1] <= n + 1;
  endmethod
  method Action holdTerm();
    pw_termHold.send;
  endmethod
  method Bool terminated() = (rg_term[1] == 0);

endmodule

// =====================================================================
// THE UNIT'S OWN TESTBENCHES, testable without instantiating storage.
// The three single-class ones are the old boxes' own (mkDecBoxTb,
// mkVflBoxTb, mkCvtBoxTb), vector for vector, with their LITERAL answers
// and LITERAL clock counts, moved onto mkSAU; mkSauMixTb is new.
// =====================================================================

// ---------------------------------------------------------------------
// mkSauAddTb (was mkDecBoxTb).  THE EXPECTATIONS ARE LITERALS, worked by
// hand from p.60's rule -- not computed by a second decimal adder in the
// testbench.  Each vector also asserts a LITERAL clock count: 4 for a
// pass, 8 when the subtraction recomplements (unstepped: half (a)'s time).
//
// Vectors 0-4 ARE Reference Manual printed p.60's five ADD examples,
// with the accumulator as `a` and the storage operand shifted two digits
// (offset 8 bits) as `b`: 37600+ + 75679+, 45623+ + 53200-, 53200+ +
// 53200-, 53200- + 53200+, 53201+ + 53200-.
//
// Vectors 9-14 are the BINARY mode (2026-11-19), worked by hand as
// 128-bit binary: each has a digit above nine somewhere, or a ripple a
// decimal step would treat differently, so an adder that left the
// decimal correction switched in fails them.  (Vector 8 is the default arm,
// the full-width subtraction.)
//
// MEASURED INJECTIONS on mkDecBox, 2026-11-19 (each reverted, the file
// compared byte for byte with the saved good copy):
//   * sauDigitStep always decimal (the correction never switched off):
//     vectors 9-14 FAIL, 0-8 pass (the decimal control).
//   * sauComp always nines' (binary subtraction complemented as
//     decimal): vectors 11, 12, 13 FAIL -- exactly the unlike-sign
//     binary ones -- and 0-10 and 14 pass (decimal, and like-sign
//     binary, as controls).
// RE-RUN ON mkSAU, 2026-11-25 (the shared add/recomplement chain is new
// code): each injection made in a
// scratch copy of this file, never in the tree, and run on all four
// testbenches:
//   * sauComp always nines': add 11, 12, 13 FAIL, every other vector of
//     all four testbenches passes -- the old box's set, unchanged.
//   * the recomplement pass not complementing (`x = a[3:0]` on both
//     passes): add 1, 7 and 12 FAIL -- exactly the three recomplemented
//     vectors -- and mix 0, the recomplemented one there.
//   * the recomplement pass adding the addend (`y = b[3:0]` on both
//     passes): NOTHING fails, and nothing can: b leaves the register four
//     bits a digit, so after the add pass's 32 digits it is zero.  An
//     equivalent mutant, recorded so nobody spends a run on it.
// ---------------------------------------------------------------------
typedef 15 NDecVec;

(* synthesize *)
module mkSauAddTb(Empty);
  SAU            box    <- mkSAU;
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
      0: DecReq { a: 128'h37600, b: 128'h75679, sub: False, binary: False, steps: sauNoSteps };
      // example 2: acc 45623+, operand 53200-: unlike, a < b.
      1: DecReq { a: 128'h45623, b: 128'h53200, sub: True, binary: False, steps: sauNoSteps };
      // example 3: acc 53200+, operand 53200-: unlike, equal.
      2: DecReq { a: 128'h53200, b: 128'h53200, sub: True, binary: False, steps: sauNoSteps };
      // example 4: acc 53200-, operand 53200+: unlike, equal.
      3: DecReq { a: 128'h53200, b: 128'h53200, sub: True, binary: False, steps: sauNoSteps };
      // example 5: acc 53201+, operand 53200-: unlike, a > b.
      4: DecReq { a: 128'h53201, b: 128'h53200, sub: True, binary: False, steps: sauNoSteps };
      // 32 nines + 1: the carry out of digit 31 (Lost Carry).
      5: DecReq { a: 128'h99999999999999999999999999999999, b: 128'h1, sub: False, binary: False, steps: sauNoSteps };
      // a carry rippling across a pass boundary (digit 7 -> 8).
      6: DecReq { a: 128'h99999999, b: 128'h1, sub: False, binary: False, steps: sauNoSteps };
      // 0 - 1: recomplement to 1, across all 32 digits.
      7: DecReq { a: 128'h0, b: 128'h1, sub: True, binary: False, steps: sauNoSteps };
      // BINARY: 2^32 - 1 + 1, the carry rippling across the first
      // pass boundary (bit 31 -> 32).
      9: DecReq { a: 128'hFFFFFFFF, b: 128'h1, sub: False, binary: True, steps: sauNoSteps };
      // BINARY: 2^128 - 1 + 1: the carry out of bit 127 (Lost Carry).
      10: DecReq { a: '1, b: 128'h1, sub: False, binary: True, steps: sauNoSteps };
      // BINARY, unlike signs, a > b: 0x100 - 1 = 0xFF, end carry.
      11: DecReq { a: 128'h100, b: 128'h1, sub: True, binary: True, steps: sauNoSteps };
      // BINARY, unlike signs, a < b: 1 - 0x100, no end carry, so the
      // second pass recomplements to 0xFF.
      12: DecReq { a: 128'h1, b: 128'h100, sub: True, binary: True, steps: sauNoSteps };
      // BINARY, unlike signs, equal: zero with the end carry.
      13: DecReq { a: 128'h5A5A, b: 128'h5A5A, sub: True, binary: True, steps: sauNoSteps };
      // BINARY: 9 + 9 = 0x12 (eighteen); decimal correction would
      // make it 0x18.
      14: DecReq { a: 128'h9, b: 128'h9, sub: False, binary: True, steps: sauNoSteps };
      // full width: 10^31 - 1 against 10^31 + ... a > b by one digit.
      default: DecReq { a: 128'h10000000000000000000000000000000,
                        b: 128'h00000000000000000000000000000001, sub: True, binary: False, steps: sauNoSteps };
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
      9: DecRsp { r: 128'h100000000, carry: False };
      10: DecRsp { r: 128'h0,     carry: True };
      11: DecRsp { r: 128'hFF,    carry: True };
      12: DecRsp { r: 128'hFF,    carry: False };   // b - a, recomplemented
      13: DecRsp { r: 128'h0,     carry: True };
      14: DecRsp { r: 128'h12,    carry: False };
      default: DecRsp { r: 128'h09999999999999999999999999999999, carry: True };
    endcase;
  // 4 a pass, 8 recomplemented: these requests are not stepped
  // (sauNoSteps), so they keep half (a)'s time (rl_add's note), though the
  // datapath has had the sum in 2 / 4 since half (b).
  function Bit#(16) clocksOf(Bit#(4) i) = (i == 1 || i == 7 || i == 12) ? 8 : 4;

  rule rl_issue (!done && !issued);
    box.request(tagged SauAdd reqOf(idx));
    issued <= True;
    t0 <= clk;
  endrule

  rule rl_collect (!done && issued && box.responseReady());
    let got  = sauDecRsp(box.response());
    let want = wantOf(idx);
    Bit#(16) took = clk - t0;
    if (got != want) begin
      $display("FAIL sau add[%0d]: r=%h carry=%0d, want r=%h carry=%0d",
               idx, got.r, got.carry, want.r, want.carry);
      fails <= fails + 1;
    end else if (took != clocksOf(idx)) begin
      $display("FAIL sau add[%0d] clocks = %0d, want %0d", idx, took, clocksOf(idx));
      fails <= fails + 1;
    end else
      $display("PASS sau add[%0d] r=%h carry=%0d in %0d clocks", idx, got.r, got.carry, took);
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

// ---------------------------------------------------------------------
// mkSauMulTb (was mkVflBoxTb).  THE EXPECTATIONS ARE LITERALS, not a `*`
// in the testbench.  They were worked in Python's arbitrary-precision
// integers, a separate implementation, and two are checkable by hand:
// (2^48 - 1)^2 is 2^96 - 2^49 + 1, and 0x123456789ABC x 0xFFF is
// 0x123456789ABC000 - 0x123456789ABC.  Every vector also asserts a
// LITERAL clock count, 4 (Buchholz printed p.211's "four cycles").
//
// The vectors place multiplier bits in each twelve-bit group in turn:
//   0-1  trivial (0 x 0, 1 x 1)                        group 0 only
//   2    (2^48 - 1)^2, every bit of both operands      all groups
//   3    (2^48 - 1) x 2^12                             group 1 only
//   4    0x123456789ABC x 0xFFF                        group 0 only
//   5    0x123456789ABC x 0xFFF000                     group 1 only
//   6    (2^48 - 1) x 2^47, the top multiplier bit     group 3 only
//   7    a dense pattern across every group            all groups
//   8    (2^47 + 1)^2, the end bits of each operand    groups 0 and 3
//
// INJECTIONS on mkVflBox, OBSERVED 2026-11-18 (each reverted from a
// saved copy, verified with cmp):
//   * the top bit of every twelve-bit group dropped (`g = truncate(lo) &
//     12'h7FF`): FAILS 2, 4, 5, 6, 7 and 8 and PASSES 0, 1 and 3, the
//     control (their multiplier bits are 0, bit 0 and bit 12).
//   * the pass shift made eleven instead of twelve: fails every vector
//     but 0 (0 x 0).
// RE-RUN ON mkSAU, 2026-11-25: the top bit of every group
// dropped: mul 2, 4, 5, 6, 7 and 8 FAIL, and mix 2 (the all-ones
// square); mul 0, 1, 3 and every other testbench pass.  The old set.
// ---------------------------------------------------------------------
typedef 9 NVflVec;

(* synthesize *)
module mkSauMulTb(Empty);
  SAU            box    <- mkSAU;
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
    box.request(tagged SauMul (tagged VflMul reqOf(idx)));
    issued <= True;
    t0 <= clk;
  endrule

  rule rl_collect (!done && issued && box.responseReady());
    Bit#(96) got  = sauVflRsp(box.response()).prod;
    Bit#(96) want = wantOf(idx);
    Bit#(16) took = clk - t0;
    if (got != want) begin
      $display("FAIL sau mul[%0d]: prod=%h, want %h", idx, got, want);
      fails <= fails + 1;
    end else if (took != 4) begin
      $display("FAIL sau mul[%0d] clocks = %0d, want 4", idx, took);
      fails <= fails + 1;
    end else
      $display("PASS sau mul[%0d] prod=%h in %0d clocks", idx, got, took);
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

// ---------------------------------------------------------------------
// mkSauCvtTb (was mkCvtBoxTb).  The expectations are LITERALS (the
// decimal ones are the number written out; the binary ones were computed
// with Python integers, not with a second converter in Bluespec), and
// each vector asserts a literal clock count: 6 binary-to-decimal, 4 back.
//
//   0  2^96 - 1 = 79228162514264337593543950335 (29 digits, the most)
//   1  zero
//   2  one
//   3  10^24, the first 25-digit value (DCV's Partial Field boundary)
//   4  10^24 - 1, twenty-four nines
//   5  32 nines to binary = 10^32 - 1 = (16)4EE2D6D415B85ACEF80FFFFFFFF
//   6  1 to binary
//   7  1234 to binary = (16)4D2
// RE-RUN ON mkSAU, 2026-11-25: the dabble threshold made six
// (`dg >= 6`): cvt 0, 3 and 4 FAIL, and mix 1; cvt 1, 2 (no digit ever
// reaches five) and the decimal-to-binary 5-7 pass, as controls.
// ---------------------------------------------------------------------
typedef 8 NCvtVec;

(* synthesize *)
module mkSauCvtTb(Empty);
  SAU            box    <- mkSAU;
  Reg#(Bit#(4))  idx    <- mkReg(0);
  Reg#(Bit#(8))  fails  <- mkReg(0);
  Reg#(Bool)     issued <- mkReg(False);
  Reg#(Bool)     done   <- mkReg(False);
  Reg#(Bit#(16)) clk    <- mkReg(0);
  Reg#(Bit#(16)) t0     <- mkReg(0);

  rule rl_clk; clk <= clk + 1; endrule

  function CvtReq reqOf(Bit#(4) i) =
    case (i)
      0: CvtReq { toDec: True,  v: 128'hFFFFFFFFFFFFFFFFFFFFFFFF, steps: sauCvtNoSteps };
      1: CvtReq { toDec: True,  v: 0, steps: sauCvtNoSteps };
      2: CvtReq { toDec: True,  v: 1, steps: sauCvtNoSteps };
      3: CvtReq { toDec: True,  v: 128'hD3C21BCECCEDA1000000, steps: sauCvtNoSteps };
      4: CvtReq { toDec: True,  v: 128'hD3C21BCECCEDA0FFFFFF, steps: sauCvtNoSteps };
      5: CvtReq { toDec: False, v: 128'h99999999999999999999999999999999, steps: sauCvtNoSteps };
      6: CvtReq { toDec: False, v: 1, steps: sauCvtNoSteps };
      default: CvtReq { toDec: False, v: 128'h1234, steps: sauCvtNoSteps };
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
    box.request(tagged SauCvt reqOf(idx));
    issued <= True;
    t0 <= clk;
  endrule

  rule rl_collect (!done && issued && box.responseReady());
    Bit#(128) got = sauCvtRsp(box.response()).r;
    Bit#(16) took = clk - t0;
    if (got != wantOf(idx)) begin
      $display("FAIL sau cvt[%0d]: r=%h, want %h", idx, got, wantOf(idx));
      fails <= fails + 1;
    end else if (took != clocksOf(idx)) begin
      $display("FAIL sau cvt[%0d] clocks = %0d, want %0d", idx, took, clocksOf(idx));
      fails <= fails + 1;
    end else
      $display("PASS sau cvt[%0d] r=%h in %0d clocks", idx, got, took);
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

// ---------------------------------------------------------------------
// mkSauMixTb, NEW WITH THE MERGE (2026-11-25).  The three classes now
// share the operand, result, carry and counter registers, so a request
// must not see what the previous class left there.  This issues the
// classes back to back, each request in the clock the previous answer
// is taken (the same clock mkEBox can re-request in), in an order where
// a stale register would show:
//   0  add, decimal, recomplemented (p.60 example 2): leaves carry False
//      and the counter of a second pass
//   1  convert binary to decimal, 2^96 - 1: reuses rg_a as the source
//   2  multiply (2^48 - 1)^2: reuses rg_r as the product register,
//      holding the conversion's 29 digits when asked
//   3  add, binary, like signs, 2^128 - 1 + 1: must read carry True
//      (Lost Carry) after the multiply
//   4  convert decimal to binary, 32 nines: rg_r was the sum
//   5  add, decimal, 0 + 0: everything zero, carry False, 4 clocks
//   6  multiply 1 x 1 after a conversion that left rg_a shifted
// The answers and clock counts are the single-class vectors' literals.
// INJECTION, OBSERVED 2026-11-25: the converter's request not
// clearing the result register (`rg_r[1] <= 0` deleted from SauCvt):
// mix 1 FAILS (it follows an add that left 7577 there) and mix 4 passes
// (it follows a binary add whose sum was zero); in mkSauCvtTb every
// vector after the first fails (1-7), each seeing the last answer.  The
// other two testbenches pass.
// ---------------------------------------------------------------------
typedef 7 NMixVec;

(* synthesize *)
module mkSauMixTb(Empty);
  SAU            box    <- mkSAU;
  Reg#(Bit#(4))  idx    <- mkReg(0);
  Reg#(Bit#(8))  fails  <- mkReg(0);
  Reg#(Bool)     issued <- mkReg(False);
  Reg#(Bool)     done   <- mkReg(False);
  Reg#(Bit#(16)) clk    <- mkReg(0);
  Reg#(Bit#(16)) t0     <- mkReg(0);

  rule rl_clk; clk <= clk + 1; endrule

  function SauReq reqOf(Bit#(4) i) =
    case (i)
      0: tagged SauAdd DecReq { a: 128'h45623, b: 128'h53200, sub: True, binary: False, steps: sauNoSteps };
      1: tagged SauCvt CvtReq { toDec: True, v: 128'hFFFFFFFFFFFFFFFFFFFFFFFF, steps: sauCvtNoSteps };
      2: tagged SauMul (tagged VflMul VflMulReq { mcand: 48'hFFFFFFFFFFFF, mpr: 48'hFFFFFFFFFFFF });
      3: tagged SauAdd DecReq { a: '1, b: 128'h1, sub: False, binary: True, steps: sauNoSteps };
      4: tagged SauCvt CvtReq { toDec: False, v: 128'h99999999999999999999999999999999, steps: sauCvtNoSteps };
      5: tagged SauAdd DecReq { a: 0, b: 0, sub: False, binary: False, steps: sauNoSteps };
      default: tagged SauMul (tagged VflMul VflMulReq { mcand: 48'h1, mpr: 48'h1 });
    endcase;
  // The class's view of the answer, widened to 128 bits, and the carry
  // where the class has one.
  function Tuple2#(Bit#(128), Bool) viewOf(Bit#(4) i, SauRsp s) =
    case (i)
      0, 3, 5: tuple2(sauDecRsp(s).r, sauDecRsp(s).carry);
      1, 4:    tuple2(sauCvtRsp(s).r, False);
      default: tuple2(zeroExtend(sauVflRsp(s).prod), False);
    endcase;
  function Tuple2#(Bit#(128), Bool) wantOf(Bit#(4) i) =
    case (i)
      0: tuple2(128'h7577, False);
      1: tuple2(128'h79228162514264337593543950335, False);
      2: tuple2(128'hFFFFFFFFFFFE000000000001, False);
      3: tuple2(128'h0, True);
      4: tuple2(128'h4EE2D6D415B85ACEF80FFFFFFFF, False);
      5: tuple2(128'h0, False);
      default: tuple2(128'h1, False);
    endcase;
  function Bit#(16) clocksOf(Bit#(4) i) =
    case (i) 0: 8; 1: 6; default: 4; endcase;

  // Issue in the clock the previous answer is taken, as mkEBox may.
  rule rl_first (!done && !issued);
    box.request(reqOf(idx));
    issued <= True;
    t0 <= clk;
  endrule

  rule rl_collect (!done && issued && box.responseReady());
    match {.gr, .gc} = viewOf(idx, box.response());
    match {.wr, .wc} = wantOf(idx);
    Bit#(16) took = clk - t0;
    if (gr != wr || gc != wc) begin
      $display("FAIL sau mix[%0d]: r=%h carry=%0d, want r=%h carry=%0d", idx, gr, gc, wr, wc);
      fails <= fails + 1;
    end else if (took != clocksOf(idx)) begin
      $display("FAIL sau mix[%0d] clocks = %0d, want %0d", idx, took, clocksOf(idx));
      fails <= fails + 1;
    end else
      $display("PASS sau mix[%0d] r=%h carry=%0d in %0d clocks", idx, gr, gc, took);
    if (idx == fromInteger(valueOf(NMixVec) - 1)) begin
      done <= True;
      issued <= False;
    end else begin
      box.request(reqOf(idx + 1));
      t0 <= clk;
      idx <= idx + 1;
    end
  endrule

  rule rl_finish (done);
    if (fails == 0) $display("ALL TESTS PASSED");
    else $display("%0d TEST(S) FAILED", fails);
    $finish(0);
  endrule
endmodule

// ---------------------------------------------------------------------
// mkSauStepTb (half (b), 2026-11-25): THE STEPPED ADD.  Each vector is a
// request with its passes (SauAddSteps), a LITERAL answer and a LITERAL
// clock count worked by hand from Table 3's terms at 2 clocks a pass
// (the switches' note above sauStepZ): 2 x (passes + z + recomplement),
// the recomplement os/r + x/y + z + 1 (+), or 1 (+MG).  ownClocks() must
// be Valid and equal the clocks taken, except for the unstepped control.
//   0  binary (BU,8,8) 0x44 + 0x44: one pass, no carry out       2
//   1  binary 0xFF + 0x01, top 8: z = 1 (carry into bit 8)       4
//   2  binary 0xFFFFFF + 0x01, top 8: z = 3 (bits 8, 16, 24)     8
//   3  binary 0x100 - 0x01, top 8: a borrow into bit 8, z = 1,
//      absorbed at bit 16; end carry, no recomplement            4
//   4  binary (BU,16,8) 0x001 - 0x100, top 16: the borrow runs to
//      the left end, which is not stepped (z = 0: rl_add's note),
//      then the recomplement 0 + 2 + 0 + 1 = 3: 2 + 3 = 5 passes  10
//   5  decimal (DU,8,4) 95 + 05, top digit 2: z = 1              6
//   6  decimal 4444 + 44 at digit 2 (osb 2, top 4): z = 0        4
//   7  +MG binary (BU,8,8) 1 - 2: the borrow runs to the left end
//      (z = 0), cleared not recomplemented, so 1 more: 2 passes   4
//   8  signed binary, one data byte and the sign pass: 2 passes  4
//   9  the unstepped control (sauNoSteps), 1 + 1: half (a)'s 4
//      clocks (rl_add's note), ownClocks() Invalid               4
// STEP 2, THE M+ FAMILY (SauStMem, SauStOne; compacted decimal fields):
//  10  M+ (DU,8,4) 44 + 44, like signs: 2 passes, no z            4
//  11  M+ 01 - 44: AB > CD, recomplemented, 2 + (2 + 1) passes   10
//  12  M+ 44 - 01: CD > AB, no recomplement: 2 passes             4
//  13  M+1 (DU,16,4) 0999 + 1: c = 3 carries (digits 0-2), 3 + 1  8
//  14  M+1 0444 + 1: c = 0, one pass                              2
//  15  M+1 0005 - 1, unlike, true result: x/y = 4 passes          8
//  16  M+1 0000 - 1, unlike, complement result: 2 x 4 + 1        18
// STEP 3, THE K FAMILY (SauStCmp, SauStCmpF; the compare's subtraction):
//  17  K (DU,8,4) 44 : 44, nothing of the accumulator beyond: w = 0  4
//  18  K 4444 : 44, accumulator digits beyond the field: w = 1 pass  6
//  19  KF, the same operands: no w                                   4
//  20  K (D,16,4) 4444 : 444 decided at the signs: sign pass, one
//      data pass, w: 3 passes (not 4 + 1)                           6
//  21  K (DU,16,4) 4444 : 4444 decided at the signs, unsigned, no w:
//      one data pass                                                 2
// STEP 4, DECIMAL SRD'S ROUND (SauStRnd):
//  22  4447 + 5 at the digit below the field: the RSU and RND cycles,
//      2 passes (sauRndPasses)                                       4
// STEP 5, THE CONVERTERS (SauCvt requests with SauCvtSteps; r compared):
//  23  CV B-D of 1: s = 1 bit, u/8 = 1, + 1: 3 passes               6
//  24  CV B-D of 1000: s = 10, u/8 = 2 (4 digits), + 1: 13 passes  26
//  25  CV D-B of 1234: s/4 = 4 digits, + 1: 5 passes               10
//  26  DCV D-B of 1: s/4 = 1, + 2: 3 passes                         6
//  27  LCV B-D (BU,8,8) of FF: x + u/8 + 1 = 8 + 2 + 1, from the
//      field alone (no accumulator term): 11 passes                22
// INJECTIONS, OBSERVED 2026-11-25 (each in a scratch copy of this file):
//   * sauStepZ := False: vectors 1, 2, 3 and 5 FAIL on clocks (2, 2, 2, 4
//     against 4, 8, 4, 6) -- the carry and borrow vectors -- and the rest
//     pass.
//   * sauStepRecomp := False: vector 4 FAILS on clocks (4 against 10) and
//     vector 7 on ownClocks (the unit reports 2 while the datapath's
//     recomplement takes 4); the rest pass.
// STEP 2 (2026-11-26): sauStepMemRecomp := False fails 11 (4 against 10);
//   sauStepOneCarry := False fails 13 (2 against 8); sauStepOneComp :=
//   False fails 16 (8 against 18); the rest pass.
// STEP 3 (2026-11-26): sauStepCmpW := False fails 18 and 20 (4 against 6
//   each); sauStepCmpEarly := False fails 20 (10 against 6) and 21 (8
//   against 2); sauStepCmpWLiteral := True fails 18 (8 against 6); the
//   rest pass.
// STEP 4 (2026-11-26): sauRndPasses := 1 fails 22 (2 against 4); the rest
//   pass.
// THE TERMINATION (fidelity_plan.md A5 part 2, 2026-11-27): after the step
// vectors, a clock-by-clock script, tc = 0..23, drives terminate(n) and
// holdTerm() and checks terminated() in EVERY clock against a literal
// table (termWant), worked from the interface note: terminate(n) in clock
// c is unseen in c (a read precedes the write), owes n clocks, and
// terminated() is first True in c + n + 1; a held clock does not count;
// a second terminate() REPLACES what is owed (the countdown register's
// write did the same); a request runs beside it, its answer on time.
//   tc 0  terminate(3)              True at 0, False 1-3, True at 4
//   tc 5  terminate(0)              True at 5 and 6: nothing owed
//   tc 7  terminate(2), hold at 8   False 8-10, True at 11 (10 unheld)
//   tc 12 hold while idle           True
//   tc 13 terminate(5), at 15 terminate(1): False 14-16, True at 17
//   tc 18 terminate(4) and a request (vector 0's add, 2 clocks):
//         responseReady False at 19, True at 20; False 19-22, True at 23
// INJECTIONS, OBSERVED 2026-11-27 (in mkSAU, each reverted by the exact
// inverse edit, `git diff` unchanged after; the step vectors 0-27 pass
// under every one of them, so only this script guards the termination):
//   * terminate stores n, not n + 1: term 3, 10, 16, 22 FAIL (True a clock
//     early, after each terminate with n > 0); 4 failures.
//   * rl_term ignores the hold (`!pw_termHold` dropped): term 10 FAILS
//     (the held clock counted); 1 failure.
//   * terminate adds to what is owed (`rg_term[1] + n + 1`): term 17, 18
//     and 23 FAIL (still owing); 3 failures.
//   * responseReady() also waits on the termination (`&& rg_term[1] == 0`):
//     term 20 FAILS (the request beside it late); 1 failure.
// ---------------------------------------------------------------------
typedef 28 NStepVec;

(* synthesize *)
module mkSauStepTb(Empty);
  SAU            box    <- mkSAU;
  Reg#(Bit#(5))  idx    <- mkReg(0);
  Reg#(Bit#(8))  fails  <- mkReg(0);
  Reg#(Bool)     issued <- mkReg(False);
  Reg#(Bool)     done   <- mkReg(False);
  Reg#(Bit#(16)) clk    <- mkReg(0);
  Reg#(Bit#(16)) t0     <- mkReg(0);

  rule rl_clk; clk <= clk + 1; endrule

  function SauAddSteps st(Bit#(8) p, Bit#(8) top, Bit#(8) osb, Bit#(8) b0, Bool mg) =
    SauAddSteps { passes: p, top: top, osb: osb, b0: b0, mg: mg, cls: SauStAdd, early: False };
  // Step 2 on: a compacted decimal field of `p` passes, x/y = `b0` digits.
  function SauAddSteps fs(Bit#(8) p, Bit#(8) b0, SauStepCls c, Bool e) =
    SauAddSteps { passes: p, top: b0, osb: 0, b0: b0, mg: False, cls: c, early: e };
  function DecReq reqOf(Bit#(5) i) =
    case (i)
      0: DecReq { a: 128'h44, b: 128'h44, sub: False, binary: True, steps: st(1, 8, 0, 1, False) };
      1: DecReq { a: 128'hFF, b: 128'h01, sub: False, binary: True, steps: st(1, 8, 0, 1, False) };
      2: DecReq { a: 128'hFFFFFF, b: 128'h01, sub: False, binary: True, steps: st(1, 8, 0, 1, False) };
      3: DecReq { a: 128'h100, b: 128'h01, sub: True, binary: True, steps: st(1, 8, 0, 1, False) };
      4: DecReq { a: 128'h001, b: 128'h100, sub: True, binary: True, steps: st(2, 16, 0, 2, False) };
      5: DecReq { a: 128'h95, b: 128'h05, sub: False, binary: False, steps: st(2, 2, 0, 2, False) };
      6: DecReq { a: 128'h4444, b: 128'h4400, sub: False, binary: False, steps: st(2, 4, 2, 2, False) };
      7: DecReq { a: 128'h1, b: 128'h2, sub: True, binary: True, steps: st(1, 8, 0, 1, True) };
      8: DecReq { a: 128'h10, b: 128'h20, sub: False, binary: True, steps: st(2, 8, 0, 1, False) };
      10: DecReq { a: 128'h44, b: 128'h44, sub: False, binary: False, steps: fs(2, 2, SauStMem, False) };
      11: DecReq { a: 128'h01, b: 128'h44, sub: True, binary: False, steps: fs(2, 2, SauStMem, False) };
      12: DecReq { a: 128'h44, b: 128'h01, sub: True, binary: False, steps: fs(2, 2, SauStMem, False) };
      13: DecReq { a: 128'h0999, b: 128'h1, sub: False, binary: False, steps: fs(4, 4, SauStOne, False) };
      14: DecReq { a: 128'h0444, b: 128'h1, sub: False, binary: False, steps: fs(4, 4, SauStOne, False) };
      15: DecReq { a: 128'h0005, b: 128'h1, sub: True, binary: False, steps: fs(4, 4, SauStOne, False) };
      16: DecReq { a: 128'h0000, b: 128'h1, sub: True, binary: False, steps: fs(4, 4, SauStOne, False) };
      17: DecReq { a: 128'h44, b: 128'h44, sub: True, binary: False, steps: fs(2, 2, SauStCmp, False) };
      18: DecReq { a: 128'h4444, b: 128'h44, sub: True, binary: False, steps: fs(2, 2, SauStCmp, False) };
      19: DecReq { a: 128'h4444, b: 128'h44, sub: True, binary: False, steps: fs(2, 2, SauStCmpF, False) };
      20: DecReq { a: 128'h4444, b: 128'h444, sub: True, binary: False, steps: fs(4, 3, SauStCmp, True) };
      21: DecReq { a: 128'h4444, b: 128'h4444, sub: True, binary: False, steps: fs(4, 4, SauStCmp, True) };
      22: DecReq { a: 128'h4447, b: 128'h5, sub: False, binary: False,
                   steps: SauAddSteps { passes: fromInteger(sauRndPasses), top: 0, osb: 0, b0: 0,
                                        mg: False, cls: SauStRnd, early: False } };
      default: DecReq { a: 128'h1, b: 128'h1, sub: False, binary: True, steps: sauNoSteps };
    endcase;
  // Step 5: vectors 23-27 are CONVERSIONS (SauCvt), compared on r alone.
  function CvtReq cvtOf(Bit#(5) i) =
    case (i)
      23: CvtReq { toDec: True,  v: 128'h1,    steps: SauCvtSteps { fixed: 1, accS: True } };
      24: CvtReq { toDec: True,  v: 128'h3E8,  steps: SauCvtSteps { fixed: 1, accS: True } };
      25: CvtReq { toDec: False, v: 128'h1234, steps: SauCvtSteps { fixed: 1, accS: True } };
      26: CvtReq { toDec: False, v: 128'h1,    steps: SauCvtSteps { fixed: 2, accS: True } };
      default: CvtReq { toDec: True, v: 128'hFF, steps: SauCvtSteps { fixed: 11, accS: False } };
    endcase;
  function Bool isCvt(Bit#(5) i) = (i >= 23);
  function DecRsp wantOf(Bit#(5) i) =
    case (i)
      0: DecRsp { r: 128'h88,      carry: False };
      1: DecRsp { r: 128'h100,     carry: False };
      2: DecRsp { r: 128'h1000000, carry: False };
      3: DecRsp { r: 128'hFF,      carry: True };
      4: DecRsp { r: 128'hFF,      carry: False };
      5: DecRsp { r: 128'h100,     carry: False };
      6: DecRsp { r: 128'h8844,    carry: False };
      7: DecRsp { r: 128'h1,       carry: False };
      8: DecRsp { r: 128'h30,      carry: False };
      10: DecRsp { r: 128'h88,     carry: False };
      11: DecRsp { r: 128'h43,     carry: False };
      12: DecRsp { r: 128'h43,     carry: True };
      13: DecRsp { r: 128'h1000,   carry: False };
      14: DecRsp { r: 128'h445,    carry: False };
      15: DecRsp { r: 128'h4,      carry: True };
      16: DecRsp { r: 128'h1,      carry: False };
      17: DecRsp { r: 128'h0,      carry: True };
      18: DecRsp { r: 128'h4400,   carry: True };
      19: DecRsp { r: 128'h4400,   carry: True };
      20: DecRsp { r: 128'h4000,   carry: True };
      21: DecRsp { r: 128'h0,      carry: True };
      22: DecRsp { r: 128'h4452,   carry: False };
      23: DecRsp { r: 128'h1,      carry: False };
      24: DecRsp { r: 128'h1000,   carry: False };
      25: DecRsp { r: 128'h4D2,    carry: False };
      26: DecRsp { r: 128'h1,      carry: False };
      27: DecRsp { r: 128'h255,    carry: False };
      default: DecRsp { r: 128'h2, carry: False };
    endcase;
  function Bit#(16) clocksOf(Bit#(5) i) =
    case (i) 0: 2; 1: 4; 2: 8; 3: 4; 4: 10; 5: 6; 6: 4; 7: 4; 8: 4;
             10: 4; 11: 10; 12: 4; 13: 8; 14: 2; 15: 8; 16: 18;
             17: 4; 18: 6; 19: 4; 20: 6; 21: 2; 22: 4;
             23: 6; 24: 26; 25: 10; 26: 6; 27: 22; default: 4; endcase;

  rule rl_issue (!done && !issued);
    if (isCvt(idx)) box.request(tagged SauCvt cvtOf(idx));
    else box.request(tagged SauAdd reqOf(idx));
    issued <= True;
    t0 <= clk;
  endrule

  rule rl_collect (!done && issued && box.responseReady());
    let got  = sauDecRsp(box.response());
    let want = wantOf(idx);
    Bit#(16) took = clk - t0;
    Maybe#(Bit#(16)) own = box.ownClocks();
    Maybe#(Bit#(16)) wantOwn = (idx == 9) ? tagged Invalid : tagged Valid took;
    Bool wrong = isCvt(idx) ? (got.r != want.r) : (got != want);
    if (wrong) begin
      $display("FAIL sau step[%0d]: r=%h carry=%0d, want r=%h carry=%0d",
               idx, got.r, got.carry, want.r, want.carry);
      fails <= fails + 1;
    end else if (took != clocksOf(idx)) begin
      $display("FAIL sau step[%0d] clocks = %0d, want %0d", idx, took, clocksOf(idx));
      fails <= fails + 1;
    end else if (own != wantOwn) begin
      $display("FAIL sau step[%0d] ownClocks wrong (took %0d)", idx, took);
      fails <= fails + 1;
    end else
      $display("PASS sau step[%0d] r=%h carry=%0d in %0d clocks", idx, got.r, got.carry, took);
    issued <= False;
    if (idx == fromInteger(valueOf(NStepVec) - 1)) done <= True;
    else idx <= idx + 1;
  endrule

  // THE TERMINATION SCRIPT (header).  rl_thold is its own rule: holdTerm()
  // must come before mkSAU's rl_term and terminate() after it.
  Reg#(Bit#(5))  tc     <- mkReg(0);
  Reg#(Bool)     tdone  <- mkReg(False);
  function Bool termWant(Bit#(5) t) =
    case (t) 1, 2, 3, 8, 9, 10, 14, 15, 16, 19, 20, 21, 22: False; default: True; endcase;
  rule rl_thold (done && !tdone && (tc == 8 || tc == 12));
    box.holdTerm();
  endrule
  rule rl_tphase (done && !tdone);
    Bool t = box.terminated();
    Bit#(8) nf = 0;
    if (t != termWant(tc)) begin
      $display("FAIL sau term[%0d]: terminated() = %0d, want %0d", tc, t, termWant(tc));
      nf = nf + 1;
    end
    if (tc == 19 && box.responseReady()) begin
      $display("FAIL sau term[19]: the request beside the termination is ready early");
      nf = nf + 1;
    end
    if (tc == 20 && (!box.responseReady() || sauDecRsp(box.response()) != wantOf(0))) begin
      $display("FAIL sau term[20]: the request beside the termination is late or wrong");
      nf = nf + 1;
    end
    fails <= fails + nf;
    case (tc)
      0: box.terminate(3);
      5: box.terminate(0);
      7: box.terminate(2);
      13: box.terminate(5);
      15: box.terminate(1);
      18: begin box.terminate(4); box.request(tagged SauAdd reqOf(0)); end
    endcase
    if (tc == 23) begin
      tdone <= True;
      $display("PASS sau term: 24 clocks scripted");
    end
    tc <= tc + 1;
  endrule

  rule rl_finish (done && tdone);
    if (fails == 0) $display("ALL TESTS PASSED");
    else $display("%0d TEST(S) FAILED", fails);
    $finish(0);
  endrule
endmodule

endpackage
