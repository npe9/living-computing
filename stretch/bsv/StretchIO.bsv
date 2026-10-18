// StretchIO.bsv
//
// A simulated Input-Output subsystem for the IBM 7030, standing in for
// the real "IBM 7619 Exchange" (Reference Manual pp.104-127) and the
// external units it connects (pp.129-149; the "External Units" chapter
// -- unlike at this file's previous revision, now read for the tape
// unit's standard and tape-specific CONTROL function codes, p.129-132;
// see the "CONTROL FUNCTIONS" section below for exactly what subset of
// that chapter this implements).
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
// DEVICES: three simulated devices, fixed at elaboration time, each
// covering only as much of the External Units chapter as this
// implementation has actually read and modeled:
//   channel 32 (chanReader):  a read-only card-reader stand-in.
//   channel 33 (chanPrinter): a write-only printer stand-in.
//   channel 34 (chanTape):    a read/write tape-drive stand-in.
// Reader and printer are backed by a fixed-size Vector of words
// (DeviceWords) that the testbench pre-loads (reader) or inspects
// after the run (printer) -- see strap/gen_tb.py. The tape is backed
// by its own, deliberately SMALLER Vector (TapeWords -- see below) and
// additionally carries a position register that PERSISTS across
// instructions, unlike the reader/printer's devIdx which always
// restarts at 0 -- see "TAPE POSITION" below. All device storage is a
// deliberate departure from real file I/O: bsc's $fopen/$fgetc are
// Actions, so a block transfer would unroll into a statically-sequenced
// chain of file accesses fighting the same one-write-per-rule
// constraint everything else in this codebase works around;
// pre-loading through the existing "one write per phase, sequenced by
// an explicit phase register" pattern (gen_tb.py's `load` rule for
// program words) reuses a proven mechanism instead of inventing a
// second one. Real file I/O, if ever wanted, is a later convenience
// layered on top of this, not a prerequisite for it.
//
// DEVICE GENERALIZATION: `DeviceKind` and `kindOf` below replace what
// was, at the two-device revision of this file, a pair of hardcoded
// `isReader`/`isPrinter` predicates -- that shape does not survive a
// third device, let alone a microcontroller port someday needing a
// fourth or fifth. Adding a device now means: one more `DeviceKind`
// tag, one more arm in `kindOf`, one more storage Vector/position
// register, one more arm in readChanCW/writeChanCW's dispatch -- not a
// new boolean threaded through every call site.
//
// INSTRUCTIONS: RD, W, CCW, REL, and CTL (and their SEOP variants) are
// implemented, CTL only against the tape channel (see "CONTROL
// FUNCTIONS" below) -- CTL issued to the reader or printer still
// decodes to Operation Code Invalid, since this implementation has not
// modeled any reader/printer control function (reserved light, check
// light, ECC mode -- p.129-130 -- none of which have an observable
// effect on this model's storage-level abstraction anyway). LOC is NOT
// implemented: the manual's addressing model has LOCATE select one of
// up to eight tape units accommodated by a single tape control on a
// channel (p.133), but this model puts exactly one tape unit directly
// on its own channel, the same direct-addressing shape as the reader
// and printer -- sidestepping the channel-to-control-to-unit hierarchy
// LOCATE exists to navigate. That's an explicit, documented
// simplification (the user's own stated tolerance: "it's okay if they
// are intended to work in a simulated environment"), not a case of
// LOCATE's semantics being unread -- see p.110-111, p.133 for what a
// multi-unit LOCATE would need if ever added.
// Chaining and multiple-block operation are also NOT implemented: a
// transfer is always a single block against a device's own fixed
// image, and the chain/multiple flags are captured in the control word
// (readable via CCW) but the transfer FSM in StretchCore ignores them.
// SKIP (p.107) IS honored, on READ only (the manual: "on writing, the
// flag is meaningless and is ignored") -- a skip-flagged READ still
// advances the device's read cursor and the memory address each cycle,
// but does not write core storage for that word. A count that would
// run the transfer past a device's capacity (DeviceWords for reader/
// printer, TapeWords for tape) ends the block early with End Exception
// (EE) + End of Operation (EOP), matching "the unit runs out of
// material" (p.121) -- this is implemented, not just documented, since
// it costs nothing extra given the FSM already tracks a device index.
//
// CARD FEED, added 2026-10-18, and it is the same argument as TAPE
// POSITION below applied to the one other device it is true of.
//
// A CARD READER FEEDS.  The 7503 pulls a card from the hopper, reads
// it, and stacks it; the next READ gets the NEXT card.  Until this
// register existed every RD restarted the reader at device index 0,
// so the machine read the same card forever -- which makes it a
// 32-word read-only buffer, not a card reader.
//
// MEASURED, not reasoned about.  strap/programs/card_reader.strap
// reads two cards and checks them separately, precisely because a
// reader that returned the same card twice would pass a one-card
// test; before this, card 2 came back bit-for-bit as card 1.
//
// THE PRINTER IS DELIBERATELY NOT GIVEN ONE.  A 1403-2 does advance
// its paper, but a line is a RECORD preceded by a carriage control
// field (docs/exchange_and_io.md 3.6) and this model has no record
// structure for the printer at all -- giving it a bare position
// would model line advance without modelling what a line IS.  The
// reader needs no record structure for the feed to be right, because
// a card IS its fixed 15 words.
//
// Hopper-empty is the End Exception the FSM already raises when
// devIdx reaches capacity, which is also what the real unit does:
// R23-9702 printed p.28's Figure 4.5-1 puts hopper-empty and
// stacker-full on the single End Exception line.
//
// TAPE POSITION: unlike the printer, where every W starts over at
// device index 0 (StretchExecute.bsv's IoOp case sets `devIdx: 0`
// for it), a real tape's read/write head stays
// wherever the last operation left it -- "operation of Tape under
// Computer Control" (p.133) describes reading, writing, spacing, and
// backspacing as all acting relative to the tape's current position,
// not an instruction-local index. This is the one property that makes
// a tape a tape and not a third card reader with a different channel
// number: two successive READs must return successive data, not the
// same block twice. Modeled here as a persistent `tapePos` register
// (StretchExecute.bsv seeds a new transfer's devIdx from it instead of
// 0; StretchCore's FSM writes it back after every word moved) which
// CONTROL REWIND resets to 0 and CONTROL BACKSPACE BLOCK decrements by
// one -- see below. `tapePos` is intentionally ONE BIT WIDER than
// `TapeIndex` (`TapePos = Bit#(TLog#(TapeWords)+1)`), the same "room
// for one past the end" idiom `IoXfer.devIdx` already uses relative to
// `DeviceIndex`, so a fully-drained tape (position == TapeWords) is
// representable without wraparound and is caught by the very next
// RD/W's End Exception check on its first FSM cycle, before any data
// moves.
//
// TapeWords IS DELIBERATELY SMALL (16, vs. DeviceWords' 32): this is
// the first device where "the unit runs out of material" is meant to
// be something a test program can actually reach with an ordinary
// count, not just a theoretical code path -- see
// strap/programs/io_tape.strap's End Exception check.
//
// CONTROL FUNCTIONS: the External Units chapter's CONTROL instruction
// format (p.111: "a selection address (LOCATE), control information
// which is decoded by the external unit (CONTROL)") puts a raw
// function code in the right effective address field -- NOT a
// core-storage word address the way RD/W/CCW's right effective address
// is. strap_asm.py's IO_OP branch accordingly does NOT apply the >>6
// word-address conversion to CTL/LOC's second field (see its own
// comment) -- a genuinely different case from RD/W/CCW's "A", caught
// only once CTL had a real behavior to test against. Of the tape
// control functions the manual lists (p.132), this implementation
// executes exactly two, both chosen because they're the minimum needed
// to demonstrate tape position actually being a persistent, mutable
// register rather than a documentation-only field:
//   octal 136 (REWIND) / 137 (REWIND AND UNLOAD): both reset tapePos
//     to 0. This model has no separate "unloaded" unit state, so the
//     two codes are not distinguished -- a documented simplification.
//     Deviates from the manual's note that REWIND's EOP indication is
//     given at the *initiation* of the operation, not its completion
//     (p.132: "the end-of-operation indication is given as soon as the
//     operation is initiated at the unit") -- this synchronous model
//     has no notion of "still rewinding" separate from "done", so
//     REWIND completes (and sets EOP) in the same execute()/CTL case
//     as every other CONTROL function, not asynchronously.
//   octal 176 (BACKSPACE BLOCK): decrements tapePos by one, UNLESS
//     tapePos is already 0 (the load point), in which case the
//     instruction is "terminated with an exchange-program-check
//     indication" per p.136 ("Beginning and End of Tape") -- position
//     is left at 0, not wrapped or made negative.
// Every other tape control code the manual documents -- SPACE BLOCK/
// FILE, WRITE TAPE MARK, BACKSPACE FILE, the density/ECC/parity/light
// functions (p.130, p.132) -- decodes to Operation Code Invalid here.
// SPACE FILE/BACKSPACE FILE/WRITE TAPE MARK need a tape-mark concept
// this word-addressed model doesn't have (p.134-135: a tape mark is a
// distinguished single-byte block, and this model has no notion of
// byte-granular blocks at all, only fixed word positions); the
// density/ECC/parity/light functions have no observable effect on a
// model that already treats every word as a flat 64 bits with no
// framing, parity, or physical light state to toggle. CTL's own SEOP
// form (CTLSEOP, already in opcodes.py since the original I/O
// milestone) suppresses EOP on REWIND/BACKSPACE BLOCK exactly as it
// does on RD/W/REL.
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
// channel that isn't chanReader, chanPrinter, or chanTape is a genuine
// reject (Unit Not Ready -- ind_UNRJ; the instruction is never accepted
// and the addressed channel's control word location, if any, is never
// touched) since none of this model's three devices is ever installed
// anywhere else. Addressing the right channel with the wrong operation
// -- e.g. RD to the printer -- is accepted but fails as an Exchange
// Program Check (EPGK) status bit, matching "an instruction is received
// that the selected unit is not designed to perform, such as a READ
// given to a printer" (p.113) exactly. The tape accepts both RD and W,
// since real magnetic tape genuinely is both readable and writable.
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
`ifdef HOST_TAPE
import StretchTapeSourceFile::*;   // Bluesim-only; see the selection
                                    // below for why this is `ifdef'd
