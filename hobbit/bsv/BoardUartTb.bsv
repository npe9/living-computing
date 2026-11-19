// Board-datapath testbench: the FPGA top's UART output, end to end.
//
// mkHobbitUlx3s is a synthesized module with an argument, which Bluesim
// cannot instantiate dynamically, and its Verilog wrapper adds only the
// power-on reset; so this mirrors its datapath exactly from HobbitUlx3s.bsv
// (image load, prefetch warm-up, start with SP = 0x100 / MSP = 0x180, the
// 48-deep BRAM retirement queue, the HRI writer at 217 clocks/bit) and
// decodes the writer's txd line as 8N1, sampling at mid-bit.
//
// Every received byte is printed as `RXB <hex>`; run_board_tb.sh reassembles
// the text in Python and requires it to equal the smoke test's 41 HRI lines
// byte for byte.  That is the proof that the bits leaving the pin are the
// records the core retired -- the part of the board milestone that neither
// the Bluesim core tests nor the netlist numbers cover.  The receiver
// samples the start bit separately from the eight data bits: an earlier
// version counted the start bit as data bit 0 and decoded noise, which the
// byte-for-byte comparison caught.
package BoardUartTb;

import FIFOF::*;
import BRAMFIFO::*;
import HobbitTypes::*;
import HobbitCore::*;
import HobbitUart::*;
import HobbitBus::*;
import SmokeImage::*;

(* synthesize *)
module mkBoardTb(Empty);

  HobbitBusMem mem <- mkHobbitBusMem;
  HobbitMem phys <- mkHobbitMemBus(mem);
  MemCycles mcyc = defaultMemCycles();
  HobbitCore core <- mkHobbitCore(phys, 32'hFFFFFFFF, mcyc);
  HriWriter uart <- mkHriWriter(217);

  Word sp0  = 32'h00000100;
  Word msp0 = 32'h00000180;

  Reg#(Bit#(8)) li <- mkReg(0);
  Reg#(Bool) loaded <- mkReg(False);
  Reg#(Bit#(2)) boot <- mkReg(0);
  Reg#(Bool) started <- mkReg(False);
  Reg#(Bit#(32)) clocks <- mkReg(0);
  Reg#(Bool) running <- mkReg(True);

  rule load (!loaded);
    if (zeroExtend(li) < imageLength()) begin
      phys.write(zeroExtend(li) << 2, imageWord(zeroExtend(li)));
      li <= li + 1;
    end else
      loaded <= True;
  endrule

  rule askPrefetch (loaded && (boot == 0));
    core.prefetchImage();
    boot <= 1;
  endrule

  rule start ((boot == 1) && core.prefetchReady());
    core.start(sp0, msp0);
    started <= True;
    boot <= 2;
  endrule

  FIFOF#(Hri) q <- mkSizedBRAMFIFOF(48);

  rule relayIn (q.notFull && core.hriValid());
    q.enq(core.hri());
  endrule

  rule relayOut (q.notEmpty && uart.ready);
    uart.enq(q.first);
    q.deq;
  endrule

  // 41 lines x 123 bytes x 10 bits x 217 clocks = 10.9M clocks; allow slack.
  rule timeout (running);
    clocks <= clocks + 1;
    if (clocks > 12_000_000) begin
      running <= False;
      $display("DONE clocks=%0d", clocks);
      $finish;
    end
  endrule

  // ---- UART receiver: 217 clocks/bit, mid-bit sampling -----------------
  Reg#(Bit#(16)) phase <- mkReg(0);
  Reg#(Bit#(4)) nbits <- mkReg(0);
  Reg#(Bit#(8)) shift <- mkReg(0);
  Reg#(Bool) rxActive <- mkReg(False);
  Reg#(Bit#(1)) prev <- mkReg(1);

  // Sample points: k=0 start bit, k=1..8 data bits, k=9 stop bit, each
  // 217 clocks after the leading edge, sampled at mid-bit (108 clocks in).
  // Explicit widths: a narrow literal here sampled at 217 mod 4 = 1 clocks.
  function Bit#(4) samplePoint(Bit#(16) p);
    Bit#(16) base = 108;
    Bit#(16) step = 217;
    Bit#(4) hit = 15;
    for (Integer k = 0; k < 10; k = k + 1) begin
      Bit#(16) kk = fromInteger(k);
      if (p == base + kk * step) hit = truncate(kk);
    end
    return hit;
  endfunction

  rule receive;
    let b = uart.txd();
    if (!rxActive) begin
      if (prev == 1 && b == 0) begin
        rxActive <= True;
        phase <= 0;
        nbits <= 0;
        shift <= 0;
      end
    end else begin
      phase <= phase + 1;
      let sp = samplePoint(phase);
      if (sp != 15) begin
        if (sp == 0) begin
          // start bit: confirm the pulse is still low at mid-bit
          if (b != 0) begin
            rxActive <= False;
            nbits <= 0;
          end
        end else if (sp < 9) begin
          shift <= { b, shift[7:1] };
          nbits <= nbits + 1;
        end else begin
          $display("RXB %02x", shift);
          rxActive <= False;
          nbits <= 0;
        end
      end
    end
    prev <= b;
  endrule

endmodule
endpackage
