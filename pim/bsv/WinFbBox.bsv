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
//   - the blit engine (rules blit*): one destination word per step, a
//             16-bit funnel from two source words, edge masks; fill,
//             copy, save, restore and glyph are all blits (a fill's
//             source is a constant 1).  Direction is chosen for
//             overlapping frame-to-frame copies: rows bottom-up when
//             dy > sy, words right to left when dy = sy and dx > sx.
//   - the line engine (rules line*): Bresenham, one read-modify-write
//             per pen dot.
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
// port A request (latency 2, WinFrame.bsv) to reach the board's clock,
// so every frame read now waits one more cycle (register fWait).  Per
// destination word: a fill 1 (set/reset/copy/reverse, a whole word) or
// 3 (xor, or an edge word); a blit from the frame 5.  A line dot is 5
// cycles, a dump word 3.  MEASURED 2026-11-25 in WinFbBoxTb, one command
// over an empty stream less the empty stream's own count (H1 figures,
// one-cycle reads, in brackets): clear 1280x984 78,721 (78,721; plan
// §2.4 estimate 78,720); xor fill 1280x984 236,161 (157,441); scroll
// 1280x964 by 20 lines 384,637 (231,361; plan ~157,000); 100 glyphs
// 12,140 (9,772; plan ~64 each); a 1,280-dot diagonal 6,401 (5,121;
// plan ~2,560); save + restore 400x300 62,102 (46,502).  On the board the
// box runs on the 25 MHz oscillator (WinUlx3s.bsv), so a full-screen
// scroll is ~15 ms.  A carried funnel
// word and pipelined frame reads (several in flight) would bring copies
// to ~1-2 a word; that is not scheduled (H4 is the owner's board step).

// Unimplemented cases fail loud: a font that is not f822 or has more
// than 255 records stops the simulation at reset.
package WinFbBox;

