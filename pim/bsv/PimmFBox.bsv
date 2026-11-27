// PIM/m core: the floating point box (2026-11-26; docs/float.md).
//
// A PIM/m float is the immediate word {FLTo 30h, IEEE single}
// (library/kbn/kbnheap.kl1:144-146, 236; the 103 float constants of the
// held .sav objects).  ref/pimm/pimm.py f32_op, f32_to_int, int_to_f32
// are the reference.
//
//   arith(fn, a, b)   floating_point_add / subtract / multiply / divide
//                     (fn 0-3) of two singles' bits, answered by result:
//                     the bits, or invalid for the cases the PIMOS
//                     manual lists as "Fail, Exception" (e-builtin.tex:
//                     508-573): inf + -inf, inf - inf, 0 * inf, 0/0,
//                     inf/inf, or a NaN operand (OURS: none can be made).
//                     Those, and x/0 (the infinity of the signs,
//                     e-builtin.tex:561), are decided here by the
//                     operands, as pimm.py decides them, not from the
//                     FPU's exception flags.  Everything else is the
//                     vendored Flute FPU (vendor/flute/FPU.bsv: bsc's
//                     FloatingPoint fused multiply-add for add, subtract
//                     and multiply, its divider for divide), rounding to
//                     nearest even (INFERENCE, docs/float.md); overflow
//                     is infinity, as the manual says (e-builtin.tex:509).
//   fToInt, intToF, fCompare   the conversions and comparisons, as
//                     functions: floating_point_to_integer towards zero
//                     ("ignoring decimal", e-builtin.tex:582), Invalid on
//                     an overflow (the range checked by the exponent
//                     here); integer_to_floating_point rounded to nearest
//                     even; the four comparisons.  The library calls are
//                     those of Flute's FBox_Core.bsv (doFCVT_W_S's
//                     vFloatToFixed with Rnd_Zero, doFCVT_S_W's
//                     vFixedToFloat, doFEQ_S/FLT_S/FLE_S's compareFP).
//
// The cycle counts are the library's: no source gives the machine's
// (an FPP, a floating-point LSI, on the PSI-UX: docs/literature_gaps.md).
package PimmFBox;

import FIFO::*;
import GetPut::*;
import ClientServer::*;
import FloatingPoint::*;
import FPU::*;

typedef struct { Bit#(32) value; Bool invalid; } FResult deriving (Bits, Eq);

interface PimmFBox;
  method Action arith(Bit#(2) fn, Bit#(32) a, Bit#(32) b);
  method ActionValue#(FResult) result;
endinterface

function FSingle fs(Bit#(32) b) = unpack(b);
function Bool fInf(Bit#(32) b) = b[30:23] == 8'hff && b[22:0] == 0;
function Bool fNaN(Bit#(32) b) = b[30:23] == 8'hff && b[22:0] != 0;
function Bool fZero(Bit#(32) b) = b[30:0] == 0;

// the explicit cases (pimm.py f32_op): Valid an answer without the FPU
function Maybe#(FResult) fSpecial(Bit#(2) fn, Bit#(32) a, Bit#(32) b);
  FResult bad = FResult { value: 0, invalid: True };
  Bool sameSign = a[31] == b[31];
  if (fNaN(a) || fNaN(b)) return tagged Valid bad;
  else if (fn == 0 && fInf(a) && fInf(b) && !sameSign) return tagged Valid bad;
  else if (fn == 1 && fInf(a) && fInf(b) && sameSign) return tagged Valid bad;
  else if (fn == 2 && ((fZero(a) && fInf(b)) || (fInf(a) && fZero(b)))) return tagged Valid bad;
  else if (fn == 3 && ((fZero(a) && fZero(b)) || (fInf(a) && fInf(b)))) return tagged Valid bad;
  else if (fn == 3 && fZero(b))
    return tagged Valid FResult { value: {a[31] ^ b[31], 31'h7f800000}, invalid: False };
  else return tagged Invalid;
endfunction

// floating_point_to_integer: Invalid unless -2^31 <= f < 2^31 (an
// exponent field of 158 or more is 2^31 or beyond, infinities and NaNs
// included; -2^31 itself, cf000000, fits)
function Maybe#(Bit#(32)) fToInt(Bit#(32) f);
  if (f[30:23] >= 158 && f != 32'hcf000000) return tagged Invalid;
  else begin
    match {.v, .e} = Tuple2#(Int#(32), FloatingPoint::Exception)'(vFloatToFixed(6'd0, fs(f), Rnd_Zero));
    return tagged Valid pack(v);
  end
endfunction

function Bit#(32) intToF(Bit#(32) i);
  match {.f, .e} = Tuple2#(FSingle, FloatingPoint::Exception)'(vFixedToFloat(Int#(32)'(unpack(i)), 6'd0, Rnd_Nearest_Even));
  return pack(f);
endfunction

// fn 0 equal, 1 not_equal, 2 less_than, 3 not_less_than (no NaN reaches
// here: none can be made)
function Bool fCompare(Bit#(8) fn, Bit#(32) a, Bit#(32) b);
  let c = compareFP(fs(a), fs(b));
  case (fn)
    0: return c == EQ;
    1: return c != EQ;
    2: return c == LT;
    default: return c == GT || c == EQ;
  endcase
endfunction

module mkPimmFBox(PimmFBox);
  FPU_IFC fpu <- mkFPU;
  FIFO#(FResult) direct <- mkFIFO;      // the explicit cases
  FIFO#(Bool) viaFpu <- mkFIFO;          // in order: was it the FPU's
  FIFO#(FResult) out <- mkFIFO;

  rule fromFpu (viaFpu.first);
    let r <- fpu.server_core.response.get;
    viaFpu.deq;
    out.enq(FResult { value: pack(tpl_1(r).S), invalid: False });
  endrule

  rule fromDirect (!viaFpu.first);
    viaFpu.deq;
    direct.deq;
    out.enq(direct.first);
  endrule

  method Action arith(Bit#(2) fn, Bit#(32) a, Bit#(32) b);
    case (fSpecial(fn, a, b)) matches
      tagged Valid .r: begin
        direct.enq(r);
        viaFpu.enq(False);
      end
      tagged Invalid: begin
        FpuOp op = case (fn) 0: FPAdd; 1: FPSub; 2: FPMul; default: FPDiv; endcase;
        fpu.server_core.request.put(tuple5(tagged S fs(a), tagged S fs(b), tagged S fs(0),
                                           Rnd_Nearest_Even, op));
        viaFpu.enq(True);
      end
    endcase
  endmethod

  method ActionValue#(FResult) result;
    out.deq;
    return out.first;
  endmethod
endmodule

endpackage
