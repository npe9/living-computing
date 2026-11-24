// Boot the shipped 1e kernel image, s9term, on the privileged machine
// (mkHobbitCoreSystem), with every device read replayed from the
// reference boot (docs/p9boot.md, "The boot on the core").
//
// tools/p9coreboot.py runs the reference boot (tools/p9boot.py on
// sem/hobbit_sem.py with a System) and writes the boot memory, the entry
// and every device-register access by record number (boot.rec).  This
// testbench starts the machine where the ROM hands off -- PC = the
// kernel's entry, every control register 0 (p9boot.py's State) -- and
// lets it run.  There is no second device model: bsv/p9kern.c answers a
// device read with the value the reference's devices returned for that
// record, checks every device write against the recording, and takes the
// console from the machine's own Quart writes.  bsv/run_p9kern.sh then
// compares the machine's retirement records with the reference's, every
// field but cyc, record by record.
//
// The MMU's table walk reads the same physical memory (p9kern.c's
// pk_peek): the kernel builds its tables in RAM.
package P9KernTb;

import HobbitTypes::*;
import HobbitMmu::*;
import HobbitEvents::*;
import HobbitCore::*;

import "BDPI" function ActionValue#(Bit#(32)) pk_fetch(Bit#(32) addr,
                                                      Bit#(32) fresh);
