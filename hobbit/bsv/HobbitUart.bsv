// HobbitUart.bsv -- 8N1 UART transmitter and HRI line writer.
//
// The Hobbit core retires one instruction per HRI record; on a board those
// records leave over a serial line, so this package turns an Hri into the
// same fixed-format text that the simulation and the checker use:
//
//   HRI pc=%04x insn=%04x%04x sp=%08x>%08x msp=%08x>%08x we=%d
//       addr=%08x data=%08x mask=%02x trap=%d cyc=%d\n
//
// (one line; split above for width only).  Lower-case hex, fixed widths,
// single spaces, a trailing decimal cycle count with no padding, and a
// trailing newline -- exactly the format parsed by
// hobbit/tests/hri_check.py and printed by HobbitCore.bsv, so a board run
// and a simulation run produce byte-identical lines.
//
// The fixed part of the line is 116 bytes; " cyc=" adds 5, the shortest
// decimal of the cycle count adds 1..10, and the newline adds 1, so a line
// is 123..132 bytes.  The writer keeps the constant part as a position map
// (prefixChar) and runs a small serial binary-to-BCD converter (double
// dabble) alongside the transmission, so no wide combinational divide is
// needed on every output bit.
//
// Timing is in board clocks because the UART has no baud generator of its
// own: the caller computes clksPerBit (25 MHz / 115200 = 217) and both
// modules run from the same clock.

package HobbitUart;

import Vector::*;
import HobbitTypes::*;