`endif
import StretchTapeSource::*;  // TapeSource, mkTapeSourceVector, and the
                              // TapeWords/TapeIndex/TapePos typedefs,
                              // which moved there with the interface

typedef 32 DeviceWords;
typedef Bit#(TLog#(DeviceWords)) DeviceIndex;
// One bit wider, room for "one past the end", the same idiom TapePos
// uses against TapeIndex -- see "CARD FEED".
typedef Bit#(TAdd#(TLog#(DeviceWords), 1)) DevicePos;

// TapeWords / TapeIndex / TapePos are no longer defined here: they
// moved to StretchTapeSource.bsv along with the TapeSource interface,
// so that an implementation of that interface -- an SD-backed one, say
// -- need not import this module in order to be one.  They are
// re-exported by the import above, so users of StretchIO see them
// unchanged.

WordAddr chanReader  = 32;
WordAddr chanPrinter = 33;
WordAddr chanTape    = 34;

// Which (if any) of this model's devices a channel address names. See
// "DEVICE GENERALIZATION" above -- this is what every future device
// should extend instead of adding another hardcoded predicate.
typedef enum { DevNone, DevReader, DevPrinter, DevTape }
  DeviceKind deriving (Bits, Eq, FShow);

function DeviceKind kindOf(WordAddr ch) =
  (ch == chanReader)  ? DevReader  :
  (ch == chanPrinter) ? DevPrinter :
  (ch == chanTape)    ? DevTape    : DevNone;

interface StretchIO;
  // Whether a channel address names one of this model's devices, and
  // if so which. Used by StretchExecute's IoOp case for the
  // reject-vs-status-bit distinction described above. (kindOf itself
  // is also directly importable -- these are just Bool convenience
  // wrappers over it for the common single-device checks.)
  method Bool isReader(WordAddr ch);
  method Bool isPrinter(WordAddr ch);
  method Bool isTape(WordAddr ch);

  // Device image access for the testbench only (see strap/gen_tb.py,
  // strap/gen_tape_tb.py) -- not part of the 7030 ISA. StretchExecute.bsv
  // never calls these.
  method Action loadReaderWord(DeviceIndex i, Word64 v);
  method Word64 readPrinterWord(DeviceIndex i);

  // Per-word transfer primitives StretchCore's ioPending FSM drives,
  // one call per step().
  method Word64 readerWord(DeviceIndex i);
  method Action writePrinterWord(DeviceIndex i, Word64 v);

  // Tape is bidirectional, unlike the read-only reader and write-only
  // printer, so one pair of methods serves both the FSM's runtime
  // transfers AND the testbench's pre-load/post-run-check calls (see
  // strap/gen_tape_tb.py) -- there's no read-only/write-only split to
  // preserve the way there is for readerWord/writePrinterWord.
  // THESE TWO ARE NO LONGER SYMMETRIC, and the asymmetry is the whole
  // change.  Before, one pair served both the FSM's runtime transfers
  // and the testbench's pre-load/post-run checks, because a tape read
  // was a combinational value method and could be called from either.
  // Now:
  //   readTapeWord  -- TESTBENCH ONLY (strap/gen_tb.py,
  //     strap/gen_tape_tb.py).  The FSM reads through tapeReadReq/
  //     tapeRespReady/tapeReadResp below; a value method cannot
  //     express a wait, which is exactly why it had to go.
  //   writeTapeWord -- STILL BOTH: the FSM's W-direction path and the
  //     testbench's pre-load.  Writes are posted rather than
  //     acknowledged, so they did not need the same treatment -- and
  //     that is itself a simplification an SD-backed source will have
  //     to revisit (StretchTapeSource.bsv's header says so).
  method Word64 readTapeWord(TapeIndex i);
  method Action writeTapeWord(TapeIndex i, Word64 v);

  // THE RUNTIME TAPE PATH.  A tape source may take any number of
  // clocks to produce a word -- a register-backed one takes one, an
  // SD-backed one takes many and a variable many -- so the transfer
  // FSM requests, waits, and collects, exactly as it already does
  // against core storage (StretchStorage's readWordReq /
  // responseReady / readWordResp).  The old combinational
  // readTapeWord(i) could not express a wait and so could not be
  // backed by anything but registers.
  method Action tapeReadReq(TapeIndex i);
  method Bool tapeRespReady();
  method ActionValue#(Word64) tapeReadResp();

  // Tape's persistent position -- see "TAPE POSITION" above.
  // StretchExecute's IoOp case reads this to seed a new transfer's
  // devIdx; StretchCore's ioPending FSM writes it back after every
  // word moved; the CTL REWIND/BACKSPACE BLOCK cases write it directly.
  // How many words the tape source holds -- forwarded so the transfer
  // FSM's End Exception test asks the SOURCE rather than assuming the
  // register-backed one's size.  See StretchTapeSource.bsv.
  method TapeIndex tapeCapacity();

  method TapePos tapePos();
  method Action setTapePos(TapePos p);

  // THE CARD READER FEEDS.  See "CARD FEED" below.
  method DevicePos readerPos();
  method Action setReaderPos(DevicePos p);

  // Per-channel control word (Figure 35): what COPY CONTROL WORD reads
  // back, and what a RD/W/REL/CTL updates. This is the EXCHANGE's own
  // copy -- distinct from the control word an instruction reads out of
  // core storage to start an operation, which core storage keeps
  // unchanged during the transfer (p.107 "State of Control Word in the
  // Exchange").
  method ControlWord readChanCW(WordAddr ch);
  method Action writeChanCW(WordAddr ch, ControlWord cw);
endinterface

module mkStretchIO(StretchIO);
  Vector#(DeviceWords, Reg#(Word64)) readerImg  <- replicateM(mkReg(0));
  Vector#(DeviceWords, Reg#(Word64)) printerImg <- replicateM(mkReg(0));
  // WHICH TAPE SOURCE, chosen at compile time.  `ifdef rather than a
  // module parameter because the file-backed source uses
  // `import "BDPI"`, which has no Verilog back end: bsc emits a .v
  // for it as VPI wrappers and yosys then fails with
  //   ERROR: Can't resolve function name '\$imported_host_tape_read_word'
  // So the BDPI package must not even be IMPORTED on a path that a
  // bitstream elaborates, which a runtime or parameter choice cannot
  // guarantee and this can.
  //
  // Build with -D HOST_TAPE and link bsv/host_tape.c to mount a real
  // image from $STRETCH_TAPE; without it the model keeps the
  // sixteen-word register image every existing test uses.  USE A
  // SEPARATE -bdir FOR THE TWO: they differ only by a -D, and a .bo
  // built one way is silently wrong for the other.
