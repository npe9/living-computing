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
// The data operations and their `[3]` accumulator forms are one entry each,
// exactly as Table 3-1 prints them; the dyadic grid of Tables 1-18/1-20
// (pp. 1-24, 1-25) supplies the opcodes.
typedef enum {
  OP_NONE,
  // --- dyadic data operations, destination form and `[3]` form --------
  OP_MOV,
  OP_ADD, OP_ADD3, OP_SUB, OP_SUB3,
  OP_AND, OP_AND3, OP_OR, OP_OR3, OP_XOR, OP_XOR3,
  OP_CMPEQ, OP_CMPGT, OP_CMPHI,
  OP_SHL, OP_SHL3, OP_SHR, OP_SHR3, OP_USHR, OP_USHR3,
  OP_MUL, OP_MUL3, OP_DIV, OP_DIV3, OP_REM, OP_REM3,
  OP_UDIV, OP_UREM,
  OP_TADD, OP_TSUB,
  OP_MOVA, OP_LDRAA,
  // --- stack class, niladic and kernel call ---------------------------
  OP_ENTER, OP_CATCH, OP_POPN, OP_RETURN, OP_NOP, OP_KCALL,
  // --- control flow ---------------------------------------------------
  OP_CALL, OP_JMP, OP_JMPTY, OP_JMPTN, OP_JMPFY, OP_JMPFN,
  // --- DQM with a constant source: two or four words (p. 3-18) ---------
  OP_DQM2, OP_DQM4,
  // --- the privileged machine (mkHobbitCoreSystem only) ----------------
  // CRET (niladic 0x005, p. 3-15) and KRET (niladic 0x001, p. 3-30)
  // return through the interrupt-stack frame; FLUSHPTE (monadic 0xB,
  // p. 3-27) drops the TLB/NPSR entry of its effective address; FLUSH
  // is FLUSHI and FLUSHP (niladic 0x003/0x004, pp. 3-24, 3-25), which
  // empty the decoded-instruction store and the prefetch buffer.
  OP_CRET, OP_KRET, OP_FLUSHPTE, OP_FLUSH,
  // The interlocked read-modify-writes, opcodes 0x01/0x02/0x03 (ORI, ANDI,
  // ADDI; pp. 3-37, 3-8, 3-6): dst = dst OP src, and the destination's
  // previous value goes to the accumulator -- two architectural writes.
  OP_ORI, OP_ANDI, OP_ADDI
} HobbitOp deriving (Eq, Bits);

// DQM (p. 3-18) moves two or four contiguous words; "if the source mode
// is 0xF, the constant is replicated either two or four times".  The two
// ops are the two sizes; the source may be the constant or a word mode
// (HobbitDecode.bsv, `dqm`).
function Bool isDqmOp(HobbitOp op) = (op == OP_DQM2) || (op == OP_DQM4);
function Word dqmBytes(HobbitOp op) = (op == OP_DQM4) ? 16 : 8;

typedef enum {
  TR_NONE,
  TR_CPU,           // CPU escape: documented p. 3-14, deliberately not modelled
  TR_UNIMP,         // opcode marked unimp in Tables 1-15..1-20
  TR_BAD_LENGTH,    // bit 15 = 1, bit 14 = 0: no such parcel form (p. 1-21)
  TR_BAD_MODE,      // addressing mode documented but outside this milestone
  TR_RETURN_MODE,   // RETURN with anything but a stack offset (p. 3-40 note)
  TR_ALIGN,         // word operand with a non-word stack offset
  TR_FETCH_MISS,    // fetch missed the prefetch buffer.  No longer produced:
                    // a miss starts a demand fill (HobbitDecode.bsv).  A
                    // runaway PC therefore fetches whatever is there
                    // instead of stopping here; the harnesses stop it by
                    // their PC limit or their clock limit.
  TR_FETCH_FAULT,   // MMU fetch translation fault (Table 1-26 0x7, p. 1-38)
  TR_UNIMP_REG      // CPU escape naming control register 0 or 13..15:
                    // exception 6 (Table 1-24 p. 1-26, p. 1-27)
} TrapReason deriving (Eq, Bits);

