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
// AND WHAT fep.py HAS FOR PIMOS's START TO THE SHELL'S PROMPT (fep.py on
// master, 2026-11-24, docs/fep_services.md 6 and 7):
//   INQUIRY (12h) to unit 7: 03 00 07 00 00; TEST UNIT READY to an absent
//   unit 0-5: Result noDevice (800h), decided here as fep.py decides it in
//   Fep.command, before the unit and LUN checks; append_open 203: [1]
//   (AppendSlots; no log is kept, fep.py keeps one in memory only);
//   create_timer 310: [1]; get_date_time 304: [1, 33742, T], T =
//   (clock / 16) mod 86,400,000, the clock the setTime input last gave
//   (fep.py's Fep.ticks, which the reference model sets from the
//   machine's timer before each command); 60 on a timer: [1];
//   fep_attributes 240: fep.ATTRIBUTES, the message held on the card
//   (mkfepcard.py writes fep.py's own); create_string_io 601 of the three
//   programs a login uses (the name compared as fep.unjis decodes it);
//   io 620 on them (fep.Fep.string_io: the replier's [1, ""] and [1,
//   "\0\0"], the local server's [1, ""] and its io(1) HELD, tcpip [5], the
//   user device's [1, ">sys>user>" ++ the name it is given]); the window
//   create 104 and calls 126 127 130 132 141 142 143 111 112: [1]; getl 110
//   HELD; 60 on a string-I/O device or a window: [1]; 70 on a device
//   with a held request: that request answered [6]; 112 on a read file:
//   [1]; and fep.Fep.idle(), the EVENT (below).
//   AND (fep.py after the merger change and the typed shutdown,
//   2026-11-24, docs/fep_services.md 2, docs/binary_reverse_engineering.md
//   1.4 "A command typed"): 601 of fep.STD_WINDOW, the string-I/O window
//   "pimos_standard_io_window" that shutdown_body's question opens; io 620
//   on it: 104, 130, 141 and 111 (putb, a string) [1, ""], 110 (getl)
//   HELD, answered by the event as a window's getl; 60 on the
//   append-opened file (the syslog's, at PIMOS's end): [1]; {-1, 80}
//   (terminate): no reply (fep.py notes Fep.terminated; nothing is kept
//   here).  Nothing else fep.py answers is missing here: any other io on
//   the window, or 80 on another device, is refused as fep.py raises.  The files of pimos: are
//   whatever the card holds under those names (mkfepcard.py --held puts
//   the held object directory there, as longrun_ipl.kernel_file serves
//   it); a name not on the card is answered 5 (autoload.tbl, me:, the
//   home directory), as fep.py's open_file None is.
//   AND (2026-11-25, R7, the primer's sample1): a home file
//   (longrun_ipl.HOME_FILES, fep.FileData) is on the card under its
//   path, with its pathname and attributes in the directory entry
//   (bytes 240-255, mkfepcard.py); 221 (pathname) and 222 (attributes)
//   on a read file that has them answer [1, the card's string], as
//   fep.py answers them after read_open in its order of tests; on a file
//   that has none (every pimos: file) they are refused, as fep.py raises.
//
// HELD REQUESTS AND THE EVENT (how the core's SCSI port sees them).  A
// request fep.py holds (the login server's io(1), a window's getl) gets
// no reply when it arrives: the emulator notes the device and the kind
// (HeldSlots), and every RECEIVE with nothing else queued is answered
// FepNotReady, so the core's RECEIVE stays outstanding: PimmScsiBox keeps
// it in its waiting list and gives it again at each poll, exactly as
// pimm.py's scsi_waiting / scsi_poll do with fep.py's None.  An answer
// comes only from an EVENT: `idle`, the bench's question when the machine
// has run dry and no waiting command moves (longrun_ipl.go calls
// Fep.idle() there).  The emulator takes the next entry of the card's
// script (the kind, login 1 or getl 2, and the reply's string: mkfepcard
// writes fep.Fep().script, so a new scripted line in fep.py is a new
// card, not new hardware); if a device holds a request of that kind (the
// lowest device id, as fep.py's sorted(held)), the reply [1, string] is
// queued and the script moves on; the answer to `idle` is 1 then, 0
// otherwise.  The next poll's RECEIVE takes the reply.  70 on a held
// device ends the hold with [6].  A close (60) does not end a hold
// (fep.py keeps held[dev] then too).
//
// ADDING THE NEXT COMMAND fep.py ANSWERS (the recipe):
//   1. a message (fep.Fep.request): one `else if (mcmd == ...)` branch in
//      `serve`, IN fep.py's ORDER OF TESTS (the device sets overlap: one
//      device can be a file, a timer and a window at once), queueing a
//      ReplyDesc.  The kinds: RStatus [status]; RString [status, string]
//      with the string from the card (a file's data, the script), zeros,
//      or the home buffer; RDate [status, date, time]; RRaw a whole
//      message from the card (a constant answer: put fep.py's constant on
//      the card in mkfepcard.fep_tables and its address in the header,
//      as fep.ATTRIBUTES).  A new event kind (fep.Fep.idle) needs only
//      a code in mkfepcard.SCRIPT_KINDS and the hold that waits for it.
//      A SCSI command (fep.Fep.command): one `else if (op == ...)` in
//      `oneCommand`, in fep.py's order.  A constant next to the others;
//      new state cleared in `main`'s configure.
//   2. one line or section in record_fep.direct_kernel_sections (the
//      answer and the FepError next to it), then
//      `python3 ref/pimm/record_fep.py --part direct_kernel`; and, if the
//      kernel now reaches it, `--kernel PKL --type shutdown --type yes`
//      again for the kernel tape.
//   3. bsv/run_fepemu.sh; one injection into the new branch, its observed
//      failures in PimmFepEmuTb.bsv's header.
//   direct_kernel's error sections hold putb (111) and getb on a device
//   that only appends, as tripwires: when fep.py answers one,
//   run_fepemu.sh fails on that line until the emulator follows; move
//   that line out of the error sections then.  (The close was such a
//   tripwire until fep.py answered it, 2026-11-24: run_fepemu.sh failed
//   at direct_kernel command 49 until this module followed.)
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
//   is not there gives status 5; getb's unit (getbUnit bytes, 1; the
//   kernel's tape 2); a getb at the end of the data gives status 2 every
//   time; a reply longer than the RECEIVE is cut into continued packets
//   (the first piece the header with flag 1 and as much of the rest as
//   fits, the rest keeping the original header); close gives status 1;
//   abort with nothing held gives nothing; the date 33742 and the time
//   from the clock; the attributes and the script (on the card, as fep.py
//   has them).  fep.py's test knobs are the configure() inputs: getbUnit,
//   getbBytes (fep.py's getb_bytes), lag (every RECEIVE refused once),
//   maxBuffer.  fep.py's `limit` is not here.  Anything fep.py raises
//   FepError (or Python raises) on is answered FepRefused, and every
//   command after it too, until configure(): fep.py's caller has stopped
//   by then.
// OURS AND NOT fep.py's (limits of a small machine; each is answered
//   FepRefused, why 8, where fep.py would go on; record_fep.py --kernel
//   prints what the kernel's start uses, to PIMOS END after a typed
//   shutdown: a request of 88 bytes, 2 files, 1 appending, 1 timer, 3
//   string-I/O, 1 window, 2 held, 4 replies queued):
//   a request message of at most BodyMax (1024) bytes; FileSlots (4)
//   files open; ReplySlots (8) replies queued; AppendSlots (2) devices
//   appending; DevSlots (8) devices that are timers, string-I/O programs
//   or windows; HeldSlots (4) held requests; one continued request
//   message in assembly at a time; a getb whose size is negative; a
//   RECEIVE shorter than 8 bytes that would have to be cut; the user
//   device's name at most HomeMax (32) bytes, and one such reply queued
//   at a time; a card with no attributes or script answers 240 and the
//   event with why 9.
// AND, DIFFERENT FROM ref_scsi.py's open_file, NOT fep.py: a name is
//   matched byte for byte against the card's directory.  ref_scsi.py
//   decodes it by asm/psdpim.py's JIS table first, which raises on a code
//   outside the table (here: status 5) and maps every row but 23 to row
//   21's punctuation (here: only the exact bytes match).  The IPL's names
//   are all rows 21 and 23.  longrun_ipl.kernel_file raises on a name
//   outside pimos:, me: and the home directory; here such a name is
//   answered 5 (none is asked on the kernel's tape).
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
// command or event at a time: classify, take a SEND's data, parse, serve,
// answer.  The reply bytes are never stored: a queued reply is a
// descriptor (device, status, kind, the card address and length of its
// data, how far a cut has given it), and a RECEIVE makes the bytes from it.

