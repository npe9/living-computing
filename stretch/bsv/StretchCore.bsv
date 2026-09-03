// StretchCore.bsv
//
// Top-level, non-pipelined IBM 7030 core: fetch, decode, execute, one
// instruction per `step()` call. See bsv/README.md "Scope" for why this
// is NOT the famous lookahead/pipelined microarchitecture -- this
// module targets ISA-level correctness only.

package StretchCore;

import Vector::*;
import StretchTypes::*;
import StretchStorage::*;
import StretchIO::*;
import StretchDecode::*;
import StretchExecute::*;
import StretchVFL::*;      // effLength/effByteSize for the VFL time budget

interface StretchCore;
  // Fetch+decode+execute exactly one instruction; returns True iff the
  // instruction branched to its own address (the "BEW, $" halt idiom,
  // C22-6531 p.14 -- "$" is the location counter, so this targets the
  // instruction itself). Runners that assemble and load real STRAP
  // programs use this to stop instead of a fixed step count -- see
  // stretch/strap/gen_tb.py.
  //
  // A progressive-indexing VFL instruction (Reference Manual p.21)
  // takes TWO calls to step() to complete -- the manual's own words:
  // "An operation in which progressive indexing is specified is
  // executed in two parts." The first call does everything except the
  // index-register write-back and does NOT advance the PC; the second
  // call (with no new instruction fetched) performs just that write
  // and then advances the PC.
  //
  // An RD or W input-output instruction (Reference Manual "IBM 7619
  // Exchange", pp.104-127) similarly takes MULTIPLE calls to complete:
  // the first call fetches the control word, starts the transfer, and
  // DOES advance the PC (matching the manual: "the computer then
  // proceeds to the execution of the next instruction"), but every
  // subsequent call moves exactly one more word of the block and
  // fetches nothing new until the whole block has moved -- see the
  // ioPending case below and StretchIO.bsv's file header for why this
  // makes the transfer synchronous from the program's point of view
  // (no genuine CPU/IO overlap) even though the real hardware overlaps
  // them. Both mechanisms return False on every call that isn't the
  // final one (a taken branch is the only way next==pc, and neither
  // progressive indexing nor an I/O transfer branches) -- callers that
  // just loop on step() until it returns True need no changes to
  // account for either.
  method ActionValue#(Bool) step();
  method HWordAddr getPC();
  method Action setPC(HWordAddr a);
  interface StretchStorage mem;  // direct access for test setup/inspection
  interface StretchIO io;        // simulated device access for test
                                  // setup/inspection -- see StretchIO.bsv
endinterface

