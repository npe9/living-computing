// StretchALU.bsv
//
// Sign-and-magnitude arithmetic primitives for VFL integer operations.
//
// SOURCE for sign-and-magnitude representation: 22-6530-2 p.~87
// "Numeric data may be signed or unsigned. For unsigned data, the sign
// is simply omitted..." and p.~103 "If the field is signed, the
// rightmost byte is the sign byte." This is explicitly NOT two's
// complement -- unlike most machines of even a few years later, and
// unlike the index-word value field's own internal encoding (also
// sign+magnitude, see StretchTypes.indexValue).
//
// SCOPE / SIMPLIFICATION (see bsv/README.md "Scope" for the full
// statement): the manual defines the sign as occupying a specific bit
// position *within* the sign byte for the accumulator sign byte
// register ("the sign of the accumulator operand is contained in the
// fifth bit position from the left in the accumulator sign byte
// register", p.~103) but does not give an equally explicit bit-within-
// byte rule for general storage fields in the excerpted text. This
// implementation uses the most-significant bit of the byte-size-wide
// sign byte as the sign, uniformly for storage fields and for the
// accumulator (modeled as a flat 128-bit sign-magnitude register, see
// below) -- a documented simplification, not a transcription.
//
// The accumulator (words 8/9, "Left Half"/"Right Half") is modeled here
// as a single conceptual 128-bit sign-magnitude value: sign = bit 0 of
// word 8 (its IBM-leftmost bit), magnitude = the remaining 127 bits of
// {word8,word9}. The separate accumulator sign byte register (word 10)
// is storage-addressable (StretchStorage) but not consulted by the ALU
// -- another documented simplification of the same "Sign Control"
// section.

package StretchALU;

import StretchTypes::*;

typedef struct {
  Bit#(1) sign; // 1 = negative
  Bit#(128) mag;
} SM128 deriving (Bits, Eq, FShow);

// The accumulator is words 8 and 9 (128 magnitude bits, Left then
// Right) plus the sign byte register, word 10 (IBM bits 0-7; the sign
// is bit 4 -- StretchFP sbSign/sbWith). Until jb_af1c F204C the model
// kept the VFL sign in bit 0 of word 8 with a 127-bit magnitude; the
// diagnostic's 64-bit checks of the left half need all 128 bits.
function Bit#(1) accSign(Word64 signByte) = signByte[59]; // IBM bit 4 of word 10

function SM128 accToSM(Word64 hi, Word64 lo, Word64 signByte);
  return SM128 { sign: accSign(signByte), mag: {hi, lo} };
endfunction

function Tuple2#(Word64,Word64) packAcc(Bit#(128) mag);
  return tuple2(mag[127:64], mag[63:0]);
endfunction

// Sign-and-magnitude add: computes a + b (each sign+magnitude) with a
// magnitude wide enough to avoid overflow inside this helper; the
// caller truncates/aligns to the field width it cares about and is
// responsible for the Lost Carry indicator when it does not fit.
function SM128 smAdd(SM128 a, SM128 b);
  if (a.sign == b.sign)
    return SM128 { sign: a.sign, mag: a.mag + b.mag };
  else if (a.mag >= b.mag)
    return SM128 { sign: a.sign, mag: a.mag - b.mag };
  else
    return SM128 { sign: b.sign, mag: b.mag - a.mag };
endfunction

// THE CONNECTIVE COUNTS, Reference Manual printed pp.75-76.
//
// p.75: "Two counts describing the result field are available after a
// connective operation.  The seven-bit all-ones counter, bits 44-50
// of location 7, contains a count of all ones in the result field.
// The seven-bit left-zeros counter, bits 17-23 of location 7,
// contains a count of" -- and p.76 finishes it -- "the number of
// zeros in the result field that are to the left of the most
// significant one-bit."
//
// p.76 on the field they are taken over: "Both counters operate
// modulo 128.  Each count is on the final result field.  **In
// CONNECT and CONNECT FOR TEST, the counts are made on the result
// field with byte size eight.  In CONNECT TO MEMORY, the counts are
// made on the result field after it is converted to the byte size of
// the storage operand.**"
//
// ARRIVED VIA MCP, printed p.17 lines 32-36.  A Hollerith digit is
// one punch among several rows, so CONNECT FOR TEST over the column
// leaves THE DIGIT ITSELF as the left-zeros count, and MCP reads it
// back as "$LZC+.3" to build a channel number.
//
// THE ALL-ZERO CASE IS AN INFERENCE, the one thing the page does not
// state: with no one-bit there is nothing for the zeros to be to the
// left of, so the count is the field width.

