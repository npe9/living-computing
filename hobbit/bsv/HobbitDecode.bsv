// HobbitDecode.bsv -- parcel fetch length, field extraction, operand
// decode and branch folding for the ATT92010 Hobbit.
//
// Encodings (all printed pages of the January 1993 Programmer's Reference
// Manual):
//
//   1 parcel   bit 15 = 0, opcode[4:0] = bits 14:10, then the format
//              selected by the opcode: dyadic (source bits 9:5,
//              destination bits 4:0), stack (Table 1-16, offset bits
//              9:2, subcode bits 1:0), or niladic (Table 1-17,
//              subcode bits 9:0).                        p. 1-21, Tables 1-15..1-17
//   3 parcels  bits 15:14 = 10, opcode[5:0] bits 13:8,
//              smode bits 7:4, dmode bits 3:0; source then
//              destination 16-bit operands.                Table 1-18, p. 1-24
//              Monadic three-parcel: opcode 0, smode, subcode
//              bits 3:0, operand-hi then operand-lo.       Table 1-19, p. 1-24
//   5 parcels  bits 15:14 = 11, same first parcel; source-hi,
//              source-lo, destination-hi, destination-lo.  Table 1-20, p. 1-25
//
// Addressing modes: all sixteen general codes of Table 1-21 (p. 1-25) are
// decoded and carried through unchanged.  The stack-offset-indirect codes
// 0x8-0xB and 0xE resolve to the pointer's value as the operand's address;
// the pointed-to word is read by the execution unit's second stage
// (HobbitCore.bsv, "indirect operands"), not here.  Tables 1-22 and 1-23
// are separate tables: the CPU-prefix register mode is not modelled
// (TR_CPU) and the CALL/JMP indirect targets still trap (TR_BAD_MODE).
//
// The 16-bit immediate and offset fields are sign extended (p. 1-23);
// absolute 16-bit addresses are zero extended because CONFIG's PC
// extension bit is 0 after reset (p. 1-23 and p. 1-35).
//
// Branch folding follows p. 4-7: after a foldable instruction, a
// one-parcel JMP/JMPxx is merged into it with the branch target as the
// next address and the fall-through as the alternate next address.

package HobbitDecode;

import Vector::*;
import FIFOF::*;
import GetPut::*;
import ClientServer::*;
import RegFile::*;
import HobbitTypes::*;
import HobbitMmu::*;

