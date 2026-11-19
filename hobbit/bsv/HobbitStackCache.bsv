// HobbitStackCache.bsv -- the 64-register stack cache and integer
// accumulator as a stateful request/response box.
//
// Documented behaviour modelled here (printed pages of the January 1993
// Programmer's Reference Manual):
//
//   * 64 words, circular buffer, word addressable, a hit when
//     SP <= address < MSP (p. 1-5, p. 1-12).
//   * the integer accumulator is the word at CSP+4; CSP is SP in this
//     milestone (p. 1-7, Figure 1-4).
//   * CALL writes the return PC at CSP (p. 3-9).
//   * ENTER sets SP = CSP + src in stack-offset mode, flushing the
//     entries nearest MSP only as far as necessary; other modes flush
//     all valid entries and empty the cache (p. 3-19/3-20).
//   * CATCH refills quad-words from memory at MSP until MSP reaches
//     the target or the cache holds SCSIZE = 256 bytes (p. 3-10/3-11).
//   * POPN sets SP += src, and MSP = SP when SP exceeds MSP (p. 3-38).
//   * RETURN reads the new PC at CSP+src, then sets SP += src with the
//     low four bits of src ignored, and MSP = SP when SP exceeds MSP
//     (p. 3-39/3-40).
//
// Flush and refill are multi-cycle: one quad-word per clock.  busy()
// tells the core to stall retirement and the next instruction until the
// box is idle, so sp_after/msp_after are final when the HRI record is
// printed.

package HobbitStackCache;

import Vector::*;
import HobbitTypes::*;

typedef enum { SC_IDLE, SC_FLUSH, SC_REFILL } ScState deriving (Eq, Bits);

interface HobbitStackCache;
  method Word sp();
  method Word msp();
  method Word csp();
  method Word shad();

  method Word read(Word addr);
  method Action write(Word addr, Word val);

  method Action reset(Word sp, Word msp);
  method Action call(Word retPc);
  method Action enter(Word target, Bool stackMode);
  method Action catchTo(Word target);
  method Action popn(Word off);
  method ActionValue#(Word) returnFrom(Word off);

  method Bool busy();
  method Bit#(32) refills();
  method Word minSpSeen();
  method Word maxSpSeen();
  method Word cacheWord(Word addr);
  method Bool cached(Word addr);
endinterface