// Index of the highest one-bit, plus one; zero if there is none.
function Bit#(8) topBitPlus1(Bit#(128) v);
  Bit#(8) hi = 0;
  for (Integer i = 0; i < 128; i = i + 1)
    if (v[i] == 1) hi = fromInteger(i) + 1;
  return hi;
endfunction

function Bit#(7) connAllOnes(Bit#(128) v);
  Bit#(8) n = 0;
  for (Integer i = 0; i < 128; i = i + 1)
    if (v[i] == 1) n = n + 1;
  return truncate(n);          // "operate modulo 128"
endfunction

function Bit#(7) connLeftZeros(Bit#(128) v, Bit#(8) width);
  Bit#(8) hi = topBitPlus1(v);
  return truncate((hi == 0) ? width : (width - hi));
endfunction

// LOAD CONVERTED's decimal-to-binary conversion, Reference Manual
// printed pp.71-73.
//
// p.72, "Load Converted (LCV)": "The addressed storage field is
// converted as an integer from decimal to binary or from binary to
// decimal depending on the setting of the radix modifier.  The
// accumulator is cleared and the converted field is placed into it at
// the specified offset."
//
// p.72 again, under Radix: "Bit 53 of the instruction, the radix
// modifier, specifies the radix of the OPERAND TO BE CONVERTED ...
// If this bit is zero, the original field is binary; if this bit is
// one, the original field is decimal.  This modifier also specifies
// the interpretation of the byte size field in the same manner as in
// integer arithmetic operations."
//
// and p.73's top completes it: the decimal field is converted "to
// byte size four" BEFORE the decimal-to-binary conversion -- so a
// byte wider than four contributes its four low-order bits and a
// narrower one is zero-extended, exactly as p.63 says of decimal
// STORE.
//
// `numBits` is the NUMERIC part only: a signed decimal field carries
// its sign byte as the rightmost byte and inside `len_` (p.56, "the
// field length specifies the total length in bits of the storage
// operand, INCLUDING THE SIGN BYTE when present"), so the caller
// shifts it off and passes what remains.
//
// Returns the binary value and the DIGIT COUNT, which the caller
// needs for Partial Field: p.73, "In a decimal-to-binary conversion,
// this indicator is also actuated if the storage field exceeds 15
// decimal digits (as could be specified using a byte size of less
// than four).  Meaningless results are then obtained."  Fifteen
// digits is under 2^50, so sixteen positions of accumulation cannot
// overflow the 128-bit magnitude and the count is the only thing
// standing between a caller and a meaningless answer.
function Integer pow10i(Integer k);
  Integer r = 1;
  for (Integer i = 0; i < k; i = i + 1) r = r * 10;
  return r;
endfunction

