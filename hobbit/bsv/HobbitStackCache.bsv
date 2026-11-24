// HobbitStackCache.bsv -- the 64-register stack cache and integer
// accumulator as a request/response box with two read ports and one
// write port per clock.
//
// Figure 1-1 (printed p. 1-2) prints "STACK CACHE 64x32x2 bits" and a
// 32-bit path to the execution unit; p. 1-1 calls it a "256 byte stack
// cache that holds top of user stack".  The box exposes two
// combinational read ports (read/read2) and one registered write port.
// The EU reads its two operands (EU_S1) and writes its destination
// (EU_S3) in the same clock, and a CATCH refill can write a word while
// the EU reads one -- the cases the single-writer sequencer could not
// express.  An indirect operand's pointed-to word is read in EU_S2; the
// two stages' reads never fall in the same clock.  A flush reads the
// array and writes memory, so the EU's write and the flush's read also
// overlap.
//
// Documented behaviour modelled here (printed pages of the January 1993
// Programmer's Reference Manual):
//
//   * 64 words, circular buffer, word addressable, a hit when
//     SP <= address < MSP (p. 1-5, p. 1-12).
//   * the integer accumulator is the word at CSP+4; CSP is SP in this
//     milestone (p. 1-7, Figure 1-4).
//   * CALL writes the return PC at CSP (p. 3-9).
//   * ENTER sets SP to its target and runs the p. 3-19/3-20 flush loop:
//     "MSP -= 16" while MSP is more than 256 bytes above the target, or
//     every valid quad-word for a non-stack-offset ENTER.  The flush is
//     Q_CYC = 4 clock cycles per quad-word because the synchronous bus
//     moves one 32-bit word per clock (the A/D/Q choice in HobbitTypes,
//     p. 4-2 and p. A-1).  Eight quads therefore occupy 32 clocks.
//   * CATCH fills quad-words upward from MSP until it reaches the target
//     or the cache holds SCSIZE = 256 bytes (p. 3-10/3-11).  The
//     architectural MSP reaches its final value in the CATCH's own
//     cycle; the refill reads one word per clock in the background, and
//     reads or writes above the fill watermark go to memory.  This is
//     what lets Table 4-36 price CATCH at 1 (printed p. 4-5) even though
//     the box needs several clocks to move the data: the p. 4-1
//     assumptions charge no fetch or operand delay for a stack-cache
//     fill, and the refill creates no architectural value.
//   * POPN sets SP += src, and MSP = SP when SP exceeds MSP (p. 3-38).
//   * RETURN reads the new PC at CSP+src, then sets SP += src with the
//     low four bits of src ignored, and MSP = SP when SP exceeds MSP
//     (p. 3-39/3-40).
//
// Structure follows Flute (Bluespec, Inc., Apache-2.0) -- see
// docs/bluespec_architecture.md: the multi-cycle datapath is a box behind
// a request/response interface, never inlined into the EU stages.

package HobbitStackCache;

import Vector::*;
import FIFOF::*;
import RegFile::*;
import HobbitTypes::*;

typedef enum { SC_IDLE, SC_FLUSH, SC_REFILL } ScState deriving (Eq, Bits);

// What this cycle's instruction asks the box to do.  BX_WRITE carries
// the one architectural word write; the others are the stack class.
typedef enum {
  BX_NONE,
  BX_WRITE,
  BX_ENTER,
  BX_CATCH,
  BX_POPN,
  BX_RETURN
} BoxOp deriving (Eq, Bits);

// One command per retired instruction.  The EU computes the architectural
// after-values with archAfterSpMsp() (HobbitTypes) and the box installs
// them, so the box and the HRI record can never disagree.
typedef struct {
  BoxOp op;
  Bool  we;          // the instruction's architectural word write
  Word  waddr;
  Word  wdata;
  Word  spBefore;
  Word  mspBefore;
  Word  spAfter;
  Word  mspAfter;
  Word  target;      // ENTER/CATCH target or POPN/RETURN offset
  Bool  stackMode;   // ENTER's stack-offset mode
} ScCmd deriving (Bits);

