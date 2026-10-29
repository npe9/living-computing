// StretchIBox.bsv
//
// The instruction unit's own pieces, as a stage module plus pure
// helpers (idiomatic-Bluespec rewrite step 5b, docs/microarchitecture_
// plan.md §1c; the mkCPU_Stage shape from Piccolo/Flute, where a stage
// takes the shared register files as module arguments and is flattened
// into the synthesized CPU):
//   - mkInstrBuffers: the 1Y/2Y instruction buffers with their IC
//     controls, advanced one clock at a time by the core's every-clock
//     rule and read by its preparation arm.
//   - the instruction classification (E-box class, fetches an operand,
//     stores where, progressive) and the I-box-ahead-of-look-ahead
//     hazard test, as functions of the decoded instruction, the
//     storage (for effective addresses) and the look-ahead levels.

package StretchIBox;

import Vector::*;
import ConfigReg::*;
import StretchTypes::*;
import StretchStorage::*;
import StretchDecode::*;
import StretchExecute::*;   // effAddr18/19/24, baWord
import StretchMemory::*;    // installed(): the address-invalid bound
import StretchVFL::*;       // fieldCrosses, effLength

// ---- Instruction classification and the I-box hazard test ----
function Bool isEboxClass(DecodedInstr d);
  case (d) matches
    tagged VflInt .*: return True;
    tagged Connective .*: return True;
    tagged Fp .*: return True;
    default: return False;
  endcase
endfunction
// Does the instruction fetch a memory operand (so a level can be
// loaded with its address from execute()'s side-effect-free bail)?
function Bool fetchesOperand(DecodedInstr d);
  case (d) matches
    // >>> CV IS EXCLUDED BECAUSE ITS OPERAND IS THE ACCUMULATOR, NOT
    // STORAGE, 2026-10-29. <<<  Reference Manual printed p.73, quoted
    // at CV's own arm in StretchExecute: "A field from the ACCUMULATOR
    // is converted as an integer from binary to decimal or from decimal
    // to binary depending on the setting of the radix modifier."  It
    // has no storage operand at all, so `v.a.p != 4` -- which only asks
    // whether the addressing is immediate -- was over-reporting.
    //
    // THE OTHER TWO CONVERSIONS DO FETCH, and were checked rather than
    // assumed: LCV's arm quotes p.72's Field Definition, "the storage
    // operand is defined by the effective address, field length, and
    // byte size in the same manner as in integer arithmetic", and
    // LTRCV's quotes p.73, "the addressed STORAGE field is converted".
    //
    // HOW THE OVER-REPORT WAS FOUND: it was one of eight cases where
    // the preparation arm's probe disagreed with the pure
    // `prepareExec`, and both CV mismatches reported an operand address
    // of 8 -- the accumulator's own word. See docs/ebox_roadmap.md.
    tagged VflInt .v: return v.a.p != 4 && v.code != 6'b011011;
    tagged Connective .c: return c.a.p != 4;
    tagged Fp .f: return f.code == fpop_L;   // FP L; ST fetches nothing
    default: return False;
  endcase
endfunction
// >>> ONE PURE DERIVATION OF AN INSTRUCTION'S ADDRESSES. <<<
//
// `prepareExec` is the beginning of the prepared bundle
// `docs/ebox_roadmap.md` asks for.  It exists because the effective
// address was being derived in THREE independently maintained places --
// here, in `storeTarget` below, and in the arms of `execute()` itself --
// and a review of this file named that as the thing to fix before
// adding a fourth.  `operandTarget` and `storeTarget` are now both
// projections out of this one record, so the `ea` arithmetic and the
// progressive-indexing rule are written once.
//
// IT REPLACES A PROTOCOL, TOO.  `rl_prepare` used to call `ebox.exec`
// with no operands so `execute()` would "bail out" with the address it
// wanted, which made execution serve as both a supposedly
// side-effect-free query and the operation that commits architectural
// effects -- a contract no type enforces.  Running this against that
// probe across the corpus is what tested it: not one address
// disagreement in 5621 checks.
//
// >>> THE PLACE A COPY OF THIS SHAPE SILENTLY DIVERGES: `p` HAS THREE
// STATES, NOT TWO. <<<  `p == 4` is immediate and addresses no storage;
// `p == 0` is an ordinary effective address; any other `p` is
// PROGRESSIVE INDEXING, where the address comes from the index register
// rather than from the instruction.  `fetchesOperand` collapses the
// last two, and `rl_prepare`'s `progressivePending` gate proves those
// paths are live.
typedef struct {
  Maybe#(WordAddr) operandAddr;   // the word a storage operand read wants
  Maybe#(WordAddr) storeAddr;     // the word the instruction writes back
  // >>> DOES THIS INSTRUCTION FINISH WITHOUT READING ANYTHING? <<<
  // The preparation arm's probe used to answer this by RUNNING
  // execute() and seeing whether it asked for a word, which is why
  // execution had to double as a query.  Every cause is a pure
  // condition; they were enumerated by instrumenting each
  // disagreement between the probe and this record and mapping it to
  // its test section (docs/ebox_roadmap.md, "Step 3, scoped").
  Bool completesWithoutFetch;
} PreparedExec deriving (Bits, Eq, FShow);

