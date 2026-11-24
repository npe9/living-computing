// Run a 1st Edition Plan 9 process on the model, with the kernel's work
// replayed from the reference run (A2 of docs/plan9_boot_plan.md).
//
// tools/p9run.py runs the same binary on the reference model
// (sem/hobbit_sem.py) and writes a recording: the boot memory (text,
// data, the exec frame, the vector page and two kernel-entry stubs), the
// start state, and every kernel entry with the arguments it saw, the
// bytes it stored and the result.  This testbench boots that memory,
// lets the machine run, and at each kernel entry has bsv/p9host.c check
// the machine's arguments against the recording and hand back the
// recorded result.  The machine's retirement records are then compared
// with the reference run's, record by record (bsv/run_p9host.sh).
//
// The machine does every instruction itself, including KCALL's frame
// (p. 3-29), the unimplemented-instruction sequence for floating point
// (p. 1-39) and both stubs.  What the host does through the testbench
// surface is what the model has no instruction for: KRET's PSW and ISP.
//
// Memory is p9host.c's sparse store, so the process keeps its real
// addresses (text at 0x1020, stack below USTKTOP = 0x80000000).  A write
// outside every segment stops the run.
package P9HostTb;

import HobbitTypes::*;
import HobbitCore::*;

import "BDPI" function ActionValue#(Bit#(32)) p9h_read(Bit#(32) addr);
import "BDPI" function Action p9h_request(Bit#(32) addr);
import "BDPI" function Action p9h_write(Bit#(32) addr, Bit#(32) v);
import "BDPI" function ActionValue#(Bit#(32)) p9h_start(Bit#(32) which);
import "BDPI" function ActionValue#(Bit#(32)) p9h_poll(Bit#(32) sp);
import "BDPI" function ActionValue#(Bit#(32)) p9h_finished();
import "BDPI" function ActionValue#(Bit#(32)) p9h_events();
import "BDPI" function ActionValue#(Bit#(32)) p9h_kclocks();
import "BDPI" function ActionValue#(Bit#(32)) p9h_unmapped_reads();

// The synchronous memory the core expects (HobbitMem): a read address
// registered by readReq, the word visible on the next clock.
//
// The store is C state, which bsc cannot schedule.  Two rules own it and
// their order is fixed: `fetch` reads the word for last clock's address,
// then `commit` applies this clock's write.  So a read sees the memory as
// it stood at the start of the clock, as mkHobbitMem's RegFile does, and
// a word written this clock is visible to a read requested this clock.
//
// `fetch` reads the registered address on every clock, because the word
// there may have been written and readData must show memory as it stands.
// So reads outside the process's segments are counted per *request*:
// `fresh` is True on the clock after a readReq, and `fetch` then reports
// that address once (p9host.c, p9h_request).
//
// The Verilator build (run_p9host_vl.sh) compiles with -D P9HOST_FLAT,
// which inlines this module into mkP9HostTb.  In Verilog, bsc puts each
// module's C calls in that module's own `always @(negedge CLK)` block,
// and the order between two such blocks is the simulator's choice, not
// the schedule's: with two modules, writes were lost (the testbench's
// block had not yet computed the core's write enable when the memory's
// called p9h_write; observed 2026-11-23).  In one module every C call is
// in one block, in schedule order -- poll, fetch, ..., commit, as Bluesim
// runs them.  Bluesim builds without the flag, so nothing changes there.
`ifndef P9HOST_FLAT
(* synthesize *)
`endif
(* execution_order = "fetch, commit" *)
module mkP9HostMem(HobbitMem);
  Reg#(Word) raddr <- mkReg(0);
  Reg#(Bool) fresh <- mkReg(False);
  PulseWire reqW <- mkPulseWire;
  Wire#(Word) rdataW <- mkDWire(0);
  Wire#(Maybe#(Tuple2#(Word, Word))) wrW <- mkDWire(tagged Invalid);

  rule fetch;
    let v <- p9h_read(raddr & 32'hFFFFFFFC);
    rdataW <= v;
    if (fresh) p9h_request(raddr & 32'hFFFFFFFC);
  endrule

  rule track;
    fresh <= reqW;
  endrule

  rule commit (wrW matches tagged Valid {.a, .v});
    p9h_write(a & 32'hFFFFFFFC, v);
  endrule

  method Action readReq(Word addr);
    raddr <= addr;
    reqW.send;
  endmethod
  method Word readData() = rdataW;
  method Action write(Word addr, Word val);
    wrW <= tagged Valid tuple2(addr, val);
  endmethod
  // The testbench probes memory through p9host.c, not through this.
  method Word peek(Word addr) = 0;
endmodule

(* synthesize *)
module mkP9HostTb(Empty);
  HobbitMem mem <- mkP9HostMem;
  // The run is the record-by-record comparison, not a cycle claim, and
  // the stub's wait loop is host time; the default memory cycles apply.
  HobbitCore core <- mkHobbitCoreEvents(mem, 32'hFFFFFFFF,
                                        defaultMemCycles());

  Reg#(Bit#(3)) boot <- mkReg(0);
  Reg#(Word) pc0 <- mkReg(0);
  Reg#(Word) sp0 <- mkReg(0);
  Reg#(Word) psw0 <- mkReg(0);
  Reg#(Word) isp0 <- mkReg(0);
  Reg#(Word) vb0 <- mkReg(0);
  Reg#(Bit#(40)) clocks <- mkReg(0);
  Reg#(Bool) finishing <- mkReg(False);
  Reg#(Bit#(32)) exitCode <- mkReg(0);

  // The clock budget ($P9KCLOCKS thousand clocks; p9host.c's default is
  // 400 million): generous for za (125,572 instructions), small enough
  // that a hung machine is a failure and not a full disk.
  Reg#(Bit#(40)) limit <- mkReg(40'd1000);

  rule b0 (boot == 0);
    let pc <- p9h_start(0);
    let sp <- p9h_start(1);
    let psw <- p9h_start(2);
    let isp <- p9h_start(3);
    let vb <- p9h_start(4);
    let kc <- p9h_kclocks();
    limit <= zeroExtend(kc) * 40'd1000;
    pc0 <= pc; sp0 <= sp; psw0 <= psw; isp0 <= isp; vb0 <= vb;
    boot <= 1;
  endrule

  // The vector table lives in the event unit's own memory (HobbitEvents'
  // evmem): copy the two vectors the recording's boot memory holds.
  rule b1 (boot == 1);
    let v <- p9h_read(vb0);
    core.eventMemWrite(vb0, v);
    boot <= 2;
  endrule
  rule b2 (boot == 2);
    let v <- p9h_read(vb0 + 12);
    core.eventMemWrite(vb0 + 12, v);
    boot <= 3;
  endrule
  rule b3 (boot == 3);
    core.setVb(vb0);
    core.setConfigKl(True);          // l.s: CONFIG.KL (machine.h:24)
    // One 1 Kbyte window to start from; everything else is filled on
    // demand (HobbitDecode.bsv, mkHobbitPrefetch).
    core.prefetchImageAt(pc0 & 32'hFFFFFC00);
    boot <= 4;
  endrule
  rule b4 (boot == 4 && core.prefetchReady());
    // MSP = SP: the cache starts empty, as the reference run's does
    // (tools/p9run.py `run`).
    core.startAt(pc0, sp0, sp0, psw0);
    boot <= 6;
  endrule
  // startAt makes ISP and SHAD the SP it is given; the interrupt stack
  // is the kernel page's, so ISP is set after the start.  Nothing can
  // have used it yet: the first instruction is still being fetched.
  rule b6 (boot == 6);
    core.setIsp(isp0);
    boot <= 5;
  endrule

  // One poll per clock.  p9host.c acts only when the stub has rung, which
  // it does after its ENTER has put the whole stack in memory.
  //
  // This rule fires every clock, so it must not be scheduled against the
  // pipeline.  It calls no Action method of the core, and it tells the
  // KRET rule through a wire, not a register: with a register the KRET
  // rule had to run *before* this one (it read what this one wrote) and
  // *after* the pipeline's rules (it writes the PSW they read), while
  // this rule had to run before them (it reads what they write) -- a
  // cycle bsc broke by making this rule conflict with `deliver`,
  // `redirect`, `startEvent` and the decoded store's rules, which, since
  // this rule always fires, starved all of them (the machine stopped at
  // the first instruction that needed a memory operand after the
  // testbench came up; the first build never retired at all).
  Wire#(Maybe#(Word)) kretW <- mkDWire(tagged Invalid);

  // KRET's part, once per system call: the PSW KCALL saved at ISP-4
  // (p. 3-29) and the ISP back above the frame.  The stub then sets
  // PSW.F itself.
  rule doKret (kretW matches tagged Valid .p);
    core.setPsw(p);
    core.setIsp(isp0);
  endrule

  rule poll (boot == 5 && !finishing);
    clocks <= clocks + 1;
    let r <- p9h_poll(core.sp());
    if (r == 4) begin
      let p <- p9h_read(isp0 - 4);
      kretW <= tagged Valid p;
    end else if (r == 2) begin
      finishing <= True;
      exitCode <= 0;
    end else if (r == 3) begin
      finishing <= True;
      exitCode <= 1;
    end else if (core.halted() || core.faulted()) begin
      finishing <= True;
      exitCode <= 2;
    end else if (clocks > limit) begin
      finishing <= True;
      exitCode <= 3;
    end
  endrule

  // Let the last retirement records print, then report.  After `exits`
  // the machine is still running (the stub returns into libc's `_loop`),
  // so this is a fixed drain, not a wait for the pipeline to empty; the
  // trace comparison stops at the reference run's last record.
  Reg#(Bit#(8)) drain <- mkReg(0);
  rule draining (finishing && drain != 8'd200);
    drain <= drain + 1;
  endrule
  rule finish (finishing && drain == 8'd200);
    let n <- p9h_events();
    let u <- p9h_unmapped_reads();
    let f <- p9h_finished();
    Bool ok = (exitCode == 0) && (f == 1);
    if (exitCode == 2)
      $display("P9HOST STOP: the machine halted, pc=%08x faultPc=%08x",
               core.pc(), core.faultPc());
    if (exitCode == 3)
      $display("P9HOST STOP: clock limit, pc=%08x sp=%08x msp=%08x dbg=%016x event=%d",
               core.pc(), core.sp(), core.msp(), core.dbgState(),
               core.eventActive());
    if ((exitCode == 0) && (f != 1))
      $display("P9HOST FAIL: exits, but the recording has entries left");
    $display("P9HOST %s: %0d kernel entries, %0d clocks, %0d instructions, %0d reads outside the segments",
             ok ? "EXIT" : "STOP", n, clocks, core.instrs(), u);
    $finish(ok ? 0 : 1);
  endrule
endmodule

endpackage
