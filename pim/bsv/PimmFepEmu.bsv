// PimmFepEmu.bsv -- the FEP, in hardware: the other end of scsi_command.
//
// WHAT IT IS.  ref/pimm/fep.py put in Bluespec: a SCSI target of the
// processor type at unit 7 that takes packets with SEND on LUN 0 and gives
// them with RECEIVE on LUN 1, answers TEST UNIT READY, and serves the IPL's
// file requests (fep#read_open 201, fep#getb 210, fep#close 60, fep#abort
// 70; statuses fep#normal 1, fep#eod 2, fep#abnormal 5) from a card image
// (pim/tools/mkfepcard.py) read in 512-byte blocks.  It answers as fep.py
// answers, byte for byte, which bsv/run_fepemu.sh checks against fep.py
// itself on every command of ref/pimm/ref_scsi.py's parts.
//
// FROM PIMOS SOURCE (through fep.py, whose header cites each):
//   the CDBs (TEST UNIT READY 00h, RECEIVE 08h, SEND 0Ah; group 0, the
//   length in bytes 2-4, the LUN in byte 1 bits 7-5:
//   bios/scsi/scsi_common.kl1, scsi_processor.kl1); the packet (device
//   id, a continued flag, then the message: command or status, the
//   number of arguments, a length word each, -1 for an integer, the
//   arguments, strings padded to four bytes: the IPL image's
//   scsi_fep_module, docs/binary_reverse_engineering.md 1.4); the
//   command and status numbers (macro/pimos/pimos/pimos.vmac).
// OURS AS fep.py's (the same choices, kept exactly):
//   MAX_BUFFER 16000 (reported, for scsi_init's Info); a reply is queued
//   when a request's last packet arrives, and a RECEIVE with nothing
//   queued is not answered (FepNotReady: the caller holds the command and
//   offers it again, as pimm.py's scsi_poll does); an open of a file that
//   is not there gives status 5; getb's unit (getbUnit bytes, 1); a getb
//   at the end of the data gives status 2 every time; a reply longer than
//   the RECEIVE is cut into continued packets (the first piece the
//   header with flag 1 and as much of the rest as fits, the rest keeping
//   the original header); close gives status 1; abort gives nothing.
//   fep.py's test knobs are the configure() inputs: getbUnit, getbBytes
//   (fep.py's getb_bytes), lag (every RECEIVE refused once), maxBuffer.
//   fep.py's `limit` is not here.  Anything fep.py raises FepError (or
//   Python raises) on is answered FepRefused, and every command after it
//   too, until configure(): fep.py's caller has stopped by then.
// OURS AND NOT fep.py's (limits of a small machine; each is answered
//   FepRefused, why 8, where fep.py would go on; none is met by any
//   ref_scsi.py part, whose largest request is 120 bytes, at most two
//   files open, two replies queued: ref/pimm/record_fep.py prints them):
//   a request message of at most BodyMax (1024) bytes; FileSlots (4)
//   files open; ReplySlots (8) replies queued; one continued request
//   message in assembly at a time; a getb whose size is negative; a
//   RECEIVE shorter than 8 bytes that would have to be cut.
// AND, DIFFERENT FROM ref_scsi.py's open_file, NOT fep.py: a name is
//   matched byte for byte against the card's directory.  ref_scsi.py
//   decodes it by asm/psdpim.py's JIS table first, which raises on a code
//   outside the table (here: status 5) and maps every row but 23 to row
//   21's punctuation (here: only the exact bytes match).  The IPL's names
//   are all rows 21 and 23.
// AND ONE CHANGE ON THE ORACLE'S SIDE: ref_scsi.py's open_file raises
//   (UnboundLocalError in lockstep_file.file_words) for a name under
//   >sys>csp>PIMOS.DIR> that the archive does not hold, where fep.py's
//   contract is "open_file -> the file's bytes, or None".  The replay that
//   makes the expected answers (ref/pimm/record_fep.open_file_for) returns
//   None there, so fep.py answers status 5, as this emulator does.  Only
//   the "direct" tape's open of an extended name meets it.
//
// Structure (as in Bluespec's own cores: boxes behind request/response
// methods, a small sequencer): mkFepCardBytes is a byte/word reader over
// the block client with a one-block cache (one BRAM); mkFepBody is the
// request-message buffer (one BRAM); mkPimmFepEmu's StmtFSM takes one
// command at a time: classify, take a SEND's data, parse, serve, answer.
// The reply bytes are never stored: a queued reply is a descriptor
// (device, status, the card address and length of its data, how far a
// cut has given it), and a RECEIVE makes the bytes from it.

