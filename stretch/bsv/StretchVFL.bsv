// StretchVFL.bsv
//
// Variable-field-length bit extraction/insertion -- the mechanism that
// makes Stretch's "bit-addressable, 1-64-bit fields, byte size 1-8"
// integer arithmetic what it is (Reference Manual 22-6530-2, "Field
// Definition", p.~89, and Figure 6 "INTEGER" row, p.18).
//
// SOURCE for the read/write convention: "the desired field is
// extracted, starting with the right end of the field. Processing is
// done from right to left, even though the bit address in the
// instruction specifies the leftmost bit of the field." (p.~89) A field
// of length L starting at bit address (word, offset) occupies IBM bits
// [offset, offset+L) of the word, continuing into the next word when
// offset+L > 64 ("The storage word or word pair which contains the
// addressed memory field is brought from storage...", same page).
//
// SCOPE NOTE: field length is fully general (1-64, 0 meaning 64, per
// p.~89 "A length field of zero in an instruction specifies a 64-bit
// storage field"). Byte size (BS, 3 bits) determines where the sign
// byte boundary falls for signed fields; this implementation could not
// locate an explicit BS-code table in the manual, so it uses the same
// "0 means max" convention the LENGTH field uses elsewhere in the
// architecture: BS value 0 means byte size 8, values 1-7 mean that many
// bits. This is a documented simplification -- see bsv/README.md
// "Scope" -- not a transcription of a confirmed table.
//
// Field *reads* are no longer performed here: StretchStorage's general
// storage is BRAM-backed (docs/phase2_arm_inventory.md step 9), so a
// read genuinely spans a clock cycle and StretchExecute.bsv's own
// prefetch/bail-out mechanism owns the whole read side, calling only
// the pure bit-extraction logic below (`extractFieldBits`) once a word
// is on hand. Field *writes* stay here, still `Action` (they call the
// single-cycle `writeWord` method, which never needed staging).

package StretchVFL;

import StretchTypes::*;
import StretchStorage::*;

function Bit#(7) effLength(Bit#(6) length) =
  (length == 0) ? 64 : zeroExtend(length);

function Bit#(4) effByteSize(Bit#(3) bs) =
  (bs == 0) ? 8 : zeroExtend(bs);

