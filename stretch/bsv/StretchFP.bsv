// StretchFP.bsv -- IBM 7030 floating-point arithmetic, single precision
// (docs/microarchitecture_plan.md stage 4c). Pure functions over the
// Reference Manual's formats, called by StretchExecute's Fp arm.
//
// SOURCES (Reference Manual, printed pages; PDF page = printed + 3):
//   p.78-79 Data format: bits 0-11 exponent (EF flag, EM 10-bit
//     magnitude, ES sign; value = ±F × 2^±E), bits 12-59 fraction
//     magnitude with the binary point left of bit 12, bit 60 fraction
//     sign, bits 61-63 data flags T U V. Ranges: N (EF=0, |E| <= 1023),
//     XFP (EF=1, ES=0, "infinity"-like), XFN (EF=1, ES=1, zero-like).
//   p.79-80 Accumulator format: exponent in accumulator bits 0-11,
//     fraction 12-59, bits 60-63 unused; the fraction sign in bit 4 of
//     the sign byte register (address 10), the data flags in bits 5-7.
//   p.81 Normalization: normalized when instruction bit 18 is 0; a
//     normalized fraction has 1 > F >= 1/2 or is zero; left shift
//     subtracts from the exponent, a right shift for a fraction overflow
//     adds one; zero fractions are not normalized.
//   p.81-82 Sign control: bit 19 "absolute sign" makes the storage
//     operand's sign positive before bit 20 "negative sign" inverts the
//     operand not changed by the operation (the storage operand for
//     accumulator-changing ops, the accumulator for stores).
//   p.82-83 Zero definition: order-of-magnitude zero keeps the exponent
//     of the operand with the larger exponent; a forced zero from ADD TO
//     MAGNITUDE sets RZ but not LS.
//   p.83 Fig.23 result exponent ranges for flagged operands; propagated
//     vs generated exponent flags; normalization suppressed when the
//     result has a propagated EF.
//   p.84 Fig.24 comparison results; noisy mode (indicator NM: ones
//     shifted in during normalization) -- modeled.
//   p.85-86 Indicators: LC, PF, ZD, TF/UF/VF, MOP, RLZ/RZ/RGZ/RN,
//     AL/AE/AH, LS, PSH, XPFP, XPO, XPH (1024 > E >= 512), XPL (512 >
//     E >= 64), XPU, ZM.
//   p.86-94 Operations: +, +MG, L, LWF, M+, M+MG, ST, K, KMG, KR, KMGR,
//     *, /, R/. Add: exponents compared, the fraction with the smler
//     exponent shifted right by the difference into a 96-bit
//     intermediate sum with an overflow bit; difference > 48 sets PSH;
//     difference > 95 gives the operand with the higher exponent.
//     Multiply: exponents added, 96-bit product, post-normalization up
//     to 96 places, ZM. Divide: divisor and dividend pre-normalized,
//     48-bit quotient, exponent difference (+1 on quotient overflow),
//     ZD suppresses the division.
//
// NOT MODELED HERE (yet): double precision (D+, DL, D*, D/, SRD, SLO,
// LFT, *+), store root, shift fraction, add to exponent, the unnormalized
// divide's PF/LZC details (an unnormalized divide behaves as normalized
// with PF left off).

package StretchFP;

import StretchTypes::*;

typedef struct {
  Bit#(1)  ef;      // exponent flag
  Bit#(10) em;      // exponent magnitude
  Bit#(1)  es;      // exponent sign (1 = negative)
  Bit#(48) frac;    // fraction magnitude, binary point to the left
  Bit#(1)  sign;    // fraction sign (1 = negative)
  Bit#(3)  flags;   // T U V
} FpNum deriving (Bits, Eq, FShow);

// ---- format conversions ----
function FpNum fpFromWord(Word64 w) =
  FpNum { ef: w[63], em: w[62:53], es: w[52], frac: w[51:4], sign: w[3], flags: w[2:0] };

function Word64 fpToWord(FpNum x) = { x.ef, x.em, x.es, x.frac, x.sign, x.flags };

