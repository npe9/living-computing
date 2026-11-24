// HobbitIntc.bsv -- the board's interrupt path as the kernel uses it:
// io.h's Irq (IONAK + 0x80), IOCTL (IONAK + 0x00) and the incon latch
// (IOBASE + 0x00).  Three standalone devices behind the ULX3S plan's
// "Device bus contract" (hobbit/docs/ulx3s_plan.md):
//
//   req(addr[11:0] offset in the device's window, wdata, be[3:0], write)
//   resp -> rdata, one response per request (latency 1 here)
//   level outputs
//
// Behavioural reference: tools/p9boot.py's Irq, Register("IOCTL") and
// Latch("incon"), checked access for access against this RTL by
// hobbit/fpga/dev/quart/run_replay.sh.  Where the Python model stops the
// run (p9boot.Stop / hobbit_sem.BusError) the RTL raises `fault`: a
// sticky flag, a running count (one per faulting access, so a testbench
// can attribute it) and the code of the last one, {dev[3:0], write,
// offset[10:0]}; the access answers 0 and changes nothing.  In Bluesim the
// fault is also $display'ed.
//
// Irq (io.h: mask0, mask1, status0, status1; trap.c setvector/interrupt):
//   mask0/1  read/write, 8 bits each (written with be = 0xF only)
//   status0/1  read only: the raw requests, bit n = io.h IRQ n
//              (CHOICES['irq-status']: unmasked, as interrupt() masks
//              them itself), sampled from `sources` one clock earlier
//   il6      the part's interrupt level 6 (CHOICES['irq-level']): every
//            board interrupt reaches the Hobbit at IL 6, asserted while
//            (status & mask) != 0
// The board wires bit 1 (IRQQUART) to the Quart's irq; IRQINCON 5,
// IRQSCSIDMA 8, IRQSONIC 9, IRQSCSI 10 come from the other devices.
//
// IOCTL (io.h IOCTLADDR; rammain.c writes 0 then IOENABLE, scsi.c
// toggles SCSIENABLE): one 32-bit read/write word at offset 0, full-word
// writes only; its value is an output for the board.
//
// incon (devincon.c Device at IOACK 0x0000: ctl, csr, pad[2], data):
// writes at offsets 0x00..0x13 are accepted and recorded; ANY read faults,
// as p9boot's Latch stops the run.  The kernel's inconreset writes csr =
// INCON_STOP and never reads (observed in the captured boot); inconpoll's
// `csr & INCON_ALIVE` read would need a Datakit board, which this design
// does not have, so it must fail loud rather than invent an answer.  The
// incon requests no interrupt (irq is constant False).

package HobbitIntc;

import FIFOF :: *;

typedef Bit#(16) FaultCode;