// Operand addressing mode after decode: the four-bit code of Table 1-21
// (printed p. 1-25), carried through unchanged so the decoder states the
// printed encoding and the execution unit applies the printed width rule.
//
//   0x0 *$addr:B   0x1 *$addr:UB  0x2 *$addr:H   0x3 *$addr:UH
//   0x4 Roffset:B  0x5 Roffset:UB 0x6 Roffset:H  0x7 Roffset:UH
//   0x8 *Roffset:B 0x9 *Roffset:UB 0xA *Roffset:H 0xB *Roffset:UH
//   0xC *$addr:W   0xD Roffset:W  0xE *Roffset:W  0xF $data
//
// A branch operand (Table 1-23, p. 1-26) is already resolved to its target
// address and carries 0xF; RETURN and POPN carry 0xD because their operand
// is a word stack offset (p. 3-38, p. 3-40).
typedef Bit#(4) OpMode;

typedef struct {
  OpMode mode;
  Word   val;   // immediate, sign-extended field, or effective address
} Operand deriving (Bits);

// Table 1-21 classes (printed p. 1-25).
function Bool modeIsImm(OpMode m) = (m == 4'hF);
function Bool modeIsStack(OpMode m) =
  ((m >= 4'h4) && (m <= 4'h7)) || (m == 4'hD);
function Bool modeIsIndirect(OpMode m) =
  ((m >= 4'h8) && (m <= 4'hB)) || (m == 4'hE);
function Bool modeIsAbs(OpMode m) = (m <= 4'h3) || (m == 4'hC);
function Bool modeIsMem(OpMode m) = (m != 4'hF);

// Width rule, p. 1-3/p. 1-28: byte modes 0/1, 4/5, 8/9; half-word modes
// 2/3, 6/7, A/B; word modes C/D/E; F is the immediate.
function Word modeSize(OpMode m);
  if ((m == 4'h0) || (m == 4'h1) || (m == 4'h4) || (m == 4'h5) ||
      (m == 4'h8) || (m == 4'h9)) return 1;
  else if ((m == 4'h2) || (m == 4'h3) || (m == 4'h6) || (m == 4'h7) ||
           (m == 4'hA) || (m == 4'hB)) return 2;
  else return 4;
endfunction

// Signed and unsigned byte/half-word modes (Table 1-21's B/UB/H/UH, p. 1-25).
function Bool modeSigned(OpMode m) =
  (m == 4'h0) || (m == 4'h2) || (m == 4'h4) || (m == 4'h6) ||
  (m == 4'h8) || (m == 4'hA) || (m == 4'hC) || (m == 4'hD) ||
  (m == 4'hE) || (m == 4'hF);

// The numbering of bytes within data words is selectable (p. 1-3): "The
// User mode is set via the program status word (PSW) UL-bit ... The
// Kernel mode is set via the configuration register (CONFIG) KL-bit."
// PSW bit 10 is the execution level (1 = user), bit 15 is UL; `kl` is
// CONFIG bit 16 (Table 1-2, p. 1-10).  Text is always big-endian (p. 1-4
// note): nothing in the fetch path takes this flag.
function Bool dataLittle(Word psw, Bool kl) =
  (psw[10] == 1'b1) ? (psw[15] == 1'b1) : kl;

// Byte lane for a byte address.  Big-endian (Figure 1-2, p. 1-4): the
// byte at the word address is bits 31:24, so lane 3 - addr[1:0].
// Little-endian (Figure 1-3): it is bits 7:0, so lane addr[1:0].
function Bit#(2) byteLane(Word addr, Bool little) =
  little ? truncate(addr) : truncate(~addr);

// True when a half-word at `addr` is the word's upper half (bits 31:16).
function Bool halfHigh(Word addr, Bool little) =
  little ? (addr[1] == 1'b1) : (addr[1] == 1'b0);

// Byte marks for a store of `size` bytes at `addr`, by lane: bit 3 is
// bits 31:24 and bit 0 is bits 7:0 (the HRI mask convention).
function Bit#(8) storeMask(Word addr, Word size, Bool little);
  if (size == 4) return 8'h0F;
  else if (size == 2) return (halfHigh(addr, little) ? 8'h0C : 8'h03);
  else return (8'd1 << byteLane(addr, little));
endfunction

// Sign- or zero-extend a loaded byte/half-word (p. 1-3, p. 1-28).
function Word extendLoad(Word word, Word addr, Word size, Bool sgn,
                         Bool little);
  if (size == 4) return word;
  else if (size == 2) begin
    Word v = (halfHigh(addr, little) ? (word >> 16) : word) & 32'h0000FFFF;
    return (sgn && (v[15] == 1'b1)) ? (v | 32'hFFFF0000) : v;
  end else begin
    Bit#(2) lane = byteLane(addr, little);
    Word v = (word >> ({30'd0, lane} << 3)) & 32'h000000FF;
    return (sgn && (v[7] == 1'b1)) ? (v | 32'hFFFFFF00) : v;
  end
endfunction

// Place a stored value in its byte lanes, other lanes zero: the HRI record's
// `data` field (sem/README.md's fixed mask convention, p. 1-4).
function Word laneData(Word value, Word addr, Word size, Bool little);
  if (size == 4) return value;
  else if (size == 2) return (halfHigh(addr, little)
                                ? ((value & 32'hFFFF) << 16)
                                : (value & 32'hFFFF));
  else return ((value & 32'hFF) << ({30'd0, byteLane(addr, little)} << 3));
endfunction

// Merge the addressed bytes of `value` into `old` (read-modify-write of the
// surrounding word).  `storeMask` is the byte-mark set.
function Word mergeStore(Word old, Word value, Word addr, Word size,
                         Bool little);
  let laneBits = laneData(value, addr, size, little);
  let m = storeMask(addr, size, little);
  Word expanded = 0;
  for (Integer i = 0; i < 4; i = i + 1)
    if ((m[i] == 1'b1)) expanded = expanded | (32'hFF << (8 * i));
  return (old & ~expanded) | (laneBits & expanded);
endfunction

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
  // The instruction follows a CPU escape (niladic 0x000, p. 3-14): "The
  // instruction following CPU is considered part of the CPU
  // instruction", so the two are one decoded instruction, `pc` is the
  // CPU parcel's, `plen` counts it (4 or 6), insn0 is 0x2C00 and insn1
  // the following instruction's first parcel (the reference model's
  // record), and an operand of mode 7 names the control register
  // `val[3:0]` (Table 1-22/1-24, p. 1-26) instead of a stack half-word.
  Bool       cpu;
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
// The direction the prefetch follows.  An unconditional JMP is always
// taken, so its "prediction" is taken too: until 2026-11-20 it was not in
// this list, a *folded* JMP was therefore prefetched down its
// fall-through, "mispredicted" every time, squashed, and charged Table
// 4-35's 3 where p. 4-3's note gives a folded JMP 0.  The values were
// right and the cycles were not (3,808 of za's 125,572 records; golden
// 020).  Every other use of this function is guarded by isCondJumpOp.
function Bool predictedTaken(HobbitOp op);
  return op == OP_JMPTY || op == OP_JMPFY || op == OP_JMP;
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
  end else if ((d.op == OP_JMP || d.op == OP_CALL) &&
               (d.src.mode == 4'hF)) begin
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
//   reserved        3   [191:189]  zero
//   pc[31:6]       26   [188:163]  tag; the index is pc[5:1]
//   op              6   [162:157]  HobbitOp
//   plen code       2   [156:155]  1/3/5 -> 0/1/2
//   trap reason     4   [154:151]  TrapReason
//   src mode        4   [150:147]  Table 1-21 mode, p. 1-25
//   dst mode        4   [146:143]  Table 1-21 mode
//   fold op code    3   [142:140]  JMP/JMPTY/JMPTN/JMPFY/JMPFN -> 1..5, 0 = none
//   src value      32   [139:108]
//   dst value      32   [107:76]
//   insn0          16   [75:60]    HRI parcel 0
//   insn1          16   [59:44]    HRI parcel 1
//   fold insn0     16   [43:28]    HRI parcel of the folded branch
//   full            1   [27]       1 = a complete decoded entry
//
// Two fields the entry does not store are recomputed exactly, not
// approximated:
//
//   * the folded branch's taken target, because it is the same
//     pcrel10() the decoder applied to the stored fold parcel:
//     foldPc + signExtend(foldInsn0[9:0]) << 1 (p. 1-22, p. 1-27);
//   * the next-PC / alternate-next-PC pair of p. 1-32, by the same
//     mkDecInstEntry() function the PDU used, as before.
//
// 162 bits of the printed 192 are used; the rest is zero.
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

// Bit 191 (one of the three reserved bits) is the CPU-escape flag; the
// plen code then counts the instruction after the escape, and the escape's
// one parcel is added back on unpack.
function DecEntry packDecEntry(DecodedInstr d);
  Bit#(8) basePlen = d.cpu ? d.plen - 1 : d.plen;
  Bit#(52) hi = { pack(d.cpu), 2'b0, d.pc[31:6], pack(d.op), encPlen(basePlen),
                  pack(d.tr), d.src.mode, d.dst.mode,
                  encFoldOp(d.foldOp) };
  Bit#(112) body = { d.src.val, d.dst.val, d.insn0, d.insn1, d.foldInsn0 };
  // The 165 fields sit at [191:27]; the 27 low bits are unused, so the
  // documented slices above are the ones unpackDecEntry reads.
  return { hi, body, 1'b1, 27'b0 };
endfunction

function Bool decEntryFull(DecEntry e) = (e[27] == 1'b1);

function Word decEntryPc(DecEntry e, Word indexPc);
  return { e[188:163], indexPc[5:1], 1'b0 };
endfunction

function DecodedInstr unpackDecEntry(DecEntry e, Word pc);
  Bool cpu = (e[191] == 1'b1);
  Bit#(8) plen = decPlen(e[156:155]) + (cpu ? 1 : 0);
  Word fpc = pc + plenBytes(plen);
  return DecodedInstr {
    pc: pc,
    plen: plen,
    op: unpack(e[162:157]),
    src: Operand { mode: e[150:147], val: e[139:108] },
    dst: Operand { mode: e[146:143], val: e[107:76] },
    insn0: e[75:60],
    insn1: e[59:44],
    fold: (decFoldOp(e[142:140]) != OP_NONE),
    foldOp: decFoldOp(e[142:140]),
    foldPc: fpc,
    foldInsn0: e[43:28],
    foldTarget: fpc + (signExtend(e[43:28][9:0]) << 1),
    foldAfter: fpc + 2,
    tr: unpack(e[154:151]),
    cpu: cpu
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
  case (op)
    OP_NONE:  return False;
    // "another jump" (p. 4-7)
    OP_CALL, OP_JMP, OP_JMPTY, OP_JMPTN, OP_JMPFY, OP_JMPFN: return False;
    // a three-parcel monadic (p. 4-7): CALL/JMP are above; KCALL, RETURN,
    // CATCH, ENTER, LDRAA and POPN are the rest of Table 1-19's row 1.
    OP_KCALL, OP_RETURN, OP_CATCH, OP_ENTER, OP_LDRAA, OP_POPN:
      return False;
    // everything else is a dyadic data operation or a niladic, which the
    // printed rule admits.
    default:  return True;
  endcase
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
    TR_FETCH_FAULT: return "MMU fetch fault (Table 1-26 0x7, p. 1-38)";
    TR_UNIMP_REG:   return "unimplemented control register (p. 1-27)";
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
//   while ((MSP > SHAD) && (MSP - target > SCSIZE)) { ...; MSP -= 16 }
// (p. 3-19): one block per iteration while MSP is more than 256 bytes
// above the target *and* still above SHAD, the old SP -- only blocks
// that are in the cache are written.  The MSP > SHAD bound was missing
// here until golden 016: a frame much larger than the cache (1e cat's
// ENTER R-8224) then "flushed" 514 blocks the cache never held, writing
// aliased cache words into the new frame and charging 2,057 cycles for
// what the printed loop does in 16 blocks.  An ENTER in any other mode
// empties the cache, flushing every valid entry between the old SP and
// MSP.  The timing table's E is this count
// (Table 4-36 prints ENTER = 1 + (Q.E), p. 4-5; the manual never states
// E's unit, so the unit is read from the p. 3-19/3-20 loop: one
// 16-byte block per iteration).
function Word enterFlushBlocks(Word sp, Word msp, Word target, Bool stackMode);
  if (stackMode) begin
    if ((msp > target) && ((msp - target) > 256) && (msp > sp)) begin
      Word want  = ceilBlocks(msp - (target + 256));
      Word valid = ceilBlocks(msp - sp);
      return (want < valid) ? want : valid;
    end else
      return 0;
  end else begin
    if (msp > sp) return ceilBlocks(msp - sp);
    else          return 0;
  end
endfunction

// ENTER's stack-offset target (the decode already sign-extended the
// offset, p. 3-20); otherwise the immediate operand is the target.
function Word enterTarget(DecodedInstr d, Word sp);
  return modeIsStack(d.src.mode) ? sp + d.src.val : d.src.val;
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
                                      modeIsStack(d.src.mode)) };
    end
    OP_CATCH: begin
      Word t = modeIsStack(d.src.mode) ? sp + d.src.val : d.src.val;
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
    // Table 4-32 (printed p. 4-3), Simple Instruction.  One slot and no
    // extra: ADD, ADD3, AND, AND3, CALL, CMP, LDRAA, MOV, MOVA, NOP, OR,
    // OR3, SHL, SHL3, SHR, SHR3, SUB, SUB3, TADD, TSUB, USHR, USHR3, XOR,
    // XOR3.  The one-, three- and five-parcel forms of a mnemonic all take
    // the printed 1 (the table prices the mnemonic, not the parcel count).
    OP_MOV:   return 0;
    OP_SUB:   return 0;
    OP_SUB3:  return 0;
    OP_ADD3:  return 0;
    OP_AND:   return 0;
    OP_AND3:  return 0;
    OP_OR:    return 0;
    OP_OR3:   return 0;
    OP_XOR:   return 0;
    OP_XOR3:  return 0;
    OP_CMPEQ: return 0;                         // CMP row, 1 (p. 3-13)
    OP_CMPGT: return 0;                         // CMP row, 1
    OP_CMPHI: return 0;                         // CMP row, 1
    // Table 4-32 (printed p. 4-3): SHL/SHL3, SHR/SHR3 and USHR/USHR3 are
    // 1, in the one-parcel uimm5,stk5 form as well as the wider forms.
    OP_SHL:   return 0;
    OP_SHL3:  return 0;
    OP_SHR:   return 0;
    OP_SHR3:  return 0;
    OP_USHR:  return 0;
    OP_USHR3: return 0;
    OP_MOVA:  return 0;                         // MOVA row, 1 (Table 4-32)
    OP_LDRAA: return 0;                         // LDRAA row, 1
    OP_ORI:   return 1;                         // ORI row, 2 (Table 4-32)
    OP_ANDI:  return 1;                         // ANDI row, 2
    OP_ADDI:  return 1;                         // ADDI row, 2
    // Table 4-34 (printed p. 4-4), DQM with a constant source: to the
    // stack cache 3 (double-word) and 5 (quad-word); to memory 1 + D and
    // 1 + Q, which are the same 3 and 5 with this model's D = 2, Q = 4.
    // (A source in memory or the stack takes the other rows of the
    // table; EU_S1 sets those where it knows the addresses.)
    OP_DQM2:  return 2;
    OP_DQM4:  return 4;
    OP_TADD:  return 0;                         // TADD row, 1
    OP_TSUB:  return 0;                         // TSUB row, 1
    // Table 4-33 (printed p. 4-4), Multi-Cycle Arithmetic.  MUL/MUL3 print
    // only a range, "Min 3, Max 20", and the page calls the time data
    // dependent without printing the dependence.  The model takes the
    // printed maximum, the same named choice sem/README.md records
    // (choice 24), so core and spec agree; the split is documented, not
    // invented.
    OP_MUL:   return 19;                        // 3..20, max taken
    OP_MUL3:  return 19;
    OP_DIV:   return 37;                        // DIV 38
    OP_DIV3:  return 37;
    OP_REM:   return 37;                        // REM 38
    OP_REM3:  return 37;
    OP_UDIV:  return 37;                        // UDIV 38
    OP_UREM:  return 37;                        // UREM 38
    OP_NOP:   return 0;
    OP_CALL:  return 0;
    OP_KCALL: return 10;                        // KCALL 8 + D + A (p. 4-5)
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
                                            modeIsStack(d.src.mode));
    // Table 4-36 (printed p. 4-5), CATCH = 1.  The quad-word refill of
    // pp. 3-10/3-11 is a stack-cache fill, not an architectural value,
    // and the p. 4-1 assumptions charge no fetch or operand delay for
    // it, so it adds nothing to `cyc`.  It does take clocks, one per
    // word, and since 2026-11-20 nothing is issued behind a CATCH until
    // the fill has ended (HobbitCore `present`); that wait, like a
    // memory operand's, is outside the count.
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

// A grant of the memory's one read port to a second user.  The memory
// has a single registered read address (HobbitMem), and one rule must own
// it: two rules that each called readReq in a clock would be composed by
// bsc with the later call *shadowing* the earlier (G0117), the loser
// reading the winner's word.  The owner is the stack-cache box; the
// prefetch buffer asks through this interface and is told, one clock
// later, whether the word then on the port is its own.
interface MemPort;
  method Action req(Word addr);
  method Bool live();
endinterface

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
