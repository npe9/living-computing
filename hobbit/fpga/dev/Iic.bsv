// Iic.bsv -- the Hobbit board's IIC bus at IOBASE+0x80: a PCF8584
// controller, register level, with the bus's two devices behind it: the
// PCF8582 256-byte EEPROM (address 0xA4) and the PCF8574 LED latch
// (address 0x40).
//
// Behaviour reference: tools/p9boot.py `class Iic` and IIC_CHOICES;
// driver: tools/plan9-1e/sys/src/9/hobbit/deviic.c; register map: io.h
// `Iic` (data = S0 at +0, ctl = S1 at +4, IOACK(Iic, 0x0080)); data sheet
// quotations: docs/devices/README.md "IIC".  Design notes and the test
// are in iic.md.
//
// There are no SCL/SDA pins: the bus is inside this module and every
// transfer completes at once, as in the model, so PIN is already clear
// when the driver first polls it.  The branches are the model's, in the
// model's order:
//   S1 read  = PIN 0x80 | LRB 0x08 (no acknowledge) | BB 0x01 (bus free)
//   S0 write, ESO off: S0' (own address) or S2 (clock) per ES1/ES2
//   S0 write, ESO on : S0 := byte; in a write transfer the byte goes to
//                      the slave (EEPROM word address, or LED latch); a
//                      second byte to the EEPROM is held as the repeated
//                      START's address (IIC_CHOICES['repeated-start'])
//   S0 read          : returns S0; in a read transfer with ACK set, the
//                      next EEPROM byte is fetched into S0 (the first
//                      read is the data sheet's dummy read)
//   S1 write, ESO on : STA (not STO) -> (repeated) START with S0 as the
//                      address; STO (not STA) -> STOP; PIN in a read
//                      transfer -> the byte in progress completes (the
//                      driver's 0xC0); PIN otherwise -> PIN set
//
// Fail loud (`fault`, sticky; the response is still given, data 0): every
// access the model stops on -- S0 read with ESO off, a register select
// other than S0'/S2, an offset outside the two registers -- and a write
// without byte lane 0.
package Iic;

import RegFile :: *;
import FIFOF   :: *;

export IicIfc(..);
export mkIic;
export mkIicCore;
export iicFaultNone, iicFaultOffset, iicFaultS0ReadEsoOff,
       iicFaultRegSelect, iicFaultLane;

interface IicIfc;
   // Device bus contract (docs/ulx3s_plan.md).
   method Action request(Bit#(12) addr, Bit#(32) wdata, Bit#(4) be,
                         Bool write);
   method ActionValue#(Bit#(32)) response;
   (* always_ready *) method Bool irq;                // the driver runs without interrupts
   (* always_ready *) method Bit#(8) fault;           // 0, or the first fault's code
   (* always_ready *) method Bit#(8) led;             // the PCF8574 latch's last byte
   (* always_ready *) method Bit#(8) ledWrites;       // count of bytes written to it (mod 256)
endinterface

Bit#(8) iicFaultNone         = 0;
Bit#(8) iicFaultOffset       = 1;   // not +0 (S0) or +4 (S1)
Bit#(8) iicFaultS0ReadEsoOff = 2;   // S0 read with the serial bus off
Bit#(8) iicFaultRegSelect    = 3;   // S0 write selecting S3 (vector) etc.
Bit#(8) iicFaultLane         = 4;   // write without byte lane 0

Bit#(8) ctlPIN = 8'h80;
Bit#(8) ctlESO = 8'h40;
Bit#(8) ctlSTA = 8'h04;
Bit#(8) ctlSTO = 8'h02;
Bit#(8) ctlACK = 8'h01;

Bit#(7) devEeprom = 7'h52;          // 0xA4 >> 1
Bit#(7) devLed    = 7'h20;          // 0x40 >> 1