module mkStretchCore(StretchCore);
  StretchStorage st <- mkStretchStorage;
  StretchIO ioDev <- mkStretchIO;
  Reg#(HWordAddr) pcReg <- mkReg(0);
  Reg#(Maybe#(Tuple2#(Bit#(4), IndexWord))) pendingIdxWrite <- mkReg(tagged Invalid);
  Reg#(Maybe#(IoXfer)) ioPending <- mkReg(tagged Invalid);

  // The instruction unit's instruction buffers 1Y/2Y and IC controls
  // (docs/microarchitecture_plan.md stage 2a; Blosk TR00.722 pp.7-10,
  // 25; CE manual figs 3.1.1-3.1.5). Each Y holds one 64-bit
  // instruction word fetched ahead of the instruction counter through
  // its own bus channel (StretchStorage.fetchReq/fetchReady/fetchResp,
  // return tags 1Y/2Y); a word is usable one I-checker cycle (two
  // clocks) after it arrives. The IC controls keep both filled with
  // the next words in sequence (`nextFetch`), free a Y once the
  // instruction counter has passed its word, and invalidate both on a
  // taken branch, a setPC, or a store to a prefetched word (program
  // store compare, Blosk p.21). A fetch still in flight for an
  // invalidated Y is discarded on arrival.
  Vector#(2, Reg#(YReg)) yr <- replicateM(mkReg(YReg{valid: False, pending: False,
                                                      discard: False, addr: 0, data: 0, chk: 0}));
  Reg#(WordAddr) nextFetch <- mkReg(0);
  // Restart requests (branch taken inside step(); setPC from outside)
  // as sequence numbers, so each register has exactly one writer.
  Reg#(Bit#(8)) branchSeq  <- mkReg(0);   // written in step()'s branch paths
  Reg#(Bit#(8)) restartSeq <- mkReg(0);   // written by setPC
  Reg#(Bit#(8)) restartSeen <- mkReg(0);  // written at the top of step()
  Reg#(Bit#(8)) branchSeen  <- mkReg(0);
  // ---- Stage 3a: the look-ahead (docs/microarchitecture_plan.md §6,
  // Buchholz ch.15, Cocke & Kolsky §III.C). Four levels in a ring;
  // E-box-class instructions (VFL, connectives, floating point) leave
  // the instruction unit into a level with their operand address, the
  // levels' fetches are issued ahead through their own bus channels,
  // and the arithmetic unit removes levels in order, executing each
  // once its operand is present. A level whose operand address equals
  // that of an earlier unretired level waits for that level to retire
  // before fetching (a store ahead of a load to the same word: the
  // LAAR's job, here done conservatively for any earlier level). In
  // this first cut an I-box-class instruction waits for the levels to
  // drain before executing (no recovery levels yet), and so does a
  // load behind a progressive-indexing instruction, whose index
  // register is modified only at execution.
  Vector#(4, Reg#(LaLevel)) la <- replicateM(mkReg(LaLevel{valid: False, di: tagged Invalid,
        pc: 0, len: Half, da: tagged Invalid, data: tagged Invalid, fetchIssued: False,
        waitFor: tagged Invalid, branch: False, target: 0}));
  // ---- Stage 3c (plan §6d): the not-taken guess. A branch on an
  // arithmetic indicator is loaded as a branch level; the instruction
  // unit snapshots the index words and indicators and continues down
  // the fall-through path. When the arithmetic unit reaches the level
  // the indicators are final: guess right, retire; guess wrong, cancel
  // the younger levels and, on the next clock (`recover`), restore the
  // snapshot, reset the instruction counter to the target and refetch.
  Reg#(Bool)                 guessPending <- mkReg(False);
  Reg#(Vector#(16, Word64))  xSnap        <- mkReg(replicate(0));
  Reg#(Word64)               indSnap      <- mkReg(0);
  Reg#(Maybe#(HWordAddr))    recover      <- mkReg(tagged Invalid);
  function Bool isIboxStore(DecodedInstr d);
    case (d) matches
      tagged DirIndex .x: return x.code[4] == 1;          // SX/SV/SC/SR
      tagged BranchOrMisc .x: return x.misc && x.code == 3'b100;  // Z
      tagged Sic .*: return True;
      tagged Transmit .*: return True;
      default: return False;
    endcase
  endfunction
  Reg#(Bit#(2)) laHead  <- mkReg(0);
  Reg#(Bit#(2)) laTail  <- mkReg(0);
  Reg#(Bit#(3)) laCount <- mkReg(0);
  Reg#(Bool)    auActive <- mkReg(False);  // execPending belongs to the look-ahead head
  Reg#(Bit#(16)) ebusy  <- mkReg(0);       // E-box time of the last removed instruction

  function Bool isEboxClass(DecodedInstr d);
    case (d) matches
      tagged VflInt .*: return True;
      tagged Connective .*: return True;
      tagged Fp .*: return True;
      default: return False;
    endcase
  endfunction
  // Does the instruction fetch a memory operand (so a level can be
  // loaded with its address from execute()'s side-effect-free bail)?
  function Bool fetchesOperand(DecodedInstr d);
    case (d) matches
      tagged VflInt .v: return v.a.p != 4;
      tagged Connective .c: return c.a.p != 4;
      tagged Fp .f: return f.code == 7'b0000110;   // FP L; ST fetches nothing
      default: return False;
    endcase
  endfunction
  function Bool hasProgressive(DecodedInstr d);
    case (d) matches
      tagged VflInt .v: return v.a.p != 0 && v.a.p != 4;
      tagged Connective .c: return c.a.p != 0 && c.a.p != 4;
      default: return False;
    endcase
  endfunction

  // ---- Stage 3b (plan §6c): may an I-box-class instruction execute now,
  // with look-ahead levels pending? It may unless a level's operand
  // word is one it reads or writes, or it branches on an arithmetic
  // indicator (which needs the levels drained). The operand words use
  // the same effective-address arithmetic as execute().
  function Bool levelHolds(Vector#(4, LaLevel) lv, WordAddr w);
    Bool r = False;
    for (Integer k = 0; k < 4; k = k + 1)
      if (lv[k].da matches tagged Valid .a &&& lv[k].valid &&& a == w) r = True;
    return r;
  endfunction

  // Mask of the index indicators in the indicator word (bit n is w[63-n]).
  Word64 indexIndMask = (64'h1 << (63 - ind_XF)) | (64'h1 << (63 - ind_XCZ)) | (64'h1 << (63 - ind_XVLZ))
                      | (64'h1 << (63 - ind_XVZ)) | (64'h1 << (63 - ind_XVGZ)) | (64'h1 << (63 - ind_XL))
                      | (64'h1 << (63 - ind_XE)) | (64'h1 << (63 - ind_XH));
  function Bool indexIndicator(Bit#(6) n) =
    (n == ind_XF || n == ind_XCZ || n == ind_XVLZ || n == ind_XVZ || n == ind_XVGZ
     || n == ind_XL || n == ind_XE || n == ind_XH);

  function Bool iboxHazard(DecodedInstr d, Vector#(4, LaLevel) lv);
    Bool pending = False;
    for (Integer k = 0; k < 4; k = k + 1) if (lv[k].valid) pending = True;
    Bool h = True;   // anything not listed (Transmit, I/O, EX...): drain first
    case (d) matches
      tagged DirIndex .x: begin
        HWordAddr ea = effAddr19(st, x.addr, x.idx);
        Bool refillWord = (x.code == 5'b01111) && levelHolds(lv, zeroExtend(st.readIndex(x.j).refill)); // V+CR
        h = levelHolds(lv, ea[18:1]) || refillWord;
      end
      tagged ImmIndex .x:
        h = (x.code == 4'b0111 || x.code == 4'b1111)                          // V+ICR / V-ICR
            && levelHolds(lv, zeroExtend(st.readIndex(x.j).refill));
      tagged CountBranch .x:
        h = (x.refill == 1) && levelHolds(lv, zeroExtend(st.readIndex(x.j).refill));
      tagged BranchInd .x: h = !indexIndicator(x.indNum);
      tagged BranchOrMisc .x: begin
        // Unconditional branches drain the levels first: a halt (a
        // branch to itself) must not be reported while E-box work is
        // still in the look-ahead, and on the real machine a taken
        // branch empties the look-ahead anyway (Perf. Char. p.3-18:
        // "BD ... empty the LA completely"). NOP is free.
        if (!x.misc) h = (x.code != 3'b110);
        else if (x.code == 3'b100) h = levelHolds(lv, baWord(effAddr24(st, {x.addr, 5'b0}, x.idx))); // Z
        else if (x.code == 3'b000 || x.code == 3'b001)                         // R / RCZ
          h = levelHolds(lv, zeroExtend(st.readIndex(x.idx).refill));
        else h = True;                                                         // EX/EXIC
      end
      tagged Sic .x: begin
        BitAddr ea = effAddr24(st, x.addr, x.idx);
        h = levelHolds(lv, ea[23:6]) || iboxHazard(decodeHalfWord(x.inner), lv);
      end
      default: h = True;
    endcase
    return (pending && h) || (guessPending && isIboxStore(d));
  endfunction

  // Stage 2b timing registers (see iboxCycles below).
  Reg#(Bit#(32)) clk      <- mkReg(0);   // clocks since reset
  Reg#(Bit#(32)) startClk <- mkReg(0);   // dispatch clock of the current instruction
  Reg#(Bit#(16)) ibusy    <- mkReg(0);   // clocks the next preparation must still wait

  // ---- Stage 2b: instruction-unit timing (docs/microarchitecture_plan.md
  // §6a). Each instruction carries a time budget in clocks (one clock =
  // 0.3 us; one I-box control cycle = 2 clocks = 0.6 us as shipped),
  // taken from IBM's own numbers: for I-box instructions the
  // Performance Characteristics tables 4-8 ("basic time + dec", dec =
  // 0.6 us, addresses in external memory), for floating point the
  // 2-cycle preparation of Blosk fig.6 plus table 2's E-box cycles,
  // for VFL the 6-cycle minimum preparation (+1 per indexing op, Perf.
  // Char. p.3-17) plus table 3's SAU equation (1.8 us pre-execution,
  // 0.6 us per byte, 0.6 us termination). The budget covers the
  // instruction's own memory waits when memory is free: it is started
  // at dispatch and whatever is left when the semantics complete
  // (execute() and its operand reads) holds the next preparation, so
  // a busy memory unit adds delay while a free one does not. Without
  // the look-ahead (stage 3) E-box time is not overlapped with the
  // next preparation -- a documented stage-2 simplification.

  function Bit#(16) iboxCycles(DecodedInstr d, Bool taken);
    case (d) matches
      tagged DirIndex .x: return case (x.code)
          5'b00001: 9;   // LX     4.8 + dec
          5'b10001: 3;   // SX     1.2 + dec (+ LAAR)
          5'b01111: 15;  // V+CR   8.4 + dec
          default:  8;   // LV/LC/LR/SV/SC/SR/V+/V+C/KV/KC  4.2 + dec
        endcase;
      tagged ImmIndex .x: return case (x.code)
          4'b0110, 4'b1110: 6;   // V+IC / V-IC   3.0 + dec
          4'b0111, 4'b1111: 13;  // V+ICR / V-ICR 7.2 + dec
          default: 5;            // LVI/LCI/LRI/LVNI/V±I/C±I/KVI/KVNI/KCI  2.4 + dec
        endcase;
      tagged CountBranch .x: return (x.refill == 1) ? (taken ? 12 : 11)   // CBR 6.6/6.0 + dec
                                                     : (taken ? 8 : 7);    // CB  4.2/3.6 + dec
      tagged BranchInd .*: return 6;   // Blosk fig.10: decode + 5 execution cycles
      tagged BranchOrMisc .x: return x.misc
          ? (case (x.code) 3'b100: 3; 3'b001: 8; default: 14; endcase)   // Z / RCZ / R
          : (case (x.code) 3'b110: 3; 3'b011: 9; 3'b001: 11; default: 7; endcase); // NOP / BR / BD (+2 LA drains) / B,BE,BEW
      tagged Sic .x: return 2 + iboxCycles(decodeHalfWord(x.inner), taken); // "SIC to EM" columns: +1.2 us
      tagged Transmit .*: return 7;    // Blosk fig.9: 2 set-up + 5 per word (one word here)
      tagged Fp .*: return 2;          // preparation; E-box cycles added below
      tagged VflInt .v: return 6 + ((v.a.i1 != 0) ? 1 : 0);   // preparation, two LA levels
      tagged Connective .c: return 6 + ((c.a.i1 != 0) ? 1 : 0);
      tagged IoOp .*: return 6;
      default: return 3;
    endcase
  endfunction

  // E-box clocks for the executing classes (table 2 FP; table 3 SAU:
  // 1.8 us + 0.6 us per byte + 0.6 us, bytes = ceil(length / byte size)).
  function Bit#(16) eboxClocks(DecodedInstr d);
    case (d) matches
      tagged Fp .*: return 3;          // preparation; E-box cycles added below
      tagged VflInt .v: begin
        Bit#(7) len_ = effLength(v.a.length);
        Bit#(4) bsz  = effByteSize(v.a.bs);
        Bit#(8) bytes = (zeroExtend(len_) + zeroExtend(bsz) - 1) / zeroExtend(bsz);
        return 8 + 2 * zeroExtend(bytes);
      end
      tagged Connective .c: begin
        Bit#(7) len_ = effLength(c.a.length);
        Bit#(4) bsz  = effByteSize(c.a.bs);
        Bit#(8) bytes = (zeroExtend(len_) + zeroExtend(bsz) - 1) / zeroExtend(bsz);
        return 8 + 2 * zeroExtend(bytes);
      end
      default: return 0;
    endcase
  endfunction

  function Bit#(16) budgetClocks(DecodedInstr d, Bool taken) =
    2 * iboxCycles(d, taken) + eboxClocks(d);


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

  // In-progress execute() call that bailed out waiting on a
  // BRAM-eligible read (docs/phase2_arm_inventory.md's per-case-arm
  // staging; execute()'s own header comment in StretchExecute.bsv has
  // the full contract). Invalid: no execute() call in flight (either
  // none has been attempted yet this instruction, or the most recent
  // attempt completed). Valid tuple3(pc, len, di): execute() was
  // called for this decoded instruction and returned a
  // needsRead -- a request for that address was issued last cycle;
  // execPrefetch/execPrefetchCount (below) track what's been collected
  // so far, so the NEXT call to execute() can pick up with one more
  // slot filled.
  Reg#(Maybe#(Tuple3#(HWordAddr, InstrLen, DecodedInstr))) execPending <- mkReg(tagged Invalid);
  Reg#(Vector#(2, Word64)) execPrefetch <- mkReg(replicate(0));
  Reg#(Bit#(2)) execPrefetchCount <- mkReg(0);

  // Call execute() for a freshly decoded instruction (prefetchCount=0
  // -- no arm has been given anything yet). Either it completes
  // outright (the common case today, since only VflInt L can bail),
  // committing exactly as execute() always did, or it bails and this
  // starts execPending's own FSM instead. Shared by both fetchPending
  // completion paths (Half- and Full-length) below, so the dispatch
  // logic isn't duplicated between them.
  function ActionValue#(Bool) startExecute(HWordAddr pc, InstrLen len, DecodedInstr di) =
    actionvalue
      let {next, vflPending, ioStart, needsRead} <-
        execute(st, ioDev, pc, len, di, replicate(0), 0);
      startClk <= clk;
      if (needsRead matches tagged Valid .a) begin
        st.readWordReq(a);
        execPending <= tagged Valid tuple3(pc, len, di);
        execPrefetchCount <= 0;
        return False;
      end else begin
        pcReg <= next;
        pendingIdxWrite <= vflPending;
        ioPending <= ioStart;
        Bool taken = (next != pc + ((len == Full) ? 2 : 1));
        if (taken) branchSeq <= branchSeq + 1;
        ibusy <= budgetClocks(di, taken);   // completed in the dispatch clock
        return next == pc;
      end
    endactionvalue;

  // Look up a prefetched, checked instruction word.
  function Maybe#(Word64) yLookup(WordAddr w);
    Maybe#(Word64) r = tagged Invalid;
    for (Integer k = 0; k < 2; k = k + 1)
      if (yr[k].valid && yr[k].chk == 0 && yr[k].addr == w) r = tagged Valid yr[k].data;
    return r;
  endfunction

  method ActionValue#(Bool) step();
    Bool done = False;
    clk <= clk + 1;
    // E-box busy time counts down every clock regardless of what the
    // instruction unit does below; written once at the exit.
    Bit#(16) eb = (ebusy != 0) ? ebusy - 1 : 0;
    // ---- Look-ahead: collect arrived operands, issue one fetch ----
    Vector#(4, LaLevel) nl = readVReg(la);
    Bit#(2) nHead = laHead; Bit#(2) nTail = laTail; Bit#(3) nCount = laCount;
    for (Integer k = 0; k < 4; k = k + 1)
      if (nl[k].valid && nl[k].fetchIssued && !isValid(nl[k].data) && st.laReady(fromInteger(k))) begin
        let d <- st.laResp(fromInteger(k));
        nl[k].data = tagged Valid d;
      end
    Bool issuedLa = False;
    for (Integer k = 0; k < 4; k = k + 1)
      if (!issuedLa && nl[k].valid && isValid(nl[k].da) && !nl[k].fetchIssued && !isValid(nl[k].waitFor)) begin
        st.laReq(fromInteger(k), validValue(nl[k].da));
        nl[k].fetchIssued = True;
        issuedLa = True;
      end
    // ---- IC controls: run every clock, before the instruction FSM ----
    Vector#(2, YReg) ny = readVReg(yr);
    Bool restart = (restartSeq != restartSeen) || (branchSeq != branchSeen);
    WordAddr nf = nextFetch;
    WordAddr pcw = pcReg[18:1];
    for (Integer k = 0; k < 2; k = k + 1) begin
      // Program store compare: a store to a prefetched word invalidates it.
      if (st.recentStore() matches tagged Valid .sw &&& ny[k].addr == sw && (ny[k].valid || ny[k].pending)) begin
        ny[k].valid = False;
        if (ny[k].pending) ny[k].discard = True;
      end
      // Restart (taken branch or setPC): drop everything buffered.
      if (restart) begin
        ny[k].valid = False;
        if (ny[k].pending) ny[k].discard = True;
      end
      // Collect an arrived word; usable after the I-checker cycle.
      if (ny[k].pending && st.fetchReady(fromInteger(k))) begin
        let d <- st.fetchResp(fromInteger(k));
        ny[k].pending = False;
        if (ny[k].discard) ny[k].discard = False;
        else begin ny[k].valid = True; ny[k].data = d; ny[k].chk = 2; end
      end else if (ny[k].valid && ny[k].chk != 0)
        ny[k].chk = ny[k].chk - 1;
      // Free a word the instruction counter has passed.
      if (ny[k].valid && ny[k].addr < pcw) ny[k].valid = False;
    end
    if (restart) begin
      nf = pcw;
      restartSeen <= restartSeq;
      branchSeen <= branchSeq;
    end
    // Issue at most one prefetch per clock into a free Y, in order.
    Bool issued = False;
    for (Integer k = 0; k < 2; k = k + 1)
      if (!issued && !ny[k].valid && !ny[k].pending && !restart) begin
        st.fetchReq(fromInteger(k), nf);
        ny[k].pending = True; ny[k].discard = False; ny[k].addr = nf; ny[k].chk = 0;
        nf = nf + 1;
        issued = True;
      end
    writeVReg(yr, ny);
    nextFetch <= nf;

    if (recover matches tagged Valid .tgt) begin
      // Wrong-way recovery (Perf. Char. p.3-23): undo the index
      // registers and index indicators the I-box changed ahead, take the
      // branch, and refetch. Charged as the branch's own execution
      // cycles again plus the refill the restart costs.
      st.restoreIndex(xSnap);
      Word64 ind = st.readIndicators();
      Word64 keep = ~indexIndMask;
      st.setIndicatorBits((ind & keep) | (indSnap & indexIndMask));
      pcReg <= tgt;
      branchSeq <= branchSeq + 1;
      recover <= tagged Invalid;
      ibusy <= 12;
      done = False;
    end else if (ioPending matches tagged Valid .x) begin
      // Service one word of an in-flight RD/W transfer. See this
      // interface's step() doc above and StretchIO.bsv's file header.
      // Capacity is device-kind-dependent: the tape's TapeWords is
      // deliberately smaller than the reader/printer's DeviceWords
      // (see StretchIO.bsv) so this is where that distinction has to
      // be made, not a single shared constant.
      DeviceKind kind = kindOf(x.ch);
      Bit#(6) capacity = (kind == DevTape)
        ? fromInteger(valueOf(TapeWords)) : fromInteger(valueOf(DeviceWords));
      if (x.devIdx >= capacity) begin
        // "the unit runs out of material" (p.121): End Exception, not
        // Unit Check -- the block ends early; whatever was already
        // moved stays moved, and the control word reflects exactly
        // that (dataAddr/count as of the last word actually
        // transferred, since this cycle transfers nothing).
        ControlWord cw = ioDev.readChanCW(x.ch);
        cw.ee = 1;
        if (!x.suppressEop) cw.eop = 1;
        ioDev.writeChanCW(x.ch, cw);
        ioPending <= tagged Invalid;
        done = False;
      end else if (!st.writeReady()) begin
        // The store queue is full: the exchange waits for the memory
        // bus before moving the next word (a RD-direction word is a
        // store; the W-direction path is also held so the two
        // directions keep the same per-word pacing).
        done = False;
      end else if (x.isWrite && !ioReadIssued) begin
        // W-direction (memory->device), first visit to this word:
        // issue the read request and wait. ioPending/x are left
        // untouched (same devIdx/memAddr/remaining next call), so the
        // NEXT call's `x` still names this same word once the
        // response is ready.
        st.readWordReq(x.memAddr);
        ioReadIssued <= True;
        done = False;
      end else if (x.isWrite && !st.responseReady()) begin
        // W-direction: the memory read is in flight; wait for it.
        done = False;
      end else begin
        // Either RD-direction (always one call, ioReadIssued unused
        // and stays False) or W-direction with the read response now
        // ready to collect.
        if (kind == DevTape) begin
          TapeIndex ti = truncate(x.devIdx); // safe: confirmed < TapeWords above
          if (x.isWrite) begin
            Word64 v <- st.readWordResp();
            ioDev.writeTapeWord(ti, v);
          end else if (!x.skip)
            st.writeWord(x.memAddr, ioDev.readTapeWord(ti));
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
            ioDev.writePrinterWord(di, v);
          end else if (!x.skip)
            st.writeWord(x.memAddr, ioDev.readerWord(di));
        end
        // else: SKIP flag set on a READ (p.107) -- the device cursor
        // and memory address still advance below exactly as if the
        // word had been transferred, but core storage is left
        // untouched for this word.
        ioReadIssued <= False;
        Bit#(19) rem1 = x.remaining - 1;
        ControlWord cw = ioDev.readChanCW(x.ch);
        cw.dataAddr = x.memAddr + 1;
        cw.count = truncate(rem1);
        if (rem1 == 0) begin
          if (!x.suppressEop) cw.eop = 1;
          ioDev.writeChanCW(x.ch, cw);
          ioPending <= tagged Invalid;
        end else begin
          ioDev.writeChanCW(x.ch, cw);
          ioPending <= tagged Valid IoXfer {
            ch: x.ch, isWrite: x.isWrite, memAddr: x.memAddr + 1,
            devIdx: x.devIdx + 1, remaining: rem1,
            suppressEop: x.suppressEop, skip: x.skip };
        end
        done = False;
      end
    end else if (pendingIdxWrite matches tagged Valid .p) begin
      // Part 2 of a progressive-indexing instruction: nothing was
      // fetched this call, and PC already advanced on part 1.
      st.writeIndex(tpl_1(p), tpl_2(p));
      pendingIdxWrite <= tagged Invalid;
      done = False;
    end else if (execPending matches tagged Valid .ep &&& st.responseReady()) begin
      // Resume an execute() call that bailed out waiting on a
      // BRAM-eligible read -- collect the response into the next
      // prefetch slot and try again. See execPending's own comment
      // above and execute()'s header comment in StretchExecute.bsv
      // for the full contract.
      HWordAddr pc       = tpl_1(ep);
      InstrLen len        = tpl_2(ep);
      DecodedInstr di     = tpl_3(ep);
      Word64 v <- st.readWordResp();
      Vector#(2, Word64) newPrefetch = execPrefetch;
      newPrefetch[execPrefetchCount] = v;
      Bit#(2) newCount = execPrefetchCount + 1;
      let {next, vflPending, ioStart, needsRead} <-
        execute(st, ioDev, pc, len, di, newPrefetch, newCount);
      if (needsRead matches tagged Valid .a) begin
        st.readWordReq(a);
        execPrefetch <= newPrefetch;
        execPrefetchCount <= newCount;
        done = False;
      end else begin
        pendingIdxWrite <= vflPending;
        ioPending <= ioStart;
        execPending <= tagged Invalid;
        if (auActive) begin
          // A look-ahead level's instruction finished: retire it.
          auActive <= False;
          eb = eboxClocks(di);
          nl[nHead].valid = False;
          for (Integer k = 0; k < 4; k = k + 1)
            if (nl[k].waitFor matches tagged Valid .w &&& w == nHead) nl[k].waitFor = tagged Invalid;
          nHead = nHead + 1; nCount = nCount - 1;
          done = False;
        end else begin
          pcReg <= next;
          Bool taken = (next != pc + ((len == Full) ? 2 : 1));
          if (taken) branchSeq <= branchSeq + 1;
          Bit#(32) elapsed = clk - startClk;
          Bit#(16) budget = budgetClocks(di, taken);
          ibusy <= (elapsed >= zeroExtend(budget)) ? 0 : budget - truncate(elapsed);
          done = (next == pc);
        end
      end
    end else if (nCount != 0 && ebusy == 0 && !auActive
                 && (!isValid(nl[nHead].da) || isValid(nl[nHead].data))) begin
      // (A branch level has no operand and is removed as soon as it is
      // the head with the E-box free, i.e. once every earlier level has
      // retired.)
      // Remove the head level into the arithmetic unit: its operand
      // (if any) is present, so execute() runs with it pre-supplied;
      // any further reads it needs go through the resume path.
      LaLevel h = nl[nHead];
      Vector#(2, Word64) pf = replicate(0);
      Bit#(2) cnt = 0;
      if (h.data matches tagged Valid .d) begin pf[0] = d; cnt = 1; end
      let {next, vflPending, ioStart, needsRead} <-
        execute(st, ioDev, h.pc, h.len, h.di, pf, cnt);
      if (h.branch) begin
        // The guessed branch, now with final indicators.
        Bool taken = (next != h.pc + ((h.len == Full) ? 2 : 1));
        guessPending <= False;
        if (taken) begin
          // Wrong guess: cancel every younger level, recover next clock.
          for (Integer k = 0; k < 4; k = k + 1) nl[k].valid = False;
          nTail = nHead; nCount = 0;
          recover <= tagged Valid next;
        end else begin
          nl[nHead].valid = False;
          for (Integer k = 0; k < 4; k = k + 1)
            if (nl[k].waitFor matches tagged Valid .w &&& w == nHead) nl[k].waitFor = tagged Invalid;
          nHead = nHead + 1; nCount = nCount - 1;
        end
        eb = 2 * 6;   // Blosk fig.10: decode + five execution cycles
      end else if (needsRead matches tagged Valid .a) begin
        st.readWordReq(a);
        execPending <= tagged Valid tuple3(h.pc, h.len, h.di);
        execPrefetch <= pf;
        execPrefetchCount <= cnt;
        auActive <= True;
      end else begin
        pendingIdxWrite <= vflPending;
        ioPending <= ioStart;
        eb = eboxClocks(h.di);
        nl[nHead].valid = False;
        for (Integer k = 0; k < 4; k = k + 1)
          if (nl[k].waitFor matches tagged Valid .w &&& w == nHead) nl[k].waitFor = tagged Invalid;
        nHead = nHead + 1; nCount = nCount - 1;
      end
      done = False;
    end else begin
      // Preparation: transfer the next instruction from the Y buffers
      // (both halves of a full-word instruction, which may straddle
      // 1Y/2Y); an E-box-class instruction is loaded into a look-ahead
      // level, an I-box-class one executes here once the levels have
      // drained. Stall until the word(s) are buffered and checked.
      HWordAddr pc = pcReg;
      Maybe#(Tuple2#(InstrLen, DecodedInstr)) prepared = tagged Invalid;
      if (yLookup(pc[18:1]) matches tagged Valid .w0) begin
        HalfWord32 hw0 = (pc[0] == 0) ? w0[63:32] : w0[31:0];
        InstrLen len = instrLen(hw0);
        if (len == Half)
          prepared = tagged Valid tuple2(len, decode(hw0, tagged Invalid));
        else begin
          HWordAddr pc1 = pc + 1;
          if (yLookup(pc1[18:1]) matches tagged Valid .w1) begin
            HalfWord32 hw1 = (pc1[0] == 0) ? w1[63:32] : w1[31:0];
            prepared = tagged Valid tuple2(Full, decode(hw0, tagged Valid hw1));
          end
        end
      end
      Bool progressivePending = False;
      for (Integer k = 0; k < 4; k = k + 1)
        if (nl[k].valid && hasProgressive(nl[k].di)) progressivePending = True;
      if (isValid(execPending) && !auActive)
        done = False;         // an I-box instruction is waiting on its operand read
      else if (ibusy != 0) begin
        ibusy <= ibusy - 1;   // previous instruction's time budget still running
        done = False;
      end else if (!st.writeReady())
        done = False; // a storing instruction could find the queue full: wait
      else if (prepared matches tagged Valid {.len, .di} &&& isEboxClass(di)) begin
        if (nCount < 4 && !progressivePending) begin
          Maybe#(WordAddr) da = tagged Invalid;
          Bool loaded = True;
          if (fetchesOperand(di)) begin
            // Side-effect-free probe: execute() with no operand bails
            // out with the address of the operand it needs.
            let {next, vflPending, ioStart, needsRead} <-
              execute(st, ioDev, pc, len, di, replicate(0), 0);
            if (needsRead matches tagged Valid .a) da = tagged Valid a;
            else begin
              // Classified as fetching but completed: treat as executed.
              $display("StretchCore: E-box instruction at %0d executed at preparation (classification mismatch)", pc);
              pcReg <= next;
              pendingIdxWrite <= vflPending;
              ioPending <= ioStart;
              loaded = False;
            end
          end
          if (loaded) begin
            Maybe#(Bit#(2)) wf = tagged Invalid;
            for (Integer k = 0; k < 4; k = k + 1)
              if (da matches tagged Valid .a &&& nl[k].valid &&& isValid(nl[k].da) &&& validValue(nl[k].da) == a)
                wf = tagged Valid fromInteger(k);
            nl[nTail] = LaLevel{valid: True, di: di, pc: pc, len: len, da: da,
                                data: tagged Invalid, fetchIssued: False, waitFor: wf,
                                branch: False, target: 0};
            nTail = nTail + 1; nCount = nCount + 1;
            pcReg <= pc + ((len == Full) ? 2 : 1);
            ibusy <= 2 * iboxCycles(di, False);   // its preparation time
          end
        end
        done = False;
      end else if (prepared matches tagged Valid {.len, .di} &&& di matches tagged BranchInd .bi
                   &&& !indexIndicator(bi.indNum)) begin
        // A branch on an arithmetic indicator: guess not taken (plan
        // §6d). Load it as a branch level with its target, snapshot the
        // index words and indicators, and carry on down the fall-
        // through path. One guess at a time.
        if (!guessPending && nCount < 4 && !progressivePending) begin
          nl[nTail] = LaLevel{valid: True, di: di, pc: pc, len: len, da: tagged Invalid,
                              data: tagged Invalid, fetchIssued: False, waitFor: tagged Invalid,
                              branch: True, target: effAddr19(st, bi.addr, {3'b0, bi.idx})};
          nTail = nTail + 1; nCount = nCount + 1;
          xSnap <= st.snapshotIndex();
          indSnap <= st.readIndicators();
          guessPending <= True;
          pcReg <= pc + ((len == Full) ? 2 : 1);
          ibusy <= 2 * 6;   // the branch's four-level load (Blosk p.39)
        end
        done = False;
      end else if (prepared matches tagged Valid {.len, .di}) begin
        // I-box class: execute ahead of pending levels unless a hazard
        // (plan §6c) says wait; never while the arithmetic unit's own
        // instruction is mid-flight (it owns the resume path).
        if (!auActive && !iboxHazard(di, nl)) begin
          let d1 <- startExecute(pc, len, di);
          done = d1;
        end else
          done = False;
      end else
        done = False;
    end
    writeVReg(la, nl);
    laHead <= nHead; laTail <= nTail; laCount <= nCount;
    ebusy <= eb;
    return done;
  endmethod

  method HWordAddr getPC() = pcReg;
  method Action setPC(HWordAddr a);
    pcReg <= a;
    restartSeq <= restartSeq + 1;
  endmethod

  interface mem = st;
  interface io = ioDev;
endmodule

endpackage