package PimmFepEmu;

import ClientServer::*;
import GetPut::*;
import FIFOF::*;
import Vector::*;
import BRAMCore::*;
import StmtFSM::*;
import PimmSdTypes::*;

// ---------------------------------------------------------------
// The command interface: what scsi_command hands a device.
// ---------------------------------------------------------------

// One scsi_command (pimm.py i_scsi_command: Unit, LUN, CDB, Length, Dir).
// After a request with dir 1 (out), the caller puts exactly `length`
// bytes on sendData (the buffer's first `length` bytes, as pimm.py
// scsi_do hands fep.py), whatever the answer will be.  After a FepDone
// answer to a dir 2 (in) command, `count` bytes follow on recvData.
typedef struct {
   Bit#(32)            unit;
   Bit#(32)            lun;
   UInt#(4)            cdbLen;    // the CDB string's length; fep.py takes 5 only
   Vector#(12, Bit#(8)) cdb;
   Bit#(2)             dir;       // 0 none, 1 out (SEND), 2 in (RECEIVE)
   UInt#(24)           length;
} FepCmd deriving (Bits, Eq, FShow);

typedef enum { FepDone, FepNotReady, FepRefused } FepAnswerKind deriving (Bits, Eq, FShow);

// FepDone: fep.py's (result, bytes): result 0 always, count the bytes
// received (0 but for RECEIVE).  FepNotReady: fep.py's None.
// FepRefused: fep.py raised; `why` says where (OURS, for a person).
typedef struct {
   FepAnswerKind kind;
   Bit#(8)       result;
   UInt#(24)     count;
   Bit#(8)       why;
} FepAnswer deriving (Bits, Eq, FShow);

// why codes
Bit#(8) whyUnitCdb   = 1;   // another unit, a CDB not 5 bytes
Bit#(8) whyLun       = 2;   // the CDB's LUN not the LUN, CDB byte 1 low bits
Bit#(8) whyCommand   = 3;   // no such command on this LUN/direction/length
Bit#(8) whyPacket    = 4;   // a packet under 8 bytes
Bit#(8) whyFlag      = 5;   // a packet flag not 0 or 1
Bit#(8) whyMessage   = 6;   // a message that does not unpack
Bit#(8) whyRequest   = 7;   // a request fep.py does not serve
Bit#(8) whyLimit     = 8;   // a limit of OURS (see the header)
Bit#(8) whyCard      = 9;   // the card: not mounted, or a read failed
Bit#(8) whyAfter     = 10;  // an earlier command was refused

typedef struct {
   UInt#(8)  getbUnit;    // fep.py getb_unit
   UInt#(24) getbBytes;   // fep.py getb_bytes, 0 for none
   Bool      lag;         // fep.py lag
   UInt#(24) maxBuffer;   // fep.py MAX_BUFFER (scsi_init reports it)
} FepConfig deriving (Bits, Eq, FShow);

FepConfig fepDefault = FepConfig { getbUnit: 1, getbBytes: 0, lag: False, maxBuffer: 16000 };

typedef enum { MountNotYet, MountOk, MountBad } FepMount deriving (Bits, Eq, FShow);

interface PimmFepEmu;
   interface Server#(FepCmd, FepAnswer) cmd;
   interface Put#(Bit#(8)) sendData;
   interface Get#(Bit#(8)) recvData;
   interface SdBlockClient card;
   // a fresh device (fep.Fep()) with these options; the card stays mounted
   method Action configure(FepConfig c);
   method UInt#(24) maxBuffer;
   method FepMount mounted;
endinterface

