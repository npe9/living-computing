// Boot a 1st Edition Plan 9 `z` image on the model.
//
// The image is produced by tools/p9exec.py: the whole file mapped at
// UTZERO (0x1000) as the 1e kernel's sysproc.c does, so the Exec header
// occupies 0x1000..0x101f, text begins at 0x1020 and data at the
// program's own bdata.  tools/p9exec.py writes the image from address 0.
//
// What this testbench does is only the loader's job: place the words,
// warm the prefetch buffer, and start at the image's `entry` with a
// user-level PSW (bit 9 set, CSP = SP) and a stack between SP and MSP.
// Everything after that is the model decoding Bell Labs' code; a parcel
// it cannot decode shows up as a trap at its own PC.
package P9BootTb;

import HobbitTypes::*;
import RegFile::*;
import HobbitCore::*;
import P9Image::*;
import P9Entry::*;

// The model's usual mkHobbitMem is a 1 Kbyte window (Bit#(8) index); a
// Plan 9 image needs text at 0x1020, data at its own bdata (0x3000 or
// 0x4000 here) and a stack at 0x800, so this testbench supplies a 64 Kbyte
// one.  The loader writes the whole image — gaps included — so no
// written-mask is needed for zero fill.
module mkP9Mem(HobbitMem);
  RegFile#(Bit#(14), Word) m <- mkRegFileFull;
  Reg#(Word) raddr <- mkReg(0);
  function Bit#(14) idx(Word a) = truncate(a >> 2);
  method Action readReq(Word a); raddr <= a; endmethod
  method Word readData() = m.sub(idx(raddr));
  method Action write(Word a, Word v); m.upd(idx(a), v); endmethod
  method Word peek(Word a) = m.sub(idx(a));
endmodule

(* synthesize *)
module mkP9BootTb(Empty);

  // Entry, stack and PSW chosen for the first run; the 1e loader sets
  // these from the kernel, which this testbench does not model.
  Word entry = p9entry();       // the image's own entry (P9Entry.bsv)
  Word sp0   = 32'h0000_0800;
  Word msp0  = 32'h0000_0c00;   // FP is 0xC00 (inferred from 0xbfc + 4)
  Word psw0  = 32'h0000_0200;   // bit 9: CSP = SP (user level)

  HobbitMem mem <- mkP9Mem;
  MemCycles mcyc = defaultMemCycles();
  HobbitCore core <- mkHobbitCore(mem, 32'hFFFFFFFF, mcyc);

  Reg#(Bit#(16)) li <- mkReg(0);
  Reg#(Bool) loaded <- mkReg(False);
  Reg#(Bit#(2)) boot <- mkReg(0);
  Reg#(Bit#(32)) clocks <- mkReg(0);
  Reg#(Bool) done <- mkReg(False);

  rule load (!loaded);
    if (zeroExtend(li) < imageLength()) begin
      mem.write(zeroExtend(li) << 2, imageWord(li));
      li <= li + 1;
    end else
      loaded <= True;
  endrule

  rule ask (loaded && boot == 0);
    core.prefetchImage();
    boot <= 1;
  endrule

  rule start ((boot == 1) && core.prefetchReady());
    core.startAt(entry, sp0, msp0, psw0);
    boot <= 2;
  endrule

  rule observe ((boot == 2) && !done);
    clocks <= clocks + 1;
    if (core.hriValid()) begin
      let h = core.hri();
      $display("HRI pc=%04x insn=%04x%04x sp=%08x>%08x msp=%08x>%08x we=%0d addr=%08x data=%08x mask=%02x trap=%0d cyc=%0d",
               h.pc, h.insn0, h.insn1, h.sp_before, h.sp_after,
               h.msp_before, h.msp_after, pack(h.mem_we), h.mem_addr,
               h.mem_wdata, h.mem_wmask, pack(h.trap), h.cyc);
    end
    let faulted = core.faulted();
    let timedout = clocks > 400;
    if (faulted) $display("FAULT pc=%08x", core.faultPc());
    if (timedout && !faulted) $display("STOP clocks=%0d pc=%08x", clocks, core.pc());
    done <= faulted || timedout;
    if (faulted || timedout) $finish;
  endrule

endmodule
endpackage