import "BDPI" function Action pk_write(Bit#(32) addr, Bit#(32) v);
import "BDPI" function Bit#(32) pk_peek(Bit#(32) addr);
import "BDPI" function Action pk_poke(Bit#(32) addr, Bit#(32) v);
import "BDPI" function Action pk_retired(Bit#(32) n);
import "BDPI" function ActionValue#(Bit#(32)) pk_start();
import "BDPI" function ActionValue#(Bit#(32)) pk_end();
import "BDPI" function ActionValue#(Bit#(32)) pk_kclocks();
import "BDPI" function ActionValue#(Bit#(32)) pk_failed();
import "BDPI" function Action pk_report();
import "BDPI" function Action pk_evwrite(Bit#(32) addr, Bit#(32) v);
import "BDPI" function ActionValue#(Bit#(32)) pk_irq_at();
import "BDPI" function ActionValue#(Bit#(32)) pk_irq_level();
import "BDPI" function ActionValue#(Bit#(32)) pk_irq_pc();
import "BDPI" function Action pk_irq_taken(Bit#(32) pc);

// The synchronous physical memory (HobbitMem), as bsv/P9HostTb.bsv's: a
// registered read address, the word visible the next clock, `fetch`
// before `commit` so a read sees memory as it stood at the clock's start.
// `fresh` marks the clock after a request, when a device register's
// value is taken from the recording (once per request).
//
// A Verilator build is to compile with -D P9KERN_FLAT, which inlines this
// module into mkP9KernTb so every BDPI call sits in one synthesized module
// (bsv/P9HostTb.bsv's P9HOST_FLAT, docs/bluespec_architecture.md
// "Simulators": separate modules' C calls run in an order Verilator
// chooses, which lost memory writes there).  Bluesim builds without it.
`ifndef P9KERN_FLAT
(* synthesize *)
`endif
(* execution_order = "fetch, commit" *)
module mkP9KernMem(HobbitMem);
  Reg#(Word) raddr <- mkReg(0);
  Reg#(Bool) fresh <- mkReg(False);
  PulseWire reqW <- mkPulseWire;
  Wire#(Word) rdataW <- mkDWire(0);
  Wire#(Maybe#(Tuple2#(Word, Word))) wrW <- mkDWire(tagged Invalid);

  rule fetch;
    let v <- pk_fetch(raddr & 32'hFFFFFFFC, fresh ? 1 : 0);
    rdataW <= v;
  endrule
  rule track;
    fresh <= reqW;
  endrule
  rule commit (wrW matches tagged Valid {.a, .v});
    pk_write(a & 32'hFFFFFFFC, v);
  endrule

  method Action readReq(Word addr);
    raddr <= addr;
    reqW.send;
  endmethod
  method Word readData() = rdataW;
  method Action write(Word addr, Word val);
    wrW <= tagged Valid tuple2(addr, val);
  endmethod
  method Word peek(Word addr) = pk_peek(addr);
endmodule

// The event unit's port (frames and vectors, p. 1-37/1-38): physical
// memory itself, through its own BDPI write so it schedules against
// nothing.  The kernel's vectors and interrupt stack are in RAM.
module mkP9KernEventMem(HobbitEventMem);
  method Word read(Word a) = pk_peek(a);
  method Action write(Word a, Word v);
    pk_evwrite(a, v);
  endmethod
endmodule

// The table walk's port: physical memory itself.
module mkP9KernTables(MmuTables);
  method Word read(Word a) = pk_peek(a);
  method Action write(Word a, Word v);
    pk_poke(a, v);
  endmethod
endmodule

(* synthesize *)
module mkP9KernTb(Empty);
  HobbitMem mem <- mkP9KernMem;
  MmuTables tbl <- mkP9KernTables;
  HobbitEventMem emem <- mkP9KernEventMem;
  HobbitCore core <- mkHobbitCoreSystem(mem, 32'hFFFFFFFF,
                                        defaultMemCycles(), tbl, emem);

  Reg#(Bit#(3)) boot <- mkReg(0);
  Reg#(Word) pc0 <- mkReg(0);
  Reg#(Bit#(32)) endN <- mkReg(0);
  Reg#(Bit#(40)) clocks <- mkReg(0);
  Reg#(Bit#(40)) limit <- mkReg(0);
  Reg#(Bool) finishing <- mkReg(False);
  Reg#(Bit#(2)) why <- mkReg(0);
  Reg#(Bit#(16)) drain <- mkReg(0);

  rule b0 (boot == 0);
    let pc <- pk_start();
    let n <- pk_end();
    let kc <- pk_kclocks();
    pc0 <= pc;
    endN <= n;
    limit <= zeroExtend(kc) * 40'd1000;
    core.prefetchImageAt(pc & 32'hFFFFFC00);
    boot <= 1;
  endrule

  // The ROM's hand-off (tools/p9boot.py `rom_handoff`, State): PC at the
  // entry, SP = MSP = ISP = 0, PSW = 0 (physical addressing, CSP = ISP,
  // level 0), VB = 0, CONFIG = 0.
  rule b1 (boot == 1 && core.prefetchReady());
    core.startAt(pc0, 0, 0, 0);
    $display("P9KERN start pc=%08x, the reference has %0d records", pc0, endN);
    boot <= 2;
  endrule

  Bit#(32) retired = core.instrs() + core.folded();

  // Every clock the board is told the retirement count.  It only reads the
  // core, so it schedules before the commit rule and against nothing.
  rule tell (boot == 2);
    pk_retired(retired);
  endrule

  // The rules below fire every clock or act on the core, so they work
  // from a copy of the core's state taken by `sample`, one clock late:
  // when they read the core directly, bsc found rule cycles through the
  // commit rule and broke them by making `watch` (always enabled)
  // conflict with it, and the core never retired an instruction.
  Reg#(Bit#(32)) sRetired <- mkReg(0);
  Reg#(Bool) sStop <- mkReg(False);
  Reg#(Word) sPc <- mkReg(0);
  Reg#(Word) sFaultPc <- mkReg(0);
  Reg#(Bit#(32)) sProbe <- mkReg(0);
  Reg#(Bit#(64)) sDbg <- mkReg(0);
  rule sample (boot == 2);
    sRetired <= retired;
    sStop <= core.halted() || core.faulted();
    sPc <= core.pc();
    sFaultPc <= core.faultPc();
    sProbe <= core.dbgBoundary();
    sDbg <= core.dbgState();
  endrule

  // The recorded interrupts (docs/p9boot.md, "How device reads and
  // interrupts reach the core", choice 3), through the core's two queues:
  // `arm` hands over the next one whenever there is room, `tookIrq` checks
  // the PC each one saved against the reference's.
  Reg#(Bit#(32)) taken <- mkReg(0);
  Reg#(Bit#(32)) armed <- mkReg(0);
  Reg#(Bool) irqBad <- mkReg(False);
  rule arm (boot == 2 && (armed == taken));
    let n <- pk_irq_at();
    let l <- pk_irq_level();
    if (n != 32'hFFFFFFFF && n < endN) begin
      core.armInterrupt(n, truncate(l));
      armed <= armed + 1;
    end
  endrule
  rule tookIrq (boot == 2);
    let saved <- core.takenInterrupt();
    let pc <- pk_irq_pc();
    pk_irq_taken(saved);
    taken <= taken + 1;
    if (pc != saved) begin
      $display("P9KERN FAIL: interrupt %0d saved pc %08x, the reference %08x",
               taken + 1, saved, pc);
      irqBad <= True;
    end
  endrule

  // A stall: no retirement for 20,000 clocks.  `watch` reports the
  // boundary probe once and stops (a deadlock otherwise runs to the clock
  // limit).  It is part of `watch`: a separate always-enabled rule
  // conflicted with it and bsc starved `watch`.
  Reg#(Bit#(32)) lastRet <- mkReg(0);
  Reg#(Bit#(32)) still <- mkReg(0);

  rule watch (boot == 2 && !finishing);
    clocks <= clocks + 1;
    Bool stalled = False;
    if (sRetired != lastRet) begin
      lastRet <= sRetired; still <= 0;
    end else begin
      still <= still + 1;
      stalled = (still == 20000);
    end
    if (stalled)
      $display("P9KERN STALL: no record retired for 20,000 clocks at %0d",
               sRetired);
    let f <- pk_failed();
    if (sRetired >= endN) begin
      finishing <= True; why <= 0;
    end else if ((f != 0) || irqBad) begin
      finishing <= True; why <= 1;
    end else if (sStop) begin
      finishing <= True; why <= 2;
    end else if (clocks > limit || stalled) begin
      finishing <= True; why <= 3;
    end
  endrule

  rule draining (finishing && drain != 16'd400);
    drain <= drain + 1;
  endrule
  rule finish (finishing && drain == 16'd400);
    pk_report();
    case (why)
      0: $display("P9KERN END: %0d records, the reference's last", sRetired);
      1: $display("P9KERN STOP: a device write or an interrupt differed, %0d records", sRetired);
      2: $display("P9KERN STOP: the machine halted, pc=%08x faultPc=%08x, %0d records",
                  sPc, sFaultPc, sRetired);
      3: $display("P9KERN STOP: clock limit or a stall, %0d records", sRetired);
    endcase
    $display("P9KERN probe: boundary %08x state %016x pc %08x", sProbe, sDbg, sPc);
    $display("P9KERN %0d clocks, %0d interrupts taken", clocks, taken);
    $finish(why == 0 ? 0 : 1);
  endrule
endmodule

endpackage
