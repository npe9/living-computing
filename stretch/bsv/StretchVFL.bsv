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

endpackage
