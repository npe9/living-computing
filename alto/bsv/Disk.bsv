// Diablo 31 / Alto disk controller — Alto Hardware Manual (May 1979) §6.
//
// Hardware, not ContrAlto:
//   * The platter only rotates forward. WFFO=0 holds the *bit counter* at -1
//     until a 1-bit is read; it does not rewind the sector word index.
//   * KWD BLOCK does not stop the drive. A late word task misses the word.
//   * A sector pulse from the drive wakes KSEC even during a seek.
//   * KCOM is BUS[1-5] (manual §6.1). KSTAT[4-7] read as 17B.
//
// The .dsk image only stores the three recorded blocks (header / label / data).
// Gap and sync words exist on the simulated platter but are not committed.

package Disk;

import ConfigReg::*;
import AltoTypes::*;

import "BDPI" function Bit#(32) host_disk_loaded();
import "BDPI" function Bit#(16) host_disk_cylinders();
import "BDPI" function Bit#(16) host_disk_read_word(Bit#(32) idx);
import "BDPI" function Action   host_disk_write_word(Bit#(32) idx, Bit#(16) data);
import "BDPI" function Action   host_disk_select(Bit#(32) cyl, Bit#(32) head, Bit#(32) sec);
import "BDPI" function Action   host_disk_commit();

interface Disk_IFC;
   method Word  kstat;
   method Word  kdata;
   method Word  kadr;
   method Word  recno;
   method Bool  dataXfer;
   method Bool  ready;
   method Bool  fatalError;
   method Bool  wdInit;
   method Bool  strobeOn;
   method Action setKDATA(Word v);
   method Action setKADR(Word v);
   method Action setKCOM(Word v);
   method Action setKSTAT(Word v);
   method Action clrStat();
   method Action incRec();
   method Action strobe();
   method Action setWdInit(Bool v);
   method Action disableSeclate();
   method Bool   wakeupSector;
   method Bool   wakeupWord;
   method Action reset();
endinterface

module mkDisk(Disk_IFC);
   Reg#(Word)  kDataRead  <- mkConfigReg(0);
   Reg#(Word)  kDataWrite <- mkConfigReg(0);
   Reg#(Bool)  kDataLatch <- mkConfigReg(False);
   Reg#(Word)  kAdrReg    <- mkConfigReg(0);
   Reg#(Word)  kComReg    <- mkConfigReg(0);
   Reg#(Word)  kStatReg   <- mkConfigReg(kstatNOTREADY);
   Reg#(Bit#(2)) recNo    <- mkConfigReg(0);

   // KCOM BUS[1-5]: XFEROFF, WDINHIB, BCLKSRC, WFFO, SENDADR.
   Reg#(Bool) xferOff   <- mkConfigReg(True);
   Reg#(Bool) wdInhib   <- mkConfigReg(True);
   Reg#(Bool) bClkSrc   <- mkConfigReg(False);
   Reg#(Bool) wffo      <- mkConfigReg(False);
   Reg#(Bool) sendAdr   <- mkConfigReg(False);
   Reg#(Bool) dataXferR <- mkConfigReg(True);
   Reg#(Bool) wdInitR   <- mkConfigReg(False);
   // Bit counter running. WFFO=0 holds it; a read of 1 releases it (§6.1).
   Reg#(Bool) bitClk    <- mkConfigReg(False);
   Reg#(Bool) syncWr    <- mkConfigReg(False);
   Reg#(Bool) restore   <- mkConfigReg(False);
   Reg#(Bool) seeking   <- mkConfigReg(False);

   Reg#(Bit#(1)) diskSel <- mkReg(0);
   Reg#(Bit#(4)) sector  <- mkReg(0);
   Reg#(Bit#(9)) cyl     <- mkReg(0);
   Reg#(Bit#(1)) head    <- mkReg(0);
   Reg#(Bit#(9)) destCyl <- mkReg(0);
   Reg#(Bit#(9)) wordIdx <- mkReg(0);

   Reg#(Bit#(16)) wordTimer    <- mkReg(0);
   Reg#(Bit#(16)) seclateTimer <- mkReg(0);
   Reg#(Bit#(16)) seekTimer    <- mkReg(0);
   Reg#(Bool)     seclateEn    <- mkReg(False);
   Reg#(Bool)     seclate      <- mkReg(False);
   Reg#(Bool)     spinning     <- mkReg(False);
   Reg#(Bool)     wakeSec      <- mkConfigReg(False);
   Reg#(Bool)     wakeWd       <- mkConfigReg(False);

   RWire#(Word) rwKDATA <- mkRWire;
   RWire#(Word) rwKADR  <- mkRWire;
   RWire#(Word) rwKCOM  <- mkRWire;
   RWire#(Word) rwKSTAT <- mkRWire;
   RWire#(Bool) rwWdInit <- mkRWire;
   PulseWire pwClr    <- mkPulseWire;
   PulseWire pwInc    <- mkPulseWire;
   PulseWire pwStrobe <- mkPulseWire;
   PulseWire pwNoSec  <- mkPulseWire;
   PulseWire pwReset  <- mkPulseWire;

   function Bool isWriteCmd(Word adr);
      Bit#(2) cmd = adr[7:6];
      return cmd == 2 || cmd == 3;
   endfunction

   // RECNO F2 map from §6.1: 0→0, 1→2, 2→3, 3→1.
   function Word recMap(Bit#(2) n);
      case (n)
         0: return 0;
         1: return 2;
         2: return 3;
         default: return 1;
      endcase
   endfunction

   // One controller clock: F1/F2 pulses land on RWires, then the autonomous
   // seek / word / SECLATE machines run. A single rule keeps those machines
   // conflict-free with each other (they share KSTAT and the word index).
   (* fire_when_enabled, no_implicit_conditions *)
   rule rl_controller;
      Word  st   = kStatReg;
      Word  kad  = kAdrReg;
      Word  kdw  = kDataWrite;
      Word  kdr  = kDataRead;
      Bool  latch= kDataLatch;
      Bit#(2) rn = recNo;
      Bool  seek = seeking;
      Bool  rest = restore;
      Bool  se   = seclateEn;
      Bool  sl   = seclate;
      Bool  wdi  = wdInitR;
      Bool  syn  = syncWr;
      Bool  bck  = bitClk;
      Bool  xoff = xferOff;
      Bool  winh = wdInhib;
      Bool  bcs  = bClkSrc;
      Bool  wf   = wffo;
      Bool  dx   = dataXferR;
      Bit#(4) sec = sector;
      Bit#(9) cy  = cyl;
      Bit#(1) hd  = head;
      Bit#(9) wi  = wordIdx;
      Bit#(16) wt = wordTimer;
      Bit#(16) slt= seclateTimer;
      Bit#(16) skt= seekTimer;
      Bool  spin = spinning;
      Bool  wsec = False;
      Bool  wwd  = False;
      Bit#(9) dcy = destCyl;
      Bool  doSel = False;
      Maybe#(Tuple2#(Bit#(32), Word)) wrReq = tagged Invalid;

      if (pwReset) begin
         st = (host_disk_loaded() != 0) ? 0 : kstatNOTREADY;
         rn = 0; sec = 0; cy = 0; hd = 0;
         seek = False; winh = True; xoff = True; wdi = False;
         syn = False; bck = False; spin = False; sl = False; se = False;
         wi = 0; wt = 0;
         doSel = True;
         wsec = True;
      end
      else begin
         if (rwKDATA.wget matches tagged Valid .v) begin
            kdw = v; latch = True;
         end
         if (rwKADR.wget matches tagged Valid .v) begin
            kad = v; rn = 0; syn = False;
            Bit#(1) nh = kdw[2];
            if (nh != hd) doSel = True;
            hd = nh;
            dx = v[1] != 1;
            diskSel <= kdw[1];
            rest = kdw[0] == 1;
         end
         if (rwKCOM.wget matches tagged Valid .v) begin
            kComReg <= v;
            xoff = v[4] == 1;
            winh = v[3] == 1;
            bcs  = v[2] == 1;
            wf   = v[1] == 1;
            sendAdr <= v[0] == 1;
            // WFFO=1 lets the bit counter run; WFFO=0 holds it at -1.
            bck  = v[1] == 1;
            if (v[3] == 1) wdi = True;
            if (v[0] == 1 && kdw[1] == 1) seek = False;
         end
         if (rwKSTAT.wget matches tagged Valid .v)
            st = v;
         if (pwClr) begin
            st = st & 16'hFF4B;
            sl = False;
         end
         if (pwInc) begin
            kad = kad << 2;
            rn = rn + 1;
            syn = False;
         end
         if (rwWdInit.wget matches tagged Valid .v)
            wdi = v;
         if (pwNoSec)
            se = False;
         if (pwStrobe) begin
            Bit#(9) dest = rest ? 0 : kdw[11:3];
            Bit#(16) maxc = host_disk_cylinders();
            if (host_disk_loaded() == 0 || zeroExtend(dest) >= maxc) begin
               st = st | kstatSEEKFAIL;
               seek = False;
            end
            else if (dest != cy) begin
               dcy = dest;
               st = (st & ~kstatSEEKFAIL) | kstatSTROBE;
               seek = True;
               skt = fromInteger(diskSeekCycles);
            end
            else
               st = st & ~kstatSEEKFAIL;
         end

         if (seek) begin
            if (skt == 0) begin
               if (cy < dcy) cy = cy + 1;
               else if (cy > dcy) cy = cy - 1;
               if (cy == dcy) begin
                  st = st & ~kstatSTROBE;
                  seek = False;
                  rest = False;
                  doSel = True;
               end
               else
                  skt = fromInteger(diskSeekCycles);
            end
            else
               skt = skt - 1;
         end

         // Platter always rotates (including during seek).
         if (!spin) begin
            spin = True;
            wt = fromInteger(diskWordCycles);
            wi = 0;
         end
         else if (wt == 0) begin
            wt = fromInteger(diskWordCycles);
            if (!seek) begin
               Word diskWord = host_disk_read_word(zeroExtend(wi));
               Bool wake = False;
               // BCLKSRC=0: crystal / delay clock — wake every word (§6.1,
               // delay mode used by the preamble). BCLKSRC=1: disk clock.
               if (!sl && !winh && !bcs)
                  wake = True;
               if (!sl && (wf || bck)) begin
                  if (!xoff) begin
                     if (!isWriteCmd(kad))
                        kdr = diskWord;
                     else begin
                        if (latch) begin
                           kdr = kdw;
                           latch = False;
                        end
                        if (syn)
                           wrReq = tagged Valid tuple2(zeroExtend(wi), kdw);
                     end
                  end
                  if (!winh) wake = True;
               end
               if (!isWriteCmd(kad) && !wf && diskWord == 1)
                  bck = True;
               else if (isWriteCmd(kad) && wf && kdw == 1 && !syn)
                  syn = True;
               if (wake)
                  wwd = True;
            end

            if (wi >= fromInteger(sectorWordCount - 1)) begin
               Bit#(4) ns = (sec == 11) ? 0 : sec + 1;
               sec = ns; wi = 0; syn = False; kdr = 0;
               doSel = True;
               st = (st & 16'h0FFF) | {ns, 12'b0};
               if (host_disk_loaded() != 0)
                  st = st & ~kstatNOTREADY;
               else
                  st = st | kstatNOTREADY;
               // Sector signal from the drive; µcode tests SWRNRDY if seeking.
               wsec = True;
               sl = False;
               se = True;
               slt = fromInteger(diskSeclateCycles);
               st = st & ~kstatSECLATE;
            end
            else
               wi = wi + 1;
         end
         else
            wt = wt - 1;

         if (se) begin
            if (slt == 0) begin
               sl = True;
               se = False;
               st = st | kstatSECLATE;
            end
            else
               slt = slt - 1;
         end
      end

      if (wrReq matches tagged Valid {.idx, .dat})
         host_disk_write_word(idx, dat);
      if (doSel)
         host_disk_select(zeroExtend(cy), zeroExtend(hd), zeroExtend(sec));

      kStatReg   <= st;
      kAdrReg    <= kad;
      kDataWrite <= kdw;
      kDataRead  <= kdr;
      kDataLatch <= latch;
      recNo      <= rn;
      seeking    <= seek;
      restore    <= rest;
      seclateEn  <= se;
      seclate    <= sl;
      wdInitR    <= wdi;
      syncWr     <= syn;
      bitClk     <= bck;
      xferOff    <= xoff;
      wdInhib    <= winh;
      bClkSrc    <= bcs;
      wffo       <= wf;
      dataXferR  <= dx;
      sector     <= sec;
      cyl        <= cy;
      head       <= hd;
      wordIdx    <= wi;
      wordTimer  <= wt;
      seclateTimer <= slt;
      seekTimer  <= skt;
      spinning   <= spin;
      wakeSec    <= wsec;
      wakeWd     <= wwd;
      destCyl    <= dcy;
   endrule

   method Word kstat = kStatReg | kstatS47;
   method Word kdata = kDataRead;
   method Word kadr = kAdrReg;
   method Word recno = recMap(recNo);
   method Bool dataXfer = dataXferR;
   method Bool ready = host_disk_loaded() != 0 && !seeking;
   method Bool fatalError =
      (kStatReg & kstatSECLATE) != 0 ||
      (kStatReg & kstatSEEKFAIL) != 0 ||
      (kStatReg & kstatNOTREADY) != 0 ||
      !(host_disk_loaded() != 0 && !seeking);
   method Bool wdInit = wdInitR;
   method Bool strobeOn = (kStatReg & kstatSTROBE) != 0;

   method Action setKDATA(Word v); rwKDATA.wset(v); endmethod
   method Action setKADR(Word v);  rwKADR.wset(v);  endmethod
   method Action setKCOM(Word v);  rwKCOM.wset(v);  endmethod
   method Action setKSTAT(Word v); rwKSTAT.wset(v); endmethod
   method Action clrStat();        pwClr.send();    endmethod
   method Action incRec();         pwInc.send();    endmethod
   method Action strobe();         pwStrobe.send(); endmethod
   method Action setWdInit(Bool v); rwWdInit.wset(v); endmethod
   method Action disableSeclate(); pwNoSec.send();  endmethod
   method Bool wakeupSector = wakeSec;
   method Bool wakeupWord = wakeWd;
   method Action reset(); pwReset.send(); endmethod
endmodule

endpackage
