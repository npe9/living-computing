// HobbitTypes.bsv -- shared types for the ATT92010 Hobbit model.
//
// Everything here is traced to the AT&T 92010 Hobbit Microprocessor
// Programmer's Reference Manual (January 1993), cited by printed page.
//
//   Parcel        a 16-bit instruction parcel                 p. 1-21
//   one-parcel    bit 15 = 0; opcode[4:0] = bits 14:10         Table 1-15 p. 1-22
//   three-parcel  bits 15:14 = 10; opcode[5:0] bits 13:8,
//                 smode bits 7:4, dmode bits 3:0              Table 1-18 p. 1-24
//   five-parcel   bits 15:14 = 11, same field layout          Table 1-20 p. 1-25
//   monadic 3/5   opcode[5:0] = 0, smode bits 7:4, subcode
//                 bits 3:0                                    Table 1-19 p. 1-24
//   stack 1       opcode 0x02, 8-bit offset bits 9:2,
//                 subcode bits 1:0                            Table 1-16 p. 1-22
//   niladic 1     opcode 0x0B, subcode bits 9:0               Table 1-17 p. 1-22
//
// The shared image format (one 32-bit word per line, words in increasing
// address order from 0, parcel at even address = bits 31:16) is the
// repository contract; mkHobbitMem is a 4096-word (16 Kbyte) model of it.

package HobbitTypes;

import Vector::*;
import RegFile::*;

typedef Bit#(16) Parcel;
typedef Bit#(32) Word;

// A reset handshake token (Flute's CPU_StageN_IFC uses Server#(Token,Token)).
typedef Bit#(0) Token;

// Table 3-1 (printed pp. 3-1 to 3-2) plus the four conditional jumps.
typedef enum {
  OP_NONE,
  OP_MOV, OP_ADD, OP_SUB, OP_ADD3, OP_CMPEQ, OP_CMPGT,
  OP_CALL, OP_RETURN, OP_ENTER, OP_CATCH, OP_POPN, OP_NOP,
  OP_JMP, OP_JMPTY, OP_JMPTN, OP_JMPFY, OP_JMPFN
} HobbitOp deriving (Eq, Bits);

typedef enum {
  TR_NONE,
  TR_CPU,           // CPU escape: documented p. 3-14, deliberately not modelled
  TR_UNIMP,         // opcode marked unimp in Tables 1-15..1-20
  TR_BAD_LENGTH,    // bit 15 = 1, bit 14 = 0: no such parcel form (p. 1-21)
  TR_BAD_MODE,      // addressing mode documented but outside this milestone
  TR_RETURN_MODE,   // RETURN with anything but a stack offset (p. 3-40 note)
  TR_ALIGN,         // word operand with a non-word stack offset
  TR_FETCH_MISS     // fetch missed the model's 3 KB prefetch window (p. 1-2)
} TrapReason deriving (Eq, Bits);

// Operand kind after decode.  OK_ABS is also used for a branch's already
// computed target address (PC-relative or absolute, p. 1-27).
typedef enum { OK_NONE, OK_IMM, OK_STACK, OK_ABS } OperandKind deriving (Eq, Bits);

typedef struct {
  OperandKind kind;
  Word        val;   // immediate, signed byte offset, or absolute address
} Operand deriving (Bits);

// A decoded instruction, including the folded branch that the PDU has
// merged into it (PRM section 4.3, printed p. 4-7).
typedef struct {
  Word       pc;
  Bit#(8)    plen;        // parcels: 1, 3 or 5
  HobbitOp   op;
  Operand    src;
  Operand    dst;
  Parcel     insn0;       // first parcel, for the retirement record
  Parcel     insn1;       // second parcel, 0 for a one-parcel instruction
  Bool       fold;        // a one-parcel branch is folded into this op
  HobbitOp   foldOp;      // JMP / JMPTY / JMPTN / JMPFY / JMPFN
  Word       foldPc;      // address of the folded branch instruction
  Parcel     foldInsn0;   // the folded branch's parcel
  Word       foldTarget;  // target taken by the folded branch
  Word       foldAfter;   // PC after the folded branch (not taken)
  TrapReason tr;
} DecodedInstr deriving (Bits);