function ScCmd noScCmd() =
  ScCmd { op: BX_NONE, we: False, waddr: 0, wdata: 0,
          spBefore: 0, mspBefore: 0, spAfter: 0, mspAfter: 0,
          target: 0, stackMode: False };

interface HobbitStackCache;
  method Word sp();
  method Word msp();
  method Word csp();
  method Word shad();

  // The read port.  `lo` and `hi` are the architectural bounds the EU
  // has already forwarded past the instructions in flight; the box adds
  // its refill watermark.  A miss returns 0: the caller tests the window
  // itself and takes a word outside it from memory (memReq below).
  method Word read(Word addr, Word lo, Word hi);
  // Second read port: the printed stack cache is "64x32x2" (Figure 1-1,
  // p. 1-2), and an instruction's two memory operands are read in the
  // same cycle.
  method Word read2(Word addr, Word lo, Word hi);

  // The write port and the pointer op, one command per retired
  // instruction.  The command reaches the box's single state rule
  // through a Wire in the same clock, so the box remains the only
  // writer of its array and its pointers.
  method Action commit(ScCmd c);

  method Action reset(Word sp, Word msp);

  method Bool busy();
  method Bool flushing();
  method Bool refilling();
  method Bit#(32) refills();
  method Word minSpSeen();
  method Word maxSpSeen();
  // The testbench probe reads the array through the box's read path; the
  // two printed ports are shared with the EU stages, whose reads and this
  // probe never fall in the same clock (the probe is used after the run).
  method Word cacheWord(Word addr);
  method Bool cached(Word addr);
  method Word fillWatermark();

  // The operand path to external memory.  A stack access hits the cache
  // only inside the printed window, SP <= address < MSP with
  // MSP <= SP + 256 (p. 1-5, p. 1-12); every other operand -- an absolute
  // address, a pointer's target, a caller's frame above MSP after a large
  // ENTER -- is a word of memory, and the box owns the one data-memory
  // read port (the same registered readReq/readData pair the CATCH
  // refill uses).  EU_S1 asks for a word with memReq while memIdle; the
  // box names the word whose data is on the port in the next clock with
  // memLive/memData.  One word per clock, so a memory operand costs the
  // model's A = 1 cycle per word fetched (the p. 4-2 choice, HobbitTypes).
  method Action memReq(Word addr);
  method Maybe#(Word) memLive();
  method Word memData();
  method Bool memIdle();

  // The same read port, lent to the prefetch buffer's fill (instruction
  // words).  The prefetch buffer translates the address itself (a text
  // reference) and asks for the *physical* word, which goes out on the
  // untranslated memory.  Priority on the port: the CATCH refill, then
  // an operand, then the prefetch.
  interface MemPort textPort;
endinterface

module mkHobbitStackCache#(HobbitMem mem, MemCycles m)(HobbitStackCache);
  HobbitStackCache c <- mkHobbitStackCacheT(mem, mem, m);
  return c;
endmodule

