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
  RegFile#(Bit#(12), Word) heap <- mkRegFileFull;

  Reg#(Word) pcR   <- mkReg(0);
  Reg#(Bool) run   <- mkReg(False);
  Reg#(Bool) haltR <- mkReg(False);
  Reg#(Bit#(12)) hp <- mkReg(0);
  Reg#(Bit#(8)) narg <- mkReg(0);
  RegFile#(Bit#(3), Word) goals <- mkRegFileFull;
  Reg#(Bit#(3)) rqfp <- mkReg(0);
  Reg#(Bit#(3)) rqt <- mkReg(0);

  // Tag values are the model's; the encoding is PIMOS-derived.
  Bit#(8) tagInt = 8'h02;
  Bit#(8) tagRef = 8'h03;
  Bit#(8) tagVar = 8'h01;

  function Word deref(Word w);
    return (w[39:32] == tagRef) ? heap.sub(w[11:0]) : w;
  endfunction

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
    Bit#(8)  c   = val[7:0];
    if (tag == 8'h23) begin
      case (op)
        8'h14: regs.upd(b, {tagInt, 24'h0, a});   // set_value c8, r
        8'h13: regs.upd(b, {tagVar, 24'h0, a});   // set_variable c8, r
        8'h34: regs.upd(b, regs.sub(a));          // put_value r, r
        8'h33: regs.upd(b, {tagVar, 24'h0, a});   // put_variable r, r
        8'hbc: regs.upd(b, regs.sub(a));          // get_value r, r
        8'h25: begin heap.upd(hp, regs.sub(a)); hp <= hp + 1; end  // write_value
        8'hbd: regs.upd(b, heap.sub(regs.sub(a)[11:0]));           // get_bound_value
        8'ha4: if (deref(regs.sub(a)) != deref(regs.sub(b)))        // wait_value
                 haltR <= True;
        8'h61: narg <= a;                          // execute: jump to label (b:c)
        8'h63: begin                                // enqueue_goal N, label
          goals.upd(rqt, zeroExtend((b << 8) | c));
          rqt <= rqt + 1;
        end
        8'h69: begin                                // suspend N, label
          goals.upd(rqt, zeroExtend((b << 8) | c));
          rqt <= rqt + 1;
        end
        8'h60: if (rqfp == rqt) haltR <= True;      // proceed: empty queue halts
        8'h71: haltR <= True;                     // halt
        default: haltR <= True;                   // unimplemented: stop loud
      endcase
    end else begin
      haltR <= True;
    end
    if (tag == 8'h23 && op == 8'h61) begin
      pcR <= zeroExtend((b << 8) | c);
    end else if (tag == 8'h23 && op == 8'h60 && rqfp != rqt) begin
      pcR <= goals.sub(rqfp);
      rqfp <= rqfp + 1;
    end else if (tag == 8'h23 && op == 8'h69) begin
      pcR <= (rqfp == rqt) ? goals.sub(rqt) : goals.sub(rqfp);
      rqfp <= rqfp + 1;
    end else begin
      pcR <= pcR + 1;
    end
  endmethod

  method Bool halted() = haltR;
  method Word readReg(RegNo r) = regs.sub(r);
  method Word pc() = pcR;

endmodule

endpackage
