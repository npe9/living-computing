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
import FIFOF::*;
import GetPut::*;
import ClientServer::*;
import RegFile::*;
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
// every address the tests use.  There is no on-demand fill engine in
// this milestone: a fetch whose line is absent is a model limitation,
// and the PDU turns it into TR_FETCH_MISS so the core retires a loud
// trap record rather than aliasing a line silently.  A fetch that hits
// costs nothing extra: the p. 4-1 assumption "instruction fetches must
// access in the instruction cache" is adopted, so no Table 4-37 fetch
// delay is charged.
interface HobbitPrefetch;
  method Action startFill();
  method Bool filling();
  method Bool ready();
  method Maybe#(Bit#(64)) lineAt(Word addr);
endinterface

typedef struct {
  Bit#(22) tag;      // addr[31:10]
  Bit#(64) data;     // {word at line+0, word at line+4}
} PfcLine deriving (Bits);

module mkHobbitPrefetch#(HobbitMem mem)(HobbitPrefetch);
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
  Reg#(Bool) fillingR <- mkReg(False);
  Reg#(Bool) readyR <- mkReg(False);

  // One 64-bit line per three clocks: request the low word, capture it
  // and request the high word, capture it and install the line.
  rule fillStep (fillingR);
    Word lineAddr = zeroExtend(fillSet) << 3;
    case (fillPhase)
      2'd0: begin
        mem.readReq(lineAddr);
        fillPhase <= 2'd1;
      end
      2'd1: begin
        fillLo <= mem.readData();
        mem.readReq(lineAddr + 4);
        fillPhase <= 2'd2;
      end
      default: begin
        Bit#(64) line = { fillLo, mem.readData() };
        PfcLine l = PfcLine { tag: lineAddr[31:10], data: line };
        way0.upd(fillSet, l);
        valid0 <= valid0 | (128'd1 << fillSet);
        if (fillSet == 7'd127) begin
          fillingR <= False;
          readyR   <= True;
        end else begin
          fillSet   <= fillSet + 1;
          fillPhase <= 2'd0;
        end
      end
    endcase
  endrule

  method Action startFill();
    if (!fillingR && !readyR) begin
      fillSet   <= 0;
      fillPhase <= 0;
      fillingR  <= True;
    end
  endmethod

  method Bool filling() = fillingR;
  method Bool ready()   = readyR;

  method Maybe#(Bit#(64)) lineAt(Word addr);
    Bit#(7) set = addr[9:3];
    Bit#(22) tag = addr[31:10];
    PfcLine a0 = way0.sub(set);
    PfcLine a1 = way1.sub(set);
    PfcLine a2 = way2.sub(set);
    Maybe#(Bit#(64)) r = tagged Invalid;
    if ((valid0[set] == 1'b1) && (a0.tag == tag))
      r = tagged Valid a0.data;
    else if ((valid1[set] == 1'b1) && (a1.tag == tag))
      r = tagged Valid a1.data;
    else if ((valid2[set] == 1'b1) && (a2.tag == tag))
      r = tagged Valid a2.data;
    return r;
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
} PduS1Out deriving (Bits);

typedef struct {
  Word pc;
  Bool miss;
  Vector#(6, Parcel) parcels;
} PduS2Out deriving (Bits);

typedef struct {
  Word pc;
  Bool miss;
  DecEntry entry;
} PduS3Out deriving (Bits);

function Bit#(64) pfcData(Maybe#(Bit#(64)) m);
  return isValid(m) ? validValue(m) : 0;
endfunction

function DecodedInstr fetchMissInstr(Word pc);
  return DecodedInstr { pc: pc, plen: 1, op: OP_NONE,
                        src: Operand { kind: OK_NONE, val: 0 },
                        dst: Operand { kind: OK_NONE, val: 0 },
                        insn0: 0, insn1: 0,
                        fold: False, foldOp: OP_NONE, foldPc: 0,
                        foldInsn0: 0, foldTarget: 0, foldAfter: 0,
                        tr: TR_FETCH_MISS };
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
    return PduS1Out { pc: pcR,
                      l0: pf.lineAt(a0),
                      l1: pf.lineAt(a0 + 8),
                      l2: pf.lineAt(a0 + 16) };
  endmethod

  method Action enq(Word pc) if (!full);
    pcR  <= pc;
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
    return PduS2Out { pc: d.pc, miss: miss, parcels: ps };
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
    if (inR.miss)
      return PduS3Out { pc: inR.pc, miss: True,
                        entry: packDecEntry(fetchMissInstr(inR.pc)) };
    else
      return PduS3Out { pc: inR.pc, miss: False,
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
interface HobbitDecodeStore;
  method Maybe#(DecInstEntry) lookup(Word pc);
  method Action fill(Word pc);
  method Bool filling();
  method Action reset();
endinterface

module mkHobbitDecodeStore#(HobbitPdu pdu)(HobbitDecodeStore);
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

  function Bit#(5) idx(Word pc) = truncate(pc >> 1);

  rule install (fillingR && pdu.outValid() && (pdu.out().pc == fillPc));
    ic.upd(idx(fillPc), pdu.out().entry);
    icValid <= icValid | (1 << idx(fillPc));
    pdu.deq;
    fillingR <= False;
  endrule

  method Maybe#(DecInstEntry) lookup(Word pc);
    let e = ic.sub(idx(pc));
    if ((icValid[idx(pc)] == 1'b1) && (e[191:166] == pc[31:6]))
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
  endmethod
endmodule

endpackage
