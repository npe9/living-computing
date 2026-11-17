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
  Maybe#(WordAddr) storeAddr2;    // and its second word, when the field crosses
  // >>> DOES THIS INSTRUCTION FINISH WITHOUT READING ANYTHING? <<<
  // The preparation arm's probe used to answer this by RUNNING
  // execute() and seeing whether it asked for a word, which is why
  // execution had to double as a query.  Every cause is a pure
  // condition; they were enumerated by instrumenting each
  // disagreement between the probe and this record and mapping it to
  // its test section (docs/ebox_roadmap.md, "Step 3, scoped").
  //
  // >>> NO TEST DISTINGUISHES THIS FIELD, AND THAT IS MEASURED, NOT
  // SUSPECTED. <<<  A full-suite sweep with it hard-wired to False came
  // back 5633 PASS / 0 FAIL, and the two decks written for its
  // never-otherwise-reached clauses -- decks/vfl_progressive_index0.strap
  // and decks/vfl_decimal_refused.strap -- report IDENTICAL cycle counts
  // with those clauses deleted.  The look-ahead's operand fetch
  // overlaps, so issuing a pointless one costs nothing observable
  // today.
  //
  // IT IS KEPT ANYWAY, for the reason the project exists: the machine
  // would not request an operand for an operation it has already
  // refused, and the target is CYCLE accuracy.  What would pin it is
  // either a count of memory requests the testbench can read, or the
  // look-ahead overlap of roadmap M2 -- at which point a pointless
  // fetch would cost a clock and those two decks' windows would move.
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
      // The five storing VflInt operations: ST, SRD (built 2026-11-16,
      // execute()'s ST arm), M+, M+MG, M+1.
      Bool stores = (v.code == 6'b001101) || (v.code == 6'b101101)
                 || (v.code == 6'b001001)
                 || (v.code == 6'b101001) || (v.code == 6'b101011);
      // (M+/M+1/M+MG crossing a word boundary were refused with OP, so
      // completed without a fetch, until 2026-11-17; they read both words
      // now, as ST does.)
      // The decimal refusal that stood here (vflDecimalBuilt) is gone
      // since 2026-11-16: decimal LFT and DCV were the last two, and
      // execute()'s gate went in the same change.
      // The length as the second index leaves it (vflSecondIndex,
      // RefMan printed p.21), as execute() sees it.
      Bit#(7) len_ = effLength(vflSecondIndex(st, v.a).length);
      Bool done = (prog && v.a.i1 == 0)                  // progressive, no index
               || dfSuppresses(st, w)                    // DF, mask-dependent
               || !installed(w);                         // AD
      return PreparedExec {
        operandAddr: (v.a.p == 4) ? tagged Invalid : tagged Valid w,
        storeAddr:   stores       ? tagged Valid w : tagged Invalid,
        storeAddr2:  (stores && fieldCrosses(ea, len_)) ? tagged Valid (w + 1)
                                                        : tagged Invalid,
        completesWithoutFetch: done };
    end
    tagged Connective .c: begin
      Bool prog = (c.a.p != 0 && c.a.p != 4);
      BitAddr ea = prog ? st.readIndex(c.a.i1).addr
                        : effAddr24(st, c.a.addr, c.a.i1);
      WordAddr w = ea[23:6];
      Bit#(7) len_ = effLength(vflSecondIndex(st, c.a).length);
      // (CM crossing into a register word was refused with OP until
      // 2026-11-17 and completed without a fetch; it reads both words now.)
      Bool done = (prog && c.a.i1 == 0)
               || dfSuppresses(st, w)
               || !installed(w);
      return PreparedExec {
        operandAddr: (c.a.p == 4) ? tagged Invalid : tagged Valid w,
        // C and CT are excluded: C writes the accumulator and CT writes
        // nothing, so neither is a store.  See storeTarget's note on
        // how CM's absence here was found.
        storeAddr: (c.suffix == conn_CM) ? tagged Valid w : tagged Invalid,
        storeAddr2: (c.suffix == conn_CM && fieldCrosses(ea, len_)) ? tagged Valid (w + 1)
                                                                    : tagged Invalid,
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
        storeAddr2:  tagged Invalid,
        completesWithoutFetch: dfSuppresses(st, w) || !installed(w) };
    end
    default: return PreparedExec { operandAddr: tagged Invalid,
                                   storeAddr:   tagged Invalid,
                                   storeAddr2:  tagged Invalid,
                                   completesWithoutFetch: False };
  endcase
endfunction

// >>> THE I-BOX'S INDEXING, DONE ONCE AND CARRIED IN THE LEVEL. <<<
// (2026-11-15; the type and its source are at LaCarry, StretchTypes.)
//
// `carryIndex` reads the index registers -- the ONLY read of them made
// on behalf of a look-ahead level, except a progressive instruction's
// own register (below).  `carriedInstr` is pure: it substitutes what
// was carried and clears the index fields, so execute()'s effAddr24 /
// effAddr18 / vflSecondIndex all take their `index 0` early return and
// the E-box re-indexes nothing.  rl_prepare derives `da` and
// `storeAddr` from the carried instruction too (prepareExec above), so
// the address a level waits on and the address it executes at are one
// derivation and cannot disagree.
//
// `p` HAS THREE STATES HERE AS EVERYWHERE (see prepareExec):
//
//   p == 0  ordinary.  The effective address replaces the address
//           field and i1 is cleared.
//   p == 4  IMMEDIATE.  The address field is the operand
//           (execute()'s immediateOperand reads vi.a.addr / cn.a.addr,
//           never `ea`), and this model does not index it, so it is
//           carried unchanged and i1 is left alone: `ea` is dead in
//           both VFL arms when immediate, whatever i1 says.
//   else    PROGRESSIVE.  The address field is the INCREMENT and i1
//           names the register execute() reads AND writes in two parts
//           (Ref. Manual printed p.21).  Both are left alone: that
//           register is held still by progressiveWrites (no I-box
//           instruction touches it) and progressivePending (no level
//           is loaded behind it), so the live read is the load-time
//           value.
//
// THE SECOND INDEX IS CARRIED FOR ALL THREE, progressive included:
// p.21 has it modify length, byte size and offset, "the value of the
// index register before modification" when both halves name one
// register, and nothing but this holds a progressive level's i2 still.
function LaCarry carryIndex(StretchStorage st, DecodedInstr d);
  case (d) matches
    tagged VflInt .v: begin
      VflAddr b = vflSecondIndex(st, v.a);
      return LaCarry { addr: (v.a.p == 0) ? effAddr24(st, v.a.addr, v.a.i1) : v.a.addr,
                       lbo:  {b.length, b.bs, b.offset} };
    end
    tagged Connective .c: begin
      VflAddr b = vflSecondIndex(st, c.a);
      return LaCarry { addr: (c.a.p == 0) ? effAddr24(st, c.a.addr, c.a.i1) : c.a.addr,
                       lbo:  {b.length, b.bs, b.offset} };
    end
    tagged Fp .f: return LaCarry { addr: {effAddr18(st, f.addr, f.idx), 6'b0}, lbo: 0 };
    default:      return LaCarry { addr: 0, lbo: 0 };
  endcase
endfunction

function VflAddr carriedVflAddr(VflAddr a, LaCarry c);
  VflAddr b = a;
  b.addr   = c.addr;
  if (a.p == 0) b.i1 = 0;
  b.length = c.lbo[15:10];
  b.bs     = c.lbo[9:7];
  b.offset = c.lbo[6:0];
  b.i2     = 0;
  return b;
endfunction

function DecodedInstr carriedInstr(DecodedInstr d, LaCarry c);
  case (d) matches
    tagged VflInt .v:
      return tagged VflInt VflInstr { a: carriedVflAddr(v.a, c), m: v.m, code: v.code };
    tagged Connective .cn:
      return tagged Connective ConnInstr { a: carriedVflAddr(cn.a, c), conn: cn.conn, suffix: cn.suffix };
    tagged Fp .f:
      return tagged Fp { addr: c.addr[23:6], unnorm: f.unnorm, absSign: f.absSign,
                         invSign: f.invSign, code: f.code, idx: 0 };
    default: return d;
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

// >>> AN INDEX REGISTER A PENDING PROGRESSIVE LEVEL WILL WRITE, 2026-11-08. <<<
// Reference Manual printed p.21: progressive indexing "is executed in two
// parts", and the second writes the index register back.  Nothing stopped
// an I-box instruction running ahead of that write and reading the old
// value.  Found by the 7030 SMAC (decks/smac7030_shell.strap): in
// "ST(BU,64)(V+I),1.0($3)", "KVI,$3,LIMIT", "BXL,LOOP" the compare saw the
// value before the store's, so the loop copied one word too many.  The
// program is sequential on paper and must be so here.  Test:
// decks/index_after_progressive.strap.
function Bool progressiveWrites(Vector#(4, LaLevel) lv, Bit#(4) j);
  Bool r = False;
  for (Integer k = 0; k < 4; k = k + 1)
    if (lv[k].valid) begin
      case (lv[k].di) matches
        tagged VflInt .v: if (v.a.p != 0 && v.a.p != 4 && v.a.i1 == j) r = True;
        tagged Connective .c: if (c.a.p != 0 && c.a.p != 4 && c.a.i1 == j) r = True;
        default: r = r;
      endcase
    end
  return r;
endfunction

// Is any pending level progressive (so will set the index indicators)?
function Bool anyProgressive(Vector#(4, LaLevel) lv);
  Bool r = False;
  for (Integer k = 0; k < 4; k = k + 1)
    if (lv[k].valid && hasProgressive(lv[k].di)) r = True;
  return r;
endfunction

// The same, for an operand addressed as storage: index registers are words
// 16-31 (jb_ax4b p.58: "R,$X15" assembles to address 037, word 31).
function Bool progressiveWord(Vector#(4, LaLevel) lv, WordAddr w);
  return (w >> 4) == 1 && progressiveWrites(lv, w[3:0]);
endfunction

// >>> NO INDEX WAIT FOR A LEVEL; A STORE WAIT FOR AN INDEX STORE. <<<
// (2026-11-15/16.)  A look-ahead level's operand and store addresses
// (`da`, `storeAddr`) are derived at LOAD time, and the store-close-to-
// fetch waits and levelHolds above compare against them.  The E-box used
// to re-derive the effective address from the CURRENT index registers
// when the level was dispatched, and nothing kept the two in step: an
// I-box instruction writing the register ran ahead of the level and
// moved its operand.  Found by the 7030 STRAP II MAIN test's driver
// (step 4b-i): "ST(BU,64),9.0($9)" loaded as a level with da = word
// 0x42f, then "V+I,$9,11.0" ran ahead of it, and the store landed at
// 0x43a, the NEXT record's word.
//
// THE FIRST FIX WAS A STALL (commit 3204601, levelIndexedBy in
// iboxHazard): an index write waited while a pending level was indexed
// by that register.  IT IS GONE.  The level now carries the I-box's
// indexing (carryIndex / carriedInstr above; LaCarry in StretchTypes)
// and the E-box indexes nothing, which is the machine's arrangement: a
// level has no address or index field (Buchholz §15.3, printed
// pp.238-240; R23-9732 Fig. 3.2.2, PDF 93), and the I unit forms the
// effective address in its MOD Z sequencers before the level-load steps
// send it to memory (R23-9732 Figs 3.1.10, 3.1.15, 3.1.20, PDF 72, 79,
// 84).  So an I-box index write behind a level runs without waiting.
//
// >>> THE STORE WAIT. <<<  What remains is the other direction: a level
// that STORES into an index register (or the indicator or mask word).
// R23-9732, I UNIT FLOW DIAGRAMS, draws it at the store step of
// preparation, on the store's OWN address and nothing else: Fig. 3.1.20
// (PDF 84), "ZOAR EQ 11 + 12 + 16 - 31" -> "TON STORE WAIT TGR",
// "TON I RCY REQ TGR"; the same hexagon in Fig. 3.1.13 sheet 3 (PDF 77)
// for the right half-word floating store, and for VFL, Fig. 3.1.24
// (PDF 88), "W EQ 11 + 12 + 16 - 31" -> "VFL CL 2 . VFL 5E" ->
// "VFL 5 CL 2 COND STORE WAIT".  No box compares it with a later
// instruction's index field.  So `storeWait` is True while ANY pending
// level stores into word 11, 12 or 16-31, and rl_prepare then prepares
// nothing -- no I-box instruction, no new level -- until that level has
// retired.
//
// THREE THINGS ARE NOT ON THOSE PAGES AND ARE THE MODEL'S CHOICE: what
// STORE WAIT blocks (here, all preparation; the pages draw only its
// turn-on, and no box takes it as a condition), what releases it (here,
// the storing level's retirement, when its value is in the register),
// and how long the "I RCY" recovery takes (not charged).  A conservative
// wait, not a measured time.  (All three figures read in the page
// images: PDF 77, printed 1-27/1-28; PDF 84, 1-41/1-42; PDF 88,
// 1-49/1-50.)
//
// It replaces two narrower things.  `indexStorePending` (a new level
// indexed by j waited for a level storing word 16+j) is subsumed.  And it
// closes a hole neither stall covered: an I-box instruction on register j
// did not wait for a pending level storing word 16+j, so "ST(BU,64),$X3"
// then "V+I,$3,1.0" read the old $3 (decks/index_after_index_store.strap).
//
// A field crossing INTO word 11, 12 or 16-31 (from word 10 or 15) was
// refused (OP) by execute() until 2026-11-17, so `storeAddr`, the first
// word, was enough.  That refusal is lifted (a tail below word 32 is
// written by rl_tail_write), so the SECOND word is tested too
// (`storeAddr2`, Valid only for a crossing store).  CHOSEN: Fig. 3.1.24's
// hexagon tests "W", the word address; the pages do not draw a crossing
// store's second word, and the model stalls for it rather than let a
// younger instruction read the register before the store's tail lands.
function Bool storeWaitWord(WordAddr w) = (w == 11 || w == 12 || (w >= 16 && w <= 31));

function Bool storeWait(Vector#(4, LaLevel) lv);
  Bool r = False;
  for (Integer k = 0; k < 4; k = k + 1) begin
    if (lv[k].valid &&& lv[k].storeAddr matches tagged Valid .sa &&& storeWaitWord(sa))
      r = True;
    if (lv[k].valid &&& lv[k].storeAddr2 matches tagged Valid .sb &&& storeWaitWord(sb))
      r = True;
  end
  return r;
endfunction

function Bool iboxHazard(StretchStorage st, Bool guessPending, DecodedInstr d, Vector#(4, LaLevel) lv);
  Bool pending = False;
  for (Integer k = 0; k < 4; k = k + 1) if (lv[k].valid) pending = True;
  Bool h = True;   // anything not listed (Transmit, I/O, EX...): drain first
  case (d) matches
    tagged DirIndex .x: begin
      HWordAddr ea = effAddr19(st, x.addr, x.idx);
      Bool refillWord = (x.code == dixop_V_PLUS_CR) && levelHolds(lv, zeroExtend(st.readIndex(x.j).refill)); // V+CR
      // >>> AND AN E-BOX REGISTER OPERAND WAITS FOR THE LEVELS,
      // 2026-11-06, READ OR STORE. <<<  A pending level does not name
      // the accumulator, factor or indicator words it will WRITE (its
      // storeAddr is a storage word, and L/+/LFT have none), so
      // levelHolds cannot see "LV,$0,$L" reading the accumulator a
      // VFL L ahead of it has not loaded yet.  MCP printed p.141 line
      // 50 / p.142 line 1 are exactly that: "L(BU,4),0.0($2),-19"
      // then "LV,$0,$L" -- the tentacle's length, 5.  The model let the
      // LV run first, read the previous accumulator (33.0), and the
      // copy loop on lines 11-13 ran 66 half-words over YXCOMD and
      // JCFIX (printed p.295).  Z and SIC already hold on
      // eboxRegister; the direct-index operations (LV/LX/LC/LR,
      // their stores, V+ ...) now do too.
      h = levelHolds(lv, ea[18:1]) || refillWord || eboxRegister(ea[18:1])
          || progressiveWrites(lv, x.j) || progressiveWrites(lv, x.idx)
          || progressiveWord(lv, ea[18:1])
          // RNX (2026-11-16) stores at X0's OLD refill and writes X0 and
          // XJ: three places the levels might name.  Drain first, as
          // for EX -- the old name is a refill field, not the operand.
          || x.code == dixop_RNX;
    end
    tagged ImmIndex .x:
      h = ((x.code == 4'b0111 || x.code == 4'b1111)                         // V+ICR / V-ICR
           && levelHolds(lv, zeroExtend(st.readIndex(x.j).refill)))
          || progressiveWrites(lv, x.j);
    tagged CountBranch .x:
      h = ((x.refill == 1) && levelHolds(lv, zeroExtend(st.readIndex(x.j).refill)))
          || progressiveWrites(lv, x.j) || (x.idx == 1 && progressiveWrites(lv, 1));
    // >>> AN INDEX-INDICATOR BRANCH WAITS FOR A PENDING PROGRESSIVE
    // LEVEL, 2026-11-16. <<<  Progressive indexing's second part sets the
    // index result indicators (XF, XCZ, XVLZ, XVZ, XVGZ: execute()'s
    // setIndexResultIndicatorsF(ind, vflPx1), "per p.21"), and it does so
    // when the LEVEL executes, not when it is loaded.  So an index-
    // indicator branch is not I-box-local while such a level is pending:
    // "ST(BU,20)(V+IC),0.20($1)" then "BZXCZ,PACK" read XCZ before the
    // store had counted, fell through after four of sixteen fields and
    // halted (C22-6578 Problem 2.6 Method 3's PACK loops, exposed when the
    // VFL E-box times became per-operation; decks/vfl_pack_cross.strap).
    tagged BranchInd .x: h = !indexIndicator(x.indNum) || (x.idx == 1 && progressiveWrites(lv, 1))
                             || anyProgressive(lv);
    tagged BranchOrMisc .x: begin
      // Unconditional branches drain the levels first: a halt (a
      // branch to itself) must not be reported while E-box work is
      // still in the look-ahead, and on the real machine a taken
      // branch empties the look-ahead anyway (Perf. Char. p.3-18:
      // "BD ... empty the LA completely"). NOP is free.
      if (!x.misc) h = (x.code != 3'b110);
      else if (x.code == 3'b100) begin                                       // Z
        WordAddr zw = baWord(effAddr24(st, {x.addr, 5'b0}, x.idx));
        h = levelHolds(lv, zw) || eboxRegister(zw) || progressiveWrites(lv, x.idx)
            || progressiveWord(lv, zw);
      end
      else if (x.code == 3'b000 || x.code == 3'b001) begin                   // R / RCZ
        // The operand is the index word AT THE EFFECTIVE ADDRESS (Ref.
        // Manual p.26; the R arm in StretchExecute.bsv), and x.idx only
        // modifies that address.  This test used to read x.idx's refill
        // field, so a store to the real refill word could be overtaken.
        // Fixed 2026-11-08.  An operand that is a storage word has a
        // refill field not visible here without a fetch: drain.
        WordAddr rw = baWord(effAddr24(st, {x.addr, 5'b0}, x.idx));
        h = (rw >> 4) != 1 || levelHolds(lv, rw)
            || levelHolds(lv, zeroExtend(st.readIndex(rw[3:0]).refill))
            || progressiveWrites(lv, x.idx) || progressiveWord(lv, rw);
      end
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
      h = levelHolds(lv, ea[23:6]) || eboxRegister(ea[23:6]) || progressiveWrites(lv, x.idx)
          || progressiveWord(lv, ea[23:6])
          || iboxHazard(st, guessPending, decodeHalfWord(x.inner), lv);
    end
    default: h = True;
  endcase
  // >>> AND AN INDEX INSTRUCTION DOES NOT OVERTAKE ONE, 2026-11-16. <<<
  // The same indicators, the other way round: the index-arithmetic,
  // load/store-index and count-branch instructions all end in
  // setIndexResultIndicatorsF (execute(), "per p.23"), so one that runs
  // ahead of a pending progressive level has its XCZ overwritten when
  // the level executes.  C22-6578 Problem 4.7 Method 2 as printed:
  // "C0111(BU,8,1)(V+ICR),0.64($1),7($3)", "V-ICR,$3,1", "BZXCZ,DIAG1"
  // -- the branch must see $3's count, and saw $1's.
  Bool setsIndexInd = False;
  case (d) matches
    tagged DirIndex .*: setsIndexInd = True;
    tagged ImmIndex .*: setsIndexInd = True;
    tagged CountBranch .*: setsIndexInd = True;
    default: setsIndexInd = False;
  endcase
  if (setsIndexInd && anyProgressive(lv)) h = True;
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
