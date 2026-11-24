package Shifter;

import AltoTypes::*;

typedef enum { ShNone, ShLeft, ShRight, ShCyc8 } ShOp deriving (Bits, Eq);
typedef enum { ModNone, ModMagic, ModDNS } ShMod deriving (Bits, Eq);

typedef struct {
   Word    out;
   Bit#(1) dnsCarry;
} ShOut deriving (Bits, Eq);

function ShOut doShift(ShOp op, ShMod mod, Word inputVal, Word t, Bit#(1) dnsCarryIn);
   Word o = inputVal;
   Bit#(1) dc = dnsCarryIn;

   case (op)
      ShNone: o = inputVal;
      ShLeft: begin
         o = inputVal << 1;
         if (mod == ModMagic)
            o = o | zeroExtend(t[15]);
         else if (mod == ModDNS) begin
            o = o | zeroExtend(dnsCarryIn);
            dc = inputVal[15];
         end
      end
      ShRight: begin
         o = inputVal >> 1;
         if (mod == ModMagic)
            o = o | {t[0], 15'b0};
         else if (mod == ModDNS) begin
            o = o | {dnsCarryIn, 15'b0};
            dc = inputVal[0];
         end
      end
      ShCyc8: o = {inputVal[7:0], inputVal[15:8]};
   endcase

   return ShOut { out: o, dnsCarry: dc };
endfunction

endpackage
