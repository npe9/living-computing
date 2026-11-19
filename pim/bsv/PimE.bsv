// PimE.bsv -- the PIM/m E stage as a microcoded, multi-cycle box.
//
// Documented basis:
//   * E has two pipelined phases controlled by microinstructions; the
//     first phase holds An/Xn, WR and PC/SP, the second XR/YR, MAR1/2
//     and MDR1/2 (p.428, section 2.3).
//   * ALU operation and tag manipulation including MRB on/off run in
//     parallel (p.428).
//   * Two-way, three-way and multi-way tag jumps; "These operations
//     requires two machine cycles.  The first cycle makes the jump
//     condition or offset, and the second generates the jump address
//     and fetches the microinstruction" (p.428, section 2.4).
//   * The WCS is 32K x 64 bits (p.426).
//
// Model-defined, because the sources do not give the bit assignments:
// the 64-bit microinstruction layout (PimTypes), the micro-op set, and
// the branch target convention (a taken branch writes PC from the
// instruction's rt operand).
//
// Interface: the box is driven by a single `cycle` request.  Given the
// S-stage result it either loads a new instruction or executes exactly
// one microinstruction, so no caller-side if/else decides which of two
// actions owns the microprogram counter.  The PC belongs to the fetch
// stage; a taken branch is returned as a redirect.
//
// Timing scope: an instruction's microprogram occupies E for its
// length; the front end is held while E is not empty.  This is the
// conservative interlock for a multi-cycle E, not a claim about the
// real PU's exact stage overlap.

package PimE;

import RegFile::*;
import PimTypes::*;
import PimALU::*;
import PimStages::*;

interface StageE;
  // One pipeline cycle.  With an empty E and a valid instruction the
  // box loads it; with a loaded instruction it executes one
  // microinstruction.  Returns a PC redirect when a branch is taken.
  method ActionValue#(Maybe#(Addr)) cycle(Maybe#(S2E) in);
  method Bool busy();
  method Bool haltReq();        // the microinstruction in E halts the PU
  method Bool errorReq();       // an undefined opcode reached E
  method Bool stopped();        // E has halted or faulted; stop loading
  method Bool isStore();        // a store occupies E (memory ordering)
  // Register hazard queries for the pipeline interlock: the register an
  // instruction will write, and whether an instruction reads a register.
  method RegSel dstOf(DecodedInstr d);
  method Bool reads(DecodedInstr d, RegSel r);
endinterface

