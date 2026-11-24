// HobbitSocCpu.bsv -- the privileged machine (mkHobbitCoreSystem) with its
// physical memory turned inside out, for the ULX3S SoC top
// (fpga/hobbit_soc.v, fpga/README.md "The SoC").
//
// The core is written against three memory faces that a simulation
// backs with an array or with C: the synchronous HobbitMem (an address
// registered by readReq, its word on readData the next clock), and two
// *combinational* faces, the MMU's table walk (MmuTables.read) and the
// event unit's vector memory (HobbitEventMem.read).  On the board the
// physical memory is an SDRAM, which answers neither in time.  So this
// module exposes every face as ports and leaves the timing to the top:
//
//   * The top clocks this module with a gated clock (an ECP5 DCCA), and
//     gives it an edge only when every word the next edge depends on is
//     in place.  Between edges the core's state is frozen, its logic
//     computes exactly what it would compute on an edge, and the top can
//     take as many SDRAM cycles as it needs.  The core counts its own
//     clocks, so its retirements and their `cyc` are the simulation's.
//
//   * readReq leaves as rdReq/rdAddr (valid during the clock before the
//     edge that would register it); readData is the rdData input, which
//     the top holds until the next request.
//
//   * The two combinational faces read a small associative window of
//     physical words (`win`, filled by the top).  The core reports, as
//     combProbes, every physical word its walks and event sequence could
//     read this clock (HobbitCore combProbes); the top fills the window
//     until every valid probe hits, and only then gives the edge.  A
//     probe that changes as the window fills (a page entry selected by a
//     segment entry just fetched) settles in more than one round.
//
//   * Every write leaves as its own port (memWr, tblWr, evWr); the top
//     applies them in that order after the edge, before anything else.
//
// The start is P9KernTb's (the ROM's hand-off, docs/p9boot.md): warm the
// prefetch window around the entry, then PC = entry, SP = MSP = PSW = 0.
package HobbitSocCpu;

import Vector::*;
import HobbitTypes::*;
import HobbitMmu::*;
import HobbitEvents::*;
import HobbitCore::*;

typedef 16 NWin;

typedef struct {
  Bool valid;
  Word addr;
  Word data;
} WinEntry deriving (Bits, Eq);

typedef Vector#(NWin, WinEntry) Window;
typedef Vector#(22, Maybe#(Word)) Probes;