import BRAMCore::*;
import FIFOF::*;
import GetPut::*;
import ClientServer::*;
import Vector::*;
import WinFrame::*;
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
typedef enum { PSrc0, PSrc1, PDst, PWr } BPhase deriving (Bits, Eq);
typedef enum { LDot, LWr, LStep } LPhase deriving (Bits, Eq);

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

   // ---- blit engine ----------------------------------------------------
   Reg#(SrcKind) bSrc <- mkRegU;
   Reg#(Bit#(8)) bSrcPitch <- mkRegU;
   Reg#(Bit#(16)) bSrcX <- mkRegU;
   Reg#(Bool) bDstSave <- mkRegU;          // False = frame
   Reg#(Bit#(8)) bDstPitch <- mkRegU;
   Reg#(Bit#(16)) bDstX <- mkRegU;
   Reg#(Bit#(16)) bW <- mkRegU;
   Reg#(Bit#(16)) bH <- mkRegU;
   Reg#(Bit#(4)) bRop <- mkRegU;
   Reg#(Bool) bUp <- mkRegU;               // rows bottom-up
   Reg#(Bool) bRtl <- mkRegU;              // words right to left
   Reg#(Bit#(16)) bRow <- mkRegU;          // rows done
   Reg#(Bit#(20)) bDstRow <- mkRegU;
   Reg#(Bit#(20)) bSrcRow <- mkRegU;
   Reg#(Bit#(12)) bK <- mkRegU;            // destination word in its row
   Reg#(Bit#(12)) bKFirst <- mkRegU;
   Reg#(Bit#(12)) bKLast <- mkRegU;
   Reg#(BPhase) bPh <- mkRegU;
   Reg#(Bit#(16)) bSa <- mkRegU;
   Reg#(Bit#(16)) bSb <- mkRegU;
   Reg#(Bit#(8)) bStatus <- mkRegU;

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
   Reg#(Bit#(4)) lRop <- mkRegU;
   Reg#(LPhase) lPh <- mkRegU;

   // ---- dump engine -----------------------------------------------------
   Reg#(Bit#(17)) dA <- mkRegU;
   Reg#(Bool) dWait <- mkRegU;

   // ---- the frame's port A answers two cycles after a put (WinFrame.bsv,
   // H3): a rule that reads the frame sets fWait, and the engines stand
   // still for the one cycle in between ------------------------------------
   Reg#(Bool) fWait <- mkReg(False);
   rule frameWait (fWait);
      fWait <= False;
   endrule

   // =====================================================================
   rule initClear (mode == MInit && !clearDone);
      frame.a.put(True, clearA, 0);
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
   // the blit engine
   // the current row's first word, destination and source: registers
   // stepped by the pitch at each row end (H3: computing base + row x
   // pitch here put a multiplier on the path to the 80 frame banks'
   // address pins, and the system clock missed 25 MHz)
   Bit#(20) dstRow = bDstRow;
   Bit#(20) srcRow = bSrcRow;
   // the source bit under the destination word's first dot, signed
   Int#(20) q0 = unpack((zeroExtend(bK) << 4) - zeroExtend(bDstX) + zeroExtend(bSrcX));
   Int#(20) jA = q0 >> 4;
   Bit#(4) sOff = truncate(pack(q0));
   Int#(20) jLo = unpack(zeroExtend(bSrcX >> 4));
   Int#(20) jHi = unpack(zeroExtend((bSrcX + bW - 1) >> 4));
   function Bool jValid(Int#(20) j) = bSrc != SConst && j >= jLo && j <= jHi;
   Bit#(16) mask = maskOf(bK, bDstX, bW);
   Bit#(16) srcBits = funnel(bSrc == SConst, bSa, bSb, sOff);

   function Action srcRead(Int#(20) j);
      action
         Bit#(20) a = srcRow + pack(j);
         case (bSrc)
            SFrame: begin frame.a.put(False, truncate(a), ?); fWait <= True; end
            SSave:  bitmap.put(False, truncate(a), ?);
            SFont:  font.put(False, truncate(a), ?);
         endcase
      endaction
   endfunction
   Bit#(16) srcData =
      case (bSrc)
         SFrame: frame.a.read;
         SSave:  bitmap.read;
         default: font.read;
      endcase;
   function Action dstPut(Bool wr, Bit#(16) d);
      action
         Bit#(20) a = dstRow + zeroExtend(bK);
         if (bDstSave) bitmap.put(wr, truncate(a), d);
         else begin
            frame.a.put(wr, truncate(a), d);
            if (!wr) fWait <= True;
         end
      endaction
   endfunction
   Bit#(16) dstData = bDstSave ? bitmap.read : frame.a.read;

   Bool needsDst =
      !(mask == 'hffff && (bRop == 3 || bRop == 4 ||
                           (bSrc == SConst && (bRop == 0 || bRop == 1))));

   // the next destination word, or the end of the blit
   Action advance =
      action
         Bool rowEnd = bK == (bRtl ? bKFirst : bKLast);
         if (rowEnd) begin
            if (bRow + 1 == bH) begin
               rspQ.enq(WinFbRsp { isData: False, status: bStatus, data: 0 });
               mode <= MIdle;
            end
            bRow <= bRow + 1;
            bDstRow <= bUp ? bDstRow - zeroExtend(bDstPitch) : bDstRow + zeroExtend(bDstPitch);
            bSrcRow <= bUp ? bSrcRow - zeroExtend(bSrcPitch) : bSrcRow + zeroExtend(bSrcPitch);
            bK <= bRtl ? bKLast : bKFirst;
         end
         else bK <= bRtl ? bK - 1 : bK + 1;
         bPh <= (bSrc == SConst) ? PDst : PSrc0;
      endaction;

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
            bW <= w; bH <= h; bRop <= r; bUp <= up; bRtl <= rtl;
            bRow <= 0; bK <= rtl ? kl : kf; bKFirst <= kf; bKLast <= kl;
            Bit#(20) last = zeroExtend(h - 1);
            bDstRow <= dBase + (up ? last * zeroExtend(dPitch) : 0);
            bSrcRow <= sBase + (up ? last * zeroExtend(sPitch) : 0);
            bPh <= (src == SConst) ? PDst : PSrc0;
            bStatus <= st;
            mode <= MBlit;
         end
      endaction
   endfunction

   rule blitSrc0 (mode == MBlit && bPh == PSrc0 && !fWait);
      if (jValid(jA)) srcRead(jA);
      bPh <= PSrc1;
   endrule
   rule blitSrc1 (mode == MBlit && bPh == PSrc1 && !fWait);
      bSa <= jValid(jA) ? srcData : 0;
      if (jValid(jA + 1)) srcRead(jA + 1);
      bPh <= PDst;
   endrule
   rule blitDst (mode == MBlit && bPh == PDst && !fWait);
      Bit#(16) sb = (bSrc != SConst && jValid(jA + 1)) ? srcData : 0;
      bSb <= sb;
      if (needsDst) begin
         dstPut(False, ?);
         bPh <= PWr;
      end
      else begin
         // every bit of the word is replaced and none depends on the frame
         dstPut(True, ropf(bRop, funnel(bSrc == SConst, bSa, sb, sOff), 0, 'hffff));
         advance;
      end
   endrule
   rule blitWr (mode == MBlit && bPh == PWr && !fWait);
      dstPut(True, ropf(bRop, srcBits, dstData, mask));
      advance;
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
   // line: Bresenham; the pen is lWidth dots across the major axis
   Int#(20) lPx = lXMajor ? lX : lX + unpack(zeroExtend(lK));
   Int#(20) lPy = lXMajor ? lY + unpack(zeroExtend(lK)) : lY;
   Bool lOn = lStyle[15 - lI] == 1;
   Bit#(20) lAddr = pack(lPy) * 80 + (pack(lPx) >> 4);
   Bit#(16) lBit = 'h8000 >> pack(lPx)[3:0];

   rule lineDot (mode == MLine && lPh == LDot && !fWait);
      if (!lOn || lK == lWidth)
         lPh <= LStep;
      else if (lPx < fromInteger(fbW) && lPy < fromInteger(fbH)) begin
         frame.a.put(False, truncate(lAddr), ?);
         fWait <= True;
         lPh <= LWr;
      end
      else lK <= lK + 1;
   endrule
   rule lineWr (mode == MLine && lPh == LWr && !fWait);
      frame.a.put(True, truncate(lAddr), ropf(lRop, lBit, frame.a.read, lBit));
      lK <= lK + 1;
      lPh <= LDot;
   endrule
   rule lineStep (mode == MLine && lPh == LStep && !fWait);
      if (lX == lX2 && lY == lY2) begin
         rspQ.enq(WinFbRsp { isData: False, status: stOK, data: 0 });
         mode <= MIdle;
      end
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
         lPh <= LDot;
      end
   endrule

   // =====================================================================
   // dump, on port B: put an address, then pass the word on
   rule dumpReq (mode == MDump && !dWait && !fWait);
      frame.a.put(False, dA, ?);
      fWait <= True;
      dWait <= True;
   endrule
   rule dumpRsp (mode == MDump && dWait && !fWait);
      rspQ.enq(WinFbRsp { isData: True, status: stOK, data: frame.a.read });
      dWait <= False;
      if (dA == fromInteger(valueOf(FbWords) - 1)) begin
         // the status follows the data; a FIFOF of 2 holds both
         mode <= MIdle;
      end
      dA <= dA + 1;
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
                  lStyle <= a[5]; lI <= 0; lWidth <= a[4]; lK <= 0; lRop <= r;
                  lPh <= LDot;
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
               dA <= 0; dWait <= False; dTail <= True;
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
