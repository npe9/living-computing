// HobbitUartTb.bsv -- Bluesim testbench for the 8N1 transmitter and the
// HRI line writer.
//
// Two checks exercise mkUartTx with a real bit-level receiver: 0x55 is
// sent, the wire is sampled mid-bit, and the decoded byte plus start/stop
// framing are checked.  The writer is then fed four known Hri records --
// an ordinary write (cyc=0), a no-write retirement (cyc=1), a trap
// (cyc=12) and the same trap with cyc=4294967295 (10 digits, the longest
// decimal) -- and its output is reassembled byte for byte.  The cycle
// count makes the lines variable length (123, 123, 124 and 132 bytes),
// and each is compared against the exact expected line, whose ASCII is
// spelled out below.  The lines are also printed between markers so the
// run output can be fed straight to hobbit/tests/hri_check.py's parser,
// which requires the trailing cyc field.
//
// clksPerBit is the board value 25 MHz / 115200 = 217 (rounded down);
// the modules take it as a parameter, so simulation and board share one
// definition.

package HobbitUartTb;

import Vector::*;
import FIFOF::*;
import HobbitTypes::*;
import HobbitUart::*;

Integer uartClksPerBit = 217;

typedef struct {
  Bit#(8) data;
  Bool    frameOk;
} RxByte deriving (Bits);