function Word winRead(Window w, Word a);
  Word r = 0;
  for (Integer i = 0; i < valueOf(NWin); i = i + 1)
    if (w[i].valid && (w[i].addr == (a & 32'hFFFFFFFC)))
      r = w[i].data;
  return r;
endfunction

interface HobbitSocCpu;
  // The synchronous face.
  (* always_ready *) method Bool rdReq;
  (* always_ready *) method Word rdAddr;
  (* always_ready, always_enabled *) method Action rdData(Word d);
  // The writes of this clock, one port per writer.
  (* always_ready *) method Maybe#(Tuple2#(Word, Word)) memWr;
  (* always_ready *) method Maybe#(Tuple2#(Word, Word)) tblWr;
  (* always_ready *) method Maybe#(Tuple2#(Word, Word)) evWr;
  // The combinational faces.
  (* always_ready, always_enabled *) method Action window(Window w);
  (* always_ready *) method Probes probes;
  // Start at the ROM's hand-off.
  method Action go(Word entry);
  (* always_ready *) method Bool running;
  // The board's interrupt level, every clock (7 = none; the board's
  // devices all request IL 6, docs/p9boot.md CHOICES irq-level): the
  // core's own live path (ilR, intWanted), taken at an idle boundary
  // when IL < PSW.IPL (Table 1-8, p. 1-15).
  (* always_ready, always_enabled *) method Action il(Bit#(3) level);
  // Interrupts through the core's queue (HobbitCore armInterrupt), for a
  // replayed run.
  method Action armInterrupt(Bit#(32) n, Bit#(3) level);
  (* always_ready *) method Bool irqArmable;
  method ActionValue#(Word) takenInterrupt;
  // State for the top's LEDs and for the co-simulation's comparison.
  (* always_ready *) method Bit#(32) retired;
  (* always_ready *) method Bool stopped;
  (* always_ready *) method Word pc;
  (* always_ready *) method Bool hriValid;
  (* always_ready *) method Hri hri;
endinterface

(* synthesize *)
module mkHobbitSocCpu(HobbitSocCpu);
  Wire#(Maybe#(Word)) rdW <- mkDWire(tagged Invalid);
  Wire#(Word) rdDataW <- mkBypassWire;
  Wire#(Window) winW <- mkBypassWire;
  Wire#(Maybe#(Tuple2#(Word, Word))) memWrW <- mkDWire(tagged Invalid);
  Wire#(Maybe#(Tuple2#(Word, Word))) tblWrW <- mkDWire(tagged Invalid);
  Wire#(Maybe#(Tuple2#(Word, Word))) evWrW <- mkDWire(tagged Invalid);

  HobbitMem mem = (interface HobbitMem;
    method Action readReq(Word a);
      rdW <= tagged Valid a;
    endmethod
    method Word readData() = rdDataW;
    method Action write(Word a, Word v);
      memWrW <= tagged Valid tuple2(a, v);
    endmethod
    method Word peek(Word a) = 0;
  endinterface);

  MmuTables tbl = (interface MmuTables;
    method Word read(Word a) = winRead(winW, a);
    method Action write(Word a, Word v);
      tblWrW <= tagged Valid tuple2(a, v);
    endmethod
  endinterface);

  HobbitEventMem evmem = (interface HobbitEventMem;
    method Word read(Word a) = winRead(winW, a);
    method Action write(Word a, Word v);
      evWrW <= tagged Valid tuple2(a, v);
    endmethod
  endinterface);

  HobbitCore core <- mkHobbitCoreSystem(mem, 32'hFFFFFFFF,
                                        defaultMemCycles(), tbl, evmem);

  Reg#(Bit#(2)) phase <- mkReg(0);
  Reg#(Word) entryR <- mkReg(0);
  Reg#(Bit#(32)) armed <- mkReg(0);
  Reg#(Bit#(32)) taken <- mkReg(0);

  // The probes are read in a rule of their own, every clock, after the
  // rules that note this clock's translations; a value method reading the
  // MMU's note wires directly closed a scheduling path through EU_S3's
  // commit (bsc G0095).
  Wire#(Probes) probesW <- mkDWire(replicate(tagged Invalid));
  Wire#(Word) vbW <- mkDWire(0);
  (* fire_when_enabled, no_implicit_conditions *)
  rule sampleVb;
    vbW <= core.vbProbe;
  endrule
  (* fire_when_enabled, no_implicit_conditions *)
  rule sampleProbes;
    probesW <= append(core.combProbes, cons(tagged Valid vbW, nil));
  endrule

  rule warm (phase == 1);
    core.prefetchImageAt(entryR & 32'hFFFFFC00);
    phase <= 2;
  endrule

  rule launch (phase == 2 && core.prefetchReady());
    core.startAt(entryR, 0, 0, 0);
    phase <= 3;
  endrule

  method Bool rdReq = isValid(rdW);
  method Word rdAddr = fromMaybe(0, rdW);
  method Action rdData(Word d);
    rdDataW <= d;
  endmethod
  method Maybe#(Tuple2#(Word, Word)) memWr = memWrW;
  method Maybe#(Tuple2#(Word, Word)) tblWr = tblWrW;
  method Maybe#(Tuple2#(Word, Word)) evWr = evWrW;
  method Action window(Window w);
    winW <= w;
  endmethod
  method Probes probes = probesW;

  method Action go(Word entry) if (phase == 0);
    entryR <= entry;
    phase <= 1;
  endmethod
  method Bool running = (phase == 3);

  method Action armInterrupt(Bit#(32) n, Bit#(3) level) if (armed == taken);
    core.armInterrupt(n, level);
    armed <= armed + 1;
  endmethod
  method Bool irqArmable = (armed == taken);
  method ActionValue#(Word) takenInterrupt;
    let s <- core.takenInterrupt();
    taken <= taken + 1;
    return s;
  endmethod

  method Action il(Bit#(3) level);
    core.setIl(level);
  endmethod

  method Bit#(32) retired = core.instrs() + core.folded();
  method Bool stopped = core.halted() || core.faulted();
  method Word pc = core.pc();
  method Bool hriValid = core.hriValid();
  method Hri hri = core.hri();
endmodule

endpackage
