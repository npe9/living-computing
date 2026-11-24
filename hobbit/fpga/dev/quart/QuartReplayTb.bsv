// QuartReplayTb.bsv -- replay a register-access trace into the Quart and
// interrupt-path RTL and compare with the Python models' answers.
//
// The vectors come from quart_trace.py (see its docstring for the trace
// and vector formats); run_tests.sh builds them from a trace, builds this
// testbench, and runs it.  The vector file is read with $readmemh as
// "vectors.hex" in the working directory.
//
// For every record:
//   access  wait until every transmitter has drained (the Python model
//           transmits in zero time, so the two agree only with empty TX
//           FIFOs), then issue the access to the device it names and
//           compare: the read value, and whether the device raised a fault
//           (its fault count went up by exactly one) against whether the
//           Python model stopped (Stop / BusError).  The counters must not
//           have expired more often than the trace says.
//   tick    wait until the RTL counter of that DUART has expired N more
//           times (it must: a timeout is a mismatch)
//   rx      drive the byte in: channel 0 as 8N1 on the rxd pin, channels
//           1..3 through rxIn; wait until it is in the FIFO
//   tx      the next byte the RTL transmitted on that channel (channel 0
//           decoded from the txd pin) must be this one
//   ext     the other interrupt requests into Irq.sources (bit 1 is the
//           Quart's irq, wired here as the board wires it)
//   sample  after the drain, Quart irq and Irq IL6 must equal the model's
//
// Output: one MISMATCH line per difference (run_tests.sh counts them),
// then  SUMMARY records=N accesses=A cycles=C
//
// Discrimination: README.md "Discrimination" lists the injected bugs and
// the failures observed for each.

package QuartReplayTb;

import Vector :: *;
import FIFOF :: *;
import RegFile :: *;
import GetPut :: *;
import HobbitQuart :: *;
import HobbitIntc :: *;

typedef 20 IdxBits;
Integer cpb = 4;            // channel 0: 4 clocks a bit in simulation
Integer ctDen = 2;          // C/T clock = clock / 2

typedef enum { Fetch, Drain, Resp, Settle, Tick, RxWait, TxWait, Done }
  Phase deriving (Bits, Eq);

