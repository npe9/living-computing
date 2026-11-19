// HobbitTimers.bsv -- TIMER1 and TIMER2 of the ATT92010.
//
// Evidence (January 1993 Programmer's Reference Manual):
//
//   p. 1-9  Table 1-2 sheet 1, CONFIG[31:25] (Timer2) and CONFIG[24:22]
//           (Timer1): interrupt enable on overflow, all-the-time vs
//           kernel-only, and the event to count.
//   p. 1-19 sections 1.5.11/1.5.12 and Tables 1-12/1-13: TIMER1 and
//           TIMER2 are 32-bit internal registers holding the count.
//   p. 1-20 Table 1-14: VB+44 is the Timer1 interrupt vector and VB+48
//           the Timer2 vector.
//   p. 1-26 Table 1-24: the CPU escape's register numbers, TIMER1 = 0xB
//           and TIMER2 = 0xC (0xD..0xF are unimp).
//   p. 1-36/1-37: an overflow with the enable set is a level-one
//           interrupt; external level one and Timer1 have priority over
//           Timer2; the interrupt sequence is step 6 of plan.md and is
//           not modelled here.
//   p. 3-14: the CPU escape is a prefix; mode 0x7 becomes register
//           addressing and the low four bits of the operand are the
//           register number.  cpuRead() below is that register file.
//
// The manual prints three Timer2 event encodings (00000 clock cycles,
// 00001 completed instructions with folded branches not counted, 11111 do
// not increment).  It prints nothing for the other 27 encodings, so they
// are not invented: the timer holds and configValid() is false.
//
// The counters are read-only through the CPU escape.  The manual does not
// say TIMER1/TIMER2 are writable, so no architectural write is modelled;
// preset1/preset2 are testbench-only probes, like HobbitBusMem::peek.
//
// Folded branches: the event is "completed instructions (folded branches
// are not counted)" (Table 1-2, p. 1-9).  The core's HRI retires a folded
// branch as its own record with cyc = 0, so the timer's `retire` input is
// the host-instruction retirement, not the folded-branch record.

package HobbitTimers;

import HobbitTypes::*;

