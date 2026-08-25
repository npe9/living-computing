// StretchExecute.bsv
//
// Execute stage. Implements the subset of the IBM 7030 instruction set
// documented as in-scope in bsv/README.md: VFL binary integer L/ST/+/M+/K
// (Reference Manual 22-6530-2 pp.~86-95) with both standard address
// modification and progressive indexing (P in {1,2,3,5,6,7}, p.21),
// direct and immediate index arithmetic (pp.22-27), count-and-branch
// and branch-on-indicator (pp.~26-27, pocket card X22-6533-1 "INDEX
// BRANCHING"/"INDICATOR BRANCHING"), unconditional branching, Store
// Zero / Refill, and direct (non-backward, single-word) Transmit.
//
// Every other decoded format/opcode -- decimal arithmetic, floating
// point arithmetic beyond L/ST, connectives, radix conversion,
// input-output, interrupts, bit branching, SIC, EX/EXIC, RNX/LVE/SVA,
// LVS, Transmit backward/swap -- sets indicator 15 (OP, Operation Code
// Invalid) and otherwise acts as a no-op, matching the documented
// real-machine behavior for an invalid/suppressed instruction
// (Reference Card, indicator class "S": "execution of instruction is
// suppressed"). See bsv/README.md "Scope" for the full accounting and
// citations.
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

import StretchTypes::*;
import StretchStorage::*;
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
function Bit#(32) readHW(StretchStorage st, HWordAddr ha);
  Word64 w = st.readWord(ha[18:1]);
  return (ha[0] == 0) ? w[63:32] : w[31:0];
endfunction

function Action writeHW(StretchStorage st, HWordAddr ha, Bit#(32) v) =
  action
    WordAddr wa = ha[18:1];
    Word64 w = st.readWord(wa);
    Word64 neww = (ha[0] == 0) ? {v, w[31:0]} : {w[63:32], v};
    st.writeWord(wa, neww);
  endaction;

// ---------------------------------------------------------------------
// Accumulator as a 128-bit sign-magnitude value (see StretchALU.bsv
// header for the documented simplification).
// ---------------------------------------------------------------------

function SM128 readAcc(StretchStorage st) =
  accToSM(st.readWord(addrAccLeft), st.readWord(addrAccRight));

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
    if (doRefill && x.count == 0)
      return unpackIndexWord(st.readWord(zeroExtend(x.refill)));
    else
      return x;
  endactionvalue;

// Progressive indexing's post-operation increment (Reference Manual
// p.21): add (P 1-3) or subtract (P 5-7) the instruction's address
// part -- reused here as a plain positive increment, not an address --
// into the SAME index register used as the effective address,
// optionally counting down (2/3, 6/7) and refilling on count zero (3,
// 7); indicators reflect the pre-refill state. A plain (non-Action)
// function -- `st.readWord` (used for the refill case) is a
// combinational value method -- returning the new index word rather
// than writing it: see the long comment at this function's one call
// site (in the VflInt case of `execute`, below) for why the actual
// `st.writeIndex` for progressive indexing happens in StretchCore.step
// instead of here.
function Tuple2#(IndexWord, Word64) progressiveIncrement(
    StretchStorage st, VflAddr a, IndexWord xIdx, Word64 indIn);
    SM128 val = SM128{sign: xIdx.sign, mag: zeroExtend(xIdx.addr)};
    Bool subtract = (a.p >= 5);
    SM128 inc = SM128{sign: (subtract ? 1 : 0), mag: zeroExtend(a.addr)};
    SM128 sum = smAdd(val, inc);
    IndexWord x1 = IndexWord{addr: truncate(sum.mag), sign: sum.sign,
                     flag: xIdx.flag, count: xIdx.count, refill: xIdx.refill};
    Bit#(3) pLow = a.p - (subtract ? 4 : 0); // 1/2/3, regardless of add/subtract
    if (pLow != 1) x1.count = x1.count - 1;
    IndexWord x2 = (pLow == 3 && x1.count == 0)
                     ? unpackIndexWord(st.readWord(zeroExtend(x1.refill)))
                     : x1;
    return tuple2(x2, setIndexResultIndicatorsF(indIn, x1)); // pre-refill state, p.21
endfunction

// ---------------------------------------------------------------------
// Top-level execute: consumes one decoded instruction, performs its
// side effects on `st`, and returns the next instruction counter
// (half-word address). `pc` is the address of the instruction just
// fetched; `len` says whether it was one or two half-words.
// ---------------------------------------------------------------------