interface HobbitDecode;
  method DecodedInstr decode(Word pc, Vector#(6, Parcel) p);
endinterface

module mkHobbitDecode(HobbitDecode);

  function Operand noOpnd();
    return Operand { mode: 4'h0, val: 0 };
  endfunction

  function DecodedInstr mkInstr(Word pc, Bit#(8) len, HobbitOp op,
                                Operand s, Operand d, TrapReason tr);
    return DecodedInstr { pc: pc, plen: len, op: op, src: s, dst: d,
                          insn0: 0, insn1: 0,
                          fold: False, foldOp: OP_NONE, foldPc: 0,
                          foldInsn0: 0, foldTarget: 0,
                          foldAfter: 0, tr: tr, cpu: False };
  endfunction

  function DecodedInstr trapAt(Word pc, Bit#(8) len, TrapReason r);
    return mkInstr(pc, len, OP_NONE, noOpnd(), noOpnd(), r);
  endfunction

  function DecodedInstr unary(Word pc, Bit#(8) len, HobbitOp op,
                              OpMode k, Word v, TrapReason r);
    return mkInstr(pc, len, op, Operand { mode: k, val: v }, noOpnd(), r);
  endfunction

  // A 10-bit PC-relative field is signed and multiplied by two
  // (p. 1-22), relative to the address of the instruction itself
  // (p. 1-27).
  function Word pcrel10(Word pc, Bit#(10) off);
    return pc + (signExtend(off) << 1);
  endfunction

  function Word imm5(Bit#(5) v) = signExtend(v);
  function Word stk5(Bit#(5) v) = zeroExtend(v) << 2;

  // Operand constructors for the one-parcel forms, which name their modes
  // in the mnemonic: C = 5-bit immediate (0xF), S = word stack offset
  // (0xD), I = word stack-offset indirect (0xE) (Table 1-21, p. 1-25;
  // Table 1-15's legend, p. 1-22).
  function Operand immOp(Word v)  = Operand { mode: 4'hF, val: v };
  function Operand stkOp(Word v)  = Operand { mode: 4'hD, val: v };
  function Operand istkOp(Word v) = Operand { mode: 4'hE, val: v };

  function HobbitOp branchOp5(Bit#(5) o);
    case (o)
      5'h03: return OP_JMP;
      5'h04: return OP_JMPFN;
      5'h05: return OP_JMPFY;
      5'h06: return OP_JMPTN;
      default: return OP_JMPTY;
    endcase
  endfunction

  function DecodedInstr branch1(Word pc, HobbitOp op, Parcel q);
    return mkInstr(pc, 1, op,
                   Operand { mode: 4'hF, val: pcrel10(pc, q[9:0]) },
                   noOpnd(), TR_NONE);
  endfunction

  // Table 1-16: stack subcode 00 ENTER, 01 CATCH, 10 RETURN, 11 POPN.
  // ENTER's eight-bit offset is one-filled and multiplied by 16; the
  // others are zero filled and multiplied by 16 (p. 1-22, p. 3-20).
  function DecodedInstr stack1(Word pc, Parcel q);
    Bit#(2) sub = q[1:0];
    Bit#(8) off = q[9:2];
    case (sub)
      // "The 8-bit stack offset is left padded with ones and multiplied
      // by 16 giving it an effective range of -16 to -4096" (p. 3-20,
      // note a).  One-filled, not sign-extended: a field below 0x80 is a
      // frame of more than 2,048 bytes, and until 2026-11-20 this
      // sign-extended it into a *positive* offset (1e's zc: `ENTER
      // R-2160`, field 0x79, moved SP up by 0x790).
      2'd0: return unary(pc, 1, OP_ENTER,  4'hD,
                         { 24'hFFFFFF, off } << 4, TR_NONE);
      2'd1: return unary(pc, 1, OP_CATCH,  4'hD,
                         zeroExtend(off) << 4, TR_NONE);
      2'd2: return unary(pc, 1, OP_RETURN, 4'hD,
                         zeroExtend(off) << 4, TR_NONE);
      default: return unary(pc, 1, OP_POPN, 4'hD,
                            zeroExtend(off) << 4, TR_NONE);
    endcase
  endfunction

  // Table 1-17: CPU = 0x000, KRET = 0x001, NOP = 0x002, FLUSHI = 0x003,
  // FLUSHP = 0x004, CRET = 0x005.  CPU on its own (not followed by a
  // three- or five-parcel instruction, `decode` below) is illegal.  KRET,
  // CRET and the two flushes exist only in the privileged machine
  // (mkHobbitCoreSystem); the other cores take them as before, through
  // the unimplemented-instruction sequence (HobbitCore.bsv, EU_S1).
  function DecodedInstr niladic1(Word pc, Parcel q);
    Bit#(10) sub = q[9:0];
    if (sub == 10'h002)
      return unary(pc, 1, OP_NOP, 4'h0, 0, TR_NONE);
    else if (sub == 10'h000)
      return trapAt(pc, 1, TR_CPU);
    else if (sub == 10'h001)
      return unary(pc, 1, OP_KRET, 4'h0, 0, TR_NONE);
    else if (sub == 10'h005)
      return unary(pc, 1, OP_CRET, 4'h0, 0, TR_NONE);
    else if ((sub == 10'h003) || (sub == 10'h004))
      return unary(pc, 1, OP_FLUSH, 4'h0, 0, TR_NONE);
    else
      return trapAt(pc, 1, TR_UNIMP);
  endfunction

  // imm5 (signed) or wai5 (unsigned, x4) source with a stk5 destination.
  function DecodedInstr dyad1(Word pc, HobbitOp op, Parcel q);
    return mkInstr(pc, 1, op,
                   immOp(imm5(q[9:5])),
                   stkOp(stk5(q[4:0])), TR_NONE);
  endfunction

  function DecodedInstr dyad1wai(Word pc, HobbitOp op, Parcel q);
    return mkInstr(pc, 1, op,
                   immOp(zeroExtend(q[9:5]) << 2),
                   stkOp(stk5(q[4:0])), TR_NONE);
  endfunction

  function DecodedInstr dyad1ss(Word pc, HobbitOp op, Parcel q);
    return mkInstr(pc, 1, op,
                   stkOp(stk5(q[9:5])),
                   stkOp(stk5(q[4:0])), TR_NONE);
  endfunction

  // MOV.IS / MOV.SI / MOV.II (opcodes 0x19/0x1A/0x1B, Table 1-15 row 11):
  // the "I" field is the 5-bit indirect stack offset, i.e. Table 1-21's
  // 0xE mode with the zero-extended, x4-scaled offset (p. 1-22, p. 3-32).
  function DecodedInstr mov1(Word pc, Bit#(4) smode, Bit#(4) dmode, Parcel q);
    return mkInstr(pc, 1, OP_MOV,
                   Operand { mode: smode, val: stk5(q[9:5]) },
                   Operand { mode: dmode, val: stk5(q[4:0]) },
                   TR_NONE);
  endfunction

  // SHL3.CS (opcode 0x1E) and SHR3.CS (opcode 0x1F), Table 1-15 row 11
  // (p. 1-22): the source is the unsigned five-bit `uimm5` field, and the
  // destination is the five-bit word stack offset scaled by four (p. 1-22,
  // Table 3-2 p. 3-4).  Unlike imm5, uimm5 is not sign-extended and is not
  // scaled: p. 3-41/3-42 print the one-parcel form as `uimm5, stk5`, and
  // its value is the shift count itself.
  function DecodedInstr shift1(Word pc, HobbitOp op, Parcel q);
    return mkInstr(pc, 1, op,
                   immOp(zeroExtend(q[9:5])),
                   stkOp(stk5(q[4:0])), TR_NONE);
  endfunction

  // MOV.WS (opcode 0x0A, Table 1-15 p. 1-22; p. 3-32): the source is the
  // unsigned `wai5` field multiplied by four (Table 3-2 p. 3-4), and the
  // 5-bit stack offset is zero-extended and multiplied by four (p. 1-22).
  function DecodedInstr movws1(Word pc, Parcel q);
    return mkInstr(pc, 1, OP_MOV,
                   immOp(zeroExtend(q[9:5]) << 2),
                   stkOp(stk5(q[4:0])), TR_NONE);
  endfunction

  // Three-parcel gen16 / five-parcel gen32 operands.  The mode nibble is
  // carried verbatim (Table 1-21, p. 1-25); p. 1-23 fixes the extension:
  // a 16-bit field is sign-extended in immediate and offset modes, and an
  // absolute address is zero-extended because CONFIG's PC-extension bit is
  // 0 (p. 1-23, p. 1-35).  A 32-bit field is used as it stands.
  function Operand gen16(Bit#(4) m, Parcel v);
    if (modeIsImm(m) || modeIsStack(m) || modeIsIndirect(m)) begin
      return Operand { mode: m, val: signExtend(v) };
    end else begin
      return Operand { mode: m, val: zeroExtend(v) };
    end
  endfunction

  function Operand gen32(Bit#(4) m, Word v) = Operand { mode: m, val: v };

  // Two pointed-to words in one instruction (both operands indirect)
  // were refused here as the unimplemented sequence until 2026-11-20, on
  // the argument that EU_S2 would need a third stack-cache port.  The
  // real part executes them -- 1e compares two bytes through two
  // pointers (`CMPEQ *R24.UB, *R28.UB`, echo's 274th instruction) -- and
  // no third port is needed: the two pointer words are EU_S1's reads and
  // the two pointed-to words are EU_S2's, a clock later, on the same two
  // printed ports (64x32x2, Figure 1-1, p. 1-2).

  // Table 1-23, p. 1-26: CALL/JMP may be PC relative (0xE), absolute
  // (0xF), absolute indirect (0xC, `**$addr`: the target is the word at
  // the address) or stack offset indirect (0xD, `*Roffset`: the target
  // is the word in the stack slot).  The direct forms carry their target
  // as an immediate; the indirect forms keep a word operand (Table 1-21's
  // 0xC / 0xD) that EU_S1 reads, and the jump is redirected from EU_S2
  // as RETURN's is (HobbitCore.bsv, `flowIndirect`).  Until 2026-11-20
  // the indirect forms trapped; 1e calls through a table of functions
  // (`CALL *R12`, doprint's format dispatch).
  function DecodedInstr branch3(Word pc, HobbitOp op, Bit#(4) m, Word v, Bit#(8) len);
    case (m)
      // Only CALL and JMP: a conditional jump with an indirect mode
      // (p. 3-28) is not modelled and still traps below.
      4'hC: if ((op == OP_CALL) || (op == OP_JMP))
              return mkInstr(pc, len, op,
                             Operand { mode: 4'hC, val: v },
                             noOpnd(), TR_NONE);
            else
              return trapAt(pc, len, TR_BAD_MODE);
      4'hD: if ((op == OP_CALL) || (op == OP_JMP))
              return mkInstr(pc, len, op,
                             Operand { mode: 4'hD, val: v },
                             noOpnd(), TR_NONE);
            else
              return trapAt(pc, len, TR_BAD_MODE);
      4'hE: return mkInstr(pc, len, op,
                           Operand { mode: 4'hF, val: pc + v },
                           noOpnd(), TR_NONE);
      4'hF: return mkInstr(pc, len, op,
                           Operand { mode: 4'hF, val: v },
                           noOpnd(), TR_NONE);
      default: return trapAt(pc, len, TR_BAD_MODE);
    endcase
  endfunction

  // DQM, opcode 0x07 (Tables 1-18/1-20; p. 3-18).  The destination mode
  // field carries the size: 0x0/0x4/0x8 are a double word (the address
  // forms of 0xC/0xD/0xE), 0xC/0xD/0xE a quad word; 0xF is an illegal
  // instruction and so, by the page's Notes, is any other mode.  The
  // source is a word mode or the constant.
  //
  // The EU does one architectural write per instruction slot.  With a
  // constant source the remaining words leave from EU_S3's commit like
  // KCALL's frame tail (1e's `DQM $0, *R4`, a structure cleared four
  // words at a time); with a source in memory or the stack the
  // instruction occupies EU_S1's slot once per word (HobbitCore.bsv,
  // `dqmIdx`; 1e's compiler copies structures this way).
  function DecodedInstr dqm(Word pc, Bit#(8) len, Bit#(4) sm, Bit#(4) dm,
                            Operand s, Operand t);
    Bool dbl  = (dm == 4'h0) || (dm == 4'h4) || (dm == 4'h8);
    Bool quad = (dm == 4'hC) || (dm == 4'hD) || (dm == 4'hE);
    Bit#(4) wm = (dm == 4'h0) ? 4'hC : ((dm == 4'h4) ? 4'hD
               : ((dm == 4'h8) ? 4'hE : dm));
    if (!dbl && !quad)
      return trapAt(pc, len, TR_BAD_MODE);
    else if (sm == 4'hF)
      return mkInstr(pc, len, dbl ? OP_DQM2 : OP_DQM4, s,
                     Operand { mode: wm, val: t.val }, TR_NONE);
    else if ((sm == 4'hC) || (sm == 4'hD) || (sm == 4'hE))
      // A source in memory or the stack: the EU moves it a word at a
      // time (HobbitCore.bsv, `dqmIdx`).
      return mkInstr(pc, len, dbl ? OP_DQM2 : OP_DQM4, s,
                     Operand { mode: wm, val: t.val }, TR_NONE);
    else
      return trapAt(pc, len, TR_BAD_MODE);
  endfunction

  // Tables 1-18 (p. 1-24) and 1-20 (p. 1-25): the three- and five-parcel
  // dyadic grids are identical.  Every opcode the tables mark "unimp"
  // returns OP_NONE and the caller traps.  Rows 010 and 111 are entirely
  // unimp; row 011 has only 1D/1E/1F; row 101 has only 2C-2F; row 001 has
  // only 0C/0D; row 000 is the monadic row plus 01-07.
  function HobbitOp dyadicOp(Bit#(6) o);
    case (o)
      // row 000
      6'h00: return OP_NONE;   // monadic (Table 1-19), handled separately
      6'h01: return OP_ORI;    // ORI  (p. 3-37): dst |= src, Acc = old dst
      6'h02: return OP_ANDI;   // ANDI (p. 3-8):  dst &= src, Acc = old dst
      6'h03: return OP_ADDI;   // ADDI (p. 3-6):  dst += src, Acc = old dst
      6'h04: return OP_MOVA;
      6'h05: return OP_UREM;
      6'h06: return OP_MOV;
      6'h07: return OP_NONE;   // DQM   -- decoded by `dqm`, before this table
      // row 001
      6'h0C: return OP_TADD;
      6'h0D: return OP_TSUB;
      // row 011
      6'h1D: return OP_CMPGT;
      6'h1E: return OP_CMPHI;
      6'h1F: return OP_CMPEQ;
      // row 100
      6'h20: return OP_SUB;
      6'h21: return OP_OR;
      6'h22: return OP_AND;
      6'h23: return OP_ADD;
      6'h24: return OP_XOR;
      6'h25: return OP_REM;
      6'h26: return OP_MUL;
      6'h27: return OP_DIV;
      // row 101
      6'h2C: return OP_SHR;
      6'h2D: return OP_USHR;
      6'h2E: return OP_SHL;
      6'h2F: return OP_UDIV;
      // row 110
      6'h30: return OP_SUB3;
      6'h31: return OP_OR3;
      6'h32: return OP_AND3;
      6'h33: return OP_ADD3;
      6'h34: return OP_XOR3;
      6'h35: return OP_REM3;
      6'h36: return OP_MUL3;
      6'h37: return OP_DIV3;
      // row 111
      6'h3C: return OP_SHR3;
      6'h3D: return OP_USHR3;
      6'h3E: return OP_SHL3;
      default: return OP_NONE;
    endcase
  endfunction

  // -------------------------------------------------------------------
  // Branch folding (p. 4-7).
  // -------------------------------------------------------------------

  function DecodedInstr maybeFold(DecodedInstr d, Vector#(6, Parcel) p);
    Parcel q = p[d.plen[2:0]];
    Bit#(5) opc = q[14:10];
    Bool oneParcelBranch = (q[15] == 1'b0) && (opc >= 5'h03) && (opc <= 5'h07);
    if (d.tr == TR_NONE && isFoldable(d.op) && oneParcelBranch) begin
      Word bpc = d.pc + plenBytes(d.plen);
      return DecodedInstr { pc: d.pc, plen: d.plen, op: d.op,
                            src: d.src, dst: d.dst,
                            insn0: d.insn0, insn1: d.insn1,
                            fold: True, foldOp: branchOp5(opc),
                            foldPc: bpc, foldInsn0: q,
                            foldTarget: pcrel10(bpc, q[9:0]),
                            foldAfter: bpc + 2, tr: d.tr, cpu: False };
    end else
      return d;
  endfunction

  function DecodedInstr decodeRaw(Word pc, Vector#(6, Parcel) p);
    Parcel p0 = p[0];

    if (p0[15] == 1'b0) begin
      // ---------------- one parcel ----------------
      // Table 1-15 (p. 1-22): 0x11/0x12 CMPGT (semantics p. 3-13);
      // 0x15/0x17 ADD3 (Acc = dst + src, the accumulator at CSP+4,
      // p. 1-7 and p. 3-5); 0x0A MOV.WS (p. 3-32).
      Bit#(5) opc = p0[14:10];
      case (opc)
        // KCALL imm10 (Table 1-15 p. 1-22, Table 3-1 #24): the ten-bit
        // field is zero-extended and multiplied by four (p. 3-29).
        5'h00: return maybeFold(unary(pc, 1, OP_KCALL, 4'hF,
                                      zeroExtend(p0[9:0]) << 2, TR_NONE), p);
        5'h01: return branch1(pc, OP_CALL, p0);
        5'h02: return maybeFold(stack1(pc, p0), p);
        5'h03: return branch1(pc, OP_JMP, p0);
        5'h04: return branch1(pc, OP_JMPFN, p0);
        5'h05: return branch1(pc, OP_JMPFY, p0);
        5'h06: return branch1(pc, OP_JMPTN, p0);
        5'h07: return branch1(pc, OP_JMPTY, p0);
        5'h0A: return maybeFold(movws1(pc, p0), p);
        5'h0B: return maybeFold(niladic1(pc, p0), p);
        // Table 1-15 row 01 (p. 1-22): ADD3.WS 0x0D uses the word-aligned
        // immediate wai5 as its source (p. 1-22, p. 3-5); AND3.CS 0x0E and
        // AND.SS 0x0F complete the AND rows of p. 3-7.
        5'h0D: return maybeFold(dyad1wai(pc, OP_ADD3, p0), p);
        5'h0E: return maybeFold(dyad1(pc, OP_AND3, p0), p);
        5'h0F: return maybeFold(dyad1ss(pc, OP_AND, p0), p);
        5'h10: return maybeFold(dyad1(pc, OP_CMPEQ, p0), p);
        5'h11: return maybeFold(dyad1ss(pc, OP_CMPGT, p0), p);
        5'h12: return maybeFold(dyad1(pc, OP_CMPGT, p0), p);
        5'h13: return maybeFold(dyad1ss(pc, OP_CMPEQ, p0), p);
        5'h14: return maybeFold(dyad1(pc, OP_ADD, p0), p);
        5'h15: return maybeFold(dyad1(pc, OP_ADD3, p0), p);
        5'h16: return maybeFold(dyad1ss(pc, OP_ADD, p0), p);
        5'h17: return maybeFold(dyad1ss(pc, OP_ADD3, p0), p);
        5'h18: return maybeFold(dyad1ss(pc, OP_MOV, p0), p);
        // Table 1-15 row 11 (p. 1-22): MOV.IS 0x19 (istk5,stk5),
        // MOV.SI 0x1A (stk5,istk5), MOV.II 0x1B (istk5,istk5).  The "I"
        // field is Table 1-21's stack-offset-indirect word mode 0xE with
        // the one-parcel field zero-extended and multiplied by four
        // (p. 1-21, p. 1-22); the pointed-to word is read in EU_S2.
        5'h19: return maybeFold(mov1(pc, 4'hE, 4'hD, p0), p);
        5'h1A: return maybeFold(mov1(pc, 4'hD, 4'hE, p0), p);
        5'h1B: return maybeFold(mov1(pc, 4'hE, 4'hE, p0), p);
        5'h1C: return maybeFold(dyad1(pc, OP_MOV, p0), p);
        // Table 1-15 row 11 (p. 1-22): MOV.CS 0x1C (above), MOVA.SS 0x1D,
        // SHL3.CS 0x1E, SHR3.CS 0x1F.  MOVA's both fields are word stack
        // offsets (p. 3-33, one-parcel encoding stk5,stk5).
        5'h1D: return maybeFold(dyad1ss(pc, OP_MOVA, p0), p);
        5'h1E: return maybeFold(shift1(pc, OP_SHL3, p0), p);
        5'h1F: return maybeFold(shift1(pc, OP_SHR3, p0), p);
        default: return trapAt(pc, 1, TR_UNIMP);
      endcase
    end else if (p0[15:14] == 2'b10) begin
      // ---------------- three parcels ----------------
      Bit#(6) opc = p0[13:8];
      Bit#(4) sm  = p0[7:4];
      Bit#(4) dm  = p0[3:0];
      // p. 1-23: monadic 1st parcel, then OPERAND-HI (parcel 2) and
      // OPERAND-LO (parcel 3), i.e. one 32-bit operand: RETURN stk32 and
      // the ENTER/CATCH/POPN word32 forms all use both parcels.
      Word v32 = { p[1], p[2] };

      if (opc == 6'h00) begin
        // Table 1-19 monadic subcodes.
        case (dm)
          4'h1: return maybeFold(branch3(pc, OP_CALL, sm, v32, 3), p);
          4'h2: if (sm == 4'hD)
                  return mkInstr(pc, 3, OP_RETURN,
                                 Operand { mode: 4'hD, val: v32 },
                                 noOpnd(), TR_NONE);
                else
                  return trapAt(pc, 3, TR_RETURN_MODE);
          4'h3: return maybeFold(branch3(pc, OP_JMP, sm, v32, 3), p);
          4'h4: return maybeFold(branch3(pc, OP_JMPFN, sm, v32, 3), p);
          4'h5: return maybeFold(branch3(pc, OP_JMPFY, sm, v32, 3), p);
          4'h6: return maybeFold(branch3(pc, OP_JMPTN, sm, v32, 3), p);
          4'h7: return maybeFold(branch3(pc, OP_JMPTY, sm, v32, 3), p);
          4'h8: if (sm == 4'hD)
                  return mkInstr(pc, 3, OP_CATCH,
                                 Operand { mode: 4'hD, val: v32 },
                                 noOpnd(), TR_NONE);
                else if (sm == 4'hF)
                  return mkInstr(pc, 3, OP_CATCH,
                                 Operand { mode: 4'hF, val: v32 },
                                 noOpnd(), TR_NONE);
                // CATCH's operand is a Table 3-2 word32 like ENTER's
                // (p. 3-10; Table 1-21, p. 1-25): absolute (0xC) and
                // stack-offset-indirect (0xE) take the target from memory,
                // which EU_S1 reads (HobbitCore.bsv, `word32Mem`).  The
                // kernel's interrupt return uses CATCH *4(SP) (s9term,
                // record 2,849,530 of the boot).
                else if ((sm == 4'hC) || (sm == 4'hE))
                  return mkInstr(pc, 3, OP_CATCH,
                                 Operand { mode: sm, val: v32 },
                                 noOpnd(), TR_NONE);
                else
                  return trapAt(pc, 3, TR_BAD_MODE);
          4'h9: if (sm == 4'hD)
                  return mkInstr(pc, 3, OP_ENTER,
                                 Operand { mode: 4'hD, val: v32 },
                                 noOpnd(), TR_NONE);
                else if (sm == 4'hF)
                  return mkInstr(pc, 3, OP_ENTER,
                                 Operand { mode: 4'hF, val: v32 },
                                 noOpnd(), TR_NONE);
                // p. 3-20, cases 3 and 4: with a stack-offset-indirect
                // (0xE) or absolute (0xC) source "the target value ... is
                // fetched from memory (or the stack cache)" and the cache
                // is set empty.  EU_S1 reads the word and passes the
                // instruction on as the immediate form (HobbitCore.bsv,
                // `word32Mem`).
                else if ((sm == 4'hC) || (sm == 4'hE))
                  return mkInstr(pc, 3, OP_ENTER,
                                 Operand { mode: sm, val: v32 },
                                 noOpnd(), TR_NONE);
                else
                  return trapAt(pc, 3, TR_BAD_MODE);
          4'hF: if (sm == 4'hD)
                  return mkInstr(pc, 3, OP_POPN,
                                 Operand { mode: 4'hD, val: v32 },
                                 noOpnd(), TR_NONE);
                else
                  return trapAt(pc, 3, TR_BAD_MODE);
          // KCALL word32 (Table 1-19 row 1 col 0, p. 1-24; p. 3-29):
          // the source is a Table 3-2 word32 operand pushed onto the
          // interrupt stack.  The EU resolves modes C/D/E/F.
          4'h0: return mkInstr(pc, 3, OP_KCALL,
                               Operand { mode: sm, val: v32 },
                               noOpnd(), TR_NONE);
          // LDRAA flow32 (Table 1-19 row 1 col 2, p. 1-24; p. 3-31):
          // Acc = &dst, the address computed exactly as a JMP target
          // (Table 1-23, p. 1-26).
          4'hA: return mkInstr(pc, 3, OP_LDRAA,
                               branch3(pc, OP_NOP, sm, v32, 3).src,
                               noOpnd(), branch3(pc, OP_NOP, sm, v32, 3).tr);
          // FLUSHPTE word32 (Table 1-19, p. 1-24; p. 3-27).  The model
          // flushes every TLB and NPSR entry (HobbitCore.bsv, EU_S3), so
          // the operand is not read.
          4'hB: return mkInstr(pc, 3, OP_FLUSHPTE,
                               Operand { mode: sm, val: v32 },
                               noOpnd(), TR_NONE);
          default: return trapAt(pc, 3, TR_UNIMP);
        endcase
      end else if (opc == 6'h07) begin
        return maybeFold(dqm(pc, 3, sm, dm, gen16(sm, p[1]),
                             gen16(dm, p[2])), p);
      end else begin
        HobbitOp op = dyadicOp(opc);
        if (op == OP_NONE)
          return trapAt(pc, 3, TR_UNIMP);
        else
          return maybeFold(mkInstr(pc, 3, op, gen16(sm, p[1]), gen16(dm, p[2]),
                                   TR_NONE), p);
      end
    end else if (p0[15:14] == 2'b11) begin
      // ---------------- five parcels ----------------
      Bit#(6) opc = p0[13:8];
      Bit#(4) sm  = p0[7:4];
      Bit#(4) dm  = p0[3:0];

      if (opc == 6'h00)
        return trapAt(pc, 5, TR_UNIMP);   // Table 1-20 row 000 col 000
      else if (opc == 6'h07)
        return maybeFold(dqm(pc, 5, sm, dm, gen32(sm, { p[1], p[2] }),
                             gen32(dm, { p[3], p[4] })), p);
      else begin
        HobbitOp op = dyadicOp(opc);
        if (op == OP_NONE)
          return trapAt(pc, 5, TR_UNIMP);
        else
          return maybeFold(mkInstr(pc, 5, op,
                                   gen32(sm, { p[1], p[2] }),
                                   gen32(dm, { p[3], p[4] }), TR_NONE), p);
      end
    end else begin
      // bit 15 = 1, bit 14 = 0 is not a legal length prefix (p. 1-21).
      return trapAt(pc, 1, TR_BAD_LENGTH);
    end
  endfunction

  // Fill the retirement record's first two parcels: the parcel stream is
  // big-endian within each memory word, so p[0] is the parcel at pc and
  // p[1] the parcel at pc+2 (p. 1-21 and the shared image format).
  // The CPU escape (p. 3-14): "The instruction following CPU is
  // considered part of the CPU instruction."  The pair is one decoded
  // instruction (`cpu`, HobbitTypes).  Only the three- and five-parcel
  // forms have the mode fields CPU modifies (Table 1-22, p. 1-26); after
  // CPU a mode below 0xC other than 7 is illegal (p. 1-39), and mode 7
  // names a control register, of which 1..12 exist (Table 1-24, p. 1-26;
  // 0 and 13..15 are exception 6, p. 1-27).  No branch is folded into a
  // CPU instruction: the six parcels the decoder sees are all its own.
  function Bool cpuModeBad(Bit#(4) m) = (m < 4'hC) && (m != 4'h7);
  function Bool cpuRegBad(Bit#(4) m, Word v) =
    (m == 4'h7) && ((v[3:0] == 0) || (v[3:0] > 4'd12));

  function DecodedInstr cpuEscape(Word pc, Vector#(6, Parcel) p);
    Vector#(6, Parcel) q = shiftInAtN(p, 0);
    Parcel q0 = q[0];
    let d = decodeRaw(pc, q);
    if (d.plen == 1)
      return trapAt(pc, 1, TR_CPU);
    else begin
      Bit#(4) sm = q0[7:4];
      Bit#(4) dm = q0[3:0];
      Bool monadic = (q0[13:8] == 6'h00);
      TrapReason tr = d.tr;
      if (!monadic && (tr == TR_NONE)) begin
        if (cpuModeBad(sm) || cpuModeBad(dm))
          tr = TR_CPU;
        else if (cpuRegBad(sm, d.src.val) || cpuRegBad(dm, d.dst.val))
          tr = TR_UNIMP_REG;
      end
      d.plen = d.plen + 1;
      d.fold = False;
      d.foldOp = OP_NONE;
      d.cpu = True;
      d.tr = tr;
      return d;
    end
  endfunction

  method DecodedInstr decode(Word pc, Vector#(6, Parcel) p);
    let d = (p[0] == 16'h2C00) ? cpuEscape(pc, p) : decodeRaw(pc, p);
    return DecodedInstr { pc: d.pc, plen: d.plen, op: d.op,
                          src: d.src, dst: d.dst,
                          insn0: p[0],
                          insn1: (d.plen == 8'd1) ? 16'd0 : p[1],
                          fold: d.fold, foldOp: d.foldOp,
                          foldPc: d.foldPc, foldInsn0: d.foldInsn0,
                          foldTarget: d.foldTarget, foldAfter: d.foldAfter,
                          tr: d.tr, cpu: d.cpu };
  endmethod

endmodule

// ---------------------------------------------------------------------
// Prefetch buffer cache: 1024 bytes per way, three ways.
//
// Figure 1-1 (printed p. 1-2) prints "PREFETCH BUFFER CACHE 1024 X3
// bytes" and a 64-bit path into the prefetch/decode unit; p. 1-1 calls
// it a "3 Kbyte encoded instruction cache (organized as 3-way set
// associative)".  A way is 1024 bytes = 128 lines of 64 bits, so the
// buffer is 128 sets x 3 ways x 64 bits = 3 Kbyte.  Set index is
// addr[9:3], tag is addr[31:10]; the three ways of a set are three
// different 1 KB regions that map to the same set.
//
// The 64-bit line is the diagram's 64-bit path: the fill reads two
// 32-bit words from the synchronous memory and assembles one line, and
// the PDU reads whole lines.  The model's memory is 1 KB (HobbitMem),
// so the boot fill installs one line in every set, in way 0; that covers
// every address the tests use.
//
// On-demand fill (2026-11-20).  A fetch whose line is absent used to be
// a model limitation (TR_FETCH_MISS); a 1e program does not fit one
// 1 Kbyte window (`echo`'s `_main` is at 0x2ad0 and its `main` at
// 0x1020), so the buffer now fills on demand: `demand(va)` reads the
// three consecutive 64-bit lines a decode at `va` can need (the PDU's
// l0, l1, l2) and installs each one that is not already present.  The
// p. 1-36 reset description calls this "demand prefetch"; CONFIG's
// prefetch-mode bit and the lookahead it selects are not modelled.
//
// Replacement is a model choice -- the manual prints the organization
// (three ways, p. 1-1) and no policy: an invalid way of the set is used
// first, otherwise one rotating victim pointer shared by all sets.
//
// Timing: a fetch that hits costs nothing extra (the p. 4-1 assumption
// "instruction fetches must access in the instruction cache"), and a
// demand fill stalls the fetch, not the instruction: like the decoded
// store's own fill it adds nothing to `cyc`, so no Table 4-37 fetch
// delay is charged.  Under translation the fill reads the virtual
// address through the text face as the boot fill does; demand fill with
// the MMU on is untested.
interface HobbitPrefetch;
  method Action startFill();
  // Fill the 128-line window from an arbitrary 8-byte-aligned address
  // (a Plan 9 image's code does not start at 0).
  method Action startFillAt(Word addr);
  method Bool filling();
  method Bool ready();
  // Fill, on demand, the three lines a decode at `va` can need.  Call
  // only when !filling().
  method Action demand(Word va);
  method Bit#(32) demandFills();
  method Maybe#(Bit#(64)) lineAt(Word addr);
  // True when the fetch address has no valid MMU mapping (p. 2-3).
  method Bool faultAt(Word addr);
  // Record a text translation so the text TLB/NPSR refills (p. 2-1).
  method Action noteFetch(Word addr);
  // PDU_S1's three lines from an 8-byte-aligned a0 -- lineAt(a0),
  // lineAt(a0 + 8), lineAt(a0 + 16) -- and whether any of the three
  // translations faults (faultAt), on two translations instead of six
  // (docs/fpga_area.md): a translation depends on the address only
  // through its page, and a0 + 8 shares a page with a0 or with a0 + 16.
  method Tuple4#(Maybe#(Bit#(64)), Maybe#(Bit#(64)), Maybe#(Bit#(64)), Bool)
    lines3(Word a0);
endinterface

typedef struct {
  Bit#(22) tag;      // addr[31:10]
  Bit#(64) data;     // {word at line+0, word at line+4}
} PfcLine deriving (Bits);

module mkHobbitPrefetch#(HobbitMem mem, MemPort port, HobbitMmu mmu,
                         Reg#(Word) psw)(HobbitPrefetch);
  // structure follows Flute (Bluespec, Inc., Apache-2.0) — see
  // docs/bluespec_architecture.md: the cache is a box behind its own
  // interface, not logic inlined into a pipeline stage.

  // Three banks, one per way (Figure 1-1 / p. 1-1's three-way set
  // associative organization).  Each bank is a plain array with one
  // write port and one combinational read; a RegFile emits that shape.
  // A Vector of 3 KB here is 41,052 LUT4 + 22,539 FF
  // (docs/area_analysis.md), so it is not an option.
  RegFile#(Bit#(7), PfcLine) way0 <- mkRegFileFull;
  RegFile#(Bit#(7), PfcLine) way1 <- mkRegFileFull;
  RegFile#(Bit#(7), PfcLine) way2 <- mkRegFileFull;
  // 128 sets x 3 ways of valid bits (way 0 is the only way the boot
  // fill installs in this milestone).  One 128-bit vector per way keeps
  // the printed 384 bits, but indexes by set alone: a single 384-bit
  // vector addressed as {set, way} needs 512 entries, so the writes for
  // sets 96..127 fell past its end.
  Reg#(Bit#(128)) valid0 <- mkReg(0);
  Reg#(Bit#(128)) valid1 <- mkReg(0);
  Reg#(Bit#(128)) valid2 <- mkReg(0);
  Reg#(Bit#(7)) fillSet <- mkReg(0);
  Reg#(Bit#(2)) fillPhase <- mkReg(0);
  Reg#(Bit#(32)) fillLo <- mkReg(0);
  Reg#(Word) fillBase <- mkReg(0);
  Reg#(Bool) fillingR <- mkReg(False);
  Reg#(Bool) readyR <- mkReg(False);
  // Demand fill: the same engine, three lines instead of 128, a way
  // chosen per line instead of way 0.
  Reg#(Bool) demandR <- mkReg(False);
  Reg#(Bit#(2)) victim <- mkReg(0);
  Reg#(Bit#(32)) ndemand <- mkReg(0);

  function MmuReq xreq(Word va) =
    MmuReq { va: va, isText: True, isWrite: False,
             user: (psw[10] == 1'b1), enabled: (psw[16] == 1'b1) };

  function Word paOf(Word va);
    return mmu.translate(xreq(va)).pa;
  endfunction

  // The fill reads two words per 64-bit line through the memory's one
  // read port, which the stack-cache box owns (`port`, HobbitTypes
  // MemPort): it asks for the word it needs, and when the box says the
  // word on the port is the prefetch's it captures it.  A clock in which
  // the box needed the port itself (a CATCH refill, an operand) costs the
  // fill a clock and nothing else.  fillPhase is 0 while the line's first
  // word is wanted and 1 while its second is.
  //
  // The address is translated here, as a text reference (p. 2-1), and the
  // port is asked for the physical word; the text TLB's bookkeeping
  // (`noteText`) is done once per word, when the word is taken.  A word
  // whose translation faults is not read and counts as zero: the fetch
  // that needs it reports the fault from lineAt()/faultAt().
  rule fillStep (fillingR);
    Word lineAddr = fillBase + (zeroExtend(fillSet) << 3);
    Bool last = (fillSet == (demandR ? 7'd2 : 7'd127));
    Word va = (fillPhase == 2'd0) ? lineAddr : lineAddr + 4;
    let x = mmu.translate(xreq(va));
    Bool ok = (x.fault == MMU_OK);
    Word data = ok ? mem.readData() : 0;
    if (ok && !port.live()) begin
      port.req(x.pa);
    end else if (fillPhase == 2'd0) begin
      mmu.noteText(xreq(va));
      fillLo <= data;
      fillPhase <= 2'd1;
    end else begin
      mmu.noteText(xreq(va));
      Word linePa = ok ? (x.pa & 32'hFFFFFFF8) : lineAddr;
      Bit#(64) line = { fillLo, data };
      PfcLine l = PfcLine { tag: linePa[31:10], data: line };
      // The set is the address's own index, not the fill counter: a
      // window filled from a base other than 0 must land in the sets
      // that lineAt() looks up (addr[9:3] of the physical address).
      Bit#(7) set = linePa[9:3];
      Bit#(22) tag = linePa[31:10];
      if (!demandR) begin
        way0.upd(set, l);
        valid0 <= valid0 | (128'd1 << set);
      end else begin
        Bool v0 = valid0[set] == 1'b1;
        Bool v1 = valid1[set] == 1'b1;
        Bool v2 = valid2[set] == 1'b1;
        PfcLine e0 = way0.sub(set);
        PfcLine e1 = way1.sub(set);
        PfcLine e2 = way2.sub(set);
        Bool present = (v0 && (e0.tag == tag)) || (v1 && (e1.tag == tag)) ||
                       (v2 && (e2.tag == tag));
        if (!present) begin
          Bit#(2) w = !v0 ? 2'd0 : (!v1 ? 2'd1 : (!v2 ? 2'd2 : victim));
          if (v0 && v1 && v2)
            victim <= (victim == 2'd2) ? 2'd0 : victim + 1;
          case (w)
            2'd0: begin way0.upd(set, l); valid0 <= valid0 | (128'd1 << set); end
            2'd1: begin way1.upd(set, l); valid1 <= valid1 | (128'd1 << set); end
            default: begin way2.upd(set, l); valid2 <= valid2 | (128'd1 << set); end
          endcase
        end
      end
      fillPhase <= 2'd0;
      if (last) begin
        fillingR <= False;
        readyR   <= True;
      end else
        fillSet <= fillSet + 1;
    end
  endrule

  // A line's lookup, given the translation `xr` of its page (lineAt's
  // body; only xr.fault and xr.pa[31:12] are used, so a translation of
  // any address on va's page will do).
  function Maybe#(Bit#(64)) lineOf(MmuResp xr, Word va);
    Word addr = { xr.pa[31:12], va[11:0] };
    Bit#(7) set = addr[9:3];
    Bit#(22) tag = addr[31:10];
    PfcLine a0 = way0.sub(set);
    PfcLine a1 = way1.sub(set);
    PfcLine a2 = way2.sub(set);
    Maybe#(Bit#(64)) r = tagged Invalid;
    if (xr.fault != MMU_OK)
      r = tagged Invalid;
    else if ((valid0[set] == 1'b1) && (a0.tag == tag))
      r = tagged Valid a0.data;
    else if ((valid1[set] == 1'b1) && (a1.tag == tag))
      r = tagged Valid a1.data;
    else if ((valid2[set] == 1'b1) && (a2.tag == tag))
      r = tagged Valid a2.data;
    return r;
  endfunction

  method Action startFillAt(Word addr);
    if (!fillingR && !readyR) begin
      fillBase  <= addr & 32'hFFFFFFF8;
      fillSet   <= 0;
      fillPhase <= 0;
      fillingR  <= True;
    end
  endmethod

  method Action demand(Word va);
    if (!fillingR) begin
      fillBase  <= va & 32'hFFFFFFF8;
      fillSet   <= 0;
      fillPhase <= 0;
      fillingR  <= True;
      demandR   <= True;
      ndemand   <= ndemand + 1;
    end
  endmethod

  method Bit#(32) demandFills() = ndemand;

  method Action startFill();
    if (!fillingR && !readyR) begin
      fillBase  <= 0;
      fillSet   <= 0;
      fillPhase <= 0;
      fillingR  <= True;
    end
  endmethod

  method Bool filling() = fillingR;
  method Bool ready()   = readyR;

  method Bool faultAt(Word addr) =
    mmu.translate(xreq(addr)).fault != MMU_OK;

  method Action noteFetch(Word addr);
    mmu.noteText(xreq(addr));
  endmethod

  method Maybe#(Bit#(64)) lineAt(Word va) = lineOf(mmu.translate(xreq(va)), va);

  // Every translation is a function of va[31:12] alone (the TLB and NPSR
  // match, the nonpaged bound in 4 KB units, the walk's entry addresses,
  // the permission checks) and passes va[11:0] through to the physical
  // address unchanged (HobbitMmu translateFn).  So a0 + 8, which is on
  // a0's page unless a0 is the page's last line and then on a0 + 16's,
  // takes that page's translation with its own low twelve bits.
  method Tuple4#(Maybe#(Bit#(64)), Maybe#(Bit#(64)), Maybe#(Bit#(64)), Bool)
      lines3(Word a0);
    Word a1 = a0 + 8;
    Word a2 = a0 + 16;
    let x0 = mmu.translate(xreq(a0));
    let x2 = mmu.translate(xreq(a2));
    let x1 = (a0[11:3] == 9'h1FF) ? x2 : x0;
    return tuple4(lineOf(x0, a0), lineOf(x1, a1), lineOf(x2, a2),
                  (x0.fault != MMU_OK) || (x1.fault != MMU_OK) ||
                  (x2.fault != MMU_OK));
  endmethod

endmodule

// ---------------------------------------------------------------------
// The prefetch/decode unit, split into three explicitly named stage
// modules.  Figure 1-1 (printed p. 1-2) prints "PREFETCH/DECODE UNIT
// 3-STAGE PIPELINE" and a 64-bit path from the prefetch buffer; p. 1-32
// (section 1.10.1) gives the unit its next-PC/alternate-next-PC job.
//
// Each stage follows Flute's CPU_StageN_IFC convention
// (enq/deq/out/notEmpty plus a Server#(Token,Token) reset port); see
// docs/bluespec_architecture.md.  A stage's `full` register is its
// back-pressure, so back-pressure is a signal the stage itself raises and
// no separate stall register (Flute's `set_full`) is needed here.  The
// stages are passive registers with a combinational datapath, and the
// wiring between them lives in mkHobbitPdu, not in mkHobbitCore.
//
//   PDU_S1  latches the PC and reads three 64-bit prefetch lines
//           (the 64-bit path; three lines cover the 16-byte parcel
//           window for every even PC).
//   PDU_S2  selects the six parcels from those lines.
//   PDU_S3  decodes and packs the 192-bit entry (Table 1-15..1-20).
typedef struct {
  Word pc;
  Maybe#(Bit#(64)) l0;   // line containing pc & ~7
  Maybe#(Bit#(64)) l1;   // the next line
  Maybe#(Bit#(64)) l2;   // the third line (odd parcel start only)
  Bool fault;            // MMU fetch translation fault (p. 2-3)
} PduS1Out deriving (Bits);

typedef struct {
  Word pc;
  Bool miss;
  Bool fault;
  Vector#(6, Parcel) parcels;
} PduS2Out deriving (Bits);

typedef struct {
  Word pc;
  Bool miss;
  Bool fault;
  DecEntry entry;
} PduS3Out deriving (Bits);

function Bit#(64) pfcData(Maybe#(Bit#(64)) m);
  return isValid(m) ? validValue(m) : 0;
endfunction

function DecodedInstr fetchFaultInstr(Word pc);
  return DecodedInstr { pc: pc, plen: 1, op: OP_NONE,
                        src: Operand { mode: 4'h0, val: 0 },
                        dst: Operand { mode: 4'h0, val: 0 },
                        insn0: 0, insn1: 0,
                        fold: False, foldOp: OP_NONE, foldPc: 0,
                        foldInsn0: 0, foldTarget: 0, foldAfter: 0,
                        tr: TR_FETCH_FAULT, cpu: False };
endfunction

function DecodedInstr fetchMissInstr(Word pc);
  return DecodedInstr { pc: pc, plen: 1, op: OP_NONE,
                        src: Operand { mode: 4'h0, val: 0 },
                        dst: Operand { mode: 4'h0, val: 0 },
                        insn0: 0, insn1: 0,
                        fold: False, foldOp: OP_NONE, foldPc: 0,
                        foldInsn0: 0, foldTarget: 0, foldAfter: 0,
                        tr: TR_FETCH_MISS, cpu: False };
endfunction

// ---- PDU_S1: PC and the 64-bit prefetch lines -----------------------
interface HobbitPduS1;
  interface Server#(Token, Token) server_reset;
  method PduS1Out out;
  method Action deq;
  method Action enq(Word pc);
  method Bool notEmpty;
endinterface

module mkHobbitPduS1#(HobbitPrefetch pf)(HobbitPduS1);
  Reg#(Bool) full <- mkReg(False);
  Reg#(Word) pcR <- mkReg(0);
  FIFOF#(Token) f_reset_reqs <- mkFIFOF;
  FIFOF#(Token) f_reset_rsps <- mkFIFOF;

  rule rl_reset;
    f_reset_reqs.deq;
    full  <= False;
    f_reset_rsps.enq(?);
  endrule

  method PduS1Out out;
    Word a0 = pcR & 32'hFFFFFFF8;
    // lineAt(a0), lineAt(a0 + 8), lineAt(a0 + 16) and the OR of the three
    // faultAt()s, on two translations (HobbitPrefetch lines3).
    match { .l0, .l1, .l2, .f } = pf.lines3(a0);
    return PduS1Out { pc: pcR, l0: l0, l1: l1, l2: l2, fault: f };
  endmethod

  method Action enq(Word pc) if (!full);
    pcR  <= pc;
    full <= True;
    pf.noteFetch(pc);
  endmethod

  method Action deq if (full);
    full <= False;
  endmethod

  method Bool notEmpty() = full;

  interface Server server_reset;
    interface Put request  = toPut(f_reset_reqs);
    interface Get response = toGet(f_reset_rsps);
  endinterface
endmodule

// ---- PDU_S2: select the six parcels --------------------------------
interface HobbitPduS2;
  interface Server#(Token, Token) server_reset;
  method PduS2Out out;
  method Action deq;
  method Action enq(PduS1Out d);
  method Bool notEmpty;
endinterface

module mkHobbitPduS2(HobbitPduS2);
  Reg#(Bool) full <- mkReg(False);
  Reg#(PduS1Out) inR <- mkRegU;
  FIFOF#(Token) f_reset_reqs <- mkFIFOF;
  FIFOF#(Token) f_reset_rsps <- mkFIFOF;

  rule rl_reset;
    f_reset_reqs.deq;
    full  <= False;
    f_reset_rsps.enq(?);
  endrule

  // Four consecutive words cover the six parcels of any instruction at
  // an even address: pc[1] selects the half of the first word.
  function Vector#(6, Parcel) selEven(Word w0, Word w1, Word w2);
    Vector#(6, Parcel) a = replicate(0);
    Vector#(6, Parcel) b = update(a, 0, w0[31:16]);
    Vector#(6, Parcel) c = update(b, 1, w0[15:0]);
    Vector#(6, Parcel) d = update(c, 2, w1[31:16]);
    Vector#(6, Parcel) e = update(d, 3, w1[15:0]);
    Vector#(6, Parcel) f = update(e, 4, w2[31:16]);
    return update(f, 5, w2[15:0]);
  endfunction

  function Vector#(6, Parcel) selOdd(Word w0, Word w1, Word w2, Word w3);
    Vector#(6, Parcel) a = replicate(0);
    Vector#(6, Parcel) b = update(a, 0, w0[15:0]);
    Vector#(6, Parcel) c = update(b, 1, w1[31:16]);
    Vector#(6, Parcel) d = update(c, 2, w1[15:0]);
    Vector#(6, Parcel) e = update(d, 3, w2[31:16]);
    Vector#(6, Parcel) f = update(e, 4, w2[15:0]);
    return update(f, 5, w3[31:16]);
  endfunction

  method PduS2Out out;
    let d = inR;
    Word base = d.pc & 32'hFFFFFFFC;
    Bool oddBase = (base[2:0] == 3'b100);
    Bool have12 = isValid(d.l0) && isValid(d.l1);
    Bool miss = !have12 || (oddBase && !isValid(d.l2));
    Bit#(64) l0 = pfcData(d.l0);
    Bit#(64) l1 = pfcData(d.l1);
    Bit#(64) l2 = pfcData(d.l2);
    Word w0 = oddBase ? l0[31:0]  : l0[63:32];
    Word w1 = oddBase ? l1[63:32] : l0[31:0];
    Word w2 = oddBase ? l1[31:0]  : l1[63:32];
    Word w3 = oddBase ? l2[63:32] : l1[31:0];
    Vector#(6, Parcel) ps = (d.pc[1] == 1'b0)
                              ? selEven(w0, w1, w2)
                              : selOdd(w0, w1, w2, w3);
    return PduS2Out { pc: d.pc, miss: miss, fault: d.fault, parcels: ps };
  endmethod

  method Action enq(PduS1Out d) if (!full);
    inR  <= d;
    full <= True;
  endmethod

  method Action deq if (full);
    full <= False;
  endmethod

  method Bool notEmpty() = full;

  interface Server server_reset;
    interface Put request  = toPut(f_reset_reqs);
    interface Get response = toGet(f_reset_rsps);
  endinterface
endmodule

// ---- PDU_S3: decode and pack the 192-bit entry ----------------------
interface HobbitPduS3;
  interface Server#(Token, Token) server_reset;
  method PduS3Out out;
  method Action deq;
  method Action enq(PduS2Out d);
  method Bool notEmpty;
endinterface

module mkHobbitPduS3(HobbitPduS3);
  HobbitDecode dec <- mkHobbitDecode;

  Reg#(Bool) full <- mkReg(False);
  Reg#(PduS2Out) inR <- mkRegU;
  FIFOF#(Token) f_reset_reqs <- mkFIFOF;
  FIFOF#(Token) f_reset_rsps <- mkFIFOF;

  rule rl_reset;
    f_reset_reqs.deq;
    full  <= False;
    f_reset_rsps.enq(?);
  endrule

  method PduS3Out out;
    if (inR.fault)
      return PduS3Out { pc: inR.pc, miss: False, fault: True,
                        entry: packDecEntry(fetchFaultInstr(inR.pc)) };
    else if (inR.miss)
      return PduS3Out { pc: inR.pc, miss: True, fault: False,
                        entry: packDecEntry(fetchMissInstr(inR.pc)) };
    else
      return PduS3Out { pc: inR.pc, miss: False, fault: False,
                        entry: packDecEntry(dec.decode(inR.pc, inR.parcels)) };
  endmethod

  method Action enq(PduS2Out d) if (!full);
    inR  <= d;
    full <= True;
  endmethod

  method Action deq if (full);
    full <= False;
  endmethod

  method Bool notEmpty() = full;

  interface Server server_reset;
    interface Put request  = toPut(f_reset_reqs);
    interface Get response = toGet(f_reset_rsps);
  endinterface
endmodule

// ---- PDU: wire the three stages -------------------------------------
interface HobbitPdu;
  method Action enq(Word pc);
  method Bool accepting();
  method Bool outValid();
  method PduS3Out out();
  method Action deq();
endinterface

module mkHobbitPdu#(HobbitPrefetch pf)(HobbitPdu);
  HobbitPduS1 s1 <- mkHobbitPduS1(pf);
  HobbitPduS2 s2 <- mkHobbitPduS2;
  HobbitPduS3 s3 <- mkHobbitPduS3;

  rule s1ToS2 (s1.notEmpty && !s2.notEmpty);
    s2.enq(s1.out);
    s1.deq;
  endrule

  rule s2ToS3 (s2.notEmpty && !s3.notEmpty);
    s3.enq(s2.out);
    s2.deq;
  endrule

  method Action enq(Word pc) = s1.enq(pc);
  method Bool accepting() = !s1.notEmpty;
  method Bool outValid() = s3.notEmpty;
  method PduS3Out out() = s3.out;
  method Action deq() = s3.deq;
endmodule

// ---------------------------------------------------------------------
// The 32-entry decoded-instruction store (the "IC" of printed p. 4-2;
// Figure 1-1, printed p. 1-2, "DECODED INSTRUCTION CACHE 32X192bits").
// p. 1-1 fixes the organization: "32-entry, direct-mapped".
//
// The store is Vector#(32, DecEntry): exactly 32 entries of exactly 192
// bits, with the bit allocation documented in HobbitTypes.  An entry is
// full (decEntryFull) when a complete decoded instruction is present;
// that is also the hit condition, together with the 26-bit PC tag.  A
// collision re-decodes through the PDU at no occupancy cost, which the
// p. 4-1 in-cache assumption permits.  The store does not widen an
// entry for a decoded instruction the printed width cannot hold: the
// next/alternate-next pair is the documented overflow and is recomputed
// on read (HobbitTypes).
//
// The EU asks for an entry by PC; a hit returns it, a miss starts one
// PDU fill and the EU stalls until the install rule writes the entry.
// A fill is a p. 4-1 in-cache fetch, so it adds no occupancy cycles.
//
// When the PDU reports that the prefetch buffer lacked a line (`miss`),
// the store asks the buffer for a demand fill, drops that PDU result and
// decodes the same PC again once the fill has ended; the entry is
// installed from the second decode.  A PDU result for a PC the store is
// no longer waiting for (the store was reset mid-fill) is dropped, so it
// cannot sit in PDU_S3 in front of the next fill.
interface HobbitDecodeStore;
  method Maybe#(DecInstEntry) lookup(Word pc);
  method Action fill(Word pc);
  method Bool filling();
  method Action reset();
endinterface

module mkHobbitDecodeStore#(HobbitPdu pdu, HobbitPrefetch pf)(HobbitDecodeStore);
  // structure follows Flute (Bluespec, Inc., Apache-2.0) — see
  // docs/bluespec_architecture.md: a decoded-instruction box with a
  // lookup/fill boundary, separate from the EU pipeline.
  //
  // One write port and a combinational 32:1 read (the EU looks up by PC
  // every clock).  RegFile emits the plain array shape that maps to LUT
  // RAM: docs/area_analysis.md's reg_32x192 is 194 LUT4, against 4,498
  // LUT4 / 6,246 FF for a Vector written by update.  The RegFile starts
  // undefined, so a 32-bit valid mask gates every hit; the 192-bit
  // entry's `full` bit remains part of the printed allocation.
  RegFile#(Bit#(5), DecEntry) ic <- mkRegFileFull;
  Reg#(Bit#(32)) icValid <- mkReg(0);
  Reg#(Bool) fillingR <- mkReg(False);
  Reg#(Word) fillPc <- mkReg(0);
  // A demand fill of the prefetch buffer is under way for fillPc; the
  // PDU is asked again when it ends.
  Reg#(Bool) refillR <- mkReg(False);

  function Bit#(5) idx(Word pc) = truncate(pc >> 1);

  Bool mine = fillingR && !refillR && pdu.outValid() &&
              (pdu.out().pc == fillPc);

  rule install (mine && !pdu.out().miss);
    ic.upd(idx(fillPc), pdu.out().entry);
    icValid <= icValid | (1 << idx(fillPc));
    pdu.deq;
    fillingR <= False;
  endrule

  rule missed (mine && pdu.out().miss && !pf.filling());
    pf.demand(fillPc);
    pdu.deq;
    refillR <= True;
  endrule

  rule retry (fillingR && refillR && !pf.filling() && pdu.accepting());
    pdu.enq(fillPc);
    refillR <= False;
  endrule

  rule dropStale (pdu.outValid() &&
                  (!fillingR || refillR || (pdu.out().pc != fillPc)));
    pdu.deq;
  endrule

  method Maybe#(DecInstEntry) lookup(Word pc);
    let e = ic.sub(idx(pc));
    if ((icValid[idx(pc)] == 1'b1) && (e[188:163] == pc[31:6]))
      return tagged Valid (decEntryToInst(e, pc));
    else
      return tagged Invalid;
  endmethod

  method Action fill(Word pc);
    if (!fillingR && pdu.accepting()) begin
      fillingR <= True;
      fillPc   <= pc;
      pdu.enq(pc);
    end
  endmethod

  method Bool filling() = fillingR;

  method Action reset();
    icValid <= 0;
    fillingR <= False;
    refillR <= False;
  endmethod
endmodule

endpackage
