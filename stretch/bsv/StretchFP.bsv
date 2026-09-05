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
function FpNum fpFromAcc(Word64 accLeft, Word64 signByte) =
  FpNum { ef: accLeft[63], em: accLeft[62:53], es: accLeft[52], frac: accLeft[51:4],
          sign: signByte[3], flags: signByte[2:0] };

function Word64 fpAccLeft(FpNum x, Word64 oldLeft) = { x.ef, x.em, x.es, x.frac, oldLeft[3:0] };

function Word64 fpSignByte(FpNum x, Word64 oldByte) = { oldByte[63:4], x.sign, x.flags };

// Signed exponent as an integer (ignoring the flag).
function Int#(13) fpExp(FpNum x);
  Int#(13) m = unpack(zeroExtend(x.em));
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
  Bit#(10) em = gen ? 10'd0 : truncate(pack(mag));
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

// Normalize a 96-bit fraction with overflow bit into 48 bits and an
// exponent adjustment; noisy mode shifts in ones. Zero fractions are
// left alone.
function Tuple3#(Bit#(48), Int#(14), Bool) fpNormalize96(Bit#(1) ovf, Bit#(96) f96, Bool normalized, Bool noisy);
  Bit#(97) v = {ovf, f96};
  Int#(14) adj = 0;
  Bool lostCarry = False;
  if (v == 0) return tuple3(0, 0, False);
  else if (!normalized) begin
    // Unnormalized: high 48 bits of the 96-bit sum; overflow bit lost.
    lostCarry = (ovf == 1);
    return tuple3(f96[95:48], 0, lostCarry);
  end else begin
    if (ovf == 1) begin
      // Right shift one to bring the overflow bit in (p.81).
      Bit#(96) sh = v[96:1];
      return tuple3(sh[95:48], 1, False);
    end else begin
      // Left shift until the high-order bit is one (up to 95 places):
      // a leading-zero count and one shift, with noisy mode filling the
      // vacated low-order bits with ones.
      UInt#(7) nz = countZerosMSB(f96);
      Int#(14) n = unpack(zeroExtend(pack(nz)));
      Bit#(96) w = f96 << nz;
      if (noisy) w = w | ((96'b1 << nz) - 1);
      return tuple3(w[95:48], -n, False);
    end
  end
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
  if (addMag) a.sign = 0;
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
    r.res = res; r.propagated = (res.ef == 1);
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
      if (addMag && sign == 1) begin
        // ADD TO MAGNITUDE: a negative sum becomes a forced zero with
        // the accumulator's sign and exponent (p.88).
        forcedZero = True;
        sum = 0;
        sign = 0;
      end
      let {frac48, adj, lostCarry} = fpNormalize96(sum[96], sum[95:0], normalized, noisy);
      Bool zeroResult = (sum == 0);
      Int#(14) e = signExtend(fpExp(big)) + (zeroResult ? 0 : adj);
      let {res, gen} = fpMakeExp(e, frac48, sign, a.flags);
      if (zeroResult) begin
        // Order-of-magnitude zero: exponent of the larger-exponent
        // operand, no normalization, no exponent change.
        res.ef = big.ef; res.em = big.em; res.es = big.es;
        gen = False;
      end
      r.res = res;
      r.lc = lostCarry;
      r.generated = gen;
      r.ls = zeroResult && !(a.frac == 0 && b.frac == 0) && !forcedZero;
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

// ---- MULTIPLY (p.92): 96-bit product, exponent sum, post-normalization
// up to 96 places, ZM for a normalized order-of-magnitude zero above
// -1024.
function FpResult fpMul(FpNum a, FpNum b, Bool normalized, Bool noisy);
  FpResult r = fpNoResult(a);
  Bit#(1) sign = a.sign ^ b.sign;
  if (a.ef == 1 || b.ef == 1) begin
    // Fig.23 multiplication table: XFP dominates; XFN otherwise;
    // result fraction = unnormalized product, EF propagated.
    FpNum res = (isXFP(a) || isXFP(b)) ? (isXFP(a) ? a : b) : (isXFN(a) ? a : b);
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