(* synthesize *)
module mkQuartReplayTb(Empty);
  HobbitQuart q <- mkHobbitQuart(cpb, 1, ctDen);
  HobbitIrq irq <- mkHobbitIrq;
  HobbitIoctl ioctl <- mkHobbitIoctl;
  HobbitIncon incon <- mkHobbitIncon;
  RegFile#(Bit#(IdxBits), Bit#(128)) vec <- mkRegFileLoad("vectors.hex", 0,
                                                          '1);
  Reg#(Bit#(IdxBits)) idx <- mkReg(0);
  Reg#(Phase) phase <- mkReg(Fetch);
  Reg#(Bit#(32)) wait_ <- mkReg(0);
  Reg#(Bit#(32)) cycle <- mkReg(0);
  Reg#(Bit#(16)) ext <- mkReg(0);
  Reg#(Bit#(32)) nacc <- mkReg(0);
  Reg#(Bit#(16)) faults0 <- mkReg(0);
  Vector#(2, Reg#(Bit#(16))) expE <- replicateM(mkReg(0));
  Reg#(Bit#(4)) rxBefore <- mkReg(0);

  // ---- channel 0 line: a TB transmitter on rxd, a TB receiver on txd
  Reg#(Bit#(10)) tbSh <- mkReg('1);
  Reg#(Bit#(4)) tbLeft <- mkReg(0);
  Reg#(Bit#(16)) tbCnt <- mkReg(0);
  Reg#(Bool) tbBusy <- mkReg(False);
  Reg#(Bit#(4)) dBit <- mkReg(0);
  Reg#(Bit#(16)) dCnt <- mkReg(0);
  Reg#(Bit#(8)) dSh <- mkReg(0);
  Vector#(4, FIFOF#(Bit#(8))) got <- replicateM(mkSizedFIFOF(64));

  Bit#(16) bitc = fromInteger(cpb);

  rule clk;
    cycle <= cycle + 1;
  endrule

  rule wires;
    q.rxd(tbSh[0]);
    irq.sources((ext & ~16'h2) | (q.irq ? 16'h2 : 0));
  endrule

  rule tbTx (tbBusy);
    if (tbCnt != 0) tbCnt <= tbCnt - 1;
    else if (tbLeft == 0) begin tbBusy <= False; tbSh <= '1; end
    else begin
      tbSh <= {1'b1, tbSh[9:1]};
      tbLeft <= tbLeft - 1;
      tbCnt <= bitc - 1;
    end
  endrule

  rule tbRx;
    Bit#(1) v = q.txd;
    if (dBit == 0) begin
      if (v == 0) begin dBit <= 1; dCnt <= bitc / 2; end
    end
    else if (dCnt != 0) dCnt <= dCnt - 1;
    else if (dBit == 1) begin dBit <= 2; dCnt <= bitc - 1; end
    else if (dBit <= 9) begin
      dSh <= {v, dSh[7:1]};
      dBit <= dBit + 1;
      dCnt <= bitc - 1;
    end
    else begin
      dBit <= 0;
      if (v == 0) $display("MISMATCH channel 0 txd: framing error");
      got[0].enq(dSh);
    end
  endrule

  for (Integer i = 1; i < 4; i = i + 1)
    rule sink;
      let b <- q.txOut[i - 1].get;
      got[i].enq(b);
    endrule

  Bit#(128) v = vec.sub(idx);
  Bit#(4) op = v[127:124];
  Bit#(4) dev = v[123:120];
  Bool wr = v[119] == 1;
  Bit#(4) be = v[118:115];
  Bit#(12) off = v[114:103];
  Bit#(32) wdata = v[102:71];
  Bit#(32) expv = v[70:39];
  Bool experr = v[38] == 1;
  Bool expq = v[37] == 1;
  Bool expil6 = v[36] == 1;
  Bit#(4) vch = v[35:32];
  Bit#(16) vcnt = v[31:16];
  Bit#(16) varg = v[15:0];

  function Bit#(16) devFaults(Bit#(4) d) =
    case (d) 0: q.faults; 1: irq.faults; 2: ioctl.faults;
             default: incon.faults; endcase;

  Bool quiet = q.dbg.txIdle && !tbBusy && dBit == 0;

  function Action mismatch(Fmt f);
    action
      $display(fshow("MISMATCH vec ") + fshow(idx) + fshow(": ") + f);
    endaction
  endfunction

  function Action next;
    action
      idx <= idx + 1;
      phase <= Fetch;
      wait_ <= 0;
    endaction
  endfunction

  // no expiries beyond the trace's
  function Action checkCtr;
    action
      for (Integer d = 0; d < 2; d = d + 1)
        if (q.dbg.ctrExpiries[d] != expE[d])
          mismatch($format("DUART %0d counter expired %0d times, the trace %0d",
                           d, q.dbg.ctrExpiries[d], expE[d]));
    endaction
  endfunction

  rule fetch (phase == Fetch);
    case (op)
      0: phase <= Done;
      1, 6: begin phase <= Drain; wait_ <= 0; end
      2: begin
           phase <= Tick;
           wait_ <= 0;
           for (Integer d = 0; d < 2; d = d + 1)
             if (vch == fromInteger(d)) expE[d] <= expE[d] + vcnt;
         end
      3: begin
           rxBefore <= q.dbg.rxLevel[vch[1:0]];
           if (vch == 0) begin
             tbSh <= {1'b1, varg[7:0], 1'b0};
             tbLeft <= 9;
             tbCnt <= bitc - 1;
             tbBusy <= True;
           end
           phase <= RxWait;
           wait_ <= 0;
         end
      4: begin phase <= TxWait; wait_ <= 0; end
      5: begin ext <= varg; next; end
      default: begin mismatch($format("bad op %0d", op)); next; end
    endcase
  endrule

  // drain, then three quiet clocks
  rule drain (phase == Drain);
    if (!quiet) wait_ <= 0;
    else if (wait_ < 3) wait_ <= wait_ + 1;
    else if (op == 6) begin
      checkCtr;
      if (q.irq != expq || irq.il6 != expil6)
        mismatch($format("irq %0d IL6 %0d, the model %0d %0d",
                         q.irq, irq.il6, expq, expil6));
      next;
    end
    else begin
      checkCtr;
      faults0 <= devFaults(dev);
      case (dev)
        0: q.req(off, wdata, be, wr);
        1: irq.req(off, wdata, be, wr);
        2: ioctl.req(off, wdata, be, wr);
        default: incon.req(off, wdata, be, wr);
      endcase
      nacc <= nacc + 1;
      phase <= Resp;
    end
  endrule

  Reg#(Bit#(32)) rdata <- mkReg(0);
  rule resp (phase == Resp);
    Bit#(32) r = 0;
    case (dev)
      0: r <- q.resp;
      1: r <- irq.resp;
      2: r <- ioctl.resp;
      default: r <- incon.resp;
    endcase
    rdata <= r;
    phase <= Settle;
    wait_ <= 0;
  endrule

  rule settle (phase == Settle);
    if (wait_ < 2) wait_ <= wait_ + 1;
    else begin
      Bit#(16) df = devFaults(dev) - faults0;
      Bool err = df != 0;
      if (df > 1)
        mismatch($format("dev %0d +0x%03x: %0d faults from one access",
                         dev, off, df));
      if (err != experr)
        mismatch($format("dev %0d %s +0x%03x data %08x be %x: fault %0d, the model %s",
                         dev, wr ? "write" : "read", off, wdata, be, err,
                         experr ? "stopped" : "did not"));
      if (!wr && !experr && rdata != expv)
        mismatch($format("dev %0d read +0x%03x = %08x, the model %08x",
                         dev, off, rdata, expv));
      next;
    end
  endrule

  rule tick (phase == Tick);
    Bit#(1) d = vch[0];
    Bit#(16) e = q.dbg.ctrExpiries[d];
    Bit#(16) want = expE[d];
    if (e == want) next;
    else if (e > want) begin
      mismatch($format("DUART %0d counter at %0d expiries, the trace %0d",
                       d, e, want));
      next;
    end
    else if (wait_ > 32'h0100_0000) begin
      mismatch($format("DUART %0d counter never expired (%0d, the trace %0d)",
                       d, e, want));
      expE[d] <= e;
      next;
    end
    else wait_ <= wait_ + 1;
  endrule

  rule rxWaitStream (phase == RxWait && vch != 0);
    case (vch)
      1: q.rxIn[0].put(varg[7:0]);
      2: q.rxIn[1].put(varg[7:0]);
      default: q.rxIn[2].put(varg[7:0]);
    endcase
    next;
  endrule
  rule rxWaitStreamStuck (phase == RxWait && vch != 0 && wait_ < 32'h1000);
    wait_ <= wait_ + 1;
  endrule
  rule rxStreamTimeout (phase == RxWait && vch != 0 && wait_ >= 32'h1000);
    mismatch($format("channel %0d: rxIn did not take 0x%02x", vch, varg));
    next;
  endrule
  (* descending_urgency = "rxWaitStream, rxWaitStreamStuck, rxStreamTimeout" *)
  rule rxWaitPin (phase == RxWait && vch == 0);
    if (!tbBusy && q.dbg.rxLevel[0] == rxBefore + 1) next;
    else if (!tbBusy && wait_ > 32'h100) begin
      mismatch($format("channel 0: 0x%02x did not reach the FIFO (level %0d)",
                       varg, q.dbg.rxLevel[0]));
      next;
    end
    else wait_ <= wait_ + 1;
  endrule

  rule txWait (phase == TxWait);
    Bool have = False;
    Bit#(8) b = 0;
    for (Integer i = 0; i < 4; i = i + 1)
      if (vch == fromInteger(i) && got[i].notEmpty) begin
        have = True; b = got[i].first;
      end
    if (have) begin
      for (Integer i = 0; i < 4; i = i + 1)
        if (vch == fromInteger(i)) got[i].deq;
      if (b != varg[7:0])
        mismatch($format("channel %0d transmitted 0x%02x, the model 0x%02x",
                         vch, b, varg));
      next;
    end
    else if (wait_ > 32'h1000) begin
      mismatch($format("channel %0d: no byte transmitted, the model 0x%02x",
                       vch, varg));
      next;
    end
    else wait_ <= wait_ + 1;
  endrule

  rule done (phase == Done);
    for (Integer i = 0; i < 4; i = i + 1)
      if (got[i].notEmpty)
        $display("MISMATCH channel %0d transmitted bytes the model did not", i);
    $display("SUMMARY records=%0d accesses=%0d cycles=%0d", idx, nacc, cycle);
    $display("FAULTS quart=%0d irq=%0d ioctl=%0d incon=%0d", q.faults,
             irq.faults, ioctl.faults, incon.faults);
    $finish(0);
  endrule
endmodule

endpackage
