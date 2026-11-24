// SonicReplayTb.bsv -- replay a p9boot.Sonic trace into the SONIC RTL.
//
// sonic_trace.py vectors writes, in the working directory:
//   events.hex  one 96-bit record per register access or offered frame:
//               [95:92] op (1 read, 2 write, 3 frame, 4 a frame whose last
//               byte has `bad`, 0 end), [91] the
//               model's irq after it, [90:79] offset, [78:47] write data
//               or the value read, [46:43] mask, [42:32] frame length,
//               [31:0] the number of DMA words the model had made by the
//               end of this event
//   txidx.hex   per event: the number of frames sent by its end
//   dma.hex     the model's DMA words in order: {write, addr, data}
//   rx.hex      offered frames' bytes back to back; tx.hex, txlen.hex the
//               transmitted frames' bytes and lengths
//
// Each event is issued, the testbench waits until the RTL is idle (busy
// low for 3 clocks), and then compares: the value read; irq; that the RTL
// made exactly the model's DMA words up to this point (each request is
// checked as it is made: read or write, address, and for writes the data
// and byte enables; reads are answered with the model's data); that it
// sent exactly the model's frames, byte for byte; and that no fault is up.
// Throughout, irq must not rise before the RTL has made all of the
// event's DMA words (isr is raised only after the data is written).
// The DMA port is stalled and the read data delayed by a pseudo-random
// pattern, so the RTL is replayed against a busy arbiter.
//
// Output: MISMATCH lines (the runner counts them), then
// SUMMARY events=E dma=D tx=T cycles=C.
package SonicReplayTb;

import FIFOF   :: *;
import GetPut  :: *;
import RegFile :: *;
import Sonic   :: *;

typedef enum { Fetch, Feed, Resp, Settle, Done } Phase deriving (Bits, Eq);