function PreparedExec prepareExec(StretchStorage st, DecodedInstr d);
  case (d) matches
    tagged VflInt .v: begin
      // Derived exactly as the VflInt arm of execute() derives it (see
      // its `ea`): progressive takes the index register's own address.
      Bool prog = (v.a.p != 0 && v.a.p != 4);
      BitAddr ea = prog ? st.readIndex(v.a.i1).addr
                        : effAddr24(st, v.a.addr, v.a.i1);
      WordAddr w = ea[23:6];
      // The four storing VflInt operations: ST, M+, M+MG, M+1.
      Bool stores = (v.code == 6'b001101) || (v.code == 6'b001001)
                 || (v.code == 6'b101001) || (v.code == 6'b101011);
      // M+/M+1/M+MG, unlike ST since 2026-10-24, still cannot cross a
      // word boundary -- see protViolates' note -- and refuse with OP.
      Bool mPlus = (v.code == 6'b001001) || (v.code == 6'b101001)
                || (v.code == 6'b101011);
      // The three radix conversions are let past the decimal refusal;
      // anything else with the decimal modifier sets OP.
      Bool radixConv = (v.code == 6'b000011) || (v.code == 6'b011011)
                    || (v.code == 6'b100011);
      Bit#(7) len_ = effLength(v.a.length);
      Bool done = (v.m.decimal == 1 && !radixConv)      // decimal refusal
               || (prog && v.a.i1 == 0)                  // progressive, no index
               || (mPlus && fieldCrosses(ea, len_))      // M+ cannot cross
               || dfSuppresses(st, w)                    // DF, mask-dependent
               || !installed(w);                         // AD
      return PreparedExec {
        operandAddr: (v.a.p == 4) ? tagged Invalid : tagged Valid w,
        storeAddr:   stores       ? tagged Valid w : tagged Invalid,
        completesWithoutFetch: done };
    end
    tagged Connective .c: begin
      Bool prog = (c.a.p != 0 && c.a.p != 4);
      BitAddr ea = prog ? st.readIndex(c.a.i1).addr
                        : effAddr24(st, c.a.addr, c.a.i1);
      WordAddr w = ea[23:6];
      Bit#(7) len_ = effLength(c.a.length);
      Bool done = (prog && c.a.i1 == 0)
               || (c.suffix == conn_CM && fieldCrosses(ea, len_))
               || dfSuppresses(st, w)
               || !installed(w);
      return PreparedExec {
        operandAddr: (c.a.p == 4) ? tagged Invalid : tagged Valid w,
        // C and CT are excluded: C writes the accumulator and CT writes
        // nothing, so neither is a store.  See storeTarget's note on
        // how CM's absence here was found.
        storeAddr: (c.suffix == conn_CM) ? tagged Valid w : tagged Invalid,
        completesWithoutFetch: done };
    end
    tagged Fp .f: begin
      // The FP format has no progressive indexing, which is why there
      // is no `prog` split here.
      WordAddr w = effAddr18(st, f.addr, f.idx);
      Bool stores = (f.code == fpop_ST) || (f.code == fpop_M_PLUS)
                 || (f.code == fpop_M_PLUS_MG) || (f.code == fpop_SRD)
                 || (f.code == fpop_SLO) || (f.code == fpop_SRT);
      return PreparedExec {
        // FP L only; ST fetches nothing.
        operandAddr: (f.code == fpop_L) ? tagged Valid w : tagged Invalid,
        storeAddr:   stores             ? tagged Valid w : tagged Invalid,
        completesWithoutFetch: dfSuppresses(st, w) || !installed(w) };
    end
    default: return PreparedExec { operandAddr: tagged Invalid,
                                   storeAddr:   tagged Invalid,
                                   completesWithoutFetch: False };
  endcase
endfunction

function Maybe#(WordAddr) operandTarget(StretchStorage st, DecodedInstr d) =
  prepareExec(st, d).operandAddr;

// The word an E-box level stores to (Fp ST/M+/M+MG, VflInt
// ST/M+/M+MG/M+1), for the store-close-to-fetch hazard; Invalid for a
// level that writes only the accumulator (L/+/E+/F+/SHF/*/D*/*+) or
// nothing; LFT writes only the factor register, word 14.
// (The derivation itself now lives in `prepareExec` above, so the `ea`
// arithmetic is written once; everything above this line is why each
// opcode is or is not in the storing set.)
function Maybe#(WordAddr) storeTarget(StretchStorage st, DecodedInstr d) =
  prepareExec(st, d).storeAddr;

function Bool hasProgressive(DecodedInstr d);
  case (d) matches
    tagged VflInt .v: return v.a.p != 0 && v.a.p != 4;
    tagged Connective .c: return c.a.p != 0 && c.a.p != 4;
    default: return False;
  endcase
endfunction

// ---- Stage 3b (plan §6c): may an I-box-class instruction execute now,
// with look-ahead levels pending? It may unless a level's operand
// word is one it reads or writes, or it branches on an arithmetic
// indicator (which needs the levels drained). The operand words use
// the same effective-address arithmetic as execute().
// The special-storage words the E-box reads and writes AT EXECUTION --
// the zeros/ones counts (7), the accumulator (8, 9) and its sign byte
// (10), the indicators (11), mask (12), remainder (13), factor (14),
// transit (15). An I-box store to one of them (Z,$IND to clear the
// indicators, Z,$L ...) must wait for every pending level to retire,
// or it lands BEFORE the E-box instruction that precedes it in the
// program and is undone / un-cleared by it. Found by jb_af1c F204D12:
// L(U) of an XPL-range operand followed by Z,$IND then M+ -- the model
// let Z,$IND run ahead of the load, which then set XPL after the
// clear, and the block's "other exponent indicators off" check failed.
// (Index words 16-31 are the I-box's own and are covered by the index
// hazard checks above, not by this.)
function Bool eboxRegister(WordAddr w) = (w >= 7 && w <= 15);

function Bool levelHolds(Vector#(4, LaLevel) lv, WordAddr w);
  Bool r = False;
  for (Integer k = 0; k < 4; k = k + 1) begin
    if (lv[k].da matches tagged Valid .a &&& lv[k].valid &&& a == w) r = True;
    if (lv[k].storeAddr matches tagged Valid .sa &&& lv[k].valid &&& sa == w) r = True;
  end
  return r;
endfunction

// Mask of the index indicators in the indicator word (bit n is w[63-n]).
Word64 indexIndMask = (64'h1 << (63 - ind_XF)) | (64'h1 << (63 - ind_XCZ)) | (64'h1 << (63 - ind_XVLZ))
                    | (64'h1 << (63 - ind_XVZ)) | (64'h1 << (63 - ind_XVGZ)) | (64'h1 << (63 - ind_XL))
                    | (64'h1 << (63 - ind_XE)) | (64'h1 << (63 - ind_XH));
function Bool indexIndicator(Bit#(6) n) =
  (n == ind_XF || n == ind_XCZ || n == ind_XVLZ || n == ind_XVZ || n == ind_XVGZ
   || n == ind_XL || n == ind_XE || n == ind_XH);

function Bool iboxHazard(StretchStorage st, Bool guessPending, DecodedInstr d, Vector#(4, LaLevel) lv);
  Bool pending = False;
  for (Integer k = 0; k < 4; k = k + 1) if (lv[k].valid) pending = True;
  Bool h = True;   // anything not listed (Transmit, I/O, EX...): drain first
  case (d) matches
    tagged DirIndex .x: begin
      HWordAddr ea = effAddr19(st, x.addr, x.idx);
      Bool refillWord = (x.code == dixop_V_PLUS_CR) && levelHolds(lv, zeroExtend(st.readIndex(x.j).refill)); // V+CR
      h = levelHolds(lv, ea[18:1]) || refillWord;
    end
    tagged ImmIndex .x:
      h = (x.code == 4'b0111 || x.code == 4'b1111)                          // V+ICR / V-ICR
          && levelHolds(lv, zeroExtend(st.readIndex(x.j).refill));
    tagged CountBranch .x:
      h = (x.refill == 1) && levelHolds(lv, zeroExtend(st.readIndex(x.j).refill));
    tagged BranchInd .x: h = !indexIndicator(x.indNum);
    tagged BranchOrMisc .x: begin
      // Unconditional branches drain the levels first: a halt (a
      // branch to itself) must not be reported while E-box work is
      // still in the look-ahead, and on the real machine a taken
      // branch empties the look-ahead anyway (Perf. Char. p.3-18:
      // "BD ... empty the LA completely"). NOP is free.
      if (!x.misc) h = (x.code != 3'b110);
      else if (x.code == 3'b100) begin                                       // Z
        WordAddr zw = baWord(effAddr24(st, {x.addr, 5'b0}, x.idx));
        h = levelHolds(lv, zw) || eboxRegister(zw);
      end
      else if (x.code == 3'b000 || x.code == 3'b001)                         // R / RCZ
        h = levelHolds(lv, zeroExtend(st.readIndex(x.idx).refill));
      // EX/EXIC: drain the levels first, unconditionally.  BOTH ARE
      // IMPLEMENTED (EX 2026-09-25, EXIC 2026-09-29) and for both this
      // is a real requirement rather than the "anything not listed"
      // default it used to be for EXIC -- the subject instruction is
      // not known until its word has been fetched, so no hazard test on
      // the EXECUTE itself could cover what the subject reads or
      // writes.  EXIC is one indirection worse still: not even the
      // subject's ADDRESS is known until the pseudo-instruction counter
      // has been read, and the counter word is then WRITTEN.  Draining
      // is the only answer available before the fetch, and it is also
      // what the real machine does for anything that disturbs the
      // look-ahead.
      else h = True;
    end
    tagged Sic .x: begin
      BitAddr ea = effAddr24(st, x.addr, x.idx);
      h = levelHolds(lv, ea[23:6]) || eboxRegister(ea[23:6])
          || iboxHazard(st, guessPending, decodeHalfWord(x.inner), lv);
    end
    default: h = True;
  endcase
  return (pending && h) || (guessPending && isIboxStore(d));
endfunction

function Bool isIboxStore(DecodedInstr d);
  case (d) matches
    tagged DirIndex .x: return x.code[4] == 1;          // SX/SV/SC/SR
    tagged BranchOrMisc .x: return x.misc && x.code == 3'b100;  // Z
    tagged Sic .*: return True;
    tagged Transmit .*: return True;
    default: return False;
  endcase
endfunction

// ---- The instruction buffers 1Y/2Y and their IC controls ----
interface InstrBuffers;
  // One clock of the IC controls: program-store compare, restart
  // (drop everything buffered and refetch from `pcw`), collect arrived
  // words, free passed ones, issue at most one prefetch.
  method Action advance(WordAddr pcw, Bool restart);
  // A prefetched, checked instruction word, if buffered.
  method Maybe#(Word64) lookup(WordAddr w);
endinterface

module mkInstrBuffers #(StretchStorage st) (InstrBuffers);
  // The instruction unit's instruction buffers 1Y/2Y and IC controls
  // (docs/microarchitecture_plan.md stage 2a; Blosk TR00.722 pp.7-10,
  // 25; CE manual figs 3.1.1-3.1.5). Each Y holds one 64-bit
  // instruction word fetched ahead of the instruction counter through
  // its own bus channel (StretchStorage.fetchReq/fetchReady/fetchResp,
  // return tags 1Y/2Y); a word is usable one I-checker cycle (two
  // clocks) after it arrives. The IC controls keep both filled with
  // the next words in sequence (`nextFetch`), free a Y once the
  // instruction counter has passed its word, and invalidate both on a
  // taken branch, a setPC, or a store to a prefetched word (program
  // store compare, Blosk p.21). A fetch still in flight for an
  // invalidated Y is discarded on arrival.
  // ConfigReg: advance() writes these while the core's preparation arm
  // calls lookup() in the same clock and writes pcReg/branchSeq that
  // advance()'s caller reads -- every read is of the pre-clock value,
  // which a ConfigReg's unordered read/write states exactly and an
  // ordinary Reg would make a scheduling cycle.
  Vector#(2, Reg#(YReg)) yr <- replicateM(mkConfigReg(YReg{valid: False, pending: False,
                                                      discard: False, addr: 0, data: 0, chk: 0}));
  Reg#(WordAddr) nextFetch <- mkReg(0);

  method Action advance(WordAddr pcw, Bool restart);
    Vector#(2, YReg) ny = readVReg(yr);
    WordAddr nf = nextFetch;
    // Where the fetch stream must go BACK to, if a store invalidated a
    // word the instruction counter has not passed yet. See below.
    Maybe#(WordAddr) rewind = tagged Invalid;
    for (Integer k = 0; k < 2; k = k + 1) begin
      // Program store compare: a store to a prefetched word invalidates it.
      if (st.recentStore() matches tagged Valid .sw &&& ny[k].addr == sw && (ny[k].valid || ny[k].pending)) begin
        ny[k].valid = False;
        if (ny[k].pending) ny[k].discard = True;
        // ... and REWIND the fetch stream to it. Invalidating alone is
        // not enough: prefetch below only ever issues at nextFetch and
        // moves forward, so a word at or ahead of the instruction
        // counter would be dropped and never re-read, and the core
        // would stall on it forever (mkStretchCore's prepare arm leaves
        // `prepared` Invalid when lookup misses, and simply retries).
        // jb_af1c F212A25 is exactly that program: a CM1111 writes six
        // ones into the address field of the VERY NEXT instruction and
        // then executes it, and before this the model livelocked at
        // 016500.00, the modified instruction's own address.
        // A store to a word the counter has ALREADY passed must not
        // drag the stream backward, hence the sw >= pcw guard.
        if (sw >= pcw)
          rewind = tagged Valid (case (rewind) matches
                                   tagged Valid .r : (r < sw ? r : sw);
                                   default         : sw;
                                 endcase);
      end
      // Restart (taken branch or setPC): drop everything buffered.
      if (restart) begin
        ny[k].valid = False;
        if (ny[k].pending) ny[k].discard = True;
      end
      // Collect an arrived word; usable after the I-checker cycle.
      if (ny[k].pending && st.fetchReady(fromInteger(k))) begin
        let d <- st.fetchResp(fromInteger(k));
        ny[k].pending = False;
        if (ny[k].discard) ny[k].discard = False;
        else begin ny[k].valid = True; ny[k].data = d; ny[k].chk = 2; end
      end else if (ny[k].valid && ny[k].chk != 0)
        ny[k].chk = ny[k].chk - 1;
      // Free a word the instruction counter has passed.
      if (ny[k].valid && ny[k].addr < pcw) ny[k].valid = False;
    end
    if (restart) nf = pcw;
    // A rewind only ever moves the stream back, never forward.
    else if (rewind matches tagged Valid .r &&& r < nf) nf = r;
    // nextFetch means "the lowest word not yet buffered", and a rewind
    // can break that: the word after the invalidated one is usually
    // still held by the other Y. Requesting it again would put BOTH
    // buffers on the same address, and then neither can ever be freed
    // by "the instruction counter has passed it" (only strictly-less
    // addresses are), so no slot frees, the word after them is never
    // fetched, and the core wedges as soon as it needs it. That is not
    // hypothetical: it is what jb_af1c F212A25 did after the rewind
    // alone was added -- the stall simply moved from 016500.00 to
    // 016501.40. Skipping addresses already held or outstanding
    // restores the invariant. Two passes suffice for two buffers.
    // "Held" means the slot will actually DELIVER that word: valid, or
    // pending without discard. A pending-with-discard slot holds
    // nothing -- its arriving word is thrown away -- and treating it as
    // held is wrong in exactly the case that matters most, a taken
    // branch: `restart` invalidates every slot and marks the pending
    // ones discard, so counting them would skip `pcw` itself and the
    // branch target would never be fetched. The first version of this
    // loop did count them and livelocked Problem 2.2 Method 2; the
    // full suite caught it.
    for (Integer t = 0; t < 2; t = t + 1)
      for (Integer j = 0; j < 2; j = j + 1)
        if ((ny[j].valid || (ny[j].pending && !ny[j].discard))
            && ny[j].addr == nf) nf = nf + 1;
    // Issue at most one prefetch per clock into a free Y, in order.
    Bool issued = False;
    for (Integer k = 0; k < 2; k = k + 1)
      if (!issued && !ny[k].valid && !ny[k].pending && !restart) begin
        st.fetchReq(fromInteger(k), nf);
        ny[k].pending = True; ny[k].discard = False; ny[k].addr = nf; ny[k].chk = 0;
        nf = nf + 1;
        issued = True;
      end
    writeVReg(yr, ny);
    nextFetch <= nf;
  endmethod

  method Maybe#(Word64) lookup(WordAddr w);
    Maybe#(Word64) r = tagged Invalid;
    for (Integer k = 0; k < 2; k = k + 1)
      if (yr[k].valid && yr[k].chk == 0 && yr[k].addr == w) r = tagged Valid yr[k].data;
    return r;
  endmethod
endmodule

endpackage
