// HobbitCore.bsv -- orchestration of the ATT92010 Hobbit model.
//
// Structure (the pipeline of printed pp. 1-32/1-33 and section 4.3 of
// the January 1993 Programmer's Reference Manual):
//
//   HobbitPrefetch     the 3 KB three-way prefetch buffer cache (box).
//   HobbitPdu          prefetch/decode unit, PDU_S1/S2/S3 (three stage
//                      modules, Figure 1-1 "3-STAGE PIPELINE").
//   HobbitDecodeStore  32-entry direct-mapped decoded instruction cache
//                      of 32 x 192 bits (p. 1-2, p. 1-1).
//   HobbitStackCache   64 x 32 x 2-bit stack cache: one read and one
//                      write port per clock (box).
//   HobbitEuS1/S2/S3   execution unit, EU_S1/S2/S3 (Figure 1-1
//                      "EXECUTION UNIT 3-STAGE PIPELINE").
//
// The stage modules follow Flute's CPU_StageN_IFC convention
// (enq/deq/out/set_full plus Server#(Token,Token)); the wiring below is
// the orchestrator, as Flute's CPU.bsv is.  See
// docs/bluespec_architecture.md.
//
// Cycle accounting.  Each stage supplies one issue slot.  `extraCycles`
// in HobbitTypes adds only what Tables 4-32..4-36 print beyond that
// slot: RETURN and POPN +1, ENTER +Q.E, the unimplemented-opcode
// sequence +6+A.  A conditional jump's misprediction is structural: the
// stage that can first see PSW.F decides how many younger slots the
// jump pays for (EU_S3 for a compare-adjacent jump: 2, EU_S2 for the
// two-instruction distance: 1, EU_S1 for three or more: 0), which is
// Table 4-35's 3/2/1.  A folded branch is one record with cyc = 0
// (p. 4-3 note, Table 4-35).  Fetch misses (the PDU/IC fill) and
// operand-forwarding stalls never enter `cyc`: they are not the
// instruction's occupancy, and the p. 4-1 assumptions charge no
// Table 4-37 fetch delay.
//
// The HRI record is the trace port (Flute's g_pc_trace analogue), not
// datapath: EU_S3 pushes records into a trace FIFO and mkHobbitCore
// drains and prints them one at a time.

package HobbitCore;

import Vector::*;
import FIFOF::*;
import GetPut::*;
import ClientServer::*;
import HobbitTypes::*;
import HobbitDecode::*;
import HobbitStackCache::*;
import HobbitMmu::*;
import HobbitEvents::*;

