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
// THE SIGN BYTE OF A STORAGE FIELD, R23-9694 printed p.100's table: S,
// ST, STU, STUV, then zones to the left of S for byte sizes 5-8.  So the
// sign bit of a right-justified field is bit min(byteSize,4)-1, and it
// lines up with position 4 of the accumulator sign byte register.  Until
// 2026-11-09 this file used the byte's top bit, a zone bit for byte sizes
// above four, and called that a simplification; signFieldIdx is the fix.
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

// THE RADIX CONVERSIONS ARE mkCvtBox's (StretchCvtBox.bsv), 2026-11-17.
// bcdToBinary (sixteen constant multiply-adds) and binaryToBcd (twenty-
// four 96-bit divides by ten) used to be here and were called inline
// from execute()'s CV, LCV and LTRCV arms; docs/fpga_feasibility.md
// section 10.2 measured the first at 2,570 LUT4 a site and the second
// did not finish synthesis.  Every conversion now goes through the box
// by execute()'s NeedBox bail.  What the caller still does itself is
// below (decFieldDigits): lay a decimal field of any byte size out as
// four-bit digits, which is wiring, not arithmetic.

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

// >>> THE BINARY ADD'S LOST CARRY AND PARTIAL FIELD, ONE RULE FOR EVERY
// ARM THE MANUAL SENDS TO "AS IN ADD", 2026-11-16. <<<  Reference Manual
// 22-6530-2 printed p.60 (PDF 63), ADD, read in the page image: "Lost
// Carry (LC).  This indicator is actuated if information is lost because
// a carry attempts to propagate beyond the left end of the accumulator.
// Partial Field (PF).  This indicator is turned on if significant bits of
// the data field from storage overlap the left end of the accumulator.
// The accumulator operand is extended with high-order zeros to combine
// with the storage operand, but the high-order bits of the result are
// dropped.  A partial field condition will not cause a lost carry
// indication.  However, both conditions may arise during the execution of
// a single instruction."  printed p.61 sends +MG there ("set as in ADD"),
// and printed p.69 sends binary MULTIPLY AND ADD there: "Lost Carry (LC).
// In a binary operation, this indicator is set as in ADD", its PF "also
// turned on in a binary operation if the offset is such that significant
// bits of the product attempt to combine with accumulator positions to the
// left of the left end of the accumulator.  Such high-order bits of the
// product are lost."
//
// So: PF is judged on the addend shifted WIDE; LC on the carry out of the
// 128-bit sum of what is left (the dropped bits cannot carry: "will not
// cause a lost carry indication"), and only for like effective signs --
// unlike signs are a subtraction, which cannot carry out.  `accUsed` is
// the accumulator operand as the arm uses it (+MG passes it positive);
// `addend` is right-justified, the offset not yet applied.  The sum's
// magnitude wraps modulo 2^128, which is the carry being lost.
// Measured by decks/vfl_binary_add_indicators.strap (B5-B10 for +, B13-B16
// for *+).
typedef struct { SM128 sum; Bool lc; Bool pf; } BinAccAdd deriving (Bits, Eq);