module mkHobbitStackCache#(HobbitMem mem)(HobbitStackCache);

  Reg#(Word) spR  <- mkReg(0);
  Reg#(Word) mspR <- mkReg(0);
  Reg#(Word) shadR <- mkReg(0);
  Reg#(Vector#(64, Word)) cache <- mkReg(replicate(0));

  Reg#(ScState) state <- mkReg(SC_IDLE);
  Reg#(Bool) flushAllR <- mkReg(False);
  Reg#(Word) workMsp <- mkReg(0);
  Reg#(Word) workTarget <- mkReg(0);
  Reg#(Word) flushBase <- mkReg(0);
  Reg#(Bit#(3)) flushIdx <- mkReg(4);   // 0..3 next word, 4 = next quad decision

  Reg#(Bit#(32)) refillCnt <- mkReg(0);
  Reg#(Word) minSpR <- mkReg(0);
  Reg#(Word) maxSpR <- mkReg(0);

  function Bit#(6) cidx(Word a) = truncate(a >> 2);

  function Bool inCache(Word a);
    return (a >= spR) && (a < mspR);
  endfunction

  function Word readWord(Word a);
    return inCache(a) ? cache[cidx(a)] : mem.read(a);
  endfunction

  function Action writeWord(Word a, Word v);
    action
      if (inCache(a))
        cache <= update(cache, cidx(a), v);
      else
        mem.write(a, v);
    endaction
  endfunction

  function Bool needFlush(Word wm);
    return flushAllR ? (wm > shadR)
                     : ((wm > shadR) && ((wm - workTarget) > 256));
  endfunction

  function Action touchSp(Word v);
    action
      if (v < minSpR) minSpR <= v;
      if (v > maxSpR) maxSpR <= v;
    endaction
  endfunction

  // --- ENTER flush engine, p. 3-19 --------------------------------
  // Quad-words leave the cache one 32-bit word per clock (memory has a
  // single write port); flushIdx 0..3 walks a quad, 4 decides whether
  // another quad is needed.
  rule flushStep (state == SC_FLUSH);
    if (flushIdx < 4) begin
      Word a = flushBase + (zeroExtend(flushIdx) << 2);
      mem.write(a, cache[cidx(a)]);
      if (flushIdx == 3) begin
        flushIdx <= 4;
        workMsp  <= workMsp - 16;
      end else
        flushIdx <= flushIdx + 1;
    end else begin
      if (needFlush(workMsp)) begin
        flushBase <= workMsp - 16;
        flushIdx  <= 1;
        mem.write(workMsp - 16, cache[cidx(workMsp - 16)]);
      end else if (flushAllR) begin
        // Nothing valid remains: the cache is empty at the target.
        mspR  <= workTarget;
        spR   <= workTarget;
        shadR <= workTarget;
        touchSp(workTarget);
        state <= SC_IDLE;
      end else begin
        let nm = (workMsp > (workTarget + 256)) ? workTarget + 256 : workMsp;
        mspR  <= nm;
        spR   <= workTarget;
        shadR <= workTarget;
        touchSp(workTarget);
        state <= SC_IDLE;
      end
    end
  endrule

  // --- CATCH refill engine, p. 3-10 -------------------------------
  rule refillStep (state == SC_REFILL);
    if ((workMsp < workTarget) && ((workMsp - spR) < 256)) begin
      Bit#(6) i = cidx(workMsp);
      let v0 = update(cache, i,          mem.read(workMsp));
      let v1 = update(v0,    i + 1,      mem.read(workMsp + 4));
      let v2 = update(v1,    i + 2,      mem.read(workMsp + 8));
      cache     <= update(v2, i + 3,     mem.read(workMsp + 12));
      workMsp   <= workMsp + 16;
      refillCnt <= refillCnt + 1;
    end else begin
      mspR  <= workMsp;
      state <= SC_IDLE;
    end
  endrule

  method Word sp()  = spR;
  method Word msp() = mspR;
  method Word csp() = spR;
  method Word shad() = shadR;

  method Word read(Word addr) = readWord(addr);

  method Action write(Word addr, Word val);
    writeWord(addr, val);
  endmethod

  method Action reset(Word spv, Word mspv);
    spR       <= spv;
    mspR      <= mspv;
    shadR     <= spv;
    cache     <= replicate(0);
    state     <= SC_IDLE;
    flushAllR <= False;
    workMsp   <= 0;
    workTarget <= 0;
    flushBase <= 0;
    flushIdx  <= 4;
    refillCnt <= 0;
    minSpR    <= spv;
    maxSpR    <= spv;
  endmethod

  // CALL: the return PC goes to the word at CSP (R0), p. 3-9.
  method Action call(Word retPc);
    writeWord(spR, retPc);
  endmethod

  method Action enter(Word target, Bool stackMode);
    if (stackMode) begin
      if ((mspR - target) > 256) begin
        if (mspR > shadR) begin
          state      <= SC_FLUSH;
          flushAllR  <= False;
          flushIdx   <= 4;
          workMsp    <= mspR;
          workTarget <= target;
        end else begin
          let nm = (mspR > (target + 256)) ? target + 256 : mspR;
          mspR  <= nm;
          spR   <= target;
          shadR <= target;
          touchSp(target);
        end
      end else begin
        spR   <= target;
        shadR <= target;
        touchSp(target);
      end
    end else begin
      if (mspR > shadR) begin
        state      <= SC_FLUSH;
        flushAllR  <= True;
        flushIdx   <= 4;
        workMsp    <= mspR;
        workTarget <= target;
      end else begin
        mspR  <= target;
        spR   <= target;
        shadR <= target;
        touchSp(target);
      end
    end
  endmethod

  method Action catchTo(Word target);
    if ((target > mspR) && (mspR >= spR) && ((mspR - spR) < 256)) begin
      state      <= SC_REFILL;
      workMsp    <= mspR;
      workTarget <= target;
    end
  endmethod

  method Action popn(Word off);
    Word d  = off & 32'hFFFFFFF0;    // low four SP bits do not exist
    Word ns = spR + d;
    spR   <= ns;
    shadR <= ns;
    if (ns > mspR) mspR <= ns;
    touchSp(ns);
  endmethod

  method ActionValue#(Word) returnFrom(Word off);
    Word rp = readWord(spR + off);
    Word d  = off & 32'hFFFFFFF0;
    Word ns = spR + d;
    spR   <= ns;
    shadR <= ns;
    if (ns > mspR) mspR <= ns;
    touchSp(ns);
    return rp;
  endmethod

  method Bool busy() = state != SC_IDLE;
  method Bit#(32) refills() = refillCnt;
  method Word minSpSeen() = minSpR;
  method Word maxSpSeen() = maxSpR;
  method Word cacheWord(Word addr) = cache[cidx(addr)];
  method Bool cached(Word addr) = inCache(addr);

endmodule

endpackage
