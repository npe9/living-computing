// WinLiveTb: the board's composition (WinUlx3s.bsv mkWinBoardCore: the
// framebuffer box, the scan-out, the host link, the input box) in its two
// clock domains, with the host's screen, keyboard and mouse emulated
// (WinHostDev.bsv / WinHostDev.c).  HAND-WRITTEN (committed);
// docs/simpos/window_hardware_plan.md H7s and §4.1.  Driven by
// bsv/run_win_live.sh (scripted, in the suite; or interactive, with
// tools/winview), whose header records the injected faults.  OURS.
//
// The clocks (Bluesim time units): pclk period 10 (74 MHz on the board),
// sys period 27 (25 MHz), unrelated, as WinUlx3sTb.  No shift clock: the
// monitor takes the pixel before the TMDS encoders (the serializer is
// WinUlx3sTb's and WinTmdsSerTb's).  Scaled timing (OURS): the link 4
// cycles a bit, a PS/2 half bit 6 cycles, the input box's filter 2,
// timeout 200, a millisecond 100 cycles.
//
// In the working directory at time 0: win_font.hex, win_stream.hex (the
// self-test's stream: an end record only, so the frame starts blank as
// the Python device's does), win_scan.hex (the scan configuration,
// psi/winscan.py's, cursor off).
package WinLiveTb;

import Clocks::*;
import WinUlx3s::*;
import WinHostDev::*;

(* synthesize *)
module mkWinLiveTb(Empty);
   Clock pclk <- mkAbsoluteClockFull(5, 1'b0, 5, 5);
   Clock sys <- mkAbsoluteClockFull(7, 1'b0, 13, 14);
   Reset sysRst <- mkInitialReset(4, clocked_by sys);
   Reset prst <- mkAsyncReset(2, sysRst, pclk);

   WinBoardCore core <- mkWinBoardCore("win_font.hex", "win_stream.hex", "win_scan.hex",
                                       4, 2, 200, 100, pclk, prst,
                                       clocked_by sys, reset_by sysRst);
   WinHostDev host <- mkWinHostDev(4, 6, 100, clocked_by sys, reset_by sysRst);
   Empty mon <- mkWinMonitor(core.video, clocked_by pclk, reset_by prst);

   (* fire_when_enabled, no_implicit_conditions *)
   rule wires;
      core.kbd(host.kbdClk, host.kbdDat);
      core.mouse(host.mouseClk, host.mouseDat);
      core.uart(host.rxd);
      host.txd(core.txd);
   endrule
endmodule

endpackage
