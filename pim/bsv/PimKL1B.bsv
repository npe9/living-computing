// PimKL1B.bsv -- a minimal KL1-B execution path.
//
// The diagnostic ISA in PimPU is a model-defined stand-in.  This module
// is the separate KL1-B path the PIMOS binaries need: a 40-bit tagged
// word (8-bit tag + 32-bit value, TR-389 p. 9), an 8-bit register file,
// and a fetch/decode/execute step.  The encodings are the PIMOS
// assembler's (docs/kl1_encoding.md), labelled PIMOS-derived.
//
// Scope for the first test: set_value, set_variable, put_value, proceed,
// halt.  The structure-building and unification instructions follow once
// this path is proven.
package PimKL1B;

import RegFile::*;

typedef Bit#(40) Word;
typedef Bit#(8)  RegNo;

interface PimKL1B;
  method Action load(Bit#(12) a, Word w);
  method Action start(Word entry);
  method Action step();
  method Bool halted();
  method Word readReg(RegNo r);
  method Word pc();
endinterface

module mkPimKL1B(PimKL1B);

  RegFile#(RegNo, Word)  regs <- mkRegFileFull;
  RegFile#(Bit#(12), Word) mem <- mkRegFileFull;

  Reg#(Word) pcR   <- mkReg(0);
  Reg#(Bool) run   <- mkReg(False);
  Reg#(Bool) haltR <- mkReg(False);

  // Tag values are the model's; the encoding is PIMOS-derived.
  Bit#(8) tagInt = 8'h02;
  Bit#(8) tagVar = 8'h01;

  method Action load(Bit#(12) a, Word w) = mem.upd(a, w);

  method Action start(Word entry) if (!run);
    pcR <= entry;
    run <= True;
    haltR <= False;
  endmethod

  method Action step() if (run && !haltR);
    Word w = mem.sub(pcR[11:0]);
    Bit#(8)  tag = w[39:32];
    Bit#(32) val = w[31:0];
    Bit#(8)  op  = val[31:24];
    Bit#(8)  a   = val[23:16];
    Bit#(8)  b   = val[15:8];
    if (tag == 8'h23) begin
      case (op)
        8'h14: regs.upd(b, {tagInt, 24'h0, a});   // set_value c8, r
        8'h13: regs.upd(b, {tagVar, 24'h0, a});   // set_variable c8, r
        8'h34: regs.upd(b, regs.sub(a));          // put_value r, r
        8'h33: regs.upd(b, {tagVar, 24'h0, a});   // put_variable r, r
        8'hbc: regs.upd(b, regs.sub(a));          // get_value r, r
        8'h60: haltR <= True;                     // proceed
        8'h71: haltR <= True;                     // halt
        default: haltR <= True;                   // unimplemented: stop loud
      endcase
    end else begin
      haltR <= True;
    end
    pcR <= pcR + 1;
  endmethod

  method Bool halted() = haltR;
  method Word readReg(RegNo r) = regs.sub(r);
  method Word pc() = pcR;

endmodule

endpackage
