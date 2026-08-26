// StretchExecute.bsv
//
// Execute stage. Implements the subset of the IBM 7030 instruction set
// documented as in-scope in bsv/README.md: VFL binary integer L/ST/+/M+/K
// (Reference Manual 22-6530-2 pp.~86-95) with both standard address
// modification and progressive indexing (P in {1,2,3,5,6,7}, p.21),
// the sixteen Connectives (C/CM/CT, p.75-77, byte-size-8 only -- see
// that case's own scope note), direct and immediate index arithmetic
// (pp.22-27), count-and-branch and branch-on-indicator (pp.~26-27,
// pocket card X22-6533-1 "INDEX BRANCHING"/"INDICATOR BRANCHING"),
// unconditional branching, Store Zero / Refill, and direct
// (non-backward, single-word) Transmit.
//
// Every other decoded format/opcode -- decimal arithmetic, floating
// point arithmetic beyond L/ST, radix conversion, input-output,
// interrupts, bit branching, SIC, EX/EXIC, RNX/LVE/SVA, LVS, Transmit
// backward/swap -- sets indicator 15 (OP, Operation Code Invalid) and
// otherwise acts as a no-op, matching the documented real-machine
// behavior for an invalid/suppressed instruction (Reference Card,
// indicator class "S": "execution of instruction is suppressed"). See
// bsv/README.md "Scope" for the full accounting and citations.
//
// INDICATORS ARE WRITTEN EXACTLY ONCE PER INSTRUCTION. A plain
// register (which is what `indicators` is, see StretchStorage.bsv)
// accepts only one `<=` per rule; an instruction that changes several
// bits (e.g. RLZ/RZ/RGZ/RN together) cannot get there by calling a
// per-bit Action several times. So indicator updates here are pure
// functions Word64 -> Word64 threaded through a single local `ind`
// variable across the whole `case`, written back once via
// `st.setIndicatorBits(ind)` after it. See bsv/README.md "Toolchain"
// for how this was diagnosed (also the reason Transmit moves only one
// word, and VFL stores that would cross a word boundary are OP
// invalid: the underlying RegFile likewise accepts only one write per
// rule).

package StretchExecute;

import Vector::*;
import StretchTypes::*;
import StretchStorage::*;
import StretchIO::*;
import StretchVFL::*;
import StretchALU::*;

// ---------------------------------------------------------------------
// Address-modification helpers (p.20-21 "Address Modification"): add
// the (signed) value field of index register `idx` to the instruction's
// raw address field; idx==0 means no modification. The carry out of the
// top bit is ignored ("this overflow bit... is ignored", p.21), which
// Bit#(n) wraparound gives for free.
// ---------------------------------------------------------------------