// HRI -- the Hobbit Retirement Interface, the Hobbit analogue of
// riscv-formal's RVFI: one record per retired instruction, in program
// order.  HRI checking here means retire-trace comparison against an
// independent one-instruction model, not a yosys formal proof.
// A stack-cache write is an architectural write (including the
// accumulator at CSP+4), so mem_we/mem_addr/mem_wdata/mem_wmask name
// the instruction's own destination write, not cache flush/refill.
typedef struct {
  Bool    valid;
  Word    pc;
  Parcel  insn0;
  Parcel  insn1;
  Word    sp_before;
  Word    sp_after;
  Word    msp_before;
  Word    msp_after;
  Bool    mem_we;
  Word    mem_addr;
  Word    mem_wdata;
  Bit#(8) mem_wmask;
  Bool    trap;
  Bit#(32) cyc;          // occupancy in core clocks, measured at retirement
} Hri deriving (Bits);

// A decoded instruction as the fetch-and-decode unit hands it to the
// decoded-instruction store.  Section 4.3 (printed p. 4-7) describes each
// decoded instruction as carrying a *next address* field, and the static
// prediction bit (p. 1-33) makes the not-predicted path available as the
// alternate next address; a folded branch stores its target in the next
// address field (p. 4-7).  Both fields are architectural here: the
// execution unit selects between them, it never recomputes them.
typedef struct {
  DecodedInstr d;
  Word         nextPc;      // predicted next address; folded-branch target
  Word         altNextPc;   // the other path, for a wrong prediction
} DecInstEntry deriving (Bits);

