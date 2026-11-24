// PIM/m core: the multiply and divide box.  A 32-step restoring
// divider, one bit a cycle, for the built-ins modulo and (later)
// divide, and a 32-step shift-and-add multiplier for multiply.
//
// Signed, truncating toward zero, so the remainder has the dividend's
// sign: that is PDSS's C `%` (emulator/blt_basic.c blt_b_modulo).  The
// PIMOS manual says only "divides Integer1 by Integer2 and unifies the
// remainder"; for negative operands this is PDSS's behaviour, not
// established for the PIM/m firmware.  The caller rejects a zero
// divisor (the built-in's failure or exception).  -2^31 by -1 gives
// quotient -2^31 and remainder 0, as PDSS has it.
//
// The multiplier is signed and says whether the product leaves 32
// bits (the built-in's exception, PIMOS manual, multiply: "If an
// overflow occurs").
//
// multiplyAdd (2026-11-24) is the same multiplier unsigned, a * b + c
// in 64 bits, for multiply_bignum_by_word's word step (VPIM's
// s_Multiply_BIGNUM_By_Word: b_Multiply_ExtendedInt, then the carry
// added).
//
// divideWide (2026-11-24) is the divider unsigned, the 64-bit hi:lo by
// a 32-bit divisor, for divide_extended; the caller sees that hi is
// below the divisor (VPIM's exception otherwise), so 32 steps from a
// remainder of hi give the 32-bit quotient.
//
// The step counts are ours: no source gives the machine's.
package PimmMBox;

import FIFO::*;

typedef struct { Bit#(32) quotient; Bit#(32) remainder; } DivResult deriving (Bits, Eq);
typedef struct { Bit#(32) value; Bool overflow; } MulResult deriving (Bits, Eq);

interface PimmMBox;
  method Action divide(Bit#(32) dividend, Bit#(32) divisor);
  method ActionValue#(DivResult) result;
  method Action multiply(Bit#(32) a, Bit#(32) b);
  method ActionValue#(MulResult) product;
  method Action multiplyAdd(Bit#(32) a, Bit#(32) b, Bit#(32) c);
  method Action divideWide(Bit#(32) hi, Bit#(32) lo, Bit#(32) divisor);
  method ActionValue#(Bit#(64)) wide;
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
  // the multiplier
  Reg#(Bool)     mBusy  <- mkReg(False);
  Reg#(Bit#(6))  mLeft  <- mkRegU;
  Reg#(Bit#(64)) acc    <- mkRegU;
  Reg#(Bit#(64)) mcand  <- mkRegU;
  Reg#(Bit#(32)) mplier <- mkRegU;
  Reg#(Bool)     negP   <- mkRegU;
  FIFO#(MulResult) prodQ <- mkFIFO;
  Reg#(Bool)     mWide  <- mkRegU;      // multiplyAdd: unsigned, the 64 bits
  FIFO#(Bit#(64)) wideQ <- mkFIFO;

  rule mulStep (mBusy && mLeft != 0);
    if (mplier[0] == 1) acc <= acc + mcand;
    mcand <= mcand << 1;
    mplier <= mplier >> 1;
    mLeft <= mLeft - 1;
  endrule

  rule mulDone (mBusy && mLeft == 0 && mWide);
    wideQ.enq(acc);
    mBusy <= False;
  endrule

  rule mulDoneSigned (mBusy && mLeft == 0 && !mWide);
    Bit#(64) p = negP ? -acc : acc;
    // it fits when bits 63..31 are all the sign
    Bit#(33) top = p[63:31];
    prodQ.enq(MulResult { value: p[31:0], overflow: top != 0 && top != '1 });
    mBusy <= False;
  endrule

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

  method Action divideWide(Bit#(32) hi, Bit#(32) lo, Bit#(32) divisor) if (!busy);
    quot <= lo;
    den <= divisor;
    rem <= zeroExtend(hi);
    negQ <= False;
    negR <= False;
    left <= 32;
    busy <= True;
  endmethod

  method ActionValue#(DivResult) result;
    resQ.deq;
    return resQ.first;
  endmethod

  method Action multiply(Bit#(32) a, Bit#(32) b) if (!mBusy);
    Bool na = a[31] == 1;
    Bool nb = b[31] == 1;
    mcand <= zeroExtend(na ? -a : a);
    mplier <= nb ? -b : b;
    acc <= 0;
    negP <= na != nb;
    mWide <= False;
    mLeft <= 32;
    mBusy <= True;
  endmethod

  method Action multiplyAdd(Bit#(32) a, Bit#(32) b, Bit#(32) c) if (!mBusy);
    mcand <= zeroExtend(a);
    mplier <= b;
    acc <= zeroExtend(c);
    negP <= False;
    mWide <= True;
    mLeft <= 32;
    mBusy <= True;
  endmethod

  method ActionValue#(Bit#(64)) wide;
    wideQ.deq;
    return wideQ.first;
  endmethod

  method ActionValue#(MulResult) product;
    prodQ.deq;
    return prodQ.first;
  endmethod
endmodule

endpackage