(* synthesize *)
module mkSonicReplayTb(Empty);
  HobbitSonic dut <- mkSonic;

  RegFile#(Bit#(18), Bit#(96)) ev    <- mkRegFileLoad("events.hex", 0, '1);
  RegFile#(Bit#(18), Bit#(32)) txidx <- mkRegFileLoad("txidx.hex", 0, '1);
  RegFile#(Bit#(20), Bit#(65)) dmav  <- mkRegFileLoad("dma.hex", 0, '1);
  RegFile#(Bit#(21), Bit#(8))  rxb   <- mkRegFileLoad("rx.hex", 0, '1);
  RegFile#(Bit#(20), Bit#(8))  txb   <- mkRegFileLoad("tx.hex", 0, '1);
  RegFile#(Bit#(14), Bit#(12)) txl   <- mkRegFileLoad("txlen.hex", 0, '1);

  Reg#(Bit#(18)) ei <- mkReg(0);
  Reg#(Phase) phase <- mkReg(Fetch);
  Reg#(Bit#(32)) cycle <- mkReg(0);
  Reg#(Bit#(32)) di <- mkReg(0);          // DMA words checked
  Reg#(Bit#(21)) rxPos <- mkReg(0);
  Reg#(Bit#(11)) feedLeft <- mkReg(0);
  Reg#(Bit#(20)) txPos <- mkReg(0);
  Reg#(Bit#(12)) txInFrame <- mkReg(0);
  Reg#(Bit#(32)) txCount <- mkReg(0);
  Reg#(Bit#(32)) got <- mkReg(0);
  Reg#(Bit#(4)) quiet <- mkReg(0);
  Reg#(Bit#(16)) lfsr <- mkReg(16'hACE1);
  FIFOF#(Bit#(32)) rdPipe <- mkSizedFIFOF(4);
  Reg#(Bit#(3)) rdDelay <- mkReg(0);

  Bit#(96) v = ev.sub(ei);
  Bit#(4)  op = v[95:92];
  Bool     expIrq = v[91] == 1;
  Bit#(12) off = v[90:79];
  Bit#(32) dat = v[78:47];
  Bit#(4)  msk = v[46:43];
  Bit#(11) flen = v[42:32];
  Bit#(32) nd = v[31:0];

  function Action mismatch(Fmt f);
    action
      $display(fshow("MISMATCH event ") + fshow(ei) + fshow(": ") + f);
    endaction
  endfunction

  rule clk;
    cycle <= cycle + 1;
    lfsr <= {lfsr[14:0], lfsr[15] ^ lfsr[13] ^ lfsr[12] ^ lfsr[10]};
  endrule

  // ---- the arbiter: stalls about one cycle in four
  rule dmaReq (lfsr[1:0] != 0);
    let q <- dut.dma.req.get;
    Bit#(65) e = dmav.sub(truncate(di));
    Bool ew = e[64] == 1;
    Bit#(32) ea = e[63:32];
    Bit#(32) ed = e[31:0];
    if (phase == Settle && di >= nd)
      mismatch($format("DMA %s 0x%08x beyond the model's %0d words",
                       q.write ? "write" : "read", q.addr, nd));
    else if (q.write != ew || q.addr != ea)
      mismatch($format("DMA %0d: RTL %s 0x%08x, model %s 0x%08x", di,
                       q.write ? "write" : "read", q.addr,
                       ew ? "write" : "read", ea));
    else if (q.write && (q.wdata != ed || q.be != 'hF))
      mismatch($format("DMA %0d write 0x%08x: RTL %08x be %x, model %08x",
                       di, q.addr, q.wdata, q.be, ed));
    if (!q.write) rdPipe.enq(ed);
    di <= di + 1;
  endrule

  rule dmaResp (lfsr[3:2] != 0);
    dut.dma.rdata.put(rdPipe.first);
    rdPipe.deq;
  endrule

  // ---- transmitted frames
  rule txSink;
    let b <- dut.tx.get;
    if (b.data != txb.sub(txPos))
      mismatch($format("frame %0d byte %0d: RTL %02x, model %02x", txCount,
                       txInFrame, b.data, txb.sub(txPos)));
    txPos <= txPos + 1;
    if (b.last) begin
      if (txInFrame + 1 != txl.sub(truncate(txCount)))
        mismatch($format("frame %0d: RTL %0d bytes, model %0d", txCount,
                         txInFrame + 1, txl.sub(truncate(txCount))));
      txInFrame <= 0;
      txCount <= txCount + 1;
    end
    else txInFrame <= txInFrame + 1;
  endrule

  rule fetch (phase == Fetch);
    case (op)
      0: phase <= Done;
      1, 2: begin
        dut.req(off, dat, (op == 2) ? msk : 0, op == 2);
        phase <= Resp;
      end
      3, 4: begin feedLeft <= flen; phase <= Feed; end
      default: begin mismatch($format("bad op %0d", op)); phase <= Done; end
    endcase
  endrule

  rule feed (phase == Feed);
    dut.rx.put(FrameByte {data: rxb.sub(rxPos), last: feedLeft == 1,
                          bad: feedLeft == 1 && op == 4});
    rxPos <= rxPos + 1;
    feedLeft <= feedLeft - 1;
    if (feedLeft == 1) begin phase <= Settle; quiet <= 0; end
  endrule

  rule resp (phase == Resp);
    let x <- dut.resp;
    got <= x;
    if (op == 1 && x != dat)
      mismatch($format("read 0x%03x: RTL %04x, model %04x", off, x, dat));
    phase <= Settle;
    quiet <= 0;
  endrule

  rule settle (phase == Settle);
    if (dut.busy || rdPipe.notEmpty) quiet <= 0;
    else if (quiet < 3) quiet <= quiet + 1;
    else begin
      if (dut.irq != expIrq)
        mismatch($format("irq: RTL %0d, model %0d", dut.irq, expIrq));
      if (di != nd)
        mismatch($format("DMA words: RTL %0d, model %0d", di, nd));
      if (txCount != txidx.sub(ei))
        mismatch($format("frames sent: RTL %0d, model %0d", txCount,
                         txidx.sub(ei)));
      if (dut.fault)
        mismatch($format("fault %0d", dut.faultInfo));
      ei <= ei + 1;
      phase <= Fetch;
    end
  endrule

  // irq may rise only once the RTL has made every DMA word of the event:
  // the isr bit announces data that is already with the arbiter
  Reg#(Bool) irqPrev <- mkReg(False);
  rule irqOrder;
    irqPrev <= dut.irq;
    if (dut.irq && !irqPrev && phase != Fetch && di != nd)
      mismatch($format("irq rose after %0d of the event's %0d DMA words",
                       di, nd));
  endrule

  rule done (phase == Done);
    $display("SUMMARY events=%0d dma=%0d tx=%0d cycles=%0d",
             ei, di, txCount, cycle);
    $finish(0);
  endrule
endmodule

endpackage
