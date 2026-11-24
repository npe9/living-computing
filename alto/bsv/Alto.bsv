package Alto;

import AltoTypes::*;
import AltoMem::*;
import Disk::*;
import Display::*;
import Devices::*;
import Ethernet::*;
import CPU::*;

interface Alto_IFC;
   method Action reset();
   method TaskId curTask;
   method UAddr  mpc;
   method Word   pc;
   method Word   ir;
   method Word   ac0;
   method Word   ac1;
   method Word   ac2;
   method Word   ac3;
   method Bit#(64) cycles;
   method Bit#(32) fields;
   method Bool   memWait;
   method Word   memAt(Bit#(18) phys);
endinterface

module mkAlto(Alto_IFC);
   Keyboard_IFC kbd <- mkKeyboard;
   IoPage_IFC   io  <- mkIoPage(kbd);
   Memory_IFC   mem <- mkMemory(io);
   Disk_IFC      dsk <- mkDisk;
   Display_IFC   dsp <- mkDisplay;
   Ethernet_IFC eth <- mkEthernet;
   CPU_IFC       cpu <- mkCPU(mem, dsk, dsp, kbd, eth);

   method Action reset();
      cpu.reset();
   endmethod

   method TaskId curTask = cpu.curTask;
   method UAddr  mpc = cpu.mpc;
   method Word   pc = cpu.r6;
   method Word   ir = cpu.irReg;
   method Word   ac0 = cpu.ac0;
   method Word   ac1 = cpu.ac1;
   method Word   ac2 = cpu.ac2;
   method Word   ac3 = cpu.ac3;
   method Bit#(64) cycles = cpu.cycles;
   method Bit#(32) fields = dsp.fields;
   method Bool   memWait = cpu.memWait;
   method Word   memAt(Bit#(18) phys) = mem.peek(phys);
endmodule

endpackage
