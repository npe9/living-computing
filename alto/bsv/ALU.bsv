package ALU;

import AltoTypes::*;

typedef struct {
   Word result;
   Bit#(1) carry;
} AluOut deriving (Bits, Eq);

function AluOut aluExec(AluFn fn, Word bus, Word t, Bit#(1) skip);
   Int#(17) b = unpack({1'b0, bus});
   Int#(17) tv = unpack({1'b0, t});
   Int#(17) r = 0;
   Bit#(1) c = 0;

   case (fn)
      AluBus:            begin r = b; c = 0; end
      AluT:              begin r = tv; c = 0; end
      AluBusOrT:         begin r = unpack({1'b0, bus | t}); c = 0; end
      AluBusAndT, AluBusAndTWb:
                         begin r = unpack({1'b0, bus & t}); c = 0; end
      AluBusXorT:        begin r = unpack({1'b0, bus ^ t}); c = 0; end
      AluBusPlus1:       begin
                            Int#(17) s = b + 1;
                            r = s;
                            c = pack(s > 17'h0FFFF)[0];
                         end
      AluBusMinus1:      begin
                            Int#(17) s = b - 1;
                            r = s;
                            // 1's-complement subtract: carry means no borrow.
                            c = pack(s >= 0)[0];
                         end
      AluBusPlusT:       begin
                            Int#(17) s = b + tv;
                            r = s;
                            c = pack(s > 17'h0FFFF)[0];
                         end
      AluBusMinusT:      begin
                            Int#(17) s = b - tv;
                            r = s;
                            c = pack(s >= 0)[0];
                         end
      AluBusMinusTMinus1: begin
                            Int#(17) s = b - tv - 1;
                            r = s;
                            c = pack(s >= 0)[0];
                         end
      AluBusPlusTPlus1:  begin
                            Int#(17) s = b + tv + 1;
                            r = s;
                            c = pack(s > 17'h0FFFF)[0];
                         end
      AluBusPlusSkip:    begin
                            Int#(17) s = b + unpack({16'b0, skip});
                            r = s;
                            c = pack(s > 17'h0FFFF)[0];
                         end
      AluBusAndNotT:     begin r = unpack({1'b0, bus & ~t}); c = 0; end
      default:           begin r = b; c = 0; end
   endcase

   return AluOut { result: truncate(pack(r)), carry: c };
endfunction

endpackage
