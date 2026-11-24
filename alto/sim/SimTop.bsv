package SimTop;

import AltoTypes::*;
import Alto::*;

import "BDPI" function Action   host_init(Bit#(32) dummy);
import "BDPI" function Action   host_shutdown(Bit#(32) dummy);
import "BDPI" function Bit#(64) host_max_cycles();
import "BDPI" function Bit#(32) host_trace();
import "BDPI" function Action   host_log(Bit#(64) cyc, Bit#(32) taskn, Bit#(32) mpc,
                                         Bit#(32) pc, Bit#(32) ir, Bit#(32) waitn,
                                         Bit#(32) fields,
                                         Bit#(32) ac0, Bit#(32) ac1,
                                         Bit#(32) ac2, Bit#(32) ac3);
import "BDPI" function Action   host_task_tick(Bit#(32) taskn);
import "BDPI" function Action   host_dump_mem(Bit#(32) addr, Bit#(32) data);

module mkSimTop(Empty);
   Alto_IFC alto <- mkAlto;
   Reg#(Bool) started <- mkReg(False);
   Reg#(Bit#(32)) logDiv <- mkReg(0);
   Reg#(Bit#(10)) dumpIdx <- mkReg(0);
   Reg#(Bool) dumping <- mkReg(False);

   rule boot(!started);
      host_init(0);
      alto.reset();
      started <= True;
   endrule

   rule monitor(started && !dumping);
      let c = alto.cycles;
      host_task_tick(zeroExtend(alto.curTask));
      if (host_trace() != 0 && logDiv == 0)
         host_log(c, zeroExtend(alto.curTask), zeroExtend(alto.mpc),
                  zeroExtend(alto.pc), zeroExtend(alto.ir),
                  alto.memWait ? 1 : 0, alto.fields,
                  zeroExtend(alto.ac0), zeroExtend(alto.ac1),
                  zeroExtend(alto.ac2), zeroExtend(alto.ac3));
      logDiv <= (logDiv == 999) ? 0 : logDiv + 1;

      if (c >= host_max_cycles() && c != 0) begin
         host_log(c, zeroExtend(alto.curTask), zeroExtend(alto.mpc),
                  zeroExtend(alto.pc), zeroExtend(alto.ir),
                  alto.memWait ? 1 : 0, alto.fields,
                  zeroExtend(alto.ac0), zeroExtend(alto.ac1),
                  zeroExtend(alto.ac2), zeroExtend(alto.ac3));
         dumping <= True;
         dumpIdx <= 0;
      end
   endrule

   rule dumpMem(dumping);
      // 0-377 boot, 420-437 display, 520-577 disk+calendar,
      // 600-637 Ethernet, 140120 DCB, 133260 BITBLT, 63660 receive buffer
      Bit#(18) addr =
         (dumpIdx < 256) ? zeroExtend(dumpIdx) :
         (dumpIdx < 272) ? (18'o0420 + zeroExtend(dumpIdx - 256)) :
         (dumpIdx < 320) ? (18'o0520 + zeroExtend(dumpIdx - 272)) :
         (dumpIdx < 352) ? (18'o0600 + zeroExtend(dumpIdx - 320)) :
         (dumpIdx < 368) ? (18'o140120 + zeroExtend(dumpIdx - 352)) :
         (dumpIdx < 384) ? (18'o133260 + zeroExtend(dumpIdx - 368)) :
         (dumpIdx < 400) ? (18'o176210 + zeroExtend(dumpIdx - 384)) :
                           (18'o63660 + zeroExtend(dumpIdx - 400));
      host_dump_mem(zeroExtend(addr), zeroExtend(alto.memAt(addr)));
      if (dumpIdx == 463) begin
         $display("");
         host_shutdown(0);
         $finish(0);
      end
      else
         dumpIdx <= dumpIdx + 1;
   endrule
endmodule

endpackage
