// EspLinkTb.bsv -- EspLink (mkEspLink25M, 10 clocks a bit) against the
// ESP32 relay's C codec.  esplink_vectors.py writes the vectors (its
// docstring lists the files); everything expected is relay.c's output.
//
//   TX  the frames of txin.hex are put into the link's tx port, whenever
//       it takes them.  A UART receiver here samples txd mid-bit and
//       compares every byte with txw.hex (relay_encode's bytes, packet
//       after packet), and checks each stop bit.  RTS is driven high in
//       pseudo-random spans (about a quarter of the time): a start bit
//       may begin only if RTS was low 3 clocks earlier (the 2-flop
//       synchroniser and the start register), and none may begin later.
//   RX  rxw.hex is driven onto rxd, 8N1, with pseudo-random idle gaps of
//       0 to 3 bit times; a byte flagged badstop is sent with its stop
//       bit low (then the line idles two byte times).  The frames out of
//       the rx port are collected; one whose last byte has `bad` is
//       dropped (as the SONIC drops it), every other must equal the next
//       frame of rxf.hex (relay_feed's good 0x45 packets).
//   At the end (every byte of both directions passed, and 3000 quiet
//   clocks) the stats must equal expect.hex.
//
// Output: MISMATCH lines, then
// SUMMARY tx=<link bytes> rxframes=<good frames> dropped=<bad frames>
//         cycles=<n>.
package EspLinkTb;

import GetPut  :: *;
import RegFile :: *;
import Sonic   :: *;
import EspLink :: *;