// fep.py's numbers
Bit#(8)  opTestUnitReady = 8'h00;
Bit#(8)  opReceive       = 8'h08;
Bit#(8)  opSend          = 8'h0a;
Int#(32) reqReadOpen = 201;
Int#(32) reqGetb     = 210;
Int#(32) reqClose    = 60;
Int#(32) reqAbort    = 70;
Int#(32) stNormal = 1;
Int#(32) stEod    = 2;
Int#(32) stAbnormal = 5;

typedef 1024 BodyMax;
typedef 4    FileSlots;
typedef 8    ReplySlots;
typedef 4    MaxArgs;     // fep.py serves nothing with more than 4 arguments

// ---------------------------------------------------------------
// mkFepCardBytes: bytes and big-endian words at a card byte address,
// over the block client, one block cached in a BRAM.
// ---------------------------------------------------------------
typedef struct { Bit#(32) addr; Bool word; } CardRead deriving (Bits, Eq, FShow);

interface FepCardBytes;
   interface Server#(CardRead, Maybe#(Bit#(32))) reads;   // Invalid: the card failed
   interface SdBlockClient card;
endinterface

module mkFepCardBytes(FepCardBytes);
   BRAM_PORT#(Bit#(9), Bit#(8)) blk <- mkBRAMCore1(512, False);
   FIFOF#(CardRead)          reqF    <- mkFIFOF;
   FIFOF#(Maybe#(Bit#(32)))  respF   <- mkFIFOF;
   FIFOF#(SdBlockReq)        bReqF   <- mkFIFOF;
   FIFOF#(SdBlockByte)       bRespF  <- mkFIFOF;
   Reg#(Maybe#(Bit#(32)))    cached  <- mkReg(tagged Invalid);
   Reg#(Bool)                filling <- mkReg(False);
   Reg#(Bit#(32))            fillBlk <- mkReg(0);
   Reg#(Bit#(9))             fillIx  <- mkReg(0);
   Reg#(Bool)                pend    <- mkReg(False);
   Reg#(UInt#(2))            k       <- mkReg(0);
   Reg#(Bit#(32))            acc     <- mkReg(0);

   Bit#(32) cur = reqF.first.addr + zeroExtend(pack(k));
   Bit#(32) curBlk = cur >> 9;
   Bool hit = cached == tagged Valid curBlk;

   rule rl_miss (reqF.notEmpty && !filling && !pend && !hit);
      bReqF.enq(SdBlockReq { block: curBlk });
      filling <= True;
      fillBlk <= curBlk;
      fillIx <= 0;
      cached <= tagged Invalid;
   endrule

   rule rl_fill (filling && !pend);
      let b = bRespF.first; bRespF.deq;
      if (b.err) begin
         // the block cannot be read: this read fails, whole
         filling <= False;
         respF.enq(tagged Invalid);
         reqF.deq;
         k <= 0; acc <= 0;
      end
      else begin
         blk.put(True, fillIx, b.data);
         fillIx <= fillIx + 1;
         if (b.last) begin
            filling <= False;
            cached <= tagged Valid fillBlk;
         end
      end
   endrule

   rule rl_read (reqF.notEmpty && !filling && !pend && hit);
      blk.put(False, cur[8:0], ?);
      pend <= True;
   endrule

   rule rl_take (pend && !filling);
      pend <= False;
      Bit#(32) a = acc << 8 | zeroExtend(blk.read);
      if (!reqF.first.word || k == 3) begin
         respF.enq(tagged Valid a);
         reqF.deq;
         k <= 0; acc <= 0;
      end
      else begin
         k <= k + 1; acc <= a;
      end
   endrule

   interface Server reads;
      interface Put request = toPut(reqF);
      interface Get response = toGet(respF);
   endinterface
   interface Client card;
      interface Get request = toGet(bReqF);
      interface Put response = toPut(bRespF);
   endinterface
endmodule

// ---------------------------------------------------------------
// mkFepBody: the request message being assembled (the bodies of a
// device's packets after their 8-byte headers, concatenated as fep.py's
// `partial` does), one BRAM; read back as bytes or big-endian words.
// ---------------------------------------------------------------
typedef Bit#(11) BodyIx;

interface FepBody;
   method Action write(BodyIx ix, Bit#(8) v);
   interface Server#(CardRead, Bit#(32)) reads;     // addr: a body offset
endinterface

module mkFepBody(FepBody);
   BRAM_PORT#(Bit#(10), Bit#(8)) mem <- mkBRAMCore1(valueOf(BodyMax), False);
   FIFOF#(CardRead) reqF  <- mkFIFOF;
   FIFOF#(Bit#(32)) respF <- mkFIFOF;
   Reg#(Bool)       pend  <- mkReg(False);
   Reg#(UInt#(2))   k     <- mkReg(0);
   Reg#(Bit#(32))   acc   <- mkReg(0);
   PulseWire        writing <- mkPulseWire;

   rule rl_read (reqF.notEmpty && !pend && !writing);
      Bit#(32) a = reqF.first.addr + zeroExtend(pack(k));
      mem.put(False, a[9:0], ?);
      pend <= True;
   endrule

   rule rl_take (pend);
      pend <= False;
      Bit#(32) a = acc << 8 | zeroExtend(mem.read);
      if (!reqF.first.word || k == 3) begin
         respF.enq(a);
         reqF.deq;
         k <= 0; acc <= 0;
      end
      else begin
         k <= k + 1; acc <= a;
      end
   endrule

   method Action write(BodyIx ix, Bit#(8) v);
      mem.put(True, ix[9:0], v);
      writing.send;
   endmethod
   interface Server reads;
      interface Put request = toPut(reqF);
      interface Get response = toGet(respF);
   endinterface
endmodule

// ---------------------------------------------------------------
// The device's state
// ---------------------------------------------------------------
typedef struct {
   Bool     valid;
   Bit#(32) dev;
   Bit#(32) start;      // the file's first block
   UInt#(32) len;
   UInt#(32) pos;
} FileSlot deriving (Bits, Eq, FShow);

// A queued reply: [status] or [status, data]; the data is `dlen` bytes
// of the card from byte address `addr`.
typedef struct {
   Bit#(32)  dev;
   Int#(32)  status;
   Bool      hasData;
   Bit#(32)  addr;
   UInt#(32) dlen;
} ReplyDesc deriving (Bits, Eq, FShow);

typedef struct {
   Bool      isInt;
   Bit#(32)  v;          // the integer, or a string's body offset
   UInt#(32) len;        // a string's length
} MsgArg deriving (Bits, Eq, FShow);

function Bit#(8) byteOf(Bit#(32) w, UInt#(32) i);   // i = 0 the high byte
   return case (i) 0: w[31:24]; 1: w[23:16]; 2: w[15:8]; default: w[7:0]; endcase;
endfunction

function UInt#(32) pad4(UInt#(32) n) = unpack((~pack(n) + 1) & 3);

// the length of a reply packet as fep.py packs it
function UInt#(32) replyLen(ReplyDesc d) =
   d.hasData ? 20 + d.dlen + pad4(d.dlen) : 16;

// ---------------------------------------------------------------
// mkPimmFepEmu
// ---------------------------------------------------------------
(* synthesize *)
module mkPimmFepEmu(PimmFepEmu);
   FepCardBytes cardB <- mkFepCardBytes;
   FepBody      body  <- mkFepBody;

   FIFOF#(FepCmd)    cmdF  <- mkFIFOF;
   FIFOF#(FepAnswer) ansF  <- mkFIFOF;
   FIFOF#(Bit#(8))   sendF <- mkFIFOF;
   FIFOF#(Bit#(8))   recvF <- mkFIFOF;
   FIFOF#(FepConfig) cfgF  <- mkFIFOF;

   Reg#(FepConfig) cfg <- mkReg(fepDefault);
   Reg#(FepMount)  mnt <- mkReg(MountNotYet);
   Reg#(UInt#(32)) dirCount <- mkReg(0);
   Reg#(Bit#(32))  dirFirst <- mkReg(0);

   // fep.Fep's state
   Reg#(Bool)      dead     <- mkReg(False);
   Vector#(FileSlots, Reg#(FileSlot)) files <- replicateM(mkReg(unpack(0)));
   // unguarded, every use checks: a full queue must refuse (queue()), not stall
   FIFOF#(ReplyDesc) replies <- mkUGSizedFIFOF(valueOf(ReplySlots));
   Reg#(UInt#(32)) skip     <- mkReg(8);     // where the head reply goes on after a cut
   Reg#(Bool)      lagged   <- mkReg(False);
   Reg#(Bool)      partValid <- mkReg(False);
   Reg#(Bit#(32))  partDev  <- mkReg(0);
   Reg#(UInt#(32)) partLen  <- mkReg(0);

   // the command in hand
   Reg#(FepCmd)    cur   <- mkRegU;
   Reg#(UInt#(32)) i     <- mkReg(0);
   Reg#(Bit#(32))  pdev  <- mkReg(0);
   Reg#(Bit#(32))  pflag <- mkReg(0);
   Reg#(UInt#(32)) base  <- mkReg(0);
   Reg#(Bool)      over  <- mkReg(False);
   Reg#(UInt#(32)) bodyLen <- mkReg(0);
   Reg#(Bit#(8))   perr  <- mkReg(0);
   Reg#(Bool)      cardErr <- mkReg(False);
   // the message
   Reg#(Int#(32))  mcmd  <- mkReg(0);
   Reg#(Int#(32))  nargs <- mkReg(0);
   Vector#(MaxArgs, Reg#(Int#(32))) lens <- replicateM(mkReg(0));
   Vector#(MaxArgs, Reg#(MsgArg))   args <- replicateM(mkReg(unpack(0)));
   Reg#(UInt#(32)) at    <- mkReg(0);
   Reg#(UInt#(32)) j     <- mkReg(0);
   // the lookup
   Reg#(UInt#(32)) e     <- mkReg(0);
   Reg#(Bool)      found <- mkReg(False);
   Reg#(Bool)      same  <- mkReg(False);
   Reg#(UInt#(32)) nl    <- mkReg(0);
   Reg#(Bit#(32))  fstart <- mkReg(0);
   Reg#(UInt#(32)) flen  <- mkReg(0);
   Reg#(Bit#(32))  w     <- mkReg(0);     // a card word read
   Reg#(Bit#(32))  bw    <- mkReg(0);     // a body word read
   // a RECEIVE
   Reg#(UInt#(32)) cnt   <- mkReg(0);
   Reg#(Bool)      cont  <- mkReg(False);
   Reg#(UInt#(32)) kk    <- mkReg(0);

   function Bit#(32) cdbLenOf(FepCmd c) = {8'h0, c.cdb[2], c.cdb[3], c.cdb[4]};
   Bit#(8)  op    = cur.cdb[0];
   Bit#(32) clun  = zeroExtend(cur.cdb[1] >> 5);
   UInt#(32) curLen = zeroExtend(cur.length);
   Bool cdbLenOk = unpack(cdbLenOf(cur)) == curLen;

   function Maybe#(UInt#(TLog#(FileSlots))) slotOf(Bit#(32) dev);
      Maybe#(UInt#(TLog#(FileSlots))) r = tagged Invalid;
      for (Integer s = valueOf(FileSlots) - 1; s >= 0; s = s - 1)
         if (files[s].valid && files[s].dev == dev) r = tagged Valid fromInteger(s);
      return r;
   endfunction
   function Maybe#(UInt#(TLog#(FileSlots))) freeSlot();
      Maybe#(UInt#(TLog#(FileSlots))) r = tagged Invalid;
      for (Integer s = valueOf(FileSlots) - 1; s >= 0; s = s - 1)
         if (!files[s].valid) r = tagged Valid fromInteger(s);
      return r;
   endfunction

   function Action answer(FepAnswerKind k, UInt#(24) n, Bit#(8) y) =
      ansF.enq(FepAnswer { kind: k, result: 0, count: n, why: y });
   function Action refuse(Bit#(8) y) = action
      ansF.enq(FepAnswer { kind: FepRefused, result: 0, count: 0, why: y });
      dead <= True;
   endaction;

   function Stmt cardRd(Bit#(32) a, Bool word) = seq
      cardB.reads.request.put(CardRead { addr: a, word: word });
      action
         let r <- cardB.reads.response.get;
         case (r) matches
            tagged Valid .x: w <= x;
            default: begin w <= 0; cardErr <= True; end
         endcase
      endaction
   endseq;
   function Stmt bodyRd(UInt#(32) a, Bool word) = seq
      body.reads.request.put(CardRead { addr: pack(a), word: word });
      action let r <- body.reads.response.get; bw <= r; endaction
   endseq;

   function Action queue(ReplyDesc d) = action
      if (replies.notFull) replies.enq(d); else perr <= whyLimit;
   endaction;

   // the byte k of a RECEIVE's piece, but for the card's data
   function Bit#(8) pieceByte(ReplyDesc d, UInt#(32) k);
      Bit#(8) r = 0;
      if (k < 4) r = byteOf(d.dev, k);
      else if (k < 8) r = (k == 7 && cont) ? 1 : 0;
      else begin
         UInt#(32) p = skip + k - 8;
         if (p >= 8 && p < 12) r = byteOf(pack(d.status), p - 8);
         else if (p >= 12 && p < 16) r = (p == 15 && d.hasData) ? 1 : 0;
         else if (p >= 16 && p < 20) r = byteOf(pack(d.dlen), p - 16);
      end
      return r;
   endfunction
   function Bool pieceIsData(ReplyDesc d, UInt#(32) k);
      UInt#(32) p = skip + k - 8;
      return k >= 8 && d.hasData && p >= 20 && p < 20 + d.dlen;
   endfunction

   // ---- mount: the card's header ---------------------------------
   Stmt mount = seq
      cardErr <= False;
      cardRd(0, True);
      if (w != 32'h50494d46) mnt <= MountBad;           // "PIMF"
      cardRd(4, True);
      if (w != 32'h45504331) mnt <= MountBad;           // "EPC1"
      cardRd(8, True);
      dirCount <= unpack(w);
      cardRd(12, True);
      dirFirst <= w;
      cardRd(20, True);
      action
         if (w != 256 || cardErr || mnt == MountBad) mnt <= MountBad;
         else mnt <= MountOk;
      endaction
   endseq;

   // ---- the message: fep.unpack_message -------------------------
   Stmt parse = seq
      if (bodyLen < 8) perr <= whyMessage;
      else seq
         bodyRd(0, True);
         mcmd <= unpack(bw);
         bodyRd(4, True);
         nargs <= unpack(bw);
         // more than four arguments: fep.py unpacks them and then serves
         // nothing (request() raises); a refusal either way
         if (nargs < 0) perr <= whyMessage;
         else if (nargs > fromInteger(valueOf(MaxArgs))) perr <= whyRequest;
         else if (8 + 4 * unpack(pack(nargs)) > bodyLen) perr <= whyMessage;
         else seq
            j <= 0;
            while (j < unpack(pack(nargs))) seq
               bodyRd(8 + 4 * j, True);
               action lens[j] <= unpack(bw); j <= j + 1; endaction
            endseq
            action at <= 8 + 4 * unpack(pack(nargs)); j <= 0; endaction
            while (j < unpack(pack(nargs)) && perr == 0) seq
               if (lens[j] == -1) seq
                  if (at + 4 > bodyLen) perr <= whyMessage;
                  else seq
                     bodyRd(at, True);
                     action
                        args[j] <= MsgArg { isInt: True, v: bw, len: 0 };
                        at <= at + 4;
                     endaction
                  endseq
               endseq
               else if (lens[j] < -1 || lens[j] > fromInteger(valueOf(BodyMax))) perr <= whyMessage;
               else action
                  UInt#(32) ln = unpack(pack(lens[j]));
                  args[j] <= MsgArg { isInt: False, v: pack(at), len: ln };
                  at <= at + ln + pad4(ln);
               endaction
               j <= j + 1;
            endseq
            if (perr == 0 && at != bodyLen) perr <= whyMessage;
         endseq
      endseq
   endseq;

   // ---- the card's directory: the entry named by args[3] ---------
   Stmt lookup = seq
      action e <= 0; found <= False; endaction
      while (e < dirCount && !found && !cardErr) seq
         cardRd(dirFirst * 512 + pack(e) * 256, True);
         nl <= unpack(w);
         if (nl == args[3].len) seq
            action j <= 0; same <= True; endaction
            while (j < nl && same && !cardErr) seq
               cardRd(dirFirst * 512 + pack(e) * 256 + 16 + pack(j), False);
               bodyRd(unpack(args[3].v) + j, False);
               action if (w != bw) same <= False; j <= j + 1; endaction
            endseq
            if (same && !cardErr) seq
               cardRd(dirFirst * 512 + pack(e) * 256 + 4, True);
               fstart <= w;
               cardRd(dirFirst * 512 + pack(e) * 256 + 8, True);
               action flen <= unpack(w); found <= True; endaction
            endseq
         endseq
         e <= e + 1;
      endseq
   endseq;

   // ---- a request: fep.Fep.request -------------------------------
   Stmt serve = seq
      if (mcmd == reqReadOpen && nargs == 4 && !isValid(slotOf(pdev))) seq
         if (args[3].isInt || pack(args[3].len)[0] == 1) perr <= whyRequest;   // open_file raises
         else seq
            lookup;
            if (cardErr) perr <= whyCard;
            else if (!found) queue(ReplyDesc { dev: pdev, status: stAbnormal, hasData: False,
                                               addr: 0, dlen: 0 });
            else action
               case (freeSlot()) matches
                  tagged Valid .s: begin
                     files[s] <= FileSlot { valid: True, dev: pdev, start: fstart, len: flen, pos: 0 };
                     queue(ReplyDesc { dev: pdev, status: stNormal, hasData: False, addr: 0, dlen: 0 });
                  end
                  default: perr <= whyLimit;
               endcase
            endaction
         endseq
      endseq
      else if (mcmd == reqGetb && nargs == 1 && isValid(slotOf(pdev))) action
         let s = validValue(slotOf(pdev));
         let f = files[s];
         Int#(32) n0 = unpack(args[0].v);
         Int#(48) unit = unpack(zeroExtend(pack(cfg.getbUnit)));
         Int#(48) size = cfg.getbBytes != 0 ? unpack(zeroExtend(pack(cfg.getbBytes)))
                         : signExtend(n0) * unit;
         UInt#(32) remain = f.len - f.pos;
         UInt#(32) chunk = (size >= unpack(zeroExtend(pack(remain)))) ? remain : unpack(truncate(pack(size)));
         if (cfg.getbBytes == 0 && !args[0].isInt) perr <= whyRequest;
         else if (size < 0) perr <= whyLimit;
         else if (chunk == 0)
            queue(ReplyDesc { dev: pdev, status: stEod, hasData: False, addr: 0, dlen: 0 });
         else begin
            queue(ReplyDesc { dev: pdev, status: stNormal, hasData: True,
                              addr: f.start * 512 + pack(f.pos), dlen: chunk });
            files[s] <= FileSlot { valid: True, dev: f.dev, start: f.start, len: f.len,
                                   pos: f.pos + chunk };
         end
      endaction
      else if (mcmd == reqClose && nargs == 0 && isValid(slotOf(pdev))) action
         files[validValue(slotOf(pdev))] <= unpack(0);
         queue(ReplyDesc { dev: pdev, status: stNormal, hasData: False, addr: 0, dlen: 0 });
      endaction
      else if (mcmd == reqAbort && nargs == 0) noAction;
      else perr <= whyRequest;
   endseq;

   // ---- SEND: fep.Fep.packet --------------------------------------
   Stmt doSend = seq
      if (curLen < 8) refuse(whyPacket);
      else if (over || (partValid && pdev != partDev)) refuse(whyLimit);
      else if (pflag == 1) action
         partValid <= True; partDev <= pdev; partLen <= base + curLen - 8;
         answer(FepDone, 0, 0);
      endaction
      else if (pflag != 0) refuse(whyFlag);
      else seq
         action bodyLen <= base + curLen - 8; partValid <= False; perr <= 0; endaction
         parse;
         if (perr == 0) serve;
         if (perr != 0) refuse(perr); else answer(FepDone, 0, 0);
      endseq
   endseq;

   // ---- RECEIVE ----------------------------------------------------
   Stmt doReceive = seq
      if (!replies.notEmpty) answer(FepNotReady, 0, 0);
      else if (cfg.lag && !lagged) action lagged <= True; answer(FepNotReady, 0, 0); endaction
      else seq
         action
            lagged <= False;
            UInt#(32) size = 8 + replyLen(replies.first) - skip;
            if (size > curLen) begin
               cnt <= curLen; cont <= True;
            end
            else begin
               cnt <= size; cont <= False;
            end
            kk <= 0;
         endaction
         if (cont && cnt < 8) refuse(whyLimit);
         else seq
            answer(FepDone, truncate(cnt), 0);
            while (kk < cnt) seq
               if (pieceIsData(replies.first, kk)) seq
                  cardRd(replies.first.addr + pack(skip + kk - 8 - 20), False);
                  action recvF.enq(w[7:0]); kk <= kk + 1; endaction
               endseq
               else action recvF.enq(pieceByte(replies.first, kk)); kk <= kk + 1; endaction
            endseq
            action
               if (cardErr) dead <= True;
               if (cont) skip <= skip + cnt - 8;
               else begin replies.deq; skip <= 8; end
            endaction
         endseq
      endseq
   endseq;

   // ---- one command -------------------------------------------------
   Stmt oneCommand = seq
      action
         let c = cmdF.first; cmdF.deq;
         cur <= c; i <= 0; pdev <= 0; pflag <= 0; over <= False; cardErr <= False;
         base <= partValid ? partLen : 0;
      endaction
      // a SEND's data is always taken, whatever the answer
      if (cur.dir == 1)
         while (i < curLen) action
            let b = sendF.first; sendF.deq;
            if (i < 4) pdev <= pdev << 8 | zeroExtend(b);
            else if (i < 8) pflag <= pflag << 8 | zeroExtend(b);
            else begin
               UInt#(32) o = base + i - 8;
               if (o < fromInteger(valueOf(BodyMax))) body.write(truncate(pack(o)), b);
               else over <= True;
            end
            i <= i + 1;
         endaction
      if (dead) refuse(whyAfter);
      else if (mnt != MountOk) refuse(whyCard);
      else if (cur.unit != 7 || cur.cdbLen != 5) refuse(whyUnitCdb);
      else if (clun != cur.lun || cur.cdb[1][4:0] != 0) refuse(whyLun);
      else if (op == opTestUnitReady && cur.dir == 0 && curLen == 0 && cdbLenOk)
         answer(FepDone, 0, 0);
      else if (op == opSend && cur.lun == 0 && cur.dir == 1 && cdbLenOk)
         doSend;
      else if (op == opReceive && cur.lun == 1 && cur.dir == 2 && cdbLenOk)
         doReceive;
      else refuse(whyCommand);
   endseq;

   Stmt main = seq
      mount;
      while (True) seq
         await(cfgF.notEmpty || cmdF.notEmpty);
         if (cfgF.notEmpty) action
            cfg <= cfgF.first; cfgF.deq;
            dead <= False;
            for (Integer s = 0; s < valueOf(FileSlots); s = s + 1) files[s] <= unpack(0);
            replies.clear;
            skip <= 8; lagged <= False; partValid <= False; partLen <= 0;
         endaction
         else oneCommand;
      endseq
   endseq;

   FSM fsm <- mkFSM(main);
   Reg#(Bool) started <- mkReg(False);
   rule rl_start (!started);
      fsm.start;
      started <= True;
   endrule

   interface Server cmd;
      interface Put request = toPut(cmdF);
      interface Get response = toGet(ansF);
   endinterface
   interface Put sendData = toPut(sendF);
   interface Get recvData = toGet(recvF);
   interface SdBlockClient card = cardB.card;
   method Action configure(FepConfig c) = cfgF.enq(c);
   method UInt#(24) maxBuffer = cfg.maxBuffer;
   method FepMount mounted = mnt;
endmodule

endpackage
