// HobbitSocDevs.bsv -- the SoC's RTL devices behind one bus port, with a
// per-device "RTL or forwarded" switch (fpga/README.md, "Devices").
//
// rtl/hobbit_soc.v's backend router asks `claims(pa)` for every I/O
// access. A claimed access goes to the RTL device here: `req`, then one
// `resp`. Any other access is forwarded over the host link to
// tools/p9host.py's p9boot models, as before. The devices are the ones the
// device agents wrote under fpga/dev/ and are used unchanged. The decode is
// p9boot.py's map, which follows io.h. Offsets follow the device contract
// (docs/ulx3s_plan.md): 13 bits, the RTC's window being 8 KB.
//
//   bit of `rtl`  device           window (physical)
//   0             incon            0xB0000000-0xB0000013
//                 ioctl            0xB8000000-0xB8000003
//                 irq              0xB8000080-0xB800008F
//   1             Quart            0xB0000100-0xB00001FF
//   2             RTC + NVRAM      0xB8002000-0xB8003FFF
//   3             IIC + EEPROM     0xB0000080-0xB0000087
//   4             Lcdisp           0xB0003000-0xB0003007
//   5             SONIC            0xA4400000-0xA44000FF
//
// The SONIC's DMA (`dmaReq`/`dmaRdata`, fpga/dev/sonic.md) goes to
// hobbit_soc's SDRAM arbiter; its frames go through EspLink to the ESP32
// pins (`esp*`, docs/ulx3s_ethernet.md, 2.5 Mbaud = 10 clocks per bit).
// Lcdisp's frame store is scanned out in the pixel clock domain (`scan`,
// `pclk`) by the HDMI path in the board top (fpga/dev/hdmi_*).
//
// Interrupts: Irq.sources gets every source each clock. Bit 1 is the
// Quart's irq (or the host's, when the Quart is forwarded), and bits 5,
// 8, 9 and 10 (incon, SCSI DMA, SONIC, SCSI) come from `hostSources`,
// the host models' source bits, carried by the host link's 'S' frame.
// The core's level is 6 while the RTL Irq asserts (`il6`).
package HobbitSocDevs;

import FIFOF :: *;
import GetPut :: *;
import Vector :: *;
import HobbitQuart :: *;
import HobbitIntc :: *;
import Rtc :: *;
import Iic :: *;
import LcdLcdisp :: *;
import Sonic :: *;
import EspLink :: *;
import Connectable :: *;

typedef enum { DNone, DIncon, DIoctl, DIrq, DQuart, DRtc, DIic, DLcd, DSonic } Dev
  deriving (Bits, Eq);

