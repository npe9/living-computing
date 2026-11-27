// StretchCore.bsv
//
// Top-level IBM 7030 core: the instruction unit with its 1Y/2Y
// buffers, the four-level look-ahead, and the E-box (StretchExecute's
// mkEBox), as per-clock rules gated by the harness's `step()` clock
// enable. See docs/microarchitecture_plan.md for the staged plan this
// implements and bsv/README.md for the model's scope.

package StretchCore;

import Vector::*;
import StretchTypes::*;
import StretchStorage::*;
import StretchMemory::*;   // installed(): the address-invalid bound,
                            // which rl_xmit needs per word
import StretchIO::*;
import ConfigReg::*;
import StretchDiskSource::*;  // DiskIndex / ArcAddr / arcWords, for the
                               // disk arms of rl_io
import StretchTapeSource::*;  // TapeWords/TapeIndex and the TapeSource
                              // interface the tape transfer now goes
                              // through; imported names are not
                              // re-exported by StretchIO, so this is
                              // needed even though StretchIO uses them
import StretchDecode::*;
import StretchExecute::*;
import StretchIBox::*;       // mkInstrBuffers, classification, iboxHazard
import StretchLookAhead::*;  // mkLookAhead
import StretchTiming::*;     // iboxCycles/eboxClocks/budgetClocks

interface StretchCore;
  // step() advances the core exactly one clock: every rule in
  // mkStretchCore is gated on the pulse it sends, so nothing moves while
  // the harness is loading storage or reading results. halted() is True
  // once an instruction has branched to its own address (the "BEW, $"
  // halt idiom, C22-6531 p.14 -- "$" is the location counter, so this
  // targets the instruction itself) and stays so until setPC. Runners
  // that assemble and load real STRAP programs poll it to stop instead
  // of using a fixed step count -- see stretch/tests/gen_tb.py, whose
  // run rule is `(!core.halted()) stepCount++` with the run latch up,
  // so the
  // step count at halt is the program's clock count on this model.
  //
  // What one clock does is the per-arm story in the rules below. Two
  // instruction kinds span several clocks in ways worth naming here:
  //
  // A progressive-indexing VFL instruction (Reference Manual p.21)
  // takes TWO clocks to complete -- the manual's own words: "An
  // operation in which progressive indexing is specified is executed in
  // two parts." The first does everything except the index-register
  // write-back and does NOT advance the PC; the second (with no new
  // instruction fetched, rl_idx_write) performs just that write and
  // then advances the PC.
  //
  // An RD or W input-output instruction (Reference Manual "IBM 7619
  // Exchange", pp.104-127) similarly takes MULTIPLE clocks: the first
  // fetches the control word, starts the transfer, and DOES advance the
  // PC (matching the manual: "the computer then proceeds to the
  // execution of the next instruction"), but every subsequent clock
  // moves exactly one more word of the block and fetches nothing new
  // until the whole block has moved -- see rl_io below and
  // StretchIO.bsv's file header for why this makes the transfer
  // synchronous from the program's point of view (no genuine CPU/IO
  // overlap) even though the real hardware overlaps them. Neither
  // mechanism can halt (a taken branch is the only way next==pc, and
  // neither progressive indexing nor an I/O transfer branches).
  // >>> THE MACHINE'S RUN LATCH, NOT A PER-CLOCK POKE FROM THE HARNESS.
  // <<<  `start` raises it, `stop` drops it, and every rule below is
  // gated on it AND on not having halted.  Reference Manual printed
  // p.34 -- "The timer runs whenever the machine is operating" -- is a
  // description of exactly this latch, which is why the oscillator
  // pulse is generated under the same gate.
  method Action start();
  method Action stop();
  method Bool   halted();    // the last clock's instruction branched to itself
  // HALTED AND NOTHING CAN WAKE IT.  A BEW,$ with the interruption
  // system enabled is a WAIT, not a stop: an I/O transfer in flight,
  // a control word holding status the exchange will report (printed
  // p.118), or an interruption being taken will move the counter.
  // MCP waits exactly this way (printed p.198 line 47, p.269 line 30).
  // halted() stays the old predicate for every program that ends in
  // BEW,$ and means it; a harness that has to run an operating system
  // stops on idle() instead.
  method Bool   idle();
  method HWordAddr getPC();
  method Action setPC(HWordAddr a);
  // Press INITIAL PROGRAM LOAD and let a unit raise a channel signal:
  // Reference Manual printed p.126.  See the method body.
  method Action iplStart();
  interface StretchStorage mem;  // direct access for test setup/inspection
  interface StretchIO io;        // simulated device access for test
                                  // setup/inspection -- see StretchIO.bsv
endinterface

// ---- INTERRUPTION RECOVERY (plan §1c 5f, 2026-11-20) ----
// What the instruction unit must be able to give back if the level it
// belongs to raises an interruption: the index words and the indicators
// as they stood when the level was LOADED (i.e. after this instruction's
// own I-box processing, before any younger one), and the count of I-box
// instructions started so far (advSeq), so that recovery can tell whether
// anything ran ahead of it.  One per look-ahead slot; the guessed branch's
// wrong-way recovery reads the same record (it used to keep its own
// xSnap/indSnap, which were exactly this record of the branch's slot).
typedef struct {
  Vector#(16, Word64) x;
  Word64              ind;
  Bit#(8)             adv;
  Bit#(8)             sto;   // storeSeq at the load: I-box STORES started so far
  Bit#(8)             oth;   // otherSeq at the load: non-index indicator
                             // rises NOT at a level's completion so far
} IxRecov deriving (Bits);

// The level that last completed in the E-box, with its record: the
// candidate "operation during which the indicator is turned on"
// (Ref. Manual printed p.48) for an interruption that becomes due in the
// next two clocks (StretchStorage's interruptDue() is latched behind the
// indicator write).  keepX names index words the level ITSELF wrote after
// its load (progressive indexing's part 2, a store or tail write into
// words 16-31), which recovery must not undo; ownInd says it set the
// index indicators itself (progressive indexing), so they are kept too.
typedef struct {
  HWordAddr pc;
  InstrLen  len;
  IxRecov   rec;
  Bit#(16)  keepX;
  Bool      ownInd;
  Bit#(32)  at;
} RetiredLevel deriving (Bits);

