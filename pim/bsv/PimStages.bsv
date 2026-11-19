// PimStages.bsv -- the PIM/m processing element's D, A, R and S stages,
// its architectural register file and its local store, each as a module
// with its own state.
//
// Documented behaviour modelled here:
//
//   D  "has a RAM table for instruction decode.  Each entry of the
//       table contains the start address of the microprogram routine
//       for an instruction"                                      p.428
//   A  "calculates the operand address by adding two of ... an
//       operand field of the instruction ... An/Xn ... CGP ... PC" p.428
//   R  "fetches an operand from data cache using the calculated
//       address, if necessary"                                    p.428
//   S  "examines the tag of fetched data, and repeatedly reads memory
//       until a non-reference data is obtained.  The state of the
//       reference path indicated by MRB ... is also examined"     p.429
//
// The S stage's SRP/COL definitions are from section 3.1, p.430:
//   SRP -- MRBs of all the pointers on the chain are off.
//   COL -- MRBs of the first two pointers are off.
//
// Pipeline shape: every stage owns the register that carries its result
// and exposes one action that either fills it or clears it, plus one
// query for whether the stage holds an instruction.  No pipeline
// register therefore has two writers, and the top-level rule only moves
// bundles between stages.
//
// PC lives in the register file because the documents call it a
// hardware counter alongside SP (p.427); the D stage advances it.

package PimStages;

import RegFile::*;
import Vector::*;
import PimTypes::*;

// ---------------------------------------------------------------------
// Local store: one write port, any number of read ports.
// ---------------------------------------------------------------------

interface LocalStore;
  method Word read(Addr a);
  method Bool miss(Addr a);          // granule not resident: hold and fetch
  method Action fetch(Addr a);       // request the granule containing a
  method Action write(Addr a, Word w);
endinterface

module mkLocalStore#(String image) (LocalStore);
  RegFile#(Addr, Word) mem <- mkRegFileLoadHex(image, 0, 65535);
  method Word read(Addr a) = mem.sub(a);
  method Bool miss(Addr a) = False;
  method Action fetch(Addr a) = noAction;
  method Action write(Addr a, Word w) = mem.upd(a, w);
endmodule

// ---------------------------------------------------------------------
// Architectural register file: An, Xn, the WR control registers
// (p.427), SP, PC, and the E-stage temporaries MAR1/2, MDR1/2, XR, YR
// (p.428).
// ---------------------------------------------------------------------