function Tuple2#(Bit#(128), Bit#(7))
         bcdToBinary(Bit#(64) digitsRaw, Bit#(7) numBits, Bit#(4) bsEff);
  Bit#(128) val = 0;
  Bit#(7)   nd  = 0;
  for (Integer k = 0; k < 16; k = k + 1) begin
    Bit#(7) lo = fromInteger(k) * zeroExtend(bsEff);
    if (lo < numBits) begin
      Bit#(7) rem = numBits - lo;
      Bit#(4) w   = (rem >= zeroExtend(bsEff)) ? bsEff : truncate(rem);
      Bit#(8) wmask = (w >= 8) ? 8'hFF : ((8'b1 << w) - 1);
      Bit#(8) byteVal = truncate(digitsRaw >> lo) & wmask;
      // "converted to byte size four": the four low-order bits.  A
      // byte narrower than four was already zeroed above it by
      // wmask, so truncation serves both cases.
      Bit#(4) digit = truncate(byteVal);
      val = val + (zeroExtend(digit) * fromInteger(pow10i(k)));
      nd  = fromInteger(k) + 1;
    end
  end
  return tuple2(val, nd);
endfunction

// ADD MAGNITUDE TO MEMORY's store rule, Reference Manual printed
// p.62, which is two sentences and both of them are about SIGNS:
//
//   "If the sum has the same sign as the sign of the storage operand,
//   it replaces that operand in storage.  If the sum is of opposite
//   sign, zero bytes replace the numeric part of the storage field.
//   In either case the sign byte, if any, of the storage operand is
//   not changed."
//
// So the sign STORED is always the storage operand's own sign and
// only the magnitude is in question.  Figure 13 on the same page
// ("Sign Condition Results") tabulates every combination and this
// reproduces its whole Add Magnitude to Memory block: storage 3-
// plus accumulator 5+ stores 0-, storage 5- plus 3+ stores 2-.
//
// `mag` is false for plain ADD TO MEMORY, which stores the sum as it
// comes, so one call site serves both.
function SM128 magToMemory(Bool mag, SM128 sum, SM128 opnd);
  // A zero sum is signless; treating it as "opposite" would still
  // store zero, so the comparison is safe either way, but compare on
  // the sign bits as the manual's table does.
  return !mag ? sum
              : SM128 { sign: opnd.sign,
                        mag: (sum.sign == opnd.sign) ? sum.mag : 0 };
endfunction

// Three-way compare of two sign-magnitude values. Returns -1/0/+1 in a
// signed 2-bit-ish encoding via Ordering-like tags.
typedef enum { CmpLow, CmpEqual, CmpHigh } Cmp3 deriving (Bits, Eq, FShow);

function Cmp3 smCompare(SM128 a, SM128 b);
  // normalize sign of zero magnitude so -0 == +0
  Bit#(1) as = (a.mag == 0) ? 0 : a.sign;
  Bit#(1) bs = (b.mag == 0) ? 0 : b.sign;
  if (as != bs)
    return (as == 1) ? CmpLow : CmpHigh; // negative < positive
  else if (a.mag == b.mag)
    return CmpEqual;
  else if (as == 0)
    return (a.mag < b.mag) ? CmpLow : CmpHigh;
  else // both negative: larger magnitude is the lower value
    return (a.mag > b.mag) ? CmpLow : CmpHigh;
endfunction

// Extract (sign, magnitude) from a right-justified `len_`-bit field per
// the a (unsigned) / b (invert) VFL modifiers and the byte-size sign
// byte convention documented above.
function SM128 fieldToSM(Bit#(64) raw, Bit#(7) len_, Bit#(4) byteSize,
                          Bit#(1) unsign, Bit#(1) invert);
  if (unsign == 1)
    // THE NEGATIVE SIGN MODIFIER APPLIES TO AN UNSIGNED FIELD TOO,
    // and this branch used to drop it.  Reference Manual printed
    // p.60, under ADD's MODIFIERS: "Negative Sign.  This modifier
    // designates whether the sign of the storage operand is taken
    // as-is or is inverted before the operation takes place.
    // **UNSIGNED FIELDS ARE CONSIDERED POSITIVE BEFORE THIS MODIFIER
    // IS APPLIED.**"  Positive first, then inverted -- so an
    // unsigned operand with the modifier set is NEGATIVE.
    //
    // p.57's "Sign Control" table says it a second way, in the
    // TO-ACCUMULATOR column: bits 51-52 = 10 is "Unsigned, use +"
    // and 11 is "Unsigned, use -".  Both bits set is a real,
    // named combination, and it was unreachable here.
    //
    // WHAT IT COST: every unsigned SUBTRACT was an ADD.  Found by
    // decks/plus_mg.strap running Reference Manual printed p.61's
    // own Figure 12, where "-MG(BU,64,8),Y,0" is supposed to compute
    // x-y and computed x+y instead.  **MCP RELIES ON THIS** -- its
    // printed p.18 line 35 is "-(BU,18),$15+.28  -COMPUTE THE NUMBER
    // OF ...", an unsigned subtract whose answer would have been
    // wrong the moment the bootstrap reached that page.
    return SM128 { sign: invert, mag: zeroExtend(raw) };
  else begin
    Bit#(1) s = raw[byteSize - 1];
    Bit#(64) mag = raw >> byteSize;
    Bit#(1) finalSign = (invert == 1) ? ~s : s;
    return SM128 { sign: finalSign, mag: zeroExtend(mag) };
  end
endfunction

// Pack a sign-magnitude value back into a right-justified `len_`-bit
// field with the given byte size (signed) or none (unsigned).
function Bit#(64) smToField(SM128 v, Bit#(7) len_, Bit#(4) byteSize, Bit#(1) unsign);
  if (unsign == 1)
    return truncate(v.mag);
  else begin
    Bit#(64) mag = truncate(v.mag);
    Bit#(64) signByte = zeroExtend(v.sign) << (byteSize - 1);
    return (mag << byteSize) | signByte;
  end
endfunction

endpackage
