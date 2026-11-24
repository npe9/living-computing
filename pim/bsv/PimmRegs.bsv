// PIM/m core: the registers.  r is the general register file (a goal's
// arguments arrive in r0..); a is the argument registers of the goal
// being built (set_value writes them, from 1); v is the work slots the
// instructions save and restore spill registers to (TM-1044's "work
// memory", in each processor's local area; 256 slots of their own:
// OURS).  Every write is traced.
package PimmRegs;

import RegFile::*;
import PimmTypes::*;

interface PimmRegs;
  method Cell r(Bit#(8) n);
  method Action wr(Bit#(8) n, Cell w);
  method Cell a(Bit#(8) n);
  method Action wa(Bit#(8) n, Cell w);
  method Cell v(Bit#(8) n);
  method Action wv(Bit#(8) n, Cell w);
endinterface

module mkPimmRegs(PimmRegs);
  RegFile#(Bit#(8), Cell) regs <- mkRegFileFull;
  RegFile#(Bit#(8), Cell) args <- mkRegFileFull;
  RegFile#(Bit#(8), Cell) work <- mkRegFileFull;

  method Cell r(Bit#(8) n) = regs.sub(n);
  method Action wr(Bit#(8) n, Cell w);
    regs.upd(n, w);
    traceR(n, w);
  endmethod
  method Cell a(Bit#(8) n) = args.sub(n);
  method Action wa(Bit#(8) n, Cell w);
    args.upd(n, w);
    traceA(n, w);
  endmethod
  method Cell v(Bit#(8) n) = work.sub(n);
  method Action wv(Bit#(8) n, Cell w);
    work.upd(n, w);
    $display("V %0d %02x%08x", n, w.tag, w.val);
  endmethod
endmodule

endpackage