function FaultCode faultCode(Bit#(4) dev, Bool write, Bit#(12) addr);
  return {dev, pack(write), addr[10:0]};
endfunction

// --------------------------------------------------------------- Irq
interface HobbitIrq;
  method Action req(Bit#(12) addr, Bit#(32) wdata, Bit#(4) be, Bool write);
  method ActionValue#(Bit#(32)) resp;
  (* always_ready, always_enabled *) method Action sources(Bit#(16) s);
  (* always_ready *) method Bool il6;
  (* always_ready *) method Bool fault;
  (* always_ready *) method Bit#(16) faults;
  (* always_ready *) method FaultCode faultInfo;
endinterface

(* synthesize *)
module mkHobbitIrq(HobbitIrq);
  Reg#(Bit#(8)) mask0 <- mkReg(0);
  Reg#(Bit#(8)) mask1 <- mkReg(0);
  Reg#(Bit#(16)) status <- mkReg(0);
  Wire#(Bit#(16)) srcW <- mkBypassWire;
  FIFOF#(Bit#(32)) respQ <- mkFIFOF;
  Reg#(Bool) faultR <- mkReg(False);
  Reg#(Bit#(16)) nfault <- mkReg(0);
  Reg#(FaultCode) finfo <- mkReg(0);

  rule sample;
    status <= srcW;
  endrule

  method Action req(Bit#(12) addr, Bit#(32) wdata, Bit#(4) be, Bool write);
    Bit#(32) r = 0;
    Bool bad = False;
    Bit#(2) idx = addr[3:2];
    if (addr > 12'h00F) bad = True;
    else if (write) begin
      if (be != 4'hF || idx > 1) bad = True;
      else if (idx == 0) mask0 <= wdata[7:0];
      else mask1 <= wdata[7:0];
    end
    else case (idx)
      0: r = zeroExtend(mask0);
      1: r = zeroExtend(mask1);
      2: r = zeroExtend(status[7:0]);
      3: r = zeroExtend(status[15:8]);
    endcase
    if (bad) begin
      faultR <= True;
      nfault <= nfault + 1;
      finfo <= faultCode(1, write, addr);
      $display("FAULT Irq: %s at +0x%03x be %x (p9boot.Irq raises BusError)", write ? "write" : "read", addr, be);
    end
    respQ.enq(r);
  endmethod
  method ActionValue#(Bit#(32)) resp;
    respQ.deq;
    return respQ.first;
  endmethod
  method Action sources(Bit#(16) s);
    srcW <= s;
  endmethod
  method Bool il6 = (status & {mask1, mask0}) != 0;
  method Bool fault = faultR;
  method Bit#(16) faults = nfault;
  method FaultCode faultInfo = finfo;
endmodule

// --------------------------------------------------------------- IOCTL
interface HobbitIoctl;
  method Action req(Bit#(12) addr, Bit#(32) wdata, Bit#(4) be, Bool write);
  method ActionValue#(Bit#(32)) resp;
  (* always_ready *) method Bit#(32) value;   // SCSIENABLE 0x1, IOENABLE 0x4
  (* always_ready *) method Bool fault;
  (* always_ready *) method Bit#(16) faults;
  (* always_ready *) method FaultCode faultInfo;
endinterface

(* synthesize *)
module mkHobbitIoctl(HobbitIoctl);
  Reg#(Bit#(32)) val <- mkReg(0);
  FIFOF#(Bit#(32)) respQ <- mkFIFOF;
  Reg#(Bool) faultR <- mkReg(False);
  Reg#(Bit#(16)) nfault <- mkReg(0);
  Reg#(FaultCode) finfo <- mkReg(0);

  method Action req(Bit#(12) addr, Bit#(32) wdata, Bit#(4) be, Bool write);
    Bool bad = addr[11:2] != 0 || (write && be != 4'hF);
    if (!bad && write) val <= wdata;
    if (bad) begin
      faultR <= True;
      nfault <= nfault + 1;
      finfo <= faultCode(2, write, addr);
      $display("FAULT IOCTL: %s at +0x%03x be %x (p9boot.Register raises BusError)", write ? "write" : "read", addr, be);
    end
    respQ.enq((bad || write) ? 0 : val);
  endmethod
  method ActionValue#(Bit#(32)) resp;
    respQ.deq;
    return respQ.first;
  endmethod
  method Bit#(32) value = val;
  method Bool fault = faultR;
  method Bit#(16) faults = nfault;
  method FaultCode faultInfo = finfo;
endmodule

// --------------------------------------------------------------- incon
interface HobbitIncon;
  method Action req(Bit#(12) addr, Bit#(32) wdata, Bit#(4) be, Bool write);
  method ActionValue#(Bit#(32)) resp;
  (* always_ready *) method Bool irq;          // IRQINCON: never
  (* always_ready *) method Bit#(32) csr;      // the last csr written
  (* always_ready *) method Bit#(16) writes;
  (* always_ready *) method Bool fault;
  (* always_ready *) method Bit#(16) faults;
  (* always_ready *) method FaultCode faultInfo;
endinterface

(* synthesize *)
module mkHobbitIncon(HobbitIncon);
  Reg#(Bit#(32)) csrR <- mkReg(0);
  Reg#(Bit#(16)) nwrites <- mkReg(0);
  FIFOF#(Bit#(32)) respQ <- mkFIFOF;
  Reg#(Bool) faultR <- mkReg(False);
  Reg#(Bit#(16)) nfault <- mkReg(0);
  Reg#(FaultCode) finfo <- mkReg(0);

  method Action req(Bit#(12) addr, Bit#(32) wdata, Bit#(4) be, Bool write);
    // p9boot maps IOBASE + 0x00 .. 0x13 to the latch.
    Bool bad = !write || addr > 12'h013;
    if (!bad) begin
      nwrites <= nwrites + 1;
      if (addr[11:2] == 1) csrR <= wdata;
    end
    else begin
      faultR <= True;
      nfault <= nfault + 1;
      finfo <= faultCode(3, write, addr);
      $display("FAULT incon: %s at +0x%03x (p9boot's Latch stops the run: no Datakit board is modelled)", write ? "write" : "read",
               addr);
    end
    respQ.enq(0);
  endmethod
  method ActionValue#(Bit#(32)) resp;
    respQ.deq;
    return respQ.first;
  endmethod
  method Bool irq = False;
  method Bit#(32) csr = csrR;
  method Bit#(16) writes = nwrites;
  method Bool fault = faultR;
  method Bit#(16) faults = nfault;
  method FaultCode faultInfo = finfo;
endmodule

endpackage
