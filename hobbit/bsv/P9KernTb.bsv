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
  HobbitCore core <- mkHobbitCoreSystem(mem, 32'hFFFFFFFF,
                                        defaultMemCycles(), tbl);

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

  rule tell (boot == 2);
    pk_retired(retired);
  endrule

  rule watch (boot == 2 && !finishing);
    clocks <= clocks + 1;
    let f <- pk_failed();
    if (retired >= endN) begin
      finishing <= True; why <= 0;
    end else if (f != 0) begin
      finishing <= True; why <= 1;
    end else if (core.halted() || core.faulted()) begin
      finishing <= True; why <= 2;
    end else if (clocks > limit) begin
      finishing <= True; why <= 3;
    end
  endrule

  rule draining (finishing && drain != 16'd400);
    drain <= drain + 1;
  endrule
  rule finish (finishing && drain == 16'd400);
    pk_report();
    case (why)
      0: $display("P9KERN END: %0d records, the reference's last", retired);
      1: $display("P9KERN STOP: a device write differed, %0d records", retired);
      2: $display("P9KERN STOP: the machine halted, pc=%08x faultPc=%08x, %0d records",
                  core.pc(), core.faultPc(), retired);
      3: $display("P9KERN STOP: clock limit, pc=%08x sp=%08x msp=%08x psw=%08x dbg=%016x, %0d records",
                  core.pc(), core.sp(), core.msp(), core.psw(), core.dbgState(),
                  retired);
    endcase
    $display("P9KERN %0d clocks", clocks);
    $finish(why == 0 ? 0 : 1);
  endrule
endmodule

endpackage
