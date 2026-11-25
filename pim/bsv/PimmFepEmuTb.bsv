// PimmFepEmuTb.bsv -- Bluesim bench: the FEP emulator on a card image,
// given the commands ref/pimm/ref_scsi.py's parts gave fep.py.  ALL OURS.
//
// Driven by bsv/run_fepemu.sh through bsv/fepemu_check.py, which turns a
// tape (ref/pimm/fep_tapes/*.tape, recorded by ref/pimm/record_fep.py)
// into a vector file (PIMM_FEP_VECTORS, read by PimmFepEmuTb.c) and a
// card image (PIMM_SD_IMAGE, pim/tools/mkfepcard.py), runs this bench,
// and compares every answer line it prints with fep.py's answer to the
// same command, made by replaying the tape into a fresh fep.Fep.
//
// The vector file: whitespace-separated hex words, records
//   1 getbUnit getbBytes lag maxBuffer                  configure
//   2 unit lun dir length cdbLen cdb... ndata data...   a command
//   3                                                   the event (idle)
//   4 high low                                          setTime: the clock
//   0                                                   the end
// Printed: "A D result count hex|-", "A N", "A E why" for each command,
// "A I 0|1" (or "A E why") for each event, then "END n"; "FAIL ..." on a
// timeout.
//
// Observed fault injections, 2026-11-23 (each into the file, from a
// backup copy, run_fepemu.sh run, the file restored from the copy and
// compared).  Sims: F the image file, S the SPI reader with a
// block-addressed card, B the SPI reader with a byte-addressed card.
//  PimmFepEmu.bsv:
//   eod status 3 for 2                     all 7 tapes FAIL on F, S, B
//                                          (first reported: characters
//                                          command 6, the reply's byte 11)
//   getb gives one byte more than asked    direct, late, odd, two_files
//                                          on F, S, B (one_file,
//                                          characters, small buffer: each
//                                          getb ran to the end of a file)
//   a getb reply's length word one more    all 7, F S B
//   continued-packet flag never set        direct, small_buffer, F S B
//   the lookup matches a name that is a    all 7, F S B (the decoy entry
//     prefix of the path                   answers: "DECOY ...")
//   a file's data one block on             all 7, F S B
//   the card reader asks for block + 1     all 7, F S B (mount fails)
//   lag ignored                            direct, late, F S B
//   a cut reply goes on one byte late      direct only, F S B (the IPL
//                                          never asks for a cut reply's
//                                          rest: ref_scsi.py "small
//                                          buffer")
//  PimmSdBlock.bsv:
//   CMD17 always takes the block number    all 7 on B only (F does not
//                                          use the reader; S is
//                                          block-addressed)
//   MISO bits taken LSB first              all 7 on S and B (mount fails)
// Nothing injected passed unnoticed.  NOT tested: the OURS limits
// (BodyMax, FileSlots, ReplySlots, AppendSlots, one continued message at
// a time): no tape reaches one.
//
// Observed fault injections, 2026-11-24, the paths for PIMOS's start
// (INQUIRY, absent units, append_open), the same way, with all 9 tapes
// on disk; every one fails on F, S and B, and only the tapes named:
//   noDevice 400h for 800h                 direct_kernel, kernel (command
//                                          2, the first absent unit:
//                                          done 1024)
//   INQUIRY's byte 2 6 for 7               direct_kernel, kernel
//                                          (command 1)
//   the absent test also needs LUN 0       direct_kernel (command 8: LUN 2
//                                          refused, fep.py answers 800h)
//   absent units 0..6                      direct, direct_kernel (unit 6
//                                          answered 800h; fep.py raises)
//   INQUIRY of any length                  direct_kernel (command 31,
//                                          36 bytes answered)
//   append_open answered status 5          direct_kernel (command 12),
//                                          kernel (command 9): the
//                                          reply's status word
//   the "not appending" test dropped       direct_kernel (append_open twice
//                                          answered)
//   configure keeps the appending devices  direct_kernel (command 24, the
//                                          next section's append_open
//                                          refused)
//   append_open on a device with a file    direct_kernel (answered; fep.py
//     open accepted                        raises)
//
// Observed fault injections, 2026-11-24, the paths to the shell's prompt
// (the timer, 240, string-I/O, windows, holds and the event), the same
// way (each from a backup copy, run_fepemu.sh run, restored, `cmp`
// equal), all 9 tapes; every one fails on F, S and B, only the tapes and
// commands named (direct_kernel's command numbers count the events):
//   get_date_time's division 17 steps,     direct_kernel 70 (the clock at
//     not 18                               2^48-1 only)
//   the date 33743                         direct_kernel 61 63 65 68 70
//                                          72, kernel 15
//   the event picks the highest device id  direct_kernel 223 (44 answered,
//                                          not -3)
//   the event answers a hold of any kind   direct_kernel 162 164 165 166
//                                          169 173
//   a name of odd length not matched       direct_kernel 108 (refused) and
//     (unjis drops the last byte)          every command after it
//   the user device's n from its second    direct_kernel 318 (n 256) --
//     byte only                            PASSED UNNOTICED until that
//                                          section was added: no tape had
//                                          a high byte set
//   the replier's io(1) answered [1, ""]   direct_kernel 98 100, kernel
//                                          108 127 134
//   a window's close clears its timer too  direct_kernel 201 (304 refused)
//                                          and after
//   240 on a known device answered         direct_kernel 245 314
//   putb's text not checked                direct_kernel 288 290
//   a held request aborted answered 1      direct_kernel 164 211
//   a whole-message reply (RRaw) read 4    direct_kernel 53 55 56 57 (240,
//     bytes off                            whole and cut), kernel 21
//   the server's io(1) held without        direct_kernel 274
//     listening
// NOT tested: the new OURS limits (DevSlots, HeldSlots, HomeMax, one home
// reply queued): no tape reaches one.
//
// Observed fault injections, 2026-11-24, after the merger change and the
// typed shutdown (the standard I/O window, 60 on the append-opened file,
// {-1, 80}), the same way: each into PimmFepEmu.bsv from a copy of the
// committed file, run_fepemu.sh run, the file restored from the copy
// (`cmp` equal, `git diff` clean).  All 9 tapes; every one FAILs on F, S
// and B alike, on only the tapes named, the other seven passing.
// Command numbers count the events; fepemu_check.py prints at most six
// per tape, so a run of six is "and after":
//   the append 60 branch removed           direct_kernel 24-29, kernel
//                                          217-222 (the syslog's close at
//                                          PIMOS END refused, why 7)
//   the append 60 answered 5               direct_kernel 25 29, kernel 218
//   the append 60 keeps the slot           direct_kernel 26-31 (the next
//                                          append_open on the device)
//   601 refuses pimos_standard_io_window   direct_kernel 336-341, kernel
//                                          184-189
//   its io 104 dropped                     direct_kernel 338-343, kernel
//                                          187-192
//   its io 130 dropped                     direct_kernel 342-347, kernel
//                                          190-195
//   its io 141 dropped                     direct_kernel 344-349, kernel
//                                          193-198
//   its io 111 dropped                     direct_kernel 348-353, kernel
//                                          196-201
//   its 111 integer text accepted          direct_kernel 376 only
//   its 110 answered [1, ""], not held     direct_kernel 354 357 358 360
//                                          385, kernel 200 202 203
//   its 110 held as a login                direct_kernel 357-362, kernel
//                                          202 203 214 215 216
//   80 accepted on any device              direct_kernel 389 only
//   80 answered [1]                        direct_kernel 368 372, kernel 221
//   the 80 branch removed                  direct_kernel 367-372, kernel
//                                          220-223
// Nothing injected passed unnoticed.  The four characters added to
// unjisChar (" ( ) =) cannot be seen on a tape: no name compared holds
// them, and a typed line reaches the emulator as card bytes.
//
// The card is reached through `card` (a module argument in
// mkPimmFepEmuBench), so the same bench runs the emulator over the
// BDPI file (mkPimmFepEmuTb) or over the SPI reader and a card model
// (mkPimmFepEmuSpiTb, PimmSdCardModel.bsv).