(* synthesize *)
module mkEspLinkTb(Empty);
  EspLink dut <- mkEspLink25M;
  Integer cpb = 10;

  RegFile#(Bit#(18), Bit#(10)) txin <- mkRegFileLoad("txin.hex", 0, '1);
  RegFile#(Bit#(18), Bit#(9))  txw  <- mkRegFileLoad("txw.hex", 0, '1);
  RegFile#(Bit#(19), Bit#(10)) rxw  <- mkRegFileLoad("rxw.hex", 0, '1);
  RegFile#(Bit#(19), Bit#(10)) rxf  <- mkRegFileLoad("rxf.hex", 0, '1);
  RegFile#(Bit#(1), Bit#(144)) exp  <- mkRegFileLoad("expect.hex", 0, 0);

  Reg#(Bit#(32)) cycle <- mkReg(0);
  Reg#(Bit#(16)) lfsr <- mkReg(16'hACE1);

  function Action mismatch(Fmt f);
    action $display(fshow("MISMATCH ") + f); endaction
  endfunction

  rule clk;
    cycle <= cycle + 1;
    lfsr <= {lfsr[14:0], lfsr[15] ^ lfsr[13] ^ lfsr[12] ^ lfsr[10]};
  endrule

  // ---------------------------------------------------------- RTS
  Reg#(Bit#(1))  rts <- mkReg(0);
  Reg#(Bit#(12)) rtsLeft <- mkReg(0);
  Reg#(Bit#(3))  rtsHist <- mkReg(0);   // rts of the last 3 clocks
  rule rtsGen;
    if (rtsLeft == 0) begin
      rts <= (lfsr[12:11] == 0) ? 1 : 0;
      rtsLeft <= zeroExtend(lfsr[9:0]) + 1;
    end
    else rtsLeft <= rtsLeft - 1;
    rtsHist <= {rtsHist[1:0], rts};
  endrule

  // ---------------------------------------------------------- RX driver
  Reg#(Bit#(19)) rxi <- mkReg(0);
  Reg#(Bit#(1))  rxd <- mkReg(1);
  Reg#(Bit#(10)) rxSh <- mkReg(0);
  Reg#(Bit#(5))  rxBits <- mkReg(0);     // bits left of this byte
  Reg#(Bit#(16)) rxCnt <- mkReg(0);
  Reg#(Bool)     rxDone <- mkReg(False);
  Bit#(10) rv = rxw.sub(rxi);

  rule rxDrive (!rxDone);
    if (rxCnt != 0) rxCnt <= rxCnt - 1;
    else if (rxBits != 0) begin
      rxd <= rxSh[0];
      rxSh <= {1'b1, rxSh[9:1]};
      rxBits <= rxBits - 1;
      rxCnt <= fromInteger(cpb - 1);
    end
    else if (rv[9] == 0) begin rxd <= 1; rxDone <= True; end
    else begin
      // start, 8 data, stop (low when badstop), then an idle gap
      Bit#(1) stop = ~rv[8];
      Bit#(5) gap = (rv[8] == 1) ? 20 : zeroExtend(lfsr[5:4] & lfsr[7:6]);
      rxSh <= {stop, rv[7:0], 1'b0};
      rxBits <= 10 + gap;
      rxi <= rxi + 1;
      rxCnt <= 0;
    end
  endrule

  rule pins;
    dut.pins(rxd, rts);
  endrule

  // ---------------------------------------------------------- TX feeder
  Reg#(Bit#(18)) txi <- mkReg(0);
  Bit#(10) tv = txin.sub(txi);
  rule txFeed (tv[9] == 1);
    dut.tx.put(FrameByte {data: tv[7:0], last: tv[8] == 1, bad: False});
    txi <= txi + 1;
  endrule

  // ---------------------------------------------------------- TX monitor
  Reg#(Bit#(18)) twi <- mkReg(0);
  Reg#(Bit#(4))  tmBit <- mkReg(0);      // 0 idle, 1 start, 2..9, 10 stop
  Reg#(Bit#(16)) tmCnt <- mkReg(0);
  Reg#(Bit#(8))  tmSh <- mkReg(0);
  Reg#(Bit#(1))  txdPrev <- mkReg(1);
  rule txMon;
    Bit#(1) v = dut.txd;
    txdPrev <= v;
    if (tmBit == 0) begin
      if (v == 0) begin
        if (rtsHist[2] == 1)
          mismatch($format("a start bit at cycle %0d, RTS high 3 clocks "
                           + "before", cycle));
        tmBit <= 1;
        tmCnt <= fromInteger(cpb / 2);
      end
    end
    else if (tmCnt != 0) tmCnt <= tmCnt - 1;
    else if (tmBit == 1) begin
      if (v != 0) mismatch($format("a short start bit at cycle %0d", cycle));
      tmBit <= 2; tmCnt <= fromInteger(cpb - 1);
    end
    else if (tmBit <= 9) begin
      tmSh <= {v, tmSh[7:1]};
      tmBit <= tmBit + 1; tmCnt <= fromInteger(cpb - 1);
    end
    else begin
      Bit#(9) e = txw.sub(twi);
      if (v != 1) mismatch($format("tx byte %0d: no stop bit", twi));
      if (e[8] == 0)
        mismatch($format("tx byte %0d %02x beyond the C's bytes", twi, tmSh));
      else if (e[7:0] != tmSh)
        mismatch($format("tx byte %0d: RTL %02x, C %02x", twi, tmSh,
                         e[7:0]));
      twi <= twi + 1;
      // resynchronise on the stop bit's middle, as a real UART
      tmBit <= 0;
    end
  endrule

  // ---------------------------------------------------------- RX sink
  Reg#(Bit#(19)) fStart <- mkReg(0);     // rxf index of the expected frame
  Reg#(Bit#(19)) fPos <- mkReg(0);
  Reg#(Bool)     fBad <- mkReg(False);   // differs from the expected
  Reg#(Bit#(32)) goodFrames <- mkReg(0);
  Reg#(Bit#(32)) dropped <- mkReg(0);
  rule rxSink;
    let b <- dut.rx.get;
    Bit#(10) e = rxf.sub(fPos);
    Bool differ = fBad || e[9] == 0 || e[7:0] != b.data
                  || (e[8] == 1) != b.last;
    if (b.last) begin
      if (b.bad) begin
        dropped <= dropped + 1;
        fPos <= fStart;
      end
      else begin
        if (differ)
          mismatch($format("rx frame %0d (a good frame) differs from the "
                           + "C's", goodFrames));
        goodFrames <= goodFrames + 1;
        fStart <= fPos + 1;
        fPos <= fPos + 1;
      end
      fBad <= False;
    end
    else begin
      fBad <= differ;
      if (e[9] == 1 && e[8] == 0) fPos <= fPos + 1;
    end
  endrule

  // ---------------------------------------------------------- the end
  Reg#(Bit#(16)) quiet <- mkReg(0);
  Bool allIn = rxDone && tv[9] == 0 && txw.sub(twi)[8] == 0 && dut.txIdle
               && tmBit == 0;
  rule finish (allIn);
    if (quiet < 3000) quiet <= quiet + 1;
    else begin
      Bit#(144) x = exp.sub(0);
      EspLinkStats s = dut.stats;
      Bit#(144) got = {s.good, s.badCrc, s.badCobs, s.badLen, s.overflows,
                       s.badType, s.framing, s.lost, s.txTooLong};
      if (got != x)
        mismatch($format("stats: RTL ") + fshow(s) +
                 $format(", expected %036x", x));
      if (rxf.sub(fStart)[9] == 1)
        mismatch($format("rx: only %0d good frames, the C has more",
                         goodFrames));
      $display("SUMMARY tx=%0d rxframes=%0d dropped=%0d cycles=%0d",
               twi, goodFrames, dropped, cycle);
      $finish(0);
    end
  endrule

  rule timeout (cycle == 100000000);
    mismatch($format("timeout: rx byte %0d, tx frame byte %0d, tx link "
                     + "byte %0d", rxi, txi, twi));
    $finish(0);
  endrule
endmodule

endpackage