interface HobbitSocDevs;
  (* always_ready *) method Bool claims(Bit#(32) pa);
  method Action req(Bit#(32) pa, Bit#(32) wdata, Bit#(4) be, Bool write);
  method ActionValue#(Bit#(32)) resp;
  (* always_ready, always_enabled *) method Action hostSources(Bit#(16) s);
  (* always_ready *) method Bool il6;
  // Quart channel 0's serial pins (the console).
  (* always_ready *) method Bit#(1) quartTxd;
  (* always_ready, always_enabled *) method Action quartRxd(Bit#(1) v);
  // The RTC's MCP7940N link (open drain: 1 = pull low).
  (* always_ready *) method Bit#(1) i2cSclLow;
  (* always_ready *) method Bit#(1) i2cSdaLow;
  (* always_ready, always_enabled *) method Action i2cPins(Bit#(1) scl, Bit#(1) sda);
  // Any device's fault flag (a register access p9boot would refuse).
  (* always_ready *) method Bit#(8) faults;
  (* always_ready *) method Bit#(8) iicLed;
  // The SONIC's DMA master: one 32-bit word per request, reads answered
  // in order.
  interface Get#(SonicDmaReq) dmaReq;
  interface Put#(Bit#(32)) dmaRdata;
  // EspLink's pins: txd to the ESP32's GPIO16 (L1); rxd from GPIO17 (N3)
  // and RTS from GPIO4 (H1).
  (* always_ready *) method Bit#(1) espTxd;
  (* always_ready, always_enabled *) method Action espPins(Bit#(1) rxd, Bit#(1) rts);
  // Lcdisp's scan port, in the pixel clock domain.
  interface LcdScan scan;
endinterface

function Dev decode(Bit#(8) rtl, Bit#(32) pa);
  Dev d = DNone;
  if (pa >= 32'hB0000000 && pa < 32'hB0000014 && rtl[0] == 1) d = DIncon;
  else if (pa >= 32'hB8000000 && pa < 32'hB8000004 && rtl[0] == 1) d = DIoctl;
  else if (pa >= 32'hB8000080 && pa < 32'hB8000090 && rtl[0] == 1) d = DIrq;
  else if (pa >= 32'hB0000100 && pa < 32'hB0000200 && rtl[1] == 1) d = DQuart;
  else if (pa >= 32'hB8002000 && pa < 32'hB8004000 && rtl[2] == 1) d = DRtc;
  else if (pa >= 32'hB0000080 && pa < 32'hB0000088 && rtl[3] == 1) d = DIic;
  else if (pa >= 32'hB0003000 && pa < 32'hB0003008 && rtl[4] == 1) d = DLcd;
  else if (pa >= 32'hA4400000 && pa < 32'hA4400100 && rtl[5] == 1) d = DSonic;
  return d;
endfunction

// clksPerBit 1302 = 19200 baud and ctNum/ctDen = 1152/125000 at 25 MHz
// (fpga/dev/quart/README.md); ticksPerSec is CLK's frequency.
(* synthesize *)
module mkHobbitSocDevs#(Clock pclk,
                        parameter Bit#(8) rtl, parameter Bit#(32) ticksPerSec,
                        parameter Bit#(56) startBcd, parameter Bit#(2) mcpMode,
                        parameter Bit#(16) i2cQuarter)(HobbitSocDevs);
  Clock clk <- exposeCurrentClock;
  HobbitIncon incon <- mkHobbitIncon;
  HobbitIoctl ioctl <- mkHobbitIoctl;
  HobbitIrq irq <- mkHobbitIrq;
  HobbitQuart quart <- mkHobbitQuart(1302, 1152, 125000);
  RtcIfc rtc <- mkRtc(ticksPerSec, startBcd, mcpMode, i2cQuarter);
  IicIfc iic <- mkIic;
  Lcdisp lcd <- mkLcdisp(pclk);
  HobbitSonic sonic <- mkSonic;
  EspLink esp <- mkEspLink(10);       // 25 MHz / 2.5 Mbaud
  mkConnection(sonic.tx, esp.tx);
  mkConnection(esp.rx, sonic.rx);

  Reg#(Dev) pend <- mkReg(DNone);
  FIFOF#(Bit#(32)) respQ <- mkFIFOF;
  Wire#(Bit#(16)) hostSrcW <- mkBypassWire;

  // Channels 1-3 of the Quart have no pins: always-ready sinks.
  for (Integer i = 0; i < 3; i = i + 1)
    rule sinkTx;
      let b <- quart.txOut[i].get;
    endrule

  (* fire_when_enabled, no_implicit_conditions *)
  rule drive_sources;
    Bit#(16) s = hostSrcW;
    if (rtl[1] == 1) s[1] = pack(quart.irq);
    if (rtl[5] == 1) s[9] = pack(sonic.irq);
    irq.sources(s);
  endrule

  rule r_incon (pend == DIncon); let v <- incon.resp; respQ.enq(v); pend <= DNone; endrule
  rule r_ioctl (pend == DIoctl); let v <- ioctl.resp; respQ.enq(v); pend <= DNone; endrule
  rule r_irq (pend == DIrq); let v <- irq.resp; respQ.enq(v); pend <= DNone; endrule
  rule r_quart (pend == DQuart); let v <- quart.resp; respQ.enq(v); pend <= DNone; endrule
  rule r_rtc (pend == DRtc); let v <- rtc.response; respQ.enq(v); pend <= DNone; endrule
  rule r_iic (pend == DIic); let v <- iic.response; respQ.enq(v); pend <= DNone; endrule
  rule r_lcd (pend == DLcd); let v <- lcd.resp; respQ.enq(v); pend <= DNone; endrule
  rule r_sonic (pend == DSonic); let v <- sonic.resp; respQ.enq(v); pend <= DNone; endrule

  method Bool claims(Bit#(32) pa) = decode(rtl, pa) != DNone;

  method Action req(Bit#(32) pa, Bit#(32) wdata, Bit#(4) be, Bool write)
      if (pend == DNone && !respQ.notEmpty);
    let d = decode(rtl, pa);
    case (d)
      DIncon: incon.req(truncate(pa - 32'hB0000000), wdata, be, write);
      DIoctl: ioctl.req(truncate(pa - 32'hB8000000), wdata, be, write);
      DIrq:   irq.req(truncate(pa - 32'hB8000080), wdata, be, write);
      DQuart: quart.req(truncate(pa - 32'hB0000100), wdata, be, write);
      DRtc:   rtc.request(truncate(pa - 32'hB8002000), wdata, be, write);
      DIic:   iic.request(truncate(pa - 32'hB0000080), wdata, be, write);
      DLcd:   lcd.req(truncate(pa - 32'hB0003000), wdata, be, write);
      DSonic: sonic.req(truncate(pa - 32'hA4400000), wdata, be, write);
    endcase
    if (d == DNone) respQ.enq(0);      // not claimed: never sent here
    else pend <= d;
  endmethod

  method ActionValue#(Bit#(32)) resp;
    respQ.deq;
    return respQ.first;
  endmethod

  method Action hostSources(Bit#(16) s) = hostSrcW._write(s);
  method Bool il6 = rtl[0] == 1 && irq.il6;
  method Bit#(1) quartTxd = quart.txd;
  method Action quartRxd(Bit#(1) v) = quart.rxd(v);
  // A forwarded RTC leaves the MCP7940N's lines released.
  method Bit#(1) i2cSclLow = rtl[2] == 1 ? rtc.i2cSclLow : 0;
  method Bit#(1) i2cSdaLow = rtl[2] == 1 ? rtc.i2cSdaLow : 0;
  method Action i2cPins(Bit#(1) scl, Bit#(1) sda) = rtc.i2cPins(scl, sda);
  method Bit#(8) faults = {3'b0, pack(lcd.overruns != 0), pack(iic.fault != 0),
                           pack(rtc.fault != 0), pack(quart.fault || sonic.fault),
                           pack(incon.fault || ioctl.fault || irq.fault)};
  method Bit#(8) iicLed = iic.led;
  interface dmaReq = sonic.dma.req;
  interface dmaRdata = sonic.dma.rdata;
  method Bit#(1) espTxd = esp.txd;
  method Action espPins(Bit#(1) rxd, Bit#(1) rts) = esp.pins(rxd, rts);
  interface scan = lcd.scan;
endmodule

endpackage
