// StretchExecute.bsv
//
// Execute stage. Implements the subset of the IBM 7030 instruction set
// documented as in-scope in bsv/README.md: VFL binary integer L/ST/+/M+/K
// (Reference Manual 22-6530-2 pp.~86-95) with both standard address
// modification and progressive indexing (P in {1,2,3,5,6,7}, p.21),
// the sixteen Connectives (C/CM/CT, p.75-77, with p.75's byte-size
// expansion as of 2026-10-19 -- see StretchVFL's connExpand), direct
// and immediate index arithmetic
// (pp.22-27), count-and-branch and branch-on-indicator (pp.~26-27,
// pocket card X22-6533-1 "INDEX BRANCHING"/"INDICATOR BRANCHING"),
// unconditional branching, Store Zero / Refill, and forward non-swap
// Transmit with an IMMEDIATE COUNT OF ONE (the only count this model
// can honour -- Ref. Manual pp.30-31).
//
// Every decoded format/opcode NOT yet implemented -- decimal
// arithmetic, radix conversion, interrupts, EXIC, RNX/LVE/SVA, LVS,
// Transmit backward/swap/multi-word/direct-count -- sets indicator 15
// (OP, Operation Code Invalid) and otherwise acts as a no-op, and for
// Transmit that was only TRUE OF `backward` until 2026-09-22: see the
// Transmit arm and StretchTypes' Transmit comment.
//
// EX (EXECUTE) LEFT THAT LIST on 2026-09-25 and EXIC did not.  The two
// share the subject-fetch machinery below (the `ExSubject` context, the
// EX arm's bail-out, mkEBox's subject swap, the EXE suppression in the
// five branch arms); what EXIC adds on top is its pseudo-instruction
// counter -- Ref. Manual printed p.50: "Bits 0-18 of the full-word
// addressed by bits 0-17 of the effective address are used as a
// pseudo-instruction counter... After the subject instruction has been
// fetched but prior to its execution, the pseudo-instruction counter is
// stepped" -- plus its two address restrictions (pseudo-IC not in 0-15,
// subject at 32.00 and above).  None of that is built; EXIC still
// reaches setOpInvalid, deliberately, so that the counter is not
// half-stepped by a partial implementation.
//
// Matching the documented
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
import StretchDiskSource::*;   // DiskIndex / ArcAddr / arcWords, for
                                // the disk arms of the IoOp case
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
  // BRANCH RELATIVE's `target` is a DISPLACEMENT, not an address: the
  // caller adds the stepped instruction counter.  evalBranch cannot,
  // having no fall-through in scope, so every caller must -- which is
  // why this flag exists rather than a second target field.
  Bool      relative;
} BranchOutcome deriving (Bits, Eq);

