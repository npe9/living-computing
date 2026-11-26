// The window framebuffer box (mkWinFbBox): a 1-bit 1280 x 1024 frame in
// block RAM and the drawing commands of the SIMPOS window device layer.
// docs/simpos/window_hardware_plan.md H0 and H1 (§2.4, §2.5).
//
// OURS SCAFFOLDING, NOT A RECONSTRUCTION.  The PSI's display controller
// is not documented (plan §1.1); this box is the hardware counterpart of
// the Python reference psi/winfb.py, whose header defines the command
// stream, every operand, the raster ops, clipping, the line algorithm,
// the glyph lookup, save areas and the status codes.  That header is the
// specification; this file implements it and bsv/run_win_tb.sh compares
// the two frames byte for byte.  Sourced facts it rests on: MSB = the
// leftmost dot in 16-bit words (TM-115 p74-76), 1 = black, the ops
// set/reset/exclusive_or/copy/reverse (window.md W§2.5), the f822 font
// layout (window_environment_plan.md §1.4).
//
// Interface: Server#(WinFbCmd, WinFbRsp).  One command at a time; each
// is answered on completion by one status response (isData False).  A
// dump is answered by the frame's 81,920 words, row-major, as isData
// responses, then its status.
//
// Structure (the idiomatic-Bluespec box pattern of the Pimm*Box modules
// and mkFBox: one module, request/response, the datapath inside, each
// engine its own rules):
//   - frame:  mkWinFrame (WinFrame.bsv, H3), 81,920 x 16 banked by hand
//             into 80 x 1,024 x 16 block RAMs.  Port A (this clock) draws
//             and dumps; port B, in the pixel clock domain `pclk`, is the
//             scan-out's (the DP16KD's second port).
//   - bitmap: mkBRAMCore1, 65,536 x 16, the save areas (plan §2.3: in
//             spare block RAM until H8 moves them to SDRAM).
//   - font:   mkBRAMCore1Load, 4,096 x 16, the f822 words of test_11
//             from a load file (the bench's, made from the held archive
//             by psi/winfb.py fonthex).
//   - index:  mkBRAMCore1, 8,869 x 8: JIS rows/cols 0x21-0x7e (94 x 94)
//             then codes 0-0x1f and 0xffff, each the record number + 1
//             (0 = none).  Built at reset by the font-scan rules from the
//             records (plan §2.5's index, OURS).
//   - the memory stages (WinMemPipe.bsv, H3 follow-up): every RAM the
//             engines stream through has a pipelined front, mkWinMemPipe,
//             with reads in flight under credits and two in-order
//             response ports (0: a source stream, 1: read-modify-write).
//             The frame's, fp, takes every port A access.
//   - the blit engine, two stages: the source stream (rules sIssue*:
//             one token a cycle, the row's first source word and then
//             one a destination word, each with its source read) and the
//             funnel (rule sCollect: each source word paired with the
//             carried one, a 16-bit funnel at a constant offset); fill,
//             copy, save, restore and glyph are all blits (a fill's
//             source is a constant 1).  Direction is chosen for
//             overlapping frame-to-frame copies: rows bottom-up when
//             dy > sy, words right to left when dy = sy and dx > sx.
//   - the line engine, two stages: Bresenham (rule lGen, one pen dot a
//             cycle) and the merge (rule lMerge: consecutive dots of one
//             word become one item).
//   - the read-modify-write stage (rules rPass, rRead*, w*), shared by
//             the blit and the line: reads a destination word when it
//             is needed, writes ropf of it, waits while an earlier item
//             still has to write the word it reads (mkWinPendQ), and ends
//             the command with the last write.
//   - the dump engine (rules dump*), on port A (H3 moved it from port
//             B, which is now the pixel domain's; port A is idle while a
//             dump runs).
//   - the scan port: port B of the frame, clocked by `pclk`, read only,
//             WinFrameLatB cycles a read (WinFrame.bsv).  It is
//             independent of the box: a dump no longer stops the
//             picture.  The one-clock benches pass the box's own clock
//             as pclk; bsv/WinUlx3sTb.bsv runs it on a separate clock.
//   - reset: the frame is cleared (81,920 cycles) and the index built;
//             commands wait until both finish.
//
// Cycles (no timing is claimed for the PSI).  H3 registered the frame's
// port A request (latency 2, WinFrame.bsv) to reach the board's clock;
// the box first waited a cycle on every frame read, then (H3 follow-up)
// the stages above were put in to keep several reads in flight, so port
// A is busy every cycle.  Per destination word: a fill 1 (set/reset/copy/
// reverse, a whole word) or 2 (xor, or an edge word); a frame-to-frame
// copy 2 (3 for an edge word), plus one source read a row; save and
// restore about 1 (the bitmap is another RAM).  A line: 2 a word it
// touches (consecutive dots in one word are one read and one write), at
// most one dot a cycle.  A dump word
// 2 (the bench's drain).  MEASURED 2026-11-25 in WinFbBoxTb, one command
// over an empty stream less the empty stream's own count; the H3 figures
// (a wait on every frame read) and then the H1 figures (one-cycle reads,
// no pipelining) in brackets:
//   clear 1280x984 (fill 0 40 1280 984 set)        78,724 (78,721; 78,721)
//   xor fill 1280x984                             157,443 (236,161; 157,441)
//   scroll 1280x964 by 20 lines (copy 0 60 ...)   155,205 (384,637; 231,361)
//   100 glyphs 'A' (16#2341, x = 11i, y = 20)       6,680 (12,140; 9,772)
//   a 1,280-dot diagonal (0,0)-(1279,1023)          2,196 (6,401; 5,121)
//   save + restore 400x300                         16,514 (62,102; 46,502)
//   the empty stream (reset and the final dump)   163,846 (327,683)
// The plan's §2.4 estimates were 78,720, ~157,000, ~64 a glyph and ~2,560.
// On the board the box runs on the 25 MHz oscillator (WinUlx3s.bsv), so a
// full-screen scroll is ~6.2 ms.  The streams are in bsv/win_measure/,
// measured by bsv/win_measure.sh.

