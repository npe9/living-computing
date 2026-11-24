// QuartUnitTb.bsv -- what the RTL does that the Python model has no
// counterpart for, checked against the SC68C94 data sheet and the 8N1
// line format directly:
//
//   pin-tx    channel 0's txd, sample by sample: start bit, eight data bits
//             LSB first, stop bit, each exactly clksPerBit clocks
//   tx-fifo   a stalled channel-2 consumer: TxRDY (sr 0x04) holds while
//             the FIFO has room and drops at eight bytes (1994 p. 317:
//             "cleared when the TxFIFO is full (eight bytes)"), TxEMT and
//             isr TxRDYa stay low while anything is held, a ninth write
//             faults (FkTxFull) and is dropped; released, the eight come
//             out in order and sr reads TxRDY|TxEMT again
//   pin-rx    channel 0's rxd: nine bytes without a read fill the eight-
//             byte FIFO and the shift register (no fault), a tenth is an
//             overrun (fault); they read back in order; a stop bit of 0 is
//             a framing fault; a byte while the receiver is disabled
//             faults
//   period    the counter: CtrRDY every 2 * count C/T clocks, exactly,
//             with ctNum/ctDen = 1/2; and with a fractional divider of 3/7
//             the mean period over 9 expiries is 2 * count * 7/3 clocks
//             (within one clock)
//   faultinfo the code of the last fault names its kind
//
// Output: FAIL lines and  UNIT pass=P fail=F
// Discrimination: see run_tests.sh's header (observed failures).

package QuartUnitTb;

import Vector :: *;
import FIFOF :: *;
import GetPut :: *;
import StmtFSM :: *;
import HobbitQuart :: *;

Integer cpb = 4;

