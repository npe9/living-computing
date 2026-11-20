// PIM/m core: the registers.  r is the general register file (a goal's
// arguments arrive in r0..); a is the argument registers of the goal
// being built (set_value writes them, from 1).  Every write is traced.
package PimmRegs;

import RegFile::*;
import PimmTypes::*;

interface PimmRegs;
  method Cell r(Bit#(8) n);
  method Action wr(Bit#(8) n, Cell w);
  method Cell a(Bit#(8) n);
  method Action wa(Bit#(8) n, Cell w);
endinterface

module mkPimmRegs(PimmRegs);
  RegFile#(Bit#(8), Cell) regs <- mkRegFileFull;
  RegFile#(Bit#(8), Cell) args <- mkRegFileFull;

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
endmodule

endpackage
