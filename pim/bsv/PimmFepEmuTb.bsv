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
//   0                                                   the end
// Printed: "A D result count hex|-", "A N", "A E why" for each command,
// then "END n"; "FAIL ..." on a timeout.
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
// (INQUIRY, absent units, append_open), the same way; every one fails
// on F, S and B, and only the tapes named:
//   noDevice 400h for 800h                 direct_kernel (command 2, the
//                                          first absent unit: done 1024)
//   INQUIRY's byte 2 6 for 7               direct_kernel (command 1)
//   the absent test also needs LUN 0       direct_kernel (command 8: LUN 2
//                                          refused, fep.py answers 800h)
//   absent units 0..6                      direct, direct_kernel (unit 6
//                                          answered 800h; fep.py raises)
//   INQUIRY of any length                  direct_kernel (command 31,
//                                          36 bytes answered)
//   append_open answered status 5          direct_kernel (command 12, the
//                                          reply's status word)
//   the "not appending" test dropped       direct_kernel (append_open twice
//                                          answered)
//   configure keeps the appending devices  direct_kernel (command 24, the
//                                          next section's append_open
//                                          refused)
//   append_open on a device with a file    direct_kernel (answered; fep.py
//     open accepted                        raises)
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