interface PimRegFile;
  method Word read(RegSel r);
  method Action write(RegSel r, Word v);
  method Bool badWrite();       // a microinstruction named an unwritable register
  method Addr pc();
  method Action pcNext(Maybe#(Addr) redirect);
endinterface

module mkPimRegFile(PimRegFile);

  Vector#(16, Reg#(Word)) aRegs <- replicateM(mkReg(0));
  Vector#(16, Reg#(Word)) xRegs <- replicateM(mkReg(0));
  Vector#(8,  Reg#(Word)) ctrl  <- replicateM(mkReg(0));  // AP..FGP
  Reg#(Word) sp   <- mkReg(0);
  Reg#(Word) mar1 <- mkReg(0);
  Reg#(Word) mar2 <- mkReg(0);
  Reg#(Word) mdr1 <- mkReg(0);
  Reg#(Word) mdr2 <- mkReg(0);
  Reg#(Word) xr   <- mkReg(0);
  Reg#(Word) yr   <- mkReg(0);
  Reg#(Addr) pcR  <- mkReg(0);
  Reg#(Bool) badW <- mkReg(False);

  function Word fileRead(RegSel r);
    if (r < 16)      return aRegs[r[3:0]];
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
    else return wordInt(0);   // source pseudo-selectors have no file state
  endfunction

  method Word read(RegSel r) = fileRead(r);

  method Action write(RegSel r, Word v);
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
    else badW <= True;        // PC and the source pseudo-selectors are not writable
  endmethod

  method Bool badWrite() = badW;
  method Addr pc() = pcR;

  method Action pcNext(Maybe#(Addr) redirect);
    if (isValid(redirect)) pcR <= validValue(redirect);
    else pcR <= pcR + 1;
  endmethod

endmodule

// ---------------------------------------------------------------------
// D stage: fetch through the local store, decode through the RAM table,
// own PC and the register that carries the decoded instruction to A.
// ---------------------------------------------------------------------

interface StageD;
  method Maybe#(DecodedInstr) out();
  method Action advance(Maybe#(Addr) redirect);
endinterface

module mkStageD#(PimRegFile regs, LocalStore mem,
                 RegFile#(Bit#(8), Bit#(20)) decTable)(StageD);

  Reg#(Maybe#(DecodedInstr)) outR <- mkReg(Invalid);

  method Maybe#(DecodedInstr) out() = outR;

  // A valid redirect squashes the fetched instruction and jumps; an
  // invalid one fetches at PC and steps PC.
  method Action advance(Maybe#(Addr) redirect);
    case (redirect) matches
      tagged Valid .t: outR <= Invalid;
      tagged Invalid: begin
        let i = unpackInstr(mem.read(regs.pc()));
        outR <= Valid(DecodedInstr { instr: i, dec: unpackDecode(decTable.sub(i.op)) });
      end
    endcase
    regs.pcNext(redirect);
  endmethod

endmodule

// ---------------------------------------------------------------------
// A stage: operand address and the three register operands.
// ---------------------------------------------------------------------

interface StageA;
  method Maybe#(A2R) out();
  method Action advance(Maybe#(DecodedInstr) in);
endinterface

module mkStageA#(PimRegFile regs)(StageA);

  Reg#(Maybe#(A2R)) outR <- mkReg(Invalid);

  function Maybe#(A2R) calc(Maybe#(DecodedInstr) in);
    case (in) matches
      tagged Valid .d: begin
        let rs = regs.read(regFieldToSel(d.instr.rs));
        let rt = regs.read(regFieldToSel(d.instr.rt));
        let rd = regs.read(regFieldToSel(d.instr.rd));
        // The address is formed only when the instruction has a memory
        // operand; the base is the instruction's rs field (p.428).
        let ea = d.dec.needsEA
                   ? truncate(wordData(rs) + zeroExtend(d.instr.imm))
                   : 0;
        return Valid(A2R { d: d, ea: ea, rsVal: rs, rtVal: rt, rdVal: rd });
      end
      tagged Invalid: return Invalid;
    endcase
  endfunction

  method Maybe#(A2R) out() = outR;
  method Action advance(Maybe#(DecodedInstr) in);
    outR <= calc(in);
  endmethod

endmodule

// ---------------------------------------------------------------------
// R stage: the memory stage.  A load reads its operand here (p.428);
// a store's data is carried on and written by E's memory microoperation.
// ---------------------------------------------------------------------

interface StageR;
  method Maybe#(R2S) out();
  method Action advance(Maybe#(A2R) in);
endinterface

module mkStageR#(LocalStore mem)(StageR);

  Reg#(Maybe#(R2S)) outR <- mkReg(Invalid);

  function Maybe#(R2S) calc(Maybe#(A2R) in);
    case (in) matches
      tagged Valid .a: begin
        let f = a.d.dec.isLoad ? Valid(mem.read(a.ea)) : Invalid;
        return Valid(R2S { d: a.d, ea: a.ea, rsVal: a.rsVal, rtVal: a.rtVal,
                           rdVal: a.rdVal, fetched: f });
      end
      tagged Invalid: return Invalid;
    endcase
  endfunction

  method Maybe#(R2S) out() = outR;
  method Action advance(Maybe#(A2R) in);
    outR <= calc(in);
  endmethod

endmodule

// ---------------------------------------------------------------------
// S stage: pipelined dereference and SRP/COL.
//
// The stage is a request/response box.  `step` is offered the R-stage
// result and whether the downstream can take a result; it consumes the
// instruction, walks one link of the reference chain per call, and
// publishes the resolved bundle in `out`.  One method writes the stage
// state, so the walk and the pass-through path cannot both drive it.
// ---------------------------------------------------------------------

typedef struct {
  Bool consumed;
  Maybe#(Addr) fetchAddr;
} SStepResult deriving (Bits, Eq);

interface StageS;
  method Maybe#(S2E) out();
  method Bool busy();
  method ActionValue#(SStepResult) step(Maybe#(R2S) in, Bool enable);
  method Action clear();
endinterface

module mkStageS#(LocalStore mem)(StageS);

  Reg#(Maybe#(S2E)) outR <- mkReg(Invalid);
  Reg#(Bool) walking <- mkReg(False);
  Reg#(R2S)  held    <- mkReg(R2S { d: noDecodedInstr(), ea: 0, rsVal: 0,
                                    rtVal: 0, rdVal: 0, fetched: Invalid });
  Reg#(Word) cur     <- mkReg(0);
  Reg#(Bool) srpR    <- mkReg(True);
  Reg#(Bool) colR    <- mkReg(True);
  Reg#(Bit#(32)) ptrs <- mkReg(0);

  function S2E resolve(R2S x, Word v, Bool s, Bool c) = S2E {
    d: x.d, ea: x.ea, rsVal: x.rsVal, rtVal: x.rtVal, rdVal: x.rdVal,
    fetched: x.fetched, derefVal: v, srp: s, col: c };

  method Maybe#(S2E) out() = outR;
  method Bool busy() = walking;

  // Returns True when `in` was consumed and the R2S register may be
  // refilled.  With `enable` low the stage holds everything, which is
  // how the pipeline stalls behind a busy E stage.
  method ActionValue#(SStepResult) step(Maybe#(R2S) in, Bool enable);
    if (!enable) return SStepResult { consumed: False, fetchAddr: Invalid };
    else if (walking) begin
      let nextAddr = truncate(wordData(cur));
      if (mem.miss(nextAddr)) begin
        return SStepResult { consumed: False, fetchAddr: Valid(nextAddr) };
      end else begin
        let next = mem.read(nextAddr);
        let pMRB = tagMRB(wordTag(cur));
        let srpN = srpR && !pMRB;
        let colN = colR && ((ptrs < 2) ? !pMRB : True);
        srpR <= srpN;
        colR <= colN;
        if (tagType(wordTag(next)) == tagRef) begin
          cur  <= next;
          ptrs <= ptrs + 1;
          return SStepResult { consumed: False, fetchAddr: Invalid };
        end else begin
          walking <= False;
          outR <= Valid(resolve(held, next, srpN, colN));
          return SStepResult { consumed: True, fetchAddr: Invalid };
        end
      end
    end else case (in) matches
      tagged Valid .x:
        if (x.d.dec.deref && tagType(wordTag(x.rsVal)) == tagRef) begin
          held    <= x;
          cur     <= x.rsVal;
          srpR    <= True;
          colR    <= True;
          ptrs    <= 0;
          walking <= True;
          outR    <= Invalid;
          return SStepResult { consumed: True, fetchAddr: Invalid };
        end else begin
          outR <= Valid(resolve(x, x.rsVal, True, True));
          return SStepResult { consumed: True, fetchAddr: Invalid };
        end
      tagged Invalid: begin
        outR <= Invalid;
        return SStepResult { consumed: True, fetchAddr: Invalid };
      end
    endcase
  endmethod

  method Action clear();
    walking <= False;
    outR <= Invalid;
  endmethod

endmodule

endpackage
