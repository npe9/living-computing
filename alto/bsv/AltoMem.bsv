// Alto II main memory and I/O page (named AltoMem to avoid clashing with Prelude Memory).

package AltoMem;

import Vector::*;
import RegFile::*;
import ConfigReg::*;
import AltoTypes::*;

interface Memory_IFC;
   method Bool ready(MemOp op);
   method Action loadMAR(Word addr, TaskId tsk, Bool xm);
   method Word peekMD();
   method Action takeMD();
   method Action loadMD(Word data);
   method Action softReset();
   method Word   peek(Bit#(18) phys);
   method Action poke(Bit#(18) phys, Word data);
   method Word   mar;
endinterface

interface IoPage_IFC;
   method Word read(Word addr);
   method Action write(Word addr, Word data);
endinterface

typedef struct {
   Word   addr;
   TaskId tsk;
   Bool   xm;
} MarReq deriving (Bits);

module mkMemory#(IoPage_IFC io)(Memory_IFC);
   RegFile#(Bit#(18), Word) ram <- mkRegFileFull;
   Vector#(16, Reg#(Bit#(4))) xmBanks <- replicateM(mkConfigReg(0));

   Reg#(Word)  marReg    <- mkConfigReg(0);
   Reg#(TaskId) taskReg  <- mkConfigReg(0);
   Reg#(Bool)  xmReg     <- mkConfigReg(False);
   Reg#(Word)  mdLow     <- mkConfigReg(0);
   Reg#(Word)  mdHigh    <- mkConfigReg(0);
   Reg#(Bool)  firstWord <- mkConfigReg(False);
   Reg#(Bool)  active    <- mkConfigReg(False);
   Reg#(Bit#(3)) memcyc  <- mkConfigReg(0);

   RWire#(MarReq) marW  <- mkRWire;
   RWire#(Word)   mdW   <- mkRWire;
   PulseWire      rdW   <- mkPulseWire;
   PulseWire      rstW  <- mkPulseWire;

   function Bit#(2) bankOf(TaskId tsk, Bool xm);
      let b = xmBanks[tsk];
      return xm ? b[1:0] : b[3:2];
   endfunction

   function Bit#(18) physOf(Word a, TaskId tsk, Bool xm);
      return {bankOf(tsk, xm), a};
   endfunction

   function Bit#(4) xmIdx(Word a) = truncate(a - xmBankBase);

   function Word busRead(Word a, TaskId tsk, Bool xm);
      if (a >= xmBankBase && a < xmBankBase + 16)
         return 16'hFFF0 | zeroExtend(xmBanks[xmIdx(a)]);
      else if (a <= ramTop)
         return ram.sub(physOf(a, tsk, xm));
      else
         return io.read(a);
   endfunction

   function Action busWrite(Word a, Word d, TaskId tsk, Bool xm);
      action
         if (a >= xmBankBase && a < xmBankBase + 16)
            xmBanks[xmIdx(a)] <= d[3:0];
         else if (a <= ramTop)
            ram.upd(physOf(a, tsk, xm), d);
         else
            io.write(a, d);
      endaction
   endfunction

   // Alto II memory: 5 cycles, 6 if the odd word is used (HW manual §2).
   (* fire_when_enabled, no_implicit_conditions *)
   rule rl_memcycle;
      Bool fw = firstWord;
      Bool act = active;
      Bit#(3) cyc = memcyc;
      Word lo = mdLow;
      Word hi = mdHigh;

      if (rstW) begin
         for (Integer i = 0; i < 16; i = i + 1)
            xmBanks[fromInteger(i)] <= 0;
         act = False;
         cyc = 0;
         fw = False;
      end
      else begin
         // <-MD / MD<- first so a same-cycle MAR<- (BravoX) sees the old data.
         if (mdW.wget matches tagged Valid .d) begin
            Word a = fw ? (marReg ^ 16'h0001) : marReg;
            busWrite(a, d, taskReg, xmReg);
            fw = !fw;
         end
         else if (rdW)
            fw = !fw;

         if (marW.wget matches tagged Valid .req) begin
            marReg  <= req.addr;
            taskReg <= req.tsk;
            xmReg   <= req.xm;
            fw = False;
            act = True;
            cyc = 2;   // cycle 1 is the MAR<- instruction; clock advances it
         end
         else if (act) begin
            Bit#(3) n = cyc + 1;
            if (n == 3)
               lo = busRead(marReg, taskReg, xmReg);
            if (n == 4)
               hi = busRead(marReg ^ 16'h0001, taskReg, xmReg);
            if (n >= 6)
               act = False;
            cyc = n;
         end
      end

      firstWord <= fw;
      active    <= act;
      memcyc    <= cyc;
      mdLow     <= lo;
      mdHigh    <= hi;
   endrule

   method Bool ready(MemOp op);
      if (!active) return True;
      else if (op == MemLoadAddr) return False;
      else if (op == MemRead) return memcyc > 4;
      else if (op == MemStore) return memcyc > 2;
      else return True;
   endmethod

   method Action loadMAR(Word addr, TaskId tsk, Bool xm);
      marW.wset(MarReq { addr: addr, tsk: tsk, xm: xm });
   endmethod

   method Word peekMD = firstWord ? mdHigh : mdLow;

   method Action takeMD();
      rdW.send();
   endmethod

   method Action loadMD(Word data);
      mdW.wset(data);
   endmethod

   method Action softReset();
      rstW.send();
   endmethod

   method Word peek(Bit#(18) phys) = ram.sub(phys);
   method Action poke(Bit#(18) phys, Word data);
      ram.upd(phys, data);
   endmethod
   method Word mar = marReg;
endmodule

endpackage
