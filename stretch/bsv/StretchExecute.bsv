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
// Every decoded format/opcode NOT yet implemented -- decimal
// arithmetic, radix conversion, interrupts, EX/EXIC, RNX/LVE/SVA, LVS,
// Transmit backward/swap -- sets indicator 15 (OP, Operation Code
// Invalid) and otherwise acts as a no-op, matching the documented
// real-machine behavior for an invalid/suppressed instruction
// (Reference Card, indicator class "S": "execution of instruction is
// suppressed"). See bsv/README.md "Scope" for the full accounting and
// citations.
//
// THIS LIST USED TO INCLUDE "floating point arithmetic beyond L/ST",
// "input-output" and "bit branching". All three are now implemented --
// the whole floating-point opcode table as of jb_af1c F218, I/O in the
// IoOp arm, bit branching in the BitBranch arm -- and the header had
// been contradicting the code (and its own `known` list) for some
// time. Found by a structural review, not by a test: a stale comment
// is exactly the thing a regression suite cannot catch.
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
import StretchMemory::*;  // installed(): the address-invalid bound
import StretchIO::*;
import StretchVFL::*;
import StretchALU::*;
import StretchDecode::*; // decodeHalfWord, for SIC's embedded branch
import StretchFP::*;     // single-precision floating-point arithmetic

// ---------------------------------------------------------------------
// Half-word branch evaluation, shared by the CountBranch / BranchInd /
// BranchOrMisc case arms of execute() and by SIC (Store Instruction
// Counter If), whose right half-word IS one of those three branches
// (Reference Manual p.41: "Bits 32-63 specify the half-word branch
// instruction used"). Pure: it reads storage/index state and returns
// what the branch WOULD do -- indicator word, index-register write,
// taken/target -- so the caller commits it, and SIC can additionally
// store the instruction counter on `taken`. Kept as a function rather
// than duplicating the CB/BI/B logic inside the Sic arm.
//
// `slot`: which prefetch slot a refilling CBR's own read lands in
// (0 today for every caller; parameterized so a caller that has
// already consumed slot 0 could pass 1). `readsUsed` reports how many
// slots the branch consumed once complete, so SIC can place its own
// target-word read in the NEXT slot instead of colliding with the
// refill word (the exact collision class docs/phase2_arm_inventory.md
// step 9 records for ST + refill).
// ---------------------------------------------------------------------
typedef struct {
  Maybe#(WordAddr) needsRead;
  Bit#(2)   readsUsed;
  Bool      doIdxWrite;
  Bit#(4)   idxWriteReg;
  IndexWord idxWriteVal;
  Word64    ind;
  Bool      taken;
  HWordAddr target;
} BranchOutcome deriving (Bits, Eq);