// Accumulator: left half bits 0-59 = exponent + fraction; sign byte
// (address 10, its bits 0-7 in the word's low byte) bit 4 = sign,
// bits 5-7 = flags.
// The accumulator sign byte register (word 10) is IBM bits 0-7 of that
// word: the sign in bit 4 ("fifth bit position from the left") and the
// data flags T/U/V in bits 5-7 (p.82: "sign byte register bit positions
// 5-7"). Both the floating-point arms (here) and the VFL accumulator
// helpers (StretchALU accToSM/packAcc) use this one layout. Before
// jb_af1c F204C the model kept the byte at IBM bits 56-63 and the VFL
// sign in bit 0 of word 8; F204C's CM1111(BU,8),10.0 / CT1100(BU,8),10.0
// and its 64-bit checks of word 8 need the real layout.
function Bit#(1) sbSign(Word64 sb)  = sb[59];
function Bit#(3) sbFlags(Word64 sb) = sb[58:56];
function Word64 sbWith(Word64 oldByte, Bit#(1) sign, Bit#(3) flags) =
  { oldByte[63:60], sign, flags, oldByte[55:0] };

function FpNum fpFromAcc(Word64 accLeft, Word64 signByte) =
  FpNum { ef: accLeft[63], em: accLeft[62:53], es: accLeft[52], frac: accLeft[51:4],
          sign: sbSign(signByte), flags: sbFlags(signByte) };

function Word64 fpAccLeft(FpNum x, Word64 oldLeft) = { x.ef, x.em, x.es, x.frac, oldLeft[3:0] };

function Word64 fpSignByte(FpNum x, Word64 oldByte) = sbWith(oldByte, x.sign, x.flags);

// Signed exponent as an integer (ignoring the flag).
function Int#(13) fpExp(FpNum x);
  Int#(13) m = unpack(zeroExtend(x.em));
  return (x.es == 1) ? -m : m;
endfunction

// The full signed exponent VALUE, EF's 1024 included.  fpExp above
// returns only the ten-bit magnitude field, which is all that a
// comparison between two operands of the SAME range needs and is what
// every existing caller wants.  But an exponent that has to be
// ARITHMETIC across the flagged boundary -- adjusted by a
// normalization shift and re-encoded -- needs the 1024 that EF stands
// for, because fpMakeExp stores an out-of-range exponent as "the LOW
// TEN BITS of its magnitude; EF only marks that it overflowed".
// jb_af1c F213A12 is where that matters: a generated XFP exponent of
// +1073 is held as EF 1 / EM 49, and normalizing shifts it by 12.
// Through fpExp that reads as 49 - 12 = 37, an N-range exponent;
// through this it reads as 1073 - 12 = 1061, which is FK57's.
//
// THE TWO COINCIDE EXACTLY WHEN ef == 0, which is why every other
// normalizing arm (L, LWF, E+I, ...) is correct with the plain fpExp:
// each guards its normalization with `v.ef == 0`, so it never
// normalizes a flagged value. The rule for anyone touching them: an
// arm that can normalize a POSSIBLY-FLAGGED value must use fpExpFull.
// Loosening such a guard without also switching the function
// reintroduces the F213A12 bug -- do not "clean up" the inconsistency
// by deleting this function.
function Int#(14) fpExpFull(FpNum x);
  Int#(14) m = unpack(zeroExtend({x.ef, x.em}));
  return (x.es == 1) ? -m : m;
endfunction

function Bool isXFP(FpNum x) = (x.ef == 1 && x.es == 0);
function Bool isXFN(FpNum x) = (x.ef == 1 && x.es == 1);
function Bool isN(FpNum x)   = (x.ef == 0);

// Build a number from a signed exponent, flagging out-of-range results
// (a *generated* flag). Returns the number and whether a flag was
// generated.
function Tuple2#(FpNum, Bool) fpMakeExp(Int#(14) e, Bit#(48) frac, Bit#(1) sign, Bit#(3) flags);
  Bool neg = (e < 0);
  Int#(14) mag = neg ? -e : e;
  Bool gen = (mag > 1023);
  // An out-of-range exponent keeps the LOW TEN BITS of its magnitude;
  // EF only marks that it overflowed. This used to write zero on a
  // generated flag, which is wrong and which nothing caught until
  // jb_af1c F211A10: that sub-test drives SLO's exponent to -1073 and
  // expects FK112, whose exponent field is -49 -- and 1073 - 1024 = 49.
  // Zeroing it halted A10 on its CT0110 at 016243.00 while A7-A9,
  // including A9's in-range normalization, all passed.
  Bit#(10) em = truncate(pack(mag));
  return tuple2(FpNum { ef: gen ? 1 : 0, em: em, es: neg ? 1 : 0, frac: frac, sign: sign, flags: flags }, gen);
endfunction

// Result of an arithmetic operation, with everything the executor
// needs to set indicators.
typedef struct {
  FpNum   res;
  Bool    lc;        // lost carry (unnormalized overflow)
  Bool    ls;        // lost significance
  Bool    psh;       // preparatory shift > 48
  Bool    generated; // result EF generated by over/underflow
  Bool    propagated;// result EF propagated from an operand
  Bool    zm;        // zero multiply
  Bool    zd;        // zero divisor (operation suppressed)
} FpResult deriving (Bits, Eq, FShow);

function FpResult fpNoResult(FpNum r) =
  FpResult { res: r, lc: False, ls: False, psh: False, generated: False,
             propagated: False, zm: False, zd: False };

// Apply the sign modifiers to a storage operand (p.81-82): absolute
// first, then negative.
function FpNum fpApplySignMods(FpNum x, Bit#(1) absSign, Bit#(1) negSign);
  Bit#(1) s = (absSign == 1) ? 0 : x.sign;
  if (negSign == 1) s = ~s;
  x.sign = s;
  return x;
endfunction

// Normalize a 96-bit fraction with overflow bit, keeping the WHOLE 96
// bits, plus an exponent adjustment; noisy mode shifts in ones. Zero
// fractions are left alone. Single-precision callers want only the
// high 48 (fpNormalize96 below); LOAD DOUBLE and the rest of the
// double-precision family need the low half too, since accumulator
// bits 60-107 are part of the fraction there (p.79-80, p.96) and
// noisy mode puts its one-bits exactly into them.
function Tuple3#(Bit#(96), Int#(14), Bool) fpNormalize96Wide(Bit#(1) ovf, Bit#(96) f96, Bool normalized, Bool noisy);
  Bit#(97) v = {ovf, f96};
  Bool lostCarry = False;
  if (v == 0) return tuple3(0, 0, False);
  else if (!normalized) begin
    // Unnormalized: the 96-bit sum stands; overflow bit lost.
    lostCarry = (ovf == 1);
    return tuple3(f96, 0, lostCarry);
  end else begin
    if (ovf == 1) begin
      // Right shift one to bring the overflow bit in (p.81).
      Bit#(96) sh = v[96:1];
      return tuple3(sh, 1, False);
    end else begin
      // Left shift until the high-order bit is one (up to 95 places):
      // a leading-zero count and one shift, with noisy mode filling the
      // vacated low-order bits with ones.
      UInt#(7) nz = countZerosMSB(f96);
      Int#(14) n = unpack(zeroExtend(pack(nz)));
      Bit#(96) w = f96 << nz;
      if (noisy) w = w | ((96'b1 << nz) - 1);
      return tuple3(w, -n, False);
    end
  end
endfunction

// SLO's normalization (p.97). Its fraction is the accumulator's LOW
// 48 bits, shifted left "until a high-order one bit is leftmost", and
// "if noisy mode is also specified, ones are entered from the right
// during the normalization shifting; otherwise zeros". That is the
// opposite of SRD, where "noisy mode does not affect this operation" --
// so this cannot go through fpNormalize96Wide, whose noisy fill lands
// in the low 48 bits that SLO does not have.
function Tuple2#(Bit#(48), Int#(14)) fpNormalize48(Bit#(48) f, Bool normalized, Bool noisy);
  if (!normalized || f == 0) return tuple2(f, 0);
  else begin
    let nz = countZerosMSB(f);
    Bit#(48) w = f << nz;
    if (noisy) w = w | ((48'b1 << nz) - 1);
    Int#(14) n = unpack(zeroExtend(pack(nz)));
    return tuple2(w, -n);
  end
endfunction

// Single-precision view of the same normalization: the high 48 bits.
function Tuple3#(Bit#(48), Int#(14), Bool) fpNormalize96(Bit#(1) ovf, Bit#(96) f96, Bool normalized, Bool noisy);
  let {w, adj, lc} = fpNormalize96Wide(ovf, f96, normalized, noisy);
  return tuple3(w[95:48], adj, lc);
endfunction

// ---- ADD (p.86-87) and its variants. a = accumulator operand, b =
// storage operand already sign-modified. addMag: ADD TO MAGNITUDE's
// forced-zero rule (accumulator sign taken positive; negative sum ->
// forced zero with the accumulator's sign and exponent).
// `a` is the operand being replaced (the accumulator for +/+MG, the
// storage word for M+/M+MG): its flags carry to the result and ADD TO
// MAGNITUDE takes its magnitude. `accIsB` says the ACCUMULATOR operand
// is `b` (the M+ family), which matters for one rule only: p.82 "Zero
// Definition" -- an order-of-magnitude zero from addition takes the
// (modified) sign of the operand with the algebraically larger
// exponent, and when the exponents are EQUAL, "the modified fraction
// sign of the operand in the accumulator". Found by jb_af1c F204B4
// (M-A of +1/3 with +1/3: the accumulator, negated by N, gives -0; with
// the storage operand's sign the model stored +0 and the sign check
// branched to SERS).
function FpResult fpAdd(FpNum a, FpNum b, Bool normalized, Bool noisy, Bool addMag, Bool accIsB);
  FpResult r = fpNoResult(a);
  // ADD TO MAGNITUDE (p.88) assumes the fraction sign of the operand IN
  // THE ACCUMULATOR positive -- that is `a` for +MG. ADD MAGNITUDE TO
  // MEMORY (p.89) does the same to its accumulator operand, `b`, but
  // does it "before the negative sign modification occurs": the M+ arm
  // of execute() therefore zeroes b.sign itself, ahead of the N
  // modifier, and this must not reach across and clear the ADDRESSED
  // operand's sign instead -- that sign is what the forced-zero rule
  // below is compared against.
  if (addMag && !accIsB) a.sign = 0;
  // Flagged operands (Fig.23 / p.87): the result is one operand or the
  // other, normalization suppressed, EF propagated.
  if (a.ef == 1 || b.ef == 1) begin
    FpNum res = a;
    if (isXFP(a) && isXFP(b)) res = a;               // both XFP: accumulator (equal ranges)
    else if (isXFN(a) && isXFN(b)) res = a;
    else if (isXFP(a) || isXFP(b)) res = isXFP(a) ? a : b;   // XFP dominates N and XFN
    else res = isN(a) ? a : b;                        // N dominates XFN
    // "the result is the operand in the same range having the
    // algebraically larger exponent" for equal ranges:
    if ((isXFP(a) && isXFP(b)) || (isXFN(a) && isXFN(b)))
      res = (fpExp(b) > fpExp(a)) ? b : a;
    Bool gen = False;
    if (addMag && (accIsB ? (res.sign != a.sign) : (res.sign == 1))) begin
      // ADD TO MAGNITUDE's forced zero (p.83) reached with a flagged
      // survivor. The two directions differ in what the forced zero
      // keeps, and each has its own check in the diagnostic:
      //
      // +MG: the accumulator's sign was made positive above, so a
      //   NEGATIVE survivor is the storage operand dominating and the
      //   sum would be negative -- a forced zero with the survivor's
      //   exponent and a zero fraction. jb_af1c F205A7 (XFN in the
      //   accumulator, negative XFP in storage) checks exactly that:
      //   exponent field = the XFP operand's, fraction forced zero.
      //   (p.88 words this as "the sign and exponent of the accumulator
      //   operand", which fits only if one reads the surviving operand
      //   as already gated into the accumulator; A7 is unambiguous.)
      //
      // M+MG: p.89 is explicit -- "the sum sign is compared with the
      //   addressed operand's effective sign... with opposite signs the
      //   result fraction is a forced zero in storage. The forced zero
      //   sign is the same as the addressed operand's original sign.
      //   The sign and exponent of the STORAGE operand become the sign
      //   and exponent of the forced order-of-magnitude zero result."
      //   Here that storage operand is `a`. jb_af1c F206A9 (XFN -2047
      //   negative in storage, XFN -1791 positive in the accumulator)
      //   needs it: the survivor is the accumulator's -1791, but the
      //   check is against FK19 -- exponent -2047, zero fraction -- and
      //   the following BB requires sign bit 1, the addressed
      //   operand's. Keeping the survivor's exponent halted there.
      //
      // Only the EXPONENT matters here for the to-memory direction: the
      // M+ arm overwrites the result sign with the addressed operand's
      // unmodified original one (p.83), which is what a forced zero
      // wants and what `a.sign` -- the sign after the absolute modifier
      // -- would get wrong under M-MGA. `a.sign` still decides WHETHER
      // the zero is forced, and there it is the A-modified sign that is
      // correct (p.89, and jb_af1c F206B23 against B24).
      res.frac = 0;
      if (accIsB) begin
        res.sign = a.sign; res.ef = a.ef; res.em = a.em; res.es = a.es;
      end else
        res.sign = 0;
    end
    if (res.ef == 0 && normalized) begin
      // The surviving operand is the UNFLAGGED one (XFN + N: N
      // dominates): it is a normal number, and a normalized operation
      // post-normalizes it like any other result. Only a flagged
      // result has normalization suppressed. jb_af1c F204E4 (XFN in
      // memory, N in the accumulator, M+(N)) expects the accumulator
      // operand normalized (FPK7 -> FPK6); E1-E3/E6, whose results
      // are flagged, expect them untouched.
      let {frac48, adj, lc} = fpNormalize96(0, {res.frac, 48'b0}, True, noisy);
      Int#(14) e = signExtend(fpExp(res)) + adj;
      let {nres, g} = fpMakeExp(e, frac48, res.sign, res.flags);
      res = nres; gen = g;
    end
    r.res = res; r.propagated = (res.ef == 1); r.generated = gen;
    r.ls = False;
    return r;
  end else begin
    Int#(13) ea = fpExp(a), eb = fpExp(b);
    Int#(14) diff = signExtend(ea) - signExtend(eb);   // positive: a has the larger exponent
    Int#(14) adiff = (diff < 0) ? -diff : diff;
    Bool aBig = (diff >= 0);
    FpNum big = aBig ? a : b;
    FpNum sml = aBig ? b : a;
    r.psh = (adiff > 48);
    if (adiff > 95) begin
      // No addition: the result is the number with the higher exponent.
      r.res = big;
      Bool bothZero = (a.frac == 0 && b.frac == 0);
      r.ls = False;
      if (big.frac == 0 && !bothZero) r.ls = True;
      return r;
    end else begin
      Bit#(96) fb = {big.frac, 48'b0};
      Bit#(96) fs = {sml.frac, 48'b0} >> adiff;
      Bit#(97) sum;
      Bit#(1) sign;
      Bool forcedZero = False;
      if (big.sign == sml.sign) begin
        sum = zeroExtend(fb) + zeroExtend(fs);
        sign = big.sign;
      end else begin
        // Subtract the smler magnitude; sign of the larger magnitude.
        if (fb >= fs) begin sum = zeroExtend(fb - fs); sign = big.sign; end
        else begin sum = zeroExtend(fs - fb); sign = sml.sign; end
        // Order-of-magnitude zero: the larger-exponent operand's sign;
        // on an exponent tie, the accumulator's (p.82, see the header).
        if (fb == fs) sign = (diff == 0 && accIsB) ? b.sign : big.sign;
      end
      if (addMag && sum != 0 && (accIsB ? (sign != a.sign) : (sign == 1))) begin
        // ADD TO MAGNITUDE: a sum whose fraction sign is reversed
        // relative to the operand being replaced becomes a forced zero
        // -- for +MG a negative sum, with the accumulator's sign and
        // exponent (p.88); for M+MG a sum whose sign differs from the
        // addressed operand's, with THAT operand's sign and exponent
        // (p.89, and see the flagged path above).
        //
        // `sum != 0`: an exact cancellation is not "a fraction sign
        // reversal obtained during the addition" (p.83) but an ordinary
        // order-of-magnitude zero, which sets LS -- p.89 says a forced
        // zero leaves LS off and that "this action distinguishes it
        // from a zero sum". Without the guard M+MG of x and -x would be
        // read as a forced zero, since the tie rule gives the zero the
        // accumulator's (positive) sign against a negative addressed
        // operand.
        forcedZero = True;
        sum = 0;
        sign = accIsB ? a.sign : 0;   // overwritten by the M+ arm with
                                      // the unmodified original sign;
                                      // see the flagged path's note
      end
      let {frac48, adj, lostCarry} = fpNormalize96(sum[96], sum[95:0], normalized, noisy);
      Bool zeroResult = (sum == 0);
      Int#(14) e = signExtend(fpExp(big)) + (zeroResult ? 0 : adj);
      let {res, gen} = fpMakeExp(e, frac48, sign, a.flags);
      if (zeroResult) begin
        // Order-of-magnitude zero: exponent of the larger-exponent
        // operand, no normalization, no exponent change -- except a
        // forced zero from M+MG, which takes the addressed operand's
        // exponent whether or not that operand had the larger one
        // (p.89).
        FpNum ez = (forcedZero && accIsB) ? a : big;
        res.ef = ez.ef; res.em = ez.em; res.es = ez.es;
        gen = False;
      end
      r.res = res;
      r.lc = lostCarry;
      r.generated = gen;
      // Same rule as ADD DOUBLE's below, and for the same reason: LS
      // asks whether the RESULT fraction is zero, and an unnormalized
      // add can carry out of the top leaving 48 zeros behind. Proven
      // for D+ by jb_af1c F208D5; NOT proven here -- no single-
      // precision sub-test in the suite distinguishes the two forms,
      // and the F204D/F206D indicator blocks reach LS only through
      // exact cancellations, where sum and result fraction are both
      // zero anyway.
      r.ls = (res.frac == 0) && !(a.frac == 0 && b.frac == 0) && !forcedZero;
      return r;
    end
  end
endfunction

// ---- DOUBLE PRECISION (p.79-80, p.95-96) ----------------------------
// The accumulator's fraction is 96 bits, IBM 12-107; a storage operand
// carries 48 and is "extended with 48 zeros during the operation".
// Everything about the exponent, the ranges and the sign is the
// single-precision rule, so this type repeats those fields with a
// wider fraction and `fpdHead` hands the narrow helpers (fpExp, isXFP,
// fpMakeExp, fpRangeBits) an FpNum to work on.
typedef struct {
  Bit#(1)  ef;
  Bit#(10) em;
  Bit#(1)  es;
  Bit#(96) frac;
  Bit#(1)  sign;
  Bit#(3)  flags;
} FpDouble deriving (Bits, Eq, FShow);

function FpNum fpdHead(FpDouble x) =
  FpNum { ef: x.ef, em: x.em, es: x.es, frac: 0, sign: x.sign, flags: x.flags };

// IBM bit n is bit 127-n of the accumulator's 128 magnitude bits, so
// the exponent and the fraction's high 48 are the left half's 63-4,
// the fraction's low 48 are the left half's 3-0 followed by the right
// half's 63-20, and IBM 108-127 -- the right half's low twenty --
// are outside the fraction entirely.
function FpDouble fpdFromAcc(Word64 accLeft, Word64 accRight, Word64 signByte) =
  FpDouble { ef: accLeft[63], em: accLeft[62:53], es: accLeft[52],
             frac: { accLeft[51:0], accRight[63:20] },
             sign: sbSign(signByte), flags: sbFlags(signByte) };

function FpDouble fpdFromWord(Word64 w) =
  FpDouble { ef: w[63], em: w[62:53], es: w[52], frac: { w[51:4], 48'b0 },
             sign: w[3], flags: w[2:0] };

function Word64 fpdAccLeft(FpDouble x) = { x.ef, x.em, x.es, x.frac[95:44] };
function Word64 fpdAccRight(FpDouble x, Word64 oldRight) = { x.frac[43:0], oldRight[19:0] };

typedef struct {
  FpDouble res;
  Bool lc;
  Bool ls;
  Bool psh;
  Bool generated;
  Bool propagated;
} FpdResult deriving (Bits, Eq, FShow);

// ADD DOUBLE (p.95). `a` is the accumulator operand, `b` the storage
// operand, already sign-modified and already extended with 48 zeros.
// The shape is ADD's, with three differences the manual is explicit
// about: the fractions are 96 bits rather than 48 extended to 96, so
// what a preparatory shift pushes past the right end is LOST (in ADD
// it is retained in the intermediate and participates); PSH is still
// "difference exceeds 48" even though the fraction is twice as long;
// and noisy mode does not add one-bits to the operands beforehand, it
// only fills the vacated positions during normalization.
// `addMag` selects ADD DOUBLE TO MAGNITUDE (D+MG, Ref. Manual p.95):
// "the same as ADD DOUBLE except that the sign of the accumulator
// operand is assumed positive and the result is made a forced zero
// when a negative sum is obtained... a zero fraction is placed into
// bits 12-107 of the accumulator and the sign and exponent of the
// accumulator operand remain equal to the original accumulator sign
// and exponent. Normalization, noisy mode, and values in the XFP or
// XFN range are handled as in ADD DOUBLE."
//
// There is no ADD DOUBLE MAGNITUDE TO MEMORY, so unlike fpAdd this
// takes no accIsB: the accumulator is always `a` and always the
// destination. The rules below mirror fpAdd's non-accIsB arm exactly,
// including the reading of "the accumulator operand" that jb_af1c
// F205A7 forced on the single-precision case -- see fpAdd's header.
function FpdResult fpAddDouble(FpDouble a, FpDouble b, Bool normalized, Bool noisy,
                               Bool addMag);
  FpdResult r = FpdResult { res: a, lc: False, ls: False, psh: False,
                            generated: False, propagated: False };
  // Only the accumulator's MAGNITUDE takes part; its sign is what the
  // forced-zero rule below is compared against, so force it first.
  if (addMag) a.sign = 0;
  if (a.ef == 1 || b.ef == 1) begin
    // Flagged operands: "the addition process follows the operation
    // outlined under ADD except that the accumulator fraction is 96
    // bits". Fig.23's table and the equal-range tie-break are the
    // single-precision ones.
    FpNum ha = fpdHead(a), hb = fpdHead(b);
    FpDouble res = a;
    if (isXFP(ha) && isXFP(hb)) res = a;
    else if (isXFN(ha) && isXFN(hb)) res = a;
    else if (isXFP(ha) || isXFP(hb)) res = isXFP(ha) ? a : b;
    else res = isN(ha) ? a : b;
    if ((isXFP(ha) && isXFP(hb)) || (isXFN(ha) && isXFN(hb)))
      res = (fpExp(hb) > fpExp(ha)) ? b : a;
    if (addMag && res.sign == 1) begin
      // The accumulator's sign was made positive above, so a NEGATIVE
      // survivor is the storage operand dominating and the sum would
      // be negative: a forced zero, keeping the survivor's exponent.
      // Same shape as fpAdd's +MG arm, which F205A7 pinned.
      res.frac = 0;
      res.sign = 0;
    end
    Bool gen = False;
    if (res.ef == 0 && normalized) begin
      // The survivor is the UNFLAGGED operand, so it normalizes like
      // any other result -- the single-precision rule F204E4 pinned.
      let {w96, adj, lc} = fpNormalize96Wide(0, res.frac, True, noisy);
      let {nres, g} = fpMakeExp(signExtend(fpExp(fpdHead(res))) + adj, 48'b0, res.sign, res.flags);
      res.ef = nres.ef; res.em = nres.em; res.es = nres.es; res.frac = w96;
      gen = g;
    end
    r.res = res; r.propagated = (res.ef == 1); r.generated = gen;
    return r;
  end else begin
    Int#(13) ea = fpExp(fpdHead(a)), eb = fpExp(fpdHead(b));
    Int#(14) diff = signExtend(ea) - signExtend(eb);
    Int#(14) adiff = (diff < 0) ? -diff : diff;
    Bool aBig = (diff >= 0);
    FpDouble big = aBig ? a : b;
    FpDouble sml = aBig ? b : a;
    r.psh = (adiff > 48);
    if (adiff > 95) begin
      // "When the difference between the exponents exceeds 95 the
      // number with the lower exponent is not added."
      r.res = big;
      Bool bothZero = (a.frac == 0 && b.frac == 0);
      r.ls = (big.frac == 0 && !bothZero);
      return r;
    end else begin
      Bit#(96) fb = big.frac;
      Bit#(96) fs = sml.frac >> adiff;
      Bit#(97) sum;
      Bit#(1) sign;
      if (big.sign == sml.sign) begin
        sum = zeroExtend(fb) + zeroExtend(fs);
        sign = big.sign;
      end else begin
        if (fb >= fs) begin sum = zeroExtend(fb - fs); sign = big.sign; end
        else begin sum = zeroExtend(fs - fb); sign = sml.sign; end
        // Order-of-magnitude zero on an exact cancellation: the
        // larger-exponent operand's sign, and on a tie the
        // accumulator's (p.82) -- which for D+ is `a`, and `a` is
        // `big` whenever the exponents are equal.
        if (fb == fs) sign = big.sign;
      end
      Bool forcedZero = False;
      if (addMag && sum != 0 && sign == 1) begin
        // A sum whose fraction sign came out negative becomes a forced
        // zero. `sum != 0` because an exact cancellation is not "a
        // fraction sign reversal obtained during the addition" but an
        // ordinary order-of-magnitude zero, which DOES set LS -- the
        // same guard F206A forced on the single-precision path.
        forcedZero = True;
        sum = 0;
        sign = 0;
      end
      let {f96, adj, lostCarry} = fpNormalize96Wide(sum[96], sum[95:0], normalized, noisy);
      Bool zeroResult = (sum == 0);
      let {hd, gen} = fpMakeExp(signExtend(fpExp(fpdHead(big))) + (zeroResult ? 0 : adj),
                                48'b0, sign, a.flags);
      FpDouble res = FpDouble { ef: hd.ef, em: hd.em, es: hd.es, frac: f96,
                                sign: sign, flags: a.flags };
      Bool g = gen;
      if (zeroResult) begin
        // "If the 96-bit intermediate sum has a zero fraction,
        // normalization, if specified, will be suppressed. The
        // exponent replacing accumulator bits 0-11 will be the
        // exponent of the intermediate result."
        res.ef = big.ef; res.em = big.em; res.es = big.es;
        g = False;
      end
      r.res = res; r.lc = lostCarry; r.generated = g;
      // "LS is set to one when at least one operand is non-zero and
      // when the 96 bits of the result fraction are zero" (p.96).
      // LS asks about the RESULT fraction, not the intermediate sum:
      // "LS is set to one when at least one operand is non-zero and
      // when the 96 bits of the result fraction are zero" (p.96). An
      // unnormalized add can carry out of the top with all 96 low bits
      // zero -- the carry is lost, and what lands in the accumulator is
      // 96 zeros -- so `sum` is non-zero while the result fraction is
      // not. jb_af1c F208D5 is exactly that: 0xffffffffffff400000000000
      // plus 0x600000000000 shifted right 47 gives 1 followed by 96
      // zeros. Testing `sum` there leaves LS off and the listing
      // demands it on. (zeroResult, on the 97-bit sum, stays as it is
      // for the separate normalization-suppression rule.)
      // A forced zero leaves LS off: p.89 says that "distinguishes it
      // from a zero sum".
      r.ls = (res.frac == 0) && !(a.frac == 0 && b.frac == 0) && !forcedZero;
      return r;
    end
  end
endfunction

// ---- COMPARE (p.90-91): algebraic comparison a ? b. Returns -1/0/+1
// (accumulator low / equal / high).
function Int#(2) fpCompare(FpNum a, FpNum b, Bool magnitude);
  if (magnitude) a.sign = 0;
  // Zero fractions: "plus zero is equal to negative zero"; otherwise
  // sign, then exponent, then fraction (Fig.24), with flagged ranges
  // per p.91 (XFP > N > XFN for positive; reversed for negative).
  Bool aZero = (a.frac == 0), bZero = (b.frac == 0);
  if (a.sign != b.sign && !(aZero && bZero)) return (a.sign == 0) ? 1 : -1;
  else begin
    // Same sign (or both zero): compare magnitudes.
    Int#(2) mag = 0;
    Bit#(2) ra = isXFP(a) ? 2 : (isN(a) ? 1 : 0);
    Bit#(2) rb = isXFP(b) ? 2 : (isN(b) ? 1 : 0);
    if (a.ef == 1 || b.ef == 1) begin
      if (ra != rb) mag = (ra > rb) ? 1 : -1;
      else mag = 0;
    end else begin
      Int#(13) ea = fpExp(a), eb = fpExp(b);
      Int#(14) diff = signExtend(ea) - signExtend(eb);
      Int#(14) adiff = (diff < 0) ? -diff : diff;
      if (adiff > 48) mag = (diff > 0) ? 1 : -1;   // judged by exponent (p.90)
      else begin
        // Align and compare 96-bit magnitudes.
        Bit#(96) fa = {a.frac, 48'b0}, fb = {b.frac, 48'b0};
        if (diff > 0) fb = fb >> adiff; else fa = fa >> adiff;
        if (fa > fb) mag = 1; else if (fa < fb) mag = -1; else mag = 0;
      end
    end
    if (aZero && bZero) return 0;
    else return (a.sign == 0) ? mag : -mag;
  end
endfunction

// ---- Figure 32, the EXPONENT MULTIPLICATION TABLE (Ref. Manual
// p.102). XFP dominates every combination, XFN dominates N, and two
// operands of the same range tie to `a` -- which for every caller here
// is the accumulator. MULTIPLY defines the table and ADD TO EXPONENT
// is defined by reference to it: "When the exponents of either or both
// operands lie in the XFP or XFN range, the rules for exponent
// handling follow the definitions given under MULTIPLY" (p.102). Only
// meaningful when a.ef == 1 || b.ef == 1; the N/N cell of the table is
// the ordinary arithmetic each caller does on its own.
function FpNum fpExpRangeWinner(FpNum a, FpNum b) =
  (isXFP(a) || isXFP(b)) ? (isXFP(a) ? a : b) : (isXFN(a) ? a : b);

// ---- MULTIPLY (p.92): 96-bit product, exponent sum, post-normalization
// up to 96 places, ZM for a normalized order-of-magnitude zero above
// -1024.
function FpResult fpMul(FpNum a, FpNum b, Bool normalized, Bool noisy);
  FpResult r = fpNoResult(a);
  Bit#(1) sign = a.sign ^ b.sign;
  if (a.ef == 1 || b.ef == 1) begin
    // Fig.32 multiplication table: XFP dominates; XFN otherwise;
    // result fraction = unnormalized product, EF propagated.
    FpNum res = fpExpRangeWinner(a, b);
    Bit#(96) p = zeroExtend(a.frac) * zeroExtend(b.frac);
    res.frac = p[95:48];
    res.sign = sign;
    res.flags = a.flags;
    r.res = res; r.propagated = True;
    return r;
  end else begin
    Bit#(96) p = zeroExtend(a.frac) * zeroExtend(b.frac);
    Int#(14) e = signExtend(fpExp(a)) + signExtend(fpExp(b));
    let {frac48, adj, lc} = fpNormalize96(0, p, normalized, noisy);
    Bool zero = (p == 0);
    let {res, gen} = fpMakeExp(e + (zero ? 0 : adj), frac48, sign, a.flags);
    if (zero) begin
      // Order-of-magnitude zero keeps the summed exponent unmodified.
      Int#(14) mag = (e < 0) ? -e : e;
      res.ef = (mag > 1023) ? 1 : 0; res.em = (mag > 1023) ? 0 : truncate(pack(mag)); res.es = (e < 0) ? 1 : 0;
      gen = (mag > 1023);
    end
    r.res = res; r.generated = gen;
    r.zm = normalized && zero && (e > -1024);
    return r;
  end
endfunction

// ---- DIVIDE (p.93-94): a / b (a = dividend from the accumulator,
// b = divisor from storage; recip = True swaps them, R/). Both
// pre-normalized; quotient exponent = dividend - divisor exponents (+1
// when the dividend fraction >= divisor fraction, with the quotient
// then developed from a right-shifted dividend); zero divisor -> ZD,
// nothing changes.
function FpResult fpDiv(FpNum a, FpNum b, Bool normalized, Bool noisy);
  FpResult r = fpNoResult(a);
  if (b.frac == 0) begin r.zd = True; return r; end
  else if (a.ef == 1 || b.ef == 1) begin
    // Fig.23 division table.
    FpNum res = a;
    if (isXFP(a) && isXFP(b)) res = a;
    else if (isXFN(a) && isXFN(b)) res = a;
    else if (isXFP(a)) res = a;                         // XFP dividend -> XFP
    else if (isXFN(a)) res = a;                         // XFN dividend / N or XFP -> XFN
    else if (isXFP(b)) begin res = b; res.es = 1; end   // N / XFP -> XFN (exponent sign reversed)
    else begin res = b; res.es = 0; end                 // N / XFN -> XFP
    res.sign = a.sign ^ b.sign; res.flags = a.flags;
    r.res = res; r.propagated = True;
    return r;
  end else begin
    // Pre-normalize divisor and dividend (shift counts adjust exponents).
    UInt#(6) nzd = countZerosMSB(b.frac);
    Bit#(48) fd = b.frac << nzd; Int#(14) nd = unpack(zeroExtend(pack(nzd)));
    Bool zeroDividend = (a.frac == 0);
    UInt#(6) nza = zeroDividend ? 0 : countZerosMSB(a.frac);
    Bit#(48) fa = a.frac << nza; Int#(14) na = unpack(zeroExtend(pack(nza)));
    // The divisor is non-zero here (checked above), but Bluesim
    // evaluates the division even on the suppressed path, so never let
    // a zero reach the divider.
    Bit#(48) fdSafe = (fd == 0) ? 48'd1 : fd;
    Int#(14) e = (signExtend(fpExp(a)) - na) - (signExtend(fpExp(b)) - nd);
    Bit#(1) sign = a.sign ^ b.sign;
    Bit#(96) num = {fa, 48'b0};
    Bit#(48) q;
    if (fa >= fd) begin
      // Quotient overflow: exponent +1, quotient from the dividend
      // shifted right one place.
      e = e + 1;
      Bit#(96) qq = (num >> 1) / zeroExtend(fdSafe);
      q = qq[47:0];
    end else begin
      Bit#(96) qq = num / zeroExtend(fdSafe);
      q = qq[47:0];
    end
    if (zeroDividend) q = 0;
    let {res, gen} = fpMakeExp(e, q, sign, a.flags);
    if (zeroDividend) begin
      Int#(14) mag = (e < 0) ? -e : e;
      res.ef = (mag > 1023) ? 1 : 0; res.em = (mag > 1023) ? 0 : truncate(pack(mag)); res.es = (e < 0) ? 1 : 0;
      gen = (mag > 1023);
    end
    r.res = res; r.generated = gen;
    return r;
  end
endfunction

// Exponent range indicator selection for a result (p.85-86): returns
// which of XPFP / XPO / XPH / XPL / XPU applies (as a 5-bit one-hot in
// that order), given propagated/generated flags.
function Bit#(5) fpRangeBits(FpNum res, Bool generated, Bool propagated);
  if (res.ef == 1) begin
    if (propagated && res.es == 0) return 5'b10000;        // XPFP
    else if (generated && res.es == 0) return 5'b01000;    // XPO
    else if (generated && res.es == 1) return 5'b00001;    // XPU
    else return 0;                                          // propagated XFN: none listed
  end else if (res.es == 0) begin
    if (res.em[9] == 1) return 5'b00100;                    // XPH: 1024 > E >= 512
    else if (res.em[8:6] != 0) return 5'b00010;             // XPL: 512 > E >= 64
    else return 0;
  end else return 0;
endfunction

endpackage
