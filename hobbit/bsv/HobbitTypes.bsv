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

typedef Bit#(16) Parcel;
typedef Bit#(32) Word;

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
  TR_ALIGN          // word operand with a non-word stack offset
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
} Hri deriving (Bits);

function Word plenBytes(Bit#(8) n) = zeroExtend(n) << 1;

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
    default:        return "none";
  endcase
endfunction

// ---------------------------------------------------------------------
// Memory: 256 32-bit words (1 Kbyte), big-endian parcel split per the
// shared image format.  The smoke program, its data and its stack all
// fit below 0x400.  A register vector gives unlimited combinational
// read ports (fetch reads six parcels, CATCH reads four words) and one
// architectural write per clock.
// ---------------------------------------------------------------------

interface HobbitMem;
  method Word read(Word addr);                       // addr is a byte address
  method Action write(Word addr, Word val);
endinterface

module mkHobbitMem(HobbitMem);
  Reg#(Vector#(256, Word)) m <- mkReg(replicate(0));

  function Bit#(8) idx(Word a) = truncate(a >> 2);

  method Word read(Word a);
    return m[idx(a)];
  endmethod

  method Action write(Word a, Word v);
    m <= update(m, idx(a), v);
  endmethod
endmodule

endpackage