(* synthesize *)
module mkQuartUnitTb(Empty);
  HobbitQuart q <- mkHobbitQuart(cpb, 1, 2);
  HobbitQuart qf <- mkHobbitQuart(cpb, 3, 7);  // fractional C/T clock
  Reg#(Bit#(32)) cycle <- mkReg(0);
  Reg#(Bit#(32)) npass <- mkReg(0);
  Reg#(Bit#(32)) nfail <- mkReg(0);
  Reg#(Bit#(32)) rdata <- mkReg(0);
  Reg#(Bit#(32)) i <- mkReg(0);
  Reg#(Bit#(16)) f0 <- mkReg(0);

  // ---- the TB's side of channel 0: a transmitter on rxd
  Reg#(Bit#(10)) tbSh <- mkReg('1);
  Reg#(Bit#(4)) tbLeft <- mkReg(0);
  Reg#(Bit#(16)) tbCnt <- mkReg(0);
  Reg#(Bool) tbBusy <- mkReg(False);
  FIFOF#(Bit#(10)) tbQ <- mkSizedFIFOF(16);   // frames to send, back to back

  // ---- txd capture: 10 * cpb samples from the first low
  Reg#(Bool) capOn <- mkReg(False);
  Reg#(Bit#(64)) cap <- mkReg(0);
  Reg#(Bit#(8)) capN <- mkReg(0);

  // ---- the channel-2 consumer, stallable
  Reg#(Bool) stall <- mkReg(True);
  FIFOF#(Bit#(8)) got2 <- mkSizedFIFOF(16);

  // ---- counter expiry times
  Reg#(Bit#(16)) lastE <- mkReg(0);
  Reg#(Bit#(32)) tStart <- mkReg(0);
  Reg#(Bit#(32)) t1 <- mkReg(0);
  Reg#(Bit#(32)) t2 <- mkReg(0);
  Reg#(Bit#(16)) lastEf <- mkReg(0);
  Reg#(Bit#(32)) tf0 <- mkReg(0);
  Reg#(Bit#(32)) tf9 <- mkReg(0);

  rule clk;
    cycle <= cycle + 1;
  endrule
  rule wires;
    q.rxd(tbSh[0]);
    qf.rxd(1);
  endrule
  rule tbStart (!tbBusy);
    tbSh <= tbQ.first; tbQ.deq;
    tbLeft <= 9; tbCnt <= fromInteger(cpb - 1); tbBusy <= True;
  endrule
  rule tbShift (tbBusy);
    if (tbCnt != 0) tbCnt <= tbCnt - 1;
    else if (tbLeft == 0) begin tbBusy <= False; tbSh <= '1; end
    else begin
      tbSh <= {1'b1, tbSh[9:1]}; tbLeft <= tbLeft - 1;
      tbCnt <= fromInteger(cpb - 1);
    end
  endrule
  rule capture;
    Bit#(1) v = q.txd;
    if (!capOn && capN == 0 && v == 0) begin
      capOn <= True; cap <= zeroExtend(v); capN <= 1;
    end
    else if (capOn) begin
      cap <= cap | (zeroExtend(v) << capN);
      capN <= capN + 1;
      if (capN + 1 == fromInteger(10 * cpb)) capOn <= False;
    end
  endrule
  rule sink2 (!stall);
    let b <- q.txOut[1].get;
    got2.enq(b);
  endrule
  rule times;
    Bit#(16) e = q.dbg.ctrExpiries[0];
    if (e != lastE) begin
      lastE <= e;
      if (e == 1) t1 <= cycle;
      if (e == 2) t2 <= cycle;
    end
    Bit#(16) ef = qf.dbg.ctrExpiries[0];
    if (ef != lastEf) begin
      lastEf <= ef;
      if (ef == 1) tf0 <= cycle;
      if (ef == 10) tf9 <= cycle;
    end
  endrule

  function Action check(Bool ok, Fmt what);
    action
      if (ok) npass <= npass + 1;
      else begin
        nfail <= nfail + 1;
        $display(fshow("FAIL ") + what);
      end
    endaction
  endfunction

  function Stmt wr(Bit#(12) a, Bit#(8) d) = seq
    q.req(a, zeroExtend(d), 4'hF, True);
    action let r <- q.resp; endaction
  endseq;
  function Stmt rd(Bit#(12) a) = seq
    q.req(a, 0, 4'hF, False);
    action let r <- q.resp; rdata <= r; endaction
  endseq;
  function Stmt expectRd(Bit#(12) a, Bit#(32) v, String what) = seq
    rd(a);
    check(rdata == v, $format("%s: +0x%03x = 0x%02x, want 0x%02x", what, a,
                              rdata, v));
  endseq;
  function Stmt wrf(Bit#(12) a, Bit#(8) d) = seq
    qf.req(a, zeroExtend(d), 4'hF, True);
    action let r <- qf.resp; endaction
  endseq;
  function Stmt settle = seq noAction; noAction; noAction; endseq;
  function Bit#(10) frame(Bit#(8) b, Bit#(1) stop) = {stop, b, 1'b0};

  // expected txd for 0xA5: start 0, 1 0 1 0 0 1 0 1 (LSB first), stop 1
  function Bit#(64) wave(Bit#(8) b);
    Bit#(10) bits = {1'b1, b, 1'b0};
    Bit#(64) w = 0;
    for (Integer k = 0; k < 10 * cpb; k = k + 1)
      w[k] = bits[k / cpb];
    return w;
  endfunction

  Stmt test = seq
    // ------------------------------------------------ pin-tx
    wr(12'h008, 8'h10); wr(12'h000, 8'h13); wr(12'h000, 8'h07);
    wr(12'h008, 8'h05);                       // TxEnable | RxEnable
    expectRd(12'h004, 32'h0c, "pin-tx sr before");
    wr(12'h00c, 8'ha5);
    await(capN == fromInteger(10 * cpb) && !capOn);
    check(cap == wave(8'ha5), $format("pin-tx txd waveform %b, want %b",
                                      cap[39:0], wave(8'ha5)[39:0]));
    await(q.dbg.txIdle);
    expectRd(12'h004, 32'h0c, "pin-tx sr after");

    // ------------------------------------------------ tx-fifo
    wr(12'h048, 8'h04);                       // channel 2 TxEnable
    expectRd(12'h044, 32'h0c, "tx-fifo empty");
    for (i <= 0; i < 8; i <= i + 1) seq
      wr(12'h04c, 8'h30 + truncate(i));
      rd(12'h044);
      check(rdata == (i < 7 ? 32'h04 : 32'h00),
            $format("tx-fifo sr after %0d bytes = 0x%02x", i + 1, rdata));
      rd(12'h054);
      check(rdata[0] == 0, $format("tx-fifo isr TxRDYa with %0d held", i + 1));
    endseq
    action f0 <= q.faults; endaction
    wr(12'h04c, 8'h99);                       // a ninth: fault, dropped
    settle;
    check(q.faults == f0 + 1 && q.faultInfo[15:12] == pack(FkTxFull),
          $format("tx-fifo ninth write: faults %0d -> %0d, info 0x%04x", f0,
                  q.faults, q.faultInfo));
    stall <= False;
    for (i <= 0; i < 8; i <= i + 1) action
      check(got2.first == 8'h30 + truncate(i),
            $format("tx-fifo byte %0d = 0x%02x", i, got2.first));
      got2.deq;
    endaction
    settle;
    check(!got2.notEmpty, $format("tx-fifo: the dropped byte came out"));
    expectRd(12'h044, 32'h0c, "tx-fifo drained");
    expectRd(12'h054, 32'h01, "tx-fifo isr TxRDYa drained");

    // ------------------------------------------------ pin-rx
    action f0 <= q.faults; endaction
    for (i <= 0; i < 9; i <= i + 1) tbQ.enq(frame(8'h60 + truncate(i), 1));
    await(!tbBusy && !tbQ.notEmpty);
    repeat (8) noAction;
    check(q.faults == f0, $format("pin-rx nine bytes faulted"));
    check(q.dbg.rxLevel[0] == 8, $format("pin-rx level %0d", q.dbg.rxLevel[0]));
    expectRd(12'h004, 32'h0f, "pin-rx sr full");
    tbQ.enq(frame(8'h77, 1));                 // the tenth: overrun
    await(!tbBusy && !tbQ.notEmpty);
    repeat (8) noAction;
    check(q.faults == f0 + 1 && q.faultInfo[15:12] == pack(FkRxOverrun),
          $format("pin-rx overrun: faults %0d -> %0d info 0x%04x", f0,
                  q.faults, q.faultInfo));
    for (i <= 0; i < 9; i <= i + 1) seq
      rd(12'h00c);
      check(rdata == 32'h60 + i,
            $format("pin-rx byte %0d = 0x%02x", i, rdata));
    endseq
    expectRd(12'h004, 32'h0c, "pin-rx sr empty");
    action f0 <= q.faults; endaction
    tbQ.enq(frame(8'h12, 0));                 // stop bit 0
    await(!tbBusy && !tbQ.notEmpty);
    repeat (8) noAction;
    check(q.faults == f0 + 1 && q.faultInfo[15:12] == pack(FkFraming),
          $format("pin-rx framing: info 0x%04x", q.faultInfo));
    check(q.dbg.rxLevel[0] == 0, $format("pin-rx framing byte kept"));
    wr(12'h008, 8'h02);                       // RxDisable
    action f0 <= q.faults; endaction
    tbQ.enq(frame(8'h13, 1));
    await(!tbBusy && !tbQ.notEmpty);
    repeat (8) noAction;
    check(q.faults == f0 + 1 && q.faultInfo[15:12] == pack(FkRxDisabled),
          $format("pin-rx disabled: info 0x%04x", q.faultInfo));

    // ------------------------------------------------ period
    wr(12'h010, 8'h70); wr(12'h018, 8'h00); wr(12'h01c, 8'h05);
    action
      q.req(12'h038, 0, 4'hF, False);         // start
      tStart <= cycle;
    endaction
    action let r <- q.resp; endaction
    await(q.dbg.ctrExpiries[0] >= 2);
    check(t2 - t1 == 20, $format("period: %0d clocks between expiries, want 2*5*2 = 20",
                                 t2 - t1));
    check(t1 - tStart >= 18 && t1 - tStart <= 22,
          $format("period: first expiry %0d clocks after start", t1 - tStart));
    wr(12'h010, 8'h00);                       // leave timer mode: the next
    action f0 <= q.faults; endaction          // expiry is a fault
    await(q.faults == f0 + 1);
    check(q.faultInfo[15:12] == pack(FkCtrMode),
          $format("period: mode change info 0x%04x", q.faultInfo));
    // fractional C/T clock 3/7: mean period 2*count*7/3 = 2*30*7/3 = 140
    wrf(12'h010, 8'h70); wrf(12'h018, 8'h00); wrf(12'h01c, 8'd30);
    qf.req(12'h038, 0, 4'hF, False);
    action let r <- qf.resp; endaction
    await(qf.dbg.ctrExpiries[0] >= 10);
    noAction;
    check(tf9 - tf0 >= 9 * 140 - 1 && tf9 - tf0 <= 9 * 140 + 1,
          $format("period: 9 fractional periods = %0d clocks, want 1260",
                  tf9 - tf0));
    $display("UNIT pass=%0d fail=%0d", npass, nfail);
    $finish(0);
  endseq;

  mkAutoFSM(test);

  rule watchdog (cycle == 32'd2000000);
    $display("FAIL watchdog: the unit test did not finish");
    $display("UNIT pass=%0d fail=%0d", npass, nfail + 1);
    $finish(0);
  endrule
endmodule

endpackage
