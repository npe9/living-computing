// Rtc.bsv -- the Hobbit board's MK48T02 timekeeper: 2040 bytes of NVRAM
// and the eight clock registers, at IONAK+0x2000..0x3FFF.
//
// Behaviour reference: tools/p9boot.py `Timekeeper` and CHOICES['rtc'];
// driver: tools/plan9-1e/sys/src/9/hobbit/devrtc.c; register map: io.h
// (Nvram at IONAK 0x2000, NVRAMLEN 2040; RTCdev at IONAK 0x3FE0); data
// sheet quotations: docs/devices/README.md "MK48T02 timekeeper".  The
// design notes, the deviations from the device bus contract and the test
// are in rtc.md.
//
// Each byte of the part is one 32-bit word on the bus, in bits 7:0 (io.h
// Nvram's `uchar val; uchar pad[3]`, RTCdev's ulongs).  The offset is in
// the 8 KB window, so the address is 13 bits, not the contract's 12:
//   off 0x0000..0x1FDF   NVRAM byte off>>2 (0..2039)
//   off 0x1FE0           control  (W 0x80 = devrtc.c RTCWRITE,
//                                  R 0x40 = RTCREAD, S and calibration
//                                  stored, no effect)
//   off 0x1FE4..0x1FFC   sec, min, hour, wday, mday, mon, year (BCD)
//
// Freeze / load (Timekeeper.write, exactly):
//   control write with R|W set where neither was set: the seven clock
//     registers are copied to the held set; reads return the held set.
//   control write clearing W where W was set: the held set is loaded into
//     the counters (wday recomputed from the date, as the model does) and
//     the one-second divider restarts, so the next second comes exactly
//     ticksPerSec cycles after the load (the model's offset = t - clock()).
//   control write with neither R nor W: the held set is dropped.
//   clock register write without W: fault (the model's BusError).
//
// The counters run from `startBcd` at reset and tick every `ticksPerSec`
// cycles of CLK.  The ULX3S path has no battery: time and NVRAM restart
// from their initial values at every configuration.
//
// Fail loud: `fault` is sticky and non-zero from the first access the
// model refuses (or that the RTL cannot reproduce: a load of a value that
// is not a valid calendar time).  The response is still given (data 0).
package Rtc;

import RegFile :: *;
import FIFOF   :: *;

export RtcIfc(..);
export RtcTime(..);
export mkRtc;
export mkRtcCore;
export rtcFaultNone, rtcFaultRegWriteNoW, rtcFaultBadLoad, rtcFaultLane,
       rtcFaultNoHeld;

typedef struct {
   Bit#(8) year;  Bit#(8) mon;  Bit#(8) mday;  Bit#(8) wday;
   Bit#(8) hour;  Bit#(8) min;  Bit#(8) sec;
} RtcTime deriving (Bits, Eq);

interface RtcIfc;
   // Device bus contract (docs/ulx3s_plan.md), with a 13-bit offset.
   method Action request(Bit#(13) addr, Bit#(32) wdata, Bit#(4) be,
                         Bool write);
   method ActionValue#(Bit#(32)) response;
   (* always_ready *) method Bool irq;                    // the MK48T02 has no interrupt pin
   (* always_ready *) method Bit#(8) fault;               // 0, or the first fault's code
endinterface

Bit#(8) rtcFaultNone        = 0;
Bit#(8) rtcFaultRegWriteNoW = 1;   // clock register written without W
Bit#(8) rtcFaultBadLoad     = 2;   // W cleared with a non-calendar value
Bit#(8) rtcFaultLane        = 3;   // write without byte lane 0
Bit#(8) rtcFaultNoHeld      = 4;   // W cleared with nothing held

// ---- BCD calendar arithmetic -------------------------------------------

