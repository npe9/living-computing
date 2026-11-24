// Sonic.bsv -- the subset of the National DP83932 SONIC that 1st Edition
// Plan 9's devether.c uses, at 0xA4400000 (io.h SONICADDR), IRQ 9.
//
// Behaviour reference: tools/p9boot.py `Sonic` and SONIC_CHOICES, which
// boot the shipped kernel through BOOTP and IL to rc; design and
// interfaces: hobbit/docs/ulx3s_ethernet.md section 6; test and
// discrimination: sonic.md.  The RTL makes exactly the model's DMA
// accesses, in the model's order, one 32-bit word at a time, so a trace
// of the model (sonic_trace.py) can be replayed into it word for word.
//
// Registers: io.h's `Sonic`, register i at byte offset 4*i, 16 bits wide
// (zero-extended on read).  Offsets above 0xFC alias (addr[7:2]).  Writes
// ignore the byte enables, as Sonic.write does.  isr is write-one-to-
// clear; rsa/rea/rrp/rwp drop bits 1:0; cr runs commands.  irq = (isr &
// imr) != 0.
//
// Commands (each runs to completion before the write is answered):
//   Rst      reset state (cr = Rst|Rxdis; Lcam/Rrra/Txp/Htx cleared)
//   Rrra     read the 4-word resource at urra:rrp (crba, rbwc), advance
//            rrp by 16, wrap rea -> rsa
//   Lcam     load cdc CAM entries from urra:cdp, then the CE word; isr Lcd
//   Txp      transmit the descriptors from utda:ctda until a link has EOL;
//            each frame goes out of `tx` whole (it is gathered first into
//            a 2 KB buffer); status word 0x0001; isr Txdn
//   Rxen/Rxdis/Stp/St/Htx only set and clear cr bits.
// Receive: a whole frame arrives on `rx` (bytes with `last`; a frame
// whose last byte has `bad` is dropped), is filtered (rcr Pro, Brd, the
// enabled CAM entries), and is written with its CRC-32 FCS, padded to 4
// bytes with 0xFF, at crba; then the descriptor, as Sonic.receive.
//
// DMA: `dma.req` gives one-word requests (physical byte addresses,
// little-endian lanes); `dma.rdata` takes one word per read, in order.
// One read is outstanding at a time.  Writes are posted: the arbiter must
// make an accepted write visible before the core's later reads (the
// engine updates isr only after its last write is accepted).
//
// Fail loud: where the model raises Stop the RTL sets the sticky `fault`
// with a code in faultInfo and abandons the command or frame (the write
// is still answered):
//   1 a command bit outside 0x03BF       2 rrp reached rwp
//   3 transmit: fragments != packet size 4 transmit frame over 2 KB
//   5 receive: frame does not fit the buffer (rbwc)
//   6 receive: frame over 2 KB (or 4 bytes short of it, with its FCS)
package Sonic;

import FIFOF    :: *;
import FIFO     :: *;
import GetPut   :: *;
import RegFile  :: *;
import Vector   :: *;
import StmtFSM  :: *;

export FrameByte(..);
export SonicDmaReq(..);
export SonicDma(..);
export HobbitSonic(..);
export mkSonic;
export crc32Byte;

typedef struct {
  Bit#(8) data;
  Bool    last;
  Bool    bad;        // meaningful on `last`: drop this frame
} FrameByte deriving (Bits, Eq, FShow);

typedef struct {
  Bit#(32) addr;      // physical byte address, bits 1:0 = 0
  Bool     write;
  Bit#(32) wdata;     // byte at addr+i in wdata[8i+7:8i]
  Bit#(4)  be;        // writes only
} SonicDmaReq deriving (Bits, Eq, FShow);

interface SonicDma;
  interface Get#(SonicDmaReq) req;
  interface Put#(Bit#(32))    rdata;  // one per read, in request order
endinterface

