package Display;

import Vector::*;
import ConfigReg::*;
import AltoTypes::*;

import "BDPI" function Action host_draw_word(Bit#(32) line, Bit#(32) wordn, Bit#(16) data, Bit#(32) lowres);
import "BDPI" function Action host_draw_cursor(Bit#(32) line, Bit#(32) x, Bit#(32) wob, Bit#(16) csr);
import "BDPI" function Action host_render_field(Bit#(32) fieldn);

interface Display_IFC;
   method Bool evenField;
   method Bool dwtBlock;
   method Bool dhtBlock;
   method Action setDwtBlock(Bool v);
   method Action setDhtBlock(Bool v);
   method Action loadDDR(Word w);
   method Action loadXPREG(Word w);
   method Action loadCSR(Word w);
   method Action setMode(Word w);
   method Bool wakeupDVT;
   method Bool wakeupDHT;
   method Bool wakeupDWT;
   method Bool fifoFull;
   method Bool wakeupCURT;
   method Bool wakeupMRT;
   method Action reset();
   method Bit#(32) fields;
endinterface

typedef enum { DsVBlank, DsHBlank, DsVisible } DispState deriving (Bits, Eq);

module mkDisplay(Display_IFC);
   Reg#(Bool) even     <- mkConfigReg(False);
   Reg#(Bool) lowRes   <- mkReg(False);
   Reg#(Bool) lowLatch <- mkReg(False);
   Reg#(Bool) wob      <- mkReg(False);
   Reg#(Bool) wobLatch <- mkReg(False);
   Reg#(Bool) modePend <- mkReg(False);
   Reg#(Bool) dwtBlk   <- mkConfigReg(True);
   Reg#(Bool) dhtBlk   <- mkConfigReg(False);

   Reg#(Word) cursorReg     <- mkReg(0);
   Reg#(Word) cursorRegL    <- mkReg(0);
   Reg#(Word) cursorX       <- mkReg(0);
   Reg#(Word) cursorXL      <- mkReg(0);
   Reg#(Bool) cursorRegPend <- mkReg(False);
   Reg#(Bool) cursorXPend   <- mkReg(False);

   Vector#(16, Reg#(Word)) fifo <- replicateM(mkReg(0));
   Reg#(Bit#(5)) fifoCount <- mkReg(0);
   Reg#(Bit#(4)) fifoRd    <- mkReg(0);
   Reg#(Bit#(4)) fifoWr    <- mkReg(0);

   Reg#(Bit#(10)) scanline <- mkReg(0);
   Reg#(Bit#(6))  wordn    <- mkReg(0);
   Reg#(Bit#(6))  vblankN  <- mkReg(0);
   Reg#(DispState) state   <- mkReg(DsVBlank);
   Reg#(Bit#(16)) timer    <- mkReg(fromInteger(dispScanCycles));
   Reg#(Bit#(32)) fieldN   <- mkConfigReg(0);

   Reg#(Bool) wDVT  <- mkConfigReg(True);
   Reg#(Bool) wDHT  <- mkConfigReg(False);
   Reg#(Bool) wDWT  <- mkConfigReg(False);
   Reg#(Bool) wCURT <- mkConfigReg(False);
   Reg#(Bool) wMRT  <- mkConfigReg(False);

   RWire#(Bool) rwDwt <- mkRWire;
   RWire#(Bool) rwDht <- mkRWire;
   RWire#(Word) rwDDR <- mkRWire;
   RWire#(Word) rwXP  <- mkRWire;
   RWire#(Word) rwCSR <- mkRWire;
   RWire#(Word) rwMode<- mkRWire;
   PulseWire    pwRst <- mkPulseWire;

   (* fire_when_enabled, no_implicit_conditions *)
   rule rl_scan;
      Bool ev = even;
      Bool lr = lowRes;
      Bool ll = lowLatch;
      Bool wb = wob;
      Bool wbl= wobLatch;
      Bool mp = modePend;
      Bool dwb= dwtBlk;
      Bool dhb= dhtBlk;
      Word cr = cursorReg;
      Word crl= cursorRegL;
      Word cx = cursorX;
      Word cxl= cursorXL;
      Bool crp= cursorRegPend;
      Bool cxp= cursorXPend;
      Bit#(5) fc = fifoCount;
      Bit#(4) fr = fifoRd;
      Bit#(4) fw = fifoWr;
      Bit#(10) sl = scanline;
      Bit#(6)  wn = wordn;
      Bit#(6)  vb = vblankN;
      DispState st = state;
      Bit#(16) tm = timer;
      Bit#(32) fn = fieldN;
      Bool dvt = False;
      Bool dht = False;
      Bool dwt = False;
      Bool cur = False;
      Bool mrt = False;
      Maybe#(Tuple2#(Bit#(4), Word)) fifoWrReq = tagged Invalid;

      if (pwRst) begin
         ev = False; lr = False; wb = False; dwb = True; dhb = False;
         st = DsVBlank; tm = fromInteger(dispScanCycles);
         sl = 0; wn = 0; vb = 0; fc = 0; fn = 0;
         dvt = True;
      end
      else begin
         if (rwDwt.wget matches tagged Valid .v) dwb = v;
         if (rwDht.wget matches tagged Valid .v) dhb = v;
         if (rwDDR.wget matches tagged Valid .w) begin
            if (fc < 16) begin
               fifoWrReq = tagged Valid tuple2(fw, w);
               fw = fw + 1;
               fc = fc + 1;
            end
         end
         if (rwXP.wget matches tagged Valid .w) begin
            if (!cxp) begin cxp = True; cx = ~w; end
         end
         if (rwCSR.wget matches tagged Valid .w) begin
            if (!crp) begin crp = True; cr = w; end
         end
         if (rwMode.wget matches tagged Valid .w) begin
            ll = unpack(w[15]); wbl = unpack(w[14]); mp = True;
         end

         if (tm != 0)
            tm = tm - 1;
         else begin
            case (st)
               DsVBlank: begin
                  vb = vb + 1;
                  mrt = True;
                  Bit#(6) limit = ev ? 33 : 34;
                  if (vb >= limit) begin
                     dht = True; cur = True; dwb = False; dhb = False;
                     st = DsHBlank; tm = fromInteger(dispHBlankCycles);
                     fc = 0; fr = 0; fw = 0;
                  end
                  else
                     tm = fromInteger(dispScanCycles);
               end
               DsHBlank: begin
                  wn = 0;
                  if (crp) begin crl = cr; crp = False; end
                  if (cxp) begin cxl = cx; cxp = False; end
                  st = DsVisible;
                  tm = fromInteger(dispWordCycles);
               end
               DsVisible: begin
                  Word dw = wb ? 0 : 16'hFFFF;
                  if (fc > 0) begin
                     Word raw = fifo[fr];
                     dw = wb ? raw : ~raw;
                     fr = fr + 1;
                     fc = fc - 1;
                  end
                  host_draw_word(zeroExtend(sl), zeroExtend(wn), dw, lr ? 1 : 0);
                  Bit#(6) words = lr ? fromInteger(dispScanlineWords / 2)
                                     : fromInteger(dispScanlineWords);
                  if (wn + 1 >= words) begin
                     if (cxl < 606)
                        host_draw_cursor(zeroExtend(sl), zeroExtend(cxl),
                                         wb ? 1 : 0, crl);
                     Bit#(10) nl = sl + 2;
                     if (nl >= fromInteger(dispVisibleLines)) begin
                        host_render_field(fn);
                        ev = !ev; fn = fn + 1;
                        sl = ev ? 1 : 0;
                        vb = 0; st = DsVBlank;
                        tm = fromInteger(dispScanCycles);
                        fc = 0; dvt = True; dwb = True;
                     end
                     else begin
                        sl = nl; cur = True; mrt = True; dwb = False;
                        fc = 0; fr = 0; fw = 0;
                        if (mp) begin lr = ll; wb = wbl; mp = False; end
                        st = DsHBlank; tm = fromInteger(dispHBlankCycles);
                     end
                  end
                  else begin
                     wn = wn + 1;
                     tm = fromInteger(lr ? dispWordCycles * 2 : dispWordCycles);
                  end
               end
            endcase
         end

         Bool fifoFull = fc >= 15;
         dwt = !fifoFull && !dhb && !dwb;
      end

      if (fifoWrReq matches tagged Valid {.i, .w})
         fifo[i] <= w;

      even <= ev; lowRes <= lr; lowLatch <= ll; wob <= wb; wobLatch <= wbl;
      modePend <= mp; dwtBlk <= dwb; dhtBlk <= dhb;
      cursorReg <= cr; cursorRegL <= crl; cursorX <= cx; cursorXL <= cxl;
      cursorRegPend <= crp; cursorXPend <= cxp;
      fifoCount <= fc; fifoRd <= fr; fifoWr <= fw;
      scanline <= sl; wordn <= wn; vblankN <= vb; state <= st; timer <= tm;
      fieldN <= fn;
      wDVT <= dvt; wDHT <= dht; wDWT <= dwt; wCURT <= cur; wMRT <= mrt;
   endrule

   method Bool evenField = even;
   method Bool dwtBlock = dwtBlk;
   method Bool dhtBlock = dhtBlk;
   method Action setDwtBlock(Bool v); rwDwt.wset(v); endmethod
   method Action setDhtBlock(Bool v); rwDht.wset(v); endmethod
   method Action loadDDR(Word w);     rwDDR.wset(w); endmethod
   method Action loadXPREG(Word w);   rwXP.wset(w);  endmethod
   method Action loadCSR(Word w);     rwCSR.wset(w); endmethod
   method Action setMode(Word w);     rwMode.wset(w); endmethod
   method Bool wakeupDVT = wDVT;
   method Bool wakeupDHT = wDHT;
   method Bool wakeupDWT = wDWT;
   method Bool fifoFull = fifoCount >= 15;
   method Bool wakeupCURT = wCURT;
   method Bool wakeupMRT = wMRT;
   method Action reset(); pwRst.send(); endmethod
   method Bit#(32) fields = fieldN;
endmodule

endpackage
