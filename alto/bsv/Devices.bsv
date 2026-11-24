// I/O page: keyboard, mouse/keyset, Ethernet stub.

package Devices;

import ConfigReg::*;
import AltoTypes::*;
import AltoMem::*;

import "BDPI" function Bit#(16) host_kb_read(Bit#(16) addr);
import "BDPI" function Bit#(16) host_mouse_bits();
import "BDPI" function Action   host_poll_input();

interface Keyboard_IFC;
   method Word read(Word addr);
   method Word mouseBits;
endinterface

module mkKeyboard(Keyboard_IFC);
   rule rl_poll;
      host_poll_input();
   endrule
   method Word read(Word addr) = host_kb_read(addr);
   method Word mouseBits = host_mouse_bits();
endmodule

// I/O page mux used by Memory.
module mkIoPage#(Keyboard_IFC kbd)(IoPage_IFC);
   Reg#(Word) eiaCount <- mkConfigReg(0);

   rule stepEia;
      eiaCount <= eiaCount + 1;
   endrule

   method Word read(Word addr);
      if (addr >= kbdBase && addr < kbdBase + 4)
         return kbd.read(addr);
      else if (addr >= utilIn && addr < utilIn + 4)
         return kbd.read(addr);
      else if (addr == eiaLoc)
         return eiaCount;
      else
         return 16'hFFFF;   // open bus
   endmethod
   method Action write(Word addr, Word data);
      noAction;
   endmethod
endmodule

endpackage
