// Alto II micromachine — one rule per 170 ns clock (HW manual §2.0).
// Task wakeup, NEXT modifiers, and the 32-bit µinstruction layout are from
// that manual; the PROM bits are the historical Alto II dumps.

package CPU;

import Vector::*;
import ConfigReg::*;
import AltoTypes::*;
import ALU::*;
import Shifter::*;
import AltoMem::*;
import Disk::*;
import Display::*;
import Devices::*;
import Ethernet::*;

import "BDPI" function Bit#(32) host_ucode(Bit#(32) bank, Bit#(32) addr);
import "BDPI" function Bit#(16) host_constant(Bit#(32) addr);
import "BDPI" function Bit#(8)  host_acs(Bit#(32) addr);
import "BDPI" function Action   host_ether_post(Bit#(16) st);
import "BDPI" function Bit#(32) host_cram_word(Bit#(32) addr);
import "BDPI" function Bit#(16) host_cram_half(Bit#(32) addr);
import "BDPI" function Action   host_cram_write(Bit#(32) addr, Bit#(32) data);

interface CPU_IFC;
   method Action reset();
   method TaskId curTask;
   method UAddr  mpc;
   method Word   tReg;
   method Word   lReg;
   method Word   irReg;
   method Word   r6;
   method Word   ac0;
   method Word   ac1;
   method Word   ac2;
   method Word   ac3;
   method Bit#(64) cycles;
   method Bool   memWait;
endinterface

module mkCPU#(Memory_IFC mem, Disk_IFC disk, Display_IFC disp,
              Keyboard_IFC kbd, Ethernet_IFC eth)
             (CPU_IFC);

   Vector#(32, Reg#(Word)) r <- replicateM(mkConfigReg(0));
   Vector#(8, Vector#(32, Reg#(Word))) s <- replicateM(replicateM(mkReg(0)));

   Reg#(Word) t        <- mkReg(0);
   Reg#(Word) l        <- mkReg(0);
   Reg#(Word) m        <- mkReg(0);
   Reg#(Word) ir       <- mkConfigReg(0);
   Reg#(Bit#(1)) aluC0 <- mkReg(0);
   Reg#(Bit#(1)) skip  <- mkReg(0);
   Reg#(Bit#(1)) carry <- mkReg(0);
   Reg#(Word) rmr      <- mkReg(16'hFFFF);

   Vector#(16, Reg#(UAddr)) taskMpc <- genWithM(compose(mkConfigReg, fromInteger));
   Vector#(16, Reg#(Bool))  wake    <- replicateM(mkReg(False));
   Vector#(16, Reg#(Bit#(3))) sBank <- replicateM(mkReg(0));
   Vector#(16, Reg#(Bit#(3))) uBank <- replicateM(mkReg(0));

   Reg#(TaskId) cur        <- mkConfigReg(0);
   Reg#(TaskId) nxt        <- mkReg(0);
   Reg#(Bool)   switchPend <- mkReg(False);
   Reg#(Bool)   firstAfter <- mkReg(True);
   // NEXT modifiers are per-task: F2 bits apply to that task's following
   // instruction, not whatever task happens to run next.
   Vector#(16, Reg#(UAddr)) taskMod <- replicateM(mkReg(0));

   Reg#(Bool) rdRam    <- mkReg(False);
   Reg#(Bool) wrtRam   <- mkReg(False);
   Reg#(Bool) swMode   <- mkReg(False);
   Reg#(Bool) softRst  <- mkReg(False);
   Reg#(Word) cramAddr <- mkReg(0);
   // Halfword latched when T loads the CRAM address so RDRAM can AND
   // it onto the bus next cycle (HW §8.3 / RDRM).
   Reg#(Word) cramHalf <- mkReg(16'hFFFF);

   Reg#(Bit#(64)) cycn    <- mkConfigReg(0);
   Reg#(Bool)     waiting <- mkConfigReg(False);
   PulseWire      pwReset <- mkPulseWire;

   function Bit#(32) fetchU(TaskId tsk, UAddr a);
      let b = uBank[tsk];
      if (b == 2) return host_cram_word(zeroExtend(a));
      else return host_ucode(zeroExtend(b), zeroExtend(a));
   endfunction

   // One microinstruction per clock (HW manual §2.0).
   (* fire_when_enabled *)
   rule rl_microcycle;
      Bit#(16) wvec = 0;
      for (Integer wi = 0; wi < 16; wi = wi + 1)
         wvec[wi] = pack(wake[fromInteger(wi)]);
      wvec[0] = 1;
      if (disk.wakeupSector) wvec[4] = 1;
      if (disk.wakeupWord)   wvec[14] = 1;
      if (disp.wakeupDVT) begin
         wvec[12] = 1;
         // Field start blocks DHT/DWT (Alto Hardware Manual / ContrAlto).
         wvec[11] = 0;
         wvec[9]  = 0;
      end
      if (disp.wakeupDHT)    wvec[11] = 1;
      // DWT request is evaluated after the pulse bits so a stale DHTBLOCK
      // from last field cannot cancel the line-start wakeup.
      if (disp.wakeupDHT || disp.wakeupDWT)
         wvec[9] = 1;
      else if (disp.dwtBlock || disp.dhtBlock || disp.fifoFull)
         wvec[9] = 0;
      if (disp.wakeupCURT)   wvec[10] = 1;
      if (disp.wakeupMRT)    wvec[8]  = 1;
      // Interface owns the Ethernet wakeup level (§7.2): data, command, or done.
      wvec[7] = pack(eth.wakeup);
      if (eth.countdown && disp.wakeupMRT)
         wvec[7] = 1;

      TaskId tsk = cur;
      let i = decodeU(fetchU(tsk, taskMpc[tsk]));
      let mop = memOpOf(i);
      Bool stall = needsMemory(i) && !mem.ready(mop);

      Word nt = t;
      Word nl = l;
      Word nm = m;
      Word nir = ir;
      Bit#(1) naluC0 = aluC0;
      Bit#(1) nskip = skip;
      Bit#(1) ncarry = carry;
      Word nrmr = rmr;
      TaskId ncur = cur;
      TaskId nnxt = nxt;
      Bool nswitch = switchPend;
      Bool nfirst = firstAfter;
      Bool nrd = rdRam;
      Bool nwrt = wrtRam;
      Bool nsw = swMode;
      Bool nsoft = False;
      Word ncram = cramAddr;
      Word ncramHalf = cramHalf;
      Maybe#(Tuple2#(RSel, Word)) rwr = tagged Invalid;
      Maybe#(Tuple3#(Bit#(3), RSel, Word)) swr = tagged Invalid;
      Maybe#(Tuple2#(Bit#(32), Bit#(32))) uwr = tagged Invalid;
      Vector#(16, UAddr) nmpc = newVector;
      Vector#(16, UAddr) nmod = newVector;
      Vector#(16, Bit#(3)) nsb = newVector;
      Vector#(16, Bit#(3)) nub = newVector;
      for (Integer i2 = 0; i2 < 16; i2 = i2 + 1) begin
         nmpc[i2] = taskMpc[fromInteger(i2)];
         nmod[i2] = taskMod[fromInteger(i2)];
         nsb[i2] = sBank[fromInteger(i2)];
         nub[i2] = uBank[fromInteger(i2)];
      end

      if (pwReset) begin
         for (Integer i2 = 0; i2 < 16; i2 = i2 + 1) begin
            nmpc[i2] = fromInteger(i2);
            // Emulator is always ready; KSEC must run its reset
            // (KPOQ) *before* the emulator writes the boot DCB.
            wvec[i2] = (i2 == 0 || i2 == 4) ? 1 : 0;
            nub[i2] = 0;
            nsb[i2] = 0;
         end
         ncur = 0; nnxt = 0; nswitch = False; nfirst = True;
         nrmr = 16'hFFFF; nskip = 0; ncarry = 0; naluC0 = 0;
         nrd = False; nwrt = False; nsw = False; nsoft = False;
         for (Integer i2 = 0; i2 < 16; i2 = i2 + 1)
            nmod[i2] = 0;
         mem.softReset();
         disk.reset();
         disp.reset();
         eth.reset();
      end
      else if (!stall) begin
         RSel rsel = i.rsel;
         if (tsk == 0) begin
            Bit#(4) f2v = pack(i.f2);
            if (f2v == fromInteger(emuACSOURCE))
               rsel = {rsel[4:2], ir[14:13] ^ 2'b11};
            else if (f2v == fromInteger(emuACDEST) || f2v == fromInteger(emuLoadDNS))
               rsel = {rsel[4:2], ir[12:11] ^ 2'b11};
         end

         Word bus = 16'hFFFF;
         Bool loadR = False;
         Bool loadS = False;
         Word cval = host_constant(zeroExtend(constantAddr(i.rsel, i.bs)));

         if (constantAccess(i))
            bus = cval;
         else if (i.bs == BsReadR)
            bus = r[rsel];
         else if (i.bs == BsLoadR) begin
            bus = 0; loadR = True;
         end
         else if (i.bs == BsNone)
            bus = 16'hFFFF;
         else if (i.bs == BsReadMD) begin
            bus = mem.peekMD();
            mem.takeMD();
         end
         else if (i.bs == BsReadMouse)
            bus = kbd.mouseBits | 16'hFFF0;
         else if (i.bs == BsReadDisp) begin
            bus = zeroExtend(ir[7:0]);
            if (ir[9:8] != 0 && ir[7] == 1)
               bus = bus | 16'hFF00;
         end
         else if (i.bs == BsTask1 || i.bs == BsTask2) begin
            if (tsk == 0) begin
               if (i.bs == BsTask1)
                  bus = (i.rsel == 0) ? m : s[sBank[tsk]][i.rsel];
               else begin
                  loadS = True; bus = 16'hFFFF;
               end
            end
            else if (tsk == 4 || tsk == 14)
               bus = (i.bs == BsTask1) ? disk.kstat : disk.kdata;
            else if (tsk == 7 && i.bs == BsTask2)
               bus = eth.peekFifo;
            else
               bus = 16'hFFFF;
         end

         if (bsUsesConstant(i.bs) && !constantAccess(i))
            bus = bus & cval;

         if (tsk == 0 && pack(i.f1) == fromInteger(emuRSNF))
            bus = bus & (16'hFF00 | fromInteger(etherHostAddress));
         if (tsk == 7 && pack(i.f1) == fromInteger(ethEILFCT))
            bus = bus & eth.peekFifo;
         if (tsk == 7 && pack(i.f1) == fromInteger(ethEPFCT)) begin
            bus = bus & eth.status;
            host_ether_post(bus);
         end
         // RDRAM: next-cycle AND of the CRAM halfword addressed by T (§8.3).
         if (rdRam && cramAddr[11] == 0) begin
            bus = bus & cramHalf;
            nrd = False;
         end
         else if (rdRam)
            nrd = False;

         AluOut ao = aluExec(i.aluf, bus, t, skip);
         Word alu = ao.result;

         ShOp sop = ShNone;
         ShMod smod = ModNone;
         if (i.f1 == F1LLSH1) sop = ShLeft;
         else if (i.f1 == F1LRSH1) sop = ShRight;
         else if (i.f1 == F1LLCY8) sop = ShCyc8;
         if (tsk == 0 && pack(i.f2) == fromInteger(emuMAGIC))
            smod = ModMagic;

         Bool doSwitch = False;
         if (i.f1 == F1LoadMAR)
            mem.loadMAR(alu, tsk, i.f2 == F2StoreMD);
         else if (i.f1 == F1Task && !firstAfter)
            doSwitch = True;
         else if (i.f1 == F1Block && tsk != 0)
            wvec[tsk] = 0;

         if (tsk == 0) begin
            Bit#(4) f1v = pack(i.f1);
            if (f1v == fromInteger(emuLoadRMR)) nrmr = bus;
            else if (f1v == fromInteger(emuSTARTF)) begin
               if (bus[15] == 1) nsoft = True;
               else if (bus[1:0] != 0) eth.startf(bus);
            end
            else if (f1v == fromInteger(emuSWMODE)) nsw = True;
            else if (f1v == fromInteger(emuRDRAM)) nrd = True;
            else if (f1v == fromInteger(emuWRTRAM)) nwrt = True;
            else if (f1v == fromInteger(emuLoadESRB)) nsb[tsk] = bus[3:1];
         end
         else if (tsk == 4 || tsk == 14) begin
            Bit#(4) f1v = pack(i.f1);
            if (f1v == fromInteger(dskLoadKDATA)) disk.setKDATA(bus);
            else if (f1v == fromInteger(dskLoadKADR)) disk.setKADR(bus & 16'h00FF);
            else if (f1v == fromInteger(dskLoadKCOMM)) disk.setKCOM(zeroExtend(bus[15:10]));
            else if (f1v == fromInteger(dskCLRSTAT)) disk.clrStat();
            else if (f1v == fromInteger(dskINCRECNO)) disk.incRec();
            else if (f1v == fromInteger(dskLoadKSTAT)) begin
               Word mb = (bus & 16'h000B) | ((~bus) & 16'h0004);
               disk.setKSTAT((disk.kstat & 16'hFFF4) | mb);
            end
            else if (f1v == fromInteger(dskSTROBE)) disk.strobe();
         end
         else if (tsk == 7) begin
            Bit#(4) f1v = pack(i.f1);
            if (f1v == fromInteger(ethEPFCT)) eth.postReset();
            else if (f1v == fromInteger(ethEWFCT)) eth.setCountdown();
         end
         if (tsk == 7 && i.bs == BsTask2)
            eth.takeFifo();

         UAddr applied = taskMod[tsk];
         UAddr newmod = 0;

         if (i.f2 == F2BusEq0 && bus == 0) newmod = newmod | 1;
         else if (i.f2 == F2Bus) newmod = newmod | truncate(bus);
         else if (i.f2 == F2ALUCY) newmod = newmod | zeroExtend(aluC0);
         else if (i.f2 == F2StoreMD && i.f1 != F1LoadMAR)
            mem.loadMD(bus);

         if (tsk == 4 || tsk == 14) begin
            UAddr initb = (tsk == 14 && disk.wdInit) ? 10'h01F : 0;
            Bit#(4) f2v = pack(i.f2);
            if (f2v == fromInteger(dskINIT)) newmod = newmod | initb;
            else if (f2v == fromInteger(dskRWC)) begin
               newmod = newmod | initb;
               Bit#(2) cmd = disk.kadr[7:6];
               if (cmd == 1) newmod = newmod | 2;
               else if (cmd == 2 || cmd == 3) newmod = newmod | 3;
            end
            else if (f2v == fromInteger(dskXFRDAT)) begin
               newmod = newmod | initb;
               if (disk.dataXfer) newmod = newmod | 1;
            end
            else if (f2v == fromInteger(dskRECNO))
               newmod = newmod | initb | truncate(disk.recno);
            else if (f2v == fromInteger(dskNFER)) begin
               newmod = newmod | initb;
               if (!disk.fatalError) newmod = newmod | 1;
            end
            else if (f2v == fromInteger(dskSTROBON)) begin
               newmod = newmod | initb;
               if (disk.strobeOn) newmod = newmod | 1;
            end
            else if (f2v == fromInteger(dskSWRNRDY)) begin
               newmod = newmod | initb;
               if (!disk.ready) newmod = newmod | 1;
            end
         end

         if (tsk == 7) begin
            Bit#(4) f2v = pack(i.f2);
            if (f2v == fromInteger(ethEODFCT)) eth.writeFifo(bus);
            else if (f2v == fromInteger(ethEOSFCT)) eth.startOutput();
            else if (f2v == fromInteger(ethERBFCT))
               newmod = newmod | {6'b0, eth.ioCmd, 2'b0};
            else if (f2v == fromInteger(ethEEFCT)) eth.endTx();
            else if (f2v == fromInteger(ethEBFCT)) begin
               if (eth.dataLate || eth.ioCmd != 0 || eth.opDone)
                  newmod = newmod | 10'h004;
               if (eth.collision)
                  newmod = newmod | 10'h008;
            end
            else if (f2v == fromInteger(ethECBFCT) && !eth.fifoEmpty)
               newmod = newmod | 10'h004;
            else if (f2v == fromInteger(ethEISFCT)) eth.startInput();
         end

         if (tsk == 12 && pack(i.f2) == 8 && disp.evenField) newmod = newmod | 1;
         if (tsk == 11) begin
            if (pack(i.f2) == 8 && disp.evenField) newmod = newmod | 1;
            if (pack(i.f2) == 9) begin
               disp.setMode(bus);
               if (bus[15] == 1) newmod = newmod | 1;
            end
         end
         if (tsk == 9 && pack(i.f2) == 8) disp.loadDDR(bus);
         if (tsk == 10) begin
            if (pack(i.f2) == 8) disp.loadXPREG(bus);
            if (pack(i.f2) == 9) disp.loadCSR(bus);
         end

         Bit#(1) dnsCarryIn = carry;
         Bool dns = (tsk == 0 && pack(i.f2) == fromInteger(emuLoadDNS));
         if (tsk == 0) begin
            Bit#(4) f2v = pack(i.f2);
            if (f2v == fromInteger(emuLoadIR)) begin
               nir = bus;
               newmod = newmod | {6'b0, bus[15], bus[10:8]};
               nskip = 0;
            end
            else if (f2v == fromInteger(emuIDISP)) begin
               if (ir[15] == 1)
                  // 3-IR[8-9]: Alto bits 8-9 are modern [7:6] (shift field).
                  newmod = newmod | zeroExtend(2'b11 - ir[7:6]);
               else
                  newmod = newmod | zeroExtend(host_acs(zeroExtend({1'b1, ir[14:8]})));
            end
            else if (f2v == fromInteger(emuACSOURCE)) begin
               if (ir[15] == 1)
                  newmod = newmod | zeroExtend(2'b11 - ir[7:6]);
               else
                  newmod = newmod | zeroExtend(host_acs(zeroExtend(ir[14:8])));
            end
            else if (f2v == fromInteger(emuBUSODD))
               newmod = newmod | zeroExtend(bus[0]);
            else if (dns) begin
               loadR = (ir[3] == 0);
               Bit#(2) cc = ir[5:4];
               Bit#(1) cin = case (cc)
                  0: carry;
                  1: 0;
                  2: 1;
                  default: ~carry;
               endcase;
               Bit#(3) op = ir[10:8];
               if ((op == 1 || op == 3 || op == 4 || op == 5 || op == 6) && aluC0 == 1)
                  cin = ~cin;
               dnsCarryIn = cin;
               smod = ModDNS;
            end
         end

         ShOut so = doShift(sop, smod, l, t, dnsCarryIn);
         Word sh = (sop == ShNone && smod == ModNone) ? l : so.out;
         if (i.f2 == F2ShLt0 && sh[15] == 1) newmod = newmod | 1;
         if (i.f2 == F2ShEq0 && sh == 0) newmod = newmod | 1;

         if (dns) begin
            Bit#(1) sk = case (ir[2:0])
               0: 0;
               1: 1;
               2: pack(so.dnsCarry == 0);
               3: so.dnsCarry;
               4: pack(sh == 0);
               5: pack(sh != 0);
               6: pack(sh == 0 || so.dnsCarry == 0);
               7: pack(sh != 0 && so.dnsCarry != 0);
            endcase;
            nskip = sk;
            if (loadR) ncarry = so.dnsCarry;
         end

         if (loadR) rwr = tagged Valid tuple2(rsel, sh);
         if (loadS) swr = tagged Valid tuple3(sBank[tsk], i.rsel, m);
         if (i.loadT) begin
            nt = loadTFromALU(i.aluf) ? alu : bus;
            ncram = alu;
            ncramHalf = host_cram_half(zeroExtend(alu));
         end
         if (i.loadL) begin
            nl = alu;
            if (tsk == 0) nm = alu;
            naluC0 = ao.carry;
         end

         if (wrtRam) begin
            nwrt = False;
            if (cramAddr[11] == 0)
               uwr = tagged Valid tuple2(zeroExtend(cramAddr[9:0]),
                                         {m, alu} ^ 32'h00088400);
         end

         Bool dropSeclate = False;
         if (i.f1 == F1Block) begin
            if (tsk == 14)
               disk.setWdInit(False);
            if (tsk == 11) disp.setDhtBlock(True);
            if (tsk == 9) begin
               disp.setDwtBlock(True);
               if (!disp.dhtBlock) wvec[11] = 1;
            end
            if (tsk == 4) dropSeclate = True;
         end

         if (swMode) begin
            nsw = False;
            nub[tsk] = (uBank[tsk] == 0) ? 3'd2 : 3'd0;
         end

         if (softRst) begin
            for (Integer ti = 0; ti < 16; ti = ti + 1) begin
               nmpc[ti] = fromInteger(ti);
               nub[ti] = unpack(rmr[ti]) ? 0 : 2;
            end
            nrmr = 16'hFFFF;
            mem.softReset();
            ncur = 0; nnxt = 0;
            wvec[4] = 1; wvec[14] = 0;
         end
         else
            nmpc[tsk] = i.next | applied;

         nmod[tsk] = newmod;

         if (doSwitch)
            nswitch = True;

         if (switchPend && !doSwitch) begin
            TaskId ht = 0;
            Bool found = False;
            for (Integer ti = 15; ti >= 0; ti = ti - 1) begin
               if (!found && wvec[ti] == 1) begin
                  ht = fromInteger(ti);
                  found = True;
               end
            end
            nnxt = ht; ncur = ht; nfirst = True; nswitch = False;
            if (ht == 4) dropSeclate = True;
            if (ht == 12) wvec[12] = 0;
            if (ht == 11) wvec[11] = 0;
            if (ht == 10) wvec[10] = 0;
            if (ht == 7) eth.ackCountdown();
         end
         else
            nfirst = False;

         if (dropSeclate)
            disk.disableSeclate();
      end

      if (rwr matches tagged Valid {.ri, .rv}) r[ri] <= rv;
      if (swr matches tagged Valid {.b, .si, .sv}) s[b][si] <= sv;
      if (uwr matches tagged Valid {.ua, .uw}) host_cram_write(ua, uw);

      t <= nt; l <= nl; m <= nm; ir <= nir;
      aluC0 <= naluC0; skip <= nskip; carry <= ncarry; rmr <= nrmr;
      cur <= ncur; nxt <= nnxt; switchPend <= nswitch; firstAfter <= nfirst;
      rdRam <= nrd; wrtRam <= nwrt; swMode <= nsw; softRst <= nsoft;
      cramAddr <= ncram;
      cramHalf <= ncramHalf;
      waiting <= stall && !pwReset;
      cycn <= pwReset ? 0 : cycn + 1;
      for (Integer i2 = 0; i2 < 16; i2 = i2 + 1) begin
         wake[fromInteger(i2)] <= unpack(wvec[i2]);
         taskMpc[fromInteger(i2)] <= nmpc[i2];
         taskMod[fromInteger(i2)] <= nmod[i2];
         sBank[fromInteger(i2)] <= nsb[i2];
         uBank[fromInteger(i2)] <= nub[i2];
      end
   endrule

   method Action reset();
      pwReset.send();
   endmethod

   method TaskId curTask = cur;
   method UAddr  mpc = taskMpc[cur];
   method Word   tReg = t;
   method Word   lReg = l;
   method Word   irReg = ir;
   method Word   r6 = r[6];
   method Word   ac0 = r[3];
   method Word   ac1 = r[2];
   method Word   ac2 = r[1];
   method Word   ac3 = r[0];
   method Bit#(64) cycles = cycn;
   method Bool   memWait = waiting;
endmodule

endpackage