function Bit#(8) bcdInc(Bit#(8) x) =
   (x[3:0] == 9) ? {x[7:4] + 1, 4'h0} : x + 1;

function Bool bcdValid(Bit#(8) x) = x[7:4] <= 9 && x[3:0] <= 9;

// tens * 10 as (tens << 3) + (tens << 1): no multiplier block
function Bit#(7) bcdToBin(Bit#(8) x);
   Bit#(7) t = zeroExtend(x[7:4]);
   return (t << 3) + (t << 1) + zeroExtend(x[3:0]);
endfunction

// Years 00..99 stand for 1970..2069 (devrtc.c rtctime); every year
// divisible by 4 in that range is a leap year, 2000 included.
function Bool leapYear(Bit#(8) y);
   Bit#(4) s = (zeroExtend(y[4]) << 1) + y[3:0];
   return s[1:0] == 0;
endfunction

function Bit#(8) monthDays(Bit#(8) mon, Bit#(8) year);
   case (mon)
      8'h02:   return leapYear(year) ? 8'h29 : 8'h28;
      8'h04, 8'h06, 8'h09, 8'h11: return 8'h30;
      default: return 8'h31;
   endcase
endfunction

// Day of the week, 1 = Sunday .. 7 = Saturday (the model's
// bcd((tm_wday + 1) % 7 + 1)).  Sakamoto's rule with the century folded
// in: for Y = 1900 + k (k = 69..169 after the Jan/Feb adjustment),
// Y + Y/4 - Y/100 + Y/400 = 2360 + k + k/4, and 2360 mod 7 = 1.
function Bit#(8) weekDay(Bit#(8) year, Bit#(8) mon, Bit#(8) mday);
   Bit#(8) yy = zeroExtend(bcdToBin(year));
   Bit#(8) m  = zeroExtend(bcdToBin(mon));
   Bit#(8) k  = ((yy < 70) ? yy + 100 : yy) - ((m < 3) ? 1 : 0);
   Bit#(8) t  = case (m)
                   1: 0;  2: 3;  3: 2;  4: 5;  5: 0;  6: 3;
                   7: 5;  8: 1;  9: 4; 10: 6; 11: 2; default: 4;
                endcase;
   Bit#(9) s = 1 + zeroExtend(k) + zeroExtend(k >> 2) + zeroExtend(t)
               + zeroExtend(bcdToBin(mday));
   // mod 7 by folding octal digits (8 = 1 mod 7)
   Bit#(6) f1 = zeroExtend(s[8:6]) + zeroExtend(s[5:3]) + zeroExtend(s[2:0]);
   Bit#(4) f2 = zeroExtend(f1[5:3]) + zeroExtend(f1[2:0]);
   Bit#(3) f3 = zeroExtend(f2[3]) + f2[2:0];
   Bit#(3) d  = (f3 == 7) ? 0 : f3;
   return zeroExtend(d) + 1;
endfunction

function Bool timeValid(RtcTime t) =
   bcdValid(t.year) && bcdValid(t.mon) && bcdValid(t.mday)
   && bcdValid(t.hour) && bcdValid(t.min) && bcdValid(t.sec)
   && t.mon >= 8'h01 && t.mon <= 8'h12
   && t.mday >= 8'h01 && t.mday <= monthDays(t.mon, t.year)
   && t.hour <= 8'h23 && t.min <= 8'h59 && t.sec <= 8'h59;

function RtcTime nextSecond(RtcTime t);
   RtcTime n = t;
   if (t.sec != 8'h59) n.sec = bcdInc(t.sec);
   else begin
      n.sec = 0;
      if (t.min != 8'h59) n.min = bcdInc(t.min);
      else begin
         n.min = 0;
         if (t.hour != 8'h23) n.hour = bcdInc(t.hour);
         else begin
            n.hour = 0;
            n.wday = (t.wday == 7) ? 1 : t.wday + 1;
            if (t.mday != monthDays(t.mon, t.year)) n.mday = bcdInc(t.mday);
            else begin
               n.mday = 1;
               if (t.mon != 8'h12) n.mon = bcdInc(t.mon);
               else begin
                  n.mon = 1;
                  n.year = (t.year == 8'h99) ? 0 : bcdInc(t.year);
               end
            end
         end
      end
   end
   return n;
endfunction

function Bit#(8) field(RtcTime t, Bit#(3) i);
   case (i)
      1: return t.sec;   2: return t.min;   3: return t.hour;
      4: return t.wday;  5: return t.mday;  6: return t.mon;
      default: return t.year;
   endcase
endfunction

function RtcTime setField(RtcTime t, Bit#(3) i, Bit#(8) v);
   case (i)
      1: t.sec = v;   2: t.min = v;   3: t.hour = v;
      4: t.wday = v;  5: t.mday = v;  6: t.mon = v;
      7: t.year = v;
   endcase
   return t;
endfunction

// ---- the device ---------------------------------------------------------

module mkRtcCore#(Bit#(32) ticksPerSec, RtcTime start, String nvramFile)
                 (RtcIfc);
   // NVRAM: one block RAM; the read address is registered (rdAddr), so
   // yosys maps it to a DP16KD (docs/area_analysis.md).
   RegFile#(Bit#(11), Bit#(8)) nvram <- mkRegFileLoad(nvramFile, 0, 2039);
   Reg#(Bit#(11)) rdAddr <- mkRegU;
   Reg#(Bool)     rdPend <- mkReg(False);

   Reg#(RtcTime)  now     <- mkReg(start);
   Reg#(Bit#(32)) div     <- mkReg(0);
   Reg#(Bit#(8))  control <- mkReg(0);
   Reg#(Bool)     isHeld  <- mkReg(False);
   Reg#(RtcTime)  held    <- mkRegU;
   Reg#(Bit#(8))  faultR  <- mkReg(0);

   RWire#(RtcTime) loadW <- mkRWire;
   FIFOF#(Bit#(32)) resp <- mkFIFOF;

   (* fire_when_enabled, no_implicit_conditions *)
   rule step;
      if (loadW.wget matches tagged Valid .t) begin
         now <= t;
         div <= 1;            // the load cycle counts as the first
      end
      else if (div == ticksPerSec - 1) begin
         now <= nextSecond(now);
         div <= 0;
      end
      else
         div <= div + 1;
   endrule

   rule nvRead (rdPend);
      resp.enq(zeroExtend(nvram.sub(rdAddr)));
      rdPend <= False;
   endrule

   function Action failWith(Bit#(8) code, String what) = action
      if (faultR == 0) faultR <= code;
      $display("RTC FAULT %0d: %s", code, what);
   endaction;

   method Action request(Bit#(13) addr, Bit#(32) wdata, Bit#(4) be,
                         Bool write) if (!rdPend);
      Bit#(11) idx = addr[12:2];
      Bit#(8)  v   = wdata[7:0];
      Bool     isNv = idx < 2040;
      Bit#(3)  reg_ = idx[2:0];
      if (!write) begin
         if (isNv) begin
            rdAddr <= idx;
            rdPend <= True;
         end
         else if (reg_ == 0)
            resp.enq(zeroExtend(control));
         else
            resp.enq(zeroExtend(field(isHeld ? held : now, reg_)));
      end
      else begin
         resp.enq(0);
         if (be[0] == 0)
            failWith(rtcFaultLane, "write without byte lane 0");
         else if (isNv)
            nvram.upd(idx, v);
         else if (reg_ != 0) begin
            if (!isHeld || control[7] == 0)
               failWith(rtcFaultRegWriteNoW,
                        "clock register written without RTCWRITE");
            else
               held <= setField(held, reg_, v);
         end
         else begin
            Bit#(8) was = control;
            control <= v;
            if (v[7:6] != 0 && was[7:6] == 0) begin
               held <= now;
               isHeld <= True;
            end
            else if (was[7] == 1 && v[7] == 0) begin
               RtcTime t = held;
               t.wday = weekDay(t.year, t.mon, t.mday);
               if (!isHeld)
                  // W set again after a load with R still set: the model
                  // has no held set to load (Timekeeper.write fails).
                  failWith(rtcFaultNoHeld,
                           "RTCWRITE cleared with no registers held");
               else if (timeValid(t)) loadW.wset(t);
               else failWith(rtcFaultBadLoad,
                             "RTCWRITE cleared with an invalid time");
               isHeld <= False;
            end
            else if (v[7:6] == 0)
               isHeld <= False;
         end
      end
   endmethod

   method ActionValue#(Bit#(32)) response;
      resp.deq;
      return resp.first;
   endmethod

   method Bool irq = False;
   method Bit#(8) fault = faultR;
endmodule

// The synthesised device.  ticksPerSec is the CLK frequency; startBcd is
// {year, mon, mday, wday, hour, min, sec} in BCD (rtc.md "Start time";
// the default build value is 1993-01-03 12:00:00, a Sunday, the model's
// RTC_BASE).  The NVRAM's initial contents are rtc_nvram.hex.
(* synthesize *)
module mkRtc#(parameter Bit#(32) ticksPerSec, parameter Bit#(56) startBcd)
             (RtcIfc);
   let m <- mkRtcCore(ticksPerSec, unpack(startBcd), "rtc_nvram.hex");
   return m;
endmodule

endpackage