module mkIicCore#(String eepromFile)(IicIfc);
   RegFile#(Bit#(8), Bit#(8)) eeprom <- mkRegFileLoad(eepromFile, 0, 255);

   Reg#(Bit#(8)) own      <- mkReg(0);      // S0', written, never read
   Reg#(Bit#(8)) clockReg <- mkReg(0);      // S2, written, never read
   Reg#(Bit#(8)) ctl      <- mkReg(0);
   Reg#(Bit#(8)) s0       <- mkReg(0);
   Reg#(Bool)    pin      <- mkReg(True);
   Reg#(Bool)    lrb      <- mkReg(False);
   Reg#(Bool)    busy     <- mkReg(False);  // a START is outstanding
   Reg#(Bit#(8)) slave    <- mkReg(0);      // its address byte
   Reg#(Bit#(8)) ptr      <- mkReg(0);      // EEPROM word address
   Reg#(Bool)    ptrSet   <- mkReg(False);
   Reg#(Bit#(8)) ledR     <- mkReg(0);
   Reg#(Bit#(8)) ledN     <- mkReg(0);
   Reg#(Bit#(8)) faultR   <- mkReg(0);

   FIFOF#(Bit#(32)) resp <- mkFIFOF;

   function Bool known(Bit#(8) a) =
      a[7:1] == devEeprom || a[7:1] == devLed;

   function Action failWith(Bit#(8) code, String what) = action
      if (faultR == 0) faultR <= code;
      $display("IIC FAULT %0d: %s", code, what);
   endaction;

   method Action request(Bit#(12) addr, Bit#(32) wdata, Bit#(4) be,
                         Bool write);
      Bit#(8) d = wdata[7:0];
      Bool reading = busy && slave[0] == 1;       // master receiver
      Bool writing = busy && slave[0] == 0;       // master transmitter
      if (addr[11:3] != 0) begin
         resp.enq(0);
         failWith(iicFaultOffset, "access outside S0/S1");
      end
      else if (!write) begin
         if (addr[2] == 1)
            resp.enq(zeroExtend({pack(pin), 3'b0, pack(lrb), 2'b0,
                                 pack(!busy)}));
         else if ((ctl & ctlESO) == 0) begin
            resp.enq(0);
            failWith(iicFaultS0ReadEsoOff, "S0 read with ESO off");
         end
         else begin
            resp.enq(zeroExtend(s0));
            if (reading && (ctl & ctlACK) != 0) begin
               s0  <= eeprom.sub(ptr);
               ptr <= ptr + 1;
               pin <= False;
               lrb <= False;
            end
         end
      end
      else begin
         resp.enq(0);
         if (be[0] == 0)
            failWith(iicFaultLane, "write without byte lane 0");
         else if (addr[2] == 0) begin
            if ((ctl & ctlESO) == 0) begin
               case (ctl[5:4])                     // ES1, ES2
                  2'b00:   own <= d;
                  2'b10:   clockReg <= d;
                  default: failWith(iicFaultRegSelect,
                                    "S0 write to a register other than S0'/S2");
               endcase
            end
            else begin
               s0 <= d;
               if (writing) begin
                  // Model `_transmitted`.
                  if (slave[7:1] == devEeprom && ptrSet)
                     pin <= True;     // held as the repeated START's address
                  else begin
                     pin <= False;
                     lrb <= !known(slave);
                     if (slave[7:1] == devEeprom) begin
                        ptr <= d;
                        ptrSet <= True;
                     end
                     else if (slave[7:1] == devLed) begin
                        ledR <= d;
                        ledN <= ledN + 1;
                     end
                  end
               end
            end
         end
         else begin
            ctl <= d;
            Bool sta = (d & ctlSTA) != 0;
            Bool sto = (d & ctlSTO) != 0;
            if ((d & ctlESO) != 0) begin
               if (sta && !sto) begin
                  // Model `_start`: (repeated) START, address from S0.
                  busy  <= True;
                  slave <= s0;
                  pin   <= False;
                  lrb   <= !known(s0);
                  if (s0[7:1] == devEeprom && s0[0] == 0)
                     ptrSet <= False;
               end
               else if (sto && !sta) begin
                  busy <= False;
                  pin  <= True;
               end
               else if ((d & ctlPIN) != 0 && reading)
                  pin <= False;   // the byte in progress completes
               else if ((d & ctlPIN) != 0)
                  pin <= True;
            end
         end
      end
   endmethod

   method ActionValue#(Bit#(32)) response;
      resp.deq;
      return resp.first;
   endmethod

   method Bool irq = False;
   method Bit#(8) fault = faultR;
   method Bit#(8) led = ledR;
   method Bit#(8) ledWrites = ledN;
endmodule

// The synthesised device; the EEPROM's contents are iic_eeprom.hex
// (generated by iic_eeprom.py from p9boot.eeprom_image()).
(* synthesize *)
module mkIic(IicIfc);
   let m <- mkIicCore("iic_eeprom.hex");
   return m;
endmodule

endpackage
