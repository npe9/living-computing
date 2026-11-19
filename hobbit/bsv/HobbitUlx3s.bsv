// HobbitUlx3s.bsv -- ULX3S (Lattice ECP5 85F, CABGA381) board top for the
// ATT92010 Hobbit model.
//
// board boundary follows Flute (Bluespec, Inc., Apache-2.0) — see docs/bluespec_architecture.md
//
// The core, the program and the golden pre-state are the ones the Bluesim
// smoke test uses (HobbitSmoke.bsv): the program is generated from
// bsv/smoke.hex by mk_image_bsv.py at every board build, so the FPGA and
// the simulator execute identical bytes.  This module adds board loading,
// the prefetch warm-up, the power-on reset gate, the HRI line writer and
// the LED report.  It contains no $display and no test-only construct, so
// the Verilog bsc emits here is what the FPGA runs.
//
// Golden pre-state (documented in HobbitSmoke.bsv and HobbitCore.bsv):
//   PC = 0, CONFIG = 0                        p. 1-35
//   PSW = 0x200 (bit 9: CSP = SP)             Table 1-8 sheet 2, p. 1-15
//   SHAD = 0x100, SP = 0x100, MSP = 0x180     shared pre-state
// The core model always uses CSP = SP and sets SHAD = SP, so the PSW bit
// is implicit here.
//
// Boot sequence (mirrors HobbitSmoke.bsv): load the image through the
// memory's single synchronous write port, one word per clock; warm the
// prefetch buffer from the synchronous read port (64 words, one per
// clock); then start the core at PC 0.
//
// UART (ftdi_rxd, 25 MHz / 115200 = 217 clocks per bit):
//   Every HRI retirement record leaves as the one fixed-format line that
//   tests/hri_check.py parses, exactly as HobbitCore.bsv's retire rule
//   prints it.  The core presents each record for exactly one clock
//   (hriValid() marks that cycle) and the record carries its own SP/MSP
//   after values, so the relay below simply copies every presented record
//   into the queue; nothing is reconstructed and no field is patched.
//
//   One line is 123 to 132 bytes: 116 fixed bytes, " cyc=", the 1-to-10
//   digit decimal cycle count, and the newline.  At 115200 baud the worst
//   case is 132 bytes = 1320 bits = 286,440 clocks = 11.46 ms per line.
//   The core runs the smoke program in a few hundred clocks, so records
//   arrive far faster than the line drains: a retirement queue is
//   unavoidable.  The core has no stall hook, so the queue is the only
//   lossless option, and dropping or coalescing a record is not allowed.
//   The fixed smoke image retires 41 records (the count sim_smoke prints);
//   the queue holds 48, one per record, so no record can be dropped.  A
//   program with more than 48 retirements would need a deeper queue or a
//   core stall hook.
//
// LEDs (active high, led[7:0]):
//   led[7]    faulted -- the loud trap/halt indicator: the core stopped on
//             the unimplemented parcel at PC 0x0BA (p. 1-39).  This is the
//             model's "halted" state (halted() = faulted()).
//   led[6]    started  -- the image loaded, the prefetch warmed and
//             start() ran.
//   led[5:0]  pc[5:0]  -- low six bits of the architectural PC; the bar
//             walks while the program runs and freezes at 0xBA[5:0] = 0x3A
//             when the trap lights led[7].
//
// The board wrapper (HobbitUlx3sTop.v) owns the pins and the power-on
// reset; this module receives the resulting level as the explicit rst_n
// argument and gates the boot with it.

package HobbitUlx3s;

import FIFOF::*;
import BRAMFIFO::*;
import HobbitTypes::*;
import HobbitCore::*;
import HobbitUart::*;
import SmokeImage::*;

interface HobbitUlx3sIfc;
  method Bit#(8) led();
  method Bit#(1) txd();
endinterface

(* synthesize *)
module mkHobbitUlx3s#(Bit#(1) rst_n)(HobbitUlx3sIfc);

  HobbitMem mem <- mkHobbitMem;
  MemCycles mcyc = defaultMemCycles();
  HobbitCore core <- mkHobbitCore(mem, 32'hFFFFFFFF, mcyc);
  // Caller-supplied clocks per bit: 25 MHz / 115200 = 217.01, truncated.
  HriWriter uart <- mkHriWriter(217);

  // Shared golden pre-state: SP = 0x100, MSP = 0x180.
  Word sp0  = 32'h00000100;
  Word msp0 = 32'h00000180;

  Reg#(Bit#(8)) li <- mkReg(0);
  Reg#(Bool) loaded <- mkReg(False);
  Reg#(Bit#(2)) boot <- mkReg(0);
  Reg#(Bool) started <- mkReg(False);

  // --- image load ---------------------------------------------------
  // One word per clock through the synchronous write port, ascending.
  // smoke.hex is 160 words, so the 8-bit index cannot wrap.
  rule load (!loaded);
    if (zeroExtend(li) < imageLength()) begin
      mem.write(zeroExtend(li) << 2, imageWord(zeroExtend(li)));
      li <= li + 1;
    end else
      loaded <= True;
  endrule

  // --- boot ---------------------------------------------------------
  // Warm the prefetch buffer from the synchronous read port, then start.
  rule askPrefetch (loaded && (boot == 0) && rst_n == 1);
    core.prefetchImage();
    boot <= 1;
  endrule

  rule start ((boot == 1) && core.prefetchReady() && rst_n == 1);
    core.start(sp0, msp0);
    started <= True;
    boot <= 2;
  endrule

  // --- retirement queue ---------------------------------------------
  // 48 records of 299 bits = 14,352 bits.  A register file costs a 48-way
  // push mux per bit plus a 299-bit 48:1 pop mux (about 19k LUT4s, which
  // overran the 85F); the same queue in the ECP5's block RAM is one or two
  // DP16KDs.  mkSizedBRAMFIFOF gives a genuine 1R1W block RAM (bsc emits
  // BRAM2) with notFull/notEmpty, and the producer/consumer rules below are
  // the same split the register version proved.
  Hri nullHri = unpack(0);
  FIFOF#(Hri) q <- mkSizedBRAMFIFOF(48);

  // Capture side.  hriValid() marks the one clock a record is presented,
  // and every such cycle presents a distinct record, so the queue takes
  // every one of them.  The fixed smoke image retires 41 records, so the
  // 48-deep FIFO never presents notFull false and nothing is dropped.
  rule relayIn (q.notFull && core.hriValid());
    q.enq(core.hri());
  endrule

  // Send side.  The rule condition is exactly the writer's readiness, so
  // the unconditional calls below are always legal; the rule fires whenever
  // a record is queued and the writer can take one.
  rule relayOut (q.notEmpty && uart.ready);
    uart.enq(q.first);
    q.deq;
  endrule

  method Bit#(8) led();
    let pc = core.pc();
    return {pack(core.faulted()), pack(started), pc[5:0]};
  endmethod

  method Bit#(1) txd() = uart.txd();

endmodule

endpackage