interface UartRx;
  method Action in(Bit#(1) x);
  method Action deq;
  method RxByte first;
  method Bool notEmpty;
endinterface

// Mid-bit sampling receiver: a falling edge starts a frame, the start
// bit is sampled half a bit later, the eight data bits one bit apart
// (LSB first), and the stop bit one bit after the last data bit.  Only
// complete bytes enter the output FIFO; frameOk reports that the start
// sample was 0 and the stop sample was 1.
module mkUartRx#(Integer clksPerBit)(UartRx);
  Integer mid = clksPerBit / 2;
  FIFOF#(RxByte) q <- mkFIFOF;
  Reg#(Bool) active <- mkReg(False);
  Reg#(Bit#(32)) cnt <- mkReg(0);
  Reg#(Bit#(8)) sh <- mkReg(0);
  Reg#(Bool) sawStart <- mkReg(False);

  method Action in(Bit#(1) x);
    if (!active) begin
      if (x == 0) begin
        active <= True;
        cnt <= 0;
        sh <= 0;
        sawStart <= False;
      end
    end
    else begin
      Bit#(32) c = cnt;
      if (c == fromInteger(mid))
        sawStart <= (x == 0);
      else if (c == fromInteger(mid + clksPerBit))
        sh <= {x, sh[7:1]};
      else if (c == fromInteger(mid + 2 * clksPerBit))
        sh <= {x, sh[7:1]};
      else if (c == fromInteger(mid + 3 * clksPerBit))
        sh <= {x, sh[7:1]};
      else if (c == fromInteger(mid + 4 * clksPerBit))
        sh <= {x, sh[7:1]};
      else if (c == fromInteger(mid + 5 * clksPerBit))
        sh <= {x, sh[7:1]};
      else if (c == fromInteger(mid + 6 * clksPerBit))
        sh <= {x, sh[7:1]};
      else if (c == fromInteger(mid + 7 * clksPerBit))
        sh <= {x, sh[7:1]};
      else if (c == fromInteger(mid + 8 * clksPerBit))
        sh <= {x, sh[7:1]};
      else if (c == fromInteger(mid + 9 * clksPerBit)) begin
        q.enq(RxByte { data: sh, frameOk: sawStart && (x == 1) });
        active <= False;
      end
      cnt <= c + 1;
    end
  endmethod

  method Action deq;
    q.deq;
  endmethod

  method RxByte first;
    return q.first;
  endmethod

  method Bool notEmpty = q.notEmpty;
endmodule

// Three retirement records: PC/parcel values, a real word write with a
// byte mask, one retirement that wrote nothing, and the trap retire whose
// architectural write is the p. 1-39 faulting-PC store.
function Hri rec(Bit#(2) i);
  case (i)
    0: return Hri { valid: True, pc: 32'h00000102, insn0: 16'h1234,
                    insn1: 16'h5678, sp_before: 32'h00000100,
                    sp_after: 32'h000000FC, msp_before: 32'h00000180,
                    msp_after: 32'h00000180, mem_we: True,
                    mem_addr: 32'h00000300, mem_wdata: 32'hDEADBEEF,
                    mem_wmask: 8'h0F, trap: False, cyc: 32'd0 };
    1: return Hri { valid: True, pc: 32'h00000104, insn0: 16'hABCD,
                    insn1: 16'h0000, sp_before: 32'h00000100,
                    sp_after: 32'h00000100, msp_before: 32'h00000180,
                    msp_after: 32'h00000180, mem_we: False,
                    mem_addr: 32'h00000000, mem_wdata: 32'h00000000,
                    mem_wmask: 8'h00, trap: False, cyc: 32'd1 };
    2: return Hri { valid: True, pc: 32'h000000BA, insn0: 16'h2C00,
                    insn1: 16'h0000, sp_before: 32'h00000070,
                    sp_after: 32'h0000006C, msp_before: 32'h000001B0,
                    msp_after: 32'h000001B0, mem_we: True,
                    mem_addr: 32'h00000070, mem_wdata: 32'h000000BA,
                    mem_wmask: 8'h03, trap: True, cyc: 32'd12 };
    default: return Hri { valid: True, pc: 32'h000000BA, insn0: 16'h2C00,
                    insn1: 16'h0000, sp_before: 32'h00000070,
                    sp_after: 32'h0000006C, msp_before: 32'h000001B0,
                    msp_after: 32'h000001B0, mem_we: True,
                    mem_addr: 32'h00000070, mem_wdata: 32'h000000BA,
                    mem_wmask: 8'h03, trap: True, cyc: 32'hFFFFFFFF };
  endcase
endfunction

function Action say(Bool ok, String label);
  action
    if (ok) $display("PASS %s", label);
    else    $display("FAIL %s", label);
  endaction
endfunction

// Compare nbytes received bytes at base against the expected line packed
// most-significant-byte first.
function Bool lineMatches(Vector#(512, Bit#(8)) v, Integer base,
                          Integer nbytes, Bit#(n) e);
  Bool ok = True;
  for (Integer i = 0; i < nbytes; i = i + 1)
    if (v[base + i] != e[8 * (nbytes - 1 - i) + 7 : 8 * (nbytes - 1 - i)])
      ok = False;
  return ok;
endfunction

(* synthesize *)
module mkUartTb(Empty);

  Integer cpb = uartClksPerBit;

  UartTx tx <- mkUartTx(cpb);
  HriWriter wr <- mkHriWriter(cpb);
  UartRx rxu <- mkUartRx(cpb);
  UartRx rxw <- mkUartRx(cpb);

  Reg#(Bool) primed <- mkReg(False);
  Reg#(Bool) idleOk <- mkReg(False);
  Reg#(Bool) readyOk <- mkReg(False);
  Reg#(Bool) queued <- mkReg(False);
  Reg#(Bit#(2)) wi <- mkReg(0);
  Reg#(Bool) gotUart <- mkReg(False);
  Reg#(Bit#(8)) uartByte <- mkReg(0);
  Reg#(Bool) uartFrame <- mkReg(False);
  Reg#(Bit#(9)) wcount <- mkReg(0);
  Reg#(Bit#(32)) wbad <- mkReg(0);
  Reg#(Vector#(512, Bit#(8))) rxbuf <- mkReg(replicate(0));
  Reg#(Bit#(32)) cyc <- mkReg(0);

  rule count;
    cyc <= cyc + 1;
  endrule

  rule prime (!primed);
    primed <= True;
    idleOk <= (tx.txd == 1);
    readyOk <= tx.ready;
    tx.send(8'h55);
  endrule

  rule feedWr (!queued);
    if (wr.ready) begin
      wr.enq(rec(wi));
      if (wi == 3) queued <= True;
      else         wi <= wi + 1;
    end
  endrule

  rule pollUart;
    rxu.in(tx.txd);
  endrule

  rule pollWr;
    rxw.in(wr.txd);
  endrule

  rule takeUart (!gotUart && rxu.notEmpty);
    let b = rxu.first;
    rxu.deq;
    uartByte <= b.data;
    uartFrame <= b.frameOk;
    gotUart <= True;
  endrule

  rule takeWr (wcount < 502 && rxw.notEmpty);
    let b = rxw.first;
    rxw.deq;
    rxbuf[wcount] <= b.data;
    if (!b.frameOk) wbad <= wbad + 1;
    wcount <= wcount + 1;
  endrule

  rule terminal;
    if (gotUart && wcount == 502) begin
      // Expected ASCII.  Line 1: at 0x0102 an ordinary word write of
      // 0xDEADBEEF (mask 0x0f) at 0x300, retired at cycle 0.  Line 2:
      // at 0x0104 a retirement with no write, at cycle 1.  Line 3: the
      // trap at 0x00BA storing the faulting PC at CSP, at cycle 12.
      // Line 4: the same trap at cycle 4294967295, the longest decimal.
      // cyc makes the lines 123, 123, 124 and 132 bytes including
      // newlines.
      Bit#(984) exp0 = {
        8'h48, 8'h52, 8'h49, 8'h20, 8'h70, 8'h63, 8'h3d, 8'h30, 8'h31, 8'h30, 8'h32, 8'h20,
        8'h69, 8'h6e, 8'h73, 8'h6e, 8'h3d, 8'h31, 8'h32, 8'h33, 8'h34, 8'h35, 8'h36, 8'h37,
        8'h38, 8'h20, 8'h73, 8'h70, 8'h3d, 8'h30, 8'h30, 8'h30, 8'h30, 8'h30, 8'h31, 8'h30,
        8'h30, 8'h3e, 8'h30, 8'h30, 8'h30, 8'h30, 8'h30, 8'h30, 8'h66, 8'h63, 8'h20, 8'h6d,
        8'h73, 8'h70, 8'h3d, 8'h30, 8'h30, 8'h30, 8'h30, 8'h30, 8'h31, 8'h38, 8'h30, 8'h3e,
        8'h30, 8'h30, 8'h30, 8'h30, 8'h30, 8'h31, 8'h38, 8'h30, 8'h20, 8'h77, 8'h65, 8'h3d,
        8'h31, 8'h20, 8'h61, 8'h64, 8'h64, 8'h72, 8'h3d, 8'h30, 8'h30, 8'h30, 8'h30, 8'h30,
        8'h33, 8'h30, 8'h30, 8'h20, 8'h64, 8'h61, 8'h74, 8'h61, 8'h3d, 8'h64, 8'h65, 8'h61,
        8'h64, 8'h62, 8'h65, 8'h65, 8'h66, 8'h20, 8'h6d, 8'h61, 8'h73, 8'h6b, 8'h3d, 8'h30,
        8'h66, 8'h20, 8'h74, 8'h72, 8'h61, 8'h70, 8'h3d, 8'h30, 8'h20, 8'h63, 8'h79, 8'h63,
        8'h3d, 8'h30, 8'h0a
      };
      Bit#(984) exp1 = {
        8'h48, 8'h52, 8'h49, 8'h20, 8'h70, 8'h63, 8'h3d, 8'h30, 8'h31, 8'h30, 8'h34, 8'h20,
        8'h69, 8'h6e, 8'h73, 8'h6e, 8'h3d, 8'h61, 8'h62, 8'h63, 8'h64, 8'h30, 8'h30, 8'h30,
        8'h30, 8'h20, 8'h73, 8'h70, 8'h3d, 8'h30, 8'h30, 8'h30, 8'h30, 8'h30, 8'h31, 8'h30,
        8'h30, 8'h3e, 8'h30, 8'h30, 8'h30, 8'h30, 8'h30, 8'h31, 8'h30, 8'h30, 8'h20, 8'h6d,
        8'h73, 8'h70, 8'h3d, 8'h30, 8'h30, 8'h30, 8'h30, 8'h30, 8'h31, 8'h38, 8'h30, 8'h3e,
        8'h30, 8'h30, 8'h30, 8'h30, 8'h30, 8'h31, 8'h38, 8'h30, 8'h20, 8'h77, 8'h65, 8'h3d,
        8'h30, 8'h20, 8'h61, 8'h64, 8'h64, 8'h72, 8'h3d, 8'h30, 8'h30, 8'h30, 8'h30, 8'h30,
        8'h30, 8'h30, 8'h30, 8'h20, 8'h64, 8'h61, 8'h74, 8'h61, 8'h3d, 8'h30, 8'h30, 8'h30,
        8'h30, 8'h30, 8'h30, 8'h30, 8'h30, 8'h20, 8'h6d, 8'h61, 8'h73, 8'h6b, 8'h3d, 8'h30,
        8'h30, 8'h20, 8'h74, 8'h72, 8'h61, 8'h70, 8'h3d, 8'h30, 8'h20, 8'h63, 8'h79, 8'h63,
        8'h3d, 8'h31, 8'h0a
      };
      Bit#(992) exp2 = {
        8'h48, 8'h52, 8'h49, 8'h20, 8'h70, 8'h63, 8'h3d, 8'h30, 8'h30, 8'h62, 8'h61, 8'h20,
        8'h69, 8'h6e, 8'h73, 8'h6e, 8'h3d, 8'h32, 8'h63, 8'h30, 8'h30, 8'h30, 8'h30, 8'h30,
        8'h30, 8'h20, 8'h73, 8'h70, 8'h3d, 8'h30, 8'h30, 8'h30, 8'h30, 8'h30, 8'h30, 8'h37,
        8'h30, 8'h3e, 8'h30, 8'h30, 8'h30, 8'h30, 8'h30, 8'h30, 8'h36, 8'h63, 8'h20, 8'h6d,
        8'h73, 8'h70, 8'h3d, 8'h30, 8'h30, 8'h30, 8'h30, 8'h30, 8'h31, 8'h62, 8'h30, 8'h3e,
        8'h30, 8'h30, 8'h30, 8'h30, 8'h30, 8'h31, 8'h62, 8'h30, 8'h20, 8'h77, 8'h65, 8'h3d,
        8'h31, 8'h20, 8'h61, 8'h64, 8'h64, 8'h72, 8'h3d, 8'h30, 8'h30, 8'h30, 8'h30, 8'h30,
        8'h30, 8'h37, 8'h30, 8'h20, 8'h64, 8'h61, 8'h74, 8'h61, 8'h3d, 8'h30, 8'h30, 8'h30,
        8'h30, 8'h30, 8'h30, 8'h62, 8'h61, 8'h20, 8'h6d, 8'h61, 8'h73, 8'h6b, 8'h3d, 8'h30,
        8'h33, 8'h20, 8'h74, 8'h72, 8'h61, 8'h70, 8'h3d, 8'h31, 8'h20, 8'h63, 8'h79, 8'h63,
        8'h3d, 8'h31, 8'h32, 8'h0a
      };
      Bit#(1056) exp3 = {
        8'h48, 8'h52, 8'h49, 8'h20, 8'h70, 8'h63, 8'h3d, 8'h30, 8'h30, 8'h62, 8'h61, 8'h20,
        8'h69, 8'h6e, 8'h73, 8'h6e, 8'h3d, 8'h32, 8'h63, 8'h30, 8'h30, 8'h30, 8'h30, 8'h30,
        8'h30, 8'h20, 8'h73, 8'h70, 8'h3d, 8'h30, 8'h30, 8'h30, 8'h30, 8'h30, 8'h30, 8'h37,
        8'h30, 8'h3e, 8'h30, 8'h30, 8'h30, 8'h30, 8'h30, 8'h30, 8'h36, 8'h63, 8'h20, 8'h6d,
        8'h73, 8'h70, 8'h3d, 8'h30, 8'h30, 8'h30, 8'h30, 8'h30, 8'h31, 8'h62, 8'h30, 8'h3e,
        8'h30, 8'h30, 8'h30, 8'h30, 8'h30, 8'h31, 8'h62, 8'h30, 8'h20, 8'h77, 8'h65, 8'h3d,
        8'h31, 8'h20, 8'h61, 8'h64, 8'h64, 8'h72, 8'h3d, 8'h30, 8'h30, 8'h30, 8'h30, 8'h30,
        8'h30, 8'h37, 8'h30, 8'h20, 8'h64, 8'h61, 8'h74, 8'h61, 8'h3d, 8'h30, 8'h30, 8'h30,
        8'h30, 8'h30, 8'h30, 8'h62, 8'h61, 8'h20, 8'h6d, 8'h61, 8'h73, 8'h6b, 8'h3d, 8'h30,
        8'h33, 8'h20, 8'h74, 8'h72, 8'h61, 8'h70, 8'h3d, 8'h31, 8'h20, 8'h63, 8'h79, 8'h63,
        8'h3d, 8'h34, 8'h32, 8'h39, 8'h34, 8'h39, 8'h36, 8'h37, 8'h32, 8'h39, 8'h35, 8'h0a
      };

      Bool c0 = idleOk;
      Bool c1 = readyOk;
      Bool c2 = gotUart && (uartByte == 8'h55);
      Bool c3 = gotUart && uartFrame;
      Bool c4 = lineMatches(rxbuf, 0, 123, exp0);
      Bool c5 = lineMatches(rxbuf, 123, 123, exp1);
      Bool c6 = lineMatches(rxbuf, 246, 124, exp2);
      Bool c7 = lineMatches(rxbuf, 370, 132, exp3);
      Bool c8 = (wcount == 502) && (wbad == 0);
      Bool c9 = (wcount == 502);

      $write("--- reconstructed ---\n");
      for (Integer i = 0; i < 502; i = i + 1)
        $write("%c", rxbuf[i]);
      $write("--- end ---\n");

      say(c0, "uart_idle_high");
      say(c1, "uart_ready");
      say(c2, "uart_byte_55");
      say(c3, "uart_framing");
      say(c4, "hri_line0_write");
      say(c5, "hri_line1_no_write");
      say(c6, "hri_line2_trap");
      say(c7, "hri_line3_max_cyc");
      say(c8, "hri_framing");
      say(c9, "hri_byte_count");

      Bit#(32) np = (c0 ? 1 : 0) + (c1 ? 1 : 0) + (c2 ? 1 : 0) + (c3 ? 1 : 0)
                   + (c4 ? 1 : 0) + (c5 ? 1 : 0) + (c6 ? 1 : 0) + (c7 ? 1 : 0)
                   + (c8 ? 1 : 0) + (c9 ? 1 : 0);
      $display("SUMMARY pass=%0d fail=%0d", np, 10 - np);
      $finish;
    end
    else if (cyc > 2000000) begin
      $display("FAIL timeout: no completion after %0d clocks", cyc);
      $display("SUMMARY pass=0 fail=1");
      $finish;
    end
  endrule

endmodule

endpackage