(* synthesize *)
module mkStretchCore(StretchCore);
  StretchStorage st <- mkStretchStorage;
  StretchIO ioDev <- mkStretchIO;
  // Idiomatic-Bluespec rewrite step 1 (plan §1c): the execute datapath
  // as ONE shared sub-module, not a function inlined at each call site
  // (the mkFBox/mkMBox shape). Its start()/resume() call sites below are
  // mutually-exclusive arms of the rule ladder, so they share this one
  // instance's method ports. See StretchExecute's mkEBox comment.
  // (This said "the four ebox.exec call sites" and "branches of step()";
  // `exec` was the preparation probe and is gone, and step() is now a
  // run latch -- see rl_prepare and `running`.)
  EBox ebox <- mkEBox(st, ioDev);
  // Step 5b: the instruction buffers (1Y/2Y + IC controls) and the
  // four-level look-ahead are stage modules of their own
  // (StretchIBox.bsv, StretchLookAhead.bsv), the mkCPU_Stage shape;
  // the rules below orchestrate them.
  InstrBuffers ibuf <- mkInstrBuffers(st);
  LookAhead    la   <- mkLookAhead(st);
  // The harness's clock enable and the halt flag it polls (see the
  // rules section below for the contract).
  // A ConfigReg for ioPending's reason: every rule's guard reads it, and
  // as a plain Reg that ordered all of them before `start`, which with
  // rl_io_report among them made start/iplStart in one harness rule a
  // G0004.  The value read is the start-of-clock latch either way.
  Reg#(Bool) running   <- mkConfigReg(False);   // the run latch; see `start`/`stop`
  Reg#(Bool) haltedReg <- mkReg(False);
  Reg#(HWordAddr) pcReg <- mkReg(0);
  Reg#(Maybe#(Tuple2#(Bit#(4), IndexWord))) pendingIdxWrite <- mkReg(tagged Invalid);
  // A crossing VFL store's second word below 32 (ExecDone.tailWrite),
  // written by rl_tail_write before anything else is armed.
  Reg#(Maybe#(Tuple2#(WordAddr, Word64))) pendingTailWrite <- mkReg(tagged Invalid);
  // A ConfigReg so that rl_io_report's read of it is not ordered against
  // iplStart, which writes it: the read is the start-of-clock value
  // either way, which is all the report asks ("has the operation
  // terminated?").  Made with `running` below while removing a G0004
  // between start and iplStart; `running` was the one that cleared it,
  // and whether this one alone was also needed was not measured.
  Reg#(Maybe#(IoXfer)) ioPending <- mkConfigReg(tagged Invalid);
  // A MULTI-WORD TRANSMIT still to drain, the memory-to-memory
  // sibling of ioPending.  Reference Manual printed p.30 and
  // StretchTypes.bsv's XmitXfer; serviced by rl_xmit below.
  Reg#(Maybe#(XmitXfer)) xmitPending <- mkReg(tagged Invalid);
  // rl_xmit's own read-staging flag, the same shape as ioReadIssued:
  // the sending word is a memory READ that takes a clock to come
  // back, so the rule has to remember that it already asked.
  Reg#(Bool) xmitReadIssued <- mkReg(False);
  // SWAP's two extra states.  An exchange needs TWO reads and TWO
  // writes per word and this model has one of each per rule, so a
  // swapped word takes three clocks: read the sending word, read the
  // receiving word and write the sending word's value into it, then
  // write the receiving word's old value back into the sending word.
  // BOTH READS HAPPEN BEFORE EITHER WRITE, which is Reference Manual
  // printed p.30's "at the same time" and the only thing that makes
  // an overlapping swap an exchange rather than a propagation.
  Reg#(Bit#(2)) xmitSwapPhase <- mkReg(0);
  Reg#(Word64)  xmitSwapHeld  <- mkReg(0);
  // HOW MANY CLOCKS A SWAP COSTS, counted rather than reasoned
  // about.  The MCP boot's step count moved by 82 when forward SWAP
  // was built, and "about five clocks a word times six words" is an
  // estimate; this is the number.  Whatever is left of the 82 is MCP
  // running differently afterwards, because Q FIN's index-register
  // restore now actually happens.
  Reg#(Bit#(32)) xmitSwapClocks <- mkReg(0);

  // ---- The interruption mechanism (Ref. Manual p.48) ----
  // Valid while THE ONE instruction at the effective interruption
  // address is in flight, holding that address.  Its Validity is what
  // makes the instruction counter stand still: p.48, "the instruction
  // counter is stepped neither before nor during the execution of the
  // instruction at the effective interruption address; however, the
  // instruction counter can be replaced as the result of a successful
  // branching operation."  So pcReg is not touched while this is
  // Valid, and commitNext below makes the one decision -- branched, or
  // fell through -- in one place.
  Reg#(Maybe#(HWordAddr)) intPC <- mkReg(tagged Invalid);

  // (The 1Y/2Y buffers and their IC controls: `ibuf`, StretchIBox.bsv.)
  // Restart requests (branch taken inside step(); setPC from outside)
  // as sequence numbers, so each register has exactly one writer.
  Reg#(Bit#(8)) branchSeq  <- mkReg(0);   // written in step()'s branch paths
  Reg#(Bit#(8)) restartSeq <- mkReg(0);   // written by setPC
  Reg#(Bit#(8)) restartSeen <- mkReg(0);  // written at the top of step()
  Reg#(Bit#(8)) branchSeen  <- mkReg(0);
  // (The four-level look-ahead ring: `la`, StretchLookAhead.bsv.)
  // ---- Stage 3c (plan §6d): the not-taken guess. A branch on an
  // arithmetic indicator is loaded as a branch level; the instruction
  // unit snapshots the index words and indicators and continues down
  // the fall-through path. When the arithmetic unit reaches the level
  // the indicators are final: guess right, retire; guess wrong, cancel
  // the younger levels and, on the next clock (`recover`), restore the
  // snapshot, reset the instruction counter to the target and refetch.
  Reg#(Bool)                 guessPending <- mkReg(False);
  // (The snapshot is the branch level's slot record, ixRec below; the
  // slot is remembered in recoverSlot for rl_recover.)
  Reg#(Maybe#(HWordAddr))    recover      <- mkReg(tagged Invalid);
  Reg#(Bit#(2))              recoverSlot  <- mkReg(0);
  // ---- INTERRUPTION RECOVERY (see IxRecov / RetiredLevel above) ----
  // Perf. Char. Vol. 1 printed p.3-22 (PDF 40): each I-box instruction
  // loads a level, which "may be an index recovery level containing the
  // old contents of an index register to enable the restoration in case
  // of unexpected interruptions"; printed p.3-24 (PDF 42): "All changes in
  // the index registers and/or index indicators due to the advance
  // processing by the I-box must now be undone ... The correct instruction
  // counter value is also shipped back to the I-box.  The interruption
  // action is quite similar to branch recovery".  The model keeps a record
  // per slot (as the wrong-way recovery always kept one per guess) rather
  // than a recovery LEVEL per I-box instruction: same architectural
  // effect, NOT the same level occupancy (docs/spec_lookahead.md's
  // correction to plan §6d stands for both).
  Vector#(4, Reg#(IxRecov))  ixRec        <- replicateM(mkReg(IxRecov{x: replicate(0), ind: 0, adv: 0, sto: 0, oth: 0}));
  Reg#(Bit#(8))              advSeq       <- mkReg(0);   // I-box instructions started (rl_prepare)
  Reg#(Bit#(8))              storeSeq     <- mkReg(0);   // ... of them, stores into storage (isIboxStore)
  Reg#(Maybe#(RetiredLevel)) lastRet      <- mkReg(tagged Invalid);
  // A recovery owed but not yet made (the clock the interruption became
  // due, something -- an I-box instruction held for its operand, part 2 of
  // a progressive level -- was still in the way).  Request/acknowledge
  // counts so each register has one writer; ConfigReg so the watcher
  // (rl_int_watch) can be ordered after the arms that read them.
  Reg#(Bit#(8))              intRecReq    <- mkConfigReg(0);
  Reg#(Bit#(8))              intRecAck    <- mkReg(0);
  Reg#(Bool)                 intDuePrev   <- mkConfigReg(False);
  // WHOSE INDICATOR IS IT.  interruptDue() names an entry, not who turned
  // the indicator on; the recovery is only for the level that completed.
  // rl_int_watch counts (otherSeq) every non-index indicator that rose in
  // a clock other than the one just after a level's completion, or in that
  // clock when an I-box instruction had started beside the completion
  // (iboxAt): an I-box instruction run ahead, an I/O report, the timer.
  // If one has risen since the level's load, recovering would move the
  // counter back before an instruction that already raised its own
  // indicator, and the routine's return would raise it again; so then no
  // recovery (taken after the drain, as before).  Conservative: a level's
  // rise that ever lands in another clock loses its recovery, never the
  // reverse -- except an I-box instruction finishing a read in the very
  // clock a level completes, which is counted as the level's.
  Reg#(Bit#(8))              otherSeq     <- mkConfigReg(0);
  Reg#(Word64)               indPrev      <- mkReg(0);
  Reg#(Bit#(32))             iboxAt       <- mkReg('1);
  // THE E-BOX'S TIME IS THE UNITS' (fidelity_plan.md A5 step 1,
  // 2026-11-26).  What a completed look-ahead instruction still owes is
  // handed to mkSAU or mkPAU as their termination (ebox.terminate) and
  // headReady waits on ebox.unitsTerminated(); until A5 it was a
  // countdown register here, decremented only in a clock in which one of
  // the instruction-unit arms below fired.  That rule is kept exactly:
  // each arm sends eArm, and in the clock after one with no arm the
  // units' count is held (rl_term_hold).  The clocks with no arm are a
  // crossing store's parked tail with nothing else pending (busyXfer by
  // st.storeTailPending() alone) and the clocks the core is stopped.
  PulseWire      eArm     <- mkPulseWire;
  Reg#(Bool)     eArmPrev <- mkReg(True);

  // Stage 2b timing registers (the budgets: StretchTiming.bsv).
  Reg#(Bit#(32)) clk      <- mkReg(0);   // clocks since reset
  // The 1,024-per-second oscillator's divider: Bresenham on the exact
  // rational 78125/24 clocks per tick (StretchTiming.bsv's
  // oscPulseNumer/oscPulseDenom, where the derivation and the choice of
  // an exact rational over a rounded integer period are written out).
  Reg#(Bit#(17)) oscAcc   <- mkReg(0);
  Reg#(Bit#(32)) startClk <- mkReg(0);   // dispatch clock of the current instruction
  Reg#(Bit#(16)) ibusy    <- mkReg(0);   // clocks the next preparation must still wait
  // THE LAAR AFTER ITS STORE LEVEL HAS RETIRED (StretchIBox's
  // laarInternal note has the source, Perf. Char. Vol. 1 printed
  // pp.3-20/3-21).  A store level holds the LAAR while it is pending
  // (laarHeldByLevel); at its removal the model commits the store at
  // once and only CHARGES the E-box time, so the "proper operand is
  // available" only the E-box countdown clocks later, and is then "checked" -- the
  // I-checker's 0.6 us "store operand error check and check code
  // conversion" (printed p.3-19, items 5 and 3) -- and "accepted by the
  // MBCU" (st.storesPending()).  laarFreeAt is the clock the first two
  // are done.  xstoreFreeAt is the same instant for a store into index
  // storage (words 1, 2, 16-31: indexStorageWord below), which in
  // addition stops ALL decoding: "A store into index storage is a time-
  // consuming operation. Whenever such an instruction is decoded, since
  // the next instruction may make use of the new index contents, the
  // I-box does no further decoding until the new index contents arrives"
  // (printed p.3-21).
  Reg#(Bit#(32)) laarFreeAt   <- mkReg(0);
  Reg#(Bit#(32)) xstoreFreeAt <- mkReg(0);
  // >>> AFTER THE INDEX-STORE HOLD, THE NEXT INSTRUCTION IS DECODED,
  // 2026-11-17. <<<  "the I-box does no further decoding until the new
  // index contents arrives" (printed p.3-21): the decode of the
  // instruction after the store BEGINS when the hold ends; it does not
  // run under it.  The model charges a decode as `ibusy` after the
  // level it gates is loaded (rl_prepare), so by the time a store level
  // reaches removal that countdown has long run out and the next
  // instruction was loaded the clock the hold ended -- a VFL ST into
  // $X0-$X3 came out 12.3 clocks under PDF 124's I-BOX column (14.3
  // indexed).  laarRetire sets this for a VFL or connective store into
  // index storage; rl_prepare then charges the prepared instruction's
  // own decode (2 * iboxCycles - 1, as at a load) before loading it.
  // NOT FOR FLOATING POINT: the FP store path into index storage is
  // StretchTiming's laarStorePost(16..31) = 17, a FIT on PDF 48's I-BOX
  // column that already contains whatever followed the hold there, so
  // charging the decode too would count it twice (and move PDF 48 and
  // 69, whose M+ indexed column another change owns).
  Reg#(Bool)     redecodeAfterHold <- mkReg(False);
  // THE LEVEL RELEASE's one-clock yield (2026-11-19; see yieldToPrepare
  // above armPrepare).  Set in the clock a box's resume yields to
  // rl_prepare (the FP box; since 2026-11-23 any box that releases its
  // level, boxReleases), cleared when the resume fires: one yield per box
  // request.
  Reg#(Bool)     resumeYielded <- mkReg(False);
  // THE CLOCK THE E-BOX FINISHES ITS CURRENT INSTRUCTION: the removal
  // clock + the charge + 1 (an E-box time of N occupies N + 1 clocks,
  // StretchTiming's removal-clock note).  Read by headReady for an FP
  // level whose operand is an internal register (fpInternalFetch).
  Reg#(Bit#(32)) eboxDoneAt   <- mkReg(0);
  // AFTER THE INDEX-STORE DECODE HOLD, AN INDEXED I-BOX OPERAND'S TWO
  // READS OF INDEX STORAGE ARE IN SERIES, 2026-11-17.  `xholdPc` names
  // the instruction rl_prepare held behind a store into INDEX STORAGE
  // (xstoreFreeAt, or a pending level storing into words 1, 2, 16-31 --
  // not STORE WAIT's indicator and mask words, which printed p.3-21's
  // hold does not name).  When that same instruction is prepared out of
  // the hold, is FP, indexed, and fetches its operand from index storage,
  // it first spends its index read (fpIndexedIboxClocks, 0.6 us, printed
  // p.3-18) and its operand's I-Checker pass (fpIboxCheckClocks, 0.6 us,
  // printed p.3-19 item 2) before its level is loaded -- RECONSTRUCTION,
  // the reasoning is at fpHoldSerialClocks (StretchTiming).  `serialPaid`
  // is what was spent that way, for the instruction `serialPc`, taken off
  // its level's own `ibusy` at the load so the preparation is not charged
  // twice.  Both are tagged by the instruction's address, and cleared by
  // every preparation and by rl_recover and rl_interrupt, so a prepared
  // instruction that is discarded leaves nothing behind for another.
  Reg#(Maybe#(HWordAddr)) xholdPc    <- mkReg(tagged Invalid);
  Reg#(Bit#(16))          serialPaid <- mkReg(0);
  Reg#(Maybe#(HWordAddr)) serialPc   <- mkReg(tagged Invalid);

  // ioPending's own read-staging flag (docs/phase2_arm_inventory.md
  // conversion order, step 3): only a W-direction (memory->device)
  // word needs a genuine BRAM-eligible read (st.memAddr); RD-direction
  // (device->memory) only ever calls st.writeWord, which stays
  // single-cycle, so this flag is meaningless (and left False) for
  // RD-direction transfers. Separate Reg rather than a new IoXfer
  // field (StretchTypes.bsv) -- confined to this FSM's own bookkeeping
  // in StretchCore.bsv, same reasoning as fetchPending living here
  // rather than folded into pcReg.
  Reg#(Bool) ioReadIssued <- mkReg(False);
  // The same staging flag, for the DEVICE side of an RD-direction tape
  // transfer.  ioReadIssued stages the MEMORY read a W-direction
  // transfer needs; this one stages the TAPE read an RD-direction
  // transfer needs, now that a tape source is allowed to take time
  // (StretchTapeSource.bsv).  Two flags rather than one because the
  // two reads are on opposite sides of the transfer and a single
  // transfer never needs both.
  Reg#(Bool) ioTapeReqIssued <- mkReg(False);
  // The disk's equivalent of ioTapeReqIssued: a platter read is a
  // request and a later response, so the rule has to remember that it
  // already asked.  Separate from the tape's because a transfer is
  // one device at a time and sharing the flag would couple two
  // devices that have nothing to do with each other.
  Reg#(Bool) ioDiskReqIssued <- mkReg(False);
  // Set while a CHAINED control word is being fetched from core
  // storage.  Figure 36 (RefMan printed p.109) says that when the
  // count reaches zero with the chain flag on and the block has not
  // ended, the exchange refills the control word and continues; the
  // refill is a core-storage READ, so like every other read in this
  // rule it needs a request/wait/collect staging flag of its own.
  Reg#(Bool) ioRefillIssued <- mkReg(False);

  // A TERMINATED WRITE LEAVES THE DATA WORD ADDRESS TWO PAST THE NEXT
  // WORD.  Reference Manual printed p.124's table: WRITE, "A_n+2", where
  // A_n = 1 + the address of the last word written.  It comes from the
  // Exchange's two-word buffer, and MCP's commentator depends on it:
  // printed p.309 line 2, "V-I,JXTEM,2.0 -REDUCE CW BY 2".  This model
  // moves one word at a time, so only the state a program can see after
  // the operation ends is reproduced (StretchIO.bsv's header).
  WordAddr writeEndLead = 2;

  // ---- INITIAL PROGRAM LOAD (Reference Manual printed p.126) -------
  // iplActive is set by iplStart() and cleared when the load
  // completes.  iplEntry holds the data word address of the REFILLED
  // control word -- the one the tape's first word becomes -- captured
  // at the refill rather than read back at the end, because by then
  // the exchange's copy has walked its dataAddr past the program.
  Reg#(Bool)     iplActive <- mkReg(False);
  Reg#(UInt#(3)) ioScan    <- mkReg(0);   // rl_io_report's scanner
  Reg#(WordAddr) iplEntry  <- mkReg(0);

  // A DEVICE-TO-CORE STORE.  Every READ-direction store below goes
  // through here.  The one that differs is the IPL read's store into
  // word 4: Reference Manual printed p.126 (PDF p.129), step 3, "The
  // first word read from the unit is stored in the special core storage
  // location referred to by means of address 4", and printed p.35 (PDF
  // p.38), "After an initial program load, this location contains the
  // first word read from the input unit" -- while "Any store to location
  // 4 causes it to contain a 0", which is what writeWord does with it
  // (StretchStorage.bsv).  So that one word takes the exchange's own
  // path, loadWord4, and the chain refill from location 4 then reads the
  // control word.  Any other store, including a non-IPL READ aimed at
  // word 4 (printed p.34 item 4 forbids it; the model does not refuse
  // it), is an ordinary writeWord.
  function Action devStore(WordAddr a, Word64 v);
    action
      if (iplActive && a == addrMaintenanceBits) st.loadWord4(v);
      else st.writeWord(a, v);
    endaction
  endfunction

  // (An instruction waiting on an operand read is held by the E-box
  // itself -- ebox.busy/busyFor/canResume/pending/resume, step 5c --
  // with the owner tag saying whether the instruction unit dispatched
  // it directly or the look-ahead did.)

  // THE ONE PLACE AN INSTRUCTION'S NEXT ADDRESS IS COMMITTED, so the
  // interruption's "do not step the instruction counter" rule is
  // written once rather than at each completion site.  Ordinarily this
  // is just `pcReg <= next`.  While the interruption instruction is in
  // flight it is not: p.48 says the instruction counter is not stepped
  // for it, "however, the instruction counter can be replaced as the
  // result of a successful branching operation" -- so a fall-through
  // leaves pcReg pointing where it already pointed (at the instruction
  // that had not yet run when the interruption was taken), and a taken
  // branch replaces it.
  //
  // Fall-through is recognised as "next is the address after this
  // instruction", which is exactly how the rest of this file already
  // tells a taken branch from a sequential completion (see the `taken`
  // computations below).
  //
  // IT ALSO OWNS branchSeq, the fetch-stream restart, and that is not
  // tidiness -- it is forced.  Written as a write here PLUS the callers'
  // own `if (taken) branchSeq <= ...`, bsc rejects both callers with
  // G0004, "uses methods that conflict in parallel": two writes to one
  // register from a function call and a statement beside it cannot be
  // ordered, even though two plain assignments could.  So the question
  // "did the instruction stream jump?" has to be answered in the same
  // place as "where does it go next?", which is where it belonged.
  function Action commitNext(HWordAddr pc, InstrLen len, HWordAddr next);
    action
      Bool taken = (next != pc + ((len == Full) ? 2 : 1));
      if (intPC matches tagged Valid .ip) begin
        if (taken) pcReg <= next;   // "replaced as the result of a
                                    //  successful branching operation"
        intPC <= tagged Invalid;
        // Always a restart: the stream jumps back to the instruction
        // counter, the mirror of the jump INTO the interruption.
        branchSeq <= branchSeq + 1;
      end else begin
        pcReg <= next;
        if (taken) branchSeq <= branchSeq + 1;
      end
    endaction
  endfunction

  // Dispatch a freshly decoded I-box-class instruction to the E-box
  // (no operand words yet). Either it completes in this clock,
  // committing exactly as execute() always did, or the E-box holds it
  // for its operand read and the resume arm finishes it.
  // WHAT COUNTS AS A HALT, and why a self-branch is not always one.
  //
  // `halted()` exists for the `BEW, $` idiom -- BRANCH ENABLED AND
  // WAIT to its own address -- which is how every program in this
  // corpus says it is finished, and the harness polls it to stop
  // stepping.  "Branched to its own address" is the test.
  //
  // A COUNT AND BRANCH TO ITS OWN ADDRESS IS A DELAY LOOP, NOT A
  // HALT, and MCP printed p.4 line 32 is one:
  //
  //     LCI,0,(8)377777.0        (131,071 into index 0's count)
  //     CB,0,$                   -- count down, branch to itself
  //
  // the wait after RELEASE DISK.  It branches to its own address
  // 131,071 times and then falls through, so a machine stopped there
  // has not finished: it has been interrupted mid-wait.  Before this
  // test existed the MCP boot run ended after ONE decrement, with
  // 131,070 still in the count, and everything printed pp.15-18 do
  // was unreachable behind it.
  //
  // THE DISCRIMINATOR IS THE INSTRUCTION, NOT THE STATE.  A count
  // branch makes progress by construction -- it writes the index
  // register whether or not it branches -- so no other test is
  // needed, and testing the count instead would make `halted` depend
  // on a value the decision site does not have.
  function Bool isHalt(DecodedInstr di, HWordAddr next, HWordAddr pc);
    Bool selfBranch = (next == pc);
    Bool counting = (case (di) matches
                       tagged CountBranch .*: True;
                       default: False;
                     endcase);
    return selfBranch && !counting;
  endfunction

  // A retiring store level releases the LAAR once its operand has been
  // produced (the E-box charge `e`, which occupies e + 1 clocks: see
  // StretchTiming's removal-clock note) and checked (laarCheckClocks),
  // and -- for a floating-point store that fetched nothing (ST, SRD, SLO,
  // SRT) -- once the store path's fitted remainder has run
  // (StretchTiming's laarStorePost, where the fit and its held-out pages
  // are).  A store into index storage also holds all decoding until then,
  // for every class.  Only FP levels take the LAAR (StretchIBox's
  // laarInternal note says why).
  // INDEX STORAGE, for the decode hold below: "$IT, $TC and $0 through $15
  // are in index storage", while "an internal operand address is ...
  // address 3, or an address between 5 and 12 inclusive" (Perf. Char.
  // Vol. 1 printed p.3-20).  So words 1, 2 and 16-31 -- NOT the indicators
  // (11) or the mask (12), which STORE WAIT (storeWaitWord, Fig. 3.1.24)
  // covers but which are internal registers.  Until 2026-11-17 the hold
  // tested storeWaitWord (decks/vfl_cross_special_words.strap: 404 with
  // it, 389 with this set).
  function Bool indexStorageWord(WordAddr w) = (w == 1 || w == 2 || (w >= 16 && w <= 31));

  function Action laarRetire(LaLevel h, Bit#(16) e) =
    action
      if (fpLaarStore(h.di, h.storeAddr) matches tagged Valid .sa) begin   // LFT: word 14 (StretchIBox)
        Bool fp = isFpInstr(h.di);
        // The fitted store path: for a store that fetched nothing (ST,
        // SRD, SLO, SRT), and -- 2026-11-17 -- for ANY FP store into index
        // storage.  "A store into index storage is a time-consuming
        // operation" (printed p.3-21) is said of the destination, not of
        // the operation, so M+ and M+MG into $X9-$X12 take it too.  Their
        // memory and internal stores still do not: PDF 69 prints M+ to
        // memory BELOW ST (StretchTiming's laarStorePost note).  And --
        // 2026-11-17 -- LFT, whose store is into $FT (word 14, memory;
        // StretchIBox's fpLaarStore), takes the memory remainder too.
        Bool indexDest = (sa >= 16 && sa <= 31);
        Bit#(32) t = clk + zeroExtend(e) + 1 + fromInteger(laarCheckClocks)
                   + ((fp && (!isValid(h.da) || indexDest || isFpLft(h.di))) ? zeroExtend(laarStorePost(sa)) : 0);   // LFT: see above
        if (fp) laarFreeAt <= t;
        if (indexStorageWord(sa)) xstoreFreeAt <= t;
        if (indexStorageWord(sa) && !fp) redecodeAfterHold <= True;
      end
    endaction;

  // Returns (completed in this clock, halted).
  function ActionValue#(Tuple2#(Bool, Bool)) startExecute(HWordAddr pc, InstrLen len, DecodedInstr di,
                                           Maybe#(HWordAddr) intIC) =
    actionvalue
      let r <- ebox.start(pc, len, di, replicate(0), 0, OwnerIbox, intIC);
      startClk <= clk;
      if (r matches tagged Valid .o) begin
        commitNext(pc, len, o.next);
        pendingIdxWrite <= o.idxWrite;
        pendingTailWrite <= o.tailWrite;
        ioPending <= o.ioStart;
        xmitPending <= o.xmitStart;
        // >>> A SWAP THAT RUNS SAYS SO. <<<  The question "does any
        // program in this corpus execute a SWAP?" stayed open for
        // four commits and was answered with an indicator trail that
        // can MISS one: tests/gen_tb's op_trail counts RISING EDGES
        // of OP, and a refusal raised while OP is already high leaves
        // no edge.  This cannot be missed, and it is cheap -- it
        // prints only when a swap actually starts.
        if (o.xmitStart matches tagged Valid .xs &&& xs.swap)
          $display("StretchCore: SWAP started at half-word %0d, %0d words", pc, xs.remaining);
        Bool taken = (o.next != pc + ((len == Full) ? 2 : 1));
        ibusy <= budgetClocks(di, taken);   // completed in the dispatch clock
        return tuple2(True, isHalt(di, o.next, pc));
      end else
        return tuple2(False, False);
    endactionvalue;

  // =====================================================================
  // Idiomatic-Bluespec rewrite step 4 (docs/microarchitecture_plan.md
  // §1c): the instruction unit's per-clock work as RULES, not one
  // monolithic step() method. The harness no longer supplies a pulse
  // per clock at all: it raises the machine's RUN LATCH once with
  // `start()` and drops it with `stop()`, and every rule below is gated
  // on `stepping` (= `running && !haltedReg`). No rule fires while the
  // harness is loading storage or reading results, because the latch is
  // down; and a halted machine stops itself rather than waiting to stop
  // being poked.
  //
  // The rules and how they relate, cycle by cycle:
  //   rl_clock        -- the clock counter.
  //   rl_la_fetch     -- look-ahead: collect arrived operands, issue one
  //                      fetch. Every clock. Writes the levels through
  //                      CReg port 0.
  //   rl_ic_controls  -- the 1Y/2Y instruction-buffer controls. Every
  //                      clock. Reads the Y buffers the preparation arm
  //                      also reads (pre-clock values, hence ConfigReg).
  //   then exactly ONE of the six decision arms, the old if/else-if
  //   ladder, each reading the levels through CReg port 1 (i.e. AFTER
  //   this clock's operand arrivals, as the ladder did):
  //   rl_recover      -- wrong-way branch recovery.
  //   rl_io           -- one word of an in-flight RD/W transfer.
  //   rl_idx_write    -- part 2 of a progressive-indexing instruction.
  //   rl_exec_resume  -- an E-box instruction's operand read arrived.
  //   rl_au_remove    -- the arithmetic unit removes the head level.
  //   rl_prepare      -- the instruction unit prepares the next
  //                      instruction (I-box class executes here).
  // The `halted` result the harness used to get back from step() is
  // now a register the executing arms write (True iff the instruction
  // branched to its own address), read through `halted()`; the harness
  // polls it in its run rule's guard, so the step count at halt is
  // unchanged (verified by the CYCLES<= bounds in the suite).
  //
  // Same-clock ordering, made explicit where the old single method had
  // it implicitly: the levels are mkCReg(2) so rl_la_fetch's arrivals
  // (port 0) are visible to the arms (port 1); the units' termination
  // counts down in every arm's clock (eArm); every other register is read in its
  // pre-clock state by every rule, as before.
  // >>> THE I-BOX'S PREPARATION TIME RUNS WHILE THE E-BOX WORKS,
  // 2026-11-17. <<<  `ibusy` used to count down only in rl_prepare's own
  // `ibusy != 0` arm.  The arms are mutually exclusive, so every clock
  // in which the E-box side took the decision -- rl_au_remove removing
  // a level, rl_exec_resume finishing a level's operand read,
  // rl_idx_write writing a progressive level's index -- stopped the
  // I-box's clock as well.  On a homogeneous stream that is one clock
  // per instruction, the removal of the level just prepared: a VFL
  // decode of 3.6 us (iboxCycles 6, 12 clocks) measured 14 clocks a
  // copy (docs/atlas_oracle.md, "Closing the residuals" items 4 and 7),
  // where the immediate compares of PDF 177-182 print 12.  The I-box
  // and the E-box are separate units (Vol. 1 printed p.3-17: the I-box
  // decodes ahead "while" the E-box executes), so the preparation time
  // now counts down in those three arms too, as the E-box countdown counts down in
  // every arm.
  //
  // NOT in rl_io, rl_xmit or rl_tail_write, deliberately.  A transfer or
  // a multi-word transmit holds the storage port and is the instruction
  // still in progress (a transmit's per-word time is its own, Blosk
  // fig.9), so letting its budget run under the drain would shorten T,
  // which is already ~30 clocks short (atlas_oracle.md "Where the model
  // is furthest off" item 2).  rl_tail_write is the crossing-store path
  // (WB XOVR), left as it was.  rl_recover sets its own.
  Bit#(16) ib = (ibusy != 0) ? ibusy - 1 : 0;   // I-box preparation time, counting down

  Bool armRecover  = isValid(recover);
  Bool armIo       = !armRecover && isValid(ioPending);
  // A MULTI-WORD TRANSMIT BLOCKS THE SAME ARMS AN I/O TRANSFER DOES,
  // and for the same reason: it owns the storage write port for as
  // many clocks as it has words left, so nothing else may execute
  // while it drains.  It is ordered AFTER rl_io in this chain because
  // the two cannot coexist -- a transmit is started by an instruction
  // and an instruction cannot start while a transfer is draining --
  // but the ordering is written down rather than assumed.
  Bool armXmit     = !armRecover && !isValid(ioPending) && isValid(xmitPending);
  // A CROSSING VFL FIELD'S TAIL WRITE IS THE THIRD THING THAT MAKES
  // THE MACHINE BUSY, 2026-10-24.  StretchStorage's writeWordTail
  // parks the second word of the store for one clock; while it waits,
  // nothing may be armed, because a newly armed instruction's own
  // write would arrive at the store queue on the clock the tail needs
  // and one of the two would be lost.  Exactly the stall a multi-word
  // transfer gets, for exactly the reason.
  //
  // IT DOES NOT NEED TO BE IN armXmit.  A transmit and a crossing
  // store cannot overlap: a transfer blocks arming through this same
  // boolean, so no ST executes while one drains, and the clock after a
  // crossing ST nothing can be armed either -- so xmitPending cannot
  // become Valid while a tail is pending.  Written down rather than
  // assumed, as with rl_io's ordering above.
  //
  // AND A FOURTH, 2026-11-17: a crossing store's second word below 32,
  // which rl_tail_write makes through writeWord (ExecDone.tailWrite).
  // Being in busyXfer is what puts it before rl_idx_write: the VFL part
  // of a progressive operation first, its index after (printed p.22).
  Bool busyXfer    = isValid(ioPending) || isValid(xmitPending)
                     || st.storeTailPending() || isValid(pendingTailWrite);
  // A REPORT IS STILL OWED on some channel: a control word holds a
  // status bit the exchange has not yet promoted (printed p.118).
  // Read by idle() only.
  function Bool cwHasStatus(WordAddr ch);
    ControlWord c = ioDev.readChanCW(ch);
    return {c.epgk, c.uk, c.ee, c.eop, c.cs} != 0;
  endfunction
  Bool statusWaiting = cwHasStatus(chanDisk) || cwHasStatus(chanReader)
                    || cwHasStatus(chanPrinter) || cwHasStatus(chanTape)
                    || cwHasStatus(chanConsole);

  // >>> THE GATE IS `running` ALONE, AND `!haltedReg` IS DELIBERATELY
  // NOT IN IT. <<<  The first version of this gate was
  // `running && !haltedReg`, to stop a halted machine in the same clock
  // the old harness stopped poking it.  StretchSmoke's scheduling
  // tripwire refused it:
  //
  //     FAIL rl_exec_resume is blocked by core rule(s): rl_clock
  //     FAIL rl_prepare     is blocked by core rule(s): rl_clock
  //
  // -- because `rl_clock` would then READ `haltedReg` through its guard
  // while `rl_exec_resume` and `rl_prepare` WRITE it, so bsc must order
  // the clock ahead of them.  `tick`, being a PulseWire, carried no such
  // dependency.  A gate that silently serialises the clock against the
  // instruction unit is worse than the extra clocks it was buying.
  //
  // WHAT THE EXTRA CLOCKS COST: after the machine halts the harness
  // needs two phases to notice and drop the latch (`afterRun`, then
  // `stopRun`), so the core re-executes its halt -- a branch to its own
  // address, which stores nothing -- for those clocks.  The CYCLES
  // bounds and windows are unaffected because they assert on the
  // HARNESS's `stepCount`, which stops the moment `run`'s
  // `!core.halted()` guard goes false.

  Bool armIdx      = !armRecover && !busyXfer && isValid(pendingIdxWrite);
  Bool armTail     = !armRecover && !isValid(ioPending) && !isValid(xmitPending)
                     && isValid(pendingTailWrite);
  Bool resumeReady = ebox.canResume();
  // (armResume itself is defined below yieldToPrepare, which it waits for.)
  Bool armResumeBase = !armRecover && !busyXfer && !isValid(pendingIdxWrite) && resumeReady;
  // (A branch level has no operand and is removed as soon as it is the
  // head with the E-box free, i.e. once every earlier level has retired.)
  // >>> THE E-BOX MUST BE FREE OF AN I-BOX INSTRUCTION TOO, 2026-11-14. <<<
  // This used to test only `!ebox.busyFor(OwnerLA)`.  An I-box
  // instruction run ahead down a guessed branch's fall-through (an LV
  // reading its index word) can still be waiting on its read when the
  // branch level reaches the head.  Removed then, a wrong guess's
  // `recover` set the counter to the target, and on the next clock
  // rl_exec_resume finished the LV and committed ITS next address over
  // it, so the fall-through ran as if the guess had been right -- and
  // the LV's index write landed after the snapshot was restored.
  // decks/strap2_7030.strap's TBMOV backward loop ("KI(BU,24),0;
  // BZAE,TBMB1" then TBMVX "LV,$3,TBMLK; B,0($3)") lost its second step
  // that way whenever the LV's read was slow enough
  // (tests/check_strap2_7030_tabman.py, found by a memory trace).  A
  // held I-box instruction also cannot share the box with a level that
  // needs an operand: start() would overwrite `held`.
  // >>> AN FP INTERNAL OPERAND IS THE E-BOX'S RESULT, FETCHED AND
  // CHECKED THROUGH THE STORE MECHANISM, 2026-11-17. <<<  Perf. Char.
  // Vol. 1 printed p.3-20 (PDF 38, read in the page image): "The I-box,
  // upon decoding an instruction whose fetch operand is an internal
  // register, uses the LAAR to store the internal operand address. This
  // is because the needed operand is not available during the decoding
  // stage, and the mechanism for internal operand fetch already exists
  // for the handling of store instructions."  So the operand is there
  // only when the instruction before it has finished in the E-box, and
  // it then takes the store path: checked by the I-Checker (0.6 us,
  // printed p.3-19 items 4 and 8) and moved as a store into an internal
  // register is.  The model commits a level's result at its removal and
  // charges the E-box time after, so the level's fetch had the value
  // long before the 7030 would, and its operand cost nothing.  Now the
  // head is not removed until fpInternalOperandClocks after the E-box
  // finishes (StretchTiming, where the number is: the check plus the
  // store path into an internal register that PDF 79's $R column fitted
  // for ST -- the same mechanism, and no new fitted number).  FP only,
  // as the LAAR (StretchIBox's laarInternal note says why).
  // THE OPERAND ADDRESS NEEDS THE ONE LAAR, 2026-11-17: the I-box "uses
  // the LAAR to store the internal operand address" (printed p.3-20), and
  // "since there is only one LAAR, if the latter is busy ... a wait must
  // occur until the LAAR is free for reloading" (printed p.3-21).  So the
  // internal fetch starts when the E-box is done AND the LAAR is free of
  // the store before it (laarFreeAt).  Only a to-memory operation (LFT,
  // M+, M+MG) leaves a store behind it in a homogeneous run; + and L
  // from $R are unchanged.
  Bit#(32) intFrom = (laarFreeAt > eboxDoneAt) ? laarFreeAt : eboxDoneAt;
  // And, 2026-11-17, a VFL or connective head level whose operand is an
  // internal register, by vflInternalOperandClocks (StretchTiming, where
  // the atlas's INTERNL columns give the number).  That one is timed from
  // the E-box alone, NOT intFrom: the VFL and connective charges are fits
  // that already contain their LAAR queuing (StretchIBox's
  // vflInternalFetch note).
  Bool intWait     = (fpInternalFetch(la.headLevel())
                      && clk < intFrom + zeroExtend(fpInternalOperandClocks))
                  || (vflInternalFetch(la.headLevel())
                      && clk < eboxDoneAt + zeroExtend(vflInternalOperandClocks));
  // LFT from memory or index storage waits for the LAAR here, at the head,
  // not at its load (StretchIBox's lftDeferredLaar).
  Bool lftWait     = la.count() != 0 && !la.headLevel().branch
                     && lftDeferredLaar(la.headLevel().di, la.headLevel().da)
                     && clk < laarFreeAt;
  Bool headReady   = la.count() != 0 && ebox.unitsTerminated() && !ebox.busy() && !intWait && !lftWait
                     && la.headLevel().kind != LaStore    // rl_store_retire's
                     && (!isValid(la.headLevel().da) || isValid(la.headLevel().data));
  Bool armRemoveBase = !armRecover && !busyXfer && !isValid(pendingIdxWrite)
                       && !resumeReady && headReady;

  // ---- THE INTERRUPTION MECHANISM (Ref. Manual p.48) ----
  //
  // "Thus, interruption requires the mask bit to be 1, the indicator
  // bit to be 1, and the mechanism to be enabled."  All three are
  // tested inside StretchStorage, which owns all three registers, and
  // arrive here as one latched Maybe: see interruptDue() there for why
  // reading `mask` from a core rule breaks the smoke test's loader
  // rather than this file.
  Maybe#(Tuple2#(Bit#(6), WordAddr)) intDue = st.interruptDue();

  // WHEN IT FIRES.  p.48 says it twice, and the second is the sharper
  // one.  "Interruption Action": "Interruption is permitted after the
  // execution of an instruction is completed, terminated, or suppressed
  // and before execution of the next instruction" -- an INSTRUCTION
  // boundary.  "Mask Register", same page: "occurrence of the
  // corresponding condition will cause program interruption AT THE END
  // OF THE OPERATION DURING WHICH THE INDICATOR IS TURNED ON."  So the
  // interruption belongs to the operation that set the indicator, and
  // must precede the next one.
  //
  // THIS USED TO FIRE LATER, AND THE LATENESS WAS MEASURED.  The
  // condition was the same list plus the E-box countdown at zero.  That is the
  // CHARGED TIME of the instruction just removed from a look-ahead
  // level -- the E-box's cycle budget, not a structural busy -- and
  // rl_prepare does NOT wait for it (it gates on `ibusy`, and a
  // retirement hands it no `ibusy`).  So every I-box instruction that
  // fitted inside the budget ran before the interruption could be
  // taken.  `la.count() == 0 && !ebox.busy()` is the structural
  // condition and it is kept; a retired instruction is functionally
  // complete, which is what p.48 asks about.
  //
  // MEASURED, on decks/int_timing_bracket.strap -- a VFL ST whose
  // store is suppressed, bracketed BE / ST / BD the way jb_ax5b routine
  // 1260 brackets every provoked interruption.  With the old condition
  // the interruption needed THREE instructions of slack before the BD
  // to be taken at all, where p.48 allows zero and the deck leaves one;
  // with fewer, the BD disabled the system first and the pending
  // interruption evaporated (StretchStorage's intDueCalc returns
  // Invalid the moment irqEn goes false).  The halt addresses, and the
  // injection that puts the E-box countdown at zero back and returns the program to
  // 004110.40, are in that program's own header and in docs/NEXT.md
  // item 3.
  //
  // THE OTHER CANDIDATE WAS RULED OUT BY MEASUREMENT, not by argument.
  // interruptDue() is latched a clock behind the indicator write, and
  // that looked like a second cause; with the E-box countdown already dropped, the
  // bracket program passes with the latch in place.  StretchStorage is
  // therefore untouched and its "no program can observe it" note on the
  // latch still stands.
  //
  // WHAT THE RECOVERY COVERS, AND WHAT IT DOES NOT (2026-11-20).  An
  // I-box-class instruction that ran AHEAD of the level raising the
  // interruption is now undone -- its index words, its index indicators
  // and the instruction counter -- by rl_int_recover (the "INTERRUPTION
  // RECOVERY: WHEN" note below armResume), and younger levels are
  // cancelled, with any I-box store held in a store level among them
  // (never made).  NOT when an I-box store was MADE ahead -- into words
  // 0-31, T/SWAP, RNX (taken late after the drain, as before), and not for an interruption
  // with any other cause (an I/O report, the timer, an I-box
  // instruction's own indicator): those still wait for the levels to
  // drain here.  docs/NEXT.md "AN INTERRUPTION RAISED BY A LEVEL".
  // (run_tests.sh's two notes on interruption timing -- in the
  // df_data_fetch_alarm section and the interrupt_pg0 one -- still
  // describe the OLD behaviour and are stale.)
  // ---- THE INSTRUCTION BEING PREPARED (hoisted from rl_prepare, 2026-11-19) ----
  // While the interruption instruction is in flight, THAT is the
  // instruction being prepared; pcReg is left pointing at the
  // instruction the interruption displaced (p.48).
  Vector#(4, LaLevel) prepNl = la.levels();
  HWordAddr prepPc = fromMaybe(pcReg, intPC);
  function Maybe#(Tuple2#(InstrLen, DecodedInstr)) preparedAt(HWordAddr pc);
    Maybe#(Tuple2#(InstrLen, DecodedInstr)) prepared = tagged Invalid;
    if (ibuf.lookup(pc[18:1]) matches tagged Valid .w0) begin
      HalfWord32 hw0 = (pc[0] == 0) ? w0[63:32] : w0[31:0];
      InstrLen len = instrLen(hw0);
      if (len == Half)
        prepared = tagged Valid tuple2(len, decode(hw0, tagged Invalid));
      else begin
        HWordAddr pc1 = pc + 1;
        if (ibuf.lookup(pc1[18:1]) matches tagged Valid .w1) begin
          HalfWord32 hw1 = (pc1[0] == 0) ? w1[63:32] : w1[31:0];
          prepared = tagged Valid tuple2(Full, decode(hw0, tagged Valid hw1));
        end
      end
    end
    return prepared;
  endfunction
  Maybe#(Tuple2#(InstrLen, DecodedInstr)) prepPrepared = preparedAt(prepPc);
  function Bool progressiveIn(Vector#(4, LaLevel) nl);
    Bool r = False;
    for (Integer k = 0; k < 4; k = k + 1)
      if (nl[k].valid && hasProgressive(nl[k].di)) r = True;
    return r;
  endfunction
  Bool prepProgressivePending = progressiveIn(prepNl);
  // >>> STORE CLOSE TO FETCH, FOR AN INSTRUCTION WORD, 2026-11-17. <<<
  // Perf. Char. Vol. 1 printed p.3-21 (PDF 39): "One such conflict is a
  // store into a location corresponding to a prefetched instruction ...
  // When such a store is decoded, I-box invalidates the prefetched
  // instructions and waits until the correct information is available."
  // The model had the invalidation (mkInstrBuffers' program store
  // compare) but only when the store is MADE, at the level's removal; an
  // instruction prepared out of 1Y/2Y before that ran as it was
  // assembled.  So: do not prepare an instruction whose word (either
  // word, for a full-word one) a pending level stores.  CHOSEN: the 7030
  // waits at the decoding of the store; the model waits at the
  // instruction in the stored word, which holds back the same
  // instructions.  Exposed when the preparation floor was fixed (`ib`):
  // the 7030 STRAP II TABMAN's "ST(BU,6),TBEN4+.35" three instructions
  // before TBEN4, and C22-6578 Problem 2.9's "ST(BU,4),SV+0.19" into the
  // very next instruction, both ran the unmodified instruction
  // (decks/store_into_prepared_instr.strap).
  //
  // AND FOR THE CLOCK AFTER THE STORE IS MADE.  The level retires in the
  // clock its store enters the store queue; StretchStorage reports it
  // through recentStore() on the next clock, and only then does
  // rl_ic_controls invalidate the Y word (a ConfigReg, seen the clock
  // after).  In between, the level is gone and the stale word is still
  // in 1Y/2Y, so a store to the word reported this clock holds the
  // preparation too.  Measured: without this term the deck's W0 still
  // came back stale.
  function Bool storesInto(WordAddr w);
    Bool r = False;
    for (Integer k = 0; k < 4; k = k + 1)
      if (levelStores(prepNl[k], w)) r = True;
    if (st.recentStore() matches tagged Valid .rs &&& rs == w) r = True;
    return r;
  endfunction
  function Bool instrStoredAt(HWordAddr pc, Maybe#(Tuple2#(InstrLen, DecodedInstr)) prepared);
    HWordAddr pcNext = pc + 1;
    Bool r = storesInto(pc[18:1]);
    if (prepared matches tagged Valid {.plen, .*} &&& plen == Full &&& storesInto(pcNext[18:1]))
      r = True;
    return r;
  endfunction
  Bool prepInstrStored = instrStoredAt(prepPc, prepPrepared);

  // ---- THE LEVEL RELEASE: THE FP BOX'S RESUME YIELDS ONE CLOCK (2026-11-19) ----
  //
  // WHAT IT RECOVERS.  With the floating-point add inline (before plan
  // §1c step 5f stage 2) a level's add completed in its removal clock, and
  // the next clock was rl_prepare's: the I-box started the instruction
  // behind it at once.  With the add in mkFpBox the removal clock issues
  // the request, the box answers, and the NEXT clock is rl_exec_resume's,
  // which takes the arm rl_prepare would have had; and while the box holds
  // the level, rl_prepare would not start an I-box instruction anyway
  // (`!ebox.busyFor(OwnerLA)`: one `held`).  Measured: the 981 CYCLES pin
  // of decks/fp_mplus_ds_not_df.strap went to 985, the NOP behind each add
  // a clock late.  So, in the clock the box has ANSWERED, and only then:
  //
  //   the resume YIELDS -- once per request (resumeYielded) -- if
  //   rl_prepare would START AN I-BOX INSTRUCTION this clock (the ladder
  //   rl_prepare walks: no I-box budget left, no interruption due, the
  //   store queue free, no store wait, nothing storing into the
  //   instruction, and iboxHazard clear), and rl_prepare may start that
  //   one instruction BESIDE the held level.  mkEBox's start() runs it only
  //   if it completes at once, and refuses it (no effect) if it would need
  //   a read or a box of its own: there is one `held`.  The resume fires
  //   the clock after.  The E-box's time is unchanged by the wait:
  //   rl_exec_resume charges ebudget - boxK, and boxK counts the yielded
  //   clock.
  //
  // WHY ONLY THEN, AND ONLY ONE (2026-11-20).  An I-box instruction started
  // beside the level commits before the level's indicators are set, so an
  // interruption the level raises is taken after it -- and the 7030 does
  // not let that be seen: "All changes in the index registers and/or index
  // indicators due to the advance processing by the I-box must now be
  // undone" (Perf. Char. Vol. 1 printed p.3-24, PDF 42, of wrong-branch
  // recovery and of interruption, listed together on p.3-23, PDF 41: "The
  // interruption action is quite similar to branch recovery"); Buchholz
  // §15.6 (printed pp.246-247, PDF 271-272): the look-ahead's
  // housecleaning restores every index word the instruction unit modified
  // and returns that unit "to the point in the program at which
  // interruption occurred"; Ref. Manual printed p.9 (PDF 12), look-ahead
  // "makes the machine appear as if it were dealing with only one
  // instruction at a time".  Since 2026-11-20 the model undoes the
  // index words, index indicators and counter (rl_int_recover); until the
  // store level (deferIboxStores, the same day) it could NOT undo a
  // store an I-box instruction made ahead (it then took the interruption
  // late, after the drain).  So from 2026-11-20 to 2026-11-23 the release
  // was confined to the overlap the model ALREADY had with the add inline
  // (the 981 pin, now 1056: the recovery re-runs what ran ahead of the
  // deck's five DS levels; with the recovery window injected off it is 981
  // again, 2026-11-20): one instruction, in the clock after the result was
  // formed.  SINCE 2026-11-23 THE HOLD CLOCKS ARE OPEN TOO (besideHold,
  // below armResume; liftHoldClocks is its switch): with the store level
  // the confinement's reason is gone.  The Vol. 2 atlas is byte-identical
  // with it; it gives back fp_box_release_interlock 1153 -> 1142,
  // fp_box_interrupt_landing 426 -> 425 and int_recovery_resume 612 -> 611
  // (each restored with liftHoldClocks := False); decks/fp_box_hold_store
  // .strap pins an SX started there.  SINCE 2026-11-23 (stage 3) THE SAME
  // FOR THE DIVIDER, THE DECIMAL ADDER AND THE VFL MULTIPLIER (boxReleases,
  // below, one switch each; decks/div_box_release, dec_box_release,
  // vfl_box_release).
  //
  // THE INTERLOCK.  The held level stays in the look-ahead (la.retireHead
  // is in rl_exec_resume), so iboxHazard sees it exactly as it sees any
  // pending level: an I-box instruction that reads the accumulator, the
  // factor or the indicator words (eboxRegister), or branches on a non-
  // index indicator, or stores where the level stores, still waits.
  // AN I-BOX STORE'S STORE LEVEL: the switch and the word (the note at
  // storeNeedsLevel, below).
  Bool deferIboxStores = True;
  // The core-storage word an I-box store writes, as indexed now; Invalid
  // for every other instruction and for a word below 32.
  function Maybe#(WordAddr) iboxStoreWord(DecodedInstr d);
    Maybe#(WordAddr) w = tagged Invalid;
    case (d) matches
      tagged DirIndex .x:
        if (x.code == dixop_SX || x.code == dixop_SV || x.code == dixop_SC
            || x.code == dixop_SR || x.code == dixop_SVA) begin
          HWordAddr ea = effAddr19(st, x.addr, x.idx);
          w = tagged Valid ea[18:1];
        end
      tagged BranchOrMisc .x:
        if (x.misc && x.code == 3'b100)                                   // Z
          w = tagged Valid baWord(effAddr24(st, {x.addr, 5'b0}, x.idx));
      tagged Sic .x: begin
        BitAddr ea = effAddr24(st, x.addr, x.idx);
        w = tagged Valid ea[23:6];
      end
      default: w = tagged Invalid;
    endcase
    if (w matches tagged Valid .a &&& a < 32) w = tagged Invalid;
    return w;
  endfunction
  // LVE READS A CHAIN OF WORDS (Ref. Manual printed p.29), and iboxHazard
  // tests only the first, so while a store level is pending an LVE could
  // read a held word as storage still has it.  Before the store level the
  // write was in the store queue, which holds every read off.  So an LVE
  // waits for the store levels.  A MODEL rule, the narrowest that keeps
  // the chain from reading a held word; the pages give LVE a look-ahead
  // drain only with its address in index storage (Perf. Char. Vol. 1
  // Tables 4-9, IR column; docs/spec_lookahead.md 2.2 item 6, 3.6).  It
  // costs decks/negative_effective_address.strap 15 clocks (812 -> 827
  // with it removed; tests/run_tests.sh at the run line).
  function Bool lveBehindStore(DecodedInstr d, Vector#(4, LaLevel) nl);
    Bool st_ = False;
    for (Integer k = 0; k < 4; k = k + 1)
      if (nl[k].valid && nl[k].kind == LaStore) st_ = True;
    Bool lve = False;
    if (d matches tagged DirIndex .x &&& x.code == dixop_LVE) lve = True;
    return lve && st_;
  endfunction
  function Bool prepWouldAct();
    Bool r = False;
    if (prepPrepared matches tagged Valid {.len, .di}) begin
      Bool branchLevel = False;   // rl_prepare loads these into a level instead
      if (di matches tagged BranchInd .bi &&& !indexIndicator(bi.indNum)) branchLevel = True;
      // An E-box-class instruction or an indicator branch's guess does not
      // yield: measured, that also moved Perf. Char. Vol. 2's M+ EXTERNAL
      // columns (atlas PDF 100-101) further from the printed times.
      if (!isEboxClass(di) && !branchLevel)
        r = !iboxHazard(st, guessPending, di, prepNl)
            && !(deferIboxStores && isValid(iboxStoreWord(di)) && la.count() == 4)
            && !lveBehindStore(di, prepNl);
    end
    return r;
  endfunction
  // >>> EVERY BOX RELEASES ITS LEVEL, 2026-11-23 (plan §1c 5f stage 3). <<<
  // The FP box's release (yieldToPrepare, besideHold below) for the
  // divider (FP and VFL divide), the decimal adder (VFL decimal add) and
  // the VFL multiplier as well.  The pages make no exception by unit:
  // Perf. Char. Vol. 1 printed p.3-16 (PDF 34), "the local autonomy of
  // the major units: ... the I-box, the look-ahead (LA), the E-box",
  // "Each major unit is responsible for processing at top speed as long
  // as there is data to process", "temporary delays up to several us in
  // one unit can be tolerated without slowing down the entire pipe line";
  // printed p.3-18 (PDF 36), "The processing time of I-box instructions
  // can be largely overlapped by concurrent E-box action".  The E-box is
  // one unit to these pages, its serial (VFL, decimal) and parallel (FP,
  // multiply, divide) parts alike.  The radix converter (DCV, boxKind 2)
  // is left confined: not in this step.  One switch per box; each is the
  // attributing injection for what it moves.
  Bool releaseDivBox = True;
  Bool releaseDecBox = True;
  Bool releaseVflBox = True;
  Bool boxReleases = case (ebox.laBoxWaiting()) matches
                       tagged Valid 4: True;                 // FP box (2026-11-19)
                       tagged Valid 0: releaseDivBox;
                       tagged Valid 1: releaseDecBox;
                       tagged Valid 3: releaseVflBox;
                       default:        False;
                     endcase;
  Bool yieldToPrepare = resumeReady && boxReleases && !resumeYielded
                        && !ebox.busyFor(OwnerIbox) && ibusy == 0
                        && !isValid(intDue) && !isValid(intPC)
                        && st.writeReady() && !storeWait(prepNl) && !(clk < xstoreFreeAt)
                        && !redecodeAfterHold && !prepInstrStored
                        && prepWouldAct();
  Bool armResume   = armResumeBase && !yieldToPrepare;
  // AND IN THE BOX'S HOLD CLOCKS (2026-11-23, plan §1c 5f stage 2): an
  // I-box instruction may start beside the level the FP box (since stage
  // 3, any box that releases: boxReleases) holds while the box works, not
  // only in the clock it answered.  The confinement's
  // reason is gone: what such an instruction does is given back if the
  // held level interrupts (rl_int_recover), and a store it makes waits in
  // a store level (deferIboxStores) -- the undo the 7030 does (Perf.
  // Char. Vol. 1 printed p.3-24; Buchholz §15.6), which the confinement
  // stood in for (the FP box's release note).  `liftHoldClocks` is the
  // switch (part a).
  Bool liftHoldClocks = True;
  Bool besideHold = liftHoldClocks && boxReleases && !resumeReady;
  // An instruction mkEBox's start() REFUSES beside a held level (one that
  // needs a read or a box) has had no effect, so it is not counted as an
  // advance and holds nothing: it is offered again next clock.
  // `uncountRefused` is the switch (part b).
  Bool uncountRefused = True;

  // ---- INTERRUPTION RECOVERY: WHEN (plan §1c 5f, 2026-11-20) ----
  // Buchholz §15.6 (printed p.246, PDF 271): "As soon as the arithmetic-
  // bus counter senses an interrupt, the instruction unit and arithmetic
  // unit are signaled to stop preparing and executing more instructions";
  // the levels after it are housecleaned, "the old contents of the index
  // word" put back for each level "for which the instruction unit has
  // previously modified an index word", and (printed p.247, PDF 272) "the
  // proper instruction-counter setting is sent to the instruction unit to
  // return that unit to the point in the program at which interruption
  // occurred".  In the model the indicator a level sets reaches
  // interruptDue() two clocks after the level completes (StretchStorage
  // latches it; measured with a $display on decks/int_recovery_resume.strap
  // case F: completion at clock 478, the rise at 480), so:
  //   intWin       -- the two clocks after a level completed with the
  //                   system enabled: the next level is NOT removed into
  //                   the E-box (it may be the one the interruption must
  //                   keep from executing); the I-box may still prepare,
  //                   which recovery undoes.  NO DECK REACHES THIS HOLD
  //                   (injected away, 2026-11-20: nothing in the three
  //                   recovery decks moves): a completing level charges
  //                   the E-box countdown, and headReady waits for it, so a younger
  //                   level is removed in the window only after a level
  //                   charged 0 or 1 clock.  Kept for that case.
  //   intRecWanted -- an interruption became due inside that window (or
  //                   did earlier and the recovery is still owed).
  // An interruption due for any other reason (an I/O report, the timer,
  // an I-box instruction's own indicator, or one already due at the
  // level's completion) is taken as before, after the levels drain.
  Bool intWin = st.irqEnabled() && isValid(lastRet)
                && (clk - validValue(lastRet).at) >= 1 && (clk - validValue(lastRet).at) <= 2;
  Bool intRise = isValid(intDue) && !intDuePrev && !isValid(intPC);
  Bool intRecWanted = (intRecReq != intRecAck) || (intRise && intWin);

  // ---- AN I-BOX STORE GOES INTO A STORE LEVEL (plan §1c 5f, 2026-11-20) ----
  // THE PAGES.  Perf. Char. Vol. 1 printed p.3-20 (PDF 38): "All 'to-
  // memory' operations involving the main memory from the 7030 CPU are
  // prepared by the I-box and accomplished by the look-ahead", and "In
  // the case of I-box store type instructions (SX, SV, SC, SR, SVA, R,
  // RXZ, T, SWAP, etc.) the store operands are already available during
  // I-box processing time and can be converted to ECC check bits during
  // shipment to LA"; Table A-2 (PDF 69, docs/spec_lookahead.md 1.7): SX,
  // Z, SV, SC, SR, SVA and a taken SIC each load a "store" level.
  // Buchholz §15.3 (printed p.240, PDF 265): the store-check counter
  // "designates the next level from which an operand is to be sent to
  // storage" -- the ring counters advance level by level, in order -- and
  // §15.5 (printed p.246, PDF 271): "The arithmetic-bus counter first
  // tests whether an interrupt is waiting, which would cause the present
  // sequence to be abandoned".  So a store an I-box instruction made
  // AHEAD of an older level reaches storage only after that level, and an
  // interruption the older level raises housecleans it first: "The
  // instruction and look-ahead units may be working on instructions which
  // may never recur after the interruption and which, therefore, should
  // leave no traces" (§15.1, printed p.230, PDF 255).
  // THE MODEL.  An I-box store into core storage that completes while a
  // level is pending (or in the interruption window after one completed,
  // or with a recovery owed) is still executed as before, but its write
  // is held (StretchStorage captureStore) in a STORE LEVEL loaded at the
  // tail: kind LaStore, storeAddr = the word.  It is the look-ahead's
  // like any level -- younger readers wait for it (levelHolds, waitFor,
  // the instruction-word compare), a drain waits for it, cancelAll
  // housecleans it (its store is then never made) -- and rl_store_retire makes the store
  // when it reaches the head, outside the window, as the E-box removal
  // waits.  No E-box time, and no I-box time beyond the arm clock: the
  // "0.9 to 1.2 us to process an LA level corresponding to I-box
  // instructions" (printed p.3-22, PDF 40) is not charged for any I-box
  // level in this model, and is not started here.  NOT HELD: a store into
  // words 0-31 (written at once, as before; words 7-15 wait on a pending
  // level by iboxHazard, the index words 16-31 are in the recovery
  // record, words 1-6 are not), T/SWAP, RNX, and the LAAR is not modelled
  // for it (Table A-2 says "yes"; the model's one LAAR is FP-only).
  // deferIboxStores is the switch the attributing injection turns off.
  // (deferIboxStores and iboxStoreWord are above prepWouldAct.)
  Bool storeNeedsLevel = deferIboxStores && !isValid(intPC)
                         && (la.count() != 0 || intWin || intRecWanted);
  // In the clock the I-box store completes: hold it in a store level.
  function Action holdStoreInLevel(HWordAddr pc, InstrLen len, DecodedInstr d, WordAddr w) =
    action
      la.load(LaLevel{valid: True, kind: LaStore, di: d, pc: pc, len: len, da: tagged Invalid,
                      data: tagged Invalid, fetchIssued: False, waitFor: tagged Invalid,
                      branch: False, target: 0, storeAddr: tagged Valid w,
                      storeAddr2: tagged Invalid, carry: LaCarry{addr: 0, lbo: 0}});
      st.captureStore(la.tail(), w);
    endaction;
  Bool headStore = la.count() != 0 && la.headLevel().kind == LaStore;
  Bool armStoreRetire = !armRecover && !busyXfer && !isValid(pendingIdxWrite)
                        && !resumeReady && headStore && !intWin && !intRecWanted
                        && st.writeReady();
  Bool armIntRecover = intRecWanted && !armRecover && !busyXfer && !isValid(pendingIdxWrite)
                       && !ebox.busy();
  Bool armRemove   = armRemoveBase && !intWin && !intRecWanted;

  Bool armInterrupt = !armRecover && !busyXfer && !isValid(pendingIdxWrite)
                      && !resumeReady && !headReady && !intRecWanted
                      && !isValid(intPC)          // one instruction, then done
                      && la.count() == 0 && !ebox.busy() && ibusy == 0
                      && isValid(intDue);
  Bool armPrepare  = !armRecover && !busyXfer && !isValid(pendingIdxWrite) && !armIntRecover
                     && !armStoreRetire
                     && (!resumeReady || yieldToPrepare) && (!headReady || (armRemoveBase && !armRemove))   // removal held by intWin only
                     && !armInterrupt;

  (* fire_when_enabled *)
  // THE CLOCKS THE E-BOX'S TIME DOES NOT COUNT (eArm's note).
  rule rl_eclk;
    eArmPrev <= eArm;
  endrule
  rule rl_term_hold (!eArmPrev);
    ebox.holdTerm();
  endrule

  rule rl_clock (running);
    clk <= clk + 1;
    // ---- THE OSCILLATOR PULSE ----
    // Reference Manual printed p.34: "The timer runs whenever the
    // machine is operating, which includes also the execution of BRANCH
    // ENABLED AND WAIT."  `stepping` IS this model's "the machine is
    // operating" signal -- a run latch the harness raises once and
    // never while it is loading the program image or reading results --
    // so the pulse is generated here rather than by a free-running rule
    // inside StretchStorage, which would count the timer down through
    // gen_tb.py's loader (one clock per word, thousands of them) and
    // hand the first instruction a timer that was already stale.  BEW
    // does not stop the clock in this model (it is a self-branch the
    // harness leaves running), so p.34's named case needs nothing extra.
    Bit#(17) acc = oscAcc + fromInteger(oscPulseNumer);
    if (acc >= fromInteger(oscPulseDenom)) begin
      acc = acc - fromInteger(oscPulseDenom);
      st.oscillatorPulse();
    end
    oscAcc <= acc;
  endrule

  // ---- Look-ahead: collect arrived operands, issue one fetch ----
  // (No fire_when_enabled on this rule or rl_ic_controls: they share the
  // look-ahead / Y-buffer bus channels with the exported `mem`
  // interface, and at the synthesized boundary bsc must assume the
  // harness could call those methods while the latch is up. It never
  // does -- it reads only between phases -- but that is a harness
  // fact, not something the scheduler can prove here.)
  rule rl_la_fetch (running);
    la.collect();
  endrule

  // ---- IC controls: run every clock, alongside the instruction FSM ----
  rule rl_ic_controls (running);
    Bool restart = (restartSeq != restartSeen) || (branchSeq != branchSeen);
    // While the interruption instruction is in flight the fetch stream
    // follows IT, not the instruction counter -- the counter is
    // deliberately standing still (p.48).
    HWordAddr fetchPC = fromMaybe(pcReg, intPC);
    ibuf.advance(fetchPC[18:1], restart);

    if (restart) begin
      restartSeen <= restartSeq;
      branchSeen <= branchSeq;
    end
  endrule

  // UNDO THE I-BOX'S ADVANCE: the index words and the index indicators
  // as a level's record holds them (both recoveries; Perf. Char. Vol. 1
  // printed p.3-24, PDF 42: "All changes in the index registers and/or
  // index indicators due to the advance processing by the I-box must now
  // be undone").  keepX / keepInd leave what the level itself wrote.
  function Action undoAdvance(IxRecov r, Bit#(16) keepX, Bool keepInd) =
    action
      st.restoreIndex(r.x, keepX);   // keepX's words are left as they are
      if (!keepInd) begin
        Word64 ind = st.readIndicators();
        st.setIndicatorBits((ind & ~indexIndMask) | (r.ind & indexIndMask));
      end
    endaction;

  // What a completing level wrote into the index words itself (RetiredLevel).
  function Bit#(16) ownIndexWrites(LaLevel h, ExecDone o);
    Bit#(16) k = 0;
    if (o.idxWrite matches tagged Valid {.j, .*}) k[j] = 1;
    if (o.tailWrite matches tagged Valid {.a, .*} &&& a >= 16 &&& a <= 31) k[a - 16] = 1;
    if (h.storeAddr matches tagged Valid .a &&& a >= 16 &&& a <= 31) k[a - 16] = 1;
    if (h.storeAddr2 matches tagged Valid .a &&& a >= 16 &&& a <= 31) k[a - 16] = 1;
    return k;
  endfunction
  function Action noteRetired(LaLevel h, ExecDone o) =
    action
      lastRet <= tagged Valid RetiredLevel{pc: h.pc, len: h.len, rec: ixRec[la.head()],
                                           keepX: ownIndexWrites(h, o),
                                           ownInd: isValid(o.idxWrite), at: clk};
    endaction;

  // The interruption's own watcher: the edge of interruptDue() and the
  // owed recovery (intRecReq).  Reads what the arms write and writes only
  // ConfigRegs the arms read, so it sits after them in the clock.
  (* fire_when_enabled *)
  rule rl_int_watch (running);
    intDuePrev <= isValid(intDue);
    Word64 indNow = st.readIndicators();
    indPrev <= indNow;
    Bool levelClock = isValid(lastRet) && clk == validValue(lastRet).at + 1
                      && iboxAt != validValue(lastRet).at;
    if ((indNow & ~indPrev & ~indexIndMask) != 0 && !levelClock)
      otherSeq <= otherSeq + 1;
    if (intRise && intWin && !armIntRecover) intRecReq <= intRecReq + 1;
  endrule

  // >>> INTERRUPTION RECOVERY, 2026-11-20 (plan §1c 5f). <<<  The level
  // that completed last (lastRet) raised an interruption: as for a wrong
  // branch, cancel the younger levels, give back the index words and index
  // indicators the I-box changed after that level was loaded, and return
  // the instruction counter to the instruction after it; rl_interrupt then
  // takes the interruption there (Ref. Manual printed p.48: "at the end of
  // the operation during which the indicator is turned on", "before
  // execution of the next instruction").  Nothing to give back (nothing
  // prepared after the level): no effect.
  // A STORE TO CORE STORAGE an I-box instruction made ahead (SX, SV, SC,
  // SR, SVA, Z, SIC) is in a store level since 2026-11-20 (the note at
  // deferIboxStores) and is housecleaned with the younger levels: never
  // made.  NOT GIVEN BACK: an I-box store MADE ahead -- into words 0-31,
  // T/SWAP, RNX, KC/LVE (isIboxStore counts them), or any store while
  // deferIboxStores is off -- so when one has started since the level's
  // load there is no recovery at all (`stored`, below); and any indicator
  // other than the index ones.  No time is charged for the housecleaning: no page found
  // gives a number for it (Perf. Char. Vol. 1 PDF 11 and 63 list its
  // steps only), so the I-box's own countdown runs on.
  rule rl_int_recover (running && armIntRecover);
    intRecAck <= intRecReq;
    let r = validValue(lastRet);
    HWordAddr nxt = r.pc + ((r.len == Full) ? 2 : 1);
    Bool advanced = advSeq != r.rec.adv;
    Bool stored   = storeSeq != r.rec.sto;
    Bool foreign  = otherSeq != r.rec.oth;
    if (foreign)
      // SOMETHING ELSE RAISED AN INDICATOR since the level's load (the
      // WHOSE INDICATOR note at otherSeq): no recovery, taken after the
      // drain as before 2026-11-20.
      $display("StretchCore: interruption at half-word %0d NOT recovered: an indicator rose outside the level's completion", nxt);
    else if (stored)
      // AN I-BOX STORE WAS MADE AHEAD (one not held in a store level, the
      // note above): it cannot be taken back, and returning the counter
      // would run it (and what led to it) AGAIN when the routine returns
      // -- "LX / V+I / SX" behind the level would count twice.  So no
      // recovery: the interruption is taken after the levels drain, late,
      // as before 2026-11-20 (the wrong-way recovery never meets this:
      // iboxHazard holds an I-box store while a guess is pending).  The
      // backstop since the store level (docs/NEXT.md).
      $display("StretchCore: interruption at half-word %0d NOT recovered: an I-box store ran ahead", nxt);
    else if (advanced || la.count() != 0 || pcReg != nxt) begin
      if (advanced) undoAdvance(r.rec, r.keepX, r.ownInd);
      la.cancelAll();      // with any store levels: their stores are never made
      guessPending <= False;
      pcReg <= nxt;
      // THE REFETCH COSTS TWO CLOCKS THE PAGES DO NOT GIVE: rl_interrupt
      // follows and restarts the fetch at the routine, throwing this one
      // away (MEASURED, injection: without this restart
      // fp_box_interrupt_landing runs 424 clocks / 36 reads, every other
      // pin unchanged; with it 426 / 40).  Kept because without it pcReg
      // moves with no restart, and nothing guarantees an interruption then
      // follows (an index indicator undone here may have been its cause).
      // docs/NEXT.md "AN INTERRUPTION RAISED BY A LEVEL" item 5.
      branchSeq <= branchSeq + 1;
      xholdPc <= tagged Invalid;
      serialPc <= tagged Invalid;
      $display("StretchCore: interruption recovery to half-word %0d (index %s, %0d younger level(s) cancelled)",
               nxt, advanced ? "restored" : "unchanged", la.count());
    end
    eArm.send;
    ibusy <= ib;
    haltedReg <= False;
  endrule

  // THE STORE LEVEL REACHES THE STORE-CHECK COUNTER: its held store goes
  // to storage, in order (the note at deferIboxStores).  Not in the two
  // clocks after a level completed, nor with a recovery owed: the level
  // ahead of it may yet be the one an interruption belongs to.
  rule rl_store_retire (running && armStoreRetire);
    st.releaseCaptured(la.head());
    la.retireHead();
    eArm.send;
    ibusy <= ib;
    haltedReg <= False;
  endrule

  (* mutually_exclusive = "rl_recover, rl_io, rl_tail_write, rl_idx_write, rl_exec_resume, rl_au_remove, rl_prepare, rl_int_recover, rl_store_retire" *)
  rule rl_recover (running && armRecover);
    // Wrong-way recovery (Perf. Char. p.3-23): undo the index
    // registers and index indicators the I-box changed ahead, take the
    // branch, and refetch. Charged as the branch's own execution
    // cycles again plus the refill the restart costs.
    let tgt = validValue(recover);
    undoAdvance(ixRec[recoverSlot], 0, False);
    pcReg <= tgt;
    branchSeq <= branchSeq + 1;
    recover <= tagged Invalid;
    ibusy <= 12;
    xholdPc <= tagged Invalid;    // the prepared instruction is discarded
    serialPc <= tagged Invalid;
    eArm.send;
    haltedReg <= False;
  endrule

  rule rl_io (running && armIo);
    // Service one word of an in-flight RD/W transfer. See this
    // interface's step() doc above and StretchIO.bsv's file header.
    // Capacity is device-kind-dependent: the tape's TapeWords is
    // deliberately smaller than the reader/printer's DeviceWords
    // (see StretchIO.bsv) so this is where that distinction has to
    // be made, not a single shared constant.
    let x = validValue(ioPending);
    DeviceKind kind = kindOf(x.ch);
    // THE TAPE'S CAPACITY NOW COMES FROM THE SOURCE, not from a
    // typedef: a file- or SD-backed source holds a reel, and the End
    // Exception test ("the unit runs out of material", p.121) has to
    // ask it rather than assume the 16-word register image.  The
    // reader and printer are still fixed-size Vectors in StretchIO.
    Bit#(25) capacity = (kind == DevTape)
      ? zeroExtend(ioDev.tapeCapacity())
      // THE DISK'S CAPACITY COMES FROM ITS SOURCE TOO, and for the
      // same reason the tape's does: a 353 is 2^21 words (Reference
      // Manual printed p.157) and the small source in
      // StretchDiskSource.bsv is two arcs.  Running off the end is
      // End Exception, exactly as running off the end of a reel is.
      : (kind == DevDisk) ? zeroExtend(ioDev.diskCapacity())
      // THE CONSOLE HAS TWO CAPACITIES, one per direction.  A WRITE
      // walks the paper, DeviceWords of it; a READ scans the switch
      // register, and Reference Manual printed p.150 says how many
      // there are -- "a word weight of 3", and a READ "is
      // automatically terminated when the three words scanned from
      // the switches have been sent to the exchange".  A read asking
      // for more than three therefore ends on the End Exception arm
      // below, which is this model's "the unit runs out of material"
      // (p.121) and the nearest thing the manual gives to
      // "automatically terminated".  MCP asks for exactly three
      // (printed p.21 line 31's "X DCW 2  CW,X LR IN,3,0"), so
      // nothing on the boot path depends on that choice -- but
      // something had to be chosen and this says so.
      : (kind == DevConsole && !x.isWrite)
          ? fromInteger(valueOf(ConsoleSwitchWords))
      // and the WRITE never runs out.  A 7152 typewriter's paper is
      // continuous, so a console write never ends in End Exception
      // for lack of paper.  Until 2026-11-07 it ended at ConsoleWords,
      // a chosen model buffer, and MCP's acknowledgement of
      // COMD,CLOCK hit that end and retried 13,457 times
      // (docs/boot_plan.md, "THE COMMAND PACKAGE RUNS").  Every typed
      // word now goes to the log as it is typed (CONSOLE_TYPED below);
      // consoleImg keeps the last ConsoleWords of them, wrapping.
      : (kind == DevConsole)
          ? '1
      : fromInteger(valueOf(DeviceWords));
    if (ioRefillIssued) begin
      // A CHAINED CONTROL WORD IS IN FLIGHT.  This arm is first in the
      // rule on purpose: the End Exception test below looks at devIdx
      // against the device's capacity, and devIdx has already been
      // advanced past the word that exhausted the old count, so that
      // test would fire spuriously while the refill is still pending.
      if (!st.responseReady()) begin
        noAction;
      end else begin
        Word64 ncwW <- st.readWordResp();
        ControlWord n = unpackControlWord(ncwW);
        ioRefillIssued <= False;
        // p.126: "Location 4 at this time should contain another
        // control word specifying the address at which the word
        // immediately following should be stored."  That address is
        // also where the CPU starts, so capture it now, before the
        // transfer walks it forward.
        if (iplActive) iplEntry <= n.dataAddr;
        ioDev.writeChanCW(x.ch, n);
        // p.123: "If the count field in the control word is zero
        // initially, it is interpreted as 2**18."  remaining is
        // Bit#(19) for exactly this.
        ioPending <= tagged Valid IoXfer {
          ch: x.ch, isWrite: x.isWrite,
          memAddr: n.dataAddr, devIdx: x.devIdx,
          remaining: (n.count == 0) ? 19'h40000 : zeroExtend(n.count),
          suppressEop: x.suppressEop, skip: (n.skip == 1),
          untilMark: x.untilMark, zeroFill: x.zeroFill };
      end
    end else if (x.devIdx >= capacity) begin
      // "the unit runs out of material" (p.121): End Exception, not
      // Unit Check -- the block ends early; whatever was already
      // moved stays moved, and the control word reflects exactly
      // that (dataAddr/count as of the last word actually
      // transferred, since this cycle transfers nothing).
      //
      // THE ARC ADDRESS REGISTER IS DELIBERATELY NOT TOUCHED HERE,
      // and this is a judgment rather than a quotation.  Reference
      // Manual printed p.161 says where the register is left after a
      // RELEASE ("at the address of the last arc used unless
      // transmission of that arc has been completed") and says
      // NOTHING about where it is left when a transfer runs off the
      // end of the volume -- which on a real 353 means an arc address
      // beyond 4095, a state the manual does not describe because the
      // twelve-bit field cannot hold one.  Leaving the register alone
      // is the behaviour that makes a following LOCATE the only way
      // to continue, which is what a program would have to do anyway.
      // What would settle it: a disk diagnostic deck, and
      // docs/disk_subsystem.md §6 records that none exists.
      //
      // ioDiskReqIssued needs no clearing on this path.  The arm sits
      // ABOVE the request arms, so the flag is False whenever a word
      // begins, and a word that reaches here has not been requested.
      ControlWord cw = ioDev.readChanCW(x.ch);
      // (Not for a WRITE TAPE MARK: its control word is the channel's
      // own and it moves no data, so there is no lead to add.)
      if (x.isWrite && !(kind == DevTape && x.zeroFill))
        cw.dataAddr = cw.dataAddr + writeEndLead;
      cw.ee = 1;
      if (!x.suppressEop) cw.eop = 1;
      cw.seop = 0;   // completion: see rl_io's other terminal arm
      ioDev.writeChanCW(x.ch, cw);
      ioPending <= tagged Invalid;
    end else if (!st.writeReady()) begin
      // The store queue is full: the exchange waits for the memory
      // bus before moving the next word (a RD-direction word is a
      // store; the W-direction path is also held so the two
      // directions keep the same per-word pacing).
      noAction;
    end else if (x.isWrite && !x.zeroFill && !ioReadIssued) begin
      // W-direction (memory->device), first visit to this word:
      // issue the read request and wait. ioPending/x are left
      // untouched (same devIdx/memAddr/remaining next call), so the
      // NEXT call's `x` still names this same word once the
      // response is ready.
      st.readWordReq(x.memAddr);
      ioReadIssued <= True;
    end else if (x.isWrite && !x.zeroFill && !st.responseReady()) begin
      // W-direction: the memory read is in flight; wait for it.
      noAction;
    end else if (kind == DevDisk && x.isWrite && !ioDev.diskCanWrite()) begin
      // W-direction disk: the source cannot take a word this clock
      // (an SDRAM or card back end; StretchDiskSource.bsv canWrite).
      // Wait with the word in hand rather than lose it: the memory
      // response stays in its register until the arm below collects
      // it.  The zero-fill tail waits the same way.
      noAction;
    end else if (kind == DevDisk && !x.isWrite && !ioDiskReqIssued) begin
      // RD-direction disk, first visit to this word.  Same two-arm
      // request/wait shape as the tape below, and for the same
      // reason: a real platter is not combinational and an SD-backed
      // source will be many clocks.
      //
      // NO SKIP ARM HERE.  Printed p.158: the disk "makes no use of
      // control word flag bits", and StretchExecute zeroes skip in
      // the control word the synchronizer adopts, so x.skip is always
      // False on a disk transfer.
      ioDev.diskReadReq(truncate(x.devIdx));
      ioDiskReqIssued <= True;
    end else if (kind == DevDisk && !x.isWrite && !ioDev.diskRespReady()) begin
      noAction;
    end else if (kind == DevTape && !x.isWrite && !x.skip
                 && !ioTapeReqIssued) begin
      // RD-direction tape, first visit to this word: ask the tape
      // source for it and wait.  As with the W-direction memory read
      // above, ioPending/x are left untouched, so the next call's `x`
      // still names this same word.
      //
      // Under SKIP no request is issued at all: p.107's flag
      // suppresses the core-storage write, and with nothing to store
      // there is nothing to fetch -- the position still advances
      // below, which is the part the manual does require.
      ioDev.tapeReadReq(truncate(x.devIdx));
      ioTapeReqIssued <= True;
    end else if (kind == DevTape && !x.isWrite && !x.skip
                 && !ioDev.tapeRespReady()) begin
      // RD-direction tape: the device read is in flight; wait for it.
      // A register-backed source makes this one clock.  An SD-backed
      // one will make it many, and the point of the arm is that
      // nothing above here has to care.
      noAction;
    end else begin
      // Either RD-direction (tape response now ready to collect, or a
      // reader/printer, which are still combinational) or W-direction
      // with the memory read response now ready to collect.
      // Set by the tape branch below when the word it just
      // collected IS a tape mark.  A LOCAL, not a register: a
      // register written here would not be readable until the next
      // clock, and the termination test twenty lines down has to see
      // it in THIS rule firing.
      Bool markJustRead = False;
      if (kind == DevDisk) begin
        DiskIndex di = truncate(x.devIdx); // safe: checked against
                                            // diskCapacity above
        if (x.isWrite) begin
          if (x.zeroFill) begin
            // THE TAIL OF A SHORT WRITE, printed p.160.  No core read
            // was issued for this word (the two W-direction arms
            // above skip themselves when zeroFill is set), so there
            // is no response to collect and nothing to collect it
            // from -- this phase writes zeros and advances, full stop.
            ioDev.writeDiskWord(di, 64'd0);
          end else begin
            Word64 v <- st.readWordResp();
            ioDev.writeDiskWord(di, v);
          end
        end else begin
          Word64 dv <- ioDev.diskReadResp();
          devStore(x.memAddr, dv);
        end
      end else if (kind == DevTape) begin
        TapeIndex ti = truncate(x.devIdx); // safe: confirmed < TapeWords above
        if (x.isWrite && x.zeroFill) begin
          // WRITE TAPE MARK (StretchExecute, CTL 117, printed p.132):
          // no core read was issued -- the W-direction arms above skip
          // themselves under zeroFill -- and the word written is the
          // mark SPACE FILE stops on.
          ioDev.writeTapeWord(ti, tapeMarkWord);
        end else if (x.isWrite) begin
          Word64 v <- st.readWordResp();
          ioDev.writeTapeWord(ti, v);
        end else if (!x.skip) begin
          Word64 tv <- ioDev.tapeReadResp();
          // A SPACE FILE READS AND DISCARDS.  It has to read -- that
          // is how it sees the mark -- but it is a CONTROL operation
          // and moves nothing into core.  SKIP suppresses the store
          // without issuing the read at all; this suppresses the
          // store while still issuing it, which is a different thing
          // and is why it is not spelled as SKIP.
          if (!x.untilMark) devStore(x.memAddr, tv);
          markJustRead = (tv == tapeMarkWord);
        end
        // Tape position PERSISTS across instructions (StretchIO.bsv
        // "TAPE POSITION"), unlike the reader/printer's devIdx which
        // is always instruction-local -- so unlike the reader/printer
        // branch below, tape also has to write its position back
        // every cycle, not just at the end of the transfer. Advances
        // even under SKIP: the manual says the flag only suppresses
        // the core-storage write, not the device's own motion.
        ioDev.setTapePos(truncate(x.devIdx + 1));
      end else begin
        DeviceIndex di = truncate(x.devIdx); // safe: confirmed < DeviceWords above
        if (x.isWrite) begin
          Word64 v <- st.readWordResp();
          // THE CONSOLE PRINTER AND THE PRINTER STAND-IN DIFFER IN
          // ONE THING: the console keeps its place across
          // instructions (StretchIO.bsv's consolePos), because a
          // console does not restart at the top of the page for each
          // message and MCP writes one message as a chain of control
          // words.
          if (kind == DevConsole) begin
            ioDev.writeConsoleWord(truncate(x.devIdx), v);
            ioDev.setConsolePos(truncate(x.devIdx + 1));
            $display("CONSOLE_TYPED %016h", v);
          end else
            ioDev.writePrinterWord(di, v);
        end else if (kind == DevConsole) begin
          // THE CONSOLE'S READ SIDE SCANS THE SWITCHES, and it had to
          // be its own arm: without this the `else` below served a
          // console READ out of the CARD READER's image and moved the
          // card reader's cursor, which was measured on 2026-10-22 as
          // the injection for this very change -- the control word
          // came back with a data word address of X LR IN + 3 and no
          // status bit at all.
          //
          // Reference Manual printed p.150: "A READ instruction
          // received by the console with the keyboard not enabled is
          // automatically terminated when the three words scanned
          // from the switches have been sent to the exchange."
          //
          // NOTHING ADVANCES.  They are SCANNED, so a second READ
          // gets the same three words; the bound is the capacity test
          // above, not a cursor.  SKIP is honoured the way every
          // other READ honours it (p.107: the flag suppresses the
          // core-storage write, not the device).
          if (!x.skip)
            devStore(x.memAddr, ioDev.consoleSwitchWord(truncate(x.devIdx)));
        end else begin
          if (!x.skip)
            devStore(x.memAddr, ioDev.readerWord(di));
          // THE CARD FEEDS whether or not the word was stored: SKIP
          // suppresses the core-storage write, not the device's own
          // motion, which is exactly the rule the tape branch above
          // already follows.  StretchIO.bsv "CARD FEED".
          ioDev.setReaderPos(truncate(x.devIdx + 1));
        end
      end
      // else: SKIP flag set on a READ (p.107) -- the device cursor
      // and memory address still advance below exactly as if the
      // word had been transferred, but core storage is left
      // untouched for this word.
      ioReadIssued <= False;
      ioTapeReqIssued <= False;
      ioDiskReqIssued <= False;
      Bit#(19) rem1 = x.remaining - 1;
      // ONE PAST THE WORD JUST MOVED, and its offset inside its arc.
      // Both are needed twice below -- to decide whether a short disk
      // WRITE still owes its arc a zero-filled tail (printed p.160)
      // and to park the arc address register where printed p.161 says
      // successive arcs leave it.
      Bit#(25) nxtIdx = x.devIdx + 1;
      Bit#(9)  arcOff = nxtIdx[8:0];
      ControlWord cw = ioDev.readChanCW(x.ch);
      // A SPACE FILE moves no data, so it leaves the control word's
      // data address and count alone; RD and W walk both forward.
      // SO DOES A ZERO FILL: the fill is not data, and a count that
      // included it would tell the program it had written more than
      // it asked to.
      if (!x.untilMark && !x.zeroFill) begin
        cw.dataAddr = x.memAddr + 1;
        cw.count = truncate(rem1);
      end
      if (x.untilMark && markJustRead) begin
        // SPACE FILE, p.132: "forward past a tape mark; EE and EOP
        // given".  The position is already one past the mark -- the
        // setTapePos above advances every cycle -- so all that is
        // left is the status the bootstrap tests.  MCP printed p.3
        // lines 45-47 wait for SEOP to clear, REQUIRE EE, and require
        // EPGK clear, then REL(SEOP) to clear EE and EOP again.
        //
        // EE ON A NORMAL COMPLETION is p.132's wording and MCP's own
        // control flow agreeing: "EE and EOP given" attaches End
        // Exception to the FUNCTION, and printed p.3 line 46's
        // BZBZ,X IPL BS+.21 branches to "ERROR IN SPACING" when EE is
        // ZERO.  MCP would not require an error condition to proceed.
        cw.ee = 1;
        if (!x.suppressEop) cw.eop = 1;
        cw.seop = 0;
        ioDev.writeChanCW(x.ch, cw);
        ioPending <= tagged Invalid;
      end else if (x.untilMark) begin
        // Not a mark: keep going, and do NOT let the count run out.
        ioPending <= tagged Valid IoXfer {
          ch: x.ch, isWrite: x.isWrite, memAddr: x.memAddr,
          devIdx: x.devIdx + 1, remaining: 19'h40000,
          suppressEop: x.suppressEop, skip: x.skip, untilMark: True,
          zeroFill: False };
      end else if (rem1 == 0 && kind == DevDisk && x.isWrite
                   && !x.zeroFill && arcOff != 0) begin
        // THE SHORT WRITE OWES ITS ARC A TAIL.  Reference Manual
        // printed p.160: "The data written need not be a multiple of
        // the number of words contained in an arc.  In this case,
        // however, the remainder of the last arc will be
        // automatically filled with zeros."
        //
        // The data phase is over -- its control word is written out
        // here, unchanged from here on -- and the transfer continues
        // in fill mode for the (512 - arcOff) words left in the arc.
        // Nothing is read from core during it and the control word is
        // not touched again, so a COPY CONTROL WORD afterwards shows
        // the data the program asked for and not the fill.
        cw.dataAddr = cw.dataAddr + writeEndLead;
        ioDev.writeChanCW(x.ch, cw);
        ioPending <= tagged Valid IoXfer {
          ch: x.ch, isWrite: True, memAddr: x.memAddr,
          devIdx: nxtIdx,
          remaining: 19'd512 - zeroExtend(arcOff),
          suppressEop: x.suppressEop, skip: False,
          untilMark: False, zeroFill: True };
      end else if (rem1 == 0 && cw.chain == 1
                   && !(kind == DevTape && x.zeroFill)) begin
        // (A WRITE TAPE MARK never chains: its control word is the
        // channel's own, not one it fetched, so its chain flag is
        // whatever the last transfer left there.)
        // FIGURE 36, printed p.109, row (multiple 0, chain 1, count
        // zero, end of block NO): "Chain and continue".  This model
        // has no record structure yet, so it never reports end of
        // block -- which is exactly the row IPL needs, and is why
        // chaining can be built before records (docs/NEXT.md 5k).
        // The row it gets wrong is (0,0,0,No), "Disconnect, then end
        // op.", where a real end of block would give "End operation":
        // a difference in whether a disconnect signal is sent, not in
        // whether the transfer completes.
        //
        // This is THE IPL BLOCKER.  RefMan printed p.126's fixed
        // control word is chain 1, count 1, refill 4: it reads one
        // word off the tape into location 4, and "since the fixed
        // control word is then exhausted, its refill address causes
        // the next control word to be fetched from location 4" --
        // which is the word just read, MCP's own CW(CR).  With chain
        // ignored the machine read that one word and stopped.
        st.readWordReq(zeroExtend(cw.refill));
        ioRefillIssued <= True;
        ioDev.writeChanCW(x.ch, cw);
        // ioPending stays valid so the refill arm above resumes; its
        // remaining/memAddr are placeholders, overwritten from the
        // new control word when it arrives.
        ioPending <= tagged Valid IoXfer {
          ch: x.ch, isWrite: x.isWrite, memAddr: x.memAddr + 1,
          devIdx: x.devIdx + 1, remaining: 0,
          suppressEop: x.suppressEop, skip: x.skip,
          untilMark: x.untilMark, zeroFill: x.zeroFill };
      end else if (rem1 == 0) begin
        if (!x.suppressEop) cw.eop = 1;
        if (x.isWrite && !x.zeroFill) cw.dataAddr = cw.dataAddr + writeEndLead;
        // THE ARC ADDRESS REGISTER, printed p.161: "Associated with
        // each disk is an arc address register.  As successive arcs
        // are used, this register is increased by one for each arc."
        // Parking it at nxtIdx >> 9 gives both halves of that in one
        // expression: an arc that was completed leaves the register
        // on the NEXT arc, and an arc only partly used leaves it on
        // ITSELF -- which is also what p.161's RELEASE rule describes
        // ("left at the address of the last arc used unless
        // transmission of that arc has been completed").  After a
        // zero-filled WRITE the index is arc-aligned by construction,
        // so a short write still advances a whole arc, which is what
        // "the remainder of the last arc will be automatically filled"
        // means for the arc after it.
        if (kind == DevDisk) ioDev.setArcAddr(truncate(nxtIdx >> 9));
        // THE SEOP STATUS BIT IS CLEARED AT COMPLETION, and this half
        // of the rule is NOT a quotation.  Reference Manual p.121 was
        // read whole: it says the bit is set when an SEOP instruction
        // is given, and says nothing about clearing it.  What settles
        // it is that IBM's own code cannot work otherwise.  MCP's
        // bootstrap, printed p.3 line 45, prints
        //     000076.00  000041.30 80  000074.34 02
        //                              BB,X IPL BS+.24,X 8 1
        // which this assembler reproduces bit-for-bit, so the
        // instruction is BB -- branch when the bit is ONE
        // (strap/opcodes.py BB_CODES) -- and its target is the CCW two
        // rows above.  The loop therefore spins while bit 24 is set.
        // Without a clear it never terminates.  ka_ul1's tape-write
        // routine is a second, independent witness.  Usage-based
        // evidence, recorded as such in docs/NEXT.md 5o.
        cw.seop = 0;
        ioDev.writeChanCW(x.ch, cw);
        ioPending <= tagged Invalid;
        // ---- the initial-start signal, p.126 steps 4 and 5 --------
        // "the exchange sends an initial start signal to the
        // computer... The computer, upon receipt of the initial-start
        // signal, fetches and executes the instruction in the location
        // specified by the data word address field of the control word
        // in core storage location 4."
        //
        // A DOCUMENTED DEPARTURE.  p.126 continues: "The address of
        // this instruction, however, is NOT placed in the instruction
        // counter."  This sets the PC to it anyway.  The difference is
        // unobservable for any legal IPL program, because the same
        // page requires that "the first instruction of a program
        // loaded by means of the initial program loading technique
        // must be BRANCH DISABLED" -- a BD replaces the instruction
        // counter itself, so what the PC held beforehand cannot
        // matter.  MCP's bootstrap obeys this: printed p.2 line 24 is
        // "X IPL BS  BD,X BEGIN  -DISABLE AND START IPL".  Modelling
        // the true rule needs the EX subject-swap in mkEBox.resume()
        // and buys nothing until a program breaks the requirement.
        if (iplActive) begin
          pcReg     <= {iplEntry, 1'b0};
          iplActive <= False;
        end
      end else begin
        ioDev.writeChanCW(x.ch, cw);
        ioPending <= tagged Valid IoXfer {
          ch: x.ch, isWrite: x.isWrite, memAddr: x.memAddr + 1,
          devIdx: x.devIdx + 1, remaining: rem1,
          suppressEop: x.suppressEop, skip: x.skip,
          untilMark: x.untilMark, zeroFill: x.zeroFill };
      end
    end
    eArm.send;
    haltedReg <= False;
  endrule

  rule rl_xmit (running && armXmit);
    // Service one word of an in-flight multi-word TRANSMIT.  This is
    // rl_io's shape with the device taken out: a storage read, then a
    // storage write of what came back, one word per clock, because
    // this model writes storage once per rule.
    //
    // THE SPEC IS Reference Manual printed p.30 and the whole of it
    // fits in this rule.  "In forward transmission, the sending and
    // receiving addresses of each successive word transmitted are
    // obtained by incrementing the previous addresses by one."  There
    // is no count to write back and no indicator to fold -- same
    // page: "The count field in the index register is not changed as
    // a result of the operation, and the index result indicators are
    // not affected."  The first word was moved by the Transmit arm in
    // StretchExecute; this drains the rest.
    //
    // PROTECTION IS CHECKED PER WORD, which is the one place this
    // rule does more than copy.  p.30 says an invalid or protected
    // address is "not detected... until the data transmission
    // actually encounters" it, so a transmit that walks into a
    // protected word must stop THERE, with the words before it moved
    // -- not be refused up front.  protViolates is the same test the
    // single-word arm uses; DS terminates the operation (p.32,
    // "storing in core storage is always suppressed, AND THE
    // OPERATION IS ALWAYS TERMINATED").
    //
    // ADDRESS INVALID IS CHECKED PER WORD TOO, and it is not optional
    // -- it is the only thing that bounds a runaway transmit.  p.30,
    // on a direct count field of zero: "A count field of zero is
    // interpreted as 2^18.  Since this many words cannot be
    // transmitted without encountering an invalid address, such a
    // count is never valid.  IT IS NOT DETECTED, HOWEVER, UNTIL THE
    // DATA TRANSMISSION ACTUALLY ENCOUNTERS AN INVALID OR PROTECTED
    // ADDRESS."  So the manual's own answer to "what stops a 2^18
    // transmit" is this check, and a model without it does not merely
    // miss an indicator: 2^18 words is the WHOLE 18-bit address
    // space, so the copy wraps and zeroes every word of core.  That
    // is exactly what happened the first time this rule ran against
    // MCP, whose tape carries no PROSA, so the dictionary it reads
    // the count out of is zeros.
    //
    // `installed` is StretchMemory's bound, the same one the Z arm
    // uses for AD (RefMan printed p.21: "an effective word address...
    // which does not correspond to a core storage location that is
    // physically available").  Both ends are tested: a transmit can
    // run off the top reading as easily as writing.
    let x = validValue(xmitPending);
    // THE NEXT PAIR, written once here because three places want it.
    // p.30: forward obtains each successive pair of addresses "by
    // incrementing the previous addresses by one", backward "by
    // decrementing".
    XmitXfer nextWord = XmitXfer {
      src: x.backward ? x.src - 1 : x.src + 1,
      dst: x.backward ? x.dst - 1 : x.dst + 1,
      remaining: x.remaining - 1, backward: x.backward, swap: x.swap };
    // ONE WRITE, AT THE END OF THE RULE.  Bluespec refuses two
    // Reg writes it cannot order ("methods that conflict in
    // parallel"), so the count is carried in a variable and stored
    // once below.
    Bit#(32) swapClk = xmitSwapClocks + (x.swap ? 1 : 0);
    if (!st.writeReady()) begin
      // The store queue is full: wait for the memory bus, the same
      // way rl_io does.
      noAction;
    end else if (x.swap && xmitSwapPhase == 2) begin
      // PHASE 2: no read.  The receiving word's OLD contents, held
      // since phase 1, go back into the sending word -- the second
      // half of p.30's exchange.  Both ends were checked in phase 0.
      st.writeWord(x.src, xmitSwapHeld);
      xmitSwapPhase <= 0;
      if (x.remaining == 1) begin
        $display("StretchCore: SWAP finished, %0d clocks in rl_xmit",
                 swapClk);
        swapClk = 0;
        xmitPending <= tagged Invalid;
      end else
        xmitPending <= tagged Valid nextWord;
    end else if (!xmitReadIssued) begin
      // PHASE 0 reads the SENDING word, phase 1 the RECEIVING one.
      st.readWordReq((x.swap && xmitSwapPhase == 1) ? x.dst : x.src);
      xmitReadIssued <= True;
    end else if (!st.responseReady()) begin
      noAction;
    end else begin
      Word64 v <- st.readWordResp();
      xmitReadIssued <= False;
      // >>> A SWAP WRITES BOTH ENDS, so BOTH are protection-checked,
      // and both are checked in phase 0 -- before anything has been
      // written for this word -- so a refused pair leaves the words
      // before it moved and this one untouched.  p.30 on an invalid
      // or protected address: it is "not detected... until the data
      // transmission actually encounters" it.
      Bool protBad = protViolates(st, x.dst)
                     || (x.swap && protViolates(st, x.src));
      if (!installed(x.src) || !installed(x.dst)) begin
        st.setIndicatorBits(setBit(st.readIndicators(), ind_AD, 1));
        xmitPending <= tagged Invalid;
        xmitSwapPhase <= 0;
      end else if (protBad) begin
        st.setIndicatorBits(setBit(st.readIndicators(), ind_DS, 1));
        xmitPending <= tagged Invalid;
        xmitSwapPhase <= 0;
      end else if (x.swap && xmitSwapPhase == 0) begin
        // PHASE 0: the sending word is in hand and NOTHING is written
        // yet.  p.30's "at the same time" is this: the receiving word
        // must still be readable when phase 1 asks for it.
        xmitSwapHeld <= v;
        xmitSwapPhase <= 1;
      end else if (x.swap) begin
        // PHASE 1: `v` is the RECEIVING word.  Write the sending
        // word's value into it and keep `v` for phase 2.
        st.writeWord(x.dst, xmitSwapHeld);
        xmitSwapHeld <= v;
        xmitSwapPhase <= 2;
      end else begin
        st.writeWord(x.dst, v);
        xmitPending <= (x.remaining == 1) ? tagged Invalid
                                          : tagged Valid nextWord;
      end
    end
    xmitSwapClocks <= swapClk;
    eArm.send;
    haltedReg <= False;
  endrule

  rule rl_tail_write (running && armTail);
    // The second word of a crossing VFL store whose second word is a
    // special or index register (ExecDone.tailWrite): the one-clock
    // stall core storage's tail gets (writeWordTail), through writeWord
    // so that the register's own store rules apply.
    let t = validValue(pendingTailWrite);
    st.writeWord(tpl_1(t), tpl_2(t));
    pendingTailWrite <= tagged Invalid;
    eArm.send;
    haltedReg <= False;
  endrule

  rule rl_idx_write (running && armIdx);
    // Part 2 of a progressive-indexing instruction: nothing was
    // fetched this call, and PC already advanced on part 1.
    let p = validValue(pendingIdxWrite);
    st.writeIndex(tpl_1(p), tpl_2(p));
    pendingIdxWrite <= tagged Invalid;
    eArm.send;
    ibusy <= ib;   // the I-box's clock runs on (see `ib`)
    haltedReg <= False;
  endrule

  rule rl_exec_resume (running && armResume);
    // The E-box's held instruction gets its operand word: let the box
    // collect it and re-run (it may bail again for a second word);
    // on completion, retire the level or advance the instruction
    // counter according to who dispatched it.
    let ep = ebox.pending();
    HWordAddr pc       = tpl_1(ep);
    InstrLen len        = tpl_2(ep);
    DecodedInstr di     = tpl_3(ep);
    Bool fromLA = ebox.busyFor(OwnerLA);
    Bit#(16) ebn = 0;   // (was the countdown, always 0 here: see eArm's note)
    Bool done = False;
    // Clocks this instruction has spent in the divide box (0 for every
    // instruction that did not use it), read BEFORE resume() clears the
    // wait.  See the charge below.
    Bit#(16) boxK = ebox.boxClocks();
    // ... and the data-dependent part of a floating-point divide's
    // time, which only the box knows (mkEBox.boxCharge; 0 for every
    // other instruction).  Added to the budget on both paths below.
    Bit#(16) boxX = ebox.boxCharge();
    // ... and, for a STEPPED add (fidelity_plan.md A3 (b), 2026-11-25),
    // the serial unit's own clocks: Valid only then.  See the charge.
    Maybe#(Bit#(16)) sauOwn = ebox.boxOwnClocks();
    Bool charged = False;     // a look-ahead level completed: ebn is its charge
    Bool chargeFp = False;
    resumeYielded <= False;
    let r <- ebox.resume();
    if (r matches tagged Valid .o) begin
      pendingIdxWrite <= o.idxWrite;
      pendingTailWrite <= o.tailWrite;
      ioPending <= o.ioStart;
      xmitPending <= o.xmitStart;
      if (o.xmitStart matches tagged Valid .xs &&& xs.swap)
        $display("StretchCore: SWAP started at half-word %0d, %0d words", pc, xs.remaining);
      if (fromLA) begin
        // A look-ahead level's instruction finished: retire it.
        // Timed off the level's instruction AS DECODED, as rl_au_remove
        // times it: the box holds the carried one, whose length the
        // second index may have changed.
        //
        // THE DIVIDE BOX'S CLOCKS COME OFF THE BUDGET, 2026-11-15, so
        // that moving the divide out of execute() into an iterative
        // box keeps the E-box's time.  (Not every instruction's time:
        // while the box runs, the held level stops I-box instructions
        // that used to overlap the countdown.  Measured on eight FP
        // decks, +1 to +16 clocks; StretchPAU.bsv's header has the
        // table.)  The budget is
        // charged from completion; a divide used to complete in the
        // clock it started and now completes `boxK` clocks later
        // (mkDivBox: 4), so charging the whole budget again would
        // lengthen every divide by that much.  Whether the box's own
        // count should REPLACE the table is a later, sourced step.
        //
        // IF THE BOX EVER TAKES LONGER THAN THE BUDGET the difference
        // cannot be absorbed and the instruction really is longer;
        // that is reported, not hidden.  It can only happen when this
        // rule lost clocks to rl_recover, rl_io or rl_idx_write while
        // the result waited.  The VFL divide's budget (66 clocks up)
        // dwarfs the box's 4; a floating-point divide's budget is
        // 5 + fpExtra = Table 2's fixed terms + 2 per reduction loop,
        // and the box walks ONE loop a clock, so the budget is always
        // more than twice the box's clocks (2026-11-17).
        //
        // The OTHER branch needs no such term: an I-box-dispatched
        // instruction is charged `budget - elapsed` from its own start
        // clock, which already contains the box's time.
        //
        // >>> EXCEPT WHERE THE SERIAL UNIT OWNS ITS TIME (fidelity_plan.md
        // A3 (b), 2026-11-25). <<<  A stepped add (L, LWF decimal; +, +MG
        // both radices) has spent the unit's passes, 2 clocks each with
        // Table 3's z and recomplement (mkSAU), in the box.  That IS the
        // row's byte term, so the row is charged without it
        // (sauRowWithUnit, the row with the unit's own clocks in place of
        // the term it steps, less those clocks) and NOTHING is taken off:
        // what is left of the row -- its fixed part -- runs from the
        // answer, as the termination does on the machine.  Since step 2
        // the decimal M+ family is stepped too (and, as they follow, the
        // K family and SRD's round).  The unit's time is not bounded by
        // the row, so there is no overrun to report.
        DecodedInstr hdi = la.headLevel().di;
        Bit#(16) ebudget = eboxClocks(hdi) + boxX;
        if (sauOwn matches tagged Valid .u)
        begin
          Bit#(16) rw = sauRowWithUnit(hdi, u);
          ebn = (rw > u) ? rw - u : 0;
        end
        else begin
          if (boxK > ebudget)
            $display("StretchCore: A BOX OVERRAN THE E-BOX BUDGET at half-word %0d: %0d clocks against %0d",
                     pc, boxK, ebudget);
          ebn = (boxK >= ebudget) ? 0 : ebudget - boxK;
        end
        laarRetire(la.headLevel(), ebn);
        noteRetired(la.headLevel(), o);
        la.retireHead();
        charged = True;
        chargeFp = isFpInstr(hdi);
      end else begin
        commitNext(pc, len, o.next);
        // An I-box store that read its word first (SV, SC, SR, SVA, SIC)
        // completes here: held in a store level, or counted as made.
        if (iboxStoreWord(di) matches tagged Valid .w) begin
          if (storeNeedsLevel) holdStoreInLevel(pc, len, di, w);
          else storeSeq <= storeSeq + 1;
        end
        Bool taken = (o.next != pc + ((len == Full) ? 2 : 1));
        Bit#(32) elapsed = clk - startClk;
        // A stepped add's unit time replaces the row's byte term here as
        // well (the note on the other branch); `elapsed` already holds it.
        Bit#(16) budget = budgetClocks(di, taken) + boxX;
        if (sauOwn matches tagged Valid .u)
          budget = budgetClocks(di, taken) - eboxClocks(di) + sauRowWithUnit(di, u);
        ibusy <= (elapsed >= zeroExtend(budget)) ? 0 : budget - truncate(elapsed);
        done = isHalt(di, o.next, pc);
      end
    end
    if (charged) ebox.terminate(chargeFp, ebn);
    eArm.send;
    if (fromLA) begin
      ibusy <= ib;   // a level's read: the I-box's clock runs on (see `ib`)
      eboxDoneAt <= clk + zeroExtend(ebn) + 1;
    end
    haltedReg <= done;
  endrule

  rule rl_au_remove (running && armRemove);
    // Remove the head level into the arithmetic unit: its operand
    // (if any) is present, so the E-box runs with it pre-supplied;
    // any further read it needs, the box holds it for (resume arm).
    Bit#(16) ebn = 0;   // (was the countdown, always 0 here: see eArm's note)
    Bool charged = False;
    LaLevel h = la.headLevel();
    Vector#(NPrefetch, Word64) pf = replicate(0);
    Bit#(2) cnt = 0;
    if (h.data matches tagged Valid .d) begin pf[0] = d; cnt = 1; end
    // THE INSTRUCTION AS THE LEVEL CARRIES IT: the indexing the I-box
    // did when the level was loaded, not a second indexing against the
    // registers as they are now (LaCarry, StretchTypes; Buchholz §15.3).
    // A branch level is not an E-box class and comes back unchanged.
    DecodedInstr xdi = carriedInstr(h.di, h.carry);
    let r <- ebox.start(h.pc, h.len, xdi, pf, cnt, OwnerLA, tagged Invalid);
    if (h.branch) begin
      // The guessed branch, now with final indicators (a branch never
      // waits on an operand, so the result is here).
      let o = validValue(r);
      Bool taken = (o.next != h.pc + ((h.len == Full) ? 2 : 1));
      guessPending <= False;
      if (taken) begin
        // Wrong guess: cancel every younger level, recover next clock.
        // THE TARGET IS THE ONE COMPUTED AT THE GUESS, not o.next: the
        // E-box has just recomputed the address from the index registers
        // as they are now, and the instruction unit may have changed them
        // running ahead (MCP printed p.362 lines 41-42, "BAE,JTABL(JX1)"
        // then "CBH,JX1,ZLOOK4"; decks/la_guess_target_index.strap).
        // `taken` above is still read off that recomputed address, so a
        // recomputed address equal to the fall-through would read as not
        // taken.  No program is known to do that.
        la.cancelAll();
        recover <= tagged Valid h.target;
        recoverSlot <= la.head();
      end else
        la.retireHead();
      ebn = 2 * 6;   // Blosk fig.10: decode + five execution cycles
      charged = True;
    end else if (r matches tagged Valid .o) begin
      pendingIdxWrite <= o.idxWrite;
      pendingTailWrite <= o.tailWrite;
      ioPending <= o.ioStart;
      xmitPending <= o.xmitStart;
      if (o.xmitStart matches tagged Valid .xs &&& xs.swap)
        $display("StretchCore: SWAP started at half-word %0d, %0d words", h.pc, xs.remaining);
      ebn = eboxClocks(h.di);
      charged = True;
      laarRetire(h, ebn);
      noteRetired(h, o);
      la.retireHead();
    end
    // else: the E-box holds the level's instruction for its operand read.
    if (charged) ebox.terminate(!h.branch && isFpInstr(h.di), ebn);
    eArm.send;
    eboxDoneAt <= clk + zeroExtend(ebn) + 1;
    ibusy <= ib;   // the I-box's clock runs on (see `ib`)
    haltedReg <= False;
  endrule

  // Take the interruption.  Which indicator and which address were
  // decided in StretchStorage's intDueCalc (leftmost masked indicator;
  // EIA = interruption address + N, in WORDS, p.48); what is left here
  // is the part that belongs to the instruction unit -- turn that
  // indicator off, point the fetch stream at the routine, and stop the
  // instruction counter.
  // THE EXCHANGE'S STATUS REPORT, Reference Manual printed p.118, read in
  // the ink: "When an operation concerning an external unit has been
  // terminated and at least one of these five status bits in the control
  // word is on, the exchange attempts to set up the corresponding
  // indicator or indicators and thus cause an interruption of the
  // program.  All of the status indicators for a particular channel are
  // set up as a group at one time.  At the same time, the address of the
  // channel causing the interruption is entered into the channel address
  // register."  StretchStorage.ioReportReady is the page's two
  // conditions; this rule is the scanner.
  //
  // MCP NEEDS IT.  Its disk request (printed p.159 lines 41-46) marks
  // channel 0 operating and issues LOCATE; only the receptor, K GATE
  // (printed p.123 line 6), clears the mark, and only an EOP
  // interruption reaches K GATE.  Without this rule MCP retried the
  // request 16,255 times (docs/boot_plan.md).
  //
  // ONE CHANNEL PER CLOCK, ascending and wrapping -- p.118: "subsequent
  // priorities are assigned in the order of ascending channel addresses,
  // looping around to the lowest address once the highest address of the
  // installation is reached".  The installation is the five channels
  // StretchIO has.  NOT MODELLED: "when an input-output instruction is
  // issued, the scanner is set to the channel to which the instruction
  // is addressed" -- it orders reports only when two channels wait at
  // once -- and p.119's few-cycle delay behind data transfers.
  //
  // NOT WHILE AN INTERRUPTION IS BEING ENTERED.  rl_interrupt turns the
  // indicator off a clock before the table word runs, and MCP's table
  // word is SIC / BD (printed p.110 lines 25-34), so for that clock and
  // the next the indicators are clear and the system still enabled.
  // p.118's condition 2 exists "to prevent the destruction of the
  // contents of the channel address register ... before the subroutine
  // ... has had time to interrogate the channel address register"; the
  // hardware meets it by the table word disabling before anything else
  // runs, and this guard is that.
  rule rl_io_report (st.ioReportReady() && !isValid(intPC) && !armInterrupt);
    WordAddr ch = case (ioScan)
                    0: chanDisk;
                    1: chanReader;
                    2: chanPrinter;
                    3: chanTape;
                    default: chanConsole;
                  endcase;
    ControlWord cw = ioDev.readChanCW(ch);
    Bit#(5) s = {cw.epgk, cw.uk, cw.ee, cw.eop, cw.cs};
    // "has been terminated": a transfer still under way reports later,
    // at its own end (p.118: the indicators "can be turned on ... only
    // after termination of the current operation").
    Bool inFlight = case (ioPending) matches
                      tagged Valid .x: (x.ch == ch);
                      default: False;
                    endcase;
    if (s != 0 && !inFlight) begin
      ioDev.clearStatus(ch);
      st.ioStatus(tagged Valid tuple2(s, truncate(ch)));
      $display("StretchCore: I/O status report, channel %0d, EPGK UK EE EOP CS = %b", ch, s);
    end else begin
      st.ioStatus(tagged Invalid);   // p.119: ready, so CA reads zero
      ioScan <= (ioScan == 4) ? 0 : ioScan + 1;
    end
  endrule

  rule rl_interrupt (running && armInterrupt);
    let {n, eia} = validValue(intDue);

    // "After this leftmost indicator has been turned off" -- and only
    // that one: the rest of the masked set stays on and interrupts
    // again, in priority order, before the instruction counter's own
    // next instruction runs (p.48's programming note).
    st.setIndicatorBits(setBit(st.readIndicators(), n, 0));

    HWordAddr epc = {eia, 1'b0};
    intPC <= tagged Valid epc;
    // The instruction stream jumps, so the Y buffers must refill from
    // the new address.  That is what branchSeq does for a taken branch
    // (rl_ic_controls turns a change into `restart`), and an
    // interruption is the same discontinuity: nothing else in this
    // model reaches forward to fetch an address of its own.
    branchSeq <= branchSeq + 1;
    xholdPc <= tagged Invalid;    // see xholdPc: nothing left for another instruction
    serialPc <= tagged Invalid;

    // p.48: the fetch of THIS instruction cannot turn on IF "even
    // though it might lie in the protected area of core storage".
    // Nothing to do here -- IF is not implemented at all (see
    // StretchExecute's protViolates) -- but when it is, this is the
    // fetch that must be exempt.

    // The charged time of the instruction just removed from a level
    // keeps draining across this clock, exactly as it does in every
    // other arm: taking the interruption early (see armInterrupt above)
    // must not also stop the clock the E-box was charged.  Before that
    // change this rule could not fire while the E-box countdown non-zero, so it never
    // had to decrement it.
    //
    // NOTHING IN THE SUITE TESTS THIS LINE, and that is said here
    // rather than left to be discovered.  No injection removes it, and
    // none could be caught: the three CYCLES<= benchmarks never enable
    // the interruption system, and every test that does interrupt
    // checks a halt address rather than a clock count.
    eArm.send;
  endrule

  rule rl_prepare (running && armPrepare);
    // Preparation: transfer the next instruction from the Y buffers
    // (both halves of a full-word instruction, which may straddle
    // 1Y/2Y); an E-box-class instruction is loaded into a look-ahead
    // level, an I-box-class one executes here once the levels have
    // drained. Stall until the word(s) are buffered and checked.
    Vector#(4, LaLevel) nl = prepNl;
    Bool done = False;
    // The instruction being prepared and the tests on it below were
    // computed in this rule until 2026-11-19; they are module-level now
    // (prepPc ... prepInstrStored, above armPrepare) so that a box's
    // resume can ask whether this rule would start an I-box instruction
    // (yieldToPrepare).  The same expressions, read in the same clock.
    HWordAddr pc = prepPc;
    Maybe#(Tuple2#(InstrLen, DecodedInstr)) prepared = prepPrepared;
    Bool progressivePending = prepProgressivePending;
    Bool instrStored = prepInstrStored;
    if (yieldToPrepare) resumeYielded <= True;
    if (ebox.busyFor(OwnerIbox))
      noAction;             // an I-box instruction is waiting on its operand read
    else if (ibusy != 0)
      ibusy <= ib;          // previous instruction's time budget still running
    else if (isValid(intDue) && !isValid(intPC))
      // >>> AN INTERRUPTION IS DUE: START NOTHING NEW, 2026-11-18. <<<
      // Ref. Manual p.48: interruption comes "AT THE END OF THE OPERATION
      // DURING WHICH THE INDICATOR IS TURNED ON" and "before execution of
      // the next instruction".  rl_interrupt waits for the levels to
      // drain (armInterrupt); until now rl_prepare went on starting
      // instructions while they drained, and an I-box instruction so
      // started was committed for good (since 2026-11-20 rl_int_recover
      // undoes what ran ahead of the level that raised it, but nothing
      // started after the interruption is due is ever undone).  The 7030 undoes such an instruction's index
      // change from its IX Rec. level (Perf. Char. Vol. 1 Table A-2, PDF
      // 69-71, the LX row's "IX Rec." level, docs/spec_lookahead.md 1.7;
      // App. A, PDF 63: "Recovery information is shipped back to the
      // I-box"; printed page numbers not checked).  Not starting it has the same
      // architectural effect.  FOUND 2026-11-18: the VFL internal-operand
      // wait (intWait) held C22-6578 Problem 2.12's "CM1111(BU,1),
      // $SB+0.7" four clocks, long enough for "LX, $2, 19.0" behind it to
      // run before the $VF interruption its LWF had raised, and ENDCYC
      // then stored through the new $2 (16 of the hundred transposed words wrong).
      // Levels ALREADY loaded still execute, as before -- unless the
      // interruption was raised by the level that just completed, when
      // rl_int_recover cancels them first.
      noAction;
    else if (!st.writeReady())
      noAction;   // a storing instruction could find the queue full: wait
    else if (storeWait(nl) || clk < xstoreFreeAt)
      // STORE WAIT (R23-9732 Figs 3.1.13, 3.1.20, 3.1.24; StretchIBox's
      // storeWait): a pending level stores into an index register, the
      // indicators or the mask, and nothing is prepared until it has.
      // (xholdPc: only the index-storage hold of printed p.3-21.)
      begin
        Bool xs = clk < xstoreFreeAt;
        for (Integer k = 0; k < 4; k = k + 1) begin
          if (nl[k].valid &&& nl[k].storeAddr matches tagged Valid .sa &&& indexStorageWord(sa)) xs = True;
          if (nl[k].valid &&& nl[k].storeAddr2 matches tagged Valid .sb &&& indexStorageWord(sb)) xs = True;
        end
        if (xs) xholdPc <= tagged Valid pc;
      end
    else if (redecodeAfterHold &&& prepared matches tagged Valid {.rlen, .rdi}) begin
      // The decode p.3-21 says waits for the index store (the note at
      // redecodeAfterHold): this clock is its first, as at a load.  Only
      // for an E-box-class instruction: an I-box instruction's budget
      // (budgetClocks, charged from its dispatch) already serializes its
      // own decode, so its dispatch at the hold's end IS its decode's
      // start, and charging the decode here would count it twice.
      // (Merged with batch26's xholdPc, 2026-11-18: an FP indexed operand
      // from index storage held behind a VFL store into index storage
      // would take both this decode and fpHoldSerialClocks.  No deck or
      // atlas row reaches that combination; stated, not measured.)
      if (isEboxClass(rdi))
        ibusy <= 2 * iboxCycles(rdi, False) - 1;
      redecodeAfterHold <= False;
    end
    else if (instrStored)
      noAction;   // a pending level stores into this instruction (above)
    else if (prepared matches tagged Valid {.len, .di}
             &&& isEboxClass(di) &&& isValid(intPC)) begin
      // NOT IMPLEMENTED, and loud about it.  An interruption
      // instruction that is E-box class would have to be loaded into a
      // look-ahead level, and a level steps the instruction counter --
      // the one thing p.48 forbids here.  Real interruption tables hold
      // branches and SIC (p.48-49: "a subroutine entered by STORE-
      // INSTRUCTION-COUNTER-IF-BRANCH-DISABLED and returned by BRANCH
      // ENABLED"), all I-box class, so this is a bound on the model
      // rather than on the machine.  Treated as a fall-through so the
      // program keeps running and its own check fails, instead of
      // silently stepping the counter.
      $display("StretchCore: interruption instruction at %0d is E-box class -- not implemented", pc);
      commitNext(pc, len, pc + ((len == Full) ? 2 : 1));
    end
    else if (prepared matches tagged Valid {.len, .di} &&& isEboxClass(di)) begin
      if (la.count() < 4 && !progressivePending) begin
        // ONE derivation of this instruction's addresses, used for both
        // the operand read below and the level's storeAddr further
        // down -- see StretchIBox's prepareExec.
        //
        // AND IT IS DERIVED FROM THE INSTRUCTION AS THE LEVEL WILL
        // CARRY IT, 2026-11-15: the index registers are read here, once
        // (carryIndex), and the E-box is later handed this same
        // instruction with its index fields cleared (rl_au_remove), so
        // `da`, `storeAddr` and the address executed at are one
        // derivation.  See LaCarry in StretchTypes.
        LaCarry carry = carryIndex(st, di);
        let prep = prepareExec(st, carriedInstr(di, carry));
        Maybe#(WordAddr) da = tagged Invalid;
        if (fetchesOperand(di) && !prep.completesWithoutFetch)
          da = prep.operandAddr;
        // THE ONE LAAR (StretchIBox's laarInternal note): a level that
        // stores, or fetches an internal register, is not loaded while
        // another holds it or its last store is not yet accepted.
        Bool laarBusy = laarHeldByLevel(nl) || clk < laarFreeAt || st.storesPending();
        Bit#(16) serialNow = (xholdPc == tagged Valid pc) ? fpHoldSerialClocks(di, da) : 0;
        if (isFpInstr(di) && !lftDeferredLaar(di, da)
            && needsLaar(fpLaarStore(di, prep.storeAddr), da) && laarBusy)
          noAction;
        else if (serialNow != 0) begin
          // Out of the index-store hold: the indexed I-box operand's reads
          // first (xholdPc above), then the load.
          ibusy <= serialNow - 1;
          serialPaid <= serialNow;
          serialPc <= tagged Valid pc;
          xholdPc <= tagged Invalid;
        end
        else
        // >>> THE PROBE IS GONE, 2026-10-29. <<<  This used to call
        // `ebox.exec` with no operands so that `execute()` would bail
        // out with the address it wanted, and then treat a non-bail as
        // "classified as fetching but completed" and commit the
        // instruction inline.  Execution was therefore both a
        // supposedly side-effect-free query and the operation that
        // commits architectural effects, and every arm had to do no
        // irreversible work before noticing an operand was missing --
        // a contract no type enforced.
        //
        // Both of the probe's answers are now pure, and both were
        // PROVEN against it across the whole corpus before it was
        // removed (docs/ebox_roadmap.md):
        //
        //   the ADDRESS      -- `prep.operandAddr`, not one
        //                       disagreement in 5621 checks;
        //   "ALREADY DONE"   -- `prep.completesWithoutFetch`, zero
        //                       disagreements in 5621 checks, with its
        //                       six causes enumerated by measurement:
        //                       the decimal refusal, progressive with
        //                       index 0, M+/CM crossing a word
        //                       boundary, DF suppression, and AD.
        //
        // An instruction that will finish without reading now simply
        // gets a level with NO operand address, exactly like ST and
        // every other non-fetching E-box instruction, and is dispatched
        // through `ebox.start()` in the ordinary way.  The inline
        // completion path and its "classification mismatch" message are
        // gone with it -- there is no longer a classification to
        // mismatch.
        begin
          // Store-close-to-fetch (plan stage 3a note): if this level
          // fetches word `a`, wait for the NEWEST earlier level that
          // stores to `a` -- every current level is program-earlier
          // than this new one (the tail), and they retire head-first, so
          // waiting for the newest such store covers all older ones.
          //
          // The same wait covers a fetch of one of the E-BOX's OWN
          // registers -- words 7-15, the zeros/ones counts, the
          // accumulator and its sign byte, the indicators, mask,
          // remainder and factor. storeTarget() reports only stores to
          // storage, deliberately: an FP load or add writes the
          // accumulator, not memory. But a VFL or connective
          // instruction may ADDRESS those words, and then the value it
          // wants is one an unretired earlier level is still going to
          // write. There is no address to compare against, so any
          // level fetching 7-15 waits for the newest earlier level,
          // whatever that level does -- the E-box on the real machine
          // is one unit and cannot hand out its accumulator ahead of
          // the operation still in it. Found by jb_af1c F207C1:
          // DL(U),FPK1 immediately followed by CT0011(BU,3),10.5,
          // which read the sign byte as it was BEFORE the load zeroed
          // its flag bits; three half-words of separation and the same
          // pair passes.
          Maybe#(Bit#(2)) wf = tagged Invalid;
          if (da matches tagged Valid .a) begin
            Bool wfound = False;
            for (Integer i = 0; i < 4; i = i + 1) begin
              Bit#(2) pos = la.tail() - 1 - fromInteger(i);
              Bool hz = nl[pos].valid
                        && (levelStores(nl[pos], a)
                            || eboxRegister(a));
              if (!wfound && hz) begin wf = tagged Valid pos; wfound = True; end
            end
          end
          la.load(LaLevel{valid: True, kind: Whole, di: di, pc: pc, len: len, da: da,
                          data: tagged Invalid, fetchIssued: False, waitFor: wf,
                          branch: False, target: 0, storeAddr: prep.storeAddr,
                          storeAddr2: prep.storeAddr2, carry: carry});
          ixRec[la.tail()] <= IxRecov{x: st.snapshotIndex(), ind: st.readIndicators(), adv: advSeq, sto: storeSeq, oth: otherSeq};
          pcReg <= pc + ((len == Full) ? 2 : 1);
          // Its preparation time, OF WHICH THIS CLOCK IS THE FIRST
          // (2026-11-17): `ibusy` clocks follow the load, so a
          // decode of N clocks is N - 1 here.  Before, the load clock
          // came on top and a VFL decode of 3.6 us (12 clocks) took 13,
          // 14 with the removal clock `ib` now gives back.  An I-box
          // operand also passes the I-Checker (fpIboxCheckClocks).
          Bit#(16) prepClk = 2 * iboxCycles(di, False) - 1
                             + fpIboxCheckClocks(di, da)
                             + fpIndexedIboxClocks(di, da)
                             - vflImmIndexedSaving(di);   // no word-boundary test (StretchTiming)
          Bit#(16) paid = (serialPc == tagged Valid pc) ? serialPaid : 0;
          ibusy <= (prepClk > paid) ? prepClk - paid : 0;
          serialPc <= tagged Invalid;
          xholdPc <= tagged Invalid;
        end
      end
    end else if (prepared matches tagged Valid {.len, .di} &&& di matches tagged BranchInd .bi
                 &&& !indexIndicator(bi.indNum) &&& !isValid(intPC)) begin
      // A branch on an arithmetic indicator: guess not taken (plan
      // §6d). Load it as a branch level with its target, snapshot the
      // index words and indicators, and carry on down the fall-
      // through path. One guess at a time.
      if (!guessPending && la.count() < 4 && !progressivePending) begin
        la.load(LaLevel{valid: True, kind: Whole, di: di, pc: pc, len: len, da: tagged Invalid,
                        data: tagged Invalid, fetchIssued: False, waitFor: tagged Invalid,
                        branch: True, target: effAddr19(st, bi.addr, {3'b0, bi.idx}),
                        storeAddr: tagged Invalid, storeAddr2: tagged Invalid,
                        carry: LaCarry{addr: 0, lbo: 0}});
        ixRec[la.tail()] <= IxRecov{x: st.snapshotIndex(), ind: st.readIndicators(), adv: advSeq, sto: storeSeq, oth: otherSeq};
        guessPending <= True;
        pcReg <= pc + ((len == Full) ? 2 : 1);
        ibusy <= 2 * 6;   // the branch's four-level load (Blosk p.39)
        xholdPc <= tagged Invalid;
        serialPc <= tagged Invalid;
      end
    end else if (prepared matches tagged Valid {.len, .di}) begin
      // I-box class: execute ahead of pending levels unless a hazard
      // (plan §6c) says wait; never while the arithmetic unit's own
      // instruction is mid-flight (it owns the resume path).
      // (or BESIDE a level a box holds -- the FP box, and since 2026-11-23
      // the divider, decimal adder and VFL multiplier (boxReleases) -- in
      // the clock the resume yields or the hold clocks: the level release,
      // above yieldToPrepare; mkEBox refuses an instruction that would bail.)
      // An I-box store that will need a store level waits for a free one.
      Maybe#(WordAddr) sw = iboxStoreWord(di);
      if ((!ebox.busyFor(OwnerLA) || yieldToPrepare || besideHold)
          && !iboxHazard(st, guessPending, di, nl)
          && !(isValid(sw) && storeNeedsLevel && la.count() == 4)
          && !lveBehindStore(di, nl)) begin
        match {.completed, .d1} <- startExecute(pc, len, di,
                              isValid(intPC) ? tagged Valid pcReg : tagged Invalid);
        done = d1;
        Bool refused = uncountRefused && ebox.busyFor(OwnerLA) && !completed;
        if (!refused) begin
          advSeq <= advSeq + 1;   // the I-box has advanced (interruption recovery)
          iboxAt <= clk;          // ... in this clock (rl_int_watch)
          // storeSeq counts the I-box stores MADE ahead (not held in a
          // level); one that reads first is counted, or held, when it
          // completes (rl_exec_resume).
          if (completed &&& sw matches tagged Valid .w &&& storeNeedsLevel)
            holdStoreInLevel(pc, len, di, w);
          else if (isIboxStore(di) && (completed || !isValid(sw)))
            storeSeq <= storeSeq + 1;
          xholdPc <= tagged Invalid;
          serialPc <= tagged Invalid;
        end
      end
    end
    eArm.send;
    haltedReg <= done;
  endrule

  method Action start();
    running <= True;
  endmethod

  method Action stop();
    running <= False;
  endmethod
  method Bool halted() = haltedReg;
  method Bool idle() = haltedReg && !(st.irqEnabled() &&
                         (isValid(ioPending) || statusWaiting || armInterrupt || isValid(intPC)));

  method HWordAddr getPC() = pcReg;
  method Action setPC(HWordAddr a);
    pcReg <= a;
    restartSeq <= restartSeq + 1;
    haltedReg <= False;
  endmethod

  // p.126: "The exchange automatically stores in the control word
  // location for the channel responsible for the channel signal a
  // fixed control word with the following contents: Data word address
  // = 4, Chain flag = 1, Multiple flag = 0, Skip flag = 0, Count = 1,
  // Refill address = 4", and then "initiates a READ for the indicated
  // channel, using the fixed control word".
  //
  // THE CHANNEL SIGNAL IS NOT SEPARATELY MODELLED.  StretchIO has one
  // tape unit on its own channel with no not-ready/ready transition
  // to raise one, and p.126 says loading works "only from a unit
  // having the selection address 0" -- which is what that unit is.
  // So this method is the key press and the signal together.  Item 7
  // of docs/NEXT.md 5k remains open for the multi-unit case.
  //
  // suppressEop is True because p.126 says "The EOP as well as the EE
  // indications, however, are not turned on upon the completion of
  // the operation."
  method Action iplStart();
    ControlWord fixed = ControlWord {
      dataAddr: 4, unitReady: 1, epgk: 0, uk: 0, ee: 0, eop: 0, cs: 0,
      seop: 0, chain: 1, multiple: 0, skip: 0, count: 1, refill: 4 };
    ioDev.writeChanCW(chanTape, fixed);
    ioPending <= tagged Valid IoXfer {
      ch: chanTape, isWrite: False, memAddr: 4, devIdx: 0,
      remaining: 1, suppressEop: True, skip: False, untilMark: False,
      zeroFill: False };
    iplActive <= True;
  endmethod

  interface mem = st;
  interface io = ioDev;
endmodule

endpackage
