// HobbitTimerTb.bsv -- PASS/FAIL checks for TIMER1/TIMER2.
//
// Every expected value is from the January 1993 PRM: CONFIG[31:25] and
// [24:22] (Table 1-2, p. 1-9), the 32-bit count registers (Tables 1-12/
// 1-13, p. 1-19), the CPU-escape register numbers 0xB/0xC (Table 1-24,
// p. 1-26), the vectors VB+44/VB+48 (Table 1-14, p. 1-20), and the
// level-one priority rule (p. 1-9, p. 1-36).

package HobbitTimerTb;

import HobbitTypes::*;
import HobbitTimers::*;

(* synthesize *)
module mkHobbitTimerTb(Empty);
  HobbitTimers timers <- mkHobbitTimers;

  Reg#(Bit#(16)) t <- mkReg(0);
  function Action chk(Bool ok, String label, Word got, Word want) =
    action
      if (ok) $display("PASS %s = 0x%08x", label, got);
      else    $display("FAIL %s = 0x%08x, want 0x%08x", label, got, want);
    endaction;

  function Action chkb(Bool ok, String label) =
    action
      if (ok) $display("PASS %s", label);
      else    $display("FAIL %s", label);
    endaction;

  // Timer1: clocks, all modes.  cfg = 0.
  // Timer2: clocks, all modes, no interrupt.  cfg = 0.
  // t=0 reset, t=1 setup, t=2..6 five clocks, t=7 check.
  rule run;
    t <= t + 1;
    case (t)
      16'd0: timers.reset();
      16'd1: begin
        timers.setConfig(32'h00000000);
        timers.setKernel(True);
        timers.preset1(0);
        timers.preset2(0);
      end
      16'd2, 16'd3, 16'd4, 16'd5, 16'd6: timers.tick();
      16'd7: begin
        chk(timers.timer1() == 5, "timer1_counts_clocks", timers.timer1(), 5);
        chk(timers.timer2() == 5, "timer2_counts_clocks", timers.timer2(), 5);
        // Timer1 counts instructions: CONFIG[22] = 1.
        timers.setConfig(32'h00400000);
        timers.preset1(0);
      end
      // t=8..12: five clocks, retire on 8, 10, 12.
      16'd8:  begin timers.tick(); timers.retire(); end
      16'd9:  timers.tick();
      16'd10: begin timers.tick(); timers.retire(); end
      16'd11: timers.tick();
      16'd12: begin timers.tick(); timers.retire(); end
      16'd13: chk(timers.timer1() == 3, "timer1_counts_instructions",
                  timers.timer1(), 3);
      // Timer1 kernel-only: CONFIG[23] = 1.
      16'd14: begin
        timers.setConfig(32'h00800000);
        timers.preset1(0);
        timers.setKernel(False);
      end
      16'd15, 16'd16, 16'd17: timers.tick();
      16'd18: chk(timers.timer1() == 0, "timer1_kernel_only_off",
                  timers.timer1(), 0);
      16'd19: timers.setKernel(True);
      16'd20, 16'd21, 16'd22: timers.tick();
      16'd23: chk(timers.timer1() == 3, "timer1_kernel_only_on",
                  timers.timer1(), 3);
      // Timer1 overflow with the interrupt enabled: CONFIG[24] = 1.
      16'd24: begin
        timers.setConfig(32'h01000000);
        timers.preset1(32'hFFFFFFFF);
      end
      16'd25: timers.tick();
      16'd26: begin
        chk(timers.timer1() == 0, "timer1_overflow_wraps",
            timers.timer1(), 0);
        chkb(timers.irq1(), "timer1_overflow_irq");
        chk(timers.vectorOffset() == 44, "timer1_vector_44",
            zeroExtend(timers.vectorOffset()), 44);
        chkb(isValid(timers.cpuRead(4'hB)), "cpu_escape_reads_timer1");
        chk(validValue(timers.cpuRead(4'hB)) == timers.timer1(),
            "cpu_escape_timer1_value",
            validValue(timers.cpuRead(4'hB)), timers.timer1());
        // Overflow with the interrupt disabled: CONFIG[24] = 0.
        timers.setConfig(32'h00000000);
        timers.preset1(32'hFFFFFFFF);
        timers.clearIrq1();
      end
      16'd27: timers.tick();
      16'd28: begin
        chk(timers.timer1() == 0, "timer1_overflow_disabled_wraps",
            timers.timer1(), 0);
        chkb(!timers.irq1(), "timer1_overflow_irq_disabled");
        // Timer2 counts instructions: CONFIG[29:25] = 00001.
        timers.setConfig(32'h02000000);
        timers.preset2(0);
      end
      16'd29: begin timers.tick(); timers.retire(); end
      16'd30: timers.tick();
      16'd31: begin timers.tick(); timers.retire(); end
      16'd32: begin
        chk(timers.timer2() == 2, "timer2_counts_instructions",
            timers.timer2(), 2);
        // Timer2 hold: CONFIG[29:25] = 11111.
        timers.setConfig(32'h3E000000);
        timers.preset2(0);
      end
      16'd33, 16'd34, 16'd35: timers.tick();
      16'd36: chk(timers.timer2() == 0, "timer2_hold_11111",
                  timers.timer2(), 0);
      // Timer2 unprinted event encodings hold and flag.
      16'd37: begin
        timers.setConfig(32'h04000000);   // CONFIG[29:25] = 00010
        timers.preset2(0);
      end
      16'd38, 16'd39: timers.tick();
      16'd40: begin
        chk(timers.timer2() == 0, "timer2_unprinted_event_holds",
            timers.timer2(), 0);
        chkb(!timers.configValid(), "timer2_unprinted_event_invalid");
        // Timer2 kernel-only: CONFIG[30] = 1.
        timers.setConfig(32'h40000000);
        timers.preset2(0);
        timers.setKernel(False);
      end
      16'd41, 16'd42: timers.tick();
      16'd43: chk(timers.timer2() == 0, "timer2_kernel_only_off",
                  timers.timer2(), 0);
      16'd44: timers.setKernel(True);
      16'd45, 16'd46: timers.tick();
      16'd47: begin
        chk(timers.timer2() == 2, "timer2_kernel_only_on",
            timers.timer2(), 2);
        // Timer2 overflow with the interrupt enabled: CONFIG[31] = 1.
        timers.setConfig(32'h80000000);
        timers.preset2(32'hFFFFFFFF);
      end
      16'd48: timers.tick();
      16'd49: begin
        chk(timers.timer2() == 0, "timer2_overflow_wraps",
            timers.timer2(), 0);
        chkb(timers.irq2(), "timer2_overflow_irq");
        chk(timers.vectorOffset() == 48, "timer2_vector_48",
            zeroExtend(timers.vectorOffset()), 48);
        chkb(isValid(timers.cpuRead(4'hC)), "cpu_escape_reads_timer2");
        chk(validValue(timers.cpuRead(4'hC)) == timers.timer2(),
            "cpu_escape_timer2_value",
            validValue(timers.cpuRead(4'hC)), timers.timer2());
        chkb(!isValid(timers.cpuRead(4'hD)), "cpu_escape_unimp_register");
        // Priority: Timer2 loses to Timer1 and to external level one.
        timers.setConfig(32'h01000000);   // Timer1 irq enabled
        timers.preset1(32'hFFFFFFFF);
      end
      16'd50: timers.tick();
      16'd51: begin
        chkb(timers.irq1() && timers.irq2(), "both_timer_irqs");
        chkb(timers.timer2Masked(), "timer2_masked_by_timer1");
        timers.clearIrq1();
      end
      16'd52: begin
        chkb(!timers.irq1() && timers.irq2(), "timer1_cleared");
        chkb(!timers.timer2Masked(), "timer2_not_masked_without_timer1");
        timers.setExternalL1(True);
      end
      16'd53: begin
        chkb(timers.timer2Masked(), "timer2_masked_by_external_l1");
        timers.setExternalL1(False);
        timers.clearIrq2();
      end
      16'd54: begin
        chkb(!timers.irq() && !timers.timer2Masked(), "all_irqs_clear");
        chk(timers.vectorOffset() == 0, "no_vector_when_idle",
            zeroExtend(timers.vectorOffset()), 0);
      end
      16'd55: begin
        $display("SUMMARY timer: done");
        $finish;
      end
      default: noAction;
    endcase
  endrule
endmodule

endpackage
