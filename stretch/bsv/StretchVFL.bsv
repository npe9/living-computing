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
// `readWord` on StretchStorage is a combinational (non-Action) method,
// so field *reads* here are plain functions; only field *writes* need
// to be Action (they call the registered-write `writeWord` method).

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

// Read an L-bit field (1-64) whose leftmost bit is at `ba`. ActionValue
// purely because `st.readWord` now is one (StretchStorage.bsv) -- the
// crossing case's two reads are of two INDEPENDENT, both-known-upfront
// addresses (w0 and w0+1), not one computed from the other's result,
// so this stays a simple two-bind sequence rather than needing a
// general dependent-read FSM (see bsv/README.md "Next steps" item 6
// for why that distinction is what makes the whole storage migration
// tractable at all).
function ActionValue#(Bit#(64)) readField(StretchStorage st, BitAddr ba, Bit#(7) len_) =
  actionvalue
    WordAddr w0 = baWord(ba);
    Bit#(6)  off = baBit(ba);
    Bit#(8) off8 = zeroExtend(off);
    Bit#(8) len8 = zeroExtend(len_);
    Bool crosses = (off8 + len8 > 64);
    Word64 hi <- st.readWord(w0);
    Word64 lo = 64'b0;
    if (crosses) begin
      let l <- st.readWord(w0 + 1);
      lo = l;
    end
    return extractFieldBits(hi, lo, off, len_);
  endactionvalue;

// Read a field AND return the raw containing word (`hi`) alongside it,
// for a caller that already knows it will turn around and write the
// SAME word back (M+, CM -- see their call sites in
// StretchExecute.bsv). Both guarantee non-crossing before calling this
// (fieldCrosses is checked first, same precondition writeField
// already has), so there is no `lo` half to carry. Pairs with
// writeFieldWithHi below to avoid the redundant re-read that a plain
// readField-then-writeField sequence would otherwise do -- both calls
// would fetch the exact same word, since the field doesn't cross and
// the address hasn't changed between them.
function ActionValue#(Tuple2#(Bit#(64), Word64)) readFieldWithHi(StretchStorage st, BitAddr ba, Bit#(7) len_) =
  actionvalue
    WordAddr w0 = baWord(ba);
    Bit#(6)  off = baBit(ba);
    Word64 hi <- st.readWord(w0);
    Bit#(64) val = extractFieldBits(hi, 0, off, len_);
    return tuple2(val, hi);
  endactionvalue;

// Write an L-bit field (1-64), leaving surrounding bits in the
// containing word untouched ("Data to the right or left of the
// specified field in storage are never affected.", p.~89).
//
// PRECONDITION: !fieldCrosses(ba, len_) -- i.e. the field must fit
// within a single word. This function issues exactly one
// `st.writeWord` call so it composes safely with the rest of a rule
// (see fieldCrosses above for why); callers are responsible for
// checking first and handling the crossing case themselves (in
// practice: OP invalid, see StretchExecute.bsv).
function Action writeField(StretchStorage st, BitAddr ba, Bit#(7) len_, Bit#(64) val) =
  action
    WordAddr w0 = baWord(ba);
    Bit#(6)  off = baBit(ba);
    Word64 hi <- st.readWord(w0);
    st.writeWord(w0, insertFieldBits(hi, off, len_, val));
  endaction;

// Write a field back into a word the caller already fetched (via
// readFieldWithHi) -- skips the internal read writeField would
// otherwise redundantly perform on the exact same word. See
// readFieldWithHi's comment for the precondition (non-crossing,
// same `ba`/`len_` as the paired read, nothing else wrote that word
// in between).
function Action writeFieldWithHi(StretchStorage st, BitAddr ba, Bit#(7) len_, Bit#(64) val, Word64 hi) =
  action
    WordAddr w0 = baWord(ba);
    Bit#(6)  off = baBit(ba);
    st.writeWord(w0, insertFieldBits(hi, off, len_, val));
  endaction;

endpackage