// Returns (next PC, an optional pending index-register write for
// progressive indexing). See the VflInt case below for why that write
// is *returned* rather than performed here, and StretchCore.step for
// where it's actually realized.
function ActionValue#(Tuple2#(HWordAddr, Maybe#(Tuple2#(Bit#(4), IndexWord))))
    execute(StretchStorage st, HWordAddr pc, InstrLen len, DecodedInstr di) =
  actionvalue
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
            6'b000101: begin // L (Load)
              Bit#(64) raw = immediate ? immediateOperand(vi.a.addr, len_)
                                        : readField(st, ea, len_);
              SM128 sm = fieldToSM(raw, len_, bsz, vi.m.unsign, vi.m.invert);
              SM128 shifted = SM128 { sign: sm.sign, mag: sm.mag << offSh };
              writeAcc(st, shifted);
              ind = setResultIndicatorsF(ind, shifted);
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
              Bit#(64) raw = immediate ? immediateOperand(vi.a.addr, len_)
                                        : readField(st, ea, len_);
              SM128 opnd = fieldToSM(raw, len_, bsz, vi.m.unsign, vi.m.invert);
              SM128 opndSh = SM128 { sign: opnd.sign, mag: opnd.mag << offSh };
              SM128 sum = smAdd(readAcc(st), opndSh);
              writeAcc(st, sum);
              ind = setResultIndicatorsF(ind, sum);
            end
            6'b001001: begin // M+ (Add to Memory)
              if (immediate || fieldCrosses(ea, len_)) begin
                ind = setOpInvalid(ind);
                vflOk = False;
              end else begin
                Bit#(64) raw = readField(st, ea, len_);
                SM128 opnd = fieldToSM(raw, len_, bsz, vi.m.unsign, vi.m.invert);
                SM128 acc = readAcc(st);
                SM128 accSh = SM128 { sign: acc.sign, mag: acc.mag >> offSh };
                SM128 sum = smAdd(opnd, accSh);
                writeField(st, ea, len_, smToField(sum, len_, bsz, vi.m.unsign));
                ind = setResultIndicatorsF(ind, sum);
              end
            end
            6'b010001: begin // K (Compare) -> AL/AE/AH
              Bit#(64) raw = immediate ? immediateOperand(vi.a.addr, len_)
                                        : readField(st, ea, len_);
              SM128 opnd = fieldToSM(raw, len_, bsz, vi.m.unsign, vi.m.invert);
              SM128 opndSh = SM128 { sign: opnd.sign, mag: opnd.mag << offSh };
              Cmp3 c = smCompare(readAcc(st), opndSh);
              ind = setAccCmpIndicatorsF(ind, c);
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
          if (isProgressive && vflOk) begin
            let {x2, ind2} = progressiveIncrement(st, vi.a, xIdx, ind);
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
          5'b00001: begin // LX
            idxWriteReg = di_.j; doIdxWrite = True;
            idxWriteVal = unpackIndexWord(st.readWord(ea[18:1]));
          end
          5'b10001: st.writeWord(ea[18:1], packIndexWord(x));                     // SX
          5'b00011: begin // LV
            Bit#(32) h = readHW(st, ea);
            idxWriteReg = di_.j; doIdxWrite = True;
            idxWriteVal = IndexWord{addr:h[31:8], sign:h[7:7], flag:x.flag,
                                            count:x.count, refill:x.refill};
          end
          5'b10011: begin // SV
            Bit#(32) h = readHW(st, ea);
            writeHW(st, ea, {x.addr, x.sign, h[6:0]});
          end
          5'b00101: begin // LC
            Bit#(32) h = readHW(st, ea);
            idxWriteReg = di_.j; doIdxWrite = True;
            idxWriteVal = IndexWord{addr:x.addr, sign:x.sign, flag:x.flag,
                                            count:h[31:14], refill:x.refill};
          end
          5'b10101: begin // SC
            Bit#(32) h = readHW(st, ea);
            writeHW(st, ea, {x.count, 7'b0, h[6:0]});
          end
          5'b00111: begin // LR
            Bit#(32) h = readHW(st, ea);
            idxWriteReg = di_.j; doIdxWrite = True;
            idxWriteVal = IndexWord{addr:x.addr, sign:x.sign, flag:x.flag,
                                            count:x.count, refill:h[31:14]};
          end
          5'b10111: begin // SR
            Bit#(32) h = readHW(st, ea);
            writeHW(st, ea, {x.refill, 7'b0, h[6:0]});
          end
          5'b01011, 5'b01101, 5'b01111: begin // V+ / V+C / V+CR
            Bit#(32) h = readHW(st, ea);
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
            Bit#(32) h = readHW(st, ea);
            SM128 opnd = SM128{sign: h[7], mag: zeroExtend(h[31:8])};
            SM128 val  = SM128{sign: x.sign, mag: zeroExtend(x.addr)};
            ind = setIndexCmpIndicatorsF(ind, smCompare(val, opnd));
          end
          5'b11001: begin // KC
            Bit#(32) h = readHW(st, ea);
            Cmp3 c = (x.count == h[31:14]) ? CmpEqual : (x.count < h[31:14]) ? CmpLow : CmpHigh;
            ind = setIndexCmpIndicatorsF(ind, c);
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
          4'b0101, 4'b0110, 4'b0111: begin // V+I / V+IC / V+ICR
            SM128 sum = smAdd(val, immSM);
            IndexWord x1 = IndexWord{addr: truncate(sum.mag), sign: sum.sign,
                             flag: x.flag, count: x.count, refill: x.refill};
            if (ii.code != 4'b0101) x1.count = x1.count - 1;
            IndexWord x2 <- (ii.code == 4'b0111) ? maybeRefill(st, x1, True)
                                                  : actionvalue return x1; endactionvalue;
            idxWriteReg = ii.j; doIdxWrite = True;
            idxWriteVal = x2; ind = setIndexResultIndicatorsF(ind, x1);
          end
          4'b1101, 4'b1110, 4'b1111: begin // V-I / V-IC / V-ICR
            SM128 diff = smAdd(val, SM128{sign: ~immSM.sign, mag: immSM.mag});
            IndexWord x1 = IndexWord{addr: truncate(diff.mag), sign: diff.sign,
                             flag: x.flag, count: x.count, refill: x.refill};
            if (ii.code != 4'b1101) x1.count = x1.count - 1;
            IndexWord x2 <- (ii.code == 4'b1111) ? maybeRefill(st, x1, True)
                                                  : actionvalue return x1; endactionvalue;
            idxWriteReg = ii.j; doIdxWrite = True;
            idxWriteVal = x2; ind = setIndexResultIndicatorsF(ind, x1);
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
        IndexWord x2 <- maybeRefill(st, x1, cb.refill == 1);
        idxWriteReg = cb.j; doIdxWrite = True;
        idxWriteVal = x2;
        ind = setIndexResultIndicatorsF(ind, x1); // per p.23: indicators reflect
                                                   // state *before* any refill.
        Bool take = (cb.branchIfZero == 1) ? (newCount == 0) : (newCount != 0);
        if (take) next = effAddr19(st, cb.addr, {3'b0, cb.idx}); // K: X1 only
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
              idxWriteVal = unpackIndexWord(st.readWord(zeroExtend(x.refill)));
            end
            3'b001: begin // RCZ (Refill on Count Zero)
              IndexWord x = st.readIndex(bm.idx);
              if (x.count == 0) begin
                idxWriteReg = bm.idx; doIdxWrite = True;
                idxWriteVal = unpackIndexWord(st.readWord(zeroExtend(x.refill)));
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
          st.writeWord(dstBase, st.readWord(srcBase));
        end
      end

      // -----------------------------------------------------------
      // Everything else this decoder recognizes structurally but does
      // not execute.
      // -----------------------------------------------------------
      tagged Connective .*: ind = setOpInvalid(ind);
      tagged Fp .fp: begin
        if (fp.code == 7'b0000110 || fp.code == 7'b0001110) begin // L / ST
          WordAddr ea = effAddr18(st, fp.addr, fp.idx);
          if (fp.code == 7'b0000110) // L: clears the whole accumulator (p.~90)
            writeAcc(st, SM128{sign: 0, mag: zeroExtend(st.readWord(ea))});
          else // ST
            st.writeWord(ea, st.readWord(addrAccRight));
        end else
          ind = setOpInvalid(ind); // FP arithmetic beyond L/ST: out of scope
      end
      tagged IoOp .*:      ind = setOpInvalid(ind);
      tagged Sic .*:       ind = setOpInvalid(ind);
      tagged BitBranch .*: ind = setOpInvalid(ind);
      tagged Unimplemented: ind = setOpInvalid(ind);
      tagged Invalid:       ind = setOpInvalid(ind);

    endcase

    if (doIdxWrite) st.writeIndex(idxWriteReg, idxWriteVal);
    st.setIndicatorBits(ind);
    return tuple2(next, vflPending);
  endactionvalue;

endpackage
