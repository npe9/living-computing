// StretchIO.bsv
//
// A simulated Input-Output subsystem for the IBM 7030, standing in for
// the real "IBM 7619 Exchange" (Reference Manual pp.104-127) and the
// external units it connects (pp.129-149, NOT read for this
// implementation -- see the scope note below for what that rules out).
//
// SCOPE -- read before extending or relying on this file.
//
// TIMING: real Exchange channels transfer one byte at a time,
// asynchronously with CPU execution -- "the computer program can
// proceed with processing while a read or write operation continues"
// (p.104). This model instead completes an entire block transfer
// SYNCHRONOUSLY, one WORD per StretchCore.step() call, with no other
// instruction executing until the transfer drains (see
// StretchCore.bsv's `ioPending` FSM). Consequence: any program that
// depends on genuine CPU/IO overlap, or on a Channel Signal (CS)
// interrupt firing mid-transfer while other code runs, is out of
// scope -- the whole interrupt system is out of scope anyway (see
// bsv/README.md "Scope"). Busy-wait polling idioms that check EOP
// after issuing an operation still behave correctly, just without the
// wait actually taking wall-clock time.
//
// DEVICES: exactly two simulated devices, fixed at elaboration time,
// matching only as much of the External Units chapter as p.104-127's
// device-independent Exchange description covers:
//   channel 32 (chanReader):  a read-only card-reader stand-in.
//   channel 33 (chanPrinter): a write-only printer stand-in.
// Both are backed by a fixed-size Vector of words (DeviceWords) that
// the testbench pre-loads (reader) or inspects after the run
// (printer) -- see strap/gen_tb.py. This is a deliberate departure
// from real file I/O: bsc's $fopen/$fgetc are Actions, so a block
// transfer would unroll into a statically-sequenced chain of file
// accesses fighting the same one-write-per-rule constraint everything
// else in this codebase works around; pre-loading through the
// existing "one write per phase, sequenced by an explicit phase
// register" pattern (gen_tb.py's `load` rule for program words) reuses
// a proven mechanism instead of inventing a second one. Real file I/O,
// if ever wanted, is a later convenience layered on top of this, not
// a prerequisite for it.
//
// INSTRUCTIONS: RD, W, CCW, and REL (and their SEOP variants) are
// implemented. CTL and LOC are NOT -- CTL's control-function codes
// (rewind, backspace, write tape mark, ...) and LOC's per-unit
// selection semantics are device-specific and documented in the
// External Units chapter, which this implementation has not read; both
// decode to Operation Code Invalid (ind_OP) rather than a guessed
// behavior, matching this codebase's standing rule against
// implementing what hasn't been verified against a primary source.
// Chaining and multiple-block operation are also NOT implemented: a
// transfer is always a single block against the device's one fixed
// image, and the chain/multiple flags are captured in the control word
// (readable via CCW) but the transfer FSM in StretchCore ignores them.
// SKIP (p.107) IS honored, on READ only (the manual: "on writing, the
// flag is meaningless and is ignored") -- a skip-flagged READ still
// advances the device's read cursor and the memory address each cycle,
// but does not write core storage for that word. A count
// that would run the transfer past the device's DeviceWords capacity
// ends the block early with End Exception (EE) + End of Operation
// (EOP), matching "the unit runs out of material" (p.121) -- this is
// implemented, not just documented, since it costs nothing extra given
// the FSM already tracks a device index.
//
// WRITE's "+2" QUIRK, DELIBERATELY NOT REPRODUCED: p.124's table says a
// terminated WRITE leaves the control word's data word address at
// A_i + N + 2 (not A_i + N, as for READ) because the real Exchange
// double-buffers two words ahead of what's actually been sent to the
// unit. This model has no such buffer -- it moves one word per cycle
// with no lookahead -- so reproducing "+2" would mean faking a hardware
// behavior this implementation doesn't have, rather than honestly
// simplifying it. WRITE here leaves the data word address at A_i + N,
// the same rule as READ. Documented here and at this file's one call
// site (StretchExecute.bsv's IoOp case) so a test checking a copied
// control word after a WRITE doesn't mysteriously come up 2 short of
// the manual's own worked value.
//
// WHAT REJECTS VS. WHAT SETS A STATUS BIT (p.111-113, "Input-Output
// Reject Indicators" / "Input-Output Status Indicators"): addressing a
// channel that isn't chanReader or chanPrinter is a genuine reject
// (Unit Not Ready -- ind_UNRJ; the instruction is never accepted and
// the addressed channel's control word location, if any, is never
// touched) since neither of this model's two devices is ever
// installed anywhere else. Addressing the right channel with the wrong
// operation -- e.g. RD to the printer -- is accepted but fails as an
// Exchange Program Check (EPGK) status bit, matching "an instruction is
// received that the selected unit is not designed to perform, such as
// a READ given to a printer" (p.113) exactly.
//
// NOT PROPAGATED: the CPU's own indicator-register bits (ind_EPGK,
// ind_UK, ind_EE, ind_EOP, ind_CS -- already defined in StretchTypes.bsv
// for BRANCH ON INDICATOR's sake) and the Channel Address register
// (word address 5) are NOT updated by any instruction here -- only the
// per-channel control word this module tracks is. The manual's own
// propagation rule ("indicators... can be set up only if... the
// interruption system is currently enabled", p.118) needs the
// interrupt-enable state this implementation doesn't model (see
// bsv/README.md "Scope"); rather than propagate unconditionally (which
// would not match the manual either), propagation is simply not done
// yet. Concretely: COPY CONTROL WORD is how a program observes EOP/EE/
// etc. here, not BRANCH ON INDICATOR or a SIC-based wait loop -- both
// of those need this gap closed first. See bsv/README.md "Next steps".