// ---------------------------------------------------------------------
// 8N1 transmitter: one start bit (0), eight data bits (LSB first), one
// stop bit (1), line idle high.  A send occupies 10 * clksPerBit clocks;
// ready is low until the stop bit has been on the wire for its full
// period.
// ---------------------------------------------------------------------
interface UartTx;
  method Bool ready;
  method Action send(Bit#(8) b);
  method Bit#(1) txd;
endinterface

module mkUartTx#(Integer clksPerBit)(UartTx);
  Reg#(Bool) busy <- mkReg(False);
  // {stop, data[7:0], start}; bit 0 is the next bit on the wire.
  Reg#(Bit#(10)) sh <- mkReg(10'h3FF);   // idle: all ones
  Reg#(Bit#(4)) nleft <- mkReg(0);       // shifts still due after this bit
  Reg#(Bit#(32)) cnt <- mkReg(0);       // clocks left in the current bit

  rule tick (busy);
    if (cnt == 0) begin
      if (nleft == 0) begin
        // The stop bit has had its full period.
        busy <= False;
        sh <= 10'h3FF;
      end
      else begin
        sh <= {1'b1, sh[9:1]};
        nleft <= nleft - 1;
        cnt <= fromInteger(clksPerBit - 1);
      end
    end
    else
      cnt <= cnt - 1;
  endrule

  method Bool ready = !busy;

  method Action send(Bit#(8) b) if (!busy);
    sh <= {1'b1, b, 1'b0};
    nleft <= 4'd9;
    cnt <= fromInteger(clksPerBit - 1);
    busy <= True;
  endmethod

  method Bit#(1) txd = sh[0];
endmodule

// ---------------------------------------------------------------------
// Line formatting.  Positions are fixed by the format above; see
// lineChar() for the map.
// ---------------------------------------------------------------------

function Bit#(8) hexChar(Bit#(4) v);
  if (v < 4'd10) return 8'h30 + zeroExtend(v);
  else           return 8'h61 + zeroExtend(v) - 8'd10;
endfunction

function Bit#(8) decChar(Bit#(1) v);
  return v == 0 ? 8'h30 : 8'h31;
endfunction

// Byte at position i of the fixed part of the HRI line for record r
// (i < 116; the cycle count and newline are appended by lineByte).
// Positions:
//   0..3 "HRI ", 4..6 "pc=", 7..10 pc, 11 " ",
//   12..16 "insn=", 17..24 insn0 then insn1, 25 " ",
//   26..28 "sp=", 29..36 sp_before, 37 ">", 38..45 sp_after, 46 " ",
//   47..50 "msp=", 51..58 msp_before, 59 ">", 60..67 msp_after, 68 " ",
//   69..71 "we=", 72 we, 73 " ",
//   74..78 "addr=", 79..86 addr, 87 " ",
//   88..92 "data=", 93..100 data, 101 " ",
//   102..106 "mask=", 107..108 mask, 109 " ",
//   110..114 "trap=", 115 trap.
function Bit#(8) prefixChar(Hri r, Bit#(8) i);
  case (i)
      0: return 8'h48;
      1: return 8'h52;
      2: return 8'h49;
      3: return 8'h20;
      4: return 8'h70;
      5: return 8'h63;
      6: return 8'h3d;
      7: return hexChar(r.pc[15:12]);
      8: return hexChar(r.pc[11:8]);
      9: return hexChar(r.pc[7:4]);
     10: return hexChar(r.pc[3:0]);
     11: return 8'h20;
     12: return 8'h69;
     13: return 8'h6e;
     14: return 8'h73;
     15: return 8'h6e;
     16: return 8'h3d;
     17: return hexChar(r.insn0[15:12]);
     18: return hexChar(r.insn0[11:8]);
     19: return hexChar(r.insn0[7:4]);
     20: return hexChar(r.insn0[3:0]);
     21: return hexChar(r.insn1[15:12]);
     22: return hexChar(r.insn1[11:8]);
     23: return hexChar(r.insn1[7:4]);
     24: return hexChar(r.insn1[3:0]);
     25: return 8'h20;
     26: return 8'h73;
     27: return 8'h70;
     28: return 8'h3d;
     29: return hexChar(r.sp_before[31:28]);
     30: return hexChar(r.sp_before[27:24]);
     31: return hexChar(r.sp_before[23:20]);
     32: return hexChar(r.sp_before[19:16]);
     33: return hexChar(r.sp_before[15:12]);
     34: return hexChar(r.sp_before[11:8]);
     35: return hexChar(r.sp_before[7:4]);
     36: return hexChar(r.sp_before[3:0]);
     37: return 8'h3e;
     38: return hexChar(r.sp_after[31:28]);
     39: return hexChar(r.sp_after[27:24]);
     40: return hexChar(r.sp_after[23:20]);
     41: return hexChar(r.sp_after[19:16]);
     42: return hexChar(r.sp_after[15:12]);
     43: return hexChar(r.sp_after[11:8]);
     44: return hexChar(r.sp_after[7:4]);
     45: return hexChar(r.sp_after[3:0]);
     46: return 8'h20;
     47: return 8'h6d;
     48: return 8'h73;
     49: return 8'h70;
     50: return 8'h3d;
     51: return hexChar(r.msp_before[31:28]);
     52: return hexChar(r.msp_before[27:24]);
     53: return hexChar(r.msp_before[23:20]);
     54: return hexChar(r.msp_before[19:16]);
     55: return hexChar(r.msp_before[15:12]);
     56: return hexChar(r.msp_before[11:8]);
     57: return hexChar(r.msp_before[7:4]);
     58: return hexChar(r.msp_before[3:0]);
     59: return 8'h3e;
     60: return hexChar(r.msp_after[31:28]);
     61: return hexChar(r.msp_after[27:24]);
     62: return hexChar(r.msp_after[23:20]);
     63: return hexChar(r.msp_after[19:16]);
     64: return hexChar(r.msp_after[15:12]);
     65: return hexChar(r.msp_after[11:8]);
     66: return hexChar(r.msp_after[7:4]);
     67: return hexChar(r.msp_after[3:0]);
     68: return 8'h20;
     69: return 8'h77;
     70: return 8'h65;
     71: return 8'h3d;
     72: return decChar(pack(r.mem_we));
     73: return 8'h20;
     74: return 8'h61;
     75: return 8'h64;
     76: return 8'h64;
     77: return 8'h72;
     78: return 8'h3d;
     79: return hexChar(r.mem_addr[31:28]);
     80: return hexChar(r.mem_addr[27:24]);
     81: return hexChar(r.mem_addr[23:20]);
     82: return hexChar(r.mem_addr[19:16]);
     83: return hexChar(r.mem_addr[15:12]);
     84: return hexChar(r.mem_addr[11:8]);
     85: return hexChar(r.mem_addr[7:4]);
     86: return hexChar(r.mem_addr[3:0]);
     87: return 8'h20;
     88: return 8'h64;
     89: return 8'h61;
     90: return 8'h74;
     91: return 8'h61;
     92: return 8'h3d;
     93: return hexChar(r.mem_wdata[31:28]);
     94: return hexChar(r.mem_wdata[27:24]);
     95: return hexChar(r.mem_wdata[23:20]);
     96: return hexChar(r.mem_wdata[19:16]);
     97: return hexChar(r.mem_wdata[15:12]);
     98: return hexChar(r.mem_wdata[11:8]);
     99: return hexChar(r.mem_wdata[7:4]);
    100: return hexChar(r.mem_wdata[3:0]);
    101: return 8'h20;
    102: return 8'h6d;
    103: return 8'h61;
    104: return 8'h73;
    105: return 8'h6b;
    106: return 8'h3d;
    107: return hexChar(r.mem_wmask[7:4]);
    108: return hexChar(r.mem_wmask[3:0]);
    109: return 8'h20;
    110: return 8'h74;
    111: return 8'h72;
    112: return 8'h61;
    113: return 8'h70;
    114: return 8'h3d;
    115: return decChar(pack(r.trap));
    default: return 8'h00;
  endcase
endfunction

// One binary-to-decimal step of the double-dabble algorithm: add 3 to
// every BCD digit that is 5 or more, then shift the packed digits left by
// one bit, bringing inbit into the units digit.  Doing this 32 times turns
// a 32-bit binary value into its ten BCD digits.
function Bit#(4) add3(Bit#(4) d);
  return (d >= 4'd5) ? (d + 4'd3) : d;
endfunction

function Vector#(10, Bit#(4)) dabbleShift(Vector#(10, Bit#(4)) v,
                                           Bit#(1) inbit);
  Vector#(10, Bit#(4)) a = replicate(0);
  for (Integer k = 0; k < 10; k = k + 1)
    a = update(a, k, add3(v[k]));
  Vector#(10, Bit#(4)) s = replicate(0);
  s = update(s, 0, {a[0][2:0], inbit});
  for (Integer k = 1; k < 10; k = k + 1)
    s = update(s, k, {a[k][2:0], a[k - 1][3]});
  return s;
endfunction

// Number of decimal digits: one more than the highest nonzero BCD digit.
// Zero has one digit.
function Bit#(8) digitsOf(Vector#(10, Bit#(4)) v);
  Bit#(8) n = 1;
  for (Integer k = 0; k < 10; k = k + 1)
    if (v[k] != 0) n = fromInteger(k + 1);
  return n;
endfunction

// One byte of the complete line: 116 fixed bytes, then " cyc=", the
// shortest decimal of the cycle count, then the newline.  d holds the
// BCD digits least significant first, so position 121 is d[nd-1] and the
// last digit is d[0].
function Bit#(8) lineByte(Hri r, Vector#(10, Bit#(4)) d, Bit#(8) nd,
                          Bit#(8) i);
  if (i < 8'd116)
    return prefixChar(r, i);
  else if (i < 8'd121) begin
    case (i - 8'd116)
      0: return 8'h20;        // ' '
      1: return 8'h63;        // 'c'
      2: return 8'h79;        // 'y'
      3: return 8'h63;        // 'c'
      default: return 8'h3d;  // '='
    endcase
  end
  else if (i < 8'd121 + nd) begin
    Bit#(4) k = truncate(nd - 8'd1 - (i - 8'd121));
    return 8'h30 + zeroExtend(d[k]);
  end
  else
    return 8'h0a;
endfunction

// ---------------------------------------------------------------------
// HRI line writer: serialises one variable-length line per accepted
// record.  ready is high only when no record is in flight and the
// transmitter is idle, so enq/ready behave like a one-place FIFO.
//
// The cycle count is converted to decimal by double dabble: 32 clocks,
// one binary bit per clock, adding 3 to each BCD digit that is 5 or more
// before each shift.  That is far shorter than the 121 byte-times before
// the first cyc digit is needed, so the conversion is finished long
// before the line reaches it.  The digits land in a 10-digit BCD buffer
// least significant first; the byte position then selects the field
// nibble or digit at send time, and the newline ends the line at
// 121 + nd, so nothing is truncated.
// ---------------------------------------------------------------------
interface HriWriter;
  method Bool ready;
  method Action enq(Hri r);
  method Bit#(1) txd;
endinterface

module mkHriWriter#(Integer clksPerBit)(HriWriter);
  UartTx tx <- mkUartTx(clksPerBit);
  Reg#(Maybe#(Hri)) cur <- mkReg(tagged Invalid);
  Reg#(Vector#(10, Bit#(4))) bcd <- mkReg(replicate(0));
  Reg#(Bit#(8)) nd <- mkReg(1);
  Reg#(Bit#(8)) pos <- mkReg(0);

  // Serial decimal conversion state.
  Reg#(Bool) conv <- mkReg(False);
  Reg#(Bit#(32)) bin <- mkReg(0);    // remaining binary bits
  Reg#(Bit#(6)) bitn <- mkReg(0);    // 0..31

  // One rule drives both phases: convert while conv is set, then send.
  // enq is disjoint from it because enq requires cur to be invalid.
  rule step (isValid(cur) && tx.ready);
    let r = validValue(cur);
    if (conv) begin
      Vector#(10, Bit#(4)) nxt = dabbleShift(bcd, bin[31]);
      bcd <= nxt;
      bin <= bin << 1;
      if (bitn == 6'd31) begin
        nd <= digitsOf(nxt);
        conv <= False;
      end
      else
        bitn <= bitn + 1;
    end
    else begin
      tx.send(lineByte(r, bcd, nd, pos));
      if (pos == 8'd121 + nd) begin
        cur <= tagged Invalid;
        pos <= 0;
      end
      else
        pos <= pos + 1;
    end
  endrule

  method Bool ready = !isValid(cur) && tx.ready;

  method Action enq(Hri r) if (!isValid(cur) && tx.ready);
    cur <= tagged Valid r;
    nd <= 0;
    pos <= 0;
    conv <= True;
    bin <= r.cyc;
    bcd <= replicate(0);
    bitn <= 0;
  endmethod

  method Bit#(1) txd = tx.txd;
endmodule

endpackage
