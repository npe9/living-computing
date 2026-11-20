// PIM/m core: the divide box.  A 32-step restoring divider, one bit a
// cycle, for the built-ins modulo and (later) divide.
//
// Signed, truncating toward zero, so the remainder has the dividend's
// sign: that is PDSS's C `%` (emulator/blt_basic.c blt_b_modulo).  The
// PIMOS manual says only "divides Integer1 by Integer2 and unifies the
// remainder"; for negative operands this is PDSS's behaviour, not
// established for the PIM/m firmware.  The caller rejects a zero
// divisor (the built-in's failure or exception).  -2^31 by -1 gives
// quotient -2^31 and remainder 0, as PDSS has it.
//
// The step count is ours: no source gives the machine's.
package PimmMBox;

import FIFO::*;

typedef struct { Bit#(32) quotient; Bit#(32) remainder; } DivResult deriving (Bits, Eq);

interface PimmMBox;
  method Action divide(Bit#(32) dividend, Bit#(32) divisor);
  method ActionValue#(DivResult) result;
endinterface

module mkPimmMBox(PimmMBox);
  Reg#(Bool)     busy   <- mkReg(False);
  Reg#(Bit#(6))  left   <- mkRegU;
  Reg#(Bit#(32)) quot   <- mkRegU;      // the dividend's magnitude, then the quotient
  Reg#(Bit#(33)) rem    <- mkRegU;
  Reg#(Bit#(32)) den    <- mkRegU;      // the divisor's magnitude
  Reg#(Bool)     negQ   <- mkRegU;
  Reg#(Bool)     negR   <- mkRegU;
  FIFO#(DivResult) resQ <- mkFIFO;

  rule step (busy && left != 0);
    Bit#(33) r = truncate({rem, quot[31]});
    Bit#(33) d = zeroExtend(den);
    Bool fits = r >= d;
    rem <= fits ? r - d : r;
    quot <= {quot[30:0], pack(fits)};
    left <= left - 1;
  endrule

  rule done (busy && left == 0);
    Bit#(32) r = truncate(rem);
    resQ.enq(DivResult { quotient: negQ ? -quot : quot, remainder: negR ? -r : r });
    busy <= False;
  endrule

  method Action divide(Bit#(32) dividend, Bit#(32) divisor) if (!busy);
    Bool na = dividend[31] == 1;
    Bool nb = divisor[31] == 1;
    quot <= na ? -dividend : dividend;
    den <= nb ? -divisor : divisor;
    rem <= 0;
    negQ <= na != nb;
    negR <= na;
    left <= 32;
    busy <= True;
  endmethod

  method ActionValue#(DivResult) result;
    resQ.deq;
    return resQ.first;
  endmethod
endmodule

endpackage