function BitAddr effAddr24(StretchStorage st, BitAddr raw, Bit#(4) idx);
  if (idx == 0)
    return raw;
  else begin
    IndexWord x = st.readIndex(idx);
    return (x.sign == 1) ? (raw - x.addr) : (raw + x.addr);
  end
endfunction

function HWordAddr effAddr19(StretchStorage st, HWordAddr raw, Bit#(4) idx);
  if (idx == 0)
    return raw;
  else begin
    IndexWord x = st.readIndex(idx);
    Bit#(19) m = truncate(x.addr);
    return (x.sign == 1) ? (raw - m) : (raw + m);
  end
endfunction

function WordAddr effAddr18(StretchStorage st, WordAddr raw, Bit#(4) idx);
  if (idx == 0)
    return raw;
  else begin
    IndexWord x = st.readIndex(idx);
    Bit#(18) m = truncate(x.addr);
    return (x.sign == 1) ? (raw - m) : (raw + m);
  end
endfunction

// Half-word-granular memory access built on the word-addressed store,
// used by Direct Index Arithmetic's LV/LC/LR/SV/SC/SR (p.22-23: "bits
// 0-18 of the effective address" identify a half-word).
function ActionValue#(Bit#(32)) readHW(StretchStorage st, HWordAddr ha) =
  actionvalue
    Word64 w <- st.readWord(ha[18:1]);
    return (ha[0] == 0) ? w[63:32] : w[31:0];
  endactionvalue;

// Read a half-word AND return the raw containing word alongside it,
// for a caller (SV/SC/SR -- see their call sites below) that already
// knows it will turn around and write the SAME word back via
// writeHWWithWord. Mirrors readFieldWithHi/writeFieldWithHi in
// StretchVFL.bsv (same redundant-re-read shape, same fix): a plain
// readHW-then-writeHW sequence would fetch the identical word twice,
// since the address doesn't change between the two calls.
function ActionValue#(Tuple2#(Bit#(32), Word64)) readHWWithWord(StretchStorage st, HWordAddr ha) =
  actionvalue
    Word64 w <- st.readWord(ha[18:1]);
    Bit#(32) half = (ha[0] == 0) ? w[63:32] : w[31:0];
    return tuple2(half, w);
  endactionvalue;

function Action writeHW(StretchStorage st, HWordAddr ha, Bit#(32) v) =
  action
    WordAddr wa = ha[18:1];
    Word64 w <- st.readWord(wa);
    Word64 neww = (ha[0] == 0) ? {v, w[31:0]} : {w[63:32], v};
    st.writeWord(wa, neww);
  endaction;

// Write a half-word back into a word the caller already fetched (via
// readHWWithWord) -- skips the internal read writeHW would otherwise
// redundantly perform on the exact same word. Precondition: `w` is
// the word most recently read at `ha`'s word address, and nothing
// else wrote that word in between (same precondition writeFieldWithHi
// has for its own `hi` parameter).
function Action writeHWWithWord(StretchStorage st, HWordAddr ha, Bit#(32) v, Word64 w) =
  action
    WordAddr wa = ha[18:1];
    Word64 neww = (ha[0] == 0) ? {v, w[31:0]} : {w[63:32], v};
    st.writeWord(wa, neww);
  endaction;

// ---------------------------------------------------------------------
// Accumulator as a 128-bit sign-magnitude value (see StretchALU.bsv
// header for the documented simplification).
// ---------------------------------------------------------------------

// Plain function again, not ActionValue: addrAccLeft/addrAccRight are
// compile-time constants, always Reg-backed (StretchStorage.bsv's
// dedicated readAccLeft/readAccRight accessors), so there's no
// request/response round trip to wait on here -- see
// docs/phase2_arm_inventory.md.
function SM128 readAcc(StretchStorage st) = accToSM(st.readAccLeft(), st.readAccRight());

function Action writeAcc(StretchStorage st, SM128 v) =
  action
    let {hi,lo} = packAcc(v.sign, truncate(v.mag));
    st.writeWord(addrAccLeft, hi);
    st.writeWord(addrAccRight, lo);
  endaction;

// ---------------------------------------------------------------------
// Pure indicator-bit helpers (see file header for why these are pure
// functions on Word64 rather than Actions).
// ---------------------------------------------------------------------

function Word64 setBit(Word64 w, Bit#(6) n, Bit#(1) v);
  Bit#(7) sh = 63 - zeroExtend(n);
  Word64 mask = (64'b1 << sh);
  return (v == 1) ? (w | mask) : (w & ~mask);
endfunction

function Word64 setOpInvalid(Word64 ind) = setBit(ind, ind_OP, 1);

function Word64 setResultIndicatorsF(Word64 ind, SM128 v);
  Bool z = (v.mag == 0);
  Word64 i1 = setBit(ind, ind_RLZ, pack(v.sign == 1 && !z));
  Word64 i2 = setBit(i1,  ind_RZ,  pack(z));
  Word64 i3 = setBit(i2,  ind_RGZ, pack(v.sign == 0 && !z));
  Word64 i4 = setBit(i3,  ind_RN,  pack(v.sign == 1 && !z));
  return i4;
endfunction

function Word64 setAccCmpIndicatorsF(Word64 ind, Cmp3 c);
  Word64 i1 = setBit(ind, ind_AL, pack(c == CmpLow));
  Word64 i2 = setBit(i1,  ind_AE, pack(c == CmpEqual));
  Word64 i3 = setBit(i2,  ind_AH, pack(c == CmpHigh));
  return i3;
endfunction

function Word64 setIndexResultIndicatorsF(Word64 ind, IndexWord x);
  Bool z = (x.addr == 0);
  Word64 i1 = setBit(ind, ind_XF,   x.flag);
  Word64 i2 = setBit(i1,  ind_XCZ,  pack(x.count == 0));
  Word64 i3 = setBit(i2,  ind_XVLZ, pack(x.sign == 1 && !z));
  Word64 i4 = setBit(i3,  ind_XVZ,  pack(z));
  Word64 i5 = setBit(i4,  ind_XVGZ, pack(x.sign == 0 && !z));
  return i5;
endfunction

function Word64 setIndexCmpIndicatorsF(Word64 ind, Cmp3 c);
  Word64 i1 = setBit(ind, ind_XL, pack(c == CmpLow));
  Word64 i2 = setBit(i1,  ind_XE, pack(c == CmpEqual));
  Word64 i3 = setBit(i2,  ind_XH, pack(c == CmpHigh));
  return i3;
endfunction

// Connectives (p.76 "Connectives", Figure 20): unlike RLZ/RZ/RGZ/RN for
// arithmetic results (setResultIndicatorsF), a connective's result has
// no sign -- it's a raw bit pattern, not a signed magnitude. p.77:
// "Result Greater than Zero (RGZ): turned on if the result field
// contains any one-bit. Result Less than Zero (RLZ); Result Negative
// (RN): turned off by the connective operations." Result Zero (RZ) is
// the complement of RGZ here (all-zero vs. any-one-bit); To-Memory
// Operation (MOP) is on for CONNECT TO MEMORY, off for CONNECT/CONNECT
// FOR TEST. The left-zeros/all-ones counts (word 7) this same section
// describes are NOT implemented -- see bsv/README.md "Scope".
function Word64 setConnectiveIndicatorsF(Word64 ind, Bool isMOP, Bool resultZero);
  Word64 i1 = setBit(ind, ind_MOP, pack(isMOP));
  Word64 i2 = setBit(i1,  ind_RLZ, 0);
  Word64 i3 = setBit(i2,  ind_RN,  0);
  Word64 i4 = setBit(i3,  ind_RGZ, pack(!resultZero));
  Word64 i5 = setBit(i4,  ind_RZ,  pack(resultZero));
  return i5;
endfunction

// The sixteen connectives (p.76 Figure 20): result bit i = f(m_i, a_i)
// where f is chosen by `conn`'s 4 bits, one per (m,a) combination --
// conn[3]=result for (m=0,a=0), conn[2]=(0,1), conn[1]=(1,0),
// conn[0]=(1,1) (matches Figure 20's own bit order exactly, e.g.
// conn=4'b0110 gives (notM&a)|(m&notA) = m XOR a = "m (+) a", listed
// there as connective 6). A minterm-sum over the whole word at once,
// relying on the caller (readField/the accumulator-field mask) to have
// already zeroed every bit outside the real field -- so bits beyond
// the field's length don't need separate masking here.
function Bit#(64) applyConnective(Bit#(4) conn, Bit#(64) m, Bit#(64) a);
  Bit#(64) notM = ~m;
  Bit#(64) notA = ~a;
  Bit#(64) r = 0;
  if (conn[3] == 1) r = r | (notM & notA);
  if (conn[2] == 1) r = r | (notM & a);
  if (conn[1] == 1) r = r | (m & notA);
  if (conn[0] == 1) r = r | (m & a);
  return r;
endfunction

// Immediate operand per p.~90 "Immediate Addressing": the instruction's
// 24-bit address field supplies the *leftmost* len_ bits of the
// operand, zero-filled on the right if len_ > 24.
function Bit#(64) immediateOperand(Bit#(24) addr, Bit#(7) len_);
  if (len_ <= 24) begin
    Bit#(7) sh = 24 - len_;
    return zeroExtend(addr >> sh);
  end else begin
    Bit#(7) sh = len_ - 24;
    Bit#(64) wide = zeroExtend(addr);
    return wide << sh;
  end
endfunction

// Conditional refill: p.22 "a new index word that can replace the
// original index word... conditional on the count's reaching zero".
function ActionValue#(IndexWord) maybeRefill(StretchStorage st, IndexWord x, Bool doRefill) =
  actionvalue
    if (doRefill && x.count == 0) begin
      Word64 w <- st.readWord(zeroExtend(x.refill));
      return unpackIndexWord(w);
    end else
      return x;
  endactionvalue;

// Progressive indexing's post-operation increment (Reference Manual
// p.21): add (P 1-3) or subtract (P 5-7) the instruction's address
// part -- reused here as a plain positive increment, not an address --
// into the SAME index register used as the effective address,
// optionally counting down (2/3, 6/7) and refilling on count zero (3,
// 7); indicators reflect the pre-refill state. ActionValue (not a
// plain function) purely because `st.readWord` (used for the refill
// case) now is one -- see StretchStorage.bsv's own interface comment
// -- returning the new index word rather than writing it: see the
// long comment at this function's one call site (in the VflInt case
// of `execute`, below) for why the actual `st.writeIndex` for
// progressive indexing happens in StretchCore.step instead of here.
function ActionValue#(Tuple2#(IndexWord, Word64)) progressiveIncrement(
    StretchStorage st, VflAddr a, IndexWord xIdx, Word64 indIn) =
  actionvalue
    SM128 val = SM128{sign: xIdx.sign, mag: zeroExtend(xIdx.addr)};
    Bool subtract = (a.p >= 5);
    SM128 inc = SM128{sign: (subtract ? 1 : 0), mag: zeroExtend(a.addr)};
    SM128 sum = smAdd(val, inc);
    IndexWord x1 = IndexWord{addr: truncate(sum.mag), sign: sum.sign,
                     flag: xIdx.flag, count: xIdx.count, refill: xIdx.refill};
    Bit#(3) pLow = a.p - (subtract ? 4 : 0); // 1/2/3, regardless of add/subtract
    if (pLow != 1) x1.count = x1.count - 1;
    IndexWord x2 = x1;
    if (pLow == 3 && x1.count == 0) begin
      Word64 w <- st.readWord(zeroExtend(x1.refill));
      x2 = unpackIndexWord(w);
    end
    return tuple2(x2, setIndexResultIndicatorsF(indIn, x1)); // pre-refill state, p.21
  endactionvalue;

// ---------------------------------------------------------------------
// Top-level execute: consumes one decoded instruction, performs its
// side effects on `st`, and returns the next instruction counter
// (half-word address). `pc` is the address of the instruction just
// fetched; `len` says whether it was one or two half-words.
// ---------------------------------------------------------------------

// Returns (next PC, an optional pending index-register write for
// progressive indexing, an optional started-but-not-yet-drained
// input-output word transfer, an optional BRAM-eligible read this
// call couldn't complete without). See the VflInt case below for why
// the index write is *returned* rather than performed here (and
// StretchCore.step for where it's actually realized); the IoOp case
// below explains the analogous reason for the transfer descriptor.
//
// `prefetch`/`prefetchCount`: the per-case-arm staging mechanism for
// the BRAM storage migration (docs/phase2_arm_inventory.md). An arm
// that needs a BRAM-eligible read checks `prefetchCount` FIRST, before
// doing anything else: if the value it needs isn't available yet, it
// sets the 4th return element (`needsRead`) to that address and does
// NOTHING further -- no writes, no `ind`/`next`/`doIdxWrite`/
// `vflPending`/`ioStart` mutation -- so the shared bail-out check at
// the very end of this function (right before the final commit) can
// safely return every output at its function-ENTRY value. This is
// what makes calling `execute()` more than once for the same
// instruction safe (unlike the rejected "call execute() twice"
// shortcut, which would have re-fired every write on a second call):
// the FIRST call, when it bails, performs literally zero side effects,
// so there's nothing to double-fire. `StretchCore.step()` drives this:
// call with `prefetchCount=0`; on `needsRead=Valid(a)`, issue
// `st.readWordReq(a)`, park (remembering `pc`/`len`/`di`), and on the
// next call pass a `prefetch` with one more slot filled and
// `prefetchCount` incremented. Bound at 2 slots -- the confirmed
// worst case for any arm converted so far (a crossing field's `w0`/
// `w0+1`, or one field read plus one progressive-indexing refill read)
// -- NOT a general bound for every arm this project might ever
// convert; a THIRD simultaneous read (e.g. a crossing field combined
// with a refill in the SAME arm) is a known, not-yet-encountered gap,
// flagged here rather than silently mishandled should it arise.
function ActionValue#(Tuple4#(HWordAddr, Maybe#(Tuple2#(Bit#(4), IndexWord)),
                               Maybe#(IoXfer), Maybe#(WordAddr)))
    execute(StretchStorage st, StretchIO io, HWordAddr pc, InstrLen len, DecodedInstr di,
            Vector#(2, Word64) prefetch, Bit#(2) prefetchCount) =
  actionvalue
    Maybe#(WordAddr) needsRead = tagged Invalid;
    HWordAddr fallthrough = pc + ((len == Full) ? 2 : 1);
    HWordAddr next = fallthrough;
    Word64 ind = st.readIndicators();

    // INDEX-REGISTER WRITES ARE DEFERRED TO ONE CALL, EXACTLY LIKE
    // INDICATORS ABOVE, for every format EXCEPT VflInt's progressive
    // indexing (see that case's own comment for why it's different):
    // every other arm below that used to call `st.writeIndex(...)`
    // directly now instead sets this local variable, and the single
    // real write happens once, at the very bottom of this function --
    // free, by the same reasoning as `ind`'s single `setIndicatorBits`
    // call, since it's plain local-variable assignment across many
    // mutually-exclusive arms, not a method call site.
    Bool doIdxWrite = False;
    Bit#(4) idxWriteReg = 0;
    IndexWord idxWriteVal = IndexWord{addr:0, sign:0, flag:0, count:0, refill:0};
    Maybe#(Tuple2#(Bit#(4), IndexWord)) vflPending = tagged Invalid;

    // A started RD/W transfer, similarly threaded out rather than
    // performed inline: a block can be many words, and this function
    // (like every other execute() arm) may only call st.writeWord (or,
    // for a WRITE, io.writePrinterWord) once per invocation -- see the
    // IoOp case below.
    Maybe#(IoXfer) ioStart = tagged Invalid;

    case (di) matches

      // -----------------------------------------------------------
      // VFL integer arithmetic (binary mode only; decimal is out of
      // scope, see file header). P in {0,4} is standard address
      // modification (direct/immediate); P in {1,2,3,5,6,7} is
      // progressive indexing (Reference Manual p.21 "Progressive
      // Indexing"): the effective address is the index register's own
      // value field directly (no addition of the instruction's
      // address part), and *afterward* the instruction's address
      // part -- reused as a plain positive increment, not an address
      // -- is added (P 1-3) or subtracted (P 5-7) into that same
      // index register's value field, optionally counting down (2/3,
      // 6/7) and refilling on count zero (3, 7). "If progressive
      // indexing with index register X0 is specified, indicator OP
      // ... is set" (X0 is the fixed no-index sentinel, not a usable
      // register here).
      // -----------------------------------------------------------
      tagged VflInt .vi: begin
        Bool isProgressive = (vi.a.p != 0 && vi.a.p != 4);
        if (vi.m.decimal == 1)
          ind = setOpInvalid(ind);
        else if (isProgressive && vi.a.i1 == 0)
          ind = setOpInvalid(ind);
        else begin
          Bit#(7) len_ = effLength(vi.a.length);
          Bit#(4) bsz  = effByteSize(vi.a.bs);
          Bool immediate = (vi.a.p == 4);
          IndexWord xIdx = st.readIndex(vi.a.i1);
          BitAddr ea = isProgressive ? xIdx.addr : effAddr24(st, vi.a.addr, vi.a.i1);
          Bit#(8) offSh = zeroExtend(vi.a.offset);
          Bool vflOk = True; // p.21: a suppressed VFL op (ST/M+
                              // immediate-or-crossing) skips the
                              // progressive increment too.

          case (vi.code)
            6'b000101: begin // L (Load) -- first arm converted to the
              // prefetch/bail-out staging (docs/phase2_arm_inventory.md).
              // Every other arm below still calls readField/readHW/
              // maybeRefill directly (the OLD, still-synchronous
              // st.readWord path) -- unconverted, unaffected, working
              // exactly as before.
              Bit#(64) raw = 0;
              if (immediate) begin
                raw = immediateOperand(vi.a.addr, len_);
              end else begin
                WordAddr w0 = baWord(ea);
                Bit#(6) off = baBit(ea);
                if (!fieldCrosses(ea, len_)) begin
                  if (prefetchCount >= 1)
                    raw = extractFieldBits(prefetch[0], 0, off, len_);
                  else
                    needsRead = tagged Valid w0;
                end else begin
                  if (prefetchCount >= 2)
                    raw = extractFieldBits(prefetch[0], prefetch[1], off, len_);
                  else if (prefetchCount == 1)
                    needsRead = tagged Valid (w0 + 1);
                  else
                    needsRead = tagged Valid w0;
                end
              end
              if (!isValid(needsRead)) begin
                SM128 sm = fieldToSM(raw, len_, bsz, vi.m.unsign, vi.m.invert);
                SM128 shifted = SM128 { sign: sm.sign, mag: sm.mag << offSh };
                writeAcc(st, shifted);
                ind = setResultIndicatorsF(ind, shifted);
              end
            end
            6'b001101: begin // ST (Store)
              if (immediate || fieldCrosses(ea, len_)) begin
                ind = setOpInvalid(ind);
                vflOk = False;
              end else begin
                SM128 acc = readAcc(st);
                SM128 shifted = SM128 { sign: acc.sign, mag: acc.mag >> offSh };
                Bit#(1) fsign = (vi.m.invert == 1) ? ~shifted.sign : shifted.sign;
                Bit#(64) packedField = smToField(SM128{sign:fsign, mag:shifted.mag}, len_, bsz, vi.m.unsign);
                writeField(st, ea, len_, packedField);
              end
            end
            6'b000001: begin // + (Add; "-" is this opcode with invert=1)
              // Same prefetch/bail-out shape as L above.
              Bit#(64) raw = 0;
              if (immediate) begin
                raw = immediateOperand(vi.a.addr, len_);
              end else begin
                WordAddr w0 = baWord(ea);
                Bit#(6) off = baBit(ea);
                if (!fieldCrosses(ea, len_)) begin
                  if (prefetchCount >= 1)
                    raw = extractFieldBits(prefetch[0], 0, off, len_);
                  else
                    needsRead = tagged Valid w0;
                end else begin
                  if (prefetchCount >= 2)
                    raw = extractFieldBits(prefetch[0], prefetch[1], off, len_);
                  else if (prefetchCount == 1)
                    needsRead = tagged Valid (w0 + 1);
                  else
                    needsRead = tagged Valid w0;
                end
              end
              if (!isValid(needsRead)) begin
                SM128 opnd = fieldToSM(raw, len_, bsz, vi.m.unsign, vi.m.invert);
                SM128 opndSh = SM128 { sign: opnd.sign, mag: opnd.mag << offSh };
                SM128 acc = readAcc(st);
                SM128 sum = smAdd(acc, opndSh);
                writeAcc(st, sum);
                ind = setResultIndicatorsF(ind, sum);
              end
            end
            6'b001001: begin // M+ (Add to Memory)
              if (immediate || fieldCrosses(ea, len_)) begin
                ind = setOpInvalid(ind);
                vflOk = False;
              end else begin
                let {raw, hiWord} <- readFieldWithHi(st, ea, len_);
                SM128 opnd = fieldToSM(raw, len_, bsz, vi.m.unsign, vi.m.invert);
                SM128 acc = readAcc(st);
                SM128 accSh = SM128 { sign: acc.sign, mag: acc.mag >> offSh };
                SM128 sum = smAdd(opnd, accSh);
                writeFieldWithHi(st, ea, len_, smToField(sum, len_, bsz, vi.m.unsign), hiWord);
                ind = setResultIndicatorsF(ind, sum);
              end
            end
            6'b010001: begin // K (Compare) -> AL/AE/AH -- same
              // prefetch/bail-out shape as L above.
              Bit#(64) raw = 0;
              if (immediate) begin
                raw = immediateOperand(vi.a.addr, len_);
              end else begin
                WordAddr w0 = baWord(ea);
                Bit#(6) off = baBit(ea);
                if (!fieldCrosses(ea, len_)) begin
                  if (prefetchCount >= 1)
                    raw = extractFieldBits(prefetch[0], 0, off, len_);
                  else
                    needsRead = tagged Valid w0;
                end else begin
                  if (prefetchCount >= 2)
                    raw = extractFieldBits(prefetch[0], prefetch[1], off, len_);
                  else if (prefetchCount == 1)
                    needsRead = tagged Valid (w0 + 1);
                  else
                    needsRead = tagged Valid w0;
                end
              end
              if (!isValid(needsRead)) begin
                SM128 opnd = fieldToSM(raw, len_, bsz, vi.m.unsign, vi.m.invert);
                SM128 opndSh = SM128 { sign: opnd.sign, mag: opnd.mag << offSh };
                SM128 acc = readAcc(st);
                Cmp3 c = smCompare(acc, opndSh);
                ind = setAccCmpIndicatorsF(ind, c);
              end
            end
            default: begin
              ind = setOpInvalid(ind);
              vflOk = False;
            end
          endcase

          // The progressive-index write-back is threaded out to a
          // SEPARATE return channel (`vflPending`, realized as a real
          // `st.writeIndex` call by the CALLER, StretchCore.step) --
          // not folded into this function's own `doIdxWrite` (used by
          // every other format below). Reason: L/ST/+/M+ each already
          // call `st.writeWord` (via writeAcc/writeField) from inside
          // this same `case (vi.code)`; once two or more of those
          // arms ALSO conditionally call `st.writeIndex` (even via the
          // shared `doIdxWrite` local), bsc's scheduler reports
          // spurious G0004 write/write conflicts between arms that
          // are mutually exclusive by construction. No other format
          // in this file has an arm that both writes general storage
          // and writes an index register, so this is the first place
          // that combination arises -- isolating the index write into
          // a value returned from (rather than performed inside) this
          // function was the fix that survived bisection (see the
          // exploratory diagnosis in git history / session notes: the
          // same code, with the write left inside this function,
          // reproduced the conflict even reduced to just two
          // memory-writing VflInt arms with all other sites removed).
          // Guarded on needsRead too, not just isProgressive/vflOk:
          // if the arm above bailed out waiting on a BRAM-eligible
          // read (currently only L can), this must NOT run -- it
          // would set vflPending and mutate ind despite the
          // instruction not actually having completed, breaking the
          // bail-out contract (see execute()'s own header comment:
          // nothing after a bail may touch the shared outputs).
          if (!isValid(needsRead) && isProgressive && vflOk) begin
            let {x2, ind2} <- progressiveIncrement(st, vi.a, xIdx, ind);
            vflPending = tagged Valid tuple2(vi.a.i1, x2);
            ind = ind2;
          end
        end
      end

      // -----------------------------------------------------------
      // Direct index arithmetic (p.22-23).
      // -----------------------------------------------------------
      tagged DirIndex .di_: begin
        HWordAddr ea = effAddr19(st, di_.addr, di_.idx);
        IndexWord x = st.readIndex(di_.j);
        case (di_.code)
          5'b00001: begin // LX -- prefetch/bail-out shape (same as
            // VflInt L/K/+ above). Half-word reads never cross a word
            // boundary (a half-word always fits within the one word
            // it addresses), so this and every other DirIndex
            // read-only arm below needs exactly 0-1 reads, never 2.
            if (prefetchCount >= 1) begin
              idxWriteReg = di_.j; doIdxWrite = True;
              idxWriteVal = unpackIndexWord(prefetch[0]);
            end else
              needsRead = tagged Valid ea[18:1];
          end
          5'b10001: st.writeWord(ea[18:1], packIndexWord(x));                     // SX
          5'b00011: begin // LV
            if (prefetchCount >= 1) begin
              Bit#(32) h = (ea[0] == 0) ? prefetch[0][63:32] : prefetch[0][31:0];
              idxWriteReg = di_.j; doIdxWrite = True;
              idxWriteVal = IndexWord{addr:h[31:8], sign:h[7:7], flag:x.flag,
                                              count:x.count, refill:x.refill};
            end else
              needsRead = tagged Valid ea[18:1];
          end
          5'b10011: begin // SV
            let {h, hWord} <- readHWWithWord(st, ea);
            writeHWWithWord(st, ea, {x.addr, x.sign, h[6:0]}, hWord);
          end
          5'b00101: begin // LC
            if (prefetchCount >= 1) begin
              Bit#(32) h = (ea[0] == 0) ? prefetch[0][63:32] : prefetch[0][31:0];
              idxWriteReg = di_.j; doIdxWrite = True;
              idxWriteVal = IndexWord{addr:x.addr, sign:x.sign, flag:x.flag,
                                              count:h[31:14], refill:x.refill};
            end else
              needsRead = tagged Valid ea[18:1];
          end
          5'b10101: begin // SC
            let {h, hWord} <- readHWWithWord(st, ea);
            writeHWWithWord(st, ea, {x.count, 7'b0, h[6:0]}, hWord);
          end
          5'b00111: begin // LR
            if (prefetchCount >= 1) begin
              Bit#(32) h = (ea[0] == 0) ? prefetch[0][63:32] : prefetch[0][31:0];
              idxWriteReg = di_.j; doIdxWrite = True;
              idxWriteVal = IndexWord{addr:x.addr, sign:x.sign, flag:x.flag,
                                              count:x.count, refill:h[31:14]};
            end else
              needsRead = tagged Valid ea[18:1];
          end
          5'b10111: begin // SR
            let {h, hWord} <- readHWWithWord(st, ea);
            writeHWWithWord(st, ea, {x.refill, 7'b0, h[6:0]}, hWord);
          end
          5'b01011, 5'b01101, 5'b01111: begin // V+ / V+C / V+CR
            Bit#(32) h <- readHW(st, ea);
            SM128 opnd = SM128{sign: h[7], mag: zeroExtend(h[31:8])};
            SM128 val  = SM128{sign: x.sign, mag: zeroExtend(x.addr)};
            SM128 sum  = smAdd(val, opnd);
            IndexWord x1 = IndexWord{addr: truncate(sum.mag), sign: sum.sign, flag: x.flag,
                                      count: x.count, refill: x.refill};
            if (di_.code != 5'b01011) x1.count = x1.count - 1;
            IndexWord x2 <- (di_.code == 5'b01111) ? maybeRefill(st, x1, True)
                                                    : actionvalue return x1; endactionvalue;
            idxWriteReg = di_.j; doIdxWrite = True;
            idxWriteVal = x2;
            ind = setIndexResultIndicatorsF(ind, x1); // reflects state before any refill, p.23
          end
          5'b01001: begin // KV
            if (prefetchCount >= 1) begin
              Bit#(32) h = (ea[0] == 0) ? prefetch[0][63:32] : prefetch[0][31:0];
              SM128 opnd = SM128{sign: h[7], mag: zeroExtend(h[31:8])};
              SM128 val  = SM128{sign: x.sign, mag: zeroExtend(x.addr)};
              ind = setIndexCmpIndicatorsF(ind, smCompare(val, opnd));
            end else
              needsRead = tagged Valid ea[18:1];
          end
          5'b11001: begin // KC
            if (prefetchCount >= 1) begin
              Bit#(32) h = (ea[0] == 0) ? prefetch[0][63:32] : prefetch[0][31:0];
              Cmp3 c = (x.count == h[31:14]) ? CmpEqual : (x.count < h[31:14]) ? CmpLow : CmpHigh;
              ind = setIndexCmpIndicatorsF(ind, c);
            end else
              needsRead = tagged Valid ea[18:1];
          end
          default: ind = setOpInvalid(ind); // RNX, LVE, SVA: out of scope
        endcase
      end

      // -----------------------------------------------------------
      // Immediate index arithmetic (pocket card "IMMEDIATE INDEX
      // ARITHMETIC"; semantics extrapolated from the direct forms
      // above plus the mnemonic table -- see bsv/README.md "Scope").
      // -----------------------------------------------------------
      tagged ImmIndex .ii: begin
        IndexWord x = st.readIndex(ii.j);
        Bit#(18) imm18 = truncate(ii.imm);
        SM128 immSM = SM128{sign: 0, mag: zeroExtend(ii.imm)};
        SM128 val = SM128{sign: x.sign, mag: zeroExtend(x.addr)};
        case (ii.code)
          4'b0001: begin // LVI
            idxWriteReg = ii.j; doIdxWrite = True;
            idxWriteVal = IndexWord{addr: zeroExtend(ii.imm), sign: 0,
                     flag: x.flag, count: x.count, refill: x.refill};
          end
          4'b1001: begin // LVNI
            idxWriteReg = ii.j; doIdxWrite = True;
            idxWriteVal = IndexWord{addr: zeroExtend(ii.imm), sign: 1,
                     flag: x.flag, count: x.count, refill: x.refill};
          end
          4'b0010: begin // LCI
            idxWriteReg = ii.j; doIdxWrite = True;
            idxWriteVal = IndexWord{addr: x.addr, sign: x.sign,
                     flag: x.flag, count: imm18, refill: x.refill};
          end
          4'b0011: begin // LRI
            idxWriteReg = ii.j; doIdxWrite = True;
            idxWriteVal = IndexWord{addr: x.addr, sign: x.sign,
                     flag: x.flag, count: x.count, refill: imm18};
          end
          4'b0000: begin // C+I
            idxWriteReg = ii.j; doIdxWrite = True;
            idxWriteVal = IndexWord{addr: x.addr, sign: x.sign, flag: x.flag,
                     count: x.count + imm18, refill: x.refill};
          end
          4'b1000: begin // C-I
            idxWriteReg = ii.j; doIdxWrite = True;
            idxWriteVal = IndexWord{addr: x.addr, sign: x.sign, flag: x.flag,
                     count: x.count - imm18, refill: x.refill};
          end
          4'b0101, 4'b0110, 4'b0111: begin // V+I / V+IC / V+ICR --
            // prefetch/bail-out shape, inlining maybeRefill's own
            // condition (doRefill && x1.count==0) rather than calling
            // it, since only the ICR variant can ever need the read.
            SM128 sum = smAdd(val, immSM);
            IndexWord x1 = IndexWord{addr: truncate(sum.mag), sign: sum.sign,
                             flag: x.flag, count: x.count, refill: x.refill};
            if (ii.code != 4'b0101) x1.count = x1.count - 1;
            if (ii.code == 4'b0111 && x1.count == 0) begin
              if (prefetchCount >= 1) begin
                idxWriteReg = ii.j; doIdxWrite = True;
                idxWriteVal = unpackIndexWord(prefetch[0]);
                ind = setIndexResultIndicatorsF(ind, x1);
              end else
                needsRead = tagged Valid zeroExtend(x1.refill);
            end else begin
              idxWriteReg = ii.j; doIdxWrite = True;
              idxWriteVal = x1; ind = setIndexResultIndicatorsF(ind, x1);
            end
          end
          4'b1101, 4'b1110, 4'b1111: begin // V-I / V-IC / V-ICR --
            // same shape as V+I/V+IC/V+ICR above.
            SM128 diff = smAdd(val, SM128{sign: ~immSM.sign, mag: immSM.mag});
            IndexWord x1 = IndexWord{addr: truncate(diff.mag), sign: diff.sign,
                             flag: x.flag, count: x.count, refill: x.refill};
            if (ii.code != 4'b1101) x1.count = x1.count - 1;
            if (ii.code == 4'b1111 && x1.count == 0) begin
              if (prefetchCount >= 1) begin
                idxWriteReg = ii.j; doIdxWrite = True;
                idxWriteVal = unpackIndexWord(prefetch[0]);
                ind = setIndexResultIndicatorsF(ind, x1);
              end else
                needsRead = tagged Valid zeroExtend(x1.refill);
            end else begin
              idxWriteReg = ii.j; doIdxWrite = True;
              idxWriteVal = x1; ind = setIndexResultIndicatorsF(ind, x1);
            end
          end
          4'b0100: ind = setIndexCmpIndicatorsF(ind, smCompare(val, immSM)); // KVI
          4'b1100: ind = setIndexCmpIndicatorsF(ind, smCompare(val, SM128{sign:~immSM.sign, mag:immSM.mag})); // KVNI
          4'b1010: begin // KCI
            Cmp3 c = (x.count==imm18) ? CmpEqual : (x.count<imm18) ? CmpLow : CmpHigh;
            ind = setIndexCmpIndicatorsF(ind, c);
          end
          default: ind = setOpInvalid(ind); // LVS: out of scope
        endcase
      end

      // -----------------------------------------------------------
      // Count and Branch / Count, Branch and Refill.
      // -----------------------------------------------------------
      tagged CountBranch .cb: begin
        IndexWord x = st.readIndex(cb.j);
        // v: 00=unchanged, 01=+half(=+1 raw), 10=+one(=+2 raw), 11=-one(=-2 raw).
        // SOURCE for the four cases: pocket card p.1 legend and p.3
        // "INDEX BRANCHING" modifier table. The exact raw-unit mapping
        // for "half"/"one" is this implementation's best-effort
        // reading -- see bsv/README.md "Scope".
        Int#(25) delta = case (cb.v)
                            2'b01: 1;
                            2'b10: 2;
                            2'b11: -2;
                            default: 0;
                          endcase;
        SM128 val = SM128{sign: x.sign, mag: zeroExtend(x.addr)};
        SM128 dSM = SM128{sign: pack(delta<0), mag: zeroExtend(pack(abs(delta)))};
        SM128 newVal = smAdd(val, dSM);
        Bit#(18) newCount = x.count - 1;
        IndexWord x1 = IndexWord{addr: truncate(newVal.mag), sign: newVal.sign,
                         flag: x.flag, count: newCount, refill: x.refill};
        // Prefetch/bail-out shape, inlining maybeRefill's own
        // condition (doRefill && x1.count==0) rather than calling it.
        Bool doRefill = (cb.refill == 1) && (x1.count == 0);
        if (doRefill && prefetchCount < 1) begin
          needsRead = tagged Valid zeroExtend(x1.refill);
        end else begin
          IndexWord x2 = doRefill ? unpackIndexWord(prefetch[0]) : x1;
          idxWriteReg = cb.j; doIdxWrite = True;
          idxWriteVal = x2;
          ind = setIndexResultIndicatorsF(ind, x1); // per p.23: indicators reflect
                                                     // state *before* any refill.
          Bool take = (cb.branchIfZero == 1) ? (newCount == 0) : (newCount != 0);
          if (take) next = effAddr19(st, cb.addr, {3'b0, cb.idx}); // K: X1 only
        end
      end

      // -----------------------------------------------------------
      // Branch on Indicator.
      // -----------------------------------------------------------
      tagged BranchInd .bi: begin
        Word64 indWord = ind; // this instruction's own indicator changes
                               // (just `clear`, below) must still land in
                               // the single end-of-execute write, so test
                               // against the value as of entry to execute().
        Bit#(7) indShift = 63 - zeroExtend(bi.indNum);
        Bit#(1) bitVal = indWord[indShift];
        Bool take = (bi.branchOn == 1) ? (bitVal == 1) : (bitVal == 0);
        if (bi.clear == 1) ind = setBit(ind, bi.indNum, 0);
        if (take) next = effAddr19(st, bi.addr, {3'b0, bi.idx});
      end

      // -----------------------------------------------------------
      // Unconditional branching / Store Zero / Refill.
      // -----------------------------------------------------------
      tagged BranchOrMisc .bm: begin
        if (!bm.misc) begin
          // B=010 BR=011 BE=000 BD=001 BEW=100 NOP=110. BE/BD/BEW's
          // interrupt-enable distinction is not modeled (no interrupt
          // system in this implementation, see README); all four
          // unconditional-branch codes other than NOP branch.
          if (bm.code != 3'b110)
            next = effAddr19(st, bm.addr, bm.idx);
        end else begin
          case (bm.code)
            3'b100: st.writeWord(baWord(effAddr24(st, {bm.addr,5'b0}, bm.idx)), 0); // Z (Store Zero)
            3'b000: begin // R (Refill, unconditional)
              IndexWord x = st.readIndex(bm.idx);
              idxWriteReg = bm.idx; doIdxWrite = True;
              let w <- st.readWord(zeroExtend(x.refill));
              idxWriteVal = unpackIndexWord(w);
            end
            3'b001: begin // RCZ (Refill on Count Zero)
              IndexWord x = st.readIndex(bm.idx);
              if (x.count == 0) begin
                idxWriteReg = bm.idx; doIdxWrite = True;
                let w <- st.readWord(zeroExtend(x.refill));
                idxWriteVal = unpackIndexWord(w);
              end
            end
            default: ind = setOpInvalid(ind); // EX, EXIC: out of scope
          endcase
        end
      end

      // -----------------------------------------------------------
      // Transmit (forward only; T only, not SWAP/backward). Copies one
      // whole word from the effective address of addr1 to the
      // effective (word-truncated) address of addr2.
      //
      // SIMPLIFICATION: real Transmit moves `count` words (from index
      // register J's count field, or J itself for immediate count --
      // pocket card "TRANSMIT OPERATIONS" modifier legend), streamed
      // over multiple cycles on the real machine. This single-rule-
      // firing model can only issue one write to storage per
      // instruction (a single-write-port memory -- see
      // bsv/README.md "Toolchain"/"Scope"), so it moves exactly one
      // word regardless of `count` and does not decrement/refill J.
      // Multi-word Transmit is a documented gap, not a silent one.
      // -----------------------------------------------------------
      tagged Transmit .t: begin
        if (t.backward == 1)
          ind = setOpInvalid(ind); // SWAP / backward transmit: out of scope
        else begin
          WordAddr srcBase = baWord(effAddr24(st, t.addr1, t.i1));
          WordAddr dstBase = (effAddr19(st, t.addr2, t.i2))[18:1];
          let srcVal <- st.readWord(srcBase);
          st.writeWord(dstBase, srcVal);
        end
      end

      // -----------------------------------------------------------
      // Everything else this decoder recognizes structurally but does
      // not execute.
      // -----------------------------------------------------------
      // -----------------------------------------------------------
      // Connectives (p.75-77 "Connectives"): sixteen bitwise boolean
      // functions of a storage field `m` and an accumulator field `a`
      // of the same length, selected by `conn` (Figure 20). Which of
      // the three connective operations to perform is NOT a separate
      // decoded tag -- it's `suffix`, IBM bits 55-59 of the same
      // instruction word (X22-6533 pocket card "CONNECTIVES" table):
      //   xxxx00111 = C  (Connect: result -> accumulator field)
      //   xxxx01111 = CM (Connect to Memory: result -> storage field)
      //   xxxx10111 = CT (Connect for Test: result discarded, only
      //                    indicators set)
      // Same addressing (direct/immediate/progressive, p.75 "Format":
      // "The connective operations use basically the same full-word
      // instruction format as the integer arithmetic operations...
      // Immediate addressing is also handled the same way") and same
      // deferred-index-write mechanism as VflInt above, for the same
      // reason: C/CM write general storage (writeAcc/writeField, both
      // go through st.writeWord) in the same arm that would write an
      // index register under progressive indexing.
      //
      // SCOPE: byte size is assumed to be 8 (BS=0, the default, and
      // the manual's own recommendation: "To combine a group of bits
      // in storage with the same number of contiguous bits in the
      // accumulator, a byte size of eight should be specified. This
      // avoids the addition of high-order zeros..."). The <8-byte-size
      // conversion p.75 "Byte Size" describes (each short byte padded
      // to 8 bits with high-order zeros before combining) is NOT
      // implemented -- effByteSize's result is decoded but unused
      // here. Partial Field (PF) and the left-zeros/all-ones counts at
      // word 7 are also not implemented, consistent with the rest of
      // this file (PF isn't implemented for VflInt either). Not
      // exercised by any program yet with BS!=8.
      tagged Connective .cn: begin
        Bool isProgressive = (cn.a.p != 0 && cn.a.p != 4);
        Bool immediate = (cn.a.p == 4);
        if (isProgressive && cn.a.i1 == 0) begin
          ind = setOpInvalid(ind);
        end else if (cn.suffix == 5'b01111 && immediate) begin
          // CM + immediate: "Immediate addressing is not possible in
          // operations whose result is placed in storage... the
          // operation is not performed and the OP indicator is turned
          // on" (p.56) -- same rule already enforced for VflInt's
          // ST/M+ above.
          ind = setOpInvalid(ind);
        end else begin
          Bit#(7) len_ = effLength(cn.a.length);
          IndexWord xIdx = st.readIndex(cn.a.i1);
          BitAddr ea = isProgressive ? xIdx.addr : effAddr24(st, cn.a.addr, cn.a.i1);
          Bit#(8) offSh = zeroExtend(cn.a.offset);
          Bit#(8) len8 = zeroExtend(len_);
          Bit#(64) fieldMask = (len_ == 64) ? '1 : ((1 << len8) - 1);
          Bool vflOk = True; // p.21/22: a suppressed VFL-format op skips
                              // the progressive increment too, same
                              // rule as VflInt.

          if (cn.suffix == 5'b01111 && fieldCrosses(ea, len_)) begin
            // CM writing a crossing field: same single-word-write
            // limitation as VflInt's ST/M+ (writeField's precondition).
            ind = setOpInvalid(ind);
            vflOk = False;
          end else begin
            Bit#(64) m = 0;
            Word64 mHiWord = 0; // valid only when !immediate; CM (the
                                 // only suffix that writes back) is
                                 // guaranteed !immediate above, so it's
                                 // always set by the time CM reads it.
            if (immediate) m = immediateOperand(cn.a.addr, len_);
            else begin
              let {r, hiWord} <- readFieldWithHi(st, ea, len_);
              m = r;
              mHiWord = hiWord;
            end
            SM128 acc = readAcc(st);
            Bit#(64) a = truncate(acc.mag >> offSh) & fieldMask;
            Bit#(64) result = applyConnective(cn.conn, m, a) & fieldMask;
            Bool resultZero = (result == 0);

            case (cn.suffix)
              5'b00111: begin // C: result replaces the accumulator
                              // field; the rest of the accumulator is
                              // unchanged (p.76 "In CONNECT... The
                              // remainder of the accumulator remains
                              // unchanged").
                Bit#(128) fieldMask128 = zeroExtend(fieldMask) << offSh;
                Bit#(128) resultSh = zeroExtend(result) << offSh;
                SM128 merged = SM128 { sign: acc.sign,
                                        mag: (acc.mag & ~fieldMask128) | resultSh };
                writeAcc(st, merged);
              end
              5'b01111: writeFieldWithHi(st, ea, len_, result, mHiWord); // CM
              5'b10111: begin end // CT: result discarded, indicators only
              default: ind = setOpInvalid(ind); // unreachable: StretchDecode's
                                                 // isConnSuffix only admits these
                                                 // three patterns; kept for bsc's
                                                 // exhaustiveness check, same style
                                                 // as VflInt's own default arm above.
            endcase

            ind = setConnectiveIndicatorsF(ind, cn.suffix == 5'b01111, resultZero);
          end

          if (isProgressive && vflOk) begin
            let {x2, ind2} <- progressiveIncrement(st, cn.a, xIdx, ind);
            vflPending = tagged Valid tuple2(cn.a.i1, x2);
            ind = ind2;
          end
        end
      end
      tagged Fp .fp: begin
        if (fp.code == 7'b0000110 || fp.code == 7'b0001110) begin // L / ST
          WordAddr ea = effAddr18(st, fp.addr, fp.idx);
          if (fp.code == 7'b0000110) begin // L: clears the whole accumulator (p.~90)
            let v <- st.readWord(ea);
            writeAcc(st, SM128{sign: 0, mag: zeroExtend(v)});
          end else begin // ST
            Word64 v = st.readAccRight(); // compile-time-constant
                                           // address; see readAcc's
                                           // own comment above.
            st.writeWord(ea, v);
          end
        end else
          ind = setOpInvalid(ind); // FP arithmetic beyond L/ST: out of scope
      end
      // -----------------------------------------------------------
      // Input-Output (Reference Manual "IBM 7619 Exchange", pp.104-127,
      // and "External Units", pp.129-149; see StretchIO.bsv's file
      // header for the full scope statement this case implements
      // against -- synchronous single-block transfer, three fixed
      // simulated devices, RD/W/CCW/REL/CTL, LOC not implemented).
      // -----------------------------------------------------------
      tagged IoOp .io_: begin
        Bit#(4) op4 = io_.op;
        Bool seop = (op4[2] == 1); // SEOP: suppress EOP on completion
        Bit#(3) base = {op4[3], op4[1], op4[0]}; // 000=RD 001=W 010=CTL
                                                   // 011=LOC 100=CCW 101=REL
        BitAddr effA1 = effAddr24(st, io_.addr1, io_.i1);
        WordAddr chAddr = zeroExtend(effA1[11:5]); // IBM bits 12-18 of
                                                     // the 24-bit
                                                     // channel-address
                                                     // field (p.111) --
                                                     // NOT offset by 32;
                                                     // the field itself
                                                     // holds the actual
                                                     // channel number.
        DeviceKind kind = kindOf(chAddr);
        Bool readerCh  = (kind == DevReader);
        Bool printerCh = (kind == DevPrinter);
        Bool tapeCh    = (kind == DevTape);

        if (kind == DevNone) begin
          // Unit Not Ready Reject (p.112): none of this model's
          // simulated devices is installed at this channel address.
          // The instruction is never accepted; no control word
          // anywhere is touched.
          ind = setBit(ind, ind_UNRJ, 1);
        end else begin
          // Address Invalid (AD) for an out-of-range control-word
          // address (p.111-112) is NOT checked here, consistent with
          // this codebase's existing general non-enforcement of AD
          // (see e.g. VflInt/Connective, which likewise don't check it)
          // -- a documented gap, not a silent one.
          WordAddr effA2 = effAddr18(st, io_.addr2, io_.i2);
          case (base)
            3'b010: begin // CTL (Control) -- only implemented against
                           // the tape channel (StretchIO.bsv "CONTROL
                           // FUNCTIONS"); reader/printer CTL and every
                           // tape function code this model doesn't
                           // implement fall through to OP-invalid.
              if (!tapeCh) begin
                ind = setOpInvalid(ind);
              end else begin
                // p.111: CONTROL's right effective address carries a
                // raw function code, NOT a core-storage word address
                // -- effA2 here is that code as-is (strap_asm.py's
                // IO_OP branch deliberately skips the >>6 word-address
                // conversion for CTL/LOC; see its own comment).
                case (effA2)
                  18'o136, 18'o137: begin // REWIND / REWIND AND UNLOAD
                                            // (p.132) -- see StretchIO.bsv
                                            // for why both map to the
                                            // same behavior here.
                    io.setTapePos(0);
                    ControlWord cw = io.readChanCW(chAddr);
                    if (!seop) cw.eop = 1;
                    io.writeChanCW(chAddr, cw);
                  end
                  18'o176: begin // BACKSPACE BLOCK (p.132)
                    ControlWord cw = io.readChanCW(chAddr);
                    if (io.tapePos() == 0) begin
                      // "the tape cannot be moved... beyond the load
                      // point. Any backspace instructions given with
                      // the tape in this position are terminated with
                      // an exchange-program-check indication" (p.136).
                      cw.epgk = 1;
                      if (!seop) cw.eop = 1;
                    end else begin
                      io.setTapePos(io.tapePos() - 1);
                      if (!seop) cw.eop = 1;
                    end
                    io.writeChanCW(chAddr, cw);
                  end
                  default: ind = setOpInvalid(ind); // SPACE BLOCK/FILE,
                                                       // WRITE TAPE MARK,
                                                       // BACKSPACE FILE,
                                                       // density/ECC/
                                                       // parity/light
                                                       // functions --
                                                       // real p.130-132
                                                       // codes this
                                                       // model does not
                                                       // implement; see
                                                       // StretchIO.bsv.
                endcase
              end
            end
            3'b011: ind = setOpInvalid(ind); // LOC: not implemented --
                                               // see StretchIO.bsv
                                               // "INSTRUCTIONS".
            3'b101: begin // REL (Release)
              ControlWord cw = io.readChanCW(chAddr);
              cw.epgk = 0; cw.uk = 0; cw.ee = 0; cw.cs = 0; cw.seop = 0;
              // "the EOP indication is immediately turned on" (p.120-121)
              // -- EXCEPT for RELEASE SEOP, where the manual is explicit
              // that "no EOP indication is ever given at the completion
              // of a RELEASE SEOP" (p.121).
              if (!seop) cw.eop = 1;
              io.writeChanCW(chAddr, cw);
            end
            3'b100: // CCW (Copy Control Word): no EOP indication given
                     // (p.122), so the control word here is left alone.
              st.writeWord(effA2, packControlWord(io.readChanCW(chAddr)));
            3'b000, 3'b001: begin // RD, W
              Bool wrongUnit = (base == 3'b000)
                ? (!readerCh && !tapeCh)   // RD valid on reader or tape
                : (!printerCh && !tapeCh); // W valid on printer or tape
              if (wrongUnit) begin
                // Exchange Program Check (p.113): "an instruction is
                // received that the selected unit is not designed to
                // perform, such as a READ given to a printer" -- the
                // exact case cited by the manual. EOP is set alongside
                // it: the operation never starts, so it's immediately
                // "terminated" in the sense every other status bit
                // uses -- a documented judgment call, not a quoted rule.
                ControlWord cw = io.readChanCW(chAddr);
                cw.epgk = 1; cw.eop = 1;
                io.writeChanCW(chAddr, cw);
              end else begin
                let raw <- st.readWord(effA2);
                ControlWord cw0 = unpackControlWord(raw);
                io.writeChanCW(chAddr, cw0); // exchange adopts the
                                              // requested control word
                                              // (p.106: "the exchange
                                              // obtains the specified
                                              // control word... and
                                              // stores it in the
                                              // exchange").
                // p.107 "Zero Initial Word Count": count==0 means 2^18,
                // representable here since `remaining` is 19 bits.
                Bit#(19) rem0 = (cw0.count == 0) ? 19'd262144 : zeroExtend(cw0.count);
                ioStart = tagged Valid IoXfer {
                  ch: chAddr, isWrite: (base == 3'b001),
                  memAddr: cw0.dataAddr,
                  // Reader/printer always restart at device index 0
                  // (StretchIO.bsv has no persistent position for
                  // either). Tape instead continues from wherever the
                  // last transfer or CTL REWIND/BACKSPACE BLOCK left
                  // it -- see StretchIO.bsv "TAPE POSITION".
                  devIdx: tapeCh ? zeroExtend(io.tapePos()) : 0,
                  remaining: rem0, suppressEop: seop,
                  // SKIP (p.107) only has meaning on READ -- "on writing,
                  // the flag is meaningless and is ignored" -- so it's
                  // only threaded through when this is an RD; a WRITE
                  // ignores cw0.skip regardless of what's in memory.
                  skip: (base == 3'b000) && (cw0.skip == 1) };
              end
            end
          endcase
        end
      end
      tagged Sic .*:       ind = setOpInvalid(ind);
      tagged BitBranch .*: ind = setOpInvalid(ind);
      tagged Unimplemented: ind = setOpInvalid(ind);
      tagged Invalid:       ind = setOpInvalid(ind);

    endcase

    if (needsRead matches tagged Invalid) begin
      if (doIdxWrite) st.writeIndex(idxWriteReg, idxWriteVal);
      st.setIndicatorBits(ind);
      return tuple4(next, vflPending, ioStart, tagged Invalid);
    end else begin
      // Bailed out partway through: the arm that set `needsRead` did
      // so before touching any of these, so returning the function-
      // ENTRY values here (not whatever partial computation produced)
      // is correct by construction -- see this function's own header
      // comment.
      return tuple4(pc, tagged Invalid, tagged Invalid, needsRead);
    end
  endactionvalue;

endpackage