// Unimplemented cases fail loud: a font that is not f822 or has more
// than 255 records stops the simulation at reset.
package WinFbBox;

import BRAMCore::*;
import FIFOF::*;
import GetPut::*;
import ClientServer::*;
import Vector::*;
import WinFrame::*;
import WinMemPipe::*;
export WinFrame::*;
export WinFbBox::*;

typedef struct {
   Bit#(8) op;                  // primitive << 4 | raster op
   Vector#(6, Bit#(16)) a;      // operands A..F (a[0] = A)
} WinFbCmd deriving (Bits, Eq, FShow);

typedef struct {
   Bool isData;
   Bit#(8) status;
   Bit#(16) data;
} WinFbRsp deriving (Bits, Eq, FShow);

interface WinFbBox;
   interface Server#(WinFbCmd, WinFbRsp) server;
   interface WinFbScan scan;
endinterface

typedef 1280 FbW;
typedef 1024 FbH;
typedef 80 FbWpr;
typedef 81920 FbWords;
typedef 65536 SaveWords;
typedef 16 SaveSlots;
typedef 8869 IndexSize;

// statuses (psi/winfb.py)
Bit#(8) stOK = 0;
Bit#(8) stBADOP = 1;
Bit#(8) stBADFONT = 2;
Bit#(8) stMISSING = 3;
Bit#(8) stBADSAVE = 4;
Bit#(8) stNOSAVE = 5;

typedef enum { MInit, MIdle, MBlit, MGlyph, MLine, MDump } Mode deriving (Bits, Eq);
typedef enum { SConst, SFrame, SSave, SFont } SrcKind deriving (Bits, Eq);

// a token of the blit's source stream (WinFbBox's stage 1 -> stage 2)
typedef struct {
   Bool load;                   // the row's first source word: only carried
   Bool mem;                    // the word is read (else it is 0)
   Bool last;                   // the blit's last destination word
   Bit#(20) addr;               // the destination word
   Bit#(16) mask;
   Bool needsDst;               // its old value is needed
} SrcTok deriving (Bits);

// a word for the read-modify-write stage
typedef struct {
   Bool word;                   // False: no word (a line's end only)
   Bool needsDst;
   Bool last;                   // the command ends with it
   Bit#(20) addr;
   Bit#(16) mask;
   Bit#(16) src;                // the source bits under the mask
} RmwItem deriving (Bits);
function Bit#(20) rmwKey(RmwItem x) = x.addr;

// a line pen dot (or only the line's end)
typedef struct {
   Bool dot;
   Bit#(20) addr;
   Bit#(16) bits;
   Bool last;
} LineDot deriving (Bits);

typedef struct {
   Bit#(16) x; Bit#(16) y; Bit#(16) w; Bit#(16) h; Bit#(16) base;
} SaveSlot deriving (Bits);

// op r of source bits s on frame bits d within mask m
function Bit#(16) ropf(Bit#(4) r, Bit#(16) s, Bit#(16) d, Bit#(16) m);
   Bit#(16) v = case (r)
                   0: (d | s);
                   1: (d & ~s);
                   2: (d ^ s);
                   3: s;
                   default: ~s;
                endcase;
   return (d & ~m) | (v & m);
endfunction

// the mask of destination word k for dots [x, x + w), MSB = leftmost
function Bit#(16) maskOf(Bit#(12) k, Bit#(16) x, Bit#(16) w);
   Bit#(20) lo = zeroExtend(k) << 4;
   Bit#(20) x0 = zeroExtend(x);
   Bit#(20) x1 = zeroExtend(x) + zeroExtend(w);
   Bit#(20) left = (lo < x0) ? x0 - lo : 0;            // 0..15
   Bit#(20) right = (x1 - lo > 16) ? 16 : x1 - lo;     // 1..16
   Bit#(17) ml = (1 << (16 - left)) - 1;
   Bit#(17) mr = (1 << (16 - right)) - 1;
   return truncate(ml & ~mr);
endfunction

// the 16 source dots from bit `off` of the word pair {a, b}
function Bit#(16) funnel(Bool isConst, Bit#(16) a, Bit#(16) b, Bit#(4) off);
   Bit#(32) sh = {a, b} << off;
   return isConst ? 'hffff : sh[31:16];
endfunction

