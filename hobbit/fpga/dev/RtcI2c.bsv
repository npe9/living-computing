// RtcI2c.bsv -- a byte-level, open-drain I2C master for mkRtc's link to
// the ULX3S's MCP7940N (rtc.md "The MCP7940N").  Single master, standard
// mode: each bit is four quarters of `quarter` cycles (25 MHz / (4 * 63)
// = 99.2 kHz), SCL released in quarter 1 and held until the line reads
// high (clock stretching), SDA sampled at the start of quarter 2.
//
// Commands go in through `cmd`; every command gives one `resp`:
//   Start  (repeated START when the bus is already ours)   -> 0
//   Stop                                                    -> 0
//   Write b  (8 bits, MSB first, then the slave's ACK slot)  -> bit 0 = NACK
//   Read ack (8 bits in, then ACK driven if `ack`)           -> the byte
// bit 8 of the response is set when SCL was held low longer than
// `stretchMax` quarters; the command is abandoned and SCL/SDA released.
//
// Pins: `sclLow`/`sdaLow` = 1 pulls the line low (to the pad's output
// enable, data 0), 0 releases it; `pins` takes the lines as read back
// through the pads (two-flop synchronised here).
package RtcI2c;

import FIFOF :: *;

export I2cKind(..);
export I2cCmd(..);
export RtcI2cIfc(..);
export mkRtcI2c;

typedef enum { Start, Stop, Write, Read } I2cKind deriving (Bits, Eq);

typedef struct {
   I2cKind kind;
   Bit#(8) data;     // Write: the byte
   Bool    ack;      // Read: drive ACK after the byte
} I2cCmd deriving (Bits, Eq);

interface RtcI2cIfc;
   method Action cmd(I2cCmd c);
   method ActionValue#(Bit#(9)) resp;
   (* always_ready *) method Bit#(1) sclLow;
   (* always_ready *) method Bit#(1) sdaLow;
   (* always_ready, always_enabled *) method Action pins(Bit#(1) scl,
                                                         Bit#(1) sda);
endinterface

module mkRtcI2c#(Bit#(16) quarter, Bit#(20) stretchMax)(RtcI2cIfc);
   FIFOF#(I2cCmd)  cmdQ  <- mkFIFOF;
   FIFOF#(Bit#(9)) respQ <- mkFIFOF;

   Reg#(Bit#(1))  sclL  <- mkReg(0);
   Reg#(Bit#(1))  sdaL  <- mkReg(0);
   Reg#(Bit#(2))  sclM  <- mkReg(2'b11);
   Reg#(Bit#(2))  sdaM  <- mkReg(2'b11);
   Wire#(Bit#(1)) sclIn <- mkBypassWire;
   Wire#(Bit#(1)) sdaIn <- mkBypassWire;

   Reg#(Bool)     busy  <- mkReg(False);
   Reg#(I2cCmd)   cur   <- mkRegU;
   Reg#(Bit#(4))  slot  <- mkReg(0);
   Reg#(Bit#(2))  q     <- mkReg(0);
   Reg#(Bit#(16)) cnt   <- mkReg(0);
   Reg#(Bit#(20)) held  <- mkReg(0);
   Reg#(Bit#(8))  rx    <- mkReg(0);
   Reg#(Bit#(1))  nack  <- mkReg(0);

   Bit#(1) sclS = sclM[1];
   Bit#(1) sdaS = sdaM[1];

   (* fire_when_enabled, no_implicit_conditions *)
   rule sync;
      sclM <= {sclM[0], sclIn};
      sdaM <= {sdaM[0], sdaIn};
   endrule

   function Bit#(4) lastSlot(I2cKind k) =
      (k == Write || k == Read) ? 8 : 0;

   // What starts quarter qq of slot s.
   function Action enter(I2cCmd c, Bit#(4) s, Bit#(2) qq) = action
      case (c.kind)
         Start: case (qq)
                   0: sdaL <= 0;      // SDA high (a repeated START)
                   1: sclL <= 0;      // SCL high
                   2: sdaL <= 1;      // SDA falls with SCL high: START
                   3: sclL <= 1;
                endcase
         Stop:  case (qq)
                   0: sdaL <= 1;
                   1: sclL <= 0;
                   2: sdaL <= 0;      // SDA rises with SCL high: STOP
                   3: noAction;       // bus free time
                endcase
         default: case (qq)
                   0: begin
                         Bit#(1) low;
                         if (c.kind == Write)
                            low = (s == 8) ? 0 : ~c.data[7 - s[2:0]];
                         else
                            low = (s == 8) ? pack(c.ack) : 0;
                         sdaL <= low;
                      end
                   1: sclL <= 0;
                   2: begin
                         if (c.kind == Write && s == 8) nack <= sdaS;
                         if (c.kind == Read && s != 8) rx <= {rx[6:0], sdaS};
                      end
                   3: sclL <= 1;
                endcase
      endcase
   endaction;

   rule begin_ (!busy);
      let c = cmdQ.first;
      cmdQ.deq;
      cur  <= c;
      busy <= True;
      slot <= 0;
      q    <= 0;
      held <= 0;
      cnt  <= quarter - 1;
      enter(c, 0, 0);
   endrule

   rule step (busy);
      if (cnt != 0) begin
         if (q == 1 && sclS == 0) begin     // a slave holds SCL low
            if (held == stretchMax) begin
               sclL <= 0;
               sdaL <= 0;
               busy <= False;
               respQ.enq(9'h100);
            end
            held <= held + 1;
         end
         else
            cnt <= cnt - 1;
      end
      else if (q != 3) begin
         held <= 0;
         q <= q + 1;
         cnt <= quarter - 1;
         enter(cur, slot, q + 1);
      end
      else if (slot != lastSlot(cur.kind)) begin
         slot <= slot + 1;
         q <= 0;
         cnt <= quarter - 1;
         enter(cur, slot + 1, 0);
      end
      else begin
         busy <= False;
         respQ.enq(case (cur.kind)
                      Write:   zeroExtend(nack);
                      Read:    zeroExtend(rx);
                      default: 0;
                   endcase);
      end
   endrule

   method Action cmd(I2cCmd c) = cmdQ.enq(c);
   method ActionValue#(Bit#(9)) resp;
      respQ.deq;
      return respQ.first;
   endmethod
   method Bit#(1) sclLow = sclL;
   method Bit#(1) sdaLow = sdaL;
   method Action pins(Bit#(1) scl, Bit#(1) sda);
      sclIn <= scl;
      sdaIn <= sda;
   endmethod
endmodule

endpackage
