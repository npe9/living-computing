// StretchFixtureTest.bsv -- the disk's two arcs and the console's paper,
// as block RAM, tested alone (2026-11-25, fidelity_plan.md F0).
//
// WHY THIS FILE EXISTS.  mkDiskSourceSmall's platter and mkStretchIO's
// consoleImg were Vectors of Reg, 81,920 flip-flops of the whole core's
// 102,219 (fpga_feasibility.md §11).  They are now BRAMCores, and a BRAM
// differs from a Vector of mkReg(0) in two ways the suite's decks do not
// see:
//
//   1. IT DOES NOT POWER ON AT ZERO.  A one-bit-per-word "written" mask
//      supplies the zero.  No deck reads an unwritten disk word on the
//      small source (io_disk.strap pre-fills arc 0 precisely so that it
//      does not depend on this), and a console dump of unwritten paper
//      is only displayed, never checked.  So the mask's checks are here.
//   2. A READ'S ANSWER IS HELD ON THE BRAM'S OUTPUT, and a write must not
//      disturb it.  Each fixture uses one port to read and the other to
//      write so that it cannot.  The checks marked HELD pin that.
//
// The latency itself -- answer in the clock after the request -- is what
// the suite's cycle pins already check through the machine, and the
// disk's checks below collect one clock after the request, so a source
// that answered later fails them too.
//
// OBSERVED FAILURE SETS, injected 2026-11-25 and reverted:
//   - both masks ignored (readResp returns img.a.read unconditionally;
//     readConsoleResp returns consoleImg.b.read): exactly five FAILs --
//     disk unwritten word, disk unwritten neighbour, disk past the end
//     reads zero (the range test rode on the same flag), console
//     unwritten word, console unwritten neighbour -- each "got
//     aaaaaaaaaaaaaaaa".  Bluesim's BRAM, like BRAM2.v's initial block,
//     powers on at 'hAAAA..., not zero.
//   - both writes moved onto the READ port (img.a.put(True..),
//     consoleImg.b.put(True..)): exactly two FAILs, disk HELD across a
//     write (got 5a5a5a5aa5a5a5a5) and console HELD across a write (got
//     fedcba9876543210).
//
// NOT NAMED *Tb.bsv ON PURPOSE: .gitignore ignores bsv/Stretch*Tb.bsv
// because nearly every testbench here is generated.  This one is
// hand-written and must be tracked (StretchFpCommitTest.bsv's pattern).
package StretchFixtureTest;

import StretchTypes::*;
import StretchDiskSource::*;
import StretchIO::*;

(* synthesize *)
module mkFixtureTb(Empty);
  DiskSource disk <- mkDiskSourceSmall;
  StretchIO  io   <- mkStretchIO;

  Reg#(Bit#(8))  phase <- mkReg(0);
  Reg#(Bit#(32)) fails <- mkReg(0);

  Word64 wA = 64'h0123_4567_89ab_cdef;
  Word64 wB = 64'hfedc_ba98_7654_3210;
  Word64 wC = 64'h5a5a_5a5a_a5a5_a5a5;

  function Action check(String what, Word64 got, Word64 want) = action
    if (got == want) $display("PASS %s", what);
    else begin
      $display("FAIL %s: got %016h, want %016h", what, got, want);
      fails <= fails + 1;
    end
  endaction;

  function Action collect(String what, Word64 want) = action
    if (!disk.respReady()) begin
      $display("FAIL %s: no response in the clock after the request", what);
      fails <= fails + 1;
    end else begin
      let v <- disk.readResp();
      check(what, v, want);
    end
  endaction;

  // ---- the disk ----
  rule d0 (phase == 0);  disk.readReq(5);                 phase <= 1;  endrule
  rule d1 (phase == 1);  collect("disk unwritten word", 0); phase <= 2; endrule
  rule d2 (phase == 2);  disk.write(5, wA);               phase <= 3;  endrule
  rule d3 (phase == 3);  disk.write(1023, wB);            phase <= 4;  endrule
  rule d4 (phase == 4);  disk.readReq(5);                 phase <= 5;  endrule
  rule d5 (phase == 5);  collect("disk written word", wA); phase <= 6; endrule
  rule d6 (phase == 6);  disk.readReq(6);                 phase <= 7;  endrule
  rule d7 (phase == 7);  collect("disk unwritten neighbour", 0); phase <= 8; endrule
  rule d8 (phase == 8);  disk.readReq(1023);              phase <= 9;  endrule
  rule d9 (phase == 9);  collect("disk last word", wB);   phase <= 10; endrule
  rule d10 (phase == 10); disk.readReq(1024);             phase <= 11; endrule
  rule d11 (phase == 11); collect("disk past the end reads zero", 0); phase <= 12; endrule
  // HELD: a write between the request and the collection, to the same
  // word, must not change the answer already read.
  rule d12 (phase == 12); disk.readReq(5);                phase <= 13; endrule
  rule d13 (phase == 13); disk.write(5, wC);              phase <= 14; endrule
  rule d14 (phase == 14);
    let v <- disk.readResp();
    check("disk HELD across a write", v, wA);
    phase <= 15;
  endrule
  rule d15 (phase == 15); disk.readReq(5);                phase <= 16; endrule
  rule d16 (phase == 16); collect("disk rewritten word", wC); phase <= 20; endrule

  // ---- the console's paper ----
  rule c0 (phase == 20); io.readConsoleReq(3);            phase <= 21; endrule
  rule c1 (phase == 21);
    check("console unwritten word", io.readConsoleResp(), 0);
    phase <= 22;
  endrule
  rule c2 (phase == 22); io.writeConsoleWord(3, wA);      phase <= 23; endrule
  rule c3 (phase == 23); io.readConsoleReq(3);            phase <= 24; endrule
  rule c4 (phase == 24);
    check("console written word", io.readConsoleResp(), wA);
    phase <= 25;
  endrule
  rule c5 (phase == 25); io.readConsoleReq(4);            phase <= 26; endrule
  rule c6 (phase == 26);
    check("console unwritten neighbour", io.readConsoleResp(), 0);
    phase <= 27;
  endrule
  rule c7 (phase == 27); io.readConsoleReq(3);            phase <= 28; endrule
  rule c8 (phase == 28); io.writeConsoleWord(3, wB);      phase <= 29; endrule
  rule c9 (phase == 29);
    check("console HELD across a write", io.readConsoleResp(), wA);
    phase <= 30;
  endrule
  rule c10 (phase == 30); io.readConsoleReq(255);         phase <= 31; endrule
  rule c11 (phase == 31); io.writeConsoleWord(255, wC);   phase <= 32; endrule
  rule c12 (phase == 32); io.readConsoleReq(255);         phase <= 33; endrule
  rule c13 (phase == 33);
    check("console last word", io.readConsoleResp(), wC);
    phase <= 34;
  endrule
  rule c14 (phase == 34); io.readConsoleReq(3);           phase <= 35; endrule
  rule c15 (phase == 35);
    check("console rewritten word", io.readConsoleResp(), wB);
    phase <= 40;
  endrule

  rule finish (phase == 40);
    if (fails == 0) $display("ALL TESTS PASSED");
    else $display("%0d TEST(S) FAILED", fails);
    $finish(0);
  endrule
endmodule

endpackage