function BranchOutcome evalBranch(StretchStorage st, DecodedInstr d, Word64 ind0,
                                  Vector#(2, Word64) prefetch, Bit#(2) prefetchCount,
                                  Bit#(2) slot);
  BranchOutcome o = BranchOutcome {
    needsRead: tagged Invalid, readsUsed: 0, doIdxWrite: False, idxWriteReg: 0,
    idxWriteVal: IndexWord{addr:0, sign:0, flag:0, spare:0, count:0, refill:0},
    ind: ind0, taken: False, target: 0, relative: False };
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
      // (decks/ibox1_p46_p51_span.strap) hang at their
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
                       flag: x.flag, spare: x.spare, count: newCount, refill: x.refill};
      // Prefetch/bail-out shape, inlining maybeRefill's own
      // condition (doRefill && x1.count==0) rather than calling it.
      Bool doRefill = (cb.refill == 1) && (x1.count == 0);
      // DF'S MASK-DEPENDENT HALF for p.32's CLASS 3 -- see dfSuppresses.
      // ASKED HERE, BEFORE THE BAIL-OUT, and not beside the dfSignal
      // call inside it: that is the whole content of the placement.
      // Tested later, the refill read would already have been ISSUED
      // and its word landed in prefetch[slot] before the arm was
      // skipped, and printed p.45 for indicator 20 says "the fetch did
      // not take place".  Nothing downstream could see the difference,
      // so the wasted read would be silent -- the one shape this
      // project's own rule about green tests is aimed at.
      Bool refillSupp = doRefill && dfSuppresses(st, zeroExtend(x1.refill));
      if (refillSupp) begin
        // THE WHOLE COUNT-BRANCH-REFILL IS SUPPRESSED: no index write,
        // no index result indicators, and NO BRANCH.  printed p.52
        // names this instruction outright, which is better authority
        // than p.45's general "the entire operation was suppressed"
        // because it settles the BRANCH half rather than leaving it to
        // inference: "if a STORE INSTRUCTION COUNTER IF COUNT, BRANCH
        // AND REFILL is executed as the subject instruction of EXECUTE,
        // it is possible for (1) the condition for branching to be met,
        // (2) the effective SIC address to be invalid, (3) the effective
        // branch address and the refill address to be protected, and
        // (4) the count to reach zero... When, however, in this example,
        // the condition for branching is not met, THE ENTIRE SUBJECT
        // INSTRUCTION IS STILL SUPPRESSED but only indicator DF is
        // actuated (the DF mask bit is assumed to be one).  Indicator DF
        // is actuated since THE TEST FOR THE REFILLING IS INDEPENDENT OF
        // THE TEST FOR A SUCCESSFUL BRANCH."
        //
        // That last clause is also the manual's own endorsement of the
        // shape already here: `doRefill` is computed from the count
        // alone and never from `take`.
        //
        // o.ind IS BUILT FROM ind0, not from o.ind.  The placement
        // hazard the note below records -- the signal must come AFTER
        // `o.ind = setIndexResultIndicatorsF(ind0, x1)`, which assigns
        // from ind0 and would discard it -- simply does not arise on
        // this path, because suppression never calls that function.
        //
        // o.readsUsed stays at its initialiser 0: nothing was read, and
        // SIC places its own read in the slot AFTER it.
        //
        // o.taken stays False, so a SIC prefix's store is suppressed as
        // a CONSEQUENCE rather than by a second test -- which is the
        // other half of p.52's example, where the branch not being
        // taken is exactly why the SIC address is never encountered.
        o.ind = dfSignal(st, zeroExtend(x1.refill), ind0);
      end else if (doRefill && prefetchCount < slot + 1) begin
        o.needsRead = tagged Valid zeroExtend(x1.refill);
      end else begin
        IndexWord x2 = doRefill ? unpackIndexWord(prefetch[slot[0]]) : x1;
        o.readsUsed = doRefill ? 1 : 0;
        o.doIdxWrite = True; o.idxWriteReg = cb.j; o.idxWriteVal = x2;
        o.ind = setIndexResultIndicatorsF(ind0, x1); // per p.23: indicators reflect
                                                      // state *before* any refill.
        // DF, p.32 class 3, the other half of the sentence: "the
        // refill address used in INDEX REFILL OPERATIONS".  AFTER the
        // line above, not before it -- that one assigns from `ind0`
        // and would discard the signal.  Inside `doRefill`, for the
        // reason the R/RCZ arm's own note gives: a refill that does
        // not happen reads nothing.
        if (doRefill) o.ind = dfSignal(st, zeroExtend(x1.refill), o.ind);
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
      // BRANCH RELATIVE (code 011) is NOT an absolute branch, and this
      // model does not implement it -- so it fails loud rather than
      // branching to the wrong place.  Two primary sources:
      //
      //   * X22-6533 pocket card, UNCONDITIONAL BRANCHING: the codes are
      //     B 010000000, BR 011000000, BE 000000000, BD 001000000,
      //     BEW 100000000, NOP 110000000, and BR is named "Branch
      //     Relative" -- a distinct operation, not a spelling of B.
      //   * Reference Manual p.42: "A simple storage of the instruction
      //     counter without branching action is accomplished by STORE
      //     INSTRUCTION COUNTER IF BRANCH RELATIVE with a branch address
      //     of 0."  A branch address of 0 meaning NO BRANCHING ACTION is
      //     only possible if the address is a displacement.
      //
      // The base is almost certainly the stepped instruction counter:
      // p.39 says "after an instruction is fetched, but before its
      // execution, the instruction counter contents are stepped in
      // ordinary fashion... prior to any attempt to replace the
      // instruction counter contents", so during execution the counter
      // already holds the fall-through, and fall-through + 0 is exactly
      // "no branching action".  What is NOT established here is whether
      // the displacement is signed and in what units, so implementing it
      // would be a guess; setOpInvalid is the honest state until a deck
      // block or the Unconditional Branching page settles it.  Nothing
      // in the suite uses BR -- the opcode-coverage audit is what found
      // it -- so nothing regresses.
      if (!bm.misc && bm.code != 3'b110) begin
        o.taken = True;
        o.target = effAddr19(st, bm.addr, bm.idx);
        // BRANCH RELATIVE (011), p.40 verbatim: "This instruction
        // causes the absolute value of the effective address to be
        // added to the instruction counter contents.  Bits 0-18 of the
        // sum replace the instruction counter contents."  The base is
        // the STEPPED counter (p.39 steps it before execution), so
        // `target` is a displacement here and the caller adds the
        // fall-through; the 19-bit wrap IS "bits 0-18 of the sum".
        //
        // p.42 corroborates and is what broke the old absolute
        // reading: "a simple storage of the instruction counter
        // WITHOUT BRANCHING ACTION is accomplished by STORE
        // INSTRUCTION COUNTER IF BRANCH RELATIVE with a branch address
        // of 0."  Zero lands on the fall-through only if the base is
        // the stepped counter; absolute, it would branch to 0.0, which
        // p.39 calls an invalid branching address.
        //
        // KNOWN LIMIT, deliberate.  p.40 says ABSOLUTE VALUE, and an
        // effective address can only go negative through index
        // modification (p.20: the instruction's address part is "a
        // positive unsigned field").  effAddr19 returns an unsigned
        // 19-bit result with no sign carried alongside, so an
        // index-modified BR whose effective address goes negative uses
        // the wrapped value, not the magnitude.  Nothing transcribed
        // exercises it and inventing a representation would be
        // guessing.
        o.relative = (bm.code == 3'b011);
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

// STORAGE PROTECTION / ADDRESS MONITORING, for STORE-type references.
// Two areas: the permanently protected words, and the one the boundary
// registers name.
//
// p.31: "The monitoring of references to locations 0-31 is independent
// of the contents of the boundary registers.  Locations 1, 2, and 3 are
// referred to as the permanently protected area of storage.
// References to these locations always give an address monitoring
// signal, regardless of the contents of the boundary registers or the
// setting of the boundary control bit.  References to locations 0 and
// 4 through 31, inclusive, never cause an address monitoring signal."
//
// p.32 on a STORE: "Since this indicator [DS] is permanently masked
// on, storing in core storage is always suppressed, and the operation
// is always terminated."  DS is bit 19 and mask bits 0-19 are
// permanently one, so a store-type reference is ALWAYS suppressed --
// no mask-dependent branch, unlike DF and IF.
//
// Gated on the enable bit because p.45 defines the indicator as a
// store attempted "while the interruption system was enabled".
//
// THE BOUNDARY REGISTERS, now consulted.  p.31: "A core storage area
// is defined by placing an address in each of two address boundary
// registers.  This area includes the word specified by the address in
// the lower boundary register and all words in subsequent locations up
// to, but not including, the address in the upper boundary register...
// If it is equal or smaller, no words are contained in the core
// storage area.  The upper boundary and lower boundary registers are
// located in bits 0-17 and 32-49, respectively, of storage location 3.
//
// The boundary control bit, bit 57 of storage location 3, determines
// which condition will cause an address monitoring signal.  When the
// boundary control bit is zero, a signal is obtained for a comparand
// INSIDE the specified area.  When the boundary control bit is one, a
// signal is obtained for a comparand OUTSIDE the specified area."
//
// Note the order -- upper first, lower second -- and that the interval
// is HALF-OPEN: [lower, upper).  `upper <= lower` needs no separate
// guard; the comparison is already false for every address, which is
// what "no words are contained" means.
//
// THE 0-31 CARVE-OUT GATES THE BOUNDARY COMPARE; it does not sit
// beside it.  That is the word INDEPENDENT in the p.31 sentence quoted
// at the top of this comment, read strictly: for an address below 32
// the boundary registers are not consulted at all.
//
// Writing that as `permanent || boundary` would be wrong, and wrong in
// a way that matters here: with the control bit set (signal outside),
// words 4-31 are outside any area a program can name, so they would
// all signal -- and words 4-31 are exactly the special registers the
// 43 constant-address st.writeWord sites below write without a guard.
// The carve-out is what keeps that argument true, so it is structural,
// not decoration.
//
// AN ADDRESS-INVALID ADDRESS IS EXEMPT.  p.32: "An address which
// actuates indicator AD, address invalid, is not compared with the
// contents of the boundary registers and cannot actuate any of the
// address alarm indicators."  Uninstalled addresses are that class
// (StretchMemory's `installed`); the model does not yet raise AD for
// them, but it must not raise DS either, which without this clause a
// control bit of one would do for every one of them.
//
// ONE PREDICATE, USED AT EACH COMPUTED-ADDRESS STORE.  Of the 64
// st.writeWord sites in this file, 43 write a CONSTANT special-register
// address -- the accumulator halves, its sign byte, the zeros/ones
// counts, remainder, factor -- all in 4-31, which p.31 says never
// signal.  Only the computed-address stores can reach the monitored
// area, and they share this one function rather than repeating the
// rule.
//
// STILL NOT IMPLEMENTED, and each is its own piece of work.  Full
// operation TERMINATION for DS (p.32 terminates the whole operation;
// this suppresses only the store, so a BB whose write is suppressed
// still branches).  DF's MASK-DEPENDENT half is now IMPLEMENTED for
// p.32's class 1 AND for the six class-3 refill sites that are not
// progressive indexing -- see dfSuppresses below, which carries the
// scope statement and says which five are left and why p.53 makes
// them a different mechanism rather than an oversight.
// p.32's class 3 for DF, "the refill address used in
// index refill operations and the operations REFILL and REFILL ON
// COUNT ZERO" -- DONE.  All eleven refill reads in this file signal:
// R and RCZ on both their paths, CBR, V+CR, V+ICR, V-ICR, and the
// VFL-format ones that progressive indexing issues (L/+/K through
// their shared trailing block, ST/M+/CM inline).  Each sits INSIDE
// its own suppression gate, because a refill that is computed and
// then skipped reads nothing and p.32 monitors addresses "actually
// used".  Class 2 is moot and class 3's INDICATOR is complete.
// ITS TWO HALVES ARE NOT AT THE SAME PLACE, and "class 3 is DONE"
// above means the INDICATOR only: the SUPPRESSION is asked at six of
// those eleven -- CBR/CBRZ, V+CR, V+ICR, V-ICR and R/RCZ on both
// paths -- and deliberately not at the five progressive-indexing ones,
// which p.53 puts under TERMINATION instead.  dfSuppresses carries the
// list and the sentences.
//
// CLASS 1 HAS FIVE SITES, not four, and the earlier wording here that
// called it complete at four is corrected rather than deleted, because
// that claim is exactly the kind this project has watched propagate.
// The five are the four instruction formats listed above and p.52's
// read-only BRANCH ON BIT.  ALL FIVE NOW SIGNAL AND ALL FIVE
// SUPPRESS.  The fifth lives in the BitBranch arm rather than here,
// because p.52's rule for it is stated per-clause on the instruction's
// own bits 60-61 and its suppression has to sit beside the branch
// decision; the sentence is quoted in full there.
// And the straddling rule ("an instruction or data
// field which straddles a boundary always gives an address monitoring
// signal", p.31) for STORES: dfSignal's callers ask about both words
// of a crossing field, the store sites still compare one word each.
function Bool protViolates(StretchStorage st, WordAddr a);
  Word64  b     = st.readBoundaries();
  WordAddr upper = b[63:46];   // IBM bits 0-17
  WordAddr lower = b[31:14];   // IBM bits 32-49
  Bit#(1)  ctl   = b[6];       // IBM bit 57
  Bool inArea = (a >= lower) && (a < upper);
  Bool signalled = (a < 32) ? (a >= 1 && a <= 3)
                            : ((ctl == 1) ? !inArea : inArea);
  return st.irqEnabled() && installed(a) && signalled;
endfunction

function BitAddr effAddr24(StretchStorage st, BitAddr raw, Bit#(4) idx);
  if (idx == 0)
    return raw;
  else begin
    IndexWord x = st.readIndex(idx);
    return (x.sign == 1) ? (raw - x.addr) : (raw + x.addr);
  end
endfunction

// THE ADDITION HAPPENS IN THE 24-BIT BIT-ADDRESS DOMAIN, always.
// Reference Manual p.20-21: "The value field of the index is
// interpreted as a signed 24-bit field.  The address part of the
// instruction is interpreted as a positive unsigned field.  The length
// of the address field depends upon the instruction class.  THE MISSING
// LOW-ORDER BITS, IF ANY, ARE ALWAYS ASSUMED TO BE ZERO", and then
// (p.21) "The effective address which results from an indexing
// operation always has 24 numeric bits and a sign.  Depending upon the
// operation, a full-word, half-word, or bit-address may be required.
// In each case, ONLY THE APPLICABLE PART of the effective address is
// used.  The non-applicable part is ignored."
//
// So the INSTRUCTION's short address is what gets aligned -- extended
// with low-order zeros into the 24-bit domain -- and the index value
// goes in as-is.  The scaling lives in the programmer's constant, never
// in a hardware shift: ONE WORD IS AN INDEX VALUE OF 64 AND ONE
// HALF-WORD IS 32.  Corroborated by p.41's index-increment table, which
// equates "H add half to value" with "add one in bit position 18" and
// "+ add one to value" with bit position 17 -- weights 2**5 and 2**6
// over a value field whose bits are 0-23.
//
// These two helpers previously added the value STRAIGHT to a word or
// half-word address, which is wrong by 64x and 32x respectively.
// Nothing caught it because no transcribed deck indexes a
// floating-point or branch address at all -- the same fact that let
// mutation_score.py's branch-target-unmodified survive until
// branch_index_modified.strap existed.  effAddr24 was always right,
// because for it the instruction address is already a bit address and
// there is nothing to align.
function HWordAddr effAddr19(StretchStorage st, HWordAddr raw, Bit#(4) idx);
  if (idx == 0)
    return raw;
  else begin
    IndexWord x = st.readIndex(idx);
    BitAddr base = {raw, 5'b0};        // 19-bit half-word address -> bits 0-18
    BitAddr ea   = (x.sign == 1) ? (base - x.addr) : (base + x.addr);
    return ea[23:5];                   // only the applicable part
  end
endfunction

function WordAddr effAddr18(StretchStorage st, WordAddr raw, Bit#(4) idx);
  if (idx == 0)
    return raw;
  else begin
    IndexWord x = st.readIndex(idx);
    BitAddr base = {raw, 6'b0};        // 18-bit word address -> bits 0-17
    BitAddr ea   = (x.sign == 1) ? (base - x.addr) : (base + x.addr);
    return ea[23:6];                   // only the applicable part
  end
endfunction

// ---------------------------------------------------------------------
// EXECUTION OPERATIONS (Reference Manual printed pp.49-50, PDF 52-53),
// read first-hand at 300 dpi.  The machinery is in three pieces and
// this is the first of them:
//
//   1. `exSubjectAddr` here -- WHERE the subject instruction lives.
//   2. execute()'s EX arm -- asks the E-box to fetch that word and
//      does nothing else.
//   3. mkEBox.resume() -- decodes the fetched word and installs the
//      SUBJECT as the held instruction, keeping the EX's own pc/len.
//
// p.50, EXECUTE: "Bits 0-18 of the effective address form the address
// of the location of a subject instruction that is fetched and
// executed.  Subject instructions of EXECUTE may occupy any addressable
// location."  BITS 0-18 IS A HALF-WORD ADDRESS, which is why this uses
// effAddr19 and not the effAddr24/baWord pair the Z and R arms beside
// EX use -- those two address a WORD and throw bit 18 away.  The deck
// settles it rather than the type: routine 1262 TEST 1CC's "EX,I62B6"
// prints machine code 24205.52, and octal pair 52 = 101010 has bit 18 =
// 1, so that subject sits at half-word 024205.40 (the reading is worked
// out in decks/ax5b_162_test1cc.strap's header).
//
// Returns Invalid for anything that is not an EXECUTE, which is how
// mkEBox tells "an operand word arrived" from "a subject instruction
// arrived": an EX is the only instruction whose bail-out read is a
// fetch of something to be DECODED rather than something to be USED.
// EXIC IS DELIBERATELY NOT RECOGNISED HERE and never will be -- see
// exicPsicAddr below, which is a different function for a reason that
// is not stylistic: EXIC's subject address is not a function of the
// instruction at all.  It is a function of a WORD THAT MUST BE FETCHED
// FIRST, so no `exSubjectAddr` case could compute it.
// ---------------------------------------------------------------------
function Maybe#(HWordAddr) exSubjectAddr(StretchStorage st, DecodedInstr d);
  case (d) matches
    tagged BranchOrMisc .bm:
      return (bm.misc && bm.code == 3'b010)
               ? tagged Valid effAddr19(st, bm.addr, bm.idx)
               : tagged Invalid;
    default: return tagged Invalid;
  endcase
endfunction

// EXECUTE INDIRECT AND COUNT -- WHERE THE PSEUDO-INSTRUCTION COUNTER
// LIVES.  Reference Manual printed p.50 (PDF 53), read first-hand at
// 300 dpi: "Bits 0-18 of the full-word addressed by BITS 0-17 of the
// effective address are used as a pseudo-instruction counter."
//
// BITS 0-17 IS A WORD ADDRESS -- ONE BIT NARROWER THAN EX'S -- so this
// is the Z / R / RCZ idiom (effAddr24 then baWord) and NOT effAddr19.
// Bit 18 of the effective address is thrown away, exactly as it is by
// the three arms beside this one.  The difference is the manual's own:
// EX says "bits 0-18 of the effective address" (a half-word: a subject
// instruction can begin in either half of a word), EXIC says "bits 0-17"
// (a full word: a pseudo-instruction counter cannot).
//
// Returns Invalid for anything that is not an EXIC.  In mkEBox it does
// double duty as the test "is the held instruction an EXIC that has not
// yet read its pseudo-IC", which is exactly the state HeldOp.exic being
// Invalid records; see the invariant stated there.
function Maybe#(WordAddr) exicPsicAddr(StretchStorage st, DecodedInstr d);
  case (d) matches
    tagged BranchOrMisc .bm:
      return (bm.misc && bm.code == 3'b011)
               ? tagged Valid baWord(effAddr24(st, {bm.addr, 5'b0}, bm.idx))
               : tagged Invalid;
    default: return tagged Invalid;
  endcase
endfunction

// WHAT execute() NEEDS TO KNOW when the instruction it is running is
// the SUBJECT of an execution operation rather than an instruction of
// the main program.  Two facts, and both of them are about rules the
// subject's own arm cannot see for itself:
//
// `under` -- p.49: "the subject instruction is not allowed to change
//   the state of the interruption system or replace the contents of the
//   instruction counter.  The execution exception indicator (EXE) is
//   turned on by any branch operation of a subject instruction in which
//   the condition for a successful branch is met.  When indicator EXE
//   is actuated, the branch and all associated operations are not
//   performed."  p.45 item 18 says how much is "all": "The subject
//   operation was suppressed."  So every arm that can branch asks this
//   flag and, when its condition is met, sets EXE and does NOTHING
//   ELSE -- not the branch, not BD's disabling, not CBR's counting and
//   refilling, not SIC's store, not BRANCH ON BIT's bit change.
//
// `ifSig` -- the accumulated p.32 class-1 alarm for the SUBJECT
//   LOCATIONS of the chain, computed by mkEBox because only the E-box
//   sees every level.  It has to be carried rather than recomputed
//   here: execute()'s indicator word is DISCARDED on every call that
//   bails for a read (see the function's tail), and every level of a
//   multi-level EX is exactly such a call, so an intermediate level's
//   alarm would otherwise be lost.
typedef struct {
  Bool under;
  Bool ifSig;
} ExSubject deriving (Bits, Eq, FShow);

ExSubject notSubject = ExSubject { under: False, ifSig: False };

// WHAT AN EXIC IN FLIGHT HAS TO REMEMBER, and every field is here
// because mkEBox cannot recompute it later.
//
// `psAddr` -- where the pseudo-instruction counter lives.  Recomputing
//   it from the instruction would mean calling exicPsicAddr a third
//   time, three clocks after the first; the EX arm's note explains why
//   no index-register write can intervene today, but carrying the
//   answer makes the step independent of that argument.
// `psWord` -- the pseudo-IC word AS READ.  The step is a
//   READ-MODIFY-WRITE of bits 0-18 only: p.50 says "bits 0-18 ... are
//   used as a pseudo-instruction counter", so bits 19-63 (an index
//   word's sign, flag, count and refill fields, if that is what the
//   program keeps there) must come back unchanged.
// `sa` -- bits 0-18 of psWord: the subject instruction's HALF-WORD
//   location, and the value the step increments.
// `haveW0` / `w0` -- a full-length subject beginning in a right
//   half-word straddles two storage words and needs a second read
//   (the shape EX met first, 1262 TEST 1CC's I62B6).  The first word
//   is kept HERE rather than in `prefetch`, because `prefetch` still
//   holds the pseudo-IC word that the EXIC arm re-reads on every call.
typedef struct {
  WordAddr  psAddr;
  Word64    psWord;
  HWordAddr sa;
  Bool      haveW0;
  Word64    w0;
} ExicCtx deriving (Bits, Eq, FShow);

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

// A half-word store whose target is word 11, the INDICATOR REGISTER.
// st.writeWord(11) is a deliberate no-op: the execute stage writes
// `indicators` exactly once per instruction via setIndicatorBits, and a
// plain register cannot take two independent writes in one rule. So the
// store is FOLDED into `ind`, the Word64 that shared tail writes -- the
// same technique the BB arm already uses for a single bit (see the
// `bw == 11` case), generalised to a half-word.
//
// Reference Card footnote c: only indicator bits 0-19 are read-only.
// The high half (IBM 32-63, BSV 31:0) is therefore unrestricted; the
// low half (IBM 0-31) may write only IBM 20-31, which is BSV 43:32 =
// nh[11:0], so IBM 0-19 = BSV 63:44 is preserved.
//
// WITNESSED BY: ja_ax1a p.25's IBIN35 block, which sets XL by hand with
// SV,$X1,$IND+.32 because no index operation touches XL. Only the HIGH
// half is exercised by that deck; the low-half arm is written to the
// footnote rather than to a listing, and is marked here as such so the
// difference in evidence is visible.
function Bool isIndicatorHW(HWordAddr ha) = (ha[18:1] == addrIndicators);

function Word64 foldIndicatorHW(Word64 ind, HWordAddr ha, Bit#(32) nh) =
  (ha[0] == 1) ? {ind[63:32], nh}                    // IBM 32-63, all writable
               : {ind[63:44], nh[11:0], ind[31:0]};  // IBM 0-19 read-only

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

// IS AN ADDRESS ALARM MASKED FOR INTERRUPTION?  p.32: with the mask
// bit ONE "the operation is terminated and an interruption occurs";
// with it ZERO "the indicator is set, but the operation proceeds".
// IBM bit n is BSV bit 63-n, and the mask's bits 0-19 are permanently
// one (StretchStorage forces them), which is exactly why DS needs no
// mask test anywhere -- it is always masked on.
//
// MOVED ABOVE dfSignal (it used to sit below ifSignal) so the three
// functions that read it -- dfSuppresses here, and IF's mask gate at
// execute()'s commit point -- can all name it, and so the file reads
// generic-helper / DF pair / IF pair.  No change of meaning.
function Bool maskedOn(StretchStorage st, Bit#(6) n) =
  st.readMask()[63 - n] == 1;

// DF, THE DATA-FETCH ADDRESS ALARM (indicator 20).  Same comparand as
// DS: p.32 separates the two by the KIND of reference, not by the
// address, so this shares protViolates rather than restating its
// rules, its 0-31 carve-out, its enable gate or its AD exemption.
//
// p.32: "When an address alarm is caused by a data address used in a
// fetch-type operation, indicator DF is turned on.  If the DF mask bit
// is one, the data fetch is suppressed and the operation terminated.
// If the DF mask bit is zero, the operation proceeds normally.  A
// fetch-type operation is one in which the contents of an addressed
// storage location are read out for use but are not subject to
// change."
//
// WHY THIS READS NO MASK BIT.  The indicator is turned on either way
// -- the mask decides only what happens NEXT -- so setting it is
// mask-independent, and p.52's list of what a suppression must NOT
// exclude names "indicators DF and IF when their mask bits are zero"
// outright.  The mask-dependent half is dfSuppresses below.
//
// WHERE IT IS CALLED, and why not at the single read.  Every operand
// word this file reads leaves through one st.readWordReq in mkEBox,
// and signalling there would be wrong: a read-modify-write STORE (VFL
// ST/M+, SX/SV/SC/SR, SVA, CM, BB's bit change) reads its word through
// that same path, and p.32 puts those on the DS side -- their contents
// ARE "subject to change".  So the call sites below are gated by
// operation, one per instruction format.
function Word64 dfSignal(StretchStorage st, WordAddr a, Word64 ind) =
  protViolates(st, a) ? setBit(ind, ind_DF, 1) : ind;

// DF'S MASK-DEPENDENT HALF: the fetch does not happen and the whole
// operation is SUPPRESSED.  Same comparand as dfSignal, one extra
// term -- the mask bit -- so the two are always asked about the same
// address, which is what keeps "indicator on, operation suppressed"
// from drifting into "indicator on, operation half done".
//
// p.32: "If the DF mask bit is one, the data fetch is suppressed and
// the operation terminated.  If the DF mask bit is zero, the operation
// proceeds normally."  p.45 item 20 says it again, from the indicator
// side and without the loose word: "If the corresponding mask bit was
// one, the fetch did not take place, and THE ENTIRE OPERATION WAS
// SUPPRESSED.  If the mask bit was zero, the operation was completed
// normally."
//
// SUPPRESSED, NOT TERMINATED, and the difference is not pedantry.
// p.32 is the storage-protection chapter using "terminated" loosely;
// the INSTRUCTION SEQUENCING chapter defines the three words, and
// Figure 11 (printed p.43, the Indicator List) gives DF class
// "P,S*,C" with the footnote "*Class S when mask is one; otherwise
// Class C" -- S is suppressed, C is completed.  p.51: "the execution
// of the instruction in progress is either carried through to
// completion or entirely suppressed... When neither is possible,
// however, execution of the instruction is terminated", and p.52-53
// give termination exactly three ways in, none of which is a plain
// masked-on DF.  So mask-zero DF is Class C (what dfSignal alone
// already models) and mask-one DF is Class S.
//
// WHAT SUPPRESSION STILL LEAVES BEHIND, p.52, which reads as an
// exhaustive list: "the suppression of an instruction must necessarily
// exclude the following operations: 1. The actuation of those
// indicators, associated with the instruction, of Class S, and
// indicators DF and IF when their mask bits are zero.  2. The
// actuation of indicators that were caused by conditions unrelated to
// the instruction in execution.  3. The stepping of the instruction
// counter.  4. The changing of the state of the interruption system
// which occurred as specification of BRANCH ENABLED, BRANCH DISABLED,
// or BRANCH ENABLED AND WAIT."
//
// Item 1 is why the call sites below signal DF and THEN suppress,
// never the other way round.  Item 3 is free here: none of the four
// sites touches `next`, so the fall-through address execute() computed
// on entry survives untouched and the instruction counter steps.
// Items 2 and 4 name nothing these four arms do.
//
// AND THE REST IS AN INFERENCE, labelled as such.  The list is framed
// as everything that survives, so by closure the result indicators,
// the progressive-index update and a direct-index load's index-result
// indicators are all suppressed, and that is what the call sites do.
// The manual never says so in those words.  The deck cannot settle it
// either: routine 1260 TEST 8C case 4 re-actuates the indicators with
// a fresh LX before testing them, precisely so its answer does not
// depend on what a suppressed operation left behind.
//
// WHERE THIS IS ASKED: at p.32's CLASS 1 -- "the effective address of
// all fetch-type operations with a direct address", i.e. the same four
// opcode-gated sites dfSignal's own note lists -- AND AT SIX OF THE
// ELEVEN CLASS-3 REFILL SITES.  The split inside class 3 is not a
// convenience, it is two different mechanisms, and it holds:
//
//  * SUPPRESSED HERE: the refills of R, RCZ, CBR, V+CR, V+ICR and
//    V-ICR.  These are NOT progressive indexing.  printed p.32's class
//    3 names "the refill address used in index refill operations and
//    the operations REFILL and REFILL ON COUNT ZERO" as its own
//    category, so printed p.45 item 20's "the fetch did not take
//    place, and the entire operation was suppressed" reaches them
//    directly.  And printed p.52 settles the one part p.45 leaves to
//    inference -- whether a suppressed count-branch-refill still
//    BRANCHES -- by working the case: a protected refill address with
//    the DF mask one on a STORE INSTRUCTION COUNTER IF COUNT, BRANCH
//    AND REFILL leaves "the entire subject instruction... still
//    suppressed but only indicator DF... actuated", "since the test
//    for the refilling is independent of the test for a successful
//    branch."  Quoted in full at the evalBranch site.
//  * NOT SUPPRESSED HERE, and deliberately so: the five
//    PROGRESSIVE-INDEXING refills in the VFL and connective formats.
//    printed p.53 gives them their own rule, and it is the third entry
//    under EXECUTION TERMINATED, not under EXECUTION SUPPRESSED: "An
//    alert of Class S during progressive indexing suppresses only the
//    indexing portion of the operation."  That is a DIFFERENT
//    mechanism from this one -- terminate, not suppress -- it needs a
//    partial-effect path the model does not have, and it is separate
//    work.  A scope decision, not an oversight.
//
// WHAT SUPPRESSION MEANS AT EACH OF THE SIX, since "the entire
// operation" names different state at each: for R, RCZ, CBR, V+CR,
// V+ICR and V-ICR the index register keeps its old value and no index
// result indicators are set; for CBR the branch does not happen
// either, and a SIC prefixed to it therefore stores nothing; for R and
// RCZ on the external-memory path the destination is the storage word
// at the effective address, which is not rewritten.  The DF indicator
// is set at every one of them first -- p.52 item 1 -- and `next` is
// left alone at every one of them, so the instruction counter still
// steps (p.52 item 3).
//
// THE FIFTH CLASS-1 SITE IS THE BitBranch ARM, not a call from here,
// and it is IMPLEMENTED.  p.52 gives BRANCH ON BIT a rule of its own
// in three clauses -- quoted in full at the arm -- because the
// read-only case (instruction bits 60 and 61 both zero) is a FETCH
// while the modifying case is DS's store.  The arm calls dfSignal and
// dfSuppresses exactly as the four sites above do, on the bit word;
// what it adds is p.52's "the instruction is suppressed without a test
// of the addressed bit", which has to sit beside the branch decision
// and so cannot live in a predicate here.  Tested by
// decks/df_bb_readonly.strap.
function Bool dfSuppresses(StretchStorage st, WordAddr a) =
  maskedOn(st, ind_DF) && protViolates(st, a);

// IF, THE INSTRUCTION-FETCH ADDRESS ALARM (indicator 21), and so far
// only p.32's CLASS 2: "Address monitoring for Instruction Fetch
// includes... 2. The branch address of all successful branch
// operations."
//
// p.32: "When an address alarm is caused by the location of the
// instruction which is to be executed next, indicator IF is turned
// on... If the branch address of a successful branch operation is such
// that control would pass into a protected area, the entire branch
// operation, including any counting, bit changing, or index
// alteration, is suppressed.  The address boundaries are ignored if
// the mask bit is zero."
//
// THAT LAST SENTENCE IS AMBIGUOUS AND THE DECK SETTLES IT.  Read
// alone it could mean the indicator does not set at all when the mask
// bit is zero.  It does set: routine 1260 TEST 8C case 3 is titled
// "ENABLE MASK 0 FETCH OK IND ON NO INT" and its error text is
// "-INSTRUCT FETCH BELOW LB FAILS TO SET IF, NO INT, MASK 0,
// ENABLED." -- the deck ERRORS if IF fails to set with the mask at
// zero.  So the sentence attaches to the BRANCH SUPPRESSION just
// before it, not to the indicator, which also matches the general
// rule two paragraphs earlier: "if the mask bit is zero, the
// indicator is set, but the operation proceeds."  The suppression is
// the mask-dependent half and is NOT implemented; see protViolates.
//
// A TARGET BELOW 32 IS AD'S BUSINESS, NOT IF'S.  p.45 on indicator
// AD: "Branching to an address below 32 also actuates the indicator."
// And p.32: an address which actuates AD "cannot actuate any of the
// address alarm indicators."  So the `a >= 32` guard is not an
// optimisation of protViolates' carve-out -- it is a different rule,
// and without it a branch to the permanently protected words 1-3
// would raise IF where the machine raises AD.  NOTE: this model does
// not yet raise AD for a branch below 32 either, so such a branch
// currently raises NEITHER.  Stated here rather than left silent.
function Bool ifViolates(StretchStorage st, WordAddr a) =
  (a >= 32) && protViolates(st, a);

function Word64 ifSignal(StretchStorage st, WordAddr a, Word64 ind) =
  ifViolates(st, a) ? setBit(ind, ind_IF, 1) : ind;

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

// The compare operations set the index FLAG as well as the three
// comparison indicators -- Ref. Manual p.24 for KV and KC ("The
// index-flag and index-comparison indicators are set in each of the last
// two operations; the index result indicators are not set in these
// operations") and p.25 for KVI, KVNI and KCI in the same words.  This
// helper used to set only XL/XE/XH, so all five compares left XF stale.
// NOW PINNED by decks/cmp_sets_index_flag.strap -- it was not
// when the fix landed, and mutation_score.py's cmp-leaves-flag survived
// the whole suite until that program was written.
function Word64 setIndexCmpIndicatorsF(Word64 ind, IndexWord x, Cmp3 c);
  Word64 i0 = setBit(ind, ind_XF, x.flag);
  Word64 i1 = setBit(i0,  ind_XL, pack(c == CmpLow));
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
//
// WIDENED TO 128 BITS, 2026-10-19, because printed p.75's byte
// expansion makes the operands wider than the storage field: a
// 21-bit field at byte size 3 is seven EIGHT-bit bytes, 56 bits of
// accumulator (StretchVFL's connExpand).  The caller masks both
// operands with connExpand's participation mask, so this still needs
// no masking of its own.
function Bit#(128) applyConnective(Bit#(4) conn, Bit#(128) m, Bit#(128) a);
  Bit#(128) notM = ~m;
  Bit#(128) notA = ~a;
  Bit#(128) r = 0;
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
                           flag: x.flag, spare: x.spare, count: x.count, refill: x.refill};
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
      if (protViolates(st, ea)) ind = setBit(ind, ind_DS, 1);
      else st.writeWord(ea, fpToWord(v));
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
      if (protViolates(st, ea)) ind = setBit(ind, ind_DS, 1);
      else st.writeWord(ea, { r.res.ef, r.res.em, r.res.es, r.res.frac,
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
      if (protViolates(st, ea)) ind = setBit(ind, ind_DS, 1);
      else st.writeWord(ea, fpToWord(out));
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
      if (protViolates(st, ea)) ind = setBit(ind, ind_DS, 1);
      else st.writeWord(ea, fpToWord(out));
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
        // COVERAGE LIMIT, RE-MEASURED 2026-09-10 against the full
        // 242-section suite: nothing transcribed requires LC to be
        // OFF after a LEFT shift. Forcing `lc = True` here leaves
        // EVERY section green, so the sh == 0 case below (which
        // leans on BSV's >> 96 being zero) is unguarded.
        //
        // The earlier note said "F212D1, still to transcribe, is an
        // LC row". F212D1 has since been transcribed and it does not
        // close this: its three sub-cases all drive LC ON (ones
        // leaving IBM 12), never off. A12 wants it on too; A24 is
        // the LC-off row but shifts RIGHT, where this branch never
        // runs.
        //
        // NO BLOCK IS KNOWN TO CLOSE IT, and the two candidates
        // this note has named were both wrong. F212D1 was named
        // before it was transcribed and turned out to drive LC ON.
        // The PAU GATES ROUTINE's SHF0 loop was named next, because
        // it does `SHF(U),0` -- a shift of exactly zero, which is
        // the fragile case -- but reading pp.180-181 shows every
        // block of that routine branches only on RZ from its two CT
        // compares. Nothing in it tests LC at all, so it cannot see
        // this.
        //
        // THE RULE THAT COST TWICE: a pointer to a future block must
        // name the BRANCH that would fail, not just the operation
        // that would differ. `SHF(U),0` differs; `BZB,$RZ` does not
        // look at what differs.
        //
        // What would close it is a left shift whose top `sh` bits
        // are zero, followed by a branch on LC being off. F212's
        // LC-off row (A24) shifts RIGHT; F212D1's three sub-cases
        // all drive it on. Left unowned rather than pointed at
        // again.
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
        if (protViolates(st, ea)) ind = setBit(ind, ind_DS, 1);
        else st.writeWord(ea, fpToWord(v));
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
          // jb_af1c F202G11-18 (decks/fp_compare_f202g.strap).
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
//
// A FIFTH MEMBER WAS APPENDED RATHER THAN INSERTED, 2026-10-18: the
// multi-word TRANSMIT's transfer goes LAST so that needsRead stays
// tpl_4 and every existing call site reads unchanged.
typedef Tuple5#(HWordAddr, Maybe#(Tuple2#(Bit#(4), IndexWord)),
                Maybe#(IoXfer), Maybe#(WordAddr),
                Maybe#(XmitXfer)) ExecResult;

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
      // THE DECIMAL BIT DOES NOT MEAN THE SAME THING FOR A RADIX
      // CONVERSION, and this guard used to refuse LCV because of it.
      // Reference Manual printed p.71, "Radix Conversion Operations",
      // under Format: "In this case, **bit 53, the radix modifier,
      // describes the format of the ORIGINAL field** and also
      // determines the type of conversion, binary to decimal or
      // decimal to binary."  p.72 says it again: "If this bit is
      // zero, the original field is binary; if this bit is one, the
      // original field is decimal."
      //
      // So for LCV the bit is not "do decimal arithmetic" -- it is
      // which way to convert, and a decimal-to-binary LOAD CONVERTED
      // is the ONLY thing it can mean.  Refusing it was refusing the
      // operation's normal case.
      //
      // Decimal ARITHMETIC is still unimplemented and still refused;
      // only code 000011, LCV, is let past here.
      Bool radixConv = (vi.code == 6'b000011);
      if (vi.m.decimal == 1 && !radixConv)
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

        // DF, p.32 class 1: "the effective address of all fetch-type
        // operations with a direct address".  L, + (and - , which is
        // + with invert) and K read their field and leave it alone;
        // ST and M+ write it back, so their read belongs to a STORE
        // and signals DS at the write below.  That distinction is why
        // this is gated by opcode instead of sitting at the one
        // readWordReq all of them funnel through.
        //
        // IMMEDIATE ADDRESSING HAS NO STORAGE OPERAND -- p.32 says
        // "with a direct address" -- so it is excluded rather than
        // monitored against the instruction's own address field.
        //
        // BOTH WORDS OF A CROSSING FIELD.  p.31: "an instruction or
        // data field which straddles a boundary always gives an
        // address monitoring signal."  This model compares one word
        // address at a time, so a crossing field asks twice, which is
        // that rule for the two-word case.
        //
        // RUN ON EVERY CALL, including the one that bails out for the
        // operand read: that call's `ind` is discarded (execute()
        // returns entry values when needsRead is Valid), and the
        // resuming call reaches this line again with the same `ea`.
        Bool vflFetchType = (vi.code == 6'b000101)    // L
                         || (vi.code == 6'b000001)    // + , -
                         || (vi.code == 6'b010001);   // K
        Bool dfSupp = False;
        if (vflFetchType && !immediate) begin
          ind = dfSignal(st, baWord(ea), ind);
          dfSupp = dfSuppresses(st, baWord(ea));
          if (fieldCrosses(ea, len_)) begin
            ind = dfSignal(st, baWord(ea) + 1, ind);
            dfSupp = dfSupp || dfSuppresses(st, baWord(ea) + 1);
          end
        end

        // DF'S MASK-DEPENDENT HALF, p.45 item 20: "If the
        // corresponding mask bit was one, the fetch did not take
        // place, and the entire operation was suppressed."  ENTIRE,
        // so the guard goes round the opcode dispatch AND round the
        // shared progressive-index block below it, not just round the
        // read: no readWordReq is issued, no accumulator write, no
        // result indicators, no progressive update and no class-3
        // refill signal, because none of those addresses is then
        // "actually used" (p.32).  `next` is untouched, which is
        // p.52's item 3 -- the instruction counter still steps.
        //
        // WHICH RULE THIS IS, since two of them reach this arm.  The
        // alert here arises on the operand FETCH, so it is p.32 class
        // 1 and Figure 11's Class S -- full suppression.  It is NOT
        // p.53's "an alert of Class S during progressive indexing
        // suppresses only the indexing portion", which is a different
        // (and unimplemented) rule for an alert raised on the REFILL
        // address further down.  A progressive L whose data address is
        // protected loses its indexing too, because the whole
        // operation goes, not because of that sentence.
        if (dfSupp) begin
          // suppressed: deliberately nothing at all
        end else begin
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
                  if (protViolates(st, w0)) ind = setBit(ind, ind_DS, 1);
                  else st.writeWord(w0, insertFieldBits(prefetch[0], off, len_, packedField));
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
                // DF, p.32 class 3.  Reached only when the operation
                // is valid (the outer test rejects immediate and
                // crossing) AND vflNeedsRefill, so the refill
                // genuinely happens -- the gate every other class-3
                // site states explicitly, this one gets from its
                // position.
                ind = dfSignal(st, zeroExtend(vflPx1.refill), ind);
                if (prefetchCount >= 2) begin
                  if (protViolates(st, w0)) ind = setBit(ind, ind_DS, 1);
                  else st.writeWord(w0, insertFieldBits(prefetch[0], off, len_, packedField));
                  vflPending = tagged Valid tuple2(vi.a.i1, unpackIndexWord(prefetch[1]));
                  ind = setIndexResultIndicatorsF(ind, vflPx1); // pre-refill state, p.21
                end else if (prefetchCount == 1)
                  needsRead = tagged Valid zeroExtend(vflPx1.refill);
                else
                  needsRead = tagged Valid w0;
              end
            end
          end
          6'b000001, 6'b100001: begin // + (Add) and +MG (Add to Magnitude)
            // "-" is + with invert=1, and "-MG" is +MG with invert=1.
            // Same prefetch/bail-out shape as L above.
            //
            // ADD TO MAGNITUDE, Reference Manual printed p.60, and
            // like its to-memory twin it is three sentences:
            //
            //   "The addressed operand is algebraically added to the
            //   MAGNITUDE of the contents of the accumulator with
            //   specified offset.  **The accumulator operand is
            //   assumed positive for purposes of the addition
            //   itself.**  If the result is positive, the sum is
            //   placed into the accumulator.  **If the result is
            //   negative, the ENTIRE ACCUMULATOR IS CLEARED TO
            //   ZERO.**  In either case the content of the
            //   accumulator sign byte register is not changed."
            //
            // Modifiers and indicators, printed p.61: "Unsigned;
            // Negative Sign; Radix.  These modifiers operate as in
            // ADD", and "Lost Carry (LC); Partial Field (PF); Data
            // Flags (TF, UF, VF); To-Memory Operation (MOP);
            // Arithmetic Result (RLZ, RZ, RGZ, RN) ... set as in
            // ADD".  So unlike M+MG, the negative sign modifier here
            // belongs to the STORAGE operand -- p.60 under ADD:
            // "This modifier designates whether the sign of the
            // storage operand is taken as-is or is inverted" -- and
            // that is the half of printed p.57's table headed
            // TO-ACCUMULATOR OPERATION.  fieldToSM already applies
            // it, so nothing changes on that side.
            //
            // FIGURE 12 ON p.61 IS THE PROOF, and it is IBM's own
            // worked example rather than my reading of the prose.
            // "Given two 64-bit unsigned binary numbers x and y, put
            // the larger of the two in the accumulator":
            //
            //     L  (BU, 64, 8), X, 0
            //     -MG(BU, 64, 8), Y, 0     note 1
            //     +  (BU, 64, 8), Y, 0     note 2
            //
            //   note 1: result is x-y if x >= y, 0 if x < y
            //   note 2: result is x   if x >= y, y if x < y
            //
            // Note 1 is the whole operation: the accumulator's
            // magnitude |x| plus the inverted storage operand -y,
            // clamped to zero when that goes negative.  The deck
            // decks/plus_mg.strap runs Figure 12 itself.
            //
            // "ENTIRE ACCUMULATOR" MEANS ENTIRE, including the bits
            // below the offset, which is why this clears `mag`
            // outright rather than masking a field.  p.60 says the
            // same thing about ADD two paragraphs earlier: "all
            // add-type operations operate upon the contents of the
            // entire accumulator ... When this occurs, the whole
            // contents of the accumulator may be changed, including
            // the part below the offset."
            Bool magnitude = (vi.code == 6'b100001);
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
              // "assumed positive for purposes of the addition itself"
              SM128 accUsed = magnitude ? SM128 { sign: 0, mag: acc.mag } : acc;
              SM128 sum = smAdd(accUsed, opndSh);
              // "If the result is positive, the sum is placed into
              // the accumulator.  If the result is negative, the
              // entire accumulator is cleared to zero.  In either
              // case the content of the accumulator sign byte
              // register is not changed."  The sign kept is the
              // accumulator's own, both ways -- which also satisfies
              // p.60's closing rule, "on any operation in which the
              // result in the accumulator is all zero, the sign
              // remains as it was before the operation began".
              SM128 stored = magnitude
                ? SM128 { sign: acc.sign,
                          mag: (sum.sign == 0) ? sum.mag : 0 }
                : sum;
              writeAcc(st, stored);
              // "set according to the contents of the ENTIRE
              // accumulator when the operation is complete" (p.60,
              // Arithmetic Result).  setResultIndicatorsF reports RZ
              // for a zero magnitude whatever the sign, so a cleared
              // accumulator with a negative sign byte reads RZ and
              // not RN -- which is what "the sign remains as it was"
              // requires.
              ind = setResultIndicatorsF(ind, stored);
            end
          end
          6'b001001, 6'b101011, 6'b101001: begin // M+, M+1, M+MG
            // (Add One to Memory) -- prefetch/bail-out shape,
            // inlining readFieldWithHi/writeFieldWithHi's own logic
            // rather than calling them: guaranteed non-crossing
            // (checked just above), exactly 1 read.
            //
            // M+1 SHARES THIS ARM BECAUSE IT IS M+ WITH ONE OPERAND
            // REPLACED.  X22-6533 (docs/X22-6533_7030_PocketCard.pdf)
            // gives "M+  Add to Memory  abc001001" and "M+1  Add One
            // to Memory  abc101011" adjacently; the difference is the
            // addend, not the addressing, the field handling, the
            // refill path, the DF class-3 signal or the protection
            // check.  Duplicating fifty lines to change one term
            // would have been the larger risk.
            //
            // "ONE" IS ONE UNIT OF THE FIELD.  fieldToSM returns the
            // field right-justified in `mag` (unsigned: mag = raw;
            // signed: mag = raw >> byteSize, sign byte stripped), so
            // the addend is SM128{sign:0, mag:1} and takes no offset
            // shift -- offSh exists to align the ACCUMULATOR, and M+1
            // has no accumulator operand.
            //
            // ARRIVED VIA MCP.  decks/mcp_bootstrap_p2.strap line
            // 34 is the fourth instruction of IBM's operating system
            // and the model used to set Operation Code Invalid on it
            // (docs/NEXT.md 6a).
            Bool addOne = (vi.code == 6'b101011);
            // ADD MAGNITUDE TO MEMORY, Reference Manual printed p.62,
            // and the whole operation is two sentences there:
            //
            //   "The magnitude of the accumulator field as specified
            //   by the offset is algebraically added to the addressed
            //   operand.  **A positive sign is assumed for the
            //   accumulator field** before the negative sign modifier
            //   is applied.  The actual accumulator sign is not used
            //   or changed by the operation.  **If the sum has the
            //   same sign as the sign of the storage operand, it
            //   replaces that operand in storage.  If the sum is of
            //   opposite sign, ZERO BYTES replace the numeric part of
            //   the storage field.**  In either case the sign byte,
            //   if any, of the storage operand is not changed."
            //
            // Figure 13 on the same page, "Sign Condition Results",
            // tabulates it for every combination and the two rules
            // reproduce the whole "Add Magnitude to Memory" block:
            // storage 3- with accumulator 5+ gives 0-, storage 5-
            // with 3+ gives 2-, and every unsigned row is a plain
            // magnitude sum with the storage sign kept.
            //
            // FOR MCP'S OWN USE IT IS SIMPLER THAN THAT.  printed
            // p.5 lines 15 and 17 are "M+MG(BU,48,8)" and
            // "M+MG(BU,8,8)" -- BINARY UNSIGNED -- and p.62 says
            // "unsigned storage fields are considered positive", so
            // both operands are positive, the sum agrees in sign, and
            // the operation is a plain add.  The opposite-sign rule
            // is still implemented because the manual states it and
            // Figure 13 pins it.
            //
            // ARRIVED VIA MCP, like M+1 before it: the ERROR ROUTINE
            // uses these two adds to write the failing address into
            // its console message, and with the operation refused the
            // message printed its own placeholder, "000000.0".
            Bool magnitude = (vi.code == 6'b101001);
            if (immediate || fieldCrosses(ea, len_)) begin
              ind = setOpInvalid(ind);
              vflOk = False;
            end else begin
              WordAddr w0 = baWord(ea);
              Bit#(6) off = baBit(ea);
              SM128 acc = readAcc(st);
              SM128 accSh = addOne
                ? SM128 { sign: 0, mag: 1 }                       // M+1
                : magnitude
                ? SM128 { sign: vi.m.invert, mag: acc.mag >> offSh } // M+MG
                : SM128 { sign: acc.sign ^ vi.m.invert,            // M+
                          mag: acc.mag >> offSh };
              // WHERE THE NEGATIVE SIGN MODIFIER LANDS, and the
              // manual answers it for the whole class rather than
              // for one operation.  Reference Manual printed p.57,
              // "Sign Control": "bit 52 designates whether the sign
              // of the UNREPLACED operand is taken as-is or inverted
              // ...  if the result is placed in the accumulator, bit
              // 52 determines the use of the sign of the operand
              // from storage; IF THE RESULT IS PLACED IN STORAGE,
              // BIT 52 DETERMINES THE USE OF THE ACCUMULATOR SIGN."
              // The table beneath it spells out all four cases under
              // "TO-MEMORY OPERATION": 01 and 11 invert the
              // ACCUMULATOR sign and leave the storage field's
              // alone, while 10 and 11 (bit 51, the unsigned
              // modifier) are what make the storage field unsigned.
              //
              // SO THE STORAGE OPERAND IS READ WITHOUT THE INVERT
              // for every operation in this arm -- M+ as much as
              // M+MG -- and the bit goes on the accumulator instead.
              // p.62 says the same thing again for M+MG alone: "the
              // accumulator sign is considered positive when the
              // negative sign modifier is zero and negative when the
              // modifier is one", on top of the assumed-positive
              // rule, which is why M+MG's arm starts from 0 and M+'s
              // from the real sign.
              //
              // NOTHING IN THE SUITE EXERCISES THIS, and it cannot:
              // the VFL path of strap_asm.py has no spelling for the
              // negative sign modifier at all (C22-6531 Appendix A
              // footnote 4's N suffix is unimplemented, and the
              // written-minus "M-"/"M-MG" forms are recognised only
              // for the floating-point operations).  So the change
              // is inert today and rests entirely on p.57.  It is
              // still worth making: the previous code would have
              // silently subtracted the wrong operand's sign the
              // moment a spelling arrived.  docs/NEXT.md carries the
              // spelling as its own item.
              //
              // M+1'S ADDEND IS LEFT ALONE.  p.57's table is about
              // "the accumulator sign", and M+1's addend is the
              // constant one rather than an accumulator field, so
              // the modifier has nothing to act on there and its
              // arm above still builds sign 0.  Its STORAGE operand
              // does follow the rule below, because that half of the
              // table is about the class -- "if the result is placed
              // in storage" -- and M+1 is a to-memory operation.  If
              // M+1's own definition says otherwise it will want
              // separating; I have not read it.
              Bit#(1) opndInvert = 0;
              if (!vflNeedsRefill) begin
                if (prefetchCount >= 1) begin
                  Bit#(64) raw = extractFieldBits(prefetch[0], 0, off, len_);
                  SM128 opnd = fieldToSM(raw, len_, bsz, vi.m.unsign, opndInvert);
                  SM128 sum = smAdd(opnd, accSh);
                  SM128 stored = magToMemory(magnitude, sum, opnd);
                  if (protViolates(st, w0)) ind = setBit(ind, ind_DS, 1);
                  else st.writeWord(w0, insertFieldBits(prefetch[0], off, len_,
                                                    smToField(stored, len_, bsz, vi.m.unsign)));
                  // "set according to the FINAL RESULT STORED"
                  // (p.62's Arithmetic Result line), which for M+MG
                  // is not always the sum.
                  ind = setResultIndicatorsF(ind, stored);
                  vflReadsUsed = 1;
                end else
                  needsRead = tagged Valid w0;
              end else begin
                // Same deferred-write shape as ST above.
                vflWriteArmHandled = True;
                // DF, p.32 class 3.  Reached only when the operation
                // is valid (the outer test rejects immediate and
                // crossing) AND vflNeedsRefill, so the refill
                // genuinely happens -- the gate every other class-3
                // site states explicitly, this one gets from its
                // position.
                ind = dfSignal(st, zeroExtend(vflPx1.refill), ind);
                if (prefetchCount >= 2) begin
                  Bit#(64) raw = extractFieldBits(prefetch[0], 0, off, len_);
                  SM128 opnd = fieldToSM(raw, len_, bsz, vi.m.unsign, opndInvert);
                  SM128 sum = smAdd(opnd, accSh);
                  SM128 stored = magToMemory(magnitude, sum, opnd);
                  if (protViolates(st, w0)) ind = setBit(ind, ind_DS, 1);
                  else st.writeWord(w0, insertFieldBits(prefetch[0], off, len_,
                                                    smToField(stored, len_, bsz, vi.m.unsign)));
                  vflPending = tagged Valid tuple2(vi.a.i1, unpackIndexWord(prefetch[1]));
                  ind = setResultIndicatorsF(ind, stored);
                  ind = setIndexResultIndicatorsF(ind, vflPx1); // pre-refill state, p.21
                end else if (prefetchCount == 1)
                  needsRead = tagged Valid zeroExtend(vflPx1.refill);
                else
                  needsRead = tagged Valid w0;
              end
            end
          end
          6'b010001, 6'b110001: begin // K (Compare), KF (Compare Field)
            // -> AL/AE/AH.  Same prefetch/bail-out shape as L above.
            //
            // COMPARE FIELD, Reference Manual printed p.65, verbatim:
            //
            //   "A field in the accumulator is algebraically compared
            //   with the addressed operand.  **This accumulator field
            //   is the same length in bytes as the field from storage
            //   exclusive of the sign byte**, and its location is
            //   specified by the offset in the usual manner.  **The
            //   actual accumulator sign is not used by the operation.
            //   A positive sign is assumed for the accumulator
            //   field.**  The sign of the storage field is used as
            //   modified by the sign modifiers.  The comparison
            //   result indicators are set to describe the accumulator
            //   field as compared with the storage field.  Neither
            //   operand is changed by the operation.  The arithmetic
            //   result indicators are not affected."
            //
            // AND THE PROGRAMMING NOTE ON THE SAME PAGE IS THE WHOLE
            // DIFFERENCE FROM K: "The field comparison operations are
            // the only arithmetic operations that do not treat the
            // entire accumulator contents as a single quantity.
            // Comparisons are made between fields of equal length in
            // numeric bytes.  For this reason, **no indication is
            // given in these operations if there is a one-bit in the
            // accumulator to the left of the field** which is being
            // compared with the storage operand."
            //
            // So K takes everything left of the offset with its real
            // sign; KF takes a bounded field with a forced positive
            // sign and ignores whatever is above it.
            //
            // ARRIVED VIA MCP, printed p.17 line 30: "KF(BU,48),
            // X IOCD" -- the compare that decides whether a card
            // image IS an IOCD card, and so the first of the two
            // operations standing between MCP and knowing what
            // devices it has (docs/boot_plan.md A2).
            Bool fieldCmp = (vi.code == 6'b110001);
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
              SM128 acc = readAcc(st);
              Cmp3 c = CmpEqual;
              if (fieldCmp) begin
                // "the same length in bytes as the field from storage
                // EXCLUSIVE OF THE SIGN BYTE" -- and fieldToSM has
                // already stripped that byte off `opnd.mag`, so the
                // two numeric parts are the same width by
                // construction.  A length at or below the sign byte
                // leaves no numeric part at all; comparing zero
                // against zero is what that degenerates to and the
                // guard keeps the subtraction from wrapping.
                Bit#(7) numBits = (vi.m.unsign == 1) ? len_
                                : ((len_ > zeroExtend(bsz)) ? (len_ - zeroExtend(bsz)) : 0);
                // numBits is at most `len_`, and effLength caps that
                // at 64, so a 128-bit mask never saturates and needs
                // no guard.
                Bit#(128) nmask = (128'b1 << numBits) - 1;
                // "A positive sign is assumed for the accumulator
                // field", and the mask is what implements "no
                // indication is given ... if there is a one-bit in
                // the accumulator to the left of the field".
                SM128 accF = SM128 { sign: 0, mag: (acc.mag >> offSh) & nmask };
                c = smCompare(accF, opnd);
              end else begin
                // COMPARE, p.65: "The contents of the accumulator
                // **LEFT OF THE SPECIFIED OFFSET** are algebraically
                // compared with the addressed operand.  **The bits to
                // the right of the offset do not participate in the
                // comparison.**"
                //
                // This arm used to shift the OPERAND left by the
                // offset and compare it against the whole
                // accumulator.  That gives the same answer whenever
                // the accumulator's low `offset` bits are zero, and a
                // different one when they are not: those bits then
                // break a tie the page excludes them from.  Measured,
                // accumulator 0x101 against an eight-bit 1 at offset
                // 8 -- the manual says equal, the old code said the
                // accumulator was high.
                //
                // NOTHING IN THE SUITE CAUGHT IT and nothing could:
                // at offset 0, or whenever the high parts already
                // differ, the two readings agree, and that covers
                // every K in several hundred listing-verified
                // sections.  decks/compare_offset.strap was written
                // to FAIL first and did.
                //
                // The same page's other clause needs no code: "if
                // the field length and offset are such that
                // high-order positions of the storage field compare
                // with positions to the left of the left end of the
                // accumulator, the accumulator field is extended by
                // adding zeros to its left" -- which a 128-bit
                // magnitude does for free.
                SM128 accSh = SM128 { sign: acc.sign, mag: acc.mag >> offSh };
                c = smCompare(accSh, opnd);
              end
              ind = setAccCmpIndicatorsF(ind, c);
            end
          end
          6'b000011: begin // LCV (Load Converted)
            // Reference Manual printed pp.71-73.  Same
            // prefetch/bail-out shape as L above; the storage
            // operand "is defined by the effective address, field
            // length, and byte size in the same manner as in integer
            // arithmetic" (p.72, Field Definition), immediate
            // addressing included.
            //
            // ARRIVED VIA MCP, printed p.17 line 34:
            // "LCV(DU,8,4),$LZC+.3,46  -CONVERT TO OCTAL NUMBER" --
            // the radix conversion that turns an IOCD card's
            // Hollerith channel digits into a channel number, and
            // the LAST of the two operations standing between MCP
            // and knowing what devices it has (docs/boot_plan.md
            // A2).  Eight bits at byte size four is two decimal
            // digits.
            //
            // ONLY DECIMAL-TO-BINARY IS BUILT.  p.72: "If this bit
            // is zero, the original field is binary" -- which asks
            // for the other direction, repeated division by ten, and
            // nothing in the corpus calls for it.  The binary source
            // sets OP below rather than being silently wrong.
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
              if (vi.m.decimal == 0) begin
                // Binary to decimal: see the scope note above.
                ind = setOpInvalid(ind);
                vflOk = False;
              end else begin
                // A signed decimal field's sign byte is its RIGHTMOST
                // byte and is inside `len_` (p.56), so shift it off
                // and convert what remains.
                Bit#(7) sbBits  = zeroExtend(bsz);
                Bool    signed_ = (vi.m.unsign == 0);
                Bit#(7) numBits = !signed_ ? len_
                                : ((len_ > sbBits) ? (len_ - sbBits) : 0);
                Bit#(64) digitsRaw = !signed_ ? raw : (raw >> bsz);
                // "The sign bit in the sign byte register is set
                // according to the sign of the data as affected by
                // the sign modifiers" (p.72).  Unsigned fields are
                // positive before the negative modifier is applied,
                // as in ADD (p.60).
                Bit#(1) rawSign = !signed_ ? 0 : raw[bsz - 1];
                Bit#(1) sgn     = rawSign ^ vi.m.invert;
                match {.cvVal, .cvDigits} = bcdToBinary(digitsRaw, numBits, bsz);
                // "The accumulator is cleared and the converted field
                // is placed into it at the specified offset."
                SM128 conv = SM128 { sign: sgn, mag: cvVal << offSh };
                writeAcc(st, conv);
                // p.73: PF "is also actuated if the storage field
                // exceeds 15 decimal digits ... Meaningless results
                // are then obtained."
                if (cvDigits > 15) ind = setBit(ind, ind_PF, 1);
                // "To-Memory Operation (MOP) ... set as in ADD", and
                // ADD turns it off (p.60).
                ind = setBit(ind, ind_MOP, 0);
                ind = setResultIndicatorsF(ind, conv);
              end
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
          end else begin
            // DF, p.32 class 3.  INSIDE this else, not beside the
            // test above it: that arm suppresses the whole operation
            // (a crossing-field read plus a refill would need a third
            // prefetch slot), so no refill read happens there, and
            // p.32 monitors addresses "actually used".  Gated on
            // vflNeedsRefill because this block runs for EVERY
            // progressive VFL operation, refill or not.
            if (vflNeedsRefill) ind = dfSignal(st, zeroExtend(vflPx1.refill), ind);
            if (vflNeedsRefill && prefetchCount < vflReadsUsed + 1) begin
              needsRead = tagged Valid zeroExtend(vflPx1.refill);
            end else begin
              Bit#(1) slot = truncate(vflReadsUsed);
              IndexWord px2 = vflNeedsRefill ? unpackIndexWord(prefetch[slot]) : vflPx1;
              vflPending = tagged Valid tuple2(vi.a.i1, px2);
              ind = setIndexResultIndicatorsF(ind, vflPx1); // pre-refill state, p.21
            end
          end
        end
        end  // DF suppression (mask 1): the whole arm, dispatch and
             // progressive-index block alike, is skipped.  Written as
             // a bare `end` rather than by re-indenting 350 lines --
             // the same shape the floating-point arm's `end // AD
             // guard` already uses below.
      end
    return VflOutcome{needsRead: needsRead, vflPending: vflPending, ind: ind};
  endactionvalue
endfunction

// ---------------------------------------------------------------------
// CONNECTIVES (the sixteen boolean functions), lifted whole out of
// execute().
//
// ITS BOUNDARY IS EXACTLY vflIntOp'S, which is why it returns the same
// VflOutcome rather than a type of its own: over 155 lines it touches
// needsRead, vflPending and ind and nothing else of execute()'s
// locals -- no doIdxWrite, no idxWriteVal, no ioStart, no io., no
// next, no fallthrough, no pc, no len -- and of storage only readIndex
// and writeWord.  The two VFL-format arms ask the caller for the same
// three things because they share the format, and the shared type says
// so.
//
// needsRead is threaded rather than returned for the same reason it is
// in vflIntOp: the trailing progressive-index block reads it.
// ---------------------------------------------------------------------
function ActionValue#(VflOutcome)
    connectiveOp(StretchStorage st, ConnInstr cn,
                 Vector#(2, Word64) prefetch, Bit#(2) prefetchCount, Word64 ind0);
  actionvalue
    Maybe#(WordAddr) needsRead = tagged Invalid;
    Maybe#(Tuple2#(Bit#(4), IndexWord)) vflPending = tagged Invalid;
    Word64 ind = ind0;

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
        // THE BYTE SIZE, WHICH THIS ARM USED TO IGNORE ENTIRELY.
        // Reference Manual printed p.75 makes it the whole shape of a
        // connective: a storage byte narrower than eight bits is
        // zero-extended to eight before the connective is applied,
        // and the accumulator operand is "composed of as many bytes
        // as there are in the addressed storage field" -- eight bits
        // each.  See StretchVFL's connExpand for the quotations and
        // for why byte size eight comes out bit-identical to the flat
        // field this arm used before.
        Bit#(4) bsEff = effByteSize(cn.a.bs);
        IndexWord xIdx = st.readIndex(cn.a.i1);
        BitAddr ea = isProgressive ? xIdx.addr : effAddr24(st, cn.a.addr, cn.a.i1);
        // THE OFFSET IS TAKEN LITERALLY, IN BITS, and that is a
        // SETTLED QUESTION with a refutation behind it -- do not
        // "fix" it by rounding to a byte boundary.
        //
        // The rounding is tempting and three strands seemed to
        // support it.  p.75's own sentence admits it ("Any offset may
        // be specified and the field is processed in eight-bit bytes
        // STARTING WITH THE OFFSET"); p.57 states the exact
        // structural analogue for decimal, as a property of the
        // machine rather than of the programmer ("the offset is
        // limited to these digit positions and hence to a multiple of
        // four by ignoring the two low-order bits of the offset");
        // and MCP's own error routine only prints a correct address
        // under it -- printed p.5 line 12's "LF(BU,21,3),X ERR AD,1"
        // carries offset ONE while lines 15 and 17 consume the result
        // at offsets 8 and 0, which want the seven result bytes
        // byte-aligned.  Measured on the bootstrap: literal, the
        // console's seven digit slots receive 0, 0, 0, 12, 12, 4, 8,
        // every digit exactly doubled; rounded, they receive
        // 0, 0, 0, 6, 6, 2, 4, the address.
        //
        // **IT WAS BUILT THAT WAY AND THE FULL SUITE KILLED IT: 56
        // SECTIONS, ALL OF jb_af1c AND THE PAU GATES.**  The
        // floating-point diagnostic checks every result with
        // "CT0110(BU,60),ROS,4" -- a connective at OFFSET 4 -- and
        // the comparison only works if those four bits are honoured.
        // IBM's own diagnostic is a far stronger oracle than a
        // three-strand inference, and it says the offset is bits.
        //
        // So MCP's console address comes out doubled, and that is now
        // an open question about MCP's four-instruction sequence
        // rather than about this line.  docs/NEXT.md carries it with
        // both measurements.
        Bit#(8) offSh = zeroExtend(cn.a.offset);
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

        // DF, p.32 class 1 -- see vflIntOp's fuller note above.  CT's
        // result "is not placed anywhere" (p.76) and C's goes to the
        // accumulator, so both are fetch-type; CM writes the field
        // back and is not.
        Bool dfSupp = False;
        if (cn.suffix != conn_CM && !immediate) begin
          ind = dfSignal(st, baWord(ea), ind);
          dfSupp = dfSuppresses(st, baWord(ea));
          if (fieldCrosses(ea, len_)) begin
            ind = dfSignal(st, baWord(ea) + 1, ind);
            dfSupp = dfSupp || dfSuppresses(st, baWord(ea) + 1);
          end
        end

        // DF'S MASK-DEPENDENT HALF -- see dfSuppresses, and vflIntOp's
        // identical guard, for the sourcing.  connectiveOp carries its
        // OWN copy of the trailing progressive-index block, so this
        // needs its own guard for exactly the reason the class-3 work
        // needed its own signal here: a check on vflIntOp's says
        // nothing about this one.
        if (dfSupp) begin
          // suppressed: deliberately nothing at all
        end else begin
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
          // DF, p.32 class 3.  This branch is entered only on
          // "CM && vflNeedsRefill", so the refill genuinely happens --
          // the gate the other class-3 sites state explicitly, this
          // one gets from its position, exactly as vflIntOp's two
          // inline shapes do.  CM's own field word gets no DF: it is
          // read and written back, so p.32 puts it on the DS side.
          ind = dfSignal(st, zeroExtend(vflPx1.refill), ind);
          WordAddr w0 = baWord(ea);
          Bit#(6) off = baBit(ea);
          if (prefetchCount >= 2) begin
            Word64 mHiWord = prefetch[0];
            Bit#(64) m = extractFieldBits(prefetch[0], 0, off, len_);
            SM128 acc = readAcc(st);
            // Byte-expanded, p.75 -- same three lines as the main
            // C/CT/CM site below.  CM's result is then contracted
            // back to the storage byte size before it is written and
            // before Result Zero is judged ("In CONNECT TO MEMORY,
            // the counts are made on the result field AFTER it is
            // converted to the byte size of the storage operand").
            match {.mVec, .maskVec, .*} = connExpand(m, len_, bsEff);
            Bit#(128) aVec = (acc.mag >> offSh) & maskVec;
            Bit#(128) rVec = applyConnective(cn.conn, mVec, aVec) & maskVec;
            Bit#(64) result = connContract(rVec, len_, bsEff);
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
            // p.75's byte expansion.  `maskVec` marks exactly which
            // bits take part: every bit of every full byte, and only
            // the in-field bits of a short high-order byte.  At byte
            // size eight it is the low `len_` bits -- the old
            // `fieldMask` -- so nothing here moves for the thirty-odd
            // connective sections already in the suite.
            match {.mVec, .maskVec, .*} = connExpand(m, len_, bsEff);
            Bit#(128) aVec = (acc.mag >> offSh) & maskVec;
            Bit#(128) rVec = applyConnective(cn.conn, mVec, aVec) & maskVec;
            // CONNECT and CONNECT FOR TEST judge the result at byte
            // size eight; CONNECT TO MEMORY judges it after the
            // contraction (p.76, "Counts and Indicators").
            Bit#(64) result = connContract(rVec, len_, bsEff);
            Bool resultZero = (cn.suffix == conn_CM) ? (result == 0) : (rVec == 0);

            case (cn.suffix)
              conn_C: begin // C: result replaces the accumulator
                              // field; the rest of the accumulator is
                              // unchanged (p.76 "In CONNECT... The
                              // remainder of the accumulator remains
                              // unchanged").  The field is now the
                              // EXPANDED one -- seven eight-bit bytes
                              // for MCP's LF(BU,21,3), not 21 bits.
                Bit#(128) fieldMask128 = maskVec << offSh;
                Bit#(128) resultSh = rVec << offSh;
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
          end else begin
            // DF, p.32 class 3 -- the same reshape vflIntOp's
            // identical block carries, and for the same reason: the
            // arm above suppresses the whole operation, so no refill
            // read happens there.
            if (vflNeedsRefill) ind = dfSignal(st, zeroExtend(vflPx1.refill), ind);
            if (vflNeedsRefill && prefetchCount < vflReadsUsed + 1) begin
              needsRead = tagged Valid zeroExtend(vflPx1.refill);
            end else begin
              Bit#(1) slot = truncate(vflReadsUsed);
              IndexWord px2 = vflNeedsRefill ? unpackIndexWord(prefetch[slot]) : vflPx1;
              vflPending = tagged Valid tuple2(cn.a.i1, px2);
              ind = setIndexResultIndicatorsF(ind, vflPx1); // pre-refill state, p.21
            end
          end
        end
        end  // DF suppression (mask 1) -- see vflIntOp's matching end
      end
    return VflOutcome{needsRead: needsRead, vflPending: vflPending, ind: ind};
  endactionvalue
endfunction

// ---------------------------------------------------------------------
// DIRECT INDEX ARITHMETIC (p.22-23), lifted whole out of execute().
//
// A THIRD SHAPE OF BOUNDARY, and worth saying why there are three
// rather than one.  The Fp classes return only indicators.  The two
// VFL-format arms return indicators, a read request, and a deferred
// index write of their own kind (vflPending).  This one returns
// indicators, a read request, and the SHARED deferred index write --
// doIdxWrite, idxWriteReg, idxWriteVal -- which is a different channel
// from vflPending and exists for the reason the caller's own comment
// gives: bsc will not take two st.writeIndex call sites in one
// execute() invocation, so VflInt's progressive update needed a
// channel of its own and everything else shares this one.
//
// Measured before cutting: over 138 lines this arm never mentions
// vflPending, ioStart, io., next, fallthrough, pc or len, and of
// storage uses only readIndex and writeHWWithWord.
// ---------------------------------------------------------------------
typedef struct {
  Maybe#(WordAddr) needsRead;
  Bool             doIdxWrite;
  Bit#(4)          idxWriteReg;
  IndexWord        idxWriteVal;
  Word64           ind;
} IndexOutcome;

function ActionValue#(IndexOutcome)
    dirIndexOp(StretchStorage st, DixInstr di_,
               Vector#(2, Word64) prefetch, Bit#(2) prefetchCount, Word64 ind0);
  actionvalue
    Maybe#(WordAddr) needsRead = tagged Invalid;
    Bool doIdxWrite = False;
    Bit#(4) idxWriteReg = 0;
    IndexWord idxWriteVal = IndexWord{addr:0, sign:0, flag:0, spare:0, count:0, refill:0};
    Word64 ind = ind0;

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
      // DF, p.32 class 1 -- see vflIntOp's fuller note above.  The
      // loads and the compares read a half-word and leave it alone;
      // SX/SV/SC/SR and SVA write it back, so their read belongs to a
      // store and signals DS at the write.  A half-word never crosses
      // a word boundary, so one address is the whole question here.
      // (LVE, p.32's class 2, now has an arm of its own below.  Its
      // per-level DF monitoring is still not modelled: the arm reads
      // ONE half-word, because it implements one level of indirection
      // and refuses a chain outright.)
      Bool dixFetchType = (di_.code == dixop_LX) || (di_.code == dixop_LV)
                       || (di_.code == dixop_LC) || (di_.code == dixop_LR)
                       || (di_.code == dixop_KV) || (di_.code == dixop_KC)
                       || (di_.code == dixop_V_PLUS)
                       || (di_.code == dixop_V_PLUS_C)
                       || (di_.code == dixop_V_PLUS_CR);
      Bool dfSupp = False;
      if (dixFetchType) begin
        ind = dfSignal(st, ea[18:1], ind);
        dfSupp = dfSuppresses(st, ea[18:1]);
      end

      // DF'S MASK-DEPENDENT HALF -- see dfSuppresses.  This is the arm
      // routine 1260 TEST 8C case 4 actually exercises: its offending
      // fetch is "LV,$X3,I60AD3" with DF's mask bit stored one, and
      // its error text if the value arrives anyway is "-FETCHED ABOVE
      // UB WITH MASK 1 AND SYSTEM ENABLED."  Suppressing the whole
      // case means the index register keeps its old value, no
      // index-result indicators are set, and V+CR's refill (class 3,
      // below) is never reached -- the deck's own probe is the index
      // VALUE, not the indicators, which is why it can ask that.
      if (dfSupp) begin
        // suppressed: deliberately nothing at all
      end else begin
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
          if (protViolates(st, ea[18:1])) ind = setBit(ind, ind_DS, 1);
          else st.writeWord(ea[18:1], packIndexWord(x));
          ind = setIndexResultIndicatorsF(ind, x);
        end
        dixop_LV: begin // LV
          if (prefetchCount >= 1) begin
            Bit#(32) h = (ea[0] == 0) ? prefetch[0][63:32] : prefetch[0][31:0];
            idxWriteReg = di_.j; doIdxWrite = True;
            idxWriteVal = IndexWord{addr:h[31:8], sign:h[7:7], flag:x.flag,
                                            spare:x.spare,
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
            begin
              Bit#(32) nh = {x.addr, x.sign, h[6:0]};
              if (isIndicatorHW(ea)) ind = foldIndicatorHW(ind, ea, nh);
              else if (protViolates(st, ea[18:1])) ind = setBit(ind, ind_DS, 1);
              else writeHWWithWord(st, ea, nh, prefetch[0]);
            end
            ind = setIndexResultIndicatorsF(ind, x);
          end else
            needsRead = tagged Valid ea[18:1];
        end
        dixop_LC: begin // LC
          if (prefetchCount >= 1) begin
            Bit#(32) h = (ea[0] == 0) ? prefetch[0][63:32] : prefetch[0][31:0];
            idxWriteReg = di_.j; doIdxWrite = True;
            idxWriteVal = IndexWord{addr:x.addr, sign:x.sign, flag:x.flag,
                                            spare:x.spare,
                                            count:h[31:14], refill:x.refill};
            ind = setIndexResultIndicatorsF(ind, idxWriteVal);
          end else
            needsRead = tagged Valid ea[18:1];
        end
        dixop_SC: begin // SC -- same shape as SV above.
          if (prefetchCount >= 1) begin
            Bit#(32) h = (ea[0] == 0) ? prefetch[0][63:32] : prefetch[0][31:0];
            begin
              Bit#(32) nh = {x.count, 7'b0, h[6:0]};
              if (isIndicatorHW(ea)) ind = foldIndicatorHW(ind, ea, nh);
              else if (protViolates(st, ea[18:1])) ind = setBit(ind, ind_DS, 1);
              else writeHWWithWord(st, ea, nh, prefetch[0]);
            end
            ind = setIndexResultIndicatorsF(ind, x);
          end else
            needsRead = tagged Valid ea[18:1];
        end
        dixop_LR: begin // LR
          if (prefetchCount >= 1) begin
            Bit#(32) h = (ea[0] == 0) ? prefetch[0][63:32] : prefetch[0][31:0];
            idxWriteReg = di_.j; doIdxWrite = True;
            idxWriteVal = IndexWord{addr:x.addr, sign:x.sign, flag:x.flag,
                                            spare:x.spare,
                                            count:x.count, refill:h[31:14]};
            ind = setIndexResultIndicatorsF(ind, idxWriteVal);
          end else
            needsRead = tagged Valid ea[18:1];
        end
        dixop_SR: begin // SR -- same shape as SV above.
          if (prefetchCount >= 1) begin
            Bit#(32) h = (ea[0] == 0) ? prefetch[0][63:32] : prefetch[0][31:0];
            begin
              Bit#(32) nh = {x.refill, 7'b0, h[6:0]};
              if (isIndicatorHW(ea)) ind = foldIndicatorHW(ind, ea, nh);
              else if (protViolates(st, ea[18:1])) ind = setBit(ind, ind_DS, 1);
              else writeHWWithWord(st, ea, nh, prefetch[0]);
            end
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
                                      spare: x.spare,
                                      count: x.count, refill: x.refill};
            if (di_.code != dixop_V_PLUS) x1.count = x1.count - 1;
            Bool needsRefill = (di_.code == dixop_V_PLUS_CR) && (x1.count == 0);
            // DF, p.32 class 3 -- see evalBranch's note.  This is a
            // SECOND monitored address for the same instruction: the
            // half-word operand was already asked about above, through
            // dixFetchType, and this is the refill source.
            if (needsRefill) ind = dfSignal(st, zeroExtend(x1.refill), ind);
            // DF'S MASK-DEPENDENT HALF for class 3 -- see dfSuppresses,
            // and evalBranch's note for why the test precedes the
            // bail-out.  NESTED INSIDE THE CLASS-1 GATE ABOVE AND ABOUT
            // A DIFFERENT ADDRESS: `dfSupp` already asked about the
            // operand half-word at `ea`, and reaching here means that
            // one did not suppress.  This asks about the refill source,
            // the second monitored address of the same instruction, and
            // when it fires the index register keeps its old value and
            // no index result indicators are set.
            if (needsRefill && dfSuppresses(st, zeroExtend(x1.refill))) begin
              // suppressed: deliberately nothing at all
            end else if (needsRefill && prefetchCount < 2) begin
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
            ind = setIndexCmpIndicatorsF(ind, x, smCompare(val, opnd));
          end else
            needsRead = tagged Valid ea[18:1];
        end
        dixop_KC: begin // KC
          if (prefetchCount >= 1) begin
            Bit#(32) h = (ea[0] == 0) ? prefetch[0][63:32] : prefetch[0][31:0];
            Cmp3 c = (x.count == h[31:14]) ? CmpEqual : (x.count < h[31:14]) ? CmpLow : CmpHigh;
            ind = setIndexCmpIndicatorsF(ind, x, c);
          end else
            needsRead = tagged Valid ea[18:1];
        end
        dixop_LVE: begin // LVE (Load Value Effective) -- INDIRECT
          // ADDRESSING.  Reference Manual printed p.29, read
          // first-hand:
          //
          //   "Even though the instruction class of the final
          //    instruction is determined in order to obtain the
          //    proper effective address, the instruction operation is
          //    not executed. ... The index register in which the
          //    final effective address is to be stored is specified
          //    by the index field J of the original LOAD VALUE
          //    EFFECTIVE instruction.  The fields J of all subsequent
          //    instructions encountered in the operation are
          //    ignored."
          //
          // and printed p.21 for how the address part becomes a
          // 24-bit effective address: "the address part of the
          // instruction, extended with the necessary low-order zeros,
          // is the effective address."
          //
          // MCP's BOOTSTRAP IS WHAT MADE THIS NECESSARY, and it uses
          // exactly one level.  Printed p.3's FIND IPL CHANNEL walks
          // the channels by adding one to the channel field of its
          // own CCW instruction and then does
          //
          //     LVE,15,X1 CCW   - OBTAIN NUMBER OF IPL CHANNEL
          //
          // -- read the CCW it has been modifying, compute THAT
          // instruction's effective address, and keep it.  Every
          // later "0($15)" on pp.3-6 then addresses the channel the
          // IPL came in on.  Measured before this arm existed: the
          // model no-opped the LVE, $15 kept the index word printed
          // p.2's core-sizing loop left in it, SPFL went to channel
          // zero, and the bootstrap stored X ER 05B's address in
          // X ERR AD and printed "UNRJ IN SPACING OVER EOF".
          //
          // THE ADDRESS WIDTH IS NOT GUESSED.  It is the same six-way
          // rule StretchDecode's svaReplaceAddr already applies, from
          // jb_ax3a printed p.140: bits 24-27 = 1000 means a 24-bit
          // bit address; bits 26-27 = 10 means floating point, 18
          // bits, a word address; everything else is 19 bits, a half
          // word address.  Writing it as the three-way test below
          // rather than calling svaReplaceAddr keeps the two in the
          // same shape without pretending one is derived from the
          // other -- SVA replaces a field, this one extracts it.
          if (prefetchCount >= 1) begin
            Bit#(32) h = (ea[0] == 0) ? prefetch[0][63:32] : prefetch[0][31:0];
            Bit#(5) hcode = h[8:4];
            Bool targetIsLve = (instrLen(h) != Full) && (hcode == dixop_LVE);
            if (targetIsLve)
              // A CHAIN IS A LOOP, AND THIS E-BOX CANNOT RUN ONE.
              // p.29 is explicit that LVE "extends the indirect
              // addressing to another level" and "is always
              // executed", terminating after one millisecond with
              // indicator USA if the chain never ends.  That is an
              // iteration with a time bound, and this model executes
              // one instruction per step with no inner loop, so a
              // chained LVE is refused out loud rather than silently
              // truncated to one level.  It needs the multi-cycle
              // E-box docs/microarchitecture_plan.md already calls
              // for; MCP uses one level and no deck in this corpus
              // uses more.
              ind = setOpInvalid(ind);
            else begin
              BitAddr a = (instrLen(h) == Full) ? h[31:8]
                        : (h[5:4] == 2'b10)     ? {h[31:14], 6'b0}
                        :                         {h[31:13], 5'b0};
              BitAddr fea = effAddr24(st, a, h[3:0]);
              idxWriteReg = di_.j; doIdxWrite = True;
              // The VALUE field only, like LV: p.29 says the final
              // effective address "is placed in the index register",
              // and names only the index flag and index result
              // indicators as the other things that change.
              //
              // THE SIGN IS ZERO, AND THAT IS A BOUNDED ASSUMPTION
              // rather than a reading.  p.21 says the effective
              // address "always has 24 numeric bits and a sign", so
              // in principle a signed value belongs here -- but the
              // same page says "the effective address sign is not
              // used in storage addressing", and "a negative
              // effective address is not considered to be invalid;
              // its magnitude is used".  effAddr24 above is written
              // to that rule and returns a 24-bit magnitude with no
              // sign to pass on, so this arm has none to store.  The
              // difference is observable only for an LVE whose
              // computed address is negative; nothing in this corpus
              // does that, and LV beside it takes its sign from the
              // loaded half-word because it is loading a VALUE, not
              // an address.
              idxWriteVal = IndexWord{addr:fea, sign:0, flag:x.flag,
                                              spare:x.spare,
                                              count:x.count, refill:x.refill};
              ind = setIndexResultIndicatorsF(ind, idxWriteVal);
            end
          end else
            needsRead = tagged Valid ea[18:1];
        end
        dixop_SVA: begin // SVA (Store Value in Address), Ref. Manual
          // p.29: "The first 18, 19, or 24 bits of the value field of
          // the index word specified by J replace the address field of
          // the instruction specified by the effective address."
          //
          // THE WIDTH COMES FROM THE TARGET, not from SVA: p.29
          // "Address Insertion" -- "The length of the address field is
          // determined from the instruction operation code". That rule
          // is svaReplaceAddr, beside instrLen in StretchDecode, where
          // its whole story lives: jb_ax3a p.140's six-case length tag,
          // why the test is on BITS rather than on decodeHalfWord, and
          // the 768 half-words the two disagree about. It is a function
          // and not inline here so that StretchSvaWidthSweep can sweep
          // the code the model runs rather than a copy of it.
          //
          // The index register is NOT modified; "the index flag and
          // index result indicators are set according to the contents
          // of the index register specified by J", so this takes the
          // store shape (indicators from the unchanged x), like SV.
          if (prefetchCount >= 1) begin
            Bit#(32) h = (ea[0] == 0) ? prefetch[0][63:32] : prefetch[0][31:0];
            Bit#(32) nh = svaReplaceAddr(h, x.addr);
            if (isIndicatorHW(ea)) ind = foldIndicatorHW(ind, ea, nh);
            else if (protViolates(st, ea[18:1])) ind = setBit(ind, ind_DS, 1);
            else writeHWWithWord(st, ea, nh, prefetch[0]);
            ind = setIndexResultIndicatorsF(ind, x);
          end else
            needsRead = tagged Valid ea[18:1];
        end
        default: ind = setOpInvalid(ind); // RNX, LVE: out of scope
      endcase
      end  // DF suppression (mask 1) -- see vflIntOp's matching end
    return IndexOutcome{needsRead: needsRead, doIdxWrite: doIdxWrite,
                        idxWriteReg: idxWriteReg, idxWriteVal: idxWriteVal,
                        ind: ind};
  endactionvalue
endfunction

// ---------------------------------------------------------------------
// IMMEDIATE INDEX ARITHMETIC, lifted whole out of execute().
//
// ITS BOUNDARY IS IDENTICAL TO dirIndexOp'S, so it returns the same
// IndexOutcome: needsRead, the shared deferred index write, and the
// indicators.  That is the second pair of arms to come out sharing a
// return type, after the two VFL-format ones, and for the same reason
// -- they are two spellings of one instruction format, so they ask the
// caller for the same things.
//
// Count-and-branch is NOT here: CB/CBR/CBZ/CBRZ are their own arm and
// go through evalBranch, which is why nothing in these ninety-four
// lines touches `next` or `fallthrough` even though the immediate
// index forms look as though they might.
// ---------------------------------------------------------------------
function ActionValue#(IndexOutcome)
    immIndexOp(StretchStorage st, ImmInstr ii,
               Vector#(2, Word64) prefetch, Bit#(2) prefetchCount, Word64 ind0);
  actionvalue
    Maybe#(WordAddr) needsRead = tagged Invalid;
    Bool doIdxWrite = False;
    Bit#(4) idxWriteReg = 0;
    IndexWord idxWriteVal = IndexWord{addr:0, sign:0, flag:0, spare:0, count:0, refill:0};
    Word64 ind = ind0;

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
      // bits for counts; caught by tests/verify_ibox1_listing.py,
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
                   flag: x.flag, spare: x.spare, count: x.count, refill: x.refill};
          ind = setIndexResultIndicatorsF(ind, idxWriteVal);
        end
        4'b1001: begin // LVNI
          idxWriteReg = ii.j; doIdxWrite = True;
          idxWriteVal = IndexWord{addr: immVal24, sign: 1,
                   flag: x.flag, spare: x.spare, count: x.count, refill: x.refill};
          ind = setIndexResultIndicatorsF(ind, idxWriteVal);
        end
        4'b0010: begin // LCI
          idxWriteReg = ii.j; doIdxWrite = True;
          idxWriteVal = IndexWord{addr: x.addr, sign: x.sign,
                   flag: x.flag, spare: x.spare, count: imm18, refill: x.refill};
          ind = setIndexResultIndicatorsF(ind, idxWriteVal);
        end
        4'b0011: begin // LRI
          idxWriteReg = ii.j; doIdxWrite = True;
          idxWriteVal = IndexWord{addr: x.addr, sign: x.sign,
                   flag: x.flag, spare: x.spare, count: x.count, refill: imm18};
          ind = setIndexResultIndicatorsF(ind, idxWriteVal);
        end
        4'b0000: begin // C+I
          idxWriteReg = ii.j; doIdxWrite = True;
          idxWriteVal = IndexWord{addr: x.addr, sign: x.sign, flag: x.flag,
                   spare: x.spare,
                   count: x.count + imm18, refill: x.refill};
          ind = setIndexResultIndicatorsF(ind, idxWriteVal);
        end
        4'b1000: begin // C-I
          idxWriteReg = ii.j; doIdxWrite = True;
          idxWriteVal = IndexWord{addr: x.addr, sign: x.sign, flag: x.flag,
                   spare: x.spare,
                   count: x.count - imm18, refill: x.refill};
          // THE IMMEDIATE INDEX OPERATIONS SET THE INDEX FLAG AND
          // RESULT INDICATORS.  Ref. Manual p.25, directly after this
          // operation: "The index flag and index result indicators are
          // set in all of the preceding immediate index arithmetic
          // operations. The index comparison indicators are not
          // changed."  LVI, LVNI, LCI, LRI, C+I and C-I all omitted it.
          //
          // C-I was found first, by the deck: jb_ax4b routine 1238
          // test 3 does C-I then BXCZ back to back, and without this
          // the loop never terminates (a step cap spinning at
          // 005553.40).  The other five were then corrected on the
          // manual's sentence, which names them all; no deck block in
          // the suite yet reads their indicators.
          //
          // WHICH WORD: the manual does not say before or after.  The
          // RESULT is used, as LV/LC/LR do with their new word, and
          // the p.25 programming note supports it -- "to set the index
          // flag and index result indicators according to the status
          // of an index without modifying that index", use V+I with a
          // zero address, which only makes sense if the indicators
          // report the index as it stands after the operation.
          ind = setIndexResultIndicatorsF(ind, idxWriteVal);
        end
        4'b0101, 4'b0110, 4'b0111: begin // V+I / V+IC / V+ICR --
          // prefetch/bail-out shape, inlining maybeRefill's own
          // condition (doRefill && x1.count==0) rather than calling
          // it, since only the ICR variant can ever need the read.
          SM128 sum = smAdd(val, immSM);
          IndexWord x1 = IndexWord{addr: truncate(sum.mag), sign: sum.sign,
                           flag: x.flag, spare: x.spare, count: x.count, refill: x.refill};
          if (ii.code != 4'b0101) x1.count = x1.count - 1;
          if (ii.code == 4'b0111 && x1.count == 0) begin
            // DF, p.32 class 3 -- see evalBranch's note.  The
            // immediate index operations read NO operand, so unlike
            // V+CR above this refill address is the only storage
            // address the instruction uses at all.
            ind = dfSignal(st, zeroExtend(x1.refill), ind);
            // DF'S MASK-DEPENDENT HALF -- see dfSuppresses, and
            // evalBranch's note for why the test precedes the bail-out.
            // There is no class-1 gate above this one to nest inside,
            // for the same reason the signal's own note gives: the
            // refill source is the ONLY storage address V+ICR uses.
            if (dfSuppresses(st, zeroExtend(x1.refill))) begin
              // suppressed: deliberately nothing at all
            end else if (prefetchCount >= 1) begin
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
                           flag: x.flag, spare: x.spare, count: x.count, refill: x.refill};
          if (ii.code != 4'b1101) x1.count = x1.count - 1;
          if (ii.code == 4'b1111 && x1.count == 0) begin
            // DF, p.32 class 3 -- same as V+ICR above.
            ind = dfSignal(st, zeroExtend(x1.refill), ind);
            // DF's mask-dependent half -- same as V+ICR above.
            if (dfSuppresses(st, zeroExtend(x1.refill))) begin
              // suppressed: deliberately nothing at all
            end else if (prefetchCount >= 1) begin
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
        4'b0100: ind = setIndexCmpIndicatorsF(ind, x, smCompare(val, immSM)); // KVI
        4'b1100: ind = setIndexCmpIndicatorsF(ind, x, smCompare(val, SM128{sign:~immSM.sign, mag:immSM.mag})); // KVNI
        4'b1010: begin // KCI
          Cmp3 c = (x.count==imm18) ? CmpEqual : (x.count<imm18) ? CmpLow : CmpHigh;
          ind = setIndexCmpIndicatorsF(ind, x, c);
        end
        4'b1011: begin // LVS -- LOAD VALUE WITH SUM
          // MULTIPLE INDEXING, Reference Manual printed p.28, and the
          // whole operation is on that one page.  THE ADDRESS FIELD
          // IS NOT AN ADDRESS:
          //
          //   "In multiple indexing, bits 0-15 of the address part of
          //   the instruction are used to indicate which index
          //   registers participate in the operation.  When bit
          //   position n contains a one, the register Xn
          //   participates."
          //
          //   "The address parts, bits 0-24, of the index registers
          //   which participate are added and replace bits 0-24 of
          //   the index word specified by J.  The addition is
          //   algebraic, taking into account the sign, bit 24, of all
          //   quantities.  **Bits 25-63 of the index word specified
          //   by J remain unchanged.**"
          //
          //   "The index flag and index result indicators are set
          //   according to the new contents of the index register
          //   specified by J."
          //
          // BIT ORDER.  IBM bit n of a 19-bit field has weight
          // 2^(18-n), so Xn's mask bit is ii.imm[18-n] -- the same
          // rule strap_asm.py's LVS encoder uses in the other
          // direction, and tests/verify_lvs_encoding.py is what says
          // that reproduces MCP's two printed instances.
          //
          // WHICH BITS ARE IGNORED, and the page disagrees with
          // itself.  The prose says "Bits 16-19 ... are ignored";
          // bit 19 is the high bit of J in the SAME page's format
          // diagram and in X22-6533's IMMEDIATE INDEX ARITHMETIC row.
          // Figure and pocket card agree against the sentence, so the
          // mask is bits 0-15 and 16-18 are ignored.  Reading only
          // n < 16 below implements exactly that, and the assembler
          // records the same discrepancy at its own LVS arm.
          //
          // "NO ADDRESS MODIFICATION IS AVAILABLE FOR THIS
          // OPERATION" (same page), which is why nothing here indexes
          // the instruction: there is no I field to apply.
          //
          // THE EMPTY MASK FALLS OUT RATHER THAN BEING SPECIAL-CASED.
          // "If bits 0-15 of the address part of the instruction are
          // all zero, the value field of the index register specified
          // by J is cleared" -- and an empty sum is +0, which is what
          // the accumulator starts at.
          SM128 lvsAcc = SM128{sign: 0, mag: 0};
          for (Integer n = 0; n < 16; n = n + 1)
            if (ii.imm[18 - n] == 1) begin
              IndexWord xn = st.readIndex(fromInteger(n));
              lvsAcc = smAdd(lvsAcc,
                             SM128{sign: xn.sign, mag: zeroExtend(xn.addr)});
            end
          idxWriteReg = ii.j; doIdxWrite = True;
          idxWriteVal = IndexWord{addr: truncate(lvsAcc.mag),
                                  sign: lvsAcc.sign,
                                  flag: x.flag, spare: x.spare,
                                  count: x.count, refill: x.refill};
          ind = setIndexResultIndicatorsF(ind, idxWriteVal);
        end
        default: ind = setOpInvalid(ind); // no immediate-index code
                                           // is left unimplemented;
                                           // the arm is exhaustive and
                                           // this catches a decode bug
      endcase
    return IndexOutcome{needsRead: needsRead, doIdxWrite: doIdxWrite,
                        idxWriteReg: idxWriteReg, idxWriteVal: idxWriteVal,
                        ind: ind};
  endactionvalue
endfunction

// ---------------------------------------------------------------------
// INPUT/OUTPUT operations, lifted whole out of execute().
//
// THE ONLY ARM THAT REACHES THE I/O INTERFACE, so the only extracted
// function that takes a StretchIO as well as a StretchStorage -- and
// that is the whole of what makes its boundary a fourth shape.  What
// it returns is needsRead, ioStart and the indicators: a started
// transfer is threaded out rather than performed inline because a
// block can be many words and this function, like every other arm, may
// call st.writeWord (or io.writePrinterWord) only once per invocation.
//
// Measured before cutting: over 151 lines it never mentions
// doIdxWrite, idxWriteVal, vflPending, next, fallthrough or pc; the
// single `len` hit is inside a comment.
// ---------------------------------------------------------------------
typedef struct {
  Maybe#(WordAddr) needsRead;
  Maybe#(IoXfer)   ioStart;
  Word64           ind;
} IoOutcome;

function ActionValue#(IoOutcome)
    ioOpExec(StretchStorage st, StretchIO io, IoInstr io_,
             Vector#(2, Word64) prefetch, Bit#(2) prefetchCount, Word64 ind0);
  actionvalue
    Maybe#(WordAddr) needsRead = tagged Invalid;
    Maybe#(IoXfer) ioStart = tagged Invalid;
    Word64 ind = ind0;

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
      Bool diskCh    = (kind == DevDisk);
      Bool consoleCh = (kind == DevConsole);
      // "AN INSTRUCTION IS RECEIVED THAT THE SELECTED UNIT IS NOT
      // DESIGNED TO PERFORM" -- Reference Manual printed p.113's own
      // words for Exchange Program Check, and the shape every arm
      // below uses for a control function the addressed unit does not
      // have.  EPGK IS NOT OP: Operation Code Invalid is about the
      // instruction's OPCODE, and a CONTROL whose FUNCTION code the
      // unit does not implement has a perfectly valid opcode.  This
      // model used to conflate them, which mattered the moment MCP's
      // ERROR ROUTINE started running: printed p.5 line 28 issues
      // "CTL(SEOP),0.0($X1),0.0  -ILLEGAL IO CONTROL CODE"
      // DELIBERATELY, to find out which channels answer at all, and
      // then tests CBJ and UNRJ.  A machine that answers OP tells it
      // nothing.
      function Action programCheck();
        action
          ControlWord cw = io.readChanCW(chAddr);
          cw.epgk = 1;
          if (!seop) cw.eop = 1;
          io.writeChanCW(chAddr, cw);
        endaction
      endfunction
      function Action acceptControl();
        action
          ControlWord cw = io.readChanCW(chAddr);
          if (!seop) cw.eop = 1;
          io.writeChanCW(chAddr, cw);
        endaction
      endfunction

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
          3'b010: begin // CTL (Control)
            if (consoleCh) begin
              // THE OPERATOR'S CONSOLE HAS FOUR CONTROL FUNCTIONS and
              // Reference Manual printed p.150 lists all of them:
              //   016  Reserved Light Off
              //   017  Reserved Light On
              //   116  Check Light On
              //   177  "Sound Gong.  This function causes a clearly
              //        audible gong to sound a single stroke."
              // None of the four has an observable effect in a model
              // with no lights and no gong, so all four are ACCEPTED
              // and nothing else happens.  THE ACCEPTANCE IS THE
              // POINT: MCP's ERROR ROUTINE identifies the console by
              // issuing GONG and checking that EPGK did NOT come on
              // (printed p.5 lines 45-51, "IF CONSOLE * NO EPGK"), so
              // "this unit performs 177" IS the console's signature.
              //
              // 177 ON A 729 IV IS BACKSPACE FILE -- same octal,
              // different device -- which is what a per-device
              // control table means and why this arm dispatches on
              // the unit before the code.
              case (effA2)
                18'o16, 18'o17, 18'o116, 18'o177: acceptControl();
                default: programCheck();
              endcase
            end else if (!tapeCh) begin
              // An installed unit with no control function this model
              // knows.  p.113's EPGK, not OP -- see programCheck.
              programCheck();
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
                18'o77: begin // SPACE FILE (p.132): "forward past a
                  // tape mark; EE and EOP given".
                  //
                  // THIS IS A TRANSFER, NOT A JUMP, and that is the
                  // substantive difference from REWIND and BACKSPACE
                  // BLOCK above.  Those two know where to go and set
                  // the position outright.  SPACE FILE has to LOOK --
                  // a real 729 moves the tape until it reads a mark,
                  // and a file- or SD-backed source cannot be searched
                  // combinationally anyway.  So it starts the same
                  // IoXfer machinery RD and W use, with untilMark set,
                  // and StretchCore's rl_io walks the tape one word per
                  // cycle exactly as a READ does.
                  //
                  // THE CONTROL WORD IS THE CHANNEL'S OWN.  Unlike
                  // RD/W, CONTROL's right effective address is a
                  // function code and not a control-word address
                  // (p.111), so there is nothing to fetch: the
                  // in-flight status goes in the control word already
                  // in the exchange.  SEOP is set at issue for the
                  // same reason RD/W set it -- MCP's printed p.3 line
                  // 45 spins on bit 24 until the operation completes.
                  ControlWord cw = io.readChanCW(chAddr);
                  cw.seop = 1;
                  io.writeChanCW(chAddr, cw);
                  ioStart = tagged Valid IoXfer {
                    ch: chAddr, isWrite: False,
                    memAddr: 0,              // nothing is stored
                    devIdx: io.tapePos(),
                    // No count bounds a SPACE FILE; the mark does, or
                    // the end of the reel does (the capacity arm in
                    // rl_io, which also gives End Exception).
                    remaining: 19'h40000,
                    suppressEop: seop, skip: False, untilMark: True,
                    zeroFill: False };
                end
                default: programCheck();          // SPACE BLOCK,
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
          3'b011: begin // LOC (Locate)
            if (!diskCh) begin
              // ON THE EXCHANGE, LOCATE IS SELECT UNIT -- C22-6531
              // Appendix A printed p.57 lists them as one operation,
              // "E LOC Locate (same as Select Unit)".
              //
              // IT SELECTS ONE UNIT OF A CONTROL THAT HAS SEVERAL,
              // and in this model only the tape has several (the 7613
              // carries up to eight 729 IVs, one active at a time).
              // So a tape channel ACCEPTS it and every other unit
              // program-checks, which is precisely the test MCP's
              // ERROR ROUTINE makes: printed p.5 line 36 is
              // "LOC(SEOP),0.0($X1),0.0  -TEST IF TAPE CHANNEL" and
              // line 42 branches on EPGK being clear with the comment
              // "-TEST IF TAPE UNIT".  **The absence of a program
              // check is how MCP recognises a tape.**
              //
              // WHICH unit gets selected is not modelled, because
              // this model has one unit per channel; the right
              // effective address is ignored here rather than
              // decoded.  Named as a gap in bsv/README.md.
              if (tapeCh) acceptControl();
              else programCheck();
            end else begin
              // ON A DISK, LOCATE IS A SEEK, and it is the whole of
              // disk addressing.  Reference Manual printed p.160:
              // "The right effective address, bit positions 32
              // through 49, of the instruction specifies the arc
              // address.  Positions 32-37 must be 0 bits while
              // positions 38-49 specify the arc address."
              //
              // effA2 is the 18-bit word address formed from EA bits
              // 32-49, so bits 38-49 -- the arc -- are its low twelve
              // and bits 32-37 are its high six.
              //
              // "MUST BE 0" IS NOT ENFORCED, and that is a documented
              // non-enforcement rather than an oversight.  The manual
              // states the requirement and NOWHERE states the
              // consequence of violating it; inventing an indicator
              // here would be putting words in its mouth.  This is the
              // same stance the arm above takes on Address Invalid for
              // an out-of-range control-word address.
              io.setArcAddr(truncate(effA2));
              // "the operation is completed" -> EOP, unless SEOP.
              // printed p.160 gives LOCATE the ordinary EOP/SEOP
              // treatment (§3.7 of docs/disk_subsystem.md).
              ControlWord cw = io.readChanCW(chAddr);
              if (!seop) cw.eop = 1;
              io.writeChanCW(chAddr, cw);
            end
          end
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
            if (protViolates(st, effA2)) ind = setBit(ind, ind_DS, 1);
            else st.writeWord(effA2, packControlWord(io.readChanCW(chAddr)));
          3'b000, 3'b001: begin // RD, W
            // THE CONSOLE IS WRITE-ONLY HERE, AND THAT IS A KNOWN
            // DEVIATION rather than a modelling choice.  Reference
            // Manual printed p.150: "A READ instruction received by
            // the console with the keyboard not enabled is
            // automatically terminated when the three words scanned
            // from the switches have been sent to the exchange" --
            // the console switches are three words and a READ returns
            // them, which is how MCP's IPL takes the time and date
            // the operator sets in binary keys 0-23 and 32-55
            // (C22-6678-1 printed p.29).  Nothing on the path that
            // runs today reads them, so the three-word switch image
            // is not built and a READ here program-checks instead.
            // When the IPL needs the switches this is the line to
            // change, and the capacity in StretchCore's rl_io is 3.
            Bool wrongUnit = (base == 3'b000)
              ? (!readerCh && !tapeCh && !diskCh)   // RD: reader, tape, disk
              : (!printerCh && !tapeCh && !diskCh
                 && !consoleCh);                    // W: + the console
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
              // p.121: "At the time an SEOP instruction is given, the
              // SEOP bit in the control word is set to one.  As the
              // result of this, the EOP bit in the control word (and
              // therefore in the indicator register) is not turned on
              // unless it is accompanied by unit check or end
              // exception."  The suppression itself was already
              // modelled through IoXfer.suppressEop; this makes the
              // BIT observable, which is what every real driver polls.
              // StretchCore's transfer FSM clears it on completion --
              // see docs/NEXT.md 5o for why that half is sourced the
              // way it is.
              cw0.seop = seop ? 1 : 0;
              // THE DISK DISCARDS THREE QUARTERS OF THE CONTROL WORD,
              // and it has to be done HERE, before the exchange adopts
              // it, because rl_io reads chain and skip back out of the
              // adopted word.  Reference Manual printed p.158: "No use
              // is made of control word flag bits or refill field and
              // they are discarded after checking the control word
              // error correction and check bits.  Only the data word
              // address field and word count field of the control word
              // are retained and used by the disk synchronizer."
              //
              // Zeroing them rather than ignoring them makes the
              // discard OBSERVABLE: a COPY CONTROL WORD after a disk
              // transfer shows what the synchronizer actually kept,
              // which is what printed p.161 says it returns ("the data
              // word address and word count fields... placed in a
              // full-word format").
              if (diskCh) begin
                cw0.chain = 0; cw0.multiple = 0; cw0.skip = 0;
                cw0.refill = 0;
              end
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
                // THE TAPE AND THE READER BOTH CONTINUE; THE
                // PRINTER RESTARTS.  A tape's head stays where the
                // last operation left it (StretchIO.bsv "TAPE
                // POSITION") and a card reader FEEDS -- the 7503
                // pulls the next card from the hopper, so two
                // successive READs must return successive cards, not
                // the same card twice (StretchIO.bsv "CARD FEED").
                // The printer has no position because this model has
                // no record structure for a printed line.
                // THE DISK'S CURSOR IS AN ARC, NOT A WORD.  Printed
                // p.161: "Associated with each disk is an arc address
                // register.  As successive arcs are used, this
                // register is increased by one for each arc."  A
                // transfer therefore starts at the FIRST WORD OF THE
                // ARC the register names -- arc * 512 -- and not
                // wherever the previous transfer stopped, which is the
                // tape's rule and not this one.
                // THE CONSOLE PRINTER KEEPS ITS PLACE, like the
                // card reader and unlike the printer stand-in: a
                // console does not go back to the top of the page for
                // every message, and MCP's error routine writes one
                // message as a CHAIN of control words (printed p.8's
                // X MS CW1 then X MSG CW), so consecutive writes that
                // restarted would print on top of each other.
                devIdx: tapeCh    ? io.tapePos()
                      : readerCh  ? zeroExtend(io.readerPos())
                      : consoleCh ? zeroExtend(io.consolePos())
                      : diskCh    ? (zeroExtend(io.arcAddr())
                                     * fromInteger(arcWords))
                      : 0,
                remaining: rem0, suppressEop: seop, untilMark: False,
                zeroFill: False,
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
    return IoOutcome{needsRead: needsRead, ioStart: ioStart, ind: ind};
  endactionvalue
endfunction

function ActionValue#(ExecResult)
    execute(StretchStorage st, StretchIO io, HWordAddr pc, InstrLen len, DecodedInstr di,
            Vector#(2, Word64) prefetch, Bit#(2) prefetchCount, Bool atIntAddr,
            ExSubject ex) =
  actionvalue
    Maybe#(WordAddr) needsRead = tagged Invalid;
    // WHEN `ex.under` IS TRUE, `pc` AND `len` ARE THE EXECUTE'S, NOT
    // THE SUBJECT'S, and that is the whole of p.49's instruction-counter
    // rule: "When an execution operation is initiated in the main
    // program, the instruction counter is stepped in normal fashion as
    // in all operations of the main program.  However, it is never
    // stepped during the execution of any subject instruction even if
    // the subject instruction is again one of the execution
    // instructions."  mkEBox installs the subject under the EX's own
    // pc/len, so `fallthrough` is the half-word after the EXECUTE at
    // every level of the chain, and StretchCore's commitNext -- which
    // reads pc/len back out of the E-box -- steps past the EXECUTE and
    // nothing else.  p.52 item 3 of what a suppression must exclude
    // ("the stepping of the instruction counter") is the same rule seen
    // from the other side.
    HWordAddr fallthrough = pc + ((len == Full) ? 2 : 1);
    HWordAddr next = fallthrough;
    Word64 ind = st.readIndicators();

    // IF, p.32 CLASS 1: "The location of each instruction to be
    // executed with the exception of the single instructions at the
    // effective interruption address which are executed when an
    // interruption occurs."  `atIntAddr` is that exception, and it is
    // why this needs a parameter at all: rl_prepare knows it as
    // isValid(intPC) and execute() cannot see it.
    //
    // WHY HERE AND NOT AT THE FETCH.  The instruction buffers prefetch
    // ahead speculatively (StretchIBox's 1Y/2Y), and p.32 monitors the
    // location of instructions TO BE EXECUTED -- a word fetched and
    // then thrown away by a taken branch must not raise IF.  Every
    // dispatch path passes the instruction's own `pc` here, so this is
    // the one place that sees exactly the executed ones.
    //
    // AND NOT IN rl_prepare EITHER, which is the other obvious site:
    // setting the indicator there would make a second writer of
    // `indicators` in a rule that already calls execute(), the G0004
    // shape StretchStorage's own comments describe.
    //
    // Run on EVERY call including the ones that bail for an operand
    // read -- that call's `ind` is discarded and the resuming call
    // reaches this line again with the same `pc`.
    if (!atIntAddr) ind = ifSignal(st, pc[18:1], ind);

    // THE SAME CLASS 1, FOR A SUBJECT INSTRUCTION'S OWN LOCATION.
    // `pc` above is the EXECUTE's location, deliberately (see
    // `fallthrough`); the subject's location is a different address and
    // p.32 class 1 -- "the location of each instruction to be executed"
    // -- covers it too, because a subject instruction IS executed.
    // mkEBox evaluates it, one level at a time, and hands the answer
    // in; the reason it is not evaluated here is in ExSubject's comment.
    //
    // AND THE BELOW-32 CARVE-OUT IS WHY `ifViolates` IS THE RIGHT
    // PREDICATE FOR IT, which is not the same as it being the same
    // rule.  p.50 on EXECUTE: "An effective address of EXECUTE that is
    // below 32.00 (including addresses between 1.00 and 3.32) is not
    // monitored by the address monitoring mechanism; that is, indicator
    // IF cannot be actuated by these addresses."  ifViolates' own
    // `a >= 32` guard exists for a DIFFERENT reason -- p.45 on AD,
    // "branching to an address below 32 also actuates the indicator",
    // plus p.32's "an address which actuates AD cannot actuate any of
    // the address alarm indicators" -- so for a BRANCH below 32 the
    // machine raises AD instead of IF.  For an EXECUTE below 32 it
    // raises NEITHER: p.50 says the subject "may occupy any addressable
    // location", so there is no invalid address to report.  The two
    // rules happen to agree on the numeric test and disagree on what
    // else happens, and the model gets both right today only because
    // it does not raise AD for a branch below 32 either (ifViolates'
    // own note says so).  Stated so that a later AD implementation does
    // not reach for this call site.
    if (ex.ifSig) ind = setBit(ind, ind_IF, 1);

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
    IndexWord idxWriteVal = IndexWord{addr:0, sign:0, flag:0, spare:0, count:0, refill:0};
    Maybe#(Tuple2#(Bit#(4), IndexWord)) vflPending = tagged Invalid;

    // A started RD/W transfer, similarly threaded out rather than
    // performed inline: a block can be many words, and this function
    // (like every other execute() arm) may only call st.writeWord (or,
    // for a WRITE, io.writePrinterWord) once per invocation -- see the
    // IoOp case below.
    Maybe#(IoXfer) ioStart = tagged Invalid;
    // The same shape for a multi-word TRANSMIT: the first word is
    // moved by the arm itself and the rest by StretchCore's rl_xmit.
    Maybe#(XmitXfer) xmitStart = tagged Invalid;

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
        IndexOutcome xo <- dirIndexOp(st, di_, prefetch, prefetchCount, ind);
        needsRead   = xo.needsRead;
        doIdxWrite  = xo.doIdxWrite;
        idxWriteReg = xo.idxWriteReg;
        idxWriteVal = xo.idxWriteVal;
        ind         = xo.ind;
      end

      // -----------------------------------------------------------
      // Immediate index arithmetic (pocket card "IMMEDIATE INDEX
      // ARITHMETIC"; semantics extrapolated from the direct forms
      // above plus the mnemonic table -- see bsv/README.md "Scope").
      // -----------------------------------------------------------
      tagged ImmIndex .ii: begin
        IndexOutcome xo <- immIndexOp(st, ii, prefetch, prefetchCount, ind);
        needsRead   = xo.needsRead;
        doIdxWrite  = xo.doIdxWrite;
        idxWriteReg = xo.idxWriteReg;
        idxWriteVal = xo.idxWriteVal;
        ind         = xo.ind;
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
          // EXE, p.49, and this arm is the one the manual NAMES: "the
          // suppressed actions include... the counting and refilling in
          // COUNT, BRANCH AND REFILL".  So `doIdxWrite` -- which is
          // exactly the count and the refill -- is not taken either,
          // and neither is `o.ind`, which carries the index result
          // indicators of a count that p.45 item 18 says never
          // happened ("The subject operation was suppressed").
          if (ex.under && o.taken)
            ind = setBit(ind, ind_EXE, 1);
          else begin
            ind = o.ind; doIdxWrite = o.doIdxWrite;
            idxWriteReg = o.idxWriteReg; idxWriteVal = o.idxWriteVal;
            if (o.taken) next = o.relative ? (fallthrough + o.target) : o.target;
          end
        end
      end

      tagged BranchInd .*: begin
        BranchOutcome o = evalBranch(st, di, ind, prefetch, prefetchCount, 0);
        // EXE, p.49.  `o.ind` is dropped here, not merged, and that
        // decision is an INFERENCE, flagged rather than smoothed: it
        // carries BRANCH ON INDICATOR's own `clear` (the BZ forms), and
        // the manual's list of suppressed actions -- BD's disabling,
        // BE/BEW's enabling, CBR's counting and refilling -- ends "and
        // so on" without naming the clear.  p.45 item 18's "The subject
        // operation was suppressed" is what tips it, since the clear is
        // part of the operation.  NO DECK WITNESS: routine 1262 TEST
        // 1CC's first subject class IS an EX of a branch-on-indicator,
        // but it sits on PDF p.92, which the transcription
        // (decks/ax5b_162_test1cc.strap) cuts away at I6225 --
        // its header says so in as many words.
        if (ex.under && o.taken)
          ind = setBit(ind, ind_EXE, 1);
        else begin
          ind = o.ind;
          if (o.taken) next = o.relative ? (fallthrough + o.target) : o.target;
        end
      end

      // -----------------------------------------------------------
      // Unconditional branching / Store Zero / Refill.
      // -----------------------------------------------------------
      tagged BranchOrMisc .bm: begin
        if (!bm.misc) begin
          // THE ENABLE BIT, p.40: BRANCH ENABLED (000) enables the
          // interrupt system, BRANCH DISABLED (001) disables it,
          // BRANCH ENABLED AND WAIT (100) enables.  All three act
          // UNCONDITIONALLY and BEFORE the branch, so even a
          // suppressed one still changes the bit.  B (010), BR (011)
          // and NOP (110) leave it alone.
          //
          // AND THAT IS p.52's RULE, not just a convenience.  Its
          // list of what survives a suppressed instruction ends with
          // "the changing of the state of the interruption system
          // which occurred as specification of BRANCH ENABLED, BRANCH
          // DISABLED, or BRANCH ENABLED AND WAIT."  Acting before the
          // branch is what makes that true here.
          //
          // (This comment used to end "there is no interruption
          // mechanism, and BE/BD/BEW remain identical AS BRANCHES."
          // The mechanism exists now -- StretchCore's rl_interrupt --
          // and BEW's WAIT is still unimplemented, which is a
          // different claim.  See docs/NEXT.md item 3.)
          //
          // AND THE ENABLE CHANGE MOVED *BELOW* evalBranch on
          // 2026-09-25, which is a real reordering and not tidying.
          // p.49 on EXE: "the subject instruction is not allowed to
          // change the state of the interruption system... The
          // suppressed actions include the disabling in BRANCH
          // DISABLED, the enabling in BRANCH ENABLED or BRANCH ENABLED
          // AND WAIT."  st.setIrqEnabled is an Action and cannot be
          // taken back later in the same call, so the EXE decision has
          // to be made before it -- which means evalBranch has to run
          // first.  Safe: evalBranch's BranchOrMisc arm reads the
          // instruction and the index registers only, never the enable
          // bit, so moving it ahead cannot change what it returns.
          // Routine 1262 TEST 1CC's I6227 and I6232 probes are the
          // deck's own test of exactly this pair of suppressions.
          BranchOutcome o = evalBranch(st, di, ind, prefetch, prefetchCount, 0);
          if (ex.under && o.taken)
            ind = setBit(ind, ind_EXE, 1);
          else begin
            case (bm.code)
              3'b000, 3'b100: st.setIrqEnabled(True);   // BE, BEW
              3'b001:         st.setIrqEnabled(False);  // BD
              default:        noAction;
            endcase
            if (o.taken) next = o.relative ? (fallthrough + o.target) : o.target;
          end
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
              else if (!installed(zw))
                // ADDRESS INVALID, Reference Manual printed p.21 --
                // NOT p.20, which this file and
                // docs/microarchitecture_plan.md both cited:
                //
                //   "When an effective word address is obtained which
                //    does not correspond to a core storage location
                //    that is physically available in a particular
                //    installation, indicator AD, address invalid, is
                //    turned on.  An instruction with an invalid data
                //    address is executed as a NO OPERATION
                //    instruction.  A branch instruction with an
                //    invalid address is also executed as a NO
                //    OPERATION.  A negative effective address is not
                //    considered to be invalid; its magnitude is used."
                //
                // MCP's BOOTSTRAP IS WHAT FOUND THIS MISSING, and it
                // needs it to do something no diagnostic deck in this
                // corpus does: SIZE CORE STORAGE BY RUNNING OFF THE
                // END OF IT.  Printed p.2 lines 36-39 are
                //
                //     X CLSTO  Z,0.0($15)      -CLEAR ONE WORD
                //              BADZ,$+1.0      -IF DONE CLEARING STORAGE
                //              CB+,$15,X CLSTO -ADVANCE AND RETURN
                //              SV,15,X S ROOF  -TEMPORARILY SAVE 7030 SIZE
                //
                // -- a loop with NO TERMINATING COUNT.  The only thing
                // that ends it is AD coming on, which BADZ then tests
                // and clears; X S ROOF is where the machine's size
                // comes from.  Without this guard the model ran the
                // loop past 98,304 words, wrapped the 24-bit address
                // field, and began clearing from the bottom again --
                // measured, twelve million steps in, with index 15's
                // value back at word 6.
                //
                // ONLY THE Z ARM IS GUARDED HERE.  The rule is
                // general and the floating-point arm already applies
                // it; every other class is still open and
                // docs/microarchitecture_plan.md records that.  A
                // blanket guard would have to decide, for each class,
                // which "addresses" are data addresses and which are
                // not -- the FP arm's own SHF and E+I exclusions are
                // that question answered once -- and inventing those
                // answers without a witness is what AGENTS.md rule 4
                // forbids.
                ind = setBit(ind, ind_AD, 1);
              else
                if (protViolates(st, zw)) ind = setBit(ind, ind_DS, 1);
                else st.writeWord(zw, 0);
            end
            3'b000, 3'b001: begin // R / RCZ -- Refill, and Refill on
              // Count Zero.  Ref. Manual p.26: the operand is the
              // index word AT THE EFFECTIVE ADDRESS, and that word's
              // REFILL field (bits 46-63) names the word which
              // replaces it.  RCZ acts only if its count (28-45) is
              // zero.
              //
              // THIS USED TO READ bm.idx AND IT WAS WRONG.  bm.idx is
              // hw[3:0], IBM bits 28-31 -- the register that MODIFIES
              // the address, which Z three arms down correctly feeds
              // through effAddr24.  Reading it as the OPERAND meant
              // "R,$X15" refilled index register 0 from index register
              // 0's refill field and never touched $X15.  The listing
              // is unambiguous: jb_ax4b p.58 assembles "R,$X15" to
              // 37.02 00, address 037 = word 31 = $X15, idx = 0.
              // MEASURED, not merely read: routine 1238's test 1
              // halted at SERS with SEN = 005313.00, its first check,
              // "REFILLED X15 FROM LOCN 1 INSTEAD OF LOCN 20".
              // AND A REFILL ADDRESS OF 1-15 IS SUPPRESSED, which the
              // routine's own header states -- "NOPING IF RF IS FROM 1
              // TO 15" -- and test 2 pins from BOTH sides:
              //
              //   TEST 2G  "CHK REFILL FRM LOCN 0"      word 0 DOES
              //            refill, from the permanently protected
              //            zero; its failure text is "FAILED TO
              //            REFILL FRM LOCN 0"
              //   TEST 2H  "CHK NO REFILL FRM LOCNS 1 THROUGH 17"
              //            (octal, so 1-15) -- suppressed, failure
              //            text "DID REFILL"
              //
              // So the obvious spelling, `refill < 16`, is WRONG: it
              // would pass 2H and fail 2G. Zero refills; only 1-15 are
              // gated. Both cases are in ibox4_refill_nop, together,
              // for exactly that reason.
              function Bool refillLegal(Bit#(18) rf) =
                (rf == 0) || (rf >= 16);
              WordAddr rw = baWord(effAddr24(st, {bm.addr, 5'b0}, bm.idx));
              if (rw >= addrIndexBase && rw < addrIndexBase + 16) begin
                Bit#(4) j = truncate(rw - addrIndexBase);
                IndexWord x = st.readIndex(j);
                if ((bm.code == 3'b000 || x.count == 0) && refillLegal(x.refill)) begin
                  // DF, p.32 class 3: "the refill address used in
                  // index refill operations and the operations REFILL
                  // and REFILL ON COUNT ZERO."  INSIDE this gate, not
                  // before it -- a refill that RCZ's count suppresses,
                  // or that refillLegal suppresses, reads nothing, and
                  // p.32 monitors "storage addresses actually used".
                  ind = dfSignal(st, zeroExtend(x.refill), ind);
                  // DF'S MASK-DEPENDENT HALF -- see dfSuppresses, and
                  // evalBranch's note for why the test precedes the
                  // bail-out.  R and RCZ are the two operations printed
                  // p.32's class 3 NAMES, so p.45 item 20's "the fetch
                  // did not take place, and the entire operation was
                  // suppressed" applies to them with nothing else in
                  // between: the whole operation here IS the refill, so
                  // suppressing it leaves the index register untouched.
                  // INSIDE both existing gates, unchanged: a refill
                  // that refillLegal or RCZ's count already suppresses
                  // reads nothing, so there is nothing for the mask to
                  // suppress either.
                  if (dfSuppresses(st, zeroExtend(x.refill))) begin
                    // suppressed: deliberately nothing at all
                  end else if (prefetchCount >= 1) begin
                    idxWriteReg = j; doIdxWrite = True;
                    idxWriteVal = unpackIndexWord(prefetch[0]);
                  end else
                    needsRead = tagged Valid zeroExtend(x.refill);
                end
              end else begin
                // ANYWHERE ELSE the index word is an ordinary storage
                // word, so it takes TWO SEQUENTIAL reads -- the same
                // shape V+CR has, and for the same reason: a value
                // from the first read decides the address of the
                // second.
                //
                //   prefetch[0]  the index word at the effective
                //                address, whose refill field names
                //   prefetch[1]  the word that replaces it
                //
                // Driven by routine 1238 test 2, whose first two cases
                // are exactly this: "TEST 2A - OP ADR IS EM, RF ADR IS
                // EM" and "TEST 2B - OP ADR IS EM, RF ADR IS XS".
                if (prefetchCount == 0)
                  needsRead = tagged Valid rw;
                else begin
                  IndexWord x = unpackIndexWord(prefetch[0]);
                  if ((bm.code == 3'b000 || x.count == 0) && refillLegal(x.refill)) begin
                    // DF, p.32 class 3 -- see the sibling gate above.
                    // `rw` itself gets no DF: it is read here and
                    // WRITTEN below, so p.32 puts it on the DS side,
                    // and the protViolates call below is where it is
                    // answered.
                    ind = dfSignal(st, zeroExtend(x.refill), ind);
                    // DF's mask-dependent half -- see the sibling gate
                    // above.  The DESTINATION on this path is the
                    // storage word `rw`, not an index register, so
                    // suppression here means that word is NOT rewritten
                    // and keeps whatever it held.
                    //
                    // AND A CORNER THIS DELIBERATELY DOES NOT DECIDE,
                    // labelled rather than guessed.  If `rw` is ALSO
                    // protected, the arm below would have set DS, and
                    // skipping it drops that.  p.52 item 1 argues the
                    // other way -- a suppression "must necessarily
                    // exclude... the actuation of those indicators,
                    // associated with the instruction, of Class S" --
                    // and p.52's own worked example actuates four
                    // indicators on one suppressed instruction.  But
                    // p.32 opens "if an address which is associated
                    // with an operation is NOT ACTUALLY USED, it will
                    // not be monitored", and a suppressed R stores
                    // nowhere.  Neither reading is witnessed by any
                    // deck this project has read, and no program in the
                    // suite reaches the combination (it needs enabled +
                    // DF mask one + `rw` protected + refill protected),
                    // so this takes the same uniform shape as every
                    // other suppression site rather than inventing a
                    // rule.  Stated here, and in docs/NEXT.md.
                    if (dfSuppresses(st, zeroExtend(x.refill))) begin
                      // suppressed: deliberately nothing at all
                    end else if (prefetchCount >= 2)
                      if (protViolates(st, rw)) ind = setBit(ind, ind_DS, 1);
                      else st.writeWord(rw, prefetch[1]);
                    else
                      needsRead = tagged Valid zeroExtend(x.refill);
                  end
                end
              end
            end
            3'b010: begin // EX (EXECUTE), Reference Manual printed p.50
              // "Bits 0-18 of the effective address form the address of
              // the location of a subject instruction that is fetched
              // and executed."
              //
              // THIS ARM ONLY ASKS FOR THE FETCH.  It sets needsRead
              // and touches nothing else, so the E-box's ordinary
              // operand bail-out carries it: mkEBox issues the read,
              // holds this EX, and on the next clock decodes the word
              // and installs the SUBJECT as the held instruction under
              // this EX's own pc and len.  execute() is a pure function
              // that BSV inlines, so it cannot call itself and a second
              // instantiation would be a second writer of storage in
              // one rule (the G0004 shape StretchStorage's comments
              // describe); the bail/resume path costs one clock that
              // any operand fetch already costs and needs neither.
              //
              // `exSubjectAddr` above computes the same address and is
              // what mkEBox uses -- one function, two callers, so the
              // half-word-address reading cannot drift between them.
              //
              // THE TWO CALLS SEE THE SAME INDEX REGISTER, and that is
              // a CONSEQUENCE OF THE DRAIN rather than a coincidence.
              // StretchIBox's iboxHazard returns True for this arm, so
              // an EX is not dispatched until every look-ahead level
              // has retired; StretchCore's rl_prepare then blocks on
              // ebox.busyFor(OwnerIbox) while the EX is held, so no new
              // level can load; pendingIdxWrite is necessarily Invalid
              // at dispatch (rl_idx_write outranks rl_prepare), so
              // progressive indexing's second step cannot interleave;
              // and rl_recover's restoreIndex is reachable only from
              // rl_au_remove, which needs a level. No rule that writes
              // an index register can fire between the two calls.
              //
              // NO INDICATOR IS SET HERE, and none could be: a call
              // that bails has its `ind` discarded (see this function's
              // tail).  The subject's own location is monitored on the
              // call that finally runs the subject, through
              // ExSubject.ifSig.
              //
              // Reached exactly once per EXECUTE, with prefetchCount 0:
              // mkEBox replaces the held instruction before this arm
              // could see a collected word, so there is no
              // "prefetchCount >= 1" branch to write.
              let sa = validValue(exSubjectAddr(st, di));
              needsRead = tagged Valid sa[18:1];
            end
            3'b011: begin // EXIC (EXECUTE INDIRECT AND COUNT), p.50
              // "Bits 0-18 of the full-word addressed by bits 0-17 of
              // the effective address are used as a pseudo-instruction
              // counter.  The contents of the pseudo-instruction
              // counter address the location of a subject instruction
              // that is fetched and executed."
              //
              // TWO BAIL-OUTS, ONE PER INDIRECTION, and that is the
              // whole of what this arm does.  EX has one (fetch the
              // subject); EXIC has two (fetch the pseudo-IC, then fetch
              // the subject it names).  Everything that happens BETWEEN
              // them -- the address checks aside -- is mkEBox's, because
              // it needs state this pure function does not have.
              //
              //   prefetchCount 0  the pseudo-IC has not been read
              //   prefetchCount 1  prefetch[0] IS the pseudo-IC word
              //
              // Reached at most twice per EXIC: mkEBox replaces the held
              // instruction with the SUBJECT before a third call could
              // happen, so there is no "prefetchCount >= 2" branch.
              WordAddr pw = validValue(exicPsicAddr(st, di));
              if (prefetchCount == 0) begin
                if (pw < 16)
                  // p.50: "Pseudo-instruction counters may occupy any
                  // of the index registers as well as main core storage
                  // locations but cannot occupy locations addressed
                  // between 0 and 15."  (That sentence finishes at the
                  // TOP OF THE RIGHT COLUMN of PDF p.53, where the "15."
                  // looks like a list number and is not.)  p.45 item 16
                  // says what an address "invalid for the specified
                  // operation" does: "Address Invalid (AD) ... The
                  // affected instruction is executed as a NO
                  // OPERATION."  So: AD, and nothing else at all -- no
                  // fetch, no step.  That is routine 1262 TEST 3A's
                  // three error messages exactly ("-NO INTERRUPT...",
                  // "-AD NOT SET...", "-INSTRUCT NOT NOPED...").
                  //
                  // THE BOUNDARY IS THE MANUAL'S, NOT THE DECK'S, and
                  // the two do not agree.  1262 TEST 3A's messages all
                  // say "LESS THAN 15"; the manual says "between 0 and
                  // 15".  No row discriminates -- the deck's pseudo-IC
                  // is word 9, illegal under either reading -- so this
                  // takes the manual (AGENTS.md rule 4) and the reading
                  // "0 through 15 inclusive", which is also the only
                  // one the machine's own storage map supports: 0-15 are
                  // the special registers and 16-31 are the index
                  // registers, which the same sentence expressly
                  // ALLOWS.  Recorded in docs/NEXT.md; a deck row with
                  // a pseudo-IC at word 15 would decide it.
                  ind = setBit(ind, ind_AD, 1);
                else if (protViolates(st, pw))
                  // THE EXIC'S EFFECTIVE ADDRESS IS A DATA STORE
                  // ADDRESS, and printed p.32 (PDF 35) names this
                  // instruction to say so.  "Address monitoring for
                  // Data Store includes: ... 5. The effective address
                  // of EXECUTE INDIRECT AND COUNT."  It is NOT in the
                  // Data Fetch list, and the same page says why: "A
                  // fetch-type operation is one in which the contents
                  // of an addressed storage location are read out for
                  // use but are not subject to change" -- and a
                  // pseudo-IC is read out AND changed.
                  //
                  // SO THE WHOLE OPERATION IS TERMINATED, not just the
                  // store, and that is stated twice.  p.32: "When an
                  // address alarm is caused by a data address used in a
                  // store-type operation, indicator DS is turned on.
                  // Since this indicator is permanently masked on,
                  // storing in core storage is always suppressed, and
                  // the operation is always terminated."  p.45 item 19:
                  // "The operation was suppressed."  Terminating HERE,
                  // before the pseudo-IC is even read, is what
                  // "suppressed" means; the alternative -- set DS, skip
                  // the store, run the subject anyway -- would execute
                  // a subject with an unstepped pseudo-IC, which is
                  // precisely the state rule (c) of 1262 TEST 2B exists
                  // to catch.
                  //
                  // THE TEST IS UNGUARDED, exactly as the Z arm's is:
                  // protViolates carries p.32's own enable gate and its
                  // 1-3 carve-out, and no `>= 32` guard belongs here
                  // (that guard is an INSTRUCTION-fetch rule; see
                  // ifViolates).  ONE CORNER IS UNWITNESSED AND SAID
                  // RATHER THAN SMOOTHED: p.32 spells the suppression
                  // "storing in CORE STORAGE is always suppressed",
                  // while p.50 expressly lets a pseudo-IC live in an
                  // index register.  The boundary test is applied
                  // uniformly here; no source read for this work says
                  // what the boundary registers do to a register-
                  // resident pseudo-IC, and no deck row reaches it.
                  ind = setBit(ind, ind_DS, 1);
                else
                  needsRead = tagged Valid pw;
              end else begin
                // The pseudo-IC has arrived.  Bits 0-18 of it are the
                // subject's half-word location (IBM bit 0 = BSV 63).
                HWordAddr sa = prefetch[0][63:45];
                if (sa[18:1] < 32)
                  // p.50, the sentence that finishes at the top of the
                  // right column: "Subject instructions of EXECUTE
                  // INDIRECT AND COUNT may occupy any available
                  // locations with addresses 32.00 and greater."  A
                  // DIFFERENT RULE FROM THE ONE ABOVE and a different
                  // boundary -- 1262 TEST 3A puts the pseudo-IC below
                  // 15, TEST 3B leaves it legal and puts the SUBJECT
                  // below 32 -- and both are p.45 item 16's "invalid
                  // for the specified operation ... executed as a NO
                  // OPERATION".  Note what is NOT done: the pseudo-IC
                  // is not stepped, because the step happens "after the
                  // subject instruction has been fetched" and no
                  // subject is fetched.
                  //
                  // AND THIS IS WHY EX'S OWN CONTRAST HOLDS.  EX's
                  // subject "may occupy any addressable location"
                  // (same page), so a low subject is legal there and
                  // illegal here.  The two arms must not share a guard.
                  //
                  // NOT IMPLEMENTED, and bounded rather than guessed:
                  // printed p.51 item (d), "If the address of the
                  // location of the subject instruction of EXECUTE or
                  // EXECUTE INDIRECT AND COUNT is both protected and
                  // invalid, indicator IF will be actuated.  Indicator
                  // AD will not be actuated as a result of this invalid
                  // address unless the IF mask bit is zero."  EX left
                  // the same corner open; this arm raises AD and never
                  // IF.
                  ind = setBit(ind, ind_AD, 1);
                else
                  needsRead = tagged Valid sa[18:1];
              end
            end
            default: ind = setOpInvalid(ind);
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
        end else if (ex.under && o.taken) begin
          // AND A CORNER THIS DELIBERATELY DOES NOT DECIDE, labelled
          // rather than guessed -- the same shape, and the same
          // argument, as the one the R/RCZ arm leaves open.  Dropping
          // `o.ind` here also drops a DF signal a COUNT, BRANCH AND
          // REFILL inner branch may have raised on its refill address
          // (p.32 class 3).  p.52 item 1 argues the other way: a
          // suppression "must necessarily exclude... the actuation of
          // those indicators, associated with the instruction, of
          // Class S, and indicators DF and IF WHEN THEIR MASK BITS ARE
          // ZERO".  p.45 item 18's "the subject operation was
          // suppressed" argues this way.  No deck this project has
          // read witnesses it and no program in the suite reaches the
          // combination (it needs SIC + a CBR inner branch + a
          // protected refill + running under EX), so this takes the
          // same uniform shape as every other suppression site.
          //
          // EXE, p.49, DECIDED HERE AND NOT AT THE COMMIT POINT, and
          // the placement is the point: SIC stores "if and only if the
          // associated branching is successful", and reading the target
          // half-word to modify it is the next thing this arm would do.
          // p.45 item 18 says the subject operation "was suppressed",
          // so the read for a store that never happens must not be
          // issued at all -- hence before the `needsRead` below rather
          // than after it.  (BRANCH ON BIT is the opposite case and its
          // arm says so: there the condition cannot be known until the
          // bit word has been read, so its EXE test comes after.)
          ind = setBit(ind, ind_EXE, 1);
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
              next = o.relative ? (fallthrough + o.target) : o.target;
              if (ha < 32)
                ind = setBit(ind, ind_AD, 1);
              else begin
                Word64 w = prefetch[o.readsUsed[0]];
                HalfWord32 old = (ha[0] == 0) ? w[63:32] : w[31:0];
                HalfWord32 hwv = {fallthrough, old[12:0]};
                Word64 w2 = (ha[0] == 0) ? {hwv, w[31:0]} : {w[63:32], hwv};
                if (protViolates(st, ha[18:1])) ind = setBit(ind, ind_DS, 1);
                else st.writeWord(ha[18:1], w2);
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
        // WHAT THIS ARM CAN HONOUR: one word, forward, not a swap.
        // Everything else sets OP and no-ops, which is what
        // bsv/README.md's "decoded but not executed" list has always
        // CLAIMED for "Transmit backward/SWAP/multi-word" and what
        // only `backward` actually did until 2026-09-22.
        //
        // THE COUNT. Reference Manual pp.30-31: the count is index J's
        // bits 28-45 (0 meaning 2^18), or -- with the immediate
        // modifier, bit 56 -- instruction bits 51-54, where **0 MEANS
        // SIXTEEN**. So "one word" is exactly immCount=1 and j=1;
        // j=0 is a sixteen-word transmit and must NOT pass. A DIRECT
        // count lives in an index register this arm never reads, so no
        // direct count can be honoured at all and all of them set OP --
        // conservative by construction: it refuses a direct count of
        // one that it would in fact have executed correctly, rather
        // than executing a direct count of n as one word.
        //
        // SWAP was the silent case. The decoder used to discard bit
        // 57, so a forward SWAP arrived here as a Transmit and this
        // arm moved one word and set nothing -- demonstrated on
        // 2026-09-22 with "SWAPI,1,SRC,DST", which left SRC alone and
        // copied it into DST with OP clear. Unreachable from STRAP
        // until strap_asm gained TRANSMIT_CODES the same day.
        // MULTI-WORD TRANSMIT, 2026-10-18.  The paragraph above is
        // kept because it is the history, but it is no longer what
        // this arm does: a FORWARD, UNIDIRECTIONAL transmit of any
        // count now executes, immediate or direct.
        //
        // THE COUNT, Reference Manual printed p.30, read whole:
        //
        //   immediate (bit 56 = 1): "the full word count is specified
        //   by instruction bits 51-54.  A zero count field indicates
        //   the maximum count of 16 full words."
        //
        //   direct (bit 56 = 0): "the field J, bits 51-54, specifies
        //   an index register.  The count field, bits 28-45, of the
        //   index word in this register is used as a full word count.
        //   A count field of zero is interpreted as 2^18... such a
        //   count is never valid.  It is not detected, however, until
        //   the data transmission actually encounters an invalid or
        //   protected address."  And: "A zero J field refers to
        //   location 16, X0" -- so J = 0 is a real register here, not
        //   "no index".
        //
        // NOTHING IS WRITTEN BACK.  Same page: "The count field in
        // the index register is not changed as a result of the
        // operation, and the index result indicators are not
        // affected."  So this arm reads the count and forgets the
        // register, which is why there is no idxWrite here.
        //
        // BACKWARD AND SWAP STILL SET OP.  MCP needs neither, SWAP's
        // two-way interchange is a different datapath, and a refusal
        // that is documented beats a half-built interchange.
        Bit#(19) xmitCount = (t.immCount == 1)
          ? ((t.j == 0) ? 19'd16 : zeroExtend(t.j))
          : ((st.readIndex(t.j).count == 0)
               ? 19'h40000 : zeroExtend(st.readIndex(t.j).count));
        if (t.backward == 1 || t.swap == 1)
          ind = setOpInvalid(ind);
        else begin
          // Prefetch/bail-out shape: reads srcBase, writes the SAME
          // value verbatim to dstBase once available -- a dependent
          // chain (the write's data IS the read's response), same
          // shape as ST/M+/CM above.
          WordAddr srcBase = baWord(effAddr24(st, t.addr1, t.i1));
          WordAddr dstBase = (effAddr19(st, t.addr2, t.i2))[18:1];
          if (prefetchCount >= 1) begin
            if (protViolates(st, dstBase)) ind = setBit(ind, ind_DS, 1);
            else begin
              st.writeWord(dstBase, prefetch[0]);
              // THE FIRST WORD IS MOVED HERE AND THE REST BY rl_xmit,
              // one per clock, because this model writes storage once
              // per rule.  p.30: "the sending and receiving addresses
              // of each successive word transmitted are obtained by
              // incrementing the previous addresses by one", so the
              // continuation starts one past each.
              if (xmitCount > 1)
                xmitStart = tagged Valid XmitXfer {
                  src: srcBase + 1, dst: dstBase + 1,
                  remaining: xmitCount - 1 };
            end
          end else
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
        VflOutcome co <- connectiveOp(st, cn, prefetch, prefetchCount, ind);
        needsRead  = co.needsRead;
        vflPending = co.vflPending;
        ind        = co.ind;
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
        // DF, p.32 class 1 -- see vflIntOp's fuller note above.  The
        // arithmetic class is exactly the floating-point group that
        // fetches an operand word; the store class (ST/SRT/SRD/SLO/
        // SHF/E+I) reads none, which is why it was lifted out into
        // fpStoreClass in the first place.
        Bool dfSupp = False;
        if (known && !isStoreClass) begin
          ind = dfSignal(st, ea, ind);
          dfSupp = dfSuppresses(st, ea);
        end

        // DF'S MASK-DEPENDENT HALF -- see dfSuppresses.  Only the
        // arithmetic class can reach it (the store class fetches
        // nothing, and an unknown code has already been decided), so
        // this rides on the same `known && !isStoreClass` the signal
        // does.  Suppressed means: no readWordReq for the operand, no
        // fpArithClass call, so the accumulator, the result
        // indicators, MOP and the exponent-range indicators are all
        // left as they were.  The AD guard outside stays outside: an
        // address which actuates AD "cannot actuate any of the address
        // alarm indicators" (p.32), so an uninstalled address never
        // gets this far.
        if (dfSupp) begin
          // suppressed: deliberately nothing at all
        end
        else if (!known)
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
        IoOutcome oo <- ioOpExec(st, io, io_, prefetch, prefetchCount, ind);
        needsRead = oo.needsRead;
        ioStart   = oo.ioStart;
        ind       = oo.ind;
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
          Bit#(2) mod = bb.modAbc[2:1];
          // OPERATION TERMINATION, p.32, and the deviation protViolates'
          // own note has named since DS was written: "this suppresses
          // only the store, so a BB whose write is suppressed still
          // branches."  It no longer does.
          //
          // p.32 on DS: "Since this indicator is permanently masked on,
          // storing in core storage is always suppressed, AND THE
          // OPERATION IS ALWAYS TERMINATED."  The branch is part of the
          // operation, so a BRANCH ON BIT whose bit-change is suppressed
          // must not take its branch either.  p.32 says the same thing
          // in the other direction for IF, which is the corroboration
          // that the machine really does suppress a whole branch rather
          // than just its store: "the entire branch operation, including
          // any counting, bit changing, or index alteration, is
          // suppressed".
          //
          // TWO CONDITIONS, and both are load-bearing -- MEASURED, not
          // assumed.  A BB with mod == 00 CHANGES NOTHING, so it is not
          // a store-type operation at all and must still branch;
          // ds_terminates_branch.strap's first block is the one that
          // holds that, and it exists because the injection dropping
          // this `changes` term SURVIVED against the program's first
          // version.  protViolates carries the enable gate, so a
          // disabled machine branches and stores as before, which is
          // what lets that program set up a protected word at all.
          //
          // A `bw != 11` TERM WAS HERE AND CAME BACK OUT.  Word 11 is
          // the indicator register and its write is folded into `ind`
          // rather than issued to storage -- but protViolates ALREADY
          // returns False for it (11 is below 32 and outside 1-3, so
          // p.31's carve-out answers it), and the injection dropping
          // the term changed nothing.  A guard whose own comment has to
          // explain why it is redundant is decoration; protViolates is
          // the single authority on which addresses signal.
          Bool changes = (mod != 2'b00);
          Bool storeViolates = changes && protViolates(st, bw);
          // DF'S FIFTH CLASS-1 SITE, and the one the other four could
          // not reach.  Printed p.52 (PDF 55), read at 300 dpi; the
          // sentence wraps into the first two lines of p.53, which is
          // where clause 3 ends.  "Another example is that, since a
          // protected effective bit address in BRANCH ON BIT could
          // result in the destruction of information, alert DS or DF
          // may occur if: 1. The addressed bit is not specified to
          // remain unconditionally unchanged; that is, bits 60 and 61
          // of the instruction are not both zero.  The instruction is
          // suppressed without a test of the addressed bit, and
          // indicator DS is actuated.  2. The addressed bit is
          // specified to remain unconditionally unchanged, and the DF
          // mask bit is one.  The instruction is suppressed without a
          // test of the addressed bit, and indicator DF is actuated.
          // 3. The addressed bit is specified to remain unconditionally
          // unchanged, and the DF mask bit is zero.  Indicator DF is
          // actuated but does not cause suppression of the
          // instruction."
          //
          // `changes` IS LITERALLY p.52'S TEST.  StretchDecode takes
          // modAbc from w[3:1] and IBM bit n is BSV bit 63-n, so
          // modAbc[2:1] is IBM bits 60-61 and modAbc[0] is IBM 62, the
          // branch condition.  "bits 60 and 61 are not both zero" is
          // therefore `changes` and "specified to remain
          // unconditionally unchanged" is `!changes` -- the same term
          // DS already uses, read from the other side.  A read-only BB
          // is not a store-type operation, which is why DS must NOT
          // fire for it; p.52 is the manual saying, for this
          // instruction by name, that it is a fetch-type one instead.
          //
          // SO CLAUSE 3 IS ONE LINE AND CLAUSE 2 IS A TERM.  dfSignal
          // is the indicator and reads no mask bit -- that is the whole
          // of clause 3, and it is what a read-only BB against a
          // protected word raised NOTHING of before this.  dfSuppresses
          // is the mask, and that is clause 2.  Both are the shared
          // helpers the other four class-1 sites call, asked about the
          // same address, so this site cannot drift away from them.
          if (!changes) ind = dfSignal(st, bw, ind);
          // "SUPPRESSED WITHOUT A TEST OF THE ADDRESSED BIT", which
          // p.52 says of clause 1 as well as clause 2 -- so this gate
          // carries storeViolates too, and that half is a CORRECTION,
          // not new coverage.  The arm already refused the branch and
          // the bit change when storeViolates fired, but it still
          // computed the branch condition from the tested bit and
          // still signalled IF from the target of a branch p.52 says
          // was never decided.  The same page rules exactly that out
          // in the AD case, in so many words: "an invalid effective
          // bit address in BRANCH ON BIT causes the actuation of
          // indicator AD and the suppression of the instruction, since
          // no bit can be tested to complete its execution.  INDICATOR
          // IF CANNOT BE ACTUATED."  No test, no successful branch; no
          // successful branch, nothing for p.32's class 2 to monitor.
          //
          // WHAT IS DELIBERATELY NOT GATED ON IT: clause 1's own DS
          // actuation, which stays inside the bit-change block below,
          // and the instruction counter -- `next` keeps the
          // fall-through execute() computed on entry, which is p.52
          // item 3, "the stepping of the instruction counter".
          //
          // A MODEL ARTIFACT, stated rather than left to be found: the
          // suppressed instruction has still READ its bit word, because
          // this arm only runs once the prefetch has arrived.  Nothing
          // architectural depends on it -- the read has no side effect
          // and DF is the alarm for it -- but a cycle-accurate version
          // of this would have to decide before the fetch, not after.
          Bool noTest = storeViolates || (!changes && dfSuppresses(st, bw));
          HWordAddr tgt = effAddr19(st, bb.addr2, {3'b0, bb.idx}); // K: X1 only
          Bool wouldBranch = (tested == bb.modAbc[0]);
          // TWO NAMES, because p.52 distinguishes two things: the bit
          // says branch (`wouldBranch`, which the comments below name
          // with that meaning) and the machine was allowed to look
          // (`takeBranch`).  Everything downstream of the test hangs
          // off the second.
          // A THIRD NAME, and it is p.49's: EXE.  "The execution
          // exception indicator (EXE) is turned on by any branch
          // operation of a subject instruction in which the condition
          // for a successful branch is met.  When indicator EXE is
          // actuated, the branch and all associated operations are not
          // performed."  The condition is `wouldBranch && !noTest` --
          // the machine looked AND the bit said branch -- so `exeHit`
          // hangs off the same pair `takeBranch` did, and `takeBranch`
          // now excludes it so that every existing consumer (the IF
          // signal, the IF suppression, `next`) is suppressed without
          // restating the rule five times.  The bit change is gated
          // separately below because it does not hang off takeBranch.
          //
          // DECIDED AFTER THE READ, deliberately, and the SIC arm says
          // the same thing from the other side: a BRANCH ON BIT's
          // condition cannot be known until its bit word has arrived,
          // so the operand read is issued before EXE can be decided.
          // That is the one read an EXE-suppressed subject still makes,
          // and p.52's own account of a suppressed subject allows it
          // -- "an alert of Class S during... the execution of a
          // subject instruction of EXECUTE... may not cause full
          // suppression of the instruction."
          //
          // THIS IS THE ARM ROUTINE 1262 TEST 1CC ACTUALLY DRIVES:
          // "EX,I62B5" (condition met -> EXE, no branch) and
          // "EX,I62B6" (condition not met -> no EXE, nothing suppressed,
          // control to the instruction after the EX).
          Bool exeHit = ex.under && wouldBranch && !noTest;
          if (exeHit) ind = setBit(ind, ind_EXE, 1);
          Bool takeBranch = wouldBranch && !noTest && !exeHit;
          // IF, p.32's BIT CHANGING -- the third of the three things a
          // protected branch target suppresses, and the one
          // execute()'s shared commit point cannot reach: "the entire
          // branch operation, including any counting, bit changing, or
          // index alteration, is suppressed."  BRANCH ON BIT issues its
          // st.writeWord HERE, before that point, so the decision has
          // to be made here too -- the same reason `storeViolates`
          // above sits in this arm rather than at the commit.
          //
          // AND THE INDICATOR IS SET HERE FOR THE SAME REASON.  The
          // commit point signals IF on `next != fallthrough`; suppress
          // the branch and that test is false, so it would never fire.
          // Setting it here keeps "the indicator sets whatever the mask
          // says" true (p.45, and TEST 8C case 3's own error text).
          Bool ifSuppress = takeBranch && maskedOn(st, ind_IF)
                            && ifViolates(st, tgt[18:1]);
          if (takeBranch) ind = ifSignal(st, tgt[18:1], ind);
          if (takeBranch && !ifSuppress)
            next = tgt;
          // NOT gated on noTest, and the omission is the point: clause
          // 1's DS actuation is inside this block, and storeViolates --
          // noTest's own first term -- already stops the write.
          // `!exeHit` is the EXE half of "all associated operations are
          // not performed": the bit change does NOT hang off
          // takeBranch (a BB1 sets its bit whether or not it branches),
          // so suppressing it needs its own term.  A subject BB whose
          // condition is NOT met is not suppressed at all and still
          // changes its bit, which is why this is `exeHit` and not
          // `ex.under`.
          if (changes && !ifSuppress && !exeHit) begin
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
              if (storeViolates) ind = setBit(ind, ind_DS, 1);
              else st.writeWord(bw, insertFieldBits(prefetch[0], baBit(ba), 1,
                                               zeroExtend(nb)));
          end
        end else
          needsRead = tagged Valid bw;
      end
      tagged Unimplemented: ind = setOpInvalid(ind);
      tagged Invalid:       ind = setOpInvalid(ind);

    endcase

    if (needsRead matches tagged Invalid) begin
      // IF, p.32 class 2, in ONE place for every branch arm in this
      // function: "the branch address of all successful branch
      // operations".  `next` differs from `fallthrough` exactly when a
      // branch was taken, which is what "successful" means here, so
      // this catches BranchInd, BitBranch, the unconditional branches,
      // count-and-branch and SIC's fused branch uniformly rather than
      // repeating the rule in each arm.
      //
      // ONE CASE IT CANNOT SEE, stated rather than left to be found: a
      // branch whose target IS its own fall-through address is
      // indistinguishable from not branching.  Such a branch is a
      // no-op in every other respect too, so the only loss is the
      // alarm it would raise -- and its target is the next instruction,
      // which p.32 class 1 will monitor once class 1 exists.
      if (next != fallthrough) begin
        ind = ifSignal(st, next[18:1], ind);
        // p.32, THE BRANCH-SUPPRESSION CLAUSE: "If the branch address
        // of a successful branch operation is such that control would
        // pass into a protected area, the entire branch operation,
        // INCLUDING ANY COUNTING, BIT CHANGING, OR INDEX ALTERATION,
        // is suppressed."  That enumeration is the specification, and
        // the sentence after it -- "The address boundaries are ignored
        // if the mask bit is zero" -- is what gates it on the mask.
        // (The deck settles that the INDICATOR still sets with the
        // mask at zero; see ifSignal's note.)
        //
        // WHAT IS SUPPRESSED HERE, and what is not, said plainly.
        // Suppressed: the branch itself, and the INDEX ALTERATION --
        // both the shared deferred index write (count-and-branch's
        // count and refill) and VflInt's progressive update.  NOT yet
        // suppressed: BIT CHANGING, because BRANCH ON BIT issues its
        // st.writeWord inside its own arm, before this point.  DS
        // already has that shape solved one arm over (`storeViolates`
        // in the BitBranch case), and doing the same for IF needs the
        // branch-target test moved into that arm.  Stated rather than
        // left as a silent third of the sentence.
        if (maskedOn(st, ind_IF) && ifViolates(st, next[18:1])) begin
          next = fallthrough;
          doIdxWrite = False;
          vflPending = tagged Invalid;
        end
      end
      if (doIdxWrite) st.writeIndex(idxWriteReg, idxWriteVal);
      st.setIndicatorBits(ind);
      return tuple5(next, vflPending, ioStart, tagged Invalid, xmitStart);
    end else begin
      // Bailed out partway through: the arm that set `needsRead` did
      // so before touching any of these, so returning the function-
      // ENTRY values here (not whatever partial computation produced)
      // is correct by construction -- see this function's own header
      // comment.
      return tuple5(pc, tagged Invalid, tagged Invalid, needsRead,
                    tagged Invalid);
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
  Maybe#(XmitXfer) xmitStart;                  // a multi-word TRANSMIT
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
// The held instruction, as a named struct rather than a tuple: EXECUTE
// added a fifth field (the execution-operation context) and a Tuple5 of
// unlabelled positions was already the wrong shape at four.
typedef struct {
  HWordAddr    pc;         // THE EXECUTE'S pc while a subject is held
  InstrLen     len;        // ... and the EXECUTE'S length
  DecodedInstr di;         // the instruction actually being run
  Bool         atIntAddr;  // p.32's interruption-address exemption
  ExSubject    ex;         // notSubject unless `di` is a subject instruction
  // THE INVARIANT, and resume() orders its dispatch on it: `exic` is
  // Valid IF AND ONLY IF `di` is an EXIC whose pseudo-instruction
  // counter has already been read.  It is cleared the moment the
  // subject replaces `di`, so a second-level EXIC starts with its own
  // Invalid and builds its own, and an EX that is the subject of an
  // EXIC is an ordinary EX with `exic` Invalid.
  Maybe#(ExicCtx) exic;
} HeldOp deriving (Bits, Eq, FShow);

interface EBox;
  method ActionValue#(ExecResult)
    exec(HWordAddr pc, InstrLen len, DecodedInstr di,
         Vector#(2, Word64) prefetch, Bit#(2) prefetchCount, Bool atIntAddr);
  method ActionValue#(Maybe#(ExecDone))
    start(HWordAddr pc, InstrLen len, DecodedInstr di,
          Vector#(2, Word64) prefetch, Bit#(2) prefetchCount, ExecOwner owner,
          Bool atIntAddr);
  method Bool busy();                 // holding an instruction that waits on a read
  method Bool busyFor(ExecOwner o);   // ... dispatched by o
  method Bool canResume();            // busy and the read has answered
                                      // (or an EXIC subject is ready to run)
  method Tuple3#(HWordAddr, InstrLen, DecodedInstr) pending();   // the held instruction
  method ActionValue#(Maybe#(ExecDone)) resume();
endinterface

module mkEBox #(StretchStorage st, StretchIO io) (EBox);
  // The held instruction: Invalid when nothing is in flight. prefetch/
  // prefetchCount are the operand words collected so far, so the next
  // run of execute() picks up with one more slot filled (execute()'s
  // header comment has the contract).
  // The flag rides in `held` with the instruction: resume() re-runs
  // execute() for the SAME instruction, so it must answer p.32's
  // interruption-address exemption the same way both times.
  //
  // "THE SAME INSTRUCTION" IS NO LONGER ALWAYS TRUE, and EXECUTE is
  // why.  When the held instruction is an EX, the word that arrives is
  // not an operand but a SUBJECT INSTRUCTION, and resume() REPLACES
  // `di` with it -- keeping `pc` and `len`, which stay the EXECUTE's so
  // that the instruction counter steps past the EXECUTE and nothing
  // else (p.49; execute()'s `fallthrough` comment has the sentence).
  Reg#(Maybe#(HeldOp)) held <- mkReg(tagged Invalid);
  Reg#(Vector#(2, Word64)) prefetch      <- mkReg(replicate(0));
  Reg#(Bit#(2))            prefetchCount <- mkReg(0);
  Reg#(ExecOwner)          owner         <- mkReg(OwnerIbox);

  // THE ONE CLOCK EXECUTE INDIRECT AND COUNT COSTS THAT EXECUTE DOES
  // NOT, and it is forced by the machine model rather than chosen.
  // Printed p.50: "After the subject instruction has been fetched but
  // PRIOR TO ITS EXECUTION, the pseudo-instruction counter is stepped."
  // The step is a storage write; so is much of what a subject
  // instruction does; and an interface method may be called only ONCE
  // per rule, so the two cannot share a clock.  When resume() writes
  // the step it therefore installs the subject and stops, setting this
  // flag; canResume() then lets the instruction unit call resume()
  // again with no read outstanding, and that call runs the subject.
  //
  // THE FLAG IS STICKY, DELIBERATELY: if rl_exec_resume loses the next
  // clock to rl_recover or rl_io, the subject is still there to be run.
  // Nothing else in the machine can observe the extra clock -- `held`
  // stays Valid throughout, so ebox.busy() blocks the interruption arm
  // and the look-ahead arm, and canResume() blocks rl_prepare, exactly
  // as they are blocked while a read is outstanding.
  Reg#(Bool)               subjReady     <- mkReg(False);

  function ExecDone doneOf(ExecResult r) =
    ExecDone { next: tpl_1(r), idxWrite: tpl_2(r), ioStart: tpl_3(r),
               xmitStart: tpl_5(r) };

  method ActionValue#(ExecResult)
      exec(HWordAddr pc, InstrLen len, DecodedInstr di,
           Vector#(2, Word64) pf, Bit#(2) cnt, Bool atIntAddr);
    // The preparation arm's side-effect-free operand-address probe.
    // Never an execution operation: StretchIBox's fetchesOperand (which
    // is what gates this call) answers False for BranchOrMisc, so an EX
    // is dispatched through start() like every other I-box instruction.
    let r <- execute(st, io, pc, len, di, pf, cnt, atIntAddr, notSubject);
    return r;
  endmethod

  method ActionValue#(Maybe#(ExecDone))
      start(HWordAddr pc, InstrLen len, DecodedInstr di,
            Vector#(2, Word64) pf, Bit#(2) cnt, ExecOwner o, Bool atIntAddr);
    // A freshly dispatched instruction is never itself a subject: the
    // instruction unit only ever hands over instructions of the main
    // program.  An EX dispatched here bails immediately for its subject
    // word and becomes the held instruction; resume() takes it from
    // there.
    let r <- execute(st, io, pc, len, di, pf, cnt, atIntAddr, notSubject);
    if (tpl_4(r) matches tagged Valid .a) begin
      st.readWordReq(a);
      held <= tagged Valid HeldOp{pc: pc, len: len, di: di,
                                  atIntAddr: atIntAddr, ex: notSubject,
                                  exic: tagged Invalid};
      prefetch <= pf;
      prefetchCount <= cnt;
      owner <= o;
      return tagged Invalid;
    end else
      return tagged Valid doneOf(r);
  endmethod

  method Bool busy() = isValid(held);
  method Bool busyFor(ExecOwner o) = isValid(held) && owner == o;
  // `subjReady` is the EXIC step's own clock: see its declaration.  It
  // is an alternative to the read handshake, not an addition to it --
  // when it is set there is no outstanding read, because the subject
  // word was consumed on the clock the step was written.
  method Bool canResume() = isValid(held) && (subjReady || st.responseReady());
  method Tuple3#(HWordAddr, InstrLen, DecodedInstr) pending();
    let h = validValue(held);
    // `pc` and `len` are the EXECUTE's while a subject is held, which
    // is exactly what StretchCore's commitNext must see (p.49).  `di`
    // is the instruction actually in flight, which is what the timing
    // budget should be charged against.
    return tuple3(h.pc, h.len, h.di);
  endmethod

  // RESUME HAS FIVE SHAPES NOW, and they are ordered on HeldOp's
  // invariant (`exic` Valid iff `di` is a mid-flight EXIC):
  //
  //   1. `subjReady`        -- no word to collect; an EXIC's subject
  //                            was installed and its pseudo-IC stepped
  //                            on the previous clock.  Run it.
  //   2. `h.exic` Valid     -- the word is an EXIC's SUBJECT.  Decode
  //                            it, STEP THE PSEUDO-IC, install, defer.
  //   3. an EXECUTE held    -- the word is an EX's SUBJECT (the swap
  //                            EX brought in).
  //   4. an EXIC held with  -- the word is the PSEUDO-IC itself; hand
  //      no context yet        it back to the arm in prefetch[0].
  //   5. anything else      -- the word is an ORDINARY OPERAND.
  //
  // ONE execute() CALL SITE, unchanged and non-negotiable: BSV inlines
  // functions, so a second call is a second instantiation of the whole
  // datapath and a second st.writeWord writer in one rule.  For the
  // same reason the step's write and execute()'s own writes are put in
  // the two arms of ONE if/else below, where bsc can see they are
  // exclusive, rather than left to be proved so by analysis.
  method ActionValue#(Maybe#(ExecDone)) resume();
    let h = validValue(held);

    // By default the arrived word is an OPERAND: re-run the same held
    // instruction with one more prefetch slot filled.  This is what
    // every instruction but an execution operation does.
    DecodedInstr       rdi  = h.di;
    ExSubject          rex  = h.ex;
    Maybe#(ExicCtx)    rexic = h.exic;
    Vector#(2, Word64) rpf  = prefetch;
    Bit#(2)            rcnt = prefetchCount;
    // AND THESE TWO ARE NEVER REASSIGNED, which is the point of naming
    // them.  Even when `rdi` below becomes the subject instruction,
    // `rpc`/`rlen` stay the EXECUTE's -- printed p.49: the instruction
    // counter "is never stepped during the execution of any subject
    // instruction even if the subject instruction is again one of the
    // execution instructions."  Assigning the subject's own location
    // here is the one-line bug that makes an execution operation
    // relinquish control, which is what routine 1262 TEST 1A (EX) and
    // TEST 2A (EXIC) are named for; the model programs' "WRONG" traps
    // exist to catch exactly that.
    HWordAddr          rpc  = h.pc;
    InstrLen           rlen = h.len;
    // `defer` = hold for another clock instead of running execute();
    // `more` = ... because a further word has been asked for.
    Bool               defer    = False;
    Bool               more     = False;
    WordAddr           moreAddr = 0;
    // The pseudo-IC step, as data rather than as an Action -- see the
    // header note on the single writeWord site.
    Maybe#(Tuple2#(WordAddr, Word64)) stepWrite = tagged Invalid;

    if (subjReady) begin
      // SHAPE 1.  Nothing arrived and nothing is outstanding: `held`
      // already IS the subject, with an empty prefetch, and the step
      // was written last clock.  Fall straight through to execute().
      subjReady <= False;
    end else begin
      Word64 v <- st.readWordResp();
      Vector#(2, Word64) pf = prefetch;
      pf[prefetchCount] = v;
      Bit#(2) cnt = prefetchCount + 1;
      rpf = pf;
      rcnt = cnt;

      if (h.exic matches tagged Valid .c) begin
        // SHAPE 2.  THE SUBJECT OF AN EXECUTE INDIRECT AND COUNT has
        // arrived (or, when c.haveW0, its second storage word).  `v` is
        // used directly and `pf` is ignored: prefetch[0] still holds the
        // pseudo-IC word, which the EXIC arm reads on every call.
        Word64     w0  = c.haveW0 ? c.w0 : v;
        HalfWord32 hw0 = (c.sa[0] == 0) ? w0[63:32] : w0[31:0];
        InstrLen   slen = instrLen(hw0);
        if (slen == Full && c.sa[0] == 1 && !c.haveW0) begin
          // A FULL-LENGTH SUBJECT STARTING IN A RIGHT HALF-WORD
          // straddles two storage words and needs a second read before
          // it can be decoded at all -- and therefore before its LENGTH
          // can size the step.  (EX met this first; 1262 TEST 1CC's
          // I62B6 is the shape.)
          defer = True; more = True; moreAddr = c.sa[18:1] + 1;
          rexic = tagged Valid ExicCtx{ psAddr: c.psAddr, psWord: c.psWord,
                                        sa: c.sa, haveW0: True, w0: v };
        end else begin
          Maybe#(HalfWord32) hw1 =
            (slen == Half) ? tagged Invalid
                           : tagged Valid ((c.sa[0] == 0) ? w0[31:0] : v[63:32]);
          rdi = decode(hw0, hw1);
          // p.32 class 1 for the subject's location, OR-ed into what
          // earlier levels found -- identical to EX's, and for EXIC the
          // `a >= 32` guard inside ifViolates is p.32's OWN wording
          // rather than a different rule that agrees numerically:
          // "Address monitoring for Instruction Fetch includes: ... 3.
          // The location of the subject instruction of the EXECUTE and
          // EXECUTE INDIRECT AND COUNT operations WHEN THIS LOCATION IS
          // IN MAIN STORAGE."  Addresses 0-31 are the special and index
          // registers, not main storage.  (For EXIC the guard is in any
          // case unreachable: the arm has already raised AD and
          // no-opped anything below 32.  EX needs a different argument
          // for the same guard and its arm gives one.)
          rex = ExSubject { under: True,
                            ifSig: h.ex.ifSig || ifViolates(st, c.sa[18:1]) };
          // The subject starts with an EMPTY prefetch: the words
          // collected so far were the pseudo-IC and the subject-
          // instruction fetch, not the subject's operand.
          rpf = replicate(0);
          rcnt = 0;
          // The level is over: a second-level EXIC builds its own
          // context from its own arm (HeldOp's invariant).
          rexic = tagged Invalid;

          // THE STEP.  Printed p.50, read first-hand at 300 dpi: "After
          // the subject instruction has been fetched but prior to its
          // execution, the pseudo-instruction counter is stepped.  If
          // the subject instruction is half-length, the pseudo-
          // instruction counter is stepped ONCE; if full-length,
          // TWICE."  One step is one HALF-WORD, i.e. +1 in bits 0-18 --
          // which is +32 in an index word's 24-bit value field, because
          // bit 18 carries weight 2^5 there.  That is why routine 1262
          // TEST 2B's four half-length classes check the stepped
          // counter with "V+I,$X2,0.32" and its FULL WD VFL class
          // checks it with "V+I,$X2,1.0".
          //
          // BITS 19-63 ARE PRESERVED, which is why psWord is carried:
          // the manual gives bits 0-18 to the counter and says nothing
          // about the rest, and the deck's own pseudo-IC I62PSI is
          // written "LX,$X0,0" -- an INDEX WORD, whose count and refill
          // fields live down there.
          //
          // p.50 again, on levels: "When EXECUTE INDIRECT AND COUNT is
          // a subject instruction in a multi-leveled execution
          // operation, EACH pseudo-instruction counter involved is
          // appropriately stepped between the fetching and executing of
          // its corresponding subject instruction."  That falls out:
          // each level runs this branch once, with its own ctx.
          HWordAddr step = (slen == Half) ? 1 : 2;
          stepWrite = tagged Valid tuple2(c.psAddr,
                                          { c.sa + step, c.psWord[44:0] });
          defer = True;          // ... and the write costs this clock
          subjReady <= True;     // ... so the subject runs on the next
        end
      end else if (exSubjectAddr(st, h.di) matches tagged Valid .sa) begin
        // SHAPE 3.  THE EX SUBJECT SWAP, Reference Manual printed p.49:
        // "If an execution operation specifies an execution instruction
        // as its subject instruction, the subject instruction of the
        // second-level execution operation is obtained.  If this, in
        // turn, is still another execution instruction, the procedure is
        // carried to succeeding levels until an instruction that is not
        // an execution instruction is obtained."  That is a loop, not a
        // recursion, and this is the loop: the held instruction is
        // replaced, one level per clock, until it is not an EXECUTE.
        // Depth is therefore unbounded in the model, and so is the time
        // -- USA (p.45 indicator 17, "a LOAD VALUE EFFECTIVE, EXECUTE,
        // or EXECUTE INDIRECT AND COUNT operation has been in progress
        // for longer than one millisecond") is NOT implemented, so an
        // execution chain that closes on itself spins here until the
        // harness's step cap rather than being terminated.  Stated
        // rather than left to be discovered.
        //
        // hw0 ALWAYS COMES FROM SLOT 0, never from the word that just
        // arrived: on the second visit below, `v` is the subject's SECOND
        // half-word and pf[0] is still the first.
        HalfWord32 hw0 = (sa[0] == 0) ? pf[0][63:32] : pf[0][31:0];
        InstrLen slen = instrLen(hw0);
        if (slen == Full && sa[0] == 1 && cnt < 2) begin
          // A FULL-LENGTH SUBJECT STARTING IN A RIGHT HALF-WORD straddles
          // two storage words, so it needs a second read.  Not a corner
          // case invented here: routine 1262 TEST 1CC's I62B6 is
          // "BB,$X0+.01,I6238", a full word, at 024205.40 -- and the EX
          // that names it prints octal pair 52, bit 18 = 1.
          defer = True; more = True; moreAddr = sa[18:1] + 1;
        end else begin
          Maybe#(HalfWord32) hw1 =
            (slen == Half) ? tagged Invalid
                           : tagged Valid ((sa[0] == 0) ? pf[0][31:0] : pf[1][63:32]);
          rdi  = decode(hw0, hw1);
          // p.32 class 1 for THIS level's subject location, OR-ed into
          // whatever earlier levels found -- never overwritten, because an
          // intermediate EXECUTE's own subject location is monitored just
          // as much as the last one's and its indicator word was thrown
          // away when it bailed.  ifViolates carries p.50's below-32
          // carve-out; execute()'s own comment says why that is the right
          // predicate and not the same rule.
          rex  = ExSubject { under: True,
                             ifSig: h.ex.ifSig || ifViolates(st, sa[18:1]) };
          // The subject starts with an EMPTY prefetch: the words collected
          // so far were the subject-instruction fetch, not its operand.
          rpf  = replicate(0);
          rcnt = 0;
        end
      end else if (exicPsicAddr(st, h.di) matches tagged Valid .pw) begin
        // SHAPE 4.  THE PSEUDO-INSTRUCTION COUNTER has arrived, for an
        // EXIC that has not got one yet (HeldOp's invariant).  Record
        // what the step will need, and let the EXIC arm re-run with the
        // word in prefetch[0]: it checks "32.00 and greater" and asks
        // for the subject fetch, or raises AD and finishes.
        rexic = tagged Valid ExicCtx{ psAddr: pw, psWord: v, sa: v[63:45],
                                      haveW0: False, w0: 0 };
      end
      // SHAPE 5 -- an ordinary operand -- is the defaults, untouched.
    end

    if (defer) begin
      if (stepWrite matches tagged Valid .t) st.writeWord(tpl_1(t), tpl_2(t));
      if (more) st.readWordReq(moreAddr);
      held <= tagged Valid HeldOp{pc: rpc, len: rlen, di: rdi,
                                  atIntAddr: h.atIntAddr, ex: rex, exic: rexic};
      prefetch <= rpf;
      prefetchCount <= rcnt;
      return tagged Invalid;
    end else begin
      let r <- execute(st, io, rpc, rlen, rdi, rpf, rcnt, h.atIntAddr, rex);
      if (tpl_4(r) matches tagged Valid .a) begin
        st.readWordReq(a);
        // Rewritten rather than left alone: on a subject swap `rdi` and
        // `rex` are new, and on an ordinary operand arrival they are
        // exactly what was already there.
        held <= tagged Valid HeldOp{pc: rpc, len: rlen, di: rdi,
                                    atIntAddr: h.atIntAddr, ex: rex,
                                    exic: rexic};
        prefetch <= rpf;
        prefetchCount <= rcnt;
        return tagged Invalid;
      end else begin
        held <= tagged Invalid;
        return tagged Valid doneOf(r);
      end
    end
  endmethod
endmodule

endpackage