function Word plenBytes(Bit#(8) n) = zeroExtend(n) << 1;

// Static prediction, p. 1-33: the trailing Y/N of JMPT/JMPF is "the
// expected result of the test", Y = taken.  JMPTY and JMPFY predict taken;
// JMPTN and JMPFN predict not taken.
function Bool predictedTaken(HobbitOp op);
  return op == OP_JMPTY || op == OP_JMPFY;
endfunction

// Build the next/alternate-next fields.  For a folded branch the target is
// the next address (p. 4-7) and the fall-through is the alternate.  For an
// unfolded conditional jump the prediction selects the prefetch path.  For
// an unconditional call or jump both fields name the target; a RETURN is
// indirect and the execution unit supplies the value read at CSP+src
// (p. 3-40).
function DecInstEntry mkDecInstEntry(DecodedInstr d);
  Word seqPc = d.pc + plenBytes(d.plen);
  if (d.fold) begin
    Word pred = predictedTaken(d.foldOp) ? d.foldTarget : d.foldAfter;
    Word alt  = predictedTaken(d.foldOp) ? d.foldAfter  : d.foldTarget;
    return DecInstEntry { d: d, nextPc: pred, altNextPc: alt };
  end else if (d.op == OP_JMP || d.op == OP_CALL) begin
    return DecInstEntry { d: d, nextPc: d.src.val, altNextPc: d.src.val };
  end else if (d.op == OP_RETURN) begin
    return DecInstEntry { d: d, nextPc: seqPc, altNextPc: seqPc };
  end else if (d.op == OP_JMPTY || d.op == OP_JMPTN ||
               d.op == OP_JMPFY || d.op == OP_JMPFN) begin
    Word pred = predictedTaken(d.op) ? d.src.val : seqPc;
    Word alt  = predictedTaken(d.op) ? seqPc : d.src.val;
    return DecInstEntry { d: d, nextPc: pred, altNextPc: alt };
  end else
    return DecInstEntry { d: d, nextPc: seqPc, altNextPc: seqPc };
endfunction

// ---------------------------------------------------------------------
// The decoded-instruction cache entry: exactly 192 bits.
//
// Figure 1-1 (printed p. 1-2) prints the decoded instruction cache as
// "32 X 192 bits"; p. 1-1 calls it a "32-entry, direct-mapped, decoded
// instruction cache".  The bit allocation below is the model's packing
// of the printed width.  All 192 bits are allocated: there is no spare
// bit with which to widen a field.
//
//   field        bits   slice
//   pc[31:6]       26   [191:166]  tag; the index is pc[5:1]
//   op              5   [165:161]  HobbitOp
//   plen code       2   [160:159]  1/3/5 -> 0/1/2
//   trap reason     3   [158:156]  TrapReason
//   src kind        2   [155:154]  OperandKind
//   dst kind        2   [153:152]  OperandKind
//   fold            1   [151]      a folded one-parcel branch (p. 4-7)
//   fold op code    3   [150:148]  JMP/JMPTY/JMPTN/JMPFY/JMPFN -> 1..5
//   src value      32   [147:116]
//   dst value      32   [115:84]
//   fold target    32   [83:52]    the folded branch's taken target
//   insn0          16   [51:36]    HRI parcel 0
//   insn1          16   [35:20]    HRI parcel 1
//   fold insn0     16   [19:4]     HRI parcel of the folded branch
//   full            1   [3]        1 = a complete decoded entry
//   reserved        3   [2:0]      zero
//
// The printed p. 1-32 sentence "the PDU assigns a next-PC and
// alternate-next-PC field for each decoded instruction" cannot be
// honoured inside 192 bits: the two fields are 64 bits, and the entry
// already spends 188 on the PC tag, the opcode/mode/flag field, both
// operand values, the folded-branch target and the three parcels the
// HRI record needs.  That 64-bit pair is therefore the documented
// overflow: it is not stored, and the same mkDecInstEntry() function the
// PDU used recomputes it from the stored fields when the entry is read.
// No field is silently widened and no second array is added.
typedef Bit#(192) DecEntry;

function Bit#(2) encPlen(Bit#(8) n);
  return (n == 8'd1) ? 2'd0 : (n == 8'd3) ? 2'd1 : 2'd2;
endfunction

function Bit#(8) decPlen(Bit#(2) c);
  return (c == 2'd0) ? 8'd1 : (c == 2'd1) ? 8'd3 : 8'd5;
endfunction

// The folded branch is one of five opcodes; a 3-bit code keeps the entry
// inside its printed width (the HobbitOp enum itself needs 5 bits).
function Bit#(3) encFoldOp(HobbitOp op);
  case (op)
    OP_JMP:   return 3'd1;
    OP_JMPTY: return 3'd2;
    OP_JMPTN: return 3'd3;
    OP_JMPFY: return 3'd4;
    OP_JMPFN: return 3'd5;
    default:  return 3'd0;
  endcase
endfunction

function HobbitOp decFoldOp(Bit#(3) c);
  case (c)
    3'd1: return OP_JMP;
    3'd2: return OP_JMPTY;
    3'd3: return OP_JMPTN;
    3'd4: return OP_JMPFY;
    3'd5: return OP_JMPFN;
    default: return OP_NONE;
  endcase
endfunction

function DecEntry packDecEntry(DecodedInstr d);
  return { d.pc[31:6],
           pack(d.op),
           encPlen(d.plen),
           pack(d.tr),
           pack(d.src.kind),
           pack(d.dst.kind),
           pack(d.fold),
           encFoldOp(d.foldOp),
           d.src.val,
           d.dst.val,
           d.foldTarget,
           d.insn0,
           d.insn1,
           d.foldInsn0,
           1'b1,
           3'b0 };
endfunction

function Bool decEntryFull(DecEntry e) = (e[3] == 1'b1);

function Word decEntryPc(DecEntry e, Word indexPc);
  return { e[191:166], indexPc[5:1], 1'b0 };
endfunction

function DecodedInstr unpackDecEntry(DecEntry e, Word pc);
  return DecodedInstr {
    pc: pc,
    plen: decPlen(e[160:159]),
    op: unpack(e[165:161]),
    src: Operand { kind: unpack(e[155:154]), val: e[147:116] },
    dst: Operand { kind: unpack(e[153:152]), val: e[115:84] },
    insn0: e[51:36],
    insn1: e[35:20],
    fold: unpack(e[151]),
    foldOp: decFoldOp(e[150:148]),
    foldPc: pc + plenBytes(decPlen(e[160:159])),
    foldInsn0: e[19:4],
    foldTarget: e[83:52],
    foldAfter: pc + plenBytes(decPlen(e[160:159])) + 2,
    tr: unpack(e[158:156])
  };
endfunction

// Read a 192-bit entry back as the EU's decoded instruction, recomputing
// the next/alternate-next pair that does not fit (see the allocation).
function DecInstEntry decEntryToInst(DecEntry e, Word pc) =
  mkDecInstEntry(unpackDecEntry(e, pc));

// Six consecutive parcels, p[0] first, for the decode interface.
function Vector#(6, Parcel) mkParcels(Parcel p0, Parcel p1, Parcel p2,
                                      Parcel p3, Parcel p4, Parcel p5);
  Vector#(6, Parcel) v0 = replicate(0);
  Vector#(6, Parcel) v1 = update(v0, 0, p0);
  Vector#(6, Parcel) v2 = update(v1, 1, p1);
  Vector#(6, Parcel) v3 = update(v2, 2, p2);
  Vector#(6, Parcel) v4 = update(v3, 3, p3);
  Vector#(6, Parcel) v5 = update(v4, 4, p4);
  return update(v5, 5, p5);
endfunction

function Bool isBranchOp(HobbitOp op);
  return op == OP_CALL || op == OP_RETURN || op == OP_JMP ||
         op == OP_JMPTY || op == OP_JMPTN || op == OP_JMPFY || op == OP_JMPFN;
endfunction

// p. 4-7: a one-parcel branch folds into a previous instruction except
// when that instruction is another jump, a one-parcel opcode 00000->00111,
// or a three-parcel monadic.  The non-branching data operations and NOP
// are the foldable class modelled here.
function Bool isFoldable(HobbitOp op);
  return op == OP_MOV || op == OP_ADD || op == OP_SUB ||
         op == OP_ADD3 || op == OP_CMPEQ || op == OP_CMPGT ||
         op == OP_NOP;
endfunction

// Conditional-jump sense, p. 3-28: JMPT(Y/N) jumps iff PSW.F = 1, and
// JMPF(Y/N) jumps iff PSW.F = 0.  The trailing Y/N is only the static
// prediction hint (p. 1-33), never part of the condition.
function Bool branchTaken(HobbitOp op, Bool flag);
  case (op)
    OP_JMPTY: return flag;
    OP_JMPTN: return flag;
    OP_JMPFY: return !flag;
    OP_JMPFN: return !flag;
    default:  return True;
  endcase
endfunction

function String trapText(TrapReason t);
  case (t)
    TR_CPU:         return "CPU escape (p. 3-14) not implemented in this milestone";
    TR_UNIMP:       return "unimplemented opcode (Tables 1-15..1-20)";
    TR_BAD_LENGTH:  return "malformed parcel length prefix (p. 1-21)";
    TR_BAD_MODE:    return "addressing mode outside the modelled subset (Tables 1-21..1-23)";
    TR_RETURN_MODE: return "RETURN requires a stack offset (p. 3-40)";
    TR_ALIGN:       return "misaligned word stack operand (p. 1-27)";
    TR_FETCH_MISS:  return "fetch missed the 3 KB prefetch window (Figure 1-1, p. 1-2)";
    default:        return "none";
  endcase
endfunction

// ---------------------------------------------------------------------
// Chapter 4 timing as code.
//
// Every entry below is the printed value from the January 1993
// Programmer's Reference Manual.  Table numbers are given both ways,
// because the printed captions (Table 4-32..4-36) are the body text's
// Table 4-1..4-5 plus 31 (docs/timing_tables.md section 1).
//
// The A, D and Q memory terms are explicit model parameters.  The manual
// defines them (printed p. 4-2: "A = memory access time for a single word
// access, D = ... double word ..., Q = ... quad word ...") but prints no
// value for any of them.  The values chosen here are
//
//   A_CYC = 1  one 32-bit word per synchronous bus cycle,
//   D_CYC = 2  a double-word transfer is two word beats,
//   Q_CYC = 4  a quad-word transfer is four word beats,
//
// because this model's bus interface moves one 32-bit word per clock and
// the ATT92010 bus is synchronous (p. 1-42).  These are choices, not
// printed numbers, and a different bus implementation may change them.
typedef struct {
  Word a;
  Word d;
  Word q;
} MemCycles deriving (Bits);

function MemCycles defaultMemCycles();
  return MemCycles { a: 1, d: 2, q: 4 };
endfunction

function Word ceilBlocks(Word bytes) = (bytes + 15) >> 4;

// Blocks the ENTER flush loop of printed pp. 3-19/3-20 moves.  A
// stack-offset ENTER sets SP to a new target and then runs
// "MSP -= 16" while MSP is more than 256 bytes above the target; an
// ENTER in any other mode empties the cache, flushing every valid entry
// between the old SP and MSP.  The timing table's E is this count
// (Table 4-36 prints ENTER = 1 + (Q.E), p. 4-5; the manual never states
// E's unit, so the unit is read from the p. 3-19/3-20 loop: one
// 16-byte block per iteration).
function Word enterFlushBlocks(Word sp, Word msp, Word target, Bool stackMode);
  if (stackMode) begin
    if ((msp > target) && ((msp - target) > 256))
      return ceilBlocks(msp - (target + 256));
    else
      return 0;
  end else begin
    if (msp > sp) return ceilBlocks(msp - sp);
    else          return 0;
  end
endfunction

// ENTER's stack-offset target (the decode already sign-extended the
// offset, p. 3-20); otherwise the immediate operand is the target.
function Word enterTarget(DecodedInstr d, Word sp);
  return (d.src.kind == OK_STACK) ? sp + d.src.val : d.src.val;
endfunction

// MSP after an ENTER: unchanged for a stack-offset frame that fits in
// 256 bytes, otherwise capped at target+256 (the p. 3-19/3-20 flush
// bound); a non-stack-offset ENTER empties the cache and sets MSP to the
// new SP (p. 3-20).
function Word enterNewMsp(Word sp, Word msp, Word target, Bool stackMode);
  if (stackMode)
    return ((msp > target) && ((msp - target) > 256)) ? target + 256 : msp;
  else
    return target;
endfunction

// MSP after a CATCH: the target rounded up to whole 16-byte blocks, but
// never beyond SP + SCSIZE (pp. 3-10/3-11).  When the target is already
// at or below MSP the instruction is a no-op.
function Word catchNewMsp(Word sp, Word msp, Word target);
  if ((target > msp) && (msp >= sp) && ((msp - sp) < 256)) begin
    Word limit = sp + 256;
    Word bound = msp + (ceilBlocks(target - msp) << 4);
    return (bound > limit) ? limit : bound;
  end else
    return msp;
endfunction

// p. 3-38/3-40: the low four bits of a POPN/RETURN offset do not exist.
function Word spPlusOff(Word sp, Word off) = sp + (off & 32'hFFFFFFF0);
function Word mspWithSp(Word msp, Word newsp) = (newsp > msp) ? newsp : msp;

typedef struct { Word sp; Word msp; } SpMsp deriving (Bits);

// The architectural SP/MSP after the instruction, computed from its
// operands and the before state.  Both the stack-cache box and the HRI
// record use this one definition, so a one-cycle ENTER/CATCH reports the
// same after values the box installs.
function SpMsp archAfterSpMsp(DecodedInstr d, Word sp, Word msp);
  case (d.op)
    OP_ENTER: begin
      Word t = enterTarget(d, sp);
      return SpMsp { sp: t,
                     msp: enterNewMsp(sp, msp, t,
                                      d.src.kind == OK_STACK) };
    end
    OP_CATCH: begin
      Word t = (d.src.kind == OK_STACK) ? sp + d.src.val : d.src.val;
      return SpMsp { sp: sp, msp: catchNewMsp(sp, msp, t) };
    end
    OP_POPN, OP_RETURN: begin
      Word ns = spPlusOff(sp, d.src.val);
      return SpMsp { sp: ns, msp: mspWithSp(msp, ns) };
    end
    default: return SpMsp { sp: sp, msp: msp };
  endcase
endfunction

// Table 4-35 (printed p. 4-5), conditional jump.  The pipeline supplies
// the jump's own one issue slot; the printed extra depends on the
// distance from the compare, because that distance decides which EU
// stage can see PSW.F:
//
//   jump immediately after compare   resolves in EU_S3 -> 2 squashed slots
//   jump 2 instructions after        resolves in EU_S2 -> 1 squashed slot
//   jump 3 or more after             resolves in EU_S1 -> 0 squashed slots
//
// so the printed totals are 3, 2 and 1.  These bubbles are structural:
// the resolution stage is the stage whose squashed younger instructions
// the jump pays for.
function Bit#(2) condJumpBubbles(Bit#(4) sinceCmp);
  return (sinceCmp == 0) ? 2 : (sinceCmp == 1) ? 1 : 0;
endfunction

// The printed total for an unfolded conditional jump (Table 4-35), kept
// as the table oracle the structural bubbles must reproduce.
function Word condJumpCycles(HobbitOp op, Bool taken, Bit#(4) sinceCmp);
  if (taken == predictedTaken(op))
    return 1;                                   // Table 4-35 p. 4-5
  else
    return 1 + zeroExtend(condJumpBubbles(sinceCmp));
endfunction

// The table-driven cycles BEYOND the EU pipeline's own one issue slot.
// The pipeline produces the base occupancy of 1 for every instruction
// that occupies a slot; this function adds only what the printed Chapter
// 4 tables say on top of it.  `taken` is the actual condition outcome
// (needed only by an unfolded conditional jump); `sinceCmp` is the
// number of instructions issued since the last CMPEQ/CMPGT at this
// instruction's issue (0 = this jump immediately follows the compare).
function Word extraCycles(DecInstEntry e, Word sp, Word msp, MemCycles m,
                          Bool taken, Bit#(4) sinceCmp);
  // Table 4-36 (printed p. 4-5), Unimplemented opcode = 7 + A.  The
  // sequence is the p. 1-39 store *(CSP) = PC, a single word write, so
  // the A term is one word access.  Six of the seven cycles are beyond
  // the trap's own issue slot.
  if (e.d.tr != TR_NONE)
    return 6 + m.a;
  else
    return opExtraCycles(e, sp, msp, m, taken, sinceCmp);
endfunction

function Word opExtraCycles(DecInstEntry e, Word sp, Word msp, MemCycles m,
                            Bool taken, Bit#(4) sinceCmp);
  let d = e.d;
  case (d.op)
    // Table 4-32 (printed p. 4-3), Simple Instruction.  MOV, SUB, ADD3,
    // CMP, NOP, CALL and unfolded JMP are one slot and no extra.
    OP_MOV:   return 0;
    OP_SUB:   return 0;
    OP_ADD3:  return 0;
    OP_CMPEQ: return 0;                         // CMP row, 1 (p. 3-13)
    OP_CMPGT: return 0;                         // CMP row, 1
    OP_NOP:   return 0;
    OP_CALL:  return 0;
    OP_RETURN:return 1;                         // RETURN 2, always indirect
    OP_POPN:  return 1;                         // POPN 2
    OP_JMP:   return 0;                         // JMP unfolded 1; folded
                                                // branches are records with
                                                // cyc = 0 (p. 4-3 note)
    // Table 4-32 (p. 4-3) prices the mnemonic, not the parcel count or
    // the operand mode: ADD is 1 for its one-, three- and five-parcel
    // forms, and the p. 4-1 assumptions admit immediate and stack-offset
    // modes at that price.  ADDI is a different instruction: opcode 0x01,
    // "Add interlocked" (p. 3-6; the 000/001 row of Tables 1-18/1-20).
    // It is not implemented and the decoder traps on it.
    OP_ADD: return 0;
    // Table 4-36 (printed p. 4-5), ENTER = 1 + (Q.E).  The Q.E flush is
    // the ENTER's structural extra: the flush engine really runs for
    // that many clocks and blocks the next issue.
    OP_ENTER: return m.q * enterFlushBlocks(sp, msp,
                                            enterTarget(d, sp),
                                            d.src.kind == OK_STACK);
    // Table 4-36 (printed p. 4-5), CATCH = 1.  The quad-word refill of
    // pp. 3-10/3-11 is a stack-cache fill, not an architectural value,
    // and the p. 4-1 assumptions charge no fetch or operand delay for
    // it; the refill therefore overlaps the following instructions.
    OP_CATCH: return 0;
    OP_JMPTY: return (taken == predictedTaken(d.op))
                        ? 0 : zeroExtend(condJumpBubbles(sinceCmp));
    OP_JMPTN: return (taken == predictedTaken(d.op))
                        ? 0 : zeroExtend(condJumpBubbles(sinceCmp));
    OP_JMPFY: return (taken == predictedTaken(d.op))
                        ? 0 : zeroExtend(condJumpBubbles(sinceCmp));
    OP_JMPFN: return (taken == predictedTaken(d.op))
                        ? 0 : zeroExtend(condJumpBubbles(sinceCmp));
    default:  return 0;
  endcase
endfunction

// The printed total, used by the smoke test's table probes.  The EU
// itself uses extraCycles(): the pipeline's own slot supplies the 1.
function Word instrCycles(DecInstEntry e, Word sp, Word msp, MemCycles m,
                          Bool taken, Bit#(4) sinceCmp);
  return 1 + extraCycles(e, sp, msp, m, taken, sinceCmp);
endfunction

// ---------------------------------------------------------------------
// Memory: 256 32-bit words (1 Kbyte), big-endian parcel split per the
// shared image format.  The smoke program, its data and its stack all
// fit below 0x400.
//
// The interface is one synchronous read port and one write port.  An
// address presented with readReq() returns its word through readData()
// in the next cycle; write() stores one word in the current cycle.  The
// 92010 has no on-chip program RAM: it fetches over the synchronous bus
// (PRM Appendix A, printed p. A-1), so one word per bus cycle with a
// one-cycle latency is the faithful model and the A = 1 choice in
// MemCycles.  The instruction side is served by the prefetch buffer in
// HobbitDecode, not by extra memory ports.
//
// peek() is a verification probe for the testbench only: the machine
// never calls it, so an elaborated board has no second read port.  It
// exists for the smoke checks that read back program results.
// ---------------------------------------------------------------------

interface HobbitMem;
  method Action readReq(Word addr);
  method Word readData();                            // word requested last cycle
  method Action write(Word addr, Word val);
  method Word peek(Word addr);                       // testbench probe only
endinterface

module mkHobbitMem(HobbitMem);
  // One write port and a registered read address, so yosys maps the
  // array to a DP16KD rather than to 8,192 flip-flops plus an 8,192-bit
  // next-state mux (docs/area_analysis.md, "Program memory").  The three
  // writers (image loader, stack-cache flush, EU write) reach the one
  // `upd` call site and are disjoint in time: the image load ends before
  // start(), and the flush and EU writes do not overlap.
  RegFile#(Bit#(8), Word) m <- mkRegFileFull;
  Reg#(Word) raddr <- mkReg(0);
  // mkRegFileFull has no reset value, so Bluesim leaves the array
  // undetermined (0xaa...) until a word is stored, while the model's
  // memory is architecturally zero-filled (tests/golden/README,
  // "Memory").  One written bit per word supplies the zero without a
  // second array port: the one `upd` call site below stays the only
  // writer, exactly as docs/area_analysis.md requires.
  Reg#(Bit#(256)) written <- mkReg(0);

  function Bit#(8) idx(Word a) = truncate(a >> 2);

  function Word readWord(Word a);
    let i = idx(a);
    return (written[i] == 1'b1) ? m.sub(i) : 32'd0;
  endfunction

  // Synchronous read: readReq() registers the address, and readData()
  // returns that word in the next cycle (registered address, combinational
  // array data -- a standard synchronous SRAM interface).  One access per
  // cycle and no read/write rule to schedule against the machine.
  method Action readReq(Word a);
    raddr <= a;
  endmethod

  method Word readData() = readWord(raddr);

  method Action write(Word a, Word v);
    m.upd(idx(a), v);
    written <= written | (256'd1 << idx(a));
  endmethod

  // Testbench probe only; the machine never calls it, so an elaborated
  // board has no second read port (the FPGA build prunes it).
  method Word peek(Word a) = readWord(a);
endmodule

endpackage