interface HobbitCore;
  // Warm the prefetch buffer from the synchronous memory (one 64-bit
  // line per three clocks) after the image is loaded; the run starts
  // when ready().
  method Action prefetchImage();
  method Bool prefetchReady();

  method Action start(Word sp, Word msp);
  // Start with an explicit PSW (the MMU path sets V = 1, p. 1-14).
  method Action startPsw(Word sp, Word msp, Word psw);
  // Start at an explicit PC (a Plan 9 image's entry is not 0).
  method Action startAt(Word pc, Word sp, Word msp, Word psw);

  method Bool halted();
  method Bool atLimit();
  method Bool faulted();
  method Word faultPc();
  method Word pc();

  method Word sp();
  method Word msp();
  method Word acc();
  method Word readMem(Word addr);
  method Word cacheWord(Word addr);
  method Bool cached(Word addr);

  method Bit#(32) folded();
  method Bit#(32) refills();
  method Bit#(32) instrs();
  method Word minSp();
  method Word maxSp();

  method Bool hriValid();
  method Hri hri();
  // True when no retirement record is being presented and none is
  // waiting; the harnesses use it to stop after the last record.
  method Bool quiescent();

  // ---- MMU / event testbench surface --------------------------------
  method Word psw();
  method Action setPsw(Word psw);
  method Word vb();
  method Action setVb(Word vb);
  method Bit#(3) il();
  method Action setIl(Bit#(3) il);
  method Word isp();
  method Word shad();
  method Action setIsp(Word isp);
  method Action setShad(Word shad);
  method Action flushPte(Word va);
  method Action flushTlb();
  method Action setStb(Word stb);
  method Bit#(32) mmuHits();
  method Bit#(32) mmuMisses();
  method Bit#(32) mmuWalks();
  method Bit#(32) mmuFaults();
  method Bool eventTaken();
  method Word eventPc();
  method Bit#(4) eventId();
  method Word savedPc();
  method Word savedPsw();
  method Bool eventActive();
  method Word eventMemRead(Word a);
  method Action eventMemWrite(Word a, Word v);

  // Verification probe for the harnesses (like HobbitMem::peek); the
  // machine never reads it.
  method Bit#(64) dbgState();
endinterface

typedef struct {
  Bool we;
  Word addr;
  Word data;
} WrInfo deriving (Bits);

function Bool isCondJumpOp(HobbitOp op) =
  op == OP_JMPTY || op == OP_JMPTN || op == OP_JMPFY || op == OP_JMPFN;

function Bool isCompareOp(HobbitOp op) =
  op == OP_CMPEQ || op == OP_CMPGT;

function Bool isSpOp(HobbitOp op) =
  op == OP_ENTER || op == OP_CATCH || op == OP_POPN || op == OP_RETURN;

function Bool signedGtW(Word a, Word b);
  Int#(32) x = unpack(a);
  Int#(32) y = unpack(b);
  return x > y;
endfunction

// The flag a folded branch must test.  A compare folded together with
// its branch produces the new PSW.F in the same instruction, so the
// branch sees the compare's result, not the previous flag (p. 3-13,
// p. 3-28, p. 4-7).
function Bool flagAfterOp(HobbitOp op, Word srcV, Word dstV, Bool oldFlag);
  case (op)
    OP_CMPEQ: return srcV == dstV;
    OP_CMPGT: return signedGtW(srcV, dstV);
    default:  return oldFlag;
  endcase
endfunction

// ---------------------------------------------------------------------
// EU_S1: fetch, operand read and the bypass network.
// ---------------------------------------------------------------------
typedef struct {
  DecInstEntry e;
  Word   pc;
  Word   spBefore;
  Word   mspBefore;
  Word   srcVal;
  Word   dstVal;
  Word   retPc;
  Word   base;
  Word   nextPc;       // predicted next PC
  Bit#(4) sinceCmp;    // issue distance from the last compare
  Word   extra;        // table extras beyond the pipeline slot
  Bool   operandMiss;
} EuS1Out deriving (Bits);

// One bypass source: the instruction in EU_S2 or EU_S3.
typedef struct {
  Bool valid;
  Bool we;
  Word addr;
  Word data;
  Bool changesSp;
  Word spAfter;
  Bool changesMsp;
  Word mspAfter;
} EuBypass deriving (Bits);

function EuBypass noBypass() =
  EuBypass { valid: False, we: False, addr: 0, data: 0,
             changesSp: False, spAfter: 0,
             changesMsp: False, mspAfter: 0 };

interface HobbitEuS1;
  interface Server#(Token, Token) server_reset;
  method Action start(Word pc);
  method Action stop();
  method Action deq;
  method EuS1Out out;
  method Bool notEmpty;
  method Word pc();
  method Bit#(8) dbgS1;
  // Drop whatever the slot holds and redirect to `pc` (a squash).
  method Action redirect(Word pc);
endinterface

module mkHobbitEuS1#(HobbitDecodeStore ic, HobbitStackCache sc,
                     MemCycles mcyc,
                     EuBypass byS2, EuBypass byS3, Reg#(Word) psw,
                     Bool squash, Word pcLimit,
                     Reg#(Bool) eventActive)(HobbitEuS1);
  // structure follows Flute (Bluespec, Inc., Apache-2.0) — see
  // docs/bluespec_architecture.md: one module per EU stage with a
  // registered boundary and one rule for the work the stage does alone.

  Reg#(Bool) active <- mkReg(False);
  // The stage holds at most one slot: `fullR` says the decoded entry for
  // pcR is present and is being handed to EU_S2.  No stall register is
  // needed, because the slot flag *is* the back-pressure (Flute's
  // CPU_Stage1 `full`), and only this stage writes it.
  Reg#(Bool) fullR <- mkReg(False);
  Reg#(Word) pcR <- mkReg(0);
  Reg#(Word) block <- mkReg(0);        // issue interlock, in clocks
  Reg#(Bit#(4)) sinceCmp <- mkReg(0);

  FIFOF#(Token) f_reset_reqs <- mkFIFOF;
  FIFOF#(Token) f_reset_rsps <- mkFIFOF;

  function Word fwdSp();
    return byS2.changesSp ? byS2.spAfter
         : byS3.changesSp ? byS3.spAfter
         : sc.sp();
  endfunction

  function Word fwdMsp();
    return byS2.changesMsp ? byS2.mspAfter
         : byS3.changesMsp ? byS3.mspAfter
         : sc.msp();
  endfunction

  function Bool inCache(Word a, Word spb, Word mspb);
    return (a >= spb) && (a < mspb) && (a < sc.fillWatermark());
  endfunction

  // Operand read with the p. 1-1 "operand bypass mechanism": the
  // youngest in-flight writer wins, then the committed stack cache.
  function Tuple2#(Word, Bool) readOp(Operand o, Word spb, Word mspb);
    if (o.kind == OK_IMM)
      return tuple2(o.val, True);
    else begin
      Word a = (o.kind == OK_STACK) ? spb + o.val : o.val;
      if (byS2.we && (byS2.addr == a))
        return tuple2(byS2.data, True);
      else if (byS3.we && (byS3.addr == a))
        return tuple2(byS3.data, True);
      else
        return tuple2(sc.read(a, spb, mspb), inCache(a, spb, mspb));
    end
  endfunction

  function Word opAddr(Operand o, Word spb) =
    (o.kind == OK_STACK) ? spb + o.val : o.val;

  function Bool needsSrc(HobbitOp op) =
    op == OP_MOV || op == OP_ADD || op == OP_SUB || op == OP_ADD3 ||
    op == OP_CMPEQ || op == OP_CMPGT;

  function Bool needsDst(HobbitOp op) =
    op == OP_ADD || op == OP_SUB || op == OP_ADD3 ||
    op == OP_CMPEQ || op == OP_CMPGT;

  function EuS1Out mkOut(DecInstEntry e, Word pc, Word spb, Word mspb,
                         Word srcV, Word dstV, Word retPc,
                         Bool miss, Bit#(4) dcmp);
    let d = e.d;
    Word base = pc + plenBytes(d.plen);
    // A conditional jump issued three or more instructions after its
    // compare resolves in EU_S1: the committed flag is already there,
    // so a misprediction costs no squashed slot (Table 4-35).
    Word npc = e.nextPc;
    if (isCondJumpOp(d.op) && (dcmp >= 2)) begin
      Bool taken = branchTaken(d.op, (psw[4] == 1'b1));
      npc = (taken == predictedTaken(d.op)) ? e.nextPc : e.altNextPc;
    end
    Bool takenGuess = isCondJumpOp(d.op) ? predictedTaken(d.op) : False;
    Word extra = extraCycles(e, spb, mspb, mcyc, takenGuess, dcmp);
    return EuS1Out { e: e, pc: pc, spBefore: spb, mspBefore: mspb,
                     srcVal: srcV, dstVal: dstV, retPc: retPc,
                     base: base, nextPc: npc, sinceCmp: dcmp,
                     extra: extra, operandMiss: miss };
  endfunction

  function EuS1Out curOut();
    let m = ic.lookup(pcR);
    if (!isValid(m))
      return unpack(0);
    else begin
      let e = validValue(m);
      let d = e.d;
      Word spb = fwdSp();
      Word mspb = fwdMsp();
      Word srcV = 0;
      Word dstV = 0;
      Word retPc = 0;
      Bool miss = False;
      if (d.tr == TR_NONE) begin
        if (needsSrc(d.op)) begin
          match { .v, .h } = readOp(d.src, spb, mspb);
          srcV = v; miss = miss || !h;
        end
        if (needsDst(d.op)) begin
          match { .v, .h } = readOp(d.dst, spb, mspb);
          dstV = v; miss = miss || !h;
        end
        if (d.op == OP_RETURN) begin
          Word a = spb + d.src.val;
          if (byS2.we && (byS2.addr == a)) begin
            retPc = byS2.data;
          end else if (byS3.we && (byS3.addr == a)) begin
            retPc = byS3.data;
          end else begin
            retPc = sc.read(a, spb, mspb);
            miss = miss || !inCache(a, spb, mspb);
          end
        end
      end
      return mkOut(e, pcR, spb, mspb, srcV, dstV, retPc, miss, sinceCmp);
    end
  endfunction

  // The one rule this stage runs on its own: own the slot.  With the
  // slot empty it first waits out the issue interlock, then presents the
  // decoded entry for pcR -- starting the single fetch that will install
  // it when the decoded store has no entry yet.  The guard is one
  // predicate and the body writes only block/fullR (plus the store's
  // fetch request), so EU_S1's handoff (`deq`, `redirect`) and this rule
  // are always mutually exclusive: deq/redirect need a populated slot or
  // a squash, and neither is true here.
  rule present (active && !squash && !fullR && !eventActive &&
                (pcR < pcLimit));
    if (block != 0)
      block <= block - 1;
    else if (isValid(ic.lookup(pcR)))
      fullR <= True;
    else begin
      ic.fill(pcR);
    end
  endrule

  rule rl_reset;
    f_reset_reqs.deq;
    active   <= False;
    fullR    <= False;
    block    <= 0;
    sinceCmp <= 0;
    f_reset_rsps.enq(?);
  endrule

  method Action start(Word pc);
    pcR      <= pc;
    active   <= True;
    fullR    <= False;
    block    <= 0;
    sinceCmp <= 0;
  endmethod

  method Action stop();
    active <= False;
  endmethod

  method Bool notEmpty() = fullR;

  // Probe layout, bits 41..34 of dbgState: {active, full, blocked,
  // squash, lookupValid, 3'b0}.  `full` replaces the retired `stall`
  // register: the slot flag is the stage's only back-pressure state.
  method Bit#(8) dbgS1 = { pack(active), pack(fullR), pack(block != 0),
                           pack(squash), pack(isValid(ic.lookup(pcR))), 3'b0 };

  method EuS1Out out() = curOut();

  method Word pc() = pcR;

  // The state advance the orchestrator performs when EU_S2 takes the
  // slot.  It writes every register `present` can write, so the two must
  // never need to fire together -- and they cannot: `present` requires
  // an empty slot and this method is called on a full one.
  method Action deq();
    fullR <= False;
    let o = curOut();
    pcR      <= o.nextPc;
    block    <= o.extra;
    sinceCmp <= isCompareOp(o.e.d.op) ? 0
              : ((sinceCmp == 15) ? 15 : sinceCmp + 1);
  endmethod

  // A squash does not go through `deq`: it must redirect even when the
  // slot is empty.  The orchestrator calls this from a rule guarded by
  // `squash`, which is exactly the complement of `present`'s guard.
  method Action redirect(Word target);
    fullR    <= False;
    pcR      <= target;
    block    <= 0;
    sinceCmp <= 0;
  endmethod

  interface Server server_reset;
    interface Put request  = toPut(f_reset_reqs);
    interface Get response = toGet(f_reset_rsps);
  endinterface
endmodule

// ---------------------------------------------------------------------
// EU_S2: execute.  The ALU, PSW.F, the stack pointers and the branch
// resolution live here.
// ---------------------------------------------------------------------
typedef struct {
  DecInstEntry e;
  Word   pc;
  Word   spBefore;
  Word   mspBefore;
  Word   spAfter;
  Word   mspAfter;
  Word   base;
  WrInfo wr;
  Word   nextPc;
  Bool   squash;       // misprediction resolved in this stage
  Word   redirectPc;
  Word   occ;
  Bit#(4) sinceCmp;
  Bool   flagValid;
  Bool   flagValue;
  Bool   foldMis;      // compare-host folded branch mispredicted
  Word   foldRedirect;
  ScCmd  cmd;
} EuS2Out deriving (Bits);

interface HobbitEuS2;
  interface Server#(Token, Token) server_reset;
  method Action start();
  method Action enq(EuS1Out d);
  method Bool canAccept();
  method EuS2Out out;
  method Action deq;
  method Bool notEmpty;
  // Harness probe: the stage holds a record in either slot.
  method Bool occupied();
  method EuBypass bypass;
  method Bool squash;
  method Word redirectPc;
  method Action flush();
endinterface

module mkHobbitEuS2#(Reg#(Word) psw)(HobbitEuS2);
  // structure follows Flute (Bluespec, Inc., Apache-2.0) — see
  // docs/bluespec_architecture.md.
  //
  // The stage holds one input slot and one output slot as plain
  // full/data register pairs, not FIFOFs.  A FIFOF's `first` is a method
  // *guarded by notEmpty*, and Bluespec conjoins a guarded method's
  // condition into every rule that may call it -- including the rules of
  // a consumer that only wants `squash`/`bypass` when the slot happens to
  // be occupied.  That would make EU_S1's fetch depend on this stage's
  // occupancy (the boot deadlock).  A register whose validity is a
  // separate flag has no implicit condition, so the consumers' own guards
  // are the whole story.
  Reg#(Bool) inFull  <- mkReg(False);
  Reg#(EuS1Out) inD  <- mkRegU;
  Reg#(Bool) outFull <- mkReg(False);
  Reg#(EuS2Out) outD <- mkRegU;
  Wire#(Bool) flushW <- mkDWire(False);

  FIFOF#(Token) f_reset_reqs <- mkFIFOF;
  FIFOF#(Token) f_reset_rsps <- mkFIFOF;

  function Word opAddr2(Operand o, Word spb) =
    (o.kind == OK_STACK) ? spb + o.val : o.val;

  function WrInfo writeInfoOf(EuS1Out i);
    let d = i.e.d;
    if (d.tr != TR_NONE)
      return WrInfo { we: True, addr: i.spBefore, data: d.pc };
    else case (d.op)
      OP_MOV:  return WrInfo { we: True, addr: opAddr2(d.dst, i.spBefore),
                               data: i.srcVal };
      OP_ADD:  return WrInfo { we: True, addr: opAddr2(d.dst, i.spBefore),
                               data: i.dstVal + i.srcVal };
      OP_SUB:  return WrInfo { we: True, addr: opAddr2(d.dst, i.spBefore),
                               data: i.dstVal - i.srcVal };
      OP_ADD3: return WrInfo { we: True, addr: i.spBefore + 4,
                               data: i.dstVal + i.srcVal };
      OP_CALL: return WrInfo { we: True, addr: i.spBefore, data: i.base };
      default: return WrInfo { we: False, addr: 0, data: 0 };
    endcase
  endfunction

  function BoxOp boxOpOf(HobbitOp op);
    case (op)
      OP_ENTER:  return BX_ENTER;
      OP_CATCH:  return BX_CATCH;
      OP_POPN:   return BX_POPN;
      OP_RETURN: return BX_RETURN;
      default:   return BX_NONE;
    endcase
  endfunction

  function Word stackTarget(EuS1Out i);
    let d = i.e.d;
    case (d.op)
      OP_ENTER:  return enterTarget(d, i.spBefore);
      OP_CATCH:  return (d.src.kind == OK_STACK) ? i.spBefore + d.src.val
                                                 : d.src.val;
      OP_POPN:   return d.src.val;
      OP_RETURN: return d.src.val;
      default:   return 0;
    endcase
  endfunction

  // The one rule this stage runs on its own: take the input slot, do the
  // work, fill the output slot.  `enq` needs an empty input slot and this
  // rule needs a full one; this rule needs an empty output slot and `deq`
  // needs a full one -- so no two of them ever write the same register in
  // the same clock.
  rule step (flushW || (inFull && !outFull));
   if (flushW) begin
    inFull  <= False;
    outFull <= False;
   end else begin
    let i = inD;
    let e = i.e;
    let d = e.d;
    Bool trap = (d.tr != TR_NONE);
    Bool cmp = isCompareOp(d.op) && !trap;
    Bool flagNew = flagAfterOp(d.op, i.srcVal, i.dstVal, (psw[4] == 1'b1));
    SpMsp after = trap ? SpMsp { sp: i.spBefore, msp: i.mspBefore }
                       : archAfterSpMsp(d, i.spBefore, i.mspBefore);
    WrInfo wr = writeInfoOf(i);

    // Branch resolution in this stage: RETURN's indirect target and a
    // conditional jump two instructions after its compare.
    Bool squashR = False;
    Word redirectR = 0;
    Word occ = 1 + i.extra;
    Bool foldMisR = False;
    Word foldRedirR = 0;

    if (!trap) begin
      if (d.op == OP_RETURN) begin
        squashR   = True;
        redirectR = i.retPc;
      end else if (isCondJumpOp(d.op) && !d.fold) begin
        if (i.sinceCmp == 1) begin
          Bool taken = branchTaken(d.op, (psw[4] == 1'b1));
          if (taken != predictedTaken(d.op)) begin
            squashR   = True;
            redirectR = e.altNextPc;
            occ       = occ + 1;          // Table 4-35: 2
          end
        end
        // sinceCmp == 0 resolves in EU_S3; sinceCmp >= 2 in EU_S1.
      end else if (d.fold && isCompareOp(d.op)) begin
        // A folded branch into the compare itself: the flag is the
        // compare's result.  The branch's own record carries the
        // Table 4-35 cost; the host keeps its one slot.
        Bool taken = branchTaken(d.foldOp, flagNew);
        if (taken != predictedTaken(d.foldOp)) begin
          foldMisR   = True;
          foldRedirR = taken ? d.foldTarget : d.foldAfter;
        end
      end
    end

    ScCmd cmd = ScCmd { op: trap ? BX_NONE : boxOpOf(d.op),
                        we: wr.we, waddr: wr.addr, wdata: wr.data,
                        spBefore: i.spBefore, mspBefore: i.mspBefore,
                        spAfter: after.sp, mspAfter: after.msp,
                        target: stackTarget(i),
                        stackMode: (d.src.kind == OK_STACK) };

    outD <= EuS2Out { e: e, pc: i.pc,
                      spBefore: i.spBefore, mspBefore: i.mspBefore,
                      spAfter: after.sp, mspAfter: after.msp,
                      base: i.base, wr: wr, nextPc: i.nextPc,
                      squash: squashR, redirectPc: redirectR,
                      occ: occ, sinceCmp: i.sinceCmp,
                      flagValid: cmp, flagValue: flagNew,
                      foldMis: foldMisR, foldRedirect: foldRedirR,
                      cmd: cmd };
    outFull <= True;
    inFull  <= False;
   end
  endrule

  rule rl_reset;
    f_reset_reqs.deq;
    f_reset_rsps.enq(?);
  endrule

  method Action start();
    inFull  <= False;
    outFull <= False;
  endmethod

  method Action enq(EuS1Out d);
    inD    <= d;
    inFull <= True;
  endmethod
  method Bool canAccept() = !inFull;
  method EuS2Out out() = outD;
  method Action deq();
    outFull <= False;
  endmethod
  method Bool notEmpty() = outFull;
  method Bool occupied() = inFull || outFull;

  method EuBypass bypass();
    if (!outFull) return noBypass();
    else begin
      let o = outD;
      return EuBypass { valid: True, we: o.wr.we,
                        addr: o.wr.addr, data: o.wr.data,
                        changesSp: isSpOp(o.e.d.op),
                        spAfter: o.spAfter,
                        changesMsp: isSpOp(o.e.d.op),
                        mspAfter: o.mspAfter };
    end
  endmethod

  method Bool squash() = outFull && outD.squash;
  method Word redirectPc() = outFull ? outD.redirectPc : 0;
  method Action flush();
    flushW <= True;
  endmethod

  interface Server server_reset;
    interface Put request  = toPut(f_reset_reqs);
    interface Get response = toGet(f_reset_rsps);
  endinterface
endmodule

// ---------------------------------------------------------------------
// EU_S3: write back, retire and emit the trace record.
// ---------------------------------------------------------------------
interface HobbitEuS3;
  interface Server#(Token, Token) server_reset;
  method Action start();
  method Action enq(EuS2Out d);
  method Bool canAccept();
  method Bool notEmpty();
  method Hri out();
  method Action deq();
  method Bool occupied();
  method Bool pswF();
  method Maybe#(Bool) flagWrite();
  method Bool trapPending();
  method TrapReason trapReason();
  method Word trapPc();
  method Parcel trapInsn0();
  method Bool trapNiladic();
  method Action clearTrap();
  method Action flush();
  method Word lastPc();
  method EuBypass bypass();
  method Bool squash();
  method Word redirectPc();
  method Bool faulted();
  method Word faultPc();
  method Bit#(32) instrs();
  method Bit#(32) folded();
endinterface

module mkHobbitEuS3#(HobbitStackCache sc, Reg#(Word) psw,
                     Bool eventsOn)(HobbitEuS3);
  // structure follows Flute (Bluespec, Inc., Apache-2.0) — see
  // docs/bluespec_architecture.md.  The HRI record is the trace port
  // (Flute's g_pc_trace analogue), not datapath.

  // Input slot as a full/data register pair for the same reason as EU_S2:
  // `bypass`, `squash` and `redirectPc` are read by EU_S1's rules, and a
  // FIFOF's guarded `first` would conjoin this stage's occupancy into
  // them.  `traceQ` keeps its FIFOF shape: every rule that touches its
  // `first` is genuinely guarded by its `notEmpty`.
  Reg#(Bool) inFull <- mkReg(False);
  Reg#(EuS2Out) inD <- mkRegU;
  FIFOF#(Hri) traceQ <- mkSizedFIFOF(64);
  Reg#(Bool) faultedR <- mkReg(False);
  Reg#(Word) faultPcR <- mkReg(0);
  Reg#(Bit#(32)) ninstr <- mkReg(0);
  Reg#(Bit#(32)) nfold <- mkReg(0);
  Reg#(Bool) haltR <- mkReg(False);
  Reg#(Word) lastPcR <- mkReg(0);
  Reg#(Bool) trapPendR <- mkReg(False);
  Reg#(TrapReason) trapReasonR <- mkReg(TR_NONE);
  Reg#(Word) trapPcR <- mkReg(0);
  Reg#(Parcel) trapInsn0R <- mkReg(0);
  Reg#(Bool) trapNiladicR <- mkReg(False);

  // The compare's flag write and an event's pipeline flush are one-cycle
  // wires so the core's PSW rule sees them in the commit cycle, and the
  // commit rule can be blocked in the flush cycle.
  Wire#(Maybe#(Bool)) flagWW <- mkDWire(tagged Invalid);
  Wire#(Bool) flushW <- mkDWire(False);

  // A folded branch record follows its host in the trace.
  Reg#(Maybe#(Hri)) pendFold <- mkReg(tagged Invalid);

  FIFOF#(Token) f_reset_reqs <- mkFIFOF;
  FIFOF#(Token) f_reset_rsps <- mkFIFOF;

  // A conditional jump issued immediately after its compare resolves
  // here, because the compare's PSW.F write and this stage's read are
  // the same edge: two younger slots are squashed (Table 4-35's 3).
  //
  // The same machinery retires a folded branch: it is one record with
  // cyc 0 (p. 4-3 note), and a misprediction costs the branch record 3
  // (Table 4-35's only printed row for it), on the flag below.
  //
  // The flag a folded branch tests: the host's own result when the host
  // is a compare, and the committed PSW.F otherwise.  A host that is not
  // a compare issues at least one slot after its compare, so by the time
  // it reaches this stage the compare's commit has written pswFR (a fold
  // into the compare itself cannot use pswFR -- the host is the writer --
  // and EU_S2 resolves that case, reporting it as foldMis).
  function Bool foldFlagValue(EuS2Out o) =
    isCompareOp(o.e.d.op) ? o.flagValue : (psw[4] == 1'b1);

  function Bool foldTaken(EuS2Out o) =
    branchTaken(o.e.d.foldOp, foldFlagValue(o));

  function Bool foldMispredicted(EuS2Out o) =
    o.e.d.fold &&
    (o.foldMis || (foldTaken(o) != predictedTaken(o.e.d.foldOp)));

  function Bool squashOf(EuS2Out o);
    if (o.e.d.tr != TR_NONE) return False;
    else if (isCondJumpOp(o.e.d.op) && !o.e.d.fold &&
             (o.sinceCmp == 0)) begin
      Bool taken = branchTaken(o.e.d.op, (psw[4] == 1'b1));
      return taken != predictedTaken(o.e.d.op);
    end else
      return foldMispredicted(o);
  endfunction

  function Word redirectOf(EuS2Out o);
    if (isCondJumpOp(o.e.d.op) && !o.e.d.fold &&
        (o.sinceCmp == 0)) begin
      // A misprediction means the actual path is the alternate one.
      return o.e.altNextPc;
    end else if (o.e.d.fold)
      return foldTaken(o) ? o.e.d.foldTarget : o.e.d.foldAfter;
    else
      return 0;
  endfunction

  function Hri hostRecord(EuS2Out o, Word cyc);
    let d = o.e.d;
    return Hri { valid: True, pc: d.pc, insn0: d.insn0, insn1: d.insn1,
                 sp_before: o.spBefore, sp_after: o.spAfter,
                 msp_before: o.mspBefore, msp_after: o.mspAfter,
                 mem_we: o.wr.we, mem_addr: o.wr.addr,
                 mem_wdata: o.wr.data,
                 mem_wmask: o.wr.we ? 8'h0F : 8'h00,
                 trap: (d.tr != TR_NONE), cyc: cyc };
  endfunction

  function Hri foldRecord(EuS2Out o, Word cyc);
    let d = o.e.d;
    return Hri { valid: True, pc: d.foldPc, insn0: d.foldInsn0, insn1: 0,
                 sp_before: o.spBefore, sp_after: o.spAfter,
                 msp_before: o.mspBefore, msp_after: o.mspAfter,
                 mem_we: False, mem_addr: 0, mem_wdata: 0,
                 mem_wmask: 0, trap: False, cyc: cyc };
  endfunction

  rule commit (!haltR && traceQ.notFull && !flushW);
    if (pendFold matches tagged Valid .r) begin
      traceQ.enq(r);
      pendFold <= tagged Invalid;
    end else if (inFull) begin
      let o = inD;
      let d = o.e.d;
      // A jump resolved in this stage pays the two squashed slots
      // (Table 4-35's 3) on its own record.  A folded branch's cost is
      // the branch record's, which foldRecord carries; the host keeps its
      // one slot (p. 4-3 note), so a fold never adds to occ.
      Bool lateMis = isCondJumpOp(d.op) && !d.fold && (o.sinceCmp == 0) &&
                     squashOf(o);
      Word occ = o.occ + (lateMis ? 2 : 0);
      traceQ.enq(hostRecord(o, occ));
      if (d.fold)
        pendFold <= tagged Valid (foldRecord(o, foldMispredicted(o) ? 3 : 0));
      if (o.flagValid) flagWW <= tagged Valid o.flagValue;
      ninstr <= ninstr + 1;
      if (d.fold) nfold <= nfold + 1;
      lastPcR <= d.pc;
      if (d.tr != TR_NONE && eventsOn) begin
        // A trap has no architectural write and must not move SP/MSP;
        // noScCmd() carries zero pointers, so keep the before values.
        let k = noScCmd();
        k.spBefore  = o.spBefore;
        k.mspBefore = o.mspBefore;
        k.spAfter   = o.spBefore;
        k.mspAfter  = o.mspBefore;
        sc.commit(k);
      end else
        sc.commit(o.cmd);
      inFull <= False;
      if (d.tr != TR_NONE) begin
        if (eventsOn) begin
          trapPendR    <= True;
          trapReasonR  <= d.tr;
          trapPcR      <= d.pc;
          trapInsn0R   <= d.insn0;
          trapNiladicR <= (d.insn0[15:10] == 6'b001011) &&
                          (d.insn0[9:0] >= 10'h200);
        end else begin
          faultedR <= True;
          faultPcR <= d.pc;
          haltR    <= True;
          $fwrite(stderr, "TRAP pc=0x%08x: %s\n", d.pc, trapText(d.tr));
        end
      end
    end
  endrule

  rule rl_reset;
    f_reset_reqs.deq;
    faultedR <= False;
    faultPcR <= 0;
    ninstr   <= 0;
    nfold    <= 0;
    haltR    <= False;
    pendFold <= tagged Invalid;
    inFull   <= False;
    trapPendR <= False;
    trapReasonR <= TR_NONE;
    trapPcR <= 0;
    trapInsn0R <= 0;
    trapNiladicR <= False;
    lastPcR <= 0;
    traceQ.clear;
    f_reset_rsps.enq(?);
  endrule

  method Action start();
    faultedR <= False;
    faultPcR <= 0;
    ninstr   <= 0;
    nfold    <= 0;
    haltR    <= False;
    pendFold <= tagged Invalid;
    inFull   <= False;
    trapPendR <= False;
    trapReasonR <= TR_NONE;
    trapPcR <= 0;
    trapInsn0R <= 0;
    trapNiladicR <= False;
    lastPcR <= 0;
    traceQ.clear;
  endmethod

  // The handoff into this stage.  `enq` needs an empty slot and the
  // commit rule needs a full one, so they never collide.
  method Action enq(EuS2Out d);
    inD    <= d;
    inFull <= True;
  endmethod
  method Bool canAccept() = !inFull;
  method Bool notEmpty() = traceQ.notEmpty;
  // Harness probe: any record this stage still holds, in either slot.
  method Bool occupied() = inFull || traceQ.notEmpty;
  method Hri out() = traceQ.first;
  method Action deq() = traceQ.deq;
  method Bool pswF() = (psw[4] == 1'b1);
  method Maybe#(Bool) flagWrite() = flagWW;
  method Bool trapPending() = trapPendR;
  method TrapReason trapReason() = trapReasonR;
  method Word trapPc() = trapPcR;
  method Parcel trapInsn0() = trapInsn0R;
  method Bool trapNiladic() = trapNiladicR;
  method Action clearTrap();
    trapPendR <= False;
  endmethod
  method Action flush();
    flushW <= True;
  endmethod
  method Word lastPc() = lastPcR;

  method EuBypass bypass();
    if (!inFull) return noBypass();
    else begin
      let o = inD;
      return EuBypass { valid: True, we: o.wr.we,
                        addr: o.wr.addr, data: o.wr.data,
                        changesSp: isSpOp(o.e.d.op),
                        spAfter: o.spAfter,
                        changesMsp: isSpOp(o.e.d.op),
                        mspAfter: o.mspAfter };
    end
  endmethod

  method Bool squash() = inFull && squashOf(inD);
  method Word redirectPc() = inFull ? redirectOf(inD) : 0;
  method Bool faulted() = faultedR;
  method Word faultPc() = faultPcR;
  method Bit#(32) instrs() = ninstr;
  method Bit#(32) folded() = nfold;

  interface Server server_reset;
    interface Put request  = toPut(f_reset_reqs);
    interface Get response = toGet(f_reset_rsps);
  endinterface
endmodule

// ---------------------------------------------------------------------
// Core: wire the boxes and the three EU stages, and drain the trace.
//
// PSW bit 16 (V) selects translation (p. 1-14, p. 2-1).  The stack
// cache and the prefetch buffer see translating memory faces; a fault
// latches in the data face (or becomes a TR_FETCH_FAULT in the PDU) and
// raises the p. 1-38 event sequence instead of the model's loud trap.
// `eventsOn = False` (mkHobbitCore) keeps the earlier diagnostic
// behaviour for the fixed oracles; `eventsOn = True`
// (mkHobbitCoreMmu) is the integrated MMU/event path.
// ---------------------------------------------------------------------
module mkHobbitCoreImpl#(HobbitMem mem, Word pcLimit, MemCycles m,
                         MmuTables tbl, Bool eventsOn)(HobbitCore);

  Reg#(Word) pswR <- mkReg(0);
  Reg#(Word) vbR <- mkReg(0);
  Reg#(Bit#(3)) ilR <- mkReg(7);
  Reg#(Bool) eventActiveR <- mkReg(False);
  Reg#(Bool) traceFired <- mkReg(False);
  Reg#(Bool) eventTakenR <- mkReg(False);
  Reg#(Word) eventPcR <- mkReg(0);
  Reg#(Bit#(4)) eventIdR <- mkReg(0);
  Reg#(Word) savedPcR <- mkReg(0);
  Reg#(Word) savedPswR <- mkReg(0);

  Wire#(Maybe#(Word)) setPswW <- mkDWire(tagged Invalid);
  Wire#(Maybe#(Word)) startPswW <- mkDWire(tagged Invalid);
  Wire#(Maybe#(Word)) eventPswW <- mkDWire(tagged Invalid);

  Reg#(Hri) present <- mkReg(unpack(0));
  Reg#(Bool) presentValid <- mkReg(False);

  HobbitMmu mmu <- mkHobbitMmu(tbl);
  HobbitMmuMem textFace <- mkHobbitMmuMem(mem, mmu, True, pswR);
  HobbitMmuMem dataFace <- mkHobbitMmuMem(mem, mmu, False, pswR);
  HobbitEventMem evmem <- mkHobbitEventMem;
  HobbitEvents events <- mkHobbitEvents(evmem, mmu);

  HobbitPrefetch pf <- mkHobbitPrefetch(textFace.mem, mmu, pswR);
  HobbitPdu pdu <- mkHobbitPdu(pf);
  HobbitDecodeStore ic <- mkHobbitDecodeStore(pdu);
  HobbitStackCache sc <- mkHobbitStackCache(dataFace.mem, m);

  // Instantiate the stages downstream-first so the bypass and flag
  // expressions can be passed as Flute passes stage2.out.bypass.
  HobbitEuS3 s3 <- mkHobbitEuS3(sc, pswR, eventsOn);
  HobbitEuS2 s2 <- mkHobbitEuS2(pswR);

  // EU_S3 resolves the youngest misprediction (a jump right after its
  // compare); otherwise EU_S2's.
  Bool squash = s2.squash || s3.squash;
  Word redirectPc = s3.squash ? s3.redirectPc : s2.redirectPc;

  HobbitEuS1 s1 <- mkHobbitEuS1(ic, sc, m, s2.bypass, s3.bypass, pswR,
                                squash, pcLimit, eventActiveR);

  // ---- PSW ownership ------------------------------------------------
  // One rule writes PSW.  A compare's F bit arrives on EU_S3's DWire in
  // the commit cycle, so a compare-adjacent jump sees it in the next
  // cycle (Table 4-35's structural 3).  A start or a testbench write
  // overrides; an event's PSW &= 0xFFFF0000 (p. 1-37/1-38) is applied by
  // the finish rule.
  rule pswUpdate;
    if (isValid(startPswW))
      pswR <= validValue(startPswW);
    else if (isValid(setPswW))
      pswR <= validValue(setPswW);
    else if (isValid(eventPswW))
      pswR <= validValue(eventPswW);
    else if (isValid(s3.flagWrite()))
      pswR <= (pswR & 32'hFFFFFFEF) |
              (validValue(s3.flagWrite()) ? 32'h10 : 32'd0);
  endrule

  // ---- S1 -> S2, the squash redirect, and S2 -> S3 -------------------
  function Action startCoreAt(Word sp, Word msp, Word p, Word pc0) =
    action
      sc.reset(sp, msp);
      ic.reset;
      s2.start;
      s3.start;
      s1.start(pc0);
      events.setIsp(sp);
      events.setShad(sp);
      startPswW <= tagged Valid p;
      presentValid <= False;
      present <= unpack(0);
      eventActiveR <= False;
      eventTakenR <= False;
      traceFired <= False;
    endaction;

  function Action startCore(Word sp, Word msp, Word p) =
    startCoreAt(sp, msp, p, 0);

  function Bool pipelineIdle() =
    !s1.notEmpty && !s2.occupied && !s3.occupied;

  function Bool intWanted() =
    (ilR != 3'b111) && ((ilR == 3'b000) || (ilR < pswR[14:12])) &&
    pipelineIdle();

  function Bool traceWanted() =
    (pswR[7] == 1'b1) && !traceFired && pipelineIdle();

  function Bool eventWanted() =
    eventsOn && !eventActiveR &&
    (s3.trapPending() || dataFace.fault() || intWanted() || traceWanted());

  rule deliver (!eventWanted() && !squash && s1.notEmpty && s2.canAccept);
    s2.enq(s1.out);
    s1.deq;
  endrule

  rule redirect (eventWanted() == False && squash);
    s1.redirect(redirectPc);
  endrule

  rule move2to3 (!eventWanted() && s2.notEmpty && s3.canAccept);
    s3.enq(s2.out);
    s2.deq;
  endrule

  rule stopAtLimit (!eventWanted() && (s1.pc >= pcLimit));
    s1.stop;
  endrule

  // ---- event start / finish -----------------------------------------
  // The causes are all presented; the events box applies the p. 1-40
  // priority.  An interrupt outranks an instruction fault, so its PC is
  // the next instruction; otherwise the faulting instruction's PC (or
  // the p. 1-39 store PC for a data fault) is saved.
  rule startEvent (eventWanted());
    let c = noEventCauses();
    c.psw = pswR;
    c.sp  = sc.sp;
    c.vb  = vbR;
    let tp = s3.trapPending();
    let df = dataFace.fault();
    let iw = intWanted();
    let tw = traceWanted();

    if (iw)
      c.pc = s1.pc;
    else if (tp)
      c.pc = s3.trapPc();
    else if (df)
      c.pc = s3.lastPc();
    else
      c.pc = s1.pc;

    if (tp) begin
      case (s3.trapReason())
        TR_CPU:         c.illegal  = True;
        TR_BAD_LENGTH:  c.illegal  = True;
        TR_BAD_MODE:    c.illegal  = True;
        TR_RETURN_MODE: c.illegal  = True;
        TR_UNIMP: begin
          c.unimp   = True;
          c.niladic = s3.trapNiladic();
        end
        TR_ALIGN:       c.align    = True;
        TR_FETCH_MISS:  c.fetchFault = True;
        TR_FETCH_FAULT: c.fetchFault = True;
        default:        c.illegal  = True;
      endcase
    end
    if (df) begin
      if (dataFace.faultWrite()) c.writeFault = True;
      else                       c.readFault  = True;
      c.va = dataFace.faultAddr();
    end
    if (iw) begin
      c.interrupt = True;
      c.il      = ilR;
    end
    if (tw) c.trace = True;

    events.setShad(sc.shad);
    events.raise(c);
    eventActiveR <= True;
    if (tw) traceFired <= True;
    s1.stop;
    s2.flush;
    s3.flush;
    ic.reset;
    s3.clearTrap;
    dataFace.clearFault;
  endrule

  rule finishEvent (eventActiveR && events.done());
    let r = events.result();
    eventPswW  <= tagged Valid r.newPsw;
    s1.start(r.vector);
    sc.reset(r.newSp, sc.msp);
    events.ack;
    eventActiveR <= False;
    eventTakenR <= r.taken;
    eventPcR    <= r.vector;
    eventIdR    <= r.id;
    savedPcR    <= r.savedPc;
    savedPswR   <= r.savedPsw;
    if (r.newPsw[7] == 1'b0) traceFired <= False;
  endrule

  // ---- retirement presentation --------------------------------------
  rule loadTrace (!presentValid && s3.notEmpty);
    present <= s3.out;
    presentValid <= True;
    s3.deq;
  endrule

  rule retire (presentValid);
    let r = present;
    $display("HRI pc=%04x insn=%04x%04x sp=%08x>%08x msp=%08x>%08x we=%d addr=%08x data=%08x mask=%02x trap=%d cyc=%0d",
             r.pc[15:0], r.insn0, r.insn1,
             r.sp_before, r.sp_after, r.msp_before, r.msp_after,
             pack(r.mem_we), r.mem_addr, r.mem_wdata, r.mem_wmask,
             pack(r.trap), r.cyc);
    presentValid <= False;
  endrule

  method Action prefetchImage();
    pf.startFill();
  endmethod

  method Bool prefetchReady() = pf.ready();

  method Action startPsw(Word sp, Word msp, Word p);
    startCore(sp, msp, p);
  endmethod

  method Action start(Word sp, Word msp);
    startCore(sp, msp, 0);
  endmethod

  method Action startAt(Word pc, Word sp, Word msp, Word psw);
    startCoreAt(sp, msp, 0, pc);
  endmethod

  method Bool halted() = s3.faulted;
  method Bool atLimit() =
    (pcLimit != 32'hFFFFFFFF) && !eventActiveR && (s1.pc >= pcLimit) &&
    !s1.notEmpty && !s2.occupied && !s3.occupied;
  method Bool faulted() = s3.faulted;
  method Word faultPc() = s3.faultPc;
  method Word pc() = s1.pc;

  method Word sp() = sc.sp;
  method Word msp() = sc.msp;
  method Word acc() = sc.read(sc.sp + 4, sc.sp, sc.msp);
  method Word readMem(Word addr) = sc.read(addr, sc.sp, sc.msp);
  method Word cacheWord(Word addr) = sc.cacheWord(addr);
  method Bool cached(Word addr) = sc.cached(addr);

  method Bit#(32) folded() = s3.folded;
  method Bit#(32) refills() = sc.refills;
  method Bit#(32) instrs() = s3.instrs;
  method Word minSp() = sc.minSpSeen;
  method Word maxSp() = sc.maxSpSeen;

  method Bool hriValid() = presentValid;
  method Hri hri() = present;
  method Bool quiescent() = !presentValid && !s3.notEmpty;

  // ---- MMU / event testbench surface (added; no existing method
  // changed).  The machine never calls these.
  method Word psw() = pswR;
  method Action setPsw(Word p);
    setPswW <= tagged Valid p;
    traceFired <= False;
  endmethod
  method Word vb() = vbR;
  method Action setVb(Word v) = action vbR <= v; endaction;
  method Bit#(3) il() = ilR;
  method Action setIl(Bit#(3) v) = action ilR <= v; endaction;
  method Word isp() = events.isp;
  method Word shad() = events.shad;
  method Action setIsp(Word v) = events.setIsp(v);
  method Action setShad(Word v) = events.setShad(v);
  method Action flushPte(Word va) = mmu.flushPte(va);
  method Action flushTlb() = mmu.flushAll;
  method Action setStb(Word v) = mmu.setStb(v);
  method Bit#(32) mmuHits() = mmu.hits;
  method Bit#(32) mmuMisses() = mmu.misses;
  method Bit#(32) mmuWalks() = mmu.walks;
  method Bit#(32) mmuFaults() = mmu.faults;
  method Bool eventTaken() = eventTakenR;
  method Word eventPc() = eventPcR;
  method Bit#(4) eventId() = eventIdR;
  method Word savedPc() = savedPcR;
  method Word savedPsw() = savedPswR;
  method Bool eventActive() = eventActiveR;
  method Word eventMemRead(Word a) = events.memRead(a);
  method Action eventMemWrite(Word a, Word v) = events.memWrite(a, v);

  method Bit#(64) dbgState() =
    { zeroExtend(s1.pc[15:0]), pack(s2.notEmpty), pack(s3.notEmpty),
      pack(ic.filling), pack(pdu.outValid), pack(pdu.accepting),
      pack(pf.ready), s1.dbgS1, 34'b0 };

endmodule

// The fixed oracles keep the earlier loud-trap behaviour and physical
// memory; the integrated MMU/event path is a separate constructor.
module mkHobbitCore#(HobbitMem mem, Word pcLimit, MemCycles m)(HobbitCore);
  MmuTables tbl <- mkMmuTablesNull();
  HobbitCore c <- mkHobbitCoreImpl(mem, pcLimit, m, tbl, False);
  return c;
endmodule

module mkHobbitCoreMmu#(HobbitMem mem, Word pcLimit, MemCycles m,
                        MmuTables tbl)(HobbitCore);
  HobbitCore c <- mkHobbitCoreImpl(mem, pcLimit, m, tbl, True);
  return c;
endmodule

endpackage
