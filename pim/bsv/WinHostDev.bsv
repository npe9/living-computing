// WinHostDev: the host's screen, keyboard and mouse for the window
// hardware in Bluesim (docs/simpos/window_hardware_plan.md §4.1, H7s).
// BLUESIM ONLY: the C side is WinHostDev.c (its header is the
// specification); `import "BDPI"` has no form yosys takes, so no board
// top imports this package (the PimmSdBlockFile.bsv split).  ALL OURS.
//
// Owner, 2026-11-26: "Figure out how to do emulate the mouse, keyboard and
// screen in bluesim."  mkWinHostDev is that emulation's bench side:
//   - THE SCREEN: a virtual monitor on the scan-out's composed pixel
//     (WinScanOut.bsv `video`: DE, the sync levels, the level), every
//     pixel clock, before the TMDS encoders; WinHostDev.c checks the
//     timing against its own mode table and takes the frame;
//   - THE KEYBOARD AND MOUSE: two PS/2 device models (WinInput.bsv
//     mkWinPs2Dev) on the input box's PINS, fed with the bytes
//     WinHostDev.c makes from host events (HID usage -> set 2 make/break,
//     mouse motion and buttons -> 3-byte packets);
//   - THE HOST END OF THE LINK: a UART pair (WinLink.bsv) on the board's
//     lines; WinHostDev.c parses the up records and sends the kl0 host's
//     frames down with the link's flow control.
// Its back ends (scripted, the suite's; a viewer socket, interactive) are
// chosen in WinHostDev.c by the environment.
package WinHostDev;

import GetPut::*;
import WinInput::*;
import WinLink::*;

import "BDPI" function ActionValue#(Bit#(32)) whd_init(Bit#(32) msDiv);
import "BDPI" function ActionValue#(Bit#(32)) whd_tick(Bit#(32) lo, Bit#(32) hi, Bit#(32) idle);
import "BDPI" function ActionValue#(Bit#(32)) whd_kbd();
import "BDPI" function ActionValue#(Bit#(32)) whd_mouse();
import "BDPI" function Action whd_up(Bit#(32) b);
import "BDPI" function ActionValue#(Bit#(32)) whd_down();
import "BDPI" function Action whd_px(Bit#(32) v);
import "BDPI" function Action whd_report();

// the board's side of the wires, as the bench sees them
interface WinHostDev;
   method Bit#(1) kbdClk;
   method Bit#(1) kbdDat;
   method Bit#(1) mouseClk;
   method Bit#(1) mouseDat;
   method Bit#(1) rxd;                     // the host's line out (the board's in)
   (* always_ready, always_enabled *) method Action txd(Bit#(1) b);   // the board's line out
endinterface

// the monitor, in the pixel domain: one call a pixel clock
module mkWinMonitor#(Tuple3#(Bool, Bit#(2), Bit#(8)) video)(Empty);
   (* fire_when_enabled, no_implicit_conditions *)
   rule pixel;
      match {.de, .c, .lev} = video;
      whd_px(zeroExtend({pack(de), c, lev}));
   endrule
endmodule

// div: the link's clocks a bit; half: a PS/2 half bit, cycles; msDiv:
// cycles a millisecond (the input box's)
module mkWinHostDev#(Integer div, Integer half, Integer msDiv)(WinHostDev);
   WinPs2Dev kd <- mkWinPs2Dev(half);
   WinPs2Dev md <- mkWinPs2Dev(half);
   WinUartTx htx <- mkWinUartTx(div);
   WinUartRx hrx <- mkWinUartRx(div, "WinHostDev host");
   Wire#(Bit#(1)) txW <- mkBypassWire;
   Reg#(Bool) started <- mkReg(False);
   Reg#(Bit#(64)) cycles <- mkReg(0);
   Reg#(Bit#(16)) sinceUp <- mkReg(0);
   Reg#(Bit#(16)) sinceDown <- mkReg(0);
   PulseWire upW <- mkPulseWire;
   PulseWire downW <- mkPulseWire;

   rule line;
      hrx.rxd(txW);
   endrule
   rule init (!started);
      let m <- whd_init(fromInteger(msDiv));
      started <= True;
   endrule
   rule count (started);
      cycles <= cycles + 1;
      sinceUp <= upW ? 0 : (sinceUp == '1 ? sinceUp : sinceUp + 1);
      sinceDown <= downW ? 0 : (sinceDown == '1 ? sinceDown : sinceDown + 1);
   endrule
   rule tick (started && cycles[5:0] == 0);
      Bool linkQuiet = sinceUp > fromInteger(40 * div) && sinceDown > fromInteger(40 * div);
      Bit#(32) idle = {29'b0, pack(linkQuiet), pack(md.idle), pack(kd.idle)};
      let r <- whd_tick(cycles[31:0], cycles[63:32], idle);
      if (r[0] == 1) begin
         whd_report;
         $finish(r[1] == 1 ? 1 : 0);
      end
   endrule
   rule kbdFeed (started && cycles[3:0] == 1);
      let v <- whd_kbd;
      if (v[31] == 1) kd.req.put(Ps2DevReq { b: v[7:0], fault: v[11:8], delay: 0 });
   endrule
   rule mouseFeed (started && cycles[3:0] == 2);
      let v <- whd_mouse;
      if (v[31] == 1) md.req.put(Ps2DevReq { b: v[7:0], fault: v[11:8], delay: 0 });
   endrule
   rule up (started);
      let b <- hrx.bytes.get;
      whd_up(zeroExtend(b));
      upW.send;
   endrule
   rule down (started && cycles[1:0] == 3);
      let v <- whd_down;
      if (v[31] == 1) begin
         htx.bytes.put(v[7:0]);
         downW.send;
      end
   endrule

   method Bit#(1) kbdClk = kd.clk;
   method Bit#(1) kbdDat = kd.dat;
   method Bit#(1) mouseClk = md.clk;
   method Bit#(1) mouseDat = md.dat;
   method Bit#(1) rxd = htx.txd;
   method Action txd(Bit#(1) b);
      txW <= b;
   endmethod
endmodule

endpackage