// Whether a field would span two words. writeField below can only issue
// one call to the underlying single-write-port storage per invocation
// (see bsv/README.md "Toolchain"/"Scope": RegFile -- even the "WCF"
// variant -- disallows two upd() calls from the same rule; the WCF
// name refers to read/write conflict-freedom, not write/write), so a
// crossing STORE is out of scope; callers must check this first and
// treat true as OP-invalid rather than calling writeField.
function Bool fieldCrosses(BitAddr ba, Bit#(7) len_);
  Bit#(8) off8 = zeroExtend(baBit(ba));
  Bit#(8) len8 = zeroExtend(len_);
  return (off8 + len8 > 64);
endfunction

// Pure bit-manipulation core shared by readField/writeField below and
// by readFieldWithHi/writeFieldWithHi further down -- factored out so
// the "already have the word(s), just need the bits" case (the latter
// pair) and the "need to fetch first" case (the former pair) can't
// drift apart into two independently-maintained copies of the same
// shift/mask arithmetic.
function Bit#(64) extractFieldBits(Word64 hi, Word64 lo, Bit#(6) off, Bit#(7) len_);
  Bit#(8) off8 = zeroExtend(off);
  Bit#(8) len8 = zeroExtend(len_);
  Bit#(128) combined = {hi, lo};
  Bit#(128) mask64 = (len_ == 64) ? '1 : ((1 << len8) - 1);
  Bit#(8) shiftAmt = 128 - off8 - len8;
  Bit#(128) shifted = combined >> shiftAmt;
  return truncate(shifted) & truncate(mask64);
endfunction

function Word64 insertFieldBits(Word64 hi, Bit#(6) off, Bit#(7) len_, Bit#(64) val);
  Bit#(8) off8 = zeroExtend(off);
  Bit#(8) len8 = zeroExtend(len_);
  Bit#(64) mask64 = (len_ == 64) ? '1 : ((1 << len8) - 1);
  Bit#(8) shiftAmt = 64 - off8 - len8;
  Bit#(64) fieldMask = mask64 << shiftAmt;
  Bit#(64) fieldVal  = (val & mask64) << shiftAmt;
  return (hi & ~fieldMask) | fieldVal;
endfunction

// The same insertion for a field that STRADDLES two storage words --
// the write-side counterpart of extractFieldBits' two-word read, and
// built the same way, by doing the arithmetic in 128 bits and cutting
// it in half at the end so the two halves cannot disagree about where
// the field is.
//
// `hi` and `lo` are the words at the field's word address and the one
// after it; the result is the new pair.  A caller that has only `hi`
// must not use this -- fieldCrosses() is the test.
//
// WHY IT EXISTS.  MCP printed p.43 line 49 stores 6-bit characters
// progressively ("ST(V+I)(BU,6,6),.6($5)"), and character ten of a
// card lands at bits 60-65 of the output word.  Until 2026-10-24 the
// ST arm refused that store outright, which left IBM's own card
// converter producing ten characters out of eighty -- see
// tests/gen_mcp_boot_tb.py's mcp_ucbf1_* checks.
function Tuple2#(Word64, Word64)
    insertFieldBitsPair(Word64 hi, Word64 lo, Bit#(6) off, Bit#(7) len_,
                        Bit#(64) val);
  Bit#(8) off8 = zeroExtend(off);
  Bit#(8) len8 = zeroExtend(len_);
  Bit#(128) mask64 = (len_ == 64) ? 128'h0000000000000000FFFFFFFFFFFFFFFF
                                  : ((1 << len8) - 1);
  Bit#(8) shiftAmt = 128 - off8 - len8;
  Bit#(128) fieldMask = mask64 << shiftAmt;
  Bit#(128) fieldVal  = (zeroExtend(val) & mask64) << shiftAmt;
  Bit#(128) combined  = ({hi, lo} & ~fieldMask) | fieldVal;
  return tuple2(combined[127:64], combined[63:0]);
endfunction

// readField/readFieldWithHi/writeField (the internal-read variants of
// this section) were removed once every caller had migrated to the
// prefetch/bail-out mechanism in StretchExecute.bsv's execute() --
// see docs/phase2_arm_inventory.md step 9 and git history (this
// package's own log, commit removing them) for what they looked like
// and why they became dead code. extractFieldBits/insertFieldBits
// above (the pure logic they were built on) and writeFieldWithHi
// below remain live.

// Write a field back into a word the caller already has on hand (via
// StretchExecute.bsv's own prefetch mechanism) -- no internal read.
// Precondition: `hi` is the word most recently read at `ba`'s word
// address (non-crossing -- the caller must have already confirmed
// this, same as the removed writeField's own precondition), and
// nothing else has written that word in between.
function Action writeFieldWithHi(StretchStorage st, BitAddr ba, Bit#(7) len_, Bit#(64) val, Word64 hi) =
  action
    WordAddr w0 = baWord(ba);
    Bit#(6)  off = baBit(ba);
    st.writeWord(w0, insertFieldBits(hi, off, len_, val));
  endaction;

// ---------------------------------------------------------------------
// CONNECTIVE BYTE-SIZE CONVERSION -- Reference Manual printed p.75
// ---------------------------------------------------------------------
// The connectives do NOT work on a flat bit field the way the integer
// arithmetic operations do.  p.75, under the heading "Byte Size", in
// its own words:
//
//   "The connective operations process data in eight-bit bytes.  In
//   these operations, the byte size specified in the instruction
//   designates the number of bits used to represent each character or
//   symbol in the storage field.  **If the byte size of the storage
//   operand is less than eight, each byte is converted into an
//   eight-bit byte before processing by the addition of high-order
//   zeros.**  The accumulator operand is assumed to have a byte size
//   of eight.  Any offset may be specified and the field is processed
//   in eight-bit bytes starting with the offset.  Each byte of the
//   storage field, after conversion to eight-bit form if necessary,
//   is combined with an eight-bit byte from the accumulator according
//   to the specified connective.  **Consequently, the result bytes
//   always have a byte size of eight.**"
//
// and, on the facing column of the same page:
//
//   "In contrast to the integer arithmetic operations, the
//   accumulator operand has a definite length; it is composed of as
//   many bytes as there are in the addressed storage field."
//
// SO A 21-BIT FIELD AT BYTE SIZE 3 IS SEVEN BYTES AND FIFTY-SIX BITS
// OF ACCUMULATOR, not twenty-one.  That is the whole point of MCP's
// printed p.5 line 12, "LF(BU,21,3),X ERR AD,1", whose own comment is
// "-BREAK ADDRESS INTO EIGHT BIT BYTES": it spreads seven octal
// digits of an address into seven character positions so that two
// later adds can turn them into IQS digits without carrying between
// them.
//
// THE SHORT LAST BYTE IS THE ONE EXCEPTION, and p.75 states it
// separately:
//
//   "Since the field lengths of the storage operand need not be a
//   multiple of the byte size, the last byte need not be of full
//   size.  When this is the case, only those bits of the high-order
//   accumulator and storage bytes that are included in the field
//   length take part in the processing.  No high-order zeros are
//   added to the short byte from storage.  However, if the field
//   length is a multiple of the byte size, and if the byte size is
//   less than eight, high-order zeros are added to the high-order
//   byte as well as to all other bytes so that all bytes of the field
//   are treated in the same manner."
//
// **WHICH IS WHY BYTE SIZE EIGHT COMES OUT BIT-IDENTICAL TO THE FLAT
// FIELD THIS MODEL USED BEFORE.**  At bs=8 every full byte masks to
// 0xFF and the short last byte masks to exactly the bits inside the
// field length, so the participation mask below is the low `len_`
// bits -- the old `fieldMask`, unchanged.  Every connective test in
// the suite uses bs=8, and that is why none of them move.
//
// Sixteen bytes is the limit here because the accumulator is 128 bits
// and p.76's PARTIAL FIELD indicator covers a storage field that runs
// off its left end.  PF is not implemented (neither was it before);
// a field with more than sixteen bytes is silently truncated.
//
// Returns (expanded value, participation mask, byte count).
function Tuple3#(Bit#(128), Bit#(128), Bit#(7))
         connExpand(Bit#(64) raw, Bit#(7) len_, Bit#(4) bsEff);
  Bit#(128) val  = 0;
  Bit#(128) mask = 0;
  Bit#(7)   nb   = 0;
  for (Integer k = 0; k < 16; k = k + 1) begin
    Bit#(7) lo = fromInteger(k) * zeroExtend(bsEff);
    if (lo < len_) begin
      Bit#(7) rem = len_ - lo;
      Bit#(4) w   = (rem >= zeroExtend(bsEff)) ? bsEff : truncate(rem);
      // A FULL byte contributes all eight result bits (high-order
      // zeros are added to the storage side); a SHORT byte -- only
      // ever the high-order one -- contributes just its own bits.
      // TWO DIFFERENT MASKS, and they look alike on purpose but are
      // not the same question.  `bmask` is how many RESULT bits take
      // part -- all eight of a full byte, however narrow the storage
      // byte was, because the storage side was zero-extended; only
      // the in-field bits of a short high-order byte.  `b` is how
      // many bits the STORAGE side actually supplies, which is `w`
      // whether the byte is full or short.  They differ exactly when
      // bsEff < 8 and the byte is full: eight result bits from a
      // three-bit datum, which IS the expansion.
      Bit#(8) bmask = (w == bsEff) ? 8'hFF : ((8'b1 << w) - 1);
      Bit#(8) wmask = (w == 8) ? 8'hFF : ((8'b1 << w) - 1);
      Bit#(8) b     = truncate(raw >> lo) & wmask;
      val  = val  | (zeroExtend(b)     << (8 * k));
      mask = mask | (zeroExtend(bmask) << (8 * k));
      nb   = fromInteger(k) + 1;
    end
  end
  return tuple3(val, mask, nb);
endfunction

// The reverse, for CONNECT TO MEMORY.  p.75: "the result byte is
// truncated before being placed in storage if the byte size of the
// storage field is less than eight.  Each byte in the storage field
// is replaced by the number of bits specified by the byte size.
// These bits are the low-order bits of each result byte; the
// remaining high-order bits of each result byte are dropped.  No
// indication is given if the bits which are dropped are significant."
function Bit#(64) connContract(Bit#(128) v, Bit#(7) len_, Bit#(4) bsEff);
  Bit#(64) out = 0;
  for (Integer k = 0; k < 16; k = k + 1) begin
    Bit#(7) lo = fromInteger(k) * zeroExtend(bsEff);
    if (lo < len_) begin
      Bit#(7) rem = len_ - lo;
      Bit#(4) w   = (rem >= zeroExtend(bsEff)) ? bsEff : truncate(rem);
      Bit#(8) wmask = (w == 8) ? 8'hFF : ((8'b1 << w) - 1);
      Bit#(8) b   = truncate(v >> (8 * k)) & wmask;
      out = out | (zeroExtend(b) << lo);
    end
  end
  return out;
endfunction

endpackage