function Bit#(16) min16(Bit#(16) a, Bit#(16) b) = (a < b) ? a : b;

// the index slot of a code, if it has one
function Maybe#(Bit#(14)) indexOf(Bit#(16) c);
   Bit#(8) hi = c[15:8];
   Bit#(8) lo = c[7:0];
   if (c < 'h20)
      return tagged Valid (8836 + truncate(c));
   else if (c == 'hffff)
      return tagged Valid (8836 + 32);
   else if (hi >= 'h21 && hi <= 'h7e && lo >= 'h21 && lo <= 'h7e) begin
      Bit#(14) h = zeroExtend(hi - 'h21);
      Bit#(14) l = zeroExtend(lo - 'h21);
      return tagged Valid (h * 94 + l);
   end
   else
      return tagged Invalid;
endfunction

module mkWinFbBox#(String fontFile, Clock pclk, Reset prst)(WinFbBox);
   Integer fbW = valueOf(FbW);
   Integer fbH = valueOf(FbH);

   WinFrame frame <- mkWinFrame(pclk, prst);
   BRAM_PORT#(Bit#(16), Bit#(16)) bitmap <- mkBRAMCore1(valueOf(SaveWords), False);
   BRAM_PORT#(Bit#(12), Bit#(16)) font <- mkBRAMCore1Load(4096, False, fontFile, False);
   BRAM_PORT#(Bit#(14), Bit#(8)) index <- mkBRAMCore1(valueOf(IndexSize), False);

   // the pipelined fronts of the three RAMs the engines stream through
   // (WinMemPipe.bsv): every frame port A access goes through fp; the
   // font's header and index reads at reset and in the glyph lookup use
   // the font RAM directly (other modes, never both in one cycle)
   WinMemPipe fp <- mkWinMemPipe(frame.a, valueOf(WinFrameLatA), 4, "WinFbBox frame");
   WinMemPipe bp <- mkWinMemPipe(bitmap, 1, 4, "WinFbBox bitmap");
   WinMemPipe np <- mkWinMemPipe(font, 1, 4, "WinFbBox font");
   Bit#(1) pSrc = 0;                      // response port of a source stream
   Bit#(1) pDst = 1;                      // of a read-modify-write

   FIFOF#(WinFbCmd) cmdQ <- mkFIFOF;
   FIFOF#(WinFbRsp) rspQ <- mkFIFOF;

   Reg#(Mode) mode <- mkReg(MInit);

   // ---- reset: clear the frame; scan the font into the index ----------
   Reg#(Bit#(17)) clearA <- mkReg(0);
   Reg#(Bool) clearDone <- mkReg(False);
   Reg#(Bit#(4)) fs <- mkReg(0);          // font-scan state
   Reg#(Bit#(14)) fsI <- mkReg(0);
   Reg#(Bit#(8)) fNum <- mkReg(0);        // records
   Reg#(Bit#(8)) fWpr <- mkReg(0);        // strip words a row
   Reg#(Bit#(12)) fBase <- mkReg(0);      // the strip's first word
   Reg#(Maybe#(Bit#(8))) fMissing <- mkReg(tagged Invalid);

   // ---- save slots ------------------------------------------------------
   Reg#(Vector#(SaveSlots, Maybe#(SaveSlot))) slots <- mkReg(replicate(tagged Invalid));

   // ---- the command's raster op and status, and its destination RAM
   // (the read-modify-write stage's; set by the blit and the line) -------
   Reg#(Bit#(4)) rRop <- mkRegU;
   Reg#(Bit#(8)) rStatus <- mkRegU;
   Reg#(Bool) bDstSave <- mkRegU;          // False = frame

   // ---- blit engine: the geometry ---------------------------------------
   Reg#(SrcKind) bSrc <- mkRegU;
   Reg#(Bit#(8)) bSrcPitch <- mkRegU;
   Reg#(Bit#(16)) bSrcX <- mkRegU;
   Reg#(Bit#(8)) bDstPitch <- mkRegU;
   Reg#(Bit#(16)) bDstX <- mkRegU;
   Reg#(Bit#(16)) bW <- mkRegU;
   Reg#(Bit#(16)) bH <- mkRegU;
   Reg#(Bool) bUp <- mkRegU;               // rows bottom-up
   Reg#(Bool) bRtl <- mkRegU;              // words right to left
   Reg#(Bit#(12)) bKFirst <- mkRegU;
   Reg#(Bit#(12)) bKLast <- mkRegU;
   Reg#(Bit#(4)) bSOff <- mkRegU;          // the funnel's offset (a constant)
   // the source stream's position
   Reg#(Bool) sOn <- mkReg(False);         // tokens still to issue
   Reg#(Bool) sFirst <- mkRegU;            // next: the row's first source word
   Reg#(Bit#(16)) sRow <- mkRegU;          // rows done
   Reg#(Bit#(20)) sDstRow <- mkRegU;
   Reg#(Bit#(20)) sSrcRow <- mkRegU;
   Reg#(Bit#(12)) sK <- mkRegU;            // destination word in its row
   Reg#(Bit#(16)) sCarry <- mkRegU;        // the funnel's carried source word
   FIFOF#(SrcTok) tokQ <- mkSizedFIFOF(4);

   // ---- the read-modify-write stage -------------------------------------
   FIFOF#(RmwItem) rmwQ <- mkFIFOF;
   WinPendQ#(RmwItem) pq <- mkWinPendQ(rmwKey);

   // ---- glyph lookup -----------------------------------------------------
   Reg#(Bit#(3)) gPh <- mkRegU;
   Reg#(Bit#(16)) gCode <- mkRegU;
   Reg#(Bit#(8)) gRec <- mkRegU;
   Reg#(Bit#(16)) gX <- mkRegU;
   Reg#(Bit#(16)) gY <- mkRegU;
   Reg#(Bit#(4)) gRop <- mkRegU;
   Reg#(Bit#(8)) gStatus <- mkRegU;
   Reg#(Bit#(16)) gRx <- mkRegU;
   Reg#(Bit#(16)) gRy <- mkRegU;
   Reg#(Bit#(16)) gRw <- mkRegU;

   // ---- line engine -----------------------------------------------------
   Reg#(Int#(20)) lX <- mkRegU;
   Reg#(Int#(20)) lY <- mkRegU;
   Reg#(Int#(20)) lX2 <- mkRegU;
   Reg#(Int#(20)) lY2 <- mkRegU;
   Reg#(Int#(20)) lDx <- mkRegU;           // |x2 - x1|
   Reg#(Int#(20)) lDy <- mkRegU;           // -|y2 - y1|
   Reg#(Int#(20)) lErr <- mkRegU;
   Reg#(Bool) lSxNeg <- mkRegU;
   Reg#(Bool) lSyNeg <- mkRegU;
   Reg#(Bool) lXMajor <- mkRegU;
   Reg#(Bit#(16)) lStyle <- mkRegU;
   Reg#(Bit#(4)) lI <- mkRegU;
   Reg#(Bit#(16)) lWidth <- mkRegU;
   Reg#(Bit#(16)) lK <- mkRegU;
   Reg#(Bool) lGenOn <- mkReg(False);
   FIFOF#(LineDot) dotQ <- mkFIFOF;
   // the word being merged: consecutive pen dots in one word
   Reg#(Bool) mHas <- mkReg(False);
   Reg#(Bit#(20)) mAddr <- mkRegU;
   Reg#(Bit#(16)) mMask <- mkRegU;         // the dots drawn

   // ---- dump engine -----------------------------------------------------
   Reg#(Bit#(17)) dA <- mkRegU;            // next read
   Reg#(Bool) dIss <- mkReg(False);
   Reg#(Bit#(17)) dB <- mkRegU;            // next word out

   // =====================================================================
   rule initClear (mode == MInit && !clearDone);
      fp.write(zeroExtend(clearA), 0);
      if (clearA == fromInteger(valueOf(FbWords) - 1)) clearDone <= True;
      clearA <= clearA + 1;
   endrule

   // fs 0: clear the index; 1..5: the header; 6, 7: the records
   rule fontClear (mode == MInit && fs == 0);
      index.put(True, fsI, 0);
      if (fsI == fromInteger(valueOf(IndexSize) - 1)) begin
         fs <= 1; fsI <= 0;
      end
      else fsI <= fsI + 1;
   endrule

   rule fontHdr0 (mode == MInit && fs == 1);
      font.put(False, 0, ?); fs <= 2;
   endrule
   rule fontHdr1 (mode == MInit && fs == 2);
      if (font.read != 'hf822) begin
         $display("WinFbBox: the font load file is not f822 (%h)", font.read);
         $finish(1);
      end
      font.put(False, 4, ?); fs <= 3;
   endrule
   rule fontHdr2 (mode == MInit && fs == 3);
      if (font.read > 255) begin
         $display("WinFbBox: more than 255 font records (%0d)", font.read);
         $finish(1);
      end
      fNum <= truncate(font.read);
      fBase <= 21 + (truncate(font.read) << 3);
      font.put(False, 5, ?); fs <= 4;
   endrule
   rule fontHdr3 (mode == MInit && fs == 4);
      Bit#(16) wpr = (font.read + 15) >> 4;
      fWpr <= truncate(wpr);
      fs <= 6; fsI <= 0;
   endrule
   rule fontRec0 (mode == MInit && fs == 6);
      if (fsI == zeroExtend(fNum)) begin
         fs <= 8;
      end
      else begin
         font.put(False, 21 + (truncate(fsI) << 3), ?); fs <= 7;
      end
   endrule
   rule fontRec1 (mode == MInit && fs == 7);
      Bit#(16) code = font.read;
      if (indexOf(code) matches tagged Valid .ix)
         index.put(True, ix, truncate(fsI) + 1);
      if (code == 'hffff) fMissing <= tagged Valid truncate(fsI);
      fsI <= fsI + 1; fs <= 6;
   endrule

   rule initDone (mode == MInit && clearDone && fs == 8);
      mode <= MIdle;
   endrule

   // =====================================================================
   // the blit engine, stage 1: the source stream.  One token a cycle: the
   // row's first source word (load), then one a destination word, each
   // with its source word's read (when the word is inside the source;
   // else the word is 0).  The tokens carry the destination word's
   // address, mask and whether its old value is needed.  The current
   // row's first word, destination and source, are registers stepped by
   // the pitch at each row end (H3: computing base + row x pitch here put
   // a multiplier on the path to the 80 frame banks' address pins, and the
   // system clock missed 25 MHz).
   //
   // Reading ahead of the writes is safe because of the copy's direction
   // (rows bottom-up when dy > sy, words right to left when dy = sy and
   // dx > sx): in that order no source word is read after the blit has
   // written it, so issuing the reads earlier changes nothing they see.
   Int#(20) q0 = unpack((zeroExtend(sK) << 4) - zeroExtend(bDstX) + zeroExtend(bSrcX));
   Int#(20) jA = q0 >> 4;
   Int#(20) jLo = unpack(zeroExtend(bSrcX >> 4));
   Int#(20) jHi = unpack(zeroExtend((bSrcX + bW - 1) >> 4));
   function Bool jValid(Int#(20) j) = bSrc != SConst && j >= jLo && j <= jHi;
   // left to right a destination word takes source words jA, jA + 1; the
   // row's first token reads jA, every word then reads jA + 1.  Right to
   // left the first reads jA + 1 and every word jA.
   Int#(20) jTok = (sFirst != bRtl) ? jA : jA + 1;
   Bool tokMem = jValid(jTok);
   Bit#(20) tokSrcA = sSrcRow + pack(jTok);
   Bit#(16) mask = maskOf(sK, bDstX, bW);
   Bool needsDst =
      !(mask == 'hffff && (rRop == 3 || rRop == 4 ||
                           (bSrc == SConst && (rRop == 0 || rRop == 1))));
   Bool rowEnd = sK == (bRtl ? bKFirst : bKLast);
   Bool lastRow = sRow + 1 == bH;
   SrcTok tok = SrcTok { load: sFirst, mem: tokMem, last: !sFirst && rowEnd && lastRow,
                         addr: sDstRow + zeroExtend(sK), mask: mask, needsDst: needsDst };

   Action sAdvance =
      action
         tokQ.enq(tok);
         if (sFirst) sFirst <= False;
         else if (rowEnd) begin
            if (lastRow) sOn <= False;
            sRow <= sRow + 1;
            sDstRow <= bUp ? sDstRow - zeroExtend(bDstPitch) : sDstRow + zeroExtend(bDstPitch);
            sSrcRow <= bUp ? sSrcRow - zeroExtend(bSrcPitch) : sSrcRow + zeroExtend(bSrcPitch);
            sK <= bRtl ? bKLast : bKFirst;
            sFirst <= bSrc != SConst;
         end
         else sK <= bRtl ? sK - 1 : sK + 1;
      endaction;

   // one rule a source RAM, so a read of the font or the save areas can go
   // in the same cycle as a write to the frame
   rule sIssueNone (mode == MBlit && sOn && !tokMem);
      sAdvance;
   endrule
   rule sIssueFrame (mode == MBlit && sOn && tokMem && bSrc == SFrame && fp.canRead(pSrc));
      fp.read(pSrc, tokSrcA); sAdvance;
   endrule
   rule sIssueSave (mode == MBlit && sOn && tokMem && bSrc == SSave && bp.canRead(pSrc));
      bp.read(pSrc, tokSrcA); sAdvance;
   endrule
   rule sIssueFont (mode == MBlit && sOn && tokMem && bSrc == SFont && np.canRead(pSrc));
      np.read(pSrc, tokSrcA); sAdvance;
   endrule

   // stage 2: pair each source word with the carried one (the funnel) and
   // pass the destination word on to the read-modify-write stage
   Bool srcRdy = case (bSrc)
                    SFrame: fp.rsp[pSrc].notEmpty;
                    SSave:  bp.rsp[pSrc].notEmpty;
                    SFont:  np.rsp[pSrc].notEmpty;
                    default: False;
                 endcase;
   Bit#(16) srcWord = case (bSrc)
                         SFrame: fp.rsp[pSrc].first;
                         SSave:  bp.rsp[pSrc].first;
                         default: np.rsp[pSrc].first;
                      endcase;
   Action srcDeq = case (bSrc)
                      SFrame: fp.rsp[pSrc].deq;
                      SSave:  bp.rsp[pSrc].deq;
                      default: np.rsp[pSrc].deq;
                   endcase;
   rule sCollect (mode == MBlit && (!tokQ.first.mem || srcRdy));
      SrcTok t = tokQ.first;
      tokQ.deq;
      Bit#(16) w = t.mem ? srcWord : 0;
      if (t.mem) srcDeq;
      sCarry <= w;
      if (!t.load) begin
         Bit#(16) a = bRtl ? w : sCarry;
         Bit#(16) b = bRtl ? sCarry : w;
         rmwQ.enq(RmwItem { word: True, needsDst: t.needsDst, last: t.last, addr: t.addr,
                            mask: t.mask, src: funnel(bSrc == SConst, a, b, bSOff) });
      end
   endrule

   function Action startBlit(SrcKind src, Bit#(20) sBase, Bit#(8) sPitch, Bit#(16) sX,
                             Bool dSave, Bit#(20) dBase, Bit#(8) dPitch, Bit#(16) dX,
                             Bit#(16) w, Bit#(16) h, Bit#(4) r, Bool up, Bool rtl,
                             Bit#(8) st);
      action
         if (w == 0 || h == 0) begin
            rspQ.enq(WinFbRsp { isData: False, status: st, data: 0 });
            mode <= MIdle;
         end
         else begin
            Bit#(12) kf = truncate(dX >> 4);
            Bit#(12) kl = truncate((dX + w - 1) >> 4);
            bSrc <= src; bSrcPitch <= sPitch; bSrcX <= sX;
            bDstSave <= dSave; bDstPitch <= dPitch; bDstX <= dX;
            bW <= w; bH <= h; rRop <= r; bUp <= up; bRtl <= rtl;
            bKFirst <= kf; bKLast <= kl;
            bSOff <= truncate(sX - dX);
            Bit#(20) last = zeroExtend(h - 1);
            sOn <= True; sFirst <= src != SConst;
            sRow <= 0; sK <= rtl ? kl : kf;
            sDstRow <= dBase + (up ? last * zeroExtend(dPitch) : 0);
            sSrcRow <= sBase + (up ? last * zeroExtend(sPitch) : 0);
            rStatus <= st;
            mode <= MBlit;
         end
      endaction
   endfunction

   // =====================================================================
   // the read-modify-write stage (the blit's destination words and the
   // line's pen words): read the old word when it is needed, then write
   // ropf of it.  An item whose word an earlier item still has to write
   // waits (pq.has).  The last item's write ends the command.
   Bool rmwOn = mode == MBlit || mode == MLine;
   RmwItem ri = rmwQ.first;
   Bool riRead = ri.word && ri.needsDst;
   rule rPass (rmwOn && !riRead);
      rmwQ.deq; pq.enq(ri);
   endrule
   rule rReadFrame (rmwOn && riRead && !bDstSave && fp.canRead(pDst) && !pq.has(ri.addr));
      fp.read(pDst, ri.addr); rmwQ.deq; pq.enq(ri);
   endrule
   rule rReadSave (rmwOn && riRead && bDstSave && bp.canRead(pDst) && !pq.has(ri.addr));
      bp.read(pDst, ri.addr); rmwQ.deq; pq.enq(ri);
   endrule

   RmwItem pi = pq.first;
   Bool piRead = pi.word && pi.needsDst;
   Action retire =
      action
         if (pi.last) begin
            rspQ.enq(WinFbRsp { isData: False, status: rStatus, data: 0 });
            mode <= MIdle;
         end
      endaction;
   (* descending_urgency = "wFrame, rReadFrame, sIssueFrame" *)
   rule wFrame (rmwOn && !bDstSave && (!piRead || fp.rsp[pDst].notEmpty));
      pq.deq;
      Bit#(16) d = piRead ? fp.rsp[pDst].first : 0;
      if (piRead) fp.rsp[pDst].deq;
      if (pi.word) fp.write(pi.addr, ropf(rRop, pi.src, d, pi.mask));
      retire;
   endrule
   (* descending_urgency = "wSave, rReadSave, sIssueSave" *)
   rule wSave (rmwOn && bDstSave && (!piRead || bp.rsp[pDst].notEmpty));
      pq.deq;
      Bit#(16) d = piRead ? bp.rsp[pDst].first : 0;
      if (piRead) bp.rsp[pDst].deq;
      if (pi.word) bp.write(pi.addr, ropf(rRop, pi.src, d, pi.mask));
      retire;
   endrule

   // =====================================================================
   // glyph: index -> record (x, y, w, h) -> a blit from the strip
   rule glyph0 (mode == MGlyph && gPh == 1);
      // the index answered: the record number + 1, or 0
      Bit#(8) e = index.read;
      if (e != 0) begin
         gRec <= e - 1; gPh <= 2;
      end
      else if (fMissing matches tagged Valid .m) begin
         gRec <= m; gStatus <= stMISSING; gPh <= 2;
      end
      else begin
         rspQ.enq(WinFbRsp { isData: False, status: stMISSING, data: 0 });
         mode <= MIdle;
      end
   endrule
   // the index slot of the code (H3: a rule of its own, a cycle after
   // accept, so the slot's multiply is not on accept's path to the index
   // RAM; the system clock missed 25 MHz there, MEASURED)
   rule glyphLook (mode == MGlyph && gPh == 7);
      if (indexOf(gCode) matches tagged Valid .ix) begin
         index.put(False, ix, ?);
         gPh <= 1;
      end
      else gPh <= 0;
   endrule
   rule glyphNone (mode == MGlyph && gPh == 0);
      // a code with no index slot
      if (fMissing matches tagged Valid .m) begin
         gRec <= m; gStatus <= stMISSING; gPh <= 2;
      end
      else begin
         rspQ.enq(WinFbRsp { isData: False, status: stMISSING, data: 0 });
         mode <= MIdle;
      end
   endrule
   Bit#(12) recA = 21 + (zeroExtend(gRec) << 3);
   rule glyph2 (mode == MGlyph && gPh == 2);
      font.put(False, recA + 1, ?); gPh <= 3;
   endrule
   rule glyph3 (mode == MGlyph && gPh == 3);
      gRx <= font.read; font.put(False, recA + 2, ?); gPh <= 4;
   endrule
   rule glyph4 (mode == MGlyph && gPh == 4);
      gRy <= font.read; font.put(False, recA + 3, ?); gPh <= 5;
   endrule
   rule glyph5 (mode == MGlyph && gPh == 5);
      gRw <= font.read; font.put(False, recA + 4, ?); gPh <= 6;
   endrule
   rule glyph6 (mode == MGlyph && gPh == 6);
      Bit#(16) gh = font.read;
      Bool outside = gX >= fromInteger(fbW) || gY >= fromInteger(fbH);
      Bit#(16) w = outside ? 0 : min16(gRw, fromInteger(fbW) - gX);
      Bit#(16) h = outside ? 0 : min16(gh, fromInteger(fbH) - gY);
      Bit#(20) sBase = zeroExtend(fBase) + zeroExtend(gRy) * zeroExtend(fWpr);
      startBlit(SFont, sBase, fWpr, gRx,
                False, zeroExtend(gY) * 80, 80, gX, w, h, gRop, False, False, gStatus);
   endrule

   // =====================================================================
   // line: Bresenham; the pen is lWidth dots across the major axis.
   // Stage 1 (lGen): one pen dot a cycle, the Bresenham step taken with
   // the pen's last dot; stage 2 (lMerge): consecutive dots in one word
   // become one read-modify-write item (mask = src = the dots); then the
   // read-modify-write stage.  One item for several dots equals the
   // reference's one read-modify-write a dot because a line never draws a
   // dot twice: a step's pen dots differ in k, and every Bresenham step
   // moves the major coordinate (checked by brute force over all lines
   // with endpoints in 0..11 x 0..11, 2026-11-25), so xor is the same.
   Int#(20) lPx = lXMajor ? lX : lX + unpack(zeroExtend(lK));
   Int#(20) lPy = lXMajor ? lY + unpack(zeroExtend(lK)) : lY;
   Bool lOn = lStyle[15 - lI] == 1;
   Bit#(20) lAddr = pack(lPy) * 80 + (pack(lPx) >> 4);
   Bit#(16) lBit = 'h8000 >> pack(lPx)[3:0];

   rule lGen (mode == MLine && lGenOn);
      Bool onScr = lPx < fromInteger(fbW) && lPy < fromInteger(fbH);
      Bool penDone = !lOn || lK + 1 == lWidth;
      Bool atEnd = lX == lX2 && lY == lY2;
      Bool last = penDone && atEnd;
      if ((lOn && onScr) || last)
         dotQ.enq(LineDot { dot: lOn && onScr, addr: lAddr, bits: lBit, last: last });
      if (!penDone) lK <= lK + 1;
      else if (atEnd) lGenOn <= False;
      else begin
         Int#(20) e2 = 2 * lErr;
         Int#(20) err = lErr;
         if (e2 >= lDy) begin
            err = err + lDy;
            lX <= lSxNeg ? lX - 1 : lX + 1;
         end
         if (e2 <= lDx) begin
            err = err + lDx;
            lY <= lSyNeg ? lY - 1 : lY + 1;
         end
         lErr <= err;
         lI <= lI + 1;
         lK <= 0;
      end
   endrule

   rule lMerge (mode == MLine);
      LineDot d = dotQ.first;
      if (d.dot && mHas && mAddr != d.addr) begin
         // a dot in another word: the merged word goes on, and the dot
         // starts the next (the line's last dot waits a cycle: its word
         // and the end go on together)
         rmwQ.enq(RmwItem { word: True, needsDst: True, last: False, addr: mAddr,
                            mask: mMask, src: mMask });
         if (d.last) mHas <= False;
         else begin
            dotQ.deq;
            mAddr <= d.addr; mMask <= d.bits;
         end
      end
      else begin
         dotQ.deq;
         Bool h = mHas || d.dot;
         Bit#(20) a = mHas ? mAddr : d.addr;
         Bit#(16) m = !d.dot ? mMask : (mHas ? (mMask | d.bits) : d.bits);
         if (d.last) begin
            rmwQ.enq(RmwItem { word: h, needsDst: True, last: True, addr: a, mask: m, src: m });
            mHas <= False;
         end
         else begin
            mHas <= h; mAddr <= a; mMask <= m;
         end
      end
   endrule

   // =====================================================================
   // dump: a stream of frame reads, each word passed on as it comes
   rule dumpReq (mode == MDump && dIss && fp.canRead(pSrc));
      fp.read(pSrc, zeroExtend(dA));
      if (dA == fromInteger(valueOf(FbWords) - 1)) dIss <= False;
      dA <= dA + 1;
   endrule
   rule dumpRsp (mode == MDump && fp.rsp[pSrc].notEmpty);
      rspQ.enq(WinFbRsp { isData: True, status: stOK, data: fp.rsp[pSrc].first });
      fp.rsp[pSrc].deq;
      if (dB == fromInteger(valueOf(FbWords) - 1)) begin
         // the status follows the data; a FIFOF of 2 holds both
         mode <= MIdle;
      end
      dB <= dB + 1;
   endrule
   Reg#(Bool) dTail <- mkReg(False);
   rule dumpEnd (mode == MIdle && dTail);
      rspQ.enq(WinFbRsp { isData: False, status: stOK, data: 0 });
      dTail <= False;
   endrule

   // =====================================================================
   // accept one command and set up its engine
   function Action reply(Bit#(8) st) =
      rspQ.enq(WinFbRsp { isData: False, status: st, data: 0 });
   rule accept (mode == MIdle && !dTail);
      WinFbCmd c = cmdQ.first;
      cmdQ.deq;
      Bit#(4) prim = c.op[7:4];
      Bit#(4) r = c.op[3:0];
      Vector#(6, Bit#(16)) a = c.a;
      Bit#(16) fw = fromInteger(fbW);
      Bit#(16) fh = fromInteger(fbH);
      if (prim == 0 || prim > 7 || r > 4)
         reply(stBADOP);
      else case (prim)
         1: begin // fill x y w h
               Bool outside = a[0] >= fw || a[1] >= fh;
               Bit#(16) w = outside ? 0 : min16(a[2], fw - a[0]);
               Bit#(16) h = outside ? 0 : min16(a[3], fh - a[1]);
               startBlit(SConst, 0, 0, 0, False, zeroExtend(a[1]) * 80, 80, a[0],
                         w, h, r, False, False, stOK);
            end
         2: begin // line x1 y1 x2 y2 width style
               if (a[4] == 0) reply(stOK);
               else begin
                  Int#(20) x1 = unpack(zeroExtend(a[0]));
                  Int#(20) y1 = unpack(zeroExtend(a[1]));
                  Int#(20) x2 = unpack(zeroExtend(a[2]));
                  Int#(20) y2 = unpack(zeroExtend(a[3]));
                  Int#(20) dx = abs(x2 - x1);
                  Int#(20) dy = -abs(y2 - y1);
                  lX <= x1; lY <= y1; lX2 <= x2; lY2 <= y2;
                  lDx <= dx; lDy <= dy; lErr <= dx + dy;
                  lSxNeg <= !(x1 < x2); lSyNeg <= !(y1 < y2);
                  lXMajor <= dx >= -dy;
                  lStyle <= a[5]; lI <= 0; lWidth <= a[4]; lK <= 0;
                  rRop <= r; rStatus <= stOK; bDstSave <= False;
                  lGenOn <= True; mHas <= False;
                  mode <= MLine;
               end
            end
         3: begin // glyph font code x y
               if (a[0] != 0) reply(stBADFONT);
               else begin
                  gX <= a[2]; gY <= a[3]; gRop <= r; gStatus <= stOK;
                  gCode <= a[1];
                  gPh <= 7;
                  mode <= MGlyph;
               end
            end
         4: begin // copy sx sy w h dx dy
               Bool outside = a[0] >= fw || a[4] >= fw || a[1] >= fh || a[5] >= fh;
               Bit#(16) w = outside ? 0 : min16(a[2], min16(fw - a[0], fw - a[4]));
               Bit#(16) h = outside ? 0 : min16(a[3], min16(fh - a[1], fh - a[5]));
               startBlit(SFrame, zeroExtend(a[1]) * 80, 80, a[0],
                         False, zeroExtend(a[5]) * 80, 80, a[4], w, h, r,
                         a[5] > a[1], a[5] == a[1] && a[4] > a[0], stOK);
            end
         5: begin // save id x y w h base
               Bit#(4) id = truncate(a[0]);
               Bool outside = a[1] >= fw || a[2] >= fh || a[3] == 0 || a[4] == 0;
               Bit#(16) w = outside ? 0 : min16(a[3], fw - a[1]);
               Bit#(16) h = outside ? 0 : min16(a[4], fh - a[2]);
               Bit#(16) pitch = (w + 15) >> 4;
               Bit#(20) need = zeroExtend(a[5]) + zeroExtend(pitch) * zeroExtend(h);
               if (a[0] >= fromInteger(valueOf(SaveSlots)) || need > fromInteger(valueOf(SaveWords)))
                  reply(stBADSAVE);
               else begin
                  slots[id] <= tagged Valid SaveSlot { x: a[1], y: a[2], w: w, h: h, base: a[5] };
                  startBlit(SFrame, zeroExtend(a[2]) * 80, 80, a[1],
                            True, zeroExtend(a[5]), truncate(pitch), 0, w, h, 3,
                            False, False, stOK);
               end
            end
         6: begin // restore id
               Bit#(4) id = truncate(a[0]);
               if (a[0] >= fromInteger(valueOf(SaveSlots))) reply(stBADSAVE);
               else if (slots[id] matches tagged Valid .s) begin
                  Bit#(16) pitch = (s.w + 15) >> 4;
                  startBlit(SSave, zeroExtend(s.base), truncate(pitch), 0,
                            False, zeroExtend(s.y) * 80, 80, s.x, s.w, s.h, r,
                            False, False, stOK);
               end
               else reply(stNOSAVE);
            end
         7: begin // dump
               dA <= 0; dB <= 0; dIss <= True; dTail <= True;
               mode <= MDump;
            end
      endcase
   endrule

   interface Server server;
      interface Put request = toPut(cmdQ);
      interface Get response = toGet(rspQ);
   endinterface
   interface WinFbScan scan = frame.b;
endmodule

endpackage
