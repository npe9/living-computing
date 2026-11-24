// Alto 3 Mbps Ethernet interface — Hardware Manual (May 1979) §7.
// 16-word FIFO, ICMD/OCMD from STARTF BUS[14-15], countdown on SWAKMRT.

package Ethernet;

import Vector::*;
import ConfigReg::*;
import AltoTypes::*;

import "BDPI" function Action   host_ether_tx_word(Bit#(16) w);
import "BDPI" function Action   host_ether_tx_end();
import "BDPI" function Bit#(32) host_ether_rx_count();
import "BDPI" function ActionValue#(Bit#(16)) host_ether_rx_word();
import "BDPI" function Action   host_ether_reset();
import "BDPI" function Action   host_ether_rx_rewind();
import "BDPI" function Action   host_ether_rx_release();

interface Ethernet_IFC;
   method Word  status;
   method Word  peekFifo;
   method Action takeFifo;
   method Action writeFifo(Word w);
   method Action startf(Word bus);
   method Action startOutput();
   method Action startInput();
   method Action endTx();
   method Action postReset();
   method Action setCountdown();
   method Action ackCountdown();
   method Bool  wakeup;
   method Bool  countdown;
   method Bit#(2) ioCmd;
   method Bool  fifoEmpty;
   method Bool  dataLate;
   method Bool  collision;
   method Bool  opDone;
   method Action reset();
endinterface

module mkEthernet(Ethernet_IFC);
   Vector#(16, Reg#(Word)) fifo <- replicateM(mkConfigReg(0));
   Reg#(Bit#(5))  fcnt <- mkConfigReg(0);
   Reg#(Bit#(4))  frd  <- mkConfigReg(0);
   Reg#(Bit#(4))  fwr  <- mkConfigReg(0);

   Reg#(Bit#(2)) ioCmdR  <- mkConfigReg(0);
   Reg#(Bool)    oBusy   <- mkConfigReg(False);
   Reg#(Bool)    iBusy   <- mkConfigReg(False);
   Reg#(Bool)    late    <- mkConfigReg(False);
   Reg#(Bool)    coll    <- mkConfigReg(False);
   Reg#(Bool)    crcBad  <- mkConfigReg(False);
   Reg#(Bool)    incomp  <- mkConfigReg(False);
   Reg#(Bool)    inGone  <- mkConfigReg(False);
   Reg#(Bool)    cdWake  <- mkConfigReg(False);
   Reg#(Bool)    wakeR   <- mkConfigReg(False);
   Reg#(Word)    statR   <- mkConfigReg(16'hFFFF);

   Reg#(Bit#(16)) txTmr  <- mkReg(0);
   Reg#(Bool)     txPend <- mkReg(False);
   Reg#(Bool)     txEnd  <- mkReg(False);
   Reg#(Bit#(16)) rxTmr  <- mkReg(0);
   // Only fill the receive FIFO after EISFCT, never while transmitting.
   // A TX post (EPFCT) would otherwise wipe a packet we just stuffed.
   Reg#(Bool)     rxArm  <- mkReg(False);

   RWire#(Word) rwStartf <- mkRWire;
   RWire#(Word) rwWr     <- mkRWire;
   PulseWire pwTake  <- mkPulseWire;
   PulseWire pwOut   <- mkPulseWire;
   PulseWire pwIn    <- mkPulseWire;
   PulseWire pwEot   <- mkPulseWire;
   PulseWire pwPost  <- mkPulseWire;
   PulseWire pwCd    <- mkPulseWire;
   PulseWire pwAckCd <- mkPulseWire;
   PulseWire pwRst   <- mkPulseWire;

   function Word hwStatus();
      // EPLOC[8-15] low-true (§7.1). Bits 8-9 unused (=1).
      Word s = 16'hFFC0;
      if (!late)  s = s | 16'h0020;
      if (!coll)  s = s | 16'h0010;
      if (!crcBad)s = s | 16'h0008;
      s = s | 16'h0006;   // last SIO bits, cleared at post
      if (!incomp) s = s | 16'h0001;
      return s;
   endfunction

   (* fire_when_enabled, no_implicit_conditions *)
   rule rl_ether;
      Bit#(5)  n  = fcnt;
      Bit#(4)  rd = frd;
      Bit#(4)  wr = fwr;
      Bool     ob = oBusy;
      Bool     ib = iBusy;
      Bool     ig = inGone;
      Bool     wk = wakeR;
      Bool     cd = cdWake;
      Bit#(2)  cmd = ioCmdR;
      Bit#(16) tt = txTmr;
      Bool     tp = txPend;
      Bool     te = txEnd;
      Bit#(16) rt = rxTmr;
      Bool     arm = rxArm;
      Maybe#(Tuple2#(Bit#(4), Word)) fifoWr = tagged Invalid;
      Maybe#(Word) txWord = tagged Invalid;
      Bool doTxEnd = False;
      Bool doRx = False;

      if (pwRst) begin
         n = 0; rd = 0; wr = 0;
         ob = False; ib = False; ig = False;
         cmd = 0; cd = False; wk = False;
         late <= False; coll <= False; crcBad <= False; incomp <= False;
         tt = 0; tp = False; te = False; rt = 0; arm = False;
         host_ether_reset();
      end
      else begin
         if (rwStartf.wget matches tagged Valid .v) begin
            cmd = v[1:0];
            wk = True;
         end
         if (pwCd) cd = True;
         if (pwAckCd) cd = False;

         if (pwPost) begin
            statR <= hwStatus();
            cmd = 0; ob = False; ib = False; ig = False;
            n = 0; rd = 0; wr = 0;
            late <= False; coll <= False; crcBad <= False; incomp <= False;
            tp = False; te = False; tt = 0; arm = False;
            wk = False;
            host_ether_rx_rewind();
         end

         if (pwOut) begin
            ob = True;
            arm = False;
            wk = True;   // fill the FIFO
         end
         if (pwIn) begin
            ib = True;
            ig = False;
            arm = True;
            host_ether_rx_release();
            rt = (host_ether_rx_count() != 0) ? 0 : fromInteger(etherWordCycles);
            wk = False;  // hunt; wake when two words are in the FIFO
         end
         if (pwEot) begin
            te = True;
            tp = True;
            tt = fromInteger(etherGapCycles);
            wk = False;
         end

         if (rwWr.wget matches tagged Valid .w) begin
            if (n >= 16) begin
               rd = rd + 1;
               n = n - 1;
            end
            fifoWr = tagged Valid tuple2(wr, w);
            wr = wr + 1;
            n = n + 1;
            txWord = tagged Valid w;
            if (ob && n >= 15) begin
               tp = True;
               tt = fromInteger(etherGapCycles);
               wk = False;  // FIFO full; wait for the wire
            end
         end

         if (pwTake && n != 0) begin
            rd = rd + 1;
            n = n - 1;
            if (n < 2) begin
               if (ig) begin
                  ib = False;
                  wk = True;
               end
               else
                  wk = False;
            end
         end

         if (tp) begin
            if (tt == 0) begin
               tp = False;
               if (te) begin
                  te = False;
                  ob = False;
                  arm = False;
                  ib = False;
                  doTxEnd = True;
                  wk = True;
               end
               else if (ob)
                  wk = True;
            end
            else
               tt = tt - 1;
         end

         if (ib && !ig && arm && !ob && !tp) begin
            if (rt == 0) begin
               rt = fromInteger(etherWordCycles);
               if (host_ether_rx_count() != 0) begin
                  if (n < 16) begin
                     doRx = True;
                     wr = wr + 1;
                     n = n + 1;
                     if (n >= 2)
                        wk = True;
                  end
                  // FIFO full: wait (do not flag data-late; the µcode
                  // has not drained yet).
               end
               else if (n < 2 && n != 0) begin
                  ig = True;
                  ib = False;
                  wk = True;
               end
               else if (n == 0 && host_ether_rx_count() == 0) begin
                  // still hunting
               end
            end
            else
               rt = rt - 1;
         end
      end

      if (txWord matches tagged Valid .w)
         host_ether_tx_word(w);
      if (doTxEnd)
         host_ether_tx_end();
      if (doRx) begin
         Word rw <- host_ether_rx_word();
         fifo[wr - 1] <= rw;
      end
      if (fifoWr matches tagged Valid {.i, .w})
         fifo[i] <= w;

      fcnt <= n; frd <= rd; fwr <= wr;
      oBusy <= ob; iBusy <= ib; inGone <= ig;
      ioCmdR <= cmd; cdWake <= cd; wakeR <= wk;
      txTmr <= tt; txPend <= tp; txEnd <= te; rxTmr <= rt; rxArm <= arm;
   endrule

   method Word status = hwStatus();
   method Word peekFifo = (fcnt == 0) ? 0 : fifo[frd];
   method Action takeFifo(); pwTake.send(); endmethod
   method Action writeFifo(Word w); rwWr.wset(w); endmethod
   method Action startf(Word bus); rwStartf.wset(bus); endmethod
   method Action startOutput(); pwOut.send(); endmethod
   method Action startInput(); pwIn.send(); endmethod
   method Action endTx(); pwEot.send(); endmethod
   method Action postReset(); pwPost.send(); endmethod
   method Action setCountdown(); pwCd.send(); endmethod
   method Action ackCountdown(); pwAckCd.send(); endmethod
   method Bool wakeup = wakeR;
   method Bool countdown = cdWake;
   method Bit#(2) ioCmd = ioCmdR;
   method Bool fifoEmpty = fcnt == 0;
   method Bool dataLate = late;
   method Bool collision = coll;
   method Bool opDone = !oBusy && !iBusy;
   method Action reset(); pwRst.send(); endmethod
endmodule

endpackage
