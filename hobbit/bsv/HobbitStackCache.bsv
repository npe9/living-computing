// HobbitStackCache.bsv -- the 64-register stack cache and integer
// accumulator as a request/response box with one read and one write
// port per clock.
//
// Figure 1-1 (printed p. 1-2) prints "STACK CACHE 64x32x2 bits" and a
// 32-bit path to the execution unit; p. 1-1 calls it a "256 byte stack
// cache that holds top of user stack".  The trailing x2 is the two
// ports modelled here: one combinational read port and one registered
// write port.  The EU reads an operand (EU_S1) and writes its
// destination (EU_S3) in the same clock, and a CATCH refill can write a
// word while the EU reads one -- the two cases the single-writer
// sequencer could not express.  A flush reads the array and writes
// memory, so the EU's write and the flush's read also overlap.
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
  // its refill watermark.  A miss returns 0 and the EU reports it
  // loudly (a p. 4-1 operand-capture violation).
  method Word read(Word addr, Word lo, Word hi);

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
  method Word cacheWord(Word addr);
  method Bool cached(Word addr);
  method Word fillWatermark();
endinterface

module mkHobbitStackCache#(HobbitMem mem, MemCycles m)(HobbitStackCache);

  Reg#(Word) spR   <- mkReg(0);
  Reg#(Word) mspR  <- mkReg(0);
  Reg#(Word) shadR <- mkReg(0);
  // Cache hit watermark.  Normally this is MSP.  During a CATCH refill it
  // is the address the refill has reached: below it the cache is valid,
  // at or above it the access goes to memory.
  Reg#(Word) fillR <- mkReg(0);
  // One write port and a combinational 64:1 read (the EU reads an
  // operand every clock).  A RegFile emits the plain array shape that
  // maps to LUT RAM: docs/area_analysis.md's reg_64x32 is 132 LUT4,
  // against 12,107 LUT4 for a Vector written by update.  The array has
  // no architectural reset value: only [SP, MSP) is valid, and the
  // flush/refill rules write every word before it can be read.
  RegFile#(Bit#(6), Word) cache <- mkRegFileFull;
  // mkRegFileFull has no reset value, so Bluesim leaves the array
  // undetermined until a word is stored.  The flush/refill engines and
  // the EU all write through the one `upd` call site below, so one
  // written bit per word (64 bits) defines every read the machine or a
  // harness can make: a word never stored reads as zero, not 0xaa...,
  // which is the only value the model's memory contract allows.
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

  function Bit#(6) cidx(Word a) = truncate(a >> 2);

  function Bool inRange(Word a, Word lo, Word hi);
    return (a >= lo) && (a < hi);
  endfunction

  // The array read: one `sub` call site, shared by the EU's operand
  // read, the testbench probe and the flush engine, with the written
  // mask supplying the zero for a word never stored.
  function Word cacheAt(Word addr);
    let i = cidx(addr);
    return (written[i] == 1'b1) ? cache.sub(i) : 32'd0;
  endfunction

  function Word readWord(Word addr, Word lo, Word hi);
    return (inRange(addr, lo, hi) && (addr < fillR))
             ? cacheAt(addr) : 0;
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

    // ---- the single array write port -------------------------------
    Bool refillWr = refillStep;
    Bool euCacheWr = False;
    Word euWrAddr = 0;
    Word euWrData = 0;
    if (haveCmd) begin
      if (c.we && inRange(c.waddr, c.spAfter, c.mspAfter) &&
          (c.waddr < fillR)) begin
        euCacheWr = True;
        euWrAddr = c.waddr;
        euWrData = c.wdata;
      end
    end

    // One write port: the refill's arriving word and the EU's in-cache
    // write are muxed to one address/data pair, then one upd.  The
    // reset does not rewrite the array (docs/area_analysis.md: the
    // reference reg_64x32 has no parallel reset); only [SP, MSP) is
    // architecturally valid, and the flush/refill rules fill it.
    Bool cacheWr = !doReset && (refillWr || euCacheWr);
    Word cacheWrAddr = euCacheWr ? euWrAddr : refCap;
    Word cacheWrData = euCacheWr ? euWrData : mem.readData();
    if (cacheWr) begin
      cache.upd(cidx(cacheWrAddr), cacheWrData);
      written <= written | (64'd1 << cidx(cacheWrAddr));
    end

    // ---- the single memory write port ------------------------------
    // The flush wins; a non-cached EU write waits in memWrQ.
    Bool euMemWr = haveCmd && c.we &&
                   !inRange(c.waddr, c.spAfter, c.mspAfter);
    Bool doMemWr = False;
    Word mwAddr = 0;
    Word mwData = 0;
    Maybe#(ScCmd) nPend = pendingMemWr;
    if (doReset) begin
      nPend = tagged Invalid;
    end else if (flushStep) begin
      doMemWr = True;
      mwAddr  = flushAddr;
      mwData  = cacheAt(flushAddr);
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
    if (refillReq) mem.readReq(refillReqAddr);

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

  method Word read(Word addr, Word lo, Word hi) = readWord(addr, lo, hi);

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
  // The testbench probe reuses the one read port; it adds no port.
  method Word cacheWord(Word addr) = readWord(addr, spR, fillR);
  method Bool cached(Word addr) = inRange(addr, spR, fillR);
  method Word fillWatermark() = fillR;

endmodule

endpackage
