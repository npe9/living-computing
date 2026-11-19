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
// Addressing modes: smode/dmode 0xF immediate, 0xD word stack offset,
// 0xC word absolute (Tables 1-21/1-22, p. 1-25/1-26).  Byte and half-word
// modes and indirect modes are decoded as TR_BAD_MODE: the source
// documents them, this milestone does not model them, and the core traps.
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
import HobbitTypes::*;

interface HobbitDecode;
  method DecodedInstr decode(Word pc, Vector#(6, Parcel) p);
endinterface

module mkHobbitDecode(HobbitDecode);

  function Operand noOpnd();
    return Operand { kind: OK_NONE, val: 0 };
  endfunction

  function DecodedInstr mkInstr(Word pc, Bit#(8) len, HobbitOp op,
                                Operand s, Operand d, TrapReason tr);
    return DecodedInstr { pc: pc, plen: len, op: op, src: s, dst: d,
                          insn0: 0, insn1: 0,
                          fold: False, foldOp: OP_NONE, foldPc: 0,
                          foldInsn0: 0, foldTarget: 0,
                          foldAfter: 0, tr: tr };
  endfunction

  function DecodedInstr trapAt(Word pc, Bit#(8) len, TrapReason r);
    return mkInstr(pc, len, OP_NONE, noOpnd(), noOpnd(), r);
  endfunction

  function DecodedInstr unary(Word pc, Bit#(8) len, HobbitOp op,
                              OperandKind k, Word v, TrapReason r);
    return mkInstr(pc, len, op, Operand { kind: k, val: v }, noOpnd(), r);
  endfunction

  // A 10-bit PC-relative field is signed and multiplied by two
  // (p. 1-22), relative to the address of the instruction itself
  // (p. 1-27).
  function Word pcrel10(Word pc, Bit#(10) off);
    return pc + (signExtend(off) << 1);
  endfunction

  function Word imm5(Bit#(5) v) = signExtend(v);
  function Word stk5(Bit#(5) v) = zeroExtend(v) << 2;

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
                   Operand { kind: OK_ABS, val: pcrel10(pc, q[9:0]) },
                   noOpnd(), TR_NONE);
  endfunction

  // Table 1-16: stack subcode 00 ENTER, 01 CATCH, 10 RETURN, 11 POPN.
  // ENTER's eight-bit offset is one-filled and multiplied by 16; the
  // others are zero filled and multiplied by 16 (p. 1-22, p. 3-20).
  function DecodedInstr stack1(Word pc, Parcel q);
    Bit#(2) sub = q[1:0];
    Bit#(8) off = q[9:2];
    case (sub)
      2'd0: return unary(pc, 1, OP_ENTER,  OK_STACK,
                         signExtend(off) << 4, TR_NONE);
      2'd1: return unary(pc, 1, OP_CATCH,  OK_STACK,
                         zeroExtend(off) << 4, TR_NONE);
      2'd2: return unary(pc, 1, OP_RETURN, OK_STACK,
                         zeroExtend(off) << 4, TR_NONE);
      default: return unary(pc, 1, OP_POPN, OK_STACK,
                            zeroExtend(off) << 4, TR_NONE);
    endcase
  endfunction

  // Table 1-17: CPU = 0x000, NOP = 0x002.  CPU is a documented escape
  // (p. 3-14) and is rejected explicitly; every other niladic is unimp.
  function DecodedInstr niladic1(Word pc, Parcel q);
    Bit#(10) sub = q[9:0];
    if (sub == 10'h002)
      return unary(pc, 1, OP_NOP, OK_NONE, 0, TR_NONE);
    else if (sub == 10'h000)
      return trapAt(pc, 1, TR_CPU);
    else
      return trapAt(pc, 1, TR_UNIMP);
  endfunction

  function DecodedInstr dyad1(Word pc, HobbitOp op, Parcel q);
    return mkInstr(pc, 1, op,
                   Operand { kind: OK_IMM,   val: imm5(q[9:5]) },
                   Operand { kind: OK_STACK, val: stk5(q[4:0]) },
                   TR_NONE);
  endfunction

  function DecodedInstr dyad1ss(Word pc, HobbitOp op, Parcel q);
    return mkInstr(pc, 1, op,
                   Operand { kind: OK_STACK, val: stk5(q[9:5]) },
                   Operand { kind: OK_STACK, val: stk5(q[4:0]) },
                   TR_NONE);
  endfunction

  // MOV.WS (opcode 0x0A, Table 1-15 p. 1-22; p. 3-32): the source is the
  // unsigned `wai5` field multiplied by four (Table 3-2 p. 3-4), and the
  // 5-bit stack offset is zero-extended and multiplied by four (p. 1-22).
  function DecodedInstr movws1(Word pc, Parcel q);
    return mkInstr(pc, 1, OP_MOV,
                   Operand { kind: OK_IMM, val: zeroExtend(q[9:5]) << 2 },
                   Operand { kind: OK_STACK, val: stk5(q[4:0]) },
                   TR_NONE);
  endfunction

  // Three-parcel gen16 / five-parcel gen32 operand modes.
  function Bool modeOK(Bit#(4) m);
    return m == 4'hF || m == 4'hD || m == 4'hC;
  endfunction

  function Operand gen16(Bit#(4) m, Parcel v);
    case (m)
      4'hF: return Operand { kind: OK_IMM,   val: signExtend(v) };
      4'hD: return Operand { kind: OK_STACK, val: signExtend(v) };
      default: return Operand { kind: OK_ABS, val: zeroExtend(v) };
    endcase
  endfunction

  function Operand gen32(Bit#(4) m, Word v);
    case (m)
      4'hF: return Operand { kind: OK_IMM,   val: v };
      4'hD: return Operand { kind: OK_STACK, val: v };
      default: return Operand { kind: OK_ABS, val: v };
    endcase
  endfunction

  // Table 1-23, p. 1-26: CALL/JMP may be PC relative (0xE) or absolute
  // (0xF) in this model; the indirect forms (0xC, 0xD) trap.
  function DecodedInstr branch3(Word pc, HobbitOp op, Bit#(4) m, Word v, Bit#(8) len);
    case (m)
      4'hE: return mkInstr(pc, len, op,
                           Operand { kind: OK_ABS, val: pc + v },
                           noOpnd(), TR_NONE);
      4'hF: return mkInstr(pc, len, op,
                           Operand { kind: OK_ABS, val: v },
                           noOpnd(), TR_NONE);
      default: return trapAt(pc, len, TR_BAD_MODE);
    endcase
  endfunction

  function HobbitOp dyadicOp(Bit#(6) o);
    case (o)
      6'h06: return OP_MOV;
      6'h23: return OP_ADD;
      6'h20: return OP_SUB;
      6'h1F: return OP_CMPEQ;
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
                            foldAfter: bpc + 2, tr: d.tr };
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
        5'h01: return branch1(pc, OP_CALL, p0);
        5'h02: return maybeFold(stack1(pc, p0), p);
        5'h03: return branch1(pc, OP_JMP, p0);
        5'h04: return branch1(pc, OP_JMPFN, p0);
        5'h05: return branch1(pc, OP_JMPFY, p0);
        5'h06: return branch1(pc, OP_JMPTN, p0);
        5'h07: return branch1(pc, OP_JMPTY, p0);
        5'h0A: return maybeFold(movws1(pc, p0), p);
        5'h0B: return maybeFold(niladic1(pc, p0), p);
        5'h10: return maybeFold(dyad1(pc, OP_CMPEQ, p0), p);
        5'h11: return maybeFold(dyad1ss(pc, OP_CMPGT, p0), p);
        5'h12: return maybeFold(dyad1(pc, OP_CMPGT, p0), p);
        5'h13: return maybeFold(dyad1ss(pc, OP_CMPEQ, p0), p);
        5'h14: return maybeFold(dyad1(pc, OP_ADD, p0), p);
        5'h15: return maybeFold(dyad1(pc, OP_ADD3, p0), p);
        5'h16: return maybeFold(dyad1ss(pc, OP_ADD, p0), p);
        5'h17: return maybeFold(dyad1ss(pc, OP_ADD3, p0), p);
        5'h18: return maybeFold(dyad1ss(pc, OP_MOV, p0), p);
        5'h1C: return maybeFold(dyad1(pc, OP_MOV, p0), p);
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
                                 Operand { kind: OK_STACK, val: v32 },
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
                                 Operand { kind: OK_STACK, val: v32 },
                                 noOpnd(), TR_NONE);
                else if (sm == 4'hF)
                  return mkInstr(pc, 3, OP_CATCH,
                                 Operand { kind: OK_IMM, val: v32 },
                                 noOpnd(), TR_NONE);
                else
                  return trapAt(pc, 3, TR_BAD_MODE);
          4'h9: if (sm == 4'hD)
                  return mkInstr(pc, 3, OP_ENTER,
                                 Operand { kind: OK_STACK, val: v32 },
                                 noOpnd(), TR_NONE);
                else if (sm == 4'hF)
                  return mkInstr(pc, 3, OP_ENTER,
                                 Operand { kind: OK_IMM, val: v32 },
                                 noOpnd(), TR_NONE);
                else
                  return trapAt(pc, 3, TR_BAD_MODE);
          4'hF: if (sm == 4'hD)
                  return mkInstr(pc, 3, OP_POPN,
                                 Operand { kind: OK_STACK, val: v32 },
                                 noOpnd(), TR_NONE);
                else
                  return trapAt(pc, 3, TR_BAD_MODE);
          4'h0: return trapAt(pc, 3, TR_UNIMP);  // KCALL, unmodelled
          default: return trapAt(pc, 3, TR_UNIMP);
        endcase
      end else begin
        HobbitOp op = dyadicOp(opc);
        if (op == OP_NONE)
          return trapAt(pc, 3, TR_UNIMP);
        else if (!modeOK(sm) || !modeOK(dm))
          return trapAt(pc, 3, TR_BAD_MODE);
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
      else begin
        HobbitOp op = dyadicOp(opc);
        if (op == OP_NONE)
          return trapAt(pc, 5, TR_UNIMP);
        else if (!modeOK(sm) || !modeOK(dm))
          return trapAt(pc, 5, TR_BAD_MODE);
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
  method DecodedInstr decode(Word pc, Vector#(6, Parcel) p);
    let d = decodeRaw(pc, p);
    return DecodedInstr { pc: d.pc, plen: d.plen, op: d.op,
                          src: d.src, dst: d.dst,
                          insn0: p[0],
                          insn1: (d.plen == 8'd1) ? 16'd0 : p[1],
                          fold: d.fold, foldOp: d.foldOp,
                          foldPc: d.foldPc, foldInsn0: d.foldInsn0,
                          foldTarget: d.foldTarget, foldAfter: d.foldAfter,
                          tr: d.tr };
  endmethod

endmodule

endpackage