function BinAccAdd binAccAdd(SM128 accUsed, SM128 addend, Bit#(8) offSh);
  Bit#(256) wide = zeroExtend(addend.mag) << offSh;
  SM128 addSh = SM128 { sign: addend.sign, mag: truncate(wide) };
  Bit#(129) carrySum = zeroExtend(accUsed.mag) + zeroExtend(addSh.mag);
  return BinAccAdd { sum: smAdd(accUsed, addSh),
                     lc:  (accUsed.sign == addSh.sign) && carrySum[128] == 1,
                     pf:  (wide >> 128) != 0 };
endfunction

// >>> THE BINARY TO-MEMORY ADD -- M+, M+MG and M+1 -- AND ITS LOST CARRY
// AND PARTIAL FIELD, 2026-11-16. <<<  (The arms set neither until then;
// the decimal arm, decMInd in StretchExecute, did.)  Read in the page
// images, Reference Manual printed p.59 (PDF 62), the class rule: "In
// binary to-memory operations, this indicator [LC] is actuated by a carry
// beyond the leftmost bit of the addressed field ... This indicator is
// also actuated when a to-memory operation with an unsigned storage
// operand produces a negative result.  In all cases, the operation is
// completed normally except for the loss of the carry."  PF: "In
// to-memory operations, the indicator is turned on when there are non-zero
// accumulator positions to the left of the accumulator field that is
// participating in the operation.  In binary operations to storage, this
// indicator is turned on if there is any one-bit in the accumulator to the
// left of the participating field."  printed p.62 (PDF 65), ADD TO MEMORY,
// the same two: "Lost Carry (LC).  This indicator is actuated by a carry
// beyond the leftmost digit, either binary or decimal, of the addressed
// field.  This indicator is also turned on if the result of an unsigned
// operation is negative.  In such a case, the magnitude of the result is
// stored in storage.  Partial Field (PF).  This indicator is turned on if
// there are non-zero digits, either binary or decimal, in the accumulator
// to the left of the highest order digit that is participating in the
// operation"; M+MG "set as in ADD TO MEMORY" (p.62); M+1 (p.63): "Lost
// Carry (LC) ... These indicators operate as in ADD TO MEMORY", and "ADD
// ONE TO MEMORY is identical to an ADD TO MEMORY in which the accumulator
// operand is +1, except that the partial field indicator is not
// affected."
//
// THE PARTICIPATING FIELD IS THE STORAGE FIELD'S NUMERIC WIDTH.  p.62's
// Programming Note: "In operations to storage, the length of the
// accumulator field between the specified offset and the left end of the
// accumulator can be less than the number of bits from the storage operand
// which are to take part in the operation.  In this event the accumulator
// operand is lengthened for the operation by the addition of high-order
// zeros."  So the accumulator operand is `numBits` wide and its bits above
// are NOT part of the sum -- p.59's "to the left of the participating
// field" says they are outside it.  Until 2026-11-16 the arm added the
// whole accumulator from the offset up, which made no difference to a
// like-signed sum (the field write drops the excess) but let a high
// accumulator bit win an unlike-signed one.
//
// "UNSIGNED ... NEGATIVE" is the STORED sign: Figure 13 (p.62) stars the
// unsigned ADD TO MEMORY cells whose sum is negative (3+ with 5-: 2+*) and
// none of ADD MAGNITUDE TO MEMORY's, whose negative sum stores zero bytes
// under the storage sign (3+ with 5-, U: 8+; the U rows have no star).
//
// THE RESULT INDICATORS GET THE FIELD'S SUM, the carry dropped: CHOSEN.
// p.62 says "set according to the algebraic sum of the two operands,
// whether the sign is stored or not" (M+) and "according to the final
// result stored" (M+MG); p.59's "completed normally except for the loss of
// the carry" reads the sum as the field holds it, which is what the
// decimal arm (dStored) already did.  The two readings differ only when
// LC is on.
typedef struct { SM128 stored; Bool lc; Bool pf; } BinMemAdd deriving (Bits, Eq);

function BinMemAdd binMemAdd(Bool magnitude, Bool addOne, Bit#(1) unsign,
                             SM128 opnd, SM128 accSh, Bit#(7) numBits);
  Bit#(128) fmask = (numBits >= 64) ? 128'hFFFFFFFFFFFFFFFF
                                    : ((128'd1 << numBits) - 1);
  SM128 accUsed = SM128 { sign: accSh.sign, mag: accSh.mag & fmask };
  SM128 sum = smAdd(opnd, accUsed);
  Bool carry = (opnd.sign == accUsed.sign) && ((sum.mag & ~fmask) != 0);
  SM128 stored = magToMemory(magnitude,
                   SM128 { sign: sum.sign, mag: sum.mag & fmask }, opnd);
  return BinMemAdd { stored: stored,
                     lc: carry || (unsign == 1 && stored.sign == 1),
                     pf: !addOne && ((accSh.mag & ~fmask) != 0) };
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
function Bit#(4) signFieldIdx(Bit#(4) byteSize) = (byteSize > 4) ? 3 : (byteSize - 1);

// The data flag bits T, U and V of a field, for the indicators (printed
// p.57, p.59).  A sign byte of size n holds the first n-1 of them, by
// p.100's table; flags not obtained from storage read as off.
function Bit#(3) fieldFlags(Bit#(64) raw, Bit#(4) byteSize, Bit#(1) unsign);
  if (unsign == 1) return 0;
  else case (byteSize)
    1: return 0;
    2: return {raw[0], 2'b00};
    3: return {raw[1:0], 1'b0};
    default: return raw[2:0];
  endcase
endfunction

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
    Bit#(1) s = raw[signFieldIdx(byteSize)];
    Bit#(64) mag = raw >> byteSize;
    Bit#(1) finalSign = (invert == 1) ? ~s : s;
    return SM128 { sign: finalSign, mag: zeroExtend(mag) };
  end
endfunction

// THE FIELD A DECIMAL UNSIGNED STORE WRITES.  Reference Manual printed
// p.63 (PDF 66), read in the ink: "In a decimal STORE, the byte size
// refers to the size of each byte in the storage field ... Each 4-bit byte
// of the accumulator replaces the four low-order bits of each byte of the
// storage field ... If the specified byte size is greater than four, the
// remaining high-order bits of each byte are replaced by the corresponding
// zone bits in the accumulator sign byte register.  If the specified byte
// size is less than four, only the low-order bits from each accumulator
// byte replace each byte in the storage field."
//
// `acc` is the accumulator, integral 4-bit bytes (printed p.58), already
// shifted by the offset.  `sb` is the sign byte register with IBM bit 7 at
// sb[0], so a byte's position j, counted from its low end, takes sb[j]:
// its zone positions line up with the register's.  The result is
// right-justified and its caller keeps the low len_ bits: "only part of
// the high-order digit is stored".  The byte size is static in each
// case arm, so this elaborates to wires and an 8-way mux.
function Bit#(64) decStoreFieldOf(Integer b, Bit#(128) acc, Bit#(8) sb);
  Bit#(64) out = 0;
  for (Integer i = 0; i < 64; i = i + 1) begin
    Integer k = div(i, b);
    Integer j = mod(i, b);
    if (j >= 4)          out[i] = sb[j];
    else if (4*k+j < 128) out[i] = acc[4*k+j];
  end
  return out;
endfunction

function Bit#(64) decStoreField(Bit#(128) acc, Bit#(4) byteSize, Bit#(8) sb);
  case (byteSize)
    1: return decStoreFieldOf(1, acc, sb);
    2: return decStoreFieldOf(2, acc, sb);
    3: return decStoreFieldOf(3, acc, sb);
    4: return decStoreFieldOf(4, acc, sb);
    5: return decStoreFieldOf(5, acc, sb);
    6: return decStoreFieldOf(6, acc, sb);
    7: return decStoreFieldOf(7, acc, sb);
    default: return decStoreFieldOf(8, acc, sb);
  endcase
endfunction

// Which bits of that field are numeric, not zone: the "data field stored"
// that sets the result indicators (printed p.63), with the zones excluded.
function Bit#(64) decStoreNumericOf(Integer b);
  Bit#(64) out = 0;
  for (Integer i = 0; i < 64; i = i + 1)
    if (mod(i, b) < 4) out[i] = 1;
  return out;
endfunction

function Bit#(64) decStoreNumeric(Bit#(4) byteSize);
  case (byteSize)
    1: return decStoreNumericOf(1);
    2: return decStoreNumericOf(2);
    3: return decStoreNumericOf(3);
    4: return decStoreNumericOf(4);
    5: return decStoreNumericOf(5);
    6: return decStoreNumericOf(6);
    7: return decStoreNumericOf(7);
    default: return decStoreNumericOf(8);
  endcase
endfunction

// PF, printed p.63: "turned on if there is a non-zero byte to the left of
// the high-order byte stored ... If all accumulator bytes to the left of
// the entire high-order accumulator byte taking part in the operation are
// zero, the partial field indicator is not turned on even if the
// high-order bits of the high-order byte that were not stored are
// non-zero."  Digit k takes part if any of its byte falls in the field,
// which is k*byteSize < len_.
function Bool decStorePF(Bit#(128) acc, Bit#(4) byteSize, Bit#(7) len_);
  Bool pf = False;
  for (Integer k = 0; k < 32; k = k + 1) begin
    UInt#(9) at = fromInteger(k) * unpack(zeroExtend(byteSize));
    Bit#(4) digit = acc[4*k+3:4*k];
    if (at >= unpack(zeroExtend(len_)) && digit != 0) pf = True;
  end
  return pf;
endfunction

// =====================================================================
// DECIMAL VFL ARITHMETIC'S BYTE PLACEMENT (2026-11-16, G2.3).  Wiring
// only: the decimal SUM is mkDecBox's (StretchDecBox.bsv), and these
// four functions move bytes between a storage field of any byte size and
// the accumulator's four-bit digits, which is all p.58 asks of them.
// Each is a per-byte-size case whose arms elaborate to wires, the shape
// decStoreField above already has.
// =====================================================================

// A STORAGE FIELD'S NUMERIC BYTES AS FOUR-BIT DIGITS.  Reference Manual
// printed p.58 (PDF 61), Radix and Byte Size: "If the byte size is
// greater than four, only the four low-order bits of each byte take part
// in the operation.  The remaining bits of each byte are ignored. ...
// When complementation is not involved, each byte of the storage operand
// is converted to a four-bit byte for processing by the addition of
// high-order zeros."  And: "the high-order byte of the memory operand
// may have an effective byte size less than that specified ... The
// high-order byte is processed according to its effective byte size" --
// which right-justified bits with zeros above the field give for free.
//
// `num` is the NUMERIC part, right-justified (a signed field's sign byte
// already stripped, as fieldToSM does).  Byte k becomes digit k.  The
// accumulator has 32 digit positions (printed p.57); a byte size of one
// can describe 64 digits, and the second result says whether any digit
// beyond the 32nd is non-zero -- the caller's Partial Field.
function Tuple2#(Bit#(128), Bool) decCompactOf(Integer b, Bit#(64) num);
  Bit#(128) out = 0;
  Bool      hi  = False;
  Integer   wb  = (b < 4) ? b : 4;
  for (Integer k = 0; k * b < 64; k = k + 1)
    for (Integer j = 0; j < wb; j = j + 1) begin
      Integer i = k * b + j;
      if (i < 64) begin
        if (k < 32) out[4*k+j] = num[i];
        else if (num[i] == 1) hi = True;
      end
    end
  return tuple2(out, hi);
endfunction

function Tuple2#(Bit#(128), Bool) decCompact(Bit#(64) num, Bit#(4) byteSize);
  case (byteSize)
    1: return decCompactOf(1, num);
    2: return decCompactOf(2, num);
    3: return decCompactOf(3, num);
    4: return decCompactOf(4, num);
    5: return decCompactOf(5, num);
    6: return decCompactOf(6, num);
    7: return decCompactOf(7, num);
    default: return decCompactOf(8, num);
  endcase
endfunction

// A DECIMAL STORAGE FIELD AS FOUR-BIT DIGITS, for the radix converter
// (LCV and LTRCV, decimal to binary).  Reference Manual printed p.72,
// LOAD CONVERTED, Radix: the radix modifier "also specifies the
// interpretation of the byte size field in the same manner as in integer
// arithmetic operations", and the field is converted "to byte size four"
// before the conversion -- a byte wider than four gives its four low-
// order bits, a narrower one is zero-extended (decCompact does both).
//
// `numBits` is the numeric part only (a signed field's sign byte is
// shifted off by the caller, p.56).  At most SIXTEEN bytes are taken,
// which is what the inline bcdToBinary took (its loop ran to sixteen):
// p.73's "if the storage field exceeds 15 decimal digits ... Meaningless
// results are then obtained" makes the sixteenth the PF case and any
// further one meaningless anyway, and keeping the bound keeps every
// result the model gave.  The count is POSITIONAL -- the bytes the field
// has, ceil(numBits / byte size) capped at sixteen, zero bytes included
// -- because Partial Field is judged on the field's size, not its value.
//
// `digits` must be zero above `numBits` (both callers mask it already).
// Byte k starts at bit k * byte size; the positions are an adder chain
// (sixteen 7-bit adds), not sixteen products -- the first version wrote
// k * byte size and yosys gave the products eleven MULT18X18D blocks
// (docs/fpga_feasibility.md 10.6).  At most 15 * 8 = 120, so seven bits
// hold every position compared.
function Tuple2#(Bit#(64), Bit#(7))
         decFieldDigits(Bit#(64) digits, Bit#(7) numBits, Bit#(4) bsEff);
  match {.dg, .hi} = decCompact(digits, bsEff);
  Bit#(7) nd = 0;
  Bit#(7) lo = 0;
  for (Integer k = 0; k < 16; k = k + 1) begin
    if (lo < numBits) nd = fromInteger(k + 1);
    lo = lo + zeroExtend(bsEff);
  end
  return tuple2(dg[63:0], nd);
endfunction

// THE INVERSE FOR A TO-MEMORY ADD, which keeps every bit it does not
// replace.  Printed p.61, ADD TO MEMORY, Radix: "If the byte size of a
// decimal storage field participating in ADD TO MEMORY is greater than
// four, only the four low-order bits of each byte participate in the
// addition.  The high-order bits of each byte are not changed by the
// operation.  If a byte size less than four is specified ... Only the
// low-order bits of each sum byte replace the byte from storage ... the
// high-order positions that are dropped from each sum byte may contain
// one bits.  These are lost and no indication of the loss is given."
// So bit j of byte k is digit k's bit j while j < 4, and the old bit
// otherwise.  (STORE's version, decStoreField, takes the zone bits from
// the sign byte register instead; p.58: "they remain unchanged in all
// other arithmetic operations to storage".)
function Bit#(64) decMergeFieldOf(Integer b, Bit#(128) digits, Bit#(64) old);
  Bit#(64) out = old;
  for (Integer i = 0; i < 64; i = i + 1) begin
    Integer k = div(i, b);
    Integer j = mod(i, b);
    if (j < 4 && 4*k+j < 128) out[i] = digits[4*k+j];
  end
  return out;
endfunction

function Bit#(64) decMergeField(Bit#(128) digits, Bit#(64) old, Bit#(4) byteSize);
  case (byteSize)
    1: return decMergeFieldOf(1, digits, old);
    2: return decMergeFieldOf(2, digits, old);
    3: return decMergeFieldOf(3, digits, old);
    4: return decMergeFieldOf(4, digits, old);
    5: return decMergeFieldOf(5, digits, old);
    6: return decMergeFieldOf(6, digits, old);
    7: return decMergeFieldOf(7, digits, old);
    default: return decMergeFieldOf(8, digits, old);
  endcase
endfunction

// The number of digit positions a numeric part of `numBits` bits holds
// at this byte size, counting a short high-order byte as a digit
// (printed p.58: it "is processed according to its effective byte
// size").  At most 64 (byte size one).
function Bit#(7) decDigitCount(Bit#(7) numBits, Bit#(4) byteSize);
  Bit#(8) n = zeroExtend(numBits);
  Bit#(8) b = zeroExtend(byteSize);
  return truncate((n + b - 1) / b);
endfunction

// A mask of the low `nd` digit positions of the 32.
function Bit#(128) decDigitMask(Bit#(7) nd);
  Bit#(9) sh = 4 * zeroExtend(nd);
  return (nd >= 32) ? '1 : ((128'd1 << sh) - 1);
endfunction

// Pack a sign-magnitude value back into a right-justified `len_`-bit
// field with the given byte size (signed) or none (unsigned).
//
// `oldByte` holds what goes around the sign bit, right-justified in the
// sign byte's own bits: a store's comes from storeSignByte, and a
// to-memory operation passes the operand's raw field, because printed p.58
// says only STORE and STORE ROUNDED replace flags and zones.
function Bit#(64) smToField(SM128 v, Bit#(7) len_, Bit#(4) byteSize, Bit#(1) unsign, Bit#(64) oldByte);
  if (unsign == 1)
    return truncate(v.mag);
  else begin
    Bit#(64) mag = truncate(v.mag);
    Bit#(64) byteMask = (64'd1 << byteSize) - 1;
    Bit#(64) signByte = oldByte & byteMask;
    signByte[signFieldIdx(byteSize)] = v.sign;
    return (mag << byteSize) | signByte;
  end
endfunction

// What a signed STORE puts in the sign byte, printed p.63: "the data flag
// bits and zone bits that are in the accumulator sign byte register", as
// many as the byte size holds, p.100's table.  S is register position 4,
// which is sb[3] here (IBM bit 7 at sb[0]).  The caller replaces S itself.
function Bit#(64) storeSignByte(Bit#(8) sb, Bit#(4) byteSize);
  Bit#(64) r = zeroExtend(sb);
  return (byteSize < 4) ? (r >> (4 - byteSize)) : r;
endfunction

endpackage
