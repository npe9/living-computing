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
    return SM128 { sign: 0, mag: zeroExtend(raw) };
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