module mkStageE#(PimRegFile regs, LocalStore mem,
                 RegFile#(UPc, Bit#(64)) wcs,
                 RegFile#(Bit#(8), UPc) jumpTable)(StageE);

  // Microprogram state.
  Reg#(Bool) eValid <- mkReg(False);
  Reg#(DecodedInstr) eInstr <- mkReg(noDecodedInstr());
  Reg#(UPc) eUPC <- mkReg(0);
  Reg#(Bit#(2)) ePhase <- mkReg(0);
  Reg#(Word) eRs <- mkReg(0);
  Reg#(Word) eRt <- mkReg(0);
  Reg#(Word) eRd <- mkReg(0);
  Reg#(Maybe#(Word)) eFetched <- mkReg(Invalid);
  Reg#(Word) eDeref <- mkReg(0);
  Reg#(Addr) eEA <- mkReg(0);

  // Second cycle of a tag jump.
  Reg#(Bool) ePendingTaken <- mkReg(False);
  Reg#(UPc)  ePendingTarget <- mkReg(0);
  Reg#(Bool) ePendingBranch <- mkReg(False);
  Reg#(Addr) ePendingBranchTarget <- mkReg(0);

  // Run-ending requests, latched for the top-level rules.
  Reg#(Bool) haltSeen <- mkReg(False);
  Reg#(Bool) errorSeen <- mkReg(False);

  function MicroInstr microNow() = unpackMicro(wcs.sub(eUPC));

  function RegSel resolveDst(RegSel d, Instr i);
    if (d == rselRd) return regFieldToSel(i.rd);
    else if (d == rselRs) return regFieldToSel(i.rs);
    else if (d == rselRt) return regFieldToSel(i.rt);
    else return d;
  endfunction

  function Word srcValue(RegSel s);
    if (s == rselImm)        return mkWord(tagInt, False, zeroExtend(eInstr.instr.imm));
    else if (s == rselRs)    return eRs;
    else if (s == rselRt)    return eRt;
    else if (s == rselRd)    return eRd;
    else if (s == rselFetch) return fromMaybe(wordInt(0), eFetched);
    else if (s == rselDeref) return eDeref;
    else return regs.read(s);
  endfunction

  // ALU result with the microinstruction's MRB manipulation (p.429).
  function Word resultNow(Word av);
    let mi = microNow();
    let r0 = alu(mi.aluOp, av, srcValue(mi.srcB));
    let r1 = mi.mrbSet ? mkWord(tagType(wordTag(r0)), True,  wordData(r0)) : r0;
    let r2 = mi.mrbClr ? mkWord(tagType(wordTag(r1)), False, wordData(r1)) : r1;
    return r2;
  endfunction

  // Tag policy (docs/pim_architecture.md "Contradicted" item 1): the
  // multi-way jump indexes the full 8-bit tag; condTagEq/condTagNe
  // compare the 7-bit type because the assembler's jmp_tag immediate
  // carries a tag type; condTagRef/condTagNotRef are type tests and
  // likewise ignore MRB.
  function Bool evalCond(Cond c, Word av);
    case (c)
      condAlways:     return True;
      condNever:      return False;
      condTagEq:      return tagType(wordTag(av)) == eInstr.instr.imm[6:0];
      condTagNe:      return tagType(wordTag(av)) != eInstr.instr.imm[6:0];
      condTagRef:     return tagType(wordTag(av)) == tagRef;
      condTagNotRef:  return tagType(wordTag(av)) != tagRef;
      condMultiway:   return True;
      condZero:       return av == mkWord(tagInt, False, 0);
    endcase
  endfunction

  method ActionValue#(Maybe#(Addr)) cycle(Maybe#(S2E) in);
    if (eValid) begin
      let mi = microNow();
      if (ePhase == 1) begin
        // Second cycle of a tag jump: form the address and the PC
        // redirect only; the first cycle already did the data effects.
        ePhase <= 0;
        eUPC <= ePendingTaken ? ePendingTarget : eUPC + 1;
        if (mi.last) eValid <= False;
        return ePendingBranch ? Valid(ePendingBranchTarget) : Invalid;
      end else begin
        // First cycle: the data effects happen here and only here.
        let av    = srcValue(mi.srcA);
        let dst   = resolveDst(mi.dst, eInstr.instr);
        let taken = evalCond(mi.cond, av);
        if (dst != rselNone) regs.write(dst, resultNow(av));
        if (mi.memOp == memWrite) mem.write(eEA, av);
        if (mi.halt) haltSeen <= True;
        if (isTagCond(mi.cond)) begin
          // A tag jump spends its first cycle on the condition or offset.
          ePhase <= 1;
          ePendingTaken <= taken;
          ePendingTarget <= (mi.cond == condMultiway)
                              ? eUPC + jumpTable.sub(wordTag(av))
                              : mi.next;
          ePendingBranch <= mi.branch && taken;
          ePendingBranchTarget <= truncate(wordData(eRt));
          return Invalid;
        end else begin
          eUPC <= taken ? mi.next : eUPC + 1;
          if (mi.last) eValid <= False;
          return (mi.branch && taken) ? Valid(truncate(wordData(eRt))) : Invalid;
        end
      end
    end else case (in) matches
      tagged Valid .x:
        if (!x.d.dec.valid) begin
          // Fail loud: an undefined opcode stops the model with error set.
          errorSeen <= True;
          return Invalid;
        end else begin
          eValid <= True;
          eInstr <= x.d;
          eUPC   <= x.d.dec.uBase;
          ePhase <= 0;
          eRs    <= x.rsVal;
          eRt    <= x.rtVal;
          eRd    <= x.rdVal;
          eFetched <= x.fetched;
          eDeref <= x.derefVal;
          eEA    <= x.ea;
          return Invalid;
        end
      tagged Invalid: return Invalid;
    endcase
  endmethod

  method Bool busy() = eValid;
  method Bool haltReq() = eValid && microNow().halt;
  method Bool errorReq() = errorSeen;
  // E has executed a halt microinstruction or seen an undefined opcode;
  // the pipeline stops loading from this point on.
  method Bool stopped() = haltSeen || errorSeen;
  method Bool isStore() = eValid && eInstr.dec.isStore;

  method RegSel dstOf(DecodedInstr d);
    if (d.dec.valid) begin
      let mi = unpackMicro(wcs.sub(d.dec.uBase));
      return resolveDst(mi.dst, d.instr);
    end else return rselNone;
  endmethod

  method Bool reads(DecodedInstr d, RegSel r);
    if (d.dec.valid) begin
      let mi = unpackMicro(wcs.sub(d.dec.uBase));
      let sA = resolveDst(mi.srcA, d.instr);
      let sB = resolveDst(mi.srcB, d.instr);
      Bool baseRead = d.dec.needsEA && (regFieldToSel(d.instr.rs) == r);
      Bool derefRead = d.dec.deref && (regFieldToSel(d.instr.rs) == r);
      Bool branchRead = mi.branch && (regFieldToSel(d.instr.rt) == r);
      return (sA == r) || (sB == r) || baseRead || derefRead || branchRead;
    end else return False;
  endmethod

endmodule

endpackage