interface HobbitTimers;
  // One core clock; one completed instruction (folded branches excluded).
  method Action tick();
  method Action retire();

  method Action setKernel(Bool kernel);
  method Action setConfig(Bit#(32) cfg);
  method Action setExternalL1(Bool asserted);

  method Action preset1(Word v);
  method Action preset2(Word v);
  method Action clearIrq1();
  method Action clearIrq2();
  method Action reset();

  method Word timer1();
  method Word timer2();
  method Maybe#(Word) cpuRead(Bit#(4) r);

  method Bool irq1();
  method Bool irq2();
  method Bool irq();            // level-one request (Timer1 or Timer2)
  method Bool timer2Masked();   // Timer2 loses to external L1 or Timer1
  method Bit#(6) vectorOffset(); // 44 Timer1, 48 Timer2, 0 none
  method Bool configValid();
endinterface

module mkHobbitTimers(HobbitTimers);
  Reg#(Bit#(32)) cfgR <- mkReg(0);       // CONFIG; 0 on reset, p. 1-36
  Reg#(Bool) kernelR <- mkReg(True);     // reset sets kernel mode, p. 1-35
  Reg#(Bool) extL1R <- mkReg(False);
  Reg#(Word) t1R <- mkReg(0);
  Reg#(Word) t2R <- mkReg(0);
  Reg#(Bool) irq1R <- mkReg(False);
  Reg#(Bool) irq2R <- mkReg(False);

  Wire#(Bool) tickW <- mkDWire(False);
  Wire#(Bool) retireW <- mkDWire(False);
  Wire#(Maybe#(Bit#(32))) cfgW <- mkDWire(tagged Invalid);
  Wire#(Maybe#(Bool)) kernelW <- mkDWire(tagged Invalid);
  Wire#(Maybe#(Bool)) extW <- mkDWire(tagged Invalid);
  Wire#(Maybe#(Word)) preset1W <- mkDWire(tagged Invalid);
  Wire#(Maybe#(Word)) preset2W <- mkDWire(tagged Invalid);
  Wire#(Bool) clear1W <- mkDWire(False);
  Wire#(Bool) clear2W <- mkDWire(False);
  Wire#(Bool) resetW <- mkDWire(False);

  // The three printed Timer2 event encodings (Table 1-2, p. 1-9).
  function Bool t2EncodingValid(Bit#(5) ev) =
    (ev == 5'd0) || (ev == 5'd1) || (ev == 5'd31);

  rule step;
    Bit#(32) nCfg = cfgR;
    Bool nKernel = kernelR;
    Bool nExt = extL1R;
    Word n1 = t1R;
    Word n2 = t2R;
    Bool nIrq1 = irq1R;
    Bool nIrq2 = irq2R;

    if (resetW) begin
      nCfg = 0;
      nKernel = True;
      nExt = False;
      n1 = 0;
      n2 = 0;
      nIrq1 = False;
      nIrq2 = False;
    end else begin
      if (isValid(cfgW)) nCfg = validValue(cfgW);
      if (isValid(kernelW)) nKernel = validValue(kernelW);
      if (isValid(extW)) nExt = validValue(extW);
      if (clear1W) nIrq1 = False;
      if (clear2W) nIrq2 = False;

      // ---- Timer1: CONFIG[24] enable, [23] kernel-only, [22] event ----
      Bool t1KernelOnly = (nCfg[23] == 1'b1);
      Bool t1Enabled = !t1KernelOnly || nKernel;
      Bool t1CountsInstr = (nCfg[22] == 1'b1);
      Bool t1Inc = t1Enabled && (t1CountsInstr ? retireW : tickW);
      Bool t1IrqEnable = (nCfg[24] == 1'b1);
      if (isValid(preset1W)) begin
        n1 = validValue(preset1W);
      end else if (t1Inc) begin
        if (t1R == 32'hFFFFFFFF) begin
          n1 = 0;
          if (t1IrqEnable) nIrq1 = True;
        end else
          n1 = t1R + 1;
      end

      // ---- Timer2: CONFIG[31] enable, [30] kernel-only, [29:25] event --
      Bool t2KernelOnly = (nCfg[30] == 1'b1);
      Bool t2Enabled = !t2KernelOnly || nKernel;
      Bit#(5) t2Ev = nCfg[29:25];
      Bool t2Valid = t2EncodingValid(t2Ev);
      Bool t2Hold = (t2Ev == 5'd31);
      Bool t2CountsInstr = (t2Ev == 5'd1);
      Bool t2Inc = t2Enabled && t2Valid && !t2Hold &&
                   (t2CountsInstr ? retireW : tickW);
      Bool t2IrqEnable = (nCfg[31] == 1'b1);
      if (isValid(preset2W)) begin
        n2 = validValue(preset2W);
      end else if (t2Inc) begin
        if (t2R == 32'hFFFFFFFF) begin
          n2 = 0;
          if (t2IrqEnable) nIrq2 = True;
        end else
          n2 = t2R + 1;
      end
    end

    cfgR <= nCfg;
    kernelR <= nKernel;
    extL1R <= nExt;
    t1R <= n1;
    t2R <= n2;
    irq1R <= nIrq1;
    irq2R <= nIrq2;
  endrule

  method Action tick();
    tickW <= True;
  endmethod
  method Action retire();
    retireW <= True;
  endmethod
  method Action setKernel(Bool kernel);
    kernelW <= tagged Valid kernel;
  endmethod
  method Action setConfig(Bit#(32) cfg);
    cfgW <= tagged Valid cfg;
  endmethod
  method Action setExternalL1(Bool asserted);
    extW <= tagged Valid asserted;
  endmethod
  method Action preset1(Word v);
    preset1W <= tagged Valid v;
  endmethod
  method Action preset2(Word v);
    preset2W <= tagged Valid v;
  endmethod
  method Action clearIrq1();
    clear1W <= True;
  endmethod
  method Action clearIrq2();
    clear2W <= True;
  endmethod
  method Action reset();
    resetW <= True;
  endmethod

  method Word timer1() = t1R;
  method Word timer2() = t2R;

  // Table 1-24, p. 1-26: 0xB TIMER1, 0xC TIMER2; 0xD..0xF unimp.
  method Maybe#(Word) cpuRead(Bit#(4) r);
    case (r)
      4'hB: return tagged Valid t1R;
      4'hC: return tagged Valid t2R;
      default: return tagged Invalid;
    endcase
  endmethod

  method Bool irq1() = irq1R;
  method Bool irq2() = irq2R;
  method Bool irq() = irq1R || irq2R;

  // p. 1-9: "An external level one interrupt and a Timer1 interrupt have
  // priority over Timer2."  The manual does not rank external against
  // Timer1, so this predicate only says Timer2 must wait.
  method Bool timer2Masked() = irq2R && (irq1R || extL1R);

  // Table 1-14, p. 1-20.
  method Bit#(6) vectorOffset() =
    irq1R ? 6'd44 : (irq2R ? 6'd48 : 6'd0);

  method Bool configValid() = t2EncodingValid(cfgR[29:25]);
endmodule

endpackage