function BranchOutcome evalBranch(StretchStorage st, DecodedInstr d, Word64 ind0,
                                  Vector#(2, Word64) prefetch, Bit#(2) prefetchCount,
                                  Bit#(2) slot);
  BranchOutcome o = BranchOutcome {
    needsRead: tagged Invalid, readsUsed: 0, doIdxWrite: False, idxWriteReg: 0,
    idxWriteVal: IndexWord{addr:0, sign:0, flag:0, count:0, refill:0},
    ind: ind0, taken: False, target: 0 };
  case (d) matches

    // Count and Branch / Count, Branch and Refill.
    tagged CountBranch .cb: begin
      IndexWord x = st.readIndex(cb.j);
      // v (instruction bits 23-24), Reference Manual p.41 "Count and
      // Branch" table: 00 no incrementing; 01 "H Add half to value:
      // Add one in bit position 18"; 10 "+ Add one to value: Add one
      // in bit position 17"; 11 "- Subtract one from value: Subtract
      // one in bit position 17". The value field is a 24-bit bit
      // address (bit 23 = 1 bit), so bit 18 is 32 bits (a half-word)
      // and bit 17 is 64 (a word). An earlier version added 1/2/-2
      // raw bits (recorded in bsv/README.md as an unconfirmed
      // reading); I-Box 1's CBR+/CBR-/CBRH/CBRZ+/CBRZ-/CBRZH groups
      // (strap/programs/ibox1_p46_p51_span.strap) hang at their
      // value tests under that mapping and pass under this one.
      Int#(25) delta = case (cb.v)
                          2'b01: 32;
                          2'b10: 64;
                          2'b11: -64;
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
      if (doRefill && prefetchCount < slot + 1) begin
        o.needsRead = tagged Valid zeroExtend(x1.refill);
      end else begin
        IndexWord x2 = doRefill ? unpackIndexWord(prefetch[slot[0]]) : x1;
        o.readsUsed = doRefill ? 1 : 0;
        o.doIdxWrite = True; o.idxWriteReg = cb.j; o.idxWriteVal = x2;
        o.ind = setIndexResultIndicatorsF(ind0, x1); // per p.23: indicators reflect
                                                      // state *before* any refill.
        Bool take = (cb.branchIfZero == 1) ? (newCount == 0) : (newCount != 0);
        if (take) begin
          o.taken = True;
          o.target = effAddr19(st, cb.addr, {3'b0, cb.idx}); // K: X1 only
        end
      end
    end

    // Branch on Indicator. Tests the indicator word as of entry to
    // execute() (ind0); its own `clear` still lands in the single
    // end-of-execute indicator write via o.ind.
    tagged BranchInd .bi: begin
      Bit#(7) indShift = 63 - zeroExtend(bi.indNum);
      Bit#(1) bitVal = ind0[indShift];
      Bool take = (bi.branchOn == 1) ? (bitVal == 1) : (bitVal == 0);
      if (bi.clear == 1) o.ind = setBit(ind0, bi.indNum, 0);
      if (take) begin
        o.taken = True;
        o.target = effAddr19(st, bi.addr, {3'b0, bi.idx});
      end
    end

    // Unconditional branching. B=010 BR=011 BE=000 BD=001 BEW=100
    // NOP=110. BE/BD/BEW's interrupt-enable distinction is not modeled
    // (no interrupt system in this implementation, see README); all
    // four unconditional-branch codes other than NOP branch. The misc
    // (Z/R/RCZ/EX) half of this format is NOT a branch and is handled
    // by execute()'s own BranchOrMisc arm; a caller only hands the
    // non-misc shape here.
    tagged BranchOrMisc .bm: begin
      if (!bm.misc && bm.code != 3'b110) begin
        o.taken = True;
        o.target = effAddr19(st, bm.addr, bm.idx);
      end
    end

    default: o.ind = setOpInvalid(ind0); // not a half-word branch: fail loud
  endcase
  return o;
endfunction

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

// readHW/readHWWithWord/writeHW (the internal-read variants of this
// section) were removed once every caller had migrated to the
// prefetch/bail-out mechanism in execute() -- see
// docs/phase2_arm_inventory.md step 9 and git history for what they
// looked like. writeHWWithWord below (no internal read) remains live.

// Write a half-word back into a word the caller already has on hand
// (via execute()'s own prefetch mechanism) -- no internal read.
// Precondition: `w` is the word most recently read at `ha`'s word
// address, and nothing else wrote that word in between (same
// precondition writeFieldWithHi has for its own `hi` parameter).
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
function SM128 readAcc(StretchStorage st) = accToSM(st.readAccLeft(), st.readAccRight(), st.readAccSign());

function Action writeAcc(StretchStorage st, SM128 v) =
  action
    let {hi,lo} = packAcc(v.mag);
    st.writeWord(addrAccLeft, hi);
    st.writeWord(addrAccRight, lo);
    Word64 sb = st.readAccSign();
    st.writeWord(addrAccSignByte, sbWith(sb, v.sign, sbFlags(sb)));
  endaction;

// Floating-point arithmetic result indicators (p.85): RLZ/RZ/RGZ from
// the fraction result's sign and zero-ness, RN = negative.
function Word64 setResultIndicatorsFp(Word64 ind, FpNum v);
  Bool z = (v.frac == 0);
  Word64 i1 = setBit(ind, ind_RLZ, pack(!z && v.sign == 1));
  Word64 i2 = setBit(i1,  ind_RZ,  pack(z));
  Word64 i3 = setBit(i2,  ind_RGZ, pack(!z && v.sign == 0));
  return setBit(i3, ind_RN, v.sign);
endfunction

// Exponent range indicators (permanent: only turned on here).
function Word64 setRangeIndicators(Word64 ind, Bit#(5) bits);
  Word64 i = ind;
  if (bits[4] == 1) i = setBit(i, ind_XPFP, 1);
  if (bits[3] == 1) i = setBit(i, ind_XPO, 1);
  if (bits[2] == 1) i = setBit(i, ind_XPH, 1);
  if (bits[1] == 1) i = setBit(i, ind_XPL, 1);
  if (bits[0] == 1) i = setBit(i, ind_XPU, 1);
  return i;
endfunction

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
// -------------------------------------------------------------------
// PROGRESSIVE-INDEX BOOKKEEPING, p.21 "Progressive Indexing". After
// the effective address is taken from the index register's own value
// field, the instruction's address part -- reused as a plain positive
// increment, not an address -- is added (P 1-3) or subtracted (P 5-7)
// back into that value field; the count field goes down for every P
// but 1 and 5; and P 3/7 refill when that count reaches zero.
//
// Computed from Reg-only state (the index register and the
// instruction's own fields) with no BRAM dependency at all, so an arm
// that also writes storage -- VFL ST/M+, connective CM -- can learn
// BEFORE it acts whether a refill read will also be needed, and defer
// its write rather than issue a write and a refill's readWordReq in
// the same execute() call (see vflWriteArmHandled).
//
// VflInt and Connective carried character-identical copies of this,
// differing only in which arm's `a` they read -- which is the same
// VflAddr type in both. Both call here now.
// -------------------------------------------------------------------
function Tuple2#(IndexWord, Bool) progressiveIndex(VflAddr a, IndexWord x);
  Bool sub = (a.p >= 5);
  SM128 val = SM128{sign: x.sign, mag: zeroExtend(x.addr)};
  SM128 inc = SM128{sign: (sub ? 1 : 0), mag: zeroExtend(a.addr)};
  SM128 sum = smAdd(val, inc);
  IndexWord px = IndexWord{addr: truncate(sum.mag), sign: sum.sign,
                           flag: x.flag, count: x.count, refill: x.refill};
  Bit#(3) low = a.p - (sub ? 4 : 0);
  if (low != 1) px.count = px.count - 1;
  Bool progressive = (a.p != 0 && a.p != 4);
  return tuple2(px, progressive && (low == 3 && px.count == 0));
endfunction

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

// maybeRefill and progressiveIncrement (conditional index-refill
// logic, Reference Manual p.21-22) were removed once every caller had
// migrated to the prefetch/bail-out mechanism, each inlining this same
// "add/subtract, count down, refill on count zero" logic directly at
// its own call site (VflInt and Connective's shared progressive-
// indexing post-blocks; ImmIndex's V+ICR/V-ICR; CountBranch;
// DirIndex's V+/V+C/V+CR) rather than sharing a function -- the
// prefetch/needsRead state these bail-outs read and write is local to
// execute()'s own body, so a shared helper would need the same
// parameters threaded through it anyway. See
// docs/phase2_arm_inventory.md step 9 and git history for what these
// two looked like before removal.

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
// ---------------------------------------------------------------------
// The floating-point operations that read NO storage operand: ST, SRT,
// SRD, SLO, SHF and E+I.  execute()'s Fp arm already drew this seam for
// itself -- these are the ones handled BEFORE the prefetch requirement,
// precisely because none of them fetches an operand -- so lifting them
// out is a move, not a redesign.
//
// The only state crossing the boundary is the indicator word, in and
// out; everything else the group does is a write through `st`.  That is
// what made this the right first cut of a 2,270-line function: ten
// values in, one out, and no participation in needsRead, the deferred
// index write, or the I/O start.  The one-write-per-instruction rule
// for `indicators` (see this file's header) is untouched -- `ind` is
// still a value threaded to a single commit in the caller.
//
// The Fp payload is an anonymous struct inside DecodedInstr, so the two
// sign-modifier bits are passed as themselves rather than as `fp`.
// ---------------------------------------------------------------------
function ActionValue#(Word64) fpStoreClass(StretchStorage st, Bit#(7) c,
                                           Bit#(1) absSign, Bit#(1) invSign,
                                           WordAddr ea, FpNum acc, Word64 accL,
                                           Word64 accS, Bool normalized, Bool noisy,
                                           Word64 ind0);
  actionvalue
    Word64 ind = ind0;
    Bool isST   = (c == fpop_ST);
    Bool isSRD  = (c == fpop_SRD);
    Bool isSLO  = (c == fpop_SLO);
    Bool isSHF  = (c == fpop_SHF);
    Bool isEplI = (c == fpop_E_PLUS_I);
    if (isST) begin
      FpNum v = fpApplySignMods(acc, absSign, invSign);
      // STORE NORMALIZES.  p.90, verbatim: "When normalized
      // operation is specified, the 48-bit operand fraction in the
      // accumulator is normalized before being placed in storage.
      // If the noisy mode is also specified, ones enter the
      // low-order fraction bit positions as they are shifted left
      // on normalization.  Normalization is suppressed when the 48
      // fraction bits are zero."  And on the next paragraph: "When
      // the exponent flag is 1, in the accumulator operand,
      // normalization, if specified, is suppressed... Thus, for
      // values with initially flagged exponent, the value in
      // storage is the same value as appears in the accumulator."
      //
      // This arm applied the sign modifiers and wrote, with no
      // normalization at all.  jb_af1c F219G catches it: ST(N) of
      // FPK77, fraction 000000000007, must store FK122's
      // ffffffffffff at -43.  Forty-eight bits, not ninety-six, for
      // the same reason LOAD is -- there is no 96-bit intermediate
      // here for noisy ones to fall into.
      Bool gen = False;
      if (normalized && v.ef == 0 && v.frac != 0) begin
        let {f48, adj} = fpNormalize48(v.frac, True, noisy);
        let {vn, g} = fpMakeExp(signExtend(fpExp(v)) + adj, f48, v.sign, v.flags);
        v = vn; gen = g;
      end
      st.writeWord(ea, fpToWord(v));
      ind = setBit(ind, ind_MOP, 1);
      ind = setResultIndicatorsFp(ind, v);
      // "If an EF of 1 is generated during normalization, the
      // exponent range indicator XPU is turned on."
      ind = setRangeIndicators(ind, fpRangeBits(v, gen, !gen && v.ef == 1));
    end else if (c == fpop_SRT) begin // SRT (STORE ROOT, pp.93, 95)
      // A store, so like ST it needs no operand fetch and is
      // handled before the prefetch requirement below.
      FpSqrtResult r = fpSqrt(acc, absSign, invSign, normalized);
      // "As with other store operations, the accumulator flag bits,
      // sign byte register bits 5-7, are placed in the flag bit
      // positions, bits 61-63 of the addressed storage location."
      st.writeWord(ea, { r.res.ef, r.res.em, r.res.es, r.res.frac,
                         r.res.sign, sbFlags(accS) });
      // "The entire accumulator and its sign byte remain unchanged."
      ind = setBit(ind, ind_MOP, 1);
      ind = setResultIndicatorsFp(ind, r.res);
      ind = setRangeIndicators(ind, fpRangeBits(r.res, r.generated, r.propagated));
      if (r.ir) ind = setBit(ind, ind_IR, 1);
      ind = setBit(ind, ind_ZM, 0);
    end else if (isSRD) begin
      // STORE ROUNDED (p.96). "The contents of the accumulator
      // after rounding are placed in the location specified by the
      // effective address." Rounding adds one to the accumulator
      // fraction AT BIT POSITION 60, which in the 96-bit IBM 12-107
      // fraction is frac[47] (IBM bit n is frac[107-n]); that gives
      // a 96-bit sum and a possible overflow bit, and "the 48
      // low-order bits are discarded" -- the kept half is IBM 12-59,
      // sum[95:48], which is exactly the fraction fpdFromWord puts
      // a single-precision word into.
      //
      // Nothing here writes the accumulator: "the entire accumulator
      // and its sign byte register remain unchanged throughout the
      // operation unless used as the effective address."
      Word64 accR = st.readAccRight();
      FpDouble da = fpdFromAcc(accL, accR, accS);
      Bit#(97) sum  = {1'b0, da.frac} + (97'b1 << 47);
      Bit#(1)  ovf  = sum[96];
      Bit#(48) hi48 = sum[95:48];
      // "The sign of the accumulator, as changed by the sign
      // modifiers, is placed in storage bit 60. The accumulator flag
      // bits are placed in storage bits 61-63."
      Bit#(1) msign = fpApplySignMods(acc, absSign, invSign).sign;
      FpNum out; Bool lc = False; Bool gen = False;
      if (da.ef == 1) begin
        // "If the value of the operand lies in the XFP or XFN range,
        // the rounding process is performed, but the exponent is not
        // changed. Normalization, if specified, is suppressed. If,
        // as a result of rounding, the fraction has an overflow bit
        // set, the overflow bit is lost."
        out = FpNum { ef: da.ef, em: da.em, es: da.es, frac: hi48,
                      sign: msign, flags: da.flags };
        lc = (ovf == 1) && !normalized;
      end else begin
        // Unnormalized: "the 48 high-order bits of the sum are placed
        // in storage bits 12-59. The overflow bit does not enter
        // storage but sets the lost carry indicator (LC) on."
        // Normalized: "the 48-bit sum is then normalized... Low-order
        // zeros are always supplied in the case of the left shift.
        // Noisy mode does not affect this operation" -- hence the
        // False for noisy whatever NM says. Feeding the 48-bit sum
        // as {hi48, 48'd0} makes fpNormalize96Wide's left shift a
        // zero-filled 48-bit shift and its overflow case the same
        // right-shift-one; its lostCarry is already "ovf and not
        // normalized", which is the rule both paragraphs describe.
        let {w96, adj, l} = fpNormalize96Wide(ovf, {hi48, 48'd0}, normalized, False);
        let {o, g} = fpMakeExp(signExtend(fpExp(fpdHead(da))) + adj,
                               w96[95:48], msign, da.flags);
        out = o; gen = g; lc = l;
      end
      st.writeWord(ea, fpToWord(out));
      // "These indicators are set as in ADD TO MEMORY": MOP, the
      // arithmetic result four, LC, the exponent range five, ZM.
      ind = setBit(ind, ind_MOP, 1);
      ind = setResultIndicatorsFp(ind, out);
      if (lc) ind = setBit(ind, ind_LC, 1);
      ind = setRangeIndicators(ind, fpRangeBits(out, gen, da.ef == 1));
      ind = setBit(ind, ind_ZM, 0);
    end else if (isSLO) begin
      // STORE LOW ORDER (p.97). "The low-order part of a
      // double-length accumulator fraction with appropriate
      // exponent is placed in the location specified by the
      // effective address." The fraction is accumulator bits
      // 60-107 -- frac[47:0] of the 96-bit IBM 12-107 fraction --
      // and "the exponent is obtained by subtracting 48 from the
      // exponent in bits 0-11 of the accumulator".
      //
      // As with SRD, nothing here writes the accumulator: "the
      // entire accumulator and sign byte register remain unchanged
      // throughout the operation unless used as the effective
      // address."
      Word64 accR = st.readAccRight();
      FpDouble da = fpdFromAcc(accL, accR, accS);
      Bit#(48) lo48 = da.frac[47:0];
      // "The accumulator sign, as modified by the sign modifiers,
      // and the accumulator flag bits, sign byte register bit
      // positions 4-7, are placed in bits 60-63 of the storage
      // word."
      Bit#(1) msign = fpApplySignMods(acc, absSign, invSign).sign;
      FpNum out; Bool gen = False;
      if (da.ef == 1) begin
        // "When the exponent, accumulator bit positions 0-11, is
        // flagged, the same exponent is set with the low-order
        // fraction when stored. The indicator settings are for
        // propagated flags. For this case normalization, if
        // specified, is suppressed."
        out = FpNum { ef: da.ef, em: da.em, es: da.es, frac: lo48,
                      sign: msign, flags: da.flags };
      end else begin
        // Unnormalized: "the low-order exponent and fraction remain
        // unchanged". Normalized: shifted left until a one is
        // leftmost, with noisy mode entering ONES from the right --
        // fpNormalize48, not fpNormalize96Wide, because SLO has no
        // low half for the latter's fill to land in.
        //
        // The -48 can underflow into a GENERATED flag, and p.97 is
        // explicit that this case differs from the propagated one:
        // "normalization, if specified, in this case does occur".
        // That is why the shift happens BEFORE fpMakeExp decides
        // whether a flag was generated, rather than being
        // suppressed by it.
        let {f48, adj} = fpNormalize48(lo48, normalized, noisy);
        let {o, g} = fpMakeExp(signExtend(fpExp(fpdHead(da))) - 48 + adj,
                               f48, msign, da.flags);
        out = o; gen = g;
      end
      st.writeWord(ea, fpToWord(out));
      // "The above indicators are set as in STORE": MOP, the
      // arithmetic result four, the exponent range four, ZM. Note
      // p.97 lists no LOST CARRY for SLO -- there is no carry out
      // of a shift -- unlike SRD.
      ind = setBit(ind, ind_MOP, 1);
      ind = setResultIndicatorsFp(ind, out);
      ind = setRangeIndicators(ind, fpRangeBits(out, gen, da.ef == 1));
      ind = setBit(ind, ind_ZM, 0);
    end else if (isSHF) begin
      // Shift Fraction (p.102): shift the accumulator fraction in
      // the direction and amount given by effective-address bits
      // 0-11 -- amount in bits 0-10 (ea[17:7]), direction in bit 11
      // (ea[6]), 0 left and 1 right -- with that direction bit read
      // as the SIGN of the shift and so "subject to modification by
      // the sign modifiers". Bits to the right of the effective
      // address (ea[5:0]) are ignored; jb_af1c F212A25 patches them
      // to ones with a CM1111 and demands the shift is unaffected.
      //
      // "Only accumulator bits 12-107 participate in the shifting;
      // all other accumulator bits remain unchanged" -- so this is
      // a 96-BIT shift across BOTH accumulator halves, not the
      // 48-bit one this arm used to do. The old version read and
      // wrote only accLeft, which left the low half untouched and
      // could never set LC from a bit that started there; jb_af1c
      // F212A12 (SHFL 107 with the low half loaded from FPK34,
      // demanding a zero result and LC ON via BZLC) is the row
      // that catches it. The exponent is not changed by this
      // operation, and neither is the sign byte.
      Word64 accRs = st.readAccRight();
      FpDouble ds = fpdFromAcc(accL, accRs, accS);
      Bit#(11) amt = ea[17:7];
      Bit#(1) dir = ea[6];
      if (absSign == 1) dir = 0;
      if (invSign == 1) dir = ~dir;
      // A shift of 96 or more clears the fraction either way, and
      // capping here keeps the "what fell off the top" expression
      // below from underflowing 96 - amt. amt is 11 bits, so 107
      // (F212A12/A24) and anything up to 2047 land in this case.
      Bit#(11) sh = (amt > 96) ? 96 : amt;
      FpDouble v = ds;
      Bool lc = False;
      if (dir == 0) begin
        // "If a one bit is shifted left beyond accumulator bit
        // position 12, it is lost and the lost carry indicator is
        // set to one." The bits that pass bit 12 are the top `sh`
        // of the fraction. At sh == 0 the shift loses nothing:
        // >> 96 is zero in BSV, which is the answer we want.
        // COVERAGE LIMIT, measured 2026-09-07: nothing transcribed
        // requires LC to be OFF after a LEFT shift. A12 wants it
        // ON; A24 is the LC-off row but shifts RIGHT, where this
        // branch never runs. Forcing `lc = True` here leaves both
        // F212A1-A11 and A12-A23 green, so the sh == 0 case below
        // (which leans on BSV's >> 96 being zero) is unguarded by
        // any test. F212D1, still to transcribe, is an LC row.
        lc = ((ds.frac >> (96 - sh)) != 0);
        v.frac = ds.frac << sh;
        // p.102: "The operation is not affected by the
        // normalization modifier. No noisy mode one bits are
        // entered on left shift if noisy mode is specified." This
        // arm used to OR ones into the vacated positions under
        // `noisy`, which the manual rules out; "zeros are inserted
        // in the bit positions which are vacated" with no
        // exception. NOW DIAGNOSTIC-PINNED, which it was not when
        // this comment was first written: every SHF in F212 is (U)
        // and none of it selects noisy mode, so nothing transcribed
        // then would have caught it -- but jb_af1c F219A1A is a
        // SHF(N) with noisy mode on, carrying the printed comment
        // "TEST NOT AFFECTED BY NOISY MODE" on both of its
        // compares and demanding FPK0's zeros in the low half. An
        // injection that fills the vacated positions halts it at
        // 021726.40.
      end else begin
        // "A one bit shifted right beyond accumulator bit position
        // 107 is lost, but no indicator is turned on" -- so no LC
        // on this side. F212A24 (SHFR 107) checks exactly that
        // with BLC,SERS "ERROR IF LC INDICATOR ON".
        v.frac = ds.frac >> sh;
      end
      st.writeWord(addrAccLeft, fpdAccLeft(v));
      st.writeWord(addrAccRight, fpdAccRight(v, accRs));
      st.writeWord(addrAccSignByte, sbWith(accS, ds.sign, sbFlags(accS)));
      FpNum vind = fpdHead(v);
      vind.frac = (v.frac == 0) ? 0 : 48'b1;
      ind = setBit(ind, ind_MOP, 0);
      ind = setResultIndicatorsFp(ind, vind);
      if (lc) ind = setBit(ind, ind_LC, 1);
      ind = setRangeIndicators(ind, fpRangeBits(vind, False, vind.ef == 1));
      ind = setBit(ind, ind_ZM, 0);
    end else if (isEplI) begin
      // Add Immediate to Exponent (p.102): bits 0-11 of the
      // effective address form a 12-bit exponent added to the
      // accumulator's exponent; fraction unchanged, normalized if
      // specified. Does not address storage.
      // p.102 makes this E+ exactly: "The operation is the same as
      // ADD TO EXPONENT, except that the addend is bits 0-11 of the
      // effective address."  So Figure 32, the ES normalization
      // rule and the 96-bit fraction all apply here too, and
      // jb_af1c F213-X drives them here the way F213A drove them
      // through E+.  The addend carries its own ES, and E+I has no
      // storage operand, so there are no sign modifiers in play.
      FpNum imm = FpNum { ef: ea[17], em: ea[16:7], es: ea[6], frac: 0, sign: 0, flags: 0 };
      Word64 accR = st.readAccRight();
      FpDouble da = fpdFromAcc(accL, accR, accS);
      FpDouble v = da; Bool gen = False; Bool prop = False;
      if (da.ef == 1 || imm.ef == 1) begin
        FpNum w = fpExpRangeWinner(fpdHead(da), imm);
        v.ef = w.ef; v.em = w.em; v.es = w.es;
        prop = True;
      end else begin
        // The sign modifiers act on the ADDEND's exponent sign,
        // and only here: p.102's "the sign modifiers are ignored
        // if either one or both of the exponents are in the XFP or
        // XFN range" applies to E+I as much as to E+, so the range
        // test above sees the UNMODIFIED immediate.  jb_af1c
        // F213-XB is the block that drives this ("THE SIGN
        // MODIFIERS APPLY TO THE SIGN OF THE EXPONENT ONLY"); its
        // sixteen sub-tests are all N-range, so they pin the
        // application but not the ignoring -- F213B's B10/B11 are
        // what pin that, for E+.
        FpNum oe = imm;
        if (absSign == 1) oe.es = 0;
        if (invSign == 1) oe.es = ~oe.es;
        Int#(14) e = signExtend(fpExp(fpdHead(da))) + signExtend(fpExp(oe));
        let {h0, g} = fpMakeExp(e, 48'b0, da.sign, da.flags);
        v.ef = h0.ef; v.em = h0.em; v.es = h0.es; gen = g;
        if (normalized && v.frac != 0 && (v.ef == 0 || v.es == 0)) begin
          let {w96, adj, lc} = fpNormalize96Wide(0, v.frac, True, noisy);
          let {h1, g2} = fpMakeExp(fpExpFull(fpdHead(v)) + adj, 48'b0, v.sign, v.flags);
          v.ef = h1.ef; v.em = h1.em; v.es = h1.es; v.frac = w96;
          gen = gen || g2;
        end
      end
      st.writeWord(addrAccLeft, fpdAccLeft(v));
      st.writeWord(addrAccRight, fpdAccRight(v, accR));
      st.writeWord(addrAccSignByte, sbWith(accS, v.sign, sbFlags(accS)));
      ind = setBit(ind, ind_MOP, 0);
      FpNum vind = fpdHead(v);
      vind.frac = (v.frac == 0) ? 0 : 48'b1;
      ind = setResultIndicatorsFp(ind, vind);
      ind = setRangeIndicators(ind, fpRangeBits(vind, gen, prop));
      ind = setBit(ind, ind_ZM, 0);
    end
    return ind;
  endactionvalue
endfunction

// ---------------------------------------------------------------------
// The floating-point operations that DO read a storage operand: the
// loads, the adds, the compares, the multiplies, the divides, LFT, *+
// and E+.  The other half of the seam fpStoreClass took -- everything
// execute()'s Fp arm reaches only after the prefetch requirement is
// satisfied, which is exactly the set that needs an operand word.
//
// Same boundary as fpStoreClass with one value added, the operand word
// itself.  Measured before the cut: over 688 lines, zero references to
// needsRead, doIdxWrite, idxWriteVal, ioStart or io.; thirty-seven
// writes through `st`; eighty-nine assignments to `ind`; and the only
// DecodedInstr fields used are the two sign-modifier bits.  The
// prefetch bail-out stays in the caller, because deciding to ask for a
// read is the caller's business -- this function is only ever entered
// once the word is in hand.
// ---------------------------------------------------------------------
function ActionValue#(Word64) fpArithClass(StretchStorage st, Bit#(7) c,
                                           Bit#(1) absSign, Bit#(1) invSign,
                                           WordAddr ea, FpNum acc, Word64 accL,
                                           Word64 accS, Bool normalized, Bool noisy,
                                           Word64 operand, Word64 ind0);
  actionvalue
    Word64 ind = ind0;
    FpNum opnd0 = fpFromWord(operand);
    FpNum opnd = fpApplySignMods(opnd0, absSign, invSign);
    ind = setBit(ind, ind_TF, opnd0.flags[2]);
    ind = setBit(ind, ind_UF, opnd0.flags[1]);
    ind = setBit(ind, ind_VF, opnd0.flags[0]);
    case (c)
      fpop_L, fpop_LWF: begin // L / LWF
        FpNum v = opnd;
        v.flags = (c == fpop_LWF) ? opnd0.flags : 0;
        Bool gen = False;
        if (normalized && v.ef == 0 && v.frac != 0) begin
          // FORTY-EIGHT BITS, NOT NINETY-SIX.  This is a
          // 48-bit fraction with no 96-bit intermediate, so
          // noisy mode's one-bits belong IN it; routing through
          // fpNormalize96 put them in a low half that is then
          // discarded, leaving zeros where the shifted-in ones
          // belong.  jb_af1c F219C1 catches it -- FPK77's
          // fraction is 000000000007, forty-five leading zeros,
          // and the answer wanted is ffffffffffff where the
          // 96-bit route gives e00000000000.
          //
          // DL and DLWF are deliberately NOT changed: for LOAD
          // DOUBLE the vacated positions ARE real accumulator
          // bits 60-107, so fpNormalize96Wide is right there.
          let {f48, adj} = fpNormalize48(v.frac, True, noisy);
          let {vn, g} = fpMakeExp(signExtend(fpExp(v)) + adj, f48, v.sign, v.flags);
          v = vn; gen = g;
        end
        st.writeWord(addrAccLeft, fpAccLeft(v, accL));
        st.writeWord(addrAccSignByte, fpSignByte(v, accS));
        ind = setBit(ind, ind_MOP, 0);
        ind = setResultIndicatorsFp(ind, v);
        ind = setRangeIndicators(ind, fpRangeBits(v, gen, !gen && v.ef == 1));
        ind = setBit(ind, ind_ZM, 0);
      end
      fpop_LFT: begin // LFT (LOAD FACTOR, p.98)
        // "The operand specified by the effective address is
        // placed in the factor register, FT.  The accumulator
        // does not participate in the operation and remains
        // unchanged."  So this is LOAD with word 14 as the
        // destination and no sign byte: exponent and fraction to
        // FT bits 0-59, the sign-modified sign to FT bit 60, and
        // "FT bits 61-63 are set to zero" -- which is why
        // v.flags is cleared rather than taken from the operand
        // the way LWF takes it.  fpMakeExp passes flags through
        // unaltered, so the zero survives the normalized path.
        //
        // FT IS THE ONLY REGISTER NO OTHER OPERATION TOUCHES:
        // p.98, "LOAD FACTOR is the only operation which changes
        // the contents of FT as an integral part of its
        // performance.  FT is not changed by any other operation
        // unless it is addressed explicitly."
        FpNum v = opnd;
        v.flags = 0;
        Bool gen = False;
        // "If a shift of 48 or more is required, normalization is
        // suppressed and the order of magnitude zero is stored in
        // bits 0-59."  A 48-bit fraction needs a shift of 48 or
        // more exactly when it is ZERO -- any one-bit is within
        // 47 places of the top -- so LOAD's `frac != 0` guard is
        // that rule, not merely an optimization: a zero fraction
        // skips normalization and keeps the operand's own
        // exponent, which is what an order-of-magnitude zero is.
        if (normalized && v.ef == 0 && v.frac != 0) begin
          // FORTY-EIGHT BITS, NOT NINETY-SIX.  This is a
          // 48-bit fraction with no 96-bit intermediate, so
          // noisy mode's one-bits belong IN it; routing through
          // fpNormalize96 put them in a low half that is then
          // discarded, leaving zeros where the shifted-in ones
          // belong.  jb_af1c F219C1 catches it -- FPK77's
          // fraction is 000000000007, forty-five leading zeros,
          // and the answer wanted is ffffffffffff where the
          // 96-bit route gives e00000000000.
          //
          // DL and DLWF are deliberately NOT changed: for LOAD
          // DOUBLE the vacated positions ARE real accumulator
          // bits 60-107, so fpNormalize96Wide is right there.
          let {f48, adj} = fpNormalize48(v.frac, True, noisy);
          let {vn, g} = fpMakeExp(signExtend(fpExp(v)) + adj, f48, v.sign, v.flags);
          v = vn; gen = g;
        end
        st.writeWord(addrFactor, fpToWord(v));
        ind = setBit(ind, ind_MOP, 0);
        ind = setResultIndicatorsFp(ind, v);
        // p.98 lists XPU alongside XPFP/XPH/XPL where LOAD's list
        // has only the first three -- LOAD cannot drive an
        // exponent down, LFT's normalization can.  fpRangeBits
        // already derives XPU from `generated && es == 1`, so the
        // call is LOAD's unchanged and the difference is in which
        // inputs can reach it, not in the function.
        ind = setRangeIndicators(ind, fpRangeBits(v, gen, !gen && v.ef == 1));
        ind = setBit(ind, ind_ZM, 0);
      end
      fpop_DL, fpop_DLWF: begin // DL / DLWF (p.96)
        // LOAD DOUBLE "is the same as LOAD except that the
        // accumulator bits 60-107 are set to zero": the exponent
        // and fraction replace bits 0-59, bits 60-107 -- the low
        // half of the double-precision 96-bit fraction -- are
        // cleared, and bits 108-127 remain unchanged. DLWF
        // additionally takes the addressed operand's flag bits
        // into the sign byte's bits 5-7 (and the TF/UF/VF
        // indicators), where DL zeroes them; that is the same
        // difference L and LWF already have.
        //
        // In the accumulator's 128 magnitude bits, IBM bit n is
        // bit 127-n, so the fraction's low half lands as the
        // left half's bits 60-63 and the right half's 64-107,
        // and 108-127 are the right half's low 20 bits.
        //
        // Normalization is over the WHOLE 96-bit fraction. With
        // the low half zero the shift can still only be up to 47
        // places (the leading one is in the high half), so the
        // exponent adjustment matches LOAD's -- but noisy mode
        // does differ: its one-bits go into the vacated
        // low-order positions, which here are real accumulator
        // bits 60-107 rather than bits that fall off the end.
        // That is why this uses fpNormalize96Wide.
        FpNum v = opnd;
        v.flags = (c == fpop_DLWF) ? opnd0.flags : 0;
        Bit#(96) f96 = {v.frac, 48'b0};
        Bool gen = False;
        if (normalized && v.ef == 0 && v.frac != 0) begin
          let {w96, adj, lc} = fpNormalize96Wide(0, f96, True, noisy);
          let {vn, g} = fpMakeExp(signExtend(fpExp(v)) + adj, w96[95:48], v.sign, v.flags);
          v = vn; gen = g; f96 = w96;
        end
        Word64 accR = st.readAccRight();
        st.writeWord(addrAccLeft, { v.ef, v.em, v.es, v.frac, f96[47:44] });
        st.writeWord(addrAccRight, { f96[43:0], accR[19:0] });
        st.writeWord(addrAccSignByte, fpSignByte(v, accS));
        ind = setBit(ind, ind_MOP, 0);
        ind = setResultIndicatorsFp(ind, v);
        ind = setRangeIndicators(ind, fpRangeBits(v, gen, !gen && v.ef == 1));
        ind = setBit(ind, ind_ZM, 0);
      end
      fpop_D_PLUS, fpop_D_PLUS_MG: begin // D+ / D+MG (p.95)
        // ADD DOUBLE works on the accumulator's whole 96-bit
        // fraction, IBM bits 12-107, against a storage operand
        // extended with 48 low-order zeros. Bits 108-127 are
        // outside the fraction and are carried through
        // untouched, exactly as for DL.
        Word64 accR = st.readAccRight();
        FpDouble da = fpdFromAcc(accL, accR, accS);
        FpDouble db = fpdFromWord(operand);
        db.sign = opnd.sign;   // the sign modifiers, already applied
        FpdResult r = fpAddDouble(da, db, normalized, noisy, c == fpop_D_PLUS_MG);
        // ADD DOUBLE TO MAGNITUDE keeps the accumulator's OWN
        // sign whatever the sum did -- "the sign remains
        // unchanged" for a positive sum, and for a forced zero
        // "the sign and exponent of the accumulator operand
        // remain equal to the original" (p.95). fpAddDouble
        // forced a.sign positive to decide the forced zero, so
        // put the real one back here, exactly as the +MG arm
        // does with acc.sign.
        if (c == fpop_D_PLUS_MG) r.res.sign = sbSign(accS);
        st.writeWord(addrAccLeft, fpdAccLeft(r.res));
        st.writeWord(addrAccRight, fpdAccRight(r.res, accR));
        // ADD leaves sign byte bits 0-3 and 5-7 alone and replaces
        // only bit 4 with the sum's sign (p.86), and D+ is "similar
        // to ADD". Take the flag bits from accS and say so, rather
        // than from r.res: on the unflagged path r.res.flags is
        // the accumulator's own and the two agree, but the FLAGGED
        // path returns one operand WHOLE, so when the survivor is
        // the storage operand r.res.flags is ITS flags. jb_af1c
        // F208C2 is exactly that case -- an all-ones accumulator
        // (flags 111) plus FPK0 (flags 000) -- and the listing
        // demands 111 afterward. The TF/UF/VF INDICATORS are a
        // separate thing and do come from the addressed operand
        // (p.87, set above for every FP op with an operand).
        st.writeWord(addrAccSignByte, sbWith(accS, r.res.sign, sbFlags(accS)));
        ind = setBit(ind, ind_MOP, 0);
        // The result indicators only ever ask whether the result
        // fraction is zero and what its sign is, so they are fed
        // a narrow view whose fraction is zero exactly when the
        // 96-bit one is.
        FpNum vind = fpdHead(r.res);
        vind.frac = (r.res.frac == 0) ? 0 : 48'b1;
        ind = setResultIndicatorsFp(ind, vind);
        if (r.lc) ind = setBit(ind, ind_LC, 1);
        if (r.ls) ind = setBit(ind, ind_LS, 1);
        if (r.psh) ind = setBit(ind, ind_PSH, 1);
        ind = setRangeIndicators(ind, fpRangeBits(vind, r.generated, r.propagated));
        ind = setBit(ind, ind_ZM, 0);
      end
      fpop_F_PLUS: begin // F+ (ADD TO FRACTION, p.101)
        // "The operation is the same as ADD DOUBLE except that
        // the exponent of the operand in the accumulator is used
        // for both the addressed operand and the operand in the
        // accumulator." So the storage operand keeps its
        // fraction, its sign -- modified by the sign modifiers
        // before the addition, exactly as for D+ -- and its own
        // data FLAGS; only ef/em/es are replaced.
        //
        // p.101 also says "when the accumulator operand is a
        // value in the XFP or XFN range, the fraction addition
        // is not performed." That needs no arm of its own:
        // forcing the accumulator's exponent onto the storage
        // operand puts BOTH operands in the SAME range with
        // EQUAL exponents, and fpAddDouble's like-flagged
        // TIE-BREAK -- `(fpExp(hb) > fpExp(ha)) ? b : a`, which
        // overwrites the range ladder above it rather than
        // being an else on it -- then returns `a`, the
        // accumulator, because the comparison is strict.
        // jb_af1c F212XA1-XA3 (an XFP accumulator) and XA7-XA9
        // (XFN) are exactly that case and demand the
        // accumulator back untouched; relaxing the `>` to `>=`
        // halts XA1 at 016654.40. F+ is the only op that makes
        // the two exponents equal, so those six rows are the
        // only cover that comparison has at equality.
        // Conversely XA4 pairs an N accumulator with an XFP
        // OPERAND and DOES demand the addition -- which is why
        // the exponent must be forced BEFORE the range test,
        // not after; dropping the substitution halts XA4 at
        // 016676.40.
        Word64 accR = st.readAccRight();
        FpDouble da = fpdFromAcc(accL, accR, accS);
        FpDouble db = fpdFromWord(operand);
        db.sign = opnd.sign;   // the sign modifiers, already applied
        db.ef = da.ef; db.em = da.em; db.es = da.es;
        FpdResult r = fpAddDouble(da, db, normalized, noisy, False);
        st.writeWord(addrAccLeft, fpdAccLeft(r.res));
        st.writeWord(addrAccRight, fpdAccRight(r.res, accR));
        // Sign byte: bit 4 from the sum, flags from accS. NOTE
        // that for F+, unlike D+, sbFlags(accS) and r.res.flags
        // are provably the SAME thing: fpAddDouble's unflagged
        // path builds its result with `flags: a.flags` always,
        // and the exponent substitution above makes any flagged
        // pair like-flagged with EQUAL exponents, so the
        // tie-break returns `a`. There is no F+ input that can
        // separate them, and jb_af1c F212XC1 does not, despite
        // addressing an operand whose flag bits are 111 against
        // a just-zeroed accumulator ("MEM FLAGS+7") -- injecting
        // r.res.flags here leaves XC green. accS is written for
        // uniformity with D+, where the two DO differ (its
        // flagged path can return the storage operand whole) and
        // where F208C2 pins the choice.
        st.writeWord(addrAccSignByte, sbWith(accS, r.res.sign, sbFlags(accS)));
        ind = setBit(ind, ind_MOP, 0);
        FpNum vind = fpdHead(r.res);
        vind.frac = (r.res.frac == 0) ? 0 : 48'b1;
        ind = setResultIndicatorsFp(ind, vind);
        // F212XA6 adds 000000000001_ffffffffffff to
        // ffffffffffff_000000000000 and demands high 000...0,
        // low fff...f, an UNCHANGED exponent of +2 and LC ON:
        // the carry out of the 96-bit fraction is simply lost.
        if (r.lc) ind = setBit(ind, ind_LC, 1);
        // LS is reachable for F+ -- an exact cancellation gives a
        // zero result fraction with non-zero operands -- but no
        // row in F212-X produces one. PSH is not reachable at
        // all: fpAddDouble computes it from |ea - eb|, and the
        // substitution above forces that difference to zero, so
        // `adiff > 48` is never true (nor is the `adiff > 95`
        // early return). The line stays anyway, because keeping
        // this arm shaped like D+'s is worth more than pruning
        // dead uniformity -- but it is dead, not merely untested.
        if (r.ls) ind = setBit(ind, ind_LS, 1);
        if (r.psh) ind = setBit(ind, ind_PSH, 1);
        ind = setRangeIndicators(ind, fpRangeBits(vind, r.generated, r.propagated));
        ind = setBit(ind, ind_ZM, 0);
      end
      fpop_PLUS, fpop_PLUS_MG: begin // + / +MG
        FpResult r = fpAdd(acc, opnd, normalized, noisy, c == fpop_PLUS_MG, False);
        // ADD TO MAGNITUDE (p.88): only the accumulator's MAGNITUDE
        // takes part, and the result keeps the accumulator's own
        // sign -- a forced zero included. jb_af1c F205B checks the
        // sign byte after every +MG/+MGA/-MG/-MGA: bit 1 whenever
        // the accumulator was loaded with LN, whatever the sum.
        if (c == fpop_PLUS_MG) r.res.sign = acc.sign;
        st.writeWord(addrAccLeft, fpAccLeft(r.res, accL));
        // Sign byte bits 5-7 are the accumulator's own, for the
        // same reason as D+ below: p.86 is ADD's own page and says
        // bits 0-3 and 5-7 "remain unchanged", but fpAdd's FLAGGED
        // path returns one operand WHOLE, so r.res.flags is the
        // STORAGE operand's whenever that operand is the survivor.
        // Proven for D+ by jb_af1c F208C2; NOT proven here, because
        // jb_af1c has no "TEST UNCHANGED REGISTERS" routine for
        // plain ADD -- F203 ends at F203B, the exponent-range
        // indicator test, and F204 begins straight after. F205C
        // checks +MG's sign byte bits 0-3 only, not 5-7.
        st.writeWord(addrAccSignByte, sbWith(accS, r.res.sign, sbFlags(accS)));
        ind = setBit(ind, ind_MOP, 0);
        ind = setResultIndicatorsFp(ind, r.res);
        if (r.lc) ind = setBit(ind, ind_LC, 1);
        if (r.ls) ind = setBit(ind, ind_LS, 1);
        if (r.psh) ind = setBit(ind, ind_PSH, 1);
        ind = setRangeIndicators(ind, fpRangeBits(r.res, r.generated, r.propagated));
        ind = setBit(ind, ind_ZM, 0);
      end
      fpop_M_PLUS, fpop_M_PLUS_MG: begin // M+ / M+MG
        FpNum a = acc;
        FpNum b = opnd0; if (absSign == 1) b.sign = 0;
        // ADD MAGNITUDE TO MEMORY (p.89): "the accumulator operand
        // sign is assumed positive BEFORE the negative sign
        // modification occurs". The negative-sign modifier here
        // is the one the M-MG mnemonic sets (invSign), NOT
        // the (N) in M+MG(N), which is the normalization
        // modifier: M-MG adds a NEGATIVE accumulator operand,
        // not the negation of whatever sign it was loaded with.
        // (fpAdd leaves this to the caller for the to-memory
        // direction; see its header.)
        if (c == fpop_M_PLUS_MG) a.sign = 0;
        if (invSign == 1) a.sign = ~a.sign;
        FpResult r = fpAdd(b, a, normalized, noisy, c == fpop_M_PLUS_MG, True);
        FpNum v = r.res; v.flags = opnd0.flags;
        // ADD MAGNITUDE TO MEMORY keeps the ADDRESSED operand's own
        // original sign, whatever the sum's: only its magnitude took
        // part. The mirror of p.88's rule for the accumulator-
        // changing direction -- "in an ADD TO MAGNITUDE operation,
        // the sign byte register bit position 4 never changes" --
        // and of the +MG line above. It covers the forced zero
        // (p.83: "the unmodified original fraction sign of the
        // addressed operand in ADD MAGNITUDE TO MEMORY", which is
        // opnd0's, NOT b's after the absolute modifier) and the
        // ordinary sum alike. jb_af1c F206B19/B24: M+MGA and M-MGA
        // of a NEGATIVE memory operand, whose sign A makes positive
        // for the arithmetic; the sum is positive, and the sign
        // stored is still the negative one. Storing the sum's sign
        // halted at B19's BB.
        if (c == fpop_M_PLUS_MG) v.sign = opnd0.sign;
        st.writeWord(ea, fpToWord(v));
        ind = setBit(ind, ind_MOP, 1);
        ind = setResultIndicatorsFp(ind, v);
        if (r.lc) ind = setBit(ind, ind_LC, 1);
        if (r.ls) ind = setBit(ind, ind_LS, 1);
        if (r.psh) ind = setBit(ind, ind_PSH, 1);
        ind = setRangeIndicators(ind, fpRangeBits(v, r.generated, r.propagated));
        ind = setBit(ind, ind_ZM, 0);
      end
      fpop_K, fpop_KMG, fpop_KR, fpop_KMGR: begin // K / KMG / KR / KMGR
        Bool magnitude = (c == fpop_KMG || c == fpop_KMGR);
        Bool range = (c == fpop_KR || c == fpop_KMGR);
        Int#(2) cmp = fpCompare(acc, opnd, magnitude, normalized, noisy);
        ind = setBit(ind, ind_MOP, 0);
        Int#(13) ea_ = fpExp(acc), eb_ = fpExp(opnd);
        Int#(14) d = signExtend(ea_) - signExtend(eb_);
        if (acc.ef == 0 && opnd.ef == 0 && ((d > 48) || (d < -48))) ind = setBit(ind, ind_PSH, 1);
        if (!range) begin
          ind = setBit(ind, ind_AL, pack(cmp < 0));
          ind = setBit(ind, ind_AE, pack(cmp == 0));
          ind = setBit(ind, ind_AH, pack(cmp > 0));
        end else if (ind[63 - ind_AH] == 1) begin
          // KR/KMGR (Compare for Range), Ref. Manual p.91: when
          // the gate AH is on, set AE to "accumulator low"
          // (acc < operand). AL and AH are NOT changed -- AH is
          // the input gate, not a result; and when AH is off the
          // comparison indicators are left unchanged (the
          // fall-through of this `else if`). Verified against
          // jb_af1c F202G11-18 (programs/fp_compare_f202g.strap).
          ind = setBit(ind, ind_AE, pack(cmp < 0));
        end
      end
      fpop_STAR: begin // *
        FpResult r = fpMul(acc, opnd, normalized, noisy);
        st.writeWord(addrAccLeft, fpAccLeft(r.res, accL));
        st.writeWord(addrAccSignByte, fpSignByte(r.res, accS));
        ind = setBit(ind, ind_MOP, 0);
        ind = setResultIndicatorsFp(ind, r.res);
        ind = setRangeIndicators(ind, fpRangeBits(r.res, r.generated, r.propagated));
        ind = setBit(ind, ind_ZM, pack(r.zm));
      end
      fpop_SLASH: begin // / (DIVIDE, pp.93-94)
        // "The operand in the left half of the accumulator, the
        // dividend, is divided by the addressed operand, the
        // divisor. ... The quotient exponent and fraction replace
        // accumulator bits 0-59.  Accumulator bits 60-127 remain
        // unchanged.  The quotient sign replaces the accumulator
        // sign in bit position 4 of the sign byte register.  No
        // remainder is retained by this operation."
        //
        // So the accumulator's RIGHT word is never written, and
        // fpAccLeft carries IBM 60-63 through -- the same shape
        // MULTIPLY has, and the reason / needs no readAccRight.
        FpDivResult r = fpDiv(acc, opnd, normalized, noisy);
        ind = setBit(ind, ind_MOP, 0);
        if (r.zd) begin
          // p.93: "When division is suppressed because of a zero
          // divisor, the accumulator and the sign byte register
          // remain unchanged.  The data flag and MOP indicators
          // will be set but the arithmetic result and exponent
          // range indicators are not changed."  Nothing is
          // written -- not even the same value back -- and ZM is
          // left alone too, since p.94 turns ZM off "except for
          // the case of a zero divisor".
          ind = setBit(ind, ind_ZD, 1);
        end else begin
          st.writeWord(addrAccLeft, fpAccLeft(r.res, accL));
          st.writeWord(addrAccSignByte, fpSignByte(r.res, accS));
          // LZC is IBM bits 17-23 of word 7 and shares that word
          // with the all-ones count at 44-50, which has to
          // survive; IBM bit n is model bit 63-n, so 17-23 is
          // [46:40].  p.94: the count "remains available for
          // program use until the LZC is changed by integer
          // multiplication, LOAD TRANSIT, division or connective
          // operations".  NOTHING IN F217 READS IT, nor PF which
          // is derived from it -- both are manual-only here.
          Word64 zoc = st.readZerosOnesCounts();
          st.writeWord(addrLeftZerosCount, { zoc[63:47], r.lzc, zoc[39:0] });
          ind = setResultIndicatorsFp(ind, r.res);
          ind = setRangeIndicators(ind, fpRangeBits(r.res, r.generated, r.propagated));
          if (r.pf) ind = setBit(ind, ind_PF, 1);
          ind = setBit(ind, ind_ZM, 0);
        end
      end
      fpop_R_SLASH: begin // R/ (RECIPROCAL DIVIDE, p.94)
        // "The operand specified by the effective address, the
        // dividend, is divided by the operand in the left half of
        // the accumulator, the divisor.  The sign of the dividend
        // is modified by the sign modifiers prior to the
        // division. ... The division process is the same as the
        // process described in DIVIDE with the exception of the
        // interchange of the operands used for dividends and
        // divisor."
        //
        // So the whole of R/ is fpDiv with its two arguments the
        // other way round.  The sign modifiers still land on the
        // ADDRESSED operand, which here is the dividend rather
        // than the divisor, and `opnd` already carries them.
        FpDivResult r = fpDiv(opnd, acc, normalized, noisy);
        ind = setBit(ind, ind_MOP, 0);
        if (r.zd) begin
          // The zero divisor is now the ACCUMULATOR's fraction.
          // Nothing is written, as in DIVIDE; jb_af1c F217XA8
          // checks it from that side, asking that "the divisor
          // remains in the accumulator".
          ind = setBit(ind, ind_ZD, 1);
        end else begin
          st.writeWord(addrAccLeft, fpAccLeft(r.res, accL));
          // Spelled out rather than fpSignByte'd, because for R/
          // the result's flag bits come from the DIVIDEND, which
          // is the storage operand -- the accumulator's own flags
          // are what must survive, as everywhere else.  For / the
          // two happen to coincide.
          st.writeWord(addrAccSignByte, sbWith(accS, r.res.sign, sbFlags(accS)));
          Word64 zoc = st.readZerosOnesCounts();
          st.writeWord(addrLeftZerosCount, { zoc[63:47], r.lzc, zoc[39:0] });
          ind = setResultIndicatorsFp(ind, r.res);
          ind = setRangeIndicators(ind, fpRangeBits(r.res, r.generated, r.propagated));
          if (r.pf) ind = setBit(ind, ind_PF, 1);
          ind = setBit(ind, ind_ZM, 0);
        end
      end
      fpop_D_SLASH: begin // D/ (DIVIDE DOUBLE, p.94)
        // "The quotient exponent and fraction replace accumulator
        // bits 0-60.  Accumulator bits 61-107 are set to zero.
        // The sign of the quotient replaces the accumulator sign.
        // Accumulator bits 108-127 remain unchanged.  The
        // remainder is placed in the remainder register, RM
        // address 13.  The original accumulator sign becomes the
        // sign of the remainder RM register bit 60.  The flag
        // bits 61-63 of the remainder register are set to zero."
        //
        // So the accumulator's left word carries the exponent,
        // FORTY-EIGHT quotient bits and then the FORTY-NINTH in
        // IBM 60, with 61-63 zero; the right word is zeroed
        // through IBM 107 and keeps 108-127.  That 49th bit is
        // what makes the field 0-60 rather than DIVIDE's 0-59,
        // and jb_af1c F217WA checks it in every sub-test.
        Word64 accR = st.readAccRight();
        FpDouble da = fpdFromAcc(accL, accR, accS);
        FpDivDblResult r = fpDivDouble(da, opnd, normalized, noisy);
        ind = setBit(ind, ind_MOP, 0);
        if (r.zd) begin
          // As in DIVIDE: nothing is written and the result and
          // range indicators are left alone.
          ind = setBit(ind, ind_ZD, 1);
        end else begin
          st.writeWord(addrAccLeft,
                       { r.res.ef, r.res.em, r.res.es, r.res.frac, r.q49, 3'b0 });
          st.writeWord(addrAccRight, { 44'b0, accR[19:0] });
          st.writeWord(addrAccSignByte, fpSignByte(r.res, accS));
          // RM: exponent and fraction in bits 0-59, the ORIGINAL
          // accumulator sign in bit 60, flags 61-63 zero.
          st.writeWord(addrRemainder,
                       { r.rem.ef, r.rem.em, r.rem.es, r.rem.frac, r.rem.sign, 3'b0 });
          Word64 zoc = st.readZerosOnesCounts();
          st.writeWord(addrLeftZerosCount, { zoc[63:47], r.lzc, zoc[39:0] });
          FpNum vind = r.res;
          vind.frac = (r.res.frac == 0 && r.q49 == 0) ? 0 : 48'b1;
          ind = setResultIndicatorsFp(ind, vind);
          ind = setRangeIndicators(ind, fpRangeBits(r.res, r.generated, r.propagated));
          if (r.pf) ind = setBit(ind, ind_PF, 1);
          if (r.lc) ind = setBit(ind, ind_LC, 1);
          if (r.ru) ind = setBit(ind, ind_RU, 1);
          ind = setBit(ind, ind_ZM, 0);
        end
      end
      fpop_D_STAR: begin // D* (multiply double, p.97): "the same
                        // as MULTIPLY, except that the 96-bit
                        // product fraction is placed in
                        // accumulator bits 12-107" -- so where *
                        // keeps the product's high half and drops
                        // the rest, D* keeps all of it, and IBM
                        // 60-63 (which * preserves) become part
                        // of the result fraction.
        // Accumulator bits 108-127 lie outside the product field
        // and survive; fpdAccRight carries oldRight[19:0]
        // through.  jb_af1c F214XB1/XB2 check exactly that, with
        // a CT0101/CT1010 over R 44-63 = IBM 108-127.
        //
        // The MULTIPLIER is taken as the 48-bit accumulator
        // fraction of bits 12-59, as under MULTIPLY, on the
        // reading that p.97 changes only where the product GOES.
        // NOTHING IN F214-X CHECKS THAT, and structurally cannot:
        // every XA sub-test enters with IBM 60-107 already zero
        // (INJ1, which never wrote the right word, still passed
        // XA1's low-half check against zero), and with a zero low
        // half a 96-bit multiplier gives the identical product;
        // XB's accumulator low half is NOT zero but XB inspects
        // only IBM 108-127 and the sign byte. Manual-only until a
        // later block loads the low half with DL and multiplies.
        Word64 accR = st.readAccRight();
        FpdResult r = fpMulDouble(acc, opnd, normalized, noisy);
        st.writeWord(addrAccLeft, fpdAccLeft(r.res));
        st.writeWord(addrAccRight, fpdAccRight(r.res, accR));
        st.writeWord(addrAccSignByte, sbWith(accS, r.res.sign, r.res.flags));
        ind = setBit(ind, ind_MOP, 0);
        // The indicators want a 48-bit stand-in; only "is the
        // fraction zero" matters and that is a 96-bit question.
        FpNum rind = fpdHead(r.res);
        rind.frac = (r.res.frac == 0) ? 0 : 48'b1;
        ind = setResultIndicatorsFp(ind, rind);
        ind = setRangeIndicators(ind, fpRangeBits(rind, r.generated, r.propagated));
        ind = setBit(ind, ind_ZM, pack(r.zm));
      end
      fpop_STAR_PLUS: begin // *+ (MULTIPLY AND ADD, pp.98-99)
        // "The operand in the FT register, designated as the
        // multiplicand, is multiplied by the operand specified by
        // the effective address, designated as the multiplier.
        // The product is added to the contents of the
        // accumulator, bits 0-107.  The sum exponent and fraction
        // replace accumulator bits 0-107.  The sign of the sum
        // replaces the accumulator sign, sign byte register bit
        // 4.  Accumulator bits 108-127 remain unchanged."
        //
        // So it is fpMulDouble feeding fpAddDouble, and the
        // manual says so: "the intermediate product fraction
        // remains unnormalized throughout the addition" and
        // "subsequent to the multiplication, an addition is
        // performed similar to that described in ADD DOUBLE".
        //
        // THE ARGUMENT ORDER OF THE MULTIPLY IS LOAD-BEARING, and
        // it is the one place *+ differs from MULTIPLY.  p.99:
        // "When both operands are in the XFP range or both in the
        // XFN range, the product exponent is the exponent of the
        // operand specified by the EFFECTIVE ADDRESS" -- where
        // Fig.32, and so fpMul and D*, give it to the accumulator
        // side.  fpExpRangeWinner resolves a same-range pair to
        // its FIRST argument, so passing (opnd, ftv) is exactly
        // that rule and nothing else in fpMulDouble is
        // asymmetric: the sign is an xor, the fraction a product,
        // and the unflagged exponent a sum.
        //
        // Note this is NOT only a tie-break here.  p.99 gives the
        // effective address the exponent whenever both operands
        // share a flagged range, whatever their magnitudes --
        // which is why the rule cannot be expressed by ordering
        // the arguments to a comparison.
        Word64 accR = st.readAccRight();
        FpDouble da = fpdFromAcc(accL, accR, accS);
        FpNum ftv = fpFromWord(st.readFactor());
        // Normalization and noisy mode belong to the ADDITION
        // only: p.99, "the intermediate product fraction remains
        // unnormalized throughout the addition", and noisy's
        // one-bits enter "during the left shifting associated
        // with normalization" of the sum.
        FpdResult m = fpMulDouble(opnd, ftv, False, False);
        FpdResult r = fpAddDouble(da, m.res, normalized, noisy, False);
        st.writeWord(addrAccLeft, fpdAccLeft(r.res));
        st.writeWord(addrAccRight, fpdAccRight(r.res, accR));
        // The sign byte takes the sum's sign and the ACCUMULATOR's
        // flag bits, as ADD DOUBLE does -- so r.res.flags never
        // reaches storage and m.res.flags (which fpMulDouble takes
        // from its first argument, here the storage operand) is
        // inert.  Said explicitly because it looks like it matters.
        st.writeWord(addrAccSignByte, sbWith(accS, r.res.sign, sbFlags(accS)));
        ind = setBit(ind, ind_MOP, 0);
        FpNum vind = fpdHead(r.res);
        vind.frac = (r.res.frac == 0) ? 0 : 48'b1;
        ind = setResultIndicatorsFp(ind, vind);
        if (r.lc) ind = setBit(ind, ind_LC, 1);
        if (r.ls) ind = setBit(ind, ind_LS, 1);
        if (r.psh) ind = setBit(ind, ind_PSH, 1);
        // p.99's generated/propagated rule falls out of the
        // composition rather than needing code.  "Generated if all
        // operands are initially in the N range" is fpAddDouble's
        // unflagged path (gen from fpMakeExp, propagated False);
        // "or if the intermediate product has a value in the XFN
        // range with a propagated exponent flag while the
        // accumulator operand is in the N range but the sum has EF
        // of 1, ES of 1 owing to final normalization" is its
        // FLAGGED path, where an unflagged survivor still
        // normalizes and fpMakeExp reports the underflow -- and
        // fpRangeBits' propagated arm requires es == 0, so an
        // es == 1 result falls through to the generated one.
        // "All other cases lead to a propagated EF of 1" is
        // r.propagated = (res.ef == 1).  Nothing in F216A checks
        // an indicator, so none of this is covered there.
        ind = setRangeIndicators(ind, fpRangeBits(vind, r.generated, r.propagated));
        // p.99: "If the final result, after addition, is an order
        // of magnitude zero with exponent greater than -1024 this
        // indicator will be turned on, otherwise, if on, it will
        // be turned off."  Unlike MULTIPLY's ZM this carries no
        // `normalized` term.
        ind = setBit(ind, ind_ZM,
                     pack((r.res.frac == 0) && (fpExpFull(vind) > -1024)));
      end
      fpop_E_PLUS: begin // E+ (add to exponent, p.102): the
                        // addressed operand's exponent (its sign
                        // subject to the sign modifiers) is added
                        // to the accumulator's exponent; fraction
                        // and sign of the operand are ignored.
        // NORMALIZATION HERE IS 96-BIT.  p.102: "When normalized
        // operation is specified, the accumulator exponent and
        // fraction bits 12-107 are normalized.  Accumulator bits
        // 108-127 and the sign byte register remain unchanged."
        // jb_af1c F213A12 is what forces it: a high half of
        // 000fffffffff over a low half of ffffffffffff, and after
        // a normalized E+ the listing demands high ffffffffffff
        // (FK57) and LOW fffffffff000 (FK48) -- the twelve
        // leading zeros leave the whole IBM 12-107 fraction,
        // pulling the low half up, and the exponent drops by 12
        // from +1073 to FK57's +1061.  A13 checks it again
        // independently with a shift of 10.  This arm used to
        // normalize {frac, 48'b0} and never wrote addrAccRight.
        Word64 accR = st.readAccRight();
        FpDouble da = fpdFromAcc(accL, accR, accS);
        FpDouble v = da; Bool gen = False; Bool prop = False;
        if (da.ef == 1 || opnd0.ef == 1) begin
          // "When the exponents of either or both operands lie in
          // the XFP or XFN range, the rules for exponent handling
          // follow the definitions given under MULTIPLY" -- Fig.32
          // -- and "when either operand has EF of 1, the result
          // will have a propagated EF of 1 and normalization, if
          // specified, is suppressed. In this case the result
          // fraction is the original accumulator fraction."
          //
          // THE RANGE TEST USES THE UNMODIFIED OPERAND. p.102:
          // "the sign modifiers are ignored if either one or both
          // of the exponents are in the XFP or XFN range" -- and
          // es is exactly what separates XFP from XFN, so applying
          // a modifier first would RECLASSIFY the operand and pick
          // the wrong winner.
          //
          // The winner's exponent is taken WHOLE rather than
          // recomputed: routing it through fpMakeExp would
          // re-derive ef/em/es from an integer, and jb_af1c
          // F213A3 pairs the XFP boundary value +2047 with an XFN
          // -2047 precisely there.
          FpNum w = fpExpRangeWinner(fpdHead(da), opnd0);
          v.ef = w.ef; v.em = w.em; v.es = w.es;
          prop = True;
        end else begin
          FpNum oe = opnd0;
          if (absSign == 1) oe.es = 0;
          if (invSign == 1) oe.es = ~oe.es;
          Int#(14) e = signExtend(fpExp(fpdHead(da))) + signExtend(fpExp(oe));
          let {h0, g} = fpMakeExp(e, 48'b0, da.sign, da.flags);
          v.ef = h0.ef; v.em = h0.em; v.es = h0.es; gen = g;
          // "When both operands have EF of 0, the result exponent
          // may have a GENERATED EF of 1. For this case
          // normalization, if specified, occurs if ES is 0 and is
          // suppressed if ES is 1." So a generated EF only
          // suppresses normalization on the NEGATIVE side; the
          // arm previously suppressed it for either sign.
          if (normalized && v.frac != 0 && (v.ef == 0 || v.es == 0)) begin
            let {w96, adj, lc} = fpNormalize96Wide(0, v.frac, True, noisy);
            // fpExpFull, not fpExp: at this point v's exponent may
            // already carry a GENERATED EF (A12's +1073 is held as
            // EF 1 / EM 49), and the shift has to come off the
            // whole value, not off the ten-bit field.
            let {h1, g2} = fpMakeExp(fpExpFull(fpdHead(v)) + adj,
                                     48'b0, v.sign, v.flags);
            v.ef = h1.ef; v.em = h1.em; v.es = h1.es; v.frac = w96;
            gen = gen || g2;
          end
        end
        st.writeWord(addrAccLeft, fpdAccLeft(v));
        st.writeWord(addrAccRight, fpdAccRight(v, accR));
        st.writeWord(addrAccSignByte, sbWith(accS, v.sign, sbFlags(accS)));
        ind = setBit(ind, ind_MOP, 0);
        FpNum vind = fpdHead(v);
        vind.frac = (v.frac == 0) ? 0 : 48'b1;
        ind = setResultIndicatorsFp(ind, vind);
        ind = setRangeIndicators(ind, fpRangeBits(vind, gen, prop));
        ind = setBit(ind, ind_ZM, 0);
      end
      default: ind = setOpInvalid(ind);
    endcase
    return ind;
  endactionvalue
endfunction

// What execute() hands back: the next instruction address, progressive
// indexing's deferred index write, an I/O transfer to start, and the
// word a still-unsatisfied operand read wants.  Declared here rather
// than beside mkEBox at the foot of the file so execute() can name it;
// BSV needs the typedef before its first use, which is the only reason
// the signature used to spell the Tuple4 out longhand and the call
// sites read it through tpl_1..tpl_4.
typedef Tuple4#(HWordAddr, Maybe#(Tuple2#(Bit#(4), IndexWord)),
                Maybe#(IoXfer), Maybe#(WordAddr)) ExecResult;

// ---------------------------------------------------------------------
// VFL INTEGER ARITHMETIC (binary mode only; decimal is out of scope,
// see file header), lifted whole out of execute().
//
// The boundary was measured before it was cut, as with the two Fp
// classes.  Over 300 lines this arm touches, of execute()'s own
// locals, exactly three: needsRead, vflPending and ind -- so those
// three are the return channel and nothing else crosses.  It never
// mentions doIdxWrite, idxWriteVal, ioStart, io., next, fallthrough,
// pc or len; of storage it uses only readIndex and writeWord.
//
// needsRead is read as well as written here (the trailing
// progressive-index block is guarded on `!isValid(needsRead)`, so an
// arm that has already asked for a read suppresses it), which is why
// it is threaded through rather than merely returned.
// ---------------------------------------------------------------------
typedef struct {
  Maybe#(WordAddr) needsRead;
  Maybe#(Tuple2#(Bit#(4), IndexWord)) vflPending;
  Word64 ind;
} VflOutcome;

function ActionValue#(VflOutcome)
    vflIntOp(StretchStorage st, VflInstr vi,
             Vector#(2, Word64) prefetch, Bit#(2) prefetchCount, Word64 ind0);
  actionvalue
    Maybe#(WordAddr) needsRead = tagged Invalid;
    Maybe#(Tuple2#(Bit#(4), IndexWord)) vflPending = tagged Invalid;
    Word64 ind = ind0;

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
        Bit#(2) vflReadsUsed = 0; // how many prefetch slots THIS
                            // arm's own (non-immediate) read already
                            // consumed once it completes -- the
                            // progressive-indexing block below reads
                            // this to pick up at the next free slot
                            // for its own refill read, instead of
                            // colliding with (and silently reading
                            // stale data from) whatever slot this
                            // arm already used. Found via xw_refill's
                            // regression failure: ST's RMW read and
                            // the refill read both defaulted to
                            // prefetch[0]/prefetchCount>=1, so the
                            // refill read was never actually issued.
        Bool vflWriteArmHandled = False; // ST/M+ set this when THEY
                            // resolve their own progressive update
                            // inline (see their arms below) instead
                            // of via the shared trailing block --
                            // required because st.writeWord and a
                            // refill's readWordReq both route through
                            // storage's single BRAM port's
                            // request.put, and bsc (correctly)
                            // refuses two request.put call sites in
                            // one execute() invocation (G0004) even
                            // when they're on provably-exclusive
                            // paths across different case arms --
                            // found when this fix's first version hit
                            // exactly that conflict in RL_stepRnx.

        // Progressive-index bookkeeping, computed up front from
        // Reg-only state (xIdx, the instruction's own fields) -- no
        // BRAM dependency at all. Arms that also write to storage
        // (ST/M+) need to know BEFORE they act whether a refill read
        // will also be required, so they can defer their write until
        // both reads are in hand rather than writing immediately and
        // then also trying to issue a refill request in the same
        // execute() call.
        Tuple2#(IndexWord, Bool) vflPx = progressiveIndex(vi.a, xIdx);
        IndexWord vflPx1 = tpl_1(vflPx);
        Bool vflNeedsRefill = tpl_2(vflPx);

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
                if (prefetchCount >= 1) begin
                  raw = extractFieldBits(prefetch[0], 0, off, len_);
                  vflReadsUsed = 1;
                end else
                  needsRead = tagged Valid w0;
              end else begin
                if (prefetchCount >= 2) begin
                  raw = extractFieldBits(prefetch[0], prefetch[1], off, len_);
                  vflReadsUsed = 2;
                end else if (prefetchCount == 1)
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
          6'b001101: begin // ST (Store) -- prefetch/bail-out shape,
            // inlining writeField's own internal RMW read rather
            // than calling it: guaranteed non-crossing (checked
            // just above), so exactly 1 read, same as SV/SC/SR.
            if (immediate || fieldCrosses(ea, len_)) begin
              ind = setOpInvalid(ind);
              vflOk = False;
            end else begin
              SM128 acc = readAcc(st);
              SM128 shifted = SM128 { sign: acc.sign, mag: acc.mag >> offSh };
              Bit#(1) fsign = (vi.m.invert == 1) ? ~shifted.sign : shifted.sign;
              Bit#(64) packedField = smToField(SM128{sign:fsign, mag:shifted.mag}, len_, bsz, vi.m.unsign);
              WordAddr w0 = baWord(ea);
              Bit#(6) off = baBit(ea);
              if (!vflNeedsRefill) begin
                if (prefetchCount >= 1) begin
                  st.writeWord(w0, insertFieldBits(prefetch[0], off, len_, packedField));
                  vflReadsUsed = 1;
                end else
                  needsRead = tagged Valid w0;
              end else begin
                // A refill is also needed: defer the write until
                // BOTH reads (this field's word and the refill word)
                // are in hand, so no execute() call ever issues a
                // write and a new read request at once. See
                // vflWriteArmHandled's own comment above.
                vflWriteArmHandled = True;
                if (prefetchCount >= 2) begin
                  st.writeWord(w0, insertFieldBits(prefetch[0], off, len_, packedField));
                  vflPending = tagged Valid tuple2(vi.a.i1, unpackIndexWord(prefetch[1]));
                  ind = setIndexResultIndicatorsF(ind, vflPx1); // pre-refill state, p.21
                end else if (prefetchCount == 1)
                  needsRead = tagged Valid zeroExtend(vflPx1.refill);
                else
                  needsRead = tagged Valid w0;
              end
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
                if (prefetchCount >= 1) begin
                  raw = extractFieldBits(prefetch[0], 0, off, len_);
                  vflReadsUsed = 1;
                end else
                  needsRead = tagged Valid w0;
              end else begin
                if (prefetchCount >= 2) begin
                  raw = extractFieldBits(prefetch[0], prefetch[1], off, len_);
                  vflReadsUsed = 2;
                end else if (prefetchCount == 1)
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
          6'b001001: begin // M+ (Add to Memory) -- prefetch/bail-out
            // shape, inlining readFieldWithHi/writeFieldWithHi's
            // own logic rather than calling them: guaranteed
            // non-crossing (checked just above), exactly 1 read.
            if (immediate || fieldCrosses(ea, len_)) begin
              ind = setOpInvalid(ind);
              vflOk = False;
            end else begin
              WordAddr w0 = baWord(ea);
              Bit#(6) off = baBit(ea);
              SM128 acc = readAcc(st);
              SM128 accSh = SM128 { sign: acc.sign, mag: acc.mag >> offSh };
              if (!vflNeedsRefill) begin
                if (prefetchCount >= 1) begin
                  Bit#(64) raw = extractFieldBits(prefetch[0], 0, off, len_);
                  SM128 opnd = fieldToSM(raw, len_, bsz, vi.m.unsign, vi.m.invert);
                  SM128 sum = smAdd(opnd, accSh);
                  st.writeWord(w0, insertFieldBits(prefetch[0], off, len_,
                                                    smToField(sum, len_, bsz, vi.m.unsign)));
                  ind = setResultIndicatorsF(ind, sum);
                  vflReadsUsed = 1;
                end else
                  needsRead = tagged Valid w0;
              end else begin
                // Same deferred-write shape as ST above.
                vflWriteArmHandled = True;
                if (prefetchCount >= 2) begin
                  Bit#(64) raw = extractFieldBits(prefetch[0], 0, off, len_);
                  SM128 opnd = fieldToSM(raw, len_, bsz, vi.m.unsign, vi.m.invert);
                  SM128 sum = smAdd(opnd, accSh);
                  st.writeWord(w0, insertFieldBits(prefetch[0], off, len_,
                                                    smToField(sum, len_, bsz, vi.m.unsign)));
                  vflPending = tagged Valid tuple2(vi.a.i1, unpackIndexWord(prefetch[1]));
                  ind = setResultIndicatorsF(ind, sum);
                  ind = setIndexResultIndicatorsF(ind, vflPx1); // pre-refill state, p.21
                end else if (prefetchCount == 1)
                  needsRead = tagged Valid zeroExtend(vflPx1.refill);
                else
                  needsRead = tagged Valid w0;
              end
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
                if (prefetchCount >= 1) begin
                  raw = extractFieldBits(prefetch[0], 0, off, len_);
                  vflReadsUsed = 1;
                end else
                  needsRead = tagged Valid w0;
              end else begin
                if (prefetchCount >= 2) begin
                  raw = extractFieldBits(prefetch[0], prefetch[1], off, len_);
                  vflReadsUsed = 2;
                end else if (prefetchCount == 1)
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
        // read, this must NOT run -- it would set vflPending and
        // mutate ind despite the instruction not actually having
        // completed, breaking the bail-out contract (see execute()'s
        // own header comment: nothing after a bail may touch the
        // shared outputs).
        if (!isValid(needsRead) && isProgressive && vflOk && !vflWriteArmHandled) begin
          // L/+/K's shared progressive-index completion: their own
          // read (if any) never collides with a refill read (they
          // only write to Regs -- accumulator/indicators -- not
          // storage), so this can safely bail for the refill itself
          // when needed. ST/M+ instead resolve their own progressive
          // update inline in their arms above (vflWriteArmHandled),
          // since THEIR completion is a storage write that cannot
          // share an execute() call with a new read request -- see
          // vflWriteArmHandled's own comment. vflPx1/vflNeedsRefill
          // computed once, up front, before the case (see there).
          if (vflNeedsRefill && vflReadsUsed >= 2) begin
            // The arm above already used both prefetch slots (a
            // crossing-field read); a refill on top of that would
            // need a 3rd slot, beyond this design's 2-slot bound.
            // Not reachable by any current test (see
            // docs/phase2_arm_inventory.md, "V+/V+C/V+CR" note) --
            // flagged explicitly rather than silently misreading
            // stale prefetch data, the same class of bug this fix
            // corrects for the (own-read + refill) case below.
            ind = setOpInvalid(ind);
          end else if (vflNeedsRefill && prefetchCount < vflReadsUsed + 1) begin
            needsRead = tagged Valid zeroExtend(vflPx1.refill);
          end else begin
            Bit#(1) slot = truncate(vflReadsUsed);
            IndexWord px2 = vflNeedsRefill ? unpackIndexWord(prefetch[slot]) : vflPx1;
            vflPending = tagged Valid tuple2(vi.a.i1, px2);
            ind = setIndexResultIndicatorsF(ind, vflPx1); // pre-refill state, p.21
          end
        end
      end
    return VflOutcome{needsRead: needsRead, vflPending: vflPending, ind: ind};
  endactionvalue
endfunction

function ActionValue#(ExecResult)
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
        VflOutcome vo <- vflIntOp(st, vi, prefetch, prefetchCount, ind);
        needsRead  = vo.needsRead;
        vflPending = vo.vflPending;
        ind        = vo.ind;
      end

      // -----------------------------------------------------------
      // Direct index arithmetic (p.22-23).
      // -----------------------------------------------------------
      tagged DirIndex .di_: begin
        HWordAddr ea = effAddr19(st, di_.addr, di_.idx);
        IndexWord x = st.readIndex(di_.j);
        // Reference Manual p.24: "The index-flag and index-result
        // indicators are set in all of the preceding direct index
        // arithmetic operations [LX/LV/LC/LR/SX/SV/SC/SR/V+/V+C/V+CR].
        // The index-comparison indicators are unchanged." -- and p.23:
        // they "describe the index after the index modification is
        // completed". So loads set them from the NEW index word and
        // stores from the (unchanged) current one. Before this was
        // added only V+/V+C/V+CR set them; caught by I-Box 1's
        // SIC-B,ZIND block (p.50-51), which tests XF/XCZ/XVGZ/XVLZ/
        // XVZ straight after an LX.
        case (di_.code)
          dixop_LX: begin // LX -- prefetch/bail-out shape (same as
            // VflInt L/K/+ above). Half-word reads never cross a word
            // boundary (a half-word always fits within the one word
            // it addresses), so this and every other DirIndex
            // read-only arm below needs exactly 0-1 reads, never 2.
            if (prefetchCount >= 1) begin
              idxWriteReg = di_.j; doIdxWrite = True;
              idxWriteVal = unpackIndexWord(prefetch[0]);
              ind = setIndexResultIndicatorsF(ind, idxWriteVal);
            end else
              needsRead = tagged Valid ea[18:1];
          end
          dixop_SX: begin // SX
            st.writeWord(ea[18:1], packIndexWord(x));
            ind = setIndexResultIndicatorsF(ind, x);
          end
          dixop_LV: begin // LV
            if (prefetchCount >= 1) begin
              Bit#(32) h = (ea[0] == 0) ? prefetch[0][63:32] : prefetch[0][31:0];
              idxWriteReg = di_.j; doIdxWrite = True;
              idxWriteVal = IndexWord{addr:h[31:8], sign:h[7:7], flag:x.flag,
                                              count:x.count, refill:x.refill};
              ind = setIndexResultIndicatorsF(ind, idxWriteVal);
            end else
              needsRead = tagged Valid ea[18:1];
          end
          dixop_SV: begin // SV -- prefetch/bail-out shape: unlike the
            // read-only arms above, this writes back using the SAME
            // read's response (a genuinely dependent chain), but
            // since writes stay single-cycle throughout this whole
            // migration, resuming with prefetch[0] available is
            // enough to both compute and issue the write in one go --
            // no second bail needed.
            if (prefetchCount >= 1) begin
              Bit#(32) h = (ea[0] == 0) ? prefetch[0][63:32] : prefetch[0][31:0];
              writeHWWithWord(st, ea, {x.addr, x.sign, h[6:0]}, prefetch[0]);
              ind = setIndexResultIndicatorsF(ind, x);
            end else
              needsRead = tagged Valid ea[18:1];
          end
          dixop_LC: begin // LC
            if (prefetchCount >= 1) begin
              Bit#(32) h = (ea[0] == 0) ? prefetch[0][63:32] : prefetch[0][31:0];
              idxWriteReg = di_.j; doIdxWrite = True;
              idxWriteVal = IndexWord{addr:x.addr, sign:x.sign, flag:x.flag,
                                              count:h[31:14], refill:x.refill};
              ind = setIndexResultIndicatorsF(ind, idxWriteVal);
            end else
              needsRead = tagged Valid ea[18:1];
          end
          dixop_SC: begin // SC -- same shape as SV above.
            if (prefetchCount >= 1) begin
              Bit#(32) h = (ea[0] == 0) ? prefetch[0][63:32] : prefetch[0][31:0];
              writeHWWithWord(st, ea, {x.count, 7'b0, h[6:0]}, prefetch[0]);
              ind = setIndexResultIndicatorsF(ind, x);
            end else
              needsRead = tagged Valid ea[18:1];
          end
          dixop_LR: begin // LR
            if (prefetchCount >= 1) begin
              Bit#(32) h = (ea[0] == 0) ? prefetch[0][63:32] : prefetch[0][31:0];
              idxWriteReg = di_.j; doIdxWrite = True;
              idxWriteVal = IndexWord{addr:x.addr, sign:x.sign, flag:x.flag,
                                              count:x.count, refill:h[31:14]};
              ind = setIndexResultIndicatorsF(ind, idxWriteVal);
            end else
              needsRead = tagged Valid ea[18:1];
          end
          dixop_SR: begin // SR -- same shape as SV above.
            if (prefetchCount >= 1) begin
              Bit#(32) h = (ea[0] == 0) ? prefetch[0][63:32] : prefetch[0][31:0];
              writeHWWithWord(st, ea, {x.refill, 7'b0, h[6:0]}, prefetch[0]);
              ind = setIndexResultIndicatorsF(ind, x);
            end else
              needsRead = tagged Valid ea[18:1];
          end
          dixop_V_PLUS, dixop_V_PLUS_C, dixop_V_PLUS_CR: begin // V+ / V+C / V+CR --
            // prefetch/bail-out shape with up to 2 SEQUENTIAL reads:
            // readHW's own half-word read (prefetch[0]), then, only
            // for V+CR when the count reaches zero, a second refill
            // read (prefetch[1]) -- the first arm converted needing 2
            // reads for a genuinely sequential reason (a value from
            // the first read decides whether a second is needed at
            // all), distinct from VflInt's crossing case (2 reads
            // always needed together for one field). Same 2-slot
            // prefetch bound covers both shapes.
            if (prefetchCount >= 1) begin
              Bit#(32) h = (ea[0] == 0) ? prefetch[0][63:32] : prefetch[0][31:0];
              SM128 opnd = SM128{sign: h[7], mag: zeroExtend(h[31:8])};
              SM128 val  = SM128{sign: x.sign, mag: zeroExtend(x.addr)};
              SM128 sum  = smAdd(val, opnd);
              IndexWord x1 = IndexWord{addr: truncate(sum.mag), sign: sum.sign, flag: x.flag,
                                        count: x.count, refill: x.refill};
              if (di_.code != dixop_V_PLUS) x1.count = x1.count - 1;
              Bool needsRefill = (di_.code == dixop_V_PLUS_CR) && (x1.count == 0);
              if (needsRefill && prefetchCount < 2) begin
                needsRead = tagged Valid zeroExtend(x1.refill);
              end else begin
                IndexWord x2 = needsRefill ? unpackIndexWord(prefetch[1]) : x1;
                idxWriteReg = di_.j; doIdxWrite = True;
                idxWriteVal = x2;
                ind = setIndexResultIndicatorsF(ind, x1); // reflects state before any refill, p.23
              end
            end else
              needsRead = tagged Valid ea[18:1];
          end
          dixop_KV: begin // KV
            if (prefetchCount >= 1) begin
              Bit#(32) h = (ea[0] == 0) ? prefetch[0][63:32] : prefetch[0][31:0];
              SM128 opnd = SM128{sign: h[7], mag: zeroExtend(h[31:8])};
              SM128 val  = SM128{sign: x.sign, mag: zeroExtend(x.addr)};
              ind = setIndexCmpIndicatorsF(ind, smCompare(val, opnd));
            end else
              needsRead = tagged Valid ea[18:1];
          end
          dixop_KC: begin // KC
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
        // Reference Manual p.25, per operation: the 19-bit address part
        // is NOT a raw integer. Value operations (LVI/LVNI/V+I.../KVI/
        // KVNI) use "the address part, bits 0-18, of the instruction"
        // as bits 0-18 OF THE VALUE FIELD, "bits 19-24 set to zero"
        // (or "zeros added to bits 19-24") -- i.e. the field is the
        // word-and-half part of a bit address, value = field << 5.
        // Count/refill operations (LCI/LRI/C+I/C-I/KCI) use "bits 0-17
        // of the address part" -- the field's TOP 18 bits. An earlier
        // version used the raw 19-bit field for values and its LOW 18
        // bits for counts; caught by strap/verify_ibox1_listing.py,
        // where I-Box 1's "LCI,$X1,4" prints as 4.03 02 (count 4 in
        // bits 0-17), then confirmed against p.25.
        Bit#(24) immVal24 = {ii.imm, 5'b0};
        Bit#(18) imm18 = ii.imm[18:1];
        SM128 immSM = SM128{sign: 0, mag: zeroExtend(immVal24)};
        SM128 val = SM128{sign: x.sign, mag: zeroExtend(x.addr)};
        case (ii.code)
          4'b0001: begin // LVI
            idxWriteReg = ii.j; doIdxWrite = True;
            idxWriteVal = IndexWord{addr: immVal24, sign: 0,
                     flag: x.flag, count: x.count, refill: x.refill};
          end
          4'b1001: begin // LVNI
            idxWriteReg = ii.j; doIdxWrite = True;
            idxWriteVal = IndexWord{addr: immVal24, sign: 1,
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
      // Half-word branches: Count and Branch (CB/CBR), Branch on
      // Indicator, Unconditional. All three evaluate through
      // evalBranch (above) so that SIC, whose right half is one of
      // them, executes the identical logic -- see the Sic arm below.
      // -----------------------------------------------------------
      tagged CountBranch .*: begin
        BranchOutcome o = evalBranch(st, di, ind, prefetch, prefetchCount, 0);
        needsRead = o.needsRead;
        if (o.needsRead matches tagged Invalid) begin
          ind = o.ind; doIdxWrite = o.doIdxWrite;
          idxWriteReg = o.idxWriteReg; idxWriteVal = o.idxWriteVal;
          if (o.taken) next = o.target;
        end
      end

      tagged BranchInd .*: begin
        BranchOutcome o = evalBranch(st, di, ind, prefetch, prefetchCount, 0);
        ind = o.ind;
        if (o.taken) next = o.target;
      end

      // -----------------------------------------------------------
      // Unconditional branching / Store Zero / Refill.
      // -----------------------------------------------------------
      tagged BranchOrMisc .bm: begin
        if (!bm.misc) begin
          BranchOutcome o = evalBranch(st, di, ind, prefetch, prefetchCount, 0);
          if (o.taken) next = o.target;
        end else begin
          case (bm.code)
            3'b100: begin // Z (Store Zero)
              WordAddr zw = baWord(effAddr24(st, {bm.addr,5'b0}, bm.idx));
              if (zw == 11)
                // Store Zero to the INDICATOR register clears the
                // settable bits 20-63 (bits 0-19 are read-only, p.41);
                // writeWord(11) is a no-op, so fold into `ind` (the
                // Word64 the shared tail writes once via
                // setIndicatorBits), keeping IBM bits 0-19 = BSV 63:44.
                // This is the diagnostic's `Z,$IND` reset before a test.
                ind = ind & 64'hFFFFF00000000000;
              else
                st.writeWord(zw, 0);
            end
            3'b000: begin // R (Refill, unconditional) -- prefetch/
              // bail-out shape (same as VflInt L/K/+ above).
              IndexWord x = st.readIndex(bm.idx);
              if (prefetchCount >= 1) begin
                idxWriteReg = bm.idx; doIdxWrite = True;
                idxWriteVal = unpackIndexWord(prefetch[0]);
              end else
                needsRead = tagged Valid zeroExtend(x.refill);
            end
            3'b001: begin // RCZ (Refill on Count Zero)
              IndexWord x = st.readIndex(bm.idx);
              if (x.count == 0) begin
                if (prefetchCount >= 1) begin
                  idxWriteReg = bm.idx; doIdxWrite = True;
                  idxWriteVal = unpackIndexWord(prefetch[0]);
                end else
                  needsRead = tagged Valid zeroExtend(x.refill);
              end
            end
            default: ind = setOpInvalid(ind); // EX, EXIC: out of scope
          endcase
        end
      end

      // -----------------------------------------------------------
      // SIC (Store Instruction Counter If), Reference Manual p.41-42:
      // a full word whose bits 32-63 are an ordinary half-word branch
      // (B/BR/BE/BD/BEW/NOP, CB family, or Branch on Indicator). The
      // branch executes with its own normal semantics; "it is executed
      // [the store] if and only if the associated branching is
      // successful. When it is executed, it causes the instruction
      // counter contents to be stored in bits 0-18 of the half-word
      // specified by bits 0-18 of the effective storage address. Other
      // bits of the half-word are not disturbed. The stored
      // instruction counter contents always address the instruction
      // whose location is next higher in storage than the branch
      // instruction to which SIC is prefixed" -- i.e. `fallthrough`.
      // "The instruction counter may be stored in any available
      // location with 19-bit address 16.0 or above" (p.42): below
      // that, AD (address invalid) is set and nothing is stored.
      // SIC + NOP is "a valid full-word NO OPERATION; the counter is
      // not stored" -- falls out of `taken` being False for NOP.
      //
      // Read-modify-write of the target half-word uses the prefetch/
      // bail mechanism, in the slot AFTER any refill read the inner
      // CBR consumed (o.readsUsed): first any inner read, then the
      // target word, then commit everything in one call. Never issues
      // the write in the same call as a bail (phase2 step 9 rule).
      // The only st.writeWord call site for SIC lives in this one arm,
      // syntactically exclusive with every other arm's writes.
      // -----------------------------------------------------------
      tagged Sic .s: begin
        DecodedInstr inner = decodeHalfWord(s.inner);
        BranchOutcome o = evalBranch(st, inner, ind, prefetch, prefetchCount, 0);
        if (o.needsRead matches tagged Valid .*) begin
          needsRead = o.needsRead;
        end else begin
          BitAddr ea = effAddr24(st, s.addr, s.idx);
          HWordAddr ha = ea[23:5];
          if (o.taken && ha >= 32 && prefetchCount < o.readsUsed + 1) begin
            needsRead = tagged Valid ha[18:1];
          end else begin
            ind = o.ind;
            // The inner CB's index-register write goes through the
            // deferred second-step path (vflPending / StretchCore's
            // pendingIdxWrite), NOT doIdxWrite: bsc rejects a
            // general-storage write and an index-register write in the
            // same rule invocation with a spurious G0004 conflict --
            // bsv/README.md "Toolchain" item 7, the exact reason
            // progressive indexing's write is deferred the same way.
            // Same observable result: the write lands on the next
            // step() call, before the next instruction fetches.
            if (o.doIdxWrite) vflPending = tagged Valid tuple2(o.idxWriteReg, o.idxWriteVal);
            if (o.taken) begin
              next = o.target;
              if (ha < 32)
                ind = setBit(ind, ind_AD, 1);
              else begin
                Word64 w = prefetch[o.readsUsed[0]];
                HalfWord32 old = (ha[0] == 0) ? w[63:32] : w[31:0];
                HalfWord32 hwv = {fallthrough, old[12:0]};
                Word64 w2 = (ha[0] == 0) ? {hwv, w[31:0]} : {w[63:32], hwv};
                st.writeWord(ha[18:1], w2);
              end
            end
          end
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
          // Prefetch/bail-out shape: reads srcBase, writes the SAME
          // value verbatim to dstBase once available -- a dependent
          // chain (the write's data IS the read's response), same
          // shape as ST/M+/CM above.
          WordAddr srcBase = baWord(effAddr24(st, t.addr1, t.i1));
          WordAddr dstBase = (effAddr19(st, t.addr2, t.i2))[18:1];
          if (prefetchCount >= 1)
            st.writeWord(dstBase, prefetch[0]);
          else
            needsRead = tagged Valid srcBase;
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
        end else if (cn.suffix == conn_CM && immediate) begin
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
          Bit#(2) vflReadsUsed = 0; // see VflInt's identical field above
                              // for why this exists (xw_refill bisection).
          Bool vflWriteArmHandled = False; // see VflInt's identical field
                              // above -- CM (the only suffix here that
                              // writes to storage) sets this when it
                              // resolves its own progressive update
                              // inline, same reason as VflInt's ST/M+.

          // Progressive-index bookkeeping, hoisted up front for the
          // same reason as VflInt's identical block: CM needs to know
          // BEFORE it reads/writes whether a refill will also be
          // needed, so it can defer its write rather than issue one in
          // the same execute() call as a refill's readWordReq.
          Tuple2#(IndexWord, Bool) vflPx = progressiveIndex(cn.a, xIdx);
          IndexWord vflPx1 = tpl_1(vflPx);
          Bool vflNeedsRefill = tpl_2(vflPx);

          if (cn.suffix == conn_CM && fieldCrosses(ea, len_)) begin
            // CM writing a crossing field: same single-word-write
            // limitation as VflInt's ST/M+ (writeField's precondition).
            ind = setOpInvalid(ind);
            vflOk = False;
          end else if (cn.suffix == conn_CM && vflNeedsRefill) begin
            // CM with a refill also pending: deferred-write shape, same
            // as VflInt's ST -- own field word first, refill second,
            // write only once both are in hand (see vflWriteArmHandled's
            // comment above for why this can't share the generic
            // C/CT/CM read-then-dispatch path below). CM is always
            // non-crossing and non-immediate here (both forced invalid
            // above), so its own read is always exactly 1 slot.
            vflWriteArmHandled = True;
            WordAddr w0 = baWord(ea);
            Bit#(6) off = baBit(ea);
            if (prefetchCount >= 2) begin
              Word64 mHiWord = prefetch[0];
              Bit#(64) m = extractFieldBits(prefetch[0], 0, off, len_);
              SM128 acc = readAcc(st);
              Bit#(64) a = truncate(acc.mag >> offSh) & fieldMask;
              Bit#(64) result = applyConnective(cn.conn, m, a) & fieldMask;
              writeFieldWithHi(st, ea, len_, result, mHiWord);
              ind = setConnectiveIndicatorsF(ind, True, result == 0);
              vflPending = tagged Valid tuple2(cn.a.i1, unpackIndexWord(prefetch[1]));
              ind = setIndexResultIndicatorsF(ind, vflPx1); // pre-refill state, p.21
            end else if (prefetchCount == 1)
              needsRead = tagged Valid zeroExtend(vflPx1.refill);
            else
              needsRead = tagged Valid w0;
          end else begin
            Bit#(64) m = 0;
            Word64 mHiWord = 0; // valid only for CM (the only suffix
                                 // that writes back); see below.
            if (immediate) begin
              m = immediateOperand(cn.a.addr, len_);
            end else begin
              // C/CT/CM all share this prefetch/bail-out shape. CM is
              // guaranteed non-crossing by the outer guard above (and
              // guaranteed !immediate by the check further above), so
              // it always takes the !crosses branch below and needs
              // exactly 1 read -- the same shape VflInt M+/ST have.
              // C/CT, unlike CM, are NOT restricted to non-crossing
              // (neither writes to general storage: C writes the
              // accumulator, CT writes nothing), so they can genuinely
              // need the 2-read crossing path.
              WordAddr w0 = baWord(ea);
              Bit#(6) off = baBit(ea);
              if (!fieldCrosses(ea, len_)) begin
                if (prefetchCount >= 1) begin
                  m = extractFieldBits(prefetch[0], 0, off, len_);
                  if (cn.suffix == conn_CM) mHiWord = prefetch[0]; // CM's writeback needs the raw word
                  vflReadsUsed = 1;
                end else
                  needsRead = tagged Valid w0;
              end else begin
                if (prefetchCount >= 2) begin
                  m = extractFieldBits(prefetch[0], prefetch[1], off, len_);
                  vflReadsUsed = 2;
                end else if (prefetchCount == 1)
                  needsRead = tagged Valid (w0 + 1);
                else
                  needsRead = tagged Valid w0;
              end
            end
            if (!isValid(needsRead)) begin
              SM128 acc = readAcc(st);
              Bit#(64) a = truncate(acc.mag >> offSh) & fieldMask;
              Bit#(64) result = applyConnective(cn.conn, m, a) & fieldMask;
              Bool resultZero = (result == 0);

              case (cn.suffix)
                conn_C: begin // C: result replaces the accumulator
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
                conn_CM: writeFieldWithHi(st, ea, len_, result, mHiWord); // CM
                conn_CT: begin end // CT: result discarded, indicators only
                default: ind = setOpInvalid(ind); // unreachable: StretchDecode's
                                                   // isConnSuffix only admits these
                                                   // three patterns; kept for bsc's
                                                   // exhaustiveness check, same style
                                                   // as VflInt's own default arm above.
              endcase

              ind = setConnectiveIndicatorsF(ind, cn.suffix == conn_CM, resultZero);
            end
          end

          if (!isValid(needsRead) && isProgressive && vflOk && !vflWriteArmHandled) begin
            // C/CT's shared progressive-index completion (CM resolves
            // its own inline above -- see vflWriteArmHandled). Reuses
            // vflPx1/vflNeedsRefill computed up front; same shape as
            // VflInt's identical trailing block.
            if (vflNeedsRefill && vflReadsUsed >= 2) begin
              // See VflInt's identical comment above: a crossing-field
              // read (C/CT only -- CM is always non-crossing, forced
              // invalid above) plus a refill would need a 3rd prefetch
              // slot. Not reachable by any current test.
              ind = setOpInvalid(ind);
            end else if (vflNeedsRefill && prefetchCount < vflReadsUsed + 1) begin
              needsRead = tagged Valid zeroExtend(vflPx1.refill);
            end else begin
              Bit#(1) slot = truncate(vflReadsUsed);
              IndexWord px2 = vflNeedsRefill ? unpackIndexWord(prefetch[slot]) : vflPx1;
              vflPending = tagged Valid tuple2(cn.a.i1, px2);
              ind = setIndexResultIndicatorsF(ind, vflPx1); // pre-refill state, p.21
            end
          end
        end
      end
      tagged Fp .fp: begin
        // Floating point, single precision (StretchFP.bsv, Reference
        // Manual pp.78-94). The accumulator operand is the left half in
        // the machine's own format (exponent + fraction in bits 0-59,
        // sign and flags in the sign byte register). Every operation
        // but ST reads its storage operand first (prefetch/bail).
        WordAddr ea = effAddr18(st, fp.addr, fp.idx);
        // Address Invalid (Reference Manual p.20): an effective word
        // address beyond the installed core (StretchMemory's
        // InstalledWords = 98304, six units) sets AD and the
        // instruction "is executed as a NO OPERATION". A floating-point
        // instruction always addresses a full word, so this one guard
        // covers L/ST and every arithmetic op below -- except SHF and
        // E+I, whose "address" is a shift spec / immediate exponent
        // and is explicitly not boundary-monitored (Reference Manual
        // pp.101-102).
        if (!installed(ea) && fp.code != fpop_SHF && fp.code != fpop_E_PLUS_I)
          ind = setBit(ind, ind_AD, 1);
        else begin
        Bool normalized = (fp.unnorm == 0);
        Bool noisy = (ind[63 - ind_NM] == 1);
        FpNum acc = fpFromAcc(st.readAccLeft(), st.readAccSign());
        Word64 accL = st.readAccLeft();
        Word64 accS = st.readAccSign();
        Bit#(7) c = fp.code;
        Bool isST = (c == fpop_ST);
        Bool isSRD = (c == fpop_SRD);  // STORE ROUNDED (p.96)
        Bool isSLO = (c == fpop_SLO);  // STORE LOW ORDER (p.97)
        // (A note here used to say divide was "deferred to the
        // multi-cycle arithmetic unit... decodes but does not execute".
        // /, R/, D/ and SRT are all implemented now, combinationally,
        // for the same reason fpMul is: see fpDivFrac's header. The
        // real machine's divide really is iterative -- about 3.5
        // quotient bits per cycle, Buchholz p.213 -- but that is a
        // timing property this model expresses as a cycle budget in
        // StretchTiming, not as datapath structure.)
        Bool isSHF = (c == fpop_SHF);
        Bool isEplI = (c == fpop_E_PLUS_I);  // E+I (add immediate to exponent)
        // The no-operand store group, lifted into fpStoreClass above.
        Bool isStoreClass = isST || isSRD || isSLO || isSHF || isEplI
                            || (c == fpop_SRT);
        Bool known = (c == fpop_PLUS || c == fpop_PLUS_MG || c == fpop_L || c == fpop_LWF
                   || c == fpop_M_PLUS || c == fpop_M_PLUS_MG || isST
                   || c == fpop_K || c == fpop_KMG || c == fpop_KR || c == fpop_KMGR
                   || c == fpop_STAR || c == fpop_D_STAR || c == fpop_LFT || c == fpop_STAR_PLUS
                   || c == fpop_SLASH || c == fpop_D_SLASH || c == fpop_R_SLASH
                   || c == fpop_SRT
                   || c == fpop_E_PLUS || isEplI || isSHF
                   || c == fpop_DL || c == fpop_DLWF
                   || c == fpop_D_PLUS || c == fpop_D_PLUS_MG
                   || c == fpop_F_PLUS
                   || isSRD || isSLO);                     // SRD / SLO
        if (!known)
          ind = setOpInvalid(ind);   // every floating-point operation is now implemented
        else if (isStoreClass) begin
          ind <- fpStoreClass(st, c, fp.absSign, fp.invSign, ea, acc, accL, accS,
                              normalized, noisy, ind);
        end else if (prefetchCount < 1)
          needsRead = tagged Valid ea;
        else begin
          ind <- fpArithClass(st, c, fp.absSign, fp.invSign, ea, acc, accL, accS,
                              normalized, noisy, prefetch[0], ind);
        end
        end  // AD guard
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
              end else if (prefetchCount >= 1) begin
                // Prefetch/bail-out shape, same as every other
                // single-read arm -- this completes step 8
                // (docs/phase2_arm_inventory.md), the last remaining
                // execute() case arm.
                ControlWord cw0 = unpackControlWord(prefetch[0]);
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
              end else
                needsRead = tagged Valid effA2;
            end
          endcase
        end
      end
      // -----------------------------------------------------------
      // BRANCH ON BIT (Reference Manual p.41). Test one bit anywhere
      // in storage at the effective bit address; if its value matches
      // bb.modAbc[0] (the branch-condition bit, IBM bit 62 -- 1 for
      // BB*, 0 for BZB*) the branch is taken. Then, WHETHER OR NOT the
      // branch was taken, the tested bit is set per bb.modAbc[2:1]
      // (IBM bits 60-61): 00 unchanged, 01 set to zero, 10 inverted,
      // 11 set to one. Read-modify-write, so it uses the two-phase
      // needsRead/prefetch path (same shape as BranchOrMisc's Refill):
      // phase 1 (prefetchCount==0) requests the word; phase 2 tests
      // the bit, decides the branch, and writes the word back.
      // 00 (unchanged) issues NO write -- avoiding a phantom store-
      // close-to-fetch hazard. Bit numbering: IBM bit p in a word is
      // BSV index 63-p (StretchTypes.bsv), matching insertFieldBits'
      // shiftAmt=64-off-len for len==1.
      //
      // BB on the INDICATOR register (word 11): p.41 says "BRANCH ON BIT
      // may also be used to test and change the contents of positions
      // 20-63 of the indicator register". A plain st.writeWord(11) is a
      // no-op (indicators are written once per rule via setIndicatorBits;
      // a Reg cannot take two writes in one rule), so the write below
      // special-cases word 11 and folds the modified bit into `ind`
      // instead -- see that arm. Verified by bb_indicator.strap
      // (BB1,$AH sets AH, then BB,$AH branches on it); it unblocks
      // jb_af1c F202G's `BB1,$AH` before its KR range compares. Other
      // read-only locations ("remain unchanged when there is any attempt
      // to change them", p.41) are not modeled; special registers 0-31
      // are Reg-backed.
      //
      // Store-close-to-fetch and index consistency (StretchCore.bsv):
      //   * BB is NOT isEboxClass, so it is never loaded into a look-
      //     ahead level and storeTarget() is deliberately NOT extended
      //     to it (a case there would be dead code). Instead iboxHazard
      //     hits its default (h=True), so BB waits for the whole look-
      //     ahead to DRAIN before it executes -- a strictly stronger
      //     guarantee than the level-to-level storeAddr interlock. BB's
      //     read of its bit word thus never sees an un-retired earlier
      //     store.
      //   * The phase-1 and phase-2 effAddr24 calls read the same index
      //     bb.i1: a parked instruction is the look-ahead head (the
      //     E-box holds it with owner OwnerLA), levels retire head-first, and the only writer
      //     of index ahead of time is wrong-guess recovery, which
      //     resolves before any younger instruction reaches the head --
      //     so nothing rewrites bb.i1 between park and re-entry.
      //   * KNOWN-UNTESTED sub-case: a BB store followed immediately by
      //     an E-box LOAD of the same word. Same class as SIC (also
      //     non-Ebox, also writes storage, also absent from
      //     storeTarget), whose store-then-execute path IS validated
      //     via recentStore(); no program exercises the BB variant yet.
      tagged BitBranch .bb: begin
        BitAddr  ba = effAddr24(st, bb.addr1, bb.i1);
        WordAddr bw = baWord(ba);
        if (prefetchCount >= 1) begin
          Bit#(6) sh     = 63 - baBit(ba);
          Bit#(1) tested = prefetch[0][sh];
          if (tested == bb.modAbc[0])
            next = effAddr19(st, bb.addr2, {3'b0, bb.idx}); // K: X1 only
          Bit#(2) mod = bb.modAbc[2:1];
          if (mod != 2'b00) begin
            Bit#(1) nb = case (mod)
                           2'b01: 1'b0;      // set to zero
                           2'b10: ~tested;   // invert (negate)
                           2'b11: 1'b1;      // set to one
                           default: tested;
                         endcase;
            if (bw == 11) begin
              // BB changing an INDICATOR-register bit (p.41: positions
              // 20-63). writeWord(11) is a no-op, so fold the modified
              // bit into `ind` -- the Word64 the shared tail writes once
              // via setIndicatorBits -- instead. prefetch[0] read back
              // the indicator value (lookupSpecial(11)=indicators), so
              // it equals `ind` here; bits 0-19 are read-only, left as
              // is. Unblocks jb_af1c F202G's BB1,$AH before its KRs.
              if (baBit(ba) >= 20)
                ind = insertFieldBits(ind, baBit(ba), 1, zeroExtend(nb));
            end else
              st.writeWord(bw, insertFieldBits(prefetch[0], baBit(ba), 1,
                                               zeroExtend(nb)));
          end
        end else
          needsRead = tagged Valid bw;
      end
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

// ---------------------------------------------------------------------
// The E-box as a single shared MODULE (idiomatic-Bluespec rewrite step
// 1, microarchitecture_plan.md §1c). `execute` above is the whole
// execute datapath as one function; BSV inlines functions, so calling
// it directly at StretchCore.step()'s four sites is un-idiomatic (the
// "weird Verilog" the owner flagged). Wrapping it in a module
// instantiated once and calling its `exec` method is the mkFBox/mkMBox
// shape from Bluespec's Piccolo/Flute: the datapath lives in a
// singleton sub-module and the pipeline just calls its method. The four
// call sites are mutually-exclusive branches of step(), so they share
// this one instance's method port. (This step alone is behavior-neutral
// scaffolding; step 2 makes the FP/VFL datapath multi-cycle boxes.)
// (ExecResult is declared above execute(), which needs it.)

// What a completed instruction hands back to the instruction unit.
typedef struct {
  HWordAddr next;                              // next instruction address
  Maybe#(Tuple2#(Bit#(4), IndexWord)) idxWrite; // progressive indexing's part 2
  Maybe#(IoXfer) ioStart;                      // an RD/W transfer to service
} ExecDone deriving (Bits, Eq, FShow);

// Who dispatched the operation the E-box is holding: the instruction
// unit directly (an I-box-class instruction executing in preparation)
// or the look-ahead (the head level, removed into the arithmetic unit).
typedef enum { OwnerIbox, OwnerLA } ExecOwner deriving (Bits, Eq, FShow);

// Step 5c (plan §1c): the E-box as a request/busy/result box, the
// mkFBox shape. `start` runs the instruction; if it completes in the
// clock, the result comes back at once (Valid); if it needs an operand
// word from core storage, the box issues the read, holds the
// instruction (pending/prefetch/prefetchCount/owner -- the bail/resume
// state that used to live in StretchCore) and reports busy until
// `resume` -- called by the instruction unit once `canResume` -- has
// collected the word and re-run it, possibly bailing again for a
// second word. `exec` is the bare one-shot datapath, kept for the
// preparation arm's side-effect-free operand-address probe.
interface EBox;
  method ActionValue#(ExecResult)
    exec(HWordAddr pc, InstrLen len, DecodedInstr di,
         Vector#(2, Word64) prefetch, Bit#(2) prefetchCount);
  method ActionValue#(Maybe#(ExecDone))
    start(HWordAddr pc, InstrLen len, DecodedInstr di,
          Vector#(2, Word64) prefetch, Bit#(2) prefetchCount, ExecOwner owner);
  method Bool busy();                 // holding an instruction that waits on a read
  method Bool busyFor(ExecOwner o);   // ... dispatched by o
  method Bool canResume();            // busy and the read has answered
  method Tuple3#(HWordAddr, InstrLen, DecodedInstr) pending();   // the held instruction
  method ActionValue#(Maybe#(ExecDone)) resume();
endinterface

module mkEBox #(StretchStorage st, StretchIO io) (EBox);
  // The held instruction: Invalid when nothing is in flight. prefetch/
  // prefetchCount are the operand words collected so far, so the next
  // run of execute() picks up with one more slot filled (execute()'s
  // header comment has the contract).
  Reg#(Maybe#(Tuple3#(HWordAddr, InstrLen, DecodedInstr))) held <- mkReg(tagged Invalid);
  Reg#(Vector#(2, Word64)) prefetch      <- mkReg(replicate(0));
  Reg#(Bit#(2))            prefetchCount <- mkReg(0);
  Reg#(ExecOwner)          owner         <- mkReg(OwnerIbox);

  function ExecDone doneOf(ExecResult r) =
    ExecDone { next: tpl_1(r), idxWrite: tpl_2(r), ioStart: tpl_3(r) };

  method ActionValue#(ExecResult)
      exec(HWordAddr pc, InstrLen len, DecodedInstr di,
           Vector#(2, Word64) pf, Bit#(2) cnt);
    let r <- execute(st, io, pc, len, di, pf, cnt);
    return r;
  endmethod

  method ActionValue#(Maybe#(ExecDone))
      start(HWordAddr pc, InstrLen len, DecodedInstr di,
            Vector#(2, Word64) pf, Bit#(2) cnt, ExecOwner o);
    let r <- execute(st, io, pc, len, di, pf, cnt);
    if (tpl_4(r) matches tagged Valid .a) begin
      st.readWordReq(a);
      held <= tagged Valid tuple3(pc, len, di);
      prefetch <= pf;
      prefetchCount <= cnt;
      owner <= o;
      return tagged Invalid;
    end else
      return tagged Valid doneOf(r);
  endmethod

  method Bool busy() = isValid(held);
  method Bool busyFor(ExecOwner o) = isValid(held) && owner == o;
  method Bool canResume() = isValid(held) && st.responseReady();
  method Tuple3#(HWordAddr, InstrLen, DecodedInstr) pending() = validValue(held);

  method ActionValue#(Maybe#(ExecDone)) resume();
    let ep = validValue(held);
    Word64 v <- st.readWordResp();
    Vector#(2, Word64) pf = prefetch;
    pf[prefetchCount] = v;
    Bit#(2) cnt = prefetchCount + 1;
    let r <- execute(st, io, tpl_1(ep), tpl_2(ep), tpl_3(ep), pf, cnt);
    if (tpl_4(r) matches tagged Valid .a) begin
      st.readWordReq(a);
      prefetch <= pf;
      prefetchCount <= cnt;
      return tagged Invalid;
    end else begin
      held <= tagged Invalid;
      return tagged Valid doneOf(r);
    end
  endmethod
endmodule

endpackage