package PimmFepEmuTb;

import ClientServer::*;
import GetPut::*;
import Connectable::*;
import Vector::*;
import StmtFSM::*;
import PimmSdTypes::*;
import PimmFepEmu::*;
import PimmSdBlockFile::*;

import "BDPI" function Bit#(32) fept_word(Bit#(32) i);

module mkPimmFepEmuBench#(SdBlockServer card)(Empty);
   PimmFepEmu emu <- mkPimmFepEmu;
   mkConnection(emu.card, card);

   Reg#(Bit#(32)) ix    <- mkReg(0);
   Reg#(Bit#(32)) k     <- mkReg(0);
   Reg#(Bit#(32)) n     <- mkReg(0);
   Reg#(Bit#(32)) cmds  <- mkReg(0);
   Reg#(UInt#(24)) cnt  <- mkReg(0);
   Reg#(Bit#(32)) cycle <- mkReg(0);
   Reg#(Bit#(32)) quiet <- mkReg(0);
   PulseWire      moved <- mkPulseWire;

   function Bit#(32) at(Bit#(32) o) = fept_word(ix + o);

   rule rl_clock;
      cycle <= cycle + 1;
      quiet <= moved ? 0 : quiet + 1;
      if (quiet > 2000000) begin
         $display("FAIL timeout: no progress for 2,000,000 cycles (cycle %0d)", cycle);
         $finish(1);
      end
   endrule

   Stmt one = seq
      action
         Vector#(12, Bit#(8)) c = replicate(0);
         Bit#(32) cl = at(5);
         for (Integer q = 0; q < 12; q = q + 1)
            if (fromInteger(q) < cl) c[q] = truncate(at(6 + fromInteger(q)));
         emu.cmd.request.put(FepCmd { unit: at(1), lun: at(2), dir: truncate(at(3)),
                                      length: unpack(truncate(at(4))),
                                      cdbLen: unpack(truncate(cl)), cdb: c });
         n <= at(6 + cl);                // ndata
         k <= 0;
         ix <= ix + 7 + cl;              // the first data word
         moved.send;
      endaction
      while (k < n) action
         emu.sendData.put(truncate(at(k)));
         k <= k + 1;
         moved.send;
      endaction
      action
         ix <= ix + n;
         let a <- emu.cmd.response.get;
         cmds <= cmds + 1;
         moved.send;
         case (a.kind)
            FepDone: begin
               $write("A D %0d %0d ", a.result, a.count);
               if (a.count == 0) $display("-");
            end
            FepNotReady: $display("A N");
            FepRefused: $display("A E %0d", a.why);
         endcase
         cnt <= (a.kind == FepDone) ? a.count : 0;
      endaction
      if (cnt != 0) seq
         while (cnt != 0) action
            let b <- emu.recvData.get;
            $write("%02x", b);
            cnt <= cnt - 1;
            moved.send;
         endaction
         $display("");
      endseq
   endseq;

   Stmt main = seq
      while (at(0) != 0) seq
         if (at(0) == 1) action
            emu.configure(FepConfig { getbUnit: unpack(truncate(at(1))),
                                      getbBytes: unpack(truncate(at(2))),
                                      lag: at(3) != 0,
                                      maxBuffer: unpack(truncate(at(4))) });
            ix <= ix + 5;
            moved.send;
         endaction
         else if (at(0) == 2) one;
         else if (at(0) == 3) seq
            action emu.idle; ix <= ix + 1; moved.send; endaction
            action
               let a <- emu.cmd.response.get;
               cmds <= cmds + 1;
               moved.send;
               if (a.kind == FepDone) $display("A I %0d", a.result);
               else if (a.kind == FepRefused) $display("A E %0d", a.why);
               else $display("A N");
            endaction
         endseq
         else if (at(0) == 4) action
            emu.setTime(truncate({at(1), at(2)}));
            ix <= ix + 3;
            moved.send;
         endaction
         else action
            $display("FAIL vector word %0d is %0d", ix, at(0));
            $finish(1);
         endaction
      endseq
      action
         $display("END %0d mounted %s maxBuffer %0d cycles %0d", cmds,
                  emu.mounted == MountOk ? "ok" : "bad", emu.maxBuffer, cycle);
         $finish(0);
      endaction
   endseq;

   mkAutoFSM(main);
endmodule

(* synthesize *)
module mkPimmFepEmuTb(Empty);
   SdBlockServer card <- mkPimmSdBlockFile(3);
   Empty b <- mkPimmFepEmuBench(card);
endmodule

endpackage
