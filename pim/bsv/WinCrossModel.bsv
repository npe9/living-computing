// WinCrossModel: a bench model of the pixel-to-shift-clock crossing of
// mkWinTmdsSer (bsv/WinScanOut.bsv).  HAND-WRITTEN BENCH SUPPORT, OURS;
// docs/simpos/window_hardware_plan.md H3.  Used by WinTmdsSerTb and
// WinUlx3sTb in place of a plain mkNullCrossingWire.
//
// Bluesim's clocks are ideal: a shift-clock rule reading the pixel
// domain's characters sees a clean value on every edge, so a serializer
// that samples on the edge where the characters change passes (H2's
// injection #14 was caught by nothing).  This model makes that sample
// visible.  In the shift domain it watches the pixel domain's `tog` (a
// bit flipped every pixel clock, so it changes exactly when the
// characters do) and counts the shift edges since the change was first
// seen, the `age`, 0-4 at five shift clocks a pixel.  A read of the
// characters at age 0 (the edge of the change: on the board the old or
// the new word, by routing) or age 4 (the edge before the next change,
// which in Bluesim's ordering of two coincident edges may be the change
// itself) returns them inverted, a poisoned value no lane check accepts.
// Ages 1-3 are clean.  The model says nothing about real delays: it
// only requires the serializer's sample phase to be a fixed distance
// from the pixel edge with at least one clean edge on each side.
// bsv/run_win_fpga.sh checks the real routed delay.
// `tog` itself is passed clean: the serializer synchronizes it.
package WinCrossModel;

import Vector::*;

interface WinCrossModel;
   interface ReadOnly#(Vector#(3, Bit#(10))) w;
   interface ReadOnly#(Bool) tog;
endinterface

module mkWinCrossModel#(ReadOnly#(Vector#(3, Bit#(10))) wRaw, ReadOnly#(Bool) togRaw)(WinCrossModel);
   Reg#(Bool) r1 <- mkReg(False);
   Reg#(UInt#(3)) age <- mkReg(7);
   Bool changed = togRaw != r1;
   UInt#(3) ageNow = changed ? 0 : (age == 7 ? 7 : age + 1);
   Bool unsafe = ageNow == 0 || ageNow >= 4;

   (* fire_when_enabled, no_implicit_conditions *)
   rule track;
      r1 <= togRaw;
      age <= ageNow;
   endrule

   interface ReadOnly w;
      method Vector#(3, Bit#(10)) _read = unsafe ? map(invert, wRaw) : wRaw;
   endinterface
   interface ReadOnly tog;
      method Bool _read = togRaw;
   endinterface
endmodule

endpackage
