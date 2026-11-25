// PIM/m core: the SCSI box.  scsi_init (22:DF) and scsi_command (22:DB),
// whose firmware is lost: what they do here is OURS, the reference
// model's (ref/pimm/pimm.py i_scsi_init, i_scsi_command, scsi_poll,
// scsi_do; docs/pimm_semantics.md), kept to the stand-in for a machine
// without them, PIMOS bios/scsi/scsi_blt.kl1.  The device is NOT here: it
// is on the core's port (devReq / devResp), which the lockstep bench
// answers from the reference's device tape (ref/pimm/driver.py) and a
// live front end could answer later.
//
//   init           scsi_init, after the exec stage has written Obj (1):
//                  the device is asked its buffer size (Init on the
//                  port, Size back), then TargetInterruptVector, a new
//                  vector {0, 0, 0}.  a = that vector
//   initInfo       then Info, a new vector {size, 8, 4, 0}
//   command(o, v)  scsi_command(Obj, {Unit, LUN, CDB, Length, Dir,
//                  Buffer, 0}, ...), the exec stage having waited for
//                  Obj and the vector: the vector's seven elements
//                  dereferenced in order.  One that is unbound: Wait, at
//                  its cell (the exec stage makes the stub's goal and
//                  hooks it there, as string_operation's).  Anything but
//                  a vector of seven, integers at 0, 1, 3, 4, an 8-bit
//                  string at 2 and 5, the integer 0 at 6 and a length
//                  in 0..the buffer's: Refused.  Otherwise Id is the
//                  count of commands so far and the command goes to the
//                  device (the exchange, below).  Finished: Done with
//                  Data, TransferredLength, Id, Result, after the
//                  commands waiting for the device have been given to
//                  it again (the poll, below: "the device has moved").
//                  Not finished yet: three new variables for Data,
//                  TransferredLength and Result, the command kept in
//                  the box's waiting list, Done with those at once
//   poll           the machine has run dry (the bench's POLL): the
//                  poll; a = the number of commands that finished
//
// The exchange: Command {unit, LUN, direction, length, CDB length} on the
// port, then the CDB's words, then for a SEND (direction 1) the first
// `length` bytes of the buffer in words (four bytes from the top; the
// last word's tail is not the command's).  The answer: not ready; or
// ready with Result and n bytes received, then their words.  For n > 0
// Data is a NEW 8-bit string as long as the buffer, the n bytes and
// then the rest of the buffer's (reference: make_string(8, data +
// buf[n:]), its descriptor and every word written, the pad bytes zero);
// for n = 0 Data is the buffer itself.  TransferredLength is n for
// direction 2 (in), the length asked for otherwise.
//
// The poll: each waiting command, oldest first, is given to the device
// again; one that finishes has its three variables unified with Data,
// TransferredLength and Result in that order (waking whoever waits), one
// that does not keeps its place.  The waiting list holds what the
// command was given (the CDB and buffer as words in memory: read again
// at each try, where the reference keeps a copy of their bytes; a
// change to them in between would show on the B line).  It holds at
// most four (one is the most run, ref_scsi.py's "late"); a fifth stops
// the simulation.
package PimmScsiBox;

import FIFO::*;
import FIFOF::*;
import Vector::*;
import PimmGen::*;
import PimmTypes::*;
import PimmMem::*;
import PimmDBox::*;
import PimmGBox::*;

// ---- the port ------------------------------------------------------------
typedef struct {
  Int#(32) unit; Int#(32) lun; Int#(32) dir; Int#(32) length; Bit#(32) cdbLen;
} ScsiCmd deriving (Bits);

typedef union tagged {
  void     Init;          // scsi_init: the device's buffer size
  ScsiCmd  Command;       // then the CDB's words, then a SEND's
  Bit#(32) Word;
} ScsiOut deriving (Bits);