package StretchIO;

import StretchTypes::*;
import Vector::*;

typedef 32 DeviceWords;
typedef Bit#(TLog#(DeviceWords)) DeviceIndex;

WordAddr chanReader  = 32;
WordAddr chanPrinter = 33;

interface StretchIO;
  // Whether a channel address names one of this model's two devices,
  // and if so which. Used by StretchExecute's IoOp case for the
  // reject-vs-status-bit distinction described above.
  method Bool isReader(WordAddr ch);
  method Bool isPrinter(WordAddr ch);

  // Device image access for the testbench only (see strap/gen_tb.py) --
  // not part of the 7030 ISA. StretchExecute.bsv never calls these.
  method Action loadReaderWord(DeviceIndex i, Word64 v);
  method Word64 readPrinterWord(DeviceIndex i);

  // Per-word transfer primitives StretchCore's ioPending FSM drives,
  // one call per step().
  method Word64 readerWord(DeviceIndex i);
  method Action writePrinterWord(DeviceIndex i, Word64 v);

  // Per-channel control word (Figure 35): what COPY CONTROL WORD reads
  // back, and what a RD/W/REL updates. This is the EXCHANGE's own copy
  // -- distinct from the control word an instruction reads out of core
  // storage to start an operation, which core storage keeps unchanged
  // during the transfer (p.107 "State of Control Word in the
  // Exchange").
  method ControlWord readChanCW(WordAddr ch);
  method Action writeChanCW(WordAddr ch, ControlWord cw);
endinterface

module mkStretchIO(StretchIO);
  Vector#(DeviceWords, Reg#(Word64)) readerImg  <- replicateM(mkReg(0));
  Vector#(DeviceWords, Reg#(Word64)) printerImg <- replicateM(mkReg(0));

  // unitReady is fixed at 1 (installed) for both simulated devices;
  // there is no not-ready/busy state to model without real device
  // timing. Both channels power on with every other status/flag/count/
  // refill field zero, matching the p.126 "initial power-on" reset
  // description closely enough for a simulated system with no IPL.
  ControlWord cwReset = ControlWord {
    dataAddr: 0, unitReady: 1, epgk: 0, uk: 0, ee: 0, eop: 0, cs: 0,
    seop: 0, chain: 0, multiple: 0, skip: 0, count: 0, refill: 0
  };
  Reg#(ControlWord) readerCW  <- mkReg(cwReset);
  Reg#(ControlWord) printerCW <- mkReg(cwReset);

  function Bool isReaderF(WordAddr ch) = (ch == chanReader);
  function Bool isPrinterF(WordAddr ch) = (ch == chanPrinter);

  method isReader = isReaderF;
  method isPrinter = isPrinterF;

  method Action loadReaderWord(DeviceIndex i, Word64 v);
    readerImg[i] <= v;
  endmethod
  method Word64 readPrinterWord(DeviceIndex i) = printerImg[i];

  method Word64 readerWord(DeviceIndex i) = readerImg[i];
  method Action writePrinterWord(DeviceIndex i, Word64 v);
    printerImg[i] <= v;
  endmethod

  method ControlWord readChanCW(WordAddr ch) =
    isReaderF(ch) ? readerCW : printerCW; // printer CW is also the
                                           // fallback for any other
                                           // (uninstalled) channel;
                                           // callers gate real use with
                                           // isReader/isPrinter first.
  method Action writeChanCW(WordAddr ch, ControlWord cw);
    if (isReaderF(ch)) readerCW <= cw;
    else if (isPrinterF(ch)) printerCW <= cw;
  endmethod
endmodule

endpackage