// `tmem` is the same memory without the data face's translation, for the
// prefetch buffer's physical reads (HobbitCore); the plain constructor
// above uses one for both.
module mkHobbitStackCacheT#(HobbitMem mem, HobbitMem tmem,
                            MemCycles m)(HobbitStackCache);

  Reg#(Word) spR   <- mkReg(0);
  Reg#(Word) mspR  <- mkReg(0);
  Reg#(Word) shadR <- mkReg(0);
  // Cache hit watermark.  Normally this is MSP.  During a CATCH refill it
  // is the address the refill has reached: below it the cache is valid,
  // at or above it the access goes to memory.
  Reg#(Word) fillR <- mkReg(0);
  // The array: 64 words with combinational reads (the EU reads an
  // operand every clock), the printed 64x32x2 (Figure 1-1, p. 1-2).  It
  // has no reset value: only [SP, MSP) is valid, and the flush/refill
  // rules write every word before it can be read.
  //
  // Until 2026-11-24 it was a Vector of 64 Regs, a 64:1 x 32-bit mux at
  // every read site: removing those reads saved 18k LUT4 of the
  // privileged core (docs/fpga_area.md).  It is now RegFiles, which bsc
  // emits as an array with one write port and combinational reads (block
  // RAM on the SoC, fpga/sysram_filter.py).  Two writers can store in one
  // clock (the EU and the refill, at different words), so there are two
  // banks, one per writer, and `lvt` (a live-value table, one bit per
  // word) says which bank holds the word's latest value; the EU wins a
  // same-word clock, as before.  Each bank is two RegFile copies with
  // identical writes, because bsc caps a RegFile at five read sites and
  // counts every call site: copy A serves `read` and the flush, copy B
  // `read2`.  Copy C serves only `cacheWord`, the harnesses' view
  // (P9BootTb reads three argument words with it, which overflowed copy
  // B); nothing reads it in the SoC, so synthesis drops it.
  RegFile#(Bit#(6), Word) bankEA <- mkRegFileFull;
  RegFile#(Bit#(6), Word) bankEB <- mkRegFileFull;
  RegFile#(Bit#(6), Word) bankEC <- mkRegFileFull;
  RegFile#(Bit#(6), Word) bankRA <- mkRegFileFull;
  RegFile#(Bit#(6), Word) bankRB <- mkRegFileFull;
  RegFile#(Bit#(6), Word) bankRC <- mkRegFileFull;
  Reg#(Bit#(64)) lvt <- mkReg(0);
  // A RegFile has no reset value, so the array is undetermined until a
  // word is stored.  The flush/refill engines and the EU all write
  // through the two write sites below, so one written bit per word (64
  // bits) defines every read the machine or a harness can
  // make: a word never stored reads as zero, not 0xaa..., which is the
  // only value the model's memory contract allows.
  Reg#(Bit#(64)) written <- mkReg(0);

  Reg#(ScState) state <- mkReg(SC_IDLE);
  Reg#(Word) flushBase <- mkReg(0);       // address of the quad being written
  Reg#(Bit#(2)) flushWord <- mkReg(0);    // 0..3 within the quad
  Reg#(Word) flushQuads <- mkReg(0);      // quads left, including the current

  Reg#(Word) refCap <- mkReg(0);          // address whose data arrives now
  Reg#(Word) refReq <- mkReg(0);          // next address to request
  Reg#(Word) fillEnd <- mkReg(0);         // CATCH fill bound (MSP after)

  Reg#(Bit#(32)) refillCnt <- mkReg(0);
  Reg#(Word) minSpR <- mkReg(0);
  Reg#(Word) maxSpR <- mkReg(0);

  // A non-cache destination waits here when the flush owns the memory
  // write port.  It is architectural state, so it is never dropped.
  // In-order execution has at most one such write outstanding: the
  // ENTER's flush blocks the issue of every younger instruction.
  Reg#(Maybe#(ScCmd)) pendingMemWr <- mkReg(tagged Invalid);

  // The EU's command and the reset request arrive on wires in the clock
  // they happen, so the single box rule remains the only writer of the
  // array, the pointers and the engines.
  Wire#(Maybe#(ScCmd)) cmdW <- mkDWire(tagged Invalid);
  Wire#(Maybe#(SpMsp)) resetW <- mkDWire(tagged Invalid);

  // EU_S1's operand-memory request, and the address whose word is on the
  // memory read port this clock (Invalid when the port carried a refill
  // word or nothing).
  Wire#(Maybe#(Word)) memReqW <- mkDWire(tagged Invalid);
  Reg#(Maybe#(Word)) memLiveR <- mkReg(tagged Invalid);
  // The prefetch buffer's request, and whether the word on the port this
  // clock is the one it asked for.
  Wire#(Maybe#(Word)) pfReqW <- mkDWire(tagged Invalid);
  Reg#(Bool) pfLiveR <- mkReg(False);

  function Bit#(6) cidx(Word a) = truncate(a >> 2);

  function Bool inRange(Word a, Word lo, Word hi);
    return (a >= lo) && (a < hi);
  endfunction

  // The array read on copy A (`a`) or copy B: the live bank's word, with
  // the written mask supplying the zero for a word never stored.
  // Copy `k`: 0 is A, 1 is B, 2 is C.
  function Word cacheAt(Bit#(2) k, Word addr);
    let i = cidx(addr);
    Word e = (k == 0) ? bankEA.sub(i) : (k == 1) ? bankEB.sub(i) : bankEC.sub(i);
    Word r = (k == 0) ? bankRA.sub(i) : (k == 1) ? bankRB.sub(i) : bankRC.sub(i);
    return (written[i] == 1'b1) ? ((lvt[i] == 1'b1) ? e : r) : 32'd0;
  endfunction

  function Word readWord(Bit#(2) k, Word addr, Word lo, Word hi);
    return (inRange(addr, lo, hi) && (addr < fillR))
             ? cacheAt(k, addr) : 0;
  endfunction

  rule boxStep;
    let mr = resetW;
    Bool doReset = isValid(mr);
    let mc = cmdW;
    Bool haveCmd = isValid(mc) && !doReset;
    ScCmd c = haveCmd ? validValue(mc) : noScCmd();

    Word nSp = spR;
    Word nMsp = mspR;
    Word nShad = shadR;
    Word nFill = fillR;
    ScState nState = state;
    Word nFlushBase = flushBase;
    Bit#(2) nFlushWord = flushWord;
    Word nFlushQuads = flushQuads;
    Word nRefCap = refCap;
    Word nRefReq = refReq;
    Word nFillEnd = fillEnd;
    Bit#(32) nRefillCnt = refillCnt;
    Word nMinSp = minSpR;
    Word nMaxSp = maxSpR;

    Bool enterStart = False;
    Bool catchStart = False;

    if (doReset) begin
      SpMsp r = validValue(mr);
      nSp = r.sp; nMsp = r.msp; nShad = r.sp; nFill = r.msp;
      nState = SC_IDLE;
      nFlushBase = 0; nFlushWord = 0; nFlushQuads = 0;
      nRefCap = r.msp; nRefReq = r.msp; nFillEnd = r.msp;
      nRefillCnt = 0; nMinSp = r.sp; nMaxSp = r.sp;
    end else begin
      if (haveCmd) begin
        nSp   = c.spAfter;
        nMsp  = c.mspAfter;
        nShad = c.spAfter;
        if (c.spAfter < nMinSp) nMinSp = c.spAfter;
        if (c.spAfter > nMaxSp) nMaxSp = c.spAfter;
        case (c.op)
          BX_ENTER: begin
            Word blocks = enterFlushBlocks(c.spBefore, c.mspBefore,
                                           c.target, c.stackMode);
            nFill = c.mspAfter;
            if (blocks != 0) begin
              enterStart  = True;
              nState      = SC_FLUSH;
              nFlushBase  = c.mspBefore - 16;
              nFlushWord  = 0;
              nFlushQuads = blocks;
            end
          end
          BX_CATCH: begin
            catchStart = (c.mspAfter != c.mspBefore);
            if (catchStart) begin
              nFill    = c.mspBefore;
              nState   = SC_REFILL;
              nRefCap  = c.mspBefore;
              nRefReq  = c.mspBefore + 4;
              nFillEnd = c.mspAfter;
            end else
              nFill = c.mspAfter;
          end
          default: nFill = c.mspAfter;
        endcase
      end
    end

    // ---- advance the running engine unless the command started one ----
    Bool flushStep  = !doReset && !enterStart && (state == SC_FLUSH);
    Bool refillStep = !doReset && !catchStart && (state == SC_REFILL);
    Word flushAddr = 0;

    if (flushStep) begin
      flushAddr = flushBase + (zeroExtend(flushWord) << 2);
      if (flushWord == 3) begin
        if (flushQuads == 1)
          nState = SC_IDLE;
        else begin
          nFlushQuads = flushQuads - 1;
          nFlushBase  = flushBase - 16;
          nFlushWord  = 0;
        end
      end else
        nFlushWord = flushWord + 1;
    end

    Bool refillReq = False;
    Word refillReqAddr = 0;
    if (refillStep) begin
      if (refCap + 4 < fillEnd) begin
        refillReq     = True;
        refillReqAddr = refReq;
        nRefCap       = refReq;
        nRefReq       = refReq + 4;
        nFill         = refCap + 4;
      end else begin
        nFill  = fillEnd;
        nState = SC_IDLE;
      end
      if ((refCap & 15) == 12) nRefillCnt = refillCnt + 1;
    end

    // A CATCH's first word is requested in the cycle it commits.
    if (catchStart) begin
      refillReq     = True;
      refillReqAddr = c.mspBefore;
    end

    // ---- the array's writes -----------------------------------------
    // Two sources can want the array in one clock: the refill's arriving
    // word (address refCap) and the EU's store.  Words the refill has
    // not reached yet -- inside [SP, MSP) but at or above the fill
    // watermark -- are still *memory* words: the EU reads them from
    // memory (HobbitCore `inCache`), so a store to one goes to memory
    // too, where the refill will pick it up.  The one exception is the
    // word whose refill data is arriving in this very clock: memory was
    // read before this store, so the store's data, not the arriving
    // word, is what the array must keep.
    //
    // Until 2026-11-20 a store to a not-yet-refilled word went nowhere
    // (it was "in range", so not a memory write, and "not filled", so not
    // an array write) and the refill then installed the stale word; and
    // a store to a filled word in the same clock as a refill step took
    // the one array write and the arriving word was dropped.  Neither
    // could happen while every run started with a full cache and CATCH
    // was a no-op; 1e's za did both within 4,000 instructions once the
    // cache started empty.
    Bool refillWr = refillStep;
    Bool euInWin = haveCmd && c.we &&
                   inRange(c.waddr, c.spAfter, c.mspAfter);
    Bool euFilled = euInWin && (c.waddr < fillR);
    Bool euUnfilled = euInWin && !(c.waddr < fillR);
    Bool euCacheWr = euFilled ||
                     (euUnfilled && refillStep && (c.waddr == refCap));
    Word euWrAddr = c.waddr;
    Word euWrData = c.wdata;

    // The reset does not rewrite the array (docs/area_analysis.md: the
    // reference reg_64x32 has no parallel reset); only [SP, MSP) is
    // architecturally valid, and the flush/refill rules fill it.  Each
    // word has one next value per clock: the EU's store wins over the
    // refill's word for the same address: the EU writes its bank and
    // the refill its own, and `lvt` records which bank is live.
    Bool ewAny = !doReset && euCacheWr;
    Bool rwAny = !doReset && refillWr &&
                 !(ewAny && (cidx(euWrAddr) == cidx(refCap)));
    Bit#(64) nWritten = written;
    Bit#(64) nLvt = lvt;
    if (ewAny) begin
      bankEA.upd(cidx(euWrAddr), euWrData);
      bankEB.upd(cidx(euWrAddr), euWrData);
      bankEC.upd(cidx(euWrAddr), euWrData);
      nWritten[cidx(euWrAddr)] = 1'b1;
      nLvt[cidx(euWrAddr)] = 1'b1;
    end
    if (rwAny) begin
      bankRA.upd(cidx(refCap), mem.readData());
      bankRB.upd(cidx(refCap), mem.readData());
      bankRC.upd(cidx(refCap), mem.readData());
      nWritten[cidx(refCap)] = 1'b1;
      nLvt[cidx(refCap)] = 1'b0;
    end
    written <= nWritten;
    lvt <= nLvt;

    // ---- the single memory write port ------------------------------
    // The flush wins; a non-cached EU write waits in memWrQ.
    Bool euMemWr = haveCmd && c.we &&
                   (!inRange(c.waddr, c.spAfter, c.mspAfter) || euUnfilled);
    Bool doMemWr = False;
    Word mwAddr = 0;
    Word mwData = 0;
    Maybe#(ScCmd) nPend = pendingMemWr;
    if (doReset) begin
      nPend = tagged Invalid;
    end else if (flushStep) begin
      doMemWr = True;
      mwAddr  = flushAddr;
      mwData  = cacheAt(0, flushAddr);
      if (euMemWr) nPend = tagged Valid c;
    end else if (pendingMemWr matches tagged Valid .p) begin
      doMemWr = True;
      mwAddr  = p.waddr;
      mwData  = p.wdata;
      nPend   = tagged Invalid;
    end else if (euMemWr) begin
      doMemWr = True;
      mwAddr  = c.waddr;
      mwData  = c.wdata;
    end
    pendingMemWr <= nPend;
    if (doMemWr) mem.write(mwAddr, mwData);
    // One memory read port: the refill wins (EU_S1 only asks while the
    // box is idle, so the two do not meet outside a reset).
    Bool opReq = !doReset && !refillReq && isValid(memReqW);
    Bool pfGrant = !refillReq && !opReq && isValid(pfReqW);
    if (refillReq) mem.readReq(refillReqAddr);
    else if (opReq) mem.readReq(validValue(memReqW));
    else if (pfGrant) tmem.readReq(validValue(pfReqW));
    memLiveR <= opReq ? memReqW : tagged Invalid;
    pfLiveR  <= pfGrant;

    // ---- commit the next state, each register once ------------------
    spR        <= nSp;
    mspR       <= nMsp;
    shadR      <= nShad;
    fillR      <= nFill;
    state      <= nState;
    flushBase  <= nFlushBase;
    flushWord  <= nFlushWord;
    flushQuads <= nFlushQuads;
    refCap     <= nRefCap;
    refReq     <= nRefReq;
    fillEnd    <= nFillEnd;
    refillCnt  <= nRefillCnt;
    minSpR     <= nMinSp;
    maxSpR     <= nMaxSp;
  endrule

  method Word sp()  = spR;
  method Word msp() = mspR;
  method Word csp() = spR;
  method Word shad() = shadR;

  method Word read(Word addr, Word lo, Word hi) = readWord(0, addr, lo, hi);
  method Word read2(Word addr, Word lo, Word hi) = readWord(1, addr, lo, hi);

  method Action commit(ScCmd c);
    cmdW <= tagged Valid c;
  endmethod

  method Action reset(Word spv, Word mspv);
    resetW <= tagged Valid (SpMsp { sp: spv, msp: mspv });
  endmethod

  method Bool busy() = state != SC_IDLE;
  method Bool flushing() = state == SC_FLUSH;
  method Bool refilling() = state == SC_REFILL;
  method Bit#(32) refills() = refillCnt;
  method Word minSpSeen() = minSpR;
  method Word maxSpSeen() = maxSpR;
  method Word cacheWord(Word addr) = readWord(2, addr, spR, fillR);
  method Bool cached(Word addr) = inRange(addr, spR, fillR);
  method Word fillWatermark() = fillR;

  method Action memReq(Word addr);
    memReqW <= tagged Valid addr;
  endmethod
  method Maybe#(Word) memLive() = memLiveR;
  method Word memData() = mem.readData();
  // No flush or refill owns the port, and no EU write to memory is still
  // parked behind a flush: memory holds every committed word.
  method Bool memIdle() = (state == SC_IDLE) && !isValid(pendingMemWr);

  interface MemPort textPort;
    method Action req(Word addr);
      pfReqW <= tagged Valid addr;
    endmethod
    method Bool live() = pfLiveR;
  endinterface

endmodule

endpackage