typedef union tagged {
  Bit#(32) Size;                                              // to Init
  struct { Bool ready; Bit#(32) result; Bit#(32) n; } Answer;  // then n bytes in words
  Bit#(32) Data;
} ScsiIn deriving (Bits);

// ---- the exec stage's side -----------------------------------------------
typedef union tagged {
  Cell Vector;                                                // init, initInfo
  Addr Wait;                                                  // command: an element unbound
  void Refused;                                               // command: not modelled
  struct { Cell data; Cell tl; Cell id; Cell result; } Done;  // command (NewObj is Obj)
} ScsiResult deriving (Bits);

interface PimmScsiBox;
  method Action init;
  method Action initInfo;
  method Action command(Cell obj, Cell vec);
  method ActionValue#(ScsiResult) result;
  method Action poll;
  method ActionValue#(Bit#(32)) polled;
  // the device
  method ActionValue#(ScsiOut) devReq;
  method Action devResp(ScsiIn r);
  // a checkpoint (ref/pimm/lockstep_shell.py), between runs: 4 the
  // commands so far (Id); 16..26 a waiting command's fields, in the
  // order of ScsiCmdState, into a staging register; 31 the staged
  // command onto the waiting list (pimm.py scsi_waiting, oldest first)
  method Action restore(Bit#(8) which, Cell c);
endinterface

typedef union tagged {
  void Init;
  void InitInfo;
  struct { Cell obj; Cell vec; } Command;
  void Poll;
} ScsiReq deriving (Bits);

// a command as given to the device
typedef struct {
  Int#(32) unit; Int#(32) lun; Int#(32) dir; Int#(32) length;
  Cell cdb; Bit#(32) cdbLen; Cell bufw; Bit#(32) bufLen;
  Cell v0; Cell v1; Cell v2;          // a waiting command's variables
} ScsiCmdState deriving (Bits);

typedef enum { BIdle,
               BI1, BI2, BIW,
               BC1, BC2, BC3, BC4, BC5, BC6, BC7,
               BX1, BXRd, BXWd, BX3, BX4, BX5, BX6, BXDone,
               BN1, BN2, BN3,
               BP0, BPU, BPUr, BPUw } ScsiState deriving (Bits, Eq);

typedef enum { CtxCommand, CtxPoll } Ctx deriving (Bits, Eq);

module mkPimmScsiBox#(MemPort mem, PimmGBox gbox, PimmDBox dbox)(PimmScsiBox);
  FIFO#(ScsiReq)    reqQ  <- mkFIFO;
  FIFO#(ScsiResult) resQ  <- mkFIFO;
  FIFO#(Bit#(32))   pollQ <- mkFIFO;
  FIFO#(ScsiOut)    outQ  <- mkFIFO;
  FIFO#(ScsiIn)     inQ   <- mkFIFO;
  FIFOF#(ScsiCmdState) waiting <- mkSizedFIFOF(5);   // a fifth stops, below

  Reg#(ScsiState) st     <- mkReg(BIdle);
  Reg#(Bit#(32))  size   <- mkRegU;      // the device's buffer size
  Reg#(Bool)      second <- mkRegU;      // init: Info, not the interrupt vector
  Reg#(Addr)      at     <- mkRegU;      // a new vector or string
  Reg#(Bit#(32))  k      <- mkRegU;      // the cell, element or word in hand
  Reg#(Cell)      vec    <- mkRegU;
  Reg#(Addr)      base   <- mkRegU;      // the vector's first element
  Vector#(7, Reg#(Cell)) e <- replicateM(mkRegU);
  Reg#(Bit#(32))  count  <- mkReg(0);    // commands so far: Id (OURS)
  Reg#(Bit#(3))   nWaiting <- mkReg(0);
  Reg#(ScsiCmdState) cur <- mkRegU;      // the command being exchanged
  Reg#(Ctx)       ctx    <- mkRegU;
  Reg#(Bool)      fromBench <- mkRegU;   // the poll: the bench's, not a command's
  Reg#(Bit#(3))   left   <- mkRegU;      // the poll: commands still to try
  Reg#(Bit#(32))  done   <- mkRegU;      // ... and those finished
  Reg#(Bool)      inCdb  <- mkRegU;      // the exchange: CDB words, then a SEND's
  Reg#(Bit#(32))  n      <- mkRegU;      // bytes received
  Reg#(Bit#(32))  res    <- mkRegU;      // Result
  Reg#(Cell)      data   <- mkRegU;      // Data
  Reg#(Bit#(2))   ui     <- mkRegU;      // the poll: the variable being unified
  Reg#(ScsiResult) answer <- mkRegU;     // a finished command's, during its poll
  Reg#(ScsiCmdState) staged <- mkRegU;   // a checkpoint's waiting command, being given

  function Addr toAddr(Bit#(32) v) = truncate(v);      // through 32 bits
  function Bit#(32) wordsOf(Bit#(32) bytes) = (bytes + 3) >> 2;
  Bit#(32) tl = cur.dir == 2 ? n : pack(cur.length);

  // a string's descriptor: 8-bit elements, and how many
  function Bool str8(Cell d) = d.tag == tag_CDESC && d.val[26:24] == 3;
  function Bit#(32) str8Len(Cell d) = (zeroExtend(d.val[23:0]) << 2) - zeroExtend(d.val[28:27]);

  rule accept (st == BIdle);
    reqQ.deq;
    case (reqQ.first) matches
      tagged Init: begin
        outQ.enq(tagged Init);
        second <= False;
        st <= BI1;
      end
      tagged InitInfo: begin
        second <= True;
        gbox.alloc(4);
        st <= BI2;
      end
      tagged Command .c: begin
        vec <= c.vec;
        mem.read(cellAddr(c.vec));
        // NewObj is the exec stage's Obj; obj is not kept here
        st <= BC1;
      end
      tagged Poll: begin
        fromBench <= True;
        left <= nWaiting;
        done <= 0;
        st <= BP0;
      end
    endcase
  endrule

  // ---- scsi_init ---------------------------------------------------------
  rule initSize (st == BI1);
    inQ.deq;
    if (inQ.first matches tagged Size .s) begin
      size <= s;
      gbox.alloc(3);
      st <= BI2;
    end
    else fatal("scsi: the device did not answer scsi_init");
  endrule

  rule initVector (st == BI2);
    let a <- gbox.allocResult;
    at <= a;
    k <= 0;
    st <= BIW;
  endrule

  rule initWrite (st == BIW);
    Bit#(32) v = !second ? 0 : (k == 0 ? size : (k == 1 ? 8 : (k == 2 ? 4 : 0)));
    Bit#(32) cells = second ? 4 : 3;
    mem.write(at + toAddr(k), intC(v));
    if (k + 1 == cells) begin
      resQ.enq(tagged Vector mkCell(second ? tag_VECT4o : tag_VECT3o, absAddr(at)));
      st <= BIdle;
    end
    else k <= k + 1;
  endrule

  // ---- scsi_command: the vector ------------------------------------------
  rule cmdDesc (st == BC1);
    let d <- mem.data;
    base <= cellAddr(d);
    if (d.tag != tag_VDESC) begin
      resQ.enq(tagged Refused);
      st <= BIdle;
    end
    else begin
      mem.read(cellAddr(vec) + 1);
      st <= BC2;
    end
  endrule

  rule cmdSize (st == BC2);
    let c <- mem.data;
    if (c.val != 7) begin
      resQ.enq(tagged Refused);
      st <= BIdle;
    end
    else begin
      k <= 0;
      dbox.deref(mkCell(tag_REFx, absAddr(base)));
      st <= BC3;
    end
  endrule

  // each element as taken from its cell (MRB on), dereferenced
  rule cmdElement (st == BC3);
    let v <- dbox.derefResult;
    e[k] <= v;
    if (k == 6) st <= BC4;
    else begin
      dbox.deref(mkCell(tag_REFx, absAddr(base + toAddr(k + 1))));
      k <= k + 1;
    end
  endrule

  function Bool unb(Integer i) = isRef(e[i]);

  rule cmdCheck (st == BC4);
    if (unb(0) || unb(1) || unb(2) || unb(3) || unb(4) || unb(5) || unb(6)) begin
      Cell w = unb(0) ? e[0] : unb(1) ? e[1] : unb(2) ? e[2] : unb(3) ? e[3]
             : unb(4) ? e[4] : unb(5) ? e[5] : e[6];
      resQ.enq(tagged Wait cellAddr(w));
      st <= BIdle;
    end
    else if (!isInt(e[0]) || !isInt(e[1]) || !isStrg(e[2]) || !isInt(e[3]) || !isInt(e[4])
             || !isStrg(e[5]) || !isInt(e[6]) || e[6].val != 0) begin
      resQ.enq(tagged Refused);
      st <= BIdle;
    end
    else begin
      mem.read(cellAddr(e[2]));
      st <= BC5;
    end
  endrule

  rule cmdCdb (st == BC5);
    let d <- mem.data;
    if (!str8(d)) begin
      resQ.enq(tagged Refused);
      st <= BIdle;
    end
    else begin
      k <= str8Len(d);
      mem.read(cellAddr(e[5]));
      st <= BC6;
    end
  endrule

  rule cmdBuffer (st == BC6);
    let d <- mem.data;
    Int#(32) length = unpack(e[3].val);
    if (!str8(d) || length < 0 || pack(length) > str8Len(d)) begin
      resQ.enq(tagged Refused);
      st <= BIdle;
    end
    else begin
      cur <= ScsiCmdState { unit: unpack(e[0].val), lun: unpack(e[1].val), dir: unpack(e[4].val),
                            length: length, cdb: e[2], cdbLen: k, bufw: e[5], bufLen: str8Len(d),
                            v0: ?, v1: ?, v2: ? };
      ctx <= CtxCommand;
      st <= BX1;
    end
  endrule

  // ---- the exchange with the device --------------------------------------
  rule xCommand (st == BX1);
    outQ.enq(tagged Command ScsiCmd { unit: cur.unit, lun: cur.lun, dir: cur.dir,
                                      length: cur.length, cdbLen: cur.cdbLen });
    inCdb <= True;
    k <= 0;
    st <= BXRd;
  endrule

  // the CDB's words, then a SEND's
  rule xRead (st == BXRd);
    Bit#(32) words = inCdb ? wordsOf(cur.cdbLen) : (cur.dir == 1 ? wordsOf(pack(cur.length)) : 0);
    if (k == words) begin
      if (inCdb) begin
        inCdb <= False;
        k <= 0;
      end
      else st <= BX3;
    end
    else begin
      mem.read(cellAddr(inCdb ? cur.cdb : cur.bufw) + 1 + toAddr(k));
      st <= BXWd;
    end
  endrule

  rule xWord (st == BXWd);
    let c <- mem.data;
    outQ.enq(tagged Word c.val);
    k <= k + 1;
    st <= BXRd;
  endrule

  rule xAnswer (st == BX3);
    inQ.deq;
    if (inQ.first matches tagged Answer .a) begin
      res <= a.result;
      n <= a.n;
      if (!a.ready) st <= BN1;
      else if (a.n > pack(cur.length)) fatal("scsi: the device gave more bytes than asked for");
      else if (a.n == 0) begin
        data <= cur.bufw;
        st <= BXDone;
      end
      else begin
        gbox.alloc(1 + toAddr(wordsOf(cur.bufLen)));
        st <= BX4;
      end
    end
    else fatal("scsi: the device did not answer the command");
  endrule

  // Data: a new string, the bytes received then the rest of the buffer
  rule xString (st == BX4);
    let a <- gbox.allocResult;
    Bit#(32) words = wordsOf(cur.bufLen);
    Bit#(32) pad = (words << 2) - cur.bufLen;
    mem.write(a, mkCell(tag_CDESC, pad << 27 | 3 << 24 | words));
    at <= a;
    data <= mkCell(tag_STRGx, absAddr(a));
    k <= 0;
    st <= BX5;
  endrule

  rule xCopyRead (st == BX5);
    if (k == wordsOf(cur.bufLen)) st <= BXDone;
    else begin
      mem.read(cellAddr(cur.bufw) + 1 + toAddr(k));
      st <= BX6;
    end
  endrule

  function Bit#(32) merged(Bit#(32) got, Bit#(32) old);
    Bit#(32) w = 0;
    for (Integer j = 0; j < 4; j = j + 1) begin
      Bit#(32) pos = (k << 2) + fromInteger(j);
      Bit#(8) b = pos < n ? got[31 - 8 * j : 24 - 8 * j]
                : (pos < cur.bufLen ? old[31 - 8 * j : 24 - 8 * j] : 0);
      w[31 - 8 * j : 24 - 8 * j] = b;
    end
    return w;
  endfunction

  // a word with bytes received in it (two rules: the device's word is
  // there only for these)
  rule xCopyReceived (st == BX6 && (k << 2) < n);
    let old <- mem.data;
    inQ.deq;
    Bit#(32) got = 0;
    if (inQ.first matches tagged Data .d) got = d;
    else fatal("scsi: the device's bytes are missing");
    mem.write(at + 1 + toAddr(k), intC(merged(got, old.val)));
    k <= k + 1;
    st <= BX5;
  endrule

  rule xCopyRest (st == BX6 && (k << 2) >= n);
    let old <- mem.data;
    mem.write(at + 1 + toAddr(k), intC(merged(0, old.val)));
    k <= k + 1;
    st <= BX5;
  endrule

  // finished: a command's poll, or the poll's unifications
  rule xDone (st == BXDone);
    if (ctx == CtxCommand) begin
      answer <= tagged Done { data: data, tl: intC(tl), id: intC(count), result: intC(res) };
      count <= count + 1;
      fromBench <= False;
      left <= nWaiting;
      done <= 0;
      st <= BP0;
    end
    else begin
      ui <= 0;
      st <= BPU;
    end
  endrule

  // ---- not finished yet ----------------------------------------------------
  rule notReady (st == BN1);
    if (ctx == CtxPoll) begin
      waiting.enq(cur);              // it keeps its place
      left <= left - 1;
      st <= BP0;
    end
    else begin
      gbox.newVar;
      k <= 0;
      st <= BN2;
    end
  endrule

  rule notReadyVar (st == BN2);
    let v <- gbox.newVarResult;
    let c = cur;
    if (k == 0) c.v0 = v;
    else if (k == 1) c.v1 = v;
    else c.v2 = v;
    cur <= c;
    if (k == 2) st <= BN3;
    else begin
      gbox.newVar;
      k <= k + 1;
    end
  endrule

  rule notReadyKept (st == BN3);
    if (nWaiting == 4) fatal("scsi: more than four commands wait for the device");
    waiting.enq(cur);
    nWaiting <= nWaiting + 1;
    resQ.enq(tagged Done { data: cur.v0, tl: cur.v1, id: intC(count), result: cur.v2 });
    count <= count + 1;
    st <= BIdle;
  endrule

  // ---- the poll ------------------------------------------------------------
  rule pollEnd (st == BP0 && left == 0);
    if (fromBench) pollQ.enq(done);
    else resQ.enq(answer);
    st <= BIdle;
  endrule

  rule pollTake (st == BP0 && left != 0);
    cur <= waiting.first;
    waiting.deq;
    ctx <= CtxPoll;
    st <= BX1;
  endrule

  rule pollUnify (st == BPU);
    Cell v = ui == 0 ? cur.v0 : (ui == 1 ? cur.v1 : cur.v2);
    Cell w = ui == 0 ? data : (ui == 1 ? intC(tl) : intC(res));
    dbox.unify(v, w);
    st <= BPUr;
  endrule

  function Action unified;
    action
      if (ui == 2) begin
        nWaiting <= nWaiting - 1;
        left <= left - 1;
        done <= done + 1;
        st <= BP0;
      end
      else begin
        ui <= ui + 1;
        st <= BPU;
      end
    endaction
  endfunction

  rule pollUnified (st == BPUr);
    let r <- dbox.unifyResult;
    case (r) matches
      tagged UOk: unified;
      tagged UWake .s: begin
        gbox.wake(s);
        st <= BPUw;
      end
      default: fatal("scsi: a waiting command's variable was not free");
    endcase
  endrule

  rule pollWoke (st == BPUw);
    gbox.done;
    unified;
  endrule

  method Action init = reqQ.enq(tagged Init);
  method Action initInfo = reqQ.enq(tagged InitInfo);
  method Action command(Cell obj, Cell v) = reqQ.enq(tagged Command { obj: obj, vec: v });
  method ActionValue#(ScsiResult) result;
    resQ.deq;
    return resQ.first;
  endmethod
  method Action poll = reqQ.enq(tagged Poll);
  method ActionValue#(Bit#(32)) polled;
    pollQ.deq;
    return pollQ.first;
  endmethod
  method ActionValue#(ScsiOut) devReq;
    outQ.deq;
    return outQ.first;
  endmethod
  method Action devResp(ScsiIn r) = inQ.enq(r);
  method Action restore(Bit#(8) which, Cell c) if (st == BIdle);
    let s = staged;
    case (which)
      4: count <= c.val;
      16: s.unit = unpack(c.val);
      17: s.lun = unpack(c.val);
      18: s.dir = unpack(c.val);
      19: s.length = unpack(c.val);
      20: s.cdb = c;
      21: s.cdbLen = c.val;
      22: s.bufw = c;
      23: s.bufLen = c.val;
      24: s.v0 = c;
      25: s.v1 = c;
      26: s.v2 = c;
      31: begin
        if (nWaiting == 4) fatal("scsi: more than four commands wait for the device");
        waiting.enq(staged);
        nWaiting <= nWaiting + 1;
      end
    endcase
    staged <= s;
  endmethod
endmodule

endpackage