`ifdef HOST_TAPE
  TapeSource                         tape       <- mkTapeSourceFile;
`else
  TapeSource                         tape       <- mkTapeSourceVector;
`endif
  Reg#(TapePos) tapePosReg <- mkReg(0);
  Reg#(DevicePos) readerPosReg <- mkReg(0);

  // unitReady is fixed at 1 (installed) for all three simulated
  // devices; there is no not-ready/busy state to model without real
  // device timing. All channels power on with every other status/flag/
  // count/refill field zero, matching the p.126 "initial power-on"
  // reset description closely enough for a simulated system with no
  // IPL.
  ControlWord cwReset = ControlWord {
    dataAddr: 0, unitReady: 1, epgk: 0, uk: 0, ee: 0, eop: 0, cs: 0,
    seop: 0, chain: 0, multiple: 0, skip: 0, count: 0, refill: 0
  };
  Reg#(ControlWord) readerCW  <- mkReg(cwReset);
  Reg#(ControlWord) printerCW <- mkReg(cwReset);
  Reg#(ControlWord) tapeCW    <- mkReg(cwReset);

  method Bool isReader(WordAddr ch) = (kindOf(ch) == DevReader);
  method Bool isPrinter(WordAddr ch) = (kindOf(ch) == DevPrinter);
  method Bool isTape(WordAddr ch) = (kindOf(ch) == DevTape);

  method Action loadReaderWord(DeviceIndex i, Word64 v);
    readerImg[i] <= v;
  endmethod
  method Word64 readPrinterWord(DeviceIndex i) = printerImg[i];

  method Word64 readerWord(DeviceIndex i) = readerImg[i];
  method Action writePrinterWord(DeviceIndex i, Word64 v);
    printerImg[i] <= v;
  endmethod

  method Word64 readTapeWord(TapeIndex i) = tape.peek(i);
  method Action writeTapeWord(TapeIndex i, Word64 v);
    tape.write(i, v);
  endmethod

  method Action tapeReadReq(TapeIndex i);
    tape.readReq(i);
  endmethod
  method Bool tapeRespReady() = tape.respReady();
  method ActionValue#(Word64) tapeReadResp();
    let v <- tape.readResp();
    return v;
  endmethod

  method TapeIndex tapeCapacity() = tape.capacity();

  method DevicePos readerPos() = readerPosReg;
  method Action setReaderPos(DevicePos p);
    readerPosReg <= p;
  endmethod

  method TapePos tapePos() = tapePosReg;
  method Action setTapePos(TapePos p);
    tapePosReg <= p;
  endmethod

  method ControlWord readChanCW(WordAddr ch);
    case (kindOf(ch))
      DevReader:  return readerCW;
      DevPrinter: return printerCW;
      DevTape:    return tapeCW;
      default:    return printerCW; // fallback for any uninstalled
                                     // channel; callers gate real use
                                     // with isReader/isPrinter/isTape
                                     // (or kindOf) first.
    endcase
  endmethod
  method Action writeChanCW(WordAddr ch, ControlWord cw);
    case (kindOf(ch))
      DevReader:  readerCW  <= cw;
      DevPrinter: printerCW <= cw;
      DevTape:    tapeCW    <= cw;
      default:    noAction;
    endcase
  endmethod
endmodule

endpackage