package PimmFepEmu;

import ClientServer::*;
import GetPut::*;
import FIFOF::*;
import Vector::*;
import List::*;
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

// FepDone: fep.py's (result, bytes): result 0 but for an absent unit's
// TEST UNIT READY (noDevice), count the bytes received (0 but for
// RECEIVE and INQUIRY).  To `idle`: FepDone with result 1 if a reply was
// queued, 0 if not (fep.Fep.idle's True / False), count 0.
// FepNotReady: fep.py's None.
// FepRefused: fep.py raised; `why` says where (OURS, for a person).
typedef struct {
   FepAnswerKind kind;
   Bit#(32)      result;    // scsi_command's Result: 0, or noDevice
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
Bit#(8) whyCard      = 9;   // the card: not mounted, a read failed, no attributes/script
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
   // a fresh device (fep.Fep()) with these options; the card stays
   // mounted, the clock goes back to 0 (a fresh Fep's ticks)
   method Action configure(FepConfig c);
   // the event (fep.Fep.idle): answered on cmd.response, in turn with
   // the commands
   method Action idle;
   // the FEP's clock, 1/16 msec, 48 bits (fep.Fep.ticks; pimm.py's
   // timer()): get_date_time's time of day follows it.  Given before the
   // command it is for; a board would drive it from a counter
   method Action setTime(Bit#(48) t);
   method UInt#(24) maxBuffer;
   method FepMount mounted;
endinterface

// fep.py's numbers
Bit#(8)  opTestUnitReady = 8'h00;
Bit#(8)  opReceive       = 8'h08;
Bit#(8)  opSend          = 8'h0a;
Bit#(8)  opInquiry       = 8'h12;
Bit#(32) noDevice        = 32'h800;   // fep.NO_DEVICE: completion code 8, OURS as fep.py's
Bit#(32) absentLast      = 5;         // fep.Fep.ABSENT: units 0..5
Int#(32) reqReadOpen   = 201;
Int#(32) reqAppendOpen = 203;
Int#(32) reqGetb       = 210;
Int#(32) reqPathname   = 221;     // fep#pathname (pimos.vmac:77)
Int#(32) reqFileAttributes = 222; // fep#attributes (pimos.vmac:138)
Int#(32) reqClose      = 60;
Int#(32) reqAbort      = 70;
Int#(32) reqTerminate  = 80;
Int#(32) reqCreateTimer = 310;
Int#(32) reqGetDateTime = 304;
Int#(32) reqAttributes = 240;
Int#(32) reqCreateStrIo = 601;
Int#(32) reqIo         = 620;
Int#(32) reqCreateWindow = 104;
Int#(32) reqGetl       = 110;
Int#(32) reqPutb       = 111;
Int#(32) reqFlush      = 112;
Int#(32) stNormal = 1;
Int#(32) stEod    = 2;
Int#(32) stAbnormal = 5;
Int#(32) stAborted = 6;
Bit#(32) fepDate  = 33742;            // fep.DATE
Bit#(48) msPerDay = 86400000;

// fep.WINDOW_ANSWERED: reshape_by_mouse (2026-11-24, the listener's
// window), reshape, set_title, set_font, activate, deactivate, show,
// putb, flush
function Bool windowAnswered(Int#(32) c) =
   c == 126 || c == 127 || c == 130 || c == 132 || c == 141 || c == 142 || c == 143 || c == reqPutb
   || c == reqFlush;

typedef 1024 BodyMax;
typedef 4    FileSlots;
typedef 8    ReplySlots;
typedef 2    AppendSlots; // devices appending at once (OURS; the kernel opens one, its syslog)
typedef 8    DevSlots;    // timers, string-I/O devices, windows (OURS; the kernel: 5 at most)
typedef 4    HeldSlots;   // held requests (OURS; the kernel: 2)
typedef 4    MaxArgs;     // arguments kept; more are parsed, not kept (no answer reads them)
typedef 32   HomeMax;     // bytes of the user device's name (OURS)

// ---------------------------------------------------------------
// Text: fep.unjis, one character at a time, and the names compared.
// ---------------------------------------------------------------
// a 16-bit JIS character as fep.unjis reads it: row 23 the low byte,
// row 21 the punctuation of fep._PUNCT; anything else is '<hex>' there,
// which no name here holds (Invalid)
function Maybe#(Bit#(8)) unjisChar(Bit#(8) hi, Bit#(8) lo);
   Maybe#(Bit#(8)) r = tagged Invalid;
   if (hi == 8'h23) r = tagged Valid lo;
   else if (hi == 8'h21)
      case (lo)
         8'h21: r = tagged Valid 32;    // ' '
         8'h24: r = tagged Valid 44;    // ','
         8'h25: r = tagged Valid 46;    // '.'
         8'h27: r = tagged Valid 58;    // ':'
         8'h32: r = tagged Valid 95;    // '_'
         8'h3f: r = tagged Valid 47;    // '/'
         8'h5d: r = tagged Valid 45;    // '-'
         8'h63: r = tagged Valid 60;    // '<'
         8'h64: r = tagged Valid 62;    // '>'
         8'h2a: r = tagged Valid 33;    // '!'
         8'h29: r = tagged Valid 63;    // '?'
         8'h76: r = tagged Valid 42;    // '*'
         // fep._PUNCT's four since 2026-11-24 (a typed line's); no name
         // compared here holds them, so they cannot be seen on a tape
         8'h49: r = tagged Valid 34;    // '"'
         8'h4a: r = tagged Valid 40;    // '('
         8'h4b: r = tagged Valid 41;    // ')'
         8'h61: r = tagged Valid 61;    // '='
      endcase
   return r;
endfunction

function Bit#(8) charAt(String s, UInt#(32) i);
   List#(Char) cs = stringToCharList(s);
   Bit#(8) r = 0;
   for (Integer k = 0; k < List::length(cs); k = k + 1)
      if (i == fromInteger(k)) r = fromInteger(charToInteger(List::head(List::drop(k, cs))));
   return r;
endfunction

// the names compared (fep.REPLIER, SERVER, USER_DEVICE; the server's
// kinds "local" and "tcpip"; fep.STD_WINDOW, the string-I/O window of
// shutdown_body's question)
typedef 6 NNames;
function String nameOf(Integer n) = case (n)
   0: "pimos_remote_login_replier";
   1: "pimos_remote_login_server";
   2: "simpos_user_device";
   3: "local";
   4: "tcpip";
   default: "pimos_standard_io_window";
endcase;
function UInt#(32) nameLen(Integer n) = fromInteger(stringLength(nameOf(n)));

// jis(">sys>user>"), the user's home ahead of the name (fep.py
// string_io; login_p.kl1:63)
function Bit#(8) homePrefix(UInt#(32) i);
   String s = ">sys>user>";
   Bit#(8) c = charAt(s, i >> 1);
   Bool punct = c == 62;
   return (pack(i)[0] == 0) ? (punct ? 8'h21 : 8'h23) : (punct ? 8'h64 : c);
endfunction

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
   Bit#(32) pblk;       // 221's answer on the card (0: none), and its length
   UInt#(32) plen;
   Bit#(32) ablk;       // 222's, likewise
   UInt#(32) alen;
} FileSlot deriving (Bits, Eq, FShow);

// fep.Fep's device sets for one device id, kept apart as fep.py keeps
// them (timers, strio, windows, listening): a slot is in use while any
// is set
typedef enum { SNone, SReplier, SServer, SUserDevice, SStdWindow } StrIo deriving (Bits, Eq, FShow);
typedef struct {
   Bit#(32) dev;
   Bool     timer;
   StrIo    strio;
   Bool     window;
   Bool     listening;
} DevSlot deriving (Bits, Eq, FShow);

function Bool inUse(DevSlot d) = d.timer || d.strio != SNone || d.window || d.listening;

// a held request (fep.Fep.held): the device and the kind of event that
// answers it, the codes of the card's script (mkfepcard.SCRIPT_KINDS)
Bit#(32) heldLogin = 1;
Bit#(32) heldGetl  = 2;
typedef struct { Bool valid; Bit#(32) dev; Bit#(32) kind; } HeldSlot deriving (Bits, Eq, FShow);

// A queued reply, after the packet's 8-byte header:
//   RStatus  [status]
//   RString  [status, a string of dlen bytes]: the card's from `addr`
//            (SrcCard), zeros (SrcZero), or ">sys>user>" and the home
//            buffer (SrcHome)
//   RDate    [status, fep.DATE, `addr` (the time of day)]
//   RRaw     dlen bytes of the card from `addr`, the whole message
typedef enum { RStatus, RString, RDate, RRaw } ReplyKind deriving (Bits, Eq, FShow);
typedef enum { SrcCard, SrcZero, SrcHome } StrSrc deriving (Bits, Eq, FShow);
typedef struct {
   Bit#(32)  dev;
   Int#(32)  status;
   ReplyKind kind;
   StrSrc    src;
   Bit#(32)  addr;
   UInt#(32) dlen;
} ReplyDesc deriving (Bits, Eq, FShow);

function ReplyDesc plain(Bit#(32) dev, Int#(32) st) =
   ReplyDesc { dev: dev, status: st, kind: RStatus, src: SrcZero, addr: 0, dlen: 0 };
function ReplyDesc zeros(Bit#(32) dev, UInt#(32) n) =
   ReplyDesc { dev: dev, status: stNormal, kind: RString, src: SrcZero, addr: 0, dlen: n };

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
function UInt#(32) replyLen(ReplyDesc d) = case (d.kind)
   RStatus: 16;
   RString: 20 + d.dlen + pad4(d.dlen);
   RDate:   32;
   default: 8 + d.dlen;
endcase;

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
   FIFOF#(void)      idleF <- mkFIFOF;

   Reg#(FepConfig) cfg <- mkReg(fepDefault);
   Reg#(FepMount)  mnt <- mkReg(MountNotYet);
   Reg#(UInt#(32)) dirCount <- mkReg(0);
   Reg#(Bit#(32))  dirFirst <- mkReg(0);
   // the card's fep.py constants (header words 32-44): the attributes
   // message and the script, block and length; 0 none
   Reg#(Bit#(32))  attrBlk  <- mkReg(0);
   Reg#(UInt#(32)) attrLen  <- mkReg(0);
   Reg#(Bit#(32))  scrBlk   <- mkReg(0);
   Reg#(UInt#(32)) scrLen   <- mkReg(0);
   Reg#(Bit#(48))  now      <- mkReg(0);   // the clock (setTime)

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
   // fep.Fep.appending: the devices an append_open accepted (the path and
   // fep.Fep.appended are not kept: fep.py keeps them in memory only, and
   // no answer reads them); a close (60) frees the slot
   Vector#(AppendSlots, Reg#(Maybe#(Bit#(32)))) appending <- replicateM(mkReg(tagged Invalid));
   Vector#(DevSlots, Reg#(DevSlot))   devs <- replicateM(mkReg(unpack(0)));
   Vector#(HeldSlots, Reg#(HeldSlot)) held <- replicateM(mkReg(unpack(0)));
   Reg#(UInt#(32)) scrPos   <- mkReg(0);     // the script's next entry (fep.Fep.script[0])
   Vector#(HomeMax, Reg#(Bit#(8))) home <- replicateM(mkReg(0));
   Reg#(Bool)      homeBusy <- mkReg(False); // a SrcHome reply is queued

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
   Reg#(Int#(32))  alen  <- mkReg(0);
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
   Reg#(Bit#(32))  fpblk <- mkReg(0);     // the entry's 221 and 222 answers
   Reg#(UInt#(32)) fplen <- mkReg(0);
   Reg#(Bit#(32))  fablk <- mkReg(0);
   Reg#(UInt#(32)) falen <- mkReg(0);
   Reg#(Bit#(32))  w     <- mkReg(0);     // a card word read
   Reg#(Bit#(32))  bw    <- mkReg(0);     // a body word read
   // a name compared (fep.unjis), the time of day, the home's name
   Vector#(NNames, Reg#(Bool)) nm <- replicateM(mkReg(False));
   Reg#(Bit#(8))   hb    <- mkReg(0);
   Reg#(Bit#(48))  rem   <- mkReg(0);
   Reg#(UInt#(5))  kd    <- mkReg(0);
   Reg#(UInt#(32)) hn    <- mkReg(0);
   // a RECEIVE
   Reg#(UInt#(32)) cnt   <- mkReg(0);
   Reg#(Bool)      cont  <- mkReg(False);
   Reg#(UInt#(32)) kk    <- mkReg(0);
   // the event
   Reg#(Bit#(32))  skind <- mkReg(0);
   Reg#(UInt#(32)) slen  <- mkReg(0);
   Reg#(Bit#(32))  evOut <- mkReg(0);

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
   function Bool isAppending(Bit#(32) dev);
      Bool r = False;
      for (Integer s = 0; s < valueOf(AppendSlots); s = s + 1)
         if (appending[s] == tagged Valid dev) r = True;
      return r;
   endfunction
   function Maybe#(UInt#(TLog#(AppendSlots))) freeAppend();
      Maybe#(UInt#(TLog#(AppendSlots))) r = tagged Invalid;
      for (Integer s = valueOf(AppendSlots) - 1; s >= 0; s = s - 1)
         if (!isValid(appending[s])) r = tagged Valid fromInteger(s);
      return r;
   endfunction
   function Maybe#(UInt#(TLog#(FileSlots))) freeSlot();
      Maybe#(UInt#(TLog#(FileSlots))) r = tagged Invalid;
      for (Integer s = valueOf(FileSlots) - 1; s >= 0; s = s - 1)
         if (!files[s].valid) r = tagged Valid fromInteger(s);
      return r;
   endfunction
   // the device's sets: its slot, or a free one; `d` what it is now
   function Maybe#(UInt#(TLog#(DevSlots))) devSlotOf(Bit#(32) dev);
      Maybe#(UInt#(TLog#(DevSlots))) r = tagged Invalid;
      for (Integer s = valueOf(DevSlots) - 1; s >= 0; s = s - 1)
         if (inUse(devs[s]) && devs[s].dev == dev) r = tagged Valid fromInteger(s);
      if (!isValid(r))
         for (Integer s = valueOf(DevSlots) - 1; s >= 0; s = s - 1)
            if (!inUse(devs[s])) r = tagged Valid fromInteger(s);
      return r;
   endfunction
   DevSlot d0 = DevSlot { dev: pdev, timer: False, strio: SNone, window: False, listening: False };
   DevSlot d = case (devSlotOf(pdev)) matches
                  tagged Valid .s &&& inUse(devs[s]): devs[s];
                  default: d0;
               endcase;
   // a device's sets changed, written back, and its reply queued (a full
   // table or queue refuses, why 8)
   function Action setDev(DevSlot n, ReplyDesc r) = action
      case (devSlotOf(pdev)) matches
         tagged Valid .s &&& replies.notFull: begin devs[s] <= n; replies.enq(r); end
         default: perr <= whyLimit;
      endcase
   endaction;
   function Maybe#(UInt#(TLog#(HeldSlots))) heldOf(Bit#(32) dev);
      Maybe#(UInt#(TLog#(HeldSlots))) r = tagged Invalid;
      for (Integer s = valueOf(HeldSlots) - 1; s >= 0; s = s - 1)
         if (held[s].valid && held[s].dev == dev) r = tagged Valid fromInteger(s);
      return r;
   endfunction
   function Action hold(Bit#(32) kind) = action
      Maybe#(UInt#(TLog#(HeldSlots))) r = tagged Invalid;
      for (Integer s = valueOf(HeldSlots) - 1; s >= 0; s = s - 1)
         if (!held[s].valid) r = tagged Valid fromInteger(s);
      case (r) matches
         tagged Valid .s: held[s] <= HeldSlot { valid: True, dev: pdev, kind: kind };
         default: perr <= whyLimit;
      endcase
   endaction;
   // fep.Fep.idle's choice: the lowest device id holding this kind
   function Maybe#(UInt#(TLog#(HeldSlots))) heldFor(Bit#(32) kind);
      Maybe#(UInt#(TLog#(HeldSlots))) r = tagged Invalid;
      for (Integer s = 0; s < valueOf(HeldSlots); s = s + 1)
         if (held[s].valid && held[s].kind == kind) begin
            Bool lower = case (r) matches
                            tagged Valid .b: (unpack(held[s].dev) < Int#(32)'(unpack(held[b].dev)));
                            default: True;
                         endcase;
            if (lower) r = tagged Valid fromInteger(s);
         end
      return r;
   endfunction
   Bool isFile = isValid(slotOf(pdev));
   Bool isHeld = isValid(heldOf(pdev));
   // fep.Fep.known
   Bool known = isFile || isAppending(pdev) || d.timer || d.strio != SNone || d.window;

   function Action answer(FepAnswerKind k, UInt#(24) n, Bit#(8) y) =
      ansF.enq(FepAnswer { kind: k, result: 0, count: n, why: y });
   function Action answerResult(Bit#(32) r) =
      ansF.enq(FepAnswer { kind: FepDone, result: r, count: 0, why: 0 });
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

   function Action queue(ReplyDesc r) = action
      if (replies.notFull) replies.enq(r); else perr <= whyLimit;
   endaction;

   // the byte k of a RECEIVE's piece, but for the card's data
   function Bit#(8) pieceByte(ReplyDesc r, UInt#(32) k);
      Bit#(8) x = 0;
      if (k < 4) x = byteOf(r.dev, k);
      else if (k < 8) x = (k == 7 && cont) ? 1 : 0;
      else begin
         UInt#(32) p = skip + k - 8;
         if (p >= 8 && p < 12) x = byteOf(pack(r.status), p - 8);
         else if (p >= 12 && p < 16)
            x = (p == 15) ? (r.kind == RString ? 1 : r.kind == RDate ? 2 : 0) : 0;
         else if (r.kind == RString) begin
            if (p < 20) x = byteOf(pack(r.dlen), p - 16);
            else if (p < 20 + r.dlen && r.src == SrcHome)
               x = (p < 40) ? homePrefix(p - 20) : home[p - 40];
         end
         else if (r.kind == RDate) begin
            if (p < 24) x = 8'hff;
            else if (p < 28) x = byteOf(fepDate, p - 24);
            else x = byteOf(r.addr, p - 28);
         end
      end
      return x;
   endfunction
   function Bool pieceIsCard(ReplyDesc r, UInt#(32) k);
      UInt#(32) p = skip + k - 8;
      return k >= 8 && ((r.kind == RString && r.src == SrcCard && p >= 20 && p < 20 + r.dlen)
                        || r.kind == RRaw);
   endfunction
   function Bit#(32) cardAddr(ReplyDesc r, UInt#(32) k) =
      r.addr + pack(skip + k - 8) - (r.kind == RRaw ? 8 : 20);

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
      cardRd(32, True);
      attrBlk <= w;
      cardRd(36, True);
      attrLen <= unpack(w);
      cardRd(40, True);
      scrBlk <= w;
      cardRd(44, True);
      scrLen <= unpack(w);
      cardRd(20, True);
      action
         if (w != 256 || cardErr || mnt == MountBad) mnt <= MountBad;
         else mnt <= MountOk;
      endaction
   endseq;

   // ---- the message: fep.unpack_message -------------------------
   // every argument is walked; the first MaxArgs are kept
   Stmt parse = seq
      if (bodyLen < 8) perr <= whyMessage;
      else seq
         bodyRd(0, True);
         mcmd <= unpack(bw);
         bodyRd(4, True);
         nargs <= unpack(bw);
         if (nargs < 0 || nargs > fromInteger(valueOf(BodyMax))) perr <= whyMessage;
         else if (8 + 4 * unpack(pack(nargs)) > bodyLen) perr <= whyMessage;
         else seq
            action at <= 8 + 4 * unpack(pack(nargs)); j <= 0; endaction
            while (j < unpack(pack(nargs)) && perr == 0) seq
               bodyRd(8 + 4 * j, True);
               alen <= unpack(bw);
               if (alen == -1) seq
                  if (at + 4 > bodyLen) perr <= whyMessage;
                  else seq
                     bodyRd(at, True);
                     action
                        if (j < fromInteger(valueOf(MaxArgs)))
                           args[j] <= MsgArg { isInt: True, v: bw, len: 0 };
                        at <= at + 4;
                     endaction
                  endseq
               endseq
               else if (alen < -1 || alen > fromInteger(valueOf(BodyMax))) perr <= whyMessage;
               else action
                  UInt#(32) ln = unpack(pack(alen));
                  if (j < fromInteger(valueOf(MaxArgs)))
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
               flen <= unpack(w);
               cardRd(dirFirst * 512 + pack(e) * 256 + 240, True);
               fpblk <= w;
               cardRd(dirFirst * 512 + pack(e) * 256 + 244, True);
               fplen <= unpack(w);
               cardRd(dirFirst * 512 + pack(e) * 256 + 248, True);
               fablk <= w;
               cardRd(dirFirst * 512 + pack(e) * 256 + 252, True);
               action falen <= unpack(w); found <= True; endaction
            endseq
         endseq
         e <= e + 1;
      endseq
   endseq;

   // ---- a string argument as fep.unjis reads it, against the names:
   // nm[n] is True when its text is nameOf(n) -----------------------
   function Stmt names(MsgArg a) = seq
      action
         for (Integer n = 0; n < valueOf(NNames); n = n + 1)
            nm[n] <= !a.isInt && (a.len >> 1) == nameLen(n);
         j <= 0;
      endaction
      while (j < (a.len >> 1) && (nm[0] || nm[1] || nm[2] || nm[3] || nm[4] || nm[5])) seq
         bodyRd(unpack(a.v) + 2 * j, False);
         hb <= bw[7:0];
         bodyRd(unpack(a.v) + 2 * j + 1, False);
         action
            let c = unjisChar(hb, bw[7:0]);
            for (Integer n = 0; n < valueOf(NNames); n = n + 1)
               if (!isValid(c) || validValue(c) != charAt(nameOf(n), j)) nm[n] <= False;
            j <= j + 1;
         endaction
      endseq
   endseq;

   // ---- fep.Fep.string_io: io(args[0], args[1]) on d.strio --------
   Int#(32) ioCmd = unpack(args[0].v);
   Bool ioInt = args[0].isInt;
   Stmt stringIo = seq
      if (ioInt && d.strio == SReplier && (ioCmd == 0 || ioCmd == 2))
         queue(zeros(pdev, 0));
      else if (ioInt && d.strio == SReplier && ioCmd == 1) action
         // a text for the user: fep.py logs data[2:] (no log here); an
         // integer raises there
         if (args[1].isInt) perr <= whyRequest;
         else queue(zeros(pdev, 2));
      endaction
      else if (ioInt && d.strio == SServer && ioCmd == 0) seq
         if (args[1].isInt) perr <= whyRequest;        // unjis of an integer raises
         else seq
            names(args[1]);
            if (nm[3]) action
               setDev(DevSlot { dev: pdev, timer: d.timer, strio: d.strio, window: d.window,
                                listening: True },
                      zeros(pdev, 0));
            endaction
            else if (nm[4]) queue(plain(pdev, stAbnormal));
            else perr <= whyRequest;
         endseq
      endseq
      else if (ioInt && d.strio == SServer && ioCmd == 1 && d.listening)
         hold(heldLogin);                               // no reply: held
      // the standard I/O window (fep.STD_WINDOW): 104 its place, 130 its
      // title, 141 activate, 111 putb: [1, ""]; putb's text is unjis'd
      // (logged) there, so it must be a string; the others' data is not
      // looked at
      else if (ioInt && d.strio == SStdWindow
               && (ioCmd == reqCreateWindow || ioCmd == 130 || ioCmd == 141 || ioCmd == reqPutb))
         action
            if (ioCmd == reqPutb && args[1].isInt) perr <= whyRequest;
            else queue(zeros(pdev, 0));
         endaction
      // its getl (110): held until the next scripted line, as a window's
      else if (ioInt && d.strio == SStdWindow && ioCmd == reqGetl)
         hold(heldGetl);                                // no reply: held
      else if (ioInt && d.strio == SUserDevice && ioCmd == 0) seq
         // [len Name, len Pass] ++ Name ++ Pass: the reply ">sys>user>"
         // ++ data[4:4+2n], n = int.from_bytes(data[:2]), as Python
         // slices it
         if (args[1].isInt) perr <= whyRequest;
         else if (homeBusy) perr <= whyLimit;
         else seq
            action hn <= 0; j <= 0; endaction
            if (args[1].len >= 1) seq
               bodyRd(unpack(args[1].v), False);
               hn <= unpack(zeroExtend(bw[7:0]));
            endseq
            if (args[1].len >= 2) seq
               bodyRd(unpack(args[1].v) + 1, False);
               hn <= hn << 8 | unpack(zeroExtend(bw[7:0]));
            endseq
            action
               UInt#(32) stop = min(args[1].len, 4 + 2 * hn);
               hn <= stop > 4 ? stop - 4 : 0;
            endaction
            if (hn > fromInteger(valueOf(HomeMax))) perr <= whyLimit;
            else seq
               while (j < hn) seq
                  bodyRd(unpack(args[1].v) + 4 + j, False);
                  action home[j] <= bw[7:0]; j <= j + 1; endaction
               endseq
               action
                  homeBusy <= True;
                  queue(ReplyDesc { dev: pdev, status: stNormal, kind: RString, src: SrcHome,
                                    addr: 0, dlen: 20 + hn });
               endaction
            endseq
         endseq
      endseq
      else perr <= whyRequest;
   endseq;

   // ---- a request: fep.Fep.request, its tests in its order ---------
   Stmt serve = seq
      if (mcmd == reqReadOpen && nargs == 4 && !isFile) seq
         if (args[3].isInt || pack(args[3].len)[0] == 1) perr <= whyRequest;   // open_file raises
         else seq
            lookup;
            if (cardErr) perr <= whyCard;
            else if (!found) queue(plain(pdev, stAbnormal));
            else action
               case (freeSlot()) matches
                  tagged Valid .s: begin
                     files[s] <= FileSlot { valid: True, dev: pdev, start: fstart, len: flen, pos: 0,
                                            pblk: fpblk, plen: fplen, ablk: fablk, alen: falen };
                     queue(plain(pdev, stNormal));
                  end
                  default: perr <= whyLimit;
               endcase
            endaction
         endseq
      endseq
      // pathname {Id, 221} and attributes {Id, 222} on a read file the
      // card gives them for (a home file, fep.FileData): [1, the card's
      // string] (2026-11-25).  On a file without them fep.py goes on
      // through its tests and raises, as here
      else if (mcmd == reqPathname && nargs == 0 && isFile
               && files[validValue(slotOf(pdev))].pblk != 0) action
         let f = files[validValue(slotOf(pdev))];
         queue(ReplyDesc { dev: pdev, status: stNormal, kind: RString, src: SrcCard,
                           addr: f.pblk * 512, dlen: f.plen });
      endaction
      else if (mcmd == reqFileAttributes && nargs == 0 && isFile
               && files[validValue(slotOf(pdev))].ablk != 0) action
         let f = files[validValue(slotOf(pdev))];
         queue(ReplyDesc { dev: pdev, status: stNormal, kind: RString, src: SrcCard,
                           addr: f.ablk * 512, dlen: f.alen });
      endaction
      // append_open {Id, 203, "", User, Password, Path}: accepted, [1],
      // whatever the arguments are (fep.py never looks at the path's
      // bytes: no open_file), if the device has no file and is not
      // appending
      else if (mcmd == reqAppendOpen && nargs == 4 && !isFile && !isAppending(pdev))
         action
            case (freeAppend()) matches
               tagged Valid .s: begin
                  appending[s] <= tagged Valid pdev;
                  queue(plain(pdev, stNormal));
               end
               default: perr <= whyLimit;
            endcase
         endaction
      // create_timer {Id, 310, Node, User, Password}: [1]
      else if (mcmd == reqCreateTimer && nargs == 3 && !d.timer) action
         setDev(DevSlot { dev: pdev, timer: True, strio: d.strio, window: d.window,
                          listening: d.listening },
                plain(pdev, stNormal));
      endaction
      // fep_attributes {Id, 240, Node}: fep.ATTRIBUTES, the card's message
      else if (mcmd == reqAttributes && nargs == 1 && !known) action
         if (attrLen == 0) perr <= whyCard;
         else queue(ReplyDesc { dev: pdev, status: stNormal, kind: RRaw, src: SrcCard,
                                addr: attrBlk * 512, dlen: attrLen });
      endaction
      // create_string_io {C, 601, Node, User, Password, Name}
      else if (mcmd == reqCreateStrIo && nargs == 4 && !known) seq
         names(args[3]);
         if (args[3].isInt || !(nm[0] || nm[1] || nm[2] || nm[5])) perr <= whyRequest;
         else action
            setDev(DevSlot { dev: pdev, timer: d.timer,
                             strio: nm[0] ? SReplier : nm[1] ? SServer
                                    : nm[2] ? SUserDevice : SStdWindow,
                             window: d.window, listening: d.listening },
                   plain(pdev, stNormal));
         endaction
      endseq
      else if (mcmd == reqIo && nargs == 2 && d.strio != SNone && !isHeld)
         stringIo;
      // create_window {W, 104, Node, User, Password}
      else if (mcmd == reqCreateWindow && nargs == 3 && !known) action
         setDev(DevSlot { dev: pdev, timer: d.timer, strio: d.strio, window: True,
                          listening: d.listening },
                plain(pdev, stNormal));
      endaction
      // the window calls answered [1]; putb's text is unjis'd (logged)
      // there, so it must be a string
      else if (windowAnswered(mcmd) && d.window && !isHeld) action
         if (mcmd == reqPutb && (nargs < 1 || args[0].isInt)) perr <= whyRequest;
         else queue(plain(pdev, stNormal));
      endaction
      else if (mcmd == reqGetl && d.window && !isHeld)
         hold(heldGetl);                                // no reply: held
      // close of a string-I/O device or a window: [1] (a hold stays)
      else if (mcmd == reqClose && nargs == 0 && (d.strio != SNone || d.window)) action
         setDev(DevSlot { dev: pdev, timer: d.timer, strio: SNone, window: False,
                          listening: False },
                plain(pdev, stNormal));
      endaction
      // abort of a held request: that request answered [6]
      else if (mcmd == reqAbort && nargs == 0 && isHeld) action
         held[validValue(heldOf(pdev))] <= unpack(0);
         queue(plain(pdev, stAborted));
      endaction
      // get_date_time {Id, 304}: [1, DATE, (clock / 16) mod one day]
      else if (mcmd == reqGetDateTime && nargs == 0 && d.timer) seq
         action rem <= now >> 4; kd <= 18; endaction
         while (kd != 0) action
            Bit#(48) sub = msPerDay << (kd - 1);
            if (rem >= sub) rem <= rem - sub;
            kd <= kd - 1;
         endaction
         queue(ReplyDesc { dev: pdev, status: stNormal, kind: RDate, src: SrcZero,
                           addr: truncate(rem), dlen: 0 });
      endseq
      else if (mcmd == reqGetb && nargs == 1 && isFile) action
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
            queue(plain(pdev, stEod));
         else begin
            queue(ReplyDesc { dev: pdev, status: stNormal, kind: RString, src: SrcCard,
                              addr: f.start * 512 + pack(f.pos), dlen: chunk });
            let g = f;
            g.pos = f.pos + chunk;
            files[s] <= g;
         end
      endaction
      // the timer's close: [1]
      else if (mcmd == reqClose && nargs == 0 && d.timer) action
         setDev(DevSlot { dev: pdev, timer: False, strio: d.strio, window: d.window,
                          listening: d.listening },
                plain(pdev, stNormal));
      endaction
      // flush of a read file: [1]
      else if (mcmd == reqFlush && nargs == 0 && isFile)
         queue(plain(pdev, stNormal));
      else if (mcmd == reqClose && nargs == 0 && isFile) action
         files[validValue(slotOf(pdev))] <= unpack(0);
         queue(plain(pdev, stNormal));
      endaction
      // the close of the append-opened file (the syslog's, at PIMOS's
      // end): [1], as a read file's
      else if (mcmd == reqClose && nargs == 0 && isAppending(pdev)) action
         for (Integer s = 0; s < valueOf(AppendSlots); s = s + 1)
            if (appending[s] == tagged Valid pdev) appending[s] <= tagged Invalid;
         queue(plain(pdev, stNormal));
      endaction
      // {-1, 80}, terminate (the link's stream closed, at PIMOS's end):
      // noted there (fep.Fep.terminated), not answered; nothing kept here
      else if (mcmd == reqTerminate && nargs == 0 && pdev == 32'hffffffff) noAction;
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
               if (pieceIsCard(replies.first, kk)) seq
                  cardRd(cardAddr(replies.first, kk), False);
                  action recvF.enq(w[7:0]); kk <= kk + 1; endaction
               endseq
               else action recvF.enq(pieceByte(replies.first, kk)); kk <= kk + 1; endaction
            endseq
            action
               if (cardErr) dead <= True;
               if (cont) skip <= skip + cnt - 8;
               else begin
                  if (replies.first.kind == RString && replies.first.src == SrcHome)
                     homeBusy <= False;
                  replies.deq; skip <= 8;
               end
            endaction
         endseq
      endseq
   endseq;

   // ---- the event: fep.Fep.idle ------------------------------------
   Stmt doIdle = seq
      if (dead) refuse(whyAfter);
      else if (mnt != MountOk) refuse(whyCard);
      else if (scrPos >= scrLen) answerResult(0);       // the script is done
      else seq
         action cardErr <= False; perr <= 0; evOut <= 0; endaction
         cardRd(scrBlk * 512 + pack(scrPos), True);
         skind <= w;
         cardRd(scrBlk * 512 + pack(scrPos) + 4, True);
         slen <= unpack(w);
         action
            if (cardErr) perr <= whyCard;
            else case (heldFor(skind)) matches
               tagged Valid .s: begin
                  queue(ReplyDesc { dev: held[s].dev, status: stNormal, kind: RString,
                                    src: SrcCard, addr: scrBlk * 512 + pack(scrPos) + 8,
                                    dlen: slen });
                  held[s] <= unpack(0);
                  scrPos <= scrPos + 8 + slen + pad4(slen);
                  evOut <= 1;
               end
               default: noAction;                       // nothing holds that kind
            endcase
         endaction
         if (perr != 0) refuse(perr); else answerResult(evOut);
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
      // an absent unit (fep.py decides it in Fep.command, before the
      // unit and LUN checks: no LUN or CDB-length check here)
      else if (cur.unit <= absentLast && cur.cdbLen == 5 && op == opTestUnitReady
               && cur.dir == 0 && curLen == 0)
         answerResult(noDevice);
      else if (cur.unit != 7 || cur.cdbLen != 5) refuse(whyUnitCdb);
      else if (clun != cur.lun || cur.cdb[1][4:0] != 0) refuse(whyLun);
      else if (op == opTestUnitReady && cur.dir == 0 && curLen == 0 && cdbLenOk)
         answer(FepDone, 0, 0);
      // INQUIRY (the kernel's bus scan): five bytes, 03 00 07 00 00
      else if (op == opInquiry && cur.lun == 0 && cur.dir == 2 && cdbLenOk && curLen == 255) seq
         answer(FepDone, 5, 0);
         recvF.enq(8'h03); recvF.enq(8'h00); recvF.enq(8'h07); recvF.enq(8'h00); recvF.enq(8'h00);
      endseq
      else if (op == opSend && cur.lun == 0 && cur.dir == 1 && cdbLenOk)
         doSend;
      else if (op == opReceive && cur.lun == 1 && cur.dir == 2 && cdbLenOk)
         doReceive;
      else refuse(whyCommand);
   endseq;

   Stmt main = seq
      mount;
      while (True) seq
         await(cfgF.notEmpty || cmdF.notEmpty || idleF.notEmpty);
         if (cfgF.notEmpty) action
            cfg <= cfgF.first; cfgF.deq;
            dead <= False;
            for (Integer s = 0; s < valueOf(FileSlots); s = s + 1) files[s] <= unpack(0);
            for (Integer s = 0; s < valueOf(AppendSlots); s = s + 1) appending[s] <= tagged Invalid;
            for (Integer s = 0; s < valueOf(DevSlots); s = s + 1) devs[s] <= unpack(0);
            for (Integer s = 0; s < valueOf(HeldSlots); s = s + 1) held[s] <= unpack(0);
            replies.clear;
            skip <= 8; lagged <= False; partValid <= False; partLen <= 0;
            scrPos <= 0; homeBusy <= False;
         endaction
         else if (idleF.notEmpty) seq
            idleF.deq;
            doIdle;
         endseq
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
   method Action configure(FepConfig c);
      cfgF.enq(c);
      now <= 0;
   endmethod
   method Action idle = idleF.enq(?);
   method Action setTime(Bit#(48) t);
      now <= t;
   endmethod
   method UInt#(24) maxBuffer = cfg.maxBuffer;
   method FepMount mounted = mnt;
endmodule

endpackage
