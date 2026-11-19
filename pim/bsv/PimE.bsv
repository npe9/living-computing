// PimE.bsv -- the PIM/m E stage as a microcoded, multi-cycle module.
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
// Timing scope: an instruction's microprogram occupies E for its
// length; the front end is held while E is not retiring.  This is the
// conservative interlock for a multi-cycle E, not a claim about the
// real PU's exact stage overlap.

package PimE;

import RegFile::*;
import Vector::*;
import PimTypes::*;
import PimALU::*;

interface StageE;
  method ActionValue#(Maybe#(Addr)) run(Bool doLoad, Bool advancePC, S2E s2e);
  method Action setPC(Maybe#(Addr) pc);
  method Bool canAccept();
  method Bool retired();
  method Bool valid();
  method Bool halted();
  method Bool error();
  method Maybe#(Addr) branchTarget();
  method Word readReg(RegSel r);
  method Addr pc();
endinterface

module mkStageE#(RegFile#(UPc, Bit#(64)) wcs,
                 RegFile#(Bit#(8), UPc) jumpTable,
                 RegFile#(Addr, Word) mem)(StageE);

  // Architectural state: An/Xn, WR control registers, SP and the
  // E-stage temporaries (p.427-428).
  Vector#(16, Reg#(Word)) aRegs <- replicateM(mkRegU);
  Vector#(16, Reg#(Word)) xRegs <- replicateM(mkRegU);
  Vector#(8,  Reg#(Word)) ctrl  <- replicateM(mkRegU);  // AP..FGP
  Reg#(Word) sp   <- mkRegU;
  Reg#(Word) mar1 <- mkRegU;
  Reg#(Word) mar2 <- mkRegU;
  Reg#(Word) mdr1 <- mkRegU;
  Reg#(Word) mdr2 <- mkRegU;
  Reg#(Word) xr   <- mkRegU;
  Reg#(Word) yr   <- mkRegU;
  Reg#(Addr) pcR  <- mkReg(0);

  // Microprogram state.
  Reg#(Bool) eValid <- mkReg(False);
  Reg#(DecodedInstr) eInstr <- mkRegU;
  Reg#(UPc) eUPC <- mkReg(0);
  Reg#(Bit#(2)) ePhase <- mkReg(0);
  Reg#(Word) eRs <- mkRegU;
  Reg#(Word) eRt <- mkRegU;
  Reg#(Word) eRd <- mkRegU;
  Reg#(Word) eFetched <- mkRegU;
  Reg#(Word) eDeref <- mkRegU;
  Reg#(Addr) eEA <- mkRegU;
  Reg#(Bool) eSRP <- mkReg(False);
  Reg#(Bool) eCOL <- mkReg(False);

  // Tag-jump second-cycle state.
  Reg#(Bool) ePendingTaken <- mkReg(False);
  Reg#(UPc)  ePendingTarget <- mkReg(0);
  Reg#(Bool) ePendingBranch <- mkReg(False);
  Reg#(Addr) ePendingBranchTarget <- mkRegU;

  // Bypass from the previous E microinstruction.
  Reg#(Bool) eLastWriteEn <- mkReg(False);
  Reg#(RegSel) eLastWriteDst <- mkReg(rselNone);
  Reg#(Word) eLastWriteVal <- mkRegU;

  Reg#(Bool) haltedR <- mkReg(False);
  Reg#(Bool) errorR  <- mkReg(False);

  function MicroInstr microNow() = unpackMicro(wcs.sub(eUPC));

  function RegSel resolveDst(RegSel d, Instr i);
    if (d == rselRd) return regFieldToSel(i.rd);
    else if (d == rselRs) return regFieldToSel(i.rs);
    else if (d == rselRt) return regFieldToSel(i.rt);
    else return d;
  endfunction

  function Word readRegFile(RegSel r);
    if (r < 16) return aRegs[r[3:0]];
    else if (r < 32) return xRegs[r[3:0]];
    else if (r < 40) return ctrl[r[2:0]];
    else if (r == rselSp)   return sp;
    else if (r == rselPc)   return mkWord(tagInt, False, zeroExtend(pcR));
    else if (r == rselMar1) return mar1;
    else if (r == rselMar2) return mar2;
    else if (r == rselMdr1) return mdr1;
    else if (r == rselMdr2) return mdr2;
    else if (r == rselXr)   return xr;
    else if (r == rselYr)   return yr;
    else return mkWord(tagInt, False, 0);
  endfunction

  function Word readRegForE(RegSel r);
    if (eLastWriteEn && (eLastWriteDst == r)) return eLastWriteVal;
    else return readRegFile(r);
  endfunction

  function Word srcValue(RegSel s);
    if (s == rselImm)   return mkWord(tagInt, False, zeroExtend(microNow().imm));
    else if (s == rselRs)    return eRs;
    else if (s == rselRt)    return eRt;
    else if (s == rselRd)    return eRd;
    else if (s == rselFetch) return eFetched;
    else if (s == rselDeref) return eDeref;
    else return readRegForE(s);
  endfunction

  function Word aluNow();
    let mi = microNow();
    return alu(mi.aluOp, srcValue(mi.srcA), srcValue(mi.srcB));
  endfunction

  function Word resultNow();
    let mi = microNow();
    let r0 = aluNow();
    let r1 = mi.mrbSet ? mkWord(tagType(wordTag(r0)), True,  wordData(r0)) : r0;
    let r2 = mi.mrbClr ? mkWord(tagType(wordTag(r1)), False, wordData(r1)) : r1;
    return r2;
  endfunction

  // readReg is the value the A and S stages see.  It forwards the
  // instruction currently in E, so a dependent instruction behind a
  // one-microinstruction E does not read the old register.
  function Word readRegBypassed(RegSel r);
    let mi = microNow();
    let dst = resolveDst(mi.dst, eInstr.instr);
    if (eValid && (mi.dst != rselNone) && (dst == r))
      return resultNow();
    else
      return readRegFile(r);
  endfunction

  function Action writeReg(RegSel r, Word v);
    action
      if (r < 16) aRegs[r[3:0]] <= v;
      else if (r < 32) xRegs[r[3:0]] <= v;
      else if (r < 40) ctrl[r[2:0]] <= v;
      else if (r == rselSp)   sp <= v;
      else if (r == rselMar1) mar1 <= v;
      else if (r == rselMar2) mar2 <= v;
      else if (r == rselMdr1) mdr1 <= v;
      else if (r == rselMdr2) mdr2 <= v;
      else if (r == rselXr)   xr <= v;
      else if (r == rselYr)   yr <= v;
    endaction
  endfunction

  function Bool evalCond(Cond c, Word av);
    case (c)
      condAlways:     return True;
      condNever:      return False;
      condTagEq:     return tagType(wordTag(av)) == eInstr.instr.imm[6:0];
      condTagNe:     return tagType(wordTag(av)) != eInstr.instr.imm[6:0];
      condTagRef:    return tagType(wordTag(av)) == tagRef;
      condTagNotRef: return tagType(wordTag(av)) != tagRef;
      condMultiway:   return True;
      condZero:       return av == mkWord(tagInt, False, 0);
    endcase
  endfunction

  function Bool retireNow();
    if (!eValid) return False;
    else if (ePhase == 0) return microNow().last && !isTagCond(microNow().cond);
    else return microNow().last;
  endfunction

  method ActionValue#(Maybe#(Addr)) run(Bool doLoad, Bool advancePC, S2E s2e);
    if (eValid) begin
      let mi = microNow();
      let av = srcValue(mi.srcA);
      let dst = resolveDst(mi.dst, eInstr.instr);
      let r = resultNow();

      if (dst != rselNone) begin
        writeReg(dst, r);
        eLastWriteEn  <= True;
        eLastWriteDst <= dst;
        eLastWriteVal <= r;
      end else begin
        eLastWriteEn <= False;
      end

      if (mi.memOp == memWrite) mem.upd(eEA, av);
      if (mi.halt) haltedR <= True;

      if (ePhase == 0) begin
        let taken = evalCond(mi.cond, av);
        if (isTagCond(mi.cond)) begin
          ePhase <= 1;
          ePendingTaken  <= taken;
          ePendingTarget <= (mi.cond == condMultiway)
                              ? eUPC + jumpTable.sub(zeroExtend(tagType(wordTag(av))))
                              : mi.next;
          ePendingBranch <= mi.branch && taken;
          ePendingBranchTarget <= truncate(wordData(eRt));
          return Invalid;
        end else begin
          eUPC <= taken ? mi.next : eUPC + 1;
          if (mi.last) eValid <= False;
          if (mi.branch && taken) return Valid(truncate(wordData(eRt)));
          else return Invalid;
        end
      end else begin
        ePhase <= 0;
        eUPC <= ePendingTaken ? ePendingTarget : eUPC + 1;
        if (mi.last) eValid <= False;
        if (ePendingBranch) return Valid(ePendingBranchTarget);
        else return Invalid;
      end
    end else if (doLoad) begin
      if (!s2e.dec.valid) begin
        // Fail loud: an undefined opcode stops the model with error set.
        errorR  <= True;
        haltedR <= True;
        eValid  <= False;
      end else begin
        eValid   <= True;
        eInstr   <= DecodedInstr { instr: s2e.instr, dec: s2e.dec };
        eUPC     <= s2e.dec.uBase;
        ePhase   <= 0;
        eRs      <= s2e.rsVal;
        eRt      <= s2e.rtVal;
        eRd      <= s2e.rdVal;
        eFetched <= s2e.fetched;
        eDeref   <= s2e.derefVal;
        eEA      <= s2e.ea;
        eSRP     <= s2e.srp;
        eCOL     <= s2e.col;
      end
      return Valid(pcR + 1);
    end else if (advancePC) begin
      return Valid(pcR + 1);
    end else begin
      return Invalid;
    end
  endmethod

  method Action setPC(Maybe#(Addr) pc);
    if (isValid(pc)) pcR <= validValue(pc);
  endmethod

  method Bool canAccept() = (!eValid) || retireNow();
  method Bool retired() = retireNow();
  method Bool valid() = eValid;
  method Bool halted() = haltedR;
  method Bool error() = errorR;

  method Maybe#(Addr) branchTarget();
    if (!eValid) return Invalid;
    else if (ePhase == 0) begin
      let mi = microNow();
      if (mi.branch && !isTagCond(mi.cond)) begin
        let av = srcValue(mi.srcA);
        if (evalCond(mi.cond, av)) return Valid(truncate(wordData(eRt)));
        else return Invalid;
      end else return Invalid;
    end else begin
      if (ePendingBranch) return Valid(ePendingBranchTarget);
      else return Invalid;
    end
  endmethod

  method Word readReg(RegSel r) = readRegBypassed(r);
  method Addr pc() = pcR;
endmodule

endpackage