interface HobbitSonic;
  method Action req(Bit#(12) addr, Bit#(32) wdata, Bit#(4) be, Bool write);
  method ActionValue#(Bit#(32)) resp;
  (* always_ready *) method Bool irq;
  interface SonicDma dma;
  interface Put#(FrameByte) rx;       // from the link or MAC
  interface Get#(FrameByte) tx;       // to the link or MAC
  (* always_ready *) method Bool busy;        // a request or frame in hand
  (* always_ready *) method Bool fault;
  (* always_ready *) method Bit#(16) faultInfo;
endinterface

// Ethernet CRC-32, reflected 0xEDB88320, one byte (no init/final xor).
function Bit#(32) crc32Byte(Bit#(32) c, Bit#(8) b);
  Bit#(32) x = c ^ zeroExtend(b);
  for (Integer k = 0; k < 8; k = k + 1)
    x = (x >> 1) ^ ((x[0] == 1) ? 32'hEDB88320 : 0);
  return x;
endfunction

typedef struct {
  Bit#(12) addr; Bit#(32) wdata; Bool write;
} SonicReq deriving (Bits);

// register indexes (io.h Sonic)
Integer iCR = 0; Integer iDCR = 1; Integer iRCR = 2; Integer iTCR = 3;
Integer iIMR = 4; Integer iISR = 5; Integer iUTDA = 6; Integer iCTDA = 7;
Integer iURDA = 'h0D; Integer iCRDA = 'h0E;
Integer iEOBC = 'h13; Integer iURRA = 'h14; Integer iRSA = 'h15;
Integer iREA = 'h16; Integer iRRP = 'h17; Integer iRWP = 'h18;
Integer iCE = 'h25; Integer iCDP = 'h26; Integer iCDC = 'h27;
Integer iRSC = 'h2B; Integer iMPT = 'h2E;

Bit#(16) cHTX = 'h0001; Bit#(16) cTXP = 'h0002; Bit#(16) cRXDIS = 'h0004;
Bit#(16) cRXEN = 'h0008; Bit#(16) cRST = 'h0080; Bit#(16) cRRRA = 'h0100;
Bit#(16) cLCAM = 'h0200; Bit#(16) cALL = 'h03BF;
Bit#(16) sRDE = 'h0040; Bit#(16) sTXDN = 'h0200; Bit#(16) sPKTRX = 'h0400;
Bit#(16) sLCD = 'h1000;
Bit#(16) rPRX = 'h0001; Bit#(16) rLPKT = 'h0040; Bit#(16) rBC = 'h0080;
Bit#(16) rPRO = 'h1000; Bit#(16) rBRD = 'h2000;

(* synthesize *)
module mkSonic(HobbitSonic);
  // reset: cr = Rst|Stp|Rxdis (SONIC_CHOICES['registers']), the rest 0
  Vector#(64, Reg#(Bit#(16))) r = newVector;
  for (Integer x = 0; x < 64; x = x + 1)
    r[x] <- mkReg((x == 0) ? 'h0094 : 0);
  Reg#(Bool) started <- mkReg(False);

  FIFOF#(SonicReq)    reqQ  <- mkFIFOF;
  FIFOF#(Bit#(32))    respQ <- mkFIFOF;
  FIFOF#(SonicDmaReq) dmaQ  <- mkFIFOF;
  FIFOF#(Bit#(32))    rdQ   <- mkSizedFIFOF(4);
  FIFOF#(FrameByte)   txQ   <- mkFIFOF;

  Reg#(Bool)     faultR <- mkReg(False);
  Reg#(Bit#(16)) faultC <- mkReg(0);
  Reg#(Bool)     active <- mkReg(False);

  // receive state (model: crba, rbwc, rx_eol) and the CAM
  Reg#(Bit#(32)) crba  <- mkReg(0);
  Reg#(Bit#(32)) rbwc  <- mkReg(0);
  Reg#(Bool)     rxEol <- mkReg(False);
  Vector#(16, Reg#(Bit#(48))) cam <- replicateM(mkReg(0));
  Reg#(Bit#(16)) camValid <- mkReg(0);

  // the frame buffers
  RegFile#(Bit#(11), Bit#(8)) rxBuf <- mkRegFileFull;
  RegFile#(Bit#(11), Bit#(8)) txBuf <- mkRegFileFull;
  Reg#(Bit#(12)) rxLen <- mkReg(0);       // bytes in rxBuf so far
  Reg#(Bool)     rxOver <- mkReg(False);  // this frame overflowed
  Reg#(Bit#(32)) rxCrc <- mkReg('1);
  Reg#(Bit#(48)) rxDst <- mkReg(0);       // frame byte i in bits 8i+7:8i
  Reg#(Bool)     rxReady <- mkReg(False); // a whole good frame waits
  Reg#(Bool)     rxFresh <- mkReg(True);  // the next byte starts a frame
  Reg#(Bool)     rxFault <- mkReg(False); // a frame over 2 KB came in
  PulseWire      rxSet <- mkPulseWire;
  PulseWire      rxClr <- mkPulseWire;

  // FSM working registers
  Reg#(SonicReq) cur <- mkRegU;
  Reg#(Bit#(16)) cmd <- mkReg(0);
  Reg#(Bool)     skip <- mkReg(False);
  Reg#(Bit#(32)) a <- mkReg(0);           // descriptor / resource base
  Reg#(Bit#(32)) fp <- mkReg(0);          // fragment / CAM pointer
  Reg#(Bit#(32)) rd <- mkReg(0);          // last DMA read
  Reg#(Bit#(16)) t <- mkReg(0);
  Reg#(Bit#(16)) n <- mkReg(0);
  Reg#(Bit#(16)) size <- mkReg(0);
  Reg#(Bit#(16)) nfrag <- mkReg(0);
  Reg#(Bit#(16)) i <- mkReg(0);
  Reg#(Bit#(32)) ptr <- mkReg(0);
  Reg#(Bit#(32)) w <- mkReg(0);
  Reg#(Bit#(32)) wend <- mkReg(0);
  Reg#(Bit#(3))  k <- mkReg(0);
  Reg#(Bit#(12)) tlen <- mkReg(0);
  Reg#(Bit#(12)) j <- mkReg(0);
  Reg#(Bool)     txMore <- mkReg(False);
  Reg#(Bool)     ok <- mkReg(True);
  Reg#(Bit#(32)) word <- mkReg(0);
  Reg#(Bit#(16)) kind <- mkReg(0);
  Reg#(Bit#(16)) status <- mkReg(0);
  Reg#(Bit#(32)) start <- mkReg(0);
  Reg#(Bit#(32)) rda <- mkReg(0);
  Reg#(Bit#(12)) padded <- mkReg(0);
  Reg#(Bit#(32)) fcs <- mkReg(0);

  function Bit#(32) cat16(Bit#(16) hi, Bit#(16) lo) = {hi, lo};
  function Bit#(8) byteOf(Bit#(32) v, Bit#(2) y) = truncate(v >> {y, 3'b0});

  function Action setFault(Bit#(16) code);
    action
      faultR <= True;
      faultC <= code;
      ok <= False;
      $display("SONIC FAULT %0d", code);
    endaction
  endfunction

  function Stmt dmaRd(Bit#(32) addr) = seq
    dmaQ.enq(SonicDmaReq {addr: addr, write: False, wdata: 0, be: 0});
    action rd <= rdQ.first; rdQ.deq; endaction
  endseq;

  function Action dmaWr(Bit#(32) addr, Bit#(16) v) =
    dmaQ.enq(SonicDmaReq {addr: addr, write: True, wdata: zeroExtend(v),
                          be: 'hF});

  // ---- the receive filter (SONIC_CHOICES['filter'])
  function Maybe#(Bit#(16)) accepts;
    Bit#(16) rcr = r[iRCR];
    Bool hit = False;
    for (Integer e = 0; e < 16; e = e + 1)
      if (camValid[e] == 1 && r[iCE][e] == 1 && cam[e] == rxDst) hit = True;
    if ((rcr & rPRO) != 0 && rxDst[0] == 0) return tagged Valid 0;
    else if ((rcr & rBRD) != 0 && rxDst == '1) return tagged Valid rBC;
    else if (hit) return tagged Valid 0;
    else return tagged Invalid;
  endfunction

  // ---- Rrra (SONIC_CHOICES['rra'])
  Stmt rra = seq
    a <= cat16(r[iURRA], r[iRRP]);
    dmaRd(a + 4);  t <= rd[15:0];
    dmaRd(a);      crba <= cat16(t, rd[15:0]);
    dmaRd(a + 12); t <= rd[15:0];
    dmaRd(a + 8);  rbwc <= cat16(t, rd[15:0]);
    action
      Bit#(16) nx = r[iRRP] + 16;
      if (nx == r[iREA]) nx = r[iRSA];
      r[iRRP] <= nx;
      if (nx == r[iRWP]) setFault(2);
    endaction
  endseq;

  // ---- Lcam (SONIC_CHOICES['cam'])
  Stmt lcam = seq
    fp <= cat16(r[iURRA], r[iCDP]);
    n <= zeroExtend(r[iCDC][4:0]);
    while (n != 0) seq
      dmaRd(fp);      t <= rd[15:0];             // entry number
      dmaRd(fp + 4);  word <= zeroExtend(rd[15:0]);
      dmaRd(fp + 8);  word <= {rd[15:0], word[15:0]};
      dmaRd(fp + 12);
      action
        cam[t[3:0]] <= {rd[15:0], word};
        camValid[t[3:0]] <= 1;
        n <= n - 1;
        fp <= fp + 16;
      endaction
    endseq
    action r[iCDC] <= 0; r[iCDP] <= fp[15:0]; endaction
    dmaRd(fp);
    action r[iCE] <= rd[15:0]; r[iISR] <= r[iISR] | sLCD; endaction
  endseq;

  // ---- Txp (SONIC_CHOICES['transmit'])
  Stmt transmit = seq
    txMore <= True;
    while (txMore && ok) seq
      a <= cat16(r[iUTDA], r[iCTDA] & 'hFFFE);
      dmaRd(a + 8);  size <= rd[15:0];
      dmaRd(a + 12); action nfrag <= rd[15:0]; i <= 0; tlen <= 0;
                            fp <= a + 16; endaction
      while (i < nfrag && ok) seq
        dmaRd(fp + 4); t <= rd[15:0];
        dmaRd(fp);     ptr <= cat16(t, rd[15:0]);
        dmaRd(fp + 8); action n <= rd[15:0];
                              w <= ptr & ~3;
                              wend <= (ptr + zeroExtend(rd[15:0]) - 1) & ~3;
                       endaction
        if (n != 0)
          while (w <= wend && ok) seq
            dmaRd(w);
            k <= 0;
            while (k < 4 && ok) action
              Bit#(32) ba = w + zeroExtend(k);
              if (ba >= ptr && ba < ptr + zeroExtend(n)) begin
                if (tlen == 2047) setFault(4);
                else begin
                  txBuf.upd(truncate(tlen), byteOf(rd, truncate(k)));
                  tlen <= tlen + 1;
                end
              end
              k <= k + 1;
            endaction
            w <= w + 4;
          endseq
        action i <= i + 1; fp <= fp + 12; endaction
      endseq
      if (ok && zeroExtend(tlen) != size) setFault(3);
      if (ok) seq
        j <= 0;
        while (j < tlen) action
          txQ.enq(FrameByte {data: txBuf.sub(truncate(j)),
                             last: j == tlen - 1, bad: False});
          j <= j + 1;
        endaction
        dmaWr(a, 1);
        dmaRd(a + 16 + 12 * zeroExtend(nfrag));
        action
          r[iCTDA] <= rd[15:0];
          if (rd[0] == 1) txMore <= False;
        endaction
      endseq
    endseq
    if (ok) r[iISR] <= r[iISR] | sTXDN;
  endseq;

  // ---- a register access
  Stmt access = seq
    action
      let q = reqQ.first;
      reqQ.deq;
      cur <= q;
      ok <= True;
    endaction
    if (!cur.write)
      respQ.enq(zeroExtend(r[cur.addr[7:2]]));
    else if (cur.addr[7:2] != fromInteger(iCR)) action
      Bit#(16) d = cur.wdata[15:0];
      Bit#(6) x = cur.addr[7:2];
      if (x == fromInteger(iISR)) r[x] <= r[x] & ~d;
      else if (x == fromInteger(iRSA) || x == fromInteger(iREA)
               || x == fromInteger(iRRP) || x == fromInteger(iRWP))
        r[x] <= d & 'hFFFC;
      else r[x] <= d;
      respQ.enq(0);
    endaction
    else seq
      action
        Bit#(16) c = cur.wdata[15:0];
        Bit#(16) cr = r[iCR];
        cmd <= c;
        if ((cr & cRST) != 0 && (c & cRST) == 0) begin
          r[iCR] <= cr & ~cRST;           // leaving software reset
          skip <= True;
        end
        else begin
          Bit#(16) nc = cr | (c & 'h03BF);
          if ((c & cRXDIS) != 0) nc = nc & ~cRXEN;
          if ((c & cRXEN) != 0) nc = nc & ~cRXDIS;
          if ((c & cRST) != 0)
            nc = (nc & ~(cLCAM | cRRRA | cTXP | cHTX)) | cRST | cRXDIS;
          r[iCR] <= nc;
          skip <= (c & cRST) != 0;
        end
      endaction
      if (!skip) seq
        if ((cmd & cRRRA) != 0) seq
          rra;
          r[iCR] <= r[iCR] & ~cRRRA;
        endseq
        if ((cmd & cLCAM) != 0 && ok) seq
          lcam;
          r[iCR] <= r[iCR] & ~cLCAM;
        endseq
        if ((cmd & cTXP) != 0 && ok) seq
          transmit;
          r[iCR] <= r[iCR] & ~cTXP;
        endseq
        if ((cmd & ~cALL) != 0 && ok) setFault(1);
      endseq
      respQ.enq(0);
    endseq
  endseq;

  // ---- one inbound frame (SONIC_CHOICES['receive'])
  Bit#(12) dlen = rxLen + 4;
  Stmt receive = seq
    ok <= True;
    if ((r[iCR] & cRXEN) != 0 && isValid(accepts)) seq
      action
        kind <= fromMaybe(0, accepts);
        padded <= ((dlen - 1) | 3) + 1;
        fcs <= ~rxCrc;
      endaction
      if (zeroExtend(padded) > (rbwc << 1)) setFault(5);
      if (ok && rxEol) seq
        dmaRd(cat16(r[iURDA], r[iCRDA]) + 20);
        if (rd[0] == 1) action
          r[iMPT] <= r[iMPT] + 1;
          ok <= False;                     // no descriptor: dropped
        endaction
        else seq
          dmaWr(cat16(r[iURDA], r[iCRDA]) + 24, 0);
          action
            r[iCRDA] <= rd[15:0];
            rxEol <= False;
            r[iISR] <= r[iISR] | sPKTRX;
          endaction
        endseq
      endseq
      if (ok) seq
        action
          rda <= cat16(r[iURDA], r[iCRDA]) & ~1;
          start <= crba;
          j <= 0;
        endaction
        while (j < padded) seq
          k <= 0;
          while (k < 4) action
            Bit#(12) x = j + zeroExtend(k);
            Bit#(8) b = 'hFF;
            if (x < rxLen) b = rxBuf.sub(truncate(x));
            else if (x < dlen) begin
              b = byteOf(fcs, truncate(x - rxLen));
            end
            word <= {b, word[31:8]};
            k <= k + 1;
          endaction
          dmaQ.enq(SonicDmaReq {addr: start + zeroExtend(j), write: True,
                                wdata: word, be: 'hF});
          j <= j + 4;
        endseq
        action
          Bit#(32) left = rbwc - zeroExtend(padded >> 1);
          crba <= crba + zeroExtend(padded);
          rbwc <= left;
          status <= rPRX | kind
                    | ((left < zeroExtend(r[iEOBC])) ? rLPKT : 0);
        endaction
        dmaWr(rda, status);
        dmaWr(rda + 4, zeroExtend(dlen));
        dmaWr(rda + 8, start[15:0]);
        dmaWr(rda + 12, start[31:16]);
        dmaWr(rda + 16, r[iRSC]);
        dmaRd(rda + 20);
        if (rd[0] == 1) action
          rxEol <= True;
          r[iISR] <= r[iISR] | sRDE;
        endaction
        else seq
          dmaWr(rda + 24, 0);
          action
            r[iCRDA] <= rd[15:0];
            r[iISR] <= r[iISR] | sPKTRX;
          endaction
        endseq
        r[iRSC] <= (r[iRSC] & 'hFF00) | ((r[iRSC] + 1) & 'h00FF);
        if ((status & rLPKT) != 0) seq
          rra;
          r[iRSC] <= (r[iRSC] + 'h100) & 'hFF00;
        endseq
      endseq
    endseq
    rxClr.send;
  endseq;

  Stmt main = seq
    while (True) seq
      await(reqQ.notEmpty || rxReady);
      active <= True;
      if (reqQ.notEmpty) access;
      else receive;
      // isr may be read only after the last write is accepted
      await(!dmaQ.notEmpty);
      active <= False;
    endseq
  endseq;
  FSM fsm <- mkFSM(main);

  rule go (!started);
    started <= True;
    fsm.start;
  endrule

  rule rxFlag (rxSet || rxClr);
    rxReady <= rxSet;
  endrule

  method Action req(Bit#(12) addr, Bit#(32) wdata, Bit#(4) be, Bool write);
    reqQ.enq(SonicReq {addr: addr, wdata: wdata, write: write});
  endmethod

  method ActionValue#(Bit#(32)) resp;
    respQ.deq;
    return respQ.first;
  endmethod

  method Bool irq = (r[iISR] & r[iIMR]) != 0;

  interface SonicDma dma;
    interface Get req = toGet(dmaQ);
    interface Put rdata = toPut(rdQ);
  endinterface

  interface Put rx;
    method Action put(FrameByte b) if (!rxReady);
      // the first byte after a `last` starts a new frame
      Bit#(12) at = rxFresh ? 0 : rxLen;
      Bit#(32) crc = rxFresh ? '1 : rxCrc;
      Bool over = rxFresh ? False : rxOver;
      Bit#(48) dst = rxDst;
      if (at == 2044) over = True;              // no room for the FCS
      else begin
        rxBuf.upd(truncate(at), b.data);
        at = at + 1;
        crc = crc32Byte(crc, b.data);
        if (at <= 6) dst = (dst & ~(48'hFF << (8 * (at - 1))))
                           | (zeroExtend(b.data) << (8 * (at - 1)));
      end
      rxLen <= at;
      rxCrc <= crc;
      rxOver <= over;
      rxDst <= dst;
      rxFresh <= b.last;
      if (b.last && !b.bad && !over) rxSet.send;
      if (b.last && over) rxFault <= True;
    endmethod
  endinterface

  interface Get tx = toGet(txQ);

  method Bool busy = active || reqQ.notEmpty || rxReady || dmaQ.notEmpty
                     || txQ.notEmpty;
  method Bool fault = faultR || rxFault;
  method Bit#(16) faultInfo = faultR ? faultC : 6;
endmodule

endpackage
