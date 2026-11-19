// PimStages.bsv -- the D, A, R and S stages of the PIM/m processing
// element as separate modules, per docs/architecture.md.
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

package PimStages;

import RegFile::*;
import PimTypes::*;

// ---------------------------------------------------------------------
// D stage
// ---------------------------------------------------------------------

interface StageD;
  method DecodedInstr decode(Word w);
endinterface

module mkStageD#(RegFile#(Bit#(8), Bit#(20)) decTable)(StageD);
  method DecodedInstr decode(Word w);
    let i = unpackInstr(w);
    let e = unpackDecode(decTable.sub(i.op));
    return DecodedInstr { instr: i, dec: e };
  endmethod
endmodule

// ---------------------------------------------------------------------
// A stage
// ---------------------------------------------------------------------

interface StageA;
  method Addr calc(DecodedInstr d, Word rsVal, Word rtVal, Word rdVal);
endinterface

module mkStageA(StageA);
  method Addr calc(DecodedInstr d, Word rsVal, Word rtVal, Word rdVal);
    let base = wordData(rsVal);
    return truncate(base + zeroExtend(d.instr.imm));
  endmethod
endmodule

// ---------------------------------------------------------------------
// R stage
// ---------------------------------------------------------------------

interface StageR;
  method Word fetch(Bool isLoad, Addr ea);
endinterface

module mkStageR#(RegFile#(Addr, Word) mem)(StageR);
  method Word fetch(Bool isLoad, Addr ea) =
    isLoad ? mem.sub(ea) : mkWord(tagInt, False, 0);
endmodule

// ---------------------------------------------------------------------
// S stage: pipelined dereference and SRP/COL
// ---------------------------------------------------------------------

interface StageS;
  method Action start(Word w);
  method Action run();
  method Bool busy();
  method Word value();
  method Bool srp();
  method Bool col();
endinterface

module mkStageS#(RegFile#(Addr, Word) mem)(StageS);
  Reg#(Bool) active <- mkReg(False);
  Reg#(Word) cur    <- mkRegU;
  Reg#(Word) res    <- mkRegU;
  Reg#(Bool) srpR   <- mkReg(True);
  Reg#(Bool) colR   <- mkReg(True);
  Reg#(Bit#(8)) ptrs <- mkReg(0);

  method Action start(Word w);
    if (tagType(wordTag(w)) == tagRef) begin
      active <= True;
      cur    <= w;
      srpR   <= True;
      colR   <= True;
      ptrs   <= 0;
    end else begin
      active <= False;
      res    <= w;
      srpR   <= True;
      colR   <= True;
      ptrs   <= 0;
    end
  endmethod

  method Action run();
    if (active) begin
      let next = mem.sub(truncate(wordData(cur)));
      let pMRB = tagMRB(wordTag(cur));
      srpR <= srpR && !pMRB;
      colR <= colR && ((ptrs < 2) ? !pMRB : True);
      if (tagType(wordTag(next)) == tagRef) begin
        cur  <= next;
        ptrs <= ptrs + 1;
      end else begin
        res    <= next;
        active <= False;
      end
    end
  endmethod

  method Bool busy() = active;
  method Word value() = res;
  method Bool srp() = srpR;
  method Bool col() = colR;
endmodule

endpackage
